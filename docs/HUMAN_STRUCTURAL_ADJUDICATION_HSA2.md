# HSA2 — Dialogue-cycle and late-Job structural adjudication

Researcher-supplied human judgments, 2026-09-22. Starting HEAD:
`28892b3f0ecab3d42749ab50d8a65bc4aa9e09c5`.
This Markdown and [CSV](HUMAN_STRUCTURAL_ADJUDICATION_HSA2.csv) are a new human
source-of-truth layer. HSA1 remains frozen; no earlier record is overwritten.
REVIEWED is explicitly authorized for these supplied decisions. Closure-candidate
review options are separately UNREVIEWED and do not constitute a target decision.

There are 25 records: 16 cycle speech onsets, 3 separate cycle-onset judgments,
the initial Job speech context, internal 11:4, and 27:1 / 28:1 / 29:1 / 31:40.
The same reference can have two distinct human functions and judgment IDs. The
three cycle-onset judgments are human structural functions; MR1 remains ANSWER+AMR.
JSON target lists contain only expressly supplied direct relations. No inverse or
transitive completion, closing edge after chapter 26, virtual Zophar III, or
whole-book parentage is generated. Named speakers and cycles are human assertions.

Primary anchor atoms remain blank because the human supplied reference-level
judgments. Exact clause/atom/event IDs remain in source links. HSA2:PANEL IDs are
explicit native-reference joins, not new analytical marker identities. Panels keep
all native clauses, co-located MR1/HR1 anchors, participants, formal occurrences and
G0–G6 atom signatures; source rows and locators are expanded without fuzzy matching.

## Recorded judgments

