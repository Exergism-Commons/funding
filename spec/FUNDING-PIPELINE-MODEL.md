# Funding pipeline classification model

This document defines how Exergism Commons separates persistent funding knowledge, concrete external opportunities, EC proposals and strategic relationships.

## Core objects

### Programme

A **programme** is a persistent or recurring funding/network mechanism whose identity survives individual call rounds.

Examples:

- Marie Skłodowska-Curie Actions / Postdoctoral Fellowships
- COST
- NLnet Restack Fund

Persistent programme knowledge belongs under `programmes/`. Programme files should describe recurring rules, institutional characteristics, recurring eligibility patterns and reusable knowledge rather than one dated call instance.

### Opportunity

An **opportunity** is a concrete externally available or anticipated route for EC action. It is represented canonically in `data/opportunities.yaml` and may have a narrative dossier under `opportunities/<stable-id>.md`.

Examples:

- `nlnet-2026-09`
- `cost-open-call-2026`
- `msca-pf-2027`

Opportunity paths are stable. Lifecycle state MUST NOT be encoded in a directory such as `active/`, `closed/` or `archived/`, because moving a dossier when its state changes would break durable links.

### Proposal

A **proposal** is EC's concrete response to an opportunity. Proposals live under `proposals/<proposal-id>/` and MUST reference the opportunity they respond to through `opportunity_id` when such an opportunity exists.

One opportunity may produce zero, one or multiple proposals. A proposal is therefore never the canonical source for call-level facts.

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

Proposal-specific states such as `scoping`, `drafting`, `submitted`, `awarded` or `rejected` belong to proposal metadata, not opportunity metadata.

### `priority`

EC's internal attention priority, currently `P0`, `P1`, etc. Priority is not lifecycle state and does not change the identity or physical location of the opportunity.

## Canonicality and public projection

`data/opportunities.yaml` is the canonical structured opportunity registry.

Narrative dossiers provide analysis and context but MUST not silently override structured fields such as status, deadline, kind or priority.

`tools/build_dashboard_data.py` produces disposable JSON projections for the public dashboard. The checked-in generated files under `docs/data/` are validated by CI against the canonical YAML sources.

## Relationship example

```text
programme: NLnet Restack Fund
        ↓
opportunity: nlnet-2026-09
        ↓
proposal: nlnet-restack-2026
```

The opportunity records the external call. The proposal records what EC intends to submit. They evolve independently and retain separate histories.
