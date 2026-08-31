// D3.js visualization for the cosmic distance scale
function createScaleVisualization() {
    const container = document.getElementById('scale-visualization');
    if (!container) return;
    
    // Clear placeholder
    container.innerHTML = '';
    
    // Set dimensions
    const width = container.clientWidth;
    const height = 400;
    const margin = {top: 50, right: 50, bottom: 50, left: 80};
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Define data - cosmic distances in light years
    const data = [
        {name: "Proxima Centauri", distance: 4.2, type: "Star"},
        {name: "Sirius", distance: 8.6, type: "Star"},
        {name: "Betelgeuse", distance: 642, type: "Star"},
        {name: "Large Magellanic Cloud", distance: 158000, type: "Galaxy"},
        {name: "Andromeda Galaxy", distance: 2500000, type: "Galaxy"},
        {name: "Virgo Cluster", distance: 54000000, type: "Galaxy Cluster"},
        {name: "GN-z11 (Most distant galaxy)", distance: 13400000000, type: "Galaxy"}
    ];
    
    // Use log scale for x-axis due to vast range of distances
    const x = d3.scaleLog()
        .domain([1, d3.max(data, d => d.distance)])
        .range([0, width - margin.left - margin.right]);
    
    // Create y-axis scale
    const y = d3.scaleBand()
        .domain(data.map(d => d.name))
        .range([0, height - margin.top - margin.bottom])
        .padding(0.2);
    
    // Add x-axis
    svg.append('g')
        .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d => {
            if (d >= 1000000000) return `${d/1000000000}B`;
            if (d >= 1000000) return `${d/1000000}M`;
            if (d >= 1000) return `${d/1000}K`;
            return d;
        }));
    
    // Add x-axis label
    svg.append('text')
        .attr('text-anchor', 'middle')
        .attr('x', (width - margin.left - margin.right) / 2)
        .attr('y', height - margin.top - 10)
        .text('Distance (light years)');
    
    // Add y-axis
    svg.append('g')
        .call(d3.axisLeft(y));
    
    // Color scale based on object type
    const color = d3.scaleOrdinal()
        .domain(["Star", "Galaxy", "Galaxy Cluster"])
        .range(["#FFC107", "#2196F3", "#9C27B0"]);
    
    // Add bars
    svg.selectAll('.bar')
        .data(data)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('y', d => y(d.name))
        .attr('height', y.bandwidth())
        .attr('x', 0)
        .attr('width', 0)
        .attr('fill', d => color(d.type))
        .transition()
        .duration(1000)
        .attr('width', d => x(d.distance));
    
    // Add labels
    svg.selectAll('.label')
        .data(data)
        .enter()
        .append('text')
        .attr('class', 'label')
        .attr('y', d => y(d.name) + y.bandwidth() / 2)
        .attr('x', d => x(d.distance) + 5)
        .attr('dy', '.35em')
        .text(d => {
            if (d.distance >= 1000000000) return `${(d.distance/1000000000).toFixed(1)}B ly`;
            if (d.distance >= 1000000) return `${(d.distance/1000000).toFixed(1)}M ly`;
            if (d.distance >= 1000) return `${(d.distance/1000).toFixed(1)}K ly`;
            return `${d.distance} ly`;
        })
        .style('opacity', 0)
        .transition()
        .delay(1000)
        .duration(500)
        .style('opacity', 1);
    
    // Add legend
    const legend = svg.append('g')
        .attr('transform', `translate(${width - margin.left - margin.right - 100}, 0)`);
    
    const types = ["Star", "Galaxy", "Galaxy Cluster"];
    
    types.forEach((type, i) => {
        const legendRow = legend.append('g')
            .attr('transform', `translate(0, ${i * 20})`);
        
        legendRow.append('rect')
            .attr('width', 10)
            .attr('height', 10)
            .attr('fill', color(type));
        
        legendRow.append('text')
            .attr('x', 15)
            .attr('y', 10)
            .text(type);
    });
    
    // Add title
    svg.append('text')
        .attr('x', (width - margin.left - margin.right) / 2)
        .attr('y', -20)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
        .text('Cosmic Distance Scale (Logarithmic)');
    
    // Add note about logarithmic scale
    svg.append('text')
        .attr('x', (width - margin.left - margin.right) / 2)
        .attr('y', height - margin.top + 30)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .style('font-style', 'italic')
        .text('Note: Scale is logarithmic due to the vast range of distances');
}

