# MFR.0.1 validation report

Readiness: **MARKER_FIRST_BASELINE_ESTABLISHED** and
**READY_FOR_MARKER_RELATION_HUMAN_REVIEW**.
Technical evidence-base completion does not adjudicate hierarchy or authorize an
R4.4 consumer, tree synthesis or a resolved root.

## A. Git (items 1–5)

Start commit: `3ee008dc59bc507dcb77ff14be5cfcea0643d4c5`. Branch `main`; verified origin
`https://github.com/aqedah/MILAL.git`.
The end commit is the commit containing this report, message
`Establish marker-first reconstruction baseline`. The exact hash, push outcome and
post-push clean-tree state are recorded in the final task response, avoiding a
self-referential hash in this file. Commit/push is authorized by the researcher.

Authority: [exact request](MFR_0_1_RESEARCHER_SOURCE.txt), SHA256
`ab75f17095d735e1b118ed1849dc1d143e01c720e019853eea36b1c8d699ba56`.
Method/spec: [marker-first method](MARKER_FIRST_METHOD.md),
[MFR.0.1 specification](MFR_0_1_SPEC.md), [execution README](README_MILAL_MFR_0_1.md).

## B. Asset provenance (items 6–9)

| reuse_class | count |
| --- | --- |
| CONTAMINATED_OR_UNCLEAR | 164 |
| DERIVED_BLIND_SAFE | 1 |
| OBSERVATION_SAFE | 22 |
| POSTBLIND_ONLY | 171 |

The audit covers all 335 pinned baseline repository files, the
upstream ZIP and 22 raw TF linguistic features. OBSERVATION_SAFE raw features are
the only historical data used in discovery. The inspected old I/O module is marked
DERIVED_BLIND_SAFE but is not imported. Uncertified old executables/fixtures remain
quarantined; CONTAMINATED_OR_UNCLEAR is not a finding that each asset is contaminated.
Historical judgments/docs/configs remain POSTBLIND_ONLY. No old analytical core changed.

## C–F. Job observation, markers, force and relations (items 10–26)

| measure | count |
| --- | --- |
| clauses | 2938 |
| unique clause_atom anchors | 2977 |
| signature rows | 41405 |
| marker candidates | 1120 |
| repeated marker occurrences | 306 |
| singleton explicit occurrences | 814 |
| marker families | 5717 |
| family memberships | 7357 |
| hierarchical-force evidence rows | 1120 |
| coverage candidates | 4092 |
| nested evidence intervals | 4092 |
| relation candidate pairs | 2435 |
| CLOSURE_TARGET_CANDIDATE | 963 |
| COMPETING_RELATIONS | 21 |
| EMBEDDING_CANDIDATE | 5 |
| FORMAL_CORRESPONDENCE_ONLY | 1265 |
| FORMAL_PARALLEL_CANDIDATE | 1475 |
| HIGHER_ORDER_TERMINAL_EFFECT_CANDIDATE | 963 |
| HYPOTAXIS_CANDIDATE | 12 |
| INSUFFICIENT_EVIDENCE | 1 |
| PARATAXIS_CANDIDATE | 22 |
| RESUMPTION_CANDIDATE | 195 |

Relation-label counts overlap: a pair can retain formal, resumption, hypotaxis,
closure and competing possibilities. These are not accepted edges. Marker counts
refer to clause-anchored occurrences with all simultaneous discovery reasons, not
individual word tokens. Signatures cover clauses and atoms at seven resolutions.
Singleton explicit markers are preserved independently of repeated formulas.

Nested rows encode exact half-open intervals of the ordered marker inventory and
its full family membership table. This is lossless factorization, not deletion of
internal markers. No coverage winner, hierarchical-force score, selected relation,
root, tree or strict/macro preclassification is present.

## G. Job post-blind controls (items 27–32)

All controls below are lookups performed after five independent blind freezes.
They do not seed extraction or family membership. Detailed raw phrase/word/atom
identities and surfaces are retained in output 28.

