import pygame
import math
import random
from abc import ABC, abstractmethod

# Initialize Pygame
pygame.init()

# Constants - Larger screen for better visibility
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

# Colors - Bright, child-friendly palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHT_BLUE = (100, 200, 255)
BRIGHT_GREEN = (100, 255, 100)
BRIGHT_RED = (255, 100, 100)
BRIGHT_YELLOW = (255, 255, 100)
BRIGHT_PURPLE = (200, 100, 255)
BRIGHT_ORANGE = (255, 180, 50)
PINK = (255, 150, 200)
LIGHT_BLUE = (150, 200, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)

# Fonts - Larger for better readability
FONT_GIANT = pygame.font.Font(None, 72)
FONT_LARGE = pygame.font.Font(None, 56)
FONT_MEDIUM = pygame.font.Font(None, 42)
FONT_SMALL = pygame.font.Font(None, 32)
FONT_TINY = pygame.font.Font(None, 24)

class MathHelper:
    """Helper class for math concepts and visual aids"""
    def __init__(self):
        self.visible = False
        self.concept = ""
        self.examples = []
        self.current_value = 0
    
    def set_content(self, concept, examples, value=0):
        self.concept = concept
        self.examples = examples
        self.current_value = value
    
    def toggle(self):
        self.visible = not self.visible
    
    def draw(self, screen):
        if not self.visible:
            return
        
        # Draw help panel
        panel_rect = pygame.Rect(20, 120, 400, 300)
        pygame.draw.rect(screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(screen, BRIGHT_YELLOW, panel_rect, 4)
        
        # Title
        title = FONT_MEDIUM.render("Math Helper", True, BRIGHT_YELLOW)
        screen.blit(title, (30, 130))
        
        # Concept
        concept_text = FONT_SMALL.render(self.concept, True, WHITE)
        screen.blit(concept_text, (30, 180))
        
        # Examples
        y = 220
        for example in self.examples:
            text = FONT_TINY.render(example, True, BRIGHT_GREEN)
            screen.blit(text, (30, y))
            y += 30
        
        # Current value
        if self.current_value != 0:
            value_text = FONT_SMALL.render(f"Current: {self.current_value}", True, BRIGHT_BLUE)
            screen.blit(value_text, (30, y + 10))


class Scene(ABC):
    """Base class for all math scenes"""
    def __init__(self, name, grade_level):
        self.name = name
        self.grade_level = grade_level
        self.helper = MathHelper()
        self.paused = False
        self.slow_mo = False
        self.score = 0
        self.level = 1
        
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
        # Scene title with grade level
        title = FONT_LARGE.render(f"{self.name} (Grade {self.grade_level})", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
        
        # Score and level
        score_text = FONT_MEDIUM.render(f"Score: {self.score}", True, BRIGHT_YELLOW)
        screen.blit(score_text, (20, 20))
        
        level_text = FONT_MEDIUM.render(f"Level: {self.level}", True, BRIGHT_BLUE)
        screen.blit(level_text, (SCREEN_WIDTH - 150, 20))
        
        # Instructions
        instructions = [
            "TAB: Next Scene | H: Math Helper | S: Slow-mo | P: Pause | R: Reset"
        ]
        y = SCREEN_HEIGHT - 50
        for inst in instructions:
            text = FONT_SMALL.render(inst, True, GRAY)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 35
        
        # Math helper
        self.helper.draw(screen)


class MultiplicationGarden(Scene):
    """Grade 3: Multiplication facts with visual arrays"""
    def __init__(self):
        super().__init__("Multiplication Garden", 3)
        self.reset()
        
    def reset(self):
        self.rows = 3
        self.cols = 4
        self.flowers = []
        self.current_problem = None
        self.user_answer = ""
        self.correct_answer = 0
        self.feedback = ""
        self.feedback_timer = 0
        self.problems_solved = 0
        self.generate_problem()
        
    def generate_problem(self):
        # Generate multiplication problem within 12x12
        self.rows = random.randint(2, 6)
        self.cols = random.randint(2, 6)
        self.correct_answer = self.rows * self.cols
        self.current_problem = f"{self.rows} × {self.cols} = ?"
        self.user_answer = ""
        self.feedback = ""
        
        # Create flower positions
        self.flowers = []
        start_x = 200
        start_y = 200
        spacing = 60
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = start_x + col * spacing
                y = start_y + row * spacing
                color = random.choice([BRIGHT_RED, BRIGHT_YELLOW, BRIGHT_PURPLE, PINK, BRIGHT_ORANGE])
                self.flowers.append((x, y, color))
    
    def update(self, dt):
        if self.paused:
            return
        
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
        
        # Update helper
        self.helper.set_content(
            "Multiplication = Repeated Addition",
            [
                f"{self.rows} × {self.cols} means",
                f"{self.rows} groups of {self.cols}",
                f"Count the flowers to check!"
            ],
            len(self.flowers)
        )
    
    def draw(self, screen):
        screen.fill(LIGHT_BLUE)
        
        # Draw garden background
        pygame.draw.rect(screen, BRIGHT_GREEN, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        
        # Draw flowers
        for x, y, color in self.flowers:
            # Flower center
            pygame.draw.circle(screen, color, (x, y), 20)
            # Petals
            for angle in range(0, 360, 60):
                rad = math.radians(angle)
                petal_x = x + math.cos(rad) * 15
                petal_y = y + math.sin(rad) * 15
                pygame.draw.circle(screen, color, (int(petal_x), int(petal_y)), 8)
        
        # Draw problem
        problem_rect = pygame.Rect(50, 50, 400, 100)
        pygame.draw.rect(screen, WHITE, problem_rect)
        pygame.draw.rect(screen, BRIGHT_BLUE, problem_rect, 4)
        
        problem_text = FONT_LARGE.render(self.current_problem, True, BLACK)
        screen.blit(problem_text, (70, 80))
        
        # Draw answer input
        answer_rect = pygame.Rect(500, 50, 200, 100)
        pygame.draw.rect(screen, WHITE, answer_rect)
        pygame.draw.rect(screen, BRIGHT_GREEN, answer_rect, 4)
        
        answer_text = FONT_LARGE.render(self.user_answer, True, BLACK)
        screen.blit(answer_text, (520, 80))
        
        # Draw feedback
        if self.feedback:
            feedback_color = BRIGHT_GREEN if "Correct" in self.feedback else BRIGHT_RED
            feedback_text = FONT_MEDIUM.render(self.feedback, True, feedback_color)
            screen.blit(feedback_text, (750, 80))
        
        # Draw array grid
        start_x = 200
        start_y = 200
        spacing = 60
        
        # Draw grid lines
        for row in range(self.rows + 1):
            y = start_y + row * spacing
            pygame.draw.line(screen, BLACK, (start_x - 10, y - 10), 
                           (start_x + self.cols * spacing - 10, y - 10), 2)
        
        for col in range(self.cols + 1):
            x = start_x + col * spacing
            pygame.draw.line(screen, BLACK, (x - 10, start_y - 10), 
                           (x - 10, start_y + self.rows * spacing - 10), 2)
        
        # Draw count display (only show after answer is submitted)
        if self.feedback:
            count_text = FONT_MEDIUM.render(f"Total flowers: {len(self.flowers)}", True, BLACK)
            screen.blit(count_text, (200, 500))
        
        # Progress
        progress_text = FONT_SMALL.render(f"Problems solved: {self.problems_solved}", True, BLACK)
        screen.blit(progress_text, (200, 550))
        
        # Instructions
        if not self.feedback:
            inst = FONT_MEDIUM.render("Count the flowers in rows and columns!", True, BRIGHT_YELLOW)
            screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 600))
        elif "Correct" in self.feedback:
            win_text = FONT_LARGE.render("Great job! Next problem...", True, BRIGHT_GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 600))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    user_ans = int(self.user_answer)
                    if user_ans == self.correct_answer:
                        self.feedback = f"Correct! {self.rows} × {self.cols} = {self.correct_answer}"
                        self.score += 10
                        self.problems_solved += 1
                        self.feedback_timer = 3.0
                        pygame.time.wait(1500)
                        self.generate_problem()
                    else:
                        self.feedback = f"Not quite! You said {user_ans}, but {self.rows} × {self.cols} = {self.correct_answer}. Count the flowers!"
                        self.feedback_timer = 4.0
                except ValueError:
                    self.feedback = "Please enter a number!"
                    self.feedback_timer = 2.0
            elif event.key == pygame.K_BACKSPACE:
                self.user_answer = self.user_answer[:-1]
            elif event.unicode.isdigit():
                self.user_answer += event.unicode


