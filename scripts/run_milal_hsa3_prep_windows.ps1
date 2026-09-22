param([switch]$SelfTest, [string]$Out, [string]$Python)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python not found: $Python" }
if (-not $Out) { $Out = Join-Path $repo ('results\hsa3_prep_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_hsa3_prep_global_seams.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
Write-Host 'HSA3-PREP unresolved-parentage triage and global seam audit'
Write-Host 'The Python preflight verifies frozen sources and required accepted artifact hashes before review-only triage.'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { Write-Error "HSA3-PREP stopped: $runExit" -ErrorAction Continue }
else {
    Write-Host "Results: $Out"
    Write-Host "ZIP: ${Out}_results.zip"
    Write-Host "Log: ${Out}_run.log"
}
exit $runExit
