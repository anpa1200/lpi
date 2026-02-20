# LPI Exam Simulator — Windows launcher (PowerShell)
# Run from anywhere; script resolves repository root.

$ErrorActionPreference = "Stop"
$RepoRoot = Join-Path (Split-Path -Parent $PSScriptRoot) ""
Set-Location $RepoRoot

if (-not (Test-Path "qst.txt")) {
    Write-Error "qst.txt not found in $RepoRoot"
    exit 1
}

$python = $null
if (Test-Path ".venv\Scripts\python.exe") { $python = ".venv\Scripts\python.exe" }
elseif (Test-Path "venv\Scripts\python.exe") { $python = "venv\Scripts\python.exe" }
else { $python = (Get-Command python -ErrorAction SilentlyContinue).Source }
if (-not $python) { $python = "py" }

& $python LPIExam.py $args
