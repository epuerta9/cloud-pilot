import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Cloud, 
  ChartLineUp, 
  Database, 
  CurrencyDollar,
  Cpu,
  CloudArrowUp,
  Warning,
  CheckCircle
} from 'phosphor-react';
import '../styles/AwsDashboard.css';

interface AwsService {
  name: string;
  status: 'healthy' | 'warning' | 'error';
  cost: number;
  region: string;
  type: string;
}

interface CostData {
  total: number;
  services: {
    name: string;
    cost: number;
    percentage: number;
  }[];
}

const AwsDashboard: React.FC = () => {
  const [services, setServices] = useState<AwsService[]>([
    {
      name: "Web Server Cluster",
      status: "healthy",
      cost: 45.20,
      region: "us-east-1",
      type: "EC2"
    },
    {
      name: "Production Database",
      status: "healthy",
      cost: 82.15,
      region: "us-east-1",
      type: "RDS"
    },
    {
      name: "Storage Bucket",
      status: "warning",
      cost: 12.50,
      region: "us-west-2",
      type: "S3"
    }
  ]);

  const [costs, setCosts] = useState<CostData>({
    total: 139.85,
    services: [
      { name: "EC2", cost: 45.20, percentage: 32 },
      { name: "RDS", cost: 82.15, percentage: 59 },
      { name: "S3", cost: 12.50, percentage: 9 }
    ]
  });

  return (
    <div className="aws-dashboard">
      <div className="dashboard-header">
        <h1>AWS Dashboard</h1>
        <button className="refresh-button">
          <CloudArrowUp size={20} />
          Refresh
        </button>
      </div>

      <div className="dashboard-content">
        {/* Cost Overview */}
        <motion.div 
          className="cost-overview"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="cost-card total">
            <div className="cost-icon">
              <CurrencyDollar size={24} />
            </div>
            <div className="cost-details">
              <h3>Total Monthly Cost</h3>
              <p className="cost-amount">${costs.total.toFixed(2)}</p>
            </div>
          </div>
          
          <div className="cost-breakdown">
            {costs.services.map(service => (
              <div key={service.name} className="cost-bar">
                <div className="cost-bar-header">
                  <span>{service.name}</span>
                  <span>${service.cost.toFixed(2)}</span>
                </div>
                <div className="cost-bar-container">
                  <div 
                    className="cost-bar-fill" 
                    style={{ width: `${service.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Services Overview */}
        <motion.div 
          className="services-grid"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {services.map(service => (
            <div key={service.name} className="service-card">
              <div className="service-header">
                <div className={`status-indicator ${service.status}`}>
                  {service.status === 'healthy' && <CheckCircle size={16} />}
                  {service.status === 'warning' && <Warning size={16} />}
                </div>
                <h3>{service.name}</h3>
              </div>
              <div className="service-details">
                <div className="detail-item">
                  <Cpu size={16} />
                  <span>{service.type}</span>
                </div>
                <div className="detail-item">
                  <Cloud size={16} />
                  <span>{service.region}</span>
                </div>
                <div className="detail-item">
                  <CurrencyDollar size={16} />
                  <span>${service.cost.toFixed(2)}/month</span>
                </div>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default AwsDashboard; 