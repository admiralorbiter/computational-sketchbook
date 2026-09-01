/**
 * EducationalStateManager - Centralized state management for The Great Exchange lab
 * Implements Observer pattern optimized for educational use cases
 */
class EducationalStateManager {
  constructor(initialState = {}) {
    this.state = {
      currentChapter: 1,
      simulationActive: false,
      userProgress: {},
      simulationData: {},
      currentSimulation: null,
      metrics: {
        iteration: 0,
        trades: 0,
        efficiency: 0,
        monetaryCirculation: 0,
        welfare: 0
      },
      settings: {
        speed: 1.0,
        maxIterations: 1000,
        convergenceThreshold: 0.8
      },
      ...initialState
    };
    this.observers = new Map();
    this.history = [];
    this.maxHistorySize = 100;
  }
  
  /**
   * Subscribe to state changes
   * @param {string} key - State key to observe
   * @param {Function} callback - Callback function
   */
  observe(key, callback) {
    if (!this.observers.has(key)) {
      this.observers.set(key, new Set());
    }
    this.observers.get(key).add(callback);
  }
  
  /**
   * Unsubscribe from state changes
   * @param {string} key - State key
   * @param {Function} callback - Callback function to remove
   */
  unobserve(key, callback) {
    if (this.observers.has(key)) {
      this.observers.get(key).delete(callback);
    }
  }
  
  /**
   * Update state and notify observers
   * @param {Object} updates - State updates
   */
  updateState(updates) {
    const previousState = { ...this.state };
    
    // Store in history
    this.history.push({
      timestamp: Date.now(),
      previous: { ...previousState },
      updates: { ...updates }
    });
    
    // Trim history if too large
    if (this.history.length > this.maxHistorySize) {
      this.history.shift();
    }
    
    // Update state
    Object.assign(this.state, updates);
    
    // Notify relevant observers
    Object.keys(updates).forEach(key => {
      if (this.observers.has(key)) {
        this.observers.get(key).forEach(callback => 
          callback(this.state[key], previousState[key])
        );
      }
    });
    
    // Notify global state change observers
    if (this.observers.has('*')) {
      this.observers.get('*').forEach(callback => 
        callback(this.state, previousState)
      );
    }
  }
  
  /**
   * Get current state
   * @param {string} key - Optional key to get specific state
   * @returns {*} State value or entire state object
   */
  getState(key = null) {
    return key ? this.state[key] : this.state;
  }
  
  /**
   * Reset state to initial values
   */
  reset() {
    this.state = {
      currentChapter: 1,
      simulationActive: false,
      userProgress: {},
      simulationData: {},
      currentSimulation: null,
      metrics: {
        iteration: 0,
        trades: 0,
        efficiency: 0,
        monetaryCirculation: 0,
        welfare: 0
      },
      settings: {
        speed: 1.0,
        maxIterations: 1000,
        convergenceThreshold: 0.8
      }
    };
    this.history = [];
    this.notifyAll();
  }
  
  /**
   * Notify all observers of current state
   */
  notifyAll() {
    this.observers.forEach((callbacks, key) => {
      callbacks.forEach(callback => 
        callback(this.state[key], this.state[key])
      );
    });
  }
  
  /**
   * Get state history
   * @param {number} limit - Maximum number of history entries to return
   * @returns {Array} State history
   */
  getHistory(limit = 10) {
    return this.history.slice(-limit);
  }
  
  /**
   * Undo last state change
   * @returns {boolean} Success status
   */
  undo() {
    if (this.history.length === 0) return false;
    
    const lastChange = this.history.pop();
    this.state = lastChange.previous;
    this.notifyAll();
    return true;
  }
  
  /**
   * Export state for persistence
   * @returns {Object} Serializable state
   */
  exportState() {
    return {
      state: this.state,
      timestamp: Date.now(),
      version: '1.0.0'
    };
  }
  
