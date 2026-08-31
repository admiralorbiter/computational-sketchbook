export class SceneManager {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(
            75, // Field of view
            window.innerWidth / window.innerHeight, // Aspect ratio
            0.1, // Near clipping plane
            1000 // Far clipping plane
        );
        
        // Set initial camera position
        this.camera.position.set(0, 1.7, 0); // Eye level for average human height
        
        // Fog for distance culling and atmosphere
        this.scene.fog = new THREE.FogExp2(0x000000, 0.015);
        
        // Object collections for organization and management
        this.rooms = new THREE.Group();
        this.hallways = new THREE.Group();
        this.artworks = new THREE.Group();
        this.decorations = new THREE.Group();
        
        // Add groups to scene
        this.scene.add(this.rooms);
        this.scene.add(this.hallways);
        this.scene.add(this.artworks);
        this.scene.add(this.decorations);
        
        // Reference to current room
        this.currentRoom = null;
    }
    
    getScene() {
        return this.scene;
    }
    
    getCamera() {
        return this.camera;
    }
    
    // Add a room to the scene
    addRoom(room, position) {
        room.position.copy(position);
        this.rooms.add(room);
        return room;
    }
    
    // Add a hallway to the scene
    addHallway(hallway, position) {
        hallway.position.copy(position);
        this.hallways.add(hallway);
        return hallway;
    }
    
    // Add artwork to the scene
    addArtwork(artwork, position, rotation) {
        artwork.position.copy(position);
        if (rotation) {
            artwork.rotation.copy(rotation);
        }
        this.artworks.add(artwork);
        return artwork;
    }
    
    // Set current room (for UI updates and procedural generation)
    setCurrentRoom(room) {
        this.currentRoom = room;
        // Update HUD with current location
        if (room.userData.name) {
            document.getElementById('location-indicator').textContent = 
                `Gallery: ${room.userData.name}`;
        }
    }
    
    // Get current room
    getCurrentRoom() {
        return this.currentRoom;
    }
    
    // Clear distant objects (performance optimization)
    clearDistantObjects(cameraPosition, maxDistance) {
        const objectsToRemove = [];
        
        // Check rooms
        this.rooms.children.forEach(room => {
            if (room !== this.currentRoom && 
                room.position.distanceTo(cameraPosition) > maxDistance) {
                objectsToRemove.push({ group: this.rooms, object: room });
            }
        });
        
        // Check hallways
        this.hallways.children.forEach(hallway => {
            if (hallway.position.distanceTo(cameraPosition) > maxDistance) {
                objectsToRemove.push({ group: this.hallways, object: hallway });
            }
        });
        
        // Remove objects
        objectsToRemove.forEach(item => {
            item.group.remove(item.object);
            // Dispose geometries and materials to free memory
            if (item.object.geometry) {
                item.object.geometry.dispose();
            }
            if (item.object.material) {
                if (Array.isArray(item.object.material)) {
                    item.object.material.forEach(material => material.dispose());
                } else {
                    item.object.material.dispose();
                }
            }
        });
        
        return objectsToRemove.length; // Return number of removed objects
    }
}