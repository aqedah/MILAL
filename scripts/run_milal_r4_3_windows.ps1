param([switch]$SelfTest, [string]$Out, [string]$Python)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python not found: $Python" }
if (-not $Out) { $Out = Join-Path $repo ('results\r4_3_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_r4_3_hierarchy_scaffold.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
Write-Host 'R4.3 human-grounded partial hierarchy scaffold'
Write-Host 'The Python preflight verifies frozen sources and required accepted artifact hashes before compilation.'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { Write-Error "R4.3 stopped: $runExit" -ErrorAction Continue }
else {
    Write-Host "Results: $Out"
    Write-Host "ZIP: ${Out}_results.zip"
    Write-Host "Log: ${Out}_run.log"
}
exit $runExit
