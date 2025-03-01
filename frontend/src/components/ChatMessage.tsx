import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Message, StructuredContent, ContentSection } from '../types';
import { motion } from 'framer-motion';
import { ClipboardIcon, CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon, CheckIcon } from '@heroicons/react/24/outline';

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

  const formattedTime = timestamp.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <>
      <motion.div
        className={`chat-bubble ${bubbleClass}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="message-content">
          <div className={isUser ? "user-avatar" : "avatar"}>
            <span>{isUser ? 'You' : 'CP'}</span>
          </div>
          <div className="message-body">
            {isUser ? (
              <div className="markdown-content">
                {content}
              </div>
            ) : (
              <div className="markdown-content">
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
            <div className="timestamp">
              {formattedTime}
            </div>

            {message.requiresConfirmation && message.confirmationData?.plan_json && (
              <div className="message-confirmation">
                <div className="confirmation-header">
                  {!content.toLowerCase().includes('confirmation required') && (
                    <h3>Confirmation Required</h3>
                  )}
                  {message.confirmationData.question && (
                    <p className="confirmation-question">{message.confirmationData.question}</p>
                  )}
                </div>
                <div className="confirmation-buttons">
                  <motion.button
                    onClick={onConfirm}
                    className="confirm-button"
                    whileTap={{ scale: 0.98 }}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: 0.1 }}
                  >
                    <CheckCircleIcon className="w-5 h-5" />
                    <span>Confirm</span>
                  </motion.button>
                  <motion.button
                    onClick={onCancel}
                    className="cancel-button"
                    whileTap={{ scale: 0.98 }}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: 0.2 }}
                  >
                    <XCircleIcon className="w-5 h-5" />
                    <span>Cancel</span>
                  </motion.button>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </>
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