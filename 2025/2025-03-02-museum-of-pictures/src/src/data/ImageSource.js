export class ImageSource {
    constructor() {
        // Local images path
        this.localImagesPath = 'images/';
        
        // External image source APIs
        this.externalSources = [
            {
                name: 'Wikimedia Commons',
                apiEndpoint: null, // Direct URLs used instead
                enabled: true
            },
            {
                name: 'Local Repository',
                apiEndpoint: null,
                enabled: true
            }
        ];
        
        // Dictionary of theme to image collections
        this.themeMap = {
            // Classical themes
            renaissance: this.getWikimediaCollection('renaissance', 8),
            classical: this.getWikimediaCollection('classical_art', 8),
            historical: this.getWikimediaCollection('historical_paintings', 8),
            
            // Modern themes
            modern: this.getWikimediaCollection('modern_art', 8),
            technological: this.getWikimediaCollection('technology_art', 8),
            abstract: this.getWikimediaCollection('abstract_art', 8),
            
            // Experimental themes
            surreal: this.getWikimediaCollection('surrealism', 8),
            contemporary: this.getWikimediaCollection('contemporary_art', 8),
            experimental: this.getWikimediaCollection('experimental_art', 8),
            
            // General (fallback)
            general: this.getWikimediaCollection('famous_paintings', 12)
        };
        
        // Cache for loaded images
        this.imageCache = {};
    }
    
    /**
     * Preload some images to ensure there's no delay during exploration
     */
    async preloadImages() {
        // Get a sample of images across different themes
        const preloadThemes = ['general', 'renaissance', 'modern', 'surreal'];
        const preloadPromises = [];
        
        for (const theme of preloadThemes) {
            const images = await this.getImagesForThemes([theme], 2);
            
            for (const image of images) {
                if (image.url) {
                    // Add error handling to continue even if an image fails to load
                    preloadPromises.push(
                        this.preloadImage(image.url)
                            .catch(error => {
                                console.warn(`Skipping failed image: ${error.message}`);
                                // Use a fallback image instead
                                return this.useFallbackImage(image);
                            })
                    );
                }
            }
        }
        
        // Wait for all preloads to complete (including those that failed but were handled)
        await Promise.allSettled(preloadPromises);
        console.log('Preloaded images for faster rendering');
    }
    
    /**
     * Use a fallback image when the original fails to load
     */
    async useFallbackImage(image) {
        // Generate a fallback URL using local placeholders
        const fallbackIndex = Math.floor(Math.random() * 5) + 1;
        const fallbackUrl = `${this.localImagesPath}placeholders/artwork_${fallbackIndex}.jpg`;
        
        // Store the fallback in the cache
        this.imageCache[image.url] = fallbackUrl;
        
        // Update the image object with the fallback URL
        image.originalUrl = image.url;
        image.url = fallbackUrl;
        image.isFallback = true;
        
        console.log(`Using fallback image for: ${image.title}`);
        return fallbackUrl;
    }
    
    /**
     * Preload a single image
     */
    async preloadImage(url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                this.imageCache[url] = true;
                resolve(url);
            };
            img.onerror = () => {
                reject(new Error(`Failed to preload image: ${url}`));
            };
            img.src = url;
        });
    }
    
    /**
     * Get images for a list of themes
     */
    async getImagesForThemes(themes = ['general'], count = 5) {
        let allImages = [];
        
        // Gather images from all requested themes
        for (const theme of themes) {
            if (this.themeMap[theme]) {
                allImages = allImages.concat(this.themeMap[theme]);
            }
        }
        
        // If no images found, use general theme
        if (allImages.length === 0) {
            allImages = this.themeMap.general;
        }
        
        // Shuffle the images
        this.shuffleArray(allImages);
        
        // Return the requested number of images
        return allImages.slice(0, count);
    }
    
    /**
     * Get a specific image by ID
     */
    async getImageById(id) {
        // Search through all collections
        for (const theme in this.themeMap) {
            const collection = this.themeMap[theme];
            const image = collection.find(img => img.id === id);
            
            if (image) {
                return image;
            }
        }
        
        return null;
    }
    
    /**
     * Helper to shuffle an array (Fisher-Yates algorithm)
     */
    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
    
    /**
     * Create a collection of Wikimedia images for a theme
     * This uses predefined URLs for demo purposes
     */
    getWikimediaCollection(theme, count) {
        const collection = [];
        
        // For development/demo purposes, create a collection with placeholder data
        // In a real application, you would fetch these from an API
        switch(theme) {
            case 'renaissance':
                collection.push(
                    {
                        id: 'renaissance_1',
                        title: 'Mona Lisa',
                        artist: 'Leonardo da Vinci',
                        description: 'One of the most famous paintings in the world, known for her enigmatic smile.',
                        year: '1503-1519',
                        source: 'Wikimedia Commons',
                        url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/800px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg'
                    },
                    {
                        id: 'renaissance_2',
                        title: 'The Birth of Venus',
                        artist: 'Sandro Botticelli',
                        description: 'Depicts the goddess Venus arriving at the shore after her birth.',
                        year: '1485-1486',
                        source: 'Wikimedia Commons',
                        url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg/2560px-Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg'
                    }
                );
                break;
                
            case 'classical_art':
                collection.push(
                    {
                        id: 'classical_1',
                        title: 'The Night Watch',
                        artist: 'Rembrandt',
                        description: 'Famous for its effective use of light and shadow (chiaroscuro).',
                        year: '1642',
                        source: 'Wikimedia Commons',
                        url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Night_Watch_-_HD.jpg/1920px-The_Night_Watch_-_HD.jpg'
                    },
                    {
                        id: 'classical_2',
                        title: 'The School of Athens',
                        artist: 'Raphael',
                        description: 'A fresco depicting the greatest mathematicians, philosophers and scientists from classical antiquity.',
                        year: '1509-1511',
                        source: 'Wikimedia Commons',
                        url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/%22The_School_of_Athens%22_by_Raffaello_Sanzio_da_Urbino.jpg/1920px-%22The_School_of_Athens%22_by_Raffaello_Sanzio_da_Urbino.jpg'
                    }
                );
                break;
                
            case 'modern_art':
                collection.push(
                    {
                        id: 'modern_1',
                        title: 'The Starry Night',
                        artist: 'Vincent van Gogh',
                        description: 'A night scene showing his view from his asylum room window.',
                        year: '1889',
                        source: 'Wikimedia Commons',
                        url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1920px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg'
                    },
                    {
                        id: 'modern_2',
                        title: 'The Persistence of Memory',
                        artist: 'Salvador Dalí',
                        description: 'Famous surrealist painting with melting pocket watches.',
                        year: '1931',
                        source: 'Wikimedia Commons',
                        url: 'https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg'
                    }
                );
                break;
                
            case 'surrealism':
                collection.push(
                    {
                        id: 'surreal_1',
                        title: 'The Son of Man',
                        artist: 'René Magritte',
                        description: 'A self-portrait with the face obscured by a floating green apple.',
                        year: '1964',
                        source: 'Wikimedia Commons',
                        url: 'https://upload.wikimedia.org/wikipedia/en/e/e5/Magritte_TheSonOfMan.jpg'
                    },
                    {
                        id: 'surreal_2',
                        title: 'The Elephants',
                        artist: 'Salvador Dalí',
                        description: 'Depicts elephants with elongated legs that give a dream-like appearance.',
                        year: '1948',
                        source: 'Wikimedia Commons',
                        url: 'https://upload.wikimedia.org/wikipedia/en/thumb/b/bd/Dali_Elephants.jpg/1280px-Dali_Elephants.jpg'
                    }
                );
                break;
                
            // Add more placeholders for other themes
            default:
                // Generic placeholders
                for (let i = 1; i <= count; i++) {
                    collection.push({
                        id: `${theme}_${i}`,
                        title: `Artwork ${i}`,
                        artist: 'Unknown Artist',
                        description: 'A sample artwork for demonstration purposes.',
                        source: 'Local Repository',
                        url: `${this.localImagesPath}placeholders/artwork_${i % 5 + 1}.jpg`
                    });
                }
        }
        
        return collection;
    }
    
    /**
     * Get local images from the /images directory
     */
    async getLocalImages(theme, count) {
        const localImages = [];
        
        // In a real application, this would scan the local directory
        // For demo purposes, return placeholders
        for (let i = 1; i <= count; i++) {
            localImages.push({
                id: `local_${theme}_${i}`,
                title: `Local Artwork ${i}`,
                artist: 'Local Artist',
                description: 'A sample artwork from the local repository.',
                source: 'Local Repository',
                url: `${this.localImagesPath}placeholders/artwork_${i % 5 + 1}.jpg`
            });
        }
        
        return localImages;
    }
}