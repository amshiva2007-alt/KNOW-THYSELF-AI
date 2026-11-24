/**
 * Know Thyself AI - Master SPA Controller & Event Bus
 * Team CORE FOUR • wHACKiest 2026 Hackathon
 */

class KnowThyselfApp {
  constructor() {
    this.currentUser = null;
    this.currentView = 'landing';  // 'landing' | 'overview' | 'activity' | 'sleep' | 'heart' | 'screentime' | 'ai' | 'copilot' | 'recommendations' | 'habits' | 'reports' | 'settings' | 'data'
    this.currentRange = 14;
    this.currentOnboardingStep = 1;
    this.onboardingData = {
      name: '',
      age: '',
      gender: '',
      height_cm: '',
      weight_kg: '',
      avg_sleep_hours: 7.5,
      activity_level: 'Moderately Active',
      avg_screen_hours: 6.5,
      goals: ['Better sleep', 'More physical activity'],
      data_preference: 'Demo dataset'
    };

    this.summaryData = null;
    this.timeseriesData = null;
    this.correlationsData = null;
    this.clustersData = null;
    this.recordsData = null;
    this.aiRecommendations = null;
    this.habitsData = null;
    this.notificationsData = [];

    this.pendingCSVFile = null;

    this.init();
  }

  async init() {
    this.bindEvents();
    this.checkInitialAuthState();
  }

  async checkInitialAuthState() {
    const token = KnowThyselfAPI.getToken();
    if (token) {
      try {
        const res = await KnowThyselfAPI.getMe();
        if (res.user) {
          this.currentUser = res.user;
          this.enterDashboard();
          return;
        }
      } catch (e) {
        console.warn('Session expired or invalid, staying on landing.');
      }
    }
    // Default: Show Landing Page
    this.showLandingPage();
  }

  showLandingPage() {
    this.currentView = 'landing';
    document.getElementById('view-landing').style.display = 'block';
    document.getElementById('app-shell').style.display = 'none';
    if (window.lucide) lucide.createIcons();
  }

  async enterDashboard(initialView = 'overview') {
    document.getElementById('view-landing').style.display = 'none';
    document.getElementById('app-shell').style.display = 'flex';
    
    // Update User Avatar and Name
    const name = this.currentUser?.name || 'Alex Morgan';
    const initials = name.split(' ').map(n => n[0]).join('').toUpperCase() || 'AM';
    const avatarEl = document.getElementById('user-avatar-initials');
    const nameEl = document.getElementById('user-display-name');
    if (avatarEl) avatarEl.innerText = initials;
    if (nameEl) nameEl.innerText = name;

    await this.loadAllDashboardData();
    this.switchView(initialView);
    await this.loadNotifications();
  }

