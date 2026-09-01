use macroquad::prelude::*;
use crate::sim::RocketState;
use crate::debug::Tunables;
use crate::app::{PLANET_RADIUS, SURFACE_GRAVITY, ATMOSPHERE_HEIGHT};
use crate::sim::atmosphere;

pub fn draw_vectors(rocket: &RocketState, tunables: &Tunables) {
    if matches!(rocket.flight_status, crate::sim::rocket::FlightStatus::Crashed { .. }) {
        return;
    }

    let pos = Vec2::new(rocket.position.x as f32, rocket.position.y as f32);
    
    // 1. Center of mass marker
    draw_line(pos.x - 5.0, pos.y, pos.x + 5.0, pos.y, 1.0, YELLOW);
    draw_line(pos.x, pos.y - 5.0, pos.x, pos.y + 5.0, 1.0, YELLOW);

    // Scaling factors for visual readability
    let f_scale = 0.005; 
    let v_scale = 1.0;

    // 2. Velocity vector (White)
    let vel = Vec2::new(rocket.velocity.x as f32, rocket.velocity.y as f32);
    if vel.length_squared() > 1.0 {
        draw_line(pos.x, pos.y, pos.x + vel.x * v_scale, pos.y + vel.y * v_scale, 2.0, WHITE);
    }

    let current_mass = rocket.total_mass();

    // 3. Thrust vector (Green)
    if rocket.throttle > 0.0 && rocket.fuel_remaining() > 0.0 {
        let total_thrust = rocket.active_thrust_vacuum();
        let thrust_mag = total_thrust * rocket.throttle * tunables.thrust_multiplier;
        let rot = rocket.rotation;
        let thrust_dir = Vec2::new(rot.sin(), rot.cos());
        let end = pos + thrust_dir * (thrust_mag * f_scale);
        draw_line(pos.x, pos.y, end.x, end.y, 3.0, GREEN);
    }

    // 4. Drag vector (Red)
    let altitude = rocket.position.length() - (PLANET_RADIUS as f64);
    if vel.length_squared() > 1.0 && altitude < (ATMOSPHERE_HEIGHT as f64) {
        let drag_force = atmosphere::drag_force(
            macroquad::math::DVec2::new(vel.x as f64, vel.y as f64), 
            1.0, 
            rocket.total_drag_area() as f64, 
            altitude
        );
        let drag_mag = drag_force.length() as f32 * tunables.drag_multiplier;
        if drag_mag > 10.0 {
            let drag_dir = -vel.normalize();
            let end = pos + drag_dir * (drag_mag * f_scale);
            draw_line(pos.x, pos.y, end.x, end.y, 3.0, RED);
        }
    }

    // 5. Gravity vector (Dark Gray)
    let dist_sq = rocket.position.length_squared(); // f64
    if dist_sq > 1e-6 {
        let up_dir = rocket.position.normalize();
        let gm = (SURFACE_GRAVITY as f64) * (PLANET_RADIUS as f64).powi(2);
        let gravity_accel = (gm / dist_sq) * (tunables.gravity_multiplier as f64);
        let g_force = gravity_accel * (current_mass as f64);
        let end_f64 = rocket.position - up_dir * (g_force * f_scale as f64);
        let end = Vec2::new(end_f64.x as f32, end_f64.y as f32);
        draw_line(pos.x, pos.y, end.x, end.y, 2.0, DARKGRAY);
    }
}
