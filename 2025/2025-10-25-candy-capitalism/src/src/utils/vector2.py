"""
2D Vector class for positions, velocities, and other 2D math operations.

Provides efficient 2D vector operations needed for game physics and positioning.
"""

import math
from typing import Tuple, Union


class Vector2:
    """
    2D Vector class with common mathematical operations.
    
    Used for positions, velocities, and other 2D calculations throughout the game.
    """
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        """Add two vectors."""
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        """Subtract two vectors."""
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: Union[float, int]) -> 'Vector2':
        """Multiply vector by scalar."""
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: Union[float, int]) -> 'Vector2':
        """Right multiply vector by scalar."""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: Union[float, int]) -> 'Vector2':
        """Divide vector by scalar."""
        if scalar == 0:
            raise ValueError("Cannot divide vector by zero")
        return Vector2(self.x / scalar, self.y / scalar)
    
    def __neg__(self) -> 'Vector2':
        """Negate vector."""
        return Vector2(-self.x, -self.y)
    
    def __eq__(self, other: 'Vector2') -> bool:
        """Check if two vectors are equal."""
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9
    
    def __repr__(self) -> str:
        """String representation of vector."""
        return f"Vector2({self.x:.2f}, {self.y:.2f})"
    
    def __iter__(self):
        """Allow unpacking: x, y = vector."""
        yield self.x
        yield self.y
    
    def length(self) -> float:
        """Get the length (magnitude) of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def length_squared(self) -> float:
        """Get the squared length of the vector (faster than length())."""
        return self.x * self.x + self.y * self.y
    
    def normalize(self) -> 'Vector2':
        """Return a normalized copy of this vector."""
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)
    
    def normalized(self) -> 'Vector2':
        """Alias for normalize()."""
        return self.normalize()
    
    def dot(self, other: 'Vector2') -> float:
        """Calculate dot product with another vector."""
        return self.x * other.x + self.y * other.y
    
    def distance_to(self, other: 'Vector2') -> float:
        """Calculate distance to another vector."""
        return (self - other).length()
    
    def distance_squared_to(self, other: 'Vector2') -> float:
        """Calculate squared distance to another vector (faster)."""
        return (self - other).length_squared()
    
    def angle_to(self, other: 'Vector2') -> float:
        """Calculate angle to another vector in radians."""
        return math.atan2(other.y - self.y, other.x - self.x)
    
    def rotate(self, angle: float) -> 'Vector2':
        """Rotate vector by angle in radians."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )
    
    def lerp(self, other: 'Vector2', t: float) -> 'Vector2':
        """Linear interpolation between this vector and another."""
        t = max(0.0, min(1.0, t))  # Clamp t to [0, 1]
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple (x, y)."""
        return (self.x, self.y)
    
    def to_int_tuple(self) -> Tuple[int, int]:
        """Convert to integer tuple (x, y)."""
        return (int(self.x), int(self.y))
    
    def copy(self) -> 'Vector2':
        """Create a copy of this vector."""
        return Vector2(self.x, self.y)
    
    @classmethod
    def from_tuple(cls, coords: Tuple[float, float]) -> 'Vector2':
        """Create vector from tuple (x, y)."""
        return cls(coords[0], coords[1])
    
    @classmethod
    def from_angle(cls, angle: float, length: float = 1.0) -> 'Vector2':
        """Create vector from angle and length."""
        return cls(
            math.cos(angle) * length,
            math.sin(angle) * length
        )
    
    @classmethod
    def zero(cls) -> 'Vector2':
        """Create zero vector."""
        return cls(0, 0)
    
    @classmethod
    def one(cls) -> 'Vector2':
        """Create vector (1, 1)."""
        return cls(1, 1)


def distance(a: Vector2, b: Vector2) -> float:
    """Calculate distance between two vectors."""
    return a.distance_to(b)


def distance_squared(a: Vector2, b: Vector2) -> float:
    """Calculate squared distance between two vectors."""
    return a.distance_squared_to(b)


def lerp(a: Vector2, b: Vector2, t: float) -> Vector2:
    """Linear interpolation between two vectors."""
    return a.lerp(b, t)
