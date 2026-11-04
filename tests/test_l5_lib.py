"""Tests of the library part of eng02 ASM Level 5 (COB-165 and COB-166): the indicator coloured by state, the plain
symbol that opens a faceplate, the notification and marks drawn like the module's pump, Ack selected and Ack all, the
banner by page and the component test page.

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import library, parent as par, screen  # noqa: E402


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


def page(symbols, node="", extra=None):
    return {"screen": {"id": "T", "route": "/t", "title": "T", "view": "Screens/T", "layout": "diagram",
                       "width": 800, "height": 400, **({"node": node} if node else {})},
            "tagRoot": "[default]tst", "symbols": symbols, **(extra or {})}


class Case(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prj, cls.contracts = par.build_parent()

    def tearDown(self):
        screen.RENDER["target"] = "stock"
        screen.RENDER["devices"] = {}

    def build(self, desc, render="stock"):
        screen.RENDER["target"] = render
        doc, info = screen.build_screen(copy.deepcopy(desc), self.contracts)
        return nodes_of(doc), doc, info

    def view(self, path):
        return nodes_of(json.loads(self.prj.files[f"com.inductiveautomation.perspective/views/{path}/view.json"]))


class LampTests(Case):
    def test_the_lamp_draws_no_status_row_and_no_frame(self):
        c = self.contracts["Automation/Indicator"]["params"]
        self.assertIs(c["showStatus"], False)
        self.assertEqual(c["colour"], "")
        n = self.view("Automation/Indicator")
        self.assertFalse([k for k in n if k in ("AlertFrame", "AlertPulse") or k.startswith("Flap_")])
        self.assertIs(self.contracts["Automation/Pump"]["params"]["showStatus"], True)
        self.assertIn("AlertFrame", self.view("Automation/Pump"))

    def test_the_colour_param_fills_the_lamp_and_its_border(self):
        ring = self.view("Automation/Indicator")["Holder"]["propConfig"]
        fill = ring["props.elements[0].fill.paint"]["binding"]["config"]["expression"]
        stroke = ring["props.elements[0].stroke.paint"]["binding"]["config"]["expression"]
        self.assertTrue(fill.startswith("if(len({view.params.colour}) > 0, {view.params.colour}, "))
        self.assertTrue(stroke.startswith("if(len({view.params.colour}) > 0, {view.params.colour}, "))
        pump = self.view("Automation/Pump")["Holder"]["propConfig"]["props.elements[0].fill.paint"]
        self.assertNotIn("colour", pump["binding"]["config"]["expression"])

    def test_the_palette_maps_to_the_theme_tokens(self):
        self.assertEqual(set(library.STATE_COLOURS), {"off", "on", "active", "alarm", "warning", "caution",
                                                      "critical", "neutral"})
        self.assertEqual(library.state_paint("alarm"), "var(--alert-alarm-color)")
        self.assertEqual(library.state_paint("#12ab34"), "#12ab34")
        tokens = (ROOT / "library/tokens/openbridge-tokens.json").read_text(encoding="utf-8")
        for var in library.STATE_COLOURS.values():
            self.assertIn('"' + var[4:-1] + '"', tokens)

    def sym(self, **kw):
        return {"id": "L1", "kind": "indicator", "x": 40, "y": 40, "w": 48, "h": 48,
                "params": {"hasTag": True, "tag": "L-1"}, "bind": {"state": "gen/lamp"}, **kw}

    def test_an_embedded_symbol_lets_its_flap_show_past_its_box(self):
        # the module's flap stands outside the frame and the box (glass, 2026-10-26): the embed does not clip it
        n, doc, info = self.build(page([{"id": "P1", "kind": "pump", "x": 40, "y": 40, "w": 72, "h": 92,
                                         "params": {"hasTag": True, "tag": "P-1"}, "bind": {"on": "gen/p1"}}]))
        self.assertEqual(info["errors"], [])
        self.assertEqual(n["P1"]["props"]["style"]["overflow"], "visible")

    def test_a_three_state_lamp_reads_its_tag_once_and_colours_by_case(self):
        states = [{"value": 0, "colour": "off", "label": "Off"}, {"value": 1, "colour": "on", "label": "On"},
                  {"value": 2, "colour": "alarm", "label": "Alarm"}]
        n, doc, info = self.build(page([self.sym(states=states, stateDefault="neutral")]))
        self.assertEqual(info["errors"], [])
        lamp = n["L1"]
        self.assertEqual(expr(lamp, "props.params.colour"),
                         "case({view.custom.g_L1}, 0, 'var(--automation-button-off-background-color)', "
                         "1, 'var(--on-background-color)', 2, 'var(--alert-alarm-color)', 'var(--element-neutral-color)')")
        self.assertEqual(expr(lamp, "props.params.on"), "{view.custom.g_L1} = 1 || {view.custom.g_L1} = 2")
        self.assertNotIn("transforms", lamp["propConfig"]["props.params.colour"]["binding"])   # no script transform
        self.assertEqual(doc["propConfig"]["custom.g_L1"]["binding"]["type"], "tag")
        self.assertEqual(doc["propConfig"]["custom.g_L1"]["binding"]["config"]["tagPath"], "[default]tst/gen/lamp")
        self.assertEqual(doc["custom"]["g_L1"], 0)

    def test_a_string_state_and_a_css_paint(self):
        states = [{"value": "RUN", "colour": "#00aa00"}, {"value": "it's", "colour": "caution"}]
        n, doc, _ = self.build(page([self.sym(states=states)]))
        self.assertEqual(expr(n["L1"], "props.params.colour"),
                         "case({view.custom.g_L1}, 'RUN', '#00aa00', 'it\\'s', 'var(--alert-caution-color)', "
                         "'var(--automation-button-off-background-color)')")
        self.assertEqual(doc["custom"]["g_L1"], "")

    def test_a_boolean_lamp_without_states_keeps_its_on_and_off_colours(self):
        n, doc, _ = self.build(page([self.sym()]))
        self.assertEqual(expr(n["L1"], "props.params.on"), "{view.custom.g_L1}")
        self.assertNotIn("props.params.colour", n["L1"]["propConfig"])
        self.assertIs(doc["custom"]["g_L1"], False)
        n, _, _ = self.build(page([self.sym(bind={"on": "gen/lamp"})]))   # `on` stays accepted
        self.assertEqual(expr(n["L1"], "props.params.on"), "{view.custom.g_L1}")

    def test_a_boolean_state_with_states(self):
        n, _, _ = self.build(page([self.sym(states=[{"value": True, "colour": "warning"},
                                                    {"value": False, "colour": "off"}])]))
        self.assertEqual(expr(n["L1"], "props.params.colour"),
                         "case({view.custom.g_L1}, true, 'var(--alert-warning-color)', false, "
                         "'var(--automation-button-off-background-color)', 'var(--automation-button-off-background-color)')")

    def test_the_readout_toggle_and_the_alert_do_not_reach_a_lamp(self):
        n, doc, _ = self.build(page([self.sym(device=True)]))
        self.assertNotIn("props.params.showStatus", n["L1"]["propConfig"])
        self.assertIn("props.params.hasTag", n["L1"]["propConfig"])
        self.assertNotIn("alerts", doc.get("custom", {}))

    def test_the_tag_model_types_the_lamp_state(self):
        def dtype(desc):
            return screen.tags_document([desc])["tags"][0]["tags"][0]["dataType"]
        self.assertEqual(dtype(page([self.sym(states=[{"value": 2, "colour": "alarm"}])])), "Float8")
        self.assertEqual(dtype(page([self.sym(states=[{"value": "A", "colour": "on"}])])), "String")
        self.assertEqual(dtype(page([self.sym()])), "Boolean")

    def test_the_schema_takes_the_keys(self):
        good = page([self.sym(states=[{"value": 1, "colour": "on", "label": "On"}], stateDefault="off")])
        good["schema"] = "cadre-hmi-screen/1"
        self.assertEqual(screen.schema_errors([good], ["d"]), [])
        bad = copy.deepcopy(good)
        bad["symbols"][0]["states"] = [{"value": 1}]
        self.assertTrue(screen.schema_errors([bad], ["d"]))


def model(*devices):
    return {"schema": "cadre-hmi-devices/1", "tagRoot": "[default]tst", "devices": list(devices)}


PUMP = {"id": "p101", "kind": "pump", "faceplate": "asm", "members": {"state": {"type": "Boolean", "access": "read"},
                                                                      "cmd": {"type": "Boolean", "access": "write"}}}
MOTOR = {"id": "m7", "kind": "motor", "faceplate": "asm", "members": {"state": {"type": "Boolean", "access": "read"}}}


class NotificationTests(Case):
    """3.2: the frame and the flap of the module's pump (`obc-alert-frame`, `small-side-flip`, thickness small)."""

    def frame(self, view="Automation/Pump"):
        return self.view(view)

    def test_the_frame_wraps_the_symbol_and_its_readout_as_the_modules_wrapper(self):
        # glass 2026-10-26: the module's frame is 54 by 69 px around its 48 px symbol and 20 px status row, 3 px wider
        # each side and 1 px lower, and its flap lies outside the frame's right edge; a frame over the whole embed box
        # and a flap inside it were not the module's
        doc = json.loads(self.prj.files["com.inductiveautomation.perspective/views/Automation/Pump/view.json"])
        self.assertEqual((doc["root"]["type"], doc["root"]["props"]["mode"]), ("ia.container.coord", "percent"))
        self.assertEqual([c["meta"]["name"] for c in doc["root"]["children"]], ["Layout"])
        n = nodes_of(doc)
        self.assertEqual(n["Layout"]["position"], {"x": 0, "y": 0, "width": 1, "height": 1})
        self.assertEqual([c["meta"]["name"] for c in n["Layout"]["children"]], ["Content"])
        self.assertEqual([c["meta"]["name"] for c in n["Content"]["children"]], ["Symbol", "Readout", "AlertPulse", "AlertFrame"])
        self.assertEqual(n["Content"]["props"]["style"]["position"], "relative")
        self.assertEqual(n["Symbol"]["props"]["style"]["margin"], "0px 3px")                  # 48 + 3 + 3 = 54
        self.assertEqual(n["Readout"]["props"]["style"]["padding"], "0px 4px")                # the row under the symbol
        st = n["AlertFrame"]["props"]["style"]
        self.assertEqual((st["position"], st["top"], st["left"], st["right"], st["bottom"], st["overflow"]),
                         ("absolute", "0px", "0px", "0px", "-1px", "visible"))
        self.assertEqual(n["AlertPulse"]["props"]["style"]["position"], "absolute")
        for name in ("root", "Layout", "Content", "AlertFrame"):
            self.assertEqual(n[name]["props"]["style"]["overflow"], "visible", name)
        self.assertIn("select_device", doc["root"]["events"]["dom"]["onClick"]["config"]["script"])   # the click is the root's

    def test_the_numbers_are_the_modules(self):
        n = self.frame()
        st = n["AlertFrame"]["props"]["style"]
        self.assertEqual((st["borderWidth"], st["borderRadius"], st["pointerEvents"]), ("2px", "6px", "none"))
        self.assertEqual(n["AlertPulse"]["props"]["style"]["borderWidth"], "4px")           # +2 px while the flash is on
        flap = n["Flap_alarm"]
        self.assertEqual(flap["props"]["viewBox"], "0 0 20 20")
        fs = flap["props"]["style"]
        self.assertEqual((fs["position"], fs["top"], fs["right"]), ("absolute", "-3px", "-22px"))   # outside the 2 px frame
        tab = flap["props"]["elements"][0]
        self.assertEqual((tab["name"], tab["fill"]["paint"]), ("frame", "var(--alert-alarm-color)"))
        badge = flap["props"]["elements"][1]
        self.assertEqual(badge["transform"], "translate(2 2) scale(0.666667)")             # the 16 px icon, 2 px padding
        self.assertEqual(badge["elements"][0]["fill"]["paint"], "var(--on-alarm-active-color)")
        self.assertEqual(n["Flap_warning"]["props"]["elements"][1]["elements"][0]["fill"]["paint"],
                         "var(--on-warning-active-color)")

    def test_the_status_row_is_the_modules_state_readout(self):
        # the module draws statusText as the package's state-on or state-off readout: obi-on or obi-off at 16 px, the
        # value text 16 px at weight 400 on a 20 px line, 4 px from the icon
        n = self.frame()
        row = n["Status"]
        self.assertEqual((row["props"]["style"]["height"], row["props"]["style"]["gap"]), ("20px", "4px"))
        text = n["Text"]["props"]["style"]
        self.assertEqual(text["lineHeight"], "20px")
        icons = {c["meta"]["name"]: c for c in row["children"] if c["type"] == "ia.shapes.svg"}
        self.assertEqual(set(icons), {"IconOn", "IconOff", "IconRun", "IconStopped"})
        self.assertEqual(icons["IconOn"]["props"]["elements"][0]["d"], library.icon("on")["elements"][0]["d"])
        self.assertEqual(icons["IconOff"]["props"]["elements"][0]["d"], library.icon("off")["elements"][0]["d"])
        # the module's colours (glass): the icons and On in --element-active-color, Off in --element-inactive-color
        for v in icons.values():
            self.assertEqual(v["props"]["elements"][0]["fill"]["paint"], "var(--element-active-color)")
        self.assertEqual(expr(n["Text"], "props.style.classes"),
                         "'cadre/font/automation-value-regular-off ' + if({view.params.on}, 'cadre/text/active', "
                         "'cadre/text/inactive')")
        # the thicker frame of an unacknowledged alert grows outward, as the module's does, never onto the readout
        st = n["AlertPulse"]["props"]["style"]
        self.assertEqual((st["top"], st["left"], st["right"], st["bottom"]), ("-2px", "-2px", "-2px", "-3px"))
        shown = {k: expr(v, "position.display") for k, v in icons.items()}
        self.assertIn("!{view.params.hasSpeed}", shown["IconOn"])         # on and off without a speed, as the module
        self.assertIn("{view.params.hasSpeed}", shown["IconRun"])

    def test_the_four_categories_have_their_own_badge_icon(self):
        n = self.frame()
        d = {k: n[f"Flap_{k}"]["props"]["elements"][1]["elements"][0]["d"] for k in ("alarm", "warning", "caution", "critical")}
        self.assertEqual(d["alarm"], library.icon("alarm-badge")["elements"][0]["d"])
        self.assertEqual(d["warning"], library.icon("warning-badge")["elements"][0]["d"])
        self.assertEqual(d["caution"], library.icon("caution-badge")["elements"][0]["d"])
        self.assertEqual(d["critical"], library.CRITICAL_BADGE_D)
        self.assertEqual(len(set(d.values())), 4)

    def test_one_flap_shows_for_each_status(self):
        n = self.frame()
        shown = {k: expr(n[f"Flap_{k}"], "position.display") for k in ("alarm", "warning", "caution", "critical")}
        self.assertEqual(shown["warning"], "{view.params.alertFrameStatus} = 'warning'")
        self.assertIn("!= 'critical'", shown["alarm"])

    def test_the_frame_is_dashed_while_rectified_and_coloured_by_status(self):
        n = self.frame()
        for name in ("AlertFrame", "AlertPulse"):
            self.assertEqual(expr(n[name], "props.style.borderStyle"),
                             "if({view.params.alertFrameMode} = 'unacked-rectified', 'dashed', 'solid')")
            self.assertIn("'critical', 'var(--alert-critical-color)'", expr(n[name], "props.style.borderColor"))
        self.assertEqual(expr(n["AlertFrame"], "meta.visible"), "{view.params.alert}")

    def test_the_thick_frame_flashes_at_the_modules_tempo(self):
        n = self.frame()
        self.assertIn("{view.params.alert}", expr(n["AlertPulse"], "meta.visible"))
        self.assertIn("!= 'caution'", expr(n["AlertPulse"], "meta.visible"))                # a caution is steady
        tempo = expr(n["AlertPulse"], "props.style.classes")
        self.assertIn("'warning', 'cadre/alert/blink-slow', 'cadre/alert/blink-fast'", tempo)
        self.assertIn("'cadre/alert/blink-very-slow'", tempo)                              # rectified
        tokens = json.loads((ROOT / "library/tokens/openbridge-tokens.json").read_text(encoding="utf-8"))
        classes = library.style_classes(tokens)
        for name, (on_ms, off_ms) in {"fast": (400, 400), "slow": (400, 1200), "very-slow": (400, 2800)}.items():
            anim = classes[f"cadre/alert/blink-{name}"]["base"]["animation"]
            half = float(anim["duration"].rstrip("s")) * 1000                   # the runtime alternates: twice this is a period
            at = float(next(k for k, v in anim["keyframes"].items() if v["opacity"] == "0" and k != "100%").rstrip("%")) / 100
            self.assertAlmostEqual(2 * at * half, on_ms, msg=name)              # shows from 0 to `at`, and again back to 0
            self.assertAlmostEqual(2 * (1 - at) * half, off_ms, msg=name)

    def test_the_generator_set_draws_the_same_frame(self):
        n = self.view("Automation/GeneratorSet")
        self.assertEqual(n["AlertFrame"]["props"]["style"]["borderWidth"], "2px")
        self.assertIn("Flap_critical", n)

    def test_every_symbol_view_but_the_lamp_has_it(self):
        for kind in library.DEVICE_KINDS:
            n = self.view(f"Automation/{kind}")
            self.assertEqual("AlertFrame" in n, kind != "Indicator", kind)


