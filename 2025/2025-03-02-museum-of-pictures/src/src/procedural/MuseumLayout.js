import { RoomGenerator } from './RoomGenerator.js';
import { HallwayGenerator } from './HallwayGenerator.js';
import { ArchitecturalStyles } from './ArchitecturalStyles.js';
import { ImageSource } from '../data/ImageSource.js';
import { MetadataManager } from '../data/MetadataManager.js';

export class MuseumLayout {
    constructor(sceneManager) {
        this.sceneManager = sceneManager;
        this.roomGenerator = new RoomGenerator();
        this.hallwayGenerator = new HallwayGenerator();
        this.architecturalStyles = new ArchitecturalStyles();
        this.imageSource = new ImageSource();
        this.metadataManager = new MetadataManager();
        
        // Track created spaces
        this.rooms = [];
        this.hallways = [];
        
        // Grid system for positioning (key: "x,y,z", value: room/hallway reference)
        this.grid = {};
        
        // Configuration
        this.roomSpacing = 15; // Distance between room centers
        this.maxRenderDistance = 50; // Max distance to render rooms
        this.generationDistance = 30; // Distance at which to generate new rooms
        
        // Museum theme regions (zones)
        this.regions = [
            {
                name: "Classical Gallery",
                style: "classical",
                center: new THREE.Vector3(0, 0, 0),
                radius: 50,
                roomTypes: ["basic", "large", "hall"],
                artThemes: ["renaissance", "classical", "historical"]
            },
            {
                name: "Futuristic Exhibition",
                style: "futuristic",
                center: new THREE.Vector3(100, 0, 0),
                radius: 50,
                roomTypes: ["basic", "corner", "large"],
                artThemes: ["modern", "technological", "abstract"]
            },
            {
                name: "Abstract Collection",
                style: "abstract",
                center: new THREE.Vector3(0, 0, 100),
                radius: 50,
                roomTypes: ["corner", "hall", "basic"],
                artThemes: ["surreal", "contemporary", "experimental"]
            }
        ];
    }
    
    async generateInitialLayout() {
        // Create entrance hall
        const entranceHall = this.roomGenerator.generateRoom("large", "classical", {
            width: 20,
            height: 8,
            depth: 20
        });
        
        // Position entrance at origin
        const entrancePosition = new THREE.Vector3(0, 0, 0);
        this.sceneManager.addRoom(entranceHall, entrancePosition);
        this.rooms.push(entranceHall);
        
        // Register the room in our grid system
        this.addToGrid(entrancePosition, entranceHall);
        
        // Set this as the current room
        this.sceneManager.setCurrentRoom(entranceHall);
        
        // Generate initial surrounding rooms and hallways
        await this.generateSurroundingRooms(entrancePosition);
        
        // Place initial artworks
        await this.placeArtworksInRoom(entranceHall);
    }
    
    async generateSurroundingRooms(centerPosition) {
        const directions = [
            { x: 0, z: 1 },  // North
            { x: 1, z: 0 },  // East
            { x: 0, z: -1 }, // South
            { x: -1, z: 0 }  // West
        ];
        
        // For each cardinal direction
        for (const dir of directions) {
            // Calculate the new room position
            const hallwayPosition = new THREE.Vector3(
                centerPosition.x + (dir.x * this.roomSpacing / 2),
                centerPosition.y,
                centerPosition.z + (dir.z * this.roomSpacing / 2)
            );
            
            const roomPosition = new THREE.Vector3(
                centerPosition.x + (dir.x * this.roomSpacing),
                centerPosition.y,
                centerPosition.z + (dir.z * this.roomSpacing)
            );
            
            // Check if there's already something at this position
            const gridKey = `${Math.round(roomPosition.x)},${Math.round(roomPosition.y)},${Math.round(roomPosition.z)}`;
            if (this.grid[gridKey]) {
                continue; // Skip if occupied
            }
            
            // Determine which region this position falls into
            const region = this.getRegionForPosition(roomPosition);
            
            // Generate a hallway connecting to the center room
            const hallwayStyle = region.style;
            const hallwayLength = this.roomSpacing / 2;
            
            const hallway = this.hallwayGenerator.generateHallway(
                "straight",
                hallwayStyle,
                {
                    width: 4,
                    height: 4,
                    length: hallwayLength
                }
            );
            
            // Rotate hallway to face the correct direction
            if (dir.x !== 0) {
                hallway.rotation.y = Math.PI / 2; // Rotate 90 degrees for east/west
            }
            
            // Add hallway to scene
            this.sceneManager.addHallway(hallway, hallwayPosition);
            this.hallways.push(hallway);
            this.addToGrid(hallwayPosition, hallway);
            
            // Generate room at the end of the hallway
            // Randomly select a room template from the region's available types
            const roomType = region.roomTypes[Math.floor(Math.random() * region.roomTypes.length)];
            const room = this.roomGenerator.generateRoom(roomType, region.style);
            
            // Add room to scene
            this.sceneManager.addRoom(room, roomPosition);
            this.rooms.push(room);
            this.addToGrid(roomPosition, room);
            
            // Place artworks in the new room
            await this.placeArtworksInRoom(room, region.artThemes);
        }
    }
    
