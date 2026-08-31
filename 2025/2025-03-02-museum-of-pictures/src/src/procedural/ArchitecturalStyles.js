export class ArchitecturalStyles {
    constructor() {
        // Define different architectural styles for the museum
        this.styles = {
            classical: {
                name: 'classical',
                // Colors
                wallColor: 0xf5f2e9,        // Off-white/cream
                floorColor: 0xc9b18f,       // Light brown/beige
                ceilingColor: 0xfffaf0,     // White/ivory
                accentColor: 0x8b7355,      // Dark brown
                
                // Materials
                wallRoughness: 0.8,
                wallMetalness: 0.0,
                floorRoughness: 0.6,
                floorMetalness: 0.1,
                ceilingRoughness: 0.5,
                ceilingMetalness: 0.0,
                accentRoughness: 0.3,
                accentMetalness: 0.2,
                
                // Optional textures (paths would be replaced with actual textures)
                wallTexture: null, // 'images/textures/classical/wall.jpg',
                floorTexture: null, // 'images/textures/classical/floor.jpg',
                ceilingTexture: null, // 'images/textures/classical/ceiling.jpg',
                
                // Architectural elements
                columnType: 'doric',
                archType: 'rounded',
                doorStyle: 'paneled',
                windowStyle: 'arched',
                
                // Decorative elements
                moldings: true,
                baseboards: true,
                cornices: true,
                
                // Lighting
                lightingStyle: 'warm',
                ambientIntensity: 0.4,
                directionalIntensity: 0.8
            },
            
            futuristic: {
                name: 'futuristic',
                // Colors
                wallColor: 0x0a1a2a,        // Dark blue
                floorColor: 0x303030,       // Dark gray
                ceilingColor: 0x0f2d4a,     // Navy blue
                accentColor: 0x00aaff,      // Bright blue
                
                // Materials
                wallRoughness: 0.2,
                wallMetalness: 0.8,
                floorRoughness: 0.1,
                floorMetalness: 0.9,
                ceilingRoughness: 0.3,
                ceilingMetalness: 0.7,
                accentRoughness: 0.1,
                accentMetalness: 1.0,
                
                // Optional textures
                wallTexture: null, // 'images/textures/futuristic/wall.jpg',
                floorTexture: null, // 'images/textures/futuristic/floor.jpg',
                ceilingTexture: null, // 'images/textures/futuristic/ceiling.jpg',
                
                // Architectural elements
                columnType: 'none',
                archType: 'angular',
                doorStyle: 'sliding',
                windowStyle: 'panoramic',
                
                // Decorative elements
                moldings: false,
                baseboards: false,
                cornices: false,
                
                // Lighting
                lightingStyle: 'cool',
                ambientIntensity: 0.3,
                directionalIntensity: 0.5
            },
            
            abstract: {
                name: 'abstract',
                // Colors
                wallColor: 0x2a0a2a,        // Dark purple
                floorColor: 0x202020,       // Near black
                ceilingColor: 0x3d0a3d,     // Purple
                accentColor: 0x00ffaa,      // Teal
                
                // Materials
                wallRoughness: 0.9,
                wallMetalness: 0.2,
                floorRoughness: 0.5,
                floorMetalness: 0.3,
                ceilingRoughness: 0.8,
                ceilingMetalness: 0.4,
                accentRoughness: 0.2,
                accentMetalness: 0.6,
                
                // Optional textures
                wallTexture: null, // 'images/textures/abstract/wall.jpg',
                floorTexture: null, // 'images/textures/abstract/floor.jpg',
                ceilingTexture: null, // 'images/textures/abstract/ceiling.jpg',
                
                // Architectural elements
                columnType: 'sculptural',
                archType: 'irregular',
                doorStyle: 'concealed',
                windowStyle: 'irregular',
                
                // Decorative elements
                moldings: false,
                baseboards: false,
                cornices: false,
                
                // Lighting
                lightingStyle: 'dramatic',
                ambientIntensity: 0.3,
                directionalIntensity: 0.3
            }
        };
    }
    
    // Get a specific style configuration
    getStyle(styleName) {
        if (this.styles[styleName]) {
            return this.styles[styleName];
        } else {
            console.warn(`Style "${styleName}" not found, defaulting to classical`);
            return this.styles.classical;
        }
    }
    
    // Get all available style names
    getStyleNames() {
        return Object.keys(this.styles);
    }
    
    // Create a transitional style that blends between two styles
    createTransitionalStyle(style1, style2, blendFactor = 0.5) {
        const style1Config = this.getStyle(style1);
        const style2Config = this.getStyle(style2);
        
        // Helper function to interpolate colors
        const lerpColor = (color1, color2, factor) => {
            const c1 = new THREE.Color(color1);
            const c2 = new THREE.Color(color2);
            return c1.lerp(c2, factor).getHex();
        };
        
        // Helper function to interpolate numbers
        const lerp = (a, b, factor) => a + (b - a) * factor;
        
        // Create blended style
        const blendedStyle = {
            name: `transition_${style1}_${style2}`,
            
            // Blend colors
            wallColor: lerpColor(style1Config.wallColor, style2Config.wallColor, blendFactor),
            floorColor: lerpColor(style1Config.floorColor, style2Config.floorColor, blendFactor),
            ceilingColor: lerpColor(style1Config.ceilingColor, style2Config.ceilingColor, blendFactor),
            accentColor: lerpColor(style1Config.accentColor, style2Config.accentColor, blendFactor),
            
            // Blend material properties
            wallRoughness: lerp(style1Config.wallRoughness, style2Config.wallRoughness, blendFactor),
            wallMetalness: lerp(style1Config.wallMetalness, style2Config.wallMetalness, blendFactor),
            floorRoughness: lerp(style1Config.floorRoughness, style2Config.floorRoughness, blendFactor),
            floorMetalness: lerp(style1Config.floorMetalness, style2Config.floorMetalness, blendFactor),
            ceilingRoughness: lerp(style1Config.ceilingRoughness, style2Config.ceilingRoughness, blendFactor),
            ceilingMetalness: lerp(style1Config.ceilingMetalness, style2Config.ceilingMetalness, blendFactor),
            accentRoughness: lerp(style1Config.accentRoughness, style2Config.accentRoughness, blendFactor),
            accentMetalness: lerp(style1Config.accentMetalness, style2Config.accentMetalness, blendFactor),
            
            // Use textures from the dominant style
            wallTexture: blendFactor < 0.5 ? style1Config.wallTexture : style2Config.wallTexture,
            floorTexture: blendFactor < 0.5 ? style1Config.floorTexture : style2Config.floorTexture,
            ceilingTexture: blendFactor < 0.5 ? style1Config.ceilingTexture : style2Config.ceilingTexture,
            
            // Use architectural elements from the dominant style
            columnType: blendFactor < 0.5 ? style1Config.columnType : style2Config.columnType,
            archType: blendFactor < 0.5 ? style1Config.archType : style2Config.archType,
            doorStyle: blendFactor < 0.5 ? style1Config.doorStyle : style2Config.doorStyle,
            windowStyle: blendFactor < 0.5 ? style1Config.windowStyle : style2Config.windowStyle,
            
            // Decorative elements based on blend factor
            moldings: blendFactor < 0.5 ? style1Config.moldings : style2Config.moldings,
            baseboards: blendFactor < 0.5 ? style1Config.baseboards : style2Config.baseboards,
            cornices: blendFactor < 0.5 ? style1Config.cornices : style2Config.cornices,
            
            // Blend lighting
            lightingStyle: blendFactor < 0.5 ? style1Config.lightingStyle : style2Config.lightingStyle,
            ambientIntensity: lerp(style1Config.ambientIntensity, style2Config.ambientIntensity, blendFactor),
            directionalIntensity: lerp(style1Config.directionalIntensity, style2Config.directionalIntensity, blendFactor)
        };
        
        return blendedStyle;
    }
    
    // Add a new custom style
    addCustomStyle(name, styleConfig) {
        // Validate style config to ensure it has all required properties
        const requiredProperties = [
            'wallColor', 'floorColor', 'ceilingColor', 'accentColor',
            'wallRoughness', 'wallMetalness', 'floorRoughness', 'floorMetalness',
            'ceilingRoughness', 'ceilingMetalness', 'accentRoughness', 'accentMetalness'
        ];
        
        const missingProperties = requiredProperties.filter(prop => !(prop in styleConfig));
        
        if (missingProperties.length > 0) {
            console.error(`Cannot add style "${name}": missing required properties: ${missingProperties.join(', ')}`);
            return false;
        }
        
        // Add the name to the style config
        styleConfig.name = name;
        
        // Add the style to our collection
        this.styles[name] = styleConfig;
        return true;
    }
}