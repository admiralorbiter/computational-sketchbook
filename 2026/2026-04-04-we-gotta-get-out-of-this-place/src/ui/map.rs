use macroquad::prelude::*;
use crate::sim::RocketState;
use crate::sim::orbit::PathType;
use crate::ui::widgets::draw_text_with_bg;

pub fn draw_map_ui(rocket: &RocketState, time_scale: u32) {
    let font_size = 20.0;
    
    // Top banner
    let banner_text = "MAP VIEW  (Press M or 3 to return to Flight)";
    let banner_size = measure_text(banner_text, None, font_size as u16, 1.0);
    draw_rectangle((screen_width() - banner_size.width) / 2.0 - 10.0, 10.0, banner_size.width + 20.0, banner_size.height + 20.0, Color::new(0.0, 0.0, 0.0, 0.7));
    draw_text(banner_text, (screen_width() - banner_size.width) / 2.0, 10.0 + font_size + 5.0, font_size, WHITE);

    if time_scale > 1 {
        draw_text_with_bg(&format!("▶▶ {}x", time_scale), screen_width() / 2.0 - 40.0, 60.0, 30.0, GOLD);
    }

    if let Some(params) = &rocket.orbital_params {
        let margin = 20.0;
        let mut y = screen_height() - 80.0;
        
        let path_str = match params.path {
            PathType::StableOrbit => "ORBIT: STABLE",
            PathType::Suborbital => "ORBIT: SUBORBITAL",
            PathType::Escaping => "ORBIT: ESCAPING",
            PathType::Ballistic => "ORBIT: BALLISTIC",
            PathType::Descending => "ORBIT: DESCENDING",
        };

        draw_text_with_bg(path_str, margin, y, font_size, WHITE);
        y += font_size + 5.0;

        let apo = if params.apoapsis_alt == f64::INFINITY { 
            "APO: Escaping".to_string() 
        } else if params.apoapsis_alt.abs() > 10_000.0 { 
            format!("APO: {:.1} km", params.apoapsis_alt / 1000.0) 
        } else { 
            format!("APO: {:.0} m", params.apoapsis_alt) 
        };
        
        let per = if params.periapsis_alt.is_nan() { 
            "PER: N/A".to_string() 
        } else if params.periapsis_alt.abs() > 10_000.0 { 
            format!("PER: {:.1} km", params.periapsis_alt / 1000.0) 
        } else { 
            format!("PER: {:.0} m", params.periapsis_alt) 
        };

        draw_text_with_bg(&apo, margin, y, font_size, SKYBLUE);
        y += font_size + 5.0;
        
        let per_color = if params.periapsis_alt < 0.0 { ORANGE } else { SKYBLUE };
        draw_text_with_bg(&per, margin, y, font_size, per_color);
        y += font_size + 5.0;

        if matches!(params.path, PathType::StableOrbit) {
            if let Some(t_seconds) = params.period_seconds(crate::app::SURFACE_GRAVITY as f64, crate::app::PLANET_RADIUS as f64) {
                let mins = (t_seconds / 60.0).floor() as u32;
                let secs = (t_seconds % 60.0).floor() as u32;
                draw_text_with_bg(&format!("OBT: {}m {}s", mins, secs), margin, y, font_size, GREEN);
            }
        }
    }
}

