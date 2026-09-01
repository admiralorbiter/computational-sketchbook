/**
 * Main application JavaScript
 */

// Global variables
let map;
let layers = {};
let currentFeatures = {};
let sidebarCollapsed = false;
let featurePanelOpen = false;
let loadingTimeout;
let loadedBounds = {}; // Track loaded areas per layer
let currentFilter = null; // Track current filter value
let consolidationEnabled = true;
let detailsSidebarOpen = false;
let activeFilters = {}; // Store active filters per layer
let spatialFilter = null; // Store active spatial filter
let searchDebounce; // For debouncing search input
let radiusFilterActive = false; // Track when radius filter mode is active
let currentChoroplethMetric = 'median_household_income'; // Current metric for choropleth visualization
let legendPanelVisible = false; // Track legend panel visibility

// Layer icon configuration
const LAYER_CONFIGS = {
    crime: {
        name: 'Crime Incidents',
        color: '#e74c3c',
        icon: 'fa-exclamation-triangle',
        bgColor: '#c0392b'
    },
    service_requests: {
        name: '311 Service Requests',
        color: '#3498db',
        icon: 'fa-phone',
        bgColor: '#2980b9'
    },
    businesses: {
        name: 'Businesses',
        color: '#2ecc71',
        icon: 'fa-store',
        bgColor: '#27ae60'
    },
    dangerous_buildings: {
        name: 'Dangerous Buildings',
        color: '#e67e22',
        icon: 'fa-exclamation-circle',
        bgColor: '#d35400'
    },
    inspections: {
        name: 'Food Inspections',
        color: '#f39c12',
        icon: 'fa-utensils',
        bgColor: '#e67e22'
    },
    points: {
        name: 'OSM Points',
        color: '#9b59b6',
        icon: 'fa-map-marker-alt',
        bgColor: '#8e44ad'
    },
    landbank_properties: {
        name: 'Land Bank Properties',
        color: '#FF8C00',
        icon: 'fa-home',
        bgColor: '#FF8C00'
    },
    block_groups: {
        name: 'Block Groups',
        color: '#95a5a6',
        icon: 'fa-border-all',
        bgColor: '#7f8c8d',
        choroplethField: 'median_household_income' // Default choropleth field
    },
    blocks: {
        name: 'Blocks',
        color: '#bdc3c7',
        icon: 'fa-th',
        bgColor: '#95a5a6'
    }
};

// Map configuration
const MAP_CONFIG = {
    center: [38.99, -94.56], // Kansas City GPS coordinates - exact location
    zoom: 18, // More zoomed in for better detail view
    minZoom: 6,
    maxZoom: 20
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeMap();
        loadLayerInfo();
        setupEventListeners();
        
        // Initialize filter panel
        renderFilterPanel();
        
        // Load features immediately
        setTimeout(() => {
            loadVisibleFeatures();
        }, 1000);
        
    } catch (error) {
        console.error('Error during initialization:', error);
    }
});

function initializeMap() {
    // Check if map container exists
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.error('Map container not found!');
        return;
    }
    
    // Create map
    map = L.map('map').setView(MAP_CONFIG.center, MAP_CONFIG.zoom);
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);
    
    // Add zoom controls
    L.control.zoom({
        position: 'topright'
    }).addTo(map);
    
    // Add map event listeners
    map.on('moveend', debounce(handleMapMove, 500));
    map.on('zoomend', debounce(handleMapMove, 500));
    
    // Close popups when clicking on map to make nearby markers clickable
    map.on('click', function() {
        map.closePopup();
    });
    
    // Initialize loaded bounds tracking
    const layerNames = ['points', 'lines', 'multipolygons', 'service_requests', 'crime', 'businesses', 'inspections', 'landbank_properties', 'block_groups', 'blocks'];
    layerNames.forEach(layer => {
        loadedBounds[layer] = [];
    });
    
    // Create ACS legend panel
    createLegendPanel();
}

function setupEventListeners() {
    
    // Layer checkboxes
    document.querySelectorAll('input[type="checkbox"][id^="layer-"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const layerName = this.id.replace('layer-', '');
            
            // Show/hide legend for block groups layer
            if (layerName === 'block_groups') {
                const isChecked = this.checked;
                toggleLegendVisibility(isChecked);
                const metricSelector = document.getElementById('metric-selector');
                if (metricSelector) {
                    metricSelector.style.display = isChecked ? 'block' : 'none';
                }
            }
            
            // Update filter panel when layers change
            renderFilterPanel();
            
            // Clear all layers and reload based on current consolidation state
            clearAllLayers();
            loadVisibleFeatures();
        });
    });
    
            // Metric selector radio buttons
            document.querySelectorAll('input[name="choropleth-metric"]').forEach(radio => {
                radio.addEventListener('change', function() {
                    updateChoroplethMetric(this.value);
                    
                    // Sync variable checkboxes to match radio button selection
                    syncVariableCheckboxes(this.value);
                });
            });
            
            // Variable search toggle button
            const toggleVarSearch = document.getElementById('toggle-variable-search');
            if (toggleVarSearch) {
                toggleVarSearch.addEventListener('click', function() {
                    toggleVariableSearch();
                });
            }
            
            // Variable search input - use delegation
            const variableSearchInput = document.getElementById('variable-search-input');
            if (variableSearchInput) {
                variableSearchInput.addEventListener('input', filterVariables);
            }
    
    // Consolidation toggle
    const consolidateToggle = document.getElementById('consolidate-toggle');
    if (consolidateToggle) {
        consolidateToggle.addEventListener('change', function() {
            consolidationEnabled = this.checked;
            clearAllLayers();
            loadVisibleFeatures();
        });
    }
    
    // Close sidebar button
    const closeSidebarBtn = document.getElementById('close-sidebar');
    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener('click', hideDetailsSidebar);
    }
    
    // Setup filter event listeners
    setupFilterEventListeners();
    
}

function loadLayerInfo() {
    fetch('/api/layers')
        .then(response => {
            return response.json();
        })
        .then(data => {
            updateLayerCounts(data);
            updateStats(data);
        })
        .catch(error => {
        console.error('Error loading layer info:', error);
            updateStats({});
        });
}

function updateLayerCounts(layerData) {
    Object.keys(layerData).forEach(layerName => {
        const countElement = document.getElementById(`count-${layerName}`);
        if (countElement) {
            countElement.textContent = layerData[layerName].count || 0;
        }
    });
}

function updateLayerCountsFromConsolidated(sourceCounts) {
    
    // Update each layer's count from the source_counts metadata
    Object.keys(sourceCounts).forEach(layerName => {
        const countElement = document.getElementById(`count-${layerName}`);
        if (countElement) {
            countElement.textContent = sourceCounts[layerName] || 0;
        }
    });
}

function updateStats(layerData) {
    const statsElement = document.getElementById('stats');
    if (statsElement) {
        const totalFeatures = Object.values(layerData).reduce((sum, layer) => sum + (layer.count || 0), 0);
    statsElement.innerHTML = `
            <span>Total Features: ${totalFeatures.toLocaleString()}</span>
            <span>Layers: ${Object.keys(layerData).length}</span>
        `;
    }
}

function clearAllLayers() {
    Object.keys(layers).forEach(layerName => {
        if (layers[layerName]) {
            map.removeLayer(layers[layerName]);
            delete layers[layerName];
        }
    });
    loadedBounds = {}; // Clear cache to force reload
}

function handleMapMove() {
    
    // If we have a spatial filter, just reapply it to existing markers
    if (spatialFilter) {
        applyRadiusFilter();
        updateMapInfo();
        return;
    }
    
    // No spatial filter - reload data normally
    loadVisibleFeatures();
}

function loadVisibleFeatures(filterValue = null) {
    
    if (!map) {
        console.error('Map not initialized!');
        return;
    }
    
    const bounds = map.getBounds();
    const bbox = [
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth()
    ];

    
    // Update map info
    updateMapInfo(bbox);
    
    // Separate Census layers from others since they need different API endpoints
    const censusLayers = ['block_groups', 'blocks'];
    const otherLayers = ['service_requests', 'crime', 'businesses', 'dangerous_buildings', 'inspections', 'landbank_properties', 'points'];
    
    // Get checked Census layers
    const checkedCensusLayers = [];
    censusLayers.forEach(layerName => {
        const checkbox = document.getElementById(`layer-${layerName}`);
        if (checkbox && checkbox.checked) {
            checkedCensusLayers.push(layerName);
        }
    });
    
    // Get checked other layers
    const checkedOtherLayers = [];
    otherLayers.forEach(layerName => {
        const checkbox = document.getElementById(`layer-${layerName}`);
        if (checkbox && checkbox.checked) {
            checkedOtherLayers.push(layerName);
        }
    });
    
    // Load Census layers directly (they use their own API endpoint)
    if (checkedCensusLayers.length > 0) {
        checkedCensusLayers.forEach(layerName => {
            loadLayerFeatures(layerName, bbox, null);
        });
    }
    
    // If consolidation is enabled, load other layers together
    if (consolidationEnabled && checkedOtherLayers.length > 0) {
        loadCrossLayerFeatures(bbox, checkedOtherLayers);
    } else if (!consolidationEnabled && checkedOtherLayers.length > 0) {
        // Load other features individually without consolidation
        checkedOtherLayers.forEach(layerName => {
            loadLayerFeatures(layerName, bbox, null);
        });
    }
}

function loadCrossLayerFeatures(bbox, layers, filterValue = null) {
    
    // Show loading indicator
    showLoadingIndicator('consolidated');
    
    // Build URL with layers parameter
    let url = `/api/features/consolidated?bbox=${bbox.join(',')}&limit=2000&layers=${layers.join(',')}`;
    
    // Add filter parameters
    const filterParams = new URLSearchParams();
    layers.forEach(layer => {
        const filters = activeFilters[layer];
        if (filters) {
            if (filters.search_text) {
                filterParams.append(`${layer}_search_text`, filters.search_text);
            }
            if (filters.offense_type && filters.offense_type.length > 0) {
                filterParams.append(`${layer}_offense_type`, filters.offense_type.join(','));
            }
            if (filters.issue_type && filters.issue_type.length > 0) {
                filterParams.append(`${layer}_issue_type`, filters.issue_type.join(','));
            }
            if (filters.status && filters.status.length > 0) {
                filterParams.append(`${layer}_status`, filters.status.join(','));
            }
            if (filters.amenity_type && filters.amenity_type.length > 0) {
                filterParams.append(`${layer}_amenity_type`, filters.amenity_type.join(','));
            }
            // Business filters
            if (filters.source && filters.source.length > 0) {
                filterParams.append(`${layer}_source`, filters.source.join(','));
            }
            if (filters.business_type && filters.business_type.length > 0) {
                filterParams.append(`${layer}_business_type`, filters.business_type.join(','));
            }
            if (filters.industry && filters.industry.length > 0) {
                filterParams.append(`${layer}_industry`, filters.industry.join(','));
            }
            // Dangerous buildings filters
            if (filters.status_of_case && filters.status_of_case.length > 0) {
                filterParams.append(`${layer}_status_of_case`, filters.status_of_case.join(','));
            }
            if (filters.council_district && filters.council_district.length > 0) {
                filterParams.append(`${layer}_council_district`, filters.council_district.join(','));
            }
        }
    });
    
    if (filterParams.toString()) {
        url += '&' + filterParams.toString();
    }
    
    
    // Fetch consolidated features
    fetch(url)
        .then(response => {
            return response.json();
        })
        .then(data => {
            if (data.features) {
                addFeaturesToMap('consolidated', data.features);  // Use 'consolidated' as layer name
                
                // FIX: Update individual layer counts from consolidated metadata
                if (data.metadata && data.metadata.source_counts) {
                    updateLayerCountsFromConsolidated(data.metadata.source_counts);
                }
            } else {
            }
            hideLoadingIndicator('consolidated');
        })
        .catch(error => {
            console.error(`Error loading consolidated features:`, error);
            hideLoadingIndicator('consolidated');
        });
}

