# Exergism Commons Funding

Public funding intelligence and institutional-capacity repository for **Exergism Commons (EC)**.

**Website:** https://funding.exergism.org

EC does not optimise for the largest possible grant. It optimises for **durable autonomous capacity**: money, people, infrastructure, legitimacy, knowledge, networks and institutionally owned capital, while minimising capture, dependency and administrative drag.

## Objectives

1. Diversify revenue across public, philanthropic, community and earned-income sources.
2. Build enough unrestricted/core funding for EC to say **no** to misaligned funders.
3. Use grants not only for deliverables, but to accumulate reusable institutional capability.
4. Build European and international research, open-source and public-sector networks.
5. Keep funding conditions and conflicts transparent.
6. Prevent any funder from obtaining governance, roadmap or IP control over EC.
7. Build an **EC Endowment** so that a growing share of future activity can be financed from capital EC already owns and controls.
8. Make material funding governance increasingly **machine-readable, auditable and reproducible**.

## Portfolio model

EC should deliberately combine:

- European R&I funding — Horizon Europe, MSCA.
- European deployment/network funding — Digital Europe, COST and related programmes.
- Open-source and digital-commons grants — NLnet and comparable foundations.
- National and regional public funding.
- Research and philanthropic foundations.
- Institutional sponsorships and memberships.
- Community funding and donations.
- Contracts, training and services consistent with EC's mission.
- Strategic reserves for continuity and refusal capacity.
- **EC Endowment** — long-duration institutional capital designed to compound and support recurring mission expenditure.

No single category should become synonymous with EC's survival.

## Capital architecture

EC distinguishes three financial pools:

1. **Operating Treasury** — current and near-term obligations.
2. **Strategic Reserve** — liquid resilience capital, progressively targeting 3, 6 and ultimately 12 months of core operating expenses.
3. **EC Endowment** — permanent or very long-duration institutional capital intended to compound and finance future EC activity through a controlled spending rule.

The Endowment belongs to EC. Membership does not create an economic claim on it.

People may be compensated for genuine work performed for EC under applicable law and EC governance, but compensation is not a distribution of membership ownership, surplus or Endowment returns.

See:

- `strategy/endowment-policy.md`
- `strategy/treasury-strategy.md`
- `strategy/compensation-principles.md`
- `strategy/anti-capture-policy.md`

## Machine-readable governance

Funding is now also implemented as a semantic governance domain rather than only a collection of prose policies.

```text
policies / EC governance
        ↓
OWL TBox
        ↓
JSON-LD governance records + live opportunity registry
        ↓
SHACL policy/integrity constraints
        ↓
derived RDF
        ↓
GitHub Actions enforcement
```

Current machine-checkable invariants include:

- rank-eligible opportunities require all ten EIV dimensions explicitly in `[0,1]`;
- funding cannot grant governance rights merely in exchange for money;
- funding cannot grant EC-wide IP ownership or exclusive control of core infrastructure;
- post-award single-funder concentration above 30% requires a diversification plan;
- concentration above 50% requires qualified approval;
- a compensation beneficiary cannot cast a substantive vote on their own compensation;
- Endowment principal withdrawal requires an exceptional condition and qualified approval;
- membership cannot be represented as a distributable economic share in EC.

The machine layer does **not** replace institutional authority. Human governance/policy remains authoritative; SHACL implements a reviewable subset of those rules. If prose policy and executable constraints diverge, the divergence must be resolved explicitly rather than silently treating code as supreme.

See `spec/MACHINE-READABLE-GOVERNANCE.md`.

## Repository structure

- `strategy/` — portfolio design, independence, treasury, Endowment and compensation principles.
- `opportunities/` — actionable calls and monitored opportunities.
- `programmes/` — persistent knowledge about recurring funding programmes.
- `partnerships/` — strategic networks and institutions relevant to funding and expansion.
- `proposals/` — proposal work products when appropriate for public development.
- `data/` — canonical structured opportunity registry.
- `knowledge/` — canonical Git-native JSON-LD governance records.
- `ontology/` — OWL TBox, JSON-LD context and SHACL constraints.
- `spec/` — machine-readable governance/data specifications.
- `tools/` — deterministic graph builders and integrity tooling.
- `tests/` — positive and adversarial governance fixtures.
- `docs/` — static public dashboard served at `funding.exergism.org`.

## Evaluation principle

Funding opportunities are evaluated by **institutional value**, not grant size alone. Relevant dimensions include:

- mission and technical fit;
- expected funding and probability;
- autonomy value;
- capture risk;
- administrative burden;
- networking value;
- reusable capability created;
- recurrence and follow-on potential;
- time to decision and cash-flow implications.

See `strategy/funding-strategy.md` and `strategy/anti-capture-policy.md` for the operating model.

## Current priorities

1. NLnet calls opening 2026-09-03 — identify a concrete open-technology proposal.
2. Digital Commons EDIC — establish EC as a visible stakeholder in the European digital-commons network.
3. Horizon Europe 2027 — enter consortia where EC can own governance/IP/semantics/commons work.
4. MSCA Postdoctoral Fellowships 2027 — assess EC as a host organisation and identify suitable researcher/supervision architecture.
5. COST Open Call 2026 — assess a European network around digital commons governance.
6. Build recurring unrestricted funding through sponsorship, membership, donations and mission-aligned services.
7. Build the legal, accounting and governance foundations required for an eventual EC Endowment.
8. Expand the machine-readable governance profile from validation into versioned decision, concentration, treasury and Endowment audit trails.

## Status

This repository is intentionally public. Funding is treated as part of EC governance and institutional architecture, not as a private grant-shopping process.
