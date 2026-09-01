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

# Colors (high contrast, classroom-friendly)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
GREEN = (50, 255, 150)
RED = (255, 80, 80)
YELLOW = (255, 220, 50)
PURPLE = (200, 100, 255)
ORANGE = (255, 165, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (150, 200, 255)

# Fonts
FONT_XLARGE = pygame.font.Font(None, 64)
FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)
FONT_TINY = pygame.font.Font(None, 20)

class MathOverlay:
    """Shows grade-appropriate math concepts and formulas"""
    def __init__(self):
        self.visible = False
        self.title = ""
        self.lines = []
        self.standard_code = ""
    
    def set_content(self, standard_code, title, lines):
        self.standard_code = standard_code
        self.title = title
        self.lines = lines
    
    def toggle(self):
        self.visible = not self.visible
    
    def draw(self, screen):
        if not self.visible:
            return
        
        # Draw overlay panel
        panel_height = 80 + len(self.lines) * 35
        panel_rect = pygame.Rect(10, 100, 450, panel_height)
        pygame.draw.rect(screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, YELLOW, panel_rect, 3)
        
        # Standard code chip
        code_text = FONT_SMALL.render(self.standard_code, True, BLACK)
        code_rect = code_text.get_rect()
        code_bg = pygame.Rect(20, 110, code_rect.width + 20, 30)
        pygame.draw.rect(screen, YELLOW, code_bg)
        screen.blit(code_text, (30, 115))
        
        # Title
        title_text = FONT_MEDIUM.render(self.title, True, WHITE)
        screen.blit(title_text, (20, 150))
        
        # Lines
        y = 190
        for line in self.lines:
            text = FONT_SMALL.render(line, True, GREEN)
            screen.blit(text, (20, y))
            y += 35


class Scene(ABC):
    """Base class for all educational scenes"""
    def __init__(self, name):
        self.name = name
        self.overlay = MathOverlay()
        self.paused = False
        self.slow_mo = False
        self.grade = 3  # Default to grade 3
        
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
    
    def set_grade(self, grade):
        self.grade = grade
        self.reset()
    
    def draw_ui(self, screen):
        """Draw common UI elements"""
        # Scene title bar
        title_bg = pygame.Rect(0, 0, SCREEN_WIDTH, 70)
        pygame.draw.rect(screen, DARK_GRAY, title_bg)
        
        title = FONT_LARGE.render(self.name, True, WHITE)
        screen.blit(title, (20, 15))
        
        # Grade indicator
        grade_text = FONT_MEDIUM.render(f"Grade {self.grade}", True, YELLOW)
        grade_rect = grade_text.get_rect()
        grade_bg = pygame.Rect(SCREEN_WIDTH - 150, 15, 130, 40)
        pygame.draw.rect(screen, BLUE, grade_bg)
        screen.blit(grade_text, (SCREEN_WIDTH - 145, 20))
        
        # Instructions
        instructions = "TAB: Next | G: Grade | O: Overlay | S: Slow-mo | P: Pause | R: Reset"
        inst_text = FONT_TINY.render(instructions, True, GRAY)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, SCREEN_HEIGHT - 25))
        
        # Math overlay
        self.overlay.draw(screen)


