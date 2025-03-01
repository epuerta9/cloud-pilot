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
import { FileText, Cloud, ChartLineUp, CurrencyDollar, Cpu, Shield, Database, Rocket } from 'phosphor-react';
import { useWebSocket } from '../contexts/WebSocketContext';

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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const inputContainerRef = useRef<HTMLDivElement>(null);

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

    // Send message through WebSocket
    sendTask({
      message: userMessage.content,
      timestamp: userMessage.timestamp,
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

  // Get suggestions based on active tab
  const getSuggestions = () => {
    if (activeTab === 'chat') {
      return (
        <>
          <button className="suggestion-button" onClick={() => handleSuggestion("Create an EC2 instance for hosting a Node.js web app")}>
            <Cpu size={24} className="suggestion-icon" />
            Launch Web App Server
          </button>

          <button className="suggestion-button" onClick={() => handleSuggestion("Set up an RDS database with proper security groups")}>
            <Database size={24} className="suggestion-icon" />
            Configure Database
          </button>

          <button className="suggestion-button" onClick={() => handleSuggestion("Create a production-ready VPC with public and private subnets")}>
            <Cloud size={24} className="suggestion-icon" />
            Setup VPC Architecture
          </button>

          <button className="suggestion-button" onClick={() => handleSuggestion("Configure auto-scaling for my EC2 instances with CloudWatch alarms")}>
            <ChartLineUp size={24} className="suggestion-icon" />
            Setup Auto-scaling
          </button>
        </>
      );
    } else {
      return (
        <>
          <button className="suggestion-button" onClick={() => handleSuggestion("How can I reduce my EC2 and RDS costs?")}>
            <CurrencyDollar size={24} className="suggestion-icon" />
            Optimize AWS Costs
          </button>

          <button className="suggestion-button" onClick={() => handleSuggestion("Help me secure my AWS resources with best practices")}>
            <Shield size={24} className="suggestion-icon" />
            Security Best Practices
          </button>

          <button className="suggestion-button" onClick={() => handleSuggestion("Set up CloudWatch monitoring and alerts for my services")}>
            <ChartLineUp size={24} className="suggestion-icon" />
            Configure Monitoring
          </button>

          <button className="suggestion-button" onClick={() => handleSuggestion("Create a CI/CD pipeline with AWS CodePipeline")}>
            <Rocket size={24} className="suggestion-icon" />
            Setup CI/CD Pipeline
          </button>
        </>
      );
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

  // Render the main chat interface
  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="chat-header">
          <Link to="/" className="nav-logo">
            <Cloud size={24} weight="fill" className="logo-icon" />
            <span className="logo-text">Cloud Pilot</span>
          </Link>
          <h1 className="chat-title">
            {activeTab === 'chat' ? 'New Chat' : activeTab === 'aws' ? 'AWS Setup' : 'Document View'}
          </h1>
          {messages.length > 0 && (
            <button
              className="clear-chat-button"
              onClick={clearChat}
              aria-label="Clear chat"
            >
              <ArrowPathIcon className="w-5 h-5" />
            </button>
          )}
        </div>

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
                    {getSuggestions()}
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
                  {isThinking && <ThinkingIndicator />}
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
                placeholder="Message Cloud Pilot..."
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
              Chat
            </button>
            <button
              className={`tab-button ${activeTab === 'document' ? 'active' : ''}`}
              onClick={() => setActiveTab('document')}
              disabled={!currentDocument}
            >
              <FileText size={20} />
              Document
            </button>
            <button
              className={`tab-button ${activeTab === 'aws' ? 'active' : ''}`}
              onClick={() => setActiveTab('aws')}
            >
              <ChartLineUp size={20} />
              AWS Dashboard
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