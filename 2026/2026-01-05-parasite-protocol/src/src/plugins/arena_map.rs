use bevy::prelude::*;
use bevy::sprite::SpriteBundle;
use bevy::render::texture::{ImageSampler, ImageSamplerDescriptor};
use bevy::render::render_resource::{Extent3d, TextureDimension, TextureFormat};

pub struct ArenaMapPlugin;

impl Plugin for ArenaMapPlugin {
    fn build(&self, app: &mut App) {
        app
            .init_resource::<CellRadius>()
            .add_systems(Startup, setup_arena);
    }
}

#[derive(Resource)]
pub struct CellRadius {
    pub radius: f32,
}

impl Default for CellRadius {
    fn default() -> Self {
        // Increased from 50.0 to 75.0 for better gameplay space
        // This gives room for modules, enemies, tracks, and vesicles
        Self { radius: 75.0 }
    }
}

#[derive(Component)]
pub struct MembraneRing;

#[derive(Component, Debug, Clone, Copy, PartialEq, Eq)]
pub enum OrganelleType {
    Nucleus,
    ErGolgi,
    Mitochondria,
}

#[derive(Component, Clone)]
pub struct Organelle {
    pub organelle_type: OrganelleType,
    pub radius: f32,
}

impl Organelle {
    pub fn color(&self) -> Color {
        match self.organelle_type {
            OrganelleType::Nucleus => Color::rgb(0.4, 0.2, 0.6), // purple
            OrganelleType::ErGolgi => Color::rgb(0.9, 0.7, 0.2), // yellow/orange
            OrganelleType::Mitochondria => Color::rgb(0.8, 0.3, 0.2), // red/orange
        }
    }
}

#[derive(Resource)]
pub struct OrganelleLayout {
    pub nucleus: OrganellePosition,
    pub er_golgi: OrganellePosition,
    pub mitochondria: Vec<OrganellePosition>,
}

#[derive(Debug, Clone, Copy)]
pub struct OrganellePosition {
    pub position: Vec2,
    pub radius: f32,
    pub organelle_type: OrganelleType,
}

// Pixel art texture generation functions

fn create_pixel_art_circle_texture(size: u32, _base_color: Color, pattern_fn: impl Fn(u32, u32, u32) -> Color) -> Image {
    let mut data = Vec::with_capacity((size * size * 4) as usize);
    let center = size as f32 / 2.0;
    let radius = center - 1.0;
    
    for y in 0..size {
        for x in 0..size {
            let dx = x as f32 - center;
            let dy = y as f32 - center;
            let dist = (dx * dx + dy * dy).sqrt();
            
            if dist <= radius {
                let pixel_color = pattern_fn(x, y, size);
                data.push((pixel_color.r() * 255.0) as u8);
                data.push((pixel_color.g() * 255.0) as u8);
                data.push((pixel_color.b() * 255.0) as u8);
                data.push((pixel_color.a() * 255.0) as u8);
            } else {
                // Transparent outside circle
                data.push(0);
                data.push(0);
                data.push(0);
                data.push(0);
            }
        }
    }
    
    let mut image = Image::new(
        Extent3d {
            width: size,
            height: size,
            depth_or_array_layers: 1,
        },
        TextureDimension::D2,
        data,
        TextureFormat::Rgba8UnormSrgb,
    );
    
    // Use nearest neighbor filtering for crisp pixel art
    image.sampler = ImageSampler::Descriptor(ImageSamplerDescriptor::nearest());
    
    image
}

fn create_membrane_texture(size: u32) -> Image {
    let base_color = Color::rgb(0.2, 0.4, 0.8);
    create_pixel_art_circle_texture(size, base_color, |x, y, size| {
        let center = size as f32 / 2.0;
        let dx = x as f32 - center;
        let dy = y as f32 - center;
        let dist = (dx * dx + dy * dy).sqrt();
        let radius = center - 1.0;
        
        // Add subtle border pattern
        if dist > radius - 2.0 {
            // Slightly darker border
            Color::rgb(0.15, 0.35, 0.7)
        } else {
            base_color
        }
    })
}

