import React, { useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import './Auth.css';

export default function Login() {
  const emailRef = useRef();
  const passwordRef = useRef();
  const { login, loginWithGoogle } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      setError('');
      setLoading(true);
      await login(emailRef.current.value, passwordRef.current.value);
      navigate('/');
    } catch (err) {
      handleFirebaseError(err);
    }
    setLoading(false);
  }

  async function handleGoogleSignIn() {
    try {
      setError('');
      setLoading(true);
      await loginWithGoogle();
      navigate('/');
    } catch (err) {
      handleFirebaseError(err);
    }
    setLoading(false);
  }

  function handleFirebaseError(err) {
    if (err.code === 'auth/wrong-password') {
      setError('Incorrect password.');
    } else if (err.code === 'auth/user-not-found') {
      setError('No user found with this email.');
    } else if (err.code === 'auth/popup-closed-by-user') {
      setError('Google sign-in popup was closed.');
    } else if (err.code === 'auth/network-request-failed') {
      setError('Network error. Please check your connection.');
    } else {
      setError('Failed to log in: ' + err.message);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Welcome Back</h2>
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input type="email" id="email" ref={emailRef} required />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input type="password" id="password" ref={passwordRef} required />
          </div>
          <button disabled={loading} className="btn-primary w-100" type="submit">
            Log In
          </button>
        </form>
        
        <div className="auth-divider">
          <span>OR</span>
        </div>

        <button 
          disabled={loading} 
          className="btn-google w-100" 
          onClick={handleGoogleSignIn}
        >
          Sign in with Google
        </button>

        <div className="auth-links">
          Need an account? <Link to="/signup">Sign Up</Link>
        </div>
      </div>
      <div className="emergency-notice">
        <strong>CRITICAL:</strong> call 112 for immediate danger
      </div>
    </div>
  );
}
