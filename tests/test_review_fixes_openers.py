"""Regression tests of the cold review's finding 1 (NOTE-WFB-10 section 11.2 item 5): every opener of a device passes
the device index's `local`, so that a local assembly's faceplate embeds `Local/<Kind>/Home` whichever row opened it.

Scenario: benchlocal's `alarm` raises High, the operator clicks the banner row, and the faceplate embedded
`Local//Home` because the row's opener passed no `local`. The alarm panel's row (`select_alarm_device`), the banner's
rows and the search rows (the list row's click and the search field's Enter) all opened a local device that way.

Run from the repository root:  python -m unittest discover -s tests
Nothing here needs the gateway or a browser.
"""
import re
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import local_support as L  # noqa: E402
import test_hmi as T  # noqa: E402  (helpers only: no test class is imported by name)
from test_asm_frame import frame_ns, wtp_descs  # noqa: E402

from hmi import framework, navigation, screen  # noqa: E402

KIND = "Skid"
FOLDER = f"{L.TAG_ROOT}/Skid1"
SOURCE = "prov:default:/tag:cadre_hmi_loc/Skid1/alarm:/alm:Alarm"


def descs():
    return [L.page(L.assembly("A1", device="Skid1"))]


def index():
    return screen.device_index(descs())


def local_session(**custom):
    idx = index()
    base = dict(devices=idx, hierarchy=screen.hierarchy(descs()), alarmScope="*cadre_hmi_loc*", contentNode="",
                faceplateMode="dock", faceplateDocked=False, selectedLocal="", selectedDevice="", selectedKind="",
                selectedTitle="", selectedLabel="", selectedTab="", selectedStyle="openbridge", frame="asm",
                searchQuery="", searchOpen=True, searchIndex=navigation.search_index(descs(), None, idx))
    base.update(custom)
    return types.SimpleNamespace(custom=types.SimpleNamespace(**base), props=types.SimpleNamespace())


class LocalAlarm(T.AlarmListTests.Event):
    def getSource(self):
        return SOURCE


def run_script(script, ns, session, view_params=None, event=None):
    """Run a component event script as Perspective would: `self.session`, `self.view.params`, `cadre.hmi`."""
    popups = []
    perspective = types.SimpleNamespace(
        navigate=lambda *a, **k: None, closePopup=lambda *a, **k: None, closeDock=lambda *a, **k: None,
        openDock=lambda *a, **k: None, openPopup=lambda *a, **k: popups.append((a, k)))
    env = {"cadre": types.SimpleNamespace(hmi=types.SimpleNamespace(**ns)), "system": types.SimpleNamespace(
        perspective=perspective)}
    exec("def f(self, event):\n" + script + "\n", env)
    me = types.SimpleNamespace(session=session, view=types.SimpleNamespace(params=view_params))
    env["f"](me, event)
    return popups


def script_of(node):
    return node["events"]["dom"]["onClick"]["config"]["script"]


class IndexTests(unittest.TestCase):
    def test_the_device_index_holds_the_local_kind_of_a_local_device(self):
        self.assertEqual([e.get("local") for e in index() if e["folder"] == FOLDER], [KIND])


class AlarmPanelTests(unittest.TestCase):
    def test_the_alarm_panels_row_click_selects_the_local_kind_of_the_device(self):
        ns, _ = frame_ns()
        s = local_session()
        got = ns["select_alarm_device"](s, {"tagId": FOLDER})
        self.assertTrue(got)
        self.assertEqual((s.custom.selectedDevice, s.custom.selectedKind, s.custom.selectedLocal),
                         (FOLDER, "local", KIND))

    def test_the_alarm_panels_row_click_of_a_library_device_clears_the_local_kind(self):
        ns, _ = frame_ns()
        pump = {"folder": f"{L.TAG_ROOT}/P1", "kind": "pump", "title": "P-1", "label": "", "unit": ""}
        s = local_session(devices=[pump, *index()], selectedLocal=KIND)
        self.assertTrue(ns["select_alarm_device"](s, {"tagId": pump["folder"]}))
        self.assertEqual(s.custom.selectedLocal, "")


