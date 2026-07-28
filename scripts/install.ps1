# VisuSpin installer: creates a private virtual environment next to this
# repository and installs the few required packages into it, so it never
# touches (or depends on) whatever Python the student already has set up.
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $RepoRoot ".venv"

Write-Host "VisuSpin installer" -ForegroundColor Cyan
Write-Host "Repository root: $RepoRoot"

$PythonCmd = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $version = & $candidate --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PythonCmd = $candidate
            Write-Host "Found $version via '$candidate'" -ForegroundColor Green
            break
        }
    } catch {}
}
if (-not $PythonCmd) {
    Write-Host "Python was not found on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.10+ from https://www.python.org/downloads/ (check 'Add python.exe to PATH' during setup), then re-run this script."
    exit 1
}

if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment at $VenvPath ..."
    & $PythonCmd -m venv $VenvPath
} else {
    Write-Host "Virtual environment already exists at $VenvPath -- reusing it."
}

$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
Write-Host "Installing dependencies (streamlit, numpy, matplotlib) ..."
& $VenvPython -m pip install --upgrade pip --quiet
& $VenvPython -m pip install -r (Join-Path $RepoRoot "requirements.txt") --quiet

# Streamlit's very first run ever on a machine shows an interactive "Welcome
# / enter your email" onboarding prompt and BLOCKS waiting for input -- fatal
# for a double-clicked .bat with no visible console to type into. Pre-writing
# an empty credentials.toml (the officially documented way to skip it) avoids
# students ever hitting this on first launch.
$StreamlitConfigDir = Join-Path $env:USERPROFILE ".streamlit"
$CredentialsPath = Join-Path $StreamlitConfigDir "credentials.toml"
if (-not (Test-Path $CredentialsPath)) {
    New-Item -ItemType Directory -Force -Path $StreamlitConfigDir | Out-Null
    # -Encoding ascii (not utf8): Windows PowerShell 5.1's utf8 encoding writes
    # a BOM, which breaks Python's toml parser -- Streamlit then silently
    # deletes the "unreadable" file and falls back to the interactive prompt
    # anyway (verified directly against streamlit/runtime/credentials.py).
    Set-Content -Path $CredentialsPath -Value "[general]`nemail = """"" -Encoding ascii
    Write-Host "Pre-configured Streamlit to skip its first-run email prompt."
}

$RunBat = Join-Path $RepoRoot "run_visuspin.bat"
if (-not (Test-Path $RunBat)) {
    Write-Host "Note: run_visuspin.bat not found at $RunBat -- it should already be checked into the repository." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Install complete." -ForegroundColor Green
Write-Host "Double-click run_visuspin.bat (in the main VisuSpin folder) to launch the app."

$CreateShortcut = Read-Host "Create a desktop shortcut for VisuSpin? [y/N]"
if ($CreateShortcut -eq "y" -or $CreateShortcut -eq "Y") {
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Desktop")) "VisuSpin.lnk"))
        $Shortcut.TargetPath = $RunBat
        $Shortcut.WorkingDirectory = $RepoRoot
        $Shortcut.Save()
        Write-Host "Desktop shortcut created." -ForegroundColor Green
    } catch {
        Write-Host "Could not create a desktop shortcut automatically; you can still run run_visuspin.bat directly." -ForegroundColor Yellow
    }
}
