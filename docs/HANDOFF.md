# MILAL Development Handoff

## Current task — HSA3-ANA.0.2 evidence addendum and criteria draft complete, 2026-09-23

Active specification: [HSA3_ANA_0_2_SPEC.md](HSA3_ANA_0_2_SPEC.md); execution:
[README_MILAL_HSA3_ANA_0_2.md](README_MILAL_HSA3_ANA_0_2.md); validation:
[HSA3_ANA_0_2_VALIDATION_REPORT.md](HSA3_ANA_0_2_VALIDATION_REPORT.md); methodology:
[HSA_ADJUDICATION_CRITERIA_REGISTRY.md](HSA_ADJUDICATION_CRITERIA_REGISTRY.md).
Starting HEAD: `51d9c5e04b1d4ef148b401d48a69aa7d565e6d37`.
The researcher authorized this addendum, criteria draft, synthetic/actual BHSA
validation, deterministic rerun and commit/push after passing tests.

**HSA3 A–G and ANA-Q2–Q5 remain unadjudicated. R4.4 is not started.**
0.1 is a frozen artifact; its 78 files and four original candidates are preserved
byte-for-byte. No real 0.1 regeneration occurred. The new source loader reuses
the frozen BHSA helper and requires an identical native snapshot/feature hashes.