fn create_nucleus_texture(size: u32) -> Image {
    let base_color = Color::rgb(0.4, 0.2, 0.6);
    create_pixel_art_circle_texture(size, base_color, |x, y, size| {
        let center = size as f32 / 2.0;
        let dx = x as f32 - center;
        let dy = y as f32 - center;
        
        // Add chromatin/nucleolus pattern (dots)
        let pattern_x = (x as f32 / 3.0).floor() as u32;
        let pattern_y = (y as f32 / 3.0).floor() as u32;
        let pattern_hash = (pattern_x * 7 + pattern_y * 11) % 5;
        
        if pattern_hash == 0 && (dx * dx + dy * dy) < (size as f32 * 0.3).powi(2) {
            // Darker dots suggesting chromatin
            Color::rgb(0.3, 0.15, 0.5)
        } else if pattern_hash == 1 && (dx * dx + dy * dy) < (size as f32 * 0.2).powi(2) {
            // Nucleolus (slightly lighter)
            Color::rgb(0.5, 0.25, 0.7)
        } else {
            base_color
        }
    })
}

fn create_er_golgi_texture(size: u32) -> Image {
    let base_color = Color::rgb(0.9, 0.7, 0.2);
    create_pixel_art_circle_texture(size, base_color, |x, y, size| {
        let center = size as f32 / 2.0;
        let dx = x as f32 - center;
        let dy = y as f32 - center;
        
        // Add membrane fold pattern (curved lines)
        let angle = dy.atan2(dx);
        let dist = (dx * dx + dy * dy).sqrt();
        let _radius = size as f32 / 2.0 - 1.0;
        
        // Create curved line pattern suggesting cisternae
        let fold_pattern = (angle * 3.0 + dist * 0.5).sin();
        if fold_pattern > 0.3 {
            // Slightly darker for membrane folds
            Color::rgb(0.8, 0.6, 0.15)
        } else if fold_pattern < -0.3 {
            // Slightly lighter
            Color::rgb(0.95, 0.75, 0.25)
        } else {
            base_color
        }
    })
}

fn create_mitochondria_texture(size: u32) -> Image {
    let base_color = Color::rgb(0.8, 0.3, 0.2);
    create_pixel_art_circle_texture(size, base_color, |x, y, size| {
        let center = size as f32 / 2.0;
        let dx = x as f32 - center;
        let dy = y as f32 - center;
        
        // Add cristae pattern (parallel lines/ridges)
        // Create horizontal lines suggesting inner membrane folds
        let line_spacing = 3.0;
        let line_y = (y as f32 / line_spacing).floor() * line_spacing;
        let line_dist = (y as f32 - line_y).abs();
        
        if line_dist < 0.5 && (dx * dx + dy * dy) < (size as f32 * 0.4).powi(2) {
            // Darker lines for cristae
            Color::rgb(0.7, 0.25, 0.15)
        } else {
            base_color
        }
    })
}

fn create_default_layout(cell_radius: f32) -> OrganelleLayout {
    // Scale organelles proportionally to cell size
    let scale_factor = cell_radius / 50.0; // Base size was 50.0
    
    // Nucleus: center, scaled radius
    let nucleus = OrganellePosition {
        position: Vec2::ZERO,
        radius: 9.0 * scale_factor,
        organelle_type: OrganelleType::Nucleus,
    };

    // ER/Golgi: offset from center at 45° angle, scaled distance and radius
    let er_golgi_angle = std::f32::consts::PI / 4.0; // 45 degrees
    let er_golgi_distance = 15.0 * scale_factor;
    let er_golgi = OrganellePosition {
        position: Vec2::new(
            er_golgi_distance * er_golgi_angle.cos(),
            er_golgi_distance * er_golgi_angle.sin(),
        ),
        radius: 7.0 * scale_factor,
        organelle_type: OrganelleType::ErGolgi,
    };

    // Mitochondria: 3 placed in annulus band, scaled positions and sizes
    let mut mitochondria = Vec::new();
    let mito_angles = [
        std::f32::consts::PI * 0.25,  // 45°
        std::f32::consts::PI * 1.25,  // 225°
        std::f32::consts::PI * 1.75,  // 315°
    ];
    let mito_distance = 25.0 * scale_factor; // Scaled distance
    
    for angle in mito_angles {
        mitochondria.push(OrganellePosition {
            position: Vec2::new(
                mito_distance * angle.cos(),
                mito_distance * angle.sin(),
            ),
            radius: 6.0 * scale_factor,
            organelle_type: OrganelleType::Mitochondria,
        });
    }

    OrganelleLayout {
        nucleus,
        er_golgi,
        mitochondria,
    }
}

