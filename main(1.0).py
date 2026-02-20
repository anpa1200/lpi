#!/usr/bin/env python3
"""
LPI 010-160 Exam — Legacy Kivy UI (alternative to LPIExam.py).

This module provides a Kivy-based graphical interface for practicing
LPI Linux Essentials (010-160) questions. It uses the same question bank
(qst.txt) and parsing logic as LPIExam.py.

LIMITATIONS (legacy):
  - Intended for a small subset of questions per run (e.g. random_e(4)).
  - Fill-in-the-blank questions (17, 40, 56, 63) are skipped in the loop.
  - No timer or full exam/trainer flow; each BoxApp().run() shows one question.
  - Right-answer list (ra_pl) may differ slightly from LPIExam.py for some questions.

USAGE:
  Run from project directory so qst.txt is found:
    python3 "main(1.0).py"
  To change how many questions are shown, edit the last line: random_e(N).

Author: Andrey Pautov <1200km@gmail.com>
License: GPL-3.0 (see LICENSE.md)
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

# Kivy (optional dependency)
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

# -----------------------------------------------------------------------------
# Configuration and paths
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
QUESTION_BANK_NAME = "qst.txt"
FILL_QUESTION_NUMBERS = (17, 40, 56, 63)


def _question_bank_path() -> Path:
    """Resolve qst.txt from script directory or current working directory."""
    for base in (SCRIPT_DIR, Path.cwd()):
        p = base / QUESTION_BANK_NAME
        if p.is_file():
            return p
    return SCRIPT_DIR / QUESTION_BANK_NAME


def load_question_bank() -> list[str]:
    """Load question bank lines (without trailing newline). Raises FileNotFoundError if missing."""
    path = _question_bank_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"Question bank not found: {path}. Run from the project directory."
        )
    with open(path, "r", encoding="UTF-8") as f:
        return [line.rstrip("\n\r") for line in f]


# Load once at import (fails fast if file missing)
text_lines = load_question_bank()


def nums(text: list[str]) -> list[str]:
    """Extract question number lines from the question bank (see DOCUMENTATION.md)."""
    return [
        line for line in text
        if 0 < len(line) <= 2 and line != " "
    ]


def bodies(text: list[str]) -> list[list[str]]:
    """Extract option bodies per question. FILL questions get one synthetic option."""
    bodylist = []
    body = []
    for line in text:
        if len(line) < 1 or line[:2] == "Ex":
            continue
        if line[:4] == "FILL":
            body.append("Print your answer here: ")
            bodylist.append(body)
            body = []
        elif line[:2] == "A.":
            body.append(line[1:])
        elif line[:2] == "B.":
            body.append(line[1:])
        elif line[:2] == "C.":
            body.append(line[1:])
        elif line[:2] == "D.":
            body.append(line[1:])
        elif line[:2] == "E.":
            body.append(line[1:])
            bodylist.append(body)
            body = []
    return bodylist


def headers(text: list[str]) -> list[str]:
    """Extract question stems (headers) per question."""
    headerlist = []
    header = ""
    listex = ("Ex", "A.", "B.", "C.", "D.", "E.")
    for line in text:
        if len(line) < 3 or line[:2] in listex:
            if len(header) >= 1:
                headerlist.append(header)
                header = ""
        else:
            header = header + line
    return headerlist


# Right answers: 1-based option indices per question (see DOCUMENTATION.md).
# Note: may differ from LPIExam.py for some questions (e.g. question 8).
ra_pl: list[list[int]] = [
    [1, 5], [2], [4], [4], [2], [4], [5], [2, 3, 5], [5], [5], [5], [1], [1], [2],
    [1, 2, 5], [2, 4], [], [2], [4], [4, 5], [4], [5], [4], [2],
    [2], [2], [4], [3], [5], [1], [1, 2, 5], [2], [4, 5], [1],
    [2, 5], [1], [5], [1], [2], [0], [2, 4], [5], [5], [4], [5], [4], [5], [4], [3],
    [3, 5], [3, 4], [4], [2, 3], [2, 5], [3], [0], [4], [3], [1, 5], [1],
    [1], [5], [0], [2], [2], [3], [1], [5], [2], [3], [1, 2], [3], [3], [4],
    [1, 5], [5], [2], [4], [2, 4, 5], [3],
]


def question(question_index: int) -> tuple[str, str, list[str], str]:
    """
    Build one question (1-based index 1..80).
    Returns (num_str, header, body_list, right_answer_letters).
    """
    x = question_index - 1
    num_str = "Question:" + nums(text_lines)[x]
    header = headers(text_lines)[x]
    chars = ["A", "B", "C", "D", "E"]
    bodyt = bodies(text_lines)[x].copy()
    ra_answ = [bodyt[i - 1] for i in ra_pl[x]] if ra_pl[x] else []
    random.shuffle(bodyt)
    body = []
    ra_answc = ""
    for counter, opt in enumerate(bodyt):
        if opt in ra_answ:
            ra_answc += chars[counter]
        body.append(chars[counter] + opt)
    return num_str, header, body, ra_answc


def answer_cli(_question_index: int, ra_answc: str) -> bool:
    """CLI answer check (for main_f). Returns True if correct."""
    answ = input("Enter your answer: ").strip().upper()
    if answ == ra_answc:
        print("Right!")
        return True
    print("Wrong!")
    return False


def main_f() -> None:
    """Run 80 questions in CLI (print question, then prompt for answer)."""
    for i in range(80):
        num_str, header, body, ra_answc = question(i + 1)
        print(num_str, "\n", header)
        print(*body, sep="\n")
        answer_cli(i + 1, ra_answc)


# Global used by BoxApp.build to know which question to show
_current_question_index: int = 1


class BoxApp(App):
    """
    Kivy app showing a single multiple-choice question.
    User builds answer by pressing option buttons (multiple allowed), then Submit.
    """

    def callback(self, instance: Button) -> None:
        """Append the first character of the pressed button to current answer."""
        self.answer += (instance.text)[0]

    def submit(self, instance: Button) -> None:
        """Check answer against global ra_answc (set when question() was called)."""
        # ra_answc is set in create() below and captured in closure
        if self.answer == self._ra_answc:
            print("Right!")
        else:
            print("Wrong!")

    def build(self) -> BoxLayout:
        bl = BoxLayout(orientation="vertical")
        self.answer = ""
        a = _current_question_index
        num_str, header, body, ra_answc = question(a)
        self._ra_answc = ra_answc

        bl.add_widget(Label(text=num_str))
        bl.add_widget(Label(text=header))
        bl.add_widget(Label(text="(Correct: " + ra_answc + ")"))

        for opt in body:
            btn = Button(text=opt)
            btn.bind(on_press=self.callback)
            bl.add_widget(btn)
        submit_btn = Button(text="Submit")
        submit_btn.bind(on_press=self.submit)
        bl.add_widget(submit_btn)

        return bl


def random_e(count: int) -> None:
    """
    Run Kivy app for `count` random questions (fill-in questions skipped).
    Each question runs in a new BoxApp instance.
    """
    global _current_question_index
    r = list(range(1, 81))
    random.shuffle(r)
    filllist = set(FILL_QUESTION_NUMBERS)
    shown = 0
    for i in r:
        if i in filllist:
            continue
        _current_question_index = i
        BoxApp().run()
        shown += 1
        if shown >= count:
            break


if __name__ == "__main__":
    try:
        random_e(4)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
