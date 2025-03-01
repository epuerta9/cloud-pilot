import React, { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { StructuredContent, ContentSection, TableRow, TerraformPlanJson } from '../types';
import { motion } from 'framer-motion';
import { ClipboardText, FileText, ArrowRight, Code, Table, ListBullets, Calendar, CheckCircle, Warning, Clock, Plus, Minus, PencilSimple } from 'phosphor-react';
import './DocumentView.css';

interface DocumentViewProps {
  content?: StructuredContent;
  isStreaming: boolean;
  terraformApplyData?: {
    terraform_json?: TerraformPlanJson;
    result?: string;
    error?: string;
    terraform_file_path?: string;
    terraform_built?: boolean;
    next_action?: string;
  };
}

const DocumentView: React.FC<DocumentViewProps> = ({ content, isStreaming, terraformApplyData }) => {
  const [activeTab, setActiveTab] = useState<string>('details');
  const [planDetails, setPlanDetails] = useState<ContentSection[]>([]);
  const [planOutput, setPlanOutput] = useState<ContentSection[]>([]);
  const [isTerraformPlan, setIsTerraformPlan] = useState<boolean>(false);
  const [isTerraformApply, setIsTerraformApply] = useState<boolean>(false);

  useEffect(() => {
    if (content && content.title === 'Terraform Plan') {
      setIsTerraformPlan(true);
      setIsTerraformApply(false);

      // Separate plan details and plan output
      const details: ContentSection[] = [];
      const output: ContentSection[] = [];
      let isOutput = false;

      content.sections.forEach(section => {
        if (section.type === 'heading' && typeof section.content === 'string' &&
            section.content === 'Plan Output') {
          isOutput = true;
          return;
        }

        if (isOutput) {
          output.push(section);
        } else {
          details.push(section);
        }
      });

      setPlanDetails(details);
      setPlanOutput(output);
    } else if ((content && content.title === 'Terraform Apply') || terraformApplyData) {
      setIsTerraformPlan(false);
      setIsTerraformApply(true);

      // If we have terraform apply data, make sure we're showing it
      if (terraformApplyData) {
        console.log('Setting up terraform apply view with data:', terraformApplyData);
      }
    } else {
      setIsTerraformPlan(false);
      setIsTerraformApply(false);
    }
  }, [content, terraformApplyData]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  // Function to process ANSI color codes in terminal output
  const processAnsiCodes = (text: string) => {
    // Replace common ANSI color codes with CSS classes
    let processed = text
      .replace(/\u001b\[0m/g, '</span>') // Reset
      .replace(/\u001b\[1m/g, '<span class="ansi-bold">') // Bold
      .replace(/\u001b\[31m/g, '<span class="ansi-red-fg">') // Red
      .replace(/\u001b\[32m/g, '<span class="ansi-green-fg">') // Green
      .replace(/\u001b\[33m/g, '<span class="ansi-yellow-fg">') // Yellow
      .replace(/\u001b\[34m/g, '<span class="ansi-blue-fg">'); // Blue

    // Ensure all spans are closed
    const openTags = (processed.match(/<span/g) || []).length;
    const closeTags = (processed.match(/<\/span>/g) || []).length;

    for (let i = 0; i < openTags - closeTags; i++) {
      processed += '</span>';
    }

    return processed;
  };

  // Render Terraform Apply Results
  const renderTerraformApplyResults = () => {
    if (!terraformApplyData) return null;

    console.log('Rendering terraform apply results:', terraformApplyData);

    const { terraform_json, result, error } = terraformApplyData;
    const isComplete = terraform_json?.complete || false;
    const isErrored = terraform_json?.errored || !!error;

    return (
      <div className="terraform-apply-result">
        {/* Status Banner */}
        <div className={`terraform-status ${isComplete && !isErrored ? 'success' : isErrored ? 'error' : ''}`}>
          <div className="terraform-status-icon">
            {isComplete && !isErrored ? (
              <CheckCircle size={32} weight="fill" />
            ) : isErrored ? (
              <Warning size={32} weight="fill" />
            ) : (
              <Clock size={32} weight="fill" />
            )}
          </div>
          <div className="terraform-status-text">
            {isComplete && !isErrored ? 'Apply Completed Successfully' :
             isErrored ? 'Apply Failed with Errors' : 'Apply In Progress'}
          </div>
        </div>

        {/* Resource Changes */}
        {terraform_json?.resource_changes && terraform_json.resource_changes.length > 0 && (
          <div className="terraform-resource-changes">
            <h3 className="section-title">Resource Changes</h3>

            {terraform_json.resource_changes.map((change: any, index: number) => (
              <div key={index} className="terraform-resource-change">
                <div className="resource-change-header">
                  <div className="resource-name">{change.address || change.name || `Resource ${index + 1}`}</div>
                  <div className={`resource-action action-${change.change?.actions?.[0]?.toLowerCase() || 'update'}`}>
                    {change.change?.actions?.[0] === 'create' && <Plus size={14} weight="bold" />}
                    {change.change?.actions?.[0] === 'update' && <PencilSimple size={14} weight="bold" />}
                    {change.change?.actions?.[0] === 'delete' && <Minus size={14} weight="bold" />}
                    <span style={{ marginLeft: '4px' }}>{change.change?.actions?.[0] || 'Update'}</span>
                  </div>
                </div>
                {change.change?.before && change.change?.after && (
                  <div className="resource-details">
                    <pre>{JSON.stringify(change.change, null, 2)}</pre>
                  </div>
                )}
              </div>
            ))}

            {/* Summary */}
            <div className="terraform-summary">
              <div className="summary-title">Summary of Changes</div>
              <div className="summary-counts">
                <div className="summary-count count-create">
                  <Plus size={16} weight="bold" />
                  <span>
                    {terraform_json.resource_changes?.filter((c: any) =>
                      c.change?.actions?.[0] === 'create').length || 0} to add
                  </span>
                </div>
                <div className="summary-count count-update">
                  <PencilSimple size={16} weight="bold" />
                  <span>
                    {terraform_json.resource_changes?.filter((c: any) =>
                      c.change?.actions?.[0] === 'update').length || 0} to change
                  </span>
                </div>
                <div className="summary-count count-delete">
                  <Minus size={16} weight="bold" />
                  <span>
                    {terraform_json.resource_changes?.filter((c: any) =>
                      c.change?.actions?.[0] === 'delete').length || 0} to destroy
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Terminal Output */}
        {result && (
          <div className="terraform-output">
            <h3 className="section-title">Terminal Output</h3>
            <div
              className="terminal-output"
              dangerouslySetInnerHTML={{ __html: processAnsiCodes(result) }}
            />
          </div>
        )}

        {/* Error Output */}
        {error && (
          <div className="terraform-error">
            <h3 className="section-title">Error</h3>
            <div className="terminal-output ansi-red-fg">{error}</div>
          </div>
        )}
      </div>
    );
  };

  if (!content && !isStreaming && !terraformApplyData) {
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

        // Skip timestamp entirely
        if (textContent.startsWith('Timestamp:')) {
          return null;
        }

        // Special handling for status and version
        if (textContent.startsWith('Status:')) {
          const status = textContent.replace('Status:', '').trim();
          return (
            <div key={index} className="document-tag-container">
              <div className={`document-tag ${status.toLowerCase() === 'complete' ? 'success' : status.toLowerCase() === 'error' ? 'error' : 'pending'}`}>
                {status.toLowerCase() === 'complete' ? (
                  <CheckCircle size={16} weight="fill" />
                ) : status.toLowerCase() === 'error' ? (
                  <Warning size={16} weight="fill" />
                ) : (
                  <Clock size={16} weight="fill" />
                )}
                <span>Status: {status}</span>
              </div>
            </div>
          );
        } else if (textContent.startsWith('Terraform Version:')) {
          const version = textContent.replace('Terraform Version:', '').trim();
          return (
            <div key={index} className="document-tag-container">
              <div className="document-tag info">
                <Code size={16} weight="fill" />
                <span>Terraform Version: {version}</span>
              </div>
            </div>
          );
        }

        // Default text rendering
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
      {isStreaming && !content && !terraformApplyData && (
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

      {(content || terraformApplyData) && (
        <motion.div
          className="document-content"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          {content?.title && (
            <div className="document-header">
              <h1 className="document-title">{content.title}</h1>

              {isTerraformPlan && (
                <div className="tabs-wrapper">
                  <div className="document-tabs">
                    <button
                      className={`document-tab ${activeTab === 'details' ? 'active' : ''}`}
                      onClick={() => setActiveTab('details')}
                    >
                      <Table size={18} weight="regular" />
                      <span>Plan Details</span>
                    </button>
                    <button
                      className={`document-tab ${activeTab === 'output' ? 'active' : ''}`}
                      onClick={() => setActiveTab('output')}
                      disabled={planOutput.length === 0}
                    >
                      <Code size={18} weight="regular" />
                      <span>Plan Output</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {!content?.title && terraformApplyData && (
            <div className="document-header">
              <h1 className="document-title">Terraform Apply Results</h1>
            </div>
          )}

          <div className="document-sections">
            {isTerraformPlan ? (
              activeTab === 'details' ? (
                <div className="plan-details-wrapper">
                  <div className="document-tags-row">
                    <div className="document-tags-container">
                      {planDetails.map((section, index) => {
                        if (section.type === 'text' && typeof section.content === 'string') {
                          const textContent = section.content;
                          if (textContent.startsWith('Status:') ||
                              textContent.startsWith('Terraform Version:')) {
                            return renderSection(section, index);
                          }
                        }
                        return null;
                      })}
                    </div>
                  </div>
                  <div className="plan-content-wrapper">
                    {planDetails.map((section, index) => {
                      if (section.type === 'text' && typeof section.content === 'string') {
                        const textContent = section.content;
                        if (textContent.startsWith('Status:') ||
                            textContent.startsWith('Terraform Version:')) {
                          return null;
                        }
                      }
                      // Skip the first heading which is "Terraform Plan Details" to avoid duplication
                      if (section.type === 'heading' && typeof section.content === 'string' &&
                          section.content === 'Terraform Plan Details') {
                        return null;
                      }
                      return renderSection(section, index);
                    })}
                  </div>
                </div>
              ) : (
                <div className="plan-output-wrapper">
                  {planOutput.length > 0 ? (
                    planOutput.map(renderSection)
                  ) : (
                    <div className="document-empty-tab">
                      <p>No plan output available</p>
                    </div>
                  )}
                </div>
              )
            ) : isTerraformApply ? (
              renderTerraformApplyResults()
            ) : (
              content?.sections.map(renderSection)
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default DocumentView;