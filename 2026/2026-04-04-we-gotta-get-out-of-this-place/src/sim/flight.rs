use macroquad::prelude::*;
use macroquad::math::DVec2;
use crate::app::{InputState, PLANET_RADIUS, SURFACE_GRAVITY, ATMOSPHERE_HEIGHT};
use crate::sim::rocket::{RocketState, FlightStatus};
use crate::sim::events::{EventLog, FlightEvent, CrashCause};
use crate::sim::atmosphere;

const TURN_RATE: f32 = std::f32::consts::PI / 2.0; // 90 degrees/sec
const MAX_SAFE_LANDING_SPEED: f32 = 10.0; // m/s

use crate::debug::Tunables;

pub fn tick(rocket: &mut RocketState, input: &InputState, events: &mut EventLog, tunables: &Tunables, dt: f32, time_scale: &mut u32) {
    if matches!(rocket.flight_status, FlightStatus::Crashed { .. }) || rocket.flight_status == FlightStatus::Landed {
        // Can't fly if crashed or landed
        return;
    }

    // 1. Check for launch and staging
    if input.stage {
        *time_scale = 1; // Auto-cancel warp on staging
        
        if rocket.flight_status == FlightStatus::PreLaunch {
            rocket.flight_status = FlightStatus::Flying;
            rocket.is_active = true;
            rocket.throttle = 1.0;
            events.push(FlightEvent::LaunchStarted);
        } else if rocket.flight_status == FlightStatus::Flying {
            crate::sim::staging::check_staging(rocket, events);
        }
    }
    
    events.advance_time(dt);

    if rocket.flight_status != FlightStatus::Flying {
        return;
    }

    // 2. Throttle & Steering
    if input.throttle_up {
        rocket.throttle += 1.0 * dt;
        *time_scale = 1; // Auto-cancel warp when increasing throttle
    }
    if input.throttle_down {
        rocket.throttle -= 1.0 * dt;
    }
    rocket.throttle = rocket.throttle.clamp(0.0, 1.0);

    let mut steer_input = 0.0;
    if input.rotate_left {
        steer_input -= 1.0;
    }
    if input.rotate_right {
        steer_input += 1.0;
    }
    
    rocket.angular_velocity = steer_input * TURN_RATE;
    rocket.rotation += rocket.angular_velocity * dt;

    // 3. Compute Mass, Thrust, Fuel
    let current_mass = rocket.total_mass();
    let total_thrust = rocket.active_thrust_vacuum();
    
    // 5. Thrust
    let thrust_force = if rocket.throttle > 0.0 && rocket.fuel_remaining() > 0.0 {
        let thrust_dir = DVec2::new(rocket.rotation.sin() as f64, rocket.rotation.cos() as f64);
        thrust_dir * (total_thrust * rocket.throttle * tunables.thrust_multiplier) as f64
    } else {
        DVec2::ZERO
    };
    
    let isp = rocket.active_isp();
    
    if rocket.throttle > 0.0 && rocket.fuel_remaining() > 0.0 && isp > 0.0 {
        // mass flow rate = T / (Isp * g0)
        let g0 = 9.81;
        let mass_flow = (total_thrust * rocket.throttle * tunables.thrust_multiplier) / (isp * g0);
        let mass_to_consume = mass_flow * dt;
        
        let mut consumed = 0.0;
        let mut needed = mass_to_consume;
        
        // Drain from active stage tanks
        if rocket.current_stage < rocket.stages.len() {
            let stage = &rocket.stages[rocket.current_stage];
            for tank_id in &stage.tank_ids {
                if needed <= 0.0 { break; }
                if let Some(tank) = rocket.tanks.iter_mut().find(|t| t.instance_id == *tank_id) {
                    if tank.fuel_remaining > 0.0 {
                        let pull = needed.min(tank.fuel_remaining);
                        tank.fuel_remaining -= pull;
                        consumed += pull;
                        needed -= pull;
                    }
                }
            }
        }

        if consumed > 0.0 && rocket.fuel_remaining() <= 0.0 {
            events.push(FlightEvent::FuelDepleted);
            rocket.throttle = 0.0; // Cut throttle immediately
            *time_scale = 1; // Auto-cancel warp on fuel depletion
        }
    } else if rocket.fuel_remaining() <= 0.0 {
        rocket.throttle = 0.0; // Prevent ghost thrust from an empty rocket
    }

    // 4. Gravity
    let dist_sq = rocket.position.length_squared();
    let up_dir = if dist_sq > 1e-6 { rocket.position.normalize() } else { DVec2::new(0.0, 1.0) };
    
    // Inverse square law: g = G * M / r^2
    // We base it on surface gravity: G * M = surface_g * radius^2
    let gm = (SURFACE_GRAVITY as f64) * (PLANET_RADIUS as f64).powi(2);
    let gravity_accel = if dist_sq > 1e-6 { gm / dist_sq } else { 0.0 } * (tunables.gravity_multiplier as f64);
    let gravity_force = -up_dir * (gravity_accel * (current_mass as f64));

    // 5. Drag
    let altitude = rocket.position.length() - (PLANET_RADIUS as f64);
    let drag_force = atmosphere::drag_force(
        rocket.velocity, 
        1.0, 
        rocket.total_drag_area() as f64, 
        altitude
    ) * (tunables.drag_multiplier as f64);

    // 6. Integrate
    let net_force = thrust_force + gravity_force + drag_force;
    let acceleration = net_force / (current_mass as f64);

    let dt_f64 = dt as f64;
    rocket.velocity += acceleration * dt_f64;
    rocket.position += rocket.velocity * dt_f64;

    rocket.orbital_params = Some(crate::sim::orbit::compute_orbital_params(
        rocket.position,
        rocket.velocity,
        PLANET_RADIUS as f64,
        SURFACE_GRAVITY as f64,
        ATMOSPHERE_HEIGHT as f64,
    ));

    if altitude > (ATMOSPHERE_HEIGHT as f64) && !rocket.has_cleared_atmosphere {
        rocket.has_cleared_atmosphere = true;
        events.push(FlightEvent::AtmosphereCleared);
    }

    if let Some(params) = &rocket.orbital_params {
        if matches!(params.path, crate::sim::orbit::PathType::StableOrbit) && !rocket.has_achieved_orbit {
            rocket.has_achieved_orbit = true;
            events.push(FlightEvent::StableOrbitAchieved);
        }
    }

    let r_f64 = PLANET_RADIUS as f64;
    let new_altitude = rocket.position.length() - r_f64;

    // 7. Ground collision detection
    let up_dir = if rocket.position.length_squared() > 1e-6 { rocket.position.normalize() } else { DVec2::ZERO };
    let vertical_speed = rocket.velocity.dot(up_dir);

    // Only collide if we are at or below the ground, AND falling downwards
    // (if taking off, vertical_speed is positive, so we let the rocket ascend).
    if new_altitude <= 0.0 && vertical_speed <= 0.0 {
        rocket.position = up_dir * r_f64;
        let speed = rocket.velocity.length() as f32;
        rocket.velocity = DVec2::ZERO;

        if rocket.flight_status == FlightStatus::Flying {
            if speed > MAX_SAFE_LANDING_SPEED {
                rocket.flight_status = FlightStatus::Crashed { cause: CrashCause::HighVelocityImpact };
                events.push(FlightEvent::Crashed(CrashCause::HighVelocityImpact));
            } else {
                rocket.flight_status = FlightStatus::Landed;
                events.push(FlightEvent::Landed);
            }
        }
    }
}
