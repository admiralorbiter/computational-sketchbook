"""
Kid entity class.

Represents a trick-or-treating child with AI behavior, trading capabilities,
and various personality traits that affect their behavior.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from ..utils.vector2 import Vector2
from .base_entity import BaseEntity


class KidState(Enum):
    """Possible states for a kid."""
    IDLE = 0
    MOVING_TO_HOUSE = 1
    TRICK_OR_TREATING = 2
    SEEKING_TRADE = 3
    IN_TRADE = 4
    FLEEING = 5


class PersonalityType(Enum):
    """Kid personality types that affect trading behavior."""
    VALUE_INVESTOR = 0
    MOMENTUM_TRADER = 1
    HOARDER = 2
    SOCIAL_TRADER = 3
    PANIC_SELLER = 4


class Mood(Enum):
    """Kid mood states that affect behavior."""
    HAPPY = 0
    NEUTRAL = 1
    ANXIOUS = 2
    GREEDY = 3
    PANIC = 4


class Kid(BaseEntity):
    """
    Represents a trick-or-treating child with AI behavior.
    
    Each kid has personality traits, preferences, and goals that affect
    their trading behavior and movement patterns.
    """
    
    def __init__(self, kid_id: str, position: Vector2 = None):
        """
        Initialize a kid entity.
        
        Args:
            kid_id: Unique identifier for this kid
            position: Initial position
        """
        super().__init__(kid_id, position)
        
        # AI state
        self.state = KidState.IDLE
        self.personality = PersonalityType.VALUE_INVESTOR
        self.mood = Mood.NEUTRAL
        
        # Trading attributes
        self.preferences: Dict[str, float] = {}  # Candy type -> preference (0-1)
        self.believed_values: Dict[str, float] = {}  # Candy type -> believed value
        self.inventory: Dict[str, int] = {}  # Candy type -> quantity
        self.debts: Dict[str, Dict[str, int]] = {}  # Kid ID -> {Candy type: quantity}
        
        # Social attributes
        self.social_network: List[str] = []  # List of kid IDs
        self.trust_levels: Dict[str, float] = {}  # Kid ID -> trust level (0-1)
        self.trading_bloc = None  # TradingBloc reference
        
        # Personal goal
        self.personal_goal = None  # PersonalGoal reference
        
        # Memory and learning
        self.recent_trades: List[Dict[str, Any]] = []
        self.observed_strategies: Dict[str, float] = {}  # Strategy -> success rate
        
        # Timers
        self.trade_cooldown = 0.0
        self.trick_or_treat_timer = 0.0
        self.ai_tick_timer = 0.0
        
        # Movement
        self.target_position: Optional[Vector2] = None
        self.target_house = None
        self.max_speed = 50.0  # pixels per second
        self.collision_radius = 15.0  # pixels
        
        # Pathfinding
        self.current_path: List[Vector2] = []
        self.path_index = 0
        self.use_pathfinding = True
    
    def initialize_believed_values(self, economy, mode: str = "fixed"):
        """
        Initialize believed values based on price discovery mode.
        
        Args:
            economy: Economy system with real values
            mode: "fixed", "random", or "convergent"
        """
        import random
        
        if mode == "fixed":
            # Kids know the true values
            self.believed_values = economy.real_values.copy()
        elif mode == "random":
            # Kids have random beliefs (0.5 to 5.0 range)
            self.believed_values = {}
            for candy_type in economy.real_values.keys():
                self.believed_values[candy_type] = random.uniform(0.5, 5.0)
        elif mode == "convergent":
            # Start random but will converge through trading
            self.believed_values = {}
            for candy_type in economy.real_values.keys():
                # Start with some variation around real value
                real_value = economy.real_values[candy_type]
                variation = random.uniform(0.5, 1.5)  # 50% to 150% of real value
                self.believed_values[candy_type] = real_value * variation
        else:
            # Default to fixed
            self.believed_values = economy.real_values.copy()
    
    def update_beliefs_from_trade(self, trade_offer: Dict[str, int], trade_request: Dict[str, int], 
                                 economy, learning_rate: float = 0.1):
        """
        Update believed values based on a completed trade.
        
        Args:
            trade_offer: What this kid offered
            trade_request: What this kid requested
            economy: Economy system
            learning_rate: How fast to adjust beliefs (0.0 to 1.0)
        """
        # Calculate the implied price from the trade
        # If we offered 1 CHOCOLATE for 1 FRUITY, implied price of FRUITY = CHOCOLATE_value
        for offered_candy, offered_qty in trade_offer.items():
            for requested_candy, requested_qty in trade_request.items():
                if offered_qty > 0 and requested_qty > 0:
                    # Implied price: 1 requested_candy = (offered_value / requested_qty)
                    offered_value = self.believed_values.get(offered_candy, economy.get_real_value(offered_candy))
                    implied_price = (offered_value * offered_qty) / requested_qty
                    
                    # Update belief toward implied price
                    current_belief = self.believed_values.get(requested_candy, economy.get_real_value(requested_candy))
                    new_belief = current_belief + learning_rate * (implied_price - current_belief)
                    
                    # Keep within reasonable bounds
                    new_belief = max(0.1, min(10.0, new_belief))
                    self.believed_values[requested_candy] = new_belief
        
    def update(self, dt: float, renderer=None):
        """Update kid state and behavior."""
        super().update(dt)
        
        if not self.active:
            return
        
        # Update timers
        self.trade_cooldown = max(0, self.trade_cooldown - dt)
        self.trick_or_treat_timer = max(0, self.trick_or_treat_timer - dt)
        self.ai_tick_timer += dt
        
        # State-based behavior
        self._update_state_behavior(dt, renderer)
    
    def _update_state_behavior(self, dt: float, renderer=None):
        """Update behavior based on current state."""
        if self.state == KidState.MOVING_TO_HOUSE:
            if self.target_position:
                if self._move_with_pathfinding(self.target_position, self.max_speed, dt):
                    self.state = KidState.TRICK_OR_TREATING
                    self.trick_or_treat_timer = 2.0  # Spend 2 seconds trick-or-treating
        elif self.state == KidState.TRICK_OR_TREATING:
            if self.trick_or_treat_timer <= 0:
                # Try to get candy from the house
                if self.target_house:
                    from ..ai.basic_behaviors import BasicBehaviors
                    BasicBehaviors.execute_trick_or_treat(self, self.target_house, renderer)
                self.state = KidState.IDLE
        elif self.state == KidState.SEEKING_TRADE:
            # Movement handled in AI tick
            pass
    
    def ai_tick(self, world):
        """
        Heavy AI logic that runs every 2-3 seconds.
        
        Args:
            world: GameWorld reference for accessing other entities
        """
        if not self.active:
            return
        
        # Use basic behaviors for now
        from ..ai.basic_behaviors import BasicBehaviors
        BasicBehaviors.update_kid_behavior(self, world, 0.0)
        
        # Check debt obligations first
        if self._has_overdue_debt():
            self._seek_debt_repayment(world)
            return
        
        # Goal-driven behavior
        if self.personal_goal and self.personal_goal.is_urgent():
            self._pursue_goal(world)
            return
    
    def _has_overdue_debt(self) -> bool:
        """Check if kid has overdue debt."""
        # Placeholder implementation
        return False
    
    def _seek_debt_repayment(self, world):
        """Seek to repay overdue debt."""
        # Placeholder implementation
        pass
    
    def _pursue_goal(self, world):
        """Pursue personal goal."""
        if not self.personal_goal:
            return
        # Placeholder implementation
        pass
    
    def _pick_new_house(self, world):
        """Pick a new house to visit for trick-or-treating."""
        if not world.houses:
            self.state = KidState.IDLE
            return
        
        # Pick a random house
        import random
        target_house = random.choice(world.houses)
        self.target_house = target_house
        self.target_position = target_house.position
        self.state = KidState.MOVING_TO_HOUSE
    
    def _seek_trade_partner(self, world):
        """Seek a trading partner."""
        # Placeholder implementation
        self.state = KidState.IDLE
    
    def evaluate_trade(self, offer: Dict[str, int], request: Dict[str, int], 
                      economy) -> float:
        """
        Evaluate a trade proposal.
        
        Args:
            offer: What this kid would give
            request: What this kid would receive
            economy: Economy system for real values
            
        Returns:
            Trade score (>0 = accept, <0 = reject)
        """
        # Calculate value of what we'd give vs what we'd receive
        # Using believed values, not real values
        give_value = self._calculate_value(offer, economy)
        receive_value = self._calculate_value(request, economy)
        
        # Base trade score is the difference
        base_score = receive_value - give_value
        
        # Apply personality modifier
        personality_modifier = self._get_personality_threshold()
        
        # Apply mood modifier
        mood_modifier = self._get_mood_modifier()
        
        # Apply preference modifier (we prefer candy we like)
        preference_modifier = self._get_preference_modifier(request, offer)
        
        # Final score combines all modifiers
        final_score = base_score * personality_modifier * mood_modifier + preference_modifier
        
        return final_score
    
    def _calculate_value(self, candy_dict: Dict[str, int], economy) -> float:
        """Calculate value of candy using believed values."""
        total_value = 0.0
        for candy_type, quantity in candy_dict.items():
            # Use believed value if available, otherwise real value
            if candy_type in self.believed_values:
                value = self.believed_values[candy_type]
            else:
                value = economy.get_real_value(candy_type)
            
            total_value += value * quantity
        
        return total_value
    
    def _get_personality_threshold(self) -> float:
        """Get trade threshold based on personality."""
        thresholds = {
            PersonalityType.VALUE_INVESTOR: 1.3,      # Stricter, want good deals
            PersonalityType.MOMENTUM_TRADER: 1.0,     # Average threshold
            PersonalityType.HOARDER: 1.5,             # Very strict, rarely trade
            PersonalityType.SOCIAL_TRADER: 0.7,       # Lenient, trade more freely
            PersonalityType.PANIC_SELLER: 0.5,        # Very lenient, trade anything
        }
        return thresholds.get(self.personality, 1.0)
    
    def _get_mood_modifier(self) -> float:
        """Get trade modifier based on mood."""
        modifiers = {
            Mood.HAPPY: 0.9,      # A bit more generous
            Mood.NEUTRAL: 1.0,    # Normal
            Mood.ANXIOUS: 1.2,    # More cautious, need better deals
            Mood.GREEDY: 1.3,     # Very strict, only good deals
            Mood.PANIC: 0.5,      # Panic selling, accept bad deals
        }
        return modifiers.get(self.mood, 1.0)
    
    def _get_preference_modifier(self, request: Dict[str, int], offer: Dict[str, int]) -> float:
        """Calculate preference-based modifier for the trade."""
        # Bonus for receiving candy we like
        request_bonus = 0.0
        for candy_type, quantity in request.items():
            preference = self.preferences.get(candy_type, 0.5)
            request_bonus += preference * quantity * 0.5
        
        # Penalty for giving away candy we like
        offer_penalty = 0.0
        for candy_type, quantity in offer.items():
            preference = self.preferences.get(candy_type, 0.5)
            offer_penalty += preference * quantity * 0.3
        
        return request_bonus - offer_penalty
    
    def hear_rumor(self, rumor):
        """Process a rumor and update beliefs."""
        # Placeholder implementation
        pass
    
    def observe_trade(self, other_kid, trade_data):
        """Observe another kid's trade and learn from it."""
        # Placeholder implementation
        pass
    
    def add_candy(self, candy_type: str, quantity: int):
        """Add candy to inventory."""
        if candy_type not in self.inventory:
            self.inventory[candy_type] = 0
        self.inventory[candy_type] += quantity
    
    def remove_candy(self, candy_type: str, quantity: int) -> bool:
        """
        Remove candy from inventory.
        
        Returns:
            True if successful, False if not enough candy
        """
        if candy_type not in self.inventory or self.inventory[candy_type] < quantity:
            return False
        self.inventory[candy_type] -= quantity
        return True
    
    def has_candy(self, candy_type: str, quantity: int = 1) -> bool:
        """Check if kid has enough of a candy type."""
        return self.inventory.get(candy_type, 0) >= quantity
    
    def get_total_candy_value(self, real_values: Dict[str, float]) -> float:
        """Calculate total value of kid's candy inventory."""
        total = 0.0
        for candy_type, quantity in self.inventory.items():
            if candy_type in real_values:
                total += real_values[candy_type] * quantity
        return total
    
    def render(self, screen, camera=None):
        """Render the kid."""
        super().render(screen, camera)
        
        if not self.visible or not self.active:
            return
        
        # Placeholder rendering - will be implemented in later sprints
        # For now, just render a colored circle
        import pygame
        
        # Convert world position to screen position
        if camera:
            screen_pos = camera.world_to_screen(self.position)
        else:
            screen_pos = self.position
        
        # Draw kid as a colored circle
        color = self._get_mood_color()
        pygame.draw.circle(screen, color, screen_pos.to_int_tuple(), 10)
    
    def move_toward(self, target: Vector2, speed: float, dt: float) -> bool:
        """
        Move toward a target position.
        
        Args:
            target: Target position to move toward
            speed: Movement speed in units per second
            dt: Delta time in seconds
            
        Returns:
            True if reached target, False otherwise
        """
        if not target:
            return True
        
        # Calculate direction to target
        direction = target - self.position
        distance = direction.length()
        
        # Check if we've reached the target
        arrival_distance = 10.0  # Close enough to consider "arrived"
        if distance <= arrival_distance:
            return True
        
        # Move toward target
        if distance > 0:
            # Normalize direction and apply speed
            move_distance = speed * dt
            if move_distance >= distance:
                # Would overshoot, just go to target
                self.position = target
                return True
            else:
                # Move partway toward target
                self.position += direction.normalize() * move_distance
        
        return False
    
    def _move_with_pathfinding(self, target: Vector2, speed: float, dt: float) -> bool:
        """
        Move toward target using pathfinding.
        
        Args:
            target: Target position to move toward
            speed: Movement speed in units per second
            dt: Delta time in seconds
            
        Returns:
            True if reached target, False otherwise
        """
        if not target:
            return True
        
        # Check if we need to find a new path
        if not self.current_path or self.path_index >= len(self.current_path):
            # Request path from world's pathfinding manager
            # For now, fall back to direct movement if no pathfinding available
            return self.move_toward(target, speed, dt)
        
        # Move along current path
        current_waypoint = self.current_path[self.path_index]
        
        # Check if we've reached the current waypoint
        if self.position.distance_to(current_waypoint) <= 10.0:
            self.path_index += 1
            
            # If we've reached the end of the path, we're at the target
            if self.path_index >= len(self.current_path):
                return True
        
        # Move toward current waypoint
        return self.move_toward(current_waypoint, speed, dt)
    
    def set_path(self, path: List[Vector2]):
        """Set a new path for the kid to follow."""
        self.current_path = path
        self.path_index = 0
    
    def clear_path(self):
        """Clear the current path."""
        self.current_path = []
        self.path_index = 0
    
    def reached_target(self) -> bool:
        """Check if kid has reached their target position."""
        if not self.target_position:
            return True
        
        distance = self.position.distance_to(self.target_position)
        return distance <= 10.0  # Arrival distance
    
    def _get_mood_color(self) -> tuple:
        """Get color based on current mood."""
        mood_colors = {
            Mood.HAPPY: (100, 255, 100),
            Mood.NEUTRAL: (255, 255, 255),
            Mood.ANXIOUS: (255, 255, 100),
            Mood.GREEDY: (255, 100, 255),
            Mood.PANIC: (255, 100, 100)
        }
        return mood_colors.get(self.mood, (255, 255, 255))
    
    def check_collision_with_kids(self, other_kids: List['Kid']) -> List['Kid']:
        """
        Check for collisions with other kids.
        
        Args:
            other_kids: List of other kid entities to check against
            
        Returns:
            List of kids this kid is colliding with
        """
        colliding_kids = []
        
        for other_kid in other_kids:
            if other_kid == self or not other_kid.active:
                continue
            
            distance = self.position.distance_to(other_kid.position)
            min_distance = self.collision_radius + other_kid.collision_radius
            
            if distance < min_distance:
                colliding_kids.append(other_kid)
        
        return colliding_kids
    
    def apply_separation_force(self, colliding_kids: List['Kid'], dt: float):
        """
        Apply separation force to avoid other kids.
        
        Args:
            colliding_kids: List of kids this kid is colliding with
            dt: Delta time
        """
        if not colliding_kids:
            return
        
        separation_force = Vector2(0, 0)
        
        for other_kid in colliding_kids:
            # Calculate direction away from other kid
            direction = self.position - other_kid.position
            distance = direction.length()
            
            if distance > 0:
                # Normalize and scale by separation strength
                direction = direction.normalized()
                separation_strength = 100.0  # Force strength
                force = direction * separation_strength
                separation_force += force
        
        # Apply separation force to movement
        if separation_force.length() > 0:
            # Normalize and apply as movement offset
            separation_force = separation_force.normalized()
            self.position += separation_force * self.max_speed * dt * 0.5
