# R4.4-CONTRACT.0.1 — Layered Input Contract Audit

CONTRACT_PROPOSAL. Baseline `113a1f3fe13ff9698a97f82f3f1a53b41b4f3b21`.
Authority: the exact researcher request in `docs/R4_4_CONTRACT_0_1_RESEARCHER_SOURCE.txt`.
This stage specifies an input proposal and tests compatibility of existing frozen
records. It creates no R4.4 analytical consumer, final research registry, output
contract, visualization, new judgment, parent, composition or overlay relation.

## Source contract and execution scope

Consume only `results/hsa3_layer_0_2_real_final_20260924_a_results.zip`, SHA256
`0754eb4c3c22e17ff59627440f8ca5aeb92ee20ecb6a7cdc197240850bb31983`.
Verify CRC, 237 members, all manifests, stage/mode/gates and 169 frozen repository
file pins. Preserve all input bytes under `history/hsa3_layer_0_2/`. Real mode does
not replay any analytical stage or load BHSA. Synthetic mode explicitly builds
frozen synthetic fixtures and cannot load a real archive.

Baseline receipt validates the exact specified ancestor so the audit remains
reproducible after its own commit. Initial HEAD equality is a separate session
preflight. This contract is not human approved: Q1–Q7 stay UNREVIEWED with blank
answers. The current request authorizes audit implementation, synthetic/real dry
runs, independent rerun and commit/push of contract docs/proposal/test files only.

## Canonical authority and coverage

Use the 18 explicit source members recorded in the job configuration. Canonical
nodes and seven relation files are from nested LAYER.0.1. Also retain its group
view, unresolved/deferred questions, role crosswalk, frozen seams, historical
proposals and presentation matrix. Outer LAYER.0.2 provides human necessity,
proposal crosswalk and final necessity state, plus its unadjudicated future note.
Provenance is embedded in every source record and linked through exact receipts.
All older artifacts remain byte-identical; they are not counted again as active
canonical records. Canonical group view repeats node information intentionally
and is identified as a view, not an additional graph node.

Historical observation → explicit later adjudication → explicit later necessity
is a provenance chain, not a single global priority that overwrites other claims.
Only the same question/dimension can be superseded. Preserve the whole original
record even when a later decision governs its active representation requirement.
See the precedence and architecture documents included in the audit output.

## Node proposal

Reuse exact node_id and existing node_kind vocabulary: TEXTUAL_NODE,
TRANSITION_ANCHOR, ROLE_ALIAS, COMPOSITION_GROUP, TECHNICAL_ROOT and
SOURCE_EVIDENCE_ANCHOR. Do not rename every textual locus TEXTUAL_UNIT: some are
internal/ending/no-boundary anchors, and evidence anchors are not promoted units.
canonical_node_id uses only the explicit canonical_textual_node crosswalk;
otherwise it is the same existing ID. This does not rewrite source relationships.

Proposed fields: node_id, canonical_node_id, node_kind, textuality,
reference_start, reference_end, anchor_ref, span_type, structural_function,
speaker, participant_role, source_stage, human_status, frozen_status,
historical_parent_status, parentage_necessity_status,
additional_parentage_review_required, direct_parent_edge_resolved,
direct_parent_ids, technical_only, qualified_spans, provenance_ids,
field_presence and original_record.

textuality distinguishes TEXTUAL/NON_TEXTUAL/TECHNICAL. A ROLE_ALIAS can describe
a textual locus while still not being a second unit. Historical reference fields
are not computed coverage. Preserve later accepted annotations and supplied
group spans separately; an explicit group scope is not textual containment.
Groups without a supplied scope use NO_SPAN_RECORDED; no interval is inferred
from member ordering or neighboring onsets.
Optional missing fields carry NOT_RECORDED presence metadata, not invented
speaker/participant identity or an overloaded NULL status. A missing source
schema invariant is an error; an explicitly optional unrecorded value is not.

## Relation proposal

Fields: relation_id, source_id, target_id, endpoint_form, source_ref, target_ref,
scope_ref, relation_layer, relation_type, polarity, directionality, status,
human_supplied, automatic_resolution, source_stage, evidence_ids, provenance_ids,
limitations, historical_status, original_dimension, membership_position,
graph_scope and original_record.

