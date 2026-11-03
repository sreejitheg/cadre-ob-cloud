"""Unit tests for the generated operator walk (tools/compare/walk.py): the plan, the glass table, the
number format, the scenes, and the runner's rules of evidence against a glass and a gateway that are
stubs. Offline: no gateway, no browser.

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "compare"))

import walk  # noqa: E402
import walk_plan  # noqa: E402
import walk_run  # noqa: E402
from hmi import framework, library, scripts  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
WTP = ROOT / "screens" / "wtp"
VIEWS = ROOT / "build" / "cadre_hmi_base" / "com.inductiveautomation.perspective" / "views"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pilot_plan(**kw) -> dict:
    return walk.build_plan([load(FIXTURES / "pilot-supply.json")], devices=load(FIXTURES / "pilot-devices.json"),
                           tags=load(FIXTURES / "pilot-tags.json"), **kw)


def pilot_plan_with_effects() -> dict:
    return pilot_plan(effects=load(FIXTURES / "pilot-walk-effects.json"))


def wtp_plan(render="stock", effects=True) -> dict:
    descs = [load(WTP / f"{n}.json") for n in ("overview", "intake", "filtration", "disinfection")]
    return walk.build_plan(descs, tags=load(WTP / "tags.json"), render=render,
                           effects=load(WTP / "walk-effects.json") if effects else None)


def capabilities(plan: dict) -> set:
    """(kind, write path, device, member) of every step of group C."""
    return {(s["kind"], s["path"], s["device"], s["member"]) for s in plan["steps"] if s["group"] == "C"}


class FormatTests(unittest.TestCase):
    """The walk's formatter against `numberFormat` with a Java decimal pattern, for the patterns the
    library and the descriptors use. Java rounds half even on the exact value of the double."""

    def test_patterns_of_the_library(self):
        cases = [(47.37, "0.0", "47.4"), (50, "0.0", "50.0"), (0.149, "0.00", "0.15"), (7, "0", "7"),
                 (79.6, "0", "80"), (1234.5, "#,##0.0", "1,234.5"), (1234567, "#,##0", "1,234,567"),
                 (0.5, "#,##0.0", "0.5"), (999.96, "#,##0.0", "1,000.0"), (-3.25, "0.0", "-3.2"),
                 (1.5, "0.000", "1.500"), (20000, "0", "20000"), (12.3456, "0.0##", "12.346"),
                 (12.3, "0.0##", "12.3"), (5, "000", "005")]
        for value, pattern, text in cases:
            self.assertEqual(walk.number_format(value, pattern), text, (value, pattern))

    def test_half_even_on_the_exact_value(self):
        # ties in decimal that are exact in binary round to the even digit
        self.assertEqual(walk.number_format(2.5, "0"), "2")
        self.assertEqual(walk.number_format(3.5, "0"), "4")
        self.assertEqual(walk.number_format(0.125, "0.00"), "0.12")
        self.assertEqual(walk.number_format(0.375, "0.00"), "0.38")
        # 0.135 is a little above the tie as a double, so it rounds up
        self.assertEqual(walk.number_format(0.135, "0.00"), "0.14")

    def test_a_pattern_not_implemented_is_refused(self):
        for pattern in ("0.0%", "#.##", "0.0E0", "0;-0", "", "0.", "#,#,##0", "'kPa' 0", "0.0 kPa", ",##0", "0#"):
            with self.assertRaises(ValueError, msg=pattern):
                walk.number_format(1.5, pattern)

    def test_a_value_not_implemented_is_refused(self):
        for value in (True, "12", None, float("nan"), float("inf")):
            with self.assertRaises(ValueError, msg=repr(value)):
                walk.number_format(value, "0.0")
        with self.assertRaises(ValueError):   # the sign Java writes for a negative zero was not measured
            walk.number_format(-0.04, "0.0")

    def test_where_java_was_measured_to_differ_the_value_is_refused(self):
        # JDK 17.0.20.1, 2026-10-11: 0.0005 under three fraction digits is '0.000' in Java, where half
        # even on the exact value gives '0.001'; a negative zero is '-0'; a double of 1e15 and more
        # has no digit to spare. The walk refuses each rather than agree with itself.
        for value, pattern in ((0.0005, "0.000"), (-0.0005, "0.000"), (0.04, "0.0"), (0.4, "0"), (-0.0, "0"),
                               (1e23, "0"), (123456789012345678, "0"), (2 ** 53 + 1, "#,##0")):
            with self.assertRaises(ValueError, msg=(value, pattern)):
                walk.number_format(value, pattern)
        self.assertEqual(walk.number_format(0, "0.000"), "0.000")
        self.assertEqual(walk.number_format(0.001, "0.000"), "0.001")   # one unit of the pattern is written

    def test_a_float4_is_formatted_from_its_32_bit_value(self):
        # Java widens the 32 bit value: measured '0.2' for 0.15f, '99.9' for 99.95f, '16384.443' for 16384.444f
        self.assertEqual(walk.number_format(0.15, "0.0", "Float4"), "0.2")
        self.assertEqual(walk.number_format(0.15, "0.0"), "0.1")
        self.assertEqual(walk.number_format(99.95, "0.0", "Float4"), "99.9")
        self.assertEqual(walk.number_format(99.95, "0.0", "Float8"), "100.0")
        self.assertEqual(walk.number_format(16384.444, "0.000", "Float4"), "16384.443")
        self.assertEqual(walk.expect_of({"how": "line", "format": ["", "0.0", " %"]}, 0.15, "Float4"), {"line": "0.2 %"})

    def test_every_pattern_of_the_descriptors_is_implemented(self):
        gen = walk._generator()
        seen = set()
        for path in list(WTP.glob("*.json")) + [FIXTURES / "pilot-supply.json", ROOT / "screens" / "sample-pump-station.json"]:
            desc = load(path)
            if "screen" not in desc:
                continue
            for s in gen.descriptor_items(desc):
                seen |= {v for k, v in s.get("params", {}).items() if k in ("format", "setpointFormat")}
        self.assertTrue(seen)
        for pattern in sorted(seen) + ["0", "#,##0", "#,##0.0"]:
            walk.number_format(12.345, pattern)


class SceneTests(unittest.TestCase):
    def tags(self, n=12):
        out = [{"tag": f"[default]x/T{i}", "node": {"dataType": "Float8", "value": 10.0 * i}} for i in range(n)]
        out.append({"tag": "[default]x/R", "node": {"dataType": "Float8", "value": 3.0, "engLow": 0.0, "engHigh": 10.0}})
        out.append({"tag": "[default]x/I", "node": {"dataType": "Int4", "value": 40}})
        out.append({"tag": "[default]x/B1", "node": {"dataType": "Boolean", "value": True}})
        out.append({"tag": "[default]x/B0", "node": {"dataType": "Boolean", "value": False}})
        return out

    def test_numbers_are_distinct_in_range_and_differ(self):
        tags = self.tags()
        walk.scene_values(tags)
        numbers = [v for t in tags if t["range"] for v in t["values"]]
        self.assertEqual(len(numbers), len(set(numbers)), "every number of the plan is distinct")
        for t in tags:
            if not t["range"]:
                continue
            a, b = t["values"]
            self.assertNotEqual(a, b)
            self.assertLess(a, b)
            for v in (a, b):
                self.assertGreaterEqual(v, t["range"]["low"])
                self.assertLessEqual(v, t["range"]["high"])

    def test_no_number_sits_on_a_rounding_tie(self):
        tags = self.tags()
        walk.scene_values(tags)
        for t in tags:
            if t["range"] and t["node"]["dataType"].startswith("Float"):
                for v in t["values"]:
                    self.assertNotEqual(round(v * 1000) % 5, 0, v)

    def test_the_stated_range_is_used(self):
        tags = self.tags()
        walk.scene_values(tags)
        r = next(t for t in tags if t["tag"].endswith("/R"))
        self.assertEqual((r["range"]["low"], r["range"]["high"], r["range"]["from"]), (0.0, 10.0, "engLow and engHigh"))
        loose = next(t for t in tags if t["tag"].endswith("/T5"))   # configured 50: a tenth either side
        self.assertEqual((loose["range"]["low"], loose["range"]["high"]), (45.0, 55.0))

    def test_booleans_go_both_ways_and_end_as_configured(self):
        tags = self.tags()
        walk.scene_values(tags)
        self.assertEqual(next(t for t in tags if t["tag"].endswith("/B1"))["values"], [False, True])
        self.assertEqual(next(t for t in tags if t["tag"].endswith("/B0"))["values"], [True, False])

    def test_integers_stay_integers(self):
        tags = self.tags()
        walk.scene_values(tags)
        i = next(t for t in tags if t["tag"].endswith("/I"))
        self.assertTrue(all(isinstance(v, int) for v in i["values"]))
        self.assertNotEqual(i["values"][0], i["values"][1])


_GENERATED: dict = {}


def generated(view: str) -> dict:
    """A view of the parent as the generator's code writes it now (`framework.framework_views`,
    `library.library_views`), not as the build folder holds it: a caption renamed in `tools/hmi/`
    fails the pin before anything is rebuilt."""
    if not _GENERATED:
        _GENERATED.update({k: doc for k, (doc, _contract) in library.library_views().items()})
        _GENERATED.update(framework.framework_views())
    return _GENERATED[view]


def nodes_of(view: str) -> list[dict]:
    """Every component of a view of the parent."""
    doc = generated(view)
    out = []

    def visit(n):
        out.append(n)
        for c in n.get("children", []):
            visit(c)
    visit(doc["root"])
    return out


def strings_of(view: str) -> list[str]:
    """Every string the built view holds: texts, expressions and scripts."""
    out = []

    def visit(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                visit(x)
        elif isinstance(v, list):
            for x in v:
                visit(x)
    visit(generated(view))
    return out


def row_texts(view: str) -> dict[str, list[str]]:
    """For each value row of a view (a flex container whose first child is a label with a static
    text), the strings of its other labels: the caption gives what the row may read."""
    out: dict[str, list[str]] = {}
    for n in nodes_of(view):
        kids = n.get("children", [])
        if len(kids) >= 2 and kids[0]["type"] == "ia.display.label" and isinstance(kids[0]["props"].get("text"), str):
            texts = []
            for k in kids[1:]:
                if k["type"] == "ia.display.label":
                    texts.append(json.dumps(k.get("propConfig", {}).get("props.text", "")) + json.dumps(k["props"].get("text", "")))
            out.setdefault(kids[0]["props"]["text"], []).extend(texts)
    return out


class GlassTableTests(unittest.TestCase):
    """Every caption, row label, tab name and state text the walk looks for on the glass, against the
    built views of the parent and the generator's own tables. A library change that renames one
    fails here, not on the gateway."""

    def test_every_fact_is_in_the_built_view_that_draws_it(self):
        facts = walk.glass_facts()
        self.assertGreater(len(facts), 80)
        limits = dict(scripts.constant("LIMITS"))
        code = scripts.HMI
        for view, what, text in facts:
            where = f"{view} {what} {text!r}"
            if what == "limit":
                self.assertIn(text, limits.values(), where)
                self.assertIn(f'"{text}"', code, where)
                continue
            nodes, strings = nodes_of(view), strings_of(view)
            buttons = [n["props"].get("text") for n in nodes if n["type"] == "ia.input.button"]
            labels = [n["props"].get("text") for n in nodes if n["type"] == "ia.display.label"]
            if what == "button":
                self.assertIn(text, buttons, where)
            elif what == "caption":
                self.assertIn(text, labels, where)
            elif what == "tab":
                tabs = [n["props"].get("text") for n in nodes
                        if n["type"] == "ia.input.button" and n["meta"]["name"].startswith("Tab_")]
                self.assertIn(text, tabs, where)
            elif what == "text":   # a literal of an expression, or a static text
                self.assertTrue(any(f"'{text}'" in s for s in strings) or text in labels + buttons, where)
            elif what == "setpoint":   # the row caption a script hands the repeater of `Faceplate/SetpointRow`
                self.assertTrue(any(f"'label': '{text}'" in s for s in strings), where)
            elif what == "format":
                if ":" in text:
                    member, fmt = text.split(":")
                    self.assertTrue(any(f"'member': '{member}'" in s and f"'format': '{fmt}'" in s for s in strings), where)
                else:
                    fields = [n["props"].get("format") for n in nodes if n["type"] == "ia.input.numeric-entry-field"]
                    self.assertEqual(fields, [text], where)
            else:
                self.fail(f"a fact of unknown kind: {where}")

    def test_the_build_folder_is_what_the_generator_writes(self):
        # the facts are pinned against the generator's code; the views the gateway was given are those of
        # the build folder, so each view a fact names must be the same there
        for view in sorted({v for v, _what, _text in walk.glass_facts() if v != "cadre/hmi"}):
            self.assertEqual(load(VIEWS / view / "view.json"), json.loads(json.dumps(generated(view))), view)
        built = (ROOT / "build" / "cadre_hmi_base" / "ignition" / "script-python" / "cadre" / "hmi" / "code.py")
        self.assertEqual(built.read_text(encoding="utf-8"), scripts.HMI)

    def test_a_rows_text_is_the_text_of_that_row(self):
        # a state text is pinned to the expression of the row that reads it, not to any string of the
        # view: "Auto" is also a button's caption, and a rename of the row's text alone must fail here
        for view, (caption, on, off) in walk.STATE_ROW.items():
            texts = " ".join(row_texts(view)[caption])
            self.assertIn(f"'{on}'", texts, (view, caption))
            self.assertIn(f"'{off}'", texts, (view, caption))
        for view in walk.COMMANDS:
            rows = row_texts(view)
            for text in (walk.FAULT["set"], walk.FAULT["clear"]):
                self.assertIn(f"'{text}'", " ".join(rows[walk.FAULT["row"]]), (view, text))
            self.assertTrue(rows[walk.MODE_ROW], view)
        for view in walk.FORCE_VIEWS:
            texts = " ".join(row_texts(view)[walk.FORCE["row"]])
            for _v, _button, text, _s in walk.FORCE["states"]:
                self.assertIn(f"'{text}'", texts, (view, text))
        for view in ("Faceplate/Pump", "Faceplate/Valve"):
            texts = " ".join(row_texts(view)[walk.MASK["row"]])
            for _v, _button, text, _s in walk.MASK["states"]:
                self.assertIn(f"'{text}'", texts, (view, text))
        for view in walk.STEP_VIEWS:
            self.assertIn("numberFormat", " ".join(row_texts(view)[walk.STEP_ROW[0]]), view)

    def test_the_mode_texts_are_the_scripts(self):
        # the row "Control mode" reads a text the project script hands the faceplate
        for caption, _value in walk.MODES + walk.LOOP:
            self.assertTrue(f'"{caption}"' in scripts.HMI or f"'{caption}'" in scripts.HMI
                            or any(f"'{caption}'" in t for v in ("Faceplate/Pump", "Faceplate/Controller")
                                   for t in row_texts(v).get(walk.MODE_ROW, [])), caption)

    def test_the_two_automatic_buttons_are_told_apart_by_their_group(self):
        for view in ("Faceplate/Pump", "Faceplate/Valve"):
            groups = [[c["props"].get("text") for c in n.get("children", []) if c["type"] == "ia.input.button"]
                      for n in nodes_of(view)]
            for table in (walk.FORCE, walk.MASK):
                for _value, button, _text, sibling in table["states"]:
                    holding = [g for g in groups if button in g and (sibling is None or sibling in g)]
                    self.assertEqual(len(holding), 1, f"{view}: {button} beside {sibling}")

    def test_tabs_are_the_generators(self):
        for view, tab in walk.FIRST_TAB.items():
            key = view.split("/")[-1].lower()
            first = framework.ASM_TABS[0][1] if view in framework.ASM_VIEW.values() else framework.FACEPLATE_TABS[key][0][1]
            self.assertEqual(first, tab, view)
        every = {label for tabs in framework.FACEPLATE_TABS.values() for _key, label in tabs}
        for tab in {walk.BYPASS["tab"], walk.FORCE["tab"], walk.MASK["tab"], "Trend", "Alarms"} \
                | {t for _p, t, _c, _f in walk.SETPOINTS.values()}:
            self.assertIn(tab, every)

    def test_member_tables_are_the_generators(self):
        self.assertEqual({m: tuple(b) for m, b in scripts.constant("MEMBER_BOUNDS").items()}, walk.BOUNDS)
        self.assertEqual(dict(scripts.constant("LIMITS")), walk.LIMITS)
        paths = scripts.constant("PATH_MEMBERS")
        for member, (path, _tab, _caption, _fmt) in walk.SETPOINTS.items():
            self.assertIn(member, paths[path], member)
        self.assertEqual([v for _c, v in walk.MODES], [0, 1, 2])
        self.assertEqual(walk.MODE_ROW, "Control mode")

    def test_symbol_kinds_are_the_librarys(self):
        for kind, (state, _on, _off, _vert, mode) in library.DEVICE_KINDS.items():
            k = kind.lower()
            self.assertIn(k, walk.AUTOMATION)
            self.assertEqual(walk.STATE_PARAM.get(k, "on"), state, kind)
            self.assertEqual(k in walk.SPEED_KINDS, mode == "speed", kind)
        self.assertEqual(len(walk.AUTOMATION), len(library.DEVICE_KINDS))
        for alias, kind in walk.KIND_ALIAS.items():
            self.assertEqual(framework.FACEPLATE_VIEW[alias], framework.FACEPLATE_VIEW[kind])
        self.assertEqual(library.READOUT_PARAMS["setpointFormat"], "#,##0")   # the defaults `reading_rule` falls back on
        self.assertEqual(library.CONTROLLER_PARAMS["format"], "#,##0.0")

    def test_write_paths_are_the_profiles(self):
        profile = walk.load_profile()
        known = set(profile["writePaths"])
        used = {p for p, *_rest in walk.SETPOINTS.values()} | set(walk.FRAME_PATHS) | set(walk.ACK_PATH.values()) \
            | {"W1", "W2", "W4", "W5", "W10", "W13", "W16", "W17", "W18"}
        self.assertLessEqual(used, known)
        self.assertEqual(profile["writePaths"]["W18"]["function"], "pulse")
        for kind, spec in profile["deviceKinds"].items():   # every kind with a pulse has a faceplate the table knows
            if spec.get("pulses"):
                self.assertIn(spec["faceplate"], walk.PULSE_VIEWS, kind)
                self.assertIn(spec["faceplate"], walk.FIRST_TAB, kind)
        self.assertEqual(sorted(e for enc in profile["forceEncodings"] for e in enc),
                         sorted(["mnt/forceOn", "mnt/forceOff", "mnt/forceMode", "mnt/forceValue"]))


class PilotPlanTests(unittest.TestCase):
    """The plan on the fixture of the new kinds, with its tag model and its device model."""

    @classmethod
    def setUpClass(cls):
        cls.plan = pilot_plan()

    def test_schema_and_groups(self):
        self.assertEqual(self.plan["schema"], "cadre-hmi-walk/1")
        self.assertEqual(self.plan["tagRoot"], "[default]cadre_hmi_pilot")
        self.assertEqual(list(self.plan["counts"]), list(walk.GROUPS))
        for g in walk.GROUPS:
            self.assertEqual(self.plan["counts"][g], sum(s["group"] == g for s in self.plan["steps"]), g)
        self.assertEqual(len({s["id"] for s in self.plan["steps"]}), len(self.plan["steps"]))

    def test_every_route_is_walked(self):
        routes = [(s["via"], s["route"], s["label"]) for s in self.plan["steps"] if s["group"] == "N"]
        self.assertEqual(routes, [("menu", "/supply", "Supply"), ("menu", "/trends", "Trends"), ("menu", "/alerts", "Alerts")])

    def test_a_route_step_proves_the_page(self):
        steps = [s for s in self.plan["steps"] if s["group"] == "N"]
        supply = steps[0]
        self.assertEqual((supply["title"], supply["symbol"]), ("Supply", "P-1"))   # the top bar's name, a symbol placed
        self.assertEqual([s["title"] for s in steps], ["Supply", "Trends", "Alerts"])
        for s in steps:   # a menu step starts from another route
            self.assertNotEqual(s["from"], s["route"], s["id"])
            self.assertIn(s["from"], [x["route"] for x in steps], s["id"])

    def test_the_first_device_of_each_kind_opens(self):
        opened = {s["kind"]: s for s in self.plan["steps"] if s["group"] == "D"}
        self.assertEqual(opened["pump"]["device"], "P-1")          # document order: P-1 before SupplyPump_No2
        self.assertEqual(opened["pump"]["expect"], {"title": "P-1", "label": "Supply pump 1",
                                                    "tabs": ["Control", "Alarms", "Maintenance"]})
        self.assertEqual(opened["controller"]["expect"]["tabs"], ["Control", "Trend", "Tuning", "Alarms"])
        self.assertEqual(opened["indicator"]["expect"]["tabs"], ["Status", "Maintenance", "Alarms"])
        self.assertEqual(opened["instrument"]["device"], "SupplyFlow_FT01")   # a readout is the kind `instrument`
        self.assertEqual(opened["valve"]["find"], "XV-1")
        self.assertEqual(opened["sequence"]["device"], "FLT-1")
        self.assertEqual(opened["sequence"]["expect"], {"title": "FLT-1", "label": "Self cleaning filter",
                                                        "tabs": ["Status", "Trend", "Alarms"]})
        self.assertFalse([n for n in self.plan["notReached"] if "device" in n])

    def test_capabilities_by_write_path(self):
        caps = capabilities(self.plan)
        want = {("pump", "W1", "SupplyPump_No2", "cmd"),               # P-1 has no command: the first pump that has one
                ("pump", "W16", "P-1", "force"), ("pump", "W17", "P-1", "mnt/errorMask"),
                ("valve", "W16", "XV-1", "force"), ("valve", "W17", "XV-1", "mnt/errorMask"),
                ("controller", "W12", "PIC-1", "sp"), ("controller", "W13", "PIC-1", "manual"),
                ("controller", "W14", "PIC-1", "manOut"), ("controller", "W15", "PIC-1", "gain"),
                ("controller", "W15", "PIC-1", "ti"), ("controller", "W15", "PIC-1", "td"),
                ("indicator", "W16", "SuctionLowLvl_SW", "force"),
                ("sequence", "W18", "FLT-1", "trigger")}
        self.assertEqual(want, caps)
        # a member the device model marks read, or leaves out, gives no step
        self.assertFalse({c for c in caps if c[1] in ("W5", "W2", "W3", "W4", "W10")})
        self.assertNotIn(("valve", "W1", "XV-1", "cmd"), caps)

    def test_both_force_encodings(self):
        steps = {s["device"]: s for s in self.plan["steps"] if s["group"] == "C" and s["path"] == "W16"}
        pair = {s["value"]: s["tags"] for s in steps["P-1"]["states"]}
        self.assertEqual(pair["on"], {"[default]cadre_hmi_pilot/P1/mnt/forceOn": True,
                                      "[default]cadre_hmi_pilot/P1/mnt/forceOff": False})
        self.assertEqual(pair["auto"], {"[default]cadre_hmi_pilot/P1/mnt/forceOn": False,
                                        "[default]cadre_hmi_pilot/P1/mnt/forceOff": False})
        mode = {s["value"]: s["tags"] for s in steps["XV-1"]["states"]}
        self.assertEqual(mode["off"], {"[default]cadre_hmi_pilot/XV1/mnt/forceMode": True,
                                       "[default]cadre_hmi_pilot/XV1/mnt/forceValue": False})
        self.assertEqual(mode["auto"], {"[default]cadre_hmi_pilot/XV1/mnt/forceMode": False})
        auto = next(s for s in steps["P-1"]["states"] if s["value"] == "auto")
        self.assertEqual((auto["button"], auto["sibling"]), ("Automatic", "Force on"))

    def test_the_manual_output_needs_manual(self):
        step = next(s for s in self.plan["steps"] if s["group"] == "C" and s["path"] == "W14")
        self.assertEqual(step["requires"]["tag"], "[default]cadre_hmi_pilot/PIC1/manual")
        self.assertEqual((step["requires"]["set"]["button"], step["requires"]["back"]["button"]), ("Manual", "Auto"))
        self.assertEqual(step["bounds"], [0, 100])
        self.assertEqual(step["delta"], 10.0)

    def test_a_step_never_writes_the_value_held(self):
        w = walk.Walk.__new__(walk.Walk)
        for s in (x for x in self.plan["steps"] if x.get("type") == "entry"):
            self.assertGreater(s["delta"], 0, s["id"])
            for current in (0.0, 1.5, 50.0, 100.0, 20000.0):
                lo, hi = s["bounds"]
                if (lo is not None and current < lo) or (hi is not None and current > hi):
                    continue
                target = walk.Walk.target_of(w, s, current)
                self.assertNotEqual(target, current, (s["id"], current))
                self.assertTrue(lo is None or target >= lo, (s["id"], current, target))
                self.assertTrue(hi is None or target <= hi, (s["id"], current, target))
        for s in (x for x in self.plan["steps"] if x.get("type") == "states"):
            self.assertGreaterEqual(len(s["states"]), 2, s["id"])
            self.assertEqual(len({json.dumps(st["tags"], sort_keys=True) for st in s["states"]}), len(s["states"]), s["id"])

    def test_refusals_mirror_capabilities(self):
        caps = {s["id"]: s for s in self.plan["steps"] if s["group"] == "C"}
        refusals = {s["mirrors"]: s for s in self.plan["steps"] if s["group"] == "R"}
        self.assertEqual(set(caps), set(refusals))
        for cid, c in caps.items():
            r = refusals[cid]
            self.assertEqual((r["path"], r["device"], r["tab"], r["session"]), (c["path"], c["device"], c["tab"], "anonymous"))
            self.assertEqual(r["id"], "R-" + cid[2:])
            if c["type"] == "entry":
                self.assertEqual((r["field"], r["tag"], r["symbols"]), (c["field"], c["tag"], c["symbols"]))
            elif c["type"] == "pulse":
                self.assertEqual([x["button"] for x in r["controls"]], [c["button"]])
            else:
                self.assertEqual([x["button"] for x in r["controls"]], [st["button"] for st in c["states"]])
        self.assertTrue(all(s["session"] == "signed" for s in caps.values()))

    def test_the_manual_outputs_refusal_runs_while_the_loop_is_in_manual(self):
        # in automatic the field is shut for every user, so a refusal there would prove the mode, not the role
        c = next(s for s in self.plan["steps"] if s["group"] == "C" and s["path"] == "W14")
        r = next(s for s in self.plan["steps"] if s.get("mirrors") == c["id"])
        self.assertEqual(r["during"], c["id"])
        self.assertEqual((r["requires"]["tag"], r["requires"]["value"]), (c["requires"]["tag"], True))
        others = [s for s in self.plan["steps"] if s["group"] == "R" and s["path"] != "W14"]
        self.assertFalse([s["id"] for s in others if s.get("during") or s.get("requires")])

    def test_the_pulse_of_a_sequence(self):
        c = next(s for s in self.plan["steps"] if s["group"] == "C" and s["path"] == "W18")
        self.assertEqual((c["type"], c["device"], c["tab"], c["button"], c["row"]),
                         ("pulse", "FLT-1", "Status", "Start cycle", "Step"))   # the device model's caption
        self.assertEqual(c["tag"], "[default]cadre_hmi_pilot/SQ1/trigger")
        self.assertEqual(c["effects"], [])   # without an effects file: the member itself must be read true
        r = next(s for s in self.plan["steps"] if s.get("mirrors") == c["id"])
        self.assertEqual((r["session"], r["path"], r["row"]), ("anonymous", "W18", "Step"))
        self.assertEqual(r["controls"], [{"button": "Start cycle", "sibling": None}])
        self.assertEqual(r["rest"], [{"symbol": "SQ1", "find": "FLT-1"}])
        with_effects = pilot_plan_with_effects()
        c = next(s for s in with_effects["steps"] if s["group"] == "C" and s["path"] == "W18")
        self.assertEqual([(e["member"], bool(e.get("changes")), bool(e.get("leaves"))) for e in c["effects"]],
                         [("SQ1/started", True, False), ("SQ1/stepText", False, True)])
        self.assertEqual(c["effects"][0]["tag"], "[default]cadre_hmi_pilot/SQ1/started")
        self.assertEqual((c["effects"][1]["symbol"], c["effects"][1]["returnsWithin"]), ("SQ1", 20))
        r = next(s for s in with_effects["steps"] if s.get("mirrors") == c["id"])
        self.assertEqual(r["watch"], ["[default]cadre_hmi_pilot/SQ1/started"])   # a pulse returned leaves its own tag false
        self.assertEqual(with_effects["effectsUnseen"], [])
        self.assertNotIn("W18", [n.get("path") for n in with_effects["notReached"]])

    def test_the_fixtures_effects_file(self):
        effects = load(FIXTURES / "pilot-walk-effects.json")
        self.assertEqual(walk.effects_errors(effects), [])
        plan = pilot_plan_with_effects()
        scene = next(s for s in plan["steps"] if s["group"] == "A")
        self.assertEqual((scene["by"], scene["device"], scene["ack"], scene["tag"]),
                         ("scene", "XV-1", "W7", "[default]cadre_hmi_pilot/src/XV1_OE"))
        tags = load(FIXTURES / "pilot-tags.json")
        src = next(t for t in tags["tags"] if t["name"] == "src")
        oe = next(t for t in src["tags"] if t["name"] == "XV1_OE")
        self.assertEqual(scene["clear"], oe)                       # the clear document is the fixture's own definition
        self.assertEqual(scene["raise"], {**oe, "value": True})
        self.assertEqual(plan["counts"], {"N": 3, "D": 6, "T": 4, "C": 13, "R": 13, "A": 1, "P": 2})
        bad = copy.deepcopy(effects)
        bad["alarmScenes"][0]["raise"]["name"] = "Other"
        bad["effects"].append({"device": "SQ1", "path": "W18", "expect": [{"member": "SQ1/step", "returnsWithin": 5}]})
        self.assertEqual(len(walk.effects_errors(bad)), 3)

    def test_trends(self):
        page = next(s for s in self.plan["steps"] if s.get("type") == "trend-page")
        cards = [(c["title"], c["member"]) for c in page["cards"]]
        for want in (("SupplyFlow_FT01", "value"), ("PIC-1", "value"), ("PIC-1", "sp"), ("PIC-1", "out"), ("FLT-1", "step")):
            self.assertIn(want, cards)
        tabs = {s["device"]: s["series"] for s in self.plan["steps"] if s.get("type") == "trend-tab"}
        self.assertEqual(tabs["FLT-1"], ["step"])
        self.assertEqual(tabs["PIC-1"], ["value", "sp", "out"])
        self.assertEqual(tabs["SupplyFlow_FT01"], ["value"])
        order = [s["group"] for s in self.plan["steps"]]
        self.assertLess(max(i for i, g in enumerate(order) if g == "T"), min(i for i, g in enumerate(order) if g == "C"),
                        "the trends are read before the walk writes a sample of its own")

    def test_parity_entries(self):
        parity = self.plan["parity"]
        self.assertEqual({t["tag"] for t in parity["tags"]},
                         {"[default]cadre_hmi_pilot/PIC1/sp", "[default]cadre_hmi_pilot/PIC1/manual"})
        scenes = [s for s in self.plan["steps"] if s["group"] == "P"]
        self.assertEqual([s["scene"] for s in scenes], [1, 2])
        first = {(r["symbol"], r["param"]): r for r in scenes[0]["readings"]}
        self.assertEqual(set(first), {("PIC1", "setpoint"), ("PIC1", "manual"), ("PIC1_PV", "setpoint")})
        sp = scenes[0]["set"]["[default]cadre_hmi_pilot/PIC1/sp"]
        self.assertEqual(first[("PIC1", "setpoint")]["expect"], {"line": "▸ " + walk.number_format(sp, "0.0")})
        self.assertEqual(first[("PIC1_PV", "setpoint")]["find"], "Header kPa")
        self.assertEqual(first[("PIC1", "manual")]["expect"], {"icon": "manual"})   # configured false: true first
        second = {(r["symbol"], r["param"]): r for r in scenes[1]["readings"]}
        self.assertEqual(second[("PIC1", "manual")]["expect"], {"icon": "auto"})
        for key in first:
            self.assertNotEqual(first[key]["expect"], second[key]["expect"], key)

    def test_what_parity_does_not_check_and_why(self):
        why = {(n["symbol"], n["param"]): n["why"] for n in self.plan["parity"]["notChecked"]}
        self.assertIn("expression tag", why[("P1", "on")])
        self.assertIn("expression tag", why[("FT1", "value")])
        self.assertIn("carries an alarm", why[("P1", "alert")])       # a reference to a memory tag with an alarm
        self.assertIn("carries an alarm", why[("XV1", "alert")])
        self.assertIn("expression tag", why[("PIC1", "output")])
        self.assertIn("expression tag", why[("SQ1", "text")])
        self.assertIn("expression tag", why[("SQ1", "step")])
        checked = {(r["symbol"], r["param"]) for s in self.plan["steps"] if s["group"] == "P" for r in s["readings"]}
        self.assertFalse(checked & set(why))
        bound = sum(len(s.get("bind", {})) for s in load(FIXTURES / "pilot-supply.json")["symbols"])
        self.assertEqual(len(checked) + len(why), bound, "every bound parameter is checked or accounted for")

    def test_a_reference_is_followed_to_the_source_given(self):
        nodes = walk.tag_nodes(load(FIXTURES / "pilot-tags.json"))
        r = walk.resolve("[default]cadre_hmi_pilot/P1/fault", nodes)
        self.assertEqual((r["kind"], r["end"]), ("memory", "[default]cadre_hmi_pilot/src/P1_OE"))
        without = {k: v for k, v in nodes.items() if "/src/" not in k}
        self.assertEqual(walk.resolve("[default]cadre_hmi_pilot/P1/fault", without)["kind"], "unknown")
        src = {"name": "src", "tagType": "Folder", "tags": [
            {"name": "P1_OE", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Boolean", "value": False}]}
        given = {**without, **walk.tag_nodes(src, "cadre_hmi_pilot")}   # as `--source-tags file@cadre_hmi_pilot`
        self.assertEqual(walk.resolve("[default]cadre_hmi_pilot/P1/fault", given)["kind"], "memory")
        self.assertEqual(walk.resolve("[default]cadre_hmi_pilot/P1/state", nodes)["kind"], "expr")
        self.assertEqual(walk.resolve("[default]cadre_hmi_pilot/none", nodes)["kind"], "missing")

    def test_write_paths_not_reached_have_reasons(self):
        reached = {s["path"] for s in self.plan["steps"] if s["group"] == "C"}
        profile = walk.load_profile()
        missing = {n["path"]: n["why"] for n in self.plan["notReached"] if "path" in n}
        self.assertEqual(reached | set(missing), set(profile["writePaths"]))
        self.assertFalse(reached & set(missing))
        self.assertTrue(all(len(w) > 20 for w in missing.values()))
        self.assertIn("W11", missing)
        self.assertIn("W6", missing)

    def test_an_alarm_scene_of_the_effects_file(self):
        tags = load(FIXTURES / "pilot-tags.json")
        src = next(t for t in tags["tags"] if t["name"] == "src")
        oe = next(t for t in src["tags"] if t["name"] == "XV1_OE")
        effects = {"schema": walk.EFFECTS_SCHEMA, "tagRoot": "[default]cadre_hmi_pilot",
                   "effects": [{"device": "P2", "path": "W1", "value": True, "within": 6,
                                "expect": [{"member": "P2/state", "value": True}, {"member": "FT1/value", "value": 25.0},
                                           {"member": "P2/none", "value": 1}]}],
                   "alarmScenes": [{"device": "XV1", "member": "fault", "tag": "[default]cadre_hmi_pilot/src/XV1_OE",
                                    "text": "XV-1 Object error", "raise": {**oe, "value": True}, "clear": {**oe, "value": False}}]}
        self.assertEqual(walk.effects_errors(effects), [])
        plan = pilot_plan(effects=effects)
        scene = next(s for s in plan["steps"] if s["group"] == "A")
        self.assertEqual((scene["by"], scene["device"], scene["ack"]), ("scene", "XV-1", "W7"))
        self.assertEqual([(r["symbol"], r["param"], r["rule"]["how"]) for r in scene["symbols"]], [("XV1", "alert", "frame")])
        self.assertEqual(scene["raise"]["value"], True)
        start = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W1")
        on = next(st for st in start["states"] if st["value"] is True)
        self.assertEqual([(e["symbol"], e["param"]) for e in on["effects"]], [("P2", "on"), ("FT1", "value")])
        self.assertEqual(walk.expect_of(on["effects"][1]["rule"], 25.0), {"line": "25.0 L/s"})
        self.assertEqual(plan["effectsUnseen"], [{"device": "SupplyPump_No2", "path": "W1", "member": "P2/none"}])
        self.assertTrue(walk.effects_errors({"schema": "other", "effects": [{"device": "P2"}]}))

    def test_the_plan_is_deterministic(self):
        self.assertEqual(walk.plan_text(pilot_plan()), walk.plan_text(pilot_plan()))
        self.assertEqual(walk.plan_text(self.plan).encode("utf-8"), walk.plan_text(pilot_plan()).encode("utf-8"))
        self.assertEqual(walk.plan_text(pilot_plan_with_effects()), walk.plan_text(pilot_plan_with_effects()))


class FaceplateStylePlanTests(unittest.TestCase):
    """The plan of a project whose faceplates are in the `asm` style (COBD-045): a step of a pump or a
    valve names the tab that style shows; a kind without an `asm` faceplate keeps its tabs."""

    def tabs(self, plan):
        return {(s["device"], s["tab"]) for s in plan["steps"] if s.get("tab")}

    def test_the_asm_style_renames_the_tabs_of_pumps_and_valves(self):
        ob, asm = pilot_plan(), pilot_plan(faceplate="asm")
        self.assertEqual({d["title"]: d["style"] for d in asm["devices"]}["XV-1"], "asm")
        self.assertEqual({d["title"]: d["style"] for d in ob["devices"]}["XV-1"], "openbridge")
        rename = {("P-1", "Maintenance"): ("P-1", "Config"), ("XV-1", "Maintenance"): ("XV-1", "Config"),
                  ("SupplyPump_No2", "Control"): ("SupplyPump_No2", "Home"),
                  ("FLT-1", "Status"): ("FLT-1", "Home")}   # a sequence has an asm faceplate since COB-158
        self.assertEqual(self.tabs(asm), {rename.get(t, t) for t in self.tabs(ob)})
        self.assertIn(("SuctionLowLvl_SW", "Maintenance"), self.tabs(asm))   # an indicator has no asm faceplate
        opened = {s["device"]: s["expect"]["tabs"] for s in asm["steps"] if s.get("type") == "open"}
        self.assertEqual((opened["P-1"], opened["SuctionLowLvl_SW"]),
                         (["Home", "Config", "Diagnostics", "Alarms", "Info"], ["Status", "Maintenance", "Alarms"]))
        model = load(FIXTURES / "pilot-devices.json")       # a device's own style wins over the project's
        next(d for d in model["devices"] if d["id"] == "XV1")["faceplate"] = "openbridge"
        own = walk.build_plan([load(FIXTURES / "pilot-supply.json")], devices=model,
                              tags=load(FIXTURES / "pilot-tags.json"), faceplate="asm")
        self.assertIn(("XV-1", "Maintenance"), self.tabs(own))


class TopBarPathTests(unittest.TestCase):
    """The glass finds the top bar's alarm button by its component path, and the path follows the order in which
    `framework.top_bar` lays out the root's children (spike T0, 2026-11-03: the alert message moved the button
    from index 5 to 6 and G10 pressed the message instead, so the alarm menu never opened)."""

    def test_the_bell_path_is_the_alarm_button_of_the_generated_top_bar(self):
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import glass
        from hmi import framework
        names = [c["meta"]["name"] for c in framework.top_bar()["root"]["children"]]
        self.assertEqual(glass.BELL, f'[data-component-path="T[0].0:{names.index("AlertButton")}"]')


class ConfirmedPressTests(unittest.TestCase):
    """The glass presses a confirmed command as an operator does (F029, COBD-045): a question still open
    is cancelled, the button pressed, the Confirm it raises answered; an entry is typed, then Set."""

    class Button:
        def __init__(self, dock, text, shown=True, on_click=None):
            self.dock, self.text, self.shown, self.on_click = dock, text, shown, on_click

        def is_visible(self):
            return self.shown

        def is_enabled(self):
            return True

        def click(self, *a, **k):
            self.dock.pressed.append(self.text)
            if self.on_click:
                self.on_click()

    class Found:
        def __init__(self, items):
            self.items = items

        def count(self):
            return len(self.items)

        def nth(self, k):
            return self.items[k]

        @property
        def first(self):
            return self.items[0]

    class Dock:
        def __init__(self):
            self.buttons, self.pressed = [], []

        def locator(self, selector, has_text=None):
            return ConfirmedPressTests.Found([b for b in self.buttons if has_text is None or has_text.search(b.text)])

    class Page:
        def __init__(self, dock):
            self.dock = dock

        def locator(self, selector):
            return self.dock

        def wait_for_timeout(self, ms):
            pass

    def setUp(self):
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import glass
        self.glass = glass
        self.dock = self.Dock()
        self.page = self.Page(self.dock)
        self.dock.page = self.page

    def ask(self):   # the faceplate raises its question
        for b in self.dock.buttons:
            if b.text in ("Confirm", "Cancel"):
                b.shown = True

    def test_a_command_is_pressed_then_confirmed(self):
        g, B = self.glass, self.Button
        self.dock.buttons = [B(self.dock, "Start", on_click=self.ask), B(self.dock, "Confirm", shown=False),
                             B(self.dock, "Cancel", shown=False)]
        g.button(self.dock, "Start").click()
        self.assertEqual(self.dock.pressed, ["Start", "Confirm"])
        self.dock.pressed.clear()                     # a question left open is cancelled, never answered for this one
        g.Confirmed(self.dock.buttons[0], self.page).click()
        self.assertEqual(self.dock.pressed, ["Cancel", "Start", "Confirm"])

    def test_a_button_of_the_page_itself_is_pressed_on_that_page(self):
        """`functional.frame_steps` finds the toolbar's toggles on the page, which has no `page` attribute (the
        G10 stop of spike T0, 2026-11-03): the press is made on the page and a toggle that asks nothing is
        pressed once."""
        g, B = self.glass, self.Button

        class PageScope(self.Page):
            def locator(self, selector, has_text=None):   # the page's buttons, or (no caption) its dock
                return self.dock if has_text is None else self.dock.locator(selector, has_text=has_text)

        page = PageScope(self.dock)
        self.dock.page = page
        self.dock.buttons = [B(self.dock, "Readout"), B(self.dock, "Confirm", shown=False)]
        press = g.button(page, "Readout")
        self.assertIs(press._page, page)
        press.click()
        self.assertEqual(self.dock.pressed, ["Readout"])

    def test_a_press_that_asks_nothing_and_an_entry(self):
        g, B = self.glass, self.Button
        self.dock.buttons = [B(self.dock, "Start"), B(self.dock, "Confirm", shown=False)]
        g.button(self.dock, "Start").click()          # an interlock holds the start: no question, no answer
        self.assertEqual(self.dock.pressed, ["Start"])

        class Field:
            page = self.page
            def click(self): pass
            def fill(self, v): self.v = v
            def press(self, key): self.key = key
        self.dock.buttons = [B(self.dock, "Set")]
        f = Field()
        g.type_into(f, 42)
        self.assertEqual((f.v, f.key, self.dock.pressed[-1]), ("42", "Enter", "Set"))


class ParityPlanTests(unittest.TestCase):
    """A reading the glass could not tell apart is not a check: the plan lists it as not checked."""

    def plan(self, tags: dict) -> dict:
        desc = {"schema": "cadre-hmi-screen/1", "tagRoot": "[default]cadre_hmi_t", "showTags": True,
                "screen": {"route": "/a", "view": "Pages/A", "title": "A"},
                "symbols": [{"id": "R1", "kind": "readout", "x": 40, "y": 40, "label": "One",
                             "params": {"tag": "FT-1", "hasTag": True, "format": "0", "unit": "m"},
                             "bind": {"value": "R1/value"}},
                            {"id": "R2", "kind": "readout", "x": 240, "y": 40, "label": "Two",
                             "params": {"tag": "FT-2", "hasTag": True, "format": "0.0", "unit": "m"},
                             "bind": {"value": "R2/value"}}]}
        return walk.build_plan([desc], tags=tags)

    def tags(self, low, high) -> dict:
        def tag(value, **more):
            return {"name": "value", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Float8", "value": value, **more}
        return {"name": "cadre_hmi_t", "tagType": "Folder", "tags": [
            {"name": "R1", "tagType": "Folder", "tags": [tag(0.2, engLow=low, engHigh=high)]},
            {"name": "R2", "tagType": "Folder", "tags": [tag(50.0, engLow=0.0, engHigh=100.0)]}]}

    def test_a_range_narrower_than_the_format_is_not_checked(self):
        # 0 to 0.4 under the pattern '0': both scenes would read alike, or below one unit of the pattern
        plan = self.plan(self.tags(0.0, 0.4))
        why = {(n["symbol"], n["param"]): n["why"] for n in plan["parity"]["notChecked"]}
        self.assertIn(("R1", "value"), why)
        self.assertEqual(plan["parity"]["checked"], 1)
        self.assertEqual([t["tag"] for t in plan["parity"]["tags"]], ["[default]cadre_hmi_t/R2/value"])
        for scene in (s for s in plan["steps"] if s["group"] == "P"):
            self.assertEqual(list(scene["set"]), ["[default]cadre_hmi_t/R2/value"])   # no tag is set for a reading dropped
        wide = self.plan(self.tags(0.0, 100.0))
        self.assertEqual(wide["parity"]["checked"], 2)

    def test_every_reading_differs_between_its_scenes(self):
        for plan in (self.plan(self.tags(0.0, 100.0)), pilot_plan(),
                     walk.build_plan([load(ROOT / "screens" / "sample-pump-station.json")])):
            scenes = [s for s in plan["steps"] if s["group"] == "P"]
            self.assertEqual(len(scenes), 2)
            for a, b in zip(scenes[0]["readings"], scenes[1]["readings"]):
                self.assertNotEqual(a["expect"], b["expect"], a["id"])


class WtpPlanTests(unittest.TestCase):
    """The plan on the water treatment sample: four descriptors, a tag model, no device model."""

    @classmethod
    def setUpClass(cls):
        cls.plan = wtp_plan()

    def test_a_menu_step_never_begins_on_its_own_route(self):
        steps = [s for s in self.plan["steps"] if s["group"] == "N" and s["via"] == "menu"]
        self.assertEqual(steps[0]["route"], "/")
        self.assertEqual(steps[0]["from"], "/intake")   # a session signs in on "/": the first step leaves it first
        self.assertEqual((steps[0]["title"], steps[0]["symbol"]), ("Plant Overview", "Raw water m³/h"))
        self.assertTrue(all(s["from"] != s["route"] for s in steps))
        card = next(s for s in self.plan["steps"] if s["group"] == "N" and s["via"] == "card")
        self.assertEqual((card["title"], card["from"]), ("Intake and Clarification", "/"))

    def test_routes_and_cards(self):
        steps = [s for s in self.plan["steps"] if s["group"] == "N"]
        self.assertEqual([s["route"] for s in steps if s["via"] == "menu"],
                         ["/", "/intake", "/filtration", "/disinfection", "/trends", "/alerts"])
        self.assertEqual([(s["from"], s["label"], s["route"]) for s in steps if s["via"] == "card"],
                         [("/", "Production", "/intake"), ("/", "Water quality", "/disinfection")])

    def test_devices_chosen_in_document_order(self):
        opened = [(s["kind"], s["device"], s["route"]) for s in self.plan["steps"] if s["group"] == "D"]
        self.assertEqual(opened, [("instrument", "FIT-101", "/"), ("tank", "TK-101", "/"), ("pump", "P-101", "/"),
                                  ("valve", "XV-101", "/intake"), ("motor", "M-201", "/intake")])
        tabs = {s["device"]: s["expect"]["tabs"] for s in self.plan["steps"] if s["group"] == "D"}
        self.assertEqual(tabs["P-101"], ["Control", "Alarms", "Interlocks"])   # its folder carries `ilk`
        self.assertEqual(tabs["M-201"], ["Control", "Alarms"])
        self.assertEqual(tabs["TK-101"], ["Values", "Trend", "Alarms"])
        field = next(s for s in self.plan["steps"] if s["group"] == "D" and s["device"] == "FIT-101")
        self.assertEqual(field["find"], "Raw water m³/h")   # an instrument field shows its label and unit

    def test_capabilities_by_write_path(self):
        caps = capabilities(self.plan)
        self.assertEqual(caps, {
            ("instrument", "W4", "AIT-301", "hiLimit"), ("instrument", "W4", "AIT-401", "loLimit"),
            ("tank", "W4", "TK-101", "hiLimit"), ("tank", "W4", "TK-101", "loLimit"),
            ("pump", "W1", "P-101", "cmd"), ("pump", "W2", "P-101", "mode"), ("pump", "W3", "P-101", "speedSp"),
            ("pump", "W5", "P-101", "fault"), ("pump", "W10", "P-101", "ilk/C01/bypassed"),
            ("valve", "W1", "XV-301", "cmd"),          # the effects file chooses a valve in manual
            ("valve", "W2", "XV-101", "mode"),
            ("motor", "W1", "M-201", "cmd"), ("motor", "W2", "M-201", "mode"), ("motor", "W3", "M-201", "speedSp"),
            ("motor", "W5", "M-201", "fault")})
        plain = capabilities(wtp_plan(effects=False))
        self.assertIn(("valve", "W1", "XV-101", "cmd"), plain)   # without the choice: the first valve

    def test_the_fault_reset_holds_its_refusal(self):
        reset = next(s for s in self.plan["steps"] if s["group"] == "C" and s["path"] == "W5" and s["kind"] == "pump")
        self.assertEqual((reset["type"], reset["device"], reset["alarm"]), ("fault-reset", "P-101", True))
        refusal = next(s for s in self.plan["steps"] if s.get("mirrors") == reset["id"])
        self.assertEqual(refusal["during"], reset["id"])
        # P-502 starts faulted: the step takes a pump that is not, so that it leaves no fault behind
        self.assertNotEqual(reset["device"], "P-502")

    def test_effects_are_resolved_to_symbols_of_the_page(self):
        stop = next(s for s in self.plan["steps"] if s["group"] == "C" and s["path"] == "W1" and s["device"] == "P-101")
        off = next(st for st in stop["states"] if st["value"] is False)
        self.assertEqual([(e["symbol"], e["param"]) for e in off["effects"]], [("C_P101", "on"), ("F_FIT101", "value")])
        self.assertEqual(walk.expect_of(off["effects"][0]["rule"], False), {"line": "Off"})
        self.assertEqual(walk.expect_of(off["effects"][1]["rule"], 0), {"line": "0.0"})
        speed = next(s for s in self.plan["steps"] if s["group"] == "C" and s["path"] == "W3" and s["device"] == "P-101")
        self.assertEqual(walk.expect_of(speed["effects"][0]["rule"], 70.0), {"line": "70 %"})
        self.assertEqual(self.plan["effectsUnseen"], [])
        module = wtp_plan(render="module")
        stop = next(s for s in module["steps"] if s["group"] == "C" and s["path"] == "W1" and s["device"] == "P-101")
        off = next(st for st in stop["states"] if st["value"] is False)
        self.assertEqual(off["effects"][0]["rule"], {"how": "module", "prop": "on"})

    def test_alarms_from_limits(self):
        alarms = [(s["device"], s["member"], s["above"], s["ack"]) for s in self.plan["steps"] if s["group"] == "A"]
        self.assertEqual(alarms, [("AIT-301", "hiLimit", True, "W7"), ("TK-101", "hiLimit", True, "W7")])
        module = [s["ack"] for s in wtp_plan(render="module")["steps"] if s["group"] == "A"]
        self.assertEqual(module, ["W8", "W8"])

    def test_parity_has_nothing_it_can_set(self):
        parity = self.plan["parity"]
        self.assertEqual(parity["checked"], 0)
        self.assertEqual(self.plan["counts"]["P"], 0)
        self.assertEqual({n["why"] for n in parity["notChecked"]}, {walk.NOT_SETTABLE["expr"]})
        descs = [load(WTP / f"{n}.json") for n in ("overview", "intake", "filtration", "disinfection")]
        gen = walk._generator()
        bound = sum(len(s.get("bind", {})) for d in descs for s in gen.descriptor_items(d))
        self.assertEqual(len(parity["notChecked"]), bound)

    def test_write_paths_not_reached(self):
        missing = {n["path"]: n["why"] for n in self.plan["notReached"] if "path" in n}
        reached = {s["path"] for s in self.plan["steps"] if s["group"] == "C"} | {s["ack"] for s in self.plan["steps"] if s["group"] == "A"}
        self.assertEqual(reached & set(missing), set())
        for path in ("W6", "W8", "W9", "W11", "W12", "W16", "W17"):
            self.assertIn(path, missing)
        self.assertEqual(reached & {f"W{n}" for n in range(1, 12)}, {"W1", "W2", "W3", "W4", "W5", "W7", "W10"})

    def test_the_plan_is_deterministic(self):
        self.assertEqual(walk.plan_text(self.plan), walk.plan_text(wtp_plan()))
        self.assertEqual(walk.plan_text(wtp_plan(render="module")), walk.plan_text(wtp_plan(render="module")))

    def test_the_effects_file_is_valid(self):
        self.assertEqual(walk.effects_errors(load(WTP / "walk-effects.json")), [])


class FakeGateway:
    """The two tag routes of `hmi.deploy`, over a tag document held in memory (GF-25: a path the
    gateway does not carry exports as `tagType` Unknown; GF-55: an import replaces a listed tag whole)."""

    def __init__(self, doc: dict):
        self.nodes = {k: copy.deepcopy(v) for k, v in walk.tag_nodes(doc).items()}
        self.imports: list[tuple[str, str]] = []
        self.fail_export = self.fail_import = self.drop_import = False

    def export_tags(self, provider: str, path: str) -> dict:
        if self.fail_export:
            raise RuntimeError("tags/export HTTP 500")
        node = self.nodes.get(path)
        return copy.deepcopy(node) if node else {"name": path.split("/")[-1], "tagType": "Unknown"}

    def import_tags(self, provider: str, path: str, doc: dict) -> dict:
        if self.fail_import:
            return {"successCount": 0, "failureCount": 1, "failures": ["Bad"]}
        found = walk.tag_nodes(doc, path)
        for k, v in found.items():
            self.imports.append((provider, k))
            if not self.drop_import:
                self.nodes[k] = copy.deepcopy(v)
        return {"successCount": len(found), "failureCount": 0, "failures": []}


class TagsTests(unittest.TestCase):
    """The REST side of the runner against a gateway held in memory."""

    def setUp(self):
        self.gw = FakeGateway(load(FIXTURES / "pilot-tags.json"))
        self.tags = walk.Tags(["[default]cadre_hmi_pilot"], deploy=self.gw)

    def test_a_reference_is_followed_and_an_expression_gives_no_value(self):
        self.assertEqual(self.tags.value("[default]cadre_hmi_pilot/XV1/fault"), (True, False))
        self.assertEqual(self.tags.source("[default]cadre_hmi_pilot/XV1/fault")[0], "[default]cadre_hmi_pilot/src/XV1_OE")
        self.assertEqual(self.tags.value("[default]cadre_hmi_pilot/P1/state"), (False, None))
        self.assertEqual(self.tags.value("[default]cadre_hmi_pilot/none"), (False, None))
        self.assertEqual(self.tags.errors, [])   # a tag the gateway does not carry is no error

    def test_a_read_the_gateway_fails_is_kept_as_an_error(self):
        self.gw.fail_export = True
        self.assertEqual(self.tags.value("[default]cadre_hmi_pilot/PIC1/sp"), (False, None))
        self.assertEqual(len(self.tags.errors), 1)
        self.assertIn("HTTP 500", self.tags.errors[0]["error"])

    def test_a_scene_is_set_and_restored_and_the_restore_is_read_back(self):
        sp = "[default]cadre_hmi_pilot/PIC1/sp"
        reply = self.tags.set({sp: 46.444})
        self.assertEqual((reply["imported"], reply["missing"], reply["failed"]), (1, [], []))
        self.assertEqual(self.tags.value(sp), (True, 46.444))
        self.assertEqual(self.tags.restore(), [sp])
        self.assertEqual(self.tags.value(sp), (True, 50.0))
        self.assertEqual((self.tags.before, self.tags.unrestored), ({}, []))

    def test_a_restore_that_does_not_hold_is_reported_and_kept(self):
        sp = "[default]cadre_hmi_pilot/PIC1/sp"
        self.tags.set({sp: 46.444})
        self.gw.drop_import = True            # the gateway counts the import and keeps the scene's value
        self.assertEqual(self.tags.restore(), [])
        self.assertEqual([u["tag"] for u in self.tags.unrestored], [sp])
        self.assertIn("value", self.tags.unrestored[0]["why"])
        self.assertIn(sp, self.tags.before)   # kept, so a later restore tries again
        self.gw.drop_import = False
        self.assertEqual(self.tags.restore(), [sp])
        self.assertEqual(self.tags.unrestored, [])
        self.tags.set({sp: 46.444})
        self.gw.fail_import = True
        self.assertEqual(self.tags.restore(), [])
        self.assertIn("1 failures", self.tags.unrestored[0]["why"])

    def test_an_import_outside_the_plans_folder_is_refused(self):
        other = walk.Tags(["[default]cadre_hmi_wtp"], deploy=self.gw)
        with self.assertRaises(walk.TagFolderRefused):
            other.set({"[default]cadre_hmi_pilot/PIC1/sp": 1.0})
        with self.assertRaises(walk.TagFolderRefused):
            other.put("[default]cadre_hmi_pilot/src/XV1_OE", {"name": "XV1_OE", "value": True})
        with self.assertRaises(walk.TagFolderRefused):   # a prefix of the folder's name is not the folder
            walk.Tags(["[default]cadre_hmi_pil"], deploy=self.gw).set({"[default]cadre_hmi_pilot/PIC1/sp": 1.0})
        with self.assertRaises(walk.TagFolderRefused):   # no folder allowed, nothing imported
            walk.Tags([], deploy=self.gw).set({"[default]cadre_hmi_pilot/PIC1/sp": 1.0})
        with self.assertRaises(walk.TagFolderRefused):   # a document that would be imported beside the tag
            self.tags.put("[default]cadre_hmi_pilot/src/XV1_OE", {"name": "Other", "value": True})
        self.assertEqual(self.gw.imports, [])

    def test_a_reference_that_leads_outside_is_refused(self):
        self.gw.nodes["cadre_hmi_pilot/PIC1/sp"] = {"name": "sp", "valueSource": "reference", "dataType": "Float8",
                                                    "sourceTagPath": "[default]elsewhere/sp"}
        self.gw.nodes["elsewhere/sp"] = {"name": "sp", "valueSource": "memory", "dataType": "Float8", "value": 1.0}
        with self.assertRaises(walk.TagFolderRefused):
            self.tags.set({"[default]cadre_hmi_pilot/PIC1/sp": 2.0})
        self.assertEqual(self.gw.imports, [])

    def test_integers_are_compared_exactly(self):
        # two stamps in milliseconds ten minutes apart: a relative tolerance took them for one value,
        # and a pulse that stamped its helper anew read as no change (the final pilot walk, 2026-10-11)
        self.assertFalse(walk.same(1791674809802, 1791675409802))
        self.assertTrue(walk.same(1791674809802, 1791674809802))
        self.assertFalse(walk.same(2, 3))
        self.assertTrue(walk.same(50.0, 50.00000001))        # a Float4 read back
        self.assertTrue(walk.same(50, 50.0))
        self.assertFalse(walk.same(True, 1))
        self.assertFalse(walk.same(0, False))

    def test_an_import_reply_is_judged(self):
        self.assertEqual(walk.import_failed({"successCount": 3, "failureCount": 0, "failures": []}), "")
        self.assertTrue(walk.import_failed({"successCount": 2, "failureCount": 1, "failures": ["x"]}))
        self.assertTrue(walk.import_failed({"successCount": 0, "failureCount": 0}))
        self.assertTrue(walk.import_failed(None))


class Clock:
    """A clock that runs a second at each reading, so that the runner's waits end at once."""

    def __init__(self):
        self.now = 0.0

    def time(self) -> float:
        self.now += 1.0
        return self.now

    def sleep(self, _seconds) -> None:
        pass


