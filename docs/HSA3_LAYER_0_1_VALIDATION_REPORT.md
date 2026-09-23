# HSA3-LAYER.0.1 validation receipt — 2026-09-23

Start commit: `45a23a833d98c1e6aa7f37824d98ac6c85768fa4`, main.
Verified origin: `https://github.com/aqedah/MILAL.git`. Startup tree was clean,
no unpublished commits, fast-forward pull already up to date.
Commit message: `Integrate HSA3 layers and audit parentage necessity`.
The end commit is the Git commit containing this receipt; the final response
records its hash and actual remote verification, avoiding self-reference.

## Implementation and methodological result

Integrated frozen HSA1–HSA3 nodes and typed relations into separate canonical
views, preserving exact IDs, original records and confirmation provenance.
Added a machine-generated necessity audit over every historical parent question.
All proposals and researcher review fields remain UNREVIEWED; no human conclusion
was entered. No direct textual parent was assigned, removed or silently resolved.

Original triage, verified directly in the frozen artifact:

| Historical category | Count |
| --- | ---: |
| KNOWN_CONTAINER_BUT_DIRECT_PARENT_UNRESOLVED | 19 |
| TRUE_GLOBAL_SEAM | 14 |
| LOCAL_RELATION_ALREADY_CONSTRAINS_STRUCTURE | 10 |
| GROUP_PARENTAGE_UNRESOLVED | 8 |
| ROLE_ALIAS_OR_SAME_TEXTUAL_LOCUS | 6 |
| Total | 57 |

Computed necessity proposals:

| Proposal | Count |
| --- | ---: |
| P2 — non-textual group | 8 |
| P3 — explicit paired roles | 6 |
| P4 — accepted local relation sufficient | 10 |
| P5 — container, peers and function sufficient | 19 |
| P6 — global layered relation sufficient | 13 |
| P7 — conservative unresolved remainder | 1 |

P7 candidate: **H:HSA012, Job 2:11**, friends arrival / participant introduction.
It has accepted composition membership and a negative exclusion, but lacks the
additional positive typed support required by the conservative global rule.
The code does not hard-code this ID or verse as P7. A test adds independent peer
support and demonstrates that the rule changes its proposal. Tests also remove
local/container/peer evidence and demonstrate movement to P7 for other nodes.

This is not a claim that 2:11 must have a textual parent or that the remainder is
the uniquely minimal scholarly set. Researchers may revise all proposals.
All **57 original direct-parent questions remain UNRESOLVED**, losslessly.

## Audited populations

Eight historical non-textual groups: CYCLE_1/2/3, DIALOGUE_CYCLE_SEQUENCE,
ELIHU_SPEECH_SEQUENCE, HUMAN_SCOPE_1_1_5, HUMAN_SCOPE_2_1_10, POST_DIALOGUE_JOB.
Actual schema determines P2; these names are reporting/regression controls only.
Their ordered members and accepted relation IDs are retained.

Six historical role rows are **three explicit pairs at 4:1, 15:1 and 22:1**:
H:HSA2-C1-S1 / H:HSA2-CYCLE-1, H:HSA2-C2-S1 / H:HSA2-CYCLE-2,
H:HSA2-C3-S1 / H:HSA2-CYCLE-3. The three speech nodes are canonical textual nodes;
the three cycle-onset records are role aliases. Both records and roles remain.
P3 concerns duplicate independent role-parent review, not speech-node deletion.

All 10 historically local, 19 known-container and 14 global-seam rows were audited.
The known-container set retains dialogue speech memberships, four Elihu onsets,
and 27:1/29:1 membership. Global set: 1:6, 1:22, 2:1, 2:10, 2:11, 3:1, 32:1,
32:2, 37:24, 38:1, 40:3, 40:6, 42:1, 42:7. Thirteen receive P6 proposals;
2:11 receives P7. Frozen seam decisions are not altered by these proposals.

## Canonical layer counts — real artifact

| View | Count | Meaning |
| --- | ---: | --- |
| Canonical nodes | 75 | 61 original + 6 accepted composition groups + 8 existing clause evidence anchors |
| Textual hierarchy/placement | 14 | 3 hierarchy edges, 10 continuation, 1 direct-local-closure |
| Textual same-level | 100 | 98 sibling rows + 2 parallel-ending rows |
| Composition groups | 14 | 8 historical + 6 already accepted A/C and F/G groups |
| Composition relations | 47 | 40 membership, 3 cycle-onset, 1 introduction, 2 termination, 1 peer |
| Transitions | 3 | component, post-speech transition, ANA-Q2 transition overlay |
| Accepted overlay/responsio | 2 | ANA-Q4/Q5 |
| Negative constraints | 27 | Exact types and dimensions retained |
| Technical navigation | 57 | Separate root links, never textual parents |
| All projected relations | 250 | Unique existing canonical IDs, including technical links |
| Unresolved/deferred | 58 | 57 original parent questions + ANA-Q3 |

