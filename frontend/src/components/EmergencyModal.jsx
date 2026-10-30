import React from 'react';
import EmergencyNumbersView from './EmergencyNumbersView';

const EmergencyModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: 'var(--color-base-navy)',
        padding: '2rem',
        borderRadius: '12px',
        maxWidth: '450px',
        width: '100%',
        border: '2px solid var(--color-accent-red)',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <EmergencyNumbersView isModal={true} onClose={onClose} />
      </div>
    </div>
  );
};

export default EmergencyModal;
