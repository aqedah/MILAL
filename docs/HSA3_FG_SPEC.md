# HSA3-F/G — Final Global Seam Human Adjudication

Baseline: `d720d805f771cb18912728dd6982177c57459ef6`, main.
Authority: [exact researcher request](HSA3_FG_RESEARCHER_SOURCE.txt) and
[transcribed decisions](../config/hsa3_fg_human_decisions.json).
The researcher authorizes synthetic validation, real frozen-evidence validation,
independent deterministic rerun, and commit/push after all tests/gates PASS.
No new lexical audit, marker discovery, parent inference or R4.4 execution.

## Sources and identity

Consume only the FG-PREP result ZIP pinned to SHA256
`14dd08fcffabf2d29b6574c05254ca403ba08b9fe01207269ccd6fb9ca3db1f6`.
Require ZIP CRC, all manifests, FG-PREP stage/status and every prior gate PASS,
A–E FROZEN, original F/G UNREVIEWED fields, and original unresolved-parent schema.
Pin 143 prior repository files. Preserve all 183 upstream members byte-for-byte
under `history/fg_prep/`, including the BHSA snapshot and every nested artifact.
Real validation uses the already extracted BHSA 2021 / TF 13.1.0 evidence;
it does not reload BHSA or recompute the frozen lexical analysis.
Synthetic mode uses the existing synthetic builders and cannot load a real ZIP.

Use exact existing HSA node/edge IDs. Selecting a researcher-specified locus in
the evidence panel is not object equivalence: retain every clause row there,
its native clause/atom/word IDs and all existing evidence links. Each selected
row has artifact/member/raw-row SHA256, one-based data row and explicit identity.
No fuzzy linkage, nearest-onset attribution or source reconstruction.

## Human composition decisions

F and G become ACCEPTED / FROZEN in a new human layer. The original blank review
records remain unchanged. Canonical REVIEW_FIELDS is imported, not redefined;
the approved decision records do not fabricate review time or other responses.

Create/confirm four NON_TEXTUAL_COMPOSITION_GROUP records:

| Group | Human span | Ordered canonical members |
| --- | --- | --- |
| YHWH_JOB_RESPONSE_COMPLEX_1 | 38:1–40:5 | H:HSA025, H:HSA026, H:HSA027 |
| YHWH_JOB_RESPONSE_COMPLEX_2 | 40:6–42:6 | H:HSA028, H:HSA029 |
| YHWH_JOB_RESPONSE_SEQUENCE | 38:1–42:6 | complex 1, complex 2 |
| FINAL_NARRATIVE_COMPLEX | 42:7–42:17 | H:HSA030 onset anchor |

Group membership is composition-only, not CHILD_OF, HIERARCHICALLY_ABOVE,
CONTINUES_WITHIN, textual SAME_LEVEL_SIBLING or BHSA mother. Spans are explicitly
supplied human annotations, not detected closure spans. 38:3/40:7 challenge
clauses are evidence anchors; no new textual nodes. Reuse H:HSA027/H:HSA029 with
40:3–5/42:1–6 response-unit span annotations, without creating duplicate units.
Final-narrative internal 42:10/12/16 clauses are evidence anchors rather than
new boundary nodes. H:HSA031 retains its existing continuation to H:HSA030.

Audit the frozen graph and accepted A–C/D–E action/group tables for existing
objects. GROUP_MEMBER_OF is reused with ordered membership positions. An exact
equivalent group under a different ID or ambiguous equivalent relation stops
execution for an explicit canonical mapping; it is not duplicated or guessed.
Matching requested claims confirm the existing canonical ID. Repeated requests
are NO_ACTION_DUPLICATE. New counts are computed, not semantic constants.

The existing repository has no composition peer or equivalent post-speech
narrative transition type. The authorized new SAME_LEVEL_COMPOSITION_PEERS is
symmetric and stored once with canonical unordered-pair equivalence. It never
rewrites historical reciprocal textual siblings. POST_SPEECH_NARRATIVE_TRANSITION
is directed from response sequence to final narrative, COMPOSITION_TRANSITION.
ANA POST_CLOSURE_TRANSITION is a different accepted overlay, not an alias.
Keep the current existing criteria registry and its admissibility unchanged.
The new human rationale cites multiple formal/distributional correspondences;
speaker, adjacency, chapter, repeated formula or semantic similarity alone is
insufficient. No scoring or automatic promotion of draft criteria occurs.

## Internal controls and negative claims

Preserve 38:1↔40:6 and 40:3↔42:1 textual SAME_LEVEL_SIBLING, and
40:1 CHILD_OF 38:1. 42:7 remains PARAGRAPH_ONSET. Its backward temporal frame
concerns YHWH speaking; 42:6 is Job's response. Do not encode direct parentage,
RESPONSE_TO or CONTINUES_WITHIN from 42:6 to 42:7 or reverse parentage.

Negative constraints use exact FG-PREP evidence IDs for loci without an HSA
node. For each 42:6 clause, record NO_DIRECT_PARENTAGE in both parent directions,
NO_DIRECT_RESPONSE_ANTECEDENT forward, and dimension-specific NO_DIRECT_RELATION
excluding CONTINUES_WITHIN forward. NO_DIRECT_PARENTAGE uses the prior canonical
meaning: source is excluded as parent of target. This is not a universal denial
of discourse relationships.

42:10 and 42:12 stay internal. New NO_BOUNDARY_PROMOTION constraints preserve the
explicitly excluded claims per source clause: 42:10 paragraph/macro/sibling/parent;
42:12 paragraph/macro/parent. This does not assert that every internal feature
is NO_BOUNDARY in the historical sense. Preserve WXQt evidence and all clauses,
including 42:10 prayer and 42:12 later WayX clause.
42:16 NO_BOUNDARY / CONTINUES_WITHIN 42:7 remains unchanged. Preserve חיה versus
היה and the post-predicate/subject Time phrase, distinct from 3:1 and 42:7.
The required gate spelling WAYHI_WAYHI_LIFE_VERB_DISTINCTION_PRESERVED follows
the request verbatim; its actual test distinguishes HJH[ and XJH[.

## Frozen and unresolved layers

A–G FROZEN means all approved seam decisions are recorded, not a fully resolved
tree. Preserve all 57 original direct-parent questions. Classify the F/G-related
six as REMAINS_UNRESOLVED; 51 others are NOT_APPLICABLE_TO_APPROVED_DECISION.
No supplied F/G decision assigns a direct textual parent. These counts are Job
regression assertions only. All historical source rows remain unchanged.
Keep ANA-Q2/Q4/Q5 ACCEPTED and Q3 UNRESOLVED/HUMAN_DEFERRED, without causal or
fulfilment assertion. The 2:11–42:9 participant frame stays unadjudicated.
HSA2-F and every frozen analytical core remain untouched. R4.4 is not started.

## Outputs and validation

Emit the twelve required files plus complete F/G clause source links, response
span annotations, schema audit, exact human authority files, preserved nodes
and ANA decisions. All prior artifacts remain nested losslessly. The complete
review summary distinguishes textual hierarchy, textual peers, composition,
transition, overlays, negative constraints and unresolved questions.

Gates compute actual artifact/decision/identity invariants. Each has a negative
mutation, including the output manifest. Syntax, stage tests, prior/full tests,
self-test and synthetic report inspection precede real frozen-evidence execution.
An internal independent derivation checks deterministic payload; two separate
real CLI invocations must additionally produce identical ZIP bytes. No count of
new canonical relations is hard-coded into semantics. Test counts, real action
counts and artifact hashes are recorded in the validation receipt after execution.
