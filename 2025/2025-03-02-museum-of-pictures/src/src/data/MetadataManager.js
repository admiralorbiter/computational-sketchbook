export class MetadataManager {
    constructor() {
        // Cache for metadata
        this.metadataCache = {};
    }
    
    /**
     * Get or create metadata for an artwork
     */
    getMetadata(artwork) {
        // If the artwork already has complete metadata
        if (artwork.userData && 
            artwork.userData.title && 
            artwork.userData.artist && 
            artwork.userData.description) {
            return artwork.userData;
        }
        
        // Check cache if we have an ID
        if (artwork.userData && artwork.userData.id && this.metadataCache[artwork.userData.id]) {
            return this.metadataCache[artwork.userData.id];
        }
        
        // Create basic metadata if nothing exists
        const metadata = {
            title: artwork.userData?.title || 'Untitled Artwork',
            artist: artwork.userData?.artist || 'Unknown Artist',
            year: artwork.userData?.year || 'Unknown Date',
            description: artwork.userData?.description || 'No description available for this artwork.',
            medium: artwork.userData?.medium || 'Unknown Medium',
            dimensions: artwork.userData?.dimensions || 'Unknown Dimensions',
            location: artwork.userData?.location || 'Virtual Museum',
            source: artwork.userData?.source || 'Unknown Source',
            url: artwork.userData?.url || null
        };
        
        // Cache the metadata if we have an ID
        if (artwork.userData && artwork.userData.id) {
            this.metadataCache[artwork.userData.id] = metadata;
        }
        
        return metadata;
    }
    
    /**
     * Update metadata for an artwork
     */
    updateMetadata(artwork, newMetadata) {
        // Merge existing userData with new metadata
        artwork.userData = {
            ...artwork.userData,
            ...newMetadata
        };
        
        // Update cache if we have an ID
        if (artwork.userData && artwork.userData.id) {
            this.metadataCache[artwork.userData.id] = artwork.userData;
        }
        
        return artwork.userData;
    }
    
    /**
     * Format metadata for display in the info panel
     */
    formatForDisplay(metadata) {
        let formattedHTML = '';
        
        // Title and Artist (required)
        formattedHTML += `<h2>${metadata.title}</h2>`;
        formattedHTML += `<p><strong>Artist:</strong> ${metadata.artist}</p>`;
        
        // Optional fields
        if (metadata.year) {
            formattedHTML += `<p><strong>Year:</strong> ${metadata.year}</p>`;
        }
        
        if (metadata.medium) {
            formattedHTML += `<p><strong>Medium:</strong> ${metadata.medium}</p>`;
        }
        
        if (metadata.dimensions) {
            formattedHTML += `<p><strong>Dimensions:</strong> ${metadata.dimensions}</p>`;
        }
        
        // Description (can be longer)
        if (metadata.description) {
            formattedHTML += `<p><strong>Description:</strong><br>${metadata.description}</p>`;
        }
        
        // Source information
        if (metadata.source) {
            formattedHTML += `<p><strong>Source:</strong> ${metadata.source}</p>`;
        }
        
        return formattedHTML;
    }
    
    /**
     * Search for artworks based on metadata criteria
     */
    searchArtworks(artworks, criteria) {
        const results = [];
        
        for (const artwork of artworks) {
            let match = true;
            
            // Check each search criterion
            for (const key in criteria) {
                if (criteria[key] && artwork.userData && artwork.userData[key]) {
                    // Case-insensitive text search
                    const criterionValue = criteria[key].toString().toLowerCase();
                    const artworkValue = artwork.userData[key].toString().toLowerCase();
                    
                    if (!artworkValue.includes(criterionValue)) {
                        match = false;
                        break;
                    }
                }
            }
            
            if (match) {
                results.push(artwork);
            }
        }
        
        return results;
    }
    
    /**
     * Generate related artworks based on metadata similarities
     */
    findRelatedArtworks(artwork, allArtworks, limit = 3) {
        const results = [];
        
        // Skip if no metadata
        if (!artwork.userData) {
            return results;
        }
        
        // Calculate a similarity score for each artwork
        const scoredArtworks = [];
        
        for (const otherArtwork of allArtworks) {
            // Skip the same artwork
            if (otherArtwork === artwork || 
                (artwork.userData.id && otherArtwork.userData && 
                 artwork.userData.id === otherArtwork.userData.id)) {
                continue;
            }
            
            // Skip if no metadata
            if (!otherArtwork.userData) {
                continue;
            }
            
            let score = 0;
            
            // Score based on same artist
            if (artwork.userData.artist && otherArtwork.userData.artist && 
                artwork.userData.artist === otherArtwork.userData.artist) {
                score += 5;
            }
            
            // Score based on same period/year (within 20 years)
            if (artwork.userData.year && otherArtwork.userData.year) {
                const year1 = parseInt(artwork.userData.year.replace(/\D/g, ''));
                const year2 = parseInt(otherArtwork.userData.year.replace(/\D/g, ''));
                
                if (!isNaN(year1) && !isNaN(year2) && Math.abs(year1 - year2) <= 20) {
                    score += 3;
                }
            }
            
            // Score based on same medium
            if (artwork.userData.medium && otherArtwork.userData.medium && 
                artwork.userData.medium === otherArtwork.userData.medium) {
                score += 2;
            }
            
            // Score based on keyword matches in title or description
            if (artwork.userData.title && otherArtwork.userData.title) {
                const words1 = artwork.userData.title.toLowerCase().split(/\s+/);
                const words2 = otherArtwork.userData.title.toLowerCase().split(/\s+/);
                
                for (const word of words1) {
                    if (word.length > 3 && words2.includes(word)) {
                        score += 1;
                    }
                }
            }
            
            if (artwork.userData.description && otherArtwork.userData.description) {
                const words1 = artwork.userData.description.toLowerCase().split(/\s+/);
                const words2 = otherArtwork.userData.description.toLowerCase().split(/\s+/);
                
                for (const word of words1) {
                    if (word.length > 3 && words2.includes(word)) {
                        score += 0.5;
                    }
                }
            }
            
            scoredArtworks.push({
                artwork: otherArtwork,
                score
            });
        }
        
        // Sort by score (highest first)
        scoredArtworks.sort((a, b) => b.score - a.score);
        
        // Return the top matches
        return scoredArtworks.slice(0, limit).map(item => item.artwork);
    }
}