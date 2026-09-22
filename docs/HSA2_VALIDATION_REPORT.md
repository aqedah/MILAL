# HSA2 validation — 2026-09-22

Starting commit: `28892b3f0ecab3d42749ab50d8a65bc4aa9e09c5`. Clean main was
fast-forward synchronized with `https://github.com/aqedah/MILAL.git`; already current.
The completion commit is the commit containing this report.

## Human records and direct relations

25 HSA2 records append new decisions/context without replacing HSA1: 16 cycle
speech-unit onsets, 3 separate cycle-onset judgments, initial Job 3:1 context,
internal 11:4, and 27:1 / 28:1 / 29:1 / 31:40. All are researcher-supplied REVIEWED
records. The same reference can have separate speech and cycle judgments with
distinct IDs. Machine evidence does not create or complete these human fields.

83 directed direct relation pairs: 80 SAME_LEVEL_SIBLING, 2 CONTINUES_WITHIN,
1 HIERARCHICALLY_ABOVE. Reciprocal peers are counted twice. The 80 peer pairs
comprise 30 + 30 + 12 within cycles, 6 between cycle onsets and 2 between 27:1/29:1.
No inverse/transitive completion or whole-book parent graph is generated.
No pair leaves 31:40 toward either opening.

Cycle 1: 4:1 Eliphaz, 6:1 Job, 8:1 Bildad, 9:1 Job, 11:1 Zophar, 12:1 Job.
Cycle 2: 15:1 Eliphaz, 16:1 Job, 18:1 Bildad, 19:1 Job, 20:1 Zophar, 21:1 Job.
Cycle 3: 22:1 Eliphaz, 23:1 Job, 25:1 Bildad, 26:1 Job; incomplete, with no
corresponding third Zophar speech generated. These are human structural assertions.
Source onsets remain ANSWER+AMR. 11:4 retains its SIMPLE_AMR identity as an internal
expression, not an additional peer speech unit. No closing edge follows chapter 26.

## Accepted-source findings

All seven accepted ZIP pins/CRCs/manifests/gates and exact upstream locators verified.
HSA2 reuses the accepted BHSA 2021 snapshot and PROV1 provenance; no extraction or
new direct Text-Fabric run occurred. Embedded historical R2 provenance is preserved,
not represented as a newly verified standalone R2 ZIP.

1968 exact source/context links: 1030 attached to human judgments, 938 to focused
audit contexts/range markers; 1680 unique evidence IDs. All 25 human records have
exact links. Full source rows and locators remain available. There are 700 exact
G0–G6 signature rows for 100 atoms, 23 marker/control scopes and 377 formal edge
relation rows. 28:28 and 29:18 internal MR1 events remain present in the focused
review range and machine-readable source links. CASE025/S02135 remain traceable.

