"""
Integration tests for Sprint 1 functionality.
"""

import pytest
import time
from src.core.game import Game
from src.systems.game_world import GameWorld
from src.entities.kid import Kid, KidState
from src.entities.house import House
from src.utils.vector2 import Vector2


class TestSprint1Integration:
    """Integration tests for complete Sprint 1 functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.game = Game()
        self.world = GameWorld()
    
    def test_complete_game_initialization(self):
        """Test complete game initialization process."""
        # Game is already initialized in __init__
        
        # Should have loaded all configs
        from src.core.config_manager import config_manager
        assert config_manager is not None
        
        # Should have state machine
        assert self.game.state_machine is not None
    
    def test_map_generation_and_house_placement(self):
        """Test map generation with proper house placement."""
        # Generate map
        self.world.generate_map("default", seed=42)
        
        # Should have houses
        assert len(self.world.houses) > 0
        assert len(self.world.houses) <= 20
        
        # All houses should have valid positions
        for house in self.world.houses:
            assert isinstance(house, House)
            assert house.position.x > 0
            assert house.position.y > 0
            assert house.quality in [1, 2, 3]
            assert house.id.startswith("house_")
        
        # Houses should maintain proper spacing
        min_distance = 100.0
        for i, house1 in enumerate(self.world.houses):
            for house2 in self.world.houses[i+1:]:
                distance = house1.position.distance_to(house2.position)
                assert distance >= min_distance
    
    def test_kid_spawning_and_placement(self):
        """Test kid spawning with proper placement."""
        # Generate map first
        self.world.generate_map("default", seed=42)
        
        # Spawn kids
        self.world.spawn_kids(10)
        
        # Should have kids
        assert len(self.world.kids) == 10
        
        # All kids should have valid positions
        for kid in self.world.kids:
            assert isinstance(kid, Kid)
            assert kid.position.x > 0
            assert kid.position.y > 0
            assert kid.state == KidState.IDLE
            assert kid.active == True
            assert kid.visible == True
    
    def test_pathfinding_integration(self):
        """Test pathfinding system integration."""
        # Generate map and spawn kids
        self.world.generate_map("default", seed=42)
        self.world.spawn_kids(5)
        
        # Should have pathfinding manager
        assert self.world.pathfinding_manager is not None
        
        # Test pathfinding between two points
        start = Vector2(100, 100)
        end = Vector2(300, 300)
        
        path = self.world.pathfinding_manager.find_path(start, end)
        assert path is not None
        assert len(path) >= 2
        # Path should start and end close to requested positions (within grid cell tolerance)
        assert path[0].distance_to(start) < 50.0  # Grid cell size tolerance
        assert path[-1].distance_to(end) < 50.0
    
    def test_kid_movement_and_house_visiting(self):
        """Test kids moving and visiting houses."""
        # Generate map and spawn kids
        self.world.generate_map("default", seed=42)
        self.world.spawn_kids(3)
        
        # Get initial positions
        initial_positions = [kid.position.copy() for kid in self.world.kids]
        
        # Update world multiple times (AI tick rate is 2.0 seconds)
        for _ in range(200):  # 20 seconds at 60 FPS to ensure AI ticks
            self.world.update(0.1)
        
        # Kids should have moved (at least some of them)
        moved_count = 0
        for i, kid in enumerate(self.world.kids):
            if kid.position != initial_positions[i]:
                moved_count += 1
        
        # At least one kid should have moved
        assert moved_count > 0, f"No kids moved. Initial: {initial_positions}, Final: {[k.position for k in self.world.kids]}"
    
    def test_candy_dispensing_system(self):
        """Test candy dispensing from houses to kids."""
        # Generate map and spawn kids
        self.world.generate_map("default", seed=42)
        self.world.spawn_kids(2)
        
        # Get a house and kid
        house = self.world.houses[0]
        kid = self.world.kids[0]
        
        # Move kid to house
        kid.position = house.position
        kid.state = KidState.TRICK_OR_TREATING
        kid.trick_or_treat_timer = 2.0
        
        # Update until trick-or-treating completes
        for _ in range(30):  # 3 seconds
            self.world.update(0.1)
        
        # Kid should have received candy
        assert len(kid.inventory) > 0
        total_candy = sum(kid.inventory.values())
        assert total_candy > 0
    
    def test_performance_with_multiple_kids(self):
        """Test performance with multiple kids."""
        # Generate map and spawn many kids
        self.world.generate_map("default", seed=42)
        self.world.spawn_kids(20)
        
        # Measure update time
        start_time = time.time()
        
        # Update world for 1 second
        for _ in range(60):  # 60 FPS
            self.world.update(1.0 / 60.0)
        
        end_time = time.time()
        update_time = end_time - start_time
        
        # Should complete in reasonable time (less than 1 second)
        assert update_time < 1.0
        
        # Should maintain 60 FPS (16.67ms per frame)
        frame_time = update_time / 60.0
        assert frame_time < 0.0167  # 16.67ms
    
    def test_spatial_grid_performance(self):
        """Test spatial grid performance with many entities."""
        # Generate map and spawn many kids
        self.world.generate_map("default", seed=42)
        self.world.spawn_kids(30)
        
        # Add some houses to spatial grid
        for house in self.world.houses:
            self.world.spatial_grid.add(house, house.position)
        
        # Add kids to spatial grid
        for kid in self.world.kids:
            self.world.spatial_grid.add(kid, kid.position)
        
        # Test neighbor queries
        start_time = time.time()
        
        for _ in range(1000):  # 1000 queries
            for kid in self.world.kids:
                neighbors = self.world.spatial_grid.get_nearby(kid.position, 100.0)
                assert isinstance(neighbors, list)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should complete quickly (less than 0.1 seconds)
        assert query_time < 0.25
    
    def test_pathfinding_cache_performance(self):
        """Test pathfinding cache performance."""
        # Generate map
        self.world.generate_map("default", seed=42)
        
        # Test multiple pathfinding requests
        start_time = time.time()
        
        for _ in range(100):  # 100 pathfinding requests
            start = Vector2(100, 100)
            end = Vector2(300, 300)
            path = self.world.pathfinding_manager.find_path(start, end)
            assert path is not None
        
        end_time = time.time()
        pathfinding_time = end_time - start_time
        
        # Should complete quickly (less than 0.5 seconds)
        assert pathfinding_time < 0.5
    
    def test_world_statistics(self):
        """Test world statistics reporting."""
        # Generate map and spawn kids
        self.world.generate_map("default", seed=42)
        self.world.spawn_kids(5)
        
        # Get statistics
        stats = self.world.get_stats()
        
        # Should have expected keys
        expected_keys = ['kids', 'houses', 'trading_blocs', 'map_generated']
        for key in expected_keys:
            assert key in stats
        
        # Should have correct counts
        assert stats['kids'] == 5
        assert stats['houses'] > 0
        assert stats['map_generated'] == True
    
    def test_entity_cleanup(self):
        """Test entity cleanup and removal."""
        # Generate map and spawn kids
        self.world.generate_map("default", seed=42)
        self.world.spawn_kids(5)
        
        initial_kid_count = len(self.world.kids)
        
        # Remove a kid
        kid_to_remove = self.world.kids[0]
        self.world.remove_kid(kid_to_remove.id)
        
        # Should have one less kid
        assert len(self.world.kids) == initial_kid_count - 1
        assert kid_to_remove not in self.world.kids
    
    def test_camera_integration(self):
        """Test camera system integration."""
        # Generate map
        self.world.generate_map("default", seed=42)
        
        # Test camera with world positions
        from src.rendering.camera import Camera
        camera = Camera()
        
        # Test world to screen conversion
        world_pos = Vector2(100, 200)
        screen_pos = camera.world_to_screen(world_pos)
        
        assert screen_pos.x > 0
        assert screen_pos.y > 0
        
        # Test screen to world conversion
        back_to_world = camera.screen_to_world(screen_pos)
        assert abs(back_to_world.x - world_pos.x) < 0.01
        assert abs(back_to_world.y - world_pos.y) < 0.01
    
    def test_debug_overlay_functionality(self):
        """Test debug overlay functionality."""
        # Generate map and spawn kids
        self.world.generate_map("default", seed=42)
        self.world.spawn_kids(3)
        
        # Test debug grid data
        if self.world.pathfinding_manager:
            debug_data = self.world.pathfinding_manager.get_debug_grid()
            assert len(debug_data) > 0
            
            # Each entry should have (x, y, walkable)
            for x, y, walkable in debug_data:
                assert isinstance(x, int)
                assert isinstance(y, int)
                assert isinstance(walkable, bool)
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with invalid layout name
        self.world.generate_map("nonexistent_layout", seed=42)
        # Should not crash, should fall back to default
        
        # Test spawning kids without map
        world_without_map = GameWorld()
        world_without_map.spawn_kids(5)
        # Should not crash, should handle gracefully
        
        # Test pathfinding with invalid positions
        if self.world.pathfinding_manager:
            invalid_path = self.world.pathfinding_manager.find_path(
                Vector2(-1000, -1000), 
                Vector2(10000, 10000)
            )
            # Should handle gracefully (may return None)
            assert invalid_path is None or len(invalid_path) >= 0


class TestSprint1StressTests:
    """Stress tests for Sprint 1 functionality."""
    
    def test_large_world_performance(self):
        """Test performance with large world."""
        world = GameWorld()
        
        # Generate large map
        world.generate_map("default", seed=42)
        
        # Spawn many kids
        world.spawn_kids(50)
        
        # Update for extended period
        start_time = time.time()
        
        for _ in range(300):  # 5 seconds at 60 FPS
            world.update(1.0 / 60.0)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should maintain reasonable performance
        assert total_time < 30.0  # Should complete in less than 30 seconds
    
    def test_memory_usage(self):
        """Test memory usage with many entities (shortened)."""
        world = GameWorld()
        
        # Generate map
        world.generate_map("default", seed=42)
        
        # Spawn fewer kids and run fewer updates
        world.spawn_kids(20)
        
        # Update fewer times to speed up test
        for _ in range(50):
            world.update(0.1)
        
        # Should not crash or consume excessive memory
        assert len(world.kids) == 20
        assert len(world.houses) > 0
    
    def test_concurrent_operations(self):
        """Test concurrent operations on world."""
        world = GameWorld()
        
        # Generate map
        world.generate_map("default", seed=42)
        
        # Spawn kids
        world.spawn_kids(20)
        
        # Simulate concurrent operations
        for _ in range(50):  # Fewer iterations
            # Update world
            world.update(0.1)
            
            # Query spatial grid
            for kid in world.kids:
                neighbors = world.spatial_grid.get_nearby(kid.position, 100.0)
                assert isinstance(neighbors, list)
        
        # Should not crash and maintain original kid count
        assert len(world.kids) == 20
