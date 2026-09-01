import math
import random
import pygame

"""
Math-in-Motion: a 5–10 minute classroom demo (Pygame)
Mode 1 (Middle school): Catch falling stars -> linear motion, speed, probability
Mode 2 (High school preview): Launch a ball at a target -> angles, projectile motion, quadratic path
Keys:
  1 = Middle school mode
  2 = High school mode
  O = Toggle math overlay
  R = Reset score / scene
Controls:
  Mode 1: Move basket with mouse or ←/→
  Mode 2: Aim with mouse; left-click to launch (power = mouse distance)
"""

# ---------- Setup ----------
pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math in Motion — Pygame")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont(None, 24)
BIG = pygame.font.SysFont(None, 36)

# Colors
BG = (20, 24, 38)
WHITE = (240, 240, 240)
ACCENT = (100, 200, 255)
GOLD = (255, 208, 48)
RED = (240, 90, 90)
GREEN = (80, 200, 120)
GRAY = (120, 130, 150)

# ---------- Helpers ----------
def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def draw_text(surface, text, pos, color=WHITE, font=FONT):
    img = font.render(text, True, color)
    surface.blit(img, pos)

# ---------- Mode 1: Falling Stars ----------
class Basket:
    def __init__(self):
        self.w, self.h = 120, 18
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.speed = 520  # pixels per second

    def update(self, dt, keys):
        # Mouse control (primary), with arrow key fallback
        mx, _ = pygame.mouse.get_pos()
        self.x += (mx - self.x) * min(1.0, dt * 12)  # smooth follow
        if keys[pygame.K_LEFT]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.x += self.speed * dt
        self.x = clamp(self.x, self.w / 2, WIDTH - self.w / 2)

    def rect(self):
        return pygame.Rect(int(self.x - self.w / 2), int(self.y - self.h / 2), self.w, self.h)

    def draw(self, surface):
        pygame.draw.rect(surface, ACCENT, self.rect(), border_radius=6)

