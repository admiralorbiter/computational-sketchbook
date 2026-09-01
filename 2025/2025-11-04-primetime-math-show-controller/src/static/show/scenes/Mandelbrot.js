/**
 * Mandelbrot Set fractal math visual preset
 * Computationally intensive - may need optimization for performance
 */

import { MathVisuals } from './MathVisuals.js';

export class Mandelbrot extends MathVisuals {
    constructor(canvas, ctx) {
        super(canvas, ctx);
        this.imageData = null;
        this.needsRedraw = true;
        this.maxIter = 100;
    }
    
    getDefaultParams() {
        const defaultColor = this.getThemeColor('accent_cyan', '#00E5FF');
        return {
            zoom: 1.0,          // Zoom level
            centerX: -0.5,      // Center X coordinate
            centerY: 0.0,      // Center Y coordinate
            maxIter: 100,       // Maximum iterations (lower = faster, less detail)
            hueCycle: 1.0,      // Color cycle speed
            color: defaultColor
        };
    }
    
    validateParam(paramName, value, defaultValue) {
        if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
            return defaultValue;
        }
        
        const numValue = typeof value === 'string' ? parseFloat(value) : value;
        
        switch (paramName) {
            case 'zoom':
                // Zoom: 0.1-100
                if (typeof numValue !== 'number' || numValue < 0.1 || numValue > 100) {
                    return Math.max(0.1, Math.min(100, numValue));
                }
                return numValue;
                
            case 'centerX':
            case 'centerY':
                // Center coordinates: -2 to 2
                if (typeof numValue !== 'number') {
                    return defaultValue;
                }
                return Math.max(-2, Math.min(2, numValue));
                
            case 'maxIter':
                // Max iterations: 10-500 (performance sensitive)
                if (typeof numValue !== 'number' || numValue < 10 || numValue > 500) {
                    return Math.max(10, Math.min(500, numValue));
                }
                return Math.floor(numValue);
                
            case 'hueCycle':
                // Hue cycle: 0-2
                if (typeof numValue !== 'number' || numValue < 0 || numValue > 2) {
                    return Math.max(0, Math.min(2, numValue));
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
    
    mandelbrotIter(cx, cy, maxIter) {
        let x = 0;
        let y = 0;
        let x2 = 0;
        let y2 = 0;
        let iter = 0;
        
        while (x2 + y2 <= 4 && iter < maxIter) {
            y = 2 * x * y + cy;
            x = x2 - y2 + cx;
            x2 = x * x;
            y2 = y * y;
            iter++;
        }
        
        return iter;
    }
    
    generateMandelbrot() {
        const { zoom, centerX, centerY, maxIter, hueCycle } = this.params;
        const t = this.currentTime / 10000 * hueCycle;
        
        this.imageData = this.ctx.createImageData(this.width, this.height);
        const data = this.imageData.data;
        
        const scale = 4.0 / zoom;
        const offsetX = centerX - scale / 2;
        const offsetY = centerY - scale / 2;
        
        // Process in chunks to avoid blocking (simplified - could be optimized)
        for (let py = 0; py < this.height; py++) {
            for (let px = 0; px < this.width; px++) {
                const cx = offsetX + (px / this.width) * scale;
                const cy = offsetY + (py / this.height) * scale;
                
                const iter = this.mandelbrotIter(cx, cy, maxIter);
                
                const index = (py * this.width + px) * 4;
                
                if (iter === maxIter) {
                    // Inside set - black
                    data[index] = 0;
                    data[index + 1] = 0;
                    data[index + 2] = 0;
                    data[index + 3] = 255;
                } else {
                    // Outside set - color based on iterations
                    const hue = (iter / maxIter + t) % 1;
                    const [r, g, b] = this.hsvToRgb(hue * 360, 1, 1);
                    data[index] = r;
                    data[index + 1] = g;
                    data[index + 2] = b;
                    data[index + 3] = 255;
                }
            }
        }
        
        this.needsRedraw = false;
    }
    
    hsvToRgb(h, s, v) {
        const c = v * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = v - c;
        
        let r, g, b;
        
        if (h < 60) {
            r = c; g = x; b = 0;
        } else if (h < 120) {
            r = x; g = c; b = 0;
        } else if (h < 180) {
            r = 0; g = c; b = x;
        } else if (h < 240) {
            r = 0; g = x; b = c;
        } else if (h < 300) {
            r = x; g = 0; b = c;
        } else {
            r = c; g = 0; b = x;
        }
        
        return [
            Math.floor((r + m) * 255),
            Math.floor((g + m) * 255),
            Math.floor((b + m) * 255)
        ];
    }
    
    init(params = {}) {
        super.init(params);
        this.maxIter = this.params.maxIter;
        this.needsRedraw = true;
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
            
            // Regenerate if needed or if zoom/center changed
            if (this.needsRedraw || this.params.maxIter !== this.maxIter) {
                this.generateMandelbrot();
                this.maxIter = this.params.maxIter;
            }
            
            // Draw the fractal
            if (this.imageData) {
                ctx.putImageData(this.imageData, 0, 0);
            }
        } catch (error) {
            console.error('Mandelbrot render error:', error);
        }
    }
    
    onParamsChanged() {
        // Mark for redraw when params change
        this.needsRedraw = true;
    }
    
    onCleanup() {
        this.imageData = null;
        this.needsRedraw = true;
    }
    
    onResize() {
        if (this.isActive) {
            this.needsRedraw = true;
        }
    }
}

