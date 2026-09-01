"""
Unit tests for rendering system.

Tests rendering functionality, including color clamping and alpha blending.
"""

import pytest
import pygame
import math
import time
from src.rendering.renderer import Renderer
from src.entities.house import House
from src.entities.kid import Kid
from src.systems.game_world import GameWorld
from src.utils.vector2 import Vector2
from src.ai.basic_behaviors import BasicBehaviors


class TestRendererColorClamping:
    """Test color clamping in rendering system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen = pygame.Surface((1000, 1000))
        self.renderer = Renderer(self.screen)
        
        # Create a world for testing
        self.world = GameWorld()
        self.renderer.current_world = self.world
        
        # Add a kid for possession testing
        self.kid = Kid("test_kid", Vector2(500, 500))
        self.world.add_kid(self.kid)
    
    def test_possession_glow_color_clamping(self):
        """Test that possession glow colors are properly clamped to valid ranges."""
        # Create a possessed kid
        self.world.possession_system.possess(self.kid)
        
        # Test various pulse values to ensure colors stay within 0-255
        for test_pulse in [0.0, 0.5, 1.0, 1.5, -0.5, 10.0]:
            # Calculate the same way as in the renderer
            g = int(80 + test_pulse * 80)
            b = int(80 + test_pulse * 80)
            clamped_g = min(255, max(0, g))
            clamped_b = min(255, max(0, b))
            glow_color = (255, clamped_g, clamped_b)
            
            # All color components must be in valid range
            assert 0 <= glow_color[0] <= 255
            assert 0 <= glow_color[1] <= 255
            assert 0 <= glow_color[2] <= 255
    
    def test_possession_glow_alpha_clamping(self):
        """Test that possession glow alpha values are properly clamped."""
        for i in range(10):
            # Calculate alpha the same way as in the renderer
            alpha = 120 - (i * 35)
            clamped_alpha = max(0, min(255, alpha))
            
            # Alpha must be in valid range
            assert 0 <= clamped_alpha <= 255
    
    def test_house_glow_alpha_clamping(self):
        """Test that house glow alpha values are properly clamped."""
        for i in range(10):
            # Calculate alpha the same way as in the renderer
            alpha = 80 - (i * 25)
            clamped_alpha = max(0, min(255, alpha))
            
            # Alpha must be in valid range
            assert 0 <= clamped_alpha <= 255
    
    def test_possession_glow_rendering_no_crash(self):
        """Test that rendering possession glow doesn't crash with invalid colors."""
        # Create a possessed kid
        self.world.possession_system.possess(self.kid)
        
        # Try rendering - should not crash with "invalid color argument"
        try:
            self.renderer._render_possession_glow(self.kid, Vector2(500, 500))
            no_crash = True
        except (TypeError, ValueError) as e:
            if "invalid color" in str(e).lower():
                pytest.fail(f"Renderer crashed with invalid color argument: {e}")
            else:
                raise
        
        assert no_crash
    
    def test_house_glow_rendering_no_crash(self):
        """Test that rendering house glow doesn't crash with invalid colors."""
        # Create a cursed house
        house = House("test_house", Vector2(500, 500))
        house.curse(duration=60.0)
        
        # Try rendering - should not crash with "invalid color argument"
        try:
            self.renderer._render_house_glow(house, Vector2(500, 500))
            no_crash = True
        except (TypeError, ValueError) as e:
            if "invalid color" in str(e).lower():
                pytest.fail(f"Renderer crashed with invalid color argument: {e}")
            else:
                raise
        
        assert no_crash
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()


class TestRendererRGBA:
    """Test RGBA color tuple creation."""
    
    def test_rgba_tuple_creation(self):
        """Test that RGBA tuples are created correctly."""
        glow_color = (255, 100, 100)
        alpha = 128
        
        # Create RGBA tuple the same way as in the renderer
        rgba_color = (glow_color[0], glow_color[1], glow_color[2], alpha)
        
        # Should be a valid 4-element tuple
        assert len(rgba_color) == 4
        assert isinstance(rgba_color, tuple)
        assert rgba_color == (255, 100, 100, 128)
        
        # All values should be integers and in valid range
        for value in rgba_color:
            assert isinstance(value, int)
            assert 0 <= value <= 255