### HSA2-INITIAL — Job 3:1 (HUMAN_INITIAL_SPEECH_CONTEXT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-INITIAL |
| reference_start | 3:1 |
| reference_end | 3:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_INITIAL_SPEECH_CONTEXT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | HIERARCHICALLY_ABOVE |
| related_reference | ["3:2"] |
| related_judgment_id_if_available | ["HSA014"] |
| linguistic_basis | אחרי כן / פתח איוב את פיהו; HSA1 distinction from 3:2 CSF. |
| source_evidence_ids | ["HSA2:PANEL:3:1","R4.2:P:853609"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Independent first Job speech before the dialogue section. Existing HSA1 paragraph/onset and above-3:2 judgment retained; new initial-speech context supplements it. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group |  |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C1-S1 — Job 4:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C1-S1 |
| reference_start | 4:1 |
| reference_end | 4:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["6:1","8:1","9:1","11:1","12:1"] |
| related_judgment_id_if_available | ["HSA2-C1-S2","HSA2-C1-S3","HSA2-C1-S4","HSA2-C1-S5","HSA2-C1-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Eliphaz. |
| source_evidence_ids | ["HSA2:PANEL:4:1","R4.2:P:853815","R4.1:MR1:csf:[\"20\"]","MR1:csf:[\"20\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 1. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Eliphaz |
| human_group | CYCLE_1 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C1-S2 — Job 6:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C1-S2 |
| reference_start | 6:1 |
| reference_end | 6:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["4:1","8:1","9:1","11:1","12:1"] |
| related_judgment_id_if_available | ["HSA2-C1-S1","HSA2-C1-S3","HSA2-C1-S4","HSA2-C1-S5","HSA2-C1-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Job. |
| source_evidence_ids | ["HSA2:PANEL:6:1","R4.2:P:854172","R4.1:MR1:csf:[\"21\"]","MR1:csf:[\"21\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 1. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | CYCLE_1 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C1-S3 — Job 8:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C1-S3 |
| reference_start | 8:1 |
| reference_end | 8:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["4:1","6:1","9:1","11:1","12:1"] |
| related_judgment_id_if_available | ["HSA2-C1-S1","HSA2-C1-S2","HSA2-C1-S4","HSA2-C1-S5","HSA2-C1-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Bildad. |
| source_evidence_ids | ["HSA2:PANEL:8:1","R4.2:P:854577","R4.1:MR1:csf:[\"22\"]","MR1:csf:[\"22\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 1. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Bildad |
| human_group | CYCLE_1 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C1-S4 — Job 9:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C1-S4 |
| reference_start | 9:1 |
| reference_end | 9:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["4:1","6:1","8:1","11:1","12:1"] |
| related_judgment_id_if_available | ["HSA2-C1-S1","HSA2-C1-S2","HSA2-C1-S3","HSA2-C1-S5","HSA2-C1-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Job. |
| source_evidence_ids | ["HSA2:PANEL:9:1","R4.2:P:854739","R4.1:MR1:csf:[\"23\"]","MR1:csf:[\"23\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 1. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | CYCLE_1 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C1-S5 — Job 11:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C1-S5 |
| reference_start | 11:1 |
| reference_end | 11:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["4:1","6:1","8:1","9:1","12:1"] |
| related_judgment_id_if_available | ["HSA2-C1-S1","HSA2-C1-S2","HSA2-C1-S3","HSA2-C1-S4","HSA2-C1-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Zophar. |
| source_evidence_ids | ["HSA2:PANEL:11:1","R4.2:P:855170","R4.1:MR1:csf:[\"24\"]","MR1:csf:[\"24\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 1. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Zophar |
| human_group | CYCLE_1 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C1-S6 — Job 12:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C1-S6 |
| reference_start | 12:1 |
| reference_end | 12:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["4:1","6:1","8:1","9:1","11:1"] |
| related_judgment_id_if_available | ["HSA2-C1-S1","HSA2-C1-S2","HSA2-C1-S3","HSA2-C1-S4","HSA2-C1-S5"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Job. |
| source_evidence_ids | ["HSA2:PANEL:12:1","R4.2:P:855338","R4.1:MR1:csf:[\"26\"]","MR1:csf:[\"26\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 1. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | CYCLE_1 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C2-S1 — Job 15:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C2-S1 |
| reference_start | 15:1 |
| reference_end | 15:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["16:1","18:1","19:1","20:1","21:1"] |
| related_judgment_id_if_available | ["HSA2-C2-S2","HSA2-C2-S3","HSA2-C2-S4","HSA2-C2-S5","HSA2-C2-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Eliphaz. |
| source_evidence_ids | ["HSA2:PANEL:15:1","R4.2:P:855909","R4.1:MR1:csf:[\"27\"]","MR1:csf:[\"27\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 2. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Eliphaz |
| human_group | CYCLE_2 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C2-S2 — Job 16:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C2-S2 |
| reference_start | 16:1 |
| reference_end | 16:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["15:1","18:1","19:1","20:1","21:1"] |
| related_judgment_id_if_available | ["HSA2-C2-S1","HSA2-C2-S3","HSA2-C2-S4","HSA2-C2-S5","HSA2-C2-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Job. |
| source_evidence_ids | ["HSA2:PANEL:16:1","R4.2:P:856174","R4.1:MR1:csf:[\"28\"]","MR1:csf:[\"28\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 2. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | CYCLE_2 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C2-S3 — Job 18:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C2-S3 |
| reference_start | 18:1 |
| reference_end | 18:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["15:1","16:1","19:1","20:1","21:1"] |
| related_judgment_id_if_available | ["HSA2-C2-S1","HSA2-C2-S2","HSA2-C2-S4","HSA2-C2-S5","HSA2-C2-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Bildad. |
| source_evidence_ids | ["HSA2:PANEL:18:1","R4.2:P:856464","R4.1:MR1:csf:[\"29\"]","MR1:csf:[\"29\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 2. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Bildad |
| human_group | CYCLE_2 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C2-S4 — Job 19:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C2-S4 |
| reference_start | 19:1 |
| reference_end | 19:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["15:1","16:1","18:1","20:1","21:1"] |
| related_judgment_id_if_available | ["HSA2-C2-S1","HSA2-C2-S2","HSA2-C2-S3","HSA2-C2-S5","HSA2-C2-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Job. |
| source_evidence_ids | ["HSA2:PANEL:19:1","R4.2:P:856608","R4.1:MR1:csf:[\"30\"]","MR1:csf:[\"30\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 2. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | CYCLE_2 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C2-S5 — Job 20:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C2-S5 |
| reference_start | 20:1 |
| reference_end | 20:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["15:1","16:1","18:1","19:1","21:1"] |
| related_judgment_id_if_available | ["HSA2-C2-S1","HSA2-C2-S2","HSA2-C2-S3","HSA2-C2-S4","HSA2-C2-S6"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Zophar. |
| source_evidence_ids | ["HSA2:PANEL:20:1","R4.2:P:856832","R4.1:MR1:csf:[\"31\"]","MR1:csf:[\"31\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 2. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Zophar |
| human_group | CYCLE_2 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C2-S6 — Job 21:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C2-S6 |
| reference_start | 21:1 |
| reference_end | 21:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["15:1","16:1","18:1","19:1","20:1"] |
| related_judgment_id_if_available | ["HSA2-C2-S1","HSA2-C2-S2","HSA2-C2-S3","HSA2-C2-S4","HSA2-C2-S5"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Job. |
| source_evidence_ids | ["HSA2:PANEL:21:1","R4.2:P:857027","R4.1:MR1:csf:[\"32\"]","MR1:csf:[\"32\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 2. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | CYCLE_2 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C3-S1 — Job 22:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C3-S1 |
| reference_start | 22:1 |
| reference_end | 22:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["23:1","25:1","26:1"] |
| related_judgment_id_if_available | ["HSA2-C3-S2","HSA2-C3-S3","HSA2-C3-S4"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Eliphaz. |
| source_evidence_ids | ["HSA2:PANEL:22:1","R4.2:P:857284","R4.1:MR1:csf:[\"34\"]","MR1:csf:[\"34\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 3. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Eliphaz |
| human_group | CYCLE_3 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C3-S2 — Job 23:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C3-S2 |
| reference_start | 23:1 |
| reference_end | 23:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["22:1","25:1","26:1"] |
| related_judgment_id_if_available | ["HSA2-C3-S1","HSA2-C3-S3","HSA2-C3-S4"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Job. |
| source_evidence_ids | ["HSA2:PANEL:23:1","R4.2:P:857514","R4.1:MR1:csf:[\"36\"]","MR1:csf:[\"36\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 3. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | CYCLE_3 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C3-S3 — Job 25:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C3-S3 |
| reference_start | 25:1 |
| reference_end | 25:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["22:1","23:1","26:1"] |
| related_judgment_id_if_available | ["HSA2-C3-S1","HSA2-C3-S2","HSA2-C3-S4"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Bildad. |
| source_evidence_ids | ["HSA2:PANEL:25:1","R4.2:P:857847","R4.1:MR1:csf:[\"37\"]","MR1:csf:[\"37\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 3. Human cycle membership does not redefine the MR1 marker type. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Bildad |
| human_group | CYCLE_3 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-C3-S4 — Job 26:1 (HUMAN_SPEECH_UNIT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-C3-S4 |
| reference_start | 26:1 |
| reference_end | 26:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_SPEECH_UNIT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["22:1","23:1","25:1"] |
| related_judgment_id_if_available | ["HSA2-C3-S1","HSA2-C3-S2","HSA2-C3-S3"] |
| linguistic_basis | Historical ANSWER+AMR formula; researcher-adjudicated speaker position Job. |
| source_evidence_ids | ["HSA2:PANEL:26:1","R4.2:P:857892","R4.1:MR1:csf:[\"38\"]","MR1:csf:[\"38\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same-level parallel speech unit within Cycle 3. Final Job speech onset within incomplete third cycle. No closing edge is inferred after chapter 26; 26:1 remains ANSWER+AMR, unlike 27:1 TAKE_MASHAL+AMR. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | CYCLE_3 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-CYCLE-1 — Job 4:1 (HUMAN_CYCLE_ONSET)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-CYCLE-1 |
| reference_start | 4:1 |
| reference_end | 4:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_CYCLE_ONSET |
| structural_function | DIALOGUE_CYCLE_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["15:1","22:1"] |
| related_judgment_id_if_available | ["HSA2-CYCLE-2","HSA2-CYCLE-3"] |
| linguistic_basis | Same MR1 ANSWER+AMR formula + recurring speaker-position pattern + human adjudication. |
| source_evidence_ids | ["HSA2:PANEL:4:1","R4.2:P:853815","R4.1:MR1:csf:[\"20\"]","MR1:csf:[\"20\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Six reviewed speeches: Eliphaz → Job → Bildad → Job → Zophar → Job. Cycles 1 and 2 repeat this speaker sequence by human judgment. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker |  |
| human_group | CYCLE_1 |
| higher_order_function | DIALOGUE_CYCLE_ONSET |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-CYCLE-2 — Job 15:1 (HUMAN_CYCLE_ONSET)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-CYCLE-2 |
| reference_start | 15:1 |
| reference_end | 15:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_CYCLE_ONSET |
| structural_function | DIALOGUE_CYCLE_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["4:1","22:1"] |
| related_judgment_id_if_available | ["HSA2-CYCLE-1","HSA2-CYCLE-3"] |
| linguistic_basis | Same MR1 ANSWER+AMR formula + recurring speaker-position pattern + human adjudication. |
| source_evidence_ids | ["HSA2:PANEL:15:1","R4.2:P:855909","R4.1:MR1:csf:[\"27\"]","MR1:csf:[\"27\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Six reviewed speeches: Eliphaz → Job → Bildad → Job → Zophar → Job. Cycles 1 and 2 repeat this speaker sequence by human judgment. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker |  |
| human_group | CYCLE_2 |
| higher_order_function | DIALOGUE_CYCLE_ONSET |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-CYCLE-3 — Job 22:1 (HUMAN_CYCLE_ONSET)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-CYCLE-3 |
| reference_start | 22:1 |
| reference_end | 22:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_CYCLE_ONSET |
| structural_function | DIALOGUE_CYCLE_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["4:1","15:1"] |
| related_judgment_id_if_available | ["HSA2-CYCLE-1","HSA2-CYCLE-2"] |
| linguistic_basis | Same MR1 ANSWER+AMR formula + recurring speaker-position pattern + human adjudication. |
| source_evidence_ids | ["HSA2:PANEL:22:1","R4.2:P:857284","R4.1:MR1:csf:[\"34\"]","MR1:csf:[\"34\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Third cycle exists and is structurally incomplete relative to cycles 1 and 2. No corresponding third Zophar speech is present; no virtual unit or missing onset is supplied. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker |  |
| human_group | CYCLE_3 |
| higher_order_function | DIALOGUE_CYCLE_ONSET |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-INTERNAL-11-4 — Job 11:4 (HUMAN_INTERNAL_EXPRESSION)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-INTERNAL-11-4 |
| reference_start | 11:4 |
| reference_end | 11:4 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_INTERNAL_EXPRESSION |
| structural_function | INTERNAL_SPEECH_EXPRESSION |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["11:1"] |
| related_judgment_id_if_available | ["HSA2-C1-S5"] |
| linguistic_basis | Historical SIMPLE_AMR source event remains separate from 11:1 ANSWER+AMR. |
| source_evidence_ids | ["HSA2:PANEL:11:4","R4.1:MR1:csf:[\"25\"]","MR1:csf:[\"25\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Embedded/internal speech expression within the 11:1 speech; not a peer speech-unit onset. Source identity retained. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker |  |
| human_group | CYCLE_1 |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-JOB-27 — Job 27:1 (HUMAN_POST_DIALOGUE_CONTEXT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-JOB-27 |
| reference_start | 27:1 |
| reference_end | 27:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_POST_DIALOGUE_CONTEXT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["29:1"] |
| related_judgment_id_if_available | ["HSA2-JOB-29"] |
| linguistic_basis | ויסף איוב שאת משלו ויאמר; historical TAKE_MASHAL+AMR. |
| source_evidence_ids | ["HSA2:PANEL:27:1","R4.2:P:857979","R4.1:MR1:csf:[\"39\"]","MR1:csf:[\"39\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Same linguistic function and same-level onset as 29:1; begins a Job speech group structurally distinguished from the preceding dialogue cycles. HSA1 peer relation unchanged. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | POST_DIALOGUE_JOB |
| higher_order_function | POST_DIALOGUE_JOB_SPEECH_GROUP_ONSET |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-JOB-29 — Job 29:1 (HUMAN_POST_DIALOGUE_CONTEXT)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-JOB-29 |
| reference_start | 29:1 |
| reference_end | 29:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_POST_DIALOGUE_CONTEXT |
| structural_function | SPEECH_UNIT_ONSET |
| hierarchy_relation | SAME_LEVEL_SIBLING |
| related_reference | ["27:1"] |
| related_judgment_id_if_available | ["HSA2-JOB-27"] |
| linguistic_basis | ויסף איוב שאת משלו ויאמר; historical TAKE_MASHAL+AMR. |
| source_evidence_ids | ["HSA2:PANEL:29:1","R4.2:P:858357","R4.1:MR1:csf:[\"41\"]","MR1:csf:[\"41\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Parallel same-level speech-unit onset; not a child of 27:1. HSA1 judgment retained. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | POST_DIALOGUE_JOB |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-NO-28 — Job 28:1 (HUMAN_CONTINUATION)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-NO-28 |
| reference_start | 28:1 |
| reference_end | 28:1 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_CONTINUATION |
| structural_function | NO_BOUNDARY |
| hierarchy_relation | CONTINUES_WITHIN |
| related_reference | ["27:1"] |
| related_judgment_id_if_available | ["HSA2-JOB-27"] |
| linguistic_basis | No explicit structural onset marker has been established at 28:1. |
| source_evidence_ids | ["HSA2:PANEL:28:1"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Job 28 continues within the speech unit beginning at 27:1. Semantic/content distinctiveness alone is insufficient. This is a human continuation judgment, not an MR1 negative rule. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker |  |
| human_group | POST_DIALOGUE_JOB |
| higher_order_function |  |
| direct_closure_target |  |
| higher_order_terminal_effect |  |

### HSA2-END-31 — Job 31:40 (HUMAN_ENDING_WITH_UNRESOLVED_TARGET)

| Field | Human-authored value |
| --- | --- |
| judgment_id | HSA2-END-31 |
| reference_start | 31:40 |
| reference_end | 31:40 |
| primary_anchor_atom_if_known |  |
| judgment_type | HUMAN_ENDING_WITH_UNRESOLVED_TARGET |
| structural_function | SPEECH_UNIT_END |
| hierarchy_relation | UNRESOLVED |
| related_reference | [] |
| related_judgment_id_if_available | [] |
| linguistic_basis | תמו דברי איוב; MR1 explicit closure and HR1 CASE025. |
| source_evidence_ids | ["HSA2:PANEL:31:40","R4.2:P:859056","R4.1:HR1:CASE025","R4.1:MR1:closure:[\"499623\",\"499623\",\"תממ+דבר\"]","HR1:CASE025","MR1:closure:[\"499623\",\"499623\",\"תממ+דבר\"]"] |
| source_layers | ["BHSA2021 accepted snapshot","MR1 where present","R4.1","R4.2","R3c.3/PROV1","HR1 where present"] |
| methodological_note | Clear speech ending. Does it directly close 29:1 while secondarily terminating the larger 27:1–31:40 group, or directly close the complex beginning at 27:1? Neither target is settled. Local and enclosing effects may coexist. |
| review_status | REVIEWED |
| reviewer_notes | Researcher-supplied HSA2 adjudication; append-only; no automatic closure-target decision. |
| human_speaker | Job |
| human_group | POST_DIALOGUE_JOB |
| higher_order_function |  |
| direct_closure_target | UNRESOLVED |
| higher_order_terminal_effect | UNRESOLVED |

## Closure-target review remains open

A marker may close the immediately active speech unit and simultaneously produce termination at one or more enclosing structural levels.

`direct_closure_target` and `higher_order_terminal_effect` are separate fields.
31:40 is an accepted SPEECH_UNIT_END, but both fields remain UNRESOLVED. A local
closure of 29:1 and enclosing termination of 27:1–31:40 can coexist as review
possibilities. No edge to either opening is settled or silently drawn.

No nearest-opening, chapter-boundary, semantic-topic, commentary, longest-span or
shortest-span heuristic is allowed. Opening משל and ending דבר are reported as
actual source lexemes without inferring semantic equivalence. 1:22/2:10 remain
human parallel endings, not MR1 explicit closures. Comparative controls do not
generate new relations.

Job 3–26 cycle structure is now human-reviewed (6 / 6 / 4; third cycle incomplete).
27:1 / 29:1 remain same-level peers; 28:1 is no boundary. HSA2 appends adjudication
through Job 31. Whole-book R4.3 parentage remains blocked pending the 31:40
closure-target review.
