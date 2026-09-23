# Execute HSA3-LAYER.0.1

This audit projects frozen HSA3 evidence and proposes parentage necessity for
human review. It performs no fresh BHSA extraction or structural adjudication.
See [specification](HSA3_LAYER_0_1_SPEC.md) and
[validation receipt](HSA3_LAYER_0_1_VALIDATION_REPORT.md).

From the repository root, use one PowerShell block with a fresh output prefix:

```powershell
$ErrorActionPreference = 'Stop'
$repo = (Get-Location).Path
$py = Join-Path $repo '.venv\Scripts\python.exe'
$stage = Join-Path $repo 'src\milal_hsa3_layer_0_1.py'
$prefix = Join-Path $repo ('results\hsa3_layer_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
Write-Host 'Syntax and full regression'
& $py -m py_compile $stage
if ($LASTEXITCODE) { throw 'Syntax failed' }
& $py -m unittest discover -s tests
if ($LASTEXITCODE) { throw 'Regression failed' }
Write-Host 'Synthetic self-test and review packet'
& $py -X utf8 $stage --self-test --out "${prefix}_synthetic"
if ($LASTEXITCODE) { throw 'Synthetic failed' }
Get-Content -Encoding utf8 "${prefix}_synthetic\16_researcher_review_packet.md"
Get-Content -Encoding utf8 "${prefix}_synthetic\13_hsa3_complete_layered_summary.md"
Write-Host 'Real frozen evidence and independent rerun'
& $py -X utf8 $stage --out "${prefix}_real"
if ($LASTEXITCODE) { throw 'Real validation failed' }
& $py -X utf8 $stage --out "${prefix}_repeat"
if ($LASTEXITCODE) { throw 'Repeat failed' }
$firstHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "${prefix}_real_results.zip").Hash
$secondHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "${prefix}_repeat_results.zip").Hash
if ($firstHash -ne $secondHash) { throw 'Rerun mismatch' }
Write-Host "PASS: ${prefix}_real_results.zip"
Write-Host "SHA256: $firstHash"
Write-Host "Review: ${prefix}_real\16_researcher_review_packet.md"
```

Windows runner options: `-SelfTest`, `-Archive`, `-Out`, `-Python`.
Python CLI: `--self-test`, `--archive`, `--out`. Alternate archive paths must match
the exact configured SHA256; substitute sources are rejected. Paths derive from
the repository root. Results/logs/ZIPs remain local ignored artifacts.
