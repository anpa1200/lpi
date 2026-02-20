# pylint: disable=E0611
"""
LPI 010-160 Exam Simulator — PyQt6 GUI.

Desktop application for practicing LPI Linux Essentials (010-160) exam questions.
Supports Trainer mode (all 80 questions) and Exam mode (40 random questions)
with multiple-choice and fill-in-the-blank question types.

Author: Andrey Pautov <1200km@gmail.com>
License: GPL-3.0 (see LICENSE.md)
"""
from __future__ import annotations

import logging
import os
import random
import sys
from pathlib import Path
from typing import List, Tuple

from PyQt6.QtCore import Qt, QTime, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# -----------------------------------------------------------------------------
# Constants and configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
QUESTION_BANK_NAME = "qst.txt"
POINTS_PER_QUESTION = 20
TRAINER_QUESTION_COUNT = 80
EXAM_QUESTION_COUNT = 40
FILL_IN_QUESTION_NUMBERS = (17, 40, 56, 63)
FILL_IN_ANSWERS = {
    17: "for",
    40: "\\",
    56: "R",
    63: "man",
}

# Right-answer list: for each question index 0..79, 1-based option indices (1=A .. 5=E).
# Empty list [] for fill-in questions (answers are in FILL_IN_ANSWERS).
RA_PL: List[List[int]] = [
    [1, 5], [2], [4], [4], [2], [4], [5], [3, 5], [5], [5], [5], [1], [1], [2],
    [1, 2, 5], [2, 4], [], [2], [4], [4, 5], [4], [5], [4], [2],
    [2], [2], [4], [3], [5], [1], [1, 2, 5], [2], [4, 5], [1],
    [2, 5], [1], [5], [1], [2], [0], [2, 4], [5], [5], [4], [5], [4], [1, 5], [4], [3],
    [3, 5], [3, 4], [4], [2, 3], [2, 5], [3], [0], [4], [3], [1, 5], [1],
    [1], [5], [0], [2], [2], [3], [1], [5], [2], [3], [1, 2], [3], [3], [4],
    [1, 5], [5], [2], [4], [2, 4, 5], [3],
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Global session state (used by GUI and main loop)
# -----------------------------------------------------------------------------
time_elapsed: int = 0
wrong_answ: List[int] = []
RA_COUNTER: int = 0
all_counter: int = 0
var: int = 0  # set by OpenWindow: TRAINER_QUESTION_COUNT or EXAM_QUESTION_COUNT

# Question bank lines (loaded at startup)
text_lines: List[str] = []


def _question_bank_path() -> Path:
    """Return path to qst.txt, preferring script directory."""
    p = SCRIPT_DIR / QUESTION_BANK_NAME
    if p.is_file():
        return p
    # Fallback: current working directory
    cwd = Path.cwd() / QUESTION_BANK_NAME
    if cwd.is_file():
        return cwd
    return SCRIPT_DIR / QUESTION_BANK_NAME  # raise with this path if not found


def load_question_bank() -> List[str]:
    """
    Load question bank file (qst.txt) from script directory or cwd.
    Returns list of lines without trailing newline.
    Raises FileNotFoundError if file is missing.
    """
    path = _question_bank_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"Question bank not found: {path}. Run the application from the project directory "
            f"or place {QUESTION_BANK_NAME} next to LPIExam.py."
        )
    with open(path, "r", encoding="UTF-8") as f:
        lines = [line.rstrip("\n\r") for line in f]
    logger.info("Loaded question bank: %s (%d lines)", path, len(lines))
    return lines


def nums(text: List[str]) -> List[str]:
    """
    Extract question number lines from the question bank text.
    A line is treated as a question number if its length is 1–2 and it is not a single space.
    """
    result = []
    for line in text:
        if 0 < len(line) <= 2 and line != " ":
            result.append(line)
    return result


def bodies(text: List[str]) -> List[List[str]]:
    """
    Extract option bodies per question. Each question yields a list of option strings.
    FILL questions get a single synthetic option 'Print your answer here: '.
    """
    bodylist: List[List[str]] = []
    body: List[str] = []
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


def headers(text: List[str]) -> List[str]:
    """
    Extract question stems (headers). Concatenates lines until a structural
    line (short line or A./B./C./D./E./Ex) is encountered.
    """
    headerlist: List[str] = []
    header = ""
    listex = ["Ex", "A.", "B.", "C.", "D.", "E."]
    for line in text:
        if len(line) < 3 or line[:2] in listex:
            if len(header) >= 1:
                headerlist.append(header)
                header = ""
        else:
            header = header + line
    return headerlist


