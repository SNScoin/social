import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Companies.css';
import { FaTrash, FaSyncAlt } from 'react-icons/fa';
import { toast } from 'react-toastify';

export default function Companies() {
  const [companies, setCompanies] = useState([]);
  const [newCompany, setNewCompany] = useState({ name: '' });
  const [error, setError] = useState('');
  const [showMondayModal, setShowMondayModal] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [mondayConfig, setMondayConfig] = useState({
    apiToken: '',
    workspaceId: '',
    boardId: ''
  });
  const [mondayWorkspaces, setMondayWorkspaces] = useState([]);
  const [mondayBoards, setMondayBoards] = useState([]);
  const [mondayColumns, setMondayColumns] = useState([]);
  const [columnMapping, setColumnMapping] = useState({
    views: '',
    likes: '',
    comments: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    console.log('Companies component mounted');
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    console.log('Starting fetchCompanies');
    try {
      const token = localStorage.getItem('access_token');
      console.log('Token from localStorage:', token ? 'exists' : 'missing');
      
      if (!token) {
        console.log('No token found, redirecting to login');
        setError('Not authenticated');
        return;
      }

      console.log('Making API request to /api/companies/');
      const response = await axios.get('http://localhost:8000/api/companies/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      console.log('API Response:', response.data);
      setCompanies(response.data);
    } catch (err) {
      console.error('Error in fetchCompanies:', err);
      setError('Failed to fetch companies');
    }
  };

  const handleInputChange = (e) => {
    setNewCompany({ ...newCompany, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Not authenticated');
        toast.error('Not authenticated');
        return;
      }
      await axios.post('http://localhost:8000/api/companies/', newCompany, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setNewCompany({ name: '' });
      fetchCompanies();
      toast.success('Company created successfully!');
    } catch (err) {
      setError('Failed to add company');
      toast.error('Failed to add company');
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Not authenticated');
        toast.error('Not authenticated');
        return;
      }
      await axios.delete(`http://localhost:8000/api/companies/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      fetchCompanies();
      toast.success('Company deleted successfully!');
    } catch (err) {
      setError('Failed to delete company');
      toast.error('Failed to delete company');
      console.error(err);
    }
  };

  const openMondayModal = (company) => {
    setSelectedCompany(company);
    setShowMondayModal(true);
    setMondayConfig({
      apiToken: '',
      workspaceId: '',
      boardId: ''
    });
    setMondayWorkspaces([]);
    setMondayBoards([]);
  };

  const closeMondayModal = () => {
    setShowMondayModal(false);
    setSelectedCompany(null);
    setMondayConfig({
      apiToken: '',
      workspaceId: '',
      boardId: ''
    });
  };

  const handleMondayConfigChange = (e) => {
    setMondayConfig({
      ...mondayConfig,
      [e.target.name]: e.target.value
    });
  };

  const fetchMondayWorkspaces = async () => {
    if (!mondayConfig.apiToken) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.post('http://localhost:8000/api/monday/workspaces', {
        api_token: mondayConfig.apiToken
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setMondayWorkspaces(response.data.workspaces || []);
    } catch (err) {
      console.error('Error fetching Monday.com workspaces:', err);
      setError('Failed to fetch Monday.com workspaces');
    } finally {
      setLoading(false);
    }
  };

  const fetchMondayBoards = async () => {
    if (!mondayConfig.workspaceId || !mondayConfig.apiToken) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.post('http://localhost:8000/api/monday/boards', {
        workspace_id: mondayConfig.workspaceId,
        api_token: mondayConfig.apiToken
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setMondayBoards(response.data.boards || []);
    } catch (err) {
      console.error('Error fetching Monday.com boards:', err);
      setError('Failed to fetch Monday.com boards');
    } finally {
      setLoading(false);
    }
  };

  const fetchMondayColumns = async () => {
    if (!mondayConfig.apiToken || !mondayConfig.boardId) return;
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await axios.post('http://localhost:8000/api/monday/columns', {
        api_token: mondayConfig.apiToken,
        board_id: mondayConfig.boardId
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setMondayColumns(response.data.columns || []);
    } catch (err) {
      setError('Failed to fetch Monday.com columns');
      setMondayColumns([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mondayConfig.apiToken) {
      fetchMondayWorkspaces();
    }
  }, [mondayConfig.apiToken]);

  useEffect(() => {
    if (mondayConfig.workspaceId) {
      fetchMondayBoards();
    }
  }, [mondayConfig.workspaceId]);

  useEffect(() => {
    if (mondayConfig.boardId) {
      fetchMondayColumns();
    } else {
      setMondayColumns([]);
      setColumnMapping({ views: '', likes: '', comments: '' });
    }
  }, [mondayConfig.boardId]);

  const handleColumnMappingChange = (e) => {
    setColumnMapping({ ...columnMapping, [e.target.name]: e.target.value });
  };

  const connectMonday = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const viewsCol = mondayColumns.find(col => col.id === columnMapping.views);
      const likesCol = mondayColumns.find(col => col.id === columnMapping.likes);
      const commentsCol = mondayColumns.find(col => col.id === columnMapping.comments);
      await axios.post('http://localhost:8000/api/monday/connect', {
        company_id: selectedCompany.id,
        api_token: mondayConfig.apiToken,
        workspace_id: mondayConfig.workspaceId,
        board_id: mondayConfig.boardId,
        views_column_id: columnMapping.views,
        views_column_name: viewsCol ? viewsCol.title : '',
        likes_column_id: columnMapping.likes,
        likes_column_name: likesCol ? likesCol.title : '',
        comments_column_id: columnMapping.comments,
        comments_column_name: commentsCol ? commentsCol.title : ''
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      closeMondayModal();
      fetchCompanies();
      toast.success('Monday.com connected successfully!');
    } catch (err) {
      setError('Failed to connect Monday.com');
      toast.error('Failed to connect Monday.com');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="companies-bg">
      <div className="companies-header">
        <h1>Companies</h1>
      </div>
      <div className="companies-card">
        <h2 className="section-title">Create New Company</h2>
        <form onSubmit={handleSubmit} className="company-form">
          <label htmlFor="company-name" className="company-label">Company Name</label>
          <input
            id="company-name"
            type="text"
            name="name"
            value={newCompany.name}
            onChange={handleInputChange}
            placeholder="Enter company name"
            required
            className="company-input"
          />
          <button type="submit" className="create-company-btn">Create Company</button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>
      <div className="companies-card">
        <h2 className="section-title">Your Companies</h2>
        <table className="companies-table">
          <thead>
            <tr>
              <th>NAME</th>
              <th>CREATED</th>
              <th>MONDAY.COM</th>
              <th>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {companies.map((company) => (
              <tr key={company.id}>
                <td>{company.name}</td>
                <td>{company.created_at ? new Date(company.created_at).toLocaleDateString() : ''}</td>
                <td>
                  {company.monday_connected ? (
                    <span className="monday-status connected">Connected</span>
                  ) : (
                    <span className="monday-status disconnected">Not Connected</span>
                  )}
                </td>
                <td>
                  <a href={`/companies/${company.id}/stats`} className="view-stats-link">View Stats</a>
                  <button 
                    onClick={() => openMondayModal(company)} 
                    className="monday-connect-btn"
                  >
                    {company.monday_connected ? 'Reconnect' : 'Connect'} Monday.com
                  </button>
                  <button
                    onClick={() => {/* Future: refresh company action */}}
                    className="icon-btn"
                    title="Refresh Company"
                    disabled
                    style={{ marginRight: 8 }}
                  >
                    <FaSyncAlt />
                  </button>
                  <button
                    onClick={() => handleDelete(company.id)}
                    className="icon-btn delete"
                    title="Delete Company"
                  >
                    <FaTrash />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Monday.com Connection Modal */}
      {showMondayModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Connect {selectedCompany?.name} to Monday.com</h2>
              <button onClick={closeMondayModal} className="modal-close">×</button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="api-token">Monday.com API Token</label>
                <input
                  type="password"
                  id="api-token"
                  name="apiToken"
                  value={mondayConfig.apiToken}
                  onChange={handleMondayConfigChange}
                  placeholder="Enter your Monday.com API token"
                  className="form-input"
                />
                <small>
                  <a href="https://monday.com/developers/v2/tutorials/getting-started-with-the-api" target="_blank" rel="noopener noreferrer">
                    How to get your API token?
                  </a>
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="workspace">Workspace</label>
                <select
                  id="workspace"
                  name="workspaceId"
                  value={mondayConfig.workspaceId}
                  onChange={handleMondayConfigChange}
                  className="form-select"
                  disabled={!mondayConfig.apiToken || loading}
                >
                  <option value="">Select a workspace</option>
                  {mondayWorkspaces.map((workspace) => (
                    <option key={workspace.id} value={workspace.id}>
                      {workspace.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="board">Board</label>
                <select
                  id="board"
                  name="boardId"
                  value={mondayConfig.boardId}
                  onChange={handleMondayConfigChange}
                  className="form-select"
                  disabled={!mondayConfig.workspaceId || loading}
                >
                  <option value="">Select a board</option>
                  {mondayBoards.map((board) => (
                    <option key={board.id} value={board.id}>
                      {board.name}
                    </option>
                  ))}
                </select>
              </div>

              {mondayColumns.length > 0 && (
                <>
                  <div className="form-group">
                    <label htmlFor="views-column">Views Column</label>
                    <select
                      id="views-column"
                      name="views"
                      value={columnMapping.views}
                      onChange={handleColumnMappingChange}
                      className="form-select"
                    >
                      <option value="">Select column for views</option>
                      {mondayColumns.map(col => (
                        <option key={col.id} value={col.id}>{col.title} ({col.type})</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="likes-column">Likes Column</label>
                    <select
                      id="likes-column"
                      name="likes"
                      value={columnMapping.likes}
                      onChange={handleColumnMappingChange}
                      className="form-select"
                    >
                      <option value="">Select column for likes</option>
                      {mondayColumns.map(col => (
                        <option key={col.id} value={col.id}>{col.title} ({col.type})</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="comments-column">Comments Column</label>
                    <select
                      id="comments-column"
                      name="comments"
                      value={columnMapping.comments}
                      onChange={handleColumnMappingChange}
                      className="form-select"
                    >
                      <option value="">Select column for comments</option>
                      {mondayColumns.map(col => (
                        <option key={col.id} value={col.id}>{col.title} ({col.type})</option>
                      ))}
                    </select>
                  </div>
                </>
              )}
            </div>

            <div className="modal-footer">
              <button onClick={closeMondayModal} className="btn-secondary">
                Cancel
              </button>
              <button 
                onClick={connectMonday} 
                className="btn-primary"
                disabled={!mondayConfig.apiToken || !mondayConfig.workspaceId || !mondayConfig.boardId || !columnMapping.views || !columnMapping.likes || !columnMapping.comments || loading}
              >
                {loading ? 'Connecting...' : 'Connect Monday.com'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 