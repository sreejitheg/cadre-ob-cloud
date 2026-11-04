"""Tests of `tools/compare/glass_gates.py` (S10-B, ARCH-WFB-01 revision B8 Table 109, schema
`cadre-hmi-glass-gates/1`).

The plan is tested offline. The gates' control flow is proven on the fake gateway's client page
(`tests/glass_fake.py`), in headless Chromium, when Playwright is importable (ctig's `.venv`):

    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe -m unittest tests.test_glass_gates_plan

What the real glass does is not claimed here: it is measured on the gateway by the integrated run (S10-G).
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump, fixture, inputs, validate  # noqa: E402

sys.path.insert(0, str(ROOT / "tools" / "compare"))
import glass_gates  # noqa: E402
from hmi import asm_descriptors, asm_model  # noqa: E402

try:
    import playwright.sync_api  # noqa: F401
    HAVE_BROWSER = True
except ImportError:
    HAVE_BROWSER = False

PROJECT = "cadre_hmi_plant"


def glass_gates_step_page(action: str) -> str | None:
    """The route a step names (`<route>: ...`), as the evidence pack of WorkflowBuilder groups the steps."""
    head = action.split(":", 1)[0]
    return head if head.startswith("/") else None
TAG_ROOT = "[default]cadre_hmi_plant"
DESIGNS = ("asm-design-overview.json", "asm-design-pumpstation.json")


def make(d: Path):
    """Model and bridge folder of the synthetic plant; the descriptors' build as asm_descriptors writes it."""
    ins = inputs(d)
    out = d / "model"
    assert asm_model.main([a for k, v in ins.items() for a in (f"--{k}", str(v))] + ["--tag-root", TAG_ROOT,
                                                                                    "--out", str(out)]) == 0
    lst = d / "designs.txt"
    paths = [dump(d / "designs" / n, fixture(n)) for n in DESIGNS]
    lst.write_text("\n".join(str(p) for p in paths) + "\n", encoding="utf-8", newline="\n")
    acc = dump(d / "acc.json", ["GAP-ups"])
    code = asm_descriptors.main(["--model", str(out / "model.json"), "--designs", str(lst), "--tables", str(ins["tables"]),
                                 "--accepted", str(acc), "--project", PROJECT, "--parent", "cadre_hmi_base_asm",
                                 "--tag-root", TAG_ROOT, "--render", "module", "--equalise", "--medium", "--simulation", "--component-test",
                                 "--out", str(d / "build")])
    assert code == 0, code
    return json.loads((out / "model.json").read_text(encoding="utf-8")), d / "build" / "bridge"


def argv_of(d: Path, base: str = "http://localhost:8088/data/perspective/client/" + PROJECT, *extra):
    return ["--base", base, "--model", str(d / "model" / "model.json"), "--build", str(d / "build" / "bridge"),
            "--window", "1280x800", "--out", str(d / "glass"), *extra]


class ModuleDrawnTests(unittest.TestCase):
    """COB-198: the symbols and readouts plans count only the symbols drawn as module components. A second pass that
    set `render: view` on eight symbols of a page drew them on the library's view, which neither selector finds, and
    the gates counted 5 of 12 motors and 0 of 1 valve on a page that drew them all."""

    def page(self):
        def motor(i, render=None):
            s = {"id": f"M{i}", "kind": "motor", "x": 100 * i, "y": 600, "w": 48, "h": 48, "device": True,
                 "params": {"hasTag": True, "tag": f"M{i}"}, "bind": {"on": f"M{i}/state"}}
            return {**s, "render": render} if render else s
        valve = {"id": "V1", "kind": "valve", "x": 50, "y": 300, "w": 48, "h": 48, "device": True,
                 "params": {"vertical": True}, "bind": {"open": "V1_open"}, "render": "view"}
        return {"schema": "cadre-hmi-screen/1", "screen": {"route": "/page_a"},
                "symbols": [motor(1), motor(2, "view"), motor(3), valve]}

    def test_a_symbol_on_the_library_view_is_not_counted(self):
        plan = glass_gates.symbols_plan([self.page()])["/page_a"]
        self.assertEqual(plan["counts"], {"motor": 2})
        self.assertEqual([(o["kind"], o["rank"]) for o in plan["opens"]], [("motor", 0), ("motor", 1)])

    def test_the_readouts_count_the_module_components_only(self):
        from hmi.screen import module_drawn
        page = self.page()
        self.assertEqual([module_drawn(s) for s in page["symbols"]], [True, False, True, False])


