/**
 * Main Operator UI controller
 * Handles WebSocket connection and UI initialization
 */

// Import Socket.io client
import { io } from 'https://cdn.socket.io/4.5.4/socket.io.esm.min.js';

class OperatorUI {
    constructor() {
        this.socket = null;
        this.connectionStatus = document.getElementById('connection-status');
        // Expose to window for scene-controls component
        window.operatorUI = this;
        this.init();
    }

    init() {
        this.setupWebSocket();
        this.setupPingButton();
        this.setupFullscreenToggle();
        console.log('Operator UI initialized');
    }

    setupWebSocket() {
        // Connect to control namespace
        this.socket = io('/control', {
            autoConnect: true,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000
        });

        // Connection event handlers
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus('Connected', 'connected');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus('Disconnected', 'disconnected');
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.updateConnectionStatus('Connection Error', 'error');
        });

        // FPS update handler (from show view)
        this.socket.on('SHOW_FPS_UPDATE', (data) => {
            console.log('FPS update:', data);
            // Forward to scene controls component if it exists
            const sceneControls = document.querySelector('scene-controls');
            if (sceneControls && sceneControls.updateFPS) {
                sceneControls.updateFPS(data.fps);
            }
        });
        
        // Listen for performance warnings
        document.addEventListener('performance-warning', (event) => {
            const { message, sceneId } = event.detail;
            console.warn('Performance warning:', message, sceneId);
            // Show toast notification if scene-controls component exists
            const sceneControls = document.querySelector('scene-controls');
            if (sceneControls && sceneControls.showToast) {
                sceneControls.showToast(`Performance: ${message}`, 'warning');
            }
        });

        // Handle server responses
        this.socket.on('status', (data) => {
            console.log('Server status:', data);
        });

        // Ping/Pong handlers
        this.socket.on('CONTROL_PONG', (data) => {
            const roundTripTime = Date.now() - data.timestamp;
            console.log(`Pong received! Round-trip time: ${roundTripTime}ms`);
            this.displayPingResult(roundTripTime);
        });
    }
    
    setupPingButton() {
        const testButton = document.getElementById('test-connection-btn');
        if (testButton) {
            testButton.addEventListener('click', () => {
                if (this.socket && this.socket.connected) {
                    this.sendPing();
                } else {
                    this.displayPingResult(null, 'Not connected');
                }
            });
        }
    }
    
    setupFullscreenToggle() {
        const toggleBtn = document.getElementById('toggle-fullscreen-btn');
        const preview = document.getElementById('show-preview');
        
        if (toggleBtn && preview) {
            toggleBtn.addEventListener('click', () => {
                if (preview.requestFullscreen) {
                    preview.requestFullscreen().catch(err => {
                        console.error('Error attempting to enable fullscreen:', err);
                    });
                } else if (preview.webkitRequestFullscreen) {
                    preview.webkitRequestFullscreen();
                } else if (preview.mozRequestFullScreen) {
                    preview.mozRequestFullScreen();
                } else if (preview.msRequestFullscreen) {
                    preview.msRequestFullscreen();
                }
            });
        }
    }
    
    sendPing() {
        const pingData = {
            timestamp: Date.now()
        };
        console.log('Sending ping...', pingData);
        this.socket.emit('CONTROL_PING', pingData);
    }
    
    displayPingResult(roundTripTime, error = null) {
        const pingResultElement = document.getElementById('ping-result');
        if (!pingResultElement) return;
        
        if (error) {
            pingResultElement.textContent = `Error: ${error}`;
            pingResultElement.className = 'ping-result error';
        } else if (roundTripTime !== null) {
            pingResultElement.textContent = `Round-trip time: ${roundTripTime}ms`;
            pingResultElement.className = 'ping-result success';
        }
        
        // Clear result after 5 seconds
        setTimeout(() => {
            if (pingResultElement) {
                pingResultElement.textContent = '';
                pingResultElement.className = 'ping-result';
            }
        }, 5000);
    }

    updateConnectionStatus(text, className) {
        if (this.connectionStatus) {
            this.connectionStatus.textContent = text;
            this.connectionStatus.className = className;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new OperatorUI();
});

