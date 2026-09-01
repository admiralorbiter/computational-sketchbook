use crate::app::AppState;
use crate::sim::{RocketState, EventLog};
use crate::ui::builder::BuilderSession;
use crate::data::PartLibrary;
use crate::data::schema::blueprint::RocketBlueprint;
use crate::debug::DebugOverlay;
use crate::app::flight_stats::FlightStats;

pub struct GameState {
    pub app_state: AppState,
    pub rocket: RocketState,
    pub builder_session: BuilderSession,
    pub blueprints: Vec<RocketBlueprint>,
    pub current_preset_idx: usize,
    pub part_lib: PartLibrary,
    pub time_scale: u32,
    pub events: EventLog,
    pub debug_overlay: DebugOverlay,
    pub tunables: crate::debug::Tunables,
    pub flight_stats: FlightStats,
}

impl GameState {
    pub fn new(
        rocket: RocketState,
        builder_session: BuilderSession,
        blueprints: Vec<RocketBlueprint>,
        part_lib: PartLibrary,
    ) -> Self {
        Self {
            app_state: AppState::MainMenu,
            rocket,
            builder_session,
            blueprints,
            current_preset_idx: 0,
            part_lib,
            time_scale: 1,
            events: EventLog::new(),
            debug_overlay: DebugOverlay::new(),
            tunables: crate::debug::Tunables::new(),
            flight_stats: FlightStats::new(),
        }
    }

    pub fn transition_to(&mut self, next_state: AppState) {
        match next_state {
            AppState::Flight | AppState::Map => {
                // Keep time warp if transitioning between Flight and Map.
                if !matches!(self.app_state, AppState::Flight | AppState::Map) {
                    self.time_scale = 1;
                }
            },
            _ => {
                self.time_scale = 1;
            }
        }
        self.app_state = next_state;
    }
}