def question(loop_number: int) -> Tuple[str, str, List[str], str]:
    """
    Build one question (number, stem, shuffled options, correct answer letters).
    loop_number is 1-based (1..80). Returns (num_str, header, body_list, right_letters).
    """
    idx = loop_number - 1
    num_str = "Question:" + nums(text_lines)[idx]
    header = headers(text_lines)[idx]
    chars = ["A", "B", "C", "D", "E"]
    bodyt = bodies(text_lines)[idx].copy()
    ra_indices = RA_PL[idx]
    ra_answ = [bodyt[i - 1] for i in ra_indices] if ra_indices else []
    random.shuffle(bodyt)
    body: List[str] = []
    right_answerc = ""
    for counter, opt in enumerate(bodyt):
        if opt in ra_answ:
            right_answerc += chars[counter]
        body.append(chars[counter] + opt)
    return num_str, header, body, right_answerc


# -----------------------------------------------------------------------------
# GUI: Fill-in-the-blank question window
# -----------------------------------------------------------------------------
class QuestionFill(QMainWindow):
    """Window for a single fill-in-the-blank question."""

    def __init__(self, current_question_number: int) -> None:
        super().__init__()
        self.current_question_number = current_question_number
        self.setFixedSize(640, 350)
        self.setWindowTitle(f"{num}          {all_counter}/{var}")
        self.label1 = QLabel(header)
        self.label1.setWordWrap(True)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.time_label = QLabel(self)
        self.time_label.setText("Time elapsed: __:__:__")
        self.timer.timeout.connect(self.update_time)
        self.label = QLabel("")
        self.button6 = QPushButton("Submit")
        self.button6.resize(100, 40)
        self.button7 = QPushButton("Next question")
        self.button7.resize(100, 40)
        self.button8 = QPushButton("Stop and Exit")
        self.button8.resize(100, 40)
        self.input = QLineEdit()
        self.input.textChanged.connect(self.label.setText)
        layout = QGridLayout()
        layout.addWidget(self.label1, 0, 0, 1, 8)
        layout.addWidget(self.label, 6, 0, 1, 6)
        layout.addWidget(self.input, 4, 0, 3, 8)
        layout.addWidget(self.button6, 9, 6)
        layout.addWidget(self.button7, 9, 7)
        layout.addWidget(self.button8, 9, 8)
        layout.addWidget(self.time_label, 11, 0, 1, 8)
        self.button8.setCheckable(True)
        self.button6.clicked.connect(self.submit_fill)
        self.button7.clicked.connect(self.next)
        self.button8.clicked.connect(self.closeit)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.timer.start()

    def update_time(self) -> None:
        global time_elapsed
        time_elapsed += 1
        t = QTime(0, 0, 0).addSecs(time_elapsed)
        self.time_label.setText("Time elapsed: " + t.toString("hh:mm:ss"))

    def closeit(self) -> None:
        sys.exit(0)

    def next(self) -> None:
        if self.label.text() in (
            '<b><p style="color:red;">Wrong!</p></b>',
            '<b><p style="color:green;">Right!</p></b>',
        ):
            self.timer.stop()
            window2.close()
        else:
            self.label.setText('Press "Submit" button first')

    def submit_fill(self) -> None:
        global RA_COUNTER, wrong_answ
        user_text = self.input.text().strip()
        expected = FILL_IN_ANSWERS.get(self.current_question_number)
        if expected is None:
            self.label.setText('<b><p style="color:red;">Unknown question.</p></b>')
            return
        if user_text == expected:
            self.label.setText('<b><p style="color:green;">Right!</p></b>')
            RA_COUNTER += 1
        else:
            self.label.setText('<b><p style="color:red;">Wrong!</p></b>')
            wrong_answ.append(self.current_question_number)


