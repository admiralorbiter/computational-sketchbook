/**
 * Block Group Analysis View
 */

// Global state
let map;
let blockGroupsLayer;
let selectedBlockGroup = null;
let analysisData = null;
let charts = {};
let panelExpanded = false;
let activeTab = 'overview';

// Map configuration
const MAP_CONFIG = {
    center: [38.99, -94.56],
    zoom: 12,
    minZoom: 10,
    maxZoom: 20
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    setupMapListeners();
});

function initializeMap() {
    // Create map
    map = L.map('map', {
        center: MAP_CONFIG.center,
        zoom: MAP_CONFIG.zoom,
        minZoom: MAP_CONFIG.minZoom,
        maxZoom: MAP_CONFIG.maxZoom
    });

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Load block groups on map move
    map.on('moveend', function() {
        loadBlockGroups();
    });

    // Initial load
    loadBlockGroups();
}

function setupMapListeners() {
    // Handle clicks for deselecting
    map.on('click', function() {
        // Optionally deselect when clicking map
    });
}

function loadBlockGroups() {
    const bounds = map.getBounds();
    const bbox = [
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth()
    ].join(',');

    const simplify = 20; // Reduce complexity for better performance
    const url = `/api/v1/census/block_groups?bbox=${bbox}&simplify=${simplify}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.features) {
                renderBlockGroups(data.features);
            }
        })
        .catch(error => {
            console.error('Error loading block groups:', error);
        });
}

function renderBlockGroups(features) {
    if (blockGroupsLayer) {
        map.removeLayer(blockGroupsLayer);
    }

    blockGroupsLayer = L.geoJSON(features, {
        style: getBlockGroupStyle,
        onEachFeature: onEachBlockGroup
    }).addTo(map);
}

function getBlockGroupStyle(feature) {
    const isSelected = selectedBlockGroup === feature.properties.geoid;
    
    return {
        fillColor: isSelected ? '#e74c3c' : getChoroplethColor(feature),
        fillOpacity: isSelected ? 0.8 : 0.3,
        color: '#2c3e50',
        weight: isSelected ? 3 : 1,
        opacity: isSelected ? 1 : 0.8
    };
}

function getChoroplethColor(feature) {
    // Default color scheme - can be customized
    const income = feature.properties.B19013_001E;
    
    if (!income || income <= 0) {
        return '#bdc3c7';
    }
    
    // Color scale based on median household income
    if (income < 30000) return '#c0392b';
    if (income < 45000) return '#e67e22';
    if (income < 60000) return '#f39c12';
    if (income < 80000) return '#27ae60';
    return '#2ecc71';
}

function onEachBlockGroup(feature, layer) {
    layer.on({
        click: function(e) {
            L.DomEvent.stopPropagation(e);
            selectBlockGroup(feature.properties.geoid, feature);
        },
        mouseover: function(e) {
            e.target.setStyle({
                weight: 2,
                fillOpacity: 0.5
            });
        },
        mouseout: function(e) {
            e.target.setStyle(getBlockGroupStyle(feature));
        }
    });
}

function selectBlockGroup(geoid, feature) {
    selectedBlockGroup = geoid;
    
    // Highlight selected block group
    blockGroupsLayer.eachLayer(function(layer) {
        const bgGeoid = layer.feature.properties.geoid;
        if (bgGeoid === geoid) {
            layer.setStyle({
                fillColor: '#e74c3c',
                fillOpacity: 0.8,
                weight: 3,
                opacity: 1
            });
        } else {
            layer.setStyle({
                fillColor: getChoroplethColor(layer.feature),
                fillOpacity: 0.3,
                weight: 1,
                opacity: 0.8
            });
        }
    });
    
    // Fetch and display analysis
    fetchBlockGroupAnalysis(geoid);
}

function fetchBlockGroupAnalysis(geoid) {
    showLoadingState();
    
    fetch(`/api/v1/analysis/block_groups/${geoid}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            
            analysisData = data;
            renderAnalysisPanel(data);
        })
        .catch(error => {
            console.error('Error fetching analysis:', error);
            showError('Failed to load analysis data');
        });
}

function showLoadingState() {
    document.getElementById('panel-content').innerHTML = `
        <div class="loading-state">
            <i class="fas fa-spinner"></i>
            <p>Loading analysis data...</p>
        </div>
    `;
    document.getElementById('panel-content').classList.add('active');
}

