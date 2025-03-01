import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { 
  ArrowRight,
  Envelope,
  WarningCircle,
  CheckCircle,
  Cloud
} from 'phosphor-react';
import '../styles/AuthPages.css';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const { forgotPassword } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Removed validation for testing purposes
    try {
      setError('');
      setIsLoading(true);
      // For testing, we'll just show success message without sending email
      // await forgotPassword(email);
      setTimeout(() => {
        setIsLoading(false);
        setIsSubmitted(true);
      }, 1000);
    } catch (error) {
      setError('Failed to send reset email. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      <motion.div 
        initial={{ opacity: 0, y: 0 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="auth-card"
      >
        <div className="auth-header">
          <Link to="/" className="auth-logo">
            <Cloud size={32} weight="fill" />
          </Link>
          <h1 className="auth-title">Reset Password</h1>
          <p className="auth-subtitle">Enter your email to receive a password reset link</p>
        </div>
        
        {isSubmitted ? (
          <div className="auth-success">
            <CheckCircle size={48} weight="fill" className="auth-success-icon" />
            <h2 className="auth-success-title">Check your email</h2>
            <p className="auth-success-text">
              We've sent a password reset link to <span className="auth-success-email">{email}</span>.
              The link will expire in 30 minutes.
            </p>
            <Link 
              to="/login" 
              className="auth-button"
            >
              Return to login
              <ArrowRight size={16} weight="bold" />
            </Link>
          </div>
        ) : (
          <div className="auth-body">
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="auth-error"
              >
                <WarningCircle size={20} weight="fill" className="auth-error-icon" />
                <p>{error}</p>
              </motion.div>
            )}
            
            <form onSubmit={handleSubmit}>
              <p className="text-slate-600 mb-6">
                Enter your email address and we'll send you a link to reset your password.
              </p>
              
              <div className="auth-form-group">
                <label htmlFor="email" className="auth-label">
                  Email
                </label>
                <div className="auth-input-wrapper">
                  <Envelope size={20} className="auth-input-icon" />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="auth-input"
                    placeholder="you@example.com"
                  />
                </div>
              </div>
              
              <button
                type="submit"
                className="auth-button"
              >
                {isLoading ? (
                  <div className="cloud-loading">
                    <div className="cloud-icon-wrapper">
                      <div className="cloud-shape"></div>
                      <div className="cloud-shape"></div>
                      <div className="cloud-shape"></div>
                    </div>
                    <span>Sending reset link...</span>
                  </div>
                ) : (
                  <>
                    <span>Send reset link</span>
                    <ArrowRight size={16} weight="bold" />
                  </>
                )}
              </button>
            </form>
          </div>
        )}
        
        <div className="auth-footer">
          <p>
            Remember your password?{' '}
            <Link to="/login" className="auth-link">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default ForgotPasswordPage; 