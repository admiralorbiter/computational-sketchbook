import { ArchitecturalStyles } from './ArchitecturalStyles.js';

export class HallwayGenerator {
    constructor() {
        this.architecturalStyles = new ArchitecturalStyles();
        this.hallwayCounter = 0;
        
        // Default hallway parameters
        this.defaultHallwaySize = {
            width: 4,   // Width of the hallway
            height: 4,  // Height of the hallway
            length: 10  // Length of the hallway
        };
        
        // Hallway templates
        this.hallwayTemplates = {
            straight: this.createStraightHallway.bind(this),
            curved: this.createCurvedHallway.bind(this),
            stairs: this.createStairsHallway.bind(this),
            transition: this.createTransitionHallway.bind(this)
        };
    }
    
    generateHallway(template = 'straight', style = 'classical', size = null, startStyle = null, endStyle = null) {
        // Use template function or default to straight
        const templateFunction = this.hallwayTemplates[template] || this.hallwayTemplates.straight;
        
        // Get style configuration
        const styleConfig = this.architecturalStyles.getStyle(style);
        
        // For transition hallways, get start and end styles
        let startStyleConfig = styleConfig;
        let endStyleConfig = styleConfig;
        
        if (template === 'transition' && startStyle && endStyle) {
            startStyleConfig = this.architecturalStyles.getStyle(startStyle);
            endStyleConfig = this.architecturalStyles.getStyle(endStyle);
        }
        
        // Generate the hallway using the template
        const hallway = templateFunction(
            styleConfig, 
            size, 
            startStyleConfig, 
            endStyleConfig
        );
        
        // Store hallway metadata
        hallway.userData = {
            id: `hallway_${this.hallwayCounter++}`,
            name: `${style.charAt(0).toUpperCase() + style.slice(1)} ${template.charAt(0).toUpperCase() + template.slice(1)}`,
            template,
            style,
            created: Date.now()
        };
        
        // Store hallway dimensions
        hallway.userData.size = size || this.defaultHallwaySize;
        
        return hallway;
    }
    
