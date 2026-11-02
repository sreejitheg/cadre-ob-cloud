"""Tests of `tools/compare/alarm_probe.py` (S11-C, COB-200): the plan and the dry run offline; the four-state chain per
priority rank on the fake client page (`tests/glass_fake.py`) in headless Chromium when Playwright is importable
(ctig's `.venv`). Synthetic names only.

    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe -m unittest tests.test_alarm_probe
"""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, validate  # noqa: E402

sys.path.insert(0, str(ROOT / "tools" / "compare"))
import alarm_probe  # noqa: E402
import glass_gates  # noqa: E402
from test_glass_gates_plan import PROJECT, make  # noqa: E402

try:
    import playwright.sync_api  # noqa: F401
    HAVE_BROWSER = True
except ImportError:
    HAVE_BROWSER = False

AU, AA, CU, CA = alarm_probe.AU, alarm_probe.AA, alarm_probe.CU, alarm_probe.CA
BASE = "http://localhost:8088/data/perspective/client/" + PROJECT
SCHEMA_FILE = "cadre-hmi-alarm-probe-1.json"


class Fixture:
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.model, cls.bridge = make(cls.dir)
        cls.descs = glass_gates.descriptors_of(cls.bridge)
        login = cls.dir / "login.properties"
        login.write_text("user=tester\npassword=not-a-real-secret\n", encoding="utf-8")
        cls.login = str(login)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def argv(self, out, base=BASE, *extra, model=None):
        return ["--base", base, "--model", str(model or self.dir / "model" / "model.json"), "--build", str(self.bridge),
                "--window", "1280x800", "--out", str(out), *extra]

    def no_boolean_model(self) -> Path:
        """The model with every alarm on an expression, none on one Boolean source tag."""
        model = copy.deepcopy(self.model)
        for a in model["alarms"]:
            a["source"] = "LEVEL_A < 3"
        path = self.dir / "nobool" / "model.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(model), encoding="utf-8")
        return path


class ClassifyTests(unittest.TestCase):
    def test_the_four_states_by_the_words_of_the_stock_table(self):
        c = alarm_probe.classify
        self.assertEqual(c("Pump 1 failed Active, Unacknowledged 12:01"), AU)
        self.assertEqual(c("Pump 1 failed Active, Acknowledged 12:01"), AA)
        self.assertEqual(c("Pump 1 failed Cleared, Unacknowledged 12:01"), CU)
        self.assertEqual(c("Pump 1 failed Cleared, Acknowledged 12:01"), CA)

    def test_a_row_without_state_words_and_no_row_name_no_state(self):
        self.assertIsNone(alarm_probe.classify("Pump 1 failed 12:01"))
        self.assertIsNone(alarm_probe.classify(None))
        self.assertIsNone(alarm_probe.classify(""))


