# HSA3-ANA.0.3 execution

Read [HANDOFF](HANDOFF.md), [specification](HSA3_ANA_0_3_SPEC.md),
[researcher request](HSA3_ANA_0_3_RESEARCHER_SOURCE.txt) and
[validation](HSA3_ANA_0_3_VALIDATION_REPORT.md).
No BHSA installation or corpus extraction is needed for this human-record stage.
Require the exact configured ANA.0.2 ZIP. Missing/hash-mismatched input stops.

From the repository root, first validate and inspect synthetic output:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& .venv/Scripts/python.exe -m unittest discover -s tests -p test_hsa3_ana_human_freeze.py -q
if ($LASTEXITCODE -ne 0) { throw 'ANA.0.3 tests failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_ana_0_3_windows.ps1 -SelfTest -Out "results/hsa3_ana_0_3_synthetic_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
Get-Content -Encoding UTF8 "results/hsa3_ana_0_3_synthetic_$stamp/08_ana_0_3_adjudication_report.md"
Get-Content -Encoding UTF8 "results/hsa3_ana_0_3_synthetic_$stamp/09_next_hsa3_seam_review_packet.md"
```

After synthetic inspection, perform the authorized frozen-artifact run and repeat:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
foreach ($suffix in @('real', 'repeat')) {
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_ana_0_3_windows.ps1 -Out "results/hsa3_ana_0_3_${suffix}_$stamp"
    if ($LASTEXITCODE -ne 0) { throw "Freeze failed: $suffix" }
}
$first = Get-FileHash "results/hsa3_ana_0_3_real_${stamp}_results.zip" -Algorithm SHA256
$repeat = Get-FileHash "results/hsa3_ana_0_3_repeat_${stamp}_results.zip" -Algorithm SHA256
if ($first.Hash -ne $repeat.Hash) { throw 'Independent ZIP rerun differs' }
Write-Host "PASS ZIP: $($first.Path) SHA256: $($first.Hash)"
```

CLI: `--out` (fresh path), `--self-test`, optional `--archive` for relocation
of the exact pinned ZIP. Self-test and archive override cannot be combined.
PowerShell also accepts `-Python`, defaulting to the repository venv.
No overwrite, network recovery, alternate evidence, fuzzy linkage or parentage
adjudication occurs. Results, ZIPs and logs stay ignored; code/config/specs/tests
and small researcher-supplied canonical records belong in Git.
