import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Not authenticated');
        return;
      }

      const response = await axios.get('http://localhost:8000/api/stats/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-bg">
<<<<<<< HEAD
        <div className="dashboard-container">
          <div className="dashboard-header">
            <h1>Dashboard</h1>
          </div>
          <div className="loading">Loading...</div>
        </div>
=======
        <div className="dashboard-header">
          <h1>Dashboard</h1>
        </div>
        <div className="loading">Loading...</div>
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-bg">
<<<<<<< HEAD
        <div className="dashboard-container">
          <div className="dashboard-header">
            <h1>Dashboard</h1>
          </div>
          <div className="error-message">{error}</div>
        </div>
=======
        <div className="dashboard-header">
          <h1>Dashboard</h1>
        </div>
        <div className="error-message">{error}</div>
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
      </div>
    );
  }

  return (
    <div className="dashboard-bg">
<<<<<<< HEAD
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <p>Overview of your social media performance</p>
        </div>
        
        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <h3>Total Links</h3>
              <div className="stat-value">{stats?.total_links || 0}</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">👁️</div>
            <div className="stat-content">
              <h3>Total Views</h3>
              <div className="stat-value">{stats?.total_views || 0}</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">👍</div>
            <div className="stat-content">
              <h3>Total Likes</h3>
              <div className="stat-value">{stats?.total_likes || 0}</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">💬</div>
            <div className="stat-content">
              <h3>Total Comments</h3>
              <div className="stat-value">{stats?.total_comments || 0}</div>
            </div>
          </div>
        </div>

        <div className="dashboard-content">
          <div className="content-card">
            <h2>Welcome to Social Stats Dashboard</h2>
            <p>This is your central hub for managing and monitoring your social media performance across different platforms.</p>
            
            <div className="quick-actions">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <a href="/companies" className="action-btn">Manage Companies</a>
                <a href="/reports" className="action-btn">View Reports</a>
              </div>
=======
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Overview of your social media performance</p>
      </div>
      
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>Total Links</h3>
            <div className="stat-value">{stats?.total_links || 0}</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">👁️</div>
          <div className="stat-content">
            <h3>Total Views</h3>
            <div className="stat-value">{stats?.total_views || 0}</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">👍</div>
          <div className="stat-content">
            <h3>Total Likes</h3>
            <div className="stat-value">{stats?.total_likes || 0}</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <h3>Total Comments</h3>
            <div className="stat-value">{stats?.total_comments || 0}</div>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="content-card">
          <h2>Welcome to Social Stats Dashboard</h2>
          <p>This is your central hub for managing and monitoring your social media performance across different platforms.</p>
          
          <div className="quick-actions">
            <h3>Quick Actions</h3>
            <div className="action-buttons">
              <a href="/companies" className="action-btn">Manage Companies</a>
              <a href="/reports" className="action-btn">View Reports</a>
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 