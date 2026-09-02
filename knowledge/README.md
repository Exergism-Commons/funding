# Funding Governance Knowledge

This directory contains the canonical Git-native JSON-LD ABox for machine-readable funding governance.

## Authority

Records here are governance data, not self-executing legal instruments. A record with `status: approved` is evidence of a recorded EC governance outcome only when the corresponding institutional procedure was validly completed under the applicable statutes, policies and law.

The funding repository and its reviewed governance/release process remain authoritative for the meaning and status of these records. `id.exergism.org` provides their persistent public identity and dereferencing surface.

## Layout

- `decisions/` — material funding/treasury/compensation/Endowment governance records.
- `states/` — explicit, reviewable institutional funding states.

Non-canonical valid and invalid examples belong under `tests/fixtures/`, not here.

## Identity

The funding vocabulary namespace is:

```text
https://id.exergism.org/funding#
```

Canonical governance records use stable HTTP IRIs derived from their stable IDs:

```text
https://id.exergism.org/funding/id/ECF-DEC-MRG-BOOTSTRAP-001
ECF-DEC-MRG-BOOTSTRAP-001
```

For a canonical record, the IRI MUST equal:

```text
https://id.exergism.org/funding/id/{stableId}
```

This separates persistent identity from repository or hosting location. Git remains the authoritative editable history; changing GitHub, the resolver implementation or the hosting provider must not require changing the public identifier.

Test fixtures are deliberately non-canonical and may use non-public IRIs. They do not mint stable identifiers under `id.exergism.org`.

## Change discipline

Material history should not be erased by overwriting an old decision into a different outcome. Prefer a new record linked with `supersedes` when a later decision changes the institutional state.
