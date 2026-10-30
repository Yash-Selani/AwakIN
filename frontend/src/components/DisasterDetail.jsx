import React, { useState } from 'react';
import AIGuidePanel from './AIGuidePanel';

const DisasterDetail = ({ disaster, onClose }) => {
  const [activeTab, setActiveTab] = useState('before');
  const guide = disaster.guides && disaster.guides.length > 0 ? disaster.guides[0] : null;

  const renderList = (data) => {
    if (!data) return <p>No specific guidelines available.</p>;
    
    // Depending on DB format (could be array or object)
    let items = [];
    if (Array.isArray(data)) {
      items = data;
    } else if (typeof data === 'object') {
      items = Object.values(data);
    }

    if (items.length === 0) return <p>No specific guidelines available.</p>;

    return (
      <ul className="guide-list">
        {items.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="disaster-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            <span className="disaster-icon">{disaster.icon}</span>
            {disaster.name} Guidelines
          </h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="tabs-header">
          <button 
            className={`tab-btn ${activeTab === 'before' ? 'active' : ''}`}
            onClick={() => setActiveTab('before')}
          >Before</button>
          <button 
            className={`tab-btn ${activeTab === 'during' ? 'active' : ''}`}
            onClick={() => setActiveTab('during')}
          >During</button>
          <button 
            className={`tab-btn ${activeTab === 'after' ? 'active' : ''}`}
            onClick={() => setActiveTab('after')}
          >After</button>
          <button 
            className={`tab-btn ${activeTab === 'first_aid' ? 'active' : ''}`}
            onClick={() => setActiveTab('first_aid')}
          >First Aid</button>
          <button 
            className={`tab-btn ${activeTab === 'ai' ? 'active' : ''}`}
            onClick={() => setActiveTab('ai')}
          >✨ AI Guide</button>
        </div>

        <div className="tab-content">
          {activeTab === 'before' && (
            <div className="guide-section">
              <h3>Before {disaster.name}</h3>
              {renderList(guide?.before_steps)}
            </div>
          )}
          {activeTab === 'during' && (
            <div className="guide-section">
              <h3>During {disaster.name}</h3>
              {renderList(guide?.during_steps)}
            </div>
          )}
          {activeTab === 'after' && (
            <div className="guide-section">
              <h3>After {disaster.name}</h3>
              {renderList(guide?.after_steps)}
            </div>
          )}
          {activeTab === 'first_aid' && (
            <div className="guide-section">
              <h3>First Aid</h3>
              {renderList(guide?.first_aid)}
            </div>
          )}
          {activeTab === 'ai' && (
            <AIGuidePanel disasterSlug={disaster.slug} disasterName={disaster.name} />
          )}
        </div>
      </div>
    </div>
  );
};

export default DisasterDetail;
