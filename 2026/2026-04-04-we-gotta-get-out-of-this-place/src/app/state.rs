#[allow(dead_code)]
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AppState {
    MainMenu,
    MissionSelect,
    Builder,
    Flight,
    Map,
    Debrief,
    Paused { previous: Box<AppState> },
}