# -----------------------------------------------------------------------------
# GUI: End / summary window
# -----------------------------------------------------------------------------
class EndWindow(QMainWindow):
    """Summary window showing score and wrong-question list."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(650, 350)
        grade = RA_COUNTER * POINTS_PER_QUESTION
        max_grade = all_counter * POINTS_PER_QUESTION
        self.setWindowTitle("End page of exam")
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.time_label = QLabel(self)
        self.time_label.setText("Time elapsed: __:__:__")
        self.timer.timeout.connect(self.update_time)
        self.label = QLabel("Congratulations!")
        self.label1 = QLabel("Total questions answered: " + str(all_counter))
        self.label2 = QLabel("Right answers: " + str(RA_COUNTER))
        self.label3 = QLabel(f"Your grade: {grade}/{max_grade}")
        self.label4 = QLabel("Wrong answers in these questions: " + str(wrong_answ))
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        layout.addWidget(self.label3)
        layout.addWidget(self.label4)
        layout.addWidget(self.time_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.timer.start()

    def update_time(self) -> None:
        t = QTime(0, 0, 0).addSecs(time_elapsed)
        self.time_label.setText("Time elapsed: " + t.toString("hh:mm:ss"))


# -----------------------------------------------------------------------------
# GUI: Multiple-choice question window
# -----------------------------------------------------------------------------
class MainWindow(QMainWindow):
    """Window for a single multiple-choice question (checkboxes)."""

    def __init__(self, current_question_number: int) -> None:
        super().__init__()
        self.current_question_number = current_question_number
        self.user_answ: List[str] = []
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.setFixedSize(640, 350)
        self.setWindowTitle(f"{num}          {all_counter}/{var}")
        self.label = QLabel(header)
        self.label.setFont(QFont("Arial", 12))
        self.time_label = QLabel(self)
        self.time_label.setText("Time elapsed: __:__:__")
        self.timer.timeout.connect(self.update_time)
        self.label.setWordWrap(True)
        self.label2 = QLabel("")
        self.body1 = QLabel(body[0][2:])
        self.body1.setWordWrap(True)
        self.body2 = QLabel(body[1][2:])
        self.body2.setWordWrap(True)
        self.body3 = QLabel(body[2][2:])
        self.body3.setWordWrap(True)
        self.body4 = QLabel(body[3][2:])
        self.body4.setWordWrap(True)
        self.body5 = QLabel(body[4][2:])
        self.body5.setWordWrap(True)
        self.button1 = QCheckBox(body[0][:2])
        self.button1.resize(20, 20)
        self.button2 = QCheckBox(body[1][:2])
        self.button2.resize(20, 20)
        self.button3 = QCheckBox(body[2][:2])
        self.button3.resize(20, 20)
        self.button4 = QCheckBox(body[3][:2])
        self.button4.resize(20, 20)
        self.button5 = QCheckBox(body[4][:2])
        self.button5.resize(20, 20)
        self.button6 = QPushButton("Submit")
        self.button6.resize(100, 40)
        self.button7 = QPushButton("Next")
        self.button7.resize(100, 40)
        self.button8 = QPushButton("Exit")
        self.button8.resize(100, 40)
        layout = QGridLayout()
        layout.addWidget(
            self.label, 0, 0, 3, 8,
            alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignTop,
        )
        layout.addWidget(self.label2, 11, 5, 1, 6)
        layout.addWidget(self.button1, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.button2, 3, 0, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.button3, 4, 0, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.button4, 5, 0, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.button5, 6, 0, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.body1, 2, 1, 1, 8)
        layout.addWidget(self.body2, 3, 1, 1, 8)
        layout.addWidget(self.body3, 4, 1, 1, 8)
        layout.addWidget(self.body4, 5, 1, 1, 8)
        layout.addWidget(self.body5, 6, 1, 1, 8)
        layout.addWidget(self.button6, 9, 6)
        layout.addWidget(self.button7, 9, 7)
        layout.addWidget(self.button8, 9, 8)
        layout.addWidget(self.time_label, 11, 0, 1, 8)
        for b in (self.button1, self.button2, self.button3, self.button4, self.button5,
                  self.button6, self.button7, self.button8):
            b.setCheckable(True)
        self.button1.clicked.connect(self.user_answer1)
        self.button2.clicked.connect(self.user_answer2)
        self.button3.clicked.connect(self.user_answer3)
        self.button4.clicked.connect(self.user_answer4)
        self.button5.clicked.connect(self.user_answer5)
        self.button6.clicked.connect(self.submit)
        self.button7.clicked.connect(self.next)
        self.button8.clicked.connect(self.closeit)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.timer.start()

    def update_time(self) -> None:
        global time_elapsed
        time_elapsed += 1
        t = QTime(0, 0, 0).addSecs(time_elapsed)
        self.time_label.setText("Time elapsed: " + t.toString("hh:mm:ss"))

    def _toggle_answer(self, option_index: int, checked: bool) -> None:
        letter = body[option_index][0]
        if checked:
            self.user_answ.append(letter)
        elif letter in self.user_answ:
            self.user_answ.remove(letter)

    def user_answer1(self, checked: bool) -> None:
        self._toggle_answer(0, checked)

    def user_answer2(self, checked: bool) -> None:
        self._toggle_answer(1, checked)

    def user_answer3(self, checked: bool) -> None:
        self._toggle_answer(2, checked)

    def user_answer4(self, checked: bool) -> None:
        self._toggle_answer(3, checked)

    def user_answer5(self, checked: bool) -> None:
        self._toggle_answer(4, checked)

    def next(self) -> None:
        if self.label2.text() in (
            '<b><p style="color:red;">Wrong!</p></b>',
            '<b><p style="color:green;">Right!</p></b>',
        ):
            self.timer.stop()
            window.close()
        else:
            self.label2.setText('<b><p style="color:red;">Press "Submit" button first</p></b>')

    def closeit(self) -> None:
        sys.exit(0)

    def submit(self) -> None:
        global RA_COUNTER, wrong_answ
        self.user_answ.sort()
        answ = "".join(self.user_answ)
        if len(answ) == len(right_a):
            if answ == right_a:
                self.label2.setText('<b><p style="color:green;">Right!</p></b>')
                self.label2.setFont(QFont("Arial", 15))
                RA_COUNTER += 1
            else:
                self.label2.setText('<b><p style="color:red;">Wrong!</p></b>')
                self.label2.setFont(QFont("Arial", 15))
                wrong_answ.append(self.current_question_number)
        elif len(answ) < len(right_a):
            self.label2.setText('<b><p style="color:red;">Choose more answers</p></b>')
            self.label2.setFont(QFont("Arial", 15))
        else:
            self.label2.setText('<b><p style="color:red;">Choose fewer answers</p></b>')
            self.label2.setFont(QFont("Arial", 15))


# -----------------------------------------------------------------------------
# GUI: Mode selection (Trainer / Exam)
# -----------------------------------------------------------------------------
class OpenWindow(QMainWindow):
    """Initial window: choose Trainer (80 questions) or Exam (40 questions)."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(650, 350)
        self.setWindowTitle("LPI Exam Simulator")

        def trainer() -> None:
            global var
            var = TRAINER_QUESTION_COUNT
            window3.close()

        def exam() -> None:
            global var
            var = EXAM_QUESTION_COUNT
            window3.close()

        def closeit() -> None:
            sys.exit(0)

        self.label = QLabel("Welcome to LPI 010-160 exam simulator/trainer")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.label.setFont(QFont("Arial", 20))
        self.label1 = QLabel(
            "‣ Trainer mode includes all 80 questions in random sequence. "
            "Press <Trainer> to start."
        )
        self.label1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label1.setWordWrap(True)
        self.label2 = QLabel(
            "‣ Exam mode is 40 random questions with time counter. Press <Exam> to start."
        )
        self.label2.setWordWrap(True)
        self.label3 = QLabel("Created by Andrey Pautov, 1200km@gmail.com")
        self.button1 = QPushButton("Trainer")
        self.button1.resize(100, 40)
        self.button2 = QPushButton("Exam")
        self.button2.resize(100, 40)
        self.button3 = QPushButton("Exit")
        self.button3.resize(100, 40)
        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0, 1, 8)
        layout.addWidget(self.label1, 4, 0, 2, 4)
        layout.addWidget(self.label2, 6, 0, 2, 6)
        layout.addWidget(self.button1, 9, 1, 1, 1)
        layout.addWidget(self.button2, 9, 2)
        layout.addWidget(self.button3, 9, 3)
        layout.addWidget(self.label3, 10, 0)
        for b in (self.button1, self.button2, self.button3):
            b.setCheckable(True)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.button1.clicked.connect(trainer)
        self.button2.clicked.connect(exam)
        self.button3.clicked.connect(closeit)


# -----------------------------------------------------------------------------
# Main entry and question loop (uses globals num, header, body, right_a)
# -----------------------------------------------------------------------------
def main() -> None:
    global text_lines, num, header, body, right_a, all_counter, time_elapsed, wrong_answ, RA_COUNTER
    text_lines = load_question_bank()
    app = QApplication(sys.argv)
    window3 = OpenWindow()
    window3.show()
    app.exec()

    rangenum = var
    rangelist = list(range(1, 81))
    random.shuffle(rangelist)
    rangelist = rangelist[:rangenum]
    filllist = list(FILL_IN_QUESTION_NUMBERS)
    for i in rangelist:
        num, header, body, right_a = question(i)
        if i in filllist:
            window2 = QuestionFill(current_question_number=i)
            window2.show()
            all_counter += 1
            app.exec()
        else:
            window = MainWindow(current_question_number=i)
            window.show()
            all_counter += 1
            app.exec()

    window4 = EndWindow()
    window4.show()
    app.exec()


if __name__ == "__main__":
    main()