class StubPage:
    url = "http://gw/client/cadre_hmi_pilot/supply"

    def wait_for_timeout(self, _ms) -> None:
        pass

    def screenshot(self, path=None) -> None:
        pass


class StubButton:
    def __init__(self, glass, caption):
        self.glass, self.caption = glass, caption

    def click(self) -> None:
        self.glass.clicked.append(self.caption)
        self.glass.on_click(self.caption)


class StubGlass:
    """A faceplate as the runner sees it. By default nothing an operator does reaches anything: a field
    keeps the text typed into it (GF-56), a button's click changes nothing. A test wires what it needs."""

    def __init__(self):
        self.fields = {}            # caption -> number shown
        self.notes = {}             # caption -> the row's other label
        self.disabled = {}          # caption -> disabled
        self.clicked = []
        self.message = ""
        self.symbols = {}           # find -> lines
        self.on_type = lambda caption, value: None
        self.on_click = lambda caption: None
        self.on_crafted_entry = lambda caption, value: None
        self.on_crafted_call = lambda caption: None
        self.crafted = []
        self.base = "http://gw/client/cadre_hmi_pilot"
        self.menu = {}              # label of a menu entry -> the route it leads to
        self.cards = {}             # title of a card -> the route it leads to
        self.top_bar = ""           # the page's name in the top bar
        self.page_components = 120  # components outside the docks
        self.holds = {}             # component type -> how many the page shows outside the docks
        self.handler = "called"     # what `crafted_call` answers

    def page_faults(self, page):
        return {"overlays": 0, "badges": 0, "not_found": False, "trial": False,
                "components": 40 + self.page_components, "page_components": self.page_components}

    def clean(self, faults):
        import glass
        return glass.clean(faults)

    def page_name(self, page):
        return self.top_bar

    def close_faceplate(self, page):
        pass

    def navigate_by_menu(self, page, label):
        if label not in self.menu:
            return False
        page.url = self.base + self.menu[label]
        return True

    def click_card_title(self, page, title):
        if title not in self.cards:
            return False
        page.url = self.base + self.cards[title]
        return True

    def page_holds(self, page, component):
        return self.holds.get(component, 0)

    def refused_rows(self, page):
        return [k for k, v in self.notes.items() if v == "Refused"]

    def dock_message(self, page):
        return self.message

    def dock_text(self, page):
        return self.message

    def dock_field(self, page, caption):
        return (caption, self.disabled.get(caption, False)) if caption in self.fields else (None, None)

    def field_number(self, field):
        return self.fields.get(field)

    def type_into(self, field, text):
        self.fields[field] = float(text)
        self.on_type(field, float(text))

    def row_text(self, page, caption):
        return self.notes.get(caption, "")

    def dock_button(self, page, caption, sibling=None):
        if caption not in self.disabled:
            return None, None
        return StubButton(self, caption), self.disabled[caption]

    def crafted_entry(self, page, caption, value):
        self.crafted.append(("entry", caption, value))
        self.on_crafted_entry(caption, value)
        return True

    def crafted_press(self, page, caption, sibling=None):
        self.crafted.append(("press", caption))
        return True

    def crafted_call(self, page, caption, sibling=None):
        self.crafted.append(("call", caption))
        if self.handler == "called":
            self.on_crafted_call(caption)
        return self.handler

    def find_symbol(self, page, find):
        lines = self.symbols.get(find)
        return None if lines is None else {"lines": list(lines), "module": None, "icons": [], "frame": None}

    def tab_count(self, right):
        return 0

    # a page command button (COB-159): what the page shows outside the docks, as texts with their disabled state
    page_texts: list = []
    page_disabled: dict = {}
    question = False
    on_page_click = staticmethod(lambda caption: None)
    on_page_crafted = staticmethod(lambda caption: None)

    def page_buttons(self, page):
        return [{"text": t, "disabled": self.page_disabled.get(t, False)} for t in self.page_texts]

    def page_button(self, page, caption):
        return (True, self.page_disabled.get(caption, False)) if caption in self.page_texts else (False, None)

    def page_button_click(self, page, caption):
        if caption not in self.page_texts:
            return False
        self.clicked.append(caption)
        self.on_page_click(caption)
        return True

    def page_crafted_call(self, page, caption):
        self.crafted.append(("page call", caption))
        if self.handler == "called":
            self.on_page_crafted(caption)
        return self.handler

    def page_label_shown(self, page, text):
        return self.question

    def dock(self, page, side):
        return object()

    def tab(self, right, name):
        return True


