import requests
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class Task:
    id: str
    description: str
    agent_type: str
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[str] = None
    timestamp: Optional[str] = None

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.interaction_callback = None  # Callback for visualizing interactions
        self.request_count = 0
        self.last_request_time = None
        self.current_agent_type = None  # Current agent making the request
        
    def set_interaction_callback(self, callback):
        """Set callback function for interaction visualization"""
        self.interaction_callback = callback
        
    def generate(self, model: str, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Ollama API"""
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
    def __init__(self, name: str, role: str, model: str = "llama3.2"):
        self.name = name
        self.role = role
        self.model = model
        self.client = OllamaClient()
        self.status = AgentStatus.IDLE
        self.tasks_completed = 0
        self.agent_type = None  # Will be set by orchestrator
        
    def set_agent_type(self, agent_type: str):
        """Set the agent type for interaction tracking"""
        self.agent_type = agent_type
        
    def process_task(self, task: Task) -> str:
        """Process a task and return the result"""
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
        """Override in subclasses to provide specific system prompts"""
        return "You are a helpful AI assistant."

class SalesConsultantAgent(BaseAgent):
    def __init__(self, name: str = "Sales Consultant"):
        super().__init__(name, "CarMax Sales Consultant", "llama3.2")
    
    def get_system_prompt(self) -> str:
        return """You are a CarMax Sales Consultant who helps customers find the perfect vehicle. 
        You're knowledgeable about car features, financing options, and customer needs. 
        Keep responses friendly, informative, and focused on customer satisfaction. Under 200 words unless asked for more."""

class AppraisalManagerAgent(BaseAgent):
    def __init__(self, name: str = "Appraisal Manager"):
        super().__init__(name, "CarMax Appraisal Manager", "llama3.2")
    
    def get_system_prompt(self) -> str:
        return """You are a CarMax Appraisal Manager who evaluates vehicle condition, market value, and trade-in assessments. 
        Be analytical, detail-oriented, and provide accurate vehicle evaluations based on data and market trends."""

class FinanceManagerAgent(BaseAgent):
    def __init__(self, name: str = "Finance Manager"):
        super().__init__(name, "CarMax Finance Manager", "llama3.2")
    
    def get_system_prompt(self) -> str:
        return """You are a CarMax Finance Manager who structures financing deals, explains loan options, and helps customers 
        understand payment plans. Create clear, organized financial solutions with step-by-step explanations."""

class StoreManagerAgent(BaseAgent):
    def __init__(self, name: str = "Store Manager"):
        super().__init__(name, "CarMax Store Manager", "llama3.2")
    
    def get_system_prompt(self) -> str:
        return """You are a CarMax Store Manager who oversees operations, ensures quality customer service, and reviews all processes. 
        Provide leadership perspective, quality assessments, and operational improvements."""

class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "sales": SalesConsultantAgent("Mike Rodriguez - Sales"),
            "appraisal": AppraisalManagerAgent("Sarah Chen - Appraisal"), 
            "finance": FinanceManagerAgent("David Williams - Finance"),
            "manager": StoreManagerAgent("Jennifer Thompson - Store Manager")
        }
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.ollama_interaction_callback = None  # For visualizer
        
        # Set up Ollama callbacks for all agents
        self.setup_ollama_callbacks()
    
    def setup_ollama_callbacks(self):
        """Set up Ollama interaction callbacks for all agents"""
        for agent_type, agent in self.agents.items():
            agent.set_agent_type(agent_type)  # Set the agent type
            agent.client.set_interaction_callback(self._handle_ollama_interaction)
            agent.client.current_agent_type = agent_type  # Set current agent type in client
    
    def set_ollama_callback(self, callback):
        """Set the callback for Ollama interactions"""
        self.ollama_interaction_callback = callback
    
    def _handle_ollama_interaction(self, interaction_type: str, data: dict):
        """Handle Ollama interactions for visualization"""
        if self.ollama_interaction_callback:
            self.ollama_interaction_callback(interaction_type, data)
    
    def create_task(self, description: str, agent_type: str) -> Task:
        """Create a new task"""
        task_id = f"task_{len(self.task_queue) + len(self.completed_tasks) + 1:03d}"
        task = Task(id=task_id, description=description, agent_type=agent_type)
        self.task_queue.append(task)
        return task
    
    def assign_task(self, task: Task) -> str:
        """Assign a task to the appropriate agent"""
        if task.agent_type not in self.agents:
            return f"Error: Unknown agent type '{task.agent_type}'"
        
        agent = self.agents[task.agent_type]
        print(f"📋 Assigning task {task.id} to {agent.name}")
        print(f"   Task: {task.description}")
        
        result = agent.process_task(task)
        
        # Move task from queue to completed
        if task in self.task_queue:
            self.task_queue.remove(task)
        self.completed_tasks.append(task)
        
        print(f"✅ {agent.name} completed task {task.id}")
        print(f"   Result: {result[:100]}{'...' if len(result) > 100 else ''}")
        print()
        
        return result
    
    def process_all_tasks(self):
        """Process all tasks in the queue"""
        print("🚀 Starting task processing...\n")
        
        while self.task_queue:
            task = self.task_queue[0]
            self.assign_task(task)
            time.sleep(1)  # Small delay between tasks
        
        print("🎉 All tasks completed!")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
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
        """Get summary of all tasks"""
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
