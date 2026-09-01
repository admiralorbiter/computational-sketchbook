import math
import random
from fractions import Fraction

import pygame

# ============================================================
# Math in Motion — KSDE 3–5 (No external assets, one file)
# Scenes:
#   1) Rate Racer & Rounding           (3.NBT, 4.NBT, 5.NBT)
#   2) Array City (Area/Perim/Volume)  (3.MD/3.OA.7, 4.OA/4.MD, 5.MD)
#   3) Fraction Fuel                   (3.NF, 4.NF, 5.NF)
#   4) Data & Line-Plot Lab            (3.MD, 4.MD, 5.MD)
#   5) Angles & Coordinates Quest      (3.G, 4.G, 5.G)
#
# Global Controls:
#   Tab / Shift+Tab = Next/Prev Scene
#   G = Grade Toggle (3→4→5)
#   O = Toggle Math Overlay
#   S = Slow-mo (hold)
#   P = Pause
#   R = Reset Scene
#
# Designed for a 5–10 minute classroom demo with live "Grade" toggles.
# ============================================================

pygame.init()
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math in Motion — KSDE 3–5")
clock = pygame.time.Clock()

# ---------------- Colors & Fonts ----------------
BG = (18, 22, 33)
PANEL = (28, 32, 45)
ACCENT = (94, 198, 255)
WHITE = (240, 240, 240)
GRAY = (150, 158, 175)
GREEN = (80, 200, 120)
RED = (230, 90, 90)
YELLOW = (255, 210, 60)
PURPLE = (170, 140, 255)
CYAN = (120, 230, 230)
ORANGE = (255, 150, 60)
DARK = (12, 15, 23)

FONT = pygame.font.SysFont("arial", 22)
SMALL = pygame.font.SysFont("arial", 18)
BIG = pygame.font.SysFont("arial", 28)

# ---------------- Helpers ----------------
def draw_text(surface, text, pos, color=WHITE, font=FONT):
    img = font.render(text, True, color)
    surface.blit(img, pos)

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def round_to_nearest(n, base):
    # Proper 1/2 up rounding for positive n
    return int(base * round(float(n) / base))

