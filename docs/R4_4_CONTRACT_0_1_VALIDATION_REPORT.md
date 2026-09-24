# R4.4-CONTRACT.0.1 validation — 2026-09-24

## Scope and Git baseline

Start: `113a1f3fe13ff9698a97f82f3f1a53b41b4f3b21`, main tracking origin/main.
Origin verified as `https://github.com/aqedah/MILAL.git`. Working tree initially
clean with no unpublished commits. `git pull --ff-only origin main` reported
Already up to date. AGENTS/HANDOFF and active LAYER.0.2 specification were read
before modifications and after synchronization.

Readiness result: **READY_FOR_HUMAN_CONTRACT_REVIEW**.
This is an input CONTRACT_PROPOSAL and compatibility audit, not R4.4 analytical
implementation, final output, scholarly adjudication or approval of Q1–Q7.

## R4.3 architecture findings

R4.3 explicitly implements a partial scaffold, not a complete tree. Its
compile_scaffold checks **at most one** direct parent, allowing zero. parents()
and acyclic() already restrict hierarchy semantics to explicit parent types.
Every unresolved node receives a TECHNICAL_ROOT_LINK to JOB_BOOK, explicitly not
an analytical parent. Membership, continuation, closure, peers and overlays are
separate typed claims, though the historical 06_overlay file mixes several
non-parent classes. It cannot be reused as modern OVERLAY_RESPONSIO wholesale.

The historical later_human_review_required=True blanket policy is no longer the
active necessity queue after LAYER.0.2. Reusing it as mandatory further review,
using technical root links as parents, treating the mixed overlay table as one
layer, or treating every textual locus as a full unit would be incompatible with
the proposed layered input. Those are rejected reuse interpretations; the audit
does not falsely claim R4.3 already required complete parentage or merged groups
with hierarchy. Current at-most-one cardinality is documented, not expanded or
newly adjudicated.

R4.3 schema audit: **83 field/document entries across 10 requested artifacts**.

| Classification | Count |
| --- | ---: |
| STILL_VALID_UNCHANGED | 49 |
| REUSABLE_WITH_EXTENSION | 19 |
| AMBIGUOUS_AFTER_HSA3 | 1 |
| INCOMPATIBLE_WITH_LAYERED_MODEL | 0 |
| DEPRECATED_FOR_R4_4 | 14 |

The one historical parent-status ambiguity is addressed by separate historical
and necessity axes in the proposal; it is not an unresolved mapping blocker.
Deprecated entries remain preserved historical records and may not serve as an
unqualified active contract. Exact IDs, records, typed relations, membership order,
source evidence/judgment IDs and provenance remain reusable. See
[R4.3/HSA architecture audit](R4_4_CONTRACT_0_1_ARCHITECTURE.md) for code citations.
At baseline, tracked filename search found no R4.4 consumer/spec/test/runner;
text search found only later-stage planning, readiness and prohibition references.

## Authoritative sources and proposed model

The only real input is accepted HSA3-LAYER.0.2 ZIP
`results/hsa3_layer_0_2_real_final_20260924_a_results.zip`, SHA256
`0754eb4c3c22e17ff59627440f8ca5aeb92ee20ecb6a7cdc197240850bb31983`.
Outer 01–03 files govern current necessity, while nested
`history/hsa3_layer_0_1/` canonical files govern nodes, seven relation layers,
groups, roles, unresolved/deferred questions and frozen seams. Ancestor original
records, judgments, raw evidence and manifests remain intact. There are 18
explicit canonical/supporting source members; the inventory names their exact
member paths, hashes, identity fields and authority scopes.

Proposed node fields:

`node_id`, `canonical_node_id`, `node_kind`, `textuality`, `reference_start`, `reference_end`, `anchor_ref`, `span_type`, `structural_function`, `speaker`, `participant_role`, `source_stage`, `human_status`, `frozen_status`, `historical_parent_status`, `parentage_necessity_status`, `additional_parentage_review_required`, `direct_parent_edge_resolved`, `direct_parent_ids`, `technical_only`, `qualified_spans`, `provenance_ids`, `field_presence`, `original_record`

Proposed relation fields:

