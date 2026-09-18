# R3c.2 reads a frozen result ZIP. No BHSA installation or configuration is needed.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$R3c1Zip,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [string]$PythonExe,
    [string]$ResultZip,
    [string]$RunLog
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$repoDir = Split-Path -Parent $PSScriptRoot
if (-not $PythonExe) { $PythonExe = Join-Path $repoDir '.venv\Scripts\python.exe' }
$scriptPath = Join-Path $repoDir 'src/milal_r3c_2_compact_review.py'

function Get-FullPath([string]$Path) {
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

function Write-RunLog([string]$Message) {
    Write-Host $Message
    Add-Content -LiteralPath $RunLog -Value $Message -Encoding UTF8 -ErrorAction Stop
}

function Invoke-Python([string[]]$Arguments) {
    Write-RunLog ('PYTHON ARGS: ' + (ConvertTo-Json -InputObject $Arguments -Compress))
    $savedPreference = $ErrorActionPreference
    try {
        # PS 5.1 wraps redirected native stderr; capture it without losing exit codes.
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
    $R3c1Zip = Get-FullPath $R3c1Zip
    if (-not $ResultZip) { $ResultZip = $OutputDir + '_results.zip' }
    if (-not $RunLog) { $RunLog = $OutputDir + '_windows_run.log' }
    $ResultZip = Get-FullPath $ResultZip
    $RunLog = Get-FullPath $RunLog
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
    $logStream = [IO.File]::Open($RunLog, 'CreateNew', 'Write', 'None')
    $logStream.Dispose()
    $logReady = $true
    Write-RunLog "MILAL R3c.2 Windows presentation; started=$([DateTime]::UtcNow.ToString('o'))"
    foreach ($path in @($PythonExe, $scriptPath, $R3c1Zip,
                        (Join-Path $repoDir 'src/milal_r3c_0_2_reviewability.py'),
                        (Join-Path $repoDir 'src/milal_r3c_1_review_units.py'))) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required file missing: $path" }
    }
    $oldPythonEncoding = $env:PYTHONIOENCODING
    $oldConsoleEncoding = [Console]::OutputEncoding
    try {
        $env:PYTHONIOENCODING = 'utf-8'
        [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
        Invoke-Python @($scriptPath, '--self-test')
        if ($script:pythonStatus -ne 0) {
            Write-RunLog "SELF-TEST STATUS: $script:pythonStatus; presentation not started."
            exit $script:pythonStatus
        }
        Invoke-Python @($scriptPath, '--r3c1-zip', $R3c1Zip, '--output-dir', $OutputDir)
        $pipelineStatus = $script:pythonStatus
        Write-RunLog "PIPELINE STATUS: $pipelineStatus"
        if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
            if ($pipelineStatus -ne 0) { exit $pipelineStatus }
            throw 'Python returned success but produced no output directory.'
        }
        [IO.Directory]::CreateDirectory((Split-Path -Parent $ResultZip)) | Out-Null
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
