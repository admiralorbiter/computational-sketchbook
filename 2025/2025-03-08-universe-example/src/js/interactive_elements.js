// Cepheid variable distance calculator
function initializeCepheidCalculator() {
    const container = document.getElementById('cepheid-calculator');
    if (!container) return;
    
    // Clear placeholder
    container.innerHTML = '';
    
    // Create HTML structure for the calculator
    container.innerHTML = `
        <div class="calculator-container">
            <h4>Cepheid Variable Distance Calculator</h4>
            <p>Cepheid variables are stars that pulsate in a regular pattern. The period of pulsation is directly related to the star's luminosity, making them valuable "standard candles" for measuring cosmic distances.</p>
            
            <div class="calculator-form">
                <div class="form-group">
                    <label for="period-input">Pulsation Period (days):</label>
                    <input type="number" id="period-input" min="1" max="100" step="0.1" value="10">
                </div>
                
                <div class="form-group">
                    <label for="apparent-magnitude">Apparent Magnitude (m):</label>
                    <input type="number" id="apparent-magnitude" min="0" max="30" step="0.1" value="15">
                </div>
                
                <button id="calculate-distance" class="btn">Calculate Distance</button>
            </div>
            
            <div class="results-container">
                <div class="result-item">
                    <span class="result-label">Absolute Magnitude (M):</span>
                    <span id="absolute-magnitude-result">-</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Distance (parsecs):</span>
                    <span id="distance-parsecs-result">-</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Distance (light years):</span>
                    <span id="distance-ly-result">-</span>
                </div>
            </div>
            
            <div class="calculator-info">
                <h5>How it works:</h5>
                <p>1. The period-luminosity relation determines the absolute magnitude (M) of the Cepheid.</p>
                <p>2. By comparing the absolute magnitude with the apparent magnitude (m), we can calculate the distance using the distance modulus formula: m - M = 5 log(d/10)</p>
                <p>3. This calculator uses a simplified version of the period-luminosity relation: M = -2.43 × log(period) - 4.05</p>
            </div>
        </div>
    `;
    
    // Add CSS for the calculator
    const style = document.createElement('style');
    style.textContent = `
        .calculator-container {
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
        }
        
        .calculator-form {
            margin: 20px 0;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .form-group label {
            font-weight: bold;
        }
        
        .form-group input {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .results-container {
            margin: 20px 0;
            padding: 15px;
            background-color: #e8f5e9;
            border-radius: 6px;
        }
        
        .result-item {
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }
        
        .result-label {
            font-weight: bold;
        }
        
        .calculator-info {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
        
        .calculator-info h5 {
            margin-bottom: 10px;
        }
        
        .calculator-info p {
            margin-bottom: 5px;
            font-size: 0.9rem;
        }
    `;
    document.head.appendChild(style);
    
    // Add interactivity
    const periodInput = document.getElementById('period-input');
    const apparentMagnitudeInput = document.getElementById('apparent-magnitude');
    const calculateButton = document.getElementById('calculate-distance');
    const absoluteMagnitudeResult = document.getElementById('absolute-magnitude-result');
    const distanceParsecResult = document.getElementById('distance-parsecs-result');
    const distanceLyResult = document.getElementById('distance-ly-result');
    
    // Calculate distance based on period and apparent magnitude
    function calculateDistance() {
        const period = parseFloat(periodInput.value);
        const apparentMagnitude = parseFloat(apparentMagnitudeInput.value);
        
        // Calculate absolute magnitude using period-luminosity relation
        // M = -2.43 × log(period) - 4.05 (simplified version)
        const absoluteMagnitude = -2.43 * Math.log10(period) - 4.05;
        
        // Calculate distance using distance modulus formula
        // m - M = 5 log(d/10)
        // d = 10 × 10^((m - M)/5)
        const distanceModulus = apparentMagnitude - absoluteMagnitude;
        const distanceParsecs = 10 * Math.pow(10, distanceModulus/5);
        
        // Convert parsecs to light years (1 parsec = 3.26 light years)
        const distanceLightYears = distanceParsecs * 3.26;
        
        // Display results
        absoluteMagnitudeResult.textContent = absoluteMagnitude.toFixed(2);
        distanceParsecResult.textContent = distanceParsecs.toLocaleString(undefined, {maximumFractionDigits: 0});
        distanceLyResult.textContent = distanceLightYears.toLocaleString(undefined, {maximumFractionDigits: 0});
    }
    
    // Event listeners
    calculateButton.addEventListener('click', calculateDistance);
    
    // Initialize with default values
    calculateDistance();
}

