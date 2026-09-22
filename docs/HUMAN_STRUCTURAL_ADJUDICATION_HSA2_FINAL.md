# Human Structural Adjudication — HSA2-F final layer

Researcher decision supplied on 2026-09-22, following frozen HSA2 at
`21225566974ca4b18d38679c790a2b5c37066cd3`. These three records append a final
resolution; HSA1/HSA2 source judgments and all original UNRESOLVED fields remain unchanged.

HSA2 evidence audit → UNRESOLVED → researcher human review → HSA2-F.
No new generic closure rule is authorized. Marker evidence alone was insufficient.
Given the already adjudicated peer onsets at 27:1/29:1, the researcher identifies the
locally active speech after 29:1 and records the direct target as 29:1. Independently,
31:40 terminates the 27:1–31:40 post-dialogue Job speech group.

Vocabulary is inherited from HSA2: NO_DIRECT_RELATION in DIRECT_CLOSURE_TARGET
means only NO_DIRECT_CLOSURE to 27:1. It does not deny the independent group relation.
TERMINATES_ENCLOSING_GROUP expresses HIGHER_ORDER_TERMINAL_EFFECT. Neither relation
creates a parent/child edge between 27:1 and 29:1. The semantic_meaning column is an
explicit mapping to the researcher's wording, not an additional inferred relation.

The following tables exactly mirror the companion CSV. REVIEWED is supplied by the
researcher, never filled from computational evidence. No review time was supplied.

### HSA2-F-01

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-F-01 |
| candidate_id | CT01 |
| ending_reference | 31:40 |
| target_reference | 29:1 |
| dimension | DIRECT_CLOSURE_TARGET |
| selected_relation | DIRECT_LOCAL_CLOSURE |
| semantic_meaning | DIRECT_LOCAL_CLOSURE |
| original_status | UNRESOLVED |
| authority | RESEARCHER_FINAL_ADJUDICATION |
| review_status | REVIEWED |
| supporting_judgment_ids | ["HSA2-END-31","HSA2-JOB-27","HSA2-JOB-29","HSA2-NO-28"] |
| decision_provenance | Researcher-supplied HSA2-F final adjudication, 2026-09-22; baseline 21225566974ca4b18d38679c790a2b5c37066cd3; request sections 3–7. |
| reasoning | Marker evidence alone left the direct target unresolved. Prior human adjudication establishes 27:1 and 29:1 as SAME_LEVEL_SIBLING with matching TAKE_MASHAL+AMR signatures, and 28:1 as NO_BOUNDARY / CONTINUES_WITHIN 27:1. Given that hierarchy, the researcher identifies the locally active unit after 29:1 as the speech opened at 29:1. The researcher separately adjudicates termination of the 27:1–31:40 group. This is not an adjacency heuristic or a generic rule. |

### HSA2-F-02

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-F-02 |
| candidate_id | CT02 |
| ending_reference | 31:40 |
| target_reference | 27:1 |
| dimension | DIRECT_CLOSURE_TARGET |
| selected_relation | NO_DIRECT_RELATION |
| semantic_meaning | NO_DIRECT_CLOSURE |
| original_status | UNRESOLVED |
| authority | RESEARCHER_FINAL_ADJUDICATION |
| review_status | REVIEWED |
| supporting_judgment_ids | ["HSA2-END-31","HSA2-JOB-27","HSA2-JOB-29","HSA2-NO-28"] |
| decision_provenance | Researcher-supplied HSA2-F final adjudication, 2026-09-22; baseline 21225566974ca4b18d38679c790a2b5c37066cd3; request sections 3–7. |
| reasoning | Marker evidence alone left the direct target unresolved. Prior human adjudication establishes 27:1 and 29:1 as SAME_LEVEL_SIBLING with matching TAKE_MASHAL+AMR signatures, and 28:1 as NO_BOUNDARY / CONTINUES_WITHIN 27:1. Given that hierarchy, the researcher identifies the locally active unit after 29:1 as the speech opened at 29:1. The researcher separately adjudicates termination of the 27:1–31:40 group. This is not an adjacency heuristic or a generic rule. |

### HSA2-F-03

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-F-03 |
| candidate_id | CT03 |
| ending_reference | 31:40 |
| target_reference | 27:1–31:40 |
| dimension | HIGHER_ORDER_TERMINAL_EFFECT |
| selected_relation | TERMINATES_ENCLOSING_GROUP |
| semantic_meaning | HIGHER_ORDER_TERMINAL_EFFECT |
| original_status | UNRESOLVED |
| authority | RESEARCHER_FINAL_ADJUDICATION |
| review_status | REVIEWED |
| supporting_judgment_ids | ["HSA2-END-31","HSA2-JOB-27","HSA2-JOB-29","HSA2-NO-28"] |
| decision_provenance | Researcher-supplied HSA2-F final adjudication, 2026-09-22; baseline 21225566974ca4b18d38679c790a2b5c37066cd3; request sections 3–7. |
| reasoning | Marker evidence alone left the direct target unresolved. Prior human adjudication establishes 27:1 and 29:1 as SAME_LEVEL_SIBLING with matching TAKE_MASHAL+AMR signatures, and 28:1 as NO_BOUNDARY / CONTINUES_WITHIN 27:1. Given that hierarchy, the researcher identifies the locally active unit after 29:1 as the speech opened at 29:1. The researcher separately adjudicates termination of the 27:1–31:40 group. This is not an adjacency heuristic or a generic rule. |
