"""Tests of WP-W02 (NOTE-WFB-10 sections 3.1, 3.2, 11.1, Table 10.5; corpus item 10; threats T8 and T9): the pin check
`module/tools/verify_pin.py`, the elements list `module/openbridge-elements.json`, the map `module/openbridge-map.json`
and the notices.

The pin check runs on a temporary root built here (the four JSON files and a few synthetic `dist/` files listed in a
synthetic manifest given by `--manifest`). One test runs on the real installed tree and is read only; it skips when the
main checkout's `node_modules` is absent. No Gradle, esbuild, npm or gateway.

    python -m unittest tests.test_openbridge_pin
"""
import ast
import hashlib
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The main checkout whose installed package the read only tests read: the owner's Windows path, or the folder named by
# CADRE_OB_MAIN_CHECKOUT (CLAUDE.md section 4; the cloud names this repository).
MAIN = Path(os.environ.get("CADRE_OB_MAIN_CHECKOUT") or "F:/repos/Cadre-Sandbox-OpenBridge")
VERIFY = ROOT / "module" / "tools" / "verify_pin.py"
ELEMENTS = ROOT / "module" / "openbridge-elements.json"
MAP = ROOT / "module" / "openbridge-map.json"
PKG = "@oicl/openbridge-webcomponents"
VERSION = "2.0.0-next.155"
RESOLVED = "https://registry.npmjs.org/@oicl/openbridge-webcomponents/-/openbridge-webcomponents-2.0.0-next.155.tgz"
INTEGRITY = "sha512-PwHJx4APgm+OmHPDdbLQHjVGzaeGaAuRgPfxs1w8ucdW+ZA+ZJPAN9erd3/qvPgjCR/+RjYhsexSIu0wKk2xug=="
REAL_PKG = MAIN / "module" / "web" / "node_modules" / "@oicl" / "openbridge-webcomponents"
REAL_MANIFEST = REAL_PKG / "custom-elements.json"

FILES = {
    "dist/automation/switch/switch.js": b"export const a = 1;\n",
    "dist/automation/bus/bus.js": b"export const b = 2;\n",
    "dist/openbridge.css": b"body{margin:0}\n",
    "custom-elements.json": b'{"modules":[]}\n',
    "bundle/openbridge-webcomponents.bundle.js": b"/* bundle */\n",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_root(base: Path) -> tuple:
    """A temporary `module/web` and a synthetic manifest outside it; returns (root, manifest path)."""
    root = base / "web"
    pkg = root / "node_modules" / "@oicl" / "openbridge-webcomponents"
    write_json(root / "package.json", {"name": "t", "dependencies": {PKG: VERSION}})
    entry = {"version": VERSION, "resolved": RESOLVED, "integrity": INTEGRITY}
    write_json(root / "package-lock.json", {
        "name": "t", "lockfileVersion": 3, "requires": True,
        "packages": {"": {"name": "t", "dependencies": {PKG: VERSION}}, f"node_modules/{PKG}": dict(entry)}})
    write_json(root / "node_modules" / ".package-lock.json", {
        "name": "t", "lockfileVersion": 3, "requires": True, "packages": {f"node_modules/{PKG}": dict(entry)}})
    write_json(pkg / "package.json", {"name": PKG, "version": VERSION})
    files = {}
    for rel, data in FILES.items():
        (pkg / rel).parent.mkdir(parents=True, exist_ok=True)
        (pkg / rel).write_bytes(data)
        files[f"{PKG}/{rel}"] = sha(data)
    files[f"{PKG}/package.json"] = sha((pkg / "package.json").read_bytes())
    manifest = base / "synthetic.sha256.json"
    write_json(manifest, {"package": PKG, "version": VERSION, "integrity": INTEGRITY, "files": files})
    return root, manifest


def run(root: Path, manifest: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(VERIFY), "--root", str(root), "--manifest", str(manifest)],
                          capture_output=True, text=True, timeout=120)


class VerifyPinTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)
        self.root, self.manifest = build_root(self.base)
        self.pkg = self.root / "node_modules" / "@oicl" / "openbridge-webcomponents"

    def refuse(self, expect_path: str) -> subprocess.CompletedProcess:
        r = run(self.root, self.manifest)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(expect_path, r.stdout + r.stderr)
        return r

    def edit(self, path: Path, fn) -> None:
        d = read_json(path)
        fn(d)
        write_json(path, d)

    def test_honest_root_exits_0(self):
        r = run(self.root, self.manifest)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_version_moved_in_package_json_is_refused_and_listed(self):
        self.edit(self.root / "package.json", lambda d: d["dependencies"].__setitem__(PKG, "2.0.0-next.156"))
        self.refuse("package.json")

    def test_range_in_package_json_is_refused(self):
        self.edit(self.root / "package.json", lambda d: d["dependencies"].__setitem__(PKG, "^" + VERSION))
        self.refuse("package.json")

    def test_version_moved_in_lock_root_dependencies_is_refused(self):
        self.edit(self.root / "package-lock.json",
                  lambda d: d["packages"][""]["dependencies"].__setitem__(PKG, "2.0.0-next.156"))
        self.refuse("package-lock.json")

    def test_version_moved_in_lock_package_entry_is_refused(self):
        self.edit(self.root / "package-lock.json",
                  lambda d: d["packages"][f"node_modules/{PKG}"].__setitem__("version", "2.0.0-next.156"))
        self.refuse("package-lock.json")

    def test_version_moved_in_hidden_lock_is_refused(self):
        p = self.root / "node_modules" / ".package-lock.json"
        self.edit(p, lambda d: d["packages"][f"node_modules/{PKG}"].__setitem__("version", "2.0.0-next.156"))
        self.refuse(".package-lock.json")

    def test_version_moved_in_installed_package_json_is_refused(self):
        self.edit(self.pkg / "package.json", lambda d: d.__setitem__("version", "2.0.0-next.156"))
        self.refuse(PKG)

    def test_resolved_differs_in_lock_is_refused(self):
        self.edit(self.root / "package-lock.json", lambda d: d["packages"][f"node_modules/{PKG}"].__setitem__(
            "resolved", RESOLVED.replace("registry.npmjs.org", "example.invalid")))
        self.refuse("package-lock.json")

    def test_integrity_differs_in_lock_is_refused(self):
        self.edit(self.root / "package-lock.json", lambda d: d["packages"][f"node_modules/{PKG}"].__setitem__(
            "integrity", INTEGRITY[:-6] + "AAAA=="))
        self.refuse("package-lock.json")

    def test_resolved_differs_in_hidden_lock_is_refused(self):
        p = self.root / "node_modules" / ".package-lock.json"
        self.edit(p, lambda d: d["packages"][f"node_modules/{PKG}"].__setitem__(
            "resolved", RESOLVED.replace("registry.npmjs.org", "example.invalid")))
        self.refuse(".package-lock.json")

    def test_integrity_differs_in_hidden_lock_is_refused(self):
        p = self.root / "node_modules" / ".package-lock.json"
        self.edit(p, lambda d: d["packages"][f"node_modules/{PKG}"].__setitem__(
            "integrity", INTEGRITY[:-6] + "AAAA=="))
        self.refuse(".package-lock.json")

    def test_one_byte_changed_in_a_listed_dist_file_is_refused_and_listed(self):
        f = self.pkg / "dist/automation/switch/switch.js"
        data = bytearray(f.read_bytes())
        data[-2] ^= 0x01
        f.write_bytes(bytes(data))
        self.refuse("dist/automation/switch/switch.js")

    def test_one_byte_changed_in_a_listed_non_dist_file_is_refused(self):
        f = self.pkg / "bundle/openbridge-webcomponents.bundle.js"
        f.write_bytes(f.read_bytes() + b" ")
        self.refuse("openbridge-webcomponents.bundle.js")

    def test_missing_listed_file_is_refused_and_listed(self):
        (self.pkg / "dist/automation/bus/bus.js").unlink()
        self.refuse("dist/automation/bus/bus.js")

    def test_unlisted_file_under_dist_is_refused_and_listed(self):
        (self.pkg / "dist/automation/bus/extra.js").write_bytes(b"export const x = 3;\n")
        self.refuse("dist/automation/bus/extra.js")

    def test_each_failing_path_is_listed_when_two_fail(self):
        (self.pkg / "dist/openbridge.css").write_bytes(b"body{margin:1px}\n")
        (self.pkg / "dist/automation/bus/bus.js").unlink()
        r = self.refuse("dist/openbridge.css")
        self.assertIn("dist/automation/bus/bus.js", r.stdout + r.stderr)

    @unittest.skipUnless(REAL_PKG.is_dir(), "the main checkout's installed element package is absent")
    def test_real_tree_passes_read_only(self):
        before = (REAL_PKG / "package.json").stat().st_mtime_ns
        r = subprocess.run([sys.executable, str(VERIFY), "--root", str(MAIN / "module" / "web")],
                           capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(before, (REAL_PKG / "package.json").stat().st_mtime_ns)


def declarations(manifest: dict) -> list:
    out = []
    for mod in manifest["modules"]:
        for d in mod.get("declarations", []):
            if d.get("customElement") is True and d.get("tagName"):
                out.append((mod["path"], d))
    return out


class ElementsListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read_json(ELEMENTS) if ELEMENTS.exists() else None

    def need(self):
        self.assertIsNotNone(self.doc, "module/openbridge-elements.json is absent")
        return self.doc

    def test_shape(self):
        doc = self.need()
        self.assertEqual(set(doc), {"release", "commit", "elements"})
        self.assertIsInstance(doc["release"], str)
        self.assertIsInstance(doc["elements"], list)
        for e in doc["elements"]:
            self.assertEqual(set(e), {"tag", "class", "path", "group", "status", "properties"}, e.get("tag"))
            for k in ("tag", "class", "path", "group"):
                self.assertIsInstance(e[k], str, e["tag"])
            self.assertIn(e["status"], ("stable", "beta", "experimental", "deprecated", None), e["tag"])
            for p in e["properties"]:
                self.assertEqual(set(p), {"name", "type", "enum", "default"}, e["tag"])
                self.assertIsInstance(p["name"], str)
                self.assertTrue(p["enum"] is None or (isinstance(p["enum"], list)
                                                      and all(isinstance(x, str) for x in p["enum"])))

    def test_release_names_the_pin(self):
        self.assertIn(VERSION, str(self.need()["release"]))

    def test_sorted_by_tag_and_property_name(self):
        els = self.need()["elements"]
        tags = [e["tag"] for e in els]
        self.assertEqual(tags, sorted(tags))
        self.assertEqual(len(tags), len(set(tags)))
        for e in els:
            names = [p["name"] for p in e["properties"]]
            self.assertEqual(names, sorted(names), e["tag"])

    def test_path_rule_and_group(self):
        for e in self.need()["elements"]:
            self.assertTrue(e["path"].startswith("dist/"), e["tag"])
            self.assertTrue(e["path"].endswith(".js"), e["tag"])
            self.assertNotIn("/src/", "/" + e["path"])
            self.assertEqual(e["group"], e["path"].split("/")[1], e["tag"])

    def test_named_elements_present_with_stated_paths(self):
        by = {e["tag"]: e for e in self.need()["elements"]}
        want = {"obc-switch": ("dist/automation/switch/switch.js", "stable"),
                "obc-automation-button": ("dist/automation/automation-button/automation-button.js", "stable"),
                "obc-bus": ("dist/automation/bus/bus.js", "beta"),
                "obc-button": ("dist/components/button/button.js", "stable")}
        for tag, (path, status) in want.items():
            self.assertIn(tag, by)
            self.assertEqual(by[tag]["path"], path, tag)
            self.assertEqual(by[tag]["status"], status, tag)

    @unittest.skipUnless(REAL_MANIFEST.exists(), "the pinned custom-elements.json is absent")
    def test_count_and_content_match_the_pinned_manifest(self):
        manifest = read_json(REAL_MANIFEST)
        decls = declarations(manifest)
        els = self.need()["elements"]
        self.assertEqual(len(els), len(decls))
        self.assertGreater(len(decls), 50)
        by = {e["tag"]: e for e in els}
        for path, d in decls:
            e = by.get(d["tagName"])
            self.assertIsNotNone(e, d["tagName"])
            self.assertEqual(e["class"], d["name"])
            self.assertEqual(e["path"], re.sub(r"\.ts$", ".js", path.replace("src/", "dist/", 1)))


class MapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read_json(MAP) if MAP.exists() else None

    def need(self):
        self.assertIsNotNone(self.doc, "module/openbridge-map.json is absent")
        return self.doc

    def test_top_level_keys(self):
        doc = self.need()
        self.assertEqual(set(doc), {"release", "rows", "rejected"})
        self.assertIn(VERSION, str(doc["release"]))

    def test_exactly_the_four_proposed_rows(self):
        rows = self.need()["rows"]
        self.assertEqual(len(rows), 4)
        got = {r["kind"]: r for r in rows}
        self.assertEqual(set(got), {"switch", "bus", "generator", "command-button"})
        want = {"switch": ("obc-switch", "dist/automation/switch/switch.js"),
                "bus": ("obc-bus", "dist/automation/bus/bus.js"),
                "generator": ("obc-automation-button", "dist/automation/automation-button/automation-button.js"),
                "command-button": ("obc-button", "dist/components/button/button.js")}
        for kind, (element, imp) in want.items():
            r = got[kind]
            self.assertEqual(r["element"], element, kind)
            self.assertIn(imp, r["import"], kind)
            self.assertTrue(r["import"].startswith(PKG + "/"), kind)
            if kind == "generator":   # WP-W06 builds this wrap (ruling RW-01, section 16.3): reviewed, its four states
                self.assertEqual(r["state"], "reviewed", kind)
                self.assertEqual([s["name"] for s in r["states"]], ["running", "stopped", "fault", "out_of_service"], kind)
                self.assertEqual(r["reference"], "WFBD-137", kind)
            else:
                self.assertEqual(r["state"], "proposed", kind)
                self.assertEqual(r["states"], [], kind)
            self.assertEqual(r["properties"], [], kind)
            self.assertTrue(str(r["reason"]).strip(), kind)
            for k in ("feature", "reference"):
                self.assertIn(k, r, kind)

    def test_exactly_the_three_rejected_entries(self):
        rej = self.need()["rejected"]
        self.assertEqual(len(rej), 3)
        for r in rej:
            self.assertEqual(set(r), {"kind", "element", "reason"})
            self.assertTrue(str(r["reason"]).strip())
        self.assertEqual({r["element"] for r in rej},
                         {"linear-indicator", "obc-gauge-generator", "obc-indicator-generator"})

    def test_rejected_elements_are_not_proposed(self):
        doc = self.need()
        self.assertFalse({r["element"] for r in doc["rows"]} & {r["element"] for r in doc["rejected"]})


class NoticeTests(unittest.TestCase):
    FILES = (ROOT / "NOTICE", ROOT / "module" / "gateway" / "src" / "main" / "resources" / "mounted" / "NOTICE.txt")

    def test_both_files_name_uplot_and_lit_labs_observers_with_licences(self):
        for f in self.FILES:
            text = f.read_text(encoding="utf-8")
            with self.subTest(file=f.name):
                self.assertRegex(text, r"(?i)uplot[^\n]*1\.6\.32[^\n]*\bMIT\b")
                self.assertRegex(text, r"@lit-labs/observers[^\n]*2\.1\.0[^\n]*BSD-3-Clause")


class WiringTests(unittest.TestCase):
    def test_prebuild_runs_verify_pin(self):
        scripts = read_json(ROOT / "module" / "web" / "package.json")["scripts"]
        self.assertIn("prebuild", scripts)
        self.assertIn("verify_pin", scripts["prebuild"])

    def first_statement(self, relpath: str) -> str:
        src = (ROOT / "module" / "tools" / relpath).read_text(encoding="utf-8")
        tree = ast.parse(src)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        body = list(main.body)
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            body = body[1:]
        return ast.get_source_segment(src, body[0]) or ""

    def test_gen_module_assets_main_checks_the_pin_first(self):
        self.assertIn("verify_pin", self.first_statement("gen_module_assets.py"))

    def test_build_module_main_checks_the_pin_first(self):
        self.assertIn("verify_pin", self.first_statement("build_module.py"))


if __name__ == "__main__":
    unittest.main()
