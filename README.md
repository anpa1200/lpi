# LPI Exam Simulator & Trainer

**Professional study and exam simulation toolkit for the Linux Professional Institute (LPI) 010-160 exam.**

This repository provides multiple ways to practice for the LPI Linux Essentials (010-160) certification: a **Bash-based** interactive exam script, a **PyQt6** graphical exam/trainer application, and an optional **Kivy** mobile-friendly UI. All tools share the same question bank and support multiple-choice and fill-in-the-blank questions.

---

## Table of Contents

- [Features](#features)
- [Repository Contents](#repository-contents)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Question Bank Format](#question-bank-format)
- [Modes of Operation](#modes-of-operation)
- [Contributing & License](#contributing--license)
- [Documentation](#documentation)

---

## Features

- **80 exam-style questions** aligned with LPI 010-160 (Linux Essentials).
- **Two practice modes**
  - **Trainer**: All 80 questions in random order (no time pressure).
  - **Exam**: 40 random questions with a running timer (exam-like conditions).
- **Multiple interfaces**
  - **Bash** (`examLPI.sh`): Terminal-based, runs anywhere Bash is available.
  - **PyQt6** (`LPIExam.py`): Desktop GUI with checkboxes, timer, and score summary.
  - **Kivy** (`main(1.0).py`): Alternative GUI (legacy); useful for touch/tiled layouts.
- **Question types**
  - Multiple choice (single or multiple correct answers).
  - Fill-in-the-blank (keyword) for a subset of questions.
- **Scoring**
  - Right/wrong feedback per question.
  - Final score and list of question numbers answered incorrectly.
- **Single question bank**
  - One shared format (`qst.txt`) for all tools; see [Question Bank Format](#question-bank-format) and [DOCUMENTATION.md](DOCUMENTATION.md).

---

## Repository Contents

| File / path        | Description |
|--------------------|-------------|
| `examLPI.sh`       | **Bash LPI exam simulator.** All questions implemented as shell functions; run in terminal. Do not modify unless you maintain your own fork. |
| `LPIExam.py`       | **Main GUI application.** PyQt6-based exam/trainer with timer, multiple-choice and fill-in handling, and end-of-session summary. |
| `main(1.0).py`     | **Legacy Kivy GUI.** Alternative UI (Kivy); see docstring and DOCUMENTATION.md for usage and limitations. |
| `qst.txt`          | **Question bank.** Plain-text, structured format: question number, stem, options A–E, fill-in markers, and explanation placeholders. |
| `README.md`        | This file: project overview, usage, and quick reference. |
| `DOCUMENTATION.md` | Detailed specification: `qst.txt` format, application architecture, and implementation notes. |
| `requirements.txt` | Python dependencies for `LPIExam.py` and optional Kivy app. |
| `LICENSE.md`       | GNU General Public License v3. |
| `.gitignore`       | Ignores build artifacts, venv, `*.exe`, IDE files, and secrets. |

---

## Requirements

- **Bash** (for `examLPI.sh`): Any system with Bash 4+ (associative arrays).
- **Python 3.8+** (for `LPIExam.py` and Kivy app).
- **PyQt6** (for `LPIExam.py`): Install via pip (see [Installation](#installation)).
- **Kivy** (optional, for `main(1.0).py`): Only if you use the legacy Kivy interface.

---

## Installation

1. **Clone or download** the repository:
   ```bash
   git clone <repository-url>
   cd lpi
   ```

2. **Python environment** (for GUI apps):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   # or:  .venv\Scripts\activate  on Windows
   pip install -r requirements.txt
   ```

3. **Run from the project directory** so that `qst.txt` is found:
   - Bash: `./examLPI.sh` (ensure executable: `chmod +x examLPI.sh`).
   - PyQt6: `python3 LPIExam.py`.
   - Kivy: `python3 "main(1.0).py"` (optional).

---

## Usage

### Bash (examLPI.sh)

```bash
cd /path/to/lpi
./examLPI.sh
```

- Follow on-screen prompts; answer by entering option letters (e.g. `A`, `BE`).
- No separate “trainer” vs “exam” mode; script defines one question flow.

### PyQt6 (LPIExam.py)

```bash
python3 LPIExam.py
```

1. **Start**: Choose **Trainer** (80 questions) or **Exam** (40 questions).
2. **Per question**: Select one or more options (checkboxes) or type the keyword for fill-in questions, then click **Submit**.
3. **Next**: After feedback, click **Next** (or **Next question**) to continue.
4. **End**: Summary window shows total answered, correct count, score, and list of wrong question numbers.

- **Exit**: Use **Exit** / **Stop and Exit** to quit at any time.

### Kivy (main(1.0).py) — legacy

```bash
python3 "main(1.0).py"
```

- See module docstring and [DOCUMENTATION.md](DOCUMENTATION.md) for behavior and current limitations.

---

## Question Bank Format

The file **`qst.txt`** uses a line-oriented, structured format so that the same bank can drive the Bash script, PyQt6, and Kivy apps.

- **Question number**: One or two digits on its own line (e.g. `1`, `2`, `17`).
- **Stem**: Lines of text until a line starting with `A.`, `B.`, … or `FILL`.
- **Options**: Lines starting with `A.`, `B.`, `C.`, `D.`, `E.` (content after the prefix).
- **Fill-in**: A line starting with `FILL` (and optional “BLANK”) marks a fill-in-the-blank question; the next logical block is the prompt; no A.–E. options.
- **Explanation**: Lines starting with `Explanation/Reference:` (and following text) are for reference only; parsers may skip them.

For full syntax, edge cases, and examples, see **[DOCUMENTATION.md](DOCUMENTATION.md)**.

---

## Modes of Operation

| Mode    | Questions | Use case |
|---------|-----------|----------|
| Trainer | 80        | Study all questions in random order. |
| Exam    | 40        | Timed practice exam with 40 random questions. |

Scoring in the PyQt6 app is linear: each question contributes equally to the total (e.g. 20 points per question for a 0–100 scale).

---

## Contributing & License

- **Author**: Andrey Pautov (1200km@gmail.com).
- **License**: GNU General Public License v3. See [LICENSE.md](LICENSE.md).
- **examLPI.sh**: Do not modify in this repo if you rely on the reference version; maintain changes in a fork or separate branch.

---

## Documentation

- **[README.md](README.md)** (this file): Overview, installation, usage.
- **[DOCUMENTATION.md](DOCUMENTATION.md)**: Detailed `qst.txt` format, application design, and implementation notes.

For parsing and extending the question bank, always refer to DOCUMENTATION.md and the actual parsers in `LPIExam.py` (and optionally `main(1.0).py`).

---

## Production / Deployment

- **No secrets**: The repo contains no API keys or credentials. `qst.txt` is data only.
- **Reproducible install**: Use `pip install -r requirements.txt` in a clean venv for a consistent environment.
- **Artifacts**: Build outputs (e.g. `*.exe`, `dist/`) are listed in `.gitignore` and should not be committed.
- **Run from repo root**: Start the app from the project directory so `qst.txt` is found (or place `qst.txt` next to the script).
- **examLPI.sh**: Make executable with `chmod +x examLPI.sh` after clone; no build step required.
