param([string]$Out,[string]$InputZip,[string]$Python,[switch]$SelfTest,[string]$RegressionReceipt)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repoRoot '.venv\Scripts\python.exe' }
if (-not $Out) { $Out = Join-Path $repoRoot ('results\mfr02a_windows_' + (Get-Date -Format 'yyyyMMdd_HHmmss')) }
$pipeline = Join-Path $repoRoot 'src\milal_mfr02a_pipeline.py'
& $Python -B -X utf8 -m unittest discover -s (Join-Path $repoRoot 'tests') -p test_mfr_0_2a.py
if ($LASTEXITCODE -ne 0) { throw 'MFR.0.2A stage tests failed' }
if ($SelfTest) { & $Python -B -X utf8 $pipeline --self-test --out $Out; exit $LASTEXITCODE }
& $Python -B -X utf8 $pipeline --self-test --out ($Out + '_synthetic')
if ($LASTEXITCODE -ne 0) { throw 'Synthetic serialization failed' }
if (-not $RegressionReceipt) {
    $RegressionReceipt = $Out + '_regression.json'
    & $Python -B -X utf8 $pipeline --regression-only $RegressionReceipt
    if ($LASTEXITCODE -ne 0) { throw 'Regression failed' }
}
$receipt = Get-Content -LiteralPath $RegressionReceipt -Raw | ConvertFrom-Json
if ($receipt.tests_run -lt 2152 -or $receipt.failures -ne 0 -or $receipt.errors -ne 0 -or $receipt.skipped -ne 0) { throw 'Regression receipt is not PASS' }
if ($InputZip) { & $Python -B -X utf8 $pipeline --input $InputZip --out $Out }
else { & $Python -B -X utf8 $pipeline --out $Out }
exit $LASTEXITCODE
