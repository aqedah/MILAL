# HSA3-ANA.0.3 validation — 2026-09-23

Start commit: `3aa956887dc1cc40563167f57af26553e38404e0`, `main` tracking
`origin/main`, verified remote `https://github.com/aqedah/MILAL.git`.
Initial tree was clean; `git pull --ff-only origin main` reported already current.
Commit message: `Freeze ana human adjudications with Q3 unresolved`.

## Human decisions and methodological interpretation

| Question | Current disposition | Relation and scope |
| --- | --- | --- |
| Q2 / ANA-C1 | ACCEPTED | POST_CLOSURE_TRANSITION, 31:40 → 32:1; TRANSITION_OVERLAY |
| Q3 / ANA-C2 | UNRESOLVED / HUMAN_DEFERRED | LONG_DISTANCE_RESPONSE candidate, 31:35 → 38:1; no accepted relation |
| Q4 / ANA-C3 | ACCEPTED | CONTRASTIVE_ANA_FRAME, 32:1 ↔ 38:1; OVERLAY_RESPONSIO |
| Q5 / ANA-C4 | ACCEPTED | ELIHU_RESPONSE_ROLE_INTERVENTION, 32:2–37:24; RHETORICAL_FUNCTION_OVERLAY / RESPONSE_RELATION |

Q3 preserves the lexical/participant correspondence and explicit request as
candidate evidence. No explicit causal/fulfillment marker, textual link from
YHWH's appearance to 31:35, or demonstrated interpretive necessity warrants
acceptance. The supplied Korean rationale is preserved verbatim, as are all
three accepted rationales. Q3 has human_decision=DEFERRED,
candidate_status_before=UNADJUDICATED, candidate_status_after=UNRESOLVED,
accepted_relation_created=false and automatic_resolution=false. The original
ANA-C2 remains live. Closure context 31:40 is contextual metadata only.

Counts: **3 accepted human judgments; 1 deferred decision; 3 accepted overlays;
0 textual hierarchy relations; 4 historical candidates**. These are separate
human-layer decisions, not new source detection or automatic parentage.
Q5 retains its historical positional candidate and keeps narrative introduction
32:2–5 distinct from speech sequence 32:6–37:24. No substitute-for-YHWH,
RESPONSE_TO God, fourth-friend or parentage claim is created.

## Validation evidence

- Syntax: `python -m py_compile` on the new module and tests: PASS.
- Stage unit tests: **59 PASS**, skip 0 (final canonical-file rerun 10.091 s).
- Full regression: **866 PASS**, skip 0, 131.400 s, including all 807 prior tests.
- Synthetic self-test: **30/30 gates PASS**; report and next-seam packet inspected.
- Real frozen-artifact execution: **30/30 gates PASS**.
- Every one of the 29 model gates has an explicit failing mutation; manifest
  corruption is separately negative-tested, covering all 30 gates.
- Independent process reruns: complete ZIP and **112/112 members byte-identical**.
- All **97/97 ANA.0.2 members** preserved byte-for-byte in the new history prefix.
- **8/8 current/nested manifests** verified; all three ZIPs' CRC checks PASS.
- **149 exact CSV row links** independently resolved by member, identity field,
  identity value, data-row number, raw CSV row SHA256 and member SHA256.
- **107/107 frozen repository file hashes** unchanged.
- Researcher source is stored with a path-specific Git `-text` attribute to
  retain its original CRLF bytes and exact SHA256 across checkouts. Canonical
  JSON uses LF according to repository policy; its pinned hash was rechecked.
- No new BHSA extraction or historical real-stage regeneration was performed.

Full regression log (ignored local artifact):
`results/hsa3_ana_0_3_full_regression_20260923.log`.
Independent audit receipt:
`results/hsa3_ana_0_3_independent_audit_20260923.json`.
Existing analytical cores, tests, source registries and accepted result packages
were not edited. Synthetic validation was completed and inspected before the
authorized real-artifact freeze.

## Artifact receipts

Input:
`results/hsa3_ana_0_2_response_family_final_20260923_a_results.zip`

SHA256: `00c3c052f6133456d371b2736261e469b69ba5ad91891d0ccf44d6b59a90aa5d`.

Final output:
`results/hsa3_ana_0_3_human_freeze_final_20260923_a_results.zip`

SHA256: `460b8f82764ea3c382c97ac6d382855a8a264272e7f152e60d133179f29c9ee1`.

Independent repeat:
`results/hsa3_ana_0_3_human_freeze_repeat_20260923_a_results.zip`
has the same SHA256 and every member byte.

Final synthetic:
`results/hsa3_ana_0_3_synthetic_release_20260923_a_results.zip`

SHA256: `dcbdc8cc89cc7eb48e00448784ca2fb4bf637240a509a0034e35ce5622b3960c`.

Researcher request SHA256:
`820f002b7b821b057cff743bfc9cab0e7182fc45f0c072cbe366440ad2b302b7`.
ZIPs, result directories and logs remain ignored and are not committed.

## Frozen integrity and next review

All **59 frozen human judgments**, **57 unresolved rows** and **7 A–G cases**
remain unchanged. Parentage candidates/review fields remain blank or their
original UNREVIEWED status. The historical Q1–Q5 worksheets remain immutable;
the new table separately records the current Q2–Q5 human decisions.

The three HSA2-F relations remain: 31:40 → 29:1 DIRECT_LOCAL_CLOSURE;
→ 27:1 NO_DIRECT_RELATION; → POST_DIALOGUE_JOB TERMINATES_ENCLOSING_GROUP.
The 3:2 formal-CSF negative control and 37:24 adjacency insufficiency remain.
The 24-code criteria draft is unchanged. Missing criteria concepts are notes,
not newly invented registry codes or global weights.

`09_next_hsa3_seam_review_packet.md` presents all original A–G questions and
unresolved identities. SEAM_D receives Q2/Q4/Q5 accepted evidence; SEAM_E receives
Q4/Q5 accepted evidence and Q3 unresolved-candidate evidence. Every dependency
has resolves_parentage=false. Q3 cannot resolve SEAM_E. This packet is preparation
for separately authorized researcher review. **A–G adjudication and R4.4 have
not begun.** No cross-computer byte equality is claimed beyond the recorded
Windows runs; input artifacts must be recovered at their exact hashes elsewhere.

## Repository files changed

- [.gitattributes](../.gitattributes): preserve exact researcher request bytes.
- [canonical decisions](../config/hsa3_ana_0_3_human_decisions.json).
- [stage configuration](../config/hsa3_ana_0_3_job.json).
- [researcher request](HSA3_ANA_0_3_RESEARCHER_SOURCE.txt).
- [specification](HSA3_ANA_0_3_SPEC.md).
- [execution instructions](README_MILAL_HSA3_ANA_0_3.md).
- [this validation report](HSA3_ANA_0_3_VALIDATION_REPORT.md).
- [HANDOFF](HANDOFF.md).
- [Windows runner](../scripts/run_milal_hsa3_ana_0_3_windows.ps1).
- [implementation](../src/milal_hsa3_ana_human_freeze.py).
- [tests](../tests/test_hsa3_ana_human_freeze.py).
