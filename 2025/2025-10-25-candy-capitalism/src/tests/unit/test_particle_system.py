"""
Unit tests for particle system.

Tests particle effects for candy dispensing visual feedback.
"""

import pytest
from src.rendering.particle_system import Particle, ParticleEmitter, ParticleSystem
from src.utils.vector2 import Vector2


class TestParticle:
    """Test individual particle functionality."""
    
    def test_particle_creation(self):
        """Test particle creation with valid parameters."""
        position = Vector2(100, 100)
        velocity = Vector2(10, -5)
        color = (255, 255, 0)
        lifetime = 2.0
        
        particle = Particle(position, velocity, color, lifetime)
        
        assert particle.position == position
        assert particle.velocity == velocity
        assert particle.color == color
        assert particle.lifetime == lifetime
        assert particle.max_lifetime == lifetime
        assert particle.active == True
    
    def test_particle_update(self):
        """Test particle update mechanics."""
        position = Vector2(100, 100)
        velocity = Vector2(10, -5)
        color = (255, 255, 0)
        lifetime = 2.0
        
        particle = Particle(position, velocity, color, lifetime)
        initial_position = particle.position.copy()
        
        # Update with small time step
        result = particle.update(0.1)
        
        # Should still be active
        assert result == True
        assert particle.active == True
        
        # Position should have changed
        assert particle.position != initial_position
        assert particle.position.x == initial_position.x + velocity.x * 0.1
        assert particle.position.y == initial_position.y + velocity.y * 0.1
        
        # Lifetime should have decreased
        assert particle.lifetime < lifetime
    
    def test_particle_expiration(self):
        """Test particle expires after lifetime."""
        position = Vector2(100, 100)
        velocity = Vector2(10, -5)
        color = (255, 255, 0)
        lifetime = 0.5
        
        particle = Particle(position, velocity, color, lifetime)
        
        # Update beyond lifetime
        result = particle.update(1.0)
        
        # Should be inactive
        assert result == False
        assert particle.active == False
        assert particle.lifetime <= 0
    
    def test_particle_alpha_calculation(self):
        """Test particle alpha calculation for fading."""
        position = Vector2(100, 100)
        velocity = Vector2(10, -5)
        color = (255, 255, 0)
        lifetime = 2.0
        
        particle = Particle(position, velocity, color, lifetime)
        
        # At start, alpha should be 255
        assert particle.get_alpha() == 255
        
        # After half lifetime, alpha should be ~127
        particle.update(1.0)
        alpha = particle.get_alpha()
        assert 120 <= alpha <= 135  # Allow some tolerance
        
        # Near end, alpha should be low
        particle.update(0.9)
        alpha = particle.get_alpha()
        assert alpha < 50


class TestParticleEmitter:
    """Test particle emitter functionality."""
    
    def test_emitter_creation(self):
        """Test particle emitter creation."""
        position = Vector2(200, 200)
        emitter = ParticleEmitter(position, particle_count=5, spread=50.0, 
                                speed=100.0, lifetime=1.0, color=(255, 0, 0))
        
        assert emitter.position == position
        assert emitter.particle_count == 5
        assert emitter.spread == 50.0
        assert emitter.speed == 100.0
        assert emitter.lifetime == 1.0
        assert emitter.color == (255, 0, 0)
    
    def test_emitter_emit(self):
        """Test particle emission."""
        position = Vector2(200, 200)
        emitter = ParticleEmitter(position, particle_count=3, spread=30.0, 
                                speed=80.0, lifetime=1.5, color=(0, 255, 0))
        
        particles = emitter.emit()
        
        # Should emit correct number of particles
        assert len(particles) == 3
        
        # All particles should be active
        for particle in particles:
            assert particle.active == True
            assert particle.position == position
            assert particle.color == (0, 255, 0)
            # Lifetime should be within expected range (0.7 to 1.3 times base lifetime)
            assert 0.7 * 1.5 <= particle.lifetime <= 1.3 * 1.5


class TestParticleSystem:
    """Test particle system management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.particle_system = ParticleSystem()
    
    def test_particle_system_creation(self):
        """Test particle system initialization."""
        assert len(self.particle_system.particles) == 0
        assert self.particle_system.max_particles == 200
    
    def test_add_particles(self):
        """Test adding particles to system."""
        position = Vector2(100, 100)
        emitter = ParticleEmitter(position, particle_count=2)
        particles = emitter.emit()
        
        self.particle_system.add_particles(particles)
        
        assert len(self.particle_system.particles) == 2
    
    def test_particle_limit(self):
        """Test particle count limit."""
        # Create more particles than the limit
        position = Vector2(100, 100)
        emitter = ParticleEmitter(position, particle_count=250)
        particles = emitter.emit()
        
        self.particle_system.add_particles(particles)
        
        # Should be limited to max_particles
        assert len(self.particle_system.particles) == self.particle_system.max_particles
    
    def test_particle_update(self):
        """Test particle system update."""
        # Add some particles
        position = Vector2(100, 100)
        emitter = ParticleEmitter(position, particle_count=3, lifetime=0.5)
        particles = emitter.emit()
        self.particle_system.add_particles(particles)
        
        initial_count = len(self.particle_system.particles)
        
        # Update system
        self.particle_system.update(0.3)
        
        # Some particles should still be active
        assert len(self.particle_system.particles) > 0
        
        # Update beyond particle lifetime
        self.particle_system.update(0.5)
        
        # All particles should be removed
        assert len(self.particle_system.particles) == 0
    
    def test_emit_candy_particles(self):
        """Test candy particle emission."""
        position = Vector2(150, 150)
        
        # Emit chocolate particles
        self.particle_system.emit_candy_particles(position, "chocolate")
        
        # Should have particles
        assert len(self.particle_system.particles) > 0
        
        # All particles should be at the correct position
        for particle in self.particle_system.particles:
            assert particle.position == position
    
    def test_clear_particles(self):
        """Test clearing all particles."""
        # Add some particles
        position = Vector2(100, 100)
        emitter = ParticleEmitter(position, particle_count=5)
        particles = emitter.emit()
        self.particle_system.add_particles(particles)
        
        assert len(self.particle_system.particles) > 0
        
        # Clear particles
        self.particle_system.clear()
        
        assert len(self.particle_system.particles) == 0
    
    def test_get_particle_count(self):
        """Test getting particle count."""
        assert self.particle_system.get_particle_count() == 0
        
        # Add some particles
        position = Vector2(100, 100)
        emitter = ParticleEmitter(position, particle_count=3)
        particles = emitter.emit()
        self.particle_system.add_particles(particles)
        
        assert self.particle_system.get_particle_count() == 3
    
    def test_emit_curse_particles(self):
        """Test curse particle emission."""
        position = Vector2(200, 200)
        
        # Emit curse particles
        self.particle_system.emit_curse_particles(position)
        
        # Should have particles
        assert len(self.particle_system.particles) == 20  # particle_count
        
        # Check particles are dark red
        for particle in self.particle_system.particles:
            assert particle.position == position
            assert particle.color == (150, 0, 0)  # Dark red
    
    def test_emit_bless_particles(self):
        """Test bless particle emission."""
        position = Vector2(250, 250)
        
        # Emit bless particles
        self.particle_system.emit_bless_particles(position)
        
        # Should have particles
        assert len(self.particle_system.particles) == 25  # particle_count
        
        # Check particles are gold
        for particle in self.particle_system.particles:
            assert particle.position == position
            assert particle.color == (255, 215, 0)  # Gold
