import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { StructuredContent, ContentSection, TableRow } from '../types';
import { motion } from 'framer-motion';
import { ClipboardText, FileText, ArrowRight } from 'phosphor-react';

interface DocumentViewProps {
  content?: StructuredContent;
  isStreaming: boolean;
}

const DocumentView: React.FC<DocumentViewProps> = ({ content, isStreaming }) => {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (!content && !isStreaming) {
    return (
      <div className="document-empty-state">
        <motion.div 
          className="document-empty-content"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <FileText size={48} weight="light" className="empty-state-icon" />
          <h2>Ready to generate documentation</h2>
          <p>Ask a question or request information from Cloud Pilot to see structured content displayed here.</p>
          
          <div className="empty-state-tips">
            <div className="empty-state-tip">
              <ArrowRight size={16} className="tip-icon" />
              <span>Ask for code examples, explanations or documentation</span>
            </div>
            <div className="empty-state-tip">
              <ArrowRight size={16} className="tip-icon" />
              <span>Request structured information about any topic</span>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  const renderSection = (section: ContentSection, index: number) => {
    switch (section.type) {
      case 'heading':
        const level = section.metadata?.level || 2;
        const headingContent = typeof section.content === 'string' ? section.content : '';
        
        if (level === 1) {
          return <h1 key={index} className="document-heading heading-1">{headingContent}</h1>;
        } else if (level === 2) {
          return <h2 key={index} className="document-heading heading-2">{headingContent}</h2>;
        } else if (level === 3) {
          return <h3 key={index} className="document-heading heading-3">{headingContent}</h3>;
        } else if (level === 4) {
          return <h4 key={index} className="document-heading heading-4">{headingContent}</h4>;
        } else if (level === 5) {
          return <h5 key={index} className="document-heading heading-5">{headingContent}</h5>;
        } else {
          return <h6 key={index} className="document-heading heading-6">{headingContent}</h6>;
        }
      
      case 'text':
        const textContent = typeof section.content === 'string' ? section.content : '';
        return (
          <p key={index} className="document-paragraph">
            {textContent}
          </p>
        );
      
      case 'code':
        const codeContent = typeof section.content === 'string' ? section.content : '';
        return (
          <div key={index} className="document-code-block">
            <div className="code-header">
              <span className="code-language">{section.metadata?.language || 'code'}</span>
              <button 
                className="copy-button"
                onClick={() => copyToClipboard(codeContent)}
                aria-label="Copy code"
              >
                <ClipboardText size={18} className="copy-icon" />
              </button>
            </div>
            <SyntaxHighlighter 
              language={section.metadata?.language} 
              style={vscDarkPlus as any}
            >
              {codeContent}
            </SyntaxHighlighter>
          </div>
        );
      
      case 'list':
        if (Array.isArray(section.content)) {
          const contentArray = section.content as any[];
          const isStringArray = contentArray.every((item: any) => typeof item === 'string');
          
          if (isStringArray) {
            const listItems = contentArray as string[];
            return (
              <ul key={index} className="document-list">
                {listItems.map((item, i) => (
                  <li key={i} className="document-list-item">{item}</li>
                ))}
              </ul>
            );
          }
        }
        return null;
      
      case 'table':
        if (Array.isArray(section.content) && section.content.length > 0) {
          const firstItem = section.content[0] as any;
          if (typeof firstItem === 'object' && firstItem !== null) {
            const tableRows = section.content as TableRow[];
            return (
              <div key={index} className="document-table-container">
                <table className="document-table">
                  <thead>
                    <tr>
                      {Object.keys(tableRows[0]).map((header, i) => (
                        <th key={i}>{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableRows.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {Object.values(row).map((cell, cellIndex) => (
                          <td key={cellIndex}>{String(cell)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          }
        }
        return null;
      
      default:
        return null;
    }
  };

  return (
    <div className="document-view">
      {isStreaming && !content && (
        <div className="document-streaming-placeholder">
          <div className="document-streaming-indicator">
            <span>Processing content...</span>
            <div className="streaming-dots">
              {[0, 1, 2].map((dot) => (
                <motion.div
                  key={dot}
                  className="streaming-dot"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.7, 1, 0.7]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: dot * 0.3,
                    ease: "easeInOut"
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      )}
      
      {content && (
        <motion.div 
          className="document-content"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {content.title && (
            <h1 className="document-title">{content.title}</h1>
          )}
          
          <div className="document-sections">
            {content.sections.map(renderSection)}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default DocumentView; 