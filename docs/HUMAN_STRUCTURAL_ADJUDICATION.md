# HSA1 — Human Structural Adjudication Registry

Authority: researcher-supplied HSA1 judgments, recorded 2026-09-22 from starting
HEAD `77ca713b9520ce085135dc845f60d920095756cb`. This document and its equivalent
[CSV](HUMAN_STRUCTURAL_ADJUDICATION.csv) are the human-authored source of truth.
These REVIEWED values are explicitly supplied by the researcher, not an automatic
completion of unreviewed computational fields. HSA1 is not an analytical stage
or an automatic hierarchy generator.

BHSA 2021 / MR1 / R3c.3 / PROV1 / HR1 / R4.0 / R4.1 / R4.2 evidence remains
separate from the human structural conclusions. HR1 scopes themselves preserve
earlier human review; their inclusion does not turn human acceptance into a marker.
The auditor reads accepted, hash-pinned outputs without re-extracting the corpus.

## Reading the record

Each row is one human-adjudicated reference or supplied span (32:2–5 is one row).
JSON lists preserve explicitly supplied related references and corresponding IDs;
an empty target ID means an enclosing span was supplied without a separate judgment
object. UNRESOLVED means no relation was adjudicated. No inverse or transitive
relations, global parent spans, numerical scores, or unreviewed units are inferred.
The four Elihu siblings explicitly list all three peers in each row. Pair counts
are directed: reciprocal sibling/parallel records count twice.

The human did not choose a unique primary native atom for these verse/span-level
judgments. `primary_anchor_atom_if_known` therefore remains blank; all exact source
atom identities stay in the linked panels. Blank does not mean absent native data.
`INTERNAL_SPEECH_ONSET` describes the supplied 40:1 judgment. `SCENE_ONSET` at
1:6/2:1 records the supplied testing-unit onset, not an inferred whole-book macro level.

`R4.2:CONTROL:<reference>` identifies an existing exact control row, including every
native clause, participant candidate, MR1/HR1 anchor and formal occurrence ID in
that panel. The derived audit expands every dependency, with source archive/member/
row hashes and the complete source row. Formal/context links are not automatic
proofs of boundary or hierarchy. No fuzzy matching or representative-pattern loss.
Explicit R4.1 anchor links resolve separately to original MR1 events or HR1 scopes.
If a future supplied judgment has no exact machine link, retain its basis and use
`NO_EXACT_MACHINE_LINK`; never fabricate a source event. All current rows have exact
native/context links, which does not make their structural judgment computational.

## Human judgments (exact field-equivalent CSV view)

