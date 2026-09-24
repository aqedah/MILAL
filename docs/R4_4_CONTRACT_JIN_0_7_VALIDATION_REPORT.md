# JIN.0.7 human relation-layer freeze — 2026-09-24

Readiness: **READY_FOR_REVISED_R4_4_CONTRACT_REVIEW**.
The six decisions below are explicit researcher adjudications, not inferred acceptance.
Validation establishes faithful transcription and preservation; it does not answer R1–R10.

Start commit: `148d741e63986c2a209ed770e6682fe8925b4e66`.
Repository `aqedah/MILAL`, branch main tracking origin/main; verified origin
`https://github.com/aqedah/MILAL.git`. Initial worktree clean; fast-forward pull was
already up to date. Normal commit/push is authorized by request §23 after PASS.

## Six primary decisions and 111 derived applications

| Decision | Approved interpretation | Strict dependency |
|---|---|---|
| Q-A | 1:13→1:6 macro containment | UNRESOLVED_UNPROVEN |
| Q-B | 3:1 macro speech-event frame; 3:2 formal CSF continuing within it | UNRESOLVED_UNPROVEN |
| Q-C | 40:1→38:1 macro containment in first YHWH response complex | UNRESOLVED_UNPROVEN |
| Q-D | Separate strict continuation, macro continuation, no-new-boundary semantics | No new strict acceptance |
| Q-E | Historical SAME_LEVEL rows are MACRO_TEXTUAL_PARATAXIS | No strict parataxis inferred |
| Q-F | Separate mandatory relation_type / relation_layer; nine-value conceptual vocabulary | No strict edges created |

Primary researcher decisions: **6**, each ACCEPTED and linked to exact source byte
offsets, excerpt SHA256 and source SHA256. Derived application records: **111**:
CHILD_OF 2; HIERARCHICALLY_ABOVE 1; CONTINUES_WITHIN 10; SAME_LEVEL_SIBLING 98.
Q-B/Q-D share one 3:2→3:1 application with both decision IDs; no duplicate edge or
double-counted primary judgment. Every application has derived_from_human_rule=true,
new_human_decision=false, migrated=false and rewrites_historical_record=false.

CONTINUES_WITHIN: **1 SPEECH_FRAME_CONTINUATION** (3:2→3:1), **7 provisional
MACRO_TEXTUAL_CONTINUATION** (1:14/16/17/18→1:13, 2:9→2:1–2:10, 11:4→11:1,
1:5→1:1–1:5), **2 NO_NEW_BOUNDARY** (28:1→27:1, 42:16→42:7).
Approval of the typing model does not turn the seven provisional cases into final
individual macro adjudications. No no-boundary placement becomes motherhood.

All 98 SAME_LEVEL IDs and stored orientations are preserved. Their new interpretation
overlay uses the explicitly approved MACRO_TEXTUAL_PARATAXIS name; historical
JIN.0.6 MACRO_PARATAXIS proposal records are not rewritten. Macro controls, historical
pairwise parataxis evidence and the two strict positive controls remain intact.
Strict controls are not promoted to human macro edges.

The conceptual model is LAYERED_TYPED_GRAPH. Nine approved relation_layer values:
STRICT_CLAUSE_HIERARCHY, STRICT_CLAUSE_PARATAXIS, MACRO_TEXTUAL_HIERARCHY,
MACRO_TEXTUAL_PARATAXIS, COMPOSITION, TRANSITION, OVERLAY_RESPONSIO,
NEGATIVE_CONSTRAINT, TECHNICAL_NAVIGATION. No BOUNDARY_PLACEMENT enum is added.
semantic_subtype distinguishes current continuation/placement meanings.

## Methodological interpretation

MILAL distinguishes strict clause hierarchy from macro textual hierarchy.

Historical macro relations may remain valid even where strict syntactic motherhood is unproven.

Jin’s one-mother principle governs strict hypotactic daughterhood, not every macro containment relation.

Macro parataxis and strict clause parataxis are distinct analytical claims.

Relation type alone is insufficient; every active analytical relation must be interpreted together with its relation layer.

CONTINUES_WITHIN may encode macro continuation or no-new-boundary placement and therefore requires semantic subtype information.

