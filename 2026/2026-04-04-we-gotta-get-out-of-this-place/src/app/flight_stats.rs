use macroquad::prelude::*;

/// Tracks peak flight statistics for the debrief screen.
#[derive(Debug, Clone, Default)]
pub struct FlightStats {
    pub max_altitude_m: f32,
    pub max_speed_mps: f32,
    pub flight_time_s: f32,
    pub fuel_used_kg: f32,
    pub stages_fired: usize,
    pub achieved_orbit: bool,
    pub crash_cause: Option<String>,
    pub total_fuel_kg: f32, // snapshot at launch for reference
}

impl FlightStats {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn reset(&mut self) {
        *self = Self::default();
    }

    /// Returns a brief summary string suitable for the debrief screen.
    pub fn max_altitude_str(&self) -> String {
        if self.max_altitude_m > 1_000_000.0 {
            format!("{:.0} Mm", self.max_altitude_m / 1_000_000.0)
        } else if self.max_altitude_m > 1_000.0 {
            format!("{:.1} km", self.max_altitude_m / 1000.0)
        } else {
            format!("{:.0} m", self.max_altitude_m)
        }
    }

    pub fn flight_time_str(&self) -> String {
        let mins = (self.flight_time_s / 60.0) as u32;
        let secs = (self.flight_time_s % 60.0) as u32;
        format!("{}m {}s", mins, secs)
    }
}

/// Draw the debrief screen given FlightStats.
pub fn draw_debrief_screen(stats: &FlightStats) {
    let cx = screen_width() / 2.0;

    // Background
    draw_rectangle(0.0, 0.0, screen_width(), screen_height(), Color::new(0.03, 0.04, 0.08, 1.0));

    // Title
    let title = if stats.crash_cause.is_some() { "FLIGHT ENDED — VEHICLE LOST" } else { "FLIGHT COMPLETE" };
    let title_color = if stats.crash_cause.is_some() { RED } else { GREEN };
    let ts = measure_text(title, None, 36, 1.0);
    draw_text(title, cx - ts.width / 2.0, 80.0, 36.0, title_color);

    // Divider
    draw_line(cx - 300.0, 100.0, cx + 300.0, 100.0, 1.0, DARKGRAY);

    // Stats table
    let font = 22.0;
    let col_label = cx - 220.0;
    let col_value = cx + 80.0;
    let row_h = 34.0;
    let start_y = 145.0;

    let rows: &[(&str, String, Color)] = &[
        ("Max Altitude:",     stats.max_altitude_str(),                  SKYBLUE),
        ("Max Speed:",        format!("{:.0} m/s", stats.max_speed_mps), WHITE),
        ("Flight Time:",      stats.flight_time_str(),                   WHITE),
        ("Fuel Used:",        format!("{:.0} kg", stats.fuel_used_kg),   if stats.fuel_used_kg >= stats.total_fuel_kg * 0.99 { ORANGE } else { WHITE }),
        ("Stages Fired:",     format!("{}", stats.stages_fired),          WHITE),
        ("Orbit Achieved:",   if stats.achieved_orbit { "YES".to_string() } else { "No".to_string() },
                              if stats.achieved_orbit { GREEN } else { GRAY }),
    ];

    for (i, (label, value, color)) in rows.iter().enumerate() {
        let y = start_y + i as f32 * row_h;
        draw_text(label, col_label, y, font, LIGHTGRAY);
        draw_text(value, col_value, y, font, *color);
    }

    if let Some(cause) = &stats.crash_cause {
        let y = start_y + rows.len() as f32 * row_h + 10.0;
        let msg = format!("Cause: {}", cause);
        let ms = measure_text(&msg, None, 20, 1.0);
        draw_text(&msg, cx - ms.width / 2.0, y, 20.0, ORANGE);
    }

    // Footer
    let footer = "[ R ] Relaunch   [ 2 ] Return to Builder";
    let fs = measure_text(footer, None, 18, 1.0);
    draw_text(footer, cx - fs.width / 2.0, screen_height() - 40.0, 18.0, DARKGRAY);
}
