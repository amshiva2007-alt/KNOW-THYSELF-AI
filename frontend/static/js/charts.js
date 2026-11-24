/**
 * Know Thyself AI - Chart.js Visualization Engine
 * Theme: Gen Z Cyberpop / Y2K Digital Core
 * Palette: Electric Neon Mint (#00FF9D), Hyper Cyan (#00F0FF), Hot Cyber Pink (#FF2A85), Digital Lavender (#A855F7), Solar Gold (#FFB800)
 */

const WellnessCharts = {
  instances: {},

  destroyChart(id) {
    if (this.instances[id]) {
      this.instances[id].destroy();
      delete this.instances[id];
    }
  },

  getDefaultGridOptions() {
    return {
      color: 'rgba(216, 180, 254, 0.08)',
      drawBorder: false
    };
  },

  getDefaultTicksOptions() {
    return {
      color: '#8B7BB5',
      font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' }
    };
  },

  // 1. Overview Trajectory Chart (Wellness Score & Sleep Hours)
  renderOverviewTrajectory(canvasId, timeseries) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    const neonGradient = ctx.createLinearGradient(0, 0, 0, 300);
    neonGradient.addColorStop(0, 'rgba(0, 255, 157, 0.35)');
    neonGradient.addColorStop(1, 'rgba(0, 255, 157, 0.0)');

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: timeseries.labels,
        datasets: [
          {
            label: 'Wellness Score',
            data: timeseries.datasets.wellness_scores,
            borderColor: '#00FF9D',
            backgroundColor: neonGradient,
            borderWidth: 2.8,
            fill: true,
            tension: 0.38,
            pointBackgroundColor: '#00FF9D',
            pointBorderColor: '#090714',
            pointBorderWidth: 1.5,
            pointRadius: 3.5,
            pointHoverRadius: 7,
            yAxisID: 'y'
          },
          {
            label: 'Sleep Duration (hrs)',
            data: timeseries.datasets.sleep_hours,
            borderColor: '#A855F7',
            backgroundColor: 'transparent',
            borderWidth: 2.2,
            borderDash: [4, 4],
            tension: 0.38,
            pointBackgroundColor: '#A855F7',
            pointBorderColor: '#090714',
            pointBorderWidth: 1,
            pointRadius: 3,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'top',
            labels: { color: '#C4B5FD', font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' } }
          },
          tooltip: {
            backgroundColor: '#120E28',
            borderColor: 'rgba(0, 255, 157, 0.4)',
            borderWidth: 1,
            titleColor: '#FFFFFF',
            bodyColor: '#C4B5FD',
            padding: 11,
            cornerRadius: 10
          }
        },
        scales: {
          x: { grid: this.getDefaultGridOptions(), ticks: this.getDefaultTicksOptions() },
          y: {
            type: 'linear',
            position: 'left',
            min: 40,
            max: 100,
            grid: this.getDefaultGridOptions(),
            ticks: this.getDefaultTicksOptions(),
            title: { display: true, text: 'Score (0-100)', color: '#8B7BB5' }
          },
          y1: {
            type: 'linear',
            position: 'right',
            min: 4,
            max: 10,
            grid: { drawOnChartArea: false },
            ticks: this.getDefaultTicksOptions(),
            title: { display: true, text: 'Hours', color: '#8B7BB5' }
          }
        }
      }
    });
  },

  // 2. Pre-Bed Screen Time vs Sleep Latency Chart (The Core Discovery)
  renderScreenSleepCorrelation(canvasId, timeseries) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: timeseries.labels,
        datasets: [
          {
            type: 'bar',
            label: 'Late Night Screen (mins)',
            data: timeseries.datasets.late_screen_mins,
            backgroundColor: 'rgba(255, 42, 133, 0.55)',
            borderColor: '#FF2A85',
            borderWidth: 1.5,
            borderRadius: 6,
            yAxisID: 'y'
          },
          {
            type: 'line',
            label: 'Sleep Latency (mins to sleep)',
            data: timeseries.datasets.sleep_latency,
            borderColor: '#00F0FF',
            backgroundColor: '#00F0FF',
            borderWidth: 2.5,
            tension: 0.35,
            pointRadius: 3.5,
            pointBackgroundColor: '#00F0FF',
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { color: '#C4B5FD', font: { weight: '600' } } },
          tooltip: {
            backgroundColor: '#120E28',
            borderColor: 'rgba(255, 42, 133, 0.45)',
            borderWidth: 1,
            titleColor: '#FFFFFF',
            bodyColor: '#C4B5FD',
            padding: 11,
            cornerRadius: 10
          }
        },
        scales: {
          x: { grid: this.getDefaultGridOptions(), ticks: this.getDefaultTicksOptions() },
          y: {
            position: 'left',
            grid: this.getDefaultGridOptions(),
            ticks: this.getDefaultTicksOptions(),
            title: { display: true, text: 'Screen (min)', color: '#8B7BB5' }
          },
          y1: {
            position: 'right',
            grid: { drawOnChartArea: false },
            ticks: this.getDefaultTicksOptions(),
            title: { display: true, text: 'Latency (min)', color: '#8B7BB5' }
          }
        }
      }
    });
  },

  // 3. Activity & Heart Dynamics
  renderActivityHeartDynamics(canvasId, timeseries) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: timeseries.labels,
        datasets: [
          {
            label: 'Daily Steps',
            data: timeseries.datasets.steps,
            borderColor: '#00FF9D',
            backgroundColor: 'rgba(0, 255, 157, 0.15)',
            fill: true,
            borderWidth: 2.5,
            yAxisID: 'y'
          },
          {
            label: 'Heart Rate Variability (HRV ms)',
            data: timeseries.datasets.hrv,
            borderColor: '#FF2A85',
            borderWidth: 2.5,
            tension: 0.35,
            pointBackgroundColor: '#FF2A85',
            yAxisID: 'y1'
          },
          {
            label: 'Resting Heart Rate (BPM)',
            data: timeseries.datasets.resting_hr,
            borderColor: '#FFB800',
            borderWidth: 2.2,
            borderDash: [3, 3],
            pointBackgroundColor: '#FFB800',
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { position: 'top', labels: { color: '#C4B5FD', font: { weight: '600' } } },
          tooltip: {
            backgroundColor: '#120E28',
            borderColor: 'rgba(0, 255, 157, 0.4)',
            borderWidth: 1,
            titleColor: '#FFFFFF',
            bodyColor: '#C4B5FD',
            padding: 11,
            cornerRadius: 10
          }
        },
        scales: {
          x: { grid: this.getDefaultGridOptions(), ticks: this.getDefaultTicksOptions() },
          y: {
            position: 'left',
            grid: this.getDefaultGridOptions(),
            ticks: this.getDefaultTicksOptions(),
            title: { display: true, text: 'Steps', color: '#8B7BB5' }
          },
          y1: {
            position: 'right',
            grid: { drawOnChartArea: false },
            ticks: this.getDefaultTicksOptions(),
            title: { display: true, text: 'BPM / ms', color: '#8B7BB5' }
          }
        }
      }
    });
  },

  // 4. Sleep Stages Breakdown
  renderSleepStages(canvasId, timeseries) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: timeseries.labels,
        datasets: [
          {
            label: 'Deep Sleep (hrs)',
            data: timeseries.datasets.deep_sleep,
            backgroundColor: '#00FF9D',
            borderRadius: 6
          },
          {
            label: 'REM Sleep (hrs)',
            data: timeseries.datasets.rem_sleep,
            backgroundColor: '#A855F7',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { color: '#C4B5FD', font: { weight: '600' } } },
          tooltip: {
            backgroundColor: '#120E28',
            borderColor: 'rgba(168, 85, 247, 0.4)',
            borderWidth: 1,
            titleColor: '#FFFFFF',
            bodyColor: '#C4B5FD',
            padding: 11,
            cornerRadius: 10
          }
        },
        scales: {
          x: { grid: this.getDefaultGridOptions(), ticks: this.getDefaultTicksOptions() },
          y: {
            stacked: false,
            grid: this.getDefaultGridOptions(),
            ticks: this.getDefaultTicksOptions(),
            title: { display: true, text: 'Hours', color: '#8B7BB5' }
          }
        }
      }
    });
  },

  // 5. Screen Time Trends
  renderScreenTimeBreakdown(canvasId, timeseries) {
    this.destroyChart(canvasId);
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    const screenGradient = ctx.createLinearGradient(0, 0, 0, 300);
    screenGradient.addColorStop(0, 'rgba(255, 42, 133, 0.28)');
    screenGradient.addColorStop(1, 'rgba(255, 42, 133, 0.0)');

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: timeseries.labels,
        datasets: [
          {
            label: 'Total Screen Time (hrs)',
            data: timeseries.datasets.screen_hours,
            borderColor: '#FF2A85',
            backgroundColor: screenGradient,
            fill: true,
            borderWidth: 2.5,
            tension: 0.38,
            pointBackgroundColor: '#FF2A85',
            pointRadius: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { color: '#C4B5FD', font: { weight: '600' } } },
          tooltip: {
            backgroundColor: '#120E28',
            borderColor: 'rgba(255, 42, 133, 0.4)',
            borderWidth: 1,
            titleColor: '#FFFFFF',
            bodyColor: '#C4B5FD',
            padding: 11,
            cornerRadius: 10
          }
        },
        scales: {
          x: { grid: this.getDefaultGridOptions(), ticks: this.getDefaultTicksOptions() },
          y: {
            grid: this.getDefaultGridOptions(),
            ticks: this.getDefaultTicksOptions(),
            title: { display: true, text: 'Screen Hours', color: '#8B7BB5' }
          }
        }
      }
    });
  }
};