class RunnerCase(unittest.TestCase):
    """A runner whose glass and gateway are stubs, on the fixture's plan with its effects file."""

    @classmethod
    def setUpClass(cls):
        cls.plan = pilot_plan_with_effects()

    def setUp(self):
        self.real_time = walk_run.time
        walk_run.time = Clock()   # the runner's waits read the clock of its own module
        self.gw = FakeGateway(load(FIXTURES / "pilot-tags.json"))
        self.tags = walk.Tags(["[default]cadre_hmi_pilot"], deploy=self.gw)
        self.glass = StubGlass()
        w = walk.Walk.__new__(walk.Walk)
        w.g, w.tags, w.rows, w.out = self.glass, self.tags, [], Path(".")
        w.plan = self.plan
        w.signed = StubPage()
        w.anon = StubPage()
        w.signed_in, w.module = True, False
        w.skip_write = w.no_crafted = w.force_crafted = False
        w.during, w.refused, w.restored, w.before_step = {}, {}, [], None
        w.base = "http://gw/client/cadre_hmi_pilot"
        w.open = lambda page, step, tab=None: (object(), "")
        w.goto = lambda page, route, fresh=False: None
        self.w = w

    def tearDown(self):
        walk_run.time = self.real_time

    def step(self, group: str, path: str, member: str | None = None) -> dict:
        return next(s for s in self.plan["steps"] if s["group"] == group and s.get("path") == path
                    and (member is None or s.get("member") == member or s.get("tag", "").endswith("/" + member)))

    def node(self, rel: str) -> dict:
        return self.gw.nodes["cadre_hmi_pilot/" + rel]

    def refuse(self, caption):
        self.glass.notes[caption] = "Refused"

    def pulse_glass(self):
        self.glass.disabled["Start cycle"] = False
        self.glass.symbols["FLT-1"] = ["FLT-1", "Standby", "Step 1"]
        self.glass.notes["Step"] = "1"

    def back_at_rest_after(self, reads: int, lines: list[str], find: str = "FLT-1") -> None:
        """The symbol `find` shows `lines` again once it has been read `reads` times."""
        real, n = self.glass.find_symbol, {"n": 0}

        def later(page, text):
            n["n"] += 1
            if n["n"] > reads:
                self.glass.symbols[find] = list(lines)
            return real(page, text)
        self.glass.find_symbol = later


