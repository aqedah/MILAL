# JIN.0.6 validation — 2026-09-24

Readiness: **READY_FOR_RELATION_LAYER_HUMAN_REVIEW**.
Technical validation is complete; no new scholarly/human adjudication is claimed.

Start HEAD: `a3d770425004af8d635518271a3d640aaf8889dc`, main tracking origin/main.
Verified origin: `https://github.com/aqedah/MILAL.git`; initial working tree clean;
`git pull --ff-only origin main` reported already up to date.
The request authorizes normal commit/push after validation; no forced update.

## Inventory and proposals

Primary hierarchy-like relations: **13**. Complete canonical/control registry: **250**,
across 24 relation types. Canonical nodes: **75**. All stored edge orientations preserved.

| Family | Total | Strict | Macro | Mixed | Unresolved | Non-parent placement |
|---|---:|---:|---:|---:|---:|---:|
| CHILD_OF | 2 | 0 | 2 | 0 | 0 | 0 |
| HIERARCHICALLY_ABOVE | 1 | 0 | 1 | 0 | 0 | 0 |
| CONTINUES_WITHIN | 10 | 0 | 0 | 0 | 0 | 10 |
| SAME_LEVEL_SIBLING | 98 | 0 | 98 | 0 | 0 | 0 |

CONTINUES_WITHIN uses RL5: proposed macro placement, **not an asserted parent edge**.
Eight are MACRO_TEXTUAL_CONTINUATION and two NO_NEW_BOUNDARY. Strict syntactic
continuation is not established. SAME_LEVEL's 98 are macro-parataxis proposals;
strict-parataxis, mixed and unresolved proposals are each zero for this family.

Potentially overloaded generic labels: **4**, not four demonstrated strict/macro
co-occurrence types. Observed alternative placement semantics occur in one family,
CONTINUES_WITHIN. No historical edge was determined to have independent strict and
macro support in this audit. The strict controls are reported separately.

Composition 47, transition 3, overlay 2, negative constraints 27 and technical
navigation 57 are retained as non-parent controls. The hierarchy table also retains
DIRECT_LOCAL_CLOSURE 1, and the same-level table PARALLEL_ENDING 2. DIRECT_LOCAL_CLOSURE
has an unresolved future layer rather than a fabricated strict-mother interpretation.
The future contract must settle closure typing. RL6 entries for already typed
non-parent controls denote hierarchy-category inapplicability, not lost provenance.

Node proposals: MACRO_TEXTUAL_UNIT 42; COMPOSITION_GROUP 14; EVIDENCE_ANCHOR 8;
TRANSITION_ANCHOR 7; ROLE_ALIAS 3; TECHNICAL 1. Clause anchors never change this typing
into strict hierarchy. Exact canonical anchor crosswalk: 49 unique IDs; historical
comparison: 101 unique relation IDs; linguistic pair inventory: 229 unique pair IDs.

## Key cases and controls

- **1:13→1:6**: RL2 macro proposal. Historical scene-containment rationale retained;
  JIN.0.5 found zero strict mother-support candidates. Latest status remains
  REOPENED_FOR_ADDITIONAL_LINGUISTIC_AUDIT, not restored strict motherhood.
- **3:1→3:2**: RL2 macro speech-frame proposal; strict mother remains unproven.
  **3:2→3:1** retains its separate historical CONTINUES_WITHIN ID as RL5 macro
  continuation. Actual N→Q transition is 3:2→3:3. Reopened status is preserved on
  the exact historical relation to which the JIN.0.4 review applies.
- **40:1→38:1**: RL2 macro hierarchy. JIN.0.4 macro reconfirmation and original
  storm formula/challenge/distribution rationale retained. Strict mother is unproven.
- **28:1→27:1** and **42:16→42:7**: RL5 NO_NEW_BOUNDARY placement, with their distinct
  HSA2/HSA1 rationale preserved; neither is newly declared a syntactic dependency.
