import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Message, StructuredContent, ContentSection } from '../types';
import { motion } from 'framer-motion';
import { ClipboardIcon, CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon, CheckIcon } from '@heroicons/react/24/outline';
import { BuildingOfficeIcon, CurrencyDollarIcon, ServerStackIcon } from '@heroicons/react/24/outline';

export interface ChatMessageProps {
  message: Message;
  isLast?: boolean;
  updateReply?: (index: number, content: string) => void;
  index?: number;
  isStreaming?: boolean;
  streamingContent?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

// Define proper types for ReactMarkdown components
interface CodeProps {
  node?: any;
  inline?: boolean;
  className?: string;
  children?: React.ReactNode;
  [key: string]: any;
}

// Define proper types for SyntaxHighlighter
type SyntaxHighlighterProps = React.ComponentProps<typeof SyntaxHighlighter>;

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isLast,
  updateReply,
  index,
  isStreaming,
  streamingContent,
  onConfirm,
  onCancel
}) => {
  const { role, content, timestamp } = message;
  const isUser = role === 'user';
  const bubbleClass = isUser ? 'user-bubble' : 'assistant-bubble';
  const contentRef = useRef<HTMLDivElement>(null);
  
  // State to track if confirmation has been clicked
  const [isConfirmed, setIsConfirmed] = useState(false);
  
  // Don't show thinking animation when confirmation is active, but show it after confirmation
  const showThinking = (isStreaming && isLast && !message.confirmationData) || (isLast && isConfirmed);

  const formattedTime = timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  // Check if content is an architecture recommendation
  const isArchitectureRecommendation = !isUser && 
    (content.includes('# Architecture Recommendation') || 
     content.includes('# Architecture Recommendation for'));

  // Apply enhanced styling to architecture recommendations after render
  useEffect(() => {
    if (isArchitectureRecommendation && contentRef.current) {
      // Add architecture recommendation class to the container
      const container = contentRef.current;
      container.classList.add('architecture-recommendation');
      
      // Find cost sections and enhance them
      const costSections = container.querySelectorAll('h2');
      costSections.forEach(section => {
        if (section.textContent?.includes('Estimated Costs') || section.textContent?.includes('Cost')) {
          const nextElement = section.nextElementSibling;
          if (nextElement && nextElement.tagName === 'UL') {
            // Create cost estimate container
            const costEstimate = document.createElement('div');
            costEstimate.className = 'cost-estimate';
            
            // Create cost estimate title
            const costTitle = document.createElement('h3');
            costTitle.textContent = section.textContent;
            costEstimate.appendChild(costTitle);
            
            // Convert list items to cost items
            const listItems = nextElement.querySelectorAll('li');
            listItems.forEach(item => {
              const text = item.textContent || '';
              if (text.includes(':')) {
                const [category, value] = text.split(':');
                
                const costItem = document.createElement('div');
                costItem.className = 'cost-item';
                
                const costCategory = document.createElement('span');
                costCategory.className = 'cost-category';
                costCategory.textContent = category.trim();
                
                const costValue = document.createElement('span');
                costValue.className = 'cost-value';
                costValue.textContent = value.trim();
                
                costItem.appendChild(costCategory);
                costItem.appendChild(costValue);
                costEstimate.appendChild(costItem);
              } else if (text.toLowerCase().includes('total')) {
                const [category, value] = text.split(':');
                
                const totalCost = document.createElement('div');
                totalCost.className = 'total-cost';
                
                const totalCategory = document.createElement('span');
                totalCategory.className = 'cost-category';
                totalCategory.textContent = category.trim();
                
                const totalValue = document.createElement('span');
                totalValue.className = 'cost-value';
                totalValue.textContent = value.trim();
                
                totalCost.appendChild(totalCategory);
                totalCost.appendChild(totalValue);
                costEstimate.appendChild(totalCost);
              }
            });
            
            // Replace the original list with the enhanced cost estimate
            nextElement.parentNode?.replaceChild(costEstimate, nextElement);
          }
        }
      });
      
      // Enhance ASCII diagrams if present
      const preElements = container.querySelectorAll('pre');
      preElements.forEach(pre => {
        if (pre.textContent?.includes('|') || pre.textContent?.includes('+---')) {
          pre.classList.add('architecture-diagram');
        }
      });
      
      // Add content section wrapper
      const contentSections = container.querySelectorAll('p, ul, ol');
      contentSections.forEach(section => {
        if (!section.parentElement?.classList.contains('cost-estimate') && 
            !section.classList.contains('architecture-diagram')) {
          if (!section.parentElement?.classList.contains('content-section')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'content-section';
            section.parentNode?.insertBefore(wrapper, section);
            wrapper.appendChild(section);
          }
        }
      });
    }
  }, [content, isArchitectureRecommendation]);

  // Handle confirmation with state update
  const handleConfirm = () => {
    setIsConfirmed(true);
    if (onConfirm) {
      onConfirm();
    }
  };

  return (
    <div className={`chat-bubble ${bubbleClass}`}>
      <div className="message-body">
        <div className="message-content" ref={contentRef}>
          {message.confirmationData && !isConfirmed ? (
            <div className="message-confirmation">
              <div className="confirmation-header">
                {message.confirmationData.title ? (
                  <h3>{message.confirmationData.title}</h3>
                ) : (
                  <h3>Confirmation Required</h3>
                )}
                {message.confirmationData.question && (
                  <p className="confirmation-question">{message.confirmationData.question}</p>
                )}
              </div>
              <div className="confirmation-buttons" style={{
                display: 'flex',
                gap: '12px',
                marginTop: '16px',
                justifyContent: 'flex-start'
              }}>
                <motion.button
                  onClick={handleConfirm}
                  className="confirm-button"
                  whileTap={{ scale: 0.97 }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: 0.1 }}
                  type="button"
                  style={{
                    backgroundColor: '#10b981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '10px 16px',
                    fontSize: '14px',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    cursor: 'pointer',
                    boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <CheckCircleIcon className="w-5 h-5" />
                  <span>Confirm</span>
                </motion.button>
                <motion.button
                  onClick={onCancel}
                  className="cancel-button"
                  whileTap={{ scale: 0.97 }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: 0.2 }}
                  type="button"
                  style={{
                    backgroundColor: 'white',
                    color: '#6b7280',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '10px 16px',
                    fontSize: '14px',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    cursor: 'pointer',
                    boxShadow: '0 2px 5px rgba(0, 0, 0, 0.05)',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <XCircleIcon className="w-5 h-5" />
                  <span>Cancel</span>
                </motion.button>
              </div>
            </div>
          ) : (
            <div className="markdown-content" ref={contentRef}>
              <ReactMarkdown
                components={{
                  code({node, inline, className, children, ...props}: CodeProps) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <div className="syntax-highlighter-wrapper">
                        <div className="code-header">
                          <span className="code-language">{match[1]}</span>
                          <button
                            className="copy-button"
                            onClick={() => copyToClipboard(String(children).replace(/\n$/, ''))}
                            aria-label="Copy code"
                          >
                            <ClipboardIcon className="copy-icon" />
                          </button>
                        </div>
                        <SyntaxHighlighter
                          language={match[1]}
                          style={vscDarkPlus as any}
                          PreTag="div"
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      </div>
                    ) : (
                      <code className="inline-code" {...props}>
                        {children}
                      </code>
                    );
                  },
                  p({node, children, ...props}) {
                    return <p className="paragraph" {...props}>{children}</p>;
                  },
                  ul({node, children, ...props}) {
                    return <ul className="list" {...props}>{children}</ul>;
                  },
                  li({node, children, ...props}) {
                    return <li className="list-item" {...props}>{children}</li>;
                  },
                  a({node, children, ...props}) {
                    return <a className="link" target="_blank" rel="noopener noreferrer" {...props}>{children}</a>;
                  }
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}
        </div>
        <div className="timestamp">{formattedTime}</div>
      </div>
      {showThinking && (
        <div className="thinking">
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </div>
      )}
    </div>
  );
};

const formatJson = (json: any): React.ReactElement => {
  const jsonString = JSON.stringify(json, null, 2);

  // Replace JSON syntax with styled spans
  const formattedJson = jsonString
    .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
    .replace(/"([^"]+)"/g, '<span class="json-string">"$1"</span>')
    .replace(/\b(true|false)\b/g, '<span class="json-boolean">$1</span>')
    .replace(/\b(null)\b/g, '<span class="json-null">$1</span>')
    .replace(/\b(\d+)\b/g, '<span class="json-number">$1</span>');

  return <div dangerouslySetInnerHTML={{ __html: formattedJson }} />;
};

export default ChatMessage;