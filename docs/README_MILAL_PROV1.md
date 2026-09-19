# PROV1 usage

See PROV1_SPEC.md. This is provenance restoration over frozen results, not R3c.4.
The closed audit established exact reconstruction without an R2.2 rerun.

Synthetic validation (no historical inputs needed):

```powershell
$py = Join-Path (Get-Location) '.venv\Scripts\python.exe'
& $py -B -m unittest discover -s tests -p test_prov1.py -v
& $py -B src/milal_prov1_signature_provenance.py --self-test --output-dir results/prov1_synthetic
```

Use a new output directory for each execution. Inspect both Markdown outputs,
including G1→G2→G3 additions, S02135's distinct atom/window hash domains, and all
CASE025 participants. Synthetic fixture sizes are not historical Job counts.

Run the complete regression suite with the canonical temporary path workaround
documented in tests/README.md. Syntax can be checked with Python `compile()` over
the source bytes without creating bytecode caches.

Real execution is **not authorized in the implementation turn**. After separate
authorization, the interface is:

```text
python -B src/milal_prov1_signature_provenance.py
  --generator <historical-generator.py>
  --r2 <accepted-r2.zip> --b2 <accepted-r3b2.zip>
  --b3 <accepted-r3b3.zip> --c3 <accepted-r3c3.zip>
  --output-dir <new-directory>
```

The Windows runner scripts/run_milal_prov1_windows.ps1 accepts `-Generator`,
`-R2Zip`, `-R3b2Zip`, `-R3b3Zip`, `-R3c3Zip`, `-OutputDir`, optional `-PythonExe`.
It defaults to repository-local .venv and runs the synthetic self-test first.
Nonzero exits are propagated. No result ZIP is automatically created; the twelve
requested artifacts are written to the fresh output directory and verified by
99_manifest_sha256.csv. Preserve this directory and all original source archives.

Inputs must match pinned accepted hashes. The generator is fingerprinted, not
executed. No BHSA installation, R1 archive or R2.2 rerun is required. No judgment
field is automatically completed, and missing direct identity links are explicit.
