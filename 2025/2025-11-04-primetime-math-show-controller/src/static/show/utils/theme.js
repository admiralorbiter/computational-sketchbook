/**
 * Theme system for PrimeTime
 * Manages theme colors and provides access to all scenes
 */

class ThemeManager {
    constructor() {
        this.currentTheme = null;
        this.defaultTheme = {
            id: 'neon-chalkboard',
            name: 'Neon Chalkboard',
            colors: {
                bg_color: '#0f1115',
                fg_color: '#F4F4F4',
                accent_green: '#39FF14',
                accent_cyan: '#00E5FF',
                card_bg: '#1a1d24',
                border_color: '#2a2d35'
            },
            fonts: {
                heading: 'Arial, sans-serif',
                body: 'Arial, sans-serif',
                mono: "'Courier New', monospace"
            }
        };
    }
    
    /**
     * Load theme from JSON file or use default
     * @param {string} themeId - Theme identifier (e.g., 'neon-chalkboard')
     * @returns {Promise<Object>} Theme object
     */
    async loadTheme(themeId = 'neon-chalkboard') {
        try {
            const response = await fetch(`/themes/${themeId}.json`);
            if (response.ok) {
                const theme = await response.json();
                this.currentTheme = theme;
                return theme;
            } else {
                console.warn(`Theme file not found: ${themeId}.json, using default`);
                this.currentTheme = this.defaultTheme;
                return this.defaultTheme;
            }
        } catch (error) {
            console.error('Error loading theme:', error);
            this.currentTheme = this.defaultTheme;
            return this.defaultTheme;
        }
    }
    
    /**
     * Get current theme
     * @returns {Object} Current theme object
     */
    getTheme() {
        if (!this.currentTheme) {
            this.currentTheme = this.defaultTheme;
        }
        return this.currentTheme;
    }
    
    /**
     * Get a specific color from current theme
     * @param {string} colorKey - Color key (e.g., 'accent_green')
     * @param {string} fallback - Fallback color if key not found
     * @returns {string} Color value
     */
    getColor(colorKey, fallback = '#FFFFFF') {
        const theme = this.getTheme();
        return theme.colors?.[colorKey] || fallback;
    }
    
    /**
     * Get all colors from current theme
     * @returns {Object} Colors object
     */
    getColors() {
        const theme = this.getTheme();
        return theme.colors || {};
    }
    
    /**
     * Get font family from theme
     * @param {string} fontKey - Font key (e.g., 'heading', 'body', 'mono')
     * @param {string} fallback - Fallback font
     * @returns {string} Font family
     */
    getFont(fontKey, fallback = 'Arial, sans-serif') {
        const theme = this.getTheme();
        return theme.fonts?.[fontKey] || fallback;
    }
    
    /**
     * Initialize theme (load from default or server)
     * @returns {Promise<void>}
     */
    async init() {
        // Try to load from server settings first (future enhancement)
        // For now, load from JSON file
        await this.loadTheme('neon-chalkboard');
    }
}

// Export singleton instance
export const themeManager = new ThemeManager();

// Initialize on import
themeManager.init();

