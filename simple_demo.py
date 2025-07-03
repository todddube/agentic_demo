#!/usr/bin/env python3
"""
Simple CarMax Store Demo with Unified Pygame Interface
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

import time
import json

from agent_system import AgentOrchestrator, Task
from unified_visualizer import UnifiedVisualizer

def print_banner():
    """Print a nice banner for the demo"""
    print("=" * 70)
    print("           🚗 CARMAX STORE DEMO 🚗")
    print("")
    print("        Multi-Agent CarMax Store System")
    print("")
    print("  Team: Sales 🏆 | Appraisal 📊 | Finance � | Manager �")
    print("=" * 70)

def check_ollama_connection(orchestrator, visualizer):
    """Check if Ollama is running and llama3.2 is available"""
    visualizer.log_message("🔍 Checking Ollama connection...", "info")
    
    try:
        # Test with a simple prompt
        test_agent = orchestrator.agents['sales']
        test_result = test_agent.client.generate(
            model="llama3.2",
            prompt="Say 'Hello' in exactly one word.",
            system_prompt="You are a test agent. Respond with exactly one word."
        )
        
        if "Error" in test_result or not test_result.strip():
            visualizer.log_message("❌ Ollama connection failed. Please ensure:", "error")
            visualizer.log_message("   1. Ollama is installed and running", "error")
            visualizer.log_message("   2. Run: ollama serve", "error")
            visualizer.log_message("   3. Run: ollama pull llama3.2", "error")
            return False
        else:
            visualizer.log_message("✅ Ollama connection successful!", "success")
            visualizer.log_message(f"   Test response: {test_result.strip()}", "text_secondary")
            return True
            
    except Exception as e:
        visualizer.log_message(f"❌ Connection error: {str(e)}", "error")
        return False

def create_demo_tasks():
    """Create a set of CarMax store-related demo tasks"""
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

def run_demo(orchestrator, visualizer):
    """Run the CarMax store demo with unified visualization"""
    visualizer.log_message("🚀 Starting CarMax Store Demo", "info")
    
    demo_tasks = create_demo_tasks()
    
    # Create tasks
    visualizer.log_message(f"📋 Creating {len(demo_tasks)} tasks for the team...", "info")
    tasks = []
    for i, (desc, agent_type) in enumerate(demo_tasks, 1):
        task = orchestrator.create_task(desc, agent_type)
        tasks.append(task)
        role_name = {"sales": "Sales", "appraisal": "Appraisal", "finance": "Finance", "manager": "Manager"}[agent_type]
        visualizer.log_message(f"   {i}. {desc[:50]}... → {role_name}", "text_secondary")
    
    visualizer.log_message(f"✨ Processing customer requests...", "info")
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
        visualizer.log_message(f"✅ Completed at {task.timestamp}", "success")
        visualizer.log_message("-" * 50, "text_dim")
        
        time.sleep(1.5)  # Delay to see the visualization
    
    # Clear current task from visualizer
    visualizer.clear_current_task()
    visualizer.log_message("🎉 All tasks completed successfully!", "success")

def show_summary(orchestrator, visualizer):
    """Show a summary of agent performance"""
    visualizer.log_message("📊 Agent Performance Summary", "info")
    visualizer.log_message("=" * 40, "text_dim")
    
    for agent_type, agent in orchestrator.agents.items():
        status_icon = "✅" if agent.status.value == "completed" else "⏳"
        summary_line = f"{status_icon} {agent.name:15} | {agent.role:15} | Tasks: {agent.tasks_completed}"
        visualizer.log_message(summary_line, "text_secondary")
    
    total_tasks = len(orchestrator.completed_tasks)
    visualizer.log_message(f"📈 Total tasks processed: {total_tasks}", "success")
    visualizer.log_message("=" * 40, "text_dim")

def show_task_details(orchestrator, visualizer):
    """Show detailed results of completed tasks"""
    visualizer.log_message("📝 Detailed Task Results", "info")
    visualizer.log_message("=" * 50, "text_dim")
    
    for task in orchestrator.completed_tasks:
        agent = orchestrator.agents[task.agent_type]
        visualizer.log_message(f"{task.id} | {agent.name} | {task.timestamp}", "info")
        visualizer.log_message(f"Task: {task.description}", "text_secondary")
        visualizer.log_message(f"Result: {task.result[:100]}{'...' if len(task.result) > 100 else ''}", "text")
        visualizer.log_message("-" * 50, "text_dim")

def main():
    """Main demo function"""
    print_banner()
    
    # Initialize the system
    print("🔧 Initializing CarMax Store System...")
    orchestrator = AgentOrchestrator()
    visualizer = UnifiedVisualizer(orchestrator)
    
    # Start the visualizer
    print("🎮 Starting CarMax store interface...")
    print("   (A large pygame window will open with both graphics and text)")
    visualizer.start()
    time.sleep(2)  # Give visualizer time to start
    
    # Check Ollama connection
    if not check_ollama_connection(orchestrator, visualizer):
        visualizer.log_message("❌ Demo cannot continue without Ollama connection.", "error")
        visualizer.log_message("Please start Ollama and try again.", "error")
        input("Press Enter to exit...")
        visualizer.stop()
        return
    
    # Show initial agent status
    visualizer.log_message("👥 Agent Team Ready:", "info")
    for agent_type, agent in orchestrator.agents.items():
        visualizer.log_message(f"   • {agent.name} - {agent.role}", "text_secondary")
    
    # Run the demo
    try:
        run_demo(orchestrator, visualizer)
        show_summary(orchestrator, visualizer)
        
        # Ask user if they want to see detailed results
        visualizer.log_message("🔍 Press 'y' + Enter in console for detailed results", "info")
        response = input("\n🔍 Would you like to see detailed task results? (y/n): ")
        if response.lower().startswith('y'):
            show_task_details(orchestrator, visualizer)
        
        # Keep visualization running
        visualizer.log_message("🎮 CarMax Store System is running!", "success")
        visualizer.log_message("📊 Graphics panel shows team network and status", "info")
        visualizer.log_message("📝 Text panel shows all system output", "info")
        visualizer.log_message("🎮 Use controls: ↑↓ scroll, Space: auto-scroll, D: details", "info")
        
        # Wait for user to finish viewing
        input("\n📋 Press Enter to close the store system and exit...")
        
    except KeyboardInterrupt:
        visualizer.log_message("⚠️ Demo interrupted by user", "error")
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        visualizer.log_message(f"❌ Demo error: {str(e)}", "error")
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop the visualizer
        print("\n🔄 Closing store system...")
        visualizer.stop()
        print("👋 Thanks for trying the CarMax Store Demo!")

if __name__ == "__main__":
    main()
