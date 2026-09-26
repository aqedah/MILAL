# MFR.0.2R-H0.1 validation report

Status: TECHNICALLY_VALIDATED — full regression and independent A/B release passed.

## Baseline and scope

Start local HEAD, fetched origin/main and actual remote main all matched
`64250a992fb4fa1035a0b1687df7eef326dcb40c`. Repository C:\MILAL, branch main,
upstream origin/main at https://github.com/aqedah/MILAL.git.
The four pre-existing untracked PDFs are preserved. No reset, rollback, branch
switch or reconstruction occurred. All 564 frozen file pins remain unchanged.

H0.1 is a decision sieve over the existing qualified universe, not relation
discovery or human adjudication. Every prior analytical core remains frozen.
The exact Q1.3 feasibility oracle and Q1.6R process-role ontology are reused.

## Frozen integrity

Raw universe 1,049,504; qualified relations 273; mother/parallel/overlay 203/70/0;
composite spans 275; reference witnesses 5,854; historical human judgments 13.
273/273 qualified outcomes receive exactly one disposition. Zero new relations,
zero deletions, zero new human judgments, zero canonical mother/hierarchy selection.
All unresolved source records remain traceable to their frozen identities.

## Target status — all 2,938 targets

| Classification | Count |
|---|---:|
| DEFERRED_COMPATIBILITY_UNRESOLVED | 0 |
| EVIDENCE_GAP_NOT_STRUCTURAL_DECISION | 224 |
| EXPLICIT_NEGATIVE_CONFLICT | 0 |
| GLOBAL_CONSTRAINT_DECISION | 0 |
| NO_QUALIFIED_RELATION | 2709 |
| QUALIFIED_COMPATIBLE_SET | 0 |
| QUALIFIED_NONCOMPETING_CANDIDATE | 4 |
| TRUE_DECISION_PIVOT | 1 |
| UNRESOLVED_REVIEW_STATUS | 0 |

Target status and structural_status are intentionally separate. Researcher S8
requires evidence-gap classification for a single candidate with unresolved identity.
Accordingly a noncompeting qualified target with unresolved evidence has primary
EVIDENCE_GAP_NOT_STRUCTURAL_DECISION, while the underlying single/compatible-set
classification remains recorded. Targets without a qualified relation remain
NO_QUALIFIED_RELATION; their evidence gaps are still preserved separately.

Underlying structural counts: 198 single noncompeting candidates, 30 compatible
multi-relation targets, one pivot, 2,709 without qualified relations. A single
noncompeting candidate means no current structural choice, not acceptance.

## Relation disposition — 273/273 accounted for

| Classification | Count |
|---|---:|
| ADDITIVE_PARALLEL | 70 |
| COMPATIBILITY_DEFERRED | 0 |
| CORROBORATED_DUPLICATE_PATH | 0 |
| EXPLICIT_CONFLICT | 0 |
| NONCOMPETING_MOTHER_CANDIDATE | 179 |
| ORTHOGONAL_COMPATIBLE | 22 |
| OTHER_EXPLAINED_STATUS | 0 |
| PART_OF_TRUE_DECISION | 2 |

## Actual minimal structural constraints

| Classification | Count |
|---|---:|
| EXPLICIT_NEGATIVE_CONFLICT | 0 |
| MOTHER_COMPETITION | 1 |
| PARALLEL_HIERARCHY_INCOMPATIBILITY_CANDIDATE | 0 |
| SB12_HARD_CONFLICT | 0 |
| STRICT_MOTHER_CYCLE | 0 |
| TRUE_PAIR_RELATION_CONFLICT | 0 |

The global symbolic search checked three conflict-directed pools and did not
enumerate the Cartesian product of undecided edges. The full unordered pair audit
contains 37,128 comparisons. Higher-order conflicts, if present, are represented
by minimal forbidden sets rather than reduced to pairwise guesses. Components
connect only relations in actual hard conflicts, never mere shared targets,
mechanisms, configuration families, domains or historical variant components.
A global decision can affect a target without two local positive alternatives;
such a target is GLOBAL_CONSTRAINT_DECISION rather than a local true pivot.
This distinction is covered by dedicated cycle and mixed-component tests.

Strict cycles, same-pair conflicts, parallel/hierarchy incompatibility, explicit
SB12 constraints and explicit negative outcomes have positive/negative synthetic
coverage even though the actual Job universe contains only the mother competition.
No compatibility-model defect was found. Unknown canonical level or shared mother
is not treated as a hard conflict.

## Human review and post-freeze diagnostic

Decision components: 1. True pivot targets: 1. Human review items: 1.
No adjudication or selection was made. Only after generic outputs were hashed,
the Job 37:20 control was inspected:

- Target clause `500065`, clause atom `590199`, כִּ֣י יְבֻלָּֽע׃.
- Qualified mother alternatives: source `500062` and source `500064`.
- Exact incompatibility: two distinct selected mothers consume the same mother
  slot (`MULTIPLE_SELECTED_MOTHERS`). Each singleton assignment is coherent;
  their union is not. Omission elsewhere remains UNDECIDED.
