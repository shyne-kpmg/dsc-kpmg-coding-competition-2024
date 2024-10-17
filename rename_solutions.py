from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


def main(arguments: list[str] | None = None) -> int:
    # argparser
    parser = argparse.ArgumentParser()
    parser.add_argument("team_name", help="The team name you have chosen")
    args = parser.parse_args(arguments)

    # get user entered team name
    team_name = args.team_name

    sol_dir = "solutions"
    pattern = re.compile(r"team_(.+)_question_(\d+).py")
    for file in os.listdir(sol_dir):
        if bool(pattern.fullmatch(file)):
            new_name = re.sub(pattern, r"team_" + team_name + r"_question_\2.py", file)
            old_path = Path(sol_dir) / file
            new_path = Path(sol_dir) / new_name
            Path.rename(old_path, new_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