class FractionPizza(Scene):
    """Grade 3-4: Fractions on number lines and visual representation"""
    def __init__(self):
        super().__init__("Fraction Pizza", 3)
        self.reset()
        
    def reset(self):
        self.pizza_slices = 8
        self.selected_slices = 0
        self.target_fraction = None
        self.current_fraction = 0
        self.feedback = ""
        self.feedback_timer = 0
        self.correct_answers = 0
        self.generate_target()
        
    def generate_target(self):
        # Generate a target fraction
        numerator = random.randint(1, self.pizza_slices - 1)
        self.target_fraction = numerator / self.pizza_slices
        self.selected_slices = 0
        self.current_fraction = 0
        self.feedback = ""
        
    def update(self, dt):
        if self.paused:
            return
        
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
        
        self.current_fraction = self.selected_slices / self.pizza_slices
        
        # Update helper
        self.helper.set_content(
            "Fractions = Parts of a Whole",
            [
                f"Pizza has {self.pizza_slices} slices",
                f"Selected: {self.selected_slices} slices",
                f"Fraction: {self.selected_slices}/{self.pizza_slices}",
                f"Decimal: {self.current_fraction:.2f}"
            ],
            self.current_fraction
        )
    
    def draw(self, screen):
        screen.fill(LIGHT_BLUE)
        
        # Draw pizza
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - 50
        radius = 200
        
        # Pizza base
        pygame.draw.circle(screen, (255, 200, 100), (center_x, center_y), radius)
        pygame.draw.circle(screen, BLACK, (center_x, center_y), radius, 4)
        
        # Draw slices
        slice_angle = 360 / self.pizza_slices
        for i in range(self.pizza_slices):
            start_angle = math.radians(i * slice_angle)
            end_angle = math.radians((i + 1) * slice_angle)
            
            # Calculate slice points
            points = [(center_x, center_y)]
            for angle in [start_angle, end_angle]:
                x = center_x + math.cos(angle) * radius
                y = center_y + math.sin(angle) * radius
                points.append((x, y))
            
            # Color based on selection
            if i < self.selected_slices:
                color = BRIGHT_GREEN
            else:
                color = (200, 150, 50)
            
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, BLACK, points, 2)
        
        # Draw target
        target_rect = pygame.Rect(50, 50, 300, 100)
        pygame.draw.rect(screen, WHITE, target_rect)
        pygame.draw.rect(screen, BRIGHT_BLUE, target_rect, 4)
        
        target_text = FONT_MEDIUM.render(f"Make: {self.target_fraction:.2f}", True, BLACK)
        screen.blit(target_text, (70, 80))
        
        # Draw current fraction
        current_rect = pygame.Rect(400, 50, 300, 100)
        pygame.draw.rect(screen, WHITE, current_rect)
        pygame.draw.rect(screen, BRIGHT_GREEN, current_rect, 4)
        
        current_text = FONT_MEDIUM.render(f"Current: {self.current_fraction:.2f}", True, BLACK)
        screen.blit(current_text, (420, 80))
        
        # Draw number line
        line_start = 100
        line_end = 700
        line_y = 600
        
        pygame.draw.line(screen, BLACK, (line_start, line_y), (line_end, line_y), 4)
        
        # Draw fraction markers
        for i in range(self.pizza_slices + 1):
            x = line_start + (line_end - line_start) * i / self.pizza_slices
            pygame.draw.line(screen, BLACK, (x, line_y - 10), (x, line_y + 10), 2)
            fraction_text = FONT_TINY.render(f"{i}/{self.pizza_slices}", True, BLACK)
            screen.blit(fraction_text, (x - 20, line_y + 15))
        
        # Draw current position
        current_x = line_start + (line_end - line_start) * self.current_fraction
        pygame.draw.circle(screen, BRIGHT_RED, (int(current_x), line_y), 8)
        
        # Check if correct
        if abs(self.current_fraction - self.target_fraction) < 0.01:
            if self.feedback_timer <= 0:
                self.feedback = "Perfect! Great job!"
                self.score += 15
                self.correct_answers += 1
                self.feedback_timer = 2.0
                pygame.time.wait(1000)
                self.generate_target()
        
        # Draw feedback
        if self.feedback:
            feedback_color = BRIGHT_GREEN if "Perfect" in self.feedback else BRIGHT_RED
            feedback_text = FONT_MEDIUM.render(self.feedback, True, feedback_color)
            screen.blit(feedback_text, (750, 80))
        
        # Instructions
        inst_text = FONT_SMALL.render("Click to add/remove slices", True, BLACK)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 700))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2 - 50
            
            # Check if click is on pizza
            dist = math.sqrt((mouse_x - center_x)**2 + (mouse_y - center_y)**2)
            if dist < 200:
                # Determine which slice was clicked
                angle = math.atan2(mouse_y - center_y, mouse_x - center_x)
                if angle < 0:
                    angle += 2 * math.pi
                
                slice_index = int(angle / (2 * math.pi / self.pizza_slices))
                
                if slice_index < self.selected_slices:
                    self.selected_slices -= 1
                else:
                    self.selected_slices += 1


