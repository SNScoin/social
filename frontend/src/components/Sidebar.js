import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Sidebar.css';

export default function Sidebar() {
  const [user, setUser] = useState(null);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserInfo();
  }, []);

  const fetchUserInfo = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }

      // For now, we'll use the token to decode user info
      // In a real app, you'd have an endpoint to get user details
      const tokenData = JSON.parse(atob(token.split('.')[1]));
      setUser({
        email: tokenData.sub || 'user@example.com',
        username: tokenData.sub?.split('@')[0] || 'User'
      });
    } catch (error) {
      console.error('Error fetching user info:', error);
      navigate('/login');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const menuItems = [
    {
      path: '/companies',
      label: 'Companies',
      icon: '🏢',
      description: 'Manage your companies'
    },
    {
      path: '/statistics',
      label: 'Dashboard',
      icon: '📊',
      description: 'View overall statistics'
    },
    {
      path: '/reports',
      label: 'Reports',
      icon: '📈',
      description: 'Generate detailed reports'
    }
  ];

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-toggle" onClick={() => setIsCollapsed(!isCollapsed)}>
          {isCollapsed ? '→' : '←'}
        </div>
        {!isCollapsed && (
          <div className="app-title">
            <h2>Social Stats</h2>
          </div>
        )}
      </div>

      <div className="user-section">
        {user && (
          <div className="user-info">
            <div className="user-avatar">
              {user.username.charAt(0).toUpperCase()}
            </div>
            {!isCollapsed && (
              <div className="user-details">
                <div className="user-name">{user.username}</div>
                <div className="user-email">{user.email}</div>
              </div>
            )}
          </div>
        )}
      </div>

      <nav className="sidebar-nav">
        <ul className="nav-menu">
          {menuItems.map((item) => (
            <li key={item.path} className={`nav-item ${isActive(item.path) ? 'active' : ''}`}>
              <Link to={item.path} className="nav-link">
                <span className="nav-icon">{item.icon}</span>
                {!isCollapsed && (
                  <div className="nav-content">
                    <span className="nav-label">{item.label}</span>
                    <span className="nav-description">{item.description}</span>
                  </div>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        {!isCollapsed && (
          <button onClick={handleLogout} className="logout-btn">
            <span className="logout-icon">🚪</span>
            <span>Logout</span>
          </button>
        )}
        {isCollapsed && (
          <button onClick={handleLogout} className="logout-btn collapsed" title="Logout">
            <span className="logout-icon">🚪</span>
          </button>
        )}
      </div>
    </div>
  );
} 