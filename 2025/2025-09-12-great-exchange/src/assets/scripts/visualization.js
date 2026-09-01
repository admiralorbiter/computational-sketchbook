/**
 * Visualization components for The Great Exchange simulation
 * Handles real-time charts, network graphs, and data visualization
 */

class SimulationVisualization {
  constructor(containerId, simulation) {
    this.container = document.getElementById(containerId);
    this.simulation = simulation;
    this.charts = {};
    this.networkGraph = null;
    this.isInitialized = false;
    
    this.initializeVisualizations();
  }
  
  /**
   * Initialize all visualization components
   */
  initializeVisualizations() {
    if (!this.container) {
      console.error('Visualization container not found');
      return;
    }
    
    this.createMetricsDashboard();
    this.createTradingNetwork();
    this.createCommodityFlow();
    this.createEfficiencyChart();
    this.createConvergenceChart();
    
    this.isInitialized = true;
  }
  
  /**
   * Create real-time metrics dashboard
   */
  createMetricsDashboard() {
    const dashboard = document.createElement('div');
    dashboard.className = 'metrics-dashboard';
    dashboard.innerHTML = `
      <div class="grid-x grid-margin-x">
        <div class="cell large-3">
          <div class="metric-card">
            <h6>Iteration</h6>
            <div class="metric-value" id="iteration-metric">0</div>
          </div>
        </div>
        <div class="cell large-3">
          <div class="metric-card">
            <h6>Total Trades</h6>
            <div class="metric-value" id="trades-metric">0</div>
          </div>
        </div>
        <div class="cell large-3">
          <div class="metric-card">
            <h6>Efficiency</h6>
            <div class="metric-value" id="efficiency-metric">0%</div>
          </div>
        </div>
        <div class="cell large-3">
          <div class="metric-card">
            <h6>Money Circulation</h6>
            <div class="metric-value" id="circulation-metric">0%</div>
          </div>
        </div>
      </div>
    `;
    
    this.container.appendChild(dashboard);
  }
  
  /**
   * Create trading network visualization
   */
  createTradingNetwork() {
    const networkContainer = document.createElement('div');
    networkContainer.className = 'network-container';
    networkContainer.innerHTML = `
      <h5>Trading Network</h5>
      <div id="network-graph" class="network-graph"></div>
    `;
    
    this.container.appendChild(networkContainer);
    
    // Initialize network graph
    this.initializeNetworkGraph();
  }
  
  /**
   * Initialize network graph using Observable Plot
   */
  initializeNetworkGraph() {
    const networkElement = document.getElementById('network-graph');
    if (!networkElement) return;
    
    // Create SVG container
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '400');
    svg.setAttribute('viewBox', '0 0 400 400');
    networkElement.appendChild(svg);
    
