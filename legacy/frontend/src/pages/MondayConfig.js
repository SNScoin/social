import React from 'react';
import './MondayConfig.css';

export default function MondayConfig() {
  return (
    <div className="monday-config-bg">
      <div className="monday-config-header">
        <h1>Monday.com Integration</h1>
        <p>Connect your Monday.com workspace to sync your social media data</p>
      </div>
      
      <div className="monday-config-content">
        <div className="content-card">
          <div className="integration-info">
            <div className="integration-icon">🔗</div>
            <div className="integration-details">
              <h2>Connect to Monday.com</h2>
              <p>Sync your social media links and metrics directly to your Monday.com boards for better project management and team collaboration.</p>
            </div>
          </div>
          
          <div className="setup-steps">
            <h3>Setup Steps</h3>
            <div className="step-list">
              <div className="step-item">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h4>Get Your Monday.com API Token</h4>
                  <p>Go to your Monday.com account settings and generate an API token</p>
                </div>
              </div>
              
              <div className="step-item">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h4>Connect Your Workspace</h4>
                  <p>Enter your API token to connect your workspace</p>
                </div>
              </div>
              
              <div className="step-item">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h4>Select Your Board</h4>
                  <p>Choose which Monday.com board to sync your data to</p>
                </div>
              </div>
              
              <div className="step-item">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h4>Start Syncing</h4>
                  <p>Your social media links will automatically sync to Monday.com</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="cta-section">
            <p>Ready to connect? Click the button below to start the integration process.</p>
            <button className="connect-btn">Connect Monday.com</button>
          </div>
        </div>
      </div>
    </div>
  );
} 