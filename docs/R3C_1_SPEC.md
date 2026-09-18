# MILAL R3c.1 — Human Review Unit Decomposition

Active specification, 2026-09-18. This stage follows the accepted real
R3c.0.2 Termux/Windows cross-validation; it does not redefine either frozen layer.

## Method and population

R3b.3 navigation containers and lineage IDs stay frozen. R3c.0.2 analytical
source and historical result files stay unchanged. No R4 or real BHSA execution
is part of development acceptance for this stage.

The population contains exactly one `REPEATED_BUNDLE_UNIT` per source R3b.3
bundle and one `SINGLETON_OUTCOME_UNIT` per canonical R3c.0.2 singleton outcome.
Unit IDs reuse `BUNDLE:<bundle_id>`, `G6:<review_item_id>` and `EVENT:<source_key>`.
Neither containers, lineages, boundaries nor extensions are population units.
No semantic, rhetorical, discourse, function or fork object is introduced.

Repeated units retain membership, lineage, parent, ancestry, depth, source
levels, sequence length, occurrence count, exemplar and direct child metadata.
The declared occurrence count must match the complete source occurrence table.
No missing required source field may be inferred. R3c.1 adds required membership
columns `occurrence_count`, `sequence_length`, `levels_present`, `lowest_level`,
and `highest_level` to the unchanged R3c.0.2 source requirements.

Singleton folding delegates to frozen `build_outcomes`: only
`mapped_g6_singleton_review_item_id == review_item_id` establishes mapped
equivalence. MAPPED, EVENT_ONLY and G6_ONLY survive with every source record,
branch, parent, span and surface. Text/span/signature similarity never folds
objects. Conflicting source identities fail. S02135 remains the fixed Job
control, expressed in configuration rather than universal corpus semantics.

## Pilot

Exactly six of each:

1. HIGH_OCCURRENCE_BUNDLE
2. LOW_OCCURRENCE_BUNDLE
3. RANDOM_BUNDLE
4. SINGLETON_OUTCOME
5. BOUNDARY_CONTROL

HIGH uses occurrence count, direct repeated child count, explicit singleton
refinement-event branch count, and refinement depth descending; bundle ID is
the final ascending tie-breaker. LOW uses ascending numeric measures and ID
after excluding HIGH. These are lexicographic orders, never weighted scores.
Explicit singleton branch count means source refinement-event rows attached to
the immediate parent; G6 link rows do not count those events again. All event
and link branches remain available in relations and provenance.

RANDOM samples six from the remaining ID-sorted bundles with the configured
seed. A separate random generator using that same recorded seed samples five
canonical singleton IDs after the fixed singleton control. Bundle strata are
disjoint; singleton and boundary evidence may overlap other cases.

Job panels remain 31:40, 32:1, 32:2, 37:24, 38:1 and 42:7. Each is a complete
control panel with all matching occurrences/outcomes, not a population unit.
No single representative pattern replaces a panel.

## Evidence and relations

Selected bundles emit every source occurrence without truncation. A bundle
case targets only that bundle; its descendants' occurrences/outcomes are not
recursively expanded. Immediate parent metadata, ancestry references, direct
repeated children and explicit singleton attachments belong in the separate
relation table. Every packet relation has a machine-readable row.

Singleton cases emit every source span and preserve every branch. Boundary
panels emit every matching repeated occurrence and all spans of every singleton
outcome with any matching span. Population/provenance preserve unselected
objects; context loading is limited to selected/panel evidence spans and panels.

Reuse R3c.0.2 span-aware context: full covering verses, previous/next in-book
verse, all word-overlapping clauses and sentences, cross-chapter spans and
nonwrapping book edges. Exact source surface is distinct from covering context.
Do not infer speaker or macro labels.

Extensions remain separate, with EXEMPLAR_ONLY or UNRESOLVED coverage. Bundle
overlays are incident to the target bundle; singleton overlays are incident to
its explicit parent bundles. Boundary overlays use exemplar-start matches plus
unresolved incident relations. No entire lineage is expanded to gather overlays.
No missing exemplar match establishes absence of an extension; location-level
evidence would be required before claiming OCCURRENCE_VERIFIED.

## Forms and provenance

Import the single canonical `REVIEW_FIELDS` from R3c.0.2. Forms appear on cases;
only review_status starts UNREVIEWED. Time is diagnostic, with no labor-hour
extrapolation. No semantic/function columns are added to generated review views.
Original source snapshots are preserved verbatim, including historical columns.

Provenance retains input archive hash/name, member path, one-based data row,
content-derived source key, source role and original row JSON. Content hashes
identify records; they are not singleton-equivalence rules. Exact duplicate
event rows retain separate ordinals. Reordering input rows preserves selections,
population identities and rendered evidence; actual provenance row numbers
necessarily follow the original source order.

## Outputs and validation

The fourteen output files are documented in [the README](README_MILAL_R3c_1.md).
Computed gates reconstruct source expectations rather than testing constants:

- SOURCE_NAVIGATION_AND_COUNTS_VALID
- REVIEW_UNIT_POPULATION_COMPLETE
- REVIEW_UNIT_IDS_UNIQUE
- NO_CONTAINER_AS_REVIEW_TARGET
- REPEATED_UNIT_LINEAGE_MATCHES_SOURCE
- REPEATED_UNIT_PARENT_MATCHES_SOURCE
- REPEATED_METADATA_COMPLETE
- ALL_SELECTED_BUNDLE_OCCURRENCES_EMITTED
- NO_TARGET_OCCURRENCE_TRUNCATION
- SELECTED_SINGLETON_SPANS_COMPLETE
- ALL_SELECTED_CONTEXTS_RESOLVED
- SINGLETON_IDENTITY_FOLDING_VALID
- SINGLETON_PARENT_LINEAGE_MATCHES
- S02135_REGRESSION_VALID (the configured control on non-Job synthetic data)
- BOUNDARY_CONTROLS_COMPLETE
- NO_EXTENSION_OBJECT_IN_CORE
- EXTENSION_RELATIONS_OVERLAY_ONLY
- REVIEW_FIELDS_BLANK_EXCEPT_STATUS
- NO_AUTOMATIC_FUNCTION_LABELS
- PILOT_CASE_COUNTS_VALID
- PILOT_SELECTIONS_DISJOINT_WHERE_REQUIRED
- FIXED_SEED_SELECTION_REPRODUCIBLE
- RELATION_CONTEXT_COMPLETE
- PROVENANCE_COMPLETE

Every gate has a negative mutation test. Input schema/count/graph failures stop
model construction with explicit diagnostics. Development acceptance requires
syntax validation, all existing and new regression tests, synthetic self-test,
and human-facing packet inspection. Windows is primary for the subsequent
separately authorized empirical run. Synthetic success does not accept R3c.1
empirically or authorize R4.
