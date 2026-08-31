import { InfoPanel } from './InfoPanel.js';
import { HUD } from './HUD.js';
import { ThemeStyles } from '../data/ThemeStyles.js';

export class UserInterface {
    constructor(cameraControls) {
        this.cameraControls = cameraControls;
        
        // Initialize UI components
        this.infoPanel = new InfoPanel();
        this.hud = new HUD();
        this.themeStyles = new ThemeStyles();
        
        // References to scene objects for raycasting
        this.camera = cameraControls.camera;
        this.scene = null;
        this.renderer = null;
        
        // Raycaster for interaction
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        // Current interactive object
        this.currentIntersected = null;
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Apply default theme
        this.themeStyles.applyTheme('classical');
    }
    
    setupEventListeners() {
        // Mouse move for hover effects
        document.addEventListener('mousemove', (event) => {
            // Only update if pointer is not locked (when not in camera control mode)
            if (!document.pointerLockElement) {
                this.updateMousePosition(event);
                this.checkIntersections();
            }
        });
        
        // Click for interaction
        document.addEventListener('click', (event) => {
            // Only handle click when not in pointer lock mode
            if (!document.pointerLockElement) {
                this.updateMousePosition(event);
                this.handleClick();
            }
        });
        
        // Key press for UI toggles
        document.addEventListener('keydown', (event) => {
            this.handleKeyPress(event);
        });
    }
    
    updateMousePosition(event) {
        // Calculate mouse position in normalized device coordinates
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    }
    
    checkIntersections() {
        if (!this.camera || !this.scene) return;
        
        // Update the raycaster
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        // Find all the intersected objects from artwork group
        const artworks = this.scene.children.find(child => child.name === 'artworks');
        if (!artworks) return;
        
        const intersects = this.raycaster.intersectObjects(artworks.children, true);
        
        // Handle hover effects
        if (intersects.length > 0) {
            // Find the first intersected object that has artwork data
            const artwork = intersects.find(intersect => 
                intersect.object.userData && intersect.object.userData.artwork
            );
            
            if (artwork) {
                if (this.currentIntersected !== artwork.object) {
                    // Reset previous hover effect
                    if (this.currentIntersected) {
                        this.currentIntersected.material.emissive.setHex(0x000000);
                    }
                    
                    // Set new hover effect
                    this.currentIntersected = artwork.object;
                    this.currentIntersected.material.emissive.setHex(0x333333);
                    
                    // Change cursor to indicate interactivity
                    document.body.style.cursor = 'pointer';
                }
            } else {
                // No artwork found in intersection
                this.resetIntersection();
            }
        } else {
            // No intersections at all
            this.resetIntersection();
        }
    }
    
    resetIntersection() {
        if (this.currentIntersected) {
            this.currentIntersected.material.emissive.setHex(0x000000);
            this.currentIntersected = null;
        }
        document.body.style.cursor = 'auto';
    }
    
    handleClick() {
        if (!this.camera || !this.scene) return;
        
        // Update the raycaster
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        // Find all the intersected objects from artwork group
        const artworks = this.scene.children.find(child => child.name === 'artworks');
        if (!artworks) return;
        
        const intersects = this.raycaster.intersectObjects(artworks.children, true);
        
        // Handle click on artwork
        if (intersects.length > 0) {
            // Find the first intersected object that has artwork data
            const artwork = intersects.find(intersect => 
                intersect.object.userData && intersect.object.userData.artwork
            );
            
            if (artwork) {
                // Show info panel for the artwork
                this.infoPanel.show(artwork.object);
                
                // Position the panel near the artwork
                const screenPosition = new THREE.Vector3();
                screenPosition.setFromMatrixPosition(artwork.object.matrixWorld);
                screenPosition.project(this.camera);
                
                this.infoPanel.updatePosition(screenPosition, this.camera, this.renderer);
            }
        }
    }
    
    handleKeyPress(event) {
        // Toggle minimap with 'M' key
        if (event.key === 'm' || event.key === 'M') {
            this.hud.toggleMinimap();
        }
        
        // Toggle HUD with 'H' key
        if (event.key === 'h' || event.key === 'H') {
            this.hud.toggleVisibility();
        }
        
        // Toggle info panel with 'I' key (if open)
        if ((event.key === 'i' || event.key === 'I') && !this.infoPanel.panel.classList.contains('hidden')) {
            this.infoPanel.hide();
        }
    }
    
    // Update references to scene and renderer
    setSceneAndRenderer(scene, renderer) {
        this.scene = scene;
        this.renderer = renderer;
    }
    
    // Update HUD with current location
    updateLocation(roomName) {
        this.hud.updateLocation(roomName);
    }
    
    // Update HUD compass
    updateCompass() {
        if (this.cameraControls) {
            const rotation = this.cameraControls.yawObject.rotation.y;
            this.hud.updateCompass(rotation);
        }
    }
    
    // Update HUD minimap
    updateMinimap(rooms, playerPosition) {
        this.hud.updateMinimap(rooms, playerPosition);
    }
    
    // Show notification
    showNotification(message, duration) {
        this.hud.showNotification(message, duration);
    }
    
    // Change theme based on current region
    updateThemeForRegion(regionStyle) {
        this.themeStyles.setCurrentTheme(regionStyle);
    }
    
    // Update performance stats
    updateStats(fps, objectCount) {
        this.hud.updatePerformanceStats(fps, objectCount);
    }
    
    // Main update loop for UI
    update() {
        // Update compass
        this.updateCompass();
        
        // Other periodic UI updates can be added here
    }
}