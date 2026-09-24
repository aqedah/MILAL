param([string]$Bhsa, [string]$Out, [string]$Python, [switch]$SelfTest, [string]$RegressionReceipt)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repoRoot '.venv\Scripts\python.exe' }
if (-not $Out) { $Out = Join-Path $repoRoot ('results\mfr01_windows_' + (Get-Date -Format 'yyyyMMdd_HHmmss')) }
if (-not $Bhsa) { $Bhsa = Join-Path $HOME 'text-fabric-data\github\etcbc\bhsa\tf\2021' }
if (-not $SelfTest) {
    foreach ($feature in @('otype.tf','oslots.tf','otext.tf')) {
        if (-not (Test-Path -LiteralPath (Join-Path $Bhsa $feature))) { throw "Missing BHSA feature: $feature" }
    }
}
& $Python -B -X utf8 -m unittest discover -s (Join-Path $repoRoot 'tests') -p test_mfr_0_1.py
if ($LASTEXITCODE -ne 0) { throw 'MFR unit/self tests failed' }
$pipeline = Join-Path $repoRoot 'src\milal_mfr_pipeline.py'
if (-not $SelfTest) {
    & $Python -B -X utf8 $pipeline --self-test --out ($Out + '_synthetic')
    if ($LASTEXITCODE -ne 0) { throw 'Synthetic MFR package failed' }
    if (-not $RegressionReceipt) {
        $RegressionReceipt = $Out + '_regression.json'
        & $Python -B -X utf8 $pipeline --regression-only $RegressionReceipt
        if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
    }
    & $Python -B -X utf8 $pipeline --bhsa $Bhsa --out $Out --regression-receipt $RegressionReceipt
} else {
    & $Python -B -X utf8 $pipeline --self-test --out $Out
}
exit $LASTEXITCODE