def draw_header(scene_name, std_tag, grade, overlay_on):
    # Top bar
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 50))
    draw_text(screen, f"{scene_name}", (14, 12), WHITE, BIG)
    draw_text(screen, f"Grade: {grade}", (WIDTH//2 - 60, 14), ACCENT, FONT)
    draw_text(screen, f"{std_tag}", (WIDTH - 320, 14), GRAY, FONT)
    # Overlay indicator
    if overlay_on:
        pygame.draw.circle(screen, ACCENT, (WIDTH - 20, 25), 6)

def draw_footer(scene_controls):
    # Bottom strip
    pygame.draw.rect(screen, PANEL, (0, HEIGHT - 40, WIDTH, 40))
    draw_text(screen, scene_controls, (12, HEIGHT - 30), GRAY, SMALL)
    draw_text(screen, "Tab/Shift+Tab Next/Prev • G Grade • O Overlay • S Slow-mo • P Pause • R Reset",
              (WIDTH - 710, HEIGHT - 30), GRAY, SMALL)

def draw_overlay(lines):
    # Left overlay panel
    w = 420
    h = min(260, 24 + 26 * len(lines))
    pygame.draw.rect(screen, PANEL, (10, 60, w, h), border_radius=8)
    pygame.draw.rect(screen, ACCENT, (10, 60, w, h), width=2, border_radius=8)
    for i, line in enumerate(lines):
        draw_text(screen, line, (24, 72 + i * 26), WHITE, SMALL)

def draw_grid(origin=(60, 90), step=40, cols=20, rows=12, color=(40, 45, 60)):
    ox, oy = origin
    for c in range(cols + 1):
        x = ox + c * step
        pygame.draw.line(screen, color, (x, oy), (x, oy + rows * step))
    for r in range(rows + 1):
        y = oy + r * step
        pygame.draw.line(screen, color, (ox, y), (ox + cols * step, y))

# ---------------- Grade & Scene Base ----------------
GRADE_LEVELS = [3, 4, 5]

class Scene:
    name = "Base"
    std_tag = ""

    def __init__(self, grade=3):
        self.grade = grade
        self.overlay_on = True
        self.paused = False
        self.slowmo = False

    def set_grade(self, g):
        self.grade = g
        self.reset()

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass

    def reset(self):
        pass

    def overlay_lines(self):
        return []

    def controls_hint(self):
        return ""

# ============================================================
# Scene 1 — Rate Racer & Rounding
# ============================================================
class RateRacer(Scene):
    name = "Rate Racer & Rounding"
    std_map = {3: "3.NBT (rounding) • +/− within 1000",
               4: "4.NBT.4–6 (multi-digit +/− × ÷)",
               5: "5.NBT (decimals place value & ops)"}

    def __init__(self, grade=3):
        super().__init__(grade)
        self.reset()

    def reset(self):
        self.running = False
        self.elapsed = 0.0
        self.position = 0.0

        # Grade-specific course/speeds
        if self.grade == 3:
            self.course = 740  # meters
            self.speed = 8.0   # m/s
            self.round_base = 10
        elif self.grade == 4:
            self.course = 1350
            self.speed = 9.0
            self.round_base = 1  # exact shown
        else:
            self.course = 120.0
            self.speed = 8.40    # decimal m/s
            self.round_base = 0.01  # hundredth

        self.start_speed = self.speed
        self.friction = 0.00   # 0..1 per second (scaled)
        self.finish_time = None
        self.finish_time_rounded = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.running:
                self.running = True
                self.elapsed = 0.0
                self.position = 0.0
                self.speed = self.start_speed
            elif event.key == pygame.K_r:
                self.reset()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        # Adjust speed / friction
        if not self.running:
            if keys[pygame.K_a]:
                self.start_speed = max(0.1, self.start_speed - 0.1)
            if keys[pygame.K_d]:
                self.start_speed = min(50.0, self.start_speed + 0.1)
            if keys[pygame.K_w]:
                self.friction = min(0.9, self.friction + 0.01)
            if keys[pygame.K_s]:
                self.friction = max(0.0, self.friction - 0.01)

        if self.running and self.finish_time is None and not self.paused:
            # Friction reduces speed a little each second
            self.speed *= (1.0 - self.friction * dt)
            self.position += self.speed * dt
            self.elapsed += dt
            if self.position >= self.course:
                self.position = self.course
                self.running = False
                self.finish_time = self.elapsed
                # Rounding by grade
                if self.grade == 3:
                    self.finish_time_rounded = round_to_nearest(self.finish_time, self.round_base)
                elif self.grade == 4:
                    self.finish_time_rounded = self.finish_time  # show exact
                else:
                    # round to hundredths
                    self.finish_time_rounded = round(self.finish_time / self.round_base) * self.round_base

        # Smol clamp
        self.start_speed = clamp(self.start_speed, 0.1, 50.0)

    def draw_track(self):
        # Track area
        top = 120
        h = 160
        pygame.draw.rect(screen, (30, 35, 52), (60, top, WIDTH-120, h), border_radius=12)
        # Finish line
        fx = 60 + (WIDTH-120) * (self.course / self.course)
        pygame.draw.rect(screen, WHITE, (fx-6, top, 3, h))
        pygame.draw.rect(screen, WHITE, (fx+6, top, 3, h))
        # Progress car
        px = 60 + (WIDTH-120) * (self.position / self.course)
        pygame.draw.circle(screen, GREEN, (int(px), top + h//2), 14)
        draw_text(screen, "Start", (66, top + h + 10), GRAY, SMALL)
        draw_text(screen, "Finish", (WIDTH-110, top + h + 10), GRAY, SMALL)

    def overlay_lines(self):
        lines = []
        if self.grade == 3:
            lines = [
                "3.NBT — Rounding & place value:",
                "time ≈ round_to_nearest(time, 10)",
                "x = x + speed × Δt   (rate × time)",
                f"Example: round({int(self.elapsed)}s) → nearest 10"
            ]
        elif self.grade == 4:
            lines = [
                "4.NBT — Multi-digit +/−, ×, ÷:",
                "distance = laps × lap_length  (×)",
                "leftover = distance ÷ speed (remainder)",
                "Add/Sub split times for total"
            ]
        else:
            lines = [
                "5.NBT — Decimals & place value:",
                "time = distance ÷ speed",
                "Round to hundredths (two decimals)",
                "place value: tenths ● hundredths"
            ]
        return lines

    def controls_hint(self):
        return "SPACE Start • A/D Speed • W/S Friction • R Reset"

    def draw(self):
        # Info
        draw_text(screen, f"Course: {self.course} m", (60, 60), WHITE, FONT)
        draw_text(screen, f"Speed: {self.start_speed:.2f} m/s (friction {self.friction:.2f}/s)", (60, 86), GRAY, SMALL)
        self.draw_track()

        # Timing
        if self.finish_time is None:
            draw_text(screen, f"Elapsed: {self.elapsed:0.2f} s", (60, 310), WHITE, FONT)
        else:
            draw_text(screen, f"Finish time: {self.finish_time:0.2f} s", (60, 310), WHITE, FONT)
            if self.grade == 3:
                draw_text(screen, f"Rounded (nearest 10): {round_to_nearest(self.finish_time, 10)} s",
                          (60, 340), YELLOW, FONT)
            elif self.grade == 5:
                draw_text(screen, f"Rounded (hundredths): {self.finish_time_rounded:0.2f} s",
                          (60, 340), YELLOW, FONT)


# ============================================================
# Scene 2 — Array City (Area & Perimeter/Volume)
# ============================================================
class ArrayCity(Scene):
    name = "Array City — Area, Perimeter & Volume"
    std_map = {3: "3.MD (area/perimeter) • 3.OA.7 (facts ≤100)",
               4: "4.OA (factors/multiples) • 4.MD (perimeter)",
               5: "5.MD (rectangular prism volume)"}

    def __init__(self, grade=3):
        super().__init__(grade)
        self.reset()

    def reset(self):
        self.cell = 32
        self.origin = (60, 90)
        self.max_cols, self.max_rows = 20, 12

        # Rectangle dimensions (in tiles)
        self.w = 6
        self.h = 4
        self.layers = 1

        # Targets
        if self.grade == 3:
            self.target_area = random.choice([18, 20, 24, 28, 30])
        elif self.grade == 4:
            self.target_area = 48  # showcase factor pairs
        else:
            self.target_volume = random.choice([36, 48, 60, 72])  # l*w*h
            # pick an initial feasible tuple
            self.layers = 2

    def handle_event(self, event):
        pass

    def update(self, dt):
        keys = pygame.key.get_pressed()
        # Adjust rectangle
        if keys[pygame.K_LEFT]:
            self.w = max(1, self.w - 1)
        if keys[pygame.K_RIGHT]:
            self.w = min(self.max_cols, self.w + 1)
        if keys[pygame.K_UP]:
            self.h = min(self.max_rows, self.h + 1)
        if keys[pygame.K_DOWN]:
            self.h = max(1, self.h - 1)
        # Layers for Grade 5
        if self.grade == 5:
            if keys[pygame.K_q]:
                self.layers = max(1, self.layers - 1)
            if keys[pygame.K_e]:
                self.layers = min(20, self.layers + 1)

        # New random targets
        if keys[pygame.K_n]:
            if self.grade == 3:
                self.target_area = random.choice([18, 20, 24, 28, 30, 32, 36])
            elif self.grade == 5:
                self.target_volume = random.choice([36, 48, 60, 72, 84, 96])

    def draw_grid_and_rect(self):
        draw_grid(self.origin, self.cell, self.max_cols, self.max_rows)
        ox, oy = self.origin
        rect = pygame.Rect(ox, oy, self.w * self.cell, self.h * self.cell)
        pygame.draw.rect(screen, (50, 160, 230), rect, width=0)
        pygame.draw.rect(screen, WHITE, rect, width=2)

        # dots (array)
        for r in range(self.h):
            for c in range(self.w):
                cx = ox + c * self.cell + self.cell // 2
                cy = oy + r * self.cell + self.cell // 2
                pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 3)

    def overlay_lines(self):
        A = self.w * self.h
        P = 2 * (self.w + self.h)
        lines = []
        if self.grade == 3:
            lines = [
                "3.MD / 3.OA.7 — Area & arrays:",
                "area = rows × columns",
                f"Current: {self.h} × {self.w} = {A}",
                f"Target area: {self.target_area}"
            ]
        elif self.grade == 4:
            lines = [
                "4.OA / 4.MD — Factors & perimeter:",
                f"area = w×h = {A}, perimeter = 2(w+h) = {P}",
                "Same area, different perimeters (factor pairs)",
                "Try area 48 → (6×8), (4×12), (3×16)…"
            ]
        else:
            V = self.w * self.h * self.layers
            lines = [
                "5.MD — Volume of rectangular prisms:",
                "V = l × w × h (unit cubes)",
                f"Current: {self.w}×{self.h}×{self.layers} = {V}",
                f"Target volume: {self.target_volume}"
            ]
        return lines

    def controls_hint(self):
        if self.grade == 5:
            return "←/→ width • ↑/↓ height • Q/E layers • N new target • R reset"
        return "←/→ width • ↑/↓ height • N new target • R reset"

    def draw(self):
        # Titles
        if self.grade == 3:
            draw_text(screen, f"Make area = {self.target_area} tiles", (60, 60), WHITE, FONT)
        elif self.grade == 4:
            draw_text(screen, "Make rectangles with area 48 — compare perimeters", (60, 60), WHITE, FONT)
        else:
            draw_text(screen, f"Stack layers to hit target volume: V = {self.target_volume}", (60, 60), WHITE, FONT)

        self.draw_grid_and_rect()

        # Numbers
        A = self.w * self.h
        P = 2 * (self.w + self.h)
        draw_text(screen, f"w={self.w}, h={self.h}, area={A}, perim={P}", (60, 500), GRAY, SMALL)
        if self.grade == 5:
            V = A * self.layers
            draw_text(screen, f"layers={self.layers}, volume={V}", (60, 526), GRAY, SMALL)

        # Success states
        if self.grade == 3 and A == self.target_area:
            draw_text(screen, "✅ Area matched!", (60, 552), GREEN, FONT)
        if self.grade == 5 and A * self.layers == self.target_volume:
            draw_text(screen, "✅ Volume matched!", (60, 552), GREEN, FONT)


# ============================================================
# Scene 3 — Fraction Fuel
# ============================================================
class FractionFuel(Scene):
    name = "Fraction Fuel — Number Line & Operations"
    std_map = {3: "3.NF (fractions are numbers on a line)",
               4: "4.NF (equivalence; +/− like denoms; frac×whole)",
               5: "5.NF (unlike denoms; frac×frac; unit frac ÷ whole)"}

    def __init__(self, grade=3):
        super().__init__(grade)
        self.reset()

    def reset(self):
        self.sum = Fraction(0, 1)
        self.history = []
        self.max_total = Fraction(2, 1)  # allow >1 for grade 5
        # Targets and piece sets by grade
        if self.grade == 3:
            self.target = random.choice([Fraction(1, 2), Fraction(3, 4), Fraction(2, 3)])
            self.pieces = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 4)]
        elif self.grade == 4:
            self.target = Fraction(3, 4)
            # emphasize like denominators & equivalence eg quarters/eighths
            self.pieces = [Fraction(1, 4), Fraction(2, 4), Fraction(1, 8), Fraction(2, 8)]
        else:
            self.target = random.choice([Fraction(7, 6), Fraction(11, 12), Fraction(5, 4)])
            self.pieces = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 4), Fraction(1, 6)]

        # layout chips
        self.chip_rects = []

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            for frac, rect in self.chip_rects:
                if rect.collidepoint(mx, my):
                    if self.sum + frac <= self.max_total:
                        self.sum += frac
                        self.history.append(frac)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.sum = Fraction(0, 1)
                self.history.clear()
            elif event.key == pygame.K_z:
                if self.history:
                    last = self.history.pop()
                    self.sum -= last
            elif event.key == pygame.K_n:
                self.reset()

    def overlay_lines(self):
        L = [
            "Fractions are numbers on a line (0 → 1 → 2)",
            f"Target: {self.target}   Current: {self.sum}",
        ]
        if self.grade == 4:
            L += ["Equivalence: 2/4 = 1/2, 2/8 = 1/4",
                  "Add like denominators; multiply fraction × whole"]
        if self.grade == 5:
            L += ["Add unlike denominators (find common unit)",
                  "Multiply fractions; unit fraction ÷ whole"]
        return L

    def controls_hint(self):
        return "Click fraction chips to add • Z undo • C clear • N new target"

    def draw_number_line(self):
        ox, y = 60, 300
        length = WIDTH - 120
        # axis
        pygame.draw.line(screen, WHITE, (ox, y), (ox + length, y), 2)
        # ticks at integers
        for i in range(0, 3):
            x = ox + int(length * i / 2)
            pygame.draw.line(screen, WHITE, (x, y - 8), (x, y + 8), 2)
            draw_text(screen, str(i), (x - 4, y + 12), WHITE, SMALL)
        # fill bar for current sum
        sum_float = float(self.sum)
        fill_len = clamp(int(length * (sum_float / 2.0)), 0, length)
        pygame.draw.rect(screen, GREEN, (ox, y - 6, fill_len, 12))
        # Target marker
        t_float = float(self.target)
        tx = ox + int(length * (t_float / 2.0))
        pygame.draw.line(screen, YELLOW, (tx, y - 14), (tx, y + 14), 3)
        draw_text(screen, f"Target {self.target}", (tx - 30, y - 40), YELLOW, SMALL)

    def draw_chips(self):
        # dynamic chip layout
        self.chip_rects.clear()
        x, y = 60, 360
        for frac in self.pieces:
            w, h = 110, 38
            r = pygame.Rect(x, y, w, h)
            pygame.draw.rect(screen, (40, 60, 90), r, border_radius=6)
            pygame.draw.rect(screen, WHITE, r, width=2, border_radius=6)
            s = f"+ {frac.numerator}/{frac.denominator}"
            draw_text(screen, s, (x + 10, y + 8), WHITE, FONT)
            self.chip_rects.append((frac, r))
            x += w + 14

    def draw(self):
        # Title
        draw_text(screen, "Fill the tank by adding fraction pieces to hit the target.",
                  (60, 60), WHITE, FONT)
        draw_text(screen, f"Current sum: {self.sum}  ({float(self.sum):.3f})", (60, 90), GRAY, SMALL)

        # Number line & chips
        self.draw_number_line()
        self.draw_chips()

        # Success
        if self.sum == self.target:
            draw_text(screen, "✅ Exact hit!", (60, 420), GREEN, BIG)
        elif self.sum > self.target:
            draw_text(screen, "Overshot — try undo (Z) or Clear (C).", (60, 420), RED, SMALL)


