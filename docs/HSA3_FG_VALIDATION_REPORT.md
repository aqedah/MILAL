# HSA3-F/G validation receipt — 2026-09-23

Start commit: `d720d805f771cb18912728dd6982177c57459ef6` on main.
Verified origin: `https://github.com/aqedah/MILAL.git`; startup fast-forward pull
reported already up to date, clean tree and no unpublished local commits.
Final commit message: `Freeze final YHWH and narrative global seams`.
The end commit is the Git commit containing this receipt; the final session
response records its full hash and live remote verification, avoiding a
self-referential commit hash inside its own tracked content.

## Implemented and methodological results

SEAM_F and SEAM_G are recorded as researcher ACCEPTED / FROZEN. All A–G are now
FROZEN in the current adjudication layer. Original F/G UNREVIEWED source rows
remain byte-identical historical evidence; no human response fields were invented.

| New composition | Supplied span | Result |
| --- | --- | --- |
| YHWH_JOB_RESPONSE_COMPLEX_1 | 38:1–40:5 | NON_TEXTUAL_COMPOSITION_GROUP |
| YHWH_JOB_RESPONSE_COMPLEX_2 | 40:6–42:6 | NON_TEXTUAL_COMPOSITION_GROUP |
| YHWH_JOB_RESPONSE_SEQUENCE | 38:1–42:6 | Ordered complex 1, complex 2 |
| FINAL_NARRATIVE_COMPLEX | 42:7–42:17 | H:HSA030 onset anchor |

The two complexes have one symmetric SAME_LEVEL_COMPOSITION_PEERS record.
POST_SPEECH_NARRATIVE_TRANSITION connects the response sequence to final narrative.
Both types are composition-only, not textual SAME_LEVEL_SIBLING or parentage.
GROUP_MEMBER_OF is reused for eight ordered composition memberships.
The schema audit found no existing equivalent group or composition peer/transition.

Existing textual relations are confirmed exactly: four directed sibling rows
for 38:1↔40:6 and 40:3↔42:1, 40:1 CHILD_OF 38:1, and the two 42:16 NO_BOUNDARY /
CONTINUES_WITHIN 42:7 rows. 38:3/40:7 are clause evidence anchors, not new nodes.
40:3–5/42:1–6 reuse H:HSA027/H:HSA029 with explicit human span annotations.

