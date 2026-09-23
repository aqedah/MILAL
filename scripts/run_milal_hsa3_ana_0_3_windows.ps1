param([switch]$SelfTest, [string]$Archive, [string]$Out, [string]$Python)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python not found: $Python" }
if ($SelfTest -and $Archive) { throw 'SelfTest cannot use an empirical archive.' }
if (-not $Out) { $Out = Join-Path $repo ('results\hsa3_ana_0_3_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_hsa3_ana_human_freeze.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
if ($Archive) { $runArgs += @('--archive', $Archive) }
Write-Host 'HSA3-ANA.0.3 researcher adjudication freeze; Q3 deferred'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { Write-Error "HSA3-ANA.0.3 stopped: $runExit" -ErrorAction Continue }
else {
    Write-Host "Results: $Out"
    Write-Host "ZIP: ${Out}_results.zip"
    Write-Host "Log: ${Out}_run.log"
}
exit $runExit