# ============================================================
# Scene 4 — Data & Line-Plot Lab
# ============================================================
class DataPlotLab(Scene):
    name = "Data & Line-Plot Lab — Measure & Plot"
    std_map = {3: "3.MD (bar/picture graphs; time/mass/volume)",
               4: "4.MD (line plots with fractional units; conversions)",
               5: "5.MD (compare plots; totals/means; connect to volume/time)"}

    def __init__(self, grade=3):
        super().__init__(grade)
        self.reset()

    def reset(self):
        self.values_A = []
        self.values_B = []
        self.unit = "in"  # inches
        self.group = "A"  # active
        # ranges
        self.x_min = 0.0
        self.x_max = 10.0
        self.tick = 1.0 if self.grade == 3 else 0.25  # 1 for 3rd; quarters for 4th/5th

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.add_sample("A")
            elif event.key == pygame.K_b:
                self.add_sample("B")
            elif event.key == pygame.K_c:
                self.values_A.clear()
                self.values_B.clear()
            elif event.key == pygame.K_u:
                self.toggle_units()

    def toggle_units(self):
        # inches ↔ feet conversion showcase
        if self.unit == "in":
            self.unit = "ft"
            # convert in → ft
            self.values_A = [v / 12.0 for v in self.values_A]
            self.values_B = [v / 12.0 for v in self.values_B]
            self.x_max /= 12.0
            self.x_min /= 12.0
            self.tick = 0.25 if self.grade >= 4 else 0.5
        else:
            self.unit = "in"
            self.values_A = [v * 12.0 for v in self.values_A]
            self.values_B = [v * 12.0 for v in self.values_B]
            self.x_max *= 12.0
            self.x_min *= 12.0
            self.tick = 1.0 if self.grade == 3 else 3.0  # quarters foot → 3 inches

    def sample_value(self):
        # produce a value with variability; fractional ticks if grade >=4
        if self.grade == 3:
            base = random.randint(2, 9)  # whole inches
            return float(base)
        else:
            # quarter-inch grid around 5 ± some
            quarters = [i / 4.0 for i in range(0, 41)]  # 0..10 step 0.25
            return random.choice(quarters)

    def add_sample(self, group):
        v = self.sample_value()
        if group == "A":
            self.values_A.append(v)
        else:
            self.values_B.append(v)

    def overlay_lines(self):
        L = ["Run trials (A/B), plot results, read the plot."]
        if self.grade == 3:
            L += ["Make a simple graph; compare counts (add/sub).",
                  "Units: inches; whole-number ticks."]
        elif self.grade == 4:
            L += ["Line plot with fractional ticks (quarters).",
                  "Unit conversions: in ↔ ft (press U)."]
        else:
            L += ["Compare two groups (A vs B): totals/means.",
                  "Relate to goals (e.g., time saved)."]
        return L

    def controls_hint(self):
        return "A add sample A • B add sample B • U switch units (in/ft) • C clear"

    def draw_axes(self, origin=(60, 450), width=880, height=150):
        ox, oy = origin
        pygame.draw.rect(screen, (30, 35, 52), (ox-10, oy-height-10, width+20, height+20), border_radius=8)
        # axis lines
        pygame.draw.line(screen, WHITE, (ox, oy), (ox + width, oy), 2)
        pygame.draw.line(screen, WHITE, (ox, oy), (ox, oy - height), 2)
        # ticks
        rng = self.x_max - self.x_min
        steps = max(1, int(rng / self.tick) + 1)
        for i in range(steps + 1):
            val = self.x_min + i * self.tick
            x = ox + int((val - self.x_min) / rng * width)
            pygame.draw.line(screen, WHITE, (x, oy - 6), (x, oy + 6), 1)
            if i % max(1, int(1.0 / (self.tick if self.unit == "in" else self.tick))) == 0:
                draw_text(screen, f"{val:g}", (x - 8, oy + 8), GRAY, SMALL)
        draw_text(screen, f"units: {self.unit}", (ox + width - 80, oy - height - 26), GRAY, SMALL)
        return ox, oy, width, height

    def draw_line_plot(self):
        ox, oy, width, height = self.draw_axes()
        # helper to plot a set
        def plot(values, color):
            if not values:
                return
            # bin by tick
            bins = {}
            for v in values:
                key = round(v / self.tick) * self.tick
                bins[key] = bins.get(key, 0) + 1
            # draw stacks
            for val, count in bins.items():
                x = ox + int((val - self.x_min) / (self.x_max - self.x_min) * width)
                for i in range(count):
                    y = oy - 12 - i * 16
                    pygame.draw.circle(screen, color, (x, y), 5)

        plot(self.values_A, CYAN)
        plot(self.values_B, ORANGE)
        # Legend
        pygame.draw.circle(screen, CYAN, (60, 480), 6); draw_text(screen, "Group A", (72, 472), CYAN, SMALL)
        pygame.draw.circle(screen, ORANGE, (140, 480), 6); draw_text(screen, "Group B", (152, 472), ORANGE, SMALL)

        # Stats (grade 5)
        if self.grade == 5:
            def mean(vals): return sum(vals)/len(vals) if vals else 0.0
            mA, mB = mean(self.values_A), mean(self.values_B)
            draw_text(screen, f"Mean A: {mA:.2f} {self.unit}", (240, 472), GRAY, SMALL)
            draw_text(screen, f"Mean B: {mB:.2f} {self.unit}", (380, 472), GRAY, SMALL)

    def draw(self):
        draw_text(screen, "Add trials (A/B). The plot builds live with whole or fractional units.", (60, 60), WHITE, FONT)
        draw_text(screen, "Try U to convert inches ↔ feet and see the scale change.", (60, 90), GRAY, SMALL)
        self.draw_line_plot()


