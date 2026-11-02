"""A quiet runner for the library's suite and its offline gates: the same commands, a short summary (WFB-267, FR-18).

    python tools/hmi/quiet_suite.py suite [unittest arguments]
    python tools/hmi/quiet_suite.py screen <screen.py arguments>
    python tools/hmi/quiet_suite.py checks <page_checks.py arguments>
    options before the mode: [--lines N] [--max-failures N]

`suite` runs `python -m unittest discover -s tests` (with any further unittest arguments) from the current folder;
`screen` runs `tools/hmi/screen.py` and `checks` runs `tools/hmi/page_checks.py`, with the arguments as given. The
program is the one that runs this file, and the script is the sibling in this folder: nothing else is ever run, so a
command prefix that allows this file allows no other command. `--deploy` is refused, and so is any
argument that is a prefix of it (`--dep`, `--deplo=1`), which an option parser that allows abbreviations would accept.

The output is a summary instead of the program's whole output, which fills a builder's context on every turn:

- `suite`: the counts (tests run, failures, errors, skipped) and each failing test with its first `--lines` lines
  (default 4) and the last line of its report (the assertion), up to `--max-failures` tests (default 10);
- `screen` and `checks`: the lines of the program's output without its JSON summary block. Every line with FAIL, ERROR
  or GATES comes first and is always shown; the other lines follow, up to a total of 40 (at least 10 of them), so
  that a gate line printed after many page notes is never cut;

The last line is `quiet_suite: <mode> exit <code>` and the exit code is the program's own, so a script that reads the
exit code reads the suite's. The full output is not kept; a failure that the summary cannot explain is rerun with the
program itself.

Exit codes: the program's own; 2 for a wrong use of this runner.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = {"screen": HERE / "screen.py", "checks": HERE / "page_checks.py"}
SUITE_ARGS = ("-m", "unittest", "discover", "-s", "tests")
SHOWN_LINES = 40  # the most lines of a `screen` or `checks` run kept
RULE = "=" * 70
RAN = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
ENDING = re.compile(r"^(OK|FAILED)(?: \(([^)]*)\))?\s*$", re.MULTILINE)
URGENT = re.compile(r"FAIL|ERROR|GATES")  # the lines of a script's output that are never cut
MIN_OTHER_LINES = 10  # the least number of other lines shown beside the urgent ones
COUNT = re.compile(r"(failures|errors|skipped|expected failures|unexpected successes)=(\d+)")
HEADER = re.compile(r"^(FAIL|ERROR): (.+)$")


def run(command: list[str]) -> tuple[int, str]:
    """The command's exit code and its output (both streams, one text)."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    done = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        check=False,
    )
    return done.returncode, done.stdout.decode("utf-8", errors="replace")


def failures_of(text: str) -> list[tuple[str, list[str]]]:
    """Each failing or erroring test of an unittest report: its header and the lines of its report."""
    found: list[tuple[str, list[str]]] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if lines[index] == RULE and index + 1 < len(lines) and HEADER.match(lines[index + 1]):
            header = lines[index + 1]
            index += 2
            body: list[str] = []
            if index < len(lines) and set(lines[index]) == {"-"}:
                index += 1
            while index < len(lines) and lines[index] != RULE and not ENDING.match(lines[index]):
                if not RAN.match(lines[index]):
                    body.append(lines[index])
                index += 1
            while body and (not body[-1].strip() or set(body[-1]) == {"-"}):
                body.pop()
            found.append((header, body))
        else:
            index += 1
    return found


def suite_summary(text: str, code: int, lines: int, limit: int) -> list[str]:
    """The counts and the failing tests of an unittest run."""
    ran = RAN.search(text)
    ending = ENDING.findall(text)
    counts = {k: 0 for k in ("failures", "errors", "skipped", "unexpected successes")}
    if ending and ending[-1][1]:
        for key, number in COUNT.findall(ending[-1][1]):
            if key in counts:
                counts[key] = int(number)
    out = [
        f"suite: ran {ran.group(1) if ran else 'no'} tests, failures {counts['failures']}, "
        f"errors {counts['errors']}, skipped {counts['skipped']}, "
        f"unexpected successes {counts['unexpected successes']}"
    ]
    failed = failures_of(text)
    for header, body in failed[:limit]:
        out.append(header)
        shown = body[:lines]
        out += [f"    {line}" for line in shown]
        if len(body) > lines:
            out.append(f"    ... {body[-1].strip()}")
    if len(failed) > limit:
        out.append(f"... {len(failed) - limit} more failing tests")
    if code != 0 and not failed and not ran:
        # the suite did not start (an import fault, a wrong folder): the program's own last lines
        tail = [line for line in text.splitlines() if line.strip()][-lines:]
        out += [f"    {line}" for line in tail]
    return out


def script_summary(text: str) -> list[str]:
    """The program's output without its JSON summary block (a line `{` to the next line `}`) and
    without blank lines: the lines with FAIL, ERROR or GATES first, all of them, then the other
    lines in their order, so that the whole is `SHOWN_LINES` long (the other lines at least
    `MIN_OTHER_LINES`), with a count of the lines left out."""
    kept: list[str] = []
    inside = False
    for line in text.splitlines():
        if line == "{":
            inside = True
        if not inside and line.strip():
            kept.append(line)
        if line == "}":
            inside = False
    urgent = [line for line in kept if URGENT.search(line)]
    other = [line for line in kept if not URGENT.search(line)]
    room = max(SHOWN_LINES - len(urgent), MIN_OTHER_LINES)
    shown = [*urgent, *other[:room]]
    if len(other) > room:
        shown.append(f"... {len(other) - room} more lines")
    return shown


def parse(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--lines", type=int, default=4, help="lines of a failing test shown")
    parser.add_argument("--max-failures", type=int, default=10, help="failing tests shown")
    parser.add_argument("mode", choices=["suite", "screen", "checks"])
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    return parser.parse_args(argv)


def refused(argument: str) -> bool:
    """Whether an argument is `--deploy`, with or without a value, or an abbreviation of it that
    argparse would accept (`--dep`): any option form that is a prefix of `--deploy`."""
    name = argument.split("=")[0]
    return len(name) > 2 and name.startswith("--") and "--deploy".startswith(name)


def main(argv: list[str] | None = None) -> int:
    args = parse(sys.argv[1:] if argv is None else argv)
    if any(refused(a) for a in args.arguments):
        print("quiet_suite: --deploy is refused")
        return 2
    if args.mode == "suite":
        command = [sys.executable, *SUITE_ARGS, *args.arguments]
    else:
        command = [sys.executable, str(SCRIPTS[args.mode]), *args.arguments]
    code, text = run(command)
    if args.mode == "suite":
        lines = suite_summary(text, code, args.lines, args.max_failures)
    else:
        lines = script_summary(text)
    print("\n".join([*lines, f"quiet_suite: {args.mode} exit {code}"]))
    return code


if __name__ == "__main__":
    sys.exit(main())
