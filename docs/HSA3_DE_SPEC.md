# HSA3-D/E — Elihu Global Seam Human Adjudication

Baseline: `60b6a5a0cdb2e8e8dde55ae2210774f58c84eb24`.
Authority: [exact researcher request](HSA3_DE_RESEARCHER_SOURCE.txt) and
[canonical human input](../config/hsa3_de_human_decisions.json).
Only D/E are adjudicated. A–C/F–G remain unadjudicated. R4.4 is not authorized.

## Frozen input and execution

The configured ANA.0.3 ZIP is required:
`results/hsa3_ana_0_3_human_freeze_final_20260923_a_results.zip`, SHA256
`460b8f82764ea3c382c97ac6d382855a8a264272e7f152e60d133179f29c9ee1`.
Verify its 112 members, CRC, manifests, stage/status, gates, human decisions,
59 historical judgments, 57 unresolved rows and seven original cases. Retain
all input files byte-for-byte beneath `history/ana_0_3/`. There is no new BHSA
scan or ANA reanalysis. Synthetic fixtures use existing synthetic builders only.

Pin 116 prior source/config/test/document files. HANDOFF and .gitattributes are
operational continuity files, not analytical cores. The new source request uses
a narrow Git byte-preservation attribute. Canonical JSON stays LF. Verify the
baseline Git object and that it is an ancestor of current HEAD, allowing later
reproduction after the new commit without hard-coding the eventual output HEAD.

## Existing-schema audit and action accounting

The frozen graph already contains:

- `H:HSA018 → H:HSA018 TRANSITION_COMPONENT`.
- `H:HSA019 → ELIHU_SPEECH_SEQUENCE NARRATIVE_INTRODUCTION`, edge
  `E:440d08279bd9b22af859`.
- Four GROUP_MEMBER_OF edges for HSA020–HSA023.
- Twelve directed SAME_LEVEL_SIBLING records for those four onsets.

These 18 existing canonical edge rows are CONFIRMED_EXISTING with their original
IDs and records. They are not 18 new judgments. Historical reciprocal sibling
records are preserved rather than collapsed or recreated. 37:24 already has
the SPEECH_UNIT_END node/judgment, but no group-terminal edge to the Elihu group.
Therefore the supplied `H:HSA024 → ELIHU_SPEECH_SEQUENCE
TERMINATES_ENCLOSING_GROUP` is a new positive relation in
HIGHER_ORDER_TERMINAL_EFFECT. It is not direct local closure or textual parentage.

Four explicit human negative constraints are supplied:

| Source | Target | Relation | Dimension |
| --- | --- | --- | --- |
| H:HSA018 (32:1) | H:HSA019 (32:2–5) | NO_DIRECT_PARENTAGE | TEXTUAL_PARENTAGE |
| H:HSA018 | ELIHU_SPEECH_SEQUENCE | NO_DIRECT_PARENTAGE | TEXTUAL_PARENTAGE |
| H:HSA024 (37:24) | H:HSA025 (38:1) | NO_DIRECT_PARENTAGE | TEXTUAL_PARENTAGE |
| H:HSA024 | H:HSA025 | NO_DIRECT_RESPONSE_ANTECEDENT | RESPONSE_RELATION |

For NO_DIRECT_PARENTAGE the source is excluded as the target's direct parent;
this is not the child→parent direction of a CHILD_OF edge. No 32:6 CHILD_OF 32:1
or 32:2 is created. No CHILD_OF, CONTINUES_WITHIN or RESPONSE_TO is generated
between 37:24 and 38:1. Negative authority is the explicit researcher judgment,
not an automatic inference from missing evidence and not a denial of all
rhetorical/discourse relationships.

No extra composition group is needed. The existing ELIHU_SPEECH_SEQUENCE remains
NON_TEXTUAL_GROUP. Its supplied 32:6–37:24 scope is new human scope metadata,
not a rewrite of the historical node's blank computed coverage fields. The
existing NARRATIVE_INTRODUCTION edge carries unit-level introduction/composition;
it does not make verse 32:6 a child of verse 32:2.

