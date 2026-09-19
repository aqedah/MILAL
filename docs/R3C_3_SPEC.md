# MILAL R3c.3 — Structural Signature Context for Human Review

Consult HANDOFF.md for current-stage authority. R3c.3 enriches the exact frozen
R3c.2 cases. No splitting, merging, resampling, deletion, inferred signatures,
automatic interpretation, or R4. R3c.0.2/R3c.1/R3c.2 Python cores stay unchanged.

## Empirical motivation (researcher supplied)

The five-case R3c.2 review found CASE007 reviewable, CASE019 locally reviewable,
CASE013 partly reviewable, CASE025 sufficient for boundary multiplicity but not
macro attachment, and CASE001 insufficient. CASE001/RB00104 is G0/depth0, length1,
366 occurrences, 314 contexts, 366 surfaces, 40 chapters, 28 repeated children,
21 singleton branches. CASE013 needs the RB00549→RB00548 distinction. These are
reported observations, not corpus constants or automatic judgments.

## Actual source inspection

Both transferred ZIPs passed SHA256 and full ZIP CRC checks on 2026-09-18:

| Source | Bytes | SHA256 |
|---|---:|---|
| job_r3b_2_results.zip | 8621833 | d7989468f82274baf6b3d3692529739e940f6950e3a24c5b38914a9a71c61095 |
| job_r3b_3_results.zip | 1291532 | 612d4f9f432b8aaac5a2266341c464b2ee654dd7d353cea688866b94355cd5af |

All CSV headers, archive listings, method reports and field definitions were
inspected. This was schema inspection, not a real R3c.3 dataset execution.
Names below are observed members; code discovers tables by column sets and
rejects ambiguous schemas. Every copied value has archive hash/member/data-row/
column/value provenance. Full source rows remain JSON in definition tables.

| Information | Classification | Source fields / deterministic rule |
|---|---|---|
| Bundle identity/geometry | AVAILABLE_FROM_SOURCE | R3b.2 `01_review_bundles.csv`: `bundle_id`, `geometry_sha256`, `occurrence_count` |
| Bundle equivalence | AVAILABLE_FROM_SOURCE | R3b.2 `10_workspace_field_definitions.csv`: `field`, `definition`, rows `review_bundle`, `geometry_sha256`, `representative_family_id`; bundles group identical ordered occurrence geometry |
| Representative family | AVAILABLE_FROM_SOURCE | R3b.2 `01_review_bundles.csv`: `representative_family_id`, `representative_level`; R3b.3 `02_lineage_bundle_members.csv`: `representative_family_id` |
| Member families | AVAILABLE_FROM_SOURCE | bundle/member tables: `member_family_count`, `member_family_ids`; R3b.2 `02_bundle_family_members.csv`: `bundle_id`, `family_id`, `is_representative` |
| Levels | AVAILABLE_FROM_SOURCE | bundle/member tables: `levels_present`, `lowest_level`, `highest_level`; family table: `level`, `level_description` |
| Genealogy | AVAILABLE_FROM_SOURCE | R3b.3 `02_lineage_bundle_members.csv`: `lineage_id`, `parent_bundle_id`, `refinement_depth` |
| Positional/BHSA/coarse/lexical flank profiles | AVAILABLE_FROM_SOURCE | R3b.2 `06_bundle_context_profiles.csv`: `bundle_id`, `source_representative_family_id`, `profile_layer`, `profile_payload_json`, `profile_sha256`, `occurrence_count`, `occurrence_share`, `profile_rank_within_bundle`; layers P0_POSITIONAL, P1_BHSA, P2_COARSE_FLANK, P3_LEXICAL_FLANK, FORENSIC_EXACT |
| Family signature identifier | AVAILABLE_FROM_SOURCE | R3b.2 `02_bundle_family_members.csv`: `signature_hash` (opaque hash) |
| Decoded membership signature | NOT_AVAILABLE_FROM_SOURCE | No family signature preimage column. Context profile JSON is a distribution, not the family membership definition |
| Parent/child transition | AVAILABLE_FROM_SOURCE | R3b.3 `03_lineage_cross_refinement_edges.csv`: `parent_bundle_id`, `child_bundle_id`, `parent_family_id`, `child_family_id`, `parent_level`, `child_level`, `child_signature_hash` |
| Source-field delta | DERIVABLE_FROM_EXPLICIT_SOURCE_FIELDS | Compare explicit edge parent/child level and family ID; join endpoint family rows for `signature_hash`. String equality → unchanged; inequality → changed. Check child family hash against edge |
| Feature additions/removals causing refinement | NOT_AVAILABLE_FROM_SOURCE | Hash changes cannot disclose the underlying changed feature; no Hebrew similarity reconstruction |
| Singleton first-unique level and G6 signature | AVAILABLE_FROM_SOURCE | R3b.2 `08_singleton_review_items.csv`, R3b.3 `06_g6_singleton_lineage_links.csv`: `review_item_id`, `first_unique_level`, `signature_G6` (opaque hash) |
| Parent at first uniqueness | AVAILABLE_FROM_SOURCE | R3b.3 `06_g6_singleton_lineage_links.csv`: `parent_bundle_id_at_first_unique`, `parent_family_id_at_first_unique`, `lineage_id` |
| Singleton mapped identity/transition | AVAILABLE_FROM_SOURCE | R3b.3 `05_lineage_singleton_refinement_events.csv`: `parent_bundle_id`, `parent_family_id`, `parent_level`, `child_level`, `child_signature_hash`, `mapped_g6_singleton_review_item_id`; exact event rows retained |
| Feature causing first uniqueness | NOT_AVAILABLE_FROM_SOURCE | first_unique_level and hashes do not supply feature preimages. EVENT_ONLY may also lack G6/first-unique fields |
| Distribution diagnostics | DERIVABLE_FROM_EXPLICIT_SOURCE_FIELDS | From R3c.2 evidence/boundary indexes: row counts, distinct `context_id`/exact `surface_text`, counts of chapter parsed from `ref_start`, contexts with multiple evidence rows |
| Span-length distribution in this implementation | NOT_AVAILABLE_FROM_SOURCE | Selected R3c.2 evidence lacks atom indices. This optional statistic is not derived by joining earlier occurrences; no verse subtraction or inferred tokenization |

