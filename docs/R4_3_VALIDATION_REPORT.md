# R4.3 validation — 2026-09-22

Baseline: `f41095917d1deaa718df553f4919e41969601ce7`, clean main synchronized by
`git pull --ff-only origin main`. The researcher authorized the partial scaffold,
synthetic and accepted-real validation, deterministic rerun, and commit/push.

## Implemented and methodological meaning

Compiled all **HSA1 31 + HSA2 25 + HSA2-F 3 = 59 original human records**, preserving
all historical fields, source IDs and original UNRESOLVED states. No new human
adjudication was invented. Four explicit named restatements map to existing scaffold
nodes, with every original record independently retained in the accounting table.

This is the first whole-book **partial** hierarchy scaffold, not a completed tree.
Hierarchy, continuation, group membership, horizontal relations, local closure,
higher termination, descriptive introduction/transition and technical attachments
remain distinct. Response/adjacency never creates parentage. Known membership or
continuation does not automatically settle the separate direct-parent question.

## Counts

**61 nodes**, including one technical root and **8 non-textual groups** (6 HUMAN_GROUP
and **2 DERIVED_SCAFFOLD_GROUP**). Node types:

| Type | Count |
| --- | ---: |
| TECHNICAL_ROOT | 1 |
| TEXTUAL_ANCHOR | 11 |
| SPEECH_UNIT | 29 |
| SCENE_UNIT | 3 |
| PARAGRAPH_UNIT | 2 |
| TRANSITION_UNIT | 7 |
| HUMAN_GROUP | 6 |
| DERIVED_SCAFFOLD_GROUP | 2 |
| UNRESOLVED_UNIT | 0 |

Known-function nodes keep their structural type even when parentage is unresolved.
These counts are neither detected boundary counts nor new human judgment counts.

**205 edges**, with **3 resolved hierarchical parent edges**, **25 membership edges**,
**57 technical links** and **120 other typed overlays**:

| Class | Type counts | Total |
| --- | --- | ---: |
| HIERARCHY | CHILD_OF 2; HIERARCHICALLY_ABOVE 1 | 3 |
| CONTINUATION | CONTINUES_WITHIN 10 | 10 |
| MEMBERSHIP | GROUP_MEMBER_OF 25 | 25 |
| HORIZONTAL | SAME_LEVEL_SIBLING 98 | 98 |
| CLOSURE_COMPARISON | PARALLEL_ENDING 2 | 2 |
| LOCAL_CLOSURE | DIRECT_LOCAL_CLOSURE 1 | 1 |
| HIGHER_TERMINATION | TERMINATES_ENCLOSING_GROUP 1 | 1 |
| NEGATIVE | NO_DIRECT_RELATION 1; NO_BOUNDARY 2 | 3 |
| DESCRIPTIVE | CYCLE_ONSET_OF 3; NARRATIVE_INTRODUCTION 1; TRANSITION_COMPONENT 1 | 5 |
| TECHNICAL | TECHNICAL_ROOT_LINK 57 | 57 |
| RESPONSE_OVERLAY | No new response antecedent asserted | 0 |

The three resolved parent edges are exactly **1:13 CHILD_OF 1:6**, **3:1
HIERARCHICALLY_ABOVE 3:2**, and **40:1 CHILD_OF 38:1**. Direct reciprocal/sibling
relations remain distinct; only identical mapped edge keys are combined while
preserving all contributing human IDs. Provenance table: **355 node/edge→human links**.

## Preserved structures

- Dialogue cycles: 6 / 6 / 4 in the supplied member order; all within-cycle peers
  and the three cycle-onset peer relations survive. No Zophar III or placeholder.
  3:1 remains independent before the cycles; 11:4 remains internal to 11:1.
- 27:1/29:1 remain peers with original TAKE_MASHAL+AMR evidence; 28:1 continues
  within 27:1 without becoming a boundary. HSA2-F activates 31:40→29:1 local closure,
  rejects 31:40→27:1 direct closure, and separately terminates POST_DIALOGUE_JOB.
  An unresolved **parent of the ending node** does not reopen its resolved closure target.
- 32:1 remains transition; 32:2–5 introduces ELIHU_SPEECH_SEQUENCE descriptively,
  without making the introduction a peer speech or forcing its global parent.
  32:6/34:1/35:1/36:1 remain peer members. 37:24 remains ending context without a
  newly assigned direct target or adjacency-derived link to 38:1.
- YHWH 38:1/40:6 remain peers; 40:1 remains child of 38:1. Job 40:3/42:1 remain peers.
  No response antecedent or adjacent ending is converted into a hierarchical parent.
- 42:7 remains final paragraph/narrative onset; 42:16 continues within it. Neither
  42:10 nor 42:12 is promoted. No unsupported 42:7–17 frame node is created.
- All Job 1–3 scene/continuation/parallel-ending judgments survive; 1:22/2:10
  remain human parallel endings, not new MR1 explicit closures.

