"""The library profile names the parent it describes (WorkflowBuilder WFB-153, S10-G finding F2): the default stays
`cadre_hmi_base`, and the ASM parent `cadre_hmi_base_asm` can be given, by `library_profile.build`, by its command
line and by the commands that read the profile (`screen.py`, `asm_descriptors.py`, `library_gaps.py`)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump  # noqa: E402

from hmi import asm_descriptors, library_gaps, library_profile, screen  # noqa: E402


class ProfileParentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = screen.load_contracts()

    def test_the_default_parent_is_unchanged(self):
        self.assertEqual(library_profile.build(self.contracts)["library"], "cadre_hmi_base")
        self.assertEqual(library_profile.build(self.contracts, "cadre_hmi_base"), library_profile.build(self.contracts))
        written = json.loads((ROOT / "library" / "profile.json").read_text(encoding="utf-8"))
        self.assertEqual(library_profile.build(self.contracts), written)        # the tracked file still equals it

    def test_a_profile_for_the_asm_parent(self):
        p = library_profile.build(self.contracts, "cadre_hmi_base_asm")
        self.assertEqual(p["library"], "cadre_hmi_base_asm")
        base = library_profile.build(self.contracts)
        self.assertEqual({k: v for k, v in p.items() if k != "library"}, {k: v for k, v in base.items() if k != "library"})

    def test_a_parent_must_start_cadre_hmi(self):
        with self.assertRaises(ValueError):
            library_profile.build(self.contracts, "base")

    def test_write_takes_the_parent(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "p.json"
            library_profile.write(self.contracts, [out], parent="cadre_hmi_base_asm")
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["library"], "cadre_hmi_base_asm")

    def test_the_command_line_takes_the_parent(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "p.json"
            with mock.patch.object(sys, "argv", ["library_profile.py", "--out", str(out), "--parent", "cadre_hmi_base_asm"]), \
                    mock.patch("builtins.print"):
                self.assertEqual(library_profile.main(), 0)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["library"], "cadre_hmi_base_asm")

    def test_library_gaps_checks_the_profile_names_the_parent_it_is_given(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model = dump(d / "m.json", {"pages": [], "mapping": []})
            lst = d / "l.txt"
            lst.write_text("", encoding="utf-8")
            prof = dump(d / "prof.json", library_profile.build(self.contracts, "cadre_hmi_base_asm"))
            base = ["--model", str(model), "--designs", str(lst), "--catalogue", str(ROOT / "library" / "contracts.json"),
                    "--profile", str(prof), "--module", str(ROOT / "module" / "components.json"), "--out", str(d / "o")]
            self.assertEqual(library_gaps.main(base + ["--parent", "cadre_hmi_base_asm"]), 0)
            self.assertEqual(library_gaps.main(base + ["--parent", "cadre_hmi_base"]), 1)
            self.assertEqual(library_gaps.main(base), 0)                          # without it, as before

    def test_asm_descriptors_builds_its_profile_for_its_parent(self):
        seen = []
        real = library_profile.build
        with mock.patch.object(library_profile, "build", side_effect=lambda c, parent="cadre_hmi_base": seen.append(parent) or real(c, parent)):
            ctx_profile = asm_descriptors.profile_for("cadre_hmi_base_asm")
        self.assertEqual(seen, ["cadre_hmi_base_asm"])
        self.assertEqual(ctx_profile["library"], "cadre_hmi_base_asm")


if __name__ == "__main__":
    unittest.main()
