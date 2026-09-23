# Run HSA3-FG-PREP

See [specification](HSA3_FG_PREP_SPEC.md) and
[validation receipt](HSA3_FG_PREP_VALIDATION_REPORT.md).
This stage requires the pinned A/C and MR1 ZIPs plus external BHSA 2021.
It generates evidence only. No F/G decision or R4.4 is authorized.

Run from repository-root PowerShell:

```powershell
$ErrorActionPreference = 'Stop'
& .venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
& scripts\run_milal_hsa3_fg_prep_windows.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
```

Inspect the synthetic packet, then run the authorized empirical audit:

```powershell
$ErrorActionPreference = 'Stop'
$tag = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$first = Join-Path $PWD "results\hsa3_fg_prep_real_$tag"
$repeat = Join-Path $PWD "results\hsa3_fg_prep_repeat_$tag"
& scripts\run_milal_hsa3_fg_prep_windows.ps1 -Out $first
if ($LASTEXITCODE -ne 0) { throw 'Real audit failed' }
& scripts\run_milal_hsa3_fg_prep_windows.ps1 -Out $repeat
if ($LASTEXITCODE -ne 0) { throw 'Independent rerun failed' }
$one = (Get-FileHash "${first}_results.zip" -Algorithm SHA256).Hash
$two = (Get-FileHash "${repeat}_results.zip" -Algorithm SHA256).Hash
if ($one -ne $two) { throw 'Deterministic ZIP check failed' }
Write-Host "SHA256 $one"
Write-Host "Packet: $first\11_hsa3_fg_prep_review_packet.md"
```

The runner defaults to `.venv\Scripts\python.exe` and the user's standard
`text-fabric-data\github\etcbc\bhsa\tf\2021` directory. Use `-Python` and
`-TfData` for explicit alternatives. Output paths must be new. Logs, result ZIPs,
source snapshots and BHSA data stay local/ignored, not in Git.
