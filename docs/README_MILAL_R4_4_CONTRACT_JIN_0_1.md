# Run the single-mother compatibility audit

See [specification](R4_4_CONTRACT_JIN_0_1_SPEC.md),
[methodological addendum](R4_4_CONTRACT_JIN_0_1_ADDENDUM.md) and
[validation report](R4_4_CONTRACT_JIN_0_1_VALIDATION_REPORT.md).
This is an append-only test/audit harness. No R4.4 consumer or parent adjudicator
is implemented. No fresh BHSA data load is needed. Results remain local/ignored.

From the repository root, run validation and inspect the synthetic packet:

```powershell
$ErrorActionPreference = 'Stop'
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& $python -m py_compile tests/r4_4_contract_jin_audit.py tests/test_r4_4_contract_jin_audit.py
if ($LASTEXITCODE -ne 0) { throw 'Syntax failed' }
& $python -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_audit.py -v
if ($LASTEXITCODE -ne 0) { throw 'Stage tests failed' }
& $python -B -X utf8 -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Regression failed' }
$synthetic = "results\r4_4_contract_jin_0_1_synthetic_$stamp"
& $python -B -X utf8 tests/r4_4_contract_jin_audit.py --self-test --out $synthetic
if ($LASTEXITCODE -ne 0) { throw 'Self-test failed' }
Get-Content "$synthetic\11_revised_r4_4_contract_review_packet.md" -Encoding UTF8
```

After inspection, within the authorized frozen-real audit scope:

```powershell
$ErrorActionPreference = 'Stop'
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$first = "results\r4_4_contract_jin_0_1_real_$stamp"
$repeat = "results\r4_4_contract_jin_0_1_repeat_$stamp"
& $python -B -X utf8 tests/r4_4_contract_jin_audit.py --out $first
if ($LASTEXITCODE -ne 0) { throw 'Real audit failed' }
& $python -B -X utf8 tests/r4_4_contract_jin_audit.py --out $repeat
if ($LASTEXITCODE -ne 0) { throw 'Independent audit failed' }
if ((Get-FileHash "${first}_results.zip").Hash -ne (Get-FileHash "${repeat}_results.zip").Hash) { throw 'ZIP mismatch' }
Get-Content "$first\17_current_readiness.txt"
Get-FileHash "${first}_results.zip" -Algorithm SHA256
Write-Host "Review: $first\11_revised_r4_4_contract_review_packet.md"
```

`--archive` accepts only the pinned archive bytes at an alternative path and
cannot be mixed with `--self-test`. `--out` must name a fresh directory.
Full regression requires zero skipped tests as well as a successful exit.
Independent rerun equality is an external release check; a single run cannot
claim it. Applicability proposals, root questions and revised Q1–Q9 remain
UNREVIEWED after successful technical validation.
