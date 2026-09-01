"""
Map generation system for creating neighborhood layouts.

Supports both procedural generation and JSON-defined layouts with
configurable house placement, spacing, and quality distribution.
"""

import random
import json
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

from ..entities.house import House
from ..utils.vector2 import Vector2
from ..core.config_manager import config_manager


class MapGenerator:
    """
    Generates neighborhood maps with houses placed according to spacing rules.
    
    Supports both procedural generation and loading from JSON configuration files.
    """
    
    def __init__(self):
        """Initialize the map generator."""
        self.layouts = {}
        self._load_layouts()
    
    def _load_layouts(self):
        """Load neighborhood layouts from JSON configuration."""
        try:
            layout_file = Path("config/neighborhood_layouts.json")
            if layout_file.exists():
                with open(layout_file, 'r') as f:
                    self.layouts = json.load(f)
            else:
                # Fallback to default layout
                self.layouts = {
                    "default": {
                        "grid_size": [40, 40],
                        "num_houses": 18,
                        "house_spacing": 150,
                        "quality_distribution": [0.2, 0.5, 0.3],
                        "world_width": 2000,
                        "world_height": 2000
                    }
                }
        except Exception as e:
            print(f"Warning: Could not load neighborhood layouts: {e}")
            # Use hardcoded default
            self.layouts = {
                "default": {
                    "grid_size": [40, 40],
                    "num_houses": 18,
                    "house_spacing": 150,
                    "quality_distribution": [0.2, 0.5, 0.3],
                    "world_width": 2000,
                    "world_height": 2000
                }
            }
    
    def generate_map(self, layout_name: str = "default", seed: Optional[int] = None) -> List[House]:
        """
        Generate a neighborhood map with houses.
        
        Args:
            layout_name: Name of the layout configuration to use
            seed: Random seed for reproducible generation (None for random)
            
        Returns:
            List of House entities placed on the map
        """
        if layout_name not in self.layouts:
            print(f"Warning: Layout '{layout_name}' not found, using 'default'")
            layout_name = "default"
        
        layout = self.layouts[layout_name]
        
        # Set random seed for reproducible generation
        if seed is not None:
            random.seed(seed)
        
        # Extract layout parameters
        grid_size = layout["grid_size"]
        num_houses = layout["num_houses"]
        house_spacing = layout["house_spacing"]
        quality_distribution = layout["quality_distribution"]
        world_width = layout["world_width"]
        world_height = layout["world_height"]
        
        # Generate house positions
        house_positions = self._generate_house_positions(
            grid_size, num_houses, house_spacing, world_width, world_height
        )
        
        # Create house entities
        houses = []
        for i, (x, y) in enumerate(house_positions):
            # Determine house quality based on distribution
            quality = self._assign_house_quality(quality_distribution)
            
            # Create house entity
            house = House(
                house_id=f"house_{i:02d}",
                position=Vector2(x, y),
                quality=quality
            )
            houses.append(house)
        
        print(f"Generated {len(houses)} houses for layout '{layout_name}'")
        
        # Debug: Show house positions
        if houses:
            min_x = min(house.position.x for house in houses)
            max_x = max(house.position.x for house in houses)
            min_y = min(house.position.y for house in houses)
            max_y = max(house.position.y for house in houses)
            print(f"House positions: X({min_x:.0f} to {max_x:.0f}), Y({min_y:.0f} to {max_y:.0f})")
        
        return houses
    
    def _generate_house_positions(
        self, 
        grid_size: List[int], 
        num_houses: int, 
        house_spacing: float,
        world_width: int,
        world_height: int
    ) -> List[Tuple[float, float]]:
        """
        Generate valid house positions with proper spacing.
        
        Args:
            grid_size: [width, height] of the grid in cells
            num_houses: Number of houses to place
            house_spacing: Minimum distance between houses
            world_width: Total world width in pixels
            world_height: Total world height in pixels
            
        Returns:
            List of (x, y) positions for houses
        """
        positions = []
        grid_width, grid_height = grid_size
        cell_width = world_width / grid_width
        cell_height = world_height / grid_height
        
        # Convert spacing to grid cells
        spacing_cells = max(1, int(house_spacing / min(cell_width, cell_height)))
        
        # Create grid of available positions
        available_positions = []
        for x in range(grid_width):
            for y in range(grid_height):
                # Convert grid position to world position (center of cell)
                world_x = (x + 0.5) * cell_width
                world_y = (y + 0.5) * cell_height
                available_positions.append((world_x, world_y))
        
        # Place houses with spacing constraints
        attempts = 0
        max_attempts = num_houses * 100  # Prevent infinite loops
        
        while len(positions) < num_houses and attempts < max_attempts:
            attempts += 1
            
            # Pick a random available position
            if not available_positions:
                break
                
            pos = random.choice(available_positions)
            x, y = pos
            
            # Check if this position is far enough from existing houses
            valid_position = True
            for existing_x, existing_y in positions:
                distance = ((x - existing_x) ** 2 + (y - existing_y) ** 2) ** 0.5
                if distance < house_spacing:
                    valid_position = False
                    break
            
            if valid_position:
                positions.append((x, y))
                # Remove nearby positions to maintain spacing
                available_positions = [
                    (px, py) for px, py in available_positions
                    if ((px - x) ** 2 + (py - y) ** 2) ** 0.5 >= house_spacing
                ]
        
        if len(positions) < num_houses:
            print(f"Warning: Only placed {len(positions)} houses out of {num_houses} requested")
        
        return positions
    
    def _assign_house_quality(self, quality_distribution: List[float]) -> int:
        """
        Assign a quality level to a house based on distribution.
        
        Args:
            quality_distribution: [low_prob, mid_prob, high_prob] probabilities
            
        Returns:
            Quality level (1, 2, or 3)
        """
        rand = random.random()
        cumulative = 0.0
        
        for i, prob in enumerate(quality_distribution):
            cumulative += prob
            if rand <= cumulative:
                return i + 1
        
        # Fallback to middle quality
        return 2
    
    def get_layout_names(self) -> List[str]:
        """Get list of available layout names."""
        return list(self.layouts.keys())
    
    def get_layout_info(self, layout_name: str) -> Dict[str, Any]:
        """Get information about a specific layout."""
        if layout_name in self.layouts:
            return self.layouts[layout_name].copy()
        return {}
    
    def create_custom_layout(
        self, 
        name: str, 
        grid_size: List[int], 
        num_houses: int, 
        house_spacing: float,
        quality_distribution: List[float],
        world_width: int = 2000,
        world_height: int = 2000
    ) -> None:
        """
        Create a custom layout and add it to available layouts.
        
        Args:
            name: Name for the new layout
            grid_size: [width, height] of the grid
            num_houses: Number of houses to place
            house_spacing: Minimum distance between houses
            quality_distribution: [low_prob, mid_prob, high_prob]
            world_width: Total world width
            world_height: Total world height
        """
        self.layouts[name] = {
            "grid_size": grid_size,
            "num_houses": num_houses,
            "house_spacing": house_spacing,
            "quality_distribution": quality_distribution,
            "world_width": world_width,
            "world_height": world_height
        }
    
    def save_layouts(self, file_path: str = "config/neighborhood_layouts.json"):
        """Save current layouts to JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.layouts, f, indent=2)
            print(f"Layouts saved to {file_path}")
        except Exception as e:
            print(f"Error saving layouts: {e}")


# Global map generator instance
map_generator = MapGenerator()
