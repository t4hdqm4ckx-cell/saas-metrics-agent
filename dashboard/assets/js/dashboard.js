/**
 * dashboard.js — FlowSync Dashboard Utility Module
 *
 * Supplemental JavaScript utilities for the FlowSync SaaS Metrics Dashboard.
 * Primary chart code lives in index.html for self-containment.
 * This module provides formatting helpers, export utilities, and event handling.
 */

'use strict';

/* ── FORMAT HELPERS ── */

const fmt = {
  currency: (v, decimals = 0) => {
    if (v >= 1_000_000) return '$' + (v / 1_000_000).toFixed(1) + 'M';
    if (v >= 1_000)     return '$' + (v / 1_000).toFixed(1) + 'K';
    return '$' + v.toFixed(decimals);
  },

  pct: (v, decimals = 1) => v.toFixed(decimals) + '%',

  number: (v) => v.toLocaleString('en-US'),

  ratio: (v) => v.toFixed(1) + '×',

  months: (v) => v.toFixed(1) + ' mo',

  delta: (current, prior) => {
    if (!prior) return null;
    const pct = (current - prior) / Math.abs(prior) * 100;
    return {
      value: pct,
      formatted: (pct >= 0 ? '+' : '') + pct.toFixed(1) + '%',
      direction: pct > 0.5 ? 'up' : pct < -0.5 ? 'down' : 'flat'
    };
  }
};

/* ── CHART EXPORT ── */

function exportChartAsPNG(chartId, filename) {
  const canvas = document.getElementById(chartId);
  if (!canvas) {
    console.error(`[FlowSync] E401: Canvas #${chartId} not found for export`);
    return;
  }
  const link = document.createElement('a');
  link.download = filename || chartId + '.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
}

/* ── DATA EXPORT ── */

function exportDataAsCSV(data, filename) {
  if (!data || !data.length) return;
  const headers = Object.keys(data[0]);
  const rows = data.map(row => headers.map(h => JSON.stringify(row[h] ?? '')).join(','));
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename || 'flowsync-export.csv';
  link.click();
}

/* ── KEYBOARD NAVIGATION ── */

document.addEventListener('keydown', e => {
  if (e.key >= '1' && e.key <= '4' && (e.metaKey || e.ctrlKey)) {
    e.preventDefault();
    const tabs = ['revenue', 'customers', 'engagement', 'economics'];
    const tabIndex = parseInt(e.key) - 1;
    if (tabIndex < tabs.length) {
      document.querySelector(`[data-tab="${tabs[tabIndex]}"]`)?.click();
    }
  }
});

/* ── WINDOW RESIZE ── */

let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    // Chart.js handles responsive resizing automatically.
    // This hook is available for custom resize logic if needed.
    window.dispatchEvent(new CustomEvent('flowsync:resize'));
  }, 150);
});

/* ── GLOBAL ERROR HANDLER ── */

window.addEventListener('error', e => {
  console.error(`[FlowSync Dashboard] Uncaught error: ${e.message} (${e.filename}:${e.lineno})`);
});

window.addEventListener('unhandledrejection', e => {
  console.error(`[FlowSync Dashboard] Unhandled promise rejection:`, e.reason);
});

/* ── EXPOSE UTILITIES ── */

window.FlowSync = { fmt, exportChartAsPNG, exportDataAsCSV };
