mod app;
mod debug;
mod render;
mod sim;
mod ui;
pub mod data;

use app::{AppState, InputState, WINDOW_WIDTH, WINDOW_HEIGHT, FIXED_TIMESTEP, INITIAL_ZOOM_M_PER_PIXEL, PLANET_RADIUS};
use sim::RocketState;
use sim::events::FlightEvent;
use macroquad::prelude::*;
use data::PartLibrary;
use data::schema::blueprint::RocketBlueprint;
use data::validate::validate_blueprint;
use ui::builder::BuilderSession;
use app::GameState;
use render::particles::ParticleSystem;
use render::starfield::Starfield;
use render::camera_shake::CameraShake;

fn window_conf() -> Conf {
    Conf {
        window_title: "We Gotta Get Out of This Place".to_owned(),
        window_width: WINDOW_WIDTH,
        window_height: WINDOW_HEIGHT,
        high_dpi: false,
        ..Default::default()
    }
}

#[macroquad::main(window_conf)]
async fn main() {
    let mut accumulator: f32 = 0.0;

    // Load external data
    let mut part_lib = PartLibrary::new();
    part_lib.load_dir("assets/parts").expect("Failed to load parts");

    let preset_paths = [
        "assets/presets/beater.ron",
        "assets/presets/featherweight.ron",
        "assets/presets/bruiser.ron",
    ];
    let mut blueprints = Vec::new();
    for p in preset_paths {
        let bp: RocketBlueprint = data::load_ron(p).unwrap_or_else(|e| panic!("Failed to load {}: {:?}", p, e));
        let issues = validate_blueprint(&bp, &part_lib);
        for issue in issues {
            println!("Blueprint {} validation: {:?}", bp.id, issue);
        }
        blueprints.push(bp);
    }

    let initial_rocket = RocketState::from_blueprint(&blueprints[0], &part_lib, PLANET_RADIUS as f64).expect("Failed to init rocket");
    let mut gs = GameState::new(initial_rocket, BuilderSession::new(), blueprints, part_lib);
    let mut builder_ui_actions = Vec::new();

    // Y-up camera for flight view
    let mut camera = Camera2D {
        target: vec2(0.0, PLANET_RADIUS + 100.0),
        zoom: vec2(
            1.0 / (INITIAL_ZOOM_M_PER_PIXEL * (screen_width() / 2.0)),
            -1.0 / (INITIAL_ZOOM_M_PER_PIXEL * (screen_height() / 2.0)),
        ),
        ..Default::default()
    };
    // Map camera
    let mut map_cam = Camera2D {
        target: vec2(0.0, PLANET_RADIUS),
        zoom: vec2(1.0 / (PLANET_RADIUS * 2.5), -1.0 / (PLANET_RADIUS * 2.5 * (screen_height() / screen_width()))),
        ..Default::default()
    };

    // User-controlled zoom multipliers (1.0 = default, scroll to adjust)
    let mut flight_user_zoom: f32 = 1.0;
    let mut map_user_zoom: f32 = 1.0;

    // Visual systems
    let mut particles = ParticleSystem::new();
    let starfield = Starfield::new(); // generated once, static
    let mut shake = CameraShake::new();

    // Track event count to detect new events each frame for camera shake triggers
    let mut last_event_count: usize = 0;

    loop {
        let frame_dt = get_frame_time().min(0.1);

        // --- Input ---
        let input = InputState::sample();

        // Screen routing shortcuts
        if is_key_pressed(KeyCode::Key1) { gs.transition_to(AppState::MainMenu); }
        if is_key_pressed(KeyCode::Key2) { gs.transition_to(AppState::Builder); }
        if is_key_pressed(KeyCode::Key3) { gs.transition_to(AppState::Flight); }
        if is_key_pressed(KeyCode::Key4) { gs.transition_to(AppState::Map); }

        if gs.app_state == AppState::Builder {
            let mut actions = crate::ui::builder_input::sample_builder_input();
            actions.append(&mut builder_ui_actions);

            let mut revalidate_needed = false;
            for action in actions {
                match action {
                    crate::ui::builder_input::BuilderAction::SelectPalette(id) => gs.builder_session.selected_palette_id = Some(id),
                    crate::ui::builder_input::BuilderAction::PlaceSelected => {
                        if let Some(id) = gs.builder_session.selected_palette_id.clone() {
                            gs.builder_session.add_part(&id, &gs.part_lib);
                            revalidate_needed = true;
                        }
                    },
                    crate::ui::builder_input::BuilderAction::SelectCanvas(idx) => gs.builder_session.selected_canvas_idx = Some(idx),
                    crate::ui::builder_input::BuilderAction::RemoveSelected => {
                        if let Some(idx) = gs.builder_session.selected_canvas_idx {
                            gs.builder_session.parts.remove(idx);
                            gs.builder_session.selected_canvas_idx = None;
                            revalidate_needed = true;
                        }
                    },
                    crate::ui::builder_input::BuilderAction::Launch => {
                        if !gs.builder_session.parts.is_empty() {
                            let bp = gs.builder_session.to_blueprint();
                            let issues = validate_blueprint(&bp, &gs.part_lib);
                            let has_error = issues.iter().any(|i| matches!(i.severity, crate::data::validate::ValidationSeverity::Error));
                            if !has_error {
                                gs.rocket = RocketState::from_blueprint(&bp, &gs.part_lib, PLANET_RADIUS as f64).expect("Failed to build rocket");
                                gs.events.reset();
                                gs.flight_stats.reset();
                                last_event_count = 0;
                                particles = ParticleSystem::new();
                                gs.transition_to(AppState::Flight);
                            }
                        }
                    },
                    crate::ui::builder_input::BuilderAction::Clear => {
                        gs.builder_session.clear();
                        revalidate_needed = true;
                    },
                    crate::ui::builder_input::BuilderAction::Back => {
                        gs.transition_to(AppState::MainMenu);
                    },
                    crate::ui::builder_input::BuilderAction::SetStageLeft => {
                        // Stage re-assignment handled inside builder UI
                    },
                    crate::ui::builder_input::BuilderAction::SetStageRight => {
                        // Stage re-assignment handled inside builder UI
                    },
                }
            }
            if revalidate_needed {
                gs.builder_session.revalidate(&gs.part_lib);
            }
        }

        if input.debug_toggle {
            gs.debug_overlay.toggle();
        }

        // Demo preset switching
        if matches!(gs.app_state, AppState::Flight | AppState::Map) {
            if is_key_pressed(KeyCode::RightBracket) {
                gs.current_preset_idx = (gs.current_preset_idx + 1) % gs.blueprints.len();
                gs.rocket = RocketState::from_blueprint(&gs.blueprints[gs.current_preset_idx], &gs.part_lib, PLANET_RADIUS as f64).expect("Launch failed");
                gs.events.reset();
                gs.flight_stats.reset();
            } else if is_key_pressed(KeyCode::LeftBracket) {
                if gs.current_preset_idx == 0 {
                    gs.current_preset_idx = gs.blueprints.len() - 1;
                } else {
                    gs.current_preset_idx -= 1;
                }
                gs.rocket = RocketState::from_blueprint(&gs.blueprints[gs.current_preset_idx], &gs.part_lib, PLANET_RADIUS as f64).expect("Launch failed");
                gs.events.reset();
                gs.flight_stats.reset();
            }
        }

        // Restart shortcut
        if gs.app_state == AppState::Flight && is_key_pressed(KeyCode::R) {
            gs.rocket = RocketState::from_blueprint(&gs.blueprints[gs.current_preset_idx], &gs.part_lib, PLANET_RADIUS as f64).unwrap();
            gs.events.reset();
            gs.flight_stats.reset();
            particles = ParticleSystem::new();
        }
        // Relaunch from debrief
        if gs.app_state == AppState::Debrief && is_key_pressed(KeyCode::R) {
            gs.rocket = RocketState::from_blueprint(&gs.blueprints[gs.current_preset_idx], &gs.part_lib, PLANET_RADIUS as f64).unwrap();
            gs.events.reset();
            gs.flight_stats.reset();
            particles = ParticleSystem::new();
            gs.transition_to(AppState::Flight);
        }

        // Time warp
        let valid_scales: [u32; 5] = [1, 2, 5, 10, 50];
        if matches!(gs.app_state, AppState::Flight | AppState::Map) {
            if input.time_warp_up {
                if let Some(idx) = valid_scales.iter().position(|&s| s == gs.time_scale) {
                    if idx < valid_scales.len() - 1 { gs.time_scale = valid_scales[idx + 1]; }
                } else { gs.time_scale = 1; }
            }
            if input.time_warp_down {
                if let Some(idx) = valid_scales.iter().position(|&s| s == gs.time_scale) {
                    if idx > 0 { gs.time_scale = valid_scales[idx - 1]; }
                } else { gs.time_scale = 1; }
            }
        } else {
            gs.time_scale = 1;
        }

        // --- Scroll zoom ---
        const ZOOM_STEP: f32 = 1.05;
        if matches!(gs.app_state, AppState::Flight) && input.scroll_delta.abs() > 0.01 {
            let dir = input.scroll_delta.signum();
            if dir > 0.0 { flight_user_zoom *= ZOOM_STEP; }
            else         { flight_user_zoom /= ZOOM_STEP; }
            flight_user_zoom = flight_user_zoom.clamp(0.25, 3.0);
        }
        if matches!(gs.app_state, AppState::Map) && input.scroll_delta.abs() > 0.01 {
            let dir = input.scroll_delta.signum();
            if dir > 0.0 { map_user_zoom *= ZOOM_STEP; }
            else         { map_user_zoom /= ZOOM_STEP; }
            map_user_zoom = map_user_zoom.clamp(0.25, 3.0);
        }

        // --- Camera shake: detect new events ---
        let current_event_count = gs.events.entries().len();
        if current_event_count > last_event_count {
            for (_, evt) in &gs.events.entries()[last_event_count..] {
                match evt {
                    FlightEvent::LaunchStarted        => shake.add_trauma(0.75),
                    FlightEvent::StageSeparated(_)    => shake.add_trauma(0.50),
                    FlightEvent::Crashed(_)           => shake.add_trauma(0.90),
                    _                                 => {}
                }
            }
            last_event_count = current_event_count;
        }
        shake.update(frame_dt);

        // --- Camera Adaptive Zoom & Follow ---
        let altitude = (gs.rocket.position.length() - PLANET_RADIUS as f64) as f32;
        let auto_zoom_scale = (1.0 + (altitude.max(0.0) / 50_000.0)).sqrt();
        let base_zoom_x = 1.0 / (INITIAL_ZOOM_M_PER_PIXEL * (screen_width() / 2.0));
        let base_zoom_y = -1.0 / (INITIAL_ZOOM_M_PER_PIXEL * (screen_height() / 2.0));

        let shake_offset = shake.offset(8.0 / (base_zoom_x * auto_zoom_scale)); // 8 screen pixels max
        let rocket_pos = vec2(gs.rocket.position.x as f32, gs.rocket.position.y as f32);
        camera.target = rocket_pos + shake_offset;
        camera.zoom = vec2(
            base_zoom_x / auto_zoom_scale * flight_user_zoom,
            base_zoom_y / auto_zoom_scale * flight_user_zoom,
        );

        // --- Physics ticks ---
        accumulator += frame_dt;
        accumulator = accumulator.min(FIXED_TIMESTEP * 4.0);

        while accumulator >= FIXED_TIMESTEP {
            if matches!(gs.app_state, AppState::Flight | AppState::Map) {
                let ticks = gs.time_scale;
                for i in 0..ticks {
                    let mut tick_input = input.clone();
                    if i > 0 { tick_input.stage = false; }
                    sim::flight::tick(&mut gs.rocket, &tick_input, &mut gs.events, &gs.tunables, FIXED_TIMESTEP, &mut gs.time_scale);

                    // Update flight stats each tick
                    let alt_now = (gs.rocket.position.length() as f32) - PLANET_RADIUS;
                    if alt_now > gs.flight_stats.max_altitude_m {
                        gs.flight_stats.max_altitude_m = alt_now;
                    }
                    let spd_now = gs.rocket.velocity.length() as f32;
                    if spd_now > gs.flight_stats.max_speed_mps {
                        gs.flight_stats.max_speed_mps = spd_now;
                    }
                    gs.flight_stats.flight_time_s += FIXED_TIMESTEP;
                    if gs.rocket.has_achieved_orbit {
                        gs.flight_stats.achieved_orbit = true;
                    }

                    if gs.time_scale < ticks { break; }
                }
            }
            accumulator -= FIXED_TIMESTEP;
        }

        // --- Particle system update & emission ---
        if matches!(gs.app_state, AppState::Flight) {
            let is_burning = gs.rocket.throttle > 0.0 && gs.rocket.fuel_remaining() > 0.0
                && matches!(gs.rocket.flight_status, sim::rocket::FlightStatus::Flying);

            if is_burning {
                let forward = Vec2::new(gs.rocket.rotation.sin(), gs.rocket.rotation.cos());
                let length = 40.0;
                let rocket_world = vec2(gs.rocket.position.x as f32, gs.rocket.position.y as f32);
                let engine_base = rocket_world + forward * (length * 0.5) - forward * length;
                // Emit more particles at higher time warp to keep the trail looking continuous
                let emit_count = (3 + gs.time_scale * 2).min(30);
                particles.emit_exhaust(emit_count, engine_base, forward, gs.rocket.throttle);
            }

            // Stage burst
            let new_events = gs.events.entries().len();
            if new_events > last_event_count.saturating_sub(1) {
                // Scan very recent for StageSeparated
                for (_, evt) in gs.events.entries().iter().rev().take(5) {
                    if let FlightEvent::StageSeparated(_) = evt {
                        let rocket_world = vec2(gs.rocket.position.x as f32, gs.rocket.position.y as f32);
                        particles.emit_stage_burst(rocket_world);
                    }
                }
            }

            particles.update(frame_dt * gs.time_scale as f32);
        }

        // --- Update fuel used in flight stats ---
        let fuel_remaining = gs.rocket.fuel_remaining();
        let fuel_cap = gs.rocket.fuel_capacity();
        gs.flight_stats.total_fuel_kg = fuel_cap + gs.flight_stats.fuel_used_kg;
        gs.flight_stats.fuel_used_kg = (gs.flight_stats.total_fuel_kg - fuel_remaining).max(0.0);

        // --- Auto-transition to Debrief ---
        if matches!(gs.app_state, AppState::Flight | AppState::Map) {
            use sim::rocket::FlightStatus;
            match &gs.rocket.flight_status {
                FlightStatus::Crashed { cause } => {
                    gs.flight_stats.crash_cause = Some(format!("{:?}", cause));
                    gs.transition_to(AppState::Debrief);
                }
                FlightStatus::Landed => {
                    gs.transition_to(AppState::Debrief);
                }
                _ => {}
            }
        }

        // Map camera zoom
        map_cam.zoom = vec2(
            1.0 / (PLANET_RADIUS * 2.5 * (screen_width() / screen_height())) * map_user_zoom,
            -1.0 / (PLANET_RADIUS * 2.5) * map_user_zoom
        );

        // --- Render ---
        builder_ui_actions = render::draw(
            &gs.app_state, gs.time_scale, &gs.rocket, &gs.debug_overlay,
            &gs.tunables, &gs.events, FIXED_TIMESTEP,
            &camera, &map_cam,
            Some(&gs.builder_session), Some(&gs.part_lib),
            &particles, &starfield, &gs.flight_stats,
        );

        if gs.debug_overlay.enabled {
            crate::ui::tunables::update_and_draw(&mut gs.tunables);
        }

        next_frame().await;
    }
}
