/**
 * Polar Roses math visual preset
 * Polar equation: r = sin(k*θ)
 * Creates beautiful rose patterns with k petals
 */

import { MathVisuals } from './MathVisuals.js';

export class PolarRoses extends MathVisuals {
    constructor(canvas, ctx) {
        super(canvas, ctx);
        this.points = [];
        this.maxPoints = 1000;
    }
    
    getDefaultParams() {
        const defaultColor = this.getThemeColor('accent_cyan', '#00E5FF');
        return {
            k: 3.0,          // Number of petals (k=2,3,5,7 produce nice patterns)
            rotation: 0.0,   // Rotation offset in radians
            petalGlow: 0.7,  // Glow effect intensity (0-1)
            speed: 1.0,      // Animation speed multiplier
            lineWidth: 2,
            color: defaultColor
        };
    }
    
    validateParam(paramName, value, defaultValue) {
        if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
            return defaultValue;
        }
        
        const numValue = typeof value === 'string' ? parseFloat(value) : value;
        
        switch (paramName) {
            case 'k':
                // k can be any positive number, but integers produce best results
                if (typeof numValue !== 'number' || numValue <= 0) {
                    return defaultValue;
                }
                return numValue;
                
            case 'rotation':
                // Rotation: 0-2π
                if (typeof numValue !== 'number') {
                    return defaultValue;
                }
                return numValue % (2 * Math.PI);
                
            case 'petalGlow':
                // Glow: 0-1
                if (typeof numValue !== 'number' || numValue < 0 || numValue > 1) {
                    return Math.max(0, Math.min(1, numValue));
                }
                return numValue;
                
            case 'speed':
                // Speed: 0.1-3
                if (typeof numValue !== 'number' || numValue < 0.1 || numValue > 3) {
                    return Math.max(0.1, Math.min(3, numValue));
                }
                return numValue;
                
            case 'lineWidth':
                // Line width: 1-10
                if (typeof numValue !== 'number' || numValue < 1 || numValue > 10) {
                    return Math.max(1, Math.min(10, numValue));
                }
                return numValue;
                
            default:
                return value !== undefined ? value : defaultValue;
        }
    }
    
    validateParams(params) {
        const defaults = this.getDefaultParams();
        const validated = {};
        
        for (const [key, value] of Object.entries(params)) {
            if (defaults.hasOwnProperty(key)) {
                validated[key] = this.validateParam(key, value, defaults[key]);
            }
        }
        
        return validated;
    }
    
    render(time, deltaTime) {
        if (!this.isActive) {
            return;
        }
        
        try {
            super.render(time, deltaTime);
            
            const ctx = this.ctx;
            if (!ctx) {
                return;
            }
            
            const { k, rotation, petalGlow, speed, lineWidth, color } = this.params;
            
            // Calculate animation time
            const t = (this.currentTime * speed) / 1000;
            
            // Calculate center
            const centerX = this.width / 2;
            const centerY = this.height / 2;
            const maxRadius = Math.min(this.width, this.height) * 0.4;
            
            // Generate points for polar rose
            const theta = t * 0.5 + rotation; // Slow rotation
            const r = Math.sin(k * theta) * maxRadius;
            
            const x = centerX + r * Math.cos(theta);
            const y = centerY + r * Math.sin(theta);
            
            // Add to points array
            this.points.push({ x, y, theta, alpha: 1.0 });
            
            // Limit points array
            if (this.points.length > this.maxPoints) {
                this.points.shift();
            }
            
            // Fade older points
            this.points.forEach(point => {
                point.alpha = Math.max(0, point.alpha - 0.01);
            });
            
            // Draw the rose
            ctx.strokeStyle = color;
            ctx.lineWidth = lineWidth;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            
            if (this.points.length > 1) {
                for (let i = 1; i < this.points.length; i++) {
                    const prev = this.points[i - 1];
                    const curr = this.points[i];
                    
                    if (curr.alpha < 0.01) continue;
                    
                    // Apply glow effect
                    ctx.globalAlpha = curr.alpha * (0.5 + petalGlow * 0.5);
                    ctx.beginPath();
                    ctx.moveTo(prev.x, prev.y);
                    ctx.lineTo(curr.x, curr.y);
                    ctx.stroke();
                }
            }
            
            // Draw current point with glow
            ctx.globalAlpha = 1.0;
            ctx.fillStyle = color;
            const glowRadius = lineWidth * (1 + petalGlow);
            ctx.beginPath();
            ctx.arc(x, y, glowRadius, 0, Math.PI * 2);
            ctx.fill();
            
            // Reset alpha
            ctx.globalAlpha = 1.0;
        } catch (error) {
            console.error('PolarRoses render error:', error);
        }
    }
    
    onCleanup() {
        this.points = [];
    }
}

