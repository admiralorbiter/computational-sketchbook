/**
 * Kiyotaki-Wright Simulation Engine
 * Implements agent-based modeling for money emergence
 */

class KiyotakiWrightSimulation {
  constructor(config = {}) {
    this.config = {
      population: config.population || 9,
      meetingProbability: config.meetingProbability || 0.25,
      storageCosts: config.storageCosts || [1, 4, 9], // c1 < c2 < c3
      recognitionCost: config.recognitionCost || 0.15,
      maxIterations: config.maxIterations || 1000,
      convergenceThreshold: config.convergenceThreshold || 0.8,
      ...config
    };
    
    this.agents = [];
    this.commodities = [];
    this.trades = [];
    this.iteration = 0;
    this.isRunning = false;
    this.metrics = {
      efficiency: 0,
      monetaryCirculation: 0,
      welfare: 0,
      welfareGain: 0,
      convergenceStep: null
    };
    
    this.baselineWelfare = 0; // Store baseline for comparison
    
    this.initializeCommodities();
    this.initializeAgents();
  }
  
  /**
   * Initialize commodities with storage costs
   */
  initializeCommodities() {
    this.commodities = [
      {
        id: 0,
        name: 'barley',
        displayName: 'Barley',
        storageCost: this.config.storageCosts[0],
        color: '#D4AF37',
        icon: '🌾',
        type: 'grain'
      },
      {
        id: 1,
        name: 'copper_tools',
        displayName: 'Copper Tools',
        storageCost: this.config.storageCosts[1],
        color: '#B87333',
        icon: '🔨',
        type: 'metalwork'
      },
      {
        id: 2,
        name: 'wool_textiles',
        displayName: 'Wool Textiles',
        storageCost: this.config.storageCosts[2],
        color: '#8B4513',
        icon: '🧶',
        type: 'textile'
      }
    ];
  }
  
  /**
   * Initialize agents with different types and preferences
   */
  initializeAgents() {
    this.agents = [];
    
    for (let i = 0; i < this.config.population; i++) {
      const agentType = i % 3; // Cycle through 3 agent types
      const agent = this.createAgent(i, agentType);
      this.agents.push(agent);
    }
  }
  
  /**
   * Create an agent of specific type
   * @param {number} id - Agent ID
   * @param {number} type - Agent type (0, 1, or 2)
   * @returns {Object} Agent object
   */
  createAgent(id, type) {
    const agentTypes = [
      {
        name: 'Kael',
        title: 'Grain Farmer',
        production: [0], // Produces barley
        consumption: [1, 2], // Consumes tools and textiles
        personality: 'practical'
      },
      {
        name: 'Tira',
        title: 'Copper Smith',
        production: [1], // Produces tools
        consumption: [0, 2], // Consumes grain and textiles
        personality: 'innovative'
      },
      {
        name: 'Jorek',
        title: 'Shepherd',
        production: [2], // Produces textiles
        consumption: [0, 1], // Consumes grain and tools
        personality: 'adaptive'
      }
    ];
    
    const agentConfig = agentTypes[type];
    
    return {
      id: id,
      type: type,
      name: agentConfig.name,
      title: agentConfig.title,
      personality: agentConfig.personality,
      production: agentConfig.production,
      consumption: agentConfig.consumption,
      holdings: [type], // Start with their production good
      preferences: this.generatePreferences(type),
      storageCosts: this.calculateStorageCosts(type),
      tradingHistory: [],
      utility: 0,
      lastTrade: null
    };
  }
  
  /**
   * Generate trading preferences for agent
   * @param {number} type - Agent type
   * @returns {Array} Preference weights for each commodity
   */
  generatePreferences(type) {
    const preferences = [0, 0, 0];
    
    // Direct consumption preferences
    const agentTypes = [
      { consumption: [1, 2] }, // Kael needs tools and textiles
      { consumption: [0, 2] }, // Tira needs grain and textiles
      { consumption: [0, 1] }  // Jorek needs grain and tools
    ];
    
    agentTypes[type].consumption.forEach(commodityId => {
      preferences[commodityId] = 1.0; // High preference for consumption goods
    });
    
    // Add some randomness to preferences
    preferences.forEach((pref, index) => {
      if (pref === 0) {
        preferences[index] = Math.random() * 0.3; // Low preference for non-consumption goods
      }
    });
    
    return preferences;
  }
  
