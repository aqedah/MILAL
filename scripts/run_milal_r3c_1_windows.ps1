# Requires Windows PowerShell 5.1 or PowerShell 7. Keep src/ and config/ beside scripts/.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$R3b2Zip,
    [Parameter(Mandatory = $true)][string]$R3b3Zip,
    [Parameter(Mandatory = $true)][string]$TfDir,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [string]$PythonExe,
    [string]$ResultZip,
    [string]$PilotConfig,
    [int]$Seed,
    [string]$RunLog
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
# Native failures are handled explicitly, including on PowerShell 7.3+.
$PSNativeCommandUseErrorActionPreference = $false
$repoDir = Split-Path -Parent $PSScriptRoot
if (-not $PythonExe) { $PythonExe = Join-Path $repoDir '.venv\Scripts\python.exe' }
$scriptPath = Join-Path $repoDir 'src/milal_r3c_1_review_units.py'
if (-not $PilotConfig) { $PilotConfig = Join-Path $repoDir 'config/r3c_1_job_pilot.json' }

function Get-FullPath([string]$Path) {
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

function Write-RunLog([string]$Message) {
    Write-Host $Message
    Add-Content -LiteralPath $RunLog -Value $Message -Encoding UTF8 -ErrorAction Stop
}

function Invoke-Python([string[]]$Arguments) {
    Write-RunLog ('PYTHON ARGS: ' + (ConvertTo-Json -InputObject $Arguments -Compress))
    # Windows PowerShell represents redirected native stderr as ErrorRecord objects.
    # Continue lets us capture those messages and retain the actual process exit code.
    $savedPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & $PythonExe @Arguments 2>&1 | ForEach-Object { Write-RunLog ([string]$_) }
        $script:pythonStatus = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $savedPreference
    }
}

$logReady = $false
$pipelineStatus = 0
try {
    $OutputDir = Get-FullPath $OutputDir
    if (-not $ResultZip) { $ResultZip = $OutputDir + '_results.zip' }
    if (-not $RunLog) { $RunLog = $OutputDir + '_windows_run.log' }
    $ResultZip = Get-FullPath $ResultZip
    $RunLog = Get-FullPath $RunLog
    # Keep auxiliary files outside the output tree so its manifest stays valid.
    $outputPrefix = $OutputDir.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    foreach ($auxiliary in @($ResultZip, $RunLog)) {
        if ($auxiliary.Equals($OutputDir, [StringComparison]::OrdinalIgnoreCase) -or
            $auxiliary.StartsWith($outputPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'ResultZip and RunLog must be outside OutputDir.'
        }
    }
    if ($ResultZip.Equals($RunLog, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'ResultZip and RunLog must be different paths.'
    }
    foreach ($path in @($OutputDir, $ResultZip, $RunLog)) {
        if (Test-Path -LiteralPath $path) { throw "Choose a fresh path; existing path preserved: $path" }
    }
    [IO.Directory]::CreateDirectory((Split-Path -Parent $RunLog)) | Out-Null
    # Exclusive creation prevents accidentally overwriting an earlier log.
    $logStream = [IO.File]::Open($RunLog, 'CreateNew', 'Write', 'None')
    $logStream.Dispose()
    $logReady = $true
    $seedDisplay = 'from pilot configuration'
    if ($PSBoundParameters.ContainsKey('Seed')) { $seedDisplay = [string]$Seed }
    Write-RunLog "MILAL R3c.1 Windows; started=$([DateTime]::UtcNow.ToString('o')); seed=$seedDisplay"
    foreach ($path in @($PythonExe, $scriptPath, (Join-Path $repoDir 'src/milal_r3c_0_2_reviewability.py'), $PilotConfig, $R3b2Zip, $R3b3Zip,
                        (Join-Path $TfDir 'otype.tf'), (Join-Path $TfDir 'oslots.tf'))) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required file missing: $path" }
    }
    # Force UTF-8 for Hebrew output when Python writes into a PowerShell pipe.
    $oldPythonEncoding = $env:PYTHONIOENCODING
    $oldConsoleEncoding = [Console]::OutputEncoding
    try {
        $env:PYTHONIOENCODING = 'utf-8'
        [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
        Invoke-Python @($scriptPath, '--self-test')
        if ($script:pythonStatus -ne 0) {
            Write-RunLog "SELF-TEST STATUS: $script:pythonStatus; analysis not started."
            exit $script:pythonStatus
        }
        $analysisArgs = @($scriptPath, '--r3b2-zip', $R3b2Zip, '--r3b3-zip', $R3b3Zip,
            '--tf-dir', $TfDir, '--output-dir', $OutputDir, '--pilot-config', $PilotConfig)
        if ($PSBoundParameters.ContainsKey('Seed')) { $analysisArgs += @('--seed', [string]$Seed) }
        Invoke-Python $analysisArgs
        $pipelineStatus = $script:pythonStatus
        Write-RunLog "PIPELINE STATUS: $pipelineStatus"
        if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
            if ($pipelineStatus -ne 0) { exit $pipelineStatus }
            throw 'Python returned success but produced no output directory.'
        }
        [IO.Directory]::CreateDirectory((Split-Path -Parent $ResultZip)) | Out-Null
        # Single quotes inside Python survive legacy Windows PowerShell native quoting.
        $zipCode = 'import pathlib,sys,zipfile; root=pathlib.Path(sys.argv[1]); z=zipfile.ZipFile(sys.argv[2], ''x'', compression=zipfile.ZIP_DEFLATED); [z.write(p, p.relative_to(root.parent)) for p in sorted(root.rglob(''*'')) if p.is_file()]; z.close()'
        Invoke-Python @('-c', $zipCode, $OutputDir, $ResultZip)
        $zipStatus = $script:pythonStatus
        Write-RunLog "ZIP STATUS: $zipStatus; RESULT: $ResultZip; RUN LOG: $RunLog"
        if ($pipelineStatus -ne 0) { exit $pipelineStatus }
        exit $zipStatus
    } finally {
        $env:PYTHONIOENCODING = $oldPythonEncoding
        [Console]::OutputEncoding = $oldConsoleEncoding
    }
} catch {
    $message = "ERROR: $($_.Exception.Message)"
    if ($logReady) { Write-RunLog $message } else { Write-Host $message }
    if ($pipelineStatus -ne 0) { exit $pipelineStatus }
    exit 2
}

