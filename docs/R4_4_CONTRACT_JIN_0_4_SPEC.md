# JIN.0.4 — Contextual Human Adjudication Batch 1

Authority: [exact researcher request](R4_4_CONTRACT_JIN_0_4_RESEARCHER_SOURCE.txt).
Baseline: `1781b36f52b9d0b47c1acfefbd07bb06411129a3`.
This is an append-only transcription stage for seven explicitly supplied human
judgments. No new detector, hierarchy consumer or whole-queue adjudication is authorized.
Real execution consumes frozen JIN.0.3; it does not rerun BHSA or change blind evidence.

## Input and identity

The exact upstream ZIP SHA256 is
`5412da317a698cbc506114464d2c7ed328f5e65e1b3af9511cf1eff224070387`.
Verify ZIP CRC, complete manifest, exact researcher bytes and 217 frozen repository pins.
Config `config/jin_human_batch1.json` transcribes B1–B7 and their verbatim source sections.
Source references are resolved to explicit historical relation IDs and neutral locus IDs
in that config, then checked against the frozen comparison and actual historical row.
No fuzzy Hebrew/span matching. Missing identity, changed historical member hash, row,
accepted-source status or explicit-control hypothesis fails. Exact pair/context IDs and
contextual review case IDs link each supplied judgment to its evidence.

Symmetric historical relations have two stored oriented IDs. B1 reuses
E:1e1cac2f463240ff6822 and E:4890d3199e4962a2706c; B7 reuses
E:45e7bca183e3cc4ce8b5 and E:d7914344ad4832c8be9e. Both source IDs
are preserved. There is one Batch judgment per symmetric pair, no replacement ID,
no canonical merge and no invented parent. B6 reuses E:94026f426d623f2921a2
with original 40:1 CHILD_OF 38:1 direction. Three relation-level duplicate creations
are avoided; five existing ID references are reaffirmed. New unique edges = 0.

## Human decisions and review state

| Case | Supplied judgment | Mother | Projection |
|---|---|---|---|
| B1: 1:6 / 2:1 | PARATACTIC | NONE | MACRO_TEXTUAL |
| B2: 1:13 / 1:6 | REQUIRES_ADDITIONAL_CONTEXT | NONE | UNRESOLVED |
| B3: 3:1 / 3:2 | REQUIRES_ADDITIONAL_CONTEXT | NONE | UNRESOLVED |
| B4: 2:11 | INSUFFICIENT_EVIDENCE | NONE | NO_MACRO_PROJECTION |
| B5: 32:1 | INSUFFICIENT_EVIDENCE | NONE | NO_MACRO_PROJECTION |
| B6: 40:1 / 38:1 | HYPOTACTIC | 38:1 | MACRO_TEXTUAL |
| B7: 38:1 / 40:6 | PARATACTIC | NONE | MACRO_TEXTUAL |

Only B2/B3 receive HUMAN_DEFERRED. Their historical ACCEPTED_SOURCE rows remain;
the latest review status is REOPENED_FOR_ADDITIONAL_LINGUISTIC_AUDIT. They are
neither REJECTED nor SUPERSEDED. Consumer precedence is documented but never executed.
B4/B5 preserve paragraph, participant-introduction, transition and composition facts
inside frozen source history; none substitutes for a textual mother. Their single-mother
target remains UNRESOLVED_PENDING_FOCUSED_AUDIT, never DIRECT_TEXTUAL_PARENT_NOT_REQUIRED.

B1/B6/B7 evidence_sufficient=true is researcher-supplied. No missing human explanation,
review time, role or unsupplied review-field value is invented. No duplicated canonical
REVIEW_FIELDS definition is introduced. This new transcription schema records only the
supplied decisions and provenance; upstream 206 review rows remain byte-identical.
B6/B7's expanded-formula and 38:3/40:7 rationale is explicitly human authority, not
claimed as a new computational detection from the JIN.0.3 +/-3 window.

## Calibration and next scopes

Two positive macro parataxis controls and one positive macro hypotaxis control are
human-supplied. Four unresolved controls stay unresolved. Explicit-subordination IDs
JP:JT0037:499628:499631 and JP:JT0037:499629:499631 are copied with their source
hypotheses as EXPLICIT_SUBORDINATION_POSITIVE_CONTROL_FOR_REVIEW, UNREVIEWED,
human_accepted=false. No automatic clause-hypotaxis acceptance.

The next plan, without execution or answers, contains JOB_1_13_MOTHER_AUDIT
(1:4–5, 1:6, 1:12, 1:13, 1:22, 2:1), JOB_3_1_2_SPEECH_FRAME_AUDIT
(generic whole-Job temporal/narrative speech-event frame to CSF/quoted onset,
פתח ... פה and אמר/ענה), and MACRO_PARENT_AUDIT_2_11_32_1
(actual preceding main loci, not their internal subordinate clauses).

## Outputs and validation

Outputs 01–11, 12_gates.csv, 90_run_metadata.json and 99_manifest_sha256.csv follow
the researcher's requested names. 13 preserves exact authority; 14 preserves config.
All 350 upstream files are copied losslessly under history/jin_0_3/. No source rewrite.
05 lists the two reopened relations; 06 lists both deferred and both insufficient cases,
with their different decision states intact. 07 remains an unaccepted review control.

Computed gates cover each B case, source/identity preservation, duplicate prevention,
explicit controls, next scope, no consumer, no Q1–Q9 approval and participant state.
Every gate has a negative test. Manifest and external deterministic/full-regression
gates have independent mutations. Validate syntax, unit tests, full regression skip0,
synthetic self-test and packet inspection, then real frozen-source execution and an
independent process rerun; verify whole ZIP equality and all nested manifests.

Readiness: BLOCKED_PENDING_FOCUSED_RELATION_AUDITS, never R4.4 implementation ready.
The request authorizes commit and normal origin/main push after tests/gates pass.
