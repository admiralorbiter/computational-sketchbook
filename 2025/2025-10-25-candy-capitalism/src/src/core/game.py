"""
Main game class and game loop.

Handles initialization, main game loop, and coordination between systems.
"""

import pygame
from typing import Optional, Dict, Any

from .constants import SCREEN_SIZE, FPS_TARGET, COLORS
from .game_state import GameState, GameStateMachine, BaseState
from .config_manager import config_manager
from ..systems.game_world import GameWorld
from ..entities.kid import Kid
from ..rendering.renderer import Renderer
from ..rendering.particle_system import ParticleSystem
from ..rendering.floating_text import FloatingTextSystem
from ..ui.market_ticker import MarketTicker
from ..ui.economy_debug import EconomyDebugOverlay
from ..utils.vector2 import Vector2


class Game:
    """
    Main game class that manages the game loop and coordinates all systems.
    
    Based on the architecture from systems.md with a focus on clean separation
    of concerns and event-driven design.
    """
    
    def __init__(self):
        """Initialize the game and all its systems."""
        pygame.init()
        
        # Create game window
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Candy Capitalism")
        
        # Game clock for FPS control
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load configurations
        config_manager.load_all()
        
        # Initialize core systems
        self.state_machine = GameStateMachine()
        self._setup_states()
        
        # Game state
        self.delta_time = 0.0
        self.game_time = 0.0
        
        print("Candy Capitalism initialized successfully")
    
    def _setup_states(self):
        """Set up all game states."""
        # For now, just register placeholder states
        # These will be implemented in later sprints
        self.state_machine.register_state(GameState.MAIN_MENU, MainMenuState())
        self.state_machine.register_state(GameState.PLAYING, PlayingState())
        self.state_machine.register_state(GameState.PAUSED, PausedState())
    
    def run(self):
        """Main game loop."""
        print("Starting game loop...")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS_TARGET) / 1000.0
            self.delta_time = min(dt, 0.1)  # Cap to prevent spiral of death
            self.game_time += self.delta_time
            
            # Handle events
            self._handle_events()
            
            # Update game state
            self.state_machine.update(self.delta_time)
            
            # Render
            self._render()
            
            # Update display
            pygame.display.flip()
        
        self._cleanup()
    
    def _handle_events(self):
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Only quit from non-playing states
                    if self.state_machine.current_state != GameState.PLAYING:
                        self.running = False
                elif event.key == pygame.K_p:
                    # Toggle pause
                    if self.state_machine.current_state == GameState.PLAYING:
                        self.state_machine.transition(GameState.PAUSED)
                    elif self.state_machine.current_state == GameState.PAUSED:
                        self.state_machine.transition(GameState.PLAYING)
                else:
                    # Pass to current state
                    result = self.state_machine.handle_event(event)
                    if result == "start_game":
                        self.state_machine.transition(GameState.PLAYING)
                    elif result == "quit":
                        self.running = False
                    elif result == "resume":
                        self.state_machine.transition(GameState.PLAYING)
            else:
                # Pass to current state
                self.state_machine.handle_event(event)
    
    def _render(self):
        """Render the current frame."""
        # Clear screen
        self.screen.fill(COLORS['BACKGROUND'])
        
        # Let current state handle rendering
        if hasattr(self.state_machine.states.get(self.state_machine.current_state), 'render'):
            self.state_machine.states[self.state_machine.current_state].render(self.screen)
    
    def _cleanup(self):
        """Clean up resources before exiting."""
        pygame.quit()
        print("Game cleanup complete")