function showError(message) {
    document.getElementById('panel-content').innerHTML = `
        <div class="error-state">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
    document.getElementById('panel-content').classList.add('active');
}

function renderAnalysisPanel(data) {
    // Destroy existing charts
    Object.values(charts).forEach(chart => {
        if (chart) chart.destroy();
    });
    charts = {};
    
    // Expand panel
    expandAnalysisPanel();
    
    const html = `
        <div class="panel-header-expanded">
            <button class="back-btn" onclick="collapseAnalysisPanel()">
                <i class="fas fa-arrow-left"></i> Back to Map
            </button>
            <div class="block-group-header">
                <h3>${data.name || 'Block Group'}</h3>
                <div class="block-group-id">${data.geoid}</div>
            </div>
        </div>
        
        <div class="analysis-tabs">
            <button class="tab-btn ${activeTab === 'overview' ? 'active' : ''}" data-tab="overview" onclick="switchTab('overview')">
                <i class="fas fa-chart-pie"></i> Overview
            </button>
            <button class="tab-btn ${activeTab === 'demographics' ? 'active' : ''}" data-tab="demographics" onclick="switchTab('demographics')">
                <i class="fas fa-users"></i> Demographics
            </button>
            <button class="tab-btn ${activeTab === 'housing' ? 'active' : ''}" data-tab="housing" onclick="switchTab('housing')">
                <i class="fas fa-home"></i> Housing
            </button>
            <button class="tab-btn ${activeTab === 'economic' ? 'active' : ''}" data-tab="economic" onclick="switchTab('economic')">
                <i class="fas fa-money-bill-wave"></i> Economic
            </button>
            <button class="tab-btn ${activeTab === 'social-health' ? 'active' : ''}" data-tab="social-health" onclick="switchTab('social-health')">
                <i class="fas fa-heart"></i> Social & Health
            </button>
            <button class="tab-btn ${activeTab === 'technology' ? 'active' : ''}" data-tab="technology" onclick="switchTab('technology')">
                <i class="fas fa-laptop"></i> Technology & Access
            </button>
            <button class="tab-btn ${activeTab === 'crime' ? 'active' : ''}" data-tab="crime" onclick="switchTab('crime')">
                <i class="fas fa-exclamation-triangle"></i> Crime
            </button>
            <button class="tab-btn ${activeTab === '311' ? 'active' : ''}" data-tab="311" onclick="switchTab('311')">
                <i class="fas fa-phone"></i> 311 Requests
            </button>
            <button class="tab-btn ${activeTab === 'businesses' ? 'active' : ''}" data-tab="businesses" onclick="switchTab('businesses')">
                <i class="fas fa-store"></i> Businesses
            </button>
        </div>
        
        <div class="tab-content active" id="tab-content-overview">
            ${renderOverviewTab(data)}
        </div>
        <div class="tab-content" id="tab-content-demographics">
            ${renderDemographicsTab(data.acs)}
        </div>
        <div class="tab-content" id="tab-content-housing">
            ${renderHousingTab(data.acs)}
        </div>
        <div class="tab-content" id="tab-content-economic">
            ${renderEconomicTab(data.acs, data.employment)}
        </div>
        <div class="tab-content" id="tab-content-social-health">
            ${renderSocialHealthTab(data.acs)}
        </div>
        <div class="tab-content" id="tab-content-technology">
            ${renderTechnologyTab(data.acs)}
        </div>
        <div class="tab-content" id="tab-content-crime">
            ${renderCrimeTab(data.aggregations)}
        </div>
        <div class="tab-content" id="tab-content-311">
            ${render311Tab(data.aggregations)}
        </div>
        <div class="tab-content" id="tab-content-businesses">
            ${renderBusinessTab(data.aggregations)}
        </div>
    `;
    
    document.getElementById('panel-content').innerHTML = html;
    document.getElementById('panel-content').classList.add('active');
    
    // Render charts after a brief delay to ensure DOM is ready
    setTimeout(() => {
        renderCharts(data);
        showActiveTab();
    }, 100);
}

const tabNames = {
    'overview': 'Overview',
    'demographics': 'Demographics',
    'housing': 'Housing',
    'economic': 'Economic',
    'social-health': 'Social & Health',
    'technology': 'Technology & Access',
    'crime': 'Crime',
    '311': '311 Requests',
    'businesses': 'Businesses'
};

function expandAnalysisPanel() {
    panelExpanded = true;
    document.querySelector('.analysis-container').classList.add('expanded');
}

function collapseAnalysisPanel() {
    panelExpanded = false;
    document.querySelector('.analysis-container').classList.remove('expanded');
    
    // Clear selection
    selectedBlockGroup = null;
    blockGroupsLayer.eachLayer(function(layer) {
        const bgGeoid = layer.feature.properties.geoid;
        layer.setStyle({
            fillColor: getChoroplethColor(layer.feature),
            fillOpacity: 0.3,
            weight: 1,
            opacity: 0.8
        });
    });
    
    document.getElementById('panel-content').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-mouse-pointer fa-3x"></i>
            <p>Select a block group on the map to begin</p>
        </div>
    `;
}

function switchTab(tabName) {
    activeTab = tabName;
    showActiveTab();
}

function showActiveTab() {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === activeTab) {
            btn.classList.add('active');
        }
    });
    
    // Show/hide tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const activeContent = document.getElementById(`tab-content-${activeTab}`);
    if (activeContent) {
        activeContent.classList.add('active');
    }
    
    // Re-render charts if needed
    if (analysisData) {
        setTimeout(() => {
            renderCharts(analysisData);
        }, 50);
    }
}

// Tab rendering functions
function renderOverviewTab(data) {
    const agg = data.aggregations;
    return `
        <div class="data-section">
            <h4><i class="fas fa-chart-bar"></i> Quick Stats</h4>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon" style="background: #e74c3c;">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="stat-details">
                        <div class="stat-label">Population</div>
                        <div class="stat-value">${data.acs?.population?.toLocaleString() || 'N/A'}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: #3498db;">
                        <i class="fas fa-dollar-sign"></i>
                    </div>
                    <div class="stat-details">
                        <div class="stat-label">Median Income</div>
                        <div class="stat-value">${formatCurrency(data.acs?.median_household_income)}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: #e67e22;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="stat-details">
                        <div class="stat-label">Crime Incidents</div>
                        <div class="stat-value">${agg?.crime_total || 0}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: #2ecc71;">
                        <i class="fas fa-phone"></i>
                    </div>
                    <div class="stat-details">
                        <div class="stat-label">311 Requests</div>
                        <div class="stat-value">${agg?.sr_total || 0}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: #9b59b6;">
                        <i class="fas fa-store"></i>
                    </div>
                    <div class="stat-details">
                        <div class="stat-label">Businesses</div>
                        <div class="stat-value">${agg?.businesses_total || 0}</div>
                    </div>
                </div>
            </div>
        </div>
        ${renderACSDemographics(data.acs)}
        ${renderCrimeSection(agg)}
        ${render311Section(agg)}
        ${renderBusinessSection(agg)}
    `;
}

