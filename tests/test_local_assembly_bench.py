"""Tests of the component test page's row for the synthetic local kind `benchlocal` (NOTE-WFB-10 section 11.2 item 8;
acceptance corpus 3, offline part: G0 to G7, coverage and tags bound for `benchlocal`). Work package WP-W03, written from
the note before the feature exists.

The row: device folder `Bench/Local1` under the test tag root, members `value` (Float8, a readout), `state` (Boolean, an
indicator), `cmdStart` (Boolean, a pulse button) and `alarm` (Boolean, one alarm of priority High); a Home with a readout of
`value`, an indicator of `state` and the pulse button; memory tags with the defaults 42.0, true, false and false.

Nothing here needs the gateway.
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import local_support as L  # noqa: E402
from local_support import KIND, TAG_ROOT, assembly, devices, nodes, page  # noqa: E402

from hmi import library_profile, page_checks, screen, testbench  # noqa: E402

FOLDER = testbench.FOLDER
KIND_BENCH = "benchlocal"
DEVICE = f"{FOLDER}/Bench/Local1"      # the test devices' ids start with the test folder (test_testbench.py)


def leaves(folder, path=""):
    for t in folder.get("tags", []):
        here = f"{path}/{t['name']}" if path else t["name"]
        if t["tagType"] == "Folder":
            yield from leaves(t, here)
        else:
            yield here, t


def parts_of(a: dict, key="parts") -> list:
    src = a.get(key) or {}
    src = src.get("parts", src) if key == "home" else src
    return [p for arr in ("labels", "symbols", "lines", "buttons", "shapes") for p in src.get(arr, [])]


class BenchRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = screen.load_contracts()
        cls.prof = library_profile.build(cls.contracts)
        cls.bench = testbench.build(cls.contracts, cls.prof, TAG_ROOT)
        cls.desc = cls.bench.descriptor
        mine = [a for a in cls.desc.get("assemblies", []) if a["kind"] == KIND_BENCH]
        cls.asm = mine[0] if mine else None

    def test_the_page_draws_one_assembly_of_the_kind_benchlocal_on_the_row_device(self):
        mine = [a for a in self.desc.get("assemblies", []) if a["kind"] == KIND_BENCH]
        self.assertEqual(len(mine), 1)
        self.assertEqual(mine[0]["device"], DEVICE)

    def test_the_page_still_passes_g0_with_the_assembly(self):
        self.assertTrue(self.desc.get("assemblies"), "the page draws an assembly")
        self.assertEqual(screen.schema_errors([self.desc], ["bench"]), [])
        self.assertEqual(testbench.check(self.desc, self.contracts), [])

    def test_the_assembly_has_a_home_of_a_readout_an_indicator_and_the_pulse_button(self):
        self.assertIsNotNone(self.asm)
        home = self.asm["home"]["parts"]
        self.assertEqual([(s["kind"], s["member"]) for s in home.get("symbols", [])],
                         [("readout", "value"), ("indicator", "state")])
        self.assertEqual([b["member"] for b in home.get("buttons", [])], ["cmdStart"])

    def test_every_dynamic_part_of_the_assembly_names_a_member_of_the_row(self):
        self.assertIsNotNone(self.asm)
        members = {"value", "state", "cmdStart", "alarm"}
        for key in ("parts", "home"):
            for p in parts_of(self.asm, key):
                if "member" in p:
                    self.assertIn(p["member"], members, (key, p["id"]))
        self.assertEqual(self.asm["kind"], KIND_BENCH)

    def test_the_device_model_entry_is_of_kind_local_with_the_four_members(self):
        entry = next((d for d in self.bench.devices if d["id"] == DEVICE), None)
        self.assertIsNotNone(entry, [d["id"] for d in self.bench.devices])
        self.assertEqual(entry["kind"], "local")
        self.assertEqual({m: s["type"] for m, s in entry["members"].items()},
                         {"value": "Float8", "state": "Boolean", "cmdStart": "Boolean", "alarm": "Boolean"})
        self.assertIs(entry["members"]["cmdStart"].get("pulse"), True)
        self.assertEqual(entry["members"]["cmdStart"]["access"], "write")
        for m in ("value", "state", "alarm"):
            self.assertEqual(entry["members"][m]["access"], "read", m)

    def test_the_tags_are_memory_tags_with_the_stated_defaults_and_one_high_alarm(self):
        flat = dict(leaves(self.bench.tags))
        self.assertTrue(all(f"Bench/Local1/{m}" in flat for m in ("value", "state", "cmdStart", "alarm")),
                        "the four members are tags of the row's folder")
        want = {"value": ("Float8", 42.0), "state": ("Boolean", True), "cmdStart": ("Boolean", False),
                "alarm": ("Boolean", False)}
        for member, (dtype, value) in want.items():
            tag = flat[f"Bench/Local1/{member}"]
            self.assertEqual((tag["valueSource"], tag["dataType"], tag["value"]), ("memory", dtype, value), member)
        self.assertEqual([a["priority"] for a in flat["Bench/Local1/alarm"]["alarms"]], ["High"])
        for member in ("value", "state", "cmdStart"):
            self.assertNotIn("alarms", flat[f"Bench/Local1/{member}"], member)

    def test_the_row_is_in_the_device_specifications_and_the_model_entries(self):
        specs = testbench.device_specs(TAG_ROOT, "Component test")
        local = {k: s for k, s in specs.items() if s["kind"] == "local"}
        self.assertEqual(len(local), 1)
        spec = next(iter(local.values()))
        self.assertEqual(set(spec["members"]), {"value", "state", "cmdStart", "alarm"})
        entries = testbench.model_entries(specs)
        self.assertEqual([e["id"] for e in entries if e["kind"] == "local"], [DEVICE])

    def test_the_profile_gains_the_device_kind_local_and_the_test_page_has_a_device_for_every_kind(self):
        self.assertIn("local", sorted(self.prof["deviceKinds"]))
        kinds = {d["kind"] for d in self.bench.devices}
        self.assertEqual(set(self.prof["deviceKinds"]) - kinds - {"readout", "instrument-field"}, set())

    def test_an_assembly_id_the_page_uses_twice_is_named_by_the_check(self):
        bad = copy.deepcopy(self.desc)
        self.assertTrue(bad.get("assemblies"), "the page draws an assembly")
        clone = copy.deepcopy(bad["assemblies"][0])
        clone["id"] = bad["symbols"][0]["id"]
        bad["assemblies"].append(clone)
        self.assertIn("used twice", " ".join(testbench.check(bad, self.contracts)))

    def test_coverage_and_tags_bound_for_benchlocal_offline(self):
        self.assertIsNotNone(self.asm)
        aid = self.asm["id"]
        dynamic = lambda a, key: [p for p in parts_of(a, key) if "member" in p]   # noqa: E731
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            counts = {}
            for name, doc in (("with", self.desc),
                              ("without", {**self.desc, "assemblies": [a for a in self.desc.get("assemblies", [])
                                                                       if a["id"] != aid]})):
                L.dump(d / name / "descriptors" / "ComponentTest.json", doc)
                devs = {"schema": "cadre-hmi-devices/1", "tagRoot": TAG_ROOT, "devices": self.bench.devices}
                code = page_checks.main([
                    "--descriptors", str(d / name / "descriptors"),
                    "--devices", str(L.dump(d / name / "devices.json", devs)),
                    "--tags", str(L.dump(d / name / "tags.json", {"name": "cadre_hmi_loc", "tagType": "Folder",
                                                                  "tags": [self.bench.tags]})),
                    "--navtable", str(L.dump(d / name / "nav.json", [])), "--project", "cadre_hmi_loc",
                    "--out", str(d / name / "out")])
                self.assertIn(code, (0, 2))
                doc = json.loads((d / name / "out" / "checks.json").read_text(encoding="utf-8"))
                counts[name] = doc
            tb = counts["with"]["tags_bound"]
            self.assertEqual([u for u in tb["unbound"] if aid + "/" in u], [], tb["unbound"])
            self.assertEqual([t for t in tb["unresolved_tags"] if aid + "/" in t], [], tb["unresolved_tags"])
            extra = tb["value_components"] - counts["without"]["tags_bound"]["value_components"]
            own = len(dynamic(self.asm, "parts"))
            self.assertIn(extra, (own, own + len(dynamic(self.asm, "home"))), (extra, own))
            self.assertTrue(own >= 1)


class BenchBuildTests(unittest.TestCase):
    """`screen.py --component-test` through the command line: the page's assembly builds, with the option or without it."""

    @classmethod
    def setUpClass(cls):
        cls.base = L.Parent()

    @classmethod
    def tearDownClass(cls):
        cls.base.close()

    def plain_page(self):
        doc = page()
        doc.pop("assemblies")
        return doc

    def test_the_page_builds_through_g0_to_g7_with_its_local_kind_listed(self):
        res = self.base.screen(self.plain_page(), local_kinds=[KIND_BENCH], extra=["--component-test"])
        self.assertEqual(res.code, 0, res.text[-2500:])
        self.assertIs(res.report["gates"]["ok"], True)
        self.assertEqual(res.g0_errors(), [])
        self.assertIn("Local/Benchlocal/Assembly/view.json", res.view_files())
        self.assertIn("Local/Benchlocal/Home/view.json", res.view_files())
        embeds = [n for n in nodes(res.view("Screens/ComponentTest"))
                  if n["type"] == "ia.display.view" and n["props"]["path"] == "Local/Benchlocal/Assembly"]
        self.assertEqual([n["props"]["params"]["deviceId"] for n in embeds], [f"{TAG_ROOT}/{DEVICE}"])

    def test_the_pages_own_assembly_needs_no_listing_by_the_user(self):
        # the existing command line test builds `--component-test` with no local kinds file and expects exit 0
        for listed in (None, [KIND]):
            res = self.base.screen(self.plain_page(), local_kinds=listed, extra=["--component-test"])
            self.assertEqual(res.code, 0, (listed, res.text[-2500:]))
            self.assertEqual(res.g0_errors(), [], listed)
            self.assertIn("Local/Benchlocal/Assembly/view.json", res.view_files())

    def test_the_g7_device_count_includes_the_row_and_the_users_page_with_its_own_kind_builds_beside_it(self):
        res = self.base.screen(page(assembly()), dev=devices("Skid1"), local_kinds=[KIND], extra=["--component-test"])
        self.assertEqual(res.code, 0, res.text[-2500:])
        contracts = screen.load_contracts()
        bench = testbench.build(contracts, library_profile.build(contracts), TAG_ROOT)
        self.assertEqual(res.report["gates"]["G7_devices"]["devices"], 1 + len(bench.devices))
        self.assertEqual(res.report["gates"]["G7_devices"]["problems"], [])
        self.assertIn("Local/Skid/Assembly/view.json", res.view_files())
        self.assertIn("Local/Benchlocal/Assembly/view.json", res.view_files())

    def test_a_users_assembly_is_still_refused_without_the_option_beside_the_component_test(self):
        res = self.base.screen(page(assembly()), dev=devices("Skid1"), local_kinds=None, extra=["--component-test"])
        self.assertNotEqual(res.code, 0)
        self.assertIn("assembly-without-local-kinds", res.g0_rules(), res.g0_errors())

    def test_the_written_descriptor_carries_the_assembly_for_the_walk_and_the_glass_gates(self):
        with tempfile.TemporaryDirectory() as td:
            res = self.base.screen(self.plain_page(), local_kinds=[KIND_BENCH],
                                   extra=["--component-test", "--write-descriptor", td])
            self.assertEqual(res.code, 0, res.text[-2500:])
            written = json.loads((Path(td) / "component-test.json").read_text(encoding="utf-8"))
            self.assertEqual([a["kind"] for a in written["assemblies"]], [KIND_BENCH])


if __name__ == "__main__":
    unittest.main()
