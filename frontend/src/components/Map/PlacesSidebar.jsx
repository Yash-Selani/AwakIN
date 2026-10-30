import React from 'react';

const PlacesSidebar = ({ places, selectedPlaceId, onPlaceClick }) => {
  if (!places || places.length === 0) {
    return (
      <div style={styles.empty}>
        No places found. Try adjusting filters or searching a different area.
      </div>
    );
  }

  return (
    <div style={styles.list}>
      {places.map(place => {
        const isSelected = selectedPlaceId === place.id;
        return (
          <div
            key={place.id}
            style={{
              ...styles.item,
              ...(isSelected ? styles.itemActive : {})
            }}
            onClick={() => onPlaceClick(place.id)}
          >
            <h3 style={styles.name}>{place.name}</h3>
            <p style={styles.address}>{place.address}</p>
            
            <div style={styles.metaRow}>
              {place.distance_meters !== null && (
                <span style={styles.distance}>{(place.distance_meters / 1000).toFixed(1)} km away</span>
              )}
              {place.open_now !== null && (
                <span style={{
                  ...styles.status,
                  color: place.open_now ? '#4caf50' : '#f44336'
                }}>
                  {place.open_now ? 'Open Now' : 'Closed'}
                </span>
              )}
            </div>

            <div style={styles.actions}>
              {place.phone_number && (
                <a
                  href={`tel:${place.phone_number.replace(/\s+/g, '')}`}
                  style={styles.btnCall}
                  onClick={(e) => e.stopPropagation()}
                >
                  Call
                </a>
              )}
              {place.google_maps_url && (
                <a
                  href={place.google_maps_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.btnDir}
                  onClick={(e) => e.stopPropagation()}
                >
                  Directions
                </a>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

const styles = {
  empty: {
    padding: '1rem',
    color: 'var(--text-secondary, #b3b3b3)',
    textAlign: 'center',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
    height: '100%',
    overflowY: 'auto',
  },
  item: {
    background: 'var(--surface-color, #1e1e1e)',
    borderRadius: '8px',
    padding: '1rem',
    cursor: 'pointer',
    border: '1px solid transparent',
    transition: 'border-color 0.2s',
  },
  itemActive: {
    border: '1px solid var(--accent-color, #007bff)',
  },
  name: {
    margin: '0 0 0.25rem 0',
    fontSize: '1rem',
    color: 'var(--text-primary, #fff)',
  },
  address: {
    margin: '0 0 0.5rem 0',
    fontSize: '0.85rem',
    color: 'var(--text-secondary, #b3b3b3)',
  },
  metaRow: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.8rem',
    marginBottom: '0.75rem',
  },
  distance: {
    color: 'var(--text-secondary, #b3b3b3)',
  },
  status: {
    fontWeight: 'bold',
  },
  actions: {
    display: 'flex',
    gap: '0.5rem',
  },
  btnCall: {
    flex: 1,
    padding: '0.5rem',
    textAlign: 'center',
    background: 'var(--success-color, #28a745)',
    color: '#fff',
    textDecoration: 'none',
    borderRadius: '4px',
    fontSize: '0.85rem',
    fontWeight: 'bold',
  },
  btnDir: {
    flex: 1,
    padding: '0.5rem',
    textAlign: 'center',
    background: 'var(--accent-color, #007bff)',
    color: '#fff',
    textDecoration: 'none',
    borderRadius: '4px',
    fontSize: '0.85rem',
    fontWeight: 'bold',
  }
};

export default PlacesSidebar;
