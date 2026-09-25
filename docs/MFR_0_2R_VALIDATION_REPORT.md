# MFR.0.2R validation report — Job-only release

Technical validation completed on computer A, 2026-09-25. This establishes the
executable engine and readiness for human revalidation, not scholarly acceptance.
The primary analysis, candidate universe, provisional hierarchy and review are
JOB only. Non-Job cases are post-freeze explicit-reference fixtures; HB_CORPUS is
construction search only. No full-Pentateuch result is included in this release.

## Required final report

| No. | Item | Verified result |
|---:|---|---|
| 1 | Start commit | `2ff2536f50998beec585b8cb187abbf2086d97e0` |
| 2 | End commit | Commit containing this report, titled `Implement clause relation grammar engine`; exact resulting SHA reported with push verification |
| 3 | Push | Finalization follows all gates; actual push outcome is reported separately, not inferred by this report |
| 4 | Working tree | Intended source/docs/tests staged only; four user PDF inputs remain untracked |
| 5 | Adopted relations | 24 Jin type relations; 4 additional active Walton procedures; 4 unverified draft records disabled |
| 6 | RG-A explicit subordination | 4 |
| 7 | RG-B different-type hypotaxis | 10 |
| 8 | RG-C same-type hypotaxis | 4 |
| 9 | RG-D same-type parataxis | 2 |
| 10 | RG-E different-type parataxis | 4 |
| 11 | Job clauses | 2,938 |
| 12 | Job clause atoms | 2,977 |
| 13 | Temporal evidence | 2,938 rows |
| 14 | Locative evidence | 2,938 rows |
| 15 | Participant evidence | 2,938 rows in combined participant/reference table |
| 16 | Reference evidence | Same 2,938 combined records, not another independent population |
| 17 | Domain evidence | 2,938 rows |
| 18 | Targets with candidates | 2,895; 43 without candidates retained |
| 19 | Preceding candidate pairs | 1,049,504 |
| 20 | Targets with one candidate | 50 |
| 21 | Targets with two or more | 2,845 |
| 22 | Long-distance candidate pairs | 1,032,178 (distance >20; reporting threshold, not admission filter) |
| 23 | Hypotactic | 49,114 HYP-only pairs; 55,253 HYP edges including MULTIPLE |
| 24 | Paratactic | 40,676 PARA-only pairs; 46,815 PARA edges including MULTIPLE |
| 25 | Multiple | 6,139 pairs |
| 26 | Formal-only | 21,088 pairs |
| 27 | Insufficient | 932,487 pairs |
| 28 | Hard global conflicts | 6,741 conditional conflicts |
| 29 | Soft conflicts | 1,097 |
| 30 | Ambiguity components | 19 |
| 31 | Materialized variants | 81 |
| 32 | Symbolic components | 1; exact candidate IDs and constraints retained |
| 33 | MFR.0.2A decisions | All 13 preserved with original hashes and provisional status; prior PARA count 5 |
| 34 | Strongly supported | 0 |
| 35 | Supported with alternatives | 0 |
| 36 | Requires revision | 0 |
| 37 | Not yet decidable | 12; remaining 1 INSUFFICIENT_CONFIRMED |
| 38 | Lev 25–26 control | 4 source cases with relation candidates recovered, including competing/configuration checks; no winner |
| 39 | Num 26 control | 2 alternative configurations representable; no winner |
| 40 | EDSF fixture | 2 configurations representable; fixture only |
| 41 | Same-pattern/different-level | 5/5 explicit cases supported with minimum preceding context |
| 42 | Cross-book control | 338 supported fixture pairs; Job primary cross-book pairs 0 |
| 43 | Frozen file changes | 0 across 422 pinned files |
| 44 | New human judgments | 0 |
| 45 | Canonical new mothers | 0 |
| 46 | Canonical whole hierarchies | 0 |
| 47 | Stage tests | 251 passed; failures 0, errors 0, skips 0 |
| 48 | Full regression | 2,403 passed in 791.932 seconds; failures 0, errors 0, skips 0 |
| 49 | Gates | 89/89 PASS; each has propagation and actual invariant mutation coverage |
| 50 | Deterministic rerun | Independent Job A/B files reused; final A/B manifest and ZIP bytes identical |
| 51 | ZIP | `D:\MILAL_runs\mfr02r_20260925\release_a_results.zip`; independent B on F: below |
| 52 | ZIP SHA256 | `93ff58ba3f1498e5e93a4aaf23e15ceb777d54ef2704edf3c15fcffad9f05b7d` |
| 53 | Engine | CLAUSE_RELATION_GRAMMAR_ENGINE_ESTABLISHED |
| 54 | Readiness | READY_FOR_CANDIDATE_SET_HUMAN_REVALIDATION |

