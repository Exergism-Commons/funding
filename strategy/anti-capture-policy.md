# Funding Anti-Capture Policy

## Objective

Funding must increase the practical freedom of Exergism Commons (EC), not convert financial dependence into external governance.

This policy defines default safeguards. Specific legal obligations and grant agreements may require stricter controls.

## 1. No governance-for-money

EC should not grant a funder, sponsor or customer automatic rights to appoint/remove governance members, obtain voting power merely by funding EC, veto EC-wide decisions, control EC's general roadmap, compel unrelated institutional positions, or obtain privileged ownership of EC-wide assets/governance infrastructure.

Any exceptional arrangement with governance implications requires explicit governance review and public disclosure.

## 2. IP firewall

Default position:

- pre-existing EC IP remains under EC/project governance;
- funders do not receive ownership merely by funding work;
- project outputs should remain as open and reusable as the relevant EC project requires;
- exclusive rights should be treated as high capture risk;
- agreements must clearly distinguish background IP, project results and third-party rights.

## 3. Concentration limits

Long-term target:

- no single funder should represent more than **30% of rolling 24-month income**;
- preferred mature-state target: **<20–25%**;
- concentration above 30% triggers a diversification plan;
- concentration above 50% is treated as a strategic dependency even if formally temporary.

These thresholds diagnose dependency and determine governance safeguards. They are **not automatic prohibitions on accepting funding**.

Machine validation does not trust an author-entered percentage. A Funding acceptance record identifies the relevant funder and supplies the post-award rolling-24-month total income, that funder's rolling income, the window end date and a content-addressed evidence reference. Threshold classification is calculated from those amounts. `singleFunderConcentrationAfter`, when present, is only a checked projection and is not authoritative input.

### Bootstrap treatment

EC may begin with one material funder. In that case the funder can temporarily represent **100% of recorded funding** without making the acceptance intrinsically invalid.

Bootstrap does not hide or waive dependency. A materially concentrated bootstrap proposal must:

1. explicitly identify EC as being in a `BootstrapState`;
2. classify concentration above 50% as a `StrategicDependencyState`;
3. include a documented, accountable diversification plan when concentration exceeds 30%;
4. identify `QualifiedApproval` as the required Governance decision class when concentration exceeds 50%;
5. preserve the no-governance-for-money and IP/infrastructure firewalls; and
6. carry review dates so bootstrap/dependency/plan state cannot become an indefinite unreviewed exception.

`QualifiedApproval` is a **process requirement**, not evidence that qualified approval occurred. Under the current `0.1-DRAFT` Governance profile there is no operative downstream authority verifier, so Funding records remain proposed and non-operative. An approved/operative Funding decision will require explicit evidence validated by a supported Governance authority mechanism before Funding may represent it as authoritative.

The key distinction is:

> **dependency detected ≠ funding prohibited**

but:

> **dependency hidden or unmanaged = governance defect**

Institutional maturity and funding dependency are separate axes. EC can therefore be simultaneously in `BootstrapState` and `StrategicDependencyState`.

The machine-readable profile uses these dependency classes:

- `DiversifiedState` — single-funder concentration at or below 30%;
- `ElevatedConcentrationState` — concentration above 30% and at or below 50%;
- `StrategicDependencyState` — concentration above 50%.

A future governance revision may replace or refine the bootstrap exit criteria. The current profile records bootstrap explicitly instead of inferring a permanent exception from age, revenue or founder status.

## 4. Unrestricted/core revenue

Long-term target: at least **30% of annual income** should be unrestricted or sufficiently flexible core revenue.

Potential sources include memberships, donations, recurring sponsorship without governance rights, mission-aligned services, training/support and lawful reserve/Endowment distributions. The strategic purpose of core revenue is the institutional capacity to refuse misaligned funding.

## 5. Reserve and permanent-capital target

EC should progressively build three months, six months and eventually twelve months of operating expenses, plus an **EC Endowment** that converts part of unrestricted surplus into permanent or very long-duration institutional capital.

Restricted grant funds must not be treated as free reserves or Endowment capital unless the relevant agreement expressly permits that use. The Endowment is governed separately under `endowment-policy.md`.

## 6. Transparency registry

Material funding should be publicly recorded with, where legally possible: funder, amount/range, period, restricted status, purpose, deliverables, reporting/audit obligations, IP conditions, governance/advisory rights, conflicts, subcontracting constraints and material termination/clawback conditions.

