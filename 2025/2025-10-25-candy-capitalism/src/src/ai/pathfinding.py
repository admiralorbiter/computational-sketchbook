"""
Pathfinding system using A* algorithm.

Implements A* pathfinding with obstacle avoidance for kids to navigate
around houses and other obstacles in the world.
"""

import heapq
import time
from typing import List, Tuple, Optional, Dict, Set
from ..utils.vector2 import Vector2
from ..core.config_manager import config_manager


class PathNode:
    """Represents a node in the pathfinding grid."""
    
    def __init__(self, x: int, y: int, walkable: bool = True):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.g_cost = 0  # Distance from start
        self.h_cost = 0  # Distance to end (heuristic)
        self.f_cost = 0  # Total cost (g + h)
        self.parent = None
    
    def __lt__(self, other):
        """For heapq comparison."""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        """For equality comparison."""
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """For set operations."""
        return hash((self.x, self.y))


class PathfindingGrid:
    """Grid-based navigation system for pathfinding."""
    
    def __init__(self, world_width: int, world_height: int, cell_size: int = 20):
        """
        Initialize the pathfinding grid.
        
        Args:
            world_width: Width of the world in pixels
            world_height: Height of the world in pixels
            cell_size: Size of each grid cell in pixels
        """
        self.world_width = world_width
        self.world_height = world_height
        self.cell_size = cell_size
        
        # Calculate grid dimensions
        self.grid_width = world_width // cell_size
        self.grid_height = world_height // cell_size
        
        # Create grid of nodes
        self.grid = []
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                row.append(PathNode(x, y, True))
            self.grid.append(row)
        
        # Obstacles (houses, etc.)
        self.obstacles: Set[Tuple[int, int]] = set()
    
    def world_to_grid(self, world_pos: Vector2) -> Tuple[int, int]:
        """Convert world position to grid coordinates."""
        x = int(world_pos.x // self.cell_size)
        y = int(world_pos.y // self.cell_size)
        return (x, y)
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Vector2:
        """Convert grid coordinates to world position (center of cell)."""
        world_x = (grid_x + 0.5) * self.cell_size
        world_y = (grid_y + 0.5) * self.cell_size
        return Vector2(world_x, world_y)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if grid position is valid."""
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a grid position is walkable."""
        if not self.is_valid_position(x, y):
            return False
        
        # Check if it's an obstacle
        if (x, y) in self.obstacles:
            return False
        
        return self.grid[y][x].walkable
    
    def add_obstacle(self, world_pos: Vector2, radius: float = 20):
        """
        Add an obstacle at a world position.
        
        Args:
            world_pos: Position of the obstacle
            radius: Radius of the obstacle in pixels
        """
        # Convert to grid coordinates
        center_x, center_y = self.world_to_grid(world_pos)
        
        # Calculate radius in grid cells
        grid_radius = int(radius // self.cell_size) + 1
        
        # Mark cells within radius as obstacles
        for dx in range(-grid_radius, grid_radius + 1):
            for dy in range(-grid_radius, grid_radius + 1):
                x = center_x + dx
                y = center_y + dy
                
                if self.is_valid_position(x, y):
                    # Check if within circular radius
                    distance = ((dx * self.cell_size) ** 2 + (dy * self.cell_size) ** 2) ** 0.5
                    if distance <= radius:
                        self.obstacles.add((x, y))
    
    def remove_obstacle(self, world_pos: Vector2, radius: float = 20):
        """Remove an obstacle at a world position."""
        center_x, center_y = self.world_to_grid(world_pos)
        grid_radius = int(radius // self.cell_size) + 1
        
        for dx in range(-grid_radius, grid_radius + 1):
            for dy in range(-grid_radius, grid_radius + 1):
                x = center_x + dx
                y = center_y + dy
                
                if self.is_valid_position(x, y):
                    distance = ((dx * self.cell_size) ** 2 + (dy * self.cell_size) ** 2) ** 0.5
                    if distance <= radius:
                        self.obstacles.discard((x, y))
    
    def get_neighbors(self, node: PathNode) -> List[PathNode]:
        """Get walkable neighbors of a node."""
        neighbors = []
        
        # 8-directional movement
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                x = node.x + dx
                y = node.y + dy
                
                if self.is_walkable(x, y):
                    neighbors.append(self.grid[y][x])
        
        return neighbors
    
    def get_distance(self, node_a: PathNode, node_b: PathNode) -> float:
        """Calculate distance between two nodes."""
        dx = abs(node_a.x - node_b.x)
        dy = abs(node_a.y - node_b.y)
        
        # Diagonal movement costs more
        if dx > 0 and dy > 0:
            return 1.414  # sqrt(2)
        else:
            return 1.0


class Pathfinder:
    """A* pathfinding implementation."""
    
    def __init__(self, grid: PathfindingGrid):
        self.grid = grid
        self.path_cache: Dict[Tuple, Tuple[List[Vector2], float]] = {}
        self.cache_lifetime = 5.0  # seconds
    
    def find_path(self, start: Vector2, end: Vector2) -> Optional[List[Vector2]]:
        """
        Find a path from start to end using A*.
        
        Args:
            start: Starting position in world coordinates
            end: Ending position in world coordinates
            
        Returns:
            List of waypoints in world coordinates, or None if no path found
        """
        # Check cache first
        cache_key = (int(start.x), int(start.y), int(end.x), int(end.y))
        if cache_key in self.path_cache:
            path, timestamp = self.path_cache[cache_key]
            if time.time() - timestamp < self.cache_lifetime:
                return path
        
        # Convert to grid coordinates
        start_grid = self.grid.world_to_grid(start)
        end_grid = self.grid.world_to_grid(end)
        
        if not self.grid.is_valid_position(*start_grid) or not self.grid.is_valid_position(*end_grid):
            return None
        
        # Get start and end nodes
        start_node = self.grid.grid[start_grid[1]][start_grid[0]]
        end_node = self.grid.grid[end_grid[1]][end_grid[0]]
        
        if not start_node.walkable or not end_node.walkable:
            return None
        
        # A* algorithm
        open_set = []
        closed_set = set()
        
        # Initialize start node
        start_node.g_cost = 0
        start_node.h_cost = self._heuristic(start_node, end_node)
        start_node.f_cost = start_node.g_cost + start_node.h_cost
        start_node.parent = None
        
        heapq.heappush(open_set, start_node)
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current == end_node:
                # Found path, reconstruct it
                path = self._reconstruct_path(current)
                # Cache the result
                self.path_cache[cache_key] = (path, time.time())
                return path
            
            closed_set.add(current)
            
            # Check neighbors
            for neighbor in self.grid.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                # Calculate tentative g cost
                tentative_g = current.g_cost + self.grid.get_distance(current, neighbor)
                
                # If this path to neighbor is better, update it
                if neighbor not in [node for node in open_set] or tentative_g < neighbor.g_cost:
                    neighbor.parent = current
                    neighbor.g_cost = tentative_g
                    neighbor.h_cost = self._heuristic(neighbor, end_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    
                    if neighbor not in [node for node in open_set]:
                        heapq.heappush(open_set, neighbor)
        
        # No path found
        return None
    
    def _heuristic(self, node_a: PathNode, node_b: PathNode) -> float:
        """Calculate heuristic distance between two nodes (Manhattan distance)."""
        dx = abs(node_a.x - node_b.x)
        dy = abs(node_a.y - node_b.y)
        return dx + dy
    
    def _reconstruct_path(self, end_node: PathNode) -> List[Vector2]:
        """Reconstruct path from end node back to start."""
        path = []
        current = end_node
        
        while current is not None:
            world_pos = self.grid.grid_to_world(current.x, current.y)
            path.append(world_pos)
            current = current.parent
        
        # Reverse to get start-to-end path
        path.reverse()
        return path
    
    def clear_cache(self):
        """Clear the path cache."""
        self.path_cache.clear()
    
    def update_obstacles(self, houses: List):
        """Update obstacles based on current houses."""
        # Clear existing obstacles
        self.grid.obstacles.clear()
        
        # Add houses as obstacles
        for house in houses:
            if hasattr(house, 'position'):
                self.grid.add_obstacle(house.position, 30)  # 30 pixel radius around house


class PathfindingManager:
    """Manages pathfinding for the entire game world."""
    
    def __init__(self, world_width: int, world_height: int):
        self.grid = PathfindingGrid(world_width, world_height)
        self.pathfinder = Pathfinder(self.grid)
        self.world_width = world_width
        self.world_height = world_height
    
    def find_path(self, start: Vector2, end: Vector2) -> Optional[List[Vector2]]:
        """Find a path from start to end."""
        return self.pathfinder.find_path(start, end)
    
    def update_obstacles(self, houses: List):
        """Update obstacles in the pathfinding grid."""
        self.pathfinder.update_obstacles(houses)
    
    def is_position_walkable(self, position: Vector2) -> bool:
        """Check if a position is walkable."""
        grid_x, grid_y = self.grid.world_to_grid(position)
        return self.grid.is_walkable(grid_x, grid_y)
    
    def get_debug_grid(self) -> List[Tuple[int, int, bool]]:
        """Get grid data for debugging visualization."""
        debug_data = []
        for y in range(self.grid.grid_height):
            for x in range(self.grid.grid_width):
                walkable = self.grid.is_walkable(x, y)
                debug_data.append((x, y, walkable))
        return debug_data
