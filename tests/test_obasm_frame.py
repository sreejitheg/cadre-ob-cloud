"""Tests of the ASM variant of the new frame (`screen.py --frame obasm`, tranche T2 batch F6b): its views against the registry
(gate G1), the generator's facts the glass will rely on, the event scripts (each cites the measured event shape and calls the
library's own function), `cadre.hmi.obasm_items` (the one script function added), the option and its refusal under the stock
rendering, and the three other frames left as they were.

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
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
from hmi import gates, navigation, obasm, obframe, parent as par, screen  # noqa: E402

COMPONENTS = json.loads((ROOT / "module" / "components.json").read_text(encoding="utf-8"))
OBASM_VIEWS = ("Framework/OBASM/Head", "Framework/OBASM/NavDock", "Framework/OBASM/Crumb")
# the event of each module component the frame wires, with what its script must call (the library's own function)
WIRED = {
    ("Framework/OBASM/Head", "TopBar", "onMenuButtonClick"): "self.session.custom.navPanel = 'pages'",
    ("Framework/OBASM/Head", "TopBar", "onAppsButtonClick"): "self.session.custom.navPanel = 'support'",
    ("Framework/OBASM/Head", "TopBar", "onAlertClick"): "'alertMenu', 'Framework/OB/AlertMenu'",
    ("Framework/OBASM/Head", "TopBar", "onDimmingButtonClick"): "'brilliance', 'Framework/OB/Brilliance'",
    ("Framework/OBASM/Head", "TopBar", "onUserButtonClick"): "'userMenu', 'Framework/OB/UserMenu'",
    ("Framework/OBASM/Head", "Pivot", "onChange"): "self.session.custom.contentNode = self.view.custom.head.nodeId",
    ("Framework/OBASM/Head", "Tabs", "onTabSelected"): "system.perspective.navigate(event.id)",
    ("Framework/OBASM/NavDock", "Tree", "onItemClick"): "self.view.custom.tree.rows",
    ("Framework/OBASM/NavDock", "Support", "onItemClick"): "self.view.custom.support.rows",
}


def names(node):
    return [c["meta"]["name"] for c in node["children"]]


def by_name(doc):
    return {n["meta"]["name"]: n for n, _ in gates.walk(doc["root"]) if "meta" in n}


class ObasmViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.views = obasm.views()

    def test_the_parent_carries_the_three_views_and_the_registry_passes_them(self):
        self.assertEqual(tuple(sorted(self.views)), tuple(sorted(OBASM_VIEWS)))
        prj, contracts = par.build_parent()
        for v in OBASM_VIEWS + ("Framework/OB/AlertMenu", "Framework/ASM/AlarmBanner"):
            self.assertIn(v, contracts)
        with tempfile.TemporaryDirectory() as d:
            out = prj.write(Path(d))
            g1 = gates.g1_registry(out)
        self.assertTrue(g1["ok"], g1["summary"])

    def test_every_property_and_event_of_a_module_component_is_one_the_module_declares(self):
        used = set()
        for path, doc in self.views.items():
            for n, _ in gates.walk(doc["root"]):
                if not n["type"].startswith("cadre.ob."):
                    continue
                used.add(n["type"])
                spec = COMPONENTS[n["type"]]
                props = set(spec["props"])
                keys = set(n.get("props", {})) | {k.split(".", 1)[1] for k in n.get("propConfig", {}) if k.startswith("props.")}
                self.assertEqual(sorted(keys - props), [], f"{path} {n['meta']['name']}")
                for group in (n.get("events") or {}).values():
                    for ev in group:
                        self.assertIn(ev, spec["events"], f"{path} {n['meta']['name']} {ev}")
        self.assertEqual(used, {"cadre.ob.topbar", "cadre.ob.pivotitemgroup", "cadre.ob.tabrow", "cadre.ob.treenavigation",
                                "cadre.ob.navigationmenu"})

    def test_the_head_is_the_one_top_dock_the_bar_over_the_strip_over_the_page_header(self):
        head = self.views["Framework/OBASM/Head"]
        self.assertEqual(names(head["root"]), ["TopBar", "Strip", "PageHeader"])
        bar, strip, header = head["root"]["children"]
        self.assertEqual(bar["type"], "cadre.ob.topbar")
        self.assertEqual([c["position"]["basis"] for c in (bar, strip, header)], ["48px", "36px", "48px"])
        self.assertEqual(COMPONENTS["cadre.ob.topbar"]["defaultSize"]["height"], obasm.TOP_BAR_HEIGHT)   # measured, F4
        self.assertEqual(COMPONENTS["cadre.ob.pivotitemgroup"]["defaultSize"]["height"] - 96, obasm.HEADER_HEIGHT)   # 48 measured, F5
        self.assertEqual(head["props"]["defaultSize"]["height"], obasm.HEAD_HEIGHT)
        self.assertEqual(obasm.HEAD_HEIGHT, 132)
        docks = obasm.shared_docks("A")
        self.assertEqual([(d["viewPath"], d["size"]) for d in docks["top"]], [("Framework/OBASM/Head", 132)])
        self.assertEqual(f'[data-component-path="T[0].0:{names(head["root"]).index("TopBar")}"]', '[data-component-path="T[0].0:0"]')

    def test_the_strip_keeps_the_cadre_crumb_search_and_alert_message(self):
        """Owner's answers 2 and 3: the Cadre crumb with its badges, and the alert message with its ACK (W6); the module has no search."""
        head = self.views["Framework/OBASM/Head"]
        strip = head["root"]["children"][1]
        self.assertEqual(names(strip), ["Crumbs", "Spacer", "SearchField", "AlertMessage"])
        self.assertEqual(strip["children"][0]["props"]["path"], "Framework/OBASM/Crumb")
        self.assertEqual(strip["children"][2]["type"], "ia.input.text-field")
        self.assertEqual(strip["children"][2]["propConfig"]["props.text"]["binding"]["config"]["path"], "session.custom.searchQuery")
        ack = by_name(head)["Ack"]
        self.assertEqual(ack["propConfig"]["props.enabled"]["binding"]["config"]["expression"], "{view.custom.can.W6}")
        self.assertIn("cadre.hmi.ack_top(", ack["events"]["component"]["onActionPerformed"]["config"]["script"])
        for key in ("custom.alarm", "custom.can", "custom.crumbs", "custom.head"):
            self.assertIn(key, head["propConfig"])
        self.assertEqual(head["propConfig"]["custom.crumbs"], navigation.CRUMBS_ASM_CFG)   # the trail follows the pivot pages' node
        self.assertIn("page_header", head["propConfig"]["custom.head"]["binding"]["transforms"][0]["code"])

    def test_the_bar_has_the_asm_menu_and_apps_buttons_and_gives_its_page_name_to_the_crumb(self):
        bar = self.views["Framework/OBASM/Head"]["root"]["children"][0]
        self.assertIs(bar["props"]["showAppsButton"], True)
        self.assertIn("onAppsButtonClick", COMPONENTS["cadre.ob.topbar"]["events"])
        name = bar["propConfig"]["props.pageName"]["binding"]
        self.assertIn("len({view.custom.crumbs}) > 0", name["config"]["expression"])
        self.assertIn("page_title", name["transforms"][0]["code"])
        shown = set(bar["props"]) | {k.split(".", 1)[1] for k in bar["propConfig"]}
        for hidden in ("showSilenceButton", "commandButtonText"):      # owner's answer 4; the F4 run-on text
            self.assertNotIn(hidden, shown)
        self.assertNotIn("onSilenceClick", bar["events"]["component"])
        expr = lambda k: bar["propConfig"][f"props.{k}"]["binding"]["config"]["expression"]   # noqa: E731
        self.assertEqual(expr("nAlerts"), "{view.custom.alarm.count}")
        self.assertEqual(expr("blinking"), "{view.custom.alarm.unacked} > 0")
        # the module variant's bar is the same function with no argument
        ob_bar = obframe.head()["root"]["children"][0]
        self.assertNotIn("showAppsButton", ob_bar["props"])
        self.assertNotIn("onAppsButtonClick", ob_bar["events"]["component"])
        self.assertEqual(ob_bar["propConfig"]["props.pageName"]["binding"]["config"]["path"], "page.props.path")

    def test_the_page_header_has_the_pivot_the_tabs_and_the_asm_buttons(self):
        head = self.views["Framework/OBASM/Head"]
        header = head["root"]["children"][2]
        self.assertEqual(names(header), ["Title", "Level", "Pivot", "Tabs", "Spacer", "Previous", "Next"])
        kids = {c["meta"]["name"]: c for c in header["children"]}
        asm = {c["meta"]["name"]: c for c in navigation.page_header()["root"]["children"]}
        for k in ("Title", "Level", "Previous", "Next"):      # the ASM header's own nodes
            self.assertEqual(kids[k], asm[k])
        pivot, tabs = kids["Pivot"], kids["Tabs"]
        self.assertEqual(pivot["type"], "cadre.ob.pivotitemgroup")
        self.assertEqual(pivot["propConfig"]["props.selectedValue"]["binding"]["config"]["expression"], "{view.custom.head.mode}")
        self.assertEqual(pivot["propConfig"]["position.display"]["binding"]["config"]["expression"], "len({view.custom.head.nodeId}) > 0")
        self.assertIn("'pivot', value", pivot["propConfig"]["props.items"]["binding"]["transforms"][0]["code"])
        self.assertEqual(tabs["type"], "cadre.ob.tabrow")
        self.assertEqual(tabs["propConfig"]["position.display"]["binding"]["config"]["expression"], "len({view.custom.head.tabs}) > 0")
        for k in ("props.tabs", "props.selectedTabId"):
            self.assertEqual(tabs["propConfig"][k]["binding"]["config"]["expression"], "{view.custom.head.tabs}")
        pv_code = pivot["events"]["component"]["onChange"]["config"]["script"]
        self.assertIn("system.perspective.navigate('/node/' + v)", pv_code)
        self.assertIn("self.view.custom.head.mimicRoute", pv_code)
        # the routes are the pivot pages the ASM header navigates to
        self.assertEqual((navigation.NODE_ALARMS_ROUTE, navigation.NODE_TREND_ROUTE), ("/node/alarms", "/node/trend"))
        self.assertIn("/node/alarms", obasm.page_config("A", {})["pages"])

    def test_the_dock_is_the_asm_docks_two_states_over_the_tree_and_the_support_menu(self):
        dock = self.views["Framework/OBASM/NavDock"]
        self.assertEqual(names(dock["root"]), ["Header", "Search", "Tree", "Support"])
        asm = {c["meta"]["name"]: c for c in navigation.nav_dock()["root"]["children"]}
        kids = {c["meta"]["name"]: c for c in dock["root"]["children"]}
        self.assertEqual(kids["Header"], asm["Header"])       # the title that follows the state, and the close button
        self.assertEqual(kids["Search"], asm["Search"])       # the search box on `navQuery`
        self.assertIn("closeDock('nav')", json.dumps(kids["Header"]))
        tree, menu = kids["Tree"], kids["Support"]
        self.assertEqual((tree["type"], menu["type"]), ("cadre.ob.treenavigation", "cadre.ob.navigationmenu"))
        self.assertEqual(tree["propConfig"]["props.items"]["binding"]["config"]["expression"], "{view.custom.tree.items}")
        self.assertEqual(menu["propConfig"]["props.items"]["binding"]["config"]["expression"], "{view.custom.support.items}")
        self.assertIn("!= 'support'", tree["propConfig"]["position.display"]["binding"]["config"]["expression"])
        self.assertIn("= 'support'", menu["propConfig"]["position.display"]["binding"]["config"]["expression"])
        cfg = dock["propConfig"]
        code = cfg["custom.tree"]["binding"]["transforms"][0]["code"]
        self.assertIn("cadre.hmi.nav_tree(self.session", code)
        self.assertIn("cadre.hmi.obasm_items('tree', rows, parts[0], ", code)
        self.assertIn("{session.custom.navQuery}", cfg["custom.tree"]["binding"]["config"]["expression"])
        self.assertIn("cadre.hmi.nav_support(self.session, value)", cfg["custom.support"]["binding"]["transforms"][0]["code"])
        self.assertIn(repr(obframe.nav_icons()), cfg["custom.support"]["binding"]["transforms"][0]["code"])

    def test_the_crumb_popup_opens_beneath_the_strip_and_the_asm_crumb_is_as_it_was(self):
        crumb = json.dumps(self.views["Framework/OBASM/Crumb"])
        self.assertIn("'top': 84", crumb)
        self.assertIn("Framework/ASM/CrumbPopup", crumb)           # Show and Areas, the areas with their badges
        self.assertIn("'top': 48", json.dumps(navigation.crumb()))
        self.assertEqual(obasm.CRUMB_POPUP_TOP, obasm.TOP_BAR_HEIGHT + obasm.STRIP_HEIGHT)

    def test_every_wired_event_cites_the_measured_shape_and_calls_the_existing_function(self):
        seen = set()
        for path, doc in self.views.items():
            for node, ev, code in A.handler_scripts(doc):
                if (path, node, ev) not in WIRED:
                    continue
                seen.add((path, node, ev))
                first = code.strip().splitlines()[0].strip()
                self.assertTrue(first.startswith("# GF-37"), f"{path} {ev}: {first}")
                self.assertIn(WIRED[(path, node, ev)], code, f"{path} {ev}")
                compile("def f(self, event):\n" + code + "\n", f"{path}/{ev}", "exec")
        self.assertEqual(seen, set(WIRED))

    def test_a_row_press_runs_the_asm_row_action_and_closes_the_dock(self):
        dock = self.views["Framework/OBASM/NavDock"]
        for node in ("Tree", "Support"):
            code = by_name(dock)[node]["events"]["component"]["onItemClick"]["config"]["script"]
            for want in ("x['id'] == event.id", "r['action'] == 'alarms'", "self.session.custom.contentNode = r['nodeId']",
                         "system.perspective.navigate(r['route'])", "cadre.hmi.select_device(self.session, r['deviceId']",
                         "closeDock('nav')"):
                self.assertIn(want, code, node)
            self.assertNotIn("system.tag.write", code)             # no write path of its own

    def test_no_credential_or_write_is_a_property_or_a_binding(self):
        for path, doc in self.views.items():
            text = json.dumps(doc).lower()
            self.assertNotIn("password", text, path)
            self.assertNotIn("system.tag.write", text, path)
            self.assertNotIn("writeblocking", text, path)


