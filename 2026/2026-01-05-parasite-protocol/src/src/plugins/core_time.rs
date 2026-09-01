use bevy::prelude::*;

pub struct CoreTimePlugin;

impl Plugin for CoreTimePlugin {
    fn build(&self, app: &mut App) {
        app
            .init_resource::<TimeScale>()
            .add_systems(Update, (
                handle_pause_input,
                handle_speed_input,
            ));
    }
}

#[derive(Resource, Default)]
pub struct TimeScale {
    pub scale: f32,
    pub is_paused: bool,
}

impl TimeScale {
    pub fn new() -> Self {
        Self {
            scale: 1.0,
            is_paused: false,
        }
    }

    pub fn effective_scale(&self) -> f32 {
        if self.is_paused {
            0.0
        } else {
            self.scale
        }
    }
}

fn handle_pause_input(
    keyboard_input: Res<Input<KeyCode>>,
    mut time_scale: ResMut<TimeScale>,
) {
    if keyboard_input.just_pressed(KeyCode::Space) {
        time_scale.is_paused = !time_scale.is_paused;
    }
}

fn handle_speed_input(
    keyboard_input: Res<Input<KeyCode>>,
    mut time_scale: ResMut<TimeScale>,
) {
    if time_scale.is_paused {
        return;
    }

    if keyboard_input.just_pressed(KeyCode::Key1) {
        time_scale.scale = 0.5;
    } else if keyboard_input.just_pressed(KeyCode::Key2) {
        time_scale.scale = 1.0;
    } else if keyboard_input.just_pressed(KeyCode::Key3) {
        time_scale.scale = 2.0;
    }
}

