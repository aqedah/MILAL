# HSA3-D/E execution

Read [HANDOFF](HANDOFF.md), [specification](HSA3_DE_SPEC.md),
[researcher request](HSA3_DE_RESEARCHER_SOURCE.txt) and
[validation](HSA3_DE_VALIDATION_REPORT.md).
This consumes the exact configured ANA.0.3 ZIP; no BHSA load or new lexical scan.
Run from the repository root:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& .venv/Scripts/python.exe -m unittest discover -s tests -p test_hsa3_de_seam_adjudication.py -q
if ($LASTEXITCODE -ne 0) { throw 'HSA3-D/E tests failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_de_windows.ps1 -SelfTest -Out "results/hsa3_de_synthetic_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
Get-Content -Encoding UTF8 "results/hsa3_de_synthetic_$stamp/08_hsa3_de_adjudication_report.md"
Get-Content -Encoding UTF8 "results/hsa3_de_synthetic_$stamp/09_hsa3_remaining_seams_review_packet.md"
```

After synthetic inspection, within the authorized frozen-artifact scope:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
foreach ($suffix in @('real', 'repeat')) {
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_de_windows.ps1 -Out "results/hsa3_de_${suffix}_$stamp"
    if ($LASTEXITCODE -ne 0) { throw "HSA3-D/E failed: $suffix" }
}
$first = Get-FileHash "results/hsa3_de_real_${stamp}_results.zip" -Algorithm SHA256
$repeat = Get-FileHash "results/hsa3_de_repeat_${stamp}_results.zip" -Algorithm SHA256
if ($first.Hash -ne $repeat.Hash) { throw 'Independent rerun differs' }
Write-Host "PASS ZIP: $($first.Path) SHA256: $($first.Hash)"
```

CLI: `--out` (fresh path), `--self-test`, optional `--archive` to relocate the
same pinned ZIP. No alternate archive hash is accepted. Self-test and archive
override cannot be combined. The PowerShell runner accepts `-Python`, defaulting
to the repository venv. Git baseline ancestry and 116 frozen file hashes are
checked. Source inputs, ZIPs and outputs are never rewritten.
