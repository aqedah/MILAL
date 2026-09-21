# MR1 — Surface Marker Provenance Recovery

Authorized 2026-09-21: implement, test, run synthetic validation, reproduce against
local BHSA 2021, rerun deterministically, compare all four historical CSVs, inspect
controls, then commit/push on successful validation. R4.0 remains on hold until
researcher review of MR1. MR1 is provenance/reproduction only, not hierarchy analysis.

## Source layers

Current execution uses actual Job nodes/features from BHSA 2021 and Text-Fabric
13.1.0. Explicit CLI paths locate data outside Git. Missing files/features,
wrong versions, mismatched source fingerprints, ambiguous identities, incompatible
schemas and input changes stop execution. No historical pipeline loader is executed.

Historical comparison baseline: `C:\py\5.2.5\output_v5_2_5`.
Rule source: `C:\py\5.2.5\job_tf_structure_pipeline_v5_2_5.py`.
Configuration: `C:\py\5.2.5\job_tf_config_v5_2_5.json`.
`config/mr1_job.json` pins exact local SHA256 fingerprints, 77 dependency AST
digests/source line ranges, the used historical configuration subset, and optional
Job-specific regression expectations. These are **current local comparison
fingerprints, not historical acceptance hashes**. v5.2–v5.2.5 marker CSVs were
found byte-identical in recovery; v5.2.5 records BHSA validation COMPLETE and 70/70
historical regressions. No historical process exit-code record was recovered.

Frozen R1.1 and v6.42.12 packages remain unavailable. MR1 does not recover or
rename either package, reconstruct a frozen registry, or accept historical macro
markers. Historical raw BHSA dataset hashes are UNKNOWN_NOT_VERIFIED. Current
file fingerprints and matching output bytes cannot prove historical input bytes.

## Exact historical behavior

The isolated historical module contains only the dependency closure of the four
marker-table writers. Each transcribed global/function/method must match its
source AST digest. The current API adapter makes feature/API errors explicit,
while retaining historical None/default and ordered membership semantics.

Closure: normalized Hebrew lexemes, ordered subsequence, span width **1..2 total
clauses**, shortest span per end-clause/pattern, historical tie-break/order.
Patterns: תמם+דבר, שבת+ענה, כלה+דבר, חדל+דבר, חדל+אמר.

CSF: start domain N; SIMPLE_AMR or historical anchor plus AMR within the next
three clauses; OPEN_MOUTH, TAKE_MASHAL, ANSWER, ADD_SPEECH priorities preserved.
Speaker resolution participates in inclusion. An empty resolver result excludes
the event; a historically generated anonymous PNG speaker is retained. The
historical phrase "unresolved speaker" must not be extended to remove these
anonymous events. Explicit addressee expands csf_profile but belongs to CORE
scope; adjuncts/expanded subject identification can produce SCOPE_EXPANDED.
The exact lookback, complementizer, participant and speaker-propagation behavior
remains in the isolated reproduction dependency closure. This is **historical
v5.2.x CSF event extraction behavior**, not a pure surface-only detector.

Wayhi core: typ Way0, historical finite היה verb, ps=p3/gn=m/nu=sg. The core
finite test excludes blank/NA/infc/infa/ptca/ptcp as the original does. WayX does
not imply Wayhi. Classification remains positive even without framing evidence.
Framing independently examines current plus next three clauses, skipping Q
clauses, for Time/Loca phrases or the temporal auxiliary construction.

Historical `03_job_way0_wayhi.csv` is an audit table of all Way0 candidates, not a table containing only positive Wayhi events.

The temporal-lexeme auxiliary condition checks for a verbal word with a non-empty/non-NA `vt` value according to the historical implementation; MR1 does not strengthen this into a newly imposed finite-only criterion.

Auxiliary temporal lexemes אחר/אחרי/טרם/בטרם must occur in the first three words,
with configured POS prep/advb/conj, and the clause must contain a pos=verb word
with vt outside blank/NA. Infinitives and participles are not additionally excluded.