| reference | markers | constructions | relations |
| --- | --- | --- | --- |
| 1:6 | 4 | BE_TEMPORAL_CONSTRUCTION, DOMAIN_CONFIGURATION_CHANGE, FORMULA_ADJUNCT_EXPANSION, REPEATED_CLAUSE_FORMULA, REPEATED_SEQUENCE_CONFIGURATION, TEMPORAL_FRAME | COMPETING_RELATIONS, EMBEDDING_CANDIDATE, FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, HYPOTAXIS_CANDIDATE, PARATAXIS_CANDIDATE, RESUMPTION_CANDIDATE |
| 1:13 | 1 | BE_TEMPORAL_CONSTRUCTION, FORMULA_ADJUNCT_EXPANSION, REPEATED_CLAUSE_FORMULA, TEMPORAL_FRAME | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE |
| 2:1 | 5 | BE_TEMPORAL_CONSTRUCTION, FORMULA_ADJUNCT_EXPANSION, REPEATED_CLAUSE_FORMULA, REPEATED_SEQUENCE_CONFIGURATION, TEMPORAL_FRAME | COMPETING_RELATIONS, EMBEDDING_CANDIDATE, FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, HYPOTAXIS_CANDIDATE, PARATAXIS_CANDIDATE, RESUMPTION_CANDIDATE |
| 2:11 | 2 | EXPLICIT_SUBJECT_CONFIGURATION_SHIFT |  |
| 3:1 | 1 | EXPLICIT_SUBJECT_CONFIGURATION_SHIFT, OPEN_MOUTH_CONSTRUCTION, TEMPORAL_FRAME |  |
| 27:1 | 3 | ADD_PROVERB_SPEECH, DOMAIN_CONFIGURATION_CHANGE, EXPLICIT_SUBJECT_CONFIGURATION_SHIFT, REPEATED_CLAUSE_FORMULA, REPEATED_SEQUENCE_CONFIGURATION, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | COMPETING_RELATIONS, EMBEDDING_CANDIDATE, FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, HYPOTAXIS_CANDIDATE, PARATAXIS_CANDIDATE, RESUMPTION_CANDIDATE |
| 29:1 | 3 | ADD_PROVERB_SPEECH, REPEATED_CLAUSE_FORMULA, REPEATED_SEQUENCE_CONFIGURATION, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | COMPETING_RELATIONS, EMBEDDING_CANDIDATE, FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, HYPOTAXIS_CANDIDATE, PARATAXIS_CANDIDATE, RESUMPTION_CANDIDATE |
| 31:40 | 2 | EXPLICIT_CESSATION, EXPLICIT_SUBJECT_CONFIGURATION_SHIFT | CLOSURE_TARGET_CANDIDATE, HIGHER_ORDER_TERMINAL_EFFECT_CANDIDATE |
| 32:1 | 2 | DOMAIN_CONFIGURATION_CHANGE, EXPLICIT_CESSATION, EXPLICIT_SUBJECT_CONFIGURATION_SHIFT, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | CLOSURE_TARGET_CANDIDATE, HIGHER_ORDER_TERMINAL_EFFECT_CANDIDATE |
| 32:2 | 3 | EXPLICIT_SUBJECT_CONFIGURATION_SHIFT |  |
| 32:6 | 5 | DOMAIN_CONFIGURATION_CHANGE, EXPLICIT_SUBJECT_CONFIGURATION_SHIFT, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, RESUMPTION_CANDIDATE |
| 34:1 | 2 | DOMAIN_CONFIGURATION_CHANGE, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, RESUMPTION_CANDIDATE |
| 35:1 | 2 | DOMAIN_CONFIGURATION_CHANGE, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, RESUMPTION_CANDIDATE |
| 36:1 | 2 | DOMAIN_CONFIGURATION_CHANGE, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE |
| 37:24 | 0 |  |  |
| 38:1 | 2 | DOMAIN_CONFIGURATION_CHANGE, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, RESUMPTION_CANDIDATE |
| 40:1 | 2 | DOMAIN_CONFIGURATION_CHANGE, EXPLICIT_SUBJECT_CONFIGURATION_SHIFT, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, RESUMPTION_CANDIDATE |
| 40:3 | 2 | DOMAIN_CONFIGURATION_CHANGE, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, RESUMPTION_CANDIDATE |
| 40:6 | 2 | DOMAIN_CONFIGURATION_CHANGE, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, RESUMPTION_CANDIDATE |
| 42:1 | 2 | DOMAIN_CONFIGURATION_CHANGE, EXPLICIT_SUBJECT_CONFIGURATION_SHIFT, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE, RESUMPTION_CANDIDATE |
| 42:7 | 5 | DOMAIN_CONFIGURATION_CHANGE, EXPLICIT_ADDRESSEE_COMPLEMENT_CONFIGURATION_SHIFT, EXPLICIT_SUBJECT_CONFIGURATION_SHIFT, REPEATED_CLAUSE_FORMULA, REPORTED_SPEECH_FORMULA, SPEECH_PREDICATE_CONSTRUCTION | FORMAL_CORRESPONDENCE_ONLY, FORMAL_PARALLEL_CANDIDATE |
| 42:16 | 1 | EXPLICIT_SUBJECT_CONFIGURATION_SHIFT, TEMPORAL_FRAME |  |

