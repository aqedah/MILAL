# Execute HSA3-F/G

This records the supplied final human seam decisions using the pinned FG-PREP
ZIP. It does not run a new BHSA extraction or begin R4.4. See
[specification](HSA3_FG_SPEC.md) and [validation receipt](HSA3_FG_VALIDATION_REPORT.md).

From the repository root, run this single PowerShell block. It performs tests,
synthetic validation and two independent real invocations; real execution is
already authorized in the exact researcher request. Use a fresh output prefix.

```powershell
$ErrorActionPreference = 'Stop'
$repo = (Get-Location).Path
$py = Join-Path $repo '.venv\Scripts\python.exe'
$stage = Join-Path $repo 'src\milal_hsa3_fg_final_adjudication.py'
$prefix = Join-Path $repo ('results\hsa3_fg_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
Write-Host 'Syntax and full regression'
& $py -m py_compile $stage
if ($LASTEXITCODE) { throw 'Syntax failed' }
& $py -m unittest discover -s tests
if ($LASTEXITCODE) { throw 'Regression failed' }
Write-Host 'Synthetic self-test'
& $py -X utf8 $stage --self-test --out "${prefix}_synthetic"
if ($LASTEXITCODE) { throw 'Synthetic failed' }
Get-Content -Encoding utf8 "${prefix}_synthetic\08_hsa3_fg_final_report.md"
Get-Content -Encoding utf8 "${prefix}_synthetic\09_hsa3_complete_review_summary.md"
Write-Host 'Real frozen evidence and independent rerun'
& $py -X utf8 $stage --out "${prefix}_real"
if ($LASTEXITCODE) { throw 'Real validation failed' }
& $py -X utf8 $stage --out "${prefix}_repeat"
if ($LASTEXITCODE) { throw 'Independent rerun failed' }
$firstHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "${prefix}_real_results.zip").Hash
$secondHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "${prefix}_repeat_results.zip").Hash
if ($firstHash -ne $secondHash) { throw 'Deterministic rerun mismatch' }
Write-Host "PASS: ${prefix}_real_results.zip"
Write-Host "SHA256: $firstHash"
Write-Host "Summary: ${prefix}_real\09_hsa3_complete_review_summary.md"
```

The runner supports `-SelfTest`, `-Archive`, `-Out`, `-Python`; Python CLI supports
`--self-test`, `--archive`, `--out`. An alternate archive path must have the exact
configured SHA256; it does not authorize substitute evidence. Default Python and
result paths derive from repository root. Generated artifacts remain ignored.
