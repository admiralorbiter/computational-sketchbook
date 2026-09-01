use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PartCategory {
    Command,
    Tank,
    Engine,
    Decoupler,
    Payload,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PartTag {
    Command,
    Engine,
    Tank,
    Decoupler,
    Recovery,
    Payload,
    Stability,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PartDef {
    pub id: String,
    pub display_name: String,
    pub category: PartCategory,
    pub dry_mass: f32, // kg
    pub fuel_capacity: f32, // kg
    pub thrust_vacuum: f32, // N
    pub isp: f32, // seconds
    pub drag_coefficient: f32,
    pub reference_area: f32, // m^2
    pub tags: Vec<PartTag>,
    
    #[allow(dead_code)]
    #[serde(default)]
    pub cost: u32,
}