The review compares the formal families/configuration differences at 1:6/1:13/2:1,
independent repetition at 27:1/29:1, cessation evidence at 31:40, raw constructions
at 32:1, expansion differences at 38:1/40:1/40:6, and constructions at 42:7/42:16.
No SPEECH_UNIT_END, TRANSITION_COMPONENT, epilogue or NO_BOUNDARY judgment is a blind
input. Formal recovery is not confirmation of the historical function or level.
Job 37:24 has no marker under these generic rules (NOT_RECOVERED); its raw clauses
remain in the complete observation inventory. It is not forced into the candidate
list merely because it is a historical control location.

## H. Cross-corpus method controls (items 33–38)

| scope | clauses | markers | families | pairs | cross_book |
| --- | --- | --- | --- | --- | --- |
| daniel_ezra | 2556 | 1199 | 5405 | 3216 | 251 |
| death | 16275 | 9481 | 34563 | 161034 | 108865 |
| job | 2938 | 1120 | 5717 | 2435 | 0 |
| pentateuch | 21181 | 11861 | 40393 | 206996 | 123884 |
| prophets | 22078 | 10606 | 38660 | 136068 | 83929 |

Total cross-book candidate pairs across independent scopes: **316929**.

### Pentateuch DSF/EDSF

| book | reference | status | markers | cross_book_cases |
| --- | --- | --- | --- | --- |
| Exodus | 4:19 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 3 | 12 |
| Exodus | 12:1 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 2 | 19 |
| Leviticus | 1:1 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 3 | 23 |
| Leviticus | 16:1 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 3 | 11 |
| Leviticus | 25:1 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 2 | 17 |
| Numeri | 1:1 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 3 | 11 |
| Numeri | 3:14 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 2 | 11 |
| Numeri | 9:1 | PARTIALLY_CONSISTENT | 3 | 11 |
| Numeri | 20:23 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 2 | 10 |
| Numeri | 33:50 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 2 | 11 |
| Numeri | 35:1 | PARTIALLY_CONSISTENT | 2 | 11 |
| Deuteronomium | 32:48 | CONSISTENT_WITH_JIN_FORMAL_FAMILY | 2 | 21 |

### Prophetic superscriptions

| book | reference | status | markers | cross_book_cases |
| --- | --- | --- | --- | --- |
| Jesaia | 1:1 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 2 | 1 |
| Hosea | 1:1 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 2 | 1 |

### Death/resumption

| book | reference | status | markers | cross_book_cases |
| --- | --- | --- | --- | --- |
| Deuteronomium | 34:5 | RECOVERED_PARTIAL_CORRESPONDENCE | 1 | 3 |
| Josua | 1:1 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 3 | 4 |
| Josua | 24:29 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 2 | 6 |
| Josua | 24:30 | NOT_RECOVERED | 0 | 0 |
| Judices | 1:1 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 5 | 8 |
| Samuel_I | 31:4 | RECOVERED_PARTIAL_CORRESPONDENCE | 3 | 0 |
| Samuel_I | 31:5 | RECOVERED_PARTIAL_CORRESPONDENCE | 3 | 4 |
| Samuel_I | 31:6 | RECOVERED_PARTIAL_CORRESPONDENCE | 1 | 3 |
| Samuel_II | 1:1 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 2 | 6 |