function renderDemographicsTab(acs) {
    if (!acs) {
        return '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No demographic data available</p></div>';
    }
    
    const youthCount = (acs.male_under_18 || 0) + (acs.female_under_18 || 0);
    const workingAgeCount = (acs.male_18_64 || 0) + (acs.female_18_64 || 0);
    const seniorsCount = (acs.male_65_plus || 0) + (acs.female_65_plus || 0);
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-users"></i> Basic Demographics</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Total Population', acs.population?.toLocaleString())}
                ${renderDemographicItemLarge('Median Household Income', formatCurrency(acs.median_household_income))}
                ${renderDemographicItemLarge('Median Age', acs.median_age?.toFixed(1) + ' years')}
                ${renderDemographicItemLarge('Poverty Rate', formatPercent(acs.poverty_rate))}
            </div>
        </div>
        
        <div class="data-section">
            <h4><i class="fas fa-child"></i> Age Distribution</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Under 18 (Youth)', youthCount.toLocaleString())}
                ${renderDemographicItemLarge('18-64 (Working Age)', workingAgeCount.toLocaleString())}
                ${renderDemographicItemLarge('65+ (Seniors)', seniorsCount.toLocaleString())}
            </div>
            <div class="chart-container">
                <canvas id="age-chart"></canvas>
            </div>
        </div>
        
        <div class="data-section">
            <h4><i class="fas fa-user-friends"></i> Detailed Age by Sex</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Male Under 18', acs.male_under_18?.toLocaleString())}
                ${renderDemographicItemLarge('Female Under 18', acs.female_under_18?.toLocaleString())}
                ${renderDemographicItemLarge('Male 18-64', acs.male_18_64?.toLocaleString())}
                ${renderDemographicItemLarge('Female 18-64', acs.female_18_64?.toLocaleString())}
                ${renderDemographicItemLarge('Male 65+', acs.male_65_plus?.toLocaleString())}
                ${renderDemographicItemLarge('Female 65+', acs.female_65_plus?.toLocaleString())}
            </div>
        </div>
        
        <div class="data-section">
            <h4><i class="fas fa-flag"></i> Race & Ethnicity</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('White Alone', acs.white_alone?.toLocaleString())}
                ${renderDemographicItemLarge('Black Alone', acs.black_alone?.toLocaleString())}
                ${renderDemographicItemLarge('Hispanic/Latino', acs.hispanic_latino?.toLocaleString())}
            </div>
            <div class="chart-container">
                <canvas id="race-chart"></canvas>
            </div>
        </div>
        
        ${acs.asian_alone !== undefined || acs.american_indian_alone !== undefined ? `
        <div class="data-section">
            <h4><i class="fas fa-globe-americas"></i> Detailed Race & Ethnicity</h4>
            <div class="demographics-grid-full">
                ${acs.american_indian_alone !== undefined ? renderDemographicItemLarge('American Indian Alone', acs.american_indian_alone?.toLocaleString()) : ''}
                ${acs.asian_alone !== undefined ? renderDemographicItemLarge('Asian Alone', acs.asian_alone?.toLocaleString()) : ''}
                ${acs.native_hawaiian_pi_alone !== undefined ? renderDemographicItemLarge('Native Hawaiian/PI Alone', acs.native_hawaiian_pi_alone?.toLocaleString()) : ''}
                ${acs.some_other_race_alone !== undefined ? renderDemographicItemLarge('Some Other Race Alone', acs.some_other_race_alone?.toLocaleString()) : ''}
                ${acs.two_or_more_races !== undefined ? renderDemographicItemLarge('Two or More Races', acs.two_or_more_races?.toLocaleString()) : ''}
            </div>
        </div>
        ` : ''}
    `;
}

function renderHousingTab(acs) {
    if (!acs) {
        return '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No housing data available</p></div>';
    }
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-home"></i> Housing Characteristics</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Total Housing Units', acs.total_housing_units?.toLocaleString())}
                ${renderDemographicItemLarge('Occupied', acs.housing_occupied?.toLocaleString())}
                ${renderDemographicItemLarge('Vacant', acs.housing_vacant?.toLocaleString())}
                ${renderDemographicItemLarge('Owner Occupied', acs.owner_occupied?.toLocaleString())}
                ${renderDemographicItemLarge('Renter Occupied', acs.renter_occupied?.toLocaleString())}
                ${renderDemographicItemLarge('Homeownership Rate', formatPercent(acs.homeownership_rate))}
                ${renderDemographicItemLarge('Vacancy Rate', formatPercent(acs.vacancy_rate))}
                ${renderDemographicItemLarge('Median Home Value', formatCurrency(acs.median_home_value))}
                ${renderDemographicItemLarge('Median Rent', formatCurrency(acs.median_rent))}
            </div>
        </div>
        
        <div class="data-section">
            <h4><i class="fas fa-building"></i> Housing Year Built</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('2014 or Later', acs.built_2014_later?.toLocaleString())}
                ${renderDemographicItemLarge('2010-2013', acs.built_2010_2013?.toLocaleString())}
                ${renderDemographicItemLarge('2000-2009', acs.built_2000_2009?.toLocaleString())}
                ${renderDemographicItemLarge('1990-1999', acs.built_1990_1999?.toLocaleString())}
                ${renderDemographicItemLarge('1980-1989', acs.built_1980_1989?.toLocaleString())}
                ${renderDemographicItemLarge('1970-1979', acs.built_1970_1979?.toLocaleString())}
                ${renderDemographicItemLarge('1960-1969', acs.built_1960_1969?.toLocaleString())}
                ${renderDemographicItemLarge('1950-1959', acs.built_1950_1959?.toLocaleString())}
                ${renderDemographicItemLarge('1940-1949', acs.built_1940_1949?.toLocaleString())}
                ${renderDemographicItemLarge('1939 or Earlier', acs.built_1939_or_earlier?.toLocaleString())}
            </div>
        </div>
        
        <div class="data-section">
            <h4><i class="fas fa-home"></i> Housing Unit Types</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Single Unit Detached', acs.single_unit_detached?.toLocaleString())}
                ${renderDemographicItemLarge('Single Unit Attached', acs.single_unit_attached?.toLocaleString())}
                ${renderDemographicItemLarge('2-4 Units', acs.units_2_4?.toLocaleString())}
                ${renderDemographicItemLarge('5-9 Units', acs.units_5_9?.toLocaleString())}
                ${renderDemographicItemLarge('10-19 Units', acs.units_10_19?.toLocaleString())}
                ${renderDemographicItemLarge('20-49 Units', acs.units_20_49?.toLocaleString())}
                ${renderDemographicItemLarge('50+ Units', acs.units_50_or_more?.toLocaleString())}
                ${renderDemographicItemLarge('Mobile Home', acs.mobile_home?.toLocaleString())}
            </div>
        </div>
        
        <div class="data-section">
            <h4><i class="fas fa-percentage"></i> Housing Cost Burden</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Less than 20% Income', acs.housing_cost_less_20pct?.toLocaleString())}
                ${renderDemographicItemLarge('20-24% Income', acs.housing_cost_20_24pct?.toLocaleString())}
                ${renderDemographicItemLarge('25-29% Income', acs.housing_cost_25_29pct?.toLocaleString())}
                ${renderDemographicItemLarge('30-34% Income', acs.housing_cost_30_34pct?.toLocaleString())}
                ${renderDemographicItemLarge('35%+ Income', acs.housing_cost_35pct_or_more?.toLocaleString())}
            </div>
        </div>
    `;
}