| Point | Exact source | Descriptive finding |
| --- | --- | --- |
| 27:1 | clauses 499251/499252/499253; atoms 589377/589378/589379; MR1 csf 39 | TAKE_MASHAL+AMR |
| 29:1 | clauses 499383/499384/499385; atoms 589510/589511/589512; MR1 csf 41 | TAKE_MASHAL+AMR; all 21 corresponding atom/level hashes equal 27:1 |
| 31:40 | ending clause 499623, atom 589751; MR1 תממ+דבר closure | תמו דברי איוב; exact lexemes TMM[, DBR/, >JWB/; no MCL/ |

The two openings have the same linguistic formula. This is consistent with the
researcher's same-level judgment. 28:1 remains the supplied NO_BOUNDARY /
CONTINUES_WITHIN 27:1 decision, not a new MR1 negative rule. The ending's absence
of משל is recorded without inferring semantic equivalence or inequality.

Formal edge rows at the three exact marker spans:

| Point | All occurrences | Starts at start | Ends at end | Crosses start | Crosses end |
| --- | --- | --- | --- | --- | --- |
| 27:1 | 22 | 7 | 8 | 1 | 2 |
| 29:1 | 22 | 7 | 8 | 1 | 2 |
| 31:40 | 6 | 4 | 5 | 2 | 1 |

Labels overlap; these are inventory counts, not scores. At 31:40 the crossing-end
G0 occurrence includes atom 589752 (32:1); such overlap neither erases the ending
nor identifies which opening it directly closes. Marker identity, lexical facts
and repeated formal patterns do not encode an opening-to-ending target relation.
**These data do not establish a preference between the two direct-target options.**
No proximity, chapter, topic, commentary or span-length preference was applied.

Three separately identified UNREVIEWED candidates remain: direct closure of 29:1,
direct closure of the complex beginning at 27:1, enclosing termination of the
27:1–31:40 group. All selected relations, direct target fields and higher-order
terminal-effect fields remain UNRESOLVED. The schema permits local and higher
effects together; a test demonstrates coexistence without changing real records.

## Verification

- Syntax: all three new Python files PASS.
- Full regression: **529 PASS**, zero failures/errors/skips (482 prior + 47 HSA2),
  completed in 75.303 seconds.
- HSA2 stage coverage: **47 tests**, including an explicit one-to-one gate-negative
  mapping check. All **31 gates**, including manifest, have negative tests.
- Final synthetic: **31/31 PASS**, human-facing report inspected and visibly marked
  SYNTHETIC_AUDIT_ONLY with fictional source identities.
- Both final accepted-real audits: **31/31 PASS**.
- Independent processes: **17/17 files and ZIP byte-identical**; exact manifests,
  ZIP CRC and disk contents verified. Human CSV/Markdown copies are byte-identical
  to their Git-tracked sources and use repository LF behavior.
- `04_job_27_31_closure_target_audit.md` manually inspected: 305 lines / 25438 bytes;
  surfaces, IDs, adjacent full verses, signatures, all edge patterns, candidate
  options, comparison controls and explicit UNRESOLVED conclusions are visible.
- Comparative 1:22/2:10 remain non-MR1 endings, and 2:10 retains both its actual
  CSF scope and the separately labeled full-verse human comparison context.
- 10 negative controls retain missing-Zophar, internal-11:4, no chapter-26 closing
  edge, peer-29:1, no-boundary-28:1, unresolved-target, no heuristic, independent
  dimensions, non-MR1 endings and no whole-book hierarchy constraints.

During pre-commit inspection, discontinuous clause membership at 28:28 showed why
clause lists must not be flattened to establish atom order. HSA2 now uses explicit
PROV1 `atom_index_1based`, verifies the full index inventory and all 12722 accepted
formal occurrence start/end indexes. A discontinuous-clause test, conflicting-index
test and native-order negative gate cover this. Final focused report content was
byte-identical to the inspected preliminary report; no closure judgment changed.
This was a correction to unpublished HSA2 code, not a change to any frozen layer.

## Frozen sources and final package

HSA1 records were checked against both frozen hashes and Git bytes at `28892b3`:

- CSV SHA256: `56e39b1470229ce29df77ecdf875b36072979ba668a8766c7c87fdfab45693c0`
- Markdown SHA256: `bba752ef6f1ac17f2d82085ae82127d94c2040b2703d7f039c99750f907c3479`

HSA1 code/tests/config and MR1/R4 modules also retain their pinned bytes. Existing
human records, analytical cores and accepted result ZIPs remain unchanged.

- Synthetic: `results/hsa2_synthetic_final2_20260922/`
- Final: `results/hsa2_dialogue_structure_final_20260922_a/`
- Rerun: `results/hsa2_dialogue_structure_final_20260922_b/`
- ZIP: `results/hsa2_dialogue_structure_final_20260922_a_results.zip`
- Log: `results/hsa2_dialogue_structure_final_20260922_a_run.log`
- ZIP bytes: **989268**
- SHA256: `669018ceacacef21db426028854ea1f88879a446d4d4ca113d24bec6ef8f2994`

Earlier exploratory artifacts are not the final package. Inputs, result directories,
ZIPs, logs and one-time authoring utilities remain ignored. Tracked changes are
limited to HSA2 source/config/tests, new human registry/spec/usage/report and HANDOFF.

Next required human review: **31:40 direct closure target and the separate possible
enclosing terminal effect**. Job 3–26 cycle review is recorded, but whole-book
**R4.3 parentage remains blocked on closure-target review**.
