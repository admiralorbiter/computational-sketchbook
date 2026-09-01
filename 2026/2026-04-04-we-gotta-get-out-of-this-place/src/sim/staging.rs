use crate::sim::rocket::RocketState;
use crate::sim::events::{EventLog, FlightEvent};

pub fn check_staging(rocket: &mut RocketState, events: &mut EventLog) -> bool {
    // Stage logic: advance current_stage
    // Returns true if a stage was advanced successfully
    if rocket.current_stage + 1 < rocket.stages.len() {
        let current_stage_idx = rocket.current_stage;
        let stage = &rocket.stages[current_stage_idx];
        
        let mut dry_mass_to_drop = 0.0;
        let mut add_mass = |id: &String| {
            if let Some(p) = rocket.parts.iter().find(|p| &p.instance_id == id) {
                dry_mass_to_drop += p.def.dry_mass;
            }
        };
        
        for id in &stage.engine_ids { add_mass(id); }
        for id in &stage.tank_ids { add_mass(id); }
        for id in &stage.decoupler_ids { add_mass(id); }
        
        rocket.dropped_mass += dry_mass_to_drop;
        rocket.current_stage += 1;
        events.push(FlightEvent::StageSeparated(rocket.current_stage));
        return true;
    }
    false
}
