use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhysicsConstants {
    pub sea_level_density: f32,
    pub scale_height: f32,
    pub surface_gravity: f32,
    pub planet_radius: f32,
    pub atmosphere_height: f32,
}
