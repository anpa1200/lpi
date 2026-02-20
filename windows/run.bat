@echo off
REM LPI Exam Simulator — Windows launcher (PyQt6 GUI)
REM Run from anywhere; script resolves repository root.

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
cd /d "%REPO_ROOT%"

if not exist "qst.txt" (
    echo Error: qst.txt not found in %REPO_ROOT%
    exit /b 1
)

REM Prefer venv if present
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" LPIExam.py %*
    exit /b
)
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" LPIExam.py %*
    exit /b
)

REM System Python
python LPIExam.py %*
exit /b
