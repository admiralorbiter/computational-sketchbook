use bevy::prelude::*;

mod plugins;

use plugins::*;

#[derive(States, Debug, Clone, PartialEq, Eq, Hash, Default)]
enum AppState {
    #[default]
    MainMenu,
    InRun,
}

#[derive(States, Debug, Clone, PartialEq, Eq, Hash, Default)]
enum RunState {
    #[default]
    Planning,
    Combat,
    Recovery,
}

fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Parasite Protocol".into(),
                resolution: (1280.0, 720.0).into(),
                ..default()
            }),
            ..default()
        }))
        .add_state::<AppState>()
        .add_state::<RunState>()
        .add_plugins((
            CoreTimePlugin,
            CoreCameraPlugin,
            ArenaMapPlugin,
        ))
        .add_systems(Startup, setup_initial_state)
        .run();
}

fn setup_initial_state(mut app_state: ResMut<NextState<AppState>>, mut run_state: ResMut<NextState<RunState>>) {
    // Start in InRun state with Planning for testing
    app_state.set(AppState::InRun);
    run_state.set(RunState::Planning);
}