class RateRacerScene(Scene):
    """Scene 1: Rate Racer & Rounding - NBT Standards"""
    def __init__(self):
        super().__init__("Rate Racer & Rounding")
        self.reset()
        
    def reset(self):
        if self.grade == 3:
            self.distance = 740  # Round to nearest 10
            self.speed = 10
            self.target_round = 10
        elif self.grade == 4:
            self.distance = 1350  # Multi-digit operations
            self.speed = 7
            self.target_round = 100
        else:  # Grade 5
            self.distance = 120
            self.speed = 8.4  # Decimals
            self.target_round = 0.1
        
        self.car_x = 100
        self.time_elapsed = 0
        self.finished = False
        self.prediction_made = False
        self.user_answer = 0
        self.input_mode = False
        self.input_text = ""
        
    def update(self, dt):
        if self.paused or self.finished:
            return
        
        actual_dt = dt * (0.3 if self.slow_mo else 1.0)
        self.time_elapsed += actual_dt
        
        # Move car based on speed
        if self.grade == 5:
            self.car_x = 100 + (self.speed * self.time_elapsed * 60 / self.distance) * 900
        else:
            self.car_x = 100 + (self.speed * self.time_elapsed * 60 / self.distance) * 900
        
        # Check if finished
        if self.car_x >= 1000:
            self.finished = True
            self.car_x = 1000
        
        # Update overlay based on grade
        if self.grade == 3:
            self.overlay.set_content(
                "3.NBT • Rounding",
                "Round to nearest 10",
                [
                    f"Time: {self.time_elapsed:.1f} seconds",
                    f"Round {int(self.time_elapsed):.0f} to nearest 10",
                    f"Look at the ones place!"
                ]
            )
        elif self.grade == 4:
            segments = [670, 680]
            total = sum(segments)
            self.overlay.set_content(
                "4.NBT • Multi-digit",
                "Add & Subtract",
                [
                    f"Segment 1: {segments[0]} m",
                    f"Segment 2: {segments[1]} m",
                    f"Total: {segments[0]} + {segments[1]} = {total} m",
                    f"Time: {self.time_elapsed:.1f} s"
                ]
            )
        else:  # Grade 5
            self.overlay.set_content(
                "5.NBT • Decimals",
                "Decimal Operations",
                [
                    f"Speed: {self.speed} m/s",
                    f"Distance: {self.distance} m",
                    f"Time = Distance ÷ Speed",
                    f"Time: {self.time_elapsed:.2f} s"
                ]
            )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw road
        pygame.draw.rect(screen, DARK_GRAY, (0, 350, SCREEN_WIDTH, 150))
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.rect(screen, YELLOW, (i, 420, 20, 5))
        
        # Draw start and finish
        pygame.draw.rect(screen, GREEN, (100, 350, 5, 150))
        pygame.draw.rect(screen, RED, (1000, 350, 5, 150))
        
        # Draw car
        pygame.draw.rect(screen, BLUE, (self.car_x - 20, 400, 40, 30))
        pygame.draw.circle(screen, BLACK, (int(self.car_x - 10), 430), 8)
        pygame.draw.circle(screen, BLACK, (int(self.car_x + 10), 430), 8)
        
        # HUD
        y = 550
        if self.grade == 3:
            info = [
                f"Distance: {self.distance} meters",
                f"Time: {self.time_elapsed:.1f} seconds",
                f"Round to nearest 10: ___"
            ]
        elif self.grade == 4:
            info = [
                f"Distance: {self.distance} meters",
                f"Speed: {self.speed} m/s",
                f"Time: {self.time_elapsed:.1f} seconds"
            ]
        else:
            info = [
                f"Distance: {self.distance} m",
                f"Speed: {self.speed} m/s",
                f"Time: {self.time_elapsed:.2f} s (decimals!)"
            ]
        
        for text in info:
            rendered = FONT_SMALL.render(text, True, WHITE)
            screen.blit(rendered, (SCREEN_WIDTH - 350, y))
            y += 30
        
        # Prediction prompt
        if self.finished and not self.prediction_made:
            prompt_rect = pygame.Rect(250, 200, 700, 200)
            pygame.draw.rect(screen, DARK_GRAY, prompt_rect)
            pygame.draw.rect(screen, YELLOW, prompt_rect, 3)
            
            if self.grade == 3:
                question = f"Round {int(self.time_elapsed)} to nearest 10:"
                answer = round(self.time_elapsed / 10) * 10
            elif self.grade == 4:
                question = f"Round {int(self.time_elapsed)} to nearest 100:"
                answer = round(self.time_elapsed / 100) * 100
            else:
                question = f"Round {self.time_elapsed:.2f} to nearest 0.1:"
                answer = round(self.time_elapsed, 1)
            
            q_text = FONT_MEDIUM.render(question, True, YELLOW)
            screen.blit(q_text, (300, 230))
            
            if self.input_mode:
                input_display = FONT_LARGE.render(self.input_text + "_", True, GREEN)
                screen.blit(input_display, (450, 290))
                hint = FONT_SMALL.render("Type answer, press ENTER", True, WHITE)
                screen.blit(hint, (420, 350))
            else:
                hint = FONT_SMALL.render("Press ENTER to answer", True, WHITE)
                screen.blit(hint, (440, 300))
        
        elif self.finished and self.prediction_made:
            result_rect = pygame.Rect(300, 200, 600, 150)
            pygame.draw.rect(screen, DARK_GRAY, result_rect)
            pygame.draw.rect(screen, GREEN, result_rect, 3)
            
            correct_text = FONT_LARGE.render("Correct! Great rounding!", True, GREEN)
            screen.blit(correct_text, (350, 250))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.finished and not self.prediction_made:
                if event.key == pygame.K_RETURN and not self.input_mode:
                    self.input_mode = True
                    self.input_text = ""
                elif self.input_mode:
                    if event.key == pygame.K_RETURN:
                        self.prediction_made = True
                        self.input_mode = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.unicode.isdigit() or event.unicode == '.':
                        self.input_text += event.unicode


