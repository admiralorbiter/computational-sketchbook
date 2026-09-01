/**
 * Land Bank Properties Map Layer
 * 
 * Displays Land Bank and Kansas City Homesteading Authority properties on the map.
 */

class LandBankLayer {
    constructor(map, options = {}) {
        this.map = map;
        this.options = {
            cluster: true,
            maxZoom: 15,
            radius: 50,
            ...options
        };
        
        this.layer = null;
        this.clusterLayer = null;
        this.isVisible = false;
        this.isLoading = false;
        
        // Layer configuration
        this.config = {
            name: 'Land Bank Properties',
            id: 'landbank',
            type: 'landbank',
            icon: 'house',
            color: '#FF8C00',
            description: 'Vacant properties and homesteading opportunities'
        };
        
        this.init();
    }
    
    init() {
        this.createLayer();
        this.setupEventHandlers();
    }
    
    createLayer() {
        // Create marker cluster group if clustering is enabled
        if (this.options.cluster) {
            this.clusterLayer = L.markerClusterGroup({
                maxClusterRadius: this.options.radius,
                disableClusteringAtZoom: this.options.maxZoom,
                iconCreateFunction: this.createClusterIcon.bind(this)
            });
            this.layer = this.clusterLayer;
        } else {
            this.layer = L.layerGroup();
        }
    }
    
    createClusterIcon(cluster) {
        const count = cluster.getChildCount();
        const size = count < 10 ? 'small' : count < 100 ? 'medium' : 'large';
        
        return L.divIcon({
            html: `<div class="cluster-icon cluster-${size}">${count}</div>`,
            className: 'landbank-cluster',
            iconSize: [30, 30]
        });
    }
    
    setupEventHandlers() {
        // Handle layer visibility changes
        this.map.on('overlayadd', (e) => {
            if (e.layer === this.layer) {
                this.show();
            }
        });
        
        this.map.on('overlayremove', (e) => {
            if (e.layer === this.layer) {
                this.hide();
            }
        });
    }
    
    async loadData(bbox, filters = {}) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingIndicator();
        
        try {
            const params = new URLSearchParams({
                bbox: bbox.join(','),
                limit: 2000,
                ...filters
            });
            
            const response = await fetch(`/api/v1/landbank/properties?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.processData(data.features);
            
        } catch (error) {
            console.error('Error loading Land Bank data:', error);
            this.showError('Failed to load Land Bank properties');
        } finally {
            this.isLoading = false;
            this.hideLoadingIndicator();
        }
    }
    
    processData(features) {
        // Clear existing markers
        this.layer.clearLayers();
        
        // Create markers for each property
        features.forEach(feature => {
            if (feature.geometry && feature.geometry.coordinates) {
                const marker = this.createMarker(feature);
                this.layer.addLayer(marker);
            }
        });
        
        console.log(`Loaded ${features.length} Land Bank properties`);
    }
    
    createMarker(feature) {
        const [lng, lat] = feature.geometry.coordinates;
        const properties = feature.properties;
        
        // Create custom icon based on property status
        const icon = this.createPropertyIcon(properties);
        
        const marker = L.marker([lat, lng], { icon })
            .bindPopup(this.createPopupContent(properties), {
                maxWidth: 300,
                className: 'landbank-popup'
            });
        
        // Store feature data for filtering
        marker.featureData = feature;
        
        return marker;
    }
    
    createPropertyIcon(properties) {
        const status = properties.property_status || 'Unknown';
        const inventoryType = properties.inventory_type || 'Land Bank';
        
        // Determine icon color based on status
        let color = '#FF8C00'; // Default orange
        if (status.toLowerCase().includes('available')) {
            color = '#32CD32'; // Green
        } else if (status.toLowerCase().includes('pending')) {
            color = '#FFD700'; // Gold
        } else if (status.toLowerCase().includes('demolished')) {
            color = '#808080'; // Gray
        }
        
        // Create icon HTML
        const iconHtml = `
            <div class="landbank-marker" style="background-color: ${color}">
                <i class="fas fa-home"></i>
            </div>
        `;
        
        return L.divIcon({
            html: iconHtml,
            className: 'landbank-marker-container',
            iconSize: [25, 25],
            iconAnchor: [12, 12]
        });
    }
    
    createPopupContent(properties) {
        const {
            address,
            city,
            state,
            postal_code,
            property_status,
            inventory_type,
            property_class,
            property_condition,
            market_value,
            market_value_year,
            square_footage,
            neighborhood,
            city_council_district,
            date_of_acquisition,
            demo_needed,
            parcel_number
        } = properties;
        
        const fullAddress = [address, city, state, postal_code].filter(Boolean).join(', ');
        const marketValueText = market_value ? `$${market_value.toLocaleString()}` : 'N/A';
        const squareFootageText = square_footage ? `${square_footage.toLocaleString()} sq ft` : 'N/A';
        const demoText = demo_needed === 'Y' ? 'Yes' : demo_needed === 'N' ? 'No' : 'Unknown';
        
        return `
            <div class="landbank-popup-content">
                <div class="popup-header">
                    <h3>Land Bank Property</h3>
                    <span class="property-status status-${property_status?.toLowerCase().replace(/\s+/g, '-') || 'unknown'}">
                        ${property_status || 'Unknown Status'}
                    </span>
                </div>
                
                <div class="popup-body">
                    <div class="property-address">
                        <strong>${fullAddress || 'No Address'}</strong>
                    </div>
                    
                    <div class="property-details">
                        <div class="detail-row">
                            <span class="label">Inventory Type:</span>
                            <span class="value">${inventory_type || 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Property Class:</span>
                            <span class="value">${property_class || 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Condition:</span>
                            <span class="value">${property_condition || 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Market Value:</span>
                            <span class="value">${marketValueText} (${market_value_year || 'N/A'})</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Square Footage:</span>
                            <span class="value">${squareFootageText}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Neighborhood:</span>
                            <span class="value">${neighborhood || 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Council District:</span>
                            <span class="value">${city_council_district || 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Date Acquired:</span>
                            <span class="value">${date_of_acquisition || 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Demo Needed:</span>
                            <span class="value">${demoText}</span>
                        </div>
                        ${parcel_number ? `
                        <div class="detail-row">
                            <span class="label">Parcel Number:</span>
                            <span class="value">${parcel_number}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="popup-footer">
                    <button class="btn btn-sm btn-primary" onclick="window.open('https://data.kcmo.org/Neighborhoods/Land-Bank-and-Kansas-City-Missouri-Homesteading-Au/2ebw-sp7f', '_blank')">
                        View Full Dataset
                    </button>
                </div>
            </div>
        `;
    }
    
    show() {
        if (!this.isVisible) {
            this.map.addLayer(this.layer);
            this.isVisible = true;
        }
    }
    
    hide() {
        if (this.isVisible) {
            this.map.removeLayer(this.layer);
            this.isVisible = false;
        }
    }
    
    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    showLoadingIndicator() {
        // Show loading indicator in UI
        const indicator = document.getElementById('landbank-loading');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }
    
    hideLoadingIndicator() {
        // Hide loading indicator
        const indicator = document.getElementById('landbank-loading');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    showError(message) {
        // Show error message
        console.error('Land Bank Layer Error:', message);
        // Could implement toast notification here
    }
    
    getLayer() {
        return this.layer;
    }
    
    getConfig() {
        return this.config;
    }
    
    destroy() {
        this.hide();
        if (this.layer) {
            this.layer.clearLayers();
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LandBankLayer;
}
