# Candy Capitalism - Systems & Engine Design Document

## Overview

This document provides the technical architecture, implementation patterns, and engine-specific details for Candy Capitalism. It's designed for a solo developer with backend strengths working in Pygame.

**Target**: 60 FPS with 30+ autonomous AI agents
**Engine**: Pygame 2.5+
**Python Version**: 3.10+
**Architecture Style**: Entity-Component-System inspired, with event-driven AI

---

## Table of Contents

1. [Engine Architecture](#engine-architecture)
2. [Core Systems](#core-systems)
3. [AI Architecture](#ai-architecture)
4. [Economy & Trading System](#economy--trading-system)
5. [Data Structures & Algorithms](#data-structures--algorithms)
6. [Performance Optimization](#performance-optimization)
7. [State Management](#state-management)
8. [Event System](#event-system)
9. [UI Architecture](#ui-architecture)
10. [Save/Load System](#saveload-system)

---

## Engine Architecture

### Main Game Loop

```python
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Core managers
        self.world = GameWorld()
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler()
        self.ui_manager = UIManager()
        
        # Game state
        self.state_machine = GameStateMachine()
        self.delta_time = 0
        
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            self.delta_time = min(dt, 0.1)  # Cap to prevent spiral of death
            
            # Process input
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                self.input_handler.process_event(event)
            
            # Update game state
            self.state_machine.update(self.delta_time)
            self.world.update(self.delta_time)
            self.ui_manager.update(self.delta_time)
            
            # Render
            self.screen.fill((20, 20, 30))  # Dark background
            self.renderer.render_world(self.world)
            self.ui_manager.render(self.screen)
            pygame.display.flip()
```

### State Machine Pattern

```python
class GameState(Enum):
    MAIN_MENU = 0
    SCENARIO_SELECT = 1
    PLAYING = 2
    PAUSED = 3
    VICTORY = 4
    DEFEAT = 5

class GameStateMachine:
    def __init__(self):
        self.current_state = GameState.MAIN_MENU
        self.states = {
            GameState.MAIN_MENU: MainMenuState(),
            GameState.SCENARIO_SELECT: ScenarioSelectState(),
            GameState.PLAYING: PlayingState(),
            # ... etc
        }
    
    def update(self, dt):
        self.states[self.current_state].update(dt)
    
    def transition(self, new_state):
        self.states[self.current_state].on_exit()
        self.current_state = new_state
        self.states[self.current_state].on_enter()
```

### Coordinate System

- **Screen Space**: Pixels (0,0) top-left, (1280, 720) bottom-right
- **World Space**: Game units (arbitrary scale, e.g., 1 unit = 32 pixels)
- **Grid Space**: Logical grid for pathfinding and zones

Conversion functions:
```python
def world_to_screen(world_pos, camera):
    return (world_pos - camera.position) * camera.zoom

def screen_to_world(screen_pos, camera):
    return screen_pos / camera.zoom + camera.position
```

---

## Core Systems

### 1. GameWorld Class

The central hub that manages all game entities and systems.

```python
class GameWorld:
    def __init__(self):
        # Entity collections
        self.kids: List[Kid] = []
        self.houses: List[House] = []
        self.trading_blocs: List[TradingBloc] = []
        
        # Systems
        self.economy = Economy()
        self.possession_system = PossessionSystem()
        self.rumor_system = RumorSystem()
        self.event_system = EventSystem()
        self.combo_detector = ComboDetector()
        
        # Spatial partitioning for optimization
        self.spatial_grid = SpatialGrid(cell_size=100)
        
        # Timing
        self.game_time = 0.0
        self.ai_tick_timer = 0.0
        self.ai_tick_rate = 2.0  # AI updates every 2 seconds
        
    def update(self, dt):
        self.game_time += dt
        
        # Update economy (decay, price calculations)
        self.economy.update(dt)
        
        # Update spatial grid
        self.spatial_grid.clear()
        for kid in self.kids:
            self.spatial_grid.add(kid.position, kid)
        
        # AI tick (not every frame for performance)
        self.ai_tick_timer += dt
        if self.ai_tick_timer >= self.ai_tick_rate:
            self.ai_tick_timer = 0.0
            self.update_ai()
        
        # Update entities (movement, animations)
        for kid in self.kids:
            kid.update(dt)
        
        # Update systems
        self.rumor_system.update(dt)
        self.event_system.update(dt, self)
        self.update_trading_blocs(dt)
        
        # Check win/lose conditions
        self.check_objectives()
    
    def update_ai(self):
        """Heavy AI logic runs at reduced rate"""
        for kid in self.kids:
            kid.ai_tick(self)
    
    def update_trading_blocs(self, dt):
        """Update cartels, merge/split as needed"""
        # Formation: Look for groups of 3+ friends trading frequently
        # Fracture: Remove members who betray bloc
        # See TradingBloc system section for details
        pass
```

### 2. Spatial Partitioning

Critical for performance with 30+ entities.

```python
class SpatialGrid:
    """Grid-based spatial partitioning for efficient neighbor queries"""
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], List[Entity]] = {}
    
    def _get_cell(self, position):
        x = int(position.x // self.cell_size)
        y = int(position.y // self.cell_size)
        return (x, y)
    
    def add(self, position, entity):
        cell = self._get_cell(position)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)
    
    def clear(self):
        self.grid.clear()
    
    def get_nearby(self, position, radius):
        """Returns entities within radius of position"""
        cell = self._get_cell(position)
        
        # Check surrounding cells
        cells_to_check = [
            (cell[0] + dx, cell[1] + dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
        ]
        
        nearby = []
        for check_cell in cells_to_check:
            if check_cell in self.grid:
                for entity in self.grid[check_cell]:
                    if distance(entity.position, position) <= radius:
                        nearby.append(entity)
        
        return nearby
```

**Usage**: O(1) neighbor queries instead of O(n) for all trading/rumor propagation.

---

## AI Architecture

### Finite State Machine per Kid

```python
class KidState(Enum):
    IDLE = 0
    MOVING_TO_HOUSE = 1
    TRICK_OR_TREATING = 2
    SEEKING_TRADE = 3
    IN_TRADE = 4
    FLEEING = 5  # From bully or parent

class Kid:
    def __init__(self, id, position):
        self.id = id
        self.position = Vector2(position)
        self.velocity = Vector2(0, 0)
        self.max_speed = 50.0  # pixels per second
        
        # State
        self.state = KidState.IDLE
        self.target_position = None
        self.target_house = None
        
        # AI attributes
        self.personality = PersonalityType.VALUE_INVESTOR
        self.preferences = {}  # CandyType -> float (0-1)
        self.believed_values = {}  # CandyType -> float
        self.mood = Mood.NEUTRAL
        self.personal_goal = None
        
        # Social
        self.social_network = []  # List of Kid IDs
        self.trust_levels = {}  # Kid ID -> float (0-1)
        self.trading_bloc = None
        
        # Economic
        self.inventory = {}  # CandyType -> int
        self.debts = {}  # Kid ID -> {CandyType: int}
        
        # Memory
        self.recent_trades = []  # Last 10 trades
        self.observed_strategies = {}  # Strategy -> success count
        
        # Timers
        self.trade_cooldown = 0.0
        
    def update(self, dt):
        """Light update every frame (movement, animations)"""
        self.trade_cooldown = max(0, self.trade_cooldown - dt)
        
        # State-based behavior
        if self.state == KidState.MOVING_TO_HOUSE:
            self.move_toward_target(dt)
            if self.reached_target():
                self.state = KidState.TRICK_OR_TREATING
        
        elif self.state == KidState.SEEKING_TRADE:
            # Movement handled in ai_tick
            pass
    
    def ai_tick(self, world):
        """Heavy AI logic, runs every 2-3 seconds"""
        # Check debt obligations first
        if self.has_overdue_debt():
            self.seek_debt_repayment(world)
            return
        
        # Goal-driven behavior
        if self.personal_goal and self.personal_goal.is_urgent():
            self.pursue_goal(world)
            return
        
        # Default: Trade or trick-or-treat
        if random.random() < 0.3:  # 30% chance to seek house
            self.pick_new_house(world)
        else:
            self.seek_trade_partner(world)
```

### Behavior Tree Alternative (Optional, Advanced)

For more complex AI, consider behavior trees:

```python
class BehaviorTree:
    def __init__(self, root_node):
        self.root = root_node
    
    def tick(self, blackboard):
        return self.root.execute(blackboard)

# Example node
class SequenceNode:
    def __init__(self, children):
        self.children = children
    
    def execute(self, blackboard):
        for child in self.children:
            result = child.execute(blackboard)
            if result != TaskStatus.SUCCESS:
                return result
        return TaskStatus.SUCCESS
```

**Recommendation**: Start with FSM for simplicity. Add behavior trees post-launch if needed.

---

## Economy & Trading System

### Economy Class

```python
class Economy:
    def __init__(self):
        # Value tracking
        self.real_values = {
            CandyType.CHOCOLATE: 8.0,
            CandyType.FRUITY: 5.0,
            CandyType.SOUR: 6.0,
            CandyType.NOVELTY: 4.0,
            CandyType.HEALTH: 2.0,
            CandyType.TRASH: 1.0,
        }
        
        # Market history (for price calculations)
        self.trade_history = deque(maxlen=100)  # Last 100 trades
        self.market_prices = {}  # CandyType -> float
        
        # Price discovery
        self.discovery_active = True
        self.discovery_progress = 0.0
        self.discovery_rate = 0.01  # Per tick
        
    def update(self, dt):
        # Apply decay to all candy
        for kid in game_world.kids:
            kid.apply_decay(dt)
        
        # Update market prices from recent trades
        self.calculate_market_prices()
        
        # Price discovery convergence
        if self.discovery_active:
            self.update_discovery(dt)
    
    def calculate_market_prices(self):
        """Calculate market price as weighted average of recent trades"""
        trades_by_candy = {}
        
        for trade in self.trade_history:
            candy_type = trade.candy_type
            if candy_type not in trades_by_candy:
                trades_by_candy[candy_type] = []
            trades_by_candy[candy_type].append(trade.price)
        
        for candy_type, prices in trades_by_candy.items():
            # Weighted average, more recent trades have higher weight
            weights = [1.0 + i * 0.1 for i in range(len(prices))]
            self.market_prices[candy_type] = np.average(prices, weights=weights)
    
    def update_discovery(self, dt):
        """Gradually converge believed values toward real values"""
        self.discovery_progress += self.discovery_rate
        
        if self.discovery_progress >= 1.0:
            self.discovery_active = False
            return
        
        # Each kid's beliefs gradually move toward reality through trading
        # Actual convergence happens in trade logic
    
    def record_trade(self, candy_type, price, kid_a, kid_b):
        trade = Trade(candy_type, price, kid_a.id, kid_b.id, time.time())
        self.trade_history.append(trade)
```

### Trading Logic

```python
class TradeEvaluator:
    @staticmethod
    def evaluate_trade(kid, offer, request):
        """
        Returns score from kid's perspective. >0 = accept, <0 = reject
        """
        # Calculate perceived value delta
        offer_value = sum(
            kid.believed_values[candy] * qty 
            for candy, qty in offer.items()
        )
        request_value = sum(
            kid.believed_values[candy] * qty 
            for candy, qty in request.items()
        )
        
        base_delta = request_value - offer_value
        
        # Adjust for personality
        threshold = kid.personality.get_threshold()
        
        # Adjust for mood
        if kid.mood == Mood.ANXIOUS:
            threshold *= 0.7  # Accept worse deals
        elif kid.mood == Mood.GREEDY:
            threshold *= 1.5  # Demand better deals
        elif kid.mood == Mood.PANIC:
            threshold = 0.0  # Accept anything
        
        # Adjust for personal goal
        if kid.personal_goal:
            goal_bonus = kid.personal_goal.evaluate_trade(offer, request)
            base_delta += goal_bonus
        
        # Adjust for trading partner (bloc members get better deals)
        if trading_partner.trading_bloc == kid.trading_bloc:
            threshold *= 0.8
        
        return base_delta - threshold

class TradingSystem:
    @staticmethod
    def execute_trade(kid_a, kid_b, offer_a, offer_b):
        """Execute a trade between two kids"""
        # Validate trade is possible
        if not (kid_a.has_items(offer_a) and kid_b.has_items(offer_b)):
            return False
        
        # Exchange inventories
        for candy, qty in offer_a.items():
            kid_a.inventory[candy] -= qty
            kid_b.inventory[candy] += qty
        
        for candy, qty in offer_b.items():
            kid_b.inventory[candy] -= qty
            kid_a.inventory[candy] += qty
        
        # Update beliefs (learning from trade)
        kid_a.update_beliefs_from_trade(offer_a, offer_b)
        kid_b.update_beliefs_from_trade(offer_b, offer_a)
        
        # Update memory
        trade_record = TradeRecord(kid_a, kid_b, offer_a, offer_b, time.time())
        kid_a.recent_trades.append(trade_record)
        kid_b.recent_trades.append(trade_record)
        
        # Record in economy
        economy.record_trade(...)
        
        # Update moods
        kid_a.evaluate_trade_outcome(offer_a, offer_b)
        kid_b.evaluate_trade_outcome(offer_b, offer_a)
        
        return True
```

### Price Discovery Convergence

```python
class Kid:
    def update_beliefs_from_trade(self, what_i_gave, what_i_got):
        """Learn about candy values through trading"""
        if not economy.discovery_active:
            return
        
        # If trade was accepted, our valuations weren't too far off
        for candy in what_i_gave:
            # Move believed value slightly toward real value
            real_val = economy.real_values[candy]
            believed_val = self.believed_values[candy]
            
            # Convergence rate depends on personality
            rate = self.personality.learning_rate  # 0.05 - 0.15
            
            new_belief = believed_val + (real_val - believed_val) * rate
            self.believed_values[candy] = new_belief
        
        # Same for what we got
        for candy in what_i_got:
            # ... similar logic
```

---

## Data Structures & Algorithms

### Pathfinding: A* with Caching

```python
class Pathfinder:
    def __init__(self, grid_world):
        self.grid = grid_world
        self.path_cache = {}  # (start, end) -> path
        self.cache_max_age = 5.0  # Paths expire after 5 seconds
    
    def find_path(self, start, end):
        cache_key = (tuple(start), tuple(end))
        
        # Check cache
        if cache_key in self.path_cache:
            path, timestamp = self.path_cache[cache_key]
            if time.time() - timestamp < self.cache_max_age:
                return path
        
        # Run A*
        path = self.a_star(start, end)
        
        # Cache result
        self.path_cache[cache_key] = (path, time.time())
        
        return path
    
    def a_star(self, start, end):
        """Standard A* implementation"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, end)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == end:
                return reconstruct_path(came_from, current)
            
            for neighbor in self.grid.get_neighbors(current):
                tentative_g = g_score[current] + distance(current, neighbor)
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # No path found
```

**Alternative for Simple Maps**: Waypoint-based navigation (faster, less flexible).

### Rumor Propagation: BFS

```python
class RumorSystem:
    def __init__(self):
        self.active_rumors = []
    
    def spread_rumor(self, rumor, origin_kid):
        """Spread rumor using BFS through social network"""
        visited = set()
        queue = deque([(origin_kid, 0)])  # (kid, depth)
        
        while queue:
            kid, depth = queue.popleft()
            
            if kid.id in visited or depth > rumor.max_depth:
                continue
            
            visited.add(kid.id)
            kid.hear_rumor(rumor)
            
            # Spread to friends and nearby kids
            for friend_id in kid.social_network:
                if random.random() < rumor.spread_chance:
                    friend = world.get_kid_by_id(friend_id)
                    queue.append((friend, depth + 1))
            
            # Also spread to physically nearby kids (overhearing)
            nearby = world.spatial_grid.get_nearby(kid.position, rumor.radius)
            for nearby_kid in nearby:
                if random.random() < rumor.overhear_chance:
                    queue.append((nearby_kid, depth + 1))
```

### Trading Bloc Detection: Union-Find

```python
class TradingBlocDetector:
    def detect_blocs(self, kids):
        """Find connected components of frequent traders"""
        # Build graph of trading relationships
        edges = []
        for kid_a in kids:
            for kid_b in kids:
                if kid_a != kid_b:
                    trade_frequency = self.get_trade_frequency(kid_a, kid_b)
                    if trade_frequency > THRESHOLD:
                        edges.append((kid_a, kid_b, trade_frequency))
        
        # Union-Find to cluster
        parent = {kid: kid for kid in kids}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Merge connected kids
        for kid_a, kid_b, freq in edges:
            union(kid_a, kid_b)
        
        # Group by parent
        blocs = {}
        for kid in kids:
            root = find(kid)
            if root not in blocs:
                blocs[root] = []
            blocs[root].append(kid)
        
        # Filter small blocs (must have 3+ members)
        return [bloc for bloc in blocs.values() if len(bloc) >= 3]
```

---

## Performance Optimization

### Update Frequency Tiers

```python
# Tier 1: Every frame (60 FPS)
- Kid movement and animation
- Camera updates
- Input handling
- UI rendering

# Tier 2: Every AI tick (0.5 Hz = every 2 seconds)
- Trading AI evaluation
- Pathfinding
- Rumor spreading
- Social network updates

# Tier 3: Slow updates (0.1 Hz = every 10 seconds)
- Trading bloc formation
- Market price recalculation
- Decay application (could be even slower)
```

### Object Pooling

```python
class ObjectPool:
    """Reuse objects instead of allocating/deallocating"""
    def __init__(self, factory, initial_size=10):
        self.factory = factory
        self.available = [factory() for _ in range(initial_size)]
        self.in_use = []
    
    def acquire(self):
        if not self.available:
            obj = self.factory()
        else:
            obj = self.available.pop()
        
        self.in_use.append(obj)
        return obj
    
    def release(self, obj):
        self.in_use.remove(obj)
        obj.reset()  # Clear state
        self.available.append(obj)

# Usage for particles, rumors, etc.
rumor_pool = ObjectPool(lambda: Rumor())
```

### Profiling Hooks

```python
import cProfile
import pstats

class PerformanceMonitor:
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.enabled = False
    
    def start(self):
        self.profiler.enable()
        self.enabled = True
    
    def stop_and_print(self):
        if self.enabled:
            self.profiler.disable()
            stats = pstats.Stats(self.profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # Top 20 functions

# Use in debug mode
if DEBUG:
    perf_monitor = PerformanceMonitor()
    perf_monitor.start()
    # ... game loop ...
    perf_monitor.stop_and_print()
```

---

## State Management

### Game State Serialization

```python
@dataclass
class GameState:
    """Snapshot of game state for save/load"""
    kids: List[KidData]
    houses: List[HouseData]
    economy_state: EconomyData
    game_time: float
    chaos_score: int
    unlocked_powers: List[str]
    
    def to_dict(self):
        return {
            'kids': [kid.to_dict() for kid in self.kids],
            'houses': [house.to_dict() for house in self.houses],
            'economy': self.economy_state.to_dict(),
            'game_time': self.game_time,
            'chaos_score': self.chaos_score,
            'unlocked_powers': self.unlocked_powers,
        }
    
    @staticmethod
    def from_dict(data):
        return GameState(
            kids=[KidData.from_dict(k) for k in data['kids']],
            houses=[HouseData.from_dict(h) for h in data['houses']],
            economy_state=EconomyData.from_dict(data['economy']),
            game_time=data['game_time'],
            chaos_score=data['chaos_score'],
            unlocked_powers=data['unlocked_powers'],
        )
```

### Undo/Replay System (Optional)

For debugging or replay features:

```python
class CommandPattern:
    """Record player actions for replay"""
    def __init__(self):
        self.history = []
        self.current_index = 0
    
    def execute(self, command):
        command.do()
        self.history = self.history[:self.current_index]
        self.history.append(command)
        self.current_index += 1
    
    def undo(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.history[self.current_index].undo()
    
    def redo(self):
        if self.current_index < len(self.history):
            self.history[self.current_index].do()
            self.current_index += 1

class PossessCommand:
    def __init__(self, kid_id):
        self.kid_id = kid_id
        self.previous_kid = None
    
    def do(self):
        self.previous_kid = possession_system.current_target
        possession_system.possess(self.kid_id)
    
    def undo(self):
        if self.previous_kid:
            possession_system.possess(self.previous_kid)
```

---

## Event System

### Event Bus Architecture

```python
class EventType(Enum):
    TRADE_COMPLETED = 1
    RUMOR_SPREAD = 2
    DEBT_DEFAULTED = 3
    COMBO_TRIGGERED = 4
    CARTEL_FORMED = 5
    RANDOM_EVENT = 6

class Event:
    def __init__(self, event_type, data):
        self.type = event_type
        self.data = data
        self.timestamp = time.time()

class EventBus:
    def __init__(self):
        self.listeners = {event_type: [] for event_type in EventType}
    
    def subscribe(self, event_type, callback):
        self.listeners[event_type].append(callback)
    
    def publish(self, event):
        for callback in self.listeners[event.type]:
            callback(event)

# Usage
event_bus = EventBus()

def on_trade_completed(event):
    kid_a = event.data['kid_a']
    kid_b = event.data['kid_b']
    # Update UI, check combos, etc.

event_bus.subscribe(EventType.TRADE_COMPLETED, on_trade_completed)

# When trade happens
event_bus.publish(Event(EventType.TRADE_COMPLETED, {
    'kid_a': kid_a,
    'kid_b': kid_b,
    'offer_a': offer_a,
    'offer_b': offer_b
}))
```

### Combo Detection via Events

```python
class ComboDetector:
    def __init__(self, event_bus):
        self.recent_actions = deque(maxlen=20)
        
        # Subscribe to relevant events
        event_bus.subscribe(EventType.RUMOR_SPREAD, self.on_rumor)
        event_bus.subscribe(EventType.TRADE_COMPLETED, self.on_trade)
        # etc.
    
    def on_rumor(self, event):
        self.recent_actions.append(('rumor', event.data, event.timestamp))
        self.check_combos()
    
    def on_trade(self, event):
        self.recent_actions.append(('trade', event.data, event.timestamp))
        self.check_combos()
    
    def check_combos(self):
        """Pattern match recent actions"""
        # Short Squeeze: rumor -> price rise -> sell
        if self.matches_pattern(['rumor:price_up', 'price_increase', 'player_sell']):
            self.trigger_combo('short_squeeze', bonus=25)
        
        # ... other patterns
    
    def trigger_combo(self, combo_name, bonus):
        event_bus.publish(Event(EventType.COMBO_TRIGGERED, {
            'combo': combo_name,
            'bonus': bonus
        }))
```

---

## UI Architecture

### Layered UI System

```python
class UILayer(Enum):
    BACKGROUND = 0
    WORLD = 1
    HUD = 2
    POPUPS = 3
    OVERLAY = 4  # Hold TAB stats

class UIManager:
    def __init__(self):
        self.layers = {layer: [] for layer in UILayer}
        self.active_popup = None
    
    def add_element(self, element, layer):
        self.layers[layer].append(element)
    
    def remove_element(self, element):
        for layer in self.layers.values():
            if element in layer:
                layer.remove(element)
    
    def update(self, dt):
        for layer in UILayer:
            for element in self.layers[layer]:
                element.update(dt)
    
    def render(self, screen):
        for layer in UILayer:
            for element in self.layers[layer]:
                element.render(screen)
    
    def handle_event(self, event):
        # Process in reverse layer order (top to bottom)
        for layer in reversed(list(UILayer)):
            for element in self.layers[layer]:
                if element.handle_event(event):
                    return True  # Event consumed
        return False
```

### UI Elements

```python
class UIElement:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.visible = True
        self.enabled = True
    
    def update(self, dt):
        pass
    
    def render(self, screen):
        pass
    
    def handle_event(self, event):
        return False  # Not consumed

class Button(UIElement):
    def __init__(self, rect, text, callback):
        super().__init__(rect)
        self.text = text
        self.callback = callback
        self.hovered = False
    
    def handle_event(self, event):
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.callback()
                return True
        
        return False
    
    def render(self, screen):
        color = (100, 100, 255) if self.hovered else (70, 70, 200)
        pygame.draw.rect(screen, color, self.rect)
        # ... render text

class EnergyBar(UIElement):
    def __init__(self, rect, possession_system):
        super().__init__(rect)
        self.possession_system = possession_system
    
    def render(self, screen):
        # Background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        
        # Fill based on current energy
        fill_width = (self.possession_system.chaos_energy / 
                      self.possession_system.max_energy) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, (255, 100, 100), fill_rect)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
```

### Text Rendering Optimization

```python
class FontManager:
    """Cache rendered text surfaces"""
    def __init__(self):
        self.fonts = {
            'small': pygame.font.Font(None, 16),
            'medium': pygame.font.Font(None, 24),
            'large': pygame.font.Font(None, 36),
        }
        self.cache = {}
    
    def render(self, text, font_size, color):
        cache_key = (text, font_size, color)
        
        if cache_key not in self.cache:
            font = self.fonts[font_size]
            surface = font.render(text, True, color)
            self.cache[cache_key] = surface
        
        return self.cache[cache_key]
    
    def clear_cache(self):
        self.cache.clear()
```

---

## Save/Load System

### Save File Format (JSON)

```json
{
  "version": "1.0.0",
  "save_timestamp": 1234567890,
  "progression": {
    "unlocked_powers": ["possess", "basic_rumor", "curse_house"],
    "completed_scenarios": ["tutorial", "market_crash"],
    "chaos_points": 1250,
    "high_scores": {
      "tutorial": {"time": 180, "chaos": 150},
      "market_crash": {"time": 420, "chaos": 800}
    }
  },
  "current_game": {
    "scenario_id": "market_crash",
    "game_time": 245.5,
    "kids": [...],
    "houses": [...],
    "economy": {...}
  }
}
```

### Save/Load Implementation

```python
import json
from pathlib import Path

class SaveSystem:
    SAVE_DIR = Path.home() / ".candy_capitalism" / "saves"
    
    def __init__(self):
        self.SAVE_DIR.mkdir(parents=True, exist_ok=True)
    
    def save_game(self, slot_name, game_state, progression):
        save_data = {
            'version': '1.0.0',
            'save_timestamp': time.time(),
            'progression': progression.to_dict(),
            'current_game': game_state.to_dict() if game_state else None
        }
        
        save_path = self.SAVE_DIR / f"{slot_name}.json"
        
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
    
    def load_game(self, slot_name):
        save_path = self.SAVE_DIR / f"{slot_name}.json"
        
        if not save_path.exists():
            return None
        
        with open(save_path, 'r') as f:
            save_data = json.load(f)
        
        # Version compatibility check
        if save_data['version'] != '1.0.0':
            # Handle migration if needed
            pass
        
        progression = Progression.from_dict(save_data['progression'])
        
        game_state = None
        if save_data['current_game']:
            game_state = GameState.from_dict(save_data['current_game'])
        
        return progression, game_state
    
    def list_saves(self):
        return [f.stem for f in self.SAVE_DIR.glob("*.json")]
```

### Auto-save

```python
class AutoSaveManager:
    def __init__(self, save_system, interval=60.0):
        self.save_system = save_system
        self.interval = interval
        self.timer = 0.0
    
    def update(self, dt, game_state, progression):
        self.timer += dt
        
        if self.timer >= self.interval:
            self.timer = 0.0
            self.save_system.save_game('autosave', game_state, progression)
            print("Auto-saved")
```

---

## Configuration System

### JSON-based Configs

```python
# config/candy_types.json
{
  "CHOCOLATE": {
    "name": "Chocolate",
    "real_value": 8.0,
    "decay_rate": 0.01,
    "icon": "chocolate.png",
    "color": [139, 69, 19]
  },
  "FRUITY": {
    "name": "Fruity",
    "real_value": 5.0,
    "decay_rate": 0.015,
    "icon": "fruity.png",
    "color": [255, 100, 100]
  }
}

# config/personalities.json
{
  "VALUE_INVESTOR": {
    "threshold": 1.5,
    "learning_rate": 0.08,
    "risk_tolerance": 0.3
  },
  "MOMENTUM_TRADER": {
    "threshold": 0.5,
    "learning_rate": 0.15,
    "risk_tolerance": 0.7
  }
}

# config/scenarios.json
{
  "tutorial": {
    "name": "First Halloween",
    "kid_count": 5,
    "starting_wealth": "equal",
    "unlocked_powers": ["possess", "basic_rumor"],
    "objective": {
      "type": "bad_trades",
      "target": 10
    },
    "time_limit": null
  }
}
```

### Config Loader

```python
class ConfigManager:
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.configs = {}
    
    def load_all(self):
        for config_file in self.config_dir.glob("*.json"):
            config_name = config_file.stem
            with open(config_file) as f:
                self.configs[config_name] = json.load(f)
    
    def get(self, category, key=None):
        if key:
            return self.configs[category][key]
        return self.configs[category]

# Usage
config = ConfigManager()
config.load_all()

chocolate_config = config.get('candy_types', 'CHOCOLATE')
```

---

## Debugging Tools

### Debug Overlay

```python
class DebugOverlay:
    def __init__(self):
        self.enabled = False
        self.font = pygame.font.Font(None, 16)
    
    def toggle(self):
        self.enabled = not self.enabled
    
    def render(self, screen, world):
        if not self.enabled:
            return
        
        y = 10
        debug_info = [
            f"FPS: {clock.get_fps():.1f}",
            f"Kids: {len(world.kids)}",
            f"Active Trades: {world.active_trade_count()}",
            f"Active Rumors: {len(world.rumor_system.active_rumors)}",
            f"Trading Blocs: {len(world.trading_blocs)}",
            f"Spatial Grid Cells: {len(world.spatial_grid.grid)}",
        ]
        
        for line in debug_info:
            surface = self.font.render(line, True, (255, 255, 0))
            screen.blit(surface, (10, y))
            y += 20
        
        # Draw spatial grid
        for cell_pos, entities in world.spatial_grid.grid.items():
            cell_rect = pygame.Rect(
                cell_pos[0] * world.spatial_grid.cell_size,
                cell_pos[1] * world.spatial_grid.cell_size,
                world.spatial_grid.cell_size,
                world.spatial_grid.cell_size
            )
            pygame.draw.rect(screen, (0, 255, 0), cell_rect, 1)

# Toggle with F3
if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
    debug_overlay.toggle()
```

### AI Debugger

```python
class AIDebugger:
    """Visualize AI decision making"""
    def __init__(self):
        self.selected_kid = None
    
    def select_kid(self, kid):
        self.selected_kid = kid
    
    def render(self, screen):
        if not self.selected_kid:
            return
        
        # Show thought bubble
        thoughts = [
            f"State: {self.selected_kid.state.name}",
            f"Mood: {self.selected_kid.mood.name}",
            f"Goal: {self.selected_kid.personal_goal.type}",
            f"Bloc: {self.selected_kid.trading_bloc.id if self.selected_kid.trading_bloc else 'None'}",
        ]
        
        # Draw near kid
        x, y = self.selected_kid.position
        for i, thought in enumerate(thoughts):
            surface = font.render(thought, True, (255, 255, 255))
            screen.blit(surface, (x + 20, y + i * 15))
```

---

## Testing Strategy

### Unit Tests

```python
import unittest

class TestTradeEvaluator(unittest.TestCase):
    def setUp(self):
        self.kid = Kid(id=1, position=(0, 0))
        self.kid.believed_values = {
            CandyType.CHOCOLATE: 8.0,
            CandyType.TRASH: 1.0
        }
        self.kid.personality = PersonalityType.VALUE_INVESTOR
    
    def test_fair_trade_accepted(self):
        offer = {CandyType.CHOCOLATE: 1}
        request = {CandyType.CHOCOLATE: 1}
        
        score = TradeEvaluator.evaluate_trade(self.kid, offer, request)
        self.assertGreaterEqual(score, 0)
    
    def test_bad_trade_rejected(self):
        offer = {CandyType.CHOCOLATE: 1}
        request = {CandyType.TRASH: 1}
        
        score = TradeEvaluator.evaluate_trade(self.kid, offer, request)
        self.assertLess(score, 0)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
class TestTradingSystem(unittest.TestCase):
    def setUp(self):
        self.world = GameWorld()
        # Set up test scenario
    
    def test_trade_execution(self):
        kid_a = self.world.kids[0]
        kid_b = self.world.kids[1]
        
        # Give kid_a chocolate
        kid_a.inventory[CandyType.CHOCOLATE] = 1
        
        # Execute trade
        result = TradingSystem.execute_trade(
            kid_a, kid_b,
            {CandyType.CHOCOLATE: 1},
            {CandyType.FRUITY: 1}
        )
        
        self.assertTrue(result)
        self.assertEqual(kid_a.inventory[CandyType.CHOCOLATE], 0)
        self.assertEqual(kid_b.inventory[CandyType.CHOCOLATE], 1)
```

---

## Performance Benchmarks

### Target Metrics

```
- Update loop: < 16ms (for 60 FPS)
- AI tick with 30 kids: < 50ms (happens every 2s, so acceptable)
- Pathfinding: < 10ms per path
- Rumor spread: < 5ms per rumor
- Trade execution: < 1ms
- Render frame: < 16ms
```

### Profiling Example

```python
import time

class PerformanceTimer:
    def __init__(self, name):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        elapsed = (time.perf_counter() - self.start_time) * 1000
        print(f"{self.name}: {elapsed:.2f}ms")

# Usage
with PerformanceTimer("AI Tick"):
    world.update_ai()
```

---

## Conclusion

This systems and engine design provides a solid foundation for Candy Capitalism:

**Key Architectural Decisions:**
- Event-driven for decoupling systems
- Spatial partitioning for performance
- Tiered update frequencies for optimization
- JSON configs for easy tuning
- State pattern for clean game flow

**Performance Strategy:**
- Heavy AI logic at 0.5 Hz, not 60 Hz
- Object pooling for frequent allocations
- Pathfinding caching
- Spatial grid for O(1) neighbor queries

**Maintainability:**
- Clear separation of concerns
- Config-driven behavior
- Comprehensive debug tools
- Unit test coverage for core logic

The architecture supports all the gameplay features while remaining simple enough for solo development. Focus your effort on the AI trading logic and emergence - that's where the magic happens. The engine just needs to be "good enough" to support it.

Start with the basics (Sprints 1-3), validate the fun, then layer in complexity. The modular design means you can ship a simpler version and expand post-launch.

Good luck building your economic chaos simulator!