// Interactive parallax demonstration
function createParallaxDemo() {
    const container = document.getElementById('parallax-demo');
    if (!container) return;
    
    // Clear placeholder
    container.innerHTML = '';
    
    // Create HTML structure for the interactive demo
    container.innerHTML = `
        <div class="parallax-demo-container">
            <div class="controls">
                <button id="reset-parallax" class="btn btn-small">Reset</button>
                <div class="slider-container">
                    <label for="earth-position">Earth's Position in Orbit:</label>
                    <input type="range" id="earth-position" min="0" max="100" value="0">
                </div>
            </div>
            <div class="parallax-visualization">
                <div class="space-background">
                    <div class="earth" id="earth-marker"></div>
                    <div class="star near-star" id="near-star"></div>
                    <div class="star far-star" id="far-star"></div>
                    <div class="parallax-angle" id="parallax-angle"></div>
                    <div class="star-label" id="near-star-label">Nearby Star</div>
                    <div class="star-label" id="far-star-label">Distant Star</div>
                </div>
            </div>
            <div class="parallax-info">
                <h4>Understanding Parallax</h4>
                <p>Parallax is the apparent shift in position of a nearby star relative to more distant stars as Earth orbits the Sun.</p>
                <p>Move the slider to see how the position of Earth in its orbit affects the apparent position of the nearby star against the background of distant stars.</p>
                <div class="parallax-data">
                    <div>Parallax Angle: <span id="angle-value">0.0</span> arcseconds</div>
                    <div>Calculated Distance: <span id="distance-value">0.0</span> parsecs</div>
                </div>
            </div>
        </div>
    `;
    
    // Add CSS for the parallax demo
    const style = document.createElement('style');
    style.textContent = `
        .parallax-demo-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .controls {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .slider-container {
            flex-grow: 1;
        }
        
        .parallax-visualization {
            height: 300px;
            position: relative;
            background-color: #000;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .space-background {
            width: 100%;
            height: 100%;
            position: relative;
        }
        
        .earth {
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: #2196F3;
            border-radius: 50%;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            box-shadow: 0 0 10px rgba(33, 150, 243, 0.8);
        }
        
        .star {
            position: absolute;
            background-color: #FFF;
            border-radius: 50%;
            box-shadow: 0 0 5px rgba(255, 255, 255, 0.8);
        }
        
        .near-star {
            width: 8px;
            height: 8px;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        
        .far-star {
            width: 6px;
            height: 6px;
            top: 30%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        
        .star-label {
            position: absolute;
            color: white;
            font-size: 12px;
        }
        
        #near-star-label {
            top: 55%;
            left: 50%;
            transform: translateX(-50%);
        }
        
        #far-star-label {
            top: 25%;
            left: 50%;
            transform: translateX(-50%);
        }
        
        .parallax-angle {
            position: absolute;
            border-left: 1px dashed rgba(255, 255, 255, 0.5);
            height: 100px;
            top: 30%;
            left: 50%;
        }
        
        .parallax-info {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
        }
        
        .parallax-data {
            margin-top: 15px;
            display: flex;
            justify-content: space-around;
            font-weight: bold;
        }
        
        .btn-small {
            padding: 5px 10px;
            font-size: 14px;
        }
    `;
    document.head.appendChild(style);
    
    // Add interactivity
    const earthPositionSlider = document.getElementById('earth-position');
    const resetButton = document.getElementById('reset-parallax');
    const earthMarker = document.getElementById('earth-marker');
    const nearStar = document.getElementById('near-star');
    const angleValue = document.getElementById('angle-value');
    const distanceValue = document.getElementById('distance-value');
    const parallaxAngle = document.getElementById('parallax-angle');
    
    // Initial positions
    let earthOrbitRadius = 100; // pixels
    let earthAngle = 0; // degrees
    
    // Update the visualization based on slider value
    function updateParallax() {
        // Convert slider value to angle in radians
        earthAngle = (earthPositionSlider.value / 100) * Math.PI * 2;
        
        // Calculate Earth's position in orbit
        const earthX = Math.cos(earthAngle) * earthOrbitRadius;
        
        // Update Earth's position
        earthMarker.style.transform = `translateX(calc(-50% + ${earthX}px))`;
        
        // Calculate parallax effect on near star
        // Simulating a star that's close enough to show parallax
        const parallaxShift = Math.sin(earthAngle) * 20; // pixels
        nearStar.style.transform = `translate(calc(-50% + ${parallaxShift}px), -50%)`;
        
        // Update the parallax angle line
        parallaxAngle.style.transform = `translateX(${parallaxShift}px)`;
        
        // Calculate and display the parallax angle in arcseconds
        // Simulating a realistic parallax angle calculation
        const simulatedParallaxAngle = Math.abs(Math.sin(earthAngle)) * 0.76; // max 0.76 arcseconds
        angleValue.textContent = simulatedParallaxAngle.toFixed(2);
        
        // Calculate distance in parsecs (1 parsec = 1/parallax in arcseconds)
        const distanceInParsecs = simulatedParallaxAngle > 0 ? (1 / simulatedParallaxAngle).toFixed(1) : "∞";
        distanceValue.textContent = distanceInParsecs;
    }
    
    // Event listeners
    earthPositionSlider.addEventListener('input', updateParallax);
    resetButton.addEventListener('click', function() {
        earthPositionSlider.value = 0;
        updateParallax();
    });
    
    // Initialize
    updateParallax();
}

// Initialize all interactive elements
document.addEventListener('DOMContentLoaded', function() {
    // Replace placeholder initializations with actual implementations
    initializeTimeline();
    createScaleVisualization();
    createParallaxDemo();
    initializeCepheidCalculator();
    initializeRedshiftCalculator();
    initializeHRDiagram();
    initializeQuiz();
});