42:10/12 remain internal evidence; neither becomes a paragraph/macro boundary
or textual parent. 42:10 has no new sibling claim. 42:16 retains NO_BOUNDARY and
CONTINUES_WITHIN H:HSA030, חיה (XJH[), and the Time phrase after predicate/subject.
The temporal frame at 42:7 refers to YHWH speaking, not a direct relation from
Job's response at 42:6. No direct 42:6↔42:7 parentage or forward response/continuation.

## Computed real-data action accounting

| Category | Count |
| --- | ---: |
| New researcher seam decisions | 2 |
| New composition groups | 4 |
| Confirmed existing groups | 0 |
| New positive composition relations | 10 |
| Confirmed existing relation rows | 7 |
| New negative constraints | 14 |
| Unresolved retained in F/G crosswalk | 6 |
| Duplicate skipped | 0 |
| RESOLVED_BY_SEAM_F / RESOLVED_BY_SEAM_G | 0 / 0 |
| NOT_APPLICABLE_TO_APPROVED_DECISION | 51 |
| All remaining original direct-parent questions | 57 |

The 14 negatives are clause-grounded: two 42:6 clauses × both parent-exclusion
directions (4), forward response exclusions (2), forward continuation exclusions
(2), four 42:10 clause boundary-promotion exclusions (4), and two 42:12 exclusions
(2). They do not create new structural nodes or infer a universal NO_BOUNDARY
judgment for every clause. Synthetic has fewer clauses, hence 7 negatives; this
is intentional fixture population, not a weakened real-data expectation.
New relation counts are calculated, never hard-coded as analytical semantics.

The six F/G-related unresolved IDs are H:HSA025, H:HSA027, H:HSA028, H:HSA029,
H:HSA030, H:HSA031. Composition decisions do not assign their textual parents.
All other 51 original questions remain in the lossless crosswalk. No historical
HSA3-PREP row is rewritten. Frozen global seams do not imply a resolved tree.

## Validation

- Syntax: new module and test module compile PASS.
- Stage-specific: **62 tests PASS**, skip 0, 13.080 seconds.
- Full regression: **1,133 tests PASS**, skip 0, 217.378 seconds; includes all
  1,071 previous tests. No tests weakened or skipped.
- Self-test through the Windows runner: **39/39 gates PASS**.
- Synthetic final report and complete review summary manually inspected before
  real execution. Layers, spans, negative controls and unresolved state retained.
- Real frozen-BHSA-evidence invocation: **39/39 gates PASS**.
- Separate real Python invocation: **39/39 gates PASS**, complete ZIP bytes equal.
- Every gate has a negative mutation: 38 model/input gates plus manifest corruption.
- Additional tests cover both forbidden parent directions, forbidden continuation,
  symmetric peer duplicate suppression, existing group/peer reuse, unknown source
  IDs, canonical-ID ambiguity, input tampering, source row links and frozen history.

Local logs: `results/hsa3_fg_unit_a.log`, `results/hsa3_fg_full_regression_a.log`.
The independent audit verified ZIP CRC, **202 result members**, **13 manifests**,
**127 exact source-row links**, **143 frozen repository pins**, all **183 upstream
members unchanged**, all report links resolved, and byte-identical independent ZIPs.
There are 36 lossless F/G clause evidence records in the current evidence table.

Real input remains the exact FG-PREP ZIP SHA256
`14dd08fcffabf2d29b6574c05254ca403ba08b9fe01207269ccd6fb9ca3db1f6`.
Its BHSA version is 2021, Text-Fabric version 13.1.0. No new BHSA extraction,
lexical audit or marker discovery was performed in F/G; real gates validate
decisions over the preserved, previously validated BHSA evidence.

## Source spot checks

- 38:3 clause 500081 / words 345459–345463 and 40:7 clause 500272 /
  words 346176–346180 preserve the repeated challenge. Their following clause
  differences (WYq0 vs ZYq0) remain in the full evidence panels.
- 42:6 preserves both 500409 (M>S[) and 500410 (NXM[); neither is silently folded.
- 42:7 preserves 500411 Way0 HJH[ and 500412 xQtX DBR[, plus all subsequent
  speech/quoted clauses. The temporal construction and speech speaker remain
  separately traceable.
- 42:10 preserves all four clauses 500428–500431, including WXQt CWB=[ and
  InfC PLL[; 42:12 preserves 500440 WXQt BRK[ and 500441 WayX HJH[.
- 42:16 preserves 500448 WayX XJH[ word 346912, plus 500449/500450.
  No HJH[/XJH[ conflation and no boundary promotion.

## Artifacts

Synthetic ZIP: `results/hsa3_fg_final_synthetic_20260923_a_results.zip`

SHA256: `f59d1cb259f9b10c17497bbabccd9c9ffde59980ff2836f457e7f338a0e7d508`

Real ZIP: `results/hsa3_fg_final_real_20260923_a_results.zip`

SHA256: `64cf25abd09fca7355abbcb3740cc46ed26f61b71e5d895ee91383c758974798`

Independent repeat: `results/hsa3_fg_final_repeat_20260923_a_results.zip`, same SHA256.

Final report: `results/hsa3_fg_final_real_20260923_a/08_hsa3_fg_final_report.md`.
Complete summary: `results/hsa3_fg_final_real_20260923_a/09_hsa3_complete_review_summary.md`.
All generated artifacts, logs and the local independent audit script are ignored,
not committed. The required twelve outputs and seven additional provenance files
are present at the result root; complete unchanged history is nested beneath it.

## Files changed

- `.gitattributes` — exact request-byte preservation.
- `config/hsa3_fg_human_decisions.json` — supplied decisions and dimensional limits.
- `config/hsa3_fg_job.json` — baseline, authority, archive and 143 frozen pins.
- `docs/HANDOFF.md` — current stage, freeze and unresolved follow-up.
- `docs/HSA3_FG_RESEARCHER_SOURCE.txt` — exact user attachment bytes.
- `docs/HSA3_FG_SPEC.md` — methods, schemas, scope and validation requirements.
- `docs/HSA3_FG_VALIDATION_REPORT.md` — this receipt.
- `docs/README_MILAL_HSA3_FG.md` — complete execution instructions.
- `scripts/run_milal_hsa3_fg_windows.ps1` — repository-relative Windows runner.
- `src/milal_hsa3_fg_final_adjudication.py` — separate human adjudication layer.
- `tests/test_hsa3_fg_final_adjudication.py` — gate mutations and invariants.

## Frozen layers and remaining work

No prior analytical core was modified. HSA1/HSA2/HSA2-F, HSA3-PREP, ANA and all
historical artifacts remain byte-identical. ANA-Q2/Q4/Q5 stay ACCEPTED;
ANA-Q3 remains UNRESOLVED / HUMAN_DEFERRED, with no causal or fulfilment claim.
The 2:11–42:9 participant-frame hypothesis remains unadjudicated. R4.4 not started.
Next recommended action is researcher review of the complete layered summary,
followed by an explicitly scoped decision about unresolved textual parentage or
the separate participant-frame hypothesis. No automatic stage progression.
