@echo off
setlocal
set REPO_ROOT=%~dp0
set VENV_PY=%REPO_ROOT%.venv\Scripts\python.exe

if not exist "%VENV_PY%" (
    echo VisuSpin has not been installed yet.
    echo Right-click scripts\install.ps1 and choose "Run with PowerShell", then try again.
    pause
    exit /b 1
)

echo Starting VisuSpin...
"%VENV_PY%" -m streamlit run "%REPO_ROOT%visuspin\ui\Home.py"
pause
