"""Tests of `tools/hmi/tag_values.py`, `tag_set.py` and `bench_descriptor.py` (COB-181). The gateway is a fake held in
memory (the two tag routes of ctig's `Gateway`); nothing here uses the network. Synthetic names only."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "hmi"))

import bench_descriptor  # noqa: E402
import deploy  # noqa: E402
import tag_set  # noqa: E402
import tag_values  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
ROOT_PATH = "[default]cadre_hmi_synth"


class FakeGw:
    """tags_export returns the successive documents given; tags_import records its calls."""

    def __init__(self, exports=()):
        self.exports = list(exports)
        self.calls = []
        self.imports = []

    def tags_export(self, provider, path):
        self.calls.append(("export", provider, path))
        return self.exports.pop(0) if len(self.exports) > 1 else self.exports[0]

    def tags_import(self, provider, path, doc):
        self.imports.append((provider, path, doc))
        return {"successCount": 1, "failureCount": 0}


def folder(**values):
    return {"name": "src", "tagType": "Folder", "tags": [
        {"name": k, "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Float8", "value": v}
        for k, v in values.items()] + [{"name": "sub", "tagType": "Folder", "tags": [
            {"name": "deep", "tagType": "AtomicTag", "value": 1}]}]}


def call(main, *argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


def patched(gw):
    return mock.patch.object(deploy, "_gateway", return_value=(gw, "test"))


class TagValuesTests(unittest.TestCase):
    def test_flatten_reads_nested_folders(self):
        self.assertEqual(tag_values.flatten(folder(a=1)), {"a": 1, "sub/deep": 1})

    def test_split_path_defaults_the_provider(self):
        self.assertEqual(tag_values.split_path("[tags]a/b/"), ("tags", "a/b"))
        self.assertEqual(tag_values.split_path("a/b"), ("default", "a/b"))

    def test_changed_tags_are_reported_and_written(self):
        gw = FakeGw([folder(a=1, b=5), folder(a=2, b=5)])
        with tempfile.TemporaryDirectory() as t, patched(gw), mock.patch("time.sleep") as sl:
            out = Path(t) / "v.json"
            code, text, _ = call(tag_values.main, "--path", "[default]x/src", "--interval", "2", "--out", str(out))
            doc = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        sl.assert_called_once_with(2.0)
        self.assertEqual(doc["schema"], "cadre-hmi-tag-values/1")
        self.assertEqual([c["tag"] for c in doc["changed"]], ["a"])
        self.assertEqual(gw.calls[0], ("export", "default", "x/src"))
        self.assertIn("1 changed", text)

    def test_a_static_folder_exits_2(self):
        gw = FakeGw([folder(a=1)])
        with patched(gw), mock.patch("time.sleep"):
            self.assertEqual(call(tag_values.main, "--path", "x")[0], 2)

    def test_a_non_local_host_is_refused_before_any_call(self):
        gw = FakeGw([folder(a=1)])
        with patched(gw), mock.patch.object(deploy, "GATEWAY", "http://gateway.example.net:8088"):
            code, _, err = call(tag_values.main, "--path", "x")
        self.assertEqual(code, 1)
        self.assertIn("not local", err)
        self.assertEqual(gw.calls, [])

    def test_a_gateway_fault_exits_1(self):
        gw = FakeGw([folder(a=1)])
        gw.tags_export = mock.Mock(side_effect=RuntimeError("HTTP 500"))
        with patched(gw):
            self.assertEqual(call(tag_values.main, "--path", "x")[0], 1)


class TagSetTests(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.file = Path(self._t.name) / "tags.json"
        doc = {"name": "cadre_hmi_synth", "tagType": "Folder", "tags": [
            {"name": "src", "tagType": "Folder", "tags": [
                {"name": "SW1", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Boolean", "value": False},
                {"name": "LV1", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Float8", "value": 1.0}]},
            {"name": "other", "tagType": "Folder", "tags": [
                {"name": "SW2", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Boolean", "value": False}]}]}
        self.file.write_text(json.dumps(doc), encoding="utf-8")

    def tearDown(self):
        self._t.cleanup()

    def args(self, tag="src/SW1", allowed=ROOT_PATH + "/src", *extra):
        return ["--tags-file", str(self.file), "--tag-root", ROOT_PATH, "--tag", tag, "--value", "true",
                "--allowed-root", allowed, *extra]

    def test_sets_the_tag_inside_the_allowed_root(self):
        gw = FakeGw([{}])
        with patched(gw):
            code, out, _ = call(tag_set.main, *self.args())
        self.assertEqual(code, 0)
        prov, path, doc = gw.imports[0]
        self.assertEqual((prov, path), ("default", "cadre_hmi_synth/src"))
        self.assertEqual(doc["tags"][0]["name"], "SW1")
        self.assertIs(doc["tags"][0]["value"], True)
        self.assertIn("SW1", out)

    def test_a_tag_outside_the_allowed_root_is_refused_before_any_call(self):
        gw = FakeGw([{}])
        with patched(gw) as g:
            code, _, err = call(tag_set.main, *self.args("other/SW2"))
        self.assertEqual(code, 2)
        self.assertIn("refused", err)
        g.assert_not_called()
        self.assertEqual(gw.imports, [])

    def test_a_sibling_with_a_shared_prefix_is_not_under_the_root(self):
        with patched(FakeGw([{}])) as g:
            code, _, _ = call(tag_set.main, *self.args("src/SW1", ROOT_PATH + "/sr"))
        self.assertEqual(code, 2)
        g.assert_not_called()

    def test_another_provider_and_a_dotdot_path_are_refused(self):
        with patched(FakeGw([{}])) as g:
            self.assertEqual(call(tag_set.main, *self.args("src/SW1", "[other]cadre_hmi_synth/src"))[0], 2)
            self.assertEqual(call(tag_set.main, *self.args("src/../other/SW2"))[0], 2)
        g.assert_not_called()

    def test_a_tag_that_is_not_boolean_memory_is_refused(self):
        with patched(FakeGw([{}])) as g:
            code, _, err = call(tag_set.main, *self.args("src/LV1"))
        self.assertEqual(code, 2)
        self.assertIn("Boolean memory", err)
        g.assert_not_called()

    def test_dry_run_prints_the_write_and_makes_no_call(self):
        with patched(FakeGw([{}])) as g:
            code, out, _ = call(tag_set.main, *self.args("src/SW1", ROOT_PATH + "/src", "--dry-run"))
        self.assertEqual(code, 0)
        self.assertIn("would set [default]cadre_hmi_synth/src/SW1 = True", out)
        g.assert_not_called()

    def test_a_non_local_host_is_refused(self):
        gw = FakeGw([{}])
        with patched(gw), mock.patch.object(deploy, "GATEWAY", "https://gw.example.net"):
            code, _, err = call(tag_set.main, *self.args())
        self.assertEqual(code, 1)
        self.assertEqual(gw.imports, [])
        self.assertNotIn("token", err.lower().replace("no gateway", ""))

    def test_a_missing_tag_is_refused(self):
        with patched(FakeGw([{}])):
            self.assertEqual(call(tag_set.main, *self.args("src/NOPE"))[0], 2)


class BenchDescriptorTests(unittest.TestCase):
    def run_tool(self, d, *extra):
        devices = Path(d) / "devices.json"
        devices.write_bytes((FIXTURES / "asm-devices.json").read_bytes())
        out = Path(d) / "out"
        code, text, err = call(bench_descriptor.main, "--tag-root", "[default]cadre_hmi_synth", "--devices",
                               str(devices), "--out", str(out), *extra)
        return code, text, out

    def test_writes_the_descriptor_and_the_devices_with_asm_bench_devices(self):
        with tempfile.TemporaryDirectory() as d:
            code, text, out = self.run_tool(d)
            desc = json.loads((out / "ComponentTest.desc.json").read_text(encoding="utf-8"))
            devs = json.loads((out / "devices_with_bench.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        bench = [x for x in devs["devices"] if x["id"].startswith("_componentTest/")]
        self.assertTrue(bench)
        self.assertEqual({x["faceplate"] for x in bench}, {"asm"})
        own = [x for x in devs["devices"] if not x["id"].startswith("_componentTest/")]
        self.assertTrue(own)
        self.assertEqual(desc["tagRoot"], "[default]cadre_hmi_synth")
        self.assertIn(f"--height {desc['screen']['height'] + 200}", text)

    def test_the_margin_is_added_to_the_page_height(self):
        with tempfile.TemporaryDirectory() as d:
            _, text, out = self.run_tool(d, "--margin", "50")
            h = json.loads((out / "ComponentTest.desc.json").read_text(encoding="utf-8"))["screen"]["height"]
        self.assertIn(f"--height {h + 50}", text)

    def test_a_missing_devices_file_exits_1(self):
        with tempfile.TemporaryDirectory() as d:
            code, _, _ = call(bench_descriptor.main, "--tag-root", ROOT_PATH, "--devices", str(Path(d) / "no.json"),
                              "--out", d)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