class ObasmOptionTests(unittest.TestCase):
    def build(self, frame, render="module"):
        _, descs = A.wtp_descs()
        return screen.build_child("cadre_hmi_wtpq", descs, "Village WTP", "*cadre_hmi_wtpq*", render, frame=frame)

    def files(self, child):
        return {k: v.decode("utf-8") for k, v in child.files.items() if k.endswith(".json")}

    def test_the_option_is_the_fourth_frame_and_the_first_three_keep_their_names(self):
        self.assertEqual(navigation.FRAMES, ("openbridge", "asm", "ob", "obasm"))
        self.assertEqual(navigation.ASM_FRAMES, ("asm", "obasm"))
        self.assertEqual(navigation.MODULE_FRAMES, ("ob", "obasm"))

    def test_a_child_with_the_option_has_the_asm_variants_docks_session_and_pages(self):
        child, reports = self.build("obasm")
        self.assertFalse(any(v["errors"] for v in reports.values()))
        files = self.files(child)
        pc = json.loads(next(v for k, v in files.items() if k.endswith("page-config/config.json")))
        d = pc["sharedDocks"]
        self.assertEqual([(x["id"], x["viewPath"], x["size"], x["show"]) for x in d["top"]], [("topbar", "Framework/OBASM/Head", 132, "visible")])
        self.assertEqual([(x["id"], x["viewPath"], x["modal"], x["size"]) for x in d["left"]], [("nav", "Framework/OBASM/NavDock", True, 320)])
        self.assertEqual([(x["viewPath"], x["size"]) for x in d["bottom"]], [("Framework/ASM/AlarmBanner", 76)])   # the banner stays
        self.assertEqual(d["right"][0]["viewPath"], "Framework/SideMenu")
        self.assertEqual(d["top"][0]["viewParams"], {"appName": "Village WTP", "showUser": True})
        for route in ("/alerts", "/node/alarms", "/node/trend"):
            self.assertIn(route, pc["pages"])
        sp = json.loads(next(v for k, v in files.items() if k.endswith("session-props/props.json")))["custom"]
        self.assertEqual(sp["frame"], "obasm")
        for key in ("pageInfo", "searchIndex", "contentNode", "hierarchy", "alarmScope", "devices"):
            self.assertIn(key, sp)
        self.assertEqual(sp["hierarchy"], self.build("asm")[0].files and json.loads(next(
            v for k, v in self.files(self.build("asm")[0]).items() if k.endswith("session-props/props.json")))["custom"]["hierarchy"])
        # a page carries the in-page search panel, as the ASM frame's does
        page = next(v for k, v in files.items() if k.endswith("Overview/view.json") or "views/Pages" in k and k.endswith("view.json"))
        self.assertIn("SearchPanel", page)

    def test_the_floating_faceplate_follows_the_session_frame(self):
        ns, _ = A.frame_ns()
        for frame, want in (("asm", True), ("obasm", True), ("openbridge", False), ("ob", False)):
            s = A.session_of(A.wtp_descs()[1], frame=frame)
            self.assertIs(ns["asm_frame"](s), want, frame)

    def test_the_three_other_frames_are_as_they_were(self):
        for frame, top in (("openbridge", ("Framework/TopBar", 48)), ("asm", ("Framework/ASM/Head", 84)), ("ob", ("Framework/OB/Head", 84))):
            child, _ = self.build(frame)
            files = self.files(child)
            text = "\n".join(files.values())
            self.assertNotIn("OBASM", text, frame)
            self.assertNotIn("obasm", text, frame)
            pc = json.loads(next(v for k, v in files.items() if k.endswith("page-config/config.json")))
            self.assertEqual([(d["viewPath"], d["size"]) for d in pc["sharedDocks"]["top"]], [top], frame)
            sp = json.loads(next(v for k, v in files.items() if k.endswith("session-props/props.json")))
            self.assertEqual(sp["custom"]["frame"], frame)

    def test_a_stock_build_with_the_option_stops_with_a_clear_error(self):
        with self.assertRaises(ValueError) as cm:
            self.build("obasm", render="stock")
        self.assertIn("--frame obasm", str(cm.exception))
        self.assertIn("--render module", str(cm.exception))
        argv = ["screen.py", "--project", "cadre_hmi_x", "--descriptor", str(ROOT / "screens" / "wtp" / "overview.json"),
                "--frame", "obasm", "--out", tempfile.gettempdir()]
        out = io.StringIO()
        with mock.patch.object(sys, "argv", argv), redirect_stdout(out):
            code = screen.main()
        self.assertEqual(code, 1)
        self.assertIn("needs --render module", out.getvalue())

    def test_the_frames_previous_and_next_must_name_a_route_as_for_the_asm_frame(self):
        _, descs = A.wtp_descs()
        descs = copy.deepcopy(descs)
        descs[0]["screen"]["next"] = "/nowhere"
        with self.assertRaises(ValueError):
            screen.build_child("cadre_hmi_wtpq", descs, "V", "*cadre_hmi_wtpq*", "module", frame="obasm")

    def test_gates_g0_to_g7_pass_on_a_sample(self):
        _, descs = A.wtp_descs()
        with tempfile.TemporaryDirectory() as d:
            base = par.build_parent()[0].write(Path(d))
            child, reports = screen.build_child("cadre_hmi_t", copy.deepcopy(descs), "T", "*cadre_hmi_t*", "module", frame="obasm")
            out = child.write(Path(d))
            res = gates.run(out, base)
            self.assertTrue(res["ok"], {k: v for k, v in res.items() if isinstance(v, dict) and not v.get("ok", True)})
            self.assertFalse(any(v["errors"] for v in reports.values()))


