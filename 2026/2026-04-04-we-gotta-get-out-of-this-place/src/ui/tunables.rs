use macroquad::prelude::*;
use crate::debug::Tunables;

pub fn update_and_draw(tunables: &mut Tunables) {
    let panel_w = 220.0;
    let panel_h = 160.0;
    let x = screen_width() - panel_w - 20.0;
    let y = 20.0;
    
    draw_rectangle(x, y, panel_w, panel_h, Color::new(0.0, 0.0, 0.0, 0.8));
    draw_rectangle_lines(x, y, panel_w, panel_h, 2.0, GRAY);
    
    draw_text("TUNABLES (dev)", x + 10.0, y + 25.0, 20.0, YELLOW);
    
    let left_click = is_mouse_button_pressed(MouseButton::Left);

    // Gravity
    let mut item_y = y + 55.0;
    draw_text(&format!("Gravity: {:.1}x", tunables.gravity_multiplier), x + 10.0, item_y, 20.0, WHITE);
    if draw_btn(x + 150.0, item_y - 15.0, 20.0, 20.0, "-") && left_click { tunables.gravity_multiplier = (tunables.gravity_multiplier - 0.1).max(0.0); }
    if draw_btn(x + 180.0, item_y - 15.0, 20.0, 20.0, "+") && left_click { tunables.gravity_multiplier += 0.1; }
    
    // Drag
    item_y += 30.0;
    draw_text(&format!("Drag: {:.1}x", tunables.drag_multiplier), x + 10.0, item_y, 20.0, WHITE);
    if draw_btn(x + 150.0, item_y - 15.0, 20.0, 20.0, "-") && left_click { tunables.drag_multiplier = (tunables.drag_multiplier - 0.1).max(0.0); }
    if draw_btn(x + 180.0, item_y - 15.0, 20.0, 20.0, "+") && left_click { tunables.drag_multiplier += 0.1; }
    
    // Thrust
    item_y += 30.0;
    draw_text(&format!("Thrust: {:.1}x", tunables.thrust_multiplier), x + 10.0, item_y, 20.0, WHITE);
    if draw_btn(x + 150.0, item_y - 15.0, 20.0, 20.0, "-") && left_click { tunables.thrust_multiplier = (tunables.thrust_multiplier - 0.1).max(0.0); }
    if draw_btn(x + 180.0, item_y - 15.0, 20.0, 20.0, "+") && left_click { tunables.thrust_multiplier += 0.1; }

    // Reset
    item_y += 30.0;
    if draw_btn(x + 10.0, item_y - 15.0, 60.0, 20.0, "Reset") && left_click { tunables.reset(); }
}

fn draw_btn(x: f32, y: f32, w: f32, h: f32, label: &str) -> bool {
    let mouse = mouse_position();
    let hovered = mouse.0 >= x && mouse.0 <= x + w && mouse.1 >= y && mouse.1 <= y + h;
    let bg = if hovered { DARKGRAY } else { GRAY };
    draw_rectangle(x, y, w, h, bg);
    draw_text(label, x + 5.0, y + 15.0, 20.0, WHITE);
    hovered
}