    checkAndGenerateNewRooms(playerPosition, direction) {
        // Find the nearest room to the player
        let nearestRoom = null;
        let nearestDistance = Infinity;
        
        for (const room of this.rooms) {
            const distance = playerPosition.distanceTo(room.position);
            if (distance < nearestDistance) {
                nearestDistance = distance;
                nearestRoom = room;
            }
        }
        
        // If we're close to a room and it's not already the current room
        if (nearestRoom && nearestDistance < 5 && nearestRoom !== this.sceneManager.getCurrentRoom()) {
            this.sceneManager.setCurrentRoom(nearestRoom);
            
            // Check if we need to generate more rooms in the direction of movement
            const directionVector = new THREE.Vector3();
            
            switch(direction) {
                case 'forward':
                    directionVector.z = -1;
                    break;
                case 'backward':
                    directionVector.z = 1;
                    break;
                case 'left':
                    directionVector.x = -1;
                    break;
                case 'right':
                    directionVector.x = 1;
                    break;
            }
            
            // Rotate the direction vector based on player's rotation
            const playerRotation = this.sceneManager.getCamera().rotation.y;
            directionVector.applyAxisAngle(new THREE.Vector3(0, 1, 0), playerRotation);
            
            // Calculate the position for a potential new room
            const newRoomPosition = new THREE.Vector3(
                nearestRoom.position.x + directionVector.x * this.roomSpacing,
                nearestRoom.position.y,
                nearestRoom.position.z + directionVector.z * this.roomSpacing
            );
            
            // Check if we already have a room at this position
            const gridKey = `${Math.round(newRoomPosition.x)},${Math.round(newRoomPosition.y)},${Math.round(newRoomPosition.z)}`;
            
            // If we don't have a room here and it's within our generation distance
            if (!this.grid[gridKey] && playerPosition.distanceTo(newRoomPosition) < this.generationDistance) {
                // Generate a new room in this direction
                this.generateNewRoomInDirection(nearestRoom, directionVector);
            }
        }
    }
    
    async generateNewRoomInDirection(sourceRoom, direction) {
        // Calculate positions
        const hallwayPosition = new THREE.Vector3(
            sourceRoom.position.x + (direction.x * this.roomSpacing / 2),
            sourceRoom.position.y,
            sourceRoom.position.z + (direction.z * this.roomSpacing / 2)
        );
        
        const roomPosition = new THREE.Vector3(
            sourceRoom.position.x + (direction.x * this.roomSpacing),
            sourceRoom.position.y,
            sourceRoom.position.z + (direction.z * this.roomSpacing)
        );
        
        // Double-check that these positions are free
        const hallwayKey = `${Math.round(hallwayPosition.x)},${Math.round(hallwayPosition.y)},${Math.round(hallwayPosition.z)}`;
        const roomKey = `${Math.round(roomPosition.x)},${Math.round(roomPosition.y)},${Math.round(roomPosition.z)}`;
        
        if (this.grid[hallwayKey] || this.grid[roomKey]) {
            return; // Positions already occupied
        }
        
        // Determine region for the new room
        const region = this.getRegionForPosition(roomPosition);
        
        // Check if we're transitioning between regions
        const sourceRegion = this.getRegionForPosition(sourceRoom.position);
        const isTransition = sourceRegion.name !== region.name;
        
        // Generate hallway
        let hallway;
        if (isTransition) {
            hallway = this.hallwayGenerator.generateHallway(
                "transition",
                "transition",
                {
                    width: 4,
                    height: 4,
                    length: this.roomSpacing / 2
                },
                sourceRegion.style,
                region.style
            );
        } else {
            // Regular hallway
            hallway = this.hallwayGenerator.generateHallway(
                "straight",
                region.style,
                {
                    width: 4,
                    height: 4,
                    length: this.roomSpacing / 2
                }
            );
        }
        
        // Rotate hallway to face the correct direction
        if (Math.abs(direction.x) > Math.abs(direction.z)) {
            hallway.rotation.y = Math.PI / 2; // Rotate 90 degrees for east/west
        }
        
        // Add hallway to scene
        this.sceneManager.addHallway(hallway, hallwayPosition);
        this.hallways.push(hallway);
        this.addToGrid(hallwayPosition, hallway);
        
        // Generate the new room
        // Randomly select a room template from the region's available types
        const roomType = region.roomTypes[Math.floor(Math.random() * region.roomTypes.length)];
        const room = this.roomGenerator.generateRoom(roomType, region.style);
        
        // Add room to scene
        this.sceneManager.addRoom(room, roomPosition);
        this.rooms.push(room);
        this.addToGrid(roomPosition, room);
        
        // Place artworks in the new room
        await this.placeArtworksInRoom(room, region.artThemes);
    }
    