`relation_id`, `source_id`, `target_id`, `endpoint_form`, `source_ref`, `target_ref`, `scope_ref`, `relation_layer`, `relation_type`, `polarity`, `directionality`, `status`, `human_supplied`, `automatic_resolution`, `source_stage`, `evidence_ids`, `provenance_ids`, `limitations`, `historical_status`, `original_dimension`, `membership_position`, `graph_scope`, `original_record`

Node kinds retain TEXTUAL_NODE, TRANSITION_ANCHOR, ROLE_ALIAS, COMPOSITION_GROUP,
TECHNICAL_ROOT and SOURCE_EVIDENCE_ANCHOR. Textuality is separate; a role alias
is not a second unit. Unrecorded group/root spans use NO_SPAN_RECORDED. Later
qualified annotations do not overwrite historical reference loci.

Relation layers retain COMPOSITION_GROUPING and the other established layer
names. Native reference-pair and scope-only endpoints are explicit extensions:
ANA-H2/H4 remain reference pairs and ANA-H5 remains scope-only. No fabricated
node joins. Polarity, source dimension, stored orientation and membership order
are retained. The 57 technical navigation links remain outside analytical scope.

Status axes: adjudication_status, human_decision_status, historical_status,
necessity_status, review_status, frozen_status, future_scope_status. Preserve
source tokens and field-presence metadata; never collapse them into NULL.
All 57 rows simultaneously retain historical UNRESOLVED, false additional
parentage review and false edge resolution. Job 2:11 keeps the exact
DIRECT_TEXTUAL_PARENT_NOT_REQUIRED token and no parent assignment.

Provenance model: current exact member/raw row/identity, row hash, member hash,
outer archive hash, complete original records and nested evidence/judgment/
addendum links. Evidence collections retain their field paths and scope. Empty
technical human-ID lists are not filled with invented IDs. Precedence applies
only to explicitly linked same-question/same-dimension decisions; history remains.
Different-dimensional positive/negative claims coexist.

## Real fixture results

| Fixture | Result and preserved claims |
| --- | --- |
| Job 2:11 | PASS: textual paragraph/participant introduction, opening membership, second-scene exclusion, historical UNRESOLVED, parent not required, no assigned parent |
| Job 31:40 | PASS: SPEECH_UNIT_END, local closure to 29:1, direct-closure negative to 27:1, POST_DIALOGUE_JOB termination |
| Job 32:1 | PASS: transition component, post-closure transition, no assigned parent, contrastive ANA anchor with 38:1 |
| Elihu | PASS: 32:2–5 introduction, 32:6–37:24 group, four peer onsets/members, independent response-role overlay |
| Job 37:24/38:1 | PASS: negative parentage and response antecedent, rhetorical overlay context retained |
| YHWH response | PASS: reciprocal textual peers, composition-complex peers/sequence, 40:1 CHILD_OF 38:1 |
| Job 42 | PASS: 42:7 onset/final narrative membership/transition, 42:16 no-boundary continuation, no 42:10/12 promotion |

Fixtures use exact source identities; reference selectors for 42:10/12 are only
regression controls, not identity joins. Frozen synthetic clause IDs differ from
real BHSA IDs, so those controls verify actual source evidence-anchor records
without hard-coding empirical node IDs into the synthetic fixture.

## Real dry-run mapping

| Status | Records |
| --- | ---: |
| LOSSLESS | 331 |
| LOSSLESS_WITH_EXTENSION | 308 |
| AMBIGUOUS_SCHEMA | 0 |
| INCOMPATIBLE | 0 |
| NOT_APPLICABLE | 7 |
| Total | 646 |

Record families: 75 nodes, 250 relations, 14 group views, 58 questions (57 parent
records plus ANA-Q3), 6 role-crosswalk rows, 7 seam statuses, 57 historical
proposals, 7 presentation matrix rows, 57 human necessity decisions, 57 necessity
crosswalk rows, 57 final necessity states and 1 future-scope document.
The seven NOT_APPLICABLE rows are preserved presentation views, not dropped
research records. Historical ancestors are preserved wholesale and not counted
again as new active records. No schema blockers remain **under this proposal**;
human approval of the schema remains pending.

## Q1–Q7 — all UNREVIEWED