class Star:
    def __init__(self, speed_boost=0.0):
        self.radius = 12
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        base_speed = random.uniform(200, 280)
        self.vy = base_speed + speed_boost

    def update(self, dt):
        self.y += self.vy * dt

    def draw(self, surface):
        pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y)), self.radius)
        # twinkle
        pygame.draw.line(surface, WHITE, (self.x - self.radius//2, self.y),
                         (self.x + self.radius//2, self.y), 2)
        pygame.draw.line(surface, WHITE, (self.x, self.y - self.radius//2),
                         (self.x, self.y + self.radius//2), 2)

# ---------- Mode 2: Projectile ----------
GRAVITY = 800.0  # pixels / s^2 (screen Y grows downward)
LAUNCH_ORIGIN = (80, HEIGHT - 80)

class Ball:
    def __init__(self):
        self.r = 12
        self.reset()

    def reset(self):
        self.x, self.y = LAUNCH_ORIGIN
        self.vx = 0.0
        self.vy = 0.0
        self.alive = False

    def launch(self, angle, power01):
        # Map power 0..1 -> launch speed
        v0 = 300 + power01 * 400  # 300..700 px/s
        self.vx = v0 * math.cos(angle)
        self.vy = v0 * math.sin(angle)
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        self.vy += GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # stop when out of bounds
        if self.x > WIDTH + 50 or self.y > HEIGHT + 50 or self.x < -50:
            self.reset()

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.r)

class Target:
    def __init__(self):
        self.r = 18
        self.reposition()

    def reposition(self):
        self.x = random.randint(WIDTH // 2 + 80, WIDTH - 60)
        self.y = random.randint(140, HEIGHT - 120)

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (self.x, self.y), self.r, 3)
        pygame.draw.circle(surface, RED, (self.x, self.y), max(4, self.r // 4))

# ---------- Scene State ----------
mode = 1  # 1 = middle school, 2 = high school preview
show_overlay = True
score = 0

# Mode 1 state
basket = Basket()
stars = []
spawn_rate = 1.1  # stars per second
difficulty_timer = 0.0

# Mode 2 state
ball = Ball()
target = Target()

# ---------- Overlay text ----------
def draw_overlay_middle(surface):
    lines = [
        "Middle school math in action:",
        "Position = Position + Speed × Time",
        "y = y + v × Δt   (Δt = time since last frame)",
        f"Spawn chance each frame ≈ rate × Δt     (rate ≈ {spawn_rate:.1f} stars/sec)",
    ]
    for i, t in enumerate(lines):
        draw_text(surface, t, (16, 60 + i * 22), color=WHITE)

def draw_overlay_high(surface, angle=None, power01=None):
    lines = [
        "High school preview — projectile motion:",
        "vx = v0 · cos(θ)         vy = v0 · sin(θ) + g · t",
        "x(t) = x0 + vx · t       y(t) = y0 + vy · t   (down is +y on screen)",
        f"g (gravity) ≈ {int(GRAVITY)} px/s²   θ ≈ {int(math.degrees(angle)) if angle is not None else '?'}°   power ≈ {int((power01 or 0)*100)}%",
    ]
    for i, t in enumerate(lines):
        draw_text(surface, t, (16, 60 + i * 22), color=WHITE)

def draw_header(surface):
    bar = pygame.Rect(0, 0, WIDTH, 44)
    pygame.draw.rect(surface, (30, 34, 52), bar)
    draw_text(surface, "Math in Motion — 1: Middle (linear)   2: High School (projectile)   O: toggle math   R: reset",
              (12, 12), color=WHITE)
    draw_text(surface, f"Score: {score}", (WIDTH - 120, 12), color=WHITE)

# ---------- Reset ----------
def hard_reset():
    global score, stars, spawn_rate, difficulty_timer
    score = 0
    stars = []
    spawn_rate = 1.1
    difficulty_timer = 0.0
    basket.x = WIDTH // 2
    ball.reset()
    target.reposition()

# ---------- Main Loop ----------
running = True
while running:
    dt = clock.tick(60) / 1000.0  # seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                mode = 1
            elif event.key == pygame.K_2:
                mode = 2
            elif event.key == pygame.K_o:
                show_overlay = not show_overlay
            elif event.key == pygame.K_r:
                hard_reset()
        elif event.type == pygame.MOUSEBUTTONDOWN and mode == 2:
            if event.button == 1:  # left click to launch
                mx, my = pygame.mouse.get_pos()
                ox, oy = LAUNCH_ORIGIN
                dx, dy = mx - ox, my - oy
                angle = math.atan2(dy, dx)
                dist = math.hypot(dx, dy)
                power01 = clamp(dist / 300.0, 0.0, 1.0)
                ball.launch(angle, power01)

    keys = pygame.key.get_pressed()

    # ---------- Update ----------
    if mode == 1:
        basket.update(dt, keys)
        # increase difficulty slowly (faster stars)
        difficulty_timer += dt
        speed_boost = min(220, difficulty_timer * 10)  # +10 px/s every second up to +220
        # spawn stars with probability spawn_rate * dt
        if random.random() < spawn_rate * dt:
            stars.append(Star(speed_boost))
        # move stars and check for catches
        rect = basket.rect()
        for s in stars[:]:
            s.update(dt)
            if rect.collidepoint(s.x, s.y):
                stars.remove(s)
                score += 1
            elif s.y > HEIGHT + s.radius:
                stars.remove(s)
    else:
        ball.update(dt)
        # check hit target
        if ball.alive:
            if math.hypot(ball.x - target.x, ball.y - target.y) <= ball.r + target.r:
                score += 1
                ball.reset()
                target.reposition()

    # ---------- Draw ----------
    screen.fill(BG)
    draw_header(screen)

    if mode == 1:
        # ground
        pygame.draw.rect(screen, (36, 42, 58), (0, HEIGHT - 40, WIDTH, 40))
        basket.draw(screen)
        for s in stars:
            s.draw(screen)
        if show_overlay:
            draw_overlay_middle(screen)
        # instructions
        draw_text(screen, "Catch the stars! (Move with mouse or ←/→)", (16, HEIGHT - 32), color=GRAY)
    else:
        # ground
        pygame.draw.rect(screen, (36, 42, 58), (0, HEIGHT - 40, WIDTH, 40))
        # draw origin slingshot
        pygame.draw.circle(screen, WHITE, LAUNCH_ORIGIN, 6)
        # Aim line and predicted arc when ball not launched
        mx, my = pygame.mouse.get_pos()
        ox, oy = LAUNCH_ORIGIN
        dx, dy = mx - ox, my - oy
        angle = math.atan2(dy, dx)
        dist = math.hypot(dx, dy)
        power01 = clamp(dist / 300.0, 0.0, 1.0)

        # aim line
        aim_len = 60 + power01 * 100
        ax = ox + math.cos(angle) * aim_len
        ay = oy + math.sin(angle) * aim_len
        pygame.draw.line(screen, ACCENT, (ox, oy), (ax, ay), 2)

        # predicted path (dotted)
        v0 = 300 + power01 * 400
        vx0 = v0 * math.cos(angle)
        vy0 = v0 * math.sin(angle)
        t = 0.0
        last = (ox, oy)
        while t < 2.8:
            t += 0.06
            x = ox + vx0 * t
            y = oy + vy0 * t + 0.5 * GRAVITY * t * t
            if y > HEIGHT - 20 or x > WIDTH + 10 or x < -10:
                break
            pygame.draw.circle(screen, (170, 210, 255), (int(x), int(y)), 3)
            last = (x, y)

        ball.draw(screen)
        target.draw(screen)
        if show_overlay:
            draw_overlay_high(screen, angle, power01)
        draw_text(screen, "Aim with mouse, left-click to launch. Hit the red target!", (16, HEIGHT - 32), color=GRAY)

    pygame.display.flip()

pygame.quit()
