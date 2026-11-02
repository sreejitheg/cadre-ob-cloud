"""Tests of `tools/hmi/asm_model.py` (S10-B, ARCH-WFB-01 revision B8 Table 109, schema `cadre-hmi-asm-model/1`).

The inputs are the synthetic fixtures `tests/fixtures/asm-*.json` (placeholder names), written as a run folder by
`asm_support.inputs`. Nothing here needs a gateway or a browser.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, UNITS, dump, fixture, inputs, validate  # noqa: E402

from hmi import asm_model  # noqa: E402


def argv_of(ins: dict, out: Path, *extra, drop=()) -> list[str]:
    a = []
    for k, v in ins.items():
        if k not in drop:
            a += [f"--{k}", str(v)]
    return a + ["--tag-root", "[default]cadre_hmi_plant", "--hierarchy", "menu", "--out", str(out), *extra]


def build(d: Path, *extra, drop=(), mutate=None):
    ins = inputs(d)
    if mutate:
        mutate(ins)
    out = d / "model"
    code = asm_model.main(argv_of(ins, out, *extra, drop=drop))
    model = json.loads((out / "model.json").read_text(encoding="utf-8")) if (out / "model.json").exists() else None
    return code, model, out, ins


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.code, cls.model, cls.out, cls.ins = build(cls.dir)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_it_exits_0_and_the_document_validates_against_its_schema(self):
        self.assertEqual(self.code, 0)
        self.assertEqual(validate(self.model, "cadre-hmi-asm-model-1.json"), [])

    def test_the_schema_carries_the_registry_identifier(self):
        schema = json.loads((ROOT / "schemas" / "cadre-hmi-asm-model-1.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "cadre-hmi-asm-model/1")
        self.assertEqual(self.model["schema"], "cadre-hmi-asm-model/1")

    # ---- the hierarchy -----------------------------------------------------------------------
    def test_the_nodes_follow_the_menus_order(self):
        names = [n["name"] for n in self.model["nodes"]]
        self.assertEqual(names, ["Site", "Plant"])   # support targets are not nodes
        by = {n["name"]: n for n in self.model["nodes"]}
        self.assertIsNone(by["Site"]["parent"])
        self.assertEqual(by["Plant"]["parent"], by["Site"]["id"])
        self.assertEqual(by["Plant"]["pages"], ["Overview", "PumpStation", "Aeration"])

    def test_a_page_with_an_understanding_is_built_and_a_menu_target_without_one_is_a_stub(self):
        pages = {p["id"]: p for p in self.model["pages"]}
        self.assertEqual((pages["Overview"]["kind"], pages["Overview"]["built"]), ("mimic", True))
        self.assertEqual((pages["Aeration"]["kind"], pages["Aeration"]["built"]), ("stub", False))
        self.assertEqual(pages["PumpStation"]["route"], "/pumpstation")
        self.assertTrue(all(p["route"].startswith("/") for p in self.model["pages"]))
        self.assertEqual(len({p["route"] for p in self.model["pages"]}), len(self.model["pages"]))

    def test_a_popup_set_is_never_a_page(self):
        ids = {p["id"] for p in self.model["pages"]}
        self.assertFalse({"PUMP01_FP", "SEQ01_SP"} & ids)

    def test_the_contract_can_give_the_hierarchy_instead(self):
        with tempfile.TemporaryDirectory() as t:
            ins = inputs(Path(t))
            out = Path(t) / "m"
            args = argv_of(ins, out, drop=("menu",))
            args[args.index("--hierarchy") + 1] = "contract"
            self.assertEqual(asm_model.main(args), 0)
            m = json.loads((out / "model.json").read_text(encoding="utf-8"))
            self.assertEqual([n["name"] for n in m["nodes"]], ["Plant", "Pumping", "Aeration"])
            node_of = {p["id"]: p["node"] for p in m["pages"]}
            names = {n["id"]: n["name"] for n in m["nodes"]}
            self.assertEqual(names[node_of["PumpStation"]], "Pumping")
            self.assertEqual(names[node_of["Overview"]], "Plant")   # not listed in an area: the root
            self.assertEqual(validate(m, "cadre-hmi-asm-model-1.json"), [])

    # ---- the mapping -------------------------------------------------------------------------
    def test_every_entry_of_every_section_has_a_mapping_row_with_a_uid(self):
        self.assertEqual(self.model["unmapped"], [])
        uids = {r["uid"] for r in self.model["mapping"]}
        for name, file in (("Overview", "asm-understanding-overview.json"), ("PumpStation",
                           "asm-understanding-pumpstation.json"), ("PUMP01_FP", "asm-understanding-pump01-fp.json"),
                           ("SEQ01_SP", "asm-understanding-seq01-sp.json")):
            u = fixture(file)
            for sec in ("regions", "devices", "flows", "readouts", "indicators", "navigation"):
                for e in u[sec]:
                    self.assertIn(f"{name}:{e['id']}", uids)
            for sec in ("static", "dropped"):
                for e in u[sec]:
                    n = e["ans"][0].split(":")[1]
                    self.assertIn(f"{name}:{'s' if sec == 'static' else 'x'}{n}", uids)

    def test_a_mapping_row_names_its_place(self):
        rows = {r["uid"]: r for r in self.model["mapping"]}
        self.assertEqual(rows["PumpStation:d_p1"]["section"], "devices")
        self.assertTrue(rows["PumpStation:d_p1"]["place"].startswith("page PumpStation"))
        self.assertTrue(rows["PUMP01_FP:v1"]["place"].startswith("faceplate PUMP01 tab Home"))
        self.assertTrue(rows["Overview:x10"]["place"].startswith("dropped"))
        self.assertEqual(rows["Overview:d_pump"]["device"], "PUMP01")

    def test_a_device_drawn_on_another_page_is_a_plain_symbol_there(self):
        rows = {r["uid"]: r for r in self.model["mapping"]}
        self.assertIn("plain symbol", rows["Overview:d_pump"]["place"])
        self.assertIn("faceplate PUMP01", rows["Overview:d_pump"]["place"])
        self.assertNotIn("plain symbol", rows["PumpStation:d_p1"]["place"])

    # ---- devices -----------------------------------------------------------------------------
    def test_a_device_has_a_node_its_own_pages_node_and_a_faceplate_kind(self):
        d = self.model["devices"]
        self.assertEqual(set(d), {"BRK01", "PUMP01", "PUMP02", "TANK01", "VALVE01", "SEQ01", "UPS01"})
        pages = {p["id"]: p for p in self.model["pages"]}
        for tag, dev in d.items():
            self.assertTrue(dev["node"], tag)
            self.assertTrue(dev["faceplate"], tag)
            self.assertEqual(dev["node"], pages[dev["page"]]["node"], tag)
        self.assertEqual(d["PUMP01"]["page"], "PumpStation")       # the faceplates document's owner_page
        self.assertEqual(d["PUMP01"]["kind"], "pump")
        self.assertEqual(d["PUMP01"]["faceplate"], "pump")
        self.assertEqual(d["SEQ01"]["faceplate"], "sequence")
        self.assertEqual(d["BRK01"]["kind"], "switch")
        self.assertEqual(d["UPS01"]["faceplate"], "empty")          # no library faceplate: said, not guessed

    def test_the_openers_of_a_device_are_listed_with_their_tab(self):
        o = self.model["devices"]["PUMP01"]["openers"]
        self.assertEqual({(x["page"], x["an"]) for x in o}, {("PumpStation", "15"), ("Overview", "7")})
        self.assertTrue(all(x["tab"] == "Home" for x in o))
        self.assertEqual(self.model["devices"]["SEQ01"]["openers"][0]["tab"], "Config")

    # ---- alarms ------------------------------------------------------------------------------
    def test_alarms_carry_a_priority_labelled_inferred_where_it_comes_from_a_category_rank(self):
        alarms = {a["tag"]: a for a in self.model["alarms"]}
        self.assertEqual(set(alarms), {"PUMP01_AFAIL", "PUMP01_ATRIP", "TANK01_AHIGH", "BRK01_AUV"})
        self.assertEqual([alarms[t]["priority"] for t in ("PUMP01_AFAIL", "PUMP01_ATRIP", "TANK01_AHIGH",
                                                          "BRK01_AUV")], ["high", "medium", "low", "diagnostic"])
        self.assertTrue(all(a["inferred"] for a in alarms.values()))
        self.assertEqual(alarms["PUMP01_AFAIL"]["delay"], 5)
        self.assertEqual(alarms["BRK01_AUV"]["delay"], 60)
        self.assertEqual(alarms["PUMP01_AFAIL"]["device"], "PUMP01")
        self.assertEqual(alarms["PUMP01_AFAIL"]["node"], self.model["devices"]["PUMP01"]["node"])
        self.assertEqual(alarms["PUMP01_AFAIL"]["uid"], "PumpStation:d_p1")

    def test_a_category_table_gives_the_priority_and_is_not_inferred(self):
        def give(ins):
            t = fixture("asm-tables.json")
            for d in t["devices"].values():
                d["priority"] = {"by_category": {"1": "critical", "2": "high", "3": "medium", "100": "low"},
                                 "inferred": False, "basis": "almcat"}
            dump(ins["tables"], t)
        with tempfile.TemporaryDirectory() as t:
            _, m, _, _ = build(Path(t), mutate=give)
            a = {x["tag"]: x for x in m["alarms"]}
            self.assertEqual((a["PUMP01_AFAIL"]["priority"], a["PUMP01_AFAIL"]["inferred"]), ("critical", False))
            self.assertEqual(a["BRK01_AUV"]["priority"], "low")

    def test_a_category_table_of_ctigs_form_gives_the_priority_by_its_number(self):
        def give(ins):
            t = fixture("asm-tables.json")
            for d in t["devices"].values():
                d["priority"] = {"by_category": {"1": {"basis": "almcat", "inferred": False, "priority": 4},
                                                 "2": {"basis": "almcat", "inferred": False, "priority": 9},
                                                 "3": {"basis": "almcat", "inferred": True, "priority": 12},
                                                 "100": {"basis": "almcat", "inferred": False, "priority": 40}},
                                 "inferred": False, "basis": "almcat"}
            dump(ins["tables"], t)
        with tempfile.TemporaryDirectory() as t:
            code, m, _, _ = build(Path(t), mutate=give)
            self.assertEqual(code, 0)
            a = {x["tag"]: x for x in m["alarms"]}
            self.assertEqual([a[k]["priority"] for k in ("PUMP01_AFAIL", "PUMP01_ATRIP", "TANK01_AHIGH", "BRK01_AUV")],
                             ["high", "medium", "low", "diagnostic"])         # the numbers 4, 9, 12, 40 by rank
            self.assertEqual([a[k]["inferred"] for k in ("PUMP01_AFAIL", "TANK01_AHIGH")], [False, True])
            self.assertEqual(validate(m, "cadre-hmi-asm-model-1.json"), [])

    # ---- the search index and trends ---------------------------------------------------------
    def test_the_tag_index_names_the_device_page_and_tab_of_a_tag(self):
        tags = {t["name"]: t for t in self.model["tags"]}
        t = tags["PUMP01_IAMP"]
        self.assertEqual((t["device"], t["units"], t["comment"]), ("PUMP01", "A", "Pump 1 current"))
        self.assertEqual(t["range"], ["0", "20"])      # the tables state text; no number is made of it
        self.assertEqual(t["page"], "PumpStation")
        self.assertEqual(t["tab"], "Home")
        self.assertTrue(tags["PUMP01_AFAIL"]["alarm"])
        self.assertFalse(tags["PUMP01_IAMP"]["alarm"])
        self.assertEqual(len(tags), len(set(tags)))

    def test_trends_are_per_node_and_bounded(self):
        self.assertTrue(self.model["trends"])
        for t in self.model["trends"]:
            self.assertLessEqual(len(t["pens"]), 3)
            self.assertIn(t["node"], {n["id"] for n in self.model["nodes"]})

    def test_the_tag_index_reads_the_tags_map_as_well_as_the_devices(self):
        tags = {t["name"]: t for t in self.model["tags"]}
        self.assertIn("PUMP02_IRUN", tags)                 # only in tables.tags, not under a device
        self.assertEqual(tags["PUMP02_IRUN"]["comment"], "Pump 2 running")
        self.assertIsNone(tags["PUMP02_IRUN"]["device"])
        self.assertEqual(tags["PUMP01_IAMP"]["range"], ["0", "20"])      # the table's text, kept as it is
        self.assertEqual(tags["PUMP01_IAMP"]["device"], "PUMP01")        # a tag in both keeps its device

    def test_a_tag_only_in_the_tags_map_takes_its_page_from_the_entry_that_reads_it(self):
        with tempfile.TemporaryDirectory() as t:
            def only_tags(ins):
                tb = fixture("asm-tables.json")
                tb["tags"]["FLOW01_PV"]["comment"] = "from the tags map"
                del tb["devices"]["FLOW01"]
                dump(ins["tables"], tb)
            _, m, _, _ = build(Path(t), mutate=only_tags)
            row = {x["name"]: x for x in m["tags"]}["FLOW01_PV"]
            self.assertEqual((row["comment"], row["page"], row["uid"]), ("from the tags map", "Overview", "Overview:v1"))

    # ---- navigation --------------------------------------------------------------------------
    def test_every_original_target_has_a_nav_row_with_a_resolution(self):
        nav = self.model["nav"]
        self.assertTrue(all(n["resolution"] in ("page", "faceplate", "support", "not_migrated") for n in nav))
        kinds = {n["from"].split(" ")[0] for n in nav}
        self.assertTrue({"menu", "opener", "Overview", "PumpStation"} <= kinds)
        for target in ("Overview", "PumpStation", "Aeration", "Alarm", "Trend", "PUMP01_FP", "SEQ01_SP", "Reports"):
            self.assertTrue(any(n["target"] == target for n in nav), target)

    def test_the_resolutions(self):
        def rows(target):
            return [n for n in self.model["nav"] if n["target"] == target]
        self.assertTrue(all(n["resolution"] == "page" and n["route"] for n in rows("PumpStation")))
        self.assertTrue(all(n["resolution"] == "page" for n in rows("Aeration")))
        self.assertTrue(all(n["resolution"] == "support" and n["route"] == "/alerts" for n in rows("Alarm")))
        self.assertTrue(all(n["resolution"] == "support" and n["route"] == "/trends" for n in rows("Trend")))
        self.assertTrue(all(n["resolution"] == "faceplate" and n["faceplate"] == "PUMP01" for n in rows("PUMP01_FP")))
        self.assertTrue(all(n["resolution"] == "faceplate" and n["faceplate"] == "SEQ01" for n in rows("SEQ01_SP")))
        r = rows("Reports")[0]
        self.assertEqual(r["resolution"], "not_migrated")
        self.assertTrue(r["reason"])

    def test_no_popup_has_the_resolution_page(self):
        popups = {"PUMP01_FP", "SEQ01_SP"}
        self.assertFalse([n for n in self.model["nav"] if n["target"] in popups and n["resolution"] == "page"])

    def test_a_navigation_row_of_an_entry_carries_its_uid_and_privilege(self):
        n = next(n for n in self.model["nav"] if n.get("uid") == "PumpStation:n3")
        self.assertEqual((n["target"], n["priv"], n["resolution"]), ("SEQ01_SP", 2, "faceplate"))

    def test_previous_and_next_of_the_pages_table_have_rows(self):
        pn = [n for n in self.model["nav"] if n["from"].split(" ")[-1] in ("previous", "next")]
        self.assertEqual({(n["from"], n["target"]) for n in pn},
                         {("Overview next", "PumpStation"), ("PumpStation previous", "Overview")})

    def test_an_opener_the_faceplates_cannot_place_is_unresolved_and_exits_2(self):
        def lose(ins):
            f = fixture("asm-faceplates.json")
            f["faceplates"] = [x for x in f["faceplates"] if x["id"] != "SEQ01"]
            dump(ins["faceplates"], f)
        with tempfile.TemporaryDirectory() as t:
            code, m, _, _ = build(Path(t), mutate=lose)
            self.assertEqual(code, 2)
            self.assertEqual([n["target"] for n in m["nav"] if n["resolution"] is None],
                             ["SEQ01_SP", "SEQ01_SP"])   # the navigation entry and the opener
            self.assertTrue(any(u["target"] == "SEQ01_SP" for u in m["unresolved"]))
            self.assertEqual(len(m["unmapped"]), 2)           # the pop-up set's rows have no tab to sit in

    # ---- the page folders --------------------------------------------------------------------
    def test_a_page_folder_per_built_page_holds_the_slice_and_the_pictures(self):
        for page in ("Overview", "PumpStation"):
            f = self.out / "pages" / page
            for name in ("page.json", "understanding.json", "inventory.json", "runtime.png", "preview.png"):
                self.assertTrue((f / name).is_file(), f"{page}/{name}")
        self.assertFalse((self.out / "pages" / "Aeration" / "understanding.json").exists())
        pages = {p["id"]: p for p in self.model["pages"]}
        self.assertEqual(pages["PumpStation"]["folder"], "pages/PumpStation")

    def test_page_json_states_the_size_the_kind_and_the_original_object_of_each_item(self):
        pj = json.loads((self.out / "pages" / "PumpStation" / "page.json").read_text(encoding="utf-8"))
        self.assertEqual(pj["page_size"], {"w": 1024, "h": 768})
        items = {i["uid"]: i for i in pj["items"]}
        self.assertEqual(items["PumpStation:d_p1"]["original_an"], "PumpStation:2")
        self.assertEqual(items["PumpStation:d_p1"]["kind"], "symbol")
        self.assertEqual({items[u]["kind"] for u in ("PumpStation:v1", "PumpStation:i1", "PumpStation:f1",
                                                      "PumpStation:n1", "PumpStation:n2", "PumpStation:s18")},
                         {"readout", "indicator", "pipe", "link", "button", "label"})
        self.assertEqual(pj["navigation"], pj["nav"])                           # both names, the present key kept
        self.assertTrue(all("ans" in i and "section" in i for i in items.values()))

    def test_page_size_may_be_a_pair_or_ctigs_object(self):
        def as_object(ins):
            f = ins["inventory"] / "units" / "PumpStation" / "unit.json"
            u = json.loads(f.read_text(encoding="utf-8"))
            u["windows"][0]["page_size"] = {"w": 800, "h": 600}
            dump(f, u)
        with tempfile.TemporaryDirectory() as t:
            _, _, out, _ = build(Path(t), mutate=as_object)
            pj = json.loads((out / "pages" / "PumpStation" / "page.json").read_text(encoding="utf-8"))
            self.assertEqual(pj["page_size"], {"w": 800, "h": 600})

    def test_page_json_lists_every_placeable_uid_once(self):
        pj = json.loads((self.out / "pages" / "PumpStation" / "page.json").read_text(encoding="utf-8"))
        uids = [i["uid"] for i in pj["items"]]
        self.assertEqual(len(uids), len(set(uids)))
        self.assertIn("PumpStation:d_p1", uids)
        self.assertIn("PumpStation:s18", uids)           # a heading is drawn
        self.assertNotIn("PumpStation:x19", uids)        # a dropped object is not
        self.assertEqual({d["tag"] for d in pj["devices"]} >= {"PUMP01", "TANK01"}, True)
        self.assertTrue(pj["nav"])
        self.assertEqual(pj["page"]["id"], "PumpStation")

    def test_a_missing_picture_is_recorded_and_does_not_fail_the_run(self):
        def lose(ins):
            (ins["pictures"] / "PumpStation.png").unlink()
        with tempfile.TemporaryDirectory() as t:
            code, m, out, _ = build(Path(t), mutate=lose)
            self.assertEqual(code, 0)
            self.assertFalse((out / "pages" / "PumpStation" / "preview.png").exists())
            self.assertIn("pages/PumpStation/preview.png", m["provenance"]["missing_files"])

    # ---- provenance, catalogue, determinism --------------------------------------------------
    def test_provenance_names_the_tool_the_inputs_and_no_secret(self):
        p = self.model["provenance"]
        self.assertEqual(p["tool"], "tools/hmi/asm_model.py")
        self.assertEqual(p["repository"], "Cadre-Sandbox-OpenBridge")
        self.assertTrue(all(len(i["sha256"]) == 64 for i in p["inputs"]))
        self.assertTrue(any(i["path"].endswith("tables.json") for i in p["inputs"]))
        self.assertIn("python", p["interpreter"]["path"].lower())

    def test_the_catalogue_lists_the_kinds_and_parts_read(self):
        c = self.model["catalogue"]
        self.assertIn("pump", c["kinds"])
        self.assertIn("cadre.ob.pump", c["module_parts"])

    def test_two_runs_give_the_same_model(self):
        with tempfile.TemporaryDirectory() as t:
            _, again, _, _ = build(Path(t))
            a, b = dict(self.model), dict(again)
            for m in (a, b):
                m["provenance"] = {k: v for k, v in m["provenance"].items()
                                   if k not in ("started", "duration_s", "argv", "inputs", "dirty", "commit")}
            self.assertEqual(a, b)

    def test_the_flows_of_the_pages_are_kept_with_their_routing_medium_and_ends(self):
        f = self.model["flows"]["PumpStation:f3"]
        self.assertEqual((f["an"], f["medium"], f["from"], f["to"]),
                         ("PumpStation:9", "waste", "PumpStation:d_p1", "PumpStation:d_v1"))
        self.assertEqual(f["path"][1], {"x": 520, "y": 354})
        self.assertEqual(len(self.model["flows"]), 3)

    def test_the_support_map_can_be_given(self):
        with tempfile.TemporaryDirectory() as t:
            sup = dump(Path(t) / "support.json", {"Reports": "/reports"})
            code, m, _, _ = build(Path(t), "--support-routes", str(sup))
            self.assertEqual(code, 0)
            r = next(n for n in m["nav"] if n["target"] == "Reports")
            self.assertEqual((r["resolution"], r["route"]), ("support", "/reports"))

    def test_no_client_name_enters_the_model(self):
        text = json.dumps(self.model)
        self.assertNotIn("eng02", text.lower())


class CommandLineTests(unittest.TestCase):
    def run_cli(self, d: Path, *extra, drop=()):
        ins = inputs(d)
        return subprocess.run([sys.executable, str(ROOT / "tools" / "hmi" / "asm_model.py"),
                               *argv_of(ins, d / "m", *extra, drop=drop)], capture_output=True, text=True, cwd=ROOT)

    def test_exit_0_on_a_clean_run(self):
        with tempfile.TemporaryDirectory() as t:
            r = self.run_cli(Path(t))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("unmapped 0", r.stdout)

    def test_exit_1_on_an_input_fault(self):
        with tempfile.TemporaryDirectory() as t:
            ins = inputs(Path(t))
            ins["tables"].write_text("{not json", encoding="utf-8")
            r = subprocess.run([sys.executable, str(ROOT / "tools" / "hmi" / "asm_model.py"),
                                *argv_of(ins, Path(t) / "m")], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(r.returncode, 1)
            self.assertIn("tables", r.stdout + r.stderr)

    def test_exit_1_when_a_required_option_is_missing(self):
        with tempfile.TemporaryDirectory() as t:
            r = self.run_cli(Path(t), drop=("faceplates",))
            self.assertEqual(r.returncode, 1)

    def test_exit_2_when_an_entry_cannot_be_mapped(self):
        with tempfile.TemporaryDirectory() as t:
            ins = inputs(Path(t))
            u = fixture("asm-understanding-pumpstation.json")
            del u["readouts"][0]["id"]
            dump(next(p for p in (Path(t) / "in" / "understandings").iterdir() if "pumpstation" in p.name), u)
            r = subprocess.run([sys.executable, str(ROOT / "tools" / "hmi" / "asm_model.py"),
                                *argv_of(ins, Path(t) / "m")], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            m = json.loads((Path(t) / "m" / "model.json").read_text(encoding="utf-8"))
            self.assertEqual(len(m["unmapped"]), 1)
            self.assertEqual(m["unmapped"][0]["section"], "readouts")


if __name__ == "__main__":
    unittest.main()
