"""
Event system for decoupled communication between game systems.

Implements an event bus pattern for publishing and subscribing to game events,
enabling loose coupling between different game systems.
"""

from typing import Dict, List, Callable, Any
from enum import Enum
import time


class EventType(Enum):
    """Types of events that can be published."""
    TRADE_COMPLETED = 1
    RUMOR_SPREAD = 2
    DEBT_DEFAULTED = 3
    COMBO_TRIGGERED = 4
    CARTEL_FORMED = 5
    RANDOM_EVENT = 6
    KID_POSSESSED = 7
    HOUSE_CURSED = 8
    HOUSE_BLESSED = 9
    PRICE_CHANGED = 10


class Event:
    """Represents a game event."""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any]):
        self.type = event_type
        self.data = data
        self.timestamp = time.time()
        self.id = f"{event_type.name}_{int(self.timestamp * 1000)}"


class EventBus:
    """
    Event bus for publishing and subscribing to game events.
    
    Enables decoupled communication between game systems using
    the publish-subscribe pattern.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self.listeners: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        self.event_history: List[Event] = []
        self.max_history = 1000  # Keep last 1000 events
        
    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to listen for
            callback: Function to call when event occurs
        """
        if callback not in self.listeners[event_type]:
            self.listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of events to stop listening for
            callback: Function to remove from listeners
        """
        if callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
    
    def publish(self, event: Event):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify all listeners
        for callback in self.listeners[event.type]:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")
    
    def publish_event(self, event_type: EventType, data: Dict[str, Any] = None):
        """
        Convenience method to publish an event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        event = Event(event_type, data or {})
        self.publish(event)
    
    def get_recent_events(self, event_type: EventType = None, limit: int = 10) -> List[Event]:
        """
        Get recent events.
        
        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        events = self.event_history[-limit:] if limit else self.event_history
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return events
    
    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event system statistics."""
        stats = {
            'total_events': len(self.event_history),
            'listeners_by_type': {}
        }
        
        for event_type, listeners in self.listeners.items():
            stats['listeners_by_type'][event_type.name] = len(listeners)
        
        return stats


class EventSystem:
    """
    High-level event system that manages event bus and provides
    convenient methods for common game events.
    """
    
    def __init__(self):
        """Initialize the event system."""
        self.event_bus = EventBus()
        self.game_world = None
        
    def set_game_world(self, game_world):
        """Set reference to game world."""
        self.game_world = game_world
    
    def update(self, dt: float, game_world):
        """
        Update event system.
        
        Args:
            dt: Delta time in seconds
            game_world: Reference to game world
        """
        # This is where we could process queued events, etc.
        pass
    
    def publish_trade_completed(self, kid_a_id: str, kid_b_id: str, 
                               offer: Dict[str, int], request: Dict[str, int]):
        """Publish a trade completed event."""
        self.event_bus.publish_event(EventType.TRADE_COMPLETED, {
            'kid_a_id': kid_a_id,
            'kid_b_id': kid_b_id,
            'offer': offer,
            'request': request
        })
    
    def publish_rumor_spread(self, rumor_id: str, target_kid_id: str):
        """Publish a rumor spread event."""
        self.event_bus.publish_event(EventType.RUMOR_SPREAD, {
            'rumor_id': rumor_id,
            'target_kid_id': target_kid_id
        })
    
    def publish_debt_defaulted(self, debtor_id: str, creditor_id: str, amount: float):
        """Publish a debt default event."""
        self.event_bus.publish_event(EventType.DEBT_DEFAULTED, {
            'debtor_id': debtor_id,
            'creditor_id': creditor_id,
            'amount': amount
        })
    
    def publish_combo_triggered(self, combo_name: str, bonus: int):
        """Publish a combo triggered event."""
        self.event_bus.publish_event(EventType.COMBO_TRIGGERED, {
            'combo_name': combo_name,
            'bonus': bonus
        })
    
    def publish_cartel_formed(self, cartel_id: str, member_ids: List[str]):
        """Publish a cartel formed event."""
        self.event_bus.publish_event(EventType.CARTEL_FORMED, {
            'cartel_id': cartel_id,
            'member_ids': member_ids
        })
    
    def publish_kid_possessed(self, kid_id: str, player_id: str = "player"):
        """Publish a kid possessed event."""
        self.event_bus.publish_event(EventType.KID_POSSESSED, {
            'kid_id': kid_id,
            'player_id': player_id
        })
    
    def publish_house_cursed(self, house_id: str, duration: float):
        """Publish a house cursed event."""
        self.event_bus.publish_event(EventType.HOUSE_CURSED, {
            'house_id': house_id,
            'duration': duration
        })
    
    def publish_house_blessed(self, house_id: str, duration: float):
        """Publish a house blessed event."""
        self.event_bus.publish_event(EventType.HOUSE_BLESSED, {
            'house_id': house_id,
            'duration': duration
        })
    
    def publish_price_changed(self, candy_type: str, old_price: float, new_price: float):
        """Publish a price changed event."""
        self.event_bus.publish_event(EventType.PRICE_CHANGED, {
            'candy_type': candy_type,
            'old_price': old_price,
            'new_price': new_price
        })
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to an event type."""
        self.event_bus.subscribe(event_type, callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from an event type."""
        self.event_bus.unsubscribe(event_type, callback)
    
    def get_event_bus(self) -> EventBus:
        """Get the underlying event bus."""
        return self.event_bus
