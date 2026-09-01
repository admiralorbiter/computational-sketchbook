/**
 * Lissajous curves math visual preset
 * Parametric curves: x = A*sin(a*t + delta), y = B*sin(b*t)
 */

import { MathVisuals } from './MathVisuals.js';

export class Lissajous extends MathVisuals {
    constructor(canvas, ctx) {
        super(canvas, ctx);
        this.trail = [];
        this.maxTrailLength = 500;
    }
    
    getDefaultParams() {
        // Use theme color for default
        const defaultColor = this.getThemeColor('accent_green', '#39FF14');
        return {
            a: 3,           // Frequency ratio for x-axis (1-10)
            b: 2,           // Frequency ratio for y-axis (1-10)
            delta: 0,       // Phase shift in radians (0-2π)
            speed: 1,       // Animation speed multiplier (0.1-3)
            amplitude: 0.4, // Amplitude (as fraction of canvas size)
            lineWidth: 2,
            trailAlpha: 0.05, // Alpha for trail fade
            color: defaultColor  // Use theme color
        };
    }
    
    /**
     * Validate and sanitize a parameter value
     * @param {string} paramName - Name of the parameter
     * @param {any} value - Value to validate
     * @param {any} defaultValue - Default value to use if invalid
     * @returns {any} Validated value
     */
    validateParam(paramName, value, defaultValue) {
        // Handle null, undefined, or NaN
        if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
            console.warn(`Lissajous: Invalid ${paramName} value (${value}), using default: ${defaultValue}`);
            return defaultValue;
        }
        
        // Convert to number if string
        const numValue = typeof value === 'string' ? parseFloat(value) : value;
        
        // Validate ranges based on parameter name
        switch (paramName) {
            case 'a':
            case 'b':
                // Frequency ratios: 1-10
                if (typeof numValue !== 'number' || numValue < 1 || numValue > 10) {
                    console.warn(`Lissajous: ${paramName} out of range (${numValue}), clamping to valid range`);
                    return Math.max(1, Math.min(10, numValue));
                }
                return numValue;
                
            case 'delta':
                // Phase shift: 0-2π
                if (typeof numValue !== 'number' || numValue < 0 || numValue > 2 * Math.PI) {
                    console.warn(`Lissajous: ${paramName} out of range (${numValue}), clamping to valid range`);
                    return Math.max(0, Math.min(2 * Math.PI, numValue));
                }
                return numValue;
                
            case 'speed':
                // Speed: 0.1-3
                if (typeof numValue !== 'number' || numValue < 0.1 || numValue > 3) {
                    console.warn(`Lissajous: ${paramName} out of range (${numValue}), clamping to valid range`);
                    return Math.max(0.1, Math.min(3, numValue));
                }
                return numValue;
                
            case 'amplitude':
                // Amplitude: 0.1-0.9
                if (typeof numValue !== 'number' || numValue < 0.1 || numValue > 0.9) {
                    console.warn(`Lissajous: ${paramName} out of range (${numValue}), clamping to valid range`);
                    return Math.max(0.1, Math.min(0.9, numValue));
                }
                return numValue;
                
            case 'lineWidth':
                // Line width: 1-10
                if (typeof numValue !== 'number' || numValue < 1 || numValue > 10) {
                    console.warn(`Lissajous: ${paramName} out of range (${numValue}), clamping to valid range`);
                    return Math.max(1, Math.min(10, numValue));
                }
                return numValue;
                
            case 'trailAlpha':
                // Trail alpha: 0.01-0.2
                if (typeof numValue !== 'number' || numValue < 0.01 || numValue > 0.2) {
                    console.warn(`Lissajous: ${paramName} out of range (${numValue}), clamping to valid range`);
                    return Math.max(0.01, Math.min(0.2, numValue));
                }
                return numValue;
                
            case 'color':
                // Color: must be valid CSS color string
                if (typeof value !== 'string' || !value.match(/^#[0-9A-Fa-f]{6}$|^[a-zA-Z]+$/)) {
                    console.warn(`Lissajous: ${paramName} invalid (${value}), using default`);
                    return defaultValue;
                }
                return value;
                
            default:
                // For unknown parameters, return as-is or default
                return value !== undefined ? value : defaultValue;
        }
    }
    
    /**
     * Validate all parameters
     * @param {Object} params - Parameters to validate
     * @returns {Object} Validated parameters
     */
    validateParams(params) {
        const defaults = this.getDefaultParams();
        const validated = {};
        
        for (const [key, value] of Object.entries(params)) {
            if (defaults.hasOwnProperty(key)) {
                validated[key] = this.validateParam(key, value, defaults[key]);
            } else {
                // Unknown parameter, log warning but keep it
                console.warn(`Lissajous: Unknown parameter "${key}", ignoring`);
            }
        }
        
        return validated;
    }
    
    render(time, deltaTime) {
        if (!this.isActive) {
            console.warn('Lissajous render called but scene is not active');
            return;
        }
        
        try {
            super.render(time, deltaTime);
            
            const ctx = this.ctx;
            if (!ctx) {
                console.error('Lissajous: No canvas context available');
                return;
            }
            
            const { a, b, delta, speed, amplitude, lineWidth, trailAlpha, color } = this.params;
            
            // Calculate animation time
            const t = (this.currentTime * speed) / 1000; // Convert to seconds
            
            // Calculate position
            const centerX = this.width / 2;
            const centerY = this.height / 2;
            const radius = Math.min(this.width, this.height) * amplitude;
            
            const x = centerX + radius * Math.sin(a * t + delta);
            const y = centerY + radius * Math.sin(b * t);
            
            // Add to trail
            this.trail.push({ x, y, alpha: 1.0 });
            
            // Limit trail length
            if (this.trail.length > this.maxTrailLength) {
                this.trail.shift();
            }
            
            // Fade trail
            this.trail.forEach(point => {
                point.alpha = Math.max(0, point.alpha - trailAlpha);
            });
            
            // Draw trail
            ctx.strokeStyle = color;
            ctx.lineWidth = lineWidth;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            
            if (this.trail.length > 1) {
                for (let i = 1; i < this.trail.length; i++) {
                    const prev = this.trail[i - 1];
                    const curr = this.trail[i];
                    
                    // Skip if alpha is too low
                    if (curr.alpha < 0.01) continue;
                    
                    ctx.globalAlpha = curr.alpha;
                    ctx.beginPath();
                    ctx.moveTo(prev.x, prev.y);
                    ctx.lineTo(curr.x, curr.y);
                    ctx.stroke();
                }
            }
            
            // Draw current point
            ctx.globalAlpha = 1.0;
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, y, lineWidth * 2, 0, Math.PI * 2);
            ctx.fill();
            
            // Reset alpha
            ctx.globalAlpha = 1.0;
        } catch (error) {
            console.error('Lissajous render error:', error);
            console.error('Error stack:', error.stack);
        }
    }
    
    onCleanup() {
        // Clear trail
        this.trail = [];
    }
}