// Redshift distance calculator
function initializeRedshiftCalculator() {
    const container = document.getElementById('redshift-calculator');
    if (!container) return;
    
    // Clear placeholder
    container.innerHTML = '';
    
    // Create HTML structure for the calculator
    container.innerHTML = `
        <div class="calculator-container">
            <h4>Redshift Distance Calculator</h4>
            <p>Redshift occurs when light from distant galaxies is stretched to longer wavelengths due to the expansion of the universe. The amount of redshift is directly related to the galaxy's distance and recession velocity.</p>
            
            <div class="calculator-form">
                <div class="form-group">
                    <label for="redshift-input">Redshift (z):</label>
                    <input type="number" id="redshift-input" min="0" max="10" step="0.01" value="0.5">
                </div>
                
                <div class="form-group">
                    <label for="hubble-constant">Hubble Constant (km/s/Mpc):</label>
                    <input type="number" id="hubble-constant" min="50" max="100" step="0.1" value="70">
                </div>
                
                <button id="calculate-redshift-distance" class="btn">Calculate Distance</button>
            </div>
            
            <div class="results-container">
                <div class="result-item">
                    <span class="result-label">Recession Velocity:</span>
                    <span id="velocity-result">-</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Distance (Mpc):</span>
                    <span id="distance-mpc-result">-</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Distance (million light years):</span>
                    <span id="distance-mly-result">-</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Lookback Time (billion years):</span>
                    <span id="lookback-time-result">-</span>
                </div>
            </div>
            
            <div class="calculator-info">
                <h5>How it works:</h5>
                <p>1. For small redshifts (z < 0.1), velocity ≈ c × z, where c is the speed of light (300,000 km/s).</p>
                <p>2. Distance is calculated using Hubble's Law: d = v/H₀, where H₀ is the Hubble constant.</p>
                <p>3. For larger redshifts, this calculator uses a simplified approximation that accounts for some relativistic effects.</p>
                <p>Note: This is a simplified model. For very high redshifts (z > 1), more complex cosmological models are needed.</p>
            </div>
        </div>
    `;
    
    // Add interactivity
    const redshiftInput = document.getElementById('redshift-input');
    const hubbleConstantInput = document.getElementById('hubble-constant');
    const calculateButton = document.getElementById('calculate-redshift-distance');
    const velocityResult = document.getElementById('velocity-result');
    const distanceMpcResult = document.getElementById('distance-mpc-result');
    const distanceMlyResult = document.getElementById('distance-mly-result');
    const lookbackTimeResult = document.getElementById('lookback-time-result');
    
    // Calculate distance based on redshift and Hubble constant
    function calculateRedshiftDistance() {
        const redshift = parseFloat(redshiftInput.value);
        const hubbleConstant = parseFloat(hubbleConstantInput.value);
        const speedOfLight = 299792.458; // km/s
        
        // Calculate recession velocity (simplified for small z)
        let velocity;
        if (redshift < 0.1) {
            velocity = redshift * speedOfLight;
        } else {
            // More accurate formula for higher redshifts
            velocity = ((1 + redshift)**2 - 1) / ((1 + redshift)**2 + 1) * speedOfLight;
        }
        
        // Calculate distance using Hubble's Law
        const distanceMpc = velocity / hubbleConstant;
        
        // Convert to million light years (1 Mpc = 3.26 million light years)
        const distanceMly = distanceMpc * 3.26;
        
        // Approximate lookback time (in billions of years)
        // This is a simplified calculation
        const lookbackTime = distanceMly / 3.26 / (hubbleConstant / 100);
        
        // Display results
        velocityResult.textContent = velocity.toLocaleString(undefined, {maximumFractionDigits: 0}) + " km/s";
        distanceMpcResult.textContent = distanceMpc.toLocaleString(undefined, {maximumFractionDigits: 2});
        distanceMlyResult.textContent = distanceMly.toLocaleString(undefined, {maximumFractionDigits: 0});
        lookbackTimeResult.textContent = lookbackTime.toLocaleString(undefined, {maximumFractionDigits: 2});
    }
    
    // Event listeners
    calculateButton.addEventListener('click', calculateRedshiftDistance);
    
    // Initialize with default values
    calculateRedshiftDistance();
}

