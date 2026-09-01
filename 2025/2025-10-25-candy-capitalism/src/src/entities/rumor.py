"""
Rumor entity class.

Represents rumors that can be spread among kids to influence their beliefs
and trading behavior.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from ..utils.vector2 import Vector2


class RumorType(Enum):
    """Types of rumors that can be spread."""
    PRICE = 0  # "Snickers are going to be worth 3x tomorrow!"
    QUALITY = 1  # "All Skittles from Oak Street are stale!"
    PERSON = 2  # "Jimmy is a scammer, don't trade with him!"
    SUPPLY = 3  # "Mrs. Henderson is giving out king-size bars!"
    EVENT = 4  # "There's a candy recall coming!"


class Rumor:
    """
    Represents a rumor that can spread through the kid social network.
    
    Rumors affect kids' beliefs about candy values, quality, and other
    market information, creating opportunities for manipulation.
    """
    
    def __init__(self, rumor_id: str, rumor_type: RumorType, content: str, 
                 origin_kid_id: str, believability: float = 0.5):
        """
        Initialize a rumor.
        
        Args:
            rumor_id: Unique identifier for this rumor
            rumor_type: Type of rumor
            content: Text content of the rumor
            origin_kid_id: ID of kid who started the rumor
            believability: How believable the rumor is (0.0 to 1.0)
        """
        self.id = rumor_id
        self.type = rumor_type
        self.content = content
        self.origin_kid_id = origin_kid_id
        
        # Rumor properties
        self.believability = believability
        self.age = 0.0  # Age in seconds
        self.max_age = 60.0  # Maximum age before decay
        self.spread_radius = 100.0  # Physical spread radius
        self.max_depth = 3  # Maximum social network depth
        
        # Spread tracking
        self.spread_count = 0
        self.affected_kids: List[str] = []  # Kids who have heard this rumor
        self.mutations = 0  # Number of times rumor has mutated
        
        # Effect properties
        self.effect_strength = 1.0  # How strong the rumor's effect is
        self.target_candy_type: Optional[str] = None
        self.value_modifier = 1.0  # Multiplier for candy values
        
    def update(self, dt: float):
        """
        Update rumor state.
        
        Args:
            dt: Delta time in seconds
        """
        self.age += dt
        
        # Check if rumor should decay
        if self.age >= self.max_age:
            self._decay()
    
    def _decay(self):
        """Apply decay effects to the rumor."""
        # Reduce believability over time
        decay_factor = self.age / self.max_age
        self.believability *= (1.0 - decay_factor * 0.5)
        
        # Reduce effect strength
        self.effect_strength *= (1.0 - decay_factor * 0.3)
    
    def is_expired(self) -> bool:
        """Check if rumor has expired."""
        return self.age >= self.max_age or self.believability <= 0.1
    
    def can_spread_to(self, kid_id: str) -> bool:
        """
        Check if rumor can spread to a specific kid.
        
        Args:
            kid_id: ID of the kid
            
        Returns:
            True if rumor can spread to this kid
        """
        # Don't spread to kids who already heard it
        if kid_id in self.affected_kids:
            return False
        
        # Don't spread to origin kid
        if kid_id == self.origin_kid_id:
            return False
        
        return True
    
    def spread_to(self, kid_id: str, mutation_chance: float = 0.1):
        """
        Spread rumor to a kid.
        
        Args:
            kid_id: ID of the kid
            mutation_chance: Chance for rumor to mutate
        """
        if not self.can_spread_to(kid_id):
            return
        
        self.affected_kids.append(kid_id)
        self.spread_count += 1
        
        # Chance for mutation
        import random
        if random.random() < mutation_chance:
            self._mutate()
    
    def _mutate(self):
        """Mutate the rumor as it spreads (like telephone game)."""
        self.mutations += 1
        
        # Slightly change believability
        import random
        change = random.uniform(-0.1, 0.1)
        self.believability = max(0.0, min(1.0, self.believability + change))
        
        # Slightly change effect strength
        change = random.uniform(-0.1, 0.1)
        self.effect_strength = max(0.1, min(2.0, self.effect_strength + change))
        
        # Sometimes change the content slightly
        if random.random() < 0.3:
            self._mutate_content()
    
    def _mutate_content(self):
        """Mutate the rumor content."""
        # Simple content mutation - in a real game, this could be more sophisticated
        mutations = [
            "I heard that " + self.content.lower(),
            "Someone told me " + self.content.lower(),
            "I think " + self.content.lower(),
            self.content + " (I'm not sure though)",
        ]
        
        import random
        self.content = random.choice(mutations)
    
    def get_effect_on_candy_value(self, candy_type: str) -> float:
        """
        Get the effect this rumor has on a candy type's perceived value.
        
        Args:
            candy_type: Type of candy
            
        Returns:
            Multiplier for the candy's perceived value
        """
        if self.type != RumorType.PRICE:
            return 1.0
        
        if self.target_candy_type and candy_type != self.target_candy_type:
            return 1.0
        
        # Apply rumor effect
        effect = self.value_modifier * self.effect_strength * self.believability
        return max(0.1, min(5.0, effect))  # Clamp to reasonable range
    
    def get_effect_on_quality(self, candy_type: str) -> float:
        """
        Get the effect this rumor has on a candy type's perceived quality.
        
        Args:
            candy_type: Type of candy
            
        Returns:
            Multiplier for the candy's perceived quality
        """
        if self.type != RumorType.QUALITY:
            return 1.0
        
        if self.target_candy_type and candy_type != self.target_candy_type:
            return 1.0
        
        # Apply rumor effect
        effect = self.effect_strength * self.believability
        return max(0.1, min(2.0, effect))  # Clamp to reasonable range
    
    def get_trust_effect(self, kid_id: str) -> float:
        """
        Get the effect this rumor has on trust in a specific kid.
        
        Args:
            kid_id: ID of the kid
            
        Returns:
            Trust modifier (-1.0 to 1.0)
        """
        if self.type != RumorType.PERSON:
            return 0.0
        
        # This would need to be more sophisticated in a real implementation
        # For now, just return a simple effect
        return -0.3 * self.effect_strength * self.believability
    
    def get_spread_info(self) -> Dict[str, Any]:
        """Get information about how the rumor has spread."""
        return {
            'spread_count': self.spread_count,
            'affected_kids': len(self.affected_kids),
            'mutations': self.mutations,
            'age': self.age,
            'believability': self.believability,
            'effect_strength': self.effect_strength
        }
    
    def __repr__(self) -> str:
        """String representation of rumor."""
        return f"Rumor(id={self.id}, type={self.type.name}, content='{self.content[:30]}...')"
