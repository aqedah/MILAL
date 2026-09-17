# MILAL R3c.0.2 — Human Review Case Pilot Specification

## Status

Active implementation specification.

## Fixed implementation decisions (2026-09-17)

The following user-approved decisions supersede broader wording below:

- Exactly 30 cases: six of each required type. HIGH uses bundle count, distinct
  singleton outcome count, depth descending, then ID ascending. LOW uses the
  corresponding ascending order after HIGH exclusion. RANDOM uses a recorded
  seed and the remaining ID-sorted pool.
- Fold only explicit mapped G6 IDs. Preserve every mapped source row and branch.
  Unmapped events become EVENT_ONLY; unpaired G6 items become G6_ONLY. Repeated
  bundle identities are not merged by shared text/span/signature.
- The Job pilot configuration requires S02135 / Job 31:40 as an independent
  mapped singleton control. Select five remaining outcomes reproducibly.
- Conflicting lineage/atom identity, incompatible mapped sequence length and
  non-overlapping mapped spans fail. Overlapping source spans stay separate.
- Preserve source ZIP hashes, member paths, data-row identities and referenced
  row snapshots, not entire input ZIPs or copies of all source tables.
- The current extension adapter has exemplar starts only. Output coverage is
  EXEMPLAR_ONLY or UNRESOLVED; never claim exhaustive boundary extension coverage.
- Exact source surface is separate from complete covering-verse context. Context
  includes overlapping clauses/sentences; neighbors stay inside the configured book.
- `REVIEW_FIELDS` in the new implementation drives all generated review schemas.

See [R3c.0.2 README](README_MILAL_R3c_0_2.md) for CLI, files, validation and limits.

## Goal

Create human-review cases from the frozen R3b.3 navigation layer without changing the underlying lineage model or reducing candidates merely for convenience.

The output must make it possible to answer:

> Is the current MILAL evidence sufficient for a human researcher to describe the observable textual behavior of this case without reopening multiple raw source files?

## Required case types

Generate exactly five case types with six cases each by default:

- `HIGH_COMPLEXITY_CONTAINER`
- `LOW_COMPLEXITY_CONTAINER`
- `RANDOM_CONTAINER`
- `SINGLETON_ITEM`
- `BOUNDARY_CONTROL`

Default total: 30.

Make case counts configurable if reasonable, but preserve these defaults.

## Canonical review schema

Define once and reuse everywhere:

```python
REVIEW_FIELDS = (
    "review_status",
    "observable_behavior",
    "recurring_context",
    "exceptions",
    "sufficient_context",
    "additional_information_needed",
    "review_time_seconds",
    "reviewer_notes",
)
```

Do not duplicate this literal schema elsewhere.

Default values:

- `review_status = UNREVIEWED`
- all remaining fields blank.

No automatic functional/rhetorical labels.

## Container cases

### HIGH_COMPLEXITY_CONTAINER

Select six hardest/most complex navigation containers using explicit structural measures (e.g. member counts / singleton outcomes / depth). This is a stress test, not a representative sample.

Document the deterministic selection rule.

### LOW_COMPLEXITY_CONTAINER

Select six structurally simple containers, excluding cases already selected elsewhere.

### RANDOM_CONTAINER

Select six containers with a fixed random seed after excluding already selected containers.

Record the seed in run metadata and output.

Do not use these six cases to extrapolate a total review-time estimate for all containers.

## Singleton cases

Create a human-facing `SINGLETON_OUTCOME` model that folds:

- the R3b.3 singleton refinement event, and
- the corresponding G6 singleton review item

when they refer to the same terminal outcome.

The folded review object must retain both source/provenance references.

At minimum expose:

- singleton outcome ID / G6 item ID,
- lineage ID,
- parent bundle ID,
- refinement transition,
- ref span,
- surface text,
- ancestry path to the parent/root,
- BHSA span-aware context,
- both provenance records.

Select six `SINGLETON_ITEM` cases as independent human review cases.

One regression/control target should ensure Job 31:40 `תמו דברי איוב` remains independently visible when present in input data. Do not hard-code its identity as a universal corpus rule.

## Boundary control cases

Create six panel-level human review cases for:

- Job 31:40
- Job 32:1
- Job 32:2
- Job 37:24
- Job 38:1
- Job 42:7

Each panel contains all relevant evidence patterns for the verse/span:

- repeated bundle occurrences,
- folded singleton outcomes,
- genealogy/branch membership,
- sequence-extension relations as a separate overlay.

The review fields apply to the **entire panel**.

The question is not "what function does one bundle have?" but whether the present evidence is sufficient to analyze the structural transition point.

## Human-facing evidence pattern folding

Avoid repeated display of the same underlying evidence merely because it exists in multiple provenance tables.

Where repeated-bundle / singleton-event / G6 records describe one human-facing pattern/outcome, emit one review object with provenance children rather than multiple visually duplicated objects.

Do not delete raw provenance tables or prevent reconstruction.

## Genealogy rendering

Human-facing Markdown must render lineage relationships hierarchically using `parent_bundle_id` rather than a flat depth-sorted list.

Requirements:

- roots visible,
- children nested,
- singleton outcomes attached to the relevant parent branch,
- ancestry paths recoverable,
- cycles detected and rejected.

## Span-aware Text-Fabric context

For every case/pattern span:

- resolve full start/end verse span,
- previous verse before span,
- full Hebrew text across the span,
- next verse after span,
- clauses overlapping/covering span,
- sentences overlapping/covering span.

Do not silently collapse a multi-verse pattern to `ref_start` only.

## Core invariants / gates

Implement executable checks:

### 1. CORE_LINEAGE_MATCHES_MEMBERSHIP
Every repeated bundle review object uses the lineage assigned by `02_lineage_bundle_members.csv`.

### 2. SINGLETON_PARENT_LINEAGE_MATCHES
Every non-orphan singleton outcome's parent bundle resolves to the same lineage as the singleton linkage/event evidence.

### 3. NO_EXTENSION_OBJECT_IN_CORE
No sequence-extension-only relation appears inside the core genealogy review-object collections.

### 4. EXTENSION_RELATIONS_OVERLAY_ONLY
All extension relations appear only in dedicated overlay outputs/views.

### Additional required gates

- source review-container IDs are nonblank and unique;
- no automatic function/rhetorical fields are populated;
- all review fields begin blank except `review_status=UNREVIEWED`;
- all six boundary controls produce review cases;
- all six singleton cases resolve their provenance;
- genealogy has no parent-cycle within sampled/rendered branches;
- span-aware TF context resolves for all six boundary controls on real runs.

No literal `True` gates.

## Outputs

Use clear versioned filenames. At minimum produce:

- review case registry (30 rows),
- container-case evidence,
- singleton-outcome registry/evidence,
- boundary-control evidence,
- separate sequence-extension overlay,
- span-aware TF context inventory,
- human-facing Markdown review packet,
- gate results,
- run metadata / sampling seed,
- manifest checksums,
- method note / README.

Exact filenames may be improved by the implementation, but README and runner must agree with them.

## Validation

Self-test must include synthetic examples for:

- large branching genealogy,
- folded singleton event + G6 item,
- orphan singleton,
- multi-verse span context,
- multi-pattern boundary verse,
- sequence-extension kept separate,
- fixed-seed random sampling,
- duplicate/blank container ID failure,
- lineage mismatch failure,
- genealogy cycle failure.

Do not claim R3c.0.2 empirically passes until the Termux/BHSA real-data result is inspected.
