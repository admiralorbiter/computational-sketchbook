/**
 * Land Bank Property Popup Component
 * 
 * Handles the display and interaction of Land Bank property popups.
 */

class LandBankPopup {
    constructor() {
        this.currentPopup = null;
        this.init();
    }
    
    init() {
        this.setupStyles();
        this.setupEventHandlers();
    }
    
    setupStyles() {
        // Add CSS styles for Land Bank popups
        if (!document.getElementById('landbank-popup-styles')) {
            const style = document.createElement('style');
            style.id = 'landbank-popup-styles';
            style.textContent = `
                .landbank-popup .leaflet-popup-content {
                    margin: 0;
                    padding: 0;
                    width: 320px !important;
                }
                
                .landbank-popup-content {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                
                .landbank-popup-content .popup-header {
                    background: linear-gradient(135deg, #FF8C00, #FFA500);
                    color: white;
                    padding: 12px 16px;
                    margin: -8px -8px 0 -8px;
                    border-radius: 8px 8px 0 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .landbank-popup-content .popup-header h3 {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 600;
                }
                
                .landbank-popup-content .property-status {
                    background: rgba(255, 255, 255, 0.2);
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                    text-transform: uppercase;
                }
                
                .landbank-popup-content .status-acquired {
                    background: rgba(255, 140, 0, 0.8);
                }
                
                .landbank-popup-content .status-available {
                    background: rgba(50, 205, 50, 0.8);
                }
                
                .landbank-popup-content .status-pending {
                    background: rgba(255, 215, 0, 0.8);
                }
                
                .landbank-popup-content .popup-body {
                    padding: 16px;
                }
                
                .landbank-popup-content .property-address {
                    font-size: 14px;
                    margin-bottom: 12px;
                    color: #333;
                    line-height: 1.4;
                }
                
                .landbank-popup-content .property-details {
                    display: grid;
                    gap: 8px;
                }
                
                .landbank-popup-content .detail-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    font-size: 13px;
                    line-height: 1.3;
                }
                
                .landbank-popup-content .detail-row .label {
                    font-weight: 600;
                    color: #666;
                    min-width: 100px;
                    flex-shrink: 0;
                }
                
                .landbank-popup-content .detail-row .value {
                    color: #333;
                    text-align: right;
                    word-break: break-word;
                }
                
                .landbank-popup-content .popup-footer {
                    padding: 12px 16px;
                    background: #f8f9fa;
                    margin: 0 -8px -8px -8px;
                    border-radius: 0 0 8px 8px;
                    text-align: center;
                }
                
                .landbank-popup-content .btn {
                    display: inline-block;
                    padding: 6px 12px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    border: none;
                    cursor: pointer;
                    transition: background-color 0.2s;
                }
                
                .landbank-popup-content .btn:hover {
                    background: #0056b3;
                }
                
                .landbank-popup-content .btn-sm {
                    padding: 4px 8px;
                    font-size: 11px;
                }
                
                .landbank-popup-content .btn-primary {
                    background: #007bff;
                }
                
                .landbank-popup-content .btn-primary:hover {
                    background: #0056b3;
                }
                
                /* Marker styles */
                .landbank-marker-container {
                    background: transparent !important;
                    border: none !important;
                }
                
                .landbank-marker {
                    width: 25px;
                    height: 25px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 12px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                    border: 2px solid white;
                }
                
                .landbank-marker i {
                    font-size: 10px;
                }
                
                /* Cluster styles */
                .landbank-cluster {
                    background: #FF8C00 !important;
                    border: 2px solid white !important;
                    border-radius: 50% !important;
                    color: white !important;
                    font-weight: bold !important;
                    text-align: center !important;
                    line-height: 26px !important;
                }
                
                .cluster-icon {
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: bold;
                }
                
                .cluster-small {
                    font-size: 10px;
                }
                
                .cluster-medium {
                    font-size: 11px;
                }
                
                .cluster-large {
                    font-size: 12px;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    setupEventHandlers() {
        // Handle popup events
        document.addEventListener('click', (e) => {
            if (e.target.matches('.landbank-popup .btn')) {
                e.preventDefault();
                this.handleButtonClick(e.target);
            }
        });
    }
    
    handleButtonClick(button) {
        const action = button.getAttribute('data-action');
        
        switch (action) {
            case 'view-dataset':
                this.openDataset();
                break;
            case 'view-details':
                this.viewPropertyDetails(button);
                break;
            case 'get-directions':
                this.getDirections(button);
                break;
            default:
                // Handle default button behavior
                break;
        }
    }
    
    openDataset() {
        window.open('https://data.kcmo.org/Neighborhoods/Land-Bank-and-Kansas-City-Missouri-Homesteading-Au/2ebw-sp7f', '_blank');
    }
    
    viewPropertyDetails(button) {
        const popup = button.closest('.landbank-popup-content');
        const parcelNumber = popup.querySelector('[data-parcel]')?.textContent;
        
        if (parcelNumber) {
            // Open property details in new tab or modal
            console.log('Viewing details for parcel:', parcelNumber);
            // Implement property details view
        }
    }
    
    getDirections(button) {
        const popup = button.closest('.landbank-popup-content');
        const address = popup.querySelector('.property-address strong')?.textContent;
        
        if (address) {
            const encodedAddress = encodeURIComponent(address);
            const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}`;
            window.open(directionsUrl, '_blank');
        }
    }
    
    createPropertyInfoWindow(properties) {
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
        
        return {
            title: 'Land Bank Property',
            content: `
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
                                <span class="value" data-parcel="${parcel_number}">${parcel_number}</span>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="popup-footer">
                        <button class="btn btn-sm btn-primary" data-action="view-dataset">
                            View Full Dataset
                        </button>
                        ${fullAddress ? `
                        <button class="btn btn-sm btn-primary" data-action="get-directions" style="margin-left: 8px;">
                            Get Directions
                        </button>
                        ` : ''}
                    </div>
                </div>
            `
        };
    }
    
    formatCurrency(amount) {
        if (amount == null) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }
    
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            return dateString;
        }
    }
    
    formatSquareFootage(sqft) {
        if (!sqft) return 'N/A';
        return new Intl.NumberFormat('en-US').format(sqft) + ' sq ft';
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LandBankPopup;
}
