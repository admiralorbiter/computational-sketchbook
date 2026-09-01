import pygame
import math
import random
from abc import ABC, abstractmethod

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Colors (high contrast, accessible)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
GREEN = (50, 255, 150)
RED = (255, 80, 80)
YELLOW = (255, 220, 50)
PURPLE = (200, 100, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)

# Fonts
FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)

class MathOverlay:
    """Manages the math overlay that shows formulas and values"""
    def __init__(self):
        self.visible = False
        self.formulas = []
        self.variables = {}
    
    def set_content(self, formulas, variables):
        self.formulas = formulas
        self.variables = variables
    
    def toggle(self):
        self.visible = not self.visible
    
    def draw(self, screen):
        if not self.visible:
            return
        
        # Draw overlay panel
        panel_rect = pygame.Rect(10, 100, 380, 250)
        pygame.draw.rect(screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, YELLOW, panel_rect, 3)
        
        # Title
        title = FONT_MEDIUM.render("Math Overlay", True, YELLOW)
        screen.blit(title, (20, 110))
        
        # Formulas
        y = 150
        for formula in self.formulas:
            text = FONT_SMALL.render(formula, True, WHITE)
            screen.blit(text, (20, y))
            y += 30
        
        # Variables
        y += 10
        for var, value in self.variables.items():
            text = FONT_SMALL.render(f"{var} = {value:.2f}", True, GREEN)
            screen.blit(text, (20, y))
            y += 28


class Scene(ABC):
    """Base class for all scenes"""
    def __init__(self, name):
        self.name = name
        self.overlay = MathOverlay()
        self.paused = False
        self.slow_mo = False
        self.time_scale = 1.0
        
    @abstractmethod
    def reset(self):
        pass
    
    @abstractmethod
    def update(self, dt):
        pass
    
    @abstractmethod
    def draw(self, screen):
        pass
    
    @abstractmethod
    def handle_input(self, event):
        pass
    
    def draw_ui(self, screen):
        """Draw common UI elements"""
        # Scene title
        title = FONT_LARGE.render(self.name, True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
        
        # Instructions
        instructions = [
            "TAB: Next Scene | O: Math Overlay | S: Slow-mo | P: Pause | R: Reset"
        ]
        y = SCREEN_HEIGHT - 40
        for inst in instructions:
            text = FONT_SMALL.render(inst, True, GRAY)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 25
        
        # Math overlay
        self.overlay.draw(screen)


class RateRacerScene(Scene):
    """Scene A: Speed = distance / time"""
    def __init__(self):
        super().__init__("Rate Racer")
        self.car_x = 100
        self.car_y = 350
        self.velocity = 0
        self.friction = 0.02
        self.distance_traveled = 0
        self.time_elapsed = 0
        self.finish_line = 1000
        self.accelerating = False
        self.won = False
        
    def reset(self):
        self.car_x = 100
        self.velocity = 0
        self.distance_traveled = 0
        self.time_elapsed = 0
        self.won = False
        
    def update(self, dt):
        if self.paused:
            return
        
        actual_dt = dt * (0.3 if self.slow_mo else 1.0)
        self.time_elapsed += actual_dt
        
        # Acceleration
        if self.accelerating:
            self.velocity += 300 * actual_dt
        
        # Apply friction
        self.velocity *= (1 - self.friction)
        
        # Update position
        old_x = self.car_x
        self.car_x += self.velocity * actual_dt
        self.distance_traveled += abs(self.car_x - old_x)
        
        # Check win condition
        if abs(self.car_x - self.finish_line) < 20 and not self.won:
            self.won = True
        
        # Calculate current speed
        current_speed = self.velocity / 60  # Convert to m/s equivalent
        
        # Update overlay
        self.overlay.set_content(
            [
                "speed = distance / time",
                "x = x + v * dt",
                "v_next = v * (1 - friction)"
            ],
            {
                "distance": self.distance_traveled / 60,
                "time": self.time_elapsed,
                "speed": current_speed,
                "friction": self.friction * 100
            }
        )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw road
        pygame.draw.rect(screen, DARK_GRAY, (0, 300, SCREEN_WIDTH, 150))
        pygame.draw.line(screen, YELLOW, (0, 375), (SCREEN_WIDTH, 375), 3)
        
        # Draw finish line
        for i in range(0, 150, 30):
            color = WHITE if (i // 30) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (self.finish_line, 300 + i, 20, 30))
        
        # Draw car
        pygame.draw.rect(screen, RED, (self.car_x - 20, self.car_y - 15, 40, 30))
        pygame.draw.circle(screen, BLACK, (int(self.car_x - 10), int(self.car_y + 15)), 8)
        pygame.draw.circle(screen, BLACK, (int(self.car_x + 10), int(self.car_y + 15)), 8)
        
        # Draw HUD
        hud_text = [
            f"Distance: {self.distance_traveled / 60:.1f} m",
            f"Time: {self.time_elapsed:.1f} s",
            f"Speed: {self.velocity / 60:.1f} m/s",
            f"Friction: {self.friction * 100:.0f}%"
        ]
        y = 100
        for text in hud_text:
            rendered = FONT_SMALL.render(text, True, WHITE)
            screen.blit(rendered, (SCREEN_WIDTH - 250, y))
            y += 30
        
        # Instructions
        if not self.won:
            inst = FONT_MEDIUM.render("Hold SPACE to accelerate!", True, YELLOW)
            screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 100))
        else:
            win_text = FONT_LARGE.render("SUCCESS!", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 100))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.accelerating = True
            elif event.key == pygame.K_UP:
                self.friction = min(0.1, self.friction + 0.01)
            elif event.key == pygame.K_DOWN:
                self.friction = max(0, self.friction - 0.01)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.accelerating = False


