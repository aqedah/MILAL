# MFR.0.2R-Q1.1 validation report

Baseline: `039284206418253d42f0998a6af05382dde511c8`.
Scope: diagnostic/methodological source-binding coverage review only.
H0.1 is not started. Previous analytical cores remain frozen.

Authority: [Q1.1 request](MFR_0_2R_Q11_RESEARCHER_SOURCE.txt).
Method contract: [Q1.1 specification](MFR_0_2R_Q11_SPEC.md).
Execution: [runner instructions](README_MILAL_MFR_0_2R_Q11.md).

## Methodological provenance

- [Q1 researcher contract](MFR_0_2R_Q1_RESEARCHER_SOURCE.txt), sections 4–5:
  SB01–SB12 intent categories and direct/unit/configuration binding examples.
  Sections 8–9 require independent correspondence and positive textual-line
  evidence; section 10 separates participant recurrence from active continuation.
- [Frozen Q1 specification](MFR_0_2R_Q1_SPEC.md) and
  [source adapter](../src/milal_q1_binding.py), `SourceIndex.native`,
  `native_configuration`, `dependency_paths`, `bindings`: actual operational
  criteria, explicitly GENERALIZED_FOR_MILAL.
- [Frozen grammar](../config/clause_relation_grammar_v1.json): exact original
  admitting rules and their scholarly source references. Q1.1 does not rewrite
  Jin/Walton rules or attribute its implementation schema to their original terms.
- [Frozen larger-unit implementation](../src/milal_mfr02r_layers.py),
  `unit_candidates`, `symbolic_unit_references`, `expand_unit_reference`:
  conditional membership, exact factorization and Bosman §9.1 p204 attribution.
  This is a generalized candidate representation, not resolved referential identity.

These sources support investigating principled mechanisms. They do not supply
a completed executable contract for the eight unsupported categories. The
three options are proposals for source review, not new scholarly acceptance.

## Baseline and repository

`git fetch origin` succeeded. Local HEAD and fetched origin/main both matched
the required baseline. Tracked files were clean before work; four existing
research PDFs remained untracked and untouched. The diagnostic configuration
pins 473 frozen files, including the 12 newly frozen Q1 files.

## Implemented diagnostic separation

The new modules independently load and verify the frozen baseline, decompose
SB06 predicates on existing units, and inspect external controls after the blind
Job diagnostic freeze. They do not call qualification, rule matching, fixture
candidate generation, new graph analysis, or structural-outcome creation.
The Bosman graph is reconstructed solely from existing fixture relation records.

Five Numbers alternatives across four pairs and two factorized Bosman reference
rows are selected for post-freeze diagnosis. SB01–SB12 coverage distinguishes
category intent, implemented adapters, and actual witnesses. Every external
pair retains its original record and Q1 record in the detailed coverage table.

## Sensitivity interpretation

The denominator is the complete original relation-pair population, separately
for Job and each existing fixture scope. Five predicates are evaluated on
unchanged Q1 units. NP lexeme/position predicates expose implications of the
full signature check. Their conjunction is verified against frozen SB06 on
every diagnostic pair. Sole and joint failures are not counts of hypothetically
recovered relations. No noncontiguous replacement units are generated.

The `missing_known_controls` field in the scope summary refers specifically to
the five designated Numbers alternatives. All other frozen fixture proposals,
including every non-retained relation, remain individually available in
`external_pair_coverage_details.csv`; these are not automatically designated
positive human judgments. B/C/D diagnostic categories may overlap.

## Validation and release

Syntax parsing passed. Focused tests: 42 passed, zero failures/errors/skips.
Synthetic output was inspected: signature failed alone once and jointly with
the non-speech predicate once; no relation was produced. Independent synthetic
CSV bytes matched. All 23 required gates have negative evidence mutations, with
additional predicate, policy and frozen-adapter conjunction tests.

Final full regression: **2,562 passed**, zero failures/errors/skips, 840.545 seconds.
Receipt: `D:\MILAL_runs\mfr02r_q1_1_20260926\regression_corrected.json` and `.log`.
Current synthetic receipt: `C:\MILAL\results\q11_synthetic_02\receipt.json`.
All 36 synthetic semantic/policy/gate checks and the synthetic byte comparison passed.

Two independent real diagnostic runs passed. **23/23 gates** passed after
independent file comparison. All 33 ZIP members and 32 manifest entries verified;
final A/B file bytes and ZIP bytes are identical. CRCs and all member hashes pass.
The final human-facing findings, exact-control tables and baseline/gates were inspected.

Final outputs:

- `D:\MILAL_runs\mfr02r_q1_1_20260926\release_a_final`
- `F:\MILAL_runs\mfr02r_q1_1_20260926\release_b_final`
- Both directory names plus `_results.zip`
- ZIP SHA256: `2925a1f241638e057cb919d2b8c5acae61995c91df31c32ef627d892210d0be5`
- Verification: `D:\MILAL_runs\mfr02r_q1_1_20260926\release_a_final_verification.json`
- Code/config/test fingerprint: `8348adebdfb532edf78090e36149240a9c6f37a7d38384689c3ee8e67aaaf65f`

Both executions independently verified Q1 ZIP SHA256
`6398abb8113e6674d0697771acabe0f19e84ddaf3f927f8c761d86a29b3ab16f`
and MFR.0.2R ZIP SHA256
`93ff58ba3f1498e5e93a4aaf23e15ceb777d54ef2704edf3c15fcffad9f05b7d`,
including CRC, full member manifest and extracted file hashes. All 473 frozen
repository pins and 24 BHSA fixture/native feature hashes remain unchanged.

The first real attempt stopped at the baseline count check: the new Q1.1 loader
had counted all 2,938 target rows in each competition table rather than only
`competition=true` rows. Q1 itself was correct and unchanged. The diagnostic
loader now checks the flag against distinct alternatives and counts 0 mother /
2 parallel competitions. Three focused regression tests cover this error and
invalid/duplicate competition records. The initial `release_a`/`release_b`
directories are failed attempts, not canonical releases. The earlier 2,559-test
receipt is superseded by the final 2,562-test receipt above.

## Frozen baseline reproduction

Raw 1,049,504; original/H0-eligible relation pairs 95,929; qualified 185 = 173
direct + 12 configuration + 0 unit-mediated; structural outcome groups 185;
pivot targets exactly 497596 and 497608; mother/parallel competitions 0/2.
All 13 human decision objects/hashes match. New judgments, canonical mothers,
canonical hierarchies and newly qualified relations: zero. Q1's original warning
and readiness remain QUALIFICATION_OVERRESTRICTIVE and
QUALIFICATION_REQUIRES_METHODOLOGICAL_REVIEW. No lower analytical core changed.

## SB01–SB12 result and fixed-unit sensitivity

Implemented adapters: SB01, SB03, SB04, SB06. Job witness counts are respectively
176, 0, 1, 12. The remaining eight IDs (SB02, SB05, SB07, SB08, SB09, SB10, SB11,
SB12) remain unsupported intent categories. Q1.1 does not implement them or
presume they would qualify a control. Witness counts are not qualified-pair counts.

Job fixed-unit population: all 95,929 original relation pairs.

| Predicate | Fails alone | Fails with another predicate |
|---|---:|---:|
| Contiguous native multi-clause units | 7 | 59,597 |
| Corresponding lexical NP | 0 | 91,134 |
| Corresponding grammatical position | 0 | 94,236 |
| Non-speech predicate | 52 | 14,031 |
| Identical full signature | 568 | 95,242 |

The complete 25-row scope/restriction matrix is in output 05. Each row retains
failure-pattern counts and all pair vectors remain available. These figures
describe the five-predicate conjunction only, not the full qualification pipeline
or recovered relations. NP/position constraints overlap signature equality.
Exact identity, native-root contiguity and non-speech predicates are conservative
Q1 operational choices, not established universal necessary conditions.

## Readiness and remaining methodological question

**NEEDS_ADDITIONAL_SOURCE_REVIEW**. H0.1 is not started and is not declared ready.
The three unselected options in output 08 are: independently anchored
configuration correspondence (SB06/SB11), independent reference/containing-unit
witnesses (SB02/SB03/SB10), and positive global constraints distinct from mere
compatibility (SB12). The SB04 active-context limitation also requires source
review. Any implementation change requires a separately approved operational
contract and blind validation; no control was adjudicated here.

## Repository files

Added: `src/milal_q11_diagnostic.py`, `src/milal_q11_controls.py`,
`src/milal_q11_runner.py`, `src/milal_q11_validation.py`,
`src/milal_q11_synthetic.py`, `tests/test_mfr_0_2r_q11.py`,
`config/mfr_0_2r_q11_review.json`, `docs/MFR_0_2R_Q11_RESEARCHER_SOURCE.txt`,
`docs/MFR_0_2R_Q11_SPEC.md`, `docs/README_MILAL_MFR_0_2R_Q11.md`, and this report.
Updated: `.gitattributes` for exact researcher-source bytes and `docs/HANDOFF.md`
for current stage/next question. Results, ZIPs, logs, BHSA and the four existing
research PDFs are not staged or committed.

