use bevy::prelude::*;

pub struct CoreCameraPlugin;

impl Plugin for CoreCameraPlugin {
    fn build(&self, app: &mut App) {
        app
            .add_systems(Startup, setup_camera)
            .add_systems(Update, (
                handle_keyboard_pan,
                handle_mouse_drag_pan,
                handle_zoom,
                clamp_camera_bounds,
            ));
    }
}

#[derive(Component)]
pub struct MainCamera;

#[derive(Resource)]
pub struct CameraBounds {
    pub min_x: f32,
    pub max_x: f32,
    pub min_y: f32,
    pub max_y: f32,
}

impl Default for CameraBounds {
    fn default() -> Self {
        // Camera bounds set to accommodate cell radius of 75.0
        // Add some padding for comfortable viewing
        let cell_radius = 75.0;
        let padding = 25.0;
        Self {
            min_x: -(cell_radius + padding),
            max_x: cell_radius + padding,
            min_y: -(cell_radius + padding),
            max_y: cell_radius + padding,
        }
    }
}

fn setup_camera(mut commands: Commands) {
    commands.spawn((
        Camera2dBundle::default(),
        MainCamera,
    ));
    
    commands.init_resource::<CameraBounds>();
}

fn handle_keyboard_pan(
    keyboard_input: Res<Input<KeyCode>>,
    mut query: Query<&mut Transform, With<MainCamera>>,
    time: Res<Time>,
) {
    let pan_speed = 200.0;
    let mut direction = Vec2::ZERO;

    if keyboard_input.pressed(KeyCode::W) || keyboard_input.pressed(KeyCode::Up) {
        direction.y += 1.0;
    }
    if keyboard_input.pressed(KeyCode::S) || keyboard_input.pressed(KeyCode::Down) {
        direction.y -= 1.0;
    }
    if keyboard_input.pressed(KeyCode::A) || keyboard_input.pressed(KeyCode::Left) {
        direction.x -= 1.0;
    }
    if keyboard_input.pressed(KeyCode::D) || keyboard_input.pressed(KeyCode::Right) {
        direction.x += 1.0;
    }

    if direction.length_squared() > 0.0 {
        direction = direction.normalize();
        for mut transform in query.iter_mut() {
            transform.translation += (direction * pan_speed * time.delta_seconds()).extend(0.0);
        }
    }
}

#[derive(Resource, Default)]
struct DragState {
    is_dragging: bool,
    last_position: Vec2,
}

fn handle_mouse_drag_pan(
    mouse_button_input: Res<Input<MouseButton>>,
    mut drag_state: Local<DragState>,
    mut query: Query<&mut Transform, With<MainCamera>>,
    windows: Query<&Window>,
    camera: Query<(&Camera, &GlobalTransform), With<MainCamera>>,
) {
    let Ok(window) = windows.get_single() else { return };
    let Ok((camera, camera_transform)) = camera.get_single() else { return };

    if mouse_button_input.just_pressed(MouseButton::Middle) {
        if let Some(cursor_pos) = window.cursor_position() {
            drag_state.is_dragging = true;
            drag_state.last_position = cursor_pos;
        }
    }

    if mouse_button_input.just_released(MouseButton::Middle) {
        drag_state.is_dragging = false;
    }

    if drag_state.is_dragging {
        if let Some(cursor_pos) = window.cursor_position() {
            let delta = cursor_pos - drag_state.last_position;
            
            // Convert screen delta to world delta
            if let Some(viewport_size) = camera.logical_viewport_size() {
                let world_delta = Vec2::new(
                    -delta.x * (camera_transform.compute_transform().scale.x / viewport_size.x),
                    delta.y * (camera_transform.compute_transform().scale.y / viewport_size.y),
                );

                for mut transform in query.iter_mut() {
                    transform.translation += world_delta.extend(0.0);
                }
            }

            drag_state.last_position = cursor_pos;
        }
    }
}

fn handle_zoom(
    mut scroll_events: EventReader<bevy::input::mouse::MouseWheel>,
    mut query: Query<&mut OrthographicProjection, With<MainCamera>>,
) {
    let zoom_speed = 0.1;
    let min_scale = 0.1;
    let max_scale = 5.0;

    for event in scroll_events.read() {
        for mut projection in query.iter_mut() {
            let zoom_delta = -event.y * zoom_speed;
            projection.scale = (projection.scale + zoom_delta).clamp(min_scale, max_scale);
        }
    }
}

fn clamp_camera_bounds(
    bounds: Res<CameraBounds>,
    mut query: Query<&mut Transform, With<MainCamera>>,
) {
    for mut transform in query.iter_mut() {
        transform.translation.x = transform.translation.x.clamp(bounds.min_x, bounds.max_x);
        transform.translation.y = transform.translation.y.clamp(bounds.min_y, bounds.max_y);
    }
}

