use std::collections::HashMap;
use crate::data::schema::part::PartDef;
use crate::data::load_ron;

pub struct PartLibrary {
    pub parts: HashMap<String, PartDef>,
}

impl Default for PartLibrary {
    fn default() -> Self {
        Self::new()
    }
}

impl PartLibrary {
    pub fn new() -> Self {
        Self { parts: HashMap::new() }
    }

    pub fn load_dir(&mut self, dir_path: &str) -> anyhow::Result<()> {
        let entries = std::fs::read_dir(dir_path)?;
        for entry in entries {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("ron") {
                let part: PartDef = load_ron(path.to_str().unwrap())?;
                self.parts.insert(part.id.clone(), part);
            }
        }
        Ok(())
    }

    pub fn get(&self, id: &str) -> Option<&PartDef> {
        self.parts.get(id)
    }
}