class AngleBouncerScene(Scene):
    """Scene B: Angle of reflection"""
    def __init__(self):
        super().__init__("Angle Bouncer")
        self.reset()
        
    def reset(self):
        self.puck_x = 200
        self.puck_y = 350
        self.puck_vx = 200
        self.puck_vy = 150
        self.puck_radius = 15
        self.goal_x = 1000
        self.goal_y = 200
        self.goal_radius = 30
        self.bounces = 0
        self.won = False
        self.moving = False
        
    def update(self, dt):
        if self.paused or not self.moving:
            return
        
        actual_dt = dt * (0.3 if self.slow_mo else 1.0)
        
        # Update position
        self.puck_x += self.puck_vx * actual_dt
        self.puck_y += self.puck_vy * actual_dt
        
        # Bounce off walls
        if self.puck_x - self.puck_radius < 0:
            self.puck_x = self.puck_radius
            self.puck_vx = abs(self.puck_vx)
            self.bounces += 1
        elif self.puck_x + self.puck_radius > SCREEN_WIDTH:
            self.puck_x = SCREEN_WIDTH - self.puck_radius
            self.puck_vx = -abs(self.puck_vx)
            self.bounces += 1
            
        if self.puck_y - self.puck_radius < 80:
            self.puck_y = 80 + self.puck_radius
            self.puck_vy = abs(self.puck_vy)
            self.bounces += 1
        elif self.puck_y + self.puck_radius > SCREEN_HEIGHT - 80:
            self.puck_y = SCREEN_HEIGHT - 80 - self.puck_radius
            self.puck_vy = -abs(self.puck_vy)
            self.bounces += 1
        
        # Check goal
        dist_to_goal = math.sqrt((self.puck_x - self.goal_x)**2 + (self.puck_y - self.goal_y)**2)
        if dist_to_goal < self.puck_radius + self.goal_radius:
            self.won = True
            self.moving = False
        
        # Calculate angle
        angle = math.degrees(math.atan2(self.puck_vy, self.puck_vx))
        
        # Update overlay
        self.overlay.set_content(
            [
                "angle_out = angle_in",
                "When hitting wall:",
                "vx or vy flips sign"
            ],
            {
                "angle": angle,
                "vx": self.puck_vx,
                "vy": self.puck_vy,
                "bounces": self.bounces
            }
        )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw boundaries
        pygame.draw.rect(screen, WHITE, (0, 80, SCREEN_WIDTH, SCREEN_HEIGHT - 160), 3)
        
        # Draw goal
        pygame.draw.circle(screen, GREEN, (self.goal_x, self.goal_y), self.goal_radius, 3)
        pygame.draw.circle(screen, GREEN, (self.goal_x, self.goal_y), 5)
        
        # Draw puck
        pygame.draw.circle(screen, BLUE, (int(self.puck_x), int(self.puck_y)), self.puck_radius)
        
        # Draw velocity vector
        if not self.moving:
            end_x = self.puck_x + self.puck_vx * 0.3
            end_y = self.puck_y + self.puck_vy * 0.3
            pygame.draw.line(screen, YELLOW, (self.puck_x, self.puck_y), (end_x, end_y), 3)
            pygame.draw.circle(screen, YELLOW, (int(end_x), int(end_y)), 5)
        
        # HUD
        hud_text = [
            f"Bounces: {self.bounces}",
            f"Angle: {math.degrees(math.atan2(self.puck_vy, self.puck_vx)):.1f}°"
        ]
        y = 100
        for text in hud_text:
            rendered = FONT_SMALL.render(text, True, WHITE)
            screen.blit(rendered, (SCREEN_WIDTH - 250, y))
            y += 30
        
        # Instructions
        if not self.moving and not self.won:
            inst = FONT_MEDIUM.render("Arrow keys to aim, SPACE to launch!", True, YELLOW)
            screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 500))
        elif self.won:
            win_text = FONT_LARGE.render(f"SUCCESS in {self.bounces} bounces!", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 300))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.moving:
                self.moving = True
            elif event.key == pygame.K_LEFT and not self.moving:
                self.puck_vx -= 20
            elif event.key == pygame.K_RIGHT and not self.moving:
                self.puck_vx += 20
            elif event.key == pygame.K_UP and not self.moving:
                self.puck_vy -= 20
            elif event.key == pygame.K_DOWN and not self.moving:
                self.puck_vy += 20


