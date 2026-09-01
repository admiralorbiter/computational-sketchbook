use macroquad::prelude::*;

#[derive(Debug, Clone)]
pub enum BuilderAction {
    SelectPalette(String),
    PlaceSelected,
    SelectCanvas(usize),
    RemoveSelected,
    Launch,
    Clear,
    Back,
    SetStageLeft,
    SetStageRight,
}

pub fn sample_builder_input() -> Vec<BuilderAction> {
    let mut actions = Vec::new();

    // Delete / Backspace removes selected part
    if is_key_pressed(KeyCode::Delete) || is_key_pressed(KeyCode::Backspace) {
        actions.push(BuilderAction::RemoveSelected);
    }

    // Enter places palette part OR launches depending on context,
    // let's say 'Enter' places palette part if one is highlighted, otherwise Launch if rocket valid?
    // Actually, maybe space or enter places it.
    if is_key_pressed(KeyCode::Enter) {
        actions.push(BuilderAction::PlaceSelected);
    }
    
    // Quick Launch override binding to L
    if is_key_pressed(KeyCode::L) {
        actions.push(BuilderAction::Launch);
    }

    // Clear binding
    if is_key_pressed(KeyCode::R) {
        actions.push(BuilderAction::Clear);
    }

    // Back to main menu
    if is_key_pressed(KeyCode::Escape) {
        actions.push(BuilderAction::Back);
    }

    actions
}
