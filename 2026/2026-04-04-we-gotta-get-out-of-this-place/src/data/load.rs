use anyhow::{Context, Result};
use std::fs;

pub fn load_ron<T: for<'de> serde::Deserialize<'de>>(path: &str) -> Result<T> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path))?;
    
    let parsed: T = ron::from_str(&content)
        .with_context(|| format!("Failed to parse RON file: {}", path))?;
        
    Ok(parsed)
}
