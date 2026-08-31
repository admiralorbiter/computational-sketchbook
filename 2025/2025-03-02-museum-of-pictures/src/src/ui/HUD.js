export class HUD {
    constructor() {
        this.hudElement = document.getElementById('hud');
        this.locationIndicator = document.getElementById('location-indicator');
        
        // Performance stats container
        this.statsContainer = document.getElementById('performance-stats');
        
        // Additional HUD elements can be initialized here
        this.initAdditionalElements();
    }
    
    /**
     * Initialize additional HUD elements
     */
    initAdditionalElements() {
        // Create a minimap container
        this.minimapContainer = document.createElement('div');
        this.minimapContainer.id = 'minimap-container';
        this.minimapContainer.style.width = '100px';
        this.minimapContainer.style.height = '100px';
        this.minimapContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.3)';
        this.minimapContainer.style.borderRadius = '50%';
        this.minimapContainer.style.marginTop = '10px';
        this.minimapContainer.style.position = 'relative';
        this.minimapContainer.style.overflow = 'hidden';
        this.minimapContainer.style.display = 'none'; // Hidden by default
        
        // Player indicator for minimap
        this.playerIndicator = document.createElement('div');
        this.playerIndicator.style.width = '8px';
        this.playerIndicator.style.height = '8px';
        this.playerIndicator.style.backgroundColor = '#ffffff';
        this.playerIndicator.style.borderRadius = '50%';
        this.playerIndicator.style.position = 'absolute';
        this.playerIndicator.style.top = '50%';
        this.playerIndicator.style.left = '50%';
        this.playerIndicator.style.transform = 'translate(-50%, -50%)';
        
        this.minimapContainer.appendChild(this.playerIndicator);
        this.hudElement.appendChild(this.minimapContainer);
        
        // Create compass indicator
        this.compassContainer = document.createElement('div');
        this.compassContainer.id = 'compass-container';
        this.compassContainer.style.width = '100px';
        this.compassContainer.style.height = '20px';
        this.compassContainer.style.marginTop = '10px';
        this.compassContainer.style.textAlign = 'center';
        this.compassContainer.textContent = 'N';
        
        this.hudElement.appendChild(this.compassContainer);
    }
    
    /**
     * Update the current location display
     */
    updateLocation(roomName) {
        if (this.locationIndicator) {
            this.locationIndicator.textContent = `Gallery: ${roomName || 'Unknown Area'}`;
        }
    }
    
    /**
     * Update compass direction based on camera rotation
     */
    updateCompass(cameraRotation) {
        // Convert rotation to cardinal direction
        // Assuming Y rotation: 0 = North, PI/2 = East, PI = South, 3PI/2 = West
        let direction = '';
        const angle = ((cameraRotation + Math.PI) % (2 * Math.PI)) / (Math.PI / 4);
        
        if (angle >= 7 || angle < 1) direction = 'N';
        else if (angle >= 1 && angle < 3) direction = 'NE';
        else if (angle >= 3 && angle < 5) direction = 'E';
        else if (angle >= 5 && angle < 7) direction = 'SE';
        else if (angle >= 7 && angle < 9) direction = 'S';
        else if (angle >= 9 && angle < 11) direction = 'SW';
        else if (angle >= 11 && angle < 13) direction = 'W';
        else if (angle >= 13 && angle < 15) direction = 'NW';
        
        if (this.compassContainer) {
            this.compassContainer.textContent = direction;
        }
    }
    
    /**
     * Update minimap with room and player positions
     */
    updateMinimap(rooms, playerPosition) {
        // Only proceed if minimap is visible
        if (this.minimapContainer.style.display === 'none') return;
        
        // Clear existing room indicators
        const existingRooms = this.minimapContainer.querySelectorAll('.room-indicator');
        existingRooms.forEach(room => room.remove());
        
        // Scale factor for minimap
        const scale = 0.1; // 10 units in world = 1 pixel on minimap
        
        // Add room indicators
        rooms.forEach(room => {
            // Only show rooms within a certain distance
            const distance = Math.sqrt(
                Math.pow(room.position.x - playerPosition.x, 2) +
                Math.pow(room.position.z - playerPosition.z, 2)
            );
            
            if (distance < 100) { // Only show rooms within 100 units
                const roomIndicator = document.createElement('div');
                roomIndicator.className = 'room-indicator';
                roomIndicator.style.width = '6px';
                roomIndicator.style.height = '6px';
                roomIndicator.style.backgroundColor = '#00aaff';
                roomIndicator.style.borderRadius = '50%';
                roomIndicator.style.position = 'absolute';
                
                // Position relative to player (center of minimap)
                const relX = (room.position.x - playerPosition.x) * scale;
                const relZ = (room.position.z - playerPosition.z) * scale;
                
                roomIndicator.style.left = `calc(50% + ${relX}px)`;
                roomIndicator.style.top = `calc(50% + ${relZ}px)`;
                
                this.minimapContainer.appendChild(roomIndicator);
            }
        });
    }
    
    /**
     * Toggle the visibility of the minimap
     */
    toggleMinimap() {
        if (this.minimapContainer.style.display === 'none') {
            this.minimapContainer.style.display = 'block';
        } else {
            this.minimapContainer.style.display = 'none';
        }
    }
    
    /**
     * Show a notification message
     */
    showNotification(message, duration = 3000) {
        // Create notification element if it doesn't exist
        if (!this.notification) {
            this.notification = document.createElement('div');
            this.notification.id = 'notification';
            this.notification.style.position = 'absolute';
            this.notification.style.bottom = '80px';
            this.notification.style.left = '20px';
            this.notification.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
            this.notification.style.color = '#ffffff';
            this.notification.style.padding = '10px 20px';
            this.notification.style.borderRadius = '5px';
            this.notification.style.fontFamily = 'Arial, sans-serif';
            this.notification.style.transition = 'opacity 0.3s ease-in-out';
            this.notification.style.opacity = '0';
            
            document.body.appendChild(this.notification);
        }
        
        // Clear any existing timeout
        if (this.notificationTimeout) {
            clearTimeout(this.notificationTimeout);
        }
        
        // Update message and show notification
        this.notification.textContent = message;
        this.notification.style.opacity = '1';
        
        // Hide after duration
        this.notificationTimeout = setTimeout(() => {
            this.notification.style.opacity = '0';
        }, duration);
    }
    
    /**
     * Update performance stats
     */
    updatePerformanceStats(fps, objectCount) {
        if (this.statsContainer) {
            this.statsContainer.textContent = `FPS: ${fps} | Objects: ${objectCount}`;
        }
    }
    
    /**
     * Toggle HUD visibility
     */
    toggleVisibility() {
        if (this.hudElement.style.display === 'none') {
            this.hudElement.style.display = 'block';
        } else {
            this.hudElement.style.display = 'none';
        }
    }
}