"""Tests of the OpenBridge variant of the new frame (`screen.py --frame ob`, tranche T2 batch F6a): its views against the
registry (gate G1), the generator's facts the glass will rely on (in the pattern of `TopBarPathTests`), the event scripts
(each cites the measured event shape and calls the library's own function), the option and its refusal under the stock
rendering, and the two older frames left as they were.

Run from the repository root:  python -m unittest discover -s tests
"""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "plants"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_asm_frame as A  # noqa: E402  (its fakes and helpers; imported as a module so its tests do not rerun here)
from hmi import gates, navigation, obframe, parent as par, screen  # noqa: E402

COMPONENTS = json.loads((ROOT / "module" / "components.json").read_text(encoding="utf-8"))
OB_VIEWS = ("Framework/OB/Head", "Framework/OB/NavDock", "Framework/OB/AlertMenu", "Framework/OB/UserMenu",
            "Framework/OB/Brilliance")
# the event of each module component the frame wires, with what its script must call (the library's own function)
WIRED = {
    ("Framework/OB/Head", "TopBar", "onMenuButtonClick"): "system.perspective.openDock(id='nav')",
    ("Framework/OB/Head", "TopBar", "onAlertClick"): "'alertMenu', 'Framework/OB/AlertMenu'",
    ("Framework/OB/Head", "TopBar", "onDimmingButtonClick"): "'brilliance', 'Framework/OB/Brilliance'",
    ("Framework/OB/Head", "TopBar", "onUserButtonClick"): "'userMenu', 'Framework/OB/UserMenu'",
    ("Framework/OB/NavDock", "Menu", "onItemClick"): "system.perspective.navigate(event.id)",
    ("Framework/OB/AlertMenu", "Menu", "onAckClick"): "cadre.hmi.ack_listed([event.id], self.session, 'W8')",
    ("Framework/OB/AlertMenu", "Menu", "onAckAllClick"): "cadre.hmi.ack_event(event, self.session, path='W9')",
    ("Framework/OB/AlertMenu", "Menu", "onItemClick"): "cadre.hmi.select_alarm_device(self.session, rows[0])",
    ("Framework/OB/AlertMenu", "Menu", "onGoToAlertListClick"): "system.perspective.navigate('/alerts')",
    ("Framework/OB/UserMenu", "Menu", "onSignInClick"): "system.perspective.login()",
    ("Framework/OB/UserMenu", "Menu", "onSignOutClick"): "system.perspective.logout()",
    ("Framework/OB/Brilliance", "Menu", "onPaletteChanged"): "cadre.hmi.set_palette(self.session, event.value)",
}


def names(node):
    return [c["meta"]["name"] for c in node["children"]]


class ObViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.views = obframe.views()

    def test_the_parent_carries_the_five_views_and_the_registry_passes_them(self):
        self.assertEqual(tuple(sorted(self.views)), tuple(sorted(OB_VIEWS)))
        prj, contracts = par.build_parent()
        for v in OB_VIEWS:
            self.assertIn(v, contracts)
            self.assertEqual(contracts[v]["kind"], "framework")
        with tempfile.TemporaryDirectory() as d:
            out = prj.write(Path(d))
            g1 = gates.g1_registry(out)
        self.assertTrue(g1["ok"], g1["summary"])
        self.assertIn("cadre.ob.topbar", g1["module_components"])   # the registry knows the module's components

    def test_every_property_and_event_of_a_module_component_is_one_the_module_declares(self):
        for path, doc in self.views.items():
            for n, _ in gates.walk(doc["root"]):
                if not n["type"].startswith("cadre.ob."):
                    continue
                spec = COMPONENTS[n["type"]]
                props = set(spec["props"])
                keys = set(n.get("props", {})) | {k.split(".", 1)[1] for k in n.get("propConfig", {}) if k.startswith("props.")}
                self.assertEqual(sorted(keys - props), [], f"{path} {n['meta']['name']}")
                for group in (n.get("events") or {}).values():
                    for ev in group:
                        self.assertIn(ev, spec["events"], f"{path} {n['meta']['name']} {ev}")

    def test_the_head_is_the_one_top_dock_the_bar_over_the_strip(self):
        """The glass finds the bar by its place in the head (F7 builds its locators from these facts), and the dock is the
        height of its two rows (GF-90: the gateway draws one top dock)."""
        head = self.views["Framework/OB/Head"]
        self.assertEqual(names(head["root"]), ["TopBar", "Strip"])
        bar, strip = head["root"]["children"]
        self.assertEqual(bar["type"], "cadre.ob.topbar")
        self.assertEqual(names(strip), ["Crumbs", "Spacer", "AlertMessage"])
        self.assertEqual(bar["position"]["basis"], f"{obframe.TOP_BAR_HEIGHT}px")
        self.assertEqual(strip["position"]["basis"], f"{obframe.STRIP_HEIGHT}px")
        self.assertEqual(COMPONENTS["cadre.ob.topbar"]["defaultSize"]["height"], obframe.TOP_BAR_HEIGHT)   # measured, F4
        self.assertEqual(head["props"]["defaultSize"]["height"], obframe.HEAD_HEIGHT)
        self.assertEqual(obframe.shared_docks("A")["top"][0]["size"], obframe.HEAD_HEIGHT)
        self.assertEqual(len(obframe.shared_docks("A")["top"]), 1)
        self.assertEqual(f'[data-component-path="T[0].0:{names(head["root"]).index("TopBar")}"]',
                         '[data-component-path="T[0].0:0"]')

    def test_the_strip_keeps_the_cadre_crumb_and_the_cadre_alert_message(self):
        """Owner's answers 2 and 3: the Cadre crumb with its badges, and the alert message with its ACK (W6)."""
        strip = self.views["Framework/OB/Head"]["root"]["children"][1]
        crumbs, _, message = strip["children"]
        self.assertEqual(crumbs["props"]["path"], "Framework/Crumb")
        ack = next(c for c in message["children"] if c["meta"]["name"] == "Ack")
        self.assertEqual(ack["propConfig"]["props.enabled"]["binding"]["config"]["expression"], "{view.custom.can.W6}")
        self.assertIn("cadre.hmi.ack_top(", ack["events"]["component"]["onActionPerformed"]["config"]["script"])
        head = self.views["Framework/OB/Head"]
        for key in ("custom.alarm", "custom.can", "custom.crumbs"):
            self.assertIn(key, head["propConfig"])

    def test_the_bar_is_bound_to_the_alarm_summary_the_page_and_the_gateways_time(self):
        bar = self.views["Framework/OB/Head"]["root"]["children"][0]
        cfg = bar["propConfig"]
        expr = lambda k: cfg[f"props.{k}"]["binding"]["config"]["expression"]   # noqa: E731
        self.assertEqual(expr("nAlerts"), "{view.custom.alarm.count}")
        self.assertEqual(expr("blinking"), "{view.custom.alarm.unacked} > 0")
        self.assertEqual(expr("appTitle"), "{view.params.appName}")
        self.assertIn("now(1000)", expr("date"))
        self.assertIn("page_title", cfg["props.pageName"]["binding"]["transforms"][0]["code"])
        # wiki 13 section 11.1: Diagnostic has no alert colour, the rest follow `ALERT_TYPE`
        want = "case({view.custom.alarm.highest}, 'Critical', 'level-critical', 'High', 'level-high', 'Medium', " \
               "'level-medium', 'Low', 'level-low', '')"
        self.assertEqual(expr("alertType"), want)
        for level in {"level-critical", "level-high", "level-medium", "level-low"}:
            self.assertIn(level, COMPONENTS["cadre.ob.topbar"]["props"]["alertType"]["enum"])

    def test_the_silence_control_and_the_command_text_are_left_as_the_owner_decided(self):
        bar = self.views["Framework/OB/Head"]["root"]["children"][0]
        shown = set(bar["props"]) | {k.split(".", 1)[1] for k in bar["propConfig"]}
        self.assertNotIn("showSilenceButton", shown)            # the module's default is false (owner's answer 4)
        self.assertFalse(COMPONENTS["cadre.ob.topbar"]["props"]["showSilenceButton"]["default"])
        self.assertNotIn("commandButtonText", shown)            # empty: the F4 run-on "Engine roomCommand" cannot recur
        self.assertEqual(COMPONENTS["cadre.ob.topbar"]["props"]["commandButtonText"]["default"], "")
        self.assertNotIn("onSilenceClick", bar["events"]["component"])
        alert = self.views["Framework/OB/AlertMenu"]
        self.assertFalse(COMPONENTS["cadre.ob.alertmenu"]["props"]["showSilenceButton"]["default"])
        self.assertNotIn("onSilenceClick", alert["root"]["children"][0]["events"]["component"])

    def test_the_navigation_menu_takes_the_projects_navigation_through_ob_items(self):
        menu = self.views["Framework/OB/NavDock"]["root"]["children"][1]
        self.assertEqual(menu["type"], "cadre.ob.navigationmenu")
        items = menu["propConfig"]["props.items"]["binding"]
        footer = menu["propConfig"]["props.footerItems"]["binding"]
        self.assertIn("{page.props.path}", items["config"]["expression"])         # the open page is checked
        self.assertIn("cadre.hmi.ob_items('nav', cadre.hmi.nav_items(self.session), value, ", items["transforms"][0]["code"])
        self.assertIn("list(self.session.custom.nav['footer'])", footer["transforms"][0]["code"])
        icons = obframe.nav_icons()                                              # from the module's own enumeration
        self.assertEqual(icons, [n for n in COMPONENTS["cadre.ob.navigationitem"]["props"]["iconName"]["enum"] if n])
        self.assertIn(repr(icons), items["transforms"][0]["code"])
        self.assertIn("dashboard", icons)
        header = self.views["Framework/OB/NavDock"]["root"]["children"][0]
        self.assertIn("closeDock('nav')", header["children"][1]["events"]["dom"]["onClick"]["config"]["script"])

    def test_every_wired_event_cites_the_measured_shape_and_calls_the_existing_function(self):
        seen = set()
        for path, doc in self.views.items():
            for node, ev, code in A.handler_scripts(doc):
                if not node.startswith(("Menu", "TopBar")):
                    continue
                seen.add((path, node, ev))
                first = code.strip().splitlines()[0].strip()
                self.assertTrue(first.startswith("# GF-37"), f"{path} {ev}: {first}")
                self.assertIn(WIRED[(path, node, ev)], code, f"{path} {ev}")
                compile("def f(self, event):\n" + code + "\n", f"{path}/{ev}", "exec")
        self.assertEqual(seen, set(WIRED))

    def test_the_acknowledgements_are_the_default_frames_paths_with_its_confirm_row(self):
        alert = self.views["Framework/OB/AlertMenu"]
        kids = alert["root"]["children"]
        self.assertEqual(names(alert["root"]), ["Menu", "AckBar", "AckConfirm"])
        self.assertEqual(kids[0]["propConfig"]["props.canAckAll"]["binding"]["config"]["expression"], "{view.custom.can.W9}")
        ids = {n["meta"]["name"]: n for n, _ in gates.walk(alert["root"]) if "meta" in n}
        self.assertNotIn("AckSelected", ids)                    # the menu has no selection
        self.assertIn("{view.custom.can.W9}", ids["AckAll"]["propConfig"]["props.enabled"]["binding"]["config"]["expression"])
        yes = ids["AckConfirmYes"]["events"]["component"]["onActionPerformed"]["config"]["script"]
        self.assertIn("cadre.hmi.ack_listed(", yes)
        self.assertIn("'W9'", yes)
        self.assertIn("allowed(self.session, 'W8')", alert["propConfig"]["custom.alarms"]["binding"]["transforms"][0]["code"])

    def test_no_credential_is_a_property_or_a_binding_of_the_user_menu(self):
        user = self.views["Framework/OB/UserMenu"]
        text = json.dumps(user).lower()
        self.assertNotIn("password", text)
        self.assertNotIn("username", text.replace("session.props.auth.user.username", ""))
        menu = user["root"]["children"][0]
        self.assertEqual(sorted(menu["propConfig"]),
                         ["props.type", "props.userInitials", "props.userLabel", "props.userRole"])
        for k in menu["propConfig"]:
            self.assertIn(k.split(".", 1)[1], COMPONENTS["cadre.ob.usermenu"]["props"])
        self.assertNotIn("password", COMPONENTS["cadre.ob.usermenu"]["props"])

    def test_the_brilliance_menu_follows_the_palette_and_hides_the_brightness(self):
        menu = self.views["Framework/OB/Brilliance"]["root"]["children"][0]
        self.assertIs(menu["props"]["showBrightness"], False)    # Cadre has no brightness function
        self.assertEqual(menu["propConfig"]["props.palette"]["binding"]["config"]["expression"],
                         "coalesce({session.custom.palette}, 'day')")
        code = menu["events"]["component"]["onPaletteChanged"]["config"]["script"]
        self.assertIn("if event.value in ('day', 'bright', 'dusk', 'night'):", code)   # the keys of PALETTE_THEME


