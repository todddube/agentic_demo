import pygame
import math
import time
import threading
import random
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
    WAVE = "wave"
    SPIRAL = "spiral"
    LIGHTNING = "lightning"
    FIREWORKS = "fireworks"
    MATRIX = "matrix"
    RAINBOW = "rainbow"

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
        
        # Resizing state for agent nodes
        self.is_resizing_agent = False
        self.resized_agent = None
        self.resize_start_size = 0
        self.resize_start_mouse = (0, 0)
        self.agent_custom_sizes = {}  # Store custom sizes for agents
        
        # Colors with enhanced neon palette
        self.colors = {
            'background': (5, 5, 15),           # Darker for better contrast
            'panel_bg': (15, 15, 25),           # Darker panel background
            'panel_border': (80, 80, 120),      # Brighter border
            'text': (255, 255, 255),
            'text_secondary': (200, 200, 220),   # Brighter secondary text
            'text_dim': (140, 140, 160),        # Brighter dim text
            'sales': (255, 69, 120),            # Hot pink - Sales Consultant
            'appraisal': (0, 255, 200),         # Cyan - Appraisal Manager
            'finance': (69, 183, 255),          # Electric blue - Finance Manager
            'manager': (150, 255, 100),         # Lime green - Store Manager
            'orchestrator': (255, 215, 0),      # Gold
            'ollama': (147, 112, 219),          # Medium slate blue - Ollama Server
            'connection': (100, 255, 200),      # Bright cyan connections
            'active': (255, 255, 0),            # Yellow for active
            'completed': (0, 255, 100),         # Bright green for completed
            'working': (255, 165, 0),           # Orange for working
            'success': (0, 255, 0),
            'error': (255, 50, 50),             # Brighter red
            'info': (100, 200, 255),            # Brighter info blue
            'request': (255, 140, 0),           # Dark orange for requests
            'response': (50, 255, 50),          # Bright lime green for responses
            'neon_purple': (191, 64, 191),      # Neon purple
            'neon_cyan': (0, 255, 255),         # Neon cyan
            'neon_pink': (255, 20, 147),        # Deep pink
            'neon_green': (57, 255, 20),        # Neon green
            'neon_orange': (255, 165, 0),       # Neon orange
            'electric_blue': (0, 191, 255),     # Electric blue
            'laser_red': (255, 0, 80),          # Laser red
            'matrix_green': (0, 255, 65),       # Matrix green
        }
        
        # Initialize all the other attributes that will be needed
        self.text_lines = []
        self.max_text_lines = 50
        self.text_scroll_offset = 0
        self.auto_scroll = True
        self.text_wrap_width = 45
        
        # Agent positions (circular layout in graphics panel)
        self.agent_positions = {}
        self.positions_file = "agent_positions.json"
        self.using_default_positions = True  # Track if using default layout
        
        # Animation and visual effects
        self.animations = {}
        self.particles = []
        self.time_offset = 0
        self.wave_offset = 0
        self.lightning_strikes = []
        self.fireworks = []
        self.matrix_drops = []
        self.rainbow_hue = 0
        self.spiral_particles = []
        self.star_field = []
        self.energy_rings = []
        self.laser_beams = []
        self.pulse_rings = []
        
        # Enhanced visual effects flags
        self.show_star_field = True
        self.show_energy_rings = True
        self.show_laser_beams = True
        self.show_matrix_rain = True
        self.show_fireworks = True
        self.animation_intensity = 1.0  # 0.0 to 2.0 for performance scaling
        
        # Additional attributes that may be missing
        self.last_fps_update = 0
        self.fps_display = 60
        
        # Demo state
        self.demo_state = "start_screen"  # "start_screen", "running", "completed"
        self.start_button_rect = None
        self.demo_callback = None  # Callback to start the actual demo
        self.fireworks = []
        self.lightning_strikes = []
        self.matrix_drops = []
        
        # Resizing and dragging state for panel
        self.is_resizing = False
        self.resize_start_x = 0
        self.resize_original_width = 0
        
        # Dragging state for agent nodes
        self.is_dragging = False
        self.dragged_agent = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_start_pos = None
        
        # Resizing state for agent nodes
        self.is_resizing_agent = False
        self.resized_agent = None
        self.resize_start_size = 0
        self.resize_start_mouse = (0, 0)
        self.agent_custom_sizes = {}  # Store custom sizes for agents
        
        # Initialize remaining attributes
        self.setup_agent_positions()
        
        # Ollama interaction tracking
        self.ollama_interactions = []
        self.ollama_status = "idle"
        self.ollama_request_count = 0
        self.ollama_last_activity = None
        self.interaction_animations = []
        
        # Animation state
        self.animations = {}
        self.particles = []
        self.time_offset = 0
        
        # Floating response windows
        self.floating_responses = []
        self.show_floating_responses = True
        
        # Task display
        self.current_task = None
        self.task_history = []
        self.task_queue = queue.Queue()
        
        # Demo state
        self.demo_state = "start_screen"
        self.demo_callback = None
        self.start_button_rect = None
        
        # UI State
        self.show_details = True
        
        # Fonts - will be updated based on panel size
        self.base_font_sizes = {
            'title': 32,
            'large': 28,
            'medium': 20,
            'small': 16,
            'mono': 18
        }
        
        # Font scaling factors (1.0 = normal size)
        self.main_font_scale = 1.0
        self.output_font_scale = 1.0
        self.min_font_scale = 0.5
        self.max_font_scale = 2.0
        self.font_scale_step = 0.1
        
        # Try to use a better monospace font if available
        self.mono_font_name = None
        try:
            pygame.font.SysFont('consolas', 16)
            self.mono_font_name = 'consolas'
        except:
            try:
                pygame.font.SysFont('courier', 16)
                self.mono_font_name = 'courier'
            except:
                self.mono_font_name = None
        
        # Now update fonts
        self.update_fonts()
    
    def init_star_field(self):
        """Initialize the animated star field background"""
        for _ in range(100):
            star = {
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.uniform(0.5, 3.0),
                'speed': random.uniform(0.1, 0.8),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_phase': random.uniform(0, 2 * math.pi),
                'color': random.choice(['white', 'cyan', 'blue', 'purple'])
            }
            self.star_field.append(star)
    
    def add_energy_ring(self, pos, color, max_radius=100):
        """Add an energy ring effect"""
        ring = {
            'x': pos[0],
            'y': pos[1],
            'radius': 0,
            'max_radius': max_radius,
            'color': color,
            'life': 60,
            'thickness': 3
        }
        self.energy_rings.append(ring)
    
    def add_laser_beam(self, start_pos, end_pos, color, duration=30):
        """Add a laser beam effect"""
        beam = {
            'start': start_pos,
            'end': end_pos,
            'color': color,
            'life': duration,
            'intensity': 255,
            'thickness': random.randint(2, 5)
        }
        self.laser_beams.append(beam)
    
    def add_firework(self, pos, color):
        """Add a firework explosion"""
        firework = {
            'x': pos[0],
            'y': pos[1],
            'particles': [],
            'life': 120,
            'color': color
        }
        
        # Create explosion particles
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            particle = {
                'x': pos[0],
                'y': pos[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(30, 80),
                'alpha': 255,
                'size': random.uniform(2, 5)
            }
            firework['particles'].append(particle)
        
        self.fireworks.append(firework)
    
    def add_matrix_drop(self):
        """Add a matrix-style digital rain drop"""
        drop = {
            'x': random.randint(0, self.graphics_width),
            'y': 0,
            'speed': random.uniform(2, 6),
            'length': random.randint(5, 15),
            'chars': [random.choice('0123456789ABCDEF') for _ in range(15)],
            'alpha': 255
        }
        self.matrix_drops.append(drop)
    
    def add_lightning_strike(self, start_pos, end_pos):
        """Add a lightning strike effect"""
        # Create jagged lightning path
        segments = []
        steps = 10
        for i in range(steps):
            t = i / steps
            x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            
            # Add random jitter
            if i > 0 and i < steps - 1:
                x += random.uniform(-15, 15)
                y += random.uniform(-15, 15)
            
            segments.append((x, y))
        
        lightning = {
            'segments': segments,
            'life': 20,
            'intensity': 255,
            'branches': []
        }
        
        # Add random branches
        for _ in range(random.randint(1, 3)):
            branch_start = random.choice(segments[1:-1])
            branch_end = (branch_start[0] + random.uniform(-30, 30), 
                         branch_start[1] + random.uniform(-30, 30))
            lightning['branches'].append([branch_start, branch_end])
        
        self.lightning_strikes.append(lightning)
    
    def add_pulse_ring(self, pos, color, max_radius=150):
        """Add a pulsing ring effect"""
        ring = {
            'x': pos[0],
            'y': pos[1],
            'radius': 0,
            'max_radius': max_radius,
            'color': color,
            'life': 90,
            'pulse_speed': 0.15
        }
        self.pulse_rings.append(ring)
    
    def setup_agent_positions(self):
        """Setup agent positions - load from file if available, otherwise use default circular layout"""
        # Try to load saved positions first
        if self.load_agent_positions():
            self.using_default_positions = False
            return
        
        # Fallback to default circular layout
        self.create_default_agent_positions()
        self.using_default_positions = True
    
    def create_default_agent_positions(self):
        """Create default circular positions for agents in the graphics panel"""
        self.using_default_positions = True
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
                    saved_data = json.load(f)
                
                # Handle legacy format (just positions) or new format (positions + sizes)
                if isinstance(saved_data, dict) and 'positions' in saved_data:
                    # New format with positions and sizes
                    saved_positions = saved_data.get('positions', {})
                    saved_sizes = saved_data.get('custom_sizes', {})
                else:
                    # Legacy format (just positions)
                    saved_positions = saved_data
                    saved_sizes = {}
                
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
                    
                    # Load custom sizes
                    self.agent_custom_sizes.update(saved_sizes)
                    
                    self.add_text(f"[FOLDER] Loaded saved agent positions and {len(saved_sizes)} custom sizes", "info")
                    self.using_default_positions = False
                    return True
        except Exception as e:
            self.add_text(f"[WARN] Error loading positions: {e}", "error")
        
        return False
    
    def save_agent_positions(self):
        """Save current agent positions to JSON file"""
        try:
            # Save both positions and custom sizes
            data_to_save = {
                'positions': {agent: list(pos) for agent, pos in self.agent_positions.items()},
                'custom_sizes': self.agent_custom_sizes.copy()
            }
            
            with open(self.positions_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            # Only show save message when not resizing (to avoid spam)
            if not self.is_resizing_agent:
                self.add_text("[SAVE] Agent positions and sizes saved", "info")
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
            
            # Add spectacular request effects
            agent_type = data.get('agent_type', 'orchestrator')
            if agent_type in self.agent_positions:
                agent_pos = self.agent_positions[agent_type]
                ollama_pos = self.agent_positions['ollama']
                
                # Add lightning strike effect
                self.add_lightning_strike(agent_pos, ollama_pos)
                
                # Add energy ring at agent
                self.add_energy_ring(agent_pos, self.colors['request'], 80)
                
                # Add pulse ring at Ollama
                self.add_pulse_ring(ollama_pos, self.colors['neon_purple'], 100)
            
            # Add animation for request
            self.add_interaction_animation("request", agent_type)
            
        elif interaction_type == "response":
            if data['success']:
                self.ollama_status = "idle"
                self.add_text(f"[OK] Ollama Response #{data['request_id']}: {data['response_length']} chars", "response")
                
                # Add spectacular response effects
                agent_type = data.get('agent_type', 'orchestrator')
                if agent_type in self.agent_positions:
                    agent_pos = self.agent_positions[agent_type]
                    ollama_pos = self.agent_positions['ollama']
                    
                    # Add laser beam from Ollama to agent
                    self.add_laser_beam(ollama_pos, agent_pos, self.colors['response'], 60)
                    
                    # Add energy ring at agent
                    self.add_energy_ring(agent_pos, self.colors['response'], 90)
                    
                    # Add spiral particles around agent
                    self.add_spiral_particles(agent_pos, self.colors['neon_green'], 12)
                
                # Add floating response window for Ollama response
                if 'response' in data and data['response']:
                    self.add_floating_response(agent_type, f"[AI] Ollama: {data['response'][:60]}...")
                
                # Add animation for response
                self.add_interaction_animation("response", agent_type)
            
        elif interaction_type == "error":
            self.ollama_status = "error"
            self.add_text(f"[ERROR] Ollama Error #{data['request_id']}: {data['error']}", "error")
            
            # Add error effects
            agent_type = data.get('agent_type', 'orchestrator')
            if agent_type in self.agent_positions:
                agent_pos = self.agent_positions[agent_type]
                ollama_pos = self.agent_positions['ollama']
                
                # Add red lightning strike
                self.add_lightning_strike(ollama_pos, agent_pos)
                
                # Add red energy ring
                self.add_energy_ring(agent_pos, self.colors['error'], 70)
            
            # Add error animation
            self.add_interaction_animation("error", agent_type)
        
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
            # Make the window resizable
            self.screen = pygame.display.set_mode(
                (self.width, self.height), 
                pygame.RESIZABLE
            )
            pygame.display.set_caption("CarMax Store System - Team Interface")
            
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        self.add_text("[CLOSE] Pygame window closed - shutting down application...", "info")
                        return  # Exit the thread cleanly
                    elif event.type == pygame.VIDEORESIZE:
                        self.handle_window_resize(event.w, event.h)
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
            # R key to reset agent positions and sizes to default
            self.create_default_agent_positions()
            self.agent_custom_sizes.clear()  # Clear all custom sizes
            self.save_agent_positions()
            self.add_text("[RESET] Agent positions and sizes reset to default", "info")
        elif key == pygame.K_f:
            # F key to toggle floating response windows
            self.show_floating_responses = not self.show_floating_responses
            status = "ON" if self.show_floating_responses else "OFF"
            self.add_text(f"[FLOAT] Floating response windows: {status}", "info")
        elif key == pygame.K_m:
            # M key to toggle matrix rain
            self.show_matrix_rain = not self.show_matrix_rain
            status = "ON" if self.show_matrix_rain else "OFF"
            self.add_text(f"[MATRIX] Matrix rain effect: {status}", "info")
        elif key == pygame.K_s:
            # S key to toggle star field
            self.show_star_field = not self.show_star_field
            status = "ON" if self.show_star_field else "OFF"
            self.add_text(f"[STARS] Star field effect: {status}", "info")
        elif key == pygame.K_x:
            # X key to create fireworks at random positions
            for _ in range(3):
                x = random.randint(100, self.graphics_width - 100)
                y = random.randint(100, self.height - 100)
                color = random.choice([self.colors['neon_cyan'], self.colors['neon_pink'], 
                                     self.colors['neon_green'], self.colors['neon_orange']])
                self.add_firework((x, y), color)
            self.add_text("[BOOM] Fireworks activated! 🎆", "info")
        elif key == pygame.K_l:
            # L key to create lightning strikes
            for _ in range(2):
                x1, y1 = random.randint(50, self.graphics_width - 50), random.randint(50, self.height // 2)
                x2, y2 = random.randint(50, self.graphics_width - 50), random.randint(self.height // 2, self.height - 50)
                self.add_lightning_strike((x1, y1), (x2, y2))
            self.add_text("[ZAP] Lightning strikes activated! ⚡", "info")
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
                # Check if clicking on a resize handle first
                resize_agent = None
                for agent_type in self.agent_positions:
                    if agent_type in ['ollama']:  # Skip non-resizable agents
                        continue
                    if self.is_mouse_on_resize_handle(pos, agent_type):
                        resize_agent = agent_type
                        break
                
                if resize_agent:
                    # Start resizing operation
                    self.is_resizing_agent = True
                    self.resized_agent = resize_agent
                    self.resize_start_mouse = pos
                    self.resize_start_size = self.get_agent_radius(resize_agent)
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)  # Diagonal resize cursor
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
            elif self.is_resizing_agent:
                # Complete the resize operation
                self.is_resizing_agent = False
                
                # Save the new sizes
                self.save_agent_positions()
                self.add_text(f"[RESIZE] Resized {self.resized_agent} agent", "info")
                
                self.resized_agent = None
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
                        self.add_text(f"[MOVE] Moved {self.dragged_agent} agent to new position", "info")
                
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
        elif self.is_resizing_agent and self.resized_agent:
            # Update agent size while resizing
            dx = mouse_x - self.resize_start_mouse[0]
            dy = mouse_y - self.resize_start_mouse[1]
            # Use the larger of the two distances for diagonal resize
            resize_delta = max(dx, dy)
            
            # Calculate new size with constraints
            new_size = self.resize_start_size + resize_delta
            min_size = 25  # Minimum agent size
            max_size = 150  # Maximum agent size
            new_size = max(min_size, min(max_size, new_size))
            
            # Store the custom size
            self.agent_custom_sizes[self.resized_agent] = int(new_size)
        elif self.is_dragging and self.dragged_agent:
            # Update agent position while dragging
            new_x = mouse_x - self.drag_offset_x
            new_y = mouse_y - self.drag_offset_y
            new_pos = self.constrain_agent_position((new_x, new_y))
            self.agent_positions[self.dragged_agent] = new_pos
            # Update agent position while dragging
            new_x = mouse_x - self.drag_offset_x
            new_y = mouse_y - self.drag_offset_y
            new_pos = self.constrain_agent_position((new_x, new_y))
            self.agent_positions[self.dragged_agent] = new_pos
        else:
            # Show appropriate cursor when hovering
            if abs(mouse_x - self.graphics_width) <= 5:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            else:
                # Check for resize handle hover
                resize_hover = False
                for agent_type in self.agent_positions:
                    if agent_type in ['ollama']:  # Skip non-resizable agents
                        continue
                    if self.is_mouse_on_resize_handle(pos, agent_type):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
                        resize_hover = True
                        break
                
                if not resize_hover:
                    # Check for agent hover
                    if self.get_agent_at_position(pos):
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
                
            # Calculate dynamic radius for this agent (same logic as in draw_agent)
            agent_radius = self.get_agent_radius(agent_type)
            
            agent_x, agent_y = agent_pos
            # Check if mouse is within agent radius
            distance = math.sqrt((mouse_x - agent_x) ** 2 + (mouse_y - agent_y) ** 2)
            if distance <= agent_radius:
                return agent_type
        
        return None
    
    def constrain_agent_position(self, pos):
        """Constrain agent position to stay within graphics panel bounds"""
        x, y = pos
        margin = 80  # Increased margin to account for larger agent circles and emojis
        
        x = max(margin, min(self.graphics_width - margin, x))
        y = max(margin, min(self.height - margin, y))
        
        return (int(x), int(y))
    
    def update_animations(self):
        """Update all animations"""
        self.time_offset = time.time()
        self.wave_offset += 0.1
        self.rainbow_hue = (self.rainbow_hue + 2) % 360
        
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
        
        # Update star field
        if self.show_star_field:
            for star in self.star_field:
                star['y'] += star['speed']
                star['twinkle_phase'] += 0.1
                if star['y'] > self.height:
                    star['y'] = -10
                    star['x'] = random.randint(0, self.width)
        
        # Update energy rings
        self.energy_rings = [ring for ring in self.energy_rings if ring['life'] > 0]
        for ring in self.energy_rings:
            ring['radius'] += ring['max_radius'] / 60
            ring['life'] -= 1
            if ring['radius'] > ring['max_radius']:
                ring['radius'] = ring['max_radius']
        
        # Update laser beams
        self.laser_beams = [beam for beam in self.laser_beams if beam['life'] > 0]
        for beam in self.laser_beams:
            beam['life'] -= 1
            beam['intensity'] = max(0, beam['intensity'] - 8)
        
        # Update fireworks
        self.fireworks = [fw for fw in self.fireworks if fw['life'] > 0]
        for firework in self.fireworks:
            firework['life'] -= 1
            firework['particles'] = [p for p in firework['particles'] if p['life'] > 0]
            for particle in firework['particles']:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.1  # Gravity
                particle['life'] -= 1
                particle['alpha'] = max(0, particle['alpha'] - 4)
        
        # Update matrix drops
        self.matrix_drops = [drop for drop in self.matrix_drops if drop['y'] < self.height + 50]
        for drop in self.matrix_drops:
            drop['y'] += drop['speed']
            drop['alpha'] = max(0, drop['alpha'] - 2)
        
        # Add new matrix drops occasionally
        if self.show_matrix_rain and random.random() < 0.1:
            self.add_matrix_drop()
        
        # Update lightning strikes
        self.lightning_strikes = [strike for strike in self.lightning_strikes if strike['life'] > 0]
        for strike in self.lightning_strikes:
            strike['life'] -= 1
            strike['intensity'] = max(0, strike['intensity'] - 12)
        
        # Update pulse rings
        self.pulse_rings = [ring for ring in self.pulse_rings if ring['life'] > 0]
        for ring in self.pulse_rings:
            ring['radius'] += ring['pulse_speed'] * ring['max_radius']
            ring['life'] -= 1
            if ring['radius'] > ring['max_radius']:
                ring['radius'] = 0
        
        # Update spiral particles
        self.spiral_particles = [p for p in self.spiral_particles if p['life'] > 0]
        for particle in self.spiral_particles:
            particle['angle'] += particle['angular_speed']
            particle['radius'] += particle['radial_speed']
            particle['x'] = particle['center_x'] + particle['radius'] * math.cos(particle['angle'])
            particle['y'] = particle['center_y'] + particle['radius'] * math.sin(particle['angle'])
            particle['life'] -= 1
            particle['alpha'] = max(0, particle['alpha'] - 2)
        
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
        # Clear screen with animated background
        self.screen.fill(self.colors['background'])
        
        # Draw animated background effects
        self.draw_star_field()
        self.draw_background_waves()
        
        # Draw panels
        self.draw_graphics_panel()
        self.draw_text_panel()
        
        # Draw panel separator with resize handle
        self.draw_panel_separator()
        
        # Update display
        pygame.display.flip()
    
    def draw_star_field(self):
        """Draw animated star field background"""
        if not self.show_star_field:
            return
            
        for star in self.star_field:
            # Twinkling effect
            brightness = star['brightness'] + 0.3 * math.sin(star['twinkle_phase'])
            brightness = max(0.2, min(1.0, brightness))
            
            # Color variations
            if star['color'] == 'cyan':
                color = (int(brightness * 0), int(brightness * 255), int(brightness * 255))
            elif star['color'] == 'blue':
                color = (int(brightness * 100), int(brightness * 100), int(brightness * 255))
            elif star['color'] == 'purple':
                color = (int(brightness * 200), int(brightness * 100), int(brightness * 255))
            else:  # white
                color = (int(brightness * 255), int(brightness * 255), int(brightness * 255))
            
            # Draw star with size variation
            if star['size'] > 2:
                pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), int(star['size']))
            else:
                pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), 1)
    
    def draw_background_waves(self):
        """Draw animated wave patterns in the background"""
        wave_colors = [
            (self.colors['neon_cyan'][0], self.colors['neon_cyan'][1], self.colors['neon_cyan'][2], 30),
            (self.colors['neon_purple'][0], self.colors['neon_purple'][1], self.colors['neon_purple'][2], 20),
            (self.colors['electric_blue'][0], self.colors['electric_blue'][1], self.colors['electric_blue'][2], 25)
        ]
        
        for i, (r, g, b, alpha) in enumerate(wave_colors):
            wave_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Create sine wave pattern
            for x in range(0, self.width, 5):
                y1 = int(self.height * 0.3 + 50 * math.sin((x + self.wave_offset * 20 + i * 60) * 0.01))
                y2 = int(self.height * 0.7 + 30 * math.sin((x + self.wave_offset * 15 + i * 80) * 0.008))
                
                # Draw wave lines (pygame.draw.line doesn't accept alpha in color tuple)
                if x > 0:
                    pygame.draw.line(wave_surface, (r, g, b), (x-5, prev_y1), (x, y1), 2)
                    pygame.draw.line(wave_surface, (r, g, b), (x-5, prev_y2), (x, y2), 2)
                
                prev_y1, prev_y2 = y1, y2
            
            self.screen.blit(wave_surface, (0, 0))
    
    def draw_energy_rings(self):
        """Draw energy ring effects"""
        for ring in self.energy_rings:
            alpha = int(255 * (ring['life'] / 60))
            if alpha > 0:
                ring_surface = pygame.Surface((ring['radius'] * 2, ring['radius'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(ring_surface, (*ring['color'], alpha), 
                                 (ring['radius'], ring['radius']), ring['radius'], ring['thickness'])
                self.screen.blit(ring_surface, (ring['x'] - ring['radius'], ring['y'] - ring['radius']))
    
    def draw_laser_beams(self):
        """Draw laser beam effects"""
        for beam in self.laser_beams:
            if beam['intensity'] > 0:
                alpha = beam['intensity']
                beam_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                # Draw main beam
                pygame.draw.line(beam_surface, (*beam['color'], alpha), 
                               beam['start'], beam['end'], beam['thickness'])
                
                # Draw beam glow
                pygame.draw.line(beam_surface, (*beam['color'], alpha // 3), 
                               beam['start'], beam['end'], beam['thickness'] * 3)
                
                self.screen.blit(beam_surface, (0, 0))
    
    def draw_fireworks(self):
        """Draw firework effects"""
        for firework in self.fireworks:
            for particle in firework['particles']:
                if particle['alpha'] > 0:
                    particle_surface = pygame.Surface((int(particle['size']) * 2, int(particle['size']) * 2), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, (*firework['color'], int(particle['alpha'])), 
                                     (int(particle['size']), int(particle['size'])), int(particle['size']))
                    self.screen.blit(particle_surface, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
    
    def draw_matrix_rain(self):
        """Draw matrix-style digital rain"""
        if not self.show_matrix_rain:
            return
            
        for drop in self.matrix_drops:
            if drop['alpha'] > 0:
                for i, char in enumerate(drop['chars']):
                    char_y = drop['y'] - i * 15
                    if char_y > 0 and char_y < self.height:
                        alpha = max(0, drop['alpha'] - i * 20)
                        if alpha > 0:
                            char_surface = self.font_small.render(char, True, (*self.colors['matrix_green'], alpha))
                            self.screen.blit(char_surface, (drop['x'], char_y))
    
    def draw_lightning_strikes(self):
        """Draw lightning strike effects"""
        for strike in self.lightning_strikes:
            if strike['intensity'] > 0:
                lightning_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                # Draw main lightning bolt
                for i in range(len(strike['segments']) - 1):
                    start = strike['segments'][i]
                    end = strike['segments'][i + 1]
                    pygame.draw.line(lightning_surface, (255, 255, 255, strike['intensity']), 
                                   start, end, 3)
                
                # Draw branches
                for branch in strike['branches']:
                    pygame.draw.line(lightning_surface, (255, 255, 255, strike['intensity'] // 2), 
                                   branch[0], branch[1], 2)
                
                self.screen.blit(lightning_surface, (0, 0))
    
    def draw_pulse_rings(self):
        """Draw pulsing ring effects"""
        for ring in self.pulse_rings:
            alpha = int(255 * (ring['life'] / 90))
            if alpha > 0 and ring['radius'] > 0:
                ring_surface = pygame.Surface((ring['radius'] * 2, ring['radius'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(ring_surface, (*ring['color'], alpha), 
                                 (ring['radius'], ring['radius']), ring['radius'], 2)
                self.screen.blit(ring_surface, (ring['x'] - ring['radius'], ring['y'] - ring['radius']))
    
    def draw_spiral_particles(self):
        """Draw spiral particle effects"""
        for particle in self.spiral_particles:
            if particle['alpha'] > 0:
                particle_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, (*particle['color'], int(particle['alpha'])), 
                                 (4, 4), 4)
                self.screen.blit(particle_surface, (int(particle['x'] - 4), int(particle['y'] - 4)))
    
    def add_spiral_particles(self, center_pos, color, count=10):
        """Add spiral particles around a center point"""
        for i in range(count):
            particle = {
                'center_x': center_pos[0],
                'center_y': center_pos[1],
                'angle': random.uniform(0, 2 * math.pi),
                'radius': random.uniform(5, 15),
                'angular_speed': random.uniform(-0.2, 0.2),
                'radial_speed': random.uniform(0.5, 2.0),
                'x': center_pos[0],
                'y': center_pos[1],
                'color': color,
                'alpha': 255,
                'life': 120
            }
            self.spiral_particles.append(particle)
    
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
        
        if self.demo_state == "start_screen" or self.demo_state == "ollama_failed":
            self.draw_start_screen()
        else:
            # Title
            title = self.font_title.render("CarMax Store Network", True, self.colors['text'])
            title_rect = title.get_rect(centerx=self.graphics_width//2, y=20)
            self.screen.blit(title, title_rect)
            
            # Draw matrix rain effect
            self.draw_matrix_rain()
            
            # Draw connections between agents
            self.draw_connections()
            
            # Draw interaction animations
            self.draw_interaction_animations()
            
            # Draw energy rings
            self.draw_energy_rings()
            
            # Draw laser beams
            self.draw_laser_beams()
            
            # Draw lightning strikes
            self.draw_lightning_strikes()
            
            # Draw orchestrator
            self.draw_orchestrator()
            
            # Draw agents
            self.draw_agents()
            
            # Draw Ollama server
            self.draw_ollama()
            
            # Draw particles
            self.draw_particles()
            
            # Draw spiral particles
            self.draw_spiral_particles()
            
            # Draw pulse rings
            self.draw_pulse_rings()
            
            # Draw fireworks
            self.draw_fireworks()
            
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
        
        # Check if this is an Ollama failure state
        if hasattr(self, 'demo_state') and self.demo_state == "ollama_failed":
            self.draw_ollama_error_screen()
            return
        
        # Add some background effects for the start screen
        self.add_random_effects()
        
        # Animated title with rainbow effect
        hue = (self.rainbow_hue + 0) % 360
        title_color = self.hsv_to_rgb(hue, 0.8, 1.0)
        title = self.font_title.render("🚗 CarMax Store Demo 🚗", True, title_color)
        title_rect = title.get_rect(centerx=center_x, y=center_y - 120)
        
        # Add title glow effect
        for i in range(5):
            glow_alpha = 50 - i * 8
            glow_surface = pygame.Surface((title_rect.width + i*4, title_rect.height + i*4), pygame.SRCALPHA)
            glow_title = self.font_title.render("🚗 CarMax Store Demo 🚗", True, (*title_color, glow_alpha))
            glow_rect = glow_title.get_rect(centerx=center_x, y=center_y - 120 - i*2)
            self.screen.blit(glow_title, glow_rect)
        
        self.screen.blit(title, title_rect)
        
        # Animated subtitle with pulsing effect
        pulse = 1.0 + 0.3 * math.sin(self.time_offset * 3)
        subtitle_color = (min(255, max(0, int(self.colors['neon_cyan'][0] * pulse))), 
                         min(255, max(0, int(self.colors['neon_cyan'][1] * pulse))), 
                         min(255, max(0, int(self.colors['neon_cyan'][2] * pulse))))
        subtitle = self.font_large.render("⚡ Multi-Agent AI System ⚡", True, subtitle_color)
        subtitle_rect = subtitle.get_rect(centerx=center_x, y=center_y - 80)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Team description with animated colors
        team_lines = [
            ("🎯 Team Members:", self.colors['neon_orange']),
            ("🚗 Mike Rodriguez - Sales Pro", self.colors['sales']),
            ("📊 Sarah Chen - Vehicle Expert", self.colors['appraisal']), 
            ("💰 David Williams - Finance Wizard", self.colors['finance']),
            ("🏆 Jennifer Thompson - Team Leader", self.colors['manager']),
            ("🤖 Ollama AI Server - llama3.2", self.colors['ollama'])
        ]
        
        for i, (line, color) in enumerate(team_lines):
            font = self.font_medium if i == 0 else self.font_small
            # Add subtle animation to text
            animated_color = (
                int(color[0] + 20 * math.sin(self.time_offset * 2 + i)),
                int(color[1] + 20 * math.sin(self.time_offset * 2 + i + 1)),
                int(color[2] + 20 * math.sin(self.time_offset * 2 + i + 2))
            )
            animated_color = tuple(max(0, min(255, c)) for c in animated_color)
            
            text = font.render(line, True, animated_color)
            text_rect = text.get_rect(centerx=center_x, y=center_y - 20 + i * 20)
            self.screen.blit(text, text_rect)
        
        # Animated start button with spectacular effects
        button_width = 250
        button_height = 60
        button_x = center_x - button_width // 2
        button_y = center_y + 80
        
        self.start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Button rainbow glow effect
        button_pulse = 1.0 + 0.4 * math.sin(self.time_offset * 4)
        for i in range(6):
            hue = (self.rainbow_hue + i * 60) % 360
            glow_color = self.hsv_to_rgb(hue, 0.8, 0.6)
            glow_alpha = int(80 * button_pulse - i * 10)
            if glow_alpha > 0:
                glow_rect = pygame.Rect(button_x - i*3, button_y - i*3, button_width + i*6, button_height + i*6)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*glow_color, glow_alpha), (0, 0, glow_rect.width, glow_rect.height), border_radius=15)
                self.screen.blit(glow_surface, glow_rect)
        
        # Main button with gradient effect
        button_hue = (self.rainbow_hue + 120) % 360
        button_color = self.hsv_to_rgb(button_hue, 0.7, 1.0)
        pygame.draw.rect(self.screen, button_color, self.start_button_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.colors['text'], self.start_button_rect, 4, border_radius=15)
        
        # Button text with glow
        button_text = self.font_large.render("🚀 START DEMO 🚀", True, self.colors['text'])
        button_text_rect = button_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Instructions with animated colors
        instructions = [
            "✨ Click the button above or press SPACE to start ✨",
            "⚡ ESC to quit at any time ⚡"
        ]
        
        for i, instruction in enumerate(instructions):
            color_hue = (self.rainbow_hue + i * 180) % 360
            color = self.hsv_to_rgb(color_hue, 0.5, 0.8)
            text = self.font_small.render(instruction, True, color)
            text_rect = text.get_rect(centerx=center_x, y=center_y + 160 + i * 20)
            self.screen.blit(text, text_rect)
    
    def draw_ollama_error_screen(self):
        """Draw error screen when Ollama connection fails"""
        center_x = self.graphics_width // 2
        center_y = self.height // 2
        
        # Error title with red pulsing effect
        pulse = 1.0 + 0.3 * math.sin(self.time_offset * 3)
        error_color = (int(255 * pulse), 50, 50)
        error_color = tuple(max(0, min(255, c)) for c in error_color)
        
        title = self.font_title.render("❌ OLLAMA CONNECTION FAILED ❌", True, error_color)
        title_rect = title.get_rect(centerx=center_x, y=center_y - 200)
        self.screen.blit(title, title_rect)
        
        # Error messages
        error_messages = [
            "",  # Empty line
            "The demo could not connect to Ollama AI server.",
            "",  # Empty line
            "📋 MANUAL SETUP REQUIRED:",
            "",  # Empty line
            "1. Open a terminal/command prompt",
            "2. Run: ollama serve",
            "3. In another terminal, run: ollama pull llama3.2",
            "4. Restart this demo",
            "",  # Empty line
            "🔗 If Ollama is not installed:",
            "• Visit: https://ollama.ai",
            "• Download and install Ollama for your system",
            "",  # Empty line
            "⚡ Press ESC or close window to exit ⚡"
        ]
        
        # Draw error messages with alternating colors
        y_offset = center_y - 120
        for i, message in enumerate(error_messages):
            if not message:  # Empty line
                y_offset += 15
                continue
                
            # Choose color based on message type
            if message.startswith("📋") or message.startswith("🔗"):
                color = self.colors['neon_cyan']
            elif message.startswith("•") or message.startswith("1.") or message.startswith("2.") or message.startswith("3.") or message.startswith("4."):
                color = self.colors['text_secondary']
            elif "ESC" in message:
                color = self.colors['neon_orange']
            else:
                color = self.colors['text']
            
            # Add subtle pulsing to important messages
            if "ESC" in message or message.startswith("📋") or message.startswith("🔗"):
                pulse_factor = 1.0 + 0.2 * math.sin(self.time_offset * 2 + i)
                color = tuple(int(c * pulse_factor) for c in color)
                color = tuple(max(0, min(255, c)) for c in color)
            
            text = self.font_small.render(message, True, color)
            text_rect = text.get_rect(centerx=center_x, y=y_offset)
            self.screen.blit(text, text_rect)
            y_offset += 18
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV color to RGB"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def add_random_effects(self):
        """Add random spectacular effects to the start screen"""
        # Add random energy rings
        if random.random() < 0.05:
            x = random.randint(50, self.graphics_width - 50)
            y = random.randint(50, self.height - 50)
            color = random.choice([self.colors['neon_cyan'], self.colors['neon_purple'], self.colors['neon_pink']])
            self.add_energy_ring((x, y), color, random.randint(60, 120))
        
        # Add random spiral particles
        if random.random() < 0.03:
            x = random.randint(50, self.graphics_width - 50)
            y = random.randint(50, self.height - 50)
            color = random.choice([self.colors['neon_green'], self.colors['electric_blue'], self.colors['neon_orange']])
            self.add_spiral_particles((x, y), color, random.randint(5, 12))
    
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
        controls_y = self.height - 180  # Moved up to accommodate more lines
        control_text = [
            "Controls: ↑↓ Scroll | Home/End | Space: Auto-scroll | D: Details | ESC: Quit",
            "Font scaling: Ctrl++ / Ctrl+- (hover over panel to select) | Ctrl+0 to reset",
            "Resize panels: Drag the separator line between panels",
            "Drag agents: Click and drag agent nodes to reposition them",
            "Resize agents: Drag the resize handle (◢) at bottom-right of each agent",
            "Reset layout: Press R to restore default agent positions and sizes",
            "Toggle effects: F: Floating responses | M: Matrix rain | S: Star field",
            "Special effects: X: Fireworks! 🎆 | L: Lightning strikes! ⚡",
            f"Effects: Stars: {'ON' if self.show_star_field else 'OFF'} | Matrix: {'ON' if self.show_matrix_rain else 'OFF'} | Floating: {'ON' if self.show_floating_responses else 'OFF'}",
            f"Auto-scroll: {'ON' if self.auto_scroll else 'OFF'} | Lines: {len(self.text_lines)}",
            f"Font scales - Main: {self.main_font_scale:.1f}x | Output: {self.output_font_scale:.1f}x"
        ]
        
        for i, text in enumerate(control_text):
            # Use smaller font for controls (two sizes smaller than medium)
            surface = self.font_small.render(text, True, self.colors['text_dim'])
            self.screen.blit(surface, (self.graphics_width + 15, controls_y + i * 14))
    
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
                
                # Draw completed segments as fading trails (no alpha in direct screen drawing)
                for i in range(current_segment_index):
                    segment = segments[i]
                    trail_alpha = int(alpha * 0.3)
                    if trail_alpha > 20:
                        pygame.draw.line(self.screen, anim['color'], 
                                       segment['start'], segment['end'], 2)
                
                # Draw current segment trail (no alpha in direct screen drawing)
                if segment_progress > 0.1:
                    trail_length = min(0.4, segment_progress)
                    trail_start_x = start_pos[0] + (end_pos[0] - start_pos[0]) * max(0, segment_progress - trail_length)
                    trail_start_y = start_pos[1] + (end_pos[1] - start_pos[1]) * max(0, segment_progress - trail_length)
                    
                    trail_alpha = int(alpha * 0.6)
                    if trail_alpha > 20:
                        pygame.draw.line(self.screen, anim['color'],
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
        
        # Calculate dynamic radius based on agent name length and font size
        base_radius = self.get_agent_radius(agent_type)
        
        # Check if this agent is being dragged or resized
        is_being_dragged = (self.is_dragging and self.dragged_agent == agent_type)
        is_being_resized = (self.is_resizing_agent and self.resized_agent == agent_type)
        
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
        
        # Increase radius slightly when being dragged or resized
        if is_being_dragged or is_being_resized:
            radius = int(radius * 1.1)
        
        # Draw drag shadow when being dragged
        if is_being_dragged:
            shadow_offset = 8
            shadow_pos = (pos[0] + shadow_offset, pos[1] + shadow_offset)
            shadow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surface, (0, 0, 0, 60), (radius, radius), radius)
            self.screen.blit(shadow_surface, (shadow_pos[0] - radius, shadow_pos[1] - radius))
        
        # Draw resize highlight when being resized
        if is_being_resized:
            glow_radius = radius + 10
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 0, 80), (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, (pos[0] - glow_radius, pos[1] - glow_radius))
        
        # Draw agent glow
        for i in range(3):
            alpha = 30 - i * 10
            glow_radius = radius + i * 6
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*status_color, alpha), 
                             (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, (pos[0] - glow_radius, pos[1] - glow_radius))
        
        # Draw role-specific background and main circle with enhanced styling
        if agent_type == 'sales':
            # Sales: Car icon with handshake theme - Enhanced with gradient effect
            # Create gradient background
            for i in range(radius):
                alpha = int(255 * (1 - i / radius))
                gradient_color = (status_color[0], status_color[1], status_color[2], alpha)
                gradient_surface = pygame.Surface((2, 2), pygame.SRCALPHA)
                pygame.draw.circle(gradient_surface, gradient_color, (1, 1), 1)
                self.screen.blit(gradient_surface, (pos[0] - 1, pos[1] - 1 - i))
            
            pygame.draw.circle(self.screen, status_color, pos, radius)
            pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
            
            # Draw enhanced car icon with animations
            car_scale = 1.0 + 0.2 * math.sin(self.time_offset * 4) if agent.status.value == 'working' else 1.0
            car_text = self.font_large.render("🚗", True, self.colors['text'])
            car_rect = car_text.get_rect(center=(pos[0], pos[1] - 8))
            if car_scale != 1.0:
                scaled_car = pygame.transform.scale(car_text, (int(car_rect.width * car_scale), int(car_rect.height * car_scale)))
                car_rect = scaled_car.get_rect(center=(pos[0], pos[1] - 8))
                self.screen.blit(scaled_car, car_rect)
            else:
                self.screen.blit(car_text, car_rect)
            
            # Draw handshake symbol with glow
            handshake_text = self.font_small.render("SALE", True, self.colors['text'])
            handshake_rect = handshake_text.get_rect(center=(pos[0], pos[1] + 12))
            # Add glow effect
            glow_text = self.font_small.render("SALE", True, (*status_color, 100))
            for offset in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                glow_rect = handshake_text.get_rect(center=(pos[0] + offset[0], pos[1] + 12 + offset[1]))
                self.screen.blit(glow_text, glow_rect)
            self.screen.blit(handshake_text, handshake_rect)
            
        elif agent_type == 'appraisal':
            # Appraisal: Enhanced clipboard/magnifying glass theme with data visualization
            pygame.draw.circle(self.screen, status_color, pos, radius)
            pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
            
            # Draw animated clipboard icon
            clipboard_scale = 1.0 + 0.15 * math.sin(self.time_offset * 3) if agent.status.value == 'working' else 1.0
            clipboard_text = self.font_large.render("📋", True, self.colors['text'])
            clipboard_rect = clipboard_text.get_rect(center=(pos[0], pos[1] - 8))
            if clipboard_scale != 1.0:
                scaled_clipboard = pygame.transform.scale(clipboard_text, (int(clipboard_rect.width * clipboard_scale), int(clipboard_rect.height * clipboard_scale)))
                clipboard_rect = scaled_clipboard.get_rect(center=(pos[0], pos[1] - 8))
                self.screen.blit(scaled_clipboard, clipboard_rect)
            else:
                self.screen.blit(clipboard_text, clipboard_rect)
            
            # Draw magnifying glass with sparkle effect
            mag_text = self.font_small.render("EVAL", True, self.colors['text'])
            mag_rect = mag_text.get_rect(center=(pos[0], pos[1] + 12))
            # Add sparkle effect for working status
            if agent.status.value == 'working':
                sparkle_color = (255, 255, 255, 150)
                sparkle_positions = [
                    (pos[0] - 15, pos[1] + 5),
                    (pos[0] + 15, pos[1] + 5),
                    (pos[0], pos[1] + 20)
                ]
                for sparkle_pos in sparkle_positions:
                    sparkle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                    pygame.draw.circle(sparkle_surface, sparkle_color, (2, 2), 2)
                    self.screen.blit(sparkle_surface, sparkle_pos)
            self.screen.blit(mag_text, mag_rect)
            
        elif agent_type == 'finance':
            # Finance: Enhanced dollar sign with calculator/chart theme and money animation
            pygame.draw.circle(self.screen, status_color, pos, radius)
            pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
            
            # Draw animated dollar sign
            dollar_scale = 1.0 + 0.25 * math.sin(self.time_offset * 5) if agent.status.value == 'working' else 1.0
            dollar_text = self.font_large.render("💰", True, self.colors['text'])
            dollar_rect = dollar_text.get_rect(center=(pos[0], pos[1] - 8))
            if dollar_scale != 1.0:
                scaled_dollar = pygame.transform.scale(dollar_text, (int(dollar_rect.width * dollar_scale), int(dollar_rect.height * dollar_scale)))
                dollar_rect = scaled_dollar.get_rect(center=(pos[0], pos[1] - 8))
                self.screen.blit(scaled_dollar, dollar_rect)
            else:
                self.screen.blit(dollar_text, dollar_rect)
            
            # Draw calculator with money flow effect
            calc_text = self.font_small.render("CALC", True, self.colors['text'])
            calc_rect = calc_text.get_rect(center=(pos[0], pos[1] + 12))
            # Add money flow particles when working
            if agent.status.value == 'working':
                for i in range(3):
                    money_x = pos[0] + 20 * math.cos(self.time_offset * 2 + i * 2)
                    money_y = pos[1] + 20 * math.sin(self.time_offset * 2 + i * 2)
                    money_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                    pygame.draw.circle(money_surface, (*self.colors['finance'], 120), (4, 4), 4)
                    self.screen.blit(money_surface, (money_x - 4, money_y - 4))
            self.screen.blit(calc_text, calc_rect)
            
        elif agent_type == 'manager':
            # Manager: Enhanced leadership theme with organizational chart animation
            pygame.draw.circle(self.screen, status_color, pos, radius)
            pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
            
            # Draw animated briefcase icon
            briefcase_scale = 1.0 + 0.1 * math.sin(self.time_offset * 2) if agent.status.value == 'working' else 1.0
            briefcase_text = self.font_large.render("👔", True, self.colors['text'])
            briefcase_rect = briefcase_text.get_rect(center=(pos[0], pos[1] - 8))
            if briefcase_scale != 1.0:
                scaled_briefcase = pygame.transform.scale(briefcase_text, (int(briefcase_rect.width * briefcase_scale), int(briefcase_rect.height * briefcase_scale)))
                briefcase_rect = scaled_briefcase.get_rect(center=(pos[0], pos[1] - 8))
                self.screen.blit(scaled_briefcase, briefcase_rect)
            else:
                self.screen.blit(briefcase_text, briefcase_rect)
            
            # Draw organizational chart with connection lines
            org_text = self.font_small.render("LEAD", True, self.colors['text'])
            org_rect = org_text.get_rect(center=(pos[0], pos[1] + 12))
            # Add leadership connection lines when working
            if agent.status.value == 'working':
                for i, other_agent in enumerate(['sales', 'appraisal', 'finance']):
                    if other_agent in self.agent_positions:
                        other_pos = self.agent_positions[other_agent]
                        alpha = int(100 + 50 * math.sin(self.time_offset * 3 + i))
                        line_surface = pygame.Surface((self.graphics_width, self.height), pygame.SRCALPHA)
                        pygame.draw.line(line_surface, (*self.colors['manager'], alpha), pos, other_pos, 2)
                        self.screen.blit(line_surface, (0, 0))
            self.screen.blit(org_text, org_rect)
        
        # Draw agent name with role title
        role_titles = {
            'sales': 'Sales Pro',
            'appraisal': 'Vehicle Expert', 
            'finance': 'Finance Wizard',
            'manager': 'Team Leader'
        }
        
        # Split agent name to get just the name part (after emoji)
        name_parts = agent.name.split(' ', 2)  # Split into emoji, first name, rest
        if len(name_parts) >= 3:
            emoji = name_parts[0]
            first_name = name_parts[1]
            title_part = name_parts[2] if len(name_parts) > 2 else ""
        else:
            emoji = "👤"  # Default emoji
            first_name = agent.name.split()[0] if agent.name else "Agent"
            title_part = ""
        
        # Draw emoji above the agent circle
        emoji_text = self.font_large.render(emoji, True, self.colors['text'])
        emoji_rect = emoji_text.get_rect(center=(pos[0], pos[1] - radius - 30))
        self.screen.blit(emoji_text, emoji_rect)
        
        # Draw first name below the circle
        name_text = self.font_medium.render(first_name, True, self.colors['text'])
        name_rect = name_text.get_rect(center=(pos[0], pos[1] + radius + 20))
        self.screen.blit(name_text, name_rect)
        
        # Role title (use the new fun titles)
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
        
        # Show size when being resized
        if is_being_resized:
            size_text = self.font_small.render(f"Size: {base_radius}", True, (255, 255, 0))
            size_rect = size_text.get_rect(center=(pos[0], pos[1] - radius - 35))
            self.screen.blit(size_text, size_rect)
        
        # Draw resize handle (small square at bottom-right of circle)
        handle_pos = self.get_resize_handle_pos(pos, base_radius)
        handle_size = 12
        handle_rect = pygame.Rect(handle_pos[0] - handle_size//2, handle_pos[1] - handle_size//2, 
                                handle_size, handle_size)
        
        # Handle color based on state
        if is_being_resized:
            handle_color = (255, 255, 0)  # Bright yellow when resizing
        elif self.is_mouse_on_resize_handle(pygame.mouse.get_pos(), agent_type):
            handle_color = (255, 200, 0)  # Orange on hover
        else:
            handle_color = (150, 150, 150)  # Gray normally
        
        # Draw handle background and border
        pygame.draw.rect(self.screen, handle_color, handle_rect)
        pygame.draw.rect(self.screen, self.colors['text'], handle_rect, 2)
        
        # Draw resize symbol in handle (with fallback)
        try:
            symbol_text = self.font_small.render("◢", True, self.colors['text'])
        except:
            symbol_text = self.font_small.render(">>", True, self.colors['text'])
        symbol_rect = symbol_text.get_rect(center=handle_pos)
        self.screen.blit(symbol_text, symbol_rect)
    
    def add_work_particles(self, pos):
        """Add particles around working agents"""
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
        
        # Add spectacular completion effects
        if task.agent_type in self.agent_positions:
            pos = self.agent_positions[task.agent_type]
            agent_color = self.colors[task.agent_type]
            
            # Add completion particles
            for _ in range(25):
                angle = random.random() * 2 * math.pi
                speed = 2 + random.random() * 4
                self.particles.append({
                    'x': pos[0],
                    'y': pos[1],
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'life': 120,
                    'alpha': 255,
                    'color': self.colors['completed']
                })
            
            # Add energy ring effect
            self.add_energy_ring(pos, agent_color, 120)
            
            # Add pulse ring effect
            self.add_pulse_ring(pos, self.colors['completed'], 180)
            
            # Add spiral particles
            self.add_spiral_particles(pos, agent_color, 15)
            
            # Add firework effect for major tasks
            if len(result) > 100:  # Major task completion
                self.add_firework(pos, agent_color)
            
            # Add laser beam from orchestrator to agent
            orchestrator_pos = self.agent_positions['orchestrator']
            self.add_laser_beam(orchestrator_pos, pos, self.colors['completed'], 45)
        
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
        # Calculate scale factor based on both text panel width and overall window size
        # Base width of 600px gives scale of 1.0
        base_width = 600
        base_height = 800
        
        # Factor in both width and height for more responsive scaling
        width_scale = self.text_width / base_width
        height_scale = self.height / base_height
        panel_scale_factor = max(0.6, min(1.8, (width_scale + height_scale) / 2))
        
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
    
    def handle_window_resize(self, new_width: int, new_height: int) -> None:
        """Handle window resize events and update layout accordingly.
        
        Args:
            new_width: New window width
            new_height: New window height
        """
        # Update window dimensions
        old_width, old_height = self.width, self.height
        self.width = new_width
        self.height = new_height
        
        # Recreate the screen surface with new dimensions
        self.screen = pygame.display.set_mode(
            (self.width, self.height), 
            pygame.RESIZABLE
        )
        
        # Calculate new panel layout while maintaining proportions
        graphics_ratio = self.graphics_width / old_width if old_width > 0 else 0.6
        self.graphics_width = int(self.width * graphics_ratio)
        
        # Apply constraints
        self.graphics_width = max(
            self.min_graphics_width, 
            min(self.graphics_width, self.max_graphics_width)
        )
        self.text_width = self.width - self.graphics_width
        
        # Update min/max graphics width based on new window size
        self.min_graphics_width = int(self.width * 0.4)
        self.max_graphics_width = int(self.width * 0.8)
        
        # Recreate star field for new dimensions
        self.star_field.clear()
        self.init_star_field()
        
        # Update agent positions proportionally if they were using default layout
        if hasattr(self, 'using_default_positions') and self.using_default_positions:
            self.create_default_agent_positions()
        else:
            # Scale existing custom positions proportionally
            width_scale = new_width / old_width if old_width > 0 else 1.0
            height_scale = new_height / old_height if old_height > 0 else 1.0
            
            for agent_type, (x, y) in self.agent_positions.items():
                # Only scale positions within graphics panel
                if x <= old_width * graphics_ratio:  # Was in graphics panel
                    new_x = min(int(x * width_scale), self.graphics_width - 50)
                    new_y = max(50, min(int(y * height_scale), self.height - 50))
                    self.agent_positions[agent_type] = (new_x, new_y)
        
        # Update font sizes for new layout
        self.update_fonts()
        
        # Log the resize event
        self.add_text(
            f"[RESIZE] Window resized to {new_width}x{new_height}", 
            "info"
        )
    
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
    
    def get_agent_radius(self, agent_type):
        """Get the current radius for an agent, including custom size"""
        # Check if agent has custom size
        if agent_type in self.agent_custom_sizes:
            return self.agent_custom_sizes[agent_type]
            
        # Calculate default radius based on name length
        if agent_type in self.orchestrator.agents:
            agent = self.orchestrator.agents[agent_type]
            name_text_surface = self.font_medium.render(agent.name, True, self.colors['text'])
            name_width = name_text_surface.get_width()
            return max(45, (name_width // 2) + 20)
        
        return 45  # Fallback
    
    def get_resize_handle_pos(self, agent_pos, agent_radius):
        """Get the position of the resize handle for an agent"""
        # Place resize handle at bottom-right of the agent circle
        handle_x = agent_pos[0] + agent_radius - 5
        handle_y = agent_pos[1] + agent_radius - 5
        return (handle_x, handle_y)
    
    def is_mouse_on_resize_handle(self, mouse_pos, agent_type):
        """Check if mouse is on the resize handle of an agent"""
        if agent_type not in self.agent_positions:
            return False
            
        agent_pos = self.agent_positions[agent_type]
        agent_radius = self.get_agent_radius(agent_type)
        handle_pos = self.get_resize_handle_pos(agent_pos, agent_radius)
        
        # Check if mouse is within the resize handle area (small square)
        handle_size = 12
        mouse_x, mouse_y = mouse_pos
        handle_x, handle_y = handle_pos
        
        return (handle_x - handle_size//2 <= mouse_x <= handle_x + handle_size//2 and
                handle_y - handle_size//2 <= mouse_y <= handle_y + handle_size//2)
