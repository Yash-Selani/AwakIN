import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { alertService } from '../services/alertService';
import { newsService } from '../services/newsService';
import { useNavigate } from 'react-router-dom';
import { FaExclamationTriangle, FaExternalLinkAlt } from 'react-icons/fa';

const Dashboard = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [topAlert, setTopAlert] = useState(null);
  const [latestNews, setLatestNews] = useState([]);

  useEffect(() => {
    // Fetch active alerts to show in banner
    const fetchTopAlert = async () => {
      try {
        const alerts = await alertService.getAlerts({ active: true });
        if (alerts && alerts.length > 0) {
          // Find highest severity alert. They are pre-sorted in the backend or we just take the first.
          setTopAlert(alerts[0]);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard alerts", err);
      }
    };
    
    const fetchLatestNews = async () => {
      try {
        const news = await newsService.getNews({ limit: 4 });
        setLatestNews(news);
      } catch (err) {
        console.error("Failed to fetch dashboard news", err);
      }
    };
    
    fetchTopAlert();
    fetchLatestNews();
  }, []);

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'extreme': return 'var(--color-accent-red)';
      case 'severe': return 'var(--color-warning-amber)';
      case 'moderate': return 'var(--color-warning-yellow)';
      case 'minor': return 'var(--color-success-green)';
      default: return 'var(--color-base-slate)';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', padding: '1rem' }}>
      {/* Alert Banner */}
      {topAlert && (
        <div style={{
          backgroundColor: getSeverityColor(topAlert.severity),
          color: topAlert.severity?.toLowerCase() === 'minor' ? '#000' : '#fff',
          padding: '1rem',
          borderRadius: '8px',
          fontWeight: 'bold',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FaExclamationTriangle /> {topAlert.severity?.toUpperCase()} ALERT: {topAlert.title}
          </span>
          <button 
            onClick={() => navigate('/alerts')}
            style={{
              background: 'transparent',
              border: `1px solid ${topAlert.severity?.toLowerCase() === 'minor' ? '#000' : '#fff'}`,
              color: 'inherit',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            View Details
          </button>
        </div>
      )}

      <h2>Welcome, {currentUser?.email || 'User'}</h2>

      {/* Quick Actions */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1rem'
      }}>
        <div style={{
          backgroundColor: 'var(--color-base-navy-light)',
          padding: '2rem',
          borderRadius: '12px',
          textAlign: 'center',
          cursor: 'pointer',
          border: '1px solid var(--color-text-secondary)'
        }}>
          <h3>🏥 Find Hospital</h3>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>Locate nearest medical facilities</p>
        </div>
        
        <div style={{
          backgroundColor: 'var(--color-accent-red)',
          padding: '2rem',
          borderRadius: '12px',
          textAlign: 'center',
          cursor: 'pointer',
          color: 'white'
        }}>
          <h3>📞 Call 112</h3>
          <p style={{ marginTop: '0.5rem' }}>Immediate emergency assistance</p>
        </div>

        <div style={{
          backgroundColor: 'var(--color-base-navy-light)',
          padding: '2rem',
          borderRadius: '12px',
          textAlign: 'center',
          cursor: 'pointer',
          border: '1px solid var(--color-text-secondary)'
        }}>
          <h3>🤖 I'm in danger</h3>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>Get AI Survival Guide</p>
        </div>
      </div>

      {/* News Strip */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0 }}>Latest Updates</h3>
          <button onClick={() => navigate('/news')} style={{ background: 'none', border: 'none', color: 'var(--color-brand-blue)', cursor: 'pointer', fontWeight: '500' }}>View All</button>
        </div>
        
        {latestNews.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: 'var(--color-base-navy-light)', borderRadius: '12px', border: '1px solid var(--color-base-slate)', color: 'var(--color-text-secondary)' }}>
            No recent updates found.
          </div>
        ) : (
          <div style={{
            display: 'flex',
            gap: '1rem',
            overflowX: 'auto',
            paddingBottom: '1rem',
            scrollSnapType: 'x mandatory'
          }}>
            {latestNews.map(item => (
              <div key={item.id} style={{
                minWidth: '300px',
                maxWidth: '300px',
                backgroundColor: 'var(--color-base-navy-light)',
                padding: '1.25rem',
                borderRadius: '12px',
                border: '1px solid var(--color-base-slate)',
                scrollSnapAlign: 'start',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                  <span>{item.source}</span>
                  {item.disaster_slug && (
                     <span style={{ color: 'var(--color-accent-red)', textTransform: 'capitalize', fontWeight: 'bold' }}>{item.disaster_slug}</span>
                  )}
                </div>
                
                <h4 style={{ margin: 0, fontSize: '1rem', lineHeight: '1.4' }}>{item.title}</h4>
                
                {item.summary && (
                  <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.875rem', lineHeight: '1.4', flexGrow: 1, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {item.summary}
                  </p>
                )}
                
                <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-brand-blue)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: '500', marginTop: 'auto' }}>
                  Read Source <FaExternalLinkAlt size={10} />
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
