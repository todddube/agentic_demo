#!/usr/bin/env python3
"""
Test script to verify the resize handle functionality for agent nodes.
"""

import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_visualizer import UnifiedVisualizer
from agent_system import AgentOrchestrator

def test_resize_functionality():
    """Test the resize functionality in a minimal setup"""
    print("Testing agent resize functionality...")
    
    # Create a simple orchestrator
    orchestrator = AgentOrchestrator()
    
    # Create the visualizer
    visualizer = UnifiedVisualizer(orchestrator, width=1200, height=800)
    
    # Test the helper functions
    print("Testing helper functions...")
    
    # Test get_agent_radius with default size
    sales_radius = visualizer.get_agent_radius('sales')
    print(f"Sales agent default radius: {sales_radius}")
    
    # Test custom size setting
    visualizer.agent_custom_sizes['sales'] = 80
    custom_radius = visualizer.get_agent_radius('sales')
    print(f"Sales agent custom radius: {custom_radius}")
    
    # Test resize handle position
    if 'sales' in visualizer.agent_positions:
        sales_pos = visualizer.agent_positions['sales']
        handle_pos = visualizer.get_resize_handle_pos(sales_pos, custom_radius)
        print(f"Sales agent handle position: {handle_pos}")
        
        # Test resize handle detection
        is_on_handle = visualizer.is_mouse_on_resize_handle(handle_pos, 'sales')
        print(f"Mouse on handle test: {is_on_handle}")
    
    # Test save/load functionality
    print("Testing save/load functionality...")
    visualizer.agent_custom_sizes['finance'] = 100
    visualizer.agent_custom_sizes['manager'] = 60
    
    # Save the data
    visualizer.save_agent_positions()
    
    # Clear and reload
    original_sizes = visualizer.agent_custom_sizes.copy()
    visualizer.agent_custom_sizes.clear()
    print(f"Cleared sizes: {visualizer.agent_custom_sizes}")
    
    # Reload
    visualizer.load_agent_positions()
    print(f"Reloaded sizes: {visualizer.agent_custom_sizes}")
    
    # Verify they match
    if visualizer.agent_custom_sizes == original_sizes:
        print("✓ Save/load test passed!")
    else:
        print("✗ Save/load test failed!")
    
    print("Basic functionality tests completed!")
    print("\nTo test interactively:")
    print("1. Run the full demo: python simple_demo.py")
    print("2. Click START DEMO")
    print("3. Try dragging the resize handles (◢) at bottom-right of each agent")
    print("4. Press R to reset positions and sizes")
    print("5. Press ESC to quit")

if __name__ == "__main__":
    test_resize_functionality()