function loadLayerFeatures(layerName, bbox, filterValue = null) {
    
    // Check if we already have data for this area (but not if filters changed)
    const boundsKey = `${bbox[0]},${bbox[1]},${bbox[2]},${bbox[3]}`;
    const filterKey = JSON.stringify(activeFilters[layerName] || {});
    const cacheKey = `${boundsKey}_${filterKey}`;
    
    if (loadedBounds[layerName] && loadedBounds[layerName].includes(cacheKey)) {
        return;
    }
        
    // Show loading indicator
    showLoadingIndicator(layerName);
    
    // Build URL - use specific API endpoints for different layers
    let url;
    if (layerName === 'businesses') {
        // Use the new business API with filter support
        url = `/api/v1/businesses/?bbox=${bbox.join(',')}&limit=2000`;
        
        // Add filter parameters
        const filters = activeFilters[layerName];
        if (filters) {
            const params = new URLSearchParams();
            if (filters.source && filters.source.length > 0) {
                params.append('source', filters.source.join(','));
            }
            if (filters.business_type && filters.business_type.length > 0) {
                params.append('business_type', filters.business_type.join(','));
            }
            if (filters.industry && filters.industry.length > 0) {
                params.append('industry', filters.industry.join(','));
            }
            if (filters.search_text) {
                params.append('search_text', filters.search_text);
            }
            if (params.toString()) {
                url += '&' + params.toString();
            }
        }
    } else if (layerName === 'dangerous_buildings') {
        // Use the dangerous buildings API
        url = `/api/v1/dangerous_buildings/?bbox=${bbox.join(',')}&limit=2000`;
        
        // Add filter parameters
        const filters = activeFilters[layerName];
        if (filters) {
            const params = new URLSearchParams();
            if (filters.status_of_case && filters.status_of_case.length > 0) {
                params.append('status_of_case', filters.status_of_case.join(','));
            }
            if (filters.council_district && filters.council_district.length > 0) {
                params.append('council_district', filters.council_district.join(','));
            }
            if (filters.search_text) {
                params.append('search_text', filters.search_text);
            }
            if (params.toString()) {
                url += '&' + params.toString();
            }
        }
    } else if (layerName === 'landbank_properties') {
        // Use the Land Bank API
        url = `/api/v1/landbank/properties?bbox=${bbox.join(',')}&limit=2000`;
        
        // Add filter parameters
        const filters = activeFilters[layerName];
        if (filters) {
            const params = new URLSearchParams();
            if (filters.property_status && filters.property_status.length > 0) {
                params.append('property_status', filters.property_status.join(','));
            }
            if (filters.inventory_type && filters.inventory_type.length > 0) {
                params.append('inventory_type', filters.inventory_type.join(','));
            }
            if (filters.neighborhood && filters.neighborhood.length > 0) {
                params.append('neighborhood', filters.neighborhood.join(','));
            }
            if (filters.city_council_district && filters.city_council_district.length > 0) {
                params.append('council_district', filters.city_council_district.join(','));
            }
            if (filters.property_class && filters.property_class.length > 0) {
                params.append('property_class', filters.property_class.join(','));
            }
            if (filters.property_condition && filters.property_condition.length > 0) {
                params.append('property_condition', filters.property_condition.join(','));
            }
            if (filters.demo_needed) {
                params.append('demo_needed', filters.demo_needed);
            }
            if (filters.search) {
                params.append('search', filters.search);
            }
            if (params.toString()) {
                url += '&' + params.toString();
            }
        }
    } else if (layerName === 'block_groups' || layerName === 'blocks') {
        // Use Census API
        url = `/api/v1/census/${layerName}?bbox=${bbox.join(',')}&simplify=20`;
    } else {
        // Use legacy API for other layers
        url = `/api/features/${layerName}?bbox=${bbox.join(',')}&limit=2000`;
        if (consolidationEnabled && ['service_requests', 'crime', 'points'].includes(layerName)) {
            url += '&consolidate=true';
        }
    }
    
    
    // Fetch features
    fetch(url)
        .then(response => {
            return response.json();
        })
        .then(data => {
            if (data.features) {
                addFeaturesToMap(layerName, data.features);
                loadedBounds[layerName] = loadedBounds[layerName] || [];
                loadedBounds[layerName].push(cacheKey);
            } else {
            }
            hideLoadingIndicator(layerName);
        })
        .catch(error => {
            console.error(`Error loading ${layerName} features:`, error);
            hideLoadingIndicator(layerName);
        });
}

function addFeaturesToMap(layerName, features) {
    
    // Remove existing layer if it exists
    if (layers[layerName]) {
        map.removeLayer(layers[layerName]);
    }
    
    // Create new layer
    const layerGroup = L.layerGroup();
    
    features.forEach((feature, index) => {
        if (index < 5) { // Only log first 5 features
        }
        
        const marker = createMarker(feature, layerName);
        if (marker) {
            layerGroup.addLayer(marker);
        }
    });
    
    // Add to map
    layers[layerName] = layerGroup;
    map.addLayer(layerGroup);
    
    // Store features for reference
    currentFeatures[layerName] = features;
}

