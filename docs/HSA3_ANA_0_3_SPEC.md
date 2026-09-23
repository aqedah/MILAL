# HSA3-ANA.0.3 — Human Adjudication Freeze

Baseline: `3aa956887dc1cc40563167f57af26553e38404e0`.
Authority: [unaltered researcher request](HSA3_ANA_0_3_RESEARCHER_SOURCE.txt),
transcribed into [canonical decisions](../config/hsa3_ana_0_3_human_decisions.json).
The request authorizes freezing these decisions, validation and commit/push.
It does not authorize A–G parentage adjudication or R4.4.

## Scope and authority

This is a human-record stage consuming the exact frozen ANA.0.2 ZIP. It does
not run BHSA extraction or reconsider lexical classifications. Human rationales
are preserved verbatim with normalized line endings, source bytes and SHA256.
The four decisions are supplied inputs, never computationally inferred review
field values. Existing canonical REVIEW_FIELDS are imported for untouched A–G
and historical Q1–Q5 sheets. Their historical UNREVIEWED state remains history;
the new decision table separately records Q2–Q5's present human disposition.

| Question | Disposition | Relation | Dimension |
| --- | --- | --- | --- |
| Q2 / ANA-C1 | ACCEPTED | POST_CLOSURE_TRANSITION, 31:40 → 32:1 | TRANSITION_OVERLAY |
| Q3 / ANA-C2 | UNRESOLVED / HUMAN_DEFERRED | LONG_DISTANCE_RESPONSE candidate, 31:35 → 38:1 | RESPONSE_RELATION |
| Q4 / ANA-C3 | ACCEPTED | CONTRASTIVE_ANA_FRAME, 32:1 ↔ 38:1 | OVERLAY_RESPONSIO |
| Q5 / ANA-C4 | ACCEPTED | ELIHU_RESPONSE_ROLE_INTERVENTION, scope 32:2–37:24 | RHETORICAL_FUNCTION_OVERLAY / RESPONSE_RELATION |

Accepted judgments 3; deferred decisions 1; accepted overlays 3; textual
hierarchy edges 0. These Job controls are configured regression expectations.
Q3 retains positive lexical/participant evidence and the explicit request, but
neither an explicit causal/fulfillment marker nor interpretive necessity has
been established. Its before/after states are UNADJUDICATED → UNRESOLVED;
human_decision=DEFERRED, accepted_relation_created=false,
automatic_resolution=false. No accepted Q3 relation is emitted. Context
31:40 remains metadata only. ANA-C2 remains a live candidate, never deleted.

Q2 does not establish CHILD_OF, SAME_LEVEL_SIBLING or DIRECT_CLOSURE_TARGET.
Q4 does not establish parentage, inclusio or Q3 fulfillment. Q5 preserves the
historical ELIHU_WITHIN_ANA_RESPONSE_INTERVAL candidate separately from its
newly accepted refinement. Its scoped role has no invented directed endpoints;
source_ref/target_ref are explicitly blank, scope_ref is populated, and the
historical interval endpoints remain in historical_candidate_record. The
32:2–5 narrative introduction remains distinct from the 32:6–37:24 speech
sequence. Elihu is not assigned substitute-for-YHWH, RESPONSE_TO God,
FOURTH_FRIEND or 32:6 CHILD_OF 32:1.

## Exact input and preservation

`config/hsa3_ana_0_3_job.json` pins the 97-member ANA.0.2 archive with SHA256
`00c3c052f6133456d371b2736261e469b69ba5ad91891d0ccf44d6b59a90aa5d`.
It also pins 107 prior source/config/test/document/runner files and the new
canonical researcher decisions. All hashes, ZIP CRC, manifests, stage/status,
gates, counts, identities and blank historical review fields are checked before
use. `--archive` relocates only the same exact ZIP, never substitutes an input.
The synthetic-only fixture reuses existing synthetic builders, is clearly
labeled, and never substitutes for the empirical package.

All 97 input members are copied byte-for-byte beneath `history/ana_0_2/`.
59 frozen human judgments, 57 unresolved rows, all seven A–G cases, all four
original candidates and all HSA2-F relations remain unchanged. In particular:

- 31:40 → 29:1 DIRECT_LOCAL_CLOSURE.
- 31:40 → 27:1 NO_DIRECT_RELATION.
- 31:40 → POST_DIALOGUE_JOB TERMINATES_ENCLOSING_GROUP.
- 3:2 formal-CSF negative control; 37:24 adjacency insufficiency.

Every evidence link resolves an existing explicit ID, exact CSV member/data
row, raw CSV row hash and member hash. No fuzzy linkage or inferred identity.
All prior evidence and original source locators remain available in the nested
artifact. Original direct/contextual addendum distinctions remain unchanged.

## Criteria and seam dependencies

Only existing canonical criteria codes are used. Explicit-request,
response-failure, self-declared-role, missing causal/fulfillment marker and
FORMAL_CSF insufficiency concepts without dedicated codes are methodological
notes. The 24-code frozen draft registry is not changed. Supplied relation
dimensions are not new registry entries. Code associations document relevant
contributions/limitations, never automatic sufficiency or global weights.

SEAM_D receives Q2/Q4/Q5 accepted-overlay evidence dependencies. SEAM_E receives
Q4/Q5 accepted-overlay dependencies and Q3 unresolved-candidate evidence only.
All six dependency rows have resolves_parentage=false and
modifies_original_case=false. Q3 cannot resolve SEAM_E. The next packet displays
original A–G questions, unresolved IDs, blank review fields and these dependencies;
it does not begin adjudication.

## Outputs and checks

Required 01–10, 90 and 99 outputs follow the researcher's names. Additional
11 contains only the three accepted overlays; 12/13 preserve canonical human
input and request bytes. The metadata reports actual computed counts, source
receipts, no BHSA extraction and no R4.4.

Validate syntax, stage tests, all 807 prior regression tests, self-test and
synthetic packet inspection before the authorized real-artifact freeze. Every
gate has a negative mutation, including output manifest corruption. Independent
model builds check determinism within each run; independent processes must also
produce identical ZIP bytes and members. Real validation consumes frozen results,
not a new BHSA run. Report exact counts and limitations in the validation note.