## All unresolved global seams

**57 direct-parent cases = 49 textual-locus nodes + 8 non-textual groups**.
Each case has its own CSV row with known relations, source judgments/evidence, reason,
and later human-review requirement. These are not 57 newly discovered ambiguities:
many have known membership/continuation, which remains explicit.

The following exhaustive grouping names every remaining case:

| Cases | Nodes/loci whose direct parent remains unresolved |
| ---: | --- |
| 8 groups | CYCLE_1, CYCLE_2, CYCLE_3, DIALOGUE_CYCLE_SEQUENCE, ELIHU_SPEECH_SEQUENCE, POST_DIALOGUE_JOB, HUMAN_SCOPE_1_1_5, HUMAN_SCOPE_2_1_10 |
| 12 early Job loci | 1:5; 1:6; 1:14; 1:16; 1:17; 1:18; 1:22; 2:1; 2:9; 2:10; 2:11; 3:1 |
| 6 cycle-1 speeches | 4:1; 6:1; 8:1; 9:1; 11:1; 12:1 |
| 6 cycle-2 speeches | 15:1; 16:1; 18:1; 19:1; 20:1; 21:1 |
| 4 cycle-3 speeches | 22:1; 23:1; 25:1; 26:1 |
| 3 distinct cycle-onset anchors | 4:1; 15:1; 22:1 (different human IDs from the speech-onset records above) |
| 1 internal expression | 11:4 |
| 4 late Job loci | 27:1; 28:1; 29:1; 31:40 |
| 7 transition/Elihu loci | 32:1; 32:2–5; 32:6; 34:1; 35:1; 36:1; 37:24 |
| 4 YHWH/Job loci | 38:1; 40:3; 40:6; 42:1 |
| 2 final-narrative loci | 42:7; 42:16 |

Accepted frame context is available only for the three early-Job candidate frames
already in R4.2. The exact participant-event context join neither proves whole-unit
containment nor assigns a parent. No larger 32:1-ending or 42:7–17 frame is fabricated.
All 57 rows are printed in the report's UNRESOLVED GLOBAL SEAMS section; no ranking.

## Validation

- Python syntax and PowerShell parser: PASS.
- Full regression: **625 PASS, zero skips** (566 previous + **59 R4.3 tests**).
- Synthetic self-test through the Windows runner: **41/41 gates PASS**.
- Both accepted-real independent processes: **41/41 gates PASS** each.
- Every gate has a negative mutation: 40 data/model gates plus serialized manifest.
  The mutations test fabricated parent edges, closure conflation, dropped history,
  missing provenance, omitted unresolved cases, forbidden boundaries and other invariants.
- During development, negative mutations exposed shared in-memory references in
  accounting/provenance objects; these now use independent copies. All mutation
  tests pass. No historical disk file was written and no unsupported parent was published.
- Exact **75/75 frozen local file SHA256** checks passed before/after execution.
  Independent Git baseline comparison also passed with Git's configured clean
  conversion; historical checkout line-ending differences were not rewritten.
- **10 accepted input ZIPs** verified. HSA1's 10 members and HSA2-F's 25 members
  (including all 17 original HSA2 members) remain byte-identical in the result.
  The two accepted R4.2 frame/context source tables also remain unchanged.
- **50/50 files and the complete ZIP are byte-identical** between independent runs.
  Outer manifest, all three nested historical manifests, CRC and disk integrity PASS.
- Independently resolved all **355 provenance links** to exact member/row hashes;
  every nontechnical edge and non-root node has human source provenance.
- Unresolved table exactly matches the 57 node statuses; graph connectivity to the
  technical root and acyclic hierarchical edges were independently verified.
- Manually inspected the synthetic and accepted-real Markdown: memberships are
  labeled MEMBERSHIP ONLY, the three explicit parent edges are labeled RESOLVED,
  all unresolved nodes remain visible, and introduction/closure overlays do not
  visually assert additional parentage.

No new BHSA extraction or analytical core modification. Windows execution is
empirically validated; Termux instructions are provided, not claimed executed.
Historical exact checkout-byte pins can require investigation on another platform.

## Artifacts

- Synthetic: `results/r4_3_synthetic_final_20260922/`
- Accepted A: `results/r4_3_whole_book_scaffold_20260922_a/`
- Independent B: `results/r4_3_whole_book_scaffold_20260922_b/`
- ZIP: `results/r4_3_whole_book_scaffold_20260922_a_results.zip` (1,713,877 bytes)
- Log: `results/r4_3_whole_book_scaffold_20260922_a_run.log`
- SHA256: `d8fc0227c6bd35517b0dea1d53b205517ad8a8308b5954486215a00955cba4f7`

Only source, config, tests, runner and documentation are committed. Results, ZIPs,
logs and temporary scripts remain ignored. HSA1/HSA2/HSA2-F and earlier analytical
cores are unchanged. Next task: human review of the explicit unresolved global seams.
