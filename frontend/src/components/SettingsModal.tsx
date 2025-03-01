import { X } from 'phosphor-react';
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './SettingsModal.css';

interface SettingsModalProps {
  onClose: () => void;
}

interface SettingsData {
  awsAccessKey: string;
  awsSecretKey: string;
  apiKey: string;
  projectName: string;
  region: string;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
  const [settings, setSettings] = useState<SettingsData>({
    awsAccessKey: '',
    awsSecretKey: '',
    apiKey: '',
    projectName: '',
    region: 'us-east-1',
  });
  
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  // Load saved settings on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('cloudPilotSettings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings(parsedSettings);
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    // Simulate saving to backend
    setTimeout(() => {
      // Save to localStorage for demo purposes
      localStorage.setItem('cloudPilotSettings', JSON.stringify(settings));
      
      setIsSaving(false);
      setSaveMessage('Settings saved successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSaveMessage('');
      }, 3000);
    }, 1000);
  };

  // Handle click outside to close
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="settings-modal-overlay">
      <motion.div 
        className="settings-modal"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="settings-header">
          <h2 className="settings-title">Settings</h2>
          <button className="close-button" onClick={onClose}>
            <X size={20} weight="bold" />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="settings-section">
            <h3>AWS Configuration</h3>
            <div className="form-group">
              <label htmlFor="awsAccessKey">AWS Access Key ID</label>
              <input
                type="password"
                id="awsAccessKey"
                name="awsAccessKey"
                value={settings.awsAccessKey}
                onChange={handleChange}
                placeholder="Enter your AWS Access Key ID"
              />
            </div>

            <div className="form-group">
              <label htmlFor="awsSecretKey">AWS Secret Access Key</label>
              <input
                type="password"
                id="awsSecretKey"
                name="awsSecretKey"
                value={settings.awsSecretKey}
                onChange={handleChange}
                placeholder="Enter your AWS Secret Access Key"
              />
            </div>

            <div className="form-group">
              <label htmlFor="region">AWS Region</label>
              <select
                id="region"
                name="region"
                value={settings.region}
                onChange={handleChange}
              >
                <option value="us-east-1">US East (N. Virginia)</option>
                <option value="us-east-2">US East (Ohio)</option>
                <option value="us-west-1">US West (N. California)</option>
                <option value="us-west-2">US West (Oregon)</option>
                <option value="eu-west-1">EU (Ireland)</option>
                <option value="eu-central-1">EU (Frankfurt)</option>
                <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                <option value="ap-southeast-2">Asia Pacific (Sydney)</option>
              </select>
            </div>
          </div>

          <div className="settings-section">
            <h3>API Configuration</h3>
            <div className="form-group">
              <label htmlFor="apiKey">API Key</label>
              <input
                type="password"
                id="apiKey"
                name="apiKey"
                value={settings.apiKey}
                onChange={handleChange}
                placeholder="Enter your API Key"
              />
            </div>
          </div>

          <div className="settings-section">
            <h3>Project Details</h3>
            <div className="form-group">
              <label htmlFor="projectName">Project Name</label>
              <input
                type="text"
                id="projectName"
                name="projectName"
                value={settings.projectName}
                onChange={handleChange}
                placeholder="Enter your project name"
              />
            </div>
          </div>

          <div className="modal-footer">
            {saveMessage && <div className="save-message success">{saveMessage}</div>}
            <button 
              type="submit" 
              className="save-button"
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default SettingsModal; 