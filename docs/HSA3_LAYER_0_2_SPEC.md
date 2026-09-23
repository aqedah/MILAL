# HSA3-LAYER.0.2 — Parentage Necessity Human Freeze

Baseline: `a8fbd794bfec3f05132f847a8ba51f9f0e63567b`, main.
Authority: [exact researcher request](HSA3_LAYER_0_2_RESEARCHER_SOURCE.txt)
and [transcribed human decisions](../config/hsa3_layer_0_2_human_decisions.json).
The request authorizes implementation, synthetic and frozen-real validation,
independent rerun, commit and push after tests/gates pass. It does not authorize
new parent edges, participant-arc analysis, fresh extraction or R4.4 implementation.

## Historical input and identity

Consume the completed HSA3-LAYER.0.1 ZIP:
`results/hsa3_layer_0_1_real_final_20260923_c_results.zip`, SHA256
`85232a5fae33433333b75daaac496f36836b00bd36d3ce0d9cf37d358b1a0e17`.
Verify SHA256, ZIP CRC, 225 members, all nested manifests, version/mode/PASS gates,
all A–G FROZEN, proposal uniqueness, category counts and exact historical row
coverage. Verify 160 frozen repository file hashes. Baseline receipt verifies
the exact supplied commit as an ancestor, so the frozen runner remains usable
after its own completion commit. The initial session HEAD must match the supplied
baseline before implementation; record that separately in the validation report.

Preserve all 225 input members byte-for-byte under `history/hsa3_layer_0_1/`.
Do not regenerate the real input, reclassify its proposals, change its review
fields, resolve original parents or change any canonical graph. Synthetic mode
uses the frozen synthetic builders and is explicitly SYNTHETIC_ONLY; it cannot
consume a real ZIP. Real mode only reads the pinned frozen artifact.

The source proposal table has no proposal_id field. Its unique key is node_id.
The new source_proposal_id explicitly names the existing composite identity:
`HSA3-LAYER.0.1::10_parentage_necessity_audit.csv::node_id=<exact ID>`.
It is an address, not an invented upstream field. Each new decision/crosswalk
records the exact member, one-based data row, node key, raw CSV row SHA256,
member SHA256, artifact SHA256, request SHA256 and human-decision JSON SHA256.
Synthetic artifact_sha256 is its manifest digest, explicitly marked synthetic
in the input receipt; real artifact_sha256 is the exact ZIP SHA256.
No fuzzy text, reference-range or nearest-onset joins are permitted.

## Authorized human layer

The researcher accepts all rows in each existing category. Apply the explicitly
supplied category decision to that exact source population; do not infer a new
scholarly judgment from the category's machine-generated rationale. Preserve
the original proposal and its criteria in full and attach a separate human
rationale, source-request section and human-decision JSON pointer.

| Original category | Count (Job regression) | Human necessity status |
| --- | ---: | --- |
| P2 non-textual group | 8 | DIRECT_PARENT_NOT_REQUIRED |
| P3 canonical speech / role alias | 6 | DIRECT_PARENT_NOT_REQUIRED |
| P4 local relations | 10 | CURRENT_LAYERED_RELATIONS_SUFFICIENT |
| P5 container membership | 19 | CURRENT_LAYERED_RELATIONS_SUFFICIENT |
| P6 global layer | 13 | CURRENT_LAYERED_RELATIONS_SUFFICIENT |
| P7 H:HSA012 / Job 2:11 | 1 | DIRECT_TEXTUAL_PARENT_NOT_REQUIRED |

Keep the last status's exact wording. The human status distribution is 14 / 42 / 1.
Each researcher_decision is ACCEPT and human_status is FROZEN. The historical
proposal_status remains UNREVIEWED, including P7. P7's former REVIEW_NEEDED
proposal remains historical; it is superseded only in representation-necessity
review, not silently rewritten. All additional_parentage_review_required fields
in the new layer are false. Original later_human_review_required fields remain
historical, not an instruction to reopen the new active queue.

Do not prefill generic observation, context or review-time fields. Import the
canonical REVIEW_FIELDS when validating the historical records; preserve them
unchanged within original_proposal. Dedicated researcher fields transcribe the
explicit current authorization rather than fabricating general review answers.

P2 group membership and ordering stay unchanged. P3 includes three canonical
speech nodes and three role aliases: neither delete nor retype the speech nodes.
P4 retains each typed local relation. P5 membership/peers/function suffice without
nearest-preceding-onset parent assignment. P6 global judgments and constraints
remain separate from parentage.

Job 2:11 remains H:HSA012, a textual PARAGRAPH_ONSET with the accepted
FRIENDS_ARRIVAL / PARTICIPANT_INTRODUCTION annotation for 2:11–13,
NOT_WITHIN_SECOND_TESTING_SCENE and OPENING_NARRATIVE_COMPLEX membership.
Record the exact supplied Korean rationale. historical_direct_parent remains
UNRESOLVED. DIRECT_TEXTUAL_PARENT_NOT_REQUIRED is about representation necessity,
not a NO_PARENT assertion or a parent at 1:1, 2:1, 3:1 or any other location.

## Distinct completion measures

- historical_unresolved_parent_rows = 57.
- PARENTAGE_NECESSITY_REVIEW_COMPLETED = 57.
- active_future_direct_parent_questions = 0.
- DIRECT_PARENT_EDGE_RESOLVED = 0.
- New structural relations / composition relations = 0 / 0.

These measures are computed from records, not populated as unconditional gates.
This stage terminates the present parentage-necessity review without constructing
a complete one-parent tree. NO DIRECT TEXTUAL PARENT does not imply STRUCTURAL
INFORMATION MISSING. Historical UNRESOLVED does not imply mandatory future review.
Textual hierarchy, same-level relations, composition, transitions, overlays,
negative constraints and unresolved/deferred states remain independent dimensions.

## Future scope and readiness

Copy the prior participant-arc NEXT_RESEARCH_SCOPE note byte-for-byte. Do not
create a 2:11–42:9 span, frame, textual macro unit, closure or 42:10 promotion.
A–G remain FROZEN, ANA-Q2/Q4/Q5 accepted, ANA-Q3 UNRESOLVED/HUMAN_DEFERRED.

Readiness becomes PARENTAGE_NECESSITY_REVIEW_COMPLETE and
R4_4_CONTRACT_REVIEW_STILL_REQUIRED. R4.4 remains NOT STARTED. A future authorized
contract must accept the partial textual hierarchy, textual peers, composition,
transitions, overlays, negatives, historical unresolved states and separate
human necessity decisions; no synthetic/default parents.

## Outputs and validation

Root files 01–03 contain decisions, exact crosswalk and final necessity states.
04 documents Job 2:11; 05 summarizes completion; 06 preserves future scope;
07 updates readiness; 08 contains computed run gates; 09 preserves exact request;
10 preserves human-decision JSON; 90 contains deterministic metadata; 99 hashes
all output members. Existing canonical views are linked in the nested history.

Every run gate has a negative mutation, including manifest corruption. Tests
also reject each prohibited Job 2:11 parent assignment, unknown/duplicate source
identities, missing schema, unauthorized decisions and real/synthetic mixing.
Run syntax, new unit tests and full regressions with zero skips. Inspect the
human-facing synthetic packet before real execution. Independently invoke two
real runs and compare complete ZIP bytes. Full-suite PASS/skip-zero and
independent ZIP equality are external release gates with their own negative tests,
recorded in the validation report; stage exit alone never claims they passed.
