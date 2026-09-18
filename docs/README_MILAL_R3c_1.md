# MILAL R3c.1 — Human Review Unit Decomposition

R3c.0.2 has passed real Termux/Windows cross-validation. Its navigation-container
pilot produced high-complexity cases of 17,612 and 18,222 lines. R3c.1 tests the
reviewability of individual existing bundles and canonical singleton outcomes.
It preserves the frozen navigation model and all target evidence.

See [the specification](R3C_1_SPEC.md) for methodological decisions and all gates.

## Windows execution (after separate authorization for real data)

Keep `src/`, `scripts/` and `config/` together, including the imported frozen
`src/milal_r3c_0_2_reviewability.py`. The default Python is
`<repository>\.venv\Scripts\python.exe`; no activation is needed. Install
Text-Fabric in that environment for real runs. Development self-tests use only
the Python standard library and do not open BHSA.

```powershell
& C:\MILAL\scripts\run_milal_r3c_1_windows.ps1 `
  -R3b2Zip 'C:\MILAL\inputs\job_r3b_2_results.zip' `
  -R3b3Zip 'C:\MILAL\inputs\job_r3b_3_results.zip' `
  -TfDir 'C:\MILAL-data\bhsa\tf\2021' `
  -OutputDir 'C:\MILAL\results\r3c_1_windows_01'
```

All four paths are required. Relative paths use the caller's directory; code,
default Python and default configuration resolve from the runner's repository.

| Option | Default |
|---|---|
| `-PythonExe` | Repository-local `.venv\Scripts\python.exe` |
| `-PilotConfig` | Repository `config/r3c_1_job_pilot.json` |
| `-Seed` | Omitted: use configuration seed; explicit value overrides it |
| `-ResultZip` | `<OutputDir>_results.zip` |
| `-RunLog` | `<OutputDir>_windows_run.log` |

The wrapper rejects existing output, ZIP or log paths and requires distinct ZIP
and log paths outside the output tree. It validates input files and BHSA
`otype.tf`/`oslots.tf`, runs the self-test, then runs analysis. It captures UTF-8
stdout/stderr and statuses. Failure diagnostics are archived when an output
directory exists. Self-test/analysis nonzero codes are preserved; ZIP failure
returns nonzero after successful analysis, and analysis failure takes precedence
if both fail. Wrapper validation errors return 2. Inspect `$LASTEXITCODE`.
Archives contain the output directory as their top-level folder. Neither logs
nor ZIPs alter the analytical manifest. No Termux runner is required for R3c.1.

Direct Python accepts `--r3b2-zip`, `--r3b3-zip`, `--tf-dir`, `--output-dir`,
`--pilot-config` and optional `--seed`. Choose a nonexistent real-run output
directory. Exit 0 means computed checks passed; it does not mean human acceptance.

## Outputs

| File | Contents |
|---|---|
| `01_source_schema_inventory.csv` | Actual source columns/counts, archive identities and hashes |
| `02_review_cases.csv` | Exactly 30 cases; canonical review fields and selection reasons |
| `03_review_unit_population.csv` | Every repeated bundle and canonical singleton outcome, including unselected units |
| `04_case_evidence.csv` | All target bundle occurrences and all selected singleton source spans |
| `05_relation_context.csv` | Ancestors, immediate parents, direct repeated children, explicit singleton branches |
| `06_object_provenance.csv` | Source row snapshots with archive hash, member, data row, key and role |
| `07_boundary_case_evidence.csv` | Every matching repeated occurrence and all spans of matching singleton outcomes |
| `08_sequence_extension_overlay.csv` | Separate target-incident/exemplar-based extension attachments |
| `09_span_context_inventory.csv` | Resolved full covering spans, book-bounded neighbors and overlapping structures |
| `10_review_packet.md` | Individual target units, relation summaries, complete target evidence, boundary panels and forms |
| `11_gates.csv` | 24 computed invariants and violations |
| `12_method_note.md` | Selection, identity, evidence, context and extension assumptions |
| `90_run_metadata.json` | Config/seed, source identities, population/case counts, gates, run kind and empirical status |
| `99_manifest_sha256.csv` | SHA-256 and size of each other output file |

Nested CSV cells contain JSON. The population has fields for both unit types;
nonapplicable cells are empty. Only cases carry human-review forms. Unselected
singletons retain all source spans/branches; their context is not loaded unless
used in target or boundary evidence. Population membership and singleton
provenance are complete; occurrence provenance covers emitted target/panel rows.

HIGH uses occurrence count, direct repeated children, explicit refinement-event
branches, and depth descending, then bundle ID ascending. LOW reverses numeric
ordering after HIGH exclusion. RANDOM samples the remaining ID-sorted pool.
Singleton selection uses a separate generator with the same recorded seed after
the fixed Job S02135 control. All groups have six cases. No weighted score,
candidate reduction, automatic interpretation or total-hour estimate is used.

Level/count requirements are explicit: membership must supply `occurrence_count`,
`sequence_length`, `levels_present`, `lowest_level` and `highest_level` in addition
to the frozen R3c.0.2 requirements. Counts must agree with occurrence rows.
Refinement branch ranking counts event records, not additional G6 link records.
The latter are still preserved as explicit relations and provenance.

## Reuse and limitations

R3c.1 imports R3c.0.2 ZIP loading, source records, unique-ID checks, ancestry
validation, exact singleton folding, span-aware TF context, review fields,
CSV serialization and manifest helpers. No globals are monkey-patched.
The old model, selector, renderer and writer cannot be reused as a whole because
they sample and expand containers. R3c.1 therefore has its own orchestration,
forms, gates and renderer. Small navigation/configured-control checks are adapted
because the old versions are embedded in those container-specific functions;
their Hebrew regression normalization preserves the same rule.

The extension adapter still has exemplar starts only. Bundle overlays are
incident to the target; singleton overlays use explicit parents. Boundary
coverage is not exhaustive. No OCCURRENCE_VERIFIED claim is made. Large numbers
of actual target occurrences or boundary matches can still produce large cases;
R3c.1 does not hide them to force a smaller packet.

## Development validation

```powershell
python -m py_compile src/milal_r3c_1_review_units.py tests/test_r3c_1.py tests/test_r3c_1_windows_runner.py
python -m unittest discover -s tests -v
python src/milal_r3c_1_review_units.py --self-test
python src/milal_r3c_1_review_units.py --self-test --output-dir results/r3c_1_synthetic
```

Use a fresh/empty directory for a retained synthetic packet. The self-test runs
the real ZIP adapter, source-order reproducibility, all 24 gates, four deliberate
negative gate mutations and packet assertions. The unit suite separately has
a negative mutation for every gate, S02135 with historical surface, all singleton
kinds, graph failures, occurrence completeness, span context and output checks.
The synthetic corpus contains 82 repeated bundles and 27 singleton outcomes;
30 cases are selected (6 per group). It is not the real Job population.

The Windows runner suite checks PowerShell 5.1 and 7 where available, default
and explicit interpreters, seed forwarding, preflight, failure statuses, logs,
ZIP packaging and no-overwrite behavior. Existing R3c.0.2 tests are preserved.
No real BHSA run or R4 work belongs to this development validation.
