import React, { useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import './Auth.css';

export default function SignUp() {
  const emailRef = useRef();
  const passwordRef = useRef();
  const passwordConfirmRef = useRef();
  const { signup, loginWithGoogle } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    if (passwordRef.current.value !== passwordConfirmRef.current.value) {
      return setError('Passwords do not match');
    }

    try {
      setError('');
      setLoading(true);
      await signup(emailRef.current.value, passwordRef.current.value);
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
    if (err.code === 'auth/email-already-in-use') {
      setError('Email is already in use.');
    } else if (err.code === 'auth/weak-password') {
      setError('Password is too weak. Must be at least 6 characters.');
    } else if (err.code === 'auth/popup-closed-by-user') {
      setError('Google sign-in popup was closed.');
    } else if (err.code === 'auth/network-request-failed') {
      setError('Network error. Please check your connection.');
    } else {
      setError('Failed to create an account: ' + err.message);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Create Account</h2>
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
          <div className="form-group">
            <label htmlFor="password-confirm">Confirm Password</label>
            <input type="password" id="password-confirm" ref={passwordConfirmRef} required />
          </div>
          <button disabled={loading} className="btn-primary w-100" type="submit">
            Sign Up
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
          Sign up with Google
        </button>

        <div className="auth-links">
          Already have an account? <Link to="/login">Log In</Link>
        </div>
      </div>
      <div className="emergency-notice">
        <strong>CRITICAL:</strong> call 112 for immediate danger
      </div>
    </div>
  );
}