class PlanTests(Fixture, unittest.TestCase):
    def plan(self, priorities=None):
        return alarm_probe.probe_plan(self.model, self.descs, "http://x/y", (1280, 800), priorities)

    def test_the_plan_is_one_alarm_a_page_that_shows_it_and_a_page_that_does_not(self):
        plan = self.plan()
        self.assertEqual(plan["alarm"]["tag"], "[default]cadre_hmi_plant/src/PUMP01_IFAIL")
        self.assertEqual(plan["page"], "/pumpstation")
        self.assertNotEqual(plan["other"], plan["page"])
        self.assertNotIn("password", json.dumps(plan).lower())
        self.assertEqual([r["rank"] for r in plan["ranks"]], ["high"])      # without --priority: the first alarm's rank

    def test_the_plan_includes_the_acknowledgement_and_the_two_passes_that_walk_the_four_states(self):
        plan = self.plan()
        self.assertEqual(plan["ack"]["buttons"], ["Ack selected", "Ack all", "Confirm"])
        self.assertEqual(plan["states"], [AU, AA, CU, CA])
        self.assertEqual([(p["name"], p["order"]) for p in plan["passes"]],
                         [("acked_then_cleared", ["raise", "ack", "clear"]), ("cleared_then_acked", ["raise", "clear", "ack"])])
        second = plan["passes"][1]["order"]
        self.assertLess(second.index("clear"), second.index("ack"))        # the second pass clears first: Cleared and Unacked

    def test_every_rank_of_the_model_is_planned_with_its_own_alarm_and_a_rank_without_a_boolean_source_is_skipped(self):
        plan = self.plan("all")
        by = {r["rank"]: r for r in plan["ranks"]}
        self.assertEqual([r["rank"] for r in plan["ranks"]], ["high", "medium", "low", "diagnostic"])   # most severe first
        self.assertEqual({k: v["alarm"]["tag"].rsplit("/", 1)[-1] for k, v in by.items() if "alarm" in v},
                         {"high": "PUMP01_IFAIL", "medium": "PUMP01_ITRIP", "low": "TANK01_HIGH"})
        self.assertIn("Boolean", by["diagnostic"]["skipped"])
        self.assertNotIn("alarm", by["diagnostic"])
        for r in plan["ranks"]:
            if "alarm" in r:
                self.assertIn(r["page"], [p["route"] for p in self.model["pages"]])
        self.assertIsNone(plan["skipped"])

    def test_a_list_of_ranks_limits_the_plan_and_an_unknown_rank_is_a_fault(self):
        self.assertEqual([r["rank"] for r in self.plan(["low", "High"])["ranks"]], ["low", "high"])
        with self.assertRaises(glass_gates.Fault):
            self.plan(["urgent"])

    def test_a_model_with_no_boolean_alarm_gives_a_skipped_plan_not_a_fault(self):
        model = json.loads(self.no_boolean_model().read_text(encoding="utf-8"))
        plan = alarm_probe.probe_plan(model, self.descs, "http://x/y", (1280, 800), "all")
        self.assertIn("no alarm on a Boolean source tag", plan["skipped"])
        self.assertIsNone(plan["alarm"])
        self.assertTrue(all("skipped" in r for r in plan["ranks"]))


class MainTests(Fixture, unittest.TestCase):
    def test_a_dry_run_writes_the_plan_and_touches_nothing(self):
        out = self.dir / "dry"
        with mock.patch("builtins.print"):
            code = alarm_probe.main(self.argv(out, BASE, "--dry-run"))
        self.assertEqual(code, 0)
        doc = json.loads((out / "probe.json").read_text(encoding="utf-8"))
        self.assertTrue(doc["dry_run"])
        self.assertEqual((doc["steps"], doc["rows"], doc["ranks"]), ([], [], []))
        self.assertEqual(json.loads((out / "plan.json").read_text(encoding="utf-8")), doc["plan"])
        self.assertFalse((out / "pictures").exists())
        self.assertEqual(validate(doc, SCHEMA_FILE), [])

    def test_a_dry_run_with_priority_plans_every_rank(self):
        out = self.dir / "dry_all"
        with mock.patch("builtins.print") as pr:
            code = alarm_probe.main(self.argv(out, BASE, "--dry-run", "--priority"))
        self.assertEqual(code, 0)
        doc = json.loads((out / "probe.json").read_text(encoding="utf-8"))
        self.assertEqual([r["rank"] for r in doc["plan"]["ranks"]], ["high", "medium", "low", "diagnostic"])
        self.assertIn("3 rank(s)", " ".join(str(c) for c in pr.call_args_list))
        self.assertEqual(validate(doc, SCHEMA_FILE), [])

    def test_a_model_without_a_boolean_alarm_is_skipped_with_exit_0_and_no_gateway_is_touched(self):
        out = self.dir / "skipped"
        deploy = mock.Mock(side_effect=AssertionError("the gateway was touched"))
        with mock.patch("builtins.print"):
            code = alarm_probe.main(self.argv(out, BASE, "--priority", model=self.no_boolean_model()), deploy=deploy)
        self.assertEqual(code, 0)
        doc = json.loads((out / "probe.json").read_text(encoding="utf-8"))
        self.assertIn("Boolean", doc["skipped"])
        self.assertEqual((doc["dry_run"], doc["steps"], doc["rows"], doc["restored"]), (False, [], [], True))
        self.assertEqual(validate(doc, SCHEMA_FILE), [])
        deploy.assert_not_called()

    def test_faults_exit_1_before_anything_is_written(self):
        out = self.dir / "fault"
        with mock.patch("builtins.print"):
            self.assertEqual(alarm_probe.main(self.argv(out, "ftp://h/x")), 1)
            self.assertEqual(alarm_probe.main(self.argv(out) + ["--window", "big"]), 1)
            self.assertEqual(alarm_probe.main(self.argv(out) + ["--allowed-root", "[default]somewhere_else"]), 1)
            self.assertEqual(alarm_probe.main(self.argv(out) + ["--priority", "urgent"]), 1)
        self.assertFalse((out / "plan.json").exists())


