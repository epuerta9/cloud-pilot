import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { 
  ArrowRight,
  Key,
  User,
  Envelope,
  WarningCircle,
  CheckCircle,
  XCircle,
  Cloud
} from 'phosphor-react';
import '../styles/AuthPages.css';

const CreateAccountPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { register } = useAuth();
  const navigate = useNavigate();
  
  // Password criteria
  const passwordCriteria = [
    { id: 'length', label: 'At least 8 characters', test: (pass: string) => pass.length >= 8 },
    { id: 'uppercase', label: 'At least one uppercase letter', test: (pass: string) => /[A-Z]/.test(pass) },
    { id: 'lowercase', label: 'At least one lowercase letter', test: (pass: string) => /[a-z]/.test(pass) },
    { id: 'number', label: 'At least one number', test: (pass: string) => /[0-9]/.test(pass) },
    { id: 'special', label: 'At least one special character', test: (pass: string) => /[^A-Za-z0-9]/.test(pass) },
  ];
  
  // Calculate password strength
  useEffect(() => {
    if (!password) {
      setPasswordStrength(0);
      return;
    }
    
    let strength = 0;
    passwordCriteria.forEach(criterion => {
      if (criterion.test(password)) {
        strength += 1;
      }
    });
    
    setPasswordStrength(strength);
  }, [password]);
  
  // Get strength label
  const getStrengthLabel = () => {
    if (passwordStrength === 0) return '';
    if (passwordStrength < 3) return 'Weak';
    if (passwordStrength < 5) return 'Medium';
    return 'Strong';
  };
  
  // Get strength color class
  const getStrengthClass = () => {
    if (passwordStrength === 0) return '';
    if (passwordStrength < 3) return 'weak';
    if (passwordStrength < 5) return 'medium';
    return 'strong';
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setError('');
      setIsLoading(true);
      // For testing, we'll just navigate without actually registering
      // await register(name, email, password);
      setTimeout(() => {
        setIsLoading(false);
        navigate('/dashboard', { replace: true });
      }, 1000);
    } catch (error) {
      setError('Registration failed. Please try again.');
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
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">Sign up to get started with Cloud Pilot</p>
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
              <label htmlFor="name" className="auth-label">
                Full Name
              </label>
              <div className="auth-input-wrapper">
                <User size={20} className="auth-input-icon" />
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="auth-input"
                  placeholder="John Doe"
                />
              </div>
            </div>
            
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
              
              {password && (
                <div className="password-strength">
                  <div className="password-strength-header">
                    <span className="password-strength-label">Password Strength</span>
                    <span className={`password-strength-text ${getStrengthClass()}`}>
                      {getStrengthLabel()}
                    </span>
                  </div>
                  <div className="password-strength-bar">
                    <div 
                      className={`password-strength-progress ${getStrengthClass()}`}
                      style={{ width: `${(passwordStrength / 5) * 100}%` }}
                    ></div>
                  </div>
                  
                  <div className="password-criteria">
                    {passwordCriteria.map(criterion => (
                      <div 
                        key={criterion.id} 
                        className="criteria-item"
                      >
                        {criterion.test(password) ? (
                          <CheckCircle size={16} weight="fill" className="criteria-icon valid" />
                        ) : (
                          <XCircle size={16} weight="fill" className="criteria-icon invalid" />
                        )}
                        <span className="criteria-text">
                          {criterion.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="auth-form-group">
              <label htmlFor="confirm-password" className="auth-label">
                Confirm Password
              </label>
              <div className="auth-input-wrapper">
                <Key size={20} className="auth-input-icon" />
                <input
                  id="confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`auth-input ${confirmPassword && password !== confirmPassword ? 'is-invalid' : ''}`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="auth-input-action"
                >
                  {showConfirmPassword ? "Hide" : "Show"}
                </button>
              </div>
              {confirmPassword && password !== confirmPassword && (
                <div className="text-red-500 text-xs mt-1">Passwords don't match</div>
              )}
            </div>
            
            <div className="flex items-center mb-6">
              <input
                id="accept-terms"
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="accept-terms" className="ml-2 block text-sm text-gray-700 terms-label">
                I accept the <Link to="/terms" className="auth-link">Terms of Service</Link> and <Link to="/privacy" className="auth-link">Privacy Policy</Link>
              </label>
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
                  <span>Creating account...</span>
                </div>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight size={16} weight="bold" />
                </>
              )}
            </button>
          </form>
        </div>
        
        <div className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="auth-link">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default CreateAccountPage; 