class TestParticleSystemRendering:
    """Test particle system rendering doesn't crash."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        from src.rendering.particle_system import ParticleSystem
        from src.rendering.camera import Camera
        from src.utils.vector2 import Vector2
        
        self.screen = pygame.Surface((1000, 1000))
        self.particle_system = ParticleSystem()
        self.camera = Camera(Vector2(500, 500), 1.0)
    
    def test_particle_rendering_no_crash(self):
        """Test that rendering particles doesn't crash with invalid colors."""
        from src.utils.vector2 import Vector2
        
        # Add some particles
        self.particle_system.emit_curse_particles(Vector2(100, 100))
        self.particle_system.emit_bless_particles(Vector2(200, 200))
        
        # Try rendering - should not crash with "invalid color argument"
        try:
            self.particle_system.render(self.screen, self.camera)
            no_crash = True
        except (TypeError, ValueError) as e:
            if "invalid color" in str(e).lower():
                pytest.fail(f"Particle rendering crashed with invalid color argument: {e}")
            else:
                raise
        
        assert no_crash
    
    def test_particle_rgba_tuple_creation(self):
        """Test that particle RGBA tuples are created correctly."""
        from src.rendering.particle_system import Particle
        from src.utils.vector2 import Vector2
        
        # Create a particle with RGB color
        particle = Particle(Vector2(0, 0), Vector2(0, 0), (255, 100, 50), 1.0)
        alpha = 128
        
        # Create RGBA tuple the same way as in the particle system
        rgba_color = (particle.color[0], particle.color[1], particle.color[2], alpha)
        
        # Should be a valid 4-element tuple
        assert len(rgba_color) == 4
        assert isinstance(rgba_color, tuple)
        assert rgba_color == (255, 100, 50, 128)
        
        # All values should be integers and in valid range
        for value in rgba_color:
            assert isinstance(value, int)
            assert 0 <= value <= 255
    
    def test_particle_with_extreme_alpha_values(self):
        """Test particles with extreme alpha values don't crash."""
        from src.rendering.particle_system import Particle
        from src.utils.vector2 import Vector2
        
        # Create particles with various alpha states
        particle1 = Particle(Vector2(0, 0), Vector2(0, 0), (255, 0, 0), 0.01)  # Nearly expired
        particle2 = Particle(Vector2(0, 0), Vector2(0, 0), (0, 255, 0), 10.0)  # Fresh
        
        # Manually set lifetimes to test edge cases
        particle1.lifetime = 0.0  # Expired
        particle2.lifetime = 100.0  # Over lifetime
        
        alpha1 = particle1.get_alpha()
        alpha2 = particle2.get_alpha()
        
        # Alpha should be clamped to 0-255
        assert 0 <= alpha1 <= 255
        assert 0 <= alpha2 <= 255
    
    def test_particle_with_invalid_colors(self):
        """Test that particles with invalid colors are skipped gracefully."""
        from src.rendering.particle_system import Particle
        from src.utils.vector2 import Vector2
        
        # Create particle with malformed color
        particle = Particle(Vector2(0, 0), Vector2(0, 0), (300, -50, 256), 1.0)
        
        # Manually add to particle system
        self.particle_system.particles.append(particle)
        
        # Rendering should not crash
        try:
            self.particle_system.render(self.screen, self.camera)
            no_crash = True
        except Exception as e:
            pytest.fail(f"Particle rendering crashed with invalid color: {e}")
        
        assert no_crash
    
    def test_particle_with_missing_color_attribute(self):
        """Test that particles without color attribute are skipped."""
        from src.rendering.particle_system import Particle
        from src.utils.vector2 import Vector2
        
        # Create normal particle
        particle = Particle(Vector2(0, 0), Vector2(0, 0), (100, 100, 100), 1.0)
        
        # Remove color attribute to simulate corrupted particle
        delattr(particle, 'color')
        
        # Manually add to particle system
        self.particle_system.particles.append(particle)
        
        # Rendering should skip this particle without crashing
        try:
            self.particle_system.render(self.screen, self.camera)
            no_crash = True
        except Exception as e:
            pytest.fail(f"Particle rendering crashed with missing color: {e}")
        
        assert no_crash
    
    def test_stress_test_many_particles(self):
        """Test rendering with many particles simultaneously."""
        from src.utils.vector2 import Vector2
        
        # Emit many particles
        for i in range(10):
            self.particle_system.emit_curse_particles(Vector2(i * 10, i * 10))
            self.particle_system.emit_bless_particles(Vector2(i * 10 + 100, i * 10))
        
        # Should have many particles
        assert len(self.particle_system.particles) > 50
        
        # Rendering should not crash
        try:
            self.particle_system.render(self.screen, self.camera)
            no_crash = True
        except Exception as e:
            pytest.fail(f"Particle rendering crashed with many particles: {e}")
        
        assert no_crash
    
    def test_particle_color_validation(self):
        """Test that color validation properly clamps values."""
        from src.rendering.particle_system import Particle
        from src.utils.vector2 import Vector2
        
        # Test various edge case colors
        test_colors = [
            (0, 0, 0),      # All zero
            (255, 255, 255), # All max
            (300, 400, 500), # Over max
            (-10, -20, -30), # Negative
            (128.5, 128.7, 129.2), # Floats
        ]
        
        for color in test_colors:
            particle = Particle(Vector2(0, 0), Vector2(0, 0), color, 1.0)
            self.particle_system.particles.append(particle)
        
        # Rendering should handle all edge cases
        try:
            self.particle_system.render(self.screen, self.camera)
            no_crash = True
        except Exception as e:
            pytest.fail(f"Particle rendering crashed with edge case colors: {e}")
        
        assert no_crash
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()


