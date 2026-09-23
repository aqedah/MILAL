param([switch]$SelfTest, [string]$TfData, [string]$Out, [string]$Python)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python not found: $Python" }
if (-not $Out) { $Out = Join-Path $repo ('results\hsa3_ana_0_2_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_hsa3_ana_response_family_addendum.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
else {
    if (-not $TfData) { $TfData = Join-Path $HOME 'text-fabric-data\github\etcbc\bhsa\tf\2021' }
    if (-not (Test-Path -LiteralPath $TfData -PathType Container)) { throw "BHSA 2021 not found: $TfData" }
    $runArgs += @('--tf-data', $TfData)
}
Write-Host 'HSA3-ANA.0.2 lexical-family addendum and criteria draft'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { Write-Error "HSA3-ANA.0.2 stopped: $runExit" -ErrorAction Continue }
else {
    Write-Host "Results: $Out"
    Write-Host "ZIP: ${Out}_results.zip"
    Write-Host "Log: ${Out}_run.log"
}
exit $runExit