function renderEconomicTab(acs, employment) {
    if (!acs) {
        return '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No economic data available</p></div>';
    }
    
    let employmentSection = '';
    if (employment) {
        employmentSection = renderEmploymentSection(employment);
    }
    
    return `
        ${employmentSection}
        
        <div class="data-section">
            <h4><i class="fas fa-briefcase"></i> Employment</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('In Labor Force', acs.in_labor_force?.toLocaleString())}
                ${renderDemographicItemLarge('Employed', acs.employed?.toLocaleString())}
                ${renderDemographicItemLarge('Unemployed', acs.unemployed?.toLocaleString())}
                ${renderDemographicItemLarge('Employment Rate', formatPercent(acs.employment_rate))}
                ${renderDemographicItemLarge('Unemployment Rate', formatPercent(acs.unemployment_rate))}
            </div>
        </div>
        
        <div class="data-section">
            <h4><i class="fas fa-car"></i> Commuting</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Drove Alone', acs.drove_alone?.toLocaleString())}
                ${renderDemographicItemLarge('Carpooled', acs.carpooled?.toLocaleString())}
                ${renderDemographicItemLarge('Public Transit', acs.public_transit?.toLocaleString())}
                ${renderDemographicItemLarge('Walked', acs.walked?.toLocaleString())}
                ${renderDemographicItemLarge('Bicycle', acs.bicycle?.toLocaleString())}
                ${renderDemographicItemLarge('Work from Home', acs.work_from_home?.toLocaleString())}
                ${renderDemographicItemLarge('Transit Use', formatPercent(acs.transit_pct))}
                ${renderDemographicItemLarge('Remote Work', formatPercent(acs.remote_work_pct))}
            </div>
        </div>
        
        ${acs.commute_5_9_min !== undefined ? `
        <div class="data-section">
            <h4><i class="fas fa-clock"></i> Commute Time</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('5-9 Minutes', acs.commute_5_9_min?.toLocaleString())}
                ${renderDemographicItemLarge('10-14 Minutes', acs.commute_10_14_min?.toLocaleString())}
                ${renderDemographicItemLarge('15-19 Minutes', acs.commute_15_19_min?.toLocaleString())}
                ${renderDemographicItemLarge('20-24 Minutes', acs.commute_20_24_min?.toLocaleString())}
                ${renderDemographicItemLarge('25-29 Minutes', acs.commute_25_29_min?.toLocaleString())}
                ${renderDemographicItemLarge('30-34 Minutes', acs.commute_30_34_min?.toLocaleString())}
                ${renderDemographicItemLarge('35-39 Minutes', acs.commute_35_39_min?.toLocaleString())}
                ${renderDemographicItemLarge('40-44 Minutes', acs.commute_40_44_min?.toLocaleString())}
                ${renderDemographicItemLarge('45-59 Minutes', acs.commute_45_59_min?.toLocaleString())}
                ${renderDemographicItemLarge('60-89 Minutes', acs.commute_60_89_min?.toLocaleString())}
                ${renderDemographicItemLarge('90+ Minutes', acs.commute_90plus_min?.toLocaleString())}
            </div>
        </div>
        ` : ''}
        
        <div class="data-section">
            <h4><i class="fas fa-money-bill-wave"></i> Income Distribution</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Under $10K', acs.income_less_10000?.toLocaleString())}
                ${renderDemographicItemLarge('$10K-$15K', acs.income_10000_14999?.toLocaleString())}
                ${renderDemographicItemLarge('$15K-$20K', acs.income_15000_19999?.toLocaleString())}
                ${renderDemographicItemLarge('$20K-$25K', acs.income_20000_24999?.toLocaleString())}
                ${renderDemographicItemLarge('$25K-$30K', acs.income_25000_29999?.toLocaleString())}
                ${renderDemographicItemLarge('$30K-$35K', acs.income_30000_34999?.toLocaleString())}
                ${renderDemographicItemLarge('$35K-$40K', acs.income_35000_39999?.toLocaleString())}
                ${renderDemographicItemLarge('$40K-$45K', acs.income_40000_44999?.toLocaleString())}
                ${renderDemographicItemLarge('$45K-$50K', acs.income_45000_49999?.toLocaleString())}
                ${renderDemographicItemLarge('$50K-$60K', acs.income_50000_59999?.toLocaleString())}
                ${renderDemographicItemLarge('$60K-$75K', acs.income_60000_74999?.toLocaleString())}
                ${renderDemographicItemLarge('$75K-$100K', acs.income_75000_99999?.toLocaleString())}
                ${renderDemographicItemLarge('$100K-$125K', acs.income_100000_124999?.toLocaleString())}
                ${renderDemographicItemLarge('$125K-$150K', acs.income_125000_149999?.toLocaleString())}
                ${renderDemographicItemLarge('$150K-$200K', acs.income_150000_199999?.toLocaleString())}
                ${renderDemographicItemLarge('$200K or More', acs.income_200000_or_more?.toLocaleString())}
            </div>
        </div>
    `;
}

