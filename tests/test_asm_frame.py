"""Tests of the ASM application frame (COB-160): several floating faceplates, the navigation dock, the crumb
popup, the global search, the page header and the bottom alarm banner, switched on by `screen.py --frame asm`.

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
import re
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "plants"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_hmi as T  # noqa: E402  (its event fakes and view helpers; imported as a module so its tests do not rerun here)
from hmi import gates, library, navigation, parent as par, screen, scripts  # noqa: E402


def frame_ns(events=()):
    """`cadre.hmi` under CPython with an alarm query answering `events` and a date fake."""
    calls = []

    class Alarm:
        @staticmethod
        def queryStatus(path=None, state=None, priority=None):
            calls.append(("query", list(path), list(state or [])))
            return list(events)

    class Date:
        @staticmethod
        def fromMillis(ms):
            return ms

        @staticmethod
        def format(d, pattern):
            return f"t{d}"

    class System:
        alarm, date = Alarm, Date
    ns = {"unicode": str, "long": int, "system": System}
    exec(scripts.HMI, ns)
    return ns, calls


def wtp_descs():
    import wtp
    descs = [wtp.overview(), wtp.intake(), wtp.filtration(), wtp.disinfection()]
    descs[0]["screen"].update(level="Level 1 overview", next="/intake")
    descs[1]["screen"].update(level="Level 2 unit", previous="/", next="/filtration")
    descs[2]["screen"].update(level="Level 2 unit", previous="/intake")
    return wtp, descs


def session_of(descs, **custom):
    """A session over the hierarchy and the device index the generator writes for `descs`."""
    h = screen.hierarchy(descs)
    c = types.SimpleNamespace(hierarchy=h, devices=screen.device_index(descs), alarmScope="*cadre_hmi_wtp*", frame="asm",
                              nav={"items": [{"label": "Filtration", "path": "/filtration", "icon": "", "node": "WTP/Filtration"},
                                             {"label": "Trends", "path": "/trends", "icon": "trend", "node": ""}],
                                   "footer": [{"label": "Alerts", "path": "/alerts", "icon": "alert-list"}]},
                              floating={}, contentNode="", pageInfo=navigation.page_info(descs),
                              selectedDevice="[default]cadre_hmi_wtp/P301", selectedKind="pump", selectedStyle="asm",
                              selectedTitle="P301", selectedLabel="Filter feed pump", selectedTab="alarms",
                              trends=[{"deviceId": "[default]cadre_hmi_wtp/P301", "member": "speed"},
                                      {"deviceId": "[default]cadre_hmi_wtp/P101", "member": "speed"}])
    for k, v in custom.items():
        setattr(c, k, v)
    return types.SimpleNamespace(custom=c)


def handler_scripts(doc):
    """(view node name, event, script) of every event handler of a view."""
    out = []
    for n, _ in gates.walk(doc["root"]):
        for group in (n.get("events") or {}).values():
            for ev, h in group.items():
                code = (h.get("config") or {}).get("script")
                if code:
                    out.append((n["meta"]["name"], ev, code))
    return out


class FloatingFaceplateTests(unittest.TestCase):
    """DESIGN section 6, float mode: a popup for each device, 24 px apart; a device already floating is
    addressed again by its own popup; the Dock pin moves that faceplate to the dock."""

    def test_a_popup_for_each_device_and_a_slot_for_each_popup(self):
        ns, _ = frame_ns()
        ids = {ns["float_id"](d) for d in ("[default]t/P1", "[default]t/P2", "[default]t/P1/x", "")}
        self.assertEqual(len(ids), 4)
        self.assertTrue(all(i.startswith("fp_") and i.replace("_", "").isalnum() for i in ids))
        _, descs = wtp_descs()
        s = session_of(descs)
        a, b = "[default]t/A", "[default]t/B"
        pa, pb = ns["float_position"](s, a), ns["float_position"](s, b)
        self.assertEqual(pa, {"top": ns["FLOAT_TOP"], "right": ns["FLOAT_RIGHT"]})
        self.assertEqual({k: pb[k] - pa[k] for k in pa}, {"top": 24, "right": 24})
        self.assertEqual(ns["float_position"](s, a), pa)                        # a device keeps its place
        for i in range(30):                                                       # the slots wrap, the list stays short
            ns["float_position"](s, f"[default]t/D{i}")
        self.assertLessEqual(len(s.custom.floating), 4 * ns["FLOAT_SLOTS"])
        self.assertLess(max(ns["float_position"](s, f"[default]t/D{i}")["right"] for i in range(30)), 5 + 24 * 6)

    def test_the_popup_carries_the_selected_device_not_the_session(self):
        ns, _ = frame_ns()
        _, descs = wtp_descs()
        s = session_of(descs)
        self.assertEqual(ns["float_params"](s, "fp_x"),
                         {"popupId": "fp_x", "deviceId": "[default]cadre_hmi_wtp/P301", "kind": "pump", "style": "asm",
                          "title": "P301", "label": "Filter feed pump", "tab": "alarms", "localKind": ""})   # WP-W04
        self.assertEqual(set(ns["float_params"](s, "x")), set(navigation.FLOAT_PARAMS))
        self.assertTrue(ns["asm_frame"](s))
        s.custom.frame = "openbridge"
        self.assertFalse(ns["asm_frame"](s))
        self.assertFalse(ns["asm_frame"](types.SimpleNamespace(custom=types.SimpleNamespace())))   # a project from before

    def test_every_opener_floats_a_popup_for_the_device_in_the_asm_frame_only(self):
        lines = library.open_faceplate()
        code = "\n".join(lines)
        compile("def f(self):\n" + "\n".join("\t" + ln for ln in lines) + "\n", "open_faceplate", "exec")
        self.assertIn("if cadre.hmi.asm_frame(self.session):", code)
        self.assertIn("openPopup(id=fid, view='Framework/ASM/FloatFaceplate', params=cadre.hmi.float_params(self.session, fid)", code)
        self.assertIn("system.perspective.closePopup(fid)", code)                 # an open device is addressed again
        self.assertIn(library.open_popup_line(), code)                           # the default frame keeps its popup
        self.assertEqual(code.count("openDock(id='faceplate')"), 1)               # dock mode unchanged: one faceplate
        tabbed = library.open_device("d", "k", tab="'alarms'")
        self.assertEqual(tabbed[0], "cadre.hmi.select_device(self.session, d, k, '', '', 'alarms')")   # COB-158

    def test_the_float_view_reads_its_parameters_and_docks_itself(self):
        v = navigation.float_faceplate()
        self.assertEqual(v["props"]["defaultSize"], {"width": 450, "height": 600})
        self.assertEqual(set(v["params"]), set(navigation.FLOAT_PARAMS))
        n = T.view_nodes(v)
        path = n["Faceplate"]["propConfig"]["props.path"]["binding"]["config"]["expression"]
        self.assertNotIn("session.custom", path)
        self.assertIn("{view.params.kind}", path)
        self.assertIn("{view.params.style}", path)
        self.assertEqual(n["Faceplate"]["propConfig"]["props.params.tab"]["binding"]["config"]["expression"], "{view.params.tab}")
        dock = n["Dock"]["events"]["component"]["onActionPerformed"]["config"]["script"].splitlines()
        self.assertEqual(dock[0].strip(), "p = self.view.params")
        self.assertEqual(dock[1].strip(), "self.session.custom.faceplateMode = 'dock'")
        self.assertIn("cadre.hmi.select_device(self.session, p.deviceId, p.kind, p.title, p.label, p.tab, local=p.localKind)", dock[2])   # WP-W04
        self.assertEqual(dock[-1].strip(), "system.perspective.closePopup(p.popupId)")

    def test_the_docks_float_button_floats_per_device_too(self):
        from hmi import framework
        float_ = T.view_nodes(framework.side_menu())["Float"]["events"]["component"]["onActionPerformed"]["config"]["script"]
        self.assertIn("cadre.hmi.asm_frame(self.session)", float_)
        self.assertIn(library.open_popup_line(), float_)


class CrumbsAndNavigationTests(unittest.TestCase):
    def setUp(self):
        _, self.descs = wtp_descs()
        self.s = session_of(self.descs)
        self.events = [T.AlarmListTests.Event("P301", "High", 1), T.AlarmListTests.Event("XV301", "Critical", 2, acked=3),
                       T.AlarmListTests.Event("P101", "Low", 4)]
        self.ns, self.calls = frame_ns(self.events)

    def test_the_trail_names_the_node_and_the_pivot_pages_follow_the_content_node(self):
        trail = self.ns["frame_crumbs"](self.s, "/filtration")
        self.assertEqual([(c["name"], c["route"], c["first"], c["last"], c["counts"]["total"]) for c in trail],
                         [("WTP", "/", True, False, 3), ("Filtration", "/filtration", False, True, 2)])
        self.assertEqual({c["nodeId"] for c in trail}, {"n0", "n2"})
        self.assertEqual(self.ns["frame_crumbs"](self.s, "/alerts"), [])
        self.s.custom.contentNode = "n3"                                      # the Alarms pivot of Intake
        self.assertEqual([c["name"] for c in self.ns["frame_crumbs"](self.s, "/node/alarms")], ["WTP", "Intake"])
        self.s.custom.contentNode = ""                                        # empty: the root
        self.assertEqual([c["name"] for c in self.ns["frame_crumbs"](self.s, "/node/trend")], ["WTP"])

    def test_the_crumb_popup_has_show_and_areas(self):
        rows = self.ns["crumb_menu"](self.s, "n0")
        self.assertEqual([(r["kind"], r["label"]) for r in rows],
                         [("group", "Show"), ("show", "Mimic"), ("show", "Alarms"), ("show", "Trend"), ("group", "Areas"),
                          ("area", "Disinfection"), ("area", "Filtration"), ("area", "Intake")])
        mimic, alarms, trend = rows[1:4]
        self.assertEqual((mimic["action"], mimic["route"]), ("route", "/"))
        self.assertEqual((alarms["action"], alarms["nodeId"], trend["action"]), ("alarms", "n0", "trend"))
        areas = {r["label"]: r for r in rows if r["kind"] == "area"}
        self.assertEqual((areas["Filtration"]["counts"]["total"], areas["Filtration"]["route"]), (2, "/filtration"))
        self.assertTrue(all(r["close"] == "crumbPopup" for r in rows[1:4]))
        leaf = self.ns["crumb_menu"](self.s, "n2")
        self.assertNotIn("Areas", [r["label"] for r in leaf])                 # a leaf node has no areas
        self.assertEqual(self.ns["crumb_menu"](self.s, "nope"), [])

    def test_the_tree_lists_nodes_with_their_pages_and_selects_the_current_page(self):
        rows = self.ns["nav_tree"](self.s, "", "/filtration")
        self.assertEqual([(r["kind"], r["label"], r["depth"]) for r in rows[:4]],
                         [("node", "WTP", 0), ("page", "Plant Overview", 1), ("node", "Disinfection", 1), ("page", "Disinfection and Storage", 2)])
        self.assertEqual([r["label"] for r in rows if r["selected"]], ["Filtration"])
        node = [r for r in rows if r["kind"] == "node" and r["label"] == "Filtration"][0]
        self.assertEqual((node["counts"]["total"], node["route"], node["close"]), (2, "/filtration", "nav"))
        self.assertEqual(len([c for c in self.calls if c[0] == "query"]), 1)   # one query for the whole tree

    def test_a_query_filters_the_tree_into_a_flat_list(self):
        rows = self.ns["nav_tree"](self.s, "filt", "/")
        self.assertEqual([(r["kind"], r["label"], r["depth"], r["second"]) for r in rows],
                         [("node", "Filtration", 0, "WTP/Filtration"), ("page", "Filtration", 0, "WTP/Filtration")])
        self.assertEqual(self.ns["nav_tree"](self.s, "zzz", "/"), [])

    def test_a_project_without_a_hierarchy_lists_its_items_and_the_footer_holds_the_support_pages(self):
        bare = types.SimpleNamespace(custom=types.SimpleNamespace(hierarchy=[], nav={
            "items": [{"label": "Home", "path": "/", "icon": "home", "node": ""}], "footer": []}))
        self.assertEqual([(r["label"], r["route"]) for r in self.ns["nav_tree"](bare, "", "/")], [("Home", "/")])
        foot = self.ns["nav_footer"](self.s, "/alerts")
        self.assertEqual([(r["label"], r["selected"]) for r in foot], [("Trends", False), ("Alerts", True)])

    def test_the_views(self):
        nodes = T.view_nodes(navigation.nav_dock())
        cfg = json.dumps(nodes["Tree"]["propConfig"])
        self.assertIn("cadre.hmi.nav_tree(self.session", cfg)
        self.assertIn("{session.custom.navQuery}", cfg)
        self.assertEqual(nodes["Search"]["propConfig"]["props.text"]["binding"]["config"],
                         {"path": "session.custom.navQuery", "bidirectional": True})
        close = nodes["Close"]["events"]["dom"]["onClick"]["config"]["script"]
        self.assertIn("closeDock('nav')", close)
        row = handler_scripts(navigation.list_row())[0][2]
        self.assertIn("system.perspective.closeDock('nav')", row)             # a selection closes the dock
        crumb = T.view_nodes(navigation.crumb())["root"]["events"]["dom"]["onClick"]["config"]["script"]
        self.assertIn("view='Framework/ASM/CrumbPopup'", crumb)
        self.assertIn("overlayDismiss=True", crumb)                           # an outside click closes it
        self.assertIn("event.clientX", crumb)                                 # beneath the crumb that was clicked
        self.assertIn("system.perspective.closePopup(p.close)", row)           # a row closes the popup it names (`close`)


class SearchTests(unittest.TestCase):
    TAGS = {"name": "t", "tagType": "Folder", "tags": [
        {"name": "P1", "tagType": "Folder", "tags": [
            {"name": "state", "tagType": "AtomicTag", "documentation": "Run state"},
            {"name": "fault", "tagType": "AtomicTag", "alarms": [{"name": "Fault"}]},
            {"name": "cfg", "tagType": "Folder", "tags": [{"name": "limit", "tagType": "AtomicTag", "engUnit": "A"}]}]},
        {"name": "orphan", "tagType": "AtomicTag", "documentation": "Not a device member"},
        {"name": "bare", "tagType": "AtomicTag"}]}

    def index(self):
        descs = [{"schema": "x", "screen": {"id": "A", "route": "/a", "title": "Area A", "view": "S/A", "layout": "diagram",
                                            "node": "Site/Area A", "level": "Level 2 unit"},
                  "tagRoot": "[default]t", "symbols": [{"id": "P1", "kind": "pump", "x": 0, "y": 0, "w": 48, "h": 48,
                                                        "device": True, "label": "Feed pump"}]}]
        idx = screen.device_index(descs)
        return navigation.search_index(descs, self.TAGS, idx, trends=True), idx

    def test_the_index_is_compact_and_comes_from_the_tag_model(self):
        index, idx = self.index()
        self.assertEqual(index["pages"], [["/a", "Area A", "Site/Area A", "Level 2 unit"], ["/alerts", "Alerts", "", ""],
                                          ["/trends", "Trends", "", ""]])
        self.assertEqual(index["devices"], [["[default]t/P1", "pump", "P1", "Feed pump", "/a", "Site/Area A", 1]])
        self.assertEqual(index["tags"], [["t/P1/state", "Run state", "", 0, "home"], ["t/P1/fault", "", "", 0, "alarms"],
                                         ["t/P1/cfg/limit", "", "A", 0, "config"], ["t/orphan", "Not a device member", "", -1, "home"]])
        big = {"name": "t", "tagType": "Folder", "tags": [{"name": f"Dev{i}", "tagType": "Folder", "tags": [
            {"name": f"member{j}", "tagType": "AtomicTag", "documentation": f"Device {i} member {j} description",
             "engUnit": "kPa"} for j in range(10)]} for i in range(40)]}   # 400 tags
        devices = [{"folder": f"[default]t/Dev{i}", "kind": "pump", "title": f"Dev{i}", "label": ""} for i in range(40)]
        sized = navigation.search_index([], big, devices)
        self.assertEqual(len(sized["tags"]), 400)
        self.assertLess(len(json.dumps(sized["tags"])), 40000)                   # about 80 bytes a tag in a session

    def rows(self, query, index=None):
        ns, _ = frame_ns()
        s = types.SimpleNamespace(custom=types.SimpleNamespace(searchIndex=json.loads(json.dumps(index or self.index()[0]))))
        return ns["search"](s, query), ns, s

    def test_groups_and_ranks(self):
        index = {"pages": [["/p", "Pump station", "Site", ""], ["/pp", "Overview", "Pump area", ""], ["/x", "P1", "", ""]],
                 "devices": [["[default]t/XP1", "pump", "XP1", "", "/p", "Site", 1], ["[default]t/P1", "pump", "P1", "", "/p", "Site", 1],
                             ["[default]t/P10", "pump", "P10", "", "/p", "Site", 1]],
                 "tags": [["t/P1/state", "", "", 1, "home"]]}
        rows, _, _ = self.rows("p1", index)
        self.assertEqual([(r["kind"], r["label"]) for r in rows],
                         [("group", "Pages"), ("page", "P1"), ("group", "Devices"), ("device", "P1"), ("device", "P10"),
                          ("device", "XP1"), ("group", "Tags"), ("tag", "state")])      # exact, prefix, substring
        self.assertEqual(self.rows("", index)[0], [])
        rows, _, _ = self.rows("PUMP", index)                                        # case-insensitive
        self.assertEqual([r["label"] for r in rows if r["kind"] == "page"], ["Pump station", "Overview"])

    def test_at_most_thirty_rows(self):
        index = {"pages": [[f"/x{i}", f"Page x{i}", "", ""] for i in range(60)],
                 "devices": [[f"[default]t/x{i}", "pump", f"x{i}", "", "/x0", "", 1] for i in range(60)],
                 "tags": [[f"t/x{i}/m", f"x tag {i}", "", 0, "home"] for i in range(60)]}
        rows, _, _ = self.rows("x", index)
        self.assertLessEqual(len(rows), 30)
        self.assertEqual([r["label"] for r in rows if r["kind"] == "group"], ["Pages", "Devices", "Tags"])

    def test_the_actions(self):
        rows, ns, s = self.rows("p1")
        dev = [r for r in rows if r["kind"] == "device"][0]
        self.assertEqual((dev["route"], dev["deviceId"], dev["deviceKind"], dev["tab"], dev["close"]),
                         ("/a", "[default]t/P1", "pump", "home", "search"))       # its page, and its faceplate on Home
        tags = {r["label"]: r for r in rows if r["kind"] == "tag"}
        self.assertEqual((tags["fault"]["tab"], tags["fault"]["deviceId"], tags["fault"]["route"]), ("alarms", "[default]t/P1", "/a"))
        self.assertEqual(tags["limit"]["tab"], "config")
        rows, _, _ = self.rows("orphan")
        self.assertTrue(all(r["disabled"] for r in rows if r["kind"] == "tag"))      # no device to go to
        # a device without a faceplate opens its page only
        index = {"pages": [], "devices": [["[default]t/Z", "readout", "Z", "", "/a", "", 0]], "tags": []}
        rows, _, _ = self.rows("z", index)
        self.assertEqual((rows[1]["deviceId"], rows[1]["route"]), ("", "/a"))
        first = ns["search_first"](s, "p1")
        self.assertEqual((first["kind"], first["label"]), ("device", "P1"))   # the first row that acts, not a group title
        self.assertIsNone(ns["search_first"](s, "qqqq"))

    def test_the_field_opens_no_popup_and_enter_acts_through_the_shared_opener(self):
        top = navigation.top_bar()
        f = T.view_nodes(top)["SearchField"]
        self.assertEqual((f["position"]["basis"], f["props"]["placeholder"]), ("300px", "Search pages, devices, tags"))
        self.assertEqual(f["propConfig"]["props.text"]["binding"]["config"], {"path": "session.custom.searchQuery", "bidirectional": True})
        self.assertIs(f["props"]["deferUpdates"], False)                     # the query follows each key
        self.assertIs(f["props"]["rejectUpdatesWhileFocused"], False)
        click = f["events"]["dom"]["onClick"]["config"]["script"]
        self.assertNotIn("Framework/ASM/SearchResults", click)              # a popup took the keyboard focus (measured)
        self.assertIn("self.session.custom.searchOpen = True", click)       # a click reopens the panel where a query is left
        keys = f["events"]["dom"]["onKeyDown"]["config"]["script"]
        self.assertNotIn("Framework/ASM/SearchResults", keys)
        self.assertNotIn("closePopup('search", keys)
        self.assertIn("k == 'Escape'", keys)
        self.assertIn("self.session.custom.searchOpen = False", keys)
        self.assertIn("cadre.hmi.search_first(self.session, self.session.custom.searchQuery)", keys)
        self.assertIn("cadre.hmi.select_device(self.session, r['deviceId'], r['deviceKind'], r['deviceTitle'], r['deviceLabel'], r['tab'], local=r['deviceLocal'])", keys)
        self.assertIn("\telse:\n\t\tself.session.custom.searchOpen = True", keys)   # any other key opens the panel
        compile("def f(self, event):\n" + keys + "\n", "keys", "exec")

    def test_keys_run_as_the_field_would(self):
        """Run the field's key script against a fake session: a letter opens the panel, Enter acts on the first row and
        closes it with the query cleared, Escape clears and closes."""
        _, descs = wtp_descs()
        keys = T.view_nodes(navigation.top_bar())["SearchField"]["events"]["dom"]["onKeyDown"]["config"]["script"]
        ns, _ = frame_ns()
        seen = []

        class Persp:
            @staticmethod
            def navigate(route):
                seen.append(("navigate", route))

            @staticmethod
            def closeDock(id=None):
                seen.append(("closeDock", id))

            @staticmethod
            def closePopup(id=None):
                seen.append(("closePopup", id))

            @staticmethod
            def openDock(id=None):
                seen.append(("openDock", id))
        scope = dict(ns)
        scope["system"] = types.SimpleNamespace(perspective=Persp)
        scope["cadre"] = types.SimpleNamespace(hmi=types.SimpleNamespace(
            search_first=lambda session, q: ns["search_first"](session, q),
            select_device=lambda *a, **k: seen.append(("select", a[1]))))
        exec("def f(self, event):\n" + "".join("\t" + ln + "\n" for ln in keys.split("\n")), scope)

        def press(session, key):
            scope["f"](types.SimpleNamespace(session=session), types.SimpleNamespace(key=key))
        s = session_of(descs, searchQuery="p301", searchOpen=False, faceplateMode="dock", faceplateDocked=False, searchIndex=navigation.search_index(
            descs, None, screen.device_index(descs)))
        press(s, "p")
        self.assertTrue(s.custom.searchOpen)                                  # a letter opens the panel
        press(s, "Enter")
        self.assertEqual(seen[0], ("navigate", "/filtration"))                # the first row that acts: the device's page
        self.assertIn(("select", "[default]cadre_hmi_wtp/P301"), seen)       # and its faceplate
        self.assertEqual((s.custom.searchOpen, s.custom.searchQuery), (False, ""))
        s.custom.searchQuery, s.custom.searchOpen = "zzzz", True
        press(s, "Enter")                                                     # no row: the panel stays, saying so
        self.assertTrue(s.custom.searchOpen)
        press(s, "Escape")
        self.assertEqual((s.custom.searchOpen, s.custom.searchQuery), (False, ""))
        self.assertFalse([x for x in seen if x[0] == "closePopup"])           # no popup is closed

    def test_the_results_panel_is_a_view_in_the_page(self):
        v = navigation.search_results()
        n = T.view_nodes(v)
        self.assertEqual(v["custom"], {"rows": []})
        cfg = json.dumps(v["propConfig"]["custom.rows"])
        self.assertIn("cadre.hmi.search(self.session, value)", cfg)
        self.assertIn("{session.custom.searchOpen}", cfg)                      # a closed panel costs no search
        self.assertEqual(n["Panel"]["position"], {"basis": "420px", "shrink": 0})
        self.assertEqual(n["PanelRow"]["children"][-1]["meta"]["name"], "Panel")   # the panel at the right
        for name in ("ScrimLeft", "ScrimBelow"):                               # a click on the page outside the panel closes it
            self.assertEqual(n[name]["events"]["dom"]["onClick"]["config"]["script"], "\tself.session.custom.searchOpen = False")
        self.assertEqual(n["Rows"]["props"]["path"], "Framework/ASM/ListRow")
        row = handler_scripts(navigation.list_row())[0][2]
        self.assertIn("elif p.close == 'search':\n\t\t\tself.session.custom.searchQuery = ''\n\t\t\tself.session.custom.searchOpen = False", row)
        self.assertNotIn("closePopup('search')", row)                          # a row of the panel closes the panel

    def test_every_page_root_carries_the_panel_out_of_the_flow(self):
        from hmi import framework
        panel = navigation.search_panel()
        self.assertEqual(panel["props"]["path"], "Framework/ASM/SearchResults")
        st = panel["props"]["style"]
        self.assertEqual((st["position"], st["top"], st["right"], st["left"], st["bottom"]), ("absolute", "0px", "0px", "0px", "0px"))
        shown = panel["propConfig"]["position.display"]["binding"]["config"]["expression"]
        self.assertIn("{session.custom.searchOpen}", shown)
        self.assertIn("len(coalesce({session.custom.searchQuery}, '')) > 0", shown)
        for name, doc in (("NodeAlarms", navigation.node_alarms()), ("NodeTrend", navigation.node_trend()),
                          ("AlertsPage", framework.alerts_page()), ("TrendsPage", framework.trends_page())):
            kids = doc["root"]["children"]
            self.assertEqual(kids[-1]["meta"]["name"], "SearchPanel", name)    # the last child: above the others
            self.assertEqual(kids[-1]["props"]["path"], "Framework/ASM/SearchResults", name)

    def test_diagram_and_stub_pages_carry_the_panel_in_the_asm_frame_only(self):
        _, descs = wtp_descs()
        stub = {"schema": "x", "screen": {"id": "Stub", "route": "/stub", "title": "Stub", "view": "Screens/Stub",
                                          "layout": "cards", "width": 1600, "height": 800}, "tagRoot": "[default]t", "rows": []}
        views = [d["screen"]["view"] for d in descs[:1]] + ["Screens/Stub"]
        for frame, want in (("asm", True), ("openbridge", False)):
            child, _ = screen.build_child("cadre_hmi_t", copy.deepcopy(descs) + [stub], "T", frame=frame)
            for view in views:
                doc = json.loads(child.files[f"com.inductiveautomation.perspective/views/{view}/view.json"].decode("utf-8"))
                names = [k["meta"]["name"] for k in doc["root"]["children"]]
                self.assertEqual("SearchPanel" in names, want, (frame, view))
                if want:
                    self.assertEqual(names[-1], "SearchPanel")


class PageHeaderTests(unittest.TestCase):
    def setUp(self):
        _, self.descs = wtp_descs()
        self.s = session_of(self.descs)
        self.ns, _ = frame_ns()

    def test_title_level_pivot_tabs_and_neighbours(self):
        h = self.ns["page_header"](self.s, "/intake")
        self.assertEqual((h["title"], h["level"], h["nodeId"], h["mode"], h["mimicRoute"]), ("Intake and Clarification", "Level 2 unit", "n3", "mimic", "/intake"))
        self.assertEqual(h["previous"], {"route": "/", "title": "Plant Overview", "enabled": True})
        self.assertEqual(h["next"], {"route": "/filtration", "title": "Filtration", "enabled": True})
        self.assertEqual(h["tabs"], [])                                      # one page: no tabs
        h = self.ns["page_header"](self.s, "/")
        self.assertEqual(h["previous"], {"route": "", "title": "", "enabled": False})      # disabled where none
        self.assertEqual(self.ns["page_header"](self.s, "/disinfection")["next"]["enabled"], False)

    def test_page_tabs_where_a_node_has_several_pages(self):
        h = copy.deepcopy(self.s.custom.hierarchy)
        h[0]["pages"].append({"label": "Overview (2)", "route": "/two"})
        self.s.custom.hierarchy = h
        got = self.ns["page_header"](self.s, "/two")
        self.assertEqual([(t["label"], t["selected"]) for t in got["tabs"]], [("Plant Overview", False), ("Overview (2)", True)])

    def test_the_pivot_pages_follow_the_content_node(self):
        self.s.custom.contentNode = "n2"
        h = self.ns["page_header"](self.s, "/node/alarms")
        self.assertEqual((h["title"], h["mode"], h["nodeId"], h["level"], h["tabs"]), ("Filtration alarms", "alarms", "n2", "", []))
        self.assertEqual(self.ns["page_header"](self.s, "/node/trend")["mode"], "trend")
        h = self.ns["page_header"](self.s, "/alerts")                        # a page of no node: no pivot
        self.assertEqual((h["nodeId"], h["title"], h["mimicRoute"]), ("", "Alerts", ""))

    def test_the_view(self):
        v = navigation.page_header()
        self.assertEqual(v["props"]["defaultSize"]["height"], 36)
        n = T.view_nodes(v)
        self.assertIn("cadre.hmi.page_header(self.session", json.dumps(v["propConfig"]["custom.head"]))
        for mode, route in (("alarms", "/node/alarms"), ("trend", "/node/trend")):
            code = n[f"Pivot_{mode}"]["events"]["component"]["onActionPerformed"]["config"]["script"]
            self.assertIn("self.session.custom.contentNode = self.view.custom.head.nodeId", code)
            self.assertIn(f"navigate('{route}')", code)
        self.assertEqual(n["Previous"]["propConfig"]["props.enabled"]["binding"]["config"]["expression"],
                         "{view.custom.head.previous.enabled}")
        self.assertEqual(n["Pivot"]["propConfig"]["position.display"]["binding"]["config"]["expression"],
                         "len({view.custom.head.nodeId}) > 0")

    def test_the_pivot_pages(self):
        self.s.custom.contentNode = "n2"
        ns, _ = frame_ns()
        sources = ns["node_sources"](self.s, "n2").split(",")
        self.assertIn("prov:default:/tag:cadre_hmi_wtp/P301/*", sources)     # the node's own devices
        self.assertNotIn("prov:default:/tag:cadre_hmi_wtp/P101/*", sources)  # not another node's
        self.assertEqual(ns["node_sources"](types.SimpleNamespace(custom=types.SimpleNamespace(hierarchy=[], devices=[])), "n9"),
                         ns["NO_MATCH"])                                       # never the whole scope
        self.assertEqual([t["deviceId"] for t in ns["node_trends"](self.s, "n0", 8)],
                         ["[default]cadre_hmi_wtp/P301", "[default]cadre_hmi_wtp/P101"])
        self.assertEqual([t["hours"] for t in ns["node_trends"](self.s, "n0", 8)], [8, 8])
        self.assertEqual([t["deviceId"] for t in ns["node_trends"](self.s, "n2", 1)], ["[default]cadre_hmi_wtp/P301"])
        self.assertIn("node_sources", json.dumps(navigation.node_alarms()["root"]))
        self.assertEqual(navigation.page_config("A", {})["pages"]["/node/trend"]["viewPath"], "Framework/ASM/NodeTrend")


class BannerTests(unittest.TestCase):
    def test_the_three_most_important_alarms_and_the_counts(self):
        Ev = T.AlarmListTests.Event
        events = [Ev("P301", "Low", 5), Ev("XV301", "Critical", 2, acked=3), Ev("P101", "High", 4), Ev("P502", "Medium", 9),
                  Ev("P102", "High", 1, cleared=2)]
        ns, calls = frame_ns(events)
        _, descs = wtp_descs()
        s = session_of(descs)
        got = ns["banner_alarms"](s)
        # unacknowledged first (a cleared, unacknowledged alarm included), then priority, then newest
        self.assertEqual([(r["tag"], r["state"]) for r in got["rows"]],
                         [("P-101", "Unacknowledged"), ("P102", "Cleared, unacknowledged"), ("P-502", "Unacknowledged")])
        self.assertEqual(got["rows"][0]["status"], "alarm")
        self.assertEqual(got["rows"][2]["status"], "warning")
        self.assertEqual((got["rows"][0]["time"], got["rows"][0]["node"], got["rows"][0]["text"]), ("t4", "Intake", "P101 Fault"))
        self.assertTrue(all(r["unacked"] for r in got["rows"]))
        c = got["counts"]                                                       # the active alarms, by priority
        self.assertEqual((c["Critical"], c["High"], c["Medium"], c["Low"], c["total"], c["unacked"]), (1, 1, 1, 1, 4, 3))
        self.assertEqual(len([x for x in calls if x[0] == "query"]), 1)
        self.assertEqual(calls[0][1], ["*cadre_hmi_wtp*"])
        # the row opens the device's faceplate: its identity comes from the device index
        self.assertEqual(got["rows"][0]["deviceId"], "[default]cadre_hmi_wtp/P101")
        self.assertEqual(got["rows"][0]["deviceKind"], "pump")

    def test_an_acknowledged_alarm_comes_after_the_unacknowledged_and_an_empty_scope_answers_nothing(self):
        Ev = T.AlarmListTests.Event
        ns, _ = frame_ns([Ev("P301", "Critical", 5, acked=6), Ev("P101", "Diagnostic", 1)])
        _, descs = wtp_descs()
        got = ns["banner_alarms"](session_of(descs))
        self.assertEqual([(r["tag"], r["status"], r["state"]) for r in got["rows"]],
                         [("P-101", "neutral", "Unacknowledged"), ("P-301", "critical", "Acknowledged")])
        ns, _ = frame_ns([])
        self.assertEqual(ns["banner_alarms"](session_of(descs))["rows"], [])

    def test_the_view_and_its_row(self):
        v = navigation.alarm_banner()
        self.assertEqual(v["props"]["defaultSize"]["height"], 76)
        n = T.view_nodes(v)
        self.assertEqual(n["Rows"]["props"]["path"], "Framework/ASM/BannerRow")
        self.assertEqual(n["Rows"]["props"]["elementPosition"]["basis"], "24px")   # three rows in 76 px
        self.assertIn("navigate('/node/alarms')", n["AllAlarms"]["events"]["component"]["onActionPerformed"]["config"]["script"])
        row = navigation.banner_row()
        r = T.view_nodes(row)
        code = r["root"]["events"]["dom"]["onClick"]["config"]["script"]
        self.assertIn("cadre.hmi.select_device(self.session, p.deviceId, p.deviceKind, p.deviceTitle, p.deviceLabel, 'alarms', local=p.deviceLocal)",
                      code)   # the shared opener, on Alarms (the tab through select_device, COB-158)
        flashing = [k for k in r if k.startswith("Priority_")]
        self.assertEqual(len(flashing), 5)
        self.assertIn("cadre/alert/flash-", json.dumps(r["Priority_alarm"]["propConfig"]))
        self.assertEqual(set(row["params"]), set(navigation.BANNER_ROW_PARAMS))


class ShapeTests(unittest.TestCase):
    """The lists a script answers carry exactly the parameters of the view that draws each item, so that a
    renamed field fails here and not on the glass."""

    def test_each_list_matches_the_parameters_of_its_row_view(self):
        _, descs = wtp_descs()
        s = session_of(descs, searchIndex=navigation.search_index(descs, None, screen.device_index(descs)))
        ns, _ = frame_ns([T.AlarmListTests.Event("P301", "High", 1)])
        rows = (ns["nav_tree"](s, "", "/") + ns["nav_footer"](s, "/") + ns["crumb_menu"](s, "n0") + ns["search"](s, "p301"))
        self.assertGreater(len(rows), 15)
        for r in rows:
            self.assertEqual(set(r), set(navigation.ROW_PARAMS), r)
        self.assertEqual(set(navigation.list_row()["params"]), set(navigation.ROW_PARAMS))
        for c in ns["frame_crumbs"](s, "/filtration"):
            self.assertEqual(set(c), set(navigation.crumb()["params"]))
        head = ns["page_header"](s, "/intake")
        self.assertEqual(set(head), set(navigation.HEAD_DEFAULT))
        self.assertEqual(set(head["previous"]), set(navigation.HEAD_DEFAULT["previous"]))
        banner = ns["banner_alarms"](s)
        self.assertEqual(set(banner), set(navigation.BANNER_DEFAULT))
        for r in banner["rows"]:
            self.assertEqual(set(r), set(navigation.BANNER_ROW_PARAMS))
        self.assertEqual(set(banner["counts"]), set(navigation.BANNER_DEFAULT["counts"]))
        h = ns["page_header"](s, "/")
        for t in h["tabs"]:
            self.assertEqual(set(t), set(navigation.page_tab()["params"]))


class BuildTests(unittest.TestCase):
    """The option: default unchanged, `--frame asm` writes the ASM docks and the data the views read."""

    @classmethod
    def setUpClass(cls):
        cls.wtp, cls.descs = wtp_descs()
        cls.tags = cls.wtp.tag_model()

    def custom(self, child):
        return json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])["custom"]

    def pageconfig(self, child):
        return json.loads(child.files["com.inductiveautomation.perspective/page-config/config.json"])

    def test_the_default_frame_is_unchanged(self):
        child, _ = screen.build_child("cadre_hmi_t", copy.deepcopy(self.descs), "T", tag_model=self.tags)
        self.assertEqual(self.pageconfig(child), json.loads(json.dumps(par.page_config("T", {
            r: {"title": p["title"], "viewPath": p["viewPath"]} for r, p in self.pageconfig(child)["pages"].items()
            if r != "/alerts"}))))
        c = self.custom(child)
        self.assertEqual((c["frame"], c["pageInfo"], c["searchIndex"], c["contentNode"]), ("openbridge", {}, {}, ""))
        docks = self.pageconfig(child)["sharedDocks"]
        self.assertEqual([d["viewPath"] for d in docks["top"]], ["Framework/TopBar"])
        self.assertNotIn("bottom", docks)
        with self.assertRaises(ValueError):
            screen.build_child("cadre_hmi_t", copy.deepcopy(self.descs), "T", frame="elegant")

    def test_the_asm_frame_writes_its_docks_and_data(self):
        child, _ = screen.build_child("cadre_hmi_t", copy.deepcopy(self.descs), "T", tag_model=self.tags, frame="asm")
        pc = self.pageconfig(child)
        docks = pc["sharedDocks"]
        self.assertEqual([(d["viewPath"], d["size"], d["show"]) for d in docks["top"]],
                         [("Framework/ASM/Head", 84, "visible")])   # one dock a side shows: both rows in one
        self.assertEqual(docks["top"][0]["viewParams"]["appName"], "T")
        self.assertEqual([(d["id"], d["viewPath"], d["size"], d["modal"], d["content"]) for d in docks["left"]],
                         [("nav", "Framework/ASM/NavDock", 320, True, "cover")])
        self.assertEqual([(d["id"], d["viewPath"], d["size"]) for d in docks["right"]], [("faceplate", "Framework/SideMenu", 400)])
        self.assertEqual([(d["viewPath"], d["size"], d["show"]) for d in docks["bottom"]],
                         [("Framework/ASM/AlarmBanner", 76, "visible")])
        self.assertIn("/node/alarms", pc["pages"])
        c = self.custom(child)
        self.assertEqual(c["frame"], "asm")
        self.assertEqual(c["pageInfo"]["/intake"], {"title": "Intake and Clarification", "level": "Level 2 unit", "previous": "/",
                                                    "previousTitle": c["pageInfo"]["/"]["title"], "next": "/filtration",
                                                    "nextTitle": "Filtration"})
        idx = c["searchIndex"]
        self.assertEqual(len(idx["devices"]), len(c["devices"]))
        routes = {d[0].rsplit("/", 1)[-1]: d[4] for d in idx["devices"]}
        self.assertEqual((routes["P301"], routes["P101"]), ("/filtration", "/intake"))   # the deepest page that draws it
        self.assertGreater(len(idx["tags"]), 100)
        self.assertEqual(sorted(p[0] for p in idx["pages"]), ["/", "/alerts", "/disinfection", "/filtration", "/intake", "/trends"])

    def test_previous_and_next_name_pages_of_the_set(self):
        bad = copy.deepcopy(self.descs)
        bad[1]["screen"]["next"] = "/nowhere"
        with self.assertRaises(ValueError) as e:
            screen.build_child("cadre_hmi_t", bad, "T", frame="asm")
        self.assertIn("/nowhere", str(e.exception))
        self.assertEqual(navigation.frame_errors(self.descs), [])

    def test_the_descriptor_schema_takes_the_keys(self):
        self.assertEqual(screen.schema_errors(self.descs, ["a", "b", "c", "d"]), [])
        bad = copy.deepcopy(self.descs[:1])
        bad[0]["screen"]["next"] = "intake"
        bad[0]["screen"]["level"] = 2
        errors = screen.schema_errors(bad, ["a"])
        self.assertEqual(len(errors), 2)

    def test_gates_pass_on_a_sample_in_both_frames(self):
        for frame in ("openbridge", "asm"):
            with tempfile.TemporaryDirectory() as d:
                base = par.build_parent()[0].write(Path(d))
                child, reports = screen.build_child("cadre_hmi_t", copy.deepcopy(self.descs), "T", tag_model=self.tags, frame=frame)
                out = child.write(Path(d))
                res = gates.run(out, base, tag_model=self.tags)
                self.assertTrue(res["ok"], (frame, {k: v for k, v in res.items() if isinstance(v, dict) and not v.get("ok", True)}))
                self.assertFalse(any(v["errors"] for v in reports.values()))

    def test_the_parent_carries_the_views_and_every_script_parses(self):
        prj, contracts = par.build_parent()
        for path, doc in navigation.views().items():
            self.assertIn(path, contracts)
            self.assertIn(f"com.inductiveautomation.perspective/views/{path}/view.json", prj.files)
            for name, ev, code in handler_scripts(doc):
                compile("def f(self, event):\n" + code + "\n", f"{path}/{name}.{ev}", "exec")
        with tempfile.TemporaryDirectory() as d:
            base = prj.write(Path(d))
            defined = gates.library_names(base)["hmi"]
        for fn in ("float_id", "float_slot", "float_position", "float_params", "asm_frame", "frame_crumbs", "crumb_menu",
                   "nav_tree", "nav_footer", "page_header", "node_sources", "node_trends", "search", "search_first",
                   "banner_alarms"):
            self.assertIn(fn, defined)
        self.assertEqual(par.session_defaults()["custom"]["frame"], "openbridge")

    def test_the_top_bar_is_the_librarys_with_the_trail_and_the_field(self):
        from hmi import framework
        plain, asm = T.view_nodes(framework.top_bar()), T.view_nodes(navigation.top_bar())
        self.assertEqual(asm["Crumbs"]["props"]["path"], "Framework/ASM/Crumb")
        self.assertEqual(plain["Crumbs"]["props"]["path"], "Framework/Crumb")
        for kept in ("MenuButton", "AlertMessage", "AlertButton", "BrillianceButton", "UserButton", "Clock"):
            self.assertIn(kept, asm)
        names = [k["meta"]["name"] for k in navigation.top_bar()["root"]["children"]]
        self.assertLess(names.index("SearchField"), names.index("AlertMessage"))
        self.assertIn("cadre.hmi.frame_crumbs(self.session", json.dumps(navigation.top_bar()["propConfig"]["custom.crumbs"]))
        self.assertIn("SiteNote", asm)


if __name__ == "__main__":
    unittest.main()


class HeadAndBannerLayoutTests(unittest.TestCase):
    """The two defects of the first gateway run (2026-10-24): a second top dock never showed, and the banner's rows
    sat at the banner's middle with no height."""

    def test_the_head_holds_the_top_bar_above_the_page_header(self):
        v = navigation.head()
        kids = v["root"]["children"]
        self.assertEqual([(k["props"]["path"], k["position"]["basis"]) for k in kids],
                         [("Framework/ASM/TopBar", "48px"), ("Framework/ASM/PageHeader", "36px")])
        self.assertEqual(v["props"]["defaultSize"]["height"], 84)
        self.assertEqual(set(v["params"]), set(navigation.top_bar()["params"]))
        for k in v["params"]:
            self.assertEqual(kids[0]["propConfig"][f"props.params.{k}"]["binding"]["config"]["expression"],
                             "{view.params.%s}" % k)
        self.assertIn("Framework/ASM/Head", navigation.views())

    def test_the_banner_rows_take_the_banners_height(self):
        left = next(c for c in navigation.alarm_banner()["root"]["children"] if c["meta"]["name"] == "Left")
        self.assertEqual(left["position"]["align"], "stretch")



