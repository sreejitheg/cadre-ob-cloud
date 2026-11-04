"""Tests of `install_module.py --list` (COB-202): the installed modules with name, version and file digest, read only.

The parsing runs on a recorded answer of the gateway's module list (`tests/fixtures/gateway-modules-healthy.json`, read
from the local 8.3.6 gateway on 2026-10-31, vendor prose removed); the gateway's own record of the module files
(`modules.json`) and the module files are built in a temporary folder. The adjacent test puts the recorded answer behind a
local HTTP server and reads it through ctig's `Gateway` class, the client `install_module.py` installs with, and checks
that nothing but GET requests were made. No gateway is touched.

    python -m unittest tests.test_install_module_list
"""
import contextlib
import hashlib
import http.server
import io
import json
import os
import sys
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, validate  # noqa: E402

sys.path.insert(0, str(ROOT / "module" / "tools"))
import install_module  # noqa: E402
from hmi import deploy  # noqa: E402

RECORDED = (ROOT / "tests" / "fixtures" / "gateway-modules-healthy.json").read_bytes()
OURS = "cadre.hmi.ob"
ALARMS = "com.inductiveautomation.alarm-notification"
PERSPECTIVE = "com.inductiveautomation.perspective"


class FakeGateway:
    """The two things `install_module` asks of a ctig `Gateway`: `_req` and a base address. Every request is kept."""
    base = "http://gateway.test:8088"

    def __init__(self, code=200, body=RECORDED):
        self.code, self.body, self.requests = code, body, []

    def _req(self, method, path, body=None, ctype=None):
        self.requests.append((method, path))
        return self.code, self.body


def modl(path: Path, module_id: str, version: str) -> bytes:
    """A module file: a ZIP with `module.xml` (only what the tool reads)."""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("module.xml", f"<modules><module><id>{module_id}</id><name>x</name><version>{version}</version></module></modules>")
    return path.read_bytes()


class Station:
    """A gateway data folder: `modules.json` names the files, as the real gateway's does."""

    def __init__(self, root: Path, ours="0.4.2", alarms="7.3.6.2026042713", skip=()):
        self.root = root
        self.lib = root / "user-lib" / "modules"
        self.lib.mkdir(parents=True)
        self.files = {OURS: self.lib / "CadreHMIComponents.modl", ALARMS: self.lib / "Alarm Notification-module.modl"}
        self.bytes = {OURS: modl(self.files[OURS], OURS, ours), ALARMS: modl(self.files[ALARMS], ALARMS, alarms)}
        self.data = root / "data"
        self.data.mkdir()
        record = {i: {"filename": str(f), "onStartup": "enabled", "certFingerprint": "00"} for i, f in self.files.items() if i not in skip}
        (self.data / "modules.json").write_text(json.dumps(record), encoding="utf-8")


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)


class ParseTests(Case):
    def test_the_recorded_answer_lists_three_modules(self):
        items = install_module.module_items(RECORDED.decode("utf-8"))
        self.assertEqual({m["id"] for m in items}, {OURS, ALARMS, PERSPECTIVE})
        self.assertEqual(next(m for m in items if m["id"] == OURS)["version"], "0.4.2 (b0)")

    def test_a_bare_list_is_read_as_well(self):
        self.assertEqual(install_module.module_items('[{"id": "a"}, 3]'), [{"id": "a"}])

    def test_the_installs_own_state_reading_agrees_with_the_listing(self):
        """`module_state` (the install flow's check after enabling) and `--list` read the answer through one parser."""
        gw = FakeGateway()
        rows = {m["id"]: m for m in install_module.list_modules(gw)["modules"]}
        self.assertEqual(install_module.module_state(gw), rows[OURS]["state"])
        self.assertEqual(rows[OURS]["state"], "ACTIVE")

    def test_versions_agree(self):
        v = install_module.versions_agree
        self.assertTrue(v("0.4.2 (b0)", "0.4.2"))
        self.assertTrue(v("7.3.6 (b2026042713)", "7.3.6.2026042713"))
        self.assertTrue(v("0.4.2", "0.4.2"))
        self.assertFalse(v("0.4.2 (b0)", "0.3.2"))
        self.assertFalse(v("0.4.2 (b0)", "0.4"))          # a prefix of the number, not of its parts, is not an agreement
        self.assertFalse(v(None, "0.4.2"))
        self.assertFalse(v("0.4.2 (b0)", None))


