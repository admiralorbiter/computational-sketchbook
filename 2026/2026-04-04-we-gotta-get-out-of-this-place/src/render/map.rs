use macroquad::prelude::*;
use crate::sim::RocketState;
use crate::app::{PLANET_RADIUS, ATMOSPHERE_HEIGHT};
use crate::ui::widgets::draw_text_with_bg;

/// Convert a world-space position to screen-space pixel coordinates given the active map camera.
fn world_to_screen(world: Vec2, cam: &Camera2D) -> Vec2 {
    let sw = screen_width();
    let sh = screen_height();
    let ndc_x = (world.x - cam.target.x) * cam.zoom.x;
    let ndc_y = (world.y - cam.target.y) * cam.zoom.y; // zoom.y is negative (Y-up)
    Vec2::new(
        (ndc_x + 1.0) * sw * 0.5,
        (1.0 - ndc_y) * sh * 0.5,
    )
}

const LAUNCH_SITE: Vec2 = Vec2::new(0.0, PLANET_RADIUS); // world-space

pub fn draw_map(rocket: &RocketState, cam: &Camera2D) {
    // Background already cleared by render/mod.rs

    // --- Planet ---
    draw_circle(0.0, 0.0, PLANET_RADIUS, DARKGRAY);
    // Subtle polar cap
    draw_circle(0.0, PLANET_RADIUS * 0.85, PLANET_RADIUS * 0.22, Color::new(0.40, 0.40, 0.42, 1.0));
    // Planet edge rim
    draw_circle_lines(0.0, 0.0, PLANET_RADIUS, 8_000.0, Color::new(0.50, 0.50, 0.52, 0.6));

    // --- Atmosphere Ring (layered for glow) ---
    draw_circle_lines(0.0, 0.0, PLANET_RADIUS + ATMOSPHERE_HEIGHT, 18_000.0, Color::new(0.3, 0.6, 0.9, 0.15));
    draw_circle_lines(0.0, 0.0, PLANET_RADIUS + ATMOSPHERE_HEIGHT * 0.85, 12_000.0, Color::new(0.35, 0.65, 0.92, 0.12));

    // --- Orbit ellipse + markers ---
    if let Some(params) = &rocket.orbital_params {
        if let Some(ellipse) = &params.ellipse {
            let orbit_color = match params.path {
                crate::sim::orbit::PathType::StableOrbit => GREEN,
                crate::sim::orbit::PathType::Escaping    => PURPLE,
                _                                        => YELLOW,
            };

            let num_segments = 192;
            let mut points = Vec::with_capacity(num_segments + 1);
            let cos_rot = ellipse.rotation.cos() as f32;
            let sin_rot = ellipse.rotation.sin() as f32;

            for i in 0..=num_segments {
                let theta = (i as f32) * std::f32::consts::PI * 2.0 / (num_segments as f32);
                let x_local = (ellipse.semi_major as f32) * theta.cos();
                let y_local = (ellipse.semi_minor as f32) * theta.sin();
                let x_world = ellipse.center.x as f32 + x_local * cos_rot - y_local * sin_rot;
                let y_world = ellipse.center.y as f32 + x_local * sin_rot + y_local * cos_rot;
                points.push(Vec2::new(x_world, y_world));
            }

            for i in 0..num_segments {
                draw_line(points[i].x, points[i].y, points[i+1].x, points[i+1].y, 12_000.0, orbit_color);
            }

            // Prograde direction arrow at midpoint of orbit
            let mid_idx = num_segments / 4;
            if mid_idx + 1 < points.len() {
                let mp = points[mid_idx];
                let md = (points[mid_idx + 1] - mp).normalize_or_zero();
                let arrow_size = 35_000.0;
                let mp2 = mp + md * arrow_size;
                let perp = Vec2::new(-md.y, md.x);
                draw_triangle(mp2, mp - perp * arrow_size * 0.4, mp + perp * arrow_size * 0.4, orbit_color);
            }

            // APO marker (world space)
            let apo = Vec2::new(ellipse.apoapsis_point.x as f32, ellipse.apoapsis_point.y as f32);
            draw_circle(apo.x, apo.y, 22_000.0, SKYBLUE);

            // PER marker (world space)
            let per = Vec2::new(ellipse.periapsis_point.x as f32, ellipse.periapsis_point.y as f32);
            let per_color = if params.periapsis_alt < 0.0 { ORANGE } else { SKYBLUE };
            draw_circle(per.x, per.y, 22_000.0, per_color);

            // --- Screen-space labels (switch camera, draw, restore) ---
            let apo_screen = world_to_screen(apo, cam);
            let per_screen = world_to_screen(per, cam);
            let apo_km = params.apoapsis_alt / 1000.0;
            let per_km = params.periapsis_alt / 1000.0;
            let apo_label = format!("APO {:.0}km", apo_km);
            let per_label = format!("PER {:.0}km", per_km);

            set_default_camera();
            draw_text_with_bg(&apo_label, apo_screen.x + 14.0, apo_screen.y + 5.0, 18.0, SKYBLUE);
            draw_text_with_bg(&per_label, per_screen.x + 14.0, per_screen.y + 5.0, 18.0, per_color);
            set_camera(cam); // restore map camera
        }
    }

    // --- Launch site marker (world space dot + screen-space label) ---
    draw_circle(LAUNCH_SITE.x, LAUNCH_SITE.y, 20_000.0, YELLOW);
    let launch_screen = world_to_screen(LAUNCH_SITE, cam);
    set_default_camera();
    draw_text_with_bg("LAUNCH", launch_screen.x + 12.0, launch_screen.y - 4.0, 16.0, YELLOW);
    set_camera(cam); // restore

    // --- Rocket icon (small oriented triangle arrow) ---
    let dir = if rocket.velocity.length_squared() > 1.0 {
        rocket.velocity.normalize()
    } else if rocket.position.length_squared() > 1.0 {
        rocket.position.normalize()
    } else {
        macroquad::math::DVec2::new(0.0, 1.0)
    };

    let rx = rocket.position.x as f32;
    let ry = rocket.position.y as f32;
    let fwd = Vec2::new(dir.x as f32, dir.y as f32);
    let rgt = Vec2::new(-fwd.y, fwd.x);
    let icon_size = 40_000.0;

    // Small rocket body along prograde
    draw_triangle(
        Vec2::new(rx, ry) + fwd * icon_size,
        Vec2::new(rx, ry) + rgt * icon_size * 0.45,
        Vec2::new(rx, ry) - rgt * icon_size * 0.45,
        WHITE,
    );
    // Velocity trail line
    let trail_end = Vec2::new(rx, ry) - fwd * icon_size * 1.5;
    draw_line(rx, ry, trail_end.x, trail_end.y, 6_000.0, Color::new(1.0, 1.0, 1.0, 0.35));
}
