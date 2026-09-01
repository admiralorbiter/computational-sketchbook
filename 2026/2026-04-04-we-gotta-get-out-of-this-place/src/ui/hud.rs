use macroquad::prelude::*;
use crate::sim::{RocketState, rocket::FlightStatus};
use crate::sim::orbit::PathType;
use crate::app::PLANET_RADIUS;
use crate::ui::widgets::{draw_text_with_bg, draw_vertical_bar};

pub fn draw_hud(rocket: &RocketState, time_scale: u32, events: &crate::sim::EventLog) {
    let font_size = 20.0;
    let margin = 10.0;
    let text_x = margin;
    let mut text_y = margin + font_size;

    let altitude = (rocket.position.length() - PLANET_RADIUS as f64) as f32;
    let speed = rocket.velocity.length() as f32;
    
    // Vertical velocity is projection of velocity onto the position vector
    let up_dir = if rocket.position.length_squared() > 1e-6 { rocket.position.normalize() } else { macroquad::math::DVec2::ZERO };
    let vertical_speed = rocket.velocity.dot(up_dir) as f32;

    let thrust_dir = macroquad::math::DVec2::new(rocket.rotation.sin() as f64, rocket.rotation.cos() as f64);
    let pitch_rad = std::f64::consts::PI / 2.0 - thrust_dir.dot(up_dir).acos();
    let pitch_deg = pitch_rad * (180.0 / std::f64::consts::PI);

    // Formatting
    let _alt_str = if altitude > 10_000.0 {
        format!("Alt: {:.1} km", altitude / 1000.0)
    } else {
        format!("Alt: {:.0} m", altitude)
    };

    // Basic flight metrics
    let simple_metrics = [
        _alt_str,
        format!("Speed: {:.0} m/s", speed),
        format!("V. Speed: {:.0} m/s {}", vertical_speed.abs(), if vertical_speed >= 0.0 { "(+)" } else { "(-)" }),
        format!("Pitch: {:.0}°", pitch_deg),
    ];
    for m in simple_metrics.iter() {
        draw_text_with_bg(m, text_x, text_y, font_size, GREEN);
        text_y += font_size + 5.0;
    }

    // Throttle with bar
    let throttle_str = format!("Throttle: {:.0}%", rocket.throttle * 100.0);
    draw_text_with_bg(&throttle_str, text_x, text_y, font_size, GREEN);
    draw_vertical_bar(text_x + 130.0, text_y - font_size + 2.0, font_size, rocket.throttle, ORANGE, GREEN);
    text_y += font_size + 5.0;

    // Fuel with bar
    let fuel_frac = if rocket.fuel_capacity() > 0.0 { rocket.fuel_remaining() / rocket.fuel_capacity() } else { 0.0 };
    let fuel_color = if fuel_frac > 0.4 { GREEN } else if fuel_frac > 0.15 { ORANGE } else { RED };
    let fuel_str = format!("Fuel: {:.0} / {:.0} kg", rocket.fuel_remaining(), rocket.fuel_capacity());
    draw_text_with_bg(&fuel_str, text_x, text_y, font_size, fuel_color);
    draw_vertical_bar(text_x + 130.0, text_y - font_size + 2.0, font_size, fuel_frac, RED, GREEN);
    text_y += font_size + 5.0;
    
    text_y += 10.0; // gap before orbit stats

    if let Some(params) = &rocket.orbital_params {
        let apo_str = if params.apoapsis_alt == f64::INFINITY {
            "APO: Escaping".to_string()
        } else if params.apoapsis_alt > 10_000.0 {
            format!("APO: {:.1} km", params.apoapsis_alt / 1000.0)
        } else {
            format!("APO: {:.0} m", params.apoapsis_alt)
        };

        let per_str = if params.periapsis_alt.is_nan() {
            "PER: N/A".to_string()
        } else if params.periapsis_alt.abs() > 10_000.0 {
            format!("PER: {:.1} km", params.periapsis_alt / 1000.0)
        } else {
            format!("PER: {:.0} m", params.periapsis_alt)
        };

        let path_str = match params.path {
            PathType::StableOrbit => "PATH: STABLE ORBIT",
            PathType::Suborbital => "PATH: SUBORBITAL",
            PathType::Escaping => "PATH: ESCAPING",
            PathType::Ballistic => "PATH: BALLISTIC",
            PathType::Descending => "PATH: DESCENDING",
        };

        draw_text_with_bg(&apo_str, text_x, text_y, font_size, SKYBLUE);
        text_y += font_size + 5.0;
        
        let per_color = if params.periapsis_alt < 0.0 { ORANGE } else { SKYBLUE };
        draw_text_with_bg(&per_str, text_x, text_y, font_size, per_color);
        text_y += font_size + 5.0;

        let path_color = if params.path == PathType::StableOrbit { GREEN } else if params.path == PathType::Escaping { PURPLE } else { WHITE };
        draw_text_with_bg(path_str, text_x, text_y, font_size, path_color);
        text_y += font_size + 5.0;

        if matches!(params.path, PathType::StableOrbit) {
            if let Some(t_seconds) = params.period_seconds(crate::app::SURFACE_GRAVITY as f64, crate::app::PLANET_RADIUS as f64) {
                let mins = (t_seconds / 60.0).floor() as u32;
                let secs = (t_seconds % 60.0).floor() as u32;
                draw_text_with_bg(&format!("OBT: {}m {}s", mins, secs), text_x, text_y, font_size, GREEN);
                text_y += font_size + 5.0;
            }
        }
    }

    // Top-center status banner
    if matches!(rocket.flight_status, FlightStatus::Crashed { .. }) {
        draw_text_with_bg("ROCKET DESTROYED", screen_width() / 2.0 - 100.0, 50.0, 30.0, RED);
    } else if rocket.fuel_remaining() <= 0.0 && rocket.flight_status == FlightStatus::Flying {
        draw_text_with_bg("FUEL DEPLETED", screen_width() / 2.0 - 80.0, 50.0, 30.0, ORANGE);
    } else {
        let status_str = match &rocket.flight_status {
            FlightStatus::PreLaunch => "PRE-LAUNCH",
            FlightStatus::Flying => "FLYING",
            FlightStatus::Crashed { .. } => "CRASHED",
            FlightStatus::Landed => "LANDED",
        };
        draw_banner(status_str, WHITE);
    }

    if time_scale > 1 {
        draw_text_with_bg(&format!("▶▶ {}x", time_scale), screen_width() / 2.0 - 40.0, 90.0, 30.0, GOLD);
    }
    
    // Draw recent banners
    let recent = events.recent_events(4.0);
    let mut banner_y = 130.0;
    for e in &recent {
        let (text, color) = match e {
            crate::sim::events::FlightEvent::LaunchStarted => ("LAUNCH!".to_string(), WHITE),
            crate::sim::events::FlightEvent::StageSeparated(idx) => (format!("STAGE {} SEP", idx), ORANGE),
            crate::sim::events::FlightEvent::AtmosphereCleared => ("ATMOSPHERE CLEARED".to_string(), WHITE),
            crate::sim::events::FlightEvent::StableOrbitAchieved => ("STABLE ORBIT ACHIEVED".to_string(), GREEN),
            _ => continue,
        };
        draw_banner_at(&text, banner_y, color);
        banner_y += 50.0;
    }
}

fn draw_banner_at(text: &str, y: f32, color: Color) {
    let font_size = 30.0;
    let text_size = measure_text(text, None, font_size as u16, 1.0);
    let x = (screen_width() - text_size.width) / 2.0;

    draw_rectangle(
        x - 10.0,
        y - font_size + 2.0,
        text_size.width + 20.0,
        text_size.height + 10.0,
        Color::new(0.0, 0.0, 0.0, 0.7),
    );
    draw_text(text, x, y, font_size, color);
}


fn draw_banner(text: &str, color: Color) {
    let font_size = 30.0;
    let text_size = measure_text(text, None, font_size as u16, 1.0);
    let x = (screen_width() - text_size.width) / 2.0;
    let y = 40.0;

    draw_rectangle(
        x - 10.0,
        y - font_size + 2.0,
        text_size.width + 20.0,
        text_size.height + 10.0,
        Color::new(0.0, 0.0, 0.0, 0.7),
    );
    draw_text(text, x, y, font_size, color);
}
