# Funding Governance Knowledge

This directory contains the canonical Git-native JSON-LD ABox for machine-readable funding governance.

## Authority

Records here are governance data, not self-executing legal instruments. A record with `status: approved` is evidence of a recorded EC governance outcome only when the corresponding institutional procedure was validly completed under the applicable statutes, policies and law.

## Layout

- `decisions/` — material funding/treasury/compensation/Endowment governance records.

Non-canonical valid and invalid examples belong under `tests/fixtures/`, not here.

## Identity

Records use provider-independent `urn:ecf:` IRIs and stable IDs such as:

```text
urn:ecf:ECF-DEC-MRG-BOOTSTRAP-001
ECF-DEC-MRG-BOOTSTRAP-001
```

The IRI and `id` must agree. A later HTTP projection may resolve these identities through `id.exergism.org` without changing their canonical Git history.

## Change discipline

Material history should not be erased by overwriting an old decision into a different outcome. Prefer a new record linked with `supersedes` when a later decision changes the institutional state.
