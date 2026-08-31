import { MetadataManager } from '../data/MetadataManager.js';

export class InfoPanel {
    constructor() {
        this.panel = document.getElementById('info-panel');
        this.titleElement = document.getElementById('info-title');
        this.authorElement = document.getElementById('info-author');
        this.descriptionElement = document.getElementById('info-description');
        this.sourceElement = document.getElementById('info-source');
        this.closeButton = document.getElementById('close-info');
        
        this.metadataManager = new MetadataManager();
        this.currentArtwork = null;
        
        // Set up event listeners
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.hide());
        }
        
        // Close panel with ESC key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && !this.panel.classList.contains('hidden')) {
                this.hide();
            }
        });
    }
    
    /**
     * Show the info panel with artwork details
     */
    show(artwork) {
        if (!artwork) return;
        
        this.currentArtwork = artwork;
        
        // Get metadata
        const metadata = this.metadataManager.getMetadata(artwork);
        
        // Update panel content
        if (this.titleElement) {
            this.titleElement.textContent = metadata.title || 'Untitled Artwork';
        }
        
        if (this.authorElement) {
            this.authorElement.textContent = metadata.artist || 'Unknown Artist';
            if (metadata.year) {
                this.authorElement.textContent += `, ${metadata.year}`;
            }
        }
        
        if (this.descriptionElement) {
            this.descriptionElement.textContent = metadata.description || 'No description available.';
        }
        
        if (this.sourceElement) {
            this.sourceElement.textContent = `Source: ${metadata.source || 'Unknown'}`;
        }
        
        // Show the panel
        this.panel.classList.remove('hidden');
    }
    
    /**
     * Hide the info panel
     */
    hide() {
        this.panel.classList.add('hidden');
        this.currentArtwork = null;
    }
    
    /**
     * Toggle the info panel
     */
    toggle(artwork) {
        if (this.panel.classList.contains('hidden') || this.currentArtwork !== artwork) {
            this.show(artwork);
        } else {
            this.hide();
        }
    }
    
    /**
     * Update the panel's position relative to an object
     */
    updatePosition(position, camera, renderer) {
        if (this.panel.classList.contains('hidden')) return;
        
        // Convert 3D position to screen coordinates
        const vector = position.clone();
        vector.project(camera);
        
        const widthHalf = renderer.domElement.width / 2;
        const heightHalf = renderer.domElement.height / 2;
        
        vector.x = (vector.x * widthHalf) + widthHalf;
        vector.y = -(vector.y * heightHalf) + heightHalf;
        
        // Position panel near the object but ensure it stays within viewport
        const panelWidth = this.panel.offsetWidth;
        const panelHeight = this.panel.offsetHeight;
        
        const padding = 20;
        
        let x = vector.x + padding;
        let y = vector.y - panelHeight / 2;
        
        // Ensure panel stays within viewport
        if (x + panelWidth > window.innerWidth - padding) {
            x = vector.x - panelWidth - padding;
        }
        
        if (y < padding) {
            y = padding;
        } else if (y + panelHeight > window.innerHeight - padding) {
            y = window.innerHeight - panelHeight - padding;
        }
        
        // Update panel position
        this.panel.style.left = `${x}px`;
        this.panel.style.top = `${y}px`;
    }
}