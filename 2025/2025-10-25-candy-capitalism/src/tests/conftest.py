"""
Pytest configuration and shared fixtures.

Provides common test fixtures and configuration for all test modules.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.entities.kid import Kid, PersonalityType, Mood
from src.entities.house import House
from src.systems.economy import Economy
from src.systems.game_world import GameWorld
from src.utils.vector2 import Vector2


@pytest.fixture
def sample_kid():
    """Create a sample kid for testing."""
    kid = Kid("test_kid_1", Vector2(100, 100))
    kid.personality = PersonalityType.VALUE_INVESTOR
    kid.mood = Mood.NEUTRAL
    kid.inventory = {"CHOCOLATE": 5, "FRUITY": 3}
    kid.believed_values = {"CHOCOLATE": 8.0, "FRUITY": 5.0}
    return kid


@pytest.fixture
def sample_house():
    """Create a sample house for testing."""
    house = House("test_house_1", Vector2(200, 200))
    house.candy_types = ["CHOCOLATE", "FRUITY"]
    house.candy_quality = 1.0
    return house


@pytest.fixture
def sample_economy():
    """Create a sample economy for testing."""
    return Economy()


@pytest.fixture
def sample_world():
    """Create a sample game world for testing."""
    world = GameWorld()
    
    # Add some test kids
    for i in range(3):
        kid = Kid(f"test_kid_{i}", Vector2(i * 100, i * 100))
        world.add_kid(kid)
    
    # Add some test houses
    for i in range(2):
        house = House(f"test_house_{i}", Vector2(i * 150, i * 150))
        world.add_house(house)
    
    return world


@pytest.fixture
def sample_vector():
    """Create a sample vector for testing."""
    return Vector2(10, 20)


@pytest.fixture
def sample_vectors():
    """Create multiple sample vectors for testing."""
    return [
        Vector2(0, 0),
        Vector2(10, 10),
        Vector2(-5, 15),
        Vector2(100, 200)
    ]