class RunnerTests(RunnerCase):
    """The runner's rules of evidence, with a glass and a gateway that are stubs: what must fail, fails."""

    # -- the high finding: an entry step ------------------------------------------------------------
    def test_an_entry_passes_when_the_tag_follows(self):
        step = self.step("C", "W15", "gain")
        self.glass.fields["Gain"] = 1.5
        self.glass.on_type = lambda caption, value: self.node("PIC1/gain").update(value=value)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["evidence"], "control and tag")
        self.assertEqual(self.node("PIC1/gain")["value"], 1.5)   # put back

    def test_an_entry_fails_when_only_the_field_shows_the_value(self):
        # the write reaches nothing and the tag cannot be read: before the fix this row passed on the
        # field it had typed into (finding 10 of the review)
        step = self.step("C", "W15", "gain")
        self.glass.fields["Gain"] = 1.5
        self.tags.value = lambda path: (False, None)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertEqual(row["evidence"], "control")
        self.assertIn("only the field typed into", row["detail"])

    def test_an_entry_fails_when_the_tag_keeps_its_value(self):
        step = self.step("C", "W15", "gain")
        self.glass.fields["Gain"] = 1.5
        self.w.run_step(step)   # the field shows 1.35, the tag still holds 1.5
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("tag 1.5", self.w.rows[-1]["detail"])

    def test_an_entry_fails_on_a_row_that_already_reads_refused(self):
        step = self.step("C", "W15", "gain")
        self.glass.fields["Gain"] = 1.5
        self.glass.notes["Gain"] = "Refused"
        self.glass.on_type = lambda caption, value: self.node("PIC1/gain").update(value=value)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("before the step acted", row["detail"])
        self.assertEqual(row["done"], "nothing")

    def test_an_entry_is_put_back_when_the_step_breaks(self):
        step = self.step("C", "W15", "gain")
        self.glass.fields["Gain"] = 1.5
        self.glass.on_type = lambda caption, value: self.node("PIC1/gain").update(value=value)
        calls = {"n": 0}
        real = self.glass.row_text

        def breaks(page, caption):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("the page went away")
            return real(page, caption)
        self.glass.row_text = breaks
        with self.assertRaises(RuntimeError):
            self.w.entry(step)
        self.assertEqual(self.node("PIC1/gain")["value"], 1.5)   # typed back in the `finally`

    def test_a_failed_tag_read_fails_the_row(self):
        step = self.step("C", "W15", "gain")
        self.glass.fields["Gain"] = 1.5
        self.glass.on_type = lambda caption, value: self.node("PIC1/gain").update(value=value)
        real = self.gw.export_tags
        seen = {"n": 0}

        def flaky(provider, path):
            seen["n"] += 1
            if seen["n"] == 2:
                raise RuntimeError("tags/export HTTP 503")
            return real(provider, path)
        self.gw.export_tags = flaky
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("tag reads failed", row["detail"])

    # -- a refusal ------------------------------------------------------------------------------------
    def test_a_refused_entry_passes_on_the_gateways_answer_and_the_tag(self):
        step = self.step("R", "W15", "gain")
        self.glass.fields["Gain"], self.glass.disabled["Gain"] = 1.5, True
        self.glass.on_crafted_entry = lambda caption, value: self.refuse(caption)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual((row["evidence"], row["refused_by"]), ("control and tag", "the gateway"))
        self.assertEqual(row["tag"], {"cadre_hmi_pilot/PIC1/gain": [1.5, 1.5]})

    def test_a_refusal_fails_when_the_gateway_gives_no_answer(self):
        step = self.step("R", "W15", "gain")
        self.glass.fields["Gain"], self.glass.disabled["Gain"] = 1.5, True
        self.w.run_step(step)   # the crafted entry is sent and the row never reads Refused
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("nothing shows that the gateway refused", row["detail"])

    def test_a_refusal_fails_when_the_tag_changes(self):
        step = self.step("R", "W15", "gain")
        self.glass.fields["Gain"], self.glass.disabled["Gain"] = 1.5, True

        def accepted(caption, value):
            self.node("PIC1/gain")["value"] = float(value)
            self.refuse(caption)
        self.glass.on_crafted_entry = accepted
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("the tag went from 1.5", self.w.rows[-1]["detail"])

    def test_a_refusal_fails_when_only_the_control_shows_it(self):
        step = self.step("R", "W15", "gain")
        self.glass.fields["Gain"], self.glass.disabled["Gain"] = 1.5, True
        self.glass.on_crafted_entry = lambda caption, value: self.refuse(caption)
        self.tags.value = lambda path: (False, None)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("only the control operated", row["detail"])

    def test_a_refusal_fails_on_an_enabled_field(self):
        step = self.step("R", "W15", "gain")
        self.glass.fields["Gain"], self.glass.disabled["Gain"] = 1.5, False
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("enabled", self.w.rows[-1]["detail"])
        self.assertEqual(self.glass.crafted, [])   # nothing is crafted on a control that is open

    def test_the_manual_outputs_refusal_fails_while_the_loop_is_in_automatic(self):
        step = self.step("R", "W14")
        self.glass.fields["Manual output (%)"], self.glass.disabled["Manual output (%)"] = 40.0, True
        self.glass.notes["Control mode"] = "Auto"
        self.glass.on_crafted_entry = lambda caption, value: self.refuse(caption)
        self.w.refusal(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("the condition that enables the control does not hold", self.w.rows[-1]["detail"])
        self.node("PIC1/manual")["value"] = True
        self.glass.notes = {"Control mode": "Manual"}
        self.w.rows.clear()
        self.w.refused.clear()
        self.w.refusal(step)
        self.assertTrue(self.w.rows[-1]["ok"], self.w.rows[-1]["detail"])

    def test_a_button_is_refused_by_the_gateway_through_its_handler(self):
        step = self.step("R", "W1")
        self.glass.disabled.update({"Start": True, "Stop": True})

        def answer(caption):
            self.glass.message = "Refused: sign in with the Administrator role"
        self.glass.on_crafted_call = answer
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["refused_by"], "the gateway")
        self.assertEqual([c[0] for c in self.glass.crafted], ["press", "call"])

    def test_a_button_whose_handler_gets_no_answer_fails(self):
        step = self.step("R", "W1")
        self.glass.disabled.update({"Start": True, "Stop": True})
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("nothing shows that the gateway refused", self.w.rows[-1]["detail"])

    def test_a_button_whose_crafted_call_writes_fails_on_the_tag(self):
        step = self.step("R", "W1")
        self.glass.disabled.update({"Start": True, "Stop": True})

        def writes(caption):
            self.glass.message = "Refused: sign in with the Administrator role"
            self.node("P2/cmd")["value"] = not self.node("P2/cmd")["value"]
        self.glass.on_crafted_call = writes
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("tags changed", self.w.rows[-1]["detail"])

    # -- a pulse ----------------------------------------------------------------------------------------
    def test_a_pulse_passes_on_its_effects(self):
        step = self.step("C", "W18")
        self.pulse_glass()

        def cycle(caption):
            self.node("SQ1/started")["value"] = 1760000000000
            self.glass.symbols["FLT-1"] = ["FLT-1", "Drive Out", "Step 2"]
            self.glass.notes["Step"] = "2"
        self.glass.on_click = cycle
        real = self.glass.find_symbol
        reads = {"n": 0}

        def back_later(page, find):   # the block comes back to rest after a few readings
            reads["n"] += 1
            if reads["n"] > 6:
                self.glass.symbols["FLT-1"] = ["FLT-1", "Standby", "Step 1"]
            return real(page, find)
        self.glass.find_symbol = back_later
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["evidence"], "glass and tag")
        self.assertEqual(self.glass.clicked, ["Start cycle"])
        self.assertEqual(self.tags.before, {})

    def test_a_pulse_passes_when_its_helper_was_stamped_before(self):
        step = self.step("C", "W18")
        self.pulse_glass()
        self.node("SQ1/started")["value"] = 1791674809802   # the stamp of an earlier cycle

        def cycle(caption):
            self.node("SQ1/started")["value"] = 1791675409802
            self.glass.symbols["FLT-1"] = ["FLT-1", "Drive Out", "Step 2"]
        self.glass.on_click = cycle
        real = self.glass.find_symbol
        reads = {"n": 0}

        def back_later(page, find):
            reads["n"] += 1
            if reads["n"] > 6:
                self.glass.symbols["FLT-1"] = ["FLT-1", "Standby", "Step 1"]
            return real(page, find)
        self.glass.find_symbol = back_later
        self.w.run_step(step)
        self.assertTrue(self.w.rows[-1]["ok"], self.w.rows[-1]["detail"])
        self.assertEqual(self.w.rows[-1]["evidence"], "glass and tag")

    def test_a_pulse_that_arrives_nowhere_fails(self):
        step = self.step("C", "W18")
        self.pulse_glass()
        self.w.run_step(step)   # the click reaches nothing
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("no effect on SQ1/started, SQ1/stepText", row["detail"])

    def test_a_pulse_fails_when_the_block_does_not_come_back(self):
        step = self.step("C", "W18")
        self.pulse_glass()

        def stuck(caption):
            self.node("SQ1/started")["value"] = 1760000000000
            self.glass.symbols["FLT-1"] = ["FLT-1", "Drive Out", "Step 2"]
        self.glass.on_click = stuck
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("did not come back", self.w.rows[-1]["detail"])

    def test_a_pulse_without_effects_needs_the_member_read_true_and_puts_it_back(self):
        step = dict(next(s for s in pilot_plan()["steps"] if s.get("path") == "W18" and s["group"] == "C"))
        self.pulse_glass()
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("names no effect of the pulse", self.w.rows[-1]["detail"])
        self.w.rows.clear()
        self.glass.on_click = lambda caption: self.node("SQ1/trigger").update(value=True)   # nothing returns it
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["evidence"], "tag")
        self.assertIs(self.node("SQ1/trigger")["value"], False)   # the definition of before, imported back
        self.assertIn("its definition of before was imported", row["detail"])

    def test_the_flags_a_pulse_moves_are_put_back_from_their_definitions_of_before(self):
        # the effects file's `restores`: a command moves a plant flag nothing returns (a sequence's in service flag)
        plan = pilot_plan(effects=effects_of({"device": "SQ1", "path": "W18", "returns": True, "within": 4,
                                              "restores": ["src/P1_RUN", "[default]cadre_hmi_pilot/src/XV1_ZSO"],
                                              "expect": [{"member": "SQ1/started", "changes": True}]}))
        step = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W18")
        self.assertEqual(step["restores"], ["[default]cadre_hmi_pilot/src/P1_RUN", "[default]cadre_hmi_pilot/src/XV1_ZSO"])
        self.pulse_glass()
        self.node("src/P1_RUN")["value"], self.node("src/XV1_ZSO")["value"] = True, False

        def cycle(caption):
            self.node("SQ1/started")["value"] = 1760000000000
            self.node("src/P1_RUN")["value"], self.node("src/XV1_ZSO")["value"] = False, True
        self.glass.on_click = cycle
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual((self.node("src/P1_RUN")["value"], self.node("src/XV1_ZSO")["value"]), (True, False))   # as found
        self.assertEqual(row["tag"]["put back"], ["cadre_hmi_pilot/src/P1_RUN", "cadre_hmi_pilot/src/XV1_ZSO"])
        self.assertEqual(self.tags.before, {})

    def test_a_flag_that_cannot_be_put_back_fails_the_pulse(self):
        plan = pilot_plan(effects=effects_of({"device": "SQ1", "path": "W18", "returns": True, "within": 4,
                                              "restores": ["src/P1_RUN"],
                                              "expect": [{"member": "SQ1/started", "changes": True}]}))
        step = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W18")
        self.pulse_glass()
        self.node("src/P1_RUN")["value"] = True

        def cycle(caption):
            self.node("SQ1/started")["value"] = 1760000000000
            self.node("src/P1_RUN")["value"] = False
            self.gw.drop_import = True   # from here the gateway takes no import: the definition of before cannot hold
        self.glass.on_click = cycle
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("could not be put back", self.w.rows[-1]["detail"])

    def test_restores_belongs_to_a_pulse_and_is_a_list_of_tag_paths(self):
        for bad in ({"device": "P2", "path": "W1", "restores": ["P1/mode"], "expect": []},
                    {"device": "SQ1", "path": "W18", "restores": "P1/mode"},
                    {"device": "SQ1", "path": "W18", "restores": []},
                    {"device": "SQ1", "path": "W18", "restores": [1]}):
            self.assertEqual(len(walk_plan.effects_errors(effects_of(bad))), 1, bad)
        self.assertEqual(walk_plan.effects_errors(effects_of(
            {"device": "SQ1", "path": "W18", "restores": ["P1/mode"], "expect": []})), [])

    def test_the_refusal_of_a_pulse_watches_what_the_pulse_would_change(self):
        step = self.step("R", "W18")
        self.pulse_glass()
        self.glass.disabled["Start cycle"] = True

        def arrives(caption):   # a library without the role check: the pulse is made and returned
            self.glass.message = "Refused: sign in with the Administrator role"
            self.node("SQ1/started")["value"] = 1760000000000
        self.glass.on_crafted_call = arrives
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("SQ1/started", self.w.rows[-1]["detail"])

    # -- parity ---------------------------------------------------------------------------------------
    def test_a_reading_both_scenes_expect_alike_fails(self):
        scenes = copy.deepcopy([s for s in self.plan["steps"] if s["group"] == "P"])
        self.glass.symbols.update({"PIC-1": ["PIC-1", "▸ 46.4"], "Header kPa": ["Header kPa", "▸ 46.4"]})
        self.glass.close_faceplate = lambda page: None
        self.glass.badge_icon = lambda name: name
        self.w.plan = {**self.plan, "steps": scenes}
        rows = self.w.parity(scenes[0])
        self.assertEqual([r["ok"] for r in rows if "setpoint" in r["expected"]], [True, True])   # the scene arrived and reads
        self.tags.restore()
        scenes[1]["readings"][0]["expect"] = scenes[0]["readings"][0]["expect"]   # a plan edited by hand
        self.w.rows.clear()
        rows = self.w.parity(scenes[0])
        self.assertFalse(rows[0]["ok"])
        self.assertIn("both scenes expect the same", rows[0]["detail"])

    # -- a fault found standing -------------------------------------------------------------------------
    def test_a_fault_found_standing_is_imported_back(self):
        plan = wtp_plan()
        step = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W5" and s["device"] == "P-101")
        gw = FakeGateway(load(WTP / "tags.json"))
        gw.nodes["cadre_hmi_wtp/P101/fault"]["value"] = True   # the device is faulted when the step begins
        self.w.tags = walk.Tags(["[default]cadre_hmi_wtp"], deploy=gw)
        self.w.plan = plan
        self.w.acknowledge = lambda page, step: True
        self.glass.disabled["Reset fault"] = False
        self.glass.notes["Fault"] = "Fault"

        def reset(caption):
            gw.nodes["cadre_hmi_wtp/P101/fault"]["value"] = False
            self.glass.notes["Fault"] = "Normal"
            del self.glass.disabled["Reset fault"]
        self.glass.on_click = reset
        self.w.no_crafted = True
        self.w.fault_reset({**step, "symbols": []})
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertIs(gw.nodes["cadre_hmi_wtp/P101/fault"]["value"], True)   # as found
        self.assertIn(("default", "cadre_hmi_wtp/P101/fault"), gw.imports)
        self.assertIn("imported and read back: 1", row["detail"])


class ModuleTests(unittest.TestCase):
    """The plan and the runner are two modules; `walk` is the command line and exports both."""

    def test_walk_exports_the_plan_and_the_runner(self):
        for name in ("build_plan", "plan_text", "number_format", "expect_of", "glass_facts", "effects_errors",
                     "tag_nodes", "resolve", "scene_values", "load_profile", "SCHEMA", "EFFECTS_SCHEMA", "GROUPS"):
            self.assertIs(getattr(walk, name), getattr(walk_plan, name), name)
        for name in ("Tags", "Walk", "run", "selftest", "summarise", "settle_trial", "same", "TagFolderRefused",
                     "import_failed"):
            self.assertIs(getattr(walk, name), getattr(walk_run, name), name)

    def test_the_plan_needs_no_browser_and_no_gateway(self):
        source = (ROOT / "tools" / "compare" / "walk_plan.py").read_text(encoding="utf-8")
        for word in ("playwright", "import glass", "deploy", "import time", "import faceplates"):
            self.assertNotIn(word, source, word)


class ResultTests(unittest.TestCase):
    def rows(self, ok=True):
        return [{"id": "N-01", "group": "N", "ok": ok, "evidence": "glass", "detail": ""},
                {"id": "R-01", "group": "R", "ok": True, "evidence": "control and tag", "detail": "", "refused_by": "the gateway"}]

    def test_a_walk_with_nobody_signed_in_is_no_pass_of_the_write_groups(self):
        plan = {"render": "stock", "counts": {}}
        full = walk.summarise(plan, self.rows(), [], True, [], login_given=True)
        self.assertEqual((full["ok"], full["verdict"]), (True, "PASS"))
        read_only = walk.summarise(plan, self.rows(), ["C-01"], False, [])
        self.assertEqual((read_only["ok"], read_only["verdict"]), (True, "PASS, READ ONLY"))
        self.assertIn("no pass of them", read_only["note"])
        refused_login = walk.summarise(plan, self.rows(), ["C-01"], False, [], login_given=True)
        self.assertEqual((refused_login["ok"], refused_login["verdict"]), (False, "FAIL"))
        self.assertEqual(walk.summarise(plan, self.rows(ok=False), [], True, [])["verdict"], "FAIL")
        self.assertEqual(walk.summarise(plan, [], [], True, [])["verdict"], "FAIL")   # a walk of no row proves nothing
        self.assertEqual(full["refused_by"], {"the gateway": 1})
        self.assertEqual(full["evidence"]["R"], {"control and tag": 1})

    def test_a_tag_left_unrestored_fails_the_walk(self):
        gw = FakeGateway(load(FIXTURES / "pilot-tags.json"))
        tags = walk.Tags(["[default]cadre_hmi_pilot"], deploy=gw)
        tags.set({"[default]cadre_hmi_pilot/PIC1/sp": 46.444})
        gw.drop_import = True
        tags.restore()
        rep = walk.summarise({"render": "stock", "counts": {}}, self.rows(), [], True, [], tags, login_given=True)
        self.assertEqual((rep["ok"], rep["verdict"]), (False, "FAIL"))
        self.assertEqual([u["tag"] for u in rep["unrestored"]], ["[default]cadre_hmi_pilot/PIC1/sp"])


class TrialTests(unittest.TestCase):
    """After a reset the REST route reports a healthy trial while a new session still shows the trial
    page: a gate starts only once a session shows the project, and never takes that page for a pass."""

    def settle(self, shown: list[bool], **kw):
        calls = {"ensure": 0, "probe": 0, "slept": 0.0}

        def ensure(seconds):
            calls["ensure"] += 1
            return {"trialSecondsLeft": 7199, "expired": False, "reset": True}

        def probe(base):
            calls["probe"] += 1
            return shown[min(calls["probe"] - 1, len(shown) - 1)]

        def sleep(s):
            calls["slept"] += s
        return walk.settle_trial(1200, "http://gw/client/x", ensure=ensure, probe=probe, sleep=sleep, **kw), calls

    def test_a_session_that_shows_the_project_settles_at_once(self):
        out, calls = self.settle([False])
        self.assertEqual((out["settled"], out["session_probes"], calls["slept"]), (True, 1, 0.0))

    def test_the_trial_page_is_waited_out(self):
        out, calls = self.settle([True, True, True, False])
        self.assertEqual((out["settled"], out["session_probes"], calls["ensure"]), (True, 4, 1))
        self.assertEqual(calls["slept"], 45.0)

    def test_a_trial_page_that_stays_is_bounded_and_never_settled(self):
        out, calls = self.settle([True], tries=3, rounds=2)
        self.assertEqual((out["settled"], out["session_probes"], calls["ensure"]), (False, 6, 2))


class GeneratedTagsTests(unittest.TestCase):
    def test_a_build_that_generates_its_tags_is_planned_from_them(self):
        plan = walk.build_plan([load(ROOT / "screens" / "sample-pump-station.json")])
        self.assertTrue(plan["inputs"]["tagsGenerated"])
        self.assertGreater(plan["parity"]["checked"], 0)   # every member of a generated model is a memory tag
        self.assertEqual({t["tag"].split("]")[0] for t in plan["parity"]["tags"]}, {"[default"})

    def test_a_device_whose_symbol_shows_no_identifier_is_said_not_reached(self):
        # the sample's pumps and valves draw no identifier, so no step can find them on the glass:
        # the plan says so for each, and plans no capability it could not carry out
        plan = walk.build_plan([load(ROOT / "screens" / "sample-pump-station.json")])
        hidden = [n for n in plan["notReached"] if "device" in n]
        self.assertEqual(sorted(n["device"] for n in hidden), ["P101", "P102", "V101", "V102", "V103"])
        self.assertTrue(all("identifier is hidden" in n["why"] for n in hidden))
        self.assertEqual(plan["counts"]["C"], 0)
        self.assertEqual(plan["counts"]["D"], 0)


def edited(doc: dict, path: str, **keys) -> dict:
    """A copy of a tag document with one tag's keys replaced (`path` below the provider)."""
    doc = copy.deepcopy(doc)
    node = doc
    for seg in path.split("/")[1:]:
        node = next(t for t in node["tags"] if t["name"] == seg)
    node.update(keys)
    return doc


def effects_of(*effects, **more) -> dict:
    return {"schema": walk.EFFECTS_SCHEMA, "tagRoot": "[default]cadre_hmi_pilot", "effects": list(effects), **more}


