import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { 
  ArrowRight, 
  Key,
  Envelope,
  WarningCircle,
  Cloud
} from 'phosphor-react';
import '../styles/AuthPages.css';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get the redirect path from location state or default to "/"
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Removed validation for testing purposes
    try {
      setError('');
      setIsLoading(true);
      // For testing, we'll just navigate without actually logging in
      // await login(email, password, rememberMe);
      setTimeout(() => {
        setIsLoading(false);
        navigate(from, { replace: true });
      }, 1000);
    } catch (error) {
      setError('Invalid email or password');
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
          <h1 className="auth-title">Cloud Pilot</h1>
          <p className="auth-subtitle">Sign in to your account</p>
        </div>
        
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
            
            <div className="auth-form-group">
              <label htmlFor="password" className="auth-label">
                Password
              </label>
              <div className="auth-input-wrapper">
                <Key size={20} className="auth-input-icon" />
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="auth-input"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="auth-input-action"
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center justify-between mb-6 gap-2">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-700">
                  Remember me
                </label>
              </div>
              <Link to="/forgot-password" className="auth-link text-sm">
                Forgot password?
              </Link>
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
                  <span>Signing in...</span>
                </div>
              ) : (
                <>
                  <span>Sign in</span>
                  <ArrowRight size={16} weight="bold" />
                </>
              )}
            </button>
          </form>
        </div>
        
        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <Link to="/create-account" className="auth-link">
              Create one now
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage; 