Counts are computed after exact-ID schema audit, never fixed as implementation
semantics. This baseline yields 2 seam decisions, 1 created positive relation,
18 confirmed-existing edge records, 4 new negative constraints and 0
NO_ACTION_DUPLICATE rows. The latter is a redundant-request count; confirmed
existing actions are not double-counted as duplicate-skipped rows. The planner
recognizes the explicitly authorized INTRODUCES_AND_ENCLOSES alias for
NARRATIVE_INTRODUCTION at identical endpoint IDs, never fuzzy text/span identity.
If a terminal relation already exists it is confirmed, not recreated; repeated
requests are NO_ACTION_DUPLICATE. Ambiguous multiple existing equivalents stop.

## Separate dimensions and preserved decisions

32:1's transition function and Q2 overlay differ from the Elihu composition.
TEXTUAL HIERARCHY, COMPOSITION/GROUPING, TRANSITION, OVERLAY/RESPONSIO and
RESPONSE RELATION remain separate. Adjacency, speaker succession, nearest
opening, theme or formula length alone never assign parentage.

Q2/Q4/Q5 remain accepted; Q3 remains UNRESOLVED/HUMAN_DEFERRED, with its positive
lexical/participant evidence retained only as an evidence dependency. No causal
or fulfillment claim follows from SEAM_E. Q4 and Q5 are not deleted by the
negative constraints. No direct hierarchy does not mean no discourse relation.
The 31:40 three HSA2-F relations, 38:1/40:6 accepted same-level major onsets and
40:1 CHILD_OF 38:1 remain unchanged. No formula-length rule replaces their
accepted contextual/distributional basis.

Apply only the actual frozen 24-code registry. Functional distinction, response
insufficiency and overlay/parentage distinction are methodological notes where
no exact code exists. E-FUNCTIONAL-EQUIVALENCE applies to independently accepted
peer onsets, not to treating the transition and introduction as equivalent.
No global scoring, registry mutation or automatically completed review field.

## Unresolved crosswalk and remaining packet

All 57 historical rows ask for an exact direct textual parent; grouping,
introduction, closure and response were explicitly separate claims in their
original reason field. No supplied decision assigns that parent. Consequently
none of these rows is marked RESOLVED_BY_SEAM_D/E merely because the seam
decision is frozen. The crosswalk retains every original record, row hash,
primary seam owner and before/after parent status.

Nine nodes directly participate in the D/E actions: eight D-owned nodes plus
38:1, which is shared E evidence but remains F-owned. These nine are
REMAINS_UNRESOLVED; 48 are NOT_APPLICABLE_TO_THIS_SEAM_DECISION. All 57 exact
parent questions remain unresolved, including all 49 primary A–C/F–G rows.
These are overlapping accounting views, not totals to add together.

The next packet presents only A/B/C/F/G questions, exact primary/participating
unresolved IDs, evidence locators, accepted positive/negative constraints,
criteria dimensions and blank canonical researcher fields. D/E are labeled
FROZEN. Shared-node D/E constraints are context only, not adjudication of F.
Historical PREP cases and review fields remain byte-identical.

## Outputs and validation

Required outputs 01–10, 90/99 follow the request. Additional 11 source facts,
12 remaining cases, 13 new positive relations, 14 canonical decisions and 15
source request preserve exact provenance. Relations retain source evidence IDs;
existing edge/member/row hashes and endpoint source facts are independently
resolvable. All old raw evidence remains in nested history.

Run syntax, new tests, all 866 prior regressions, self-test and synthetic packet
inspection before the authorized actual frozen-artifact run. Each computed gate
has a negative test, including corruption of the output manifest. Compare two
independent processes' ZIP bytes and members, in addition to independent model
builds. Only after PASS inspect/stage intended files, commit and push to verified
origin/main. Results, logs, ZIPs and data remain ignored. Do not start R4.4.
