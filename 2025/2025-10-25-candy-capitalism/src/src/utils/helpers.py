"""
Helper functions and utilities.

Common helper functions used throughout the game for coordinate conversion,
math operations, and other utilities.
"""

import math
from typing import Tuple, Union
from .vector2 import Vector2


def world_to_screen(world_pos: Vector2, camera_pos: Vector2, zoom: float = 1.0) -> Vector2:
    """
    Convert world coordinates to screen coordinates.
    
    Args:
        world_pos: Position in world space
        camera_pos: Camera position in world space
        zoom: Camera zoom level
        
    Returns:
        Position in screen space
    """
    return (world_pos - camera_pos) * zoom


def screen_to_world(screen_pos: Vector2, camera_pos: Vector2, zoom: float = 1.0) -> Vector2:
    """
    Convert screen coordinates to world coordinates.
    
    Args:
        screen_pos: Position in screen space
        camera_pos: Camera position in world space
        zoom: Camera zoom level
        
    Returns:
        Position in world space
    """
    return screen_pos / zoom + camera_pos


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Interpolated value
    """
    t = clamp(t, 0.0, 1.0)
    return a + (b - a) * t


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """
    Smooth interpolation function.
    
    Args:
        edge0: Lower edge
        edge1: Upper edge
        x: Input value
        
    Returns:
        Smoothly interpolated value
    """
    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def angle_between_vectors(a: Vector2, b: Vector2) -> float:
    """
    Calculate the angle between two vectors in radians.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Angle in radians
    """
    dot = a.normalize().dot(b.normalize())
    return math.acos(clamp(dot, -1.0, 1.0))


def random_point_in_circle(center: Vector2, radius: float) -> Vector2:
    """
    Generate a random point within a circle.
    
    Args:
        center: Center of the circle
        radius: Radius of the circle
        
    Returns:
        Random point within the circle
    """
    import random
    
    # Generate random angle and distance
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, radius)
    
    return center + Vector2.from_angle(angle, distance)


def random_point_in_rect(top_left: Vector2, bottom_right: Vector2) -> Vector2:
    """
    Generate a random point within a rectangle.
    
    Args:
        top_left: Top-left corner of rectangle
        bottom_right: Bottom-right corner of rectangle
        
    Returns:
        Random point within the rectangle
    """
    import random
    
    x = random.uniform(top_left.x, bottom_right.x)
    y = random.uniform(top_left.y, bottom_right.y)
    
    return Vector2(x, y)


def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def format_currency(amount: float) -> str:
    """
    Format a number as currency.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:.2f}"


def is_point_in_rect(point: Vector2, rect_pos: Vector2, rect_size: Vector2) -> bool:
    """
    Check if a point is inside a rectangle.
    
    Args:
        point: Point to check
        rect_pos: Top-left position of rectangle
        rect_size: Size of rectangle
        
    Returns:
        True if point is inside rectangle
    """
    return (rect_pos.x <= point.x <= rect_pos.x + rect_size.x and
            rect_pos.y <= point.y <= rect_pos.y + rect_size.y)


def rect_intersects_rect(pos1: Vector2, size1: Vector2, 
                        pos2: Vector2, size2: Vector2) -> bool:
    """
    Check if two rectangles intersect.
    
    Args:
        pos1: Position of first rectangle
        size1: Size of first rectangle
        pos2: Position of second rectangle
        size2: Size of second rectangle
        
    Returns:
        True if rectangles intersect
    """
    return not (pos1.x + size1.x < pos2.x or
                pos2.x + size2.x < pos1.x or
                pos1.y + size1.y < pos2.y or
                pos2.y + size2.y < pos1.y)


def normalize_angle(angle: float) -> float:
    """
    Normalize an angle to the range [0, 2π).
    
    Args:
        angle: Angle in radians
        
    Returns:
        Normalized angle
    """
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle


def angle_difference(a: float, b: float) -> float:
    """
    Calculate the shortest angular difference between two angles.
    
    Args:
        a: First angle in radians
        b: Second angle in radians
        
    Returns:
        Shortest angular difference in radians
    """
    diff = b - a
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff


def sign(value: float) -> int:
    """
    Get the sign of a value.
    
    Args:
        value: Value to check
        
    Returns:
        -1 if negative, 0 if zero, 1 if positive
    """
    if value < 0:
        return -1
    elif value > 0:
        return 1
    else:
        return 0
