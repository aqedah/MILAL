param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$Archive,
    [Parameter(Mandatory=$true)][string]$RunRoot,
    [string]$Python = ''
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (Test-Path -LiteralPath $RunRoot) { throw 'Use a fresh RunRoot; existing results are preserved.' }
New-Item -ItemType Directory -Path $RunRoot | Out-Null
$entry = Join-Path $repo 'src\milal_h0_runner.py'
function Invoke-H0([string[]]$StageArgs) {
    & $Python -B -X utf8 $entry @StageArgs
    if ($LASTEXITCODE -ne 0) { throw "H0 failed: $StageArgs" }
}
Invoke-H0 @('--self-test','--out',(Join-Path $RunRoot 'synthetic'))
& $Python -B -X utf8 (Join-Path $repo 'src\milal_mfr02r_pipeline.py') --regression-only (Join-Path $RunRoot 'regression.json')
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed.' }
foreach ($label in @('a','b')) {
    Invoke-H0 @('--source',$Source,'--archive',$Archive,'--out',(Join-Path $RunRoot $label),'--regression-receipt',(Join-Path $RunRoot 'regression.json'))
}
Invoke-H0 @('--release',(Join-Path $RunRoot 'a'),(Join-Path $RunRoot 'b'))
Write-Output "H0 result: $(Join-Path $RunRoot 'a_results.zip'); inspect warnings before human-stage readiness."