### Daniel/Ezra

| book | reference | status | markers | cross_book_cases |
| --- | --- | --- | --- | --- |
| Daniel | 9:1 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 1 | 1 |
| Daniel | 9:2 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 4 | 1 |
| Esra | 1:1 | RECOVERED_STRONG_FORMAL_CORRESPONDENCE | 4 | 2 |

All twelve Pentateuch locations contain generically recovered DSF construction
evidence. Jin's supplied Pattern 1–5 values are loaded post-blind only. Exact adjunct
pattern agreement is descriptive; differing BHSA phrase segmentation or additional
context adjuncts is retained as PARTIALLY_CONSISTENT. Pattern-4 recurrence across
books and Num 3:14 do not assign a common level.
Num 9:1 has two raw BHSA Time phrases where the supplied pattern groups one;
Num 35:1 has one raw BHSA Loca phrase containing the two prepositional expressions
where the supplied pattern lists double Loca. Both remain PARTIALLY_CONSISTENT.

Isa 1:1/Hos 1:1 retain a cross-book formal comparison, not an automatic direct sibling
decision. Death/after-death constructions preserve formal family evidence separately
from temporal resumption. Daniel/Ezra comparisons retain actual linguistic candidates
and differences; book metadata cannot reject them. A representable hypotaxis
possibility is not a selected relation. Complete candidate labels and distances
remain in each independently frozen relation table.
All three after-death formulas and the three specified death-to-resumption pairs
are recovered. Josh 24:30 is retained as raw burial context without a marker
(NOT_RECOVERED). Broad lexical and four-clause context matches also produce extra
candidate links; these do not resolve participant identity or prove event identity.
For example, the Deut 34:5 / Judg 1:1 candidate preserves shared contextual lexical
evidence but is not a claim that Moses and Joshua are the same participant or that
their deaths are the same event. Control recovery checks recall and representability,
not precision of all corpus-wide candidates. Human adjudication must assess these
additional links. No known-reference exclusion is used to hide them.

## I. Historical marker-first provenance audit (items 39–42)

| classification | count |
| --- | --- |
| EVIDENCE_FIRST_VALID_REVIEW_PATH | 0 |
| EVIDENCE_FIRST_BUT_NEEDS_READJUDICATION | 0 |
| STRUCTURE_FIRST_CONTAMINATION | 0 |
| PROVENANCE_UNCLEAR | 250 |

| comparison_status | count |
| --- | --- |
| BLIND_EVIDENCE_PARTIALLY_SUPPORTS_HISTORICAL | 93 |
| HISTORICAL_RELATION_NOT_RECOVERED | 16 |
| INSUFFICIENT | 137 |
| MULTIPLE_RELATIONS_REMAIN | 4 |

All 250 canonical historical relation records are retained
exactly with member path/hash, row number and original record. An absent historical
blind-discovery chronology is PROVENANCE_UNCLEAR and requires marker-first
readjudication; it is not retroactive proof of structure-first contamination.
Original evidence IDs, source stages and human rationales remain present; the
independence and order of the full historical discovery-to-adjudication chain are
not established by those links alone. Current marker matches cannot establish
the temporal order of earlier research.
No relation is silently deleted, marked false or migrated. Output 29 additionally
compares 56 HSA1/HSA2 judgments through explicit atom/clause
identities, with all original human fields preserved. The complete original JIN.0.9
ZIP and all 538 member hashes are in the package.

## J. Integrity (items 43–50)

Each scope's actual file-read manifest reports human input, structural-label input
and technical-root input counts of zero. Static source/config target-reference
leakage is zero. No same-book/chapter/verse eligibility filter exists; synthetic
metadata changes preserve candidate identities/labels. All five manifests freeze
before known references load, and historical judgments load afterward. Frozen bytes
are verified again after post-blind work.

New human judgments, accepted relations and roots: **0**. Participant arc remains
UNADJUDICATED. R4.4 consumer absent. Existing historical analytical cores and all
335 pinned assets are unchanged. Human fields are blank except
UNREVIEWED in 5717 family review cases.

## K. Validation and package (items 51–56)