Sensitive personal, banking and security information must not be published.

## 7. Conflict management

A person with a material personal interest in a funding, investment or compensation decision should disclose it and abstain where appropriate and practicable.

Examples include a member whose employer is the funder, a researcher deciding their own compensation, a governance member negotiating a related-party contract, or a decision-maker with a financial interest in an Endowment counterparty.

Where every active member is conflicted because all are also workers, EC should rely on objective compensation formulas, benchmarking, written rationale and additional review rather than treating the conflict as nonexistent.

## 8. No private ownership through membership

Membership in EC must not function as an economic share in the organisation. Members do not acquire an automatic right to annual surplus, reserves, Endowment principal/returns or revenue in proportion to voting/membership status.

EC may compensate members for genuine work under applicable law and a documented compensation policy, but **work -> compensation** must remain distinct from **membership -> distribution**.

The membership/economic-ownership invariant belongs to organization Governance, not to the Funding namespace. Funding must not mint a duplicate local term to express it.

See `compensation-principles.md`.

## 9. Endowment anti-capture rule

No donor, sponsor, external asset manager or financial institution obtains institutional control merely because it contributes to or manages Endowment assets.

Endowment arrangements should avoid donor governance rights unrelated to a narrow restriction, investment-like ownership claims, permanent exclusivity, mission-distorting conditions, avoidable single-counterparty dependency and private claims on EC capital by members/founders.

Material restrictions on Endowment gifts should be accepted only after explicit governance review.

## 10. Mission distortion test

Before accepting material funding, EC should ask whether EC would pursue substantially this work without this funder, whether reusable capability remains afterwards, whether public/scientific integrity is preserved, whether EC can walk away, whether the agreement weakens future autonomy, and whether surplus/reusable capability strengthens EC after the funded period.

A negative answer does not automatically reject funding, but raises the required level of governance scrutiny.

## 11. Exitability

Funding relationships should be designed so EC can terminate or decline renewal without losing control of its identity, core repositories, governance, domains, trademarks, essential infrastructure, pre-existing IP, community channels, unrestricted reserves or Endowment capital.

## 12. Machine-readable enforcement profile

A reviewable subset of this policy is represented by the composed profile:

- `ontology/funding.shacl.ttl` — Funding-domain structural rules;
- `ontology/funding-authority.shacl.ttl` — downstream fail-closed authority/integrity rules;
- the pinned Governance structural SHACL dependency;
- the pinned Governance downstream-authority snapshot.

The executable profile currently enforces, among other invariants:

- Funding reuses Commons/Governance terms rather than reintroducing moved `funding#` vocabulary in TBox or hosted ABox data;
- Funding-hosted decisions remain `proposed`, `operative=false` and bound to institutional Governance version `0.1-DRAFT` while Governance is non-operative;
- `EmergencyAction` cannot be used without an adopted emergency policy;
- no governance-for-money, EC-wide IP transfer or exclusive core-infrastructure-control flags on funding acceptance records;
- every acceptance identifies the exact `Funder` to which its single-funder concentration evidence applies;
- rolling-24-month concentration thresholds are calculated from evidence-backed amounts rather than trusting a self-asserted ratio;
- evidence-bearing canonical records bind evidence by repository path and SHA-256;
- an explicit institutional phase and dependency state for acceptance records;
- dependency-state classification consistent with evidence-backed concentration;
- an accountable diversification plan above 30%, including owner, actions, target and review date;
- `QualifiedApproval` as the **required process class** above 50%, without treating that label as proof the process passed;
- compensation conflict disclosure and beneficiary abstention;
- enhanced safeguards for Endowment principal withdrawal;
- canonical IDs/history are append-only/supersession-oriented rather than silently rewritten;
- review deadlines fail closed once overdue.

The human policy and adopted organization Governance remain authoritative. SHACL is a machine-checkable projection and structural gate, not an independent constitution and not evidence that a vote or legal act occurred. A divergence between policy, Governance authority state and executable shapes is itself a review defect and must be resolved explicitly.

See `spec/MACHINE-READABLE-GOVERNANCE.md`.

## 13. Strategic principle

**The correct measure of funding quality is not how much control EC gains over money, but how much durable freedom EC gains after accepting it.**

A mature EC should be progressively harder to capture because part of its future operating capacity is financed by diversified recurring income, liquid reserves and capital that EC itself already owns.
