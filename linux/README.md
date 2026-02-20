# Linux

Run the LPI Exam Simulator on **Linux** (and most Unix-like systems).

## Quick run (GUI)

From the repository root:

```bash
./linux/run.sh
```

Or from anywhere:

```bash
/path/to/lpi/linux/run.sh
```

The script finds the repo root, checks for `qst.txt`, and runs the PyQt6 app. It uses `.venv` or `venv` if present, otherwise system `python3`.

## First-time setup

1. **Clone and enter the repo**
   ```bash
   git clone https://github.com/anpa1200/lpi.git
   cd lpi
   ```

2. **Optional: virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Make launcher executable** (if needed)
   ```bash
   chmod +x linux/run.sh
   ```

4. **Run**
   ```bash
   ./linux/run.sh
   ```

## Bash exam (terminal)

For the pure-Bash exam script (no Python):

```bash
chmod +x examLPI.sh
./examLPI.sh
```

## Requirements

- **Python 3.8+** and **PyQt6** for the GUI (`LPIExam.py`).
- **Bash 4+** for `examLPI.sh`.
