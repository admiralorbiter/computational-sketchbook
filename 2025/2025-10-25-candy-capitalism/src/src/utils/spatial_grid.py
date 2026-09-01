"""
Spatial partitioning system for efficient neighbor queries.

Uses a grid-based approach to optimize collision detection and neighbor finding
for 30+ entities in the game world.
"""

from typing import List, Tuple, Dict, Any, Optional
from .vector2 import Vector2


class SpatialGrid:
    """
    Grid-based spatial partitioning for efficient neighbor queries.
    
    Divides the world into a grid of cells and stores entities in the appropriate
    cells. This allows O(1) neighbor queries instead of O(n) for all entities.
    """
    
    def __init__(self, cell_size: float = 100.0):
        """
        Initialize spatial grid.
        
        Args:
            cell_size: Size of each grid cell in world units
        """
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], List[Any]] = {}
        self.entity_positions: Dict[Any, Tuple[int, int]] = {}
    
    def _get_cell(self, position: Vector2) -> Tuple[int, int]:
        """Get grid cell coordinates for a world position."""
        x = int(position.x // self.cell_size)
        y = int(position.y // self.cell_size)
        return (x, y)
    
    def add(self, entity: Any, position: Vector2):
        """
        Add an entity to the spatial grid.
        
        Args:
            entity: The entity to add
            position: World position of the entity
        """
        cell = self._get_cell(position)
        
        # Remove from old position if it exists
        if entity in self.entity_positions:
            old_cell = self.entity_positions[entity]
            if old_cell in self.grid and entity in self.grid[old_cell]:
                self.grid[old_cell].remove(entity)
                if not self.grid[old_cell]:  # Remove empty cells
                    del self.grid[old_cell]
        
        # Add to new position
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)
        self.entity_positions[entity] = cell
    
    def remove(self, entity: Any):
        """
        Remove an entity from the spatial grid.
        
        Args:
            entity: The entity to remove
        """
        if entity in self.entity_positions:
            cell = self.entity_positions[entity]
            if cell in self.grid and entity in self.grid[cell]:
                self.grid[cell].remove(entity)
                if not self.grid[cell]:  # Remove empty cells
                    del self.grid[cell]
            del self.entity_positions[entity]
    
    def update_position(self, entity: Any, new_position: Vector2):
        """
        Update an entity's position in the grid.
        
        Args:
            entity: The entity to update
            new_position: New world position
        """
        self.add(entity, new_position)
    
    def get_nearby(self, position: Vector2, radius: float) -> List[Any]:
        """
        Get all entities within radius of a position.
        
        Args:
            position: Center position for the search
            radius: Search radius in world units
            
        Returns:
            List of entities within the radius
        """
        center_cell = self._get_cell(position)
        radius_cells = int(radius // self.cell_size) + 1
        
        nearby = []
        
        # Check all cells within radius
        for dx in range(-radius_cells, radius_cells + 1):
            for dy in range(-radius_cells, radius_cells + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                
                if cell in self.grid:
                    for entity in self.grid[cell]:
                        # Get entity position (this assumes entities have a position attribute)
                        if hasattr(entity, 'position'):
                            entity_pos = entity.position
                        else:
                            # Fallback: we can't calculate distance without position
                            continue
                            
                        if entity_pos.distance_to(position) <= radius:
                            nearby.append(entity)
        
        return nearby
    
    def get_entities_in_cell(self, position: Vector2) -> List[Any]:
        """
        Get all entities in the same cell as the given position.
        
        Args:
            position: World position
            
        Returns:
            List of entities in the same cell
        """
        cell = self._get_cell(position)
        return self.grid.get(cell, [])
    
    def get_entities_in_rect(self, top_left: Vector2, bottom_right: Vector2) -> List[Any]:
        """
        Get all entities within a rectangular area.
        
        Args:
            top_left: Top-left corner of the rectangle
            bottom_right: Bottom-right corner of the rectangle
            
        Returns:
            List of entities within the rectangle
        """
        entities = []
        
        # Calculate cell range
        start_cell = self._get_cell(top_left)
        end_cell = self._get_cell(bottom_right)
        
        for x in range(start_cell[0], end_cell[0] + 1):
            for y in range(start_cell[1], end_cell[1] + 1):
                cell = (x, y)
                if cell in self.grid:
                    for entity in self.grid[cell]:
                        if hasattr(entity, 'position'):
                            pos = entity.position
                            if (top_left.x <= pos.x <= bottom_right.x and 
                                top_left.y <= pos.y <= bottom_right.y):
                                entities.append(entity)
        
        return entities
    
    def clear(self):
        """Clear all entities from the grid."""
        self.grid.clear()
        self.entity_positions.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the spatial grid.
        
        Returns:
            Dictionary with grid statistics
        """
        total_entities = sum(len(entities) for entities in self.grid.values())
        return {
            'total_entities': total_entities,
            'occupied_cells': len(self.grid),
            'cell_size': int(self.cell_size)
        }
    
    def debug_render(self, screen, camera=None):
        """
        Render grid cells for debugging (optional).
        
        Args:
            screen: Pygame screen surface
            camera: Camera for coordinate conversion (optional)
        """
        import pygame
        
        # This would need camera conversion to work properly
        # For now, just a placeholder
        pass