function renderSocialHealthTab(acs) {
    if (!acs) {
        return '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No social and health data available</p></div>';
    }
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-graduation-cap"></i> Education</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('High School Grad', acs.high_school_grad?.toLocaleString())}
                ${renderDemographicItemLarge('Bachelors Degree', acs.bachelors_degree?.toLocaleString())}
                ${renderDemographicItemLarge('Masters Degree', acs.masters_degree?.toLocaleString())}
                ${renderDemographicItemLarge('Professional Degree', acs.professional_degree?.toLocaleString())}
                ${renderDemographicItemLarge('Doctorate Degree', acs.doctorate_degree?.toLocaleString())}
                ${renderDemographicItemLarge('Bachelors+', formatPercent(acs.bachelors_plus_pct))}
            </div>
        </div>
        
        <div class="data-section">
            <h4><i class="fas fa-family"></i> Family Structure</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Family Households', acs.family_households?.toLocaleString())}
                ${renderDemographicItemLarge('Married Couple Families', acs.married_couple_families?.toLocaleString())}
                ${renderDemographicItemLarge('Single Male Families', acs.single_male_families?.toLocaleString())}
                ${renderDemographicItemLarge('Single Female Families', acs.single_female_families?.toLocaleString())}
                ${renderDemographicItemLarge('Non-Family Households', acs.non_family_households?.toLocaleString())}
            </div>
        </div>
        
        ${(acs.health_insurance_universe !== undefined && acs.health_insurance_universe !== null) ? `
        <div class="data-section">
            <h4><i class="fas fa-heartbeat"></i> Health Insurance Coverage</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Total Universe', acs.health_insurance_universe?.toLocaleString())}
                ${renderDemographicItemLarge('With Health Insurance', acs.with_health_insurance?.toLocaleString())}
                ${renderDemographicItemLarge('With Private Insurance', acs.with_private_insurance?.toLocaleString())}
                ${renderDemographicItemLarge('With Public Insurance', acs.with_public_insurance?.toLocaleString())}
                ${renderDemographicItemLarge('Without Health Insurance', acs.without_health_insurance?.toLocaleString())}
            </div>
        </div>
        ` : ''}
        
        ${(acs.disability_universe !== undefined && acs.disability_universe !== null) ? `
        <div class="data-section">
            <h4><i class="fas fa-wheelchair"></i> Disability Status</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Total Universe', acs.disability_universe?.toLocaleString())}
                ${renderDemographicItemLarge('With Disability', acs.with_disability?.toLocaleString())}
                ${renderDemographicItemLarge('Without Disability', acs.without_disability?.toLocaleString())}
            </div>
        </div>
        ` : ''}
        
        ${acs.veteran_universe !== undefined ? `
        <div class="data-section">
            <h4><i class="fas fa-flag-usa"></i> Veteran Status</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Total Universe', acs.veteran_universe?.toLocaleString())}
                ${renderDemographicItemLarge('Veteran (With Flag)', acs.veteran_status_with_flag?.toLocaleString())}
                ${renderDemographicItemLarge('Non-Veteran', acs.veteran_status_without_flag?.toLocaleString())}
            </div>
        </div>
        ` : ''}
        
        ${(acs.language_universe !== undefined && acs.language_universe !== null) ? `
        <div class="data-section">
            <h4><i class="fas fa-language"></i> Language Spoken at Home</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Total Universe', acs.language_universe?.toLocaleString())}
                ${renderDemographicItemLarge('English Only', acs.english_only?.toLocaleString())}
                ${renderDemographicItemLarge('Spanish, Limited English', acs.spanish_speak_limited_english?.toLocaleString())}
                ${renderDemographicItemLarge('Other Language, Limited English', acs.other_language_speak_limited_english?.toLocaleString())}
            </div>
        </div>
        ` : ''}
        
        <div class="data-section">
            <h4><i class="fas fa-passport"></i> Citizenship & Nativity</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Native Born', acs.native_born?.toLocaleString())}
                ${renderDemographicItemLarge('Naturalized Citizen', acs.naturalized_citizen?.toLocaleString())}
                ${renderDemographicItemLarge('Not U.S. Citizen', acs.not_us_citizen?.toLocaleString())}
            </div>
        </div>
    `;
}

function renderTechnologyTab(acs) {
    if (!acs) {
        return '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No technology data available</p></div>';
    }
    
    return `
        ${acs.computer_with_broadband !== undefined ? `
        <div class="data-section">
            <h4><i class="fas fa-laptop"></i> Computer & Internet Access</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('Computer with Broadband', acs.computer_with_broadband?.toLocaleString())}
                ${renderDemographicItemLarge('Computer without Broadband', acs.computer_without_broadband?.toLocaleString())}
                ${renderDemographicItemLarge('Smartphone Only', acs.smartphone_only?.toLocaleString())}
                ${renderDemographicItemLarge('No Computer', acs.no_computer?.toLocaleString())}
            </div>
        </div>
        ` : ''}
        
        <div class="data-section">
            <h4><i class="fas fa-truck"></i> Vehicle Availability</h4>
            <div class="demographics-grid-full">
                ${renderDemographicItemLarge('No Vehicles', acs.no_vehicles?.toLocaleString())}
                ${renderDemographicItemLarge('One Vehicle', acs.one_vehicle?.toLocaleString())}
                ${renderDemographicItemLarge('Two Vehicles', acs.two_vehicles?.toLocaleString())}
                ${renderDemographicItemLarge('Three Vehicles', acs.three_vehicles?.toLocaleString())}
                ${renderDemographicItemLarge('Four or More Vehicles', acs.four_or_more_vehicles?.toLocaleString())}
            </div>
        </div>
    `;
}

function renderCrimeTab(agg) {
    const total = agg.crime_total || 0;
    const breakdown = agg.crime_by_offense || {};
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-exclamation-triangle"></i> Crime Incidents</h4>
            <div class="section-total">${total.toLocaleString()}</div>
            <div class="section-total-label">Total Incidents</div>
            ${total > 0 ? renderBreakdownList(breakdown) : '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No crime data available</p></div>'}
            <div class="chart-container">
                <canvas id="crime-chart"></canvas>
            </div>
        </div>
    `;
}