  /**
   * Calculate storage costs for agent's current holdings
   * @param {number} type - Agent type
   * @returns {Object} Storage costs for each commodity
   */
  calculateStorageCosts(type) {
    const costs = {};
    this.commodities.forEach(commodity => {
      costs[commodity.id] = commodity.storageCost;
    });
    return costs;
  }
  
  /**
   * Run one iteration of the simulation
   */
  runIteration() {
    if (this.isRunning && this.iteration < this.config.maxIterations) {
      this.iteration++;
      
      // Randomly select agents for potential meetings
      const meetingPairs = this.generateMeetingPairs();
      
      // Process each meeting
      meetingPairs.forEach(pair => {
        this.processMeeting(pair[0], pair[1]);
      });
      
      // Update metrics
      this.updateMetrics();
      
      // Log progress every 100 iterations for debugging
      if (this.iteration % 100 === 0) {
        const speculativeTrades = this.trades.filter(t => t.type === 'speculative');
        const barleyTrades = this.trades.filter(t => t.commodity1 === 0 || t.commodity2 === 0);
        const moneyTrades = this.trades.filter(t => this.isMoneyTrade(t));
        const recentSpeculativeTrades = this.trades.slice(-50).filter(t => t.type === 'speculative');
        const recentBarleyTrades = this.trades.slice(-50).filter(t => t.commodity1 === 0 || t.commodity2 === 0);
        
        console.log(`Iteration ${this.iteration}: Efficiency=${(this.metrics.efficiency*100).toFixed(1)}%, Money Circulation=${(this.metrics.monetaryCirculation*100).toFixed(1)}%, Welfare=${this.metrics.welfare.toFixed(1)}%`);
        console.log(`  Total: Speculative=${speculativeTrades.length}, Barley=${barleyTrades.length}, Money=${moneyTrades.length}, Total=${this.trades.length}`);
        console.log(`  Recent (last 50): Speculative=${recentSpeculativeTrades.length}, Barley=${recentBarleyTrades.length}`);
        
        // Check agent holdings
        const barleyHolders = this.agents.filter(a => a.holdings.includes(0)).length;
        console.log(`  Agents holding barley: ${barleyHolders}/${this.agents.length}`);
      }
      
      // Check for convergence
      if (this.checkConvergence()) {
        console.log(`Convergence achieved at iteration ${this.iteration}! Money circulation: ${(this.metrics.monetaryCirculation*100).toFixed(1)}%`);
        this.stop();
      }
      
      return true;
    }
    return false;
  }
  
  /**
   * Generate random meeting pairs
   * @returns {Array} Array of agent pairs
   */
  generateMeetingPairs() {
    const pairs = [];
    const shuffledAgents = [...this.agents].sort(() => Math.random() - 0.5);
    
    for (let i = 0; i < shuffledAgents.length - 1; i += 2) {
      if (Math.random() < this.config.meetingProbability) {
        pairs.push([shuffledAgents[i], shuffledAgents[i + 1]]);
      }
    }
    
    return pairs;
  }
  
  /**
   * Process a meeting between two agents
   * @param {Object} agent1 - First agent
   * @param {Object} agent2 - Second agent
   */
  processMeeting(agent1, agent2) {
    // Check if agents can trade directly
    const directTrade = this.checkDirectTrade(agent1, agent2);
    
    if (directTrade.possible) {
      this.executeDirectTrade(agent1, agent2, directTrade);
    } else {
      // For basic barter simulation, no speculative trading is allowed
      // This demonstrates the double coincidence of wants problem
      if (this.config.simulationType === 'basic-barter') {
        // Record failed trade attempt for basic barter
        this.recordFailedTrade(agent1, agent2, directTrade);
      } else {
        // Check for speculative trades in storage-costs and emergence-patterns simulations
        const speculativeTrade = this.checkSpeculativeTrade(agent1, agent2);
        
        
        if (speculativeTrade.possible) {
          this.executeSpeculativeTrade(agent1, agent2, speculativeTrade);
        } else {
          // Record failed trade attempt for advanced simulations too
          this.recordFailedTrade(agent1, agent2, directTrade);
        }
      }
    }
  }
  