Projection creates **0 human judgments, 0 structural relations, 0 composition
relations**. Existing confirmations append source links, not duplicate edges.
Source automatic technical/derived authority remains distinguishable from human
authority. Original dimensions remain intact, including ANA-Q2 TRANSITION_OVERLAY.

The matrix preserves seven requested major components. It traverses only exact
membership paths for context, never infers a new transitive edge or textual parent.
Shared ANA/BHSA verbal-word witnesses are report context, not canonical endpoint
identity. Scope/endpoint fields in the canonical overlay records are unchanged.

## Validation

- Syntax: new module and tests compile PASS.
- New stage tests: **66 PASS**, skip 0; final unit run 33.707 seconds.
- Full regression: **1,199 tests PASS**, skip 0, 241.350 seconds; includes all
  1,133 previous tests and the 66 new tests on the final code.
- Final synthetic Windows-runner self-test: **36/36 gates PASS**.
- Synthetic review packet and layered summary inspected before real execution.
- Real frozen-artifact validation and independent invocation: **36/36 gates PASS**
  in each; complete result ZIP bytes identical.
- Negative coverage: all 35 model/input gates plus manifest corruption test.
- Independent audit: **225 members, 14 manifests, 676 exact source-row links,
  152 frozen repository pins, 202 unchanged upstream members**, ZIP CRC PASS;
  all report links resolve and relation files partition canonical IDs exactly.
  The D/E JSON scope annotation and its source hash/pointer were also verified.

Logs: `results/hsa3_layer_0_1_unit_final_c.log` and
`results/hsa3_layer_0_1_full_regression_final_c.log`.
Earlier synthetic runs remain local but are superseded by the final artifact.
No tests were weakened or skipped. No fresh BHSA or marker extraction occurred.

## Final artifacts

Synthetic: `results/hsa3_layer_0_1_synthetic_final_20260923_c_results.zip`

SHA256: `f559d211a2193c7260afa51e751226ac983a5ef7bd0094c05674a1d21e8316f4`

Real: `results/hsa3_layer_0_1_real_final_20260923_c_results.zip`

SHA256: `85232a5fae33433333b75daaac496f36836b00bd36d3ce0d9cf37d358b1a0e17`

Repeat: `results/hsa3_layer_0_1_real_repeat_20260923_c_results.zip`, identical SHA256.

Review packet: `results/hsa3_layer_0_1_real_final_20260923_c/16_researcher_review_packet.md`.
Layered matrix: `results/hsa3_layer_0_1_real_final_20260923_c/12_hsa3_complete_layered_matrix.csv`.
Layered summary: `results/hsa3_layer_0_1_real_final_20260923_c/13_hsa3_complete_layered_summary.md`.
All 19 requested outputs plus four provenance/navigation additions are present.
Generated files, ZIPs, logs, and local independent audit script remain ignored.

## Files changed

- `.gitattributes`
- `config/hsa3_layer_0_1_job.json`
- `docs/HANDOFF.md`
- `docs/HSA3_LAYER_0_1_RESEARCHER_SOURCE.txt`
- `docs/HSA3_LAYER_0_1_SPEC.md`
- `docs/HSA3_LAYER_0_1_VALIDATION_REPORT.md`
- `docs/README_MILAL_HSA3_LAYER_0_1.md`
- `scripts/run_milal_hsa3_layer_0_1_windows.ps1`
- `src/milal_hsa3_layer_0_1.py`
- `tests/test_hsa3_layer_0_1.py`

## Frozen layers and readiness

No frozen analytical core changed. All A–G FROZEN decisions, HSA2-F, accepted
ANA-Q2/Q4/Q5, deferred ANA-Q3 and all historical artifacts are preserved.
The original 57 unanswered fields are not a structural-completeness score.

FRIENDS_ENTRY_RESOLUTION_PARTICIPANT_ARC is NEXT_RESEARCH_SCOPE only: separate
2:11–13 and 42:7–9 windows, with participant continuity, adjudication/obedience,
42:10 restoration, 32:1–5, possible חרה אף correspondence and narrator voice as
future questions. No accepted frame/span, parentage or 42:10 boundary is created.

R4.4: DESIGN_CONTRACT_REVIEW_REQUIRED, implementation NOT STARTED. No implemented
repository contract establishes a parent-complete-tree requirement. Such a
requirement would conflict with the accepted layered representation. Recommend
a versioned consumer contract preserving the partial textual graph, composition,
transition, overlays, negatives, technical links, provenance and unresolved states.
Lossless consumption without resolving 57 parents is feasible in principle;
this is not an empirical R4.4 validation or authorization to implement it.
Next: researcher reviews necessity proposals and separately authorizes future scope.