class ListTests(Case):
    def test_each_module_carries_name_version_state_and_the_digest_of_its_file(self):
        station = Station(self.dir)
        gw = FakeGateway()
        doc = install_module.list_modules(gw, station.data)
        rows = {m["id"]: m for m in doc["modules"]}
        self.assertEqual(doc["schema"], "cadre-hmi-installed-modules/1")
        self.assertEqual(doc["gateway"], "http://gateway.test:8088")
        self.assertEqual(doc["modules_json"], str(station.data / "modules.json"))
        ours = rows[OURS]
        self.assertEqual((ours["name"], ours["version"], ours["state"]), ("Cadre HMI Components", "0.4.2 (b0)", "ACTIVE"))
        self.assertEqual(ours["sha256"], hashlib.sha256(station.bytes[OURS]).hexdigest())
        self.assertEqual((ours["bytes"], ours["file"], ours["file_version"], ours["file_matches_version"], ours["note"]),
                         (len(station.bytes[OURS]), str(station.files[OURS]), "0.4.2", True, None))
        self.assertTrue(rows[ALARMS]["file_matches_version"])

    def test_a_file_older_than_the_installed_version_is_said_so(self):
        """The case of a stale rollback copy: the file the gateway holds names another version than the gateway runs."""
        station = Station(self.dir, ours="0.3.2")
        ours = {m["id"]: m for m in install_module.list_modules(FakeGateway(), station.data)["modules"]}[OURS]
        self.assertEqual((ours["file_version"], ours["file_matches_version"]), ("0.3.2", False))
        self.assertEqual(ours["sha256"], hashlib.sha256(station.bytes[OURS]).hexdigest())

    def test_a_module_the_record_does_not_name_has_no_digest_and_says_why(self):
        station = Station(self.dir, skip=(ALARMS,))
        rows = {m["id"]: m for m in install_module.list_modules(FakeGateway(), station.data)["modules"]}
        self.assertIsNone(rows[ALARMS]["sha256"])
        self.assertIn("names no file", rows[ALARMS]["note"])
        self.assertIsNone(rows[PERSPECTIVE]["sha256"])               # the recorded answer has Perspective; the record does not
        self.assertIsNotNone(rows[OURS]["sha256"])

    def test_a_missing_file_is_a_row_with_a_note_not_a_fault(self):
        station = Station(self.dir)
        station.files[OURS].unlink()
        ours = {m["id"]: m for m in install_module.list_modules(FakeGateway(), station.data)["modules"]}[OURS]
        self.assertIsNone(ours["sha256"])
        self.assertEqual(ours["file"], str(station.files[OURS]))
        self.assertIn("could not be read", ours["note"])

    def test_without_the_gateways_data_folder_the_digest_is_null_and_the_note_says_why(self):
        for folder in (None, self.dir / "elsewhere"):
            rows = install_module.list_modules(FakeGateway(), folder)["modules"]
            self.assertTrue(all(m["sha256"] is None and m["note"] for m in rows))
            self.assertTrue(all(m["name"] and m["version"] for m in rows))      # name and version are still the gateway's

    def test_the_id_option_limits_the_listing(self):
        station = Station(self.dir)
        rows = install_module.list_modules(FakeGateway(), station.data, OURS)["modules"]
        self.assertEqual([m["id"] for m in rows], [OURS])

    def test_an_error_from_the_gateway_is_raised_not_listed_as_empty(self):
        with self.assertRaises(RuntimeError):
            install_module.list_modules(FakeGateway(code=500, body=b"boom"))

    def test_listing_is_one_get_and_nothing_else(self):
        gw = FakeGateway()
        install_module.list_modules(gw, Station(self.dir).data)
        self.assertEqual(gw.requests, [("GET", "/data/api/v1/modules/healthy")])

    def test_the_document_validates_against_its_schema_when_one_is_written(self):
        schema = ROOT / "schemas" / "cadre-hmi-installed-modules-1.json"
        doc = install_module.list_modules(FakeGateway(), Station(self.dir).data)
        self.assertEqual(validate(doc, schema.name), [])


class DataDirTests(Case):
    def test_the_argument_then_the_environment_then_the_cadre_gateway_file(self):
        with mock.patch.dict(os.environ, {"CADRE_IGNITION_DATA": "E:/env"}):
            self.assertEqual(install_module.data_dir_of("D:/arg"), Path("D:/arg"))
            self.assertEqual(install_module.data_dir_of(None), Path("E:/env"))
        home = self.dir / "home"
        (home / ".cadre").mkdir(parents=True)
        (home / ".cadre" / "gateway.json").write_text(json.dumps({"ignition": {"projects_dir": "C:/gw/data/projects"}}), encoding="utf-8")
        with mock.patch.dict(os.environ), mock.patch.object(Path, "home", return_value=home):
            os.environ.pop("CADRE_IGNITION_DATA", None)
            self.assertEqual(install_module.data_dir_of(None), Path("C:/gw/data"))
        with mock.patch.dict(os.environ), mock.patch.object(Path, "home", return_value=self.dir / "none"):
            os.environ.pop("CADRE_IGNITION_DATA", None)
            self.assertIsNone(install_module.data_dir_of(None))