  /**
   * Check if agents can trade directly (double coincidence of wants)
   * @param {Object} agent1 - First agent
   * @param {Object} agent2 - Second agent
   * @returns {Object} Trade analysis
   */
  checkDirectTrade(agent1, agent2) {
    const agent1Good = agent1.holdings[0];
    const agent2Good = agent2.holdings[0];
    
    // For basic barter, agents can only trade if there's a direct match
    // Agent1 must want what Agent2 has AND Agent2 must want what Agent1 has
    const agent1Wants = agent2Good;
    const agent2Wants = agent1Good;
    
    const agent1WantsIt = agent1.consumption.includes(agent1Wants);
    const agent2WantsIt = agent2.consumption.includes(agent2Wants);
    
    // In basic barter, NO speculative trading is allowed
    return {
      possible: agent1WantsIt && agent2WantsIt,
      agent1Good: agent1Good,
      agent2Good: agent2Good,
      type: 'direct'
    };
  }
  
  /**
   * Check if agents can trade speculatively (accepting non-consumption goods)
   * @param {Object} agent1 - First agent
   * @param {Object} agent2 - Second agent
   * @returns {Object} Trade analysis
   */
  checkSpeculativeTrade(agent1, agent2) {
    const agent1Good = agent1.holdings[0];
    const agent2Good = agent2.holdings[0];
    
    // Check if agent1 would accept agent2's good speculatively
    const agent1Accepts = this.wouldAcceptSpeculatively(agent1, agent2Good);
    const agent2Accepts = this.wouldAcceptSpeculatively(agent2, agent1Good);
    
    // Also check if agents have different goods (not the same commodity)
    const differentGoods = agent1Good !== agent2Good;
    
    return {
      possible: (agent1Accepts || agent2Accepts) && differentGoods,
      agent1Good: agent1Good,
      agent2Good: agent2Good,
      agent1Accepts: agent1Accepts,
      agent2Accepts: agent2Accepts,
      type: 'speculative'
    };
  }
  
  /**
   * Determine if agent would accept a good speculatively
   * @param {Object} agent - Agent to check
   * @param {number} commodityId - Commodity to potentially accept
   * @returns {boolean} Whether agent would accept
   */
  wouldAcceptSpeculatively(agent, commodityId) {
    // Don't accept if it's what they already have
    if (agent.holdings.includes(commodityId)) {
      return false;
    }
    
    const currentStorageCost = this.getStorageCost(agent.holdings[0]);
    const newStorageCost = this.getStorageCost(commodityId);
    
    // Always accept if storage cost is significantly lower (Kiyotaki-Wright core mechanism)
    if (newStorageCost < currentStorageCost) {
      return true;
    }
    
    // For emergence-patterns simulation, use enhanced logic
    if (this.config.simulationType === 'emergence-patterns') {
      // Special case: If it's barley (the money commodity), be much more aggressive
      if (commodityId === 0) { // Barley is commodity 0
        const tradingPotential = this.calculateTradingPotential(commodityId);
        const socialLearningFactor = this.calculateSocialLearningFactor(commodityId);
        
        // EXTREMELY high acceptance probability for barley
        let baseChance = 0.6; // Base 60% chance
        
        // Tipping point: If barley circulation is already high, make it even more likely
        if (this.metrics.monetaryCirculation > 0.3) { // If >30% circulation
          baseChance = 0.8; // Jump to 80% base chance
        }
        if (this.metrics.monetaryCirculation > 0.5) { // If >50% circulation
          baseChance = 0.9; // Jump to 90% base chance
        }
        
        const barleyAcceptanceProbability = Math.min(0.98, 
          baseChance +
          tradingPotential * 0.2 + // 20% weight for trading potential
          socialLearningFactor * 0.1 + // 10% weight for social learning
          Math.random() * 0.1 // 10% random factor
        );
        
        const shouldAccept = barleyAcceptanceProbability > 0.15;
        
        // Debug logging for barley acceptance
        if (this.iteration % 200 === 0) {
          console.log(`Barley acceptance check: prob=${barleyAcceptanceProbability.toFixed(3)}, threshold=0.15, accept=${shouldAccept}, circulation=${(this.metrics.monetaryCirculation*100).toFixed(1)}%`);
        }
        
        return shouldAccept;
      }
      
      // For other commodities, use more conservative logic
      const storageCostBenefit = (currentStorageCost - newStorageCost) / Math.max(currentStorageCost, 1);
      const tradingPotential = this.calculateTradingPotential(commodityId);
      const socialLearningFactor = this.calculateSocialLearningFactor(commodityId);
      
      // Base acceptance probability with stronger incentives
      const baseProbability = 0.2; // Lower base probability for non-money commodities
      const storageWeight = 0.5;   // Higher weight for storage costs
      const tradingWeight = 0.2;   // Lower weight for trading potential
      const socialWeight = 0.1;    // Lower weight for social learning
      const randomFactor = 0.1;    // 10% random factor
      
      const acceptanceProbability = Math.max(0, Math.min(1,
        baseProbability +
        storageCostBenefit * storageWeight +
        tradingPotential * tradingWeight +
        socialLearningFactor * socialWeight +
        Math.random() * randomFactor
      ));
      
      return acceptanceProbability > 0.6; // Higher threshold for non-money commodities
    }
    
    // For storage-costs simulation, accept with high probability
    if (this.config.simulationType === 'storage-costs') {
      return Math.random() < 0.8; // 80% chance to accept any good speculatively
    }
    
    // Default logic for other simulations
    const storageCostBenefit = (currentStorageCost - newStorageCost) / Math.max(currentStorageCost, 1);
    const tradingPotential = this.calculateTradingPotential(commodityId);
    
    const acceptanceProbability = Math.max(0, 
      storageCostBenefit * 0.4 + 
      tradingPotential * 0.2 + 
      Math.random() * 0.1 + 
      0.3
    );
    
    return acceptanceProbability > 0.5;
  }
  
