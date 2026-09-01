pub struct Tunables {
    pub gravity_multiplier: f32,
    pub drag_multiplier: f32,
    pub thrust_multiplier: f32,
}

impl Tunables {
    pub fn new() -> Self {
        Self {
            gravity_multiplier: 1.0,
            drag_multiplier: 1.0,
            thrust_multiplier: 1.0,
        }
    }

    pub fn reset(&mut self) {
        self.gravity_multiplier = 1.0;
        self.drag_multiplier = 1.0;
        self.thrust_multiplier = 1.0;
    }
}
