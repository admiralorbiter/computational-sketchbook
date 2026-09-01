use macroquad::prelude::*;
use crate::app::{PLANET_RADIUS, ATMOSPHERE_HEIGHT};

const MAX_PARTICLES: usize = 2000;

#[derive(Clone)]
struct Particle {
    position: Vec2,
    velocity: Vec2,
    life: f32,     // seconds remaining
    max_life: f32, // seconds at birth
    size: f32,
}

pub struct ParticleSystem {
    particles: Vec<Particle>,
    /// Simple LCG seed — avoids needing rand crate
    seed: u64,
}

impl ParticleSystem {
    pub fn new() -> Self {
        Self {
            particles: Vec::with_capacity(MAX_PARTICLES),
            seed: 0xC0FFEE_DEADBEEF,
        }
    }

    fn rand_f32(&mut self) -> f32 {
        self.seed ^= self.seed << 13;
        self.seed ^= self.seed >> 7;
        self.seed ^= self.seed << 17;
        (self.seed as f32) / (u64::MAX as f32)
    }

    fn rand_range(&mut self, lo: f32, hi: f32) -> f32 {
        lo + self.rand_f32().abs() * (hi - lo)
    }

    /// Emit exhaust particles. Call each fixed tick while engine is burning.
    /// `emit_count` — number of particles to spawn this tick (multiply by time_scale for warp).
    /// `base` — world-space engine nozzle position.
    /// `thrust_dir` — unit vector pointing in thrust direction (away from engine).
    /// `throttle` — 0..1, used to scale spread and count.
    pub fn emit_exhaust(
        &mut self,
        emit_count: u32,
        base: Vec2,
        thrust_dir: Vec2,    // points AWAY from rocket (exhaust direction)
        throttle: f32,
    ) {
        // back-facing exhaust dir
        let back = -thrust_dir;
        let right = Vec2::new(back.y, -back.x);

        for _ in 0..emit_count {
            if self.particles.len() >= MAX_PARTICLES {
                // Remove oldest particle to make room
                self.particles.remove(0);
            }

            let speed = self.rand_range(60.0, 180.0) * throttle;
            let spread = self.rand_range(-0.35, 0.35); // radians spread
            let spread_dir = Vec2::new(
                back.x * spread.cos() - back.y * spread.sin(),
                back.x * spread.sin() + back.y * spread.cos(),
            );
            let lateral_rng = self.rand_range(-1.0, 1.0);
            let pos_offset = self.rand_range(-3.0, 3.0);

            let life = self.rand_range(0.25, 0.6);
            let size = self.rand_range(2.5, 6.0) * throttle;

            if self.particles.len() >= MAX_PARTICLES {
                // Remove oldest particle to make room
                self.particles.remove(0);
            }

            self.particles.push(Particle {
                position: base + right * pos_offset,
                velocity: spread_dir * speed + right * lateral_rng * 2.0 * throttle,
                life,
                max_life: life,
                size,
            });
        }
    }

    /// Emit a burst on staging — white-hot flash of particles.
    pub fn emit_stage_burst(&mut self, position: Vec2) {
        for _ in 0..80 {
            if self.particles.len() >= MAX_PARTICLES {
                self.particles.remove(0);
            }
            let angle = self.rand_f32() * std::f32::consts::PI * 2.0;
            let speed = self.rand_range(30.0, 120.0);
            let life = self.rand_range(0.2, 0.5);
            let burst_size = self.rand_range(3.0, 8.0);
            if self.particles.len() >= MAX_PARTICLES {
                self.particles.remove(0);
            }
            self.particles.push(Particle {
                position,
                velocity: Vec2::new(angle.cos(), angle.sin()) * speed,
                life,
                max_life: life,
                size: burst_size,
            });
        }
    }

    /// Update all particles by `dt` seconds.
    pub fn update(&mut self, dt: f32) {
        // Simple drag so particles slow down naturally
        let drag = 0.92_f32.powf(dt * 60.0);
        for p in &mut self.particles {
            p.life -= dt;
            p.velocity *= drag;
            p.position += p.velocity * dt;
        }
        self.particles.retain(|p| p.life > 0.0);
    }

    /// Render all particles. Call with world camera active.
    pub fn draw(&self) {
        let altitude_of_particle = |pos: Vec2| -> f32 {
            pos.length() - PLANET_RADIUS
        };

        for p in &self.particles {
            let t = p.life / p.max_life; // 1.0 = fresh, 0.0 = dying
            let alpha = t * t; // quadratic fade

            // Color gradient: yellow-core (fresh) → orange → dim red (dying)
            let color = if t > 0.6 {
                // yellow-white
                Color::new(1.0, 0.95, 0.4, alpha)
            } else if t > 0.3 {
                // orange
                Color::new(1.0, 0.5, 0.1, alpha * 0.85)
            } else {
                // dim red smoke
                Color::new(0.6, 0.15, 0.05, alpha * 0.5)
            };

            // Don't draw particles underground
            let alt = altitude_of_particle(p.position);
            if alt < -(ATMOSPHERE_HEIGHT * 0.1) {
                continue;
            }

            draw_circle(p.position.x, p.position.y, p.size, color);
        }
    }

    pub fn particle_count(&self) -> usize {
        self.particles.len()
    }
}
