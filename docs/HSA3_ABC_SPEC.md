# HSA3-A/C — Opening–Dialogue Global Seam Human Adjudication

Baseline: `9abbb45f1a4159db99a86ce4647f26d538937808`.
Authority: [exact researcher request](HSA3_ABC_RESEARCHER_SOURCE.txt) and
[canonical decisions](../config/hsa3_abc_human_decisions.json).
Only A/B/C are adjudicated. D/E and ANA remain frozen; F/G remain UNREVIEWED.
No R4.4, new lexical scan, marker discovery, or participant-frame adjudication.

## Input and provenance

Read the frozen D/E ZIP, not a re-execution of historical empirical analysis:
`results/hsa3_de_elihu_seam_final_20260923_a_results.zip`, SHA256
`bff67a7d8b67b40134fe3a1114eb04f3d8c7a683f33442479fb36dfd1d1d3cab`.
Verify exact SHA256, CRC, 129 members, nested manifests, stage/status and gates.
All 129 members are copied byte-for-byte beneath `history/hsa3_de/`.
Pin 125 prior repository files. Verify the baseline commit object and ancestry;
do not record a changing current HEAD in deterministic output metadata.
Synthetic execution uses the existing synthetic builders; real execution only
reads the exact frozen artifact. No substitute files or fuzzy linkage.

Node, case, criteria and unresolved links include exact identity, source member,
one-based CSV data row, raw CSV row SHA256, member SHA256 and input artifact SHA256.
CSV compound fields use the repository's canonical JSON encoding.
The exact request bytes are protected by a narrow Git `-text` attribute.

## Existing-schema audit

The 61-node/205-edge historical graph has neither requested composition complex.
There is no canonical sequential edge type. Reuse existing GROUP_MEMBER_OF with
ordered membership fields; do not create PRECEDES or infer textual parentage.
Compare exact ordered member IDs and non-textual semantics to detect an existing
equivalent group. Ambiguous equivalence, an incompatible ID collision, or an
unmapped alternate canonical ID stops rather than silently duplicating a group.

Reuse `H:HSA012` for the 2:11 onset and `H:HSA013` for INITIAL_JOB_SPEECH.
HSA013 and HSA2-INITIAL already map explicitly to H:HSA013. Preserve both historical
PARAGRAPH_ONSET and SPEECH_UNIT_ONSET judgments; do not replace either. The new
labels/spans are separate supplied human annotations, not modified frozen nodes.
Existing DIALOGUE_CYCLE_SEQUENCE, CYCLE_1/2/3 and POST_DIALOGUE_JOB IDs are reused.

## Approved decisions and relation dimensions

A: 2:11–13 is FRIENDS_ARRIVAL / PARTICIPANT_INTRODUCTION, separate from 2:1–10.
`H:HSA012 → HUMAN_SCOPE_2_1_10 NOT_WITHIN_SECOND_TESTING_SCENE` states precisely
that negative containment decision. Its exact direct textual parent stays
UNRESOLVED: no parent is supplied at 1:1, 2:1 or 3:1.

OPENING_NARRATIVE_COMPLEX, 1:1–2:13, is NON_TEXTUAL_COMPOSITION_GROUP:

1. HUMAN_SCOPE_1_1_5 — household/opening frame 1:1–1:5.
2. H:HSA002 — testing scene 1, 1:6–1:22.
3. HUMAN_SCOPE_2_1_10 — testing scene 2, 2:1–2:10.
4. H:HSA012 — friends arrival, 2:11–2:13.

B: H:HSA013 is INITIAL_JOB_SPEECH, 3:1–3:26, with NOT_MEMBER_OF_CYCLE_1.
Cycle 1 starts at 4:1. The historical 3:1 HIERARCHICALLY_ABOVE 3:2 and
3:2 CONTINUES_WITHIN 3:1 remain. Initial speech precedes the cycles only in
composition order. It is not their parent or a Cycle 1 member.

