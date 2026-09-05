# Funding Governance Ontology

This directory implements the funding-domain semantic layer for Exergism Commons.

- `funding.owl.ttl` — OWL 2 TBox for funding-specific semantics.
- `funding-context.jsonld` — JSON-LD context that composes Funding with shared EC and Governance terms.
- `funding.shacl.ttl` — repository/policy validity constraints for funding records.

Persistent identifiers:

- Funding vocabulary namespace: `https://id.exergism.org/funding#`
- Funding ontology IRI: `https://id.exergism.org/ontology/funding`
- canonical Funding records: `https://id.exergism.org/funding/id/{stableId}`

Dependencies used by this pre-1.0 normalization:

- shared EC primitives: `https://id.exergism.org/commons#`
- institutional governance: `https://id.exergism.org/governance#`

The Funding repository remains authoritative only for funding-specific semantics. It intentionally does **not** redefine generic `Actor`, `Person`, `Organization`, `GovernanceRecord`, `GovernanceDecision`, `Vote`, conflict, identity or provenance terms. Those are reused from the shared/Governance vocabularies once their corresponding draft architecture is adopted.

The local JSON-LD keys `GovernanceDecision`, `Vote`, `ConflictDisclosure`, `approvalClass`, `hasVote`, `voter` and similar names are compatibility/convenience terms in the JSON-LD context. They expand to `governance#` IRIs, not `funding#` IRIs.

These identifiers are issued under the shared Exergism Commons identifier authority. `id.exergism.org` provides persistence and dereferencing rather than becoming a second semantic source.

## Reasoning boundary

OWL describes classes and properties but deliberately does not infer approvals, vote outcomes, funding acceptance, compensation entitlement, Endowment withdrawals or economic rights.

SHACL checks explicit Funding states. A validation failure means the encoded state conflicts with the current machine-readable policy profile. It is not a self-executing legal judgment.

Membership and organization-wide economic-ownership constraints belong to Governance rather than Funding. Funding may enforce a funding-specific consequence of such a rule only when the rule itself is owned by Governance.

See `../spec/MACHINE-READABLE-GOVERNANCE.md` and the cross-project semantic architecture in `Exergism-Commons/governance/SEMANTIC-ARCHITECTURE.md`.
