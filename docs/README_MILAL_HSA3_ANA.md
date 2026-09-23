# HSA3-ANA.0.1 execution

Read [specification](HSA3_ANA_0_1_SPEC.md), [HANDOFF](HANDOFF.md) and
[validation report](HSA3_ANA_0_1_VALIDATION_REPORT.md). This is a source audit,
not an A–G parentage decision. Actual BHSA execution was explicitly authorized.

Use the exact configured twelve accepted artifact ZIPs, including
`results/hsa3_prep_global_seams_final2_20260922_a_results.zip`. Preflight fails
on missing files, SHA/CRC/manifest mismatches or changed frozen files; it never
substitutes other runs. Install Text-Fabric 13.1.0 and provide external BHSA 2021.
The runner defaults to the current user's standard Text-Fabric data location;
`-TfData` overrides it. No data is downloaded automatically.

From the repository root in PowerShell:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& .venv/Scripts/python.exe -m unittest discover -s tests -p test_hsa3_ana_response_frame.py -q
if ($LASTEXITCODE -ne 0) { throw 'ANA tests failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_ana_windows.ps1 -SelfTest -Out "results/hsa3_ana_synthetic_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
Write-Host "Inspect results/hsa3_ana_synthetic_$stamp/08_ana_response_frame_review_packet.md before real execution."
```

After inspecting synthetic output, within the authorized empirical scope:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$anaTfData = Join-Path $HOME 'text-fabric-data/github/etcbc/bhsa/tf/2021'
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_ana_windows.ps1 -TfData $anaTfData -Out "results/hsa3_ana_real_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Real audit failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_ana_windows.ps1 -TfData $anaTfData -Out "results/hsa3_ana_repeat_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Repeat audit failed' }
$anaFirst = Get-FileHash "results/hsa3_ana_real_${stamp}_results.zip" -Algorithm SHA256
$anaRepeat = Get-FileHash "results/hsa3_ana_repeat_${stamp}_results.zip" -Algorithm SHA256
if ($anaFirst.Hash -ne $anaRepeat.Hash) { throw 'Independent rerun differs' }
Write-Host "PASS: $($anaFirst.Path) SHA256=$($anaFirst.Hash)"
```

The Python CLI accepts `--out`, `--tf-data`, and `--self-test`; output paths must
not exist. Results, ZIP and log remain ignored by Git. Fixed ZIP timestamps and
canonical serialization permit byte comparison on the same source paths/runtime.
Metadata intentionally retains exact local TF paths, so cross-machine archive
byte equality is not claimed. No reviewer response is filled automatically.
