param(
    [switch]$SelfTest,
    [string]$TfData,
    [string]$HistoricalDir,
    [string]$HistoricalScript,
    [string]$HistoricalConfig,
    [string]$Out,
    [string]$Python
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not $Out) {
    $mode = if ($SelfTest) { 'synthetic' } else { 'real' }
    $Out = Join-Path $repo ('results\mr1_' + $mode + '_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
}
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_mr1_surface_marker_provenance.py'), '--out', $Out)
if ($SelfTest) {
    $runArgs += '--self-test'
} else {
    if (-not $TfData -or -not $HistoricalDir -or -not $HistoricalScript -or -not $HistoricalConfig) {
        throw 'Real execution requires TfData, HistoricalDir, HistoricalScript, HistoricalConfig.'
    }
    $runArgs += @('--tf-data', $TfData, '--historical-dir', $HistoricalDir, '--historical-script', $HistoricalScript, '--historical-config', $HistoricalConfig)
}
Write-Host 'MR1 surface marker provenance reproduction'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { Write-Error "MR1 stopped with exit code $runExit" -ErrorAction Continue }
Write-Host "Result directory: $Out"
exit $runExit
