# MILAL R3c.2 — Lossless Compact Review Presentation

Active presentation specification, 2026-09-18. R3b.3, R3c.0.2 and the R3c.1
analytical core remain frozen. No R4 work or real-data execution is authorized
by development acceptance.

## Empirical basis supplied by the researcher

The real Windows/BHSA 2021 R3c.1 run passed 24 gates: 8,908 units (2,219 repeated
bundles and 6,689 singleton outcomes), 30 cases, 1,657 selected evidence rows,
798/798 resolved contexts, independent S02135 and six boundary controls. Extension
remained overlay-only / EXEMPLAR_ONLY. The packet had 32,038 lines. Its first six
cases had 366/327/307/181/180/174 occurrences and respectively
5,784/4,978/4,989/3,033/3,027/3,090 lines. These are empirical observations, not
generic corpus constants or length-based acceptance thresholds.

The next problem is presentation. Do not split bundles, introduce new analytical
objects, resample, drop rare evidence, truncate, choose exemplars instead of all
occurrences, suppress exceptions, or infer semantic clusters.

## Frozen source contract

The primary input is one R3c.1 result ZIP. Read it without extracting paths or
loading BHSA. Verify complete manifest SHA256/byte sizes, source metadata version
R3c.1, successful status, all source gates PASS and exactly 30 unique source cases.
Record the input ZIP SHA256. Reuse its case rows/order and targets unchanged.
Missing or ambiguous schemas fail explicitly. Preserve all source CSV columns.

The original R3c.1 ZIP remains the external provenance authority. Derived indexes
record member paths and one-based CSV data-row numbers (excluding the header).
Do not duplicate the full population or global provenance table unnecessarily.

## Presentation contract

- Once per repeated target, show unit/lineage IDs, parent, ancestry, depth,
  sequence length, occurrence count, direct repeated child count, explicit
  singleton branch count and exact exemplar. Copy only selected/panel summary
  projections, including a locator into the original population table.
- Group evidence display by context_id within each case. List **every** evidence
  ID, unit ID and exact surface beneath the single displayed context. Show full
  covering verses, previous/next verses and overlapping clause/sentence counts.
- Retain complete context cells, including full clause/sentence JSON, in the
  context detail table. Never regenerate or alter them.
- Group structural relation display by relation_kind + related_unit_id **within
  the same case and target unit**. This scope preserves distinct target relations
  within multi-unit boundary panels. Retain all raw row IDs, counts, transition
  sets and ancestry paths. A mapped event and G6 link can share a display row;
  their separate raw records remain auditable.
- Summarize extensions separately: row count, coverage categories, directed
  short-to-long endpoint-pair counts and involved bundle IDs. Preserve every raw
  extension attachment. No OCCURRENCE_VERIFIED or exhaustive-coverage claim.
- Apply the same presentation to all boundary evidence; retain the entire set.
- Import canonical REVIEW_FIELDS. Only review_status is UNREVIEWED. No automatic
  interpretation labels or population review-time estimates.

Display group keys and raw-row locators are presentation references, not new
analytical identities. Duplicate source relation rows retain distinct ordinals.
Evidence identity is scoped by case_id/evidence_id: reuse across panels is valid.

## Outputs

Use the fourteen files documented in [the README](README_MILAL_R3c_2.md).
Per-case metrics are source evidence rows, unique contexts (including a standalone
panel context), raw/compact relation rows, extension rows, packet lines and UTF-8
bytes. Case blocks include their heading and trailing blank line. Shared preamble
counts appear only in whole-packet metadata. Metrics never score meaning or gate
acceptance by length.

## Computed gates

Every gate has a negative mutation test:

1. SOURCE_R3C1_MANIFEST_VALID
2. SOURCE_R3C1_GATES_ALL_PASS
3. SOURCE_R3C1_VERSION_VALID
4. SOURCE_CASE_COUNT_VALID
5. SOURCE_CASE_SET_PRESERVED
6. SOURCE_CASE_ORDER_PRESERVED
7. REVIEW_TARGET_IDS_UNCHANGED
8. ALL_EVIDENCE_IDS_PRESERVED
9. NO_EVIDENCE_DUPLICATION_OR_LOSS
10. ALL_CONTEXT_REFERENCES_RESOLVE
11. CONTEXT_DETAIL_LOSSLESS
12. RAW_RELATION_ROWS_PRESERVED
13. COMPACT_RELATIONS_TRACE_TO_RAW
14. BOUNDARY_EVIDENCE_PRESERVED
15. EXTENSION_ROWS_PRESERVED
16. EXTENSION_REMAINS_OVERLAY_ONLY
17. REVIEW_FIELDS_BLANK_EXCEPT_STATUS
18. NO_AUTOMATIC_FUNCTION_LABELS
19. S02135_PRESERVED
20. PACKET_INDEX_COVERS_ALL_TARGET_EVIDENCE
21. PACKET_METRICS_MATCH_RENDERED_PACKET
22. SOURCE_REFERENCES_RESOLVE
23. TARGET_SUMMARIES_PRESERVED

Compare complete original-field row multisets, not only counts. Verify packet
trace markers against visible evidence IDs and compare actual rendering to the
complete model. Reordering non-case CSV rows must not change rendering; original
case ordering explicitly takes precedence over sorting. Source archive hashes
and data-row locators necessarily change when source rows are reordered.

## Acceptance boundary

Run syntax checks, the entire prior/new regression suite, synthetic R3c.2 self-test
and direct synthetic packet inspection. Report exact test/gate counts and metrics.
Do not run the real R3c.1 ZIP in this task. Keep every frozen core and historical
result unchanged. A later real compact-presentation run requires authorization.
