use macroquad::prelude::*;
use crate::app::{AppState, PLANET_RADIUS};
use crate::sim::{RocketState, EventLog};

pub struct DebugOverlay {
    pub enabled: bool,
}

impl DebugOverlay {
    pub fn new() -> Self {
        Self { enabled: false }
    }

    pub fn toggle(&mut self) {
        self.enabled = !self.enabled;
    }

    pub fn draw(&self, state: &AppState, rocket: &RocketState, events: &EventLog, sim_dt: f32, time_scale: u32) {
        if !self.enabled {
            return;
        }

        let margin = 10.0;
        let font_size = 20.0;
        let mut y = margin + font_size;

        let state_name = match state {
            AppState::MainMenu => "MainMenu",
            AppState::MissionSelect => "MissionSelect",
            AppState::Builder => "Builder",
            AppState::Flight => "Flight",
            AppState::Map => "Map",
            AppState::Debrief => "Debrief",
            AppState::Paused { .. } => "Paused",
        };

        let fps = get_fps();
        let altitude = (rocket.position.length() - PLANET_RADIUS as f64) as f32;
        
        let last_event_str = if let Some((_, evt)) = events.entries().last() {
            format!("{:?}", evt)
        } else {
            "None".to_string()
        };

        let mut lines = vec![
            format!("App State: {}", state_name),
            format!("FPS: {}", fps),
            format!("Sim DT: {:.2}ms", sim_dt * 1000.0),
            format!("Time Scale: {}x", time_scale),
        ];

        if *state == AppState::Flight {
            lines.extend(vec![
                format!("Pos: ({:.0}, {:.0})", rocket.position.x, rocket.position.y),
                format!("Alt: {:.1}m", altitude),
                format!("Speed: {:.1}m/s", rocket.velocity.length()),
                format!("Vel: ({:.1}, {:.1})", rocket.velocity.x, rocket.velocity.y),
                format!("Mass: {:.1}kg", rocket.total_mass()),
                format!("Throttle: {:.0}%", rocket.throttle * 100.0),
                format!("Stage: {} / {}", rocket.current_stage, rocket.stages.len()),
                format!("Last Evt: {}", last_event_str),
            ]);
        }

        lines.push("[F3 to hide]".to_string());

        for line in lines.iter() {
            // Draw simple black background for text readability
            let text_size = measure_text(line, None, font_size as u16, 1.0);
            draw_rectangle(
                margin - 2.0,
                y - font_size + 2.0,
                text_size.width + 4.0,
                text_size.height + 4.0,
                Color::new(0.0, 0.0, 0.0, 0.5),
            );
            draw_text(line, margin, y, font_size, YELLOW);
            y += font_size + 5.0;
        }
    }
}
