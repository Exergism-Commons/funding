# Machine-Readable Funding Governance

> **Status: draft governance/data specification.** This repository layer validates the structure and policy-conformance of funding records. It does not itself execute legal acts, payments, contracts, investments or employment decisions.

## 1. Objective

Exergism Commons (EC) treats funding as a governance domain rather than a private administrative function. Material funding, treasury, compensation and Endowment decisions should become inspectable records with machine-checkable invariants.

The initial semantic stack mirrors the architecture already used elsewhere in EC:

```text
Human policy / governance documents
        ↓
OWL 2 TBox                 domain semantics
        ↓
JSON-LD ABox               concrete Git-native records
        ↓
SHACL                      closed policy/integrity constraints
        ↓
Derived RDF / SPARQL       query, audit and dependency analysis
        ↓
GitHub review              public change/provenance surface
```

The Git repository is the authoritative editable history. A future triplestore is an index, not the source of truth.

## 2. Authority boundary

Three different things must never be conflated:

1. **Semantic inference** — what follows safely from the ontology.
2. **Validation** — whether a proposed repository state satisfies SHACL constraints.
3. **Governance decision** — an institutional act taken by the competent EC body under the statutes, applicable law and the relevant governance procedure.

A SHACL pass means only that the machine-readable record is structurally and procedurally compatible with the encoded policy profile. It does **not** mean that a grant has legally been accepted, a salary has been lawfully authorised, money has moved, an investment is suitable, or an Endowment withdrawal is legally permitted.

Likewise, a SHACL failure means the repository state conflicts with an encoded invariant. It is a governance-integrity failure, not an automatic legal conclusion.

## 3. Namespace and artifacts

The initial namespace is:

```text
urn:ecf:
```

Artifacts:

- `ontology/funding.owl.ttl` — OWL TBox;
- `ontology/funding-context.jsonld` — Git-native JSON-LD context;
- `ontology/funding.shacl.ttl` — canonical closed constraints;
- `knowledge/` — canonical ABox records;
- `tests/fixtures/` — deliberately valid/invalid non-canonical records;
- `tests/test_machine_governance.py` — semantic integrity test suite;
- `.github/workflows/machine-governance-integrity.yml` — CI enforcement.

`urn:ecf:` is deliberately provider-independent. A later persistent HTTP identifier projection may be added under `id.exergism.org` without making GitHub or the funding website the semantic authority.

## 4. Initial domain model

### FundingOpportunity

Represents a candidate financing/network opportunity. A record can be marked `rankEligible: true` only if every Expected Institutional Value (EIV) dimension is explicitly present:

Positive dimensions:

- `fit`
- `fundingValue`
- `capabilityValue`
- `strategicOptionality`
- `autonomyValue`
- `networkValue`
- `recurrence`

Negative dimensions:

- `captureRisk`
- `adminCost`
- `executionRisk`

Every dimension is constrained to `[0,1]`. Missing values are not defaulted. SHACL validates completeness but does not infer a ranking or funding decision.

### FundingAcceptanceDecision

Represents a proposal/decision concerning acceptance of material funding. Initial hard invariants include:

- no governance right may be granted merely in exchange for funding;
- no EC-wide IP ownership may be granted to the funder;
- no exclusive right over core EC infrastructure may be granted;
- post-award single-funder concentration must be explicit;
- institutional phase and dependency state must be explicit;
- concentration above 30% requires an explicit `DiversificationPlan`;
- concentration above 50% requires `qualified` approval.

The thresholds encode the current anti-capture policy. Changing them is a governance change and should be reviewed as such.

### Funding phase and dependency states

Institutional maturity and funding dependency are **two separate semantic axes**.

Funding phase:

- `BootstrapState` — EC is in an explicitly temporary early financing phase;
- `NormalState` — EC is no longer relying on the bootstrap designation.

Dependency state:

- `DiversifiedState` — single-funder concentration is `<= 30%`;
- `ElevatedConcentrationState` — concentration is `> 30%` and `<= 50%`;
- `StrategicDependencyState` — concentration is `> 50%`.