C: the sequence retains the three cycles and exact 6/6/4 speech pattern.
Cycle onsets 4:1/15:1/22:1 retain their higher structural function. No synthetic
Zophar III or Cycle 4 is created. POST_DIALOGUE_JOB retains 27:1/29:1 siblings,
28:1 NO_BOUNDARY/continuation and all three 31:40 HSA2-F closure dimensions.

Four directional NO_DIRECT_PARENTAGE constraints exclude parentage both ways
between POST_DIALOGUE_JOB and DIALOGUE_CYCLE_SEQUENCE, and both ways between
POST_DIALOGUE_JOB and CYCLE_3. Use the existing TEXTUAL_PARENTAGE dimension:
as in D/E, the source is excluded as the target's parent. This is distinct from
the child-to-parent direction of CHILD_OF. These explicit negatives do not deny
all discourse relations.

JOB_FRIENDS_DISPUTE_COMPLEX, 3:1–31:40, is NON_TEXTUAL_COMPOSITION_GROUP:

1. H:HSA013 — INITIAL_JOB_SPEECH, 3:1–3:26.
2. DIALOGUE_CYCLE_SEQUENCE — 4:1–26:14.
3. POST_DIALOGUE_JOB — 27:1–31:40.

Spans are researcher-supplied scope metadata, including 26:14; no new closure
is detected. Neither new group is a textual parent, CHILD_OF target,
HIERARCHICALLY_ABOVE node, structural mother or BHSA mother surrogate.
Same-level structure, composition, textual hierarchy and overlay remain separate.
Do not attach 2:11 to the dispute complex or adjudicate the broader
2:11–42:9 participant-frame hypothesis. No new grouping links 32:1 onward.

## Actions, criteria and unresolved accounting

Confirm each unique existing edge referenced by A/B/C panels once, keeping its
original ID/record. Shared-panel references are not duplicate relation creation.
Existing historical directed reciprocal rows remain separate records. New
requests are checked against exact endpoint/type semantics; repeated requests
are NO_ACTION_DUPLICATE. No label/span similarity establishes identity.

Report CREATED, CONFIRMED_EXISTING, NEGATIVE_CONSTRAINT_CREATED,
UNRESOLVED_RETAINED and NO_ACTION_DUPLICATE separately. New composition nodes
are counted separately from relations. Current baseline yields 3 seam decisions,
2 groups, 7 new membership relations, 123 existing edge confirmations, 6 negative
constraints, 43 retained unresolved questions, and 0 duplicate-skipped requests.
These counts are computed from audited data, not analytical rules.

Use the actual 24-code criteria registry. Evidence contributions and
insufficient-alone codes are crosswalks of the supplied rationale, not automatic
inference or a retroactive claim about original researcher reasoning. Preserve
the full registry records, dimensions and judgment/edge references. Ordering is
documented in prose without inventing an evidence code. Adjacency, chapter,
speaker, theme and semantic response alone never assign a parent.

All 57 historical unresolved rows are preserved. A/B/C participation identifies
43 rows: 0 resolved by A, 0 by B, 0 by C, 43 REMAINS_UNRESOLVED. Other 14 are
NOT_APPLICABLE_TO_APPROVED_DECISION; they are still unresolved historically.
Frozen seam decisions do not resolve parent questions. In particular 2:11 stays
unresolved even while SEAM_A is FROZEN.

## Outputs and validation

The twelve required outputs retain the names in the request. Additional files:
11 source facts, 12 separate human unit annotations, 13 exact F/G cases,
14 canonical decisions, 15 exact request. All original input members remain.
The F/G packet keeps original questions, involved nodes, evidence pointers,
accepted positive/negative constraints, unresolved rows, criteria dimensions
and canonical REVIEW_FIELDS (UNREVIEWED only; all other fields blank).
It includes relevant already-frozen D/E negatives as context, not adjudication.

Every computed gate has a negative mutation test, including manifest corruption.
Run syntax, stage tests and all prior regressions (zero skips), then the stage
self-test. Inspect synthetic human-facing output before real execution. Run
real adjudication and an independent invocation; require every output member
and ZIP to be byte-identical, with CRC and nested manifests verified.
Technical PASS is not an adjudication of F/G or authorization to start R4.4.