class ObasmItemsTests(unittest.TestCase):
    """`cadre.hmi.obasm_items`, the one script function added: it shapes the library's rows into the components' items."""

    @classmethod
    def setUpClass(cls):
        # three active alarms, two of them in Filtration (the sample's own pumps and valve)
        events = [A.T.AlarmListTests.Event("P301", "High", 1), A.T.AlarmListTests.Event("XV301", "Critical", 2, acked=3),
                  A.T.AlarmListTests.Event("P101", "Low", 4)]
        cls.ns, cls.calls = A.frame_ns(events)
        cls.items = staticmethod(cls.ns["obasm_items"])
        _, cls.descs = A.wtp_descs()

    def session(self):
        return A.session_of(self.descs)

    def test_the_pivot_has_the_three_pages_and_mimic_waits_for_a_page(self):
        out = self.items("pivot", "/filtration")
        self.assertEqual([(i["id"], i["value"], i["label"]) for i in out], [("mimic", "mimic", "Mimic"), ("alarms", "alarms", "Alarms"), ("trend", "trend", "Trend")])
        self.assertEqual([i["disabled"] for i in out], [False] * 3)
        self.assertEqual([i["disabled"] for i in self.items("pivot", "")], [True, False, False])
        for i in out:
            self.assertEqual(i["tag"], "obc-pivot-item")
            self.assertLessEqual(set(i) - {"tag", "id", "children"}, set(COMPONENTS["cadre.ob.pivotitem"]["props"]))

    def test_the_tabs_are_the_nodes_pages_and_the_selected_tab_is_the_open_one(self):
        tabs = [{"label": "Filtration", "route": "/filtration", "selected": True}, {"label": "Backwash", "route": "/backwash", "selected": False}]
        self.assertEqual(self.items("tabs", tabs), [{"id": "/filtration", "title": "Filtration"}, {"id": "/backwash", "title": "Backwash"}])
        self.assertEqual(self.items("tab", tabs), "/filtration")
        self.assertEqual(self.items("tab", [dict(t, selected=False) for t in tabs]), "")
        self.assertEqual((self.items("tabs", []), self.items("tab", [])), ([], ""))
        for t in self.items("tabs", tabs):
            self.assertLessEqual(set(t), set(COMPONENTS["cadre.ob.tabrow"]["props"]["tabs"]["items"]["properties"]))

    def test_the_tree_nests_the_hierarchy_opens_the_current_branch_and_carries_the_counts(self):
        s = self.session()
        rows = self.ns["nav_tree"](s, "", "/filtration")
        out = self.items("tree", rows, "/filtration", obframe.nav_icons())
        top = out["items"]
        self.assertEqual([i["label"] for i in top], ["WTP"])
        root = top[0]
        self.assertEqual((root["tag"], root["id"], root["hasIcon"]), ("obc-tree-navigation-group", "n:n0", False))
        self.assertTrue(root["expanded"])                                       # the current page stands beneath it
        kids = {c["label"]: c for c in root["children"]}
        self.assertEqual(set(kids), {"Plant Overview", "Disinfection", "Filtration", "Intake"})
        self.assertEqual(kids["Plant Overview"]["tag"], "obc-tree-navigation-item")
        self.assertEqual(kids["Plant Overview"]["id"], "p:/")
        filtration = kids["Filtration"]
        self.assertEqual(filtration["tag"], "obc-tree-navigation-group")
        self.assertTrue(filtration["expanded"])
        self.assertFalse(kids["Disinfection"]["expanded"])
        page = filtration["children"][0]
        self.assertEqual((page["label"], page["checked"], page["id"]), ("Filtration", True, "p:/filtration"))
        self.assertNotIn("alerts", page)                                        # a page names no node's counts
        # wiki 13 section 11.1: the node's counts, rolled up, by the same table as the navigation menu
        want = rows[[r["label"] for r in rows].index("WTP")]["counts"]
        self.assertEqual(root["alerts"], {self.ns["OB_COUNT_OF"][p]: want[p] for p in self.ns["OB_COUNT_OF"]})
        self.assertEqual(filtration["alerts"]["countLevelCritical"] + filtration["alerts"]["countAlarm"]
                         + filtration["alerts"]["countWarning"] + filtration["alerts"]["countCaution"]
                         + filtration["alerts"]["countLevelDiagnostic"], 2)
        self.assertEqual(want["total"], 3)
        self.assertEqual(root["alerts"]["countAlarm"], 1)                      # High; Critical is countLevelCritical
        self.assertEqual(root["alerts"]["countLevelCritical"], 1)
        self.assertLessEqual(set(self.ns["OB_COUNT_OF"].values()),
                             set(COMPONENTS["cadre.ob.treenavigationgroup"]["props"]["alerts"]["properties"]))
        # the tags and attributes are the ones the module's items declare
        def walk(item):
            tag = item["tag"]
            allowed = set(COMPONENTS[{"obc-tree-navigation-group": "cadre.ob.treenavigationgroup",
                                      "obc-tree-navigation-item": "cadre.ob.treenavigationitem"}[tag]]["props"]) | {"tag", "id", "children", "hasIcon", "hasLeadingIcon"}
            self.assertLessEqual(set(item), allowed, item["label"])
            for c in item.get("children", []):
                walk(c)
        walk(root)

    def test_every_item_of_the_tree_has_its_row_for_a_press(self):
        s = self.session()
        for query, route in (("", "/"), ("", "/filtration"), ("filt", "/")):
            rows = self.ns["nav_tree"](s, query, route)
            out = self.items("tree", rows, route, [])
            ids = {r["id"] for r in out["rows"]}
            self.assertEqual(len(ids), len(out["rows"]), "an id is used once")

            def collect(item):
                yield item["id"]
                for c in item.get("children", []):
                    yield from collect(c)
            shown = [i for item in out["items"] for i in collect(item)]
            self.assertEqual(sorted(set(shown) - ids), [], (query, route))
            for r in out["rows"]:
                self.assertLessEqual(set(r), {"id", *self.ns["ROW_ACTION_KEYS"]})
        # a node row opens its first page, a leaf node without one its Alarms page, both closing the dock
        rows = {r["id"]: r for r in self.items("tree", self.ns["nav_tree"](s, "", "/"), "/", [])["rows"]}
        self.assertEqual((rows["p:/filtration"]["action"], rows["p:/filtration"]["route"], rows["p:/filtration"]["close"]), ("route", "/filtration", "nav"))

    def test_a_query_gives_a_flat_list_and_a_node_without_a_page_keeps_its_alarms(self):
        s = self.session()
        flat = self.items("tree", self.ns["nav_tree"](s, "filt", "/"), "/", [])
        self.assertEqual([(i["tag"], i["label"]) for i in flat["items"]],
                         [("obc-tree-navigation-item", "Filtration"), ("obc-tree-navigation-item", "Filtration")])
        # a node holding only a node: a group, whose first leaf is the node's Alarms page
        rows = [dict(self.ns["ROW_DEFAULT"], kind="node", label="Plant", depth=0, nodeId="n9", route="", action="alarms", close="nav",
                     counts=self.ns["_no_counts"]()),
                dict(self.ns["ROW_DEFAULT"], kind="node", label="Area", depth=1, nodeId="n10", route="/area", action="route", close="nav",
                     counts=self.ns["_no_counts"]()),
                dict(self.ns["ROW_DEFAULT"], kind="page", label="Area", depth=2, route="/area", action="route", nodeId="n10", close="nav")]
        out = self.items("tree", rows, "/", [])
        plant = out["items"][0]
        self.assertEqual(plant["tag"], "obc-tree-navigation-group")
        self.assertEqual([c["label"] for c in plant["children"]], ["Alarms", "Area"])
        self.assertEqual(plant["children"][0]["id"], "n:n9:alarms")
        alarms = {r["id"]: r for r in out["rows"]}["n:n9:alarms"]
        self.assertEqual((alarms["action"], alarms["nodeId"], alarms["route"]), ("alarms", "n9", ""))
        self.assertFalse(plant["expanded"])

    def test_a_project_without_a_hierarchy_lists_its_pages(self):
        import types
        bare = types.SimpleNamespace(custom=types.SimpleNamespace(hierarchy=[], nav={
            "items": [{"label": "Home", "path": "/", "icon": "home", "node": ""}], "footer": []}))
        out = self.items("tree", self.ns["nav_tree"](bare, "", "/"), "/", [])
        self.assertEqual([(i["tag"], i["label"], i["checked"]) for i in out["items"]], [("obc-tree-navigation-item", "Home", True)])
        self.assertEqual(self.items("tree", [], "/", []), {"rows": [], "items": []})

    def test_the_support_list_is_the_navigation_menu_with_the_open_page_checked(self):
        s = self.session()
        rows = self.ns["nav_support"](s, "/alerts")
        out = self.items("support", rows, "/alerts", ["alert-list", "dashboard"])
        self.assertEqual([i["label"] for i in out["items"]], ["All alarms", "Trends", "Alerts"])
        self.assertEqual([i["checked"] for i in out["items"]], [False, False, True])
        alerts = out["items"][2]
        self.assertEqual((alerts["tag"], alerts["id"], alerts["hasIcon"]), ("obc-navigation-item", "s:/alerts", True))
        self.assertEqual(alerts["children"], [{"tag": "obi-alert-list", "slot": "icon"}])
        self.assertNotIn("hasIcon", out["items"][1])                            # an icon the module does not bundle draws none
        self.assertEqual(out["items"][0]["id"], "s:alarms")
        by = {r["id"]: r for r in out["rows"]}
        self.assertEqual((by["s:alarms"]["action"], by["s:alarms"]["nodeId"], by["s:/alerts"]["route"]), ("alarms", "", "/alerts"))
        for i in out["items"]:
            self.assertLessEqual(set(i) - {"tag", "id", "children"}, set(COMPONENTS["cadre.ob.navigationitem"]["props"]))


if __name__ == "__main__":
    unittest.main()
