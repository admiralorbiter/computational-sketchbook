use macroquad::prelude::*;
use crate::ui::builder::BuilderSession;
use crate::ui::builder_input::BuilderAction;
use crate::data::PartLibrary;
use crate::data::schema::part::PartCategory;

pub fn draw_builder(session: &BuilderSession, library: &PartLibrary) -> Vec<BuilderAction> {
    let mut actions = Vec::new();
    let mouse_p = mouse_position();
    let mouse_pos = vec2(mouse_p.0, mouse_p.1);
    let clicked = is_mouse_button_pressed(MouseButton::Left);

    let sw = screen_width();
    let sh = screen_height();
    
    let left_w = sw * 0.25;
    let right_w = sw * 0.25;
    let center_w = sw * 0.50;

    // --- LEFT PANEL: Palette ---
    draw_rectangle(0.0, 0.0, left_w, sh, Color::new(0.1, 0.1, 0.15, 1.0));
    draw_text("PARTS", 10.0, 30.0, 30.0, WHITE);
    
    let mut y = 60.0;
    // We sort parts by ID for stability
    let mut part_ids: Vec<_> = library.parts.keys().cloned().collect();
    part_ids.sort();

    for id in &part_ids {
        if let Some(def) = library.get(id) {
            let is_selected = session.selected_palette_id.as_deref() == Some(id);
            let rect = Rect::new(10.0, y - 20.0, left_w - 20.0, 25.0);
            
            if rect.contains(mouse_pos) {
                draw_rectangle_lines(rect.x, rect.y, rect.w, rect.h, 2.0, LIGHTGRAY);
                if clicked {
                    if is_selected {
                        // Double click behavior: place it if it's already selected
                        actions.push(BuilderAction::PlaceSelected);
                    } else {
                        actions.push(BuilderAction::SelectPalette(id.clone()));
                    }
                }
            }

            if is_selected {
                draw_rectangle(rect.x, rect.y, rect.w, rect.h, Color::new(0.2, 0.5, 0.2, 0.8));
            }
            
            // Show mass in the palette for easier decision making
            let total_part_mass = def.dry_mass + def.fuel_capacity;
            let display_text = format!("{} ({}kg)", def.display_name, total_part_mass);
            draw_text(&display_text, 15.0, y, 20.0, WHITE);
            y += 30.0;
        }
    }

    // --- RIGHT PANEL: Stats ---
    let right_x = sw - right_w;
    draw_rectangle(right_x, 0.0, right_w, sh, Color::new(0.1, 0.1, 0.15, 1.0));
    draw_text("BUILD STATS", right_x + 10.0, 30.0, 30.0, WHITE);

    let mut ry = 60.0;
    
    let stats = [
        ("Total Mass", format!("{:.0} kg", session.total_mass(library))),
        ("Dry Mass", format!("{:.0} kg", session.dry_mass(library))),
        ("Fuel Mass", format!("{:.0} kg", session.fuel_mass(library))),
        ("Stages", format!("{}", session.stage_count())),
    ];

    for (label, val) in &stats {
        draw_text(label, right_x + 10.0, ry, 20.0, LIGHTGRAY);
        draw_text(val, right_x + 10.0, ry + 20.0, 22.0, WHITE);
        ry += 40.0;
    }

    ry += 20.0;

    let bp = session.to_blueprint();
    let dv_budget = crate::sim::delta_v::compute_delta_v(&bp, library);
    
    draw_text("Total ΔV", right_x + 10.0, ry, 20.0, LIGHTGRAY);
    draw_text(&format!("{:.0} m/s", dv_budget.total), right_x + 10.0, ry + 20.0, 22.0, WHITE);
    ry += 40.0;
    
    for (i, dv) in dv_budget.per_stage.iter().enumerate() {
        if *dv > 0.0 {
            draw_text(&format!("  Stage {}: {:.0} m/s", i, dv), right_x + 10.0, ry, 18.0, LIGHTGRAY);
            ry += 20.0;
        }
    }

    ry += 20.0;
    // Launch Validation Block
    if session.validation.is_empty() && !session.parts.is_empty() {
        draw_text("VALIDATION PASS", right_x + 10.0, ry, 20.0, GREEN);
        ry += 30.0;
        let launch_rect = Rect::new(right_x + 10.0, ry, right_w - 20.0, 40.0);
        draw_rectangle(launch_rect.x, launch_rect.y, launch_rect.w, launch_rect.h, GREEN);
        draw_text("LAUNCH [L]", launch_rect.x + 20.0, launch_rect.y + 25.0, 25.0, BLACK);
        if launch_rect.contains(mouse_pos) && clicked {
            actions.push(BuilderAction::Launch);
        }
    } else if !session.parts.is_empty() {
        draw_text("WARNINGS / ERRORS", right_x + 10.0, ry, 20.0, ORANGE);
        ry += 25.0;
        for issue in &session.validation {
            let color = match issue.severity {
                crate::data::validate::ValidationSeverity::Error => RED,
                crate::data::validate::ValidationSeverity::Warning => ORANGE,
                crate::data::validate::ValidationSeverity::Info => LIGHTGRAY,
            };
            draw_text(&issue.message, right_x + 10.0, ry, 16.0, color);
            ry += 20.0;
        }
    }

    // --- CENTER PANEL: Schematic Canvas ---
    draw_text(&session.display_name, left_w + 20.0, 30.0, 30.0, WHITE);

    let max_h = sh - 100.0;
    let schem_x = left_w + (center_w / 2.0);
    let mut curr_y = 100.0;

    for (i, inst) in session.parts.iter().enumerate() {
        if let Some(def) = library.get(&inst.part_id) {
            let is_selected = session.selected_canvas_idx == Some(i);
            
            // Proportional heights based on category/mass for visual flair
            let (h, w, color) = match def.category {
                PartCategory::Command => (40.0, 40.0, GRAY),
                PartCategory::Tank => (20.0 + (def.fuel_capacity / 50.0).clamp(20.0, 150.0), 60.0, WHITE),
                PartCategory::Engine => (30.0, 30.0, DARKGRAY),
                _ => (30.0, 40.0, LIGHTGRAY),
            };

            let rect = Rect::new(schem_x - w/2.0, curr_y, w, h);
            
            if rect.contains(mouse_pos) {
                draw_rectangle_lines(rect.x - 2.0, rect.y - 2.0, w + 4.0, h + 4.0, 2.0, YELLOW);
                if clicked {
                    actions.push(BuilderAction::SelectCanvas(i));
                }
            }

            draw_rectangle(rect.x, rect.y, rect.w, rect.h, color);
            
            if is_selected {
                draw_rectangle_lines(rect.x - 2.0, rect.y - 2.0, w + 4.0, h + 4.0, 2.0, GREEN);
                draw_text(&def.display_name, rect.x + w + 10.0, rect.y + h/2.0, 20.0, GREEN);
                // Draw stage info next to selected part
                let mut stage_idx = 0;
                for (s_i, s) in session.stages.iter().enumerate() {
                    if s.engine_ids.contains(&inst.instance_id) || s.tank_ids.contains(&inst.instance_id) {
                        stage_idx = s_i;
                        break;
                    }
                }
                draw_text(&format!("Stage {}", stage_idx), rect.x + w + 10.0, rect.y + h/2.0 + 20.0, 16.0, ORANGE);
            }
            
            curr_y += h + 2.0;

            if curr_y > max_h {
                draw_text("... (rocket too tall for viewport)", schem_x - 50.0, curr_y + 20.0, 20.0, RED);
                break;
            }
        }
    }

    // Bottom Help Text
    draw_text("[Double-Click/Enter] Place  |  [Del] Remove  |  [Left/Right] Stage  |  [L] Launch  |  [R] Clear  |  [Esc] Back", left_w + 20.0, sh - 20.0, 18.0, GRAY);

    actions
}