Retain the established COMPOSITION_GROUPING name and all seven source layers:
TEXTUAL_HIERARCHY, TEXTUAL_SAME_LEVEL, COMPOSITION_GROUPING, TRANSITION,
OVERLAY_RESPONSIO, NEGATIVE_CONSTRAINT, TECHNICAL_NAVIGATION. The authoritative
member and explicit stored layer must agree; never guess layer from type alone.
Keep original_dimension even where TRANSITION originated as TRANSITION_OVERLAY.
SAME_LEVEL_COMPOSITION_PEERS is not SAME_LEVEL_SIBLING. membership_position
preserves order without inventing an ORDERED_MEMBER edge. CONTINUES_WITHIN and
DIRECT_LOCAL_CLOSURE remain typed placement relations, not direct parent claims.

An endpoint union is essential: NODE_IDS, REFERENCE_PAIR and REFERENCE_SCOPE.
ANA-H2/H4 have native reference pairs; ANA-H5 has a native scope only. Neither
can require guessed node identity or a fabricated binary endpoint. Unrecognized
forms are AMBIGUOUS_SCHEMA and block readiness. Deferred ANA-Q3 remains a
candidate state envelope, not a newly accepted relation. Polarity distinguishes
explicit negatives, positive assertions and technical navigation. Stored
orientation and original direction remain; no inverse/transitive edge is added.

## Status and provenance proposal

Use separate adjudication_status, human_decision_status, historical_status,
necessity_status, review_status, frozen_status and future_scope_status axes.
Preserve source tokens such as ACCEPTED_SOURCE and FROZEN_SOURCE verbatim.
Keep the specific DIRECT_TEXTUAL_PARENT_NOT_REQUIRED wording for H:HSA012.
HISTORICAL or SUPERSEDED_BY_LATER_ADJUDICATION describes a scoped history link,
not erasure of the old value. The 57 rows must simultaneously express historical
UNRESOLVED, false additional review and false parent-edge resolution.

Each mapping has SOURCE_RECORD → CONTRACT_NODE / CONTRACT_RELATION or an
explicit state/view extension, with exact member, raw row, identity key/value,
row hash, member hash and outer artifact hash. Keep full original_record, all
upstream provenance and qualified annotations. Source-named evidence and
limitation fields retain JSON paths; no flattening across scopes. Human judgment
and addendum IDs remain in the original chain. Technical-only objects can have
no human judgment IDs; preserve that fact instead of inventing an author.

## Fixtures and mapping statuses

Seven source-grounded fixtures cover Job 2:11, 31:40, 32:1, Elihu, 37:24/38:1,
YHWH response complexes and final Job 42 narrative. Exact IDs/reference fields
are test selectors only, not detection or parent-assignment rules. Preserve all
simultaneous relations, source dimensions, explicit negatives and no-boundary
decisions. 42:10/12 remain evidence anchors, not promoted textual units.

LOSSLESS: existing record fully represented with its source envelope.
LOSSLESS_WITH_EXTENSION: typed node/status or native endpoint extension required
by the proposal, with every original field retained. AMBIGUOUS_SCHEMA: source
shape cannot yet be assigned safely. INCOMPATIBLE: required facts cannot coexist
under the proposal. NOT_APPLICABLE: preserved presentation-only matrix rows;
these are not dropped and are not converted into graph relations.

Current source records must all be mapped, including supporting state/view rows.
The mapping CSV includes the proposal projection and original record; it is an
audit artifact, never an accepted R4.4 registry. Report all status counts,
including zero incompatible/ambiguous counts. Readiness is exactly one token:
READY_FOR_HUMAN_CONTRACT_REVIEW or BLOCKED_BY_SCHEMA_ISSUES. Never declare
READY_FOR_IMPLEMENTATION. The future participant arc remains a note; schema
extensibility is tested without creating even a hypothetical research relation.

## Validation and output scope

Generate the requested 01–15/90/99 audit files, plus architecture report, exact
request and proposal JSON. No separate mapped-node/edge production exports.
Validate syntax, stage tests, full regression skip-zero, computed gates with
negative mutations, human-facing synthetic packet, frozen-real dry-run and
independent byte-identical rerun. Full regression and independent ZIP equality
are external release gates, not claims derived from a stage exit. Test harness
lives under tests; no src R4.4 consumer or runner is added.
