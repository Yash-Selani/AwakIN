import React, { useState, useEffect } from 'react';
import { fetchEmergencyNumbers } from '../services/emergencyService';

const EmergencyNumbersView = ({ isModal = false, onClose = () => {} }) => {
  const [numbers, setNumbers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadNumbers = async () => {
      try {
        setLoading(true);
        const data = await fetchEmergencyNumbers();
        setNumbers(data);
      } catch (err) {
        console.error(err);
        setError('Failed to load emergency numbers. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    loadNumbers();
  }, []);

  const filteredNumbers = numbers.filter(n => {
    const term = searchQuery.toLowerCase();
    return (
      n.label.toLowerCase().includes(term) ||
      n.number.toLowerCase().includes(term) ||
      (n.category && n.category.toLowerCase().includes(term)) ||
      (n.description && n.description.toLowerCase().includes(term))
    );
  });

  // Group by category (exclude 112 as it will be prominent at the top)
  const mainEmergencyNumber = "112";
  const categorized = filteredNumbers
    .filter(n => n.number !== mainEmergencyNumber)
    .reduce((acc, curr) => {
      const cat = curr.category || 'Other';
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(curr);
      return acc;
    }, {});

  const renderNumberCard = (n) => (
    <a 
      key={n.id || n.number}
      href={`tel:${n.number}`} 
      style={{
        backgroundColor: 'var(--color-base-navy-light)',
        padding: '1rem',
        borderRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        textDecoration: 'none',
        color: 'white',
        border: '1px solid var(--color-base-navy)',
        transition: 'transform 0.2s, border-color 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.borderColor = 'var(--color-accent-red)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.borderColor = 'var(--color-base-navy)';
      }}
    >
      <div>
        <div style={{ fontWeight: 'bold' }}>{n.label}</div>
        {n.description && (
          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
            {n.description}
          </div>
        )}
      </div>
      <div style={{ color: 'var(--color-accent-red)', fontWeight: 'bold', fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span>📞</span>
        {n.number}
      </div>
    </a>
  );

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      height: isModal ? 'auto' : '100%',
      maxHeight: isModal ? '80vh' : 'auto'
    }}>
      {/* Header Area */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '1.5rem',
        flexShrink: 0
      }}>
        <h2 style={{ color: 'var(--color-accent-red)', margin: 0 }}>Emergency Numbers</h2>
        {isModal && (
          <button onClick={onClose} style={{
            background: 'none',
            border: 'none',
            color: 'white',
            fontSize: '1.5rem',
            cursor: 'pointer',
            padding: '0.25rem'
          }}>&times;</button>
        )}
      </div>

      <div style={{
        overflowY: 'auto',
        paddingRight: '0.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        
        {/* Search Box */}
        <input 
          type="text" 
          placeholder="Search services, numbers..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid var(--color-base-navy-light)',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            color: 'white',
            outline: 'none'
          }}
        />

        {error && (
          <div style={{ backgroundColor: 'rgba(244, 67, 54, 0.1)', color: '#f44336', padding: '1rem', borderRadius: '6px' }}>
            {error}
          </div>
        )}

        {/* Prominent 112 Card */}
        {(!searchQuery || "112".includes(searchQuery) || "national emergency".includes(searchQuery.toLowerCase())) && (
          <a 
            href="tel:112"
            style={{
              backgroundColor: 'var(--color-accent-red)',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              textDecoration: 'none',
              boxShadow: '0 4px 12px rgba(244, 67, 54, 0.3)',
              transform: 'scale(1)',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <div>
              <h3 style={{ margin: 0, fontSize: '1.5rem' }}>National Emergency</h3>
              <div style={{ opacity: 0.9, marginTop: '0.25rem' }}>All-in-one emergency helpline</div>
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>112</div>
          </a>
        )}

        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: '2rem' }}>Loading numbers...</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {Object.keys(categorized).map(category => (
              <div key={category}>
                <h4 style={{ color: 'var(--color-text-secondary)', marginBottom: '0.75rem', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '1px' }}>
                  {category}
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {categorized[category].map(renderNumberCard)}
                </div>
              </div>
            ))}
            
            {filteredNumbers.length === 0 && !(!searchQuery || "112".includes(searchQuery)) && (
              <div style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: '2rem' }}>
                No emergency numbers found matching "{searchQuery}".
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EmergencyNumbersView;