# ============================================================
# Scene 5 — Angles & Coordinates Quest
# ============================================================
class AnglesCoords(Scene):
    name = "Angles & Coordinates Quest — Bounce & Graph"
    std_map = {3: "3.G (reason about shapes & right angles)",
               4: "4.G (classify angles; parallel/perpendicular)",
               5: "5.G (graph points in first quadrant)"}

    def __init__(self, grade=3):
        super().__init__(grade)
        self.reset()

    def reset(self):
        self.origin = (120, 120)
        self.bounds = pygame.Rect(120, 120, WIDTH - 240, HEIGHT - 260)
        self.ball = pygame.Vector2(self.bounds.left + 40, self.bounds.bottom - 40)
        self.v = pygame.Vector2(0, 0)
        self.ball_r = 10
        self.aiming = True
        # Goal
        gx = random.randint(self.bounds.left + 80, self.bounds.right - 80)
        gy = random.randint(self.bounds.top + 80, self.bounds.bottom - 80)
        self.goal = pygame.Vector2(gx, gy)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.aiming:
            mx, my = pygame.mouse.get_pos()
            dir = pygame.Vector2(mx - self.ball.x, my - self.ball.y)
            if dir.length() > 0:
                dir = dir.normalize()
                power = min(550, pygame.Vector2(mx - self.ball.x, my - self.ball.y).length() * 3)
                self.v = dir * power
                self.aiming = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset()

    def update(self, dt):
        if self.paused: return
        if not self.aiming:
            self.ball += self.v * dt
            # wall reflections (angle in = angle out)
            if self.ball.x - self.ball_r < self.bounds.left:
                self.ball.x = self.bounds.left + self.ball_r
                self.v.x *= -1
            if self.ball.x + self.ball_r > self.bounds.right:
                self.ball.x = self.bounds.right - self.ball_r
                self.v.x *= -1
            if self.ball.y - self.ball_r < self.bounds.top:
                self.ball.y = self.bounds.top + self.ball_r
                self.v.y *= -1
            if self.ball.y + self.ball_r > self.bounds.bottom:
                self.ball.y = self.bounds.bottom - self.ball_r
                self.v.y *= -1
            # friction
            self.v *= 0.999

            # success
            if self.ball.distance_to(self.goal) <= self.ball_r + 14:
                self.aiming = True
                self.goal = pygame.Vector2(
                    random.randint(self.bounds.left + 80, self.bounds.right - 80),
                    random.randint(self.bounds.top + 80, self.bounds.bottom - 80)
                )

    def overlay_lines(self):
        L = ["Bank shots use angle rules:",
             "angle_out = angle_in (mirror bounce)"]
        if self.grade == 4:
            L += ["Classify angles: acute < 90°, right = 90°, obtuse > 90°",
                  "Walls are perpendicular/parallel edges"]
        if self.grade == 5:
            L += [f"Goal ≈ ({int(self.goal.x)}, {int(self.goal.y)}) on grid (first quadrant)"]
        return L

    def controls_hint(self):
        return "Aim with mouse • Left-click to shoot • R reset target/ball"

    def draw_arena(self):
        # grid (for 5th grade clarity)
        if self.grade == 5:
            step = 40
            ox, oy, w, h = self.bounds.left, self.bounds.top, self.bounds.width, self.bounds.height
            for x in range(ox, ox + w + 1, step):
                pygame.draw.line(screen, (35, 40, 58), (x, oy), (x, oy + h))
            for y in range(oy, oy + h + 1, step):
                pygame.draw.line(screen, (35, 40, 58), (ox, y), (ox + w, y))

        pygame.draw.rect(screen, (30, 35, 52), self.bounds, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.bounds, width=2, border_radius=8)

    def draw(self):
        draw_text(screen, "Bank a shot to the goal. Bounces follow angle rules.", (60, 60), WHITE, FONT)
        self.draw_arena()

        # draw goal
        pygame.draw.circle(screen, RED, (int(self.goal.x), int(self.goal.y)), 14, width=3)
        pygame.draw.circle(screen, RED, (int(self.goal.x), int(self.goal.y)), 4)

        # aim line
        if self.aiming:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.line(screen, ACCENT, (int(self.ball.x), int(self.ball.y)), (mx, my), 2)

        # ball
        pygame.draw.circle(screen, GREEN, (int(self.ball.x), int(self.ball.y)), self.ball_r)

        # coordinates (grade 5 emphasis)
        if self.grade == 5:
            draw_text(screen, f"Ball ({int(self.ball.x)}, {int(self.ball.y)})", (self.bounds.left, self.bounds.bottom + 10), GRAY, SMALL)
            draw_text(screen, f"Goal ({int(self.goal.x)}, {int(self.goal.y)})", (self.bounds.left + 180, self.bounds.bottom + 10), GRAY, SMALL)


