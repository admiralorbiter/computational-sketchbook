import { SceneManager } from './core/SceneManager.js';
import { Renderer } from './core/Renderer.js';
import { CameraControls } from './core/CameraControls.js';
import { Lighting } from './core/Lighting.js';
import { MuseumLayout } from './procedural/MuseumLayout.js';
import { UserInterface } from './ui/UserInterface.js';
import { ImageSource } from './data/ImageSource.js';
import Stats from 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/jsm/libs/stats.module.js';

class VirtualMuseumApp {
    constructor() {
        this.container = document.getElementById('container');
        this.loadingScreen = document.getElementById('loading-screen');
        
        // Initialize Stats for performance monitoring
        this.stats = new Stats();
        this.stats.showPanel(0); // 0: fps, 1: ms, 2: mb, 3+: custom
        document.getElementById('performance-stats').appendChild(this.stats.dom);
        
        // Initialize core components
        this.renderer = new Renderer(this.container);
        this.sceneManager = new SceneManager();
        this.cameraControls = new CameraControls(this.sceneManager.getCamera(), this.container);
        this.sceneManager.getScene().add(this.cameraControls.yawObject);
        this.lighting = new Lighting(this.sceneManager.getScene());
        
        // Initialize procedural generation
        this.museumLayout = new MuseumLayout(this.sceneManager);
        
        // Initialize UI
        this.userInterface = new UserInterface(this.cameraControls);
        
        // Initialize image source
        this.imageSource = new ImageSource();
        
        // Set initial position
        this.cameraControls.setPosition(new THREE.Vector3(0, this.cameraControls.playerHeight, 0));
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start the application
        this.init();
    }
    
    async init() {
        // Check if THREE is available
        if (typeof THREE === 'undefined') {
            console.error('THREE.js is not loaded!');
            this.loadingScreen.innerHTML = '<p>Error: THREE.js library not loaded</p>';
            return;
        }
        // Load initial resources
        try {
            console.log("Starting image preloading...");
            await this.imageSource.preloadImages();
            console.log("Images preloaded successfully");
            
            console.log("Generating initial layout...");
            await this.museumLayout.generateInitialLayout();
            console.log("Initial layout generated successfully");
            
            // Hide loading screen
            this.loadingScreen.classList.add('hidden');
            
            // Add a click-to-start overlay
            const clickToStartOverlay = document.createElement('div');
            clickToStartOverlay.id = 'click-to-start';
            clickToStartOverlay.innerHTML = '<div class="click-message">Click to explore the museum</div>';
            document.body.appendChild(clickToStartOverlay);
            
            // Add event listener to start the experience
            clickToStartOverlay.addEventListener('click', () => {
                // Remove the overlay
                clickToStartOverlay.remove();
                
                // Request pointer lock directly
                this.container.requestPointerLock = this.container.requestPointerLock || 
                                                    this.container.mozRequestPointerLock ||
                                                    this.container.webkitRequestPointerLock;
                this.container.requestPointerLock();
            });
            
            // Start animation loop
            this.animate();
            
            console.log("Checking renderer...");
            try {
                // Test render
                this.renderer.render(
                    this.sceneManager.getScene(),
                    this.sceneManager.getCamera()
                );
                console.log("Renderer test successful");
            } catch (error) {
                console.error("Renderer test failed:", error);
            }
            
            // Force hide loading screen with a timeout
            setTimeout(() => {
                console.log("Force hiding loading screen");
                const loadingScreen = document.getElementById('loading-screen');
                if (loadingScreen) {
                    loadingScreen.style.display = 'none';
                }
            }, 1000); // 1 second delay
        } catch (error) {
            console.error('Error initializing the application:', error);
            // Display error to user
            this.loadingScreen.innerHTML = `<p>Error loading museum: ${error.message}</p>`;
        }
    }
    
    setupEventListeners() {
        // Handle window resize
        window.addEventListener('resize', () => {
            this.renderer.onWindowResize();
            this.cameraControls.updateAspect(window.innerWidth / window.innerHeight);
        });
        
        // Track user movement for procedural generation
        document.addEventListener('keydown', (event) => {
            // Get the direction of movement from key press
            let direction = null;
            switch(event.code) {
                case 'KeyW':
                case 'ArrowUp':
                    direction = 'forward';
                    break;
                case 'KeyS':
                case 'ArrowDown':
                    direction = 'backward';
                    break;
                case 'KeyA':
                case 'ArrowLeft':
                    direction = 'left';
                    break;
                case 'KeyD':
                case 'ArrowRight':
                    direction = 'right';
                    break;
                default:
                    break;
            }
            
            // If a movement key was pressed, check if we need to generate new rooms
            if (direction) {
                this.museumLayout.checkAndGenerateNewRooms(
                    this.cameraControls.getPosition(),
                    direction
                );
            }
        });
    }
    
    animate() {
        console.log("Animation loop started");
        this.stats.begin();
        
        // Update controls
        this.cameraControls.update();
        
        // Update museum layout (LOD, unloading distant rooms, etc.)
        this.museumLayout.update(this.cameraControls.getPosition());
        
        // Render the scene
        this.renderer.render(
            this.sceneManager.getScene(),
            this.sceneManager.getCamera()
        );
        
        this.stats.end();
        
        // Continue animation loop
        requestAnimationFrame(this.animate.bind(this));
    }
}

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    new VirtualMuseumApp();
});