class ArrayCityScene(Scene):
    """Scene 2: Array City - Area & Perimeter"""
    def __init__(self):
        super().__init__("Array City - Area & Perimeter")
        self.reset()
        
    def reset(self):
        if self.grade == 3:
            self.target_rows = 6
            self.target_cols = 4
            self.focus = "area"
        elif self.grade == 4:
            self.target_area = 48
            self.focus = "factors"
        else:  # Grade 5
            self.target_rows = 3
            self.target_cols = 2
            self.target_height = 5
            self.focus = "volume"
        
        self.rows = 1
        self.cols = 1
        self.height = 1
        self.tile_size = 40
        self.won = False
        
    def update(self, dt):
        if self.paused:
            return
        
        area = self.rows * self.cols
        perimeter = 2 * (self.rows + self.cols)
        
        # Check win condition
        if self.grade == 3:
            self.won = (self.rows == self.target_rows and self.cols == self.target_cols)
        elif self.grade == 4:
            self.won = (area == self.target_area)
        else:
            volume = self.rows * self.cols * self.height
            target_volume = self.target_rows * self.target_cols * self.target_height
            self.won = (volume == target_volume)
        
        # Update overlay
        if self.grade == 3:
            self.overlay.set_content(
                "3.MD • Area",
                "Area = rows × columns",
                [
                    f"Rows: {self.rows}",
                    f"Columns: {self.cols}",
                    f"Area: {self.rows} × {self.cols} = {area}",
                    f"Target: {self.target_rows} × {self.target_cols}"
                ]
            )
        elif self.grade == 4:
            self.overlay.set_content(
                "4.OA • Factors",
                "Find factor pairs",
                [
                    f"Area: {area}",
                    f"Perimeter: {perimeter}",
                    f"Target area: {self.target_area}",
                    f"Different rectangles, same area!"
                ]
            )
        else:
            volume = self.rows * self.cols * self.height
            self.overlay.set_content(
                "5.MD • Volume",
                "V = l × w × h",
                [
                    f"Length: {self.rows}",
                    f"Width: {self.cols}",
                    f"Height: {self.height}",
                    f"Volume: {self.rows}×{self.cols}×{self.height} = {volume}"
                ]
            )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw grid
        start_x = 500
        start_y = 250
        
        if self.grade == 5:
            # Draw 3D stacked layers
            for layer in range(self.height):
                offset_x = layer * 15
                offset_y = -layer * 15
                for r in range(self.rows):
                    for c in range(self.cols):
                        x = start_x + c * self.tile_size + offset_x
                        y = start_y + r * self.tile_size + offset_y
                        color = BLUE if layer == self.height - 1 else LIGHT_BLUE
                        pygame.draw.rect(screen, color, (x, y, self.tile_size - 2, self.tile_size - 2))
                        pygame.draw.rect(screen, WHITE, (x, y, self.tile_size - 2, self.tile_size - 2), 1)
        else:
            # Draw 2D array
            for r in range(self.rows):
                for c in range(self.cols):
                    x = start_x + c * self.tile_size
                    y = start_y + r * self.tile_size
                    pygame.draw.rect(screen, GREEN, (x, y, self.tile_size - 2, self.tile_size - 2))
                    pygame.draw.rect(screen, WHITE, (x, y, self.tile_size - 2, self.tile_size - 2), 1)
        
        # Info panel
        area = self.rows * self.cols
        perimeter = 2 * (self.rows + self.cols)
        
        info_y = 150
        if self.grade == 3:
            info = [
                f"Build: {self.target_rows} × {self.target_cols}",
                f"Current: {self.rows} × {self.cols}",
                f"Area: {area}"
            ]
        elif self.grade == 4:
            info = [
                f"Target Area: {self.target_area}",
                f"Current Area: {area}",
                f"Perimeter: {perimeter}",
                "Find factor pairs!"
            ]
        else:
            volume = self.rows * self.cols * self.height
            target_vol = self.target_rows * self.target_cols * self.target_height
            info = [
                f"Target Volume: {target_vol}",
                f"Current: {self.rows}×{self.cols}×{self.height}",
                f"Volume: {volume}"
            ]
        
        for text in info:
            rendered = FONT_SMALL.render(text, True, WHITE)
            screen.blit(rendered, (100, info_y))
            info_y += 35
        
        # Controls
        controls = [
            "Q/A: Rows",
            "W/S: Columns"
        ]
        if self.grade == 5:
            controls.append("E/D: Height")
        
        control_y = 400
        for text in controls:
            rendered = FONT_SMALL.render(text, True, YELLOW)
            screen.blit(rendered, (100, control_y))
            control_y += 30
        
        # Win message
        if self.won:
            win_rect = pygame.Rect(350, 100, 500, 100)
            pygame.draw.rect(screen, DARK_GRAY, win_rect)
            pygame.draw.rect(screen, GREEN, win_rect, 3)
            win_text = FONT_LARGE.render("SUCCESS!", True, GREEN)
            screen.blit(win_text, (500, 130))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.rows = min(10, self.rows + 1)
            elif event.key == pygame.K_a:
                self.rows = max(1, self.rows - 1)
            elif event.key == pygame.K_w:
                self.cols = min(10, self.cols + 1)
            elif event.key == pygame.K_s:
                self.cols = max(1, self.cols - 1)
            elif event.key == pygame.K_e and self.grade == 5:
                self.height = min(8, self.height + 1)
            elif event.key == pygame.K_d and self.grade == 5:
                self.height = max(1, self.height - 1)


