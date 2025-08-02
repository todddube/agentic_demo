#!/usr/bin/env python3
"""Simple CarMax Store Demo with Unified Pygame Interface.

======================================================

This demo showcases CarMax store employees working together using Ollama's llama3.2 model
with a unified pygame interface showing both graphics and text output in one window.

Agents:
- Mike Rodriguez: Sales Consultant who helps customers find vehicles
- Sarah Chen: Appraisal Manager who evaluates vehicle values
- David Williams: Finance Manager who structures payment deals  
- Jennifer Thompson: Store Manager who oversees operations

Usage:
    python simple_demo.py

Requirements:
    - Ollama installed and running (http://localhost:11434)
    - llama3.2 model downloaded (ollama pull llama3.2)
    - pygame installed (pip install pygame)
"""

import json
import subprocess
import time
from typing import List, Tuple
import sys
import os

from agent_system import AgentOrchestrator, Task
from unified_visualizer import UnifiedVisualizer

def print_banner() -> None:
    """Print a nice banner for the demo."""
    print("=" * 70)
    print("           CarMax Store Demo")
    print("")
    print("        Multi-Agent CarMax Store System")
    print("")
    print("  Team: Sales | Appraisal | Finance | Manager")
    print("=" * 70)

def check_ollama_connection(orchestrator: AgentOrchestrator, 
                          visualizer: UnifiedVisualizer) -> bool:
    """Check if Ollama is running and llama3.2 is available.
    
    Args:
        orchestrator: Agent orchestrator instance
        visualizer: Visualizer instance for logging
        
    Returns:
        True if connection is successful, False otherwise
    """
    visualizer.log_message("[CHECK] Checking Ollama connection...", "info")
    
    def test_ollama_connection():
        """Test if Ollama is responding"""
        try:
            test_agent = orchestrator.agents['sales']
            test_result = test_agent.client.generate(
                model="llama3.2",
                prompt="Say 'Hello' in exactly one word.",
                system_prompt="You are a test agent. Respond with exactly one word."
            )
            return not ("Error" in test_result or not test_result.strip()), test_result
        except Exception as e:
            return False, str(e)
    
    # First attempt to connect
    success, result = test_ollama_connection()
    
    if success:
        visualizer.log_message("[OK] Ollama connection successful!", "success")
        visualizer.log_message(f"   Test response: {result.strip()}", "text_secondary")
        return True
    
    # Connection failed - try to start Ollama automatically
    visualizer.log_message("[WARN] Ollama not responding. Attempting to start Ollama...", "info")
    
    try:
        # Try to start Ollama service
        if os.name == 'nt':  # Windows
            # Try to start ollama serve in background
            subprocess.Popen(
                ["ollama", "serve"], 
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:  # Unix-like systems
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        visualizer.log_message("[INFO] Starting Ollama service... Please wait...", "info")
        
        # Wait a moment for Ollama to start
        for i in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            visualizer.log_message(f"[WAIT] Checking connection... ({i+1}/10)", "info")
            
            success, result = test_ollama_connection()
            if success:
                visualizer.log_message("[OK] Ollama started successfully!", "success")
                visualizer.log_message(f"   Test response: {result.strip()}", "text_secondary")
                return True
        
        # Still not working after trying to start
        visualizer.log_message("[ERROR] Failed to start Ollama automatically.", "error")
        
    except FileNotFoundError:
        visualizer.log_message("[ERROR] Ollama not found in system PATH.", "error")
    except Exception as e:
        visualizer.log_message(f"[ERROR] Error starting Ollama: {str(e)}", "error")
    
    # Final error message and instructions
    visualizer.log_message("", "error")  # Empty line
    visualizer.log_message("❌ OLLAMA CONNECTION FAILED", "error")
    visualizer.log_message("", "error")  # Empty line
    visualizer.log_message("Please manually start Ollama:", "error")
    visualizer.log_message("", "error")  # Empty line
    visualizer.log_message("1. Open a terminal/command prompt", "error")
    visualizer.log_message("2. Run: ollama serve", "error")
    visualizer.log_message("3. In another terminal, run: ollama pull llama3.2", "error")
    visualizer.log_message("4. Restart this demo", "error")
    visualizer.log_message("", "error")  # Empty line
    visualizer.log_message("If Ollama is not installed:", "error")
    visualizer.log_message("• Visit: https://ollama.ai", "error")
    visualizer.log_message("• Download and install Ollama", "error")
    visualizer.log_message("", "error")  # Empty line
    visualizer.log_message("Press ESC or close window to exit.", "error")
    
    return False

def create_demo_tasks() -> List[Tuple[str, str]]:
    """Create a set of CarMax store-related demo tasks.
    
    Returns:
        List of tuples containing (task_description, agent_type)
    """
    return [
        ("Help a customer find a reliable family SUV under $25,000", "sales"),
        ("Create a plan for training new sales consultants", "manager"),
        ("Appraise a 2018 Honda Civic with 45,000 miles", "appraisal"),
        ("Explain financing options for a customer with 650 credit score", "finance"),
        ("Review and improve our customer service approach", "manager"),
        ("Plan a 30-day sales training program for new hires", "manager"),
        ("Analyze current market trends for electric vehicles", "appraisal"),
        ("Help a first-time buyer understand CarMax warranties", "sales"),
    ]

def run_demo(orchestrator: AgentOrchestrator, 
            visualizer: UnifiedVisualizer) -> None:
    """Run the CarMax store demo with unified visualization.
    
    Args:
        orchestrator: Agent orchestrator instance
        visualizer: Visualizer instance for display
    """
    visualizer.log_message("[START] Starting CarMax Store Demo", "info")
    
    demo_tasks = create_demo_tasks()
    
    # Create tasks
    visualizer.log_message(f"[TASKS] Creating {len(demo_tasks)} tasks for the team...", "info")
    tasks = []
    for i, (desc, agent_type) in enumerate(demo_tasks, 1):
        task = orchestrator.create_task(desc, agent_type)
        tasks.append(task)
        role_name = {
            "sales": "Sales", 
            "appraisal": "Appraisal", 
            "finance": "Finance", 
            "manager": "Manager"
        }[agent_type]
        visualizer.log_message(f"   {i}. {desc[:50]}... → {role_name}", "text_secondary")
    
    visualizer.log_message(f"[PROCESS] Processing customer requests...", "info")
    visualizer.log_message("-" * 50, "text_dim")
    
    # Process tasks
    for i, task in enumerate(tasks, 1):
        agent_name = orchestrator.agents[task.agent_type].name
        visualizer.log_message(f"[{i}/{len(tasks)}] {agent_name} is working...", "info")
        visualizer.log_message(f"Task: {task.description}", "text_secondary")
        
        # Update visualizer with current task
        visualizer.update_current_task(task, agent_name, task.agent_type)
        
        # Process the task
        result = orchestrator.assign_task(task)
        
        # Notify visualizer of completion
        visualizer.task_completed(task, result)
        
        # Show completion
        visualizer.log_message(f"[DONE] Completed at {task.timestamp}", "success")
        visualizer.log_message("-" * 50, "text_dim")
        
        time.sleep(1.5)  # Delay to see the visualization
    
    # Clear current task from visualizer
    visualizer.clear_current_task()
    visualizer.log_message("[SUCCESS] All tasks completed successfully!", "success")

def show_summary(orchestrator: AgentOrchestrator, 
                visualizer: UnifiedVisualizer) -> None:
    """Show a summary of agent performance.
    
    Args:
        orchestrator: Agent orchestrator instance
        visualizer: Visualizer instance for display
    """
    visualizer.log_message("[STATS] Agent Performance Summary", "info")
    visualizer.log_message("=" * 40, "text_dim")
    
    for agent_type, agent in orchestrator.agents.items():
        status_icon = "[OK]" if agent.status.value == "completed" else "[WAIT]"
        summary_line = (
            f"{status_icon} {agent.name:15} | "
            f"{agent.role:15} | Tasks: {agent.tasks_completed}"
        )
        visualizer.log_message(summary_line, "text_secondary")
    
    total_tasks = len(orchestrator.completed_tasks)
    visualizer.log_message(f"[TOTAL] Total tasks processed: {total_tasks}", "success")
    visualizer.log_message("=" * 40, "text_dim")

def show_task_details(orchestrator: AgentOrchestrator, 
                     visualizer: UnifiedVisualizer) -> None:
    """Show detailed results of completed tasks.
    
    Args:
        orchestrator: Agent orchestrator instance
        visualizer: Visualizer instance for display
    """
    visualizer.log_message("[DETAILS] Detailed Task Results", "info")
    visualizer.log_message("=" * 50, "text_dim")
    
    for task in orchestrator.completed_tasks:
        agent = orchestrator.agents[task.agent_type]
        visualizer.log_message(f"{task.id} | {agent.name} | {task.timestamp}", "info")
        visualizer.log_message(f"Task: {task.description}", "text_secondary")
        result_preview = task.result[:100] + ("..." if len(task.result) > 100 else "")
        visualizer.log_message(f"Result: {result_preview}", "text")
        visualizer.log_message("-" * 50, "text_dim")

def main() -> None:
    """Main demo function."""
    # Initialize the system
    print("[INIT] Initializing CarMax Store System...")
    orchestrator = AgentOrchestrator()
    visualizer = UnifiedVisualizer(orchestrator)
    
    # Set up log callback so agent system messages go to pygame window
    orchestrator.set_log_callback(visualizer.log_message)
    
    # Define the demo function to be called when start button is clicked
    def demo_function() -> None:
        """The actual demo logic that runs when start button is clicked."""
        # Check Ollama connection
        if not check_ollama_connection(orchestrator, visualizer):
            visualizer.log_message("❌ Demo cannot continue without Ollama connection.", "error")
            visualizer.log_message("", "error")  # Empty line
            visualizer.log_message("The demo will remain open so you can:", "error")
            visualizer.log_message("• Read the instructions above", "error")  
            visualizer.log_message("• Start Ollama manually", "error")
            visualizer.log_message("• Press ESC or close window when ready", "error")
            
            # Set demo state to failed so user knows what happened
            visualizer.demo_state = "ollama_failed"
            return
        
        # Show initial agent status
        visualizer.log_message("[TEAM] Agent Team Ready:", "info")
        for agent_type, agent in orchestrator.agents.items():
            visualizer.log_message(f"   • {agent.name} - {agent.role}", "text_secondary")
        
        # Run the demo tasks
        run_demo(orchestrator, visualizer)
        show_summary(orchestrator, visualizer)
        
        # Mark demo as completed
        visualizer.demo_state = "completed"
        visualizer.log_message("[DONE] Demo completed! The system is now ready for exploration.", "success")
        visualizer.log_message("[INFO] Graphics panel shows team network and status", "info")
        visualizer.log_message("[INFO] Text panel shows all system output", "info")
        visualizer.log_message(
            "[UI] Use controls: ↑↓ scroll, Space: auto-scroll, D: details", "info"
        )
        visualizer.log_message(
            "[EXIT] Close pygame window or press ESC to exit", "info"
        )
    
    # Set the demo callback
    visualizer.set_demo_callback(demo_function)
    
    # Start the visualizer (shows start screen)
    print("[START] Starting CarMax store interface...")
    visualizer.start()
    
    # Wait for pygame window to be closed (the visualization thread handles everything)
    try:
        # Join the visualization thread instead of polling
        if hasattr(visualizer, 'visualization_thread'):
            visualizer.visualization_thread.join()
    except KeyboardInterrupt:
        visualizer.stop()
    finally:
        pass

if __name__ == "__main__":
    main()