The 12 undecidable revalidations do not overturn human judgments: a compound
human configuration is not equivalent to one onset edge. Original decisions
remain intact. All 2,528 new review cases have blank adjudication fields.

## Validation and reproducibility

- Current code/config/test fingerprint: `44ec0c7bf7358896aeac710e8c97aba4c8a4ce865ad012bb760c929f8fb6534a`.
- Full receipt: `D:\MILAL_runs\mfr02r_20260925\regression_fixture_context.json` and adjacent `.log`.
- A: `D:\MILAL_runs\mfr02r_20260925\release_a`.
- B: `F:\MILAL_runs\mfr02r_20260925\release_b`.
- Independent B ZIP: `F:\MILAL_runs\mfr02r_20260925\release_b_results.zip`.
- Verification receipt: `D:\MILAL_runs\mfr02r_20260925\release_a_verification.json`.
- Final manifest entries: 2612. ZIP CRC and every member hash verified.
- Preserved Job manifest SHA256: `231a3fd765480389c4dca58e130c793852fd5f3e1732230118c7b58c21ecd02b`.
- Original Job producer fingerprint: `cf13911188386365157ae9b63df8b8063c16c27ba357ab230e986551d5c8f0cc`.
- Python syntax passed for all 22 new implementation/test modules; PowerShell parser passed.
- Synthetic self-test: 7 clauses/atoms, 21 pairs (HYP-only 6, MULTIPLE 4,
  insufficient 11); 10 HYP and 4 PARA edges; 7 hard/3 soft conflicts, one symbolic
  component. Six synthetic target packets inspected; human fields blank.
- Real packet inspection confirmed Hebrew source text, exact clause IDs,
  source/target alternatives, evidence dimensions, conflict/variant references
  and links to complete machine-readable records. No candidate preselected.
- Git staging preserves exact tested configuration bytes via two explicit `-text`
  attributes. Staged source/config/test bytes equal the validated working files.
  Diff inspection notes one harmless extra blank EOF line in the synthetic module;
  no analytical source was changed after the final regression.
- Release guards also reject missing/duplicate gates, non-boolean pass values,
  wrong mode/stage, stale code fingerprints and differing files.
- The four scope gates all PASS: PRIMARY_ANALYSIS_SCOPE_JOB_ONLY,
  PENTATEUCH_FULL_ANALYSIS_ABSENT, PENTATEUCH_CONTROLS_FIXTURE_ONLY,
  CORPUS_SEARCH_NOT_CONFUSED_WITH_ANALYSIS_SCOPE.

A/B are independent Windows executions on the same computer, not a claim of
cross-platform replication. Termux runner exists; no Termux empirical run is claimed.

## Source provenance and methodological interpretation

MILAL does not simply reproduce Jin's methodology. It selectively adopts
bottom-up linguistic observation, preceding-clause search, paratactic/hypotactic
principles and whole-structure reassessment, and extends them with exhaustive
computational candidate generation within explicit predicates, evidence
provenance, alternatives, compatibility analysis, deterministic reproduction
and explicit human adjudication history. Recovering Jin's chosen hierarchy is
not the success criterion; exposing plausible alternatives is.

Jin Chapter 3, §§3.2.9.2–3.2.9.4.2, printed pp.25–35, was verified locally.
RG-A/B/C/D/E correspond respectively to §§3.2.9.2, 3.2.9.3.1, 3.2.9.3.2,
3.2.9.4.1 and 3.2.9.4.2. Clause-type relations are DIRECTLY_ADOPTED;
required/supporting/counterevidence features and functional-role schema are
GENERALIZED_FOR_MILAL. Unverified additions remain UNKNOWN_NOT_VERIFIED and disabled.

Walton §§2.1.1.1–2.1.2.4, pp.16–19, iterative reasoning pp.18–19/27 and
long-distance discussion p.28 were verified. Time, location, participant and
reference are first-class dimensions; participant status is lexical evidence,
not resolved identity. Same-type clauses can support exceptions rather than a
hard parataxis default. There are 129 Jin/Walton conflict records with no
forced winner. Revision history is append-only and hashed; semantic
correspondence remains a separately sourced secondary stage. Walton's Qohelet
conclusions were not encoded as Job answers.

BHSA 2021 path: `C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021`.
Runtime Python 3.12.7, installed Text-Fabric 13.1.0. Execution uses the frozen
raw-feature reader rather than the TF app loader. Native mother/rela are
DATABASE_EXISTING_RELATION, never accepted textual hierarchy.