class ObOptionTests(unittest.TestCase):
    def build(self, frame, render="module"):
        _, descs = A.wtp_descs()
        return screen.build_child("cadre_hmi_wtpobf", descs, "Village WTP", "*cadre_hmi_wtpobf*", render, frame=frame)

    def files(self, child):
        return {k: v.decode("utf-8") for k, v in child.files.items() if k.endswith(".json")}

    def test_the_option_is_the_third_frame_and_the_first_two_keep_their_names(self):
        self.assertEqual(navigation.FRAMES, ("openbridge", "asm", "ob"))

    def test_a_child_with_the_option_has_the_obframes_docks_and_session(self):
        child, _ = self.build("ob")
        files = self.files(child)
        pc = json.loads(next(v for k, v in files.items() if k.endswith("page-config/config.json")))
        top, left, right = pc["sharedDocks"]["top"], pc["sharedDocks"]["left"], pc["sharedDocks"]["right"]
        self.assertEqual([(d["viewPath"], d["size"], d["show"]) for d in top], [("Framework/OB/Head", 84, "visible")])
        self.assertEqual([(d["id"], d["viewPath"], d["modal"], d["size"]) for d in left], [("nav", "Framework/OB/NavDock", True, 320)])
        self.assertEqual(right[0]["viewPath"], "Framework/SideMenu")        # the faceplate dock is not frame chrome
        self.assertEqual(top[0]["viewParams"], {"appName": "Village WTP", "showUser": True})
        self.assertIn("/alerts", pc["pages"])
        sp = json.loads(next(v for k, v in files.items() if k.endswith("session-props/props.json")))
        self.assertEqual(sp["custom"]["frame"], "ob")
        self.assertEqual(sp["custom"]["nav"]["footer"][0]["path"], "/alerts")
        self.assertIn("alarmScope", sp["custom"])

    def test_the_two_older_frames_are_as_they_were(self):
        for frame, top in (("openbridge", ("Framework/TopBar", 48)), ("asm", ("Framework/ASM/Head", 84))):
            child, _ = self.build(frame)
            files = self.files(child)
            text = "\n".join(files.values())
            self.assertNotIn("Framework/OB", text, frame)
            self.assertNotIn("cadre.ob.topbar", text, frame)
            self.assertNotIn("ob_items", text, frame)
            pc = json.loads(next(v for k, v in files.items() if k.endswith("page-config/config.json")))
            self.assertEqual([(d["viewPath"], d["size"]) for d in pc["sharedDocks"]["top"]], [top], frame)
            sp = json.loads(next(v for k, v in files.items() if k.endswith("session-props/props.json")))
            self.assertEqual(sp["custom"]["frame"], frame)

    def test_a_stock_build_with_the_option_stops_with_a_clear_error(self):
        with self.assertRaises(ValueError) as cm:
            self.build("ob", render="stock")
        self.assertIn("--frame ob", str(cm.exception))
        self.assertIn("--render module", str(cm.exception))
        argv = ["screen.py", "--project", "cadre_hmi_x", "--descriptor", str(ROOT / "screens" / "wtp" / "overview.json"),
                "--frame", "ob", "--out", tempfile.gettempdir()]
        out = io.StringIO()
        with mock.patch.object(sys, "argv", argv), redirect_stdout(out):
            code = screen.main()
        self.assertEqual(code, 1)
        self.assertIn("needs --render module", out.getvalue())


