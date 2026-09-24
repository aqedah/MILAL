# Run JIN.0.8

Read [specification](R4_4_CONTRACT_JIN_0_8_SPEC.md) and
[exact authority](R4_4_CONTRACT_JIN_0_8_RESEARCHER_SOURCE.txt).
From the repository root, use an unused output name. Existing outputs are never overwritten.

```powershell
$ErrorActionPreference = 'Stop'
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_8.py -v
if ($LASTEXITCODE -ne 0) { throw 'JIN.0.8 unit tests failed' }
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_jin_contract_freeze_windows.ps1 -SelfTest -Out .\results\jin08_synthetic_new
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
```

Inspect the synthetic contract, fixture tables and scope packet. After full regression
with zero skips, execute the authorized frozen-input run and independent rerun:

```powershell
$ErrorActionPreference = 'Stop'
foreach ($runName in @('jin08_real_new_a', 'jin08_real_new_b')) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_jin_contract_freeze_windows.ps1 -Out (Join-Path '.\results' $runName)
    if ($LASTEXITCODE -ne 0) { throw "Run failed: $runName" }
}
Get-FileHash .\results\jin08_real_new_a_results.zip, .\results\jin08_real_new_b_results.zip -Algorithm SHA256
```

ExecutionPolicy Bypass is scoped to the runner process; no persistent machine setting
is changed. Python defaults to the repository's .venv and accepts `-Python` override.
The required ZIP path/hash, source authority and frozen pins are in the stage config.
No downloads, fallback source or fuzzy linkage are permitted. All result files stay local.

Termux equivalent, after the same validation prerequisites:
`bash scripts/run_milal_jin_contract_freeze_termux.sh --out results/jin08_termux_new`.
Use `--self-test` for synthetic execution and `PYTHON` to override the interpreter.
No Termux empirical validation is claimed without actually executing it.
