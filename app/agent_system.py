"""CarMax Store Agent System.

This module provides the agent system for the CarMax store demo,
including agent orchestration, task management, and Ollama API integration.
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import asynccontextmanager

import aiohttp
import requests
from pydantic import BaseModel, Field

class AgentStatus(Enum):
    """Enumeration of possible agent statuses."""
    
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"

class TaskModel(BaseModel):
    """Pydantic model for structured task data."""
    task_type: str
    priority: int = Field(default=1, ge=1, le=5)
    context: Dict[str, Any] = Field(default_factory=dict)
    tools_available: List[str] = Field(default_factory=list)

@dataclass
class Task:
    """Represents a task to be processed by an agent.
    
    Attributes:
        id: Unique identifier for the task
        description: Human-readable description of the task
        agent_type: Type of agent that should handle this task
        status: Current status of the task
        result: Result returned by the agent (if completed)
        timestamp: Timestamp when the task was completed
        model: Structured data model for the task
    """
    
    id: str
    description: str
    agent_type: str
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[str] = None
    timestamp: Optional[str] = None
    model: Optional[TaskModel] = None
    retry_count: int = 0
    max_retries: int = 3

class OllamaClient:
    """Modern async Ollama client with structured outputs and resilience.
    
    Handles HTTP requests to the Ollama server with async support,
    structured outputs, retry logic, and interaction visualization.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        """Initialize the Ollama client.
        
        Args:
            base_url: Base URL for the Ollama API server
        """
        self.base_url = base_url
        self.interaction_callback: Optional[Callable] = None
        self.request_count = 0
        self.last_request_time: Optional[float] = None
        self.current_agent_type: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=60)
        self.max_retries = 3
        self.backoff_factor = 1.5
        
    def set_interaction_callback(self, callback: Callable) -> None:
        """Set callback function for interaction visualization.
        
        Args:
            callback: Function to call when interactions occur
        """
        self.interaction_callback = callback
        
    @asynccontextmanager
    async def session(self):
        """Async context manager for HTTP session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        try:
            yield self._session
        finally:
            pass  # Keep session alive for reuse
    
    async def close(self):
        """Close the HTTP session with error handling."""
        if self._session:
            try:
                await self._session.close()
            except Exception as e:
                print(f"Warning: Error closing HTTP session: {e}")
            finally:
                self._session = None
    
    def generate(self, model: str, prompt: str, system_prompt: str = "") -> str:
        """Synchronous wrapper for async generate method."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, run in thread pool
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.async_generate(model, prompt, system_prompt))
                    return future.result(timeout=60)
            else:
                return asyncio.run(self.async_generate(model, prompt, system_prompt))
        except Exception as e:
            return f"Error in sync wrapper: {str(e)}"
    
    async def async_generate(self, model: str, prompt: str, system_prompt: str = "", 
                           format_type: Optional[str] = None) -> str:
        """Generate text using Ollama API with async support and structured outputs.
        
        Args:
            model: Name of the Ollama model to use
            prompt: Input prompt for text generation
            system_prompt: System prompt to set context
            format_type: Optional format for structured output (json, etc.)
            
        Returns:
            Generated text response or error message
        """
        for attempt in range(self.max_retries):
            try:
                self.request_count += 1
                self.last_request_time = time.time()
                
                # Notify visualizer of outgoing request
                if self.interaction_callback:
                    self.interaction_callback("request", {
                        "model": model,
                        "prompt_length": len(prompt),
                        "system_prompt_length": len(system_prompt),
                        "request_id": self.request_count,
                        "agent_type": self.current_agent_type,
                        "attempt": attempt + 1
                    })
                
                data = {
                    "model": model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_k": 40,
                        "top_p": 0.9,
                    }
                }
                
                if format_type:
                    data["format"] = format_type
                
                async with self.session() as session:
                    url = f"{self.base_url}/api/generate"
                    async with session.post(url, json=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        response_text = result.get("response", "")
                        
                        # Notify visualizer of response
                        if self.interaction_callback:
                            self.interaction_callback("response", {
                                "success": True,
                                "response_length": len(response_text),
                                "request_id": self.request_count,
                                "agent_type": self.current_agent_type,
                                "attempt": attempt + 1
                            })
                        
                        return response_text
                        
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                
                error_msg = f"Error after {self.max_retries} attempts: {str(e)}"
                if self.interaction_callback:
                    self.interaction_callback("error", {
                        "success": False,
                        "error": str(e),
                        "request_id": self.request_count,
                        "agent_type": self.current_agent_type,
                        "attempts": self.max_retries
                    })
                return error_msg
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                if self.interaction_callback:
                    self.interaction_callback("error", {
                        "success": False,
                        "error": str(e),
                        "request_id": self.request_count,
                        "agent_type": self.current_agent_type
                    })
                return error_msg
        
        return "Failed to generate response after all retries"

class BaseAgent:
    """Base class for all agents in the CarMax system.
    
    Provides common functionality for task processing and status management.
    """
    
    def __init__(self, name: str, role: str, model: str = "llama3.2") -> None:
        """Initialize the base agent.
        
        Args:
            name: Display name for the agent
            role: Role description for the agent
            model: Ollama model to use for text generation
        """
        self.name = name
        self.role = role
        self.model = model
        self.client = OllamaClient()
        self.status = AgentStatus.IDLE
        self.tasks_completed = 0
        self.agent_type: Optional[str] = None
        
    def set_agent_type(self, agent_type: str) -> None:
        """Set the agent type for interaction tracking.
        
        Args:
            agent_type: Type identifier for this agent
        """
        self.agent_type = agent_type
        
    def process_task(self, task: Task) -> str:
        """Process a task with retry logic and enhanced error handling.
        
        Args:
            task: Task object to process
            
        Returns:
            Result string from task processing
        """
        self.status = AgentStatus.WORKING
        task.status = AgentStatus.WORKING
        
        while task.retry_count < task.max_retries:
            try:
                # Set current agent type in client for this request
                if hasattr(self.client, 'current_agent_type'):
                    self.client.current_agent_type = self.agent_type
                
                # Enhanced system prompt with role clarity
                system_prompt = self._build_system_prompt(task)
                
                # Use structured output if task model specifies format
                format_type = None
                if task.model and "json" in task.model.tools_available:
                    format_type = "json"
                
                if hasattr(self.client, 'async_generate'):
                    # Use async method if available
                    result = asyncio.run(self.client.async_generate(
                        model=self.model,
                        prompt=self._build_prompt(task),
                        system_prompt=system_prompt,
                        format_type=format_type
                    ))
                else:
                    # Fallback to sync method
                    result = self.client.generate(
                        model=self.model,
                        prompt=self._build_prompt(task),
                        system_prompt=system_prompt
                    )
                
                # Validate and post-process result
                result = self._validate_result(result, task)
                
                task.result = result
                task.status = AgentStatus.COMPLETED
                task.timestamp = time.strftime("%H:%M:%S")
                self.status = AgentStatus.COMPLETED
                self.tasks_completed += 1
                
                return result
                
            except Exception as e:
                task.retry_count += 1
                if task.retry_count >= task.max_retries:
                    error_msg = f"Error processing task after {task.max_retries} attempts: {str(e)}"
                    task.result = error_msg
                    task.status = AgentStatus.ERROR
                    self.status = AgentStatus.ERROR
                    return error_msg
                else:
                    # Wait before retry with exponential backoff
                    time.sleep(1.5 ** task.retry_count)
                    continue
        
        return "Task failed after all retries"
    
    def _build_system_prompt(self, task: Task) -> str:
        """Build enhanced system prompt with context."""
        base_prompt = f"You are {self.name}, a {self.role}. {self.get_system_prompt()}"
        
        if task.model and task.model.context:
            context_info = "\n\nAdditional Context:\n"
            for key, value in task.model.context.items():
                context_info += f"- {key}: {value}\n"
            base_prompt += context_info
        
        return base_prompt
    
    def _build_prompt(self, task: Task) -> str:
        """Build enhanced prompt with task-specific information."""
        prompt = task.description
        
        if task.model:
            if task.model.priority > 3:
                prompt = f"[HIGH PRIORITY] {prompt}"
            
            if task.model.tools_available:
                prompt += f"\n\nAvailable tools: {', '.join(task.model.tools_available)}"
        
        return prompt
    
    def _validate_result(self, result: str, task: Task) -> str:
        """Validate and post-process the result."""
        # Basic validation
        if not result or len(result.strip()) < 10:
            raise ValueError("Result too short or empty")
        
        # Remove potential error prefixes
        if result.startswith("Error:") or result.startswith("Unexpected error:"):
            raise ValueError(f"LLM returned error: {result}")
        
        return result.strip()
    
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent type.
        
        Override in subclasses to provide specific system prompts.
        
        Returns:
            System prompt string
        """
        return "You are a helpful AI assistant."

class SalesConsultantAgent(BaseAgent):
    """Sales consultant agent with advanced customer interaction tools."""
    
    def __init__(self, name: str = "Sales Consultant") -> None:
        """Initialize the sales consultant agent.
        
        Args:
            name: Display name for the agent
        """
        super().__init__(name, "CarMax Sales Consultant", "llama3.2")
        self.available_tools = ["inventory_search", "price_calculator", "feature_comparison", "appointment_scheduler"]
        self.knowledge_base = {
            "vehicle_categories": ["sedan", "suv", "truck", "coupe", "convertible", "wagon"],
            "popular_features": ["navigation", "backup_camera", "heated_seats", "sunroof", "bluetooth"],
            "price_ranges": {"budget": "<$15k", "mid": "$15k-$30k", "premium": "$30k+"}
        }
    
    def get_system_prompt(self) -> str:
        return f"""You are a CarMax Sales Consultant with access to advanced tools: {', '.join(self.available_tools)}.
        
        You help customers find the perfect vehicle by:
        - Understanding their needs, budget, and preferences
        - Using inventory search to find matching vehicles
        - Explaining features and comparing options
        - Calculating pricing with financing options
        - Scheduling test drives and appointments
        
        Knowledge Base: {json.dumps(self.knowledge_base, indent=2)}
        
        Be consultative, ask clarifying questions, and provide data-driven recommendations.
        Keep initial responses under 200 words, but elaborate when requested."""

class AppraisalManagerAgent(BaseAgent):
    """Advanced appraisal manager with market analysis and valuation tools."""
    
    def __init__(self, name: str = "Appraisal Manager") -> None:
        """Initialize the appraisal manager agent.
        
        Args:
            name: Display name for the agent
        """
        super().__init__(name, "CarMax Appraisal Manager", "llama3.2")
        self.available_tools = ["market_analyzer", "condition_assessor", "price_estimator", "history_checker"]
        self.valuation_factors = {
            "mileage_impact": {"low": "+10%", "average": "0%", "high": "-15%"},
            "condition_grades": ["excellent", "good", "fair", "poor"],
            "market_trends": ["demand", "seasonality", "model_popularity", "economic_factors"]
        }
    
    def get_system_prompt(self) -> str:
        return f"""You are a CarMax Appraisal Manager with access to professional tools: {', '.join(self.available_tools)}.
        
        Your expertise includes:
        - Comprehensive vehicle condition assessment
        - Market value analysis using current data
        - Trade-in value calculations
        - History and damage evaluation
        - Depreciation and appreciation trends
        
        Valuation Framework: {json.dumps(self.valuation_factors, indent=2)}
        
        Provide detailed, data-driven appraisals with clear reasoning.
        Include specific dollar amounts, condition notes, and market justification."""

class FinanceManagerAgent(BaseAgent):
    """Advanced finance manager with comprehensive financial tools and calculators."""
    
    def __init__(self, name: str = "Finance Manager") -> None:
        """Initialize the finance manager agent.
        
        Args:
            name: Display name for the agent
        """
        super().__init__(name, "CarMax Finance Manager", "llama3.2")
        self.available_tools = ["loan_calculator", "credit_analyzer", "payment_optimizer", "insurance_estimator"]
        self.financing_options = {
            "loan_terms": ["36", "48", "60", "72", "84"],
            "credit_tiers": {"excellent": "750+", "good": "650-749", "fair": "550-649", "poor": "<550"},
            "rate_ranges": {"excellent": "3-5%", "good": "5-8%", "fair": "8-12%", "poor": "12-18%"}
        }
    
    def get_system_prompt(self) -> str:
        return f"""You are a CarMax Finance Manager with access to advanced financial tools: {', '.join(self.available_tools)}.
        
        Your specialties include:
        - Loan structuring and payment calculations
        - Credit analysis and approval likelihood
        - Interest rate optimization
        - Insurance and warranty options
        - Down payment strategies
        - Monthly budget planning
        
        Financing Framework: {json.dumps(self.financing_options, indent=2)}
        
        Always provide multiple financing scenarios with specific numbers.
        Include total cost comparisons and explain pros/cons of each option.
        Use tables and clear calculations when possible."""

class StoreManagerAgent(BaseAgent):
    """Strategic store manager with operational analytics and team coordination tools."""
    
    def __init__(self, name: str = "Store Manager") -> None:
        """Initialize the store manager agent.
        
        Args:
            name: Display name for the agent
        """
        super().__init__(name, "CarMax Store Manager", "llama3.2")
        self.available_tools = ["performance_dashboard", "team_coordinator", "quality_assessor", "process_optimizer"]
        self.management_framework = {
            "kpis": ["customer_satisfaction", "sales_velocity", "team_productivity", "quality_metrics"],
            "processes": ["sales_flow", "appraisal_workflow", "financing_pipeline", "customer_journey"],
            "quality_standards": ["response_time", "accuracy", "customer_service", "compliance"]
        }
    
    def get_system_prompt(self) -> str:
        return f"""You are a CarMax Store Manager with access to operational tools: {', '.join(self.available_tools)}.
        
        Your responsibilities include:
        - Team performance monitoring and coaching
        - Process optimization and quality assurance
        - Customer experience oversight
        - Operational efficiency improvements
        - Cross-functional coordination
        - Strategic decision-making
        
        Management Framework: {json.dumps(self.management_framework, indent=2)}
        
        Provide strategic insights, actionable recommendations, and team leadership.
        Focus on both immediate solutions and long-term improvements.
        Include specific metrics and improvement plans when relevant."""

class AgentOrchestrator:
    """Orchestrates multiple agents to handle CarMax store operations.
    
    Manages task distribution, agent coordination, and provides
    callbacks for visualization and logging.
    """
    
    def __init__(self) -> None:
        """Initialize the agent orchestrator with CarMax team members."""
        self.agents: Dict[str, BaseAgent] = {
            "sales": SalesConsultantAgent("🚗 Mike Rodriguez - Sales Pro"),
            "appraisal": AppraisalManagerAgent("📊 Sarah Chen - Vehicle Expert"), 
            "finance": FinanceManagerAgent("💰 David Williams - Finance Wizard"),
            "manager": StoreManagerAgent("🏆 Jennifer Thompson - Team Leader")
        }
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.ollama_interaction_callback: Optional[Callable] = None
        self.log_callback: Optional[Callable] = None
        
        # Set up Ollama callbacks for all agents
        self.setup_ollama_callbacks()
    
    def setup_ollama_callbacks(self) -> None:
        """Set up Ollama interaction callbacks for all agents."""
        for agent_type, agent in self.agents.items():
            agent.set_agent_type(agent_type)  # Set the agent type
            agent.client.set_interaction_callback(self._handle_ollama_interaction)
            agent.client.current_agent_type = agent_type  # Set current agent type in client
    
    def set_ollama_callback(self, callback: Callable) -> None:
        """Set the callback for Ollama interactions.
        
        Args:
            callback: Function to call when Ollama interactions occur
        """
        self.ollama_interaction_callback = callback
    
    def _handle_ollama_interaction(self, interaction_type: str, data: dict) -> None:
        """Handle Ollama interactions for visualization.
        
        Args:
            interaction_type: Type of interaction (request/response/error)
            data: Interaction data dictionary
        """
        if self.ollama_interaction_callback:
            self.ollama_interaction_callback(interaction_type, data)
    
    def set_log_callback(self, callback: Callable) -> None:
        """Set the callback for log messages.
        
        Args:
            callback: Function to call for log messages
        """
        self.log_callback = callback
    
    def log_message(self, message: str, message_type: str = "info") -> None:
        """Send a log message to the visualizer if callback is set, otherwise print.
        
        Args:
            message: Message to log
            message_type: Type of message (info, error, success, etc.)
        """
        if self.log_callback:
            self.log_callback(message, message_type)
        else:
            print(message)
    
    def create_task(self, description: str, agent_type: str) -> Task:
        """Create a new task.
        
        Args:
            description: Human-readable description of the task
            agent_type: Type of agent that should handle this task
            
        Returns:
            Created Task object
        """
        task_id = f"task_{len(self.task_queue) + len(self.completed_tasks) + 1:03d}"
        task = Task(id=task_id, description=description, agent_type=agent_type)
        self.task_queue.append(task)
        return task
    
    def assign_task(self, task: Task) -> str:
        """Assign a task to the appropriate agent with enhanced error handling.
        
        Args:
            task: Task to assign and process
            
        Returns:
            Result string from task processing
        """
        if task.agent_type not in self.agents:
            error_msg = f"Error: Unknown agent type '{task.agent_type}'"
            task.status = AgentStatus.ERROR
            task.result = error_msg
            self.log_message(f"[ERROR] {error_msg}", "error")
            return error_msg
        
        agent = self.agents[task.agent_type]
        try:
            self.log_message(f"[ASSIGN] Task {task.id} → {agent.name}", "info")
            self.log_message(f"   Task: {task.description[:80]}{'...' if len(task.description) > 80 else ''}", "text_secondary")
            
            # Set agent to working status
            agent.status = AgentStatus.WORKING
            
            result = agent.process_task(task)
            
            # Move task from queue to completed only if successful
            if task.status == AgentStatus.COMPLETED:
                if task in self.task_queue:
                    self.task_queue.remove(task)
                self.completed_tasks.append(task)
                
                self.log_message(f"[COMPLETE] {agent.name} finished task {task.id}", "success")
                self.log_message(f"   Result: {result[:80]}{'...' if len(result) > 80 else ''}", "text_secondary")
            else:
                self.log_message(f"[FAILED] {agent.name} failed task {task.id}", "error")
                self.log_message(f"   Error: {result[:80]}{'...' if len(result) > 80 else ''}", "error")
            
            return result
            
        except Exception as e:
            error_msg = f"Critical error assigning task {task.id}: {str(e)}"
            task.status = AgentStatus.ERROR
            task.result = error_msg
            agent.status = AgentStatus.ERROR
            self.log_message(f"[CRITICAL] {error_msg}", "error")
            return error_msg
    
    def process_all_tasks(self) -> None:
        """Process all tasks in the queue with enhanced error handling."""
        total_tasks = len(self.task_queue)
        self.log_message(f"[PROCESS] Starting processing of {total_tasks} tasks...", "info")
        
        failed_tasks = []
        completed_count = 0
        
        while self.task_queue:
            task = self.task_queue[0]
            
            try:
                self.assign_task(task)
                
                if task.status == AgentStatus.COMPLETED:
                    completed_count += 1
                elif task.status == AgentStatus.ERROR:
                    failed_tasks.append(task)
                    # Remove failed task from queue
                    if task in self.task_queue:
                        self.task_queue.remove(task)
                
                # Small delay between tasks for better visualization
                time.sleep(1.5)
                
            except Exception as e:
                self.log_message(f"[ERROR] Exception processing task {task.id}: {str(e)}", "error")
                failed_tasks.append(task)
                if task in self.task_queue:
                    self.task_queue.remove(task)
        
        # Final summary
        if failed_tasks:
            self.log_message(f"[SUMMARY] {completed_count}/{total_tasks} tasks completed, {len(failed_tasks)} failed", "error")
            for failed_task in failed_tasks:
                self.log_message(f"   Failed: {failed_task.id} - {failed_task.description[:50]}...", "error")
        else:
            self.log_message(f"[DONE] All {total_tasks} tasks completed successfully!", "success")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents.
        
        Returns:
            Dictionary with agent status information
        """
        status = {}
        for agent_type, agent in self.agents.items():
            status[agent_type] = {
                "name": agent.name,
                "role": agent.role,
                "status": agent.status.value,
                "tasks_completed": agent.tasks_completed
            }
        return status
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of all tasks.
        
        Returns:
            Dictionary with task summary information
        """
        return {
            "total_tasks": len(self.completed_tasks) + len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": len(self.task_queue),
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description[:50] + "..." if len(task.description) > 50 else task.description,
                    "agent_type": task.agent_type,
                    "status": task.status.value,
                    "timestamp": task.timestamp
                }
                for task in self.completed_tasks + self.task_queue
            ]
        }
