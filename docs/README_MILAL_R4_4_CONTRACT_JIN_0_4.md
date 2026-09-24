# Run JIN.0.4 Batch 1

This appends the seven researcher-supplied judgments. It does not detect new relations,
run focused audits, modify BHSA, or decide the remaining contextual queue.
See [spec](R4_4_CONTRACT_JIN_0_4_SPEC.md) and
[validation report](R4_4_CONTRACT_JIN_0_4_VALIDATION_REPORT.md).

From repository root in Windows PowerShell (verified upstream ZIP must be local):

```powershell
$ErrorActionPreference = 'Stop'
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_4.py -v
if ($LASTEXITCODE) { throw 'Batch tests failed' }
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p 'test_*.py' -v
if ($LASTEXITCODE) { throw 'Regression failed' }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& .\scripts\run_milal_jin_human_batch_windows.ps1 -SelfTest -Out "results\jin04_synthetic_$stamp"
if ($LASTEXITCODE) { throw 'Synthetic failed' }
```

Inspect synthetic 10_batch1_adjudication_report.md and control 07 before real execution:

```powershell
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& .\scripts\run_milal_jin_human_batch_windows.ps1 -Out "results\jin04_real_$stamp"
if ($LASTEXITCODE) { throw 'Real failed' }
Get-FileHash "results\jin04_real_${stamp}_results.zip" -Algorithm SHA256
```

Termux equivalent, after repository synchronization and exact upstream ZIP recovery:

```bash
python -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_4.py -v &&
python -B -X utf8 -m unittest discover -s tests -p 'test_*.py' -v &&
bash scripts/run_milal_jin_human_batch_termux.sh --self-test --out "results/jin04_synthetic_$(date +%Y%m%d_%H%M%S)"
```

After inspecting synthetic output:

```bash
run_out="results/jin04_real_$(date +%Y%m%d_%H%M%S)"
bash scripts/run_milal_jin_human_batch_termux.sh --out "$run_out" &&
sha256sum "${run_out}_results.zip"
```

Independent rerun uses another fresh output path; compare entire ZIP bytes. Output paths
must be fresh. Results/ZIPs remain ignored. No empirical Termux run is claimed.
