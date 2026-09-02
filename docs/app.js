const state = { opportunities: [], filter: 'all', query: '' };

const positiveDimensions = ['fit','funding_value','capability_value','strategic_optionality','autonomy_value','network_value','recurrence'];
const negativeDimensions = ['capture_risk','admin_cost','execution_risk'];
const requiredDimensions = [...positiveDimensions, ...negativeDimensions];

function mean(values) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function hasCompleteScore(opportunity) {
  return requiredDimensions.every(key => {
    const value = opportunity[key];
    return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1;
  });
}

function institutionalSignal(opportunity) {
  if (!hasCompleteScore(opportunity)) return null;
  const positive = mean(positiveDimensions.map(key => opportunity[key]));
  const invertedRisk = 1 - mean(negativeDimensions.map(key => opportunity[key]));
  return Math.max(0, Math.min(1, (positive + invertedRisk) / 2));
}

function formatStatus(value) {
  return String(value || 'unknown').replaceAll('_', ' ');
}

function formatDate(value) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(date);
}

function deadlineLabel(value) {
  if (!value) return '<strong>Continuous</strong><br>strategic engagement';
  const target = new Date(value);
  const now = new Date();
  const targetTime = target.getTime();
  const dateText = formatDate(value);

  if (Number.isNaN(targetTime) || !dateText) return '<strong>Unknown</strong><br>deadline unavailable';
  if (targetTime <= now.getTime()) return `<strong>${dateText}</strong><br>deadline passed`;

  const sameLocalDay = target.getFullYear() === now.getFullYear()
    && target.getMonth() === now.getMonth()
    && target.getDate() === now.getDate();
  if (sameLocalDay) return `<strong>${dateText}</strong><br>due today`;

  const diffDays = Math.ceil((targetTime - now.getTime()) / 86400000);
  if (diffDays === 1) return `<strong>${dateText}</strong><br>1 day remaining`;
  return `<strong>${dateText}</strong><br>${diffDays} days remaining`;
}

function matches(opportunity) {
  const priorityMatch = state.filter === 'all' || opportunity.priority === state.filter;
  const haystack = [opportunity.name, opportunity.funder, opportunity.programme, opportunity.ec_role, opportunity.geography, opportunity.next_action]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
  const queryMatch = !state.query || haystack.includes(state.query);
  return priorityMatch && queryMatch;
}

function cardTemplate(opportunity) {
  const signal = institutionalSignal(opportunity);
  const ranked = signal !== null;
  const percent = ranked ? Math.round(signal * 100) : null;
  const sourceLink = opportunity.dossier || opportunity.source;
  const scoreValue = ranked ? `${percent}/100` : 'Not ranked';
  const scoreTitle = ranked
    ? 'Non-binding EIV heuristic'
    : 'Missing or invalid required EIV dimensions; excluded from automated ranking';
  const scoreWidth = ranked ? percent : 0;
  return `
    <article class="opportunity-card" data-priority="${opportunity.priority}">
      <div class="card-top">
        <span class="priority" data-priority="${opportunity.priority}">${opportunity.priority}</span>
        <span class="card-status">${formatStatus(opportunity.status)}</span>
      </div>
      <h3>${opportunity.name}</h3>
      <p class="card-funder">${opportunity.funder || opportunity.programme}</p>

      <div class="card-meta">
        <div class="meta-box"><span>EC role</span><strong>${opportunity.ec_role}</strong></div>
        <div class="meta-box"><span>Geography</span><strong>${opportunity.geography}</strong></div>
      </div>

      <div class="eiv-wrap">
        <div class="eiv-row"><span>Institutional value signal</span><strong>${scoreValue}</strong></div>
        <div class="eiv-track" title="${scoreTitle}"><span style="width:${scoreWidth}%"></span></div>
      </div>

      <p class="card-next"><strong>Next:</strong> ${opportunity.next_action}</p>

      <div class="card-actions">
        <a class="card-link" href="${sourceLink}">Open dossier ↗</a>
        <span class="deadline">${deadlineLabel(opportunity.deadline)}</span>
      </div>
    </article>`;
}

function compareByInstitutionalSignal(a, b) {
  const aSignal = institutionalSignal(a);
  const bSignal = institutionalSignal(b);
  if (aSignal === null && bSignal === null) return 0;
  if (aSignal === null) return 1;
  if (bSignal === null) return -1;
  return bSignal - aSignal;
}

function render() {
  const grid = document.querySelector('#opportunity-grid');
  const empty = document.querySelector('#empty-state');
  const visible = state.opportunities
    .filter(matches)
    .sort(compareByInstitutionalSignal);

  grid.innerHTML = visible.map(cardTemplate).join('');
  empty.hidden = visible.length !== 0;
}

async function loadData() {
  const grid = document.querySelector('#opportunity-grid');
  try {
    const response = await fetch('data/opportunities.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    state.opportunities = Array.isArray(data.opportunities) ? data.opportunities : [];
    document.querySelector('#data-updated').textContent = data.updated || 'unknown';
    render();
  } catch (error) {
    grid.innerHTML = '<p class="empty-state">Opportunity data could not be loaded. Use the public GitHub repository as the source of truth.</p>';
    console.error('Funding data load failed:', error);
  }
}

function bindFilters() {
  document.querySelectorAll('.filter').forEach(button => {
    button.addEventListener('click', () => {
      state.filter = button.dataset.filter;
      document.querySelectorAll('.filter').forEach(item => item.classList.toggle('is-active', item === button));
      render();
    });
  });

  const search = document.querySelector('#search');
  search.addEventListener('input', () => {
    state.query = search.value.trim().toLowerCase();
    render();
  });
}

function bindNavigation() {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#primary-nav');
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('is-open', !open);
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
  }));
}

bindFilters();
bindNavigation();
loadData();
