use macroquad::math::DVec2;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum PathType {
    StableOrbit,
    Suborbital,
    Escaping,
    Ballistic,  // fully inside atmosphere, no meaningful orbit
    Descending,
}

#[allow(dead_code)]
#[derive(Debug, Clone, Copy)]
pub struct OrbitEllipse {
    pub center: DVec2,          // world-space center of ellipse
    pub semi_major: f64,        // a
    pub semi_minor: f64,        // b = a*sqrt(1-e²)
    pub rotation: f64,          // angle of periapsis direction (for drawing)
    pub apoapsis_point: DVec2,  // world-space position of APO
    pub periapsis_point: DVec2, // world-space position of PER
}

#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct OrbitalParams {
    pub apoapsis_alt: f64,    // meters above surface, can be negative
    pub periapsis_alt: f64,   // meters above surface, can be negative
    pub eccentricity: f64,
    pub semi_major_axis: f64,
    pub path: PathType,
    pub ellipse: Option<OrbitEllipse>, // only if bound orbit
}

impl OrbitalParams {
    /// Returns the Keplerian orbital period in seconds, or None if not a stable orbit.
    pub fn period_seconds(&self, surface_gravity: f64, planet_radius: f64) -> Option<f64> {
        if !matches!(self.path, PathType::StableOrbit) {
            return None;
        }
        if let Some(ellipse) = &self.ellipse {
            let a = ellipse.semi_major;
            if a > 0.0 {
                let mu = surface_gravity * planet_radius * planet_radius;
                return Some(2.0 * std::f64::consts::PI * (a.powi(3) / mu).sqrt());
            }
        }
        None
    }
}

pub fn compute_orbital_params(
    position: DVec2, 
    velocity: DVec2,
    planet_radius: f64,
    surface_gravity: f64,
    atmo_height: f64,
) -> OrbitalParams {
    let r_mag = position.length();
    let v_mag_sq = velocity.length_squared();
    
    // Standard gravitational parameter GM
    let gm = surface_gravity * (planet_radius * planet_radius);
    
    // Specific orbital energy
    let energy = (v_mag_sq / 2.0) - (gm / r_mag);
    
    // Specific angular momentum h (scalar in 2D = r_x * v_y - r_y * v_x)
    let h = position.x * velocity.y - position.y * velocity.x;

    // Escaping trajectory
    if energy >= 0.0 {
        return OrbitalParams {
            apoapsis_alt: f64::INFINITY,
            periapsis_alt: f64::NAN, // Wait, periapsis exists for hyperbolic, but we keep it simple
            eccentricity: f64::INFINITY,
            semi_major_axis: f64::INFINITY,
            path: PathType::Escaping,
            ellipse: None,
        };
    }

    // Bound orbit
    let a = -gm / (2.0 * energy);
    
    // Eccentricity vector e = (v x h)/mu - r_hat
    // h_vec in 3D is [0, 0, h]. v x h_vec = [v.y * h, -v.x * h, 0]
    let e_vec_x = (velocity.y * h) / gm - (position.x / r_mag);
    let e_vec_y = (-velocity.x * h) / gm - (position.y / r_mag);
    let eccentricity = (e_vec_x * e_vec_x + e_vec_y * e_vec_y).sqrt();

    // Prevent completely degenerate math issues
    let e = eccentricity.min(0.99999);
    
    let r_apo = a * (1.0 + e);
    let r_peri = a * (1.0 - e);

    let apoapsis_alt = r_apo - planet_radius;
    let periapsis_alt = r_peri - planet_radius;

    let r_dot_v = position.dot(velocity);
    
    let mut path = if apoapsis_alt < atmo_height {
        PathType::Ballistic
    } else if periapsis_alt >= atmo_height {
        PathType::StableOrbit
    } else {
        PathType::Suborbital
    };
    
    // If we're already falling back to the surface on a ballistic path...
    if path == PathType::Ballistic && r_dot_v < 0.0 {
        path = PathType::Descending;
    }

    // Ellipse geometry
    let b = a * (1.0 - e * e).sqrt();
    
    // The eccentricity vector points from the focus (planet center) toward periapsis.
    // The center of the ellipse is distance a*e away from the focus, in the opposite direction of e_vec.
    // Wait, the center of an ellipse is offset from the focus towards apoapsis.
    // e_vec points to periapsis. So the center is at -a * e * e_vec_normalized
    let e_vec_len = eccentricity;
    let e_dir = if e_vec_len > 1e-7 {
        DVec2::new(e_vec_x / e_vec_len, e_vec_y / e_vec_len)
    } else {
        DVec2::new(0.0, 1.0)
    };
    
    let center = e_dir * (-a * e);
    let rotation = e_dir.y.atan2(e_dir.x); // angle of periapsis

    let apoapsis_point = center - e_dir * a;
    let periapsis_point = center + e_dir * a;

    let ellipse = Some(OrbitEllipse {
        center,
        semi_major: a,
        semi_minor: b,
        rotation,
        apoapsis_point,
        periapsis_point,
    });

    OrbitalParams {
        apoapsis_alt,
        periapsis_alt,
        eccentricity,
        semi_major_axis: a,
        path,
        ellipse,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use macroquad::math::DVec2;

    #[test]
    fn test_circular_orbit() {
        let r: f64 = 600_000.0 + 100_000.0; // 100km altitude
        let planet_radius: f64 = 600_000.0;
        let surface_gravity: f64 = 9.81;
        
        let gm = surface_gravity * (planet_radius * planet_radius);
        let v: f64 = (gm / r).sqrt();

        let pos = DVec2::new(0.0, r);
        let vel = DVec2::new(v, 0.0);

        let params = compute_orbital_params(pos, vel, planet_radius, surface_gravity, 70_000.0);
        
        assert_eq!(params.path, PathType::StableOrbit);
        assert!((params.apoapsis_alt - 100_000.0).abs() < 1.0);
        assert!((params.periapsis_alt - 100_000.0).abs() < 1.0);
        assert!(params.eccentricity < 1e-4);
    }
}
