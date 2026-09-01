use macroquad::prelude::*;
use crate::sim::RocketState;

pub fn draw_world(planet_radius: f32, atmo_height: f32, camera: &Camera2D, rocket: &RocketState) {
    let altitude = (rocket.position.length() as f32) - planet_radius;
    let atmo_fraction = (1.0 - altitude / atmo_height).clamp(0.0, 1.0);

    // --- Altitude-tinted background ---
    // At ground level: subtly blue. In space: pure dark.
    let bg_blue = atmo_fraction * 0.07;
    let bg_green = atmo_fraction * 0.03;
    clear_background(Color::new(0.05, 0.05 + bg_green, 0.08 + bg_blue, 1.0));

    // --- Planet body ---
    draw_circle(0.0, 0.0, planet_radius, DARKGRAY);

    // Subtle polar highlight — slightly lighter cap at the "north" (+Y) pole
    draw_circle(0.0, planet_radius * 0.8, planet_radius * 0.35, Color::new(0.40, 0.40, 0.42, 1.0));

    // --- Precision horizon arc (pie slices to avoid V-gaps) ---
    let screen_width_world = 2.0 / camera.zoom.x.abs();
    let cam_dist = camera.target.length();
    if cam_dist > 1.0 && altitude < 300_000.0 {
        let angle_to_cam = camera.target.y.atan2(camera.target.x);
        let arc_span = (screen_width_world / planet_radius * 2.0).clamp(0.01, std::f32::consts::PI * 2.0);
        let segments = 256;
        let angle_step = arc_span / (segments as f32);
        let start_angle = angle_to_cam - arc_span * 0.5;

        for i in 0..segments {
            let a1 = start_angle + (i as f32) * angle_step;
            let a2 = start_angle + ((i as f32 + 1.1) * angle_step);
            let p1 = Vec2::new(a1.cos(), a1.sin()) * planet_radius;
            let p2 = Vec2::new(a2.cos(), a2.sin()) * planet_radius;
            draw_triangle(p1, p2, Vec2::ZERO, DARKGRAY);
        }
    }

    // --- Atmosphere glow rings (layered from outer → inner) ---
    let atmo_r = planet_radius + atmo_height;
    let glow_layers = [
        (atmo_r,                        5_000.0, Color::new(0.25, 0.55, 0.90, 0.07)),
        (atmo_r * 0.985,                6_000.0, Color::new(0.30, 0.60, 0.92, 0.12)),
        (planet_radius + atmo_height * 0.6, 8_000.0, Color::new(0.35, 0.65, 0.90, 0.18)),
        (planet_radius + atmo_height * 0.25, 10_000.0, Color::new(0.50, 0.75, 0.95, 0.15)),
    ];
    for (r, thickness, color) in glow_layers {
        draw_circle_lines(0.0, 0.0, r, thickness, color);
    }

    // --- Reentry heat glow ---
    // Only when fast AND inside atmosphere
    let speed = rocket.velocity.length() as f32;
    let heat_intensity = ((speed - 1500.0) / 3000.0).clamp(0.0, 1.0) * atmo_fraction;
    if heat_intensity > 0.01 {
        let rx = rocket.position.x as f32;
        let ry = rocket.position.y as f32;
        // Several expanding circles at decreasing alpha
        for i in 0..4 {
            let scale = 1.0 + i as f32 * 0.8;
            let alpha = heat_intensity * (0.35 - i as f32 * 0.07);
            draw_circle(rx, ry, 25.0 * scale, Color::new(1.0, 0.4 + i as f32 * 0.05, 0.05, alpha));
        }
    }
}
