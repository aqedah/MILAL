# MILAL R3c.2 — Lossless Compact Review Presentation

R3c.2 reads a frozen R3c.1 result ZIP, verifies its manifest, version, gates and
30-case registry, then presents exactly that evidence more compactly. It needs
no BHSA path and never resamples or rebuilds analytical units.
See [the specification](R3C_2_SPEC.md) for the full losslessness contract.

## Windows runner (for a later authorized input run)

```powershell
& C:\MILAL\scripts\run_milal_r3c_2_windows.ps1 `
  -R3c1Zip 'C:\MILAL\inputs\r3c_1_windows_results.zip' `
  -OutputDir 'C:\MILAL\results\r3c_2_windows_01'
```

`-R3c1Zip` and `-OutputDir` are required. Default Python is the repository-local
`.venv\Scripts\python.exe`; optional `-PythonExe` supplies another interpreter.
No virtual-environment activation is needed. `-ResultZip` defaults to
`<OutputDir>_results.zip`, and `-RunLog` to `<OutputDir>_windows_run.log`.

Keep src/ and scripts/ together. R3c.2 imports only canonical REVIEW_FIELDS from
the unchanged R3c.0.2 module in normal operation. Its synthetic self-test uses
the unchanged R3c.1 fixture/writer, so both frozen modules must remain available.
Only the Python standard library is needed; Text-Fabric is not loaded.

The runner performs self-test before presentation, captures UTF-8 stdout/stderr,
preserves self-test/presentation failure exit codes and packages diagnostics when
available. Packaging failure returns nonzero; a simultaneous presentation failure
takes precedence. Existing output directories, ZIPs and logs are never overwritten.
Auxiliary ZIP/log paths must be outside the output tree and distinct. Archive
creation is exclusive; archives have the output directory as their top folder.

Direct CLI:

```powershell
python src/milal_r3c_2_compact_review.py `
  --r3c1-zip inputs/r3c_1_windows_results.zip `
  --output-dir results/r3c_2_windows_01
```

Use a nonexistent output directory. Failure returns 2 and records source/schema
diagnostics where possible. A successful run still requires human inspection.

## Derived files

| File | Contents |
|---|---|
| `01_source_r3c1_inventory.csv` | Source ZIP hash, every archived member hash/size, CSV columns/counts |
| `02_review_cases.csv` | Original cases/order/fields plus small target-summary projections and population locators |
| `03_compact_evidence_index.csv` | Every original target evidence row and its source locator |
| `04_context_detail_inventory.csv` | Every context, complete original clauses/sentences JSON and resolution status |
| `05_compact_relation_index.csv` | Display groups with every raw relation ID, source count, transition and path |
| `06_raw_relation_index.csv` | Every original relation row, distinct raw row IDs and source locators |
| `07_boundary_evidence_index.csv` | All boundary evidence rows and locators |
| `08_sequence_extension_overlay.csv` | All original overlay rows and locators |
| `09_review_packet_compact.md` | Target summaries, one context entry per case/context, all evidence IDs/surfaces, compact relation/overlay summaries |
| `10_packet_metrics.csv` | Per-case evidence/context/relation/extension counts and exact rendered line/byte sizes |
| `11_gates.csv` | 23 computed checks and violations |
| `12_method_note.md` | Losslessness, grouping, provenance and metric conventions |
| `90_run_metadata.json` | Source ZIP SHA256/metadata, totals, whole-packet size, gate status |
| `99_manifest_sha256.csv` | SHA256/size of every other derived file |

Original CSV cell strings remain exact, including complete context JSON cells.
Derived list/dict cells are JSON. Source data-row numbers start at 1 after the
header. Keep the original ZIP whose hash is recorded: that archive resolves full
provenance and the unselected unit population without duplicating them here.

Relation grouping uses case + target + relation kind + related unit. This is the
requested kind/related-unit display folding scoped to its owner, not an analytical
merge. Evidence IDs can legitimately recur across different boundary panels; full
row multisets preserve those attachments. All distinct target identities survive.

The main packet omits full inline clause/sentence inventories and repeated source
IDs; the detail CSV/source ZIP preserve them. All covering verses and exact source
surfaces remain visible. Each visible evidence line also has a JSON HTML trace
comment. Overlays remain EXEMPLAR_ONLY or UNRESOLVED; endpoint-direction counts
are literal short-bundle → long-bundle pairs, not functional labels.

## Development checks

```powershell
python -m py_compile src/milal_r3c_2_compact_review.py tests/test_r3c_2.py tests/test_r3c_2_windows_runner.py
python -m unittest discover -s tests -v
python src/milal_r3c_2_compact_review.py --self-test
python src/milal_r3c_2_compact_review.py --self-test --output-dir results/r3c_2_synthetic
```

The retained self-test also preserves a synthetic frozen source ZIP alongside
the output as `<OutputDir>_source_r3c1.zip`, making its locators auditable after
the temporary test directory is cleaned. Both paths must be new.

Tests cover every gate negatively, shared contexts, all evidence traces, raw
relation multiplicity, untouched contexts, boundary/extension records, S02135,
metrics, deterministic non-case row reordering, source manifest/version/gate
rejection, no-overwrite and PowerShell 5.1/7 contracts where available. Existing
R3c.0.2/R3c.1 tests remain unchanged.

No real R3c.1 ZIP is processed during this development task. The researcher’s
reported R3c.1 empirical findings are recorded in HANDOFF; the real archive was
not bundled in the B-computer clone. Synthetic validation cannot establish real
compact-packet usability or authorize R4.
