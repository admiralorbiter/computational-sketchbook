#![allow(dead_code)]
use macroquad::prelude::*;

pub fn draw_main_menu() {
    draw_title("Main Menu");
}

pub fn draw_mission_select() {
    draw_title("Mission Select");
}

pub fn draw_builder() {
    draw_title("Builder");
}

pub fn draw_flight() {
    draw_title("Flight");
}

pub fn draw_map() {
    draw_title("Map");
}

pub fn draw_debrief() {
    draw_title("Debrief");
}

pub fn draw_paused() {
    draw_title("Paused");
}

fn draw_title(title: &str) {
    let font_size = 50.0;
    let text_size = measure_text(title, None, font_size as u16, 1.0);
    draw_text(
        title,
        (screen_width() - text_size.width) / 2.0,
        screen_height() / 2.0,
        font_size,
        WHITE,
    );
}
