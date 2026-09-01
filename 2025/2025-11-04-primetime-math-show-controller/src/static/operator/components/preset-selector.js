/**
 * Preset Selector Web Component
 * Displays grid of math visual presets for selection
 */

class PresetSelector extends HTMLElement {
    constructor() {
        super();
        this.socket = null;
        this.presets = [
            {
                id: 'lissajous',
                name: 'Lissajous Curves',
                description: 'Parametric curves with trail effect',
                complexity: 'simple',
                thumbnail: '📈'
            },
            {
                id: 'polar-roses',
                name: 'Polar Roses',
                description: 'Beautiful rose patterns from polar equations',
                complexity: 'simple',
                thumbnail: '🌹'
            },
            {
                id: 'spirograph',
                name: 'Spirograph',
                description: 'Nested circles creating mesmerizing patterns',
                complexity: 'medium',
                thumbnail: '🌀'
            },
            {
                id: 'digits-rain',
                name: 'Digits Rain',
                description: 'Matrix-style falling numbers (π, e, primes)',
                complexity: 'medium',
                thumbnail: '💧'
            },
            {
                id: 'ulam-spiral',
                name: 'Ulam Spiral',
                description: 'Prime number patterns in spiral layout',
                complexity: 'medium',
                thumbnail: '🌀'
            },
            {
                id: 'conway-life',
                name: "Conway's Life",
                description: 'Cellular automaton with emergent patterns',
                complexity: 'complex',
                thumbnail: '🔬'
            },
            {
                id: 'mandelbrot',
                name: 'Mandelbrot Set',
                description: 'Fractal visualization with zoom',
                complexity: 'complex',
                thumbnail: '🌊'
            }
        ];
    }
    
    connectedCallback() {
        this.render();
        this.setupEventListeners();
        this.waitForSocket();
    }
    
    waitForSocket() {
        if (window.operatorUI && window.operatorUI.socket) {
            this.socket = window.operatorUI.socket;
            return;
        }
        
        setTimeout(() => {
            if (window.operatorUI && window.operatorUI.socket) {
                this.socket = window.operatorUI.socket;
            } else {
                setTimeout(() => {
                    if (window.operatorUI && window.operatorUI.socket) {
                        this.socket = window.operatorUI.socket;
                    }
                }, 500);
            }
        }, 100);
    }
    
    render() {
        this.innerHTML = `
            <div class="preset-selector-panel">
                <h2>Math Visual Presets</h2>
                <div class="presets-grid" id="presets-grid">
                    ${this.presets.map(preset => `
                        <div class="preset-card" data-preset-id="${preset.id}">
                            <div class="preset-thumbnail">${preset.thumbnail}</div>
                            <div class="preset-info">
                                <h3>${preset.name}</h3>
                                <p class="preset-description">${preset.description}</p>
                                <span class="preset-complexity complexity-${preset.complexity}">${preset.complexity}</span>
                            </div>
                            <button class="btn btn-primary preset-start-btn" data-preset-id="${preset.id}">
                                Start Preset
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    setupEventListeners() {
        // Add click handlers to all preset start buttons
        const startButtons = this.querySelectorAll('.preset-start-btn');
        startButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const presetId = e.target.getAttribute('data-preset-id');
                this.startPreset(presetId);
            });
        });
        
        // Make entire card clickable
        const presetCards = this.querySelectorAll('.preset-card');
        presetCards.forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.classList.contains('preset-start-btn')) {
                    const presetId = card.getAttribute('data-preset-id');
                    this.startPreset(presetId);
                }
            });
        });
    }
    
    startPreset(presetId) {
        if (!this.socket) {
            this.waitForSocket();
        }
        
        if (!this.socket || !this.socket.connected) {
            this.showToast('WebSocket not connected. Please wait for connection.', 'error');
            return;
        }
        
        // Find preset
        const preset = this.presets.find(p => p.id === presetId);
        if (!preset) {
            console.error(`Preset not found: ${presetId}`);
            return;
        }
        
        // Send start scene command
        this.socket.emit('CONTROL_START_SCENE', {
            sceneId: presetId,
            params: {}
        });
        
        // Show feedback
        this.showToast(`Starting ${preset.name}...`, 'info');
        
        // Update active state
        this.updateActivePreset(presetId);
    }
    
    updateActivePreset(activeId) {
        const presetCards = this.querySelectorAll('.preset-card');
        presetCards.forEach(card => {
            const presetId = card.getAttribute('data-preset-id');
            if (presetId === activeId) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        });
    }
    
    showToast(message, type = 'info') {
        // Use the scene-controls toast system if available
        const sceneControls = document.querySelector('scene-controls');
        if (sceneControls && sceneControls.showToast) {
            sceneControls.showToast(message, type);
        } else {
            // Fallback: use alert
            console.log(`[${type}] ${message}`);
        }
    }
    
    // Method to add new presets dynamically
    addPreset(preset) {
        this.presets.push(preset);
        this.render();
        this.setupEventListeners();
    }
}

customElements.define('preset-selector', PresetSelector);