    createStraightHallway(styleConfig, customSize = null) {
        const size = customSize || this.defaultHallwaySize;
        const hallway = new THREE.Group();
        
        // Floor
        const floorGeometry = new THREE.PlaneGeometry(size.width, size.length);
        const floorMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.floorColor,
            roughness: styleConfig.floorRoughness,
            metalness: styleConfig.floorMetalness
        });
        
        if (styleConfig.floorTexture) {
            const textureLoader = new THREE.TextureLoader();
            const texture = textureLoader.load(styleConfig.floorTexture);
            texture.wrapS = THREE.RepeatWrapping;
            texture.wrapT = THREE.RepeatWrapping;
            texture.repeat.set(size.width / 2, size.length / 2);
            floorMaterial.map = texture;
        }
        
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = 0;
        floor.receiveShadow = true;
        hallway.add(floor);
        
        // Ceiling
        const ceilingGeometry = new THREE.PlaneGeometry(size.width, size.length);
        const ceilingMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.ceilingColor,
            roughness: styleConfig.ceilingRoughness,
            metalness: styleConfig.ceilingMetalness
        });
        
        if (styleConfig.ceilingTexture) {
            const textureLoader = new THREE.TextureLoader();
            const texture = textureLoader.load(styleConfig.ceilingTexture);
            texture.wrapS = THREE.RepeatWrapping;
            texture.wrapT = THREE.RepeatWrapping;
            texture.repeat.set(size.width / 2, size.length / 2);
            ceilingMaterial.map = texture;
        }
        
        const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = size.height;
        ceiling.receiveShadow = true;
        hallway.add(ceiling);
        
        // Walls
        const wallMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.wallColor,
            roughness: styleConfig.wallRoughness,
            metalness: styleConfig.wallMetalness
        });
        
        if (styleConfig.wallTexture) {
            const textureLoader = new THREE.TextureLoader();
            const texture = textureLoader.load(styleConfig.wallTexture);
            texture.wrapS = THREE.RepeatWrapping;
            texture.wrapT = THREE.RepeatWrapping;
            wallMaterial.map = texture;
        }
        
        // Left wall
        const leftWallGeometry = new THREE.PlaneGeometry(size.length, size.height);
        const leftWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
        leftWall.position.set(-size.width / 2, size.height / 2, 0);
        leftWall.rotation.y = Math.PI / 2;
        leftWall.castShadow = true;
        leftWall.receiveShadow = true;
        hallway.add(leftWall);
        
        // Right wall
        const rightWallGeometry = new THREE.PlaneGeometry(size.length, size.height);
        const rightWall = new THREE.Mesh(rightWallGeometry, wallMaterial);
        rightWall.position.set(size.width / 2, size.height / 2, 0);
        rightWall.rotation.y = -Math.PI / 2;
        rightWall.castShadow = true;
        rightWall.receiveShadow = true;
        hallway.add(rightWall);
        
        // Store hallway direction (for connecting rooms)
        hallway.userData.direction = new THREE.Vector3(0, 0, 1); // Forward along Z-axis
        
        return hallway;
    }
    
    createCurvedHallway(styleConfig, customSize = null) {
        const size = customSize || this.defaultHallwaySize;
        const hallway = new THREE.Group();
        
        // For a curved hallway, we'll create a series of segments that rotate slightly
        const numSegments = 10;
        const segmentLength = size.length / numSegments;
        const totalAngle = Math.PI / 2; // 90-degree turn
        const anglePerSegment = totalAngle / numSegments;
        
        for (let i = 0; i < numSegments; i++) {
            // Create a segment
            const segmentSize = {
                width: size.width,
                height: size.height,
                length: segmentLength
            };
            
            const segment = this.createStraightHallway(styleConfig, segmentSize);
            
            // Position and rotate segment
            const angle = i * anglePerSegment;
            const radius = size.length / (Math.PI / 2); // Radius for a 90-degree turn
            
            // Calculate position along the curve
            const x = radius * Math.sin(angle);
            const z = radius * (1 - Math.cos(angle));
            
            segment.position.set(x, 0, z);
            segment.rotation.y = angle;
            
            hallway.add(segment);
        }
        
        // Store hallway direction (for connecting rooms)
        hallway.userData.direction = new THREE.Vector3(1, 0, 0); // Ends pointing along X-axis after 90-degree turn
        hallway.userData.isCurved = true;
        
        return hallway;
    }
    
    createStairsHallway(styleConfig, customSize = null) {
        const size = customSize || this.defaultHallwaySize;
        const hallway = new THREE.Group();
        
        // Create a series of steps with landings
        const stepHeight = 0.25; // Each step height
        const stepDepth = 0.5;  // Each step depth
        const numSteps = Math.floor((size.height * 0.6) / stepHeight); // Use 60% of the hallway height for steps
        const totalStepHeight = numSteps * stepHeight;
        
        // Floor (landing at start)
        const landingLength = (size.length - (numSteps * stepDepth)) / 2;
        
        const floorMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.floorColor,
            roughness: styleConfig.floorRoughness,
            metalness: styleConfig.floorMetalness
        });
        
        // First landing
        const startLandingGeometry = new THREE.PlaneGeometry(size.width, landingLength);
        const startLanding = new THREE.Mesh(startLandingGeometry, floorMaterial);
        startLanding.rotation.x = -Math.PI / 2;
        startLanding.position.set(0, 0, -size.length / 2 + landingLength / 2);
        startLanding.receiveShadow = true;
        hallway.add(startLanding);
        
        // Steps
        const stepMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.accentColor,
            roughness: styleConfig.accentRoughness,
            metalness: styleConfig.accentMetalness
        });
        
        for (let i = 0; i < numSteps; i++) {
            // Step tread
            const stepTreadGeometry = new THREE.BoxGeometry(size.width, stepHeight, stepDepth);
            const stepTread = new THREE.Mesh(stepTreadGeometry, stepMaterial);
            stepTread.position.set(
                0,
                i * stepHeight + stepHeight / 2,
                -size.length / 2 + landingLength + i * stepDepth + stepDepth / 2
            );
            stepTread.castShadow = true;
            stepTread.receiveShadow = true;
            hallway.add(stepTread);
        }
        
        // Second landing
        const endLandingGeometry = new THREE.PlaneGeometry(size.width, landingLength);
        const endLanding = new THREE.Mesh(endLandingGeometry, floorMaterial);
        endLanding.rotation.x = -Math.PI / 2;
        endLanding.position.set(
            0,
            totalStepHeight,
            size.length / 2 - landingLength / 2
        );
        endLanding.receiveShadow = true;
        hallway.add(endLanding);
        
        // Walls
        const wallMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.wallColor,
            roughness: styleConfig.wallRoughness,
            metalness: styleConfig.wallMetalness
        });
        
        // Left wall
        const leftWallGeometry = new THREE.PlaneGeometry(size.length, size.height + totalStepHeight);
        const leftWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
        leftWall.position.set(
            -size.width / 2,
            (size.height + totalStepHeight) / 2,
            0
        );
        leftWall.rotation.y = Math.PI / 2;
        leftWall.castShadow = true;
        leftWall.receiveShadow = true;
        hallway.add(leftWall);
        
        // Right wall
        const rightWallGeometry = new THREE.PlaneGeometry(size.length, size.height + totalStepHeight);
        const rightWall = new THREE.Mesh(rightWallGeometry, wallMaterial);
        rightWall.position.set(
            size.width / 2,
            (size.height + totalStepHeight) / 2,
            0
        );
        rightWall.rotation.y = -Math.PI / 2;
        rightWall.castShadow = true;
        rightWall.receiveShadow = true;
        hallway.add(rightWall);
        
        // Ceiling
        const ceilingGeometry = new THREE.PlaneGeometry(size.width, size.length);
        const ceilingMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.ceilingColor,
            roughness: styleConfig.ceilingRoughness,
            metalness: styleConfig.ceilingMetalness
        });
        
        const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.set(0, size.height + totalStepHeight, 0);
        ceiling.receiveShadow = true;
        hallway.add(ceiling);
        
        // Store hallway direction and elevation change
        hallway.userData.direction = new THREE.Vector3(0, 0, 1);
        hallway.userData.elevationChange = totalStepHeight;
        
        return hallway;
    }
    
    createTransitionHallway(styleConfig, customSize = null, startStyleConfig = null, endStyleConfig = null) {
        const size = customSize || this.defaultHallwaySize;
        const hallway = new THREE.Group();
        
        // Create a hallway that transitions between two different architectural styles
        // If no specific start/end styles provided, use the passed styleConfig
        if (!startStyleConfig) startStyleConfig = styleConfig;
        if (!endStyleConfig) endStyleConfig = styleConfig;
        
        // Floor
        const floorGeometry = new THREE.PlaneGeometry(size.width, size.length);
        // Create floor with gradient material
        const floorMaterial = new THREE.ShaderMaterial({
            uniforms: {
                colorStart: { value: new THREE.Color(startStyleConfig.floorColor) },
                colorEnd: { value: new THREE.Color(endStyleConfig.floorColor) }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 colorStart;
                uniform vec3 colorEnd;
                varying vec2 vUv;
                void main() {
                    gl_FragColor = vec4(mix(colorStart, colorEnd, vUv.y), 1.0);
                }
            `
        });
        
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = 0;
        floor.receiveShadow = true;
        hallway.add(floor);
        
        // Ceiling
        const ceilingGeometry = new THREE.PlaneGeometry(size.width, size.length);
        // Create ceiling with gradient material
        const ceilingMaterial = new THREE.ShaderMaterial({
            uniforms: {
                colorStart: { value: new THREE.Color(startStyleConfig.ceilingColor) },
                colorEnd: { value: new THREE.Color(endStyleConfig.ceilingColor) }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 colorStart;
                uniform vec3 colorEnd;
                varying vec2 vUv;
                void main() {
                    gl_FragColor = vec4(mix(colorStart, colorEnd, vUv.y), 1.0);
                }
            `
        });
        
        const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = size.height;
        ceiling.receiveShadow = true;
        hallway.add(ceiling);
        
        // Walls with gradient material
        const leftWallGeometry = new THREE.PlaneGeometry(size.length, size.height);
        const leftWallMaterial = new THREE.ShaderMaterial({
            uniforms: {
                colorStart: { value: new THREE.Color(startStyleConfig.wallColor) },
                colorEnd: { value: new THREE.Color(endStyleConfig.wallColor) }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 colorStart;
                uniform vec3 colorEnd;
                varying vec2 vUv;
                void main() {
                    gl_FragColor = vec4(mix(colorStart, colorEnd, vUv.x), 1.0);
                }
            `
        });
        
        const leftWall = new THREE.Mesh(leftWallGeometry, leftWallMaterial);
        leftWall.position.set(-size.width / 2, size.height / 2, 0);
        leftWall.rotation.y = Math.PI / 2;
        leftWall.castShadow = true;
        leftWall.receiveShadow = true;
        hallway.add(leftWall);
        
        const rightWall = new THREE.Mesh(leftWallGeometry, leftWallMaterial);
        rightWall.position.set(size.width / 2, size.height / 2, 0);
        rightWall.rotation.y = -Math.PI / 2;
        rightWall.castShadow = true;
        rightWall.receiveShadow = true;
        hallway.add(rightWall);
        
        // Add some transition elements
        const numElements = 5;
        const spacing = size.length / (numElements + 1);
        
        for (let i = 0; i < numElements; i++) {
            const progress = (i + 1) / (numElements + 1);
            const position = -size.length / 2 + (i + 1) * spacing;
            
            // Create a decorative element that transitions between styles
            // Interpolate between start and end colors
            const color = new THREE.Color().lerpColors(
                new THREE.Color(startStyleConfig.accentColor),
                new THREE.Color(endStyleConfig.accentColor),
                progress
            );
            
            const elementMaterial = new THREE.MeshStandardMaterial({
                color: color,
                roughness: 0.5,
                metalness: 0.5
            });
            
            // Transition from rectangular to circular elements
            let elementGeometry;
            if (progress < 0.5) {
                // More rectangular
                const boxWidth = size.width * 0.2;
                const boxHeight = size.height * 0.1;
                const boxDepth = 0.2;
                elementGeometry = new THREE.BoxGeometry(boxWidth, boxHeight, boxDepth);
            } else {
                // More circular
                const radius = size.width * 0.08;
                const segments = 16;
                elementGeometry = new THREE.CylinderGeometry(radius, radius, size.height * 0.1, segments);
                // Rotate to stand upright
                const element = new THREE.Mesh(elementGeometry, elementMaterial);
                element.rotation.x = Math.PI / 2;
                element.position.set(0, size.height * 0.75, position);
                element.castShadow = true;
                element.receiveShadow = true;
                hallway.add(element);
                
                // Continue to next iteration, since we've already added the element
                continue;
            }
            
            const element = new THREE.Mesh(elementGeometry, elementMaterial);
            element.position.set(0, size.height * 0.75, position);
            element.castShadow = true;
            element.receiveShadow = true;
            hallway.add(element);
        }
        
        // Store hallway direction
        hallway.userData.direction = new THREE.Vector3(0, 0, 1);
        hallway.userData.isTransition = true;
        hallway.userData.startStyle = startStyleConfig.name;
        hallway.userData.endStyle = endStyleConfig.name;
        
        return hallway;
    }
}