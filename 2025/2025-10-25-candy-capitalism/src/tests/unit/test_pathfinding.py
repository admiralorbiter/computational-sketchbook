"""
Unit tests for pathfinding system.
"""

import pytest
from src.ai.pathfinding import PathNode, PathfindingGrid, Pathfinder, PathfindingManager
from src.utils.vector2 import Vector2


class TestPathNode:
    """Test cases for PathNode class."""
    
    def test_path_node_creation(self):
        """Test creating path nodes."""
        node = PathNode(5, 10, True)
        
        assert node.x == 5
        assert node.y == 10
        assert node.walkable == True
        assert node.g_cost == 0
        assert node.h_cost == 0
        assert node.f_cost == 0
        assert node.parent is None
    
    def test_path_node_comparison(self):
        """Test path node comparison for heapq."""
        node1 = PathNode(1, 1, True)
        node1.f_cost = 10
        
        node2 = PathNode(2, 2, True)
        node2.f_cost = 5
        
        # node2 should be "less than" node1 (lower f_cost)
        assert node2 < node1
        assert not (node1 < node2)
    
    def test_path_node_equality(self):
        """Test path node equality."""
        node1 = PathNode(3, 4, True)
        node2 = PathNode(3, 4, True)
        node3 = PathNode(3, 5, True)
        
        assert node1 == node2
        assert node1 != node3
    
    def test_path_node_hash(self):
        """Test path node hashing for set operations."""
        node1 = PathNode(1, 2, True)
        node2 = PathNode(1, 2, True)
        node3 = PathNode(2, 1, True)
        
        # Same position should have same hash
        assert hash(node1) == hash(node2)
        # Different position should have different hash
        assert hash(node1) != hash(node3)


