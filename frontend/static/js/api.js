/**
 * Know Thyself AI - Complete REST API Client
 * Team CORE FOUR • wHACKiest 2026 Hackathon
 */

const KnowThyselfAPI = {
  baseUrl: '',

  getToken() {
    return localStorage.getItem('knowthyself_token') || '';
  },

  setToken(token) {
    if (token) {
      localStorage.setItem('knowthyself_token', token);
    } else {
      localStorage.removeItem('knowthyself_token');
    }
  },

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth & Profile
  async register(email, password, name) {
    const res = await this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name })
    });
    if (res.token) this.setToken(res.token);
    return res;
  },

  async login(email, password) {
    const res = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (res.token) this.setToken(res.token);
    return res;
  },

  async demoLogin() {
    const res = await this.request('/api/auth/demo', { method: 'POST' });
    if (res.token) this.setToken(res.token);
    return res;
  },

  async getMe() {
    return this.request('/api/auth/me');
  },

  logout() {
    this.setToken(null);
  },

  getProfile() {
    return this.request('/api/user/profile');
  },

  updateProfile(profileData) {
    return this.request('/api/user/profile', {
      method: 'POST',
      body: JSON.stringify(profileData)
    });
  },

  completeOnboarding(onboardingData) {
    return this.request('/api/user/onboarding', {
      method: 'POST',
      body: JSON.stringify(onboardingData)
    });
  },

  getPreferences() {
    return this.request('/api/user/preferences');
  },

  updatePreferences(prefs) {
    return this.request('/api/user/preferences', {
      method: 'POST',
      body: JSON.stringify(prefs)
    });
  },

  // Telemetry & Records
  getHealth() {
    return this.request('/api/health');
  },

  getSummary(days = 7) {
    return this.request(`/api/analytics/dashboard?days=${days}`);
  },

  getTimeseries(days = 14) {
    return this.request(`/api/analytics/timeseries?days=${days}`);
  },

  getCorrelations() {
    return this.request('/api/analytics/correlations');
  },

  getClusters() {
    return this.request('/api/analytics/clusters');
  },

  getAnomalies() {
    return this.request('/api/analytics/anomalies');
  },

  getRecords(limit = 30) {
    return this.request(`/api/wellness/records?limit=${limit}`);
  },

  saveRecord(recordData) {
    return this.request('/api/wellness/add', {
      method: 'POST',
      body: JSON.stringify(recordData)
    });
  },

  deleteRecord(id) {
    return this.request('/api/wellness/delete', {
      method: 'POST',
      body: JSON.stringify({ id })
    });
  },

  resetData() {
    return this.request('/api/wellness/reset', { method: 'POST' });
  },

  // CSV Processing
  async previewCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    const token = this.getToken();
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

    const resp = await fetch('/api/upload/preview', {
      method: 'POST',
      headers,
      body: formData
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to preview CSV');
    }
    return await resp.json();
  },

  async importCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    const token = this.getToken();
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

    const resp = await fetch('/api/upload/csv', {
      method: 'POST',
      headers,
      body: formData
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to import CSV');
    }
    return await resp.json();
  },

  getSampleCSVUrl() {
    return '/api/upload/sample-csv';
  },

  // Habits & Notifications
  getHabits(date) {
    const query = date ? `?date=${date}` : '';
    return this.request(`/api/habits${query}`);
  },

  toggleHabit(habitId, date) {
    return this.request('/api/habits/toggle', {
      method: 'POST',
      body: JSON.stringify({ habit_id: habitId, date })
    });
  },

  getNotifications() {
    return this.request('/api/notifications');
  },

  // AI & Copilot
  getAIRecommendations() {
    return this.request('/api/insights/recommendations');
  },

  getDailyInsight() {
    return this.request('/api/insights/daily');
  },

  sendAIChat(message) {
    return this.request('/api/insights/chat', {
      method: 'POST',
      body: JSON.stringify({ message })
    });
  },

  // Reports
  getPdfReportUrl(days = 7) {
    return `/api/reports/pdf?days=${days}`;
  },

  getExportCsvUrl() {
    return '/api/reports/export';
  }
};