class LootLabScene(Scene):
    """Scene C: Probability and expected value"""
    def __init__(self):
        super().__init__("Loot Lab")
        self.reset()
        
    def reset(self):
        self.common_prob = 0.70
        self.rare_prob = 0.25
        self.epic_prob = 0.05
        self.common_points = 10
        self.rare_points = 50
        self.epic_points = 200
        self.results = {"Common": 0, "Rare": 0, "Epic": 0}
        self.total_trials = 0
        self.total_points = 0
        self.last_drop = None
        self.drop_timer = 0
        
    def update(self, dt):
        if self.paused:
            return
        
        if self.drop_timer > 0:
            self.drop_timer -= dt
        
        # Calculate expected value
        expected_value = (self.common_prob * self.common_points + 
                         self.rare_prob * self.rare_points + 
                         self.epic_prob * self.epic_points)
        
        avg_points = self.total_points / max(1, self.total_trials)
        
        # Update overlay
        self.overlay.set_content(
            [
                "Expected Value =",
                "Σ (probability × points)",
                f"EV = {expected_value:.1f}"
            ],
            {
                "trials": self.total_trials,
                "avg_points": avg_points,
                "total_points": self.total_points
            }
        )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw chest
        chest_x = 300
        chest_y = 300
        pygame.draw.rect(screen, (139, 69, 19), (chest_x, chest_y, 100, 80))
        pygame.draw.rect(screen, YELLOW, (chest_x + 35, chest_y + 20, 30, 30))
        
        # Draw drop table
        table_x = 500
        table_y = 150
        pygame.draw.rect(screen, DARK_GRAY, (table_x, table_y, 300, 200))
        pygame.draw.rect(screen, WHITE, (table_x, table_y, 300, 200), 2)
        
        title = FONT_MEDIUM.render("Drop Table", True, WHITE)
        screen.blit(title, (table_x + 80, table_y + 10))
        
        drops = [
            (f"Common: {self.common_prob*100:.0f}% - {self.common_points} pts", GREEN),
            (f"Rare: {self.rare_prob*100:.0f}% - {self.rare_points} pts", BLUE),
            (f"Epic: {self.epic_prob*100:.0f}% - {self.epic_points} pts", PURPLE)
        ]
        y = table_y + 60
        for text, color in drops:
            rendered = FONT_SMALL.render(text, True, color)
            screen.blit(rendered, (table_x + 20, y))
            y += 40
        
        # Draw results
        results_x = 850
        results_y = 150
        pygame.draw.rect(screen, DARK_GRAY, (results_x, results_y, 300, 250))
        pygame.draw.rect(screen, WHITE, (results_x, results_y, 300, 250), 2)
        
        title = FONT_MEDIUM.render("Results", True, WHITE)
        screen.blit(title, (results_x + 90, results_y + 10))
        
        y = results_y + 60
        for rarity, count in self.results.items():
            text = f"{rarity}: {count}"
            rendered = FONT_SMALL.render(text, True, WHITE)
            screen.blit(rendered, (results_x + 20, y))
            y += 35
        
        # Total stats
        y += 10
        stats = [
            f"Total Trials: {self.total_trials}",
            f"Total Points: {self.total_points}",
            f"Average: {self.total_points / max(1, self.total_trials):.1f}"
        ]
        for text in stats:
            rendered = FONT_SMALL.render(text, True, YELLOW)
            screen.blit(rendered, (results_x + 20, y))
            y += 30
        
        # Show last drop
        if self.drop_timer > 0 and self.last_drop:
            drop_text = FONT_LARGE.render(self.last_drop, True, GREEN if "Common" in self.last_drop else BLUE if "Rare" in self.last_drop else PURPLE)
            screen.blit(drop_text, (chest_x - 50, chest_y - 80))
        
        # Instructions
        inst = FONT_MEDIUM.render("Press SPACE to open chest!", True, YELLOW)
        screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 500))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Roll for drop
                roll = random.random()
                if roll < self.common_prob:
                    self.results["Common"] += 1
                    self.total_points += self.common_points
                    self.last_drop = f"Common! +{self.common_points}"
                elif roll < self.common_prob + self.rare_prob:
                    self.results["Rare"] += 1
                    self.total_points += self.rare_points
                    self.last_drop = f"Rare! +{self.rare_points}"
                else:
                    self.results["Epic"] += 1
                    self.total_points += self.epic_points
                    self.last_drop = f"EPIC! +{self.epic_points}"
                
                self.total_trials += 1
                self.drop_timer = 1.5


