# JIN.0.8 validation — 2026-09-24

Contract: **REVISED_R4_4_CONTRACT_HUMAN_FROZEN**.
Readiness: **BLOCKED_PENDING_TOP_LEVEL_AND_REMAINING_HIERARCHY_AUDITS**.

Start commit: `f3b08ae8e07b6e9a54c9e62569bf1e6219415562`.
Repository aqedah/MILAL, main tracking origin/main, verified origin
`https://github.com/aqedah/MILAL.git`. Initial clean-tree fast-forward pull was
already up to date. Request section 23 authorizes commit/push after PASS.

## Approved contract

Exactly **10 primary human decisions**, R1–R10 ACCEPTED. R3 and R8 retain
QUALIFICATION; R10 retains REWORDING. Exact source bytes, offsets, excerpt hashes,
source hash and day-precision version provenance are preserved.

| Decision | Frozen meaning |
|---|---|
| R1 | Canonical LAYERED_TYPED_GRAPH; hierarchy remains an explicit relation layer |
| R2 | Exactly one strict mother only for adjudicated STRICT_HYPOTACTIC_DAUGHTER |
| R3 | Exactly one macro mother for adjudicated MACRO_HYPOTACTIC_DAUGHTER; no universal mother requirement |
| R4 | Unresolved strict parentage coexists with accepted macro relation |
| R5 | Non-textual composition groups cannot be textual mothers |
| R6 | Technical navigation and JOB_BOOK cannot supply analytical mothers |
| R7 | Negative constraints are first-class assertions, distinct from missing edges |
| R8 | Append-only overlays; lower-layer changes require explicit versioned superseding human adjudication |
| R9 | Validation and cycle semantics differ by relation layer |
| R10 | Strict/macro top-level configuration is separately empirical; no root preselected |

**20** source-grounded invariants, CINV-R44-001–020; **111** derived interpretation
records, not new human judgments. **9** relation layers:
STRICT_CLAUSE_HIERARCHY, STRICT_CLAUSE_PARATAXIS, MACRO_TEXTUAL_HIERARCHY,
MACRO_TEXTUAL_PARATAXIS, COMPOSITION, TRANSITION, OVERLAY_RESPONSIO,
NEGATIVE_CONSTRAINT, TECHNICAL_NAVIGATION.

The minimum future schema preserves relation_type/layer/subtype, strict/macro
statuses and all eight independent status axes. Historical Q1–Q9 receive a new
SUPERSEDED_FOR_ACTIVE_REVIEW_BY_REVISED_R1_R10 crosswalk; all original artifacts
and JIN.0.7 blank review fields remain unchanged.

## Fixture and historical integrity

| Fixture | Verified result |
|---|---|
| 1:13 / 1:6 | Macro accepted; strict mother UNRESOLVED_UNPROVEN |
| 3:1 / 3:2 | Macro speech frame / continuation; strict dependency unresolved |
| 40:1 / 38:1 | Macro accepted; strict mother UNRESOLVED_UNPROVEN |
| 28:1 | NO_NEW_BOUNDARY; no strict daughter inferred |
| 42:16 | NO_NEW_BOUNDARY; no strict daughter inferred |
| 1:6 / 2:1 | Macro parataxis preserved; no strict parataxis inferred |
| 37:24 / 38:1 | Negative constraints coexist with existing separate overlay evidence; no new direct overlay edge |
| 31:40 | Closure, composition, transition and negative dimensions preserved |
| 2:11 | NO_MACRO_MOTHER_FOUND; other structural facts preserved |
| 32:1 | NO_MACRO_MOTHER_FOUND; accepted transition preserved |

All **250 historical relation rows** remain unchanged. The preview is NOT_EXECUTED:
111 previously approved typing applications and 139 UNRESOLVED_NOT_ADJUDICATED
future-layer entries. Seven macro continuations remain provisional; all 98
SAME_LEVEL interpretations remain MACRO_TEXTUAL_PARATAXIS.

New analytical relations, parents, composition relations, roots, participant overlays
and migrations: **0 each**. Previous analytical cores were not modified.
Participant arc: UNADJUDICATED. R4.4 consumer: NOT IMPLEMENTED.

## Remaining research

Open review-scope records: **220** = strict **209**, macro **9**, top-level **2**.
Strict 209 = three named strict questions plus 206 historical contextual cases for
strict applicability/scope review. Macro 9 = two unresolved placements plus seven
provisional continuations. These are not 220 disjoint unresolved edges. Exact
historical case rows and subsequent JIN.0.4 judgments remain attached, without
reopening accepted macro/control decisions or deleting source candidates.

Next: separate STRICT_TOP_LEVEL_ROOT_AUDIT and MACRO_TOP_LEVEL_ROOT_AUDIT,
then remaining strict-scope review, targeted audits if needed, migration dry-run,
and only then consideration of a consumer. Allowed evidence and forbidden heuristics
are explicit in output 09. No Job 1:1/JOB_BOOK/default root assumption. Participant
arc is separate future research, not an implementation blocker unless later decided.

## Validation

- Python and PowerShell syntax PASS.
- New tests **63 PASS**; all model/preflight/manifest gates have negative tests.
- Complete regression **1,784 PASS**, failures 0, errors 0, skips 0; runner 688.797 s.
- Synthetic self-test **57/57 run gates PASS**; human-facing output inspected before real execution.
- Real frozen-source execution and independent rerun **57/57 run gates PASS** each.
- External deterministic/regression release gates **2/2 PASS**, with failure mutations covered.
- Independent verification: **483 ZIP members**, **465 upstream files unchanged**,
  **263 frozen repository hashes unchanged**, **24 recursive manifests valid**.
- Exact source excerpts, ten fixtures, 10/111/20 accounting, 220 blank open-scope
  records and zero new edges/migrations independently verified.
- Windows empirical mode REAL_FROZEN_JIN_0_7. No raw BHSA extraction or Termux empirical claim.

After an interrupted turn, disk inspection found NUL corruption in the earlier
`jin08_real_final_20260924_*` ZIPs and release receipts. Those files were retained
but are not release artifacts. Source/config/tests and completed regression logs
remained readable; new tests were rerun. Two fresh recovered runs passed CRC,
all manifests, exact-byte comparison and independent release verification. Their
SHA256 also matches the pre-interruption computed result.

Release ZIP: `results/jin08_real_recovered_20260924_a_results.zip`.
Independent ZIP: `results/jin08_real_recovered_20260924_b_results.zip`.
Both SHA256:
`0c23eeb732e7b94117fddf6705b164f5776893b619ef1f6a810923f343890ad1`.

Receipts: `results/jin08_regression_20260924_a.json`,
`results/jin08_release_verification_recovered_20260924.json`.
All result artifacts, logs and local verification scripts remain outside Git.

## Changed files

- `.gitattributes`
- `docs/HANDOFF.md`
- `config/r4_4_contract_jin_0_8_job.json`
- `docs/R4_4_CONTRACT_JIN_0_8_RESEARCHER_SOURCE.txt`
- `docs/R4_4_CONTRACT_JIN_0_8_SPEC.md`
- `docs/R4_4_CONTRACT_JIN_0_8_VALIDATION_REPORT.md`
- `docs/README_MILAL_R4_4_CONTRACT_JIN_0_8.md`
- `src/milal_jin_contract_freeze.py`
- `src/milal_jin_contract_freeze_fixture.py`
- `scripts/run_milal_jin_contract_freeze_windows.ps1`
- `scripts/run_milal_jin_contract_freeze_termux.sh`
- `tests/test_r4_4_contract_jin_0_8.py`
