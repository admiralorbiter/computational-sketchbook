/**
 * Base class for math visual presets
 * All math scenes should extend this class
 */

import { themeManager } from '../utils/theme.js';

export class MathVisuals {
    constructor(canvas, ctx) {
        this.canvas = canvas;
        this.ctx = ctx;
        this.width = canvas.width;
        this.height = canvas.height;
        this.params = {};
        this.isActive = false;
        this.startTime = null;
        this.currentTime = 0;
        this.theme = themeManager;
    }
    
    /**
     * Get theme color
     * @param {string} colorKey - Color key from theme
     * @param {string} fallback - Fallback color
     * @returns {string} Color value
     */
    getThemeColor(colorKey, fallback = '#FFFFFF') {
        return this.theme.getColor(colorKey, fallback);
    }
    
    /**
     * Get all theme colors
     * @returns {Object} Colors object
     */
    getThemeColors() {
        return this.theme.getColors();
    }
    
    /**
     * Reduce complexity for performance guardrails
     * Override in subclasses to implement specific reduction strategies
     */
    reduceComplexity() {
        // Default implementation - reduce common performance-sensitive parameters
        const params = this.params || {};
        
        // Reduce density/particle counts by 50%
        if (params.density !== undefined) {
            this.updateParams({ density: Math.max(0.1, params.density * 0.5) });
        }
        
        // Reduce max iterations by 50%
        if (params.maxIter !== undefined) {
            this.updateParams({ maxIter: Math.max(10, Math.floor(params.maxIter * 0.5)) });
        }
        
        // Increase cell size (fewer cells)
        if (params.cellSize !== undefined) {
            this.updateParams({ cellSize: Math.min(20, params.cellSize * 1.5) });
        }
        
        // Disable glow effects
        if (params.petalGlow !== undefined) {
            this.updateParams({ petalGlow: 0 });
        }
        
        console.log('MathVisuals: Complexity reduced for performance');
    }
    
    /**
     * Initialize the scene
     * Called when scene is started
     * @param {Object} params - Scene parameters
     */
    init(params = {}) {
        // If scene has validateParams method, use it
        if (typeof this.validateParams === 'function') {
            const validated = this.validateParams(params);
            this.params = { ...this.getDefaultParams(), ...validated };
        } else {
            // Otherwise, merge directly
            this.params = { ...this.getDefaultParams(), ...params };
        }
        this.isActive = true;
        this.startTime = null; // Will be set on first render
        this.resize();
    }
    
    /**
     * Get default parameters for this scene
     * Override in subclasses
     * @returns {Object} Default parameters
     */
    getDefaultParams() {
        return {};
    }
    
    /**
     * Update scene parameters
     * @param {Object} newParams - New parameter values
     */
    updateParams(newParams) {
        if (!newParams || typeof newParams !== 'object') {
            console.warn('MathVisuals: Invalid parameters provided to updateParams');
            return;
        }
        
        // If scene has validateParams method, use it
        if (typeof this.validateParams === 'function') {
            const validated = this.validateParams(newParams);
            this.params = { ...this.params, ...validated };
        } else {
            // Otherwise, merge directly
            this.params = { ...this.params, ...newParams };
        }
        
        this.onParamsChanged();
    }
    
    /**
     * Called when parameters change
     * Override in subclasses to react to parameter changes
     */
    onParamsChanged() {
        // Override in subclasses
    }
    
    /**
     * Render the scene
     * Base class handles time tracking, subclasses override to implement rendering
     * @param {number} time - Current time in milliseconds (since page load)
     * @param {number} deltaTime - Time since last frame in milliseconds
     */
    render(time, deltaTime) {
        if (!this.isActive) return;
        
        // Set start time on first render
        if (this.startTime === null) {
            this.startTime = time;
        }
        
        this.currentTime = time - this.startTime;
        
        // Base class just handles time tracking
        // Subclasses override this method to implement actual rendering
    }
    
    /**
     * Handle canvas resize
     */
    resize() {
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        this.onResize();
    }
    
    /**
     * Called when canvas is resized
     * Override in subclasses to react to resize
     */
    onResize() {
        // Override in subclasses
    }
    
    /**
     * Stop and cleanup the scene
     */
    cleanup() {
        this.isActive = false;
        this.onCleanup();
    }
    
    /**
     * Called during cleanup
     * Override in subclasses to perform cleanup
     */
    onCleanup() {
        // Override in subclasses
    }
}