Q1. Adopt a layered typed graph instead of a complete one-parent tree?
Q2. Preserve historical unresolved parent and human parent-not-required together?
Q3. Freeze the invariant excluding current composition groups as textual parents?
Q4. Separate technical navigation from analytical graph?
Q5. Keep negative constraints as first-class records?
Q6. Permit future participant/rhetorical overlays without modifying lower layers?
Q7. Validate cycles by relation-layer semantics rather than the heterogeneous graph?

No answers were supplied by Codex. The review packet leaves all answers blank.
Future participant arc remains NEXT_RESEARCH_SCOPE / UNADJUDICATED, with no
hypothetical relation generated. Extensibility tests inspect the endpoint/schema
extension and lower-layer immutability only. No new human judgment, structural,
composition or overlay relation: **0 / 0 / 0 / 0**. R4.4 consumer implementations: **0**.
A–G remain FROZEN, ANA-Q2/Q4/Q5 accepted, ANA-Q3 UNRESOLVED/HUMAN_DEFERRED.
All prior analytical cores remain unchanged.

## Validation and artifacts

- Syntax: PASS for both test-harness files.
- Stage tests: **68 PASS**, no failures/errors/skips; 24.850 seconds.
- Full regression: **1,325 PASS**, no failures/errors/skips; 307.953 seconds
  including discovery and receipt generation.
- Synthetic, real and independent rerun: **44/44 run gates PASS** each.
- 43 model gates have targeted negative mutations; manifest corruption has a
  separate negative test. Two external release gates also have negative tests.
- Full-regression skip-zero and independent ZIP byte equality: **2/2 release gates PASS**.
- Human-facing synthetic packet, readiness, schemas and fixtures inspected before
  real execution. Optional missing group/root spans are explicitly distinguished.
- Real independent audit: 646 raw source receipts verified, all 237 upstream
  members byte-preserved, 169 frozen repository pins unchanged, 257 output members
  and 16 valid manifests. New code/config/document hashes match the actual artifact.
- Two independent real process invocations produced identical entire ZIP bytes.

Synthetic ZIP: `results/r4_4_contract_0_1_synthetic_final_20260924_a_results.zip`

SHA256: `4ab0427aad3fc11197b29deaf45c90db67e5431060d66f0a955fd1f011e7996f`.
Synthetic fixture maps 635 records; its smaller population is not conflated with
646 real records. No old regression tests were weakened or skipped.

Real ZIP: `results/r4_4_contract_0_1_real_final_20260924_a_results.zip`

Independent ZIP: `results/r4_4_contract_0_1_real_repeat_20260924_a_results.zip`

Both SHA256: `9fb5e4ec65cb7eb8961a1ee25c4cd7f64a0c5ee598fb160d0dcd0bfaae5560f2`.

Local receipts: `results/r4_4_contract_0_1_unit_final_20260924_b.log`,
`results/r4_4_contract_0_1_full_regression_final_20260924_a.log`,
`results/r4_4_contract_0_1_full_regression_final_20260924_a.json`,
`results/r4_4_contract_0_1_independent_audit_20260924_a.json`.
All real ZIPs, outputs, logs and the independent inspection script remain ignored.

## Repository changes and next step

Contract documentation, schema proposals and test harness only:

- `config/r4_4_contract_0_1_job.json`
- `config/r4_4_contract_0_1_proposal.json`
- `tests/r4_4_contract_audit.py`
- `tests/test_r4_4_contract_audit.py`
- `docs/R4_4_CONTRACT_0_1_ARCHITECTURE.md`
- `docs/R4_4_CONTRACT_0_1_INVARIANTS.md`
- `docs/R4_4_CONTRACT_0_1_PRECEDENCE.md`
- `docs/R4_4_CONTRACT_0_1_RESEARCHER_SOURCE.txt`
- `docs/R4_4_CONTRACT_0_1_SPEC.md`
- `docs/R4_4_CONTRACT_0_1_VALIDATION_REPORT.md`
- `docs/README_MILAL_R4_4_CONTRACT_0_1.md`
- `docs/HANDOFF.md`
- `.gitattributes`

Commit message: `Audit R4.4 layered input contract`.
Resulting commit and verified remote HEAD are reported after commit/push.
Next: researcher reviews Q1–Q7 and proposed extensions. Implementation requires
separate subsequent authorization. This report does not declare READY_FOR_IMPLEMENTATION.
