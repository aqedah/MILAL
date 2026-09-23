# HSA3-FG-PREP validation — 2026-09-23

Starting commit: `92f989e8da282f105781b57688174d57257bc9ca`, main,
origin `https://github.com/aqedah/MILAL.git`. Clean working tree and no local-only
commits at entry; `git pull --ff-only origin main` reported already up to date.
Resulting commit message: `Audit narrator frames and final response complexes`.
This receipt is included in that commit; the final response reports its ID.

## Source and whole-book inventory

BHSA data: `C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021`.
Dataset version 2021; Text-Fabric 13.1.0. The complete Job snapshot contains
**2,938 clauses / 10,912 words**; 73 loaded feature/configuration files have
recorded SHA256. Focused panels cover 275 distinct clauses. Feature/node IDs,
exact pointed Hebrew surfaces and raw morphological values are preserved.

The narrow whole-book inventory has **20 occurrences**: 15 `>XR/` (after) and
5 `>XR=/` (other homonym). Classification:

| Classification | Count | Meaning |
| --- | --- | --- |
| TEMPORAL_SUPPORTED | 7 | Six explicit Time phrases plus 42:7 Conj before overt perfect verb |
| NON_TEMPORAL_OTHER_HOMONYM | 5 | Distinct lexical identity meaning other |
| UNRESOLVED_SENSE | 8 | Adju/Cmpl annotation alone does not settle temporal versus spatial/other sense |

The eight unresolved instances are 19:26, 21:33, 31:7, 34:27, 37:4, 39:8,
39:10 and 41:24. They are retained, not reclassified from contextual intuition.
The supported temporal instances are 3:1, 18:2, 21:3, 21:21, 29:22, 42:7, 42:16.
אחרית/אחרון derivatives are explicitly outside this narrow inventory and remain
in the full source snapshot; no prefix matching equates them with אחר/אחרי.

## Temporal and ויהי comparison

| Locus | Exact source evidence | Position and clause configuration | Frozen judgment |
| --- | --- | --- | --- |
| 3:1 | אַחֲרֵי־כֵ֗ן | clause 497687, xQtX; Time phrase 853607, words 336836–336837; positions 1–2 before פתח | PARAGRAPH_ONSET and SPEECH_UNIT_ONSET retained |
| 42:7 | אַחַ֨ר דִּבֶּ֧ר יְהוָ֛ה | clause 500412, xQtX; אחר is Conj phrase 861220 at position 1; דבר is annotated perf; separate preceding clause 500411 is Way0 ויהי | PARAGRAPH_ONSET |
| 42:16 | אַֽחֲרֵי־זֹ֔את | clause 500448, WayX; Time phrase 861358, words 346914–346915; positions 4–5 after predicate and overt Job | NO_BOUNDARY / CONTINUES_WITHIN 42:7 |

42:16 word 346912 is `XJH[` / חיה, wayq, p3/m/sg. It is not `HJH[` / היה.
42:7 word 346679 is היה wayq, p3/m/sg. Exact lexical/morphological checks keep
ויהי and ויחי distinct. MR1 Way0/is_wayhi rows are reused by start_clause and
remain separate from lexical flags. 42:12 clause 500441 also has היה wayyiqtol
(word 346850) but is WayX, not a MR1 Way0 candidate or a new boundary.

## Repeated scene configuration and formal shift

