$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not available in PATH."
}

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".git")) {
    git init
}

git add .

$hasHead = $true
try {
    git rev-parse --verify HEAD *> $null
} catch {
    $hasHead = $false
}

if (-not $hasHead) {
    git commit -m "MILAL R3c.0.1 baseline and Codex handoff"
} else {
    Write-Host "Git repository already has commits. Current status:"
    git status --short
}

Write-Host ""
Write-Host "Repository ready. Open this folder in Codex."
