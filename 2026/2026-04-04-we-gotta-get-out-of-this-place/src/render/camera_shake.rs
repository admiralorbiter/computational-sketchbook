use macroquad::prelude::*;

/// Simple quadratic camera shake. Set `trauma` to 1.0 on a big impact, 0.5 on smaller ones.
/// Each frame call `update(dt)` then read `offset()` to shift the camera target.
pub struct CameraShake {
    pub trauma: f32,
    seed: f32, // shifts the noise pattern per shake instance
}

impl CameraShake {
    pub fn new() -> Self {
        Self { trauma: 0.0, seed: 0.0 }
    }

    pub fn add_trauma(&mut self, amount: f32) {
        self.trauma = (self.trauma + amount).min(1.0);
        self.seed += 37.3; // advance noise pattern so stacked traumas don't cancel
    }

    /// Call once per frame with the real (unscaled) frame dt.
    pub fn update(&mut self, dt: f32) {
        let decay = 2.5; // trauma/sec decay rate — full shake dies in ~0.4s
        self.trauma = (self.trauma - decay * dt).max(0.0);
    }

    /// Returns a world-space pixel offset to apply to the camera target.
    /// Amplitude scales as trauma² so small residual trauma is nearly invisible.
    pub fn offset(&self, max_pixels: f32) -> Vec2 {
        if self.trauma < 0.001 {
            return Vec2::ZERO;
        }
        let magnitude = self.trauma * self.trauma * max_pixels;
        // Simple pseudo-random using sin/cos on the seed — deterministic but chaotic
        let t = get_time() as f32 * 60.0; // 60 "noise" samples per second
        let x = ((t * 1.37 + self.seed).sin()) * magnitude;
        let y = ((t * 1.97 + self.seed * 0.7).sin()) * magnitude;
        Vec2::new(x, y)
    }
}
