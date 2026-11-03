"""Unit tests for the generator: flow compilation, routing, emit guards, contracts, gates.

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import diagram, pv, screen  # noqa: E402


def two_tank_desc(closed_pipe=False):
    """Two tanks joined twice: through a valve, and through a pump (the vendor example shape)."""
    return {
        "screen": {"width": 800, "height": 400},
        "symbols": [
            {"id": "TA", "kind": "tank", "x": 0, "y": 0, "w": 100, "h": 100},
            {"id": "TB", "kind": "tank", "x": 600, "y": 0, "w": 100, "h": 100},
            {"id": "V1", "kind": "valve", "x": 300, "y": 20, "w": 48, "h": 48},
            {"id": "P1", "kind": "pump", "x": 300, "y": 200, "w": 48, "h": 48},
        ],
        "junctions": [],
        "pipes": [
            {"id": "a", "from": {"ref": "TA", "side": "right"}, "to": {"ref": "V1", "side": "left"}},
            {"id": "b", "from": {"ref": "V1", "side": "right"}, "to": {"ref": "TB", "side": "left"},
             **({"state": "closed"} if closed_pipe else {})},
            {"id": "c", "from": {"ref": "TA", "side": "bottom"}, "to": {"ref": "P1", "side": "left"}},
            {"id": "d", "from": {"ref": "P1", "side": "right"}, "to": {"ref": "TB", "side": "bottom"}},
        ],
    }


class FlowTests(unittest.TestCase):
    def test_two_tanks(self):
        g, _ = diagram.build_graph(two_tank_desc(), {})
        dnf = diagram.compile_flow(g)
        self.assertEqual(dnf["a"], [frozenset({"V1"})])
        self.assertEqual(dnf["c"], [frozenset({"P1"})])
        self.assertEqual(diagram.solve(g, {"V1": True, "P1": False}), {"a", "b"})
        self.assertEqual(diagram.solve(g, {"V1": False, "P1": False}), set())

    def test_closed_pipe_blocks(self):
        g, _ = diagram.build_graph(two_tank_desc(closed_pipe=True), {})
        self.assertNotIn("b", g.edges)
        self.assertEqual(diagram.solve(g, {"V1": True, "P1": False}), set())

    def test_expressions_agree_with_solver(self):
        g, _ = diagram.build_graph(two_tank_desc(), {})
        exprs = {e: diagram.dnf_expression(t, lambda n: f"{{view.custom.g_{n}}}")
                 for e, t in diagram.compile_flow(g).items()}
        self.assertTrue(diagram.check_flow(g, exprs)["ok"])

    def test_pump_is_not_a_source(self):
        desc = {"screen": {"width": 400, "height": 200},
                "symbols": [{"id": "P1", "kind": "pump", "x": 100, "y": 50, "w": 48, "h": 48}],
                "pipes": [{"id": "x", "from": {"x": 0, "y": 74, "end": "cap"}, "to": {"ref": "P1", "side": "left"}},
                          {"id": "y", "from": {"ref": "P1", "side": "right"}, "to": {"x": 300, "y": 74, "end": "arrow-out"}}]}
        g, _ = diagram.build_graph(desc, {})
        self.assertEqual(diagram.solve(g, {"P1": True}), set())

    def test_sample_descriptor(self):
        desc = json.loads((ROOT / "screens/sample-pump-station.json").read_text(encoding="utf-8"))
        doc, info = screen.build_screen(desc, screen.load_contracts())
        self.assertEqual(info["errors"], [])
        self.assertTrue(info["flow"]["ok"])


class RoutingTests(unittest.TestCase):
    def test_z_and_l(self):
        self.assertEqual(diagram.route((0, 0), "bottom", (100, 100), "top"),
                         [(0, 0), (0, 50), (100, 50), (100, 100)])
        self.assertEqual(diagram.route((0, 0), "right", (100, 100), "top"), [(0, 0), (100, 0), (100, 100)])
        self.assertEqual(diagram.route((0, 0), "right", (100, 0), "left"), [(0, 0), (100, 0)])

    def test_via_points_are_orthogonal(self):
        pts = diagram.route((0, 0), "right", (100, 100), "left", via=[(50, 20)])
        for a, b in zip(pts, pts[1:]):
            self.assertTrue(a[0] == b[0] or a[1] == b[1], (a, b))


class EmitGuardTests(unittest.TestCase):
    def test_view_level_key_guard(self):
        with self.assertRaises(ValueError):
            pv.view(pv.node("ia.container.flex", "root", {}), custom_config={"view.custom.x": {}})

    def test_containers_default_to_hidden_overflow(self):
        n = pv.node("ia.container.flex", "c", {}, {"style": {}})
        self.assertEqual(n["props"]["style"]["overflow"], "hidden")
        n = pv.node("ia.container.flex", "c", {}, {"style": {"overflow": "auto"}})
        self.assertEqual(n["props"]["style"]["overflow"], "auto")

    def test_tag_binding_keys_are_declared(self):
        cfg = pv.tag("[default]x")["config"]
        self.assertLessEqual(set(cfg), {"bidirectional", "mode", "references", "tagPath"})

    def test_unknown_parameter_is_an_error(self):
        desc = two_tank_desc()
        desc["symbols"][2]["params"] = {"colour": "red"}
        _, info = screen.build_screen(desc, screen.load_contracts())
        self.assertTrue(any("colour" in e for e in info["errors"]))

    def test_unknown_kind_is_a_counted_gap(self):
        desc = two_tank_desc()
        desc["symbols"].append({"id": "C1", "kind": "compass", "x": 10, "y": 300, "w": 80, "h": 80})
        _, info = screen.build_screen(desc, screen.load_contracts())
        self.assertEqual([g["kind"] for g in info["gaps"]], ["compass"])


class ProjectTests(unittest.TestCase):
    def test_build_is_deterministic(self):
        desc = json.loads((ROOT / "screens/sample-pump-station.json").read_text(encoding="utf-8"))
        a, _ = screen.build_child("cadre_hmi_t", [desc], "T")
        b, _ = screen.build_child("cadre_hmi_t", [desc], "T")
        self.assertEqual(a.zip_bytes(), b.zip_bytes())

    def test_parent_name_is_an_option(self):
        """A second parent (for example the ASM build beside the deployed one) and a child of it (COB-157)."""
        from hmi import parent as par
        base, _ = par.build_parent("cadre_hmi_base_asm")
        self.assertEqual(base.name, "cadre_hmi_base_asm")
        self.assertTrue(json.loads(base.files["project.json"])["inheritable"])
        desc = json.loads((ROOT / "screens/sample-pump-station.json").read_text(encoding="utf-8"))
        child, _ = screen.build_child("cadre_hmi_t", [desc], "T", parent="cadre_hmi_base_asm")
        self.assertEqual(json.loads(child.files["project.json"])["parent"], "cadre_hmi_base_asm")
        default, _ = screen.build_child("cadre_hmi_t", [desc], "T")
        self.assertEqual(json.loads(default.files["project.json"])["parent"], par.PARENT)
        with self.assertRaises(ValueError):
            par.build_parent("other_base")



class TagDocumentTests(unittest.TestCase):
    def test_two_roots_share_a_top_folder(self):
        a = {"tagRoot": "[default]top/a", "tagValues": {"V1/state": True},
             "symbols": [{"id": "V1", "kind": "valve", "x": 0, "y": 0, "bind": {"open": "V1/state"}}]}
        b = {"tagRoot": "[default]top/b", "tagValues": {"V2/state": False},
             "symbols": [{"id": "V2", "kind": "valve", "x": 0, "y": 0, "bind": {"open": "V2/state"}}]}
        doc = screen.tags_document([a, b])
        self.assertEqual(doc["name"], "top")
        names = sorted(t["name"] for t in doc["tags"])
        self.assertEqual(names, ["a", "b"])
        va = next(t for t in doc["tags"] if t["name"] == "a")["tags"][0]["tags"][0]
        self.assertEqual((va["name"], va["value"]), ("state", True))


class FaceplateContractTests(unittest.TestCase):
    def leaves(self, folder, path=()):
        out = {}
        for t in folder.get("tags", []):
            if t["tagType"] == "Folder":
                out.update(self.leaves(t, path + (t["name"],)))
            else:
                out["/".join(path + (t["name"],))] = t["value"]
        return out

    def test_generated_devices_carry_their_faceplate_members(self):
        desc = {"tagRoot": "[default]t", "symbols": [
            {"id": "P1", "kind": "pump", "x": 0, "y": 0, "device": True, "bind": {"on": "P1/state"}},
            {"id": "T1", "kind": "tank", "x": 0, "y": 0, "device": True, "bind": {"value": "T1/volume"}},
            {"id": "T2", "kind": "tank", "x": 0, "y": 0, "bind": {"value": "T2/level"}}]}
        got = self.leaves(screen.tags_document([desc]))
        self.assertEqual(sorted(k for k in got if k.startswith("P1/")),
                         ["P1/cmd", "P1/fault", "P1/mode", "P1/speed", "P1/speedSp", "P1/state"])
        self.assertEqual(sorted(k for k in got if k.startswith("T1/")),
                         ["T1/hiLimit", "T1/level", "T1/loLimit", "T1/volume"])
        self.assertEqual(sorted(k for k in got if k.startswith("T2/")), ["T2/level"])

    def test_a_card_symbol_names_the_device_folder(self):
        sym = {"id": "C_P1", "kind": "pump", "x": 0, "y": 0, "w": 48, "h": 48, "device": "P1",
               "bind": {"on": "P1/state", "speed": "P1/speed"}}
        got = self.leaves(screen.tags_document([{"tagRoot": "[default]t", "symbols": [sym]}]))
        self.assertIn("P1/speedSp", got)
        self.assertFalse(any(k.startswith("C_P1") for k in got))
        rep = screen.Report()
        node, _, _ = screen.embed_symbol(sym, screen.load_contracts(), "[default]t", rep, toolbar=False)
        self.assertEqual(node["props"]["params"]["deviceId"], "[default]t/P1")
        self.assertEqual(rep.errors, [])

    def test_a_device_bound_outside_its_folder_is_an_error(self):
        desc = two_tank_desc()
        desc["tagRoot"] = "[default]t"
        desc["symbols"][3].update({"device": True, "bind": {"on": "P9/state"}})
        _, info = screen.build_screen(desc, screen.load_contracts())
        self.assertTrue(any("faceplate contract" in e for e in info["errors"]))


class ModuleRenderTests(unittest.TestCase):
    """The render switch of the Cadre OpenBridge module (wiki page 12): the same descriptor, the
    module's components for pumps and tanks, every other kind as before."""

    def setUp(self):
        self.desc = json.loads((ROOT / "screens/wtp/intake.json").read_text(encoding="utf-8"))

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def nodes(self, render):
        child, reports = screen.build_child("cadre_hmi_t", [self.desc], "T", render=render)
        view = json.loads(child.files["com.inductiveautomation.perspective/views/Screens/Intake/view.json"])
        out = {}

        def walk(n):
            out[n.get("meta", {}).get("name")] = n
            for c in n.get("children") or []:
                walk(c)
        walk(view["root"])
        return out, reports

    def test_pump_keeps_its_symbol_box_and_selection(self):
        stock, _ = self.nodes("stock")
        mod, rep = self.nodes("module")
        self.assertEqual(stock["P101"]["type"], "ia.display.view")
        p = mod["P101"]
        self.assertEqual(p["type"], "cadre.ob.pump")
        sym = next(s for s in self.desc["symbols"] if s["id"] == "P101")
        self.assertEqual((p["position"]["x"], p["position"]["y"], p["position"]["width"]), (sym["x"], sym["y"], 48))
        self.assertIn("props.speedInPercent", p["propConfig"])
        self.assertEqual(p["custom"]["deviceKind"], "pump")
        self.assertIn("onClick", p["events"]["dom"])
        self.assertEqual(mod["XV101"]["type"], "cadre.ob.valve")    # valves are the module's since 0.3.0
        self.assertEqual((mod["XV101"]["position"]["width"], mod["XV101"]["props"]["positioning"]), (48, "symbol"))
        self.assertEqual(rep["/intake"]["errors"], [])

    def test_registry_gate_checks_module_props(self):
        from hmi import gates
        mod, _ = self.nodes("module")
        with tempfile.TemporaryDirectory() as d:
            child, _ = screen.build_child("cadre_hmi_t", [self.desc], "T", render="module")
            out = child.write(Path(d))
            self.assertTrue(gates.g1_registry(out)["ok"])
            vf = out / "com.inductiveautomation.perspective/views/Screens/Intake/view.json"
            doc = json.loads(vf.read_text(encoding="utf-8"))

            def poison(n):
                if n.get("type") == "cadre.ob.pump":
                    n["props"]["colour"] = "red"
                for c in n.get("children") or []:
                    poison(c)
            poison(doc["root"])
            vf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertFalse(gates.g1_registry(out)["ok"])


class FaceplateTabTests(unittest.TestCase):
    """Tabbed faceplates (COB-076): the tab row, one pane per tab, the reset to the first tab on a
    new device, and the alarm list narrowed by the device's source; G7 checks all of it."""

    def build(self, d):
        from hmi import parent as par
        prj, _ = par.build_parent()
        base = prj.write(Path(d))
        desc = json.loads((ROOT / "screens/wtp/intake.json").read_text(encoding="utf-8"))
        child, _ = screen.build_child("cadre_hmi_t", [desc], "T")
        return child.write(Path(d)), base

    def view(self, base, path):
        return json.loads((base / "com.inductiveautomation.perspective/views" / path / "view.json").read_text(encoding="utf-8"))

    def test_param_change_shape(self):
        v = pv.view(pv.node("ia.container.flex", "root", {}), params={"deviceId": ""},
                    param_dirs={"deviceId": "input"}, param_change={"deviceId": ["self.custom.tab = 'control'"]})
        self.assertEqual(v["propConfig"]["params.deviceId"],
                         {"paramDirection": "input", "persistent": True,
                          "onChange": {"enabled": None, "script": "\tself.custom.tab = 'control'"}})

    def test_faceplates_pass_g7_and_a_broken_one_fails(self):
        from hmi import gates
        with tempfile.TemporaryDirectory() as d:
            child, base = self.build(d)
            res = gates.g7_faceplates(child, base)
            self.assertTrue(res["ok"], res["problems"])
            self.assertEqual(res["tabs"]["Faceplate/Pump"], ["control", "alarms", "interlocks", "maintenance"])
            self.assertEqual(res["tabs"]["Faceplate/Controller"], ["control", "trend", "tuning", "alarms"])
            self.assertEqual(res["tabs"]["Faceplate/Input"], ["status", "maintenance", "alarms"])
            self.assertEqual(res["tabs"]["Faceplate/Sequence"], ["status", "trend", "alarms"])
            self.assertEqual(res["tabs"]["Faceplate/Tank"], ["values", "trend", "alarms"])
            self.assertEqual(res["tabs"]["Faceplate/Instrument"], ["values", "trend", "alarms"])
            self.assertEqual(res["alarm_list"], ["ia.display.alarmstatustable"])
            # a pane removed, then a text filter put back on the table: each fails the gate
            vf = base / "com.inductiveautomation.perspective/views/Faceplate/Valve/view.json"
            doc = json.loads(vf.read_text(encoding="utf-8"))
            doc["root"]["children"] = [c for c in doc["root"]["children"] if c["meta"]["name"] != "Pane_alarms"]
            vf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertTrue(any("Valve: tab 'alarms' has no pane" in p for p in gates.g7_faceplates(child, base)["problems"]))
            af = base / "com.inductiveautomation.perspective/views/Faceplate/Alarms/view.json"
            doc = json.loads(af.read_text(encoding="utf-8"))
            doc["root"]["children"][0]["propConfig"]["props.filters.active.text"] = pv.bind(pv.expr("'P-502'"))
            af.write_text(json.dumps(doc), encoding="utf-8")
            self.assertTrue(any("filters by text" in p for p in gates.g7_faceplates(child, base)["problems"]))

    def test_no_faceplate_filters_by_title(self):
        with tempfile.TemporaryDirectory() as d:
            _, base = self.build(d)
            for fp in ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/Tank", "Faceplate/Alarms"):
                self.assertNotIn("filters.active.text", json.dumps(self.view(base, fp)), fp)


class AlarmListTests(unittest.TestCase):
    """The pure parts of `cadre.hmi.alarm_list` and `ack` (COB-077), run offline against stub alarm
    events that answer the accessors experiment E4 measured (GF-34, GF-35)."""

    class Key:
        """A property key: its text is the name, its hash is its identity, so a lookup of the raw
        map by the name string misses, as on the gateway (GF-35)."""
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name

    class Data:
        def __init__(self, ts, raw=None):
            self.ts = ts
            self.raw = {AlarmListTests.Key(k): v for k, v in (raw or {}).items()}

        def getTimestamp(self):
            return self.ts

        def getRawValueMap(self):
            return self.raw

        def getProperties(self):
            return list(self.raw)

    class Event:
        def __init__(self, folder, priority, ts, acked=None, cleared=None):
            self.folder, self.priority, self.ts, self.acked, self.cleared = folder, priority, ts, acked, cleared

        def getId(self): return f"id-{self.folder}-{self.ts}"
        def getSource(self): return f"prov:default:/tag:cadre_hmi_wtp/{self.folder}/fault:/alm:Fault"
        def getDisplayPathOrSource(self): return f"WTP/{self.folder}"
        def getLabel(self): return f"{self.folder} Fault"
        def getName(self): return "Fault"
        def getPriority(self): return self.priority
        def getNotes(self): return ""
        def getActiveData(self): return AlarmListTests.Data(self.ts)
        def isAcked(self): return self.acked is not None
        def getAckData(self): return AlarmListTests.Data(self.acked, {"ackUser": "usr:probe"}) if self.acked else None
        def isCleared(self): return self.cleared is not None
        def getClearedData(self): return AlarmListTests.Data(self.cleared) if self.cleared else None

    def hmi(self, events=()):
        from hmi import scripts
        calls = []

        class Alarm:
            @staticmethod
            def queryStatus(path=None, state=None, priority=None):
                calls.append(("query", path, state))
                return list(events)

            @staticmethod
            def acknowledge(ids, notes, user):
                calls.append(("ack", ids, notes, user))
                return []

        class System:
            alarm = Alarm
        ns = {"unicode": str, "long": int, "system": System}
        exec(scripts.HMI, ns)
        return ns, calls

    def test_device_source_and_tag_id(self):
        ns, _ = self.hmi()
        self.assertEqual(ns["device_source"]("[default]cadre_hmi_wtp/P502"), "prov:default:/tag:cadre_hmi_wtp/P502/*")
        for bad in ("", "cadre_hmi_wtp/P502", "[default]", None):
            self.assertEqual(ns["device_source"](bad), ns["NO_MATCH"])
        self.assertEqual(ns["tag_id"]("prov:default:/tag:cadre_hmi_wtp/P502/fault:/alm:Fault"), "[default]cadre_hmi_wtp/P502")

    def test_priority_map_covers_the_five_priorities(self):
        ns, _ = self.hmi()
        self.assertEqual(ns["ALERT_TYPE"], {"Critical": "level-critical", "High": "level-high", "Medium": "level-medium",
                                            "Low": "level-low", "Diagnostic": "level-diagnostic"})

    def test_record_shape(self):
        ns, _ = self.hmi()
        rec = ns["alert_record"](self.Event("P502", "High", 1791463808784))
        self.assertEqual(rec, {"id": "id-P502-1791463808784", "tagId": "[default]cadre_hmi_wtp/P502",
                               "source": "WTP/P502", "text": "P502 Fault", "type": "level-high",
                               "time": 1791463808784, "acknowledged": False, "active": True, "shelved": False})
        rec = ns["alert_record"](self.Event("P502", "High", 10, acked=20, cleared=30))
        self.assertEqual(rec["acknowledged"], {"acknowledgedBy": "probe", "acknowledgedAt": 20})
        self.assertEqual(rec["active"], {"rectifiedTime": 30})

    def test_list_order_and_query(self):
        evs = [self.Event("A", "Low", 5), self.Event("B", "Critical", 1), self.Event("C", "High", 3),
               self.Event("D", "High", 4)]
        ns, calls = self.hmi(evs)
        out = ns["alarm_list"]("*cadre_hmi_wtp*", "prov:default:/tag:cadre_hmi_wtp/P502/*", None, 3)
        self.assertEqual([r["tagId"][-1] for r in out], ["B", "D", "C"])
        self.assertEqual(calls[0], ("query", ["prov:default:/tag:cadre_hmi_wtp/P502/*"],
                                    ["ActiveUnacked", "ActiveAcked", "ClearUnacked"]))
        ns["alarm_list"]("*cadre_hmi_wtp*")
        self.assertEqual(calls[1][1], ["*cadre_hmi_wtp*"])
        self.assertNotIn("noAck", out[0])
        # the faceplate's display only list (COBD-025): every record marked noAck
        self.assertTrue(all(r["noAck"] is True for r in ns["alarm_list"]("*", "x", no_ack=True)))

    def test_ack_user(self):
        ns, calls = self.hmi([self.Event("P502", "High", 5)])
        # nobody signed in: refused, nothing acknowledged, never as "operator" (COBD-024)
        self.assertEqual(ns["ack"](["id-P502-5"], None), ns["REFUSED"])
        self.assertEqual([c for c in calls if c[0] == "ack"], [])

        class Auth:
            authenticated = True

            class user:
                userName = "jo"
                roles = ["Administrator"]

        class Session:
            class props:
                auth = Auth

            class custom:
                alarmScope = "*cadre_hmi_wtp*"
        ns["ack"](["id-P502-5"], Session, "note")
        self.assertEqual(calls[-1], ("ack", ["id-P502-5"], "note", "jo"))
        n = len(calls)
        self.assertEqual(ns["ack"]([], Session), [])
        self.assertEqual(len(calls), n)


class ModuleAlarmListTests(unittest.TestCase):
    """The module's alarm lists (COB-078): the generated contract, the child overrides under
    `--render module`, the registry gate over them, the device index and the event helpers."""

    def setUp(self):
        self.descs = [json.loads((ROOT / f"screens/wtp/{n}.json").read_text(encoding="utf-8"))
                      for n in ("overview", "intake", "filtration", "disinfection")]

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def test_contract_declares_events_with_schemas(self):
        comps = json.loads((ROOT / "module/components.json").read_text(encoding="utf-8"))
        res = ROOT / "module/common/src/main/resources"
        self.assertEqual(set(comps["cadre.ob.alertlist"]["events"]), {"onAckClick", "onRowClick"})
        self.assertEqual(set(comps["cadre.ob.alertpanel"]["events"]),
                         {"onAckClick", "onRowClick", "onSilenceClick", "onAckAllClick"})
        for c in comps.values():
            self.assertTrue((res / c["schema"]).exists())
            for e in (c.get("events") or {}).values():
                self.assertTrue((res / e["schema"]).exists(), e)
        self.assertEqual(comps["cadre.ob.alertpanel"]["props"]["selectedMode"]["enum"], ["unacked", "all", "shelved"])
        js = (ROOT / "module/gateway/src/main/resources/mounted/js/cadre-ob.js").read_text(encoding="utf-8")
        self.assertIn("fireComponentEvent", js)
        self.assertIn("readArray", js)

    def test_module_render_overrides_only_the_alarm_views(self):
        from hmi import gates, parent as par
        stock, _ = screen.build_child("cadre_hmi_t", self.descs, "T")
        mod, _ = screen.build_child("cadre_hmi_t", self.descs, "T", render="module")
        views = "com.inductiveautomation.perspective/views/"
        self.assertNotIn(views + "Faceplate/Alarms/view.json", stock.files)
        fa = json.loads(mod.files[views + "Faceplate/Alarms/view.json"])
        am = json.loads(mod.files[views + "Framework/AlertMenu/view.json"])
        self.assertEqual(fa["root"]["children"][0]["type"], "cadre.ob.alertlist")
        panel = next(n for n in am["root"]["children"] if n["meta"]["name"] == "Panel")
        self.assertEqual(panel["type"], "cadre.ob.alertpanel")
        # the menu closes from its own close button as from a click outside it (a modal popup, `framework.top_bar`)
        close = am["root"]["children"][0]["children"][1]["events"]["dom"]["onClick"]["config"]["script"]
        self.assertIn("closePopup('alertMenu')", close)
        tt = json.loads(mod.files[views + "Faceplate/TankTile/view.json"])   # the faceplate's tank as on the diagram
        self.assertEqual(tt["root"]["children"][0]["type"], "cadre.ob.tank")
        # the faceplate's module tab is display only (COBD-025): no acknowledge event, records marked noAck;
        # the alarm menu keeps ACK and ACK visible
        for n in fa["root"]["children"]:
            self.assertNotIn("events", n, n["meta"]["name"])
        self.assertIn("no_ack=True", fa["propConfig"]["custom.alarms"]["binding"]["transforms"][0]["code"])
        self.assertEqual(set(panel["events"]["component"]), {"onAckClick", "onAckAllClick", "onRowClick"})
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            out = mod.write(Path(d))
            self.assertTrue(gates.g1_registry(out)["ok"])
            res = gates.g7_faceplates(out, base)
            self.assertTrue(res["ok"], res["problems"])
            self.assertEqual(res["alarm_list"], ["cadre.ob.alertlist", "cadre.ob.alertlist"])   # active, cleared
            # G7 refuses a module faceplate list that acknowledges, or whose records are not marked noAck
            vf = out / "com.inductiveautomation.perspective/views/Faceplate/Alarms/view.json"
            broken = json.loads(vf.read_text(encoding="utf-8"))
            broken["root"]["children"][0]["events"] = {"component": {"onAckClick": {}}}
            t = broken["propConfig"]["custom.alarms"]["binding"]["transforms"][0]
            t["code"] = t["code"].replace(", no_ack=True", "")
            vf.write_text(json.dumps(broken), encoding="utf-8")
            res = gates.g7_faceplates(out, base)
            self.assertFalse(res["ok"])
            self.assertEqual(len(res["problems"]), 2, res["problems"])

    def test_the_list_layout_rule_lives_in_the_module(self):
        # module 0.2.1 (COB-082): the alarm lists fill their box by the module's own stylesheet, not the parent's
        from hmi import parent as par
        css = (ROOT / "module/gateway/src/main/resources/mounted/css/cadre-ob.css").read_text(encoding="utf-8")
        self.assertIn(".cadre-ob > obc-alert-list-page-small", css)
        prj, _ = par.build_parent()
        sheet = next(v for k, v in prj.files.items() if k.endswith("stylesheet.css")).decode("utf-8")
        self.assertNotIn("obc-alert-list", sheet)
        # a plain major.minor.revision version (GF-27); the release number itself is asserted in test_module.py
        self.assertRegex((ROOT / "module/build.gradle.kts").read_text(encoding="utf-8"), r'version = "\d+\.\d+\.\d+"')

    def test_device_index(self):
        idx = screen.device_index(self.descs)
        # 19 devices and 11 instruments; the overview's cards and fields repeat devices of the diagrams
        self.assertEqual(len(idx), 30)
        fit = next(d for d in idx if d["folder"] == "[default]cadre_hmi_wtp/FIT101")
        # the overview's field comes first; a readout and a field open the same instrument faceplate
        self.assertEqual((fit["kind"], fit["title"], fit["label"], fit["unit"]),
                         ("instrument-field", "FIT-101", "Raw water flow", "m³/h"))
        p502 = next(d for d in idx if d["folder"] == "[default]cadre_hmi_wtp/P502")
        self.assertEqual(p502, {"folder": "[default]cadre_hmi_wtp/P502", "kind": "pump", "title": "P-502",
                                "label": "Distribution pump 2", "unit": ""})

    def test_event_helpers(self):
        ns, calls = AlarmListTests().hmi([AlarmListTests.Event("P502", "High", 1), AlarmListTests.Event("P502", "High", 2)])

        class Ev:
            ids = ["id-P502-1"]
            tagId = "[default]cadre_hmi_wtp/P502"

        class Admin:
            class props:
                class auth:
                    authenticated = True

                    class user:
                        userName = "jo"
                        roles = ["Administrator"]

            class custom:
                alarmScope = "*cadre_hmi_wtp*"
        self.assertEqual(ns["ack_event"](Ev, None), ns["REFUSED"])
        ns["ack_event"](Ev, Admin)
        self.assertEqual(calls[-1], ("ack", ["id-P502-1"], "Acknowledged from the alarm list", "jo"))
        ns["ack_event"]({"ids": ["id-P502-2"]}, Admin, path="W9")
        self.assertEqual(calls[-1][1], ["id-P502-2"])

        class Session:
            class custom:
                devices = [{"folder": "[default]cadre_hmi_wtp/P502", "kind": "pump", "title": "P-502",
                            "label": "Distribution pump 2"}]
        self.assertTrue(ns["select_alarm_device"](Session, Ev))
        self.assertEqual((Session.custom.selectedDevice, Session.custom.selectedKind, Session.custom.selectedTitle),
                         ("[default]cadre_hmi_wtp/P502", "pump", "P-502"))

        class Analyser:
            tagId = "[default]cadre_hmi_wtp/AIT301"
        self.assertFalse(ns["select_alarm_device"](Session, Analyser))


class InterlockTests(unittest.TestCase):
    """The provisional interlock and permissive contract (COB-079): the sample's tag model, the gate
    over it, the faceplate's Interlocks tab and Start refusal, and the helpers, offline."""

    def model(self):
        sys.path.insert(0, str(ROOT / "tools" / "plants"))
        import wtp
        return wtp

    def test_sample_model_passes_the_contract_and_the_gate_catches_breaks(self):
        from hmi import gates
        wtp = self.model()
        res = gates.g7_interlocks(wtp.tag_model())
        self.assertTrue(res["ok"], res["problems"])
        self.assertEqual(res["devices"], ["cadre_hmi_wtp/P101", "cadre_hmi_wtp/P301", "cadre_hmi_wtp/P502"])
        bad = wtp.tag_model()
        ilk = next(t for t in next(f for f in bad["tags"] if f["name"] == "P301")["tags"] if t["name"] == "ilk")
        c01 = next(t for t in ilk["tags"] if t["name"] == "C01")
        next(t for t in c01["tags"] if t["name"] == "kind")["value"] = "warning"
        c01["tags"] = [t for t in c01["tags"] if t["name"] != "requiredText"]
        probs = gates.g7_interlocks(bad)["problems"]
        self.assertTrue(any("kind 'warning'" in p for p in probs), probs)
        self.assertTrue(any("requiredText missing" in p for p in probs), probs)
        # COBD-023: every trip latches; G7 refuses one that does not
        bad = wtp.tag_model()
        ilk = next(t for t in next(f for f in bad["tags"] if f["name"] == "P502")["tags"] if t["name"] == "ilk")
        c01 = next(t for t in ilk["tags"] if t["name"] == "C01")
        next(t for t in c01["tags"] if t["name"] == "latched")["value"] = False
        probs = gates.g7_interlocks(bad)["problems"]
        self.assertEqual(probs, ["cadre_hmi_wtp/P502/ilk/C01: a trip that does not latch (COBD-023)"])

    def test_the_latch_and_its_reset_in_the_model(self):
        wtp = self.model()
        folders = {f["name"]: f for f in wtp.tag_model()["tags"]}
        ilk = {t["name"]: t for t in next(t for t in folders["P502"]["tags"] if t["name"] == "ilk")["tags"]}
        c01 = {t["name"]: t for t in ilk["C01"]["tags"]}
        self.assertEqual((c01["latched"]["value"], c01["bypassable"]["value"], c01["bypassed"]["value"]),
                         (True, False, False))
        # the time the condition was last not met, held by a self reference and cleared by the plant's reset
        self.assertIn("{[.]notMetAt}", c01["notMetAt"]["expression"])
        self.assertIn("[default]cadre_hmi_wtp/sim/reset", c01["notMetAt"]["expression"])
        # met again, latched, and last not met after the last reset request
        self.assertIn("{[default]cadre_hmi_wtp/P502/ilk/resetSeen}", c01["resetRequired"]["expression"])
        self.assertEqual((ilk["resetAt"]["valueSource"], ilk["resetAt"]["dataType"]), ("memory", "Int8"))
        # an import returns resetAt to 0 but leaves a self reference at its value (GF-42): resetSeen keeps the
        # latest request, so a trip reset before an import is not latched again; the plant's reset clears it
        seen = ilk["resetSeen"]["expression"]
        self.assertIn("{[.]resetSeen}", seen)
        self.assertIn("{[.]resetAt}", seen)
        self.assertIn("[default]cadre_hmi_wtp/sim/reset", seen)
        self.assertIn("C01/resetRequired", ilk["interlocked"]["expression"])
        self.assertIn("C01/resetRequired", ilk["resetRequired"]["expression"])
        # a permissive does not latch, and the sample's permissives may be bypassed
        p301 = {t["name"]: t for t in next(t for t in next(t for t in folders["P301"]["tags"] if t["name"] == "ilk")["tags"]
                                           if t["name"] == "C01")["tags"]}
        self.assertEqual((p301["latched"]["value"], p301["bypassable"]["value"]), (False, True))

    def test_state_holds_a_start_and_the_badge_is_bound(self):
        wtp = self.model()
        folders = {f["name"]: f for f in wtp.tag_model()["tags"]}
        state = next(t for t in folders["P101"]["tags"] if t["name"] == "state")["expression"]
        self.assertIn("{[.]ilk/permitted}", state)
        self.assertIn("{[.]ilk/interlocked}", state)
        plain = next(t for t in folders["P501"]["tags"] if t["name"] == "state")["expression"]
        self.assertNotIn("ilk", plain)
        bound = {s["id"]: s["bind"].get("badgeInterlock") for s in wtp.disinfection()["symbols"] if "bind" in s}
        self.assertEqual(bound["P502"], "P502/ilk/badge")
        self.assertIsNone(bound["P501"])

    def test_faceplate_interlocks_tab_and_start_refusal(self):
        from hmi import framework
        fp = framework.faceplate("pump")
        nodes = {}

        def walk(n):
            nodes[n.get("meta", {}).get("name")] = n
            for c in n.get("children") or []:
                walk(c)
        walk(fp["root"])
        self.assertEqual(nodes["Tab_interlocks"]["propConfig"]["position.display"]["binding"]["config"]["expression"],
                         "{view.custom.ilk.present}")
        self.assertEqual(nodes["Conditions"]["props"]["path"], "Faceplate/InterlockRow")
        self.assertIn("cadre.hmi.start_permitted", nodes["On"]["events"]["component"]["onActionPerformed"]["config"]["script"])
        self.assertIn("HeldRow", nodes)
        self.assertNotIn("Tab_interlocks", json.dumps(framework.faceplate_tank()))
        row = framework.faceplate_interlock_row()
        self.assertEqual(row["propConfig"]["custom.ok"]["binding"]["config"]["tagPath"], "{0}/ilk/{1}/ok")
        self.assertEqual(row["propConfig"]["custom.resetRequired"]["binding"]["config"]["tagPath"],
                         "{0}/ilk/{1}/resetRequired")
        # the latch's Reset (COBD-023), shown while a latched trip waits for it
        self.assertEqual(nodes["ResetRow"]["propConfig"]["position.display"]["binding"]["config"]["expression"],
                         "{view.custom.ilk.resetRequired}")
        self.assertIn("'path': 'W11'",   # F029: Reset asks; the Confirm row makes the write
                      nodes["ResetInterlocks"]["events"]["component"]["onActionPerformed"]["config"]["script"])

    def test_helpers(self):
        from hmi import scripts
        tags = {"[default]t/P1/ilk/C01/ok": True, "[default]t/P1/ilk/C02/ok": False,
                "[default]t/P1/ilk/permitted": False, "[default]t/P1/ilk/interlocked": False,
                "[default]t/P1/ilk/bypassed": False, "[default]t/P1/ilk/unsatisfied": 1,
                # P3: its one trip met again, latched and waiting for a reset (COBD-023)
                "[default]t/P3/ilk/C01/ok": True, "[default]t/P3/ilk/C01/resetRequired": True,
                "[default]t/P3/ilk/permitted": True, "[default]t/P3/ilk/interlocked": True,
                "[default]t/P3/ilk/bypassed": False, "[default]t/P3/ilk/unsatisfied": 0,
                "[default]t/P3/ilk/resetRequired": True}

        class QV:
            def __init__(self, v):
                self.value = v

        class Tag:
            @staticmethod
            def exists(p):
                return p in tags

            @staticmethod
            def readBlocking(paths):
                return [QV(tags.get(p)) for p in paths]

        class System:
            tag = Tag
        ns = {"unicode": str, "long": int, "system": System}
        exec(scripts.HMI, ns)
        self.assertEqual([r["cid"] for r in ns["interlock_rows"]("[default]t/P1")], ["C01", "C02"])
        self.assertEqual(ns["interlock_rows"]("[default]t/P2"), [])
        s = ns["interlock_summary"]("[default]t/P1")
        self.assertEqual((s["present"], s["permitted"], s["unsatisfied"]), (True, False, 1))
        self.assertFalse(ns["start_permitted"]("[default]t/P1"))
        self.assertTrue(ns["start_permitted"]("[default]t/P2"))   # no interlocks: always permitted
        self.assertFalse(s["resetRequired"])
        self.assertEqual(s["holding"], 1)
        s3 = ns["interlock_summary"]("[default]t/P3")   # the tab counts the latched condition
        self.assertEqual((s3["unsatisfied"], s3["resetRequired"], s3["holding"]), (0, True, 1))
        self.assertFalse(ns["start_permitted"]("[default]t/P3"))

    def test_reset_writes_the_request_time(self):
        from hmi import scripts
        written = []

        class Tag:
            @staticmethod
            def exists(p):
                return p == "[default]t/P1/ilk/resetAt"

            @staticmethod
            def writeBlocking(paths, values):
                written.append((paths, values))
                return ["Good"] * len(paths)

        class Date:
            @staticmethod
            def now():
                return 1791500000000

            @staticmethod
            def toMillis(d):
                return d

        class System:
            tag = Tag
            date = Date
        ns = {"unicode": str, "long": int, "system": System}
        exec(scripts.HMI, ns)
        admin = CommandSecurityTests().session(["Administrator"], devices=("[default]t/P1", "[default]t/P2"))
        self.assertEqual(ns["reset_interlocks"](admin, "[default]t/P1"), "")
        self.assertEqual(written, [(["[default]t/P1/ilk/resetAt"], [1791500000000])])
        self.assertTrue(ns["reset_interlocks"](admin, "[default]t/P2").startswith("Refused"))   # no interlocks
        self.assertEqual(ns["reset_interlocks"](CommandSecurityTests().session(None), "[default]t/P1"), ns["REFUSED"])
        self.assertEqual(len(written), 1)


class CommandSecurityTests(unittest.TestCase):
    """Command security (COB-063, COBD-024; NOTE-COB-04 Table 6 tests T1, T2 and the checks of section
    6.2), offline: the permission table, the checked writes against stub sessions, and gate G7."""

    class Auth:
        def __init__(self, roles, name="someone"):
            self.authenticated = roles is not None
            self.user = type("U", (), {"roles": roles, "userName": name if roles is not None else None})()

    def session(self, roles, devices=("[default]t/P1",)):
        auth = self.Auth(roles)
        props = type("P", (), {"auth": auth})()
        custom = type("C", (), {"devices": [{"folder": d} for d in devices], "alarmScope": "*t*"})()
        return type("S", (), {"props": props, "custom": custom})()

    def hmi(self, tags=None):
        from hmi import scripts
        tags = dict(tags or {})
        calls = []

        class QV:
            def __init__(self, v):
                self.value = v

        class Tag:
            @staticmethod
            def exists(p):
                return p in tags

            @staticmethod
            def readBlocking(paths):
                return [QV(tags.get(p)) for p in paths]

            @staticmethod
            def writeBlocking(paths, values):
                calls.append(("write", list(paths), list(values)))
                return ["Good"] * len(paths)

        class Alarm:
            @staticmethod
            def queryStatus(path=None, state=None, priority=None):
                return [AlarmListTests.Event("P1", "High", 5)]

            @staticmethod
            def acknowledge(ids, notes, user):
                calls.append(("ack", list(ids), user))
                return []

        class Date:
            @staticmethod
            def now():
                return 7

            @staticmethod
            def toMillis(d):
                return d

        class System:
            tag, alarm, date = Tag, Alarm, Date
        ns = {"unicode": str, "long": int, "system": System}
        exec(scripts.HMI, ns)
        return ns, calls

    def test_t1_every_write_path_needs_the_admin_role(self):
        ns, _ = self.hmi()
        self.assertEqual(ns["WRITE_PATHS"], [f"W{i}" for i in range(1, 20)])   # W12 to W17: stage 2; W18: 2b; W19: COBD-045
        self.assertEqual(set(map(tuple, ns["PERMITTED"].values())), {("Administrator",)})
        self.assertEqual(ns["permissions"](self.session(None)), {w: False for w in ns["WRITE_PATHS"]})
        self.assertEqual(ns["permissions"](self.session(["Administrator"])), {w: True for w in ns["WRITE_PATHS"]})
        self.assertFalse(ns["allowed"](self.session(["Operator"]), "W1"))

    def test_the_checked_writes_refuse_and_write(self):
        ns, calls = self.hmi({"[default]t/P1/ilk/C01/bypassable": True, "[default]t/P1/ilk/C02/bypassable": False,
                              "[default]t/P1/ilk/resetAt": 0})
        anon, admin = self.session(None), self.session(["Administrator"])
        self.assertEqual(ns["command"](anon, "W1", "[default]t/P1", "cmd", False), ns["REFUSED"])
        self.assertEqual(ns["bypass"](anon, "[default]t/P1", "C01", True), ns["REFUSED"])
        self.assertEqual(ns["reset_interlocks"](anon, "[default]t/P1"), ns["REFUSED"])
        self.assertEqual(ns["ack_top"]("*t*", anon), ns["REFUSED"])
        self.assertEqual(ns["ack"](["id-P1-5"], anon), ns["REFUSED"])
        self.assertEqual(calls, [])                                   # nothing written, nothing acknowledged
        self.assertEqual(ns["command"](admin, "W1", "[default]t/P1", "cmd", False), "")
        self.assertEqual(calls[-1], ("write", ["[default]t/P1/cmd"], [False]))
        self.assertTrue(ns["command"](admin, "W1", "[default]t/P1", "mode", 2).startswith("Refused"))   # not W1's member
        self.assertTrue(ns["command"](admin, "W5", "[default]t/P1", "fault", True).startswith("Refused"))   # only clears
        self.assertTrue(ns["command"](admin, "W1", "[default]other/X", "cmd", True).startswith("Refused"))   # not ours
        # a start honours the interlocks on the gateway too, so no start is left pending
        held_ns, held_calls = self.hmi({"[default]t/P1/ilk/permitted": False, "[default]t/P1/ilk/interlocked": False,
                                        "[default]t/P1/ilk/bypassed": False, "[default]t/P1/ilk/unsatisfied": 1,
                                        "[default]t/P1/ilk/resetRequired": False})
        self.assertEqual(held_ns["command"](admin, "W1", "[default]t/P1", "cmd", True), "Refused: interlocks hold the device")
        self.assertEqual(held_ns["command"](admin, "W1", "[default]t/P1", "cmd", False), "")   # a stop is never held
        self.assertEqual(held_calls, [("write", ["[default]t/P1/cmd"], [False])])
        self.assertEqual(ns["bypass"](admin, "[default]t/P1", "C01", True), "")
        self.assertEqual(calls[-1], ("write", ["[default]t/P1/ilk/C01/bypassed"], [True]))
        self.assertTrue(ns["bypass"](admin, "[default]t/P1", "C02", True).startswith("Refused"))   # not bypassable
        self.assertEqual(ns["reset_interlocks"](admin, "[default]t/P1"), "")
        self.assertEqual(calls[-1], ("write", ["[default]t/P1/ilk/resetAt"], [7]))
        n = len(calls)
        ns["ack"](["id-P1-5", "not-in-scope"], admin, path="W9")       # out of scope ids are dropped
        self.assertEqual(calls[n:], [("ack", ["id-P1-5"], "someone")])
        self.assertIsNone(ns["session_user"](anon))                    # no made up "operator"

    def test_t2_g7_refuses_a_direct_write(self):
        from hmi import gates, parent as par
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            res = gates.g7_commands(base, None)
            self.assertTrue(res["ok"], res["problems"])
            vf = base / "com.inductiveautomation.perspective/views/Faceplate/Pump/view.json"
            doc = json.loads(vf.read_text(encoding="utf-8"))
            text = json.dumps(doc).replace("cadre.hmi.command(self.session, p.path, self.view.params.deviceId, p.member, p.value)",
                                           "system.tag.writeBlocking([self.view.params.deviceId + '/cmd'], [False])")
            vf.write_text(text, encoding="utf-8")
            probs = gates.g7_commands(base, None)["problems"]
            self.assertTrue(any("direct system.tag.write" in p for p in probs), probs)
            # an enabled bound to a constant does not follow the permissions
            vf.write_text(json.dumps(doc).replace("{view.custom.can.W2}", "true"), encoding="utf-8")
            probs = gates.g7_commands(base, None)["problems"]
            self.assertTrue(any("does not follow the permissions" in p for p in probs), probs)


class TrendPageTests(unittest.TestCase):
    """The trend page (COB-064): the generator lists the descriptors' devices whose trended member the
    tag model historises, adds the route and the navigation item, and the parent carries the views."""

    def test_trend_index_route_and_views(self):
        from hmi import gates, parent as par
        descs = [json.loads((ROOT / f"screens/wtp/{n}.json").read_text(encoding="utf-8"))
                 for n in ("overview", "intake", "filtration", "disinfection")]
        model = json.loads((ROOT / "screens/wtp/tags.json").read_text(encoding="utf-8"))
        idx = screen.trend_index(descs, model)
        self.assertEqual(len(idx), 17)                                   # 11 instruments, 6 tanks
        self.assertEqual(sum(1 for t in idx if t["member"] == "level"), 6)
        tk = next(t for t in idx if t["title"] == "TK-101")
        self.assertEqual((tk["deviceId"], tk["member"], tk["kind"], tk["unit"]),
                         ("[default]cadre_hmi_wtp/TK101", "level", "tank", "%"))
        self.assertEqual(screen.trend_index(descs, None), [])            # no model, nothing known historised
        child, _ = screen.build_child("cadre_hmi_t", descs, "T", tag_model=model)
        pc = json.loads(child.files["com.inductiveautomation.perspective/page-config/config.json"])
        self.assertEqual(pc["pages"]["/trends"]["viewPath"], "Framework/TrendsPage")
        sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
        self.assertIn({"label": "Trends", "path": "/trends", "icon": "trend"}, sp["custom"]["nav"]["items"])
        self.assertEqual(len(sp["custom"]["trends"]), 17)
        plain, _ = screen.build_child("cadre_hmi_t", descs, "T")
        self.assertNotIn("/trends", json.loads(plain.files["com.inductiveautomation.perspective/page-config/config.json"])["pages"])
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            out = child.write(Path(d))
            self.assertTrue(gates.g4_project(out, base)["ok"])
            self.assertTrue(gates.g7_history(out, base)["ok"])           # the card's history binding


class InstrumentTests(unittest.TestCase):
    """The analogue instrument faceplate and the trend (COB-062, COB-064): the history binding rule,
    the faceplate, selectable readouts, limits that move their alarms, and the helpers offline."""

    def test_history_binding_needs_an_array(self):
        with self.assertRaises(ValueError):
            pv.tag_history("[default]x/value", "1")       # a path string: the runtime rejects it
        with self.assertRaises(ValueError):
            pv.tag_history([{"alias": "x"}], "1")         # an entry without a path
        b = pv.tag_history("{view.custom.historyTags}", "{view.custom.hours}", "HOUR")
        self.assertEqual((b["type"], b["config"]["tags"], b["config"]["dateRange"]["mostRecent"]),
                         ("tag-history", "{view.custom.historyTags}", "{view.custom.hours}"))
        self.assertEqual(pv.tag_history([{"path": "[default]x/value"}], "1")["config"]["tags"][0]["path"],
                         "[default]x/value")

    def test_trend_and_gate(self):
        from hmi import framework, gates
        fp = framework.faceplate_instrument()
        nodes = {}

        def walk(n):
            nodes[n.get("meta", {}).get("name")] = n
            for c in n.get("children") or []:
                walk(c)
        walk(fp["root"])
        chart = nodes["Chart"]
        self.assertEqual(chart["type"], "ia.chart.timeseries")
        self.assertEqual(chart["propConfig"]["props.series[0].data"]["binding"]["type"], "tag-history")
        self.assertEqual(fp["custom"]["historyTags"], [{"path": "", "alias": "value"}])
        with tempfile.TemporaryDirectory() as d:
            from hmi import parent as par
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            self.assertTrue(gates.g7_history(base, None)["ok"])
            vf = base / "com.inductiveautomation.perspective/views/Faceplate/Instrument/view.json"
            doc = json.loads(vf.read_text(encoding="utf-8"))
            doc["custom"]["historyTags"] = "[default]x/value"     # a string: refused
            vf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertFalse(gates.g7_history(base, None)["ok"])

    def test_readouts_are_selectable_and_limits_move_alarms(self):
        contracts = screen.load_contracts()
        for v in ("Automation/Readout", "Instrument/Field"):
            self.assertIn("deviceId", contracts[v]["params"])
        sys.path.insert(0, str(ROOT / "tools" / "plants"))
        import wtp
        folders = {f["name"]: f for f in wtp.tag_model()["tags"]}
        ait = folders["AIT301"]["tags"]
        self.assertEqual(next(t for t in ait if t["name"] == "value")["alarms"][0]["setpointA"],
                         {"bindType": "Expression", "value": "{[.]hiLimit}"})
        self.assertIn("hiLimit", [t["name"] for t in ait])
        lvl = next(t for t in folders["TK501"]["tags"] if t["name"] == "level")
        self.assertEqual([a["setpointA"]["value"] for a in lvl["alarms"]], ["{[.]hiLimit}", "{[.]loLimit}"])

    def test_helpers(self):
        from hmi import scripts
        tags = {"[default]t/A1/hiLimit": 1.0, "[default]t/A1/value": 0.2}

        class QV:
            def __init__(self, v):
                self.value = v

        class Tag:
            @staticmethod
            def exists(p):
                return p in tags

            @staticmethod
            def readBlocking(paths):
                return [QV(tags.get(p)) for p in paths]

        class Date:
            @staticmethod
            def now():
                return 10 * 3600 * 1000

            @staticmethod
            def addHours(d, h):
                return d + h * 3600 * 1000

            @staticmethod
            def toMillis(d):
                return d

        class System:
            tag = Tag
            date = Date
        ns = {"unicode": str, "long": int, "system": System}
        exec(scripts.HMI, ns)
        self.assertEqual(ns["limit_rows"]("[default]t/A1"),   # without a session nothing may be written
                         [{"deviceId": "[default]t/A1", "member": "hiLimit", "label": "High limit", "writable": False}])
        self.assertEqual(ns["history_tags"]("[default]t/A1"), [{"path": "[default]t/A1/value", "alias": "value"}])
        pts = ns["limit_series"]("[default]t/A1", 8)
        self.assertEqual([p["time"] for p in pts], [2 * 3600 * 1000, 10 * 3600 * 1000])
        self.assertEqual(pts[0]["hiLimit"], 1.0)
        self.assertEqual(ns["limit_series"]("[default]t/B9", 1), [])


# ---------------------------------------------------------------------------------------
# Stage 2: faceplates that list what a device carries, the device model, the controller, the
# digital input and the maintenance functions.
# ---------------------------------------------------------------------------------------
FIXTURES = ROOT / "tests" / "fixtures"
PILOT = "[default]cadre_hmi_pilot"


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def hmi_ns(tags=None, bad=(), events=(), refuse=()):
    """`cadre.hmi`, Jython held as text, run under CPython against fakes: `tags` is {path: value},
    the paths in `bad` read with a quality that is not good, `events` answer every alarm query, and
    the gateway refuses a write to a path in `refuse` as it refuses an expression tag (GF-49): the tag
    keeps its value and the write answers `Bad_ReadOnly`. Returns the namespace and the list of calls
    made (reads, writes, queries)."""
    from hmi import scripts
    tags = tags if tags is not None else {}
    calls = []

    class QV:
        def __init__(self, path):
            self.value = tags.get(path)
            self.quality = 'Bad_NotFound("Path not found.")' if path in bad else "Good"

    class Tag:
        @staticmethod
        def exists(path):
            return path in tags

        @staticmethod
        def readBlocking(paths):
            calls.append(("read", list(paths)))
            return [QV(p) for p in paths]

        @staticmethod
        def writeBlocking(paths, values):
            calls.append(("write", list(paths), list(values)))
            out = []
            for p, v in zip(paths, values):
                if p in refuse:
                    out.append('Bad_ReadOnly("Tag value source does not support writing.")')
                else:
                    tags[p] = v
                    out.append("Good")
            return out

    class Alarm:
        @staticmethod
        def queryStatus(path=None, state=None, priority=None):
            calls.append(("query", list(path)))
            return list(events)

    class Date:
        @staticmethod
        def now():
            return 7

        @staticmethod
        def toMillis(d):
            return d

    class System:
        tag, alarm, date = Tag, Alarm, Date
    ns = {"unicode": str, "long": int, "system": System}
    exec(scripts.HMI, ns)
    return ns, calls


def session(roles, devices=(), trends=(), model=None):
    """A session: `roles` None for nobody signed in; `devices` the entries of the device index;
    `model` the `deviceModel` flag a build with a device model sets (left out: no such property)."""
    auth = CommandSecurityTests.Auth(roles)
    custom = type("C", (), {"devices": [dict(d) for d in devices], "trends": [dict(t) for t in trends],
                            "alarmScope": "*cadre_hmi_pilot*"})()
    if model is not None:
        custom.deviceModel = model
    return type("S", (), {"props": type("P", (), {"auth": auth})(), "custom": custom})()


def view_nodes(doc):
    out = {}

    def walk(n):
        out[n.get("meta", {}).get("name")] = n
        for c in n.get("children") or []:
            walk(c)
    walk(doc["root"])
    return out


def bindings(doc):
    """Every binding of a view, view level and component level: (where, key, binding)."""
    out = [("view", k, c["binding"]) for k, c in (doc.get("propConfig") or {}).items() if "binding" in c]

    def walk(n):
        for k, c in (n.get("propConfig") or {}).items():
            if "binding" in c:
                out.append((n["meta"]["name"], k, c["binding"]))
        for c in n.get("children") or []:
            walk(c)
    walk(doc["root"])
    return out


def display(node):
    return node["propConfig"]["position.display"]["binding"]["config"]["expression"]


def shown(expr, dev):
    """A display expression over `custom.dev`, evaluated for one answer of `device_read`."""
    py = re.sub(r"\{view\.custom\.dev\.(\w+)(?:\.(\w+))?\}",
                lambda m: repr(dev[m.group(1)][m.group(2)] if m.group(2) else dev[m.group(1)]), expr)
    return bool(eval(py.replace("||", " or ").replace("&&", " and ").replace("!", " not ")))


class DeviceReadTests(unittest.TestCase):
    """`cadre.hmi.device_read` (wiki page 13 section 9): one poll that says which members a device
    carries, their values, their quality and what a session may write; and the faceplates that
    derive every row from it and bind no member's tag."""

    PUMP = ["state", "cmd", "mode", "fault", "speed", "speedSp", "mnt/forceOn", "mnt/forceOff", "mnt/forceMode",
            "mnt/forceValue", "mnt/errorMask", "mnt/simulated", "mnt/alarmSuppress", "mnt/manualMode"]
    D = "[default]t/P1"

    def test_each_member_present_and_absent(self):
        full = {f"{self.D}/{m}": v for m, v in (("state", True), ("cmd", True), ("mode", 2), ("fault", False),
                                                 ("speed", 61), ("speedSp", 60.0))}
        ns, calls = hmi_ns(full)
        admin = session(["Administrator"], [{"folder": self.D}])
        got = ns["device_read"](admin, self.D, self.PUMP)
        for m in ("state", "cmd", "mode", "fault", "speed", "speedSp"):
            self.assertTrue(got["has"][m], m)
        self.assertEqual((got["value"]["state"], got["value"]["mode"], got["value"]["speed"]), (True, 2, 61.0))
        self.assertIsInstance(got["value"]["speed"], float)          # typed as the member's default
        self.assertFalse(got["has"]["mnt_forceOn"])                  # the slash of `mnt/` is an underscore
        self.assertEqual((got["mnt"], got["force"], got["quality"], got["bad"]), (False, "", "", []))
        # one member at a time is taken away: it reads as absent, its typed default stands in, it is never read
        for m in ("state", "cmd", "mode", "fault", "speed", "speedSp"):
            tags = {k: v for k, v in full.items() if not k.endswith("/" + m)}
            ns, calls = hmi_ns(tags)
            got = ns["device_read"](admin, self.D, self.PUMP)
            self.assertFalse(got["has"][m], m)
            self.assertEqual(got["value"][m], ns["MEMBER_DEFAULTS"][m], m)
            self.assertIsNotNone(got["value"][m])
            self.assertFalse(got["writable"][m] or got["write"][m], m)
            self.assertNotIn(f"{self.D}/{m}", [x for c in calls if c[0] == "read" for x in c[1]])
        self.assertEqual(len([c for c in calls if c[0] == "read"]), 1)   # one read for the whole device

    def test_what_a_session_may_write(self):
        tags = {f"{self.D}/{m}": False for m in ("state", "cmd", "fault")}
        ns, _ = hmi_ns(tags)
        plain = [{"folder": self.D}]
        admin, anon = session(["Administrator"], plain), session(None, plain)
        got = ns["device_read"](admin, self.D, self.PUMP)
        self.assertEqual((got["writable"]["cmd"], got["write"]["cmd"]), (True, True))
        self.assertEqual((got["writable"]["fault"], got["write"]["fault"]), (True, True))   # no model: today's rule
        self.assertFalse(got["writable"]["state"])                   # no write path writes a state
        got = ns["device_read"](anon, self.D, self.PUMP)
        self.assertEqual((got["writable"]["cmd"], got["write"]["cmd"]), (True, False))      # shown, disabled
        # a device model marks the fault a status of the source: no session may write it
        model = session(["Administrator"], [{"folder": self.D, "write": ["cmd"], "members": ["state", "cmd", "fault"]}])
        got = ns["device_read"](model, self.D, self.PUMP)
        self.assertEqual((got["writable"]["cmd"], got["writable"]["fault"], got["write"]["fault"]), (True, False, False))
        # a folder that is no device of the session's project is read, and nothing of it may be written
        got = ns["device_read"](session(["Administrator"], []), self.D, self.PUMP)
        self.assertTrue(got["has"]["cmd"])
        self.assertFalse(got["writable"]["cmd"])

    def test_bad_quality_is_named(self):
        tags = {f"{self.D}/state": None, f"{self.D}/fault": True}
        ns, _ = hmi_ns(tags, bad=[f"{self.D}/state"])
        got = ns["device_read"](session(None, [{"folder": self.D}]), self.D, self.PUMP)
        self.assertEqual(got["bad"], ["state"])
        self.assertEqual(got["quality"], "Bad quality: state")
        self.assertIs(got["value"]["state"], False)                  # null never reaches an expression
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import faceplates
        self.assertTrue(got["quality"].startswith(faceplates.QUALITY_LINE))   # the line G11 fails on

    def test_force_state_and_no_device(self):
        ns, _ = hmi_ns({f"{self.D}/mnt/forceOn": False, f"{self.D}/mnt/forceOff": True})
        admin = session(["Administrator"], [{"folder": self.D}])
        got = ns["device_read"](admin, self.D, self.PUMP)
        self.assertEqual((got["mnt"], got["force"], got["writable"]["force"], got["write"]["force"]),
                         (True, "off", True, True))
        ns, _ = hmi_ns({f"{self.D}/mnt/forceMode": True, f"{self.D}/mnt/forceValue": True, f"{self.D}/mnt/forceOn": True})
        got = ns["device_read"](session(["Administrator"], [{"folder": self.D, "write": ["mnt/forceMode"]}]),
                                self.D, self.PUMP)
        self.assertEqual((got["force"], got["writable"]["force"]), ("on", False))   # the value is read only
        ns, _ = hmi_ns({f"{self.D}/mnt/forceOn": True})              # half a pair is no force function,
        got = ns["device_read"](admin, self.D, self.PUMP)            # and no Maintenance tab with nothing in it
        self.assertEqual((got["force"], got["mnt"], got["has"]["mnt_forceOn"]), ("", False, True))
        ns, _ = hmi_ns({f"{self.D}/mnt/forceOn": True, f"{self.D}/mnt/simulated": False})
        self.assertTrue(ns["device_read"](admin, self.D, self.PUMP)["mnt"])   # a flag is a row
        # no device selected: the structure every view starts from
        from hmi import framework
        for kind, members in framework.FACEPLATE_READS.items():
            self.assertEqual(framework.dev_default(members), ns["device_read"](None, "", members), kind)

    def test_no_faceplate_binds_a_member_tag(self):
        from hmi import framework
        views = framework.framework_views()
        for path in ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/Tank", "Faceplate/Instrument",
                     "Faceplate/Controller", "Faceplate/Input", "Faceplate/Sequence"):
            tagged = [(w, k) for w, k, b in bindings(views[path]) if b["type"] == "tag"]
            self.assertEqual(tagged, [], path)
            poll = views[path]["propConfig"]["custom.dev"]["binding"]
            self.assertIn("now(1000)", poll["config"]["expression"])
            self.assertIn("cadre.hmi.device_read(self.session, value, [", poll["transforms"][0]["code"])
            self.assertIn("{view.custom.dev.quality}", json.dumps(view_nodes(views[path])["Quality"]))
        # the rows that do bind a tag are views of their own, instantiated only for a member that exists
        rows = {p: [b["config"]["tagPath"] for _w, _k, b in bindings(views[p]) if b["type"] == "tag"]
                for p in ("Faceplate/SetpointRow", "Faceplate/LimitRow")}
        self.assertEqual(rows["Faceplate/SetpointRow"], ["{0}/{1}"])
        self.assertTrue(all(not b["config"].get("bidirectional") for p in rows for _w, _k, b in bindings(views[p])
                            if b["type"] == "tag"))

    def test_a_status_only_pump_shows_state_and_fault_and_nothing_else(self):
        from hmi import framework
        tags = {f"{self.D}/state": True, f"{self.D}/fault": True}
        ns, _ = hmi_ns(tags)
        model = session(["Administrator"], [{"folder": self.D, "write": [], "members": ["fault", "state"]}])
        dev = ns["device_read"](model, self.D, framework.FACEPLATE_READS["pump"])
        nodes = view_nodes(framework.faceplate("pump"))
        control = ["StatusTitle", "StateRow", "ModeRow", "FaultRow", "SpeedRow", "CommandTitle", "Commands", "Modes",
                   "SpeedSp", "Reset"]
        self.assertEqual([n for n in control if shown(display(nodes[n]), dev)], ["StatusTitle", "StateRow", "FaultRow"])
        self.assertFalse(shown(display(nodes["Tab_maintenance"]), dev))
        # every child of the Control pane but the refusal line and the held line carries a display condition
        for c in nodes["Pane_control"]["children"]:
            self.assertIn("position.display", c.get("propConfig") or {}, c["meta"]["name"])
        # the same pump with every member, in a project without a device model: the faceplate of before
        full = {f"{self.D}/{m}": v for m, v in (("state", True), ("cmd", True), ("mode", 0), ("fault", True),
                                                 ("speed", 80.0), ("speedSp", 80.0))}
        ns, _ = hmi_ns(full)
        dev = ns["device_read"](session(["Administrator"], [{"folder": self.D}]), self.D, framework.FACEPLATE_READS["pump"])
        self.assertEqual([n for n in control if shown(display(nodes[n]), dev)], control)
        texts = json.dumps(framework.faceplate("pump"))
        for t in ("Running", "Stopped", "Start", "Stop", "Auto", "Manual", "Local", "Reset fault",
                  "Speed setpoint (%)", "Start refused", "Control mode"):
            self.assertIn(t, texts, t)
        # a valve that carries a fault shows it; one that does not shows what it showed before
        valve = view_nodes(framework.faceplate("valve"))
        self.assertEqual(display(valve["FaultRow"]), "{view.custom.dev.has.fault}")
        self.assertNotIn("SpeedSp", valve)

    def test_setpoint_row_keeps_the_typed_text(self):
        """A setpoint field is bound one way to its tag, which hands it a value when the member
        changes and not at each poll; nothing of the polled structure reaches `props.value`."""
        from hmi import framework
        row = framework.faceplate_setpoint_row()
        field = view_nodes(row)["Setpoint"]
        b = field["propConfig"]["props.value"]["binding"]
        self.assertEqual((b["type"], b["config"]["mode"], b["config"]["tagPath"]), ("tag", "indirect", "{0}/{1}"))
        self.assertLessEqual(set(b["config"]), {"mode", "references", "tagPath"})   # IGW:06 section 4, one way
        self.assertNotIn("custom.dev", json.dumps(row))
        self.assertIn("{view.custom.can.W3}", field["propConfig"]["props.enabled"]["binding"]["config"]["expression"])
        self.assertEqual(field["events"]["component"]["onActionPerformed"]["config"]["script"],   # F029: it only holds
                         "".join("\t" + ln + "\n" for ln in framework.ROW_HOLD).rstrip("\n"))
        self.assertIn("cadre.hmi.command(self.session, p.path, p.deviceId, p.member, self.view.custom.typed)",
                      view_nodes(row)["Set"]["events"]["component"]["onActionPerformed"]["config"]["script"])
        # the repeater holds the row while the device carries the member, and none otherwise
        rep = view_nodes(framework.faceplate("pump"))["SpeedSp"]
        self.assertEqual((rep["type"], rep["props"]["path"]), ("ia.display.flex-repeater", "Faceplate/SetpointRow"))
        cfg = rep["propConfig"]["props.instances"]["binding"]
        self.assertTrue(cfg["config"]["expression"].startswith("if({view.custom.dev.has.speedSp}, {view.params.deviceId}"))
        code = cfg["transforms"][0]["code"]
        scope = {}
        exec("def f(value):\n" + code, scope)
        self.assertEqual(scope["f"](""), [])
        self.assertEqual(scope["f"]("[default]t/P1|1|"), [{
            "member": "speedSp", "label": "Speed setpoint (%)", "path": "W3", "format": "0.0", "minimum": 0,
            "maximum": 100, "deviceId": "[default]t/P1", "enabled": True, "unit": ""}])
        self.assertFalse(scope["f"]("[default]t/P1|0|%")[0]["enabled"])

    def test_a_rows_refusal_does_not_follow_it_to_another_device(self):
        """A repeater keeps a row's view while its instance changes, so a row that read "Refused" on
        one device read it on the next one opened (found by the generated walk on 2026-10-11). The row
        clears its message when it is handed another device or another member, by a change script on
        the parameter (IGW:09-params-and-custom section 6), and by nothing else: an accepted write
        clears it through the write's own answer."""
        from hmi import framework
        for row in (framework.faceplate_setpoint_row(), framework.faceplate_limit_row()):
            self.assertEqual(row["custom"]["message"], "")
            for param in ("deviceId", "member"):
                cfg = row["propConfig"][f"params.{param}"]
                self.assertEqual(cfg["paramDirection"], "input", param)
                self.assertEqual(cfg["onChange"], {"enabled": None,
                                                   "script": "\tself.custom.message = ''\n\tself.custom.pending = False"}, param)
            # no other parameter clears it, and the change script writes nothing but the message and the hold (F029)
            changing = [k for k, v in row["propConfig"].items() if isinstance(v, dict) and "onChange" in v]
            self.assertEqual(sorted(changing), ["params.deviceId", "params.member"])
            # the text an operator reads still follows the message
            shown = [n for n in view_nodes(row).values()
                     if "{view.custom.message}" in json.dumps(n.get("propConfig", {}).get("props.text", ""))]
            self.assertEqual(len(shown), 1)
            self.assertIn("'Refused'", json.dumps(shown[0]["propConfig"]["props.text"]))

    def test_limit_rows_and_history_need_their_member(self):
        ns, _ = hmi_ns({"[default]t/A1/hiLimit": 1.0, "[default]t/A2/hiLimit": 1.0, "[default]t/A2/value": 0.5})
        self.assertEqual(ns["limit_rows"]("[default]t/A1", "value"), [])      # no value to compare the limit with
        self.assertEqual(len(ns["limit_rows"]("[default]t/A2", "value")), 1)
        self.assertEqual(len(ns["limit_rows"]("[default]t/A1")), 1)           # the callers of before
        self.assertEqual(ns["history_tags"]("[default]t/A1"), [{"path": "", "alias": "value"}])
        self.assertEqual(ns["history_tags"]("[default]t/A2"), [{"path": "[default]t/A2/value", "alias": "value"}])


class DeviceModelTests(unittest.TestCase):
    """The device model (`--devices-file`, wiki page 08 section 3.1): the device index, the alarm
    sources, the trend index, the generated tags and gate G7 devices, on the fixture of tests/fixtures."""

    def setUp(self):
        self.desc, self.model, self.tags = (fixture("pilot-supply.json"), fixture("pilot-devices.json"),
                                            fixture("pilot-tags.json"))

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def test_the_model_validates_and_a_broken_one_does_not(self):
        self.assertEqual(screen.devices_schema_errors(self.model, "m"), [])
        self.assertEqual(screen.schema_errors([self.desc], ["d"]), [])           # the new kinds need no schema change
        bad = copy.deepcopy(self.model)
        bad["devices"][0]["members"]["state"]["access"] = "both"
        bad["devices"][1]["members"]["bad name"] = {"type": "Boolean", "access": "read"}
        bad["devices"][2]["alarmSources"] = ["a,b"]
        del bad["devices"][3]["kind"]
        self.assertEqual(len(screen.devices_schema_errors(bad, "m")), 4)

    def test_device_index_with_and_without_a_model(self):
        plain = screen.device_index([self.desc])
        self.assertEqual([sorted(d) for d in plain], [["folder", "kind", "label", "title", "unit"]] * 8)
        self.assertEqual({d["folder"].split("/")[-1]: d["kind"] for d in plain},
                         {"DI1": "indicator", "FT1": "readout", "P1": "pump", "P2": "pump", "PIC1": "controller",
                          "SQ1": "sequence", "TST1": "indicator", "XV1": "valve"})
        idx = {d["folder"].split("/")[-1]: d for d in screen.device_index([self.desc], self.model)}
        self.assertEqual(idx["P1"], {
            "folder": f"{PILOT}/P1", "kind": "pump", "title": "P-1", "label": "Supply pump 1", "unit": "",
            "sources": ["prov:default:/tag:cadre_hmi_pilot/src/P1_OE:/alm:*"],
            "write": ["mnt/errorMask", "mnt/forceOff", "mnt/forceOn"],
            "members": ["fault", "mnt/errorMask", "mnt/forceOff", "mnt/forceOn", "state"]})
        self.assertEqual((idx["FT1"]["kind"], idx["FT1"]["write"], "sources" in idx["FT1"]), ("instrument", [], False))
        self.assertEqual(idx["P2"]["sources"], [])                               # listed empty: no alarm
        self.assertEqual((idx["PIC1"]["unit"], len(idx["PIC1"]["sources"])), ("kPa", 2))
        # the session props of a build carry it; a build without the model carries the index of before
        child, _ = screen.build_child("cadre_hmi_t", [self.desc], "T", devices=self.model)
        sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
        self.assertEqual(sp["custom"]["devices"], [idx[k] for k in sorted(idx)])
        child, _ = screen.build_child("cadre_hmi_t", [self.desc], "T")
        sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
        self.assertEqual(sp["custom"]["devices"], plain)

    def test_device_sources_and_an_alarm_on_a_source_tag(self):
        idx = screen.device_index([self.desc], self.model)
        src = "prov:default:/tag:cadre_hmi_pilot/src/P1_OE:/alm:Object error"

        class Event(AlarmListTests.Event):
            def getSource(self): return src
        ns, calls = hmi_ns(events=[Event("P1", "High", 5)])
        s = session(["Administrator"], idx)
        self.assertEqual(ns["device_sources"](s, f"{PILOT}/P1"), ["prov:default:/tag:cadre_hmi_pilot/src/P1_OE:/alm:*"])
        self.assertEqual(len(ns["device_sources"](s, f"{PILOT}/PIC1")), 2)
        self.assertEqual(ns["device_sources"](s, f"{PILOT}/P2"), [ns["NO_MATCH"]])      # listed empty
        self.assertEqual(ns["device_sources"](s, f"{PILOT}/FT1"), ["prov:default:/tag:cadre_hmi_pilot/FT1/*"])
        self.assertEqual(ns["device_sources"](session(None, screen.device_index([self.desc])), f"{PILOT}/P1"),
                         ["prov:default:/tag:cadre_hmi_pilot/P1/*"])                    # no model: the folder
        # several patterns reach queryStatus as a list, from a list or from the comma separated text
        both = ns["device_sources"](s, f"{PILOT}/PIC1")
        ns["alarm_count"]("*", both)
        ns["alarm_list"]("*", ",".join(both))
        self.assertEqual([c[1] for c in calls if c[0] == "query"], [both, both])
        # the alarm on the source tag names its device, and the row opens it
        self.assertEqual(ns["tag_id"](src), "[default]cadre_hmi_pilot/src")              # without the index
        self.assertEqual(ns["tag_id"](src, idx), f"{PILOT}/P1")
        self.assertEqual(ns["tag_id"]("prov:default:/tag:cadre_hmi_pilot/FT1/value:/alm:High", idx), f"{PILOT}/FT1")
        rec = ns["alarm_list"]("*", "", session=s)[0]
        self.assertEqual(rec["tagId"], f"{PILOT}/P1")
        ev = type("Ev", (), {"tagId": rec["tagId"]})
        self.assertTrue(ns["select_alarm_device"](s, ev))
        self.assertEqual((s.custom.selectedDevice, s.custom.selectedKind, s.custom.selectedTitle),
                         (f"{PILOT}/P1", "pump", "P-1"))
        from hmi import framework
        self.assertIn("','.join(cadre.hmi.device_sources(self.session, value))",
                      framework.DEVICE_SOURCE_CFG["binding"]["transforms"][0]["code"])

    def test_trend_index_from_the_model(self):
        idx = screen.trend_index([self.desc], None, self.model)
        self.assertEqual([(t["deviceId"].split("/")[-1], t["member"], t["unit"]) for t in idx],
                         [("FT1", "value", "L/s"), ("PIC1", "value", "kPa"), ("PIC1", "sp", "kPa"), ("PIC1", "out", "%"),
                          ("SQ1", "step", "")])
        self.assertEqual(idx[3]["label"], "Header pressure control (output)")
        self.assertEqual(idx[4]["label"], "Self cleaning filter")                # the sequence's own member
        # without the model's lists the tag model says what is historised, as before
        lean = copy.deepcopy(self.model)
        for d in lean["devices"]:
            d.pop("trend", None)
        self.assertEqual(len(screen.trend_index([self.desc], self.tags, lean)), 5)
        self.assertEqual(screen.trend_index([self.desc], None, lean), [])
        ns, _ = hmi_ns({f"{PILOT}/PIC1/sp": 50.0})
        s = session(None, [], idx)
        self.assertEqual(ns["trended"](s, f"{PILOT}/PIC1", ["value", "sp", "out"]), {"value": True, "sp": True, "out": True})
        self.assertEqual(ns["trended"](s, f"{PILOT}/P1", ["value"]), {"value": False})
        self.assertEqual(ns["trend_tags"](s, f"{PILOT}/PIC1", "sp"), [{"path": f"{PILOT}/PIC1/sp", "alias": "sp"}])
        self.assertEqual(ns["trend_tags"](s, f"{PILOT}/P1", "sp"), [{"path": "", "alias": "sp"}])

    def test_generated_tags_follow_the_model(self):
        desc = dict(self.desc, tagModel="generated")
        doc = screen.tags_document([desc], self.model)
        leaves = FaceplateContractTests().leaves(doc)
        self.assertEqual(sorted(k for k in leaves if k.startswith("P1/")),      # no cmd, mode, speed or speedSp
                         ["P1/fault", "P1/forceBadge", "P1/mnt/errorMask", "P1/mnt/forceOff", "P1/mnt/forceOn", "P1/state"])
        self.assertEqual(sorted(k for k in leaves if k.startswith("PIC1/")),
                         ["PIC1/" + m for m in sorted(["value", "sp", "out", "manual", "manOut", "gain", "ti", "td"])])
        # without the model a device gets the members of its kind
        leaves = FaceplateContractTests().leaves(screen.tags_document([desc]))
        self.assertIn("P1/speedSp", leaves)
        self.assertEqual(sorted(k for k in leaves if k.startswith("DI1/")), ["DI1/forceBadge", "DI1/state"])

    def g7(self, model=None, desc=None, tags="fixture"):
        from hmi import gates, library_profile
        profile = library_profile.build(screen.load_contracts())
        return gates.g7_devices(model or self.model, profile, screen.device_symbols([desc or self.desc]),
                                self.tags if tags == "fixture" else tags)

    def test_g7_devices_passes_the_fixture(self):
        res = self.g7()
        self.assertTrue(res["ok"], res["problems"])
        self.assertEqual((res["devices"], res["symbols"], res["members_in_tag_model"]), (8, 9, 30))   # TST1: F059, F049
        self.assertTrue(self.g7(tags=None)["ok"])                                # without a tag model

    def test_g7_devices_catches_each_break(self):
        def broken(change, text, tags="fixture"):
            model, desc, tag_model = copy.deepcopy(self.model), copy.deepcopy(self.desc), copy.deepcopy(self.tags)
            devices = {d["id"]: d for d in model["devices"]}
            symbols = {s["id"]: s for s in desc["symbols"]}
            folders = {f["name"]: f for f in tag_model["tags"]}
            change(devices, symbols, folders, model)
            probs = self.g7(model, desc, tag_model if tags == "fixture" else None)["problems"]
            self.assertTrue(any(text in p for p in probs), (text, probs))
            return probs
        # the model against the library profile
        broken(lambda d, s, f, m: m["devices"].append(copy.deepcopy(d["P2"])), "P2: listed twice")
        broken(lambda d, s, f, m: d["P1"].update(kind="compressor"), "kind 'compressor' has no faceplate")
        broken(lambda d, s, f, m: d["P1"]["members"].update(runHours={"type": "Float8", "access": "read"}),
               "member 'runHours' is not a member the library knows for kind 'pump'")
        broken(lambda d, s, f, m: d["FT1"]["members"].update({"mnt/forceOn": {"type": "Boolean", "access": "read"}}),
               "member 'mnt/forceOn' is not a member the library knows for kind 'instrument'")
        broken(lambda d, s, f, m: d["P1"]["members"]["state"].update(type="Float8"), "the library reads it as Boolean")
        broken(lambda d, s, f, m: d["P1"]["members"]["state"].update(access="write"),
               "member 'state' is marked writable and no write path writes it")
        broken(lambda d, s, f, m: d["FT1"].update(trend=["level"]), "trend names 'level'")
        # the descriptors against the model
        broken(lambda d, s, f, m: m["devices"].remove(d["XV1"]), "XV1: device '[default]cadre_hmi_pilot/XV1' is not in")
        broken(lambda d, s, f, m: s["PIC1_PV"]["params"].pop("deviceKind"),
               "PIC1_PV: opens Faceplate/Instrument (kind 'instrument-field'); the device's kind 'controller' opens "
               "Faceplate/Controller: name it in params.deviceKind")
        broken(lambda d, s, f, m: d["P1"]["members"].pop("state"), "'on' is bound to 'P1/state'; the model lists no member")
        broken(lambda d, s, f, m: d["PIC1"]["members"].pop("sp"), "PIC1_PV: 'setpoint' is bound to 'PIC1/sp'")
        # the model against the tag model
        broken(lambda d, s, f, m: f["P1"]["tags"].pop(0), "P1: the tag model lacks member 'state'")
        probs = broken(lambda d, s, f, m: d["FT1"]["members"]["value"].update(type="Float4"),
                       "member 'value' is Float8 in the tag model, Float4 in the device model")
        self.assertEqual(len(probs), 1)                                          # a Float4 suits the library
        broken(lambda d, s, f, m: f["P2"]["tags"].append({"name": "mode", "tagType": "AtomicTag", "dataType": "Int4"}),
               "P2: the tag folder carries 'mode', which the device model does not list")

        def no_folder(d, s, f, m):
            m["tagRoot"] = "[default]cadre_hmi_elsewhere"
        self.assertTrue(any("is not in the device model" in p for p in broken(no_folder, "the tag model has no folder")))

    def test_the_fixture_builds_and_passes_every_offline_gate(self):
        from hmi import gates, library_profile, parent as par
        self.assertEqual(screen.devices_schema_errors(self.model, "m") + screen.schema_errors([self.desc], ["d"]), [])
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            for render in ("stock", "module"):
                child, reports = screen.build_child("cadre_hmi_pilot", [self.desc], "Pilot", "*cadre_hmi_pilot*",
                                                    render, tag_model=self.tags, devices=self.model)
                out = child.write(Path(d))
                rep = Path(d) / "report.json"
                rep.write_text(json.dumps(reports, default=list), encoding="utf-8")
                self.assertEqual(reports["/supply"]["errors"] + reports["/supply"]["gaps"], [])
                res = gates.run(out, base, rep, tag_model=self.tags, devices=self.model,
                                symbols=screen.device_symbols([self.desc]),
                                profile=library_profile.build(screen.load_contracts()))
                self.assertTrue(res["ok"], {k: v for k, v in res.items() if isinstance(v, dict) and not v.get("ok")})
                self.assertEqual(sorted(k for k in res if k.startswith("G")),
                                 ["G1_registry", "G1_registry_parent", "G2_references", "G3_view_keys", "G4_project",
                                  "G5_layout", "G6_flow", "G7_commands", "G7_contract", "G7_devices", "G7_faceplates",
                                  "G7_history", "G7_interlocks", "G7_tag_libraries"])
                self.assertEqual(res["G7_devices"]["devices"], 8)
                # a kind without a module component is drawn with its stock view under either rendering
                nodes = view_nodes(json.loads(child.files["com.inductiveautomation.perspective/views/Screens/PilotSupply/view.json"]))
                self.assertEqual((nodes["PIC1"]["props"]["path"], nodes["DI1"]["props"]["path"], nodes["SQ1"]["props"]["path"]),
                                 ("Instrument/Controller", "Automation/Indicator", "Instrument/Sequence"))
                # the fixture's pump has no speed: the module's pump takes `hasSpeed` (0.3.0), so it draws it too
                self.assertEqual(nodes["P1"]["type"], "cadre.ob.pump" if render == "module" else "ia.display.view")
                if render == "module":
                    self.assertIs(nodes["P1"]["props"]["hasSpeed"], False)
            pc = json.loads(child.files["com.inductiveautomation.perspective/page-config/config.json"])
            self.assertIn("/trends", pc["pages"])


class MaintenanceTests(unittest.TestCase):
    """The maintenance functions (wiki page 13 section 9) and the write paths W12 to W17: each checked
    function refuses first, and gate G7 forces the advisory binding on every control that calls one."""

    D = "[default]t/P1"

    def tags(self, *members):
        return {f"{self.D}/{m}": False for m in members}

    def test_force_refuses_and_writes(self):
        entry = {"folder": self.D, "write": ["mnt/forceOn", "mnt/forceOff"]}
        admin, anon = session(["Administrator"], [entry]), session(None, [entry])
        ns, calls = hmi_ns(self.tags("mnt/forceOn", "mnt/forceOff"))
        writes = lambda: [c[1:] for c in calls if c[0] == "write"]
        self.assertEqual(ns["force"](anon, self.D, "on"), ns["REFUSED"])                 # without the role
        self.assertEqual(ns["force"](session(["Operator"], [entry]), self.D, "on"), ns["REFUSED"])
        self.assertTrue(ns["force"](admin, "[default]t/P9", "on").startswith("Refused: not a device"))
        self.assertTrue(ns["force"](admin, self.D, "toggle").startswith("Refused"))
        self.assertEqual(writes(), [])
        on, off = f"{self.D}/mnt/forceOn", f"{self.D}/mnt/forceOff"
        self.assertEqual(ns["force"](admin, self.D, "on"), "")
        self.assertEqual(ns["force"](admin, self.D, "off"), "")
        self.assertEqual(ns["force"](admin, self.D, "auto"), "")
        # each member is a write of its own, the flag that clears before the flag that sets
        self.assertEqual(writes(), [([off], [False]), ([on], [True]), ([on], [False]), ([off], [True]),
                                    ([on], [False]), ([off], [False])])
        # a member the device model marks read only: nothing is written, neither flag, whatever the action
        ro = session(["Administrator"], [{"folder": self.D, "write": ["mnt/forceOn"]}])
        for action in ("on", "off", "auto"):
            self.assertEqual(ns["force"](ro, self.D, action), "Refused: mnt/forceOff is read only on this device")
        self.assertEqual(len(writes()), 6)
        # a device without the members
        ns, calls = hmi_ns(self.tags("state", "mnt/forceOn"))
        self.assertEqual(ns["force"](admin, self.D, "on"), "Refused: this device has no force")
        self.assertEqual(calls, [])

    def test_force_by_mode_and_value(self):
        ns, calls = hmi_ns(self.tags("mnt/forceMode", "mnt/forceValue", "mnt/forceOn", "mnt/forceOff"))
        admin = session(["Administrator"], [{"folder": self.D}])                  # no model: the path's rule alone
        mode, value = f"{self.D}/mnt/forceMode", f"{self.D}/mnt/forceValue"
        for action in ("on", "off", "auto"):
            self.assertEqual(ns["force"](admin, self.D, action), "")
        # the newer interface wins; automatic clears the mode and leaves the value
        self.assertEqual([c[1:] for c in calls if c[0] == "write"],
                         [([value], [True]), ([mode], [True]), ([value], [False]), ([mode], [True]), ([mode], [False])])
        # the value read only and the mode writable: the function is not the project's to write, so
        # automatic is refused as on and off are, and `writable.force` says the same
        ns, calls = hmi_ns(self.tags("mnt/forceMode", "mnt/forceValue"))
        half = session(["Administrator"], [{"folder": self.D, "write": ["mnt/forceMode"]}])
        for action in ("on", "off", "auto"):
            self.assertEqual(ns["force"](half, self.D, action), "Refused: mnt/forceValue is read only on this device")
        self.assertEqual([c for c in calls if c[0] == "write"], [])
        self.assertFalse(ns["device_read"](half, self.D, ["mnt/forceMode", "mnt/forceValue"])["writable"]["force"])
        # a device that carries both encodings under a model that lists the pair only: the mode and the
        # value win in the faceplate and in the function, the model does not let them be written, and
        # nothing is written (gate G7 devices refuses such a tag folder before it is built)
        ns, calls = hmi_ns(self.tags("mnt/forceMode", "mnt/forceValue", "mnt/forceOn", "mnt/forceOff"))
        pair = session(["Administrator"], [{"folder": self.D, "write": ["mnt/forceOn", "mnt/forceOff"]}])
        self.assertEqual(ns["force"](pair, self.D, "on"), "Refused: mnt/forceMode is read only on this device")
        self.assertEqual([c for c in calls if c[0] == "write"], [])

    def test_error_mask_refuses_and_writes(self):
        entry = {"folder": self.D, "write": ["mnt/errorMask"]}
        admin = session(["Administrator"], [entry])
        ns, calls = hmi_ns(self.tags("mnt/errorMask"))
        self.assertEqual(ns["error_mask"](session(None, [entry]), self.D, True), ns["REFUSED"])
        self.assertEqual(ns["error_mask"](session(["Operator"], [entry]), self.D, True), ns["REFUSED"])
        self.assertTrue(ns["error_mask"](admin, "[default]t/P9", True).startswith("Refused: not a device"))
        ro = session(["Administrator"], [{"folder": self.D, "write": []}])
        self.assertEqual(ns["error_mask"](ro, self.D, True), "Refused: mnt/errorMask is read only on this device")
        self.assertEqual(calls, [])
        self.assertEqual(ns["error_mask"](admin, self.D, 1), "")
        self.assertEqual(ns["error_mask"](admin, self.D, False), "")
        mask = f"{self.D}/mnt/errorMask"
        self.assertEqual(calls, [("write", [mask], [True]), ("write", [mask], [False])])
        ns, calls = hmi_ns(self.tags("state"))
        self.assertEqual(ns["error_mask"](admin, self.D, True), "Refused: this device has no object error mask")

    def test_command_refuses_a_read_only_member_and_writes_the_controller(self):
        d = "[default]t/PIC1"
        entry = {"folder": d, "write": ["sp", "manual", "manOut", "gain", "ti", "td"]}
        admin, anon = session(["Administrator"], [entry]), session(None, [entry])
        ns, calls = hmi_ns({f"{d}/manual": False})
        writes = lambda: [c for c in calls if c[0] == "write"]
        for path, member, value in (("W12", "sp", 55.0), ("W13", "manual", True), ("W14", "manOut", 30.0),
                                    ("W15", "gain", 2.0), ("W15", "ti", 15000), ("W15", "td", 0)):
            self.assertEqual(ns["command"](anon, path, d, member, value), ns["REFUSED"])
            self.assertEqual(ns["command"](admin, path, d, member, value), "")
            self.assertEqual(calls[-1], ("write", [f"{d}/{member}"], [value]))
        self.assertEqual(len(writes()), 6)
        # the same paths on a device without a write list, in a project built without a device model:
        # the rule of the write path alone, as W1 to W5 have it
        plain = session(["Administrator"], [{"folder": d}])
        self.assertEqual(ns["command"](plain, "W12", d, "sp", 60.0), "")
        self.assertEqual(ns["command"](plain, "W15", d, "td", 5), "")
        self.assertEqual(len(writes()), 8)
        del calls[-2:]
        self.assertTrue(ns["command"](admin, "W12", d, "out", 5).startswith("Refused: W12 does not write out"))
        self.assertTrue(ns["command"](admin, "W15", d, "sp", 5).startswith("Refused"))        # not the path's member
        self.assertTrue(ns["command"](admin, "W16", d, "mnt/forceOn", True).startswith("Refused"))   # never by command
        # a member the device model marks read only: a fault that is a status of the source cannot be reset
        pump = session(["Administrator"], [{"folder": self.D, "write": ["cmd"]}])
        self.assertEqual(ns["command"](pump, "W5", self.D, "fault", False), "Refused: fault is read only on this device")
        self.assertEqual(ns["command"](pump, "W1", self.D, "cmd", False), "")
        tuned = session(["Administrator"], [{"folder": d, "write": ["sp"]}])
        self.assertEqual(ns["command"](tuned, "W15", d, "gain", 9.0), "Refused: gain is read only on this device")
        self.assertEqual(len(writes()), 7)
        # the interlock writes honour the model too
        ns, calls = hmi_ns({f"{self.D}/ilk/C01/bypassable": True, f"{self.D}/ilk/resetAt": 0})
        self.assertTrue(ns["bypass"](pump, self.D, "C01", True).startswith("Refused: the bypass is read only"))
        self.assertTrue(ns["reset_interlocks"](pump, self.D).startswith("Refused: the reset is read only"))
        self.assertEqual([c for c in calls if c[0] == "write"], [])

    def test_permissions_cover_the_new_paths(self):
        from hmi import framework, scripts
        ns, _ = hmi_ns({})
        self.assertEqual(sorted(framework.CAN_DEFAULT), sorted(ns["WRITE_PATHS"]))
        self.assertTrue(all(ns["permissions"](session(["Administrator"]))[w] for w in ("W12", "W13", "W14", "W15", "W16", "W17")))
        self.assertFalse(any(ns["permissions"](session(None)).values()))
        self.assertEqual(scripts.constant("PATH_MEMBERS")["W15"], ["gain", "ti", "td"])
        self.assertEqual(scripts.constant("FUNCTION_MEMBERS"),
                         {"W16": ["mnt/forceOn", "mnt/forceOff", "mnt/forceMode", "mnt/forceValue"], "W17": ["mnt/errorMask"],
                          "W18": ["trigger", "cmdStart", "cmdStop", "cmdReset", "cmdServiceDone", "cmdInService",
                                  "cmdOutOfService", "cmdEnable", "cmdDisable"],   # COB-158
                          "W6": ["alarmAck"], "W8": ["alarmAck"], "W9": ["alarmAck"]})   # F049
        self.assertEqual({ns["_path_of"](m) for m in ("sp", "manual", "manOut", "td", "mnt/forceValue", "mnt/errorMask", "state")},
                         {"W12", "W13", "W14", "W15", "W16", "W17", None})

    def test_maintenance_tab(self):
        from hmi import framework
        for fp in (framework.faceplate("pump"), framework.faceplate("valve"), framework.faceplate_input()):
            nodes = view_nodes(fp)
            self.assertEqual(display(nodes["Tab_maintenance"]), "{view.custom.dev.mnt} || {view.custom.dev.config} > 0")
            self.assertEqual(display(nodes["Pane_maintenance"]), "{view.custom.tab} = 'maintenance'")
            self.assertEqual([nodes[n]["props"]["text"] for n in ("ForceOn", "ForceOff", "ForceAuto", "MaskOn", "MaskAuto")],
                             ["Force on", "Force off", "Automatic", "Mask", "Automatic"])
            script = nodes["ForceOff"]["events"]["component"]["onActionPerformed"]["config"]["script"]
            self.assertIn("'path': 'W16', 'member': 'force', 'value': 'off'", script)   # F029: asked, then confirmed
            self.assertEqual(nodes["ForceOff"]["propConfig"]["props.enabled"]["binding"]["config"]["expression"],
                             "{view.custom.can.W16} && {view.custom.dev.write.force} && {view.custom.dev.allowed.W16}")
            self.assertIn("'path': 'W17', 'member': 'mnt/errorMask', 'value': True",
                          nodes["MaskOn"]["events"]["component"]["onActionPerformed"]["config"]["script"])
            self.assertIn("{view.custom.can.W17}", json.dumps(nodes["MaskAuto"]["propConfig"]["props.enabled"]))
            self.assertIn("'Forced on'", json.dumps(nodes["ForceRow"]))
        self.assertNotIn("Tab_maintenance", view_nodes(framework.faceplate_tank()))
        # which rows a device shows: a status only pump with the pair and the mask; an input with the pair only
        d = "[default]t/P1"
        ns, _ = hmi_ns({f"{d}/{m}": False for m in ("state", "mnt/forceOn", "mnt/forceOff", "mnt/errorMask")})
        s = session(["Administrator"], [{"folder": d}])
        dev = ns["device_read"](s, d, framework.FACEPLATE_READS["pump"])
        nodes = view_nodes(framework.faceplate("pump"))
        rows = ["ForceTitle", "ForceRow", "ForceCommands", "MaskTitle", "MaskRow", "MaskCommands", "FlagTitle",
                "Flag0Row", "Flag1Row", "Flag2Row"]

        def visible(dev):   # the force rows read `dev.force`, a word
            out = []
            for n in rows:
                e = display(nodes[n]).replace("len({view.custom.dev.force}) > 0", repr(bool(dev["force"])))
                out.append(n) if shown(e, dev) else None
            return out
        self.assertTrue(dev["mnt"])
        self.assertEqual(visible(dev), rows[:6])
        ns, _ = hmi_ns({f"{d}/{m}": False for m in ("state", "mnt/forceOn", "mnt/forceOff", "mnt/simulated")})
        self.assertEqual(visible(ns["device_read"](s, d, framework.FACEPLATE_READS["pump"])),
                         ["ForceTitle", "ForceRow", "ForceCommands", "FlagTitle", "Flag0Row"])
        ns, _ = hmi_ns({f"{d}/state": False})
        dev = ns["device_read"](s, d, framework.FACEPLATE_READS["pump"])
        self.assertEqual((dev["mnt"], visible(dev)), (False, []))

    def test_g7_forces_the_binding_on_the_new_controls(self):
        from hmi import gates, parent as par
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            self.assertTrue(gates.g7_commands(base, None)["ok"])
            views = base / "com.inductiveautomation.perspective/views"
            for view, old, new, text in (
                    ("Faceplate/Input", "'W16', {view.custom.can.W16}", "'W16', true", "enabled does not follow the permissions"),
                    ("Faceplate/Valve", "{view.custom.can.W17}", "true", "enabled does not follow the permissions"),
                    ("Faceplate/Controller", "{view.custom.can.W13}", "true", "enabled does not follow the permissions"),
                    # one branch of the row's case set to true: the row no longer follows that path
                    ("Faceplate/SetpointRow", "{view.custom.can.W12}", "true", "enabled does not follow the permissions"),
                    ("Faceplate/SetpointRow", "{view.custom.can.W19}, false)", "{view.custom.can.W19}, true)",
                     "enabled does not follow the permissions"),
                    ("Faceplate/LimitRow", "{view.custom.can.W4}", "{view.custom.can.W3}",
                     "enabled does not follow the permissions"),
                    ("Faceplate/InterlockRow", "{view.custom.can.W10} && ", "{view.custom.can.W10} || ",
                     "enabled does not follow the permissions"),
                    ("Faceplate/SetpointRow", "cadre.hmi.command(self.session, p.path, p.deviceId, p.member, self.view.custom.typed)",
                     "system.tag.writeBlocking([p.deviceId + '/' + p.member], [self.view.custom.typed])", "a direct system.tag.write"),
                    ("Faceplate/Controller", "cadre.hmi.command(self.session, p.path, self.view.params.deviceId, p.member, p.value)",
                     "system.tag.writeBlocking([self.view.params.deviceId + '/manual'], [True])", "a direct system.tag.write")):
                vf = views / view / "view.json"
                good = vf.read_text(encoding="utf-8")
                self.assertIn(json.dumps(old)[1:-1], good, (view, old))
                vf.write_text(good.replace(json.dumps(old)[1:-1], json.dumps(new)[1:-1]), encoding="utf-8")
                probs = gates.g7_commands(base, None)["problems"]
                self.assertEqual(bool(probs), text is not None, (view, old, probs))
                if text:
                    self.assertTrue(all(view in p and text in p for p in probs), probs)
                vf.write_text(good, encoding="utf-8")
            # a bidirectional tag binding on the setpoint field writes without a check
            vf = views / "Faceplate/SetpointRow/view.json"
            doc = json.loads(vf.read_text(encoding="utf-8"))
            view_nodes(doc)["Setpoint"]["propConfig"]["props.value"]["binding"]["config"]["bidirectional"] = True
            vf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertTrue(any("bidirectional tag binding" in p for p in gates.g7_commands(base, None)["problems"]))
            # the faceplate gate examines the new faceplates: a Tuning pane taken away fails it
            cf = views / "Faceplate/Controller/view.json"
            doc = json.loads(cf.read_text(encoding="utf-8"))
            doc["root"]["children"] = [c for c in doc["root"]["children"] if c["meta"]["name"] != "Pane_tuning"]
            cf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertIn("Faceplate/Controller: tab 'tuning' has no pane", gates.g7_faceplates(base, None)["problems"])


class NewKindTests(unittest.TestCase):
    """The controller and the digital input: their library views and contracts, the flow roles, the
    bind rule by the device's kind, and the controller faceplate."""

    def test_contracts(self):
        from hmi import parent as par
        contracts = screen.library_contracts()      # the file; `load_contracts` adds the module-only kinds (B0)
        self.assertEqual(par.build_parent()[1], contracts)                       # the generated file is current
        c = contracts["Instrument/Controller"]
        self.assertEqual((c["kind"], c["anchor"], c["flow"]), ("controller", "box", "pass"))
        self.assertEqual(sorted(c["params"]), sorted([
            "value", "setpoint", "output", "manual", "hasSetpoint", "hasOutput", "unit", "format", "label", "tag",
            "hasTag", "deviceId", "deviceKind", "deviceLabel"]))
        self.assertEqual(c["params"]["deviceKind"], "controller")
        # a loop without a setpoint or an output draws neither unless the descriptor says so
        self.assertEqual((c["params"]["hasSetpoint"], c["params"]["hasOutput"]), (False, False))
        self.assertIs(contracts["Instrument/Field"]["params"]["hasSetpoint"], False)
        i = contracts["Automation/Indicator"]
        self.assertEqual((i["kind"], i["state"], i["statusMode"], i["gate"], i["flow"], i["anchor"]),
                         ("indicator", "on", "onoff", None, "pass", "symbol-centre"))
        self.assertIn("badgeControl", i["params"])                               # a forced input shows on its symbol
        self.assertEqual(contracts["Automation/Filter"]["gate"], "on")           # the kinds of before are as they were
        for v in ("Automation/Readout", "Instrument/Field"):
            self.assertEqual(contracts[v]["params"]["deviceKind"], "instrument")
        self.assertEqual((screen.KIND_VIEW["controller"], screen.KIND_VIEW["indicator"]),
                         ("Instrument/Controller", "Automation/Indicator"))
        self.assertEqual((diagram.node_role("controller"), diagram.node_role("indicator")), ("pass", "pass"))
        self.assertEqual(sorted(screen.FACEPLATE_MEMBERS["controller"]),
                         sorted(["value", "sp", "out", "manual", "manOut", "gain", "ti", "td"]))
        self.assertEqual(screen.FACEPLATE_MEMBERS["indicator"], {"state": ("Boolean", False)})
        self.assertEqual(screen.TREND_KINDS["controller"], "value")

    def test_library_views(self):
        from hmi import library
        doc, _ = library.instrument_controller()
        nodes = view_nodes(doc)
        self.assertEqual(display(nodes["Badge_manual"]), "{view.params.manual}")
        self.assertEqual(display(nodes["Badge_auto"]), "!{view.params.manual}")
        self.assertEqual(display(nodes["Setpoint"]), "{view.params.hasSetpoint}")
        self.assertEqual(display(nodes["Output"]), "{view.params.hasOutput}")
        self.assertIn("self.view.params.deviceKind or 'controller'", doc["root"]["events"]["dom"]["onClick"]["config"]["script"])
        lamp, _ = library.automation_symbol("Indicator")
        text = json.dumps(lamp)
        self.assertIn("automation-device-primary-inverted-color", text)          # the unlit lamp, drawn here
        self.assertEqual(lamp["params"]["deviceKind"], "indicator")
        self.assertFalse((ROOT / "library/icons/lamp-on.json").exists())         # no new download

    def test_the_bind_rule_follows_the_device_kind(self):
        contracts = screen.load_contracts()

        def errors(sym):
            rep = screen.Report()
            screen.embed_symbol(dict({"x": 0, "y": 0, "w": 96, "h": 64}, **sym), contracts, "[default]t", rep, toolbar=False)
            return rep.errors
        good = {"id": "PIC1", "kind": "controller", "device": True,
                "bind": {"value": "PIC1/value", "setpoint": "PIC1/sp", "output": "PIC1/out", "manual": "PIC1/manual"}}
        self.assertEqual(errors(good), [])
        bad = dict(good, bind={"value": "PIC1/value", "setpoint": "PIC1/setpoint", "output": "PIC9/out"})
        self.assertEqual(len([e for e in errors(bad) if "faceplate contract" in e]), 2)
        # a field of an instrument binds its setpoint where it likes; a field that opens a controller does not
        field = {"id": "F1", "kind": "instrument-field", "device": "PIC1",
                 "bind": {"value": "PIC1/value", "setpoint": "PIC1/target"}}
        self.assertEqual(errors(field), [])
        opens = dict(field, params={"deviceKind": "controller"})
        self.assertTrue(any("'PIC1/sp' (faceplate contract)" in e for e in errors(opens)))
        self.assertEqual(errors(dict(opens, bind={"value": "PIC1/value", "setpoint": "PIC1/sp"})), [])
        idx = screen.device_index([{"tagRoot": "[default]t", "symbols": [dict(opens, x=0, y=0)]}])
        self.assertEqual(idx[0]["kind"], "controller")                           # the kind the alarm menu opens
        from hmi import framework
        self.assertIn("'controller', 'Faceplate/Controller', 'indicator', 'Faceplate/Input'", framework.FACEPLATE_OF_KIND)

    def test_controller_faceplate(self):
        from hmi import framework
        fp = framework.faceplate_controller()
        nodes = view_nodes(fp)
        self.assertEqual([c["meta"]["name"] for c in nodes["Tabs"]["children"]],
                         ["Tab_control", "Tab_trend", "Tab_tuning", "Tab_alarms"])
        self.assertEqual(display(nodes["Tab_tuning"]), "{view.custom.dev.has.gain} || {view.custom.dev.has.ti} || "
                         "{view.custom.dev.has.td}")
        self.assertEqual(display(nodes["Tab_trend"]),
                         "{view.custom.trend.value} || {view.custom.trend.sp} || {view.custom.trend.out}")
        # W12 to W15, each through the checked command
        rows = {n: nodes[n]["propConfig"]["props.instances"]["binding"]["transforms"][0]["code"]
                for n in ("Sp", "ManOut", "Gain", "Ti", "Td")}
        for n, (member, path) in {"Sp": ("sp", "W12"), "ManOut": ("manOut", "W14"), "Gain": ("gain", "W15"),
                                  "Ti": ("ti", "W15"), "Td": ("td", "W15")}.items():
            self.assertIn(f"'member': '{member}'", rows[n])
            self.assertIn(f"'path': '{path}'", rows[n])
        self.assertIn("Integral time (ms)", rows["Ti"])
        self.assertIn("Derivative time (ms)", rows["Td"])
        # the manual output is enabled only in manual
        self.assertIn("{view.custom.dev.writable.manOut} && {view.custom.dev.value.manual}",
                      nodes["ManOut"]["propConfig"]["props.instances"]["binding"]["config"]["expression"])
        self.assertIn("'path': 'W13', 'member': 'manual', 'value': True",   # F029: asked, then confirmed
                      nodes["Manual"]["events"]["component"]["onActionPerformed"]["config"]["script"])
        self.assertIn("'value': False", nodes["Auto"]["events"]["component"]["onActionPerformed"]["config"]["script"])
        self.assertEqual(nodes["Manual"]["propConfig"]["props.enabled"]["binding"]["config"]["expression"],
                         "{view.custom.can.W13} && {view.custom.dev.write.manual}")
        self.assertEqual((nodes["OutputBar"]["type"], nodes["OutputBar"]["props"]["max"]), ("ia.display.progress", 100))
        # the trend: the value, the limits and the setpoint on the value axis, the output on its own, 0 to 100
        chart = nodes["Chart"]
        self.assertEqual([s["name"] for s in chart["props"]["series"]], ["value", "limits", "sp", "out"])
        plot = chart["props"]["plots"][0]
        self.assertEqual([(t["series"], t["axis"]) for t in plot["trends"]],
                         [("value", "value"), ("limits", "value"), ("sp", "value"), ("out", "out")])
        self.assertEqual([(a["name"], a["alignment"], a.get("min"), a.get("max")) for a in plot["axes"]],
                         [("value", "left", None, None), ("out", "right", 0, 100)])
        for i, prop in ((0, "historyTags"), (2, "historySp"), (3, "historyOut")):
            b = chart["propConfig"][f"props.series[{i}].data"]["binding"]
            self.assertEqual((b["type"], b["config"]["tags"]), ("tag-history", "{view.custom.%s}" % prop))
            self.assertEqual(fp["custom"][prop][0]["path"], "")                  # a list default: gate G7 history
        self.assertEqual(chart["propConfig"]["props.plots[0].trends[3].visible"]["binding"]["config"]["expression"],
                         "{view.custom.trend.out}")
        # the instrument's chart is the chart of before
        plain = view_nodes(framework.faceplate_instrument())["Chart"]["props"]
        self.assertEqual(([s["name"] for s in plain["series"]], len(plain["plots"][0]["axes"])), (["value", "limits"], 1))
        # the input: its state in words
        status = view_nodes(framework.faceplate_input())
        self.assertIn("'On', 'Off'", json.dumps(status["StateRow"]))
        self.assertEqual([c["meta"]["name"] for c in status["Tabs"]["children"]],
                         ["Tab_status", "Tab_maintenance", "Tab_alarms"])


class ProfileTests(unittest.TestCase):
    """The library profile (`library/profile.json`): what the library states to a tool that writes
    descriptors and device models, generated from the tables the code uses."""

    def test_profile(self):
        from hmi import library_profile
        prof = library_profile.build(screen.load_contracts())
        self.assertEqual(json.loads((ROOT / "library/profile.json").read_text(encoding="utf-8")), prof)   # current
        self.assertEqual((prof["schema"], prof["devices"]), ("cadre-hmi-library/1", "cadre-hmi-devices/1"))
        self.assertEqual(sorted(prof["kinds"]), sorted(screen.KIND_VIEW))
        for table in (prof["kinds"], prof["deviceKinds"]):                       # every member is optional now
            self.assertFalse([m for k in table.values() for m in k["members"].values() if m["required"]])
        pump = prof["kinds"]["pump"]
        self.assertEqual(sorted(m for m in pump["members"] if m.startswith("mnt/")),
                         ["mnt/alarmSuppress", "mnt/errorMask", "mnt/forceMode", "mnt/forceOff", "mnt/forceOn",
                          "mnt/forceValue", "mnt/manualMode", "mnt/simulated"])
        self.assertTrue(pump["maintenance"] and prof["kinds"]["indicator"]["maintenance"])
        self.assertFalse(prof["kinds"]["tank"]["maintenance"])
        ctl = prof["kinds"]["controller"]
        self.assertEqual((ctl["view"], ctl["faceplate"], ctl["flow"], ctl["gate"], ctl["trend"]),
                         ("Instrument/Controller", "Faceplate/Controller", "pass", None, "value"))
        self.assertEqual(ctl["bind"], {"manual": "manual", "output": "out", "setpoint": "sp", "value": "value"})
        self.assertEqual(sorted(ctl["members"]), sorted(["value", "sp", "out", "manual", "manOut", "gain", "ti", "td",
                                                          "hiHiLimit", "hiLimit", "loLimit", "loLoLimit",
                                                          "hiHiLimitDelay", "hiLimitDelay", "loLimitDelay", "loLoLimitDelay",
                                                          "alarmAck"]))
        ind = prof["kinds"]["indicator"]
        self.assertEqual((ind["view"], ind["faceplate"], ind["flow"], ind["bind"]),
                         ("Automation/Indicator", "Faceplate/Input", "pass", {"on": "state"}))
        self.assertEqual(sorted(prof["deviceKinds"]),
                         sorted(["pump", "motor", "fan", "valve", "analogvalve", "damper", "tank", "instrument", "readout",
                                 "instrument-field", "controller", "indicator", "sequence", "generator"]))
        self.assertEqual(prof["deviceKinds"]["controller"]["trend"], ["value", "out", "sp"])
        self.assertEqual(prof["deviceKinds"]["instrument"]["faceplate"], "Faceplate/Instrument")
        self.assertIn("fault", prof["deviceKinds"]["valve"]["members"])
        self.assertEqual(prof["faceplates"]["Faceplate/Controller"]["tabs"], ["control", "trend", "tuning", "alarms"])
        self.assertEqual(prof["faceplates"]["Faceplate/Input"]["tabs"], ["status", "maintenance", "alarms"])
        self.assertEqual(list(prof["writePaths"]), [f"W{i}" for i in range(1, 20)])
        got = {w: (v["members"], v["function"]) for w, v in prof["writePaths"].items()}
        self.assertEqual(got["W12"], (["sp"], "command"))
        self.assertEqual(got["W13"], (["manual"], "command"))
        self.assertEqual(got["W14"], (["manOut"], "command"))
        self.assertEqual(got["W15"], (["gain", "ti", "td"], "command"))
        self.assertEqual(got["W16"], (["mnt/forceOn", "mnt/forceOff", "mnt/forceMode", "mnt/forceValue"], "force"))
        self.assertEqual(got["W17"], (["mnt/errorMask"], "error_mask"))
        self.assertEqual((got["W1"], got["W7"]), ((["cmd"], "command"), ([], "")))
        self.assertTrue(all(v["role"] == "Administrator" and v["what"] for v in prof["writePaths"].values()))
        self.assertLessEqual({"force", "error-mask", "pid-faceplate", "pid-tuning", "alarm-list", "interlocks", "trend"},
                             set(prof["functions"]))
        self.assertEqual(prof["forceEncodings"], [["mnt/forceOn", "mnt/forceOff"], ["mnt/forceMode", "mnt/forceValue"]])


class SweepTests(unittest.TestCase):
    """The pure functions of the faceplate sweep (G11): the tab labels it opens, the line it fails on,
    and, with a device model, the tabs and the alarm rows it expects of a device. The sweep itself runs
    against the gateway."""

    def setUp(self):
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import faceplates
        self.fp = faceplates
        self.exp = faceplates.device_expectations([fixture("pilot-supply.json")], fixture("pilot-devices.json"))

    def test_tab_labels(self):
        for label, key, count in (("Maintenance", "Maintenance", None), ("Tuning", "Tuning", None),
                                  (" Status ", "Status", None), ("Alarms (2)", "Alarms", "2"), ("Control", "Control", None)):
            m = self.fp.TAB.match(label)
            self.assertEqual((m.group(1), m.group(3)), (key, count))
        self.assertIsNone(self.fp.TAB.match("Force on"))
        from hmi import framework
        labels = {label for tabs in framework.FACEPLATE_TABS.values() for _k, label in tabs}
        self.assertEqual([x for x in labels if not self.fp.TAB.match(x)], [])    # every tab the library has

    def test_expected_tabs(self):
        self.assertEqual({t: e["tabs"] for t, e in self.exp.items()}, {
            "P-1": ["Control", "Alarms", "Maintenance"], "SupplyPump_No2": ["Control", "Alarms"],
            "XV-1": ["Control", "Alarms", "Maintenance"], "SupplyFlow_FT01": ["Values", "Trend", "Alarms"],
            "PIC-1": ["Control", "Trend", "Tuning", "Alarms"], "SuctionLowLvl_SW": ["Status", "Maintenance", "Alarms"],
            "FLT-1": ["Status", "Trend", "Alarms"], "TST-1": ["Status", "Alarms"]})
        self.assertEqual(self.fp.tab_faults("P-1", ["Control", "Alarms", "Maintenance"], self.exp["P-1"]), [])
        self.assertEqual(len(self.fp.tab_faults("P-1", ["Control", "Alarms"], self.exp["P-1"])), 1)
        self.assertEqual(self.fp.tab_faults("P-502", ["Control", "Alarms", "Interlocks"], None), [])   # no model
        from hmi import framework
        self.assertEqual(framework.expected_tabs("pump", ["state", "ilk/permitted", "ilk/C01/ok"]),
                         ["Control", "Alarms", "Interlocks"])
        self.assertEqual(framework.expected_tabs("controller", ["value", "sp"]), ["Control", "Alarms"])
        self.assertEqual(framework.expected_tabs("tank", ["hiLimit"]), ["Values", "Alarms"])
        # the Maintenance tab only where it has a row: a whole force, the mask or a flag
        for members, shown in ((["state", "mnt/forceOn"], False), (["state", "mnt/forceMode"], False),
                               (["mnt/forceOn", "mnt/forceOff"], True), (["mnt/forceMode", "mnt/forceValue"], True),
                               (["mnt/errorMask"], True), (["mnt/simulated"], True)):
            self.assertEqual("Maintenance" in framework.expected_tabs("indicator", members), shown, members)
        # a controller whose model names no trend: the tag model decides, and the sweep does not judge the tab
        model = fixture("pilot-devices.json")
        next(d for d in model["devices"] if d["id"] == "PIC1").pop("trend")
        open_ = self.fp.device_expectations([fixture("pilot-supply.json")], model)["PIC-1"]
        self.assertTrue(open_["trend_open"])
        self.assertEqual(self.fp.tab_faults("PIC-1", ["Control", "Trend", "Tuning", "Alarms"], open_), [])
        self.assertEqual(len(self.fp.tab_faults("PIC-1", ["Control", "Trend", "Alarms"], open_)), 1)

    def test_alarm_rows(self):
        p1, ft1, p2 = self.exp["P-1"], self.exp["SupplyFlow_FT01"], self.exp["SupplyPump_No2"]
        self.assertEqual(p1["sources"], ["prov:default:/tag:cadre_hmi_pilot/src/P1_OE:/alm:*"])
        self.assertEqual(ft1["sources"], ["prov:default:/tag:cadre_hmi_pilot/FT1/*"])      # no list: the folder
        self.assertEqual(p2["sources"], [])
        self.assertEqual(self.fp.source_core(p1["sources"][0]), "cadre_hmi_pilot/src/P1_OE")
        self.assertEqual(self.fp.source_core(ft1["sources"][0]), "cadre_hmi_pilot/FT1/")
        row = "10/10/2026 21:42:00 Pilot/P-1 High Active, Unacknowledged prov:default:/tag:cadre_hmi_pilot/src/P1_OE:/alm:Object error"
        self.assertTrue(self.fp.row_belongs(row, "P-1", p1))
        self.assertTrue(self.fp.row_belongs("Active cadre_hmi_pilot/src/P1_OE Object error", "P-1", p1))   # the tag path alone
        self.assertFalse(self.fp.row_belongs(row.replace("P1_OE", "XV1_OE"), "P-1", p1))    # the title is in the row
        self.assertFalse(self.fp.row_belongs(row, "SupplyPump_No2", p2))                               # a device without alarms
        self.assertTrue(self.fp.row_belongs("Pilot/P-1 P-1 Object error [default]cadre_hmi_pilot/P1", "P-1", p1))   # tagId
        self.assertTrue(self.fp.row_belongs("WTP/P-502 P-502 Fault", "P-502"))               # no model: the title
        self.assertFalse(self.fp.row_belongs("WTP/P-501 P-501 Fault", "P-502"))


# ---------------------------------------------------------------------------------------
# Stage 2 review: the checked write carries every check and reads what the gateway answers;
# gate G7 names the path a control must follow; gate G7 devices bounds the force and the
# alarm sources.
# ---------------------------------------------------------------------------------------
class CheckedWriteTests(unittest.TestCase):
    """`cadre.hmi._checked_writes` is the one place a device member is written: it refuses on its own,
    and a write the gateway does not make is answered as a refusal (GF-49, GF-50)."""

    D = "[default]t/P1"

    def tags(self, **members):
        return {f"{self.D}/{m.replace('_', '/')}": v for m, v in members.items()}

    def test_the_helper_refuses_on_its_own(self):
        ns, calls = hmi_ns({})
        admin, anon = session(["Administrator"], [{"folder": self.D}]), session(None, [{"folder": self.D}])
        helper = ns["_checked_writes"]
        self.assertEqual(helper(anon, "W16", self.D, [("mnt/forceOn", True)]), ns["REFUSED"])
        self.assertEqual(helper(session(["Operator"], [{"folder": self.D}]), "W16", self.D, [("mnt/forceOn", True)]),
                         ns["REFUSED"])
        # a folder outside the session's index, and no folder at all
        self.assertEqual(helper(admin, "W16", "[default]elsewhere/X", [("mnt/forceOn", True)]),
                         "Refused: not a device of this project")
        self.assertEqual(helper(admin, "W16", "", [("mnt/forceOn", True)]), "Refused: not a device of this project")
        # a member the path does not write: any tag, another path's member, and both force flags by W1
        self.assertEqual(helper(admin, "W16", self.D, [("any/tag", 1)]), "Refused: W16 does not write any/tag")
        self.assertEqual(helper(admin, "W16", self.D, [("mnt/forceOn", True), ("cmd", True)]),
                         "Refused: W16 does not write cmd")
        self.assertEqual(helper(admin, "W1", self.D, [("mnt/forceOn", True), ("mnt/forceOff", True)]),
                         "Refused: W1 does not write mnt/forceOn")
        self.assertEqual(helper(admin, "W99", self.D, [("cmd", True)]), ns["REFUSED"])   # no such path, no role
        # a member the model marks read only refuses the whole list
        ro = session(["Administrator"], [{"folder": self.D, "write": ["mnt/forceOn"]}])
        self.assertEqual(helper(ro, "W16", self.D, [("mnt/forceOn", False), ("mnt/forceOff", True)]),
                         "Refused: mnt/forceOff is read only on this device")
        self.assertEqual(calls, [])                                              # nothing was written by any of them
        self.assertEqual(helper(admin, "W16", self.D, [("mnt/forceOn", False), ("mnt/forceOff", True)]), "")
        self.assertEqual([c[1:] for c in calls], [([f"{self.D}/mnt/forceOn"], [False]), ([f"{self.D}/mnt/forceOff"], [True])])

    def test_a_missing_write_list_fails_closed_in_a_project_with_a_device_model(self):
        tags = self.tags(fault=True)
        for entries in ([{"folder": self.D}], [{"folder": self.D, "write": None}],
                        [{"folder": self.D}, {"folder": self.D, "write": ["fault"]}]):   # the first entry counts
            ns, calls = hmi_ns(dict(tags))
            # built without a model: no list means the rule of the write path alone, as before
            self.assertEqual(ns["command"](session(["Administrator"], entries), "W5", self.D, "fault", False), "")
            self.assertEqual(ns["command"](session(["Administrator"], entries, model=False), "W5", self.D, "fault", False), "")
            self.assertEqual(len(calls), 2)
            # built with a model: the list is lost, and nothing may be written
            strict = session(["Administrator"], entries, model=True)
            self.assertEqual(ns["command"](strict, "W5", self.D, "fault", False), "Refused: fault is read only on this device")
            self.assertFalse(ns["device_read"](strict, self.D, ["fault"])["writable"]["fault"])
            self.assertEqual(len([c for c in calls if c[0] == "write"]), 2)
        ns, calls = hmi_ns(dict(tags))
        listed = session(["Administrator"], [{"folder": self.D, "write": []}], model=True)
        self.assertTrue(ns["command"](listed, "W5", self.D, "fault", False).startswith("Refused: fault is read only"))
        full = session(["Administrator"], [{"folder": self.D, "write": ["fault"]}], model=True)
        self.assertEqual(ns["command"](full, "W5", self.D, "fault", False), "")
        # the generator sets the flag with a device model, and clears it without one
        for devices, flag in ((fixture("pilot-devices.json"), True), (None, False)):
            child, _ = screen.build_child("cadre_hmi_t", [fixture("pilot-supply.json")], "T", devices=devices)
            sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
            self.assertIs(sp["custom"]["deviceModel"], flag)
        screen.RENDER["target"] = "stock"

    def test_a_write_the_gateway_refuses_is_answered(self):
        admin = session(["Administrator"], [{"folder": self.D}])
        ns, calls = hmi_ns(self.tags(cmd=False, mnt_errorMask=False), refuse=[f"{self.D}/cmd", f"{self.D}/mnt/errorMask"])
        self.assertEqual(ns["command"](admin, "W1", self.D, "cmd", True), "Refused: the gateway did not write cmd (Bad_ReadOnly)")
        self.assertEqual(ns["error_mask"](admin, self.D, True),
                         "Refused: the gateway did not write mnt/errorMask (Bad_ReadOnly)")
        ilk = {f"{self.D}/ilk/C01/bypassable": True, f"{self.D}/ilk/C01/bypassed": False, f"{self.D}/ilk/resetAt": 0}
        ns, calls = hmi_ns(ilk, refuse=[f"{self.D}/ilk/C01/bypassed", f"{self.D}/ilk/resetAt"])
        self.assertEqual(ns["bypass"](admin, self.D, "C01", True), "Refused: the gateway did not write the bypass (Bad_ReadOnly)")
        self.assertEqual(ns["reset_interlocks"](admin, self.D), "Refused: the gateway did not write the reset (Bad_ReadOnly)")
        # an answer that cannot be read counts as not written, and a pending write as written
        self.assertEqual(ns["_written"](None, ["sp"]), "Refused: the gateway did not write sp (no answer)")
        self.assertEqual(ns["_written"](["Good", 'Bad_NotFound("Path not found.")'], ["a", "b"]),
                         "Refused: the gateway did not write b (Bad_NotFound)")
        self.assertEqual(ns["_written"](["Good_WritePending"], ["sp"]), "")

    def test_a_force_whose_write_fails_is_never_the_opposite_and_never_both(self):
        admin = session(["Administrator"], [{"folder": self.D}])
        on, off = f"{self.D}/mnt/forceOn", f"{self.D}/mnt/forceOff"
        mode, value = f"{self.D}/mnt/forceMode", f"{self.D}/mnt/forceValue"

        def run(tags, refuse, action):
            ns, calls = hmi_ns(tags, refuse=[refuse])
            msg = ns["force"](admin, self.D, action)
            self.assertTrue(msg.startswith("Refused: the gateway did not write"), msg)
            return tags, ns["device_read"](admin, self.D, list(ns["MNT_FORCE_PAIR"] + ns["MNT_FORCE_MODE"]))["force"]
        # the pair, forced off, force on asked, the clearing write refused: still forced off, forceOn untouched
        tags, state = run({on: False, off: True}, off, "on")
        self.assertEqual((tags[on], tags[off], state), (False, True, "off"))
        # the pair, automatic, force on asked, the setting write refused: automatic
        tags, state = run({on: False, off: False}, on, "on")
        self.assertEqual((tags[on], tags[off], state), (False, False, "auto"))
        # the pair, forced on, force off asked, the setting write refused: automatic, not forced on and not both
        tags, state = run({on: True, off: False}, off, "off")
        self.assertEqual((tags[on], tags[off], state), (False, False, "auto"))
        # the pair, forced on, automatic asked, the first write refused: unchanged
        tags, state = run({on: True, off: False}, on, "auto")
        self.assertEqual((tags[on], tags[off], state), (True, False, "on"))
        # the mode and the value, automatic with the value false, force on asked, the value refused: the
        # mode is not written, so the device is not forced off
        tags, state = run({mode: False, value: False}, value, "on")
        self.assertEqual((tags[mode], tags[value], state), (False, False, "auto"))
        # the same with the mode refused: the value is set and the device stays automatic
        tags, state = run({mode: False, value: False}, mode, "on")
        self.assertEqual((tags[mode], tags[value], state), (False, True, "auto"))
        # across every state, action and refused member, no call ends with both flags true or forced the other way
        for a in (False, True):
            for b in (False, True):
                for action in ("on", "off", "auto"):
                    for first, second in ((on, off), (mode, value)):
                        for refused in (first, second):
                            tags = {first: a, second: b}
                            ns, _ = hmi_ns(tags, refuse=[refused])
                            before = ns["_force_state"]({"mnt_forceOn": first == on, "mnt_forceOff": first == on,
                                                         "mnt_forceMode": first == mode, "mnt_forceValue": first == mode},
                                                        {k.split("/")[-2] + "_" + k.split("/")[-1]: v for k, v in tags.items()})
                            ns["force"](admin, self.D, action)
                            after = ns["device_read"](admin, self.D, [first[len(self.D) + 1:], second[len(self.D) + 1:]])["force"]
                            if first == on and not (a and b):
                                self.assertFalse(tags[on] and tags[off], (a, b, action, refused))
                            wrong = {"on": "off", "off": "on", "auto": None}[action]
                            if before != wrong:
                                self.assertNotEqual(after, wrong, (first, a, b, action, refused, before, after))

    def test_the_value_rules_of_command(self):
        d = "[default]t/PIC1"
        admin = session(["Administrator"], [{"folder": d}, {"folder": self.D}])
        ns, calls = hmi_ns({f"{d}/manual": False})
        writes = lambda: [c[1:] for c in calls if c[0] == "write"]
        for bad in ([1, 2, 3], "text", None, True, float("nan"), float("inf"), -float("inf")):
            self.assertEqual(ns["command"](admin, "W12", d, "sp", bad), "Refused: sp takes a number", repr(bad))
        self.assertEqual(ns["command"](admin, "W4", d, "hiLimit", "9"), "Refused: hiLimit takes a number")
        for path, member, value in (("W3", "speedSp", -1), ("W3", "speedSp", 100.5), ("W14", "manOut", 101),
                                    ("W14", "manOut", -0.1), ("W15", "ti", -1), ("W15", "td", -0.001)):
            self.assertEqual(ns["command"](admin, path, self.D if member == "speedSp" else d, member, value),
                             "Refused: %s is outside its range" % member)
        # the manual output only while the loop is in manual; a loop without the member is never in manual
        self.assertEqual(ns["command"](admin, "W14", d, "manOut", 30.0), "Refused: the loop is not in manual")
        self.assertEqual(ns["command"](admin, "W14", self.D, "manOut", 30.0), "Refused: the loop is not in manual")
        self.assertEqual(writes(), [])
        self.assertEqual(ns["command"](admin, "W13", d, "manual", True), "")
        self.assertEqual(ns["command"](admin, "W14", d, "manOut", 30.0), "")
        # the bounds are met at their ends, a setpoint has none, and a whole number is a number
        for path, device, member, value in (("W3", self.D, "speedSp", 0), ("W3", self.D, "speedSp", 100),
                                             ("W12", d, "sp", -1e30), ("W15", d, "ti", 0), ("W15", d, "gain", -2.5),
                                             ("W4", d, "loLimit", 12)):
            self.assertEqual(ns["command"](admin, path, device, member, value), "", (member, value))
        self.assertEqual(len(writes()), 8)
        # the setpoint fields carry the same bounds as the rule
        from hmi import framework
        self.assertEqual(framework.SETPOINT_BOUNDS, ns["MEMBER_BOUNDS"])
        rows = view_nodes(framework.faceplate_controller())
        for name, low, high in (("ManOut", 0, 100), ("Ti", 0, None), ("Td", 0, None), ("Sp", None, None), ("Gain", None, None)):
            code = rows[name]["propConfig"]["props.instances"]["binding"]["transforms"][0]["code"]
            self.assertIn(f"'minimum': {low!r}, 'maximum': {high!r}", code, name)

    def test_device_read_looks_the_device_up_once(self):
        members = DeviceReadTests.PUMP
        ns, calls = hmi_ns({f"{self.D}/{m}": False for m in members})

        class Counted(list):
            passes = 0

            def __iter__(self):
                Counted.passes += 1
                return list.__iter__(self)
        s = session(["Administrator"], [])
        s.custom.devices = Counted([{"folder": "[default]t/X%d" % i, "write": []} for i in range(50)]
                                   + [{"folder": self.D, "write": ["cmd", "mnt/forceMode", "mnt/forceValue"]}])
        got = ns["device_read"](s, self.D, members)
        self.assertEqual(Counted.passes, 1)                                      # not once for each member
        self.assertEqual((got["write"]["cmd"], got["write"]["mode"], got["writable"]["force"]), (True, False, True))
        self.assertEqual(len([c for c in calls if c[0] == "read"]), 1)

    def test_limit_bypass_and_reset_follow_the_write_list(self):
        from hmi import framework
        tags = {f"{self.D}/value": 1.0, f"{self.D}/hiLimit": 2.0, f"{self.D}/loLimit": 0.5,
                f"{self.D}/ilk/C01/ok": True, f"{self.D}/ilk/C02/ok": True, f"{self.D}/ilk/permitted": True,
                f"{self.D}/ilk/resetAt": 0}
        ns, _ = hmi_ns(tags)
        plain = session(["Administrator"], [{"folder": self.D}])
        model = session(None, [{"folder": self.D, "write": ["hiLimit", "ilk/C02/bypassed"]}], model=True)
        other = session(["Administrator"], [])                                   # the folder is no device of the project
        flags = lambda rows: [r["writable"] for r in rows]
        self.assertEqual(flags(ns["limit_rows"](self.D, "value", plain)), [True, True])
        self.assertEqual(flags(ns["limit_rows"](self.D, "value", model)), [True, False])   # a fact of the model, not of the role
        self.assertEqual(flags(ns["limit_rows"](self.D, "value", other)), [False, False])
        self.assertEqual(flags(ns["interlock_rows"](self.D, plain)), [True, True])
        self.assertEqual(flags(ns["interlock_rows"](self.D, model)), [False, True])
        self.assertEqual(flags(ns["interlock_rows"](self.D)), [False, False])
        self.assertTrue(ns["interlock_summary"](self.D, plain)["resetWritable"])
        self.assertFalse(ns["interlock_summary"](self.D, model)["resetWritable"])
        self.assertFalse(ns["interlock_summary"](self.D)["resetWritable"])
        self.assertEqual(ns["interlock_summary"]("", plain), framework.ILK_DEFAULT)   # the view's default
        # the controls bind the flag beside the permission of their path, and the views hand it to them
        views = framework.framework_views()
        enabled = lambda path, name: view_nodes(views[path])[name]["propConfig"]["props.enabled"]["binding"]["config"]["expression"]
        self.assertEqual(enabled("Faceplate/LimitRow", "Setpoint"), "{view.custom.can.W4} && {view.params.writable}")
        self.assertEqual(enabled("Faceplate/InterlockRow", "Bypass"), "{view.custom.can.W10} && {view.params.writable}")
        self.assertEqual(enabled("Faceplate/Pump", "ResetInterlocks"), "{view.custom.can.W11} && {view.custom.ilk.resetWritable}")
        for path in ("Faceplate/LimitRow", "Faceplate/InterlockRow"):
            self.assertIs(views[path]["params"]["writable"], False)
        pump, inst = views["Faceplate/Pump"]["propConfig"], views["Faceplate/Instrument"]["propConfig"]
        self.assertIn("cadre.hmi.interlock_rows(value, self.session)", pump["custom.ilkRows"]["binding"]["transforms"][0]["code"])
        self.assertIn("cadre.hmi.interlock_summary(value, self.session)", pump["custom.ilk"]["binding"]["transforms"][0]["code"])
        code = inst["custom.limitRows"]["binding"]["transforms"][0]["code"]
        self.assertIn("cadre.hmi.limit_rows(value, 'value', self.session)", code)
        self.assertIn("dict(r, valueMember='value'", code)                       # the row's flag reaches the instance


class CommandGateTests(unittest.TestCase):
    """Gate G7 commands on single hand written views: the path a control must follow, the scripts it
    reads and the names it refuses."""

    def problems(self, node=None, **doc):
        from hmi import gates, scripts
        with tempfile.TemporaryDirectory() as d:
            vf = Path(d) / "com.inductiveautomation.perspective/views/T/V/view.json"
            vf.parent.mkdir(parents=True)
            root = {"type": "ia.container.flex", "meta": {"name": "root"}, "children": [node] if node else []}
            vf.write_text(json.dumps({"root": root, **doc}), encoding="utf-8")
            for name, code in (("hmi", scripts.HMI), ("icons", scripts.icons_module(ROOT / "library/icons"))):
                lib = Path(d) / f"ignition/script-python/cadre/{name}/code.py"   # the names resolve in it (F050)
                lib.parent.mkdir(parents=True)
                lib.write_text(code, encoding="utf-8")
            return gates.g7_commands(Path(d), None)["problems"]

    def button(self, script, enabled=None, **more):
        n = {"type": "ia.input.button", "meta": {"name": "B"},
             "events": {"component": {"onActionPerformed": {"config": {"script": script}}}}, "propConfig": {}}
        if enabled is not None:
            n["propConfig"]["props.enabled"] = {"binding": {"type": "expr", "config": {"expression": enabled}}}
        n.update(more)
        return n

    FORCE = "self.view.custom.message = cadre.hmi.force(self.session, self.view.params.deviceId, 'on')"
    ROW = "p = self.view.params\nmsg = cadre.hmi.command(self.session, p.path, p.deviceId, p.member, self.props.value)"
    CASE = "case({view.params.path}, 'W3', {view.custom.can.W3}, 'W12', {view.custom.can.W12}, false)"

    def test_enabled_names_the_path_the_control_calls(self):
        for enabled in ("{view.custom.can.W16}", "{view.custom.can.W16} && {view.custom.dev.write.force}",
                        "{view.params.x} && {view.custom.can.W16} && ({view.params.a} || {view.params.b})"):
            self.assertEqual(self.problems(self.button(self.FORCE, enabled)), [], enabled)
        for enabled in (None, "true", "{view.custom.can.W16} || true", "{view.custom.can.W6}",
                        "if(true, true, {view.custom.can.W16})", "!{view.custom.can.W16}",
                        "{view.custom.can.W17} && {view.custom.dev.write.force}",
                        "{view.custom.can.W16} && {view.params.a} || {view.params.b}"):
            probs = self.problems(self.button(self.FORCE, enabled))
            self.assertTrue(len(probs) == 1 and "does not follow the permissions (write path W16)" in probs[0], (enabled, probs))
        # a literal `enabled`, and a binding whose transform could answer anything
        self.assertTrue(self.problems(self.button(self.FORCE, None, props={"enabled": True})))
        n = self.button(self.FORCE, "{view.custom.can.W16}")
        n["propConfig"]["props.enabled"]["binding"]["transforms"] = [{"type": "script", "code": "\treturn True"}]
        self.assertTrue(self.problems(n))
        # each checked function has its path; `command` names it in its second argument
        for script, path in (("cadre.hmi.error_mask(self.session, d, True)", "W17"),
                             ("cadre.hmi.bypass(self.session, d, c, True)", "W10"),
                             ("cadre.hmi.reset_interlocks(self.session, d)", "W11"),
                             ("cadre.hmi.ack_top(scope, self.session)", "W6"),
                             ("cadre.hmi.pulse(self.session, d, 'trigger')", "W18"),
                             ("cadre.hmi.command(self.session, 'W13', d, 'manual', True)", "W13"),
                             ('cadre.hmi.command(self.session, "W5", d, "fault", False)', "W5")):
            self.assertEqual(self.problems(self.button(script, "{view.custom.can.%s}" % path)), [], script)
            self.assertTrue(self.problems(self.button(script, "{view.custom.can.W1}")), script)
        # two paths in one script need both permissions
        both = "cadre.hmi.command(self.session, 'W1', d, 'cmd', True)\ncadre.hmi.command(self.session, 'W2', d, 'mode', 0)"
        self.assertEqual(self.problems(self.button(both, "{view.custom.can.W1} && {view.custom.can.W2}")), [])
        self.assertEqual(len(self.problems(self.button(both, "{view.custom.can.W1}"))), 1)
        # a path the gate cannot tell is refused
        self.assertTrue(self.problems(self.button("cadre.hmi.command(self.session, path, d, m, v)", "{view.custom.can.W1}")))

    def test_the_row_view_follows_the_path_it_is_given(self):
        self.assertEqual(self.problems(self.button(self.ROW, self.CASE + " && {view.params.enabled}")), [])
        self.assertEqual(self.problems(self.button(self.ROW.replace("p.path", "self.view.params.path").split("\n")[1], self.CASE)), [])
        for enabled in (self.CASE.replace(", false)", ", true)"),                # the default would enable an unknown path
                        self.CASE.replace("{view.custom.can.W12}", "true"),
                        self.CASE.replace("{view.custom.can.W12}", "{view.custom.can.W3}"),
                        self.CASE.replace("{view.params.path}", "{view.params.other}"),
                        self.CASE + " || true", "{view.custom.can.W3}"):
            probs = self.problems(self.button(self.ROW, enabled))
            self.assertTrue(len(probs) == 1 and "write path {view.params.path}" in probs[0], (enabled, probs))
        # `p` that is not the view's parameters names no path
        self.assertTrue(self.problems(self.button(self.ROW.replace("p = self.view.params", "p = other"), self.CASE)))

    def test_no_private_function_and_no_direct_write_in_any_script(self):
        ok = "{view.custom.can.W16}"
        private = "cadre.hmi._checked_writes(self.session, 'W16', '[default]any/folder', [('tag', 1)])"
        self.assertTrue(any("cadre.hmi._checked_writes is not a function for a view" in p
                            for p in self.problems(self.button(private, ok))))
        for script in ("h = cadre.hmi\nh.force(self.session, d, 'on')", "getattr(cadre.hmi, '_wri' + 'tten')(None, [])"):
            self.assertTrue(any("is not a function for a view" in p for p in self.problems(self.button(script, ok))), script)
        for script, name in (("system.tag.writeBlocking([p], [1])", "system.tag.writeBlocking"),
                             ("system.tag.writeAsync([p], [1])", "system.tag.writeAsync"),
                             ("t = system.tag\nt.writeBlocking([p], [1])", "system.tag"),
                             ("getattr(system.tag, 'write' + 'Blocking')([p], [1])", "system.tag"),
                             ("system.tag.configure(base, [{'name': 'x', 'value': 1}])", "system.tag.configure"),
                             ("system.tag.deleteTags([p])", "system.tag.deleteTags"),
                             ("system.opc.writeValue('s', 'i', 1)", "system.opc.writeValue"),
                             ("system.alarm.acknowledge(ids, 'n', 'u')", "system.alarm.acknowledge"),
                             ("system.alarm.shelve(path=[p])", "system.alarm.shelve")):
            probs = self.problems(self.button(script))
            self.assertTrue(any(f"a direct {name} (use" in p for p in probs), (script, probs))
        reads = ("v = system.tag.readBlocking([p])[0].value\nif system.tag.exists(p):\n\tsystem.tag.browse(p)\n"
                 "n = len(system.alarm.queryStatus(path=[p]))\nsystem.tag.queryTagHistory(paths=[p])")
        self.assertEqual(self.problems(self.button(reads)), [])
        # the scripts a node holds besides its events: custom methods, message handlers, a change script,
        # a transform, and an expression that runs a script
        write = "system.tag.writeBlocking([self.view.params.deviceId + '/cmd'], [True])"
        for more in ({"scripts": {"customMethods": [{"name": "go", "params": [], "script": write}]}},
                     {"scripts": {"messageHandlers": [{"messageType": "go", "script": write, "pageScope": True}]}},
                     {"scripts": {"extensionFunctions": [{"name": "f", "script": write}]}},
                     {"propConfig": {"custom.x": {"onChange": {"script": write}}}},
                     {"propConfig": {"custom.x": {"binding": {"type": "expr", "config": {"expression": "1"},
                                                              "transforms": [{"type": "script", "code": write}]}}}},
                     {"propConfig": {"custom.x": {"binding": {"type": "expr", "config": {
                         "expression": "runScript('system.tag.writeBlocking', 0, {view.params.p}, 1)"}}}}},
                     {"propConfig": {"custom.x": {"binding": {"type": "property", "config": {"path": "view.params.p"},
                                                              "transforms": [{"type": "expression", "expression":
                                                                              "runScript('system.tag.writeBlocking', 0, {value}, 1)"}]}}}}):
            n = {"type": "ia.display.label", "meta": {"name": "L"}, **more}
            self.assertTrue(any("a direct system.tag.writeBlocking" in p for p in self.problems(n)), more)
        run = {"type": "ia.display.label", "meta": {"name": "L"}, "propConfig": {"props.text": {"binding": {
            "type": "expr", "config": {"expression": "runScript('cadre.hmi.force', 0, {session}, {view.params.d}, 'on')"}}}}}
        self.assertTrue(any("called from an expression" in p for p in self.problems(run)))
        # a checked write at view level has no control whose `enabled` could follow it
        level = {"custom.x": {"binding": {"type": "expr", "config": {"expression": "now(1000)"}, "transforms": [
            {"type": "script", "code": "\treturn cadre.hmi.force(self.session, self.params.deviceId, 'on')"}]}}}
        self.assertTrue(any("a checked write called at view level" in p for p in self.problems(propConfig=level)))
        # the stock table's actions follow W7 itself
        table = {"type": "ia.display.alarmstatustable", "meta": {"name": "T"}, "propConfig": {
            f"props.{a}": {"binding": {"type": "expr", "config": {"expression": "{view.custom.can.W7}"}}}
            for a in ("enableAcknowledge", "enableShelve", "enableUnshelve")}}
        self.assertEqual(self.problems(table), [])
        table["propConfig"]["props.enableShelve"]["binding"]["config"]["expression"] = "{view.custom.can.W7} || true"
        self.assertTrue(any("['enableShelve'] not bound to the permissions" in p for p in self.problems(table)))

    def test_a_checked_write_is_found_however_it_is_spelt(self):
        """A checked function counts as called wherever it is named, so a spaced bracket, a spaced
        name, an alias and a bound method each need the permission of the path. `system` and `cadre`
        are named only with their module, so an import, an alias and a lookup are refused."""
        from hmi import gates
        pulse = "cadre.hmi.pulse(self.session, self.view.params.deviceId, 'trigger')"
        self.assertEqual(self.problems(self.button(pulse, "{view.custom.can.W18}")), [])
        for script in ("cadre.hmi.pulse (self.session, d, 'trigger')",
                       "cadre . hmi . pulse(self.session, d, 'trigger')",
                       "cadre.hmi.pulse\t(self.session, d, 'trigger')",
                       "cadre.hmi.\n\tpulse(self.session, d, 'trigger')",
                       "f = cadre.hmi.pulse\nf(self.session, d, 'trigger')",
                       "f = cadre.hmi.pulse; f(self.session, d, 'trigger')",
                       "cadre.hmi.pulse.__call__(self.session, d, 'trigger')",
                       "map(cadre.hmi.pulse, [self.session], [d], ['trigger'])",
                       "# cadre.hmi.pulse\nx = 1"):                               # a mention counts: the gate fails closed
            for enabled in (None, "true", "{view.custom.can.W1}"):
                probs = self.problems(self.button(script, enabled))
                self.assertTrue(len(probs) == 1 and "does not follow the permissions (write path W18)" in probs[0],
                                (script, enabled, probs))
            self.assertEqual(self.problems(self.button(script, "{view.custom.can.W18} && {view.custom.dev.write.trigger}")),
                             [], script)
        # another name is no checked write; one the library lacks is refused as such (F050), and only so
        self.assertEqual(self.problems(self.button("cadre.hmi.pulse_width(d)")),
                         ["T/V root/B: cadre.hmi.pulse_width is not defined by the project's library (cadre/hmi)"])
        for script, path in (("cadre.hmi.force (self.session, d, 'on')", "W16"),
                             ("cadre.hmi.error_mask\n(self.session, d, True)", "W17"),
                             ("cadre . hmi . bypass (self.session, d, c, True)", "W10"),
                             ("cadre.hmi.reset_interlocks  (self.session, d)", "W11"),
                             ("cadre.hmi.ack_top (scope, self.session)", "W6"),
                             ("cadre.hmi.command (self.session, 'W13', d, 'manual', True)", "W13"),
                             ("cadre . hmi . command( self.session , 'W5' , d, 'fault', False)", "W5")):
            self.assertEqual(self.problems(self.button(script, "{view.custom.can.%s}" % path)), [], script)
            probs = self.problems(self.button(script))
            self.assertTrue(len(probs) == 1 and "(write path %s)" % path in probs[0], (script, probs))
        # `command` named and not called with a path the gate can read: no permission answers for it
        for script in ("c = cadre.hmi.command\nc(self.session, 'W1', d, 'cmd', True)",
                       "cadre.hmi.command.__call__(self.session, 'W1', d, 'cmd', True)",
                       "apply(cadre.hmi.command, [self.session, 'W1', d, 'cmd', True])"):
            probs = self.problems(self.button(script, "{view.custom.can.W1}"))
            self.assertTrue(len(probs) == 1 and "(write path ?)" in probs[0], (script, probs))
        # an import, an alias and a lookup of `cadre` and of `system`, whatever the control's binding
        ok = "{view.custom.can.W18} && {view.custom.can.W16}"
        bare_cadre, bare_system = "cadre named without cadre.hmi or cadre.icons", "system named without a module"
        for script, text in (
                ("from cadre import hmi\nhmi.pulse(self.session, d, 'trigger')", bare_cadre),
                ("from cadre import hmi as h\nh._checked_writes(self.session, 'W18', d, [('trigger', False)])", bare_cadre),
                ("import cadre\nc = cadre\nc.hmi.pulse(self.session, d, 'trigger')", bare_cadre),
                ("getattr(cadre, 'hmi').pulse(self.session, d, 'trigger')", bare_cadre),
                ("cadre.\\\nhmi.pulse(self.session, d, 'trigger')", bare_cadre),
                ("from cadre.hmi import pulse\npulse(self.session, d, 'trigger')", "cadre.hmi is not a function for a view"),
                ("import cadre.hmi as h\nh.pulse(self.session, d, 'trigger')", "cadre.hmi is not a function for a view"),
                ("from system import tag\ntag.writeBlocking([p], [True])", bare_system),
                ("import system as s\ns.tag.writeBlocking([p], [True])", bare_system),
                ("s = system\ns.tag.writeBlocking([p], [True])", bare_system),
                ("getattr(system, 'tag').writeBlocking([p], [True])", bare_system),
                ("system.__dict__['tag'].writeBlocking([p], [True])", bare_system),
                ("__import__('system').tag.writeBlocking([p], [True])", bare_system),
                ("t = cadre.hmi.system\nt.tag.writeBlocking([p], [True])", bare_system),
                ("cadre.hmi.system.tag.writeBlocking([p], [True])", "a direct system.tag.writeBlocking (use"),
                ("from system.tag import writeBlocking as w\nw([p], [True])", "a direct system.tag (use"),
                ("import system.tag\nsystem . tag . writeBlocking([p], [True])", "a direct system.tag.writeBlocking (use")):
            probs = self.problems(self.button(script, ok))
            self.assertTrue(any(text in p for p in probs), (script, probs))
        # what the library's views do call stays free
        fine = ("system.perspective.openDock(id='faceplate')\nv = system.tag.readBlocking([p])[0].value\n"
                "cadre.hmi.select_device(self.session, d, 'pump')\nx = cadre.icons.elements('pump')")
        self.assertEqual(self.problems(self.button(fine)), [])
        # a pulse wherever a script may sit: refused at view level and from an expression; in a custom
        # method, a message handler or a change script of a component it needs that component's binding
        level = {"custom.x": {"binding": {"type": "expr", "config": {"expression": "now(1000)"}, "transforms": [
            {"type": "script", "code": "\treturn cadre.hmi.pulse(self.session, self.params.deviceId, 'trigger')"}]}}}
        self.assertTrue(any("a checked write called at view level" in p for p in self.problems(propConfig=level)))
        run = {"type": "ia.display.label", "meta": {"name": "L"}, "propConfig": {"props.text": {"binding": {
            "type": "expr", "config": {"expression": "runScript('cadre.hmi.pulse', 0, {session}, {view.params.d}, 'trigger')"}}}}}
        self.assertTrue(any("called from an expression" in p for p in self.problems(run)))
        for more in ({"scripts": {"customMethods": [{"name": "go", "params": [], "script": pulse}]}},
                     {"scripts": {"messageHandlers": [{"messageType": "go", "script": pulse, "pageScope": True}]}},
                     {"propConfig": {"custom.x": {"onChange": {"script": pulse}}}}):
            probs = self.problems({"type": "ia.display.label", "meta": {"name": "L"}, **more})
            self.assertTrue(len(probs) == 1 and "(write path W18)" in probs[0], (more, probs))
        # the names the gate reads are those of the table of calls
        self.assertEqual(gates.NAME_PATH, {"bypass": "W10", "reset_interlocks": "W11", "ack_top": "W6", "force": "W16",
                                           "error_mask": "W17", "pulse": "W18", "page_pulse": "W18"})
        self.assertEqual(sorted(set(gates.CHECKED_NAMES.findall(" ".join(c[:-1] for c in gates.CHECKED_CALLS)))),
                         sorted(["command"] + list(gates.NAME_PATH)))

    def test_a_two_way_tag_binding_is_refused_wherever_it_sits(self):
        """Only a bidirectional tag binding writes a tag. A field bound two ways onto a view property
        writes that property and no tag, unless the property's own tag binding is two way, and that
        binding is refused at view level."""
        tag = lambda two_way: {"binding": {"type": "tag", "config": dict(
            {"mode": "indirect", "tagPath": "{0}/sp", "references": {"0": "{view.params.deviceId}"}},
            **({"bidirectional": True} if two_way else {}))}}
        field = {"type": "ia.input.numeric-entry-field", "meta": {"name": "F"}, "propConfig": {"props.value": {
            "binding": {"type": "property", "config": {"path": "view.custom.sp", "bidirectional": True}}}}}
        self.assertEqual(self.problems(field, propConfig={"custom.sp": tag(False)}), [])
        probs = self.problems(field, propConfig={"custom.sp": tag(True)})
        self.assertEqual(len(probs), 1)
        self.assertIn("T/V view custom.sp: a bidirectional tag binding writes without a check", probs[0])
        direct = dict(field, propConfig={"props.value": tag(True)})
        self.assertTrue(any("a bidirectional tag binding" in p for p in self.problems(direct)))

    def test_every_built_control_names_its_own_path(self):
        """The views the generator builds: every control that calls a checked write follows the path it
        calls (the gate passes), and none calls a private function."""
        from hmi import framework, gates
        calls = 0
        for path, doc in {**framework.framework_views(), **framework.module_overrides()}.items():
            text = json.dumps(doc)
            self.assertNotIn("cadre.hmi._", text, path)
            for n in view_nodes(doc).values():
                for script in gates._scripts_of(n):
                    for w in gates._paths_called(script):
                        calls += 1
                        self.assertTrue(gates._follows_permissions(n, "props.enabled", w), (path, n["meta"]["name"], w))
        self.assertGreaterEqual(calls, 12)   # F029: the command buttons ask, the Confirm rows and row answers write


class DeviceGateTests(unittest.TestCase):
    """Gate G7 devices: the force as one whole encoding, the alarm sources, the bindings inside a
    device folder, a writable expression tag and the controller block's flags."""

    def setUp(self):
        self.base = DeviceModelTests()
        self.base.setUp()

    def run_gate(self, change, tags="fixture", scope="*cadre_hmi_pilot*"):
        from hmi import gates, library_profile
        b = self.base
        model, desc, tag_model = copy.deepcopy(b.model), copy.deepcopy(b.desc), copy.deepcopy(b.tags)
        change({d["id"]: d for d in model["devices"]}, {s["id"]: s for s in desc["symbols"]},
               {f["name"]: f for f in tag_model["tags"]})
        return gates.g7_devices(model, library_profile.build(screen.load_contracts()), screen.device_symbols([desc]),
                                tag_model if tags == "fixture" else None, scope)

    def fails(self, change, text, **kw):
        res = self.run_gate(change, **kw)
        self.assertTrue(any(text in p for p in res["problems"]), (text, res["problems"]))
        return res

    def test_the_fixture_has_no_problem_and_no_warning(self):
        res = self.run_gate(lambda d, s, f: None)
        self.assertEqual((res["ok"], res["problems"], res["warnings"]), (True, [], []))

    def test_a_force_is_one_whole_encoding(self):
        rw = {"type": "Boolean", "access": "write"}

        def drop(folder, name):
            mnt = next(t for t in folder["tags"] if t["name"] == "mnt")
            mnt["tags"] = [t for t in mnt["tags"] if t["name"] != name]
        self.fails(lambda d, s, f: (d["P1"]["members"].pop("mnt/forceOff"), drop(f["P1"], "forceOff")),
                   "P1: member 'mnt/forceOn' without 'mnt/forceOff': a force needs both members")
        self.fails(lambda d, s, f: d["XV1"]["members"].pop("mnt/forceValue"),
                   "XV1: member 'mnt/forceMode' without 'mnt/forceValue'", tags=None)
        self.fails(lambda d, s, f: d["P1"]["members"]["mnt/forceOff"].update(access="read"),
                   "P1: 'mnt/forceOn' and 'mnt/forceOff' differ in access")
        self.fails(lambda d, s, f: d["P1"]["members"].update({"mnt/forceMode": dict(rw), "mnt/forceValue": dict(rw)}),
                   "P1: lists the force twice (mnt/forceOn, mnt/forceOff and mnt/forceMode, mnt/forceValue)", tags=None)
        # a read only force, whole, is a force the faceplate shows and does not offer
        res = self.run_gate(lambda d, s, f: [d["DI1"]["members"][m].update(access="read") for m in ("mnt/forceOn", "mnt/forceOff")])
        self.assertTrue(res["ok"], res["problems"])

    def test_alarm_sources_are_bounded(self):
        for pattern in ("prov:default:/tag:*", "prov:default:/tag:*:/alm:*", "prov:default:/tag:*/*:/alm:Fault"):
            self.fails(lambda d, s, f: d["P1"].update(alarmSources=[pattern]), "names no tag")
            self.assertEqual(screen.devices_schema_errors({"schema": "cadre-hmi-devices/1", "tagRoot": "[default]site", "devices": [
                {"id": "P1", "kind": "pump", "members": {}, "alarmSources": [pattern]}]}, "m"), [])   # the schema lets it by
        # two devices on one source, and a pattern that takes in another device's: reported, not failed
        p1 = "prov:default:/tag:cadre_hmi_pilot/src/P1_OE:/alm:*"
        res = self.run_gate(lambda d, s, f: d["P2"].update(alarmSources=[p1]))
        self.assertTrue(res["ok"])
        self.assertEqual(len(res["warnings"]), 1)
        self.assertIn("P1 and P2: alarm sources", res["warnings"][0])
        res = self.run_gate(lambda d, s, f: d["P1"].update(alarmSources=["prov:default:/tag:cadre_hmi_pilot/*"]))
        self.assertTrue(res["ok"])
        self.assertEqual(sorted(w.split(":")[0] for w in res["warnings"]),
                         ["P1 and FT1", "P1 and PIC1", "P1 and PIC1", "P1 and SQ1", "P1 and TST1", "P1 and XV1"])    # FT1 by its folder
        # a source outside the alarm scope of the build: the frame's lists would leave it out
        res = self.run_gate(lambda d, s, f: d["P1"].update(alarmSources=["prov:default:/tag:site/P1_OE:/alm:*"]))
        self.assertEqual((res["ok"], len(res["warnings"])), (True, 1))
        self.assertIn("lies outside the alarm scope '*cadre_hmi_pilot*'", res["warnings"][0])
        self.assertEqual(self.run_gate(lambda d, s, f: d["P1"].update(alarmSources=["prov:default:/tag:site/P1_OE:/alm:*"]),
                                       scope="*")["warnings"], [])

    def test_a_binding_inside_the_device_folder_meets_a_tag(self):
        def no_tag(folder, name):
            folder["tags"] = [t for t in folder["tags"] if t["name"] != name]
        # `alert` on a member the library knows and the model does not list, with and without a tag model
        for tags in ("fixture", None):
            self.fails(lambda d, s, f: (d["P1"]["members"].pop("fault"), no_tag(f["P1"], "fault")),
                       "P1: 'alert' is bound to 'P1/fault'; the model lists no member 'fault' for P1", tags=tags)
        # `badgeControl` on a tag of the folder that is no faceplate member: the tag model must carry it
        self.fails(lambda d, s, f: no_tag(f["P1"], "forceBadge"),
                   "P1: 'badgeControl' is bound to 'P1/forceBadge', which neither the device model nor the tag model carries")
        self.assertTrue(self.run_gate(lambda d, s, f: no_tag(f["P1"], "forceBadge"), tags=None)["ok"])   # nothing to check against
        # a binding outside the device folder is the descriptor's own affair
        res = self.run_gate(lambda d, s, f: s["P1"]["bind"].update(alert="src/P1_OE"))
        self.assertTrue(res["ok"], res["problems"])

    def test_a_writable_member_is_not_an_expression_tag(self):
        def as_expression(d, s, f):
            sp = next(t for t in f["PIC1"]["tags"] if t["name"] == "sp")
            sp.update(valueSource="expr", expression="50")
        self.fails(as_expression, "PIC1: member 'sp' is marked writable and is an expression tag")
        # a reference tag writes its source (GF-47), and a read only member may be an expression
        def as_reference(d, s, f):
            next(t for t in f["PIC1"]["tags"] if t["name"] == "sp").update(valueSource="reference", sourceTagPath="[.]x")
        self.assertTrue(self.run_gate(as_reference)["ok"])

    def test_a_block_draws_only_what_the_device_lists(self):
        def no_member(name):
            def change(d, s, f):
                d["PIC1"]["members"].pop(name)
                d["PIC1"]["trend"] = ["value"]
                f["PIC1"]["tags"] = [t for t in f["PIC1"]["tags"] if t["name"] != name]
                for sym in (s["PIC1"], s["PIC1_PV"]):
                    sym["bind"] = {k: v for k, v in sym["bind"].items() if not v.endswith("/" + name)}
            return change
        res = self.fails(no_member("sp"), "PIC1: hasSetpoint is true; the model lists no member 'sp' for PIC1")
        self.assertTrue(any("PIC1_PV: hasSetpoint is true" in p for p in res["problems"]))   # the field that opens the loop
        self.fails(no_member("out"), "PIC1: hasOutput is true; the model lists no member 'out' for PIC1")

        def unflagged(d, s, f):
            no_member("out")(d, s, f)
            s["PIC1"]["params"].pop("hasOutput")
        self.assertTrue(self.run_gate(unflagged)["ok"])                          # the default draws no output


# ---------------------------------------------------------------------------------------
# Stage 2b: the sequence kind (a step number with a text per step), the pulse command of
# write path W18, and the sizes a layouter reads from the library profile.
# ---------------------------------------------------------------------------------------
SEQ = ["step", "stepText", "trigger", "fault"]
SQ = "[default]t/SQ1"
IGW = Path(os.environ.get("CADRE_IGNITION_WIKI", "F:/repos/Ignition-Wiki")) / "schemas"


def seq_tags(**members):
    return {f"{SQ}/{m}": v for m, v in members.items()}


class SequenceKindTests(unittest.TestCase):
    """The kind `sequence`: its contract and tables, its block on a page, its place in the flow graph,
    the bind rule, and `Faceplate/Sequence` with its stepped trend."""

    def test_contract_and_tables(self):
        from hmi import framework, gates, library
        c = screen.load_contracts()["Instrument/Sequence"]
        self.assertEqual((c["kind"], c["anchor"], c["flow"], c["size"]), ("sequence", "box", "pass", [144, 72]))
        self.assertEqual(sorted(c["params"]), sorted(["text", "step", "hasStep", "label", "tag", "hasTag", "deviceId",
                                                      "deviceKind", "deviceLabel"]))
        # as the controller's block: no alert parameters, the tag shown, and the number only where asked for
        self.assertEqual(sorted(set(c["params"]) & {"alert", "alertFrameStatus", "alertFrameMode"}), [])
        self.assertEqual((c["params"]["deviceKind"], c["params"]["hasStep"], c["params"]["hasTag"]),
                         ("sequence", False, True))
        self.assertNotIn("state", c)                                             # no gate parameter: never gated
        self.assertEqual(screen.KIND_VIEW["sequence"], "Instrument/Sequence")
        self.assertEqual(screen.FACEPLATE_MEMBERS["sequence"],
                         {"step": ("Int4", 0), "stepText": ("String", ""), "trigger": ("Boolean", False),
                          "fault": ("Boolean", False)})
        self.assertEqual(screen.known_members("sequence"),
                         {"step": "Int4", "stepText": "String", "trigger": "Boolean", "fault": "Boolean", "alarmAck": "Boolean",
                          **{m: "Boolean" for m in ("inService", "enabled", "normal", "cmdInService", "cmdOutOfService",
                                                    "cmdEnable", "cmdDisable")}})   # the asm faceplate's (COB-158)
        rule = screen.bind_rule("sequence")
        self.assertEqual((rule["text"], rule["step"]), ("stepText", "step"))
        self.assertEqual(screen.TREND_KINDS["sequence"], "step")
        self.assertEqual(screen.pulse_members("sequence")[0], "trigger")
        self.assertEqual([k for k in screen.KIND_VIEW if screen.pulse_members(k)], ["sequence", "generator"])
        self.assertEqual(framework.FACEPLATE_VIEW["sequence"], "Faceplate/Sequence")
        self.assertEqual(framework.FACEPLATE_TABS["sequence"], [("status", "Status"), ("trend", "Trend"), ("alarms", "Alarms")])
        self.assertEqual(framework.FACEPLATE_READS["sequence"], SEQ)
        self.assertEqual(sorted(framework.FACEPLATE_READS["sequence"]), sorted(screen.FACEPLATE_MEMBERS["sequence"]))
        self.assertIn("'sequence', 'Faceplate/Sequence'", framework.FACEPLATE_OF_KIND)
        self.assertIn("Faceplate/Sequence", gates.FACEPLATES)
        self.assertIn("Instrument/Sequence", library.library_views())
        self.assertEqual(screen.schema_errors([fixture("pilot-supply.json")], ["d"]), [])

    def test_a_pass_node_that_is_never_gated(self):
        self.assertEqual(diagram.node_role("sequence"), "pass")
        self.assertNotIn("sequence", diagram.GATED)
        desc = {"screen": {"width": 800, "height": 400}, "junctions": [],
                "symbols": [{"id": "TA", "kind": "tank", "x": 0, "y": 0, "w": 100, "h": 100},
                            {"id": "SQ1", "kind": "sequence", "x": 300, "y": 14, "w": 144, "h": 72},
                            {"id": "TB", "kind": "tank", "x": 600, "y": 0, "w": 100, "h": 100}],
                "pipes": [{"id": "a", "from": {"ref": "TA", "side": "right"}, "to": {"ref": "SQ1", "side": "left"}},
                          {"id": "b", "from": {"ref": "SQ1", "side": "right"}, "to": {"ref": "TB", "side": "left"}}]}
        g, geo = diagram.build_graph(desc, screen.load_contracts())
        self.assertEqual((g.nodes["SQ1"], g.gate_of), ("pass", {}))
        self.assertEqual(diagram.compile_flow(g), {"a": [frozenset()], "b": [frozenset()]})   # the medium always passes
        self.assertEqual(diagram.solve(g, {}), {"a", "b"})
        self.assertEqual((geo["a"][2], geo["b"][0]), ((300, 50.0), (444, 50.0)))   # a box: the pipes meet its edges
        doc, info = screen.build_screen(desc, screen.load_contracts())
        self.assertEqual((info["errors"], info["gaps"], info["flow"]["ok"]), ([], [], True))
        self.assertNotIn("g_SQ1", doc["custom"])                                 # no gate property on the view

    def test_the_block_on_a_page(self):
        from hmi import library
        doc, contract = library.instrument_sequence()
        nodes = view_nodes(doc)
        self.assertEqual(doc["props"]["defaultSize"], {"width": 144, "height": 72})
        self.assertEqual([c["meta"]["name"] for c in doc["root"]["children"]], ["Tag", "Text", "Step"])
        text = lambda n: nodes[n]["propConfig"]["props.text"]["binding"]["config"]["expression"]
        self.assertEqual(text("Text"), "{view.params.text}")
        self.assertEqual(text("Step"), "'Step ' + numberFormat({view.params.step}, '0')")   # "Step 2", whole
        self.assertEqual(display(nodes["Step"]), "{view.params.hasStep}")
        self.assertIn("{view.params.tag}, {view.params.label}", text("Tag"))
        self.assertIn("instrument-value-regular-active", nodes["Text"]["props"]["style"]["classes"])   # the text large
        self.assertIn("instrument-unit", nodes["Step"]["props"]["style"]["classes"])                    # the number small
        script = doc["root"]["events"]["dom"]["onClick"]["config"]["script"]
        self.assertIn("self.view.params.deviceKind or 'sequence'", script)
        self.assertIn("system.perspective.openDock(id='faceplate')", script)
        self.assertEqual([b for _w, _k, b in bindings(doc) if b["type"] != "expr"], [])   # parameters only
        self.assertEqual(set(doc["params"]), set(contract["params"]))

    def test_the_bind_rule(self):
        contracts = screen.load_contracts()

        def errors(sym):
            rep = screen.Report()
            node, _c, _cfg = screen.embed_symbol(dict({"x": 10, "y": 20, "w": 144, "h": 72}, **sym), contracts,
                                                 "[default]t", rep, toolbar=True)
            return rep.errors, node
        good = {"id": "SQ1", "kind": "sequence", "device": True, "params": {"tag": "FLT-1", "hasStep": True},
                "bind": {"text": "SQ1/stepText", "step": "SQ1/step"}}
        errs, node = errors(good)
        self.assertEqual(errs, [])
        self.assertEqual((node["props"]["path"], node["position"]), ("Instrument/Sequence", pv.cpos(10, 20, 144, 72)))
        self.assertEqual(node["props"]["params"]["deviceId"], "[default]t/SQ1")
        cfg = node["propConfig"]
        self.assertEqual(sorted(cfg), ["props.params.step", "props.params.text"])   # no toolbar binding on a box
        self.assertEqual(cfg["props.params.text"]["binding"]["config"]["tagPath"], "[default]t/SQ1/stepText")
        errs, _ = errors(dict(good, bind={"text": "SQ1/label", "step": "SQ9/step"}))
        self.assertEqual(len([e for e in errs if "faceplate contract" in e]), 2)
        self.assertTrue(any("'SQ1/stepText' (faceplate contract)" in e for e in errs))
        errs, _ = errors(dict(good, bind={"value": "SQ1/step"}))
        self.assertTrue(any("parameter 'value' is not in the Instrument/Sequence contract" in e for e in errs))
        idx = screen.device_index([{"tagRoot": "[default]t", "symbols": [dict(good, x=0, y=0, label="Filter")]}])
        self.assertEqual(idx, [{"folder": "[default]t/SQ1", "kind": "sequence", "title": "FLT-1", "label": "Filter",
                                "unit": ""}])

    def test_generated_tags(self):
        def types(doc, folder):
            node = next(t for t in doc["tags"] if t["name"] == folder)
            return {t["name"]: (t["dataType"], t["value"]) for t in node["tags"]}
        desc = dict(fixture("pilot-supply.json"), tagModel="generated")
        want = {"step": ("Int4", 0), "stepText": ("String", ""), "trigger": ("Boolean", False), "fault": ("Boolean", False)}
        self.assertEqual(types(screen.tags_document([desc]), "SQ1"), want)       # the members of the kind
        self.assertEqual(types(screen.tags_document([desc], fixture("pilot-devices.json")), "SQ1"), want)   # the model's
        lean = fixture("pilot-devices.json")
        sq = next(d for d in lean["devices"] if d["id"] == "SQ1")
        sq["members"] = {"step": {"type": "Int2", "access": "read"}}
        sq.pop("trend")
        only = copy.deepcopy(desc)
        next(s for s in only["symbols"] if s["id"] == "SQ1")["bind"].pop("text")
        self.assertEqual(types(screen.tags_document([dict(only, tagValues={"SQ1/step": 3})], lean), "SQ1"),
                         {"step": ("Int2", 3)})                                  # exactly what the model lists
        # a bound member of every other kind keeps the type it had (the pump's speed, the valve's state)
        sample = json.loads((ROOT / "screens/sample-pump-station.json").read_text(encoding="utf-8"))
        leaves = {}

        def walk(node, path=()):
            for t in node.get("tags", []):
                walk(t, path + (t["name"],)) if t["tagType"] == "Folder" else leaves.update({"/".join(path + (t["name"],)): t["dataType"]})
        walk(screen.tags_document([sample]))
        self.assertEqual({k.split("/")[-1]: v for k, v in leaves.items() if k.split("/")[-1] in ("state", "speed", "mode")},
                         {"state": "Boolean", "speed": "Float8", "mode": "Int4"})
        # the member's own type replaces the type a parameter's default gives, and the two differ for
        # the step of a sequence alone: every bound member of every other kind has the type it had
        contracts, differ, compared = screen.load_contracts(), [], 0
        for kind, members in screen.FACEPLATE_MEMBERS.items():
            params = contracts.get(screen.KIND_VIEW.get(kind, ""), {"params": {}})["params"]   # `instrument` has no page view
            for param, member in sorted(screen.bind_rule(kind).items()):
                if param in params and member in members:
                    compared += 1
                    by_default = "Boolean" if isinstance(params[param], bool) else (
                        "Float8" if isinstance(params[param], (int, float)) else "String")
                    if by_default != members[member][0]:
                        differ.append((kind, param, member, by_default, members[member][0]))
        self.assertEqual(differ, [("sequence", "step", "step", "Float8", "Int4")])
        self.assertGreaterEqual(compared, 15)

    def test_faceplate(self):
        from hmi import framework
        fp = framework.faceplate_sequence()
        nodes = view_nodes(fp)
        self.assertEqual([c["meta"]["name"] for c in nodes["Tabs"]["children"]], ["Tab_status", "Tab_trend", "Tab_alarms"])
        self.assertEqual(display(nodes["Tab_trend"]), "{view.custom.trend.step}")
        self.assertNotIn("position.display", nodes["Tab_status"]["propConfig"])
        self.assertEqual((fp["custom"]["tab"], fp["custom"]["dev"]), ("status", framework.dev_default(SEQ)))
        self.assertEqual(fp["custom"]["dev"]["pulses"], {"trigger": "trigger"})
        self.assertEqual(fp["custom"]["dev"]["value"], {"step": 0, "stepText": "", "trigger": False, "fault": False})
        text = lambda n: nodes[n]["propConfig"]["props.text"]["binding"]["config"]["expression"]
        self.assertEqual(text("StepText"), "{view.custom.dev.value.stepText}")
        self.assertIn("instrument-value-m-active", nodes["StepText"]["props"]["style"]["classes"])    # large
        self.assertEqual(text("StepValue"), "numberFormat({view.custom.dev.value.step}, '0')")
        self.assertEqual(text("FaultValue"), "if({view.custom.dev.value.fault}, 'Fault', 'Normal')")
        self.assertIn("badge-alarm", json.dumps(nodes["FaultRow"]))
        # the pulse button: the checked function, the advisory binding, the caption from the poll
        b = nodes["Pulse_trigger"]
        self.assertIn("'path': 'W18', 'member': 'trigger', 'value': True",   # F029: asked, then confirmed
                      b["events"]["component"]["onActionPerformed"]["config"]["script"])
        self.assertEqual(b["propConfig"]["props.enabled"]["binding"]["config"]["expression"],
                         "{view.custom.can.W18} && {view.custom.dev.write.trigger} && {view.custom.dev.allowed.W18}")
        self.assertEqual(text("Pulse_trigger"), "{view.custom.dev.pulses.trigger}")
        self.assertEqual(display(b), "{view.custom.dev.writable.trigger}")
        self.assertEqual([c["meta"]["name"] for c in nodes["Commands"]["children"]],
                         ["Pulse_" + m for m in framework.PULSE_MEMBERS if m in SEQ])   # one button per pulse member
        self.assertIn("{view.custom.message}", json.dumps(nodes["Message"]))
        self.assertNotIn("Reset", nodes)                                         # the fault is shown, not reset here
        for c in nodes["Pane_status"]["children"]:                               # every row follows its member
            self.assertIn("position.display", c.get("propConfig") or {}, c["meta"]["name"])
        self.assertEqual([(w, k) for w, k, x in bindings(fp) if x["type"] == "tag"], [])

    def test_the_rows_a_device_shows(self):
        from hmi import framework
        nodes = view_nodes(framework.faceplate_sequence())
        rows = ["StepTitle", "StepText", "StepRow", "FaultRow", "CommandTitle", "Commands", "Pulse_trigger"]

        def visible(tags, entry, roles=("Administrator",)):
            ns, _ = hmi_ns(tags)
            dev = ns["device_read"](session(list(roles) if roles else None, [entry], model="write" in entry), SQ, SEQ)
            return [n for n in rows if shown(display(nodes[n]), dev)], dev
        full = seq_tags(step=2, stepText="Drive Out", trigger=False, fault=False)
        listed = {"folder": SQ, "write": ["trigger"], "pulses": [{"member": "trigger", "caption": "Start cycle"}]}
        got, dev = visible(full, listed)
        self.assertEqual(got, rows)
        self.assertEqual((dev["pulses"], dev["write"]["trigger"]), ({"trigger": "Start cycle"}, True))
        got, dev = visible(full, listed, roles=None)                             # shown, and disabled
        self.assertEqual((got, dev["write"]["trigger"]), (rows, False))
        # a step number alone; a trigger the model marks read only; a project without a device model
        self.assertEqual(visible(seq_tags(step=3), {"folder": SQ, "write": []})[0], ["StepTitle", "StepRow"])
        self.assertEqual(visible(full, {"folder": SQ, "write": []})[0], rows[:4])
        got, dev = visible(full, {"folder": SQ})
        self.assertEqual((got, dev["pulses"]), (rows, {"trigger": "trigger"}))   # the member's name
        self.assertEqual(visible(seq_tags(fault=True), {"folder": SQ, "write": []})[0], ["StepTitle", "FaultRow"])
        self.assertEqual(visible({}, listed)[0], [])

    def test_the_stepped_trend(self):
        from hmi import framework
        fp = framework.faceplate_sequence()
        chart = view_nodes(fp)["Chart"]
        plot = chart["props"]["plots"][0]
        self.assertEqual([s["name"] for s in chart["props"]["series"]], ["value"])
        self.assertEqual(len(plot["trends"]), 1)                                 # no limits series
        self.assertEqual((plot["trends"][0]["columns"], plot["trends"][0]["interpolation"]),
                         ([{"key": "step"}], "curveStepAfter"))
        self.assertEqual(len(plot["axes"]), 1)
        b = chart["propConfig"]["props.series[0].data"]["binding"]
        self.assertEqual((b["type"], b["config"]["tags"]), ("tag-history", "{view.custom.historyTags}"))
        self.assertEqual(fp["custom"]["historyTags"], [{"path": "", "alias": "step"}])   # a list default: gate G7 history
        self.assertEqual((fp["custom"]["trend"], fp["custom"]["hours"]), ({"step": False}, 1))
        code = lambda k: fp["propConfig"][k]["binding"]["transforms"][0]["code"]
        self.assertIn("cadre.hmi.trended(self.session, value, ['step'])", code("custom.trend"))
        self.assertIn("cadre.hmi.trend_tags(self.session, value, 'step')", code("custom.historyTags"))
        # the values are those the Ignition-Wiki registry declares for the chart and the binding
        chart_schema = json.loads((IGW / "components/ia.chart.timeseries.schema.json").read_text(encoding="utf-8"))
        curves = chart_schema["properties"]["plots"]["items"]["properties"]["trends"]["items"]["properties"]["interpolation"]
        self.assertIn(framework.STEPPED, curves["enum"])
        self.assertEqual(curves["default"], "curveLinear")
        history = json.loads((IGW / "bindings/binding-tag-history.json").read_text(encoding="utf-8"))
        self.assertIn("LastValue", history["definitions"]["aggregate"]["suggestions"])
        self.assertIn("aggregate", history["properties"]["tags"]["oneOf"][0]["items"]["properties"])
        # the path object of a stepped member asks for the last value of each interval, no other does
        ns, _ = hmi_ns(seq_tags(step=1, value=2.0))
        self.assertEqual(ns["history_tags"](SQ, "step", "step"), [{"path": f"{SQ}/step", "alias": "step", "aggregate": "LastValue"}])
        self.assertEqual(ns["history_tags"](SQ), [{"path": f"{SQ}/value", "alias": "value"}])
        s = session(None, [], [{"deviceId": SQ, "member": "step"}])
        self.assertEqual(ns["trended"](s, SQ, ["step"]), {"step": True})
        self.assertEqual(ns["trend_tags"](s, SQ, "step"), [{"path": f"{SQ}/step", "alias": "step", "aggregate": "LastValue"}])
        self.assertEqual(ns["trend_tags"](session(None), SQ, "step"), [{"path": "", "alias": "step"}])   # not trended
        self.assertEqual(framework.STEP_MEMBERS, tuple(ns["STEP_MEMBERS"]))
        # the trend page's card draws a stepped member as steps and every other as before
        card = view_nodes(framework.trend_card())["Chart"]
        self.assertEqual(card["propConfig"]["props.plots[0].trends[0].interpolation"]["binding"]["config"]["expression"],
                         "if({view.params.member} = 'step', 'curveStepAfter', 'curveLinear')")
        self.assertNotIn("interpolation", card["props"]["plots"][0]["trends"][0])
        for other in (framework.faceplate_instrument(), framework.faceplate_controller(), framework.faceplate_tank()):
            self.assertNotIn("interpolation", json.dumps(view_nodes(other)["Chart"]))
        # the trend index lists the step where the tag model historises it, or the device model names it
        desc, tags = fixture("pilot-supply.json"), fixture("pilot-tags.json")
        self.assertIn(("SQ1", "step"), [(t["deviceId"].split("/")[-1], t["member"]) for t in screen.trend_index([desc], tags)])
        self.assertEqual(framework.expected_tabs("sequence", SEQ, ["step"]), ["Status", "Trend", "Alarms"])
        self.assertEqual(framework.expected_tabs("sequence", SEQ), ["Status", "Alarms"])
        self.assertTrue(framework.trend_by_index("sequence") and framework.trend_by_index("controller"))
        self.assertFalse(framework.trend_by_index("instrument") or framework.trend_by_index("pump"))

    def test_gate_g1_reads_inside_the_chart(self):
        """Gate G1 below the top level of a component's props, which the validator of the Ignition-Wiki
        does not read: an enumerated value, a key of a closed object and a bound path, here the
        chart's `plots[].trends[]` that carry the stepped line."""
        from hmi import gates, parent as par
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            res = gates.g1_registry(base)
            self.assertTrue(res["ok"] and "ERROR: 0" in res["summary"], res["summary"])

            def broken(view, change):
                vf = base / "com.inductiveautomation.perspective/views" / view / "view.json"
                good = vf.read_text(encoding="utf-8")
                doc = json.loads(good)
                change(next(n for n, _p in gates.walk(doc["root"]) if n.get("type") == "ia.chart.timeseries"))
                vf.write_text(json.dumps(doc), encoding="utf-8")
                res = gates.g1_registry(base)
                vf.write_text(good, encoding="utf-8")
                self.assertFalse(res["ok"])
                self.assertIn("ERROR: 1", res["summary"])
                return res["summary"][-1]
            trend = lambda c: c["props"]["plots"][0]["trends"][0]
            line = broken("Faceplate/Sequence", lambda c: trend(c).update(interpolation="curveStepped"))
            self.assertIn("ENUM_VIOLATION", line)
            self.assertIn("props.plots[0].trends[0].interpolation is 'curveStepped'; declared domain is", line)
            self.assertIn("Faceplate", line)
            self.assertIn("props.plots[0].trends[0].type is 'linez'",
                          broken("Faceplate/Sequence", lambda c: trend(c).update(type="linez")))
            self.assertIn("props.plots[0].trends[0].interpolationz is not declared",
                          broken("Faceplate/Controller", lambda c: trend(c).update(interpolationz="curveStepAfter")))
            # the card binds the interpolation: the bound path is read, the expression's values are not
            key = "props.plots[0].trends[0].interpolation"
            line = broken("Trend/Card", lambda c: c["propConfig"].update({key + "z": c["propConfig"].pop(key)}))
            self.assertIn(f"{key}z is bound; {key}z is not declared by ia.chart.timeseries", line)
            self.assertTrue(gates.g1_registry(base)["ok"])                       # each view was put back
            # a column object is open in the registry, so a misspelt `key` in it is undeclared and not
            # prohibited: the gate passes it, and `test_the_stepped_trend` holds the column as built
            vf = base / "com.inductiveautomation.perspective/views/Faceplate/Sequence/view.json"
            doc = json.loads(vf.read_text(encoding="utf-8"))
            column = trend(next(n for n, _p in gates.walk(doc["root"]) if n.get("type") == "ia.chart.timeseries"))["columns"][0]
            column["keyz"] = column.pop("key")
            vf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertTrue(gates.g1_registry(base)["ok"])
        # what the walk cannot follow it leaves alone, and the top level stays the validator's
        out = []
        gates._deep_props({"a": {"b": "x", "c": {"d": 1}}, "top": "x", "list": ["p", "q"]},
                          {"properties": {"a": {"properties": {"b": {"enum": ["y"]}, "c": {"$ref": "#/x"}}},
                                          "top": {"enum": ["y"]}, "list": {"items": {"enum": ["p"]}}}}, "props", out)
        self.assertEqual(out, [("ENUM_VIOLATION", "props.a.b is 'x'; declared domain is ['y']"),
                               ("ENUM_VIOLATION", "props.list[1] is 'q'; declared domain is ['p']")])
        self.assertIsNone(gates._bound_undeclared("props.a.c.anything", {"properties": {"a": {"properties": {"c": {"$ref": "#"}}}}}))
        self.assertIsNone(gates._bound_undeclared("custom.x", {"additionalProperties": False, "properties": {}}))
        self.assertEqual(gates._bound_undeclared("props.a.z", {"properties": {"a": {"properties": {}, "additionalProperties": False}}}),
                         "props.a.z")

    def test_the_gates_examine_the_new_views(self):
        from hmi import gates, parent as par
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            self.assertTrue(gates.g1_registry(base)["ok"])
            self.assertTrue(gates.g7_commands(base, None)["ok"])
            self.assertTrue(gates.g7_history(base, None)["ok"])
            vf = base / "com.inductiveautomation.perspective/views/Faceplate/Sequence/view.json"
            good = vf.read_text(encoding="utf-8")
            for old, new, text in (
                    # F029: the Confirm row makes the pulse, following the pending path
                    ("'W18', {view.custom.can.W18}", "'W18', true",
                     "enabled does not follow the permissions (write path {view.custom.pending.path})"),
                    ("{view.custom.can.W18}", "{view.custom.can.W1}",
                     "enabled does not follow the permissions (write path {view.custom.pending.path})"),
                    ("cadre.hmi.command(self.session, p.path, self.view.params.deviceId, p.member, p.value)",
                     "system.tag.writeBlocking([self.view.params.deviceId + '/trigger'], [True])", "a direct system.tag.write"),
                    ("cadre.hmi.command(self.session, p.path, self.view.params.deviceId, p.member, p.value)",
                     "cadre.hmi._checked_writes(self.session, 'W18', self.view.params.deviceId, [('trigger', True)])",
                     "cadre.hmi._checked_writes is not a function for a view")):
                self.assertIn(json.dumps(old)[1:-1], good, old)
                vf.write_text(good.replace(json.dumps(old)[1:-1], json.dumps(new)[1:-1]), encoding="utf-8")
                probs = gates.g7_commands(base, None)["problems"]
                self.assertTrue(probs and all("Faceplate/Sequence" in p and text in p for p in probs), (old, probs))
            doc = json.loads(good)
            doc["root"]["children"] = [c for c in doc["root"]["children"] if c["meta"]["name"] != "Pane_trend"]
            vf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertIn("Faceplate/Sequence: tab 'trend' has no pane", gates.g7_faceplates(base, None)["problems"])
            doc = json.loads(good)
            doc["custom"]["historyTags"] = ""
            vf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertTrue(any("Faceplate/Sequence" in p for p in gates.g7_history(base, None)["problems"]))


class PulseTests(unittest.TestCase):
    """`cadre.hmi.pulse`, write path W18: refused first, then true written to the pulse member and
    nothing else; and what `device_read` answers of a sequence."""

    def test_device_read_with_and_without_each_member(self):
        full = seq_tags(step=2.0, stepText="Drive Out", trigger=True, fault=False)
        admin = session(["Administrator"], [{"folder": SQ}])
        ns, calls = hmi_ns(dict(full))
        got = ns["device_read"](admin, SQ, SEQ)
        self.assertEqual(got["has"], {m: True for m in SEQ})
        self.assertEqual(got["value"], {"step": 2, "stepText": "Drive Out", "trigger": True, "fault": False})
        self.assertIsInstance(got["value"]["step"], int)                         # an integer, whatever the tag holds
        self.assertEqual((got["bad"], got["quality"], got["mnt"], got["force"]), ([], "", False, ""))
        self.assertEqual(got["pulses"], {"trigger": "trigger"})                  # no device model: the member's name
        self.assertEqual((got["writable"]["trigger"], got["write"]["trigger"]), (True, True))
        self.assertEqual((got["writable"]["step"], got["writable"]["stepText"]), (False, False))   # no path writes them
        for m in SEQ:                                                            # one member at a time is taken away
            ns, calls = hmi_ns({k: v for k, v in full.items() if not k.endswith("/" + m)})
            got = ns["device_read"](admin, SQ, SEQ)
            self.assertEqual([k for k in SEQ if not got["has"][k]], [m])
            self.assertEqual(got["value"][m], ns["MEMBER_DEFAULTS"][m], m)
            self.assertIsNotNone(got["value"][m])
            self.assertFalse(got["writable"][m] or got["write"][m], m)
            self.assertNotIn(f"{SQ}/{m}", [x for c in calls if c[0] == "read" for x in c[1]])
            self.assertEqual(got["pulses"], {"trigger": "trigger"})              # the key stays, the button hides
        # a step that reads null, and a text of bad quality: the typed default, and the member named
        ns, _ = hmi_ns(seq_tags(step=None, stepText=None), bad=[f"{SQ}/stepText"])
        got = ns["device_read"](admin, SQ, SEQ)
        self.assertEqual((got["value"]["step"], got["value"]["stepText"], got["quality"]), (0, "", "Bad quality: stepText"))
        # the captions of a device model reach the faceplate; one left out, or empty, is the member's name
        for pulses, caption in (([{"member": "trigger", "caption": "Start cycle"}], "Start cycle"),
                                ([{"member": "trigger", "caption": ""}], "trigger"), ([], "trigger"),
                                ([{"member": "other", "caption": "Other"}], "trigger"), (None, "trigger")):
            entry = {"folder": SQ, "write": ["trigger"], "pulses": pulses}
            ns, _ = hmi_ns(dict(full))
            got = ns["device_read"](session(["Administrator"], [entry], model=True), SQ, SEQ)
            self.assertEqual((got["pulses"], got["write"]["trigger"]), ({"trigger": caption}, True), pulses)
        # the model marks the trigger read only, or the write list is lost: no session may pulse
        for entry in ({"folder": SQ, "write": []}, {"folder": SQ}):
            got = ns["device_read"](session(["Administrator"], [entry], model=True), SQ, SEQ)
            self.assertEqual((got["has"]["trigger"], got["writable"]["trigger"], got["write"]["trigger"]), (True, False, False))
        got = ns["device_read"](session(None, [{"folder": SQ}]), SQ, SEQ)
        self.assertEqual((got["writable"]["trigger"], got["write"]["trigger"]), (True, False))   # shown, disabled
        # a faceplate without a pulse member answers no caption
        self.assertEqual(ns["device_read"](admin, SQ, ["state", "cmd"])["pulses"], {})
        from hmi import framework
        self.assertEqual(framework.dev_default(SEQ), ns["device_read"](None, "", SEQ))

    def test_pulse_refuses(self):
        entry = {"folder": SQ, "write": ["trigger"], "pulses": [{"member": "trigger", "caption": "Start cycle"}]}
        admin = session(["Administrator"], [entry], model=True)
        tags = seq_tags(step=1, trigger=False, fault=False, cmd=False)
        ns, calls = hmi_ns(tags)
        pulse = ns["pulse"]
        self.assertEqual(pulse(session(None, [entry]), SQ, "trigger"), ns["REFUSED"])               # nobody signed in
        self.assertEqual(pulse(session(["Operator"], [entry]), SQ, "trigger"), ns["REFUSED"])       # another role
        self.assertEqual(pulse(admin, "[default]t/SQ9", "trigger"), "Refused: not a device of this project")
        self.assertEqual(pulse(admin, "", "trigger"), "Refused: not a device of this project")
        for member in ("cmd", "fault", "step", "mnt/forceOn", "trigger/x", "", None):                # no pulse member
            self.assertEqual(pulse(admin, SQ, member), "Refused: %s is not a pulse command" % (member or "this"))
        # a member the device model does not mark writable, and a write list that is lost
        ro = session(["Administrator"], [{"folder": SQ, "write": ["cmd"]}], model=True)
        self.assertEqual(pulse(ro, SQ, "trigger"), "Refused: trigger is read only on this device")
        lost = session(["Administrator"], [{"folder": SQ}], model=True)
        self.assertEqual(pulse(lost, SQ, "trigger"), "Refused: trigger is read only on this device")
        self.assertEqual(calls, [])                                              # nothing was written by any of them
        self.assertIs(tags[f"{SQ}/trigger"], False)
        # a device that does not carry the member
        ns2, calls2 = hmi_ns(seq_tags(step=1))
        self.assertEqual(ns2["pulse"](admin, SQ, "trigger"), "Refused: this device has no trigger")
        self.assertEqual(calls2, [])
        # `command` writes no pulse member false, by its own path (handed to `pulse`, F029) or by another
        self.assertEqual(ns["command"](admin, "W18", SQ, "trigger", False), "Refused: a pulse command only writes true")
        self.assertEqual(ns["command"](admin, "W1", SQ, "trigger", True), "Refused: W1 does not write trigger")
        self.assertEqual(ns["_checked_writes"](admin, "W18", SQ, [("cmd", True)]), "Refused: W18 does not write cmd")
        self.assertEqual(ns["_checked_writes"](session(None, [entry]), "W18", SQ, [("trigger", True)]), ns["REFUSED"])
        self.assertEqual(calls, [])
        # the helper writes a pulse member nothing but true: no value that only reads as true, and no
        # false, so that no call of `cadre.hmi`, the private helper included, returns one to false
        for value in (False, 0, 1, 1.0, None, "true", "x", [True]):
            self.assertEqual(ns["_checked_writes"](admin, "W18", SQ, [("trigger", value)]),
                             "Refused: a pulse command only writes true", repr(value))
        for path in ("W1", "W5", "W16", "W17"):
            got = ns["command"](admin, path, SQ, "trigger", False)
            if path in ("W16", "W17"):   # handed to `force` and `error_mask` (F029), which refuse on their own
                self.assertTrue(got.startswith("Refused: "), (path, got))
            else:
                self.assertEqual(got, "Refused: %s does not write trigger" % path)
            self.assertEqual(ns["_checked_writes"](admin, path, SQ, [("trigger", False)]),
                             "Refused: %s does not write trigger" % path)
        self.assertEqual(calls, [])
        self.assertIs(tags[f"{SQ}/trigger"], False)

    def test_the_role_is_asked_first_and_a_crafted_argument_is_refused(self):
        entry = {"folder": SQ, "write": ["trigger"]}
        admin = session(["Administrator"], [entry], model=True)
        ns, calls = hmi_ns(seq_tags(trigger=False))
        pulse = ns["pulse"]
        # a session without the role is refused before the device and the member are examined, so it
        # learns nothing of either
        ghost = session(["Administrator"], [entry])
        ghost.props.auth.authenticated = False                                   # a role list, and nobody signed in
        for s in (session(None, []), session(None, [entry]), session(["Operator"], [entry]), session([], [entry]), ghost):
            for device, member in ((SQ, "trigger"), ("[default]t/SQ9", "cmd"), ("", ""), (None, None), (7, ["trigger"])):
                self.assertEqual(pulse(s, device, member), ns["REFUSED"], (device, member))
        # an identifier that is not text names no device, and a member that is not the name itself no pulse member
        for device in (7, 1.5, True, [SQ], (SQ,), {"folder": SQ}, SQ + "/", SQ.upper(), SQ + "/trigger"):
            self.assertEqual(pulse(admin, device, "trigger"), "Refused: not a device of this project", repr(device))
        for member in (["trigger"], ("trigger",), {"trigger": 1}, 1, True, " trigger", "trigger ", "trigger\n", "Trigger",
                       "TRIGGER", "./trigger", "../SQ1/trigger", "/trigger", "trigger/", SQ + "/trigger", "trigger.value"):
            self.assertTrue(pulse(admin, SQ, member).endswith(" is not a pulse command"), repr(member))
        self.assertEqual(pulse(admin, " " + SQ + " ", "trigger"), "")           # the identifier is trimmed, as everywhere
        self.assertEqual(calls, [("write", [f"{SQ}/trigger"], [True])])

    def test_pulse_does_not_ask_the_kind_of_the_device(self):
        """Without a device model the rule of the write path stands alone, as for W1 to W17: any device
        of the index whose folder carries a tag named `trigger` is pulsed by a session with the role.
        With a model the `write` list decides, and gate G7 devices lets no kind but one with the pulse
        member mark it (`PulseModelTests`)."""
        pump = "[default]t/P1"
        ns, calls = hmi_ns({f"{pump}/trigger": False, f"{pump}/cmd": False})
        for s in (session(["Administrator"], [{"folder": pump, "kind": "pump"}]),
                  session(["Administrator"], [{"folder": pump, "kind": "pump"}], model=False)):
            self.assertEqual(ns["pulse"](s, pump, "trigger"), "")
        self.assertEqual(calls, [("write", [f"{pump}/trigger"], [True])] * 2)
        for write in (["cmd"], [], None):                                        # a model: the list, and a list that is lost
            entry = {"folder": pump, "kind": "pump"} if write is None else {"folder": pump, "kind": "pump", "write": write}
            strict = session(["Administrator"], [entry], model=True)
            self.assertEqual(ns["pulse"](strict, pump, "trigger"), "Refused: trigger is read only on this device")
            self.assertFalse(ns["device_read"](strict, pump, ["trigger"])["writable"]["trigger"])
        self.assertEqual(len([c for c in calls if c[0] == "write"]), 2)

    def test_an_answer_of_the_gateway_that_is_no_quality(self):
        admin = session(["Administrator"], [{"folder": SQ}])
        for answer, text in ((None, "no answer"), ([], "no answer"), ([None], "None"), (["Bad_Failure"], "Bad_Failure")):
            ns, _ = hmi_ns(seq_tags(trigger=False))
            ns["system"].tag.writeBlocking = staticmethod(lambda paths, values, a=answer: a)
            self.assertEqual(ns["pulse"](admin, SQ, "trigger"), "Refused: the gateway did not write trigger (%s)" % text)
        # `writeBlocking` answers a quality and does not raise (GF-47, GF-49); were it to raise, the
        # exception leaves the function, and no message is made up for a write whose fate is not known
        ns, _ = hmi_ns(seq_tags(trigger=False))

        def raises(paths, values):
            raise RuntimeError("the gateway")
        ns["system"].tag.writeBlocking = staticmethod(raises)
        with self.assertRaises(RuntimeError):
            ns["pulse"](admin, SQ, "trigger")

    def test_pulse_writes_true_and_nothing_else(self):
        entry = {"folder": SQ, "write": ["trigger"]}
        tags = seq_tags(step=1, stepText="Standby", trigger=False, fault=False)
        before = dict(tags)
        ns, calls = hmi_ns(tags)
        self.assertEqual(ns["pulse"](session(["Administrator"], [entry], model=True), SQ, "trigger"), "")
        self.assertEqual(calls, [("write", [f"{SQ}/trigger"], [True])])           # one write, of true
        self.assertIs(calls[0][2][0], True)                                      # the Boolean itself, not a 1
        self.assertEqual({k: v for k, v in tags.items() if v != before[k]}, {f"{SQ}/trigger": True})
        # the function never returns the member to false: a second pulse writes true again
        self.assertEqual(ns["pulse"](session(["Administrator"], [entry], model=True), SQ, "trigger"), "")
        self.assertEqual([c[2] for c in calls], [[True], [True]])
        # a project built without a device model: the rule of the write path alone
        ns, calls = hmi_ns(seq_tags(trigger=False))
        self.assertEqual(ns["pulse"](session(["Administrator"], [{"folder": SQ}]), SQ, "trigger"), "")
        self.assertEqual(calls, [("write", [f"{SQ}/trigger"], [True])])
        # a write the gateway does not make is answered, as every checked write answers it
        ns, calls = hmi_ns(seq_tags(trigger=False), refuse=[f"{SQ}/trigger"])
        self.assertEqual(ns["pulse"](session(["Administrator"], [{"folder": SQ}]), SQ, "trigger"),
                         "Refused: the gateway did not write trigger (Bad_ReadOnly)")

    def test_the_path_and_its_permission(self):
        from hmi import framework, gates, scripts
        ns, _ = hmi_ns({})
        self.assertEqual((ns["PULSE_PATH"], ns["FUNCTION_MEMBERS"]["W18"][0]), ("W18", "trigger"))   # and COB-158's
        self.assertEqual(ns["PERMITTED"]["W18"], ["Administrator"])
        self.assertIs(ns["permissions"](session(["Administrator"]))["W18"], True)
        self.assertIs(ns["permissions"](session(None))["W18"], False)
        self.assertIs(framework.CAN_DEFAULT["W18"], False)
        self.assertEqual(ns["_path_of"]("trigger"), "W18")
        self.assertNotIn("trigger", [m for ms in scripts.constant("PATH_MEMBERS").values() for m in ms])
        self.assertEqual((framework.PULSE_PATH, framework.PULSE_MEMBERS, screen.PULSE_MEMBERS), ("W18", tuple(scripts.constant("FUNCTION_MEMBERS")["W18"]),
                          tuple(scripts.constant("FUNCTION_MEMBERS")["W18"])))   # COB-158 added the generator's and the asm sequence's
        self.assertEqual(gates.CALL_PATH["cadre.hmi.pulse("], "W18")
        self.assertIn("cadre.hmi.pulse(", gates.CHECKED_CALLS)
        self.assertTrue(gates.CHECKED_NAMES.search("x = cadre.hmi.pulse(s, d, 'trigger')"))
        # every member default is typed, so `device_read` answers no null for a member of any faceplate
        for kind, members in framework.FACEPLATE_READS.items():
            self.assertEqual([m for m in members if m not in ns["MEMBER_DEFAULTS"]], [], kind)
        self.assertEqual({m: type(ns["MEMBER_DEFAULTS"][m]) for m in SEQ},
                         {"step": int, "stepText": str, "trigger": bool, "fault": bool})


class PulseModelTests(unittest.TestCase):
    """The device model's `pulse` and `caption`: the schema, the device index, gate G7 devices on the
    fixture and on each kind of broken model, and the fixture's expression model of the sequence."""

    def setUp(self):
        self.gate = DeviceGateTests()
        self.gate.setUp()
        self.desc, self.model, self.tags = self.gate.base.desc, self.gate.base.model, self.gate.base.tags

    def test_the_schema(self):
        self.assertEqual(screen.devices_schema_errors(self.model, "m"), [])
        sq = next(d for d in self.model["devices"] if d["id"] == "SQ1")
        self.assertEqual(sq["members"]["trigger"], {"type": "Boolean", "access": "write", "pulse": True, "caption": "Start cycle"})
        for change, bad in (({"caption": ""}, True), ({"pulse": "yes"}, True), ({"caption": 3}, True),
                            ({"pulsed": True}, True), ({"pulse": False}, False), ({"caption": "Go"}, False),
                            # a caption is one line of 1 to 32 characters with no space at either end
                            ({"caption": "   "}, True), ({"caption": " Go"}, True), ({"caption": "Go "}, True),
                            ({"caption": "Start\ncycle"}, True), ({"caption": "Go\tnow"}, True),
                            ({"caption": "x" * 33}, True), ({"caption": "x" * 300}, True),
                            ({"caption": "x" * 32}, False), ({"caption": "G"}, False),
                            ({"caption": "Start the cleaning cycle"}, False)):
            model = copy.deepcopy(self.model)
            next(d for d in model["devices"] if d["id"] == "SQ1")["members"]["trigger"].update(change)
            self.assertEqual(bool(screen.devices_schema_errors(model, "m")), bad, change)
        from hmi import gates
        caption = json.loads((ROOT / "schemas/devices.schema.json").read_text(encoding="utf-8"))["$defs"]["member"]["properties"]["caption"]
        self.assertEqual((caption["minLength"], caption["maxLength"]), (1, gates.CAPTION_MAX))   # one bound, stated twice

    def test_the_device_index_carries_the_captions(self):
        idx = {d["folder"].split("/")[-1]: d for d in screen.device_index([self.desc], self.model)}
        self.assertEqual(idx["SQ1"], {
            "folder": f"{PILOT}/SQ1", "kind": "sequence", "title": "FLT-1", "label": "Self cleaning filter", "unit": "",
            "sources": ["prov:default:/tag:cadre_hmi_pilot/src/SQ1_FLT:/alm:*"], "write": ["trigger"],
            "members": ["fault", "step", "stepText", "trigger"],
            "pulses": [{"member": "trigger", "caption": "Start cycle"}]})
        self.assertEqual([k for k, d in idx.items() if "pulses" in d], ["SQ1"])   # only a device with a pulse member
        lean = copy.deepcopy(self.model)
        del next(d for d in lean["devices"] if d["id"] == "SQ1")["members"]["trigger"]["caption"]
        entry = next(d for d in screen.device_index([self.desc], lean) if d["folder"].endswith("/SQ1"))
        self.assertEqual(entry["pulses"], [{"member": "trigger", "caption": "trigger"}])   # the member's name
        self.assertNotIn("pulses", screen.device_index([self.desc])[-2])          # no model: no list
        # the index a build writes is what `device_read` and `pulse` meet
        child, _ = screen.build_child("cadre_hmi_t", [self.desc], "T", devices=self.model)
        screen.RENDER["target"] = "stock"
        sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])["custom"]
        d = f"{PILOT}/SQ1"
        ns, calls = hmi_ns({f"{d}/{m}": v for m, v in (("step", 1), ("stepText", "Standby"), ("trigger", False), ("fault", False))})
        s = session(["Administrator"], sp["devices"], sp["trends"], model=sp["deviceModel"])
        got = ns["device_read"](s, d, SEQ)
        self.assertEqual((got["pulses"], got["write"]["trigger"], got["writable"]["fault"]), ({"trigger": "Start cycle"}, True, False))
        self.assertEqual(ns["trended"](s, d, ["step"]), {"step": True})
        self.assertEqual(ns["pulse"](s, d, "trigger"), "")
        self.assertEqual([c for c in calls if c[0] == "write"], [("write", [f"{d}/trigger"], [True])])
        self.assertEqual(ns["device_sources"](s, d), ["prov:default:/tag:cadre_hmi_pilot/src/SQ1_FLT:/alm:*"])
        self.assertEqual(ns["pulse"](s, f"{PILOT}/P2", "trigger"), "Refused: this device has no trigger")

    def test_the_gate_passes_the_fixture_and_catches_each_break(self):
        ok = self.gate.run_gate(lambda d, s, f: None)
        self.assertEqual((ok["ok"], ok["problems"], ok["warnings"], ok["devices"]), (True, [], [], 8))
        fails, passes = self.gate.fails, lambda change, **kw: self.assertEqual(self.gate.run_gate(change, **kw)["problems"], [])

        def tag(folder, name):
            return next(t for t in folder["tags"] if t["name"] == name)
        trig = lambda d: d["SQ1"]["members"]["trigger"]
        # a pulse member is Boolean, written, and a pulse member of its kind
        fails(lambda d, s, f: (trig(d).update(type="Int4"), tag(f["SQ1"], "trigger").update(dataType="Int4")),
              "SQ1: pulse member 'trigger' is Int4; a pulse is Boolean")
        fails(lambda d, s, f: trig(d).update(access="read"), "SQ1: pulse member 'trigger' is marked read only; a pulse is written")
        fails(lambda d, s, f: d["P2"]["members"]["cmd"].update(pulse=True),
              "P2: member 'cmd' is marked a pulse; kind 'pump' has no pulse member of that name")
        fails(lambda d, s, f: d["SQ1"]["members"]["fault"].update(pulse=True, access="write"),
              "SQ1: member 'fault' is marked a pulse; kind 'sequence' has no pulse member of that name", tags=None)
        # a caption belongs to a pulse member, and is no tab's label
        fails(lambda d, s, f: d["SQ1"]["members"]["fault"].update(caption="Reset"),
              "SQ1: member 'fault' carries a caption and is not marked a pulse")
        fails(lambda d, s, f: trig(d).pop("pulse"), "SQ1: member 'trigger' carries a caption and is not marked a pulse")
        for caption in ("Trend", "alarms", " Status ", "Alarms (2)", "Maintenance"):
            fails(lambda d, s, f: trig(d).update(caption=caption), "is the label of a faceplate tab")
        passes(lambda d, s, f: trig(d).update(caption="Start trend"))
        # a caption is one line of printing text that the button holds: the gate states it on its own,
        # for a model that reaches it without the schema
        for caption, text in (("   ", "is blank"), ("", "is blank"), (7, "is blank"),
                              ("Start\ncycle", "holds a line break or another character that does not print"),
                              ("Go\tnow", "holds a line break"), ("Go\x07", "holds a line break"),
                              (" Go", "begins or ends with a space"), ("Go ", "begins or ends with a space"),
                              ("x" * 33, "is 33 characters long, over the 32 a button holds"),
                              ("x" * 300, "is 300 characters long")):
            res = fails(lambda d, s, f: trig(d).update(caption=caption), "SQ1: the caption ")
            self.assertTrue(len(res["problems"]) == 1 and text in res["problems"][0], (caption, res["problems"]))
            self.assertLess(len(res["problems"][0]), 200)                        # a long caption is not repeated whole
        for caption in ("x" * 32, "G", "Start the cleaning cycle", "Rückspülung starten"):
            passes(lambda d, s, f: trig(d).update(caption=caption))
        # a pulse member belongs to a kind that has one: a pump's folder may carry no `trigger` the model marks
        fails(lambda d, s, f: d["P2"]["members"].update(trigger={"type": "Boolean", "access": "write", "pulse": True}),
              "P2: member 'trigger' is marked a pulse; kind 'pump' has no pulse member of that name", tags=None)
        fails(lambda d, s, f: d["P2"]["members"].update(trigger={"type": "Boolean", "access": "write"}),
              "P2: member 'trigger' is not a member the library knows for kind 'pump'", tags=None)
        # a writable pulse member is marked a pulse: its faceplate draws its button
        fails(lambda d, s, f: (trig(d).pop("pulse"), trig(d).pop("caption")),
              "SQ1: member 'trigger' is a pulse member of kind 'sequence' and is marked writable without \"pulse\": true")
        # a trigger the source only reports, a pulse without a caption, a narrower integer: each is a good model
        passes(lambda d, s, f: (trig(d).pop("pulse"), trig(d).pop("caption"), trig(d).update(access="read")))
        passes(lambda d, s, f: trig(d).pop("caption"))
        passes(lambda d, s, f: (d["SQ1"]["members"]["step"].update(type="Int2"), tag(f["SQ1"], "step").update(dataType="Int2")))
        # the members and their types
        fails(lambda d, s, f: d["SQ1"]["members"]["step"].update(type="Float8"), "SQ1: member 'step' is Float8; the library reads it as Int4")
        fails(lambda d, s, f: d["SQ1"]["members"]["stepText"].update(type="Int4"), "the library reads it as String")
        fails(lambda d, s, f: d["SQ1"]["members"].update(state={"type": "Boolean", "access": "read"}),
              "SQ1: member 'state' is not a member the library knows for kind 'sequence'", tags=None)
        fails(lambda d, s, f: d["SQ1"]["members"]["step"].update(access="write"),
              "SQ1: member 'step' is marked writable and no write path writes it")
        fails(lambda d, s, f: d["SQ1"].update(trend=["stepText", "value"]), "SQ1: trend names 'value'")
        # a pulse member that is an expression tag would refuse the write (GF-49)
        fails(lambda d, s, f: tag(f["SQ1"], "trigger").update(valueSource="expr", expression="false"),
              "SQ1: member 'trigger' is marked writable and is an expression tag")
        fails(lambda d, s, f: f["SQ1"]["tags"].remove(tag(f["SQ1"], "trigger")), "SQ1: the tag model lacks member 'trigger'")
        # the block on the page against the model
        fails(lambda d, s, f: (d["SQ1"]["members"].pop("stepText"), f["SQ1"]["tags"].remove(tag(f["SQ1"], "stepText"))),
              "SQ1: 'text' is bound to 'SQ1/stepText'; the model lists no member 'stepText' for SQ1")

        def no_step(d, s, f):
            d["SQ1"]["members"].pop("step")
            d["SQ1"].pop("trend")
            s["SQ1"]["bind"].pop("step")
        fails(no_step, "SQ1: hasStep is true; the model lists no member 'step' for SQ1", tags=None)
        passes(lambda d, s, f: (no_step(d, s, f), s["SQ1"]["params"].pop("hasStep")), tags=None)
        fails(lambda d, s, f: d["SQ1"].update(kind="indicator", members={"state": {"type": "Boolean", "access": "read"}}, trend=[]),
              "SQ1: opens Faceplate/Sequence (kind 'sequence'); the device's kind 'indicator' opens Faceplate/Input", tags=None)
        # a helper tag of the simulation (`started`) is no faceplate member: the gate leaves it alone
        self.assertIn("started", [t["name"] for t in next(f for f in self.tags["tags"] if f["name"] == "SQ1")["tags"]])

    def test_the_fixture_model_advances_the_step_after_its_trigger(self):
        """The fixture stands in for the plant: a value-changed event script on the trigger stamps
        `started` and returns the trigger to false (measured on the gateway, GF-57), and the step
        reads the time since the stamp. The expressions are evaluated here against a clock the test
        moves; the event script is read as text and its effect is applied by hand. The functions are
        those the Ignition-Wiki attests: `if`, `coalesce`, `case`, `toMillis`, `now`."""
        folder = next(f for f in self.tags["tags"] if f["name"] == "SQ1")
        tags = {t["name"]: t for t in folder["tags"]}
        self.assertEqual({n: t["valueSource"] for n, t in tags.items()},
                         {"trigger": "memory", "started": "memory", "step": "expr", "stepText": "expr",
                          "fault": "reference"})
        self.assertEqual((tags["step"]["dataType"], tags["stepText"]["dataType"], tags["step"].get("historyEnabled")),
                         ("Int4", "String", True))
        self.assertEqual((tags["started"]["dataType"], tags["started"]["value"]), ("Int8", 0))
        self.assertEqual(tags["fault"]["sourceTagPath"], "[default]cadre_hmi_pilot/src/SQ1_FLT")
        self.assertNotIn("eventScripts", tags["started"])                        # only the pulse member carries a script
        (event,) = tags["trigger"]["eventScripts"]
        self.assertEqual(event["eventid"], "valueChanged")
        script = event["script"]
        self.assertIn("if currentValue.value and not initialChange:", script)     # a pulse, never the return or a restart
        self.assertEqual(re.findall(r"'(\[default\][\w/]+)'", script),
                         ["[default]cadre_hmi_pilot/SQ1/started", "[default]cadre_hmi_pilot/SQ1/trigger"])
        self.assertIn("[system.date.toMillis(system.date.now()), False])", script.replace("\n\t\t\t", ""))
        self.assertEqual(script.count("system.tag.writeBlocking"), 1)             # one write, of its own two tags

        clock = {"ms": 1_000_000}

        def python(expression):
            e = re.sub(r"\{\[\.\]([\w/]+)\}", r'T["\1"]', expression)
            e = re.sub(r"\{\[default\]cadre_hmi_pilot/([\w/]+)\}", r'T["/\1"]', e)
            self.assertNotIn("{", e, expression)                                 # every reference is one of the two forms
            e = re.sub(r"\bif\(", "if_(", re.sub(r"\bcase\(", "case_(", e))
            e = re.sub(r"(?<![<>=!])=(?!=)", "==", e)                            # the expression language's equality
            return re.sub(r"\bfalse\b", "False", re.sub(r"\btrue\b", "True", e))

        def case_(value, *rest):
            return next((r for k, r in zip(rest[:-1:2], rest[1:-1:2]) if k == value), rest[-1])
        scope = {"if_": lambda c, a, b: a if c else b, "case_": case_, "toMillis": lambda t: t,
                 "now": lambda _rate=0: clock["ms"],
                 "coalesce": lambda *a: next((x for x in a if x is not None), None)}
        T = {"trigger": False, "started": None, "step": None, "stepText": None, "/src/SQ1_FLT": False}
        for name in ("step", "stepText"):                                        # every cross reference has a default (GF-19)
            self.assertEqual(tags[name]["expression"].count("{"), tags[name]["expression"].count("coalesce("), name)

        def scan(seconds=1):
            seen = []
            for _ in range(seconds):
                clock["ms"] += 1000
                for name in ("step", "stepText"):
                    T[name] = eval(python(tags[name]["expression"]), dict(scope, T=T))
                seen.append((T["step"], T["stepText"]))
            return seen

        def pulse():                                                             # `cadre.hmi.pulse` writes true, then the script
            T["started"], T["trigger"] = clock["ms"], False

        self.assertEqual(scan(3), [(1, "Standby")] * 3)                          # from a null start: no null spreads
        T["started"] = 0
        self.assertEqual(scan(2), [(1, "Standby")] * 2)                          # as imported: never started
        pulse()
        self.assertEqual(scan(12), [(2, "Drive Out")] * 4 + [(3, "Drive Back")] * 5 + [(1, "Standby")] * 3)
        self.assertIs(T["trigger"], False)                                       # returned, so a pulse can come again
        pulse()
        self.assertEqual(scan(1), [(2, "Drive Out")])                            # and the next pulse starts a cycle
        T["/src/SQ1_FLT"] = True
        self.assertEqual(scan(1), [(4, "Fault")])
        T["/src/SQ1_FLT"] = False
        self.assertEqual(scan(1), [(2, "Drive Out")])

    def test_the_example_of_the_wiki_passes_the_gate(self):
        """The device model shown on wiki page 08 section 3.1 is one a tool may copy: it validates and
        passes gate G7 devices against the profile."""
        from hmi import gates, library_profile
        page = (ROOT / "wiki/08-generation-and-validation.md").read_text(encoding="utf-8")
        model = json.loads(re.search(r"```json\n(\{\"schema\": \"cadre-hmi-devices/1\".*?)\n```", page, re.S).group(1))
        self.assertEqual(screen.devices_schema_errors(model, "wiki/08"), [])
        res = gates.g7_devices(model, library_profile.build(screen.load_contracts()), [])
        self.assertEqual((res["ok"], res["problems"], res["warnings"], res["devices"]), (True, [], [], 2))
        self.assertEqual([d["kind"] for d in model["devices"]], ["pump", "sequence"])
        self.assertTrue(model["devices"][1]["members"]["trigger"]["pulse"])

    def test_the_sweep_expects_the_sequence_tabs(self):
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import faceplates
        exp = faceplates.device_expectations([self.desc], self.model)["FLT-1"]
        self.assertEqual((exp["tabs"], exp["trend_open"], exp["sources"]),
                         (["Status", "Trend", "Alarms"], False, ["prov:default:/tag:cadre_hmi_pilot/src/SQ1_FLT:/alm:*"]))
        model = copy.deepcopy(self.model)
        next(d for d in model["devices"] if d["id"] == "SQ1").pop("trend")       # the tag model then decides the tab
        open_ = faceplates.device_expectations([self.desc], model)["FLT-1"]
        self.assertEqual((open_["tabs"], open_["trend_open"]), (["Status", "Alarms"], True))
        self.assertEqual(faceplates.tab_faults("FLT-1", ["Status", "Trend", "Alarms"], open_), [])
        self.assertEqual(len(faceplates.tab_faults("FLT-1", ["Status", "Alarms"], exp)), 1)
        self.assertIn("FLT-1", faceplates.expected_devices(self.desc))
        self.assertIsNone(faceplates.TAB.match("Start cycle"))                   # the pulse button is no tab to the sweep


class ProfileSizeTests(unittest.TestCase):
    """What the library profile states of the sequence and the pulse, and the sizes a layouter in
    another repository places symbols from: each equals the built view, and each embed box equals
    `screen.symbol_box`."""

    def setUp(self):
        from hmi import library_profile, parent as par
        self.prj, self.contracts = par.build_parent()
        self.prof = library_profile.build(self.contracts)

    def view(self, path):
        return json.loads(self.prj.files[f"com.inductiveautomation.perspective/views/{path}/view.json"])

    def test_the_sequence_and_the_pulse(self):
        prof = self.prof
        self.assertEqual(json.loads((ROOT / "library/profile.json").read_text(encoding="utf-8")), prof)   # current
        seq = prof["kinds"]["sequence"]
        self.assertEqual((seq["view"], seq["faceplate"], seq["flow"], seq["gate"], seq["anchor"], seq["trend"]),
                         ("Instrument/Sequence", "Faceplate/Sequence", "pass", None, "box", "step"))
        self.assertEqual(seq["bind"], {"step": "step", "text": "stepText"})
        self.assertEqual(seq["members"], {"fault": {"type": "Boolean", "required": False},
                                          "step": {"type": "Int4", "required": False},
                                          "stepText": {"type": "String", "required": False},
                                          "trigger": {"type": "Boolean", "required": False},
                                          "alarmAck": {"type": "Boolean", "required": False},   # F049
                                          **{m: {"type": "Boolean", "required": False}   # COB-158
                                             for m in ("inService", "enabled", "normal", "cmdInService",
                                                       "cmdOutOfService", "cmdEnable", "cmdDisable")}})
        self.assertEqual((seq["pulses"], seq["interlocks"], seq["maintenance"], seq["module"]),
                         (["trigger", "cmdInService", "cmdOutOfService", "cmdEnable", "cmdDisable"], True, False, None))
        self.assertEqual((seq["size"], seq["symbolSize"], seq["embedBox"]), ([144, 72], None, None))
        self.assertEqual(seq["params"], sorted(self.contracts["Instrument/Sequence"]["params"]))
        dk = prof["deviceKinds"]["sequence"]
        self.assertEqual((dk["faceplate"], dk["pulses"], dk["trend"], dk["bind"], dk["members"]),
                         ("Faceplate/Sequence", seq["pulses"], ["step"], seq["bind"], seq["members"]))
        for table in (prof["kinds"], prof["deviceKinds"]):                       # every kind states its pulse members
            self.assertEqual({k: v["pulses"] for k, v in table.items() if v["pulses"]},
                             {"sequence": seq["pulses"], "generator": ["cmdStart", "cmdStop", "cmdReset", "cmdServiceDone"]})
            self.assertTrue(all(isinstance(v["pulses"], list) for v in table.values()))
        self.assertEqual(prof["faceplates"]["Faceplate/Sequence"]["tabs"], ["status", "trend", "alarms"])
        from hmi import scripts
        seq_pulses_w18 = lambda: scripts.constant("FUNCTION_MEMBERS")["W18"]
        self.assertEqual(prof["writePaths"]["W18"],
                         {"members": seq_pulses_w18(), "role": "Administrator",
                          "what": "pulse command", "function": "pulse"})
        self.assertIn("pulse-command", prof["functions"])
        # a pulse member is Boolean in the library, and W18 is the path that writes it
        for kind, v in prof["deviceKinds"].items():
            for m in v["pulses"]:
                self.assertEqual(v["members"][m]["type"], "Boolean", (kind, m))
                self.assertIn(m, prof["writePaths"]["W18"]["members"])

    def test_sizes_are_those_of_the_built_views(self):
        from hmi import framework, library
        prof, positions = self.prof, tuple(screen.READOUT_EXTENT)
        self.assertEqual(sorted(positions), ["bottom", "left", "none", "right", "top"])
        automation = sorted(k.lower() for k in library.DEVICE_KINDS)
        seen = []
        for kind, k in prof["kinds"].items():
            size = self.view(k["view"])["props"]["defaultSize"]
            self.assertEqual(k["size"], [size["width"], size["height"]], kind)   # the built view's default size
            c = self.contracts[k["view"]]
            self.assertEqual((k["anchor"], k["symbolSize"]), (c.get("anchor"), c.get("symbolSize")), kind)
            if kind not in automation:                                           # its box is used as the descriptor gives it
                self.assertEqual((k["embedBox"], k["symbolSize"]), (None, None), kind)
                sym = {"kind": kind, "x": 7, "y": 9, "w": k["size"][0], "h": k["size"][1], "params": {}}
                self.assertEqual(screen.symbol_box(sym, c), (7, 9, k["size"][0], k["size"][1]), kind)
                continue
            seen.append(kind)
            self.assertEqual((k["symbolSize"], k["size"], sorted(k["embedBox"])), (48, [48, 48], sorted(positions)), kind)
            for pos in positions:
                at = screen.symbol_box({"kind": kind, "x": 0, "y": 0, "w": 48, "h": 48, "params": {"readoutPosition": pos}}, c)
                self.assertEqual(k["embedBox"][pos], list(at), (kind, pos))
                # an offset from the 48 px symbol box, wherever the symbol stands
                x, y, w, h = screen.symbol_box({"kind": kind, "x": 300, "y": 160, "w": 48, "h": 48,
                                                "params": {"readoutPosition": pos}}, c)
                dx, dy, bw, bh = k["embedBox"][pos]
                self.assertEqual((x, y, w, h), (300 + dx, 160 + dy, bw, bh), (kind, pos))
            self.assertEqual(k["embedBox"]["none"], [0, 0, 48, 48], kind)
        self.assertEqual(sorted(seen), automation)                               # every automation kind, and no other
        self.assertEqual(sorted(k for k, v in prof["kinds"].items() if v["embedBox"] is None),
                         ["controller", "instrument-field", "readout", "sequence", "tank"])
        # the frame: the docks of the page configuration, and a canvas the fixture's page fits
        docks = framework.shared_docks()
        self.assertEqual((prof["frame"]["topDock"], prof["frame"]["faceplateDock"]),
                         (docks["top"][0]["size"], docks["right"][0]["size"]))
        self.assertEqual(sorted(prof["frame"]), ["cardsCanvas", "diagramCanvas", "faceplateDock", "topDock", "viewport"])
        page = fixture("pilot-supply.json")["screen"]
        self.assertEqual([page["width"], page["height"]], prof["frame"]["diagramCanvas"])

    def test_the_profile_file_is_replaced_whole(self):
        import os
        from hmi import library_profile
        text = json.dumps(self.prof, indent=1, sort_keys=True) + "\n"
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "sub" / "profile.json"
            for _ in range(2):                                                   # a first write, and one over a file
                self.assertEqual(library_profile.write(self.contracts, [out]), [out])
                self.assertEqual(out.read_bytes(), text.encode("utf-8"))
                self.assertEqual(sorted(p.name for p in out.parent.iterdir()), ["profile.json"])   # no file left beside it
            # written beside the file and moved over it: a reader never meets half a profile
            seen = []
            real = os.replace

            def watched(src, dst):
                seen.append((Path(src).name, Path(dst).name, json.loads(Path(dst).read_text(encoding="utf-8")) == self.prof,
                             json.loads(Path(src).read_text(encoding="utf-8")) == self.prof))
                return real(src, dst)
            os.replace = watched
            try:
                library_profile.write(self.contracts, [out])
            finally:
                os.replace = real
            self.assertEqual(seen, [("profile.json.tmp", "profile.json", True, True)])
            # a replacement the system refuses every time (a reader holds the file): written in place
            def refused(src, dst):
                raise PermissionError("held")
            os.replace, pause = refused, library_profile.time.sleep
            library_profile.time.sleep = lambda s: None
            try:
                library_profile.write(self.contracts, [out])
            finally:
                os.replace, library_profile.time.sleep = real, pause
            self.assertEqual(out.read_bytes(), text.encode("utf-8"))
            self.assertEqual(sorted(p.name for p in out.parent.iterdir()), ["profile.json"])


def profile_embed(prof, s):
    """The embed box of a symbol as a layouter computes it from the library profile alone, with nothing
    beside the symbol: the descriptor's box for a box kind; for a kind that `grows` (a readout) that
    box, grown about its centre to the size its flags need (`sizes`: a parameter the symbol does not
    give meets no `when`) and to the width of the identifier it shows; for an automation symbol the
    48 px symbol box moved and grown by `embedBox`, and grown across by what the identifier needs
    beyond the default readout."""
    k = prof["kinds"][s["kind"]]
    p = s.get("params", {})
    if k["embedBox"] is None:
        x, y, w, h = s["x"], s["y"], s["w"], s["h"]
        if not k["grows"]:
            return [x, y, w, h]
        need = next((e["size"] for e in k["sizes"] if all(p.get(f) == v for f, v in e["when"].items())), None)
        w2, h2 = (max(w, need[0]), max(h, need[1])) if need else (w, h)
        ident, text = k["identifier"], prof["text"]
        if p.get(ident["param"]) and p.get(ident["flag"]):
            chars = min(len(p[ident["param"]]), text["identifierChars"])
            w2 = max(w2, chars * text["fonts"][ident["font"]]["charWidth"] + ident["pad"])
        return [x + (w - w2) / 2, y + (h - h2) / 2, w2, h2]
    pos = p.get("readoutPosition", "bottom")
    dx, dy, w, h = k["embedBox"][pos]
    tag = p.get("tag", "")
    if pos != "none" and tag and p.get("hasTag") is not False:
        ident, text = k["identifier"], prof["text"]
        need = min(len(tag), text["identifierChars"]) * text["fonts"][ident["font"]]["charWidth"] + ident["pad"]
        if pos in ("bottom", "top"):               # the readout is centred on the symbol
            grown = max(w, need)
            dx, w = dx - (grown - w) / 2, grown
        else:                                      # the readout lies beside the symbol
            grown = 48 + max(w - 48, need)
            dx, w = (dx - (grown - w) if pos == "left" else dx), grown
    return [s["x"] + dx, s["y"] + dy, w, h]


class FirstRenderTests(unittest.TestCase):
    """What the first page built from a plant's data asked of the library (2026-10-11): a static tank
    that shows no capacity nobody states and whose pipes meet its tile, identifiers of 16 characters
    read from their first character, the true sizes of the blocks in the library profile, a cards page
    whose rows are as high as their content, and gate warnings a tool can read."""

    @classmethod
    def setUpClass(cls):
        from hmi import library_profile, parent as par
        cls.prj, cls.contracts = par.build_parent()
        cls.prof = library_profile.build(cls.contracts)

    def view(self, path):
        return json.loads(self.prj.files[f"com.inductiveautomation.perspective/views/{path}/view.json"])

    def embed(self, sym, render="stock"):
        screen.RENDER["target"] = render
        try:
            rep = screen.Report()
            node, _c, _cfg = screen.embed_symbol(sym, self.contracts, "[default]t", rep, toolbar=True)
            return node, rep.errors
        finally:
            screen.RENDER["target"] = "stock"

    # ---- 0. every parameter stated, a bound one left to its binding --------------------------
    def test_an_embedded_symbol_states_every_parameter_it_does_not_bind(self):
        # GF-60: after a load by URL an embedded view keeps, for each parameter its embedding leaves out, the
        # value of the instance that stood at the same place before; so no unbound parameter is left out.
        # GF-61: a default stated beside a binding shows instead of the bound value on the second of two
        # symbols of the same view at the same place of two displays; so a bound parameter is left out.
        def bound(node):
            return {k[len("props.params."):] for k in (node.get("propConfig") or {}) if k.startswith("props.params.")}
        for kind, view in (("instrument-field", "Instrument/Field"), ("pump", "Automation/Pump"),
                           ("valve", "Automation/Valve"), ("tank", "Automation/Tank")):
            contract = self.contracts[view]["params"]
            node, errors = self.embed({"id": "S", "kind": kind, "x": 0, "y": 0, "w": 96, "h": 96,
                                       "params": {"tag": "S-1"}})
            self.assertEqual((kind, errors), (kind, []))
            self.assertEqual((kind, sorted(node["props"]["params"])), (kind, sorted(set(contract) - bound(node))))
            for name, default in contract.items():
                if name != "tag" and name not in bound(node):
                    self.assertEqual((kind, name, node["props"]["params"][name]), (kind, name, default))
        # the toolbar binds the identifier and the status row of an automation symbol: neither is stated
        node, errors = self.embed({"id": "P", "kind": "pump", "x": 0, "y": 0, "w": 48, "h": 48,
                                   "params": {"tag": "P-1"}})
        self.assertEqual((bound(node), bound(node) & set(node["props"]["params"]), errors),
                         ({"hasTag", "showStatus"}, set(), []))
        # also where the descriptor states them: its own value lives in the binding
        node, errors = self.embed({"id": "P", "kind": "pump", "x": 0, "y": 0, "w": 48, "h": 48,
                                   "params": {"tag": "P-1", "hasTag": True, "showStatus": False}})
        self.assertEqual((bound(node) & set(node["props"]["params"]), errors), (set(), []))
        self.assertEqual(node["propConfig"]["props.params.showStatus"]["binding"]["config"]["expression"],
                         "{view.custom.showReadout} && false")
        # a member the descriptor binds is its binding alone, the state gate of a symbol among them
        node, errors = self.embed({"id": "L", "kind": "indicator", "x": 0, "y": 0, "w": 48, "h": 48,
                                   "params": {"tag": "L-1"}, "bind": {"on": "L1/state"}})
        self.assertEqual(("on" in bound(node), "on" in node["props"]["params"], errors), (True, False, []))
        node, errors = self.embed({"id": "F", "kind": "instrument-field", "x": 0, "y": 0, "w": 96, "h": 48,
                                   "params": {"tag": "H-1"}, "bind": {"value": "H1/value"}})
        self.assertEqual((bound(node), "value" in node["props"]["params"], node["props"]["params"]["setpoint"],
                          errors), ({"value", "hasTag"}, False, self.contracts["Instrument/Field"]["params"]["setpoint"], []))
        # what the descriptor states wins, also beside a binding, and a label of the symbol is the device's label
        node, errors = self.embed({"id": "F", "kind": "instrument-field", "x": 0, "y": 0, "w": 96, "h": 48,
                                   "label": "Start hour", "params": {"tag": "H-1", "unit": "h"}})
        got = node["props"]["params"]
        self.assertEqual((got["unit"], got["deviceLabel"], errors), ("h", "Start hour", []))
        node, errors = self.embed({"id": "G", "kind": "instrument-field", "x": 0, "y": 0, "w": 96, "h": 48,
                                   "params": {"tag": "H-2"}})
        got = node["props"]["params"]
        self.assertEqual((got["unit"], got["deviceLabel"], got["deviceId"], errors), ("", "", "", []))

    # ---- 1. the static tank -------------------------------------------------------------
    def test_a_static_tank_draws_no_capacity_nobody_states(self):
        from hmi import library
        tank = self.contracts["Automation/Tank"]
        self.assertIs(tank["params"]["hasCapacity"], True)                       # the default: as before
        nodes = view_nodes(self.view("Automation/Tank"))
        self.assertEqual(nodes["StaticValue"]["propConfig"]["meta.visible"]["binding"]["config"]["expression"],
                         "{view.params.static} && {view.params.hasCapacity}")
        self.assertEqual(nodes["StaticTag"]["propConfig"]["meta.visible"]["binding"]["config"]["expression"],
                         "{view.params.static} && {view.params.hasTag}")         # the identifier stays, but for ID-tag
        at = nodes["StaticTile"]["position"]
        self.assertEqual((at["x"], at["y"], at["width"], at["height"]), library.STATIC_TILE)
        box = {"id": "T", "kind": "tank", "x": 0, "y": 0, "w": 168, "h": 216}
        node, errors = self.embed(dict(box, params={"static": True, "tag": "Break tank"}))
        self.assertEqual((node["props"]["params"]["hasCapacity"], errors), (False, []))
        # a capacity the descriptor states, as a parameter or as a binding, is drawn as before: the contract's
        # default, which the embedding states like every other parameter (GF-60)
        node, errors = self.embed(dict(box, params={"static": True, "max": 450, "unit": "m3"}))
        self.assertEqual((node["props"]["params"]["hasCapacity"], errors), (True, []))
        node, errors = self.embed(dict(box, params={"static": True}, bind={"max": "T/capacity"}))
        self.assertEqual((node["props"]["params"]["hasCapacity"], errors), (True, []))
        node, errors = self.embed(dict(box, params={"max": 450}))                # a live tank: untouched
        self.assertEqual((node["props"]["params"]["hasCapacity"], errors), (True, []))
        node, errors = self.embed(dict(box, params={"static": True, "max": 450, "hasCapacity": False}))
        self.assertEqual((node["props"]["params"]["hasCapacity"], errors), (False, []))   # hidden on request
        # the line asked for and no capacity stated: the default would be an invented number
        _node, errors = self.embed(dict(box, params={"static": True, "hasCapacity": True}))
        self.assertEqual(len(errors), 1)
        self.assertIn("'hasCapacity' is true and the descriptor states no 'max'", errors[0])
        # the module's tank has `hasCapacity` since 0.3.0: a vessel that states no capacity is the module's tank
        # with no capacity line, and one that states its capacity prints it
        node, errors = self.embed(dict(box, params={"static": True, "tag": "Break tank"}), render="module")
        self.assertEqual((node["type"], node["props"]["hasCapacity"], errors), ("cadre.ob.tank", False, []))
        node, errors = self.embed(dict(box, params={"static": True, "max": 450, "unit": "m³"}), render="module")
        self.assertEqual((node["type"], node["props"]["hasCapacity"], errors), ("cadre.ob.tank", True, []))
        node, errors = self.embed(dict(box, params={"max": 450}), render="module")   # a live tank: the module's
        self.assertEqual((node["type"], errors), ("cadre.ob.tank", []))
        # a level in another unit is the module's tank too: it states its unit (0.3.0)
        node, errors = self.embed(dict(box, params={"max": 8200, "unit": "Lt"}), render="module")
        self.assertEqual((node["type"], node["props"]["unit"], errors), ("cadre.ob.tank", "Lt", []))
        node, errors = self.embed(dict(box, params={"max": 450}), render="module")        # none stated: the contract's
        self.assertEqual((node["type"], node["props"]["unit"], errors), ("cadre.ob.tank", "m\u00b3", []))
        # a pump with no speed is the module's pump with `hasSpeed` false; one that states none is as the library's
        pump = {"id": "P", "kind": "pump", "x": 0, "y": 0, "w": 48, "h": 48}
        node, errors = self.embed(dict(pump, params={"tag": "P-9"}), render="module")
        self.assertEqual((node["type"], node["props"]["hasSpeed"], errors), ("cadre.ob.pump", False, []))
        node, errors = self.embed(dict(pump, params={"tag": "P-9", "hasSpeed": True}), render="module")
        self.assertEqual((node["type"], node["props"]["hasSpeed"], errors), ("cadre.ob.pump", True, []))
        # the motor and the valves are the module's (COB-074); a vertical fan has no module artwork
        for kind in ("motor", "valve", "analogvalve", "fan", "filter"):
            node, errors = self.embed(dict(pump, kind=kind, params={"tag": "X-9"}), render="module")
            self.assertEqual((node["type"], errors), (screen.MODULE_KIND[kind], []), kind)
        node, errors = self.embed(dict(pump, kind="fan", params={"tag": "F-9", "vertical": True}), render="module")
        self.assertEqual((node["type"], errors), ("ia.display.view", []))
        node, errors = self.embed(dict(pump, kind="valve", params={"tag": "V-9", "variant": "double"}), render="module")
        self.assertEqual((node["type"], errors), ("ia.display.view", []))
        self.assertEqual((screen.MODULE_NEEDS, screen.MODULE_EXCEPT), (
            {"valve": {"variant": ["regular", "flat"]}, "analogvalve": {"variant": ["regular", "flat"]},
             "filter": {"variant": ["regular", "flat"]},
             "generator": {"variant": ["regular"], "activated": [False], "progress": [False],
                           "badgeControl": ["none"], "badgeInterlock": ["none"], "badgeCommandLocked": ["none"]},
             "tank": {"valueFractionDigits": [0]}, "instrument-field": {"align": ["center", "end"]}},
            {"fan": [{"vertical": True}], "filter": [{"vertical": True}], "generator": [{"picture": "genset"}],
             "instrument-field": [{"size": "enhanced", "hasSetpoint": True}]}))
        # a filter: the library's regular variant is the element's square; a vertical one stays on the library's view
        node, errors = self.embed(dict(pump, kind="filter", params={"tag": "FL-9", "variant": "regular"}), render="module")
        self.assertEqual((node["type"], node["props"]["variant"], errors), ("cadre.ob.filter", "square", []))
        node, errors = self.embed(dict(pump, kind="filter", params={"tag": "FL-9", "variant": "flat"}), render="module")
        self.assertEqual((node["type"], node["props"]["variant"], errors), ("cadre.ob.filter", "flat", []))
        node, errors = self.embed(dict(pump, kind="filter", params={"tag": "FL-9", "vertical": True}), render="module")
        self.assertEqual((node["type"], errors), ("ia.display.view", []))

    def test_a_generator_is_the_modules_indicator_unless_it_asks_for_what_the_disc_lacks(self):
        # spike T0 wrap W2: the plain generator symbol is `cadre.ob.generator`; the generator set, another variant, the
        # activated ground, a progress ring (stated or bound), a badge and the duty and out of service marks stay on the library's view
        gen = {"id": "G", "kind": "generator", "x": 0, "y": 0, "w": 48, "h": 48}
        node, errors = self.embed(dict(gen, params={"tag": "GEN-9", "picture": "symbol"}), render="module")
        self.assertEqual((node["type"], errors), ("cadre.ob.generator", []))
        # the library's own parameters the disc has no property for are not passed (gate G1)
        self.assertEqual(set(node["props"]) - set(json.loads((ROOT / "module/components.json").read_text(
            encoding="utf-8"))["cadre.ob.generator"]["props"]), set())
        for params in ({"picture": "genset"}, {"variant": "flat"}, {"activated": True}, {"progress": True},
                       {"badgeControl": "manual"}, {"badgeInterlock": "interlock"}, {"badgeDuty": True},
                       {"outOfService": True}):
            node, errors = self.embed(dict(gen, params=dict(params, tag="GEN-9")), render="module")
            self.assertEqual((node["type"], errors), ("ia.display.view", []), params)
        for bound in ("progress", "activated"):
            node, errors = self.embed(dict(gen, params={"tag": "GEN-9"}, bind={bound: "G/" + bound}), render="module")
            self.assertEqual(node["type"], "ia.display.view", bound)
        # the state binds `on`; the identifier and the status word follow the toolbar; the click opens the generator faceplate
        node, errors = self.embed(dict(gen, device="G1", label="Genset", params={"tag": "GEN-9"}, bind={"on": "G1/state"}),
                                  render="module")
        self.assertEqual(node["type"], "cadre.ob.generator")
        self.assertIn("props.on", node["propConfig"])
        # the alarm state follows the device's alarms as the other module symbols do (wiki page 13 section 11.2)
        for prop, field in (("alert", "alertAny"), ("alertFrameStatus", "level"), ("alertFrameMode", "mode")):
            self.assertIn(f".{field}}}", json.dumps(node["propConfig"][f"props.{prop}"]))
        self.assertEqual(node["custom"]["deviceKind"], "generator")
        self.assertIn("cadre.hmi.select_device", json.dumps(node["events"]))

    def test_every_module_property_the_generator_states_is_in_the_components_schema(self):
        # a property of the library's contract that the generator passes to a module component must be one the
        # component has (gate G1 refuses others), and each dropped one is a deliberate drop
        comps = json.loads((ROOT / "module/components.json").read_text(encoding="utf-8"))
        contracts = json.loads((ROOT / "library" / "contracts.json").read_text(encoding="utf-8"))
        contracts = contracts.get("views", contracts)
        for kind, ctype in screen.MODULE_KIND.items():
            c = contracts[screen.KIND_VIEW[kind]]["params"]
            have = set(comps[ctype]["props"])
            passed = {screen.MODULE_PARAM[kind].get(k, k) for k in c if k not in screen.module_drop(kind)}
            self.assertEqual(passed - have, set(), kind)
            # (L4) with the properties of module 3.2 in the schema, they are passed, and nothing else new
            more = have | set(screen.MODULE_IF_LISTED.get(kind, ()))
            with mock.patch.object(screen, "module_props", lambda t, k=ctype, m=more: m if t == k else set()):
                passed = {screen.MODULE_PARAM[kind].get(k, k) for k in c if k not in screen.module_drop(kind)}
            self.assertEqual(passed - more, set(), kind)
            self.assertEqual(passed - have, {k for k in c if k in screen.MODULE_IF_LISTED.get(kind, ()) and k not in have},
                             kind)   # module 0.4.0 lists them on the pump, the motor and the fan

    def test_a_pipe_meets_the_tile_of_a_static_tank(self):
        from hmi import library
        fx, fy, fw, fh = library.STATIC_TILE
        box = {"x": 100, "y": 50, "w": 200, "h": 100}
        live = {s: diagram.connection_point(box, s) for s in diagram.SIDES}
        self.assertEqual(live, {"left": (100, 100), "right": (300, 100), "top": (200, 50), "bottom": (200, 150)})
        static = {s: diagram.connection_point(dict(box, tile=library.STATIC_TILE), s) for s in diagram.SIDES}
        self.assertEqual(static["left"], (100 + fx * 200, 100))                  # the tile's edges, the box's centre lines
        self.assertEqual(static["right"], (100 + (fx + fw) * 200, 100))
        self.assertEqual(static["top"], (200, 50 + fy * 100))
        self.assertEqual(static["bottom"], live["bottom"])                       # the identifier lies beneath the tile
        # the fixture's break tank states no capacity: the library's tile under the stock rendering (the pipe
        # into it ends at the tile's left edge, the pipe out of it starts at its right edge), the module's tank
        # under the module rendering (0.3.0), which fills its box
        desc = fixture("pilot-supply.json")
        bt = next(s for s in desc["symbols"] if s["id"] == "BT1")
        self.assertEqual((bt["params"], "device" in bt), ({"static": True, "tag": "Break tank"}, False))
        left, right, y = bt["x"] + fx * bt["w"], bt["x"] + (fx + fw) * bt["w"], bt["y"] + bt["h"] / 2
        for render, ends in (("stock", (left, right)), ("module", (bt["x"], bt["x"] + bt["w"]))):
            screen.RENDER["target"] = render
            try:
                doc, info = screen.build_screen(copy.deepcopy(desc), self.contracts)
            finally:
                screen.RENDER["target"] = "stock"
            self.assertEqual(info["errors"], [])
            paths = {e["name"]: e["d"] for e in view_nodes(doc)["Pipes"]["props"]["elements"]}
            self.assertEqual(paths["p9"], diagram.path_d([(56, 184), (ends[0], y)]), render)
            self.assertEqual(paths["p1"], diagram.path_d([(ends[1], y), (200, 184)]), render)
            self.assertTrue(info["flow"]["ok"])
        self.assertEqual(view_nodes(doc)["BT1"]["type"], "cadre.ob.tank")
        self.assertIs(view_nodes(doc)["BT1"]["props"]["hasCapacity"], False)
        # with its capacity stated, the module draws the tank, which fills its box: the pipes end at the box
        stated = copy.deepcopy(desc)
        next(x for x in stated["symbols"] if x["id"] == "BT1")["params"].update(max=450, unit="m³")
        screen.RENDER["target"] = "module"
        try:
            doc, info = screen.build_screen(stated, self.contracts)
        finally:
            screen.RENDER["target"] = "stock"
        self.assertEqual((view_nodes(doc)["BT1"]["type"], info["errors"]), ("cadre.ob.tank", []))
        paths = {e["name"]: e["d"] for e in view_nodes(doc)["Pipes"]["props"]["elements"]}
        self.assertEqual(paths["p9"], diagram.path_d([(56, 184), (bt["x"], y)]))
        self.assertEqual(paths["p1"], diagram.path_d([(bt["x"] + bt["w"], y), (200, 184)]))

    # ---- 2. identifiers -----------------------------------------------------------------
    def test_an_identifier_ends_in_an_ellipsis_and_is_never_cut_at_the_start(self):
        from hmi import library, theme
        css = self.prj.files["com.inductiveautomation.perspective/stylesheet/stylesheet.css"].decode("utf-8")
        self.assertIn(theme.layout_css().strip(), css)
        label = ".ia_labelComponent.psc-cadre\\/text\\/ellipsis"
        self.assertIn(label + " {\n  max-width: 100%;\n  min-width: 0;\n  overflow: hidden;\n}", css)
        self.assertIn(label + " > * {\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}", css)
        self.assertIn(".psc-cadre\\/box\\/within {\n  max-width: 100%;\n  min-width: 0;\n}", css)
        for name in library.LAYOUT_CLASSES:                                      # each a style class of the parent
            body = json.loads(self.prj.files[f"com.inductiveautomation.perspective/style-classes/{name}/style.json"])
            self.assertEqual(body, {"base": {"style": {}}})
        # the label that draws the identifier of every kind, and the caption of an instrument field
        where = {f"Automation/{k}": ["Tag"] for k in library.DEVICE_KINDS}
        where.update({"Automation/Readout": ["Tag"], "Automation/Tank": ["Tag", "StaticTag"],
                      "Instrument/Field": ["UnitLabel"], "Instrument/Controller": ["Tag"],
                      "Instrument/Sequence": ["Tag", "Text"]})
        self.assertEqual(sorted(where), sorted(k["view"] for k in self.prof["kinds"].values()))
        for path, names in where.items():
            nodes = view_nodes(self.view(path))
            for n in names:
                style = nodes[n]["props"]["style"]
                self.assertIn(library.ELLIPSIS, style["classes"].split(), (path, n))
                self.assertEqual(style["whiteSpace"], "nowrap", (path, n))
                # a `textOverflow` on the label itself shows no ellipsis (its text is in an inner element)
                self.assertNotIn("textOverflow", style, (path, n))
        # under a symbol the readout is no wider than the embed, so the identifier's label is held too
        for k in library.DEVICE_KINDS:
            readout = view_nodes(self.view(f"Automation/{k}"))["Readout"]
            self.assertEqual((readout["props"]["style"]["classes"], readout["position"]), (library.WITHIN, {"shrink": 1}), k)

    def test_the_embed_of_a_symbol_is_as_wide_as_its_identifier_needs(self):
        from hmi import library
        pump = self.contracts["Automation/Pump"]
        self.assertEqual((library.IDENTIFIER_CHARS, pump["identifier"]["pad"]), (16, 8))

        def box(tag, pos="bottom", **params):
            return screen.symbol_box({"kind": "pump", "x": 300, "y": 160, "w": 48, "h": 48,
                                      "params": {"readoutPosition": pos, "tag": tag, **params}}, pump)
        self.assertEqual(box("P-101", hasTag=True), (288.0, 160, 72, 92))       # as before: an identifier that fits
        self.assertEqual(box("ABCDEFGH", hasTag=True), (288.0, 160, 72, 92))    # eight characters fit the default
        self.assertEqual(box("ABCDEFGHI", hasTag=True), (284.0, 160, 80, 92))   # nine: 9 * 8 + 8, centred on the symbol
        self.assertEqual(box("SuctionLowLvl_SW", hasTag=True), (256.0, 160, 136, 92))
        self.assertEqual(box("x" * 40, hasTag=True), (256.0, 160, 136, 92))     # no wider than 16 characters need
        self.assertEqual(box("SuctionLowLvl_SW", "top", hasTag=True), (256.0, 116, 136, 92))
        self.assertEqual(box("SuctionLowLvl_SW", "right", hasTag=True), (300, 160, 48 + 136, 48))
        self.assertEqual(box("SuctionLowLvl_SW", "left", hasTag=True), (300 - 136, 160, 48 + 136, 48))
        self.assertEqual(box("ABCDEFG", "right", hasTag=True), (300, 160, 112, 48))   # seven fit beside the symbol
        self.assertEqual(box("SuctionLowLvl_SW", "none", hasTag=True), (300, 160, 48, 48))
        self.assertEqual(box("SuctionLowLvl_SW", hasTag=False), (288.0, 160, 72, 92))  # an identifier not drawn
        self.assertEqual(box("SuctionLowLvl_SW"), (256.0, 160, 136, 92))        # the page's ID-tag button may show it
        self.assertEqual(box(""), (288.0, 160, 72, 92))
        # the cell of a card is as wide as the embed
        group = {"direction": "row", "items": [{"id": "C", "kind": "pump", "basis": "0px", "grow": 1,
                                                "params": {"hasTag": True, "tag": "SupplyPump_No2"}}]}
        body = screen.flex_group(group, self.contracts, "[default]t", screen.Report(), {}, {})
        self.assertEqual(view_nodes({"root": body})["C"]["props"]["style"], {"width": f"{14 * 8 + 8}px", "height": "92px"})

    def test_the_samples_are_built_as_before(self):
        """Every identifier of our own pages fits the default embed, so no embed of theirs moved."""
        from hmi import library
        automation = {k.lower() for k in library.DEVICE_KINDS}
        seen = 0
        for path in sorted((ROOT / "screens").rglob("*.json")):
            desc = json.loads(path.read_text(encoding="utf-8"))
            if "screen" not in desc:
                continue
            for s in screen.descriptor_items(desc):
                if s["kind"].lower() not in automation:
                    continue
                c = self.contracts[screen.KIND_VIEW[s["kind"].lower()]]
                pos = s.get("params", {}).get("readoutPosition", "bottom")
                self.assertEqual(screen.readout_extent(s, c), screen.READOUT_EXTENT[pos], (path.name, s["id"]))
                seen += 1
        self.assertGreater(seen, 20)

    def test_the_fixture_shows_what_the_plant_showed(self):
        desc, model = fixture("pilot-supply.json"), fixture("pilot-devices.json")
        syms = {s["id"]: s for s in desc["symbols"]}
        long_ = {i: syms[i]["params"]["tag"] for i in ("P2", "DI1", "FT1")}
        self.assertEqual({i: (syms[i]["kind"], len(t)) for i, t in long_.items()},
                         {"P2": ("pump", 14), "DI1": ("indicator", 16), "FT1": ("readout", 15)})
        titles = {d["id"]: d["title"] for d in model["devices"]}
        self.assertEqual({i: titles[i] for i in long_}, long_)                   # the faceplate header shows it whole
        doc, info = screen.build_screen(copy.deepcopy(desc), self.contracts)
        nodes = view_nodes(doc)
        self.assertEqual(nodes["P2"]["position"], pv.cpos(300 - 36, 340, 14 * 8 + 8, 92))
        self.assertEqual(nodes["DI1"]["position"], pv.cpos(1366 - 44, 160, 136, 92))
        # the readout is as wide as its identifier needs and as high as the profile says with `hasTag`
        ro = self.prof["kinds"]["readout"]
        self.assertEqual(ro["sizes"], [{"when": {"hasTag": True}, "size": [72, 40]}])
        self.assertEqual((syms["FT1"]["w"], syms["FT1"]["h"]), (15 * 8 + ro["identifier"]["pad"], 40))

    def test_a_readout_too_small_for_what_it_shows_is_grown_about_its_centre(self):
        ro = self.contracts["Automation/Readout"]
        self.assertIs(ro["grows"], True)
        self.assertEqual({k: v["grows"] for k, v in self.prof["kinds"].items()},
                         {k: k == "readout" for k in self.prof["kinds"]})      # the one kind the generator grows

        def box(w, h, limit=None, **params):
            return screen.symbol_box({"id": "R", "kind": "readout", "x": 400, "y": 200, "w": w, "h": h,
                                      "params": params}, ro, limit)
        self.assertEqual(box(72, 24), (400, 200, 72, 24))                        # as before: no flag, the box as given
        self.assertEqual(box(60, 20), (400, 200, 60, 20))                        # even one smaller than the default
        self.assertEqual(box(72, 24, tag="SupplyFlow_FT01"), (400, 200, 72, 24))                # an identifier not drawn
        self.assertEqual(box(72, 24, hasTag=False, tag="SupplyFlow_FT01"), (400, 200, 72, 24))
        self.assertEqual(box(96, 40, hasTag=True, tag="FIT-101"), (400, 200, 96, 40))           # a box that holds it
        self.assertEqual(box(130, 40, hasTag=True, tag="SupplyFlow_FT01"), (400, 200, 130, 40))
        self.assertEqual(box(160, 60, hasTag=True, tag="SupplyFlow_FT01"), (400, 200, 160, 60))  # never made smaller
        self.assertEqual(box(72, 24, hasTag=True, tag="FT-1"), (400, 192, 72, 40))              # the two lines: `sizes`
        self.assertEqual(box(60, 24, hasTag=True, tag="FT-1"), (394, 192, 72, 40))
        self.assertEqual(box(72, 24, hasTag=True, tag="SupplyFlow_FT01"), (400 - 29, 192, 15 * 8 + 10, 40))
        self.assertEqual(box(72, 24, hasTag=True, tag="x" * 40), (400 - 33, 192, 16 * 8 + 10, 40))  # 16 characters at most
        self.assertEqual(box(72, 24, 16, hasTag=True, tag="SupplyFlow_FT01"), (392, 192, 88, 40))   # the room it is given
        self.assertEqual(box(72, 24, 0, hasTag=True, tag="SupplyFlow_FT01"), (400, 192, 72, 40))    # the lines all the same
        for given in ((72, 24), (130, 40)):                                      # its centre stays where the box had it
            x, y, w, h = box(*given, hasTag=True, tag="SupplyFlow_FT01")
            self.assertEqual((x + w / 2, y + h / 2), (400 + given[0] / 2, 200 + given[1] / 2))
        # on the page: the embed is grown, and the pipes still end where the descriptor's box has its sides
        desc = copy.deepcopy(fixture("pilot-supply.json"))
        ft1 = next(s for s in desc["symbols"] if s["id"] == "FT1")
        ft1.update(x=549, y=172, w=72, h=24)                                     # the same centre as the fixture's box
        doc, info = screen.build_screen(copy.deepcopy(desc), self.contracts)
        self.assertEqual(info["errors"], [])
        full, _info = screen.build_screen(copy.deepcopy(fixture("pilot-supply.json")), self.contracts)
        self.assertEqual(view_nodes(doc)["FT1"]["position"], view_nodes(full)["FT1"]["position"])
        self.assertEqual(view_nodes(doc)["FT1"]["position"], pv.cpos(520, 164, 130, 40))
        fixed = copy.deepcopy(self.contracts)
        del fixed["Automation/Readout"]["grows"]
        given, _info = screen.build_screen(copy.deepcopy(desc), fixed)
        self.assertEqual(view_nodes(given)["FT1"]["position"], pv.cpos(549, 172, 72, 24))
        self.assertEqual(view_nodes(doc)["Pipes"], view_nodes(given)["Pipes"])
        ends = [e["d"] for e in view_nodes(doc)["Pipes"]["props"]["elements"] if "549 " in e["d"] or "621 " in e["d"]]
        self.assertGreaterEqual(len(ends), 2)                                    # a pipe at each side of the box given
        # a readout in a card takes its place in the row; the row is as high as the readout needs
        self.assertEqual(screen.leaf_height({"id": "R", "kind": "readout", "params": {"hasTag": True}}, self.contracts), 40)

    def test_an_embed_is_widened_only_into_the_room_the_next_symbol_leaves(self):
        c = self.contracts
        ind, pump = c["Automation/Indicator"], c["Automation/Pump"]

        def lamp(i, x, tag, y=100, **params):
            return {"id": i, "kind": "indicator", "x": x, "y": y, "w": 48, "h": 48,
                    "params": {"tag": tag, "hasTag": True, **params}}
        a14, b14, a10 = "FwdLimit_LS_01", "RevLimit_LS_02", "FwdLim_LS1"
        self.assertEqual([len(t) for t in (a14, b14, a10)], [14, 14, 10])
        box = lambda s, lim: screen.symbol_box(s, ind, lim.get(s["id"]))          # noqa: E731
        # far enough apart: each embed is as wide as its identifier needs, 14 * 8 + 8
        a, b = lamp("A", 700, a14), lamp("B", 820, b14)
        self.assertEqual(screen.embed_limits([a, b], c), {})
        self.assertEqual((box(a, {}), box(b, {})), ((664, 100, 120, 92), (784, 100, 120, 92)))
        # 80 px apart: the default embeds leave 8 px between them, and each takes half
        a, b = lamp("A", 700, a14), lamp("B", 780, b14)
        lim = screen.embed_limits([a, b], c)
        self.assertEqual(lim, {"A": 8, "B": 8})
        self.assertEqual((box(a, lim), box(b, lim)), ((684, 100, 80, 92), (764, 100, 80, 92)))   # they meet, no more
        self.assertEqual(screen.embed_limits([b, a], c), lim)                    # whatever the order
        # one wants less than half of the gap: the other takes the rest
        a, b = lamp("A", 700, a10), lamp("B", 800, b14)
        lim = screen.embed_limits([a, b], c)
        self.assertEqual(lim, {"B": 40})                                         # 28 px between: A takes 8, B the 20 left
        self.assertEqual((box(a, lim), box(b, lim)), ((680, 100, 88, 92), (768, 100, 112, 92)))
        # between two neighbours the embed stays centred on its symbol: it gives up at both sides
        a, b, e = lamp("A", 700, a14), lamp("B", 780, b14), lamp("E", 900, "E-1")
        lim = screen.embed_limits([a, b, e], c)
        self.assertEqual(lim, {"A": 8, "B": 8})
        self.assertEqual(box(b, lim), (764, 100, 80, 92))
        self.assertEqual(box(e, lim), (888, 100, 72, 92))                        # a neighbour that fits is untouched
        # another row (no more than the tolerance shared down the page): nothing in the way
        self.assertEqual(screen.embed_limits([lamp("A", 700, a14), lamp("B", 780, b14, y=100 + 92 - screen.OVERLAP)], c), {})
        self.assertEqual(screen.embed_limits([lamp("A", 700, a14), lamp("B", 780, b14, y=100 + 91 - screen.OVERLAP)], c),
                         {"A": 8, "B": 8})
        # default embeds that overlap already: no narrower identifier parts them, and gate G5 reports the pair
        self.assertEqual(screen.embed_limits([lamp("A", 700, a14), lamp("B", 760, b14)], c), {})
        # an identifier nobody shows wants nothing
        self.assertEqual(screen.embed_limits([lamp("A", 700, a14, hasTag=False), lamp("B", 780, b14)], c), {"B": 16})
        # a readout beside the symbol reaches one way only, up to the block that stands there
        p = {"id": "P", "kind": "pump", "x": 300, "y": 100, "w": 48, "h": 48,
             "params": {"readoutPosition": "right", "tag": "SupplyPump_No002"}}
        blk = {"id": "C", "kind": "controller", "x": 300 + 48 + 64 + 20, "y": 90, "w": 120, "h": 96, "params": {"tag": "PIC-1"}}
        lim = screen.embed_limits([p, blk], c)
        self.assertEqual(lim, {"P": 20})
        self.assertEqual(screen.symbol_box(p, pump, lim["P"]), (300, 100, 48 + 64 + 20, 48))
        self.assertEqual(screen.symbol_box(dict(p, params={**p["params"], "readoutPosition": "left"}), pump, 20),
                         (300 - 84, 100, 48 + 84, 48))
        gap = {"id": "G", "kind": "compass", "x": 432, "y": 90, "w": 120, "h": 96}   # a kind the library lacks: its box
        self.assertEqual(screen.embed_limits([p, gap], c), {"P": 20})
        # a readout too narrow beside a valve: the two share the gap, the readout about its centre
        ro = {"id": "R", "kind": "readout", "x": 520, "y": 164, "w": 72, "h": 24, "params": {"hasTag": True, "tag": "SupplyFlow_FT01"}}
        xv = {"id": "X", "kind": "valve", "x": 620, "y": 160, "w": 48, "h": 48, "params": {"tag": "SupplyValve_XV01"}}
        lim = screen.embed_limits([ro, xv], c)
        self.assertEqual(lim, {"R": 16, "X": 16})
        self.assertEqual(screen.symbol_box(ro, c["Automation/Readout"], lim["R"]), (512, 156, 88, 40))
        self.assertEqual(screen.symbol_box(xv, c["Automation/Valve"], lim["X"]), (600, 160, 88, 92))
        # on a page: the two lamps of a row 80 px apart no longer lie over each other
        desc = {"screen": {"id": "T", "route": "/t", "title": "T", "view": "Screens/T", "layout": "diagram",
                           "width": 1580, "height": 600}, "tagRoot": "[default]t",
                "symbols": [lamp("A", 700, a14), lamp("B", 780, b14)]}
        doc, info = screen.build_screen(copy.deepcopy(desc), c)
        nodes = view_nodes(doc)
        self.assertEqual((info["errors"], nodes["A"]["position"], nodes["B"]["position"]),
                         ([], pv.cpos(684, 100, 80, 92), pv.cpos(764, 100, 80, 92)))
        with tempfile.TemporaryDirectory() as d:
            out, _base, _reports, gates = self.build(d, desc)
            res = gates.g5_layout(out)
        self.assertEqual((res["ok"], res["warnings"]), (True, [                  # said by the gate, each by its name
            "Screens/T: A is 80 px wide and its tag of 14 characters needs 120 px: it ends in an ellipsis",
            "Screens/T: B is 80 px wide and its tag of 14 characters needs 120 px: it ends in an ellipsis"]))
        # the same where the descriptor does not state `hasTag`: the toolbar's button shows the identifier,
        # and the gate reads the binding, not the contract's default that stands beside it (GF-60)
        bare = copy.deepcopy(desc)
        for sym in bare["symbols"]:
            del sym["params"]["hasTag"]
        with tempfile.TemporaryDirectory() as d:
            out, _base, _reports, gates = self.build(d, bare)
            res = gates.g5_layout(out)
        self.assertEqual((res["ok"], res["warnings"]), (True, [
            "Screens/T: A is 80 px wide and its tag of 14 characters needs 120 px: it ends in an ellipsis",
            "Screens/T: B is 80 px wide and its tag of 14 characters needs 120 px: it ends in an ellipsis"]))
        # and none where the descriptor refuses the identifier
        off = copy.deepcopy(desc)
        for sym in off["symbols"]:
            sym["params"]["hasTag"] = False
        with tempfile.TemporaryDirectory() as d:
            out, _base, _reports, gates = self.build(d, off)
            res = gates.g5_layout(out)
        self.assertEqual((res["ok"], res["warnings"]), (True, []))
        # default embeds that overlap already keep their width, and the gate reports the pair as it always did
        desc["symbols"] = [lamp("A", 700, a14), lamp("B", 760, b14)]
        with tempfile.TemporaryDirectory() as d:
            out, _base, _reports, gates = self.build(d, desc)
            res = gates.g5_layout(out)
        self.assertEqual((res["ok"], res["warnings"]), (True, ["Screens/T: readout area A overlaps B (60 x 92 px)"]))
        # our own pages and the fixture: no embed is held back, so each is built as before
        pages = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "screens").rglob("*.json"))]
        pages = [p for p in pages if "symbols" in p] + [fixture("pilot-supply.json")]
        self.assertGreater(len(pages), 4)
        for page in pages:
            self.assertEqual(screen.embed_limits(page["symbols"], c), {}, page["screen"]["route"])

    def test_what_the_identifier_of_each_kind_needs(self):
        from hmi import library
        c = self.contracts
        pump, ro, ctl = c["Automation/Pump"], c["Automation/Readout"], c["Instrument/Controller"]
        tank, fld = c["Automation/Tank"], c["Instrument/Field"]
        shown, needs = library.identifier_shown, library.identifier_needs
        # an automation symbol: unless the descriptor says no (the page's ID-tag button shows it), and never without a readout
        self.assertEqual([shown(pump, p) for p in ({}, {"hasTag": True}, {"hasTag": False}, {"readoutPosition": "none"})],
                         [True, True, False, False])
        self.assertEqual([shown(ro, p) for p in ({}, {"hasTag": True}, {"hasTag": False})], [False, True, False])
        self.assertEqual([shown(ctl, p) for p in ({}, {"hasTag": True}, {"hasTag": False})], [True, True, False])
        self.assertEqual((shown(tank, {}), shown(fld, {}), shown({"params": {}}, {})), (True, True, False))
        self.assertEqual((needs(pump, {}, 14), needs(pump, {"readoutPosition": "top"}, 14)), (120, 120))
        self.assertEqual(needs(pump, {"readoutPosition": "right"}, 14), 120 + 48)   # beside the symbol
        self.assertEqual((needs(pump, {}, 20), library.identifier_width(pump, 20)), (168, 136))   # the whole text; the embed
        self.assertEqual((needs(ro, {}, 15), needs(ctl, {}, 16), needs(fld, {}, 19)), (130, 162, 142.5))
        # a tank: the identifier of a live tank takes a share of the tile at any size, a static one's the whole width
        ident = self.prof["kinds"]["tank"]["identifier"]
        self.assertEqual((ident["share"], tank["identifier"]["share"]), (0.86, library.TANK_TAG_WIDTH))
        self.assertEqual([k for k, v in self.prof["kinds"].items() if "share" in v["identifier"]], ["tank"])
        nodes = view_nodes(self.view("Automation/Tank"))
        self.assertEqual(nodes["Tag"]["position"]["width"], ident["share"])
        self.assertEqual((nodes["StaticTag"]["position"]["x"], nodes["StaticTag"]["position"]["width"]), (0.0, 1.0))
        cw = self.prof["text"]["fonts"][ident["font"]]["charWidth"]
        self.assertEqual((needs(tank, {}, 16), needs(tank, {"static": True}, 16)), (16 * cw / 0.86, 16 * cw))
        for n in range(1, library.IDENTIFIER_CHARS + 1):                         # `pad` never asks for less than the share
            self.assertGreaterEqual(library.identifier_width(tank, n), needs(tank, {}, n), n)
        width = self.prof["kinds"]["tank"]["size"][0]                            # `fits` and `pad`: the default width
        self.assertLessEqual(needs(tank, {}, ident["fits"]), width)
        self.assertGreater(needs(tank, {}, ident["fits"] + 1), width)
        self.assertEqual(ident["pad"], round(width * (1 - ident["share"])))

    # ---- 3. the profile -----------------------------------------------------------------
    def test_the_profile_states_the_sizes_a_layouter_needs(self):
        from hmi import library, theme
        prof = self.prof
        self.assertEqual(json.loads((ROOT / "library/profile.json").read_text(encoding="utf-8")), prof)   # current
        self.assertEqual(sorted(prof), ["ackRelay", "alarms", "config", "descriptor", "deviceKinds", "devices", "diagram", "faceplate", "faceplates", "forceEncodings",
                                        "frame", "functions", "kinds", "library", "ownership", "parts", "schema", "text", "writePaths"])
        self.assertEqual(prof["text"], {"identifierChars": 16, "fonts": library.FONTS})
        # each font is the one that was measured: its size and its line in the tokens
        tokens = theme.load_tokens(ROOT / "library/tokens/openbridge-tokens.json")

        def token(v):
            m = re.match(r"var\((--[\w-]+)\)$", str(v))
            return token(tokens["sizes"]["regular"].get(m.group(1), tokens["global"].get(m.group(1)))) if m else v
        for name, font in library.FONTS.items():
            decl = {k: token(v) for k, v in tokens["fonts"][name].items()}
            self.assertEqual((decl["fontFamily"], decl["fontSize"]), ('"Noto Sans"', f"{font['px']:g}px"), name)
            self.assertEqual(decl.get("lineHeight", "22px"), f"{font['line']}px", name)   # no token: the measured line
            m = font["measured"]
            self.assertGreaterEqual(font["charWidth"], m["upper"] if "label" in name or "unit" in name else m["digit"], name)
            self.assertLess(font["charWidth"] - 0.5, m["upper"], name)           # the mean rounded up to half a pixel
            self.assertEqual(sorted(font), ["charWidth", "line", "measured", "px"], name)
        # the sizes a flag needs beyond the default: taken from the lines of the fonts and the built views
        kinds = prof["kinds"]
        self.assertEqual({k: v["sizes"] for k, v in kinds.items() if v["sizes"]},
                         {"readout": [{"when": {"hasTag": True}, "size": [72, 40]}],
                          "instrument-field": [{"when": {"size": "enhanced", "hasSetpoint": True}, "size": [96, 66]}],
                          "tank": [{"when": {"static": True}, "size": [96, 80]}]})
        # a static vessel: the size of the fixture's break tank, with the identifier's line beneath the tile
        w, h = library.STATIC_TANK_SIZE
        bt = next(x for x in fixture("pilot-supply.json")["symbols"] if x["id"] == "BT1")
        self.assertEqual((bt["w"], bt["h"]), (w, h))
        self.assertGreaterEqual(h * (1 - library.STATIC_TILE[1] - library.STATIC_TILE[3]), library.FONTS["instrument-label"]["line"])
        self.assertTrue(all(isinstance(v["sizes"], list) for v in kinds.values()))
        ro = view_nodes(self.view("Automation/Readout"))
        self.assertEqual(ro["root"]["props"]["style"]["border"].split()[0], "1px")
        self.assertEqual(ro["Value"]["props"]["style"]["classes"].split()[0], "cadre/font/automation-value-regular")
        self.assertEqual(ro["Tag"]["props"]["style"]["classes"].split()[0], "cadre/font/automation-label")
        self.assertEqual(library.READOUT_TAGGED, 22 + 16 + 2)
        enhanced = {k: token(v) for k, v in tokens["fonts"]["instrument-value-enhanced-active"].items()}
        small = {k: token(v) for k, v in tokens["fonts"]["instrument-value-small-neutral"].items()}
        fld = view_nodes(self.view("Instrument/Field"))
        self.assertEqual(fld["Value"]["props"]["style"]["lineHeight"], "1")      # the value is as high as its font
        self.assertEqual([c["meta"]["name"] for c in fld["root"]["children"]], ["Setpoint", "Value", "UnitLabel"])
        self.assertEqual(library.FIELD_ENHANCED_SETPOINT,
                         int(small["lineHeight"][:-2]) + int(enhanced["fontSize"][:-2]) + library.FONTS["instrument-unit"]["line"])
        self.assertLessEqual(16 + 16 + 16, kinds["instrument-field"]["size"][1])  # the regular value with a setpoint fits
        self.assertLessEqual(34 + 16, kinds["instrument-field"]["size"][1])       # the enhanced value alone fits
        ctl = kinds["controller"]                                                # every flag of a controller fits
        self.assertLessEqual(20 + 3 * 16 + 3 * 2 + 2 * 2 + 2, ctl["size"][1])
        self.assertLessEqual(20 + 16 + 16 + 2 * 2 + 2 * 2 + 2, kinds["sequence"]["size"][1])
        # `block_size`: the first entry the parameters meet, a parameter not given at its default
        rc, fc = self.contracts["Automation/Readout"], self.contracts["Instrument/Field"]
        self.assertEqual((library.block_size(rc), library.block_size(rc, {"hasTag": True}),
                          library.block_size(rc, {"hasTag": False})), ([72, 24], [72, 40], [72, 24]))
        self.assertEqual((library.block_size(fc, {"size": "enhanced"}), library.block_size(fc, {"hasSetpoint": True}),
                          library.block_size(fc, {"size": "enhanced", "hasSetpoint": True})), ([96, 64], [96, 64], [96, 66]))

    def test_the_profile_states_each_kind_s_identifier(self):
        from hmi import library
        kinds = self.prof["kinds"]
        got = {k: (v["identifier"]["param"], v["identifier"]["flag"], v["identifier"]["font"], v["identifier"]["pad"],
                   v["identifier"]["fits"]) for k, v in kinds.items()}
        symbol = ("tag", "hasTag", "automation-label", 8, 8)
        self.assertEqual(got, {**{k.lower(): symbol for k in library.DEVICE_KINDS},
                               "readout": ("tag", "hasTag", "automation-label", 10, 7),
                               "controller": ("tag", "hasTag", "automation-label", 34, 10),
                               "sequence": ("tag", "hasTag", "automation-label", 14, 16),
                               "tank": ("tag", "hasTag", "instrument-label", 24, 19),
                               "instrument-field": ("label", "hasTag", "instrument-unit", 0, 12)})
        self.assertEqual({k: v["identifier"].get("suffix") for k, v in kinds.items() if "suffix" in v["identifier"]},
                         {"instrument-field": "unit"})                           # its caption is the label and the unit
        self.assertEqual({k: v["value"] for k, v in kinds.items() if v["value"]},
                         {"readout": {"font": "automation-value-regular", "pad": 10}})
        for kind, k in kinds.items():                                            # the parameter and the flag are the kind's own
            ident = k["identifier"]
            self.assertIn(ident["param"], k["params"], kind)
            self.assertTrue(ident["flag"] is None or ident["flag"] in k["params"], kind)
            width = k["embedBox"]["bottom"][2] if k["embedBox"] else k["size"][0]
            cw = self.prof["text"]["fonts"][ident["font"]]["charWidth"]
            self.assertLessEqual(ident["fits"] * cw + ident["pad"], width, kind)             # `fits` characters fit
            self.assertGreater((ident["fits"] + 1) * cw + ident["pad"], width, kind)         # and one more does not
            n = min(ident["fits"], library.IDENTIFIER_CHARS)                     # no identifier is longer
            self.assertEqual(library.identifier_width(self.contracts[k["view"]], ident["fits"]), n * cw + ident["pad"], kind)
        # `pad` is what the built view takes beside the text
        def px(v):
            return [int(x[:-2]) if x.endswith("px") else int(x) for x in str(v).split()]
        sym = view_nodes(self.view("Automation/Pump"))
        self.assertEqual(2 * px(sym["Readout"]["props"]["style"]["padding"])[1], 8)
        ro = view_nodes(self.view("Automation/Readout"))["root"]["props"]["style"]
        self.assertEqual(2 * px(ro["padding"])[1] + 2 * px(ro["border"].split()[0])[0], 10)
        ctl = view_nodes(self.view("Instrument/Controller"))
        style = ctl["root"]["props"]["style"]
        badge = px(ctl["Badge_auto"]["position"]["basis"])[0]
        gap = px(ctl["Head"]["props"]["style"]["gap"])[0]
        self.assertEqual(2 * px(style["padding"])[1] + 2 * px(style["border"].split()[0])[0] + badge + gap, 34)
        self.assertEqual(ctl["Tag"]["position"], {"grow": 1, "basis": "0px"})    # the identifier takes the rest of the head
        seq = view_nodes(self.view("Instrument/Sequence"))["root"]["props"]["style"]
        self.assertEqual(2 * px(seq["padding"])[1] + 2 * px(seq["border"].split()[0])[0], 14)
        tank = view_nodes(self.view("Automation/Tank"))["Tag"]["position"]
        self.assertEqual((tank["width"], round(168 * (1 - tank["width"]))), (library.TANK_TAG_WIDTH, 24))

    def test_a_layouter_places_each_symbol_from_the_profile_alone(self):
        """The embed the generator writes for each symbol of the fixture page has the box the profile
        gives: the descriptor's box for a box kind; for an automation symbol the symbol box moved and
        grown by `embedBox`, and as much wider as its identifier needs (`profile_embed`)."""
        desc = fixture("pilot-supply.json")
        doc, info = screen.build_screen(copy.deepcopy(desc), self.contracts)
        self.assertEqual(info["errors"], [])
        nodes = view_nodes(doc)
        for s in desc["symbols"]:
            x, y, w, h = profile_embed(self.prof, s)
            self.assertEqual(nodes[s["id"]]["position"], pv.cpos(x, y, w, h), s["id"])
        sq = next(s for s in desc["symbols"] if s["id"] == "SQ1")
        self.assertEqual([sq["w"], sq["h"]], self.prof["kinds"]["sequence"]["size"])   # placed at its default size
        # a readout, whatever box it is given, with and without its identifier
        ro = self.contracts["Automation/Readout"]
        for w, h in ((72, 24), (60, 20), (72, 40), (96, 40), (130, 40), (200, 60)):
            for n in (0, 4, 7, 8, 15, 16, 30):
                for flag in (True, False, None):
                    params = {"tag": "W" * n, **({} if flag is None else {"hasTag": flag})}
                    s = {"id": "R", "kind": "readout", "x": 400, "y": 200, "w": w, "h": h, "params": params}
                    self.assertEqual(list(screen.symbol_box(s, ro)), profile_embed(self.prof, s), (w, h, n, flag))
        # a `when` never names a parameter's default, so a parameter a symbol does not give meets none
        for kind, k in self.prof["kinds"].items():
            defaults = self.contracts[k["view"]]["params"]
            for entry in k["sizes"]:
                for flag, value in entry["when"].items():
                    self.assertNotEqual(defaults[flag], value, (kind, flag))
        # the rule, against the generator, for every automation kind, side and length of identifier
        for kind, k in self.prof["kinds"].items():
            if k["embedBox"] is None:
                continue
            c = self.contracts[k["view"]]
            for pos in k["embedBox"]:
                for n in (0, 1, 7, 8, 9, 12, 16, 17, 30):
                    for flag in (True, False, None):
                        params = {"readoutPosition": pos, "tag": "W" * n, **({} if flag is None else {"hasTag": flag})}
                        s = {"id": "S", "kind": kind, "x": 400, "y": 200, "w": 48, "h": 48, "params": params}
                        self.assertEqual(list(screen.symbol_box(s, c)), profile_embed(self.prof, s), (kind, pos, n, flag))

    def test_the_profile_states_how_a_pipe_meets_a_symbol_and_how_it_is_routed(self):
        from hmi import library
        d = self.prof["diagram"]
        from hmi import gates
        self.assertEqual(d, {"ring": diagram.RING, "symbol": 48, "staticTile": list(library.STATIC_TILE),
                             "routes": diagram.ROUTES, "via": diagram.VIA, "overlap": screen.OVERLAP})
        self.assertEqual((d["overlap"], gates.OVERLAP), (4, screen.OVERLAP))    # one tolerance: the gate's and the generator's
        self.assertEqual((d["ring"], d["staticTile"]), (18, [0.06, 0.06, 0.88, 0.66]))
        sym = {"x": 100, "y": 100, "w": d["symbol"], "h": d["symbol"], "anchor": "symbol-centre"}
        self.assertEqual({s: diagram.connection_point(sym, s) for s in diagram.SIDES},
                         {"left": (124 - d["ring"], 124), "right": (124 + d["ring"], 124),
                          "top": (124, 124 - d["ring"]), "bottom": (124, 124 + d["ring"])})
        holder = view_nodes(self.view("Automation/Pump"))["Holder"]["position"]   # the round holder the pipe meets
        self.assertEqual((holder["width"] / 2, holder["x"] + holder["width"] / 2), (d["ring"], d["symbol"] / 2))
        # every pair of axes has a shape, and `route` draws it
        self.assertEqual(sorted(d["routes"]), sorted(a + b for a in "vh-" for b in "vh-"))
        p0, p1 = (10, 20), (110, 80)
        shapes = {"Z_Y": [p0, (10, 50), (110, 50), p1], "Z_X": [p0, (60, 20), (60, 80), p1],
                  "L_Y": [p0, (10, 80), p1], "L_X": [p0, (110, 20), p1]}
        self.assertEqual(sorted(set(d["routes"].values())), ["L_X", "L_Y", "Z_X", "Z_Y"])
        side = {"v": ("top", "bottom"), "h": ("left", "right"), "-": (None,)}
        for axes, shape in d["routes"].items():
            for s0 in side[axes[0]]:
                for s1 in side[axes[1]]:
                    self.assertEqual(diagram.route(p0, s0, p1, s1), shapes[shape], (axes, s0, s1))
                    self.assertEqual(diagram.route(p0, s0, (10, 80), s1), [p0, (10, 80)])   # aligned: straight
        self.assertEqual(diagram.route(p0, "top", p1, "left", via=[(40, 60)]),
                         [p0, (40, 20), (40, 60), (110, 60), p1])                # between via points: `via`
        self.assertEqual(d["via"], "L_X")
        self.assertEqual(sorted(self.prof["frame"]), ["cardsCanvas", "diagramCanvas", "faceplateDock", "topDock", "viewport"])

    # ---- 4. the cards page --------------------------------------------------------------
    def test_a_row_of_cards_is_as_high_as_its_content(self):
        c = self.contracts
        desc = json.loads((ROOT / "screens/wtp/overview.json").read_text(encoding="utf-8"))
        # fields of 64 px under a 40 px title, 8 px of padding and the 8 px margins; tanks of 216 px
        self.assertEqual([[screen.card_height(card, c) for card in row] for row in desc["rows"]],
                         [[112, 112], [264, 40 + 92 + 8]])
        self.assertEqual([screen.row_height(row, c) for row in desc["rows"]], [128, 280])
        doc, info = screen.build_screen(copy.deepcopy(desc), c)
        self.assertEqual(info["errors"], [])
        root = doc["root"]
        self.assertEqual([r["position"] for r in root["children"]],
                         [{"basis": "128px", "grow": 0, "shrink": 0}, {"basis": "280px", "grow": 0, "shrink": 0}])
        self.assertEqual(root["props"]["style"]["overflow"], "auto")             # rows taller than the viewport scroll
        nodes = view_nodes(doc)
        self.assertEqual((nodes["Card_Storage"]["position"], nodes["Card_Storage"]["props"]["style"]["margin"]),
                         ({"grow": 1, "basis": "0px"}, "8px"))                    # across the row as before
        self.assertEqual((nodes["Title"]["position"]["basis"], nodes["Body"]["props"]["style"]["padding"]),
                         ("40px", "0 8px 8px 8px"))

    def test_the_height_of_a_card_follows_the_flex_arithmetic(self):
        c = self.contracts
        pump = {"id": "P", "kind": "pump", "basis": "0px", "grow": 1, "params": {"hasTag": True, "tag": "P-1"}}
        field = {"id": "F", "kind": "instrument-field", "basis": "0px", "grow": 1, "params": {"label": "Flow"}}
        tall = {"id": "E", "kind": "instrument-field", "params": {"size": "enhanced", "hasSetpoint": True}}
        label = {"basis": "24px", "label": "Pumps"}
        self.assertEqual(screen.leaf_height(pump, c), 92)                        # the symbol and its readout
        self.assertEqual(screen.leaf_height(dict(pump, params={"readoutPosition": "right"}), c), 48)
        self.assertEqual((screen.leaf_height(field, c), screen.leaf_height(tall, c)), (64, 66))
        self.assertEqual(screen.leaf_height({"label": "x"}, c), 16)
        self.assertIsNone(screen.leaf_height({"id": "G", "kind": "compass"}, c))  # a gap box has no size of its own
        row = {"direction": "row", "items": [pump, field]}
        self.assertEqual(screen.group_height(row, c), 92)                        # across: the tallest
        col = {"direction": "column", "items": [label, dict(row, basis="0px", grow=1)]}
        self.assertEqual(screen.group_height(col, c), 24 + 4 + 92)               # down: the items and the gap
        # two groups that grow alike share the height: each gets what the taller needs
        two = {"direction": "column", "items": [dict(row, basis="0px", grow=1),
                                                {"direction": "row", "basis": "0px", "grow": 1, "items": [field]}]}
        self.assertEqual(screen.group_height(two, c), 4 + 2 * 92)
        self.assertEqual(screen.group_height({"direction": "column", "items": [tall, tall]}, c), 66 + 4 + 66)
        self.assertEqual(screen.group_height({"direction": "row", "items": []}, c), 0)
        card = {"id": "c", "title": "T", "body": {"direction": "row", "items": [
            dict(col, basis="0px", grow=1), {"direction": "column", "basis": "0px", "grow": 1, "items": [label, row]}]}}
        self.assertEqual(screen.card_height(card, c), 40 + 120 + 8)
        self.assertEqual(screen.card_height({"id": "c", "body": card["body"]}, c), 120 + 8)   # no title
        self.assertEqual(screen.card_height({"id": "c", "title": "T", "bodyWidth": 300, "bodyHeight": 150, "items": []}, c), 190)
        self.assertEqual(screen.row_height([card, card], c), 168 + 16)
        # one row: it stands at the top at its own height, where it took the whole viewport
        desc = {"screen": {"layout": "cards", "width": 1600, "height": 852}, "rows": [[card]]}
        doc, info = screen.build_screen(copy.deepcopy(desc), c)
        self.assertEqual((info["errors"], info["gaps"]), ([], []))
        self.assertEqual([r["position"] for r in doc["root"]["children"]], [{"basis": "184px", "grow": 0, "shrink": 0}])
        self.assertEqual(doc["root"]["props"]["style"]["overflow"], "auto")
        # a card with a gap box has no height of its own: its row shares the height left, as before
        gap = {"id": "g", "title": "G", "body": {"direction": "row", "items": [{"id": "G", "kind": "compass", "basis": "0px", "grow": 1}]}}
        self.assertIsNone(screen.card_height(gap, c))
        self.assertIsNone(screen.row_height([card, gap], c))
        desc = {"screen": {"layout": "cards", "width": 1600, "height": 852}, "rows": [[card], [card, gap]]}
        doc, info = screen.build_screen(copy.deepcopy(desc), c)
        self.assertEqual(len(info["gaps"]), 1)
        self.assertEqual([r["position"] for r in doc["root"]["children"]],
                         [{"basis": "184px", "grow": 0, "shrink": 0}, {"grow": 1, "basis": "0px"}])
        self.assertEqual(doc["root"]["props"]["style"]["overflow"], "hidden")

    # ---- 5. the warnings ----------------------------------------------------------------
    def build(self, d, desc, name="cadre_hmi_t"):
        from hmi import gates
        base = self.prj.write(Path(d))
        child, reports = screen.build_child(name, [desc], "T")
        out = child.write(Path(d))
        return out, base, reports, gates

    def test_g5_warns_of_a_block_too_small_for_what_it_shows(self):
        desc = copy.deepcopy(fixture("pilot-supply.json"))
        with tempfile.TemporaryDirectory() as d:
            out, _base, reports, gates = self.build(d, copy.deepcopy(desc))
            self.assertEqual(reports["/supply"]["errors"], [])
            res = gates.g5_layout(out)
            self.assertEqual((res["ok"], res["problems"], res["warnings"]), (True, [], []))   # the fixture: none
            syms = {s["id"]: s for s in desc["symbols"]}
            syms["FT1"].update(w=72, h=24)                                       # the default size, with its identifier:
            out, _base, _reports, gates = self.build(d, copy.deepcopy(desc))     # the generator grows it, so nothing
            self.assertEqual(gates.g5_layout(out)["warnings"], [])               # is cut and nothing is warned of
            syms["PIC1"]["params"]["tag"] = "HeaderPress_PIC1"
            syms["PIC1_PV"]["params"]["label"] = "Header pressure"               # with its unit: 19 characters
            syms["XV1"]["params"]["tag"] = "SupplyValve_XV01"                     # the generator widens its embed
            syms["XV1"]["x"] = 620                                               # as far as the readout beside it allows
            out, _base, reports, gates = self.build(d, desc)
            self.assertEqual(reports["/supply"]["errors"], [])
            res = gates.g5_layout(out)
            self.assertTrue(res["ok"])                                           # warnings fail nothing
            self.assertEqual(res["warnings"], [                                  # the two share the 16 px between them
                "Screens/PilotSupply: FT1 is 88 px wide and its tag of 15 characters needs 130 px: it ends in an ellipsis",
                "Screens/PilotSupply: XV1 is 88 px wide and its tag of 16 characters needs 136 px: it ends in an ellipsis",
                "Screens/PilotSupply: PIC1 is 120 px wide and its tag of 16 characters needs 162 px: it ends in an ellipsis",
                "Screens/PilotSupply: PIC1_PV is 96 px wide and its label of 19 characters needs 142.5 px: "
                "it ends in an ellipsis"])
            # a block the generator does not size: a box smaller than its flags need, a tank too narrow
            def block(path, w, h, **params):
                return {"meta": {"name": "B"}, "position": {"x": 0, "y": 0, "width": w, "height": h},
                        "props": {"path": path, "params": params}}
            warn = lambda *a, **k: gates.block_warnings("V", block(*a, **k), self.contracts)   # noqa: E731
            self.assertEqual(warn("Automation/Readout", 72, 24, hasTag=True, tag="FT-1"),
                             ["V: B is 72 x 24 px and needs 72 x 40 px with hasTag true"])
            self.assertEqual(warn("Instrument/Field", 96, 64, size="enhanced", hasSetpoint=True),
                             ["V: B is 96 x 64 px and needs 96 x 66 px with hasSetpoint true, size \"enhanced\""])
            self.assertEqual(warn("Automation/Tank", 168, 216, tag="RawWaterTank_T01"), [])
            self.assertEqual(warn("Automation/Tank", 120, 160, tag="RawWaterTank_T01"),   # 16 * 7.5 / 0.86
                             ["V: B is 120 px wide and its tag of 16 characters needs 139.535 px: it ends in an ellipsis"])
            self.assertEqual(warn("Automation/Tank", 120, 160, tag="RawWaterTank_T01", static=True), [])   # the whole width
            self.assertEqual(warn("Automation/Tank", 96, 80, tag="RawWaterTank_T01", static=True),
                             ["V: B is 96 px wide and its tag of 16 characters needs 120 px: it ends in an ellipsis"])
            self.assertEqual(warn("Automation/Pump", 136, 92, tag="SupplyPump_No0002"),       # 17: more than the library allows for
                             ["V: B is 136 px wide and its tag of 17 characters needs 144 px: it ends in an ellipsis"])
            self.assertEqual(warn("Automation/Pump", 136, 92, tag="SupplyPump_No002"), [])
            self.assertEqual(warn("Automation/Pump", 72, 92, tag="SupplyPump_No002", hasTag=False), [])
            self.assertEqual(warn("Automation/Pump", 48, 48, tag="SupplyPump_No002", readoutPosition="none"), [])
            self.assertEqual(warn("Automation/Pump", 48 + 100, 48, tag="SupplyPump_No002", readoutPosition="right"),
                             ["V: B is 148 px wide and its tag of 16 characters needs 184 px: it ends in an ellipsis"])

    def test_the_report_carries_the_warnings_of_every_gate(self):
        g = {"G5_layout": {"ok": True, "problems": [], "warnings": ["a overlaps b"], "pairs": 3},
             "G6_flow": {"ok": True, "routes": {}}, "ok": True}
        rec = screen.gate_record(g)
        self.assertEqual(rec, {"G5_layout": {"ok": True, "problems": [], "warnings": ["a overlaps b"], "pairs": 3},
                               "G6_flow": {"ok": True, "routes": {}, "warnings": []}, "ok": True})
        self.assertNotIn("warnings", g["G6_flow"])                               # the gates' own result is left alone
        self.assertEqual(screen.GATES_KEY, "gates")
        schema = json.loads((ROOT / "schemas/screen-descriptor.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["screen"]["properties"]["route"]["pattern"], "^/")   # never a route

    def test_the_generator_prints_and_records_the_warnings(self):
        import contextlib
        import io
        desc = copy.deepcopy(fixture("pilot-supply.json"))
        desc.pop("tagModel")
        syms = {s["id"]: s for s in desc["symbols"]}
        syms["PIC1"]["params"]["tag"] = "HeaderPress_PIC1"
        syms["PIC1_PV"]["params"]["label"] = "Header pressure"
        with tempfile.TemporaryDirectory() as d:
            self.prj.write(Path(d))
            src, rep = Path(d) / "page.json", Path(d) / "report.json"
            src.write_text(json.dumps(desc), encoding="utf-8")

            def run(*more):
                argv, printed = sys.argv, io.StringIO()
                sys.argv = ["screen.py", "--project", "cadre_hmi_t", "--descriptor", str(src), "--out", d,
                            "--report", str(rep), *more]
                try:
                    with contextlib.redirect_stdout(printed):
                        code = screen.main()
                finally:
                    sys.argv = argv
                    screen.RENDER["target"] = "stock"
                return code, printed.getvalue().splitlines()
            # the module's tank takes `hasCapacity` (0.3.0), so a static tank that states no capacity is drawn
            # by the module with no capacity line: no note, no invented number
            code, lines = run("--render", "module")
            self.assertEqual((code, [ln for ln in lines if ln.startswith("  note: ")]), (0, []))
            self.assertEqual(json.loads(rep.read_text(encoding="utf-8"))["/supply"]["notes"], [])
            self.assertNotIn("tank", screen.MODULE_EXCEPT)
            code, lines = run()
            self.assertEqual(code, 0)                                            # a warning fails nothing
            self.assertEqual([ln for ln in lines if ln.startswith("  note: ")], [])   # the library's own tank hides it
            self.assertEqual(json.loads(rep.read_text(encoding="utf-8"))["/supply"]["notes"], [])
            at = next(i for i, ln in enumerate(lines) if ln.startswith("  G5_layout"))
            self.assertEqual(lines[at].split(), ["G5_layout", "PASS"])
            self.assertEqual(lines[at + 1:at + 3], [
                "    warning: Screens/PilotSupply: PIC1 is 120 px wide and its tag of 16 characters needs 162 px: "
                "it ends in an ellipsis",
                "    warning: Screens/PilotSupply: PIC1_PV is 96 px wide and its label of 19 characters needs 142.5 px: "
                "it ends in an ellipsis"])
            report = json.loads(rep.read_text(encoding="utf-8"))
            self.assertEqual(sorted(report), ["/supply", "gates"])               # the routes, and the gates beside them
            gates_ = report["gates"]
            self.assertEqual(gates_["G5_layout"]["warnings"], [ln[len("    warning: "):] for ln in lines[at + 1:at + 3]])
            named = {k: v for k, v in gates_.items() if isinstance(v, dict)}
            self.assertEqual(sorted(named), ["G1_registry", "G1_registry_parent", "G2_references", "G3_view_keys",
                                             "G4_project", "G5_layout", "G6_flow", "G7_commands", "G7_contract",
                                             "G7_faceplates", "G7_history"])
            self.assertTrue(all(isinstance(v["warnings"], list) for v in named.values()))   # "no warning" in one read
            self.assertEqual([k for k, v in named.items() if v["warnings"]], ["G5_layout"])
            self.assertIs(gates_["ok"], True)
            # the gates script reads the same file as a screen report: the gates' key is no route
            from hmi import gates
            res = gates.run(Path(d) / "cadre_hmi_t", Path(d) / "cadre_hmi_base", rep)
            self.assertEqual((res["ok"], sorted(res["G6_flow"]["routes"])), (True, ["/supply"]))


class InstrumentModuleTests(unittest.TestCase):
    """Module 0.3.1 (COB-127): the library kinds `readout` and `instrument-field` are drawn by the module's
    `cadre.ob.readout` (obc-transmitter) and `cadre.ob.instrumentfield` (obc-instrument-field) wherever the
    element shows the symbol truthfully, and by the library's views elsewhere."""

    @classmethod
    def setUpClass(cls):
        from hmi import library_profile, parent as par
        cls.prj, cls.contracts = par.build_parent()
        cls.prof = library_profile.build(cls.contracts)

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def embed(self, sym, render="module", toolbar=True, limit=None):
        screen.RENDER["target"] = render
        try:
            rep = screen.Report()
            node, _custom, _cfg = screen.embed_symbol(sym, self.contracts, "[default]t", rep, toolbar=toolbar,
                                                      limit=limit)
            return node, rep.errors
        finally:
            screen.RENDER["target"] = "stock"

    def readout(self, **kw):
        return dict({"id": "R", "kind": "readout", "x": 100, "y": 50, "w": 72, "h": 24, "params": {}}, **kw)

    def field(self, **kw):
        return dict({"id": "F", "kind": "instrument-field", "x": 10, "y": 20, "w": 96, "h": 64, "params": {}}, **kw)

    # ---- 1. the number format -------------------------------------------------------------
    def test_a_number_format_pattern_becomes_a_digit_count_or_nothing(self):
        for pattern, digits in (("#,##0", 0), ("#,##0.0", 1), ("0.00", 2), ("0", 0), ("0.0", 1), ("#,##0.000", 3)):
            self.assertEqual((pattern, screen.fraction_digits(pattern)), (pattern, digits))
        # a pattern the element cannot print the same way: a percent, an exponent, literal text, an optional digit
        for pattern in ("0%", "#,##0.0%", "0.0E0", "#,##0 m3", "'T'0", "0.0#", "0.#", "", "#", "abc", None, 5):
            self.assertIsNone(screen.fraction_digits(pattern), pattern)

    # ---- 2. the readout --------------------------------------------------------------------
    def test_a_readout_is_the_modules_readout_in_the_box_the_library_gives_it(self):
        sym = self.readout(params={"unit": "m³/h", "format": "#,##0.0", "tag": "FT-101"},
                           bind={"value": "FIT101/value"})
        node, errors = self.embed(sym)
        self.assertEqual((node["type"], errors), ("cadre.ob.readout", []))
        # no tag shown (`hasTag` false): no identifier; the value is the tag's alone (GF-61); the digits stated
        self.assertEqual(node["props"], {"unit": "m³/h", "fractionDigits": 1})
        self.assertEqual(node["propConfig"]["props.value"]["binding"]["config"]["tagPath"], "[default]t/FIT101/value")
        pos = node["position"]
        self.assertEqual((pos["x"], pos["y"], pos["width"], pos["height"]), (100, 50, 72, 24))
        self.assertNotIn("positioning", node["props"])          # not a 48 px symbol: `symbol-centre` is its anchor
        self.assertNotIn("props.idTag", node.get("propConfig", {}))  # no identifier: nothing for the ID-tag button
        # with the identifier shown, the box grows as the library's does (`grown_box`), and the identifier lies
        # beneath the value in `idTag` (the transmitter's `tag` draws nothing in a value chip, measured)
        node, errors = self.embed(self.readout(params={"tag": "FT-101", "hasTag": True, "unit": "%"}), toolbar=False)
        pos = node["position"]
        self.assertEqual((node["props"]["idTag"], node["props"]["value"], errors), ("FT-101", 0, []))
        self.assertNotIn("tag", node["props"])
        self.assertEqual((pos["x"], pos["y"], pos["width"], pos["height"]), (100, 42, 72, 40))
        # under a toolbar the ID-tag button shows it: the text in the component's custom, nothing beside the binding
        node, errors = self.embed(self.readout(params={"tag": "FT-101", "hasTag": True, "unit": "%"}))
        self.assertEqual((node["custom"]["idText"], "idTag" in node["props"], errors), ("FT-101", False, []))
        self.assertEqual(node["propConfig"]["props.idTag"]["binding"]["config"]["expression"],
                         "if({view.custom.showTag} && true, {this.custom.idText}, '')")
        self.assertEqual(node["position"]["height"], 40)                          # the box keeps the identifier's room
        # a descriptor that states no format has the contract's: one digit
        node, _ = self.embed(self.readout(params={"tag": "FT-101"}))
        self.assertEqual(node["props"]["fractionDigits"], 1)
        # a limit the next symbol leaves (`embed_limits`) holds the identifier's width as for the library's view
        node, _ = self.embed(self.readout(params={"tag": "A-VERY-LONG-IDENTIFIER", "hasTag": True}), limit=0)
        self.assertEqual(node["position"]["width"], 72)

    def test_a_readout_stays_on_the_librarys_view_where_the_element_cannot_print_its_format(self):
        for fmt in ("0%", "0.0E0", "0.0 'm'"):
            node, errors = self.embed(self.readout(params={"format": fmt}))
            self.assertEqual((fmt, node["type"], errors), (fmt, "ia.display.view", []))
        for fmt, digits in (("#,##0", 0), ("0.00", 2)):
            node, _ = self.embed(self.readout(params={"format": fmt}))
            self.assertEqual((node["type"], node["props"]["fractionDigits"]), ("cadre.ob.readout", digits))
        node, _ = self.embed(self.readout(params={"format": "0%"}), render="stock")
        self.assertEqual(node["type"], "ia.display.view")

    # ---- 3. the instrument field -------------------------------------------------------------
    def test_a_field_is_the_modules_field_with_its_caption_as_the_elements_tag(self):
        sym = self.field(params={"label": "Raw water flow", "unit": "m³/h", "format": "#,##0.0",
                                 "source": "FIT-101", "tag": "FIT-101", "size": "regular"},
                         bind={"value": "FIT101/value"})
        node, errors = self.embed(sym, toolbar=False)
        self.assertEqual((node["type"], errors), ("cadre.ob.instrumentfield", []))
        # the label is the element's `tag` (its caption); the library's field draws no source nor identifier, so
        # the element draws neither; `align` end is the element's own, `format` is the digit count
        self.assertEqual(node["props"], {"tag": "Raw water flow", "unit": "m³/h", "size": "regular",
                                         "fractionDigits": 1})
        # under a toolbar the ID-tag button shows the label; the unit stays whichever way it stands
        node, errors = self.embed(sym)
        self.assertEqual((node["custom"]["idText"], "tag" in node["props"], node["props"]["unit"], errors),
                         ("Raw water flow", False, "m³/h", []))
        self.assertIn("{view.custom.showTag} && true", node["propConfig"]["props.tag"]["binding"]["config"]["expression"])
        # a field whose descriptor refuses its label draws the unit alone, with or without a toolbar
        node, _ = self.embed(self.field(params={"label": "Raw water flow", "unit": "m³/h", "hasTag": False}))
        self.assertEqual(("tag" in node["props"], "props.tag" in node.get("propConfig", {})), (False, False))
        node = self.embed(sym)[0]
        self.assertIn("props.value", node["propConfig"])
        pos = node["position"]
        self.assertEqual((pos["x"], pos["y"], pos["width"], pos["height"]), (10, 20, 96, 64))
        # the setpoint, centred; an unbound value is the contract's
        node, _ = self.embed(self.field(params={"label": "Level", "align": "center", "hasSetpoint": True,
                                                "setpoint": 55, "format": "0.0", "setpointFormat": "0.0"}))
        self.assertEqual(node["type"], "cadre.ob.instrumentfield")
        self.assertEqual((node["props"]["center"], node["props"]["hasSetpoint"], node["props"]["setpoint"],
                          node["props"]["value"], node["props"]["fractionDigits"]), (True, True, 55, 0, 1))
        # a bound setpoint is its binding alone
        node, _ = self.embed(self.field(params={"hasSetpoint": True}, bind={"setpoint": "H/sp"}))
        self.assertEqual(("setpoint" in node["props"], "props.setpoint" in node["propConfig"]), (False, True))
        # centre is stated only for a centred field
        node, _ = self.embed(self.field(params={"align": "end"}))
        self.assertNotIn("center", node["props"])

    def test_a_field_stays_on_the_librarys_view_where_the_element_cannot_draw_it(self):
        def drawn(**params):
            node, errors = self.embed(self.field(params=params))
            self.assertEqual(errors, [])
            return node["type"]
        # the element's rows end at the end of its box; `center` is its own, `start` is not drawn
        self.assertEqual((drawn(align="end"), drawn(align="center"), drawn(align="start")),
                         ("cadre.ob.instrumentfield", "cadre.ob.instrumentfield", "ia.display.view"))
        # one digit count for the value and the setpoint
        self.assertEqual(drawn(hasSetpoint=True, format="#,##0.0", setpointFormat="#,##0"), "ia.display.view")
        self.assertEqual(drawn(hasSetpoint=True, format="0.0", setpointFormat="#,##0.0"), "cadre.ob.instrumentfield")
        self.assertEqual(drawn(hasSetpoint=False, format="0.0", setpointFormat="0%"), "cadre.ob.instrumentfield")
        self.assertEqual(drawn(hasSetpoint=True, format="0.0", setpointFormat="0%"), "ia.display.view")
        self.assertEqual(drawn(format="0.0E0"), "ia.display.view")
        # the enhanced field with a setpoint is 6 px higher than the library's box (measured): not cut, but not
        # fitted either; the enhanced field alone fits
        self.assertEqual(drawn(size="enhanced", hasSetpoint=True), "ia.display.view")
        self.assertEqual(drawn(size="enhanced"), "cadre.ob.instrumentfield")
        self.assertEqual(drawn(size="regular", hasSetpoint=True), "cadre.ob.instrumentfield")

    def test_the_rules_are_published_in_the_library_profile_without_a_new_key(self):
        kinds = self.prof["kinds"]
        self.assertEqual(kinds["readout"]["module"], "cadre.ob.readout")
        self.assertEqual(kinds["instrument-field"]["module"], "cadre.ob.instrumentfield")
        self.assertEqual(kinds["instrument-field"]["moduleNeeds"], {"align": ["center", "end"]})
        self.assertEqual(kinds["instrument-field"]["moduleExcept"], [{"size": "enhanced", "hasSetpoint": True}])
        self.assertEqual(kinds["readout"]["moduleNeeds"], {})
        self.assertEqual(set(kinds["readout"]), set(kinds["pump"]))             # the shape of an entry is unchanged
        self.assertEqual(set(kinds["instrument-field"]), set(kinds["pump"]))
        for kind in ("readout", "instrument-field"):                            # and so are the sizes and the box
            view = screen.KIND_VIEW[kind]
            self.assertEqual((kinds[kind]["size"], kinds[kind]["sizes"], kinds[kind]["grows"]),
                             (self.contracts[view]["size"], self.contracts[view].get("sizes", []),
                              bool(self.contracts[view].get("grows", False))))

    # ---- 4. the click ----------------------------------------------------------------------
    def test_a_device_symbol_opens_the_faceplate_of_the_kind_its_device_kind_names(self):
        def click(node):
            return node["custom"], node["events"]["dom"]["onClick"]["config"]["script"]
        node, _ = self.embed(self.readout(params={"tag": "FT-101", "hasTag": True}, device="FIT101", label="Raw flow"))
        custom, script = click(node)
        self.assertEqual((custom["deviceId"], custom["deviceKind"], custom["title"], custom["label"]),
                         ("[default]t/FIT101", "instrument", "FT-101", "Raw flow"))
        self.assertIn("select_device(self.session, self.custom.deviceId, self.custom.deviceKind", script)
        self.assertIn("openDock(id='faceplate')", script)
        # a controller's process value names the controller
        node, _ = self.embed(self.readout(params={"deviceKind": "controller"}, device="PIC1"))
        self.assertEqual(click(node)[0]["deviceKind"], "controller")
        # a field has no identifier of its own: it is titled with the tag, else the label, as the library's
        node, _ = self.embed(self.field(params={"label": "Raw water flow", "unit": "m3/h"}, device="FIT101"))
        self.assertEqual((click(node)[0]["deviceKind"], click(node)[0]["title"]), ("instrument", "Raw water flow"))
        node, _ = self.embed(self.field(params={"label": "Raw water flow", "tag": "FIT-101"}, device="FIT101"))
        self.assertEqual(click(node)[0]["title"], "FIT-101")
        node, _ = self.embed(self.field(params={"label": "Flow"}))
        self.assertNotIn("events", node)                                        # no device: no click

    # ---- 5. the schema --------------------------------------------------------------------------
    def test_every_property_the_generator_passes_is_in_the_components_schema(self):
        comps = json.loads((ROOT / "module/components.json").read_text(encoding="utf-8"))
        rich = {"readout": self.readout(params={"unit": "%", "format": "0.00", "tag": "T-1", "hasTag": True,
                                                "label": "L", "value": 4.5}, device="X", label="Lbl"),
                "instrument-field": self.field(params={"label": "L", "unit": "u", "format": "0.0", "align": "center",
                                                       "hasSetpoint": True, "setpoint": 3, "setpointFormat": "0.0",
                                                       "size": "regular", "source": "S", "tag": "T", "value": 2},
                                               device="X", label="Lbl")}
        for kind, sym in rich.items():
            node, errors = self.embed(sym)
            self.assertEqual((kind, node["type"], errors), (kind, screen.MODULE_KIND[kind], []))
            have = comps[node["type"]]["props"]
            self.assertEqual(set(node["props"]) - set(have), set(), kind)
            bound = {k[len("props."):] for k in node.get("propConfig", {})}
            self.assertEqual(bound - set(have), set(), kind)
            for k, v in node["props"].items():                                  # a value of the schema's own type
                spec = have[k]
                if "enum" in spec:
                    self.assertIn(v, spec["enum"], k)
                kinds = spec["type"] if isinstance(spec["type"], list) else [spec["type"]]
                names = {"string": str, "boolean": bool, "number": (int, float)}
                self.assertTrue(any(isinstance(v, names[t]) for t in kinds if t in names), (kind, k, v))

    # ---- 6. a build ------------------------------------------------------------------------------
    def test_the_water_treatment_sample_draws_its_readouts_and_fields_with_the_module(self):
        descs = [json.loads((ROOT / "screens/wtp" / f"{n}.json").read_text(encoding="utf-8"))
                 for n in ("overview", "intake", "filtration", "disinfection")]
        count = {}

        def walk(render, n):
            if n.get("type") in ("cadre.ob.readout", "cadre.ob.instrumentfield"):
                count[(render, n["type"])] = count.get((render, n["type"]), 0) + 1
            path = (n.get("props") or {}).get("path")
            if path in ("Automation/Readout", "Instrument/Field"):
                count[(render, path)] = count.get((render, path), 0) + 1
            for c in n.get("children") or []:
                walk(render, c)
        for render in ("stock", "module"):
            child, reports = screen.build_child("cadre_hmi_t", descs, "T", render=render)
            self.assertEqual([r for rep in reports.values() for r in rep["errors"]], [])
            for name, doc in child.files.items():
                if name.endswith("view.json"):
                    walk(render, json.loads(doc)["root"])
        self.assertFalse([k for k in count if k[0] == "stock" and k[1].startswith("cadre.")])
        self.assertTrue(count[("module", "cadre.ob.readout")] > 0 and count[("module", "cadre.ob.instrumentfield")] > 0)
        # a kind is drawn by one or the other, never both nor neither
        for lib, mod in (("Automation/Readout", "cadre.ob.readout"), ("Instrument/Field", "cadre.ob.instrumentfield")):
            self.assertEqual(count[("stock", lib)], count.get(("module", lib), 0) + count[("module", mod)], lib)

    # ---- 7. review findings of 0.3.1 ----------------------------------------------------------------
    def test_a_field_in_a_box_shorter_than_its_element_stays_on_the_librarys_view(self):
        def drawn(h, **params):
            node, errors = self.embed(self.field(h=h, params=params))
            self.assertEqual(errors, [])
            return node["type"]
        mod, lib = "cadre.ob.instrumentfield", "ia.display.view"
        # regular, 40 px: the box may be 4 px short
        self.assertEqual((drawn(32), drawn(36), drawn(64)), (lib, mod, mod))
        # regular with a setpoint, 60 px
        self.assertEqual((drawn(48, hasSetpoint=True), drawn(55, hasSetpoint=True), drawn(56, hasSetpoint=True)),
                         (lib, lib, mod))
        # enhanced, 52 px
        self.assertEqual((drawn(47, size="enhanced"), drawn(48, size="enhanced")), (lib, mod))
        # the module's profile shape is unchanged: the rule is not published
        self.assertEqual(set(self.prof["kinds"]["instrument-field"]), set(self.prof["kinds"]["pump"]))

    def test_a_readout_is_never_shorter_than_its_element_allows(self):
        # the generator grows a readout's box to the library's size (24, or 40 with an identifier), which is within
        # 4 px of the chip (26, or 44): the same rule never takes a readout from the module
        for h in (10, 24):
            node, _ = self.embed(self.readout(h=h, params={"hasTag": True, "tag": "FT-1"}))
            self.assertEqual((node["type"], node["position"]["height"]), ("cadre.ob.readout", 40))
        self.assertEqual(screen.module_height("readout", {"hasTag": True}), 44)
        self.assertEqual(screen.module_height("readout", {}), 26)
        self.assertFalse(screen.module_draws("readout", {}, target="module", height=21))
        self.assertTrue(screen.module_draws("readout", {}, target="module", height=22))

    def test_a_symbol_in_a_card_has_no_box_to_compare(self):
        # a card lays its items out (a flex item, the generator gives it a box of 0 x 0): the module draws it
        screen.RENDER["target"] = "module"
        try:
            rep = screen.Report()
            node, _c, _cfg = screen.embed_symbol(self.field(h=0), self.contracts, "[default]t", rep, toolbar=False,
                                                 pos=screen.pv.fpos(shrink=0))
            self.assertEqual(node["type"], "cadre.ob.instrumentfield")
        finally:
            screen.RENDER["target"] = "stock"

    def test_the_stylesheet_defines_what_the_elements_read_from_html(self):
        css = (ROOT / "module/gateway/src/main/resources/mounted/css/cadre-ob.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.cadre-ob[^{}]*\{[^{}]*--obc-can-hover: 1;")

    def test_the_module_names_the_components_it_carries(self):
        text = (ROOT / "module/build.gradle.kts").read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if "moduleDescription" in ln)
        for word in ("pump", "tank", "motor", "fan", "valve", "readout", "instrument field", "alert list"):
            self.assertIn(word, line, word)


class FrameMenuTests(unittest.TestCase):
    """The top bar's menus and the navigation menu close on a click outside them and from a close button
    (owner's report of 2026-10-22: the alert menu and the navigation menu stayed open)."""

    def scripts(self, node, out=None):
        """Every event script of a tree of components, by component name."""
        out = {} if out is None else out
        for scope in node.get("events", {}).values():
            for ev in scope.values():
                out.setdefault(node["meta"]["name"], []).append(ev["config"].get("script", ""))
        for n in node.get("children", []):
            self.scripts(n, out)
        return out

    def test_the_top_bar_menus_close_on_a_click_outside(self):
        from hmi import framework
        found = {}
        for name, lines in self.scripts(framework.top_bar()["root"]).items():
            for s in lines:
                for m in re.finditer(r"openPopup\('(\w+)'.*?\)$", s, re.M):
                    found[m.group(1)] = m.group(0)
        self.assertEqual(sorted(found), ["alertMenu", "brilliance", "userMenu"])
        for pid, call in found.items():
            self.assertIn("modal=True", call, pid)
            self.assertIn("overlayDismiss=True", call, pid)

    def test_the_menus_have_a_close_button(self):
        from hmi import framework
        for view, close in ((framework.alert_menu(), "closePopup('alertMenu')"),
                            (framework.alert_menu_module(), "closePopup('alertMenu')"),
                            (framework.nav_menu(), "closeDock('nav')")):
            head = view["root"]["children"][0]
            self.assertEqual(head["meta"]["name"], "Header")
            self.assertIn(close, self.scripts(head)["Close"][0])

    def test_the_navigation_dock_is_modal_and_the_faceplate_dock_is_not(self):
        from hmi import framework
        docks = framework.shared_docks()
        self.assertTrue(docks["left"][0]["modal"])
        self.assertFalse(docks["right"][0]["modal"])
        self.assertFalse(docks["top"][0]["modal"])


class ToolbarTests(unittest.TestCase):
    """The diagram toolbar reaches every symbol it names (owner's report of 2026-10-22: Readout left the module's
    devices as they were, and Color changed nothing on a page whose pipes name no medium)."""

    def setUp(self):
        self.desc = json.loads((ROOT / "screens/wtp/filtration.json").read_text(encoding="utf-8"))

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def nodes(self, desc, render="module"):
        child, _ = screen.build_child("cadre_hmi_t", [desc], "T", render=render)
        view = json.loads(child.files[f"com.inductiveautomation.perspective/views/{desc['screen']['view']}/view.json"])
        out = {}

        def walk(n):
            out[n.get("meta", {}).get("name")] = n
            for c in n.get("children") or []:
                walk(c)
        walk(view["root"])
        return out

    def test_readout_binds_the_state_readout_of_every_automation_symbol(self):
        nodes = self.nodes(self.desc)
        symbols = [s for s in self.desc["symbols"] if s["kind"] in ("pump", "valve", "filter")]
        kinds = set()
        for s in symbols:
            n = nodes[s["id"]]
            kinds.add(n["type"])
            key = "props.showStatus" if n["type"].startswith("cadre.ob.") else "props.params.showStatus"
            self.assertEqual(n["propConfig"][key]["binding"]["config"]["expression"], "{view.custom.showReadout} && true",
                             s["id"])
            # no value beside the binding (GF-61)
            self.assertNotIn("showStatus", n["props"].get("params", n["props"]), s["id"])
        self.assertEqual(kinds, {"cadre.ob.pump", "cadre.ob.valve", "cadre.ob.filter"})   # module and library alike
        # a symbol whose descriptor refuses its state readout keeps it hidden whichever way the button stands
        desc = copy.deepcopy(self.desc)
        next(s for s in desc["symbols"] if s["id"] == "P301")["params"]["showStatus"] = False
        self.assertEqual(self.nodes(desc)["P301"]["propConfig"]["props.showStatus"]["binding"]["config"]["expression"],
                         "{view.custom.showReadout} && false")

    def test_every_automation_component_of_the_module_has_show_status(self):
        comps = json.loads((ROOT / "module/components.json").read_text(encoding="utf-8"))
        for ctype in ("cadre.ob.pump", "cadre.ob.motor", "cadre.ob.fan", "cadre.ob.valve", "cadre.ob.analogvalve"):
            self.assertEqual(comps[ctype]["props"]["showStatus"], {"type": "boolean", "default": True}, ctype)
        js = (ROOT / "module/gateway/src/main/resources/mounted/js/cadre-ob.js").read_text(encoding="utf-8")
        self.assertIn('{"name":"showStatus","kind":"boolean","def":true}', js)   # the wrapper sets it on the element

    def test_id_tag_binds_the_identifier_of_tanks_readouts_and_fields(self):
        intake = json.loads((ROOT / "screens/wtp/intake.json").read_text(encoding="utf-8"))
        on = "{view.custom.showTag} && true"
        # the module's elements: the text in the component's custom, the property bound, nothing stated beside it
        nodes = self.nodes(intake)
        for sid, ident, text in (("TK101", "tag", "TK-101"), ("CL201", "tag", "CL-201"), ("FIT101", "idTag", "FIT-101"),
                                 ("P101", "tag", "P-101")):
            n = nodes[sid]
            self.assertTrue(n["type"].startswith("cadre.ob."), sid)
            self.assertEqual((n["custom"]["idText"], ident in n["props"]), (text, False), sid)
            self.assertEqual(n["propConfig"][f"props.{ident}"]["binding"]["config"]["expression"],
                             f"if({on}, {{this.custom.idText}}, '')", sid)
        # the library's views: the `hasTag` flag bound, as for an automation symbol
        nodes = self.nodes(intake, render="stock")
        for sid in ("TK101", "CL201", "FIT101", "P101"):
            self.assertEqual(nodes[sid]["propConfig"]["props.params.hasTag"]["binding"]["config"]["expression"], on, sid)
            self.assertNotIn("hasTag", nodes[sid]["props"]["params"], sid)
        # a field on a diagram, both renderings; a controller and a sequence keep their names (no binding)
        desc = copy.deepcopy(intake)
        desc["symbols"].append({"id": "FF1", "kind": "instrument-field", "x": 600, "y": 400, "w": 96, "h": 64,
                                "params": {"label": "Raw flow", "unit": "m³/h", "format": "0.0"}})
        desc["symbols"].append({"id": "SQ1", "kind": "sequence", "x": 600, "y": 480, "w": 144, "h": 72,
                                "params": {"tag": "SQ-1"}})
        mod, stock = self.nodes(desc), self.nodes(desc, render="stock")
        self.assertEqual((mod["FF1"]["type"], mod["FF1"]["custom"]["idText"]), ("cadre.ob.instrumentfield", "Raw flow"))
        self.assertEqual(stock["FF1"]["propConfig"]["props.params.hasTag"]["binding"]["config"]["expression"], on)
        self.assertNotIn("props.params.hasTag", stock["SQ1"].get("propConfig") or {})
        # the walk finds none of them on a diagram whose ID-tag button starts off, by the generator's own start rule:
        # off where the descriptor states no `showTags`, on where it has no toolbar
        sys.path.insert(0, str(ROOT / "tools" / "compare"))           # as tests/test_walk.py imports it
        import walk_plan
        station = json.loads((ROOT / "screens/sample-pump-station.json").read_text(encoding="utf-8"))
        unstated = {k: v for k, v in station.items() if k != "showTags"}
        self.assertEqual((screen.tags_shown_at_start(station), screen.tags_shown_at_start(unstated),
                          screen.tags_shown_at_start({"toolbar": False})), (True, False, True))
        for desc, found in ((station, True), (unstated, False)):
            plan = {s["id"]: s["find"] for s in walk_plan._symbols([desc], screen.load_contracts(), "stock")}
            self.assertEqual({sid: plan[sid] is not None for sid in ("T101", "T102")}, {"T101": found, "T102": found})
        for kind, params in (("tank", {"tag": "TK-1"}), ("readout", {"tag": "FT-1", "hasTag": True}),
                             ("instrument-field", {"label": "Flow", "unit": "m³/h"})):
            self.assertIsNotNone(walk_plan.find_text(kind, params, True), kind)
            self.assertIsNone(walk_plan.find_text(kind, params, False), kind)

    def test_color_is_drawn_only_where_a_pipe_names_a_medium(self):
        def buttons(desc):
            return [n["meta"]["name"] for n in self.nodes(desc)["UserToolbar"]["children"]]
        self.assertEqual(buttons(self.desc), ["Color", "IdTag", "Readout", "Zoom"])   # the zoom controls on every diagram
        plain = copy.deepcopy(self.desc)
        for p in plain["pipes"]:
            p.pop("medium", None)
        self.assertEqual(buttons(plain), ["IdTag", "Readout", "Zoom"])
        # the sample's dosing lines name none and stay neutral; its water and sludge lines take their colour
        intake = json.loads((ROOT / "screens/wtp/intake.json").read_text(encoding="utf-8"))
        media = {p["id"]: p.get("medium") for p in intake["pipes"]}
        self.assertEqual((media["p1"], media["p6"], media["p12"]), ("fresh-water", None, "waste"))
class OwnershipTests(unittest.TestCase):
    """Ownership by mode (COBD-044, the ASMP study's F005 option B): a device model may give a device
    its modes and their owners; the checked writes refuse what the owner does not allow, `device_read`
    says who holds the device and why a command is disabled, and the faceplate moves ownership through
    W2 behind a confirmation. A device without modes keeps the rules it had."""

    D = "[default]t/P1"
    MODES = [{"value": 0, "name": "Auto", "owner": "program"}, {"value": 1, "name": "Manual", "owner": "operator"},
             {"value": 2, "name": "Maintenance", "owner": "maintenance"}, {"value": 3, "name": "Local", "owner": "local"}]

    def ns_at(self, mode, modes=True):
        tags = {f"{self.D}/{m}": v for m, v in (("mode", mode), ("cmd", False), ("fault", True), ("speedSp", 0.0),
                                                ("mnt/forceOn", False), ("mnt/forceOff", False))}
        entry = {"folder": self.D, "title": "P-1", **({"modes": self.MODES} if modes else {})}
        ns, calls = hmi_ns(tags)
        return ns, calls, session(["Administrator"], [entry])

    def writes(self, calls):
        return [c for c in calls if c[0] == "write"]

    def test_the_checked_writes_follow_the_owner(self):
        ns, calls, admin = self.ns_at(0)                                   # Auto: the program holds the device
        for path, member, value in (("W1", "cmd", True), ("W3", "speedSp", 50.0), ("W5", "fault", False)):
            self.assertEqual(ns["command"](admin, path, self.D, member, value), "Refused: P-1 is owned by the program (Auto)")
        self.assertEqual(ns["force"](admin, self.D, "on"), "Refused: P-1 is owned by the program (Auto)")
        self.assertEqual(self.writes(calls), [])
        ns, calls, admin = self.ns_at(1)                                   # Manual: the operator holds it
        self.assertEqual(ns["command"](admin, "W1", self.D, "cmd", True), "")
        self.assertEqual(ns["command"](admin, "W3", self.D, "speedSp", 50.0), "")
        self.assertEqual(ns["force"](admin, self.D, "on"), "Refused: P-1 is owned by the operator (Manual)")
        self.assertEqual(len(self.writes(calls)), 2)
        ns, calls, admin = self.ns_at(2)                                   # Maintenance may force
        self.assertEqual(ns["force"](admin, self.D, "on"), "")
        ns, calls, admin = self.ns_at(3)                                   # the local station holds it
        self.assertEqual(ns["command"](admin, "W1", self.D, "cmd", True), "Refused: P-1 is owned by the local station (Local)")
        self.assertEqual(ns["command"](admin, "W2", self.D, "mode", 1), "Refused: P-1 is held by the local station (Local)")
        self.assertEqual(self.writes(calls), [])
        ns, calls, admin = self.ns_at(9)                                   # a value that is no mode of the device
        self.assertEqual(ns["command"](admin, "W1", self.D, "cmd", True), "Refused: the mode of P-1 is not one of its modes")
        self.assertEqual(ns["command"](admin, "W2", self.D, "mode", 1), "Refused: the mode of P-1 is not one of its modes")
        # a device without modes keeps the rules of its write paths alone
        ns, calls, admin = self.ns_at(0, modes=False)
        self.assertEqual(ns["command"](admin, "W1", self.D, "cmd", True), "")
        self.assertEqual(ns["force"](admin, self.D, "on"), "")

    def test_the_mode_command_moves_ownership_and_nothing_else(self):
        ns, calls, admin = self.ns_at(0)
        self.assertEqual(ns["command"](admin, "W2", self.D, "mode", 1), "")      # Take control
        self.assertEqual(self.writes(calls)[-1][1:], ([f"{self.D}/mode"], [1]))
        for bad in (3, 7, True, "1", 1.5):                                      # local, unknown, not a whole number
            self.assertTrue(ns["command"](admin, "W2", self.D, "mode", bad).startswith("Refused: "), bad)
        self.assertEqual(len(self.writes(calls)), 1)
        self.assertEqual(ns["command"](admin, "W2", self.D, "mode", 0), "")      # Release, from Manual
        anon = session(None, [{"folder": self.D, "modes": self.MODES}])
        self.assertEqual(ns["command"](anon, "W2", self.D, "mode", 1), ns["REFUSED"])   # the role still comes first

    def test_device_read_says_who_holds_the_device(self):
        from hmi import framework, scripts
        read = lambda ns, s: ns["device_read"](s, self.D, ["mode", "cmd", "state", "fault"])
        ns, _, admin = self.ns_at(0)
        got = read(ns, admin)
        self.assertEqual((got["owned"], got["owner"]), (True, {"name": "Auto", "owner": "program", "text": "Program"}))
        self.assertEqual(got["reason"], "Owned by the program (Auto)")
        self.assertFalse(any(got["allowed"].values()))
        self.assertEqual(got["take"], {"offered": True, "value": 1, "name": "Manual"})
        self.assertFalse(got["release"]["offered"] or got["maintain"]["offered"])
        ns, _, admin = self.ns_at(1)
        got = read(ns, admin)
        self.assertEqual((got["reason"], got["allowed"]["W1"], got["allowed"]["W16"]), ("", True, False))
        self.assertEqual((got["take"]["offered"], got["release"], got["maintain"]),
                         (False, {"offered": True, "value": 0, "name": "Auto"},
                          {"offered": True, "value": 2, "name": "Maintenance"}))
        ns, _, admin = self.ns_at(2)
        got = read(ns, admin)
        self.assertEqual((got["take"]["value"], got["release"]["value"], got["allowed"]["W16"]), (1, 0, True))
        ns, _, admin = self.ns_at(3)
        got = read(ns, admin)
        self.assertEqual(got["reason"], "Owned by the local station (Local)")
        self.assertFalse(any(m["offered"] for m in (got["take"], got["release"], got["maintain"])))
        # without modes: the default of the faceplate, every gated path allowed
        ns, _, admin = self.ns_at(0, modes=False)
        got = read(ns, admin)
        self.assertEqual({k: got[k] for k in framework.ownership_default()}, framework.ownership_default())

    def model_with_modes(self, modes=None):
        model = copy.deepcopy(fixture("pilot-devices.json"))
        p1 = next(d for d in model["devices"] if d["id"].endswith("P1"))
        p1["members"]["mode"] = {"type": "Int4", "access": "write"}
        p1["modes"] = copy.deepcopy(self.MODES if modes is None else modes)
        return model, p1

    def test_the_device_index_the_schema_and_gate_g7(self):
        from hmi import framework, scripts
        from hmi import gates, library_profile
        model, p1 = self.model_with_modes()
        self.assertEqual(screen.devices_schema_errors(model, "m"), [])
        entry = next(e for e in screen.device_index([fixture("pilot-supply.json")], model) if e["folder"].endswith("/P1"))
        self.assertEqual(entry["modes"], self.MODES)
        schema = json.loads((ROOT / "schemas" / "devices.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$defs"]["device"]["properties"]["modes"]["items"]["properties"]["owner"]["enum"],
                         scripts.constant("OWNERS"))
        profile = library_profile.build(screen.load_contracts())
        self.assertEqual(profile["ownership"]["paths"], scripts.constant("OWNER_PATHS"))
        symbols = screen.device_symbols([fixture("pilot-supply.json")])
        self.assertEqual(gates.g7_devices(model, profile, symbols)["problems"], [])
        for change, text in ((lambda d: d["members"].pop("mode"), "lists no member 'mode'"),
                             (lambda d: d["members"]["mode"].update(type="Boolean"), "a mode is a whole number"),
                             (lambda d: d["modes"].append({"value": 0, "name": "Again", "owner": "program"}),
                              "a mode value is given twice"),
                             (lambda d: d["modes"][0].update(owner="sequence"), "names owner 'sequence'")):
            m, d = self.model_with_modes()
            change(d)
            probs = gates.g7_devices(m, profile, symbols)["problems"]
            self.assertTrue(any(text in p for p in probs), (text, probs))
        m, d = self.model_with_modes([{"value": 0, "name": "Auto", "owner": "program"}])
        res = gates.g7_devices(m, profile, symbols)
        self.assertEqual(res["problems"], [])
        self.assertTrue(any("offers no Take control" in w for w in res["warnings"]), res["warnings"])

    def test_the_faceplate_moves_ownership_behind_a_confirm(self):
        from hmi import framework, scripts
        from hmi import gates, parent as par
        doc = framework.framework_views()["Faceplate/Pump"]
        nodes = view_nodes(doc)
        expr = lambda n, k: nodes[n]["propConfig"][k]["binding"]["config"]["expression"]
        for key in ("take", "release", "maintain"):
            self.assertEqual(expr(f"Move_{key}", "position.display"), f"{{view.custom.dev.{key}.offered}}")
            self.assertNotIn("cadre.hmi", json.dumps(nodes[f"Move_{key}"].get("events")))   # a move writes nothing
        # the move asks W2 of the mode it offers, through the faceplate's shared Confirm row (F029)
        self.assertIn("'path': 'W2', 'member': 'mode', 'value': m.value", json.dumps(nodes["Move_take"]["events"]))
        self.assertIn("cadre.hmi.command(self.session, p.path", json.dumps(nodes["ConfirmYes"]["events"]))
        self.assertIn("'W2', {view.custom.can.W2}", expr("ConfirmYes", "props.enabled"))
        self.assertIn("{view.custom.pending.device} = {view.params.deviceId}", expr("Confirm", "position.display"))
        self.assertIn("!{view.custom.dev.owned}", expr("Modes", "position.display"))       # the old buttons step aside
        self.assertTrue(expr("On", "props.enabled").endswith("&& {view.custom.dev.allowed.W1}"))
        self.assertEqual(doc["custom"]["pending"], framework.PENDING_DEFAULT)
        self.assertIn(f"self.custom.pending = {framework.PENDING_DEFAULT!r}", json.dumps(doc))
        with tempfile.TemporaryDirectory() as d:                         # gate G7 commands passes on the parent
            prj, _ = par.build_parent()
            res = gates.g7_commands(prj.write(Path(d)), None)
            self.assertTrue(res["ok"], res["problems"])


class FaceplateStyleTests(unittest.TestCase):
    """The faceplate style (COBD-045): `openbridge`, the default, or `asm`, the anatomy of the ASMP
    study, chosen per device by the device model or for the project by `screen.py --faceplate`. The
    dock opens the view of the selected device's kind and style; a kind without an `asm` view keeps
    its `openbridge` faceplate."""

    D = "[default]t/P1"

    def test_select_device_writes_the_style(self):
        from hmi import scripts
        ns, _ = hmi_ns({})
        for entry, default, want in (({"faceplate": "asm"}, None, "asm"), ({}, "asm", "asm"),
                                     ({"faceplate": "openbridge"}, "asm", "openbridge"), ({}, None, "openbridge"),
                                     ({"faceplate": "fancy"}, "fancy", "openbridge")):
            s = session(["Administrator"], [{"folder": self.D, **entry}])
            if default is not None:
                s.custom.faceplateStyle = default
            ns["select_device"](s, self.D, "pump", "P-1")
            self.assertEqual((s.custom.selectedStyle, s.custom.selectedKind, s.custom.selectedTitle), (want, "pump", "P-1"))
        self.assertEqual(scripts.constant("FACEPLATE_STYLES"), ["openbridge", "asm"])

    def test_the_dock_opens_the_view_of_the_kind_and_the_style(self):
        from hmi import framework, parent as par
        self.assertEqual(view_nodes(framework.side_menu())["Faceplate"]["propConfig"]["props.path"]["binding"]["config"]
                         ["expression"], framework.FACEPLATE_OF_SELECTION)
        for kind, style, want in (("pump", "asm", "Faceplate/ASM/Pump"), ("fan", "asm", "Faceplate/ASM/Pump"),
                                  ("damper", "asm", "Faceplate/ASM/Valve"), ("tank", "asm", "Faceplate/Tank"),
                                  ("pump", "openbridge", "Faceplate/Pump"), ("nothing", "asm", "")):
            self.assertEqual(framework.faceplate_view(kind, style), want)
        views = framework.framework_views()
        self.assertTrue(set(framework.ASM_VIEW.values()) <= set(views))
        self.assertEqual(par.session_defaults()["custom"]["selectedStyle"], "openbridge")
        self.assertEqual(par.session_defaults()["custom"]["faceplateStyle"], "openbridge")

    def test_the_asm_anatomy_holds_the_openbridge_rows(self):
        from hmi import framework, gates, parent as par
        views = framework.framework_views()
        for kind in ("pump", "valve"):
            doc = views[framework.ASM_VIEW[kind]]
            nodes = view_nodes(doc)
            expr = lambda n, k: nodes[n]["propConfig"][k]["binding"]["config"]["expression"]
            self.assertEqual([c["meta"]["name"] for c in doc["root"]["children"][:3]], ["Header", "Tabs", "Quality"])
            self.assertEqual([c["meta"]["name"] for c in nodes["Tabs"]["children"]],
                             ["Tab_" + k for k, _ in framework.ASM_TABS])
            self.assertEqual(nodes["Tabs"]["props"]["wrap"], "wrap")
            self.assertTrue(expr("Tab_interlocks", "props.text").startswith("'Interlock' + "))
            self.assertEqual(expr("Tab_config", "position.display"), "{view.custom.dev.mnt} || {view.custom.dev.config} > 0")
            self.assertEqual(doc["custom"]["tab"], "home")
            # the Home tab holds every row of the openbridge Control tab
            ob = view_nodes(views[framework.FACEPLATE_VIEW[kind]])
            under = lambda ns, pane: {n["meta"]["name"] for n, _ in gates.walk(ns[pane])}
            self.assertEqual(under(nodes, "Pane_home"), under(ob, "Pane_control") - {"Pane_control"} | {"Pane_home"})
            self.assertTrue({"ForceOn", "MaskOn"} <= under(nodes, "Pane_config"))
            self.assertEqual(nodes["DiagStatus0Label"]["props"]["text"], "state")
            self.assertEqual(expr("DiagStatus0Value", "props.text"), "toStr({view.custom.dev.value.state})")
            self.assertTrue({"InfoNameRow", "InfoFolderRow", "InfoOwnerRow", "InfoSources"} <= under(nodes, "Pane_info"))
            self.assertEqual(expr("HeadInterlock", "position.display"), framework.ILK_HELD)
        with tempfile.TemporaryDirectory() as d:   # gates G7 faceplates and commands pass on the parent
            base = par.build_parent()[0].write(Path(d))
            res = gates.g7_faceplates(base, None)
            self.assertTrue(res["ok"], res["problems"])
            self.assertEqual(res["tabs"]["Faceplate/ASM/Valve"], [k for k, _ in framework.ASM_TABS])
            self.assertTrue(gates.g7_commands(base, None)["ok"])

    def test_the_model_the_index_the_profile_and_gate_g7(self):
        from hmi import framework, gates, library_profile
        model = copy.deepcopy(fixture("pilot-devices.json"))
        by_id = {d["id"]: d for d in model["devices"]}
        by_id["XV1"]["faceplate"] = "asm"
        by_id["FT1"]["faceplate"] = "asm"            # an instrument has no asm faceplate
        self.assertEqual(screen.devices_schema_errors(model, "m"), [])
        index = {e["folder"].split("/")[-1]: e for e in screen.device_index([fixture("pilot-supply.json")], model)}
        self.assertEqual((index["XV1"]["faceplate"], "faceplate" in index["P1"]), ("asm", False))
        bad = copy.deepcopy(model)
        bad["devices"][0]["faceplate"] = "fancy"
        self.assertTrue(screen.devices_schema_errors(bad, "m"))
        profile = library_profile.build(screen.load_contracts())
        self.assertEqual(profile["deviceKinds"]["valve"]["faceplates"], {"openbridge": "Faceplate/Valve", "asm": "Faceplate/ASM/Valve"})
        self.assertEqual(profile["deviceKinds"]["tank"]["faceplates"]["asm"], "Faceplate/Tank")
        self.assertEqual(profile["faceplates"]["Faceplate/ASM/Pump"]["tabs"], [k for k, _ in framework.ASM_TABS])
        res = gates.g7_devices(model, profile, screen.device_symbols([fixture("pilot-supply.json")]))
        self.assertEqual(res["problems"], [])
        self.assertEqual([w for w in res["warnings"] if "asm style" in w], [])   # an instrument has one since COB-158
        for style in ("openbridge", "asm"):          # the project's default reaches every session
            child, _ = screen.build_child("cadre_hmi_t", [fixture("pilot-supply.json")], "T", faceplate=style)
            sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
            self.assertEqual(sp["custom"]["faceplateStyle"], style)

    def test_the_sweep_expects_the_tabs_of_the_style(self):
        from hmi import framework, scripts
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import faceplates
        valve = ["state", "fault", "ilk/permit", scripts.constant("MNT_MASK")]
        self.assertEqual(framework.expected_tabs("valve", valve, (), "asm"),
                         ["Home", "Config", "Diagnostics", "Alarms", "Interlock", "Info"])
        self.assertEqual(framework.expected_tabs("valve", ["state"], (), "asm"), ["Home", "Diagnostics", "Alarms", "Info"])
        self.assertEqual(framework.expected_tabs("valve", valve), ["Control", "Alarms", "Interlocks", "Maintenance"])
        self.assertEqual(framework.expected_tabs("tank", ["level"], (), "asm"), framework.expected_tabs("tank", ["level"]))
        for label, key in (("Interlock (2)", "Interlock"), ("Diagnostics", "Diagnostics"), ("Home", "Home")):
            self.assertEqual(faceplates.TAB.match(label).group(1), key)
        model = copy.deepcopy(fixture("pilot-devices.json"))
        exp = lambda m, **kw: {v["folder"].split("/")[-1]: v["tabs"]
                               for v in faceplates.device_expectations([fixture("pilot-supply.json")], m, **kw).values()}
        self.assertEqual(exp(model, style="asm")["XV1"][0], "Home")       # the project's default
        next(d for d in model["devices"] if d["id"] == "XV1")["faceplate"] = "openbridge"
        self.assertEqual(exp(model, style="asm")["XV1"][0], "Control")    # the device's own style wins


class FaceplatePinTests(unittest.TestCase):
    """The pin (COBD-045): a faceplate opens in the right dock, the default, or in a floating popup of
    450 by 600 px; Float and Dock move the open faceplate and keep the choice for the session, and
    every symbol, alarm row and trend title that opens a faceplate opens it where the session keeps it."""

    MODE_TEST = "if self.session.custom.faceplateMode == 'popup':"

    def scripts_of(self, views):
        from hmi import gates
        out = []
        for path, doc in views.items():
            for n, _ in gates.walk(doc["root"]):
                for group in (n.get("events") or {}).values():
                    for ev in group.values():
                        for h in ev if isinstance(ev, list) else [ev]:
                            code = (h.get("config") or {}).get("script")
                            if code:
                                out.append((path, n["meta"]["name"], code))
        return out

    def test_every_opener_opens_where_the_session_keeps_the_faceplate(self):
        from hmi import gates, library, parent as par
        with tempfile.TemporaryDirectory() as d:
            base = par.build_parent()[0].write(Path(d))
            child, _ = screen.build_child("cadre_hmi_t", [fixture("pilot-supply.json")], "T", render="module",
                                          devices=fixture("pilot-devices.json"))
            views = {**gates.views_of(base), **gates.views_of(child.write(Path(d)))}
        openers = 0
        for path, name, code in self.scripts_of(views):
            compile("def f(self, event):\n" + code + "\n", f"{path}/{name}", "exec")   # each handler parses
            if "select_device(" in code or "select_alarm_device(" in code:
                openers += 1
                self.assertIn(self.MODE_TEST, code, (path, name))
                self.assertIn(f"openPopup(id='{library.FACEPLATE_POPUP_ID}', view='{library.FACEPLATE_POPUP_VIEW}'", code)
            elif "openDock(id='faceplate')" in code:   # only the popup's Dock button opens the dock unasked; the dock's
                # Float button opens a popup through the same lines as every opener (COB-160)
                self.assertIn((path, name), [(library.FACEPLATE_POPUP_VIEW, "Dock"), ("Framework/SideMenu", "Float")])
        self.assertGreaterEqual(openers, 8)

    def test_float_and_dock_move_the_faceplate(self):
        from hmi import framework, library
        side = view_nodes(framework.side_menu())
        float_ = side["Float"]["events"]["component"]["onActionPerformed"]["config"]["script"]
        self.assertEqual([ln.strip() for ln in float_.splitlines()][:2],
                         ["self.session.custom.faceplateMode = 'popup'", "system.perspective.closeDock('faceplate')"])
        self.assertIn(library.open_popup_line(), float_)
        popup = framework.faceplate_popup()
        nodes = view_nodes(popup)
        dock = nodes["Dock"]["events"]["component"]["onActionPerformed"]["config"]["script"]
        self.assertEqual([ln.strip() for ln in dock.splitlines()],
                         ["self.session.custom.faceplateMode = 'dock'",
                          f"system.perspective.closePopup('{library.FACEPLATE_POPUP_ID}')",
                          "system.perspective.openDock(id='faceplate')",
                          "self.session.custom.faceplateDocked = True"])   # GP-10: a fitted page leaves the dock's width
        self.assertEqual(popup["props"]["defaultSize"], {"width": 450, "height": 600})
        self.assertEqual(nodes["Faceplate"]["propConfig"]["props.path"]["binding"]["config"]["expression"],
                         framework.FACEPLATE_OF_SELECTION)
        self.assertEqual(nodes["Scroll"]["props"]["style"]["overflow"], "auto")
        self.assertEqual(nodes["Faceplate"]["position"]["basis"], f"{framework.FACEPLATE_HEIGHT}px")
        self.assertIn(library.FACEPLATE_POPUP_VIEW, framework.framework_views())

    def test_the_session_the_project_and_the_profile_state_the_place(self):
        from hmi import library, library_profile, parent as par
        self.assertEqual(par.session_defaults()["custom"]["faceplateMode"], "dock")
        for mode in library.FACEPLATE_MODES:
            child, _ = screen.build_child("cadre_hmi_t", [fixture("pilot-supply.json")], "T", faceplate_mode=mode)
            sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
            self.assertEqual(sp["custom"]["faceplateMode"], mode)
        prof = library_profile.build(screen.load_contracts())["faceplate"]
        self.assertEqual((prof["styles"], prof["style"], prof["modes"], prof["mode"]),
                         (["openbridge", "asm"], "openbridge", ["dock", "popup"], "dock"))
        self.assertEqual(prof["popup"], {"view": "Framework/FaceplatePopup", "id": "faceplatePopup", "size": [450, 600]})


class ConfigRowTests(unittest.TestCase):
    """The Config rows (F010 of the ASMP study, COBD-045): a device model marks numbers under `cfg/` as
    configuration, each with its caption, unit, bounds and format; the faceplate lists one setpoint row
    for each, and `cadre.hmi.configure` (W19) writes it within its bounds, as the device's owner allows."""

    D = "[default]t/P1"
    CFG = [{"member": "cfg/startDelay", "caption": "Start delay", "unit": "s", "minimum": 0, "maximum": 600,
            "format": "0"}, {"member": "cfg/runOn", "caption": "Run on", "unit": "s", "minimum": None,
                             "maximum": None, "format": "0.0"}]

    def ns_at(self, entry=None, mode=None):
        tags = {f"{self.D}/cfg/startDelay": 5, f"{self.D}/cfg/runOn": 1.0, f"{self.D}/state": False}
        if mode is not None:
            tags[f"{self.D}/mode"] = mode
        ns, calls = hmi_ns(tags)
        e = {"folder": self.D, "title": "P-1", "config": copy.deepcopy(self.CFG), **(entry or {})}
        return ns, calls, session(["Administrator"], [e]), e

    def test_configure_writes_within_the_bounds(self):
        ns, calls, admin, e = self.ns_at()
        writes = lambda: [c[1:] for c in calls if c[0] == "write"]
        self.assertEqual(ns["configure"](admin, self.D, "cfg/startDelay", 30), "")
        self.assertEqual(writes(), [([f"{self.D}/cfg/startDelay"], [30])])
        self.assertEqual(ns["command"](admin, "W19", self.D, "cfg/runOn", 2.5), "")   # the setpoint row's call
        for member, value, text in (("cfg/startDelay", 601, "is outside its range"), ("cfg/startDelay", -1, "is outside its range"),
                                    ("cfg/startDelay", "30", "takes a number"), ("cfg/startDelay", True, "takes a number"),
                                    ("cfg/other", 1, "is not a configuration member"), ("state", 1, "is not a configuration member")):
            self.assertIn(text, ns["configure"](admin, self.D, member, value), (member, value))
        self.assertEqual(ns["configure"](admin, self.D, "cfg/runOn", 1e9), "")         # no bounds: any number
        self.assertEqual(ns["configure"](session(None, [e]), self.D, "cfg/runOn", 1), ns["REFUSED"])
        self.assertEqual(ns["configure"](admin, "[default]t/P9", "cfg/runOn", 1), "Refused: not a device of this project")
        self.assertEqual(len(writes()), 3)
        ns, calls, admin, e = self.ns_at({"write": ["cfg/runOn"]})                     # the model marks one read only
        self.assertEqual(ns["configure"](admin, self.D, "cfg/startDelay", 1), "Refused: cfg/startDelay is read only on this device")
        self.assertEqual(ns["_checked_writes"](admin, "W19", self.D, [("state", True)]), "Refused: W19 does not write state")

    def test_the_owner_gates_the_configuration(self):
        modes = [{"value": 0, "name": "Auto", "owner": "program"}, {"value": 1, "name": "Manual", "owner": "operator"},
                 {"value": 2, "name": "Maintenance", "owner": "maintenance"}]
        for mode, want in ((0, "Refused: P-1 is owned by the program (Auto)"),
                           (1, "Refused: P-1 is owned by the operator (Manual)"), (2, "")):
            ns, _, admin, _e = self.ns_at({"modes": modes}, mode=mode)
            self.assertEqual(ns["configure"](admin, self.D, "cfg/startDelay", 10), want, mode)

    def test_config_rows_and_device_read(self):
        from hmi import framework
        ns, _, admin, _e = self.ns_at({"write": ["cfg/startDelay"]})
        rows = ns["config_rows"](admin, self.D, True)
        self.assertEqual([(r["member"], r["label"], r["path"], r["minimum"], r["maximum"], r["unit"], r["format"], r["enabled"])
                          for r in rows],
                         [("cfg/startDelay", "Start delay", "W19", 0, 600, "s", "0", True),
                          ("cfg/runOn", "Run on", "W19", None, None, "s", "0.0", False)])
        self.assertFalse(any(r["enabled"] for r in ns["config_rows"](admin, self.D, False)))   # the owner refuses W19
        self.assertTrue(set(rows[0]) <= set(framework.faceplate_setpoint_row()["params"]))
        self.assertEqual(ns["config_rows"](admin, "[default]t/none"), [])
        self.assertEqual(ns["device_read"](admin, self.D, ["state"])["config"], 2)
        self.assertEqual(ns["device_read"](admin, "", ["state"])["config"], framework.dev_default(["state"])["config"])

    def model(self):
        model = copy.deepcopy(fixture("pilot-devices.json"))
        p1 = next(d for d in model["devices"] if d["id"] == "P1")
        p1["members"]["cfg/startDelay"] = {"type": "Int4", "access": "write",
                                           "config": {"caption": "Start delay", "unit": "s", "minimum": 0, "maximum": 600, "format": "0"}}
        return model, p1

    def test_the_index_the_schema_the_profile_and_gate_g7(self):
        from hmi import framework, gates, library_profile
        model, p1 = self.model()
        self.assertEqual(screen.devices_schema_errors(model, "m"), [])
        entry = next(e for e in screen.device_index([fixture("pilot-supply.json")], model) if e["folder"].endswith("/P1"))
        self.assertEqual(entry["config"], [{"member": "cfg/startDelay", "caption": "Start delay", "unit": "s", "minimum": 0,
                                            "maximum": 600, "format": "0"}])
        for change in (lambda c: c.update(format="0.00000"), lambda c: c.update(caption="x" * 25), lambda c: c.pop("caption")):
            bad, d = self.model()
            change(d["members"]["cfg/startDelay"]["config"])
            self.assertTrue(screen.devices_schema_errors(bad, "m"))
        profile = library_profile.build(screen.load_contracts())
        self.assertEqual((profile["deviceKinds"]["pump"]["config"], profile["deviceKinds"]["valve"]["config"],
                          profile["deviceKinds"]["indicator"]["config"], profile["deviceKinds"]["controller"]["config"]),
                         (True, True, True, False))
        self.assertEqual(profile["config"]["path"], "W19")
        self.assertEqual(profile["writePaths"]["W19"]["what"], "configuration value")
        symbols = screen.device_symbols([fixture("pilot-supply.json")])
        res = gates.g7_devices(model, profile, symbols)
        self.assertEqual((res["problems"], [w for w in res["warnings"] if "cfg/" in w]), ([], []))
        cases = ((lambda d: d["members"].update({"cfg/x": {"type": "Int4", "access": "write"}}), "is not marked config"),
                 (lambda d: d["members"].update({"delay": {"type": "Int4", "access": "write", "config": {"caption": "D"}}}),
                  "is not under cfg/"),
                 (lambda d: d["members"]["cfg/startDelay"].update(type="Boolean"), "a Config row takes a number"),
                 (lambda d: d["members"]["cfg/startDelay"]["config"].update(minimum=700), "above its maximum"),
                 (lambda d: d["members"]["cfg/startDelay"]["config"].update(caption="Alarms"), "label of a faceplate tab"))
        for change, text in cases:
            m, d = self.model()
            change(d)
            probs = gates.g7_devices(m, profile, symbols)["problems"]
            self.assertTrue(any(text in p for p in probs), (text, probs))
        m, d = self.model()                              # a controller's faceplate draws no Config rows
        pic = next(x for x in m["devices"] if x["kind"] == "controller")
        pic["members"]["cfg/x"] = copy.deepcopy(d["members"]["cfg/startDelay"])
        self.assertTrue(any("has no Config rows" in p for p in gates.g7_devices(m, profile, symbols)["problems"]))
        m, d = self.model()
        for k in ("minimum", "maximum"):
            d["members"]["cfg/startDelay"]["config"].pop(k)
        self.assertTrue(any("has no bounds" in w for w in gates.g7_devices(m, profile, symbols)["warnings"]))

    def test_the_rows_head_the_maintenance_and_config_tabs(self):
        from hmi import framework, gates
        views = framework.framework_views()
        for view, pane in (("Faceplate/Pump", "Pane_maintenance"), ("Faceplate/Input", "Pane_maintenance"),
                           ("Faceplate/ASM/Valve", "Pane_config")):
            nodes = view_nodes(views[view])
            self.assertEqual([c["meta"]["name"] for c in nodes[pane]["children"][:2]], ["ConfigTitle", "ConfigRows"], view)
            rows = nodes["ConfigRows"]
            self.assertEqual(rows["props"]["path"], "Faceplate/SetpointRow")
            pc = rows["propConfig"]
            self.assertEqual(pc["position.basis"]["binding"]["config"]["expression"], "toStr({view.custom.dev.config} * 44) + 'px'")
            self.assertIn("cadre.hmi.config_rows(self.session, parts[0]", json.dumps(pc["props.instances"]))
            self.assertIn("{view.custom.dev.allowed.W19}", pc["props.instances"]["binding"]["config"]["expression"])
        self.assertEqual(framework.expected_tabs("pump", ["state", "cfg/startDelay"]), ["Control", "Alarms", "Maintenance"])
        self.assertEqual(framework.expected_tabs("valve", ["state", "cfg/startDelay"], (), "asm"),
                         ["Home", "Config", "Diagnostics", "Alarms", "Info"])
        self.assertIn("W19", framework.SETPOINT_PATHS)


class AlarmStateTests(unittest.TestCase):
    """A device symbol's alarm state (F016, COB-140) and the priorities' colours by rank (F053): a symbol
    whose descriptor binds no alert follows its device's alarms, one query for the page; Critical takes
    the critical colour, High alarm, Medium warning, Low caution, and Diagnostic no alert colour."""

    def test_alert_states_rank_the_device_alarms(self):
        Ev = AlarmListTests.Event
        events = [Ev("P1", "High", 1), Ev("P1", "Critical", 2, acked=3), Ev("P2", "Critical", 4, acked=5),
                  Ev("P3", "Low", 6, cleared=7), Ev("P3", "Medium", 8, acked=9, cleared=10),
                  Ev("P4", "Diagnostic", 11), Ev("P10", "High", 12)]
        ns, calls = hmi_ns({}, events=events)
        folders = {k: f"[default]cadre_hmi_wtp/{k[2:]}" for k in ("a_P1", "a_P2", "a_P3", "a_P4", "a_P5")}
        s = session(["Administrator"], [{"folder": f} for f in folders.values()])
        got = ns["alert_states"](s, folders)
        self.assertEqual(got["a_P1"], {"alert": True, "alertAny": True, "status": "alarm", "level": "level-high",
                                       "mode": "unacked-active"})   # the unacknowledged one leads
        self.assertEqual((got["a_P2"]["status"], got["a_P2"]["level"], got["a_P2"]["mode"]),
                         ("critical", "level-critical", "acked-active"))
        self.assertEqual((got["a_P3"]["status"], got["a_P3"]["mode"]), ("caution", "unacked-rectified"))
        self.assertEqual((got["a_P4"]["alert"], got["a_P4"]["alertAny"], got["a_P4"]["level"]),
                         (False, True, "level-diagnostic"))   # Diagnostic: no frame on a library symbol
        self.assertEqual(got["a_P5"], ns["ALERT_NONE"])          # P10's alarm is not P1's (the trailing slash)
        self.assertEqual(len([c for c in calls if c[0] == "query"]), 1)   # one query for the page
        self.assertEqual(ns["alert_states"](s, {}), {})

    def test_the_generator_binds_the_symbols_that_bind_no_alert(self):
        model = fixture("pilot-devices.json")
        for render, prefix, fields in (("stock", "props.params.", ("alert", "status", "mode")),
                                       ("module", "props.", ("alertAny", "level", "mode"))):
            child, _ = screen.build_child("cadre_hmi_t", [fixture("pilot-supply.json")], "T", render=render, devices=model)
            doc = json.loads(next(v for k, v in child.files.items() if k.endswith("PilotSupply/view.json")))
            nodes = view_nodes(doc)
            self.assertEqual(sorted(doc["custom"]["alerts"]), ["a_P2"])   # a lamp draws no frame (L5)
            poll = doc["propConfig"]["custom.alerts"]["binding"]
            self.assertEqual(poll["config"]["expression"], screen.ALERT_POLL)
            self.assertIn("cadre.hmi.alert_states(self.session, {'a_P2': ", poll["transforms"][0]["code"])
            pc = nodes["P2"]["propConfig"]
            self.assertEqual([pc[f"{prefix}{k}"]["binding"]["config"]["expression"] for k in screen.ALERT_PARAMS],
                             ["{view.custom.alerts.a_P2.%s}" % f for f in fields], render)
            shown = nodes["P2"]["props"].get("params", nodes["P2"]["props"])
            self.assertFalse(set(screen.ALERT_PARAMS) & set(shown), render)   # no default beside a binding (GF-61)
            own = (nodes["P1"].get("propConfig") or {}).get(f"{prefix}alert", {}).get("binding", {})
            self.assertEqual(own.get("type"), "tag", render)   # P1 binds its own member, which stays

    def test_the_priorities_take_the_colours_by_rank(self):
        from hmi import framework, library, scripts
        self.assertEqual(scripts.constant("PRIORITY_STATUS"),
                         {"Critical": "critical", "High": "alarm", "Medium": "warning", "Low": "caution", "Diagnostic": ""})
        self.assertTrue(framework.PRIORITY_VAR.startswith("case({view.custom.alarm.highest}, 'Critical', "
                                                          "'var(--alert-critical-color)', 'High', 'var(--alert-alarm-color)'"))
        self.assertNotIn("Diagnostic", framework.PRIORITY_VAR)
        classes = library.style_classes(json.loads((ROOT / "library/tokens/openbridge-tokens.json").read_text(encoding="utf-8")))
        self.assertTrue({"cadre/alert/flash-critical", "cadre/alert/badge-critical"} <= set(classes))
        layers = {n["meta"]["name"]: n for n in library._alert_frame()}
        nodes = {c["meta"]["name"]: c for c in layers["AlertFrame"]["children"]}
        self.assertIn("Flap_critical", nodes)
        alarm_flap = json.dumps(nodes["Flap_alarm"]["propConfig"])
        self.assertIn("!= 'critical'", alarm_flap)
        self.assertIn("'critical', 'var(--alert-critical-color)'", json.dumps(layers["AlertFrame"]["propConfig"]))


class AlarmFormTests(unittest.TestCase):
    """The one form of an alarm (tools/hmi/alarms.py; F028, F042, F043, F045, F059): label, display path of
    the device's node, priority, shelving by priority, an on-delay that follows its member; the delay rows
    and the shelving times of the faceplates; the node of a page; the alarm test device of the fixture."""

    def test_the_form(self):
        from hmi import alarms, library_profile
        a = alarms.definition("High level", "TK-1", "High level", "High", "WTP/Intake", mode="AboveValue",
                              limit="hiLimit", delay=True)
        self.assertEqual(a, {"name": "High level", "label": "TK-1 High level", "displayPath": "WTP/Intake/TK-1",
                             "priority": "High", "shelvingAllowed": True, "mode": "AboveValue",
                             "setpointA": {"bindType": "Expression", "value": "{[.]hiLimit}"},
                             "timeOnDelaySeconds": {"bindType": "Expression", "value": "{[.]hiLimitDelay}"}})
        self.assertFalse(alarms.definition("Trip", "P-1", "Trip", "Critical")["shelvingAllowed"])   # F045
        self.assertEqual(alarms.definition("Run", "P-1", "Running", alarms.STATE_REPORT)["displayPath"], "P-1")
        for bad in (lambda: alarms.definition("x", "P-1", "x", "Urgent"),
                    lambda: alarms.definition("x", "P-1", "x", "Low", delay=True)):
            self.assertRaises(ValueError, bad)
        self.assertEqual(library_profile.build(screen.load_contracts())["alarms"], alarms.form())
        self.assertEqual(alarms.SHELVE_SECONDS[-1], 8 * 3600)

    def test_delay_rows_and_their_write(self):
        from hmi import framework
        d = "[default]t/FT1"
        ns, calls = hmi_ns({f"{d}/value": 1.0, f"{d}/hiLimit": 2.0, f"{d}/hiLimitDelay": 5.0})
        admin = session(["Administrator"], [{"folder": d}])
        self.assertEqual(ns["delay_rows"](d, admin), [{"deviceId": d, "member": "hiLimitDelay", "label": "High delay (s)",
                                                       "path": "W4", "format": "0", "minimum": 0, "maximum": 3600,
                                                       "unit": "s", "enabled": True}])
        self.assertEqual(ns["command"](admin, "W4", d, "hiLimitDelay", 30), "")
        self.assertEqual(ns["command"](admin, "W4", d, "hiLimitDelay", 3601), "Refused: hiLimitDelay is outside its range")
        self.assertEqual(ns["delay_rows"]("", admin), [])
        for view in ("Faceplate/Instrument", "Faceplate/Tank", "Faceplate/Controller"):
            doc = framework.framework_views()[view]
            nodes = view_nodes(doc)
            self.assertEqual(nodes["Delays"]["props"]["path"], "Faceplate/SetpointRow", view)
            self.assertIn("cadre.hmi.delay_rows(value, self.session)", json.dumps(doc["propConfig"]["custom.delayRows"]))
            self.assertEqual(doc["custom"]["delayRows"], [])
        self.assertIn("W4", framework.SETPOINT_PATHS)

    def test_the_tables_shelve_for_the_librarys_times(self):
        from hmi import alarms, framework, gates
        views = framework.framework_views()
        tables = [(p, n) for p, doc in views.items() for n, _ in gates.walk(doc["root"])
                  if n["type"] == "ia.display.alarmstatustable"]
        self.assertEqual(len(tables), 3)
        for p, n in tables:
            self.assertEqual(n["props"]["shelvingTimes"], alarms.SHELVE_SECONDS, p)

    def test_the_node_of_a_page_and_of_a_device(self):
        sys.path.insert(0, str(ROOT / "tools" / "plants"))
        import wtp
        descs = [wtp.overview(), wtp.intake(), wtp.filtration(), wtp.disinfection()]
        self.assertEqual(screen.schema_errors(descs, ["o", "i", "f", "d"]), [])
        nodes = screen.device_nodes(descs)
        self.assertEqual((nodes[f"{wtp.P}/P101"], nodes[f"{wtp.P}/P301"], nodes[f"{wtp.P}/TK501"]),
                         ("WTP/Intake", "WTP/Filtration", "WTP/Disinfection"))   # the area page, not the overview
        bad = copy.deepcopy(descs[0])
        bad["screen"]["node"] = "WTP//Intake"
        self.assertTrue(screen.schema_errors([bad], ["o"]))
        folders = {f["name"]: f for f in wtp.tag_model()["tags"]}
        ait = next(t for t in folders["AIT301"]["tags"] if t["name"] == "value")["alarms"][0]
        self.assertEqual((ait["displayPath"], ait["timeOnDelaySeconds"]["value"]), ("WTP/Filtration/AIT-301", "{[.]hiLimitDelay}"))
        self.assertIn("hiLimitDelay", [t["name"] for t in folders["AIT301"]["tags"]])

    def test_the_alarm_test_device(self):
        from hmi import alarms
        tst = next(t for t in fixture("pilot-tags.json")["tags"] if t["name"] == "TST1")
        state = tst["tags"][0]
        self.assertFalse(state["value"])   # clear at the start: a gate raises it, never the build (F059)
        self.assertEqual([a["priority"] for a in state["alarms"]], list(alarms.PRIORITIES))
        self.assertEqual({a["displayPath"] for a in state["alarms"]}, {"Pilot/TST-1"})


class AckRelayTests(unittest.TestCase):
    """The controller acknowledgement bit (F049, COBD-044: optional per device, off by default): an
    acknowledgement through `cadre.hmi` writes true to `alarmAck` of each acknowledged alarm's device
    whose device model lists it, under the acknowledgement's path; no other device is told."""

    def harness(self, tags, events, failed=()):
        from hmi import scripts
        calls = []

        class Tag:
            @staticmethod
            def exists(path):
                return path in tags

            @staticmethod
            def readBlocking(paths):
                return [type("QV", (), {"value": tags.get(p), "quality": "Good"})() for p in paths]

            @staticmethod
            def writeBlocking(paths, values):
                calls.append(("write", list(paths), list(values)))
                return ["Good" for _ in paths]

        class Alarm:
            @staticmethod
            def queryStatus(path=None, state=None, priority=None):
                return [e for e in events if priority is None or e.getPriority() in priority]

            @staticmethod
            def acknowledge(ids, notes, user):
                calls.append(("ack", list(ids)))
                return [i for i in ids if i in failed]

        class System:
            tag, alarm = Tag, Alarm
        ns = {"unicode": str, "long": int, "system": System}
        exec(scripts.HMI, ns)
        return ns, calls

    D = "[default]cadre_hmi_wtp/P502"

    def entry(self, ack=True):
        members = ["fault"] + (["alarmAck"] if ack else [])
        return {"folder": self.D, "members": members, "write": members}

    def test_a_list_acknowledgement_tells_the_device_that_asks(self):
        ev = AlarmListTests.Event("P502", "High", 10)
        for ack, failed, writes in ((True, (), [("write", [f"{self.D}/alarmAck"], [True])]), (False, (), []),
                                    (True, (ev.getId(),), [])):
            ns, calls = self.harness({f"{self.D}/alarmAck": False, f"{self.D}/fault": True}, [ev], failed)
            s = session(["Administrator"], [self.entry(ack)])
            ns["ack"]([ev.getId()], s, path="W9")
            self.assertEqual([c for c in calls if c[0] == "write"], writes, (ack, failed))
        ns, calls = self.harness({f"{self.D}/alarmAck": False}, [ev])
        self.assertEqual(ns["ack"]([ev.getId()], session(None, [self.entry()])), ns["REFUSED"])
        self.assertEqual(calls, [])

    def test_the_top_bar_tells_the_device_of_its_top_alarm(self):
        ev = AlarmListTests.Event("P502", "Critical", 10)
        ns, calls = self.harness({f"{self.D}/alarmAck": False}, [ev])
        s = session(["Administrator"], [self.entry()])
        ns["ack_top"]("*", s)
        self.assertEqual(calls, [("ack", [ev.getId()]), ("write", [f"{self.D}/alarmAck"], [True])])
        self.assertEqual(ns["alarm_summary"]("*")["topSource"], ev.getSource())

    def test_the_fixture_carries_the_bit(self):
        from hmi import gates, library_profile
        tst = next(d for d in fixture("pilot-devices.json")["devices"] if d["id"] == "TST1")
        self.assertEqual(tst["members"]["alarmAck"], {"type": "Boolean", "access": "write"})
        prof = library_profile.build(screen.load_contracts())
        self.assertEqual(prof["ackRelay"], {"member": "alarmAck", "value": True, "paths": ["W6", "W8", "W9"]})
        self.assertTrue(all("alarmAck" in k["members"] for k in prof["deviceKinds"].values()))


class HierarchyTests(unittest.TestCase):
    """The plant hierarchy of the descriptor set (F033, COB-141), its alarm counts per node (F047), the
    badges (F046) and the breadcrumb (F036): one query counts every node, an alarm going to its device and
    the device to its node, and each node holds the counts of the nodes beneath it."""

    def descs(self):
        sys.path.insert(0, str(ROOT / "tools" / "plants"))
        import wtp
        return wtp, [wtp.overview(), wtp.intake(), wtp.filtration(), wtp.disinfection()]

    def test_the_generator_writes_the_hierarchy(self):
        wtp, descs = self.descs()
        h = screen.hierarchy(descs)
        self.assertEqual([(n["id"], n["path"], n["parentId"], n["name"]) for n in h],
                         [("n0", "WTP", "", "WTP"), ("n1", "WTP/Disinfection", "n0", "Disinfection"),
                          ("n2", "WTP/Filtration", "n0", "Filtration"), ("n3", "WTP/Intake", "n0", "Intake")])
        self.assertEqual(h[0]["pages"], [{"label": "Plant Overview", "route": "/"}])
        self.assertIn(f"{wtp.P}/P301", h[2]["devices"])
        self.assertEqual(h[0]["devices"], [])   # every device of the overview has an area page
        child, _ = screen.build_child("cadre_hmi_wtp", descs, "W")
        sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
        self.assertEqual(sp["custom"]["hierarchy"], h)
        self.assertEqual({i["path"]: i["node"] for i in sp["custom"]["nav"]["items"]}["/intake"], "WTP/Intake")
        nameless = copy.deepcopy(fixture("pilot-supply.json"))
        nameless["screen"].pop("node")
        self.assertEqual(screen.hierarchy([nameless]), [])

    def session_at(self, events):
        wtp, descs = self.descs()
        h = screen.hierarchy(descs)
        ns, calls = hmi_ns({}, events=events)
        s = session(["Administrator"], [{"folder": f} for n in h for f in n["devices"]])
        s.custom.hierarchy = h
        s.custom.nav = {"items": [{"label": "Filtration", "path": "/filtration", "icon": "", "node": "WTP/Filtration"},
                                  {"label": "Trends", "path": "/trends", "icon": "trend", "node": ""}], "footer": []}
        return ns, calls, s

    def test_counts_per_node_roll_up(self):
        Ev = AlarmListTests.Event
        events = [Ev("P301", "High", 1), Ev("XV301", "Critical", 2, acked=3), Ev("P101", "Low", 4), Ev("GHOST", "High", 5)]
        ns, calls, s = self.session_at(events)
        got = ns["node_counts"](s)
        self.assertEqual({k: (v["Critical"], v["High"], v["Low"], v["total"], v["unacked"]) for k, v in got.items()},
                         {"n0": (1, 1, 1, 3, 2), "n1": (0, 0, 0, 0, 0), "n2": (1, 1, 0, 2, 1), "n3": (0, 0, 1, 1, 1)})
        self.assertEqual(len([c for c in calls if c[0] == "query"]), 1)
        trail = ns["crumbs"](s, "/filtration")
        self.assertEqual([(c["name"], c["route"], c["first"], c["counts"]["total"]) for c in trail],
                         [("WTP", "/", True, 3), ("Filtration", "/filtration", False, 2)])
        self.assertEqual(ns["crumbs"](s, "/alerts"), [])
        items = ns["nav_items"](s)
        self.assertEqual([(i["path"], i["counts"]["total"]) for i in items], [("/filtration", 2), ("/trends", 0)])
        empty = session(["Administrator"], [])
        self.assertEqual((ns["node_counts"](empty), ns["crumbs"](empty, "/")), ({}, []))

    def test_the_views(self):
        from hmi import framework, scripts
        views = framework.framework_views()
        b = view_nodes(views["Framework/Badges"])
        for p, status in scripts.constant("PRIORITY_STATUS").items():
            n = b[f"Badge_{p}"]
            self.assertEqual(n["propConfig"]["position.display"]["binding"]["config"]["expression"], f"{{view.params.counts.{p}}} > 0")
            self.assertIn(f"cadre/alert/badge-{status}" if status else "cadre/text/neutral", n["props"]["style"]["classes"])
        top = views["Framework/TopBar"]
        t = view_nodes(top)
        self.assertEqual(t["Crumbs"]["props"]["path"], "Framework/Crumb")
        self.assertEqual(t["PageName"]["propConfig"]["position.display"]["binding"]["config"]["expression"],
                         "len({view.custom.crumbs}) = 0")
        self.assertIn("cadre.hmi.crumbs(self.session, value)", json.dumps(top["propConfig"]["custom.crumbs"]))
        menu = view_nodes(views["Framework/NavMenu"])
        self.assertIn("cadre.hmi.nav_items(self.session)", json.dumps(menu["Items"]["propConfig"]))
        self.assertEqual(menu["Footer"]["propConfig"]["props.instances"]["binding"]["config"]["expression"],
                         "{session.custom.nav.footer}")
        self.assertIn("Badges", view_nodes(views["Framework/NavItem"]))
        c = view_nodes(views["Framework/Crumb"])
        self.assertEqual(c["Chevron"]["propConfig"]["position.display"]["binding"]["config"]["expression"], "!{view.params.first}")
        self.assertEqual(framework.NO_COUNTS, {**{p: 0 for p in scripts.constant("PRIORITIES")}, "total": 0, "unacked": 0})


class LibraryCallTests(unittest.TestCase):
    """Gate G7 resolves every library call (F050 of the ASMP study, COB-142): a name a view's script or a
    tag takes from `cadre.hmi` or `cadre.icons` must be one the library code the projects ship defines,
    where the source's alarm handlers named functions their module lacked and nothing told."""

    def test_views_name_only_what_the_parent_defines(self):
        from hmi import gates, parent as par, scripts
        with tempfile.TemporaryDirectory() as d:
            base = par.build_parent()[0].write(Path(d) / "base")
            defined = gates.library_names(base)
            self.assertTrue({"command", "select_device", "configure", "alarm_count", "CONFIG_PATH"} <= defined["hmi"])
            self.assertEqual(defined["icons"], {"ICONS", "elements"})
            self.assertFalse(any(n.startswith("_") for n in defined["hmi"]))
            self.assertTrue(gates.g7_commands(base, None)["ok"])
            vf = base / "com.inductiveautomation.perspective/views/Faceplate/Pump/view.json"
            good = vf.read_text(encoding="utf-8")
            vf.write_text(good.replace("cadre.hmi.device_read(", "cadre.hmi.device_reads("), encoding="utf-8")
            probs = gates.g7_commands(base, None)["problems"]
            self.assertTrue(probs and all("cadre.hmi.device_reads is not defined by the project's library" in p
                                          for p in probs), probs)
            vf.write_text(good, encoding="utf-8")
            # a child is resolved against its parent's library; without it, nothing it names resolves
            child, _ = screen.build_child("cadre_hmi_t", [fixture("pilot-supply.json")], "T", render="module")
            cp = child.write(Path(d))   # its module views override the parent's and call the library
            self.assertTrue(gates.g7_commands(cp, base)["ok"])
            alone = gates.g7_commands(cp, None)["problems"]
            self.assertTrue(alone and all("is not defined by the project's library" in p for p in alone))
            # every top-level function of the library text is one the gate reads
            self.assertTrue({m for m in re.findall(r"^def ([a-z]\w*)\(", scripts.HMI, re.M)} <= defined["hmi"])

    def test_a_tag_names_only_what_the_parent_defines(self):
        from hmi import gates, parent as par
        with tempfile.TemporaryDirectory() as d:
            base = par.build_parent()[0].write(Path(d))
            good = {"tags": [{"name": "A", "tagType": "Folder", "tags": [
                {"name": "n", "tagType": "AtomicTag", "valueSource": "expr", "expression": "runScript('cadre.hmi.alarm_count', 0, '*')"}]}]}
            self.assertEqual(gates.g7_tag_libraries(good, base, None)["problems"], [])
            bad = copy.deepcopy(good)
            bad["tags"][0]["tags"][0]["expression"] = "runScript('cadre.hmi.summary_of', 0, '*')"
            self.assertEqual(gates.g7_tag_libraries(bad, base, None)["problems"],
                             ["/A/n: cadre.hmi.summary_of is not defined by the project's library",
                              "/A/n: runScript of cadre.hmi.summary_of, which no library of the project defines"])
            self.assertTrue(gates.g7_tag_libraries(fixture("pilot-tags.json"), base, None)["ok"])


class ConfirmationTests(unittest.TestCase):
    """Confirmation (F029 of the ASMP study, COBD-045): a command that changes the state of the process,
    and a setpoint, is written only once the operator confirms it, in both faceplate styles. A command
    button asks and writes nothing; the Confirm row beneath the tabs makes the one checked write; a row
    holds the value typed until its Set; a bypass waits for its own Confirm."""

    FACEPLATES = ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/ASM/Pump", "Faceplate/ASM/Valve",
                  "Faceplate/Controller", "Faceplate/Input", "Faceplate/Sequence", "Faceplate/Tank",
                  "Faceplate/Instrument")

    def script(self, n):
        return ((n.get("events") or {}).get("component") or {}).get("onActionPerformed", {}).get("config", {}).get("script", "")

    def test_every_command_button_asks_and_the_confirm_row_writes(self):
        from hmi import framework, gates
        views = framework.framework_views()
        asked = set()
        for path in self.FACEPLATES:
            doc = views[path]
            names = [c["meta"]["name"] for c in doc["root"]["children"]]
            self.assertEqual(names[names.index("Quality") + 1], "Confirm", path)   # on every tab
            self.assertEqual(doc["custom"]["pending"], framework.PENDING_DEFAULT, path)
            for n, _ in gates.walk(doc["root"]):
                code = self.script(n)
                if "self.view.custom.pending = {'active': True" in code:
                    self.assertNotIn("cadre.hmi.", code.replace("cadre.hmi.start_permitted(", ""), (path, n["meta"]["name"]))
                    asked.add(re.search(r"'path': '(W\d+)'", code).group(1))
                elif n["type"] == "ia.input.button" and "cadre.hmi.command(" in code:
                    self.assertEqual(n["meta"]["name"], "ConfirmYes", (path, code))
            yes = view_nodes(doc)["ConfirmYes"]
            enabled = yes["propConfig"]["props.enabled"]["binding"]["config"]["expression"]
            self.assertTrue(gates._case_follows(enabled, "{view.custom.pending.path}"), enabled)
            self.assertEqual(gates._paths_called(self.script(yes)), ["{view.custom.pending.path}"])
        self.assertEqual(asked, set(framework.CONFIRMED_PATHS))
        for w in framework.CONFIRMED_PATHS:
            self.assertIn(f"'{w}', {{view.custom.can.{w}}}", enabled)

    def test_command_hands_the_confirmed_paths_to_their_functions(self):
        d = "[default]t/P1"
        tags = {f"{d}/{m}": v for m, v in (("mnt/forceOn", False), ("mnt/forceOff", False), ("mnt/errorMask", False),
                                            ("trigger", False), ("ilk/resetAt", 0))}
        ns, calls = hmi_ns(tags)
        admin = session(["Administrator"], [{"folder": d}])
        for path, member, value, want in (("W16", "force", "on", [f"{d}/mnt/forceOff", f"{d}/mnt/forceOn"]),
                                          ("W17", "mnt/errorMask", True, [f"{d}/mnt/errorMask"]),
                                          ("W18", "trigger", True, [f"{d}/trigger"])):
            before = len(calls)
            self.assertEqual(ns["command"](admin, path, d, member, value), "", path)
            self.assertEqual([c[1][0] for c in calls[before:] if c[0] == "write"], want, path)
        self.assertEqual(ns["command"](admin, "W16", d, "force", "sideways"), "Refused: no such force action")
        self.assertEqual(ns["command"](session(None, [{"folder": d}]), "W17", d, "mnt/errorMask", True), ns["REFUSED"])

    def test_a_row_holds_the_value_until_set(self):
        from hmi import framework, gates
        for row, path_arg in ((framework.faceplate_setpoint_row(), "{view.params.path}"),
                              (framework.faceplate_limit_row(), "W4")):
            nodes = view_nodes(row)
            self.assertEqual(self.script(nodes["Setpoint"]), "".join("\t" + ln + "\n" for ln in framework.ROW_HOLD).rstrip("\n"))
            field_on = nodes["Setpoint"]["propConfig"]["props.enabled"]["binding"]["config"]["expression"]
            self.assertEqual(nodes["Set"]["propConfig"]["props.enabled"]["binding"]["config"]["expression"], field_on)
            self.assertEqual(gates._paths_called(self.script(nodes["Set"])), [path_arg])
            for name, shown in (("Set", "{view.custom.pending}"), ("Undo", "{view.custom.pending}")):
                self.assertEqual(nodes[name]["propConfig"]["position.display"]["binding"]["config"]["expression"], shown)
            self.assertIn("system.tag.readBlocking", self.script(nodes["Undo"]))
            self.assertNotIn("cadre.hmi", self.script(nodes["Undo"]))
            self.assertIn("self.custom.pending = False", row["propConfig"]["params.deviceId"]["onChange"]["script"])
            width = sum(int(c["position"]["basis"][:-2]) for c in row["root"]["children"]
                        if c["meta"]["name"] not in ("Note", "Lamp")) + 8 * 3
            self.assertLessEqual(width, row["props"]["defaultSize"]["width"])   # the answers fit the row
        ilk = view_nodes(framework.faceplate_interlock_row())
        self.assertEqual(self.script(ilk["Bypass"]), "\tself.view.custom.pending = True")
        self.assertIn("cadre.hmi.bypass(", self.script(ilk["BypassYes"]))
        self.assertTrue(gates._follows_permissions(ilk["BypassYes"], "props.enabled", "W10"))

    def test_the_captions_agree(self):
        from hmi import framework
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import glass
        import walk_plan
        self.assertEqual((framework.CONFIRM, framework.CANCEL, framework.SET),
                         (glass.CONFIRM, glass.CANCEL, glass.SET))
        self.assertEqual((walk_plan.CONFIRM, walk_plan.SET), (framework.CONFIRM, framework.SET))


class ModuleDevicePropsTests(unittest.TestCase):
    """L4 items 3, 4 and 9: the status words and their mute, the duty and out of service marks and the readout's stretch
    reach the module's components, each only where the module's schema lists the property (module 3.2 of the L4 contract)."""

    @classmethod
    def setUpClass(cls):
        from hmi import parent as par
        cls.contracts = par.build_parent()[1]
        cls.comps = json.loads((ROOT / "module/components.json").read_text(encoding="utf-8"))

    def listing(self, extra=True):
        """A schema that lists the new properties of every component that may carry them, or one without them
        (the module before 0.4.0)."""
        def props(ctype):
            have = set(self.comps.get(ctype, {}).get("props", {}))
            for kind, names in screen.MODULE_IF_LISTED.items():
                if screen.MODULE_KIND[kind] == ctype:
                    have = have | set(names) if extra else have - set(names)
            return have
        return mock.patch.object(screen, "module_props", props)

    def embed(self, sym, toolbar=True):
        screen.RENDER["target"] = "module"
        try:
            rep = screen.Report()
            node, custom, _cfg = screen.embed_symbol(sym, self.contracts, "[default]t", rep, toolbar=toolbar)
            return node, custom, rep.errors
        finally:
            screen.RENDER["target"] = "stock"

    def sym(self, kind="pump", **kw):
        return dict({"id": "P1", "kind": kind, "x": 100, "y": 100, "w": 48, "h": 48, "params": {}}, **kw)

    def expr(self, node, key):
        return node["propConfig"][key]["binding"]["config"]["expression"]

    def test_the_schema_in_force_gets_none_of_them(self):
        with self.listing(extra=False):
            node, _custom, errors = self.embed(self.sym(bind={"on": "P1/state"}))
        self.assertEqual((node["type"], errors), ("cadre.ob.pump", []))
        for k in ("showStatus", "statusText", "badgeDuty", "outOfService"):
            self.assertNotIn(k, node["props"])
            self.assertNotIn(f"props.{k}", node["propConfig"])
        # a symbol that states a mark stays on the library's view while the module cannot show it
        with self.listing(extra=False):
            node, _custom, _e = self.embed(self.sym(params={"outOfService": True}))
        self.assertEqual(node["type"], "ia.display.view")

    def test_the_status_words_follow_the_state_and_the_readout_toggle(self):
        with self.listing():
            node, custom, errors = self.embed(self.sym(bind={"on": "P1/state"}))
        self.assertEqual((node["type"], errors), ("cadre.ob.pump", []))
        self.assertEqual(self.expr(node, "props.showStatus"), "{view.custom.showReadout} && true")
        self.assertEqual(self.expr(node, "props.statusText"), "if({view.custom.g_P1}, 'On', 'Off')")
        self.assertIn("g_P1", custom)
        self.assertNotIn("showStatus", node["props"])
        self.assertNotIn("statusText", node["props"])

    def test_the_words_of_a_pump_with_a_speed_are_the_speed(self):
        with self.listing():
            node, _c, _e = self.embed(self.sym("motor", params={"hasSpeed": True},
                                               bind={"on": "M1/state", "speed": "M1/speed"}))
        self.assertEqual(self.expr(node, "props.statusText"),
                         "if({view.custom.g_P1}, numberFormat({this.props.speedInPercent}, '0') + ' %', 'Off')")
        self.assertEqual(node["propConfig"]["props.speedInPercent"]["binding"]["config"]["tagPath"], "[default]t/M1/speed")

    def test_a_symbol_without_a_state_says_off_and_a_card_has_no_toggle(self):
        with self.listing():
            node, _c, _e = self.embed(self.sym("fan"))
            self.assertEqual(self.expr(node, "props.statusText"), "if(false, 'On', 'Off')")
            node, _c, _e = self.embed(self.sym(bind={"on": "P1/state"}), toolbar=False)
        self.assertNotIn("props.showStatus", node["propConfig"])      # no toolbar, no toggle
        self.assertIn("props.statusText", node["propConfig"])         # the words are the symbol's own

    def test_words_the_descriptor_states_are_kept(self):
        with self.listing():
            node, _c, _e = self.embed(self.sym(params={"statusText": "Duty"}, bind={"on": "P1/state"}))
        self.assertEqual(node["props"]["statusText"], "Duty")
        self.assertNotIn("props.statusText", node["propConfig"])
        self.assertEqual(self.expr(node, "props.showStatus"), "{view.custom.showReadout} && true")   # as the library view's toggle

    def test_the_analogue_valve_row_is_not_invented(self):
        with self.listing():
            node, _c, _e = self.embed(self.sym("analogvalve", bind={"open": "V1/state"}))
        self.assertEqual(node["type"], "cadre.ob.analogvalve")
        self.assertNotIn("props.statusText", node["propConfig"])
        self.assertIn("props.showStatus", node["propConfig"])

    def test_the_marks_pass_through_and_no_longer_keep_a_symbol_on_the_library(self):
        with self.listing():
            node, _c, errors = self.embed(self.sym(params={"badgeDuty": True, "outOfService": True}))
            self.assertEqual((node["type"], errors), ("cadre.ob.pump", []))
            self.assertEqual((node["props"]["badgeDuty"], node["props"]["outOfService"]), (True, True))
            node, _c, _e = self.embed(self.sym(bind={"badgeDuty": "P1/duty", "outOfService": "P1/oos"}))
            self.assertEqual(node["type"], "cadre.ob.pump")
            self.assertEqual(node["propConfig"]["props.badgeDuty"]["binding"]["config"]["tagPath"], "[default]t/P1/duty")
            self.assertEqual(node["propConfig"]["props.outOfService"]["binding"]["config"]["tagPath"], "[default]t/P1/oos")
            self.assertNotIn("badgeDuty", node["props"])
            self.assertTrue(screen.module_draws("pump", {"badgeDuty": None}, target="module"))
            self.assertTrue(screen.module_draws("valve", {"outOfService": True}, target="module"))
        self.assertTrue(screen.module_draws("pump", {"outOfService": True}, target="module"))    # module 0.4.0, in force

    def test_every_property_emitted_is_one_the_patched_schema_lists(self):
        for kind in ("pump", "motor", "fan", "valve"):
            state = "open" if kind == "valve" else "on"
            with self.listing():
                node, _c, _e = self.embed(self.sym(kind, params={"badgeDuty": True, "hasSpeed": kind != "valve"},
                                                   bind={state: "X/state"}))
                have = screen.module_props(screen.MODULE_KIND[kind])
            keys = set(node["props"]) | {k[len("props."):].split(".")[0].split("[")[0]
                                         for k in node.get("propConfig", {}) if k.startswith("props.")}
            self.assertEqual(keys - have, set(), kind)

    def test_the_readout_stretches_only_where_the_module_has_it(self):
        sym = {"id": "R1", "kind": "readout", "x": 10, "y": 10, "w": 72, "h": 24, "params": {"stretch": True}}
        self.assertIs(self.contracts["Automation/Readout"]["params"]["stretch"], False)
        with self.listing(extra=False):
            node, _c, errors = self.embed(sym)
        self.assertEqual((node["type"], "stretch" in node["props"], errors), ("cadre.ob.readout", False, []))
        with self.listing():
            node, _c, errors = self.embed(sym)
            plain, _c, _e = self.embed(dict(sym, params={}))
        self.assertEqual((node["type"], node["props"]["stretch"], errors), ("cadre.ob.readout", True, []))
        self.assertNotIn("stretch", plain["props"])


if __name__ == "__main__":
    unittest.main()
