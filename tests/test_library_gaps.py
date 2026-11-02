"""Tests of `tools/hmi/library_gaps.py` (S10-B, ARCH-WFB-01 revision B8 Table 109, schema `cadre-hmi-library-gaps/1`)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump, fixture, inputs, validate  # noqa: E402

from hmi import asm_model, library_gaps  # noqa: E402

DESIGNS = ("asm-design-overview.json", "asm-design-pumpstation.json")


def prepare(d: Path):
    ins = inputs(d)
    out = d / "model"
    assert asm_model.main([a for k, v in ins.items() for a in (f"--{k}", str(v))]
                          + ["--tag-root", "[default]cadre_hmi_plant", "--out", str(out)]) == 0
    lst = d / "designs.txt"
    paths = [dump(d / "designs" / n, fixture(n)) for n in DESIGNS]
    lst.write_text("\n".join(str(p) for p in paths) + "\n", encoding="utf-8", newline="\n")
    return out / "model.json", lst


def argv_of(model, lst, out, *extra):
    return ["--model", str(model), "--designs", str(lst), "--catalogue", str(ROOT / "library" / "contracts.json"),
            "--profile", str(ROOT / "library" / "profile.json"), "--module", str(ROOT / "module" / "components.json"),
            "--out", str(out), *extra]


class GapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.model, cls.lst = prepare(cls.dir)
        cls.code = library_gaps.main(argv_of(cls.model, cls.lst, cls.dir / "g", "--module-first"))
        cls.doc = json.loads((cls.dir / "g" / "gaps.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def kinds(self):
        return {k["kind"]: k for k in self.doc["kinds"]}

    def test_a_kind_without_a_library_symbol_leaves_the_run_with_an_open_gap_and_exit_2(self):
        self.assertEqual(self.code, 2)
        self.assertEqual(self.doc["open_count"], 1)

    def test_the_document_validates_against_its_schema_with_the_registry_identifier(self):
        self.assertEqual(validate(self.doc, "cadre-hmi-library-gaps-1.json"), [])
        schema = json.loads((ROOT / "schemas" / "cadre-hmi-library-gaps-1.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "cadre-hmi-library-gaps/1")
        self.assertEqual(self.doc["schema"], "cadre-hmi-library-gaps/1")

    def test_every_kind_of_the_designs_has_a_resolution(self):
        kinds = self.kinds()
        self.assertEqual(set(kinds), {"switch", "pump", "readout", "indicator", "tank", "valve", "sequence", "ups"})
        self.assertTrue(all(k["resolution"] in ("module", "library", "gap") for k in kinds.values()))

    def test_module_first_chooses_the_module_where_it_has_a_part(self):
        k = self.kinds()
        for name in ("pump", "tank", "valve", "readout"):
            self.assertEqual(k[name]["resolution"], "module", name)
            self.assertEqual(k[name]["audit"]["module_part"], f"cadre.ob.{name}")
            self.assertEqual(k[name]["audit"]["choice"], "module")
        self.assertEqual(k["sequence"]["resolution"], "library")
        self.assertIsNone(k["sequence"]["audit"]["module_part"])
        self.assertEqual(k["sequence"]["audit"]["library_part"], "Instrument/Sequence")
        self.assertTrue(all(x["audit"]["reason"] for x in k.values()))

    def test_without_module_first_the_library_is_chosen_where_it_has_the_kind(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(library_gaps.main(argv_of(self.model, self.lst, Path(t))), 2)
            doc = json.loads((Path(t) / "gaps.json").read_text(encoding="utf-8"))
            self.assertEqual({k["kind"]: k["resolution"] for k in doc["kinds"]}["pump"], "library")

    def test_counts_and_pages(self):
        k = self.kinds()
        self.assertEqual(k["pump"]["count"], 3)
        self.assertEqual(k["pump"]["pages"], ["Overview", "PumpStation"])
        self.assertEqual(k["tank"]["pages"], ["PumpStation"])
        self.assertEqual(k["readout"]["count"], 4)

    def test_a_gap_has_a_status_a_reason_and_the_rows_it_affects(self):
        g = self.doc["gaps"][0]
        self.assertEqual((g["id"], g["kind"], g["status"]), ("GAP-ups", "ups", "open"))
        self.assertEqual(g["item"], "PumpStation:d_ups")
        self.assertTrue(g["reason"] and g["library_today"] and g["needed"])
        self.assertEqual(g["mapping_rows"], ["PumpStation:d_ups"])

    def test_an_accepted_gap_does_not_count_as_open(self):
        with tempfile.TemporaryDirectory() as t:
            acc = dump(Path(t) / "acc.json", [{"id": "GAP-ups", "reason": "the owner accepts a counted box"}])
            self.assertEqual(library_gaps.main(argv_of(self.model, self.lst, Path(t) / "g", "--module-first",
                                                       "--accepted", str(acc))), 0)
            doc = json.loads((Path(t) / "g" / "gaps.json").read_text(encoding="utf-8"))
            self.assertEqual((doc["gaps"][0]["status"], doc["open_count"]), ("accepted", 0))
            self.assertIn("owner accepts", doc["gaps"][0]["reason"])

    def test_accepted_ids_may_be_one_to_a_line(self):
        with tempfile.TemporaryDirectory() as t:
            acc = Path(t) / "acc.txt"
            acc.write_text("GAP-ups\n", encoding="utf-8")
            self.assertEqual(library_gaps.main(argv_of(self.model, self.lst, Path(t) / "g", "--accepted", str(acc))), 0)

    def test_a_catalogue_without_a_kind_is_what_makes_the_gap(self):
        with tempfile.TemporaryDirectory() as t:
            prof = json.loads((ROOT / "library" / "profile.json").read_text(encoding="utf-8"))
            del prof["kinds"]["sequence"]
            p = dump(Path(t) / "profile.json", prof)
            argv = argv_of(self.model, self.lst, Path(t) / "g")
            argv[argv.index("--profile") + 1] = str(p)
            self.assertEqual(library_gaps.main(argv), 2)
            doc = json.loads((Path(t) / "g" / "gaps.json").read_text(encoding="utf-8"))
            self.assertEqual(doc["open_count"], 2)

    def test_the_audit_table_is_written_for_the_block(self):
        audit = json.loads((self.dir / "g" / "audit.json").read_text(encoding="utf-8"))
        self.assertEqual({r["kind"] for r in audit}, set(self.kinds()))
        self.assertEqual(set(audit[0]), {"kind", "count", "module_part", "library_part", "choice", "reason"})

    def test_provenance_and_lf(self):
        self.assertEqual(self.doc["provenance"]["tool"], "tools/hmi/library_gaps.py")
        self.assertNotIn(b"\r", (self.dir / "g" / "gaps.json").read_bytes())

    def test_cli_exit_codes(self):
        run = lambda a: subprocess.run([sys.executable, str(ROOT / "tools" / "hmi" / "library_gaps.py"), *a],  # noqa: E731
                                       capture_output=True, text=True, cwd=ROOT)
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(run(argv_of(self.model, self.lst, Path(t), "--module-first")).returncode, 2)
            bad = argv_of(Path(t) / "none.json", self.lst, Path(t))
            r = run(bad)
            self.assertEqual(r.returncode, 1)
            self.assertIn("model", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
