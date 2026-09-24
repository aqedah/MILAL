# R4.4-CONTRACT.JIN.0.9 validation report

Date: 2026-09-24. Readiness: **READY_FOR_TOP_LEVEL_HUMAN_ADJUDICATION**.
This is technical audit completion, not human acceptance or R4.4 implementation readiness.

## Git and authority (requested items 1–4)

Repository `aqedah/MILAL`, branch `main`, verified origin
`https://github.com/aqedah/MILAL.git`.
Start HEAD: `e64f115a97dc7e57c7b70a19885919e979c8ec8c`.
The release commit containing this report is the end commit; its exact ID, push result
and post-push clean-tree check are reported in the final task response to avoid a
self-referential commit hash. Commit/push is explicitly authorized by request section 49.

Exact researcher source: `docs/R4_4_CONTRACT_JIN_0_9_RESEARCHER_SOURCE.txt`.
SHA256 `d4b28ad0bbdf62d37f3a11fc31dcf1e52fe0badb43fae1a0d855b011e1701991`.
Specification: [JIN.0.9](R4_4_CONTRACT_JIN_0_9_SPEC.md).
Execution: [Windows/Termux README](README_MILAL_R4_4_CONTRACT_JIN_0_9.md).

## Independent source boundaries

Real raw source: `C:/Users/yisaa/text-fabric-data/github/etcbc/bhsa/tf/2021`,
BHSA 2021, raw book feature `Iob`. The existing raw TF-file reader is reused;
this execution does not require or claim a Text-Fabric API reload.
S and M run in separate guarded Python processes. Each has its own source read
audit, raw inventory, model, and physically frozen manifest. M does not read S.
Only after both freezes does the coordinator open the historical human archive.

Observed sequence: `S_FREEZE_VERIFIED`, `M_FREEZE_VERIFIED`,
`HUMAN_ARCHIVE_OPENED`, `POSTBLIND_COMPARISON`.
S/M human-source, native-hierarchy-source and human-label leakage counts: **0 / 0**
for each measure. Native `mother`, `tab`, `pargr`, `rela`, `code` are not loaded.
Human outline/group names are absent from the blind discovery inputs.
Raw chapter/verse references are descriptive, not selection rules.

Historical input: `results/jin08_real_recovered_20260924_a_results.zip`.
SHA256 `0c23eeb732e7b94117fddf6705b164f5776893b619ef1f6a810923f343890ad1`.
All 483 upstream members remain byte-identical. All 273 frozen repository pins
remain unchanged. No previous analytical core was edited.

## Strict findings (items 5–11)

| Measure | Count |
| --- | ---: |
| Raw clauses, all preserved | 2,938 |
| Retained relation candidates (including insufficient candidates) | 9,337 |
| Explicit/local hypotaxis candidates | 44 |
| All hypotaxis-supported candidates | 799 |
| Parataxis-supported candidates | 108 |
| Narrative-to-speech dependency candidates | 151 |
| Within-actual-clause finite/infinitive observations | 10 |
| Top-level candidate records | 421 |
| Distinct top-level candidate references | 269 |

Candidate-kind counts overlap: S_TOP_UNEMBEDDED 330; S_TOP_LEVEL_INSUFFICIENT 90;
S_TOP_PARATACTIC 12; S_SCOPE_INITIAL 1. These are possible dispositions, not
adjudicated roots or parents. Within-clause observations create no clause edge.
All prior matching formal-family/verb-form candidates are indexed; local explicit
dependency checks retain the established bounded linguistic window. No nearest-only
mother choice or chapter boundary filter is applied.

Observed configurations, both UNADJUDICATED and unselected:

- `S_CONFIG_MULTIPLE_TOP_LEVEL_PARATACTIC_CANDIDATES`
- `S_CONFIG_INSUFFICIENT`

Full candidate identities/evidence: `03_strict_top_level_candidates.csv` and
`05_strict_candidate_evidence.csv` in the release directory. All references appear
in Appendix S below; multiple clauses may share one verse reference.