function createMarker(feature, layerName) {
    
    // Handle polygon features (Census boundaries)
    if (feature.geometry && (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon')) {
        const config = LAYER_CONFIGS[layerName] || LAYER_CONFIGS.block_groups;
        
        // Different styling for block groups vs blocks
        let styleOptions = {
            color: config.color,
            fillColor: config.color,
            fillOpacity: 0.1,
            weight: layerName === 'block_groups' ? 2 : 1,
            opacity: 0.7
        };
        
        // Apply choropleth coloring for block groups with ACS data
        if (layerName === 'block_groups') {
            const metricValue = getMetricValue(feature);
            if (metricValue !== null && metricValue !== undefined) {
                styleOptions.fillColor = getChoroplethColor(metricValue, currentChoroplethMetric);
                styleOptions.fillOpacity = 0.6;
            }
        }
        
        // Create GeoJSON layer for single feature
        const layer = L.geoJSON(feature, {
            style: () => styleOptions,
            onEachFeature: (feature, layer) => {
                // Add enhanced popup with ACS data
                const popupContent = createEnhancedPopup(feature);
                layer.bindPopup(popupContent, {
                    autoClose: false,  // Don't auto-close
                    closeOnClick: false, // Don't close when clicking map
                    maxWidth: 350,
                    className: 'census-popup'
                });
            }
        });
        
        // Return the first layer from the GeoJSON feature
        return layer.getLayers()[0];
    }
    
    const coords = feature.geometry.coordinates;
    const latlng = [coords[1], coords[0]];
    
    
    const isConsolidated = feature.properties.consolidated === true;
    const count = feature.properties.count || 1;
    
    
    // Determine which layer this feature belongs to
    let primaryLayer = layerName;
    if (layerName === 'consolidated' && feature.properties.layers) {
        // For cross-layer consolidated, use the first layer or determine primary
        primaryLayer = feature.properties.layers[0];
    }
    
    // Map database table names to our layer config names
    if (primaryLayer === 'crime_incidents') {
        primaryLayer = 'crime';
    } else if (primaryLayer === 'service_requests_311') {
        primaryLayer = 'service_requests';
    } else if (primaryLayer === 'business_licenses') {
        primaryLayer = 'businesses';
    } else if (primaryLayer === 'dangerous_buildings') {
        primaryLayer = 'dangerous_buildings';
    } else if (primaryLayer === 'food_inspections') {
        primaryLayer = 'inspections';
    } else if (primaryLayer === 'landbank_properties') {
        primaryLayer = 'landbank_properties';
    }
    
    const config = LAYER_CONFIGS[primaryLayer] || LAYER_CONFIGS.points;
    
    // For businesses, differentiate by source
    let markerColor, markerBgColor, markerIcon;
    if (primaryLayer === 'businesses' && feature.properties.source) {
        if (feature.properties.source === 'license') {
            // License data - use blue colors
            markerColor = '#3498db';
            markerBgColor = '#2980b9';
            markerIcon = 'fa-file-alt'; // Document icon for licenses
        } else if (feature.properties.source === 'company') {
            // Company data - use green colors
            markerColor = '#2ecc71';
            markerBgColor = '#27ae60';
            markerIcon = 'fa-building'; // Building icon for companies
        } else {
            // Fallback to default
            markerColor = config.color;
            markerBgColor = config.bgColor;
            markerIcon = config.icon;
        }
    } else if (primaryLayer === 'landbank_properties') {
        // Land Bank properties - color by status
        const status = feature.properties.property_status || 'Unknown';
        if (status.toLowerCase().includes('available')) {
            markerColor = '#32CD32'; // Green
            markerBgColor = '#32CD32';
            markerIcon = 'fa-home';
        } else if (status.toLowerCase().includes('pending')) {
            markerColor = '#FFD700'; // Gold
            markerBgColor = '#FFD700';
            markerIcon = 'fa-home';
        } else if (status.toLowerCase().includes('demolished')) {
            markerColor = '#808080'; // Gray
            markerBgColor = '#808080';
            markerIcon = 'fa-home';
        } else {
            // Default orange for acquired and other statuses
            markerColor = config.color;
            markerBgColor = config.bgColor;
            markerIcon = config.icon;
        }
    } else {
        // Use default layer colors
        markerColor = config.color;
        markerBgColor = config.bgColor;
        markerIcon = config.icon;
    }
    
    // Create icon HTML
    let iconHtml;
    if (isConsolidated && count > 1) {
        // Consolidated marker with count badge
        if (feature.properties.layers && feature.properties.layers.length > 1) {
            // Multi-layer: use mixed icon (fa-layer-group) with multi-color gradient
            iconHtml = `
                <div class="marker-container">
                    <div class="marker-icon multi-layer">
                        <i class="fas fa-layer-group"></i>
                        <span class="marker-count">${count}</span>
            </div>
            </div>
            `;
        } else {
            // Single layer: use layer-specific icon with count
            iconHtml = `
                <div class="marker-container">
                    <div class="marker-icon" style="background-color: ${markerBgColor}; border-color: ${markerColor};">
                        <i class="fas ${markerIcon}" style="color: white;"></i>
                        <span class="marker-count">${count}</span>
            </div>
            </div>
            `;
        }
    } else {
        // Single feature: simple icon without count
        iconHtml = `
            <div class="marker-container">
                <div class="marker-icon single" style="background-color: ${markerBgColor}; border-color: ${markerColor};">
                    <i class="fas ${markerIcon}" style="color: white;"></i>
            </div>
            </div>
        `;
    }
    
    const marker = L.marker(latlng, {
        icon: L.divIcon({
            html: iconHtml,
            className: 'custom-marker',
            iconSize: count > 1 ? [36, 36] : [28, 28],
            iconAnchor: count > 1 ? [18, 18] : [14, 14]
        })
    });
    
    // Store feature data on marker for radius filtering
    marker.feature = feature;
    
    // Add click handler for consolidated features
    if (isConsolidated && count > 1) {
        marker.on('click', function(e) {
            L.DomEvent.stopPropagation(e);
            
            // If radius filter is active, don't override the radius sidebar
            if (radiusFilterActive) {
                return;
            }
            
            // Normal behavior - show details for this marker
            showDetailsSidebar(feature);
        });
    } else {
        // Single feature: show popup
        marker.bindPopup(createPopupContent(feature), {
            maxWidth: 250,
            className: 'feature-popup'
        });
    }
    
    return marker;
}

function showDetailsSidebar(feature) {
    
    const sidebar = document.getElementById('details-sidebar');
    const title = document.getElementById('sidebar-title');
    const content = document.getElementById('sidebar-content');
    
    // Set title
    const address = feature.properties.address || feature.properties.incident_address || 'Location';
    title.textContent = address;
    
    // Build content
    let html = '';
    html += `<div class="location-summary">`;
    html += `<p><strong>${feature.properties.count}</strong> records at this location</p>`;
    if (feature.properties.layers && feature.properties.layers.length > 1) {
        html += `<p>Data from: ${feature.properties.layers.join(', ')}</p>`;
    }
    html += `</div>`;
    
    // Add each entry
    if (feature.properties.entries && feature.properties.entries.length > 0) {
        feature.properties.entries.forEach((entry, index) => {
            html += createEntryCard(entry, index);
        });
    }
    
    content.innerHTML = html;
    
    // Show sidebar
    sidebar.classList.add('open');
    detailsSidebarOpen = true;
    
    // Adjust map container
    document.querySelector('.map-container').classList.add('sidebar-open');
}

function hideDetailsSidebar() {
    const sidebar = document.getElementById('details-sidebar');
    sidebar.classList.remove('open');
    detailsSidebarOpen = false;
    
    // Adjust map container
    document.querySelector('.map-container').classList.remove('sidebar-open');
}

function showRadiusFilteredSidebar(features, radius) {
    
    const sidebar = document.getElementById('details-sidebar');
    const title = document.getElementById('sidebar-title');
    const content = document.getElementById('sidebar-content');
    
    if (!sidebar) {
        console.error('Sidebar element not found!');
        return;
    }
    
    // IMPROVED TITLE FORMAT
    title.textContent = `Within ${radius}m Radius - ${features.length} Records`;
    
    // Build content with better messaging
    let html = '';
    html += `<div class="location-summary radius-mode-summary">`;
    html += `<p><i class="fas fa-bullseye"></i> <strong>Radius Filter Active</strong></p>`;
    html += `<p>Showing <strong>${features.length}</strong> individual records from all markers within ${radius}m</p>`;
    html += `<p class="radius-hint">Adjust slider to change radius. Click "×" on circle button to exit radius mode.</p>`;
    html += `</div>`;
    
    // Group features by layer
    const featuresByLayer = {};
    features.forEach(feature => {
        let layerType = feature.properties.type || 'unknown';
        
        // Map database table names to LAYER_CONFIGS keys
        if (layerType === 'crime_incidents') {
            layerType = 'crime';
        } else if (layerType === 'service_requests_311') {
            layerType = 'service_requests';
        } else if (layerType === 'business_licenses') {
            layerType = 'businesses';
        } else if (layerType === 'food_inspections') {
            layerType = 'inspections';
        } else if (layerType === 'points') {
            layerType = 'points';
        }
        
        if (!featuresByLayer[layerType]) {
            featuresByLayer[layerType] = [];
        }
        featuresByLayer[layerType].push(feature);
    });
    
    // Create entries for each feature
    Object.keys(featuresByLayer).forEach(layerType => {
        const layerFeatures = featuresByLayer[layerType];
        const layerConfig = LAYER_CONFIGS[layerType];
        const icon = layerConfig?.icon || 'fa-circle';
        const color = layerConfig?.color || '#3498db';
        
        html += `<div class="layer-group">`;
        html += `<h4><i class="fas ${icon}" style="color: ${color}"></i> ${layerConfig?.name || layerType} (${layerFeatures.length})</h4>`;
        
        layerFeatures.forEach((feature, index) => {
            html += createEntryCard(feature, index);
        });
        
        html += `</div>`;
    });
    
    content.innerHTML = html;
    
    // Show sidebar
    sidebar.classList.add('open');
    detailsSidebarOpen = true;
    
    const mapContainer = document.querySelector('.map-container');
    if (mapContainer) {
        mapContainer.classList.add('sidebar-open');
    }
}

// Test function to manually open sidebar (for debugging)
function testSidebar() {
    const testFeatures = [
        {
            properties: {
                type: 'service_requests_311',
                address: 'Test Address',
                issue_type: 'Test Issue',
                status: 'Test Status'
            }
        }
    ];
    showRadiusFilteredSidebar(testFeatures, 100);
}

function createEntryCard(entry, index) {
    const props = entry.properties;
    let layerType = props.type;
    
    // Map database table names to our layer config names
    if (layerType === 'crime_incidents') {
        layerType = 'crime';
    } else if (layerType === 'service_requests_311') {
        layerType = 'service_requests';
    } else if (layerType === 'business_licenses' || layerType === 'businesses') {
        layerType = 'businesses';
    } else if (layerType === 'dangerous_buildings') {
        layerType = 'dangerous_buildings';
    } else if (layerType === 'food_inspections') {
        layerType = 'inspections';
    } else if (layerType === 'landbank_properties') {
        layerType = 'landbank_properties';
    }
    
    const config = LAYER_CONFIGS[layerType] || LAYER_CONFIGS.points;
    
    let html = `<div class="entry-card" style="border-left-color: ${config.color};">`;
    html += `<h4>`;
    html += `<i class="fas ${config.icon}" style="color: ${config.color};"></i>`;
    html += `<span class="entry-type" style="background: ${config.color};">${config.name}</span>`;
    html += `</h4>`;
    html += `<dl class="entry-details">`;
    
    // Add layer-specific details
    if (layerType === 'crime') {
        if (props.offense) html += `<dt>Offense:</dt><dd>${props.offense}</dd>`;
        if (props.report) html += `<dt>Report:</dt><dd>${props.report}</dd>`;
        if (props.reported_date) html += `<dt>Date:</dt><dd>${props.reported_date}</dd>`;
        if (props.address) html += `<dt>Address:</dt><dd>${props.address}</dd>`;
    } else if (layerType === 'service_requests') {
        if (props.issue_type) html += `<dt>Issue Type:</dt><dd>${props.issue_type}</dd>`;
        if (props.current_status) html += `<dt>Status:</dt><dd>${props.current_status}</dd>`;
        if (props.request_id) html += `<dt>Request ID:</dt><dd>${props.request_id}</dd>`;
        if (props.incident_address) html += `<dt>Address:</dt><dd>${props.incident_address}</dd>`;
    } else if (layerType === 'businesses') {
        if (props.name) html += `<dt>Business Name:</dt><dd>${props.name}</dd>`;
        if (props.dba_name && props.dba_name !== props.name) html += `<dt>DBA Name:</dt><dd>${props.dba_name}</dd>`;
        if (props.business_type) html += `<dt>Business Type:</dt><dd>${props.business_type}</dd>`;
        if (props.industry) html += `<dt>Industry:</dt><dd>${props.industry}</dd>`;
        if (props.description) html += `<dt>Description:</dt><dd>${props.description}</dd>`;
        if (props.address) html += `<dt>Address:</dt><dd>${props.address}</dd>`;
        if (props.city) html += `<dt>City:</dt><dd>${props.city}</dd>`;
        if (props.state) html += `<dt>State:</dt><dd>${props.state}</dd>`;
        if (props.zipcode) html += `<dt>ZIP Code:</dt><dd>${props.zipcode}</dd>`;
    } else if (layerType === 'dangerous_buildings') {
        if (props.case_number) html += `<dt>Case Number:</dt><dd>${props.case_number}</dd>`;
        if (props.status_of_case) html += `<dt>Status:</dt><dd>${props.status_of_case}</dd>`;
        if (props.case_opened) html += `<dt>Case Opened:</dt><dd>${props.case_opened}</dd>`;
        if (props.address) html += `<dt>Address:</dt><dd>${props.address}</dd>`;
        if (props.city) html += `<dt>City:</dt><dd>${props.city}</dd>`;
        if (props.state) html += `<dt>State:</dt><dd>${props.state}</dd>`;
        if (props.zipcode) html += `<dt>ZIP Code:</dt><dd>${props.zipcode}</dd>`;
        if (props.pin) html += `<dt>PIN:</dt><dd>${props.pin}</dd>`;
        if (props.council_district) html += `<dt>Council District:</dt><dd>${props.council_district}</dd>`;
    } else if (layerType === 'inspections') {
        if (props.establishment_name) html += `<dt>Establishment:</dt><dd>${props.establishment_name}</dd>`;
        if (props.inspection_type) html += `<dt>Inspection:</dt><dd>${props.inspection_type}</dd>`;
        if (props.establishment_address) html += `<dt>Address:</dt><dd>${props.establishment_address}</dd>`;
    } else if (layerType === 'points') {
        if (props.tags && props.tags.name) html += `<dt>Name:</dt><dd>${props.tags.name}</dd>`;
        if (props.tags && props.tags.amenity) html += `<dt>Amenity:</dt><dd>${props.tags.amenity}</dd>`;
        if (props.tags && props.tags.traffic_signals) html += `<dt>Type:</dt><dd>Traffic Signal</dd>`;
        if (props.osm_id) html += `<dt>OSM ID:</dt><dd>${props.osm_id}</dd>`;
    } else if (layerType === 'landbank_properties') {
        if (props.address) html += `<dt>Address:</dt><dd>${props.address}</dd>`;
        if (props.city) html += `<dt>City:</dt><dd>${props.city}</dd>`;
        if (props.state) html += `<dt>State:</dt><dd>${props.state}</dd>`;
        if (props.postal_code) html += `<dt>ZIP Code:</dt><dd>${props.postal_code}</dd>`;
        if (props.property_status) html += `<dt>Status:</dt><dd>${props.property_status}</dd>`;
        if (props.inventory_type) html += `<dt>Inventory Type:</dt><dd>${props.inventory_type}</dd>`;
        if (props.property_class) html += `<dt>Property Class:</dt><dd>${props.property_class}</dd>`;
        if (props.property_condition) html += `<dt>Condition:</dt><dd>${props.property_condition}</dd>`;
        if (props.market_value) html += `<dt>Market Value:</dt><dd>$${props.market_value.toLocaleString()}</dd>`;
        if (props.market_value_year) html += `<dt>Value Year:</dt><dd>${props.market_value_year}</dd>`;
        if (props.square_footage) html += `<dt>Square Footage:</dt><dd>${props.square_footage.toLocaleString()} sq ft</dd>`;
        if (props.neighborhood) html += `<dt>Neighborhood:</dt><dd>${props.neighborhood}</dd>`;
        if (props.city_council_district) html += `<dt>Council District:</dt><dd>${props.city_council_district}</dd>`;
        if (props.date_of_acquisition) html += `<dt>Date Acquired:</dt><dd>${props.date_of_acquisition}</dd>`;
        if (props.demo_needed) html += `<dt>Demo Needed:</dt><dd>${props.demo_needed === 'Y' ? 'Yes' : props.demo_needed === 'N' ? 'No' : 'Unknown'}</dd>`;
        if (props.parcel_number) html += `<dt>Parcel Number:</dt><dd>${props.parcel_number}</dd>`;
    }
    
    html += `</dl></div>`;
    return html;
}

function createPopupContent(feature) {
    const props = feature.properties;
    let layerType = props.type;
    
    // Map database table names to our layer config names
    if (layerType === 'crime_incidents') {
        layerType = 'crime';
    } else if (layerType === 'service_requests_311') {
        layerType = 'service_requests';
    } else if (layerType === 'business_licenses' || layerType === 'businesses') {
        layerType = 'businesses';
    } else if (layerType === 'dangerous_buildings') {
        layerType = 'dangerous_buildings';
    } else if (layerType === 'food_inspections') {
        layerType = 'inspections';
    } else if (layerType === 'landbank_properties') {
        layerType = 'landbank_properties';
    }
    
    const config = LAYER_CONFIGS[layerType] || LAYER_CONFIGS.points;
    
    let html = `<div class="feature-popup-content">`;
    html += `<h4 style="color: ${config.color}; margin: 0 0 8px 0;">`;
    html += `<i class="fas ${config.icon}"></i> ${config.name}`;
    html += `</h4>`;
    
    if (props.address || props.incident_address) {
        html += `<p><strong>${props.address || props.incident_address}</strong></p>`;
    }
    
    // Add key details based on type
    if (layerType === 'crime' && props.offense) {
        html += `<p>${props.offense}</p>`;
    } else if (layerType === 'service_requests' && props.issue_type) {
        html += `<p>${props.issue_type}</p>`;
    } else if (layerType === 'businesses') {
        if (props.name) {
            html += `<p><strong>${props.name}</strong></p>`;
        }
        if (props.business_type) {
            html += `<p>Type: ${props.business_type}</p>`;
        }
        if (props.industry) {
            html += `<p>Industry: ${props.industry}</p>`;
        }
        if (props.source) {
            const sourceLabel = props.source === 'license' ? 'Business License' : 'Company Directory';
            html += `<p><small>Source: ${sourceLabel}</small></p>`;
        }
    } else if (layerType === 'landbank_properties') {
        if (props.property_status) {
            html += `<p><strong>Status: ${props.property_status}</strong></p>`;
        }
        if (props.inventory_type) {
            html += `<p>Type: ${props.inventory_type}</p>`;
        }
        if (props.property_class) {
            html += `<p>Class: ${props.property_class}</p>`;
        }
        if (props.market_value) {
            html += `<p>Value: $${props.market_value.toLocaleString()}</p>`;
        }
        if (props.neighborhood) {
            html += `<p>Neighborhood: ${props.neighborhood}</p>`;
        }
    }
    
    html += `</div>`;
    return html;
}

function showLayer(layerName) {
    if (layers[layerName]) {
        map.addLayer(layers[layerName]);
    } else {
        loadVisibleFeatures();
    }
}

function hideLayer(layerName) {
    if (layers[layerName]) {
        map.removeLayer(layers[layerName]);
    }
}

function clearAllLayers() {
    Object.keys(layers).forEach(layerName => {
        if (layers[layerName]) {
            map.removeLayer(layers[layerName]);
        }
    });
    layers = {};
    currentFeatures = {};
    loadedBounds = {};
}

function showLoadingIndicator(layerName) {
    const countElement = document.getElementById(`count-${layerName}`);
    if (countElement) {
        countElement.textContent = '...';
    }
}

function hideLoadingIndicator(layerName) {
    // Count will be updated when data loads
}

function updateMapInfo(bbox) {
    const zoomElement = document.getElementById('map-zoom');
    const featuresElement = document.getElementById('map-features');
    const boundsElement = document.getElementById('map-bounds');
    
    if (zoomElement) {
        zoomElement.textContent = map.getZoom();
    }
    
    if (featuresElement) {
        // Count visible features (opacity > 0)
        let visibleCount = 0;
        Object.values(layers).forEach(layer => {
            layer.eachLayer(marker => {
                if (marker.options.opacity > 0) {
                    visibleCount++;
                }
            });
        });
        
        // Check if any filters are active
        const hasFilters = spatialFilter || Object.keys(activeFilters).some(k => 
            Object.keys(activeFilters[k]).some(key => 
                key === 'search_text' ? activeFilters[k][key] : activeFilters[k][key]?.length > 0
            )
        );
        
        if (hasFilters) {
            featuresElement.textContent = `${visibleCount} (filtered)`;
        } else {
            featuresElement.textContent = visibleCount;
        }
    }
    
    if (boundsElement && bbox) {
        boundsElement.textContent = `${bbox[0].toFixed(4)}, ${bbox[1].toFixed(4)}, ${bbox[2].toFixed(4)}, ${bbox[3].toFixed(4)}`;
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Filter Panel Functions
function renderFilterPanel() {
    const checkedLayers = getCheckedLayers();
    let html = '<div class="filter-panel">';
    
    if (checkedLayers.length === 0) {
        html += '<p style="color: #666; font-style: italic;">Check layers to see filter options</p>';
    } else {
        checkedLayers.forEach(layer => {
            html += `<div class="filter-section" data-layer="${layer}">`;
            html += `<h4>${LAYER_CONFIGS[layer].name} Filters</h4>`;
            html += buildLayerFilters(layer);
            html += `</div>`;
        });
    }
    
    html += '</div>';
    document.getElementById('filter-container').innerHTML = html;
    
    // Load filter options for service_requests, crime, and businesses layers
    checkedLayers.forEach(layer => {
        if (layer === 'service_requests' || layer === 'crime' || layer === 'businesses') {
            loadFilterOptions(layer);
        }
    });
}

function getCheckedLayers() {
    const layerNames = ['service_requests', 'crime', 'businesses', 'inspections', 'points'];
    return layerNames.filter(layerName => {
        const checkbox = document.getElementById(`layer-${layerName}`);
        return checkbox && checkbox.checked;
    });
}

function buildLayerFilters(layer) {
    let html = '';
    
    // Show filters for service_requests, crime, and businesses layers
    if (layer === 'service_requests' || layer === 'crime' || layer === 'businesses') {
        // Text search (common to all layers)
        html += `
            <div class="filter-group">
                <label>Search</label>
                <input type="text" 
                       id="filter-${layer}-search" 
                       placeholder="Search addresses, names..."
                       class="filter-search"
                       value="${activeFilters[layer]?.search_text || ''}">
                </div>
        `;
        
        // Category filters (layer-specific)
        if (layer === 'crime') {
            html += buildMultiSelect('offense_type', 'Offense Type', layer);
        } else if (layer === 'service_requests') {
            html += buildMultiSelect('issue_type', 'Issue Type', layer);
            // Removed status filter as requested
        } else if (layer === 'businesses') {
            // Source filter to distinguish between license and company data
            html += buildMultiSelect('source', 'Data Source', layer);
            html += buildMultiSelect('business_type', 'Business Type', layer);
            html += buildMultiSelect('industry', 'Industry', layer);
            
            // Add legend for business markers
            html += `
                <div class="filter-group">
                    <label>Marker Legend</label>
                    <div style="display: flex; gap: 15px; margin-top: 5px; font-size: 12px;">
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <div style="width: 12px; height: 12px; background-color: #2980b9; border: 2px solid #3498db; border-radius: 50%;"></div>
                            <span>License Data</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <div style="width: 12px; height: 12px; background-color: #27ae60; border: 2px solid #2ecc71; border-radius: 50%;"></div>
                            <span>Company Data</span>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    return html;
}

function buildMultiSelect(field, label, layer) {
    return `
        <div class="filter-group">
            <label>${label}</label>
            <select id="filter-${layer}-${field}" 
                    multiple 
                    class="filter-select">
                <!-- Options loaded from API -->
            </select>
            </div>
    `;
}

async function loadFilterOptions(layer) {
    try {
        const response = await fetch(`/api/filters/${layer}`);
        const data = await response.json();
        
        if (data.filters) {
            // Wait a tick to ensure DOM is ready
            setTimeout(() => {
                data.filters.forEach(filter => {
                    populateFilterSelect(layer, filter.field, filter.options);
                });
            }, 100);
        }
    } catch (error) {
        console.error(`Error loading filter options for ${layer}:`, error);
    }
}

function populateFilterSelect(layer, field, options) {
    const select = document.getElementById(`filter-${layer}-${field}`);
    if (!select) return;
    
    // Clear existing options
    select.innerHTML = '';
    
    // Add options
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        select.appendChild(option);
    });
    
    // Set selected values if they exist in activeFilters
    if (activeFilters[layer] && activeFilters[layer][field]) {
        const selectedValues = Array.isArray(activeFilters[layer][field]) 
            ? activeFilters[layer][field] 
            : [activeFilters[layer][field]];
        
        Array.from(select.options).forEach(option => {
            if (selectedValues.includes(option.value)) {
                option.selected = true;
            }
        });
    }
}

function updateFiltersAndReload() {
    
    // Read current filter values from UI
    document.querySelectorAll('.filter-section').forEach(section => {
        const layer = section.dataset.layer;
        if (!activeFilters[layer]) {
            activeFilters[layer] = {};
        }
        
        // Read search text
        const searchInput = document.getElementById(`filter-${layer}-search`);
        if (searchInput) {
            activeFilters[layer].search_text = searchInput.value;
        }
        
        // Read multi-select values
        const selects = section.querySelectorAll('.filter-select');
        selects.forEach(select => {
            const field = select.id.replace(`filter-${layer}-`, '');
            const selectedValues = Array.from(select.selectedOptions).map(opt => opt.value);
            activeFilters[layer][field] = selectedValues.length > 0 ? selectedValues : null;
        });
    });
    
    
    // Update filter indicators
    updateFilterIndicator();
    updateActiveFiltersSummary();
    
    // Clear layer cache for businesses when filters change
    if (activeFilters.businesses) {
        loadedBounds.businesses = [];
    }
    
    // Reload map with new filters
    clearAllLayers();
    loadVisibleFeatures();
}

function updateFilterIndicator() {
    let activeCount = 0;
    Object.values(activeFilters).forEach(filters => {
        if (filters.search_text) activeCount++;
        Object.keys(filters).forEach(key => {
            if (key !== 'search_text' && filters[key]?.length > 0) {
                activeCount++;
            }
        });
    });
    
    // Add spatial filter count
    if (spatialFilter) {
        activeCount++;
    }
    
    const indicator = document.getElementById('filter-indicator');
    if (activeCount > 0) {
        indicator.textContent = activeCount;
        indicator.style.display = 'inline-block';
    } else {
        indicator.style.display = 'none';
    }
}

function updateActiveFiltersSummary() {
    const summaryDiv = document.getElementById('active-filters-summary');
    const listDiv = document.getElementById('active-filters-list');
    let filtersHtml = '';
    let hasFilters = false;
    
    // Add spatial filter
    if (spatialFilter) {
        hasFilters = true;
        filtersHtml += `
            <div class="filter-tag">
                <i class="fas fa-circle"></i>
                ${spatialFilter.radius}m radius
                <button onclick="clearSpatialFilter()" class="filter-remove">×</button>
            </div>
        `;
    }
    
    // Add layer filters
    Object.keys(activeFilters).forEach(layer => {
        const filters = activeFilters[layer];
        
        if (filters.search_text) {
            hasFilters = true;
            filtersHtml += `
                <div class="filter-tag">
                    <i class="fas fa-search"></i>
                    "${filters.search_text}"
                    <button onclick="clearLayerSearchFilter('${layer}')" class="filter-remove">×</button>
                </div>
            `;
        }
        
        Object.keys(filters).forEach(key => {
            if (key !== 'search_text' && filters[key]?.length > 0) {
                hasFilters = true;
                const count = filters[key].length;
                filtersHtml += `
                    <div class="filter-tag">
                        ${key}: ${count} selected
                        <button onclick="clearLayerCategoryFilter('${layer}', '${key}')" class="filter-remove">×</button>
                    </div>
                `;
            }
        });
    });
    
    if (hasFilters) {
        listDiv.innerHTML = filtersHtml;
        summaryDiv.style.display = 'block';
    } else {
        summaryDiv.style.display = 'none';
    }
}

function clearAllFiltersComplete() {
    // Clear attribute filters
    activeFilters = {};
    
    // Clear spatial filter
    if (spatialFilter) {
        clearSpatialFilter();
    }
    
    // Reset UI
    renderFilterPanel();
    updateActiveFiltersSummary();
    updateFilterIndicator();
    
    // Reload all data
    clearAllLayers();
    loadVisibleFeatures();
}

// Helper functions for removing individual filters
function clearLayerSearchFilter(layer) {
    if (activeFilters[layer]) {
        activeFilters[layer].search_text = '';
        const searchInput = document.getElementById(`filter-${layer}-search`);
        if (searchInput) searchInput.value = '';
        updateFiltersAndReload();
    }
}

function clearLayerCategoryFilter(layer, field) {
    if (activeFilters[layer]) {
        activeFilters[layer][field] = null;
        const select = document.getElementById(`filter-${layer}-${field}`);
        if (select) {
            Array.from(select.options).forEach(option => option.selected = false);
        }
        updateFiltersAndReload();
    }
}

// Spatial Filter Functions
function enableCircleDraw() {
    map.getContainer().style.cursor = 'crosshair';
    
    // Calculate appropriate default radius based on current zoom
    const bounds = map.getBounds();
    const mapWidthMeters = bounds.getNorthEast().distanceTo(bounds.getNorthWest());
    const defaultRadius = Math.min(Math.round(mapWidthMeters / 10), 1000); // 10% of view or 1km max
    
    // Single click to set center
    map.once('click', function(e) {
        const center = e.latlng;
        
        // Create visible circle with appropriate radius
        const circle = L.circle(center, {
            radius: defaultRadius,
            color: '#3498db',
            fillColor: '#3498db',
            fillOpacity: 0.15,
            weight: 3
        }).addTo(map);
        
        // Add radius control
        addRadiusSlider(circle, defaultRadius);
        
        // Store as active filter
        spatialFilter = {
            type: 'circle',
            center: [center.lat, center.lng],
            radius: defaultRadius,
            layer: circle
        };
        
        // SET RADIUS MODE ACTIVE
        radiusFilterActive = true;
        
        // Show radius mode badge
        const badge = document.getElementById('radius-mode-badge');
        if (badge) badge.style.display = 'block';
        
        // Update button state
        document.getElementById('draw-circle-btn').classList.add('active');
        
        // Apply filter and show sidebar immediately
        applyRadiusFilter();
    });
}

function addRadiusSlider(circle, initialRadius) {
    const maxRadius = Math.min(5000, initialRadius * 10); // Max 10x initial or 5km
    
    const sliderHtml = `
        <div class="radius-control">
            <label>Radius: <span id="radius-value">${initialRadius}</span>m</label>
            <input type="range" 
                   id="radius-slider" 
                   min="50" 
                   max="${maxRadius}" 
                   step="50" 
                   value="${initialRadius}">
            <div class="radius-hint">Drag slider to adjust</div>
        </div>
    `;
    
    circle.bindPopup(sliderHtml, {
        closeButton: false,
        autoClose: false,
        closeOnClick: false
    }).openPopup();
    
    // Debounce filter updates for performance
    let filterTimeout;
    
    // Update circle on slider change (real-time visual feedback)
    setTimeout(() => {
        const slider = document.getElementById('radius-slider');
        if (slider) {
            slider.addEventListener('input', function(e) {
                const radius = parseInt(e.target.value);
                circle.setRadius(radius);
                spatialFilter.radius = radius;
                document.getElementById('radius-value').textContent = radius;
                
                // Debounce the actual filtering for performance
                clearTimeout(filterTimeout);
                filterTimeout = setTimeout(() => {
                    applyRadiusFilter();
                }, 300);  // 300ms delay
            });
        }
    }, 100);
}

function applyRadiusFilter() {
    if (!spatialFilter) {
        // No filter - show all markers, remove all classes
        Object.values(layers).forEach(layer => {
            layer.eachLayer(marker => {
                marker.setOpacity(1);
                if (marker._icon) {
                    marker._icon.classList.remove('within-radius', 'outside-radius');
                }
            });
        });
        hideDetailsSidebar();
        radiusFilterActive = false;
        return;
    }
    
    const center = L.latLng(spatialFilter.center[0], spatialFilter.center[1]);
    const radius = spatialFilter.radius;
    
    let visibleCount = 0;
    let hiddenCount = 0;
    let visibleFeatures = [];
    
    // Filter each layer's markers and collect visible features
    Object.values(layers).forEach(layer => {
        layer.eachLayer(marker => {
            const markerPos = marker.getLatLng();
            const distance = center.distanceTo(markerPos);
            
            if (distance <= radius) {
                marker.setOpacity(1);
                visibleCount++;
                
                // Add visual highlight
                if (marker._icon) {
                    marker._icon.classList.add('within-radius');
                    marker._icon.classList.remove('outside-radius');
                }
                
                // Collect feature data for sidebar
                if (marker.feature) {
                    // Check if this is a consolidated marker with individual records
                    if (marker.feature.properties.entries && Array.isArray(marker.feature.properties.entries)) {
                        // This is a consolidated marker - add all individual entries
                        marker.feature.properties.entries.forEach(entry => {
                            visibleFeatures.push(entry);
                        });
    } else {
                        // This is a single feature - add it directly
                        visibleFeatures.push(marker.feature);
                    }
                }
            } else {
                marker.setOpacity(0);
                hiddenCount++;
                
                // Add dim visual
                if (marker._icon) {
                    marker._icon.classList.add('outside-radius');
                    marker._icon.classList.remove('within-radius');
                }
            }
        });
    });
    
    
    // AUTO-OPEN AND UPDATE SIDEBAR
    if (visibleFeatures.length > 0) {
        showRadiusFilteredSidebar(visibleFeatures, radius);
    } else {
        hideDetailsSidebar();
    }
    
    updateMapInfo();
}

function clearSpatialFilter() {
    if (spatialFilter && spatialFilter.layer) {
        map.removeLayer(spatialFilter.layer);
    }
    spatialFilter = null;
    
    // CLEAR RADIUS MODE
    radiusFilterActive = false;
    
    // Hide radius mode badge
    const badge = document.getElementById('radius-mode-badge');
    if (badge) badge.style.display = 'none';
    
    map.getContainer().style.cursor = '';
    document.getElementById('draw-circle-btn').classList.remove('active');
    
    // Show all markers again and remove visual classes
    Object.values(layers).forEach(layer => {
        layer.eachLayer(marker => {
            marker.setOpacity(1);
            // Remove radius highlight
            if (marker._icon) {
                marker._icon.classList.remove('within-radius', 'outside-radius');
            }
        });
    });
    
    // Close sidebar
    hideDetailsSidebar();
    
    updateMapInfo();
    updateFilterIndicator();
    updateActiveFiltersSummary();
}

function setupFilterEventListeners() {
    
    // Text search with debounce
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('filter-search')) {
            clearTimeout(searchDebounce);
            searchDebounce = setTimeout(() => {
                updateFiltersAndReload();
            }, 500);
        }
    });
    
    // Category select changes
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('filter-select')) {
            updateFiltersAndReload();
        }
    });
    
    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            clearAllFiltersComplete();
        });
    }
    
    // Spatial filter tools
    const drawCircleBtn = document.getElementById('draw-circle-btn');
    if (drawCircleBtn) {
        drawCircleBtn.addEventListener('click', () => {
            enableCircleDraw();
        });
    }
    
    const clearSpatialBtn = document.getElementById('clear-spatial-filter');
    if (clearSpatialBtn) {
        clearSpatialBtn.addEventListener('click', () => {
            clearSpatialFilter();
        });
    }
    
    // Settings functionality
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', openSettings);
    }
    
    // Load consolidation settings on init
    loadConsolidationSettings();
}

// ==================== SIDEBAR FUNCTIONALITY ====================

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mapContainer = document.querySelector('.map-container');
    
    if (sidebar && mapContainer) {
        sidebar.classList.toggle('collapsed');
        mapContainer.classList.toggle('sidebar-collapsed');
    }
}

// ==================== SETTINGS FUNCTIONALITY ====================

let consolidationSettings = {
    enabled: true,
    strategy: 'hybrid',
    address_tolerance: 0.00005,
    coordinate_precision: 3,
    min_records_to_consolidate: 2
};

function openSettings() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.style.display = 'flex';
        loadSettingsIntoUI();
    }
}

function closeSettings() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.style.display = 'none';
    } else {
        console.error('Settings modal not found');
    }
}

function loadSettingsIntoUI() {
    
    // Set preset based on current settings
    const preset = determinePreset();
    const presetRadio = document.getElementById(`preset-${preset}`);
    if (presetRadio) {
        presetRadio.checked = true;
    }
    
    // Update custom settings visibility
    const customSettings = document.getElementById('custom-settings');
    if (customSettings) {
        customSettings.style.display = preset === 'custom' ? 'block' : 'none';
    }
    
    // Set custom values
    const addressTolerance = document.getElementById('address-tolerance');
    const coordinatePrecision = document.getElementById('coordinate-precision');
    const minRecords = document.getElementById('min-records');
    const consolidationEnabled = document.getElementById('consolidation-enabled');
    
    if (addressTolerance) {
        addressTolerance.value = consolidationSettings.address_tolerance;
        updateSettingValue('address-tolerance-value', consolidationSettings.address_tolerance);
    }
    
    if (coordinatePrecision) {
        coordinatePrecision.value = consolidationSettings.coordinate_precision;
        updateSettingValue('coordinate-precision-value', consolidationSettings.coordinate_precision);
    }
    
    if (minRecords) {
        minRecords.value = consolidationSettings.min_records_to_consolidate;
        updateSettingValue('min-records-value', consolidationSettings.min_records_to_consolidate);
    }
    
    if (consolidationEnabled) {
        consolidationEnabled.checked = consolidationSettings.enabled;
    }
    
    // Add event listeners for preset changes
    document.querySelectorAll('input[name="preset"]').forEach(radio => {
        radio.addEventListener('change', handlePresetChange);
    });
    
    // Add event listeners for custom sliders
    if (addressTolerance) {
        addressTolerance.addEventListener('input', (e) => {
            updateSettingValue('address-tolerance-value', e.target.value);
        });
    }
    
    if (coordinatePrecision) {
        coordinatePrecision.addEventListener('input', (e) => {
            updateSettingValue('coordinate-precision-value', e.target.value);
        });
    }
    
    if (minRecords) {
        minRecords.addEventListener('input', (e) => {
            updateSettingValue('min-records-value', e.target.value);
        });
    }
}

function determinePreset() {
    const settings = consolidationSettings;
    
    // Check for aggressive preset
    if (settings.address_tolerance === 0.001 && 
        settings.coordinate_precision === 3 && 
        settings.min_records_to_consolidate === 3) {
        return 'aggressive';
    }
    
    // Check for balanced preset
    if (settings.address_tolerance === 0.0005 && 
        settings.coordinate_precision === 4 && 
        settings.min_records_to_consolidate === 4) {
        return 'balanced';
    }
    
    // Check for loose preset
    if (settings.address_tolerance === 0.0002 && 
        settings.coordinate_precision === 5 && 
        settings.min_records_to_consolidate === 5) {
        return 'loose';
    }
    
    // Otherwise it's custom
    return 'custom';
}

function handlePresetChange(event) {
    const preset = event.target.value;
    
    const customSettings = document.getElementById('custom-settings');
    
    if (preset === 'custom') {
        customSettings.style.display = 'block';
        return;
    }
    
    customSettings.style.display = 'none';
    
    // Apply preset values
    const presetValues = {
        aggressive: { address_tolerance: 0.0001, coordinate_precision: 2, min_records: 1 },
        balanced: { address_tolerance: 0.00005, coordinate_precision: 3, min_records: 2 },
        loose: { address_tolerance: 0.00001, coordinate_precision: 4, min_records: 3 }
    };
    
    const values = presetValues[preset];
    if (values) {
        updateSettingValue('address-tolerance-value', values.address_tolerance);
        updateSettingValue('coordinate-precision-value', values.coordinate_precision);
        updateSettingValue('min-records-value', values.min_records);
        
        // Update sliders
        const addressTolerance = document.getElementById('address-tolerance');
        const coordinatePrecision = document.getElementById('coordinate-precision');
        const minRecords = document.getElementById('min-records');
        
        if (addressTolerance) addressTolerance.value = values.address_tolerance;
        if (coordinatePrecision) coordinatePrecision.value = values.coordinate_precision;
        if (minRecords) minRecords.value = values.min_records;
    }
}

function updateSettingValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

function applySettings() {
    
    try {
        // Get current values from UI
        const presetElement = document.querySelector('input[name="preset"]:checked');
        if (!presetElement) {
            console.error('No preset selected');
            alert('Please select a consolidation preset');
            return;
        }
        const preset = presetElement.value;
        const consolidationEnabled = document.getElementById('consolidation-enabled').checked;
    
    let settings = {
        enabled: consolidationEnabled,
        strategy: 'hybrid'
    };
    
    
    if (preset === 'custom') {
        settings.address_tolerance = parseFloat(document.getElementById('address-tolerance').value);
        settings.coordinate_precision = parseInt(document.getElementById('coordinate-precision').value);
        settings.min_records_to_consolidate = parseInt(document.getElementById('min-records').value);
    } else {
    const presetValues = {
        aggressive: { address_tolerance: 0.001, coordinate_precision: 3, min_records_to_consolidate: 3 },
        balanced: { address_tolerance: 0.0005, coordinate_precision: 4, min_records_to_consolidate: 4 },
        loose: { address_tolerance: 0.0002, coordinate_precision: 5, min_records_to_consolidate: 5 }
    };
        
        settings = { ...settings, ...presetValues[preset] };
    }
    
    
    // Update global settings
    consolidationSettings = settings;
    
    // Save to localStorage
    localStorage.setItem('consolidationSettings', JSON.stringify(settings));
    
    // Apply settings to backend
    updateBackendSettings(settings);
    
    // Reload current data with new settings
    reloadCurrentData();
    
    // Close modal
    closeSettings();
    
    } catch (error) {
        console.error('Error applying settings:', error);
        alert('Error applying settings: ' + error.message);
    }
}

function resetSettings() {
    
    // Reset to balanced preset
    consolidationSettings = {
        enabled: true,
        strategy: 'hybrid',
        address_tolerance: 0.00005,
        coordinate_precision: 3,
        min_records_to_consolidate: 2
    };
    
    // Update UI
    loadSettingsIntoUI();
    
    // Save to localStorage
    localStorage.setItem('consolidationSettings', JSON.stringify(consolidationSettings));
    
}

function loadConsolidationSettings() {
    
    try {
        const saved = localStorage.getItem('consolidationSettings');
        if (saved) {
            consolidationSettings = { ...consolidationSettings, ...JSON.parse(saved) };
        }
    } catch (e) {
        console.error('Error loading consolidation settings:', e);
    }
    
    // Apply settings to backend
    updateBackendSettings(consolidationSettings);
}

function updateBackendSettings(settings) {
    
    // Send settings to backend API
    fetch('/api/settings/consolidation', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
    })
    .catch(error => {
        console.error('Error updating backend settings:', error);
    });
}

function reloadCurrentData() {
    
    // Clear current features
    clearAllLayers();
    
    // Clear loaded bounds to force reload
    loadedBounds = {};
    
    // Reload current view
    const bounds = map.getBounds();
    const bbox = [
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth()
    ];
    
    // Get enabled layers
    const enabledLayers = getCheckedLayers();
    
    if (enabledLayers.length > 0) {
        if (consolidationEnabled) {
            loadCrossLayerFeatures(bbox, enabledLayers);
        } else {
            enabledLayers.forEach(layer => {
                loadLayerFeatures(layer, bbox);
            });
        }
    }
}

// Variable Search Functionality
const VARIABLE_DEFINITIONS = {
    'population': { label: 'Population', icon: '👥', type: 'number' },
    'median_household_income': { label: 'Median Household Income', icon: '💰', type: 'currency' },
    'median_age': { label: 'Median Age', icon: '📅', type: 'number' },
    'youth_pct': { label: 'Youth % (<18)', icon: '👶', type: 'percent' },
    'seniors_pct': { label: 'Seniors % (65+)', icon: '👴', type: 'percent' },
    'housing_occupied': { label: 'Housing Occupied', icon: '🏠', type: 'number' },
    'homeownership_rate': { label: 'Homeownership Rate', icon: '🏡', type: 'percent' },
    'median_home_value': { label: 'Median Home Value', icon: '💵', type: 'currency' },
    'median_rent': { label: 'Median Rent', icon: '🏘️', type: 'currency' },
    'bachelors_plus_pct': { label: 'Bachelor\'s Degree+', icon: '🎓', type: 'percent' },
    'employment_rate': { label: 'Employment Rate', icon: '💼', type: 'percent' },
    'unemployment_rate': { label: 'Unemployment Rate', icon: '📉', type: 'percent' },
    'remote_work_pct': { label: 'Work from Home %', icon: '🏢', type: 'percent' },
    'transit_pct': { label: 'Public Transit %', icon: '🚌', type: 'percent' },
    // Vehicle Availability
    'no_vehicles': { label: 'Households w/ No Vehicles', icon: '🚫', type: 'number' },
    'one_vehicle': { label: 'Households w/ One Vehicle', icon: '🚗', type: 'number' },
    'two_vehicles': { label: 'Households w/ Two Vehicles', icon: '🚙', type: 'number' },
    'three_vehicles': { label: 'Households w/ Three Vehicles', icon: '🚕', type: 'number' },
    // Income Brackets (key ones for mapping)
    'income_75000_99999': { label: 'Income $75K-$100K', icon: '💵', type: 'number' },
    'income_100000_124999': { label: 'Income $100K-$125K', icon: '💰', type: 'number' },
    'income_150000_199999': { label: 'Income $150K-$200K', icon: '💸', type: 'number' },
};

let variableSearchVisible = false;

function toggleVariableSearch() {
    const searchDiv = document.getElementById('variable-search');
    if (!searchDiv) {
        console.error('variable-search element not found');
        return;
    }
    
    variableSearchVisible = !variableSearchVisible;
    
    if (variableSearchVisible) {
        searchDiv.style.display = 'block';
        populateVariableList();
    } else {
        searchDiv.style.display = 'none';
    }
}

function populateVariableList() {
    const listDiv = document.getElementById('variable-list');
    if (!listDiv) {
        console.error('variable-list element not found');
        return;
    }
    
    listDiv.innerHTML = '';
    
    // Get available variables from first feature if any block groups loaded
    let availableVars = [];
    if (currentFeatures && currentFeatures.block_groups && currentFeatures.block_groups.features && currentFeatures.block_groups.features.length > 0) {
        availableVars = Object.keys(currentFeatures.block_groups.features[0].properties);
    }
    
    Object.keys(VARIABLE_DEFINITIONS).forEach(varName => {
        const def = VARIABLE_DEFINITIONS[varName];
        const hasData = availableVars.length === 0 || availableVars.includes(varName);
        
        const item = document.createElement('div');
        item.className = 'variable-item';
        const checkboxId = `var-${varName}`;
        item.innerHTML = `
            <label>
                <input type="checkbox" class="variable-checkbox" id="${checkboxId}" data-variable="${varName}">
                <span>${def.icon} ${def.label}</span>
            </label>
        `;
        listDiv.appendChild(item);
        
        // Add event listener to checkbox
        const checkbox = document.getElementById(checkboxId);
        if (checkbox) {
            checkbox.addEventListener('change', handleVariableCheckbox);
        }
    });
}

function filterVariables(e) {
    if (!e || !e.target) return;
    
    const searchTerm = e.target.value.toLowerCase();
    const items = document.querySelectorAll('.variable-item');
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
}

// Handle variable checkbox selection - single selection only (radio-like behavior)
function handleVariableCheckbox(e) {
    const variable = e.target.dataset.variable;
    
    if (e.target.checked) {
        // Uncheck all other checkboxes in the variable list
        const allCheckboxes = document.querySelectorAll('.variable-list input[type="checkbox"]');
        allCheckboxes.forEach(cb => {
            if (cb !== e.target) {
                cb.checked = false;
            }
        });
        
        // Update choropleth if this variable is mappable
        if (['population', 'median_household_income', 'median_age', 'youth_pct', 'seniors_pct', 
             'housing_occupied', 'homeownership_rate', 'bachelors_plus_pct', 
             'employment_rate', 'remote_work_pct'].includes(variable)) {
            currentChoroplethMetric = variable;
            updateChoroplethMetric(variable);
            
            // Also update the radio button selection to match
            const radio = document.querySelector(`input[name="choropleth-metric"][value="${variable}"]`);
            if (radio) {
                radio.checked = true;
            }
        }
    } else {
        // If unchecking, set to 'none'
        currentChoroplethMetric = 'none';
        updateChoroplethMetric('none');
        
        // Also update the radio button to 'none'
        const noneRadio = document.querySelector(`input[name="choropleth-metric"][value="none"]`);
        if (noneRadio) {
            noneRadio.checked = true;
        }
    }
}

// Sync variable checkboxes to match radio button selection
function syncVariableCheckboxes(metric) {
    const allCheckboxes = document.querySelectorAll('.variable-list input[type="checkbox"]');
    
    // Uncheck all first
    allCheckboxes.forEach(cb => {
        cb.checked = false;
    });
    
    // Check the matching checkbox if the metric is in the variable list
    const matchingCheckbox = document.querySelector(`.variable-list input[type="checkbox"][data-variable="${metric}"]`);
    if (matchingCheckbox) {
        matchingCheckbox.checked = true;
    }
}

// Make functions globally available
window.openSettings = openSettings;
window.closeSettings = closeSettings;
window.applySettings = applySettings;
window.resetSettings = resetSettings;

// ============================================
// ACS Data Visualization Helper Functions
// ============================================

/**
 * Get color for choropleth based on value and metric
 */
function getChoroplethColor(value, metric) {
    if (value === null || value === undefined || isNaN(value)) {
        return '#f7f7f7'; // Gray for no data
    }
    
    switch(metric) {
        case 'median_household_income':
            // Green scale for income (higher = darker green)
            if (value >= 150000) return '#005a32'; // Dark green
            if (value >= 100000) return '#238b45'; // Green
            if (value >= 75000) return '#41ab5d'; // Light green
            if (value >= 50000) return '#74c476'; // Lighter green
            if (value >= 25000) return '#addd8e'; // Very light green
            if (value > 0) return '#d9f0a3'; // Pale green
            return '#f7f7f7'; // Gray
            
        case 'median_age':
            // Purple scale for age (older = darker)
            if (value >= 60) return '#54278f';
            if (value >= 50) return '#756bb1';
            if (value >= 40) return '#9e9ac8';
            if (value >= 30) return '#bcbddc';
            if (value >= 20) return '#dadaeb';
            if (value > 0) return '#f2f0f7';
            return '#f7f7f7';
            
        case 'population':
            // Blue scale for population density
            if (value >= 2000) return '#08306b'; // Dark blue
            if (value >= 1500) return '#08519c'; // Blue
            if (value >= 1000) return '#2171b5'; // Light blue
            if (value >= 500) return '#4292c6'; // Lighter blue
            if (value >= 250) return '#6baed6'; // Very light blue
            if (value > 0) return '#c6dbef'; // Pale blue
            return '#f7f7f7'; // Gray
            
        case 'youth_pct':
            // Orange scale for youth percentage (higher = darker orange)
            if (value >= 40) return '#cc4c02';
            if (value >= 30) return '#fe9929';
            if (value >= 20) return '#feb24c';
            if (value >= 10) return '#fed976';
            if (value > 0) return '#fff7bc';
            return '#f7f7f7';
            
        case 'seniors_pct':
            // Brown scale for seniors (higher = darker brown)
            if (value >= 30) return '#8c510a';
            if (value >= 20) return '#bf812d';
            if (value >= 15) return '#dfc27d';
            if (value >= 10) return '#f6e8c3';
            if (value > 0) return '#fef7ed';
            return '#f7f7f7';
            
        case 'housing_occupied':
            // Yellow scale for housing (higher = darker yellow)
            if (value >= 500) return '#7f4e00';
            if (value >= 400) return '#a06100';
            if (value >= 300) return '#c17f02';
            if (value >= 200) return '#e29e02';
            if (value >= 100) return '#f5b301';
            if (value > 0) return '#fbd582';
            return '#f7f7f7';
            
        case 'homeownership_rate':
            // Teal scale for homeownership (higher = darker teal)
            if (value >= 90) return '#00441b';
            if (value >= 80) return '#006d2c';
            if (value >= 70) return '#238b45';
            if (value >= 60) return '#41ae76';
            if (value >= 50) return '#66c2a4';
            if (value > 0) return '#99d8c9';
            return '#f7f7f7';
            
        case 'bachelors_plus_pct':
            // Blue-green scale for education (higher = darker)
            if (value >= 60) return '#006d2c';
            if (value >= 50) return '#238b45';
            if (value >= 40) return '#41ae76';
            if (value >= 30) return '#66c2a4';
            if (value >= 20) return '#99d8c9';
            if (value > 0) return '#cce5df';
            return '#f7f7f7';
            
        case 'employment_rate':
            // Green scale for employment (higher = darker green)
            if (value >= 95) return '#005a32';
            if (value >= 90) return '#238b45';
            if (value >= 85) return '#41ab5d';
            if (value >= 80) return '#74c476';
            if (value >= 75) return '#addd8e';
            if (value > 0) return '#d9f0a3';
            return '#f7f7f7';
            
        case 'remote_work_pct':
            // Cyan scale for remote work (higher = darker cyan)
            if (value >= 40) return '#00474e';
            if (value >= 30) return '#016c61';
            if (value >= 20) return '#02818a';
            if (value >= 10) return '#43a2ca';
            if (value >= 5) return '#7bccc4';
            if (value > 0) return '#bae4e3';
            return '#f7f7f7';
            
        default:
            return '#95a5a6'; // Default gray
    }
}

/**
 * Format number based on type
 */
function formatNumber(num, type) {
    // Handle nullable pandas types (Int64) and normal numbers
    if (num === null || num === undefined || num === 'Int64' || num === 'Float64' || isNaN(num)) {
        return 'N/A';
    }
    
    // Convert to number if it's a string
    const numValue = typeof num === 'string' ? parseFloat(num) : num;
    
    if (isNaN(numValue)) {
        return 'N/A';
    }
    
    switch(type) {
        case 'currency':
            return '$' + numValue.toLocaleString('en-US');
        case 'percent':
            return (numValue * 100).toFixed(1) + '%';
        case 'number':
        default:
            return numValue.toLocaleString('en-US');
    }
}

/**
 * Create enhanced popup content with ACS data
 */
function createEnhancedPopup(feature) {
    const props = feature.properties;
    let content = '<div class="census-popup">';
    
    // Helper to safely convert to number
    const toNumber = (val) => {
        // Handle edge cases
        if (val === null || val === undefined || val === 'Int64' || val === 'Float64') return null;
        
        // If it's a string, try to parse it
        if (typeof val === 'string') {
            const num = parseFloat(val);
            return isNaN(num) ? null : num;
        }
        
        // If it's already a number, return it (unless NaN)
        return isNaN(val) ? null : val;
    };
    
    // Header
    content += `<strong>${props.name || 'Block Group ' + props.geoid}</strong><br>`;
    content += `GEOID: ${props.geoid}<br>`;
    
    // ACS Data Section
    const population = toNumber(props.population);
    const hasAnyData = population !== null && population !== undefined && population > 0;
    
    if (hasAnyData) {
        content += '<hr>';
        content += `<strong>📊 Demographics (ACS ${props.acs_year || 'N/A'})</strong><br>`;
        
        // Population
        content += `👥 Population: ${formatNumber(population, 'number')}<br>`;
        
        // Income
        const income = toNumber(props.median_household_income);
        if (income !== null && income !== undefined && income > 0) {
            content += `💰 Median Household Income: ${formatNumber(income, 'currency')}<br>`;
        }
        
        // Age Distribution
        const medianAge = toNumber(props.median_age);
        if (medianAge !== null && medianAge !== undefined) {
            content += `📅 Median Age: ${medianAge.toFixed(1)} years<br>`;
        }
        
        // Race/Ethnicity
        const white = toNumber(props.white_alone);
        const black = toNumber(props.black_alone);
        const hispanic = toNumber(props.hispanic_latino);
        const total = toNumber(props.total_race) || population;
        
        if (white || black || hispanic) {
            content += '<hr><strong>🔍 Race/Ethnicity:</strong><br>';
            
            if (white) {
                const pct = total > 0 ? Math.round((white / total) * 100) : 0;
                content += `• White: ${formatNumber(white, 'number')} (${pct}%)<br>`;
            }
            if (black) {
                const pct = total > 0 ? Math.round((black / total) * 100) : 0;
                content += `• Black: ${formatNumber(black, 'number')} (${pct}%)<br>`;
            }
            if (hispanic) {
                const pct = total > 0 ? Math.round((hispanic / total) * 100) : 0;
                content += `• Hispanic/Latino: ${formatNumber(hispanic, 'number')} (${pct}%)<br>`;
            }
        }
        
        // Housing
        const housingOccupied = toNumber(props.housing_occupied);
        const ownerOccupied = toNumber(props.owner_occupied);
        const renterOccupied = toNumber(props.renter_occupied);
        const medianHomeValue = toNumber(props.median_home_value);
        const medianRent = toNumber(props.median_rent);
        
        if (housingOccupied || ownerOccupied || renterOccupied) {
            content += '<hr><strong>🏠 Housing:</strong><br>';
            if (housingOccupied) content += `Occupied: ${formatNumber(housingOccupied, 'number')}<br>`;
            if (ownerOccupied && renterOccupied) {
                const homeownershipPct = Math.round((ownerOccupied / (ownerOccupied + renterOccupied)) * 100);
                content += `Ownership: ${homeownershipPct}% owner, ${100-homeownershipPct}% renter<br>`;
            }
            if (medianHomeValue) content += `Median Home Value: ${formatNumber(medianHomeValue, 'currency')}<br>`;
            if (medianRent) content += `Median Rent: ${formatNumber(medianRent, 'currency')}/mo<br>`;
        }
        
        // Education
        const bachelors = toNumber(props.bachelors_degree);
        const educationUniverse = toNumber(props.education_universe);
        if (bachelors && educationUniverse && educationUniverse > 0) {
            const bachelorsPct = Math.round((bachelors / educationUniverse) * 100);
            content += `<hr><strong>🎓 Education:</strong><br>`;
            content += `Bachelor's Degree+: ${bachelorsPct}%<br>`;
        }
        
        // Employment
        const employed = toNumber(props.employed);
        const inLaborForce = toNumber(props.in_labor_force);
        if (employed && inLaborForce && inLaborForce > 0) {
            const employmentRate = Math.round((employed / inLaborForce) * 100);
            content += `<hr><strong>💼 Employment:</strong><br>`;
            content += `Employment Rate: ${employmentRate}%<br>`;
        }
        
        // Commute
        const workFromHome = toNumber(props.work_from_home);
        const commuteUniverse = toNumber(props.commute_universe);
        if (workFromHome && commuteUniverse && commuteUniverse > 0) {
            const remotePct = Math.round((workFromHome / commuteUniverse) * 100);
            content += `<hr><strong>🚗 Commute:</strong><br>`;
            content += `Work from Home: ${remotePct}%<br>`;
        }
    } else {
        content += '<hr><em>No demographic data available</em><br>';
    }
    
    content += '</div>';
    return content;
}

/**
 * Get the value from feature properties based on current metric
 */
function getMetricValue(feature) {
    const props = feature.properties;
    
    // Helper to convert value to number
    const toNumber = (val) => {
        if (val === null || val === undefined || val === 'Int64' || val === 'Float64') return null;
        const num = typeof val === 'string' ? parseFloat(val) : val;
        return isNaN(num) ? null : num;
    };
    
    switch(currentChoroplethMetric) {
        case 'median_household_income':
            return toNumber(props.median_household_income);
        case 'population':
            return toNumber(props.population);
        case 'median_age':
            return toNumber(props.median_age);
        case 'youth_pct':
            return toNumber(props.youth_pct);
        case 'seniors_pct':
            return toNumber(props.seniors_pct);
        case 'housing_occupied':
            return toNumber(props.housing_occupied);
        case 'homeownership_rate':
            return toNumber(props.homeownership_rate);
        case 'bachelors_plus_pct':
            return toNumber(props.bachelors_plus_pct);
        case 'employment_rate':
            return toNumber(props.employment_rate);
        case 'remote_work_pct':
            return toNumber(props.remote_work_pct);
        default:
            return null;
    }
}

/**
 * Update choropleth metric and re-style visible block groups
 */
function updateChoroplethMetric(metric) {
    currentChoroplethMetric = metric;
    
    // Update legend title
    updateLegendTitle(metric);
    
    // Re-style all visible block groups
    if (layers.block_groups && currentFeatures.block_groups) {
        layers.block_groups.eachLayer(layer => {
            const feature = layer.feature;
            if (feature) {
                const metricValue = getMetricValue(feature);
                const color = getChoroplethColor(metricValue, metric);
                
                layer.setStyle({
                    fillColor: color,
                    fillOpacity: 0.6
                });
            }
        });
    }
}

/**
 * Create legend panel in bottom-left
 */
function createLegendPanel() {
    const legendContainer = document.createElement('div');
    legendContainer.id = 'acs-legend-panel';
    legendContainer.className = 'acs-legend-panel';
    legendContainer.style.display = 'none'; // Hidden by default
    
    const header = document.createElement('div');
    header.className = 'legend-header';
    header.innerHTML = `
        <span>📊 <span id="legend-title">Poverty Rate</span></span>
        <button class="toggle-legend" onclick="toggleLegendPanel()">▼</button>
    `;
    
    const content = document.createElement('div');
    content.className = 'legend-content';
    content.id = 'legend-content';
    
    // Add legend items (will be updated based on metric)
    updateLegendContent(content);
    
    legendContainer.appendChild(header);
    legendContainer.appendChild(content);
    
    // Add to map container
    document.getElementById('map').appendChild(legendContainer);
}

/**
 * Update legend content based on current metric
 */
function updateLegendContent(contentDiv) {
    let items = '';
    
    if (currentChoroplethMetric === 'median_household_income') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #005a32"></span>
                <span class="legend-label">≥$150k</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #238b45"></span>
                <span class="legend-label">$100-150k</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #41ab5d"></span>
                <span class="legend-label">$75-100k</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #74c476"></span>
                <span class="legend-label">$50-75k</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #addd8e"></span>
                <span class="legend-label">$25-50k</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #d9f0a3"></span>
                <span class="legend-label">&lt;$25k</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'population') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #08306b"></span>
                <span class="legend-label">≥2,000</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #08519c"></span>
                <span class="legend-label">1,500-2,000</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #2171b5"></span>
                <span class="legend-label">1,000-1,500</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #4292c6"></span>
                <span class="legend-label">500-1,000</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #6baed6"></span>
                <span class="legend-label">250-500</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #c6dbef"></span>
                <span class="legend-label">&lt;250</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'median_age') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #54278f"></span>
                <span class="legend-label">≥60 years</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #756bb1"></span>
                <span class="legend-label">50-60 years</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #9e9ac8"></span>
                <span class="legend-label">40-50 years</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #bcbddc"></span>
                <span class="legend-label">30-40 years</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #dadaeb"></span>
                <span class="legend-label">20-30 years</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f2f0f7"></span>
                <span class="legend-label">&lt;20 years</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'youth_pct') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #cc4c02"></span>
                <span class="legend-label">≥40%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #fe9929"></span>
                <span class="legend-label">30-40%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #feb24c"></span>
                <span class="legend-label">20-30%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #fed976"></span>
                <span class="legend-label">10-20%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #fff7bc"></span>
                <span class="legend-label">&lt;10%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'seniors_pct') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #8c510a"></span>
                <span class="legend-label">≥30%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #bf812d"></span>
                <span class="legend-label">20-30%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #dfc27d"></span>
                <span class="legend-label">15-20%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f6e8c3"></span>
                <span class="legend-label">10-15%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #fef7ed"></span>
                <span class="legend-label">&lt;10%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'housing_occupied') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #7f4e00"></span>
                <span class="legend-label">≥500</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #a06100"></span>
                <span class="legend-label">400-500</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #c17f02"></span>
                <span class="legend-label">300-400</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #e29e02"></span>
                <span class="legend-label">200-300</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f5b301"></span>
                <span class="legend-label">100-200</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #fbd582"></span>
                <span class="legend-label">&lt;100</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'homeownership_rate') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #00441b"></span>
                <span class="legend-label">≥90%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #006d2c"></span>
                <span class="legend-label">80-90%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #238b45"></span>
                <span class="legend-label">70-80%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #41ae76"></span>
                <span class="legend-label">60-70%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #66c2a4"></span>
                <span class="legend-label">50-60%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #99d8c9"></span>
                <span class="legend-label">&lt;50%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'bachelors_plus_pct') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #006d2c"></span>
                <span class="legend-label">≥60%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #238b45"></span>
                <span class="legend-label">50-60%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #41ae76"></span>
                <span class="legend-label">40-50%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #66c2a4"></span>
                <span class="legend-label">30-40%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #99d8c9"></span>
                <span class="legend-label">20-30%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #cce5df"></span>
                <span class="legend-label">&lt;20%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'employment_rate') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #005a32"></span>
                <span class="legend-label">≥95%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #238b45"></span>
                <span class="legend-label">90-95%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #41ab5d"></span>
                <span class="legend-label">85-90%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #74c476"></span>
                <span class="legend-label">80-85%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #addd8e"></span>
                <span class="legend-label">75-80%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #d9f0a3"></span>
                <span class="legend-label">&lt;75%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'remote_work_pct') {
        items = `
            <div class="legend-item">
                <span class="legend-color" style="background: #00474e"></span>
                <span class="legend-label">≥40%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #016c61"></span>
                <span class="legend-label">30-40%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #02818a"></span>
                <span class="legend-label">20-30%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #43a2ca"></span>
                <span class="legend-label">10-20%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #7bccc4"></span>
                <span class="legend-label">5-10%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #bae4e3"></span>
                <span class="legend-label">&lt;5%</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f7f7f7"></span>
                <span class="legend-label">No data</span>
            </div>
        `;
    } else if (currentChoroplethMetric === 'none') {
        items = '<div class="legend-item"><span class="legend-label">Choropleth disabled</span></div>';
    } else {
        // Generic legend for other metrics
        items = `<div class="legend-item"><span class="legend-label">Darker = Higher values</span></div>
        <div class="legend-item"><span class="legend-color" style="background: #f7f7f7"></span>
        <span class="legend-label">No data</span></div>`;
    }
    
    contentDiv.innerHTML = items;
}

