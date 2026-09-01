use macroquad::prelude::*;

const STAR_COUNT: usize = 350;
const PARALLAX_FACTOR: f32 = 0.04; // Stars move at 4% of camera speed — very subtle

pub struct Starfield {
    /// Each star stored as a normalized direction from origin + a distance multiplier.
    /// We store world-space positions at a huge radius so zoom doesn't matter.
    stars: Vec<StarData>,
}

struct StarData {
    /// Direction unit vector
    dir: Vec2,
    /// Base distance from origin (large, so they never intersect foreground)
    base_dist: f32,
    radius: f32,
    color: Color,
}

impl Starfield {
    pub fn new() -> Self {
        let mut stars = Vec::with_capacity(STAR_COUNT);

        // Deterministic pseudo-random using integer hash — no rand dependency needed
        let mut seed: u64 = 0xDEADBEEF_CAFEBABE;
        let hash = |s: &mut u64| -> f32 {
            *s ^= *s << 13;
            *s ^= *s >> 7;
            *s ^= *s << 17;
            (*s as f32) / (u64::MAX as f32)
        };

        for _ in 0..STAR_COUNT {
            let angle = hash(&mut seed) * std::f32::consts::PI * 2.0;
            let dist = 3_500_000.0 + hash(&mut seed) * 6_000_000.0; // well outside atmosphere
            let radius = if hash(&mut seed) > 0.93 {
                // ~7% brighter "foreground" stars
                3000.0 + hash(&mut seed) * 4000.0
            } else {
                800.0 + hash(&mut seed) * 2500.0
            };

            // Slightly randomize star color: mostly white, some warm/cool tints
            let tint = hash(&mut seed);
            let color = if tint > 0.8 {
                Color::new(0.7, 0.8, 1.0, 0.9) // cool blue-white
            } else if tint > 0.6 {
                Color::new(1.0, 0.95, 0.8, 0.85) // warm yellow-white
            } else {
                Color::new(0.9, 0.9, 0.95, 0.8) // neutral white
            };

            stars.push(StarData {
                dir: Vec2::new(angle.cos(), angle.sin()),
                base_dist: dist,
                radius,
                color,
            });
        }

        Self { stars }
    }

    /// Draw stars with slight parallax relative to the camera position.
    /// Call this AFTER setting the world camera (stars are in world space).
    pub fn draw(&self, camera_target: Vec2) {
        for star in &self.stars {
            // Parallax: stars don't fully track the camera — they lag behind
            let world_pos = star.dir * star.base_dist + camera_target * PARALLAX_FACTOR;
            draw_circle(world_pos.x, world_pos.y, star.radius, star.color);
        }
    }
}
