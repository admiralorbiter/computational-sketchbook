/**
 * Land Bank Properties Filter Component
 * 
 * Handles filtering of Land Bank properties by various criteria.
 */

class LandBankFilters {
    constructor(containerId, onFilterChange) {
        this.containerId = containerId;
        this.onFilterChange = onFilterChange;
        this.filters = {};
        this.filterOptions = {};
        
        this.init();
    }
    
    async init() {
        await this.loadFilterOptions();
        this.render();
        this.setupEventHandlers();
    }
    
    async loadFilterOptions() {
        try {
            const response = await fetch('/api/v1/landbank/filters');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.filterOptions = data.filters || {};
            
        } catch (error) {
            console.error('Error loading Land Bank filter options:', error);
            this.filterOptions = {};
        }
    }
    
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with ID '${this.containerId}' not found`);
            return;
        }
        
        container.innerHTML = `
            <div class="filter-section landbank-filters">
                <h4>Land Bank Properties</h4>
                
                <div class="filter-group">
                    <label for="landbank-property-status">Property Status</label>
                    <select id="landbank-property-status" class="form-control">
                        <option value="">All Statuses</option>
                        ${this.renderSelectOptions(this.filterOptions.property_status)}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="landbank-inventory-type">Inventory Type</label>
                    <select id="landbank-inventory-type" class="form-control">
                        <option value="">All Types</option>
                        ${this.renderSelectOptions(this.filterOptions.inventory_type)}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="landbank-property-class">Property Class</label>
                    <select id="landbank-property-class" class="form-control">
                        <option value="">All Classes</option>
                        ${this.renderSelectOptions(this.filterOptions.property_class)}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="landbank-property-condition">Property Condition</label>
                    <select id="landbank-property-condition" class="form-control">
                        <option value="">All Conditions</option>
                        ${this.renderSelectOptions(this.filterOptions.property_condition)}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="landbank-neighborhood">Neighborhood</label>
                    <select id="landbank-neighborhood" class="form-control">
                        <option value="">All Neighborhoods</option>
                        ${this.renderSelectOptions(this.filterOptions.neighborhood)}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="landbank-council-district">Council District</label>
                    <select id="landbank-council-district" class="form-control">
                        <option value="">All Districts</option>
                        ${this.renderSelectOptions(this.filterOptions.city_council_district)}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="landbank-demo-needed">Demo Needed</label>
                    <select id="landbank-demo-needed" class="form-control">
                        <option value="">All</option>
                        <option value="Y">Yes</option>
                        <option value="N">No</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="landbank-search">Search Address/Parcel</label>
                    <input type="text" id="landbank-search" class="form-control" 
                           placeholder="Enter address or parcel number...">
                </div>
                
                <div class="filter-group">
                    <label for="landbank-market-value-min">Min Market Value</label>
                    <input type="number" id="landbank-market-value-min" class="form-control" 
                           placeholder="Min value" min="0">
                </div>
                
                <div class="filter-group">
                    <label for="landbank-market-value-max">Max Market Value</label>
                    <input type="number" id="landbank-market-value-max" class="form-control" 
                           placeholder="Max value" min="0">
                </div>
                
