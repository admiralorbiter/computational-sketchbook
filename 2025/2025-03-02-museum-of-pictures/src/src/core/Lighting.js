export class Lighting {
    constructor(scene) {
        this.scene = scene;
        this.lights = [];
        
        // Initialize base lighting
        this.setupAmbientLight();
        
        // Create lighting presets
        this.createPresets();
    }
    
    setupAmbientLight() {
        // Global ambient light for base illumination
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);
        this.lights.push({ type: 'ambient', light: ambientLight });
    }
    
    createPresets() {
        this.presets = {
            classical: {
                ambient: { color: 0xfff1e0, intensity: 0.4 }, // Warm ambient
                directional: { color: 0xfff5e1, intensity: 0.8 }, // Sunlight through windows
                point: { color: 0xffe9b9, intensity: 0.7 } // Warm spotlight effect
            },
            futuristic: {
                ambient: { color: 0x0a1a2a, intensity: 0.3 }, // Dark blue ambient
                directional: { color: 0xffffff, intensity: 0.5 }, // Cool white light
                point: { color: 0x00aaff, intensity: 1.0 } // Blue neon glow
            },
            abstract: {
                ambient: { color: 0x2a0a2a, intensity: 0.3 }, // Purple ambient
                directional: { color: 0xff00ff, intensity: 0.3 }, // Magenta directional
                point: { color: 0x00ffaa, intensity: 0.8 } // Teal accent
            }
        };
    }
    
    // Add a new light to a specific room or area
    addRoomLight(position, type = 'point', style = 'classical', intensity = 1.0) {
        let light;
        const preset = this.presets[style] || this.presets.classical;
        
        switch(type) {
            case 'point':
                const pointSettings = preset.point;
                light = new THREE.PointLight(
                    pointSettings.color,
                    pointSettings.intensity * intensity,
                    15, // Distance
                    1 // Decay
                );
                light.castShadow = true;
                // Optimize shadow settings
                light.shadow.mapSize.width = 512;
                light.shadow.mapSize.height = 512;
                light.shadow.camera.near = 0.5;
                light.shadow.camera.far = 20;
                break;
                
            case 'spot':
                light = new THREE.SpotLight(
                    preset.directional.color,
                    preset.directional.intensity * intensity,
                    20, // Distance
                    Math.PI / 6, // Angle
                    0.5, // Penumbra
                    1 // Decay
                );
                light.castShadow = true;
                light.shadow.mapSize.width = 512;
                light.shadow.mapSize.height = 512;
                break;
                
            case 'directional':
                light = new THREE.DirectionalLight(
                    preset.directional.color,
                    preset.directional.intensity * intensity
                );
                light.castShadow = true;
                light.shadow.mapSize.width = 512;
                light.shadow.mapSize.height = 512;
                // Set the shadow camera's frustum
                light.shadow.camera.left = -10;
                light.shadow.camera.right = 10;
                light.shadow.camera.top = 10;
                light.shadow.camera.bottom = -10;
                break;
                
            case 'hemisphere':
                light = new THREE.HemisphereLight(
                    preset.ambient.color, // Sky color
                    0x404040, // Ground color
                    preset.ambient.intensity * intensity
                );
                // Hemisphere lights don't cast shadows
                break;
                
            default:
                console.warn(`Unknown light type: ${type}, defaulting to point light`);
                light = new THREE.PointLight(0xffffff, 1.0, 10, 1);
        }
        
        // Set light position
        light.position.copy(position);
        
        // Add to scene
        this.scene.add(light);
        
        // Store reference to the light
        const lightRef = { type, light, style };
        this.lights.push(lightRef);
        
        return lightRef;
    }
    
    // Create a special lighting effect for transitioning between areas
    createTransitionLighting(startPosition, endPosition, style = 'futuristic') {
        // Create a series of lights along the path
        const direction = new THREE.Vector3().subVectors(endPosition, startPosition);
        const distance = direction.length();
        const steps = Math.ceil(distance / 5); // Light every 5 units
        direction.normalize();
        
        const lights = [];
        
        for (let i = 0; i <= steps; i++) {
            const position = new THREE.Vector3().copy(startPosition).add(
                direction.clone().multiplyScalar(i * (distance / steps))
            );
            
            // Alternate colors for effect
            const colorIndex = i % 2;
            const intensity = 0.5 + (Math.sin(i / steps * Math.PI) * 0.5);
            
            const lightRef = this.addRoomLight(
                position,
                'point',
                style,
                intensity
            );
            
            lights.push(lightRef);
        }
        
        return lights;
    }
    
    // Apply a specific lighting style to an area
    applyLightingStyle(roomLights, style) {
        if (!this.presets[style]) {
            console.warn(`Unknown lighting style: ${style}, defaulting to classical`);
            style = 'classical';
        }
        
        const preset = this.presets[style];
        
        roomLights.forEach(lightRef => {
            const light = lightRef.light;
            
            switch(lightRef.type) {
                case 'ambient':
                    light.color.set(preset.ambient.color);
                    light.intensity = preset.ambient.intensity;
                    break;
                    
                case 'directional':
                case 'spot':
                    light.color.set(preset.directional.color);
                    light.intensity = preset.directional.intensity;
                    break;
                    
                case 'point':
                    light.color.set(preset.point.color);
                    light.intensity = preset.point.intensity;
                    break;
                    
                case 'hemisphere':
                    light.skyColor.set(preset.ambient.color);
                    light.intensity = preset.ambient.intensity;
                    break;
            }
            
            // Update the style reference
            lightRef.style = style;
        });
    }
    
    // Create a light that follows the camera (for testing or special effects)
    createPlayerLight() {
        const light = new THREE.PointLight(0xffffff, 0.5, 5, 1);
        this.scene.add(light);
        
        const lightRef = { type: 'player', light, style: 'personal' };
        this.lights.push(lightRef);
        
        return lightRef;
    }
    
    // Update player light position to follow camera
    updatePlayerLight(camera, lightRef) {
        if (lightRef && lightRef.type === 'player') {
            lightRef.light.position.copy(camera.position);
        }
    }
    
    // Dispose of lights that are no longer needed
    disposeLights(lightsToRemove) {
        lightsToRemove.forEach(lightRef => {
            this.scene.remove(lightRef.light);
            const index = this.lights.indexOf(lightRef);
            if (index !== -1) {
                this.lights.splice(index, 1);
            }
        });
    }
}