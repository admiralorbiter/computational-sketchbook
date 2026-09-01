/**
 * Conway's Game of Life math visual preset
 * Cellular automaton with emergent patterns
 */

import { MathVisuals } from './MathVisuals.js';

export class ConwayLife extends MathVisuals {
    constructor(canvas, ctx) {
        super(canvas, ctx);
        this.grid = [];
        this.nextGrid = [];
        this.lastStepTime = 0;
    }
    
    getDefaultParams() {
        const defaultColor = this.getThemeColor('accent_green', '#39FF14');
        return {
            seed: 'random',    // 'random', 'gosper', or custom pattern
            stepMs: 100,        // Milliseconds between steps
            cellSize: 10,       // Cell size in pixels
            color: defaultColor
        };
    }
    
    validateParam(paramName, value, defaultValue) {
        if (value === null || value === undefined || (typeof value === 'number' && isNaN(value))) {
            return defaultValue;
        }
        
        const numValue = typeof value === 'string' ? parseFloat(value) : value;
        
        switch (paramName) {
            case 'seed':
                // Must be 'random', 'gosper', or valid string
                if (typeof value === 'string') {
                    return value;
                }
                return defaultValue;
                
            case 'stepMs':
                // Step interval: 50-1000ms
                if (typeof numValue !== 'number' || numValue < 50 || numValue > 1000) {
                    return Math.max(50, Math.min(1000, numValue));
                }
                return numValue;
                
            case 'cellSize':
                // Cell size: 5-20
                if (typeof numValue !== 'number' || numValue < 5 || numValue > 20) {
                    return Math.max(5, Math.min(20, numValue));
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
    
    initializeGrid(seed) {
        const cols = Math.floor(this.width / this.params.cellSize);
        const rows = Math.floor(this.height / this.params.cellSize);
        
        this.grid = [];
        this.nextGrid = [];
        
        for (let y = 0; y < rows; y++) {
            this.grid[y] = [];
            this.nextGrid[y] = [];
            for (let x = 0; x < cols; x++) {
                let alive = false;
                
                if (seed === 'random') {
                    alive = Math.random() > 0.7;
                } else if (seed === 'gosper') {
                    // Gosper glider gun pattern (simplified)
                    const centerX = Math.floor(cols / 2);
                    const centerY = Math.floor(rows / 2);
                    const dx = x - centerX;
                    const dy = y - centerY;
                    
                    // Simple pattern
                    alive = Math.abs(dx) < 10 && Math.abs(dy) < 10 && 
                            (dx * dx + dy * dy) < 50 && Math.random() > 0.8;
                }
                
                this.grid[y][x] = alive ? 1 : 0;
                this.nextGrid[y][x] = 0;
            }
        }
    }
    
    countNeighbors(x, y) {
        let count = 0;
        const rows = this.grid.length;
        const cols = this.grid[0].length;
        
        for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
                if (dx === 0 && dy === 0) continue;
                
                const ny = y + dy;
                const nx = x + dx;
                
                if (ny >= 0 && ny < rows && nx >= 0 && nx < cols) {
                    count += this.grid[ny][nx];
                }
            }
        }
        
        return count;
    }
    
    step() {
        const rows = this.grid.length;
        const cols = this.grid[0].length;
        
        // Calculate next generation
        for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                const neighbors = this.countNeighbors(x, y);
                const current = this.grid[y][x];
                
                // Conway's rules
                if (current === 1) {
                    // Live cell
                    this.nextGrid[y][x] = (neighbors === 2 || neighbors === 3) ? 1 : 0;
                } else {
                    // Dead cell
                    this.nextGrid[y][x] = (neighbors === 3) ? 1 : 0;
                }
            }
        }
        
        // Swap grids
        const temp = this.grid;
        this.grid = this.nextGrid;
        this.nextGrid = temp;
    }
    
    init(params = {}) {
        super.init(params);
        this.initializeGrid(this.params.seed);
        this.lastStepTime = performance.now();
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
            
            const { stepMs, cellSize, color } = this.params;
            
            // Step simulation if enough time has passed
            if (time - this.lastStepTime >= stepMs) {
                this.step();
                this.lastStepTime = time;
            }
            
            // Draw grid
            ctx.fillStyle = color;
            const rows = this.grid.length;
            const cols = this.grid[0].length;
            
            for (let y = 0; y < rows; y++) {
                for (let x = 0; x < cols; x++) {
                    if (this.grid[y][x] === 1) {
                        ctx.fillRect(
                            x * cellSize,
                            y * cellSize,
                            cellSize - 1,
                            cellSize - 1
                        );
                    }
                }
            }
        } catch (error) {
            console.error('ConwayLife render error:', error);
        }
    }
    
    onCleanup() {
        this.grid = [];
        this.nextGrid = [];
    }
    
    onResize() {
        if (this.isActive) {
            this.initializeGrid(this.params.seed);
        }
    }
}

