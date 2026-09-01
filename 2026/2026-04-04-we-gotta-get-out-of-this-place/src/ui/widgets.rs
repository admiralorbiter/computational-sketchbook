use macroquad::prelude::*;

/// Draws text with a semi-transparent black background pill behind it.
/// Shared by HUD, map UI, and any future overlay that needs readable screen-space text.
pub fn draw_text_with_bg(text: &str, x: f32, y: f32, font_size: f32, color: Color) {
    let text_size = measure_text(text, None, font_size as u16, 1.0);
    draw_rectangle(
        x - 2.0,
        y - font_size + 2.0,
        text_size.width + 4.0,
        text_size.height + 4.0,
        Color::new(0.0, 0.0, 0.0, 0.5),
    );
    draw_text(text, x, y, font_size, color);
}

/// Draws a small vertical progress bar (e.g. for throttle or fuel).
/// `x, y` are the top-left corner. `height` matches a single text row.
/// `fraction` is 0.0..1.0. `empty_color` is shown for the unfilled portion.
pub fn draw_vertical_bar(x: f32, y: f32, height: f32, fraction: f32, empty_color: Color, fill_color: Color) {
    let bar_w = 6.0;
    let clamped = fraction.clamp(0.0, 1.0);
    let fill_h = height * clamped;
    // Background track
    draw_rectangle(x, y, bar_w, height, Color::new(empty_color.r, empty_color.g, empty_color.b, 0.3));
    // Fill (bottom-up)
    draw_rectangle(x, y + height - fill_h, bar_w, fill_h, fill_color);
}
