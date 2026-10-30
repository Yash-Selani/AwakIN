import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import EmergencyModal from './EmergencyModal';

const Navbar = () => {
  const { currentUser, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isEmergencyModalOpen, setIsEmergencyModalOpen] = useState(false);

  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

  const navLinks = [
    { name: 'Dashboard', path: '/' },
    { name: 'Map', path: '/map' },
    { name: 'Disasters', path: '/disasters' },
    { name: 'Alerts', path: '/alerts' },
    { name: 'News', path: '/news' },
    { name: 'Departments', path: '/departments' },
  ];

  return (
    <>
      <nav style={{
        position: 'sticky',
        top: 0,
        backgroundColor: 'var(--color-base-navy)',
        borderBottom: '1px solid var(--color-base-navy-light)',
        padding: '1rem',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Logo and Mobile Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button 
            className="mobile-toggle"
            onClick={toggleMobileMenu}
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              fontSize: '1.5rem',
              cursor: 'pointer',
              display: 'none' // Handled by media query in App.css or index.css, will inline for now
            }}
          >
            ☰
          </button>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            letterSpacing: '1px'
          }}>
            <span style={{ color: 'white' }}>Awak</span>
            <span style={{ color: 'var(--color-accent-red)' }}>IN</span>
          </div>
        </div>

        {/* Desktop Navigation */}
        <div className="desktop-nav" style={{
          display: 'flex',
          gap: '1.5rem',
          alignItems: 'center'
        }}>
          {navLinks.map((link) => (
            <NavLink
              key={link.name}
              to={link.path}
              style={({ isActive }) => ({
                color: isActive ? 'white' : 'var(--color-text-secondary)',
                textDecoration: 'none',
                fontWeight: isActive ? 'bold' : 'normal',
                transition: 'color 0.2s'
              })}
            >
              {link.name}
            </NavLink>
          ))}
        </div>

        {/* Right Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => setIsEmergencyModalOpen(true)}
            style={{
              backgroundColor: 'var(--color-accent-red)',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontWeight: 'bold',
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            Emergency Numbers
          </button>
          
          {currentUser && (
            <div className="user-dropdown" style={{ position: 'relative' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <div style={{
                  width: '32px', height: '32px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-base-navy-light)',
                  display: 'flex', justifyContent: 'center', alignItems: 'center',
                  fontWeight: 'bold', border: '1px solid var(--color-text-secondary)'
                }}>
                  {currentUser.email?.[0].toUpperCase()}
                </div>
              </div>
              
              {/* Dropdown would go here, simplified for now: */}
              <button 
                onClick={logout}
                style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: '0.5rem',
                  backgroundColor: 'var(--color-base-navy-light)',
                  color: 'white',
                  border: '1px solid var(--color-text-secondary)',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Mobile Menu Drawer */}
      {isMobileMenuOpen && (
        <div style={{
          position: 'fixed',
          top: '73px', // approx navbar height
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'var(--color-base-navy)',
          zIndex: 99,
          padding: '1rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          {navLinks.map((link) => (
            <NavLink
              key={link.name}
              to={link.path}
              onClick={() => setIsMobileMenuOpen(false)}
              style={({ isActive }) => ({
                color: isActive ? 'white' : 'var(--color-text-secondary)',
                textDecoration: 'none',
                fontWeight: isActive ? 'bold' : 'normal',
                fontSize: '1.25rem',
                padding: '0.5rem 0'
              })}
            >
              {link.name}
            </NavLink>
          ))}
        </div>
      )}

      {/* Emergency Modal */}
      <EmergencyModal 
        isOpen={isEmergencyModalOpen} 
        onClose={() => setIsEmergencyModalOpen(false)} 
      />

      {/* Add inline styles for responsive display of mobile toggle and desktop nav */}
      <style>{`
        @media (max-width: 768px) {
          .desktop-nav { display: none !important; }
          .mobile-toggle { display: block !important; }
        }
      `}</style>
    </>
  );
};

export default Navbar;
