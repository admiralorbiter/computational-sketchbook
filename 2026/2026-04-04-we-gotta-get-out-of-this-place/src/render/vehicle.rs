use macroquad::prelude::*;
use crate::sim::RocketState;
use crate::sim::rocket::FlightStatus;

pub fn draw_vehicle(rocket: &RocketState) {
    let forward = Vec2::new(rocket.rotation.sin(), rocket.rotation.cos());
    let right = Vec2::new(rocket.rotation.cos(), -rocket.rotation.sin());

    let length = 40.0;
    let width = 10.0;

    let center = Vec2::new(rocket.position.x as f32, rocket.position.y as f32) + forward * (length * 0.5);

    let nose  = center + forward * (length * 0.5 + 4.0); // narrower / sharper
    let base  = center - forward * (length * 0.5);

    // Nose is narrower than the body for a sharper silhouette
    let nose_left  = center + forward * (length * 0.3) - right * (width * 0.35);
    let nose_right = center + forward * (length * 0.3) + right * (width * 0.35);

    let base_left  = base - right * (width * 0.5);
    let base_right = base + right * (width * 0.5);
    let top_left   = center + forward * (length * 0.3) - right * (width * 0.5);
    let top_right  = center + forward * (length * 0.3) + right * (width * 0.5);

    // --- Rocket body ---
    // Nose cone (sharper)
    draw_triangle(nose, nose_left, nose_right, WHITE);
    // Upper body
    draw_triangle(nose_left, top_left, nose_right, LIGHTGRAY);
    draw_triangle(nose_right, top_left, top_right, LIGHTGRAY);
    // Lower body
    draw_triangle(top_left, base_left, base_right, Color::new(0.75, 0.75, 0.78, 1.0));
    draw_triangle(top_left, base_right, top_right, Color::new(0.75, 0.75, 0.78, 1.0));

    // Stage separation marker line (subtle band at 30% up body)
    let sep_l = center + forward * 0.0 - right * (width * 0.52);
    let sep_r = center + forward * 0.0 + right * (width * 0.52);
    draw_line(sep_l.x, sep_l.y, sep_r.x, sep_r.y, 1.2, Color::new(0.2, 0.2, 0.25, 0.8));

    // --- Fins (two diagonal triangles at base) ---
    let fin_len   = 14.0;
    let fin_width = 5.0;
    // Left fin
    draw_triangle(
        base_left,
        base_left - right * fin_width,
        base_left - forward * fin_len,
        Color::new(0.55, 0.55, 0.60, 1.0),
    );
    // Right fin
    draw_triangle(
        base_right,
        base_right + right * fin_width,
        base_right - forward * fin_len,
        Color::new(0.55, 0.55, 0.60, 1.0),
    );

    // --- Landed legs ---
    if rocket.flight_status == FlightStatus::Landed {
        let leg_out  = right * (width * 1.2);
        let leg_down = -forward * (fin_len * 1.4);
        // Left leg
        draw_line(base_left.x, base_left.y, (base_left + leg_out * -0.4 + leg_down).x, (base_left + leg_out * -0.4 + leg_down).y, 2.5, GRAY);
        // Right leg
        draw_line(base_right.x, base_right.y, (base_right + leg_out * 0.4 + leg_down).x, (base_right + leg_out * 0.4 + leg_down).y, 2.5, GRAY);
    }

    // --- Exhaust flame ---
    if rocket.throttle > 0.0 && rocket.fuel_remaining() > 0.0 {
        let exhaust_len = 25.0 * rocket.throttle;
        let exhaust_tip = base - forward * exhaust_len;
        let inner_tip   = base - forward * (exhaust_len * 0.5);

        // Outer flame (orange)
        draw_triangle(base_left, exhaust_tip, base_right, ORANGE);
        // Inner core flame (yellow)
        draw_triangle(
            base - right * (width * 0.25),
            inner_tip,
            base + right * (width * 0.25),
            YELLOW,
        );
    }
}