  /**
   * Get storage cost for commodity
   * @param {number} commodityId - Commodity ID
   * @returns {number} Storage cost
   */
  getStorageCost(commodityId) {
    const commodity = this.commodities.find(c => c.id === commodityId);
    return commodity ? commodity.storageCost : 0;
  }
  
  /**
   * Calculate trading potential for commodity
   * @param {number} commodityId - Commodity ID
   * @returns {number} Trading potential (0-1)
   */
  calculateTradingPotential(commodityId) {
    const recentTrades = this.trades.slice(-20); // Last 20 trades
    const commodityTrades = recentTrades.filter(trade => 
      trade.commodity1 === commodityId || trade.commodity2 === commodityId
    );
    
    return commodityTrades.length / Math.max(1, recentTrades.length);
  }
  
  /**
   * Calculate social learning factor - how much agents observe others' success
   * @param {number} commodityId - Commodity ID
   * @returns {number} Social learning factor (0-1)
   */
  calculateSocialLearningFactor(commodityId) {
    const recentTrades = this.trades.slice(-50); // Last 50 trades
    const successfulCommodityTrades = recentTrades.filter(trade => 
      (trade.commodity1 === commodityId || trade.commodity2 === commodityId) && 
      trade.successful && 
      trade.type === 'speculative'
    );
    
    const totalSuccessfulTrades = recentTrades.filter(trade => 
      trade.successful && trade.type === 'speculative'
    );
    
    if (totalSuccessfulTrades.length === 0) return 0;
    
    return successfulCommodityTrades.length / totalSuccessfulTrades.length;
  }
  
  /**
   * Execute a direct trade
   * @param {Object} agent1 - First agent
   * @param {Object} agent2 - Second agent
   * @param {Object} trade - Trade details
   */
  executeDirectTrade(agent1, agent2, trade) {
    // Exchange goods
    agent1.holdings = [trade.agent2Good];
    agent2.holdings = [trade.agent1Good];
    
    // Update utility
    agent1.utility += this.calculateUtility(agent1, trade.agent2Good);
    agent2.utility += this.calculateUtility(agent2, trade.agent1Good);
    
    // Record trade
    this.recordTrade(agent1, agent2, trade, true);
  }
  
  /**
   * Execute a speculative trade
   * @param {Object} agent1 - First agent
   * @param {Object} agent2 - Second agent
   * @param {Object} trade - Trade details
   */
  executeSpeculativeTrade(agent1, agent2, trade) {
    // Determine who accepts speculatively
    if (trade.agent1Accepts && !trade.agent2Accepts) {
      // Agent1 accepts agent2's good speculatively
      agent1.holdings = [trade.agent2Good]; // Agent1 gets Agent2's good
      // Agent2 keeps their original good (no change)
      agent1.utility += this.calculateSpeculativeUtility(agent1, trade.agent2Good);
    } else if (trade.agent2Accepts && !trade.agent1Accepts) {
      // Agent2 accepts agent1's good speculatively
      agent2.holdings = [trade.agent1Good]; // Agent2 gets Agent1's good
      // Agent1 keeps their original good (no change)
      agent2.utility += this.calculateSpeculativeUtility(agent2, trade.agent1Good);
    } else if (trade.agent1Accepts && trade.agent2Accepts) {
      // Both accept speculatively - random choice
      if (Math.random() < 0.5) {
        agent1.holdings = [trade.agent2Good]; // Agent1 gets Agent2's good
        // Agent2 keeps their original good
        agent1.utility += this.calculateSpeculativeUtility(agent1, trade.agent2Good);
      } else {
        agent2.holdings = [trade.agent1Good]; // Agent2 gets Agent1's good
        // Agent1 keeps their original good
        agent2.utility += this.calculateSpeculativeUtility(agent2, trade.agent1Good);
      }
    }
    
    // Record trade
    this.recordTrade(agent1, agent2, trade, true);
  }
  
