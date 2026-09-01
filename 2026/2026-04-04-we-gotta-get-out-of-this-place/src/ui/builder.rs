use crate::data::schema::blueprint::{PartInstance, RocketBlueprint, StageConfig};
use crate::data::schema::part::PartCategory;
use crate::data::validate::{validate_blueprint, ValidationIssue};
use crate::data::PartLibrary;

#[derive(Debug, Clone)]
pub struct BuilderSession {
    pub display_name: String,
    pub parts: Vec<PartInstance>,
    pub stages: Vec<StageConfig>,
    
    // UI State
    pub selected_canvas_idx: Option<usize>,
    pub selected_palette_id: Option<String>,
    pub validation: Vec<ValidationIssue>,

    // For generating unique instance IDs
    instance_counter: usize,
}

impl BuilderSession {
    pub fn new() -> Self {
        Self {
            display_name: "New Rocket".to_string(),
            parts: Vec::new(),
            stages: Vec::new(),
            selected_canvas_idx: None,
            selected_palette_id: None,
            validation: Vec::new(),
            instance_counter: 0,
        }
    }

    pub fn to_blueprint(&self) -> RocketBlueprint {
        RocketBlueprint {
            id: "builder_custom".to_string(),
            display_name: self.display_name.clone(),
            parts: self.parts.clone(),
            stages: self.stages.clone(),
        }
    }

    pub fn revalidate(&mut self, library: &PartLibrary) {
        let bp = self.to_blueprint();
        self.validation = validate_blueprint(&bp, library);
    }

    pub fn add_part(&mut self, part_id: &str, _library: &PartLibrary) {
        let instance_id = format!("{}_{}", part_id, self.instance_counter);
        self.instance_counter += 1;

        self.parts.push(PartInstance {
            part_id: part_id.to_string(),
            instance_id,
        });

        // We defer auto-staging explicitly so user can auto-stage on demand,
        // or we auto-stage immediately. For MVP, just auto-assign.
        self.auto_stage_all(_library);
    }

    pub fn remove_selected(&mut self, library: &PartLibrary) {
        if let Some(idx) = self.selected_canvas_idx {
            if idx < self.parts.len() {
                self.parts.remove(idx);
                // Adjust selection
                if self.parts.is_empty() {
                    self.selected_canvas_idx = None;
                } else if idx >= self.parts.len() {
                    self.selected_canvas_idx = Some(self.parts.len() - 1);
                }
                self.auto_stage_all(library);
            }
        }
    }

    pub fn clear(&mut self) {
        self.parts.clear();
        self.stages.clear();
        self.selected_canvas_idx = None;
        self.instance_counter = 0;
        self.validation.clear();
    }

    /// Complete MVP auto-stager: dumps all tanks and engines into Stage 0.
    pub fn auto_stage_all(&mut self, library: &PartLibrary) {
        let mut engines = Vec::new();
        let mut tanks = Vec::new();

        for inst in &self.parts {
            if let Some(def) = library.get(&inst.part_id) {
                if def.category == PartCategory::Engine {
                    engines.push(inst.instance_id.clone());
                } else if def.category == PartCategory::Tank {
                    tanks.push(inst.instance_id.clone());
                }
                // TODO: Payload and Command parts are intentionally omitted from staging
                // for MVP. When decoupler support is added, Command/Payload mass above
                // a decoupler will need to be factored into upper-stage mass calculations.
            }
        }

        if engines.is_empty() && tanks.is_empty() {
            self.stages.clear();
            return;
        }

        self.stages = vec![StageConfig {
            order: 0,
            engine_ids: engines,
            tank_ids: tanks,
            decoupler_ids: Vec::new(),
        }];
    }

    pub fn nudge_stage(&mut self, dir: i32, library: &PartLibrary) {
        let selected_idx = match self.selected_canvas_idx {
            Some(idx) => idx,
            None => return,
        };

        if selected_idx >= self.parts.len() {
            return;
        }

        let inst = &self.parts[selected_idx];
        let def = match library.get(&inst.part_id) {
            Some(def) => def,
            None => return,
        };

        // Find current stage
        let mut curr_stage_idx = 0;
        let mut found = false;
        for (i, stage) in self.stages.iter().enumerate() {
            if stage.engine_ids.contains(&inst.instance_id) || stage.tank_ids.contains(&inst.instance_id) {
                curr_stage_idx = i;
                found = true;
                break;
            }
        }

        // If it's not anywhere, just default to stage 0
        if !found {
            if self.stages.is_empty() {
                self.stages.push(StageConfig {
                    order: 0,
                    engine_ids: Vec::new(),
                    tank_ids: Vec::new(),
                    decoupler_ids: Vec::new(),
                });
            }
            if def.category == PartCategory::Engine { self.stages[0].engine_ids.push(inst.instance_id.clone()); }
            if def.category == PartCategory::Tank { self.stages[0].tank_ids.push(inst.instance_id.clone()); }
            return; // done for this pass
        }

        let mut target_stage = curr_stage_idx as i32 + dir;
        if target_stage < 0 {
            target_stage = 0;
        }

        let target_stage = target_stage as usize;

        if target_stage == curr_stage_idx {
            return;
        }

        // Remove from current
        self.stages[curr_stage_idx].engine_ids.retain(|x| x != &inst.instance_id);
        self.stages[curr_stage_idx].tank_ids.retain(|x| x != &inst.instance_id);

        // Ensure target stage exists
        while self.stages.len() <= target_stage {
            let next_order = self.stages.len();
            self.stages.push(StageConfig {
                order: next_order,
                engine_ids: Vec::new(),
                tank_ids: Vec::new(),
                decoupler_ids: Vec::new(),
            });
        }

        // Add to new
        if def.category == PartCategory::Engine { self.stages[target_stage].engine_ids.push(inst.instance_id.clone()); }
        if def.category == PartCategory::Tank { self.stages[target_stage].tank_ids.push(inst.instance_id.clone()); }
        
        // Clean up empty stages from the end
        while self.stages.len() > 1 {
            let last = self.stages.last().unwrap();
            if last.engine_ids.is_empty() && last.tank_ids.is_empty() && last.decoupler_ids.is_empty() {
                self.stages.pop();
            } else {
                break;
            }
        }
    }

    // Quick helpers for UI stats preview
    pub fn total_mass(&self, library: &PartLibrary) -> f32 {
        self.parts.iter().filter_map(|p| library.get(&p.part_id)).map(|def| def.dry_mass + def.fuel_capacity).sum()
    }
    
    pub fn dry_mass(&self, library: &PartLibrary) -> f32 {
        self.parts.iter().filter_map(|p| library.get(&p.part_id)).map(|def| def.dry_mass).sum()
    }

    pub fn fuel_mass(&self, library: &PartLibrary) -> f32 {
        self.parts.iter().filter_map(|p| library.get(&p.part_id)).map(|def| def.fuel_capacity).sum()
    }

    pub fn stage_count(&self) -> usize {
        self.stages.len()
    }

    pub fn can_launch(&self) -> bool {
        // Safe to launch if there are no Error-level validations
        !self.validation.iter().any(|v| matches!(v.severity, crate::data::validate::ValidationSeverity::Error))
    }
}