class MainMenuState(BaseState):
    """Main menu state with game start option."""
    
    def on_enter(self, data=None):
        print("Entered main menu")
    
    def handle_event(self, event):
        """Handle input events for main menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Start the game
                return "start_game"
            elif event.key == pygame.K_ESCAPE:
                # Quit
                return "quit"
        return False
    
    def render(self, screen):
        # Simple placeholder rendering
        font = pygame.font.Font(None, 48)
        text = font.render("Candy Capitalism", True, COLORS['WHITE'])
        text_rect = text.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2))
        screen.blit(text, text_rect)
        
        # Instructions
        font_small = pygame.font.Font(None, 24)
        instructions = font_small.render("Press SPACE to start, ESC to quit", True, COLORS['GRAY'])
        inst_rect = instructions.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2 + 50))
        screen.blit(instructions, inst_rect)


class PlayingState(BaseState):
    """Playing state with world and rendering."""
    
    def __init__(self):
        self.world = GameWorld()
        self.renderer = None
        self.initialized = False
        
        # UI elements
        self.particle_system = ParticleSystem()
        self.floating_text_system = FloatingTextSystem()
        self.market_ticker = MarketTicker(SCREEN_SIZE[0], SCREEN_SIZE[1])
        self.economy_debug = EconomyDebugOverlay(SCREEN_SIZE[0], SCREEN_SIZE[1])
        
        # Sprint 3 HUD elements
        from ..ui.energy_bar import EnergyBar
        from ..ui.kid_info_panel import KidInfoPanel
        from ..ui.chaos_score_display import ChaosScoreDisplay
        from ..ui.power_menu import PowerMenu
        from ..ui.trade_window import TradeWindow
        
        self.energy_bar = EnergyBar()
        self.kid_info_panel = KidInfoPanel()
        self.chaos_score = ChaosScoreDisplay(SCREEN_SIZE[0])
        self.power_menu = None  # Created when needed
        self.trade_window = None  # Created when needed
        
        # Ensure HUD elements are properly initialized
        self.energy_bar.visible = True
        self.energy_bar.enabled = True
        self.kid_info_panel.visible = True
        self.kid_info_panel.enabled = True
        self.chaos_score.visible = True
        self.chaos_score.enabled = True
    
    def on_enter(self, data=None):
        print("Entered playing state")
        if not self.initialized:
            self.renderer = Renderer(pygame.display.get_surface())
            
            # Add UI systems to renderer for trade effects
            self.renderer.particle_system = self.particle_system
            self.renderer.floating_text_system = self.floating_text_system
            
            # Generate the map
            self.world.generate_map("default")
            # Spawn kids
            self.world.spawn_kids(10)
            
            # Initialize HUD elements with possession system
            if self.world.possession_system:
                self.energy_bar.set_possession_system(self.world.possession_system)
                self.kid_info_panel.set_possession_system(self.world.possession_system)
            
            self.initialized = True
            print("Playing state initialized with map and kids")
    
    def update(self, dt):
        """Update the playing state."""
        if self.world:
            self.world.update(dt, self.renderer)
            
            # Update UI elements
            self.particle_system.update(dt)
            self.floating_text_system.update(dt)
            self.market_ticker.update(dt, self.world.economy)
            
            # Update HUD elements
            self.energy_bar.update(dt)
            self.kid_info_panel.update(dt)
            self.chaos_score.update(dt)
            
            if self.power_menu:
                self.power_menu.update(dt)
                if not self.power_menu.visible:
                    self.power_menu = None
            
            if self.trade_window:
                self.trade_window.update(dt)
                if not self.trade_window.visible:
                    self.trade_window = None
    
    def handle_event(self, event):
        """Handle input events for playing state."""
        # Handle power menu events first (highest priority)
        if self.power_menu and self.power_menu.visible and self.power_menu.handle_event(event):
            return True
        
        # Handle trade window events (second priority)
        if self.trade_window and self.trade_window.visible and self.trade_window.handle_event(event):
            return True
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                # Toggle debug overlay
                if self.renderer:
                    self.renderer.toggle_debug()
                return True
            elif event.key == pygame.K_h:
                # Toggle help overlay
                if self.renderer:
                    self.renderer.toggle_help()
                return True
            elif event.key == pygame.K_i:
                # Toggle inventory display
                if self.renderer:
                    self.renderer.toggle_inventory_display(self.world)
                return True
            elif event.key == pygame.K_e:
                # Toggle economy debug overlay
                self.economy_debug.toggle()
                return True
            elif event.key == pygame.K_t:
                # Toggle trade window (if possessing)
                if self.world and self.world.possession_system and self.world.possession_system.is_possessing():
                    if self.trade_window and self.trade_window.visible:
                        # Close trade window
                        self.trade_window.close()
                    else:
                        # Open trade window (need to select target kid via click first)
                        print("Press 'T' and then click on a kid to trade, or click a different kid while possessing")
                return True
            elif event.key == pygame.K_ESCAPE:
                # Release possession
                print("ESC key pressed - attempting to release possession")
                if self.world and self.world.possession_system:
                    if self.world.possession_system.is_possessing():
                        print("Releasing possession...")
                        self.world.release_possession()
                        print("✓ Possession released")
                    else:
                        print("Not currently possessing anyone")
                else:
                    print("No world or possession system available")
                return True
            
            # WASD movement for possessed kid
            elif event.key == pygame.K_w:
                if self.world and self.world.possession_system and self.world.possession_system.is_possessing():
                    self.world.move_possessed_kid(Vector2(0, -1))
                return True
            elif event.key == pygame.K_s:
                if self.world and self.world.possession_system and self.world.possession_system.is_possessing():
                    self.world.move_possessed_kid(Vector2(0, 1))
                return True
            elif event.key == pygame.K_a:
                if self.world and self.world.possession_system and self.world.possession_system.is_possessing():
                    self.world.move_possessed_kid(Vector2(-1, 0))
                return True
            elif event.key == pygame.K_d:
                if self.world and self.world.possession_system and self.world.possession_system.is_possessing():
                    self.world.move_possessed_kid(Vector2(1, 0))
                return True
            
            # Camera movement (panning)
            elif event.key == pygame.K_LEFT:
                if self.renderer:
                    current_pos = self.renderer.camera.position
                    new_pos = current_pos + Vector2(-100, 0)
                    self.renderer.camera.set_position(new_pos, smooth=False)
                    print(f"Camera moved LEFT to: {new_pos}")
                return True
            elif event.key == pygame.K_RIGHT:
                if self.renderer:
                    current_pos = self.renderer.camera.position
                    new_pos = current_pos + Vector2(100, 0)
                    self.renderer.camera.set_position(new_pos, smooth=False)
                    print(f"Camera moved RIGHT to: {new_pos}")
                return True
            elif event.key == pygame.K_UP:
                if self.renderer:
                    current_pos = self.renderer.camera.position
                    new_pos = current_pos + Vector2(0, -100)
                    self.renderer.camera.set_position(new_pos, smooth=False)
                    print(f"Camera moved UP to: {new_pos}")
                return True
            elif event.key == pygame.K_DOWN:
                if self.renderer:
                    current_pos = self.renderer.camera.position
                    new_pos = current_pos + Vector2(0, 100)
                    self.renderer.camera.set_position(new_pos, smooth=False)
                    print(f"Camera moved DOWN to: {new_pos}")
                return True
            
            # Camera zoom
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                if self.renderer:
                    self.renderer.camera.zoom_in(1.2)
                    print(f"Camera zoomed IN to: {self.renderer.camera.zoom}")
                return True
            elif event.key == pygame.K_MINUS:
                if self.renderer:
                    self.renderer.camera.zoom_out(1.2)
                    print(f"Camera zoomed OUT to: {self.renderer.camera.zoom}")
                return True
            
            # Reset camera to center
            elif event.key == pygame.K_r:
                if self.renderer:
                    self.renderer.camera.set_position(Vector2(1000, 1000), smooth=False)  # Center of world
                    self.renderer.camera.set_zoom(0.5, smooth=False)  # Zoomed out to see more
                    print("Camera reset to center of world")
                return True
        
        # Mouse wheel zoom
        elif event.type == pygame.MOUSEWHEEL:
            if self.renderer:
                if event.y > 0:  # Scroll up - zoom in
                    self.renderer.camera.zoom_in(1.1)
                    print(f"Mouse wheel ZOOM IN to: {self.renderer.camera.zoom}")
                else:  # Scroll down - zoom out
                    self.renderer.camera.zoom_out(1.1)
                    print(f"Mouse wheel ZOOM OUT to: {self.renderer.camera.zoom}")
            return True
        
        # Mouse click handling
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.renderer and self.world:
                    # Convert screen position to world position
                    screen_pos = Vector2(event.pos[0], event.pos[1])
                    world_pos = self.renderer.camera.screen_to_world(screen_pos)
                    
                    # Get entity at clicked position
                    entity = self.world.get_entity_at_position(world_pos)
                    
                    if entity:
                        if hasattr(entity, 'id') and entity.id.startswith('kid_'):  # It's a kid
                            # If already possessing, try to trade instead of re-possessing
                            if self.world and self.world.possession_system and self.world.possession_system.is_possessing():
                                # Check if clicking on a different kid
                                possessed_kid = self.world.possession_system.get_possessed_kid()
                                if possessed_kid and possessed_kid.id != entity.id:
                                    # Try to initiate trade with this kid
                                    print(f"Attempting to trade with kid: {entity.id}")
                                    self._initiate_trade(entity)
                                    return True
                            
                            # Try to possess the kid
                            print(f"Attempting to possess kid: {entity.id}")
                            success = self.world.try_possess_kid(entity)
                            if success:
                                print(f"✓ Successfully possessed kid: {entity.id}")
                            else:
                                possession_system = self.world.possession_system
                                if possession_system:
                                    print(f"✗ Failed to possess kid: {entity.id}")
                                    print(f"  - Energy: {possession_system.current_energy}")
                                    print(f"  - Cooldown: {possession_system.possession_cooldown}")
                                    print(f"  - Can possess: {possession_system.can_possess()}")
                                else:
                                    print(f"✗ No possession system available")
                        
                        elif hasattr(entity, 'id') and entity.id.startswith('house_'):  # It's a house
                            print(f"Clicked on house: {entity.id}")
                            # Only allow house powers when not possessing
                            if not (self.world.possession_system and self.world.possession_system.is_possessing()):
                                print(f"Showing power menu for house: {entity.id}")
                                # Show power menu
                                self._show_power_menu(event.pos[0], event.pos[1], entity.id)
                            else:
                                print("Cannot use house powers while possessing a kid")
                    
                    return True
            
            elif event.button == 3:  # Right click - release possession or initiate trade
                print("Right-click detected")
                
                # If trade window is open, close it
                if self.trade_window and self.trade_window.visible:
                    print("Closing trade window")
                    self.trade_window.close()
                    return True
                
                # If possessing a kid, try to initiate trade with clicked kid
                if self.world and self.world.possession_system and self.world.possession_system.is_possessing():
                    if self.renderer and self.world:
                        # Convert screen position to world position
                        screen_pos = Vector2(event.pos[0], event.pos[1])
                        world_pos = self.renderer.camera.screen_to_world(screen_pos)
                        
                        # Get entity at clicked position
                        entity = self.world.get_entity_at_position(world_pos)
                        
                        if entity and hasattr(entity, 'id') and entity.id.startswith('kid_'):
                            # Try to initiate trade with this kid
                            print(f"Attempting to trade with kid: {entity.id}")
                            self._initiate_trade(entity)
                            return True
                
                # Otherwise, release possession
                print("Releasing possession via right-click")
                if self.world and self.world.possession_system and self.world.possession_system.is_possessing():
                    print("Releasing possession via right-click...")
                    self.world.release_possession()
                    print("✓ Possession released via right-click")
                return True
        
        # Handle power menu events
        if self.power_menu and self.power_menu.handle_event(event):
            return True
        
        return False
    
    def _show_power_menu(self, x: int, y: int, house_id: str):
        """Show power menu for house interaction."""
        if self.power_menu:
            self.power_menu.close()
        
        from ..ui.power_menu import PowerMenu
        
        # Get current energy
        current_energy = 100
        if self.world.possession_system:
            current_energy = int(self.world.possession_system.current_energy)
        
        # Create power menu
        print(f"Creating power menu for house: {house_id} at ({x}, {y}) with energy: {current_energy}")
        self.power_menu = PowerMenu(x, y, house_id)
        self.power_menu.set_energy(current_energy)
        
        # Set callbacks
        self.power_menu.set_callbacks(
            curse_callback=self._on_curse_house,
            bless_callback=self._on_bless_house,
            close_callback=self._on_power_menu_close
        )
        print(f"Power menu created successfully: {self.power_menu}")
        
        self.power_menu.show(x, y, current_energy)
    
    def _initiate_trade(self, target_kid):
        """Initiate trade with target kid."""
        if not self.world or not self.world.possession_system:
            return
        
        possessed_kid = self.world.possession_system.get_possessed_kid()
        if not possessed_kid:
            print("No kid currently possessed")
            return
        
        print(f"Opening trade window: {possessed_kid.id} <-> {target_kid.id}")
        
        # Create trade window
        from ..ui.trade_window import TradeWindow
        self.trade_window = TradeWindow(200, 100, 600, 400)
        self.trade_window.set_kids(possessed_kid, target_kid)
        self.trade_window.set_callbacks(
            close_callback=self._on_trade_window_close,
            propose_callback=self._on_propose_trade
        )
        self.trade_window.visible = True
        self.trade_window.enabled = True
    
    def _on_trade_window_close(self):
        """Handle trade window close."""
        if self.trade_window:
            self.trade_window.visible = False
            self.trade_window = None
        print("Trade window closed")
    
    def _on_propose_trade(self, player_offer: Dict[str, int], target_offer: Dict[str, int]):
        """Handle trade proposal."""
        if not self.world or not self.world.possession_system:
            return
        
        possessed_kid = self.world.possession_system.get_possessed_kid()
        if not possessed_kid or not self.trade_window:
            return
        
        target_kid = self.trade_window.target_kid
        if not target_kid:
            return
        
        print(f"Proposing trade: {possessed_kid.id} offers {player_offer} for {target_kid.id}'s {target_offer}")
        
        # Calculate trade value (simple calculation for now)
        player_value = sum(player_offer.values())
        target_value = sum(target_offer.values())
        trade_value = target_value - player_value
        
        # Award chaos points for bad trades (negative value = bad for player)
        if trade_value < 0:
            chaos_points = abs(trade_value) * 2  # 2 chaos per candy value
            print(f"Awarding {chaos_points} chaos points for bad trade")
            self.chaos_score.add_chaos_points(chaos_points, "bad_trade")
        
        # Execute the trade (simple inventory swap)
        self._execute_trade(possessed_kid, target_kid, player_offer, target_offer)
        
        # Close trade window
        self._on_trade_window_close()
    
    def _execute_trade(self, kid1: Kid, kid2: Kid, offer1: Dict[str, int], offer2: Dict[str, int]):
        """Execute the trade between two kids."""
        if not hasattr(kid1, 'inventory') or not hasattr(kid2, 'inventory'):
            return
        
        # Remove items from inventories
        for candy_type, quantity in offer1.items():
            if candy_type in kid1.inventory:
                kid1.inventory[candy_type] = max(0, kid1.inventory[candy_type] - quantity)
        
        for candy_type, quantity in offer2.items():
            if candy_type in kid2.inventory:
                kid2.inventory[candy_type] = max(0, kid2.inventory[candy_type] - quantity)
        
        # Add items to inventories
        for candy_type, quantity in offer2.items():
            if candy_type not in kid1.inventory:
                kid1.inventory[candy_type] = 0
            kid1.inventory[candy_type] += quantity
        
        for candy_type, quantity in offer1.items():
            if candy_type not in kid2.inventory:
                kid2.inventory[candy_type] = 0
            kid2.inventory[candy_type] += quantity
        
        print(f"✓ Trade executed: {kid1.id} <-> {kid2.id}")
    
    def _on_curse_house(self, house_id: str):
        """Handle curse house action."""
        house = self.world.get_house_by_id(house_id)
        if house:
            success = self.world.try_curse_house(house)
            if success:
                print(f"Cursed house: {house_id}")
                self.chaos_score.add_chaos_points(5, "house_curse")
                # Emit curse particles
                self.particle_system.emit_curse_particles(house.position)
            else:
                print(f"Failed to curse house: {house_id} (insufficient energy)")
    
    def _on_bless_house(self, house_id: str):
        """Handle bless house action."""
        house = self.world.get_house_by_id(house_id)
        if house:
            success = self.world.try_bless_house(house)
            if success:
                print(f"Blessed house: {house_id}")
                self.chaos_score.add_chaos_points(3, "house_bless")
                # Emit bless particles
                self.particle_system.emit_bless_particles(house.position)
            else:
                print(f"Failed to bless house: {house_id} (insufficient energy)")
    
    def _on_power_menu_close(self):
        """Handle power menu close."""
        self.power_menu = None
    
    def render(self, screen):
        """Render the playing state."""
        if self.world and self.renderer:
            self.renderer.render_world(self.world)
            
            # Render UI elements
            self.particle_system.render(screen, self.renderer.camera)
            self.floating_text_system.render(screen, self.renderer.camera)
            self.market_ticker.render(screen)
            
            # Render HUD elements
            self.energy_bar.render(screen)
            self.kid_info_panel.render(screen)
            self.chaos_score.render(screen)
            
            if self.power_menu:
                self.power_menu.render(screen)
            
            # Render trade window
            if self.trade_window and self.trade_window.visible:
                self.trade_window.render(screen)
            
            # Render debug overlay
            self.economy_debug.render(screen, self.world.economy, self.world.kids, self.renderer.camera)
        else:
            # Fallback rendering
            font = pygame.font.Font(None, 36)
            text = font.render("Playing State - Initializing...", True, COLORS['GREEN'])
            text_rect = text.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2))
            screen.blit(text, text_rect)


class PausedState(BaseState):
    """Paused state (placeholder for now)."""
    
    def on_enter(self, data=None):
        print("Entered paused state")
    
    def handle_event(self, event):
        """Handle input events for paused state."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                # Resume game
                return "resume"
        return False
    
    def render(self, screen):
        # Simple placeholder rendering
        font = pygame.font.Font(None, 36)
        text = font.render("Paused - Press P to resume", True, COLORS['YELLOW'])
        text_rect = text.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2))
        screen.blit(text, text_rect)
