/**
 * Utility functions for the Virtual Museum
 */

/**
 * Generate a random integer between min and max (inclusive)
 * @param {number} min The minimum value
 * @param {number} max The maximum value
 * @returns {number} Random integer
 */
export function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Generate a random float between min and max
 * @param {number} min The minimum value
 * @param {number} max The maximum value
 * @returns {number} Random float
 */
export function randomFloat(min, max) {
    return Math.random() * (max - min) + min;
}

/**
 * Generate a random color
 * @param {boolean} pastel Whether to generate a pastel color
 * @returns {THREE.Color} Random color
 */
export function randomColor(pastel = false) {
    if (pastel) {
        // Pastel colors
        return new THREE.Color(
            0.5 + Math.random() * 0.5,
            0.5 + Math.random() * 0.5,
            0.5 + Math.random() * 0.5
        );
    } else {
        // Fully saturated colors
        return new THREE.Color(
            Math.random(),
            Math.random(),
            Math.random()
        );
    }
}

/**
 * Interpolate between two colors
 * @param {THREE.Color|number} color1 First color
 * @param {THREE.Color|number} color2 Second color
 * @param {number} factor Interpolation factor (0-1)
 * @returns {THREE.Color} Interpolated color
 */
export function lerpColor(color1, color2, factor) {
    const c1 = (color1 instanceof THREE.Color) ? color1 : new THREE.Color(color1);
    const c2 = (color2 instanceof THREE.Color) ? color2 : new THREE.Color(color2);
    
    return new THREE.Color(
        c1.r + (c2.r - c1.r) * factor,
        c1.g + (c2.g - c1.g) * factor,
        c1.b + (c2.b - c1.b) * factor
    );
}

/**
 * Linear interpolation between two values
 * @param {number} a First value
 * @param {number} b Second value
 * @param {number} t Interpolation factor (0-1)
 * @returns {number} Interpolated value
 */
export function lerp(a, b, t) {
    return a + (b - a) * t;
}

/**
 * Convert a hexadecimal color to RGB components
 * @param {string|number} hex Hexadecimal color
 * @returns {Object} Object with r, g, b components (0-255)
 */
export function hexToRgb(hex) {
    // Handle string format
    if (typeof hex === 'string') {
        hex = hex.replace(/^#/, '');
    }
    
    // Parse hex
    const bigint = typeof hex === 'string' ? parseInt(hex, 16) : hex;
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    
    return { r, g, b };
}

/**
 * Calculate distance between two points in 3D space
 * @param {THREE.Vector3} point1 First point
 * @param {THREE.Vector3} point2 Second point
 * @returns {number} Distance
 */
export function distance3D(point1, point2) {
    return Math.sqrt(
        Math.pow(point2.x - point1.x, 2) +
        Math.pow(point2.y - point1.y, 2) +
        Math.pow(point2.z - point1.z, 2)
    );
}

/**
 * Calculate distance between two points in 2D space (ignoring Y axis)
 * @param {THREE.Vector3} point1 First point
 * @param {THREE.Vector3} point2 Second point
 * @returns {number} Distance
 */
export function distance2D(point1, point2) {
    return Math.sqrt(
        Math.pow(point2.x - point1.x, 2) +
        Math.pow(point2.z - point1.z, 2)
    );
}

/**
 * Normalize a value to a range between 0 and 1
 * @param {number} value Value to normalize
 * @param {number} min Minimum value
 * @param {number} max Maximum value
 * @returns {number} Normalized value (0-1)
 */
export function normalize(value, min, max) {
    return (value - min) / (max - min);
}

/**
 * Clamp a value between min and max
 * @param {number} value Value to clamp
 * @param {number} min Minimum value
 * @param {number} max Maximum value
 * @returns {number} Clamped value
 */
export function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

/**
 * Check if a point is inside a box
 * @param {THREE.Vector3} point The point to check
 * @param {THREE.Box3} box The box
 * @returns {boolean} True if the point is inside the box
 */
export function pointInBox(point, box) {
    return (
        point.x >= box.min.x && point.x <= box.max.x &&
        point.y >= box.min.y && point.y <= box.max.y &&
        point.z >= box.min.z && point.z <= box.max.z
    );
}

/**
 * Create a unique ID
 * @param {string} prefix Optional prefix for the ID
 * @returns {string} Unique ID
 */
export function createUniqueId(prefix = '') {
    return `${prefix}${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Delay execution for a specified time
 * @param {number} ms Milliseconds to delay
 * @returns {Promise} Promise that resolves after the delay
 */
export function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Check if WebGL is available and supported
 * @returns {boolean} True if WebGL is supported
 */
export function isWebGLAvailable() {
    try {
        const canvas = document.createElement('canvas');
        return !!(
            window.WebGLRenderingContext && 
            (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
        );
    } catch (e) {
        return false;
    }
}

/**
 * Check if WebXR is available for VR
 * @returns {boolean} True if WebXR is supported
 */
export function isVRSupported() {
    return 'xr' in navigator;
}

/**
 * Format a number with commas
 * @param {number} number Number to format
 * @returns {string} Formatted number string
 */
export function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Load a texture with a progress callback
 * @param {string} url Texture URL
 * @param {Function} onProgress Progress callback (receives percentage 0-100)
 * @returns {Promise<THREE.Texture>} Promise that resolves with the loaded texture
 */
export function loadTextureWithProgress(url, onProgress) {
    return new Promise((resolve, reject) => {
        const loader = new THREE.TextureLoader();
        loader.load(
            url,
            texture => resolve(texture),
            xhr => {
                if (xhr.lengthComputable) {
                    const percentage = (xhr.loaded / xhr.total) * 100;
                    if (onProgress) onProgress(percentage);
                }
            },
            error => reject(error)
        );
    });
}

/**
 * Load a texture as a promise
 * @param {string} url Texture URL
 * @returns {Promise<THREE.Texture>} Promise that resolves with the loaded texture
 */
export function loadTexture(url) {
    return new Promise((resolve, reject) => {
        new THREE.TextureLoader().load(
            url,
            resolve,
            undefined,
            reject
        );
    });
}

/**
 * Dispose of a Three.js object and all its children
 * @param {THREE.Object3D} object Object to dispose
 */
export function disposeObject(object) {
    if (!object) return;
    
    // Traverse and dispose of geometries and materials
    object.traverse(child => {
        if (child.geometry) {
            child.geometry.dispose();
        }
        
        if (child.material) {
            if (Array.isArray(child.material)) {
                child.material.forEach(material => disposeMaterial(material));
            } else {
                disposeMaterial(child.material);
            }
        }
    });
    
    // Remove from parent
    if (object.parent) {
        object.parent.remove(object);
    }
}

/**
 * Dispose of a Three.js material and its textures
 * @param {THREE.Material} material Material to dispose
 */
function disposeMaterial(material) {
    // Dispose of material maps and textures
    for (const prop in material) {
        const value = material[prop];
        if (value && typeof value === 'object' && 'minFilter' in value) {
            value.dispose();
        }
    }
    
    // Dispose of the material itself
    material.dispose();
}