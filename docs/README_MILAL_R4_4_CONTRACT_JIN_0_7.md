# JIN.0.7 execution

The JIN.0.6 ZIP and SHA256 are pinned in `config/r4_4_contract_jin_0_7_job.json`.
Use new output paths; overwrite is refused. Default Python is repository-relative.

```powershell
Set-Location C:\MILAL
& .venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_7.py
if ($LASTEXITCODE -ne 0) { throw 'JIN.0.7 tests failed' }
& scripts\run_milal_jin_layer_freeze_windows.ps1 -SelfTest -Out results\jin07_synthetic
if ($LASTEXITCODE -ne 0) { throw 'Self-test failed' }
& scripts\run_milal_jin_layer_freeze_windows.ps1 -Out results\jin07_real
if ($LASTEXITCODE -ne 0) { throw 'Human freeze failed' }
Write-Host 'Review results\jin07_real\09_revised_contract_review_packet.md'
```

For release, run full unittest discovery across tests with zero failures/errors/skips,
inspect the synthetic packet, then execute real A and B into independent fresh paths.
Compare complete ZIP bytes and recursive manifests. Results and logs remain local-only.

```sh
bash scripts/run_milal_jin_layer_freeze_termux.sh --self-test --out results/jin07_synthetic_termux
bash scripts/run_milal_jin_layer_freeze_termux.sh --out results/jin07_real_termux
```

Only six primary researcher decisions are frozen; per-row applications are derived
interpretation records. R1–R10 remain unanswered. No migration or R4.4 consumer is run.