class ObItemsTests(unittest.TestCase):
    """`cadre.hmi.ob_items`, the one script function added: it shapes the library's rows into the components' item lists."""

    @classmethod
    def setUpClass(cls):
        cls.ns, _ = A.frame_ns()
        cls.items = staticmethod(cls.ns["ob_items"])

    def alert(self, id_, acked, active=True, type_="level-critical", time=1000):
        return {"id": id_, "tagId": "d", "source": f"src/{id_}", "text": f"Alarm {id_}", "type": type_, "time": time,
                "acknowledged": acked, "active": active, "shelved": False}

    def test_alert_rows_become_menu_items_with_the_ack_by_permission(self):
        rows = [self.alert("a", False), self.alert("b", {"acknowledgedBy": "u"}, type_="level-low"),
                self.alert("c", False, active=False, type_="level-medium")]
        out = self.items("alerts", rows, True)
        self.assertEqual([i["id"] for i in out], ["a", "b", "c"])
        self.assertTrue(all(i["tag"] == "obc-alert-menu-item" for i in out))
        self.assertEqual([i["status"] for i in out], ["unacknowledged", "acknowledged", "unacknowledged"])
        self.assertEqual([i["primaryActionState"] for i in out], ["enabled"] * 3)
        self.assertEqual(out[0]["title"], "Alarm a")
        self.assertEqual(out[0]["description"], "src/a")
        self.assertEqual(out[0]["time"], "t1000")
        icon = out[2]["children"][0]
        self.assertEqual((icon["tag"], icon["slot"], icon["type"], icon["active"], icon["acknowledged"]),
                         ("obc-alert-icon", "alert-icon", "level-medium", False, False))
        self.assertTrue(out[1]["children"][0]["acknowledged"])
        for i in out:   # the item and its icon use only attributes the element declares
            self.assertLessEqual(set(i) - {"tag", "id", "children"}, set(COMPONENTS["cadre.ob.alertmenuitem"]["props"]))
        self.assertEqual({i["primaryActionState"] for i in self.items("alerts", rows, False)}, {"disabled"})
        self.assertEqual(self.items("alerts", [], True), [])

    def test_a_row_without_a_time_has_no_time(self):
        out = self.items("alerts", [self.alert("a", False, time=None)], True)
        self.assertEqual((out[0]["time"], out[0]["day"]), ("", ""))

    def test_navigation_items_carry_the_route_the_check_the_icon_and_the_nodes_counts(self):
        counts = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4, "Diagnostic": 5, "total": 15, "unacked": 2}
        rows = [{"label": "Overview", "path": "/", "icon": "dashboard", "counts": counts},
                {"label": "Filtration", "path": "/filtration", "icon": "filter", "counts": {**counts, "total": 0}},
                {"label": "Alerts", "path": "/alerts", "icon": "alert-list"}]
        out = self.items("nav", rows, "/filtration", ["dashboard", "alert-list"])
        self.assertEqual([i["id"] for i in out], ["/", "/filtration", "/alerts"])
        self.assertEqual([i["checked"] for i in out], [False, True, False])
        self.assertEqual(out[0]["hasIcon"], True)
        self.assertEqual(out[0]["children"], [{"tag": "obi-dashboard", "slot": "icon"}])
        self.assertNotIn("hasIcon", out[1])            # an icon the module does not bundle draws none
        self.assertNotIn("children", out[1])
        self.assertEqual(out[0]["alerts"], {"countLevelCritical": 1, "countAlarm": 2, "countWarning": 3, "countCaution": 4,
                                            "countLevelDiagnostic": 5})   # wiki 13 section 11.1
        self.assertNotIn("alerts", out[1])             # no active alarm, no badge
        self.assertNotIn("alerts", out[2])             # a footer row names no node
        for i in out:
            self.assertLessEqual(set(i) - {"tag", "id", "children"}, set(COMPONENTS["cadre.ob.navigationitem"]["props"]))
        self.assertEqual(set(out[0]["alerts"]), set(self.ns["OB_COUNT_OF"].values()))
        self.assertLessEqual(set(self.ns["OB_COUNT_OF"].values()),
                             set(COMPONENTS["cadre.ob.navigationitem"]["props"]["alerts"]["properties"]))

    def test_the_icon_names_are_the_modules_bundled_ones(self):
        bundled = obframe.nav_icons()
        out = self.items("nav", [{"label": "x", "path": "/x", "icon": n} for n in bundled], "", bundled)
        self.assertEqual(len(out), len(bundled))
        self.assertTrue(all(i.get("hasIcon") for i in out))


if __name__ == "__main__":
    unittest.main()