class FractionFuelScene(Scene):
    """Scene 3: Fraction Fuel - NF Standards"""
    def __init__(self):
        super().__init__("Fraction Fuel")
        self.reset()
        
    def reset(self):
        if self.grade == 3:
            self.target = 0.5  # 1/2
            self.available_fractions = [(1, 4), (1, 4), (2, 4)]
        elif self.grade == 4:
            self.target = 0.75  # 3/4
            self.available_fractions = [(1, 4), (1, 4), (1, 4)]
        else:  # Grade 5
            self.target = 7/6
            self.available_fractions = [(1, 2), (1, 3), (1, 6)]
        
        self.current_fuel = 0
        self.used_fractions = []
        self.won = False
        
    def add_fraction(self, num, denom):
        value = num / denom
        if self.current_fuel + value <= self.target + 0.1:
            self.current_fuel += value
            self.used_fractions.append((num, denom))
            
            if abs(self.current_fuel - self.target) < 0.05:
                self.won = True
    
    def update(self, dt):
        if self.paused:
            return
        
        # Update overlay
        if self.grade == 3:
            self.overlay.set_content(
                "3.NF • Fractions",
                "Fractions on number line",
                [
                    f"Target: 1/2",
                    f"Current: {self.current_fuel:.2f}",
                    "Each piece = 1/4"
                ]
            )
        elif self.grade == 4:
            self.overlay.set_content(
                "4.NF • Add Fractions",
                "Same denominators",
                [
                    f"Target: 3/4",
                    f"1/4 + 1/4 + 1/4 = 3/4",
                    f"Current: {self.current_fuel:.2f}"
                ]
            )
        else:
            self.overlay.set_content(
                "5.NF • Unlike Denoms",
                "Add unlike denominators",
                [
                    f"Target: 7/6",
                    f"1/2 + 1/3 + 1/6 = ?",
                    f"Find common denominator!",
                    f"Current: {self.current_fuel:.3f}"
                ]
            )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw fuel tank
        tank_x = 800
        tank_y = 200
        tank_width = 100
        tank_height = 300
        
        pygame.draw.rect(screen, DARK_GRAY, (tank_x, tank_y, tank_width, tank_height), 3)
        
        # Fill level
        fill_height = min(tank_height, (self.current_fuel / self.target) * tank_height)
        fill_y = tank_y + tank_height - fill_height
        pygame.draw.rect(screen, BLUE, (tank_x + 2, fill_y, tank_width - 4, fill_height))
        
        # Target line
        target_y = tank_y + tank_height - (tank_height)
        pygame.draw.line(screen, RED, (tank_x - 10, target_y), (tank_x + tank_width + 10, target_y), 3)
        
        # Number line
        line_y = 550
        line_start = 100
        line_end = 700
        pygame.draw.line(screen, WHITE, (line_start, line_y), (line_end, line_y), 3)
        
        # Draw tick marks
        num_ticks = 7 if self.grade == 5 else 5
        for i in range(num_ticks):
            x = line_start + i * (line_end - line_start) / (num_ticks - 1)
            pygame.draw.line(screen, WHITE, (x, line_y - 10), (x, line_y + 10), 2)
        
        # Current position marker
        marker_x = line_start + (self.current_fuel / self.target) * (line_end - line_start)
        marker_x = min(line_end, max(line_start, marker_x))
        pygame.draw.circle(screen, YELLOW, (int(marker_x), line_y), 8)
        
        # Available fractions
        info_y = 150
        title = FONT_MEDIUM.render("Available Fractions:", True, WHITE)
        screen.blit(title, (100, info_y))
        info_y += 50
        
        for i, (num, denom) in enumerate(self.available_fractions):
            if i >= len(self.used_fractions):
                frac_text = FONT_LARGE.render(f"{num}/{denom}", True, GREEN)
                button_text = FONT_SMALL.render(f"Press {i+1}", True, YELLOW)
                screen.blit(frac_text, (120, info_y))
                screen.blit(button_text, (120, info_y + 45))
                info_y += 90
        
        # Stats
        stats_y = 150
        stats = [
            f"Target: {self.target:.3f}",
            f"Current: {self.current_fuel:.3f}",
            f"Pieces used: {len(self.used_fractions)}"
        ]
        for text in stats:
            rendered = FONT_SMALL.render(text, True, WHITE)
            screen.blit(rendered, (950, stats_y))
            stats_y += 35
        
        # Win message
        if self.won:
            win_rect = pygame.Rect(300, 250, 600, 150)
            pygame.draw.rect(screen, DARK_GRAY, win_rect)
            pygame.draw.rect(screen, GREEN, win_rect, 3)
            win_text = FONT_XLARGE.render("PERFECT!", True, GREEN)
            screen.blit(win_text, (420, 300))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and len(self.used_fractions) < len(self.available_fractions):
                idx = len(self.used_fractions)
                if idx < len(self.available_fractions):
                    num, denom = self.available_fractions[idx]
                    self.add_fraction(num, denom)
            elif event.key == pygame.K_2 and len(self.used_fractions) < len(self.available_fractions):
                idx = len(self.used_fractions)
                if idx < len(self.available_fractions):
                    num, denom = self.available_fractions[idx]
                    self.add_fraction(num, denom)


