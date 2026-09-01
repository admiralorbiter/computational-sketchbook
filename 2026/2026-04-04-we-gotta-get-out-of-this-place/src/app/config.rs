pub const WINDOW_WIDTH: i32 = 1280;
pub const WINDOW_HEIGHT: i32 = 720;
pub const FIXED_TIMESTEP: f32 = 1.0 / 60.0;

// World / physics
pub const PLANET_RADIUS: f32 = 600_000.0;       // meters
pub const ATMOSPHERE_HEIGHT: f32 = 70_000.0;    // meters above surface
pub const SURFACE_GRAVITY: f32 = 9.81;           // m/s²

// Camera
pub const INITIAL_ZOOM_M_PER_PIXEL: f32 = 2.0; // how many meters one pixel represents at startup
