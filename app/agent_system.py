"""CarMax Store Agent System.

This module provides the agent system for the CarMax store demo,
including agent orchestration, task management, and Ollama API integration.
"""

import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import requests

class AgentStatus(Enum):
    """Enumeration of possible agent statuses."""
    
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"

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
    """
    
    id: str
    description: str
    agent_type: str
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[str] = None
    timestamp: Optional[str] = None

class OllamaClient:
    """Client for communicating with Ollama API.
    
    Handles HTTP requests to the Ollama server and provides
    callbacks for interaction visualization.
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
        
    def set_interaction_callback(self, callback: Callable) -> None:
        """Set callback function for interaction visualization.
        
        Args:
            callback: Function to call when interactions occur
        """
        self.interaction_callback = callback
        
    def generate(self, model: str, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Ollama API.
        
        Args:
            model: Name of the Ollama model to use
            prompt: Input prompt for text generation
            system_prompt: System prompt to set context
            
        Returns:
            Generated text response or error message
        """
        self.request_count += 1
        self.last_request_time = time.time()
        
        # Notify visualizer of outgoing request
        if self.interaction_callback:
            self.interaction_callback("request", {
                "model": model,
                "prompt_length": len(prompt),
                "system_prompt_length": len(system_prompt),
                "request_id": self.request_count,
                "agent_type": self.current_agent_type
            })
        
        try:
            url = f"{self.base_url}/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Notify visualizer of response
            if self.interaction_callback:
                self.interaction_callback("response", {
                    "success": True,
                    "response_length": len(response_text),
                    "request_id": self.request_count,
                    "agent_type": self.current_agent_type
                })
            
            return response_text
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error: {str(e)}"
            # Notify visualizer of error
            if self.interaction_callback:
                self.interaction_callback("error", {
                    "success": False,
                    "error": str(e),
                    "request_id": self.request_count,
                    "agent_type": self.current_agent_type
                })
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            # Notify visualizer of error
            if self.interaction_callback:
                self.interaction_callback("error", {
                    "success": False,
                    "error": str(e),
                    "request_id": self.request_count,
                    "agent_type": self.current_agent_type
                })
            return error_msg

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
        """Process a task and return the result.
        
        Args:
            task: Task object to process
            
        Returns:
            Result string from task processing
        """
        self.status = AgentStatus.WORKING
        task.status = AgentStatus.WORKING
        
        try:
            # Set current agent type in client for this request
            if hasattr(self.client, 'current_agent_type'):
                self.client.current_agent_type = self.agent_type
            
            system_prompt = f"You are {self.name}, a {self.role}. {self.get_system_prompt()}"
            result = self.client.generate(
                model=self.model,
                prompt=task.description,
                system_prompt=system_prompt
            )
            
            task.result = result
            task.status = AgentStatus.COMPLETED
            task.timestamp = time.strftime("%H:%M:%S")
            self.status = AgentStatus.COMPLETED
            self.tasks_completed += 1
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing task: {str(e)}"
            task.result = error_msg
            task.status = AgentStatus.ERROR
            self.status = AgentStatus.ERROR
            return error_msg
    
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent type.
        
        Override in subclasses to provide specific system prompts.
        
        Returns:
            System prompt string
        """
        return "You are a helpful AI assistant."

class SalesConsultantAgent(BaseAgent):
    """Sales consultant agent specialized in helping customers find vehicles."""
    
    def __init__(self, name: str = "Sales Consultant") -> None:
        """Initialize the sales consultant agent.
        
        Args:
            name: Display name for the agent
        """
        super().__init__(name, "CarMax Sales Consultant", "llama3.2")
    
    def get_system_prompt(self) -> str:
        return """You are a CarMax Sales Consultant who helps customers find the perfect vehicle. 
        You're knowledgeable about car features, financing options, and customer needs. 
        Keep responses friendly, informative, and focused on customer satisfaction. Under 200 words unless asked for more."""

class AppraisalManagerAgent(BaseAgent):
    """Appraisal manager agent specialized in vehicle evaluation."""
    
    def __init__(self, name: str = "Appraisal Manager") -> None:
        """Initialize the appraisal manager agent.
        
        Args:
            name: Display name for the agent
        """
        super().__init__(name, "CarMax Appraisal Manager", "llama3.2")
    
    def get_system_prompt(self) -> str:
        return """You are a CarMax Appraisal Manager who evaluates vehicle condition, market value, and trade-in assessments. 
        Be analytical, detail-oriented, and provide accurate vehicle evaluations based on data and market trends."""

class FinanceManagerAgent(BaseAgent):
    """Finance manager agent specialized in financing deals."""
    
    def __init__(self, name: str = "Finance Manager") -> None:
        """Initialize the finance manager agent.
        
        Args:
            name: Display name for the agent
        """
        super().__init__(name, "CarMax Finance Manager", "llama3.2")
    
    def get_system_prompt(self) -> str:
        return """You are a CarMax Finance Manager who structures financing deals, explains loan options, and helps customers 
        understand payment plans. Create clear, organized financial solutions with step-by-step explanations."""

class StoreManagerAgent(BaseAgent):
    """Store manager agent specialized in operations oversight."""
    
    def __init__(self, name: str = "Store Manager") -> None:
        """Initialize the store manager agent.
        
        Args:
            name: Display name for the agent
        """
        super().__init__(name, "CarMax Store Manager", "llama3.2")
    
    def get_system_prompt(self) -> str:
        return """You are a CarMax Store Manager who oversees operations, ensures quality customer service, and reviews all processes. 
        Provide leadership perspective, quality assessments, and operational improvements."""

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
        """Assign a task to the appropriate agent.
        
        Args:
            task: Task to assign and process
            
        Returns:
            Result string from task processing
        """
        if task.agent_type not in self.agents:
            return f"Error: Unknown agent type '{task.agent_type}'"
        
        agent = self.agents[task.agent_type]
        self.log_message(f"[ASSIGN] Task {task.id} → {agent.name}", "info")
        self.log_message(f"   Task: {task.description}", "text_secondary")
        
        result = agent.process_task(task)
        
        # Move task from queue to completed
        if task in self.task_queue:
            self.task_queue.remove(task)
        self.completed_tasks.append(task)
        
        self.log_message(f"[COMPLETE] {agent.name} finished task {task.id}", "success")
        self.log_message(f"   Result: {result[:100]}{'...' if len(result) > 100 else ''}", "text_secondary")
        
        return result
    
    def process_all_tasks(self) -> None:
        """Process all tasks in the queue sequentially."""
        self.log_message("[PROCESS] Starting task processing...", "info")
        
        while self.task_queue:
            task = self.task_queue[0]
            self.assign_task(task)
            time.sleep(1)  # Small delay between tasks
        
        self.log_message("[DONE] All tasks completed!", "success")
    
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
