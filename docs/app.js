const themeScript = document.createElement('script');
themeScript.src = 'https://www.exergism.org/assets/theme.js';
themeScript.dataset.ecTheme = '';
document.head.appendChild(themeScript);

const wordmarkStylesheet = document.createElement('link');
wordmarkStylesheet.rel = 'stylesheet';
wordmarkStylesheet.href = 'wordmark.css';
wordmarkStylesheet.dataset.commonsWordmark = '';
document.head.appendChild(wordmarkStylesheet);

const siteBrand = document.querySelector('.site-header .brand');
if (siteBrand) {
  siteBrand.setAttribute('href', '/');
  siteBrand.setAttribute('aria-label', 'Funding home');
}

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
  const text = String(value);
  const match = text.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!match) return null;
  const [, year, month, day] = match;
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const monthName = monthNames[Number(month) - 1];
  return monthName ? `${day} ${monthName} ${year}` : null;
}

function deadlineContent(value) {
  if (!value) return { primary: 'Continuous', secondary: 'strategic engagement' };

  const target = new Date(value);
  const now = new Date();
  const targetTime = target.getTime();
  const dateText = formatDate(value);

  if (Number.isNaN(targetTime) || !dateText) {
    return { primary: 'Unknown', secondary: 'deadline unavailable' };
  }

  const remainingMs = targetTime - now.getTime();
  if (remainingMs <= 0) {
    return { primary: dateText, secondary: 'deadline passed' };
  }
  if (remainingMs < 86400000) {
    return { primary: dateText, secondary: 'less than 24 hours remaining' };
  }

  const diffDays = Math.ceil(remainingMs / 86400000);
  const dayLabel = diffDays === 1 ? 'day' : 'days';
  return { primary: dateText, secondary: `${diffDays} ${dayLabel} remaining` };
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

function safeHttpsUrl(href) {
  if (!href) return null;
  try {
    const url = new URL(String(href), window.location.href);
    return url.protocol === 'https:' ? url.href : null;
  } catch {
    return null;
  }
}

function metaBox(label, value) {
  const box = document.createElement('div');
  box.className = 'meta-box';
  const labelNode = document.createElement('span');
  const valueNode = document.createElement('strong');
  labelNode.textContent = label;
  valueNode.textContent = value || 'Unknown';
  box.append(labelNode, valueNode);
  return box;
}

function opportunityElement(opportunity) {
  const signal = institutionalSignal(opportunity);
  const ranked = signal !== null;
  const percent = ranked ? Math.round(signal * 100) : null;
  const scoreValue = ranked ? `${percent}/100` : 'Not ranked';
  const scoreTitle = ranked
    ? 'Non-binding EIV heuristic'
    : 'Missing or invalid required EIV dimensions; excluded from automated ranking';
  const scoreWidth = ranked ? percent : 0;

  const article = document.createElement('article');
  article.className = 'opportunity-card';
  article.dataset.priority = String(opportunity.priority || '');

  const top = document.createElement('div');
  top.className = 'card-top';
  const priority = document.createElement('span');
  priority.className = 'priority';
  priority.dataset.priority = String(opportunity.priority || '');
  priority.textContent = opportunity.priority || '—';
  const status = document.createElement('span');
  status.className = 'card-status';
  status.textContent = formatStatus(opportunity.status);
  top.append(priority, status);

  const title = document.createElement('h3');
  title.textContent = opportunity.name || 'Untitled opportunity';

  const funder = document.createElement('p');
  funder.className = 'card-funder';
  funder.textContent = opportunity.funder || opportunity.programme || 'Unknown';

  const meta = document.createElement('div');
  meta.className = 'card-meta';
  meta.append(
    metaBox('EC role', opportunity.ec_role),
    metaBox('Geography', opportunity.geography),
  );

  const eivWrap = document.createElement('div');
  eivWrap.className = 'eiv-wrap';
  const eivRow = document.createElement('div');
  eivRow.className = 'eiv-row';
  const eivLabel = document.createElement('span');
  eivLabel.textContent = 'Institutional value signal';
  const eivValue = document.createElement('strong');
  eivValue.textContent = scoreValue;
  eivRow.append(eivLabel, eivValue);
  const eivTrack = document.createElement('div');
  eivTrack.className = 'eiv-track';
  eivTrack.title = scoreTitle;
  const eivBar = document.createElement('span');
  eivBar.style.width = `${scoreWidth}%`;
  eivTrack.appendChild(eivBar);
  eivWrap.append(eivRow, eivTrack);

  const next = document.createElement('p');
  next.className = 'card-next';
  const nextLabel = document.createElement('strong');
  nextLabel.textContent = 'Next:';
  next.append(nextLabel, document.createTextNode(` ${opportunity.next_action || 'No next action recorded.'}`));

  const actions = document.createElement('div');
  actions.className = 'card-actions';
  const sourceLink = safeHttpsUrl(opportunity.dossier || opportunity.source);
  if (sourceLink) {
    const link = document.createElement('a');
    link.className = 'card-link';
    link.href = sourceLink;
    link.textContent = 'Open dossier ↗';
    actions.appendChild(link);
  }

  const deadline = document.createElement('span');
  deadline.className = 'deadline';
  const deadlineValue = deadlineContent(opportunity.deadline);
  const deadlinePrimary = document.createElement('strong');
  deadlinePrimary.textContent = deadlineValue.primary;
  deadline.append(deadlinePrimary, document.createElement('br'), document.createTextNode(deadlineValue.secondary));
  actions.appendChild(deadline);

  article.append(top, title, funder, meta, eivWrap, next, actions);
  return article;
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

  grid.replaceChildren(...visible.map(opportunityElement));
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
    const message = document.createElement('p');
    message.className = 'empty-state';
    message.textContent = 'Opportunity data could not be loaded. Use the public GitHub repository as the source of truth.';
    grid.replaceChildren(message);
    console.error('Funding data load failed:', error);
  }
}

