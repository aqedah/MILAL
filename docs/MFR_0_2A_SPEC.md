# MFR.0.2A — First marker-first human relation freeze

Authority: [exact researcher instruction](MFR_0_2A_RESEARCHER_SOURCE.txt).
Baseline: `9c005d862452709b4b53cf80de6185fd081d825b` on main.
This phase records the researcher's 13 supplied H1 judgments as a new append-only
human layer. It does not discover, regroup, or adjudicate any additional case.
The MFR.0.1, MFR.0.1a and MFR.0.1b analytical layers remain frozen.

## Decision semantics and authority

The decision unit is CONFIGURATION_RELATION_CASE. Five PARATACTIC decisions accept
direct configuration-level relations. Seven FORMAL_ONLY decisions preserve
linguistically meaningful correspondence without asserting a direct hierarchy
relation. One INSUFFICIENT decision leaves hierarchy unsupported by the present
evidence; it does not reject relations in every other dimension.

An accepted configuration relation is not expanded into constituent sibling edges.
All underlying raw pairs remain evidence memberships, including pairs whose frozen
machine candidate labels differ from the researcher decision. There are no new
HYPOTACTIC or EMBEDDING decisions, direct mothers, root, tree, or R4.4 consumer.

`config/mfr_0_2a_human_decisions.json` transcribes the supplied decisions and seven
calibration principles. Authority bytes, source sections, excerpts, excerpt hashes,
verbatim formal labels and explicit inherited rationale references are retained.
Decision flags are the one-hot encoding of the supplied primary decision; they
are not computed from evidence. Fields not supplied, such as configuration_validity
for some isolated-form cases, remain blank rather than receiving invented review.
No timing or other unsupplied human review fields are filled.

CFG000227's analytical formal_relationship is REPEATED_TRANSITION_CONFIGURATION,
following the researcher's observable-form naming rule. The original supplied
REPEATED_MESSENGER_TRANSITION_CONFIGURATION remains in provenance. This records no
literary scene label or participant identity resolution. CFG000281/282/333 retain
their explicit reference to CFG000231's rationale.

## Frozen source linkage and isolation

The exact MFR.0.1b ZIP, embedded MFR.0.1a ZIP and embedded MFR.0.1 ZIP are verified
by SHA256, CRC, member universe and manifest hashes. Repository baseline ancestry
and all 405 immutable baseline file hashes are checked. HANDOFF and gitattributes
are excluded from immutable pins because they carry stage transitions and exact
source-file encoding exceptions.

A projection contains only H1/R1/C1 memberships and the 13 H1 evidence attachments.
The decision serializer runs in a separate process. A file-read allowlist permits
only this projection and the supplied decisions; historical imports and all other
file reads are blocked. It writes decisions, provenance, raw-pair crosswalk,
calibrations, deferred dimensions, accepted configuration decisions and an explicit
representation inventory, then hashes those seven files. It does not read R1/C1
contents until after the human freeze. A receipt records the logical read set.

Historical comparison may start only after that manifest verifies. Comparison is
read-only and cannot alter the frozen decision bytes. The full upstream ZIP and
unchanged H1 attachments remain in the release, so no omitted queue or displayed
summary deletes earlier raw evidence.

## Evidence and deferred dimensions

Only existing independently usable formal/sequence evidence IDs are admitted as
computational support links for PARATACTIC rationales. Every other evidence row
remains in the attachment. Cessation roots and their coverage/nested derivatives
cannot enter independent hierarchy support. A support link documents provenance;
the researcher's supplied judgment remains the authority for acceptance.

Resumption is UNREVIEWED_SEPARATE_DIMENSION; cases with existing resumption
memberships are DEFERRED_TO_MFR_0_2B. Closure is independently unreviewed; H1 cases
containing cessation, coverage or nested evidence defer that dimension to MFR.0.2C.
This includes evidence that was archived from the default closure queue. Absence
of an H1 evidence facet is reported as such, not as a negative human decision.

Future scope files preserve the complete frozen R1 and C1 sets without reducing
them by H1 outcomes. They add only blank future decisions, deferred review status
and an exact H1 decision cross-reference where present. They perform no B/C review.

## Post-freeze historical comparison

The pinned JIN.0.8 release contains the JIN.0.7 historical-relation crosswalk with
HSA relation IDs, explicit BHSA2021 clause endpoints, later JIN review status and
complete nested provenance. The selected member and its whole archive are pinned.
The unchanged selected table is included in this release. This comparison is scoped
to that 111-relation inventory, not a claim to have adjudicated every historical
dimension or literary judgment. Eight historical records with UNRESOLVED endpoints
remain explicitly listed as non-joinable; their nodes are not inferred.

Clause IDs, not Hebrew text or references, drive comparison. Both endpoint sets
must match exactly, or one must match exactly while the other MFR endpoint is an
explicit subset of the historical endpoint. The second case reports scope overlap,
never object identity. Mere intersections or two partial endpoints do not join.
Original directed IDs remain separate even when two historical rows express the
same symmetric relation in opposite directions.

Same relation with exact endpoints is AGREES_WITH_HISTORICAL; same relation with
the permitted partial endpoint match is PARTIALLY_AGREES. Exact-scope FORMAL_ONLY
or INSUFFICIENT versus historical hierarchy is MFR_MORE_CONSERVATIVE. Incompatible
asserted hierarchy types at exact scope are CONFLICTS. A distinct historical
relation subtype outside the MFR decision vocabulary is HISTORICAL_MORE_SPECIFIC.
No eligible join, or incompatible dimensions at only partial scope, produces
NO_HISTORICAL_COMPARISON. This status is not historical rejection or a new judgment.

For the observed control, CFG000028 has four target clauses while the historical
2:1 record has five: PARTIALLY_AGREES. CFG001981's 27:1/29:1 endpoint sets agree
exactly. These observations are post-freeze results, never rules selecting decisions.

## Validation and release

All requested gate definitions have negative mutations. Tests cover authority,
exact universe/distribution, non-expansion, lossless evidence memberships,
append-only behavior, deferred dimensions, independent support and read isolation.
Synthetic execution precedes real execution. Full regression must pass with zero
skips; independent empirical A/B ZIPs, freeze hashes and final manifests must match.
The final independent receipt checks package and regression gates without making a
self-referential claim inside the ZIP that is being compared.

Success: MFR_H1_CONFIGURATION_ADJUDICATED and
READY_FOR_MFR_0_2B_RESUMPTION_ADJUDICATION. Whole-book hierarchy/tree assembly and
R4.4 implementation readiness are not implied. Subsequent human batches must use
new decision IDs and preserve earlier serialized decisions.