class PlaceValueCastle(Scene):
    """Grade 3-4: Place value with visual blocks"""
    def __init__(self):
        super().__init__("Place Value Castle", 3)
        self.reset()
        
    def reset(self):
        self.target_number = random.randint(100, 9999)
        self.ones = 0
        self.tens = 0
        self.hundreds = 0
        self.thousands = 0
        self.current_number = 0
        self.feedback = ""
        self.feedback_timer = 0
        self.correct_answers = 0
        
    def update(self, dt):
        if self.paused:
            return
        
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
        
        self.current_number = (self.thousands * 1000 + 
                             self.hundreds * 100 + 
                             self.tens * 10 + 
                             self.ones)
        
        # Update helper
        self.helper.set_content(
            "Place Value = Position Matters",
            [
                f"Thousands: {self.thousands} × 1000 = {self.thousands * 1000}",
                f"Hundreds: {self.hundreds} × 100 = {self.hundreds * 100}",
                f"Tens: {self.tens} × 10 = {self.tens * 10}",
                f"Ones: {self.ones} × 1 = {self.ones}",
                f"Total: {self.current_number}"
            ],
            self.current_number
        )
        
        # Check if correct
        if self.current_number == self.target_number:
            if self.feedback_timer <= 0:
                self.feedback = "Excellent! Perfect place value!"
                self.score += 20
                self.correct_answers += 1
                self.feedback_timer = 2.0
                pygame.time.wait(1000)
                self.reset()
    
    def draw(self, screen):
        screen.fill(LIGHT_BLUE)
        
        # Draw castle background
        castle_rect = pygame.Rect(100, 200, 1000, 400)
        pygame.draw.rect(screen, GRAY, castle_rect)
        pygame.draw.rect(screen, BLACK, castle_rect, 4)
        
        # Draw towers
        for i in range(5):
            tower_x = 120 + i * 200
            tower_rect = pygame.Rect(tower_x, 150, 60, 250)
            pygame.draw.rect(screen, DARK_GRAY, tower_rect)
            pygame.draw.rect(screen, BLACK, tower_rect, 3)
        
        # Draw place value columns
        place_values = [
            ("Thousands", self.thousands, 0, BRIGHT_PURPLE),
            ("Hundreds", self.hundreds, 1, BRIGHT_BLUE),
            ("Tens", self.tens, 2, BRIGHT_GREEN),
            ("Ones", self.ones, 3, BRIGHT_YELLOW)
        ]
        
        for label, value, col, color in place_values:
            x = 150 + col * 200
            y = 300
            
            # Draw column header
            header_text = FONT_SMALL.render(label, True, BLACK)
            screen.blit(header_text, (x - 30, y - 50))
            
            # Draw blocks
            for i in range(value):
                block_y = y + i * 30
                pygame.draw.rect(screen, color, (x, block_y, 40, 25))
                pygame.draw.rect(screen, BLACK, (x, block_y, 40, 25), 2)
            
            # Draw value
            value_text = FONT_MEDIUM.render(str(value), True, BLACK)
            screen.blit(value_text, (x + 50, y + 100))
        
        # Draw target number
        target_rect = pygame.Rect(50, 50, 300, 100)
        pygame.draw.rect(screen, WHITE, target_rect)
        pygame.draw.rect(screen, BRIGHT_RED, target_rect, 4)
        
        target_text = FONT_LARGE.render(f"Build: {self.target_number}", True, BLACK)
        screen.blit(target_text, (70, 80))
        
        # Draw current number
        current_rect = pygame.Rect(400, 50, 300, 100)
        pygame.draw.rect(screen, WHITE, current_rect)
        pygame.draw.rect(screen, BRIGHT_GREEN, current_rect, 4)
        
        current_text = FONT_LARGE.render(f"Current: {self.current_number}", True, BLACK)
        screen.blit(current_text, (420, 80))
        
        # Draw feedback
        if self.feedback:
            feedback_color = BRIGHT_GREEN if "Excellent" in self.feedback else BRIGHT_RED
            feedback_text = FONT_MEDIUM.render(self.feedback, True, feedback_color)
            screen.blit(feedback_text, (750, 80))
        
        # Instructions
        inst_text = FONT_SMALL.render("Arrow keys to change place values", True, BLACK)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 650))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if pygame.key.get_pressed()[pygame.K_1]:
                    self.ones = min(9, self.ones + 1)
                elif pygame.key.get_pressed()[pygame.K_2]:
                    self.tens = min(9, self.tens + 1)
                elif pygame.key.get_pressed()[pygame.K_3]:
                    self.hundreds = min(9, self.hundreds + 1)
                elif pygame.key.get_pressed()[pygame.K_4]:
                    self.thousands = min(9, self.thousands + 1)
            elif event.key == pygame.K_DOWN:
                if pygame.key.get_pressed()[pygame.K_1]:
                    self.ones = max(0, self.ones - 1)
                elif pygame.key.get_pressed()[pygame.K_2]:
                    self.tens = max(0, self.tens - 1)
                elif pygame.key.get_pressed()[pygame.K_3]:
                    self.hundreds = max(0, self.hundreds - 1)
                elif pygame.key.get_pressed()[pygame.K_4]:
                    self.thousands = max(0, self.thousands - 1)