class BannerTests(unittest.TestCase):
    def rows(self):
        ns, _ = frame_ns([LocalAlarm("Skid1", "High", 5)])
        s = local_session()
        return ns, s, ns["banner_alarms"](s)["rows"]

    def test_a_banner_row_of_a_local_device_carries_its_local_kind(self):
        _, _, rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["deviceId"], FOLDER)
        self.assertEqual(rows[0].get("deviceLocal"), KIND)
        self.assertEqual(set(rows[0]), set(navigation.BANNER_ROW_PARAMS))

    def test_a_banner_row_of_a_library_device_carries_an_empty_local_kind(self):
        ns, _ = frame_ns([T.AlarmListTests.Event("P301", "High", 1)])
        _wtp, wdescs = wtp_descs()
        s = local_session(devices=screen.device_index(wdescs), hierarchy=screen.hierarchy(wdescs),
                          alarmScope="*cadre_hmi_wtp*")
        rows = ns["banner_alarms"](s)["rows"]
        self.assertEqual([r.get("deviceLocal") for r in rows], [""])

    def test_clicking_the_banner_row_of_a_local_alarm_selects_the_local_kind_for_the_faceplate(self):
        ns, s, rows = self.rows()
        run_script(script_of(navigation.banner_row()["root"]), ns, s, types.SimpleNamespace(**rows[0]))
        self.assertEqual((s.custom.selectedDevice, s.custom.selectedKind, s.custom.selectedTab),
                         (FOLDER, "local", "alarms"))
        self.assertEqual(s.custom.selectedLocal, KIND, "the dock embeds Local//Home when this is empty")

    def test_the_banner_rows_script_passes_the_rows_local_kind_to_the_opener(self):
        script = script_of(navigation.banner_row()["root"])
        self.assertRegex(script, r"select_device\(self\.session, p\.deviceId, [^\n]*,\s*local\s*=\s*p\.deviceLocal\)")
        self.assertIn("deviceLocal", navigation.BANNER_ROW_PARAMS)


class SearchTests(unittest.TestCase):
    def device_row(self):
        ns, _ = frame_ns()
        s = local_session()
        rows = [r for r in ns["search"](s, "skid") if r["kind"] == "device"]
        self.assertEqual(len(rows), 1, rows)
        return ns, s, rows[0]

    def test_a_search_row_of_a_local_device_carries_its_local_kind(self):
        _, _, row = self.device_row()
        self.assertEqual(row["deviceId"], FOLDER)
        self.assertEqual(row.get("deviceLocal"), KIND)
        self.assertEqual(set(row), set(navigation.ROW_PARAMS))

    def test_a_search_row_of_a_library_device_carries_an_empty_local_kind(self):
        _wtp, wdescs = wtp_descs()
        ns, _ = frame_ns()
        idx = screen.device_index(wdescs)
        s = local_session(devices=idx, searchIndex=navigation.search_index(wdescs, None, idx))
        rows = [r for r in ns["search"](s, "p301") if r["kind"] == "device"]
        self.assertTrue(rows)
        self.assertEqual({r.get("deviceLocal") for r in rows}, {""})

    def test_clicking_the_search_row_of_a_local_device_selects_the_local_kind(self):
        ns, s, row = self.device_row()
        run_script(script_of(navigation.list_row()["root"]), ns, s, types.SimpleNamespace(**row))
        self.assertEqual((s.custom.selectedDevice, s.custom.selectedKind), (FOLDER, "local"))
        self.assertEqual(s.custom.selectedLocal, KIND)

    def test_enter_in_the_search_field_selects_the_local_kind_of_the_first_device(self):
        ns, s, _row = self.device_row()
        s.custom.searchQuery = "skid"
        field = navigation._search_field()
        keys = field["events"]["dom"]["onKeyDown"]["config"]["script"]
        run_script(keys, ns, s, None, types.SimpleNamespace(key="Enter"))
        self.assertEqual((s.custom.selectedDevice, s.custom.selectedKind), (FOLDER, "local"))
        self.assertEqual(s.custom.selectedLocal, KIND)

    def test_the_search_rows_scripts_pass_the_rows_local_kind_to_the_opener(self):
        click = script_of(navigation.list_row()["root"])
        self.assertRegex(click, r"select_device\(self\.session, p\.deviceId, [^\n]*,\s*local\s*=\s*p\.deviceLocal\)")
        keys = navigation._search_field()["events"]["dom"]["onKeyDown"]["config"]["script"]
        self.assertRegex(keys, r"select_device\(self\.session, r\['deviceId'\], [^\n]*,\s*local\s*=\s*r\['deviceLocal'\]\)")

    def test_the_search_index_devices_carry_the_local_kind_after_the_faceplate_flag(self):
        devices = [d for d in navigation.search_index(descs(), None, index())["devices"] if d[0] == FOLDER]
        self.assertEqual(len(devices), 1)
        self.assertEqual(len(devices[0]), 8)
        self.assertEqual((devices[0][6], devices[0][7]), (1, KIND))

    def test_a_device_that_is_no_local_assemblys_keeps_the_seven_items(self):
        _wtp, wdescs = wtp_descs()
        devices = navigation.search_index(wdescs, None, screen.device_index(wdescs))["devices"]
        self.assertTrue(devices)
        self.assertEqual({len(d) for d in devices}, {7})


class EveryOpenerTests(unittest.TestCase):
    """No opener of a device in the frame's views leaves the local kind out."""

    def test_the_alarm_menus_row_click_goes_through_select_alarm_device(self):
        doc = framework.alert_menu_module()
        text = repr(doc)
        self.assertIn("select_alarm_device", text)
        self.assertEqual(len(re.findall(r"select_device\(", text)), 0, "the row opens through the alarm opener")


if __name__ == "__main__":
    unittest.main()
