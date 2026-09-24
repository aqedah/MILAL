param([Parameter(Mandatory=$true)][string]$Out, [switch]$SelfTest, [string]$Python)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repoRoot '.venv\Scripts\python.exe' }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repoRoot 'src\milal_jin_contract_freeze.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
& $Python @runArgs
exit $LASTEXITCODE