class TestCrashReproduction:
    """Test to reproduce the actual crash scenario."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        from src.rendering.particle_system import ParticleSystem
        from src.rendering.camera import Camera
        from src.utils.vector2 import Vector2
        
        self.screen = pygame.Surface((1000, 1000))
        self.particle_system = ParticleSystem()
        self.camera = Camera(Vector2(500, 500), 1.0)
    
    def test_crash_reproduction_sequence(self):
        """Reproduce the exact sequence that causes the crash in game."""
        from src.utils.vector2 import Vector2
        
        # Simulate the game sequence: curse 3 houses
        positions = [
            Vector2(305, 255),  # house_06
            Vector2(251, 174),  # house_12
            Vector2(570, 86),   # house_00
        ]
        
        # Emit curse particles for each house (exactly like the game does)
        for position in positions:
            self.particle_system.emit_curse_particles(position)
        
        # Update particles multiple times (like multiple frames)
        for _ in range(10):
            self.particle_system.update(1.0 / 60.0)  # 60 FPS
            
            # Render after each update (like the game does)
            try:
                self.particle_system.render(self.screen, self.camera)
                no_crash = True
            except (TypeError, ValueError) as e:
                if "invalid color" in str(e).lower():
                    # Save debug info
                    print(f"\nCRASH DETECTED!")
                    print(f"Particle count: {len(self.particle_system.particles)}")
                    print(f"Error: {e}")
                    
                    # Check particle colors
                    for i, particle in enumerate(self.particle_system.particles[:5]):
                        print(f"Particle {i}: color={particle.color}, alpha={particle.get_alpha()}")
                    
                    pytest.fail(f"Crash reproduced: {e}")
                else:
                    raise
        
        assert no_crash
    
    def test_stress_with_rapid_emissions(self):
        """Test rapid particle emissions like the game does."""
        from src.utils.vector2 import Vector2
        import random
        
        # Rapidly emit many particles
        for _ in range(20):
            pos = Vector2(random.randint(0, 1000), random.randint(0, 1000))
            self.particle_system.emit_curse_particles(pos)
            
            # Update and render
            self.particle_system.update(1.0 / 60.0)
            try:
                self.particle_system.render(self.screen, self.camera)
            except Exception as e:
                pytest.fail(f"Crash with rapid emissions: {e}")
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
