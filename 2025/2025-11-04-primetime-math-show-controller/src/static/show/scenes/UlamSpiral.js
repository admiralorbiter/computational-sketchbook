/**
 * Ulam Prime Spiral math visual preset
 * Spiral grid layout revealing patterns in prime numbers
 */

import { MathVisuals } from './MathVisuals.js';
import { isPrime } from '../utils/primes.js';

export class UlamSpiral extends MathVisuals {
    constructor(canvas, ctx) {
        super(canvas, ctx);
        this.grid = [];
        this.cellSize = 0;
        this.spiralData = [];
    }
    
    getDefaultParams() {
        const defaultColor = this.getThemeColor('accent_cyan', '#00E5FF');
        return {
            grid: 50,              // Grid size (spiral will be grid x grid)
            pulse: 1.0,            // Pulse animation intensity (0-1)
            highlightPrimes: true, // Highlight prime numbers
            color: defaultColor
        };
    }
    
    validateParam(paramName, value, defaultValue) {
        if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
            return defaultValue;
        }
        
        const numValue = typeof value === 'string' ? parseFloat(value) : value;
        
        switch (paramName) {
            case 'grid':
                // Grid size: 20-100
                if (typeof numValue !== 'number' || numValue < 20 || numValue > 100) {
                    return Math.max(20, Math.min(100, numValue));
                }
                return Math.floor(numValue);
                
            case 'pulse':
                // Pulse: 0-1
                if (typeof numValue !== 'number' || numValue < 0 || numValue > 1) {
                    return Math.max(0, Math.min(1, numValue));
                }
                return numValue;
                
            case 'highlightPrimes':
                // Boolean
                return typeof value === 'boolean' ? value : defaultValue;
                
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
    
    generateSpiral(gridSize) {
        // Generate spiral coordinates for Ulam spiral
        const spiral = [];
        const center = Math.floor(gridSize / 2);
        
        let x = center;
        let y = center;
        let num = 1;
        let step = 1;
        let direction = 0; // 0=right, 1=up, 2=left, 3=down
        
        spiral.push({ x, y, num, isPrime: isPrime(num) });
        
        while (spiral.length < gridSize * gridSize) {
            for (let i = 0; i < 2; i++) {
                for (let j = 0; j < step; j++) {
                    num++;
                    if (num > gridSize * gridSize) break;
                    
                    switch (direction) {
                        case 0: x++; break;
                        case 1: y--; break;
                        case 2: x--; break;
                        case 3: y++; break;
                    }
                    
                    spiral.push({ 
                        x, 
                        y, 
                        num, 
                        isPrime: isPrime(num) 
                    });
                }
                direction = (direction + 1) % 4;
            }
            step++;
        }
        
        return spiral;
    }
    
    init(params = {}) {
        super.init(params);
        
        const { grid } = this.params;
        this.cellSize = Math.min(this.width, this.height) / grid;
        this.spiralData = this.generateSpiral(grid);
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
            
            const { pulse, highlightPrimes, color } = this.params;
            const t = this.currentTime / 1000;
            
            // Calculate pulse animation
            const pulseValue = 0.5 + 0.5 * Math.sin(t * 2) * pulse;
            
            // Draw spiral
            const centerX = this.width / 2;
            const centerY = this.height / 2;
            
            this.spiralData.forEach(cell => {
                const x = centerX + (cell.x - this.params.grid / 2) * this.cellSize;
                const y = centerY + (cell.y - this.params.grid / 2) * this.cellSize;
                
                if (highlightPrimes && cell.isPrime) {
                    // Highlight prime numbers
                    ctx.fillStyle = color;
                    ctx.globalAlpha = pulseValue;
                    ctx.fillRect(
                        x - this.cellSize / 2,
                        y - this.cellSize / 2,
                        this.cellSize * 0.8,
                        this.cellSize * 0.8
                    );
                } else {
                    // Dim non-primes
                    ctx.fillStyle = color;
                    ctx.globalAlpha = 0.1;
                    ctx.fillRect(
                        x - this.cellSize / 2,
                        y - this.cellSize / 2,
                        this.cellSize * 0.3,
                        this.cellSize * 0.3
                    );
                }
            });
            
            ctx.globalAlpha = 1.0;
        } catch (error) {
            console.error('UlamSpiral render error:', error);
        }
    }
    
    onCleanup() {
        this.spiralData = [];
    }
    
    onResize() {
        if (this.isActive) {
            const { grid } = this.params;
            this.cellSize = Math.min(this.width, this.height) / grid;
        }
    }
}

