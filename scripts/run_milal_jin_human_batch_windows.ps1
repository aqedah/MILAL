param([switch]$SelfTest, [string]$Out, [string]$Python)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "Python not found: $Python" }
if (-not $Out) { $Out = Join-Path $repo ('results\jin_human_batch1_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff')) }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_jin_human_batch.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
& $Python @runArgs
exit $LASTEXITCODE
