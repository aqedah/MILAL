# Run the R4.4 input-contract audit

This is a test harness and CONTRACT_PROPOSAL, not an analytical consumer.
See [specification](R4_4_CONTRACT_0_1_SPEC.md),
[architecture audit](R4_4_CONTRACT_0_1_ARCHITECTURE.md) and
[validation report](R4_4_CONTRACT_0_1_VALIDATION_REPORT.md).
No BHSA data is required. Real mode reads only the pinned accepted LAYER.0.2 ZIP.
All generated results/ZIPs/logs remain local and ignored.

From the repository root in PowerShell:

```powershell
$ErrorActionPreference = 'Stop'
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& $python -m py_compile tests/r4_4_contract_audit.py tests/test_r4_4_contract_audit.py
if ($LASTEXITCODE -ne 0) { throw 'Syntax validation failed' }
& $python -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_audit.py -v
if ($LASTEXITCODE -ne 0) { throw 'Contract tests failed' }
& $python -B -X utf8 -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Regression failed' }
$synthetic = "results\r4_4_contract_0_1_synthetic_$stamp"
& $python -B -X utf8 tests/r4_4_contract_audit.py --self-test --out $synthetic
if ($LASTEXITCODE -ne 0) { throw 'Synthetic audit failed' }
Write-Host "Inspect $synthetic\13_r4_4_contract_review_packet.md before real dry-run."
```

After inspecting the synthetic packet, within the authorized dry-run scope:

```powershell
$ErrorActionPreference = 'Stop'
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$first = "results\r4_4_contract_0_1_real_$stamp"
$repeat = "results\r4_4_contract_0_1_repeat_$stamp"
& $python -B -X utf8 tests/r4_4_contract_audit.py --out $first
if ($LASTEXITCODE -ne 0) { throw 'Real dry-run failed' }
& $python -B -X utf8 tests/r4_4_contract_audit.py --out $repeat
if ($LASTEXITCODE -ne 0) { throw 'Independent dry-run failed' }
if ((Get-FileHash "${first}_results.zip").Hash -ne (Get-FileHash "${repeat}_results.zip").Hash) { throw 'ZIP mismatch' }
Get-Content "$first\14_r4_4_implementation_readiness.md"
Write-Host "Researcher questions: $first\13_r4_4_contract_review_packet.md"
Get-FileHash "${first}_results.zip" -Algorithm SHA256
```

Optional `--archive` can specify identical pinned ZIP bytes at another path;
it cannot be combined with `--self-test`. `--out` must name a fresh directory.
READY_FOR_HUMAN_CONTRACT_REVIEW does not authorize implementation or answer Q1–Q7.