function injectMachineGovernance() {
  if (document.querySelector('#machine-governance')) return;

  const independence = document.querySelector('#independence');
  if (independence) {
    independence.insertAdjacentHTML('afterend', `
      <section class="section" id="machine-governance">
        <div class="shell">
          <div class="section-heading">
            <p class="eyebrow">04 · Executable governance</p>
            <h2>Policy that can be inspected by machines.</h2>
            <p>Funding governance is represented as an auditable semantic stack. Code validates explicit institutional state; it does not replace the competent EC body, statutes or applicable law.</p>
          </div>

          <div class="principles-grid">
            <article class="principle-card">
              <span class="principle-index">OWL</span>
              <h3>Domain semantics</h3>
              <p>Funding opportunities, decisions, conflicts, votes, compensation and Endowment actions have explicit classes and properties without hidden approval inference.</p>
            </article>
            <article class="principle-card">
              <span class="principle-index">JSON-LD</span>
              <h3>Git-native state</h3>
              <p>Concrete governance records remain diffable, versioned and attributable in Git instead of disappearing inside a private database.</p>
            </article>
            <article class="principle-card">
              <span class="principle-index">SHACL</span>
              <h3>Machine-checkable safeguards</h3>
              <p>Anti-capture, concentration, conflict-of-interest, EIV completeness and Endowment-principal invariants are validated as repository constraints.</p>
            </article>
            <article class="principle-card">
              <span class="principle-index">RDF</span>
              <h3>Rebuildable audit graph</h3>
              <p>The live opportunity registry and governance records compile into disposable RDF that can be rebuilt deterministically from canonical repository sources.</p>
            </article>
          </div>

          <div class="hero-actions">
            <a class="button button-primary" href="https://github.com/Exergism-Commons/funding/blob/main/spec/MACHINE-READABLE-GOVERNANCE.md">Read the governance specification</a>
            <a class="button button-secondary" href="https://github.com/Exergism-Commons/funding/tree/main/ontology">Inspect ontology &amp; SHACL</a>
            <a class="button button-secondary" href="https://github.com/Exergism-Commons/funding/tree/main/knowledge">Inspect governance records</a>
          </div>
        </div>
      </section>`);
  }

  const nav = document.querySelector('#primary-nav');
  if (nav && !nav.querySelector('a[href="#machine-governance"]')) {
    const commonsLink = [...nav.querySelectorAll('a')].find(link => link.href === 'https://www.exergism.org/');
    const governanceLink = document.createElement('a');
    governanceLink.href = '#machine-governance';
    governanceLink.textContent = 'Governance';
    if (commonsLink) nav.insertBefore(governanceLink, commonsLink);
    else nav.appendChild(governanceLink);
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

injectMachineGovernance();
bindFilters();
bindNavigation();
loadData();