## Macro findings (items 12–18)

| Measure | Count |
| --- | ---: |
| Complete raw clause-observation inventory | 2,938 |
| Marker-bearing clause observations | 1,189 |
| Onset candidates | 1,074 |
| Closure candidates | 308 |
| Repeated multi-clause configuration families | 13 |
| Macro relation candidates | 41 |
| Containment-possible / parataxis-possible candidates | 28 / 13 |
| Top-level candidate records | 234 |
| Distinct top-level candidate references | 157 |

The reported raw marker count is **marker-bearing clause observations**, not
1,189 distinct tokens or events. A clause may expose several simultaneous flags;
all 2,938 inventory rows and all flags remain available.
Candidate-kind counts overlap: M_TOP_UNCONTAINED 219; M_TOP_PARATACTIC 18;
M_TOP_LEVEL_INSUFFICIENT 15; M_SCOPE_INITIAL 1.
Exact ordered multi-clause formal families receive neutral MF IDs. No historical
composition group supplies family discovery or a container. Containment requires
the conjunction of recorded formal, temporal/locative/domain, participant-surface,
asymmetry and closure evidence; candidate coverage is descriptive, not ranking.

Observed configurations, both UNADJUDICATED and unselected:

- `M_CONFIG_MULTIPLE_TOP_LEVEL_PARATACTIC_UNITS`
- `M_CONFIG_INSUFFICIENT`

Full candidate identities/evidence: `12_macro_top_level_candidates.csv` and
`14_macro_candidate_evidence.csv`. All references appear in Appendix M.

## Post-blind historical comparisons (items 19–22)

These statuses describe recovery under this audit's permitted evidence. They do
not accept/reject the historical human decisions or migrate relations.

### Strict comparison statuses

| status | count |
| --- | --- |
| S_ALTERNATIVE_SUPPORTED | 2 |
| S_HISTORICAL_NOT_RECOVERED | 11483 |
| S_HISTORICAL_PARTIAL | 1636 |
| S_HISTORICAL_SUPPORTED | 378 |
| S_MULTIPLE_OPTIONS | 79 |

### Macro comparison statuses

| status | count |
| --- | --- |
| M_HISTORICAL_NOT_RECOVERED | 10 |
| M_HISTORICAL_PARTIAL | 98 |
| M_HISTORICAL_SUPPORTED | 2 |
| M_INSUFFICIENT | 2 |
| M_MULTIPLE_OPTIONS | 2 |

### Groups comparison statuses

| status | count |
| --- | --- |
| M_HISTORICAL_NOT_RECOVERED | 2 |
| M_HISTORICAL_PARTIAL | 10 |

Strict comparison has 13,578 rows: 13,344 JIN.0.2 historical candidate rows,
229 JIN.0.3 rows, two explicit controls and three unresolved-hypotaxis fixtures.
The two explicit controls 499628→499631 and 499629→499631 are recovered with
multiple options preserved. The 3:1/3:2 fixture is partial. For 1:13→1:6 and
40:1→38:1, parataxis evidence is `S_ALTERNATIVE_SUPPORTED`, not confirmation of
the historical HYPOTAXIS candidate. `expected_relation_family` makes this distinction
inspectable. Manual inspection found an initial status conflation; a failing
regression was added before correcting only the post-blind comparison. S/M blind
artifacts are unchanged. Final validation was rerun in the required order.

Macro comparison has 114 rows; composition comparison has 12 groups. Ten groups
have partial onset evidence. DIALOGUE_CYCLE_SEQUENCE and YHWH_JOB_RESPONSE_SEQUENCE
are not recovered through direct clause anchors. Groups whose members are themselves
groups are not expanded into invented textual mothers; non-recovery is not refutation.
All historical source members, hashes, row numbers and original records are linked.

