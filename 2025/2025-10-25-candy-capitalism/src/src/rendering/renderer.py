"""
Rendering system for the game world.

Handles world rendering, sprite management, and visual effects
with support for layered rendering and camera systems.
"""

import pygame
import math
import time
from typing import List, Dict, Any, Optional
from ..entities.base_entity import BaseEntity
from ..entities.kid import Kid
from ..entities.house import House
from .camera import Camera
from .particle_system import ParticleSystem
from ..core.constants import COLORS, SCREEN_SIZE
from ..utils.vector2 import Vector2
from ..ui.inventory_display import InventoryManager
from .safe_draw import circle as safe_circle, lines as safe_lines


class Renderer:
    """
    Main rendering system for the game world.
    
    Handles rendering of all game entities with support for
    layered rendering and camera systems.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the renderer.
        
        Args:
            screen: Pygame screen surface to render to
        """
        self.screen = screen
        self.camera = Camera(Vector2(1000, 1000), 0.5)  # Center of 2000x2000 world, zoomed out
        
        # Rendering layers
        self.layers = {
            'background': [],
            'world': [],
            'effects': [],
            'ui': []
        }
        
        # Sprite management
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        self.font_cache: Dict[tuple, pygame.font.Font] = {}
        
        # Debug overlay
        self.debug_enabled = False
        self.help_enabled = False
        
        # Particle system
        self.particle_system = ParticleSystem()
        
        # Inventory display
        self.inventory_manager = InventoryManager()
        self.inventory_display_enabled = False
        
    def render_world(self, world, dt: float = 0.0):
        """
        Render the entire game world.
        
        Args:
            world: GameWorld instance to render
            dt: Delta time for animations
        """
        # Clear screen
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Store world reference for possession checking
        self.current_world = world
        
        # Render background layer
        self._render_background()
        
        # Render world entities
        self._render_entities(world)
        
        # Render effects layer
        self._render_effects()
        
        # Update and render particles
        self.particle_system.update(dt)
        self.particle_system.render(self.screen, self.camera)
        
        # Render UI layer
        self._render_ui()
        
        # Render debug overlay
        if self.debug_enabled:
            self._render_debug_overlay(world)
        
        # Render help overlay
        if self.help_enabled:
            self._render_help_overlay()
        
        # Render inventory display
        if self.inventory_display_enabled:
            font = self._get_font(14)
            self.inventory_manager.render(self.screen, font)
    
    def _render_background(self):
        """Render background elements."""
        # For now, just a simple grid pattern
        grid_size = 50
        for x in range(0, SCREEN_SIZE[0], grid_size):
            safe_lines(self.screen, COLORS['DARK_GRAY'], False, [(x, 0), (x, SCREEN_SIZE[1])], 1)
        for y in range(0, SCREEN_SIZE[1], grid_size):
            safe_lines(self.screen, COLORS['DARK_GRAY'], False, [(0, y), (SCREEN_SIZE[0], y)], 1)
    
    def _render_entities(self, world):
        """Render all world entities."""
        # Render houses first (background)
        for house in world.houses:
            if house.active and house.visible:
                self._render_house(house)
        
        # Render kids
        for kid in world.kids:
            if kid.active and kid.visible:
                self._render_kid(kid)
        
        # Render trading blocs (visual indicators)
        for bloc in world.trading_blocs:
            self._render_trading_bloc(bloc, world.kids)
    
    def _render_house(self, house: House):
        """Render a house entity."""
        # Convert world position to screen position
        screen_pos = self.camera.world_to_screen(house.position)
        
        # Draw house glow effect (before house)
        self._render_house_glow(house, screen_pos)
        
        # Draw house as a rectangle
        house_rect = pygame.Rect(
            screen_pos.x - 20, screen_pos.y - 15,
            40, 30
        )
        
        # Choose color based on house state and quality
        if house.is_blessed():
            color = (100, 255, 100)  # Green for blessed
        elif house.is_cursed():
            color = (255, 100, 100)  # Red for cursed
        else:
            # Color based on quality level
            if house.quality == 1:  # Low quality
                color = (150, 150, 150)  # Gray
            elif house.quality == 2:  # Mid quality
                color = (139, 69, 19)  # Brown
            else:  # High quality
                color = (255, 215, 0)  # Gold
        
        pygame.draw.rect(self.screen, color, house_rect)
        pygame.draw.rect(self.screen, COLORS['BLACK'], house_rect, 2)
        
        # Draw house quality indicator (letter)
        font = self._get_font(16)
        quality_letter = chr(ord('A') + house.quality - 1)  # A, B, C for quality 1, 2, 3
        text_surface = font.render(quality_letter, True, COLORS['WHITE'])
        text_rect = text_surface.get_rect(center=house_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        # Draw cooldown indicator
        if house.dispense_cooldown > 0:
            self._render_house_cooldown(house, screen_pos)
    
    def _render_kid(self, kid: Kid):
        """Render a kid entity."""
        # Convert world position to screen position
        screen_pos = self.camera.world_to_screen(kid.position)
        
        # Draw kid as a colored circle
        color = self._get_kid_color(kid)
        radius = 8
        
        # Draw possession glow effect
        self._render_possession_glow(kid, screen_pos)
        
        safe_circle(self.screen, color, screen_pos.to_int_tuple(), radius)
        safe_circle(self.screen, (0, 0, 0), screen_pos.to_int_tuple(), radius, 2)
        
        # Draw kid ID
        font = self._get_font(12)
        text_surface = font.render(kid.id, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_pos.x, screen_pos.y - 20))
        self.screen.blit(text_surface, text_rect)
        
        # Draw inventory count
        self._render_inventory_count(kid, screen_pos)
        
        # Draw personality indicator
        self._render_personality_indicator(kid, screen_pos)
    
    def _get_kid_color(self, kid: Kid) -> tuple:
        """Get color for a kid based on their state."""
        if kid.state.name == "FLEEING":
            return COLORS['RED']
        elif kid.state.name == "IN_TRADE":
            return COLORS['YELLOW']
        elif kid.mood.name == "PANIC":
            return COLORS['ORANGE']
        elif kid.mood.name == "HAPPY":
            return COLORS['GREEN']
        else:
            return COLORS['WHITE']
    
    def _render_mood_indicator(self, kid: Kid, screen_pos):
        """Render mood indicator above kid."""
        mood_symbols = {
            'HAPPY': '😊',
            'NEUTRAL': '😐',
            'ANXIOUS': '😰',
            'GREEDY': '😈',
            'PANIC': '😱'
        }
        
        symbol = mood_symbols.get(kid.mood.name, '?')
        font = self._get_font(16)
        text_surface = font.render(symbol, True, COLORS['WHITE'])
        
        # Position above kid
        text_rect = text_surface.get_rect(center=(screen_pos.x, screen_pos.y - 20))
        self.screen.blit(text_surface, text_rect)
    
    def _render_inventory_count(self, kid: Kid, screen_pos):
        """Render inventory count as text."""
        if not kid.inventory:
            return
        
        # Count total candy
        total_candy = sum(kid.inventory.values())
        if total_candy == 0:
            return
        
        # Draw candy count
        font = self._get_font(10)
        text = f"{total_candy}"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_pos.x, screen_pos.y + 15))
        self.screen.blit(text_surface, text_rect)
    
    def _render_inventory_indicator(self, kid: Kid, screen_pos):
        """Render small inventory indicator."""
        if not kid.inventory:
            return
        
        # Count total candy
        total_candy = sum(kid.inventory.values())
        if total_candy == 0:
            return
        
        # Draw small indicator
        indicator_rect = pygame.Rect(
            screen_pos.x - 12, screen_pos.y + 12,
            24, 4
        )
        
        # Color based on total candy value
        if total_candy > 10:
            color = COLORS['GREEN']
        elif total_candy > 5:
            color = COLORS['YELLOW']
        else:
            color = COLORS['RED']
        
        pygame.draw.rect(self.screen, color, indicator_rect)
    
    def _render_house_glow(self, house: House, screen_pos: Vector2):
        """Render glow effect for cursed/blessed houses."""
        pulse = (math.sin(time.time() * 3) + 1) / 2  # 0-1 pulsing
        
        # Determine glow color based on house state
        if house.is_cursed() and house.is_blessed():
            # Both active - use orange/yellow for conflicted state
            glow_color = (255, 165, 0)  # Orange
            glow_radius = 45 + int(pulse * 10)
        elif house.is_cursed():
            glow_color = (255, 50, 50)  # Red
            glow_radius = 35 + int(pulse * 10)
        elif house.is_blessed():
            glow_color = (100, 255, 100)  # Green
            glow_radius = 40 + int(pulse * 10)
        else:
            return
        
        # Multi-layer glow
        for i in range(3):
            alpha = max(0, min(255, 80 - (i * 25)))  # Clamp alpha to 0-255
            radius = glow_radius + (i * 5)
            
            # CRITICAL: Ensure radius fits within surface
            # Radius must be less than surface_size/2 to fit inside
            # Use a safe buffer to prevent edge cases
            max_radius = 45  # Safe maximum radius
            radius = min(radius, max_radius)
            
            # Surface size must be at least 2*radius + 4 for safety margins
            surface_size = max(2 * radius + 4, 4)
            
            # Ensure color components are valid integers in 0-255 range
            r = max(0, min(255, int(glow_color[0])))
            g = max(0, min(255, int(glow_color[1])))
            b = max(0, min(255, int(glow_color[2])))
            a = max(0, min(255, int(alpha)))
            
            glow_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            center_pos = (surface_size // 2, surface_size // 2)
            # Draw RGB-only, then apply alpha to the surface
            pygame.draw.circle(glow_surface, (r, g, b), center_pos, radius)
            glow_surface.set_alpha(a)
            glow_rect = glow_surface.get_rect(center=screen_pos.to_int_tuple())
            self.screen.blit(glow_surface, glow_rect)
    
    def _render_trading_bloc(self, bloc, kids: List[Kid]):
        """Render trading bloc visual indicators."""
        if not bloc.members:
            return
        
        # Get member positions
        member_positions = []
        for kid_id in bloc.members:
            kid = next((k for k in kids if k.id == kid_id), None)
            if kid and kid.active:
                member_positions.append(kid.position)
        
        if len(member_positions) < 2:
            return
        
        # Draw connections between members
        for i, pos1 in enumerate(member_positions):
            for pos2 in member_positions[i+1:]:
                screen_pos1 = self.camera.world_to_screen(pos1)
                screen_pos2 = self.camera.world_to_screen(pos2)
                
                safe_lines(self.screen, bloc.color, False, [screen_pos1.to_int_tuple(), screen_pos2.to_int_tuple()], 2)
    
    def _render_effects(self):
        """Render visual effects."""
        # Placeholder for particle effects, etc.
        pass
    
    def _render_ui(self):
        """Render UI elements."""
        # Placeholder for UI rendering
        pass
    
    def _get_font(self, size: int) -> pygame.font.Font:
        """Get cached font."""
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(None, size)
        return self.font_cache[size]
    
    def set_camera(self, camera: Camera):
        """Set the camera for rendering."""
        self.camera = camera
    
    def get_camera(self) -> Camera:
        """Get the current camera."""
        return self.camera
    
    def _render_debug_overlay(self, world):
        """Render debug information overlay."""
        font = self._get_font(14)
        y_offset = 10
        
        # FPS counter
        fps_text = f"FPS: {pygame.time.Clock().get_fps():.1f}"
        fps_surface = font.render(fps_text, True, (255, 255, 0))
        self.screen.blit(fps_surface, (10, y_offset))
        y_offset += 20
        
        # Kid count
        kid_text = f"Kids: {len(world.kids)}"
        kid_surface = font.render(kid_text, True, (255, 255, 0))
        self.screen.blit(kid_surface, (10, y_offset))
        y_offset += 20
        
        # House count
        house_text = f"Houses: {len(world.houses)}"
        house_surface = font.render(house_text, True, (255, 255, 0))
        self.screen.blit(house_surface, (10, y_offset))
        y_offset += 20
        
        # Pathfinding info
        if world.pathfinding_manager:
            path_text = f"Pathfinding: Active"
            path_surface = font.render(path_text, True, (255, 255, 0))
            self.screen.blit(path_surface, (10, y_offset))
            y_offset += 20
        
        # Particle count
        particle_text = f"Particles: {self.particle_system.get_particle_count()}"
        particle_surface = font.render(particle_text, True, (255, 255, 0))
        self.screen.blit(particle_surface, (10, y_offset))
        y_offset += 20
        
        # House cooldowns
        houses_on_cooldown = [h for h in world.houses if h.dispense_cooldown > 0]
        cooldown_text = f"Houses on cooldown: {len(houses_on_cooldown)}"
        cooldown_surface = font.render(cooldown_text, True, (255, 255, 0))
        self.screen.blit(cooldown_surface, (10, y_offset))
        y_offset += 20
        
        # Personality distribution
        personality_counts = {}
        for kid in world.kids:
            personality = kid.personality.name
            personality_counts[personality] = personality_counts.get(personality, 0) + 1
        
        personality_text = "Personalities: " + ", ".join([f"{k}: {v}" for k, v in personality_counts.items()])
        personality_surface = font.render(personality_text, True, (255, 255, 0))
        self.screen.blit(personality_surface, (10, y_offset))
        y_offset += 20
        
        # Render kid paths
        for kid in world.kids:
            if kid.current_path and len(kid.current_path) > 1:
                self._render_kid_path(kid)
    
    def _render_kid_path(self, kid):
        """Render a kid's current path."""
        if not kid.current_path or len(kid.current_path) < 2:
            return
        
        # Convert path to screen coordinates
        screen_path = []
        for waypoint in kid.current_path:
            screen_pos = self.camera.world_to_screen(waypoint)
            screen_path.append(screen_pos.to_int_tuple())
        
        # Draw path as connected lines
        if len(screen_path) > 1:
            pygame.draw.lines(self.screen, (0, 255, 255), False, screen_path, 2)
            
            # Draw waypoints
            for i, point in enumerate(screen_path):
                color = (255, 0, 0) if i == kid.path_index else (0, 255, 255)
                safe_circle(self.screen, color, point, 3)
    
    def toggle_debug(self):
        """Toggle debug overlay on/off."""
        self.debug_enabled = not self.debug_enabled
    
    def toggle_help(self):
        """Toggle help overlay on/off."""
        self.help_enabled = not self.help_enabled
    
    def _render_help_overlay(self):
        """Render help overlay with controls."""
        font = self._get_font(16)
        y_offset = 10
        
        # Help title
        title_text = "Candy Capitalism - Controls"
        title_surface = font.render(title_text, True, (255, 255, 0))
        self.screen.blit(title_surface, (10, y_offset))
        y_offset += 30
        
        # Camera controls
        controls = [
            "Camera Movement:",
            "  Arrow Keys - Pan around map",
            "  Mouse Wheel - Zoom in/out",
            "  +/- Keys - Zoom in/out",
            "  R - Reset camera to center",
            "",
                "Debug:",
                "  F3 - Toggle debug overlay",
                "  H - Toggle this help",
                "  I - Toggle inventory display",
                "  E - Toggle economy debug overlay",
            "",
            "Game:",
            "  SPACE - Start game",
            "  ESC - Quit"
        ]
        
        for control in controls:
            if control == "":
                y_offset += 10
                continue
            
            color = (255, 255, 255) if control.endswith(":") else (200, 200, 200)
            text_surface = font.render(control, True, color)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
    
    def _render_house_cooldown(self, house: House, screen_pos: Vector2):
        """Render house cooldown indicator."""
        # Draw cooldown progress bar above house
        progress = house.get_cooldown_progress()
        bar_width = 30
        bar_height = 4
        bar_x = screen_pos.x - bar_width // 2
        bar_y = screen_pos.y - 25
        
        # Background (empty)
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Progress fill
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            color = (0, 255, 0) if progress > 0.8 else (255, 255, 0) if progress > 0.4 else (255, 0, 0)
            pygame.draw.rect(self.screen, color, 
                           (bar_x, bar_y, fill_width, bar_height))
        
        # Cooldown text
        if house.dispense_cooldown > 0:
            font = self._get_font(10)
            cooldown_text = f"{house.dispense_cooldown:.1f}s"
            text_surface = font.render(cooldown_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_pos.x, bar_y - 8))
            self.screen.blit(text_surface, text_rect)
    
    def _render_personality_indicator(self, kid: Kid, screen_pos: Vector2):
        """Render personality indicator above kid."""
        # Personality letter mapping
        personality_letters = {
            "VALUE_INVESTOR": "V",
            "FOMO_CHASER": "F", 
            "HOARDER": "H",
            "DIVERSIFIER": "D",
            "SOCIAL_TRADER": "S"
        }
        
        letter = personality_letters.get(kid.personality.name, "?")
        
        # Draw background circle
        circle_pos = (int(screen_pos.x), int(screen_pos.y - 35))
        safe_circle(self.screen, (0, 0, 0), circle_pos, 8)
        safe_circle(self.screen, (255, 255, 255), circle_pos, 8, 2)
        
        # Draw letter
        font = self._get_font(12)
        text_surface = font.render(letter, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=circle_pos)
        self.screen.blit(text_surface, text_rect)
    
    def emit_candy_particles(self, position: Vector2, candy_type: str = "chocolate"):
        """Emit particles when candy is dispensed."""
        self.particle_system.emit_candy_particles(position, candy_type)
    
    def toggle_inventory_display(self, world=None):
        """Toggle inventory display on/off."""
        self.inventory_display_enabled = not self.inventory_display_enabled
        
        if self.inventory_display_enabled:
            self.inventory_manager.show_main_display()
            # Auto-select first kid if available
            if world and world.kids and not self.inventory_manager.selected_kid_id:
                self.select_kid_for_inventory(world.kids[0])
        else:
            self.inventory_manager.hide_main_display()
    
    def select_kid_for_inventory(self, kid: Kid):
        """Select a kid to show inventory for."""
        self.inventory_manager.select_kid(kid)
    
    def _render_possession_glow(self, kid: Kid, screen_pos: Vector2):
        """Render possession glow effect around possessed kid."""
        # Check if this kid is possessed
        if not hasattr(self, 'current_world') or not self.current_world:
            return
        
        possession_system = self.current_world.possession_system
        if not possession_system or not possession_system.is_possessing():
            return
        
        possessed_kid = possession_system.get_possessed_kid()
        if not possessed_kid or possessed_kid.id != kid.id:
            return
        
        # Red pulsing glow for possessed kids
        pulse = (math.sin(time.time() * 4) + 1) / 2  # Faster pulse
        base_radius = 15
        glow_radius = base_radius + int(pulse * 5)  # Pulsing size
        
        # Calculate pulsing red color with clamped values
        g = int(80 + pulse * 80)
        b = int(80 + pulse * 80)
        glow_color = (255, min(255, g), min(255, b))  # Clamp RGB values to 0-255
        
        # Draw multiple circles for glow effect
        for i in range(3):
            alpha = max(0, min(255, 120 - (i * 35)))  # Clamp alpha to 0-255
            radius = glow_radius + (i * 3)
            
            # CRITICAL: Ensure radius fits within surface
            max_radius = 25  # Safe maximum radius for possession glow
            radius = min(radius, max_radius)
            
            # Surface size must be at least 2*radius + 4 for safety margins
            surface_size = max(2 * radius + 4, 4)
            
            # Ensure color components are valid integers in 0-255 range
            r = max(0, min(255, int(glow_color[0])))
            g = max(0, min(255, int(glow_color[1])))
            b = max(0, min(255, int(glow_color[2])))
            a = max(0, min(255, int(alpha)))
            
            glow_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            center_pos = (surface_size // 2, surface_size // 2)
            # Draw RGB-only, then apply alpha to the surface
            pygame.draw.circle(glow_surface, (r, g, b), center_pos, radius)
            glow_surface.set_alpha(a)
            
            # Blit to screen
            glow_rect = glow_surface.get_rect(center=screen_pos.to_int_tuple())
            self.screen.blit(glow_surface, glow_rect)
    
    def clear_cache(self):
        """Clear sprite and font caches."""
        self.sprite_cache.clear()
        self.font_cache.clear()
