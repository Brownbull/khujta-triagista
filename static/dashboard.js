/* Dashboard JS — SRE Triage Agent */
/* Settings persistence, triage/ack/resolve actions */

(function() {
  'use strict';

  // ==================== SETTINGS ====================
  const STORAGE_KEY = 'sre-dashboard-settings';
  const DEFAULTS = { theme: 'dark', fontSize: 'medium', font: 'IBM Plex Sans' };

  function loadSettings() {
    try {
      return Object.assign({}, DEFAULTS, JSON.parse(localStorage.getItem(STORAGE_KEY)));
    } catch { return Object.assign({}, DEFAULTS); }
  }

  function saveSettings(s) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  }

  function applySettings(s) {
    var html = document.documentElement;
    // Theme
    html.classList.remove('light');
    if (s.theme === 'light') html.classList.add('light');
    // Font size
    html.classList.remove('font-small', 'font-medium', 'font-large');
    html.classList.add('font-' + s.fontSize);
    // Font family
    html.style.setProperty('--sans', "'" + s.font + "', sans-serif");

    // Update active buttons
    updateSettingsUI(s);
  }

  function updateSettingsUI(s) {
    // Theme buttons
    document.querySelectorAll('[data-setting="theme"]').forEach(function(btn) {
      btn.classList.toggle('active', btn.dataset.value === s.theme);
    });
    // Font size buttons
    document.querySelectorAll('[data-setting="fontSize"]').forEach(function(btn) {
      btn.classList.toggle('active', btn.dataset.value === s.fontSize);
    });
    // Font buttons
    document.querySelectorAll('[data-setting="font"]').forEach(function(btn) {
      btn.classList.toggle('active', btn.dataset.value === s.font);
    });
  }

  // Toggle settings dropdown
  window.toggleSettings = function() {
    var dd = document.getElementById('settings-dropdown');
    if (dd) dd.classList.toggle('open');
  };

  // Close dropdown on outside click
  document.addEventListener('click', function(e) {
    var dd = document.getElementById('settings-dropdown');
    var btn = document.getElementById('settings-btn');
    if (dd && btn && !dd.contains(e.target) && !btn.contains(e.target)) {
      dd.classList.remove('open');
    }
  });

  // Setting change handler
  window.changeSetting = function(key, value) {
    var s = loadSettings();
    s[key] = value;
    saveSettings(s);
    applySettings(s);
  };

  // Apply on load
  applySettings(loadSettings());

  // ==================== TRIAGE ====================
  window.runTriage = function(incidentId) {
    var btn = document.getElementById('btn-triage');
    if (!btn) return;
    btn.disabled = true;
    btn.innerHTML = '<span class="triage-spinner"></span> Triaging...';

    var provider = localStorage.getItem('sre-triage-provider') || '';
    var url = '/api/incidents/' + incidentId + '/triage';
    if (provider) url += '?provider=' + encodeURIComponent(provider);

    fetch(url, { method: 'POST' })
      .then(function(r) {
        if (!r.ok) return r.json().then(function(d) { throw new Error(d.detail || 'Triage failed'); });
        return r.json();
      })
      .then(function() { window.location.reload(); })
      .catch(function(err) {
        alert('Triage error: ' + err.message);
        btn.disabled = false;
        btn.textContent = 'Run Triage';
      });
  };

  // ==================== ACKNOWLEDGE ====================
  window.acknowledgeIncident = function(incidentId) {
    fetch('/api/incidents/' + incidentId + '/acknowledge', { method: 'POST' })
      .then(function(r) {
        if (!r.ok) return r.json().then(function(d) { throw new Error(d.detail || 'Failed'); });
        window.location.reload();
      })
      .catch(function(err) { alert('Acknowledge error: ' + err.message); });
  };

  // ==================== RESOLVE ====================
  window.openResolveDialog = function() {
    var overlay = document.getElementById('resolve-overlay');
    if (overlay) overlay.classList.add('open');
  };

  window.closeResolveDialog = function() {
    var overlay = document.getElementById('resolve-overlay');
    if (overlay) overlay.classList.remove('open');
  };

  window.submitResolve = function(incidentId) {
    var form = document.getElementById('resolve-form');
    if (!form) return;
    var formData = new FormData(form);

    fetch('/api/incidents/' + incidentId + '/resolve', {
      method: 'POST',
      body: formData,
    })
      .then(function(r) {
        if (!r.ok) return r.json().then(function(d) { throw new Error(d.detail || 'Failed'); });
        window.location.reload();
      })
      .catch(function(err) { alert('Resolve error: ' + err.message); });
  };

  // Close resolve dialog on overlay click
  document.addEventListener('click', function(e) {
    if (e.target.id === 'resolve-overlay') {
      window.closeResolveDialog();
    }
  });

  // Close resolve dialog on Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') window.closeResolveDialog();
  });

  // ==================== MOBILE SIDEBAR ====================
  window.toggleSidebar = function() {
    document.querySelector('.sidebar').classList.toggle('open');
    document.getElementById('sidebar-overlay').classList.toggle('open');
  };

  window.closeSidebar = function() {
    document.querySelector('.sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('open');
  };

  // ==================== EXPLANATION TABS ====================
  window.switchExplainTab = function(tab, btn) {
    document.querySelectorAll('.explain-content').forEach(function(c) { c.classList.remove('active'); });
    document.querySelectorAll('.explain-tab').forEach(function(t) { t.classList.remove('active'); });
    var el = document.getElementById('explain-' + tab);
    if (el) el.classList.add('active');
    if (btn) btn.classList.add('active');
  };

})();
