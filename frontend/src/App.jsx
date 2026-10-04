import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import { useAuth } from './context/AuthContext';
import './App.css';

function Dashboard() {
  const { currentUser, logout } = useAuth();
  
  return (
    <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h1>Welcome to AwakIN</h1>
      <p>Logged in as: <strong>{currentUser.email}</strong></p>
      <button 
        onClick={logout} 
        style={{ 
          padding: '0.75rem 1.5rem', 
          marginTop: '1rem', 
          cursor: 'pointer',
          backgroundColor: '#e53e3e',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          fontWeight: 'bold'
        }}
      >
        Sign Out
      </button>
      
      <div style={{ 
        marginTop: '3rem', 
        backgroundColor: '#fff5f5', 
        color: '#c53030', 
        padding: '1rem 2rem', 
        borderRadius: '8px', 
        border: '1px solid #feb2b2',
        fontWeight: 'bold',
        fontSize: '1.2rem'
      }}>
        CRITICAL: call 112 for immediate danger
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