### HSA001 — Job 1:5

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA001 |
| reference_start | 1:5 |
| reference_end | 1:5 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | INTERNAL_TRANSITION |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["1:1–1:5"] |
| related_judgment_id_if_available | [""] |
| linguistic_basis | ויהי; 1:1–5 내부의 전환. |
| source_evidence_ids | ["R4.2:CONTROL:1:5","R4.2:P:853130","R4.2:P:853133","R4.2:P:853145","R4.2:P:853148","R4.2:P:853155","R4.1:MR1:way0:[\"497528\"]","R4.1:MR1:csf:[\"1\"]","MR1:way0:[\"497528\"]","MR1:csf:[\"1\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 1:6과 동일 계층으로 승격하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA002 — Job 1:6

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA002 |
| reference_start | 1:6 |
| reference_end | 1:6 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SCENE_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["2:1"] |
| related_judgment_id_if_available | ["HSA009"] |
| linguistic_basis | ויהי היום; 2:1과 병행하는 시험 단위 시작. |
| source_evidence_ids | ["R4.2:CONTROL:1:6","R4.2:P:853162","R4.2:P:853164","R4.2:P:853167","R4.1:MR1:way0:[\"497538\"]","MR1:way0:[\"497538\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 동일 계층은 연구자 판정이다. 정확한 전체 parent span은 미정. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA003 — Job 1:13

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA003 |
| reference_start | 1:13 |
| reference_end | 1:13 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SCENE_ONSET |
| hierarchy_relation | CHILD_OF |
| related_reference | ["1:6"] |
| related_judgment_id_if_available | ["HSA002"] |
| linguistic_basis | ויהי היום; 1:6에서 시작한 단위 내부의 새 장면. |
| source_evidence_ids | ["R4.2:CONTROL:1:13","R4.2:P:853263","R4.1:MR1:way0:[\"497569\"]","MR1:way0:[\"497569\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 1:6의 하위 장면이며 동일 계층 단위가 아니다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA004 — Job 1:14

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA004 |
| reference_start | 1:14 |
| reference_end | 1:14 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | INTERNAL_TRANSITION |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["1:13"] |
| related_judgment_id_if_available | ["HSA003"] |
| linguistic_basis | מלאך; 1:13에서 열린 장면 안의 participant-entry event. |
| source_evidence_ids | ["R4.2:CONTROL:1:14","R4.2:P:853270","R4.2:P:853272","R4.2:P:853279","R4.1:MR1:csf:[\"7\"]","MR1:csf:[\"7\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 네 전달자 sequence는 human control이다. 1:14는 overt מלאך; 1:16/17/18은 익명 진입이며 computational identity/first appearance는 UNRESOLVED. IMPLICIT_ROLE_FROM_PREVIOUS_SUBJECT는 identity 근거가 아니다. 1:6 수준으로 승격하지 않으며 사건 사이의 추가 sibling 관계는 판정하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA005 — Job 1:16

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA005 |
| reference_start | 1:16 |
| reference_end | 1:16 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | INTERNAL_TRANSITION |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["1:13"] |
| related_judgment_id_if_available | ["HSA003"] |
| linguistic_basis | זה + בא; 1:13에서 열린 장면 안의 participant-entry event. |
| source_evidence_ids | ["R4.2:CONTROL:1:16","R4.2:P:853300","R4.2:P:853304","R4.1:MR1:csf:[\"8\"]","MR1:csf:[\"8\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 네 전달자 sequence는 human control이다. 1:14는 overt מלאך; 1:16/17/18은 익명 진입이며 computational identity/first appearance는 UNRESOLVED. IMPLICIT_ROLE_FROM_PREVIOUS_SUBJECT는 identity 근거가 아니다. 1:6 수준으로 승격하지 않으며 사건 사이의 추가 sibling 관계는 판정하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA006 — Job 1:17

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA006 |
| reference_start | 1:17 |
| reference_end | 1:17 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | INTERNAL_TRANSITION |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["1:13"] |
| related_judgment_id_if_available | ["HSA003"] |
| linguistic_basis | זה + בא; 1:13에서 열린 장면 안의 participant-entry event. |
| source_evidence_ids | ["R4.2:CONTROL:1:17","R4.2:P:853321","R4.2:P:853325","R4.1:MR1:csf:[\"9\"]","MR1:csf:[\"9\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 네 전달자 sequence는 human control이다. 1:14는 overt מלאך; 1:16/17/18은 익명 진입이며 computational identity/first appearance는 UNRESOLVED. IMPLICIT_ROLE_FROM_PREVIOUS_SUBJECT는 identity 근거가 아니다. 1:6 수준으로 승격하지 않으며 사건 사이의 추가 sibling 관계는 판정하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA007 — Job 1:18

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA007 |
| reference_start | 1:18 |
| reference_end | 1:18 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | INTERNAL_TRANSITION |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["1:13"] |
| related_judgment_id_if_available | ["HSA003"] |
| linguistic_basis | זה + בא; 1:13에서 열린 장면 안의 participant-entry event. |
| source_evidence_ids | ["R4.2:CONTROL:1:18","R4.2:P:853346","R4.2:P:853350","R4.1:MR1:csf:[\"10\"]","MR1:csf:[\"10\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 네 전달자 sequence는 human control이다. 1:14는 overt מלאך; 1:16/17/18은 익명 진입이며 computational identity/first appearance는 UNRESOLVED. IMPLICIT_ROLE_FROM_PREVIOUS_SUBJECT는 identity 근거가 아니다. 1:6 수준으로 승격하지 않으며 사건 사이의 추가 sibling 관계는 판정하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA008 — Job 1:22

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA008 |
| reference_start | 1:22 |
| reference_end | 1:22 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | PARALLEL_ENDING |
| hierarchy_relation | PARALLEL_TO |
| related_reference | ["2:10"] |
| related_judgment_id_if_available | ["HSA011"] |
| linguistic_basis | בכל זאת לא חטא איוב; R4.2의 대응 평가절 및 F000020/G0, F001232/G1 형식 근거. |
| source_evidence_ids | ["R4.2:CONTROL:1:22","R4.2:P:853408"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance"] |
| methodological_note | MR1_EXPLICIT_CLOSURE=false. 두 시험 단위의 human parallel ending이며 MR1 closure rule 추가가 아니다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA009 — Job 2:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA009 |
| reference_start | 2:1 |
| reference_end | 2:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SCENE_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["1:6"] |
| related_judgment_id_if_available | ["HSA002"] |
| linguistic_basis | ויהי היום; 1:6과 병행하는 시험 단위 시작. |
| source_evidence_ids | ["R4.2:CONTROL:2:1","R4.2:P:853419","R4.2:P:853421","R4.2:P:853424","R4.2:P:853427","R4.1:MR1:way0:[\"497623\"]","MR1:way0:[\"497623\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 동일 계층은 연구자 판정이다. 정확한 전체 parent span은 미정. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA010 — Job 2:9

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA010 |
| reference_start | 2:9 |
| reference_end | 2:9 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | INTERNAL_TRANSITION |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["2:1–2:10"] |
| related_judgment_id_if_available | [""] |
| linguistic_basis | ותאמר לו אשתו; 아내의 participant/scene change. |
| source_evidence_ids | ["R4.2:CONTROL:2:9","R4.2:P:853525","R4.1:MR1:csf:[\"17\"]","MR1:csf:[\"17\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 2:1–10 단위 안에 있다. 2:1과 병행하는 동일 계층 시작이 아니다. source의 소유 접미사로 referential identity를 새로 계산하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA011 — Job 2:10

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA011 |
| reference_start | 2:10 |
| reference_end | 2:10 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | PARALLEL_ENDING |
| hierarchy_relation | PARALLEL_TO |
| related_reference | ["1:22"] |
| related_judgment_id_if_available | ["HSA008"] |
| linguistic_basis | בכל זאת לא חטא איוב בשפתיו; R4.2 대응 평가절 및 F000020/G0, F001232/G1. |
| source_evidence_ids | ["R4.2:CONTROL:2:10","R4.2:P:853537","R4.2:P:853549","R4.1:MR1:csf:[\"18\"]","MR1:csf:[\"18\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | MR1_EXPLICIT_CLOSURE=false. 절 전체의 발화 문맥과 마지막 평가절을 구분한다. human ending을 MR1에 승격하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA012 — Job 2:11

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA012 |
| reference_start | 2:11 |
| reference_end | 2:11 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | PARAGRAPH_ONSET |
| hierarchy_relation | UNRESOLVED |
| related_reference | [] |
| related_judgment_id_if_available | [] |
| linguistic_basis | שלשת רעי איוב; 2:10 종결 이후의 친구 집단 도입. |
| source_evidence_ids | ["R4.2:CONTROL:2:11","R4.2:P:853553","R4.2:P:853562"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance"] |
| methodological_note | 새 단락 시작으로 연구자가 확정하였다. 아내 사건과 달리 2:1–10 안에 둘러싸이지 않는다. global parent는 미정. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA013 — Job 3:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA013 |
| reference_start | 3:1 |
| reference_end | 3:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | PARAGRAPH_ONSET |
| hierarchy_relation | HIERARCHICALLY_ABOVE |
| related_reference | ["3:2"] |
| related_judgment_id_if_available | ["HSA014"] |
| linguistic_basis | אחרי כן / פתח איוב את פיהו; 시간 및 발화 개시 표면 근거. |
| source_evidence_ids | ["R4.2:CONTROL:3:1","R4.2:P:853609"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance"] |
| methodological_note | MR1 marker 없음. 더 큰 전환의 human onset이며 MR1 사건을 만들거나 규칙을 변경하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA014 — Job 3:2

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA014 |
| reference_start | 3:2 |
| reference_end | 3:2 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["3:1"] |
| related_judgment_id_if_available | ["HSA013"] |
| linguistic_basis | ויען איוב ויאמר; 명시적 CSF. |
| source_evidence_ids | ["R4.2:CONTROL:3:2","R4.2:P:853616","R4.1:MR1:csf:[\"19\"]","MR1:csf:[\"19\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 3:1의 더 큰 전환 안에 놓인 speech-frame onset. 연구자가 판정한 포함 관계만 기록한다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA015 — Job 27:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA015 |
| reference_start | 27:1 |
| reference_end | 27:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["29:1"] |
| related_judgment_id_if_available | ["HSA016"] |
| linguistic_basis | ויסף ... שאת משלו ויאמר; 같은 언어학적 기능의 병행 발화 시작. |
| source_evidence_ids | ["R4.2:CONTROL:27:1","R4.2:P:857979","R4.1:MR1:csf:[\"39\"]","MR1:csf:[\"39\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | not macro-level does not mean subordinate. whole-book macro boundary가 아니라는 이유로 하위 단위라 하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA016 — Job 29:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA016 |
| reference_start | 29:1 |
| reference_end | 29:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["27:1"] |
| related_judgment_id_if_available | ["HSA015"] |
| linguistic_basis | ויסף ... שאת משלו ויאמר; 같은 언어학적 기능의 병행 발화 시작. |
| source_evidence_ids | ["R4.2:CONTROL:29:1","R4.2:P:858357","R4.1:MR1:csf:[\"41\"]","MR1:csf:[\"41\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | not macro-level does not mean subordinate. whole-book macro boundary가 아니라는 이유로 하위 단위라 하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA017 — Job 31:40

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA017 |
| reference_start | 31:40 |
| reference_end | 31:40 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_END |
| hierarchy_relation | UNRESOLVED |
| related_reference | [] |
| related_judgment_id_if_available | [] |
| linguistic_basis | תמו דברי איוב; MR1 explicit closure 및 HR1 CASE025. |
| source_evidence_ids | ["R4.2:CONTROL:31:40","R4.2:P:859056","R4.1:MR1:closure:[\"499623\",\"499623\",\"תממ+דבר\"]","R4.1:HR1:CASE025","MR1:closure:[\"499623\",\"499623\",\"תממ+דבר\"]","HR1:CASE025"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1","HR1 human-review scope"] |
| methodological_note | 욥 발화의 명확한 끝. S02135를 포함한 모든 source evidence는 독립적으로 보존한다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA018 — Job 32:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA018 |
| reference_start | 32:1 |
| reference_end | 32:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | TRANSITION_COMPONENT |
| hierarchy_relation | UNRESOLVED |
| related_reference | [] |
| related_judgment_id_if_available | [] |
| linguistic_basis | וישבתו ... מענות; MR1 explicit closure 및 HR1 CASE026. |
| source_evidence_ids | ["R4.2:CONTROL:32:1","R4.2:P:859059","R4.2:P:859061","R4.1:MR1:closure:[\"499624\",\"499625\",\"שבת+ענה\"]","R4.1:HR1:CASE026","MR1:closure:[\"499624\",\"499625\",\"שבת+ענה\"]","HR1:CASE026"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1","HR1 human-review scope"] |
| methodological_note | 이전 answering/debate 관계의 종료. 욥 종결과 엘리후 도입 사이의 전환 구성요소이며 exact parent는 판정하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA019 — Job 32:2

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA019 |
| reference_start | 32:2 |
| reference_end | 32:5 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | NARRATIVE_INTRODUCTION |
| hierarchy_relation | UNRESOLVED |
| related_reference | [] |
| related_judgment_id_if_available | [] |
| linguistic_basis | אליהוא בן ברכאל ...; 32:2–5의 참여자 및 서술 도입; HR1 CASE027. |
| source_evidence_ids | ["R4.2:CONTROL:32:2","R4.2:CONTROL:32:3","R4.2:CONTROL:32:4","R4.2:CONTROL:32:5","R4.2:P:859068","R4.2:P:859069","R4.2:P:859085","R4.2:P:859087","R4.2:P:859089","R4.2:P:859098","R4.1:HR1:CASE027","HR1:CASE027"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","HR1 human-review scope"] |
| methodological_note | 엘리후의 narrative introduction. 32:6 실제 발화 시작과 구별하며 exact parent를 강제하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA020 — Job 32:6

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA020 |
| reference_start | 32:6 |
| reference_end | 32:6 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["34:1","35:1","36:1"] |
| related_judgment_id_if_available | ["HSA021","HSA022","HSA023"] |
| linguistic_basis | ויען ... ויאמר / ויסף ... ויאמר; 엘리후 네 연설의 병행 시작. |
| source_evidence_ids | ["R4.2:CONTROL:32:6","R4.2:P:859108","R4.1:MR1:csf:[\"43\"]","MR1:csf:[\"43\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 네 시작은 연구자가 동일 계층 sibling으로 판정하였다. 34:1/35:1/36:1을 32:6의 하위 발화로 두지 않는다. marker family만으로 이 관계를 계산하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA021 — Job 34:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA021 |
| reference_start | 34:1 |
| reference_end | 34:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["32:6","35:1","36:1"] |
| related_judgment_id_if_available | ["HSA020","HSA022","HSA023"] |
| linguistic_basis | ויען ... ויאמר / ויסף ... ויאמר; 엘리후 네 연설의 병행 시작. |
| source_evidence_ids | ["R4.2:CONTROL:34:1","R4.2:P:859489","R4.1:MR1:csf:[\"46\"]","MR1:csf:[\"46\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 네 시작은 연구자가 동일 계층 sibling으로 판정하였다. 34:1/35:1/36:1을 32:6의 하위 발화로 두지 않는다. marker family만으로 이 관계를 계산하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA022 — Job 35:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA022 |
| reference_start | 35:1 |
| reference_end | 35:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["32:6","34:1","36:1"] |
| related_judgment_id_if_available | ["HSA020","HSA021","HSA023"] |
| linguistic_basis | ויען ... ויאמר / ויסף ... ויאמר; 엘리후 네 연설의 병행 시작. |
| source_evidence_ids | ["R4.2:CONTROL:35:1","R4.2:P:859772","R4.1:MR1:csf:[\"47\"]","MR1:csf:[\"47\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 네 시작은 연구자가 동일 계층 sibling으로 판정하였다. 34:1/35:1/36:1을 32:6의 하위 발화로 두지 않는다. marker family만으로 이 관계를 계산하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA023 — Job 36:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA023 |
| reference_start | 36:1 |
| reference_end | 36:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["32:6","34:1","35:1"] |
| related_judgment_id_if_available | ["HSA020","HSA021","HSA022"] |
| linguistic_basis | ויען ... ויאמר / ויסף ... ויאמר; 엘리후 네 연설의 병행 시작. |
| source_evidence_ids | ["R4.2:CONTROL:36:1","R4.2:P:859894","R4.1:MR1:csf:[\"48\"]","MR1:csf:[\"48\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 네 시작은 연구자가 동일 계층 sibling으로 판정하였다. 34:1/35:1/36:1을 32:6의 하위 발화로 두지 않는다. marker family만으로 이 관계를 계산하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA024 — Job 37:24

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA024 |
| reference_start | 37:24 |
| reference_end | 37:24 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_END |
| hierarchy_relation | UNRESOLVED |
| related_reference | [] |
| related_judgment_id_if_available | [] |
| linguistic_basis | HR1 CASE028와 38:1 발화 시작 앞의 종결 문맥. |
| source_evidence_ids | ["R4.2:CONTROL:37:24","R4.2:P:860302","R4.1:HR1:CASE028","HR1:CASE028"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","HR1 human-review scope"] |
| methodological_note | 엘리후 마지막 연설의 명확한 끝이라는 human judgment. 37:24 → 38:1 인접성은 직접적인 Elihu→YHWH discourse continuity를 확립하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA025 — Job 38:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA025 |
| reference_start | 38:1 |
| reference_end | 38:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["40:6"] |
| related_judgment_id_if_available | ["HSA028"] |
| linguistic_basis | ויען יהוה ... מן (ה)סערה ויאמר; fuller storm formula. |
| source_evidence_ids | ["R4.2:CONTROL:38:1","R4.2:P:860308","R4.2:P:860309","R4.1:MR1:csf:[\"50\"]","R4.1:HR1:CASE029","MR1:csf:[\"50\"]","HR1:CASE029"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1","HR1 human-review scope"] |
| methodological_note | 여호와 두 주요 연설의 동일 계층 병행 시작. boundary와 discourse continuity는 별개이다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA026 — Job 40:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA026 |
| reference_start | 40:1 |
| reference_end | 40:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | INTERNAL_SPEECH_ONSET |
| hierarchy_relation | CHILD_OF |
| related_reference | ["38:1"] |
| related_judgment_id_if_available | ["HSA025"] |
| linguistic_basis | ויען יהוה את איוב ויאמר; 내부 발화 onset. |
| source_evidence_ids | ["R4.2:CONTROL:40:1","R4.2:P:860805","R4.2:P:860806","R4.1:MR1:csf:[\"52\"]","MR1:csf:[\"52\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 38:1에서 시작하는 첫 여호와 연설 아래에 속한다. 38:1/40:6과 동일 계층이 아니다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA027 — Job 40:3

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA027 |
| reference_start | 40:3 |
| reference_end | 40:3 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["42:1"] |
| related_judgment_id_if_available | ["HSA029"] |
| linguistic_basis | ויען איוב את יהוה ויאמר; 두 욥 응답의 발화 시작. |
| source_evidence_ids | ["R4.2:CONTROL:40:3","R4.2:P:860818","R4.2:P:860819","R4.1:MR1:csf:[\"53\"]","MR1:csf:[\"53\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 연구자가 두 응답을 동일 계층의 병행 단위로 판정하였다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA028 — Job 40:6

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA028 |
| reference_start | 40:6 |
| reference_end | 40:6 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["38:1"] |
| related_judgment_id_if_available | ["HSA025"] |
| linguistic_basis | ויען יהוה ... מן (ה)סערה ויאמר; fuller storm formula. |
| source_evidence_ids | ["R4.2:CONTROL:40:6","R4.2:P:860841","R4.2:P:860842","R4.1:MR1:csf:[\"54\"]","MR1:csf:[\"54\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 여호와 두 주요 연설의 동일 계층 병행 시작. boundary와 discourse continuity는 별개이다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA029 — Job 42:1

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA029 |
| reference_start | 42:1 |
| reference_end | 42:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["40:3"] |
| related_judgment_id_if_available | ["HSA027"] |
| linguistic_basis | ויען איוב את יהוה ויאמר; 두 욥 응답의 발화 시작. |
| source_evidence_ids | ["R4.2:CONTROL:42:1","R4.2:P:861173","R4.2:P:861174","R4.1:MR1:csf:[\"55\"]","MR1:csf:[\"55\"]"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1"] |
| methodological_note | 연구자가 두 응답을 동일 계층의 병행 단위로 판정하였다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA030 — Job 42:7

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA030 |
| reference_start | 42:7 |
| reference_end | 42:7 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | PARAGRAPH_ONSET |
| hierarchy_relation | UNRESOLVED |
| related_reference | [] |
| related_judgment_id_if_available | [] |
| linguistic_basis | Wayhi-positive; SIMPLE_AMR; HR1 CASE030; participant/addressee 구성 변화. |
| source_evidence_ids | ["R4.2:CONTROL:42:7","R4.2:P:861222","R4.2:P:861223","R4.2:P:861224","R4.2:P:861227","R4.2:P:861228","R4.2:P:861236","R4.2:P:861237","R4.1:MR1:way0:[\"500411\"]","R4.1:MR1:csf:[\"56\"]","R4.1:HR1:CASE030","MR1:way0:[\"500411\"]","MR1:csf:[\"56\"]","HR1:CASE030"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance","R4.1","MR1","HR1 human-review scope"] |
| methodological_note | 여호와–욥 교환 이후 새 단락. Wayhi, SIMPLE_AMR, CASE030은 서로 별도의 source evidence로 유지한다. global parent는 미정. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |

### HSA031 — Job 42:16

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA031 |
| reference_start | 42:16 |
| reference_end | 42:16 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_STRUCTURAL_ADJUDICATION |
| structural_function | NO_BOUNDARY |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["42:7"] |
| related_judgment_id_if_available | ["HSA030"] |
| linguistic_basis | 새 구조 단위를 확립할 명시적 언어학적 구조 표지가 없음. |
| source_evidence_ids | ["R4.2:CONTROL:42:16","R4.2:P:861357"] |
| source_layers | ["BHSA2021 snapshot","R4.2","R3c.3/PROV1 exact formal provenance"] |
| methodological_note | 42:7에서 시작한 단락의 연속. 생애 요약이라는 의미/내용만으로 경계를 만들지 않는다. overt participant mention이나 formal occurrence의 부재를 주장하지 않는다. |
| review_status | REVIEWED |
| reviewer_notes | 연구자 HSA1 지시문의 확정 판단. 미검토 범위로 일반화하지 않음. |


## Scope and unresolved review

2:11 is accepted as a new paragraph onset. Job 3–26 dialogue-unit hierarchy remains
incomplete; the supplied 3:1/3:2 judgment is not a review of all dialogue cycles.
Next task: review the Job 3–26 speech-unit structure using the same linguistic-marker
criteria. R4.3 whole-book parentage remains blocked pending that human review.

An explicit participant-entry event may be preserved even when the participant's
referential identity cannot be resolved from the permitted surface evidence.
Event existence and participant identity are separate claims. The human four-messenger
sequence does not overwrite the three source-layer UNRESOLVED identities.

1:22/2:10 remain MR1_EXPLICIT_CLOSURE=false. 3:1 has no MR1 event. Formal evidence
for these human judgments does not change frozen MR1 rules. 42:7 keeps Wayhi-positive,
SIMPLE_AMR and CASE030 distinct; 42:16 is an explicit human NO_BOUNDARY negative control.
37:24 ending and 38:1 onset do not imply direct Elihu→YHWH discourse continuity.

## Methodological principles

1. Linguistic markers have priority over semantic/content shifts.
2. Participant change is scene-transition evidence but not automatic macro hierarchy.
3. Hierarchy level depends on surrounding opening/ending/enclosure evidence.
4. The same linguistic formula may support the same structural function.
5. The same marker family does not automatically imply the same hierarchy level.
6. Absence of an explicit marker can prevent a semantic shift from becoming a structural boundary.
7. Parallel endings may be human-recognized formal evidence without being promoted into MR1 explicit closure rules.
8. Computational evidence and human structural adjudication remain separate.
9. Boundary and discourse continuity are distinct.
10. Not macro-level does not mean subordinate.
