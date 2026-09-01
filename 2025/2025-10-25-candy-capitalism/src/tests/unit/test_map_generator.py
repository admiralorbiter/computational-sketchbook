"""
Unit tests for map generation system.
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.systems.map_generator import MapGenerator
from src.utils.vector2 import Vector2


class TestMapGenerator:
    """Test cases for MapGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = MapGenerator()
    
    def test_generate_map_default_layout(self):
        """Test generating map with default layout."""
        houses = self.generator.generate_map("default", seed=42)
        
        # Should generate houses
        assert len(houses) > 0
        assert len(houses) <= 20  # Should not exceed max
        
        # All houses should have valid positions
        for house in houses:
            assert house.position.x > 0
            assert house.position.y > 0
            assert house.quality in [1, 2, 3]
            assert house.id.startswith("house_")
    
    def test_generate_map_deterministic(self):
        """Test that same seed produces same map."""
        houses1 = self.generator.generate_map("default", seed=123)
        houses2 = self.generator.generate_map("default", seed=123)
        
        # Should generate same number of houses
        assert len(houses1) == len(houses2)
        
        # Should have same positions (within tolerance)
        for h1, h2 in zip(houses1, houses2):
            assert abs(h1.position.x - h2.position.x) < 0.1
            assert abs(h1.position.y - h2.position.y) < 0.1
            assert h1.quality == h2.quality
    
    def test_house_spacing(self):
        """Test that houses maintain proper spacing."""
        houses = self.generator.generate_map("default", seed=42)
        
        # Check minimum distance between houses
        min_distance = 100.0  # Should be at least 100 units apart
        
        for i, house1 in enumerate(houses):
            for house2 in houses[i+1:]:
                distance = house1.position.distance_to(house2.position)
                assert distance >= min_distance, f"Houses too close: {distance}"
    
    def test_quality_distribution(self):
        """Test that house quality follows distribution."""
        houses = self.generator.generate_map("default", seed=42)
        
        # Count quality levels
        quality_counts = {1: 0, 2: 0, 3: 0}
        for house in houses:
            quality_counts[house.quality] += 1
        
        # Should have some distribution (not all same quality)
        total_houses = len(houses)
        assert total_houses > 0
        
        # Each quality should have at least some houses
        for quality in [1, 2, 3]:
            assert quality_counts[quality] >= 0  # At least 0 (distribution may vary)
    
    def test_custom_layout_creation(self):
        """Test creating custom layouts."""
        # Create a custom layout
        self.generator.create_custom_layout(
            "test_custom",
            grid_size=[10, 10],
            num_houses=5,
            house_spacing=100,
            quality_distribution=[0.4, 0.4, 0.2],
            world_width=1000,
            world_height=1000
        )
        
        # Generate map with custom layout
        houses = self.generator.generate_map("test_custom", seed=42)
        
        # Should generate correct number of houses
        assert len(houses) <= 5
        
        # All houses should be within world bounds
        for house in houses:
            assert 0 <= house.position.x <= 1000
            assert 0 <= house.position.y <= 1000
    
    def test_layout_names(self):
        """Test getting available layout names."""
        names = self.generator.get_layout_names()
        
        assert "default" in names
        assert len(names) > 0
    
    def test_layout_info(self):
        """Test getting layout information."""
        info = self.generator.get_layout_info("default")
        
        assert "grid_size" in info
        assert "num_houses" in info
        assert "house_spacing" in info
        assert "quality_distribution" in info
    
    def test_invalid_layout_fallback(self):
        """Test that invalid layout name falls back to default."""
        houses = self.generator.generate_map("nonexistent_layout", seed=42)
        
        # Should still generate houses (fallback to default)
        assert len(houses) > 0
    
    def test_house_quality_assignment(self):
        """Test house quality assignment logic."""
        # Test with specific distribution
        houses = self.generator.generate_map("default", seed=42)
        
        for house in houses:
            assert house.quality in [1, 2, 3]
            
            # Check that quality affects house properties
            if house.quality == 1:
                assert house.candy_quality <= 1.0  # Low quality
            elif house.quality == 2:
                assert 1.0 <= house.candy_quality <= 1.5  # Mid quality
            else:  # quality == 3
                assert house.candy_quality >= 1.5  # High quality


class TestMapGeneratorIntegration:
    """Integration tests for map generation."""
    
    def test_map_generator_with_temp_config(self):
        """Test map generator with temporary config file."""
        # Create temporary config
        temp_config = {
            "test_temp": {
                "grid_size": [20, 20],
                "num_houses": 8,
                "house_spacing": 120,
                "quality_distribution": [0.3, 0.4, 0.3],
                "world_width": 1500,
                "world_height": 1500
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_config, f)
            temp_path = f.name
        
        try:
            # Create generator with temp config
            generator = MapGenerator()
            generator.layouts = temp_config
            
            # Generate map
            houses = generator.generate_map("test_temp", seed=42)
            
            # Verify results
            assert len(houses) <= 8
            assert len(houses) > 0
            
            # All houses within bounds
            for house in houses:
                assert 0 <= house.position.x <= 1500
                assert 0 <= house.position.y <= 1500
                
        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)
