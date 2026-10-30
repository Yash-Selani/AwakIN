import React from 'react';
import EmergencyNumbersView from '../components/EmergencyNumbersView';

const EmergencyNumbersPage = () => {
  return (
    <div style={{
      padding: '2rem',
      maxWidth: '800px',
      margin: '0 auto',
      minHeight: 'calc(100vh - 73px)'
    }}>
      <EmergencyNumbersView isModal={false} />
    </div>
  );
};

export default EmergencyNumbersPage;
