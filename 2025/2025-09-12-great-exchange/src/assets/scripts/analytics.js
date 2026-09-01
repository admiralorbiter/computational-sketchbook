/**
 * Analytics and Learning Progress Tracking
 * Tracks user interactions and learning outcomes for The Great Exchange lab
 */

class LearningAnalytics {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.startTime = Date.now();
    this.interactions = [];
    this.learningProgress = {
      chaptersCompleted: [],
      simulationsRun: [],
      conceptsUnderstood: [],
      questionsAnswered: []
    };
    
    this.initializeTracking();
  }
  
  /**
   * Generate unique session ID
   * @returns {string} Session ID
   */
  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
  
  /**
   * Initialize event tracking
   */
  initializeTracking() {
    // Track page views
    this.trackEvent('page_view', {
      page: window.location.pathname,
      timestamp: Date.now()
    });
    
    // Track simulation interactions
    this.trackSimulationEvents();
    
    // Track chapter progress
    this.trackChapterProgress();
    
    // Track form interactions
    this.trackFormInteractions();
  }
  
  /**
   * Track simulation events
   */
  trackSimulationEvents() {
    // Track simulation starts
    document.addEventListener('click', (event) => {
      if (event.target.id === 'start-simulation') {
        this.trackEvent('simulation_started', {
          simulation_type: this.getSimulationType(),
          timestamp: Date.now()
        });
      }
    });
    
    // Track simulation stops
    document.addEventListener('click', (event) => {
      if (event.target.id === 'pause-simulation' || event.target.id === 'reset-simulation') {
        this.trackEvent('simulation_stopped', {
          simulation_type: this.getSimulationType(),
          timestamp: Date.now()
        });
      }
    });
    
    // Track parameter changes
    document.addEventListener('input', (event) => {
      if (event.target.type === 'range') {
        this.trackEvent('parameter_changed', {
          parameter: event.target.id,
          value: event.target.value,
          simulation_type: this.getSimulationType(),
          timestamp: Date.now()
        });
      }
    });
  }
  
  /**
   * Track chapter progress
   */
  trackChapterProgress() {
    // Track chapter completion
    const chapterElements = document.querySelectorAll('.story-content');
    if (chapterElements.length > 0) {
      const chapterNumber = this.getChapterNumber();
      if (chapterNumber && !this.learningProgress.chaptersCompleted.includes(chapterNumber)) {
        this.trackEvent('chapter_completed', {
          chapter: chapterNumber,
          timestamp: Date.now()
        });
        this.learningProgress.chaptersCompleted.push(chapterNumber);
      }
    }
  }
  
  /**
   * Track form interactions
   */
  trackFormInteractions() {
    // Track answer submissions
    document.addEventListener('input', (event) => {
      if (event.target.classList.contains('answer-area')) {
        this.trackEvent('answer_typed', {
          question: event.target.closest('.question')?.querySelector('h4')?.textContent,
          answer_length: event.target.textContent.length,
          timestamp: Date.now()
        });
      }
    });
    
    // Track button clicks
    document.addEventListener('click', (event) => {
      if (event.target.classList.contains('button')) {
        this.trackEvent('button_clicked', {
          button_text: event.target.textContent.trim(),
          button_class: event.target.className,
          page: window.location.pathname,
          timestamp: Date.now()
        });
      }
    });
  }
  
  /**
   * Get current simulation type
   * @returns {string} Simulation type
   */
  getSimulationType() {
    const path = window.location.pathname;
    if (path.includes('basic-barter')) return 'basic-barter';
    if (path.includes('storage-costs')) return 'storage-costs';
    if (path.includes('emergence-patterns')) return 'emergence-patterns';
    return 'unknown';
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
   * Track a learning event
   * @param {string} eventType - Type of event
   * @param {Object} data - Event data
   */
  trackEvent(eventType, data) {
    const event = {
      sessionId: this.sessionId,
      eventType: eventType,
      data: data,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };
    
    this.interactions.push(event);
    
    // Store in localStorage for persistence
    this.storeEvent(event);
    
    // Send to analytics service (if available)
    this.sendToAnalytics(event);
  }
  
  /**
   * Store event in localStorage
   * @param {Object} event - Event to store
   */
  storeEvent(event) {
    try {
      const stored = JSON.parse(localStorage.getItem('great_exchange_analytics') || '[]');
      stored.push(event);
      
      // Keep only last 100 events to avoid storage bloat
      if (stored.length > 100) {
        stored.splice(0, stored.length - 100);
      }
      
      localStorage.setItem('great_exchange_analytics', JSON.stringify(stored));
    } catch (error) {
      console.warn('Failed to store analytics event:', error);
    }
  }
  
  /**
   * Send event to analytics service
   * @param {Object} event - Event to send
   */
  sendToAnalytics(event) {
    // In a real implementation, this would send to an analytics service
    // For now, we'll just log to console
    console.log('Analytics Event:', event);
  }
  
  /**
   * Track learning outcome
   * @param {string} concept - Concept learned
   * @param {number} understanding - Understanding level (1-5)
   */
  trackLearningOutcome(concept, understanding) {
    this.trackEvent('learning_outcome', {
      concept: concept,
      understanding_level: understanding,
      timestamp: Date.now()
    });
    
    this.learningProgress.conceptsUnderstood.push({
      concept: concept,
      understanding: understanding,
      timestamp: Date.now()
    });
  }
  
  /**
   * Track simulation result
   * @param {Object} result - Simulation result data
   */
  trackSimulationResult(result) {
    this.trackEvent('simulation_result', {
      simulation_type: this.getSimulationType(),
      result: result,
      timestamp: Date.now()
    });
    
    this.learningProgress.simulationsRun.push({
      type: this.getSimulationType(),
      result: result,
      timestamp: Date.now()
    });
  }
  
  /**
   * Get learning progress summary
   * @returns {Object} Progress summary
   */
  getProgressSummary() {
    const sessionDuration = Date.now() - this.startTime;
    const totalInteractions = this.interactions.length;
    const chaptersCompleted = this.learningProgress.chaptersCompleted.length;
    const simulationsRun = this.learningProgress.simulationsRun.length;
    
    return {
      sessionId: this.sessionId,
      sessionDuration: sessionDuration,
      totalInteractions: totalInteractions,
      chaptersCompleted: chaptersCompleted,
      simulationsRun: simulationsRun,
      conceptsUnderstood: this.learningProgress.conceptsUnderstood.length,
      progressPercentage: this.calculateProgressPercentage()
    };
  }
  
  /**
   * Calculate overall progress percentage
   * @returns {number} Progress percentage
   */
  calculateProgressPercentage() {
    const totalChapters = 6;
        const totalSimulations = 3;
        
        const chapterProgress = (this.learningProgress.chaptersCompleted.length / totalChapters) * 50;
        const simulationProgress = (this.learningProgress.simulationsRun.length / totalSimulations) * 50;
        
        return Math.min(100, chapterProgress + simulationProgress);
  }
  
  /**
   * Export learning data
   * @returns {Object} Exported data
   */
  exportData() {
    return {
      sessionId: this.sessionId,
      startTime: this.startTime,
      endTime: Date.now(),
      interactions: this.interactions,
      learningProgress: this.learningProgress,
      summary: this.getProgressSummary()
    };
  }
  
  /**
   * Clear stored data
   */
  clearData() {
    localStorage.removeItem('great_exchange_analytics');
    this.interactions = [];
    this.learningProgress = {
      chaptersCompleted: [],
      simulationsRun: [],
      conceptsUnderstood: [],
      questionsAnswered: []
    };
  }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  window.learningAnalytics = new LearningAnalytics();
});

// Export for global use
window.LearningAnalytics = LearningAnalytics;