class SlingshotScene(Scene):
    """Scene D: Projectile motion"""
    def __init__(self):
        super().__init__("Slingshot Challenge")
        self.reset()
        
    def reset(self):
        self.projectile_x = 150
        self.projectile_y = 500
        self.start_x = 150
        self.start_y = 500
        self.vx = 0
        self.vy = 0
        self.angle = 45
        self.power = 300
        self.gravity = 500
        self.target_x = 900
        self.target_y = 450
        self.target_radius = 40
        self.launched = False
        self.won = False
        self.trajectory = []
        
    def update(self, dt):
        if self.paused:
            return
        
        if self.launched:
            actual_dt = dt * (0.3 if self.slow_mo else 1.0)
            
            # Apply gravity
            self.vy += self.gravity * actual_dt
            
            # Update position
            self.projectile_x += self.vx * actual_dt
            self.projectile_y += self.vy * actual_dt
            
            # Record trajectory
            self.trajectory.append((int(self.projectile_x), int(self.projectile_y)))
            if len(self.trajectory) > 100:
                self.trajectory.pop(0)
            
            # Check collision with target
            dist = math.sqrt((self.projectile_x - self.target_x)**2 + 
                           (self.projectile_y - self.target_y)**2)
            if dist < self.target_radius:
                self.won = True
                self.launched = False
            
            # Reset if off screen
            if self.projectile_y > SCREEN_HEIGHT or self.projectile_x > SCREEN_WIDTH:
                self.launched = False
                self.projectile_x = self.start_x
                self.projectile_y = self.start_y
                self.trajectory = []
        
        # Update overlay
        rad_angle = math.radians(self.angle)
        self.overlay.set_content(
            [
                "vx = v₀ × cos(θ)",
                "vy = v₀ × sin(θ)",
                "y = y₀ + vy×t + ½g×t²"
            ],
            {
                "angle": self.angle,
                "power": self.power,
                "vx": self.power * math.cos(rad_angle),
                "vy": -self.power * math.sin(rad_angle),
                "gravity": self.gravity
            }
        )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw ground
        pygame.draw.line(screen, GREEN, (0, SCREEN_HEIGHT - 50), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 5)
        
        # Draw target
        pygame.draw.circle(screen, RED, (self.target_x, self.target_y), self.target_radius, 5)
        pygame.draw.circle(screen, RED, (self.target_x, self.target_y), 5)
        
        # Draw trajectory trail
        if len(self.trajectory) > 1:
            pygame.draw.lines(screen, YELLOW, False, self.trajectory, 2)
        
        # Draw projectile
        pygame.draw.circle(screen, BLUE, (int(self.projectile_x), int(self.projectile_y)), 10)
        
        # Draw aim line if not launched
        if not self.launched:
            rad_angle = math.radians(self.angle)
            end_x = self.start_x + math.cos(rad_angle) * self.power * 0.5
            end_y = self.start_y - math.sin(rad_angle) * self.power * 0.5
            pygame.draw.line(screen, WHITE, (self.start_x, self.start_y), 
                           (end_x, end_y), 3)
            pygame.draw.circle(screen, WHITE, (int(end_x), int(end_y)), 5)
        
        # HUD
        hud_text = [
            f"Angle: {self.angle:.0f}°",
            f"Power: {self.power:.0f}",
            f"Gravity: {self.gravity:.0f}"
        ]
        y = 100
        for text in hud_text:
            rendered = FONT_SMALL.render(text, True, WHITE)
            screen.blit(rendered, (SCREEN_WIDTH - 250, y))
            y += 30
        
        # Instructions
        if not self.launched and not self.won:
            inst = FONT_MEDIUM.render("LEFT/RIGHT: angle | UP/DOWN: power | SPACE: launch", True, YELLOW)
            screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 100))
        elif self.won:
            win_text = FONT_LARGE.render("BULLSEYE!", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 200))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.launched:
                rad_angle = math.radians(self.angle)
                self.vx = self.power * math.cos(rad_angle)
                self.vy = -self.power * math.sin(rad_angle)
                self.launched = True
                self.trajectory = []
            elif event.key == pygame.K_LEFT and not self.launched:
                self.angle = min(90, self.angle + 5)
            elif event.key == pygame.K_RIGHT and not self.launched:
                self.angle = max(0, self.angle - 5)
            elif event.key == pygame.K_UP and not self.launched:
                self.power = min(500, self.power + 20)
            elif event.key == pygame.K_DOWN and not self.launched:
                self.power = max(50, self.power - 20)


class SceneManager:
    """Manages all scenes and transitions"""
    def __init__(self):
        self.scenes = [
            RateRacerScene(),
            AngleBouncerScene(),
            LootLabScene(),
            SlingshotScene()
        ]
        self.current_scene = 0
    
    def get_current_scene(self):
        return self.scenes[self.current_scene]
    
    def next_scene(self):
        self.current_scene = (self.current_scene + 1) % len(self.scenes)
        self.scenes[self.current_scene].reset()
    
    def reset_current_scene(self):
        self.scenes[self.current_scene].reset()


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Math in Motion - Interactive Demo")
    clock = pygame.time.Clock()
    
    scene_manager = SceneManager()
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_scene = scene_manager.get_current_scene()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    scene_manager.next_scene()
                elif event.key == pygame.K_o:
                    current_scene.overlay.toggle()
                elif event.key == pygame.K_s:
                    current_scene.slow_mo = not current_scene.slow_mo
                elif event.key == pygame.K_p:
                    current_scene.paused = not current_scene.paused
                elif event.key == pygame.K_r:
                    scene_manager.reset_current_scene()
                else:
                    current_scene.handle_input(event)
            else:
                current_scene.handle_input(event)
        
        # Update and draw
        current_scene.update(dt)
        current_scene.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