class TestPathfindingGrid:
    """Test cases for PathfindingGrid class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.grid = PathfindingGrid(200, 200, 20)  # 10x10 grid
    
    def test_grid_creation(self):
        """Test grid creation."""
        assert self.grid.world_width == 200
        assert self.grid.world_height == 200
        assert self.grid.cell_size == 20
        assert self.grid.grid_width == 10
        assert self.grid.grid_height == 10
        assert len(self.grid.grid) == 10
        assert len(self.grid.grid[0]) == 10
    
    def test_world_to_grid_conversion(self):
        """Test world to grid coordinate conversion."""
        # Test exact cell centers
        assert self.grid.world_to_grid(Vector2(10, 10)) == (0, 0)
        assert self.grid.world_to_grid(Vector2(30, 30)) == (1, 1)
        assert self.grid.world_to_grid(Vector2(190, 190)) == (9, 9)
        
        # Test edge cases
        assert self.grid.world_to_grid(Vector2(0, 0)) == (0, 0)
        assert self.grid.world_to_grid(Vector2(199, 199)) == (9, 9)
    
    def test_grid_to_world_conversion(self):
        """Test grid to world coordinate conversion."""
        # Test cell centers
        world_pos = self.grid.grid_to_world(0, 0)
        assert world_pos.x == 10  # 0.5 * 20
        assert world_pos.y == 10
        
        world_pos = self.grid.grid_to_world(1, 1)
        assert world_pos.x == 30  # 1.5 * 20
        assert world_pos.y == 30
    
    def test_position_validation(self):
        """Test position validation."""
        # Valid positions
        assert self.grid.is_valid_position(0, 0)
        assert self.grid.is_valid_position(9, 9)
        assert self.grid.is_valid_position(5, 5)
        
        # Invalid positions
        assert not self.grid.is_valid_position(-1, 0)
        assert not self.grid.is_valid_position(0, -1)
        assert not self.grid.is_valid_position(10, 0)
        assert not self.grid.is_valid_position(0, 10)
        assert not self.grid.is_valid_position(15, 15)
    
    def test_walkable_check(self):
        """Test walkable position checking."""
        # All positions should be walkable initially
        assert self.grid.is_walkable(0, 0)
        assert self.grid.is_walkable(5, 5)
        assert self.grid.is_walkable(9, 9)
        
        # Invalid positions should not be walkable
        assert not self.grid.is_walkable(-1, 0)
        assert not self.grid.is_walkable(10, 0)
    
    def test_obstacle_management(self):
        """Test adding and removing obstacles."""
        # Add obstacle with smaller radius
        self.grid.add_obstacle(Vector2(30, 30), 10)  # Center of cell (1,1)
        
        # Cell should not be walkable
        assert not self.grid.is_walkable(1, 1)
        
        # Adjacent cells should still be walkable
        assert self.grid.is_walkable(0, 1)
        assert self.grid.is_walkable(2, 1)
        assert self.grid.is_walkable(1, 0)
        assert self.grid.is_walkable(1, 2)
        
        # Remove obstacle
        self.grid.remove_obstacle(Vector2(30, 30), 10)
        
        # Cell should be walkable again
        assert self.grid.is_walkable(1, 1)
    
    def test_neighbor_retrieval(self):
        """Test getting walkable neighbors."""
        # Add some obstacles with smaller radius
        self.grid.add_obstacle(Vector2(30, 30), 8)  # Block cell (1,1)
        
        # Get neighbors of cell (0,0)
        center_node = self.grid.grid[0][0]
        neighbors = self.grid.get_neighbors(center_node)
        
        # Should have 2-3 neighbors (not including blocked cell)
        assert 2 <= len(neighbors) <= 3
        
        # Check that blocked cell is not included
        neighbor_positions = [(n.x, n.y) for n in neighbors]
        assert (1, 1) not in neighbor_positions
    
    def test_distance_calculation(self):
        """Test distance calculation between nodes."""
        node1 = self.grid.grid[0][0]  # (0,0)
        node2 = self.grid.grid[1][1]  # (1,1)
        node3 = self.grid.grid[2][0]  # (2,0)
        
        # Diagonal distance
        distance = self.grid.get_distance(node1, node2)
        assert abs(distance - 1.414) < 0.01  # sqrt(2)
        
        # Horizontal distance (2 cells apart)
        distance = self.grid.get_distance(node1, node3)
        assert distance == 1.0  # Only 1 cell difference in x, 0 in y


class TestPathfinder:
    """Test cases for Pathfinder class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.grid = PathfindingGrid(200, 200, 20)
        self.pathfinder = Pathfinder(self.grid)
    
    def test_simple_pathfinding(self):
        """Test simple pathfinding without obstacles."""
        start = Vector2(10, 10)  # Cell (0,0)
        end = Vector2(30, 30)    # Cell (1,1)
        
        path = self.pathfinder.find_path(start, end)
        
        assert path is not None
        assert len(path) >= 2
        assert path[0] == start
        assert path[-1] == end
    
    def test_pathfinding_with_obstacles(self):
        """Test pathfinding around obstacles."""
        # Add obstacle in the middle
        self.grid.add_obstacle(Vector2(30, 30), 15)  # Block cell (1,1)
        
        start = Vector2(10, 10)  # Cell (0,0)
        end = Vector2(50, 50)    # Cell (2,2)
        
        path = self.pathfinder.find_path(start, end)
        
        assert path is not None
        assert len(path) > 2  # Should go around obstacle
        
        # Path should not go through blocked cell
        for waypoint in path:
            grid_pos = self.grid.world_to_grid(waypoint)
            assert grid_pos != (1, 1)
    
    def test_no_path_scenario(self):
        """Test pathfinding when no path exists."""
        # Block all possible paths more thoroughly
        self.grid.add_obstacle(Vector2(30, 10), 25)  # Block (1,0) with larger radius
        self.grid.add_obstacle(Vector2(50, 10), 25)  # Block (2,0) with larger radius
        self.grid.add_obstacle(Vector2(10, 30), 25)  # Block (0,1) with larger radius
        self.grid.add_obstacle(Vector2(10, 50), 25)  # Block (0,2) with larger radius
        self.grid.add_obstacle(Vector2(30, 30), 25)  # Block (1,1) to prevent diagonal
        self.grid.add_obstacle(Vector2(50, 30), 25)  # Block (2,1) to prevent diagonal
        self.grid.add_obstacle(Vector2(30, 50), 25)  # Block (1,2) to prevent diagonal
        
        start = Vector2(10, 10)  # Cell (0,0)
        end = Vector2(50, 50)    # Cell (2,2)
        
        path = self.pathfinder.find_path(start, end)
        
        # Should return None when no path exists
        assert path is None
    
    def test_path_caching(self):
        """Test path caching functionality."""
        start = Vector2(10, 10)
        end = Vector2(30, 30)
        
        # First pathfinding
        path1 = self.pathfinder.find_path(start, end)
        assert path1 is not None
        
        # Second pathfinding (should use cache)
        path2 = self.pathfinder.find_path(start, end)
        assert path2 is not None
        assert path1 == path2  # Should be identical
    
    def test_heuristic_calculation(self):
        """Test heuristic distance calculation."""
        node1 = self.grid.grid[0][0]  # (0,0)
        node2 = self.grid.grid[2][3]  # (2,3)
        
        heuristic = self.pathfinder._heuristic(node1, node2)
        expected = 2 + 3  # Manhattan distance
        assert heuristic == expected
    
    def test_path_reconstruction(self):
        """Test path reconstruction from end node."""
        # Create a simple path manually
        start_node = self.grid.grid[0][0]
        middle_node = self.grid.grid[1][1]
        end_node = self.grid.grid[2][2]
        
        # Set up parent chain
        middle_node.parent = start_node
        end_node.parent = middle_node
        
        # Reconstruct path
        path = self.pathfinder._reconstruct_path(end_node)
        
        assert len(path) == 3
        assert path[0] == self.grid.grid_to_world(0, 0)
        assert path[1] == self.grid.grid_to_world(1, 1)
        assert path[2] == self.grid.grid_to_world(2, 2)


