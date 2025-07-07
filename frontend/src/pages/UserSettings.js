import React, { useEffect, useState, useRef } from 'react';
import './UserSettings.css';

const API_BASE = 'http://localhost:8000';

const defaultProfile = {
  display_name: '',
  bio: '',
  timezone: 'UTC',
  profile_picture: '',
  email: '',
  username: '',
  email_verified: false,
  created_at: '',
  last_login: '',
};

const TABS = [
  { key: 'profile', label: 'Profile', icon: <span className="tab-icon">👤</span> },
  { key: 'security', label: 'Security', icon: <span className="tab-icon">🔒</span> },
  { key: 'account', label: 'Account', icon: <span className="tab-icon">⚙️</span> },
];

export default function UserSettings() {
  const [profile, setProfile] = useState(defaultProfile);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('profile');
  const [form, setForm] = useState({ display_name: '', bio: '', timezone: 'UTC' });
  const [timezones, setTimezones] = useState([]);
  const [profilePicFile, setProfilePicFile] = useState(null);
  const [profilePicPreview, setProfilePicPreview] = useState('');
  const [passwords, setPasswords] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [deleteConfirm, setDeleteConfirm] = useState('');
  const [deletePassword, setDeletePassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const fileInputRef = useRef();

  const getToken = () => localStorage.getItem('access_token');

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/user/profile`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
      .then(res => res.json())
      .then(data => {
        setProfile(data);
        setForm({
          display_name: data.display_name || '',
          bio: data.bio || '',
          timezone: data.timezone || 'UTC',
        });
        setProfilePicPreview(data.profile_picture || '');
        setLoading(false);
      })
      .catch(() => setLoading(false));
    fetch(`${API_BASE}/api/user/timezones`)
      .then(res => res.json())
      .then(data => setTimezones(data.timezones))
      .catch(() => {});
  }, []);

  // Profile form change
  const handleFormChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  // Save profile
  const handleProfileSave = async e => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage('');
    setError('');
    try {
      const response = await fetch(`${API_BASE}/api/user/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify(form),
      });
      if (!response.ok) throw new Error((await response.json()).detail || 'Failed to update profile');
      const data = await response.json();
      setProfile(data);
      setMessage('Profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Profile picture upload
  const handleProfilePicChange = e => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) return setError('Profile picture must be less than 5MB');
      if (!file.type.startsWith('image/')) return setError('Please select a valid image file');
      setProfilePicFile(file);
      const reader = new FileReader();
      reader.onload = ev => setProfilePicPreview(ev.target.result);
      reader.readAsDataURL(file);
      setError('');
    }
  };
  const handleProfilePicUpload = async e => {
    e.preventDefault();
    if (!profilePicFile) return;
    setIsSubmitting(true);
    setMessage('');
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', profilePicFile);
      const response = await fetch(`${API_BASE}/api/user/profile/picture`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: formData,
      });
      if (!response.ok) throw new Error((await response.json()).detail || 'Failed to upload profile picture');
      const data = await response.json();
      setProfile({ ...profile, profile_picture: data.profile_picture_url });
      setProfilePicPreview(data.profile_picture_url);
      setProfilePicFile(null);
      setMessage('Profile picture updated successfully!');
      if (fileInputRef.current) fileInputRef.current.value = '';
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Password change
  const handlePasswordChange = async e => {
    e.preventDefault();
    if (passwords.new_password !== passwords.confirm_password) return setError('New passwords do not match');
    if (passwords.new_password.length < 8) return setError('New password must be at least 8 characters long');
    setIsSubmitting(true);
    setMessage('');
    setError('');
    try {
      const response = await fetch(`${API_BASE}/api/user/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({
          current_password: passwords.current_password,
          new_password: passwords.new_password
        }),
      });
      if (!response.ok) throw new Error((await response.json()).detail || 'Failed to change password');
      setMessage('Password changed successfully!');
      setPasswords({ current_password: '', new_password: '', confirm_password: '' });
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Account deletion
  const handleDeleteAccount = async e => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage('');
    setError('');
    try {
      const response = await fetch(`${API_BASE}/api/user/delete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({
          password: deletePassword,
          confirm: deleteConfirm,
        }),
      });
      if (!response.ok) throw new Error((await response.json()).detail || 'Failed to delete account');
      setMessage('Account deleted. Logging out...');
      setTimeout(() => {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
      setShowDeleteModal(false);
    }
  };

  // Tab content renderers
  const renderProfileTab = () => (
    <form className="settings-form" onSubmit={handleProfileSave} autoComplete="off">
      <div className="profile-picture-section">
        <div className="current-picture">
          {profilePicPreview ? (
            <img src={profilePicPreview} alt="Profile" />
          ) : (
            <div className="picture-placeholder">{profile.display_name?.charAt(0) || profile.username?.charAt(0) || 'U'}</div>
          )}
          <label className="avatar-upload-btn" title="Upload new picture">
            <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleProfilePicChange} ref={fileInputRef} />
            <span role="img" aria-label="Upload">📷</span>
          </label>
        </div>
        {profilePicFile && (
          <div className="picture-actions">
            <button className="btn btn-secondary" onClick={handleProfilePicUpload} disabled={isSubmitting}>
              {isSubmitting ? <span className="spinner-small" /> : 'Save Picture'}
            </button>
            <button className="btn btn-danger" onClick={() => { setProfilePicFile(null); setProfilePicPreview(profile.profile_picture || ''); }} disabled={isSubmitting}>Cancel</button>
          </div>
        )}
      </div>
      <div className="form-group">
        <label htmlFor="display_name">Display Name</label>
        <input className="form-input" id="display_name" name="display_name" value={form.display_name} onChange={handleFormChange} maxLength={32} autoComplete="off" />
      </div>
      <div className="form-group">
        <label htmlFor="bio">Bio</label>
        <textarea className="form-textarea" id="bio" name="bio" value={form.bio} onChange={handleFormChange} maxLength={500} placeholder="Tell us about yourself..." />
        <small>{form.bio.length}/500 characters</small>
      </div>
      <div className="form-group">
        <label htmlFor="timezone">Timezone</label>
        <select className="form-input" id="timezone" name="timezone" value={form.timezone} onChange={handleFormChange}>
          {timezones.map(tz => <option key={tz.value} value={tz.value}>{tz.label}</option>)}
        </select>
      </div>
      <div className="form-actions">
        <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? <span className="spinner-small" /> : 'Save Changes'}
        </button>
      </div>
    </form>
  );

  const renderSecurityTab = () => (
    <form className="settings-form" onSubmit={handlePasswordChange} autoComplete="off">
      <div className="form-group">
        <label htmlFor="current_password">Current Password</label>
        <input className="form-input" id="current_password" name="current_password" type={showPassword ? 'text' : 'password'} value={passwords.current_password} onChange={e => setPasswords({ ...passwords, current_password: e.target.value })} autoComplete="current-password" />
      </div>
      <div className="form-group">
        <label htmlFor="new_password">New Password</label>
        <input className="form-input" id="new_password" name="new_password" type={showPassword ? 'text' : 'password'} value={passwords.new_password} onChange={e => setPasswords({ ...passwords, new_password: e.target.value })} autoComplete="new-password" />
      </div>
      <div className="form-group">
        <label htmlFor="confirm_password">Confirm New Password</label>
        <input className="form-input" id="confirm_password" name="confirm_password" type={showPassword ? 'text' : 'password'} value={passwords.confirm_password} onChange={e => setPasswords({ ...passwords, confirm_password: e.target.value })} autoComplete="new-password" />
      </div>
      <div className="form-group">
        <label>
          <input type="checkbox" checked={showPassword} onChange={e => setShowPassword(e.target.checked)} /> Show Passwords
        </label>
      </div>
      <div className="form-actions">
        <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? <span className="spinner-small" /> : 'Change Password'}
        </button>
      </div>
    </form>
  );

  const renderAccountTab = () => (
    <div className="danger-zone">
      <div className="danger-content">
        <div className="danger-info">
          <h4>Delete Account</h4>
          <p>This action is irreversible. All your data will be permanently deleted.</p>
        </div>
        <button className="btn btn-danger" onClick={() => setShowDeleteModal(true)}>
          Delete Account
        </button>
      </div>
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Confirm Account Deletion</h3>
              <button className="modal-close" onClick={() => setShowDeleteModal(false)}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="warning-message">
                <span className="warning-icon">⚠️</span>
                <p>This action cannot be undone. Please type <b>DELETE</b> and enter your password to confirm.</p>
              </div>
              <form onSubmit={handleDeleteAccount} autoComplete="off">
                <div className="form-group">
                  <label htmlFor="deleteConfirm">Type DELETE to confirm</label>
                  <input className="form-input" id="deleteConfirm" name="deleteConfirm" value={deleteConfirm} onChange={e => setDeleteConfirm(e.target.value)} autoComplete="off" />
                </div>
                <div className="form-group">
                  <label htmlFor="deletePassword">Password</label>
                  <input className="form-input" id="deletePassword" name="deletePassword" type="password" value={deletePassword} onChange={e => setDeletePassword(e.target.value)} autoComplete="current-password" />
                </div>
                <div className="modal-actions">
                  <button className="btn btn-danger" type="submit" disabled={isSubmitting || deleteConfirm !== 'DELETE' || !deletePassword}>
                    {isSubmitting ? <span className="spinner-small" /> : 'Delete Account'}
                  </button>
                  <button className="btn btn-secondary" type="button" onClick={() => setShowDeleteModal(false)} disabled={isSubmitting}>Cancel</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="user-settings-outer">
      {loading ? (
        <div className="loading-spinner"><span className="spinner" /> Loading...</div>
      ) : (
        <div className="user-settings-main">
          {/* Profile Card */}
          <div className="profile-card">
            <div className="profile-avatar-large">
              {profile.profile_picture ? (
                <img src={profile.profile_picture} alt="Profile" />
              ) : (
                <div className="avatar-placeholder">{profile.display_name?.charAt(0) || profile.username?.charAt(0) || 'U'}</div>
              )}
              <label className="avatar-upload-btn" title="Upload new picture">
                <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleProfilePicChange} ref={fileInputRef} />
                <span role="img" aria-label="Upload">📷</span>
              </label>
            </div>
            <div className="profile-info">
              <div className="profile-name">{profile.display_name || profile.username}</div>
              <div className="profile-email">{profile.email}</div>
              <div className="profile-stats">
                <div className="stat">Member since: {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : '-'}</div>
              </div>
            </div>
          </div>

          {/* Main Content: Tabs and Forms */}
          <div className="user-settings-content">
            {/* Tab Navigation */}
            <nav className="settings-navigation">
              <div className="tab-container">
                {TABS.map(tab => (
                  <button
                    key={tab.key}
                    className={`tab-button${activeTab === tab.key ? ' active' : ''}`}
                    onClick={() => setActiveTab(tab.key)}
                    type="button"
                  >
                    {tab.icon}
                    <span className="tab-label">{tab.label}</span>
                  </button>
                ))}
              </div>
            </nav>

            {/* Feedback Messages */}
            {message && <div className="success-message message"><span className="message-icon">✔️</span> {message}</div>}
            {error && <div className="error-message message"><span className="message-icon">❌</span> {error}</div>}

            {/* Tab Content */}
            <div className="settings-content">
              <div className="tab-content">
                {activeTab === 'profile' && renderProfileTab()}
                {activeTab === 'security' && renderSecurityTab()}
                {activeTab === 'account' && renderAccountTab()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 