  bindEvents() {
    // 1. Landing Page Navigation CTAs
    document.querySelectorAll('[data-action="enter-demo"]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        await this.handleDemoLogin();
      });
    });

    document.querySelectorAll('[data-action="open-login"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.openModal('modal-auth');
      });
    });

    document.querySelectorAll('[data-action="open-onboarding"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.openModal('modal-onboarding');
      });
    });

    // 2. Auth Modal Tabs & Submit
    const authForm = document.getElementById('form-auth');
    if (authForm) {
      authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleAuthSubmit();
      });
    }

    const tabLogin = document.getElementById('tab-auth-login');
    const tabRegister = document.getElementById('tab-auth-register');
    if (tabLogin && tabRegister) {
      tabLogin.addEventListener('click', () => {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        document.getElementById('auth-name-group').style.display = 'none';
        document.getElementById('auth-submit-btn').innerText = 'Sign In';
      });
      tabRegister.addEventListener('click', () => {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        document.getElementById('auth-name-group').style.display = 'block';
        document.getElementById('auth-submit-btn').innerText = 'Create Account';
      });
    }

    // Password Toggle
    document.querySelectorAll('.password-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const input = btn.parentElement.querySelector('input');
        if (input.type === 'password') {
          input.type = 'text';
          btn.innerHTML = '<i data-lucide="eye-off" style="width: 16px; height: 16px;"></i>';
        } else {
          input.type = 'password';
          btn.innerHTML = '<i data-lucide="eye" style="width: 16px; height: 16px;"></i>';
        }
        if (window.lucide) lucide.createIcons();
      });
    });

    // 3. Sidebar Navigation Links
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const viewId = item.getAttribute('data-view');
        if (viewId) this.switchView(viewId);
      });
    });

    // Brand Logo click returns to landing or overview
    const brandBadge = document.querySelector('.brand-badge');
    if (brandBadge) {
      brandBadge.addEventListener('click', () => {
        this.switchView('overview');
      });
    }

    // 4. Time Range Buttons (7D, 14D, 30D)
    document.querySelectorAll('.range-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentRange = parseInt(btn.getAttribute('data-range'), 10) || 14;
        await this.loadAllDashboardData();
        UIComponents.showToast(`Updated analytics range to last ${this.currentRange} days.`, 'info');
      });
    });

    // 5. Header Quick Actions
    const refreshBtn = document.getElementById('btn-refresh');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', async () => {
        refreshBtn.classList.add('spinning');
        await this.loadAllDashboardData();
        setTimeout(() => refreshBtn.classList.remove('spinning'), 600);
        UIComponents.showToast('Biometric telemetry refreshed.', 'success');
      });
    }

    const notifBtn = document.getElementById('btn-notif-bell');
    const notifDropdown = document.getElementById('notifications-dropdown');
    if (notifBtn && notifDropdown) {
      notifBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        notifDropdown.classList.toggle('active');
      });
      document.addEventListener('click', (e) => {
        if (!notifDropdown.contains(e.target) && e.target !== notifBtn) {
          notifDropdown.classList.remove('active');
        }
      });
    }

    const headerAiBtn = document.getElementById('btn-header-ai');
    if (headerAiBtn) {
      headerAiBtn.addEventListener('click', async () => {
        this.switchView('ai');
        await this.loadAIRecommendations(true);
      });
    }

    const headerLogBtn = document.getElementById('btn-header-log');
    if (headerLogBtn) {
      headerLogBtn.addEventListener('click', () => {
        this.openModal('modal-log-entry');
      });
    }

    // 6. Modal Close Buttons
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.closeAllModals();
      });
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          this.closeAllModals();
        }
      });
    });

    // 7. Manual Entry Form Submission
    const logForm = document.getElementById('form-log-entry');
    if (logForm) {
      logForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleLogSubmit(logForm);
      });
    }

    // 8. Onboarding Wizard Controls
    this.bindOnboardingEvents();

    // 9. CSV Drag and Drop Zone
    this.bindCSVUploadEvents();

    // 10. Copilot Chat Form
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
      chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleChatSubmit();
      });
    }

    document.querySelectorAll('.query-chip').forEach(chip => {
      chip.addEventListener('click', async () => {
        const query = chip.getAttribute('data-query');
        const input = document.getElementById('chat-input');
        if (input) {
          input.value = query;
          await this.handleChatSubmit();
        }
      });
    });

    // 11. PDF Report Download
    const btnDownloadPdf = document.getElementById('btn-download-pdf');
    if (btnDownloadPdf) {
      btnDownloadPdf.addEventListener('click', () => {
        const days = this.currentRange || 7;
        window.location.href = KnowThyselfAPI.getPdfReportUrl(days);
        UIComponents.showToast(`Generating ${days}-Day Wellness Report PDF...`, 'info');
      });
    }

    const btnExportCsv = document.getElementById('btn-export-csv');
    if (btnExportCsv) {
      btnExportCsv.addEventListener('click', () => {
        window.location.href = KnowThyselfAPI.getExportCsvUrl();
        UIComponents.showToast('Downloading complete CSV telemetry...', 'info');
      });
    }

    // 12. Reset Data
    const resetBtn = document.getElementById('btn-reset-data');
    if (resetBtn) {
      resetBtn.addEventListener('click', async () => {
        if (confirm('Reset telemetry to the 30-day realistic sample dataset?')) {
          await KnowThyselfAPI.resetData();
          await this.loadAllDashboardData();
          UIComponents.showToast('Telemetry reset to pristine 30-day sample data.', 'success');
        }
      });
    }

    // 13. Mobile Menu Toggle
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const sidebar = document.querySelector('.app-sidebar');
    if (mobileToggle && sidebar) {
      mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
    }
  }

  // ================= AUTH HANDLERS =================
  async handleDemoLogin() {
    try {
      const res = await KnowThyselfAPI.demoLogin();
      this.currentUser = res.user;
      this.closeAllModals();
      await this.enterDashboard('overview');
      UIComponents.showToast('Welcome to Demo Mode! Evaluator access activated.', 'success');
    } catch (err) {
      console.error(err);
      UIComponents.showToast('Failed to activate demo mode.', 'error');
    }
  }

  async handleAuthSubmit() {
    const isRegister = document.getElementById('tab-auth-register').classList.contains('active');
    const email = document.getElementById('auth-email').value.trim();
    const password = document.getElementById('auth-password').value;
    const name = document.getElementById('auth-name').value.trim();

    try {
      let res;
      if (isRegister) {
        res = await KnowThyselfAPI.register(email, password, name);
        this.currentUser = res.user;
        this.closeAllModals();
        this.openModal('modal-onboarding');
        UIComponents.showToast('Account created! Let’s personalize your baseline.', 'success');
      } else {
        res = await KnowThyselfAPI.login(email, password);
        this.currentUser = res.user;
        this.closeAllModals();
        await this.enterDashboard('overview');
        UIComponents.showToast(`Welcome back, ${res.user.name}!`, 'success');
      }
    } catch (err) {
      UIComponents.showToast(err.message || 'Authentication error', 'error');
    }
  }

  handleLogout() {
    KnowThyselfAPI.logout();
    this.currentUser = null;
    this.showLandingPage();
    UIComponents.showToast('Logged out successfully.', 'info');
  }

  // ================= ONBOARDING WIZARD =================
  bindOnboardingEvents() {
    document.querySelectorAll('.select-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const group = chip.parentElement.getAttribute('data-group');
        if (group === 'goals') {
          chip.classList.toggle('selected');
        } else {
          chip.parentElement.querySelectorAll('.select-chip').forEach(c => c.classList.remove('selected'));
          chip.classList.add('selected');
        }
      });
    });

    document.querySelectorAll('[data-onboard-action]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const action = btn.getAttribute('data-onboard-action');
        if (action === 'next') {
          this.stepOnboarding(1);
        } else if (action === 'prev') {
          this.stepOnboarding(-1);
        } else if (action === 'skip') {
          this.stepOnboarding(1);
        } else if (action === 'finish') {
          await this.completeOnboarding();
        }
      });
    });
  }

  stepOnboarding(delta) {
    this.currentOnboardingStep = Math.max(1, Math.min(5, this.currentOnboardingStep + delta));

    document.querySelectorAll('.progress-step-node').forEach((node, idx) => {
      const stepNum = idx + 1;
      node.classList.toggle('active', stepNum === this.currentOnboardingStep);
      node.classList.toggle('completed', stepNum < this.currentOnboardingStep);
    });

    document.querySelectorAll('.onboarding-step-content').forEach(content => {
      const stepNum = parseInt(content.getAttribute('data-step'), 10);
      content.classList.toggle('active', stepNum === this.currentOnboardingStep);
    });

    const nextBtn = document.querySelector('[data-onboard-action="next"]');
    const finishBtn = document.querySelector('[data-onboard-action="finish"]');
    const skipBtn = document.querySelector('[data-onboard-action="skip"]');
    if (this.currentOnboardingStep === 5) {
      if (nextBtn) nextBtn.style.display = 'none';
      if (skipBtn) skipBtn.style.display = 'none';
      if (finishBtn) finishBtn.style.display = 'inline-flex';
    } else {
      if (nextBtn) nextBtn.style.display = 'inline-flex';
      if (skipBtn) skipBtn.style.display = 'inline-flex';
      if (finishBtn) finishBtn.style.display = 'none';
    }

    if (window.lucide) lucide.createIcons();
  }

  async completeOnboarding() {
    const nameInput = document.getElementById('onboard-name');
    const ageInput = document.getElementById('onboard-age');
    if (nameInput && nameInput.value) this.onboardingData.name = nameInput.value;
    if (ageInput && ageInput.value) this.onboardingData.age = parseInt(ageInput.value, 10);

    try {
      const res = await KnowThyselfAPI.completeOnboarding(this.onboardingData);
      this.currentUser = res.user;
      this.closeAllModals();
      await this.enterDashboard('overview');
      UIComponents.showToast('Onboarding complete! Your intelligence dashboard is ready.', 'success');
    } catch (err) {
      console.error(err);
      this.closeAllModals();
      await this.enterDashboard('overview');
    }
  }

  // ================= VIEW SWITCHER =================
  switchView(viewId) {
    this.currentView = viewId;

    // Update nav active states
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-view') === viewId);
    });

    // Update section active states
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.toggle('active', sec.id === `view-${viewId}`);
    });

    const viewHeadings = {
      overview: { title: 'Executive Overview', sub: 'Holistic Biometric Telemetry & Correlation Index' },
      activity: { title: 'Activity & Movement Analytics', sub: 'Daily Movement, Workouts & Caloric Flux' },
      sleep: { title: 'Sleep Architecture & Recovery', sub: 'Circadian Cycles, Sleep Stages & Sleep Latency' },
      heart: { title: 'Cardiovascular Autonomic Rhythm', sub: 'Heart Rate Variability (HRV) & Resting Pulse' },
      screentime: { title: 'Screen Time & Digital Focus', sub: 'Device Exposure & Late-Night Behavioural Friction' },
      ai: { title: 'Gemini AI Intelligence', sub: 'Personalised Lifestyle Synthesis & Prescriptions' },
      copilot: { title: 'AI Wellness Copilot', sub: 'Interactive Conversational Q&A Grounded in Your Telemetry' },
      recommendations: { title: 'Personalised Recommendations', sub: 'Evidence-Based Habit Prescriptions & Targets' },
      habits: { title: 'Habit Consistency Tracker', sub: 'Daily Checklist, Streaks & 28-Day Consistency Matrix' },
      reports: { title: 'Executive Wellness Reports', sub: 'Downloadable PDF Summaries & CSV Telemetry Exports' },
      settings: { title: 'Platform & Privacy Settings', sub: 'Profile, Goals, Notifications & Data Sovereignty' },
      data: { title: 'Data Management & CSV Ingestion', sub: 'Manual Logging, Drag-and-Drop CSV & Raw Records' }
    };

    const header = viewHeadings[viewId] || viewHeadings.overview;
    const titleEl = document.getElementById('view-title');
    const subEl = document.getElementById('view-subtitle');
    if (titleEl) titleEl.innerText = header.title;
    if (subEl) subEl.innerText = header.sub;

    // Dynamic View Rendering
    if (this.timeseriesData) {
      if (viewId === 'activity') {
        WellnessCharts.renderActivityHeartDynamics('chart-activity-main', this.timeseriesData);
      } else if (viewId === 'sleep') {
        WellnessCharts.renderSleepStages('chart-sleep-stages-main', this.timeseriesData);
      } else if (viewId === 'heart') {
        WellnessCharts.renderActivityHeartDynamics('chart-heart-main', this.timeseriesData);
      } else if (viewId === 'screentime') {
        WellnessCharts.renderScreenTimeBreakdown('chart-screentime-main', this.timeseriesData);
        WellnessCharts.renderScreenSleepCorrelation('chart-screentime-latency-main', this.timeseriesData);
      }
    }

    if (viewId === 'ai' && !this.aiRecommendations) {
      this.loadAIRecommendations();
    }

    if (viewId === 'habits') {
      this.loadHabitsView();
    }

    const sidebar = document.querySelector('.app-sidebar');
    if (sidebar) sidebar.classList.remove('open');

    if (window.lucide) lucide.createIcons();
  }

  // ================= DATA LOADING =================
  async loadAllDashboardData() {
    try {
      const [summary, timeseries, correlations, clusters, records, habits] = await Promise.all([
        KnowThyselfAPI.getSummary(this.currentRange),
        KnowThyselfAPI.getTimeseries(this.currentRange),
        KnowThyselfAPI.getCorrelations(),
        KnowThyselfAPI.getClusters(),
        KnowThyselfAPI.getRecords(30),
        KnowThyselfAPI.getHabits()
      ]);

      this.summaryData = summary;
      this.timeseriesData = timeseries;
      this.correlationsData = correlations;
      this.clustersData = clusters;
      this.recordsData = records.records || [];
      this.habitsData = habits;

      this.renderOverview();
      this.renderDataTableView();
      this.renderHabitsView();

      if (window.lucide) lucide.createIcons();
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    }
  }

  renderOverview() {
    if (!this.summaryData) return;

    // 1. Hero Score
    const scoreVal = this.summaryData.overall_score?.value || 0;
    const scoreStatus = this.summaryData.overall_score?.status || 'Optimal';
    const scoreEl = document.getElementById('hero-score-val');
    const scoreStatusEl = document.getElementById('hero-score-status');
    if (scoreEl) scoreEl.innerText = scoreVal;
    if (scoreStatusEl) scoreStatusEl.innerText = scoreStatus;

    // 2. Overview Metric Tiles
    const act = this.summaryData.activity || {};
    const slp = this.summaryData.sleep || {};
    const hr = this.summaryData.heart_rate || {};
    const scr = this.summaryData.screen_time || {};

    // Activity
    document.getElementById('metric-steps-val').innerText = (act.avg_steps || 0).toLocaleString();
    document.getElementById('metric-steps-delta').innerHTML = UIComponents.renderDeltaBadge(act.change);
    document.getElementById('metric-active-mins').innerText = `${act.avg_active_mins || 0}m`;
    document.getElementById('metric-calories').innerText = `${(act.total_calories || 0).toLocaleString()} kcal`;

    // Sleep
    document.getElementById('metric-sleep-val').innerText = slp.avg_hours || 0;
    document.getElementById('metric-sleep-delta').innerHTML = UIComponents.renderDeltaBadge(slp.change, 'h');
    document.getElementById('metric-sleep-deep').innerText = `${slp.avg_deep_hours || 0}h`;
    document.getElementById('metric-sleep-eff').innerText = `${slp.avg_efficiency || 0}%`;

    // Heart Rate
    document.getElementById('metric-hr-val').innerText = hr.avg_resting_bpm || 0;
    document.getElementById('metric-hr-delta').innerHTML = UIComponents.renderDeltaBadge(hr.change, ' bpm', true);
    document.getElementById('metric-hrv').innerText = `${hr.avg_hrv_ms || 0} ms`;

    // Screen Time
    document.getElementById('metric-screen-val').innerText = scr.avg_hours || 0;
    document.getElementById('metric-screen-delta').innerHTML = UIComponents.renderDeltaBadge(scr.change, 'h', true);
    document.getElementById('metric-late-screen').innerText = `${scr.avg_late_screen_mins || 0}m`;

    // 3. Render Charts
    if (this.timeseriesData) {
      WellnessCharts.renderOverviewTrajectory('chart-overview-trajectory', this.timeseriesData);
      WellnessCharts.renderScreenSleepCorrelation('chart-screen-latency-overview', this.timeseriesData);
    }

    // 4. Correlations & Findings
    const corrContainer = document.getElementById('overview-correlations-container');
    if (corrContainer && this.correlationsData) {
      corrContainer.innerHTML = UIComponents.renderCorrelationCards(this.correlationsData.findings);
    }

    // 5. Clusters Archetypes
    const clusterContainer = document.getElementById('overview-clusters-container');
    if (clusterContainer && this.clustersData) {
      clusterContainer.innerHTML = UIComponents.renderClusters(this.clustersData.clusters);
    }
  }

  renderDataTableView() {
    const tableBody = document.getElementById('data-table-body');
    if (tableBody && this.recordsData) {
      tableBody.innerHTML = UIComponents.renderDataTable(this.recordsData);
    }
  }

  renderHabitsView() {
    if (!this.habitsData) return;
    const checklistEl = document.getElementById('habits-checklist-container');
    const heatmapEl = document.getElementById('habits-heatmap-container');
    const pctEl = document.getElementById('habits-completion-pct');

    if (checklistEl) checklistEl.innerHTML = UIComponents.renderHabitsList(this.habitsData.habits);
    if (heatmapEl) heatmapEl.innerHTML = UIComponents.renderHeatmap(this.habitsData.heatmap);
    if (pctEl) pctEl.innerText = `${this.habitsData.completion_percentage}%`;
    if (window.lucide) lucide.createIcons();
  }

  async loadHabitsView() {
    try {
      this.habitsData = await KnowThyselfAPI.getHabits();
      this.renderHabitsView();
    } catch (e) {
      console.warn('Could not reload habits:', e);
    }
  }

  async toggleHabit(habitId) {
    try {
      await KnowThyselfAPI.toggleHabit(habitId);
      await this.loadHabitsView();
      UIComponents.showToast('Habit status updated.', 'success');
    } catch (e) {
      console.error(e);
      UIComponents.showToast('Failed to toggle habit', 'error');
    }
  }

  async loadNotifications() {
    try {
      const res = await KnowThyselfAPI.getNotifications();
      this.notificationsData = res.notifications || [];
      const listEl = document.getElementById('notifications-list-container');
      const badgeEl = document.getElementById('notif-unread-badge');

      if (listEl) listEl.innerHTML = UIComponents.renderNotificationsList(this.notificationsData);
      if (badgeEl) {
        badgeEl.innerText = res.unread_count || 0;
        badgeEl.style.display = res.unread_count > 0 ? 'flex' : 'none';
      }
      if (window.lucide) lucide.createIcons();
    } catch (e) {
      console.warn('Could not load notifications:', e);
    }
  }

  async loadAIRecommendations(forceRefresh = false) {
    const container = document.getElementById('ai-recommendations-container');
    const recsPageContainer = document.getElementById('recommendations-page-container');
    if (!container && !recsPageContainer) return;

    if (!forceRefresh && this.aiRecommendations) {
      const html = UIComponents.renderAIRecommendations(this.aiRecommendations);
      if (container) container.innerHTML = html;
      if (recsPageContainer) recsPageContainer.innerHTML = html;
      if (window.lucide) lucide.createIcons();
      return;
    }

    const loaderHtml = `
      <div style="text-align: center; padding: 48px;">
        <div class="card-icon violet spinning" style="margin: 0 auto 16px; width: 48px; height: 48px;">
          <i data-lucide="loader" style="width: 28px; height: 28px;"></i>
        </div>
        <p style="color: var(--text-primary); font-size: 1rem; font-weight: 600;">Synthesizing Wellness Intelligence...</p>
        <p style="color: var(--text-muted); font-size: 0.85rem;">Cross-referencing circadian markers, HRV elasticity & screen friction</p>
      </div>
    `;
    if (container) container.innerHTML = loaderHtml;
    if (recsPageContainer) recsPageContainer.innerHTML = loaderHtml;
    if (window.lucide) lucide.createIcons();

    try {
      const recs = await KnowThyselfAPI.getAIRecommendations();
      this.aiRecommendations = recs;
      const html = UIComponents.renderAIRecommendations(recs);
      if (container) container.innerHTML = html;
      if (recsPageContainer) recsPageContainer.innerHTML = html;
      if (window.lucide) lucide.createIcons();
      UIComponents.showToast('Personalised recommendations generated.', 'success');
    } catch (err) {
      console.error(err);
      if (container) container.innerHTML = `<p style="color: var(--rose-primary); padding: 20px;">Failed to generate AI recommendations.</p>`;
    }
  }

  // ================= COPILOT CHAT =================
  async handleChatSubmit() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    const messagesBox = document.getElementById('chat-messages');

    // User Bubble
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user';
    userBubble.innerText = msg;
    messagesBox.appendChild(userBubble);
    input.value = '';
    messagesBox.scrollTop = messagesBox.scrollHeight;

    // Bot Typing
    const botLoading = document.createElement('div');
    botLoading.className = 'chat-bubble bot';
    botLoading.innerHTML = `
      <div style="font-size: 0.72rem; color: var(--teal-primary); font-weight: 700; margin-bottom: 4px;">Know Thyself AI Copilot</div>
      <div>Analyzing your verified telemetry...</div>
    `;
    messagesBox.appendChild(botLoading);
    messagesBox.scrollTop = messagesBox.scrollHeight;

    try {
      const res = await KnowThyselfAPI.sendAIChat(msg);
      botLoading.innerHTML = `
        <div style="font-size: 0.72rem; color: var(--teal-primary); font-weight: 700; margin-bottom: 4px;">${res.source || 'Know Thyself AI'}</div>
        <div>${res.reply}</div>
      `;
    } catch (err) {
      botLoading.innerText = 'Unable to analyze query right now.';
    }
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  // ================= CSV DRAG & DROP =================
  bindCSVUploadEvents() {
    const dropzone = document.getElementById('csv-dropzone');
    const fileInput = document.getElementById('csv-file-input');
    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover'].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', async (e) => {
      if (e.dataTransfer.files.length) {
        await this.handleCSVFileSelected(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', async () => {
      if (fileInput.files.length) {
        await this.handleCSVFileSelected(fileInput.files[0]);
      }
    });

    const confirmBtn = document.getElementById('btn-confirm-csv-import');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', async () => {
        if (!this.pendingCSVFile) return;
        confirmBtn.disabled = true;
        confirmBtn.innerText = 'Importing...';
        try {
          const res = await KnowThyselfAPI.importCSV(this.pendingCSVFile);
          UIComponents.showToast(res.message, 'success');
          document.getElementById('csv-preview-container').style.display = 'none';
          this.pendingCSVFile = null;
          await this.loadAllDashboardData();
        } catch (err) {
          UIComponents.showToast(err.message, 'error');
        } finally {
          confirmBtn.disabled = false;
          confirmBtn.innerText = 'Confirm & Import Telemetry';
        }
      });
    }
  }

  async handleCSVFileSelected(file) {
    if (!file.name.endsWith('.csv')) {
      UIComponents.showToast('Please upload a valid .csv file.', 'error');
      return;
    }

    this.pendingCSVFile = file;
    try {
      const preview = await KnowThyselfAPI.previewCSV(file);
      const container = document.getElementById('csv-preview-container');
      const statsEl = document.getElementById('csv-preview-stats');
      const tableHead = document.getElementById('csv-preview-thead');
      const tableBody = document.getElementById('csv-preview-tbody');

      if (statsEl) {
        statsEl.innerHTML = `
          <div style="display: flex; gap: 16px; margin-bottom: 12px; font-size: 0.85rem;">
            <span>Total Rows: <strong>${preview.total_rows}</strong></span>
            <span>Valid: <strong style="color: var(--teal-primary);">${preview.valid_rows_count}</strong></span>
            <span>Duplicates Detected: <strong style="color: var(--amber-primary);">${preview.duplicate_dates_count}</strong></span>
          </div>
        `;
      }

      if (preview.preview && preview.preview.length) {
        const cols = Object.keys(preview.preview[0]);
        if (tableHead) {
          tableHead.innerHTML = `<tr>${cols.map(c => `<th>${c}</th>`).join('')}</tr>`;
        }
        if (tableBody) {
          tableBody.innerHTML = preview.preview.map(row => `
            <tr>${cols.map(c => `<td>${row[c]}</td>`).join('')}</tr>
          `).join('');
        }
      }

      if (container) container.style.display = 'block';
      UIComponents.showToast(`CSV analyzed: ${preview.valid_rows_count} valid records detected.`, 'info');
    } catch (err) {
      UIComponents.showToast(err.message, 'error');
    }
  }

  // ================= LOG ENTRY & DELETE =================
  async handleLogSubmit(form) {
    const formData = new FormData(form);
    const date = formData.get('date') || new Date().toISOString().split('T')[0];
    const steps = parseInt(formData.get('steps'), 10) || 7500;
    const activeMins = parseInt(formData.get('active_minutes'), 10) || 45;
    const sleepHours = parseFloat(formData.get('sleep_hours')) || 7.2;
    const latency = parseInt(formData.get('latency'), 10) || 20;
    const restingHr = parseInt(formData.get('resting_hr'), 10) || 62;
    const hrv = parseInt(formData.get('hrv'), 10) || 60;
    const screenHours = parseFloat(formData.get('screen_hours')) || 6.5;
    const lateScreen = parseInt(formData.get('late_screen'), 10) || 40;

    const record = {
      id: `day-${date}`,
      date: date,
      timestamp: `${date}T23:59:59Z`,
      activity: {
        steps: steps,
        active_minutes: activeMins,
        distance_km: parseFloat((steps * 0.00078).toFixed(2)),
        calories_burned: 1800 + Math.round(steps * 0.05),
        workout_type: formData.get('workout') || 'General Activity'
      },
      sleep: {
        total_sleep_hours: sleepHours,
        deep_sleep_hours: parseFloat((sleepHours * 0.2).toFixed(2)),
        rem_sleep_hours: parseFloat((sleepHours * 0.22).toFixed(2)),
        light_sleep_hours: parseFloat((sleepHours * 0.58).toFixed(2)),
        efficiency_score: Math.min(98, Math.max(60, 95 - Math.round(latency * 0.3))),
        sleep_latency_minutes: latency
      },
      heart_rate: {
        resting_bpm: restingHr,
        average_bpm: restingHr + 14,
        max_bpm: 140,
        hrv_ms: hrv
      },
      screen_time: {
        total_screen_hours: screenHours,
        late_night_screen_minutes: lateScreen,
        productivity_hours: parseFloat((screenHours * 0.5).toFixed(1)),
        entertainment_social_hours: parseFloat((screenHours * 0.5).toFixed(1)),
        pickup_count: Math.round(screenHours * 11)
      },
      wellness_score: Math.min(96, Math.max(45, Math.round((steps / 100) * 0.3 + (sleepHours * 10) * 0.4 + (hrv * 0.3)))),
      tags: [formData.get('workout') || 'Manual Entry']
    };

    try {
      await KnowThyselfAPI.saveRecord(record);
      this.closeAllModals();
      form.reset();
      await this.loadAllDashboardData();
      UIComponents.showToast(`Logged entry for ${date}.`, 'success');
    } catch (err) {
      console.error(err);
      UIComponents.showToast('Failed to save record.', 'error');
    }
  }

  async handleDeleteRecord(id) {
    if (!confirm(`Delete record '${id}'?`)) return;
    try {
      await KnowThyselfAPI.deleteRecord(id);
      await this.loadAllDashboardData();
      UIComponents.showToast('Record deleted.', 'info');
    } catch (e) {
      UIComponents.showToast('Failed to delete record.', 'error');
    }
  }

  // ================= MODAL HELPERS =================
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      const dateInput = modal.querySelector('input[name="date"]');
      if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
      }
    }
    if (window.lucide) lucide.createIcons();
  }

  closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.app = new KnowThyselfApp();
});