function render311Tab(agg) {
    const total = agg.sr_total || 0;
    const breakdown = agg.sr_by_issue_type || {};
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-phone"></i> 311 Service Requests</h4>
            <div class="section-total">${total.toLocaleString()}</div>
            <div class="section-total-label">Total Requests</div>
            ${total > 0 ? renderBreakdownList(breakdown) : '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No service request data available</p></div>'}
            <div class="chart-container">
                <canvas id="311-chart"></canvas>
            </div>
        </div>
    `;
}

function renderBusinessTab(agg) {
    const total = agg.businesses_total || 0;
    const breakdownByType = agg.business_by_type || {};
    const breakdownByIndustry = agg.business_by_industry || {};
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-store"></i> Businesses</h4>
            <div class="section-total">${total.toLocaleString()}</div>
            <div class="section-total-label">Total Businesses</div>
            ${total > 0 ? renderBreakdownList(breakdownByType) : '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No business data available</p></div>'}
            <div class="chart-container">
                <canvas id="business-chart"></canvas>
            </div>
        </div>
        
        ${Object.keys(breakdownByIndustry).length > 0 ? `
            <div class="data-section">
                <h4><i class="fas fa-industry"></i> By Industry</h4>
                ${renderBreakdownList(breakdownByIndustry)}
                <div class="chart-container">
                    <canvas id="business-industry-chart"></canvas>
                </div>
            </div>
        ` : ''}
    `;
}

function renderACSDemographics(acs) {
    if (!acs || !acs.population) {
        return '';
    }
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-users"></i> ACS Demographics</h4>
            <div class="demographics-grid">
                ${renderDemographicItem('Population', acs.population?.toLocaleString())}
                ${renderDemographicItem('Median Income', formatCurrency(acs.median_household_income))}
                ${renderDemographicItem('Median Age', acs.median_age?.toFixed(1))}
                ${renderDemographicItem('Poverty Rate', formatPercent(acs.poverty_rate))}
            </div>
        </div>
    `;
}

function renderDemographicItem(label, value) {
    if (!value) return '';
    return `
        <div class="demographic-item">
            <div class="demographic-label">${label}</div>
            <div class="demographic-value">${value}</div>
        </div>
    `;
}

function renderDemographicItemLarge(label, value) {
    if (!value) return '';
    return `
        <div class="demographic-item-large">
            <div class="demographic-label">${label}</div>
            <div class="demographic-value-large">${value}</div>
        </div>
    `;
}

function renderCrimeSection(agg) {
    const total = agg.crime_total || 0;
    const breakdown = agg.crime_by_offense || {};
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-exclamation-triangle"></i> Crime Incidents</h4>
            <div class="section-total">${total.toLocaleString()}</div>
            <div class="section-total-label">Total Incidents</div>
            ${total > 0 ? renderBreakdownList(breakdown) : '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No crime data available</p></div>'}
            <div class="chart-container">
                <canvas id="crime-chart"></canvas>
            </div>
        </div>
    `;
}

