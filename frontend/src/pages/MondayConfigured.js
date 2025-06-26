import React from 'react';
import './MondayConfigured.css';

export default function MondayConfigured() {
  return (
    <div className="monday-configured-bg">
      <div className="monday-configured-header">
        <h1>Monday.com Connected!</h1>
        <p>Your Monday.com integration is now active and ready to use</p>
      </div>
      
      <div className="monday-configured-content">
        <div className="content-card">
          <div className="success-info">
            <div className="success-icon">✅</div>
            <div className="success-details">
              <h2>Integration Successful</h2>
              <p>Your Monday.com workspace has been successfully connected. Your social media data will now automatically sync to your selected board.</p>
            </div>
          </div>
          
          <div className="sync-info">
            <h3>What's Syncing</h3>
            <div className="sync-features">
              <div className="sync-feature">
                <span className="feature-icon">📊</span>
                <div className="feature-content">
                  <h4>Social Media Links</h4>
                  <p>All your social media links are automatically added as items in your Monday.com board</p>
                </div>
              </div>
              
              <div className="sync-feature">
                <span className="feature-icon">📈</span>
                <div className="feature-content">
                  <h4>Performance Metrics</h4>
                  <p>Views, likes, and comments are updated in real-time on your Monday.com items</p>
                </div>
              </div>
              
              <div className="sync-feature">
                <span className="feature-icon">🔄</span>
                <div className="feature-content">
                  <h4>Automatic Updates</h4>
                  <p>Metrics are refreshed automatically to keep your Monday.com board up to date</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="action-section">
            <div className="action-buttons">
              <a href="/companies" className="action-btn primary">Manage Companies</a>
              <a href="/statistics" className="action-btn secondary">View Dashboard</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 