"""The builder's own tests of the local assembly (NOTE-WFB-10 section 11.2, WP-W03), beside the tester's: the rule
`assembly-part-ids` by name, the screen report of a schema failure, the local kinds file's form, the drawn shapes and
the bindings of the kind's view, and the pulse a button declares. Synthetic names only; nothing needs the gateway."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import local_support as L  # noqa: E402
from local_support import KIND, KIND_VIEW, TAG_ROOT, assembly, devices, nodes, page  # noqa: E402

from hmi import assembly as asm, parts, screen  # noqa: E402


def rules(res) -> list[str]:
    return [e.get("rule") for e in res.g0_errors()]


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = L.Parent()

    @classmethod
    def tearDownClass(cls):
        cls.base.close()

    def test_a_part_id_used_twice_is_refused_by_its_rule_name(self):
        a = assembly(home={"w": 100, "h": 50, "parts": {"labels": [{"id": "T", "x": 0, "y": 0, "w": 50, "h": 20,
                                                                    "text": "same id as a part"}]}})
        res = self.base.screen(page(a), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        self.assertEqual(rules(res), ["assembly-part-ids"])
        self.assertIn("T", res.g0_errors()[0]["message"])

    def test_a_schema_failure_writes_the_report_with_the_errors(self):
        a = assembly()
        a["parts"]["labels"][0]["align"] = "justify"
        res = self.base.screen(page(a), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        self.assertIs(res.report["gates"]["ok"], False)
        self.assertIs(res.report["gates"]["G0"]["ok"], False)
        self.assertEqual(rules(res), ["schema"])
        self.assertIn("align", res.g0_errors()[0]["message"])

    def test_the_local_kinds_file_must_be_a_list_of_names(self):
        for bad in ({"kinds": [KIND]}, [KIND, 3]):
            res = self.base.screen(page(assembly()), dev=devices("Skid1"), local_kinds=bad)
            self.assertEqual(res.code, 1, bad)
            self.assertIn("--local-kinds", res.out)

    def test_the_kind_view_binds_each_dynamic_part_indirectly_through_the_device(self):
        res = self.base.screen(page(assembly()), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertEqual(res.code, 0, res.text[-1500:])
        view = res.view(f"Local/{KIND_VIEW}/Assembly")
        self.assertEqual(view["params"], {"deviceId": ""})
        bindings = [b["binding"] for b in list(view["propConfig"].values()) + [
            c for n in nodes(view) for c in (n.get("propConfig") or {}).values()] if b.get("binding", {}).get("type") == "tag"]
        self.assertTrue(bindings)
        for b in bindings:
            self.assertEqual(b["config"]["mode"], "indirect", b)
            self.assertEqual(b["config"]["references"], {"0": "{view.params.deviceId}"})
            self.assertTrue(b["config"]["tagPath"].startswith("{0}/"), b)
        self.assertEqual(sorted(b["config"]["tagPath"] for b in bindings), ["{0}/state", "{0}/value"])
        confirm = next(n for n in nodes(res.view(f"Local/{KIND_VIEW}/Home")) if n["meta"]["name"] == "Confirm")   # the button is in the Home
        script = confirm["events"]["component"]["onActionPerformed"]["config"]["script"]
        self.assertIn("cadre.hmi.page_pulse(self.session, self.view.params.deviceId + '/cmdStart')", script)

    def test_the_shapes_are_drawn_in_the_neutral_stroke_with_no_fill(self):
        a = assembly()
        a["parts"]["shapes"] = [
            {"id": "S1", "x": 0, "y": 0, "w": 50, "h": 20, "form": "rect"},
            {"id": "S2", "x": 0, "y": 30, "w": 50, "h": 20, "form": "ellipse"},
            {"id": "S3", "x": 60, "y": 0, "w": 50, "h": 20, "form": "polyline", "points": [[0, 0], [10, 10], [20, 0]]},
            {"id": "S4", "x": 60, "y": 30, "w": 50, "h": 20, "form": "polygon", "points": [[0, 0], [10, 10], [20, 0]]}]
        res = self.base.screen(page(a), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertEqual(res.code, 0, res.text[-1500:])
        shapes = {n["meta"]["name"]: n for n in nodes(res.view(f"Local/{KIND_VIEW}/Assembly")) if n["meta"]["name"].startswith("Shape_")}
        els = {k: v["props"]["elements"][0] for k, v in shapes.items()}
        self.assertEqual({k: e["type"] for k, e in els.items()},
                         {"Shape_S1": "rect", "Shape_S2": "ellipse", "Shape_S3": "path", "Shape_S4": "polygon"})
        self.assertEqual(els["Shape_S4"]["points"], "0,0 10,10 20,0")
        for e in els.values():
            self.assertEqual((e["fill"]["paint"], e["stroke"]["paint"]), ("none", "var(--element-neutral-color)"))

    def test_a_button_of_an_assembly_is_a_declared_command_of_its_device(self):
        desc = page(assembly("A1", device="Skid1"), assembly("A2", device="Skid2", x=300))
        self.assertEqual(parts.commands_index([desc]), [
            {"path": f"{TAG_ROOT}/Skid1/cmdStart", "ms": asm.PULSE_MS},
            {"path": f"{TAG_ROOT}/Skid2/cmdStart", "ms": asm.PULSE_MS}])

    def test_a_local_device_without_a_model_has_the_members_its_parts_name(self):
        doc = screen.tags_document([page(assembly("A1", device="Skid1"))])
        skid = next(t for t in doc["tags"] if t["name"] == "Skid1")
        self.assertEqual({t["name"]: t["dataType"] for t in skid["tags"]},
                         {"value": "Float8", "state": "Boolean", "cmdStart": "Boolean"})


if __name__ == "__main__":
    unittest.main()