Four distinct evidence layers remain separate. Verbal ענה: 62 frozen records
(60 answer + 2 non-answer). Broad nominal spelling/root screen: 32 records,
including **2 answer nouns at 32:3/5** and 30 excluded similar forms/root hits.
The lex_utf8 spelling מענה also denotes two distinct hiding-place nouns at
37:8/38:40; these are not answer-family members. Answer-noun root is unavailable,
not inferred. Whole-book שוב verbs: **39** (38 CWB[ + 1 CWB=[); provisional
senses: **7 reply, 16 return/restore, 4 other, 12 unresolved**.

The 32:1–33:14 cluster has 14 rows: verbal 9, nominal 2, reply-neighbor 2,
context-reframing candidate 1. 33:14 דבר is only POSSIBLE_RESPONSE_REFRAMING,
not core family or a response lexicon. 32:13 stays context-only; 36:1 stays
NO_ANA / ADD_SPEECH. Original 32:3/5 NO_ANA classifications are unchanged.

ANA-C1–C4 remain UNADJUDICATED and automatic_resolution=false. C4 keeps its
original type and gains only a separate UNADJUDICATED refinement label:
ELIHU_RESPONSE_ROLE_INTERVENTION. POSITIONAL_ONLY and RESPONSE_ROLE_INTERVENTION
remain unselected. New human judgments and structural relations are both **0**.
59 frozen human judgments, 57 unresolved rows, A–G and the three HSA2-F closure
relations remain intact; all prior analytical cores are unchanged.

Criteria **draft**: seven relation dimensions, 24 evidence codes, 21 frozen
judgment example crosswalks. No numerical weighting or global priority ranking.
BHSA syntax is corroboration, never automatic MILAL parentage. Crosswalk mappings
are illustrative, not new judgments or reconstructed unstated researcher reasoning.

Validation: **70 new / 807 total tests**, skip 0; **30/30 synthetic and actual
gates**, all with negative coverage. Final independent-process ZIP and all
97 members are byte-identical. Verified 97 frozen file hashes, 70 BHSA feature
hashes, 7 manifests, 155 row links, 4 candidate links and 2 seam-dependency links.

Final local artifact:
`results/hsa3_ana_0_2_response_family_final_20260923_a_results.zip`
SHA256 `00c3c052f6133456d371b2736261e469b69ba5ad91891d0ccf44d6b59a90aa5d`.
All result/data/log files remain ignored by Git.

**Next: researcher ANA-Q2–Q5 review using the new evidence packet.**
Q2 post-closure transition; Q3 long-distance response; Q4 contrastive frame;
Q5 positional interval versus response-role intervention. Preserve UNRESOLVED /
INSUFFICIENT_EVIDENCE when warranted. Q1 is the frozen 3:2 counterexample.
Do not recompile hierarchy or begin R4.4 before separate authorization.

## Previous task — HSA3-ANA.0.1 source audit complete, 2026-09-23

Active specification: [HSA3_ANA_0_1_SPEC.md](HSA3_ANA_0_1_SPEC.md); execution:
[README_MILAL_HSA3_ANA.md](README_MILAL_HSA3_ANA.md); results:
[HSA3_ANA_0_1_VALIDATION_REPORT.md](HSA3_ANA_0_1_VALIDATION_REPORT.md).
Starting HEAD: `f1292ba51b90fd545069741ee5ccce3d63d9704a` (HSA3-PREP complete).
The researcher authorized this independent linguistic audit, actual BHSA 2021,
deterministic rerun and commit/push after successful validation.

**HSA3 A–G remain unadjudicated. R4.4 is not started or authorized.**
Whole-book BHSA 2021 / Text-Fabric 13.1.0 scan: 10,912 words, 2,938 clauses,
62 ענה occurrences = 60 answer lexeme + 2 separate be-lowly homonyms.
Construction counts and explicit limitations are in the validation report.
3:2 remains the formal-CSF/nonreply control; 36:1 is NO_ANA / ADD_SPEECH.
31:35 is a contextual request; 32:1 has cessation with explicit target Job;
38:1 has an explicit YHWH subject and Job object. No long-distance antecedent,
שדי=יהוה equivalence, Elihu fourth-friend identity or parentage is inferred.

Four hypotheses ANA-C1–C4 remain UNADJUDICATED with automatic_resolution=false:
post-closure transition 31:40→32:1; long-distance response 31:35→38:1;
contrastive frame 32:1→38:1; Elihu within that positional interval.
**Next: researcher ANA-Q2–Q5 review of those four questions.** ANA-Q1 displays
the frozen 3:2 control only. Source-supported relation / UNRESOLVED /
INSUFFICIENT_EVIDENCE are the allowed human outcomes. SEAM_D/E receive an
evidence-dependency addendum only; original A–G cases and review fields are unchanged.

Frozen preservation: 89 repository files; 12 exact accepted upstream ZIPs;
all 62 PREP archive members; 59 human judgments, 61 nodes, 205 relations and
57 unresolved parent rows. New human judgments and structural relations: both 0.
The three HSA2-F closure decisions and all prior analytical cores remain intact.

Validation: 58 new tests; 737 full regression tests; zero skips; 32/32 synthetic
and actual gates, each with negative coverage. Independent actual rerun is
byte-identical across the ZIP and all 78 members. Six nested/current manifests,
251 evidence-row links, ZIP CRCs and all frozen/source hashes passed.

Final local artifact:
`results/hsa3_ana_0_1_response_frame_final_20260923_a_results.zip`
SHA256 `b7238ddcb0ee0940bd6a397a23bbef95a18da0dacb5af98e2b1b17396eb89294`.
It is technical evidence for review, not an accepted final hierarchy.
All result ZIPs/directories/logs and BHSA data remain outside Git tracking.

## Previous task — HSA3-PREP global structural seam review preparation, 2026-09-22

Active specification: [HSA3_PREP_SPEC.md](HSA3_PREP_SPEC.md); execution:
[README_MILAL_HSA3_PREP.md](README_MILAL_HSA3_PREP.md); results:
[HSA3_PREP_VALIDATION_REPORT.md](HSA3_PREP_VALIDATION_REPORT.md).
Starting HEAD: `b7834a76dceae046e4b83821445353793318a056`.
The researcher authorized review-only triage, synthetic/accepted-real audit,
deterministic rerun and commit/push. **HSA1/HSA2/HSA2-F and R4.3 are frozen.**

**R4.3 still contains 57 unresolved direct-parent rows. HSA3-PREP adjudicates none.**
All 57 rows are crosswalked by source row/hash and structural review dependency;
all 59 historical human judgments, 61 nodes, 205 relations and 3 settled parent
edges are unchanged. The entire accepted 50-file R4.3 package is preserved.

Exclusive review-only triage: 14 TRUE_GLOBAL_SEAM participants; 6 same-locus role
rows; 19 known-group/container rows; 10 local-relation-constrained rows; 8 group
parentage rows; 0 technical cases. Same-locus roles at **4:1, 15:1 and 22:1** retain
both human records and exact shared evidence. No reference-only identity inference.
There are 22 textual group members in total; three speech-onset role records are
counted in the role category instead. 3:2 is resolved context, not another unresolved row.

**Seven distinct open-attachment review cases A–G**, plus **H summary**, now organize
the work. This is review-scope compression, not proof that exactly seven atomic
human judgments suffice. Existing local/group constraints are preserved; cases
overlap. Primary case assignments are presentation bookkeeping, never new parents:

| Case | Question | Primary unresolved rows | Participating rows |
| --- | --- | ---: | ---: |
| A | Opening narrative/testing scopes, 2:11 and 3:1 | 13 | 14 |
| B | Independent Job 3:1/3:2 and dialogue-cycle entry | 1 | 25 |
| C | Three cycles and POST_DIALOGUE_JOB | 29 | 29 |
| D | 31:40 / 32:1 / Elihu introduction and sequence | 8 | 13 |
| E | Elihu ending / YHWH onset interface | 0 | 3 |
| F | Higher organization of YHWH–Job response sequences | 4 | 4 |
| G | Final speech-response complex / 42:7 final narrative | 2 | 4 |
| H | Whole-book summary of A–G, not an additional independent case | — | — |

All previously accepted functions remain fixed, including cycles 6/6/4 and no
Zophar III; 27:1/29:1 peers and HSA2-F closure distinctions; Elihu introduction
not being a peer speech; four Elihu peers; YHWH/Job respective peer pairs;
40:1 child of 38:1; 42:7 onset and 42:16 continuation. No 42:10/42:12 promotion,
new MR1 rule, nearest-opening, adjacency/response parentage or candidate ranking.

Final syntax/parser PASS; full regression **679 PASS, zero skips** (625 previous
plus 54 new). Final synthetic and both independent real audits **35/35 gates PASS**,
every gate negatively tested. **82 frozen raw hashes** unchanged; 11 accepted
archives verified. Independent checker verified all **3,992 evidence links**,
typed dependency paths, 57 original rows, baseline Git identities and **5 manifests**.
**62/62 files and complete ZIP byte-identical**. Human packet manually inspected.
No Termux empirical run claimed; exact instructions are provided.

- Final: `results/hsa3_prep_global_seams_final2_20260922_a/`
- Rerun: `results/hsa3_prep_global_seams_final2_20260922_b/`
- Packet: `04_global_seam_review_packet.md` within the final directory.
- ZIP: `results/hsa3_prep_global_seams_final2_20260922_a_results.zip`
- Log: `results/hsa3_prep_global_seams_final2_20260922_a_run.log`
- SHA256: `06e41a935d1ccb18eed1b1773d4ca04a493a097533e36cf2875f741fa116cc77`

**Next: researcher human adjudication of A–G using H as the summary.** Local/group
member decisions are deferred for coordinated review, not silently declared
resolved or permanently unnecessary. UNRESOLVED / INSUFFICIENT_EVIDENCE remain
valid outcomes. **R4.4 hierarchy recompilation must wait until that review is complete.**

## Previous task — R4.3 human-grounded whole-book partial scaffold, 2026-09-22

Active specification: [R4_3_SPEC.md](R4_3_SPEC.md); usage:
[README_MILAL_R4_3.md](README_MILAL_R4_3.md). Starting HEAD:
`f41095917d1deaa718df553f4919e41969601ce7`. The researcher authorized integration
of accepted human decisions into the first partial whole-book scaffold, with
synthetic/accepted-real validation, deterministic rerun and commit/push.

**HSA1, HSA2 and HSA2-F remain frozen. All 59 original human records are represented**
(31 + 25 + 3), including historical UNRESOLVED fields. No new human judgment was
invented. The derived view has **61 nodes** (including one technical JOB_BOOK root),
**205 typed edges**, **8 non-textual groups** (6 human + 2 relation-derived), and
**355 node/edge provenance links**. All accepted historical context remains lossless.

**This is not complete global parentage.** Only **3 explicit hierarchical parent
edges** are resolved: 1:13 CHILD_OF 1:6, 3:1 HIERARCHICALLY_ABOVE 3:2, and 40:1
CHILD_OF 38:1. There are **57 explicit unresolved direct-parent cases**. Known group
membership and continuation remain separate claims, not secretly completed parents.
JOB_BOOK links are TECHNICAL_ROOT_LINK, never human parentage. Group indentation in
the Markdown means membership only; resolved hierarchy is displayed separately.

Preserved: dialogue cycles **6 / 6 / 4**, no Zophar III or placeholder; cycle-onset
peers at 4:1/15:1/22:1; independent initial 3:1; internal 11:4; final cycle-3 onset 26:1.
27:1/29:1 remain same-level, 28:1 remains non-boundary continuation. **31:40 local
closure to 29:1 and higher-order termination of POST_DIALOGUE_JOB remain distinct**;
direct closure to 27:1 is rejected. Its unresolved parent does not reopen its closure target.

Elihu's 32:6/34:1/35:1/36:1 remain same-level group members. 32:2–5 introduces that
sequence descriptively, not as a peer speech or forced parent; 32:1 remains transition.
37:24 remains ending context without a new direct closure target. **38:1/40:6 remain
same-level; 40:1 remains child of 38:1; 40:3/42:1 remain same-level** Job responses.
**42:7 begins the final paragraph/narrative transition; 42:16 continues within it**.
42:10/42:12 were not promoted. 1:22/2:10 remain non-MR1 human parallel endings.
**Response and adjacency were never converted into parentage.** No new marker rule.

Syntax PASS; full regression **625 PASS, zero skips** (566 prior + 59 R4.3).
Windows synthetic and both accepted-real audits **41/41 gates PASS**, each negatively
tested. Independent runs reproduce **50/50 files and the complete ZIP**. All **75
frozen file hashes**, 10 accepted input ZIPs, exact provenance, unresolved completeness,
graph connectivity, outer and nested manifests passed. Markdown manually inspected.
See [R4_3_VALIDATION_REPORT.md](R4_3_VALIDATION_REPORT.md) for counts and every seam.

- Final: `results/r4_3_whole_book_scaffold_20260922_a/`
- Rerun: `results/r4_3_whole_book_scaffold_20260922_b/`
- ZIP: `results/r4_3_whole_book_scaffold_20260922_a_results.zip`
- Log: `results/r4_3_whole_book_scaffold_20260922_a_run.log`
- SHA256: `d8fc0227c6bd35517b0dea1d53b205517ad8a8308b5954486215a00955cba4f7`

**Next task: human review of unresolved global seams**, now exhaustively listed in
03_unresolved_parentage.csv and the report's UNRESOLVED GLOBAL SEAMS section. These
include all eight groups and the 49 remaining textual-locus direct-parent questions.
No automatic completion or next analytical stage is authorized by technical success.

## Previous task — HSA2-F final Job 31:40 closure adjudication, 2026-09-22

Active specification: [HSA2_FINAL_SPEC.md](HSA2_FINAL_SPEC.md); usage:
[README_MILAL_HSA2_FINAL.md](README_MILAL_HSA2_FINAL.md). Starting HEAD:
`21225566974ca4b18d38679c790a2b5c37066cd3`. The researcher supplied final closure
decisions and authorized append-only implementation, validation and commit/push.

**HSA1 and HSA2 are frozen**, including their source/context evidence and original
UNRESOLVED closure fields. The separate [final Markdown](HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.md)
and [CSV](HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.csv) append **three REVIEWED human
decisions**. Original HSA2 was an evidence audit; it did not automatically select 29:1.

**31:40 remains SPEECH_UNIT_END. Its direct/local target is now human-adjudicated
as 29:1 (DIRECT_LOCAL_CLOSURE).** Direct closure to 27:1 is rejected via
NO_DIRECT_RELATION in the DIRECT_CLOSURE_TARGET dimension (= NO_DIRECT_CLOSURE).
Separately, 31:40 has **HIGHER_ORDER_TERMINAL_EFFECT on the 27:1–31:40 post-dialogue
Job speech group**, recorded as TERMINATES_ENCLOSING_GROUP. This rejection does not
deny the independent group relation. **27:1/29:1 remain SAME_LEVEL_SIBLING** speech
onsets, not parent/child; **28:1 remains NO_BOUNDARY / CONTINUES_WITHIN 27:1**.

The researcher used previously adjudicated hierarchy to identify the locally active
29:1 speech. **No nearest-opening heuristic or new automatic closure rule** was
introduced. All 6/6/4 cycle judgments, no Zophar III, 3:1, 4:1/15:1/22:1 cycle
onsets, 26:1 and historical MR1 labels remain unchanged.

HSA1 31 + HSA2 25 + final 3 = **59 human decision records**. HSA2's **83 directed
pairs remain unchanged**, with three final typed assertions added separately (86
across the two tables, including one rejection). **1968 source/context links remain
unchanged**, plus 15 new human-decision provenance links. All **17 original HSA2
members** are preserved byte-for-byte under `hsa2/` inside the new package.

Syntax PASS; full regression **566 PASS, zero skips** (529 prior + 37 HSA2-F).
Synthetic and both accepted-real audits **26/26 gates PASS**, every gate negatively
tested. Independent processes reproduce **25/25 files and the complete ZIP**.
Outer/nested manifests and all **67 pinned frozen repository files** pass; eight
accepted ZIPs verified. Real compact report manually inspected. No frozen analytical
core was modified. See [HSA2_FINAL_VALIDATION_REPORT.md](HSA2_FINAL_VALIDATION_REPORT.md).

- Final: `results/hsa2_f_final2_20260922_a/`
- Rerun: `results/hsa2_f_final2_20260922_b/`
- ZIP: `results/hsa2_f_final2_20260922_a_results.zip`
- Log: `results/hsa2_f_final2_20260922_a_run.log`
- SHA256: `64cf4c0eae884f8c7d407d3880e0d867a70bdd56d79bd2bb557ee2b119103bcc`

**R4.3 is now unblocked following successful HSA2-F validation.** Whole-book
hierarchy/parentage has **not** been generated. R4.3 remains the next separately
scoped methodological stage, not an output or automatic continuation of HSA2-F.
Earlier HANDOFF sections below preserve the historical unresolved state and blockers.

## Previous task — HSA2 dialogue-cycle adjudication and closure-target audit, 2026-09-22

Active specification: [HSA2_SPEC.md](HSA2_SPEC.md); usage:
[README_MILAL_HSA2.md](README_MILAL_HSA2.md). Starting HEAD:
`28892b3f0ecab3d42749ab50d8a65bc4aa9e09c5`. The researcher authorized appending
new human judgments, a focused accepted-source audit, validation and commit/push.

**HSA1 is frozen.** The separate HSA2
[Markdown](HUMAN_STRUCTURAL_ADJUDICATION_HSA2.md) and
[CSV](HUMAN_STRUCTURAL_ADJUDICATION_HSA2.csv) append **25 human records through
Job 31**; they do not replace HSA1. **Job 3–26 dialogue cycles are human-reviewed**:
6 / 6 / 4 speeches, with an incomplete third cycle and no generated Zophar III.
Speech and cycle-onset judgments at 4:1/15:1/22:1 have separate IDs; MR1 remains
ANSWER+AMR. There are **83 directed, directly supplied human relation pairs**.

**27:1 / 29:1 are same-level peers; 28:1 is no boundary; 31:40 is an accepted
speech ending. Its direct closure target remains UNRESOLVED.** The separate
higher-order terminal effect also remains UNRESOLVED. Three candidate review rows
allow a local closure and enclosing termination to coexist, without selecting
either or adding a settled closure edge. No nearest-opening or span-length rule.

The audit preserves **1968 source/context links** (1030 judgment links and 938
audit-context links), **700 signatures for 100 atoms**, **377 formal edge rows**,
23 marker/control scopes and 10 negative controls. The two three-atom opening
formulas match in all 21 corresponding G0–G6 hashes. The 31:40 marker has
תמם / דבר / איוב and no משל; this does not decide a direct target. Source identity
and recurrence alone do not establish a preference between 27:1 and 29:1.

Syntax and full regression **529 PASS, zero skips** (482 prior + 47 HSA2).
Final synthetic and both accepted-real audits **31/31 gates PASS**, each gate
with a negative test. Independent processes reproduce **17/17 files and the
complete ZIP byte-for-byte**. Native order is verified from PROV1 atom indexes,
including discontinuous clause membership; no frozen analytical core was changed.
Focused report manually inspected. See [HSA2_VALIDATION_REPORT.md](HSA2_VALIDATION_REPORT.md).

- Final: `results/hsa2_dialogue_structure_final_20260922_a/`
- Rerun: `results/hsa2_dialogue_structure_final_20260922_b/`
- ZIP: `results/hsa2_dialogue_structure_final_20260922_a_results.zip`
- Log: `results/hsa2_dialogue_structure_final_20260922_a_run.log`
- SHA256: `669018ceacacef21db426028854ea1f88879a446d4d4ca113d24bec6ef8f2994`

Next task: researcher review of **31:40 direct closure target and the independent
enclosing terminal effect**. Whole-book **R4.3 parentage remains blocked on this
closure-target review**. No whole-book hierarchy was generated.

## Previous task — HSA1 human structural adjudication registry, 2026-09-22

Active specification: [HSA1_SPEC.md](HSA1_SPEC.md); usage:
[README_MILAL_HSA1.md](README_MILAL_HSA1.md). Starting HEAD:
`77ca713b9520ce085135dc845f60d920095756cb`. The researcher authorized recording
the supplied judgments, linkage validation, deterministic audit and commit/push.

**HSA1 is the human-authored structural source of truth**, not a new analytical
stage or an automatic hierarchy generator. The equivalent
[Markdown](HUMAN_STRUCTURAL_ADJUDICATION.md) and
[CSV](HUMAN_STRUCTURAL_ADJUDICATION.csv) contain **31 REVIEWED judgments** and
**33 direct, directed relation pairs**. Reciprocal pairs count twice; no transitive
or inverse completion is inferred. **2:11 is accepted as a new paragraph onset**;
2:9 remains internal to 2:1–10. 27:1/29:1 and all four Elihu speech onsets remain
same-level siblings. Not macro-level does not mean subordinate.

All 31 judgments have exact native/context source links; zero lack machine links.
The audit expands **1122 source links** without reducing formal or case context,
and retains **19 negative controls**. Human judgment is not a computational result.
3:1 remains outside MR1; 1:22/2:10 remain non-MR1 human parallel endings. Anonymous
entry identities/first appearance remain UNRESOLVED. 42:7 keeps Wayhi, SIMPLE_AMR
and CASE030 distinct; 42:16 remains human NO_BOUNDARY. No new primary atom is guessed.

Syntax passed. Full regression **482 PASS, zero skips** (436 prior + 46 HSA1).
Final synthetic self-test and both accepted-artifact audits **30/30 gates PASS**;
each gate has a negative test. Independent processes reproduce **10/10 files and
the complete ZIP byte-for-byte**. This reads hash-pinned accepted BHSA 2021 evidence
snapshots; it is not a new BHSA extraction or cross-platform validation.
See [HSA1_VALIDATION_REPORT.md](HSA1_VALIDATION_REPORT.md).

- Final results: `results/hsa1_structural_adjudication_lf_final_20260922_a/`
- ZIP: `results/hsa1_structural_adjudication_lf_final_20260922_a_results.zip`
- Log: `results/hsa1_structural_adjudication_lf_final_20260922_a_run.log`
- Rerun: `results/hsa1_structural_adjudication_lf_final_20260922_b/`
- ZIP SHA256: `9ed87863ccc4388cf608d72675ba69354846c2376e3d764c96f5a79c2599a885`

All frozen analytical cores and accepted artifacts remain unchanged. **Hierarchy
remains incomplete for Job 3–26.** The next task is human review of the Job 3–26
speech-unit structure using the same linguistic-marker criteria. The supplied
3:1/3:2 judgment does not complete that review. **R4.3 whole-book parentage remains
blocked pending dialogue-unit review.** No unreviewed hierarchy was inferred.

## Previous task — R4.2 participant transition/enclosure audit, 2026-09-21

Active specification: [R4_2_SPEC.md](R4_2_SPEC.md); usage:
[README_MILAL_R4_2.md](README_MILAL_R4_2.md). Starting HEAD:
`16e13b525a467e63181eb1a434e0c152d96d309a`. The researcher supplied R4.1 human
judgments, authorized R4.2 through commit/push after validation, and explicitly
resolved the initial messenger identity stop: preserve **one overt מלאך event
and three anonymous זה + בא entries**; do not promote historical inferred speaker
IDs into referential identities. Event existence and participant identity are
separate claims. New human judgments are versioned in
[R4_2_HUMAN_JUDGMENTS.json](R4_2_HUMAN_JUDGMENTS.json), not extraction rules.

**Participant change is scene evidence, not automatic hierarchy.** Wife, friends,
Elihu and messenger controls use the same whole-book surface rules. Audit scope:
2938 clauses / 2977 atoms / 8286 phrase inclusion-or-exclusion rows. There are
**452 source-phrase event candidates**, not 452 confirmed scene transitions or
distinct entities: 449 overt source mentions and three anonymous entries.
Referential first appearance remains UNRESOLVED; exact name-form word facts are
separate. Proper-name/grammatical-group/speech-argument candidates can include
reported content or inanimate expressions; their scene status is human-reviewed.

Primary type counts: new-participant candidate 39; group candidate 232;
speaker-expression change 49; addressee-expression change 34; other explicit
set-change candidate 98. Complete matching tags remain. Enclosure rows **469**:
inside supplied frame 70, between closure/opening 362, after closure 28, before
opening 9. Formal event/clause-span links **3362**; full formal inventory 12722.
Three human-supplied candidate frames are overlays, not macro units or parents.

Controls: all four entries lie inside supplied 1:6–1:22 and 1:13–1:22 frames.
Wife 2:9 lies inside supplied 2:1–2:10. Friends 2:11 lie after human ending 2:10
and before human 3:1 transition / MR1 3:2 CSF. Elihu 32:2 is after MR1 32:1
closure and before MR1 32:6 CSF; 31:40 and 32:2–5 source context remain separate.
**1:22/2:10 parallel-ending control**: corresponding evaluation clauses are xQtX
with חטא qal/perfect/3ms; 2:10 adds בשפתיו. Shared formal families F000020/G0
and F001232/G1. Both remain **MR1_EXPLICIT_CLOSURE=false**. Human ending status
is separate, and all 69 formal recurrences of the shared families are retained.
**3:1 marker-layer gap** is explicit: אחרי כן / פתח איוב את פיהו surface evidence,
no MR1 marker; 3:2 CSF remains separate. MR1 rules are unchanged.

Final syntax PASS; full regression **436 PASS, zero skips** (383 prior + 53 R4.2).
Every gate has a negative test. Final synthetic and both real runs **31/31 PASS**.
Independent rerun reproduces **27/27 files and the complete ZIP byte-for-byte**.
Every event has expanded source context in the review packet. Source, manifest,
eligibility, identity and enclosure audits passed. See
[R4_2_VALIDATION_REPORT.md](R4_2_VALIDATION_REPORT.md) for details and limitations.

- Results: `results/r4_2_real_final_20260921_a/`
- ZIP: `results/r4_2_real_final_20260921_a_results.zip`
- Log: `results/r4_2_real_final_20260921_a_run.log`
- Rerun: `results/r4_2_real_final_20260921_b/`
- ZIP SHA256: `7b6c91fb862bf1755c097a9edc31783933388279b54f88796531b0a2419be8d3`

All previous analytical cores and accepted artifacts remain unchanged. No legacy
hierarchy, automated parentage, scores/ranks or new interpretive labels. Existing
human hierarchy judgments remain attributed; new conclusion/hierarchy fields are
blank. **Hierarchy is still human-adjudicated.** Next task: researcher review of
surface participant candidates and surrounding evidence; no automatic next stage.

## Previous task — R4.1 boundary-oriented evidence profiles, 2026-09-21

Active specification: [R4_1_SPEC.md](R4_1_SPEC.md); runner instructions:
[README_MILAL_R4_1.md](README_MILAL_R4_1.md). Starting HEAD:
`fc81663ccddf1fdc343e60d5ee70152850d02103`.

The researcher technically **accepted R4.0 as an exhaustive scaffold**, then
authorized R4.1 implementation, tests, synthetic/real execution, independent
deterministic rerun, inspection and commit/push after validation. R4.0 saturation
is preserved as a finding: 2977 atoms, 2976 candidates, **2900 formal-only**,
2975 transition-zone overlays. It is not retroactively considered an R4.0 failure.

R4.1 separates **boundary-oriented source anchors** from **formal contextual
evidence**. Formal occurrence no longer creates an anchor. There are **69**
separate anchors: CSF 56, explicit closures 2, positive Wayhi 5, exact HR1 verse
scopes 6. Co-located identities remain separate, with 5 exact overlap links.
Formal inventory retains all 12722 occurrences; 1140 anchor/occurrence span rows
carry 3002 overlapping positional labels. Two edges per anchor give 138 edges,
represented by 414 exhaustive classification rows (1755636 occurrence assignments,
including remote before/after context). **2400 incident edge assignments** isolate
immediate endings/beginnings and crossings. All **693** exact same-family pairs
are preserved without similarity scores or hierarchy implications.

Validation: syntax PASS; full regression **383 PASS, zero skips** (336 previous
and 47 R4.1); all stage tests rerun after final report formatting. Synthetic and
both real runs **32/32 gates PASS**, with a negative test for every gate.
All **22 member files and complete ZIP bytes are identical** between fresh runs.
Independent serialized-output audit verified every edge assignment and complete
69-anchor / 693-comparison packet coverage, CRC, disk bytes and manifest.

Critical profiles preserve 31:40 closure, 32:1 closure, 32:2 HR1 scope and 32:6
Elihu CSF separately. CASE028 does not infer direct Elihu→YHWH continuity;
38:1 retains Job as explicit addressee. Ordered CSF inventory 38:1–42:1 includes
**38:11 SIMPLE_AMR** as well as requested 38:1/40:1/40:3/40:6/42:1 frames.
42:7 has distinct Wayhi, SIMPLE_AMR and CASE030 scope. **42:16 has zero anchors**
despite 21 formal occurrences. All 30 human records, 3540 extension rows,
1018 human locators and 170 Way0 audit records remain unchanged.

- Results: `results/r4_1_real_20260921_a/`
- ZIP: `results/r4_1_real_20260921_a_results.zip`
- Log: `results/r4_1_real_20260921_a_run.log`
- Independent rerun: `results/r4_1_real_20260921_b/`
- ZIP SHA256: `92d01bd0deccd6c77c288cd69e7d1eaebeea289f64378f59b667e4aaa91af966`

See [R4_1_VALIDATION_REPORT.md](R4_1_VALIDATION_REPORT.md) for counts, sources,
comparison findings and limitations. **Hierarchy remains unassigned.** No score,
ranking, convenience pruning, new discourse/theological label or legacy hierarchy
reuse. Frozen layers including R4.0 are unchanged. Next task: researcher review
of source-event profiles and positional evidence; no hierarchy stage is authorized.

## Previous task — R4.0 whole-book candidate inventory, 2026-09-21

Active specification: [R4_0_SPEC.md](R4_0_SPEC.md); usage:
[README_MILAL_R4_0.md](README_MILAL_R4_0.md). The researcher accepted MR1 as R4
marker provenance and explicitly authorized R4.0 implementation, tests, synthetic
validation, real execution, deterministic rerun, focus inspection and commit/push
after validation. Starting HEAD: `5cfb91847bc967858c75cf850050036b4e4c5bc6`.

R4.0 is inventory/scaffold only; there is no final hierarchy or parentage yet.
Frozen R1.1/v6.42.12 remain historically unavailable; legacy hierarchy is not
reused. The initial source preflight stopped before implementation because the
accepted R3c.3/PROV1/HR1 ZIPs were absent on A. The researcher restored all three;
exact supplied SHA256, CRC and manifests now pass. Actual PROV1/HR1 local names
have download suffixes (1)/(2), recorded in the R4 config, with identical accepted
bytes. No substitute source was used.

Validation completed: syntax PASS; full regression **336 PASS, zero skips**
(273 previous + 63 R4 tests), with final R4 tests rerun after focus-field
presentation changes. Synthetic and both real runs passed **34/34 gates**;
every gate has a negative mutation, including manifest corruption. PowerShell
5.1 synthetic and PowerShell 7 real runners exited 0.

Whole-book native scope: 2938 clauses / 2977 atoms / 39 multi-atom clauses,
through Job 42:17. Marker inventory: **63** = CSF 56 + closures 2 + positive
Wayhi 5. All 170 Way0 records retained; 165 negatives did not trigger candidates.
All 12,722 formal bundle occurrences and 15,292 explicit family-occurrence links
remain. Candidate anchors **2976**, candidate/source-locator links **39414**,
adjacent-anchor relations **2975**, overlapping transition-zone overlays **2975**.
These dense counts arise from preserving every formal repeated-window endpoint;
they do **not** mean 2976 macro boundaries. The only native atom with no trigger
is 587997 (Job 5:27), retained without a candidate in the full coverage inventory.

All 30 human records remain verbatim (CLEAR 21 / PARTIAL 5 / INSUFFICIENT 4),
including all 3540 extension overlay rows and 1018 HR1 source locators. Six
boundary cases retain all 117 panel participants and their full verse atom scopes;
no invented atom-level human judgment. CASE007–012 dependency and CASE028/029
continuity/addressee cautions remain. All 16 controls and the full 27–42 focus
report were inspected. At 42:16 there is no MR1 marker but 21 formal occurrences;
control status does not fabricate a marker. No final hierarchy/parentage,
scores/rankings or new rhetorical/theological labels were produced. Frozen
R1–R3/PROV1/HR1/MR1 analytical cores and inputs remain unchanged.

Two fresh real processes produced **21/21 identical members and identical ZIPs**:

- Results: `results/r4_0_real_20260921_a/`
- ZIP: `results/r4_0_real_20260921_a_results.zip`
- Log: `results/r4_0_real_20260921_a_run.log`
- Rerun: `results/r4_0_real_20260921_b/`
- ZIP SHA256: `c313d102e65854c4d40ff9efac716f78a2388750e1c983b200655984ad7ded47`

See [R4_0_VALIDATION_REPORT.md](R4_0_VALIDATION_REPORT.md) for source hashes,
complete control audit and focus findings. Next task: researcher review of this
unpruned candidate inventory and positional zone convention. Hierarchy questions
remain unresolved; no later hierarchy-building stage is authorized automatically.

## Previous task — MR1 provenance/reproduction, 2026-09-21

Active specification: [MR1_SPEC.md](MR1_SPEC.md); execution instructions:
[README_MILAL_MR1.md](README_MILAL_MR1.md). The researcher explicitly authorized
implementation, synthetic tests, real BHSA 2021 reproduction, deterministic rerun,
historical four-CSV comparison, field/control audit and commit/push after success.
Starting commit: `fa7d4477470306513a2002c26982368e6954de2d` on main/origin/main.

MR1 is provenance/reproduction only. R4.0 remains blocked pending MR1 review.
Frozen R1.1/v6.42.12 packages remain unavailable; v5.2.5 is a historical
comparison source, not an authoritative replacement registry/hierarchy.
The corrected expected populations are Way0 audit 170, Wayhi-positive 5 and
negative 165. Temporal auxiliary evidence uses nonempty/non-NA vt, not an added
finite-only restriction.

Validation complete: syntax PASS; full regression **273/273 PASS**, zero skips
(202 previous + 71 MR1 tests); synthetic self-test **33/33 gates PASS**, with a
negative test/mutation for every gate. PowerShell 5.1 synthetic runner and
PowerShell 7 real runner completed successfully. Frozen analytical cores were
not modified.

Real BHSA 2021 / TF 13.1.0 execution: **33/33 gates PASS**, exit 0. All **3166**
historical rows have exact explicit-key/coordinate and all-field equality:
surface 2938, CSF 56, closure 2, Way0 audit 170. Historical-only/current-only/
field-different rows: **0/0/0**. All four historical-schema exports are
byte-identical to their local comparison CSVs. Wayhi-positive 5 at 1:5, 1:6,
1:13, 2:1, 42:7; negative 165. CSF has historical ordinal IDs/coordinates, not
historical clause IDs; MR1 does not guess them.

Native membership: 2938 clauses, 2977 atoms, 39 multi-atom clauses. Complete
event/clause links: 3201 rows (3240 event/clause/atom memberships). All control
locations inspected, including 175 clauses in 1:1–3:1. Job 31:40 clause 499623
still maps independently to atom 589751 (frozen S02135 control).

Two fresh processes produced **17/17 byte-identical members and identical ZIPs**:

- Results: `results/mr1_real_final_20260921_a/`
- ZIP: `results/mr1_real_final_20260921_a_results.zip`
- Log: `results/mr1_real_final_20260921_a_run.log`
- Rerun: `results/mr1_real_final_20260921_b/`
- ZIP SHA256: `9f287dca2a7689e04f37b4a9dbcfe53dd714dcc8dc9d1a702f46f476f6537ec0`

See [MR1_VALIDATION_REPORT.md](MR1_VALIDATION_REPORT.md) for exact source paths,
hashes, field comparison and control findings. Current source dataset bytes are
fingerprinted; historical raw BHSA byte identity remains UNKNOWN_NOT_VERIFIED.
Next pending task: researcher review of MR1 provenance/reproduction and CSF use.
Technical success is not methodological acceptance; **R4.0 is still on hold**.

## Previous task — HR1 linkage validated, technical pilot closure ready, 2026-09-21

Active specification: [HR1_SPEC.md](HR1_SPEC.md); usage:
[README_MILAL_HR1.md](README_MILAL_HR1.md). HR1 is a non-analytical linkage
sidecar joining the committed human adjudications to frozen R3c.3 and PROV1.
The researcher authorized implementation, complete validation, real execution,
and commit/push after success. Starting/source adjudication commit:
`a1e2b99b6fb70a56ccd4ba7230998bae69031dc0` (main tracking origin/main).

Final validation: Python syntax PASS; complete regression 202 PASS, zero
failures/skips (31 HR1 tests plus 171 prior tests); synthetic self-test 22/22
gates PASS, each with a negative test. The synthetic packet was inspected.
An initial real attempt was intentionally interrupted before output publication
to cache immutable member SHA256 values once per derivation. There was no
reported source/gate failure. All 11 synthetic output files remained byte-identical
after this performance change; full regression and self-test were rerun before
the final real execution.

Accepted real execution completed with exit code 0 and 22/22 gates PASS:

- Directory: `results/hr1_human_review_linkage_20260921_114012/`
- ZIP: `results/hr1_human_review_linkage_20260921_114012_results.zip`
- Run log: `results/hr1_human_review_linkage_20260921_114012_run.log`
- ZIP SHA256: `7566dcd6191da1b7e4d29b11af4a44c37511dcf0fefa24449a0489ee97c64191`

There are 30 adjudication links, 141 case-target links, 288 R3c.3 evidence
locators, 730 PROV1 provenance locators, 3,540 preserved extension overlay rows,
six boundary panels (117 participant links) and six categorical summary rows.
Unresolved links: 0; ambiguous links: 0. Boundary participant counts for CASE025–030
are respectively 23, 16, 13, 17, 21, 27. CASE019 retains G6:S02135, atom 589751,
lineage RL00218 and explicit parent-family provenance F001969. Missing identity
domains are marked NOT_AVAILABLE_FROM_SOURCE, not guessed.

The result ZIP CRC, manifest, written file bytes and original source hashes were
rechecked after execution. Sources (repository-local paths on B computer):

| Source | SHA256 |
| --- | --- |
| `results/r3c_3_windows_20260919_091111_results.zip` | `5f8239a692a516fd9722d94fb919321d399fad93c3583dd828ac1c1883576981` |
| `results/prov1_windows_20260920_081304_results.zip` | `38c6703721e2f9cca590ab96d64d7a2860a3d075e059cabeb2abe9eb6708c482` |
| `docs/HUMAN_REVIEW_PILOT_ADJUDICATION.csv` | `4fb8c15a9ae530e778122f97c3ffcdcc78ded89f534535e4c7afe5cb2272abe3` |

Human fields remain verbatim: CLEAR 21 / PARTIAL 5 / INSUFFICIENT 4; context
YES 26 / PARTIAL 4 / NO 0; all 30 REVIEWED and all review times blank. CASE007–012
remain one human-recognized extended sequence with explicit overlay dependency,
not six independent evidences. CASE028/029 retain Elihu's ending, YHWH's beginning,
no automatic direct Elihu→YHWH continuity, and Job as explicit addressee.

The inspected acceptance report supports technical readiness to close this
30-case human-review pilot, qualitatively from the recorded distinctions and
limitations, without a score or population-wide claim. All frozen analytical
cores/outputs and human source records remain unchanged. No R2.2 rerun is needed.
Next pending task: researcher decision on formal methodological closure using
the HR1 report and source-linked human record. No R3c.4, R4, corrective pipeline,
new automatic judgments or further methodological stage is authorized.

## Previous task — Human-authored pilot adjudication record, 2026-09-21

The researcher supplied completed CASE001–CASE030 human adjudications. Their
source-of-truth record is [HUMAN_REVIEW_PILOT_ADJUDICATION.md](HUMAN_REVIEW_PILOT_ADJUDICATION.md)
with an equivalent [CSV](HUMAN_REVIEW_PILOT_ADJUDICATION.csv). These are human
researcher statements, not R3c/PROV1 outputs or automatically assigned labels.
The supplied form assessments total CLEAR 21 / PARTIAL 5 / INSUFFICIENT 4;
sufficient_context YES 26 / PARTIAL 4 / NO 0. All 30 cases are REVIEWED; review
time was not measured and remains blank. Original case statements are retained
in reviewer_notes without automatically assigning them to other judgment fields.

The CASE007–012 sequence-extension caution and CASE028/029 discourse-continuity
cautions remain part of the human record. No writeback to R3c/PROV1 results,
input/result modification, pipeline execution, new automatic scoring, R3c.4 or
R4 is authorized by this recording task. Any later integration with local result
artifacts requires a separate instruction; these Git-tracked human records can
be shared without synchronizing inputs/results. Starting PROV1 commit:
`8c87fc33f612326eca0ee2ed0b8781451297c85b`.

## Previous task — PROV1 provenance sidecar, 2026-09-20

Active specification: [PROV1_SPEC.md](PROV1_SPEC.md); usage:
[README_MILAL_PROV1.md](README_MILAL_PROV1.md).
This non-analytical sidecar is neither R3c.4 nor R4. The Signature Feature
Provenance Audit closed as B — EXACTLY_RECONSTRUCTABLE: all 14 historical controls
and all 20,839 atom hashes exactly matched. No R2.2 rerun is required.

The verified generator establishes cumulative named atom components, canonical
UTF-8 JSON/SHA256, and the distinct level/length/ordered-atom-hash window preimage.
R2.2 persists reconstructable components; complete component propagation stops
at R3.1 and is absent from later signature-only sources. Frozen source outputs
and R3c analytical cores must not change.

The researcher authorized PROV1 implementation and synthetic validation only.
Real PROV1 execution, commit/push, corrective analytical stages, R3c.4 and R4
remain unauthorized. Next pending task: review the implementation/synthetic
validation, then separately authorize a real sidecar run and human inspection.

Implementation validation passed on 2026-09-20: 171 complete regression tests,
zero failures/skips, including both installed PowerShell versions. After final
Markdown mode/identity presentation refinements, all 43 PROV1 tests were rerun
and passed. Python/PowerShell syntax checks passed. Synthetic self-test passed
all 22 gates, each with a negative test; manifest verified after writing.
Synthetic counts: 112 atom-level records, 57 families, 51 refinement rows,
2 G6 singletons, 233 identity-link rows, 234 exact hash comparisons. The inspected
catalog has 402 lines / 27,772 UTF-8 bytes; five-case packet 207 lines / 18,339 bytes.
CASE001/007/013/019/025 and S02135 are rendered with explicit synthetic labeling.
Final local output: `results/prov1_synthetic_20260920_final/`. No full real PROV1
dataset has been run; no analytical identity/hash or frozen core was modified.

2026-09-20: the researcher accepted synthetic validation and authorized freezing
and pushing PROV1, then running the accepted real historical inputs. Record the
execution result in the timestamped local outputs/log; do not assume success
from this authorization. The next task is separate human inspection of the real
five-case packet. No further PROV version, R3c.4, R4 or automatic review is authorized.

## Previous stage — R3c.3 development, 2026-09-18

Active specification: [R3C_3_SPEC.md](R3C_3_SPEC.md). Usage:
[README_MILAL_R3c_3.md](README_MILAL_R3c_3.md).

The researcher reports an assisted real R3c.2 review: CASE007 reviewable, CASE019
locally reviewable, CASE013 partly reviewable, CASE025 sufficient for boundary
multiplicity but not macro attachment, CASE001 insufficient. The next problem
is structural definition/refinement context, not batching or object identity.

Transferred R3b.2/3 ZIPs passed historical SHA256 and CRC checks. Inspected schemas
provide family/level/genealogy records, context profile JSON and opaque signature
hashes. They do not expose family signature preimages or exact feature changes
causing uniqueness; these remain NOT_AVAILABLE_FROM_SOURCE.

R3c.3 enriches frozen R3c.2 cases and requires its hash-matched R3c.1 ZIP for source
inventory/singleton provenance plus the two exact R3b ZIPs. All previous analytical
cores stay unchanged. This task authorizes synthetic execution only. Next pending
empirical work is a separately authorized real R3c.3 run and renewed five-case human
review, with missing signature payloads explicit.

2026-09-19: the researcher authorized committing/pushing this implementation and
running the real R3c.3 Windows dataset after verifying the exact input chain.
Human review remains separate; no R3c.4 or R4 is authorized. The execution result
must be checked in the local timestamped output and run log, not assumed here.

Development validation passed: syntax, all 126 regression tests (no skips;
PowerShell 5.1 and 7), all 26 computed gates with negative tests, and synthetic
self-test. The inspected synthetic packet has 30 cases, 4,248 lines and 256,623
UTF-8 bytes. All five acceptance case IDs have enriched sections; unavailable
membership preimages/feature deltas remain explicit. This is not empirical
acceptance of the real five targets.

## Historical R3c.2 stage, 2026-09-18

The researcher reports the real Windows/BHSA 2021 R3c.1 result passed all 24
gates: 8,908 units (2,219 repeated bundles, 6,689 singleton outcomes), 30 pilot
cases, 1,657 selected evidence rows and 798/798 resolved contexts. S02135 and all
six boundary panels survived; extension stayed overlay-only / EXEMPLAR_ONLY.
The whole packet had 32,038 lines. HIGH cases 001–006 had respectively
366/327/307/181/180/174 occurrences and 5,784/4,978/4,989/3,033/3,027/3,090 lines.
These observations establish a presentation problem, not a reason to split units.

R3c.2 is implemented in `src/milal_r3c_2_compact_review.py` as a presentation layer
over the frozen R3c.1 result ZIP. It verifies source hashes/version/gates/cases,
reuses the exact 30 cases, groups display by context and structural relation keys,
and retains every target/boundary/relation/overlay record. Context detail JSON is
unchanged. No BHSA reload, resampling or new analytical identity is introduced.
See [R3c.2 specification](R3C_2_SPEC.md) and [instructions](README_MILAL_R3c_2.md).

The real R3c.1 result ZIP is not bundled in this B-computer clone; its structure
was inspected through the frozen writer/specification. The empirical observations
above are researcher-supplied. This task validates only synthetic derived output;
it does not process the real R3c.1 ZIP. The next pending step is a separately
authorized R3c.2 run over that frozen ZIP and human inspection of the compact
packet. R3b.3, R3c.0.2, R3c.1 analytical cores and historical outputs stay frozen.
R4 remains out of scope.

Development validation: syntax and synthetic self-test passed; all 101 regression
tests passed with no skips (PowerShell 5.1 and 7), after canonicalizing the test
temporary path to avoid existing short-path spelling comparisons. All 23 R3c.2
gates passed and have negative tests. The inspected synthetic compact packet
contains 30 cases, 2,466 lines and 276,551 UTF-8 bytes. See tests/README.md for
the reproducible command and synthetic record counts.

## Historical R3c.1 stage, 2026-09-18

The researcher reports completed, inspected Termux and Windows R3c.0.2 runs on
the same real Job/BHSA 2021 data. Cross-platform analytical invariants matched:

- 30 review cases; 17/17 gates PASS.
- 1,066 unique navigation containers.
- 6,689 singleton outcomes: 2,672 MAPPED, 4,016 EVENT_ONLY, 1 G6_ONLY.
- S02135 retained as an independent singleton outcome.
- All six boundary controls resolved; span-aware BHSA context functioning.
- Sequence extension remained overlay-only and EXEMPLAR_ONLY.

These are empirical Job observations, not hard-coded corpus requirements.
The finding is that R3b.3 containers remain valid navigation objects, but
high-complexity containers are too large for human review units: CASE001 had
17,612 lines and CASE002 had 18,222 lines in the real packet.

R3c.1 therefore targets individual existing repeated bundles and canonical
singleton outcomes. Containers/lineages stay navigation metadata; boundary
panels stay controls. No new rhetorical, discourse, semantic or fork object
is introduced. All selected bundle occurrences remain available, with parent,
ancestor and direct child relations separated from target evidence. No recursive
descendant-target expansion or evidence truncation is permitted.

Implementation: `src/milal_r3c_1_review_units.py`; configuration:
`config/r3c_1_job_pilot.json`; primary runner:
`scripts/run_milal_r3c_1_windows.ps1`. See [the active specification](R3C_1_SPEC.md)
and [R3c.1 instructions](README_MILAL_R3c_1.md). The frozen R3c.0.2 core is imported
for validated pure helpers and span-aware context, not rewritten.

Development acceptance was synthetic: syntax, full regression suite, all computed
gates and packet inspection. The researcher subsequently reported the real R3c.1
Windows run summarized above. No R4 work has been done.
Historical R3c.0.2 outputs must not be retroactively changed.

The sections below preserve the R3c.0.2 development rationale and earlier
R3c.0.1 observations; their pilot design describes the prior stage.

## Historical R3c.0.2 implementation update — 2026-09-17

The new implementation is in `src/milal_r3c_0_2_reviewability.py`; R3c.0.1 is
preserved. Job controls are in `config/r3c_0_2_job_pilot.json`. The new Termux
runner resolves `../src/` and creates fresh result paths without deleting runs.
See `docs/README_MILAL_R3c_0_2.md` for outputs and validation commands.

Real R3b.2/R3b.3 input ZIPs and BHSA are not bundled in this development workspace.
Synthetic validation and the checked-in R3c.0.1 control regression are development
checks only. The real Termux/Windows validation was subsequently completed as
recorded above. Do not advance to R4 on synthetic results.

## 1. Program

**MILAL = Marker-Informed Linguistic Analysis of Layers**

MILAL is being developed as a generalizable Hebrew Bible surface-text analysis pipeline. Job is the present primary research corpus, but code semantics must not assume Job-only row counts or fixed structural conclusions.

The present dissertation use case concerns the role of the Elihu speeches (Job 32:6–37:24) within the literary/rhetorical structure of Job. The computational method must remain bottom-up: surface form and distribution first, observable contextual behavior next, rhetorical/function interpretation later.

## 2. Core methodological rule

R3 does not automatically decide rhetorical function.

The pipeline may identify:
- repeated surface patterns,
- refinement genealogies,
- singleton outcomes,
- occurrence distributions,
- local BHSA context,
- sequence-extension relations,
- navigation/review structures.

It must not automatically assign labels such as "transition function", "closure function", "rhetorical bridge", etc. Those belong to later human analysis.

## 3. Current pipeline state

The relevant recent stages are:

- R3b.2: review bundles and full occurrence data.
- R3b.3: refinement lineages and navigation containers.
- R3c.0: first reviewability pilot; found that sampling internal bundles was the wrong unit.
- R3c.0.1: corrected the population to R3b.3 review containers, separated singleton object types, restored BHSA context, and built all-match boundary panels.

R3b.3 is now treated as a **frozen navigation layer**. Do not alter it merely to make human review easier. Human-review views belong in R3c.

## 4. Current real-data facts from Job

These are descriptive regression facts, not universal MILAL constants:

- R3b.3 navigation containers: 1,066.
- R3b.3 internal bundles: 2,219.
- R3c.0.1 pilot containers: 24.
- R3c.0.1 actual pilot output included:
  - 532 repeated-bundle rows,
  - 1,873 singleton refinement-event rows,
  - 1,841 G6 singleton-item rows,
  - 1,170 sequence-extension overlay rows.
- `results/r3c_0_1/07_pilot_review_container_packet.md` is about 724 KB / 6,734 lines.
- A single high-complexity case can approach ~1,000 displayed rows/objects.

Therefore: **navigation container ≠ human review unit**.

## 5. Empirical findings that must drive R3c.0.2

### 5.1 Singleton visibility

Job 31:40 `תמו דברי איוב` is a key regression/control example.

The data show a genealogy in which broader repeated forms narrow through refinement and the final form becomes a G6 singleton (e.g. S02135 in the current output). The singleton must be independently reviewable while retaining its lineage ancestry/provenance.

General rule:

> A singleton may belong to a genealogy, but must not lose its singleton review identity.

### 5.2 Duplicate human-facing singleton display

In large pilot containers, singleton refinement events and G6 singleton items are frequently 1:1 representations of the same human-review outcome. They are distinct provenance layers but should not be shown twice to the reviewer.

R3c.0.2 should create one human-facing `SINGLETON_OUTCOME` object with both provenance records attached.

Do not delete either provenance source.

### 5.3 Boundary verses are multi-pattern panels

Current controls:

- Job 31:40
- Job 32:1
- Job 32:2
- Job 37:24
- Job 38:1
- Job 42:7

A boundary verse may match multiple repeated patterns, singleton outcomes, and sequence-extension relations simultaneously. Never choose one representative bundle as "the" pattern for a verse.

R3c.0.1 successfully restored all-match panels, but these controls were not themselves measurable human-review cases. R3c.0.2 must fix this.

### 5.4 Span-aware context

R3c.0.1 attached BHSA context using `ref_start`. This is insufficient when a pattern spans multiple verses.

R3c.0.2 context should expose:

- previous verse before the full span,
- full pattern span text,
- next verse after the full span,
- clauses overlapping/covering the full span,
- sentences overlapping/covering the full span.

Do not fabricate speaker or macro labels if the source does not establish them.

### 5.5 Genealogy must be visible as genealogy

R3c.0.1 Markdown flattened lineage members into a list even though parent IDs existed. R3c.0.2 should expose tree/branch structure in the human-facing review packet.

This is a presentation/reviewability change, not a redefinition of lineage identity.

## 6. Primary purpose of the next pilot

The primary question is **reviewability / context sufficiency**, not total labor-hour estimation.

The primary fields are:

- `review_status`
- `observable_behavior`
- `recurring_context`
- `exceptions`
- `sufficient_context`
- `additional_information_needed`
- `review_time_seconds`
- `reviewer_notes`

`review_time_seconds` should remain as a diagnostic observation, but R3c.0.2 must not extrapolate six random cases into an estimated total time for all navigation containers.

## 7. R3c.0.2 review-case design

Use five strata / case types, six each (30 total):

1. `HIGH_COMPLEXITY_CONTAINER` × 6
2. `LOW_COMPLEXITY_CONTAINER` × 6
3. `RANDOM_CONTAINER` × 6
4. `SINGLETON_ITEM` × 6
5. `BOUNDARY_CONTROL` × 6

Roles:

- HIGH: stress-test the hardest navigation containers.
- LOW: test minimal/simple review contexts.
- RANDOM: unbiased comparison/control only; not enough for population time inference.
- SINGLETON_ITEM: test whether a singleton outcome itself is independently reviewable.
- BOUNDARY_CONTROL: test whether the current MILAL evidence is sufficient to analyze a known structural transition point. The review unit is the entire boundary panel, not one pattern.

Random sampling must use a fixed, recorded seed.

## 8. Sequence-extension invariant

Refinement genealogy and sequence-extension remain separate.

R3c.0.2 should implement actual checks, not declarative/pass-through gates:

1. `CORE_LINEAGE_MATCHES_MEMBERSHIP`
   - every repeated bundle's lineage equals the source R3b.3 membership mapping.

2. `SINGLETON_PARENT_LINEAGE_MATCHES`
   - every non-orphan singleton outcome's parent bundle resolves to the expected lineage.

3. `NO_EXTENSION_OBJECT_IN_CORE`
   - no `SEQUENCE_EXTENSION_OVERLAY_ONLY` object occurs in core review-object outputs.

4. `EXTENSION_RELATIONS_OVERLAY_ONLY`
   - sequence-extension relations occur only in dedicated overlay outputs/views.

Do not add a redundant always-true fingerprint gate merely to increase gate count.

## 9. Genericity

Remove semantic dependence on:

`EXPECTED_REVIEW_CONTAINER_COUNT = 1066`

Instead validate source data dynamically:

- workspace row count,
- unique review-container ID count,
- blank ID count,
- duplicate ID count.

If desired, allow an optional CLI regression argument such as:

`--expected-review-containers 1066`

This must be a corpus-specific regression assertion, not part of MILAL's general logic.

## 10. Current development workflow

- This repository is the coding workspace.
- Codex implements and tests code here.
- Windows is now the primary real BHSA execution environment.
- The result ZIP is then examined for methodological correctness before moving to R4.

Do not move to R4 merely because unit/self-tests pass. R3c.0.2 cross-validation
is complete and the researcher reports a successful real R3c.1 Windows run.
R3c.2 still requires separately authorized processing of the frozen R3c.1 result
ZIP and inspection of its lossless compact packet.