class EntryEvidenceTests(RunnerCase):
    """Finding 1 of the second pass: a symbol that reads the same before and after a write is no second
    surface. The step is planned no finer than the coarsest symbol that shows the member, and the runner
    counts a symbol or an effect as evidence only when it did not agree before the write."""

    MARK = walk.SETPOINT_MARK.strip()

    def test_an_entry_step_is_never_finer_than_a_symbol_that_shows_it(self):
        # a setpoint of 0.4: a tenth of it is 0.04, which the field (0.00) shows and the symbols (0.0) do not
        plan = walk.build_plan([load(FIXTURES / "pilot-supply.json")], devices=load(FIXTURES / "pilot-devices.json"),
                               tags=edited(load(FIXTURES / "pilot-tags.json"), "cadre_hmi_pilot/PIC1/sp", value=0.4))
        step = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W12")
        self.assertEqual((step["format"], [s["rule"]["format"][1] for s in step["symbols"]]), ("0.00", ["0.0", "0.0"]))
        self.assertEqual(step["delta"], 0.1)
        target = walk.Walk.target_of(walk.Walk.__new__(walk.Walk), step, 0.4)
        for s in step["symbols"]:   # the symbol's text differs between the value held and the value typed
            self.assertNotEqual(walk.expect_of(s["rule"], 0.4), walk.expect_of(s["rule"], target), s["symbol"])
        # an effect that reads the value written counts the same way (the sample's speed line, format 0)
        speed = next(s for s in wtp_plan()["steps"] if s["group"] == "C" and s["path"] == "W3")
        self.assertGreaterEqual(speed["delta"], 1.0)
        self.assertEqual(walk_plan._step_delta(0.04, "0.000", (None, None), 0), 1.0)
        self.assertEqual(walk_plan._step_delta(0.04, "0.000", (None, None)), 0.004)

    def test_an_entry_fails_when_its_symbols_read_the_same_before_and_after(self):
        # the verifier's experiment 7: the write reaches nothing, the tag cannot be read, and both symbols
        # read 0.4 for 0.40 and for 0.36 alike; the row passed as "glass and control"
        step = {**self.step("C", "W12"), "delta": 0.04}   # a step finer than the symbols, as a hand-edited plan may hold
        self.glass.fields["Setpoint"] = 0.4
        self.glass.symbols.update({"PIC-1": ["PIC-1", self.MARK + " 0.4", "0.4", "kPa"],
                                   "Header kPa": [self.MARK + " 0.4", "0.4", "Header kPa"]})
        self.tags.value = lambda path: (False, None)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertEqual(row["evidence"], "control")
        self.assertIn("only the field typed into", row["detail"])
        self.assertIn("2 read what the value calls for before the write", row["detail"])
        self.assertEqual(len(row["glass"]["read the same before the write"]), 2)

    def test_an_entry_passes_on_a_symbol_that_follows_when_the_tag_cannot_be_read(self):
        step = self.step("C", "W12")

        def show(value):
            text = self.MARK + " " + walk.number_format(value, "0.0")
            self.glass.symbols.update({"PIC-1": ["PIC-1", text, "50.0", "kPa"], "Header kPa": [text, "50.0", "Header kPa"]})
        self.glass.fields["Setpoint"] = 50.0
        show(50.0)
        self.glass.on_type = lambda caption, value: show(value)
        self.tags.value = lambda path: (False, None)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["evidence"], "glass and control")
        self.assertNotIn("read the same before the write", row["glass"])

    def test_an_effect_met_before_the_write_is_checked_and_is_no_evidence(self):
        # a bound the plant met before (the sample's flow of at least 1): still checked afterwards,
        # never what proves the write
        plan = wtp_plan()
        step = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W3")
        bound = next(e for e in step["effects"] if "min" in e)
        step = {**step, "effects": [bound]}
        self.w.plan = plan
        self.glass.fields[step["field"]] = 80.0
        self.glass.symbols[bound["find"]] = [bound["find"], "100.0"]
        self.tags.value = lambda path: (False, None)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("only the field typed into", row["detail"])
        self.assertIn("1 read what the value calls for before the write", row["detail"])


class EffectsTests(RunnerCase):
    """Findings 2, 4 and 5 of the second pass: `changes` and `leaves` in every type of step, the floor
    of `within`, a reading that leaves judged on the member's own line, and a pulse the plant returns."""

    def errors(self, expect: dict, path: str = "W1", **more) -> list[str]:
        return walk.effects_errors(effects_of({"device": "P2", "path": path, **more, "expect": [expect]}))

    def test_an_expectation_states_one_thing_and_only_a_pulse_returns(self):
        self.assertEqual(self.errors({"member": "SQ1/started", "changes": True}), [])   # on a command, not only a pulse
        self.assertEqual(self.errors({"member": "PIC1/out", "leaves": True}, path="W15"), [])
        self.assertEqual(self.errors({"member": "a", "min": 1, "max": 2}), [])
        self.assertEqual(self.errors({"member": "a", "leaves": True, "returnsWithin": 5}, path="W18", returns=True), [])
        for bad in ({"member": "a"}, {"member": "a", "changes": True, "value": 1}, {"member": "a", "written": True, "min": 0},
                    {"member": "a", "changes": False}, {"member": "a", "leaves": "yes"}, {"changes": True}):
            self.assertEqual(len(self.errors(bad)), 1, bad)
        self.assertIn("returnsWithin", self.errors({"member": "a", "leaves": True, "returnsWithin": 5})[0])   # no pulse
        self.assertIn("returns", self.errors({"member": "a", "value": 1}, returns=True)[0])
        self.assertIn("returns", self.errors({"member": "a", "changes": True}, path="W18", returns=False)[0])
        for within in (0, -1, True, "6"):
            self.assertIn("within", self.errors({"member": "a", "value": 1}, within=within)[0], within)

    def test_an_effect_on_a_path_whose_step_reads_none_is_refused(self):
        # the fault reset and the frame's paths: an effect there was dropped without a word
        self.assertEqual(walk_plan.EFFECT_PATHS, ("W1", "W2", "W3", "W4", "W10", "W12", "W13", "W14", "W15", "W16",
                                                  "W17", "W18", "W19"))
        for path in ("W5", "W6", "W7", "W8", "W9", "W11", "w1"):
            bad = self.errors({"member": "SQ1/started", "changes": True}, path=path)
            self.assertEqual(len(bad), 1, path)
            self.assertIn(f"no step of write path {path} reads an effect", bad[0])
        # every path that is accepted has a step type that hands its effects to the runner
        reads = {s["path"] for plan in (pilot_plan_with_effects(), wtp_plan()) for s in plan["steps"]
                 if s["group"] == "C" and ("effects" in s or any("effects" in st for st in s.get("states", [])))}
        self.assertLessEqual(reads, set(walk_plan.EFFECT_PATHS))
        self.assertNotIn("W5", reads)
        for plan in (pilot_plan_with_effects(), wtp_plan()):
            for s in plan["steps"]:
                if s["group"] == "C" and s["path"] not in walk_plan.EFFECT_PATHS:
                    self.assertEqual(s["type"], "fault-reset", s["id"])

    def command_with_a_member_that_changes(self, **more) -> tuple[dict, dict]:
        plan = pilot_plan(effects=effects_of({"device": "P2", "path": "W1", "value": True, **more,
                                              "expect": [{"member": "SQ1/started", "changes": True}]}))
        step = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W1")
        self.w.plan = plan
        self.glass.disabled.update({"Start": False, "Stop": False})
        return plan, step

    def test_a_command_is_judged_on_a_member_that_changes(self):
        # the verifier's experiment 4: the effect was planned without a rule and the step raised KeyError
        _plan, step = self.command_with_a_member_that_changes()
        on = step["states"][0]
        self.assertEqual(on["effects"], [{"member": "SQ1/started", "tag": "[default]cadre_hmi_pilot/SQ1/started",
                                          "changes": True, "within": walk_plan.WAIT_FLOOR}])
        stamps = iter(range(1, 9))

        def command(caption, stamp=True):
            self.node("P2/cmd")["value"] = caption == "Start"
            if stamp and caption == "Start":
                self.node("SQ1/started")["value"] = next(stamps)
        self.glass.on_click = command
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["evidence"], "tag")
        self.assertIn("SQ1/started went from 0 to 1", json.dumps(row["tag"]))
        self.glass.on_click = lambda caption: command(caption, stamp=False)   # the command arrives, the member stays
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("SQ1/started holds 1 as before", row["detail"])
        self.assertIs(self.node("P2/cmd")["value"], False)   # put back

    def test_a_member_that_cannot_be_read_before_the_action_fails_the_step(self):
        _plan, step = self.command_with_a_member_that_changes()
        del self.gw.nodes["cadre_hmi_pilot/SQ1/started"]
        self.w.run_step(step)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("SQ1/started could not be read before the action", self.w.rows[-1]["detail"])
        self.assertEqual(self.glass.clicked, [])   # nothing is commanded on an effect that could not be judged

    def test_an_entry_is_judged_on_a_reading_that_leaves(self):
        plan = pilot_plan(effects=effects_of({"device": "PIC1", "path": "W15", "member": "gain",
                                              "expect": [{"member": "PIC1/out", "leaves": True}]}))
        step = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W15" and s["member"] == "gain")
        self.assertEqual([(e["symbol"], e["param"], e["rule"]["how"], e["leaves"]) for e in step["effects"]],
                         [("PIC1", "output", "line", True)])
        self.w.plan = plan
        block = ["PIC-1", "▸ 50.0", "50.0", "kPa", "Out 50 %"]
        self.glass.fields["Gain"] = 1.5
        self.glass.symbols["PIC-1"] = list(block)
        self.tags.value = lambda path: (False, None)
        self.glass.on_type = lambda caption, value: self.glass.symbols.update(
            {"PIC-1": block[:4] + ["Out 50 %" if value == 1.5 else "Out 43 %"]})
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["evidence"], "glass and control")
        self.assertIn("PIC1.output went from 'Out 50 %' to 'Out 43 %'", row["glass"]["symbols"])
        # the value line of the block moving is not the output leaving its reading
        self.glass.on_type = lambda caption, value: self.glass.symbols.update({"PIC-1": block[:2] + ["49.9"] + block[3:]})
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("PIC1.output reads 'Out 50 %' as before", row["detail"])

    def test_an_entry_waits_for_its_put_back_as_long_as_for_its_effects(self):
        # the plant project's first walk with its simulation: a setpoint whose loop follows within 49 s was
        # given 8 s to follow the value put back, and the step failed on a plant that did as it should
        plan = pilot_plan(effects=effects_of({"device": "PIC1", "path": "W15", "member": "gain", "within": 20,
                                              "expect": [{"member": "PIC1/out", "leaves": True}]}))
        step = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W15" and s["member"] == "gain")
        self.assertEqual([e["within"] for e in step["effects"]], [20])
        self.w.plan = plan
        block = ["PIC-1", "\u25b8 50.0", "50.0", "kPa", "Out 50 %"]
        self.glass.fields["Gain"] = 1.5
        self.glass.symbols["PIC-1"] = list(block)
        self.tags.value = lambda path: (False, None)
        self.glass.on_type = lambda caption, value: self.glass.symbols.update(
            {"PIC-1": block[:4] + ["Out 50 %" if value == 1.5 else "Out 43 %"]})
        waits, real = [], self.w.wait

        def wait(page, check, seconds=8.0, step_ms=500):
            waits.append(seconds)
            return real(page, check, seconds, step_ms)
        self.w.wait = wait
        self.w.run_step(step)
        self.assertTrue(self.w.rows[-1]["ok"], self.w.rows[-1]["detail"])
        self.assertEqual(waits[-2:], [20, 20])              # the effects, then the put back

    def test_the_floor_of_within(self):
        self.assertEqual(walk_plan.WAIT_FLOOR, 8)
        self.assertIs(walk_run.WAIT_FLOOR, walk_plan.WAIT_FLOOR)
        clock = walk_run.time

        def waited(**more) -> float:
            _plan, step = self.command_with_a_member_that_changes(**more)
            self.glass.clicked.clear()
            began = clock.now
            self.w.run_step(step)   # the click reaches nothing: the step waits its whole time, then fails
            self.assertFalse(self.w.rows[-1]["ok"])
            return clock.now - began
        floor = waited()
        self.assertEqual(waited(within=2), floor)       # a `within` below the floor changes nothing
        self.assertEqual(waited(within=8), floor)
        self.assertEqual(waited(within=20), floor + 12)
        table = (ROOT / "wiki" / "08-generation-and-validation.md").read_text(encoding="utf-8")
        self.assertRegex(table, r"\| `effects\[\]\.within` \|[^\n]*never fewer than 8[^\n]*\|")

    # -- finding 4: the member's own line ---------------------------------------------------------------
    def test_a_reading_that_leaves_is_the_members_own_line(self):
        step = self.step("C", "W18")
        text = step["effects"][1]
        self.assertEqual((text["member"], text["rule"], text["fixed"], text["others"]),
                         ("SQ1/stepText", {"how": "text"}, ["FLT-1"], [["Step ", "0", ""]]))
        self.glass.symbols["FLT-1"] = ["FLT-1", "Drive Out", "Step 2"]
        self.assertEqual(self.w.shown(self.w.signed, text), ["Drive Out"])
        self.assertEqual(self.w.shown(self.w.signed, {"find": "FLT-1"}), ["FLT-1", "Drive Out", "Step 2"])   # a refusal's `rest`
        start = next(s for s in self.plan["steps"] if s["group"] == "C" and s["path"] == "W1")["states"][0]["effects"]
        self.glass.symbols.update({"SupplyPump_No2": ["On", "SupplyPump_No2"], "SupplyFlow_FT01": ["12.5 L/s", "SupplyFlow_FT01"]})
        self.assertEqual([self.w.shown(self.w.signed, e) for e in start], [["On"], ["12.5 L/s"]])

    def test_a_pulse_fails_when_only_another_line_of_the_block_moves(self):
        # the verifier's experiment 2: the step number changed, the step text never left "Standby",
        # and the effect on the text was met by the number's line
        step = self.step("C", "W18")
        self.pulse_glass()

        def cycle(caption):
            self.node("SQ1/started")["value"] = 1760000000000
            self.glass.symbols["FLT-1"] = ["FLT-1", "Standby", "Step 2"]
        self.glass.on_click = cycle
        self.back_at_rest_after(40, ["FLT-1", "Standby", "Step 1"])
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("no effect on SQ1/stepText", row["detail"])
        self.assertNotIn("SQ1/started,", row["detail"])   # the helper did change: only the text is missing

    # -- finding 5: a pulse the plant returns -------------------------------------------------------------
    def stuck_pulse(self, step: dict) -> dict:
        self.pulse_glass()

        def cycle(caption):
            self.node("SQ1/trigger")["value"] = True   # the plant takes the pulse and never returns the member
            self.node("SQ1/started")["value"] = 1760000000000
            self.glass.symbols["FLT-1"] = ["FLT-1", "Drive Out", "Step 2"]
        self.glass.on_click = cycle
        self.back_at_rest_after(6, ["FLT-1", "Standby", "Step 1"])
        self.w.run_step(step)
        return self.w.rows[-1]

    def test_the_effects_file_says_that_the_plant_returns_a_pulse(self):
        step = self.step("C", "W18")
        self.assertIs(step["returns"], True)   # the fixture's trigger is returned by its own event script (GF-57)
        self.assertIs(next(s for s in pilot_plan()["steps"] if s.get("type") == "pulse")["returns"], False)
        self.assertIn("the plant returns trigger to false", self.stuck_pulse(step)["expected"])

    def test_a_pulse_the_plant_does_not_return_fails(self):
        # the verifier's experiment 1: the trigger stayed true, the walk imported it back and passed
        row = self.stuck_pulse(self.step("C", "W18"))
        self.assertFalse(row["ok"])
        self.assertIn("the plant did not return trigger to false", row["detail"])
        self.assertIn("its definition of before was imported", row["detail"])
        self.assertIs(self.node("SQ1/trigger")["value"], False)   # put back whatever the verdict
        self.assertEqual(self.tags.before, {})

    def test_a_pulse_nothing_returns_passes_where_the_effects_file_does_not_say_it_returns(self):
        row = self.stuck_pulse({**self.step("C", "W18"), "returns": False})
        self.assertTrue(row["ok"], row["detail"])
        self.assertIn("its definition of before was imported", row["detail"])
        self.assertIs(self.node("SQ1/trigger")["value"], False)


class RouteTests(RunnerCase):
    """Finding 3 of the second pass: what a navigation step checks, pinned. The address and the top
    bar's page name are one fact (the name is computed from the route), so a step proves the page by
    what it holds: the symbol the descriptor places, or the component a page of the frame draws."""

    def setUp(self):
        super().setUp()
        self.w.goto = lambda page, route, fresh=False: setattr(page, "url", self.w.base + route)
        self.steps = [s for s in self.plan["steps"] if s["group"] == "N"]
        self.supply, self.trends, self.alerts = self.steps
        self.glass.menu = {s["label"]: s["route"] for s in self.steps}

    def show(self, step: dict) -> None:
        """The glass as the page of `step` draws it."""
        self.glass.top_bar = step["title"]
        self.glass.symbols = {step["symbol"]: [step["symbol"]]} if step.get("symbol") else {}
        self.glass.holds = {step["holds"]["component"]: 5} if step.get("holds") else {}

    def walked(self, step: dict) -> dict:
        self.w.route(step)
        return self.w.rows[-1]

    def test_the_plan_names_what_each_page_must_hold(self):
        self.assertEqual([(s["route"], s["symbol"], s["holds"]) for s in self.steps], [
            ("/supply", "P-1", None),
            ("/trends", None, {"component": "ia.chart.timeseries", "what": "a trend card"}),
            ("/alerts", None, {"component": "ia.display.alarmstatustable", "what": "the alarm status table"})])
        for s in wtp_plan()["steps"]:
            if s["group"] == "N":   # every route step can tell its page from a blank view under the right address
                self.assertTrue(s["symbol"] or s["holds"], s["id"])
        # the views that draw the two pages of the frame do hold the component named
        for route, (view, component, _what) in walk_plan.PAGE_HOLDS.items():
            self.assertIn(component, [n["type"] for n in nodes_of(view)], (route, view))

    def test_a_route_step_passes_on_its_page(self):
        for step in self.steps:
            self.show(step)
            row = self.walked(step)
            self.assertTrue(row["ok"], (step["id"], row["detail"]))
            self.assertNotIn(f"from {step['route']}", row["done"])   # the page each step began on is another
        self.assertIn("holding the alarm status table", self.w.rows[-1]["expected"])
        self.assertEqual(self.w.rows[-1]["glass"]["the alarm status table"], 5)

    def test_a_wrong_title_fails(self):
        self.show(self.supply)
        self.glass.top_bar = "Trends"
        self.assertIn("the top bar reads 'Trends', the page is 'Supply'", self.walked(self.supply)["detail"])
        self.assertFalse(self.w.rows[-1]["ok"])

    def test_a_page_without_the_symbol_the_descriptor_places_fails(self):
        self.show(self.supply)
        self.glass.symbols = {}
        row = self.walked(self.supply)
        self.assertFalse(row["ok"])
        self.assertIn("no symbol of the page shows 'P-1'", row["detail"])

    def test_a_blank_view_under_the_right_address_fails(self):
        self.show(self.supply)
        self.glass.page_components = 0   # the frame renders its own around a blank view
        row = self.walked(self.supply)
        self.assertFalse(row["ok"])
        self.assertIn("the page holds no component outside the docks", row["detail"])

    def test_a_page_of_the_frame_without_its_component_fails(self):
        # the address and the title are right and the page holds components: before `holds`, that passed
        for step in (self.trends, self.alerts):
            self.show(step)
            self.glass.holds = {}
            row = self.walked(step)
            self.assertFalse(row["ok"], step["id"])
            self.assertIn(f"the page holds no {step['holds']['component']}", row["detail"])

    def test_a_step_that_begins_on_its_own_route_fails(self):
        self.show(self.supply)
        row = self.walked({**self.supply, "from": "/supply"})   # the page is on /supply and is sent nowhere else first
        self.assertFalse(row["ok"])
        self.assertIn("the step began on the route itself", row["detail"])

    def test_an_entry_that_is_not_found_or_leads_elsewhere_fails(self):
        self.show(self.supply)
        self.glass.menu = {}
        row = self.walked(self.supply)
        self.assertIn("the entry was not found", row["detail"])
        self.assertIn("the address is /trends", row["detail"])
        self.glass.menu = {"Supply": "/alerts"}
        self.assertIn("the address is /alerts", self.walked(self.supply)["detail"])

    def test_a_card_title_leads_to_its_page(self):
        card = next(s for s in wtp_plan()["steps"] if s["group"] == "N" and s["via"] == "card")
        self.show(card)
        self.glass.cards = {card["label"]: card["route"]}
        self.assertTrue(self.walked(card)["ok"], self.w.rows[-1]["detail"])
        self.glass.cards = {}
        self.assertIn("the entry was not found", self.walked(card)["detail"])

    # -- the controls of a navigation step ----------------------------------------------------------------
    def test_the_route_controls_fail_for_their_reasons(self):
        controls = {name: (step, because) for name, step, because, _why in
                    walk_run.route_controls(self.plan["steps"], lambda route, text: False)}
        step, because = controls["route"]
        self.assertEqual((step["id"], step["route"], step["from"], because),
                         ("N-01", "/supply", "/supply", "the step began on the route itself"))
        step, because = controls["route-content"]   # the fixture has one page of a descriptor: another page's component
        self.assertEqual((step["id"], step["symbol"], step["holds"], because),
                         ("N-01", "P-1", self.trends["holds"], ("the page holds no",)))
        for name, (step, because) in controls.items():
            self.show(self.supply)   # the page is as it should be: only what the control changed can fail
            self.w.signed.url = self.w.base + step["route"]
            n = len(self.w.rows)
            self.w.route(step)
            verdict = walk_run.control_verdict(name, step, self.w.rows[n:], because)
            self.assertTrue(verdict["ok"], verdict)
            self.assertIs(verdict["row_ok"], False)

    def test_route_content_takes_a_symbol_the_page_does_not_show(self):
        steps = wtp_plan()["steps"]
        asked = []

        def shows(route, text):
            asked.append((route, text))
            return text == "XV-101"   # the overview draws the first symbol of the intake page too
        content = {name: (step, because) for name, step, because, _why in walk_run.route_controls(steps, shows)}["route-content"]
        self.assertEqual((content[0]["route"], content[0]["symbol"]), ("/", "P-301"))
        self.assertEqual(content[1], ("no symbol of the page shows", "the page holds no"))
        self.assertEqual(asked, [("/", "XV-101"), ("/", "P-301")])
        none = walk_run.route_controls([s for s in steps if s["group"] != "N"], shows)
        self.assertEqual([(name, step) for name, step, _b, _w in none], [("route", None), ("route-content", None)])