- Source `500062` is supported through SB03 reference paths; source `500064`
  through SB01/SB02 paths. All paths and shared raw identities remain in the
  machine packet, with Q1.6R roles displayed separately.
- Other-pair bindings sharing nearby clauses are explicitly context-only; they
  are not presented as direct support for an alternative.
- Q1.6 unique-evidence ablation records retain the `500064` alternative when
  either SB01-unique or SB02-unique facts are removed. Other mechanism rows do
  not list these two outcomes as lost or changed. This is unique-raw-fact ablation,
  not disabling every path of a mechanism; shared facts remain preserved.
- Unresolved references/domains remain unresolved and are not turned into an
  invented NO_RELATION. No mother is recommended, ranked, accepted or selected.

The human packet contains both alternatives, grammar, Hebrew/node identity,
primary and contextual evidence, time/location, participant/reference, lexical
FORM, pre-relation evidence, exact constraints and shared-raw warnings. Complete
raw/process records are in packet_evidence_catalog.json and the CSV. Only
review_status=UNREVIEWED is prefilled; other canonical human fields are blank.

## Separate evidence gaps — source records, not distinct decisions

| Classification | Count |
|---|---:|
| DOMAIN_VISIBILITY | 3880 |
| LEXICAL_ANAPHORA | 2943 |
| LOCATION_INTERPRETATION | 58 |
| REFERENCE_IDENTITY | 2911 |
| TIME_INTERPRETATION | 69 |
| VALENCY_GOVERNANCE_NOT_ESTABLISHED | 39 |

9,900 gap records preserve distinct evidence types and may refer to the same
textual locus. Their current absence of an additional qualified commitment is
separate from unresolved possible future effect. No missing relation is invented.

Nondecision QA: 271 qualified relations, 59 observed groups, 59 deterministic
representatives. All group members remain machine-readable. Grouping uses relation
type, binding mode, primary mechanism, recorded configuration family/signature and
status. Minimum exact relation ID is an ordering convention, not a preference.
No QA representative enters the structural human-review universe.

## Historical comparison after freeze

Verified historical H0: raw 1,049,504; relation-eligible 95,929; review-required
targets 2,719/2,938. Current qualified relations: 273; H0.1 review items: 1.
The old H0 archive is read only after the current audit freeze and has no
classification effect. Progression is SEARCH CANDIDATE → SOURCE-BOUND QUALIFIED
RELATION → COMPATIBILITY → TRUE STRUCTURAL DECISION. This is not an independently
validated accuracy improvement.

## Validation

Syntax: 8 files. Focused tests: 71 PASS. Synthetic: 14/14 PASS.
Negative mutations: 36/36 PASS. Human-facing synthetic and real packets inspected.
Full regression: 3,050 PASS in 758.631 seconds; failures/errors/skips: 0/0/0.
Final computed release gates: 36/36 PASS in both independent runs.
Validated code fingerprint:
`0b7da20951c3f255db27bf308cbf104265ca7037358fa73f4ac71874c2898ddb`.

ZIP A: `D:\MILAL_runs\mfr02r_h01_20260926\release_a_results.zip`.
ZIP B: `F:\MILAL_runs\mfr02r_h01_20260926\release_b_results.zip`.
Both exist; both contain 30 members; CRC and manifest validation PASS for both.
Independent manifests and ZIP bytes are identical. Shared SHA256:
`e07a3a6cc90674acf1e408372f7faf43b302e9d389c013e3609b4f71f9ad04c8`.

Human packet: `D:\MILAL_runs\mfr02r_h01_20260926\release_a\13_h01_review_packets.md`.
Machine packet: `D:\MILAL_runs\mfr02r_h01_20260926\release_a\12_h01_review_packets.csv`.
Evidence catalog: `D:\MILAL_runs\mfr02r_h01_20260926\release_a\packet_evidence_catalog.json`.
The independent B directory contains the same packet bytes.

Regression log: `D:\MILAL_runs\mfr02r_h01_20260926\regression_verified.log`.
The regression helper's historical baseline field is not the H0.1 start commit;
H0.1 start identity is separately verified above and in stage metadata.

## Readiness

Final release result: READY_FOR_MFR_0_2R_H0_2.
H0.2 must use only the H0.1 packets, requires explicit researcher authorization,
and has not started. Technical validation does not adjudicate or accept relations.

## Files changed

- `config/mfr_0_2r_h01_job.json`
- `src/milal_h01_model.py`, `src/milal_h01_evidence.py`,
  `src/milal_h01_pipeline.py`, `src/milal_h01_controls.py`,
  `src/milal_h01_validation.py`, `src/milal_h01_synthetic.py`,
  `src/milal_h01_runner.py`
- `tests/test_milal_h01.py`
- `docs/MFR_0_2R_H01_SPEC.md`, `docs/MFR_0_2R_H01_RESEARCHER_SOURCE.txt`,
  `docs/README_MILAL_MFR_0_2R_H01.md`, this validation report, `docs/HANDOFF.md`
- `.gitattributes` for exact attachment bytes.

Generated releases, logs, ZIPs, PDFs, inputs and corpus data remain local-only.