/**
 * Update legend title based on metric
 */
function updateLegendTitle(metric) {
    const titles = {
        'median_household_income': 'Median Household Income',
        'population': 'Population',
        'median_age': 'Median Age',
        'youth_pct': 'Youth % (<18)',
        'seniors_pct': 'Seniors % (65+)',
        'housing_occupied': 'Housing Occupied',
        'homeownership_rate': 'Homeownership Rate',
        'bachelors_plus_pct': 'Bachelor\'s Degree+',
        'employment_rate': 'Employment Rate',
        'remote_work_pct': 'Work from Home %',
        'none': 'None'
    };
    
    const titleElement = document.getElementById('legend-title');
    if (titleElement) {
        titleElement.textContent = titles[metric] || 'Metric';
    }
    
    // Update content
    const contentDiv = document.getElementById('legend-content');
    if (contentDiv) {
        updateLegendContent(contentDiv);
    }
}

/**
 * Toggle legend panel visibility
 */
function toggleLegendPanel() {
    const panel = document.getElementById('acs-legend-panel');
    const content = document.getElementById('legend-content');
    const button = panel.querySelector('.toggle-legend');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        button.textContent = '▼';
    } else {
        content.style.display = 'none';
        button.textContent = '▶';
    }
}

/**
 * Show/hide legend panel based on block groups layer state
 */
function toggleLegendVisibility(isVisible) {
    const panel = document.getElementById('acs-legend-panel');
    if (panel) {
        panel.style.display = isVisible ? 'block' : 'none';
        legendPanelVisible = isVisible;
    }
}

// Make functions globally available
window.toggleLegendPanel = toggleLegendPanel;
