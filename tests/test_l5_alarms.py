"""Tests of eng02 ASM Level 5, alarms (COB-166): Ack selected and Ack all under each alarm list, and the banner by
page.

Run from the repository root:  python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "plants"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_asm_frame as TF  # noqa: E402  (its alarm fakes and the water plant's session; a module, so its tests do not rerun)
import test_hmi as T  # noqa: E402
from hmi import framework, navigation, screen  # noqa: E402


def nodes_of(doc):
    out = {}

    def walk(n):
        out[n.get("meta", {}).get("name")] = n
        for c in n.get("children") or []:
            walk(c)
    walk(doc["root"])
    return out


def expr(node, key):
    return node["propConfig"][key]["binding"]["config"]["expression"]


def script(node, event="onActionPerformed"):
    return node["events"]["component"][event]["config"]["script"]


class AckScriptTests(unittest.TestCase):
    Ev = T.AlarmListTests.Event

    def ns(self, events=()):
        return T.AlarmListTests("test_ack_user").hmi(events)

    def session(self, roles=("Administrator",)):
        class Auth:
            authenticated = roles is not None

            class user:
                userName = "jo"
        Auth.user.roles = list(roles or [])

        class Session:
            class props:
                auth = Auth

            class custom:
                alarmScope = "*cadre_hmi_wtp*"
                devices = []
        return Session

    def test_ids_of_rows_records_and_strings(self):
        ns, _ = self.ns()
        rows = [{"eventId": "a", "isAcked": False}, {"eventId": "b", "isAcked": True}, {"id": "c", "acknowledged": False},
                {"id": "d", "acknowledged": {"acknowledgedBy": "x"}}, "e", {"eventId": "a", "isAcked": False}, {}]
        self.assertEqual(ns["unacked_ids"](rows), ["a", "c", "e"])                 # once each, the unacknowledged only
        self.assertEqual(ns["selected_ids"](rows[:2], [{"id": "z"}, "b"]), ["a", "b", "z"])
        self.assertEqual((ns["unacked_ids"](None), ns["selected_ids"]()), ([], []))

    def test_stock_table_rows_carry_strings(self):
        # Ignition 8.3.6 (glass, 2026-10-26): the alarm status table's filters.active.results.data gives every field
        # as a string, isAcked "false" or "true"; read as a boolean, every row looked acknowledged and Ack all did nothing
        ns, _ = self.ns()
        rows = [{"eventId": "a", "isAcked": "false"}, {"eventId": "b", "isAcked": "true"},
                {"eventId": "c", "isAcked": "False"}, {"eventId": "d", "isAcked": "TRUE"}]
        self.assertEqual(ns["unacked_ids"](rows), ["a", "c"])

    def test_the_message(self):
        ns, _ = self.ns()
        self.assertEqual(ns["ack_message"]([]), "")
        self.assertEqual(ns["ack_message"](["a"]), "1 alarm could not be acknowledged")
        self.assertEqual(ns["ack_message"](["a", "b"]), "2 alarms could not be acknowledged")
        self.assertEqual(ns["ack_message"](ns["REFUSED"]), ns["REFUSED"])

    def test_the_acknowledgement_is_the_checked_one_under_the_path_given(self):
        ns, calls = self.ns([self.Ev("P502", "High", 5), self.Ev("P101", "Low", 6)])
        self.assertEqual(ns["ack_listed"](["id-P502-5"], self.session(None), "W9"), ns["REFUSED"])   # nobody signed in
        self.assertEqual([c for c in calls if c[0] == "ack"], [])
        self.assertEqual(ns["ack_listed"](["id-P502-5", "id-P101-6", "not-ours"], self.session(), "W9"), "")
        self.assertEqual(calls[-1], ("ack", ["id-P502-5", "id-P101-6"], "Acknowledged from the alarm list", "jo"))


class AckBarTests(unittest.TestCase):
    def test_the_stock_pages_and_panels_have_the_bar_under_their_table(self):
        for doc, table in ((framework.alerts_page(), "Status"), (navigation.node_alarms(), "Table"),
                           (framework.alert_menu(), "Alarms"), (framework.faceplate_alarms(), "Table")):
            n = nodes_of(doc)
            self.assertTrue({"AckBar", "AckSelected", "AckAll", "AckConfirm", "AckConfirmYes", "AckConfirmNo"} <= set(n), table)
            self.assertEqual(n[table]["props"]["filters"], {"active": {"results": {"enabled": True}}})
            self.assertEqual(doc["propConfig"]["custom.selected"]["binding"]["config"]["path"],
                             f"/root/{table}.props.selection.active.data")
            self.assertEqual(doc["propConfig"]["custom.shown"]["binding"]["config"]["path"],
                             f"/root/{table}.props.filters.active.results.data")
            self.assertEqual(expr(n["AckSelected"], "props.enabled"),
                             "{view.custom.can.W7} && len({view.custom.selected}) > 0")      # disabled while nothing is selected
            self.assertEqual(expr(n["AckAll"], "props.enabled"), "{view.custom.can.W7} && {view.custom.unacked} > 0")
            self.assertEqual(expr(n["AckConfirmYes"], "props.enabled"), "{view.custom.can.W7}")
            self.assertIn("can", doc["custom"])
            names = [c["meta"]["name"] for c in doc["root"]["children"]]
            self.assertLess(names.index(table), names.index("AckBar"))

    def test_the_alerts_page_shows_the_bar_on_its_active_tab_only(self):
        n = nodes_of(framework.alerts_page())
        self.assertEqual(expr(n["AckBar"], "position.display"), "{view.custom.tab} = 'active'")
        self.assertIn("{view.custom.tab} = 'active'", expr(n["AckConfirm"], "position.display"))

    def test_ack_all_asks_first_and_names_the_count(self):
        n = nodes_of(framework.alerts_page())
        click = script(n["AckAll"])
        self.assertIn("cadre.hmi.unacked_ids(self.view.custom.shown)", click)
        self.assertIn("'Acknowledge ' + str(len(ids))", click)
        self.assertNotIn("ack_listed", click)                              # nothing is acknowledged before Confirm
        yes = script(n["AckConfirmYes"])
        self.assertIn("ack_listed(self.view.custom.ackPending.ids, self.session, 'W7')", yes)
        self.assertIn("'active': False", yes)
        self.assertIn("'active': False", script(n["AckConfirmNo"]))
        self.assertIn("ack_listed(ids, self.session, 'W7')", script(n["AckSelected"]))

    @staticmethod
    def with_ticks(ticks):
        props = {"alerts": {}, **({"selectable": {}, "selectedIds": {}} if ticks else {})}
        module = {"cadre.ob.alertlist": {"props": dict(props)}, "cadre.ob.alertpanel": {"props": dict(props)}}
        return mock.patch.dict(screen._MODULE_SCHEMA, module, clear=True)

    def test_the_module_panels_use_w8_and_w9_and_the_ticks_when_the_module_has_them(self):
        with self.with_ticks(True):
            for doc, lists in ((framework.alert_menu_module(), ("Panel", "Rectified")),
                               (framework.faceplate_alarms_module(), ("List", "Rectified"))):
                n = nodes_of(doc)
                self.assertEqual(expr(n["AckSelected"], "props.enabled"),
                                 "{view.custom.can.W8} && len({view.custom.selected}) + len({view.custom.selectedR}) > 0")
                self.assertEqual(expr(n["AckAll"], "props.enabled"), "{view.custom.can.W9} && {view.custom.unacked} > 0")
                for name, sel in zip(lists, ("selected", "selectedR")):
                    self.assertIs(n[name]["props"]["selectable"], True)
                    b = n[name]["propConfig"]["props.selectedIds"]["binding"]["config"]
                    self.assertEqual((b["path"], b["bidirectional"]), (f"view.custom.{sel}", True))
                self.assertIn("ack_listed(ids, self.session, 'W8')", script(n["AckSelected"]))
                self.assertIn("'W9')", script(n["AckConfirmYes"]))
                self.assertEqual(doc["propConfig"]["custom.shown"]["binding"]["config"]["expression"],
                                 "{view.custom.alarms.alerts}")
                self.assertIn("can", doc["custom"])

    def test_without_the_ticks_in_the_schema_there_is_no_ack_selected_and_no_selection_prop(self):
        with self.with_ticks(False):
            for doc in (framework.alert_menu_module(), framework.faceplate_alarms_module()):
                n = nodes_of(doc)
                self.assertNotIn("AckSelected", n)
                self.assertIn("AckAll", n)
                for name in ("Panel", "List", "Rectified"):
                    if name in n:
                        self.assertNotIn("selectable", n[name]["props"])
                        self.assertNotIn("props.selectedIds", n[name].get("propConfig", {}))
                self.assertNotIn("selected", doc["custom"])


class BannerByPageTests(unittest.TestCase):
    def setUp(self):
        _, self.descs = TF.wtp_descs()
        self.Ev = T.AlarmListTests.Event

    def banner(self, route=None, content=""):
        ns, calls = TF.frame_ns([self.Ev("P301", "Low", 5), self.Ev("P101", "High", 4)])
        s = TF.session_of(self.descs, contentNode=content)
        got = ns["banner_alarms"](s) if route is None else ns["banner_alarms"](s, route)
        return got, calls

    def test_a_page_with_a_node_asks_for_its_devices_sources(self):
        _got, calls = self.banner("/filtration")
        paths = calls[0][1]
        self.assertIn("prov:default:/tag:cadre_hmi_wtp/P301/*", paths)
        self.assertNotIn("prov:default:/tag:cadre_hmi_wtp/P101/*", paths)
        self.assertNotIn("*cadre_hmi_wtp*", paths)

    def test_the_node_includes_the_nodes_beneath_it(self):
        _got, calls = self.banner("/")                    # the plant's own page: the root node, every node beneath it
        self.assertIn("prov:default:/tag:cadre_hmi_wtp/P301/*", calls[0][1])
        self.assertIn("prov:default:/tag:cadre_hmi_wtp/P101/*", calls[0][1])

    def test_a_page_without_a_node_and_a_call_without_a_route_show_the_whole_scope(self):
        for route in (None, "", "/alerts", "/component-test"):
            _got, calls = self.banner(route)
            self.assertEqual(calls[0][1], ["*cadre_hmi_wtp*"], route)

    def test_the_pivot_pages_follow_the_content_node(self):
        _g, calls = self.banner("/node/alarms", "n2")
        self.assertIn("prov:default:/tag:cadre_hmi_wtp/P301/*", calls[0][1])
        self.assertNotIn("prov:default:/tag:cadre_hmi_wtp/P101/*", calls[0][1])
        _g, calls = self.banner("/node/trend", "n3")
        self.assertIn("prov:default:/tag:cadre_hmi_wtp/P101/*", calls[0][1])
        _g, calls = self.banner("/node/alarms", "")        # the root: the whole scope
        self.assertEqual(calls[0][1], ["*cadre_hmi_wtp*"])

    def test_a_node_without_alarm_sources_shows_nothing_never_everything(self):
        s = TF.session_of(self.descs)
        s.custom.hierarchy = [dict(h, devices=[]) for h in s.custom.hierarchy]
        ns, calls = TF.frame_ns([])
        ns["banner_alarms"](s, "/intake")
        self.assertEqual(calls[0][1], [ns["NO_MATCH"]])

    def test_the_banner_binds_the_page_path(self):
        doc = navigation.alarm_banner()
        b = doc["propConfig"]["custom.banner"]["binding"]
        self.assertEqual(b["config"]["expression"], "if(toMillis(now(2000)) > 0, {page.props.path}, '')")
        self.assertIn("banner_alarms(self.session, value)", b["transforms"][0]["code"])


if __name__ == "__main__":
    unittest.main()
