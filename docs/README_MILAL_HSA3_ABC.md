# Run HSA3-A/C

See [specification](HSA3_ABC_SPEC.md) and [validation](HSA3_ABC_VALIDATION_REPORT.md).
The runner uses the repository `.venv` by default; `-Python` may override it.
Paths derive from the repository root. Real execution requires the exact
configured D/E ZIP; no BHSA installation or new lexical scan is needed.

From repository-root PowerShell:

```powershell
$ErrorActionPreference = 'Stop'
& .venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { throw 'Regression failed' }
& scripts\run_milal_hsa3_abc_windows.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
```

Inspect the printed synthetic report and F/G packet before real execution.
The researcher has authorized real frozen-artifact execution for this stage:

```powershell
$ErrorActionPreference = 'Stop'
$tag = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$first = Join-Path $PWD "results\hsa3_abc_real_$tag"
$second = Join-Path $PWD "results\hsa3_abc_repeat_$tag"
& scripts\run_milal_hsa3_abc_windows.ps1 -Out $first
if ($LASTEXITCODE -ne 0) { throw 'Real validation failed' }
& scripts\run_milal_hsa3_abc_windows.ps1 -Out $second
if ($LASTEXITCODE -ne 0) { throw 'Independent rerun failed' }
$h1 = (Get-FileHash -Algorithm SHA256 "${first}_results.zip").Hash
$h2 = (Get-FileHash -Algorithm SHA256 "${second}_results.zip").Hash
if ($h1 -ne $h2) { throw 'Independent ZIP bytes differ' }
Write-Host "PASS SHA256 $h1"
Write-Host "Report: $first\08_hsa3_abc_adjudication_report.md"
Write-Host "F/G packet: $first\09_hsa3_fg_remaining_review_packet.md"
```

Outputs must be fresh paths. `-Archive` accepts only a byte-identical copy of
the pinned input ZIP and cannot be combined with `-SelfTest`. Results, ZIPs and
logs stay local and ignored. F/G stay UNREVIEWED, 2:11 parent stays unresolved,
and R4.4 is not started.
