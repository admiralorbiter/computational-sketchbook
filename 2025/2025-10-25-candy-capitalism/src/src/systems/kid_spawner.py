"""
Kid spawning system.

Handles spawning kids at game start and managing their initial properties.
"""

import random
from typing import List, Dict, Any
from ..entities.kid import Kid, PersonalityType, Mood
from ..utils.vector2 import Vector2
from ..core.config_manager import config_manager


class KidSpawner:
    """
    Manages kid spawning and initial property assignment.
    
    Spawns kids with random positions, personalities, and initial candy.
    """
    
    def __init__(self):
        """Initialize the kid spawner."""
        self.spawned_count = 0
        self.kid_colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
            (255, 200, 100),  # Orange
            (200, 100, 255),  # Purple
            (100, 200, 100),  # Dark Green
            (200, 200, 200),  # Light Gray
        ]
    
    def spawn_kids(self, world, count: int = 10, world_bounds: tuple = (2000, 2000)) -> List[Kid]:
        """
        Spawn kids in the world.
        
        Args:
            world: GameWorld instance
            count: Number of kids to spawn
            world_bounds: (width, height) of the world
            
        Returns:
            List of spawned Kid entities
        """
        kids = []
        world_width, world_height = world_bounds
        
        for i in range(count):
            # Generate spawn position (avoid houses)
            position = self._find_valid_spawn_position(world, world_width, world_height)
            
            # Create kid
            kid_id = f"kid_{self.spawned_count:02d}"
            kid = Kid(kid_id, position)
            
            # Assign random properties
            self._assign_random_properties(kid, i, world)
            
            # Add to world
            world.add_kid(kid)
            kids.append(kid)
            self.spawned_count += 1
        
        print(f"Spawned {len(kids)} kids")
        return kids
    
    def _find_valid_spawn_position(self, world, world_width: int, world_height: int, max_attempts: int = 50) -> Vector2:
        """
        Find a valid spawn position that doesn't overlap with houses.
        
        Args:
            world: GameWorld instance
            world_width: World width
            world_height: World height
            max_attempts: Maximum attempts to find valid position
            
        Returns:
            Valid spawn position
        """
        min_distance_from_house = 80.0  # Minimum distance from any house
        
        for attempt in range(max_attempts):
            # Generate random position
            x = random.uniform(50, world_width - 50)
            y = random.uniform(50, world_height - 50)
            position = Vector2(x, y)
            
            # Check distance from all houses
            valid_position = True
            for house in world.houses:
                distance = position.distance_to(house.position)
                if distance < min_distance_from_house:
                    valid_position = False
                    break
            
            if valid_position:
                return position
        
        # Fallback: spawn at world center if no valid position found
        print("Warning: Could not find valid spawn position, using world center")
        return Vector2(world_width // 2, world_height // 2)
    
    def _assign_random_properties(self, kid: Kid, index: int, world=None):
        """
        Assign random properties to a kid.
        
        Args:
            kid: Kid entity to assign properties to
            index: Index of the kid (for consistent color assignment)
            world: GameWorld instance (for economy access)
        """
        # Assign personality
        personalities = list(PersonalityType)
        kid.personality = random.choice(personalities)
        
        # Assign mood
        moods = list(Mood)
        kid.mood = random.choice(moods)
        
        # Assign color (cycle through available colors)
        kid.color = self.kid_colors[index % len(self.kid_colors)]
        
        # Initialize preferences (random values 0-1 for each candy type)
        # Use uppercase to match config file
        candy_types = ["CHOCOLATE", "FRUITY", "SOUR", "NOVELTY", "HEALTH", "TRASH"]
        kid.preferences = {candy: random.uniform(0.0, 1.0) for candy in candy_types}
        
        # Initialize believed values based on economy settings
        if world and world.economy and hasattr(kid, 'initialize_believed_values'):
            # Get price discovery mode from economy settings
            mode = world.economy.settings.get('price_discovery_mode', 'fixed')
            kid.initialize_believed_values(world.economy, mode)
        else:
            # Fallback: random values
            kid.believed_values = {candy: random.uniform(0.5, 5.0) for candy in candy_types}
        
        # Give some initial candy
        self._give_initial_candy(kid)
        
        # Set movement speed based on personality
        kid.max_speed = self._get_personality_speed(kid.personality)
    
    def _give_initial_candy(self, kid: Kid):
        """Give kid some initial candy based on their preferences."""
        # Use uppercase to match config file
        candy_types = ["CHOCOLATE", "FRUITY", "SOUR", "NOVELTY", "HEALTH", "TRASH"]
        
        # Give 2-5 pieces of random candy
        num_pieces = random.randint(2, 5)
        for _ in range(num_pieces):
            # Weight selection by preferences
            weights = [kid.preferences.get(candy, 0.5) for candy in candy_types]
            candy_type = random.choices(candy_types, weights=weights)[0]
            kid.add_candy(candy_type, 1)
    
    def _get_personality_speed(self, personality: PersonalityType) -> float:
        """Get movement speed based on personality."""
        speed_multipliers = {
            PersonalityType.VALUE_INVESTOR: 0.8,    # Patient, slower
            PersonalityType.MOMENTUM_TRADER: 1.2,   # Energetic, faster
            PersonalityType.HOARDER: 0.6,           # Cautious, slowest
            PersonalityType.SOCIAL_TRADER: 1.0,     # Average speed
            PersonalityType.PANIC_SELLER: 1.4,      # Anxious, fastest
        }
        
        base_speed = 50.0  # Base speed from config
        multiplier = speed_multipliers.get(personality, 1.0)
        return base_speed * multiplier
    
    def spawn_kid_at_position(self, world, position: Vector2) -> Kid:
        """
        Spawn a single kid at a specific position.
        
        Args:
            world: GameWorld instance
            position: Position to spawn kid at
            
        Returns:
            Spawned Kid entity
        """
        kid_id = f"kid_{self.spawned_count:02d}"
        kid = Kid(kid_id, position)
        
        # Assign random properties
        self._assign_random_properties(kid, self.spawned_count)
        
        # Add to world
        world.add_kid(kid)
        self.spawned_count += 1
        
        return kid
    
    def get_spawned_count(self) -> int:
        """Get the number of kids spawned so far."""
        return self.spawned_count
    
    def reset(self):
        """Reset the spawner state."""
        self.spawned_count = 0


# Global kid spawner instance
kid_spawner = KidSpawner()
