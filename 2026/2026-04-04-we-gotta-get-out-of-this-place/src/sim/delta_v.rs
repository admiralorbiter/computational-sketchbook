use crate::data::schema::blueprint::RocketBlueprint;
use crate::data::PartLibrary;

pub struct DeltaVBudget {
    pub per_stage: Vec<f64>,
    pub total: f64,
}

pub fn compute_delta_v(blueprint: &RocketBlueprint, lib: &PartLibrary) -> DeltaVBudget {
    let mut total_dv = 0.0;
    let mut per_stage = Vec::new();

    // In a logical rocket stack, the "active" mass during Stage N 
    // includes all parts of Stage N and all higher stages (N+1, N+2, ...).
    // Let's iterate from Stage 0 to Stage max.
    
    // First, map which parts belong to which stage.
    // In our simplified builder, parts are just assigned to stages.
    
    let g0 = 9.81;
    let mut current_wet_mass = blueprint.parts.iter().filter_map(|p| {
        lib.get(&p.part_id).map(|def| def.dry_mass + def.fuel_capacity)
    }).sum::<f32>() as f64;

    for stage_idx in 0..blueprint.stages.len() {
        let stage = &blueprint.stages[stage_idx];
        
        let mut stage_thrust = 0.0;
        let mut mass_flow = 0.0;
        let mut stage_fuel = 0.0;
        let mut stage_dry_mass = 0.0;

        for tank_id in &stage.tank_ids {
            if let Some(inst) = blueprint.parts.iter().find(|p| p.instance_id == *tank_id) {
                if let Some(def) = lib.get(&inst.part_id) {
                    stage_fuel += def.fuel_capacity as f64;
                    stage_dry_mass += def.dry_mass as f64;
                }
            }
        }
        
        for eng_id in &stage.engine_ids {
            if let Some(inst) = blueprint.parts.iter().find(|p| p.instance_id == *eng_id) {
                if let Some(def) = lib.get(&inst.part_id) {
                    stage_thrust += def.thrust_vacuum as f64;
                    if def.isp > 0.0 {
                        mass_flow += (def.thrust_vacuum as f64) / (def.isp as f64 * g0);
                    }
                    stage_dry_mass += def.dry_mass as f64;
                }
            }
        }

        // Add decouplers to dry mass too for completeness
        for dec_id in &stage.decoupler_ids {
            if let Some(inst) = blueprint.parts.iter().find(|p| p.instance_id == *dec_id) {
                if let Some(def) = lib.get(&inst.part_id) {
                    stage_dry_mass += def.dry_mass as f64;
                }
            }
        }

        if mass_flow > 0.0 && stage_fuel > 0.0 {
            let m_wet = current_wet_mass;
            let m_dry = current_wet_mass - stage_fuel;
            let ve = stage_thrust / mass_flow; // Effective exhaust velocity bypassing g0
            let dv = ve * (m_wet / m_dry).ln();
            per_stage.push(dv);
            total_dv += dv;
        } else {
            per_stage.push(0.0);
        }

        // Assume staging drops the dry mass of this stage along with the consumed fuel
        current_wet_mass -= stage_fuel + stage_dry_mass;
        if current_wet_mass < 0.0 { current_wet_mass = 0.0; }
    }

    DeltaVBudget {
        per_stage,
        total: total_dv,
    }
}
