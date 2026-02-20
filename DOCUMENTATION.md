# LPI Exam Simulator — Detailed Documentation

This document describes the **question bank format** (`qst.txt`), the **architecture** of the Python applications, and **implementation notes** for maintainers and contributors. It does not describe `examLPI.sh`, which is kept unchanged in this repository.

---

## Table of Contents

1. [Question Bank: qst.txt Format](#1-question-bank-qsttxt-format)
2. [Parsing Rules (LPIExam.py)](#2-parsing-rules-lpiexampy)
3. [Application Architecture](#3-application-architecture)
4. [Right-Answer Metadata](#4-right-answer-metadata)
5. [Fill-in-the-Blank Questions](#5-fill-in-the-blank-questions)
6. [Implementation Notes and Conventions](#6-implementation-notes-and-conventions)

---

## 1. Question Bank: qst.txt Format

### 1.1 Overview

`qst.txt` is a **UTF-8 encoded**, line-oriented text file. Each question is a contiguous block of lines. The structure is:

1. **Question number** (optional blank line before it).
2. **Question stem** (one or more lines of text).
3. **Answer options** (lines starting with `A.`, `B.`, `C.`, `D.`, `E.`) **or** a **fill-in marker** (`FILL`).
4. **Explanation/Reference** (optional): line starting with `Explanation/Reference:` and optional body.

No strict blank-line separation is required between questions; parsers use line prefixes to detect boundaries.

### 1.2 Line Types and Syntax

| Line pattern | Meaning | Parser behavior (typical) |
|--------------|---------|----------------------------|
| Empty line or single space | Ignored for structure | Skipped or used to break stem accumulation. |
| One or two digits only (e.g. `1`, `17`) | Question number | Start of new question; previous question block ends. |
| `A.` … `E.` at start of line | Multiple-choice option | Text after the prefix (e.g. `A.`) is the option text. Option `E.` often ends the option list. |
| Line starting with `FILL` | Fill-in-the-blank marker | Next block is a fill-in question; no A.–E. options. Body may include a single line like “Print your answer here: ”. |
| `Explanation/Reference:` | Explanation block | Reference only; not shown as answer options. |
| Any other non-empty line | Part of stem or explanation | Appended to current stem or explanation. |

### 1.3 Example: Multiple-Choice Question

```text
1
What are the differences between hard disk drives and solid state disks? (Choose two.)
A. Hard disks have a motor and moving parts, solid state disks do not.
B. Hard disks can fail due to physical damage, while solid state disks cannot fail.
C. Solid state disks can store many times as much data as hard disk drives.
D. /dev/sda is a hard disk device while /dev/ssda is a solid state disk.
E. Solid state disks provide faster access to stored data than hard disks.
Explanation/Reference:
```

- Line `1` = question number.  
- Next line = stem.  
- Lines starting with `A.`–`E.` = options.  
- `Explanation/Reference:` = start of reference block (may be empty).

### 1.4 Example: Fill-in-the-Blank Question

```text
17
FILL BLANK:
  What keyword is used in a shell script to begin a loop? (Specify one keyword only, without any additional information.)
Explanation/Reference:
```

- Number `17` = question number.  
- `FILL BLANK:` = marker; parser may treat the following line(s) as the prompt and may inject a single synthetic option like “Print your answer here: ” for UI consistency.  
- Correct answer (e.g. `for`) is **not** stored in `qst.txt`; it is hardcoded in the application (see [Section 5](#5-fill-in-the-blank-questions)).

### 1.5 Multi-line Stems and HTML-like Content

- Stems can span multiple lines until an `A.`/`B.`/…/`FILL`/`Explanation` line is seen.  
- Stems may contain HTML-like tags (e.g. `<i>`, `<b>`, `<br>`) for display; the GUI may render them or strip them depending on the widget.  
- Spaces and line breaks are preserved when concatenating stem lines.

### 1.6 Character Encoding and Line Endings

- **Encoding**: UTF-8.  
- **Line endings**: Any of CRLF, LF, or CR; parsers typically strip the last character when reading “line by line”, so `line[:-1]` is common. Empty lines are valid.

---

## 2. Parsing Rules (LPIExam.py)

The module `LPIExam.py` defines three main parsers that operate on the list of lines (each line without trailing newline):

- **`nums(text)`**  
  - Collects **question numbers**: lines where length is in (0, 2] and line is not a single space.  
  - Returns a list of strings (e.g. `['1','2',…]`). Order matches line order in file.

- **`headers(text)`**  
  - Builds **stems** by concatenating lines that are “body” of the question until a structural line is hit.  
  - Structural lines: length &lt; 3, or line starting with `Ex`, `A.`, `B.`, `C.`, `D.`, `E.`.  
  - When a structural line is seen and the current stem is non-empty, the stem is appended to the list and reset.  
  - Returns a list of strings (one stem per question).

- **`bodies(text)`**  
  - Builds **option lists** per question.  
  - Skips empty lines and lines starting with `Ex`.  
  - On `FILL`: appends one synthetic option `"Print your answer here: "` and closes the current question’s body.  
  - On `A.`–`E.`: takes the substring after the two-character prefix (e.g. `line[1:]`) and appends to current body; on `E.` also closes the question body.  
  - Returns a list of lists of strings (each inner list = one question’s options).

**Index alignment**: The lists returned by `nums`, `headers`, and `bodies` are aligned by index: index `i` corresponds to question number `nums(…)[i]`, stem `headers(…)[i]`, and options `bodies(…)[i]`.

---

## 3. Application Architecture

### 3.1 LPIExam.py (PyQt6)

- **Entry**: `QApplication` and `OpenWindow` (mode selection: Trainer 80 / Exam 40).  
- **Global state**:  
  - `var`: number of questions to run (40 or 80).  
  - `rangelist`: shuffled list of question indices (1–80); then sliced to `var` length.  
  - `all_counter`, `RA_COUNTER`, `wrong_answ`, `time_elapsed`: session stats.  
- **Main loop** (after mode selection):  
  - For each `i` in `rangelist`, call `question(i)` to get `num`, `header`, `body`, `right_a`.  
  - If `i` is in `filllist` (e.g. 17, 40, 56, 63): show `QuestionFill` window (fill-in-the-blank).  
  - Else: show `MainWindow` (multiple-choice with checkboxes).  
  - Each window runs a nested `app.exec()` until the user proceeds or exits.  
- **End**: `EndWindow` shows total answered, correct count, grade, and list of wrong question numbers.

### 3.2 main(1.0).py (Kivy, legacy)

- Uses the same `qst.txt` and similar parsing (`nums`, `headers`, `bodies`).  
- Right-answer list `ra_pl` may differ slightly from `LPIExam.py` (e.g. question 8); see [Section 4](#4-right-answer-metadata).  
- Builds a single-screen Kivy UI with buttons for options and a Submit button.  
- Intended for a small subset of questions (e.g. `random_e(4)`); not a full exam flow.  
- File handle for `qst.txt` should be closed (e.g. context manager); see code comments.

---

## 4. Right-Answer Metadata

Correct answers are **not** stored in `qst.txt`. They are defined in code:

- **LPIExam.py**: list **`ra_pl`** — for each question index (0–79), a list of **1-based option indices** (1–5) that are correct. Example: `[1, 5]` means options 1 and 5 (A and E) are correct. For fill-in questions, the corresponding entry may be empty `[]`; the actual keyword is in `QuestionFill.submit_fill`.  
- **main(1.0).py**: similar list, also named **`ra_pl`**; may differ for some questions (e.g. 8).

Fill-in questions use **hardcoded** answers in the PyQt6 `submit_fill` method (e.g. `for`, `\`, `R`, `man` for questions 17, 40, 56, 63).

---

## 5. Fill-in-the-Blank Questions

- **Question numbers** (in default setup): 17, 40, 56, 63.  
- **Stored in qst.txt**: Only the stem (and optional “Print your answer here: ”); no correct answer string.  
- **Correct answers** in `LPIExam.py` `QuestionFill.submit_fill`:  
  - 17: `for`  
  - 40: `\` (backslash)  
  - 56: `R`  
  - 63: `man`  
- Comparison is case-sensitive unless the code explicitly normalizes (e.g. strip, lower).

---

## 6. Implementation Notes and Conventions

- **Paths**: `qst.txt` is opened with a relative path from the current working directory. Running the script from the project root is required unless the code is changed to resolve paths relative to the script file.  
- **Scoring**: Linear; each question has equal weight. “Grade” is often computed as (correct_count * 20) for display purposes (e.g. out of 80 or 40 * 20).  
- **Timer**: PyQt6 uses a 1-second `QTimer`; `time_elapsed` is a global second counter.  
- **Wrong-answer list**: Stores **question numbers** (1–80) for which the user answered incorrectly, for review.  
- **examLPI.sh**: Not modified in this repo; it implements the same exam domain (LPI 010-160) with its own question set and logic.

For any change to the question bank format, update this document and ensure `nums`, `headers`, and `bodies` in both Python apps remain consistent with the specification above.
