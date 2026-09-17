# Minimal R3c.0.1 historical regression fixtures

Extracted from the historical baseline CSV members in the local `MILAL.zip`
handoff archive (located in Downloads when extracted). This is a minimal
regression extract, not an analytical result set or a reconstruction of the
baseline. The full results directory and archive are not included or required.

## Source provenance

Archive SHA-256: `d27a4ec5f825908fc791ebfa542c5b21081eb8f7a882306b72492ac0e77a1f00`

- `MILAL/results/r3c_0_1/08_boundary_control_pattern_matches.csv`
  - Original member SHA-256: `ca5012ca677efab727d0bd73ad463ebf18d9608deabef7120c418faaca69e8a0`
  - Extract: 2 data rows; fields: review_item_id, object_type, parent_bundle_id, lineage_id, surface_text.
- `MILAL/results/r3c_0_1/01_source_schema_inventory.csv`
  - Original member SHA-256: `dd86390afc2a0de2230f527bc785171cfb9c0d98433dabaff3fe8d13d56921c1`
  - Extract: 7 data rows; fields: source, columns.

## Preserved invariants and extraction scope

- The two original S02135 rows preserve both `G6_SINGLETON_REVIEW_ITEM` and
  `SINGLETON_REFINEMENT_EVENT`, parent `RB01716`, lineage `RL00218`, and the exact
  historical Hebrew `surface_text` (including its original marks/formatting).
  Only the five fields consumed by the identity/rendering regressions are kept.
- The schema extract keeps seven source entries and only the `source` and
  `columns` fields. Each column list is filtered to the columns required by
  R3c.0.2 at extraction time, in historical inventory order. Every retained
  column was checked against the original inventory; names were not fabricated
  from the implementation. This is intentionally not a full source inventory.
- The CSVs are fixed, version-controlled expectations, never generated during
  tests. Changes to required schemas must be checked against historical source
  evidence before changing these fixtures.

The three consumers are `test_optional_job_regression_from_checked_in_baseline`,
`test_job_config_control_through_new_pipeline`, and
`test_required_columns_match_actual_baseline_inventory` in `tests/test_r3c_0_2.py`.
The pipeline control test uses the historical identity/surface in a synthetic
genealogy; it does not reconstruct the historical ancestry or load real BHSA.
Missing fixtures are test failures, not reasons to skip.