fn setup_arena(
    mut commands: Commands,
    cell_radius: Res<CellRadius>,
    mut images: ResMut<Assets<Image>>,
) {
    // Create pixel art texture for cell membrane
    let membrane_size = 128u32; // Pixel art resolution
    let membrane_texture = create_membrane_texture(membrane_size);
    let membrane_handle = images.add(membrane_texture);
    
    // Spawn the cell membrane as a pixel art sprite (z = 0, background layer)
    let membrane_diameter = cell_radius.radius * 2.0;
    commands.spawn((
        MembraneRing,
        SpriteBundle {
            texture: membrane_handle,
            sprite: Sprite {
                custom_size: Some(Vec2::new(membrane_diameter, membrane_diameter)),
                ..default()
            },
            transform: Transform::from_translation(Vec3::new(0.0, 0.0, 0.0)),
            ..default()
        },
    ));

    // Create the organelle layout
    let layout = create_default_layout(cell_radius.radius);
    
    // Create pixel art textures for organelles
    let nucleus_size = 64u32;
    let nucleus_texture = create_nucleus_texture(nucleus_size);
    let nucleus_handle = images.add(nucleus_texture);
    
    // Spawn nucleus (z = 1, in front of membrane)
    let nucleus_organelle = Organelle {
        organelle_type: OrganelleType::Nucleus,
        radius: layout.nucleus.radius,
    };
    let nucleus_diameter = layout.nucleus.radius * 2.0;
    commands.spawn((
        nucleus_organelle,
        SpriteBundle {
            texture: nucleus_handle.clone(),
            sprite: Sprite {
                custom_size: Some(Vec2::new(nucleus_diameter, nucleus_diameter)),
                ..default()
            },
            transform: Transform::from_translation(layout.nucleus.position.extend(1.0)),
            ..default()
        },
    ));

    // Create ER/Golgi texture
    let er_golgi_size = 56u32;
    let er_golgi_texture = create_er_golgi_texture(er_golgi_size);
    let er_golgi_handle = images.add(er_golgi_texture);
    
    // Spawn ER/Golgi (z = 1, same layer as other organelles)
    let er_golgi_organelle = Organelle {
        organelle_type: OrganelleType::ErGolgi,
        radius: layout.er_golgi.radius,
    };
    let er_golgi_diameter = layout.er_golgi.radius * 2.0;
    commands.spawn((
        er_golgi_organelle,
        SpriteBundle {
            texture: er_golgi_handle.clone(),
            sprite: Sprite {
                custom_size: Some(Vec2::new(er_golgi_diameter, er_golgi_diameter)),
                ..default()
            },
            transform: Transform::from_translation(layout.er_golgi.position.extend(1.0)),
            ..default()
        },
    ));

    // Create mitochondria texture
    let mito_size = 48u32;
    let mito_texture = create_mitochondria_texture(mito_size);
    let mito_handle = images.add(mito_texture);
    
    // Spawn mitochondria (z = 1, same layer as other organelles)
    for mito_pos in &layout.mitochondria {
        let mito_organelle = Organelle {
            organelle_type: OrganelleType::Mitochondria,
            radius: mito_pos.radius,
        };
        let mito_diameter = mito_pos.radius * 2.0;
        commands.spawn((
            mito_organelle,
            SpriteBundle {
                texture: mito_handle.clone(),
                sprite: Sprite {
                    custom_size: Some(Vec2::new(mito_diameter, mito_diameter)),
                    ..default()
                },
                transform: Transform::from_translation(mito_pos.position.extend(1.0)),
                ..default()
            },
        ));
    }
}

