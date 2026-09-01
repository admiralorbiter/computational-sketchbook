"""
Rumor system for spreading misinformation and manipulating beliefs.

Manages rumor propagation through social networks and affects kid
beliefs about candy values and market information.
"""

from typing import List, Dict, Any, Optional
from ..entities.rumor import Rumor, RumorType
from ..entities.kid import Kid
from ..utils.vector2 import Vector2


class RumorSystem:
    """
    Manages rumor creation, propagation, and effects.
    
    Handles the spread of rumors through social networks and their
    impact on kid beliefs and trading behavior.
    """
    
    def __init__(self):
        """Initialize rumor system."""
        self.active_rumors: List[Rumor] = []
        self.rumor_id_counter = 0
        
        # Propagation settings
        self.spread_chance = 0.3  # Base chance for rumor to spread
        self.overhear_chance = 0.1  # Chance to overhear nearby rumors
        self.mutation_chance = 0.15  # Chance for rumor to mutate
        
        # Rumor templates
        self.rumor_templates = {
            RumorType.PRICE: [
                "{candy_type} is going to be worth {multiplier}x tomorrow!",
                "I heard {candy_type} prices are about to {direction}!",
                "Someone told me {candy_type} will be {multiplier}x more valuable!"
            ],
            RumorType.QUALITY: [
                "All {candy_type} from {location} are {quality}!",
                "I heard {candy_type} is {quality} this year!",
                "Someone said {candy_type} tastes {quality} now!"
            ],
            RumorType.PERSON: [
                "{kid_name} is a {description}!",
                "Don't trade with {kid_name}, they're {description}!",
                "I heard {kid_name} {action}!"
            ],
            RumorType.SUPPLY: [
                "{location} is giving out {candy_type}!",
                "I heard {location} has {candy_type}!",
                "Someone told me {location} is giving {candy_type}!"
            ]
        }
    
    def update(self, dt: float):
        """
        Update rumor system.
        
        Args:
            dt: Delta time in seconds
        """
        # Update all active rumors
        for rumor in self.active_rumors[:]:  # Copy list to avoid modification during iteration
            rumor.update(dt)
            
            # Remove expired rumors
            if rumor.is_expired():
                self.active_rumors.remove(rumor)
    
    def create_rumor(self, rumor_type: RumorType, target_kid: Kid, 
                    content: str = None, believability: float = 0.5) -> Rumor:
        """
        Create a new rumor.
        
        Args:
            rumor_type: Type of rumor
            target_kid: Kid who will hear the rumor first
            content: Custom content (optional)
            believability: How believable the rumor is
            
        Returns:
            Created rumor
        """
        self.rumor_id_counter += 1
        rumor_id = f"rumor_{self.rumor_id_counter}"
        
        if content is None:
            content = self._generate_rumor_content(rumor_type, target_kid)
        
        rumor = Rumor(rumor_id, rumor_type, content, target_kid.id, believability)
        self.active_rumors.append(rumor)
        
        # Apply initial effect
        self._apply_rumor_effect(rumor, target_kid)
        
        return rumor
    
    def _generate_rumor_content(self, rumor_type: RumorType, target_kid: Kid) -> str:
        """Generate rumor content from templates."""
        import random
        
        templates = self.rumor_templates.get(rumor_type, ["Generic rumor"])
        template = random.choice(templates)
        
        # Fill in template variables
        content = template.format(
            candy_type=random.choice(['Chocolate', 'Skittles', 'M&Ms', 'Reese\'s']),
            multiplier=random.choice(['2', '3', '5']),
            direction=random.choice(['skyrocket', 'crash', 'double']),
            location=random.choice(['Oak Street', 'Main Street', 'Elm Avenue']),
            quality=random.choice(['stale', 'amazing', 'terrible', 'delicious']),
            kid_name=target_kid.id,
            description=random.choice(['scammer', 'cheater', 'liar']),
            action=random.choice(['stole candy', 'cheated me', 'lied about prices'])
        )
        
        return content
    
    def spread_rumor(self, rumor: Rumor, world):
        """
        Spread a rumor through the social network.
        
        Args:
            rumor: Rumor to spread
            world: Game world reference
        """
        # Get kids within spread radius
        nearby_kids = world.get_nearby_kids(rumor.origin_kid.position, rumor.spread_radius)
        
        for kid in nearby_kids:
            if rumor.can_spread_to(kid.id):
                # Check if rumor spreads to this kid
                import random
                if random.random() < self.spread_chance:
                    rumor.spread_to(kid.id, self.mutation_chance)
                    self._apply_rumor_effect(rumor, kid)
    
    def _apply_rumor_effect(self, rumor: Rumor, kid: Kid):
        """Apply rumor effects to a kid."""
        if rumor.type == RumorType.PRICE:
            # Update kid's believed values
            for candy_type in kid.believed_values:
                if rumor.target_candy_type is None or candy_type == rumor.target_candy_type:
                    effect = rumor.get_effect_on_candy_value(candy_type)
                    kid.believed_values[candy_type] *= effect
        
        elif rumor.type == RumorType.QUALITY:
            # Update quality beliefs (placeholder)
            pass
        
        elif rumor.type == RumorType.PERSON:
            # Update trust levels (placeholder)
            pass
        
        elif rumor.type == RumorType.SUPPLY:
            # Update house preferences (placeholder)
            pass
    
    def get_rumors_affecting_kid(self, kid_id: str) -> List[Rumor]:
        """
        Get all rumors affecting a specific kid.
        
        Args:
            kid_id: ID of the kid
            
        Returns:
            List of active rumors affecting the kid
        """
        return [rumor for rumor in self.active_rumors 
                if kid_id in rumor.affected_kids]
    
    def get_rumors_by_type(self, rumor_type: RumorType) -> List[Rumor]:
        """
        Get all rumors of a specific type.
        
        Args:
            rumor_type: Type of rumors to get
            
        Returns:
            List of rumors of the specified type
        """
        return [rumor for rumor in self.active_rumors 
                if rumor.type == rumor_type]
    
    def get_rumor_stats(self) -> Dict[str, Any]:
        """Get rumor system statistics."""
        stats = {
            'active_rumors': len(self.active_rumors),
            'rumors_by_type': {},
            'total_spread_count': 0,
            'total_mutations': 0
        }
        
        for rumor in self.active_rumors:
            # Count by type
            type_name = rumor.type.name
            stats['rumors_by_type'][type_name] = stats['rumors_by_type'].get(type_name, 0) + 1
            
            # Aggregate stats
            stats['total_spread_count'] += rumor.spread_count
            stats['total_mutations'] += rumor.mutations
        
        return stats
    
    def clear_all_rumors(self):
        """Clear all active rumors."""
        self.active_rumors.clear()
    
    def get_rumor_by_id(self, rumor_id: str) -> Optional[Rumor]:
        """
        Get a rumor by ID.
        
        Args:
            rumor_id: ID of the rumor
            
        Returns:
            Rumor if found, None otherwise
        """
        for rumor in self.active_rumors:
            if rumor.id == rumor_id:
                return rumor
        return None