class FaceplateKeyTests(Case):
    def sym(self, sid, kind, **kw):
        return {"id": sid, "kind": kind, "x": 40, "y": 40, "w": 48, "h": 48, "params": {"hasTag": True, "tag": sid},
                "bind": {"on": f"{sid}/state"}, **kw}

    def test_a_plain_symbol_opens_the_faceplate_of_the_device_it_names(self):
        screen.RENDER["devices"] = screen.model_devices(model(PUMP, MOTOR))
        n, _, info = self.build(page([self.sym("PM1", "motor", faceplate="p101")]))
        self.assertEqual(info["errors"], [])
        p = n["PM1"]["props"]["params"]
        self.assertEqual((p["deviceId"], p["deviceKind"]), ("[default]tst/p101", "pump"))   # the device's kind opens its faceplate
        n, _, _ = self.build(page([self.sym("PM1", "motor", faceplate="p101", params={"deviceKind": "motor"})]))
        self.assertEqual(n["PM1"]["props"]["params"]["deviceKind"], "motor")             # a stated kind stays

    def test_the_module_symbol_opens_it_too(self):
        screen.RENDER["devices"] = screen.model_devices(model(PUMP))
        n, _, _ = self.build(page([self.sym("PM1", "pump", faceplate="p101", params={"hasTag": True, "tag": "P1"})]),
                             render="module")
        self.assertEqual(n["PM1"]["type"], "cadre.ob.pump")
        self.assertEqual(n["PM1"]["custom"]["deviceId"], "[default]tst/p101")
        self.assertIn("select_device", n["PM1"]["events"]["dom"]["onClick"]["config"]["script"])

    def test_it_draws_no_node_for_the_device(self):
        a = page([self.sym("P101", "pump", device=True)], node="Site/Area")
        b = page([self.sym("PM1", "motor", faceplate="p101")], node="Site/Other")
        b["screen"].update(id="U", route="/u", view="Screens/U")
        self.assertEqual(screen.device_nodes([a, b]), {"[default]tst/P101": "Site/Area"})
        b2 = copy.deepcopy(b)
        b2["symbols"][0]["device"] = "p101"
        self.assertEqual(screen.device_nodes([a, b2])["[default]tst/p101"], "Site/Other")
        h = {x["path"]: x for x in screen.hierarchy([a, b], model(PUMP))}
        self.assertEqual(h["Site/Other"]["devices"], [])
        self.assertEqual(h["Site/Area"]["devices"], ["[default]tst/P101"])

    def test_a_device_with_a_node_and_no_page_has_that_node(self):
        a = page([self.sym("PM1", "motor", faceplate="m7")], node="Site/Area")
        m = model(dict(MOTOR, node="Site/Area/Sub"))
        self.assertEqual(screen.device_nodes([a], m), {"[default]tst/m7": "Site/Area/Sub"})
        h = {x["path"]: x for x in screen.hierarchy([a], m)}
        self.assertEqual(h["Site/Area/Sub"]["devices"], ["[default]tst/m7"])
        self.assertEqual(h["Site/Area/Sub"]["parentId"], h["Site/Area"]["id"])
        # a device with no node and no page has none
        self.assertEqual(screen.device_nodes([a], model(MOTOR)), {})
        # and it is indexed for the faceplate, with its node's sources
        index = {d["folder"]: d for d in screen.device_index([a], m)}
        self.assertEqual(index["[default]tst/m7"]["members"], ["state"])

    def test_the_device_index_lists_a_device_only_a_faceplate_symbol_draws(self):
        a = page([self.sym("PM1", "motor", faceplate="m7")])
        index = {d["folder"]: d for d in screen.device_index([a], model(MOTOR))}
        self.assertEqual(index["[default]tst/m7"]["faceplate"], "asm")
        self.assertEqual(index["[default]tst/m7"]["write"], [])
        self.assertEqual(screen.device_index([a]), [{"folder": "[default]tst/m7", "kind": "motor", "title": "m7",
                                                    "label": "", "unit": ""}])

    def test_the_state_only_motor_builds_with_the_asm_faceplate(self):
        a = page([self.sym("PM1", "motor", faceplate="m7")], node="Site/Area")
        child, reports = screen.build_child("cadre_hmi_t", [a], "T", devices=model(MOTOR), faceplate="asm")
        self.assertEqual(reports["/t"]["errors"], [])
        props = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
        dev = props["custom"]["devices"][0]
        self.assertEqual((dev["kind"], dev["faceplate"], dev["members"], dev["write"]), ("motor", "asm", ["state"], []))
        view = json.loads(child.files["com.inductiveautomation.perspective/views/Screens/T/view.json"])
        self.assertEqual(nodes_of(view)["PM1"]["props"]["params"]["deviceId"], "[default]tst/m7")

    def test_the_schema_and_the_model_take_the_keys(self):
        a = page([self.sym("PM1", "motor", faceplate="m7", render="view")])
        a["schema"] = "cadre-hmi-screen/1"
        self.assertEqual(screen.schema_errors([a], ["d"]), [])
        self.assertEqual(screen.devices_schema_errors(model(dict(MOTOR, node="Site/Area")), "m"), [])

    def test_render_view_keeps_the_library_view_under_the_module(self):
        n, _, _ = self.build(page([self.sym("P1", "pump", render="view")]), render="module")
        self.assertEqual(n["P1"]["type"], "ia.display.view")
        n, _, _ = self.build(page([self.sym("P1", "pump")]), render="module")
        self.assertEqual(n["P1"]["type"], "cadre.ob.pump")


