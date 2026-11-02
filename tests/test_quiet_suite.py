"""Tests of `tools/hmi/quiet_suite.py` (WFB-267, FR-18): the exit code equals the suite's for a passing and a failing
suite, and the output is short. The suites are tiny folders made here. Synthetic names only."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from hmi import quiet_suite  # noqa: E402

SCRIPT = ROOT / "tools" / "hmi" / "quiet_suite.py"
PASSING = """import unittest


class T(unittest.TestCase):
    def test_a(self):
        self.assertTrue(True)

    def test_b(self):
        pass
"""
FAILING = r"""import unittest


class T(unittest.TestCase):
    def test_ok(self):
        pass

    def test_bad(self):
        print("\n".join("line %d" % n for n in range(300)))
        self.assertEqual(1, 2, "one is not two")

    def test_err(self):
        raise RuntimeError("broken")

    @unittest.skip("later")
    def test_skipped(self):
        pass
"""


def make(root: Path, source: str) -> Path:
    (root / "tests").mkdir()
    (root / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tests" / "test_sample.py").write_text(source, encoding="utf-8", newline="\n")
    return root


def direct(folder: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *quiet_suite.SUITE_ARGS], cwd=folder, capture_output=True, text=True)


def quiet(folder: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=folder, capture_output=True, text=True)


class QuietSuiteTests(unittest.TestCase):
    def test_a_passing_suite_exits_zero_with_the_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = make(Path(tmp), PASSING)
            plain, short = direct(folder), quiet(folder, "suite")
            self.assertEqual(plain.returncode, 0)
            self.assertEqual(short.returncode, plain.returncode)
            self.assertIn("suite: ran 2 tests, failures 0, errors 0, skipped 0", short.stdout)
            self.assertIn("quiet_suite: suite exit 0", short.stdout)

    def test_a_failing_suite_exits_as_the_suite_does_and_names_each_failure_briefly(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = make(Path(tmp), FAILING)
            plain, short = direct(folder), quiet(folder, "suite")
            self.assertNotEqual(plain.returncode, 0)
            self.assertEqual(short.returncode, plain.returncode)
            out = short.stdout
            self.assertIn("ran 4 tests, failures 1, errors 1, skipped 1", out)
            self.assertIn("FAIL: test_bad", out)
            self.assertIn("ERROR: test_err", out)
            self.assertIn("one is not two", out)
            self.assertIn("broken", out)
            self.assertNotIn("line 299", out)  # the test's own noise stays out
            self.assertLess(len(out.splitlines()), 30)
            self.assertLess(len(out), len(plain.stdout + plain.stderr) // 3)

    def test_the_lines_and_failure_limits_cut_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = make(Path(tmp), FAILING)
            out = quiet(folder, "--max-failures", "1", "--lines", "1", "suite").stdout
            self.assertIn("... 1 more failing tests", out)

    def test_extra_arguments_reach_unittest(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = make(Path(tmp), FAILING)
            short = quiet(folder, "suite", "-k", "test_ok")
            self.assertEqual(short.returncode, 0)
            self.assertIn("ran 1 tests, failures 0", short.stdout)

    def test_a_suite_that_does_not_start_shows_the_programs_last_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            short = quiet(Path(tmp), "suite")  # no tests folder
            self.assertNotEqual(short.returncode, 0)
            self.assertIn("suite: ran no tests", short.stdout)
            self.assertIn(f"exit {short.returncode}", short.stdout)

    def test_deploy_and_unknown_modes_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(quiet(Path(tmp), "screen", "--deploy").returncode, 2)
            self.assertEqual(quiet(Path(tmp), "screen", "--deploy=1").returncode, 2)
            self.assertEqual(quiet(Path(tmp), "bash").returncode, 2)

    def test_screen_and_checks_run_their_own_script_and_keep_its_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mode, script in (("screen", "screen.py"), ("checks", "page_checks.py")):
                plain = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / "hmi" / script), "--no-such-option"],
                    cwd=tmp, capture_output=True, text=True,
                )
                short = quiet(Path(tmp), mode, "--no-such-option")
                self.assertEqual(short.returncode, plain.returncode)
                self.assertIn(f"quiet_suite: {mode} exit {plain.returncode}", short.stdout)

    def test_the_script_summary_drops_the_json_block_and_caps_the_lines(self):
        text = "  G0_a  PASS\n{\n \"a\": 1\n}\n  G1_b  FAIL\n    problem x\n\n" + "\n".join(f"x{n}" for n in range(60))
        lines = quiet_suite.script_summary(text)
        self.assertEqual(lines[:1], ["  G1_b  FAIL"])  # a FAIL line comes first
        self.assertEqual(lines[1:3], ["  G0_a  PASS", "    problem x"])
        self.assertNotIn('"a": 1', "\n".join(lines))
        self.assertEqual(len(lines), quiet_suite.SHOWN_LINES + 1)
        self.assertTrue(lines[-1].startswith("... "))

    def test_failures_after_many_page_notes_are_never_cut(self):
        # review finding 10: screen.py prints its notes before the gate lines; 45 notes hid every FAIL
        notes = [f"note: page {n} has a long label" for n in range(45)]
        gates = ["  G5_layout  FAIL", "  G6_flow  PASS", "ERROR: descriptor x", "GATES: 1 failed"]
        lines = quiet_suite.script_summary("\n".join([*notes, *gates]))
        self.assertEqual(lines[:3], ["  G5_layout  FAIL", "ERROR: descriptor x", "GATES: 1 failed"])
        self.assertIn("  G5_layout  FAIL", lines)
        self.assertTrue(lines[-1].startswith("... ") and "more lines" in lines[-1])
        # many failing lines are all shown, with at least ten other lines beside them
        many = [f"  G{n}_x  FAIL" for n in range(60)]
        lines = quiet_suite.script_summary("\n".join([*notes, *many]))
        self.assertEqual(lines[:60], many)
        self.assertEqual(len(lines), 60 + quiet_suite.MIN_OTHER_LINES + 1)

    def test_an_unexpected_success_is_counted(self):
        source = (
            "import unittest\n\n\nclass T(unittest.TestCase):\n"
            "    @unittest.expectedFailure\n    def test_surprise(self):\n        pass\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            folder = make(Path(tmp), source)
            plain, short = direct(folder), quiet(folder, "suite")
            self.assertNotEqual(plain.returncode, 0)
            self.assertEqual(short.returncode, plain.returncode)
            self.assertIn("unexpected successes 1", short.stdout)
            self.assertIn("unexpected successes 0", quiet(folder, "suite", "-k", "nothing").stdout)

    def test_an_abbreviation_of_deploy_is_refused(self):
        for argument in ("--dep", "--depl", "--deplo=1", "--deploy", "--d"):
            self.assertTrue(quiet_suite.refused(argument), argument)
        for argument in ("--descriptor", "--devices", "--", "-d", "deploy", "--deployment", "x"):
            self.assertFalse(quiet_suite.refused(argument), argument)
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("screen", "checks", "suite"):
                short = quiet(Path(tmp), mode, "--dep")
                self.assertEqual(short.returncode, 2, mode)
                self.assertIn("refused", short.stdout)

    def test_the_scripts_do_not_accept_an_abbreviated_option(self):
        # review finding 10: argparse took `--dep` for `--deploy`; the parsers refuse abbreviations
        full_checks = ["--descriptors", "a", "--devices", "b", "--tags", "c", "--navtable", "d", "--project", "p", "--out", "o"]
        cases = (
            ("screen.py", ["--project", "p", "--dep"]),
            ("screen.py", ["--project", "p", "--app", "N"]),
            ("page_checks.py", [*full_checks, "--cov", "x"]),
        )
        with tempfile.TemporaryDirectory() as tmp:
            for script, arguments in cases:
                done = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / "hmi" / script), *arguments],
                    cwd=tmp, capture_output=True, text=True,
                )
                # page_checks.py maps a usage error to exit 1, screen.py leaves argparse's 2
                self.assertIn(done.returncode, (1, 2), script + " " + " ".join(arguments))
                self.assertIn("unrecognized arguments: --", done.stderr)


if __name__ == "__main__":
    unittest.main()
