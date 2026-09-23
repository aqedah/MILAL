# HSA3-LAYER.0.2 validation — 2026-09-24

## Baseline and authorized result

Start commit: `a8fbd794bfec3f05132f847a8ba51f9f0e63567b`, main tracking origin/main.
Verified origin: `https://github.com/aqedah/MILAL.git`. Working tree initially clean,
no unpublished commits; `git pull --ff-only origin main` reported Already up to date.
Read AGENTS and HANDOFF before implementation, and reread after synchronization.
Authority is the byte-preserved researcher request and separate human-decision JSON.
Request SHA256: `6ba990199ed4dd0d1e9d069b5fa73646c84db250522de2f1d5d6df8c6532a74e`.

The original 57 R4.3 parent fields remain historically UNRESOLVED. After layered
review, none of these 57 requires further direct textual-parent adjudication for
current MILAL representation. This is not assignment of 57 parent edges.
Parentage-necessity review terminates without constructing a complete one-parent
tree. Job 2:11 remains a textual paragraph onset / participant-introduction unit,
with no exact parent required. Historical proposal status remains UNREVIEWED.

| Measure | Result |
| --- | ---: |
| Historical unresolved parent rows | 57 |
| P2 / P3 / P4 / P5 / P6 / P7 | 8 / 6 / 10 / 19 / 13 / 1 |
| PARENTAGE_NECESSITY_REVIEW_COMPLETED | 57 |
| Active future direct-parent questions | 0 |
| DIRECT_PARENT_EDGE_RESOLVED | 0 |
| New structural / composition relations | 0 / 0 |
| DIRECT_PARENT_NOT_REQUIRED | 14 |
| CURRENT_LAYERED_RELATIONS_SUFFICIENT | 42 |
| DIRECT_TEXTUAL_PARENT_NOT_REQUIRED | 1 |

H:HSA012 (Job 2:11) has DIRECT_TEXTUAL_PARENT_NOT_REQUIRED, historical UNRESOLVED,
and additional_parentage_review_required=false. Its accepted 2:11–13 annotation,
PARAGRAPH_ONSET, NOT_WITHIN_SECOND_TESTING_SCENE and OPENING_NARRATIVE_COMPLEX
membership remain. No new CHILD_OF, NO_PARENT assertion or parent at 1:1, 2:1,
3:1 or any other node. The exact Korean researcher rationale is preserved.

## Validation

- Python syntax validation: PASS for module and tests.
- PowerShell runner parsing and actual synthetic/real invocation: PASS.
- Stage tests: **58 PASS**, no failures/errors/skips, 17.122 seconds.
- Full suite: **1,257 PASS**, no failures/errors/skips, 246.715 test seconds
  (246.953 seconds including discovery/receipt generation).
- Synthetic self-test: **38/38 run gates PASS**.
- Real frozen-input execution: **38/38 run gates PASS**.
- Independent real invocation: **38/38 run gates PASS**; complete ZIP bytes equal.
- External release gates: **2/2 PASS**, based on the actual unittest result and
  the two independently generated ZIP byte strings, not the stage exit status.
- Every one of the 37 model gates has its own failing mutation; manifest has a
  corruption test. Both release gates have negative tests (including skip>0,
  failure/error/empty suite and ZIP mismatch/empty bytes).
- Additional negative checks cover prohibited Job 2:11 parent assignments,
  schema/identity/authority failures and real/synthetic input separation.

Logs (local/ignored):
`results/hsa3_layer_0_2_unit_final_20260924_a.log`,
`results/hsa3_layer_0_2_full_regression_final_20260924_a.log`,
`results/hsa3_layer_0_2_full_regression_final_20260924_a.json`.
The initial new-stage test incorrectly expected real package member count in the
synthetic fixture; corrected to verify its actual receipt and exact retained
bytes. No prior regression test or frozen implementation was modified.

