param(
    [switch]$SelfTest,
    [string]$TfData,
    [string]$Mr1,
    [string]$R3c3,
    [string]$Prov1,
    [string]$Hr1,
    [string]$Human,
    [string]$Out,
    [string]$Python
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $repo '.venv\Scripts\python.exe' }
if (-not $Out) {
    $mode = if ($SelfTest) { 'synthetic' } else { 'real' }
    $Out = Join-Path $repo ('results\r4_0_' + $mode + '_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
}
$runArgs = @('-B', '-X', 'utf8', (Join-Path $repo 'src\milal_r4_0_macro_boundary_inventory.py'), '--out', $Out)
if ($SelfTest) { $runArgs += '--self-test' }
else {
    if (-not $TfData) { throw 'Real R4.0 execution requires -TfData.' }
    $runArgs += @('--tf-data', $TfData)
    foreach ($item in @(@('mr1', $Mr1), @('r3c3', $R3c3), @('prov1', $Prov1), @('hr1', $Hr1), @('human', $Human))) {
        if ($item[1]) { $runArgs += @('--' + $item[0], $item[1]) }
    }
}
Write-Host 'R4.0 whole-book macro boundary candidate inventory'
& $Python @runArgs
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { Write-Error "R4.0 stopped with exit code $runExit" -ErrorAction Continue }
Write-Host "Result directory: $Out"
exit $runExit
