# JIN.0.2 independent parataxis / hypotaxis audit

Start commit: `178bea7fd73634c00a68828eb533c91991a3d69e`.
Scope: [exact authorization](R4_4_CONTRACT_JIN_0_2_RESEARCHER_SOURCE.txt),
[specification](R4_4_CONTRACT_JIN_0_2_SPEC.md),
[Windows/Termux execution](README_MILAL_R4_4_CONTRACT_JIN_0_2.md).
This report records technical validation, not acceptance of a relation or mother.

## Methodological result

The audit first generates clause-level linguistic candidates independently of
historical researcher judgments, freezes those bytes, and then compares them to
the historical judgments. It does not prove the old judgments by construction.
The single-mother principle applies to a hypotactic daughter, not automatically
to every textual locus. Parataxis is independently possible. Root selection and
clause-to-macro projection remain separate questions for human adjudication.

Readiness: **BLOCKED_PENDING_BLIND_RELATION_HUMAN_REVIEW**. Historical Q1–Q9
remain byte-identical and UNREVIEWED; new RQ1–RQ7 also remain UNREVIEWED with blank
answers. New human judgments, accepted paratactic/hypotactic relations, accepted
structural relations and parent edges are all **0**. No mother or root was chosen.
Participant arc stays UNADJUDICATED; the R4.4 consumer remains NOT IMPLEMENTED.

## Source separation

Preparation projects the exact 49 textual loci from the pinned JIN.0.1 ZIP into
neutral JT IDs and book/chapter/verse. Only the neutral projection enters the
fresh Phase A subprocess. The human ZIP is not a Phase A input.

Phase A reads exactly 28 logical sources: 23 explicit BHSA TF files, neutral
target JSON, linguistic rule JSON and the three discovery module files for their
hashes. The 23 TF files are otype, oslots, book, chapter, verse, typ, function,
domain, txt, lex, lex_utf8, g_word_utf8, trailer_utf8, sp, pdp, vt, vs, ps, gn, nu,
prs_ps, prs_gn and prs_nu. Physical file access is checked by the Python audit
hook. **Human-source count = 0; native-hierarchy source count = 0; label leakage
= 0.** Negative tests attempt actual forbidden file reads and module imports.

Corpus path: `C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021`.
All raw feature headers declare version 2021. The attested native book value is
`Iob`, explicitly mapped from display name `Job`; otype must be `book`.
BHSA `domain = ?` is Unknown, not positive domain evidence. Hebrew surfaces use
ketiv `g_word_utf8 + trailer_utf8` without inferred qere substitution.

The exact Phase A source hashes are in `06_blind_discovery_source_audit.csv`.
External `_run.log` files contain the physical source paths. Phase B verifies
`07_blind_discovery_manifest.csv` before loading the pinned human artifact and
mother/tab/pargr/rela/code. The coordinator independently checks the freeze
before B and checks that all Phase A files remain unchanged afterward.

## Blind population and provisional results

Job contains 2,938 source clauses. All clauses intersecting each of the 49
target verses are retained; the target is not reduced to a chosen representative.
163,207 predecessor pairs plus 263 forward-context pairs = **163,470 scanned**.
**13,355 eligible** pairs are preserved, including insufficient candidates.
150,115 scans lack an implemented trigger and are counted as NO_LINGUISTIC_SUPPORT.

| Blind hypothesis | Target-specific pair rows |
|---|---:|
| PARATAXIS_SUPPORTED | 80 |
| HYPOTAXIS_SUPPORTED | 147 |
| HYPOTAXIS_EXPLICIT_SUBORDINATION_SUPPORTED | 2 |
| PARATAXIS_AND_HYPOTAXIS_SUPPORTED | 0 |
| RELATION_CANDIDATE_INSUFFICIENT | 13,126 |

Thus hypotaxis-supported rows total 149, including the two explicit-subordination
rows. BOTH is supported and positively tested in synthetic controls, but occurs
zero times in this real pair population. Four loci nonetheless have separate
paratactic and hypotactic candidates and are proposed as JP5. Nothing is ranked.

