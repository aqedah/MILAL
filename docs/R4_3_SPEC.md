# R4.3 — Human-Grounded Whole-Book Hierarchy Scaffold

Authorized on 2026-09-22 from `f41095917d1deaa718df553f4919e41969601ce7`:
implement, test, inspect synthetic output, audit accepted-real inputs, independently
rerun, document, commit and push. This is the first **partial whole-book scaffold**,
not a completed Job hierarchy or authority to resolve new human questions.

## Sources and precedence

HSA1 (31), HSA2 (25) and HSA2-F (3) remain frozen: all **59 original records** are
retained, including original HSA2 UNRESOLVED candidate fields. The active view uses
HSA2-F closure decisions, then HSA2, HSA1, and accepted analytical context. Precedence
changes the derived view; it never rewrites a source registry. No review field is
automatically completed and no new human adjudication is created.

The accepted HSA1 and HSA2-F ZIPs are SHA256-pinned; the latter contains all original
HSA2 files. The frozen HSA2-F adapter verifies the HSA2 ZIP and its seven upstream
archives (MR1/R3c.3/PROV1/HR1/R4.0/R4.1/R4.2). Verify CRC, exact member manifests,
accepted status/gates and human-file byte fidelity. Preserve complete HSA1/HSA2-F
archive members under `history/`, including all source/context evidence and nested
manifests. No new BHSA extraction or marker computation takes place.

`config/r4_3_job.json` pins 75 baseline source/config/test/human/specification files.
It also declares four explicit record mappings: HSA2-INITIAL→HSA013,
HSA2-JOB-27→HSA015, HSA2-JOB-29→HSA016, HSA2-END-31→HSA017. These named restatements
share exact source identities (respectively P:853609, csf:39, csf:41 and the exact
31:40 closure/CASE025), not just similar text or location. This is a derived-view
mapping, not deletion of historical records. All original fields and IDs appear in
the accounting table; 3:1 retains both its HSA1 paragraph function and HSA2 speech
function. Final decisions reference the same ending node and separate target edges.

## Node and relation semantics

Supported node types: TECHNICAL_ROOT, TEXTUAL_ANCHOR, SPEECH_UNIT, SCENE_UNIT,
PARAGRAPH_UNIT, TRANSITION_UNIT, HUMAN_GROUP, DERIVED_SCAFFOLD_GROUP, UNRESOLVED_UNIT.
A node may have an unresolved parent without having an unknown structural function;
therefore known speech units keep SPEECH_UNIT, not UNRESOLVED_UNIT.

One JOB_BOOK TECHNICAL_ROOT provides graph connectivity only. It is not a textual
marker, boundary or discovered unit. Unresolved nodes connect via TECHNICAL_ROOT_LINK.
`textual_boundary` records the human boundary function, not an MR1 classification.
Non-textual groups have textual_boundary=false and explicit group_origin/provenance.

Relation classes are independent:

| Class | Types and scope |
| --- | --- |
| HIERARCHY | Explicit CHILD_OF or HIERARCHICALLY_ABOVE only |
| CONTINUATION | CONTINUES_WITHIN; not promoted to a direct-parent edge |
| MEMBERSHIP | GROUP_MEMBER_OF; reviewed grouping, not direct parentage |
| HORIZONTAL | SAME_LEVEL_SIBLING; PARALLEL_TO supported |
| CLOSURE_COMPARISON | Human PARALLEL_ENDING; original PARALLEL_TO retained |
| LOCAL_CLOSURE | HSA2-F DIRECT_LOCAL_CLOSURE |
| HIGHER_TERMINATION | HSA2-F TERMINATES_ENCLOSING_GROUP |
| NEGATIVE | NO_DIRECT_RELATION and NO_BOUNDARY |
| DESCRIPTIVE | TRANSITION_COMPONENT, NARRATIVE_INTRODUCTION, CYCLE_ONSET_OF |
| RESPONSE_OVERLAY | RESPONSE supported; no new antecedent is inferred |
| TECHNICAL | TECHNICAL_ROOT_LINK only |

Negative NO_BOUNDARY and descriptive TRANSITION_COMPONENT are typed self-assertions,
not self-parent edges. Only HIERARCHY edges determine direct_parent_ids; all others
remain distinct. Deduplicate only identical mapped source/target/type/dimension keys,
retaining every contributing judgment ID. No inverse or transitive completion.

Reference_start/end describe a judgment locus (32:2–5, for example), not the whole
speech's coverage. Coverage_start/end remain blank: a sibling onset does not create
an explicit ending at the preceding verse. Human-supplied group scope is labeled
as such and does not create a new marker.

## Groups and preserved structure

- CYCLE_1/2/3 are non-textual HUMAN_GROUP nodes with 6/6/4 peer speech members.
  Membership positions follow the supplied sequence, never a parent-selection rule.
  Distinct textual cycle-onset records at 4:1/15:1/22:1 remain sibling anchors.
  CYCLE_ONSET_OF associates each with its group. 11:4 stays within 11:1; no Zophar III,
  placeholder or inferred missing speech exists. 26:1 is the final cycle-3 onset.
