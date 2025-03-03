import React from 'react';
import { BuildingOfficeIcon, CurrencyDollarIcon, CpuChipIcon } from '@heroicons/react/24/outline';

interface ArchitectureModeProps {
  isActive: boolean;
  onSelect: (mode: string) => void;
  currentMode: string;
}

const ArchitectureMode: React.FC<ArchitectureModeProps> = ({ isActive, onSelect, currentMode }) => {
  if (!isActive) return null;

  const modes = [
    {
      id: 'normal',
      name: 'Normal',
      description: 'Standard chat mode for general assistance',
      icon: <CpuChipIcon className="w-5 h-5" />
    },
    {
      id: 'architect',
      name: 'Architect',
      description: 'Recommends optimal architecture designs and patterns',
      icon: <BuildingOfficeIcon className="w-5 h-5" />
    },
    {
      id: 'deploy',
      name: 'Deploy',
      description: 'Focuses on deployment options with cost estimates',
      icon: <CurrencyDollarIcon className="w-5 h-5" />
    }
  ];

  return (
    <div className="architecture-mode-container">
      <h3 className="mode-title">Select Mode</h3>
      <div className="mode-options">
        {modes.map((mode) => (
          <div 
            key={mode.id}
            className={`mode-option ${currentMode === mode.id ? 'active' : ''}`}
            onClick={() => onSelect(mode.id)}
          >
            <div className="mode-icon">{mode.icon}</div>
            <div className="mode-info">
              <h4 className="mode-name">{mode.name}</h4>
              <p className="mode-description">{mode.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ArchitectureMode; 