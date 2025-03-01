import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Message } from '../types';
import { motion } from 'framer-motion';
import { ClipboardIcon } from '@heroicons/react/24/outline';

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
      {message.requiresConfirmation && message.confirmationData?.terraform_json && (
        <motion.div
          className="chat-bubble assistant-bubble"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="message-content">
            <div className="avatar">
              <span>CP</span>
            </div>
            <div className="message-body">
              <div className="plan-output markdown-content">
                <ReactMarkdown>
                  {message.confirmationData.terraform_json}
                </ReactMarkdown>
              </div>
              <div className="timestamp">
                {formattedTime}
              </div>
            </div>
          </div>
        </motion.div>
      )}
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
          </div>
          {message.requiresConfirmation && (
            <div className="confirmation-buttons">
              <button onClick={onConfirm} className="confirm-button">
                Confirm
              </button>
              <button onClick={onCancel} className="cancel-button">
                Cancel
              </button>
            </div>
          )}
        </div>
      </motion.div>
    </>
  );
};

export default ChatMessage;