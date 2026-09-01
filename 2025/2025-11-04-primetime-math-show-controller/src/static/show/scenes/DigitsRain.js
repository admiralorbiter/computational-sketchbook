/**
 * Digits Rain math visual preset
 * Matrix-style falling text with mathematical constants (π, e, primes)
 */

import { MathVisuals } from './MathVisuals.js';
import { getFirstNPrimes } from '../utils/primes.js';

export class DigitsRain extends MathVisuals {
    constructor(canvas, ctx) {
        super(canvas, ctx);
        this.columns = [];
        this.charsets = {
            pi: this.generatePiDigits(1000),
            e: this.generateEDigits(1000),
            primes: getFirstNPrimes(1000).map(p => p.toString())
        };
    }
    
    generatePiDigits(count) {
        // Approximation of π digits (simplified - in production use more accurate calculation)
        const pi = Math.PI.toString().replace('.', '');
        const digits = [];
        for (let i = 0; i < count; i++) {
            digits.push(pi[i % pi.length]);
        }
        return digits;
    }
    
    generateEDigits(count) {
        // Approximation of e digits
        const e = Math.E.toString().replace('.', '');
        const digits = [];
        for (let i = 0; i < count; i++) {
            digits.push(e[i % e.length]);
        }
        return digits;
    }
    
    getDefaultParams() {
        const defaultColor = this.getThemeColor('accent_green', '#39FF14');
        return {
            charset: 'pi',      // 'pi', 'e', or 'primes'
            density: 0.5,        // Column density (0-1)
            speed: 1.0,          // Animation speed
            fontSize: 16,        // Font size in pixels
            color: defaultColor
        };
    }
    
    validateParam(paramName, value, defaultValue) {
        if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
            return defaultValue;
        }
        
        const numValue = typeof value === 'string' ? parseFloat(value) : value;
        
        switch (paramName) {
            case 'charset':
                // Must be 'pi', 'e', or 'primes'
                if (['pi', 'e', 'primes'].includes(value)) {
                    return value;
                }
                return defaultValue;
                
            case 'density':
                // Density: 0-1
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
                
            case 'fontSize':
                // Font size: 8-48
                if (typeof numValue !== 'number' || numValue < 8 || numValue > 48) {
                    return Math.max(8, Math.min(48, numValue));
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
    
    init(params = {}) {
        super.init(params);
        
        // Initialize columns based on density
        const { density, fontSize } = this.params;
        const columnWidth = fontSize * 1.2;
        const numColumns = Math.floor(this.width / columnWidth * density);
        
        this.columns = [];
        const charset = this.charsets[this.params.charset] || this.charsets.pi;
        
        for (let i = 0; i < numColumns; i++) {
            this.columns.push({
                x: (i / numColumns) * this.width + columnWidth / 2,
                y: -Math.random() * this.height,
                speed: 0.5 + Math.random() * 0.5,
                chars: [...charset],
                charIndex: Math.floor(Math.random() * charset.length)
            });
        }
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
            
            const { charset, speed, fontSize, color } = this.params;
            const charsetData = this.charsets[charset] || this.charsets.pi;
            
            ctx.font = `${fontSize}px 'Courier New', monospace`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            // Update and draw columns
            this.columns.forEach(column => {
                // Move column down
                column.y += column.speed * speed * (deltaTime / 16);
                
                // Reset if off screen
                if (column.y > this.height + fontSize) {
                    column.y = -fontSize;
                    column.charIndex = (column.charIndex + 1) % charsetData.length;
                }
                
                // Draw falling characters with fade
                const charsToDraw = Math.floor(this.height / fontSize) + 2;
                for (let i = 0; i < charsToDraw; i++) {
                    const y = column.y + i * fontSize;
                    if (y < -fontSize || y > this.height + fontSize) continue;
                    
                    const charIndex = (column.charIndex + i) % charsetData.length;
                    const char = charsetData[charIndex];
                    
                    // Fade effect (brightest at bottom)
                    const fade = Math.max(0.2, 1.0 - (i / charsToDraw));
                    ctx.fillStyle = color;
                    ctx.globalAlpha = fade;
                    
                    ctx.fillText(char, column.x, y);
                }
            });
            
            ctx.globalAlpha = 1.0;
        } catch (error) {
            console.error('DigitsRain render error:', error);
        }
    }
    
    onCleanup() {
        this.columns = [];
    }
    
    onResize() {
        // Reinitialize columns on resize
        if (this.isActive) {
            const { density, fontSize } = this.params;
            const columnWidth = fontSize * 1.2;
            const numColumns = Math.floor(this.width / columnWidth * density);
            
            this.columns = [];
            const charset = this.charsets[this.params.charset] || this.charsets.pi;
            
            for (let i = 0; i < numColumns; i++) {
                this.columns.push({
                    x: (i / numColumns) * this.width + columnWidth / 2,
                    y: -Math.random() * this.height,
                    speed: 0.5 + Math.random() * 0.5,
                    chars: [...charset],
                    charIndex: Math.floor(Math.random() * charset.length)
                });
            }
        }
    }
}