class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.model, cls.bridge = make(cls.dir)
        cls.descs = glass_gates.descriptors_of(cls.bridge)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def plan(self, raise_alarm=True, gates=None):
        return glass_gates.plan_of(self.model, self.descs, "http://localhost:8088/data/perspective/client/" + PROJECT,
                                   (1920, 1080), gates or list(glass_gates.GATES), raise_alarm)

    def test_the_plan_names_the_origin_only_never_the_path(self):
        self.assertEqual(self.plan()["base"], "http://localhost:8088")

    def test_the_plan_holds_every_gate_with_its_inputs(self):
        p = self.plan()
        self.assertEqual(p["gates"], list(glass_gates.GATES))
        self.assertEqual(p["search"]["route"], "/overview")
        self.assertEqual((p["search"]["page"]["query"], p["search"]["page"]["route"]), ("Pump station", "/pumpstation"))
        self.assertEqual(p["search"]["device"]["query"], "PUMP01")
        self.assertEqual(p["search"]["device"]["row"], "Pump 1")
        self.assertEqual(p["zoom"]["route"], "/pumpstation")
        self.assertEqual(p["zoom"]["device"], "PUMP01")
        self.assertEqual(p["search"]["none"], "zzqq")
        self.assertEqual(p["zoom"]["steps"], glass_gates.ZOOM_STEPS)
        self.assertIn("/pumpstation", p["routes"])
        self.assertIn("/aeration", p["routes"])          # a stub page's route is opened too
        self.assertIn("/alerts", p["routes"])
        self.assertIn("/component-test", p["routes"])
        self.assertEqual(p["window"], {"w": 1920, "h": 1080})

    def test_the_search_device_is_one_with_a_library_faceplate(self):
        d = self.plan()["search"]["device"]
        self.assertNotEqual(self.model["devices"][d["faceplate"]]["faceplate"], "empty")

    def test_readouts_and_colour_come_from_the_build(self):
        p = self.plan()
        self.assertEqual(p["readouts"]["/pumpstation"]["module"], 3)       # two pumps and a valve: the module's On/Off kinds
        self.assertEqual(p["readouts"]["/overview"]["module"], 2)       # the design's readout and its switch (the module's since B1)
        self.assertIn("/pumpstation", p["colour"]["with_medium"])
        self.assertIn("/overview", p["colour"]["without_medium"])

    def test_the_columns_are_the_readouts_that_share_an_x(self):
        cols = self.plan()["columns"]["/overview"]
        self.assertEqual([c["count"] for c in cols], [2])
        self.assertEqual(cols[0]["x"], 400)

    def test_the_alarm_is_one_source_tag_under_the_tag_root(self):
        a = self.plan()["alarm"]
        self.assertEqual(a["tag"], "[default]cadre_hmi_plant/src/PUMP01_IFAIL")
        self.assertEqual((a["raise"], a["clear"]), (True, False))
        self.assertEqual(a["alarm"], "PUMP01_AFAIL")

    def test_without_raise_alarm_there_is_no_alarm_in_the_plan(self):
        p = self.plan(raise_alarm=False)
        self.assertIsNone(p["alarm"])
        self.assertIsNone(p["banner"])
        self.assertIsNone(p["ack"])

    def test_the_banner_rule_follows_the_alarms_node_and_subtree(self):
        p = self.plan()
        self.assertEqual(set(p["banner"]["shows"]) | set(p["banner"]["hides"]),
                         {x["route"] for x in self.model["pages"] if x["built"]})
        self.assertIn("/pumpstation", p["banner"]["shows"])

    def test_the_fill_gate_knows_each_pages_canvas(self):
        f = {x["route"]: x["canvas"] for x in self.plan()["fill"]}
        self.assertEqual(f["/overview"], {"w": 1580, "h": 600})

    def test_routes_include_the_designs_page_and_support_routes(self):
        nav = {"entries": [{"id": "menu:a", "kind": "menu", "target": "X"}]}      # block 12 names no route
        design = {"routes": [{"target": "menu:a", "treatment": "page", "route": "/from-the-design"},
                             {"target": "menu:b", "treatment": "support", "route": "/trends"},
                             {"target": "popup:c", "treatment": "faceplate", "device": "D"}]}
        plan = glass_gates.plan_of(self.model, self.descs, "http://x/y", (1280, 800), ["routes"], False, nav, design)
        self.assertIn("/from-the-design", plan["routes"])
        self.assertIn("/trends", plan["routes"])
        self.assertEqual(glass_gates.navtable_routes(nav, design), ["/from-the-design", "/trends"])
        self.assertEqual(glass_gates.navtable_routes(nav), [])

    def test_only_routes_limits_the_page_by_page_gates_and_keeps_the_others(self):
        whole = self.plan()
        self.assertNotIn("only_routes", whole)
        only = glass_gates.plan_of(self.model, self.descs, "http://localhost:8088/data/perspective/client/" + PROJECT,
                                   (1920, 1080), list(glass_gates.GATES), True, only_routes=["/pumpstation"])
        self.assertEqual(only["only_routes"], ["/pumpstation"])
        self.assertEqual(list(only["readouts"]), ["/pumpstation"])
        self.assertEqual(only["colour"], {"with_medium": ["/pumpstation"], "without_medium": []})
        self.assertEqual(only["columns"], {k: v for k, v in whole["columns"].items() if k == "/pumpstation"})
        self.assertEqual([f["route"] for f in only["fill"]], ["/pumpstation"])
        self.assertEqual(list(only["symbols"]), ["/pumpstation"])
        self.assertEqual(only["fill_after_dock"], whole["fill"][-1]["route"])     # the dock steps keep their page
        for key in ("search", "zoom", "menus", "panels", "alarm", "alarms", "banner", "ack", "testpage"):
            self.assertEqual(only[key], whole[key], key)
        self.assertEqual(glass_gates.PAGE_GATES, ("readouts", "colour", "sizes", "fill", "routes", "symbols"))
        none = glass_gates.plan_of(self.model, self.descs, "http://x/y", (1920, 1080), ["symbols"], False, only_routes=[])
        self.assertEqual((none["readouts"], none["fill"], none["symbols"], none["columns"]), ({}, [], {}, {}))
        self.assertIn("--only-routes", glass_gates.skip_reason("symbols", none))
        self.assertEqual(glass_gates.skip_reason("symbols", whole), None)

    def test_only_routes_limits_the_routes_gate_and_keeps_a_route_no_descriptor_draws(self):
        whole = self.plan()
        page_routes = {d["screen"]["route"] for d in self.descs}
        frame = [r for r in whole["routes"] if r not in page_routes]
        self.assertIn("/alerts", frame)
        self.assertIn("/trends", frame)                    # a support route: no descriptor draws it
        self.assertIn("/aeration", page_routes)            # a page with a descriptor
        only = glass_gates.plan_of(self.model, self.descs, "http://x/y", (1920, 1080), ["routes"], False,
                                   only_routes=["/pumpstation"])
        self.assertEqual(only["routes"], [r for r in whole["routes"] if r == "/pumpstation" or r in frame])   # order kept
        self.assertNotIn("/overview", only["routes"])
        self.assertNotIn("/aeration", only["routes"])
        none = glass_gates.plan_of(self.model, self.descs, "http://x/y", (1920, 1080), ["routes"], False, only_routes=[])
        self.assertEqual(none["routes"], frame)
        self.assertEqual(whole["routes"], self.plan(gates=["routes"])["routes"])    # a full plan lists every route

    def test_the_readouts_step_found_names_the_count_and_the_devices_without_on_or_off(self):
        devs = [{"text": "On"}, {"text": "Off"}, {"text": "45 %"}, {"text": ""}]
        self.assertEqual(glass_gates.readout_found(devs), {"count": 4, "without_on_off": ["45 %", ""]})
        many = [{"text": f"x{i}"} for i in range(12)]
        self.assertEqual(glass_gates.readout_found(many)["without_on_off"], [f"x{i}" for i in range(8)])
        self.assertEqual(glass_gates.readout_found([]), {"count": 0, "without_on_off": []})

    def test_every_module_tag_is_an_element_the_module_defines(self):
        """The readouts selector counted no valve while it named `obc-valve` and `obc-analogvalve` (COB-194)."""
        comps = json.loads((ROOT / "module" / "components.json").read_text(encoding="utf-8"))
        elements = {c["element"] for c in comps.values()}
        for kind, tag in glass_gates.MODULE_TAGS.items():
            self.assertIn(tag, elements, kind)
        self.assertEqual(glass_gates.MODULE_TAGS["valve"], "obc-digital-valve")
        self.assertEqual(glass_gates.MODULE_TAGS["analogvalve"], "obc-analog-valve")

    def test_the_plan_is_a_function_of_its_inputs(self):
        self.assertEqual(json.dumps(self.plan(), sort_keys=True), json.dumps(self.plan(), sort_keys=True))

    def test_a_base_that_is_not_http_is_a_fault(self):
        with self.assertRaises(glass_gates.Fault):
            glass_gates.origin_of("file:///x")

    def test_the_schema_has_the_registry_identifier_and_keeps_the_plan(self):
        schema = json.loads((ROOT / "schemas" / "cadre-hmi-glass-gates-1.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "cadre-hmi-glass-gates/1")

    # ---- the command before any input --------------------------------------------------------
    def test_faults_exit_1_before_anything_is_written(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "o"
            base = ["--base", "http://localhost:8088/x", "--model", str(self.dir / "model" / "model.json"),
                    "--build", str(self.bridge), "--out", str(out)]
            self.assertEqual(glass_gates.main(base + ["--gates", "nope"]), 1)
            self.assertEqual(glass_gates.main(base + ["--window", "big"]), 1)
            bad = list(base)
            bad[bad.index("--base") + 1] = "ftp://h/x"
            self.assertEqual(glass_gates.main(bad), 1)
            self.assertEqual(glass_gates.main(["--base", "http://h/x", "--model", str(self.bridge / "build.json"),
                                               "--build", str(self.bridge), "--out", str(out)]), 1)
            self.assertFalse((out / "plan.json").exists())

    def test_an_alarm_source_outside_the_allowed_roots_stops_everything(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "o"
            code = glass_gates.main(["--base", "http://localhost:8088/data/perspective/client/" + PROJECT,
                                     "--model", str(self.dir / "model" / "model.json"), "--build", str(self.bridge),
                                     "--raise-alarm", "--allowed-root", "[default]somewhere_else", "--out", str(out)],
                                    deploy=mock.Mock())
            self.assertEqual(code, 1)
            self.assertFalse((out / "plan.json").exists())

    def test_no_secret_and_no_client_name_in_the_plan(self):
        text = json.dumps(self.plan())
        self.assertNotIn("eng02", text.lower())
        self.assertNotIn("password", text.lower())


@unittest.skipUnless(HAVE_BROWSER, "Playwright is not importable here; run under ctig's .venv")
class FakeGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.model, cls.bridge = make(cls.dir)
        cls.descs = glass_gates.descriptors_of(cls.bridge)
        login = cls.dir / "login.properties"
        login.write_text("user=tester\npassword=not-a-real-secret\n", encoding="utf-8")
        cls.login = str(login)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def config(self, shows=None):
        from glass_fake import FakeGateway  # noqa: F401
        plan = glass_gates.plan_of(self.model, self.descs, "http://x/y", (1280, 800), list(glass_gates.GATES), True)
        pages, devices, tags = [], [], []
        routes = {p["id"]: p["route"] for p in self.model["pages"]}
        for p in self.model["pages"]:
            d = next((x for x in self.descs if x["screen"]["route"] == p["route"]), None)
            objects = []
            for s in (d or {}).get("symbols", []):
                if s["kind"] in glass_gates.MODULE_TAGS:
                    objects.append({"el": glass_gates.MODULE_TAGS[s["kind"]], "text": "On", "x": s["x"], "y": s["y"], "w": s["w"],
                                    "device": glass_gates.device_of(s)})
                elif s["kind"] == "readout":
                    objects.append({"el": "obc-readout", "text": "12.5 A", "x": s["x"], "y": s["y"], "w": s["w"]})
            pages.append({"id": p["id"], "title": p["title"], "route": p["route"], "canvas": {"w": 1580, "h": 600},
                          "objects": objects, "medium": p["route"] in plan["colour"]["with_medium"]})
        for t, dv in self.model["devices"].items():
            if dv["faceplate"] != "empty":
                devices.append({"tag": t, "label": dv["label"], "route": routes[dv["page"]]})
        for t in self.model["tags"]:
            if t.get("page"):
                tags.append({"name": t["name"], "route": routes[t["page"]]})
        alarms = [{"tag": a["alarm"], "desc": a["desc"], "source": a["tag"],
                   "shows": plan["banner"]["shows"] if shows is None else shows} for a in plan["alarms"]]
        test = plan["testpage"]
        pages.append({"id": "ComponentTest", "title": "Component test", "route": test["route"],
                      "canvas": {"w": 1000, "h": 560}, "objects": [], "medium": False})
        return {"project": PROJECT, "root": "Site", "pages": pages, "devices": devices, "tags": tags, "alarms": alarms,
                "testpage": test}

    def run_gates(self, *extra, shows=None, fail_restore=False, env=True):
        from glass_fake import FakeDeploy, FakeGateway
        out = self.dir / f"glass{len(list(self.dir.glob('glass*')))}"
        with FakeGateway(self.config(shows)) as gw:
            fd = FakeDeploy(gw, {a["source"]: False for a in gw.config["alarms"]}, fail_restore=fail_restore)
            argv = ["--base", gw.base, "--model", str(self.dir / "model" / "model.json"), "--build", str(self.bridge),
                    "--window", "1280x800", "--settle", "0.04", "--out", str(out), *extra]
            with mock.patch.dict(os.environ, {"CADRE_TEST_LOGIN": self.login} if env else {}), \
                    mock.patch("builtins.print"):
                code = glass_gates.main(argv, deploy=fd)
            return code, out, gw, fd

    def doc(self, out):
        return json.loads((out / "gates.json").read_text(encoding="utf-8"))

    def test_every_gate_runs_to_its_end_on_the_fake_client_page(self):
        code, out, gw, fd = self.run_gates("--raise-alarm")
        doc = self.doc(out)
        report = {g["name"]: [s for s in g["steps"] if not s["ok"]] for g in doc["gates"]}
        self.assertEqual(code, 0, json.dumps({k: v for k, v in report.items() if v}, indent=1)[:4000])
        self.assertEqual([g["name"] for g in doc["gates"]], list(glass_gates.GATES))
        self.assertTrue(all(g["steps"] for g in doc["gates"]))

    def test_only_routes_visits_the_pages_listed_and_writes_the_filter_in_the_plan(self):
        code, out, gw, fd = self.run_gates("--gates", "fill,symbols,colour,routes", "--only-routes", "/pumpstation")
        doc = self.doc(out)
        self.assertEqual(code, 0, json.dumps([g for g in doc["gates"] if not g["ok"]])[:2000])
        self.assertEqual(json.loads((out / "plan.json").read_text(encoding="utf-8"))["only_routes"], ["/pumpstation"])
        gates = {g["name"]: g for g in doc["gates"]}
        for name in ("fill", "symbols", "colour"):
            pages = {glass_gates_step_page(s["action"]) for s in gates[name]["steps"]} - {None}
            self.assertEqual(pages, {"/pumpstation"}, name)
        self.assertTrue(any("after a docked faceplate" in s["action"] for s in gates["fill"]["steps"]))
        route_steps = gates["routes"]["steps"]                      # one step per route; the others are the frame's
        plan = json.loads((out / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual([x["action"] for x in route_steps], [f"{r}: the route opens" for r in plan["routes"]])
        self.assertTrue(all(x["expected"] == "opens" and x["found"] == "opened" and x["ok"] for x in route_steps))
        self.assertNotIn("/overview", plan["routes"])
        self.assertIn("/alerts", plan["routes"])
        self.assertEqual(glass_gates_step_page(route_steps[0]["action"]), plan["routes"][0])
        code, out, gw, fd = self.run_gates("--gates", "fill", "--only-routes", "pumpstation")
        self.assertEqual(code, 1)                                        # not a route: refused before any input
        self.assertFalse((out / "plan.json").exists())

    def test_the_readouts_gate_reports_the_count_and_the_devices_without_on_or_off(self):
        code, out, gw, fd = self.run_gates("--gates", "readouts")
        steps = self.doc(out)["gates"][0]["steps"]
        self.assertEqual(code, 0, json.dumps([x for x in steps if not x["ok"]])[:2000])
        first = next(x for x in steps if "shows On or Off" in x["action"])
        self.assertEqual(first["found"], {"count": first["expected"], "without_on_off": []})
        self.assertEqual(validate(self.doc(out), "cadre-hmi-glass-gates-1.json"), [])

    def test_the_symbols_gate_counts_the_module_symbols_and_opens_a_faceplate_from_a_click(self):
        code, out, gw, fd = self.run_gates("--gates", "symbols")
        doc = self.doc(out)
        steps = doc["gates"][0]["steps"]
        self.assertEqual(code, 0, json.dumps([x for x in steps if not x["ok"]])[:2000])
        self.assertTrue(any("opens its faceplate" in x["action"] for x in steps))
        self.assertTrue(any("symbols drawn" in x["action"] for x in steps))
        self.assertEqual(gw.writes, [])                       # a read only gate

    def test_the_lamps_and_the_test_panel_gates_use_the_test_page_the_descriptor_describes(self):
        plan = glass_gates.plan_of(self.model, self.descs, "http://x/y", (1280, 800), ["lamps"], True)
        t = plan["testpage"]
        self.assertEqual(t["route"], "/component-test")
        self.assertTrue(t["lamps"]["section"].startswith("Indicator"))
        self.assertIn("Lamp to 2 (alarm)", t["lamps"]["buttons"])
        self.assertEqual(t["alarms"]["raise_all"], "Raise all five")
        self.assertEqual(t["alarms"]["hold_s"], 65)
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "lamps,testpanel")
        names = {g["name"]: g for g in self.doc(out)["gates"]}
        self.assertEqual(code, 0, json.dumps({k: [x for x in g["steps"] if not x["ok"]] for k, g in names.items()})[:3000])
        self.assertEqual(len(names["testpanel"]["steps"]), 6)   # the sign-in and five
        self.assertEqual(len(names["lamps"]["steps"]), 2)      # the sign-in and the colours

    def test_routes_come_from_the_navigation_table_and_the_descriptors(self):
        nav = {"entries": [{"id": "n1", "target": "X", "route": "/from-the-navtable"}]}
        plan = glass_gates.plan_of(self.model, self.descs, "http://x/y", (1280, 800), ["routes"], False, nav)
        self.assertIn("/from-the-navtable", plan["routes"])
        for d in self.descs:
            self.assertIn(d["screen"]["route"], plan["routes"])
        self.assertEqual(len(plan["routes"]), len(set(plan["routes"])))
        dropped = [d for d in self.descs if d["screen"]["route"] != "/component-test"]
        self.assertNotIn("/component-test", glass_gates.plan_of(self.model, dropped, "http://x/y", (1280, 800), ["routes"],
                                                                False)["routes"])

    def test_the_document_validates_and_plan_json_was_written_first(self):
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "search,routes,alarm")
        doc = self.doc(out)
        self.assertEqual(validate(doc, "cadre-hmi-glass-gates-1.json"), [])
        plan = json.loads((out / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan, doc["plan"])
        self.assertLessEqual((out / "plan.json").stat().st_mtime, (out / "gates.json").stat().st_mtime)
        self.assertEqual(doc["base"], gw.base.split("/data")[0])

    def test_the_alarm_is_raised_and_put_back_through_the_lane(self):
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "alarm")
        self.assertEqual(code, 0)
        tag = "[default]cadre_hmi_plant/src/PUMP01_IFAIL"
        self.assertEqual([v for t, v in gw.writes if t == tag], [True, False])    # raised once, restored once
        self.assertFalse(gw.tags[tag])
        self.assertTrue(self.doc(out)["restored"])

    def test_without_raise_alarm_the_alarm_gates_are_skipped_and_nothing_is_written(self):
        code, out, gw, fd = self.run_gates()
        doc = self.doc(out)
        for g in doc["gates"]:
            if g["name"] in glass_gates.WRITES:
                self.assertIn("skipped", g)
                self.assertTrue(g["ok"])
        self.assertEqual(gw.writes, [])
        self.assertEqual(fd.imports, [])

    def test_zoom_records_the_frame_before_and_after_each_step(self):
        code, out, gw, fd = self.run_gates("--gates", "zoom")
        doc = self.doc(out)
        self.assertEqual(code, 0, json.dumps([s for g in doc["gates"] for s in g["steps"] if not s["ok"]])[:2000])
        self.assertEqual(set(doc["frame_before"]), set(doc["frame_after"]))
        self.assertGreaterEqual(len(doc["frame_before"]), 6)
        for k, b in doc["frame_before"].items():
            self.assertEqual(b, doc["frame_after"][k], k)             # the frame's rectangles equal

    def test_a_failed_restore_is_reported_and_exits_2(self):
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "alarm", fail_restore=True)
        self.assertEqual(code, 2)
        self.assertFalse(self.doc(out)["restored"])

    def test_a_banner_that_does_not_show_the_alarm_fails_the_banner_gate(self):
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "alarm,banner", shows=[])
        self.assertEqual(code, 2)
        names = {g["name"]: g["ok"] for g in self.doc(out)["gates"]}
        self.assertFalse(names["alarm"] and names["banner"])
        self.assertTrue(self.doc(out)["restored"])      # put back although a gate failed

    def test_without_the_test_login_the_ack_gate_fails_and_says_why(self):
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "alarm,ack", env=False)
        ack = next(g for g in self.doc(out)["gates"] if g["name"] == "ack")
        self.assertFalse(ack["ok"])
        self.assertIn("CADRE_TEST_LOGIN", ack["steps"][0]["expected"])

    def test_the_login_is_never_written_to_a_document(self):
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "alarm,ack")
        for f in out.rglob("*.json"):
            text = f.read_text(encoding="utf-8")
            self.assertNotIn("not-a-real-secret", text)
            self.assertNotIn("tester", text)

    def test_accepted_rows_turn_a_failed_step_into_an_accepted_one(self):
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "alarm,banner", shows=[])
        failed = [f"{g['name']}:{s['action']}" for g in self.doc(out)["gates"] for s in g["steps"] if not s["ok"]]
        acc = dump(self.dir / "accepted_rows.json", failed)
        code, out, gw, fd = self.run_gates("--raise-alarm", "--gates", "alarm,banner", "--accepted-rows", str(acc), shows=[])
        self.assertEqual(code, 0)
        self.assertTrue(any(s.get("accepted") for g in self.doc(out)["gates"] for s in g["steps"]))


if __name__ == "__main__":
    unittest.main()
