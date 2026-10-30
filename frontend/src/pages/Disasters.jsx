import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Disasters.css';
import DisasterDetail from '../components/DisasterDetail';
import { toast } from 'react-hot-toast';

const Disasters = () => {
  const [disasters, setDisasters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDisaster, setSelectedDisaster] = useState(null);

  useEffect(() => {
    fetchDisasters();
  }, []);

  const fetchDisasters = async () => {
    try {
      const response = await api.get('/api/disasters/');
      setDisasters(response.data);
    } catch (err) {
      console.error('Error fetching disasters:', err);
      setError('Failed to load disasters. Please try again later.');
      toast.error('Failed to load disasters.');
    } finally {
      setLoading(false);
    }
  };

  const openDetail = (disaster) => {
    setSelectedDisaster(disaster);
  };

  const closeDetail = () => {
    setSelectedDisaster(null);
  };

  if (loading) {
    return <div className="disasters-container"><div className="loading-spinner"><div className="spinner"></div><p>Loading guidelines...</p></div></div>;
  }

  return (
    <div className="disasters-container">
      <div className="disasters-header">
        <h1>Emergency Guidelines</h1>
        <p>Select a disaster type to view safety protocols and access the AI Situation Guide.</p>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <div className="disasters-grid">
        {disasters.map((disaster) => (
          <div key={disaster.id} className="disaster-card" onClick={() => openDetail(disaster)}>
            <div className="disaster-icon">{disaster.icon || '⚠️'}</div>
            <h3 className="disaster-name">{disaster.name}</h3>
            {disaster.severity_note && (
              <p className="disaster-severity">{disaster.severity_note}</p>
            )}
          </div>
        ))}
      </div>

      {selectedDisaster && (
        <DisasterDetail disaster={selectedDisaster} onClose={closeDetail} />
      )}
    </div>
  );
};

export default Disasters;
