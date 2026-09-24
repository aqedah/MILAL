param([switch]$SelfTest, [string]$TfData, [string]$Out, [string]$Python, [string]$Archive)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python not found: $Python" }
if (-not $Out) { $Out = Join-Path $repo ('results\r4_4_contract_jin_0_2_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
if (-not $SelfTest -and -not $TfData) { throw 'Real mode requires -TfData with the exact external BHSA 2021 directory.' }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_jin_audit_pipeline.py'), '--config', (Join-Path $repo 'config\r4_4_contract_jin_0_2_job.json'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
if ($TfData) { $runArgs += @('--tf-data', $TfData) }
if ($Archive) { $runArgs += @('--archive', $Archive) }
Write-Host 'JIN.0.2: isolated blind discovery, freeze, then human/native comparison'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -eq 0) {
    Write-Host "Results: $Out"
    Write-Host "ZIP: ${Out}_results.zip"
    Write-Host "Physical source access log: ${Out}_run.log"
}
exit $runExit
