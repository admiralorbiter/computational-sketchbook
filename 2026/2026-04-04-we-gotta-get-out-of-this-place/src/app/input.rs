use macroquad::prelude::*;

#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct InputState {
    pub throttle_up: bool,
    pub throttle_down: bool,
    pub rotate_left: bool,
    pub rotate_right: bool,
    pub stage: bool,
    pub map_toggle: bool,
    pub pause: bool,
    pub debug_toggle: bool,
    pub time_warp_up: bool,
    pub time_warp_down: bool,
    pub scroll_delta: f32,  // positive = zoom in, negative = zoom out
}

impl InputState {
    pub fn sample() -> Self {
        let (_, scroll_y) = mouse_wheel();
        Self {
            throttle_up: is_key_down(KeyCode::W) || is_key_down(KeyCode::Up),
            throttle_down: is_key_down(KeyCode::S) || is_key_down(KeyCode::Down),
            rotate_left: is_key_down(KeyCode::A) || is_key_down(KeyCode::Left),
            rotate_right: is_key_down(KeyCode::D) || is_key_down(KeyCode::Right),
            stage: is_key_pressed(KeyCode::Space),
            map_toggle: is_key_pressed(KeyCode::M),
            pause: is_key_pressed(KeyCode::Escape) || is_key_pressed(KeyCode::P),
            debug_toggle: is_key_pressed(KeyCode::F3),
            time_warp_up: is_key_pressed(KeyCode::Period),
            time_warp_down: is_key_pressed(KeyCode::Comma),
            scroll_delta: scroll_y,
        }
    }
}
