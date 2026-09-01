use crate::data::schema::blueprint::RocketBlueprint;
use crate::data::schema::part::PartCategory;
use crate::data::PartLibrary;
use crate::app::SURFACE_GRAVITY;

#[derive(Debug, Clone)]
pub enum ValidationSeverity {
    Error,
    Warning,
    Info,
}

#[derive(Debug, Clone)]
pub struct ValidationIssue {
    pub severity: ValidationSeverity,
    pub message: String,
}

pub fn validate_blueprint(blueprint: &RocketBlueprint, library: &PartLibrary) -> Vec<ValidationIssue> {
    let mut issues = Vec::new();
    
    let mut unknown_parts = false;
    for inst in &blueprint.parts {
        if library.get(&inst.part_id).is_none() {
            issues.push(ValidationIssue {
                severity: ValidationSeverity::Error,
                message: format!("Unknown part ID referenced: '{}'", inst.part_id),
            });
            unknown_parts = true;
        }
    }
    
    if unknown_parts {
        return issues; 
    }

    let has_command = blueprint.parts.iter().any(|inst| {
        library.get(&inst.part_id).unwrap().category == PartCategory::Command
    });
    if !has_command {
        issues.push(ValidationIssue {
            severity: ValidationSeverity::Error,
            message: "Rocket has no Command module.".into(),
        });
    }

    if blueprint.stages.is_empty() {
        issues.push(ValidationIssue {
            severity: ValidationSeverity::Error,
            message: "Rocket has no stages.".into(),
        });
    } else {
        let launch_stage = &blueprint.stages[0];
        if launch_stage.engine_ids.is_empty() {
            issues.push(ValidationIssue {
                severity: ValidationSeverity::Error,
                message: "Launch stage (Stage 0) has no engines.".into(),
            });
        }
        
        let mut total_mass = 0.0;
        let mut stage_thrust = 0.0;
        
        for inst in &blueprint.parts {
            let part = library.get(&inst.part_id).unwrap();
            total_mass += part.dry_mass + part.fuel_capacity;
        }
        
        for act in &launch_stage.engine_ids {
            if let Some(inst) = blueprint.parts.iter().find(|p| p.instance_id == *act) {
                let part = library.get(&inst.part_id).unwrap();
                stage_thrust += part.thrust_vacuum;
            }
        }
        
        let twr = stage_thrust / (total_mass * SURFACE_GRAVITY);
        if twr > 0.0 && twr < 1.0 {
            issues.push(ValidationIssue {
                severity: ValidationSeverity::Warning,
                message: format!("Launch TWR is {:.2} (less than 1.0). Rocket will not lift off.", twr),
            });
        }
    }

    issues
}
