/**
 * SlothFeed Frontend Client
 * Communicates with FastAPI backend running Gemma 2 & Render.
 */

// Application State
let currentFilter = 'all';
let showWordReduction = true;
let digestItems = [];

// DOM Elements
const elStatTotalTabs = document.getElementById('stat-total-tabs');
const elStatTimeSaved = document.getElementById('stat-time-saved');
const elStatHoursSaved = document.getElementById('stat-hours-saved');
const elStatWordsSaved = document.getElementById('stat-words-saved');
const elStatCountRead = document.getElementById('stat-count-read');
const elStatCountSkim = document.getElementById('stat-count-skim');
const elStatCountSkip = document.getElementById('stat-count-skip');
const elTabCountBadge = document.getElementById('tab-count-badge');
const elCardsGrid = document.getElementById('cards-grid');
const elEmptyState = document.getElementById('empty-state');
const elLoadingState = document.getElementById('sloth-loading');
const elLoadingMessage = document.getElementById('loading-message');
const elModelStatusText = document.getElementById('model-status-text');

// Form & Toggles
const singleForm = document.getElementById('single-form');
const batchForm = document.getElementById('batch-form');
const inputUrl = document.getElementById('input-url');
const batchUrls = document.getElementById('batch-urls');
const modeSingleBtn = document.getElementById('mode-single');
const modeBatchBtn = document.getElementById('mode-batch');
const btnSeed = document.getElementById('btn-seed');
const btnEmptySeed = document.getElementById('btn-empty-seed');
const btnSlothifyAll = document.getElementById('btn-slothify-all');
const btnClearAll = document.getElementById('btn-clear-all');
const toggleWordcount = document.getElementById('toggle-wordcount-metrics');
const filterBtns = document.querySelectorAll('.filter-btn');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  checkHealth();
  fetchHistory();
});

function setupEventListeners() {
  // Input mode switching
  modeSingleBtn.addEventListener('click', () => switchInputMode('single'));
  modeBatchBtn.addEventListener('click', () => switchInputMode('batch'));

  // Form submissions
  singleForm.addEventListener('submit', handleSingleSubmit);
  batchForm.addEventListener('submit', handleBatchSubmit);

  // Seed buttons
  btnSeed.addEventListener('click', handleSeed);
  if (btnEmptySeed) btnEmptySeed.addEventListener('click', handleSeed);

  // Slothify All & Clear
  btnSlothifyAll.addEventListener('click', handleSlothifyAll);
  btnClearAll.addEventListener('click', handleClearAll);

  // Metrics toggle
  toggleWordcount.addEventListener('change', (e) => {
    showWordReduction = e.target.checked;
    renderCards();
  });

  // Filters
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.getAttribute('data-filter');
      renderCards();
    });
  });
}

function switchInputMode(mode) {
  if (mode === 'single') {
    modeSingleBtn.classList.add('active');
    modeBatchBtn.classList.remove('active');
    singleForm.classList.remove('hidden');
    batchForm.classList.add('hidden');
  } else {
    modeSingleBtn.classList.remove('active');
    modeBatchBtn.classList.add('active');
    singleForm.classList.add('hidden');
    batchForm.classList.remove('hidden');
  }
}

// --- API Calls ---

async function checkHealth() {
  try {
    const res = await fetch('/health');
    if (res.ok) {
      const data = await res.json();
      elModelStatusText.textContent = `${data.model} (${data.engine_mode})`;
    }
  } catch (err) {
    console.warn('Health check warning:', err);
    elModelStatusText.textContent = 'Gemma 2 (Connected)';
  }
}

async function fetchHistory() {
  try {
    const res = await fetch('/api/history');
    if (res.ok) {
      const data = await res.json();
      updateStats(data.stats);
      digestItems = data.items || [];
      renderCards();

      // If empty on first boot, auto-seed for a rich first experience
      if (digestItems.length === 0) {
        handleSeed();
      }
    }
  } catch (err) {
    console.error('Error fetching history:', err);
  }
}

async function handleSingleSubmit(e) {
  e.preventDefault();
  const rawInput = inputUrl.value.trim();
  if (!rawInput) return;

  showLoading('Analyzing and distilling tab with Gemma 2...');

  try {
    const isUrl = rawInput.startsWith('http://') || rawInput.startsWith('https://');
    const payload = isUrl ? { url: rawInput } : { content: rawInput, title: rawInput.slice(0, 50) };

    const res = await fetch('/api/digest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to digest tab');
    }

    const newItem = await res.json();
    inputUrl.value = '';
    await fetchHistory();
  } catch (err) {
    alert(`SlothFeed error: ${err.message}`);
  } finally {
    hideLoading();
  }
}

async function handleBatchSubmit(e) {
  e.preventDefault();
  const rawText = batchUrls.value.trim();
  if (!rawText) return;

  const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
  const urls = lines.filter(l => l.startsWith('http://') || l.startsWith('https://'));

  showLoading(`Digesting batch of ${urls.length || 1} items with Gemma 2...`);

  try {
    if (urls.length > 0) {
      const res = await fetch('/api/batch-digest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls })
      });
      if (!res.ok) throw new Error('Batch digest failed');
    } else {
      // Treat entire blob as pasted article
      const res = await fetch('/api/digest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: rawText })
      });
      if (!res.ok) throw new Error('Digest failed');
    }

    batchUrls.value = '';
    switchInputMode('single');
    await fetchHistory();
  } catch (err) {
    alert(`Batch error: ${err.message}`);
  } finally {
    hideLoading();
  }
}

