export class Renderer {
    constructor(container) {
        this.container = container;
        
        // Create WebGL renderer
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            powerPreference: 'high-performance'
        });
        
        // Configure renderer
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Soft shadows
        this.renderer.outputEncoding = THREE.sRGBEncoding; // For better color rendering
        
        // Add to DOM
        this.container.appendChild(this.renderer.domElement);
        
        // Set up post-processing if needed
        this.setupPostProcessing();
    }
    
    setupPostProcessing() {
        // This can be expanded with more advanced post-processing effects
        // For now, we'll keep it simple
        this.composer = null;
    }
    
    onWindowResize() {
        // Update renderer size when window is resized
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        
        // Update composer if it exists
        if (this.composer) {
            this.composer.setSize(window.innerWidth, window.innerHeight);
        }
    }
    
    render(scene, camera) {
        // If we have post-processing set up, use composer
        if (this.composer) {
            this.composer.render();
        } else {
            // Otherwise use standard rendering
            this.renderer.render(scene, camera);
        }
    }
    
    // Method to enable/disable specific renderer features
    setRenderQuality(quality) {
        switch(quality) {
            case 'low':
                this.renderer.setPixelRatio(1);
                this.renderer.shadowMap.enabled = false;
                break;
            case 'medium':
                this.renderer.setPixelRatio(Math.min(1.5, window.devicePixelRatio));
                this.renderer.shadowMap.enabled = true;
                this.renderer.shadowMap.type = THREE.PCFShadowMap;
                break;
            case 'high':
                this.renderer.setPixelRatio(window.devicePixelRatio);
                this.renderer.shadowMap.enabled = true;
                this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                break;
            default:
                console.warn('Unknown quality setting:', quality);
        }
    }
    
    // Enable VR if WebXR is available (for future extension)
    enableVR() {
        if (navigator.xr) {
            this.renderer.xr.enabled = true;
            // Create VR button - this would need to be implemented
            // or use a library like three.js VRButton
            console.log('VR enabled');
            return true;
        } else {
            console.warn('WebXR not available in this browser');
            return false;
        }
    }
}