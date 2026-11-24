/**
 * Know Thyself AI - UI Components & Template Renderers
 * Generates modular components for habits, notifications, insights & tables.
 */

const UIComponents = {
  renderDeltaBadge(val, suffix = '', invert = false) {
    if (val === 0 || val === undefined || isNaN(val)) {
      return `<span class="metric-delta neutral">0${suffix}</span>`;
    }
    const isPositive = val > 0;
    const isGood = invert ? !isPositive : isPositive;
    const sign = isPositive ? '+' : '';
    const badgeClass = isGood ? 'positive' : 'negative';
    const arrow = isPositive ? '↑' : '↓';
    return `<span class="metric-delta ${badgeClass}">${arrow} ${sign}${val}${suffix}</span>`;
  },

  renderCorrelationCards(findings = []) {
    if (!findings.length) {
      return `<p class="card-subtitle">Telemetry baseline active. No significant anomalous correlations detected.</p>`;
    }
    return findings.map(f => {
      const isNegative = f.type === 'negative_impact';
      const cardType = isNegative ? 'warning' : 'accent';
      const tagLabel = isNegative ? 'Behavioural Risk' : 'Performance Catalyst';
      return `
        <div class="card insight-card ${cardType}">
          <div class="insight-tag">${tagLabel}</div>
          <div class="insight-title">${f.metric_pair}</div>
          <div class="insight-body">${f.summary}</div>
          <div class="insight-metric-tag">Pearson r: ${f.coefficient} • Verified Telemetry</div>
        </div>
      `;
    }).join('');
  },

  renderClusters(clusters = []) {
    if (!clusters.length) return '';
    return clusters.map(c => `
      <div class="cluster-pill" style="border-color: rgba(244, 247, 251, 0.12); padding: 8px 14px; background: rgba(244, 247, 251, 0.04); border-radius: 12px;">
        <span class="status-dot" style="background-color: var(--${c.color === 'teal' ? 'teal-primary' : c.color === 'violet' ? 'violet-primary' : 'text-muted'})"></span>
        <strong style="color: var(--text-primary); font-size: 0.85rem;">${c.name}</strong> 
        <span style="color: var(--text-muted); font-size: 0.78rem;">(${c.percentage}% of days)</span>
      </div>
    `).join('');
  },

  renderHabitsList(habits = []) {
    if (!habits.length) return `<p style="color: var(--text-muted); padding: 10px;">No habits configured.</p>`;
    return habits.map(h => `
      <div class="habit-row-item ${h.is_completed_today ? 'completed' : ''}" id="row-${h.id}">
        <div class="habit-row-left" onclick="app.toggleHabit('${h.id}')">
          <div class="habit-check-box">
            <i data-lucide="check" style="width: 14px; height: 14px; stroke-width: 3;"></i>
          </div>
          <div>
            <div style="font-weight: 600; font-size: 0.92rem; color: var(--text-primary); text-decoration: ${h.is_completed_today ? 'line-through' : 'none'};">
              ${h.title}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">${h.description}</div>
          </div>
        </div>
        <div class="habit-streak-badge">
          <i data-lucide="flame" style="width: 13px; height: 13px;"></i>
          <span>${h.current_streak_days} Day Streak</span>
        </div>
      </div>
    `).join('');
  },

  renderHeatmap(heatmap = []) {
    if (!heatmap.length) return '';
    return heatmap.map(d => `
      <div class="heatmap-day-cell level-${d.level}" title="${d.date}: ${d.completed}/${d.total} habits (${d.percentage}%)">
        <span>${d.day_name}</span>
        <span style="font-size: 0.65rem; opacity: 0.85;">${d.date.slice(8)}</span>
      </div>
    `).join('');
  },

  renderNotificationsList(notifications = []) {
    if (!notifications.length) {
      return `<div style="padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.85rem;">No notifications right now.</div>`;
    }
    return notifications.map(n => `
      <div class="notif-item ${!n.read ? 'unread' : ''}">
        <div class="card-icon ${n.type === 'activity' ? 'teal' : n.type === 'screen' ? 'violet' : 'amber'}" style="width: 32px; height: 32px; flex-shrink: 0;">
          <i data-lucide="${n.icon || 'bell'}" style="width: 16px; height: 16px;"></i>
        </div>
        <div>
          <div style="font-weight: 600; font-size: 0.85rem; color: var(--text-primary); margin-bottom: 2px;">${n.title}</div>
          <div style="font-size: 0.78rem; color: var(--text-secondary); line-height: 1.4;">${n.message}</div>
          <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 4px;">${n.timestamp}</div>
        </div>
      </div>
    `).join('');
  },

  renderAIRecommendations(recs) {
    if (!recs) return '';

    const sleepP = recs.circadian_sleep_prescription || {};
    const screenP = recs.digital_screen_protocol || {};
    const actP = recs.activity_heart_strategy || {};
    const habits = recs.actionable_habits || [];

    return `
      <div class="card" style="margin-bottom: 24px; border-color: rgba(146, 116, 255, 0.35);">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-icon violet"><i data-lucide="sparkles"></i></div>
            <div>
              <div class="card-title">Executive Wellness Synthesis</div>
              <div class="card-subtitle">${recs.wellness_index_status || 'Telemetry Analysis'}</div>
            </div>
          </div>
          <span class="hero-pill" style="margin: 0; background: var(--violet-dim); color: var(--violet-primary); border-color: rgba(146, 116, 255, 0.4);">
            ${recs.engine_source || 'AI Engine'}
          </span>
        </div>
        <p style="color: var(--text-primary); font-size: 1.05rem; line-height: 1.6;">${recs.executive_summary || ''}</p>
        
        <div class="medical-disclaimer-box">
          <i data-lucide="alert-circle" style="width: 18px; height: 18px; color: var(--violet-primary); flex-shrink: 0;"></i>
          <span><strong>Wellness Awareness Platform:</strong> This analysis highlights behavioural correlations and lifestyle trends. It is not a clinical medical assessment or diagnostic tool.</span>
        </div>
      </div>

      <div class="grid-metrics" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); margin-bottom: 24px;">
        <div class="card" style="display: flex; flex-direction: column;">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-icon teal"><i data-lucide="moon"></i></div>
              <div>
                <strong style="color: var(--text-primary); font-size: 0.95rem;">Circadian Sleep</strong>
                <div style="font-size: 0.78rem; color: var(--text-muted);">${sleepP.headline || ''}</div>
              </div>
            </div>
          </div>
          <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; flex: 1;">${sleepP.recommendation || ''}</p>
          <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border-subtle); font-size: 0.8rem; color: var(--teal-primary); font-weight: 600;">
            🎯 Target: ${sleepP.target_metric || 'Optimal'}
          </div>
        </div>

        <div class="card" style="display: flex; flex-direction: column;">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-icon violet"><i data-lucide="smartphone"></i></div>
              <div>
                <strong style="color: var(--text-primary); font-size: 0.95rem;">Digital Boundary</strong>
                <div style="font-size: 0.78rem; color: var(--text-muted);">${screenP.headline || ''}</div>
              </div>
            </div>
          </div>
          <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; flex: 1;">${screenP.recommendation || ''}</p>
          <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border-subtle); font-size: 0.8rem; color: var(--violet-primary); font-weight: 600;">
            🎯 Target: ${screenP.target_metric || 'Optimal'}
          </div>
        </div>

        <div class="card" style="display: flex; flex-direction: column;">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-icon emerald"><i data-lucide="activity"></i></div>
              <div>
                <strong style="color: var(--text-primary); font-size: 0.95rem;">Cardio & Recovery</strong>
                <div style="font-size: 0.78rem; color: var(--text-muted);">${actP.headline || ''}</div>
              </div>
            </div>
          </div>
          <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; flex: 1;">${actP.recommendation || ''}</p>
          <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border-subtle); font-size: 0.8rem; color: var(--emerald-primary); font-weight: 600;">
            🎯 Target: ${actP.target_metric || 'Optimal'}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-icon teal"><i data-lucide="check-circle-2"></i></div>
            <div>
              <div class="card-title">Actionable Micro-Habits Checklist</div>
              <div class="card-subtitle">Click items to mark completed for today</div>
            </div>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 12px;">
          ${habits.map((habit, idx) => `
            <div class="habit-row-item" onclick="this.classList.toggle('completed')">
              <div class="habit-row-left">
                <div class="habit-check-box"><i data-lucide="check" style="width: 14px; height: 14px;"></i></div>
                <span style="font-size: 0.9rem; color: var(--text-primary);">${habit}</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  renderDataTable(records = []) {
    if (!records.length) {
      return `<tr><td colspan="8" style="text-align: center; padding: 24px; color: var(--text-muted);">No telemetry records logged yet.</td></tr>`;
    }
    return records.slice(-15).reverse().map(r => {
      const act = r.activity || {};
      const slp = r.sleep || {};
      const hr = r.heart_rate || {};
      const scr = r.screen_time || {};
      return `
        <tr>
          <td><strong>${r.date}</strong></td>
          <td><span style="color: var(--teal-primary); font-weight: 700;">${r.wellness_score}/100</span></td>
          <td>${(act.steps || 0).toLocaleString()} steps</td>
          <td>${slp.total_sleep_hours || 0}h (${slp.efficiency_score || 0}%)</td>
          <td>${hr.resting_bpm || 0} bpm / ${hr.hrv_ms || 0} ms</td>
          <td>${scr.total_screen_hours || 0}h (${scr.late_night_screen_minutes || 0}m late)</td>
          <td><span class="cluster-pill" style="padding: 2px 8px; font-size: 0.72rem; border-radius: 6px;">${(r.tags || [])[0] || 'Logged'}</span></td>
          <td>
            <button class="btn-icon-only" onclick="app.handleDeleteRecord('${r.id}')" title="Delete record" style="padding: 4px; width: 28px; height: 28px;">
              <i data-lucide="trash-2" style="width: 14px; height: 14px; color: var(--rose-primary);"></i>
            </button>
          </td>
        </tr>
      `;
    }).join('');
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    const iconName = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-circle' : 'info';
    toast.innerHTML = `
      <i data-lucide="${iconName}" style="width: 18px; height: 18px; color: var(--${type === 'success' ? 'teal-primary' : type === 'error' ? 'rose-primary' : 'teal-primary'});"></i>
      <span>${message}</span>
    `;
    container.appendChild(toast);
    if (window.lucide) lucide.createIcons({ root: toast });
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  }
};