- DIALOGUE_CYCLE_SEQUENCE is HUMAN_RELATION_DERIVED, containing the three cycle
  groups as members. Independent initial Job speech 3:1 is not made its child/member.
  The explicit 3:1 HIERARCHICALLY_ABOVE 3:2 and 3:2 continuation remain separate.
- POST_DIALOGUE_JOB contains peer onsets 27:1 and 29:1, preserving TAKE_MASHAL+AMR
  in historical evidence. 28:1 remains NO_BOUNDARY / CONTINUES_WITHIN 27:1.
- HSA2-F yields 31:40→29:1 DIRECT_LOCAL_CLOSURE; 31:40→27:1 NO_DIRECT_RELATION in
  DIRECT_CLOSURE_TARGET (= NO_DIRECT_CLOSURE); 31:40→POST_DIALOGUE_JOB
  TERMINATES_ENCLOSING_GROUP (= HIGHER_ORDER_TERMINAL_EFFECT). Ending status survives.
  None of these makes 29:1 subordinate to 27:1 or creates a general closure rule.
- Two explicit human span targets, 1:1–1:5 and 2:1–2:10, become non-textual HUMAN_GROUP
  references with provenance HSA001/HSA010. They are not equated to other nodes by
  a shared opening reference. All Job 1–3 scene/continuation/parallel-ending relations
  remain. 1:22/2:10 are not MR1 explicit closures; 2:11 global parent remains unresolved.
- ELIHU_SPEECH_SEQUENCE is HUMAN_RELATION_DERIVED from HSA020–HSA023. Its four peer
  members are 32:6/34:1/35:1/36:1. The requested introduction representation uses
  a DESCRIPTIVE NARRATIVE_INTRODUCTION edge from HSA019 (32:2–5) to this group,
  attributed to those human records and R4.3 request sections 14–15. This does not
  rewrite HSA019's unresolved parent, make introduction and speech peer onsets, or
  assert a new hierarchical parent. 32:1 remains a transition; 37:24 remains an
  ending without a newly assigned direct closure target.
- YHWH onsets 38:1/40:6 remain peers; only reviewed 40:1 is CHILD_OF 38:1. Job
  responses 40:3/42:1 remain peers. No rhetorical-response or adjacency relation is
  converted to hierarchy. No specific response antecedent is newly asserted.
- 42:7 remains PARAGRAPH_ONSET; 42:16 remains NO_BOUNDARY / CONTINUES_WITHIN 42:7.
  42:10/42:12 are not promoted. No supplied 42:7–17 analytical frame was found in
  accepted R4.2's three-frame inventory, so no extra enclosing node is manufactured.

Accepted R4.2 frame/enclosure tables remain unchanged. Optional frame context in
the unresolved table uses an exact participant_event_id join through a node's source
context. It does not assert that the whole node is enclosed, rank a possible parent,
or adopt nearest-anchor fields. Only three early-Job candidate frames are present;
none supplies a later 32:1 or final-narrative global parent.

## Unresolved parentage and display

Every non-root node without an explicit hierarchical parent appears in
03_unresolved_parentage.csv, with reference, function, known typed relations/groups,
accepted frame context, reason, all human/evidence IDs and later-review requirement.
Known continuation or membership is not erased merely because direct parent remains
UNRESOLVED. This strict distinction leaves 57 cases, including anchors and group
members, rather than pretending the scaffold supplies a finished hierarchy.

Markdown separates group membership indentation, explicit resolved hierarchy and
typed overlays. Every unresolved case appears in UNRESOLVED GLOBAL SEAMS. The report
must never visually make a technical link or a group-membership indentation into
a settled parent. No score, rank or preferred parent exists.

Unsupported connections remain unresolved and compilation continues. Stop only for
source/schema contradictions or logic that would invent parentage or overwrite human
evidence. No adjacency, chapter, verse, speaker, marker identity, semantic topic,
commentary, nearest-anchor or shortest/longest-span parent heuristic is allowed.

## Outputs and validation

01 nodes; 02 typed edges; 03 unresolved parentage; 04 Markdown scaffold; 05 group
membership; 06 non-parent overlays; 07 node/edge provenance; 08 negative controls;
09 gates; 10 lossless human-record accounting; 11 accepted frame context; 90 metadata;
99 complete SHA256 manifest. `history/` retains all accepted source members.

Syntax, original full regression, stage unit tests, synthetic self-test/manual report
inspection precede real compilation. Every gate has a negative mutation. Independently
rerun with identical accepted artifacts and require byte-identical files and ZIP.
Verify frozen hashes before/after, all provenance, unresolved completeness, nested
and outer manifests, CRC, disk bytes and Markdown truthfulness. Windows is empirical;
Termux instructions do not claim cross-platform execution. Source outputs remain ignored.
