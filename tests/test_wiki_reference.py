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


DESCRIPTOR = json.loads((ROOT / "schemas" / "screen-descriptor.schema.json").read_text(encoding="utf-8"))
DEVICES = json.loads((ROOT / "schemas" / "devices.schema.json").read_text(encoding="utf-8"))
CONTRACTS = json.loads((ROOT / "library" / "contracts.json").read_text(encoding="utf-8"))
COMPONENTS = json.loads((ROOT / "module" / "components.json").read_text(encoding="utf-8"))


class ViewBuilderReference(unittest.TestCase):
    """Page 18, the view builder reference."""

    # each key table of the page and the object schema it states (schema, path to the object)
    KEY_TABLES = {
        "4": (DEVICES, ()), "5": (DEVICES, ("$defs", "device")), "6": (DEVICES, ("$defs", "member")),
        "7": (DESCRIPTOR, ()), "9": (DESCRIPTOR, ("properties", "screen")), "10": (DESCRIPTOR, ("$defs", "symbol")),
        "12": (DESCRIPTOR, ("$defs", "symbol", "properties", "states", "items")),
        "33": (DESCRIPTOR, ("$defs", "card")), "34": (DESCRIPTOR, ("$defs", "group")),
        "35": (DESCRIPTOR, ("$defs", "flexSymbol")), "36": (DESCRIPTOR, ("$defs", "label")),
        "37": (DESCRIPTOR, ("properties", "sections", "items")), "38": (DESCRIPTOR, ("properties", "junctions", "items")),
        "39": (DESCRIPTOR, ("properties", "pipes", "items")),
        "40": (DESCRIPTOR, ("$defs", "end", "oneOf", 0)), "41": (DESCRIPTOR, ("$defs", "end", "oneOf", 1)),
        "43": (DESCRIPTOR, ("properties", "labels", "items")),
        "44": (DESCRIPTOR, ("properties", "labels", "items", "properties", "emphasis")),
        "45": (DESCRIPTOR, ("properties", "buttons", "items")), "47": (DESCRIPTOR, ("properties", "bars", "items")),
        "48": (DESCRIPTOR, ("$defs", "symbol", "properties", "bar")),
        "49": (DESCRIPTOR, ("properties", "trends", "items")),
        "50": (DESCRIPTOR, ("properties", "trends", "items", "properties", "pens", "items")),
        "51": (DESCRIPTOR, ("properties", "lines", "items")), "52": (DESCRIPTOR, ("properties", "links", "items")),
        "53": (DESCRIPTOR, ("properties", "brackets", "items")), "54": (DESCRIPTOR, ("properties", "wells", "items")),
        "55": (DESCRIPTOR, ("properties", "wells", "items", "properties", "marks", "items")),
        "56": (DESCRIPTOR, ("properties", "alarmPanels", "items")),
    }
    # the parameter tables of section 6 and the view each states
    PARAM_TABLES = {"14": "Automation/Pump", "15": "Automation/Motor", "16": "Automation/Fan", "17": "Automation/Valve",
                    "18": "Automation/AnalogValve", "19": "Automation/Damper", "20": "Automation/Filter",
                    "21": "Automation/Switch", "22": "Automation/Indicator", "23": "Automation/Generator",
                    "24": "Automation/GeneratorSet", "25": "Automation/Tank", "26": "Automation/Readout",
                    "27": "Instrument/Field", "28": "Instrument/Controller", "29": "Instrument/Sequence"}

    @classmethod
    def setUpClass(cls):
        cls.text = page("18-view-builder-reference.md")

    @staticmethod
    def resolve(schema: dict, path: tuple) -> dict:
        at = schema
        for key in path:
            at = at[key]
            if isinstance(at, dict) and "$ref" in at:
                target = schema
                for part in at["$ref"].lstrip("#/").split("/"):
                    target = target[part]
                at = target
        return at

    def test_every_key_table_lists_exactly_the_keys_of_its_schema_object_and_which_are_required(self):
        for number, (schema, path) in self.KEY_TABLES.items():
            obj = self.resolve(schema, path)
            rows = {r[0].strip("`"): r for r in table(self.text, number)}
            self.assertEqual(set(rows), set(obj["properties"]), f"Table {number}")
            for key, r in rows.items():
                self.assertEqual(r[2].lower().startswith("yes"), key in obj.get("required", []), f"Table {number}, {key}")

    def test_every_parameter_table_gives_the_parameters_and_defaults_of_its_view(self):
        for number, view in self.PARAM_TABLES.items():
            self.assertIn(f"`{view}`", re.search(rf"^Table {number}\. .*$", self.text, re.M).group(0))
            rows = {r[0].strip("`"): r for r in table(self.text, number)}
            params = CONTRACTS[view]["params"]
            self.assertEqual(set(rows), set(params), f"Table {number}, {view}")
            for name, default in params.items():
                self.assertEqual(json.loads(rows[name][2].strip("`")), default, f"Table {number}, {view}, {name}")
        self.assertEqual({v for v in self.PARAM_TABLES.values()}, set(screen.KIND_VIEW.values()) | {screen.GENSET_VIEW})

    def test_table_2_gives_every_option_of_the_command_line(self):
        source = (ROOT / "tools" / "hmi" / "screen.py").read_text(encoding="utf-8")
        options = set(re.findall(r"add_argument\(\"(--[a-z-]+)\"", source))
        listed = {r[0].strip("`") for r in table(self.text, "2")}
        self.assertEqual(listed, options)

    def test_table_11_gives_every_library_kind_with_its_view(self):
        rows = table(self.text, "11")
        views = {r[0].split()[0].strip("`"): r[1].strip("`") for r in rows if "genset" not in r[0]}
        self.assertEqual(views, screen.KIND_VIEW)

    def test_the_worked_examples_validate_and_the_device_model_passes_the_gate(self):
        """Section 13 holds files a builder may copy: the two descriptors pass the schema (gate G0), and the device model
        passes the schema and gate G7 devices against the diagram's device symbols."""
        from hmi import gates, library_profile
        section = self.text[self.text.index("## 13. "):self.text.index("## 14. ")]
        blocks = [json.loads(b) for b in re.findall(r"```json\n(.*?)\n```", section, re.S)]
        descs = [b for b in blocks if b.get("schema") == "cadre-hmi-screen/1"]
        models = [b for b in blocks if b.get("schema") == "cadre-hmi-devices/1"]
        self.assertEqual(([d["screen"]["layout"] for d in descs], len(models)), (["diagram", "cards"], 1))
        self.assertEqual(screen.schema_errors(descs, ["intake.json", "overview.json"]), [])
        self.assertEqual(screen.devices_schema_errors(models[0], "devices.json"), [])
        res = gates.g7_devices(models[0], library_profile.build(screen.load_contracts()),
                               screen.device_symbols(descs[:1], models[0]))
        self.assertEqual((res["ok"], res["problems"], res["warnings"]), (True, [], []))

    def test_table_4a_gives_the_library_icons_the_module_navigation_icons_and_both(self):
        rows = [set(re.findall(r"`([a-z0-9-]+)`", r[1])) for r in table(self.text, "4a")]
        library = {p.stem for p in (ROOT / "library" / "icons").glob("*.json") if p.stem != "index"}
        module = {n for n in COMPONENTS["cadre.ob.navigationitem"]["props"]["iconName"]["enum"] if n}
        self.assertEqual(rows, [library, module, library & module])

    def test_table_58_gives_every_module_only_kind_with_its_component(self):
        rows = {r[0].strip("`"): r[1].strip("`") for r in table(self.text, "58")}
        want = {k: v for k, v in screen.MODULE_ONLY.items() if k not in screen.FRAME_ONLY}
        self.assertEqual(rows, want)
        for kind, ctype in want.items():
            self.assertIn(ctype, COMPONENTS, kind)


if __name__ == "__main__":
    unittest.main()