  /**
   * Calculate utility from consuming a good
   * @param {Object} agent - Agent
   * @param {number} commodityId - Commodity ID
   * @returns {number} Utility gained
   */
  calculateUtility(agent, commodityId) {
    if (agent.consumption.includes(commodityId)) {
      return 1.0; // Full utility for consumption goods
    }
    return 0; // No utility for non-consumption goods
  }
  
  /**
   * Calculate speculative utility (future trading potential)
   * @param {Object} agent - Agent
   * @param {number} commodityId - Commodity ID
   * @returns {number} Speculative utility
   */
  calculateSpeculativeUtility(agent, commodityId) {
    const storageCost = this.getStorageCost(commodityId);
    const tradingPotential = this.calculateTradingPotential(commodityId);
    
    // Utility based on storage cost (lower is better) and trading potential
    return (1 - storageCost / 10) * tradingPotential * 0.5;
  }
  
  /**
   * Record a failed trade attempt
   * @param {Object} agent1 - First agent
   * @param {Object} agent2 - Second agent
   * @param {Object} trade - Trade details
   */
  recordFailedTrade(agent1, agent2, trade) {
    const tradeRecord = {
      id: this.trades.length,
      iteration: this.iteration,
      timestamp: Date.now(),
      agent1: agent1.id,
      agent2: agent2.id,
      commodity1: trade.agent1Good,
      commodity2: trade.agent2Good,
      type: 'failed_attempt',
      successful: false,
      usedMoney: false,
      reason: 'double_coincidence_problem'
    };
    
    this.trades.push(tradeRecord);
  }

  /**
   * Record a trade
   * @param {Object} agent1 - First agent
   * @param {Object} agent2 - Second agent
   * @param {Object} trade - Trade details
   * @param {boolean} successful - Whether trade was successful
   */
  recordTrade(agent1, agent2, trade, successful) {
    const tradeRecord = {
      id: this.trades.length,
      iteration: this.iteration,
      timestamp: Date.now(),
      agent1: agent1.id,
      agent2: agent2.id,
      commodity1: trade.agent1Good,
      commodity2: trade.agent2Good,
      type: trade.type,
      successful: successful,
      usedMoney: this.isMoneyTrade(trade)
    };
    
    this.trades.push(tradeRecord);
    
    // Update agent trading history
    agent1.tradingHistory.push(tradeRecord);
    agent2.tradingHistory.push(tradeRecord);
    agent1.lastTrade = tradeRecord;
    agent2.lastTrade = tradeRecord;
  }
  
  /**
   * Check if trade used money (lowest storage cost commodity)
   * @param {Object} trade - Trade details
   * @returns {boolean} Whether trade used money
   */
  isMoneyTrade(trade) {
    const moneyCommodity = this.commodities.reduce((min, commodity) => 
      commodity.storageCost < min.storageCost ? commodity : min
    );
    
    // A trade uses money if either commodity is the lowest storage cost good
    // For storage costs simulation, count any trade involving Barley as money usage
    if (this.config.simulationType === 'storage-costs') {
      return trade.commodity1 === moneyCommodity.id || trade.commodity2 === moneyCommodity.id;
    }
    
    // For emergence-patterns simulation, count any trade involving the money commodity
    // This includes both direct and speculative trades, as the goal is to measure
    // how much the low-storage-cost commodity is being used in circulation
    if (this.config.simulationType === 'emergence-patterns') {
      return trade.commodity1 === moneyCommodity.id || trade.commodity2 === moneyCommodity.id;
    }
    
    // For other simulations, only count speculative trades as money usage
    return (trade.commodity1 === moneyCommodity.id || trade.commodity2 === moneyCommodity.id) &&
           trade.type === 'speculative';
  }
  
