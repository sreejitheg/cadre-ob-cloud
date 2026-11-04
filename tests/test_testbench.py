"""Tests of the component test page (L4 item 10, `tools/hmi/testbench.py`, `screen.py --component-test`).

Run from the repository root:  python -m unittest discover -s tests
The page is built from `library/contracts.json` and `library/profile.json` alone; the sample project of the gate run
is `tests/fixtures/asm-screen.json` with its device model (synthetic names). Nothing here needs the gateway.
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

from hmi import alarms, framework, gates, library, library_profile, scripts, screen, testbench  # noqa: E402
from hmi import parent as par  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
TAG_ROOT = "[default]cadre_hmi_asmtest"
FOLDER = testbench.FOLDER


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def walk(node):
    yield node
    for c in node.get("children") or []:
        yield from walk(c)


def stated(bench, s):
    """The parameters a symbol states: its params and the starting values of the gallery tags it binds (L5)."""
    return {**s.get("params", {}), **bench.gallery.get(s["id"], {})}


def leaves(folder, path=""):
    for t in folder.get("tags", []):
        here = f"{path}/{t['name']}" if path else t["name"]
        if t["tagType"] == "Folder":
            yield from leaves(t, here)
        else:
            yield here, t


class PageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = screen.load_contracts()
        cls.prof = library_profile.build(cls.contracts)
        cls.bench = testbench.build(cls.contracts, cls.prof, TAG_ROOT)
        cls.desc = cls.bench.descriptor

    # ---- the page ------------------------------------------------------------------------
    def test_it_is_a_level_four_support_page_with_the_agreed_route_and_label(self):
        s = self.desc["screen"]
        self.assertEqual((s["route"], s["layout"], s["navLabel"], s["level"], s.get("nav", True)),
                         ("/component-test", "diagram", "Tools: Component test", "Level 4 support", True))
        self.assertNotIn("node", s)                          # a support page belongs to no node of the plant
        self.assertEqual((self.desc["toolbar"], self.desc["tagModel"]), (True, "external"))
        self.assertEqual(screen.schema_errors([self.desc], ["bench"]), [])   # G0

    def test_it_agrees_with_the_catalogue_it_came_from(self):
        self.assertEqual(testbench.check(self.desc, self.contracts), [])
        # a parameter a contract lacks is named, never dropped
        bad = copy.deepcopy(self.desc)
        bad["symbols"][0]["params"]["nonsense"] = 1
        self.assertIn("nonsense", " ".join(testbench.check(bad, self.contracts)))
        bad = copy.deepcopy(self.desc)
        bad["symbols"].append(dict(bad["symbols"][0]))
        self.assertIn("used twice", " ".join(testbench.check(bad, self.contracts)))

    def test_every_kind_of_the_profile_and_the_generator_set_is_drawn(self):
        drawn = testbench.kinds_drawn(self.desc)
        self.assertEqual(set(self.prof["kinds"]) - drawn, set())
        self.assertIn("genset", drawn)
        titles = {s["label"] for s in self.desc["sections"]}
        for kind in self.prof["kinds"]:
            self.assertTrue(any(t.lower().startswith(kind) for t in titles), kind)   # a section for each kind

    def test_a_kind_the_library_gains_is_drawn_with_its_state_and_its_booleans(self):
        # nothing is listed by name for a kind the table of extras lacks: its state both ways and its marks follow
        contracts = copy.deepcopy(self.contracts)
        contracts["Automation/Pump"]["params"]["newFlag"] = False
        cases = testbench.kind_cases("pump", contracts["Automation/Pump"], self.prof)
        states = [c.params["on"] for c in cases if "on" in c.params]
        self.assertIn(True, states)
        self.assertIn(False, states)

    def test_the_contracts_booleans_and_enumerations_are_each_stated_off_their_default(self):
        by_view: dict[str, list] = {}
        for s in self.desc["symbols"]:
            by_view.setdefault(screen.view_of(s), []).append(s)
        skip = {"deviceId", "deviceLabel", "deviceKind", "speed", "value", "picture", "medium", "source", "tag", "label"}
        # the marks all automation symbols draw alike are shown on each kind; the generator's set has its own few
        for view, syms in by_view.items():
            if view == screen.GENSET_VIEW:
                continue
            for k, default in self.contracts[view]["params"].items():
                if k in skip or k.startswith(("alertFrame", "badgeControl", "badgeInterlock", "badgeCommandLocked")):
                    continue
                if isinstance(default, bool):
                    if view == "Automation/Indicator" and k in ("showStatus", "alert"):
                        continue   # a lamp draws no status row and no frame (L5)
                    if view in ("Automation/Generator", "Automation/Indicator") and k in ("hasSpeed",):
                        continue   # a symbol with no speed reading
                    if view in ("Automation/Valve", "Automation/AnalogValve", "Automation/Damper", "Automation/Filter",
                                "Automation/Switch", "Automation/Generator", "Automation/Indicator") and k == "hasSpeed":
                        continue
                    self.assertTrue(any(stated(self.bench, s).get(k, default) != default for s in syms), (view, k))

    def test_every_alert_status_and_mode_and_every_badge_is_shown(self):
        syms = {s["id"]: stated(self.bench, s) for s in self.desc["symbols"]}
        pairs = {(p["alertFrameStatus"], p["alertFrameMode"]) for p in syms.values() if p.get("alert")}
        for st in library.ALERT_COLOURS:
            for m in testbench.ALERT_MODE:
                self.assertIn((st, m), pairs)
        for b in library.CONTROL_BADGES:
            self.assertTrue(any(p.get("badgeControl") == b for p in syms.values()), b)
        for b in testbench.BADGE_INTERLOCK:
            self.assertTrue(any(p.get("badgeInterlock") == b for p in syms.values()), b)
        for flag in ("badgeDuty", "outOfService", "progress", "activated"):
            self.assertTrue(any(p.get(flag) for p in syms.values()), flag)

    def test_a_pipe_for_each_medium_and_each_size_which_flow(self):
        pipes = self.desc["pipes"]
        self.assertEqual({p["medium"] for p in pipes}, set(screen.MEDIUM_VAR))
        self.assertEqual({p["size"] for p in pipes if "size" in p}, {"small", "medium", "large", "xl"})
        for p in pipes:   # a loose source to a loose sink, or ends at the test pump and valve
            for end in ("from", "to"):
                self.assertTrue("ref" in p[end] or p[end].get("end") in ("arrow-in", "arrow-out"), p["id"])

    def test_the_genset_is_shown_in_several_box_sizes(self):
        sets = [s for s in self.desc["symbols"] if screen.view_of(s) == screen.GENSET_VIEW and s["id"].startswith("S_")]
        self.assertGreaterEqual(len({(s["w"], s["h"]) for s in sets}), 4)
        self.assertEqual({stated(self.bench, s)["on"] for s in sets}, {True, False})

    def test_the_readout_stretch_is_shown_both_ways_in_equal_boxes(self):
        ro = [s for s in self.desc["symbols"] if s["kind"] == "readout" and "stretch" in s["params"]]
        self.assertEqual({s["params"]["stretch"] for s in ro}, {True, False})
        self.assertEqual(len({(s["w"], s["h"]) for s in ro}), 1)

    # ---- the layout ----------------------------------------------------------------------
    def test_every_item_lies_in_its_section_and_sections_do_not_overlap(self):
        boxes = self.desc["sections"]
        W, H = self.desc["screen"]["width"], self.desc["screen"]["height"]
        for a in boxes:
            self.assertTrue(0 <= a["x"] and a["x"] + a["w"] <= W and 0 <= a["y"] and a["y"] + a["h"] <= H, a["id"])
            for b in boxes:
                if a is not b:
                    apart = a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"] \
                        or a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"]
                    self.assertTrue(apart, (a["id"], b["id"]))
        for array in ("labels", "buttons"):
            for it in self.desc[array]:
                self.assertTrue(any(b["x"] <= it["x"] and it["x"] + it["w"] <= b["x"] + b["w"] + 1
                                    and b["y"] <= it["y"] and it["y"] + it["h"] <= b["y"] + b["h"] + 1
                                    for b in boxes), (array, it["id"]))

    def test_shifting_moves_loose_pipe_ends_and_leaves_a_symbol_end_alone(self):
        pipe = {"id": "p", "from": {"x": 1, "y": 2, "end": "arrow-in"}, "to": {"ref": "S", "side": "left"},
                "via": [[3, 4]]}
        out = testbench.shifted(pipe, 10, 20)
        self.assertEqual((out["from"]["x"], out["from"]["y"], out["to"], out["via"]),
                         (11, 22, {"ref": "S", "side": "left"}, [[13, 24]]))
        self.assertEqual(pipe["from"]["x"], 1)    # a copy

    # ---- the module: a value the module cannot draw is not asked of it --------------------
    def test_a_value_only_the_librarys_view_has_is_kept_off_the_symbols_the_module_draws(self):
        pump = [s for s in self.desc["symbols"] if s["kind"] == "pump"]
        self.assertNotIn("none", {s["params"].get("readoutPosition") for s in pump})
        damper = [s for s in self.desc["symbols"] if s["kind"] == "damper"]
        self.assertNotIn("none", {s["params"].get("readoutPosition") for s in damper})   # the module's damper (B1) has no such value
        indicator = [s for s in self.desc["symbols"] if s["kind"] == "indicator"]
        self.assertIn("none", {s["params"].get("readoutPosition") for s in indicator})   # no module indicator
        # a status only the library has is on the pump only forced onto the library's view (module beside view, L5)
        critical = [s for s in pump if stated(self.bench, s).get("alertFrameStatus") == "critical"]
        self.assertTrue(critical)
        self.assertEqual({s.get("render") for s in critical}, {"view"})
        self.assertIn("critical", {stated(self.bench, s).get("alertFrameStatus") for s in self.desc["symbols"]})
        valves = [s for s in self.desc["symbols"] if s["kind"] == "valve"]
        self.assertIn("double", {s["params"].get("variant") for s in valves + pump})
        self.assertNotIn("double", {s["params"].get("variant") for s in valves})   # stays library: the module has two

    # ---- the test devices and their tags --------------------------------------------------
    def test_a_test_device_for_each_device_kind_and_each_priority(self):
        kinds = {d["kind"] for d in self.bench.devices}
        self.assertEqual(set(self.prof["deviceKinds"]) - kinds - {"readout", "instrument-field"}, set())
        ids = {d["id"] for d in self.bench.devices}
        for prio in alarms.PRIORITIES:
            self.assertIn(f"{FOLDER}/ALM_{prio.upper()}", ids)
        # each device symbol opens a faceplate (G11): it is a device symbol, in the model, of a kind with a faceplate
        folders = {s["device"] for s in self.desc["symbols"] if s.get("device")}
        folders |= {s["faceplate"] for s in self.desc["symbols"] if s.get("faceplate")}   # a plain symbol opens one (L5)
        self.assertEqual({d["id"] for d in self.bench.devices} - folders, set())
        for d in self.bench.devices:
            self.assertIn(d["kind"], self.prof["deviceKinds"])

    def test_the_tags_are_memory_and_expression_tags_under_the_test_folder_alone(self):
        self.assertEqual((self.bench.tags["name"], self.bench.tags["tagType"]), (FOLDER, "Folder"))
        for path, t in leaves(self.bench.tags):
            self.assertIn(t["valueSource"], ("memory", "expr"), path)
            if t["valueSource"] == "expr":
                self.assertIn("coalesce", t["expression"], path)   # null spreads through an expression (GF-19)
        # every tag a symbol binds, a button pulses or a model lists is in the folder (the root of the build is the folder's parent)
        have = {p for p, _t in leaves(self.bench.tags)}
        for s in self.desc["symbols"]:
            for member in s.get("bind", {}).values():
                self.assertTrue(member.startswith(FOLDER + "/"), (s["id"], member))
                self.assertIn(member[len(FOLDER) + 1:], have, (s["id"], member))
        for t in self.bench.pulse_tags:
            self.assertTrue(t.startswith(FOLDER + "/"), t)
            self.assertIn(t[len(FOLDER) + 1:], have, t)
        for d in self.bench.devices:
            for m in d["members"]:
                self.assertIn(f"{d['id'][len(FOLDER) + 1:]}/{m}", have, (d["id"], m))

    def test_the_buttons_write_only_test_tags(self):
        pulses = [b["action"]["tag"] for b in self.desc["buttons"] if b["action"]["type"] == "pulse"]
        self.assertTrue(pulses)
        self.assertEqual({t for t in pulses if not t.startswith(FOLDER + "/")}, set())
        self.assertEqual(set(pulses), set(self.bench.pulse_tags))
        for b in self.desc["buttons"]:
            if b["action"]["type"] == "pulse":
                self.assertEqual(b["action"]["ms"], testbench.PULSE_MS)
            if b["action"]["type"] == "faceplate":
                self.assertTrue(b["action"]["device"].startswith(FOLDER + "/"))
        # the page's pulses are all in the folder's tags as memory Booleans, which the plant need not return to false
        flat = dict(leaves(self.bench.tags))
        for t in pulses:
            tag = flat[t[len(FOLDER) + 1:]]
            self.assertEqual((tag["valueSource"], tag["dataType"]), ("memory", "Boolean"), t)

    def test_there_is_one_alarm_of_each_priority_in_the_librarys_form(self):
        flat = dict(leaves(self.bench.tags))
        for prio in alarms.PRIORITIES:
            tag = flat[f"ALM_{prio.upper()}/state"]
            self.assertEqual([a["priority"] for a in tag["alarms"]], [prio])
            a = tag["alarms"][0]
            self.assertEqual(a["shelvingAllowed"], prio not in alarms.NOT_SHELVED)
            self.assertTrue(a["label"].startswith(f"ALM-{prio.upper()} "), a["label"])
            self.assertEqual(a["displayPath"], f"Component test/ALM-{prio.upper()}")
            # the state follows its own raise tag and the all-alarms tag, in the project's own tag root
            self.assertIn("{[.]raise}", tag["expression"])
            self.assertIn(f"{{{TAG_ROOT}/{FOLDER}/ALM_ALL/raise}}", tag["expression"])

    def test_the_limits_move_the_instruments_alarms(self):
        flat = dict(leaves(self.bench.tags))
        alarm = flat["TB_READOUT/value"]["alarms"][0]
        self.assertEqual(alarm["setpointA"], {"bindType": "Expression", "value": "{[.]hiLimit}"})

    def test_the_modes_and_the_owners(self):
        by_id = {d["id"]: d for d in self.bench.devices}
        for ident in ("TB_PUMP", "TB_MOTOR", "TB_VALVE"):
            d = by_id[f"{FOLDER}/{ident}"]
            self.assertEqual({m["owner"] for m in d["modes"]}, set(self.prof["ownership"]["owners"]))
            self.assertEqual(d["members"]["mode"], {"type": "Int4", "access": "write"})
        self.assertNotIn("modes", by_id[f"{FOLDER}/TB_FAN"])

    # ---- the model and the tag model ------------------------------------------------------
    def test_extending_the_models_copies_and_passes_none_through(self):
        self.assertIsNone(self.bench.extend_devices(None))
        self.assertIsNone(self.bench.extend_tags(None))
        model = load("asm-devices.json")
        before = copy.deepcopy(model)
        out = self.bench.extend_devices(model)
        self.assertEqual(model, before)
        self.assertEqual(len(out["devices"]), len(model["devices"]) + len(self.bench.devices))
        self.assertEqual(len(self.bench.extend_devices(out)["devices"]), len(out["devices"]))   # none twice
        tags = {"name": "cadre_hmi_asmtest", "tagType": "Folder", "tags": [{"name": FOLDER, "tagType": "Folder", "tags": []}]}
        out = self.bench.extend_tags(tags)
        self.assertEqual([t["name"] for t in out["tags"]], [FOLDER])
        self.assertEqual(tags["tags"][0]["tags"], [])
        self.assertTrue(out["tags"][0]["tags"])


class GateTests(unittest.TestCase):
    """The page passes G0 to G7 on a project built with the asm frame, under both renderings, with and without a model."""

    @classmethod
    def setUpClass(cls):
        cls.contracts = screen.load_contracts()
        cls.prof = library_profile.build(cls.contracts)
        cls.desc, cls.model = load("asm-screen.json"), load("asm-devices.json")
        cls.bench = testbench.build(cls.contracts, cls.prof, TAG_ROOT)

    def build(self, render="stock", model=True, **extra):
        descs = [self.desc, self.bench.descriptor]
        devices = self.bench.extend_devices(self.model) if model else None
        tags = self.bench.extend_tags(screen.tags_document([self.desc], self.model))
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            child, reports = screen.build_child("cadre_hmi_asmtest", descs, "Asm", "*cadre_hmi_asmtest*", render,
                                                tag_model=tags, devices=devices, faceplate="asm", **extra)
            out = child.write(Path(d))
            rep = Path(d) / "report.json"
            rep.write_text(json.dumps(reports, default=list), encoding="utf-8")
            res = gates.run(out, base, rep, tag_model=tags, devices=devices, symbols=screen.device_symbols(descs),
                            profile=self.prof, alarm_scope="*cadre_hmi_asmtest*")
        return child, reports, res

    def test_both_renderings_pass_with_the_asm_frame(self):
        for render in ("stock", "module"):
            child, reports, res = self.build(render, frame="asm")
            page = reports["/component-test"]
            self.assertEqual((page["errors"], page["gaps"]), ([], []), render)
            self.assertTrue(res["ok"], {k: v for k, v in res.items() if isinstance(v, dict) and not v.get("ok")})
            self.assertEqual(res["G7_devices"]["problems"], [], render)
            self.assertEqual(res["G7_devices"]["warnings"], [], render)
            self.assertEqual(res["G7_devices"]["devices"], len(self.model["devices"]) + len(self.bench.devices))
            self.assertEqual(res["G5_layout"]["warnings"], [], render)

    def test_without_a_device_model_the_page_still_builds(self):
        _child, reports, res = self.build("stock", model=False)
        self.assertEqual(reports["/component-test"]["errors"], [])
        self.assertTrue(res["ok"], {k: v for k, v in res.items() if isinstance(v, dict) and not v.get("ok")})

    def test_the_page_is_in_the_navigation_and_the_device_index(self):
        child, _reports, _res = self.build("module", frame="asm")
        props = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
        nav = props["custom"]["nav"]["items"]
        self.assertIn(("/component-test", "Tools: Component test"), [(i["path"], i["label"]) for i in nav])
        devices = {d["folder"]: d for d in props["custom"]["devices"]}
        for d in self.bench.devices:
            self.assertIn(f"{TAG_ROOT}/{d['id']}", devices)
        # the pulse tags the buttons write are the page's own, the only ones its commands list gains
        commands = {c["path"] for c in props["custom"]["commands"]}
        self.assertTrue({f"{TAG_ROOT}/{t}" for t in self.bench.pulse_tags} <= commands)

    def test_the_page_follows_the_alarms_of_its_devices_and_not_its_static_symbols(self):
        child, _reports, _res = self.build("stock")
        doc = json.loads(child.files["com.inductiveautomation.perspective/views/Screens/ComponentTest/view.json"])
        keys = set(doc["custom"]["alerts"])
        self.assertTrue({f"a_ALM_{p.upper()}" for p in alarms.PRIORITIES} <= keys)
        self.assertEqual({k for k in keys if not k.startswith(("a_ALM_", "a_TB_"))}, set())   # no static symbol polls

    def test_the_stock_and_the_module_rendering_draw_the_same_page_with_the_modules_symbols(self):
        stock, _r, _g = self.build("stock")
        module, _r, _g = self.build("module")
        path = "com.inductiveautomation.perspective/views/Screens/ComponentTest/view.json"
        types = lambda c: {n["type"] for n in walk(json.loads(c.files[path])["root"])}   # noqa: E731
        self.assertEqual({t for t in types(stock) if t.startswith("cadre.ob")}, set())
        self.assertTrue({"cadre.ob.pump", "cadre.ob.tank", "cadre.ob.readout"} <= types(module))


class CommandLineTests(unittest.TestCase):
    """`screen.py --component-test` through `main`: the page is added, the tags are written beside the build."""

    def test_the_option_adds_the_page_the_tags_and_the_models(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "build"
            argv = ["screen.py", "--project", "cadre_hmi_asmtest", "--descriptor", str(FIXTURES / "asm-screen.json"),
                    "--devices-file", str(FIXTURES / "asm-devices.json"), "--frame", "asm", "--faceplate", "asm",
                    "--alarm-scope", "*cadre_hmi_asmtest*", "--component-test", "--out", str(out),
                    "--report", str(Path(d) / "report.json")]
            prj, _ = par.build_parent()
            prj.write(out)
            with mock.patch.object(sys, "argv", argv), mock.patch("builtins.print"):
                self.assertEqual(screen.main(), 0)
            tags = json.loads((out / "cadre_hmi_asmtest.component-test-tags.json").read_text(encoding="utf-8"))
            self.assertEqual(tags["name"], FOLDER)
            report = json.loads((Path(d) / "report.json").read_text(encoding="utf-8"))
            self.assertIn("/component-test", report)
            self.assertTrue(report["gates"]["ok"])
            self.assertEqual(report["gates"]["G7_devices"]["devices"], 4 + len(testbench.model_entries(
                testbench.device_specs(TAG_ROOT, "Component test"))))
            self.assertTrue((out / "cadre_hmi_asmtest" / "com.inductiveautomation.perspective" / "views" / "Screens"
                             / "ComponentTest" / "view.json").exists())

    def test_without_the_option_the_build_is_what_it_was(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "build"
            argv = ["screen.py", "--project", "cadre_hmi_asmtest", "--descriptor", str(FIXTURES / "asm-screen.json"),
                    "--devices-file", str(FIXTURES / "asm-devices.json"), "--out", str(out)]
            prj, _ = par.build_parent()
            prj.write(out)
            with mock.patch.object(sys, "argv", argv), mock.patch("builtins.print"):
                self.assertEqual(screen.main(), 0)
            self.assertFalse(list(out.glob("*.component-test-tags.json")))
            self.assertFalse((out / "cadre_hmi_asmtest" / "com.inductiveautomation.perspective" / "views" / "Screens"
                              / "ComponentTest").exists())

    def test_descriptors_with_two_tag_roots_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            other = load("asm-screen.json")
            other["tagRoot"] = "[default]cadre_hmi_other"
            other["screen"]["route"], other["screen"]["id"], other["screen"]["view"] = "/o", "Other", "Screens/Other"
            path = Path(d) / "other.json"
            path.write_text(json.dumps(other), encoding="utf-8")
            argv = ["screen.py", "--project", "cadre_hmi_asmtest", "--descriptor", str(FIXTURES / "asm-screen.json"),
                    "--descriptor", str(path), "--component-test", "--out", str(Path(d) / "build")]
            with mock.patch.object(sys, "argv", argv), mock.patch("builtins.print"):
                self.assertEqual(screen.main(), 1)


if __name__ == "__main__":
    unittest.main()