if __name__ == "__main__":
    unittest.main()


class SweepOfPlainFaceplateSymbols(unittest.TestCase):
    """G11 on the gateway (2026-10-26): the sweep opened the faceplates of the twelve plain motors that carry
    `faceplate` (contract 3.3) and called them unexpected; a plain symbol with `faceplate` expects its device."""

    def test_a_faceplate_symbol_is_expected_and_checked_like_a_device_symbol(self):
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import faceplates
        desc = {"tagRoot": "[default]cadre_hmi_x", "symbols": [
            {"id": "M_P1", "kind": "motor", "faceplate": "P1", "params": {"tag": "P1"}},
            {"id": "M_P2", "kind": "motor", "params": {"tag": "P2"}}]}
        self.assertEqual(faceplates.expected_devices(desc), {"P1"})
        model = {"tagRoot": "[default]cadre_hmi_x", "devices": [{"id": "P1", "kind": "motor", "faceplate": "asm", "members": {"state": {"type": "Boolean"}}}]}
        self.assertIn("P1", faceplates.device_expectations([desc], model))

    def test_the_maintenance_move_of_an_asm_faceplate_is_no_tab(self):
        # G11 on the test page (2026-10-26): a device with modes shows the moves Take control, Release and Maintenance;
        # an asm faceplate has no Maintenance tab (its maintenance rows are on Config), so that button is the move
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import faceplates
        names = ["Home", "Config", "Diagnostics", "Alarms", "Info", "Maintenance"]
        self.assertEqual(faceplates.tab_names(names, {"style": "asm"}), names[:5])
        self.assertEqual(faceplates.tab_names(names, {"style": "openbridge"}), names)
        self.assertEqual(faceplates.tab_names(names, None), names)
        desc = {"tagRoot": "[default]cadre_hmi_x", "symbols": [{"id": "P1", "kind": "pump", "device": "P1"}]}
        model = {"tagRoot": "[default]cadre_hmi_x", "devices": [{"id": "P1", "kind": "pump", "faceplate": "asm",
                                                                 "members": {"state": {"type": "Boolean"}}}]}
        self.assertEqual(faceplates.device_expectations([desc], model)["P1"]["style"], "asm")