| Input stage | Exact ZIP SHA256 | Members | CRC/member manifest |
|---|---|---:|---|
| MFR.0.1 | a0904cb11931790e6d78d53f5f67731aba067c5feca4ed50dd10eb11e268b05d | 103 | PASS |
| MFR.0.1a | c5815d00ec4383296568d24b03693dc8fc64ba52803d76563a2b34a46b2f1a92 | 1238 | PASS |
| MFR.0.1b | 47b1dff0d19556a6d467df00cf4e0e8b439d33f7f1028d1d52d3c48434023f81 | 75 | PASS |
| MFR.0.2A | 6be4c760a07aaa18cfbdb8229dd575bf3ffb6fef2941bdb926ab4e351007d2cf | 34 | PASS |

## BOSMAN_INTEGRATION

1. Verified sections: §9.1 pp.201–207 (hidden units p.204), §12.1 pp.246–247,
   §§13.1–13.5 pp.251–256, Appendix A pp.293–294.
2. Adopted distinctions: textual syntax, participant/reference and poetic
   structure can disagree. Executable typed edges, factorized unit memberships,
   revision schemas and 13 descriptive label definitions are MILAL generalizations.
3. Lamentations acrostics, strophes and literary conclusions are not imported
   into Job. Verified Job colon/strophe boundaries are NOT_AVAILABLE.
4. Larger-unit reference evidence: 2,241 factorized rows, 1,187,395 source-unit /
   target pairs and 19,377,530 antecedent/target triples, with exact path witnesses
   recoverable by query. Compression does not discard evidence.
5. Participant/syntax divergence is representable and negatively tested; actual
   referential identity remains unresolved. Potential references are not counted
   as adjudicated divergences or accepted participant identities.
6. Poetic evidence covers 1,049,504 pairs: 2,124 observed formal correspondences,
   1,047,380 without verified poetic relation; one poetry-aware exception
   candidate. These are not confirmed poetic/syntactic contradictions. Prosody
   is NOT_VERIFIED for the 2,124 and NOT_AVAILABLE for the remainder.
7. POETIC_LEXICAL_PATTERN occurs 2,124 times; POETIC_CONFIGURATION 121;
   121 pairs carry multiple poetic categories, without syntax override.
8. Program/human matrix: 95,929 PROGRAM_PROPOSED_HUMAN_UNDECIDED and
   953,575 PROGRAM_NOT_PROPOSED_HUMAN_UNDECIDED.
9. Human rejection preservation is tested with provenance-bearing synthetic
   events. There are zero newly rejected real candidates because no new human
   adjudication occurred; nothing was deleted on that basis.
10. Rule-discovery/decision-learning table: 1,049,504 rows, retaining proposals,
    evidence, human-event fields, competing candidates and revision references;
    no model training performed.
11. Synthetic tests cover typed-layer separation, unit expansion/path witnesses,
    multi-labels, divergent evidence, source provenance, rejection and immutability.
12. Lamentations controls materialize only explicit references and minimum
    context (22 clauses), after Job freeze. No Lamentations hierarchy generated.
13. All 17 Bosman-specific gates PASS, within 89 tested gates; each has negative
    mutation coverage. Source crosswalk and poetic rows preserve author/work/pages.
14. Frozen analytical changes: zero.
15. Canonical hierarchy changes: zero. Apparent conflicts remain alternatives.

## OOSTING_INTEGRATION

1. Verified §§1.1.4 pp.25–27, 1.2 introduction pp.28–30, 1.2.3–1.2.4 pp.39–43,
   1.3 p.48, 1.3.6 pp.61–64 and 1.4 p.65.
2. Adopted concepts: valency before clause relations, exact construction,
   atom binding, recursive potentials, corpus analogues and secondary textual
   tradition. JSON signatures/index keys and executable predicates are MILAL schemas.
3. No Isaiah-specific participle reading, composition conclusion or emendation
   adopted. No obligatory-valency lexicon available; missing arguments UNKNOWN.
4. Observed valency signatures: 2,938, with actual Pred/PreC nominal predicates;
   absent predicates cannot manufacture analogue matches.
5. Internal binding candidates: 39; raw clause/atom identities remain preserved.
6. Atom-level relations deferred for binding: 39; no arbitrary clause merger.
7. HB supplement: 2,938 Job construction cases, comprising exact 396, close 658,
   partial 1,436 and no analogue 448. Search index contains 88,131 exact clause
   identities across 39 BHSA books; no corpus hierarchy generated.
8. Cross-book analogues: 2,437 Job cases, 1,257,487 distinct Job-source / other-book
   target links across exact/close/partial classes (deduplicated within source).
9. Behavior-variation/counterexample patterns: 43, preserved as observations.
10. Masoretic secondary rows: 2,938; 1,097 display a secondary tiebreaker context,
    1,841 do not; all assessments NOT_DECISIVE. 79 qere-variant words. No accent
    boundary or emendation is accepted automatically.
