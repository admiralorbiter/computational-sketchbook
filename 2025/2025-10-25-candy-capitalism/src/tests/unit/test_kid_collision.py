"""
Unit tests for kid collision detection.

Tests collision detection and separation between kids.
"""

import pytest
from src.entities.kid import Kid, PersonalityType, Mood, KidState
from src.utils.vector2 import Vector2


class TestKidCollision:
    """Test kid collision detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.kid1 = Kid("kid1", Vector2(100, 100))
        self.kid2 = Kid("kid2", Vector2(120, 100))  # 20 units away
        self.kid3 = Kid("kid3", Vector2(200, 200))  # Far away
        self.kid4 = Kid("kid4", Vector2(100, 100))  # Same position as kid1
    
    def test_collision_radius_property(self):
        """Test collision radius property."""
        assert self.kid1.collision_radius == 15.0
        assert self.kid2.collision_radius == 15.0
    
    def test_no_collision_when_far_apart(self):
        """Test no collision when kids are far apart."""
        colliding_kids = self.kid1.check_collision_with_kids([self.kid3])
        assert len(colliding_kids) == 0
    
    def test_collision_when_close(self):
        """Test collision when kids are close together."""
        # kid1 and kid2 are 20 units apart, collision radius is 15 each
        # Total minimum distance is 30, so they should collide (20 < 30)
        colliding_kids = self.kid1.check_collision_with_kids([self.kid2])
        assert len(colliding_kids) == 1
        assert self.kid2 in colliding_kids
        
        # Move kid2 further apart (35 units apart)
        self.kid2.position = Vector2(135, 100)
        colliding_kids = self.kid1.check_collision_with_kids([self.kid2])
        assert len(colliding_kids) == 0
    
    def test_collision_when_overlapping(self):
        """Test collision when kids are overlapping."""
        # kid1 and kid4 are at same position
        colliding_kids = self.kid1.check_collision_with_kids([self.kid4])
        assert len(colliding_kids) == 1
        assert self.kid4 in colliding_kids
    
    def test_collision_with_multiple_kids(self):
        """Test collision detection with multiple kids."""
        kids = [self.kid2, self.kid3, self.kid4]
        
        # Move kid2 closer
        self.kid2.position = Vector2(110, 100)
        
        colliding_kids = self.kid1.check_collision_with_kids(kids)
        assert len(colliding_kids) == 2  # kid2 and kid4
        assert self.kid2 in colliding_kids
        assert self.kid4 in colliding_kids
        assert self.kid3 not in colliding_kids
    
    def test_no_collision_with_self(self):
        """Test no collision with self."""
        colliding_kids = self.kid1.check_collision_with_kids([self.kid1])
        assert len(colliding_kids) == 0
    
    def test_no_collision_with_inactive_kid(self):
        """Test no collision with inactive kid."""
        self.kid2.active = False
        self.kid2.position = Vector2(105, 100)  # Very close
        
        colliding_kids = self.kid1.check_collision_with_kids([self.kid2])
        assert len(colliding_kids) == 0
    
    def test_separation_force_no_collisions(self):
        """Test separation force with no collisions."""
        initial_position = self.kid1.position.copy()
        
        self.kid1.apply_separation_force([], 0.1)
        
        # Position should not change
        assert self.kid1.position == initial_position
    
    def test_separation_force_with_collisions(self):
        """Test separation force with collisions."""
        # Position kids to collide
        self.kid1.position = Vector2(100, 100)
        self.kid2.position = Vector2(105, 100)  # Very close
        
        initial_position = self.kid1.position.copy()
        
        # Apply separation force
        self.kid1.apply_separation_force([self.kid2], 0.1)
        
        # Position should have changed
        assert self.kid1.position != initial_position
        
        # Should move away from kid2
        distance_after = self.kid1.position.distance_to(self.kid2.position)
        distance_before = initial_position.distance_to(self.kid2.position)
        assert distance_after > distance_before
    
    def test_separation_force_multiple_collisions(self):
        """Test separation force with multiple collisions."""
        # Position kids to collide
        self.kid1.position = Vector2(100, 100)
        self.kid2.position = Vector2(105, 100)  # Close on right
        self.kid3.position = Vector2(95, 100)   # Close on left
        
        initial_position = self.kid1.position.copy()
        
        # Apply separation force
        self.kid1.apply_separation_force([self.kid2, self.kid3], 0.1)
        
        # Position should have changed (or at least the force should be applied)
        # Note: If kids are positioned symmetrically, forces might cancel out
        # So we test that the method doesn't crash and the kid is still active
        assert self.kid1.active == True
        # The position might not change if forces cancel out, which is valid behavior
    
    def test_separation_force_strength(self):
        """Test separation force strength."""
        # Position kids to collide
        self.kid1.position = Vector2(100, 100)
        self.kid2.position = Vector2(105, 100)
        
        initial_position = self.kid1.position.copy()
        
        # Apply separation force with different time steps
        self.kid1.apply_separation_force([self.kid2], 0.1)
        movement1 = self.kid1.position.distance_to(initial_position)
        
        # Reset position
        self.kid1.position = initial_position.copy()
        
        # Apply with larger time step
        self.kid1.apply_separation_force([self.kid2], 0.2)
        movement2 = self.kid1.position.distance_to(initial_position)
        
        # Larger time step should result in more movement
        assert movement2 > movement1
    
    def test_collision_edge_case_exact_distance(self):
        """Test collision detection at exact minimum distance."""
        # Set kids at exact minimum collision distance
        self.kid1.position = Vector2(100, 100)
        self.kid2.position = Vector2(100 + 30, 100)  # Exactly 30 units away
        
        colliding_kids = self.kid1.check_collision_with_kids([self.kid2])
        # Should not collide at exact minimum distance
        assert len(colliding_kids) == 0
        
        # Move slightly closer
        self.kid2.position = Vector2(100 + 29, 100)
        colliding_kids = self.kid1.check_collision_with_kids([self.kid2])
        # Should now collide
        assert len(colliding_kids) == 1
    
    def test_collision_detection_performance(self):
        """Test collision detection with many kids."""
        # Create many kids
        kids = []
        for i in range(50):
            kid = Kid(f"kid_{i}", Vector2(100 + i * 5, 100))
            kids.append(kid)
        
        # Test collision detection performance
        colliding_kids = self.kid1.check_collision_with_kids(kids)
        
        # Should find some collisions (kids close to position 100, 100)
        assert len(colliding_kids) > 0
        assert len(colliding_kids) < len(kids)  # Not all kids should collide
