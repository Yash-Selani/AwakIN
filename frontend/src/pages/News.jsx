import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { newsService } from '../services/newsService';
import { FaExternalLinkAlt, FaInfoCircle, FaExclamationCircle } from 'react-icons/fa';

const DISASTER_TYPES = [
  'All', 'flood', 'earthquake', 'fire', 'cyclone', 'landslide', 'accident', 'blast'
];

const News = () => {
  const [newsItems, setNewsItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('All');

  const fetchNews = async () => {
    try {
      const params = filter !== 'All' ? { disaster: filter } : {};
      const data = await newsService.getNews(params);
      setNewsItems(data);
    } catch (err) {
      console.error("Failed to fetch news", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchNews();

    // Auto-refresh every 2 minutes without scroll jump
    const interval = setInterval(fetchNews, 2 * 60 * 1000);
    return () => clearInterval(interval);
  }, [filter]);

  const getTimeAgo = (dateStr) => {
    if (!dateStr) return '';
    const diff = (new Date() - new Date(dateStr)) / 1000; // in seconds
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h1 style={{ margin: 0 }}>Nearby-Incident News</h1>
      </div>

      <div style={{
        backgroundColor: 'var(--color-warning-amber)',
        color: '#000',
        padding: '0.75rem 1rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        fontWeight: '500'
      }}>
        <FaInfoCircle />
        <span>News reports, not official alerts. <Link to="/alerts" style={{ color: '#000', textDecoration: 'underline', fontWeight: 'bold' }}>View Official Alerts</Link></span>
      </div>

      {/* Filter Chips */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        {DISASTER_TYPES.map(type => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              border: '1px solid var(--color-base-slate)',
              backgroundColor: filter === type ? 'var(--color-brand-blue)' : 'var(--color-base-navy)',
              color: 'white',
              cursor: 'pointer',
              textTransform: 'capitalize',
              fontWeight: filter === type ? 'bold' : 'normal',
              transition: 'all 0.2s ease'
            }}
          >
            {type}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} style={{ backgroundColor: 'var(--color-base-navy-light)', height: '200px', borderRadius: '12px', animation: 'pulse 1.5s infinite' }} />
          ))}
        </div>
      ) : newsItems.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-text-secondary)' }}>
          <FaExclamationCircle size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
          <h2>No incidents reported near you</h2>
          <p>We are constantly monitoring for updates. Check back later.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {newsItems.map(item => (
            <div key={item.id} style={{
              backgroundColor: 'var(--color-base-navy-light)',
              borderRadius: '12px',
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
              border: '1px solid var(--color-base-slate)',
              transition: 'transform 0.2s ease, box-shadow 0.2s ease',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                <span style={{ fontWeight: '500' }}>{item.source}</span>
                <span>{getTimeAgo(item.published_at)}</span>
              </div>
              
              <h3 style={{ margin: 0, fontSize: '1.125rem', lineHeight: '1.4' }}>{item.title}</h3>
              
              {item.summary && (
                <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.95rem', lineHeight: '1.5', flexGrow: 1 }}>
                  {item.summary}
                </p>
              )}
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--color-base-slate)' }}>
                {item.disaster_slug ? (
                  <span style={{
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    color: 'var(--color-accent-red)',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: 'bold',
                    textTransform: 'capitalize'
                  }}>
                    {item.disaster_slug} {item.city ? `• ${item.city}` : ''}
                  </span>
                ) : (
                  <span />
                )}
                
                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-brand-blue)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: '500' }}
                >
                  Read Source <FaExternalLinkAlt size={12} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <style>{`
        @keyframes pulse {
          0% { opacity: 0.6; }
          50% { opacity: 0.3; }
          100% { opacity: 0.6; }
        }
      `}</style>
    </div>
  );
};

export default News;
