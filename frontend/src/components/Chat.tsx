import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import { SparklesIcon, ArrowPathIcon, LightBulbIcon, CodeBracketIcon, ChatBubbleLeftRightIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import ChatMessage from './ChatMessage';
import ThinkingIndicator from './ThinkingIndicator';
import VoiceInput from './VoiceInput';
import DocumentView from './DocumentView';
import AwsDashboard from './AwsDashboard';
import { Message, StructuredContent, ContentSection } from '../types';
import { ApiService } from '../services/api';
import SettingsModal from './SettingsModal';
import { FileText, Cloud, ChartLineUp, CurrencyDollar, Cpu, Shield, Database, Rocket, ArrowsClockwise, Eraser } from 'phosphor-react';
import { useWebSocket } from '../contexts/WebSocketContext';
import ArchitectureMode from './ArchitectureMode';
import websocketService from '../services/websocket';
import '../styles/Header.css';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [currentDocument, setCurrentDocument] = useState<StructuredContent | undefined>(undefined);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [showArchitectureMode, setShowArchitectureMode] = useState(false);
  const [currentMode, setCurrentMode] = useState('normal');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const inputContainerRef = useRef<HTMLDivElement>(null);
  const [connectionStatus, setConnectionStatus] = useState<string>('UNKNOWN');

  const { isConnected, sendTask, lastResult, confirmationData, sendConfirmation, terraformApplyData } = useWebSocket();

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking, streamingContent]);

  // Handle WebSocket results
  useEffect(() => {
    if (lastResult) {
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: lastResult.message || lastResult.toString(),
        timestamp: new Date(),
        structuredContent: lastResult.structuredContent,
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsThinking(false);
      setIsStreaming(false);
      setStreamingContent('');

      // If there's structured content, update the document view
      if (lastResult.structuredContent) {
        setCurrentDocument(lastResult.structuredContent);
        setActiveTab('document');
      }
    }
  }, [lastResult]);

  // Handle confirmation requests
  useEffect(() => {
    if (confirmationData) {
      const confirmationMessage: Message = {
        id: Date.now().toString(),
        role: 'system',
        content: confirmationData.question || 'Do you want to proceed with this action?',
        timestamp: new Date(),
        requiresConfirmation: true,
        confirmationData: confirmationData,
      };
      setMessages(prev => [...prev, confirmationMessage]);

      // Create structured content for the document view when we have confirmation data
      if (confirmationData.terraform_json) {
        const planJson = confirmationData.terraform_json;
        const sections: ContentSection[] = [];

        // Add title section
        sections.push({
          type: 'heading',
          content: 'Terraform Plan Details',
          metadata: { level: 1 }
        });

        // Add status section
        sections.push({
          type: 'text',
          content: `Status: ${planJson.errored ? 'Error' : planJson.complete ? 'Complete' : 'Pending'}`
        });

        // Add version info
        if (planJson.terraform_version) {
          sections.push({
            type: 'text',
            content: `Terraform Version: ${planJson.terraform_version}`
          });
        }

        // Add timestamp
        if (planJson.timestamp) {
          sections.push({
            type: 'text',
            content: `Timestamp: ${planJson.timestamp}`
          });
        }

        // Add the full JSON as a code block
        sections.push({
          type: 'code',
          content: JSON.stringify(planJson, null, 2),
          metadata: { language: 'json' }
        });

        // Add plan output if available
        if (confirmationData.plan_output) {
          sections.push({
            type: 'heading',
            content: 'Plan Output',
            metadata: { level: 2 }
          });

          sections.push({
            type: 'code',
            content: confirmationData.plan_output,
            metadata: { language: 'shell' }
          });
        }

        const terraformPlanContent: StructuredContent = {
          title: 'Terraform Plan',
          sections
        };

        setCurrentDocument(terraformPlanContent);
        setActiveTab('document');
      }
    }
  }, [confirmationData]);

  // Auto-resize textarea based on content
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      // Reset height to get accurate scrollHeight
      textarea.style.height = '0px';

      // Calculate new height with max limit
      const maxHeight = 140;
      const height = Math.min(textarea.scrollHeight, maxHeight);

      // Set textarea height
      textarea.style.height = height + 'px';

      // Update wrapper height
      const wrapper = textarea.closest('.input-wrapper') as HTMLElement;
      if (wrapper) {
        const minHeight = 44;
        const padding = 16;
        const wrapperHeight = Math.min(Math.max(height + padding, minHeight), maxHeight);
        wrapper.style.height = wrapperHeight + 'px';
      }
    }
  }, [input]);

  // Focus input when component mounts
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!input.trim() && !isRecording) return;
    if (!isConnected) {
      alert('Not connected to server. Please try again in a moment.');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsThinking(true);
    setShowSuggestions(false);

    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = '24px';
      const wrapper = textarea.closest('.input-wrapper') as HTMLElement;
      if (wrapper) {
        wrapper.style.height = '44px';
      }
    }

    // Send message through WebSocket with the current mode
    sendTask({
      message: userMessage.content,
      timestamp: userMessage.timestamp,
      mode: currentMode
    });
  };

  // Handle confirmation response
  const handleConfirmation = (message: Message, confirmed: boolean) => {
    if (message.confirmationData) {
      sendConfirmation(confirmed, message.confirmationData);

      // Add response to messages
      const responseMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: confirmed ? 'Confirmed' : 'Cancelled',
        timestamp: new Date(),
        isConfirmationResponse: true,
      };
      setMessages(prev => [...prev, responseMessage]);

      // If user cancels, switch back to chat view
      if (!confirmed) {
        setActiveTab('chat');
      }
    }
  };

  // Toggle voice recording
  const toggleRecording = () => {
    setIsRecording(!isRecording);

    // If we're stopping recording, we'll let the VoiceInput component handle the transcript
    if (isRecording) {
      textareaRef.current?.focus();
    }
  };

  // Handle voice transcript from VoiceInput
  const handleVoiceTranscript = (transcript: string) => {
    if (transcript.trim()) {
      setInput(prev => {
        // If there's already text in the input, add a space before the transcript
        const separator = prev.trim() ? ' ' : '';
        return prev + separator + transcript;
      });
    }
  };

  // Handle suggestion click
  const handleSuggestion = (suggestion: string) => {
    setInput(suggestion);
    textareaRef.current?.focus();
  };

  // Clear chat history
  const clearChat = () => {
    setMessages([]);
    setShowSuggestions(true);
    setCurrentDocument(undefined);
    setIsStreaming(false);
    setStreamingContent('');
  };

  // Toggle settings modal
  const toggleSettingsModal = () => {
    setShowSettingsModal(!showSettingsModal);
  };

  // Toggle architecture mode selector
  const toggleArchitectureMode = () => {
    setShowArchitectureMode(!showArchitectureMode);
  };

  // Handle mode selection
  const handleModeSelect = (mode: string) => {
    setCurrentMode(mode);
    setShowArchitectureMode(false);
  };

  // Get suggestions based on active tab
  const getSuggestions = () => {
    // Different suggestions based on the current mode
    if (currentMode === 'architect') {
      return [
        {
          icon: <Cpu size={24} className="suggestion-icon" />,
          title: "Social Media Platform",
          description: "Architecture for a social media application",
          prompt: "I'm looking to build a social media platform similar to Instagram. What architecture would you recommend and what would be the estimated costs?"
        },
        {
          icon: <ChartLineUp size={24} className="suggestion-icon" />,
          title: "E-commerce Website",
          description: "Architecture for an online store",
          prompt: "I need to build an e-commerce website that can handle 50,000 monthly visitors. What architecture would you recommend?"
        },
        {
          icon: <CurrencyDollar size={24} className="suggestion-icon" />,
          title: "Content Streaming Service",
          description: "Architecture for video/audio streaming",
          prompt: "I want to create a video streaming service like YouTube. What would be the best architecture and estimated costs per 1000 users?"
        },
        {
          icon: <Rocket size={24} className="suggestion-icon" />,
          title: "Mobile App Backend",
          description: "Architecture for mobile application backend",
          prompt: "I'm developing a mobile app with user profiles, real-time chat, and data synchronization. What cloud architecture would you recommend?"
        }
      ];
    } else if (currentMode === 'deploy' || currentMode === 'normal') {
      // Use the same suggestions for both deploy and normal modes
      return [
        {
          icon: <Cpu size={24} className="suggestion-icon" />,
          title: "EC2 Web Server",
          description: "Deploy a web server on EC2",
          prompt: "I need to deploy a Node.js web application on an EC2 instance. Can you help me set it up?"
        },
        {
          icon: <ChartLineUp size={24} className="suggestion-icon" />,
          title: "Serverless API",
          description: "Deploy a serverless API with Lambda",
          prompt: "I want to create a serverless REST API using AWS Lambda and API Gateway. How should I set it up?"
        },
        {
          icon: <CurrencyDollar size={24} className="suggestion-icon" />,
          title: "Container Deployment",
          description: "Deploy containers with ECS or EKS",
          prompt: "I have a containerized application. Should I use ECS or EKS to deploy it, and how do I set it up?"
        },
        {
          icon: <Rocket size={24} className="suggestion-icon" />,
          title: "Static Website",
          description: "Deploy a static website with S3 and CloudFront",
          prompt: "I need to deploy a React static website with S3 and CloudFront. Can you help me set it up?"
        }
      ];
    } else {
      // This case should never be reached, but keeping it as a fallback
      return [
        {
          icon: <Cpu size={24} className="suggestion-icon" />,
          title: "Generate Documentation",
          description: "Create comprehensive documentation for your project",
          prompt: "Generate documentation for my React application with TypeScript"
        },
        {
          icon: <ChartLineUp size={24} className="suggestion-icon" />,
          title: "Optimize Performance",
          description: "Get tips to improve your application's performance",
          prompt: "How can I optimize the performance of my web application?"
        },
        {
          icon: <CurrencyDollar size={24} className="suggestion-icon" />,
          title: "Cost Estimation",
          description: "Estimate cloud infrastructure costs",
          prompt: "Estimate the cost of hosting a web application with 10,000 monthly users"
        },
        {
          icon: <Rocket size={24} className="suggestion-icon" />,
          title: "Architecture Design",
          description: "Design scalable architecture for your application",
          prompt: "Design a scalable architecture for a web application with user authentication"
        }
      ];
    }
  };

  // Handle key press (Enter to send, Shift+Enter for new line)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Add a useEffect to handle terraformApplyData
  useEffect(() => {
    if (terraformApplyData) {
      // Switch to document tab when terraform apply data is received
      setActiveTab('document');
    }
  }, [terraformApplyData]);

  // Update connection status periodically
  useEffect(() => {
    const updateConnectionStatus = () => {
      setConnectionStatus(websocketService.getConnectionStatus());
    };
    
    // Update immediately
    updateConnectionStatus();
    
    // Then update every 2 seconds
    const interval = setInterval(updateConnectionStatus, 2000);
    
    return () => clearInterval(interval);
  }, []);

  // Handle reconnect button click
  const handleReconnect = () => {
    websocketService.forceReconnect();
  };

  // Render the main chat interface
  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="chat-header">
          <Link to="/" className="nav-logo">
            <Cloud size={24} weight="fill" className="logo-icon" />
            <span className="logo-text">CloudPilot</span>
          </Link>
          <h1 className="chat-title">
            {activeTab === 'chat' ? 'New Chat' : activeTab === 'aws' ? 'AWS Setup' : 'Document View'}
          </h1>
          <div className="header-buttons">
            <div className="connection-status">
              <span className={`status-indicator ${connectionStatus === 'OPEN' ? 'connected' : 'disconnected'}`}></span>
              <span className="status-text">{connectionStatus}</span>
              {connectionStatus !== 'OPEN' && (
                <button className="reconnect-button" onClick={handleReconnect}>
                  <ArrowsClockwise size={16} />
                </button>
              )}
            </div>
            {messages.length > 0 && (
              <button
                className="clear-chat-button"
                onClick={clearChat}
                aria-label="Clear chat"
              >
                <ArrowPathIcon className="w-5 h-5" />
              </button>
            )}
            <button
              className="mode-toggle-button"
              onClick={toggleArchitectureMode}
              aria-label="Toggle architecture mode"
            >
              <Rocket size={20} />
            </button>
          </div>
        </div>

        {/* Architecture Mode Selector */}
        <ArchitectureMode 
          isActive={showArchitectureMode} 
          onSelect={handleModeSelect} 
          currentMode={currentMode} 
        />

        <div className="main-content">
          <div className="chat-messages">
            <AnimatePresence>
              {messages.length === 0 && showSuggestions ? (
                <motion.div
                  className="welcome-container"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="welcome-header">
                    <h2 className="welcome-title">
                      {activeTab === 'chat' ? 'Welcome to Cloud Pilot' : 'AWS Setup Assistant'}
                    </h2>
                  </div>
                  <p className="welcome-text">
                    {activeTab === 'chat'
                      ? 'Your next-generation AI assistant. Ask me anything about coding, technology, or just chat!'
                      : 'I can help you set up and manage your AWS infrastructure. Ask me about services, costs, or configurations!'}
                  </p>

                  <div className="suggestion-grid">
                    {getSuggestions().map((suggestion, index) => (
                      <button 
                        key={index} 
                        className="suggestion-button" 
                        onClick={() => handleSuggestion(suggestion.prompt)}
                      >
                        {suggestion.icon}
                        <div className="suggestion-content">
                          <h3 className="suggestion-title">{suggestion.title}</h3>
                          <p className="suggestion-description">{suggestion.description}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </motion.div>
              ) : (
                <>
                  {messages.map((message, index) => (
                    <ChatMessage
                      key={message.id}
                      message={message}
                      isLast={index === messages.length - 1}
                      updateReply={(idx: number, content: string) => {
                        const updatedMessages = [...messages];
                        if (updatedMessages[idx]) {
                          updatedMessages[idx].content = content;
                          setMessages(updatedMessages);
                        }
                      }}
                      index={index}
                      isStreaming={isStreaming && index === messages.length - 1}
                      streamingContent={streamingContent}
                      onConfirm={message.requiresConfirmation ?
                        () => handleConfirmation(message, true) : undefined}
                      onCancel={message.requiresConfirmation ?
                        () => handleConfirmation(message, false) : undefined}
                    />
                  ))}
                  {/* Only show thinking indicator if there's no pending confirmation */}
                  {isThinking && !messages.some(m => m.confirmationData) && <ThinkingIndicator />}
                  {isStreaming && streamingContent && (
                    <ChatMessage
                      message={{
                        id: 'streaming',
                        role: 'assistant',
                        content: streamingContent,
                        timestamp: new Date(),
                      }}
                      isLast={true}
                      isStreaming={true}
                      streamingContent={streamingContent}
                    />
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Only show chat input if there's no pending confirmation */}
        {!messages.some(m => m.requiresConfirmation && !m.isConfirmationResponse) && (
          <div className="chat-input-container">
            <div className="input-wrapper">
              <textarea
                ref={textareaRef}
                className="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  currentMode === 'deploy' || currentMode === 'normal' 
                    ? "Ask about deploying web servers, serverless APIs, containers, or static websites..."
                    : currentMode === 'architect'
                    ? "Ask about architecture designs, cost estimates, or infrastructure recommendations..."
                    : `Message Cloud Pilot (${currentMode} mode)...`
                }
                disabled={isThinking || isStreaming}
                rows={1}
                style={{ height: 'auto' }}
              />

              <div className="input-buttons">
                <VoiceInput
                  isRecording={isRecording}
                  toggleRecording={toggleRecording}
                  onTranscript={handleVoiceTranscript}
                  disabled={isThinking || isStreaming}
                />

                <button
                  className="send-button"
                  onClick={handleSendMessage}
                  disabled={(!input.trim() && !isRecording) || isThinking || isStreaming}
                  aria-label="Send message"
                >
                  <PaperAirplaneIcon className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="document-container">
        <div className="document-header">
          <div className="document-header-content">
            {activeTab === 'chat' ? (
              <>
                <FileText size={20} className="document-icon" />
                <span className="document-header-title">Document View</span>
              </>
            ) : activeTab === 'aws' ? (
              <>
                <ChartLineUp size={20} className="document-icon" />
                <span className="document-header-title">AWS Dashboard</span>
              </>
            ) : (
              <>
                <FileText size={20} className="document-icon" />
                <span className="document-header-title">{currentDocument?.title || "Document View"}</span>
              </>
            )}
          </div>
          <div className="header-actions">
            <button
              className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5" />
              <span>Chat</span>
            </button>
            <button
              className={`tab-button ${activeTab === 'document' ? 'active' : ''}`}
              onClick={() => setActiveTab('document')}
              disabled={!currentDocument}
            >
              <FileText size={20} />
              <span>Document</span>
            </button>
            <button
              className={`tab-button ${activeTab === 'aws' ? 'active' : ''}`}
              onClick={() => setActiveTab('aws')}
            >
              <ChartLineUp size={20} />
              <span>AWS Dashboard</span>
            </button>
            <button
              className="settings-button"
              onClick={toggleSettingsModal}
              aria-label="Settings"
            >
              <Cog6ToothIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
        <div className="document-content">
          {activeTab === 'document' ? (
            <DocumentView content={currentDocument} isStreaming={isStreaming} terraformApplyData={terraformApplyData} />
          ) : activeTab === 'aws' ? (
            <AwsDashboard />
          ) : (
            <DocumentView content={undefined} isStreaming={isStreaming} />
          )}
        </div>
      </div>

      {showSettingsModal && (
        <SettingsModal onClose={toggleSettingsModal} />
      )}
    </div>
  );
};

export default Chat;