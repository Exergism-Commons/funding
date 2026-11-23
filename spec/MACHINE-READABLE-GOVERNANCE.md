# Machine-Readable Funding Governance

> **Status: draft governance/data specification.** This layer validates explicit Funding-domain state and downstream authority constraints. It does not itself execute legal acts, payments, contracts, investments, employment decisions or institutional votes.

## 1. Objective

Exergism Commons (EC) treats funding as a governance domain rather than a private administrative function. Material funding, treasury, compensation and Endowment decisions should become inspectable records with machine-checkable invariants.

```text
Human policy / adopted Governance
        ↓
OWL 2 TBox                  vocabulary/domain semantics
        ↓
JSON-LD ABox                Git-native records
        ↓
SHACL + repository guards   structural/integrity constraints
        ↓
Derived RDF                 query/audit projection
        ↓
Git history                 review/provenance/persistence surface
```

The Git repository is the authoritative editable history. A future triplestore is an index, not the source of truth. Persistent public identity is provided by `id.exergism.org` and is independent of GitHub and resolver implementation.

## 2. Authority boundary

Four different things must not be conflated:

1. **Semantic inference** — what follows from the ontology.
2. **Structural/integrity validation** — whether RDF and repository state satisfy the encoded profile.
3. **Required decision class** — which Governance process a Funding proposal would require.
4. **Authoritative institutional decision** — evidence that the competent EC process actually validly approved/rejected/activated the proposal.

`ecg:decisionClass ecg:QualifiedApproval` means **qualified approval is required**. It does not prove quorum, electorate, votes, recusals, signatures, adoption or legal effectiveness.

The pinned Governance downstream-authority snapshot currently identifies institutional Governance version `0.1-DRAFT` as `operative: false` and reports no supported operative-decision authority validator. Funding therefore operates **fail closed**: hosted Governance decisions must remain `status="proposed"` and `operative=false`. If Governance later becomes operative, Funding CI intentionally fails until a supported authority-evidence integration is reviewed and added.

A SHACL pass therefore never means money moved, a grant was legally accepted, compensation was lawfully authorised, an investment is suitable, or an Endowment withdrawal is legally permitted.

`id.exergism.org` is an identifier/publication authority, not a second semantic or governance authority.

## 3. Namespace, versioning and dependency closure

```text
Vocabulary namespace:  https://id.exergism.org/funding#
Ontology IRI:          https://id.exergism.org/ontology/funding
Version IRI:           https://id.exergism.org/ontology/funding/0.2.0-pre1
Record base:           https://id.exergism.org/funding/id/
```

Funding `0.2.0-pre1` imports owner-authored immutable version IRIs:

- `https://id.exergism.org/ontology/commons/0.1-PRE2`
- `https://id.exergism.org/ontology/governance/0.1-PRE2`

The Git provenance root for the consumed Commons/Governance profile is `Exergism-Commons/governance@517c0df4c905c79ec2b2824231b40ccaa6a1b510`.

Vendored dependencies:

- `ontology/dependencies/commons.ttl`
- `ontology/dependencies/governance.ttl`
- `ontology/dependencies/governance-shapes.ttl`
- `ontology/dependencies/downstream-authority.json`
- `ontology/dependencies/manifest.json`

The provenance workflow fetches the declared Governance commit and requires exact coverage of every consumed dependency plus exact upstream Git-blob equality. Vendoring is for deterministic offline validation; it does not transfer semantic ownership to Funding.

Funding validation composes:

- `ontology/funding.shacl.ttl` — Funding-domain structural constraints;
- `ontology/funding-authority.shacl.ttl` — downstream fail-closed/hosting/ownership constraints;
- the pinned Governance structural SHACL profile.

Ontology triples are present for explicit type/subclass checks, but general RDFS entailment is disabled so `rdfs:domain`/`rdfs:range` cannot manufacture types that `sh:class` is intended to validate.

## 4. Persistent records and history

A canonical record with stable ID `ECF-DEC-EXAMPLE-001` has IRI:

```text
https://id.exergism.org/funding/id/ECF-DEC-EXAMPLE-001
```

Every canonical document under `knowledge/` carries a stable `id`, exact corresponding `@id` and non-empty provenance. Public identifiers are append-only/supersession-oriented: once the persistence contract exists, CI walks Git transitions and rejects silent deletion or mutation of previously published canonical records. Material state changes should be expressed through a new record linked by `supersedes`.

Opportunity IDs derived from `data/opportunities.yaml` are also treated as persistent once established. The builder rejects cross-source stable-ID collisions between derived opportunities and `knowledge/**` records.

The historical `ECF-DEC-MRG-BOOTSTRAP-001` record retains its original JSON-LD interpretation through a frozen legacy context. The normalization is expressed by a later record rather than retrospectively changing the RDF meaning of PID 001.

## 5. FundingOpportunity

A candidate funding/network opportunity can be `rankEligible: true` only when every Expected Institutional Value dimension is explicitly present. Positive dimensions are `fit`, `fundingValue`, `capabilityValue`, `strategicOptionality`, `autonomyValue`, `networkValue`, `recurrence`; negative dimensions are `captureRisk`, `adminCost`, `executionRisk`.

Each score is `[0,1]`. Missing values are not defaulted. Completeness never implies approval.

## 6. FundingAcceptanceDecision

A Funding acceptance proposal must identify:

- the exact `FundingOpportunity`;
- the exact `Funder` whose concentration is being measured;
- amount/currency/restriction status;
- institutional phase and dependency state;
- post-award rolling-24-month total income;
- post-award rolling-24-month income attributable to that funder;
- concentration window end date;
- repository evidence path plus SHA-256 binding;
- anti-capture control flags.