class DataLabScene(Scene):
    """Scene 4: Data & Line-Plot Lab"""
    def __init__(self):
        super().__init__("Data & Line-Plot Lab")
        self.reset()
        
    def reset(self):
        self.data_points = []
        self.current_trial = 0
        
        if self.grade == 3:
            self.max_trials = 5
            self.unit = "meters"
        elif self.grade == 4:
            self.max_trials = 8
            self.unit = "1/4 units"
        else:  # Grade 5
            self.max_trials = 10
            self.unit = "meters"
        
        self.won = False
        
    def add_trial(self):
        if self.current_trial >= self.max_trials:
            return
        
        if self.grade == 3:
            value = random.randint(3, 8)
        elif self.grade == 4:
            value = random.choice([2.25, 2.5, 2.75, 3.0, 3.25, 3.5])
        else:
            value = round(random.uniform(2.5, 5.5), 1)
        
        self.data_points.append(value)
        self.current_trial += 1
        
        if self.current_trial >= self.max_trials:
            self.won = True
    
    def update(self, dt):
        if self.paused:
            return
        
        # Calculate stats
        if len(self.data_points) > 0:
            avg = sum(self.data_points) / len(self.data_points)
            total = sum(self.data_points)
        else:
            avg = 0
            total = 0
        
        # Update overlay
        if self.grade == 3:
            self.overlay.set_content(
                "3.MD • Data",
                "Simple graphs",
                [
                    f"Trials: {len(self.data_points)}",
                    f"Total: {total:.1f} {self.unit}",
                    "Collect and compare!"
                ]
            )
        elif self.grade == 4:
            self.overlay.set_content(
                "4.MD • Line Plots",
                "Fractional units",
                [
                    f"Trials: {len(self.data_points)}",
                    f"Average: {avg:.2f}",
                    "Line plots with fractions!"
                ]
            )
        else:
            self.overlay.set_content(
                "5.MD • Compare Data",
                "Analyze distributions",
                [
                    f"Trials: {len(self.data_points)}",
                    f"Average: {avg:.2f}",
                    f"Total: {total:.1f}",
                    "Interpret the data!"
                ]
            )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw line plot
        plot_x = 150
        plot_y = 400
        plot_width = 900
        plot_height = 200
        
        # Axis
        pygame.draw.line(screen, WHITE, (plot_x, plot_y), (plot_x + plot_width, plot_y), 3)
        pygame.draw.line(screen, WHITE, (plot_x, plot_y - plot_height), (plot_x, plot_y), 3)
        
        # Y-axis label
        y_label = FONT_SMALL.render("Frequency", True, WHITE)
        screen.blit(y_label, (50, plot_y - 100))
        
        # X-axis label
        x_label = FONT_SMALL.render(f"Value ({self.unit})", True, WHITE)
        screen.blit(x_label, (plot_x + plot_width // 2 - 50, plot_y + 30))
        
        # Plot data
        if len(self.data_points) > 0:
            # Count frequencies
            freq_map = {}
            for value in self.data_points:
                freq_map[value] = freq_map.get(value, 0) + 1
            
            # Determine range
            if self.grade == 3:
                min_val, max_val = 0, 10
            elif self.grade == 4:
                min_val, max_val = 2.0, 4.0
            else:
                min_val, max_val = 2.0, 6.0
            
            # Draw tick marks and X's
            for value, freq in freq_map.items():
                x_pos = plot_x + ((value - min_val) / (max_val - min_val)) * plot_width
                
                # Tick mark
                pygame.draw.line(screen, WHITE, (x_pos, plot_y - 5), (x_pos, plot_y + 5), 2)
                
                # Value label
                label = FONT_TINY.render(f"{value:.1f}" if self.grade != 3 else str(int(value)), True, WHITE)
                screen.blit(label, (x_pos - 10, plot_y + 10))
                
                # Stack X's
                for i in range(freq):
                    y_pos = plot_y - 20 - (i * 20)
                    # Draw X
                    size = 8
                    pygame.draw.line(screen, RED, (x_pos - size, y_pos - size), (x_pos + size, y_pos + size), 3)
                    pygame.draw.line(screen, RED, (x_pos - size, y_pos + size), (x_pos + size, y_pos - size), 3)
        
        # Stats panel
        stats_y = 150
        stats_title = FONT_MEDIUM.render("Statistics", True, YELLOW)
        screen.blit(stats_title, (100, stats_y))
        stats_y += 50
        
        if len(self.data_points) > 0:
            avg = sum(self.data_points) / len(self.data_points)
            total = sum(self.data_points)
            stats = [
                f"Trials: {len(self.data_points)} / {self.max_trials}",
                f"Average: {avg:.2f}",
                f"Total: {total:.1f}"
            ]
        else:
            stats = [
                f"Trials: 0 / {self.max_trials}",
                "Press SPACE for trial"
            ]
        
        for text in stats:
            rendered = FONT_SMALL.render(text, True, WHITE)
            screen.blit(rendered, (100, stats_y))
            stats_y += 35
        
        # Instructions
        if not self.won:
            inst = FONT_MEDIUM.render("Press SPACE to run trial", True, YELLOW)
            screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 120))
        else:
            win_text = FONT_LARGE.render("Data collection complete!", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 120))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.add_trial()


