#!/usr/bin/env python3
"""
Ollama Interaction Demo for CarMax Store System
===============================================

This demo specifically showcases Ollama interactions with visual feedback
in the pygame interface. Watch the animated connections between agents
and the Ollama server as requests and responses flow back and forth.

Features:
- Visual Ollama server node
- Animated request/response lines
- Real-time interaction tracking
- Status indicators and counters

Usage:
    python ollama_demo.py

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
    print("           🤖 OLLAMA INTERACTION DEMO 🤖")
    print("")
    print("     CarMax Store System with Ollama Visualization")
    print("")
    print("  Watch the animated connections between agents and Ollama!")
    print("=" * 70)

def run_ollama_demo():
    """Run the Ollama interaction demo"""
    print_banner()
    
    print("🔧 Initializing CarMax Store System...")
    orchestrator = AgentOrchestrator()
    
    print("🎮 Starting Ollama interaction visualization...")
    print("   (A pygame window will open showing agent-Ollama interactions)")
    
    # Create the unified visualizer
    visualizer = UnifiedVisualizer(orchestrator)
    visualizer.start()
    
    # Wait for visualization to start
    time.sleep(2)
    
    print("\n🚀 Starting Ollama interaction demo...")
    print("   Watch the pygame window for animated connections!")
    print("   Requests appear as orange particles moving TO Ollama")
    print("   Responses appear as green particles moving FROM Ollama")
    print("   The Ollama node will pulse and change colors based on activity\n")
    
    # Demo tasks that will generate Ollama interactions
    demo_tasks = [
        ("sales", "What are the key features of a 2020 Honda CR-V?"),
        ("appraisal", "Evaluate a 2018 Toyota Camry with 45,000 miles"),
        ("finance", "Create a financing plan for a $22,000 vehicle"),
        ("manager", "Review our customer satisfaction metrics"),
        ("sales", "Compare SUVs vs sedans for a family of 4"),
        ("appraisal", "Assess trade-in value for a 2019 Ford F-150"),
        ("finance", "Explain APR vs flat rate financing"),
        ("manager", "Analyze our inventory turnover rate"),
        ("sales", "Help customer choose between hybrid and gas vehicles"),
        ("appraisal", "Inspect a vehicle with minor accident history"),
    ]
    
    try:
        # Create and process tasks with delays to show interactions
        for i, (agent_type, description) in enumerate(demo_tasks, 1):
            print(f"🎯 Creating task {i}/10: {agent_type.upper()} - {description[:40]}...")
            
            # Create and assign task
            task = orchestrator.create_task(description, agent_type)
            
            # Show task creation in visualizer
            agent = orchestrator.agents[agent_type]
            visualizer.update_current_task(task, agent.name, agent_type)
            
            # Process the task (this will trigger Ollama interactions)
            result = orchestrator.assign_task(task)
            
            # Show completion in visualizer
            visualizer.task_completed(task, result)
            visualizer.clear_current_task()
            
            print(f"   ✅ Completed! Watch the Ollama interactions in the pygame window.")
            
            # Delay between tasks to see interactions clearly
            if i < len(demo_tasks):
                print(f"   ⏳ Waiting 3 seconds before next task...\n")
                time.sleep(3)
        
        print("\n🎉 Demo completed! All Ollama interactions visualized.")
        print("   The pygame window will remain open for you to observe.")
        print("   You can see:")
        print("   - Total Ollama requests made")
        print("   - Current Ollama status")
        print("   - Agent completion counts")
        print("   - Interaction history in the text panel")
        print("\n   Press any key in the pygame window or Ctrl+C here to exit.")
        
        # Keep the demo running
        while True:
            time.sleep(1)
            if not visualizer.running:
                break
    
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        print("🔌 Shutting down visualization...")
        visualizer.stop()
        print("👋 Goodbye!")

if __name__ == "__main__":
    run_ollama_demo()
