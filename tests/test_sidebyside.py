"""Tests of `tools/compare/sidebyside.py` (S10-B, ARCH-WFB-01 revision B8 Table 109, schema `cadre-hmi-sidebyside/1`).

The page-list and discovery tests are offline; the composition tests drive headless Chromium and run when
Playwright is importable (ctig's `.venv`)."""
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump, fixture, png, validate  # noqa: E402

sys.path.insert(0, str(ROOT / "tools" / "compare"))
import sidebyside  # noqa: E402

try:
    import playwright.sync_api  # noqa: F401
    HAVE_BROWSER = True
except ImportError:
    HAVE_BROWSER = False

NAMES = ["Overview", "PumpStation"]
FACEPLATES = ["PUMP01"]


def dims(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


def folder(base: Path, name: str, names=NAMES + FACEPLATES, colour=(120, 120, 120), size=(160, 90), sub=False):
    f = base / name
    target = f / "pictures" if sub else f
    target.mkdir(parents=True, exist_ok=True)
    for n in names:
        if not (target / f"{n}.png").exists():     # a picture a test removed stays removed
            (target / f"{n}.png").write_bytes(png(size[0], size[1], colour))
    return f


def pages_file(base: Path, lines=None) -> Path:
    p = base / "pages.txt"
    p.write_text("\n".join(lines or NAMES + [f"faceplate:{n}" for n in FACEPLATES]) + "\n", encoding="utf-8", newline="\n")
    return p


class OfflineTests(unittest.TestCase):
    def test_a_page_list_reads_names_kinds_and_json(self):
        with tempfile.TemporaryDirectory() as t:
            p = pages_file(Path(t), ["Overview", "page:PumpStation", "faceplate:PUMP01", "# not a comment line here"])
            got = sidebyside.read_pages(str(p), None)
            self.assertEqual([(x["name"], x["kind"]) for x in got[:3]],
                             [("Overview", "page"), ("PumpStation", "page"), ("PUMP01", "faceplate")])
            j = dump(Path(t) / "l.json", ["A", {"name": "B", "kind": "faceplate"}])
            self.assertEqual([(x["name"], x["kind"]) for x in sidebyside.read_pages(str(j), None)],
                             [("A", "page"), ("B", "faceplate")])

    def test_the_list_may_come_from_an_asm_model(self):
        with tempfile.TemporaryDirectory() as t:
            model = {"pages": [{"id": "A", "built": True}, {"id": "S", "built": False}],
                     "devices": {"P1": {"faceplate": "pump"}, "U1": {"faceplate": "empty"}}}
            m = dump(Path(t) / "m.json", model)
            self.assertEqual([(x["name"], x["kind"]) for x in sidebyside.read_pages(None, str(m))],
                             [("A", "page"), ("P1", "faceplate")])

    def test_a_picture_is_found_in_the_folder_in_pictures_or_by_a_capture_manifest(self):
        with tempfile.TemporaryDirectory() as t:
            b = Path(t)
            f1 = folder(b, "a", ["X"])
            f2 = folder(b, "b", ["X"], sub=True)
            f3 = b / "c"
            f3.mkdir()
            (f3 / "shot_7.png").write_bytes(png())
            dump(f3 / "manifest.json", {"windows": [{"target": "X", "picture": "shot_7.png"}]})
            for f in (f1, f2, f3):
                self.assertIsNotNone(sidebyside.find_picture(f, "X"), f)
            self.assertIsNone(sidebyside.find_picture(f1, "nope"))

    def test_a_faceplate_that_shares_a_pages_name_gets_its_own_file(self):
        used: set[str] = set()
        self.assertEqual(sidebyside.file_name({"name": "A", "kind": "page"}, used), "A.png")
        self.assertEqual(sidebyside.file_name({"name": "A", "kind": "faceplate"}, used), "A-faceplate.png")

    def test_faults_exit_1(self):
        with tempfile.TemporaryDirectory() as t:
            b = Path(t)
            o = folder(b, "o")
            self.assertEqual(sidebyside.main(["--original", str(b / "none"), "--pages", str(pages_file(b)),
                                              "--out", str(b / "out")]), 1)
            self.assertEqual(sidebyside.main(["--original", str(o), "--column", f"bogus={o}", "--pages",
                                              str(pages_file(b)), "--out", str(b / "out")]), 1)
            self.assertEqual(sidebyside.main(["--original", str(o), "--out", str(b / "out")]), 1)    # no list
            self.assertEqual(sidebyside.main(["--original", str(o), "--pages", str(pages_file(b)), "--sheets",
                                              "--out", str(b / "out")]), 1)                           # one column
            self.assertEqual(sidebyside.main(["--original", str(o), "--pages", str(pages_file(b)), "--window", "x",
                                              "--out", str(b / "out")]), 1)

    def test_the_schema_has_the_registry_identifier(self):
        schema = json.loads((ROOT / "schemas" / "cadre-hmi-sidebyside-1.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "cadre-hmi-sidebyside/1")


@unittest.skipUnless(HAVE_BROWSER, "Playwright is not importable here; run under ctig's .venv")
class ComposeTests(unittest.TestCase):
    def run_it(self, base: Path, *extra, columns=("preview", "asm"), pages=None):
        args = ["--original", str(folder(base, "orig", colour=(200, 120, 120)))]
        for c in columns:
            args += ["--column", f"{c}={folder(base, c, colour=(120, 200, 120))}"]
        args += ["--pages", str(pages or pages_file(base)), "--window", "160x90", "--out", str(base / "out"), *extra]
        return sidebyside.main(args)

    def test_a_picture_for_every_page_and_faceplate_with_the_columns_side_by_side(self):
        with tempfile.TemporaryDirectory() as t:
            b = Path(t)
            self.assertEqual(self.run_it(b), 0)
            for n in NAMES + FACEPLATES:
                w, h = dims(b / "out" / f"{n}.png")
                self.assertGreaterEqual(w, 3 * 160)       # three pictures of 160 px, side by side
                self.assertGreaterEqual(h, 90)
            doc = json.loads((b / "out" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(validate(doc, "cadre-hmi-sidebyside-1.json"), [])
            self.assertEqual(doc["columns"], ["original", "preview", "asm"])
            self.assertEqual(doc["missing"], [])
            self.assertEqual([p["name"] for p in doc["pictures"]], NAMES + FACEPLATES)
            self.assertIsNone(doc["sheets"])

    def test_each_source_is_named_by_path_and_digest(self):
        with tempfile.TemporaryDirectory() as t:
            b = Path(t)
            self.run_it(b)
            doc = json.loads((b / "out" / "manifest.json").read_text(encoding="utf-8"))
            src = doc["pictures"][0]["sources"]
            self.assertEqual([s["column"] for s in src], ["original", "preview", "asm"])
            first = Path(src[0]["path"])
            self.assertEqual(src[0]["sha256"], hashlib.sha256(first.read_bytes()).hexdigest())

    def test_a_missing_picture_is_a_labelled_gap_and_exit_2(self):
        with tempfile.TemporaryDirectory() as t:
            b = Path(t)
            self.run_it(b)   # builds the folders
            (b / "asm" / "PumpStation.png").unlink()
            args = ["--original", str(b / "orig"), "--column", f"preview={b / 'preview'}", "--column",
                    f"asm={b / 'asm'}", "--pages", str(pages_file(b)), "--window", "160x90", "--out", str(b / "out")]
            self.assertEqual(sidebyside.main(args), 2)
            doc = json.loads((b / "out" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(doc["missing"], [{"name": "PumpStation", "kind": "page", "column": "asm"}])
            self.assertTrue((b / "out" / "PumpStation.png").is_file())      # still composed, the gap labelled

    def test_the_sheets_tile_the_last_two_columns_page_by_page_in_one_grid(self):
        with tempfile.TemporaryDirectory() as t:
            b = Path(t)
            self.assertEqual(self.run_it(b, "--sheets"), 0)
            doc = json.loads((b / "out" / "manifest.json").read_text(encoding="utf-8"))
            s = doc["sheets"]
            self.assertEqual((s["a"], s["b"], s["columns"]), ("sheet-a.png", "sheet-b.png", ["preview", "asm"]))
            g = s["grid"]
            self.assertEqual((g["cols"], g["rows"]), (2, 2))               # three pictures in a 2 by 2 grid
            self.assertEqual(g["order"], NAMES + FACEPLATES)
            self.assertEqual(dims(b / "out" / "sheet-a.png"), dims(b / "out" / "sheet-b.png"))
            self.assertEqual(g["cell_h"], round(g["cell_w"] * 90 / 160))

    def test_the_sheets_of_two_runs_have_the_same_grid_and_size(self):
        with tempfile.TemporaryDirectory() as t:
            b = Path(t)
            self.run_it(b, "--sheets")
            first = dims(b / "out" / "sheet-a.png")
            self.run_it(b, "--sheets")
            self.assertEqual(dims(b / "out" / "sheet-a.png"), first)

    def test_one_column_beside_the_original_is_enough_without_sheets(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(self.run_it(Path(t), columns=("asm",)), 0)

    def test_the_ignition_column_is_accepted(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(self.run_it(Path(t), columns=("preview", "asm", "ignition"), pages=None), 0)


if __name__ == "__main__":
    unittest.main()
