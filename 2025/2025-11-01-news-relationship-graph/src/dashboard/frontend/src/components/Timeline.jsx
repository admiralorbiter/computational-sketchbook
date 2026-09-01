import { useState, useEffect } from 'react';
import { getTimeline } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Timeline() {
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTimeline();
  }, []);

  const loadTimeline = async () => {
    try {
      setLoading(true);
      const response = await getTimeline();
      setTimeline(response.data.timeline);
    } catch (error) {
      console.error('Error loading timeline:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading timeline...</div>;
  }

  return (
    <div className="timeline">
      <h2>Article Timeline</h2>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={timeline}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#8884d8" name="Articles" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Timeline;

