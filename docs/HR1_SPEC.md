# HR1 — Human Review Adjudication Linkage Sidecar

HR1 is a non-analytical linkage record over frozen R3c.3 and PROV1 outputs.
It neither creates R3c.4 nor authorizes R4. Historical ZIPs, identities, hashes,
memberships, genealogy, boundary evidence and extension relations are immutable.
The researcher authorized implementation, synthetic validation, real execution,
and commit/push after complete validation on 2026-09-21.

## Sources and scope

The sole human judgment source is `docs/HUMAN_REVIEW_PILOT_ADJUDICATION.csv`
at commit `a1e2b99b6fb70a56ccd4ba7230998bae69031dc0`. HR1 verifies its exact
bytes against both Git and SHA256. The accepted pilot input fingerprints are:

| Role | SHA256 |
| --- | --- |
| Human CSV | `4fb8c15a9ae530e778122f97c3ffcdcc78ded89f534535e4c7afe5cb2272abe3` |
| R3c.3 ZIP | `5f8239a692a516fd9722d94fb919321d399fad93c3583dd828ac1c1883576981` |
| PROV1 ZIP | `38c6703721e2f9cca590ab96d64d7a2860a3d075e059cabeb2abe9eb6708c482` |

Both archives must pass CRC and member-manifest validation. PROV1 metadata must
name this exact R3c.3 hash; source versions, recorded gate counts and all gate
statuses must agree. These fingerprints and CASE001–030/count controls describe
this accepted pilot, not general Job or MILAL semantics. There is no production
hash override. The separate synthetic builder constructs explicitly labeled
small archives without reading real result ZIPs.

## Exact identity resolution

R3c.3 `02_review_cases.csv` provides case_id, case_type, unit_id, unit_type,
boundary_ref and JSON target_summaries. Each target must match exactly one PROV1
`05_downstream_identity_links.csv` review_unit row by case_id/review_unit_id.
Its summary and original case source row must match R3c.3 exactly. No matching
uses Hebrew text, verse similarity, signature similarity or inferred ID prefixes.

Repeated bundle targets resolve through R3c.3 `03_bundle_definition_context.csv`
bundle_id and PROV1 `02_family_signature_provenance.csv` explicit bundle_ids.
Every linked family gets a locator; explicit members/lineages crosswalk records
are retained. Singleton targets resolve through R3c.3
`05_singleton_definition_context.csv` unit_id. Explicit review_item_id maps to
PROV1 `04_singleton_signature_provenance.csv` review_item_ids and atom_node.
Source event rows match PROV1 `03_refinement_feature_delta.csv` source.source_row
by the exact tuple (parent_family_id, child_level, child_signature_hash,
exemplar_window_id). This includes event-only singletons without a G6 item ID.
Every R3c.3 singleton source row must be represented by the PROV1
review_unit_source crosswalk. Ambiguous or missing required links abort.

Boundary panels resolve by case_id and the complete unit_ids set in R3c.3
`07_boundary_definition_context.csv`. All participants receive their own
evidence/provenance locators, including units also present in other panels.
No boundary participant is replaced by a representative.

The sidecar preserves every PROV1 overlay row, including ones outside the pilot.
Endpoint case lists use explicit bundle IDs. Sequence extension remains an
overlay, never a parent-child refinement relation. CASE007–012 retain the human
dependency annotation and must be connected by explicit overlay relations.
This is one human-recognized extended sequence, not six independent evidences;
the six human assessments still remain six recorded case rows.

## Output schema