Regression expectations, never detection inputs: surface 2938, CSF 56, closure 2,
Way0 audit 170, Wayhi-positive 5, negative 165. Positive refs 1:5, 1:6, 1:13, 2:1,
42:7. No rule contains these counts or references.

## Identity, evidence and output contract

The four primary outputs wrap historical fields in `historical_projection` to
keep their historical status visible. The additional historical-schema exports
reproduce every field in original order/UTF-8 BOM/CRLF for optional byte checks.
Historical speaker/participant/classification fields are comparison values only.
No macro hierarchy, macro composition, mother assignment, parentage, final
boundary engine or newly inferred rhetorical/theological labels are produced.
The legacy method named `_macro_subject_profile` is included solely because the
historical participant_set column depends on subject phrase features; it neither
creates nor consumes macro units.

Every primary record has current native clause IDs, ordered clause span and
atom membership, current extractor version, original rule/source hash/lines,
feature evidence locator, and historical file/row/status. Way0 rows preserve
`is_wayhi`, actual verb features and separate lookahead framing evidence.
CSF fields expose historical scope/profile and speaker-resolution source.
Closure fields preserve pattern, textual span and shortest-span result.

`05_clause_atom_marker_links.csv` is one row per event/clause, including surface
inventory rows, with the complete ordered atom list/count/first/last. Multi-atom
clauses are never folded. `10_current_feature_evidence.json` records all queried
feature values (including None), coordinates and ordered API relationships,
including speaker lookbacks and framing lookaheads. Node keys are current BHSA
IDs. Feature snapshots retain actual values instead of inferred missing values.

Comparison joins only explicit keys: surface/Way0 clause_node; closure
start_clause/end_clause/pattern; CSF event_id. The historical CSF CSV does not
contain clause IDs. Its ordinal event_id is not a globally stable native node:
MR1 independently checks ref/formula_end_ref/family/speech_level and all other
fields, but does not claim a supplied historical clause ID or guess one from
text/coordinates. Duplicate keys fail; changed identities never fuzzy-remap.

The audit retains EXACT, FIELD_DIFFERENCE, CURRENT_ONLY, HISTORICAL_ONLY, every
differing field and both values. Count, explicit identity, all-field normalized
row identity, source-data identity and byte identity are separate claims.
Any gate failure publishes a clearly failed diagnostic packet with nonzero exit;
it does not authorize acceptance, follow-on execution or commit/push.

Outputs: 01–04 primary tables (04 named `04_way0_wayhi_reproduction.csv`), 05
links, 06 field audit, 07 rule catalog, 08 summary, 09 computed gates, 10 evidence,
11 control inspection, 20–23 historical-schema projections, 90 metadata, 99 exact
member SHA256 manifest. ZIP timestamps/order are deterministic. No output path or
run timestamp is included in member content. Existing outputs are never overwritten.

## Validation and limits

Each computed gate has a negative mutation, including byte/member corruption for
the manifest. Rule behavior tests cover ordered closure spans, anchor detection,
speaker inclusion, scope distinction, exact Way0 classification, nonfinite
auxiliary verbs, framing exclusions/lookahead, multi-atom mapping and no fuzzy
comparison. Synthetic fixtures are small fabricated regression examples; they
do not establish historical reproducibility. Synthetic API version fields are
explicit simulation, not evidence that Text-Fabric was loaded.

Before real execution: syntax, complete previous regression, MR1 tests, self-test,
and manual synthetic report inspection. Real runs validate expected full scope,
native counts, exact source fingerprints, all-field comparison and two independent
Analyzer instances. A second fresh process verifies every package member and ZIP
bytes. Current input files are hashed again before publication. The manifest is
computed on serialized payload, then regenerated including the gate report and
verified after final serialization, disk writes and ZIP reads; it excludes only
itself. No unconditional manifest success is accepted.

Control inspection includes every clause in Job 1:1–3:1 and 27:1, 29:1, 31:40,
32:1, 32:2, 37:24, 38:1, 40:1, 42:7, 42:16. Controls never create occurrences.
Technical reproduction success is distinct from scholarly acceptance and does
not authorize R4 or modify any frozen R1–R3/PROV1/HR1 core.
