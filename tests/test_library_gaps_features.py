"""Tests of the parts and features of `tools/hmi/library_gaps.py` (S11-D addendum): the project design's components
(`wfb.migration.project_design/1`: `mapping[].component`, `devices[].component`, `faceplates[]`) resolved against the
catalogue, the descriptor schema and the profile; a name that resolves nowhere is a gap row. All names are synthetic."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump, validate  # noqa: E402
from test_library_gaps import prepare  # noqa: E402

from hmi import library_gaps  # noqa: E402

CATALOGUE = {
    "Automation/Pump": {"kind": "symbol", "view": "Automation/Pump"},
    "Faceplate/ASM/Pump": {"kind": "framework", "params": {"deviceId": ""}, "view": "Faceplate/ASM/Pump"},
    "Faceplate/ASM/Valve": {"kind": "framework", "params": {"deviceId": "", "tab": ""}, "view": "Faceplate/ASM/Valve"},
    "Parts/Trend": {"kind": "part", "view": "Parts/Trend"},
}
SCHEMA = {"properties": {"labels": {"type": "array"}, "links": {"type": "array"}, "alarmPanels": {"type": "array"}}}


def design(mapping=(), devices=(), faceplates=()):
    return {"schema": "wfb.migration.project_design/1", "mapping": list(mapping), "devices": list(devices),
            "faceplates": list(faceplates)}


def row(entry, component, page="P1"):
    return {"entry": entry, "treatment": "drawn", "component": component, "gap": None, "page": page}


class FeatureGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.model, cls.lst = prepare(cls.dir)
        cls.catalogue = dump(cls.dir / "contracts.json", CATALOGUE)
        cls.schema = dump(cls.dir / "descriptor.schema.json", SCHEMA)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def run_tool(self, name, doc, *extra, designs=False, schema=True):
        path = dump(self.dir / f"{name}.design.json", doc)
        out = self.dir / name
        argv = ["--model", str(self.model), "--design", str(path), "--catalogue", str(self.catalogue),
                "--profile", str(ROOT / "library" / "profile.json"), "--module", str(ROOT / "module" / "components.json"),
                "--out", str(out), *extra]
        if designs:
            argv += ["--designs", str(self.lst)]
        if schema:
            argv += ["--descriptor-schema", str(self.schema)]
        code = library_gaps.main(argv)
        gaps = json.loads((out / "gaps.json").read_text(encoding="utf-8")) if (out / "gaps.json").exists() else None
        return code, gaps

    def gaps_by_id(self, doc):
        return {g["id"]: g for g in doc["gaps"]}

    def test_a_descriptor_element_resolves_by_its_schema_key_and_a_missing_one_is_a_gap_row(self):
        code, doc = self.run_tool("elements", design([row("u1:1", "label"), row("u1:2", "alarm-panel"),
                                                      row("u1:3", "bar"), row("u1:4", "bar", "P2")]))
        self.assertEqual(code, 2)
        gaps = self.gaps_by_id(doc)
        self.assertEqual(sorted(gaps), ["GAP-element-bars"])
        gap = gaps["GAP-element-bars"]
        self.assertEqual(gap["kind"], "bar")
        self.assertEqual(gap["mapping_rows"], ["u1:3", "u1:4"])
        self.assertEqual(gap["status"], "open")
        self.assertIn("bars", gap["library_today"])
        self.assertEqual(validate(doc, "cadre-hmi-library-gaps-1.json"), [])
        features = {f["name"]: f for f in doc["features"]}
        self.assertTrue(features["alarm-panel"]["resolved"])
        self.assertEqual(features["bar"]["count"], 2)
        self.assertEqual(features["bar"]["pages"], ["P1", "P2"])

    def test_a_catalogue_view_resolves_by_name_and_a_missing_one_is_a_gap(self):
        _, doc = self.run_tool("views", design([row("u1:1", "Parts/Trend"), row("u1:2", "Parts/RangeBar")]))
        self.assertEqual(sorted(self.gaps_by_id(doc)), ["GAP-view-Parts/RangeBar"])

    def test_a_faceplate_kind_without_a_view_and_a_tab_without_the_tab_parameter_are_gaps(self):
        _, doc = self.run_tool("faceplates", design(faceplates=[
            {"kind": "pump", "tabs": ["home", "config", "alarms"], "used_by": ["D1"]},
            {"kind": "valve", "tabs": ["home", "config"], "used_by": ["D2"]},
            {"kind": "sequence", "tabs": ["home"], "used_by": ["D3"]},
        ]))
        self.assertEqual(sorted(self.gaps_by_id(doc)),
                         ["GAP-faceplate-sequence", "GAP-tab-pump-alarms", "GAP-tab-pump-config"])
        self.assertEqual(self.gaps_by_id(doc)["GAP-faceplate-sequence"]["mapping_rows"], ["D3"])

    def test_faceplate_content_and_the_frame_are_the_librarys_and_never_element_gaps(self):
        # WorkflowBuilder wave 3: a pop-up's rows and tabs land on a faceplate, which the faceplate check covers by
        # the device's kind; the frame is the library's own. None of them is a descriptor element.
        _, doc = self.run_tool("content", design([row("u1:1", "faceplate-row"), row("u1:2", "faceplate-tab"),
                                                  row("u1:3", "frame")]))
        self.assertEqual(self.gaps_by_id(doc), {})
        classes = {f["name"]: (f["class"], f["resolved"]) for f in doc["features"]}
        self.assertEqual(classes["faceplate-row"], ("faceplate", True))
        self.assertEqual(classes["frame"], ("frame", True))
        self.assertEqual(validate(doc, "cadre-hmi-library-gaps-1.json"), [])

    def test_a_name_that_resolves_nowhere_is_a_gap_whatever_it_means(self):
        _, doc = self.run_tool("unknown", design([row("u1:1", "cadre.ob.widget")]))
        gap = self.gaps_by_id(doc)["GAP-element-cadre.ob.widgets"]
        self.assertIn("no kind, view or descriptor element", gap["library_today"])

    def test_a_device_kind_in_the_design_goes_to_the_kind_analysis(self):
        _, doc = self.run_tool("kinds", design(devices=[{"device": "D1", "component": "pump", "gap": None,
                                                        "faceplate": None}]))
        self.assertEqual([k["kind"] for k in doc["kinds"]], ["pump"])
        self.assertNotIn("pump", {f["name"] for f in doc["features"]})

    def test_an_accepted_feature_gap_is_accepted_and_not_counted(self):
        accepted = dump(self.dir / "accepted.json", {"accepted": [{"id": "GAP-element-bars", "reason": "owner"}]})
        code, doc = self.run_tool("accepted", design([row("u1:1", "bar")]), "--accepted", str(accepted))
        self.assertEqual(code, 0)
        self.assertEqual(doc["open_count"], 0)
        self.assertEqual(self.gaps_by_id(doc)["GAP-element-bars"]["status"], "accepted")

    def test_the_design_without_the_descriptor_schema_is_an_input_fault(self):
        code, _ = self.run_tool("noschema", design([row("u1:1", "label")]), schema=False)
        self.assertEqual(code, 1)

    def test_the_page_designs_and_the_project_design_together_count_both(self):
        code, doc = self.run_tool("both", design([row("u1:1", "bar")]), designs=True)
        self.assertIn("GAP-element-bars", self.gaps_by_id(doc))
        self.assertTrue(doc["kinds"])  # the page designs' kinds are still analysed


if __name__ == "__main__":
    unittest.main()


SCHEMA_PROPS = {
    "properties": {
        "labels": {"type": "array", "items": {"properties": {"text": {}, "style": {}}}},
        "symbols": {"type": "array", "items": {"$ref": "#/$defs/symbol"}},
        "links": {"type": "array", "items": {"properties": {"to": {}}}},
    },
    "$defs": {"symbol": {"properties": {"kind": {}, "params": {"type": "object"},
                                        "states": {"type": "object", "properties": {"on": {}}}}}},
}


class PropertyGapTests(unittest.TestCase):
    """`mapping[].properties`: each key the entry needs on its element resolves among the element's item properties in
    the descriptor schema (a `$ref` followed; `a.b` inside the property `a`); a key that does not is a gap row."""

    gaps_by_id = FeatureGapTests.gaps_by_id
    run_tool = FeatureGapTests.run_tool

    @classmethod
    def setUpClass(cls):
        FeatureGapTests.setUpClass.__func__(cls)
        cls.schema = dump(cls.dir / "descriptor.props.schema.json", SCHEMA_PROPS)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def prow(self, entry, component, properties):
        return {**row(entry, component), "properties": properties}

    def test_a_key_the_element_has_resolves_and_a_missing_one_is_a_gap_row(self):
        code, doc = self.run_tool("props", design([self.prow("u1:1", "label", ["text", "emphasis"]),
                                                   self.prow("u1:2", "label", ["emphasis"])]))
        self.assertEqual(code, 2)
        gap = self.gaps_by_id(doc)["GAP-property-labels.emphasis"]
        self.assertEqual(gap["kind"], "labels.emphasis")
        self.assertEqual(gap["mapping_rows"], ["u1:1", "u1:2"])
        self.assertEqual(validate(doc, "cadre-hmi-library-gaps-1.json"), [])
        self.assertNotIn("GAP-property-labels.text", self.gaps_by_id(doc))

    def test_a_device_kind_takes_the_symbol_definition_by_its_reference(self):
        _, doc = self.run_tool("symprops", design([self.prow("u1:1", "pump", ["states", "badgeDuty"])]))
        self.assertEqual(sorted(self.gaps_by_id(doc)), ["GAP-property-symbols.badgeDuty"])

    def test_a_dotted_key_looks_inside_its_property_and_a_free_object_resolves(self):
        _, doc = self.run_tool("dotted", design([self.prow("u1:1", "pump", ["states.on", "states.off", "params.x"])]))
        self.assertEqual(sorted(self.gaps_by_id(doc)), ["GAP-property-symbols.states.off"])

    def test_the_properties_of_a_missing_element_are_not_counted_twice(self):
        _, doc = self.run_tool("noelement", design([self.prow("u1:1", "bar", ["min"])]))
        self.assertEqual(sorted(self.gaps_by_id(doc)), ["GAP-element-bars"])


class FaceplateMapTests(unittest.TestCase):
    """A faceplate kind resolves through the library's own map (`framework.faceplate_view`, asm style), not by its
    name: motor and fan open the pump's faceplate; a kind the map lacks is a gap."""

    gaps_by_id = FeatureGapTests.gaps_by_id
    run_tool = FeatureGapTests.run_tool

    @classmethod
    def setUpClass(cls):
        FeatureGapTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_motor_and_fan_open_the_pump_faceplate(self):
        _, doc = self.run_tool("motorfan", design(faceplates=[
            {"kind": "motor", "tabs": ["home"], "used_by": ["M1"]},
            {"kind": "fan", "tabs": ["home"], "used_by": ["F1"]},
        ]))
        self.assertEqual(self.gaps_by_id(doc), {})
        views = {f["name"] for f in doc["features"] if f["class"] == "faceplate"}
        self.assertEqual(views, {"Faceplate/ASM/Pump"})

    def test_a_kind_the_map_lacks_is_a_gap(self):
        _, doc = self.run_tool("nomap", design(faceplates=[{"kind": "conveyor", "tabs": ["home"],
                                                            "used_by": ["C1"]}]))
        gap = self.gaps_by_id(doc)["GAP-faceplate-conveyor"]
        self.assertIn("no faceplate for the kind", gap["library_today"])
        self.assertEqual(gap["mapping_rows"], ["C1"])
