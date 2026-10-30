import React, { useState } from 'react';
import { getAIGuide } from '../services/aiService';

const AIGuidePanel = ({ disasterSlug, disasterName }) => {
  const [situationText, setSituationText] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [location, setLocation] = useState(null);
  const [gettingLocation, setGettingLocation] = useState(false);
  const [response, setResponse] = useState(null);

  const handleAttachLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }
    
    setGettingLocation(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lon: position.coords.longitude
        });
        setGettingLocation(false);
      },
      (error) => {
        console.error('Error getting location', error);
        alert('Could not access location. Please check your browser permissions.');
        setGettingLocation(false);
      },
      { timeout: 10000 }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!situationText.trim()) return;

    setLoading(true);
    setError('');
    setResponse(null);

    const payload = {
      disaster_slug: disasterSlug,
      situation_text: situationText,
      language,
      ...(location && { lat: location.lat, lon: location.lon })
    };

    try {
      const data = await getAIGuide(payload);
      setResponse(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate AI guide. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-panel">
      {!response ? (
        <>
          <div className="ai-intro">
            <h3>✨ Personalized AI Guidance</h3>
            <p>Describe your exact situation. Our AI will combine official {disasterName} protocols with your context to give you immediate actionable steps.</p>
          </div>

          <form onSubmit={handleSubmit} className="ai-form">
            <textarea
              placeholder="E.g., Water is entering my ground floor, and my elderly parent is with me..."
              value={situationText}
              onChange={(e) => setSituationText(e.target.value)}
              required
            />
            
            <div className="form-controls">
              <button 
                type="button" 
                className={`loc-btn ${location ? 'active' : ''}`}
                onClick={handleAttachLocation}
                disabled={gettingLocation}
              >
                📍 {gettingLocation ? 'Locating...' : location ? 'Location Attached' : 'Attach Location'}
              </button>
              
              <select 
                className="lang-select"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="hi">हिंदी (Hindi)</option>
              </select>

              <button type="submit" className="submit-btn" disabled={loading || !situationText.trim()}>
                {loading ? 'Analyzing...' : 'Get Guide'}
              </button>
            </div>
            {error && <div className="error-msg">{error}</div>}
          </form>
        </>
      ) : (
        <div className="ai-response">
          <div className="emergency-warning">
            ⚠️ <span>Call 112 for immediate danger</span>
          </div>

          <div className="form-controls" style={{ marginBottom: '1rem' }}>
             <button type="button" className="loc-btn" onClick={() => setResponse(null)}>
               ← New Query
             </button>
          </div>

          {response.immediate_actions && response.immediate_actions.length > 0 && (
            <div className="response-section">
              <h4>Immediate Actions</h4>
              <ul>
                {response.immediate_actions.map((act, i) => <li key={i}>{act}</li>)}
              </ul>
            </div>
          )}

          {response.precautions && response.precautions.length > 0 && (
            <div className="response-section">
              <h4>Precautions</h4>
              <ul>
                {response.precautions.map((act, i) => <li key={i}>{act}</li>)}
              </ul>
            </div>
          )}

          {response.first_aid && response.first_aid.length > 0 && (
            <div className="response-section">
              <h4>First Aid</h4>
              <ul>
                {response.first_aid.map((act, i) => <li key={i}>{act}</li>)}
              </ul>
            </div>
          )}

          {response.what_not_to_do && response.what_not_to_do.length > 0 && (
            <div className="response-section" style={{ borderLeft: '4px solid #ef4444', paddingLeft: '1rem' }}>
              <h4 style={{ color: '#ef4444', borderBottomColor: '#ef4444' }}>What NOT to do</h4>
              <ul>
                {response.what_not_to_do.map((act, i) => <li key={i}>{act}</li>)}
              </ul>
            </div>
          )}

          {response.who_to_call && response.who_to_call.length > 0 && (
            <div className="response-section">
              <h4>Who to Call</h4>
              <ul>
                {response.who_to_call.map((act, i) => <li key={i}>{act}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIGuidePanel;
