import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchDepartments } from '../services/emergencyService';

const CATEGORIES = ['All', 'police', 'fire_station', 'hospital', 'disaster_response'];

const mapTypeMapping = {
  'police': 'police',
  'fire_station': 'fire_station',
  'hospital': 'hospital',
  'disaster_response': 'hospital', // fallback
};

const Departments = () => {
  const [departments, setDepartments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchDepartments();
        setDepartments(data);
      } catch (err) {
        console.error(err);
        setError('Failed to load departments. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const filteredDepartments = departments.filter(dep => {
    const term = searchQuery.toLowerCase();
    const matchesSearch = 
      dep.name.toLowerCase().includes(term) ||
      (dep.description && dep.description.toLowerCase().includes(term)) ||
      (dep.state && dep.state.toLowerCase().includes(term));
      
    const matchesCategory = selectedCategory === 'All' || dep.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', minHeight: 'calc(100vh - 73px)' }}>
      <h1 style={{ color: 'white', marginBottom: '1.5rem', textAlign: 'center' }}>Emergency Departments</h1>
      
      {/* Filters Area */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '1rem', 
        marginBottom: '2rem',
        backgroundColor: 'var(--color-base-navy-light)',
        padding: '1.5rem',
        borderRadius: '12px'
      }}>
        <input 
          type="text" 
          placeholder="Search by name, description, or state..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid var(--color-base-navy)',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            color: 'white',
            outline: 'none'
          }}
        />

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                backgroundColor: selectedCategory === cat ? 'var(--color-accent-red)' : 'rgba(255, 255, 255, 0.1)',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '20px',
                cursor: 'pointer',
                fontWeight: selectedCategory === cat ? 'bold' : 'normal',
                textTransform: 'capitalize',
                transition: 'background-color 0.2s'
              }}
            >
              {cat.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'rgba(244, 67, 54, 0.1)', color: '#f44336', padding: '1rem', borderRadius: '6px', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: '2rem' }}>Loading departments...</div>
      ) : (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
          gap: '1.5rem' 
        }}>
          {filteredDepartments.map(dep => {
            const mapType = mapTypeMapping[dep.category] || 'hospital';
            return (
              <div 
                key={dep.id} 
                style={{
                  backgroundColor: 'var(--color-base-navy-light)',
                  border: '1px solid var(--color-base-navy)',
                  borderRadius: '12px',
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem',
                  transition: 'transform 0.2s',
                }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div>
                  <h3 style={{ margin: '0 0 0.5rem 0', color: 'white' }}>{dep.name}</h3>
                  {dep.category && (
                    <span style={{ 
                      fontSize: '0.75rem', 
                      backgroundColor: 'rgba(255,255,255,0.1)', 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px',
                      color: 'var(--color-text-secondary)',
                      textTransform: 'capitalize'
                    }}>
                      {dep.category.replace('_', ' ')}
                    </span>
                  )}
                </div>
                
                {dep.description && (
                  <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-text-secondary)', flexGrow: 1 }}>
                    {dep.description}
                  </p>
                )}
                
                {dep.state && (
                  <div style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                    📍 State: {dep.state}
                  </div>
                )}

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: 'auto' }}>
                  {dep.phone && (
                    <a 
                      href={`tel:${dep.phone}`}
                      style={{
                        backgroundColor: 'var(--color-accent-red)',
                        color: 'white',
                        textAlign: 'center',
                        textDecoration: 'none',
                        padding: '0.75rem',
                        borderRadius: '6px',
                        fontWeight: 'bold',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      <span>📞</span> Call {dep.phone}
                    </a>
                  )}

                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    {dep.website && (
                      <a 
                        href={dep.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          flex: 1,
                          backgroundColor: 'rgba(255, 255, 255, 0.1)',
                          color: 'white',
                          textAlign: 'center',
                          textDecoration: 'none',
                          padding: '0.5rem',
                          borderRadius: '6px',
                          fontSize: '0.9rem'
                        }}
                      >
                        🌐 Website
                      </a>
                    )}
                    
                    <Link 
                      to={`/map?type=${mapType}`}
                      style={{
                        flex: 1,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        color: 'white',
                        textAlign: 'center',
                        textDecoration: 'none',
                        padding: '0.5rem',
                        borderRadius: '6px',
                        fontSize: '0.9rem'
                      }}
                    >
                      🗺️ Show on map
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
          
          {filteredDepartments.length === 0 && (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--color-text-secondary)' }}>
              No departments found matching your criteria.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Departments;