## Exact larger-unit distinction

The frozen factorized objects are both assignment-dependent, but their available
native support is different. `UC-504907 → 504911` expands through antecedent
`504908` and conditional edge `P504907-504908-HYPOTACTIC`; Q1 has no witness for
that edge. Antecedent/target share the participant lexeme `XWMH/`. This establishes
lexical recurrence, not a resolved anaphoric reference or containing-unit claim.

`UC-504910 → 504924` expands through antecedent `504911` and conditional edge
`P504910-504911-HYPOTACTIC`. Unlike the first case, Q1 retains that intermediate
edge with SB01: exact native `dependent_node=504911`, `head_node=504910`,
`rela=Adju`. This is independent database support for that intermediate
dependency, not a canonical textual mother. The larger-unit target `504924`
shares `BT/` and `YJWN==/` with antecedent `504911`, but its `REFERENCE.mentions`
list is empty. It supplies neither a resolved target-to-antecedent reference nor
the target-to-word native edge required by the implemented SB03 subset.

Consequently, the second case must not be described as lacking all independent
path evidence. Its remaining gap is directed reference/binding and independently
justified textual-unit interpretation; lexical recurrence alone does not close
that gap. Both referential identities remain UNRESOLVED. Exact source words,
phrases, references and native annotations are preserved in the Lamentations
source-evidence table, and the intermediate Q1 statuses are in the complete
external pair audit. No new mechanism or authoritative relation is inferred.

## Exact Numbers hypotactic distinction

`P443836-443840 — HYPOTACTIC` was originally admitted by `RG-C01` and `W-H01`.
The source/target are Num 26:1/26:3. Their participant configuration recurs with
different grammatical roles; the frozen Q1 adapter requires more than that
recurrence. There is no direct SB01 native edge or SB03 target-to-word path
witness. SB04 also fails: this pair is not adjacent and has no required native
dependency, so an active participant context is not witnessed by that adapter.

The absence of an SB04 witness is an implementation-scope limitation, not proof
that historical participant continuity is impossible. A corpus-wide extension
would need independent evidence of the active/source-containing unit. Merely
whitelisting this pair or upgrading repeated participant lexemes to identity is
illegitimate. SB02/SB05/SB10 remain category intents, not demonstrated solutions
for this hypotactic alternative. The general participant/reference witness
question must be resolved before any separately approved mechanism change.

The four PARATACTIC alternatives were all admitted by the `W-P01` prior. They
fail the following fixed-unit SB06 predicates:

| Pair | Failed predicates |
|---|---|
| P443836-443840 | NP grammatical position; non-speech predicate; full signature |
| P443836-443956 | Non-speech predicate; full signature |
| P443837-443841 | All five |
| P443837-443957 | All five |

The first two compare two-clause speech-opening configurations. The latter two
compare the `לאמר` clauses: source `443837` has Q1 members `[443837,443838]`,
whereas the target configurations are `[443841]` and `[443957]`. Q1 compares
configuration openings and explicitly does not infer constituent sibling
relations. A principled correspondence mechanism would therefore also need to
specify corresponding positions inside independently evidenced configurations;
it cannot simply copy a parent relation to its constituents. No such recovery
or qualification is performed here.

## External coverage units

| Scope | Fixture clauses / pairs | Original relation pairs / alternatives | Qualified pairs / alternatives | Missing HYP / PARA alternatives |
|---|---:|---:|---:|---:|
| Pentateuch | 115 / 3,650 | 594 / 740 | 27 / 27 | 395 / 318 |
| Qohelet | 19 / 83 | 9 / 9 | 3 / 3 | 5 / 1 |
| Lamentations | 22 / 52 | 9 / 11 | 2 / 2 | 2 / 7 |
| Isaiah | 25 / 49 | 16 / 18 | 5 / 5 | 9 / 4 |

There are 778 original alternatives and 37 retained alternatives, hence 741
non-retained alternatives across 591 entirely non-retained relation pairs.
There are no partially retained multi-relation pairs in these frozen fixtures.
All retained alternatives are supported by SB01; the external witness inventory
also has one dependent SB04 context witness. SB06 contributes no external
configuration witness. Absence of a qualified alternative is not NO_RELATION.

The 3,206 other raw fixture pairs had no original relation alternative to
retain. The A category marks this pipeline-level fact; it is not a new scholarly
rejection. B/C/D classifications concern evidence availability and conservative
implementation, may overlap, and do not create positive or negative judgments.
