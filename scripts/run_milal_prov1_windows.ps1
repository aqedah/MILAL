# PROV1 derives a sidecar from frozen outputs; no BHSA/R1/R2 execution.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Generator,
    [Parameter(Mandatory=$true)][string]$R2Zip,
    [Parameter(Mandatory=$true)][string]$R3b2Zip,
    [Parameter(Mandatory=$true)][string]$R3b3Zip,
    [Parameter(Mandatory=$true)][string]$R3c3Zip,
    [Parameter(Mandatory=$true)][string]$OutputDir,
    [string]$PythonExe
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repoDir = Split-Path -Parent $PSScriptRoot
if (-not $PythonExe) { $PythonExe = Join-Path $repoDir '.venv\Scripts\python.exe' }
$scriptPath = Join-Path $repoDir 'src\milal_prov1_signature_provenance.py'
try {
    foreach ($file in @($PythonExe,$Generator,$R2Zip,$R3b2Zip,$R3b3Zip,$R3c3Zip)) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing input/interpreter: $file" }
    }
    if (Test-Path -LiteralPath $OutputDir) { throw 'OutputDir must be new.' }
    & $PythonExe -B $scriptPath --self-test
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $PythonExe -B $scriptPath --generator $Generator --r2 $R2Zip --b2 $R3b2Zip --b3 $R3b3Zip --c3 $R3c3Zip --output-dir $OutputDir
    exit $LASTEXITCODE
} catch {
    Write-Error $_ -ErrorAction Continue
    exit 1
}
