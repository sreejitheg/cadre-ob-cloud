"""Gate G11 and the local assembly's device (tranche T3, the owner's word after the first sweep).

The faceplate sweep (`tools/compare/faceplates.py`) takes its expected devices from the descriptors. A local assembly
(NOTE-WFB-10 section 11.2) is neither a symbol nor a card item, but its embed is a leaf the sweep clicks, and the click
opens `Faceplate/ASM/Local` for its device. The first sweep of the component test page opened and read that faceplate
(TB-LOCAL) and failed it as unexpected; the sweep now expects each assembly's device by the title the generator
registers (`assembly.item`: its `title`, else its kind) and, with a device model, the tabs of the kind `local`.

Run from the repository root:  python -m unittest tests.test_g11_local
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "compare"))

import faceplates  # noqa: E402
import local_support as L  # noqa: E402
from hmi import library_profile, screen, testbench  # noqa: E402


class TheExpectedDevices(unittest.TestCase):
    def test_an_assembly_is_expected_by_its_title(self):
        self.assertEqual(faceplates.expected_devices(L.page(L.assembly())), {"Skid"})

    def test_an_assembly_with_no_title_is_expected_by_its_kind(self):
        a = L.assembly()
        a.pop("title")
        self.assertEqual(faceplates.expected_devices(L.page(a)), {L.KIND})

    def test_each_assembly_is_expected_beside_the_symbols(self):
        doc = L.page(L.assembly("A1", device="Skid1", title="SK-1"), L.assembly("A2", device="Skid2", title="SK-2"),
                     symbols=[{"id": "P1", "kind": "pump", "x": 400, "y": 100, "w": 48, "h": 48, "device": "P1",
                               "params": {"tag": "P-1"}}])
        self.assertEqual(faceplates.expected_devices(doc), {"SK-1", "SK-2", "P-1"})

    def test_a_page_with_no_assembly_expects_what_it_did(self):
        doc = L.page(symbols=[{"id": "P1", "kind": "pump", "x": 400, "y": 100, "w": 48, "h": 48, "device": "P1"}])
        doc.pop("assemblies")
        self.assertEqual(faceplates.expected_devices(doc), {"P1"})


class TheDeviceModel(unittest.TestCase):
    def test_the_local_device_expects_the_tabs_of_the_kind_local(self):
        out = faceplates.device_expectations([L.page(L.assembly())], L.devices("Skid1"), "asm")
        self.assertEqual(set(out), {"Skid"})
        self.assertEqual(out["Skid"]["tabs"], ["Home", "Alarms", "Info"])
        self.assertEqual(out["Skid"]["folder"], f"{L.TAG_ROOT}/Skid1")
        self.assertEqual(out["Skid"]["sources"], [faceplates.folder_pattern(f"{L.TAG_ROOT}/Skid1")])
        self.assertIs(out["Skid"]["trend_open"], False)

    def test_an_assembly_whose_device_the_model_lacks_has_no_model_expectation(self):
        self.assertEqual(faceplates.device_expectations([L.page(L.assembly(device="Skid9"))], L.devices("Skid1")), {})


class TheComponentTestPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        contracts = screen.load_contracts()
        cls.bench = testbench.build(contracts, library_profile.build(contracts), "[default]cadre_hmi_ctest")

    def test_the_sweep_expects_the_benchlocal_device_beside_the_symbols(self):
        expected = faceplates.expected_devices(self.bench.descriptor)
        self.assertIn("TB-LOCAL", expected)
        without = dict(self.bench.descriptor, assemblies=[])
        self.assertEqual(expected - faceplates.expected_devices(without), {"TB-LOCAL"})


if __name__ == "__main__":
    unittest.main()
