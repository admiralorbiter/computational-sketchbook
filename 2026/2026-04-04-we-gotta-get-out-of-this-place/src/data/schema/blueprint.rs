use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PartInstance {
    pub part_id: String,
    pub instance_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StageConfig {
    pub order: usize,
    pub engine_ids: Vec<String>,
    pub tank_ids: Vec<String>,
    pub decoupler_ids: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RocketBlueprint {
    pub id: String,
    pub display_name: String,
    pub parts: Vec<PartInstance>,
    pub stages: Vec<StageConfig>,
}