  /**
   * Import state from persistence
   * @param {Object} exportedState - Previously exported state
   */
  importState(exportedState) {
    if (exportedState && exportedState.state) {
      this.state = { ...this.state, ...exportedState.state };
      this.notifyAll();
    }
  }
}

/**
 * Simulation-specific state management
 */
class SimulationStateManager extends EducationalStateManager {
  constructor(simulationType = 'basic-barter') {
    super();
    this.simulationType = simulationType;
    this.agents = [];
    this.commodities = [];
    this.trades = [];
    this.initializeSimulation();
  }
  
  /**
   * Initialize simulation based on type
   */
  initializeSimulation() {
    const scenarios = window.scenarios || {};
    const simulationConfig = scenarios.simulationLevels?.find(
      level => level.id === this.simulationType
    );
    
    if (simulationConfig) {
      this.updateState({
        currentSimulation: this.simulationType,
        settings: {
          ...this.state.settings,
          ...simulationConfig.parameters
        }
      });
    }
  }
  
  /**
   * Add agent to simulation
   * @param {Object} agent - Agent configuration
   */
  addAgent(agent) {
    this.agents.push({
      id: agent.id || this.agents.length,
      type: agent.type,
      holdings: agent.holdings || [],
      preferences: agent.preferences || [],
      storageCosts: agent.storageCosts || {},
      ...agent
    });
  }
  
  /**
   * Add commodity to simulation
   * @param {Object} commodity - Commodity configuration
   */
  addCommodity(commodity) {
    this.commodities.push({
      id: commodity.id || this.commodities.length,
      name: commodity.name,
      storageCost: commodity.storageCost,
      color: commodity.color,
      icon: commodity.icon,
      ...commodity
    });
  }
  
  /**
   * Record a trade
   * @param {Object} trade - Trade details
   */
  recordTrade(trade) {
    this.trades.push({
      id: this.trades.length,
      timestamp: Date.now(),
      iteration: this.state.metrics.iteration,
      ...trade
    });
    
    this.updateState({
      metrics: {
        ...this.state.metrics,
        trades: this.state.metrics.trades + 1
      }
    });
  }
  
  /**
   * Update simulation metrics
   * @param {Object} metrics - New metrics
   */
  updateMetrics(metrics) {
    this.updateState({
      metrics: {
        ...this.state.metrics,
        ...metrics
      }
    });
  }
  
  /**
   * Get agent by ID
   * @param {number} id - Agent ID
   * @returns {Object} Agent object
   */
  getAgent(id) {
    return this.agents.find(agent => agent.id === id);
  }
  
  /**
   * Get commodity by ID
   * @param {number} id - Commodity ID
   * @returns {Object} Commodity object
   */
  getCommodity(id) {
    return this.commodities.find(commodity => commodity.id === id);
  }
  
  /**
   * Get recent trades
   * @param {number} limit - Number of recent trades to return
   * @returns {Array} Recent trades
   */
  getRecentTrades(limit = 10) {
    return this.trades.slice(-limit);
  }
  
  /**
   * Calculate current efficiency
   * @returns {number} Current efficiency rate
   */
  calculateEfficiency() {
    if (this.trades.length === 0) return 0;
    
    const successfulTrades = this.trades.filter(trade => trade.successful);
    return successfulTrades.length / this.trades.length;
  }
  
  /**
   * Calculate monetary circulation rate
   * @returns {number} Monetary circulation rate
   */
  calculateMonetaryCirculation() {
    if (this.trades.length === 0) return 0;
    
    const moneyTrades = this.trades.filter(trade => trade.usedMoney);
    return moneyTrades.length / this.trades.length;
  }
}

// Global state manager instance
window.stateManager = new EducationalStateManager();
window.simulationManager = null;

// Initialize simulation manager when simulation starts
function initializeSimulation(simulationType) {
  window.simulationManager = new SimulationStateManager(simulationType);
  return window.simulationManager;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { EducationalStateManager, SimulationStateManager };
}
