param([switch]$SelfTest, [string]$TfData, [string]$Out, [string]$Python)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not $Out) { $Out = Join-Path $repo ('results\r4_2_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_r4_2_participant_audit.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
else {
    if (-not $TfData) { throw 'Real R4.2 execution requires -TfData.' }
    $runArgs += @('--tf-data', $TfData)
}
Write-Host 'R4.2 participant transition and enclosure audit'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { Write-Error "R4.2 stopped: $runExit" -ErrorAction Continue }
Write-Host "Result directory: $Out"
exit $runExit
