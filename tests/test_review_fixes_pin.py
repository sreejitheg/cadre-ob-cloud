"""Regression tests of the cold review's findings 4 and 11 on the pin check and the bundle record (NOTE-WFB-10 section
11.1 item 3 and section 13 invariant 4):

    4   with `CADRE_OB_WEB_ROOT` set, `package.json` and `package-lock.json` are read from the checkout being built
        (the sibling `module/web` of the script) and only the `node_modules` tree from the named root
    11  the bundle build records `{lock_sha256, entry_sha256, bundle_sha256}` beside the bundle; `build_module.py`
        refuses a bundle whose record does not match the checkout's lock and entry files (or has none) and refuses
        `--allow-stale-bundle`; `gen_module_assets.py` without that option checks the record too

Fixtures only: no npm, esbuild, Gradle or gateway is run, and the installed tree of the main checkout is not read.

Run from the repository root:  python -m unittest discover -s tests
"""
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "module" / "tools"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(TOOLS))
from test_openbridge_pin import PKG, VERSION, build_root, read_json, write_json  # noqa: E402

import verify_pin  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class OtherCheckoutTests(unittest.TestCase):
    """Finding 4: a copy of the script stands for the checkout being built; `other` for the main checkout whose
    `node_modules` it reads through `CADRE_OB_WEB_ROOT`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.other, self.manifest = build_root(base / "other")
        self.web = base / "checkout" / "module" / "web"
        self.web.mkdir(parents=True)
        for name in ("package.json", "package-lock.json"):
            shutil.copyfile(self.other / name, self.web / name)
        shutil.copyfile(self.manifest, self.web / verify_pin.MANIFEST_NAME)
        (base / "checkout" / "module" / "tools").mkdir()
        self.script = base / "checkout" / "module" / "tools" / "verify_pin.py"
        shutil.copyfile(TOOLS / "verify_pin.py", self.script)

    def run_pin(self):
        env = dict(os.environ, CADRE_OB_WEB_ROOT=str(self.other))
        return subprocess.run([sys.executable, str(self.script)], capture_output=True, text=True, env=env, timeout=120)

    def test_the_honest_pair_passes(self):
        r = self.run_pin()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_version_files_of_the_other_checkout_are_not_read(self):
        # the other checkout's package.json and lock are moved off the pin: the build is unaffected by them
        d = read_json(self.other / "package.json")
        d["dependencies"][PKG] = "^2.0.0-next.156"
        write_json(self.other / "package.json", d)
        lock = read_json(self.other / "package-lock.json")
        lock["packages"][""]["dependencies"][PKG] = "2.0.0-next.156"
        lock["packages"][f"node_modules/{PKG}"]["integrity"] = "sha512-changed"
        write_json(self.other / "package-lock.json", lock)
        r = self.run_pin()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_a_package_json_of_this_checkout_off_the_pin_is_refused_whatever_the_other_one_says(self):
        d = read_json(self.web / "package.json")
        d["dependencies"][PKG] = "^" + VERSION
        write_json(self.web / "package.json", d)
        r = self.run_pin()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("package.json", r.stdout)

    def test_a_lock_of_this_checkout_off_the_pin_is_refused(self):
        lock = read_json(self.web / "package-lock.json")
        lock["packages"][f"node_modules/{PKG}"]["integrity"] = "sha512-changed"
        write_json(self.web / "package-lock.json", lock)
        r = self.run_pin()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("package-lock.json", r.stdout)

    def test_the_node_modules_tree_is_still_read_from_the_named_root(self):
        f = self.other / "node_modules" / PKG / "dist" / "openbridge.css"
        f.write_bytes(f.read_bytes() + b" ")
        r = self.run_pin()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("dist/openbridge.css", r.stdout)

    def test_an_explicit_root_still_reads_all_four_files_from_it(self):
        d = read_json(self.other / "package.json")
        d["dependencies"][PKG] = "^" + VERSION
        write_json(self.other / "package.json", d)
        r = subprocess.run([sys.executable, str(self.script), "--root", str(self.other), "--manifest",
                            str(self.manifest)], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("package.json", r.stdout)


class BundleFixture(unittest.TestCase):
    """A checkout `module/web` with a lock, an entry file and a built bundle (a fixture), in a temporary folder."""

    BUNDLE = b"/* a bundle */\n"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)
        self.web = self.make_web(self.base / "checkout")

    def make_web(self, folder: Path, lock=b'{"lock": 1}\n', entry=b"import 'x';\n", bundle=None) -> Path:
        web = folder / "module" / "web"
        (web / "dist").mkdir(parents=True)
        (web / "package-lock.json").write_bytes(lock)
        (web / "entry.js").write_bytes(entry)
        (web / "dist" / "ob-components.js").write_bytes(self.BUNDLE if bundle is None else bundle)
        return web

    def record_path(self, web: Path) -> Path:
        return web / "dist" / "ob-components.build.json"


class RecordTests(BundleFixture):
    def test_the_build_step_writes_the_record_beside_the_bundle(self):
        verify_pin.write_bundle_record(self.web)
        rec = read_json(self.record_path(self.web))
        self.assertEqual(rec, {"lock_sha256": sha(b'{"lock": 1}\n'), "entry_sha256": sha(b"import 'x';\n"),
                               "bundle_sha256": sha(self.BUNDLE)})

    def test_the_command_line_step_writes_the_same_record(self):
        r = subprocess.run([sys.executable, str(TOOLS / "verify_pin.py"), "--record-bundle", "--root", str(self.web)],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(set(read_json(self.record_path(self.web))), {"lock_sha256", "entry_sha256", "bundle_sha256"})

    def test_npm_run_build_records_the_bundle_after_esbuild(self):
        scripts = read_json(ROOT / "module" / "web" / "package.json")["scripts"]
        build = scripts["build"]
        self.assertTrue(build.startswith("esbuild "), build)
        self.assertIn("--record-bundle", build)
        self.assertLess(build.index("esbuild"), build.index("--record-bundle"))
        self.assertIn("verify_pin", scripts["prebuild"], "the pin check still runs first")

    def test_a_matching_record_passes(self):
        verify_pin.write_bundle_record(self.web)
        self.assertEqual(verify_pin.check_bundle_record(self.web, self.web), [])

    def test_a_bundle_with_no_record_is_refused(self):
        failures = verify_pin.check_bundle_record(self.web, self.web)
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("record", failures[0])

    def test_a_lock_changed_after_the_build_is_refused(self):
        verify_pin.write_bundle_record(self.web)
        (self.web / "package-lock.json").write_bytes(b'{"lock": 2}\n')
        failures = verify_pin.check_bundle_record(self.web, self.web)
        self.assertTrue(any("lock" in f for f in failures), failures)

    def test_an_entry_changed_after_the_build_is_refused(self):
        verify_pin.write_bundle_record(self.web)
        (self.web / "entry.js").write_bytes(b"import 'y';\n")
        failures = verify_pin.check_bundle_record(self.web, self.web)
        self.assertTrue(any("entry" in f for f in failures), failures)

    def test_a_bundle_changed_after_the_record_is_refused(self):
        verify_pin.write_bundle_record(self.web)
        (self.web / "dist" / "ob-components.js").write_bytes(b"/* another */\n")
        failures = verify_pin.check_bundle_record(self.web, self.web)
        self.assertTrue(any("bundle" in f for f in failures), failures)

    def test_a_record_without_a_hash_is_refused(self):
        verify_pin.write_bundle_record(self.web)
        rec = read_json(self.record_path(self.web))
        rec.pop("entry_sha256")
        write_json(self.record_path(self.web), rec)
        self.assertTrue(verify_pin.check_bundle_record(self.web, self.web))

    def test_a_record_that_is_not_json_is_refused(self):
        self.record_path(self.web).write_text("not json", encoding="utf-8")
        self.assertTrue(verify_pin.check_bundle_record(self.web, self.web))

    def test_a_bundle_built_in_another_checkout_is_judged_against_this_checkouts_lock_and_entry(self):
        other = self.make_web(self.base / "other")
        verify_pin.write_bundle_record(other)
        self.assertEqual(verify_pin.check_bundle_record(other, self.web), [], "the same lock and entry files")
        (self.web / "package-lock.json").write_bytes(b'{"lock": 3}\n')
        failures = verify_pin.check_bundle_record(other, self.web)
        self.assertTrue(any("lock" in f for f in failures), failures)

    def test_require_bundle_record_ends_the_process_listing_the_findings(self):
        with self.assertRaises(SystemExit) as caught:
            verify_pin.require_bundle_record(self.web, self.web)
        self.assertNotEqual(caught.exception.code, 0)
        verify_pin.write_bundle_record(self.web)
        verify_pin.require_bundle_record(self.web, self.web)


class BuildModuleTests(BundleFixture):
    @classmethod
    def setUpClass(cls):
        import build_module
        cls.build_module = build_module

    def test_the_stale_bundle_option_is_refused(self):
        with self.assertRaises(SystemExit) as caught:
            self.build_module.refuse_stale_bundle(["--allow-stale-bundle"])
        self.assertIn("allow-stale-bundle", str(caught.exception))

    def test_other_arguments_are_not_refused(self):
        self.build_module.refuse_stale_bundle(["--task", "build", "--jdk", "x"])

    def source_of_main(self):
        src = (TOOLS / "build_module.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        return ast.get_source_segment(src, main) or ""

    def test_main_checks_the_pin_then_refuses_the_stale_option_then_checks_the_record_before_any_build(self):
        text = self.source_of_main()
        order = [text.find(s) for s in ("require_pin", "refuse_stale_bundle", "require_bundle_record", "gradlew")]
        self.assertTrue(all(i >= 0 for i in order), order)
        self.assertEqual(order, sorted(order), order)


class GenerateAssetsTests(BundleFixture):
    @classmethod
    def setUpClass(cls):
        import gen_module_assets
        cls.gen = gen_module_assets

    def test_without_the_stale_option_an_unrecorded_bundle_is_refused(self):
        with self.assertRaises(SystemExit):
            self.gen.require_recorded_bundle(False, self.web, self.web)

    def test_without_the_stale_option_a_recorded_bundle_passes(self):
        verify_pin.write_bundle_record(self.web)
        self.gen.require_recorded_bundle(False, self.web, self.web)

    def test_the_stale_option_stays_an_offline_option_of_this_script_only(self):
        self.gen.require_recorded_bundle(True, self.web, self.web)

    def test_main_checks_the_pin_first_and_then_the_record(self):
        src = (TOOLS / "gen_module_assets.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
        text = ast.get_source_segment(src, main) or ""
        self.assertLess(text.find("require_pin"), text.find("require_recorded_bundle"))
        self.assertGreater(text.find("require_recorded_bundle"), 0)
        self.assertLess(text.find("require_recorded_bundle"), text.find("custom-elements.json"))


class MeasureDefaultsTests(BundleFixture):
    @classmethod
    def setUpClass(cls):
        import measure_defaults
        cls.measure = measure_defaults

    def package_bundle(self) -> Path:
        f = self.web / "node_modules" / PKG / "bundle" / "openbridge-webcomponents.bundle.js"
        f.parent.mkdir(parents=True)
        f.write_bytes(b"/* the package's own bundle */\n")
        return f

    def test_a_bundle_of_the_pinned_package_is_measured(self):
        self.measure.require_trusted_bundle(self.package_bundle(), self.web, self.web)

    def test_a_recorded_dist_bundle_is_measured(self):
        verify_pin.write_bundle_record(self.web)
        self.measure.require_trusted_bundle(self.web / "dist" / "ob-components.js", self.web, self.web)

    def test_an_unrecorded_dist_bundle_is_refused(self):
        with self.assertRaises(SystemExit):
            self.measure.require_trusted_bundle(self.web / "dist" / "ob-components.js", self.web, self.web)

    def test_any_other_file_is_refused(self):
        stray = self.base / "stray.js"
        stray.write_bytes(b"/* a bundle of unknown origin */\n")
        verify_pin.write_bundle_record(self.web)
        with self.assertRaises(SystemExit):
            self.measure.require_trusted_bundle(stray, self.web, self.web)


if __name__ == "__main__":
    unittest.main()
