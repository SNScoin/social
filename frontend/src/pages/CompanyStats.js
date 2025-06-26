import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import './CompanyStats.css';
import { FaTrash, FaSyncAlt } from 'react-icons/fa';
import { toast } from 'react-toastify';

const platforms = [
  { name: 'YouTube', icon: 'https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg' },
  { name: 'TikTok', icon: 'https://cdn-icons-png.flaticon.com/512/3046/3046120.png' },
  { name: 'Instagram', icon: 'https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png' },
  { name: 'Facebook', icon: 'https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg' }
];

export default function CompanyStats() {
  const { companyId } = useParams();
  const navigate = useNavigate();
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(companyId);
  const [stats, setStats] = useState(null);
  const [links, setLinks] = useState([]);
  const [platform, setPlatform] = useState(platforms[0].name);
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('Initial load with companyId:', companyId);
    console.log('Selected company:', selectedCompany);
    fetchCompanies();
    if (companyId) {
      console.log('Fetching data for company ID:', companyId);
      fetchStats(companyId);
      fetchLinks(companyId);
      setSelectedCompany(companyId);
    } else {
      console.warn('No company ID provided in URL');
    }
  }, [companyId]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`
    };
  };

  const fetchCompanies = async () => {
    try {
      console.log('Fetching companies...');
      const res = await axios.get('http://localhost:8000/api/companies/', {
        headers: getAuthHeaders()
      });
      console.log('Companies response:', res.data);
      setCompanies(res.data);
    } catch (err) {
      console.error('Error fetching companies:', err);
      setError('Failed to fetch companies');
    }
  };

  const fetchStats = async (id) => {
    try {
      console.log('Fetching stats for company:', id);
      const res = await axios.get(`http://localhost:8000/api/companies/${id}/stats`, {
        headers: getAuthHeaders()
      });
      console.log('Stats response:', res.data);
      setStats(res.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to fetch stats');
    }
  };

  const fetchLinks = async (id) => {
    try {
      console.log('Fetching links for company:', id);
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No token found in localStorage');
        setError('Not authenticated');
        return;
      }
      console.log('Making request to:', `http://localhost:8000/api/links/?company_id=${id}`);
      const res = await axios.get(`http://localhost:8000/api/links/?company_id=${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      console.log('Links response:', res.data);
      if (Array.isArray(res.data)) {
        console.log('Number of links received:', res.data.length);
        setLinks(res.data);
      } else {
        console.error('Response is not an array:', res.data);
        setError('Invalid response format');
      }
    } catch (err) {
      console.error('Error fetching links:', err);
      if (err.response) {
        console.error('Error response:', err.response.data);
        console.error('Error status:', err.response.status);
      }
      setError('Failed to fetch links');
    }
  };

  const handleCompanyChange = (e) => {
    const newCompanyId = e.target.value;
    console.log('Company changed to:', newCompanyId);
    setSelectedCompany(newCompanyId);
    if (newCompanyId) {
      console.log('Fetching data for new company ID:', newCompanyId);
      fetchStats(newCompanyId);
      fetchLinks(newCompanyId);
      navigate(`/companies/${newCompanyId}/stats`);
    } else {
      console.warn('No company selected');
    }
  };

  const handleAddLink = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/links/', {
        url,
        company_id: selectedCompany,
        platform
      }, {
        headers: getAuthHeaders()
      });
      
      // Check Monday.com sync status
      const { monday_sync_status, monday_error } = response.data;
      
      if (monday_sync_status === 'success') {
        toast.success('Link added and synced to Monday.com!');
      } else if (monday_sync_status === 'error') {
        toast.error(`Link added but Monday.com sync failed: ${monday_error}`);
      } else if (monday_sync_status === 'not_configured') {
        toast.info('Link added! Monday.com not configured for this company.');
      } else {
        toast.success('Link added successfully!');
      }
      
      setUrl('');
      fetchLinks(selectedCompany);
      fetchStats(selectedCompany);
    } catch (err) {
      toast.error('Failed to add link');
      setError('Failed to add link');
      console.error('Error adding link:', err);
    }
  };

  const handleDeleteLink = async (linkId) => {
    if (!window.confirm('Are you sure you want to delete this link?')) return;
    try {
      await axios.delete(`http://localhost:8000/api/links/${linkId}`, {
        headers: getAuthHeaders()
      });
      fetchLinks(selectedCompany);
      fetchStats(selectedCompany);
      toast.success('Link deleted successfully!');
    } catch (err) {
      toast.error('Failed to delete link');
      setError('Failed to delete link');
      console.error('Error deleting link:', err);
    }
  };

  const handleRefreshStats = async (linkId) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/links/${linkId}/refresh`, {}, {
        headers: getAuthHeaders()
      });
      
      // Check Monday.com sync status
      const { monday_sync_status, monday_error } = response.data;
      
      if (monday_sync_status === 'success') {
        toast.success('Link stats refreshed and synced to Monday.com!');
      } else if (monday_sync_status === 'error') {
        toast.error(`Link refreshed but Monday.com sync failed: ${monday_error}`);
      } else if (monday_sync_status === 'not_configured') {
        toast.info('Link refreshed! Monday.com not configured for this company.');
      } else {
        toast.success('Link stats refreshed!');
      }
      
      fetchLinks(selectedCompany);
      fetchStats(selectedCompany);
    } catch (err) {
      toast.error('Failed to refresh stats');
      setError('Failed to refresh stats');
      console.error('Error refreshing stats:', err);
    }
  };

  return (
    <div className="company-stats-bg">
      <div className="company-stats-header">
        <div className="company-title">
          <span className="logo-title">Social Media Stats</span>
        </div>
        <div className="company-actions">
          <select value={selectedCompany} onChange={handleCompanyChange} className="company-dropdown">
            {companies.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <a href="/companies" className="nav-link">Companies</a>
          <a href="/logout" className="nav-link">Logout</a>
        </div>
      </div>
      {stats && (
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-label">Total Links</div>
            <div className="stat-value">{stats.total_links}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Likes</div>
            <div className="stat-value">{stats.total_likes}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Views</div>
            <div className="stat-value">{stats.total_views}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Comments</div>
            <div className="stat-value">{stats.total_comments}</div>
          </div>
        </div>
      )}
      <div className="add-link-card">
        <h2>Add New Link</h2>
        <form onSubmit={handleAddLink} className="add-link-form">
          <div className="platform-select">
            {platforms.map(p => (
              <button
                type="button"
                key={p.name}
                className={`platform-btn${platform === p.name ? ' selected' : ''}`}
                onClick={() => setPlatform(p.name)}
              >
                <img src={p.icon} alt={p.name} className="platform-icon" />
                <span>{p.name}</span>
              </button>
            ))}
          </div>
          <input
            type="text"
            className="link-input"
            placeholder="Enter a YouTube, TikTok, or Instagram link"
            value={url}
            onChange={e => setUrl(e.target.value)}
            required
          />
          <button type="submit" className="add-link-btn">Add Link</button>
        </form>
      </div>
      <div className="all-links-card">
        <h2>All Links</h2>
        <table className="links-table">
          <thead>
            <tr>
              <th>Platform</th>
              <th>Title</th>
              <th>URL</th>
              <th>Views</th>
              <th>Likes</th>
              <th>Comments</th>
              <th>Monday.com</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {links.map(link => (
              <tr key={link.id}>
                <td>{link.platform}</td>
                <td>{link.title && link.title.trim() !== ""
                  ? (link.title.length > 40 ? link.title.slice(0, 40) + '...' : link.title)
                  : <a href={link.url} target="_blank" rel="noopener noreferrer">{link.url}</a>
                }</td>
                <td><a href={link.url} target="_blank" rel="noopener noreferrer">{link.url}</a></td>
                <td>{link.metrics?.views ?? 0}</td>
                <td>{link.metrics?.likes ?? 0}</td>
                <td>{link.metrics?.comments ?? 0}</td>
                <td>
                  {link.monday_item_id ? (
                    <span title="Synced to Monday.com" style={{color: '#10b981', fontWeight: 'bold', fontSize: '1.2em'}}>✅</span>
                  ) : (
                    <span title="Not synced to Monday.com" style={{color: '#e11d48', fontWeight: 'bold', fontSize: '1.2em'}}>❌</span>
                  )}
                </td>
                <td>
                  <button
                    onClick={() => handleDeleteLink(link.id)}
                    className="icon-btn delete"
                    title="Delete Link"
                  >
                    <FaTrash />
                  </button>
                  <button
                    onClick={() => handleRefreshStats(link.id)}
                    className="icon-btn"
                    title="Refresh Stats"
                  >
                    <FaSyncAlt />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {error && <div className="error">{error}</div>}
    </div>
  );
} 