Cross-layer comparison has 423 exact-anchor rows: 232 shared, 189 strict-only,
two macro-only. Shared anchors do not imply shared root status. No automatic
unification, identity inference or source feedback occurs.

## Job 1:1 and competing candidates (items 23–26)

Job 1:1 is present as STC0001 and MTC0001, raw clause 497514 / atom 587617.
It is scope-initial and has locative and explicit participant-introduction surface
features. S assigns S_SCOPE_INITIAL_CANDIDATE only. M additionally records
M_TOP_LEVEL_INSUFFICIENT. Neither selects it as root or establishes uniqueness.
Participant surfaces `<WY=/` and `>JC/` remain surface observations, identity UNRESOLVED.
No missing mother is converted into root evidence.

The raw initial domain is `?`, not N. It is preserved without repair. The whole-book
frame observation finds shared opening/final participant lexemes `>JC/`, `>JWB/`
and verbal lexeme `HJH[`, but raw domain recurrence fails (`?` versus N).
Thus the observation remains M_RELATION_INSUFFICIENT; no covering span or higher
frame is synthesized. Inspect `blind/M/m_frame_observation.json` for complete evidence.
This is a limitation requiring human assessment, not an invitation to force N.

There are many competing candidates (full references in appendices). Requested
controls were checked only after discovery. All 23 loci have raw source evidence
and an onset or closure observation. 3:1 and 31:40 do not become macro top-level
candidates under these rules; 37:24 is a closure-only observation, not an onset or
top candidate. This preserves the difference between evidence and selection.

## Scope and integrity (items 27–36)

ROOT:STRICT and ROOT:MACRO remain **UNREVIEWED**, with five questions each.
All 220 original scope records are preserved exactly; only these two root scopes
are direct review targets. The remaining 218 are context-only and unresolved by
this task. Existing judgments are preserved without automatic completion.
2:11 and 32:1 remain NO_MACRO_MOTHER_FOUND.

New human judgments, selected roots, parent edges, accepted strict/macro relations
and migration: **all zero**. Participant arc remains UNADJUDICATED; no participant
overlay is created. R4.4 consumer remains absent. The strict one-mother constraint
applies to adjudicated strict hypotactic daughters; its macro counterpart remains
separate. Paratactic candidates need no fabricated mother.

## Validation and release (items 37–41)

Syntax checks PASS. Stage tests: **76 PASS**. Full regression:
**1,860 PASS / failures 0 / errors 0 / skipped 0** (1,784 previous + 76 new).
Synthetic S1–S5/M1–M7 PASS, including no forced root, explicit dependency,
multiple peers, insufficient frame evidence and forbidden source controls.
Every one of 53 computed run gates has a negative test, including manifest
tampering; the two external release gates also have failure tests.
Final synthetic and both real runs: **53 run gates PASS**.
External regression and deterministic rerun gates: **2 PASS**.

The final sequence was syntax/stage tests/full regression, synthetic S then M,
real S/freeze then independent M/freeze, leakage/post-blind/cross-layer/review,
independent complete real rerun, manifests and manual candidate inspection.
Final packages A/B are byte-identical, with 538 members. ZIP CRC and duplicate-name
checks pass. All 25 recursive 99-manifests and both independent blind manifests
verify; root-level blind table views match their authoritative blind directories.
The post-blind status fix does not change either blind frozen artifact set.
Earlier `jin09_real_final_*` diagnostic artifacts are superseded by `release_*`.
Termux runner is supplied but no empirical Termux result is claimed.

Release A: `results/jin09_real_release_20260924_a_results.zip`.
Independent B: `results/jin09_real_release_20260924_b_results.zip`.
SHA256 (both): **`80821a089d3097721e80eecdf85272640e77b3e19b0206e3066f82de6c088b06`**.
Synthetic: `results/jin09_synthetic_release_20260924_a_results.zip`.
Regression receipt: `results/jin09_regression_20260924_final.json`.
Independent verification: `results/jin09_release_verification_20260924_final.json`.
These local artifacts are intentionally excluded from Git.

