# HSA3-ANA.0.2 execution

Read [HANDOFF](HANDOFF.md), [specification](HSA3_ANA_0_2_SPEC.md),
[criteria draft](HSA_ADJUDICATION_CRITERIA_REGISTRY.md), and
[validation](HSA3_ANA_0_2_VALIDATION_REPORT.md).
This stage produces additional evidence only; human judgments stay unchanged.

Require the exact configured 0.1 ZIP and the existing BHSA 2021 data used for it.
Preflight checks its SHA256, CRC, manifest and accepted-state invariants. Missing
or mismatched inputs stop. A fresh BHSA snapshot must match frozen 0.1 source
bytes/hashes. Do not regenerate 0.1 or substitute another run.

From the repository root, PowerShell:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& .venv/Scripts/python.exe -m unittest discover -s tests -p test_hsa3_ana_response_family_addendum.py -q
if ($LASTEXITCODE -ne 0) { throw 'ANA.0.2 tests failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_ana_0_2_windows.ps1 -SelfTest -Out "results/hsa3_ana_0_2_synthetic_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic audit failed' }
Write-Host "Inspect results/hsa3_ana_0_2_synthetic_$stamp/11_ana_0_2_review_packet.md before real execution."
```

After inspecting synthetic output, within the researcher's authorized real scope:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$anaFamilyData = Join-Path $HOME 'text-fabric-data/github/etcbc/bhsa/tf/2021'
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_ana_0_2_windows.ps1 -TfData $anaFamilyData -Out "results/hsa3_ana_0_2_real_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Real audit failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_ana_0_2_windows.ps1 -TfData $anaFamilyData -Out "results/hsa3_ana_0_2_repeat_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Repeat audit failed' }
$anaFamilyFirst = Get-FileHash "results/hsa3_ana_0_2_real_${stamp}_results.zip" -Algorithm SHA256
$anaFamilyRepeat = Get-FileHash "results/hsa3_ana_0_2_repeat_${stamp}_results.zip" -Algorithm SHA256
if ($anaFamilyFirst.Hash -ne $anaFamilyRepeat.Hash) { throw 'Independent rerun differs' }
Write-Host "PASS: $($anaFamilyFirst.Path) SHA256=$($anaFamilyFirst.Hash)"
```

CLI: `--out`, `--tf-data`, `--self-test`. The PowerShell runner additionally
accepts `-Python`, defaults to the repository venv and current user's standard
Text-Fabric path. Output paths must not exist. Text-Fabric 13.1.0 is required.
No automatic data download occurs. Synthetic fixtures are explicitly invented
counterparts; their smaller counts are not empirical claims.

Byte-identical reruns are verified on the same paths/runtime. Cross-machine
archive byte equality is not claimed because exact local paths are provenance.
Source/root ambiguity and unresolved semantic readings remain visible in outputs.
