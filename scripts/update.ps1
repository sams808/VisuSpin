# VisuSpin updater: pulls the latest version from GitHub and refreshes the
# virtual environment's dependencies. Safe to run any time.
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $RepoRoot ".venv"

Write-Host "VisuSpin updater" -ForegroundColor Cyan

Push-Location $RepoRoot
try {
    $IsGitRepo = Test-Path (Join-Path $RepoRoot ".git")
    if (-not $IsGitRepo) {
        Write-Host "This folder isn't a git checkout of VisuSpin (no .git folder found)." -ForegroundColor Yellow
        Write-Host "Download the latest version from https://github.com/sams808/VisuSpin instead, or ask your instructor for a git-cloned copy so this updater can work."
        exit 1
    }

    $GitStatus = git status --porcelain 2>&1
    if ($GitStatus) {
        Write-Host "You have local changes in this folder:" -ForegroundColor Yellow
        Write-Host $GitStatus
        $Continue = Read-Host "Continue and pull the latest version anyway? Local changes may cause conflicts. [y/N]"
        if ($Continue -ne "y" -and $Continue -ne "Y") {
            Write-Host "Update cancelled."
            exit 0
        }
    }

    Write-Host "Pulling latest changes..."
    git pull

    if (-not (Test-Path $VenvPath)) {
        Write-Host "No virtual environment found -- running install.ps1 first." -ForegroundColor Yellow
        & (Join-Path $PSScriptRoot "install.ps1")
    } else {
        $VenvPython = Join-Path $VenvPath "Scripts\python.exe"
        Write-Host "Refreshing dependencies..."
        & $VenvPython -m pip install -r (Join-Path $RepoRoot "requirements.txt") --upgrade --quiet
    }

    Write-Host ""
    Write-Host "Update complete." -ForegroundColor Green
} finally {
    Pop-Location
}