class DecimalDiner(Scene):
    """Grade 4-5: Decimal operations with money"""
    def __init__(self):
        super().__init__("Decimal Diner", 4)
        self.reset()
        
    def reset(self):
        self.menu_items = [
            ("Burger", 4.99),
            ("Fries", 2.50),
            ("Drink", 1.75),
            ("Salad", 3.25),
            ("Pizza", 6.00)
        ]
        self.order = []
        self.total = 0.0
        self.money_given = 0.0
        self.change = 0.0
        self.feedback = ""
        self.feedback_timer = 0
        self.orders_completed = 0
        
    def update(self, dt):
        if self.paused:
            return
        
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
        
        # Calculate total
        self.total = sum(item[1] for item in self.order)
        self.change = self.money_given - self.total
        
        # Update helper
        self.helper.set_content(
            "Decimals = Money Math",
            [
                f"Order total: ${self.total:.2f}",
                f"Money given: ${self.money_given:.2f}",
                f"Change: ${self.change:.2f}",
                "Add items with number keys!"
            ],
            self.total
        )
    
    def draw(self, screen):
        screen.fill(LIGHT_BLUE)
        
        # Draw diner background
        pygame.draw.rect(screen, BRIGHT_ORANGE, (0, 0, SCREEN_WIDTH, 200))
        pygame.draw.rect(screen, BRIGHT_GREEN, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        
        # Draw menu
        menu_rect = pygame.Rect(50, 250, 300, 400)
        pygame.draw.rect(screen, WHITE, menu_rect)
        pygame.draw.rect(screen, BLACK, menu_rect, 4)
        
        menu_title = FONT_MEDIUM.render("MENU", True, BLACK)
        screen.blit(menu_title, (150, 270))
        
        y = 320
        for i, (item, price) in enumerate(self.menu_items):
            item_text = FONT_SMALL.render(f"{i+1}. {item}: ${price:.2f}", True, BLACK)
            screen.blit(item_text, (70, y))
            y += 40
        
        # Draw order
        order_rect = pygame.Rect(400, 250, 400, 300)
        pygame.draw.rect(screen, WHITE, order_rect)
        pygame.draw.rect(screen, BRIGHT_BLUE, order_rect, 4)
        
        order_title = FONT_MEDIUM.render("YOUR ORDER", True, BLACK)
        screen.blit(order_title, (500, 270))
        
        y = 320
        for item, price in self.order:
            item_text = FONT_SMALL.render(f"{item}: ${price:.2f}", True, BLACK)
            screen.blit(item_text, (420, y))
            y += 30
        
        # Draw total
        total_text = FONT_MEDIUM.render(f"Total: ${self.total:.2f}", True, BRIGHT_RED)
        screen.blit(total_text, (420, 450))
        
        # Draw money input
        money_rect = pygame.Rect(850, 250, 200, 100)
        pygame.draw.rect(screen, WHITE, money_rect)
        pygame.draw.rect(screen, BRIGHT_GREEN, money_rect, 4)
        
        money_text = FONT_MEDIUM.render(f"${self.money_given:.2f}", True, BLACK)
        screen.blit(money_text, (870, 280))
        
        # Draw change
        change_rect = pygame.Rect(850, 370, 200, 100)
        pygame.draw.rect(screen, WHITE, change_rect)
        pygame.draw.rect(screen, BRIGHT_YELLOW, change_rect, 4)
        
        change_text = FONT_MEDIUM.render(f"Change: ${self.change:.2f}", True, BLACK)
        screen.blit(change_text, (860, 400))
        
        # Draw feedback
        if self.feedback:
            feedback_color = BRIGHT_GREEN if "Correct" in self.feedback else BRIGHT_RED
            feedback_text = FONT_MEDIUM.render(self.feedback, True, feedback_color)
            screen.blit(feedback_text, (500, 500))
        
        # Instructions
        inst_text = FONT_SMALL.render("1-5: Add items | +: Add money | ENTER: Complete order", True, BLACK)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 600))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.order.append(self.menu_items[0])
            elif event.key == pygame.K_2:
                self.order.append(self.menu_items[1])
            elif event.key == pygame.K_3:
                self.order.append(self.menu_items[2])
            elif event.key == pygame.K_4:
                self.order.append(self.menu_items[3])
            elif event.key == pygame.K_5:
                self.order.append(self.menu_items[4])
            elif event.key == pygame.K_PLUS:
                self.money_given += 1.0
            elif event.key == pygame.K_RETURN:
                if self.money_given >= self.total:
                    self.feedback = "Correct change! Order complete!"
                    self.score += 25
                    self.orders_completed += 1
                    self.feedback_timer = 2.0
                    pygame.time.wait(1000)
                    self.reset()
                else:
                    self.feedback = f"Need ${self.total - self.money_given:.2f} more!"
                    self.feedback_timer = 2.0


