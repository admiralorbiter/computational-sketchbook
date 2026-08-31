import { ArchitecturalStyles } from './ArchitecturalStyles.js';

export class RoomGenerator {
    constructor() {
        this.architecturalStyles = new ArchitecturalStyles();
        this.roomCounter = 0;
        
        // Room size parameters
        this.defaultRoomSize = {
            width: 10,
            height: 5,
            depth: 10
        };
        
        // Room templates
        this.roomTemplates = {
            basic: this.createBasicRoom.bind(this),
            large: this.createLargeRoom.bind(this),
            hall: this.createHallRoom.bind(this),
            corner: this.createCornerRoom.bind(this)
        };
    }
    
    generateRoom(template = 'basic', style = 'classical', size = null) {
        // Use template function or default to basic
        const templateFunction = this.roomTemplates[template] || this.roomTemplates.basic;
        
        // Get style configuration
        const styleConfig = this.architecturalStyles.getStyle(style);
        
        // Generate the room using the template
        const room = templateFunction(styleConfig, size);
        
        // Store room metadata WITHOUT overwriting existing userData
        room.userData = {
            ...room.userData,  // Preserve existing userData properties
            id: `room_${this.roomCounter++}`,
            name: `${style.charAt(0).toUpperCase() + style.slice(1)} ${template.charAt(0).toUpperCase() + template.slice(1)}`,
            template,
            style,
            created: Date.now()
        };
        
        // Setup room walls for artwork placement
        this.setupArtworkWalls(room);
        
        return room;
    }
    
    createBasicRoom(styleConfig, customSize = null) {
        const size = customSize || this.defaultRoomSize;
        const room = new THREE.Group();
        
        // Floor
        const floorGeometry = new THREE.PlaneGeometry(size.width, size.depth);
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
            texture.repeat.set(size.width / 2, size.depth / 2);
            floorMaterial.map = texture;
        }
        
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = 0;
        floor.receiveShadow = true;
        room.add(floor);
        
