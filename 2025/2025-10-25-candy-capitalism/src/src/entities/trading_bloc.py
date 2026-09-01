"""
Trading bloc entity class.

Represents groups of kids who form trading alliances, sharing information
and trading preferentially with each other.
"""

from typing import List, Dict, Any, Optional
from ..utils.vector2 import Vector2


class TradingBloc:
    """
    Represents a trading bloc (cartel) of kids who trade preferentially.
    
    Trading blocs form naturally from social networks and provide
    information advantages and better trading rates to members.
    """
    
    def __init__(self, bloc_id: str):
        """
        Initialize a trading bloc.
        
        Args:
            bloc_id: Unique identifier for this bloc
        """
        self.id = bloc_id
        self.members: List[str] = []  # List of kid IDs
        self.shared_beliefs: Dict[str, float] = {}  # Candy type -> believed value
        self.bloc_strength = 0.0  # Strength of the bloc (0.0 to 1.0)
        self.formation_time = 0.0  # When the bloc was formed
        self.color = (100, 100, 255)  # Visual color for bloc members
        
        # Trading statistics
        self.internal_trades = 0  # Trades between bloc members
        self.external_trades = 0  # Trades with non-members
        self.total_profit = 0.0  # Total profit from bloc trades
        
    def add_member(self, kid_id: str):
        """
        Add a kid to the trading bloc.
        
        Args:
            kid_id: ID of the kid to add
        """
        if kid_id not in self.members:
            self.members.append(kid_id)
            self._update_strength()
    
    def remove_member(self, kid_id: str):
        """
        Remove a kid from the trading bloc.
        
        Args:
            kid_id: ID of the kid to remove
        """
        if kid_id in self.members:
            self.members.remove(kid_id)
            self._update_strength()
    
    def is_member(self, kid_id: str) -> bool:
        """
        Check if a kid is a member of this bloc.
        
        Args:
            kid_id: ID of the kid to check
            
        Returns:
            True if kid is a member
        """
        return kid_id in self.members
    
    def get_member_count(self) -> int:
        """Get the number of members in this bloc."""
        return len(self.members)
    
    def can_form(self) -> bool:
        """Check if this bloc can be formed (needs 3+ members)."""
        return len(self.members) >= 3
    
    def _update_strength(self):
        """Update bloc strength based on member count and trading activity."""
        # Base strength from member count
        member_strength = min(1.0, len(self.members) / 10.0)
        
        # Trading activity bonus
        total_trades = self.internal_trades + self.external_trades
        if total_trades > 0:
            internal_ratio = self.internal_trades / total_trades
            trading_bonus = internal_ratio * 0.3  # Up to 30% bonus
        else:
            trading_bonus = 0.0
        
        self.bloc_strength = min(1.0, member_strength + trading_bonus)
    
    def update_shared_beliefs(self, new_beliefs: Dict[str, float], kid_id: str):
        """
        Update shared beliefs based on a member's new information.
        
        Args:
            new_beliefs: New belief values from a member
            kid_id: ID of the kid providing the information
        """
        if not self.is_member(kid_id):
            return
        
        # Update shared beliefs (weighted average with existing beliefs)
        for candy_type, value in new_beliefs.items():
            if candy_type in self.shared_beliefs:
                # Weighted average: 70% existing, 30% new
                self.shared_beliefs[candy_type] = (
                    self.shared_beliefs[candy_type] * 0.7 + value * 0.3
                )
            else:
                self.shared_beliefs[candy_type] = value
    
    def get_shared_belief(self, candy_type: str) -> Optional[float]:
        """
        Get the bloc's shared belief about a candy type.
        
        Args:
            candy_type: Type of candy
            
        Returns:
            Shared belief value, or None if not known
        """
        return self.shared_beliefs.get(candy_type)
    
    def record_trade(self, kid_a_id: str, kid_b_id: str, profit: float):
        """
        Record a trade between bloc members.
        
        Args:
            kid_a_id: ID of first kid
            kid_b_id: ID of second kid
            profit: Profit from the trade
        """
        if self.is_member(kid_a_id) and self.is_member(kid_b_id):
            self.internal_trades += 1
            self.total_profit += profit
        else:
            self.external_trades += 1
        
        self._update_strength()
    
    def get_trading_bonus(self) -> float:
        """
        Get the trading bonus for bloc members.
        
        Returns:
            Multiplier for trading benefits (1.0 to 1.5)
        """
        # Bloc members get better trading rates
        return 1.0 + (self.bloc_strength * 0.5)
    
    def get_information_advantage(self) -> float:
        """
        Get the information advantage for bloc members.
        
        Returns:
            Multiplier for information sharing speed (1.0 to 2.0)
        """
        # Bloc members share information faster
        return 1.0 + (self.bloc_strength * 1.0)
    
    def should_fracture(self) -> bool:
        """
        Check if the bloc should fracture due to low activity or betrayals.
        
        Returns:
            True if bloc should fracture
        """
        # Fracture if too few members
        if len(self.members) < 2:
            return True
        
        # Fracture if too many external trades (members trading outside bloc)
        total_trades = self.internal_trades + self.external_trades
        if total_trades > 0:
            external_ratio = self.external_trades / total_trades
            if external_ratio > 0.7:  # More than 70% external trades
                return True
        
        return False
    
    def fracture(self) -> List[str]:
        """
        Fracture the bloc and return list of remaining members.
        
        Returns:
            List of kid IDs who remain in the bloc
        """
        # Keep the most active members (simplified logic)
        keep_count = max(1, len(self.members) // 2)
        remaining_members = self.members[:keep_count]
        
        # Reset statistics
        self.internal_trades = 0
        self.external_trades = 0
        self.total_profit = 0.0
        self._update_strength()
        
        return remaining_members
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the trading bloc."""
        return {
            'id': self.id,
            'member_count': len(self.members),
            'strength': self.bloc_strength,
            'internal_trades': self.internal_trades,
            'external_trades': self.external_trades,
            'total_profit': self.total_profit,
            'formation_time': self.formation_time
        }
    
    def __repr__(self) -> str:
        """String representation of trading bloc."""
        return f"TradingBloc(id={self.id}, members={len(self.members)}, strength={self.bloc_strength:.2f})"
