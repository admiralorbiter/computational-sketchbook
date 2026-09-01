"""
Candy type definitions and visual properties.

Defines candy types, their properties, and visual representations.
"""

from typing import Dict, Tuple, Optional
from ..core.config_manager import config_manager


class CandyType:
    """Represents a type of candy with its properties."""
    
    def __init__(self, name: str, real_value: float, decay_rate: float = 0.01,
                 color: Tuple[int, int, int] = (255, 255, 255), 
                 icon: str = "?", description: str = ""):
        self.name = name
        self.real_value = real_value
        self.decay_rate = decay_rate
        self.color = color
        self.icon = icon
        self.description = description
    
    def __repr__(self):
        return f"CandyType({self.name}, value={self.real_value})"


class CandyTypes:
    """Manages candy type definitions and visual properties."""
    
    # Registry of all candy types
    _candy_types: Dict[str, CandyType] = {}
    _initialized = False
    
    # Candy type colors (RGB tuples) - defaults
    CANDY_COLORS = {
        "CHOCOLATE": (139, 69, 19),    # Brown
        "FRUITY": (255, 100, 100),     # Pink-red
        "SOUR": (255, 255, 100),       # Yellow
        "MINT": (0, 255, 127),         # Green
        "CARAMEL": (255, 165, 0),      # Orange
        "LICORICE": (75, 0, 130),      # Purple
        "TRASH": (100, 100, 100),      # Gray
        "HEALTH": (100, 255, 100),     # Bright Green
        "NOVELTY": (255, 100, 255)     # Hot Pink
    }
    
    # Candy type icons (single characters for now)
    CANDY_ICONS = {
        "CHOCOLATE": "C",
        "FRUITY": "F",
        "SOUR": "S",
        "MINT": "M",
        "CARAMEL": "A",
        "LICORICE": "L",
        "TRASH": "T",
        "HEALTH": "H",
        "NOVELTY": "N"
    }
    
    # Fallback for unknown candy types
    DEFAULT_COLOR = (255, 255, 255)  # White
    DEFAULT_ICON = "?"  # Generic candy
    
    @classmethod
    def load_from_config(cls):
        """Load candy types from configuration file."""
        if cls._initialized:
            return
        
        try:
            # Ensure config is loaded
            if not config_manager.configs:
                config_manager.load_all()
            
            candy_config = config_manager.get('candy_types')
            if candy_config:
                for candy_key, properties in candy_config.items():
                    name = properties.get('name', candy_key.title())
                    real_value = properties.get('real_value', 5.0)
                    decay_rate = properties.get('decay_rate', 0.01)
                    color = tuple(properties.get('color', cls.CANDY_COLORS.get(candy_key, cls.DEFAULT_COLOR)))
                    icon = properties.get('icon', cls.CANDY_ICONS.get(candy_key, cls.DEFAULT_ICON))
                    description = properties.get('description', '')
                    
                    candy_type = CandyType(name, real_value, decay_rate, color, icon, description)
                    cls._candy_types[candy_key] = candy_type
                    
                    # Update color and icon maps
                    cls.CANDY_COLORS[candy_key] = color
                    cls.CANDY_ICONS[candy_key] = icon
        except Exception as e:
            print(f"Warning: Could not load candy types from config: {e}")
        
        cls._initialized = True
    
    @classmethod
    def get(cls, candy_key: str) -> Optional[CandyType]:
        """Get a candy type by key."""
        if not cls._initialized:
            cls.load_from_config()
        return cls._candy_types.get(candy_key)
    
    @classmethod
    def get_color(cls, candy_type: str) -> Tuple[int, int, int]:
        """Get color for a candy type."""
        if not cls._initialized:
            cls.load_from_config()
        return cls.CANDY_COLORS.get(candy_type, cls.DEFAULT_COLOR)
    
    @classmethod
    def get_icon(cls, candy_type: str) -> str:
        """Get icon for a candy type."""
        if not cls._initialized:
            cls.load_from_config()
        return cls.CANDY_ICONS.get(candy_type, cls.DEFAULT_ICON)
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get list of all candy type keys."""
        if not cls._initialized:
            cls.load_from_config()
        return list(cls._candy_types.keys())
    
    @classmethod
    def get_all_candy_objects(cls) -> list:
        """Get list of all CandyType objects."""
        if not cls._initialized:
            cls.load_from_config()
        return list(cls._candy_types.values())
    
    @classmethod
    def get_visual_properties(cls, candy_type: str) -> Dict[str, any]:
        """Get all visual properties for a candy type."""
        candy_obj = cls.get(candy_type)
        if candy_obj:
            return {
                "color": candy_obj.color,
                "icon": candy_obj.icon,
                "name": candy_obj.name,
                "real_value": candy_obj.real_value
            }
        return {
            "color": cls.DEFAULT_COLOR,
            "icon": cls.DEFAULT_ICON,
            "name": candy_type.title(),
            "real_value": 1.0
        }


# Initialize candy types from config
CandyTypes.load_from_config()
