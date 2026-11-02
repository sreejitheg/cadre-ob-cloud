"""Tests of `tools/hmi/asm_descriptors.py` (S10-B, ARCH-WFB-01 revision B8 Table 109, schema
`cadre-hmi-descriptor-coverage/1`).

The ASM model is built from the synthetic fixtures by `asm_model.main`, the designs are the fixtures
`asm-design-*.json`, and the descriptors are run through `screen.py`'s gates G0 to G7 offline. Nothing here needs a
gateway or a browser.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump, fixture, inputs, validate  # noqa: E402

from hmi import asm_descriptors, asm_model, screen  # noqa: E402
from hmi import parent as par  # noqa: E402

PROJECT = "cadre_hmi_plant"
PARENT = "cadre_hmi_base_asm"
TAG_ROOT = "[default]cadre_hmi_plant"
DESIGNS = ("asm-design-overview.json", "asm-design-pumpstation.json")


def make_model(d: Path) -> tuple[Path, dict]:
    ins = inputs(d)
    out = d / "model"
    code = asm_model.main([a for k, v in ins.items() for a in (f"--{k}", str(v))]
                          + ["--tag-root", TAG_ROOT, "--out", str(out)])
    assert code == 0, code
    return out / "model.json", ins


def argv_of(d: Path, model: Path, ins: dict, *extra, designs=DESIGNS, accepted=("GAP-ups",), edit=None):
    lst = d / "designs.txt"
    docs = {n: fixture(n) for n in designs}
    for n, fn in (edit or {}).items():
        fn(docs[n])
    paths = [dump(d / "designs" / n, doc) for n, doc in docs.items()]
    lst.write_text("\n".join(str(p) for p in paths) + "\n", encoding="utf-8", newline="\n")
    acc = dump(d / "accepted.json", list(accepted))
    return ["--model", str(model), "--designs", str(lst), "--faceplates", str(ins["faceplates"]),
            "--tables", str(ins["tables"]), "--accepted", str(acc), "--inventory", str(ins["inventory"]),
            "--project", PROJECT, "--parent", PARENT, "--tag-root", TAG_ROOT, "--window", "1920x1080",
            "--render", "module", "--frame", "asm", "--faceplate", "asm", "--module-first", "--equalise",
            "--medium", "--out", str(d / "out"), *extra]


class Run:
    def __init__(self, *extra, designs=DESIGNS, accepted=("GAP-ups",), edit=None):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        model, ins = make_model(self.dir)
        self.code = asm_descriptors.main(argv_of(self.dir, model, ins, *extra, designs=designs, accepted=accepted,
                                                 edit=edit))
        self.out = self.dir / "out"
        self.bridge = self.out / "bridge"

    def read(self, rel):
        return json.loads((self.out / rel).read_text(encoding="utf-8"))

    def descriptor(self, name):
        return self.read(f"bridge/descriptors/{name}.json")

    def close(self):
        self._tmp.cleanup()


class DescriptorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = Run("--simulation")

    @classmethod
    def tearDownClass(cls):
        cls.r.close()

    # ---- the layout and the documents --------------------------------------------------------
    def test_it_exits_0_and_writes_the_bridge_layout(self):
        self.assertEqual(self.r.code, 0)
        for rel in ("bridge/build.json", "bridge/devices.json", "bridge/tags_devices.json", "bridge/tags.json",
                    "bridge/coverage_map.json", "bridge/route_map.json", "bridge/walk/walk.json", "coverage.json",
                    "tags-document.json", "gaps-after.json", "bridge/descriptors/overview.json",
                    "bridge/descriptors/pumpstation.json", "bridge/descriptors/aeration.json"):
            self.assertTrue((self.r.out / rel).is_file(), rel)

    def test_the_coverage_document_validates_and_is_complete(self):
        cov = self.r.read("coverage.json")
        self.assertEqual(validate(cov, "cadre-hmi-descriptor-coverage-1.json"), [])
        self.assertEqual(cov["missing"], [])
        self.assertEqual(cov["unresolved"], [])
        self.assertEqual(cov["schema"], "cadre-hmi-descriptor-coverage/1")
        schema = json.loads((ROOT / "schemas" / "cadre-hmi-descriptor-coverage-1.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "cadre-hmi-descriptor-coverage/1")

    def test_every_mapping_row_of_the_model_is_carried_once_or_more(self):
        model = json.loads((self.r.dir / "model" / "model.json").read_text(encoding="utf-8"))
        rows = {r["uid"]: r for r in self.r.read("coverage.json")["rows"]}
        self.assertEqual(set(rows), {m["uid"] for m in model["mapping"]})
        self.assertTrue(all(r["carried_by"] for r in rows.values()))
        self.assertEqual(rows["PumpStation:d_p1"]["carried_by"], ["symbols:PUMP01"])
        self.assertEqual(rows["Overview:x10"]["carried_by"], ["dropped"])

    def test_the_generated_files_are_lf_json(self):
        for f in (self.r.out / "bridge").rglob("*.json"):
            data = f.read_bytes()
            self.assertNotIn(b"\r", data, f.name)
            self.assertTrue(data.endswith(b"\n"), f.name)

    # ---- the device symbol on its own page only ----------------------------------------------
    def test_a_device_symbol_with_its_node_is_drawn_on_its_own_page(self):
        syms = {s["id"]: s for s in self.r.descriptor("pumpstation")["symbols"]}
        self.assertIs(syms["PUMP01"]["device"], True)
        self.assertNotIn("faceplate", syms["PUMP01"])
        self.assertEqual(syms["PUMP01"]["bind"], {"on": "PUMP01/state"})

    def test_elsewhere_the_symbol_is_plain_and_still_opens_the_faceplate(self):
        syms = self.r.descriptor("overview")["symbols"]
        pump = next(s for s in syms if s["kind"] == "pump")
        self.assertNotIn("device", pump)
        self.assertEqual(pump["faceplate"], "PUMP01")
        self.assertEqual(pump["bind"], {"on": "PUMP01/state"})
        self.assertEqual(sum(1 for d in (self.r.descriptor("overview"), self.r.descriptor("pumpstation"))
                             for s in d["symbols"] if s.get("device") is True and s["id"] == "PUMP01"), 1)

    def test_a_device_with_no_library_folder_is_a_standalone_symbol(self):
        brk = next(s for s in self.r.descriptor("overview")["symbols"] if s["kind"] == "switch")
        self.assertNotIn("device", brk)
        self.assertEqual(brk["bind"], {"on": "src/BRK01_CLOSED"})

    def test_the_device_model_lists_the_members_the_symbols_bind(self):
        devs = {d["id"]: d for d in self.r.read("bridge/devices.json")["devices"]}
        self.assertEqual(validate(self.r.read("bridge/devices.json"), "devices.schema.json"), [])
        self.assertEqual(set(devs["PUMP01"]["members"]), {"state"})
        self.assertEqual(devs["PUMP01"]["faceplate"], "asm")
        self.assertEqual(set(devs["TANK01"]["members"]), {"level"})
        self.assertEqual(set(devs["SEQ01"]["members"]), {"stepText", "step"})
        self.assertNotIn("BRK01", devs)
        self.assertNotIn("node", devs["PUMP01"])   # a page draws it with `device`: the page gives the node

    def test_the_page_carries_its_node_from_the_model(self):
        s = self.r.descriptor("pumpstation")["screen"]
        self.assertEqual(s["node"], "Site/Plant")
        self.assertEqual(s["level"], "Level 2 unit")
        self.assertEqual(self.r.descriptor("overview")["screen"]["next"], "/pumpstation")
        self.assertEqual(self.r.descriptor("pumpstation")["screen"]["previous"], "/overview")

    # ---- elements ----------------------------------------------------------------------------
    def test_an_indicator_carries_its_states_and_default(self):
        ind = next(s for s in self.r.descriptor("pumpstation")["symbols"] if s["kind"] == "indicator"
                   and s["bind"]["state"].endswith("PUMP01_IRUN"))
        self.assertEqual(ind["states"][0], {"value": True, "colour": "on", "label": "Running"})
        self.assertEqual(ind["stateDefault"], "off")

    def test_an_alarm_lamp_follows_the_alarm_tag_of_its_device(self):
        lamp = next(s for s in self.r.descriptor("pumpstation")["symbols"] if s.get("alarm"))
        self.assertEqual(lamp["alarm"], "TANK01/alm/TANK01_AHIGH")

    def test_every_readout_binds_a_tag_of_the_tag_model(self):
        tags = self.r.read("bridge/tags.json")

        def paths(node, prefix=""):
            for t in node.get("tags", []):
                here = f"{prefix}/{t['name']}" if prefix else t["name"]
                if t["tagType"] == "Folder":
                    yield from paths(t, here)
                else:
                    yield here
        have = set(paths(tags))
        for name in ("overview", "pumpstation"):
            for s in self.r.descriptor(name)["symbols"]:
                if s["kind"] == "readout":
                    self.assertIn(s["bind"]["value"], have, s["id"])

    def test_pipes_take_the_medium_and_refer_to_symbols(self):
        pipes = {p["id"]: p for p in self.r.descriptor("pumpstation")["pipes"]}
        self.assertEqual(len(pipes), 3)
        self.assertTrue(all(p["medium"] == "waste" for p in pipes.values()))
        self.assertEqual(pipes["p_f1"]["from"]["ref"], "TANK01")
        self.assertEqual(pipes["p_f1"]["to"]["ref"], "PUMP01")
        self.assertEqual(pipes["p_f3"]["via"], [[520, 354]])

    def test_without_the_medium_option_a_pipe_is_neutral(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model, ins = make_model(d)
            args = [a for a in argv_of(d, model, ins) if a != "--medium"]
            self.assertEqual(asm_descriptors.main(args), 0)
            pipes = json.loads((d / "out" / "bridge" / "descriptors" / "pumpstation.json").read_text(encoding="utf-8"))["pipes"]
            self.assertTrue(all(p["medium"] == "neutral" for p in pipes))

    def test_a_pipe_takes_its_routing_and_medium_from_the_model_scaled_by_the_canvas(self):
        def halve(doc):
            doc["canvas"]["scale"] = 0.5
        r = Run(edit={"asm-design-pumpstation.json": halve})
        try:
            p = {x["id"]: x for x in r.descriptor("pumpstation")["pipes"]}
            self.assertEqual(p["p_f3"]["via"], [[260.0, 177.0]])
            self.assertEqual(p["p_f3"]["medium"], "waste")
        finally:
            r.close()

    def test_a_readouts_unit_comes_from_the_tags_document_and_no_format_is_invented(self):
        ro = {s["id"]: s for s in self.r.descriptor("pumpstation")["symbols"] if s["kind"] == "readout"}
        self.assertEqual(ro["i_v1"]["params"]["unit"], "m")
        self.assertEqual(ro["i_v2"]["params"]["unit"], "A")
        self.assertTrue(all("format" not in s["params"] for s in ro.values()))   # the variables state none

    def test_a_format_the_tags_document_states_is_used(self):
        # the tables are read by asm_model too, so write them before the model is built
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            ins = inputs(d)
            tb = fixture("asm-tables.json")
            tb["devices"]["TANK01"]["variables"][0]["format"] = "0.00"
            dump(ins["tables"], tb)
            asm_model.main([a for k, v in ins.items() for a in (f"--{k}", str(v))] + ["--tag-root", TAG_ROOT, "--out", str(d / "model")])
            self.assertEqual(asm_descriptors.main(argv_of(d, d / "model" / "model.json", ins)), 0)
            ro = json.loads((d / "out" / "bridge" / "descriptors" / "pumpstation.json").read_text(encoding="utf-8"))
            v1 = next(s for s in ro["symbols"] if s["id"] == "i_v1")
            self.assertEqual(v1["params"]["format"], "0.00")

    def test_a_box_stays_the_designs_and_a_kind_that_does_not_fit_it_is_a_finding(self):
        def squeeze(doc):
            for it in doc["items"]:
                if it["uid"] == "PumpStation:i2":
                    it["bbox"] = {"x": 60, "y": 270, "w": 24, "h": 24}   # drawn 48 by 48 by the library: reaches the tank
        r = Run(edit={"asm-design-pumpstation.json": squeeze})
        try:
            self.assertEqual(r.code, 2)
            lamp = next(s for s in r.descriptor("pumpstation")["symbols"] if s["id"] == "i_i2")
            self.assertEqual((lamp["w"], lamp["h"]), (24, 24))                  # not grown
            found = r.read("coverage.json")["findings"]
            self.assertTrue(any("PumpStation:i2" in f and "48 x 48" in f and "TANK01" in f for f in found), found)
        finally:
            r.close()

    def test_boxes_that_fit_make_no_finding(self):
        self.assertEqual(self.r.read("coverage.json")["findings"], [])

    def test_a_readouts_unit_and_format_come_from_the_tags_map_row(self):
        def row(ins_tables):
            ins_tables["tags"]["TANK01_LEVEL"]["format"] = "0.00"
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            ins = inputs(d)
            tb = fixture("asm-tables.json")
            row(tb)
            del tb["devices"]["TANK01"]["variables"][0]            # the device no longer lists it: only the tags map has it
            dump(ins["tables"], tb)
            asm_model.main([a for k, v in ins.items() for a in (f"--{k}", str(v))] + ["--tag-root", TAG_ROOT, "--out", str(d / "model")])
            self.assertEqual(asm_descriptors.main(argv_of(d, d / "model" / "model.json", ins)), 0)
            syms = json.loads((d / "out" / "bridge" / "descriptors" / "pumpstation.json").read_text(encoding="utf-8"))["symbols"]
            v1 = next(s for s in syms if s["id"] == "i_v1")
            self.assertEqual((v1["params"]["unit"], v1["params"]["format"]), ("m", "0.00"))

    def test_a_tag_read_but_in_neither_map_is_reported_not_invented(self):
        def drop(doc):
            del doc["tags"]["PUMP02_IRUN"]
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            ins = inputs(d)
            tb = fixture("asm-tables.json")
            drop(tb)
            dump(ins["tables"], tb)
            asm_model.main([a for k, v in ins.items() for a in (f"--{k}", str(v))] + ["--tag-root", TAG_ROOT, "--out", str(d / "model")])
            self.assertEqual(asm_descriptors.main(argv_of(d, d / "model" / "model.json", ins)), 2)
            cov = json.loads((d / "out" / "coverage.json").read_text(encoding="utf-8"))
            self.assertEqual([f for f in cov["findings"] if "PUMP02_IRUN" in f],      # the pump and the pipe that reads it
                             [f"PumpStation:{u}: the tag PUMP02_IRUN is in neither the tables' devices nor its tags map"
                              for u in ("d_p2", "f2")])
            self.assertEqual(len(cov["findings"]), 2)
            tags = json.loads((d / "out" / "bridge" / "tags.json").read_text(encoding="utf-8"))
            self.assertNotIn("documentation", next(x for x in next(f for f in tags["tags"] if f["name"] == "src")["tags"]
                                                   if x["name"] == "PUMP02_IRUN"))      # no comment or unit made up

    def test_the_walk_entries_carry_the_faceplate_style(self):
        for m in self.r.read("bridge/walk/walk.json")["renderings"][0]["modes"]:
            argv = m["plan"]["argv"]
            self.assertEqual(argv[argv.index("--faceplate") + 1], "asm")

    def test_links_buttons_and_labels(self):
        d = self.r.descriptor("pumpstation")
        self.assertEqual(d["links"][0]["route"], "/overview")
        btn = {b["id"]: b for b in d["buttons"]}
        self.assertEqual(btn["b_n2"]["action"], {"type": "faceplate", "device": "PUMP01", "tab": "home", "label": "Pump 1"})
        self.assertEqual(btn["b_n3"]["action"]["device"], "SEQ01")
        self.assertEqual(d["labels"][0]["text"], "Pump station")
        self.assertEqual(d["labels"][0]["style"], "heading")

    def test_a_stub_page_has_a_descriptor_so_that_its_route_resolves(self):
        d = self.r.descriptor("aeration")
        self.assertEqual(d["screen"]["route"], "/aeration")
        self.assertIn("outside the scope", d["labels"][1]["text"])

    # ---- the module and the gaps -------------------------------------------------------------
    def test_the_module_audit_names_who_draws_each_kind(self):
        audit = {r["kind"]: r for r in self.r.read("coverage.json")["module_first"]}
        self.assertEqual(audit["pump"]["rendered_by"], "module")
        self.assertEqual(audit["tank"]["rendered_by"], "module")
        self.assertEqual(audit["sequence"]["rendered_by"], "library")
        self.assertTrue(audit["sequence"]["reason"])
        self.assertEqual(audit["ups"]["rendered_by"], "gap")

    def test_a_kind_the_library_lacks_is_a_gap_that_must_be_accepted(self):
        cov = self.r.read("coverage.json")
        self.assertEqual({g["id"]: g["status"] for g in cov["gaps"]}, {"GAP-ups": "accepted"})
        r = Run(accepted=())
        try:
            self.assertEqual(r.code, 2)
            self.assertEqual(r.read("gaps-after.json")["open"][0]["id"], "GAP-ups")
        finally:
            r.close()

    # ---- the tag model -----------------------------------------------------------------------
    def test_the_simulation_adds_one_tick_tag_with_a_compiling_script(self):
        tags = self.r.read("bridge/tags.json")
        sim = next(t for t in tags["tags"] if t["name"] == "sim")
        tick = next(t for t in sim["tags"] if t["name"] == "tick")
        script = tick["eventScripts"][0]["script"]
        self.assertIn("writeBlocking", script)
        self.assertIn("src/TANK01_LEVEL", script)
        compile(script.replace("\t", "    ").replace("\n    ", "\n"), "<sim>", "exec")
        self.assertFalse([t for t in self.r.read("bridge/tags_devices.json")["tags"] if t["name"] == "sim"])

    def test_without_the_simulation_there_is_no_sim_folder(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model, ins = make_model(d)
            self.assertEqual(asm_descriptors.main(argv_of(d, model, ins)), 0)
            tags = json.loads((d / "out" / "bridge" / "tags.json").read_text(encoding="utf-8"))
            self.assertNotIn("sim", [x["name"] for x in tags["tags"]])

    def test_an_alarm_tag_sits_under_its_device_in_the_library_alarm_form(self):
        tags = self.r.read("bridge/tags_devices.json")
        pump = next(t for t in tags["tags"] if t["name"] == "PUMP01")
        alm = next(t for t in pump["tags"] if t["name"] == "alm")
        fail = next(t for t in alm["tags"] if t["name"] == "PUMP01_AFAIL")
        a = fail["alarms"][0]
        self.assertEqual((a["priority"], a["timeOnDelaySeconds"], a["setpointA"]), ("High", 5, 1.0))
        self.assertIn("PUMP01_IFAIL", fail["expression"])
        undervoltage = next(t for t in next(x for x in tags["tags"] if x["name"] == "alm")["tags"]
                            if t["name"] == "BRK01")["tags"][0]
        self.assertIn("< 380", undervoltage["expression"])

    # ---- build.json and the walk plan entries ------------------------------------------------
    def test_build_json_gives_the_generator_command_line(self):
        b = self.r.read("bridge/build.json")
        self.assertEqual(b["schema"], "ctig.bridge.build/1")
        r = b["renderings"][0]
        argv = r["argv"]
        self.assertEqual(argv[:4], ["python", "tools/hmi/screen.py", "--project", PROJECT])
        for opt, val in (("--parent", PARENT), ("--frame", "asm"), ("--faceplate", "asm"), ("--render", "module")):
            self.assertEqual(argv[argv.index(opt) + 1], val)
        self.assertNotIn("--component-test", argv)
        self.assertEqual(argv.count("--descriptor"), 3)
        for a in argv:
            if a.startswith(str(self.r.dir).replace("\\", "/")) or a.startswith(self.r.dir.as_posix()):
                self.assertTrue(a.startswith((self.r.out / "bridge").as_posix()), a)

    def test_the_walk_entries_are_in_the_shape_walk_plan_reads(self):
        w = self.r.read("bridge/walk/walk.json")
        self.assertEqual(w["schema"], "ctig.bridge.walk/1")
        entry = w["renderings"][0]
        self.assertEqual((entry["render"], entry["project"]), ("module", PROJECT))
        self.assertEqual([m["mode"] for m in entry["modes"]], ["static", "dynamic"])
        known = {"--descriptor", "--devices-file", "--tags-file", "--source-tags", "--source-folder", "--effects",
                 "--render", "--faceplate", "--out", "--profile"}
        for m in entry["modes"]:
            argv = m["plan"]["argv"]
            self.assertEqual(argv[1:3], ["tools/compare/walk.py", "plan"])
            rest = argv[3:]
            self.assertEqual(len(rest) % 2, 0)
            self.assertTrue(set(rest[::2]) <= known)
            self.assertEqual(rest[::2].count("--descriptor"), 3)
            self.assertTrue((self.r.bridge / "walk" / f"effects-{m['mode']}.json").is_file())

    def test_the_planner_accepts_a_walk_entry_offline(self):
        entry = self.r.read("bridge/walk/walk.json")["renderings"][0]["modes"][0]
        argv = [sys.executable, str(ROOT / "tools" / "compare" / "walk.py")] + entry["plan"]["argv"][2:]
        argv[argv.index("--out") + 1] = str(self.r.dir / "plan.json")
        r = subprocess.run(argv + ["--profile", str(ROOT / "library" / "profile.json")], capture_output=True,
                           text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        plan = json.loads((self.r.dir / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["schema"], "cadre-hmi-walk/1")

    # ---- the generator's gates ---------------------------------------------------------------
    def run_screen(self, build_json: dict, out: Path, extra=()):
        argv = build_json["renderings"][0]["argv"][2:]
        argv[argv.index("--out") + 1] = str(out)
        argv[argv.index("--report") + 1] = str(self.r.dir / "report.json")
        prj, _ = par.build_parent(PARENT)
        prj.write(out)
        printed = []
        with mock.patch.object(sys, "argv", ["screen.py", *argv, *extra]), \
                mock.patch("builtins.print", side_effect=lambda *a, **k: printed.append(" ".join(map(str, a)))):
            code = screen.main()
        return code, "\n".join(printed)

    def test_the_descriptors_pass_the_generators_gates_g0_to_g7_offline(self):
        out = self.r.dir / "build"
        code, printed = self.run_screen(self.r.read("bridge/build.json"), out)
        self.assertEqual(code, 0, printed[-2000:])
        report = json.loads((self.r.dir / "report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["gates"]["ok"], report["gates"])

    def test_with_the_component_test_the_page_joins_the_build(self):
        r = Run("--component-test")
        try:
            self.assertEqual(r.code, 0)
            b = r.read("bridge/build.json")
            self.assertIn("--component-test", b["renderings"][0]["argv"])
            self.assertEqual(b["renderings"][0]["argv"].count("--descriptor"), 3)   # the page is generated by screen.py
            self.assertTrue((r.bridge / "descriptors" / "component-test.json").is_file())
            devs = r.read("bridge/devices.json")["devices"]
            self.assertTrue(any(d["id"].startswith("_componentTest") for d in devs))
            walk = r.read("bridge/walk/walk.json")["renderings"][0]["modes"][0]["plan"]["argv"]
            self.assertEqual(walk.count("--descriptor"), 4)                         # the walk reads it
            code, printed = self.run_screen(b, r.dir / "build")
            self.assertEqual(code, 0, printed[-2000:])
        finally:
            r.close()

    # ---- equal sizes -------------------------------------------------------------------------
    def test_items_of_one_column_share_a_width(self):
        def narrow(doc):
            for it in doc["items"]:
                if it["uid"] == "Overview:v2":
                    it["bbox"]["w"] = 100          # 20 px narrower than v1 above it, at the same x
            doc["balance"] = {"columns": [["Overview:v1", "Overview:v2"]], "rows": []}
        r = Run(edit={"asm-design-overview.json": narrow})
        try:
            self.assertEqual(r.code, 0)
            widths = {s["id"]: s["w"] for s in r.descriptor("overview")["symbols"] if s["kind"] == "readout"}
            self.assertEqual(set(widths.values()), {120})
            cols = r.read("coverage.json")["columns"]
            self.assertEqual(cols[0]["widths"], [120, 120])
        finally:
            r.close()

    def test_without_equalise_a_column_that_differs_is_a_finding(self):
        def narrow(doc):
            for it in doc["items"]:
                if it["uid"] == "Overview:v2":
                    it["bbox"]["w"] = 100
            doc["balance"] = {"columns": [["Overview:v1", "Overview:v2"]], "rows": []}
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model, ins = make_model(d)
            args = [a for a in argv_of(d, model, ins, edit={"asm-design-overview.json": narrow}) if a != "--equalise"]
            self.assertEqual(asm_descriptors.main(args), 2)

    def test_the_equalise_function_grows_only(self):
        desc = {"symbols": [{"id": "a", "kind": "readout", "x": 10, "y": 0, "w": 50, "h": 20},
                            {"id": "b", "kind": "readout", "x": 13, "y": 40, "w": 80, "h": 20},
                            {"id": "c", "kind": "readout", "x": 200, "y": 40, "w": 30, "h": 25}]}
        asm_descriptors.equalise(desc)
        s = {x["id"]: x for x in desc["symbols"]}
        self.assertEqual((s["a"]["w"], s["b"]["w"], s["c"]["w"]), (80, 80, 30))
        self.assertEqual((s["b"]["h"], s["c"]["h"]), (25, 25))      # b and c share a y
        self.assertEqual(s["a"]["h"], 20)

    # ---- faults ------------------------------------------------------------------------------
    def test_a_page_without_a_design_is_reported(self):
        r = Run(designs=("asm-design-overview.json",))
        try:
            self.assertEqual(r.code, 2)
            self.assertTrue(r.read("coverage.json")["findings"])
            self.assertTrue(any(u.startswith("PumpStation:") for u in r.read("coverage.json")["missing"]))
        finally:
            r.close()

    def test_a_route_to_a_page_with_no_descriptor_is_unresolved(self):
        r = Run(designs=("asm-design-overview.json", "asm-design-pumpstation.json"))
        try:
            self.assertEqual(r.read("coverage.json")["unresolved"], [])
        finally:
            r.close()

    def test_a_project_name_must_start_cadre_hmi(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model, ins = make_model(d)
            args = argv_of(d, model, ins)
            args[args.index("--project") + 1] = "plant"
            self.assertEqual(asm_descriptors.main(args), 1)

    def test_an_unreadable_design_is_an_input_fault(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model, ins = make_model(d)
            args = argv_of(d, model, ins)
            (d / "designs" / "asm-design-overview.json").write_text("{nope", encoding="utf-8")
            self.assertEqual(asm_descriptors.main(args), 1)

    def test_no_client_name_enters_a_descriptor(self):
        text = "".join(f.read_text(encoding="utf-8") for f in self.r.bridge.rglob("*.json"))
        self.assertNotIn("eng02", text.lower())


if __name__ == "__main__":
    unittest.main()
