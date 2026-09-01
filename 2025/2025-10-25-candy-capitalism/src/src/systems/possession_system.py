"""
Possession system for player control of kids.

Manages chaos energy, possession mechanics, and player actions
while controlling possessed kids.
"""

from typing import Optional, Dict, Any
from ..entities.kid import Kid
from ..utils.vector2 import Vector2


class PossessionSystem:
    """
    Manages player possession of kids and chaos energy.
    
    Handles the core mechanic of taking control of kids to manipulate
    the candy economy through direct action.
    """
    
    def __init__(self, max_energy: float = 100.0, regen_rate: float = 1.0):
        """
        Initialize possession system.
        
        Args:
            max_energy: Maximum chaos energy
            regen_rate: Energy regeneration per second
        """
        self.max_energy = max_energy
        self.current_energy = max_energy
        self.regen_rate = regen_rate
        self.drain_rate = 2.0  # Energy drain per second while possessing
        
        # Possession state
        self.current_target: Optional[Kid] = None
        self.possession_cooldown = 0.0
        self.cooldown_duration = 1.0  # Seconds between possessions (reduced for better UX)
        
        # Player actions
        self.available_actions = [
            'move', 'trade', 'refuse_trade', 'borrow', 'hoard'
        ]
        
    def update(self, dt: float):
        """
        Update possession system.
        
        Args:
            dt: Delta time in seconds
        """
        # Update cooldown
        if self.possession_cooldown > 0:
            self.possession_cooldown -= dt
        
        # Regenerate energy
        if self.current_energy < self.max_energy:
            self.current_energy = min(self.max_energy, 
                                    self.current_energy + self.regen_rate * dt)
        
        # Drain energy while possessing
        if self.current_target:
            self.current_energy = max(0, 
                                    self.current_energy - self.drain_rate * dt)
            
            # Auto-release if out of energy
            if self.current_energy <= 0:
                self.release()
    
    def can_possess(self) -> bool:
        """Check if player can possess a kid."""
        return (self.possession_cooldown <= 0 and 
                self.current_energy > 10.0)  # Need some energy to start
    
    def possess(self, kid: Kid) -> bool:
        """
        Possess a kid.
        
        Args:
            kid: Kid to possess
            
        Returns:
            True if successful, False otherwise
        """
        if not self.can_possess():
            return False
        
        if not kid.active:
            return False
        
        self.current_target = kid
        self.possession_cooldown = self.cooldown_duration
        return True
    
    def release(self):
        """Release current possession."""
        if self.current_target:
            print(f"Releasing possession of {self.current_target.id}")
            self.current_target = None
            self.possession_cooldown = self.cooldown_duration
            print("✓ Possession released successfully")
        else:
            print("No target to release")
    
    def is_possessing(self) -> bool:
        """Check if currently possessing a kid."""
        return self.current_target is not None
    
    def get_possessed_kid(self) -> Optional[Kid]:
        """Get currently possessed kid."""
        return self.current_target
    
    def move_possessed(self, direction: Vector2, speed: float = 50.0):
        """
        Move the possessed kid.
        
        Args:
            direction: Direction to move (normalized)
            speed: Movement speed
        """
        if not self.current_target:
            return
        
        self.current_target.velocity = direction * speed
    
    def stop_possessed(self):
        """Stop the possessed kid from moving."""
        if self.current_target:
            self.current_target.velocity = Vector2(0, 0)
    
    def force_trade(self, other_kid: Kid, offer: Dict[str, int], 
                   request: Dict[str, int]) -> bool:
        """
        Force a trade while possessing a kid.
        
        Args:
            other_kid: Kid to trade with
            offer: What to offer
            request: What to request
            
        Returns:
            True if trade was successful
        """
        if not self.current_target:
            return False
        
        # This would integrate with the trading system
        # For now, just a placeholder
        return True
    
    def refuse_trade(self, other_kid: Kid):
        """
        Refuse a trade while possessing a kid.
        
        Args:
            other_kid: Kid whose trade to refuse
        """
        if not self.current_target:
            return
        
        # This would integrate with the trading system
        # For now, just a placeholder
        pass
    
    def borrow_candy(self, other_kid: Kid, candy_type: str, quantity: int) -> bool:
        """
        Borrow candy from another kid.
        
        Args:
            other_kid: Kid to borrow from
            candy_type: Type of candy to borrow
            quantity: Amount to borrow
            
        Returns:
            True if successful
        """
        if not self.current_target:
            return False
        
        # This would integrate with the debt system
        # For now, just a placeholder
        return True
    
    def hoard_candy(self, candy_type: str, quantity: int):
        """
        Hoard specific candy type.
        
        Args:
            candy_type: Type of candy to hoard
            quantity: Amount to hoard
        """
        if not self.current_target:
            return
        
        # This would affect the kid's trading behavior
        # For now, just a placeholder
        pass
    
    def get_energy_percentage(self) -> float:
        """Get current energy as percentage."""
        return self.current_energy / self.max_energy
    
    def add_energy(self, amount: float):
        """Add energy (from combos, etc.)."""
        self.current_energy = min(self.max_energy, self.current_energy + amount)
    
    def can_use_action(self, action: str) -> bool:
        """
        Check if an action can be used.
        
        Args:
            action: Action to check
            
        Returns:
            True if action can be used
        """
        if not self.is_possessing():
            return False
        
        if action not in self.available_actions:
            return False
        
        # Some actions might have additional requirements
        if action == 'trade' and self.current_energy < 5:
            return False
        
        return True
    
    def get_possession_info(self) -> Dict[str, Any]:
        """Get information about current possession."""
        if not self.current_target:
            return {
                'possessing': False,
                'energy': self.current_energy,
                'energy_percentage': self.get_energy_percentage(),
                'cooldown': self.possession_cooldown
            }
        
        return {
            'possessing': True,
            'kid_id': self.current_target.id,
            'kid_mood': self.current_target.mood.name,
            'kid_inventory': self.current_target.inventory.copy(),
            'energy': self.current_energy,
            'energy_percentage': self.get_energy_percentage(),
            'cooldown': self.possession_cooldown
        }
