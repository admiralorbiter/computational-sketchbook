#[derive(Debug, Clone, PartialEq)]
#[allow(dead_code)]
pub enum CrashCause {
    HighVelocityImpact,
    FuelDepletedOutOfAtmosphere,
    // Future: BurnedUp
}

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub enum FlightEvent {
    LaunchStarted,
    FuelDepleted,
    MaxAltitudeReached(f32),
    Crashed(CrashCause),
    Landed,
    StageSeparated(usize),
    AtmosphereCleared,
    StableOrbitAchieved,
}

pub struct EventLog {
    entries: Vec<(f32, FlightEvent)>,
    time: f32,
}

impl EventLog {
    pub fn new() -> Self {
        Self {
            entries: Vec::new(),
            time: 0.0,
        }
    }

    pub fn reset(&mut self) {
        self.entries.clear();
        self.time = 0.0;
    }

    pub fn advance_time(&mut self, dt: f32) {
        self.time += dt;
    }

    pub fn push(&mut self, event: FlightEvent) {
        self.entries.push((self.time, event));
    }

    pub fn entries(&self) -> &[(f32, FlightEvent)] {
        &self.entries
    }

    pub fn recent_events(&self, duration: f32) -> Vec<FlightEvent> {
        self.entries
            .iter()
            .filter(|(t, _)| self.time - t <= duration)
            .map(|(_, e)| e.clone())
            .collect()
    }
}
