use macroquad::math::DVec2;
use crate::sim::events::CrashCause;
use crate::data::schema::blueprint::{RocketBlueprint, StageConfig};
use crate::data::schema::part::PartDef;
use crate::data::PartLibrary;
use crate::sim::orbit::OrbitalParams;

#[derive(Debug, Clone, PartialEq)]
pub enum FlightStatus {
    PreLaunch,
    Flying,
    Crashed { cause: CrashCause },
    Landed,
}

#[derive(Debug, Clone)]
pub struct TankState {
    pub instance_id: String,
    pub fuel_remaining: f32,
    pub capacity: f32,
}

#[derive(Debug, Clone)]
pub struct ResolvedPart {
    pub instance_id: String,
    pub def: PartDef,
}

#[allow(dead_code)]
pub struct RocketState {
    // Physical state (runtime, changes each tick)
    pub position: DVec2,         // world meters (f64 for precision at radius)
    pub velocity: DVec2,         // m/s
    pub rotation: f32,           // radians, 0 = pointing up
    pub angular_velocity: f32,   // rad/s
    pub throttle: f32,           // 0.0..1.0
    
    // Components and staging
    pub parts: Vec<ResolvedPart>,
    pub tanks: Vec<TankState>,
    pub stages: Vec<StageConfig>,
    pub current_stage: usize,

    pub is_active: bool,
    pub flight_status: FlightStatus,
    pub display_name: String,
    
    pub has_cleared_atmosphere: bool,
    pub has_achieved_orbit: bool,
    pub dropped_mass: f32,

    pub orbital_params: Option<OrbitalParams>,
}

impl RocketState {
    pub fn from_blueprint(blueprint: &RocketBlueprint, library: &PartLibrary, start_radius: f64) -> anyhow::Result<Self> {
        let mut resolved_parts = Vec::new();
        let mut tanks = Vec::new();

        for inst in &blueprint.parts {
            let def = library.get(&inst.part_id)
                .ok_or_else(|| anyhow::anyhow!("Blueprint references unknown part ID: {}", inst.part_id))?;
            
            resolved_parts.push(ResolvedPart {
                instance_id: inst.instance_id.clone(),
                def: def.clone(),
            });

            if def.fuel_capacity > 0.0 {
                tanks.push(TankState {
                    instance_id: inst.instance_id.clone(),
                    fuel_remaining: def.fuel_capacity,
                    capacity: def.fuel_capacity,
                });
            }
        }

        Ok(Self {
            position: DVec2::new(0.0, start_radius),
            velocity: DVec2::ZERO,
            rotation: 0.0,
            angular_velocity: 0.0,
            throttle: 0.0,
            
            parts: resolved_parts,
            tanks,
            stages: blueprint.stages.clone(),
            current_stage: 0,

            is_active: false,
            flight_status: FlightStatus::PreLaunch,
            display_name: blueprint.display_name.clone(),
            has_cleared_atmosphere: false,
            has_achieved_orbit: false,
            dropped_mass: 0.0,
            orbital_params: None,
        })
    }

    pub fn total_mass(&self) -> f32 {
        let dry_mass: f32 = self.parts.iter().map(|p| p.def.dry_mass).sum();
        let fuel_mass: f32 = self.tanks.iter().map(|t| t.fuel_remaining).sum();
        let m = dry_mass + fuel_mass - self.dropped_mass;
        m.max(10.0) // fail-safe to prevent divide-by-zero crashes
    }

    pub fn fuel_remaining(&self) -> f32 {
        self.tanks.iter().map(|t| t.fuel_remaining).sum()
    }
    
    pub fn fuel_capacity(&self) -> f32 {
        self.tanks.iter().map(|t| t.capacity).sum()
    }

    pub fn total_drag_area(&self) -> f32 {
        // Simplified: just sum the reference area multiplied by drag coefficient
        self.parts.iter().map(|p| p.def.drag_coefficient * p.def.reference_area).sum()
    }

    // Only engines in the current stage contribute thrust
    pub fn active_thrust_vacuum(&self) -> f32 {
        if self.current_stage >= self.stages.len() { return 0.0; }
        let stage = &self.stages[self.current_stage];
        
        let mut thrust = 0.0;
        for eng_id in &stage.engine_ids {
            if let Some(part) = self.parts.iter().find(|p| p.instance_id == *eng_id) {
                thrust += part.def.thrust_vacuum;
            }
        }
        thrust
    }

    // Average ISP of active engines (weighted by thrust)
    pub fn active_isp(&self) -> f32 {
        if self.current_stage >= self.stages.len() { return 1.0; }
        let stage = &self.stages[self.current_stage];
        
        let mut total_thrust = 0.0;
        let mut mass_flow = 0.0;
        
        for eng_id in &stage.engine_ids {
            if let Some(part) = self.parts.iter().find(|p| p.instance_id == *eng_id) {
                total_thrust += part.def.thrust_vacuum;
                if part.def.isp > 0.0 {
                    mass_flow += part.def.thrust_vacuum / (part.def.isp * 9.81);
                }
            }
        }
        
        if mass_flow > 0.0 {
            (total_thrust / mass_flow) / 9.81
        } else {
            1.0 // fallback to avoid div0
        }
    }
}