class FramePopupsAndNavigationPanelTests(unittest.TestCase):
    """L4: every frame popup opens modal so that a click outside closes it (a non-modal popup stays open whatever its
    `overlayDismiss`, measured 2026-10-24); one left dock in two states; the menu button opens the tree only."""

    def test_every_frame_popup_opens_modal_with_overlay_dismiss(self):
        from hmi import framework
        opened = []
        for doc in (framework.top_bar(), navigation.top_bar(), navigation.crumb(), navigation.head()):
            for name, ev, code in handler_scripts(doc):
                for line in code.split("\n"):
                    if "openPopup" in line and "Faceplate" not in line:   # (a floating faceplate is not modal: it stays beside the page)
                        opened.append((name, line))
        ids = sorted(set(re.search(r"openPopup\((?:id=)?'(\w+)'", line).group(1) for _, line in opened))
        self.assertEqual(ids, ["alertMenu", "brilliance", "crumbPopup", "userMenu"])
        for name, line in opened:
            self.assertIn("modal=True, overlayDismiss=True", line, name)
            self.assertNotIn("modal=False", line, name)
        self.assertIn("modal=True, overlayDismiss=True", navigation._popup_line("x", "V", "{}", "{}"))

    def test_the_menu_button_opens_the_tree_and_a_second_button_the_support_list(self):
        names = T.view_nodes(navigation.top_bar())
        menu = names["MenuButton"]["events"]["dom"]["onClick"]["config"]["script"]
        support = names["SupportButton"]["events"]["dom"]["onClick"]["config"]["script"]
        self.assertEqual(menu, "\tself.session.custom.navPanel = 'pages'\n\tsystem.perspective.openDock(id='nav')")
        self.assertEqual(support, "\tself.session.custom.navPanel = 'support'\n\tsystem.perspective.openDock(id='nav')")
        order = [k["meta"]["name"] for k in navigation.top_bar()["root"]["children"]]
        self.assertEqual(order[:2], ["MenuButton", "SupportButton"])           # beside each other, before the title
        self.assertTrue((ROOT / "library" / "icons" / f"{navigation.SUPPORT_ICON}.json").exists())   # one of the 92 icons
        self.assertEqual(len([d for d in navigation.shared_docks("T")["left"]]), 1)   # one dock of the edge (GF-90)
        self.assertEqual(par.session_defaults()["custom"]["navPanel"], "pages")
        self.assertIs(par.session_defaults()["custom"]["searchOpen"], False)

    def test_the_default_frame_keeps_its_toggle(self):
        from hmi import framework
        menu = T.view_nodes(framework.top_bar())["MenuButton"]["events"]["dom"]["onClick"]
        self.assertEqual(menu["config"], {"id": "nav", "type": "toggle"})
        self.assertNotIn("SupportButton", T.view_nodes(framework.top_bar()))

    def test_the_dock_shows_the_tree_or_the_support_list_and_has_no_footer(self):
        n = T.view_nodes(navigation.nav_dock())
        self.assertNotIn("Footer", n)
        self.assertNotIn("Divider", n)
        pages = "coalesce({session.custom.navPanel}, 'pages') != 'support'"
        support = "coalesce({session.custom.navPanel}, 'pages') = 'support'"
        shown = lambda name: n[name]["propConfig"]["position.display"]["binding"]["config"]["expression"]
        self.assertEqual((shown("Search"), shown("Tree"), shown("Support")), (pages, pages, support))
        self.assertIn("cadre.hmi.nav_support(self.session", json.dumps(n["Support"]["propConfig"]["props.instances"]))
        self.assertIn("'Tools and support'", n["Title"]["propConfig"]["props.text"]["binding"]["config"]["expression"])
        self.assertEqual(n["Support"]["props"]["path"], "Framework/ASM/ListRow")

    def test_the_support_list_holds_all_alarms_trends_and_alerts(self):
        _, descs = wtp_descs()
        s = session_of(descs)
        ns, _ = frame_ns()
        rows = ns["nav_support"](s, "/trends")
        self.assertEqual([(r["label"], r["action"], r["close"]) for r in rows],
                         [("All alarms", "alarms", "nav"), ("Trends", "route", "nav"), ("Alerts", "route", "nav")])
        self.assertEqual([r["selected"] for r in rows], [False, True, False])
        self.assertEqual(rows[0]["nodeId"], "")                                # the Alarms page of the root
        self.assertEqual([r["label"] for r in ns["nav_tree"](s, "", "/")][:2], ["WTP", "Plant Overview"])   # the tree has no support rows
        self.assertNotIn("Trends", [r["label"] for r in ns["nav_tree"](s, "", "/")])

    def test_the_modal_navigation_dock_stays_modal(self):
        dock = navigation.shared_docks("T")["left"][0]
        self.assertEqual((dock["id"], dock["modal"], dock["show"]), ("nav", True, "onDemand"))

    def test_the_fit_reads_the_measured_canvas_where_the_module_gives_it(self):
        # the session's dock flag outlived a reload (the gateway keeps the page): glass, 2026-10-24
        from hmi import parts
        e = parts.fit_expression(1900, 860, {"reserveX": 0, "reserveY": 216})
        self.assertTrue(e.startswith("if(coalesce({view.custom.canvasW}, 0) > 0"))
        self.assertIn("{view.custom.canvasH} / 860.0", e)
        self.assertIn("faceplateDocked", e)   # the viewport rule stays for the stock rendering