Coverage is bounded by the published Boolean bundles: P1 requires verbal PNG
correspondence plus an explicit subject/frame correspondence, so purely nominal
clauses cannot satisfy P1 in this version. H1–H6 use a three-clause local window;
the full predecessor scan still preserves other eligible long-distance pairs.
Insufficient evidence therefore means insufficient under these implemented
rules, not proof that no linguistic relation exists. Raw features are retained
for the researcher to assess these operational limits without rewriting history.

## Historical comparison

98 historical SAME_LEVEL rows: **34 support found, 64 partial support**. There
is no automatic acceptance from either status. Among all 101 audited historical
same-level/mother relations: support 34; competing-alternative 0; partial 64;
insufficient 1; not-recovered 0; conflict 2. The other 149 historical relation
rows are preserved as outside this comparison's scope (250 total).

| Existing mother judgment | Independent clause evidence |
|---|---|
| 1:13 CHILD_OF 1:6 | CONFLICT: a paratactic candidate is supported; no hypotactic support for that historical pair |
| 3:1 HIERARCHICALLY_ABOVE 3:2 | INSUFFICIENT: eligible evidence remains insufficient for either relation |
| 40:1 CHILD_OF 38:1 | CONFLICT: a paratactic candidate is supported; no hypotactic support for that historical pair |

These are clause-level comparisons to historical macro judgments, not deletions
or reversals of those judgments. “Competing alternative” in the crosswalk means
both expected and opposite relation evidence for the compared anchor population;
the complete separate mother-candidate pool remains in file 05.

Job **2:11**: JP3, four supported hypotactic pair candidates, no supported
paratactic pair, no assigned mother. Job **32:1**: JP3, two supported hypotactic
pair candidates, no supported paratactic pair, no assigned parent. Both the
preceding and explicit forward context remain in files 03/04; placement uses
the target-as-later-clause population. Human FRIENDS_ARRIVAL/transition labels
appear only in post-blind comparison records.

The 2:11 hypotactic pairs are 497667→497669, 497668→497669,
497668→497671 and 497672→497675 (H4 pronominal morphology compatibility).
The 32:1 pairs are 499623→499625 (H2) and 499623→499626 (H4), with the
antecedent candidate at 31:40. These local surface candidates do not resolve
referential identity or assign 31:40 as a macro mother. The independent closure
control and all historical human judgments remain unchanged.

| Provisional placement | Loci |
|---|---:|
| JP1 root review | 0 |
| JP2 already human-mothered with blind support | 0 |
| JP3 hypotactic candidate | 17 |
| JP4 paratactic candidate | 19 |
| JP5 competing | 4 |
| JP6 transition review | 1 |
| JP7 insufficient | 8 |

Native post-blind comparison: AGREES 2, DIFFERS 0, NO_DATA 0, NOT_COMPARABLE
13,353. Exact native mother endpoints and documented rela values are required
for comparison; tab/pargr/code are retained without an invented decoder. Native
non-comparability is not evidence against a blind candidate.

## Observable controls inspected

| Loci | Raw observations, without human hierarchy labels |
|---|---|
| 1:6 / 2:1 | Way0 ויהי היום, WayX arrival of בני האלהים, InfC להתיצב, and WayX Satan arrival recur; 2:1 has another InfC |
| 1:13 | Same Way0 ויהי היום; following clauses are Ptcp eating/drinking, not the same surrounding configuration |
| 3:1 / 3:2 | xQtX פתח איוב את פיהו has raw Unknown domain; then curse clause; 3:2 has WayX answer plus Way0 say |
| 27:1 / 29:1 | WayX JSP + Job, InfC משלו, Way0 אמר; ADD_PROVERB_SAY recurs |
| 32:6 / 34:1 / 35:1 / 36:1 | Elihu lexeme recurs; first three answer/say, 36:1 add/say; 32:6 contains the longer subject and additional clauses |
| 38:1 / 40:6 | YHWH answer + Job object + storm lexeme/frame and say; raw ketiv variants retained |
| 40:3 / 42:1 | Job answer + YHWH object and say recur |
| 40:1 | YHWH answer + Job object and say; its internal location supplies no automatic CHILD_OF conclusion |