        // Ceiling
        const ceilingGeometry = new THREE.PlaneGeometry(size.width, size.depth);
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
            texture.repeat.set(size.width / 2, size.depth / 2);
            ceilingMaterial.map = texture;
        }
        
        const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = size.height;
        ceiling.receiveShadow = true;
        room.add(ceiling);
        
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
        
        // Front wall (with door)
        const frontWallGroup = new THREE.Group();
        const doorWidth = 2;
        const doorHeight = 3;
        
        // Left part of front wall
        const frontWallLeftGeometry = new THREE.PlaneGeometry(
            (size.width - doorWidth) / 2,
            size.height
        );
        const frontWallLeft = new THREE.Mesh(frontWallLeftGeometry, wallMaterial);
        frontWallLeft.position.set(-(size.width - doorWidth) / 4 - doorWidth / 2, size.height / 2, size.depth / 2);
        frontWallLeft.castShadow = true;
        frontWallLeft.receiveShadow = true;
        frontWallGroup.add(frontWallLeft);
        
        // Right part of front wall
        const frontWallRightGeometry = new THREE.PlaneGeometry(
            (size.width - doorWidth) / 2,
            size.height
        );
        const frontWallRight = new THREE.Mesh(frontWallRightGeometry, wallMaterial);
        frontWallRight.position.set((size.width - doorWidth) / 4 + doorWidth / 2, size.height / 2, size.depth / 2);
        frontWallRight.castShadow = true;
        frontWallRight.receiveShadow = true;
        frontWallGroup.add(frontWallRight);
        
        // Top part of front wall (above door)
        const frontWallTopGeometry = new THREE.PlaneGeometry(
            doorWidth,
            size.height - doorHeight
        );
        const frontWallTop = new THREE.Mesh(frontWallTopGeometry, wallMaterial);
        frontWallTop.position.set(0, size.height - (size.height - doorHeight) / 2, size.depth / 2);
        frontWallTop.castShadow = true;
        frontWallTop.receiveShadow = true;
        frontWallGroup.add(frontWallTop);
        
        room.add(frontWallGroup);
        
        // Back wall
        const backWallGeometry = new THREE.PlaneGeometry(size.width, size.height);
        const backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
        backWall.position.set(0, size.height / 2, -size.depth / 2);
        backWall.rotation.y = Math.PI;
        backWall.castShadow = true;
        backWall.receiveShadow = true;
        room.add(backWall);
        
        // Left wall
        const leftWallGeometry = new THREE.PlaneGeometry(size.depth, size.height);
        const leftWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
        leftWall.position.set(-size.width / 2, size.height / 2, 0);
        leftWall.rotation.y = Math.PI / 2;
        leftWall.castShadow = true;
        leftWall.receiveShadow = true;
        room.add(leftWall);
        
        // Right wall
        const rightWallGeometry = new THREE.PlaneGeometry(size.depth, size.height);
        const rightWall = new THREE.Mesh(rightWallGeometry, wallMaterial);
        rightWall.position.set(size.width / 2, size.height / 2, 0);
        rightWall.rotation.y = -Math.PI / 2;
        rightWall.castShadow = true;
        rightWall.receiveShadow = true;
        room.add(rightWall);
        
        // Store wall references for artwork placement
        room.userData.walls = {
            front: frontWallGroup,
            back: backWall,
            left: leftWall,
            right: rightWall
        };
        
        // Store room dimensions
        room.userData.size = { ...size };
        
        return room;
    }
    
    createLargeRoom(styleConfig, customSize = null) {
        // Create a larger room with columns or special features
        const defaultLargeSize = {
            width: 20,
            height: 8,
            depth: 20
        };
        
        const size = customSize || defaultLargeSize;
        
        // Start with a basic room
        const room = this.createBasicRoom(styleConfig, size);
        
        // Add columns
        const columnRadius = 0.5;
        const columnHeight = size.height;
        const columnGeometry = new THREE.CylinderGeometry(
            columnRadius, columnRadius, columnHeight, 16
        );
        
        const columnMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.accentColor,
            roughness: styleConfig.accentRoughness,
            metalness: styleConfig.accentMetalness
        });
        
        // Position columns in the room
        const columnPositions = [
            { x: -size.width / 4, z: -size.depth / 4 },
            { x: size.width / 4, z: -size.depth / 4 },
            { x: -size.width / 4, z: size.depth / 4 },
            { x: size.width / 4, z: size.depth / 4 }
        ];
        
        columnPositions.forEach(pos => {
            const column = new THREE.Mesh(columnGeometry, columnMaterial);
            column.position.set(pos.x, columnHeight / 2, pos.z);
            column.castShadow = true;
            column.receiveShadow = true;
            room.add(column);
        });
        
        return room;
    }
    
    createHallRoom(styleConfig, customSize = null) {
        // Create a hallway-like room with display alcoves
        const defaultHallSize = {
            width: 8,
            height: 5,
            depth: 20
        };
        
        const size = customSize || defaultHallSize;
        
        // Start with a basic room
        const room = this.createBasicRoom(styleConfig, size);
        
        // Add display alcoves along the walls
        const alcoveWidth = 3;
        const alcoveDepth = 1;
        const alcoveHeight = 3;
        const alcoveSpacing = 5;
        
        const alcoveMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.accentColor,
            roughness: styleConfig.accentRoughness,
            metalness: styleConfig.accentMetalness
        });
        
        // Left wall alcoves
        const leftWall = room.userData.walls.left;
        const numAlcovesPerWall = Math.floor(size.depth / alcoveSpacing) - 1;
        
        for (let i = 0; i < numAlcovesPerWall; i++) {
            const alcovePosition = -size.depth / 2 + (i + 1) * alcoveSpacing;
            
            // Alcove back
            const alcoveBackGeometry = new THREE.PlaneGeometry(alcoveWidth, alcoveHeight);
            const alcoveBack = new THREE.Mesh(alcoveBackGeometry, alcoveMaterial);
            alcoveBack.position.set(
                -size.width / 2 - alcoveDepth,
                alcoveHeight / 2 + 1, // Raised slightly above the floor
                alcovePosition
            );
            alcoveBack.rotation.y = -Math.PI / 2;
            alcoveBack.castShadow = true;
            alcoveBack.receiveShadow = true;
            room.add(alcoveBack);
            
            // Store alcove for artwork placement
            if (!room.userData.alcoves) {
                room.userData.alcoves = [];
            }
            room.userData.alcoves.push({
                position: new THREE.Vector3(
                    -size.width / 2 - alcoveDepth + 0.1, // Slight offset to avoid z-fighting
                    alcoveHeight / 2 + 1,
                    alcovePosition
                ),
                rotation: new THREE.Euler(0, -Math.PI / 2, 0),
                size: { width: alcoveWidth, height: alcoveHeight }
            });
        }
        
        // Right wall alcoves
        const rightWall = room.userData.walls.right;
        
        for (let i = 0; i < numAlcovesPerWall; i++) {
            const alcovePosition = -size.depth / 2 + (i + 1) * alcoveSpacing;
            
            // Alcove back
            const alcoveBackGeometry = new THREE.PlaneGeometry(alcoveWidth, alcoveHeight);
            const alcoveBack = new THREE.Mesh(alcoveBackGeometry, alcoveMaterial);
            alcoveBack.position.set(
                size.width / 2 + alcoveDepth,
                alcoveHeight / 2 + 1, // Raised slightly above the floor
                alcovePosition
            );
            alcoveBack.rotation.y = Math.PI / 2;
            alcoveBack.castShadow = true;
            alcoveBack.receiveShadow = true;
            room.add(alcoveBack);
            
            // Store alcove for artwork placement
            if (!room.userData.alcoves) {
                room.userData.alcoves = [];
            }
            room.userData.alcoves.push({
                position: new THREE.Vector3(
                    size.width / 2 + alcoveDepth - 0.1, // Slight offset to avoid z-fighting
                    alcoveHeight / 2 + 1,
                    alcovePosition
                ),
                rotation: new THREE.Euler(0, Math.PI / 2, 0),
                size: { width: alcoveWidth, height: alcoveHeight }
            });
        }
        
        return room;
    }
    
    createCornerRoom(styleConfig, customSize = null) {
        // Create a corner-style room with an angled entrance
        const defaultCornerSize = {
            width: 12,
            height: 5,
            depth: 12
        };
        
        const size = customSize || defaultCornerSize;
        
        // Start with a basic room but without the front wall
        const room = new THREE.Group();
        
        // Floor
        const floorGeometry = new THREE.PlaneGeometry(size.width, size.depth);
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
            texture.repeat.set(size.width / 2, size.depth / 2);
            floorMaterial.map = texture;
        }
        
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = 0;
        floor.receiveShadow = true;
        room.add(floor);
        
        // Ceiling
        const ceilingGeometry = new THREE.PlaneGeometry(size.width, size.depth);
        const ceilingMaterial = new THREE.MeshStandardMaterial({
            color: styleConfig.ceilingColor,
            roughness: styleConfig.ceilingRoughness,
            metalness: styleConfig.ceilingMetalness
        });
        
        const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = size.height;
        ceiling.receiveShadow = true;
        room.add(ceiling);
        
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
        
        // Angled entrance (front-left corner is open)
        
        // Back wall
        const backWallGeometry = new THREE.PlaneGeometry(size.width, size.height);
        const backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
        backWall.position.set(0, size.height / 2, -size.depth / 2);
        backWall.rotation.y = Math.PI;
        backWall.castShadow = true;
        backWall.receiveShadow = true;
        room.add(backWall);
        
        // Right wall
        const rightWallGeometry = new THREE.PlaneGeometry(size.depth, size.height);
        const rightWall = new THREE.Mesh(rightWallGeometry, wallMaterial);
        rightWall.position.set(size.width / 2, size.height / 2, 0);
        rightWall.rotation.y = -Math.PI / 2;
        rightWall.castShadow = true;
        rightWall.receiveShadow = true;
        room.add(rightWall);
        
        // Partial left wall
        const leftWallGeometry = new THREE.PlaneGeometry(size.depth / 2, size.height);
        const leftWall = new THREE.Mesh(leftWallGeometry, wallMaterial);
        leftWall.position.set(-size.width / 2, size.height / 2, -size.depth / 4);
        leftWall.rotation.y = Math.PI / 2;
        leftWall.castShadow = true;
        leftWall.receiveShadow = true;
        room.add(leftWall);
        
        // Partial front wall
        const frontWallGeometry = new THREE.PlaneGeometry(size.width / 2, size.height);
        const frontWall = new THREE.Mesh(frontWallGeometry, wallMaterial);
        frontWall.position.set(size.width / 4, size.height / 2, size.depth / 2);
        frontWall.castShadow = true;
        frontWall.receiveShadow = true;
        room.add(frontWall);
        
        // Diagonal wall to create corner entrance
        const diagonalWallLength = Math.sqrt(Math.pow(size.width / 2, 2) + Math.pow(size.depth / 2, 2));
        const diagonalWallGeometry = new THREE.PlaneGeometry(diagonalWallLength, size.height);
        const diagonalWall = new THREE.Mesh(diagonalWallGeometry, wallMaterial);
        diagonalWall.position.set(-size.width / 4, size.height / 2, size.depth / 4);
        diagonalWall.rotation.y = Math.PI / 4;
        diagonalWall.castShadow = true;
        diagonalWall.receiveShadow = true;
        room.add(diagonalWall);
        
        // Store wall references for artwork placement
        room.userData.walls = {
            back: backWall,
            right: rightWall,
            left: leftWall,
            front: frontWall,
            diagonal: diagonalWall
        };
        
        // Store room dimensions
        room.userData.size = { ...size };
        
        return room;
    }
    
    setupArtworkWalls(room) {
        // Define artwork placement points on walls
        const artworkPlacements = [];
        const walls = room.userData.walls;
        const size = room.userData.size;
        
        // Check if walls is defined before trying to access properties
        if (!walls) {
            console.warn('No walls defined for room:', room.userData.id);
            room.userData.artworkPlacements = [];
            return;
        }
        
        // Artwork dimensions
        const artworkWidth = 2;
        const artworkHeight = 1.5;
        const artworkSpacing = 0.5;
        const heightFromFloor = 1.7; // Eye level
        
        // Back wall placements
        if (walls.back) {
            const backWallWidth = size.width;
            const numPlacements = Math.floor(backWallWidth / (artworkWidth + artworkSpacing));
            const startX = -(numPlacements - 1) * (artworkWidth + artworkSpacing) / 2;
            
            for (let i = 0; i < numPlacements; i++) {
                artworkPlacements.push({
                    position: new THREE.Vector3(
                        startX + i * (artworkWidth + artworkSpacing),
                        heightFromFloor,
                        -size.depth / 2 + 0.1 // Slight offset to avoid z-fighting
                    ),
                    rotation: new THREE.Euler(0, 0, 0),
                    size: { width: artworkWidth, height: artworkHeight },
                    wall: 'back'
                });
            }
        }
        
        // Side wall placements
        if (walls.left) {
            const leftWallDepth = size.depth;
            const numPlacements = Math.floor(leftWallDepth / (artworkWidth + artworkSpacing));
            const startZ = -(numPlacements - 1) * (artworkWidth + artworkSpacing) / 2;
            
            for (let i = 0; i < numPlacements; i++) {
                artworkPlacements.push({
                    position: new THREE.Vector3(
                        -size.width / 2 + 0.1, // Slight offset to avoid z-fighting
                        heightFromFloor,
                        startZ + i * (artworkWidth + artworkSpacing)
                    ),
                    rotation: new THREE.Euler(0, Math.PI / 2, 0),
                    size: { width: artworkWidth, height: artworkHeight },
                    wall: 'left'
                });
            }
        }
        
        if (walls.right) {
            const rightWallDepth = size.depth;
            const numPlacements = Math.floor(rightWallDepth / (artworkWidth + artworkSpacing));
            const startZ = -(numPlacements - 1) * (artworkWidth + artworkSpacing) / 2;
            
            for (let i = 0; i < numPlacements; i++) {
                artworkPlacements.push({
                    position: new THREE.Vector3(
                        size.width / 2 - 0.1, // Slight offset to avoid z-fighting
                        heightFromFloor,
                        startZ + i * (artworkWidth + artworkSpacing)
                    ),
                    rotation: new THREE.Euler(0, -Math.PI / 2, 0),
                    size: { width: artworkWidth, height: artworkHeight },
                    wall: 'right'
                });
            }
        }
        
        // Add any alcove placements from hall room
        if (room.userData.alcoves) {
            artworkPlacements.push(...room.userData.alcoves);
        }
        
        // Store artwork placement points in room userData
        room.userData.artworkPlacements = artworkPlacements;
    }
}