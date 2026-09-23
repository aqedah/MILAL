# HSA3-LAYER.0.2 execution

See [specification](HSA3_LAYER_0_2_SPEC.md) and
[validation report](HSA3_LAYER_0_2_VALIDATION_REPORT.md).
This records researcher-supplied necessity judgments; it creates no parent edge.
Real execution requires the exact upstream ZIP in the configured results path
or an explicit `-Archive` pointing to identical bytes. No BHSA install is needed.
Repository defaults are relative to the runner's repository root.

```powershell
$ErrorActionPreference = 'Stop'
$repo = (Get-Location).Path
$python = Join-Path $repo '.venv\Scripts\python.exe'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& $python -m py_compile src/milal_hsa3_layer_0_2.py tests/test_hsa3_layer_0_2.py
if ($LASTEXITCODE -ne 0) { throw 'Syntax validation failed' }
& $python -B -X utf8 -m unittest discover -s tests -p test_hsa3_layer_0_2.py -v
if ($LASTEXITCODE -ne 0) { throw 'Stage tests failed' }
& $python -B -X utf8 -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Regression failed' }
& .\scripts\run_milal_hsa3_layer_0_2_windows.ps1 -SelfTest -Out "results\hsa3_layer_0_2_synthetic_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Self-test failed' }
Write-Host "Inspect synthetic reports 04–07 in results\hsa3_layer_0_2_synthetic_$stamp before real execution."
```

After synthetic inspection, within the authorized frozen-real scope:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$first = "results\hsa3_layer_0_2_real_$stamp"
$repeat = "results\hsa3_layer_0_2_repeat_$stamp"
& .\scripts\run_milal_hsa3_layer_0_2_windows.ps1 -Out $first
if ($LASTEXITCODE -ne 0) { throw 'Real run failed' }
& .\scripts\run_milal_hsa3_layer_0_2_windows.ps1 -Out $repeat
if ($LASTEXITCODE -ne 0) { throw 'Repeat failed' }
if ((Get-FileHash "${first}_results.zip").Hash -ne (Get-FileHash "${repeat}_results.zip").Hash) { throw 'ZIP mismatch' }
Write-Host "Summary: $first\05_hsa3_layered_completion_summary.md"
Get-FileHash "${first}_results.zip" -Algorithm SHA256
```

CLI equivalents accept `--self-test`, `--archive`, and required `--out`.
The synthetic and archive options are mutually exclusive. Output must be fresh.
Generated files and input ZIPs remain local/ignored. Do not commit them.