Human-facing synthetic files 04–07 were read before empirical execution. Verified
separate human necessity vs historical parent states, exact Job 2:11 rationale,
unchanged future scope, and R4.4 contract-review-only readiness. The final synthetic
completion report matches the inspected development report bytes. New machine
CSV rows and their raw source receipts were independently checked after real runs.

## Artifacts and deterministic rerun

Input: `results/hsa3_layer_0_1_real_final_20260923_c_results.zip`

SHA256: `85232a5fae33433333b75daaac496f36836b00bd36d3ce0d9cf37d358b1a0e17`.
CRC PASS, 225 members, 14 valid manifests. No replacement input or regeneration.

Synthetic: `results/hsa3_layer_0_2_synthetic_final_20260924_a_results.zip`

SHA256: `e9b598184af722e6fe6fc2115a9b29b973e840cad3aa7166299efc9b186fa58f`.
Synthetic input has 209 members; its size is not conflated with real input size.

Real: `results/hsa3_layer_0_2_real_final_20260924_a_results.zip`

Repeat: `results/hsa3_layer_0_2_real_repeat_20260924_a_results.zip`

Both SHA256: `0754eb4c3c22e17ff59627440f8ca5aeb92ee20ecb6a7cdc197240850bb31983`.

The independent audit verified all 225 nested upstream members byte-for-byte,
237 total output members, 15 valid manifests, 160 frozen repository file hashes,
57 exact source-row receipts, all category/status counts, exact researcher
rationale, preserved canonical relation files and source request/config/code hashes.
The actual archive bytes, not merely the model digest, match between real runs.
Independent audit receipt: `results/hsa3_layer_0_2_independent_audit_20260924_a.json`.

The output root contains all ten requested files plus exact researcher source and
human-decision JSON. Crosswalk IDs address existing source member+node_id; no
historical proposal ID was invented or matched from text. Previous proposal and
historical review-required fields remain lossless, including superseded opinions.
The new necessity layer determines the current active review queue separately.

## Integrity and remaining work

All prior analytical cores and historical artifacts remain unchanged. A–G FROZEN;
ANA-Q2/Q4/Q5 accepted and ANA-Q3 UNRESOLVED/HUMAN_DEFERRED. No canonical speech node
was deleted/retyped, no role alias merged, and no local/container/global relation
was rewritten. Participant arc remains NEXT_RESEARCH_SCOPE / UNADJUDICATED;
its note is copied byte-for-byte. No 2:11–42:9 span/frame, closure or 42:10 promotion.

Readiness: PARENTAGE_NECESSITY_REVIEW_COMPLETE and
R4_4_CONTRACT_REVIEW_STILL_REQUIRED. R4.4 remains NOT STARTED. Recommend a separately
authorized R4.4 contract review preserving partial typed graphs, historical
unresolved states and separate human necessity judgments. Participant-arc study
remains a separate future task; there are no active direct-parent questions in
this 57-row necessity review. Technical validation does not imply new scholarly
acceptance beyond the decisions explicitly supplied by the researcher.

## Intended repository changes

- `src/milal_hsa3_layer_0_2.py`
- `tests/test_hsa3_layer_0_2.py`
- `config/hsa3_layer_0_2_job.json`
- `config/hsa3_layer_0_2_human_decisions.json`
- `scripts/run_milal_hsa3_layer_0_2_windows.ps1`
- `docs/HSA3_LAYER_0_2_RESEARCHER_SOURCE.txt`
- `docs/HSA3_LAYER_0_2_SPEC.md`
- `docs/HSA3_LAYER_0_2_VALIDATION_REPORT.md`
- `docs/README_MILAL_HSA3_LAYER_0_2.md`
- `docs/HANDOFF.md`
- `.gitattributes`

Commit message: `Freeze parentage necessity decisions`.
Completion commit and verified push receipt are reported after commit; no
self-referential commit hash is embedded in the committed report.
