import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Cloud, 
  ChartLineUp, 
  Shield, 
  DeviceMobile, 
  Rocket, 
  UserPlus, 
  ArrowRight, 
  Envelope,
  ChatDots,
  CheckCircle
} from 'phosphor-react';
import '../styles/HomePage.css';

const HomePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');

  const handleTabClick = (tabName: string) => {
    setActiveTab(tabName);
  };

  return (
    <div className="home-container">
      {/* Navigation */}
      <nav className="home-nav">
        <Link to="/" className="nav-logo">
          <Cloud size={32} weight="fill" className="logo-icon" />
          <span className="logo-text">Cloud Pilot</span>
        </Link>
        <div className="nav-links">
          <a href="#features" className="nav-link">Features</a>
          <a href="#pricing" className="nav-link">Pricing</a>
          <a href="#docs" className="nav-link">Documentation</a>
          <Link to="/login" className="nav-link-button">Sign In</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <motion.div 
          className="hero-content"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="hero-title">
            Cloud Infrastructure in Plain English
          </h1>
          <p className="hero-subtitle">
            AI-powered chat to build and manage your AWS resources
          </p>
          <div className="hero-buttons">
            <Link to="/create-account" className="primary-button">
              Get Started
              <Rocket size={20} weight="bold" className="button-icon" />
            </Link>
            <a href="#demo" className="secondary-button">
              Watch Demo
            </a>
          </div>
        </motion.div>

        <motion.div
          className="hero-image"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {/* Dashboard Preview */}
          <div className="dashboard-preview">
            <div className="preview-header">
              <div className="preview-dots">
                <div className="dot red"></div>
                <div className="dot yellow"></div>
                <div className="dot green"></div>
              </div>
              <div className="preview-title">Cloud Pilot Dashboard</div>
            </div>
            <div className="preview-body">
              <div className="preview-sidebar">
                <div 
                  className={`sidebar-item ${activeTab === 'dashboard' ? 'active' : ''}`}
                  onClick={() => handleTabClick('dashboard')}
                >
                  <ChartLineUp size={20} className="sidebar-icon" />
                </div>
                <div 
                  className={`sidebar-item ${activeTab === 'cloud' ? 'active' : ''}`}
                  onClick={() => handleTabClick('cloud')}
                >
                  <Cloud size={20} className="sidebar-icon" />
                </div>
                <div 
                  className={`sidebar-item ${activeTab === 'security' ? 'active' : ''}`}
                  onClick={() => handleTabClick('security')}
                >
                  <Shield size={20} className="sidebar-icon" />
                </div>
                <div 
                  className={`sidebar-item ${activeTab === 'chat' ? 'active' : ''}`}
                  onClick={() => handleTabClick('chat')}
                >
                  <ChatDots size={20} className="sidebar-icon" />
                </div>
                <div 
                  className={`sidebar-item ${activeTab === 'mobile' ? 'active' : ''}`}
                  onClick={() => handleTabClick('mobile')}
                >
                  <DeviceMobile size={20} className="sidebar-icon" />
                </div>
              </div>
              <div className="preview-main">
                {/* Dashboard View - show when activeTab is dashboard */}
                {activeTab === 'dashboard' && (
                  <>
                    <div className="preview-stats">
                      <div className="stat-card">
                        <div className="stat-icon server">
                          <Cloud size={24} weight="fill" color="white" />
                        </div>
                        <div className="stat-info">
                          <div className="stat-value">24</div>
                          <div className="stat-label">Active Servers</div>
                        </div>
                      </div>
                      <div className="stat-card">
                        <div className="stat-icon performance">
                          <ChartLineUp size={24} weight="fill" color="white" />
                        </div>
                        <div className="stat-info">
                          <div className="stat-value">99.8%</div>
                          <div className="stat-label">Uptime</div>
                        </div>
                      </div>
                      <div className="stat-card">
                        <div className="stat-icon security">
                          <Shield size={24} weight="fill" color="white" />
                        </div>
                        <div className="stat-info">
                          <div className="stat-value">$1,245</div>
                          <div className="stat-label">Monthly Cost</div>
                        </div>
                      </div>
                    </div>

                    <div className="preview-chart">
                      {/* Simplified chart visualization */}
                    </div>

                    <div className="preview-table">
                      <div className="table-row header">
                        <div className="table-cell">Service</div>
                        <div className="table-cell">Status</div>
                        <div className="table-cell">Load</div>
                      </div>
                      <div className="table-row">
                        <div className="table-cell">Web Server</div>
                        <div className="table-cell">
                          <span className="status-badge green">Operational</span>
                        </div>
                        <div className="table-cell">42%</div>
                      </div>
                      <div className="table-row">
                        <div className="table-cell">Database</div>
                        <div className="table-cell">
                          <span className="status-badge green">Operational</span>
                        </div>
                        <div className="table-cell">28%</div>
                      </div>
                      <div className="table-row">
                        <div className="table-cell">Storage</div>
                        <div className="table-cell">
                          <span className="status-badge yellow">High Load</span>
                        </div>
                        <div className="table-cell">78%</div>
                      </div>
                    </div>
                  </>
                )}

                {/* Chat View - show when activeTab is chat */}
                {activeTab === 'chat' && (
                  <>
                    <div className="preview-chat-container">
                      <div className="preview-chat">
                        <div className="chat-messages">
                          <div className="chat-message system">
                           {/*  <div className="message-bubble">
                              Welcome to Cloud Pilot! I can help you manage your infrastructure. Try commands like:
                              <ul className="command-suggestions">
                                <li>"Create 2 EC2 t2.micro instances in us-east-1"</li>
                                <li>"Set up an RDS database with MySQL"</li>
                                <li>"Configure auto-scaling for my web servers"</li>
                              </ul>
                            </div> */}
                          </div>
                          <div className="chat-message outgoing">
                            <div className="message-bubble">Create 2 EC2 instances for a web application</div>
                            <div className="message-time">10:42 AM</div>
                          </div>
                          <div className="chat-message incoming">
                            <div className="message-bubble">
                              I'll help you set up 2 EC2 instances. Here's what I'm doing:
                              <div className="execution-steps">
                                <div className="step completed">✓ Creating VPC and security groups</div>
                                <div className="step completed">✓ Launching EC2 instance 1 (t2.micro)</div>
                                <div className="step active">⟳ Launching EC2 instance 2 (t2.micro)</div>
                                <div className="step pending">• Configuring load balancer</div>
                              </div>
                            </div>
                            <div className="message-time">10:43 AM</div>
                          </div>
                        </div>
                        <div className="chat-input">
                          <input type="text" placeholder="Describe what infrastructure you need..." disabled />
                          <button className="chat-send-button" disabled>Send</button>
                        </div>
                      </div>
                    </div>

                    {/* Floating Documentation - now outside chat container */}
                    <div className="floating-docs-overlay">
                      <div className="floating-docs">
                        <div className="docs-header">
                          <h3>Created Files</h3>
                          <button className="docs-close">×</button>
                        </div>
                        <div className="docs-content">
                          <div className="docs-section">
                            <div className="docs-item active">
                              <div className="docs-title">EC2 Instance Creation</div>
                              <div className="docs-details">
                                <div className="docs-step">
                                  <span className="step-number">1</span>
                                  <span>VPC & Security Groups</span>
                                </div>
                                <div className="docs-step">
                                  <span className="step-number">2</span>
                                  <span>Instance Launch (t2.micro)</span>
                                </div>
                                <div className="docs-step">
                                  <span className="step-number">3</span>
                                  <span>Load Balancer Setup</span>
                                </div>
                                <a href="#" className="docs-link">View Full Documentation →</a>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Placeholders for other tabs */}
                {activeTab === 'cloud' && (
                  <div className="preview-placeholder">
                    <div style={{textAlign: 'center', padding: '40px 20px', color: '#666'}}>
                      Cloud Resources View
                    </div>
                  </div>
                )}

                {activeTab === 'security' && (
                  <div className="preview-placeholder">
                    <div style={{textAlign: 'center', padding: '40px 20px', color: '#666'}}>
                      Security Dashboard
                    </div>
                  </div>
                )}

                {activeTab === 'mobile' && (
                  <div className="preview-placeholder">
                    <div style={{textAlign: 'center', padding: '40px 20px', color: '#666'}}>
                      Mobile Management
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Automation Section */}
      <section className="automation-section">
        <div className="automation-container">
          <div className="automation-content">
            <motion.div 
              className="automation-text"
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <h2>Tired of Wrestling with Terraform?</h2>
              <p className="automation-subtitle">Say goodbye to endless YAML files and HCL debugging</p>
              <div className="automation-points">
                <div className="point">
                  <span className="point-icon">✨</span>
                  <span>Just describe what you need in plain English</span>
                </div>
                <div className="point">
                  <span className="point-icon">🤖</span>
                  <span>We'll generate and manage the Terraform code</span>
                </div>
                <div className="point">
                  <span className="point-icon">🔄</span>
                  <span>Automatic state management and drift detection</span>
                </div>
                <div className="point">
                  <span className="point-icon">🛠️</span>
                  <span>Best practices and security built-in</span>
                </div>
              </div>
              <div className="automation-cta">
                <Link to="/create-account" className="try-now-button">
                  Try It Free
                  <ArrowRight size={16} weight="bold" />
                </Link>
              </div>
            </motion.div>
            <motion.div 
              className="automation-visual"
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <div className="code-comparison">
                <div className="code-before">
                  <div className="code-header">
                    <span className="code-label">Before: Complex Terraform</span>
                  </div>
                  <pre className="code-content">
                    <code>{`resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public.id
  
  tags = {
    Name = "web-server"
  }
}`}</code>
                  </pre>
                </div>
                <div className="code-after">
                  <div className="code-header">
                    <span className="code-label">After: Just Chat</span>
                  </div>
                  <div className="chat-message">
                    "Create a VPC with a public subnet and launch a web server"
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section">
        <div className="benefits-container">
          <div className="benefits-header">
            <h2>Why Choose Cloud Pilot?</h2>
            <p>Experience the future of cloud infrastructure management with our AI-powered platform</p>
          </div>
          <div className="benefits-grid">
            <motion.div 
              className="benefit-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <div className="benefit-icon">🚀</div>
              <h3>Instant Deployment</h3>
              <p>Deploy complex infrastructure in seconds using natural language commands</p>
            </motion.div>
            <motion.div 
              className="benefit-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <div className="benefit-icon">🤖</div>
              <h3>AI-Powered Automation</h3>
              <p>Let our AI handle the complexity while you focus on your business goals</p>
            </motion.div>
            <motion.div 
              className="benefit-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <div className="benefit-icon">💡</div>
              <h3>Smart Suggestions</h3>
              <p>Get intelligent recommendations for optimization and cost savings</p>
            </motion.div>
            <motion.div 
              className="benefit-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <div className="benefit-icon">🛡️</div>
              <h3>Built-in Security</h3>
              <p>Enterprise-grade security with automated compliance checks</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* DevOps Workflow Section */}
      <section className="devops-section">
        <div className="section-header">
          <h2 className="section-title">Modern DevOps Workflow</h2>
          <p className="section-subtitle">
            Streamline your entire development and operations lifecycle with Cloud Pilot
          </p>
        </div>

        <motion.div 
          className="devops-container"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="devops-content">
            <div className="devops-image">
              <img 
                src="https://cycle.io/global/resources/images/devops.svg" 
                alt="DevOps Infinity Loop"
                className="workflow-diagram"
              />
            </div>
            <div className="devops-steps">
              <div className="step-group left">
                <div className="workflow-step">
                  <h3>Plan & Code</h3>
                  <p>Collaborate on infrastructure planning and development with AI-assisted coding</p>
                </div>
                <div className="workflow-step">
                  <h3>Build & Test</h3>
                  <p>Automated building and testing of infrastructure configurations</p>
                </div>
              </div>
              <div className="step-group right">
                <div className="workflow-step">
                  <h3>Release & Deploy</h3>
                  <p>Seamless deployment with automated safety checks and rollback capabilities</p>
                </div>
                <div className="workflow-step">
                  <h3>Monitor & Operate</h3>
                  <p>Real-time monitoring and AI-powered operational insights</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="features-section" id="features">
        <div className="section-header">
          <h2 className="section-title">Powerful Features</h2>
          <p className="section-subtitle">
            Everything you need to manage your cloud infrastructure efficiently in one platform.
          </p>
        </div>

        <div className="features-grid">
          <motion.div 
            className="feature-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="feature-icon-wrapper blue">
              <ChartLineUp size={24} className="feature-icon" />
            </div>
            <h3 className="feature-title">Smart Monitoring</h3>
            <p className="feature-description">
              Real-time metrics and alerts to keep your services running smoothly. Monitor all your cloud resources from a single dashboard.
            </p>
          </motion.div>

          <motion.div 
            className="feature-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="feature-icon-wrapper green">
              <Cloud size={24} className="feature-icon" />
            </div>
            <h3 className="feature-title">Cost Optimization</h3>
            <p className="feature-description">
              Identify cost-saving opportunities and optimize your cloud spending with our intelligent recommendations.
            </p>
          </motion.div>

          <motion.div 
            className="feature-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="feature-icon-wrapper red">
              <Shield size={24} className="feature-icon" />
            </div>
            <h3 className="feature-title">Security & Compliance</h3>
            <p className="feature-description">
              Automated security scans and compliance checks to keep your cloud infrastructure secure and compliant.
            </p>
          </motion.div>

          <motion.div 
            className="feature-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <div className="feature-icon-wrapper purple">
              <DeviceMobile size={24} className="feature-icon" />
            </div>
            <h3 className="feature-title">Mobile Access</h3>
            <p className="feature-description">
              Manage your infrastructure on the go with our mobile app. Respond to alerts and make changes from anywhere.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section" id="pricing">
        <div className="section-header">
          <h2 className="section-title">Simple, Transparent Pricing</h2>
          <p className="section-subtitle">
            Choose the plan that best fits your needs. All plans include core features.
          </p>
        </div>

        <div className="pricing-grid">
          <motion.div 
            className="pricing-card starter"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="pricing-header">
              <h3>Starter</h3>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">29</span>
                <span className="period">/mo</span>
              </div>
              <p>Perfect for individuals and small teams</p>
            </div>
            <ul className="pricing-features">
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Up to 5 team members</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>100 AI chat interactions/mo</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Basic infrastructure templates</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Community support</span>
              </li>
            </ul>
            <Link to="/create-account" className="pricing-cta starter">
              Get Started
              <ArrowRight size={16} weight="bold" />
            </Link>
          </motion.div>

          <motion.div 
            className="pricing-card pro"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="pricing-badge">Most Popular</div>
            <div className="pricing-header">
              <h3>Professional</h3>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">99</span>
                <span className="period">/mo</span>
              </div>
              <p>For growing teams and businesses</p>
            </div>
            <ul className="pricing-features">
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Up to 20 team members</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Unlimited AI chat interactions</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Advanced infrastructure templates</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Priority email support</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Custom integrations</span>
              </li>
            </ul>
            <Link to="/create-account" className="pricing-cta pro">
              Get Started
              <ArrowRight size={16} weight="bold" />
            </Link>
          </motion.div>

          <motion.div 
            className="pricing-card enterprise"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="pricing-header">
              <h3>Enterprise</h3>
              <div className="price">
                <span className="custom-price">Custom</span>
              </div>
              <p>For large organizations with custom needs</p>
            </div>
            <ul className="pricing-features">
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Unlimited team members</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Unlimited AI chat interactions</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Custom infrastructure solutions</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>24/7 dedicated support</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>SLA guarantees</span>
              </li>
              <li>
                <CheckCircle size={20} weight="fill" className="feature-icon" />
                <span>Custom security requirements</span>
              </li>
            </ul>
            <Link to="/contact" className="pricing-cta enterprise">
              Contact Sales
              <ArrowRight size={16} weight="bold" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Documentation Section */}
      <section className="docs-section" id="docs">
        <div className="section-header">
          <h2 className="section-title">Comprehensive Documentation</h2>
          <p className="section-subtitle">
            Everything you need to get started and make the most of Cloud Pilot
          </p>
        </div>

        <div className="docs-grid">
          <motion.div 
            className="docs-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="docs-icon">📚</div>
            <h3>Getting Started</h3>
            <p>Quick start guides and tutorials to help you begin with Cloud Pilot</p>
            <Link to="/docs/getting-started" className="docs-link">
              Learn More
              <ArrowRight size={16} weight="bold" />
            </Link>
          </motion.div>

          <motion.div 
            className="docs-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="docs-icon">🔧</div>
            <h3>API Reference</h3>
            <p>Detailed API documentation for advanced integrations and customization</p>
            <Link to="/docs/api" className="docs-link">
              View APIs
              <ArrowRight size={16} weight="bold" />
            </Link>
          </motion.div>

          <motion.div 
            className="docs-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="docs-icon">📖</div>
            <h3>Best Practices</h3>
            <p>Learn about cloud infrastructure best practices and optimization tips</p>
            <Link to="/docs/best-practices" className="docs-link">
              Explore
              <ArrowRight size={16} weight="bold" />
            </Link>
          </motion.div>

          <motion.div 
            className="docs-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <div className="docs-icon">🎓</div>
            <h3>Tutorials</h3>
            <p>Step-by-step guides for common cloud infrastructure scenarios</p>
            <Link to="/docs/tutorials" className="docs-link">
              Start Learning
              <ArrowRight size={16} weight="bold" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to take control of your cloud?</h2>
          <p className="cta-subtitle">
            Join thousands of companies that use Cloud Pilot to manage their cloud infrastructure.
          </p>
          <div className="cta-buttons">
            <Link to="/create-account" className="primary-button">
              Create Free Account
              <UserPlus size={20} weight="bold" />
            </Link>
            <a href="#contact" className="text-link">
              Contact Sales <ArrowRight size={16} style={{ marginLeft: '0.5rem' }} />
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <div className="footer-top">
          <div>
            <div className="footer-logo">
              <Cloud size={32} weight="fill" className="logo-icon" />
              <span className="logo-text">Cloud Pilot</span>
            </div>
            <p style={{ maxWidth: '320px', color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: '1.6' }}>
              The all-in-one platform for monitoring, managing, and optimizing your cloud infrastructure.
            </p>
          </div>

          <div className="footer-links">
            <div className="footer-column">
              <h4 className="footer-title">Product</h4>
              <a href="#features" className="footer-link">Features</a>
              <a href="#pricing" className="footer-link">Pricing</a>
              <a href="#integrations" className="footer-link">Integrations</a>
              <a href="#changelog" className="footer-link">What's New</a>
            </div>

            <div className="footer-column">
              <h4 className="footer-title">Resources</h4>
              <a href="#docs" className="footer-link">Documentation</a>
              <a href="#guides" className="footer-link">Guides</a>
              <a href="#blog" className="footer-link">Blog</a>
              <a href="#support" className="footer-link">Support</a>
            </div>

            <div className="footer-column">
              <h4 className="footer-title">Company</h4>
              <a href="#about" className="footer-link">About Us</a>
              <a href="#careers" className="footer-link">Careers</a>
              <a href="#contact" className="footer-link">Contact</a>
            </div>

            <div className="footer-column">
              <h4 className="footer-title">Legal</h4>
              <a href="#terms" className="footer-link">Terms</a>
              <a href="#privacy" className="footer-link">Privacy</a>
              <a href="#cookies" className="footer-link">Cookies</a>
              <a href="#licenses" className="footer-link">Licenses</a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="copyright">
            © {new Date().getFullYear()} Cloud Pilot. All rights reserved.
          </div>
          <div className="social-links">
            <a href="#twitter" className="social-link">Twitter</a>
            <a href="#linkedin" className="social-link">LinkedIn</a>
            <a href="#github" className="social-link">GitHub</a>
            <a href="#youtube" className="social-link">YouTube</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage; 