                <div class="filter-actions">
                    <button type="button" class="btn btn-secondary btn-sm" id="landbank-clear-filters">
                        Clear Filters
                    </button>
                    <button type="button" class="btn btn-primary btn-sm" id="landbank-apply-filters">
                        Apply Filters
                    </button>
                </div>
            </div>
        `;
    }
    
    renderSelectOptions(options) {
        if (!options || !Array.isArray(options)) {
            return '';
        }
        
        return options.map(option => {
            const value = typeof option === 'string' ? option : option.value || option;
            const label = typeof option === 'string' ? option : option.label || option.value || option;
            return `<option value="${value}">${label}</option>`;
        }).join('');
    }
    
    setupEventHandlers() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        // Handle filter changes
        const filterInputs = container.querySelectorAll('select, input');
        filterInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.updateFilters();
            });
            
            // For text inputs, add debounced input event
            if (input.type === 'text' || input.type === 'number') {
                let timeout;
                input.addEventListener('input', () => {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        this.updateFilters();
                    }, 500);
                });
            }
        });
        
        // Handle clear filters button
        const clearButton = container.querySelector('#landbank-clear-filters');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearFilters();
            });
        }
        
        // Handle apply filters button
        const applyButton = container.querySelector('#landbank-apply-filters');
        if (applyButton) {
            applyButton.addEventListener('click', () => {
                this.applyFilters();
            });
        }
    }
    
    updateFilters() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        const newFilters = {};
        
        // Get all filter values
        const propertyStatus = container.querySelector('#landbank-property-status')?.value;
        const inventoryType = container.querySelector('#landbank-inventory-type')?.value;
        const propertyClass = container.querySelector('#landbank-property-class')?.value;
        const propertyCondition = container.querySelector('#landbank-property-condition')?.value;
        const neighborhood = container.querySelector('#landbank-neighborhood')?.value;
        const councilDistrict = container.querySelector('#landbank-council-district')?.value;
        const demoNeeded = container.querySelector('#landbank-demo-needed')?.value;
        const search = container.querySelector('#landbank-search')?.value;
        const marketValueMin = container.querySelector('#landbank-market-value-min')?.value;
        const marketValueMax = container.querySelector('#landbank-market-value-max')?.value;
        
        // Add non-empty filters
        if (propertyStatus) newFilters.property_status = propertyStatus;
        if (inventoryType) newFilters.inventory_type = inventoryType;
        if (propertyClass) newFilters.property_class = propertyClass;
        if (propertyCondition) newFilters.property_condition = propertyCondition;
        if (neighborhood) newFilters.neighborhood = neighborhood;
        if (councilDistrict) newFilters.city_council_district = councilDistrict;
        if (demoNeeded) newFilters.demo_needed = demoNeeded;
        if (search) newFilters.search = search;
        
        // Handle market value range
        if (marketValueMin || marketValueMax) {
            newFilters.market_value_range = {
                min: marketValueMin ? parseFloat(marketValueMin) : null,
                max: marketValueMax ? parseFloat(marketValueMax) : null
            };
        }
        
        this.filters = newFilters;
        
        // Notify parent component
        if (this.onFilterChange) {
            this.onFilterChange(this.filters);
        }
    }
    
    clearFilters() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        // Reset all form elements
        const filterInputs = container.querySelectorAll('select, input');
        filterInputs.forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        
        // Clear internal filters
        this.filters = {};
        
        // Notify parent component
        if (this.onFilterChange) {
            this.onFilterChange(this.filters);
        }
    }
    
    applyFilters() {
        this.updateFilters();
    }
    
    getFilters() {
        return this.filters;
    }
    
    setFilters(filters) {
        this.filters = filters || {};
        this.updateUI();
    }
    
    updateUI() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        // Update form elements with current filter values
        Object.entries(this.filters).forEach(([key, value]) => {
            const input = container.querySelector(`#landbank-${key.replace(/_/g, '-')}`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = value;
                } else {
                    input.value = value;
                }
            }
        });
    }
    
    getFilterSummary() {
        const activeFilters = Object.keys(this.filters).length;
        if (activeFilters === 0) {
            return 'No filters applied';
        }
        
        const filterNames = Object.keys(this.filters).map(key => {
            return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        });
        
        return `${activeFilters} filter${activeFilters > 1 ? 's' : ''} applied: ${filterNames.join(', ')}`;
    }
    
    exportFilters() {
        return JSON.stringify(this.filters, null, 2);
    }
    
    importFilters(filterJson) {
        try {
            const filters = JSON.parse(filterJson);
            this.setFilters(filters);
            return true;
        } catch (error) {
            console.error('Error importing filters:', error);
            return false;
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LandBankFilters;
}
