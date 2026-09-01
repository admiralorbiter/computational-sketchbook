/**
 * Scene Manager
 * Manages active scene lifecycle and coordinates with render loop
 */

import { TransitionManager } from './transitions.js';

export class SceneManager {
    constructor(renderer) {
        this.renderer = renderer;
        this.activeScene = null;
        this.sceneRegistry = new Map();
        this.canvas = renderer.canvas;
        this.ctx = renderer.ctx;
        
        // Transition state
        this.transitionState = null;
        this.oldScene = null;
        this.transitionStartTime = null;
        
        // Duration control
        this.sceneDuration = 0; // 0 = infinite
        this.sceneStartTime = null;
        this.durationTimeout = null;
        
        // Performance guardrails
        this.performanceHistory = [];
        this.lowFpsCount = 0;
        this.performanceDegraded = false;
        this.guardrailCheckInterval = 3000; // Check every 3 seconds
        this.lastGuardrailCheck = 0;
    }
    
    /**
     * Register a scene class
     * @param {string} sceneId - Unique identifier for the scene
     * @param {Class} SceneClass - Scene class constructor
     */
    registerScene(sceneId, SceneClass) {
        this.sceneRegistry.set(sceneId, SceneClass);
    }
    
    /**
     * Start a scene with optional transition
     * @param {string} sceneId - Scene identifier
     * @param {Object} params - Scene parameters (may include transitionIn, transitionOut, transitionMs)
     */
    startScene(sceneId, params = {}) {
        // Validate inputs
        if (!sceneId || typeof sceneId !== 'string') {
            console.error('SceneManager: Invalid sceneId provided');
            return false;
        }
        
        // Check if canvas and context are available
        if (!this.canvas || !this.ctx) {
            console.error('SceneManager: Canvas or context not available');
            const errorEvent = new CustomEvent('scene-error', {
                detail: { 
                    error: 'Canvas context not available',
                    sceneId: sceneId
                }
            });
            document.dispatchEvent(errorEvent);
            return false;
        }
        
        // Parse transition parameters
        const transitionIn = params.transitionIn || 'cut';
        const transitionMs = params.transitionMs || (typeof transitionIn === 'string' && transitionIn.includes(':') ? parseInt(transitionIn.split(':')[1]) || 0 : 0);
        const transitionConfig = TransitionManager.parseTransition(transitionIn);
        
        // Use transitionMs if provided, otherwise use parsed duration
        if (transitionMs > 0) {
            transitionConfig.duration = transitionMs;
        }
        
        // Store old scene for transition
        const hadOldScene = this.activeScene !== null;
        if (hadOldScene) {
            this.oldScene = this.activeScene;
            // Don't cleanup old scene yet if we're transitioning
            if (transitionConfig.duration > 0 && transitionConfig.type !== 'cut') {
                // Keep old scene for transition
            } else {
                this.oldScene.cleanup();
                this.oldScene = null;
            }
        }
        
        // Get scene class
        const SceneClass = this.sceneRegistry.get(sceneId);
        if (!SceneClass) {
            console.error(`SceneManager: Scene "${sceneId}" not found in registry`);
            const errorEvent = new CustomEvent('scene-error', {
                detail: { 
                    error: `Scene "${sceneId}" not found`,
                    sceneId: sceneId
                }
            });
            document.dispatchEvent(errorEvent);
            return false;
        }
        
        try {
            console.log(`Creating scene instance: ${sceneId}`, {
                canvas: this.canvas,
                hasCtx: !!this.ctx,
                canvasWidth: this.canvas.width,
                canvasHeight: this.canvas.height,
                transition: transitionConfig
            });
            
            // Create new scene instance
            const newScene = new SceneClass(this.canvas, this.ctx);
            
            // Remove transition params before initializing scene
            const sceneParams = { ...params };
            delete sceneParams.transitionIn;
            delete sceneParams.transitionOut;
            delete sceneParams.transitionMs;
            
            newScene.init(sceneParams);
            this.activeScene = newScene;
            
            // Setup transition if needed
            if (hadOldScene && transitionConfig.duration > 0 && transitionConfig.type !== 'cut') {
                this.transitionState = {
                    type: transitionConfig.type,
                    duration: transitionConfig.duration,
                    startTime: performance.now()
                };
                this.transitionStartTime = performance.now();
            } else {
                this.transitionState = null;
                this.oldScene = null;
            }
            
            // Setup duration control
            this.sceneDuration = params.duration || 0; // 0 = infinite
            this.sceneStartTime = performance.now();
            
            // Clear any existing duration timeout
            if (this.durationTimeout) {
                clearTimeout(this.durationTimeout);
                this.durationTimeout = null;
            }
            
            // Set duration timeout if duration > 0
            if (this.sceneDuration > 0) {
                this.durationTimeout = setTimeout(() => {
                    this.handleDurationExpired();
                }, this.sceneDuration);
            }
            
            console.log(`Started scene: ${sceneId}`, sceneParams, {
                isActive: this.activeScene.isActive,
                params: this.activeScene.params,
                transition: this.transitionState
            });
            
            // Emit success event
            const successEvent = new CustomEvent('scene-started', {
                detail: { sceneId: sceneId }
            });
            document.dispatchEvent(successEvent);
            
            return true;
        } catch (error) {
            console.error(`SceneManager: Error starting scene "${sceneId}":`, error);
            console.error('Error stack:', error.stack);
            this.activeScene = null;
            this.transitionState = null;
            this.oldScene = null;
            
            // Emit error event
            const errorEvent = new CustomEvent('scene-error', {
                detail: { 
                    error: error.message || 'Unknown error starting scene',
                    sceneId: sceneId,
                    stack: error.stack
                }
            });
            document.dispatchEvent(errorEvent);
            return false;
        }
    }
    
