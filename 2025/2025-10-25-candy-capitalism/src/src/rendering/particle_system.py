"""
Particle system for visual effects.

Provides particle effects for candy dispensing and other visual feedback.
"""

import random
import math
from typing import List, Tuple
from ..utils.vector2 import Vector2


class Particle:
    """Individual particle with position, velocity, and lifetime."""
    
    def __init__(self, position: Vector2, velocity: Vector2, color: Tuple[int, int, int], lifetime: float):
        self.position = position.copy()
        self.velocity = velocity.copy()
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.active = True
    
    def update(self, dt: float) -> bool:
        """
        Update particle position and lifetime.
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            True if particle is still active, False if expired
        """
        if not self.active:
            return False
        
        # Update position
        self.position += self.velocity * dt
        
        # Update lifetime
        self.lifetime -= dt
        
        # Check if expired
        if self.lifetime <= 0:
            self.active = False
            return False
        
        return True
    
    def get_alpha(self) -> int:
        """Get alpha value based on lifetime (fade out)."""
        if self.max_lifetime <= 0:
            return 255
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        return max(0, min(255, alpha))


class ParticleEmitter:
    """Emits particles from a specific location."""
    
    def __init__(self, position: Vector2, particle_count: int = 5, spread: float = 50.0, 
                 speed: float = 100.0, lifetime: float = 1.0, color: Tuple[int, int, int] = (255, 255, 0)):
        self.position = position
        self.particle_count = particle_count
        self.spread = spread
        self.speed = speed
        self.lifetime = lifetime
        self.color = color
    
    def emit(self) -> List[Particle]:
        """Emit a burst of particles."""
        particles = []
        
        for _ in range(self.particle_count):
            # Random direction within spread
            angle = random.uniform(0, 2 * math.pi)
            direction = Vector2(math.cos(angle), math.sin(angle))
            
            # Add some randomness to speed
            particle_speed = self.speed * random.uniform(0.5, 1.5)
            velocity = direction * particle_speed
            
            # Add some randomness to lifetime
            particle_lifetime = self.lifetime * random.uniform(0.7, 1.3)
            
            particle = Particle(self.position, velocity, self.color, particle_lifetime)
            particles.append(particle)
        
        return particles


