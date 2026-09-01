/**
 * Show View controller
 * Handles WebSocket connection, canvas rendering, and scene management
 */

// Import Socket.io client
import { io } from 'https://cdn.socket.io/4.5.4/socket.io.esm.min.js';
import { Renderer } from './utils/renderer.js';
import { SceneManager } from './utils/scene-manager.js';
import { Lissajous } from './scenes/Lissajous.js';
import { PolarRoses } from './scenes/PolarRoses.js';
import { Spirograph } from './scenes/Spirograph.js';
import { DigitsRain } from './scenes/DigitsRain.js';
import { UlamSpiral } from './scenes/UlamSpiral.js';
import { ConwayLife } from './scenes/ConwayLife.js';
import { Mandelbrot } from './scenes/Mandelbrot.js';

class ShowView {
    constructor() {
        this.socket = null;
        this.statusElement = document.getElementById('status');
        this.canvas = document.getElementById('show-canvas');
        this.renderer = null;
        this.sceneManager = null;
        this.fpsTelemetryInterval = null;
        this.init();
    }

    init() {
        // Initialize canvas renderer with error handling
        if (this.canvas) {
            try {
                this.renderer = new Renderer(this.canvas);
                // Initialize scene manager
                this.sceneManager = new SceneManager(this.renderer);
                
                // Register scenes
                this.sceneManager.registerScene('lissajous', Lissajous);
                this.sceneManager.registerScene('polar-roses', PolarRoses);
                this.sceneManager.registerScene('spirograph', Spirograph);
                this.sceneManager.registerScene('digits-rain', DigitsRain);
                this.sceneManager.registerScene('ulam-spiral', UlamSpiral);
                this.sceneManager.registerScene('conway-life', ConwayLife);
                this.sceneManager.registerScene('mandelbrot', Mandelbrot);
                
                // Handle canvas resize
                window.addEventListener('resize', () => {
                    if (this.sceneManager) {
                        this.sceneManager.handleResize();
                    }
                });
                
                // Start render loop
                this.renderer.startRenderLoop((ctx, time, deltaTime) => {
                    // Delegate rendering to scene manager
                    if (this.sceneManager) {
                        this.sceneManager.render(ctx, time, deltaTime);
                    }
                });
            } catch (error) {
                console.error('Show View: Failed to initialize renderer:', error);
                this.showError('Failed to initialize canvas. Please refresh the page.');
                // Still set up WebSocket for operator communication
            }
        } else {
            console.error('Show View: Canvas element not found');
            this.showError('Canvas element not found. Please check the page setup.');
        }
        
        // Listen for renderer errors
        document.addEventListener('renderer-error', (event) => {
            const { error, type } = event.detail;
            console.error(`Renderer error (${type}):`, error);
            this.showError(`Canvas error: ${error}`);
        });
        
        this.setupWebSocket();
        this.startFPSTelemetry();
        console.log('Show View initialized');
    }
    
    showError(message) {
        const errorElement = document.getElementById('error-message');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
            // Auto-hide after 10 seconds
            setTimeout(() => {
                errorElement.classList.remove('show');
            }, 10000);
        }
    }

    setupWebSocket() {
        // Connect to show namespace
        this.socket = io('/show', {
            autoConnect: true,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000
        });

        // Connection event handlers
        this.socket.on('connect', () => {
            console.log('Show View connected to server');
            if (this.statusElement) {
                this.statusElement.textContent = 'Connected';
            }
        });

        this.socket.on('disconnect', () => {
            console.log('Show View disconnected');
            if (this.statusElement) {
                this.statusElement.textContent = 'Disconnected';
            }
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            if (this.statusElement) {
                this.statusElement.textContent = 'Connection Error';
            }
        });

        // Ping/Pong handlers
        this.socket.on('SHOW_PING', (data) => {
            console.log('Received ping from server:', data);
            // Respond immediately with pong
            this.socket.emit('SHOW_PONG', {
                timestamp: data.timestamp,
                showTimestamp: Date.now()
            });
        });

        // Handle server commands (will be expanded later)
        this.socket.on('SHOW_LOAD_TIMELINE', (data) => {
            console.log('Load timeline:', data);
            // TODO: Load timeline and start playback
        });

        this.socket.on('SHOW_PLAY', (data) => {
            console.log('Play command:', data);
            // TODO: Start/resume playback
        });

        this.socket.on('SHOW_PAUSE', () => {
            console.log('Pause command');
            // TODO: Pause playback
        });

        // Scene control handlers (for Phase 1B)
        this.socket.on('SHOW_START_SCENE', (data) => {
            console.log('Start scene:', data);
            if (this.sceneManager && data.sceneId) {
                const success = this.sceneManager.startScene(data.sceneId, data.params || {});
                console.log(`Scene start ${success ? 'successful' : 'failed'}:`, data.sceneId);
            } else {
                console.error('Cannot start scene - missing sceneManager or sceneId', {
                    hasSceneManager: !!this.sceneManager,
                    sceneId: data?.sceneId
                });
            }
        });

        this.socket.on('SHOW_UPDATE_PARAMS', (data) => {
            console.log('Update params:', data);
            if (this.sceneManager && data.params) {
                this.sceneManager.updateParams(data.params);
            }
        });

        this.socket.on('SHOW_STOP_SCENE', () => {
            console.log('Stop scene');
            if (this.sceneManager) {
                this.sceneManager.stopScene();
            }
        });
    }

    startFPSTelemetry() {
        // Emit FPS updates to server every second
        this.fpsTelemetryInterval = setInterval(() => {
            if (this.socket && this.socket.connected && this.renderer) {
                const fps = this.renderer.getFPS();
                this.socket.emit('SHOW_FPS_UPDATE', {
                    fps: fps,
                    timestamp: Date.now()
                });
            }
        }, 1000);
    }

    stopFPSTelemetry() {
        if (this.fpsTelemetryInterval) {
            clearInterval(this.fpsTelemetryInterval);
            this.fpsTelemetryInterval = null;
        }
    }

    updateStatus(text) {
        if (this.statusElement) {
            this.statusElement.textContent = text;
        }
    }

    destroy() {
        this.stopFPSTelemetry();
        if (this.sceneManager) {
            this.sceneManager.stopScene();
        }
        if (this.renderer) {
            this.renderer.stopRenderLoop();
        }
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.showView = new ShowView();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (window.showView) {
            window.showView.destroy();
        }
    });
});

