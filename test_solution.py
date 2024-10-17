from __future__ import annotations

import argparse
import os
import re
import traceback as tb
from pathlib import Path

from examples_local import examples
from marker import Marker, Result

marker = Marker()

GREEN = "\33[32m"
RED = "\033[91m"
CEND = "\033[0m"


def print_colour(text: str, c: str) -> None:
    print(c + text + CEND)


def green_print(text: str) -> None:
    print_colour(text, GREEN)


def red_print(text: str) -> None:
    print_colour(text, RED)


def main(arguments: list[str] | None = None) -> None:
    # argparser
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="The question to test")
    args = parser.parse_args(arguments)

    # get user entered question
    q = args.question

    # grab the question from examples based on question number
    question = examples[int(q)]

    folder = "solutions"
    pattern = re.compile("team_(.+)_question_" + q + ".py")
    filename = None
    for file in os.listdir(folder):
        if pattern.fullmatch(file):
            filename = Path(folder) / file

    if filename is None:
        msg = (
            "Solution not found. "
            "Make sure you have a file at solutions/team_{team_name}_question_{q}.py."
        )
        raise FileNotFoundError(msg)

    # mark the question
    print(f"Testing question {q}\n")
    results = marker.mark(question, filename)

    for i, test_case_result in enumerate(results.test_case_results):
        if test_case_result.result == Result.FAILED:
            red_print(f"Test {i+1}: FAIL")
            test_case = examples[int(q)].test_cases[i]
            if len(test_case.input_args) == 1:
                (input_args,) = test_case.input_args
            else:
                input_args = test_case.input_args
            print(f"Input: {input_args}")
            print(f"Expected output: {test_case.expected_output}")
            print(f"Received output: {test_case_result.output}")

            if isinstance(test_case_result.message, Exception):
                tb.print_exception(test_case_result.message)
            else:
                print(f"Message: {test_case_result.message}")

        else:
            green_print(f"Test {i+1}: PASS")
            print("\n")


if __name__ == "__main__":
    raise SystemExit(main())
