/**
 * Lab Integration Script
 * Coordinates all components of The Great Exchange lab
 */

class LabIntegration {
  constructor() {
    this.isInitialized = false;
    this.components = {
      stateManager: null,
      simulationManager: null,
      visualization: null,
      analytics: null
    };
    
    this.initializeLab();
  }
  
  /**
   * Initialize the lab
   */
  initializeLab() {
    if (this.isInitialized) return;
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupLab());
    } else {
      this.setupLab();
    }
  }
  
  /**
   * Setup lab components
   */
  setupLab() {
    try {
      // Initialize state management
      this.initializeStateManagement();
      
      // Initialize analytics
      this.initializeAnalytics();
      
      // Initialize page-specific components
      this.initializePageComponents();
      
      // Setup global event handlers
      this.setupGlobalEventHandlers();
      
      this.isInitialized = true;
      console.log('The Great Exchange Lab initialized successfully');
      
    } catch (error) {
      console.error('Failed to initialize lab:', error);
    }
  }
  
  /**
   * Initialize state management
   */
  initializeStateManagement() {
    if (window.stateManager) {
      this.components.stateManager = window.stateManager;
    } else {
      console.warn('State manager not available');
    }
  }
  
  /**
   * Initialize analytics
   */
  initializeAnalytics() {
    if (window.learningAnalytics) {
      this.components.analytics = window.learningAnalytics;
    } else {
      console.warn('Analytics not available');
    }
  }
  
  /**
   * Initialize page-specific components
   */
  initializePageComponents() {
    const path = window.location.pathname;
    
    if (path.includes('/simulations/')) {
      this.initializeSimulationPage();
    } else if (path.includes('/chapters/')) {
      this.initializeChapterPage();
    } else if (path.includes('/great-exchange/')) {
      this.initializeLabHomePage();
    }
  }
  
  /**
   * Initialize simulation page
   */
  initializeSimulationPage() {
    // Load simulation data
    this.loadSimulationData();
    
    // Initialize simulation-specific components
    this.initializeSimulationComponents();
  }
  
  /**
   * Initialize chapter page
   */
  initializeChapterPage() {
    // Setup chapter navigation
    this.setupChapterNavigation();
    
    // Track chapter progress
    this.trackChapterProgress();
  }
  
  /**
   * Initialize lab home page
   */
  initializeLabHomePage() {
    // Setup lab overview
    this.setupLabOverview();
  }
  
  /**
   * Load simulation data
   */
  async loadSimulationData() {
    try {
      // Load civilization data
      const civilizationResponse = await fetch('/great-exchange/assets/data/civilization.json');
      if (civilizationResponse.ok) {
        window.civilization = await civilizationResponse.json();
      }
      
      // Load scenarios data
      const scenariosResponse = await fetch('/great-exchange/assets/data/scenarios.json');
      if (scenariosResponse.ok) {
        window.scenarios = await scenariosResponse.json();
      }
      
      // Load metrics data
      const metricsResponse = await fetch('/great-exchange/assets/data/metrics.json');
      if (metricsResponse.ok) {
        window.metrics = await metricsResponse.json();
      }
      
    } catch (error) {
      console.warn('Failed to load simulation data:', error);
    }
  }
  
  /**
   * Initialize simulation components
   */
  initializeSimulationComponents() {
    // This will be called by individual simulation pages
    // after they initialize their specific components
  }
  
  /**
   * Setup chapter navigation
   */
  setupChapterNavigation() {
    // Add keyboard navigation
    document.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') {
        const prevButton = document.querySelector('.button.secondary');
        if (prevButton) prevButton.click();
      } else if (event.key === 'ArrowRight') {
        const nextButton = document.querySelector('.button.primary');
        if (nextButton) nextButton.click();
      }
    });
  }
  
  /**
   * Track chapter progress
   */
  trackChapterProgress() {
    if (this.components.analytics) {
      const chapterNumber = this.getChapterNumber();
      if (chapterNumber) {
        this.components.analytics.trackEvent('chapter_viewed', {
          chapter: chapterNumber,
          timestamp: Date.now()
        });
      }
    }
  }
  
  /**
   * Setup lab overview
   */
  setupLabOverview() {
    // Add interactive elements
    this.setupInteractiveElements();
  }
  
  /**
   * Setup interactive elements
   */
  setupInteractiveElements() {
    // Add hover effects to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
      card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-5px)';
      });
      
      card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0)';
      });
    });
    
    // Add click tracking to buttons
    const buttons = document.querySelectorAll('.button');
    buttons.forEach(button => {
      button.addEventListener('click', () => {
        if (this.components.analytics) {
          this.components.analytics.trackEvent('button_clicked', {
            button_text: button.textContent.trim(),
            button_class: button.className,
            page: window.location.pathname,
            timestamp: Date.now()
          });
        }
      });
    });
  }
  
  /**
   * Setup global event handlers
   */
  setupGlobalEventHandlers() {
    // Handle window resize
    window.addEventListener('resize', this.debounce(() => {
      this.handleResize();
    }, 250));
    
    // Handle visibility change
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.handlePageHidden();
      } else {
        this.handlePageVisible();
      }
    });
    
    // Handle beforeunload
    window.addEventListener('beforeunload', () => {
      this.handlePageUnload();
    });
  }
  
  /**
   * Handle window resize
   */
  handleResize() {
    // Update visualizations if they exist
    if (this.components.visualization) {
      this.components.visualization.update();
    }
  }
  
  /**
   * Handle page hidden
   */
  handlePageHidden() {
    // Pause simulations
    if (this.components.simulationManager) {
      this.components.simulationManager.stop();
    }
  }
  
  /**
   * Handle page visible
   */
  handlePageVisible() {
    // Resume simulations if they were running
    // This would be handled by individual simulation pages
  }
  
  /**
   * Handle page unload
   */
  handlePageUnload() {
    // Save progress
    if (this.components.analytics) {
      const progressData = this.components.analytics.exportData();
      localStorage.setItem('great_exchange_progress', JSON.stringify(progressData));
    }
  }
  
  /**
   * Get current chapter number
   * @returns {number} Chapter number
   */
  getChapterNumber() {
    const path = window.location.pathname;
    const match = path.match(/chapters\/(\d+)-/);
    return match ? parseInt(match[1]) : null;
  }
  
  /**
   * Debounce function
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in ms
   * @returns {Function} Debounced function
   */
  debounce(func, wait) {
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
  
  /**
   * Get lab status
   * @returns {Object} Lab status
   */
  getStatus() {
    return {
      initialized: this.isInitialized,
      components: Object.keys(this.components).filter(key => this.components[key] !== null),
      currentPage: window.location.pathname,
      timestamp: Date.now()
    };
  }
}

// Initialize lab integration
window.labIntegration = new LabIntegration();

// Export for global use
window.LabIntegration = LabIntegration;
