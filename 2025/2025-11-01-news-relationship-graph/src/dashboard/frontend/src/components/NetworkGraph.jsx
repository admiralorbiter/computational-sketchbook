import { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { getNetwork } from '../api/client';

function NetworkGraph() {
  const svgRef = useRef();
  const [loading, setLoading] = useState(true);
  const [minStrength, setMinStrength] = useState(0.5);
  const [networkData, setNetworkData] = useState(null);

  useEffect(() => {
    loadNetworkData();
  }, [minStrength]);

  const loadNetworkData = async () => {
    try {
      setLoading(true);
      const response = await getNetwork({ min_strength: minStrength, limit: 500 });
      setNetworkData(response.data);
    } catch (error) {
      console.error('Error loading network:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!networkData || loading) return;

    // Clear previous render
    d3.select(svgRef.current).selectAll('*').remove();

    const width = svgRef.current.clientWidth || 1200;
    const height = svgRef.current.clientHeight || 800;

    // Create force simulation
    const simulation = d3.forceSimulation(networkData.nodes)
      .force('link', d3.forceLink(networkData.edges).id(d => d.id).distance(d => 100 / (d.strength || 1)))
      .force('charge', d3.forceManyBody().strength(-100))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => 10 + d.connections / 10));

    const svg = d3.select(svgRef.current);
    const g = svg.append('g');

    // Add zoom
    const zoom = d3.zoom()
      .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    // Create links
    const link = g.append('g')
      .selectAll('line')
      .data(networkData.edges)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', d => d.strength * 0.8)
      .attr('stroke-width', d => d.strength * 3);

    // Create nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(networkData.nodes)
      .enter().append('circle')
      .attr('r', d => 5 + d.connections / 10)
      .attr('fill', d => getCategoryColor(d.category))
      .call(drag(simulation));

    // Add labels
    const label = g.append('g')
      .selectAll('text')
      .data(networkData.nodes)
      .enter().append('text')
      .text(d => d.title.length > 30 ? d.title.substring(0, 30) + '...' : d.title)
      .attr('font-size', '10px')
      .attr('dx', 10)
      .attr('dy', 5);

    // Add tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0);

    node.on('mouseover', (event, d) => {
      tooltip.transition().duration(200).style('opacity', .9);
      tooltip.html(`
        <strong>${d.title}</strong><br/>
        Category: ${d.category}<br/>
        Connections: ${d.connections}
      `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px');
    })
    .on('mouseout', () => {
      tooltip.transition().duration(200).style('opacity', 0);
    });

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });

    // Cleanup
    return () => {
      d3.select('body').selectAll('.tooltip').remove();
    };
  }, [networkData, loading]);

  const getCategoryColor = (category) => {
    const colors = {
      'Legal & Judicial': '#8884d8',
      'Education & Research': '#82ca9d',
      'Immigration & Border': '#ffc658',
      'Federal Spending & Cuts': '#ff7300',
      'Media & Info Control': '#0088fe',
      'Civil Rights & Democracy': '#00c49f',
      'International Relations': '#ffbb28',
      'Government Workforce': '#ff8042',
      'Musk/Doge': '#d62728',
    };
    return colors[category] || '#888888';
  };

  const drag = (simulation) => {
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    return d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  };

  if (loading) {
    return <div className="loading">Loading network graph...</div>;
  }

  return (
    <div className="network-graph">
      <div className="network-controls">
        <h2>Article Relationship Network</h2>
        <div className="control-group">
          <label>Min Strength:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={minStrength}
            onChange={(e) => setMinStrength(parseFloat(e.target.value))}
          />
          <span>{minStrength}</span>
        </div>
      </div>
      <svg ref={svgRef} className="network-svg" width="100%" height="800"></svg>
    </div>
  );
}

export default NetworkGraph;