class TestPathfindingManager:
    """Test cases for PathfindingManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PathfindingManager(400, 400)
    
    def test_manager_initialization(self):
        """Test pathfinding manager initialization."""
        assert self.manager.world_width == 400
        assert self.manager.world_height == 400
        assert self.manager.grid is not None
        assert self.manager.pathfinder is not None
    
    def test_find_path(self):
        """Test finding path through manager."""
        start = Vector2(20, 20)
        end = Vector2(60, 60)
        
        path = self.manager.find_path(start, end)
        
        assert path is not None
        assert len(path) >= 2
        # Path starts and ends close to requested positions (within grid cell tolerance)
        assert path[0].distance_to(start) < 20  # Within one cell
        assert path[-1].distance_to(end) < 20   # Within one cell
    
    def test_position_walkability(self):
        """Test checking if position is walkable."""
        # Valid position should be walkable
        assert self.manager.is_position_walkable(Vector2(50, 50))
        
        # Position outside world should not be walkable
        assert not self.manager.is_position_walkable(Vector2(500, 500))
    
    def test_obstacle_update(self):
        """Test updating obstacles from houses."""
        # Create mock houses
        class MockHouse:
            def __init__(self, x, y):
                self.position = Vector2(x, y)
        
        houses = [
            MockHouse(30, 30),
            MockHouse(60, 60)
        ]
        
        # Update obstacles
        self.manager.update_obstacles(houses)
        
        # Positions near houses should not be walkable
        assert not self.manager.is_position_walkable(Vector2(30, 30))
        assert not self.manager.is_position_walkable(Vector2(60, 60))
        
        # Positions away from houses should be walkable
        assert self.manager.is_position_walkable(Vector2(200, 200))  # Far from houses
        assert self.manager.is_position_walkable(Vector2(300, 300))  # Far from houses
    
    def test_debug_grid_data(self):
        """Test getting debug grid data."""
        debug_data = self.manager.get_debug_grid()
        
        assert len(debug_data) > 0
        
        # Each entry should have (x, y, walkable)
        for x, y, walkable in debug_data:
            assert isinstance(x, int)
            assert isinstance(y, int)
            assert isinstance(walkable, bool)