class MainTests(Case):
    def run_main(self, *argv, gateway=None):
        out, err = io.StringIO(), io.StringIO()
        gw = gateway or FakeGateway()
        with mock.patch.object(sys, "argv", ["install_module.py", *argv]), \
                mock.patch.object(deploy, "_gateway", return_value=(gw, "test")), \
                mock.patch.object(deploy, "ensure_trial", side_effect=AssertionError("the trial was touched")), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = install_module.main()
        return code, out.getvalue(), err.getvalue(), gw

    def test_list_prints_one_json_document_and_makes_no_install_call(self):
        station = Station(self.dir)
        code, out, err, gw = self.run_main("--list", "--data-dir", str(station.data))
        self.assertEqual(code, 0, err)
        doc = json.loads(out)
        self.assertEqual({m["id"] for m in doc["modules"]}, {OURS, ALARMS, PERSPECTIVE})
        self.assertEqual({m for m, _ in gw.requests}, {"GET"})
        self.assertEqual(len(gw.requests), 1)

    def test_list_with_an_id_prints_that_module_only(self):
        station = Station(self.dir)
        code, out, err, gw = self.run_main("--list", "--id", OURS, "--data-dir", str(station.data))
        self.assertEqual([m["id"] for m in json.loads(out)["modules"]], [OURS])

    def test_a_gateway_that_is_down_exits_1_with_the_reason(self):
        class Down(FakeGateway):
            def _req(self, *a, **k):
                raise ConnectionError("refused")

        code, out, err, _ = self.run_main("--list", gateway=Down())
        self.assertEqual((code, out), (1, ""))
        self.assertIn("refused", err)

    def test_the_options_are_added_to_the_installer_not_replacing_it(self):
        with mock.patch.object(sys, "argv", ["install_module.py", "--help"]), contextlib.redirect_stdout(io.StringIO()) as h:
            with self.assertRaises(SystemExit):
                install_module.main()
        self.assertIn("--file", h.getvalue())
        self.assertIn("--list", h.getvalue())


class RecordedGatewayHandler(http.server.BaseHTTPRequestHandler):
    seen: list = []

    def log_message(self, *a):
        pass

    def _answer(self):
        type(self).seen.append((self.command, self.path))
        body = RECORDED if self.path.startswith("/data/api/v1/modules/healthy") else b"{}"
        code = 200 if self.path.startswith("/data/api/v1/modules/healthy") else 404
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = do_PUT = do_DELETE = _answer


class ThroughTheInstallersClientTests(Case):
    """Adjacent integration: `--list` through ctig's `Gateway`, the client the installer uses, over real HTTP."""

    @classmethod
    def setUpClass(cls):
        if str(deploy.CTIG_SRC) not in sys.path:
            sys.path.insert(0, str(deploy.CTIG_SRC))
        try:
            from ctig.gateway.rest import Gateway  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("ctig is not importable here") from None
        RecordedGatewayHandler.seen = []
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), RecordedGatewayHandler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_the_listing_reads_the_recorded_answer_over_http_with_get_requests_only(self):
        from ctig.gateway.rest import Gateway
        station = Station(self.dir)
        gw = Gateway(self.url, "test-token")
        RecordedGatewayHandler.seen.clear()
        with mock.patch.object(sys, "argv", ["install_module.py", "--list", "--data-dir", str(station.data)]), \
                mock.patch.object(deploy, "_gateway", return_value=(gw, "test")), contextlib.redirect_stdout(io.StringIO()) as out:
            code = install_module.main()
        doc = json.loads(out.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(RecordedGatewayHandler.seen, [("GET", "/data/api/v1/modules/healthy")])
        ours = next(m for m in doc["modules"] if m["id"] == OURS)
        self.assertEqual((ours["version"], ours["sha256"]), ("0.4.2 (b0)", hashlib.sha256(station.bytes[OURS]).hexdigest()))
        self.assertEqual(doc["gateway"], self.url)
        self.assertEqual(install_module.module_state(gw), "ACTIVE")      # the installer's own read of the same answer


if __name__ == "__main__":
    unittest.main()