The author-entered `singleFunderConcentrationAfter`, when present, is only a checked projection. Threshold logic is computed from the evidence-backed numerator/denominator:

```text
single * 10 <= total * 3   → <= 30%
single * 10 >  total * 3   → > 30%
single * 2  >  total       → > 50%
```

Additional consistency rules prevent single-funder income exceeding total income and require the accepted amount not to exceed the post-award income attributed to that funder.

### Dependency classes

- `DiversifiedState` — concentration `<= 30%`;
- `ElevatedConcentrationState` — `>30%` and `<=50%`;
- `StrategicDependencyState` — `>50%`.

Above 30%, an explicit `DiversificationPlan` is required. A plan is not a placeholder: it requires an accountable owner, one or more actions, a target date and a review date.

Above 50%, `ecg:QualifiedApproval` is the required decision class. Under current non-operative Governance that remains a **requirement classification on a proposal**, not evidence that qualified approval has occurred.

No funding proposal may grant governance power for money, EC-wide IP ownership, or exclusive core-infrastructure rights through the encoded acceptance flags.

## 7. Bootstrap and review deadlines

Institutional maturity and funding dependency are separate axes. EC may be simultaneously:

```text
BootstrapState + StrategicDependencyState
```

A first material funder may therefore account for 100% of rolling income without making the proposal intrinsically invalid, provided the dependency is explicit, an accountable diversification plan exists, QualifiedApproval is identified as required, and anti-capture firewalls remain intact.

Canonical records carrying `reviewDue` are checked against an explicit evaluation date. An overdue canonical review fails CI. Tests can override the evaluation date for reproducibility. A plan's review date may not fall after its target date.

This converts `reviewDue` from documentation into a fail-closed repository obligation.

## 8. Evidence binding

Canonical concentration evidence is content-addressed. If a canonical record declares concentration evidence:

- the path must be repository-relative and cannot escape the repository;
- the file must exist;
- the declared SHA-256 must be valid hex and match the exact bytes.

Synthetic fixture paths/hashes are allowed in non-canonical adversarial fixtures because they are test data, not persistent public records.

Generic `ec:provenance` remains descriptive metadata; Git history plus specialized content-addressed evidence bindings provide stronger integrity where policy requires it.

## 9. CompensationDecision

Compensation represents remuneration for real work, not membership-derived ownership. Required data include beneficiary, work basis, amount/currency and conflict declaration. The beneficiary must be named as interested party; if they have a recorded vote on their own compensation it must be `abstain`.

Votes/conflicts use Governance-owned IRIs. Funding does not define a competing vote vocabulary or membership-economic-share predicate.

## 10. EndowmentPrincipalWithdrawalDecision

The structural Funding profile requires a positive principal-withdrawal amount, explicit purpose, exceptional condition and `QualifiedApproval` requirement classification.

Under current Governance this record still remains proposed/non-operative; the decision-class label does not manufacture actual approval.

## 11. Vocabulary ownership boundary

Funding owns Funding-domain classes/properties only. Commons owns shared identity/provenance primitives; Governance owns institutional decisions, decision classes, membership, votes, conflicts, delegations and roles.

CI enforces this at several layers:

- Funding TBox may not redeclare known moved shared/Governance terms;
- Funding may not mint a local class/property name already declared by Commons/Governance;
- hosted ABox data may use `funding#` predicates/classes only if actually declared by the Funding ontology;
- a Funding domain record cannot simultaneously masquerade as Governance Vote/Conflict/Delegation/Membership infrastructure.

This prevents normalization from being undone by either schema or data.

## 12. Governance authority drift

Funding vendors `downstream-authority.json` from Governance and tests its contract explicitly. Current assumptions include:

- institutional version `0.1-DRAFT`;
- Governance non-operative;
- no operative downstream authority verifier;
- proposed records allowed;
- approved/operative records not authoritative;
- EmergencyAction unavailable without an adopted emergency policy.

If those upstream facts change, Funding intentionally fails closed until its authority integration is reviewed. A dependency update must not silently turn a structural record into an operative decision.

## 13. Publication contract

`funding` remains semantic authority for Funding-specific material; `id` only publishes persistent representations. Adoption is staged:

1. `id#8` publishes adopted Commons/Governance namespace documents, owner-authored version IRIs, authority profile and catalogs.
2. Funding #8 lands, making Funding `0.2.0-pre1` authoritative in `funding/main`.
3. The resolver publication PR is rebuilt from the resulting `id/main`, repinned to the **actual Funding main commit** (not the pre-squash PR head), and its publication artifacts are content-addressed against that source.
4. Only then may Funding switch from `migrating` to `adopted` in the resolver catalog.
5. Deployment/dereferencing smoke tests complete the cross-repository publication; merge alone is not treated as deployment.

Funding public JSON-LD publication must use immutable/versioned contexts for historical meaning. A mutable “current” context must never retroactively change RDF semantics of already-published record bytes.

## 14. What remains outside this profile

Future work may add agreement/restriction clause semantics, treasury liquidity buckets, Endowment spending rules, richer real-world entity identifiers, and an operative Governance authority-evidence verifier once Governance adopts one.

Those capabilities must be added by the owning semantic/governance layer rather than inferred from repository permissions or Funding labels.

## 15. Design rule

**If a policy matters enough to constrain institutional money or power, the relevant state should be explicit, reviewable and mechanically testable — without pretending that code, RDF or a decision-class label replaces governance.**
