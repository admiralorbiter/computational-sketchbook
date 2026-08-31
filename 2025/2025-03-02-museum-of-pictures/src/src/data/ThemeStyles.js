export class ThemeStyles {
    constructor() {
        // Theme definitions for different museum areas
        this.themes = {
            classical: {
                name: 'Classical Gallery',
                description: 'A traditional museum experience with marble floors and warm lighting',
                
                // UI styling
                colors: {
                    primary: '#8b7355',     // Dark brown
                    secondary: '#c9b18f',   // Light brown
                    background: '#f5f2e9',  // Off-white
                    text: '#333333',        // Dark gray
                    accent: '#6d4c41'       // Mahogany
                },
                
                // Font settings
                typography: {
                    titleFont: 'Georgia, serif',
                    bodyFont: 'Georgia, serif',
                    fontSize: '1em'
                },
                
                // UI elements
                ui: {
                    panelOpacity: 0.85,
                    borderRadius: '4px',
                    borderWidth: '2px',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
                }
            },
            
            futuristic: {
                name: 'Futuristic Exhibition',
                description: 'A high-tech, modern exhibit space with sleek metallic surfaces',
                
                // UI styling
                colors: {
                    primary: '#0a1a2a',     // Dark blue
                    secondary: '#00aaff',   // Bright blue
                    background: '#151f2e',  // Navy blue
                    text: '#ffffff',        // White
                    accent: '#00ffcc'       // Teal
                },
                
                // Font settings
                typography: {
                    titleFont: 'Orbitron, Arial, sans-serif',
                    bodyFont: 'Roboto, Arial, sans-serif',
                    fontSize: '0.95em'
                },
                
                // UI elements
                ui: {
                    panelOpacity: 0.9,
                    borderRadius: '0',
                    borderWidth: '1px',
                    boxShadow: '0 0 15px rgba(0,170,255,0.5)'
                }
            },
            
            abstract: {
                name: 'Abstract Collection',
                description: 'A surreal, experimental space with unusual forms and lighting',
                
                // UI styling
                colors: {
                    primary: '#2a0a2a',     // Dark purple
                    secondary: '#00ffaa',   // Bright teal
                    background: '#1a0a1a',  // Very dark purple
                    text: '#ffffff',        // White
                    accent: '#ff00ff'       // Magenta
                },
                
                // Font settings
                typography: {
                    titleFont: 'Rajdhani, Arial, sans-serif',
                    bodyFont: 'Quicksand, Arial, sans-serif',
                    fontSize: '1em'
                },
                
                // UI elements
                ui: {
                    panelOpacity: 0.8,
                    borderRadius: '8px',
                    borderWidth: '0',
                    boxShadow: '0 0 20px rgba(255,0,255,0.6)'
                }
            }
        };
        
        // Default theme
        this.currentTheme = 'classical';
    }
    
    // Get a specific theme
    getTheme(themeName) {
        if (this.themes[themeName]) {
            return this.themes[themeName];
        } else {
            console.warn(`Theme ${themeName} not found, using default theme`);
            return this.themes[this.currentTheme];
        }
    }
    
    // Get current theme
    getCurrentTheme() {
        return this.themes[this.currentTheme];
    }
    
    // Set current theme
    setCurrentTheme(themeName) {
        if (this.themes[themeName]) {
            this.currentTheme = themeName;
            this.applyTheme(themeName);
            return true;
        }
        return false;
    }
    
    // Apply theme to UI elements
    applyTheme(themeName) {
        const theme = this.getTheme(themeName);
        
        // Apply to CSS variables
        const root = document.documentElement;
        
        // Colors
        root.style.setProperty('--primary-color', theme.colors.primary);
        root.style.setProperty('--secondary-color', theme.colors.secondary);
        root.style.setProperty('--background-color', theme.colors.background);
        root.style.setProperty('--text-color', theme.colors.text);
        root.style.setProperty('--accent-color', theme.colors.accent);
        
        // Typography
        root.style.setProperty('--title-font', theme.typography.titleFont);
        root.style.setProperty('--body-font', theme.typography.bodyFont);
        root.style.setProperty('--font-size', theme.typography.fontSize);
        
        // UI elements
        root.style.setProperty('--panel-opacity', theme.ui.panelOpacity);
        root.style.setProperty('--border-radius', theme.ui.borderRadius);
        root.style.setProperty('--border-width', theme.ui.borderWidth);
        root.style.setProperty('--box-shadow', theme.ui.boxShadow);
        
        // Apply theme to specific UI elements
        this.updateInfoPanel(theme);
        this.updateHUD(theme);
    }
    
    // Update info panel styling
    updateInfoPanel(theme) {
        const infoPanel = document.getElementById('info-panel');
        if (!infoPanel) return;
        
        // Apply theme-specific styles
        infoPanel.style.backgroundColor = `rgba(${this.hexToRgb(theme.colors.background)}, ${theme.ui.panelOpacity})`;
        infoPanel.style.color = theme.colors.text;
        infoPanel.style.borderRadius = theme.ui.borderRadius;
        infoPanel.style.boxShadow = theme.ui.boxShadow;
        infoPanel.style.border = `${theme.ui.borderWidth} solid ${theme.colors.primary}`;
        
        // Typography
        const infoTitle = document.getElementById('info-title');
        if (infoTitle) {
            infoTitle.style.fontFamily = theme.typography.titleFont;
            infoTitle.style.color = theme.colors.accent;
        }
        
        const infoContent = document.querySelector('.info-content');
        if (infoContent) {
            infoContent.style.fontFamily = theme.typography.bodyFont;
            infoContent.style.fontSize = theme.typography.fontSize;
        }
    }
    
    // Update HUD styling
    updateHUD(theme) {
        const hud = document.getElementById('hud');
        if (!hud) return;
        
        // Apply theme-specific styles
        hud.style.backgroundColor = `rgba(${this.hexToRgb(theme.colors.primary)}, ${theme.ui.panelOpacity})`;
        hud.style.color = theme.colors.text;
        hud.style.borderRadius = theme.ui.borderRadius;
        hud.style.boxShadow = theme.ui.boxShadow;
        hud.style.fontFamily = theme.typography.bodyFont;
    }
    
    // Helper function to convert hex color to RGB
    hexToRgb(hex) {
        // Remove # if present
        hex = hex.replace(/^#/, '');
        
        // Parse hex
        const bigint = parseInt(hex, 16);
        const r = (bigint >> 16) & 255;
        const g = (bigint >> 8) & 255;
        const b = bigint & 255;
        
        return `${r}, ${g}, ${b}`;
    }
}