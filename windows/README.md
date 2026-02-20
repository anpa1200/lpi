# Windows

Run the LPI Exam Simulator on **Windows**.

## Quick run (GUI)

From the repository root (Command Prompt or PowerShell):

**Command Prompt:**
```cmd
windows\run.bat
```

**PowerShell:**
```powershell
.\windows\run.ps1
```

The launcher finds the repo root, checks for `qst.txt`, and runs the PyQt6 app. It uses `.venv` or `venv` if present, otherwise `python` or `py`.

## First-time setup

1. **Clone and enter the repo**
   ```cmd
   git clone https://github.com/anpa1200/lpi.git
   cd lpi
   ```

2. **Optional: virtual environment**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run**
   ```cmd
   windows\run.bat
   ```
   or in PowerShell:
   ```powershell
   .\windows\run.ps1
   ```

## Standalone .exe (optional)

If you build a standalone Windows executable (e.g. with PyInstaller), place it in this folder or in a subfolder (e.g. `windows\build\`) and run it from the **repository root** so it can find `qst.txt`, or configure the build to embed/bundle the question bank.

Example layout:
```
lpi/
  windows/
    run.bat
    run.ps1
    README.md
    build/          (optional: place your .exe here)
      LPIExam.exe
  qst.txt
  ...
```

Run the .exe from the repo root so `qst.txt` is in the current directory, or set the working directory to the repo root in your shortcut/build.

## Requirements

- **Python 3.8+** and **PyQt6** for the GUI (`LPIExam.py`).
- On Windows, `python` or `py` must be on PATH.
