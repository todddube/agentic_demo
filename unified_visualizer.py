import pygame
import math
import time
import threading
from typing import Dict, List, Tuple, Optional
from enum import Enum
import queue
import textwrap

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
            self.width = int(info.current_w * 0.75)
            self.height = int(info.current_h * 0.75)
        else:
            self.width = width
            self.height = height
            
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        
        # Layout configuration
        self.graphics_width = int(self.width * 0.6)  # 60% for graphics
        self.text_width = self.width - self.graphics_width  # 40% for text
        self.panel_padding = 10
        
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
            'connection': (100, 100, 150),
            'active': (255, 255, 0),           # Yellow for active
            'completed': (0, 255, 0),          # Green for completed
            'working': (255, 165, 0),          # Orange for working
            'success': (0, 200, 0),
            'error': (200, 0, 0),
            'info': (100, 150, 255),
        }
        
        # Agent positions (circular layout in graphics panel)
        self.agent_positions = {}
        self.setup_agent_positions()
        
        # Animation state
        self.animations = {}
        self.particles = []
        self.time_offset = 0
        
        # Task display
        self.current_task = None
        self.task_history = []
        self.task_queue = queue.Queue()
        
        # Text output system
        self.text_lines = []
        self.max_text_lines = 50
        self.text_scroll_offset = 0
        self.auto_scroll = True
        
        # Fonts
        self.font_title = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.font_mono = pygame.font.Font(None, 18)  # Increased from 14 to 18 for better readability
        
        # Try to use a better monospace font if available
        try:
            self.font_mono = pygame.font.SysFont('consolas', 16)  # Windows Consolas font
        except:
            try:
                self.font_mono = pygame.font.SysFont('courier', 16)  # Fallback to Courier
            except:
                self.font_mono = pygame.font.Font(None, 18)  # Final fallback
        
        # UI State
        self.show_details = True
        self.last_fps_update = 0
        self.fps_display = 60
        
    def setup_agent_positions(self):
        """Setup circular positions for agents in the graphics panel"""
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
    
    def start(self):
        """Start the visualization in a separate thread"""
        if not self.running:
            self.running = True
            self.add_text("🎮 Starting unified pygame visualization...", "info")
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
        
        # Wrap long lines - adjusted for larger font
        wrapped_lines = textwrap.wrap(text, width=45)  # Reduced from 50 to 45 for larger font
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
                    elif event.type == pygame.KEYDOWN:
                        self.handle_keypress(event.key)
                    elif event.type == pygame.MOUSEWHEEL:
                        self.handle_scroll(event.y)
                
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
    
    def handle_keypress(self, key):
        """Handle keyboard input"""
        if key == pygame.K_SPACE:
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
    
    def handle_scroll(self, direction):
        """Handle mouse wheel scrolling in text panel"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x > self.graphics_width:  # In text panel
            self.text_scroll_offset = max(0, min(
                self.text_scroll_offset - direction * 3,
                len(self.text_lines) - 1
            ))
            self.auto_scroll = False
    
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
        
        # Update FPS display
        if time.time() - self.last_fps_update > 1.0:
            self.fps_display = int(self.clock.get_fps())
            self.last_fps_update = time.time()
    
    def draw_frame(self):
        """Draw a complete frame"""
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Draw panels
        self.draw_graphics_panel()
        self.draw_text_panel()
        
        # Draw panel separator
        pygame.draw.line(self.screen, self.colors['panel_border'], 
                        (self.graphics_width, 0), (self.graphics_width, self.height), 2)
        
        # Update display
        pygame.display.flip()
    
    def draw_graphics_panel(self):
        """Draw the graphics panel with agent visualization"""
        # Panel background
        graphics_rect = pygame.Rect(0, 0, self.graphics_width, self.height)
        pygame.draw.rect(self.screen, self.colors['panel_bg'], graphics_rect)
        pygame.draw.rect(self.screen, self.colors['panel_border'], graphics_rect, 2)
        
        # Title
        title = self.font_title.render("CarMax Store Network", True, self.colors['text'])
        title_rect = title.get_rect(centerx=self.graphics_width//2, y=20)
        self.screen.blit(title, title_rect)
        
        # Draw connections between agents
        self.draw_connections()
        
        # Draw orchestrator
        self.draw_orchestrator()
        
        # Draw agents
        self.draw_agents()
        
        # Draw particles
        self.draw_particles()
        
        # Draw current task info in graphics panel
        self.draw_current_task_overlay()
        
        # Draw graphics panel stats
        self.draw_graphics_stats()
    
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
        controls_y = self.height - 45  # Moved up slightly for better visibility
        control_text = [
            "Controls: ↑↓ Scroll | Home/End | Space: Auto-scroll | D: Details",
            f"Auto-scroll: {'ON' if self.auto_scroll else 'OFF'} | Lines: {len(self.text_lines)}"
        ]
        
        for i, text in enumerate(control_text):
            # Use medium font for better readability of controls
            surface = self.font_medium.render(text, True, self.colors['text_dim'])
            self.screen.blit(surface, (self.graphics_width + 15, controls_y + i * 18))
    
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
    
    def draw_agents(self):
        """Draw all agents with their current status"""
        for agent_type, pos in self.agent_positions.items():
            if agent_type == 'orchestrator':
                continue
                
            agent = self.orchestrator.agents[agent_type]
            self.draw_agent(agent_type, agent, pos)
    
    def draw_agent(self, agent_type, agent, pos):
        """Draw a single agent"""
        base_radius = 45
        
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
        
        # Draw agent glow
        for i in range(3):
            alpha = 30 - i * 10
            glow_radius = radius + i * 6
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*status_color, alpha), 
                             (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, (pos[0] - glow_radius, pos[1] - glow_radius))
        
        # Draw main circle
        pygame.draw.circle(self.screen, status_color, pos, radius)
        pygame.draw.circle(self.screen, self.colors['text'], pos, radius, 3)
        
        # Draw agent name
        name_text = self.font_medium.render(agent.name.split()[0], True, self.colors['text'])
        name_rect = name_text.get_rect(center=(pos[0], pos[1] + radius + 20))
        self.screen.blit(name_text, name_rect)
        
        # Draw task count
        count_text = self.font_small.render(f"Tasks: {agent.tasks_completed}", True, self.colors['text'])
        count_rect = count_text.get_rect(center=(pos[0], pos[1] + radius + 35))
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
            f"FPS: {self.fps_display}"
        ]
        
        for i, stat in enumerate(stats_text):
            stat_render = self.font_small.render(stat, True, self.colors['text_secondary'])
            self.screen.blit(stat_render, (20, stats_y + i * 18))
    
    def update_current_task(self, task, agent_name, agent_type):
        """Update the currently displayed task"""
        self.current_task = {
            'id': task.id,
            'description': task.description,
            'agent': agent_name,
            'type': agent_type
        }
        self.add_text(f"🔄 {agent_name} started: {task.description[:40]}...", "info")
    
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
            import random
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
        
        # Add completion text
        agent_name = self.orchestrator.agents[task.agent_type].name
        self.add_text(f"✅ {agent_name} completed {task.id}", "success")
        self.add_text(f"   Result: {result[:80]}{'...' if len(result) > 80 else ''}", "text_secondary")
    
    def clear_current_task(self):
        """Clear the current task display"""
        self.current_task = None
    
    def log_message(self, message, message_type="info"):
        """Public method to log messages"""
        self.add_text(message, message_type)
