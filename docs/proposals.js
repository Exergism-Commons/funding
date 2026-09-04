const proposalStylesheet = document.createElement('link');
proposalStylesheet.rel = 'stylesheet';
proposalStylesheet.href = 'proposals.css';
document.head.appendChild(proposalStylesheet);

const TERMINAL_PROPOSAL_STATUSES = new Set(['awarded', 'rejected']);
const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const proposalState = { proposals: [] };

function proposalFormatStatus(value) {
  return String(value || 'unknown').replaceAll('_', ' ');
}

function proposalFormatDeadline(value) {
  if (!value) return 'No deadline';

  const text = String(value);
  const match = text.match(/^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2})(?::\d{2}(?:\.\d+)?)?(Z|[+-]\d{2}:\d{2}))?$/);
  if (!match) return text;

  const [, year, month, day, hour, minute, zone] = match;
  const monthName = MONTH_NAMES[Number(month) - 1];
  if (!monthName) return text;

  const dateText = `${day} ${monthName} ${year}`;
  if (!hour || !minute || !zone) return dateText;

  const zoneText = zone === 'Z' ? 'UTC' : `UTC${zone}`;
  return `${dateText} · ${hour}:${minute} ${zoneText}`;
}

function proposalAmount(proposal) {
  if (typeof proposal.requested_amount !== 'number') return 'Amount not fixed';
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: proposal.currency || 'EUR',
    maximumFractionDigits: 0,
  }).format(proposal.requested_amount);
}

function proposalLink(label, href) {
  if (!href) return null;

  let url;
  try {
    url = new URL(String(href), window.location.href);
  } catch {
    return null;
  }
  if (url.protocol !== 'https:') return null;

  const link = document.createElement('a');
  link.className = 'proposal-link';
  link.href = url.href;
  link.textContent = `${label} ↗`;
  return link;
}

function isActiveProposal(proposal) {
  return !TERMINAL_PROPOSAL_STATUSES.has(String(proposal.status || '').toLowerCase());
}

function proposalMetaItem(label, value) {
  const item = document.createElement('div');
  const labelNode = document.createElement('span');
  const valueNode = document.createElement('strong');
  labelNode.textContent = label;
  valueNode.textContent = value;
  item.append(labelNode, valueNode);
  return item;
}

function proposalElement(proposal) {
  const links = proposal.links || {};
  const article = document.createElement('article');
  article.className = 'proposal-card';

  const top = document.createElement('div');
  top.className = 'proposal-card-top';
  const status = document.createElement('span');
  status.className = 'proposal-status';
  status.textContent = proposalFormatStatus(proposal.status);
  const updated = document.createElement('span');
  updated.className = 'proposal-updated';
  updated.textContent = `Updated ${proposal.updated || 'unknown'}`;
  top.append(status, updated);

  const title = document.createElement('h3');
  title.textContent = proposal.title || 'Untitled proposal';

  const funder = document.createElement('p');
  funder.className = 'proposal-funder';
  funder.textContent = [proposal.funder, proposal.fund].filter(Boolean).join(' · ');

  const meta = document.createElement('div');
  meta.className = 'proposal-meta';
  meta.append(
    proposalMetaItem('Request', proposalAmount(proposal)),
    proposalMetaItem('Deadline', proposalFormatDeadline(proposal.deadline)),
  );

  const summary = document.createElement('p');
  summary.className = 'proposal-summary';
  summary.textContent = proposal.summary || '';

  const next = document.createElement('p');
  next.className = 'proposal-next';
  const nextLabel = document.createElement('strong');
  nextLabel.textContent = 'Next:';
  next.append(nextLabel, document.createTextNode(` ${proposal.next_action || 'No next action recorded.'}`));

  const actions = document.createElement('div');
  actions.className = 'proposal-actions';
  for (const [label, href] of [
    ['Proposal', links.proposal],
    ['Budget', links.budget],
    ['AI provenance', links.provenance],
    ['Call', links.source],
  ]) {
    const link = proposalLink(label, href);
    if (link) actions.appendChild(link);
  }

  article.append(top, title, funder, meta, summary, next, actions);
  return article;
}

async function loadProposals() {
  const grid = document.querySelector('#proposal-grid');
  const empty = document.querySelector('#proposal-empty-state');
  if (!grid || !empty) return;

  try {
    const response = await fetch('data/proposals.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const proposals = Array.isArray(data.proposals) ? data.proposals : [];
    proposalState.proposals = proposals.filter(isActiveProposal);
    grid.replaceChildren(...proposalState.proposals.map(proposalElement));
    empty.hidden = proposalState.proposals.length !== 0;
    const updated = document.querySelector('#proposal-data-updated');
    if (updated) updated.textContent = data.updated || 'unknown';
  } catch (error) {
    const message = document.createElement('p');
    message.className = 'empty-state';
    message.textContent = 'Proposal data could not be loaded. Use the public GitHub repository as the source of truth.';
    grid.replaceChildren(message);
    empty.hidden = true;
    console.error('Proposal data load failed:', error);
  }
}

loadProposals();