I1–I6 are recorded as approved invariants. Conceptual approval does not execute the
future contract, select a root, require every macro unit to have a mother or answer
the separately requested R1–R10 operational questions.

## Historical preservation and open questions

The original 250-relation registry remains immutable. The 139 relations outside the
approved application scope receive no new typing application. All historical IDs,
types and earlier review statuses remain available exactly as recorded, including
reopened statuses, without rejection/deletion. The new layer supersedes interpretation
only; an old status is not silently rewritten.

New relation count **0**; new parent edge count **0**; relation migration count **0**;
new accepted strict relation count **0**. Previous analytical cores unchanged.
Job 2:11 / 32:1: **NO_MACRO_MOTHER_FOUND**, no search or mother assignment.
Participant arc UNADJUDICATED. R4.4 consumer absent.

Historical Q1–Q9 retain UNAPPROVED status, with exact original wording and source hash.
Q1 maps to revised R1/R2/R3, Q2 to R4, Q3 to R5, Q4 to R6, Q5 to R7, Q6 to R8,
Q7 to R9, Q8 to R2/R3 and Q9 to R10. These are suggested review crosswalks, not answers.

R1–R10 are all UNREVIEWED with every human answer field blank:
canonical layered representation; strict single-mother scope; macro mother requirement;
independent unresolved strict status; composition exclusion; navigation separation;
negative constraints; append-only overlays; layer-specific cycles; separate root scope.
The researcher-approved conceptual model and the requested unreviewed canonical
operational adoption questions are explicitly distinguished.

## Validation

- Python and Windows runner syntax: PASS.
- New unit tests: **44 PASS**, including negative tests for all model/preflight gates
  and manifest/determinism/regression failure or skip cases.
- Complete regression: **1,721 PASS; failures 0, errors 0, skipped 0**; 750.983 seconds.
- Final Windows synthetic self-test: **38/38 run gates PASS**. Packet, provisional
  scope and blank R1–R10 fields inspected before real execution.
- Real A and independent real B: **38/38 run gates PASS**, same complete ZIP bytes.
- External release checks: **2/2 PASS** (deterministic rerun, full regression receipt).
- Independent verification: **465 output ZIP members**, **449 original files unchanged**,
  **253 frozen repository hashes unchanged**, **23 recursive SHA256 manifests valid**.
  Exact historical-row linkage, 6/111 accounting, provisional 7, subtype 1/7/2, source
  excerpts, nine-value vocabulary, blank questions and zero new edges/migration verified.
- Empirical mode: REAL_FROZEN_JIN_0_6. No new raw BHSA extraction. No Termux empirical claim.

Real ZIP A: `results/jin07_real_final_20260924_a_results.zip`.
Independent B: `results/jin07_real_final_20260924_b_results.zip`.
Both SHA256:
`0f8d9e785a97421abe2184b29e0c257c2aa0ed43f36f088ba6229a3cbc04bbc4`.

Local receipts: `results/jin07_regression_20260924_a.json`,
`results/jin07_regression_20260924_a.log`,
`results/jin07_release_verification_20260924.json`.

## Files changed and next task

`.gitattributes`; `docs/HANDOFF.md`; `config/r4_4_contract_jin_0_7_job.json`;
`docs/R4_4_CONTRACT_JIN_0_7_RESEARCHER_SOURCE.txt`;
`docs/R4_4_CONTRACT_JIN_0_7_SPEC.md`;
`docs/R4_4_CONTRACT_JIN_0_7_VALIDATION_REPORT.md`;
`docs/README_MILAL_R4_4_CONTRACT_JIN_0_7.md`;
`src/milal_jin_layer_freeze.py`; `src/milal_jin_layer_freeze_fixture.py`;
`scripts/run_milal_jin_layer_freeze_windows.ps1`;
`scripts/run_milal_jin_layer_freeze_termux.sh`;
`tests/test_r4_4_contract_jin_0_7.py`.
No input ZIP, result directory/archive, local verification script, log, cache or BHSA
data is committed.

Next task: researcher review of `09_revised_contract_review_packet.md` and
`10_remaining_strict_macro_questions.csv`. No migration or R4.4 implementation follows
automatically from this freeze.
