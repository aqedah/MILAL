param([Parameter(Mandatory=$true)][string]$Out, [switch]$SelfTest, [string]$Python, [string]$TfData)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repoRoot '.venv\Scripts\python.exe' }
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repoRoot 'src\milal_jin_top_level_pipeline.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' } else {
    if (-not $TfData) { $TfData = Join-Path $HOME 'text-fabric-data\github\etcbc\bhsa\tf\2021' }
    $runArgs += @('--tf-data', $TfData)
}
& $Python @runArgs
exit $LASTEXITCODE