11. All 1,049,504 Job pair assessments follow the construction stage. The 39
    binding deferrals concern atom independence, not deletion of Job clause pairs.
    HB supplementation modifies zero frozen Job candidate/graph files.
12. Synthetic tests cover valency/nominal predicates, binding across interruption,
    exact signatures, unknown arguments, false empty analogues, secondary accents
    and provenance of participant dual use.
13. Two binding controls pass; Isaiah explicit fixtures select 25 clauses only.
    Qohelet selects 19; Pentateuch selects 115. No whole-book control analysis.
14. All 17 Oosting-specific gates PASS, within 89 gates, with negative coverage.
15. Frozen analytical changes: zero.
16. Canonical hierarchy changes: zero. Later plot/discourse interpretation remains
    outside this implementation and requires explicit human provenance.

The preserved Job files retain the former configured-union analogue results
(exact 341, close 548, partial 1,497, none 552). They are historical provenance,
not relabeled HB-wide search. The separate `corpus_search/01_job_hb_analogues.csv`
and index/receipt provide current HB coverage without modifying Job results.
HB index SHA256: `dabb7c1746cb910e731cc01ecc4f82689da2285deec1f537c5404a464753aab6`.
All 2,938 Job signatures match exactly. HB search includes the corpus as encoded;
it does not promote Aramaic passages or other books into primary analysis.

## Correction history and limits

Initial broad-scope workers were stopped immediately on the researcher's scope
correction. Their partial external outputs remain audit-only and are excluded
from release. Completed independent Job files were retained and never rerun.
Earlier interrupted attempts have no claimed successful validation receipt.

The first fixture-only attempts failed on an empty-set JSON value. A synthetic
regression now covers conversion to the same boolean convention as the primary
writer. A subsequent control recovered 4/5 same-pattern cases because the opening
Exod 4:19 clause lacked preceding context. The final, uniformly applied reading
policy includes one immediately preceding verse within the same book, separately
marked as minimum context, plus complete clauses/enclosed interruptions. This is
not a nearest-mother heuristic or an answer patch; no relation rule changed.
Final controls recover 5/5. Job graph and candidate generation were unaffected.

Human configuration acceptance, participant identity, prosodic units and later
semantic roles remain unresolved where source evidence is insufficient. Technical
success authorizes MFR.0.2R-H human revalidation, not resumption/closure decisions,
new canonical mothers, a whole tree, or an R4.4 consumer.

## Files changed

Exact repository-relative paths in this release:

- `.gitattributes`
- `config/clause_relation_grammar_v1.json`
- `config/mfr_0_2r_controls.json`
- `config/mfr_0_2r_evidence_labels.json`
- `config/mfr_0_2r_job.json`
- `config/mfr_0_2r_required_gates.json`
- `docs/CLAUSE_RELATION_GRAMMAR.md`
- `docs/HANDOFF.md`
- `docs/MFR_0_2R_BOSMAN_SOURCE.txt`
- `docs/MFR_0_2R_OOSTING_SOURCE.txt`
- `docs/MFR_0_2R_RESEARCHER_SOURCE.txt`
- `docs/MFR_0_2R_SCOPE_CORRECTION.md`
- `docs/MFR_0_2R_SOURCE_CLARIFICATION.md`
- `docs/MFR_0_2R_SPEC.md`
- `docs/MFR_0_2R_VALIDATION_REPORT.md`
- `docs/MFR_0_2R_WALTON_SOURCE.txt`
- `docs/README_MILAL_MFR_0_2R.md`
- `scripts/run_milal_mfr_0_2r_termux.sh`
- `scripts/run_milal_mfr_0_2r_windows.ps1`
- `src/milal_mfr02r_controls.py`
- `src/milal_mfr02r_data.py`
- `src/milal_mfr02r_engine.py`
- `src/milal_mfr02r_features.py`
- `src/milal_mfr02r_gates.py`
- `src/milal_mfr02r_grammar.py`
- `src/milal_mfr02r_graph.py`
- `src/milal_mfr02r_io.py`
- `src/milal_mfr02r_layers.py`
- `src/milal_mfr02r_pipeline.py`
- `src/milal_mfr02r_query.py`
- `src/milal_mfr02r_review.py`
- `src/milal_mfr02r_revision.py`
- `src/milal_mfr02r_scope.py`
- `src/milal_mfr02r_synthetic.py`
- `src/milal_mfr02r_valency.py`
- `tests/test_mfr02r_gate_artifacts.py`
- `tests/test_mfr02r_grammar.py`
- `tests/test_mfr02r_layers.py`
- `tests/test_mfr02r_scope.py`
- `tests/test_mfr02r_valency.py`
- `tests/test_mfr02r_validation.py`