- Job 32:3 strict controls `JP:JT0037:499628:499631` and
  `JP:JT0037:499629:499631`: STRICT_HYPOTAXIS_POSITIVE_CONTROL, UNREVIEWED;
  human_accepted=false and macro_evidence=false. No registry edges created.
- Macro controls retain B1/B6/B7 and their seven exact relation-ID records.
  Required same-level fixtures 1:6↔2:1, 27:1↔29:1, 32:6/34:1/35:1/36:1,
  38:1↔40:6 and 40:3↔42:1 are present in both stored orientations; cycle speech
  relations remain in the complete 98-row table and packet.
- **2:11 / 32:1**: NO_MACRO_MOTHER_FOUND unchanged, no new mother search.
  POST_CLOSURE_TRANSITION stays in TRANSITION, never a parent edge.

Q-A–Q-F are all UNREVIEWED with all human decision fields blank. Q1–Q9 remain
UNAPPROVED; participant arc UNADJUDICATED; R4.4 consumer absent.
New accepted relations, parent edges, human judgments and migrations: **0 each**.

## Validation

- Python syntax and Windows runner syntax: PASS.
- New stage unit tests: **43 PASS**. Includes a negative mutation for every model
  and preflight gate, plus manifest, determinism and regression-failure/skip negatives.
- Full suite: **1,677 PASS; failures 0, errors 0, skipped 0** (757.062 seconds).
- Final Windows-runner synthetic self-test: **34/34 gates PASS**, human-facing
  packet and blank review fields inspected before empirical execution.
- Real frozen-source audit A and independent process B: **34/34 run gates PASS**.
- External release gates: deterministic ZIP identity and regression receipt: **2/2 PASS**.
- Independent verification: **449 ZIP members**, **425 upstream files byte-identical**,
  **243 frozen repository hashes unchanged**, **22 recursive SHA256 manifests valid**.
  Inventory row IDs/types/source records match exact original CSV rows; full crosswalk
  coverage, key controls, blank human fields and zero mutation counts independently checked.
- No new raw BHSA extraction; empirical mode is REAL_FROZEN_SOURCE_AUDIT.
  No Termux empirical execution claimed. No old test or analytical core modified.

Real ZIP A: `results/jin06_real_final_20260924_a_results.zip`.
Independent ZIP B: `results/jin06_real_final_20260924_b_results.zip`.
Both SHA256:
`4ae3ea0d3486f8b655338568030f427c308726efc8ede72b24912f9efa6ea94d`.

Local-only receipts: `results/jin06_regression_20260924_a.json`,
`results/jin06_regression_20260924_c.log`,
`results/jin06_release_verification_20260924.json`.
Earlier interrupted development runs are not counted as completed regression passes.

## Files and next review

Tracked changes: `.gitattributes`; `docs/HANDOFF.md`;
`config/r4_4_contract_jin_0_6_job.json`;
`docs/R4_4_CONTRACT_JIN_0_6_RESEARCHER_SOURCE.txt`;
`docs/R4_4_CONTRACT_JIN_0_6_SPEC.md`;
`docs/R4_4_CONTRACT_JIN_0_6_VALIDATION_REPORT.md`;
`docs/README_MILAL_R4_4_CONTRACT_JIN_0_6.md`;
`src/milal_jin_relation_layers.py`; `src/milal_jin_relation_layers_fixture.py`;
`scripts/run_milal_jin_relation_layers_windows.ps1`;
`scripts/run_milal_jin_relation_layers_termux.sh`;
`tests/test_r4_4_contract_jin_0_6.py`.
Results, archives, runtime logs, local validation scripts and BHSA are not committed.

Next: human review of `17_human_review_packet.md` and `16_human_review_cases.csv`.
Adjudicate Q-A/B/C's relation scope, then Q-D/E/F's explicit typing/schema policy.
The audit does not authorize migration, a new mother, participant decisions or R4.4
implementation. Unknown unit extent and unresolved future closure typing remain explicit.
