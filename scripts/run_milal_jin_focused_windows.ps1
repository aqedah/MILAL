param([switch]$SelfTest, [string]$TfData, [string]$Out, [string]$Python)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python not found: $Python" }
if (-not $SelfTest -and -not $TfData) { throw 'Real mode requires exact external BHSA 2021 -TfData' }
if (-not $Out) { $Out = Join-Path $repo ('results\jin05_focused_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_jin_focused_pipeline.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
if ($TfData) { $runArgs += @('--tf-data', $TfData) }
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -eq 0) { Write-Host "Results: $Out"; Write-Host "ZIP: ${Out}_results.zip"; Write-Host "Source read log: ${Out}_run.log" }
exit $runExit