S manifest SHA256: `86756308dac88f8c92dddddcc39de46a91c7c141df3eed0c8a1820ea476c125f`.
M manifest SHA256: `66ae87b083d6b845438544555814e47f3229671caf9a7c1c35ab25cd61121ac7`.

## Human-review questions (items 42–43)

All questions below are UNREVIEWED; answer/evidence-sufficiency fields are blank.

| question_id | scope_id | question |
| --- | --- | --- |
| S-Q1 | ROOT:STRICT | Strict clause hierarchy: one top-level candidate or multiple? |
| S-Q2 | ROOT:STRICT | If multiple, is there top-level paratactic relation evidence? |
| S-Q3 | ROOT:STRICT | Is Job 1:1 only BOOK_SCOPE_INITIAL or a linguistically supported unique strict-root candidate? |
| S-Q4 | ROOT:STRICT | Define strict root within Job book scope and leave external canonical context separate? |
| S-Q5 | ROOT:STRICT | If evidence is insufficient, defer a unique strict root? |
| M-Q1 | ROOT:MACRO | Does macro configuration support one root, multiple peers or a higher frame? |
| M-Q2 | ROOT:MACRO | Is Job 1:1 a macro-root candidate or only an opening-unit onset? |
| M-Q3 | ROOT:MACRO | What top-level relation candidates do the major transitions/onsets including 3:1, 32:1/32:2, 38:1 and 42:7 form? |
| M-Q4 | ROOT:MACRO | Does raw opening/final narrative correspondence support a higher whole-book frame? |
| M-Q5 | ROOT:MACRO | Does present evidence require selecting a unique macro root? |

## Readiness and remaining work (item 44)

**READY_FOR_TOP_LEVEL_HUMAN_ADJUDICATION**. Review S and M independently, including
the meaning of the raw initial unknown domain, partial opening/final correspondence,
paratactic plurality and insufficient evidence. No unique root is required by this
technical result. BOOK_SCOPE_ROOT concerns the present Job scope only;
CORPUS_ABSOLUTE_ROOT remains OUT_OF_SCOPE_FUTURE_RESEARCH. Remaining strict/macro
scope review and later migration dry-run/consumer decisions remain separate.

## Files changed

`.gitattributes`; `config/jin_top_level_rules.json`;
`config/r4_4_contract_jin_0_9_job.json`; `docs/HANDOFF.md`;
`docs/R4_4_CONTRACT_JIN_0_9_RESEARCHER_SOURCE.txt`;
`docs/R4_4_CONTRACT_JIN_0_9_SPEC.md`;
`docs/R4_4_CONTRACT_JIN_0_9_VALIDATION_REPORT.md`;
`docs/README_MILAL_R4_4_CONTRACT_JIN_0_9.md`;
`scripts/run_milal_jin_top_level_windows.ps1`;
`scripts/run_milal_jin_top_level_termux.sh`;
`src/milal_jin_top_level_common.py`;
`src/milal_jin_strict_top_level_audit.py`;
`src/milal_jin_macro_top_level_audit.py`;
`src/milal_jin_top_level_postblind.py`;
`src/milal_jin_top_level_pipeline.py`;
`src/milal_jin_top_level_synthetic.py`;
`tests/test_r4_4_contract_jin_0_9.py`.

## Appendix S — all distinct strict top-level references

No reference is a ranking or selected root. Exact clause/atom IDs and overlapping
kinds remain in the candidate CSV and human-review packet.