Availability is per target/row. An existing column may have no usable value for
one target. Runtime inventory preserves all member schemas, including unused tables.
Explicit profile field/value sets are deterministic JSON key projections, with
full distributions retained. They never substitute for membership features.

## Input chain

Require R3c.2, its exact R3c.1 source, R3b.2 and R3b.3 ZIPs. R3c.1 is an additional
necessary provenance dependency: R3c.2 preserves its inventory hash but not the
inventory contents or full singleton source rows. Verify R3c.1 ZIP hash/metadata
against R3c.2, both manifests, versions and gate records; match R3b hashes to the
R3c.1 inventory and nested recorded inputs. Filename is never archive identity.

Missing identity schemas fail; optional absent evidence is explicitly unavailable.
Singletons join through exact archived R3c.1 provenance row JSON, not text similarity.
Keep all four source ZIPs. Every R3c.2 member is referenced with exact hash/size,
including all raw evidence, contexts, boundary rows, relations and extension rows.
No BHSA loading. Case rows/order/IDs/judgments are unchanged. Boundary unit sets
are complete. Include immediate parent definitions for target/panel units and
singleton attachments, without recursive analytical expansion.

## Thirteen outputs

| File | Schema |
|---|---|
| 01_source_signature_inventory.csv | archive_role, archive_sha256, member, sha256, bytes, columns, row_count |
| 02_review_cases.csv | Exact original R3c.2 case columns/rows |
| 03_bundle_definition_context.csv | bundle_id, fields JSON (status/evidence), source_rows JSON |
| 04_parent_child_structural_delta.csv | bundle_id, parent_bundle_id, status, comparisons, feature_payload_delta, source_rows |
| 05_singleton_definition_context.csv | unit_id, fields, uniqueness_feature_payload, parent_bundle_ids, source_rows |
| 06_distribution_diagnostics.csv | case_id, status, evidence_row_count, unique_context_count, unique_surface_count, start_chapter_distribution, contexts_with_multiple_evidence_rows, span_length_distribution |
| 07_boundary_definition_context.csv | case_id, complete unit_ids referencing definitions |
| 08_review_packet_signature_enriched.md | Structural evidence before frozen occurrence/context references |
| 09_human_review_readiness.csv | Per-case availability diagnostics, never sufficient_context judgments |
| 10_gates.csv | gate_id, status, detail, violations |
| 11_method_note.md | Method/limitations |
| 90_run_metadata.json | Source hashes, exact R3c.2 member references, counts/metrics |
| 99_manifest_sha256.csv | Every other output's SHA256/bytes |

Nested cells are JSON; source strings are exact. Human packet references complete
parent definitions in CSV and occurrences in the verified original packet rather
than re-expanding them. Canonical REVIEW_FIELDS are imported, never inferred.

Readiness distinguishes structural_metadata_available from structural_definition_available:
the latter means decoded membership feature values, unavailable for these hash-only
archives. Parent metadata and source-field deltas can be available while feature
definitions/deltas remain unavailable. NOT_APPLICABLE marks absent parent/singleton
roles. Singleton/boundary row counts are evidence counts, not deduplicated population
occurrences. Chapter counts use start chapters only. No metric scores meaning,
estimates population review time, or decides sufficient_context.

## Validation and limits

26 computed gates: the 20 requested gates plus SOURCE_CHAIN_VALID,
SOURCE_VERSIONS_AND_GATES_VALID, FIVE_ACCEPTANCE_CONTROLS_PRESERVED,
DISTRIBUTION_USES_EXPLICIT_EVIDENCE, SOURCE_INVENTORY_COMPLETE and
PACKET_MATCHES_SOURCE_ENRICHMENT. Every gate has a negative mutation test.
Expected records are recomputed from source bytes, not cached PASS declarations.

Run syntax validation, full regression suite, synthetic self-test and inspect its
packet. CASE001/007/013/019/025 and S02135 stay explicit controls. Synthetic controls
are not validation of the real five target bundles. No real R3c.3 dataset run,
commit, push or R4 is authorized in this development task.
