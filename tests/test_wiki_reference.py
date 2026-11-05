"""The design-time reference pages of the wiki (pages 16, 17 and 18) are written by hand from generated sources: the library
profile (`library/profile.json`), the descriptor and device model schemas and the module tables of `tools/hmi/screen.py`. These
tests hold the tables of each page to those sources, so that a change to a kind, a member, a write path or a descriptor key that the
pages do not follow fails here. When one fails, correct the page from its source; never edit the source to suit the page.

Run from the repository root:  python -m unittest tests.test_wiki_reference
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import screen  # noqa: E402

WIKI = ROOT / "wiki"
PROFILE = json.loads((ROOT / "library" / "profile.json").read_text(encoding="utf-8"))
FORBIDDEN = ("—", "–", "→", "←", "⇒", "->", "=>")   # em and en dashes, arrows (CLAUDE.md section 7)
PAGES = ("16-component-selection.md", "17-tag-model-and-udts.md", "18-view-builder-reference.md")


def page(name: str) -> str:
    return (WIKI / name).read_text(encoding="utf-8")


def table(text: str, number: str) -> list[list[str]]:
    """The body rows of the table whose caption starts `Table <number>.`, each as its list of cells."""
    m = re.search(rf"^Table {re.escape(number)}\. .*$", text, re.M)
    if not m:
        raise AssertionError(f"no Table {number}")
    rows, started = [], False
    for line in text[m.end():].splitlines():
        if line.startswith("|"):
            started = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                rows.append(cells)
        elif started:
            break
        elif line.strip():
            raise AssertionError(f"Table {number}: text between the caption and the table")
    return rows[1:]   # without the header


def code_spans(text: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", text))


def prose(text: str) -> str:
    """The page without its fenced code blocks (JSON examples may hold arrows of their own)."""
    return re.sub(r"^```.*?^```", "", text, flags=re.M | re.S)


class HouseStyle(unittest.TestCase):
    def test_no_dash_or_arrow_in_the_prose_of_the_reference_pages(self):
        for name in PAGES:
            for i, line in enumerate(prose(page(name)).splitlines(), 1):
                for bad in FORBIDDEN:
                    self.assertNotIn(bad, line, f"{name} line {i}")

    def test_each_page_is_in_the_index(self):
        index = page("index.md")
        for name in PAGES:
            self.assertIn(f"]({name})", index)


class SelectionGuide(unittest.TestCase):
    """Page 16, the component selection guide."""

    @classmethod
    def setUpClass(cls):
        cls.text = page("16-component-selection.md")

    def test_table_8_has_a_row_for_every_library_kind_with_its_view_and_module_component(self):
        rows = table(self.text, "8")
        kinds = {}
        for r in rows:
            kinds.setdefault(r[1].strip("`"), r)
        self.assertEqual(set(kinds), set(screen.KIND_VIEW))
        for kind, r in kinds.items():
            self.assertIn(f"`{screen.KIND_VIEW[kind]}`", r[2], kind)
            if kind in screen.MODULE_KIND:
                self.assertIn(f"`{screen.MODULE_KIND[kind]}`", r[3], kind)
            else:
                self.assertTrue(r[3].startswith("None"), kind)

    def test_table_10_lists_every_module_only_kind_once_and_no_frame_component(self):
        listed = []
        for r in table(self.text, "10"):
            listed += re.findall(r"`([a-z0-9-]+)`", r[1])
        wanted = set(screen.MODULE_ONLY) - set(screen.FRAME_ONLY)
        self.assertEqual(sorted(listed), sorted(wanted))
        self.assertIn(f"`FRAME_ONLY`, {len(wanted)} kinds)", self.text)

    def test_table_3_names_every_kind_the_module_hands_back_to_the_library_view(self):
        named = set()
        for r in table(self.text, "3"):
            named |= set(re.findall(r"`([a-z-]+)`", r[0]))
        self.assertLessEqual(set(screen.MODULE_EXCEPT) | set(screen.MODULE_NEEDS), named)
        no_component = set(screen.KIND_VIEW) - set(screen.MODULE_KIND)
        self.assertLessEqual(no_component, named)

    def test_table_6_gives_the_faceplate_of_every_device_kind_in_both_styles(self):
        seen = set()
        for r in table(self.text, "6"):
            for kind in re.findall(r"`([a-z-]+)`", r[0]):
                seen.add(kind)
                faces = PROFILE["deviceKinds"][kind]["faceplates"]
                self.assertIn(f"`{faces['openbridge']}`", r[1], kind)
                self.assertIn(f"`{faces['asm']}`", r[2], kind)
        self.assertEqual(seen, set(PROFILE["deviceKinds"]))

    def test_the_interlock_and_maintenance_kinds_follow_the_profile(self):
        row = {r[0]: r for r in table(self.text, "15")}
        for option, key in (("Interlocks and permissives", "interlocks"), ("Maintenance functions", "maintenance")):
            listed = set(re.findall(r"`([a-z-]+)`", row[option][2])) & set(PROFILE["deviceKinds"])
            have = {k for k, v in PROFILE["deviceKinds"].items() if v[key]} - {"readout", "instrument-field"}
            self.assertEqual(listed, have, option)


class TagModel(unittest.TestCase):
    """Page 17, the tag model and the UDT of each device kind."""

    # the member tables of section 4 and the device kinds each one states
    KIND_TABLES = {"4": ("pump", "motor", "fan"), "5": ("valve", "analogvalve", "damper"), "6": ("tank",),
                   "7": ("instrument", "readout", "instrument-field"), "8": ("controller",), "9": ("indicator",),
                   "10": ("sequence",), "11": ("generator",)}

    @classmethod
    def setUpClass(cls):
        cls.text = page("17-tag-model-and-udts.md")

    @staticmethod
    def members(rows) -> dict[str, list[str]]:
        """Member name to row, for rows whose first cell names one or more members in code spans."""
        out = {}
        for r in rows:
            for m in re.findall(r"`([A-Za-z0-9_/]+)`", r[0]):
                out[m] = r
        return out

    def test_the_member_tables_give_every_member_of_every_kind_with_its_type(self):
        self.assertEqual({k for ks in self.KIND_TABLES.values() for k in ks}, set(PROFILE["deviceKinds"]))
        for number, kinds in self.KIND_TABLES.items():
            listed = self.members(table(self.text, number))
            for kind in kinds:
                spec = PROFILE["deviceKinds"][kind]["members"]
                own = {m: s for m, s in spec.items() if not m.startswith("mnt/")}
                self.assertEqual(set(listed), set(own), f"Table {number}, {kind}")
                for m, s in own.items():
                    self.assertEqual(listed[m][1], s["type"], f"Table {number}, {kind}, {m}")

    def test_the_test_model_column_follows_the_generator(self):
        for number, kinds in self.KIND_TABLES.items():
            listed = self.members(table(self.text, number))
            created = screen.FACEPLATE_MEMBERS[kinds[0]]
            for m, r in listed.items():
                self.assertEqual(r[3].startswith("Yes"), m in created, f"Table {number}, {m}")

    def test_table_12_gives_every_maintenance_member(self):
        listed = self.members(table(self.text, "12"))
        mnt = {m: s["type"] for spec in PROFILE["deviceKinds"].values() for m, s in spec["members"].items()
               if m.startswith("mnt/")}
        self.assertEqual(set(listed), set(mnt))
        for m, t in mnt.items():
            self.assertEqual(listed[m][1], t, m)

    def test_table_16_gives_every_write_path_with_its_members(self):
        rows = {r[0]: r for r in table(self.text, "16")}
        self.assertEqual(set(rows), set(PROFILE["writePaths"]))
        for path, spec in PROFILE["writePaths"].items():
            named = set(re.findall(r"`([A-Za-z0-9_/]+)`", rows[path][2]))
            if spec["members"]:
                self.assertEqual(named, set(spec["members"]), path)
            else:   # W7, W10, W11, W19: the profile names no member; the page says what the path writes
                self.assertTrue(rows[path][2], path)
            self.assertEqual(rows[path][3], spec["role"], path)

    def test_table_17_gives_every_pulse_member_with_its_kind(self):
        listed = {}
        for r in table(self.text, "17"):
            for m in re.findall(r"`([A-Za-z0-9_]+)`", r[0]):
                listed[m] = r[1]
        want = {m: k for k, spec in PROFILE["deviceKinds"].items() for m in spec["pulses"]}
        self.assertEqual(listed, want)

    def test_the_device_model_of_the_worked_example_validates_and_passes_the_gate(self):
        """Section 9.4 is an entry a builder may copy: it validates against the schema and passes gate G7 devices."""
        from hmi import gates, library_profile
        block = re.search(r"### 9\.4 .*?```json\n(.*?)\n```", self.text, re.S).group(1)
        model = json.loads(block)
        self.assertEqual(screen.devices_schema_errors(model, "wiki/17"), [])
        res = gates.g7_devices(model, library_profile.build(screen.load_contracts()), [])
        self.assertEqual((res["ok"], res["problems"], res["warnings"]), (True, [], []))
        self.assertEqual([d["kind"] for d in model["devices"]], ["pump"])

    def test_tables_18_and_19_give_the_interlock_members_the_gate_checks(self):
        from hmi import gates
        for number, want in (("18", gates.ILK_CONDITION), ("19", gates.ILK_SUMMARY)):
            listed = self.members(table(self.text, number))
            for m, t in want.items():
                self.assertIn(m, listed, f"Table {number}")
                self.assertEqual(listed[m][1], t, f"Table {number}, {m}")


if __name__ == "__main__":
    unittest.main()