| File | Contents |
| --- | --- |
| 01_case_adjudication_links.csv | Entire human row unchanged plus review_unit_id/type, boundary_identity, JSON target_objects, human and R3c.3 locators, extension dependency cases/note |
| 02_case_evidence_locators.csv | case_id, review_unit_id, relationship, link_status, JSON locator for each case target/definition/panel |
| 03_case_provenance_locators.csv | Same locator schema for PROV1 crosswalk/family/singleton/refinement/identity rows |
| 04_extension_dependency_links.csv | Original overlay source_relation, layer, endpoint case lists, locator and human warning source |
| 05_boundary_review_links.csv | case_id, explicit boundary_identity, all participating_unit_ids, panel and human locators |
| 06_adjudication_summary.csv | human_field, human_value, case_count, source; six categorical counts, no score |
| 07_human_review_pilot_report.md | All 30 cases, explicit identities and verbatim researcher notes |
| 08_r3_human_review_acceptance.md | Qualitative, bounded readiness assessment citing the recorded human evidence |
| 09_gates.csv | Computed gate_id/status rows |
| 90_run_metadata.json | Input hashes, adjudication commit, source metadata, mode, row counts, gate count and unresolved/ambiguous counts |
| 99_manifest_sha256.csv | SHA256/size manifest of every other output |

Nested CSV values are JSON. Source locators contain archive role/hash, exact ZIP
member path/hash, one-based CSV data_row (header excluded) and row_sha256.
The row fingerprint hashes the parsed dictionary serialized as sorted compact
UTF-8 JSON; it is a locator checksum, never a replacement historical signature.
summary_index is zero-based within the original JSON list. Human locators record
Git commit, file SHA256 and one-based row. Original evidence remains losslessly
recoverable from the fingerprinted archives; the sidecar does not rewrite it.

target_objects carries review_unit_id/type, explicit bundle_id, review_item_id,
lineage_id, family_ids, atom_node and the complete original r3c3_summary. A missing
scalar identity is NOT_AVAILABLE_FROM_SOURCE. Family IDs for singleton events
are explicitly parent-family provenance, not a new singleton family assignment.
A boundary's single-unit field is unavailable: its identity is the explicit case
and boundary_ref together with its complete participant list. Absence of one
identity domain is not an unresolved required link.

## Human discipline and acceptance

HR1 imports the canonical REVIEW_FIELDS and adds human-authored form_assessment.
All source columns/field values, including blank values and multiline notes,
are copied without paraphrase or assigning prose to otherwise blank fields.
Human counts are CLEAR 21 / PARTIAL 5 / INSUFFICIENT 4 and context YES 26 /
PARTIAL 4 / NO 0. All 30 are REVIEWED; review_time_seconds remains blank.

CASE001/004/006/016 retain the distinction between reproducible grouping and
human-recognizable coherence. Singleton uniqueness, form recognition and
structural significance remain distinct. CASE028/029 notes retain Elihu's
speech ending, YHWH's speech beginning, the absence of an automatic direct
Elihu-to-YHWH continuity inference, and Job as the explicit addressee in
ויען יהוה את־איוב. No automated interpretive labels or numeric quality score
are added. No pilot-time population extrapolation is made.

Acceptance is a qualitative assessment of the recorded pilot only. Technical
closure readiness does not imply all families are coherent, population-wide
validity, or authorization to enter R4.

## Validation and failure behavior

There are 21 linkage/report gates plus OUTPUT_MANIFEST_INTEGRITY (22 total).
The implemented names and negative tests are in
`tests/test_hr1_adjudication_linkage.py`. Every gate has a mutation demonstrating
rejection. Source commit, SHA, CRC and manifest defects fail at preflight before
an output model can be built; they never produce a PASS package. Other gates
compare the sidecar against a fresh deterministic derivation from verified
sources, plus actual human counts, caution text and extension connectivity.

Run syntax validation, full regression, synthetic self-test and inspect the
synthetic packet before the authorized real execution. A genuine real failure
is a stop condition, not permission to weaken a gate or repair historical data.
Output directory, ZIP and log must all be fresh. The ZIP and every written file
are reread and compared with serialized bytes; source files are checked unchanged
before a success log is written. On failure no success log is emitted; preserve
any partial artifacts for diagnosis. Generated outputs/logs remain ignored.
