"""The elements list and the placement tool's outputs are strict JSON (WorkflowBuilder NOTE-WFB-10, COB-210).

`obc-number-input-field`'s `value` defaults to `NaN` in the pinned release. Python's `json` reads and writes `NaN`, but no
JSON reader of the manager accepts it: stage A's survey run failed on the elements list carried in `proposal_source`.
"""

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "module" / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "hmi"))

import gen_openbridge_elements  # noqa: E402
import provenance  # noqa: E402


def _refuse(constant):
    raise ValueError(f"not JSON: {constant}")


class ElementDefaultsTests(unittest.TestCase):
    def test_a_non_finite_default_stays_text(self):
        for text in ("NaN", "Infinity", "-Infinity"):
            self.assertEqual(gen_openbridge_elements.parse_default(text), text)

    def test_json_defaults_still_parse(self):
        self.assertEqual(gen_openbridge_elements.parse_default("1.5"), 1.5)
        self.assertEqual(gen_openbridge_elements.parse_default('"on"'), "on")
        self.assertIs(gen_openbridge_elements.parse_default("false"), False)
        self.assertIsNone(gen_openbridge_elements.parse_default(None))
        self.assertEqual(gen_openbridge_elements.parse_default("this.x"), "this.x")

    def test_the_committed_elements_list_is_strict_json(self):
        text = (ROOT / "module" / "openbridge-elements.json").read_text("utf-8")
        doc = json.loads(text, parse_constant=_refuse)
        number_field = next(e for e in doc["elements"] if e["tag"] == "obc-number-input-field")
        value = next(p for p in number_field["properties"] if p["name"] == "value")
        self.assertEqual(value["default"], "NaN")


class StrictWriteTests(unittest.TestCase):
    def test_strict_write_refuses_a_non_finite_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                provenance.write_json(Path(tmp) / "x.json", {"x": math.nan}, strict=True)

    def test_the_default_write_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = provenance.write_json(Path(tmp) / "x.json", {"x": 1.0})
            self.assertEqual(json.loads(path.read_text("utf-8")), {"x": 1.0})

    def test_the_placement_tool_writes_its_outputs_strictly(self):
        source = (ROOT / "tools" / "hmi" / "placement_survey.py").read_text("utf-8")
        for name in ("survey.json", "unmapped.json", "proposal_source.json", "gaps.json"):
            self.assertIn(f'write_json(out / "{name}", ', source)
            line = next(x for x in source.splitlines() if f'out / "{name}"' in x and "write_json" in x)
            self.assertIn("strict=True", line, name)


class TreeStateMessageTests(unittest.TestCase):
    def test_the_paths_keep_their_first_letter_whether_or_not_the_output_was_stripped(self):
        for out in (" M module/openbridge-elements.json\n?? library/profile.json", "M module/openbridge-elements.json"):
            self.assertIn("module/openbridge-elements.json", provenance.porcelain_paths(out))
        self.assertEqual(provenance.porcelain_paths("MM a.json\n?? b.json"), ["a.json", "b.json"])


if __name__ == "__main__":
    unittest.main()