Stage tests: **97 PASS**. Full regression: **1957 PASS**,
failures/errors/skips all zero. SYN1–SYN15 cover repeated/expanded/singleton forms,
cross-book and different-form configurations, resumption, nesting, alternative
coverage, competing relations and outside-scope uncertainty. All **55 run gates**
have negative tests; **3 external release gates** pass for byte determinism, full
regression and skip zero. Syntax/static/source-guard tests pass.

Independent Windows A/B executions produce identical ZIP bytes. ZIP CRC, duplicate
names, every file hash, all five blind manifests/hash files and final manifest
verify. The independent verifier checks original historical records and source
hashes as well as blank review fields and zero accepted output relations.
Manual spot checks covered every required Job and external control location,
including source phrases, family correspondence and competing candidate evidence.
No empirical Termux validation is claimed.

Manual inspection of the first diagnostic real runs exposed three generic
co-occurrence errors. Four regression tests were first observed failing, then the
draft MFR rules were corrected: after-death uses adjacent after/death content in
the actual Time phrase (including nominal `MWT/`); first-year requires ordered
year/one content in Time; DSF uses the explicit local speaker and complementary
segment head instead of a later subject or a name inside a title. Added positive
and negative tests also cover the immediate call/speech construction. Job 42:16
remains a marker without being mislabeled after-death; Num 1:1 is not first-year.
The corrected death gate requires all three after-death formulas and all three
specified cross-book temporal-resumption pairs. Full regression, synthetic, real
A/B runs and independent verification were repeated after these corrections.
No reference-specific detection patch or historical-core modification was made.

Final ZIP: `results/mfr01_real_corrected_20260924_a_results.zip`.
SHA256: **`a0904cb11931790e6d78d53f5f67731aba067c5feca4ed50dd10eb11e268b05d`**.
ZIP members: 103.
Independent verification: `results/mfr01_real_corrected_20260924_a_independent_verification.json`.
Earlier diagnostic MFR artifacts are not release artifacts.

## L. Readiness and next scope (items 57–58)

**MARKER_FIRST_BASELINE_ESTABLISHED**.
**READY_FOR_MARKER_RELATION_HUMAN_REVIEW**.
Next: MFR.0.2 — Human Marker-Family and Relation Adjudication. Only after that,
MFR.0.3 — Adjudicated Relation → Text-Hierarchy Assembly. Plot/narrative/rhetoric
integration follows hierarchy assembly. No R4.4 implementation readiness is claimed.

Required upload: final complete MFR.0.1 results ZIP. Optional: this report, the human
review packet and selected CSVs. The ZIP already includes the complete output package.

## Changed files

`.gitattributes` preserves exact researcher-source bytes. The current HANDOFF
entry changes; historical handoff entries remain intact. No historical JIN document
is rewritten. Results, TF data, logs and local verification scripts are ignored
and excluded from the commit.

- `.gitattributes`
- `config/mfr_0_1_blind_rules.json`
- `config/mfr_0_1_controls.json`
- `config/mfr_0_1_job.json`
- `docs/HANDOFF.md`
- `docs/MARKER_FIRST_METHOD.md`
- `docs/MFR_0_1_RESEARCHER_SOURCE.txt`
- `docs/MFR_0_1_SPEC.md`
- `docs/MFR_0_1_VALIDATION_REPORT.md`
- `docs/README_MILAL_MFR_0_1.md`
- `scripts/run_milal_mfr_0_1_termux.sh`
- `scripts/run_milal_mfr_0_1_windows.ps1`
- `src/milal_mfr_blind.py`
- `src/milal_mfr_common.py`
- `src/milal_mfr_controls.py`
- `src/milal_mfr_coverage.py`
- `src/milal_mfr_families.py`
- `src/milal_mfr_force_evidence.py`
- `src/milal_mfr_gates.py`
- `src/milal_mfr_marker_discovery.py`
- `src/milal_mfr_observation.py`
- `src/milal_mfr_pipeline.py`
- `src/milal_mfr_postblind.py`
- `src/milal_mfr_provenance.py`
- `src/milal_mfr_relation_candidates.py`
- `src/milal_mfr_selftest.py`
- `src/milal_mfr_signatures.py`
- `src/milal_mfr_synthetic.py`
- `tests/test_mfr_0_1.py`
