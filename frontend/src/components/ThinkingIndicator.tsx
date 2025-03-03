import React from 'react';
import { motion } from 'framer-motion';

const ThinkingIndicator: React.FC = () => {
  return (
    <div className="chat-bubble assistant-bubble">
      <div className="message-content">
        <div className="message-body">
          <div className="thinking-text">
            <span className="thinking-label">Thinking</span>
            <div className="cloud-animation-container">
              <div className="cloud-icon">
                <svg viewBox="-5 -5 280 280">
                  <path className="cloud-gray" d="M242.84,115.89c.23,20.08-16.69,36.51-36.79,36.51H50.24a45.2,45.2,0,1,1,0-90.39,44.77,44.77,0,0,1,6,.4,3.65,3.65,0,0,0,4.13-3.66v-.31a53.5,53.5,0,0,1,106.26-8.81,2.36,2.36,0,0,0,4,1.35,25.69,25.69,0,0,1,43,16.83,25.41,25.41,0,0,1-2.23,12.66.06.06,0,0,0,0,.08A36.09,36.09,0,0,1,242.84,115.89Z"/>
                  <path className="animated-cloud" d="M242.84,115.89c.23,20.08-16.69,36.51-36.79,36.51H50.24a45.2,45.2,0,1,1,0-90.39,44.77,44.77,0,0,1,6,.4,3.65,3.65,0,0,0,4.13-3.66v-.31a53.5,53.5,0,0,1,106.26-8.81,2.36,2.36,0,0,0,4,1.35,25.69,25.69,0,0,1,43,16.83,25.41,25.41,0,0,1-2.23,12.66.06.06,0,0,0,0,.08A36.09,36.09,0,0,1,242.84,115.89Z"/>
                </svg>
              </div>
            </div>
          </div>
          <div className="timestamp">
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThinkingIndicator; 