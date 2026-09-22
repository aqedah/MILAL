# HSA3-PREP validation — 2026-09-22

Starting commit: `b7834a76dceae046e4b83821445353793318a056` (R4.3 baseline).
Execution: Windows repository Python, accepted artifacts only; no BHSA re-extraction.
Active specification: [HSA3_PREP_SPEC.md](HSA3_PREP_SPEC.md).

## Methodological result

All **57/57** original unresolved direct-parent rows are crosswalked with original
row number/hash, one primary review assignment and every overlapping case. All
59 human judgments, 61 nodes, 205 original edges and three settled hierarchy
relations remain unchanged. No new human judgment, parentage, closure, permanent
role relation, MR1 rule or candidate ranking was created. No accepted decision is
reopened. HSA1/HSA2/HSA2-F/R4.3 remain frozen.

The data support **seven distinct open-attachment review scopes A–G**, plus the H
whole-book summary. They do **not** establish that exactly seven independent
atomic judgments will complete parentage. Primary case ownership schedules review;
it does not settle a parent or guarantee that one decision resolves all dependent
rows. Cases overlap. This distinction prevents replacing 57 unsupported independent
decisions with a different unsupported fixed decision count.

## Exclusive triage partition

| Category | Rows |
| --- | ---: |
| TRUE_GLOBAL_SEAM | 14 |
| ROLE_ALIAS_OR_SAME_TEXTUAL_LOCUS | 6 |
| KNOWN_CONTAINER_BUT_DIRECT_PARENT_UNRESOLVED | 19 |
| GROUP_PARENTAGE_UNRESOLVED | 8 |
| LOCAL_RELATION_ALREADY_CONSTRAINS_STRUCTURE | 10 |
| TECHNICAL_OR_REPRESENTATIONAL_CASE | 0 |
| Total | 57 |

All 61 nodes were audited. Exactly three duplicated textual loci were found:
4:1 (H:HSA2-C1-S1 / H:HSA2-CYCLE-1), 15:1 (H:HSA2-C2-S1 /
H:HSA2-CYCLE-2), 22:1 (H:HSA2-C3-S1 / H:HSA2-CYCLE-3). Each retains its
SPEECH_UNIT_ONSET and DIALOGUE_CYCLE_ONSET, distinct judgment records and shared
exact source evidence. No historical role record was merged or deleted. Reference
equality is only an audit trigger; explicit authorization and shared evidence are
required. No additional textual duplicate locus was found.

There are **22 textual speech members** (16 cycle + 4 Elihu + 2 post-dialogue).
Three are counted in the role category instead, leaving 19 in the exclusive
membership category. The three cycle groups additionally belong to the dialogue
sequence; their category remains GROUP_PARENTAGE_UNRESOLVED.

Local cases: 1:5; 1:14/16/17/18; 2:9; 11:4; 28:1; 42:16 (nine continuations),
plus 31:40 (settled local/higher termination; parent representation still open).
3:2 is already hierarchically resolved and appears only as contextual evidence,
not a 58th unresolved row.

The 14 remaining textual global participants are 1:6, 1:22, 2:1, 2:10, 2:11,
3:1, 32:1, 32:2–5, 37:24, 38:1, 40:3, 40:6, 42:1 and 42:7. Their already
known functions, sibling/parallel-ending relations and introduction remain intact.
They are coordinated across the cases below, not asserted to require 14 unrelated
decisions.

## Complete case inventory

References identify review loci, not newly inferred unit coverage.

| Case | Main question / loci | Primary rows | Participating rows |
| --- | --- | ---: | ---: |
| SEAM_A | Opening/testing scopes; 1:6, 1:13, 1:22, 2:1, 2:10, 2:11, 3:1/2 and dependent local events | 13 | 14 |
| SEAM_B | Independent 3:1 above 3:2 and entry at 4:1 into DIALOGUE_CYCLE_SEQUENCE | 1 | 25 |
| SEAM_C | CYCLE_1/2/3 (4:1/15:1/22:1; last 26:1) versus POST_DIALOGUE_JOB (27:1/29:1/31:40) | 29 | 29 |
| SEAM_D | 31:40, 32:1, 32:2–5, Elihu 32:6/34:1/35:1/36:1 and 37:24 | 8 | 13 |
| SEAM_E | Elihu 36:1/37:24 and YHWH 38:1 interface | 0 | 3 |
| SEAM_F | 38:1, 40:1, 40:3, 40:6, 42:1 higher organization | 4 | 4 |
| SEAM_G | 40:6/42:1 to 42:7 final narrative, with 42:16 continuation | 2 | 4 |
| SEAM_H | Whole-book summary of A–G; not another independent case/tree | — | — |
| Total primary assignment | Exact partition, no silent disappearance | 57 | Overlaps allowed |

