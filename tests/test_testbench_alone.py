"""Tests of `screen.py --component-test --tag-root` (S10-B, B8 Table 109): the component test page built alone.

Before this extension `--descriptor` was required and `--component-test` took the descriptors' one `tagRoot`. With
`--tag-root` and no descriptor the generator builds the page from the catalogue alone and writes the descriptor and
the devices file it generated (`--write-descriptor DIR`, `--write-devices FILE`), which gate G11 and the walk read.
A build that gives descriptors changes nothing. Nothing here needs the gateway.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import screen, testbench  # noqa: E402
from hmi import parent as par  # noqa: E402

TAG_ROOT = "[default]cadre_hmi_bench"
PROJECT = "cadre_hmi_bench"


def run(argv, out):
    """screen.main() with `argv`, the parent written beside the project as the deploy writes it; (code, printed)."""
    prj, _ = par.build_parent()
    prj.write(out)
    printed = []
    with mock.patch.object(sys, "argv", ["screen.py", *argv]), \
            mock.patch("builtins.print", side_effect=lambda *a, **k: printed.append(" ".join(map(str, a)))):
        code = screen.main()
    return code, "\n".join(printed)


class AloneTests(unittest.TestCase):
    def build(self, d, *extra):
        out = Path(d) / "build"
        argv = ["--project", PROJECT, "--component-test", "--tag-root", TAG_ROOT, "--render", "module",
                "--frame", "asm", "--faceplate", "asm", "--app-name", "Component test", "--out", str(out),
                "--report", str(Path(d) / "report.json"),
                "--write-descriptor", str(Path(d) / "bridge" / "descriptors"),
                "--write-devices", str(Path(d) / "bridge" / "devices.json"), *extra]
        return out, *run(argv, out)

    def test_the_page_builds_from_the_tag_root_alone_and_passes_the_gates(self):
        with tempfile.TemporaryDirectory() as d:
            out, code, printed = self.build(d)
            self.assertEqual(code, 0, printed)
            report = json.loads((Path(d) / "report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["gates"]["ok"])
            self.assertIn("/component-test", report)
            self.assertTrue((out / PROJECT / "com.inductiveautomation.perspective" / "views" / "Screens"
                             / "ComponentTest" / "view.json").exists())
            self.assertTrue((out / f"{PROJECT}.component-test-tags.json").exists())

    def test_the_descriptor_and_the_devices_are_written_where_asked(self):
        with tempfile.TemporaryDirectory() as d:
            _, code, printed = self.build(d)
            self.assertEqual(code, 0, printed)
            desc = json.loads((Path(d) / "bridge" / "descriptors" / "component-test.json").read_text(encoding="utf-8"))
            self.assertEqual(desc["screen"]["route"], "/component-test")
            self.assertEqual(desc["tagRoot"], TAG_ROOT)
            devices = json.loads((Path(d) / "bridge" / "devices.json").read_text(encoding="utf-8"))
            self.assertEqual(devices["schema"], "cadre-hmi-devices/1")
            self.assertEqual(devices["tagRoot"], TAG_ROOT)
            self.assertEqual(len(devices["devices"]),
                             len(testbench.model_entries(testbench.device_specs(TAG_ROOT, "Component test"))))

    def test_the_written_files_end_in_a_line_feed_and_hold_no_carriage_return(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            for name in ("descriptors/component-test.json", "devices.json"):
                data = (Path(d) / "bridge" / name).read_bytes()
                self.assertTrue(data.endswith(b"\n"), name)
                self.assertNotIn(b"\r", data, name)

    def test_the_generated_descriptor_builds_the_same_page_as_the_alone_build(self):
        with tempfile.TemporaryDirectory() as d:
            self.build(d)
            again = Path(d) / "again"
            argv = ["--project", PROJECT, "--descriptor", str(Path(d) / "bridge" / "descriptors" / "component-test.json"),
                    "--devices-file", str(Path(d) / "bridge" / "devices.json"), "--render", "module", "--frame", "asm",
                    "--faceplate", "asm", "--out", str(again)]
            # the page's local assembly needs the option once the page is a plain descriptor (NOTE-WFB-10 section 11.2
            # item 6: only --component-test allows its own kind without it)
            kinds = Path(d) / "local-kinds.json"
            kinds.write_text(json.dumps([testbench.LOCAL_KIND]), encoding="utf-8")
            argv += ["--local-kinds", str(kinds)]
            code, printed = run(argv, again)
            self.assertEqual(code, 0, printed)

    def test_without_a_tag_root_or_a_descriptor_the_build_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            code, printed = run(["--project", PROJECT, "--component-test", "--out", str(Path(d) / "build")],
                                Path(d) / "build")
            self.assertEqual(code, 1)
            self.assertIn("--tag-root", printed)

    def test_a_build_without_the_component_test_still_needs_a_descriptor(self):
        with tempfile.TemporaryDirectory() as d:
            code, printed = run(["--project", PROJECT, "--tag-root", TAG_ROOT, "--out", str(Path(d) / "build")],
                                Path(d) / "build")
            self.assertEqual(code, 1)
            self.assertIn("--descriptor", printed)

    def test_a_tag_root_without_a_provider_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            code, printed = run(["--project", PROJECT, "--component-test", "--tag-root", "cadre_hmi_bench",
                                 "--out", str(Path(d) / "build")], Path(d) / "build")
            self.assertEqual(code, 1)
            self.assertIn("--tag-root", printed)


if __name__ == "__main__":
    unittest.main()