All three opening clauses at 1:6, 1:13 and 2:1 have the exact lexical sequence
W / HJH[ / H / JWM/. In the configured windows:

| Window | בני האלהים | להתיצב על יהוה | Divine–Satan speech clauses |
| --- | --- | --- | --- |
| 1:6–12 | 1 match | 1 match | 497542, 497548, 497564 |
| 1:13–19 | 0 | 0 | none |
| 2:1–7 | 1 match | 2 matches | 497628, 497634, 497650 |

The latter windows are correspondences, not identical strings or clause lists:
2:1 has an additional standing clause. 1:13 instead has eating/drinking
participial configuration. All ordered clause surfaces remain visible.
The accepted 1:6/2:1 siblings and 1:13 child of 1:6 remain unchanged.

27:1: `וַיֹּ֣סֶף אִ֭יֹּוב שְׂאֵ֥ת מְשָׁלֹ֗ו וַיֹּאמַֽר׃`.
36:1: `וַיֹּ֥סֶף אֱלִיה֗וּא וַיֹּאמַֽר׃`.
Both use JSP[ then AMR after preceding ANSWER-type onsets. 27:1 additionally has
the NF>[ / MCL/ sequence (342378–342379); 36:1 does not. The 16 configured cycle
onsets and 32:6/34:1/35:1 preserve ANSWER forms. 27:1 remains in POST_DIALOGUE_JOB;
36:1 remains the fourth onset within ELIHU_SPEECH_SEQUENCE. Formal similarity
does not assert equal structural function, parentage or a new group.

## F evidence

38:1 and 40:6 share ANSWER+AMR, explicit YHWH subject / Job object and storm
lexeme S<RH/. Preserve the article difference: 38:1 has הַסְּעָרָה, 40:6 סְעָרָה.
40:3 and 42:1 share ANSWER+AMR with explicit Job subject / YHWH object.
The existing two peer pairs and 40:1 CHILD_OF 38:1 remain unchanged.

38:3 clause 500081 and 40:7 clause 500272 have the identical surface
`אֱזָר־נָ֣א כְגֶ֣בֶר חֲלָצֶ֑יךָ` and exact five-lexeme sequence
>ZR[ / N> / K / GBR/ / XLY/. The following asking clauses differ in initial
W: 38:3 WYq0 versus 40:7 ZYq0. These are comparison evidence for already
established peers, not automatic sibling/parent assignments.

**Three candidate propositions remain UNADJUDICATED**: two proposed complexes
(38:1–40:5 and 40:6–42:6), plus their possible peer relation. They are not created
composition objects. All have automatic_resolution=false, UNREVIEWED and empty
response fields. No semantic response antecedent is assigned from adjacency.

## G evidence and 42:16 countervailing observations

- 42:7: Way0 היה clause, separate clause-initial אחר/Conj + דבר/perf + YHWH,
  then WayX speech toward Eliphaz and quoted Q-domain clauses. Existing onset retained.
- 42:9: explicit friends in a WayX clause, subsequent action, speech-reference
  xQtX and YHWH/Job clause. Full configuration retained without a new boundary.
- 42:10: subject-first WXQt (`ויהוה שב`), InfC prayer clause, WayX addition and
  NmCl. Participant/state-change evidence retained; no major-boundary promotion.
- 42:12: subject-first WXQt (`ויהוה ברך`) parallels the initial configuration
  at 42:10; a following WayX היה clause lists possessions. No new sibling,
  parent or paragraph relation is asserted.
- 42:16: WayX חיה with overt Job, post-predicate אחרי זאת and duration Time
  phrase; following seeing/generations clauses retained. Temporal reference,
  overt participant and possible life-summary shift are visible countervailing
  observations for review. This audit does not judge them a contradiction of
  NO_BOUNDARY or decide whether to revise the historical judgment.

SIMILARITY, DIFFERENCE, STRUCTURAL_IMPLICATION and CURRENT_JUDGMENT are separate
fields. The report does not defend a frozen judgment by suppressing contrary
observations, nor promote an observation to a new structural decision.

## Validation

- Syntax/JSON validation: PASS.
- **65 new tests PASS**, zero skips; final stage test duration 15.340 seconds.
- **1,071 full regression tests PASS**, zero failures/errors/skips,
  199.506 seconds (1,006 prior + 65 new).
- Every one of 44 model gates has a failure mutation; MANIFEST_VALID has a
  corruption negative test. Synthetic self-test: **45/45 PASS**.
- Final synthetic packet inspected; mode clearly SYNTHETIC, all links/manifests
  valid, both historical 3:1 functions visible and researcher fields blank.
- Real BHSA run and independent invocation: **45/45 PASS each**.
- Complete real ZIPs are byte-identical, CRC valid, 183 members,
  all 12 manifest checks PASS.
- All 146 A/C and 17 MR1 original members preserved byte-for-byte.
- 134 pinned prior repository files unchanged; 73 BHSA feature/config hashes recorded.
- Independent audit verified 275 source clause hashes and 67 unique frozen
  CSV row links, with exact identity/data-row/member/raw-row hashes.
- No previous analytical core changed. A–E stay frozen; F/G stay UNREVIEWED;
  ANA Q2/Q4/Q5 accepted and Q3 deferred remain unchanged; no R4.4.
- Computed new human judgments = **0**, new textual relations = **0**,
  new accepted overlay relations = **0**.

Real ZIP: `C:\MILAL\results\hsa3_fg_prep_real_final_20260923_a_results.zip`

SHA256: `14dd08fcffabf2d29b6574c05254ca403ba08b9fe01207269ccd6fb9ca3db1f6`

Independent repeat: `C:\MILAL\results\hsa3_fg_prep_real_repeat_20260923_a_results.zip`
with identical bytes/SHA256.

Final synthetic: `results/hsa3_fg_prep_synthetic_final_20260923_c_results.zip`,
SHA256 `29c91b050fa73794e2683ecac38dd3dc2459278da3cdb691112b09c4c93d1c2a`.
Logs: `results/hsa3_fg_prep_unit_final_b.log`,
`results/hsa3_fg_prep_full_regression_final.log` and matching `_run.log` files.

## Remaining human questions

Packet: `C:\MILAL\results\hsa3_fg_prep_real_final_20260923_a\11_hsa3_fg_prep_review_packet.md`.

F: Do the established peer pairs support two same-level YHWH–Job response
complexes: 38:1–40:5 and 40:6–42:6?

G: What relation connects the YHWH–Job speech complex ending at 42:6 with the
final narrative beginning at 42:7? Retain internal controls 42:10/12/16.

No answers are supplied. Narratorial Frame Spine remains an evidence overlay.

## Intended repository changes

- `.gitattributes`
- `config/hsa3_fg_prep_job.json`
- `docs/HANDOFF.md`
- `docs/HSA3_FG_PREP_RESEARCHER_SOURCE.txt`
- `docs/HSA3_FG_PREP_SPEC.md`
- `docs/HSA3_FG_PREP_VALIDATION_REPORT.md`
- `docs/README_MILAL_HSA3_FG_PREP.md`
- `scripts/run_milal_hsa3_fg_prep_windows.ps1`
- `src/milal_hsa3_fg_prep.py`
- `src/milal_hsa3_fg_synthetic.py`
- `tests/test_hsa3_fg_prep.py`

Input/output ZIPs, generated snapshots, logs and BHSA data remain ignored/local.
