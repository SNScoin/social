import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiCalendar, FiTrendingUp, FiBarChart2, FiUsers, FiEye, FiHeart, FiMessageCircle, FiDownload, FiRefreshCw } from 'react-icons/fi';
import './Reports.css';

export default function Reports() {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [activeReport, setActiveReport] = useState('platform');
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState({});
  const [error, setError] = useState('');

  // Set default dates (last 30 days)
  useEffect(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    
    setEndDate(end.toISOString().split('T')[0]);
    setStartDate(start.toISOString().split('T')[0]);
  }, []);

  // Fetch companies on component mount
  useEffect(() => {
    fetchCompanies();
  }, []);

  // Fetch companies
  const fetchCompanies = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Not authenticated');
        return;
      }

      const response = await axios.get('http://localhost:8000/api/companies/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setCompanies(response.data);
      if (response.data.length > 0) {
        setSelectedCompany(response.data[0].id);
      }
    } catch (err) {
      console.error('Error fetching companies:', err);
      setError('Failed to fetch companies');
      toast.error('Failed to load companies');
    }
  };

  // Generate report
  const generateReport = async () => {
    if (!selectedCompany || !startDate || !endDate) {
      toast.error('Please select a company and date range');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const endpoints = {
        platform: 'http://localhost:8000/api/reports/platform-performance',
        engagement: 'http://localhost:8000/api/reports/engagement-analysis',
        growth: 'http://localhost:8000/api/reports/growth-trends'
      };

      const response = await axios.get(endpoints[activeReport], {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          company_id: selectedCompany,
          start_date: startDate,
          end_date: endDate
        }
      });

      setReportData(prev => ({
        ...prev,
        [activeReport]: response.data
      }));

      toast.success('Report generated successfully!');
    } catch (err) {
      console.error('Error generating report:', err);
      setError('Failed to generate report');
      toast.error('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  // Export report as CSV
  const exportReport = () => {
    const data = reportData[activeReport];
    if (!data) {
      toast.error('No data to export');
      return;
    }

    let csvContent = '';
    
    if (activeReport === 'platform') {
      csvContent = 'Platform,Views,Likes,Comments,Count,Avg Views,Avg Likes,Avg Comments\n';
      Object.entries(data).forEach(([platform, stats]) => {
        csvContent += `${platform},${stats.views},${stats.likes},${stats.comments},${stats.count},${stats.avg_views},${stats.avg_likes},${stats.avg_comments}\n`;
      });
    } else if (activeReport === 'engagement') {
      csvContent = 'Metric,Value\n';
      csvContent += `Total Views,${data.total_views}\n`;
      csvContent += `Total Likes,${data.total_likes}\n`;
      csvContent += `Total Comments,${data.total_comments}\n`;
      csvContent += `Total Links,${data.total_links}\n`;
      csvContent += `Engagement Rate,${data.engagement_rate.toFixed(2)}%\n`;
    } else if (activeReport === 'growth') {
      csvContent = 'Metric,Value\n';
      csvContent += `Total Views,${data.total_views}\n`;
      csvContent += `Total Likes,${data.total_likes}\n`;
      csvContent += `Total Comments,${data.total_comments}\n`;
      csvContent += `Total Links,${data.total_links}\n`;
      csvContent += `Growth Rate,${data.growth_rate.toFixed(2)}%\n`;
    }

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeReport}_report_${startDate}_to_${endDate}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success('Report exported successfully!');
  };

  // Format number with commas
  const formatNumber = (num) => {
    return num?.toLocaleString() || '0';
  };

  // Calculate percentage for progress bars
  const calculatePercentage = (value, max) => {
    if (!max || max === 0) return 0;
    return Math.min((value / max) * 100, 100);
  };

  // Render platform performance report
  const renderPlatformReport = () => {
    const data = reportData.platform;
    if (!data) return null;

    const platforms = Object.keys(data);
    const maxViews = Math.max(...platforms.map(p => data[p].views));
    const maxLikes = Math.max(...platforms.map(p => data[p].likes));
    const maxComments = Math.max(...platforms.map(p => data[p].comments));

    return (
      <div className="report-content">
        <div className="report-summary">
          <div className="summary-card">
            <FiEye className="summary-icon" />
            <div className="summary-content">
              <h3>Total Views</h3>
              <div className="summary-value">
                {formatNumber(platforms.reduce((sum, p) => sum + data[p].views, 0))}
              </div>
            </div>
          </div>
          <div className="summary-card">
            <FiHeart className="summary-icon" />
            <div className="summary-content">
              <h3>Total Likes</h3>
              <div className="summary-value">
                {formatNumber(platforms.reduce((sum, p) => sum + data[p].likes, 0))}
              </div>
            </div>
          </div>
          <div className="summary-card">
            <FiMessageCircle className="summary-icon" />
            <div className="summary-content">
              <h3>Total Comments</h3>
              <div className="summary-value">
                {formatNumber(platforms.reduce((sum, p) => sum + data[p].comments, 0))}
              </div>
            </div>
          </div>
        </div>

        <div className="platform-grid">
          {platforms.map(platform => {
            const stats = data[platform];
            const platformColors = {
              'YouTube': '#FF0000',
              'TikTok': '#000000',
              'Instagram': '#E4405F',
              'Facebook': '#1877F2'
            };

            return (
              <div key={platform} className="platform-card">
                <div className="platform-header" style={{ borderLeftColor: platformColors[platform] }}>
                  <h3>{platform}</h3>
                  <span className="platform-count">{stats.count} links</span>
                </div>
                
                <div className="platform-stats">
                  <div className="stat-row">
                    <span className="stat-label">Views</span>
                    <span className="stat-value">{formatNumber(stats.views)}</span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${calculatePercentage(stats.views, maxViews)}%`,
                          backgroundColor: platformColors[platform]
                        }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="stat-row">
                    <span className="stat-label">Likes</span>
                    <span className="stat-value">{formatNumber(stats.likes)}</span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${calculatePercentage(stats.likes, maxLikes)}%`,
                          backgroundColor: platformColors[platform]
                        }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="stat-row">
                    <span className="stat-label">Comments</span>
                    <span className="stat-value">{formatNumber(stats.comments)}</span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${calculatePercentage(stats.comments, maxComments)}%`,
                          backgroundColor: platformColors[platform]
                        }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="platform-averages">
                  <div className="avg-item">
                    <span className="avg-label">Avg Views</span>
                    <span className="avg-value">{formatNumber(Math.round(stats.avg_views))}</span>
                  </div>
                  <div className="avg-item">
                    <span className="avg-label">Avg Likes</span>
                    <span className="avg-value">{formatNumber(Math.round(stats.avg_likes))}</span>
                  </div>
                  <div className="avg-item">
                    <span className="avg-label">Avg Comments</span>
                    <span className="avg-value">{formatNumber(Math.round(stats.avg_comments))}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Render engagement analysis report
  const renderEngagementReport = () => {
    const data = reportData.engagement;
    if (!data) return null;

    return (
      <div className="report-content">
        <div className="engagement-overview">
          <div className="engagement-card">
            <FiEye className="engagement-icon" />
            <div className="engagement-content">
              <h3>Total Views</h3>
              <div className="engagement-value">{formatNumber(data.total_views)}</div>
            </div>
          </div>
          
          <div className="engagement-card">
            <FiHeart className="engagement-icon" />
            <div className="engagement-content">
              <h3>Total Likes</h3>
              <div className="engagement-value">{formatNumber(data.total_likes)}</div>
            </div>
          </div>
          
          <div className="engagement-card">
            <FiMessageCircle className="engagement-icon" />
            <div className="engagement-content">
              <h3>Total Comments</h3>
              <div className="engagement-value">{formatNumber(data.total_comments)}</div>
            </div>
          </div>
          
          <div className="engagement-card highlight">
            <FiTrendingUp className="engagement-icon" />
            <div className="engagement-content">
              <h3>Engagement Rate</h3>
              <div className="engagement-value">{data.engagement_rate.toFixed(2)}%</div>
            </div>
          </div>
        </div>

        <div className="engagement-breakdown">
          <h3>Engagement Breakdown</h3>
          <div className="breakdown-chart">
            <div className="chart-bar">
              <div className="bar-label">Likes</div>
              <div className="bar-container">
                <div 
                  className="bar-fill likes-bar" 
                  style={{ width: `${calculatePercentage(data.total_likes, data.total_views)}%` }}
                ></div>
              </div>
              <div className="bar-value">{formatNumber(data.total_likes)}</div>
            </div>
            
            <div className="chart-bar">
              <div className="bar-label">Comments</div>
              <div className="bar-container">
                <div 
                  className="bar-fill comments-bar" 
                  style={{ width: `${calculatePercentage(data.total_comments, data.total_views)}%` }}
                ></div>
              </div>
              <div className="bar-value">{formatNumber(data.total_comments)}</div>
            </div>
          </div>
        </div>

        <div className="engagement-insights">
          <h3>Key Insights</h3>
          <div className="insights-grid">
            <div className="insight-card">
              <h4>Content Performance</h4>
              <p>Your content has an engagement rate of <strong>{data.engagement_rate.toFixed(2)}%</strong>, which indicates how well your audience is interacting with your posts.</p>
            </div>
            <div className="insight-card">
              <h4>Audience Interaction</h4>
              <p>For every 100 views, you're getting approximately <strong>{Math.round((data.total_likes + data.total_comments) / data.total_views * 100)}</strong> interactions.</p>
            </div>
            <div className="insight-card">
              <h4>Content Volume</h4>
              <p>You have <strong>{data.total_links}</strong> active links being tracked across all platforms.</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render growth trends report
  const renderGrowthReport = () => {
    const data = reportData.growth;
    if (!data) return null;

    return (
      <div className="report-content">
        <div className="growth-overview">
          <div className="growth-card">
            <FiTrendingUp className="growth-icon" />
            <div className="growth-content">
              <h3>Growth Rate</h3>
              <div className="growth-value">{data.growth_rate.toFixed(2)}%</div>
            </div>
          </div>
          
          <div className="growth-card">
            <FiUsers className="growth-icon" />
            <div className="growth-content">
              <h3>Total Links</h3>
              <div className="growth-value">{formatNumber(data.total_links)}</div>
            </div>
          </div>
          
          <div className="growth-card">
            <FiBarChart2 className="growth-icon" />
            <div className="growth-content">
              <h3>Total Interactions</h3>
              <div className="growth-value">{formatNumber(data.total_views + data.total_likes + data.total_comments)}</div>
            </div>
          </div>
        </div>

        <div className="growth-metrics">
          <h3>Growth Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-header">
                <FiEye className="metric-icon" />
                <span>Views Growth</span>
              </div>
              <div className="metric-value">{formatNumber(data.total_views)}</div>
              <div className="metric-per-link">~{formatNumber(Math.round(data.total_views / data.total_links))} per link</div>
            </div>
            
            <div className="metric-card">
              <div className="metric-header">
                <FiHeart className="metric-icon" />
                <span>Likes Growth</span>
              </div>
              <div className="metric-value">{formatNumber(data.total_likes)}</div>
              <div className="metric-per-link">~{formatNumber(Math.round(data.total_likes / data.total_links))} per link</div>
            </div>
            
            <div className="metric-card">
              <div className="metric-header">
                <FiMessageCircle className="metric-icon" />
                <span>Comments Growth</span>
              </div>
              <div className="metric-value">{formatNumber(data.total_comments)}</div>
              <div className="metric-per-link">~{formatNumber(Math.round(data.total_comments / data.total_links))} per link</div>
            </div>
          </div>
        </div>

        <div className="growth-analysis">
          <h3>Growth Analysis</h3>
          <div className="analysis-content">
            <div className="analysis-item">
              <h4>Performance Overview</h4>
              <p>Your content is showing a growth rate of <strong>{data.growth_rate.toFixed(2)}%</strong>, indicating the overall performance improvement across your social media presence.</p>
            </div>
            <div className="analysis-item">
              <h4>Content Strategy</h4>
              <p>With <strong>{data.total_links}</strong> active links, you're maintaining a diverse content portfolio across multiple platforms.</p>
            </div>
            <div className="analysis-item">
              <h4>Engagement Quality</h4>
              <p>The ratio of interactions to content suggests your audience is actively engaging with your posts, which is crucial for organic growth.</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="reports-bg">
      <div className="reports-header">
        <h1>Reports & Analytics</h1>
        <p>Generate detailed performance reports and insights across your social media platforms</p>
      </div>
      
      <div className="reports-content">
        {/* Report Controls */}
        <div className="report-controls">
          <div className="control-group">
            <label>Company</label>
            <select 
              value={selectedCompany || ''} 
              onChange={(e) => setSelectedCompany(Number(e.target.value))}
              className="control-select"
            >
              <option value="">Select Company</option>
              {companies.map(company => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="control-group">
            <label>Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="control-input"
            />
          </div>
          
          <div className="control-group">
            <label>End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="control-input"
            />
          </div>
          
          <button 
            onClick={generateReport}
            disabled={loading || !selectedCompany || !startDate || !endDate}
            className="generate-btn"
          >
            {loading ? <FiRefreshCw className="spinning" /> : <FiBarChart2 />}
            {loading ? 'Generating...' : 'Generate Report'}
          </button>
        </div>

        {/* Report Type Tabs */}
        <div className="report-tabs">
          <button 
            className={`tab-btn ${activeReport === 'platform' ? 'active' : ''}`}
            onClick={() => setActiveReport('platform')}
          >
            <FiBarChart2 />
            Platform Performance
          </button>
          <button 
            className={`tab-btn ${activeReport === 'engagement' ? 'active' : ''}`}
            onClick={() => setActiveReport('engagement')}
          >
            <FiTrendingUp />
            Engagement Analysis
          </button>
          <button 
            className={`tab-btn ${activeReport === 'growth' ? 'active' : ''}`}
            onClick={() => setActiveReport('growth')}
          >
            <FiUsers />
            Growth Trends
          </button>
        </div>

        {/* Report Content */}
        <div className="report-container">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          {loading && (
            <div className="loading-container">
              <FiRefreshCw className="spinning" />
              <p>Generating report...</p>
            </div>
          )}
          
          {!loading && !error && reportData[activeReport] && (
            <>
              <div className="report-header">
                <h2>
                  {activeReport === 'platform' && 'Platform Performance Report'}
                  {activeReport === 'engagement' && 'Engagement Analysis Report'}
                  {activeReport === 'growth' && 'Growth Trends Report'}
                </h2>
                <button onClick={exportReport} className="export-btn">
                  <FiDownload />
                  Export CSV
                </button>
              </div>
              
              {activeReport === 'platform' && renderPlatformReport()}
              {activeReport === 'engagement' && renderEngagementReport()}
              {activeReport === 'growth' && renderGrowthReport()}
            </>
          )}
          
          {!loading && !error && !reportData[activeReport] && (
            <div className="no-data">
              <FiBarChart2 className="no-data-icon" />
              <h3>No Report Data</h3>
              <p>Select a company and date range, then generate a report to see your analytics.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 