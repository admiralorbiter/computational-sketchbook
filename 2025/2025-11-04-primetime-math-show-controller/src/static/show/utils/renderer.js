/**
 * Renderer utility for Show View
 * Handles canvas setup, FPS tracking, and render loop
 */

export class Renderer {
    constructor(canvasElement) {
        if (!canvasElement) {
            throw new Error('Renderer: Canvas element is required');
        }
        
        this.canvas = canvasElement;
        
        // Try to get 2D context with error handling
        try {
            this.ctx = this.canvas.getContext('2d');
            if (!this.ctx) {
                throw new Error('Failed to get 2D rendering context');
            }
        } catch (error) {
            console.error('Renderer: Failed to initialize canvas context:', error);
            this.ctx = null;
            // Emit error event for ShowView to handle
            const errorEvent = new CustomEvent('renderer-error', {
                detail: { 
                    error: error.message || 'Canvas context initialization failed',
                    type: 'context_init'
                }
            });
            document.dispatchEvent(errorEvent);
            throw error;
        }
        
        this.animationFrameId = null;
        this.isRunning = false;
        
        // FPS tracking
        this.lastFrameTime = performance.now();
        this.frameCount = 0;
        this.fps = 0;
        this.fpsUpdateInterval = 1000; // Update FPS every second
        this.lastFpsUpdateTime = performance.now();
        this.frameTimeHistory = [];
        
        // Resize handler
        try {
            this.handleResize();
            window.addEventListener('resize', () => this.handleResize());
        } catch (error) {
            console.error('Renderer: Error during initialization:', error);
        }
    }
    
    handleResize() {
        if (!this.canvas || !this.ctx) {
            console.warn('Renderer: Cannot resize - canvas or context not available');
            return;
        }
        
        try {
            // Set canvas to full window size
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
            
            // Clear canvas
            this.ctx.fillStyle = '#000';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        } catch (error) {
            console.error('Renderer: Error during resize:', error);
        }
    }
    
    startRenderLoop(renderCallback) {
        if (this.isRunning) {
            return;
        }
        
        if (!this.ctx) {
            console.error('Renderer: Cannot start render loop - context not available');
            const errorEvent = new CustomEvent('renderer-error', {
                detail: { 
                    error: 'Canvas context not available',
                    type: 'render_loop_start'
                }
            });
            document.dispatchEvent(errorEvent);
            return;
        }
        
        this.isRunning = true;
        this.lastFrameTime = performance.now();
        this.lastFpsUpdateTime = performance.now();
        
        const loop = (currentTime) => {
            if (!this.isRunning) {
                return;
            }
            
            // Check if context is still valid (handles context loss)
            if (!this.ctx) {
                console.error('Renderer: Canvas context lost during render loop');
                this.stopRenderLoop();
                const errorEvent = new CustomEvent('renderer-error', {
                    detail: { 
                        error: 'Canvas context lost',
                        type: 'context_lost'
                    }
                });
                document.dispatchEvent(errorEvent);
                return;
            }
            
            try {
                // Calculate delta time
                const deltaTime = currentTime - this.lastFrameTime;
                this.lastFrameTime = currentTime;
                
                // Track frame time for FPS calculation
                this.frameTimeHistory.push(deltaTime);
                if (this.frameTimeHistory.length > 60) {
                    this.frameTimeHistory.shift(); // Keep last 60 frames
                }
                
                // Update FPS every second
                if (currentTime - this.lastFpsUpdateTime >= this.fpsUpdateInterval) {
                    this.updateFPS();
                    this.lastFpsUpdateTime = currentTime;
                }
                
                // Clear canvas
                this.ctx.fillStyle = '#000';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Call render callback with context and time
                if (renderCallback) {
                    renderCallback(this.ctx, currentTime, deltaTime);
                }
                
                // Draw FPS counter
                this.drawFPSCounter();
            } catch (error) {
                console.error('Renderer: Error in render loop:', error);
                // Don't stop the loop on single-frame errors, but log them
            }
            
            // Continue loop
            this.animationFrameId = requestAnimationFrame(loop);
        };
        
        this.animationFrameId = requestAnimationFrame(loop);
    }
    
    stopRenderLoop() {
        this.isRunning = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }
    
    updateFPS() {
        if (this.frameTimeHistory.length === 0) {
            this.fps = 0;
            return;
        }
        
        // Calculate average frame time
        const avgFrameTime = this.frameTimeHistory.reduce((a, b) => a + b, 0) / this.frameTimeHistory.length;
        this.fps = Math.round(1000 / avgFrameTime);
    }
    
    getFPS() {
        return this.fps;
    }
    
    drawFPSCounter() {
        const fpsText = `FPS: ${this.fps}`;
        const fpsElement = document.getElementById('fps-counter');
        if (fpsElement) {
            fpsElement.textContent = fpsText;
            // Color code based on performance
            if (this.fps >= 55) {
                fpsElement.style.color = '#39FF14'; // Green
                fpsElement.style.borderColor = '#39FF14';
            } else if (this.fps >= 30) {
                fpsElement.style.color = '#FFD700'; // Yellow
                fpsElement.style.borderColor = '#FFD700';
            } else {
                fpsElement.style.color = '#FF4444'; // Red
                fpsElement.style.borderColor = '#FF4444';
            }
        }
    }
    
    clear() {
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
}