class AngleCoordScene(Scene):
    """Scene 5: Angles & Coordinates Quest"""
    def __init__(self):
        super().__init__("Angles & Coordinates Quest")
        self.reset()
        
    def reset(self):
        if self.grade == 3:
            self.task = "shape"  # Identify shapes
            self.shapes = ["square", "triangle", "rectangle"]
            self.current_shape = 0
        elif self.grade == 4:
            self.task = "angle"  # Classify angles
            self.angles = [30, 90, 120]
            self.current_angle = 0
        else:  # Grade 5
            self.task = "coordinate"
            self.player_x = 1
            self.player_y = 1
            self.goal_x = 7
            self.goal_y = 5
        
        self.won = False
        
    def update(self, dt):
        if self.paused:
            return
        
        # Check win condition
        if self.grade == 5:
            self.won = (self.player_x == self.goal_x and self.player_y == self.goal_y)
        
        # Update overlay
        if self.grade == 3:
            self.overlay.set_content(
                "3.G • Shapes",
                "Reason about shapes",
                [
                    "Identify the shape",
                    "Count sides and angles",
                    "Look for right angles!"
                ]
            )
        elif self.grade == 4:
            angle = self.angles[self.current_angle]
            if angle < 90:
                angle_type = "Acute"
            elif angle == 90:
                angle_type = "Right"
            else:
                angle_type = "Obtuse"
            
            self.overlay.set_content(
                "4.G • Angles",
                "Classify angles",
                [
                    f"Angle: {angle}°",
                    f"Type: {angle_type}",
                    "< 90° = Acute",
                    "= 90° = Right",
                    "> 90° = Obtuse"
                ]
            )
        else:
            self.overlay.set_content(
                "5.G • Coordinates",
                "Graph ordered pairs",
                [
                    f"Player: ({self.player_x}, {self.player_y})",
                    f"Goal: ({self.goal_x}, {self.goal_y})",
                    "(x, y) = (right, up)"
                ]
            )
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        if self.grade == 3:
            # Draw shape
            center_x = SCREEN_WIDTH // 2
            center_y = 350
            size = 150
            
            shape = self.shapes[self.current_shape]
            
            if shape == "square":
                pygame.draw.rect(screen, GREEN, (center_x - size//2, center_y - size//2, size, size), 5)
                label = "Square - 4 equal sides, 4 right angles"
            elif shape == "triangle":
                points = [
                    (center_x, center_y - size),
                    (center_x - size, center_y + size//2),
                    (center_x + size, center_y + size//2)
                ]
                pygame.draw.polygon(screen, BLUE, points, 5)
                label = "Triangle - 3 sides, 3 angles"
            else:  # rectangle
                pygame.draw.rect(screen, PURPLE, (center_x - size, center_y - size//2, size*2, size), 5)
                label = "Rectangle - 4 sides, 4 right angles"
            
            label_text = FONT_MEDIUM.render(label, True, YELLOW)
            screen.blit(label_text, (SCREEN_WIDTH // 2 - label_text.get_width() // 2, 550))
            
            inst = FONT_SMALL.render("Press SPACE for next shape", True, WHITE)
            screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 150))
            
        elif self.grade == 4:
            # Draw angle
            center_x = SCREEN_WIDTH // 2
            center_y = 400
            angle = self.angles[self.current_angle]
            
            # Base line
            pygame.draw.line(screen, WHITE, (center_x - 200, center_y), (center_x + 200, center_y), 4)
            
            # Angled line
            rad = math.radians(angle)
            end_x = center_x + 200 * math.cos(rad)
            end_y = center_y - 200 * math.sin(rad)
            pygame.draw.line(screen, YELLOW, (center_x, center_y), (end_x, end_y), 4)
            
            # Arc
            arc_radius = 80
            pygame.draw.arc(screen, GREEN, (center_x - arc_radius, center_y - arc_radius, arc_radius * 2, arc_radius * 2), 0, math.radians(angle), 4)
            
            # Angle measurement
            angle_text = FONT_XLARGE.render(f"{angle}°", True, YELLOW)
            screen.blit(angle_text, (center_x + 100, center_y - 100))
            
            # Classification
            if angle < 90:
                classification = "ACUTE (< 90°)"
                color = BLUE
            elif angle == 90:
                classification = "RIGHT (= 90°)"
                color = GREEN
            else:
                classification = "OBTUSE (> 90°)"
                color = RED
            
            class_text = FONT_LARGE.render(classification, True, color)
            screen.blit(class_text, (SCREEN_WIDTH // 2 - class_text.get_width() // 2, 550))
            
            inst = FONT_SMALL.render("Press SPACE for next angle", True, WHITE)
            screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 150))
            
        else:  # Grade 5 - coordinate grid
            # Draw grid
            grid_size = 50
            grid_start_x = 300
            grid_start_y = 500
            
            # Axes
            for i in range(9):
                x = grid_start_x + i * grid_size
                pygame.draw.line(screen, DARK_GRAY, (x, grid_start_y), (x, grid_start_y - 8 * grid_size), 1)
            for i in range(9):
                y = grid_start_y - i * grid_size
                pygame.draw.line(screen, DARK_GRAY, (grid_start_x, y), (grid_start_x + 8 * grid_size, y), 1)
            
            # Main axes
            pygame.draw.line(screen, WHITE, (grid_start_x, grid_start_y), (grid_start_x + 8 * grid_size, grid_start_y), 3)
            pygame.draw.line(screen, WHITE, (grid_start_x, grid_start_y), (grid_start_x, grid_start_y - 8 * grid_size), 3)
            
            # Labels
            for i in range(9):
                label = FONT_TINY.render(str(i), True, WHITE)
                screen.blit(label, (grid_start_x + i * grid_size - 5, grid_start_y + 10))
                if i > 0:
                    screen.blit(label, (grid_start_x - 20, grid_start_y - i * grid_size + 5))
            
            # Player
            player_screen_x = grid_start_x + self.player_x * grid_size
            player_screen_y = grid_start_y - self.player_y * grid_size
            pygame.draw.circle(screen, BLUE, (player_screen_x, player_screen_y), 15)
            
            # Goal
            goal_screen_x = grid_start_x + self.goal_x * grid_size
            goal_screen_y = grid_start_y - self.goal_y * grid_size
            pygame.draw.circle(screen, GREEN, (goal_screen_x, goal_screen_y), 20, 4)
            pygame.draw.circle(screen, GREEN, (goal_screen_x, goal_screen_y), 5)
            
            # Coordinates display
            coord_text = FONT_MEDIUM.render(f"Player: ({self.player_x}, {self.player_y})", True, YELLOW)
            screen.blit(coord_text, (100, 150))
            
            goal_text = FONT_MEDIUM.render(f"Goal: ({self.goal_x}, {self.goal_y})", True, GREEN)
            screen.blit(goal_text, (100, 200))
            
            inst = FONT_SMALL.render("Arrow keys to move", True, WHITE)
            screen.blit(inst, (100, 250))
        
        # Win message
        if self.won:
            win_rect = pygame.Rect(350, 100, 500, 100)
            pygame.draw.rect(screen, DARK_GRAY, win_rect)
            pygame.draw.rect(screen, GREEN, win_rect, 3)
            win_text = FONT_LARGE.render("GOAL REACHED!", True, GREEN)
            screen.blit(win_text, (450, 130))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.grade in [3, 4]:
                if event.key == pygame.K_SPACE:
                    if self.grade == 3:
                        self.current_shape = (self.current_shape + 1) % len(self.shapes)
                    else:
                        self.current_angle = (self.current_angle + 1) % len(self.angles)
            elif self.grade == 5:
                if event.key == pygame.K_LEFT:
                    self.player_x = max(0, self.player_x - 1)
                elif event.key == pygame.K_RIGHT:
                    self.player_x = min(8, self.player_x + 1)
                elif event.key == pygame.K_UP:
                    self.player_y = min(8, self.player_y + 1)
                elif event.key == pygame.K_DOWN:
                    self.player_y = max(0, self.player_y - 1)


class SceneManager:
    """Manages all scenes and grade level"""
    def __init__(self):
        self.scenes = [
            RateRacerScene(),
            ArrayCityScene(),
            FractionFuelScene(),
            DataLabScene(),
            AngleCoordScene()
        ]
        self.current_scene_idx = 0
        self.grade = 3
        
    def get_current_scene(self):
        return self.scenes[self.current_scene_idx]
    
    def next_scene(self):
        self.current_scene_idx = (self.current_scene_idx + 1) % len(self.scenes)
        self.get_current_scene().set_grade(self.grade)
    
    def cycle_grade(self):
        self.grade = 3 if self.grade == 5 else self.grade + 1
        for scene in self.scenes:
            scene.set_grade(self.grade)
    
    def reset_current_scene(self):
        self.get_current_scene().reset()


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Math in Motion - KSDE Standards (Grades 3-5)")
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
                elif event.key == pygame.K_g:
                    scene_manager.cycle_grade()
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