    /**
     * Update parameters of active scene
     * @param {Object} params - Parameter updates
     */
    updateParams(params) {
        if (this.activeScene) {
            this.activeScene.updateParams(params);
        }
    }
    
    /**
     * Stop the active scene
     */
    stopScene() {
        // Clear duration timeout
        if (this.durationTimeout) {
            clearTimeout(this.durationTimeout);
            this.durationTimeout = null;
        }
        
        if (this.activeScene) {
            this.activeScene.cleanup();
            this.activeScene = null;
        }
        if (this.oldScene) {
            this.oldScene.cleanup();
            this.oldScene = null;
        }
        this.transitionState = null;
        this.sceneDuration = 0;
        this.sceneStartTime = null;
        console.log('Scene stopped');
    }
    
    /**
     * Handle scene duration expiration
     */
    handleDurationExpired() {
        if (this.activeScene && this.sceneDuration > 0) {
            const elapsed = performance.now() - this.sceneStartTime;
            if (elapsed >= this.sceneDuration) {
                // Emit duration expired event
                const expiredEvent = new CustomEvent('scene-duration-expired', {
                    detail: {
                        sceneId: this.activeScene.constructor.name,
                        duration: this.sceneDuration
                    }
                });
                document.dispatchEvent(expiredEvent);
                
                // Stop the scene
                this.stopScene();
            }
        }
    }
    
    /**
     * Check if scene duration has expired (called during render loop)
     */
    checkDuration() {
        if (this.activeScene && this.sceneDuration > 0 && this.sceneStartTime) {
            const elapsed = performance.now() - this.sceneStartTime;
            if (elapsed >= this.sceneDuration) {
                this.handleDurationExpired();
            }
        }
    }
    
