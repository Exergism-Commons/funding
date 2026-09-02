# Funding Governance Ontology

This directory implements the semantic layer for Exergism Commons funding governance.

- `funding.owl.ttl` — OWL 2 TBox: domain semantics only.
- `funding-context.jsonld` — JSON-LD context for Git-native governance records.
- `funding.shacl.ttl` — closed repository/policy validity constraints.

Namespace: `urn:ecf:`.

## Reasoning boundary

OWL describes classes and properties but deliberately does not infer approvals, vote outcomes, funding acceptance, compensation entitlement, Endowment withdrawals or economic rights.

SHACL checks explicit repository states. A validation failure means the encoded state conflicts with the current machine-readable policy profile. It is not a self-executing legal judgment.

See `../spec/MACHINE-READABLE-GOVERNANCE.md`.
