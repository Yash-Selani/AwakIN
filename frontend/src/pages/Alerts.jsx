import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { alertService } from '../services/alertService';
import { FaExclamationTriangle, FaMapMarkerAlt, FaClock, FaRobot } from 'react-icons/fa';
import { toast } from 'react-hot-toast';

const getSeverityColor = (severity) => {
  switch (severity?.toLowerCase()) {
    case 'extreme': return 'var(--color-accent-red)';
    case 'severe': return 'var(--color-warning-amber)';
    case 'moderate': return 'var(--color-warning-yellow)';
    case 'minor': return 'var(--color-success-green)';
    default: return 'var(--color-base-slate)';
  }
};

const ExplainModal = ({ alert, onClose, onExplain, loading, explanation }) => {
  if (!alert) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.7)',
      display: 'flex', justifyContent: 'center', alignItems: 'center',
      zIndex: 1000, padding: '1rem'
    }}>
      <div style={{
        backgroundColor: 'var(--color-base-navy)',
        padding: '2rem',
        borderRadius: '12px',
        maxWidth: '600px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        border: '1px solid var(--color-base-slate)'
      }}>
        <h2 style={{ marginBottom: '1rem', color: 'var(--color-text-primary)' }}>AI Explanation</h2>
        
        {!explanation && !loading && (
          <div style={{ textAlign: 'center', margin: '2rem 0' }}>
            <button 
              onClick={() => onExplain(alert)}
              style={{
                backgroundColor: 'var(--color-brand-blue)',
                color: 'white', border: 'none', padding: '0.75rem 1.5rem',
                borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'
              }}
            >
              Generate Explanation
            </button>
          </div>
        )}

        {loading && (
          <div style={{ textAlign: 'center', margin: '2rem 0', color: 'var(--color-text-secondary)' }}>
            <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
            Generating explanation using Gemini...
          </div>
        )}

        {explanation && (
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>English</h3>
              <p style={{ color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>{explanation.summary_en}</p>
              <ul style={{ color: 'var(--color-text-secondary)', paddingLeft: '1.5rem' }}>
                {explanation.precautions_en?.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>हिंदी</h3>
              <p style={{ color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>{explanation.summary_hi}</p>
              <ul style={{ color: 'var(--color-text-secondary)', paddingLeft: '1.5rem' }}>
                {explanation.precautions_hi?.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>
          </div>
        )}

        <button 
          onClick={onClose}
          style={{
            width: '100%', padding: '0.75rem', marginTop: '1rem',
            backgroundColor: 'transparent', color: 'var(--color-text-primary)',
            border: '1px solid var(--color-base-slate)', borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Close
        </button>
      </div>
    </div>
  );
};

const Alerts = () => {
  const { currentUser } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedState, setSelectedState] = useState('');
  
  const [explainModalAlert, setExplainModalAlert] = useState(null);
  const [explainLoading, setExplainLoading] = useState(false);
  const [explanation, setExplanation] = useState(null);

  useEffect(() => {
    fetchAlerts();
  }, [selectedState]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await alertService.getAlerts({ active: true, state: selectedState || undefined });
      setAlerts(data);
    } catch (error) {
      console.error('Failed to fetch alerts', error);
      toast.error('Failed to load alerts.');
    } finally {
      setLoading(false);
    }
  };

  const handleExplain = async (alert) => {
    if (!currentUser) {
      toast.error("Please login to use AI features.");
      return;
    }
    
    setExplainLoading(true);
    try {
      const token = await currentUser.getIdToken();
      const result = await alertService.explainAlert({
        alert_title: alert.title,
        alert_severity: alert.severity,
        alert_description: alert.description,
        alert_instruction: alert.instruction
      }, token);
      
      setExplanation(result);
    } catch (error) {
      console.error("Explanation failed", error);
      toast.error("Failed to generate AI explanation.");
    } finally {
      setExplainLoading(false);
    }
  };

  const openExplainModal = (alert) => {
    setExplainModalAlert(alert);
    setExplanation(null);
  };

  const states = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat", "Kerala", "Assam"];

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h1>Government Alerts</h1>
        
        <select 
          value={selectedState} 
          onChange={(e) => setSelectedState(e.target.value)}
          style={{
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            backgroundColor: 'var(--color-base-navy-light)',
            color: 'var(--color-text-primary)',
            border: '1px solid var(--color-base-slate)',
            outline: 'none'
          }}
        >
          <option value="">All Regions</option>
          {states.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-secondary)' }}>Loading alerts...</div>
      ) : alerts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', backgroundColor: 'var(--color-base-navy-light)', borderRadius: '12px', border: '1px solid var(--color-base-slate)' }}>
          <h3 style={{ color: 'var(--color-text-primary)' }}>No Active Alerts</h3>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>There are currently no active emergency alerts for the selected region.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
          {alerts.map(alert => (
            <div key={alert.id} style={{
              backgroundColor: 'var(--color-base-navy-light)',
              borderRadius: '12px',
              border: '1px solid var(--color-base-slate)',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column'
            }}>
              {/* Header colored by severity */}
              <div style={{
                backgroundColor: getSeverityColor(alert.severity),
                color: alert.severity?.toLowerCase() === 'minor' ? '#000' : '#fff',
                padding: '0.75rem 1rem',
                fontWeight: 'bold',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <FaExclamationTriangle />
                  {alert.severity || 'Unknown'} Severity
                </span>
                <span style={{ fontSize: '0.8rem', opacity: 0.9 }}>{alert.source}</span>
              </div>
              
              <div style={{ padding: '1.5rem', flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ marginBottom: '1rem', color: 'var(--color-text-primary)', fontSize: '1.1rem' }}>
                  {alert.title}
                </h3>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
                  {(alert.state || alert.area_desc) && (
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
                      <FaMapMarkerAlt style={{ marginTop: '3px', flexShrink: 0 }} />
                      <span>{alert.area_desc || `${alert.district ? alert.district + ', ' : ''}${alert.state}`}</span>
                    </div>
                  )}
                  
                  {alert.expires_at && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
                      <FaClock />
                      <span>Valid until: {new Date(alert.expires_at).toLocaleString()}</span>
                    </div>
                  )}
                </div>
                
                {alert.instruction && (
                  <div style={{ 
                    backgroundColor: 'rgba(59, 130, 246, 0.1)', 
                    borderLeft: '4px solid var(--color-brand-blue)',
                    padding: '1rem',
                    borderRadius: '0 8px 8px 0',
                    marginBottom: '1.5rem',
                    color: 'var(--color-text-secondary)',
                    fontSize: '0.95rem',
                    flexGrow: 1
                  }}>
                    <strong>Instructions:</strong> {alert.instruction}
                  </div>
                )}
                
                <div style={{ marginTop: 'auto' }}>
                  <button 
                    onClick={() => openExplainModal(alert)}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem',
                      backgroundColor: 'transparent',
                      color: 'var(--color-brand-blue)',
                      border: '1px solid var(--color-brand-blue)',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      transition: 'all 0.2s'
                    }}
                    onMouseOver={(e) => { e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)' }}
                    onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'transparent' }}
                  >
                    <FaRobot /> Explain this alert
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {explainModalAlert && (
        <ExplainModal 
          alert={explainModalAlert} 
          onClose={() => setExplainModalAlert(null)}
          onExplain={handleExplain}
          loading={explainLoading}
          explanation={explanation}
        />
      )}
    </div>
  );
};

export default Alerts;
