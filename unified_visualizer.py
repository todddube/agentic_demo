import pygame
import math
import time
import threading
from typing import Dict, List, Tuple, Optional
from enum import Enum
import queue
import textwrap
import json
import os
import random

# Initialize Pygame
pygame.init()

class AnimationType(Enum):
    PULSE = "pulse"
    ROTATE = "rotate"
    GLOW = "glow"
    PARTICLE = "particle"

class UnifiedVisualizer:
    def __init__(self, orchestrator, width=None, height=None):
        self.orchestrator = orchestrator
        
        # Auto-calculate screen size to 75% of display resolution
        if width is None or height is None:
            pygame.display.init()  # Initialize display module to get screen info
            info = pygame.display.Info()
            self.width = int(info.current_w * 0.90)
            self.height = int(info.current_h * 0.85)
        else:
            self.width = width
            self.height = height
            
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        
        # Layout configuration
        self.min_graphics_width = int(self.width * 0.4)  # Minimum 40% for graphics
        self.max_graphics_width = int(self.width * 0.8)  # Maximum 80% for graphics
        self.graphics_width = int(self.width * 0.6)      # Default 60% for graphics
        self.text_width = self.width - self.graphics_width  # Remaining for text
        self.panel_padding = 10
        
        # Resizing state
        self.is_resizing = False
        self.resize_start_x = 0
        self.resize_original_width = 0
        
        # Dragging state for agent nodes
        self.is_dragging = False
        self.dragged_agent = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_start_pos = None
        
        # Colors
        self.colors = {
            'background': (15, 15, 25),
            'panel_bg': (25, 25, 35),
            'panel_border': (60, 60, 80),
            'text': (255, 255, 255),
            'text_secondary': (180, 180, 200),
            'text_dim': (120, 120, 140),
            'sales': (255, 107, 107),          # Red - Sales Consultant
            'appraisal': (78, 205, 196),       # Teal - Appraisal Manager
            'finance': (69, 183, 209),         # Blue - Finance Manager
            'manager': (150, 206, 180),        # Green - Store Manager
            'orchestrator': (255, 215, 0),     # Gold
            'ollama': (138, 43, 226),          # Blue Violet - Ollama Server
            'connection': (100, 100, 150),
            'active': (255, 255, 0),           # Yellow for active
            'completed': (0, 255, 0),          # Green for completed
            'working': (255, 165, 0),          # Orange for working
            'success': (0, 200, 0),
            'error': (200, 0, 0),
            'info': (100, 150, 255),
            'request': (255, 140, 0),          # Dark orange for requests
            'response': (50, 205, 50),         # Lime green for responses
        }
        
        # Text output system (initialize early for position loading messages)
        self.text_lines = []
        self.max_text_lines = 50
        self.text_scroll_offset = 0
        self.auto_scroll = True
        self.text_wrap_width = 45  # Will be updated based on font size
        
        # Agent positions (circular layout in graphics panel)
        self.agent_positions = {}
        self.positions_file = "agent_positions.json"
        self.setup_agent_positions()
        
        # Ollama interaction tracking
        self.ollama_interactions = []  # Store recent interactions
        self.ollama_status = "idle"    # idle, processing, error
        self.ollama_request_count = 0
        self.ollama_last_activity = None
        self.interaction_animations = []  # For animated lines between agents and Ollama
        
        # Animation state
        self.animations = {}
        self.particles = []
        self.time_offset = 0
        
        # Floating response windows
        self.floating_responses = []  # List of floating response windows
        self.show_floating_responses = True  # Toggle for floating responses
        
        # Task display
        self.current_task = None
        self.task_history = []
        self.task_queue = queue.Queue()
        
        # Fonts - will be updated based on panel size
        self.base_font_sizes = {
            'title': 32,
            'large': 28,
            'medium': 20,
            'small': 16,
            'mono': 18
        }
        
        # Font scaling factors (1.0 = normal size)
        self.main_font_scale = 1.0  # For main graphics panel fonts
        self.output_font_scale = 1.0  # For output panel text
        self.min_font_scale = 0.5
        self.max_font_scale = 2.0
        self.font_scale_step = 0.1
        
        # Try to use a better monospace font if available
        self.mono_font_name = None
        try:
            pygame.font.SysFont('consolas', 16)  # Test if Consolas is available
            self.mono_font_name = 'consolas'
        except:
            try:
                pygame.font.SysFont('courier', 16)  # Test if Courier is available
                self.mono_font_name = 'courier'
            except:
                self.mono_font_name = None
        
        # Now update fonts
        self.update_fonts()
        
        # UI State
        self.show_details = True
        self.last_fps_update = 0
        self.fps_display = 60
        
        # Start screen state
        self.demo_state = "start_screen"  # "start_screen", "running", "completed"
        self.start_button_rect = None
        self.demo_callback = None  # Callback to start the actual demo
    
    def setup_agent_positions(self):
        """Setup agent positions - load from file if available, otherwise use default circular layout"""
        # Try to load saved positions first
        if self.load_agent_positions():
            return
        
        # Fallback to default circular layout
        self.create_default_agent_positions()
    
    def create_default_agent_positions(self):
        """Create default circular positions for agents in the graphics panel"""
        # Center of graphics panel
        center_x = self.graphics_width // 2
        center_y = self.height // 2
        radius = min(self.graphics_width, self.height) // 4
        
        agents = ['sales', 'appraisal', 'finance', 'manager']
        angle_step = 2 * math.pi / len(agents)
        
        for i, agent_type in enumerate(agents):
            angle = i * angle_step - math.pi / 2  # Start from top
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.agent_positions[agent_type] = (int(x), int(y))
        
        # Orchestrator at center
        self.agent_positions['orchestrator'] = (center_x, center_y)
        
        # Ollama server positioned in top right corner of graphics panel
        ollama_margin = 80
        ollama_x = self.graphics_width - ollama_margin
        ollama_y = ollama_margin
        self.agent_positions['ollama'] = (int(ollama_x), int(ollama_y))
    
    def load_agent_positions(self):
        """Load agent positions from JSON file"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r') as f:
                    saved_positions = json.load(f)
                
                # Validate that all required agents are present
                required_agents = ['sales', 'appraisal', 'finance', 'manager', 'orchestrator', 'ollama']
                if all(agent in saved_positions for agent in required_agents):
                    # Convert list tuples back to tuples and validate positions
                    for agent, pos in saved_positions.items():
                        if isinstance(pos, list) and len(pos) == 2:
                            # Ensure positions are within current graphics panel bounds
                            x, y = pos
                            x = max(50, min(self.graphics_width - 50, x))
                            y = max(50, min(self.height - 50, y))
                            self.agent_positions[agent] = (int(x), int(y))
                        else:
                            return False  # Invalid position format
                    
                    self.add_text("[FOLDER] Loaded saved agent positions", "info")
                    return True
        except Exception as e:
            self.add_text(f"[WARN] Error loading positions: {e}", "error")
        
        return False
    
    def save_agent_positions(self):
        """Save current agent positions to JSON file"""
        try:
            # Convert tuples to lists for JSON serialization
            positions_to_save = {agent: list(pos) for agent, pos in self.agent_positions.items()}
            
            with open(self.positions_file, 'w') as f:
                json.dump(positions_to_save, f, indent=2)
            
            self.add_text("[SAVE] Agent positions saved", "info")
        except Exception as e:
            self.add_text(f"[WARN] Error saving positions: {e}", "error")
    
    def start(self):
        """Start the visualization in a separate thread"""
        if not self.running:
            self.running = True
            self.add_text("[START] Starting unified pygame visualization...", "info")
            
            # Set up Ollama interaction callback
            self.orchestrator.set_ollama_callback(self.handle_ollama_interaction)
            
            self.visualization_thread = threading.Thread(target=self.run_visualization, daemon=True)
            self.visualization_thread.start()
    
    def stop(self):
        """Stop the visualization"""
        self.running = False
        if hasattr(self, 'visualization_thread'):
            self.visualization_thread.join(timeout=1.0)
        if self.screen:
            pygame.quit()
    
    def add_text(self, text, message_type="info"):
        """Add text to the output panel"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Color based on message type
        color = self.colors.get(message_type, self.colors['text'])
        
        # Wrap long lines using dynamic wrap width
        wrapped_lines = textwrap.wrap(text, width=self.text_wrap_width)
        if not wrapped_lines:
            wrapped_lines = [text]
            
        for i, line in enumerate(wrapped_lines):
            prefix = f"[{timestamp}] " if i == 0 else "          "
            full_line = prefix + line
            
            self.text_lines.append({
                'text': full_line,
                'color': color,
                'timestamp': time.time()
            })
        
        # Keep only recent lines
        if len(self.text_lines) > self.max_text_lines:
            self.text_lines = self.text_lines[-self.max_text_lines:]
        
        # Auto-scroll to bottom
        if self.auto_scroll:
            self.text_scroll_offset = 0
    
    def handle_ollama_interaction(self, interaction_type: str, data: dict):
        """Handle Ollama interactions for visualization"""
        self.ollama_request_count += 1
        self.ollama_last_activity = time.time()
        
        if interaction_type == "request":
            self.ollama_status = "processing"
            self.add_text(f"[AI-REQ] Ollama Request #{data['request_id']}: {data['model']} (prompt: {data['prompt_length']} chars)", "request")
            
            # Add animation for request
            self.add_interaction_animation("request", data.get('agent_type', 'orchestrator'))
            
        elif interaction_type == "response":
            if data['success']:
                self.ollama_status = "idle"
                self.add_text(f"[OK] Ollama Response #{data['request_id']}: {data['response_length']} chars", "response")
                
                # Add floating response window for Ollama response
                agent_type = data.get('agent_type', 'orchestrator')
                if 'response' in data and data['response']:
                    self.add_floating_response(agent_type, f"[AI] Ollama: {data['response'][:60]}...")
                
                # Add animation for response
                self.add_interaction_animation("response", agent_type)
            
        elif interaction_type == "error":
            self.ollama_status = "error"
            self.add_text(f"[ERROR] Ollama Error #{data['request_id']}: {data['error']}", "error")
            
            # Add error animation
            self.add_interaction_animation("error", data.get('agent_type', 'orchestrator'))
        
        # Store interaction for history
        self.ollama_interactions.append({
            'type': interaction_type,
            'data': data,
            'timestamp': time.time()
        })
        
        # Keep only recent interactions
        if len(self.ollama_interactions) > 50:
            self.ollama_interactions = self.ollama_interactions[-50:]
    
    def add_interaction_animation(self, animation_type: str, agent_type: str = None):
        """Add an animated line that follows agent -> orchestrator -> Ollama path"""
        if agent_type and agent_type in self.agent_positions and agent_type not in ['orchestrator', 'ollama']:
            # Multi-segment animation: agent -> orchestrator -> Ollama
            agent_pos = self.agent_positions[agent_type]
            orchestrator_pos = self.agent_positions['orchestrator']
            ollama_pos = self.agent_positions['ollama']
            
            # Create path segments
            segments = [
                {'start': agent_pos, 'end': orchestrator_pos},  # Agent to orchestrator
                {'start': orchestrator_pos, 'end': ollama_pos}  # Orchestrator to Ollama
            ]
        else:
            # Simple animation: orchestrator -> Ollama (for direct orchestrator requests)
            orchestrator_pos = self.agent_positions['orchestrator']
            ollama_pos = self.agent_positions['ollama']
            segments = [
                {'start': orchestrator_pos, 'end': ollama_pos}
            ]
        
        # Determine color based on interaction type
        if animation_type == "request":
            color = self.colors['request']
        elif animation_type == "response":
            color = self.colors['response']
        elif animation_type == "error":
            color = self.colors['error']
        else:
            color = self.colors['connection']
        
        # Add multi-segment animated line
        self.interaction_animations.append({
            'segments': segments,
            'color': color,
            'progress': 0.0,
            'direction': 1 if animation_type == "request" else -1,  # 1 for to Ollama, -1 for from Ollama
            'life': 180,  # Increased frames for multi-segment animation
            'type': animation_type,
            'agent_type': agent_type
        })
    
    def run_visualization(self):
        """Main visualization loop"""
        try:
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("CarMax Store System - Team Interface")
            
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        self.add_text("[CLOSE] Pygame window closed - shutting down application...", "info")
                        return  # Exit the thread cleanly                       
                    elif event.type == pygame.KEYDOWN:
                        # Check for Ctrl key combinations
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                            self.handle_ctrl_keypress(event.key)
                        else:
                            self.handle_keypress(event.key)
                    elif event.type == pygame.MOUSEWHEEL:
                        self.handle_scroll(event.y)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_mouse_down(event.pos, event.button)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.handle_mouse_up(event.pos, event.button)
                    elif event.type == pygame.MOUSEMOTION:
                        self.handle_mouse_motion(event.pos)
                
                # Update animations
                self.update_animations()
                
                # Draw everything
                self.draw_frame()
                
                # Control frame rate
                self.clock.tick(60)
                
        except Exception as e:
            print(f"Visualization error: {e}")
        finally:
            if self.screen:
                pygame.quit()
            self.running = False  # Ensure running is False when thread exits
    
    def handle_keypress(self, key):
        """Handle keyboard input"""
        if key == pygame.K_SPACE:
            if self.demo_state == "start_screen":
                self.start_demo()
            else:
                self.auto_scroll = not self.auto_scroll
        elif key == pygame.K_UP:
            self.text_scroll_offset = min(self.text_scroll_offset + 1, len(self.text_lines) - 1)
            self.auto_scroll = False
        elif key == pygame.K_DOWN:
            self.text_scroll_offset = max(self.text_scroll_offset - 1, 0)
        elif key == pygame.K_HOME:
            self.text_scroll_offset = len(self.text_lines) - 1
            self.auto_scroll = False
        elif key == pygame.K_END:
            self.text_scroll_offset = 0
            self.auto_scroll = True
        elif key == pygame.K_d:
            self.show_details = not self.show_details
        elif key == pygame.K_r:
            # R key to reset agent positions to default
            self.create_default_agent_positions()
            self.save_agent_positions()
            self.add_text("[RESET] Agent positions reset to default layout", "info")
        elif key == pygame.K_f:
            # F key to toggle floating response windows
            self.show_floating_responses = not self.show_floating_responses
            status = "ON" if self.show_floating_responses else "OFF"
            self.add_text(f"[FLOAT] Floating response windows: {status}", "info")
        elif key == pygame.K_ESCAPE:
            # ESC key to quit
            self.add_text("[EXIT] ESC pressed - shutting down application...", "info")
            self.running = False
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks"""
        if self.demo_state == "start_screen" and self.start_button_rect:
            if self.start_button_rect.collidepoint(pos):
                self.start_demo()
    
    def handle_mouse_down(self, pos, button):
        """Handle mouse button down events"""
        # Handle start screen button
        if self.demo_state == "start_screen" and self.start_button_rect:
            if self.start_button_rect.collidepoint(pos):
                self.start_demo()
                return
        
        # Handle panel resizing (left mouse button)
        if button == 1:  # Left mouse button
            mouse_x, mouse_y = pos
            
            # Check if clicking near the panel divider
            if abs(mouse_x - self.graphics_width) <= 5:
                self.is_resizing = True
                self.resize_start_x = mouse_x
                self.resize_original_width = self.graphics_width
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            else:
                # Check if clicking on an agent for dragging
                agent_type = self.get_agent_at_position(pos)
                if agent_type:
                    self.is_dragging = True
                    self.dragged_agent = agent_type
                    self.drag_start_pos = pos
                    
                    # Calculate offset from agent center
                    agent_pos = self.agent_positions[agent_type]
                    self.drag_offset_x = mouse_x - agent_pos[0]
                    self.drag_offset_y = mouse_y - agent_pos[1]
                    
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    
    def handle_mouse_up(self, pos, button):
        """Handle mouse button up events"""
        if button == 1:  # Left mouse button
            if self.is_resizing:
                self.is_resizing = False
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif self.is_dragging:
                # Complete the drag operation
                self.is_dragging = False
                
                # Check if agent was actually moved (not just a click)
                if self.drag_start_pos:
                    drag_distance = math.sqrt(
                        (pos[0] - self.drag_start_pos[0]) ** 2 + 
                        (pos[1] - self.drag_start_pos[1]) ** 2
                    )
                    
                    if drag_distance > 5:  # Minimum drag distance to count as a move
                        self.save_agent_positions()
                        self.add_text(f"📍 Moved {self.dragged_agent} agent to new position", "info")
                
                self.dragged_agent = None
                self.drag_start_pos = None
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def handle_mouse_motion(self, pos):
        """Handle mouse motion events"""
        mouse_x, mouse_y = pos
        
        if self.is_resizing:
            # Calculate new panel width
            delta_x = mouse_x - self.resize_start_x
            new_graphics_width = self.resize_original_width + delta_x
            
            # Clamp to min/max values
            new_graphics_width = max(self.min_graphics_width, min(self.max_graphics_width, new_graphics_width))
            
            # Update panel widths
            if new_graphics_width != self.graphics_width:
                self.graphics_width = new_graphics_width
                self.text_width = self.width - self.graphics_width
                # Update fonts based on new text panel width
                self.update_fonts()
                # Only recalculate positions if using default layout (no saved positions)
                if not os.path.exists(self.positions_file):
                    self.create_default_agent_positions()
        elif self.is_dragging and self.dragged_agent:
            # Update agent position while dragging
            new_x = mouse_x - self.drag_offset_x
            new_y = mouse_y - self.drag_offset_y
            new_pos = self.constrain_agent_position((new_x, new_y))
            self.agent_positions[self.dragged_agent] = new_pos
        else:
            # Show appropriate cursor when hovering
            if abs(mouse_x - self.graphics_width) <= 5:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            elif self.get_agent_at_position(pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def get_agent_at_position(self, pos):
        """Check if mouse position is over an agent node"""
        mouse_x, mouse_y = pos
        
        for agent_type, agent_pos in self.agent_positions.items():
            # Skip ollama server as it's not draggable
            if agent_type == 'ollama':
                continue
                
            agent_x, agent_y = agent_pos
            # Check if mouse is within agent radius (45 pixels base radius)
            distance = math.sqrt((mouse_x - agent_x) ** 2 + (mouse_y - agent_y) ** 2)
            if distance <= 45:  # Base radius from draw_agent method
                return agent_type
        
        return None
    
    def constrain_agent_position(self, pos):
        """Constrain agent position to stay within graphics panel bounds"""
        x, y = pos
        margin = 50  # Keep agents away from edges
        
        x = max(margin, min(self.graphics_width - margin, x))
        y = max(margin, min(self.height - margin, y))
        
        return (int(x), int(y))
    
    def update_animations(self):
        """Update all animations"""
        self.time_offset = time.time()
        
        # Update particles
        self.particles = [p for p in self.particles if p['life'] > 0]
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['alpha'] = max(0, particle['alpha'] - 2)
        
        # Update interaction animations
        self.interaction_animations = [anim for anim in self.interaction_animations if anim['life'] > 0]
        for anim in self.interaction_animations:
            anim['progress'] += 0.02  # Animation speed
            anim['life'] -= 1
            
            # Clamp progress
            anim['progress'] = max(0.0, min(1.0, anim['progress']))
        
        # Update Ollama status based on recent activity
        if self.ollama_last_activity:
            time_since_activity = time.time() - self.ollama_last_activity
            if time_since_activity > 3.0 and self.ollama_status == "processing":
                self.ollama_status = "idle"
        
        # Update FPS display
        if time.time() - self.last_fps_update > 1.0:
            self.fps_display = int(self.clock.get_fps())
            self.last_fps_update = time.time()
        
        # Update floating responses
        self.update_floating_responses()
    
    def draw_frame(self):
        """Draw a complete frame"""
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Draw panels
        self.draw_graphics_panel()
        self.draw_text_panel()
        
        # Draw panel separator with resize handle
        self.draw_panel_separator()
        
        # Update display
        pygame.display.flip()
    
    def draw_panel_separator(self):
        """Draw the resizable panel separator"""
        # Main separator line
        separator_color = self.colors['panel_border']
        if self.is_resizing:
            separator_color = self.colors['active']
        
        pygame.draw.line(self.screen, separator_color, 
                        (self.graphics_width, 0), (self.graphics_width, self.height), 3)
        
        # Draw resize handle in the middle
        handle_size = 20
        handle_x = self.graphics_width - handle_size // 2
        handle_y = self.height // 2 - handle_size // 2
        handle_rect = pygame.Rect(handle_x, handle_y, handle_size, handle_size)
        
        # Handle background
        handle_color = self.colors['panel_bg'] if not self.is_resizing else self.colors['active']
        pygame.draw.rect(self.screen, handle_color, handle_rect, border_radius=5)
        pygame.draw.rect(self.screen, separator_color, handle_rect, 2, border_radius=5)
        
        # Draw resize indicator (three vertical lines)
        for i in range(3):
            line_x = handle_x + 6 + i * 3
            pygame.draw.line(self.screen, separator_color, 
                           (line_x, handle_y + 4), (line_x, handle_y + handle_size - 4), 1)
    
    def draw_graphics_panel(self):
        """Draw the graphics panel with agent visualization"""
        # Panel background
        graphics_rect = pygame.Rect(0, 0, self.graphics_width, self.height)
        pygame.draw.rect(self.screen, self.colors['panel_bg'], graphics_rect)
        pygame.draw.rect(self.screen, self.colors['panel_border'], graphics_rect, 2)
        
        if self.demo_state == "start_screen":
            self.draw_start_screen()
        else:
            # Title
            title = self.font_title.render("CarMax Store Network", True, self.colors['text'])
            title_rect = title.get_rect(centerx=self.graphics_width//2, y=20)
            self.screen.blit(title, title_rect)
            
            # Draw connections between agents
            self.draw_connections()
            
            # Draw interaction animations
            self.draw_interaction_animations()
            
            # Draw orchestrator
            self.draw_orchestrator()
            
            # Draw agents
            self.draw_agents()
            
            # Draw Ollama server
            self.draw_ollama()
            
            # Draw particles
            self.draw_particles()
            
            # Draw floating response windows
            self.draw_floating_responses()
            
            # Draw current task info in graphics panel
            self.draw_current_task_overlay()
            
            # Draw graphics panel stats
            self.draw_graphics_stats()
    
    def draw_start_screen(self):
        """Draw the start screen with title and start button"""
        center_x = self.graphics_width // 2
        center_y = self.height // 2
        
        # Main title
        title = self.font_title.render("CarMax Store Demo", True, self.colors['text'])
        title_rect = title.get_rect(centerx=center_x, y=center_y - 120)
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_large.render("Multi-Agent AI System", True, self.colors['text_secondary'])
        subtitle_rect = subtitle.get_rect(centerx=center_x, y=center_y - 80)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Team description
        team_lines = [
            "Team Members:",
            "[CAR] Mike Rodriguez - Sales Consultant",
            "[DOC] Sarah Chen - Appraisal Manager", 
            "[$$$] David Williams - Finance Manager",
            "[MGR] Jennifer Thompson - Store Manager",
            "[AI] Ollama AI Server - llama3.2"
        ]
        
        for i, line in enumerate(team_lines):
            color = self.colors['text'] if i == 0 else self.colors['text_secondary']
            font = self.font_medium if i == 0 else self.font_small
            text = font.render(line, True, color)
            text_rect = text.get_rect(centerx=center_x, y=center_y - 20 + i * 20)
            self.screen.blit(text, text_rect)
        
        # Start button
        button_width = 200
        button_height = 50
        button_x = center_x - button_width // 2
        button_y = center_y + 80
        
        self.start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Button glow effect
        glow_color = (*self.colors['success'], 100)
        for i in range(3):
            glow_rect = pygame.Rect(button_x - i*2, button_y - i*2, button_width + i*4, button_height + i*4)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
            self.screen.blit(glow_surface, glow_rect)
        
        # Main button
        pygame.draw.rect(self.screen, self.colors['success'], self.start_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['text'], self.start_button_rect, 3, border_radius=10)
        
        # Button text
        button_text = self.font_large.render("START DEMO", True, self.colors['text'])
        button_text_rect = button_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Instructions
        instructions = [
            "Click the button above or press SPACE to start",
            "ESC to quit at any time"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, self.colors['text_dim'])
            text_rect = text.get_rect(centerx=center_x, y=center_y + 160 + i * 20)
            self.screen.blit(text, text_rect)
    
    def draw_text_panel(self):
        """Draw the text output panel"""
        # Panel background
        text_rect = pygame.Rect(self.graphics_width, 0, self.text_width, self.height)
        pygame.draw.rect(self.screen, self.colors['panel_bg'], text_rect)
        pygame.draw.rect(self.screen, self.colors['panel_border'], text_rect, 2)
        
        # Title
        title = self.font_large.render("System Output", True, self.colors['text'])
        title_rect = title.get_rect(centerx=self.graphics_width + self.text_width//2, y=15)
        self.screen.blit(title, title_rect)
        
        # Draw text lines
        start_y = 50
        line_height = 20  # Increased from 16 to 20 for better spacing with larger font
        visible_lines = (self.height - start_y - 50) // line_height
        
        # Calculate which lines to show
        total_lines = len(self.text_lines)
        if total_lines <= visible_lines:
            start_idx = 0
            end_idx = total_lines
        else:
            start_idx = max(0, total_lines - visible_lines - self.text_scroll_offset)
            end_idx = total_lines - self.text_scroll_offset
        
        # Draw visible text lines
        for i, line_idx in enumerate(range(start_idx, end_idx)):
            if line_idx < len(self.text_lines):
                line_data = self.text_lines[line_idx]
                y_pos = start_y + i * line_height
                
                # Fade older lines
                age = time.time() - line_data['timestamp']
                alpha = max(0.4, 1.0 - age / 30.0)  # Increased minimum alpha from 0.3 to 0.4
                
                # Render text with alpha and antialiasing for better readability
                text_surface = self.font_mono.render(line_data['text'], True, line_data['color'])
                if alpha < 1.0:
                    text_surface.set_alpha(int(alpha * 255))
                
                # Clip text to panel width
                text_x = self.graphics_width + 15  # Increased margin from 10 to 15
                max_width = self.text_width - 30   # Increased margin from 20 to 30
                if text_surface.get_width() > max_width:
                    # Instead of scaling, clip the text cleanly
                    clipped_surface = pygame.Surface((max_width, text_surface.get_height()), pygame.SRCALPHA)
                    clipped_surface.blit(text_surface, (0, 0))
                    text_surface = clipped_surface
                
                self.screen.blit(text_surface, (text_x, y_pos))
        
        # Draw scroll indicator
        if total_lines > visible_lines:
            self.draw_scroll_indicator(start_y, visible_lines, line_height)
        
        # Draw text panel controls
        self.draw_text_controls()
    
    def draw_scroll_indicator(self, start_y, visible_lines, line_height):
        """Draw scroll bar indicator"""
        total_lines = len(self.text_lines)
        scroll_area_height = visible_lines * line_height
        
        # Scroll bar background
        scroll_x = self.graphics_width + self.text_width - 15
        scroll_rect = pygame.Rect(scroll_x, start_y, 10, scroll_area_height)
        pygame.draw.rect(self.screen, (40, 40, 50), scroll_rect)
        
        # Scroll thumb
        thumb_height = max(20, int(scroll_area_height * visible_lines / total_lines))
        thumb_pos = start_y + int((scroll_area_height - thumb_height) * self.text_scroll_offset / max(1, total_lines - visible_lines))
        
        thumb_rect = pygame.Rect(scroll_x + 1, thumb_pos, 8, thumb_height)
        pygame.draw.rect(self.screen, (100, 100, 120), thumb_rect)
    
    def draw_text_controls(self):
        """Draw text panel controls"""
        controls_y = self.height - 130  # Moved up to accommodate more lines
        control_text = [
            "Controls: ↑↓ Scroll | Home/End | Space: Auto-scroll | D: Details | ESC: Quit",
            "Font scaling: Ctrl++ / Ctrl+- (hover over panel to select) | Ctrl+0 to reset",
            "Resize panels: Drag the separator line between panels",
            "Drag agents: Click and drag agent nodes to reposition them",
            "Reset positions: Press R to restore default agent layout",
            "Toggle floating responses: Press F to enable/disable response windows",
            f"Auto-scroll: {'ON' if self.auto_scroll else 'OFF'} | Floating: {'ON' if self.show_floating_responses else 'OFF'} | Lines: {len(self.text_lines)}",
            f"Font scales - Main: {self.main_font_scale:.1f}x | Output: {self.output_font_scale:.1f}x"
        ]
        
        for i, text in enumerate(control_text):
            # Use medium font for better readability of controls
            surface = self.font_medium.render(text, True, self.colors['text_dim'])
            self.screen.blit(surface, (self.graphics_width + 15, controls_y + i * 16))
    
    def draw_connections(self):
        """Draw connections between agents"""
        center = self.agent_positions['orchestrator']
        
        for agent_type, pos in self.agent_positions.items():
            if agent_type != 'orchestrator':
                # Draw line to center
                color = self.colors['connection']
                alpha = 50 + 30 * math.sin(self.time_offset * 2 + hash(agent_type) % 10)
                
                # Create surface for alpha blending
                line_surface = pygame.Surface((self.graphics_width, self.height), pygame.SRCALPHA)
                pygame.draw.line(line_surface, (*color, int(alpha)), center, pos, 2)
                self.screen.blit(line_surface, (0, 0))
    
    def draw_orchestrator(self):
        """Draw the central orchestrator"""
        pos = self.agent_positions['orchestrator']
        
        # Pulsing effect
        pulse = 1.0 + 0.2 * math.sin(self.time_offset * 3)
        radius = int(35 * pulse)
        
        # Draw outer glow
        for i in range(5):
            alpha = 50 - i * 10
            glow_radius = radius + i * 4
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.colors['orchestrator'], alpha), 
                             (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, (pos[0] - glow_radius, pos[1] - glow_radius))
        
        # Draw main circle
        pygame.draw.circle(self.screen, self.colors['orchestrator'], pos, radius)
        pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
        
        # Draw label
        text = self.font_small.render("CarMax District Manager", True, self.colors['text'])
        text_rect = text.get_rect(center=(pos[0], pos[1] + radius + 25))
        self.screen.blit(text, text_rect)
    
    def draw_ollama(self):
        """Draw the Ollama server node with a rectangular server-like appearance"""
        pos = self.agent_positions['ollama']
        
        # Server box dimensions
        box_width = 120
        box_height = 80
        corner_radius = 8
        
        # Calculate box position (centered on pos)
        box_x = pos[0] - box_width // 2
        box_y = pos[1] - box_height // 2
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Status-based colors and effects
        if self.ollama_status == "processing":
            pulse = 1.0 + 0.2 * math.sin(self.time_offset * 4)
            glow_intensity = int(50 + 30 * pulse)
            status_color = self.colors['working']
        elif self.ollama_status == "error":
            glow_intensity = 80
            status_color = self.colors['error']
        else:
            glow_intensity = 30
            status_color = self.colors['ollama']
        
        # Draw outer glow/shadow
        for i in range(6):
            alpha = glow_intensity - i * 8
            if alpha > 0:
                glow_rect = pygame.Rect(box_x - i*2, box_y - i*2, 
                                      box_width + i*4, box_height + i*4)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*status_color, alpha), 
                               (0, 0, glow_rect.width, glow_rect.height), 
                               border_radius=corner_radius + i)
                self.screen.blit(glow_surface, glow_rect)
        
        # Draw main server box with gradient effect
        # Dark background
        pygame.draw.rect(self.screen, (20, 20, 30), box_rect, border_radius=corner_radius)
        
        # Lighter top section
        top_rect = pygame.Rect(box_x, box_y, box_width, box_height // 3)
        pygame.draw.rect(self.screen, (40, 40, 50), top_rect, border_top_left_radius=corner_radius, border_top_right_radius=corner_radius)
        
        # Status indicator strip
        status_strip = pygame.Rect(box_x + 5, box_y + 5, box_width - 10, 8)
        pygame.draw.rect(self.screen, status_color, status_strip, border_radius=2)
        
        # Draw server "ports" or connection indicators
        for i in range(3):
            port_x = box_x + 15 + i * 30
            port_y = box_y + box_height - 20
            port_rect = pygame.Rect(port_x, port_y, 20, 10)
            port_color = status_color if self.ollama_status == "processing" else (60, 60, 80)
            pygame.draw.rect(self.screen, port_color, port_rect, border_radius=2)
        
        # Main border
        pygame.draw.rect(self.screen, self.colors['text'], box_rect, 2, border_radius=corner_radius)
        
        # Draw Ollama logo/icon in center
        icon_text = self.font_large.render("AI", True, self.colors['text'])
        icon_rect = icon_text.get_rect(center=(pos[0], pos[1] - 5))
        self.screen.blit(icon_text, icon_rect)
        
        # Draw labels outside the box
        name_text = self.font_medium.render("Ollama Server", True, self.colors['text'])
        name_rect = name_text.get_rect(center=(pos[0], pos[1] + box_height//2 + 20))
        self.screen.blit(name_text, name_rect)
        
        model_text = self.font_small.render("llama3.2", True, self.colors['text_secondary'])
        model_rect = model_text.get_rect(center=(pos[0], pos[1] + box_height//2 + 35))
        self.screen.blit(model_text, model_rect)
        
        # Draw request count
        count_text = self.font_small.render(f"Requests: {self.ollama_request_count}", True, self.colors['text'])
        count_rect = count_text.get_rect(center=(pos[0], pos[1] + box_height//2 + 50))
        self.screen.blit(count_text, count_rect)
        
        # Draw status in top-left corner of graphics panel
        status_text = self.font_small.render(f"Status: {self.ollama_status.upper()}", True, status_color)
        self.screen.blit(status_text, (15, 15))
    
    def draw_interaction_animations(self):
        """Draw animated lines that follow agent -> orchestrator -> Ollama path"""
        for anim in self.interaction_animations:
            if anim['progress'] <= 1.0:
                segments = anim['segments']
                num_segments = len(segments)
                
                # Calculate which segment we're on and progress within that segment
                total_progress = anim['progress']
                if anim['direction'] == -1:  # Response: reverse the direction
                    total_progress = 1.0 - total_progress
                    segments = list(reversed(segments))
                    # Swap start and end for each segment when going in reverse
                    segments = [{'start': seg['end'], 'end': seg['start']} for seg in segments]
                
                # Each segment gets equal time (1/num_segments of total animation)
                segment_duration = 1.0 / num_segments
                current_segment_index = min(num_segments - 1, int(total_progress / segment_duration))
                segment_progress = (total_progress % segment_duration) / segment_duration
                
                # Get current segment
                current_segment = segments[current_segment_index]
                start_pos = current_segment['start']
                end_pos = current_segment['end']
                
                # Calculate current position within the segment
                current_x = start_pos[0] + (end_pos[0] - start_pos[0]) * segment_progress
                current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * segment_progress
                
                # Draw animated line with fade
                alpha = max(50, 255 - (1.0 - anim['progress']) * 200)
                
                # Draw the moving particle
                particle_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
                color_with_alpha = (*anim['color'], int(alpha))
                pygame.draw.circle(particle_surface, color_with_alpha, (6, 6), 6)
                self.screen.blit(particle_surface, (int(current_x - 6), int(current_y - 6)))
                
                # Draw completed segments as fading trails
                for i in range(current_segment_index):
                    segment = segments[i]
                    trail_alpha = int(alpha * 0.3)
                    if trail_alpha > 20:
                        pygame.draw.line(self.screen, (*anim['color'], trail_alpha), 
                                       segment['start'], segment['end'], 2)
                
                # Draw current segment trail
                if segment_progress > 0.1:
                    trail_length = min(0.4, segment_progress)
                    trail_start_x = start_pos[0] + (end_pos[0] - start_pos[0]) * max(0, segment_progress - trail_length)
                    trail_start_y = start_pos[1] + (end_pos[1] - start_pos[1]) * max(0, segment_progress - trail_length)
                    
                    trail_alpha = int(alpha * 0.6)
                    if trail_alpha > 20:
                        pygame.draw.line(self.screen, (*anim['color'], trail_alpha),
                                       (trail_start_x, trail_start_y), (current_x, current_y), 3)
                
                # Add glow effect at orchestrator when particle passes through (for multi-segment animations)
                if num_segments > 1 and current_segment_index == 0 and segment_progress > 0.8:
                    orchestrator_pos = self.agent_positions['orchestrator']
                    glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
                    glow_alpha = int(100 * (segment_progress - 0.8) / 0.2)  # Fade in over last 20% of first segment
                    pygame.draw.circle(glow_surface, (*anim['color'], glow_alpha), (15, 15), 15)
                    self.screen.blit(glow_surface, (orchestrator_pos[0] - 15, orchestrator_pos[1] - 15))
    
    def draw_agents(self):
        """Draw all agents with their current status"""
        for agent_type, pos in self.agent_positions.items():
            if agent_type in ['orchestrator', 'ollama']:
                continue
                
            agent = self.orchestrator.agents[agent_type]
            self.draw_agent(agent_type, agent, pos)
    
    def draw_agent(self, agent_type, agent, pos):
        """Draw a single agent with role-specific graphics"""
        base_radius = 45
        
        # Check if this agent is being dragged
        is_being_dragged = (self.is_dragging and self.dragged_agent == agent_type)
        
        # Get status color
        if agent.status.value == 'working':
            status_color = self.colors['working']
            # Animate working agents
            pulse = 1.0 + 0.4 * math.sin(self.time_offset * 5)
            radius = int(base_radius * pulse)
            
            # Add particles for working state
            if len(self.particles) < 50:  # Limit particles
                self.add_work_particles(pos)
        elif agent.status.value == 'completed':
            status_color = self.colors['completed']
            radius = base_radius
        else:
            status_color = self.colors[agent_type]
            radius = base_radius
        
        # Increase radius slightly when being dragged
        if is_being_dragged:
            radius = int(radius * 1.1)
        
        # Draw drag shadow when being dragged
        if is_being_dragged:
            shadow_offset = 8
            shadow_pos = (pos[0] + shadow_offset, pos[1] + shadow_offset)
            shadow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surface, (0, 0, 0, 60), (radius, radius), radius)
            self.screen.blit(shadow_surface, (shadow_pos[0] - radius, shadow_pos[1] - radius))
        
        # Draw agent glow
        for i in range(3):
            alpha = 30 - i * 10
            glow_radius = radius + i * 6
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*status_color, alpha), 
                             (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, (pos[0] - glow_radius, pos[1] - glow_radius))
        
        # Draw role-specific background and main circle
        if agent_type == 'sales':
            # Sales: Car icon with handshake theme
            pygame.draw.circle(self.screen, status_color, pos, radius)
            pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
            
            # Draw car icon
            car_text = self.font_large.render("CAR", True, self.colors['text'])
            car_rect = car_text.get_rect(center=(pos[0], pos[1] - 8))
            self.screen.blit(car_text, car_rect)
            
            # Draw handshake symbol smaller below
            handshake_text = self.font_small.render("SALE", True, self.colors['text'])
            handshake_rect = handshake_text.get_rect(center=(pos[0], pos[1] + 12))
            self.screen.blit(handshake_text, handshake_rect)
            
        elif agent_type == 'appraisal':
            # Appraisal: Clipboard/magnifying glass theme with data
            pygame.draw.circle(self.screen, status_color, pos, radius)
            pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
            
            # Draw clipboard icon
            clipboard_text = self.font_large.render("DOC", True, self.colors['text'])
            clipboard_rect = clipboard_text.get_rect(center=(pos[0], pos[1] - 8))
            self.screen.blit(clipboard_text, clipboard_rect)
            
            # Draw magnifying glass
            mag_text = self.font_small.render("EVAL", True, self.colors['text'])
            mag_rect = mag_text.get_rect(center=(pos[0], pos[1] + 12))
            self.screen.blit(mag_text, mag_rect)
            
        elif agent_type == 'finance':
            # Finance: Dollar sign with calculator/chart theme
            pygame.draw.circle(self.screen, status_color, pos, radius)
            pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
            
            # Draw dollar sign
            dollar_text = self.font_large.render("$$$", True, self.colors['text'])
            dollar_rect = dollar_text.get_rect(center=(pos[0], pos[1] - 8))
            self.screen.blit(dollar_text, dollar_rect)
            
            # Draw calculator
            calc_text = self.font_small.render("CALC", True, self.colors['text'])
            calc_rect = calc_text.get_rect(center=(pos[0], pos[1] + 12))
            self.screen.blit(calc_text, calc_rect)
            
        elif agent_type == 'manager':
            # Manager: Leadership/organizational theme
            pygame.draw.circle(self.screen, status_color, pos, radius)
            pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
            
            # Draw briefcase icon
            briefcase_text = self.font_large.render("MGR", True, self.colors['text'])
            briefcase_rect = briefcase_text.get_rect(center=(pos[0], pos[1] - 8))
            self.screen.blit(briefcase_text, briefcase_rect)
            
            # Draw organizational chart
            org_text = self.font_small.render("LEAD", True, self.colors['text'])
            org_rect = org_text.get_rect(center=(pos[0], pos[1] + 12))
            self.screen.blit(org_text, org_rect)
        
        # Draw agent name with role title
        role_titles = {
            'sales': 'Sales',
            'appraisal': 'Appraiser', 
            'finance': 'Finance',
            'manager': 'Manager'
        }
        
        # First name only
        first_name = agent.name.split()[0]
        name_text = self.font_medium.render(first_name, True, self.colors['text'])
        name_rect = name_text.get_rect(center=(pos[0], pos[1] + radius + 20))
        self.screen.blit(name_text, name_rect)
        
        # Role title
        role_text = self.font_small.render(role_titles.get(agent_type, 'Agent'), True, self.colors['text_secondary'])
        role_rect = role_text.get_rect(center=(pos[0], pos[1] + radius + 35))
        self.screen.blit(role_text, role_rect)
        
        # Draw task count
        count_text = self.font_small.render(f"Tasks: {agent.tasks_completed}", True, self.colors['text'])
        count_rect = count_text.get_rect(center=(pos[0], pos[1] + radius + 50))
        self.screen.blit(count_text, count_rect)
        
        # Draw status indicator
        status_text = self.font_small.render(agent.status.value.upper(), True, status_color)
        status_rect = status_text.get_rect(center=(pos[0], pos[1] - radius - 20))
        self.screen.blit(status_text, status_rect)
    
    def add_work_particles(self, pos):
        """Add particles around working agents"""
        import random
        for _ in range(2):
            angle = random.random() * 2 * math.pi
            speed = 1 + random.random() * 2
            self.particles.append({
                'x': pos[0] + random.random() * 30 - 15,
                'y': pos[1] + random.random() * 30 - 15,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 60,
                'alpha': 255,
                'color': self.colors['working']
            })
    
    def draw_particles(self):
        """Draw all particles"""
        for particle in self.particles:
            if particle['alpha'] > 0:
                particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                color = (*particle['color'], int(particle['alpha']))
                pygame.draw.circle(particle_surface, color, (3, 3), 3)
                self.screen.blit(particle_surface, (int(particle['x']), int(particle['y'])))
    
    def draw_current_task_overlay(self):
        """Draw current task information overlay in graphics panel"""
        if self.current_task and self.show_details:
            # Semi-transparent overlay
            overlay_rect = pygame.Rect(10, self.height - 120, self.graphics_width - 20, 100)
            overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(overlay_surface, (0, 0, 0, 180), (0, 0, overlay_rect.width, overlay_rect.height))
            pygame.draw.rect(overlay_surface, self.colors['panel_border'], (0, 0, overlay_rect.width, overlay_rect.height), 2)
            self.screen.blit(overlay_surface, overlay_rect)
            
            # Current task info
            y_offset = overlay_rect.y + 10
            
            title_text = self.font_medium.render("Current Task:", True, self.colors['text'])
            self.screen.blit(title_text, (overlay_rect.x + 10, y_offset))
            
            task_text = f"{self.current_task['id']}: {self.current_task['description'][:50]}..."
            task_surface = self.font_small.render(task_text, True, self.colors['text'])
            self.screen.blit(task_surface, (overlay_rect.x + 10, y_offset + 20))
            
            agent_text = f"Agent: {self.current_task['agent']}"
            agent_color = self.colors[self.current_task['type']]
            agent_surface = self.font_small.render(agent_text, True, agent_color)
            self.screen.blit(agent_surface, (overlay_rect.x + 10, y_offset + 40))
    
    def draw_graphics_stats(self):
        """Draw statistics in graphics panel"""
        stats_y = 60
        total_tasks = len(self.orchestrator.completed_tasks) + len(self.orchestrator.task_queue)
        completed_tasks = len(self.orchestrator.completed_tasks)
        
        stats_text = [
            f"Total Tasks: {total_tasks}",
            f"Completed: {completed_tasks}",
            f"Pending: {len(self.orchestrator.task_queue)}",
            f"Ollama Requests: {self.ollama_request_count}",
            f"Ollama Status: {self.ollama_status.upper()}",
            f"FPS: {self.fps_display}"
        ]
        
        for i, stat in enumerate(stats_text):
            # Color code Ollama status
            if "Ollama Status" in stat:
                if self.ollama_status == "processing":
                    color = self.colors['working']
                elif self.ollama_status == "error":
                    color = self.colors['error']
                else:
                    color = self.colors['success']
            else:
                color = self.colors['text_secondary']
                
            stat_render = self.font_small.render(stat, True, color)
            self.screen.blit(stat_render, (20, stats_y + i * 18))
    
    def update_current_task(self, task, agent_name, agent_type):
        """Update the currently displayed task"""
        self.current_task = {
            'id': task.id,
            'description': task.description,
            'agent': agent_name,
            'type': agent_type
        }
        self.add_text(f"[START] {agent_name} started: {task.description[:40]}...", "info")
    
    def task_completed(self, task, result):
        """Called when a task is completed"""
        self.task_history.append({
            'task': task,
            'result': result,
            'timestamp': time.time()
        })
        
        # Add completion particles
        if task.agent_type in self.agent_positions:
            pos = self.agent_positions[task.agent_type]
            for _ in range(15):
                angle = random.random() * 2 * math.pi
                speed = 2 + random.random() * 3
                self.particles.append({
                    'x': pos[0],
                    'y': pos[1],
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'life': 120,
                    'alpha': 255,
                    'color': self.colors['completed']
                })
        
        # Add floating response window
        self.add_floating_response(task.agent_type, result)
        
        # Add completion text
        agent_name = self.orchestrator.agents[task.agent_type].name
        self.add_text(f"[DONE] {agent_name} completed {task.id}", "success")
        self.add_text(f"   Result: {result[:80]}{'...' if len(result) > 80 else ''}", "text_secondary")
    
    def clear_current_task(self):
        """Clear the current task display"""
        self.current_task = None
    
    def log_message(self, message, message_type="info"):
        """Public method to log messages"""
        self.add_text(message, message_type)
    
    def set_demo_callback(self, callback):
        """Set the callback function to start the actual demo"""
        self.demo_callback = callback
    
    def start_demo(self):
        """Start the actual demo - called when start button is clicked"""
        if self.demo_state == "start_screen" and self.demo_callback:
            self.demo_state = "running"
            self.add_text("[LAUNCH] Starting CarMax Store Demo...", "info")
            # Run demo in a separate thread so UI remains responsive
            demo_thread = threading.Thread(target=self.demo_callback, daemon=True)
            demo_thread.start()
    
    def update_fonts(self):
        """Update font sizes based on text panel width and scaling factors"""
        # Calculate scale factor based on text panel width
        # Base width of 600px gives scale of 1.0
        base_width = 600
        panel_scale_factor = max(0.7, min(1.5, self.text_width / base_width))
        
        # Apply main font scaling to graphics panel fonts
        main_scale = panel_scale_factor * self.main_font_scale
        title_size = max(12, int(self.base_font_sizes['title'] * main_scale))
        large_size = max(10, int(self.base_font_sizes['large'] * main_scale))
        medium_size = max(8, int(self.base_font_sizes['medium'] * main_scale))
        small_size = max(6, int(self.base_font_sizes['small'] * main_scale))
        
        # Apply output font scaling to output panel font
        output_scale = panel_scale_factor * self.output_font_scale
        mono_size = max(6, int(self.base_font_sizes['mono'] * output_scale))
        
        # Create main font objects (for graphics panel)
        self.font_title = pygame.font.Font(None, title_size)
        self.font_large = pygame.font.Font(None, large_size)
        self.font_medium = pygame.font.Font(None, medium_size)
        self.font_small = pygame.font.Font(None, small_size)
        
        # Create monospace font with preferred font family (for output panel)
        if self.mono_font_name:
            try:
                self.font_mono = pygame.font.SysFont(self.mono_font_name, mono_size)
            except:
                self.font_mono = pygame.font.Font(None, mono_size)
        else:
            self.font_mono = pygame.font.Font(None, mono_size)
        
        # Update text wrapping width based on new font size
        # Estimate character width and calculate wrap width
        char_width = self.font_mono.size("M")[0]  # Use 'M' as reference character
        available_width = self.text_width - 30  # Account for padding
        self.text_wrap_width = max(20, available_width // char_width)
    
    def add_floating_response(self, agent_type: str, response_text: str):
        """Add a floating response window near an agent"""
        if not self.show_floating_responses or agent_type not in self.agent_positions:
            return
        
        agent_pos = self.agent_positions[agent_type]
        
        # Truncate long responses for the floating window
        display_text = response_text[:100] + "..." if len(response_text) > 100 else response_text
        
        # Create floating response
        floating_response = {
            'agent_type': agent_type,
            'text': display_text,
            'start_time': time.time(),
            'duration': 4.0,  # Show for 4 seconds
            'start_pos': agent_pos,
            'offset_y': -80,  # Start above the agent
            'alpha': 255,
            'scale': 1.0
        }
        
        self.floating_responses.append(floating_response)
        
        # Limit number of floating responses
        if len(self.floating_responses) > 10:
            self.floating_responses = self.floating_responses[-10:]
    
    def update_floating_responses(self):
        """Update floating response animations"""
        current_time = time.time()
        active_responses = []
        
        for response in self.floating_responses:
            elapsed = current_time - response['start_time']
            progress = elapsed / response['duration']
            
            if progress <= 1.0:  # Still active
                # Fade out over time
                response['alpha'] = int(255 * (1.0 - progress) ** 0.5)
                
                # Move upward slowly
                response['offset_y'] = -80 - (progress * 30)
                
                # Scale slightly
                response['scale'] = 1.0 + (progress * 0.1)
                
                active_responses.append(response)
        
        self.floating_responses = active_responses
    
    def draw_floating_responses(self):
        """Draw floating response windows"""
        for response in self.floating_responses:
            agent_pos = response['start_pos']
            x = agent_pos[0]
            y = agent_pos[1] + response['offset_y']
            
            # Get agent color
            agent_color = self.colors.get(response['agent_type'], self.colors['text'])
            
            # Prepare text
            text_lines = response['text'].split('\n')[:3]  # Max 3 lines
            
            # Calculate window size
            max_width = 0
            line_height = self.font_small.get_height()
            total_height = len(text_lines) * line_height + 10
            
            for line in text_lines:
                text_width = self.font_small.size(line)[0]
                max_width = max(max_width, text_width)
            
            window_width = min(250, max_width + 20)
            window_height = total_height
            
            # Center the window
            window_x = x - window_width // 2
            window_y = y - window_height // 2
            
            # Ensure window stays within graphics panel bounds
            window_x = max(10, min(self.graphics_width - window_width - 10, window_x))
            window_y = max(10, min(self.height - window_height - 10, window_y))
            
            # Create surface with alpha for fading
            window_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
            
            # Draw rounded background
            bg_alpha = min(200, response['alpha'])
            pygame.draw.rect(window_surface, (*agent_color, bg_alpha // 3), 
                           (0, 0, window_width, window_height), border_radius=8)
            pygame.draw.rect(window_surface, (*agent_color, bg_alpha), 
                           (0, 0, window_width, window_height), width=2, border_radius=8)
            
            # Draw text
            text_alpha = response['alpha']
            for i, line in enumerate(text_lines):
                text_surface = self.font_small.render(line, True, (*self.colors['text'], text_alpha))
                text_rect = text_surface.get_rect()
                text_rect.x = 10
                text_rect.y = 5 + i * line_height
                window_surface.blit(text_surface, text_rect)
            
            # Blit the window to screen
            self.screen.blit(window_surface, (window_x, window_y))
    
    def handle_ctrl_keypress(self, key):
        """Handle Ctrl+key combinations"""
        if key == pygame.K_EQUALS or key == pygame.K_PLUS or key == pygame.K_KP_PLUS:
            # Ctrl+Plus: Increase font size
            # Check mouse position to determine which panel to scale
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.graphics_width:
                # Mouse over graphics panel - scale main fonts
                self.main_font_scale = min(self.max_font_scale, self.main_font_scale + self.font_scale_step)
                self.update_fonts()
                self.add_text(f"[FONT] Main panel font scale: {self.main_font_scale:.1f}x", "info")
            else:
                # Mouse over output panel - scale output fonts
                self.output_font_scale = min(self.max_font_scale, self.output_font_scale + self.font_scale_step)
                self.update_fonts()
                self.add_text(f"[FONT] Output panel font scale: {self.output_font_scale:.1f}x", "info")
        
        elif key == pygame.K_MINUS or key == pygame.K_KP_MINUS:
            # Ctrl+Minus: Decrease font size
            # Check mouse position to determine which panel to scale
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.graphics_width:
                # Mouse over graphics panel - scale main fonts
                self.main_font_scale = max(self.min_font_scale, self.main_font_scale - self.font_scale_step)
                self.update_fonts()
                self.add_text(f"[FONT] Main panel font scale: {self.main_font_scale:.1f}x", "info")
            else:
                # Mouse over output panel - scale output fonts
                self.output_font_scale = max(self.min_font_scale, self.output_font_scale - self.font_scale_step)
                self.update_fonts()
                self.add_text(f"[FONT] Output panel font scale: {self.output_font_scale:.1f}x", "info")
        
        elif key == pygame.K_0 or key == pygame.K_KP0:
            # Ctrl+0: Reset font scales to normal
            # Check mouse position to determine which panel to reset
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.graphics_width:
                # Mouse over graphics panel - reset main fonts
                self.main_font_scale = 1.0
                self.update_fonts()
                self.add_text("[FONT] Main panel font scale reset to 1.0x", "info")
            else:
                # Mouse over output panel - reset output fonts
                self.output_font_scale = 1.0
                self.update_fonts()
                self.add_text("[FONT] Output panel font scale reset to 1.0x", "info")
    
    def handle_scroll(self, scroll_y):
        """Handle mouse wheel scrolling"""
        # Scroll through text output
        self.text_scroll_offset = max(0, self.text_scroll_offset - scroll_y)
        if self.text_scroll_offset > 0:
            self.auto_scroll = False
        elif self.text_scroll_offset == 0:
            self.auto_scroll = True
