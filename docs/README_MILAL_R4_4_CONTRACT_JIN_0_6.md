# Running JIN.0.6

Use the verified JIN.0.5 result ZIP at the path and SHA256 pinned in
`config/r4_4_contract_jin_0_6_job.json`. No substitute inputs or fuzzy linkage.
Output directories must be new. Python defaults are repository-relative.

```powershell
Set-Location C:\MILAL
& .venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_6.py
if ($LASTEXITCODE -ne 0) { throw 'JIN.0.6 tests failed' }
& scripts\run_milal_jin_relation_layers_windows.ps1 -SelfTest -Out results\jin06_synthetic
if ($LASTEXITCODE -ne 0) { throw 'Self-test failed' }
& scripts\run_milal_jin_relation_layers_windows.ps1 -Out results\jin06_real
if ($LASTEXITCODE -ne 0) { throw 'Audit failed' }
Write-Host 'Review results\jin06_real\17_human_review_packet.md'
```

Full regression is required before release, using unittest discovery across all tests;
failure/error/skip counts must all be zero. For release, run again into another new
directory and compare complete ZIP bytes/SHA256 plus every recursive manifest. A process
PASS is a technical invariant result, not human acceptance or authorization to migrate.

Termux/cross-validation (requires the same verified upstream ZIP):

```sh
bash scripts/run_milal_jin_relation_layers_termux.sh --self-test --out results/jin06_synthetic_termux
bash scripts/run_milal_jin_relation_layers_termux.sh --out results/jin06_real_termux
```

Termux execution is not claimed unless actually performed. Runners do not fetch BHSA
or modify analytical inputs. All generated directories and ZIPs remain local-only.
