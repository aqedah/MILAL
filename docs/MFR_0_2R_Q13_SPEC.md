# MFR.0.2R-Q1.3 — Orthogonal relation compatibility

Authority: [exact researcher request](MFR_0_2R_Q13_RESEARCHER_SOURCE.txt).
Baseline: `f47756caf72cf1aa171568e6c1a5efa0623753fd`.
The executable schema is **GENERALIZED_FOR_MILAL**. This stage corrects assignment
semantics; it does not introduce scholarly source claims or new source bindings.

## Input and frozen scope

The immediate input is the verified Q1.2 result ZIP with SHA256
`3a3118876006a9eaf7ba5f79b435ab5521cd6d4087711def8854512815816770`.
The extracted manifest must match the archive, every physical member must hash
correctly, and ZIP CRC verification must pass. Q1.2's 195 qualified relations,
195 outcome groups, all provenance paths, 1,049,504 raw crosswalk records and
13 historical human decisions remain unchanged. The prior seven pivot records
are preserved as historical output, not overwritten by the new interpretation.

All 499 frozen repository files in `config/mfr_0_2r_q13_job.json` must match their
pins, and the baseline must be an ancestor of HEAD. No Q1.2 profile, reference,
qualification, unit-boundary or configuration algorithm is called to regenerate
evidence. Q1.3 consumes existing outcome identities and profile clause IDs.
Primary analysis is Job only. No external-book candidate generation or corpus
search runs in this stage. The four user PDFs remain external, untracked files.

Large raw/reference tables are preserved in the mandatory verified upstream
archive, identified member by member in `source_preservation_receipt.json`.
Small qualified/outcome/pivot/human tables are also copied byte for byte into
the new release. This avoids duplication without discarding source evidence.

## Dimensions and compatibility

| Dimension | Selection semantics |
| --- | --- |
| MOTHER_RELATION_DIMENSION | Zero or one **distinct** HYPOTACTIC mother per daughter |
| PARALLEL_RELATION_DIMENSION | Zero or many PARATACTIC peers |
| NON_HIERARCHICAL_TYPED_RELATION_DIMENSION | Explicitly typed overlays; no mother slot |

Explicit constrained EXCLUDED outcomes are supported separately when their
positive outcome ID and constraint provenance are supplied. No such outcome is
inferred from nonselection. Unknown relation schemas fail explicitly.

Different mothers for the same target conflict. Different parallel peers are
additive unless a recorded independent constraint proves otherwise. Mother plus
parallel is potentially compatible. Same unordered pair HYPOTACTIC/PARATACTIC
conflicts under the current single relation-layer contract. Reverse-direction
pairs are checked without creating inverse source outcomes.

The compatibility matrix covers pairs of original outcomes for the same original
target. Statuses are COMPATIBLE, MUTUALLY_EXCLUSIVE or CONDITIONALLY_COMPATIBLE;
the final parallel level/mother constraint can remain UNRESOLVED even when a
bare pair is jointly representable. Unknown final placement is not a conflict.
This is exposed separately as `level_compatibility_classification =
UNRESOLVED_COMPATIBILITY`. A proven conflict under an explicit shared context
is recorded as `conditional_context_constraint = INCOMPATIBLE`; it does not
claim that the bare pair is mutually exclusive without that context.
PARATACTIC imposes an equal-level constraint **within a selected hypothetical
assignment**; it neither assigns canonical level nor propagates a shared mother.

The existing structural validator checks single mother, strict/equal-level
contradiction, and cycles after parallel contraction. Existing SB12 hard
constraints restrict qualified outcomes only. Its soft competing-chain notices
are retained as provenance and never converted into hard prohibitions. No
SB12-created positive relation is permitted.

## Coherent assignment and pivot proof

Each target retains symbolic mother options, parallel options, overlays and
explicit exclusions. An explicit feasibility witness contains:

- `mother_assignment`: zero or one distinct mother;
- `parallel_peer_assignments`: zero or many peers;
- `overlay_relations` and `explicit_exclusions`;
- `unresolved_relations`: local outcomes not selected;
- `supporting_selected_context`: selected outcomes of other targets;
- exact selected outcome IDs, blank canonical fields and `accepted=false`.

**UNSELECTED = UNDECIDED**, never NO_RELATION. M versus M+P, or P1 versus P2,
does not establish a target pivot just because the selected sets differ.

A true target pivot requires two positively distinct target commitments and
two coherent assignments whose union violates a documented constraint. Both
target commitments must be essential to a minimal incompatible union. The proof
records both assignments, common positive context, violations and provenance.
This distinguishes a global variant difference elsewhere from a target pivot.
Rule/evidence provenance differences for an identical commitment corroborate
that commitment and do not create pivots.

For global constraints, conflict-directed search minimizes an incompatible pool.
If that core excludes a requested commitment, it branches by removing a member
of the irrelevant core. It does not enumerate the Cartesian product of undecided
choices. Search is exact for the monotone constraints used here; inherently
difficult conflict sets can still require many branches. No arbitrary search cap
or candidate deletion is introduced. A pair can coexist in isolation yet have
a conditional conflict under an explicitly recorded common positive context.

Only TRUE_MOTHER_COMPETITION, TRUE_PAIR_RELATION_CONFLICT or
GLOBAL_STRUCTURAL_CONFLICT with such a proof can require pivot review.
CORROBORATED_RELATIONS, ADDITIVE_PARALLEL_RELATIONS, ORTHOGONAL_RELATIONS and
unresolved level compatibility alone cannot. The global audit also records
whole-pool feasibility and, if necessary, one minimal global conflict. This
sample core is not claimed to enumerate every possible global conflict.

## Outputs and post-freeze controls

Required outputs 01–16 and 90/99 follow the researcher's filenames. Tables 03,
04, 07 and 10 include every source target, including targets with no qualified
relation. Table 10 exposes NON_PIVOT as well as true pivots. Empty competition
tables retain headers. Additional JSON files retain symbolic components,
original SB12 constraints, source receipts, blind hashes and gate evidence.

The blind model is frozen before loading old pivot labels, human judgments or
diagnostic control IDs. Table 11 reaudits exactly the prior seven targets from
configuration. Report 12 checks configured Job 2:1 identities for representability:
497625 with mother 497624 and peer 497540, and 497623 with peers 497569/497538.
These are post-freeze checks, never logic branches or new human acceptance.
The multiple-peer and mother-plus-parallel gates also validate these actual
diagnostic assignments against the model, in addition to their synthetic cases.

Metrics distinguish all parallel-bearing targets with unresolved final level
from multi-relation targets with unresolved compatibility. Reported true pivot
counts are calculated without any expected final-count assertion.

## Validation and progression

Run syntax validation, focused tests, the synthetic self-test and output inspection,
then full regression with zero failures/errors/skips. Do not change source,
configuration or tests during the full regression. Real execution requires
current matching fingerprints for full regression and synthetic validation.
Independent runs must produce identical manifests and ZIP bytes; both ZIPs are
verified. The 23 requested gates plus positive-proof and source-binding guards
are computed from actual evidence and each has a negative mutation test.
Synthetic S1–S10, overlays, explicit exclusions, global-versus-target differences,
cycles, reversed pairs and conflict-search distractors are exercised.

All gates passing permits **READY_FOR_MFR_0_2R_Q1_4** as technical readiness.
It does not establish a canonical hierarchy, accept a structural assignment,
resolve the Q1.2 reference gaps, or fix the 27:1–29:1 unit-boundary limitation.
Q1.4 must not start without separate authorization.