    /**
     * Check performance and apply guardrails if needed
     * @param {number} fps - Current FPS
     * @param {number} time - Current time
     */
    checkPerformance(fps, time) {
        // Track FPS history
        this.performanceHistory.push({ fps, time });
        
        // Keep only last 60 entries (about 1 minute at 60fps)
        if (this.performanceHistory.length > 60) {
            this.performanceHistory.shift();
        }
        
        // Check guardrails every N seconds
        if (time - this.lastGuardrailCheck >= this.guardrailCheckInterval) {
            this.lastGuardrailCheck = time;
            
            // Count low FPS frames in recent history
            const recentFrames = this.performanceHistory.filter(
                entry => time - entry.time <= 3000 // Last 3 seconds
            );
            
            const lowFpsFrames = recentFrames.filter(entry => entry.fps < 55).length;
            
            if (lowFpsFrames >= 3) {
                // FPS < 55 for 3 consecutive checks
                if (!this.performanceDegraded) {
                    this.applyPerformanceGuardrails();
                    this.performanceDegraded = true;
                }
            } else if (recentFrames.length > 0) {
                // FPS recovered
                const avgFps = recentFrames.reduce((sum, e) => sum + e.fps, 0) / recentFrames.length;
                if (avgFps >= 55 && this.performanceDegraded) {
                    // Could restore performance here if needed
                    this.performanceDegraded = false;
                }
            }
        }
    }
    
    /**
     * Apply performance guardrails to reduce complexity
     */
    applyPerformanceGuardrails() {
        if (!this.activeScene) return;
        
        console.warn('SceneManager: Performance guardrails activated - reducing complexity');
        
        // Emit performance warning event
        const warningEvent = new CustomEvent('performance-warning', {
            detail: {
                message: 'FPS dropped below 55 - reducing complexity',
                sceneId: this.activeScene.constructor.name
            }
        });
        document.dispatchEvent(warningEvent);
        
        // Try to reduce complexity in active scene
        if (typeof this.activeScene.reduceComplexity === 'function') {
            this.activeScene.reduceComplexity();
        } else {
            // Generic parameter reduction
            const params = this.activeScene.params || {};
            
            // Reduce density/particle counts
            if (params.density !== undefined) {
                params.density = Math.max(0.1, params.density * 0.5);
            }
            if (params.maxIter !== undefined) {
                params.maxIter = Math.max(10, Math.floor(params.maxIter * 0.5));
            }
            if (params.cellSize !== undefined) {
                params.cellSize = Math.min(20, params.cellSize * 1.5);
            }
            
            this.activeScene.updateParams(params);
        }
    }
    
    /**
     * Render callback for render loop
     * Called by renderer on each frame
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {number} time - Current time
     * @param {number} deltaTime - Delta time
     */
    render(ctx, time, deltaTime) {
        // Check duration expiration
        this.checkDuration();
        
        // Check performance (FPS from renderer)
        if (this.renderer && typeof this.renderer.getFPS === 'function') {
            const fps = this.renderer.getFPS();
            this.checkPerformance(fps, time);
        }
        // Handle transition
        if (this.transitionState && this.oldScene && this.activeScene) {
            const elapsed = time - this.transitionStartTime;
            const progress = Math.min(1.0, elapsed / this.transitionState.duration);
            const easedProgress = TransitionManager.ease(progress, 'easeInOut');
            
            const transitionFunc = TransitionManager.getTransition(this.transitionState.type);
            
            // Render with transition
            transitionFunc(
                ctx,
                () => this.oldScene.render(time, deltaTime),
                () => this.activeScene.render(time, deltaTime),
                easedProgress
            );
            
            // Clean up transition when complete
            if (progress >= 1.0) {
                this.oldScene.cleanup();
                this.oldScene = null;
                this.transitionState = null;
            }
        } else if (this.activeScene) {
            // Normal rendering
            try {
                if (!this.activeScene.isActive) {
                    console.warn('Scene exists but is not active');
                    return;
                }
                this.activeScene.render(time, deltaTime);
            } catch (error) {
                console.error('Error rendering scene:', error);
                console.error('Error stack:', error.stack);
                // Stop scene on error
                this.stopScene();
            }
        }
    }
    
    /**
     * Handle canvas resize
     */
    handleResize() {
        if (this.activeScene) {
            this.activeScene.resize();
        }
    }
    
    /**
     * Get active scene
     * @returns {MathVisuals|null} Active scene instance
     */
    getActiveScene() {
        return this.activeScene;
    }
    
    /**
     * Check if a scene is active
     * @returns {boolean} True if scene is active
     */
    isSceneActive() {
        return this.activeScene !== null && this.activeScene.isActive;
    }
}