class VolumeVault(Scene):
    """Grade 5: Volume calculations with 3D shapes"""
    def __init__(self):
        super().__init__("Volume Vault", 5)
        self.reset()
        
    def reset(self):
        self.shape_type = "cube"
        self.length = 3
        self.width = 3
        self.height = 3
        self.volume = 0
        self.target_volume = random.randint(50, 200)
        self.feedback = ""
        self.feedback_timer = 0
        self.correct_answers = 0
        
    def update(self, dt):
        if self.paused:
            return
        
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
        
        # Calculate volume
        if self.shape_type == "cube":
            self.volume = self.length ** 3
        elif self.shape_type == "rectangular_prism":
            self.volume = self.length * self.width * self.height
        
        # Update helper
        if self.shape_type == "cube":
            formula = f"Volume = side³ = {self.length}³ = {self.volume}"
        else:
            formula = f"Volume = l × w × h = {self.length} × {self.width} × {self.height} = {self.volume}"
        
        self.helper.set_content(
            "Volume = Space Inside",
            [
                f"Shape: {self.shape_type}",
                formula,
                f"Target: {self.target_volume}",
                "Use arrow keys to adjust!"
            ],
            self.volume
        )
        
        # Check if correct
        if abs(self.volume - self.target_volume) <= 5:
            if self.feedback_timer <= 0:
                self.feedback = "Perfect volume! Great job!"
                self.score += 30
                self.correct_answers += 1
                self.feedback_timer = 2.0
                pygame.time.wait(1000)
                self.reset()
    
    def draw(self, screen):
        screen.fill(LIGHT_BLUE)
        
        # Draw 3D cube visualization
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Draw cube faces
        size = min(self.length, self.width, self.height) * 20
        
        # Front face
        front_points = [
            (center_x - size//2, center_y - size//2),
            (center_x + size//2, center_y - size//2),
            (center_x + size//2, center_y + size//2),
            (center_x - size//2, center_y + size//2)
        ]
        pygame.draw.polygon(screen, BRIGHT_BLUE, front_points)
        pygame.draw.polygon(screen, BLACK, front_points, 3)
        
        # Top face
        top_points = [
            (center_x - size//2, center_y - size//2),
            (center_x + size//2, center_y - size//2),
            (center_x + size//2 - 20, center_y - size//2 - 20),
            (center_x - size//2 - 20, center_y - size//2 - 20)
        ]
        pygame.draw.polygon(screen, BRIGHT_GREEN, top_points)
        pygame.draw.polygon(screen, BLACK, top_points, 3)
        
        # Right face
        right_points = [
            (center_x + size//2, center_y - size//2),
            (center_x + size//2, center_y + size//2),
            (center_x + size//2 - 20, center_y + size//2 - 20),
            (center_x + size//2 - 20, center_y - size//2 - 20)
        ]
        pygame.draw.polygon(screen, BRIGHT_RED, right_points)
        pygame.draw.polygon(screen, BLACK, right_points, 3)
        
        # Draw controls
        controls_rect = pygame.Rect(50, 50, 300, 200)
        pygame.draw.rect(screen, WHITE, controls_rect)
        pygame.draw.rect(screen, BLACK, controls_rect, 4)
        
        controls_title = FONT_MEDIUM.render("DIMENSIONS", True, BLACK)
        screen.blit(controls_title, (120, 70))
        
        length_text = FONT_SMALL.render(f"Length: {self.length}", True, BLACK)
        screen.blit(length_text, (70, 110))
        
        width_text = FONT_SMALL.render(f"Width: {self.width}", True, BLACK)
        screen.blit(width_text, (70, 140))
        
        height_text = FONT_SMALL.render(f"Height: {self.height}", True, BLACK)
        screen.blit(height_text, (70, 170))
        
        # Draw target and current
        target_rect = pygame.Rect(400, 50, 300, 100)
        pygame.draw.rect(screen, WHITE, target_rect)
        pygame.draw.rect(screen, BRIGHT_RED, target_rect, 4)
        
        target_text = FONT_MEDIUM.render(f"Target: {self.target_volume}", True, BLACK)
        screen.blit(target_text, (420, 80))
        
        current_rect = pygame.Rect(750, 50, 300, 100)
        pygame.draw.rect(screen, WHITE, current_rect)
        pygame.draw.rect(screen, BRIGHT_GREEN, current_rect, 4)
        
        current_text = FONT_MEDIUM.render(f"Current: {self.volume}", True, BLACK)
        screen.blit(current_text, (770, 80))
        
        # Draw feedback
        if self.feedback:
            feedback_color = BRIGHT_GREEN if "Perfect" in self.feedback else BRIGHT_RED
            feedback_text = FONT_MEDIUM.render(self.feedback, True, feedback_color)
            screen.blit(feedback_text, (500, 200))
        
        # Instructions
        inst_text = FONT_SMALL.render("Arrow keys to adjust dimensions | C: Change shape", True, BLACK)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 600))
        
        self.draw_ui(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.length = max(1, self.length - 1)
            elif event.key == pygame.K_RIGHT:
                self.length = min(10, self.length + 1)
            elif event.key == pygame.K_UP:
                self.height = max(1, self.height - 1)
            elif event.key == pygame.K_DOWN:
                self.height = min(10, self.height + 1)
            elif event.key == pygame.K_c:
                self.shape_type = "rectangular_prism" if self.shape_type == "cube" else "cube"


class SceneManager:
    """Manages all math scenes and transitions"""
    def __init__(self):
        self.scenes = [
            MultiplicationGarden(),
            FractionPizza(),
            PlaceValueCastle(),
            DecimalDiner(),
            VolumeVault()
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
    pygame.display.set_caption("Elementary Math Adventure - Grades 3-5")
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
                elif event.key == pygame.K_h:
                    current_scene.helper.toggle()
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