class ControlTests(RunnerCase):
    """Finding 8 of the second pass: a negative control holds only when its step failed for the reason
    the control stands for."""

    def test_a_control_holds_only_for_its_stated_reason(self):
        step = {"id": "C-01"}

        def verdict(detail, because, ok=False):
            return walk_run.control_verdict("capability", step, [{"id": "C-01", "ok": ok, "detail": detail}], because)["ok"]
        reason = walk_run.SKIPPED_BECAUSE["states"]
        self.assertTrue(verdict("after Start: glass {}, tag {'P2/cmd': False}, expected True", reason))
        self.assertFalse(verdict("the button Start is disabled", reason))
        self.assertFalse(verdict("no faceplate opened on P-2 from the symbol showing 'P-2'", reason))
        self.assertFalse(verdict("the faceplate read 'Refused' on Setpoint before the step acted", walk_run.SKIPPED_BECAUSE["entry"]))
        self.assertFalse(verdict("after Start: glass {}, tag {}, expected True", reason, ok=True))   # the step passed
        self.assertFalse(walk_run.control_verdict("capability", step, [], reason)["ok"])              # no row at all
        self.assertTrue(verdict("a; b", ("a", "b")))
        self.assertFalse(verdict("a", ("a", "b")))   # every reason named, or the control does not hold

    def skipped(self, step: dict) -> dict:
        self.w.skip_write = True
        try:
            n = len(self.w.rows)
            self.w.run_step(step)
            kind = "pulse, no effect named" if step["type"] == "pulse" and not step["effects"] else step["type"]
            return walk_run.control_verdict("control", step, self.w.rows[n:], walk_run.SKIPPED_BECAUSE[kind])
        finally:
            self.w.skip_write = False

    def test_a_skipped_write_fails_each_type_of_step_for_its_reason(self):
        self.glass.disabled.update({"Start": False, "Stop": False})
        self.glass.fields["Gain"] = 1.5
        self.pulse_glass()
        bare_pulse = next(s for s in pilot_plan()["steps"] if s.get("type") == "pulse")
        for step in (self.step("C", "W1"), self.step("C", "W15", "gain"), self.step("C", "W18"), bare_pulse):
            verdict = self.skipped(step)
            self.assertTrue(verdict["ok"], verdict)
        self.assertEqual(self.glass.clicked, [])
        self.assertEqual(self.gw.imports, [])

    def test_a_step_that_fails_before_it_acts_is_no_control(self):
        self.w.open = lambda page, step, tab=None: (None, "no faceplate opened")
        for step in (self.step("C", "W1"), self.step("C", "W15", "gain"), self.step("C", "W18")):
            verdict = self.skipped(step)
            self.assertFalse(verdict["ok"], verdict)
            self.assertIs(verdict["row_ok"], False)

    def test_a_button_whose_handler_cannot_be_called_fails(self):
        # the client alone refused: the gateway's own check was not exercised (wiki 08 section 9.4)
        step = self.step("R", "W1")
        self.glass.disabled.update({"Start": True, "Stop": True})
        self.glass.handler = "no handler"
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertEqual(row["refused_by"], "the client only")
        self.assertIn("the button's handler could not be called (no handler)", row["detail"])


class UncaughtMutantTests(RunnerCase):
    """What the verifier's mutation check found no test for (2026-10-11): a module reading compared to
    the precision of a Float4, the acknowledgement read back under stock rendering, and a `states` step
    that ends with no evidence."""

    def test_a_module_reading_agrees_to_the_precision_of_a_float4(self):
        # the element's property is the tag's value as bound: a fixed 0.5 let 46.9 pass for 46.444
        element = {"lines": [], "module": "cadre.ob.pump", "icons": [], "frame": False, "on": True, "speed": 46.9,
                   "value": None}
        self.glass.find_symbol = lambda page, find: dict(element)
        reading, want = {"find": "P-101"}, {"module": "speed", "value": 46.444}
        self.assertEqual(self.w.read(None, reading, want), (False, "speed 46.9"))
        element["speed"] = 46.44400024414062   # the Float4 of 46.444, as the gateway hands it to the element
        self.assertTrue(self.w.read(None, reading, want)[0])
        self.assertTrue(self.w.read(None, reading, {"module": "on", "value": True})[0])
        self.assertFalse(self.w.read(None, reading, {"module": "on", "value": False})[0])
        self.assertFalse(self.w.read(None, reading, {"module": "frame", "value": True})[0])

    def alarm_glass(self, acknowledges: bool) -> dict:
        """The glass of the fixture's alarm scene under stock rendering: the faceplate's table lists
        the alarm while the source tag is true; Acknowledge answers true and, with `acknowledges`,
        the row then reads acknowledged."""
        import faceplates
        step = {**next(s for s in self.plan["steps"] if s["group"] == "A"), "symbols": []}
        state = {"acked": False}

        def raised() -> bool:
            return self.node("src/XV1_OE")["value"] is True

        def rows(page, right):
            return [f"XV-1 Object error Active, {'Acknowledged' if state['acked'] else 'Unacknowledged'}"] if raised() else []

        def ack(page, match):
            state["acked"] = acknowledges
            return True
        self.real_rows = faceplates.alarm_rows
        faceplates.alarm_rows = rows
        self.addCleanup(lambda: setattr(faceplates, "alarm_rows", self.real_rows))
        self.glass.tab_count = lambda right: int(raised())
        self.glass.frame_alarm_count = lambda page: int(raised())
        self.glass.ack_alarm = ack
        self.glass.alarm_menu_rows = lambda page, module: rows(page, None)
        self.glass.dock_open = lambda page: True
        return step

    def test_an_alarm_is_acknowledged_and_reads_so(self):
        step = self.alarm_glass(acknowledges=True)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["glass"]["after the acknowledgement"], ["XV-1 Object error Active, Acknowledged"])
        self.assertIs(self.node("src/XV1_OE")["value"], False)   # the scene cleared, the definition of before back

    def test_an_acknowledgement_that_does_not_show_fails(self):
        # Acknowledge answered, and the table still reads the alarm unacknowledged
        step = self.alarm_glass(acknowledges=False)
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("after Acknowledge the faceplate's table reads", row["detail"])
        self.assertIs(self.node("src/XV1_OE")["value"], False)

    def test_a_states_step_that_ends_with_no_evidence_fails(self):
        # the state is read once to choose the other one; after that the tag cannot be read, the step
        # has no row and no symbol, so nothing shows what the buttons did
        step = next(s for s in pilot_plan()["steps"] if s["group"] == "C" and s["path"] == "W1")
        self.assertEqual((step["row"], [st["symbols"] + st["effects"] for st in step["states"]]), (None, [[], []]))
        self.glass.disabled.update({"Start": False, "Stop": False})
        real, reads = self.tags.value, {"n": 0}

        def once(path):
            reads["n"] += 1
            return real(path) if reads["n"] <= len(step["states"]) else (False, None)
        self.tags.value = once
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertEqual(row["evidence"], "none")
        self.assertIn("neither the glass nor a tag showed the state", row["detail"])


class ReconcileTests(RunnerCase):
    """Finding 6 of the second pass: the result is reconciled with the plan."""

    ROWS = [{"id": "N-01", "group": "N", "ok": True, "evidence": "glass", "detail": ""},
            {"id": "R-01", "group": "R", "ok": True, "evidence": "control and tag", "detail": "", "refused_by": "the gateway"}]

    def plan_of(self, *steps) -> dict:
        return {"render": "stock", "counts": {}, "steps": [
            {"id": "N-01", "group": "N", "type": "route"}, {"id": "R-01", "group": "R", "type": "refusal"}, *steps]}

    def test_a_step_without_a_row_fails_the_walk(self):
        full = walk.summarise(self.plan_of(), self.ROWS, [], True, [], login_given=True)
        self.assertEqual((full["verdict"], full["missing"]), ("PASS", []))
        lost = walk.summarise(self.plan_of({"id": "T-01", "group": "T", "type": "trend-page"}), self.ROWS, [], True, [], login_given=True)
        self.assertEqual((lost["verdict"], lost["missing"]), ("FAIL", [{"id": "T-01", "why": "the step left no row"}]))
        not_run = walk.summarise(self.plan_of({"id": "C-01", "group": "C", "type": "states"}), self.ROWS, ["C-01"], False, [])
        self.assertEqual((not_run["verdict"], not_run["missing"]), ("PASS, READ ONLY", []))

    def test_a_held_refusal_whose_holder_did_not_run_it_is_missing(self):
        held = {"id": "R-07", "group": "R", "type": "refusal", "during": "C-07"}
        holder = {"id": "C-07", "group": "C", "type": "entry"}
        gone = walk.summarise(self.plan_of(held), self.ROWS, [], True, [], login_given=True)
        self.assertEqual(gone["verdict"], "FAIL")
        self.assertEqual(gone["missing"], [{"id": "R-07", "why": "a refusal held during C-07, which the plan does not hold"}])
        broke = walk.summarise(self.plan_of(holder, held), self.ROWS + [{"id": "C-07", "group": "C", "ok": True,
                                                                         "evidence": "tag", "detail": ""}], [], True, [])
        self.assertEqual(broke["missing"], [{"id": "R-07", "why": "a refusal held during C-07, which ran and did not reach it"}])
        self.assertEqual(broke["verdict"], "FAIL")
        read_only = walk.summarise(self.plan_of(holder, held), self.ROWS, ["C-07", "R-07"], False, [])
        self.assertEqual((read_only["verdict"], read_only["missing"]), ("PASS, READ ONLY", []))

    def test_a_parity_step_is_accounted_for_by_its_readings(self):
        scene = {"id": "P-1", "group": "P", "type": "parity", "readings": [{"id": "P-1.01"}, {"id": "P-1.02"}]}
        rows = self.ROWS + [{"id": i, "group": "P", "ok": True, "evidence": "glass and tag", "detail": ""} for i in ("P-1.01", "P-1.02")]
        self.assertEqual(walk.summarise(self.plan_of(scene), rows, [], True, [])["missing"], [])
        self.assertEqual([m["id"] for m in walk.summarise(self.plan_of(scene), rows[:-1], [], True, [])["missing"]], ["P-1"])
        broke = self.ROWS + [{"id": "P-1", "group": "P", "ok": False, "evidence": "none", "detail": "the step broke"}]
        self.assertEqual(walk.summarise(self.plan_of(scene), broke, [], True, [])["missing"], [])

    def test_a_walk_of_a_plan_whose_holder_was_deleted_fails(self):
        # the verifier's experiment 3: a plan a person overruled, the step that holds a refusal deleted
        held = [s for s in self.plan["steps"] if s.get("during")]
        keep = self.step("R", "W15", "gain")
        plan = {**self.plan, "steps": [keep] + copy.deepcopy(held)}
        self.w.plan = plan
        self.glass.fields["Gain"], self.glass.disabled["Gain"] = 1.5, True
        self.glass.on_crafted_entry = lambda caption, value: self.refuse(caption)
        not_run = self.w.walk()
        rep = walk.summarise(plan, self.w.rows, not_run, True, [], self.tags, login_given=True)
        self.assertEqual([(r["id"], r["ok"]) for r in rep["rows"]], [(keep["id"], True)])
        self.assertEqual((rep["verdict"], [m["id"] for m in rep["missing"]]), ("FAIL", [h["id"] for h in held]))

    def test_every_step_of_the_fixtures_plan_is_accounted_for_by_ids_the_runner_writes(self):
        # a full result as the runner shapes it: one row for each step, one for each parity reading
        ids = [r["id"] for s in self.plan["steps"] for r in (s["readings"] if s["type"] == "parity" else [s])]
        rows = [{"id": i, "group": i[0], "ok": True, "evidence": "glass", "detail": ""} for i in ids]
        self.assertEqual(walk.summarise(self.plan, rows, [], True, [], login_given=True)["verdict"], "PASS")
        self.assertEqual(walk.summarise(self.plan, rows[1:], [], True, [], login_given=True)["missing"][0]["id"], "N-01")