    this.networkSvg = svg;
    this.updateNetworkGraph();
  }
  
  /**
   * Update network graph with current data
   */
  updateNetworkGraph() {
    if (!this.networkSvg || !this.simulation) return;
    
    const data = this.simulation.getSimulationData();
    const agents = data.agents;
    const trades = data.trades.slice(-20); // Last 20 trades
    
    // Clear previous content
    this.networkSvg.innerHTML = '';
    
    // Create agent nodes
    const nodeRadius = 20;
    const centerX = 200;
    const centerY = 200;
    const radius = 150;
    
    agents.forEach((agent, index) => {
      const angle = (2 * Math.PI * index) / agents.length;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', x);
      circle.setAttribute('cy', y);
      circle.setAttribute('r', nodeRadius);
      circle.setAttribute('fill', this.getAgentColor(agent));
      circle.setAttribute('stroke', '#333');
      circle.setAttribute('stroke-width', '2');
      
      // Add agent name
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', x);
      text.setAttribute('y', y + 5);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('font-size', '12');
      text.setAttribute('fill', 'white');
      text.textContent = agent.name;
      
      this.networkSvg.appendChild(circle);
      this.networkSvg.appendChild(text);
    });
    
    // Draw trade connections
    trades.forEach(trade => {
      if (trade.successful) {
        const agent1 = agents.find(a => a.id === trade.agent1);
        const agent2 = agents.find(a => a.id === trade.agent2);
        
        if (agent1 && agent2) {
          const index1 = agents.indexOf(agent1);
          const index2 = agents.indexOf(agent2);
          
          const angle1 = (2 * Math.PI * index1) / agents.length;
          const angle2 = (2 * Math.PI * index2) / agents.length;
          
          const x1 = centerX + radius * Math.cos(angle1);
          const y1 = centerY + radius * Math.sin(angle1);
          const x2 = centerX + radius * Math.cos(angle2);
          const y2 = centerY + radius * Math.sin(angle2);
          
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
          line.setAttribute('x1', x1);
          line.setAttribute('y1', y1);
          line.setAttribute('x2', x2);
          line.setAttribute('y2', y2);
          line.setAttribute('stroke', trade.usedMoney ? '#4CAF50' : '#FF9800');
          line.setAttribute('stroke-width', '2');
          line.setAttribute('opacity', '0.7');
          
          this.networkSvg.appendChild(line);
        }
      }
    });
  }
  
  /**
   * Get color for agent based on holdings
   * @param {Object} agent - Agent object
   * @returns {string} Color code
   */
  getAgentColor(agent) {
    if (!agent.holdings || agent.holdings.length === 0) return '#999';
    
    const commodity = this.simulation.commodities.find(c => c.id === agent.holdings[0]);
    return commodity ? commodity.color : '#999';
  }
  
  /**
   * Create commodity flow visualization
   */
  createCommodityFlow() {
    const flowContainer = document.createElement('div');
    flowContainer.className = 'flow-container';
    flowContainer.innerHTML = `
      <h5>Commodity Flow</h5>
      <div id="commodity-flow" class="commodity-flow"></div>
    `;
    
    this.container.appendChild(flowContainer);
    
    // Initialize commodity flow chart
    this.initializeCommodityFlow();
  }
  
  /**
   * Initialize commodity flow chart
   */
  initializeCommodityFlow() {
    const flowElement = document.getElementById('commodity-flow');
    if (!flowElement) return;
    
    // Create canvas for Chart.js
    const canvas = document.createElement('canvas');
    canvas.id = 'commodity-flow-chart';
    flowElement.appendChild(canvas);
    
    this.commodityFlowChart = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: [],
        datasets: [{
          data: [],
          backgroundColor: [],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
    
    this.updateCommodityFlow();
  }
  
  /**
   * Update commodity flow chart
   */
  updateCommodityFlow() {
    if (!this.commodityFlowChart || !this.simulation) return;
    
    const data = this.simulation.getSimulationData();
    const agents = data.agents;
    const commodities = data.commodities;
    const trades = data.trades;
    
    // Count trading activity by commodity (not just holdings)
    const tradingActivity = {};
    commodities.forEach(commodity => {
      tradingActivity[commodity.id] = 0;
    });
    
    // Count how many times each commodity appears in trades
    trades.forEach(trade => {
      if (trade.successful) {
        tradingActivity[trade.commodity1] = (tradingActivity[trade.commodity1] || 0) + 1;
        tradingActivity[trade.commodity2] = (tradingActivity[trade.commodity2] || 0) + 1;
      }
    });
    
    // Calculate percentages
    const totalActivity = Object.values(tradingActivity).reduce((sum, count) => sum + count, 0);
    const percentages = commodities.map(c => {
      const count = tradingActivity[c.id] || 0;
      return totalActivity > 0 ? (count / totalActivity) * 100 : 0;
    });
    
    // Update chart data
    this.commodityFlowChart.data.labels = commodities.map(c => c.displayName);
    this.commodityFlowChart.data.datasets[0].data = percentages;
    this.commodityFlowChart.data.datasets[0].backgroundColor = commodities.map(c => c.color);
    
    this.commodityFlowChart.update();
    
    // Also update the commodity usage analysis display
    this.updateCommodityUsageDisplay(percentages, commodities);
  }
  
  /**
   * Update commodity usage analysis display
   */
  updateCommodityUsageDisplay(percentages, commodities) {
    // Map commodity names to the correct element IDs
    const elementMap = {
      'barley': 'barley',
      'copper_tools': 'copper',
      'wool_textiles': 'wool'
    };
    
    // Find the money commodity (lowest storage cost)
    const moneyCommodity = commodities.reduce((min, commodity) => 
      commodity.storageCost < min.storageCost ? commodity : min
    );
    
    commodities.forEach((commodity, index) => {
      const elementId = elementMap[commodity.name];
      if (elementId) {
        const percentageElement = document.getElementById(`${elementId}-percentage`);
        const usageBarElement = document.getElementById(`${elementId}-usage`);
        const commodityNameElement = document.querySelector(`#${elementId}-percentage`)?.previousElementSibling;
        
        if (percentageElement) {
          const isMoney = commodity.id === moneyCommodity.id;
          const moneyIndicator = isMoney ? ' 💰' : '';
          percentageElement.textContent = `${percentages[index].toFixed(1)}%${moneyIndicator}`;
        }
        if (usageBarElement) {
          usageBarElement.style.width = `${percentages[index]}%`;
          // Highlight the money commodity
          if (commodity.id === moneyCommodity.id) {
            usageBarElement.style.backgroundColor = '#FFD700'; // Gold color for money
            usageBarElement.style.border = '2px solid #FFA500';
          }
        }
        if (commodityNameElement && commodity.id === moneyCommodity.id) {
          try {
            commodityNameElement.style.fontWeight = 'bold';
            commodityNameElement.style.color = '#B8860B';
          } catch (e) {
            console.warn('Could not style commodity name element:', e);
          }
        }
      }
    });
  }
  
  /**
   * Create efficiency chart
   */
  createEfficiencyChart() {
    const efficiencyContainer = document.createElement('div');
    efficiencyContainer.className = 'efficiency-container';
    efficiencyContainer.innerHTML = `
      <h5>Trading Efficiency Over Time</h5>
      <div id="efficiency-chart" class="efficiency-chart"></div>
    `;
    
    this.container.appendChild(efficiencyContainer);
    
    // Initialize efficiency chart
    this.initializeEfficiencyChart();
  }
  
  /**
   * Initialize efficiency chart
   */
  initializeEfficiencyChart() {
    const efficiencyElement = document.getElementById('efficiency-chart');
    if (!efficiencyElement) return;
    
    const canvas = document.createElement('canvas');
    canvas.id = 'efficiency-chart-canvas';
    efficiencyElement.appendChild(canvas);
    
    this.efficiencyChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Efficiency',
          data: [],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4
        }, {
          label: 'Monetary Circulation',
          data: [],
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 1,
            ticks: {
              callback: function(value) {
                return (value * 100).toFixed(0) + '%';
              }
            }
          }
        },
        plugins: {
          legend: {
            display: true
          }
        }
      }
    });
    
    this.efficiencyData = [];
  }
  
  /**
   * Update efficiency chart
   */
  updateEfficiencyChart() {
    if (!this.efficiencyChart || !this.simulation) return;
    
    const data = this.simulation.getSimulationData();
    const iteration = data.iteration;
    const efficiency = data.metrics.efficiency;
    const circulation = data.metrics.monetaryCirculation;
    
    // Add new data point
    this.efficiencyData.push({
      iteration: iteration,
      efficiency: efficiency,
      circulation: circulation
    });
    
    // Keep only last 100 data points
    if (this.efficiencyData.length > 100) {
      this.efficiencyData.shift();
    }
    
    // Update chart
    this.efficiencyChart.data.labels = this.efficiencyData.map(d => d.iteration);
    this.efficiencyChart.data.datasets[0].data = this.efficiencyData.map(d => d.efficiency);
    this.efficiencyChart.data.datasets[1].data = this.efficiencyData.map(d => d.circulation);
    
    this.efficiencyChart.update();
  }
  
  /**
   * Create convergence chart
   */
  createConvergenceChart() {
    const convergenceContainer = document.createElement('div');
    convergenceContainer.className = 'convergence-container';
    convergenceContainer.innerHTML = `
      <h5>Money Emergence Convergence</h5>
      <div id="convergence-chart" class="convergence-chart"></div>
    `;
    
    this.container.appendChild(convergenceContainer);
    
    // Initialize convergence chart
    this.initializeConvergenceChart();
  }
  
  /**
   * Initialize convergence chart
   */
  initializeConvergenceChart() {
    const convergenceElement = document.getElementById('convergence-chart');
    if (!convergenceElement) return;
    
    const canvas = document.createElement('canvas');
    canvas.id = 'convergence-chart-canvas';
    convergenceElement.appendChild(canvas);
    
    this.convergenceChart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: ['Barley', 'Copper Tools', 'Wool Textiles'],
        datasets: [{
          label: 'Usage as Money',
          data: [0, 0, 0],
          backgroundColor: ['#D4AF37', '#B87333', '#8B4513'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 1,
            ticks: {
              callback: function(value) {
                return (value * 100).toFixed(0) + '%';
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
    
    this.updateConvergenceChart();
  }
  
  /**
   * Update convergence chart
   */
  updateConvergenceChart() {
    if (!this.convergenceChart || !this.simulation) return;
    
    const data = this.simulation.getSimulationData();
    const trades = data.trades;
    const commodities = data.commodities;
    
    // Calculate money usage for each commodity using the simulation's money detection
    const moneyUsage = commodities.map(commodity => {
      const commodityTrades = trades.filter(trade => 
        this.simulation.isMoneyTrade(trade) && (trade.commodity1 === commodity.id || trade.commodity2 === commodity.id)
      );
      return commodityTrades.length / Math.max(1, trades.length);
    });
    
    this.convergenceChart.data.datasets[0].data = moneyUsage;
    this.convergenceChart.update();
  }
  
  /**
   * Update all visualizations
   */
  update() {
    if (!this.isInitialized) return;
    
    this.updateMetrics();
    this.updateNetworkGraph();
    this.updateCommodityFlow();
    this.updateEfficiencyChart();
    this.updateConvergenceChart();
  }
  
  /**
   * Update metrics display
   */
  updateMetrics() {
    if (!this.simulation) return;
    
    const data = this.simulation.getSimulationData();
    
    // Update metric displays
    const iterationElement = document.getElementById('iteration-metric');
    const tradesElement = document.getElementById('trades-metric');
    const efficiencyElement = document.getElementById('efficiency-metric');
    const circulationElement = document.getElementById('circulation-metric');
    
    if (iterationElement) iterationElement.textContent = data.iteration;
    if (tradesElement) tradesElement.textContent = data.trades.length;
    if (efficiencyElement) efficiencyElement.textContent = (data.metrics.efficiency * 100).toFixed(1) + '%';
    if (circulationElement) circulationElement.textContent = (data.metrics.monetaryCirculation * 100).toFixed(1) + '%';
  }
  
  /**
   * Reset all visualizations
   */
  reset() {
    this.efficiencyData = [];
    
    if (this.efficiencyChart) {
      this.efficiencyChart.data.labels = [];
      this.efficiencyChart.data.datasets[0].data = [];
      this.efficiencyChart.data.datasets[1].data = [];
      this.efficiencyChart.update();
    }
    
    if (this.convergenceChart) {
      this.convergenceChart.data.datasets[0].data = [0, 0, 0];
      this.convergenceChart.update();
    }
    
    this.update();
  }
}

// Export for global use
window.SimulationVisualization = SimulationVisualization;
