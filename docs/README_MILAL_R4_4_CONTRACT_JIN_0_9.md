# Run JIN.0.9

Read [specification](R4_4_CONTRACT_JIN_0_9_SPEC.md). Use unused output names.
The runner rejects existing output/work directories and never overwrites results.
Real input is raw external BHSA 2021 plus the SHA256-pinned JIN.0.8 release archive.

After syntax, stage tests and full regression with zero skips:

```powershell
$ErrorActionPreference = 'Stop'
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_jin_top_level_windows.ps1 -SelfTest -Out .\results\jin09_synthetic_new
if ($LASTEXITCODE -ne 0) { throw 'Synthetic failed' }
```

Inspect the synthetic S/M candidates and review packet before real execution.

```powershell
$ErrorActionPreference = 'Stop'
$tfData = Join-Path $HOME 'text-fabric-data\github\etcbc\bhsa\tf\2021'
foreach ($feature in @('otype.tf','oslots.tf','otext.tf')) {
    if (-not (Test-Path -LiteralPath (Join-Path $tfData $feature))) { throw "Missing $feature" }
}
foreach ($runName in @('jin09_real_new_a','jin09_real_new_b')) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_jin_top_level_windows.ps1 -TfData $tfData -Out (Join-Path '.\results' $runName)
    if ($LASTEXITCODE -ne 0) { throw "Run failed: $runName" }
}
Get-FileHash .\results\jin09_real_new_a_results.zip, .\results\jin09_real_new_b_results.zip -Algorithm SHA256
```

PowerShell policy override applies only to the child process. Python defaults to
the repository `.venv`; pass `-Python` to override. Raw BHSA is never committed.

Termux, with equivalent pinned local inputs and validation prerequisites:

```bash
cd ~/MILAL
git pull --ff-only
tf_data="$HOME/text-fabric-data/github/ETCBC/bhsa/tf/2021"
test -f "$tf_data/otype.tf" && test -f "$tf_data/oslots.tf" && test -f "$tf_data/otext.tf" || exit 1
bash scripts/run_milal_jin_top_level_termux.sh --self-test --out results/jin09_termux_synthetic_new
# Inspect the synthetic output before the following real run.
bash scripts/run_milal_jin_top_level_termux.sh --tf-data "$tf_data" --out results/jin09_termux_real_new
sha256sum results/jin09_termux_real_new_results.zip
```

The case-sensitive Termux directory must match the actual installed BHSA directory;
set `tf_data` explicitly if it uses lowercase `etcbc`. No download fallback occurs.
Termux and Windows share the Python implementation, schemas and deterministic ZIP
format. Termux empirical verification is not claimed without actual supplied results.
