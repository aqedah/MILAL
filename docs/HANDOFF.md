# MILAL Development Handoff

## R3c.0.2 implementation update — 2026-09-17

The new implementation is in `src/milal_r3c_0_2_reviewability.py`; R3c.0.1 is
preserved. Job controls are in `config/r3c_0_2_job_pilot.json`. The new Termux
runner resolves `../src/` and creates fresh result paths without deleting runs.
See `docs/README_MILAL_R3c_0_2.md` for outputs and validation commands.

Real R3b.2/R3b.3 input ZIPs and BHSA are not bundled in this development workspace.
Synthetic validation and the checked-in R3c.0.1 control regression are development
checks only. Empirical acceptance still requires the real Termux/BHSA 2021 result
ZIP and human-facing packet inspection. Do not advance to R4 on synthetic results.

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

## 10. Development workflow

- This repository is the coding workspace.
- Codex implements and tests code here.
- Termux performs the final real BHSA execution.
- The result ZIP is then examined for methodological correctness before moving to R4.

Do not move to R4 merely because unit/self-tests pass. R3c.0.2 must first be run against the real Job/BHSA data and the human-facing output must be inspected.
