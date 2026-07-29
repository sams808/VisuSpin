@echo off
setlocal
set REPO_ROOT=%~dp0
set EXPLORER_HTML=%REPO_ROOT%visuspin\classic\live_vector_explorer.html

if not exist "%EXPLORER_HTML%" (
    echo Could not find live_vector_explorer.html at:
    echo %EXPLORER_HTML%
    pause
    exit /b 1
)

echo Opening VisuSpin Live Vector Explorer in your browser...
start "" "%EXPLORER_HTML%"
