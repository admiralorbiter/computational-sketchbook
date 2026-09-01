/**
 * Scene transition utilities
 * Provides cut, fade, and crossfade transitions between scenes
 */

export class TransitionManager {
    /**
     * Apply cut transition (instant switch)
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {Function} renderOldScene - Function to render old scene
     * @param {Function} renderNewScene - Function to render new scene
     * @param {number} progress - Transition progress (0-1)
     */
    static cut(ctx, renderOldScene, renderNewScene, progress) {
        // Cut is instant - just render new scene
        if (progress >= 1.0) {
            renderNewScene();
        } else {
            renderOldScene();
        }
    }
    
    /**
     * Apply fade transition
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {Function} renderOldScene - Function to render old scene
     * @param {Function} renderNewScene - Function to render new scene
     * @param {number} progress - Transition progress (0-1)
     */
    static fade(ctx, renderOldScene, renderNewScene, progress) {
        // Fade out old scene, fade in new scene
        if (progress < 0.5) {
            // Fade out old scene
            ctx.save();
            ctx.globalAlpha = 1.0 - (progress * 2);
            renderOldScene();
            ctx.restore();
        } else {
            // Fade in new scene
            ctx.save();
            ctx.globalAlpha = (progress - 0.5) * 2;
            renderNewScene();
            ctx.restore();
        }
    }
    
    /**
     * Apply crossfade transition
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {Function} renderOldScene - Function to render old scene
     * @param {Function} renderNewScene - Function to render new scene
     * @param {number} progress - Transition progress (0-1)
     */
    static crossfade(ctx, renderOldScene, renderNewScene, progress) {
        // Both scenes visible, crossfading
        ctx.save();
        
        // Render old scene fading out
        ctx.globalAlpha = 1.0 - progress;
        renderOldScene();
        
        // Render new scene fading in
        ctx.globalAlpha = progress;
        renderNewScene();
        
        ctx.restore();
    }
    
    /**
     * Get transition function by name
     * @param {string} transitionType - 'cut', 'fade', or 'crossfade'
     * @returns {Function} Transition function
     */
    static getTransition(transitionType) {
        switch (transitionType) {
            case 'cut':
                return TransitionManager.cut;
            case 'fade':
                return TransitionManager.fade;
            case 'crossfade':
            case 'cross':
                return TransitionManager.crossfade;
            default:
                return TransitionManager.cut; // Default to cut
        }
    }
    
    /**
     * Parse transition string (e.g., "fade:500" or "crossfade:300")
     * @param {string} transitionStr - Transition string
     * @returns {Object} { type: string, duration: number }
     */
    static parseTransition(transitionStr) {
        if (!transitionStr || typeof transitionStr !== 'string') {
            return { type: 'cut', duration: 0 };
        }
        
        const parts = transitionStr.split(':');
        const type = parts[0] || 'cut';
        const duration = parts.length > 1 ? parseInt(parts[1], 10) || 0 : 0;
        
        return { type, duration };
    }
    
    /**
     * Easing function for smooth transitions
     * @param {number} t - Progress (0-1)
     * @param {string} easing - Easing type ('linear', 'easeInOut', 'easeOut')
     * @returns {number} Eased progress (0-1)
     */
    static ease(t, easing = 'easeInOut') {
        switch (easing) {
            case 'linear':
                return t;
            case 'easeInOut':
                return t < 0.5 
                    ? 2 * t * t 
                    : -1 + (4 - 2 * t) * t;
            case 'easeOut':
                return t * (2 - t);
            case 'easeIn':
                return t * t;
            default:
                return TransitionManager.ease(t, 'easeInOut');
        }
    }
}