This separation is deliberate. EC can simultaneously be:

```text
BootstrapState
+
StrategicDependencyState
```

For example, the first material grant can represent 100% of recorded funding. That state is not automatically forbidden. A 100% bootstrap decision can conform when:

- the dependency is explicitly represented as `StrategicDependencyState`;
- a `DiversificationPlan` exists;
- approval is `qualified`;
- no governance/IP/core-infrastructure control is granted to the funder; and
- the bootstrap/dependency state has an explicit review date.

Thus the machine policy distinguishes:

```text
dependency detected != funding prohibited
```

from:

```text
dependency hidden or unmanaged = governance-integrity failure
```

SHACL checks that the asserted dependency-state class matches the numeric concentration. A 100% decision cannot claim `DiversifiedState` merely because EC is in bootstrap.

The ontology does **not** infer a state individual from a percentage. The state remains an explicit, reviewable governance record; SHACL checks consistency between that record and the quantitative input.

### CompensationDecision

Represents remuneration for real work rather than an economic entitlement arising from membership.

Initial invariants include:

- beneficiary, work basis, amount and currency are explicit;
- at least one conflict disclosure is linked;
- the beneficiary is named as an interested party;
- if the beneficiary has a recorded vote on their own compensation, it must be `abstain`.

The model deliberately does not infer employment status, tax treatment or the legality of a specific contractual form.

### EndowmentPrincipalWithdrawalDecision

Represents a proposal to consume principal rather than ordinary Endowment distributions.

The initial machine policy requires:

- positive withdrawal amount;
- explicit purpose;
- an exceptional condition;
- `qualified` approval.

These are governance safeguards, not investment advice and not a substitute for tax/accounting/legal review.

## 5. Explicitly forbidden state

`ecf:membershipEconomicShare` exists only as a detectable forbidden predicate. Any canonical record asserting a distributable economic share because of membership fails SHACL validation.

This makes the repository distinction machine-checkable:

```text
membership ≠ ownership claim
work       → may support compensation
capital    → belongs to EC
```

## 6. Decision lifecycle

Recommended lifecycle for a material decision:

```text
record proposed
  ↓
PR opened with dossier/evidence
  ↓
JSON-LD parses as RDF
  ↓
OWL/SHACL integrity passes
  ↓
human governance review
  ↓
competent body approves/rejects
  ↓
record status updated
  ↓
Git history preserves provenance
```

A decision record should not be rewritten to erase a prior material outcome. Use `supersedes` for later records when the institutional state changes materially.

Institutional funding-state records are also time-bounded review artifacts. `BootstrapState`, in particular, must have a `reviewDue`; it must not silently persist forever because EC was once young or small.

## 7. What should become machine-readable next

The v0.1 profile is intentionally narrow. Candidate next layers are:

1. funding agreements and restriction clauses;
2. donor/funder identities and rolling concentration calculations;
3. reserve and Endowment allocation decisions;
4. annual Endowment spending-rule computation;
5. treasury liquidity buckets;
6. conflicts/recusals and quorum/majority profiles sourced from `governance`;
7. immutable governance snapshots binding policy versions to decisions;
8. SPARQL dependency checks showing which decisions become stale when a policy or funding condition changes;
9. formal bootstrap exit criteria once EC has enough financial history to calibrate them;
10. projection of persistent identifiers through `id.exergism.org`.

## 8. Cross-repository governance

The funding ontology is not the constitution of EC and is not an extension of the ECL software licence. Institutional authority should remain in the EC governance layer.

The intended dependency direction is:

```text
EC governance / statutes
        ↓
funding policies and machine profile
        ↓
funding records and decisions
```

ECL and other EC projects may reuse the same semantic-governance patterns, but a software licence must not silently acquire authority over salaries, treasury or the Endowment.

## 9. Design rule

**If a policy matters enough to constrain institutional money or power, EC should aim to make the relevant state explicit, reviewable and mechanically testable — without pretending that code replaces governance.**
