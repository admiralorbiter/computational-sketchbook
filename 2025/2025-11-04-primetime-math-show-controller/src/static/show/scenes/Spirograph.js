/**
 * Spirograph/Epicycles math visual preset
 * Multiple circles with compound rotation creating mesmerizing patterns
 */

import { MathVisuals } from './MathVisuals.js';

export class Spirograph extends MathVisuals {
    constructor(canvas, ctx) {
        super(canvas, ctx);
        this.trail = [];
        this.maxTrailLength = 800;
        this.angles = []; // Track angles for each circle
    }
    
    getDefaultParams() {
        const defaultColor = this.getThemeColor('accent_green', '#39FF14');
        return {
            radii: [80, 50, 30],  // Array of radii for nested circles
            speed: 1.0,            // Animation speed multiplier
            trace: true,           // Whether to draw trail
            lineWidth: 2,
            color: defaultColor
        };
    }
    
    validateParam(paramName, value, defaultValue) {
        if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
            return defaultValue;
        }
        
        switch (paramName) {
            case 'radii':
                // Must be array of positive numbers
                if (!Array.isArray(value)) {
                    return defaultValue;
                }
                return value
                    .map(r => typeof r === 'number' ? Math.max(10, Math.min(200, r)) : 10)
                    .filter(r => r > 0)
                    .slice(0, 5); // Limit to 5 circles max
                
            case 'speed':
                // Speed: 0.1-3
                const numValue = typeof value === 'string' ? parseFloat(value) : value;
                if (typeof numValue !== 'number' || numValue < 0.1 || numValue > 3) {
                    return Math.max(0.1, Math.min(3, numValue));
                }
                return numValue;
                
            case 'trace':
                // Boolean
                return typeof value === 'boolean' ? value : defaultValue;
                
            case 'lineWidth':
                const numLineWidth = typeof value === 'string' ? parseFloat(value) : value;
                if (typeof numLineWidth !== 'number' || numLineWidth < 1 || numLineWidth > 10) {
                    return Math.max(1, Math.min(10, numLineWidth));
                }
                return numLineWidth;
                
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
            
            const { radii, speed, trace, lineWidth, color } = this.params;
            
            // Initialize angles array if needed
            if (this.angles.length !== radii.length) {
                this.angles = new Array(radii.length).fill(0);
            }
            
            // Calculate animation time
            const t = (this.currentTime * speed) / 1000;
            
            // Calculate center
            const centerX = this.width / 2;
            const centerY = this.height / 2;
            
            // Calculate compound rotation for nested circles
            let currentX = centerX;
            let currentY = centerY;
            let currentAngle = 0;
            
            // Draw circles and calculate final point
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.globalAlpha = 0.3;
            
            for (let i = 0; i < radii.length; i++) {
                const radius = radii[i];
                // Each circle rotates at different speed (faster for inner circles)
                const rotationSpeed = (i + 1) * 0.5;
                this.angles[i] = t * rotationSpeed;
                currentAngle += this.angles[i];
                
                // Draw circle outline
                ctx.beginPath();
                ctx.arc(currentX, currentY, radius, 0, Math.PI * 2);
                ctx.stroke();
                
                // Calculate next center point
                currentX += radius * Math.cos(currentAngle);
                currentY += radius * Math.sin(currentAngle);
            }
            
            // Final point is the drawing position
            const finalX = currentX;
            const finalY = currentY;
            
            // Add to trail if tracing
            if (trace) {
                this.trail.push({ x: finalX, y: finalY, alpha: 1.0 });
                
                // Limit trail length
                if (this.trail.length > this.maxTrailLength) {
                    this.trail.shift();
                }
                
                // Fade trail
                this.trail.forEach(point => {
                    point.alpha = Math.max(0, point.alpha - 0.003);
                });
                
                // Draw trail
                ctx.globalAlpha = 1.0;
                ctx.lineWidth = lineWidth;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                
                if (this.trail.length > 1) {
                    for (let i = 1; i < this.trail.length; i++) {
                        const prev = this.trail[i - 1];
                        const curr = this.trail[i];
                        
                        if (curr.alpha < 0.01) continue;
                        
                        ctx.globalAlpha = curr.alpha;
                        ctx.beginPath();
                        ctx.moveTo(prev.x, prev.y);
                        ctx.lineTo(curr.x, curr.y);
                        ctx.stroke();
                    }
                }
            }
            
            // Draw current point
            ctx.globalAlpha = 1.0;
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(finalX, finalY, lineWidth * 2, 0, Math.PI * 2);
            ctx.fill();
            
            // Reset alpha
            ctx.globalAlpha = 1.0;
        } catch (error) {
            console.error('Spirograph render error:', error);
        }
    }
    
    onCleanup() {
        this.trail = [];
        this.angles = [];
    }
}