// HR Diagram interactive visualization
function initializeHRDiagram() {
    const container = document.getElementById('hr-diagram');
    if (!container) return;
    
    // Clear placeholder
    container.innerHTML = '';
    
    // Set dimensions
    const width = container.clientWidth;
    const height = 500;
    const margin = {top: 50, right: 50, bottom: 70, left: 70};
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Define data - star types with temperature and luminosity
    const starData = [
        {type: "O", temperature: 40000, luminosity: 100000, examples: ["Mintaka", "Alnitak"], color: "#9bb0ff"},
        {type: "B", temperature: 20000, luminosity: 1000, examples: ["Rigel", "Spica"], color: "#aabfff"},
        {type: "A", temperature: 10000, luminosity: 100, examples: ["Sirius", "Vega"], color: "#cad7ff"},
        {type: "F", temperature: 7000, luminosity: 10, examples: ["Procyon", "Canopus"], color: "#f8f7ff"},
        {type: "G", temperature: 5500, luminosity: 1, examples: ["Sun", "Alpha Centauri A"], color: "#fff4ea"},
        {type: "K", temperature: 4000, luminosity: 0.1, examples: ["Arcturus", "Aldebaran"], color: "#ffd2a1"},
        {type: "M", temperature: 3000, luminosity: 0.01, examples: ["Proxima Centauri", "Betelgeuse"], color: "#ffcc6f"},
        // Giants and supergiants
        {type: "Giant", temperature: 4500, luminosity: 100, examples: ["Aldebaran"], color: "#ffd2a1"},
        {type: "Supergiant", temperature: 3500, luminosity: 10000, examples: ["Betelgeuse"], color: "#ffcc6f"},
        // White dwarfs
        {type: "White Dwarf", temperature: 10000, luminosity: 0.01, examples: ["Sirius B"], color: "#cad7ff"}
    ];
    
    // Create scales
    // Temperature is plotted in reverse (hotter stars on left)
    const x = d3.scaleLog()
        .domain([50000, 2000])
        .range([0, width - margin.left - margin.right]);
    
    const y = d3.scaleLog()
        .domain([0.0001, 1000000])
        .range([height - margin.top - margin.bottom, 0]);
    
    // Add x-axis
    svg.append('g')
        .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d => d.toLocaleString()));
    
    // Add x-axis label
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('x', (width - margin.left - margin.right) / 2)
        .attr('y', height - margin.top - 10)
        .text('Surface Temperature (K)');
    
    // Add secondary x-axis label for spectral class
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('x', (width - margin.left - margin.right) / 2)
        .attr('y', height - margin.top + 30)
        .text('Spectral Class: O B A F G K M');
    
    // Add y-axis
    svg.append('g')
        .call(d3.axisLeft(y).tickFormat(d => {
            if (d === 1) return "1 (Sun)";
            return d.toString();
        }));
    
    // Add y-axis label
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('transform', 'rotate(-90)')
        .attr('x', -(height - margin.top - margin.bottom) / 2)
        .attr('y', -50)
        .text('Luminosity (Sun = 1)');
    
    // Add main sequence line
    const mainSequenceData = [
        {temperature: 40000, luminosity: 100000},
        {temperature: 20000, luminosity: 1000},
        {temperature: 10000, luminosity: 100},
        {temperature: 7000, luminosity: 10},
        {temperature: 5500, luminosity: 1},
        {temperature: 4000, luminosity: 0.1},
        {temperature: 3000, luminosity: 0.01}
    ];
    
    const line = d3.line()
        .x(d => x(d.temperature))
        .y(d => y(d.luminosity))
        .curve(d3.curveMonotoneX);
    
    svg.append('path')
        .datum(mainSequenceData)
        .attr('fill', 'none')
        .attr('stroke', '#666')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('d', line);
    
    // Add stars
    svg.selectAll('.star')
        .data(starData)
        .enter()
        .append('circle')
        .attr('class', 'star')
        .attr('cx', d => x(d.temperature))
        .attr('cy', d => y(d.luminosity))
        .attr('r', 8)
        .attr('fill', d => d.color)
        .attr('stroke', '#333')
        .attr('stroke-width', 1)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('r', 12);
            
            // Show tooltip
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(`
                <strong>Type:</strong> ${d.type}<br>
                <strong>Temperature:</strong> ${d.temperature.toLocaleString()} K<br>
                <strong>Luminosity:</strong> ${d.luminosity} × Sun<br>
                <strong>Examples:</strong> ${d.examples.join(', ')}
            `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
            d3.select(this).attr('r', 8);
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
    
    // Add star labels
    svg.selectAll('.star-label')
        .data(starData)
        .enter()
        .append('text')
        .attr('class', 'star-label')
        .attr('x', d => x(d.temperature))
        .attr('y', d => y(d.luminosity) - 15)
        .attr('text-anchor', 'middle')
        .text(d => d.type)
        .style('font-size', '12px')
        .style('font-weight', 'bold');
    
    // Add regions
    svg.append('text')
        .attr('x', x(30000))
        .attr('y', y(10))
        .attr('text-anchor', 'middle')
        .text('Main Sequence')
        .style('font-size', '14px')
        .style('font-style', 'italic');
    
    svg.append('text')
        .attr('x', x(4000))
        .attr('y', y(1000))
        .attr('text-anchor', 'middle')
        .text('Giants')
        .style('font-size', '14px')
        .style('font-style', 'italic');
    
    svg.append('text')
        .attr('x', x(10000))
        .attr('y', y(0.001))
        .attr('text-anchor', 'middle')
        .text('White Dwarfs')
        .style('font-size', '14px')
        .style('font-style', 'italic');
    
    // Add title
    svg.append('text')
        .attr('x', (width - margin.left - margin.right) / 2)
        .attr('y', -20)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
        .text('Hertzsprung-Russell Diagram');
    
    // Add tooltip
    const tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0)
        .style('position', 'absolute')
        .style('background-color', 'white')
        .style('border', '1px solid #ddd')
        .style('border-radius', '5px')
        .style('padding', '10px')
        .style('pointer-events', 'none')
        .style('font-size', '12px')
        .style('z-index', 100);
    
    // Add explanation
    container.insertAdjacentHTML('beforeend', `
        <div class="hr-diagram-info" style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 8px;">
            <h5>Understanding the HR Diagram</h5>
            <p>The Hertzsprung-Russell diagram plots stars according to their temperature (x-axis) and luminosity (y-axis). It reveals several distinct groupings:</p>
            <ul style="margin-left: 20px; margin-top: 10px;">
                <li><strong>Main Sequence:</strong> Where most stars spend the majority of their lives, including our Sun.</li>
                <li><strong>Giants and Supergiants:</strong> Evolved stars with high luminosity but relatively cool temperatures.</li>
                <li><strong>White Dwarfs:</strong> Remnants of stars that have exhausted their nuclear fuel, with high temperature but low luminosity.</li>
            </ul>
            <p style="margin-top: 10px;">Astronomers use the HR diagram to determine stellar distances by comparing the apparent brightness of stars with their expected absolute brightness based on their spectral classification.</p>
        </div>
    `);
}