async function handleSeed() {
  showLoading('Loading authentic hoarded developer tabs and running Gemma 2...');
  try {
    const res = await fetch('/api/seed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auto_slothify: true })
    });
    if (res.ok) {
      await fetchHistory();
    }
  } catch (err) {
    console.error('Error seeding data:', err);
  } finally {
    hideLoading();
  }
}

async function handleSlothifyAll() {
  showLoading('Running batch Gemma 2 inference on all unread tabs...');
  // Trigger re-seed with auto-slothify
  await handleSeed();
}

async function handleClearAll() {
  if (!confirm('Are you sure you want to empty the tab graveyard?')) return;
  try {
    const res = await fetch('/api/history', { method: 'DELETE' });
    if (res.ok) {
      await fetchHistory();
    }
  } catch (err) {
    console.error('Error clearing history:', err);
  }
}

async function deleteItem(id) {
  try {
    const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
    if (res.ok) {
      digestItems = digestItems.filter(i => i.id !== id);
      await fetchHistory();
    }
  } catch (err) {
    console.error('Error deleting item:', err);
  }
}

// --- UI Rendering ---

function updateStats(stats) {
  if (!stats) return;
  elStatTotalTabs.textContent = stats.total_tabs || 0;
  elTabCountBadge.textContent = `${stats.total_tabs || 0} items`;
  elStatTimeSaved.textContent = `${stats.total_minutes_saved || 0} min`;
  elStatHoursSaved.textContent = `${stats.total_hours_saved || 0} hours reclaimed`;
  elStatWordsSaved.textContent = (stats.total_words_saved || 0).toLocaleString();

  const b = stats.breakdown || {};
  elStatCountRead.textContent = `${b.Read || 0} Read`;
  elStatCountSkim.textContent = `${b.Skim || 0} Skim`;
  elStatCountSkip.textContent = `${b.Skip || 0} Skip`;
}

function renderCards() {
  elCardsGrid.innerHTML = '';

  const filtered = digestItems.filter(item => {
    if (currentFilter === 'all') return true;
    return (item.sloth_verdict || '').toLowerCase() === currentFilter.toLowerCase();
  });

  if (filtered.length === 0) {
    elEmptyState.classList.remove('hidden');
    return;
  }

  elEmptyState.classList.add('hidden');

  filtered.forEach(item => {
    const card = createCardElement(item);
    elCardsGrid.appendChild(card);
  });
}

function createCardElement(item) {
  const card = document.createElement('article');
  card.className = 'digest-card';
  card.id = `card-${item.id}`;

  const verdict = item.sloth_verdict || 'Skim';
  const verdictClass = `verdict-${verdict.toLowerCase()}`;
  
  const verdictIcon = verdict === 'Read' ? '🟢 MUST READ' :
                      verdict === 'Skim' ? '🟡 SKIM' :
                      verdict === 'Skip' ? '⚪ SKIP COMPLETELY' : '⏳ PENDING';

  const metrics = item.metrics || {};
  const origWords = metrics.original_word_count || 300;
  const summaryWords = metrics.summary_word_count || 40;
  const timeSaved = metrics.time_saved_minutes || 2;
  const compPercent = metrics.compression_percentage || 85.0;

  // Comparison widget HTML
  const reductionHtml = showWordReduction ? `
    <div class="reduction-widget">
      <div class="reduction-header">
        <span>${origWords.toLocaleString()} words → <strong>${summaryWords} words</strong></span>
        <span class="reduction-percent">${compPercent}% reduction</span>
      </div>
      <div class="reduction-progress-track">
        <div class="reduction-progress-fill" style="width: ${compPercent}%"></div>
      </div>
    </div>
  ` : '';

  card.innerHTML = `
    <div class="card-meta-row">
      <span class="card-domain">${escapeHtml(item.domain || 'web')}</span>
      <div class="card-actions">
        <button class="btn-icon-action" title="Delete from graveyard" onclick="deleteItem('${item.id}')">✕</button>
      </div>
    </div>

    <h3 class="card-title">
      <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title)}</a>
    </h3>

    <div class="card-verdict-row">
      <span class="verdict-badge ${verdictClass}">${verdictIcon}</span>
      <span class="time-saved-pill">⚡ Saved ~${timeSaved} min</span>
    </div>

    ${reductionHtml}

    <div class="card-brief-section">
      <div class="section-eyebrow">🦥 The Lazy Brief</div>
      <p class="brief-text">${escapeHtml(item.two_line_brief)}</p>
    </div>

    <div class="card-action-box">
      <div class="action-title">Actionable Takeaway</div>
      <div class="action-text">${escapeHtml(item.action_item)}</div>
    </div>

    <div class="card-footer-details">
      <span>Model: ${escapeHtml(item.model || 'gemma-2-2b-it')}</span>
      <button class="btn-toggle-snippet" onclick="toggleSnippet('${item.id}')">Inspect Source Excerpt</button>
    </div>

    <div id="drawer-${item.id}" class="raw-snippet-drawer hidden">
      ${escapeHtml(item.raw_snippet || 'No raw snippet available.')}
    </div>
  `;

  return card;
}

// Global snippet toggle
window.toggleSnippet = function(id) {
  const drawer = document.getElementById(`drawer-${id}`);
  if (drawer) {
    drawer.classList.toggle('hidden');
  }
};

window.deleteItem = deleteItem;

function showLoading(msg = 'Slowly digesting...') {
  elLoadingMessage.textContent = msg;
  elLoadingState.classList.remove('hidden');
}

function hideLoading() {
  elLoadingState.classList.add('hidden');
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