E has no exclusively assigned rows because its three participants are already
assigned to D/F. Its interface question is still preserved. H does not duplicate
the primary assignments. Eight non-textual groups are separately audited with
origin, explicit members, human IDs, relation IDs, dependent rows and open
parent-representation questions; none becomes a textual boundary.

Preserved: cycles 6/6/4, no Zophar III, 3:1 outside Cycle 1, 27:1/29:1 peers,
28:1 continuation, all three HSA2-F 31:40 relations. The introduction at 32:2–5
is not a peer speech with 32:6–37:24; its introduced/subordinate organization is
fixed while exact node parentage remains open. Elihu's four speeches remain peers.
No closure target is invented for 37:24. YHWH/Job peer pairs and 40:1 child relation
remain; response, adjacency and speaker alternation generate no parent. 42:7 and
42:16 retain their functions; 42:10/42:12 are not promoted.

## Validation

- Python AST: both new modules PASS; Windows PowerShell parser PASS.
- Full regression: **679 PASS, zero skips** (625 previous + 54 HSA3-PREP),
  final run 96.914 seconds. No old test changed or weakened.
- Stage tests: 54 PASS, including synthetic triage, extra-case discovery,
  ambiguous-owner non-ranking, reference-only identity rejection, missing-row
  rejection, 3:2 context, closure preservation and independent in-memory copies.
- Gates: **35/35 PASS** in final synthetic and both accepted-real runs.
  All 34 model/source gates have named negative mutations; the manifest gate has
  its own corruption test. No unconditional PASS gate.
- Final synthetic packet equals the manually inspected prior synthetic packet;
  review response fields are blank except UNREVIEWED.
- Frozen raw SHA256: **82/82 unchanged**; independently compared to baseline Git
  objects using Git's configured clean normalization as a separate identity check.
- Input archive receipts: **11**, all exact SHA256; accepted source chain CRC,
  manifests/status and original human bytes verified.
- Evidence: **3,992 case/source links**, each independently resolved to the exact
  original member and row with both hashes checked. Raw upstream locators retained.
- Exact dependency paths resolve to original typed R4.3 edges. The full original
  50-file R4.3 package remains byte-identical inside the result.
- Independent final runs: **62/62 files and complete ZIP byte-identical**.
- Outer plus four nested manifests, ZIP CRC and extracted disk bytes PASS.
- Human-facing packet inspected for questions, local/group/role constraints,
  source IDs, three accepted early-Job frames, blank review fields and all 57 rows.
  No later frame is manufactured when the accepted linkage supplies none.
- Termux instructions supplied; no Termux empirical execution claimed.

## Artifacts

- Synthetic: `results/hsa3_prep_synthetic_final2_20260922/`
- Final: `results/hsa3_prep_global_seams_final2_20260922_a/`
- Independent rerun: `results/hsa3_prep_global_seams_final2_20260922_b/`
- Packet: `results/hsa3_prep_global_seams_final2_20260922_a/04_global_seam_review_packet.md`
- ZIP: `results/hsa3_prep_global_seams_final2_20260922_a_results.zip`
- Log: `results/hsa3_prep_global_seams_final2_20260922_a_run.log`

Final ZIP SHA256:
`06e41a935d1ccb18eed1b1773d4ca04a493a097533e36cf2875f741fa116cc77`.
ZIP size: 3,636,724 bytes. The first exploratory real package and earlier synthetic
package remain ignored local validation artifacts; the `final2` paths above are
the deliverables corresponding to the final code/config hashes. The new JSON was
normalized to repository LF policy before these final runs; its parsed content
and all review outputs are unchanged. The 54 stage tests passed again afterward.

Next: researcher human adjudication of A–G with H as the whole-book summary.
Explicit unresolved/insufficient-evidence outcomes remain valid. R4.4 hierarchy
recompilation must wait until that review is complete.