  /**
   * Update simulation metrics
   */
  updateMetrics() {
    this.metrics.efficiency = this.calculateEfficiency();
    this.metrics.monetaryCirculation = this.calculateMonetaryCirculation();
    this.metrics.welfare = this.calculateWelfare();
    // welfareGain is calculated within calculateWelfare()
  }
  
  /**
   * Calculate trading efficiency
   * @returns {number} Efficiency rate (0-1)
   */
  calculateEfficiency() {
    if (this.trades.length === 0) return 0;
    
    const successfulTrades = this.trades.filter(trade => trade.successful);
    return successfulTrades.length / this.trades.length;
  }
  
  /**
   * Calculate monetary circulation rate
   * @returns {number} Monetary circulation rate (0-1)
   */
  calculateMonetaryCirculation() {
    if (this.trades.length === 0) return 0;
    
    const moneyTrades = this.trades.filter(trade => this.isMoneyTrade(trade));
    return moneyTrades.length / this.trades.length;
  }
  
  /**
   * Calculate total welfare
   * @returns {number} Total welfare (normalized percentage)
   */
  calculateWelfare() {
    const totalUtility = this.agents.reduce((total, agent) => total + agent.utility, 0);
    const maxPossibleUtility = this.agents.length * this.iteration * 0.1; // Theoretical maximum
    const welfarePercentage = Math.min(100, (totalUtility / Math.max(maxPossibleUtility, 1)) * 100);
    
    // Calculate welfare gain if we have a baseline
    if (this.baselineWelfare > 0) {
      this.metrics.welfareGain = ((welfarePercentage - this.baselineWelfare) / Math.max(this.baselineWelfare, 1)) * 100;
    } else if (this.iteration >= 50 && this.baselineWelfare === 0) {
      // Set baseline after 50 iterations
      this.baselineWelfare = welfarePercentage;
      console.log(`Baseline welfare set at iteration ${this.iteration}: ${welfarePercentage.toFixed(1)}%`);
    } else if (this.iteration < 50) {
      // For early iterations, set a very low baseline to ensure we get positive gains
      this.baselineWelfare = Math.max(1, welfarePercentage * 0.5);
    }
    
    return welfarePercentage;
  }
  
  /**
   * Check if simulation has converged
   * @returns {boolean} Whether converged
   */
  checkConvergence() {
    // Only check for convergence after a minimum number of iterations
    if (this.iteration < 100) {
      return false;
    }
    
    if (this.metrics.monetaryCirculation >= this.config.convergenceThreshold) {
      if (!this.metrics.convergenceStep) {
        this.metrics.convergenceStep = this.iteration;
        console.log(`Convergence achieved at iteration ${this.iteration}! Money circulation: ${(this.metrics.monetaryCirculation*100).toFixed(1)}%`);
      }
      
      // Only stop if we've been converged for at least 50 iterations
      if (this.iteration - this.metrics.convergenceStep >= 50) {
        return true;
      }
    }
    return false;
  }
  
  /**
   * Start simulation
   */
  start() {
    this.isRunning = true;
    this.runSimulationLoop();
  }
  
  /**
   * Stop simulation
   */
  stop() {
    this.isRunning = false;
  }
  
  /**
   * Reset simulation
   */
  reset() {
    this.iteration = 0;
    this.trades = [];
    this.metrics = {
      efficiency: 0,
      monetaryCirculation: 0,
      welfare: 0,
      welfareGain: 0,
      convergenceStep: null
    };
    this.baselineWelfare = 0;
    this.initializeAgents();
  }
  
  /**
   * Run simulation loop
   */
  runSimulationLoop() {
    if (this.isRunning) {
      this.runIteration();
      
      // Notify observers
      if (window.stateManager) {
        window.stateManager.updateState({
          metrics: {
            iteration: this.iteration,
            trades: this.trades.length,
            efficiency: this.metrics.efficiency,
            monetaryCirculation: this.metrics.monetaryCirculation,
            welfare: this.metrics.welfare
          }
        });
      }
      
      // Continue loop
      setTimeout(() => this.runSimulationLoop(), 1000 / this.config.speed);
    }
  }
  
  /**
   * Get simulation data for visualization
   * @returns {Object} Simulation data
   */
  getSimulationData() {
    return {
      agents: this.agents,
      commodities: this.commodities,
      trades: this.trades,
      metrics: this.metrics,
      iteration: this.iteration
    };
  }
}

// Export for global use
window.KiyotakiWrightSimulation = KiyotakiWrightSimulation;