| Job chapter | Verses |
| --- | --- |
| 1 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 |
| 2 | 1, 2, 3, 4, 6, 7, 9, 10, 11, 13 |
| 3 | 1, 2, 3, 6, 10, 11, 13, 21, 22, 23, 24, 25, 26 |
| 4 | 1, 2, 5, 6, 12, 13, 20 |
| 5 | 3, 4, 8, 14, 15, 16, 17 |
| 6 | 1, 3, 17, 20, 21, 22, 28 |
| 7 | 5, 6, 7, 9, 15, 16, 18, 19, 20, 21 |
| 8 | 1, 2, 4, 5, 6, 12, 16 |
| 9 | 1, 2, 4, 5, 16, 20, 21, 31 |
| 10 | 8, 9, 22 |
| 11 | 1, 2, 3, 4, 11, 12 |
| 12 | 1, 2, 4, 18, 19, 22, 23, 24, 25 |
| 13 | 1, 2, 19 |
| 14 | 2, 3, 10, 11, 12, 14, 16, 17, 18, 20, 21 |
| 15 | 1, 2, 27, 28, 29, 32 |
| 16 | 1, 2, 7, 8, 9, 12, 13, 15 |
| 17 | 7, 8 |
| 18 | 1, 2 |
| 19 | 1, 2, 9, 10, 12, 13, 18, 19, 20, 21, 24, 25 |
| 20 | 1, 2, 7, 15, 25 |
| 21 | 1, 2, 14, 21, 30 |
| 22 | 1, 2, 29 |
| 23 | 1, 2, 7, 13, 14 |
| 24 | 14, 20 |
| 25 | 1, 2 |
| 26 | 1, 2 |
| 27 | 1, 2, 20 |
| 28 | 27, 28 |
| 29 | 1, 2, 11, 12, 14, 17, 18, 22 |
| 30 | 1, 9, 10, 11, 12, 13, 16, 17, 19, 20, 21, 24, 26, 27, 31 |
| 31 | 1, 5, 6, 15, 16, 27, 28, 34 |
| 32 | 1, 2, 5, 6, 7 |
| 33 | 22, 23, 24, 26, 27 |
| 34 | 1, 2, 20, 24, 25 |
| 35 | 1, 2, 15 |
| 36 | 1, 2, 7, 8, 9, 10, 11, 32, 33 |
| 37 | 8, 10, 21, 22 |
| 38 | 1, 2, 7, 8, 9, 11 |
| 39 | 15, 16 |
| 40 | 1, 2, 3, 4, 6, 7 |
| 42 | 1, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17 |

## Appendix M — all distinct macro top-level references

| Job chapter | Verses |
| --- | --- |
| 1 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 |
| 2 | 1, 2, 3, 4, 6, 7, 9, 10, 11, 13 |
| 3 | 2, 10, 21, 23, 24, 25, 26 |
| 4 | 1, 5, 12 |
| 5 | 3, 15, 16 |
| 6 | 1, 20, 21 |
| 7 | 5, 6, 9, 15, 18, 20 |
| 8 | 1, 4 |
| 9 | 1, 4, 16, 20 |
| 10 | 8, 22 |
| 11 | 1, 3, 4, 11 |
| 12 | 1, 4, 18, 22, 23, 24, 25 |
| 13 | 1 |
| 14 | 10, 17, 20 |
| 15 | 1, 27, 28 |
| 16 | 1, 8, 9, 12 |
| 17 | 7 |
| 18 | 1 |
| 19 | 1, 9, 10, 12, 18, 20 |
| 20 | 1, 15, 25 |
| 21 | 1, 14 |
| 22 | 1, 29 |
| 23 | 1, 13 |
| 24 | 20 |
| 25 | 1 |
| 26 | 1 |
| 27 | 1 |
| 28 | 28 |
| 29 | 1, 11, 14, 17, 18 |
| 30 | 9, 11, 12, 19, 20, 26, 31 |
| 31 | 5, 15, 27, 34 |
| 32 | 1, 2, 5, 6 |
| 33 | 22, 24, 26, 27 |
| 34 | 1, 24 |
| 35 | 1 |
| 36 | 1, 7, 9, 10, 32 |
| 37 | 8, 21 |
| 38 | 1, 7, 9, 11 |
| 39 | 15 |
| 40 | 1, 3, 6 |
| 42 | 1, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17 |
