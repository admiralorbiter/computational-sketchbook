/**
 * Global configuration settings for the Virtual Museum
 */
export const Config = {
    // Performance settings
    performance: {
        maxRenderDistance: 50,      // Distance beyond which objects are unloaded
        generationDistance: 30,      // Distance at which new rooms are generated
        targetFPS: 60,               // Target frames per second
        qualityPreset: 'medium',     // Options: 'low', 'medium', 'high'
        enableShadows: true,         // Enable/disable shadow rendering
        enablePostProcessing: false, // Enable/disable post-processing effects
        maxArtworksPerRoom: 5        // Maximum number of artworks in a single room
    },
    
    // Navigation settings
    navigation: {
        moveSpeed: 0.1,              // Base movement speed
        runMultiplier: 2.0,          // Speed multiplier when running
        mouseSensitivity: 0.002,     // Mouse look sensitivity
        enableJumping: true,         // Enable/disable jumping
        jumpHeight: 1.0,             // Maximum jump height
        playerHeight: 1.7,           // Player eye level height
        collisionDetection: true     // Enable/disable collision detection
    },
    
    // Museum layout settings
    museum: {
        roomSpacing: 15,             // Distance between room centers
        defaultRoomSize: {           // Default dimensions for a standard room
            width: 10,
            height: 5,
            depth: 10
        },
        regionTransitionDistance: 5, // Distance threshold for region transition effects
        enableElevationChanges: true // Enable/disable multi-level architecture
    },
    
    // UI settings
    ui: {
        showHUD: true,               // Show/hide heads-up display
        showMinimap: false,          // Show/hide minimap
        showFPS: true,               // Show/hide FPS counter
        hudOpacity: 0.8,             // Opacity of HUD elements
        infoPanelWidth: 400,         // Width of artwork info panel in pixels
        autoCloseInfoPanel: false,   // Automatically close info panel when moving
        hudPosition: 'bottom-left',  // HUD position: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    },
    
    // Content settings
    content: {
        preferredArtSource: 'wikimedia', // Options: 'wikimedia', 'local', 'mixed'
        loadPlaceholdersFirst: true,     // Load placeholder images first, then real content
        preloadImages: true,             // Preload images on startup for smoother experience
        textureQuality: 'medium',        // Options: 'low', 'medium', 'high'
        audioEnabled: false,             // Enable/disable ambient audio
        audioVolume: 0.5                 // Audio volume (0.0 to 1.0)
    },
    
    // Debug settings
    debug: {
        showStats: true,                 // Show performance statistics
        logGeneratedRooms: false,        // Log info about newly generated rooms
        showBoundingBoxes: false,        // Show bounding boxes around objects
        disableUnloading: false,         // Disable unloading of distant rooms (may cause performance issues)
        showRegionBoundaries: false      // Highlight region boundaries
    }
};

/**
 * Apply user-defined configuration settings
 * @param {Object} userConfig User configuration object to merge with defaults
 */
export function applyUserConfig(userConfig) {
    // Deep merge userConfig into Config
    mergeDeep(Config, userConfig);
    console.log('Applied user configuration settings');
}

/**
 * Utility function to deep merge objects
 * @param {Object} target Target object
 * @param {Object} source Source object
 * @returns {Object} Merged object
 */
function mergeDeep(target, source) {
    const isObject = (obj) => obj && typeof obj === 'object';
    
    if (!isObject(target) || !isObject(source)) {
        return source;
    }
    
    Object.keys(source).forEach(key => {
        const targetValue = target[key];
        const sourceValue = source[key];
        
        if (Array.isArray(targetValue) && Array.isArray(sourceValue)) {
            target[key] = targetValue.concat(sourceValue);
        } else if (isObject(targetValue) && isObject(sourceValue)) {
            target[key] = mergeDeep(Object.assign({}, targetValue), sourceValue);
        } else {
            target[key] = sourceValue;
        }
    });
    
    return target;
}