import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import Dashboard from './pages/Dashboard';
import MapPage from './pages/MapPage';
import Disasters from './pages/Disasters';
import Alerts from './pages/Alerts';
import News from './pages/News';
import Departments from './pages/Departments';
import EmergencyNumbersPage from './pages/EmergencyNumbersPage';
import NotFound from './pages/NotFound';
import { Toaster } from 'react-hot-toast';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Toaster position="top-right" />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
            
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="map" element={<MapPage />} />
              <Route path="disasters" element={<Disasters />} />
              <Route path="alerts" element={<Alerts />} />
              <Route path="news" element={<News />} />
              <Route path="departments" element={<Departments />} />
              <Route path="emergency" element={<EmergencyNumbersPage />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
