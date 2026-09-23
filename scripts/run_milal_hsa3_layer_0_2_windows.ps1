param([switch]$SelfTest, [string]$Archive, [string]$Out, [string]$Python)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python not found: $Python" }
if ($SelfTest -and $Archive) { throw 'SelfTest cannot use a real archive.' }
if (-not $Out) { $Out = Join-Path $repo ('results\hsa3_layer_0_2_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_hsa3_layer_0_2.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
if ($Archive) { $runArgs += @('--archive', $Archive) }
Write-Host 'HSA3-LAYER.0.2: Human necessity freeze; historical parents unchanged; no R4.4'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { Write-Error "HSA3-LAYER.0.2 stopped: $runExit" -ErrorAction Continue }
else {
    Write-Host "Results: $Out"
    Write-Host "ZIP: ${Out}_results.zip"
    Write-Host "Review packet: $Out\05_hsa3_layered_completion_summary.md"
}
exit $runExit
