use macroquad::math::DVec2;

const SEA_LEVEL_DENSITY: f64 = 1.225; // kg/m^3 (Earth-like)
const SCALE_HEIGHT: f64 = 8_500.0; // meters (Earth-like)

pub fn density_at(altitude_m: f64) -> f64 {
    if altitude_m < 0.0 {
        SEA_LEVEL_DENSITY // Assuming uniform density below sea level for now
    } else {
        SEA_LEVEL_DENSITY * (-altitude_m / SCALE_HEIGHT).exp()
    }
}

pub fn drag_force(velocity: DVec2, cd: f64, area: f64, altitude: f64) -> DVec2 {
    let speed = velocity.length();
    if speed < 0.001 {
        return DVec2::ZERO;
    }
    
    let density = density_at(altitude);
    let drag_magnitude = 0.5 * density * speed * speed * cd * area;
    
    // Drag points opposite to velocity
    let direction = -velocity / speed;
    direction * drag_magnitude
}
