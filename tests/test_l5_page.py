"""Tests of the component test page of eng02 ASM Level 5 (COB-165; contract 3.8 and 3.4): the lamps coloured by state, the
module beside the view for every status, mode and mark, the plain motors that open a faceplate, the alarm panel with Ack
selected and Ack all, and the gallery on memory tags.

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import library_profile, screen, testbench  # noqa: E402

TAG_ROOT = "[default]cadre_hmi_l5test"


def nodes_of(doc):
    out = {}

    def walk(n):
        out[n.get("meta", {}).get("name")] = n
        for c in n.get("children") or []:
            walk(c)
    walk(doc["root"])
    return out


def expr(node, key):
    return node["propConfig"][key]["binding"]["config"]["expression"]


class TestPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = screen.load_contracts()
        cls.prof = library_profile.build(cls.contracts)
        cls.bench = testbench.build(cls.contracts, cls.prof, TAG_ROOT)
        cls.desc = cls.bench.descriptor
        cls.syms = {s["id"]: s for s in cls.desc["symbols"]}
        cls.flat = {}

        def walk(folder, path=""):
            for t in folder["tags"]:
                here = f"{path}/{t['name']}" if path else t["name"]
                if t["tagType"] == "Folder":
                    walk(t, here)
                else:
                    cls.flat[here] = t
        walk(cls.bench.tags)

    def build(self, render="stock"):
        screen.RENDER["target"] = render
        try:
            doc, info = screen.build_screen(copy.deepcopy(self.desc), self.contracts)
        finally:
            screen.RENDER["target"] = "stock"
        return doc, nodes_of(doc), info

    def test_the_lamps_are_a_boolean_a_three_state_a_string_and_a_paint(self):
        lamps = {k: v for k, v in self.syms.items() if k.startswith("L_")}
        self.assertEqual(set(lamps), {"L_BOOL", "L_NUM", "L_STR", "L_PAINT"})
        self.assertNotIn("states", lamps["L_BOOL"])
        self.assertEqual([st["value"] for st in lamps["L_NUM"]["states"]], [0, 1, 2])
        self.assertEqual([st["colour"] for st in lamps["L_NUM"]["states"]], ["off", "on", "alarm"])
        self.assertEqual([st["value"] for st in lamps["L_STR"]["states"]], ["STOP", "RUN", "TRIP"])
        self.assertTrue(lamps["L_PAINT"]["states"][1]["colour"].startswith("#"))
        for ident, sym in lamps.items():
            self.assertEqual(sym["bind"], {"state": f"_componentTest/lamps/{ident}/state"})
            self.assertIn(f"lamps/{ident}/state", self.flat)
        self.assertEqual(self.flat["lamps/L_NUM/state"]["dataType"], "Float8")
        self.assertEqual(self.flat["lamps/L_STR/state"]["dataType"], "String")
        # the buttons write the lamps' own test tags
        pulses = {b["action"]["tag"] for b in self.desc["buttons"] if b["id"].startswith("L_")}
        self.assertEqual(pulses, {f"_componentTest/lamps/{i}/{m}" for i, m in (
            ("L_BOOL", "set"), ("L_NUM", "set1"), ("L_NUM", "set2"), ("L_STR", "run"), ("L_STR", "trip"),
            ("L_PAINT", "set"))})
        for t in pulses:
            self.assertIn(t, self.bench.pulse_tags)
            self.assertIn(t[len("_componentTest/"):], self.flat)

    def test_the_lamps_build_with_their_colour_expressions(self):
        doc, n, info = self.build()
        self.assertEqual(info["errors"], [])
        self.assertIn("case({view.custom.g_L_NUM}, 0,", expr(n["L_NUM"], "props.params.colour"))
        self.assertEqual(doc["propConfig"]["custom.g_L_STR"]["binding"]["config"]["tagPath"],
                         f"{TAG_ROOT}/_componentTest/lamps/L_STR/state")

    def test_the_notification_and_the_marks_put_module_beside_view(self):
        for prefix in ("N_pump_", "B_pump_"):
            cells = sorted((s for k, s in self.syms.items() if k.startswith(prefix)),
                           key=lambda s: int(s["id"][len(prefix):]))
            self.assertTrue(cells)
            self.assertEqual(len(cells) % 2, 0)
            for a, b in zip(cells[::2], cells[1::2]):
                self.assertEqual(a["y"], b["y"])                                       # one row
                self.assertGreater(b["x"], a["x"])                                      # the view to the right
                self.assertEqual(b.get("render"), "view")
                self.assertEqual(self.bench.gallery.get(a["id"]), self.bench.gallery.get(b["id"]))   # the same case
        critical = [s for k, s in self.syms.items()
                    if k.startswith("N_pump_") and self.bench.gallery[k].get("alertFrameStatus") == "critical"]
        self.assertTrue(critical)
        self.assertEqual({s.get("render") for s in critical}, {"view"})                 # the module has no critical status

    def test_the_pairs_draw_differently_under_the_module_and_alike_under_the_stock_rendering(self):
        _d, n, _i = self.build("module")
        self.assertEqual((n["N_pump_1"]["type"], n["N_pump_2"]["type"]), ("cadre.ob.pump", "ia.display.view"))
        _d, n, _i = self.build("stock")
        self.assertEqual((n["N_pump_1"]["type"], n["N_pump_2"]["type"]), ("ia.display.view", "ia.display.view"))

    def test_two_plain_motors_open_faceplates_and_the_state_motor_has_a_state_only(self):
        a, b = self.syms["TB_PLAIN_PUMP"], self.syms["TB_PLAIN_MOTOR"]
        self.assertEqual((a["kind"], a["faceplate"]), ("motor", "_componentTest/TB_PUMP"))
        self.assertEqual((b["kind"], b["faceplate"]), ("motor", "_componentTest/TB_MSTATE"))
        self.assertNotIn("device", a)
        ms = next(d for d in self.bench.devices if d["id"] == "_componentTest/TB_MSTATE")
        self.assertEqual((ms["kind"], ms["faceplate"], list(ms["members"])), ("motor", "asm", ["state"]))
        self.assertIn("TB_MSTATE/state", self.flat)
        self.assertIn("_componentTest/TB_MSTATE/state", self.bench.pulse_tags)

    def test_the_alarm_panel_lists_the_test_alarms_beside_the_raise_buttons(self):
        panel = self.desc["alarmPanels"][0]
        self.assertEqual(panel["sources"], ["_componentTest"])
        raise_buttons = [b for b in self.desc["buttons"] if b["id"].startswith("ALM_")]
        self.assertTrue(raise_buttons)
        self.assertGreater(panel["x"], max(b["x"] + b["w"] for b in raise_buttons))           # beside them
        _d, n, info = self.build()
        self.assertEqual(info["errors"], [])
        node = n["Alarms_ALM_panel"]
        self.assertEqual(node["props"]["path"], "Faceplate/Alarms")
        self.assertEqual(node["props"]["params"]["source"], "prov:default:/tag:cadre_hmi_l5test/_componentTest/*")
        self.assertEqual(screen.schema_errors([self.desc], ["bench"]), [])

    def test_every_gallery_symbol_reads_memory_tags_with_todays_values(self):
        gallery = self.bench.gallery
        self.assertGreater(len(gallery), 100)
        grid = [s for k, s in self.syms.items() if k.startswith(testbench.GALLERY_PREFIXES) and not s.get("device")]
        for s in grid:
            for k in s.get("params", {}):
                self.assertNotIn(k, testbench.GALLERY_PARAMS, (s["id"], k))                  # moved to its tag
            for k, value in gallery.get(s["id"], {}).items():
                self.assertEqual(s["bind"][k], f"_componentTest/gallery/{s['id']}/{k}")
                tag = self.flat[f"gallery/{s['id']}/{k}"]
                want = value if isinstance(value, (bool, str)) else float(value)
                self.assertEqual((tag["valueSource"], tag["value"]), ("memory", want))
        self.assertEqual(self.flat["gallery/S_pump_2/on"]["dataType"], "Boolean")
        self.assertEqual(self.flat["gallery/N_pump_1/alertFrameStatus"]["dataType"], "String")
        # layout stays in the view
        kept = {k for s in grid for k in s.get("params", {})}
        self.assertTrue({"readoutPosition", "hasTag", "variant"} <= kept)

    def test_the_page_follows_no_alarm_with_its_static_symbols(self):
        doc, _n, info = self.build()
        self.assertEqual(info["errors"], [])
        keys = set(doc["custom"].get("alerts", {}))
        self.assertEqual({k for k in keys if not k.startswith(("a_ALM_", "a_TB_"))}, set())


if __name__ == "__main__":
    unittest.main()