@unittest.skipUnless(HAVE_BROWSER, "Playwright is not importable here; run under ctig's .venv")
class ProbeOnTheFakePageTests(Fixture, unittest.TestCase):
    def gateway(self, shows=None):
        from glass_fake import FakeGateway
        from test_glass_gates_plan import FakeGatewayTests
        helper = FakeGatewayTests("run_gates")
        helper.model, helper.descs, helper.dir, helper.bridge = self.model, self.descs, self.dir, self.bridge
        return FakeGateway(helper.config(shows))

    def run_probe(self, *extra, shows=None, fail_restore=False, ignore_ack=False, login=False):
        from glass_fake import FakeDeploy
        out = self.dir / f"probe{len(list(self.dir.glob('probe*')))}"
        with self.gateway(shows) as gw:
            gw.ignore_ack = ignore_ack
            fd = FakeDeploy(gw, {a["source"]: False for a in gw.config["alarms"]}, fail_restore=fail_restore)
            env = {"CADRE_TEST_LOGIN": self.login} if login else {}
            with mock.patch.dict(os.environ, env), mock.patch("builtins.print"):
                if not login:
                    os.environ.pop("CADRE_TEST_LOGIN", None)
                code = alarm_probe.main(self.argv(out, gw.base, "--settle", "0.04", *extra), deploy=fd)
        return code, out, gw

    def doc(self, out):
        return json.loads((out / "probe.json").read_text(encoding="utf-8"))

    def test_one_rank_walks_the_four_states_in_two_passes_and_the_tag_is_put_back(self):
        code, out, gw = self.run_probe()
        doc = self.doc(out)
        self.assertEqual(code, 0, json.dumps([s for s in doc["steps"] if not s["ok"]]))
        tag = doc["plan"]["alarm"]["tag"]
        self.assertEqual([v for t, v in gw.writes if t == tag], [True, False, True, False, False])   # 2 raises, 2 clears, restored
        self.assertTrue(doc["restored"])
        self.assertEqual(doc["ranks"], [{"rank": "high", "alarm": doc["plan"]["alarm"]["alarm"], "tag": tag,
                                         "states": {AU: True, AA: True, CU: True, CA: True}, "ok": True}])
        self.assertEqual([(r["state"], r["pass"], r["ok"]) for r in doc["rows"]],
                         [(AU, "acked_then_cleared", True), (AA, "acked_then_cleared", True), (CA, "acked_then_cleared", True),
                          (AU, "cleared_then_acked", True), (CU, "cleared_then_acked", True), (CA, "cleared_then_acked", True)])
        row = {(r["state"], r["pass"]): r for r in doc["rows"]}
        self.assertIn("Cleared, Unacknowledged", row[(CU, "cleared_then_acked")]["observed"])   # read from the alert list
        self.assertIn("Active, Acknowledged", row[(AA, "acked_then_cleared")]["observed"])
        self.assertEqual(row[(CA, "acked_then_cleared")]["observed"], "absent")                  # a cleared, acked event leaves
        self.assertEqual(validate(doc, SCHEMA_FILE), [])

    def test_priority_runs_once_per_rank_and_skips_the_rank_without_a_boolean_source(self):
        code, out, gw = self.run_probe("--priority")
        doc = self.doc(out)
        self.assertEqual(code, 0, json.dumps([s for s in doc["steps"] if not s["ok"]]))
        ranked = {r["rank"]: r for r in doc["ranks"]}
        self.assertEqual(list(ranked), ["high", "medium", "low", "diagnostic"])
        for rank in ("high", "medium", "low"):
            self.assertEqual(ranked[rank]["states"], {AU: True, AA: True, CU: True, CA: True}, rank)
            self.assertEqual(len([r for r in doc["rows"] if r["rank"] == rank]), 6)
        self.assertIn("Boolean", ranked["diagnostic"]["skipped"])
        self.assertEqual({r["rank"] for r in doc["rows"]}, {"high", "medium", "low"})
        for a in doc["plan"]["ranks"]:
            if "alarm" in a:
                self.assertFalse(gw.tags[a["alarm"]["tag"]])      # every tag is back
        self.assertEqual(validate(doc, SCHEMA_FILE), [])

    def test_the_acknowledgement_signs_in_when_the_test_login_is_named_and_the_login_is_never_written(self):
        code, out, gw = self.run_probe(login=True)
        doc = self.doc(out)
        self.assertEqual(code, 0, json.dumps([s for s in doc["steps"] if not s["ok"]]))
        self.assertTrue(any(s["action"] == "sign in with the test login" and s["ok"] for s in doc["steps"]))
        for f in out.rglob("*.json"):
            text = f.read_text(encoding="utf-8")
            self.assertNotIn("not-a-real-secret", text)
            self.assertNotIn("tester", text)

    def test_a_gateway_whose_acknowledgement_does_nothing_fails_the_probe_and_the_tag_is_still_put_back(self):
        code, out, gw = self.run_probe(ignore_ack=True)
        doc = self.doc(out)
        self.assertEqual(code, 2)
        self.assertTrue(doc["restored"])
        failed = {(r["state"], r["pass"]) for r in doc["rows"] if not r["ok"]}
        self.assertIn((AA, "acked_then_cleared"), failed)
        self.assertFalse(doc["ranks"][0]["ok"])
        self.assertFalse(doc["ranks"][0]["states"][AA])

    def test_a_banner_that_does_not_list_the_alarm_fails_the_probe_and_the_tag_is_still_put_back(self):
        code, out, gw = self.run_probe(shows=[])
        doc = self.doc(out)
        self.assertEqual(code, 2)
        self.assertTrue(doc["restored"])
        self.assertFalse(gw.tags[doc["plan"]["alarm"]["tag"]])

    def test_a_failed_restore_is_reported_and_exits_2(self):
        code, out, gw = self.run_probe(fail_restore=True)
        self.assertEqual(code, 2)
        self.assertFalse(self.doc(out)["restored"])

    def test_the_probe_and_the_glass_gates_share_one_gateway_without_disturbing_each_other(self):
        """Adjacent integration: the probe leaves the tags and the alert list as the glass gates' alarm, ack and banner
        gates expect them, and those gates pass on the same fake gateway straight after the probe."""
        from glass_fake import FakeDeploy
        with self.gateway() as gw:
            fd = FakeDeploy(gw, {a["source"]: False for a in gw.config["alarms"]})
            with mock.patch.dict(os.environ, {"CADRE_TEST_LOGIN": self.login}), mock.patch("builtins.print"):
                first = alarm_probe.main(self.argv(self.dir / "adj_probe", gw.base, "--settle", "0.04", "--priority"), deploy=fd)
                second = glass_gates.main(["--base", gw.base, "--model", str(self.dir / "model" / "model.json"),
                                           "--build", str(self.bridge), "--window", "1280x800", "--settle", "0.04",
                                           "--raise-alarm", "--gates", "alarm,ack,banner", "--out", str(self.dir / "adj_gates")],
                                          deploy=fd)
        gates = json.loads((self.dir / "adj_gates" / "gates.json").read_text(encoding="utf-8"))
        self.assertEqual((first, second), (0, 0), json.dumps([s for g in gates["gates"] for s in g["steps"] if not s["ok"]])[:1500])
        self.assertEqual([g["name"] for g in gates["gates"]], ["alarm", "ack", "banner"])
        self.assertTrue(all(g["steps"] and g["ok"] for g in gates["gates"]))


if __name__ == "__main__":
    unittest.main()
