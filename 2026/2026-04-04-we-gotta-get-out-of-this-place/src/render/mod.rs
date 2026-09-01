pub mod world;
pub mod vehicle;
pub mod builder;
pub mod map;
pub mod debug_draw;
pub mod starfield;
pub mod particles;
pub mod camera_shake;

use crate::app::{AppState, PLANET_RADIUS, ATMOSPHERE_HEIGHT};
use crate::debug::DebugOverlay;
use crate::sim::{RocketState, EventLog};
use crate::ui::builder::BuilderSession;
use crate::data::PartLibrary;
use crate::ui::builder_input::BuilderAction;
use crate::app::flight_stats::FlightStats;
use crate::render::particles::ParticleSystem;
use crate::render::starfield::Starfield;
use macroquad::prelude::*;

#[allow(clippy::too_many_arguments)]
pub fn draw(
    state: &AppState,
    time_scale: u32,
    rocket: &RocketState,
    debug: &DebugOverlay,
    tunables: &crate::debug::Tunables,
    events: &EventLog,
    sim_dt: f32,
    world_cam: &Camera2D,
    map_cam: &Camera2D,
    builder_session: Option<&BuilderSession>,
    library: Option<&PartLibrary>,
    particles: &ParticleSystem,
    starfield: &Starfield,
    flight_stats: &FlightStats,
) -> Vec<BuilderAction> {
    let mut ui_actions = Vec::new();

    // Always clear
    clear_background(Color::new(0.05, 0.05, 0.08, 1.0));

    match state {
        AppState::Flight => {
            set_camera(world_cam);

            // Starfield (behind everything)
            starfield.draw(world_cam.target);

            // World geometry
            world::draw_world(PLANET_RADIUS, ATMOSPHERE_HEIGHT, world_cam, rocket);

            // Particles (behind rocket)
            particles.draw();

            // Vehicle
            vehicle::draw_vehicle(rocket);

            if debug.enabled {
                crate::render::debug_draw::draw_vectors(rocket, tunables);
            }
        }
        AppState::Map => {
            set_camera(map_cam);
            starfield.draw(map_cam.target);
            map::draw_map(rocket, map_cam);
            set_default_camera();
        }
        AppState::Debrief => {
            set_default_camera();
            crate::app::flight_stats::draw_debrief_screen(flight_stats);
            return ui_actions;
        }
        _ => {}
    }

    // Pass 2: UI / Screen space
    set_default_camera();

    match state {
        AppState::MainMenu =>    crate::app::screens::draw_main_menu(),
        AppState::MissionSelect => crate::app::screens::draw_mission_select(),
        AppState::Builder => {
            if let (Some(sess), Some(lib)) = (builder_session, library) {
                ui_actions = builder::draw_builder(sess, lib);
            }
        },
        AppState::Flight => {
            crate::ui::hud::draw_hud(rocket, time_scale, events);
        },
        AppState::Map => {
            crate::ui::map::draw_map_ui(rocket, time_scale);
        },
        AppState::Debrief => { /* handled above */ },
        AppState::Paused { .. } => crate::app::screens::draw_paused(),
    }

    debug.draw(state, rocket, events, sim_dt, time_scale);

    // HUD particle count when debug enabled
    if debug.enabled {
        let msg = format!("Particles: {}", particles.particle_count());
        draw_text(&msg, 10.0, screen_height() - 20.0, 18.0, DARKGRAY);
    }

    ui_actions
}