    async placeArtworksInRoom(room, themes = ['general']) {
        // Get artwork placement points from the room
        const placements = room.userData.artworkPlacements || [];
        
        if (placements.length === 0) {
            return; // No placement points
        }
        
        // Fetch images for this room based on themes
        const images = await this.imageSource.getImagesForThemes(themes, placements.length);
        
        if (images.length === 0) {
            return; // No images available
        }
        
        // Place images at the placement points
        for (let i = 0; i < Math.min(placements.length, images.length); i++) {
            const placement = placements[i];
            const image = images[i];
            
            // Create frame
            const frameGeometry = new THREE.BoxGeometry(
                placement.size.width + 0.2,
                placement.size.height + 0.2,
                0.1
            );
            
            const frameMaterial = new THREE.MeshStandardMaterial({
                color: 0x5c4033, // Brown color for frame
                roughness: 0.8,
                metalness: 0.2
            });
            
            const frame = new THREE.Mesh(frameGeometry, frameMaterial);
            
            // Create artwork plane
            const artworkGeometry = new THREE.PlaneGeometry(
                placement.size.width,
                placement.size.height
            );
            
            // Load image texture
            const textureLoader = new THREE.TextureLoader();
            const texture = await new Promise((resolve) => {
                textureLoader.load(
                    image.url,
                    (texture) => resolve(texture),
                    undefined,
                    () => {
                        // If loading fails, use a placeholder
                        textureLoader.load('images/placeholders/artwork_placeholder.jpg', resolve);
                    }
                );
            });
            
            const artworkMaterial = new THREE.MeshStandardMaterial({
                map: texture,
                roughness: 0.5,
                metalness: 0.0
            });
            
            const artwork = new THREE.Mesh(artworkGeometry, artworkMaterial);
            artwork.position.z = 0.06; // Slightly in front of the frame
            
            // Add artwork to frame
            frame.add(artwork);
            
            // Add metadata to artwork for info panel
            frame.userData = {
                artwork: true,
                title: image.title || 'Untitled',
                artist: image.artist || 'Unknown Artist',
                description: image.description || 'No description available',
                source: image.source || 'Unknown Source',
                url: image.url
            };
            
            // Position and rotate the framed artwork
            frame.position.copy(placement.position);
            frame.rotation.copy(placement.rotation);
            
            // Add the framed artwork to the scene
            this.sceneManager.addArtwork(frame, placement.position, placement.rotation);
        }
    }
    
    update(playerPosition) {
        // Unload distant rooms to save memory
        const numRemoved = this.sceneManager.clearDistantObjects(playerPosition, this.maxRenderDistance);
        
        if (numRemoved > 0) {
            console.log(`Unloaded ${numRemoved} distant objects`);
        }
        
        // Update level of detail for objects based on distance
        this.updateLOD(playerPosition);
    }
    
    updateLOD(playerPosition) {
        // For all rooms, adjust level of detail based on distance
        for (const room of this.rooms) {
            const distance = playerPosition.distanceTo(room.position);
            
            // Skip if room is too far
            if (distance > this.maxRenderDistance) {
                continue;
            }
            
            // Normalize distance to 0-1 range
            const normalizedDistance = Math.min(distance / this.maxRenderDistance, 1);
            
            // Apply LOD to room
            this.applyLOD(room, normalizedDistance);
        }
    }
    
    applyLOD(object, distanceFactor) {
        // For simple LOD, we just toggle visibility of some detailed elements
        object.traverse(child => {
            // If this is a mesh with "detail" in userData
            if (child.isMesh && child.userData && child.userData.detail) {
                const detailLevel = child.userData.detail;
                
                // High detail elements
                if (detailLevel === 'high') {
                    child.visible = distanceFactor < 0.7;
                }
                // Medium detail elements
                else if (detailLevel === 'medium') {
                    child.visible = distanceFactor < 0.9;
                }
                // Low detail is always visible
            }
        });
    }
    
    addToGrid(position, object) {
        // Round position to nearest grid cell
        const gridKey = `${Math.round(position.x)},${Math.round(position.y)},${Math.round(position.z)}`;
        this.grid[gridKey] = object;
    }
    
    getRegionForPosition(position) {
        // Find which region this position falls into
        let closestRegion = this.regions[0];
        let closestDistance = position.distanceTo(new THREE.Vector3(
            this.regions[0].center.x,
            this.regions[0].center.y,
            this.regions[0].center.z
        ));
        
        for (let i = 1; i < this.regions.length; i++) {
            const region = this.regions[i];
            const distance = position.distanceTo(new THREE.Vector3(
                region.center.x,
                region.center.y,
                region.center.z
            ));
            
            if (distance < closestDistance) {
                closestDistance = distance;
                closestRegion = region;
            }
        }
        
        return closestRegion;
    }
}