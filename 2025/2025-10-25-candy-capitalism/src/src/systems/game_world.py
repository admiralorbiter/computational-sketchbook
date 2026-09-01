"""
Game world management system.

Central hub that manages all game entities and coordinates system updates
with tiered update frequencies for optimal performance.
"""

from typing import List, Dict, Any, Optional
from ..entities.kid import Kid
from ..entities.house import House
from ..entities.rumor import Rumor
from ..entities.trading_bloc import TradingBloc
from ..utils.spatial_grid import SpatialGrid
from ..utils.vector2 import Vector2
from .map_generator import map_generator
from .kid_spawner import kid_spawner
from ..ai.pathfinding import PathfindingManager


class GameWorld:
    """
    Central hub that manages all game entities and systems.
    
    Coordinates updates between different systems and manages the
    spatial partitioning for efficient neighbor queries.
    """
    
    def __init__(self):
        """Initialize the game world."""
        # Entity collections
        self.kids: List[Kid] = []
        self.houses: List[House] = []
        self.trading_blocs: List[TradingBloc] = []
        
        # Systems
        from .economy import Economy
        from .possession_system import PossessionSystem
        self.economy = Economy()  # Initialize economy system
        self.possession_system = PossessionSystem()  # Initialize possession system
        self.rumor_system = None  # Rumor system
        self.event_system = None  # Event system
        self.combo_detector = None  # Combo detection system
        
        # Spatial partitioning for optimization
        self.spatial_grid = SpatialGrid(cell_size=100)
        
        # Timing
        self.game_time = 0.0
        self.ai_tick_timer = 0.0
        self.ai_tick_rate = 2.0  # AI updates every 2 seconds
        
        # World state
        self.active = True
        self.paused = False
        
        # Map generation
        self.map_generated = False
        
        # Pathfinding
        self.pathfinding_manager = None
        
    def update(self, dt: float, renderer=None):
        """
        Update the game world.
        
        Args:
            dt: Delta time in seconds
            renderer: Optional renderer for particle effects
        """
        if not self.active or self.paused:
            return
        
        self.game_time += dt
        
        # Update spatial grid
        self._update_spatial_grid()
        
        # AI tick (not every frame for performance)
        self.ai_tick_timer += dt
        if self.ai_tick_timer >= self.ai_tick_rate:
            self.ai_tick_timer = 0.0
            self._update_ai()
        
        # Update entities (movement, animations)
        self._update_entities(dt, renderer)
        
        # Update systems
        self._update_systems(dt)
        
        # Update trading blocs
        self._update_trading_blocs(dt)
    
    def _update_spatial_grid(self):
        """Update spatial partitioning grid."""
        self.spatial_grid.clear()
        
        # Add kids to spatial grid
        for kid in self.kids:
            if kid.active:
                self.spatial_grid.add(kid, kid.position)
        
        # Add houses to spatial grid
        for house in self.houses:
            if house.active:
                self.spatial_grid.add(house, house.position)
    
    def _update_ai(self):
        """Heavy AI logic runs at reduced rate."""
        for kid in self.kids:
            if kid.active:
                kid.ai_tick(self)
    
    def _update_entities(self, dt: float, renderer=None):
        """Update all entities."""
        # Update kids
        for kid in self.kids:
            kid.update(dt, renderer)
        
        # Update houses
        for house in self.houses:
            house.update(dt)
        
        # Handle kid-kid collision detection and separation
        self._handle_kid_collisions(dt)
    
    def _update_systems(self, dt: float):
        """Update all systems."""
        # These will be implemented in later sprints
        if self.economy:
            self.economy.update(dt)
        
        if self.possession_system:
            self.possession_system.update(dt)
        
        if self.rumor_system:
            self.rumor_system.update(dt)
        
        if self.event_system:
            self.event_system.update(dt, self)
    
    def _update_trading_blocs(self, dt: float):
        """Update trading blocs and check for formation/fracture."""
        # Check for bloc formation (simplified for now)
        self._check_bloc_formation()
        
        # Check for bloc fracture
        for bloc in self.trading_blocs[:]:  # Copy list to avoid modification during iteration
            if bloc.should_fracture():
                self._fracture_bloc(bloc)
    
    def _check_bloc_formation(self):
        """Check if new trading blocs should form."""
        # Simplified implementation - in a real game, this would be more sophisticated
        # For now, just create a placeholder bloc if we have enough kids
        if len(self.kids) >= 3 and len(self.trading_blocs) == 0:
            bloc = TradingBloc(f"bloc_{len(self.trading_blocs)}")
            for i, kid in enumerate(self.kids[:3]):  # Add first 3 kids
                bloc.add_member(kid.id)
            self.trading_blocs.append(bloc)
    
    def _fracture_bloc(self, bloc: TradingBloc):
        """Fracture a trading bloc."""
        remaining_members = bloc.fracture()
        
        if len(remaining_members) < 2:
            # Remove bloc entirely
            self.trading_blocs.remove(bloc)
        else:
            # Update bloc with remaining members
            bloc.members = remaining_members
    
    def add_kid(self, kid: Kid):
        """Add a kid to the world."""
        self.kids.append(kid)
    
    def add_house(self, house: House):
        """Add a house to the world."""
        self.houses.append(house)
    
    def remove_kid(self, kid_id: str):
        """Remove a kid from the world."""
        self.kids = [kid for kid in self.kids if kid.id != kid_id]
    
    def remove_house(self, house_id: str):
        """Remove a house from the world."""
        self.houses = [house for house in self.houses if house.id != house_id]
    
    def get_kid_by_id(self, kid_id: str) -> Optional[Kid]:
        """Get a kid by ID."""
        for kid in self.kids:
            if kid.id == kid_id:
                return kid
        return None
    
    def get_house_by_id(self, house_id: str) -> Optional[House]:
        """Get a house by ID."""
        for house in self.houses:
            if house.id == house_id:
                return house
        return None
    
    def get_nearby_kids(self, position: Vector2, radius: float) -> List[Kid]:
        """Get kids within radius of a position."""
        nearby_entities = self.spatial_grid.get_nearby(position, radius)
        return [entity for entity in nearby_entities if isinstance(entity, Kid)]
    
    def get_nearby_houses(self, position: Vector2, radius: float) -> List[House]:
        """Get houses within radius of a position."""
        nearby_entities = self.spatial_grid.get_nearby(position, radius)
        return [entity for entity in nearby_entities if isinstance(entity, House)]
    
    def get_active_trade_count(self) -> int:
        """Get the number of active trades (placeholder)."""
        # This will be implemented when trading system is added
        return 0
    
    def pause(self):
        """Pause the game world."""
        self.paused = True
    
    def resume(self):
        """Resume the game world."""
        self.paused = False
    
    def reset(self):
        """Reset the game world to initial state."""
        self.kids.clear()
        self.houses.clear()
        self.trading_blocs.clear()
        self.spatial_grid.clear()
        self.game_time = 0.0
        self.ai_tick_timer = 0.0
    
    def generate_map(self, layout_name: str = "default", seed: Optional[int] = None):
        """
        Generate a new map with houses.
        
        Args:
            layout_name: Name of the layout configuration to use
            seed: Random seed for reproducible generation
        """
        if self.map_generated:
            print("Warning: Map already generated, clearing existing houses")
            self.houses.clear()
        
        # Generate houses using map generator
        houses = map_generator.generate_map(layout_name, seed)
        
        # Add houses to world
        for house in houses:
            self.add_house(house)
        
        self.map_generated = True
        
        # Initialize pathfinding manager
        layout_info = map_generator.get_layout_info(layout_name)
        world_width = layout_info.get("world_width", 2000)
        world_height = layout_info.get("world_height", 2000)
        self.pathfinding_manager = PathfindingManager(world_width, world_height)
        
        # Update obstacles with houses
        self.pathfinding_manager.update_obstacles(self.houses)
        
        print(f"Generated map with {len(self.houses)} houses using layout '{layout_name}'")
    
    def spawn_kids(self, count: int = 10):
        """
        Spawn kids in the world.
        
        Args:
            count: Number of kids to spawn
        """
        if not self.map_generated:
            print("Warning: Cannot spawn kids without a map. Generate map first.")
            return
        
        # Get world bounds from map generator
        layout_info = map_generator.get_layout_info("default")
        world_width = layout_info.get("world_width", 2000)
        world_height = layout_info.get("world_height", 2000)
        
        # Spawn kids
        kids = kid_spawner.spawn_kids(self, count, (world_width, world_height))
        print(f"Spawned {len(kids)} kids")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get world statistics."""
        return {
            'kids': len(self.kids),
            'houses': len(self.houses),
            'trading_blocs': len(self.trading_blocs),
            'game_time': self.game_time,
            'spatial_grid_stats': self.spatial_grid.get_stats(),
            'map_generated': self.map_generated
        }
    
    def _handle_kid_collisions(self, dt: float):
        """Handle collision detection and separation between kids."""
        if len(self.kids) < 2:
            return
        
        # Use spatial grid for efficient collision detection
        for kid in self.kids:
            if not kid.active:
                continue
            
            # Find nearby kids using spatial grid
            search_radius = kid.collision_radius * 3
            top_left = Vector2(kid.position.x - search_radius, kid.position.y - search_radius)
            bottom_right = Vector2(kid.position.x + search_radius, kid.position.y + search_radius)
            nearby_kids = self.spatial_grid.get_entities_in_rect(top_left, bottom_right)
            
            # Filter to only other kids
            other_kids = [entity for entity in nearby_kids 
                         if isinstance(entity, type(kid)) and entity != kid and entity.active]
            
            # Check for collisions
            colliding_kids = kid.check_collision_with_kids(other_kids)
            
            # Apply separation force
            if colliding_kids:
                kid.apply_separation_force(colliding_kids, dt)
    
    def try_possess_kid(self, kid: Kid) -> bool:
        """
        Attempt to possess a kid.
        
        Args:
            kid: Kid to possess
            
        Returns:
            True if successful, False otherwise
        """
        if not self.possession_system:
            return False
        
        return self.possession_system.possess(kid)
    
    def release_possession(self):
        """Release current possession."""
        if self.possession_system:
            self.possession_system.release()
    
    def move_possessed_kid(self, direction: Vector2):
        """
        Move the currently possessed kid.
        
        Args:
            direction: Direction to move (normalized)
        """
        if self.possession_system and self.possession_system.is_possessing():
            self.possession_system.move_possessed(direction)
    
    def stop_possessed_kid(self):
        """Stop the currently possessed kid from moving."""
        if self.possession_system and self.possession_system.is_possessing():
            self.possession_system.stop_possessed()
    
    def try_curse_house(self, house: House) -> bool:
        """
        Attempt to curse a house.
        
        Args:
            house: House to curse
            
        Returns:
            True if successful, False otherwise
        """
        if not self.possession_system:
            return False
        
        # Check if we have enough energy
        curse_cost = 15  # From config
        if self.possession_system.current_energy < curse_cost:
            return False
        
        # Apply curse
        house.curse()
        
        # Deduct energy
        self.possession_system.current_energy -= curse_cost
        
        return True
    
    def try_bless_house(self, house: House) -> bool:
        """
        Attempt to bless a house.
        
        Args:
            house: House to bless
            
        Returns:
            True if successful, False otherwise
        """
        if not self.possession_system:
            return False
        
        # Check if we have enough energy
        bless_cost = 25  # From config
        if self.possession_system.current_energy < bless_cost:
            return False
        
        # Apply blessing
        house.bless()
        
        # Deduct energy
        self.possession_system.current_energy -= bless_cost
        
        return True
    
    def get_entity_at_position(self, position: Vector2) -> Optional[Any]:
        """
        Get the topmost entity at a given position.
        
        Args:
            position: World position to check
            
        Returns:
            Entity at position, or None if none found
        """
        # Check kids first (they're on top)
        for kid in self.kids:
            if not kid.active:
                continue
            
            # Simple distance check (assuming kids are ~20 pixels radius)
            if kid.position.distance_to(position) <= 20:
                return kid
        
        # Check houses
        for house in self.houses:
            if not house.active:
                continue
            
            # Simple distance check (assuming houses are ~40 pixels radius)
            if house.position.distance_to(position) <= 40:
                return house
        
        return None
