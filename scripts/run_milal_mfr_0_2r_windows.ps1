param(
    [Parameter(Mandatory=$true)][string]$TfPath,
    [Parameter(Mandatory=$true)][string]$RunRoot,
    [string]$Python = ''
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
$entry = Join-Path $repo 'src\milal_mfr02r_pipeline.py'
if (Test-Path -LiteralPath $RunRoot) { throw 'RunRoot must be a new directory; existing artifacts are preserved.' }
New-Item -ItemType Directory -Path $RunRoot | Out-Null
function Invoke-Stage([string[]]$StageArgs) {
    & $Python -B -X utf8 $entry @StageArgs
    if ($LASTEXITCODE -ne 0) { throw "MFR.0.2R stage failed: $StageArgs" }
}
Invoke-Stage @('--self-test', '--out', (Join-Path $RunRoot 'synthetic'))
Invoke-Stage @('--regression-only', (Join-Path $RunRoot 'regression.json'))
Invoke-Stage @('--prepare', '--tf-path', $TfPath, '--projection', (Join-Path $RunRoot 'projection'))
foreach ($label in @('a', 'b')) {
    Invoke-Stage @('--out', (Join-Path $RunRoot $label), '--projection', (Join-Path $RunRoot 'projection'), '--regression-receipt', (Join-Path $RunRoot 'regression.json'))
}
Invoke-Stage @('--release', (Join-Path $RunRoot 'a'), (Join-Path $RunRoot 'b'))
Write-Output "Verified results: $(Join-Path $RunRoot 'a_results.zip')"
