#!/usr/bin/env python3
"""
Minimal test to isolate pygame color errors
"""

import pygame
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_system import AgentOrchestrator

def test_pygame_basic():
    """Test basic pygame functionality"""
    print("Testing basic pygame...")
    
    # Initialize pygame
    pygame.init()
    
    # Set up display
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Basic Pygame Test")
    
    # Test colors
    colors = {
        'background': (5, 5, 15),
        'text': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255)
    }
    
    print("Testing color rendering...")
    clock = pygame.time.Clock()
    
    for i in range(10):  # Draw 10 frames to test
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Test drawing with colors
        screen.fill(colors['background'])
        
        # Draw some test shapes
        pygame.draw.circle(screen, colors['red'], (100, 100), 50)
        pygame.draw.circle(screen, colors['green'], (200, 100), 50)
        pygame.draw.circle(screen, colors['blue'], (300, 100), 50)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✓ Basic pygame test passed!")

def test_unified_visualizer_minimal():
    """Test minimal UnifiedVisualizer creation"""
    print("Testing minimal UnifiedVisualizer...")
    
    try:
        from unified_visualizer import UnifiedVisualizer
        orchestrator = AgentOrchestrator()
        
        # Try to create the visualizer (this might be where the error occurs)
        print("Creating UnifiedVisualizer...")
        visualizer = UnifiedVisualizer(orchestrator, width=800, height=600)
        print("✓ UnifiedVisualizer created successfully!")
        
        # Try to access some basic properties
        print(f"Colors defined: {len(visualizer.colors)}")
        print(f"Background color: {visualizer.colors['background']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating UnifiedVisualizer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Pygame Color Error Debug ===")
    
    # Test 1: Basic pygame functionality
    test_pygame_basic()
    
    # Test 2: UnifiedVisualizer creation
    success = test_unified_visualizer_minimal()
    
    if success:
        print("\n✓ All tests passed - the issue might be in the visualization loop")
    else:
        print("\n✗ Error occurs during UnifiedVisualizer creation")
