const proposalStylesheet = document.createElement('link');
proposalStylesheet.rel = 'stylesheet';
proposalStylesheet.href = 'proposals.css';
document.head.appendChild(proposalStylesheet);

const proposalState = { proposals: [] };

function proposalFormatStatus(value) {
  return String(value || 'unknown').replaceAll('_', ' ');
}

function proposalFormatDate(value) {
  if (!value) return 'No deadline';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Unknown deadline';
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(date);
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
  return href ? `<a class="proposal-link" href="${href}">${label} ↗</a>` : '';
}

function proposalTemplate(proposal) {
  const links = proposal.links || {};
  return `
    <article class="proposal-card">
      <div class="proposal-card-top">
        <span class="proposal-status">${proposalFormatStatus(proposal.status)}</span>
        <span class="proposal-updated">Updated ${proposal.updated || 'unknown'}</span>
      </div>
      <h3>${proposal.title}</h3>
      <p class="proposal-funder">${proposal.funder || ''}${proposal.fund ? ` · ${proposal.fund}` : ''}</p>
      <div class="proposal-meta">
        <div><span>Request</span><strong>${proposalAmount(proposal)}</strong></div>
        <div><span>Deadline</span><strong>${proposalFormatDate(proposal.deadline)}</strong></div>
      </div>
      <p class="proposal-summary">${proposal.summary || ''}</p>
      <p class="proposal-next"><strong>Next:</strong> ${proposal.next_action || 'No next action recorded.'}</p>
      <div class="proposal-actions">
        ${proposalLink('Proposal', links.proposal)}
        ${proposalLink('Budget', links.budget)}
        ${proposalLink('AI provenance', links.provenance)}
        ${proposalLink('Call', links.source)}
      </div>
    </article>`;
}

async function loadProposals() {
  const grid = document.querySelector('#proposal-grid');
  const empty = document.querySelector('#proposal-empty-state');
  if (!grid || !empty) return;

  try {
    const response = await fetch('data/proposals.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    proposalState.proposals = Array.isArray(data.proposals) ? data.proposals : [];
    grid.innerHTML = proposalState.proposals.map(proposalTemplate).join('');
    empty.hidden = proposalState.proposals.length !== 0;
    const updated = document.querySelector('#proposal-data-updated');
    if (updated) updated.textContent = data.updated || 'unknown';
  } catch (error) {
    grid.innerHTML = '<p class="empty-state">Proposal data could not be loaded. Use the public GitHub repository as the source of truth.</p>';
    empty.hidden = true;
    console.error('Proposal data load failed:', error);
  }
}

loadProposals();