class ParticleSystem:
    """Manages all particles in the game."""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = 200  # Limit for performance
    
    def add_particles(self, particles: List[Particle]):
        """Add particles to the system."""
        self.particles.extend(particles)
        
        # Limit total particles
        if len(self.particles) > self.max_particles:
            # Remove oldest particles
            self.particles = self.particles[-self.max_particles:]
    
    def emit_candy_particles(self, position: Vector2, candy_type: str = "chocolate"):
        """Emit particles for candy dispensing."""
        # Color based on candy type
        candy_colors = {
            "chocolate": (139, 69, 19),    # Brown
            "fruity": (255, 192, 203),     # Pink
            "sour": (255, 255, 0),         # Yellow
            "mint": (0, 255, 127),         # Green
            "caramel": (255, 165, 0),      # Orange
            "licorice": (75, 0, 130)       # Purple
        }
        
        color = candy_colors.get(candy_type, (255, 255, 0))  # Default yellow
        
        emitter = ParticleEmitter(
            position=position,
            particle_count=8,
            spread=60.0,
            speed=80.0,
            lifetime=1.5,
            color=color
        )
        
        particles = emitter.emit()
        self.add_particles(particles)
    
    def emit_trade_particles(self, kid1_pos: Vector2, kid2_pos: Vector2, 
                            offer: dict, request: dict):
        """Emit particles for a trade between two kids."""
        # Create particles that move between the two kids
        mid_point = Vector2(
            (kid1_pos.x + kid2_pos.x) / 2,
            (kid1_pos.y + kid2_pos.y) / 2
        )
        
        # Emit particles for each candy type in the trade
        all_trade_items = {**offer, **request}
        
        for candy_type, quantity in all_trade_items.items():
            # Get color for this candy type
            color = self._get_candy_color(candy_type)
            
            # Create particles that move from kid1 to kid2
            for _ in range(min(quantity, 3)):  # Max 3 particles per candy type
                # Random position between kids
                t = random.uniform(0.2, 0.8)
                start_pos = Vector2(
                    kid1_pos.x + (kid2_pos.x - kid1_pos.x) * t,
                    kid1_pos.y + (kid2_pos.y - kid1_pos.y) * t
                )
                
                # Velocity toward the other kid
                direction = (kid2_pos - kid1_pos).normalized()
                velocity = direction * random.uniform(50, 100)
                
                particle = Particle(start_pos, velocity, color, 2.0)
                self.particles.append(particle)
    
    def emit_trade_success_particles(self, position: Vector2):
        """Emit celebration particles for successful trade."""
        # Golden sparkles
        emitter = ParticleEmitter(
            position=position,
            particle_count=12,
            spread=80.0,
            speed=60.0,
            lifetime=2.0,
            color=(255, 215, 0)  # Gold
        )
        
        particles = emitter.emit()
        self.add_particles(particles)
    
    def _get_candy_color(self, candy_type: str) -> Tuple[int, int, int]:
        """Get color for a candy type."""
        candy_colors = {
            "CHOCOLATE": (139, 69, 19),    # Brown
            "FRUITY": (255, 192, 203),     # Pink
            "SOUR": (255, 255, 0),         # Yellow
            "NOVELTY": (255, 165, 0),      # Orange
            "HEALTH": (0, 255, 127),       # Green
            "TRASH": (128, 128, 128)       # Gray
        }
        return candy_colors.get(candy_type, (255, 255, 255))  # Default white
    
    def update(self, dt: float):
        """Update all particles."""
        # Update particles and remove inactive ones
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def render(self, screen, camera):
        """Render all particles."""
        for particle in self.particles:
            if not particle.active:
                continue
            
            # Convert world position to screen position
            screen_pos = camera.world_to_screen(particle.position)
            
            # Skip if off-screen
            if (screen_pos.x < -10 or screen_pos.x > screen.get_width() + 10 or
                screen_pos.y < -10 or screen_pos.y > screen.get_height() + 10):
                continue
            
            # Get alpha for fading
            alpha = particle.get_alpha()
            
            # CRITICAL: Validate and clamp all color components
            # Ensure particle.color is valid and has 3 components
            if not hasattr(particle, 'color') or not particle.color or len(particle.color) < 3:
                # Skip invalid particles
                continue
            
            # Clamp all color components to valid integer range
            r = max(0, min(255, int(particle.color[0])))
            g = max(0, min(255, int(particle.color[1])))
            b = max(0, min(255, int(particle.color[2])))
            a = max(0, min(255, int(alpha)))
            
            # Create surface with alpha and draw RGB-only, apply alpha via set_alpha
            import pygame
            particle_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (r, g, b), (4, 4), 4)
            particle_surface.set_alpha(a)
            
            # Blit to screen with integer coordinates
            screen.blit(particle_surface, (int(screen_pos.x - 4), int(screen_pos.y - 4)))
    
    def clear(self):
        """Clear all particles."""
        self.particles.clear()
    
    def get_particle_count(self) -> int:
        """Get current particle count."""
        return len(self.particles)
    
    def emit_curse_particles(self, position: Vector2):
        """Emit dark particles for curse effect."""
        emitter = ParticleEmitter(
            position=position,
            particle_count=20,
            spread=60.0,
            speed=40.0,
            lifetime=2.5,
            color=(150, 0, 0)  # Dark red
        )
        self.add_particles(emitter.emit())
    
    def emit_bless_particles(self, position: Vector2):
        """Emit golden particles for bless effect."""
        emitter = ParticleEmitter(
            position=position,
            particle_count=25,
            spread=70.0,
            speed=50.0,
            lifetime=3.0,
            color=(255, 215, 0)  # Gold
        )
        self.add_particles(emitter.emit())