# ============================================================
# Scene Manager & App
# ============================================================
SCENE_CLASSES = [RateRacer, ArrayCity, FractionFuel, DataPlotLab, AnglesCoords]

class App:
    def __init__(self):
        self.grade_index = 0  # start Grade 3
        self.grade = GRADE_LEVELS[self.grade_index]
        self.scenes = [cls(self.grade) for cls in SCENE_CLASSES]
        self.index = 0
        self.scene = self.scenes[self.index]
        self.overlay_on = True
        self.paused = False
        self.slowmo = False

    def set_grade(self, g):
        self.grade = g
        for sc in self.scenes:
            sc.set_grade(g)

    def next_scene(self):
        self.index = (self.index + 1) % len(self.scenes)
        self.scene = self.scenes[self.index]

    def prev_scene(self):
        self.index = (self.index - 1) % len(self.scenes)
        self.scene = self.scenes[self.index]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB and not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.next_scene()
            elif event.key == pygame.K_TAB and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                self.prev_scene()
            elif event.key == pygame.K_g:
                self.grade_index = (self.grade_index + 1) % len(GRADE_LEVELS)
                self.set_grade(GRADE_LEVELS[self.grade_index])
            elif event.key == pygame.K_o:
                self.overlay_on = not self.overlay_on
                self.scene.overlay_on = self.overlay_on
            elif event.key == pygame.K_p:
                self.paused = not self.paused
                self.scene.paused = self.paused
            elif event.key == pygame.K_r:
                self.scene.reset()

        self.scene.handle_event(event)

    def run(self):
        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            self.slowmo = pygame.key.get_pressed()[pygame.K_s]
            dt = dt * 0.25 if self.slowmo else dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_event(event)

            # Update
            if not self.paused:
                self.scene.update(dt)

            # Draw
            screen.fill(BG)
            std_tag = getattr(self.scene, "std_map", {}).get(self.grade, "")
            draw_header(self.scene.name, std_tag, self.grade, self.overlay_on)
            self.scene.draw()
            if self.overlay_on:
                draw_overlay(self.scene.overlay_lines())
            draw_footer(self.scene.controls_hint())

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    App().run()
