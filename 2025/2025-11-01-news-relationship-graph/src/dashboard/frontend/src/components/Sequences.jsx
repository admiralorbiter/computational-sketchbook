import { useState, useEffect } from 'react';
import { getRelationships, getArticle } from '../api/client';

function Sequences() {
  const [sequences, setSequences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState('all');

  useEffect(() => {
    loadSequences();
  }, [selectedType]);

  const loadSequences = async () => {
    try {
      setLoading(true);
      const response = await getRelationships({
        rel_type: selectedType === 'all' ? '' : selectedType,
        min_strength: 0.5
      });
      
      const allRelationships = response.data.relationships;
      // Filter to only sequence types
      const sequenceTypes = ['follows_up', 'causes_chain', 'causal_chain', 'context_for'];
      const filtered = allRelationships.filter(rel => 
        sequenceTypes.some(type => rel.rel_type.includes(type))
      );
      
      // Load article details for each
      const sequencesWithDetails = await Promise.all(
        filtered.map(async (seq) => {
          const [sourceArt, targetArt] = await Promise.all([
            getArticle(seq.source_id),
            getArticle(seq.target_id)
          ]);
          return {
            ...seq,
            source_title: sourceArt.data.title,
            target_title: targetArt.data.title,
            source_date: sourceArt.data.date,
            target_date: targetArt.data.date
          };
        })
      );
      
      setSequences(sequencesWithDetails);
    } catch (error) {
      console.error('Error loading sequences:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading sequences...</div>;
  }

  const typeGroups = {
    'all': 'All Types',
    'follows_up': 'Follow-up Stories',
    'causes_chain': 'Causal Chains',
    'causal_chain': 'Causal Chains',
    'context_for': 'Context Relationships'
  };

  return (
    <div className="sequences">
      <h2>Sequential News Stories</h2>
      
      <div className="sequences-controls">
        <div className="type-filter">
          <label>Filter by type:</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
          >
            <option value="all">All Types</option>
            <option value="follows_up">Follow-up Stories</option>
            <option value="causes_chain">Causal Chains</option>
            <option value="context_for">Context</option>
          </select>
        </div>
        <div className="sequences-count">
          {sequences.length} sequential relationships found
        </div>
      </div>

      <div className="sequences-list">
        {sequences.map((seq, idx) => (
          <div key={idx} className="sequence-item">
            <div className="sequence-header">
              <span className="sequence-type">{seq.rel_type}</span>
              <span className="sequence-strength">Strength: {seq.strength.toFixed(2)}</span>
            </div>
            
            <div className="sequence-flow">
              <div className="sequence-from">
                <div className="sequence-arrow">→</div>
                <div className="sequence-art">
                  <span className="art-id">{seq.source_id}</span>
                  <span className="art-date">{seq.source_date}</span>
                  <span className="art-title">{seq.source_title}</span>
                </div>
              </div>
              
              <div className="sequence-reason">
                <strong>Reason:</strong> {seq.reason}
              </div>
              
              <div className="sequence-to">
                <div className="sequence-arrow">↓</div>
                <div className="sequence-art">
                  <span className="art-id">{seq.target_id}</span>
                  <span className="art-date">{seq.target_date}</span>
                  <span className="art-title">{seq.target_title}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {sequences.length === 0 && (
        <div className="placeholder">
          No sequences found with the selected filter
        </div>
      )}
    </div>
  );
}

export default Sequences;

