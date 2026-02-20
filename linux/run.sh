#!/usr/bin/env bash
# LPI Exam Simulator — Linux launcher (PyQt6 GUI)
# Run from anywhere; script resolves repository root automatically.

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -f "qst.txt" ]; then
    echo "Error: qst.txt not found in $REPO_ROOT" >&2
    exit 1
fi

# Prefer venv if present
if [ -d ".venv/bin" ]; then
    exec .venv/bin/python3 LPIExam.py "$@"
fi
if [ -d "venv/bin" ]; then
    exec venv/bin/python3 LPIExam.py "$@"
fi

exec python3 LPIExam.py "$@"
