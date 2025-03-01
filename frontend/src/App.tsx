import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Chat from './components/Chat';
import LoginPage from './components/LoginPage';
import CreateAccountPage from './components/CreateAccountPage';
import ForgotPasswordPage from './components/ForgotPasswordPage';
import HomePage from './components/HomePage';
import PrivateRoute from './components/PrivateRoute';
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <WebSocketProvider>
        <Router>
          <div className="App">
            <Routes>
              {/* Public landing page */}
              <Route path="/" element={<HomePage />} />
              
              {/* Auth routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/create-account" element={<CreateAccountPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/dashboard" element={<Chat />} />

              
              {/* Fallback route */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </Router>
      </WebSocketProvider>
    </AuthProvider>
  );
};

export default App;