class SourceFolderTests(unittest.TestCase):
    """Finding 7 of the second pass and the way in: a tag outside the plan's tag folder is not planned
    (the runner would refuse the import), unless the caller names its folder with `--source-folder`."""

    SOURCE = {"name": "Plant", "tagType": "Folder", "tags": [
        {"name": "PIC1_SP", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Float8", "value": 50.0}]}
    SP = "[default]Plant/PIC1_SP"

    def plan(self, **kw) -> dict:
        tags = edited(load(FIXTURES / "pilot-tags.json"), "cadre_hmi_pilot/PIC1/sp", valueSource="reference",
                      sourceTagPath=self.SP)
        return walk.build_plan([load(FIXTURES / "pilot-supply.json")], devices=load(FIXTURES / "pilot-devices.json"),
                               tags=tags, source_tags=[(self.SOURCE, "")], **kw)

    def setpoint_of(self, plan: dict) -> tuple[list, list]:
        sets = [s for s in plan["steps"] if s["group"] == "P" and self.SP in s["set"]]
        why = [n["why"] for n in plan["parity"]["notChecked"] if n["param"] == "setpoint"]
        return sets, why

    def test_a_source_outside_the_tag_folder_is_not_checked(self):
        # the verifier's experiment 5: the plan set [default]Plant/PIC1_SP and the runner refused the import
        plan = self.plan()
        self.assertEqual(plan["sourceFolders"], [])
        sets, why = self.setpoint_of(plan)
        self.assertEqual(sets, [])
        self.assertEqual(len(why), 2)   # the block and the field both show the setpoint
        for w in why:
            self.assertIn(f"its value lies in {self.SP}, outside the plan's tag folder [default]cadre_hmi_pilot", w)
            self.assertIn("--source-folder", w)
        # the entry step on the member stays: an entry is typed, nothing is imported, and its tag is read
        self.assertTrue([s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W12"])
        self.assertEqual(walk_run.allowed_folders(plan), ["[default]cadre_hmi_pilot"])

    def test_a_source_folder_named_is_recorded_and_planned(self):
        plan = self.plan(source_folders=["[default]Plant"])
        self.assertEqual(plan["sourceFolders"], ["[default]Plant"])
        sets, why = self.setpoint_of(plan)
        self.assertEqual((len(sets), why), (2, []))
        self.assertEqual({r["source"] for r in sets[0]["readings"] if r["param"] == "setpoint"}, {self.SP})
        self.assertEqual(walk_run.allowed_folders(plan), ["[default]cadre_hmi_pilot", "[default]Plant"])
        # another folder named is not this one: nothing is inferred from where the document lies
        other = self.plan(source_folders=["[default]Other", "[default]Plan"])
        self.assertEqual(self.setpoint_of(other)[0], [])
        self.assertIn("and the source folders named ([default]Other, [default]Plan)", self.setpoint_of(other)[1][0])

    def test_without_the_option_a_plan_differs_only_by_the_empty_list(self):
        plain = pilot_plan_with_effects()
        self.assertEqual(plain["sourceFolders"], [])
        named = pilot_plan(effects=load(FIXTURES / "pilot-walk-effects.json"), source_folders=["[default]Plant"])
        self.assertEqual({**named, "sourceFolders": []}, plain)   # a folder no tag of the plan lies in changes no step
        self.assertEqual(walk.plan_text(self.plan(source_folders=["[default]Plant"])),
                         walk.plan_text(self.plan(source_folders=["[default]Plant"])))

    def test_how_a_source_folder_is_written(self):
        self.assertEqual(walk.source_folders_of(["[default]ctig/BH260602DL/", "[default]Plant", "[default]Plant"]),
                         ["[default]Plant", "[default]ctig/BH260602DL"])
        self.assertEqual(walk.source_folders_of(None), [])
        for bad in ("[default]", "Plant", "[default]/", "", "default]Plant"):
            with self.assertRaises(ValueError, msg=bad):
                walk.source_folders_of([bad])
        with self.assertRaises(ValueError):
            self.plan(source_folders=["[default]"])

    def test_the_runner_imports_into_the_folders_named_and_no_other(self):
        gw = FakeGateway(load(FIXTURES / "pilot-tags.json"))
        gw.nodes.update(walk.tag_nodes(self.SOURCE))
        gw.nodes["Plant2/PIC1_SP"] = dict(self.SOURCE["tags"][0])
        gw.nodes["cadre_hmi_pilot/PIC1/sp"] = {"name": "sp", "valueSource": "reference", "dataType": "Float8",
                                               "sourceTagPath": self.SP}
        refused = walk.Tags(walk_run.allowed_folders(self.plan()), deploy=gw)
        with self.assertRaises(walk.TagFolderRefused):
            refused.set({"[default]cadre_hmi_pilot/PIC1/sp": 46.444})
        self.assertEqual(gw.imports, [])
        tags = walk.Tags(walk_run.allowed_folders(self.plan(source_folders=["[default]Plant"])), deploy=gw)
        self.assertEqual(tags.set({"[default]cadre_hmi_pilot/PIC1/sp": 46.444})["failed"], [])
        self.assertEqual(gw.imports, [("default", "Plant/PIC1_SP")])
        self.assertEqual(tags.restore(), [self.SP])
        with self.assertRaises(walk.TagFolderRefused):   # a folder whose name begins alike, and another provider
            tags.set({"[default]Plant2/PIC1_SP": 1.0})
        with self.assertRaises(walk.TagFolderRefused):
            tags.put("[other]Plant/PIC1_SP", {"name": "PIC1_SP", "value": 1.0})

    def test_a_reference_to_another_provider_ends_there(self):
        nodes = {"a/x": {"name": "x", "valueSource": "reference", "sourceTagPath": "[edge]b/y"},
                 "b/y": {"name": "y", "valueSource": "memory", "value": 1}}
        self.assertEqual(walk.resolve("[default]a/x", nodes)["end"], "[edge]b/y")

    def faults_outside(self) -> tuple[dict, dict]:
        """The sample's tag model with every device's fault a reference into another folder."""
        tags = load(WTP / "tags.json")
        source = {"name": "Field", "tagType": "Folder", "tags": []}
        for folder in tags["tags"]:
            for t in folder.get("tags", []):
                if t["name"] == "fault" and t.get("valueSource", "memory") == "memory":
                    source["tags"].append({**t, "name": folder["name"] + "_FLT"})
                    keep = {k: t[k] for k in ("name", "tagType", "dataType") if k in t}
                    t.clear()
                    t.update({**keep, "valueSource": "reference", "sourceTagPath": f"[default]Field/{folder['name']}_FLT"})
        return tags, source

    def test_a_fault_or_an_alarm_scene_outside_the_tag_folder_is_not_reached(self):
        tags, source = self.faults_outside()
        self.assertGreater(len(source["tags"]), 3)
        descs = [load(WTP / f"{n}.json") for n in ("overview", "intake", "filtration", "disinfection")]
        plan = walk.build_plan(descs, tags=tags, source_tags=[(source, "")])
        self.assertFalse([s for s in plan["steps"] if s.get("path") == "W5"])
        why = [n["why"] for n in plan["notReached"] if n.get("path") == "W5"]
        self.assertTrue(why and all("lies outside the plan's tag folder [default]cadre_hmi_wtp" in w for w in why), why)
        named = walk.build_plan(descs, tags=tags, source_tags=[(source, "")], source_folders=["[default]Field"])
        raised = [s for s in named["steps"] if s["group"] == "C" and s.get("path") == "W5"]
        self.assertTrue(raised and all(s["source"].startswith("[default]Field/") for s in raised))
        scene = load(FIXTURES / "pilot-walk-effects.json")
        scene["alarmScenes"][0]["tag"] = "[default]Field/XV1_OE"
        self.assertEqual(walk.effects_errors(scene), [])
        plan = pilot_plan(effects=scene)
        self.assertEqual(plan["counts"]["A"], 0)
        self.assertIn("the alarm scene's tag [default]Field/XV1_OE lies outside", [n["why"] for n in plan["notReached"] if "scene" in n][0])
        self.assertEqual(pilot_plan(effects=scene, source_folders=["[default]Field"])["counts"]["A"], 1)


class SourceFolderRunnerTests(RunnerCase):
    def test_a_pulse_whose_member_lies_outside_is_pressed_and_never_imported(self):
        step = dict(next(s for s in pilot_plan()["steps"] if s.get("type") == "pulse"))
        self.gw.nodes["cadre_hmi_pilot/SQ1/trigger"] = {"name": "trigger", "valueSource": "reference",
                                                        "dataType": "Boolean", "sourceTagPath": "[default]Field/TRG"}
        self.gw.nodes["Field/TRG"] = {"name": "TRG", "valueSource": "memory", "dataType": "Boolean", "value": False}
        self.pulse_glass()
        self.glass.on_click = lambda caption: self.gw.nodes["Field/TRG"].update(value=True)   # nothing returns it
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("its source lies outside the plan's tag folder", row["detail"])
        self.assertEqual(self.gw.imports, [])
        # with the folder named, the member nothing returned is imported back
        self.w.tags = walk.Tags(["[default]cadre_hmi_pilot", "[default]Field"], deploy=self.gw)
        self.gw.nodes["Field/TRG"]["value"] = False
        self.w.run_step(step)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(self.gw.imports, [("default", "Field/TRG")])
        self.assertIs(self.gw.nodes["Field/TRG"]["value"], False)


class SuiteVerdictTests(unittest.TestCase):
    """Finding 10 of the second pass: the rules of `wtp_suite.run_project` (the trial asked for before
    each gate, a walk with nobody signed in failing where a test login exists, the plant verified), with
    gates that are stubs."""

    def setUp(self):
        import tempfile
        import wtp_suite
        self.suite = wtp_suite
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = {}
        self.calls = []
        self.settled = {}                # gate -> False where a session keeps showing the trial page
        self.login = {"stub": True}      # what `read_login` answers: a login exists on the machine, or None
        self.walk_result = {"ok": True, "verdict": "PASS", "counts": {}, "signed_in": True, "failed": [], "not_run": [],
                            "refused_by": {}, "unrestored": [], "note": "", "restored": [], "plan": {}}
        self.plant = {"ok": True, "tags": 219, "differences": [], "extra": []}
        self.g10 = {"passed": 15, "checks": 15, "results": [], "signed_in": True}
        gates = iter(("g8", "g11", "g10", "walk"))

        def settle(seconds, base):
            gate = next(gates)
            self.calls.append("trial " + gate)
            return {"settled": self.settled.get(gate, True), "session_probes": 1}

        def capture(base, route, out):
            self.calls.append("g8 " + route)
            return {"ok": True, "components": 200, "view_error_badges": 0, "quality_overlays": 0,
                    "trial_expired": False, "view_not_found": False}

        def functional_run(base, out, restore=None, login=None, trends=None):
            self.calls.append("g10")
            return self.g10

        def generated_walk(project, base, out):
            self.calls.append("walk")
            if isinstance(self.walk_result, Exception):
                raise self.walk_result
            return self.walk_result
        self.patch(wtp_suite.walk, "settle_trial", settle)
        self.patch(wtp_suite.capture, "capture", capture)
        self.patch(wtp_suite, "g11", lambda base, out: self.calls.append("g11") or {
            "ok": True, "opened": 44, "expected": 44, "faults": [], "missing": [], "unexpected": []})
        self.patch(wtp_suite.functional, "run", functional_run)
        self.patch(wtp_suite.functional, "read_login", lambda: self.login)
        self.patch(wtp_suite, "generated_walk", generated_walk)
        self.patch(wtp_suite, "restore_plant", lambda: self.calls.append("restore") or {"successCount": 219})
        self.patch(wtp_suite, "verify_plant", lambda: self.calls.append("verify") or self.plant)

    def patch(self, owner, name, value):
        self.saved[(owner, name)] = getattr(owner, name)
        setattr(owner, name, value)

    def tearDown(self):
        for (owner, name), value in self.saved.items():
            setattr(owner, name, value)
        self.tmp.cleanup()

    def run_project(self) -> dict:
        return self.suite.run_project("cadre_hmi_wtp", Path(self.tmp.name) / "wtp")

    def test_every_gate_green_and_signed_in_passes(self):
        res = self.run_project()
        self.assertTrue(res["ok"])
        self.assertFalse(res["read_only"])
        gates = [c for c in self.calls if not c.startswith("g8 ")]
        self.assertEqual(gates, ["restore", "trial g8", "trial g11", "g11", "trial g10", "g10", "restore", "trial walk",
                                 "walk", "restore", "verify"])
        self.assertEqual(len([c for c in self.calls if c.startswith("g8 ")]), len(self.suite.ROUTES))

    def test_a_walk_with_nobody_signed_in_fails_where_a_test_login_exists(self):
        self.walk_result = {**self.walk_result, "verdict": "PASS, READ ONLY", "signed_in": False}
        self.assertFalse(self.run_project()["ok"])

    def test_without_a_test_login_the_suite_passes_read_only_and_says_so(self):
        self.login = None
        self.walk_result = {**self.walk_result, "verdict": "PASS, READ ONLY", "signed_in": False}
        res = self.run_project()
        self.assertEqual((res["ok"], res["read_only"]), (True, True))

    def test_a_trial_page_that_stays_fails_the_gate_by_name_and_runs_nothing_of_it(self):
        self.settled = {"g10": False}
        res = self.run_project()
        self.assertFalse(res["ok"])
        self.assertEqual(res["trial_page_persists"], ["g10"])
        self.assertNotIn("g10", self.calls)
        self.assertEqual((res["G10"]["ok"], res["G10"]["checks"]), (False, 0))
        self.assertIn("walk", self.calls)   # the gates after it still run

    def test_a_trial_page_before_g8_is_no_blank_page_that_passes(self):
        self.settled = {"g8": False}
        res = self.run_project()
        self.assertEqual((res["ok"], res["G8"]), (False, {"ok": False, "routes": {}}))
        self.assertFalse([c for c in self.calls if c.startswith("g8 ")])

    def test_a_failed_check_of_g10_fails(self):
        self.g10 = {**self.g10, "passed": 14, "results": [{"id": "F3", "ok": False, "detail": "x"}]}
        res = self.run_project()
        self.assertEqual((res["ok"], [f["id"] for f in res["G10"]["failed"]]), (False, ["F3"]))

    def test_a_plant_not_restored_fails(self):
        self.plant = {"ok": False, "tags": 219, "differences": [{"tag": "a", "why": "differs on ['value']"}], "extra": []}
        self.assertFalse(self.run_project()["ok"])

    def test_a_failed_walk_fails(self):
        self.walk_result = {**self.walk_result, "ok": False, "verdict": "FAIL"}
        self.assertFalse(self.run_project()["ok"])

    def test_the_plant_is_restored_and_verified_when_the_walk_breaks(self):
        self.walk_result = RuntimeError("the browser went away")
        with self.assertRaises(RuntimeError):
            self.run_project()
        self.assertEqual(self.calls[-2:], ["restore", "verify"])

    def test_a_step_of_the_plan_without_a_row_is_listed_as_a_failure_of_the_walk(self):
        # `generated_walk` itself, over a runner that is a stub: what `summarise` calls missing is shown as failed
        self.patch(self.suite, "generated_walk", self.saved[(self.suite, "generated_walk")])
        self.patch(self.suite, "walk_plan", lambda project: {"counts": {}, "steps": []})
        self.patch(self.suite.walk, "run", lambda plan, base, out, login=None, before_step=None: {
            "ok": False, "verdict": "FAIL", "counts": {}, "signed_in": True, "refused_by": {}, "rows": [],
            "missing": [{"id": "R-07", "why": "a refusal held during C-07, which the plan does not hold"}],
            "not_run": [], "note": "", "restored": [], "unrestored": []})
        res = self.suite.generated_walk("cadre_hmi_wtp", "http://gw/x", Path(self.tmp.name) / "walk")
        self.assertEqual(res["failed"], [{"id": "R-07", "detail": "no row: a refusal held during C-07, which the plan does not hold"}])


class PlantRunTests(unittest.TestCase):
    """What the walk's first run on a plant project asked of the plan (2026-10-11)."""

    def test_a_symbol_the_librarys_view_draws_under_the_module_rendering_is_not_read_as_a_module_component(self):
        # the generator's rule (`screen.module_draws`): a symbol the module's component cannot show (a vertical fan,
        # a valve variant the module lacks) is a library view under the module rendering too
        how = lambda kind, params, param, render: (walk_plan.reading_rule(kind, params, param, render)[0] or {}).get("how")
        self.assertEqual(how("pump", {"tag": "P-1", "hasTag": True, "hasSpeed": True}, "on", "module"), "module")
        self.assertEqual(how("pump", {"tag": "P-1", "hasTag": True}, "on", "module"), "module")   # speedless: 0.3.0
        self.assertEqual(walk_plan.reading_rule("pump", {"tag": "P-1"}, "speed", "module")[0], None)
        self.assertEqual(how("tank", {"tag": "T-1", "unit": "Lt"}, "value", "module"), "module")
        self.assertEqual(how("valve", {"tag": "V-1"}, "open", "module"), "module")
        self.assertEqual(how("motor", {"tag": "M-1"}, "on", "module"), "module")
        self.assertNotEqual(how("fan", {"tag": "F-1", "vertical": True}, "on", "module"), "module")
        self.assertNotEqual(how("valve", {"tag": "V-1", "variant": "double"}, "open", "module"), "module")
        # a static tank that states no capacity is the library's tile, as the generator settles it: the plan
        # reads the descriptor's symbol the same way, whatever the contract's default says
        desc = {"schema": "cadre-hmi-screen/1",
                "screen": {"id": "T", "route": "/t", "title": "T", "view": "Screens/T", "layout": "diagram",
                           "width": 1580, "height": 600}, "tagRoot": "[default]t",
                "symbols": [{"id": "V", "kind": "tank", "x": 100, "y": 100, "w": 96, "h": 80,
                             "params": {"static": True, "tag": "V-1"}}]}
        contracts = json.loads((ROOT / "library" / "contracts.json").read_text(encoding="utf-8"))
        contracts = contracts.get("views", contracts)
        syms = walk_plan._symbols([desc], contracts, "module")
        self.assertEqual([(s["id"], s["params"]["hasCapacity"]) for s in syms], [("V", False)])
        for kind, params, param in (("pump", {"tag": "P-1", "hasSpeed": True}, "on"), ("tank", {"tag": "T-1"}, "value")):
            self.assertNotEqual(how(kind, params, param, "stock"), "module")       # never under the stock rendering

    def test_a_trend_tab_is_walked_only_where_the_faceplate_has_one(self):
        # an indicator's faceplate has no Trend tab (`framework.expected_tabs`): its history stands on the
        # trend page, and the plan says so instead of planning a step that cannot pass
        self.assertNotIn("Trend", framework.expected_tabs("indicator", ["state"], ["state"]))
        devices = load(FIXTURES / "pilot-devices.json")
        indicator = next(d for d in devices["devices"] if d["kind"] == "indicator")
        indicator["trend"] = ["state"]
        plan = walk.build_plan([load(FIXTURES / "pilot-supply.json")], devices=devices,
                               tags=load(FIXTURES / "pilot-tags.json"))
        tabs = [s for s in plan["steps"] if s["type"] == "trend-tab"]
        self.assertTrue(tabs)
        self.assertNotIn("indicator", [s["kind"] for s in tabs])
        self.assertEqual(plan["trendTabAbsent"], {"indicator": [indicator["title"]]})
        self.assertNotIn("trendTabAbsent", pilot_plan())                           # absent where nothing is listed


class InstrumentModuleReadingTests(unittest.TestCase):
    """Module 0.3.1 (COB-127): once a readout or an instrument field is a component of the module, the walk
    reads the element's bound property and the glass finds the symbol by its element."""

    def rule(self, kind, params, param, render):
        return walk_plan.reading_rule(kind, {**library.READOUT_PARAMS, **params}, param, render)

    def test_a_module_readout_and_field_are_read_by_the_property_the_value_is_bound_to(self):
        ro = {"tag": "FT-101", "hasTag": True, "unit": "m3/h", "format": "#,##0.0"}
        self.assertEqual(self.rule("readout", ro, "value", "module")[0], {"how": "module", "prop": "value"})
        self.assertEqual(self.rule("readout", ro, "value", "stock")[0]["how"], "line")
        # a format the element cannot print is the library's view, read as under the stock rendering
        self.assertEqual(self.rule("readout", dict(ro, format="0%"), "value", "module")[0]["how"], "line")
        fi = {"label": "Flow", "unit": "m3/h", "format": "#,##0", "hasSetpoint": True, "setpointFormat": "#,##0"}
        self.assertEqual(self.rule("instrument-field", fi, "value", "module")[0], {"how": "module", "prop": "value"})
        self.assertEqual(self.rule("instrument-field", fi, "setpoint", "module")[0],
                         {"how": "module", "prop": "setpoint"})
        none, why = self.rule("instrument-field", dict(fi, hasSetpoint=False), "setpoint", "module")
        self.assertIsNone(none)
        self.assertIn("no setpoint", why)
        self.assertEqual(self.rule("instrument-field", dict(fi, align="start"), "value", "module")[0]["how"], "line")
        self.assertEqual(self.rule("instrument-field", fi, "value", "stock")[0]["how"], "line")

    def test_a_field_in_a_short_box_is_read_as_the_librarys_view(self):
        fi = {"label": "Flow", "unit": "m3/h", "format": "#,##0"}
        rule = lambda height: walk_plan.reading_rule("instrument-field", {**library.READOUT_PARAMS, **fi}, "value",
                                                     "module", height=height)[0]["how"]
        self.assertEqual((rule(None), rule(64), rule(36), rule(32)), ("module", "module", "module", "line"))

    def test_the_sample_is_read_by_the_module_property_exactly_where_the_generator_draws_the_module(self):
        gen = walk_plan._generator()
        descs = [load(WTP / f"{n}.json") for n in ("overview", "intake", "filtration", "disinfection")]
        seen = {"module": 0, "line": 0}
        for desc in descs:
            for sym in gen.descriptor_items(desc):
                kind = sym["kind"].lower()
                if kind not in ("readout", "instrument-field"):
                    continue
                defaults = library.READOUT_PARAMS if kind == "instrument-field" else library.AUTOMATION_READOUT_PARAMS
                params = {**defaults, **sym.get("params", {})}
                rule = walk_plan.reading_rule(kind, params, "value", "module")[0]
                draws = gen.module_draws(kind, params, target="module")
                self.assertEqual(rule["how"], "module" if draws else "line", sym["id"])
                seen[rule["how"]] += 1
                self.assertEqual(walk_plan.reading_rule(kind, params, "value", "stock")[0]["how"], "line")
        self.assertGreater(seen["module"], 0)


class ModuleGlassTests(unittest.TestCase):
    """The glass finds a readout and an instrument field of the module by their element and reads the value
    from it (shadow DOM). A page with stand-ins for the two elements: the glass reads properties and shadow
    DOM text, not the real element's drawing."""

    PAGE = """<html><body>
    <script>
    const define = (tag, html) => customElements.define(tag, class extends HTMLElement {
      connectedCallback() { this.attachShadow({mode: 'open'}).innerHTML = html(this); } });
    const sheet = '<style data-cadre>.transmitter { transform: none; }</style>';
    define('obc-transmitter', e => `<div class="chip"><span>${e.value}</span><span>${e.unit}</span></div><div>${e.idTag}</div>${sheet}`);
    define('obc-instrument-field', e => `<div class="value">${e.value}</div><div>${e.tag} ${e.unit}</div>${sheet}`);
    define('obc-pump', e => `<div>${e.tag}</div>`);
    const put = (type, tag, props, y) => {
      const box = document.createElement('div');
      box.setAttribute('data-component', type);
      box.style.cssText = `position:absolute;left:100px;top:${y}px;width:80px;height:30px`;
      const el = document.createElement(tag);
      Object.assign(el, props);
      box.appendChild(el); document.body.appendChild(box);
    };
    put('cadre.ob.readout', 'obc-transmitter', {value: 12.5, unit: 'm3/h', idTag: 'FT-101'}, 10);
    put('cadre.ob.instrumentfield', 'obc-instrument-field', {value: 47.5, setpoint: 50, tag: 'Raw water flow', unit: 'm3/h'}, 60);
    put('cadre.ob.instrumentfield', 'obc-instrument-field', {value: 3, tag: 'Level', unit: ''}, 110);
    put('cadre.ob.pump', 'obc-pump', {tag: 'P-101', on: true, speedInPercent: 80}, 160);
    </script></body></html>"""

    @classmethod
    def setUpClass(cls):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise unittest.SkipTest("Playwright is not installed in this interpreter")
        import glass
        cls.glass = glass
        cls.pw = sync_playwright().start()
        try:
            cls.browser = cls.pw.chromium.launch()
        except Exception as e:      # no browser installed
            cls.pw.stop()
            raise unittest.SkipTest(f"no browser: {e}")
        cls.page = cls.browser.new_page()
        cls.page.set_content(cls.PAGE)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def test_a_readout_is_found_by_its_identifier_and_read_by_its_value(self):
        s = self.glass.find_symbol(self.page, "FT-101")
        self.assertEqual((s["module"], s["value"]), ("cadre.ob.readout", 12.5))
        self.assertIn("12.5", s["text"])
        self.assertEqual((round(s["x"]), round(s["y"])), (140, 25))

    def test_a_field_is_found_by_its_label_and_unit_and_read_by_its_value_and_setpoint(self):
        s = self.glass.find_symbol(self.page, "Raw water flow m3/h")
        self.assertEqual((s["module"], s["value"], s["setpoint"]), ("cadre.ob.instrumentfield", 47.5, 50))
        self.assertIn("47.5", s["text"])
        s = self.glass.find_symbol(self.page, "Level")                     # no unit: the label alone
        self.assertEqual((s["module"], s["value"]), ("cadre.ob.instrumentfield", 3))
        self.assertIsNone(self.glass.find_symbol(self.page, "Raw water flow"))     # the caption is label and unit
        self.assertIsNone(self.glass.find_symbol(self.page, "FT-999"))

    def test_a_pump_is_still_found_by_its_tag_and_a_readout_by_no_other_property(self):
        s = self.glass.find_symbol(self.page, "P-101")
        self.assertEqual((s["module"], s["on"], s["speed"]), ("cadre.ob.pump", True, 80))
        self.assertIsNone(self.glass.find_symbol(self.page, "12.5"))        # a value is no identifier

    def test_the_text_a_symbol_prints_leaves_out_the_wrappers_style(self):
        s = self.glass.find_symbol(self.page, "FT-101")
        self.assertNotIn("transform", s["text"])
        self.assertTrue(s["text"].startswith("12.5"), s["text"])      # in document order: the value, its unit, the tag

    def test_gate_g10_reads_the_value_a_module_readout_prints(self):
        # F3 of gate G10 reads FIT-101's flow after a stop: the printed value, as the library's view prints it
        self.assertTrue(self.glass.value_of(self.page, "FT-101").startswith("12.5"))
        self.assertTrue(self.glass.value_of(self.page, "Raw water flow m3/h").startswith("47.5"))
        self.assertNotIn("transform", self.glass.value_of(self.page, "FT-101"))
        at = self.page.evaluate(self.glass.READOUT_AT, "FT-101")
        self.assertEqual([round(v) for v in at], [140, 25])

    def test_gate_g10_finds_a_module_readout_by_its_tag(self):
        at = self.page.evaluate(self.glass.READOUT_AT, "FT-101")
        self.assertEqual([round(v) for v in at], [140, 25])
        self.assertIsNone(self.page.evaluate(self.glass.READOUT_AT, "FT-999"))


# ---------------------------------------------------------------------------------------------------------
# The writes of the eng02 ASM project that no gate had pressed (COB-158, COB-159): the page's command buttons,
# the generator's Service completed on Config, and the Config rows of the asm faceplates (W19)
# ---------------------------------------------------------------------------------------------------------
def asm_plan(**kw) -> dict:
    return walk.build_plan([load(FIXTURES / "asm-screen.json")], devices=load(FIXTURES / "asm-devices.json"),
                           render="module", faceplate="asm", **kw)


def parts_plan() -> dict:
    return walk.build_plan([load(FIXTURES / "page-parts.json")], render="module")


class AsmWritesPlanTests(unittest.TestCase):
    """The plan reaches the asm faceplates' Config rows, the generator's service command and a page's pulse button."""

    def test_a_config_row_is_an_entry_on_the_config_tab_within_the_models_bounds(self):
        plan = asm_plan()
        c = next(s for s in plan["steps"] if s["group"] == "C" and s["path"] == "W19")
        self.assertEqual((c["type"], c["device"], c["tab"], c["field"], c["format"], c["bounds"]),
                         ("entry", "SQ-1", "Config", "Excess run time alarm", "0", [0, 1440]))
        self.assertEqual(c["tag"], "[default]cadre_hmi_asmtest/SQ1/cfg/runTimeSP")
        r = next(s for s in plan["steps"] if s.get("mirrors") == c["id"])
        self.assertEqual((r["session"], r["path"], r["field"]), ("anonymous", "W19", "Excess run time alarm"))
        self.assertNotIn("W19", [n.get("path") for n in plan["notReached"]])

    def test_a_config_row_is_planned_for_the_asm_style_only(self):
        model = load(FIXTURES / "asm-devices.json")
        for dev in model["devices"]:   # a device's own style wins over the project's
            dev.pop("faceplate", None)
        plan = walk.build_plan([load(FIXTURES / "asm-screen.json")], devices=model, render="module",
                               faceplate="openbridge")
        self.assertEqual([s for s in plan["steps"] if s.get("path") == "W19"], [])

    def test_a_device_with_modes_is_listed_not_walked_for_its_config_rows(self):
        model = load(FIXTURES / "asm-devices.json")
        sq = next(d for d in model["devices"] if d["id"] == "SQ1")
        sq["modes"] = [{"value": 0, "name": "Remote auto", "owner": "program"},
                       {"value": 2, "name": "Out of service", "owner": "maintenance"}]
        plan = walk.build_plan([load(FIXTURES / "asm-screen.json")], devices=model, render="module", faceplate="asm")
        self.assertEqual([s for s in plan["steps"] if s.get("path") == "W19"], [])
        why = next(n for n in plan["notReached"] if n.get("path") == "W19" and n.get("device") == "SQ-1")["why"]
        self.assertIn("maintenance mode", why)

    def test_service_completed_stands_on_the_config_tab_and_the_other_pulses_on_home(self):
        plan = asm_plan()
        tabs = {s["button"]: s["tab"] for s in plan["steps"] if s["group"] == "C" and s["path"] == "W18"}
        self.assertEqual(tabs["Service done"], "Config")
        self.assertEqual({tabs[b] for b in ("Start generator", "Stop generator", "Reset generator", "Put in service")},
                         {"Home"})
        mirror = next(s for s in plan["steps"] if s["group"] == "R" and s["path"] == "W18" and s["tab"] == "Config")
        self.assertEqual(mirror["controls"], [{"button": "Service done", "sibling": None}])

    def test_a_pulse_button_of_a_page_is_a_step_and_a_refusal(self):
        plan = parts_plan()
        c = next(s for s in plan["steps"] if s.get("type") == "page-pulse")
        self.assertEqual((c["group"], c["session"], c["path"], c["route"], c["button"], c["question"], c["ms"]),
                         ("C", "signed", "W18", "/page-parts", "PLANTWIDE RESET", "Reset the plant?", 5000))
        self.assertEqual(c["tag"], "[default]cadre_hmi_parts/sim/reset")
        r = next(s for s in plan["steps"] if s.get("mirrors") == c["id"])
        self.assertEqual((r["type"], r["group"], r["session"], r["button"], r["tag"]),
                         ("page-refusal", "R", "anonymous", "PLANTWIDE RESET", c["tag"]))
        self.assertEqual([s["button"] for s in plan["steps"] if s.get("type") == "page-pulse"], ["PLANTWIDE RESET"])

    def test_a_route_or_faceplate_button_is_no_pulse(self):
        plan = parts_plan()   # the page also holds buttons of the types faceplate and route
        self.assertEqual(len([s for s in plan["steps"] if s.get("type") == "page-pulse"]), 1)

    def test_the_plans_are_deterministic(self):
        self.assertEqual(walk.plan_text(asm_plan()), walk.plan_text(asm_plan()))
        self.assertEqual(walk.plan_text(parts_plan()), walk.plan_text(parts_plan()))


class PagePulseRunnerTests(RunnerCase):
    """The page button's rules of evidence, with a glass and a gateway that are stubs."""

    TAG = "[default]cadre_hmi_pilot/SQ1/trigger"

    def setUp(self):
        super().setUp()
        self.glass.page_texts = ["PLANTWIDE RESET", "NEXT >"]
        self.glass.page_disabled = {}
        self.glass.question = False
        self.step_c = {"id": "C-90", "group": "C", "session": "signed", "path": "W18", "device": "", "kind": "page",
                       "route": "/supply", "type": "page-pulse", "button": "PLANTWIDE RESET",
                       "question": "Reset the plant?", "tag": self.TAG, "ms": 5000}
        self.step_r = {"id": "R-90", "group": "R", "session": "anonymous", "mirrors": "C-90", "path": "W18",
                       "device": "", "kind": "page", "route": "/supply", "type": "page-refusal",
                       "button": "PLANTWIDE RESET", "tag": self.TAG}
        self.reads = {"n": 0, "armed": False}
        self.plant = lambda n: False       # the tag after n reads since Confirm
        real = self.gw.export_tags

        def export(provider, path):
            node = real(provider, path)
            if self.reads["armed"] and path.endswith("SQ1/trigger"):
                self.reads["n"] += 1
                node["value"] = self.plant(self.reads["n"])
            return node
        self.gw.export_tags = export
        put = self.gw.import_tags

        def import_tags(provider, path, doc):
            self.reads["armed"] = False   # the plant is the stub's: an import of the definition of before ends it
            return put(provider, path, doc)
        self.gw.import_tags = import_tags
        self.glass.on_page_click = self.press

    def press(self, caption):
        g = self.glass
        if caption == "PLANTWIDE RESET":
            g.page_texts, g.question = ["Confirm", "Cancel", "NEXT >"], True
        elif caption == "Cancel":
            g.page_texts, g.question = ["PLANTWIDE RESET", "NEXT >"], False
        elif caption == "Confirm":
            g.page_texts, g.question = ["PLANTWIDE RESET", "NEXT >"], False
            self.reads.update(n=0, armed=True)

    def held_for(self, first: int, last: int):
        """The tag reads true from read `first` to read `last`, then false."""
        self.plant = lambda n: first <= n <= last

    def test_a_pulse_button_asks_then_holds_the_tag_true_and_lets_it_go(self):
        self.held_for(1, 3)
        self.w.run_step(self.step_c)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["evidence"], "glass and tag")
        self.assertEqual(self.glass.clicked, ["PLANTWIDE RESET", "Cancel", "PLANTWIDE RESET", "Confirm"])
        self.assertTrue(row["glass"]["asked"]["question"])
        self.assertIn("held true for", row["tag"])
        self.assertFalse(self.node("SQ1/trigger")["value"])

    def test_a_press_that_writes_before_confirm_fails(self):
        self.node("SQ1/trigger")["value"] = False
        real = self.glass.on_page_click

        def writes(caption):
            real(caption)
            if caption == "PLANTWIDE RESET":
                self.node("SQ1/trigger")["value"] = True
        self.glass.on_page_click = writes
        self.w.run_step(self.step_c)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("the press wrote", self.w.rows[-1]["detail"])

    def test_a_pulse_held_far_shorter_than_its_length_fails(self):
        self.held_for(1, 1)
        self.w.run_step(self.step_c)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("not about 5 s", self.w.rows[-1]["detail"])

    def test_a_pulse_that_never_arrives_fails(self):
        self.held_for(99, 99)
        self.w.run_step(self.step_c)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("was not read true", self.w.rows[-1]["detail"])

    def test_a_tag_nothing_lets_go_is_imported_back_and_fails(self):
        self.held_for(1, 10 ** 6)
        self.w.run_step(self.step_c)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("not let go", row["detail"])
        self.assertIn("definition of before was imported", row["detail"])
        self.assertFalse(self.node("SQ1/trigger")["value"])

    def test_a_disabled_button_fails_the_signed_step(self):
        self.glass.page_disabled = {"PLANTWIDE RESET": True}
        self.w.run_step(self.step_c)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("disabled", self.w.rows[-1]["detail"])
        self.assertEqual(self.glass.clicked, [])

    def test_a_button_that_reads_a_refusal_afterwards_fails(self):
        self.held_for(1, 3)
        real = self.glass.on_page_click

        def refuses(caption):
            real(caption)
            if caption == "Confirm":
                self.glass.page_texts = ["Refused: not a command of this project", "NEXT >"]
        self.glass.on_page_click = refuses
        self.w.run_step(self.step_c)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("Refused", self.w.rows[-1]["detail"])

    # -- with nobody signed in ----------------------------------------------------------------------------
    def refusal_glass(self):
        g = self.glass
        g.page_disabled = {"PLANTWIDE RESET": True}

        def crafted(caption):
            if caption == "PLANTWIDE RESET":
                g.page_texts = ["Confirm", "Cancel", "NEXT >"]
            elif caption == "Confirm":
                g.page_texts = ["Refused: sign in with the Administrator role", "NEXT >"]
        g.on_page_crafted = crafted

    def test_a_page_button_is_refused_by_the_gateway_through_its_handlers(self):
        self.refusal_glass()
        self.w.run_step(self.step_r)
        row = self.w.rows[-1]
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["refused_by"], "the gateway")
        self.assertEqual(row["evidence"], "glass and control and tag")
        self.assertEqual([c for c in self.glass.crafted], [("page call", "PLANTWIDE RESET"), ("page call", "Confirm")])

    def test_a_page_button_whose_handlers_get_no_answer_fails(self):
        self.refusal_glass()
        self.glass.on_page_crafted = lambda caption: None
        self.w.run_step(self.step_r)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("nothing shows that the gateway refused", self.w.rows[-1]["detail"])

    def test_a_page_button_whose_crafted_call_writes_fails_on_the_tag(self):
        self.refusal_glass()
        real = self.glass.on_page_crafted

        def writes(caption):
            real(caption)
            self.node("SQ1/trigger")["value"] = True
        self.glass.on_page_crafted = writes
        self.w.run_step(self.step_r)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("the tag went from", self.w.rows[-1]["detail"])

    def test_an_enabled_page_button_fails_the_refusal(self):
        self.refusal_glass()
        self.glass.page_disabled = {}
        self.w.run_step(self.step_r)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertIn("enabled", self.w.rows[-1]["detail"])

    def test_a_handler_the_client_does_not_hold_is_no_proof_of_the_gateway(self):
        self.refusal_glass()
        self.glass.handler = "no handler"
        self.w.run_step(self.step_r)
        self.assertFalse(self.w.rows[-1]["ok"])
        self.assertEqual(self.w.rows[-1]["refused_by"], "the client only")



# -- the trip (COB-204) ------------------------------------------------------------------------------
WTP_SCREENS = ("overview", "intake", "filtration", "disinfection")
P502 = "cadre_hmi_wtp/P502"


def wtp_trip_tags() -> dict:
    """The sample's tags with P-502's fault, the source of its latched trip C01, at rest and without its
    alarm, so that the walk may raise it."""
    return edited(load(WTP / "tags.json"), f"{P502}/fault", value=False, alarms=[])


def wtp_trip_plan(tags: dict | None = None, **kw) -> dict:
    return walk.build_plan([load(WTP / f"{n}.json") for n in WTP_SCREENS],
                           tags=tags if tags is not None else wtp_trip_tags(), **kw)


class TripExpressionTests(unittest.TestCase):
    """The reading of a condition's `ok` (`ok_expression`, `trip_source`): a parse, never an evaluation."""

    def test_the_trip_value_is_read_from_the_expression(self):
        for text, trip in (("!coalesce({[default]a/x}, false)", True),
                           ("coalesce(!coalesce({[default]a/x}, false), false)", True),
                           ("coalesce({[default]a/x}, true)", False),
                           ("!(!{[default]a/x} || false)", False)):
            self.assertEqual(walk.trip_source("[default]a/ilk/C01/ok", {"valueSource": "expr", "expression": text}),
                             ("[default]a/x", trip), text)

    def test_a_relative_reference_and_a_memory_ok(self):
        self.assertEqual(walk.trip_source("[default]a/d/ilk/C01/ok",
                                          {"valueSource": "expr", "expression": "!{[.]../../src}"}),
                         ("[default]a/d/src", True))
        self.assertEqual(walk.trip_source("[default]a/ilk/C01/ok", {"valueSource": "memory", "value": True}),
                         ("[default]a/ilk/C01/ok", False))

    def test_what_the_walk_does_not_read_is_said(self):
        for text, why in (("coalesce({[default]a/l}, 50) < 95", "does not read"),
                          ("{[default]a/x} && {[default]a/y}", "references 2 tags"),
                          ("__import__('os').system('x') || {[default]a/x}", "does not read"),
                          ("{[default]a/x} || true", "does not turn"),
                          ("coalesce({[default]a/x}, false", "not one the walk reads")):
            got = walk.trip_source("[default]a/ilk/C01/ok", {"valueSource": "expr", "expression": text})
            self.assertIsInstance(got, str, text)
            self.assertIn(why, got, text)
        self.assertIn("names no provider",
                      walk.trip_source("[default]a/ilk/C01/ok", {"valueSource": "expr", "expression": "!{a/x}"}))


class TripPlanTests(unittest.TestCase):
    """`build_plan(trip=True)`: the first device of a kind with interlocks whose latched trip the walk can raise."""

    def test_the_trip_of_the_first_device_that_can_be_raised(self):
        steps = [s for s in wtp_trip_plan(trip=True)["steps"] if s["type"] == "trip"]
        self.assertEqual(len(steps), 1)
        s = steps[0]
        self.assertEqual((s["group"], s["path"], s["device"], s["kind"], s["tab"]),
                         ("C", "W11", "P-502", "pump", "Interlocks"))
        self.assertEqual((s["condition"], s["text"], s["source"], s["trip"]),
                         ("C01", "Pump fault clear", f"[default]{P502}/fault", True))
        self.assertEqual(s["tag"], f"[default]{P502}/ilk/resetAt")
        self.assertEqual((s["button"], s["head"], s["cleared"]), ("Reset", None, "A latched trip has cleared"))
        self.assertEqual(s["lamps"], {"met": "Met", "tripped": "Not met", "latched": "Latched"})

    def test_the_asm_style_reads_its_header_on_its_interlock_tab(self):
        s = next(s for s in wtp_trip_plan(trip=True, faceplate="asm")["steps"] if s["type"] == "trip")
        self.assertEqual((s["tab"], s["head"]), ("Interlock", "Interlocked"))

    def test_the_trip_reaches_w11(self):
        plan = wtp_trip_plan(trip=True)
        self.assertNotIn("W11", [n.get("path") for n in plan["notReached"]])
        without = wtp_trip_plan()
        self.assertFalse([s for s in without["steps"] if s["type"] == "trip"])
        self.assertIn("--trip", next(n["why"] for n in without["notReached"] if n.get("path") == "W11"))

    def test_why_no_trip_could_be_raised(self):
        plan = wtp_trip_plan(load(WTP / "tags.json"), trip=True)
        self.assertFalse([s for s in plan["steps"] if s["type"] == "trip"])
        why = next(n["why"] for n in plan["notReached"] if n.get("path") == "W11" and n.get("kind") == "pump")
        self.assertIn("P-101: C02: its expression holds", why)
        self.assertIn("P-502: C01: its source [default]cadre_hmi_wtp/P502/fault carries an alarm", why)

    def test_a_source_outside_the_plans_folders_or_at_its_trip_value_is_refused(self):
        tags = edited(wtp_trip_tags(), f"{P502}/ilk/C01/ok",
                      expression="!coalesce({[default]elsewhere/estop}, false)")
        source = {"name": "elsewhere", "tagType": "Folder", "tags": [
            {"name": "estop", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Boolean", "value": False}]}
        plan = wtp_trip_plan(tags, trip=True, source_tags=[(source, "")])
        self.assertIn("lies outside", next(n["why"] for n in plan["notReached"] if n.get("path") == "W11"))
        tripped = edited(wtp_trip_tags(), f"{P502}/fault", value=True, alarms=[])
        self.assertIn("rests at the value that trips it",
                      next(n["why"] for n in wtp_trip_plan(tripped, trip=True)["notReached"] if n.get("path") == "W11"))

    def test_a_trip_that_does_not_latch_is_not_planned(self):
        tags = edited(wtp_trip_tags(), f"{P502}/ilk/C01/latched", value=False)
        self.assertIn("C01 does not latch",
                      next(n["why"] for n in wtp_trip_plan(tags, trip=True)["notReached"] if n.get("path") == "W11"))

    def test_the_plan_is_deterministic(self):
        self.assertEqual(walk.plan_text(wtp_trip_plan(trip=True)), walk.plan_text(wtp_trip_plan(trip=True)))


class TripGlass(StubGlass):
    """The Interlocks tab of P-502 over the fake gateway: the trip latches while the fault is raised, and
    a reset later than the last one seen releases it (the library's `resetSeen`, a self reference)."""

    def __init__(self, gw, text: str, latches: bool = True, reset_writes: bool = True):
        super().__init__()
        self.gw, self.text, self.latches, self.reset_writes = gw, text, latches, reset_writes
        self.latched, self.seen_reset = False, 0
        self.disabled["Reset"] = False
        self.on_click = self.clicked_on

    def _value(self, member):
        return self.gw.nodes[f"{P502}/{member}"].get("value")

    def _update(self):
        if self._value("fault") is True and self.latches:
            self.latched = True
        reset = self._value("ilk/resetAt") or 0
        if reset > self.seen_reset:
            self.seen_reset = reset
            if self._value("fault") is not True:
                self.latched = False

    def clicked_on(self, caption):
        if caption == "Reset" and self.reset_writes:
            self.gw.nodes[f"{P502}/ilk/resetAt"]["value"] = 1_900_000_000_000

    def interlock_lamp(self, page, text):
        self._update()
        if text != self.text:
            return None
        return "Not met" if self._value("fault") is True else "Latched" if self.latched else "Met"

    def dock_text(self, page):
        self._update()
        held = self._value("fault") is True or self.latched
        return " ".join(["P-502", "Interlocked" if held else "",
                         "A latched trip has cleared" if self.latched and self._value("fault") is not True else ""])


class TripRunnerTests(RunnerCase):
    """`Walk.trip` against a stub glass and the fake gateway: what must fail fails, and nothing is left."""

    def setUp(self):
        super().setUp()
        self.gw = FakeGateway(wtp_trip_tags())
        self.tags = walk.Tags(["[default]cadre_hmi_wtp"], deploy=self.gw)
        self.step = next(s for s in wtp_trip_plan(trip=True)["steps"] if s["type"] == "trip")
        self.w.tags = self.tags

    def walk_with(self, **kw):
        self.glass = TripGlass(self.gw, self.step["text"], **kw)
        self.w.g = self.glass
        self.w.trip(self.step)
        return self.w.rows[-1]

    def assert_left_as_found(self):
        self.assertIs(self.gw.nodes[f"{P502}/fault"]["value"], False)
        self.assertEqual(self.gw.nodes[f"{P502}/ilk/resetAt"]["value"], 0)
        self.assertEqual(self.tags.before, {})
        self.assertFalse(self.glass.latched)

    def test_a_trip_that_latches_and_is_reset_passes(self):
        row = self.walk_with()
        self.assertTrue(row["ok"], row["detail"])
        self.assertEqual(row["evidence"], "glass and tag")
        self.assertEqual([g["row"] for g in row["glass"]], ["Met", "Not met", "Latched", "Met"])
        self.assertEqual(self.glass.clicked, ["Reset"])
        self.assertEqual(row["tag"]["ilk/resetAt"], [0, 1_900_000_000_000])
        self.assert_left_as_found()

    def test_a_trip_that_does_not_latch_fails_and_leaves_nothing(self):
        row = self.walk_with(latches=False)
        self.assertFalse(row["ok"])
        self.assertIn("no latch", row["detail"])
        self.assertEqual(self.glass.clicked, [])
        self.assert_left_as_found()

    def test_a_reset_that_writes_nothing_fails_and_the_latch_is_cleared_by_an_import(self):
        row = self.walk_with(reset_writes=False)
        self.assertFalse(row["ok"])
        self.assertIn("the write did not arrive", row["detail"])
        self.assertIn("the latch cleared by an import of ilk/resetAt", row["detail"])
        self.assert_left_as_found()

    def test_a_disabled_reset_fails_and_the_latch_is_cleared(self):
        self.glass = TripGlass(self.gw, self.step["text"])
        self.glass.disabled["Reset"] = True
        self.w.g = self.glass
        self.w.trip(self.step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("the button Reset is disabled", row["detail"])
        self.assert_left_as_found()

    def test_a_source_found_at_its_trip_value_is_not_touched(self):
        self.gw.nodes[f"{P502}/fault"]["value"] = True
        row = self.walk_with()
        self.assertFalse(row["ok"])
        self.assertIn("already holds its trip value", row["detail"])
        self.assertEqual(self.gw.imports, [])

    def test_the_negative_control_that_writes_nothing_fails(self):
        self.w.skip_write = True
        row = self.walk_with()
        self.assertFalse(row["ok"])
        self.assertIn("with the source raised the row reads 'Met'", row["detail"])
        self.assert_left_as_found()   # the definitions kept are imported back as they were

    def test_the_runner_knows_the_step_type(self):
        self.assertEqual(walk.Walk.STEP_TYPES["trip"], "trip")

    def test_the_asm_header_must_read_interlocked_while_held(self):
        self.step = next(s for s in wtp_trip_plan(trip=True, faceplate="asm")["steps"] if s["type"] == "trip")
        self.assertTrue(self.walk_with()["ok"])
        self.w.rows.clear()
        self.glass = TripGlass(self.gw, self.step["text"])
        self.glass.dock_text = lambda page: "P-502"   # a header that never says the device is held
        self.w.g = self.glass
        self.w.trip(self.step)
        row = self.w.rows[-1]
        self.assertFalse(row["ok"])
        self.assertIn("the head not held", row["detail"])
        self.assert_left_as_found()


class TripRelatchGlass(TripGlass):
    """A latch that comes back when ilk/resetAt is put back below the reset it has seen (the review's case:
    the put-back re-latches). `stubborn`: no later reset releases the latch either."""

    relatches = True

    def __init__(self, gw, text: str, stubborn: bool = False, **kw):
        super().__init__(gw, text, **kw)
        self.stubborn = stubborn

    def _update(self):
        super()._update()
        if self.stubborn and self._value("fault") is not True and self._value("ilk/resetAt") != 0:
            self.latched = True
        if self.relatches and self._value("ilk/resetAt") == 0 and self.seen_reset > 0:
            self.latched = True

    def clicked_on(self, caption):   # a reset time the clock of the test (a few thousand ms) has passed
        if caption == "Reset" and self.reset_writes:
            self.gw.nodes[f"{P502}/ilk/resetAt"]["value"] = 5


class TripLeftBehindTests(TripRunnerTests):
    """The final restore of ilk/resetAt (review finding 8): a put-back that latches the trip again is cleared
    once more and the latch read again; a trip still latched is an unrestored fault."""

    def walk_relatch(self, **kw):
        self.glass = TripRelatchGlass(self.gw, self.step["text"], **kw)
        self.w.g = self.glass
        self.w.trip(self.step)
        return self.w.rows[-1]

    def test_a_put_back_that_latches_again_is_cleared_once_more(self):
        row = self.walk_relatch()
        self.assertFalse(row["ok"])
        self.assertIn("latched again", row["detail"])
        self.assertIn("cleared once more", row["detail"])
        self.assertFalse(self.glass.latched)
        self.assertEqual([u for u in self.tags.unrestored if "still latched" in u["why"]], [])

    def test_a_trip_still_latched_after_the_second_clear_is_recorded_unrestored(self):
        row = self.walk_relatch(stubborn=True)
        self.assertFalse(row["ok"])
        self.assertIn("still latched", row["detail"])
        left = [u for u in self.tags.unrestored if "still latched" in u["why"]]
        self.assertEqual([u["tag"] for u in left], [f"[default]{P502}/ilk/resetAt"])
        rep = walk.summarise(self.plan, [{"id": "C-trip", "group": "C", "ok": True, "evidence": "glass"}], [], True,
                             [], self.tags, login_given=True)
        self.assertFalse(rep["ok"])
        self.assertTrue(rep["unrestored"])


class TripResetTypeTests(unittest.TestCase):
    """The data type of ilk/resetAt is read before the walk writes milliseconds into it (review finding 8)."""

    def test_a_reset_tag_that_cannot_take_milliseconds_is_refused_with_its_type(self):
        for kind in ("Int4", "Boolean", "String", "Int2"):
            tags = edited(wtp_trip_tags(), f"{P502}/ilk/resetAt", dataType=kind)
            plan = wtp_trip_plan(tags, trip=True)
            self.assertFalse([s for s in plan["steps"] if s["type"] == "trip"], kind)
            why = next(n["why"] for n in plan["notReached"] if n.get("path") == "W11" and n.get("kind") == "pump")
            self.assertIn(f"ilk/resetAt is a {kind}", why)
            self.assertIn("does not take an integer of milliseconds", why)

    def test_int8_and_float8_are_accepted(self):
        for kind in ("Int8", "Float8"):
            tags = edited(wtp_trip_tags(), f"{P502}/ilk/resetAt", dataType=kind)
            self.assertTrue([s for s in wtp_trip_plan(tags, trip=True)["steps"] if s["type"] == "trip"], kind)


class UserMenuFake:
    """A page for `glass._open_user_menu`: a top bar whose menu popup offers `entries` once opened, a body
    that shows the text 'Sign in' outside any popup, and a record of every click."""

    def __init__(self, entries=("Sign in",), coords=3, icons=3, body_text=True):
        self.entries, self.coords, self.icons, self.body_text = set(entries), coords, icons, body_text
        self.opened, self.clicks = False, []
        self.mouse = self.keyboard = self

    def locator(self, selector):
        return _UserMenuLoc(self, selector)

    def evaluate(self, script):
        return [[1500 + 40 * i, 20] for i in range(self.icons)]

    def wait_for_timeout(self, ms):
        pass

    def press(self, key):   # keyboard.press
        self.opened = False

    def click(self, x, y):   # mouse.click
        self.clicks.append(("icon", x, y))
        self.opened = True


class _UserMenuLoc:
    COORD = '[data-component="ia.container.coord"]'

    def __init__(self, page, selector, scoped=False, nth=None):
        self.page, self.selector, self.scoped, self.nth_i = page, selector, scoped, nth

    @property
    def first(self):
        return self

    def locator(self, selector, **kw):
        return _UserMenuLoc(self.page, selector, scoped=self.selector == ".ia_popup" or self.scoped)

    def nth(self, i):
        return _UserMenuLoc(self.page, self.selector, self.scoped, i)

    def _caption(self):
        import re
        found = re.search(r'text-is\("([^"]+)"\)', self.selector)
        return found.group(1) if found else "Sign in"

    def count(self):
        if self.selector == self.COORD:
            return self.page.coords
        return 1 if self.is_visible() else 0

    def is_visible(self):
        if not self.scoped:   # the page behind the popup shows the text always
            return self.page.body_text
        return self.page.opened and self._caption() in self.page.entries

    def click(self):
        if self.selector == self.COORD:
            self.page.clicks.append(("coord", self.nth_i))   # this frame's third container opens nothing
        else:
            self.page.clicks.append(("entry", self._caption(), self.scoped))


class UserMenuTests(unittest.TestCase):
    """`glass._open_user_menu` (review finding 9): the entry is looked for in the opened popup alone, and the
    icon fallback is clicked only in a top bar of the three menu icons."""

    def setUp(self):
        import glass
        self.glass = glass

    def test_the_entry_is_found_in_the_popup_opened_by_the_last_icon(self):
        page = UserMenuFake(coords=0)
        self.assertTrue(self.glass._open_user_menu(page, "Sign in"))
        self.assertEqual(page.clicks[0][0], "icon")
        self.assertEqual(page.clicks[-1], ("entry", "Sign in", True))

    def test_a_sign_in_text_of_the_page_behind_is_never_clicked(self):
        page = UserMenuFake(entries=(), coords=0)
        self.assertFalse(self.glass._open_user_menu(page, "Sign in"))
        self.assertFalse([c for c in page.clicks if c[0] == "entry"])
        self.assertIn("offers no 'Sign in'", self.glass.SIGN_IN_WHY)

    def test_a_top_bar_without_the_three_menu_icons_is_not_clicked_and_says_why(self):
        page = UserMenuFake(coords=0, icons=1)
        self.assertFalse(self.glass._open_user_menu(page, "Sign in"))
        self.assertEqual(page.clicks, [])
        self.assertIn("shows 1 icons, not the three menu icons", self.glass.SIGN_IN_WHY)
        self.assertIn("the user menu was not found", self.glass.SIGN_IN_WHY)

    def test_the_summary_names_why_the_login_did_not_sign_in(self):
        rep = walk.summarise({"render": "stock", "counts": {}}, [], [], False, [], login_given=True,
                             why="the top bar shows 0 icons")
        self.assertIn("the top bar shows 0 icons", rep["note"])


if __name__ == "__main__":
    unittest.main()