Source-node details and raw text are in 02 and the 14 review packet. The external
independent audit receipt records the complete control feature extracts.

## Next actual human review scope

**13,344 distinct ordered clause-pair cases** require relation adjudication in
the complete unranked `21_relation_review_cases.csv`. Its `blind_pair_ids` retain
all 13,355 target-specific occurrences; identity deduplication loses no evidence.
This includes insufficient eligible cases, not merely positively supported rows.
The exact list is the CSV, rather than a reconstructed list based on 57 old
unresolved parentage records. The packet also presents 101 historical comparisons
and 49 locus projections; these counts are not additive independent case counts.

RQ1–RQ7 cover paratactic support, hypotactic support, discrepancies, two basic
relation types, hypotactic-only mother cardinality, separate macro projection
and separate root selection. Every answer and relation-selection field is blank.

## Validation and release receipt

Validation completed on Windows, 2026-09-24:

- Syntax: all six new Python modules and the new test module parse; PowerShell
  and Bash runner syntax pass.
- Stage unit tests: **73 PASS**, skip 0.
- Full regression: **1,461 PASS**, failures 0, errors 0, skip 0 (378.621 seconds).
- Final synthetic self-test: **48/48 gates PASS**; all S1–S10 controls pass;
  researcher packet inspected. Both relation types, BOTH and multiple mother
  candidates are exercised; speaker/adjacency alone do not establish a relation.
- Real and independent real rerun: **48/48 gates PASS each**.
- External release gates: **2/2 PASS** (independent ZIP byte equality and full
  regression skip-zero). Every programmed gate has a negative mutation/test.
- Source-leakage gates pass: human source 0, native pre-freeze source 0, leaked
  human labels 0. Phase A directory bytes stay unchanged through Phase B.
- Final ZIP has **304 members**, all **278 historical members byte-identical**,
  **18 recursive 99 manifests plus the blind 07 manifest verified**, and **188
  frozen repository file pins verified**.
- Independent official Text-Fabric **13.1.0** comparison: **2,938 clauses**,
  **152,768 word-feature values**, **8,286 phrase records**, **510 native nodes**
  match. This independent loader runs only after the blind freeze.
- Complete case identity coverage and blank review fields verify. Historical
  HANDOFF sections are preserved verbatim below the new entry (heading changed
  from Current to Previous only). No previous analytical core was modified.
- Termux empirical execution was **not performed**; executable runner/documented
  commands and Bash syntax are provided. No regression test was skipped for this.

Final artifact:
`results/r4_4_contract_jin_0_2_blind_relation_audit_final_20260924_e_results.zip`
(14,432,509 bytes).
Independent rerun:
`results/r4_4_contract_jin_0_2_blind_relation_audit_final_20260924_f_results.zip`.
They are byte-identical. SHA256:

`837e34f552a63e9143eeaf0fe747b466f80c8d6868e8bb904519a47732fe3abd`

Blind freeze manifest SHA256:
`be97e9db3133fc8bdd898579ae28e34ce05af68246d71da704bcc389851038ab`.
Final synthetic ZIP:
`results/r4_4_contract_jin_0_2_synthetic_final_20260924_d_results.zip`, SHA256
`f04467eecef2d924415919130a9601382a03e37346669f63765a8221361a54c8`.

Local receipts (ignored, not committed):
`results/r4_4_contract_jin_0_2_regression_20260924_c.json`, corresponding `.log`,
`results/r4_4_contract_jin_0_2_unit_final_20260924_d.log`,
`results/r4_4_contract_jin_0_2_independent_audit_20260924_final.json` and `.log`,
plus each final real run's `_run.log` with physical Phase A/B source paths.

Two development preflights stopped at exact book identity checks before producing
blind output. The fixes follow the actual `book.tf`/`otype.tf` values; no fuzzy
fallback was introduced. Source inspection also corrected Unknown-domain handling
from the actual `domain.tf` header. New tests, synthetic execution, both real runs
and the final full regression were rerun after these corrections. No rule was
patched to agree with a historical human relation.
