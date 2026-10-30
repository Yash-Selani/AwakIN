import React from 'react';

const TYPES = [
  { label: "Hospitals", value: "hospital" },
  { label: "Fire Stations", value: "fire_station" },
  { label: "Police", value: "police" },
  { label: "Pharmacies", value: "pharmacy" },
  { label: "Blood Banks", value: "blood_bank" }
];

const RADII = [
  { label: "1 km", value: 1000 },
  { label: "3 km", value: 3000 },
  { label: "5 km", value: 5000 },
  { label: "10 km", value: 10000 }
];

const FilterChips = ({ selectedType, onTypeChange, selectedRadius, onRadiusChange }) => {
  return (
    <div style={styles.container}>
      <div style={styles.section}>
        <span style={styles.label}>Type:</span>
        <div style={styles.chips}>
          {TYPES.map(t => (
            <button
              key={t.value}
              onClick={() => onTypeChange(t.value)}
              style={{
                ...styles.chip,
                ...(selectedType === t.value ? styles.chipActive : {})
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>
      <div style={styles.section}>
        <span style={styles.label}>Radius:</span>
        <div style={styles.chips}>
          {RADII.map(r => (
            <button
              key={r.value}
              onClick={() => onRadiusChange(r.value)}
              style={{
                ...styles.chip,
                ...(selectedRadius === r.value ? styles.chipActive : {})
              }}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
    padding: '0.5rem',
    background: 'var(--surface-color, #1e1e1e)',
    borderRadius: '8px',
    marginBottom: '1rem',
  },
  section: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    overflowX: 'auto',
  },
  label: {
    fontWeight: 'bold',
    fontSize: '0.85rem',
    color: 'var(--text-secondary, #b3b3b3)',
    minWidth: '50px',
  },
  chips: {
    display: 'flex',
    gap: '0.5rem',
  },
  chip: {
    padding: '0.4rem 0.8rem',
    borderRadius: '16px',
    border: '1px solid var(--border-color, #333)',
    background: 'transparent',
    color: 'var(--text-color, #fff)',
    cursor: 'pointer',
    fontSize: '0.85rem',
    whiteSpace: 'nowrap',
    transition: 'all 0.2s',
  },
  chipActive: {
    background: 'var(--accent-color, #007bff)',
    borderColor: 'var(--accent-color, #007bff)',
    color: '#fff',
  }
};

export default FilterChips;
