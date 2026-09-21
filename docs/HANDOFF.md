# MILAL Development Handoff

## Current task — MR1 provenance/reproduction, 2026-09-21

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
