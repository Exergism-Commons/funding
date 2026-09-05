# Funding pipeline classification model

This document defines how Exergism Commons separates concrete external opportunities, EC proposals and strategic relationships.

## Core objects

### Opportunity

An **opportunity** is a concrete externally available or anticipated route for EC action. It is represented canonically in `data/opportunities.yaml` and may have a narrative dossier under `opportunities/<stable-id>.md`.

Examples:

- `nlnet-2026-09`
- `cost-open-call-2026`
- `msca-pf-2027`

Opportunity paths are stable. Lifecycle state MUST NOT be encoded in a directory such as `active/`, `closed/` or `archived/`, because moving a dossier when its state changes would break durable links.

External programme names such as NLnet Restack, COST Actions or Horizon Europe / MSCA may be recorded in the opportunity's `programme` metadata. They are descriptive attributes, not separate first-class repository objects.

### Proposal

A **proposal** is EC's concrete response to an opportunity. Proposals live under `proposals/<proposal-id>/` and MUST reference the opportunity they respond to through `opportunity_id`.

One opportunity may produce zero, one or multiple proposals. A proposal is therefore never the canonical source for call-level facts. Proposal metadata MUST NOT duplicate opportunity-owned facts such as the external funder, call deadline or primary call source. Public proposal projections resolve those values through `opportunity_id`, and generation MUST fail when the referenced opportunity does not exist.

Proposal lifecycle state is a controlled value. Current values are:

- `scoping` — the funded deliverable, amount or milestones are still being selected;
- `drafting` — the proposal is being actively prepared;
- `submitted` — the application has been submitted and is awaiting an outcome;
- `awarded` — the proposal succeeded;
- `rejected` — the proposal did not succeed.

`awarded` and `rejected` are terminal states and MUST NOT appear in the dashboard section labelled “Active proposals”. Unknown, missing or misspelled proposal states MUST fail projection generation instead of being treated as active.

### Partnership

A **partnership** is a durable institutional relationship or strategic network object, not necessarily a funding call. Partnership knowledge belongs under `partnerships/`.

A strategic engagement may still appear in the live institutional pipeline when EC has a concrete next action, but it MUST be typed accordingly rather than disguised as a funding call.

## Independent classification axes

Each pipeline entry is classified independently by:

### `kind`

What the entry is.

Current controlled values:

- `funding_call` — a dated call that can directly finance work;
- `network_call` — a dated call primarily aimed at building or financing a network/action;
- `strategic_engagement` — a concrete institutional/network route without a conventional grant call.

### `status`

Where the external opportunity is in its lifecycle.

Current controlled values:

- `forthcoming`
- `open`
- `continuous`
- `closed`
- `cancelled`

Proposal-specific lifecycle values are defined separately under the Proposal object and belong to proposal metadata, not opportunity metadata.

### `priority`

EC's internal attention priority, currently `P0`, `P1`, etc. Priority is not lifecycle state and does not change the identity or physical location of the opportunity.

## Canonicality and public projection

`data/opportunities.yaml` is the canonical structured opportunity registry.

Narrative dossiers provide analysis and context but MUST not silently override structured fields such as status, deadline, kind or priority.

`tools/build_dashboard_data.py` produces disposable JSON projections for the public dashboard. The checked-in generated files under `docs/data/` are validated by CI against the canonical YAML sources.

The dashboard preserves deadline cutoff times and their source UTC offsets instead of converting them to the browser's local timezone. Proposal metadata is rendered as text nodes, and proposal links are restricted to validated HTTPS URLs before insertion into the document.

## Relationship example

```text
opportunity: nlnet-2026-09
  programme: NLnet open technology grants
        ↓
proposal: nlnet-restack-2026
```

The opportunity records the external call and may name its external programme as metadata. The proposal records what EC intends to submit. They evolve independently and retain separate histories.
