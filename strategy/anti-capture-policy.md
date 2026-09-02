# Funding Anti-Capture Policy

## Objective

Funding must increase the practical freedom of Exergism Commons (EC), not convert financial dependence into external governance.

This policy defines default safeguards. Specific legal obligations and grant agreements may require stricter controls.

## 1. No governance-for-money

EC should not grant a funder, sponsor or customer automatic rights to:

- appoint or remove EC governance members;
- obtain voting power merely because it funds EC;
- veto EC-wide decisions;
- control EC's general roadmap;
- compel political, scientific or public positions unrelated to a funded scope;
- obtain privileged ownership of EC-wide assets or governance infrastructure.

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

### Bootstrap treatment

EC may begin with one material funder. In that case the funder can temporarily represent **100% of recorded funding** without making the acceptance intrinsically invalid.

Bootstrap does not hide or waive dependency. A materially concentrated bootstrap decision must:

1. explicitly identify EC as being in a `BootstrapState`;
2. classify concentration above 50% as a `StrategicDependencyState`;
3. include a documented diversification plan when concentration exceeds 30%;
4. use qualified approval when concentration exceeds 50%;
5. preserve the no-governance-for-money and IP/infrastructure firewalls; and
6. carry a review date so bootstrap status cannot become an indefinite unreviewed exception.

The key distinction is:

> **dependency detected ≠ funding prohibited**

but:

> **dependency hidden or unmanaged = governance defect**

Institutional maturity and funding dependency are separate axes. EC can therefore be simultaneously in `BootstrapState` and `StrategicDependencyState`.

The machine-readable profile uses these dependency classes:

- `DiversifiedState` — single-funder concentration at or below 30%;
- `ElevatedConcentrationState` — concentration above 30% and at or below 50%;
- `StrategicDependencyState` — concentration above 50%.

A future governance revision may replace or refine the bootstrap exit criteria. The current profile deliberately records bootstrap explicitly instead of inferring a permanent exception from age, revenue or founder status.

## 4. Unrestricted/core revenue

Long-term target: at least **30% of annual income** should be unrestricted or sufficiently flexible core revenue.

Potential sources:

- memberships;
- donations;
- recurring sponsorship without governance rights;
- mission-aligned services;
- training/support;
- reserve or Endowment distributions where lawful.

The strategic purpose of core revenue is the institutional capacity to refuse misaligned funding.

## 5. Reserve and permanent-capital target

EC should progressively build:

1. three months of operating expenses;
2. six months;
3. twelve months as a mature resilience target;
4. an **EC Endowment** that converts part of unrestricted surplus into permanent or very long-duration institutional capital.

Restricted grant funds must not be treated as free reserves or Endowment capital unless the relevant agreement expressly permits that use.

The Endowment is governed separately under `endowment-policy.md`.

## 6. Transparency registry

Material funding should be publicly recorded with, where legally possible:

- funder;
- amount or amount range;
- period;
- restricted/unrestricted status;
- purpose;
- deliverables;
- reporting/audit obligations;
- IP conditions;
- governance or advisory rights;
- conflicts of interest;
- subcontracting/third-party constraints;
- termination/clawback conditions where material.

Sensitive personal/banking/security information must not be published.

## 7. Conflict management

A person with a material personal interest in a funding, investment or compensation decision should disclose it and abstain from the relevant decision where appropriate and practicable.

Examples:

- a member whose employer is the funder;
- a researcher deciding their own compensation package;
- a governance member negotiating a related-party contract;
- a decision-maker with a financial interest in an Endowment counterparty.

Where every active member is conflicted because all are also workers, EC should rely on objective compensation formulas, benchmarking, written rationale and additional review rather than treating the conflict as nonexistent.

## 8. No private ownership through membership

Membership in EC must not function as an economic share in the organisation.

Members do not acquire an automatic right to:

- annual surplus;
- reserves;
- Endowment principal;
- Endowment returns;
- revenue in proportion to voting rights or membership status.

EC may compensate members for genuine work under applicable law and a documented compensation policy, but **work -> compensation** must remain distinct from **membership -> distribution**.

See `compensation-principles.md`.

## 9. Endowment anti-capture rule

No donor, sponsor, external asset manager or financial institution obtains institutional control merely because it contributes to or manages Endowment assets.

Endowment arrangements should avoid:

- donor governance rights unrelated to a narrowly documented restriction;
- return or ownership rights that convert a donation into an investment interest;
- permanent exclusivity;
- mission-distorting investment conditions;
- avoidable dependency on a single custodian, manager or counterparty;
- private claims on EC capital by members or founders.

Material restrictions on Endowment gifts should be accepted only after explicit governance review.

## 10. Mission distortion test

Before accepting material funding, EC should ask:

1. Would EC pursue substantially this work without this specific funder?
2. Does the work create reusable capability after funding ends?
3. Are public outputs and scientific/technical integrity preserved?
4. Can EC walk away without threatening organisational survival?
5. Does the agreement create a precedent that weakens future autonomy?
6. Can any unrestricted surplus or reusable capability strengthen EC after the funded period ends?

A negative answer does not automatically reject funding, but raises the required level of governance scrutiny.

## 11. Exitability

Funding relationships should be designed so EC can terminate or decline renewal without losing control of:

- its identity;
- core repositories;
- governance;
- domains;
- trademarks;
- essential infrastructure;
- pre-existing IP;
- community channels;
- unrestricted reserves;
- EC Endowment capital.

## 12. Machine-readable enforcement profile

A reviewable subset of this policy is represented in `ontology/funding.shacl.ttl` and validated against Git-native governance records and the live opportunity registry.

The executable profile currently enforces, among other invariants:

- no governance-for-money flag on funding acceptance records;
- no EC-wide IP ownership transfer to a funder;
- no exclusive funder control of core EC infrastructure;
- an explicit institutional phase and funding-dependency state for funding acceptance records;
- dependency-state classification consistent with the numeric concentration value;
- diversification planning above the 30% concentration threshold;
- qualified approval above the 50% strategic-dependency threshold;
- compensation conflict disclosure and beneficiary abstention;
- enhanced safeguards for Endowment principal withdrawal;
- prohibition of a membership-based distributable economic share.

The human policy remains the governance authority. SHACL is a machine-checkable projection of part of that authority, not an independent constitution. A divergence between policy and shapes is itself a review defect and must be resolved explicitly.

See `spec/MACHINE-READABLE-GOVERNANCE.md`.

## 13. Strategic principle

**The correct measure of funding quality is not how much control EC gains over money, but how much durable freedom EC gains after accepting it.**

A mature EC should be progressively harder to capture because part of its future operating capacity is financed by diversified recurring income, liquid reserves and capital that EC itself already owns.