function render311Section(agg) {
    const total = agg.sr_total || 0;
    const breakdown = agg.sr_by_issue_type || {};
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-phone"></i> 311 Service Requests</h4>
            <div class="section-total">${total.toLocaleString()}</div>
            <div class="section-total-label">Total Requests</div>
            ${total > 0 ? renderBreakdownList(breakdown) : '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No service request data available</p></div>'}
            <div class="chart-container">
                <canvas id="311-chart"></canvas>
            </div>
        </div>
    `;
}

function renderEmploymentSection(employment) {
    if (!employment) return '';
    
    const jobsAtWorkplace = employment.jobs_at_workplace || 0;
    const workersLivingHere = employment.workers_living_here || 0;
    const ratio = employment.jobs_housing_ratio || 0;
    
    // Determine balance interpretation
    let balanceClass = '';
    let balanceLabel = '';
    if (ratio > 1.2) {
        balanceClass = 'balance-jobs-center';
        balanceLabel = 'Jobs Center';
    } else if (ratio >= 0.8) {
        balanceClass = 'balance-balanced';
        balanceLabel = 'Balanced';
    } else {
        balanceClass = 'balance-residential';
        balanceLabel = 'Residential Area';
    }
    
    const topIndustries = (employment.top_industries || []).map(ind => 
        `<div class="industry-item">
            <span class="industry-name">${ind.name}</span>
            <span class="industry-jobs">${ind.jobs.toLocaleString()}</span>
        </div>`
    ).join('');
    
    const ageGroups = employment.worker_age_groups || {};
    const earnings = employment.earnings_distribution || {};
    
    return `
        <div class="employment-section">
            <div class="stat-grid-compact">
                <div class="stat-card-compact">
                    <h4>Jobs Here</h4>
                    <div class="stat-value-compact">${jobsAtWorkplace.toLocaleString()}</div>
                </div>
                <div class="stat-card-compact">
                    <h4>Workers Living Here</h4>
                    <div class="stat-value-compact">${workersLivingHere.toLocaleString()}</div>
                </div>
                <div class="stat-card-compact ${balanceClass}">
                    <h4>Jobs/Housing Balance</h4>
                    <div class="stat-value-compact">${ratio.toFixed(2)}</div>
                    <div class="stat-label-compact">${balanceLabel}</div>
                </div>
            </div>
            
            ${topIndustries ? `
                <div class="employment-subsection">
                    <h4><i class="fas fa-industry"></i> Top Industries</h4>
                    <div class="compact-list">${topIndustries}</div>
                </div>
            ` : ''}
            
            ${ageGroups.age_29_under > 0 || ageGroups.age_30_54 > 0 || ageGroups.age_55_plus > 0 ? `
                <div class="employment-subsection">
                    <h4><i class="fas fa-users"></i> Worker Age</h4>
                    <div class="stat-grid-2col">
                        <div class="stat-item-compact">
                            <span class="stat-label-compact">≤29</span>
                            <span class="stat-value-compact">${ageGroups.age_29_under?.toLocaleString()}</span>
                        </div>
                        <div class="stat-item-compact">
                            <span class="stat-label-compact">30-54</span>
                            <span class="stat-value-compact">${ageGroups.age_30_54?.toLocaleString()}</span>
                        </div>
                        <div class="stat-item-compact">
                            <span class="stat-label-compact">55+</span>
                            <span class="stat-value-compact">${ageGroups.age_55_plus?.toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            ` : ''}
            
            ${earnings.low > 0 || earnings.mid > 0 || earnings.high > 0 ? `
                <div class="employment-subsection">
                    <h4><i class="fas fa-dollar-sign"></i> Worker Earnings</h4>
                    <div class="stat-grid-2col">
                        <div class="stat-item-compact">
                            <span class="stat-label-compact">Low</span>
                            <span class="stat-value-compact">${earnings.low?.toLocaleString()}</span>
                        </div>
                        <div class="stat-item-compact">
                            <span class="stat-label-compact">Mid</span>
                            <span class="stat-value-compact">${earnings.mid?.toLocaleString()}</span>
                        </div>
                        <div class="stat-item-compact">
                            <span class="stat-label-compact">High</span>
                            <span class="stat-value-compact">${earnings.high?.toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            ` : ''}
            
            ${employment.worker_education && Object.keys(employment.worker_education).length > 0 ? `
                <div class="employment-subsection">
                    <h4><i class="fas fa-graduation-cap"></i> Worker Education</h4>
                    <div class="stat-grid-2col">
                        ${employment.worker_education.less_than_hs > 0 ? `
                            <div class="stat-item-compact">
                                <span class="stat-label-compact">&lt;HS</span>
                                <span class="stat-value-compact">${employment.worker_education.less_than_hs?.toLocaleString()}</span>
                            </div>` : ''}
                        ${employment.worker_education.high_school > 0 ? `
                            <div class="stat-item-compact">
                                <span class="stat-label-compact">HS</span>
                                <span class="stat-value-compact">${employment.worker_education.high_school?.toLocaleString()}</span>
                            </div>` : ''}
                        ${employment.worker_education.some_college > 0 ? `
                            <div class="stat-item-compact">
                                <span class="stat-label-compact">Some College</span>
                                <span class="stat-value-compact">${employment.worker_education.some_college?.toLocaleString()}</span>
                            </div>` : ''}
                        ${employment.worker_education.bachelors_plus > 0 ? `
                            <div class="stat-item-compact">
                                <span class="stat-label-compact">Bachelor's+</span>
                                <span class="stat-value-compact">${employment.worker_education.bachelors_plus?.toLocaleString()}</span>
                            </div>` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${employment.worker_race && Object.keys(employment.worker_race).length > 0 ? `
                <div class="employment-subsection">
                    <h4><i class="fas fa-users"></i> Worker Race</h4>
                    <div class="compact-list">
                        ${Object.entries(employment.worker_race).filter(([_, v]) => v > 0).map(([k, v]) => 
                            `<div class="compact-item">
                                <span class="compact-key">${k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                                <span class="compact-value">${v.toLocaleString()}</span>
                            </div>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${employment.worker_sex && (employment.worker_sex.male > 0 || employment.worker_sex.female > 0) ? `
                <div class="employment-subsection">
                    <h4><i class="fas fa-venus-mars"></i> Worker Sex</h4>
                    <div class="stat-grid-2col">
                        ${employment.worker_sex.male > 0 ? `
                            <div class="stat-item-compact">
                                <span class="stat-label-compact">Male</span>
                                <span class="stat-value-compact">${employment.worker_sex.male?.toLocaleString()}</span>
                            </div>` : ''}
                        ${employment.worker_sex.female > 0 ? `
                            <div class="stat-item-compact">
                                <span class="stat-label-compact">Female</span>
                                <span class="stat-value-compact">${employment.worker_sex.female?.toLocaleString()}</span>
                            </div>` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${employment.firm_age && Object.keys(employment.firm_age).length > 0 && Object.values(employment.firm_age).some(v => v > 0) ? `
                <div class="employment-subsection">
                    <h4><i class="fas fa-calendar"></i> Firm Age</h4>
                    <div class="stat-grid-2col">
                        ${employment.firm_age.age_0_2 > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">0-2 yrs</span><span class="stat-value-compact">${employment.firm_age.age_0_2?.toLocaleString()}</span></div>` : ''}
                        ${employment.firm_age.age_3_5 > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">3-5 yrs</span><span class="stat-value-compact">${employment.firm_age.age_3_5?.toLocaleString()}</span></div>` : ''}
                        ${employment.firm_age.age_6_10 > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">6-10 yrs</span><span class="stat-value-compact">${employment.firm_age.age_6_10?.toLocaleString()}</span></div>` : ''}
                        ${employment.firm_age.age_11_plus > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">11+ yrs</span><span class="stat-value-compact">${employment.firm_age.age_11_plus?.toLocaleString()}</span></div>` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${employment.firm_size && Object.keys(employment.firm_size).length > 0 && Object.values(employment.firm_size).some(v => v > 0) ? `
                <div class="employment-subsection">
                    <h4><i class="fas fa-building"></i> Firm Size</h4>
                    <div class="stat-grid-2col">
                        ${employment.firm_size.size_0_19 > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">0-19 emp</span><span class="stat-value-compact">${employment.firm_size.size_0_19?.toLocaleString()}</span></div>` : ''}
                        ${employment.firm_size.size_20_49 > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">20-49 emp</span><span class="stat-value-compact">${employment.firm_size.size_20_49?.toLocaleString()}</span></div>` : ''}
                        ${employment.firm_size.size_50_249 > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">50-249 emp</span><span class="stat-value-compact">${employment.firm_size.size_50_249?.toLocaleString()}</span></div>` : ''}
                        ${employment.firm_size.size_250_499 > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">250-499 emp</span><span class="stat-value-compact">${employment.firm_size.size_250_499?.toLocaleString()}</span></div>` : ''}
                        ${employment.firm_size.size_500_plus > 0 ? `<div class="stat-item-compact"><span class="stat-label-compact">500+ emp</span><span class="stat-value-compact">${employment.firm_size.size_500_plus?.toLocaleString()}</span></div>` : ''}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

function renderBusinessSection(agg) {
    const total = agg.businesses_total || 0;
    const breakdown = agg.business_by_type || {};
    
    return `
        <div class="data-section">
            <h4><i class="fas fa-store"></i> Businesses</h4>
            <div class="section-total">${total.toLocaleString()}</div>
            <div class="section-total-label">Total Businesses</div>
            ${total > 0 ? renderBreakdownList(breakdown) : '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No business data available</p></div>'}
            <div class="chart-container">
                <canvas id="business-chart"></canvas>
            </div>
        </div>
    `;
}

function renderOtherData(agg) {
    return `
        <div class="data-section">
            <h4><i class="fas fa-building"></i> Other Data</h4>
            ${renderBreakdownList({
                'Dangerous Buildings': agg.dangerous_buildings || 0,
                'Land Bank Properties': agg.landbank_properties || 0
            })}
        </div>
    `;
}

function renderBreakdownList(breakdown) {
    if (!breakdown || Object.keys(breakdown).length === 0) {
        return '<div class="no-data-state"><i class="fas fa-inbox"></i><p>No data available</p></div>';
    }
    
    // Get items, sorted by count
    const items = Object.entries(breakdown)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10); // Top 10 items
    
    if (items.length === 0) return '';
    
    const total = items.reduce((sum, [, count]) => sum + count, 0);
    
    return `
        <ul class="breakdown-list">
            ${items.map(([label, count]) => {
                const percent = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
                return `
                    <li class="breakdown-item">
                        <span class="breakdown-label">${label}</span>
                        <span class="breakdown-count">${count.toLocaleString()}</span>
                        <span class="breakdown-percent">${percent}%</span>
                    </li>
                `;
            }).join('')}
        </ul>
    `;
}

function renderCharts(data) {
    const agg = data.aggregations;
    
    // Render crime chart
    if (agg.crime_by_offense && Object.keys(agg.crime_by_offense).length > 0) {
        renderChart('crime-chart', 'doughnut', 'Crime by Offense Type', agg.crime_by_offense);
    }
    
    // Render 311 chart
    if (agg.sr_by_issue_type && Object.keys(agg.sr_by_issue_type).length > 0) {
        renderChart('311-chart', 'bar', '311 Requests by Type', agg.sr_by_issue_type);
    }
    
    // Render business chart
    if (agg.business_by_type && Object.keys(agg.business_by_type).length > 0) {
        renderChart('business-chart', 'bar', 'Businesses by Type', agg.business_by_type);
    }
    
    // Render business industry chart
    if (agg.business_by_industry && Object.keys(agg.business_by_industry).length > 0) {
        renderChart('business-industry-chart', 'doughnut', 'Businesses by Industry', agg.business_by_industry);
    }
    
    // Render demographics charts
    if (data.acs) {
        renderDemographicsCharts(data.acs);
    }
}

function renderChart(canvasId, type, label, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    const items = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5); // Top 5 for charts
    
    const labels = items.map(([label]) => label);
    const values = items.map(([, value]) => value);
    
    charts[canvasId] = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: type === 'doughnut' 
                    ? ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
                    : '#3498db'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

function renderDemographicsCharts(acs) {
    if (!acs) return;
    
    // Race/ethnicity chart
    const raceData = {
        'White': acs.white_alone || 0,
        'Black': acs.black_alone || 0,
        'Hispanic/Latino': acs.hispanic_latino || 0
    };
    
    if (Object.values(raceData).some(v => v > 0)) {
        renderChart('race-chart', 'pie', 'Race and Ethnicity', raceData);
    }
    
    // Age distribution chart
    const ageData = {
        'Under 18': (acs.male_under_18 || 0) + (acs.female_under_18 || 0),
        '18-64': (acs.male_18_64 || 0) + (acs.female_18_64 || 0),
        '65+': (acs.male_65_plus || 0) + (acs.female_65_plus || 0)
    };
    
    if (Object.values(ageData).some(v => v > 0)) {
        renderChart('age-chart', 'doughnut', 'Age Distribution', ageData);
    }
}

// Helper functions
function formatCurrency(value) {
    if (!value || value === 0) return 'N/A';
    return '$' + value.toLocaleString();
}

function formatPercent(value) {
    if (!value && value !== 0) return 'N/A';
    // Values are already stored as percentages (0-100 range)
    // Just format and cap if necessary
    const percent = Math.min(Math.abs(value), 100); // Cap at 100% max
    return percent.toFixed(1) + '%';
}

