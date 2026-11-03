"""Tests of the Cadre OpenBridge module's contract (version 0.4.3: eng02 ASM Levels 4 and 5, and the valves' `showStatus`
of 0.3.2).

The module's sources are the generator (`module/tools/gen_module_assets.py`), the canvas zoom component
(`module/web/canvaszoom.js`) and the files they write: `components.json`, the property schemas and the browser
script. These tests hold the written files to each other and to the Level 4 interface (device props and the
canvas zoom), without a gateway. The browser behaviour is checked in Chromium by `module/tools/` harness pages
and, finally, on the glass.

Run from the repository root:  python -m unittest discover -s tests
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "module"
MOUNTED = MODULE / "gateway/src/main/resources/mounted"

COMPONENTS = json.loads((MODULE / "components.json").read_text(encoding="utf-8"))
JS = (MOUNTED / "js/cadre-ob.js").read_text(encoding="utf-8")
ZOOM_JS = (MODULE / "web/canvaszoom.js").read_text(encoding="utf-8")
CSS = (MOUNTED / "css/cadre-ob.css").read_text(encoding="utf-8")

DEVICES = ("cadre.ob.pump", "cadre.ob.motor", "cadre.ob.fan")
# the device props the Level 4 contract fixes (3.2): name, type, default
DEVICE_PROPS = {"showStatus": ("boolean", True), "statusText": ("string", ""),
                "badgeDuty": ("boolean", False), "outOfService": ("boolean", False)}
# the canvas zoom props (3.1)
ZOOM_PROPS = {"zoom": ("number", 1), "min": ("number", 0.5), "max": ("number", 4),
              "targetDomId": ("string", "cadre-canvas"), "guardBrowserZoom": ("boolean", True),
              "viewWidth": ("number", 0), "viewHeight": ("number", 0)}   # 0.4.1: the measured canvas


# the row selection props of the alarm lists (Level 5 contract 3.5, module 0.4.2): name, type, default
LISTS = ("cadre.ob.alertlist", "cadre.ob.alertpanel")
SELECT_PROPS = {"selectable": ("boolean", False), "selectedIds": ("array", [])}


def schema_of(ctype: str) -> dict:
    return json.loads((MODULE / "common/src/main/resources" / COMPONENTS[ctype]["schema"]).read_text(encoding="utf-8"))


class ContractAgreesWithSchemas(unittest.TestCase):
    def test_every_component_has_its_schema_and_the_props_agree(self):
        for ctype, c in COMPONENTS.items():
            schema = schema_of(ctype)
            props = {k: v for k, v in schema["properties"].items() if k != "style"}
            self.assertEqual(set(c["props"]), set(props), ctype)
            for name, p in c["props"].items():
                self.assertEqual(p["type"], props[name]["type"], f"{ctype}.{name}")
                self.assertEqual(p["default"], props[name]["default"], f"{ctype}.{name}")
                self.assertEqual(p.get("enum"), props[name].get("enum"), f"{ctype}.{name}")

    def test_every_prop_has_a_default_and_a_description_in_its_schema(self):
        for ctype in COMPONENTS:
            for name, p in schema_of(ctype)["properties"].items():
                if name == "style":
                    continue
                self.assertIn("default", p, f"{ctype}.{name}")
                self.assertTrue(p.get("description"), f"{ctype}.{name}")

    def test_the_schemas_are_closed(self):
        for ctype in COMPONENTS:
            self.assertIs(schema_of(ctype)["additionalProperties"], False, ctype)


class DeviceProps(unittest.TestCase):
    def test_pump_motor_and_fan_carry_the_status_and_badge_props(self):
        for ctype in DEVICES:
            props = COMPONENTS[ctype]["props"]
            for name, (typ, default) in DEVICE_PROPS.items():
                self.assertEqual(props[name]["type"], typ, f"{ctype}.{name}")
                self.assertEqual(props[name]["default"], default, f"{ctype}.{name}")
                self.assertEqual(schema_of(ctype)["properties"][name]["default"], default, f"{ctype}.{name}")

    def test_the_other_components_do_not_carry_them(self):
        # the two valves and the filter carry the element's own `showStatus` (valves since 0.3.2) (`gen_module_assets.PROPERTIES`);
        # the generator indicator carries `showStatus` and `statusText`, which its wrapper draws itself (W2), and neither mark
        carried = {"cadre.ob.valve": ("showStatus",), "cadre.ob.analogvalve": ("showStatus",),
                   "cadre.ob.filter": ("showStatus",), "cadre.ob.generator": ("showStatus", "statusText")}
        for ctype, c in COMPONENTS.items():
            if ctype in DEVICES:
                continue
            for name in DEVICE_PROPS:
                if name in carried.get(ctype, ()):
                    self.assertEqual((c["props"][name]["type"], c["props"][name]["default"]), DEVICE_PROPS[name], ctype)
                    continue
                self.assertNotIn(name, c["props"], f"{ctype}.{name}")

    def test_the_readout_stretches_on_request_only(self):
        p = COMPONENTS["cadre.ob.readout"]["props"]["stretch"]
        self.assertEqual((p["type"], p["default"]), ("boolean", False))
        for ctype, c in COMPONENTS.items():
            if ctype != "cadre.ob.readout":
                self.assertNotIn("stretch", c["props"], ctype)

    def test_the_older_props_are_unchanged(self):
        # the Level 4 props only add; the speed and tag props of the wrappers D already maps keep their shape
        pump = COMPONENTS["cadre.ob.pump"]["props"]
        for name in ("hasSpeed", "speedInPercent", "badgeInterlock", "badgeCommandLocked", "badgeControl",
                     "badgeAlert", "tag", "readoutPosition", "positioning"):
            self.assertIn(name, pump, name)
        self.assertEqual(pump["hasSpeed"]["default"], True)

    def test_the_wrapper_applies_each_device_prop(self):
        # the wrapper source: the status override of the element's readouts, the duty slot, the veil
        self.assertIn("applyStatus", JS)
        self.assertIn("extraReadouts", JS)
        self.assertIn("dutySlot", JS)
        self.assertIn("badge-bottom-left", JS)
        self.assertIn("cadre-ob-oos", JS)
        self.assertIn("p.outOfService", JS)
        self.assertIn("p.badgeDuty", JS)
        self.assertIn("data-stretch", JS)
        # the reducer reads every device prop with its default
        specs = json.loads(re.search(r"var COMPONENTS = (\[.*?\]);\n  var SHEETS", JS, re.S).group(1))
        by_type = {s["type"]: s for s in specs}
        for ctype in DEVICES:
            self.assertTrue(by_type[ctype]["status"], ctype)
            extras = {e["name"]: e["def"] for e in by_type[ctype]["extras"]}
            for name, (_typ, default) in DEVICE_PROPS.items():
                self.assertEqual(extras[name], default, f"{ctype}.{name}")
        self.assertEqual({e["name"]: e["def"] for e in by_type["cadre.ob.readout"]["extras"]}, {"stretch": False})
        self.assertTrue(by_type["cadre.ob.readout"]["chipSheet"])

    def test_the_stylesheet_carries_the_veil_and_the_stretch_rules(self):
        self.assertRegex(CSS, r"\.cadre-ob > \.cadre-ob-oos \{[^}]*pointer-events: none;")
        self.assertRegex(CSS, r"\.cadre-ob > obc-transmitter\[data-stretch\] \{[^}]*width: 100%;")
        self.assertRegex(CSS, r"\.cadre-ob \{ position: relative; \}")


class CanvasZoomComponent(unittest.TestCase):
    def test_the_contract_fixes_names_types_and_defaults(self):
        c = COMPONENTS["cadre.ob.canvaszoom"]
        self.assertEqual(set(c["props"]), set(ZOOM_PROPS))
        for name, (typ, default) in ZOOM_PROPS.items():
            self.assertEqual(c["props"][name]["type"], typ, name)
            self.assertEqual(c["props"][name]["default"], default, name)
            self.assertEqual(schema_of("cadre.ob.canvaszoom")["properties"][name]["default"], default, name)
        self.assertIsNone(c["element"])       # a leaf component: it draws no OpenBridge element

    def test_the_component_is_registered_in_java_for_the_gateway_and_the_designer(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.canvaszoom", "canvaszoom"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/canvaszoom.props.json").exists())

    def test_the_generated_script_carries_the_component_source_verbatim(self):
        # a change to web/canvaszoom.js without a regeneration is caught here
        self.assertIn(ZOOM_JS.strip(), JS)
        self.assertIn("'cadre.ob.canvaszoom'", JS)

    def test_the_gestures_have_non_passive_listeners(self):
        self.assertIn("var opt = { passive: false, capture: true };", ZOOM_JS)
        for kind in ("wheel", "keydown", "pointerdown", "pointermove", "pointerup", "pointercancel",
                     "gesturestart", "gesturechange", "touchstart", "touchmove", "touchend", "touchcancel"):
            self.assertRegex(ZOOM_JS, rf"this\.listen\(document, '{kind}', ", kind)

    def test_every_listener_is_removed_on_unmount(self):
        # listeners go through one registry (`listen`), and `detach` removes each of them; unmount calls it
        self.assertEqual(ZOOM_JS.count("addEventListener"), 1)
        self.assertEqual(ZOOM_JS.count("removeEventListener"), 1)
        self.assertRegex(ZOOM_JS, r"componentWillUnmount\(\) \{ this\.detach\(\); \}")
        self.assertRegex(ZOOM_JS, r"this\.listeners\.forEach\(function \(l\) \{ l\[0\]\.removeEventListener\(l\[1\], l\[2\], l\[3\]\); \}\);")
        self.assertIn("window.cancelAnimationFrame", ZOOM_JS)

    def test_the_keys_and_the_wheel(self):
        self.assertIn("e.ctrlKey", ZOOM_JS)
        for key in ("'+'", "'='", "'-'", "'0'", "NumpadAdd", "NumpadSubtract", "Numpad0"):
            self.assertIn(key, ZOOM_JS, key)
        self.assertIn("getElementById(s.id)", ZOOM_JS)
        self.assertIn("targetDomId", ZOOM_JS)

    def test_the_zoom_is_clamped_and_written_back(self):
        self.assertIn("clamp(next, s.min, s.max)", ZOOM_JS)
        self.assertIn("this.put('zoom', zoom)", ZOOM_JS)
        self.assertIn("store.props.write(name, value)", ZOOM_JS)
        self.assertIn("this.put('viewWidth', w)", ZOOM_JS)          # 0.4.1: the canvas it measures
        self.assertIn("this.resizer.disconnect()", ZOOM_JS)

    def test_the_point_under_the_pointer_is_held_by_the_scroll(self):
        self.assertIn("t.scrollLeft = (a.left + a.px) * ratio - a.px;", ZOOM_JS)
        self.assertIn("t.scrollTop = (a.top + a.py) * ratio - a.py;", ZOOM_JS)

    def test_the_browser_zoom_guard(self):
        self.assertIn("maximum-scale=1", ZOOM_JS)
        self.assertIn("guardBrowserZoom !== false", ZOOM_JS)
        self.assertIn("'pan-x pan-y'", ZOOM_JS)
        # the viewport meta is put back on unmount
        self.assertIn("ms.meta.setAttribute('content', ms.content)", ZOOM_JS)

    def test_the_component_renders_nothing_visible(self):
        self.assertRegex(ZOOM_JS, r"visibility: 'hidden', pointerEvents: 'none'")
        self.assertIn("width: 0, height: 0", ZOOM_JS)


class AlertRowSelection(unittest.TestCase):
    """Module 0.4.2: the alert list and the alert panel select rows; the component writes `selectedIds`."""

    def test_both_lists_carry_the_two_props_with_their_defaults(self):
        for ctype in LISTS:
            props = COMPONENTS[ctype]["props"]
            sprops = schema_of(ctype)["properties"]
            for name, (typ, default) in SELECT_PROPS.items():
                self.assertEqual(props[name]["type"], typ, f"{ctype}.{name}")
                self.assertEqual(props[name]["default"], default, f"{ctype}.{name}")
                self.assertEqual(sprops[name]["default"], default, f"{ctype}.{name}")
            self.assertEqual(sprops["selectedIds"]["items"], {"type": "string"}, ctype)

    def test_no_other_component_carries_them(self):
        for ctype, c in COMPONENTS.items():
            if ctype in LISTS:
                continue
            for name in SELECT_PROPS:
                self.assertNotIn(name, c["props"], f"{ctype}.{name}")

    def test_the_lists_keep_their_older_props_and_events(self):
        for ctype in LISTS:
            for name in ("selectedMode", "showTime", "alerts", "componentSize"):
                self.assertIn(name, COMPONENTS[ctype]["props"], f"{ctype}.{name}")
            self.assertIn("onRowClick", COMPONENTS[ctype]["events"], ctype)
            self.assertIn("onAckClick", COMPONENTS[ctype]["events"], ctype)
        self.assertIn("onAckAllClick", COMPONENTS["cadre.ob.alertpanel"]["events"])

    def test_the_wrapper_drives_the_elements_own_table_selection(self):
        # OpenBridge's table has the tick column (obc-checkbox) itself: selectable, selectedRowIds, selection-change
        for needle in ("applySelection", "selection-change", "selectedRowIds", "t.selectable = ", "obc-alert-list-details",
                       "obc-table", "this.put('selectedIds'"):
            self.assertIn(needle, JS, needle)
        self.assertIn('"selection":true', JS)

    def test_only_the_two_lists_are_wrapped_with_selection(self):
        specs = json.loads(re.search(r"var COMPONENTS = (\[.*?\]);\n  var SHEETS", JS, re.S).group(1))
        for s in specs:
            self.assertEqual(bool(s.get("selection")), s["type"] in LISTS, s["type"])
            if s["type"] in LISTS:
                extras = {e["name"]: (e["kind"], e["def"]) for e in s["extras"]}
                self.assertEqual(extras["selectable"], ("boolean", False))
                self.assertEqual(extras["selectedIds"], ("array", []))

    def test_the_reducer_reads_an_array_extra(self):
        self.assertIn("case 'array': return tree.readArray(f.name, f.def);", JS)

    def test_a_tick_toggles_only_the_selection_a_row_click_is_not_hidden(self):
        # the tick's own click stops there (the table's rule), and the wrapper never fires onRowClick for a selection
        self.assertNotRegex(JS, r"selection-change[^;]{0,200}fireComponentEvent")

    def test_stale_ids_are_dropped_against_the_rows_shown(self):
        self.assertIn("pruneSelection", JS)

    def test_the_offline_harness_checks_it(self):
        mjs = (MODULE / "tools/harness/alertselect.mjs").read_text(encoding="utf-8")
        for needle in ("selectable false", "stale", "onRowClick", "selectedIds"):
            self.assertIn(needle, mjs, needle)
        self.assertIn("alertselect.mjs", (MODULE / "tools/harness/README.md").read_text(encoding="utf-8"))


class FilterComponent(unittest.TestCase):
    """The static filter symbol (spike T0, wrap W1): `obc-filter`, no events, no command of its own."""
    ctype = "cadre.ob.filter"

    # the element's attributes in the manifest (src/automation/filter/filter.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves
    MANIFEST_ATTRIBUTES = {
        "alternativeIcon", "on", "variant", "orientation", "readoutPosition", "readoutSize", "tag", "positioning",
        "activated", "alert", "alertFrameType", "alertFrameThickness", "alertFrameStatus", "alertFrameMode",
        "showAlertIcon", "progress", "progressMode", "progressValue", "badgeControl", "badgeCommandLocked",
        "badgeInterlock", "badgeAlert"}

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-filter")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/filter/filter.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-filter")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["filter1", "filter2", "filter3", "filter4"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.filter", "filter"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/filter.props.json").exists())
        self.assertIn("automation/filter/filter.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.filter","tag":"obc-filter"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-filter"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class GeneratorComponent(unittest.TestCase):
    """The generator indicator (spike T0, wrap W2): `obc-indicator-generator`, a 48 px disc with no events. The element
    knows no running state, identifier, status word or alert; the wrapper adds them (`gen_module_assets.EXTRA`)."""
    ctype = "cadre.ob.generator"

    # the element's attributes in the manifest (src/automation/indicator-generator/indicator-generator.ts)
    MANIFEST_ATTRIBUTES = {"variant", "value", "level", "secondaryLevel"}
    # what the wrapper adds, and where it comes from
    WRAPPER_PROPS = {"on", "tag", "readoutPosition", "showStatus", "statusText", "alert", "alertFrameStatus", "alertFrameMode"}

    def test_the_contract_names_the_element_its_four_attributes_and_the_wrapper_props(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-indicator-generator")
        self.assertEqual(set(c["props"]) - {"componentSize"}, self.MANIFEST_ATTRIBUTES | self.WRAPPER_PROPS)
        self.assertNotIn("events", c)

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/indicator-generator/indicator-generator.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-indicator-generator")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element_and_the_alert_frame(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["variant"]["enum"], ["button", "bar", "double-bar"])
        self.assertEqual(props["value"]["enum"], ["off", "regular", "filled", "enhanced", "categorical"])
        self.assertEqual((props["variant"]["default"], props["value"]["default"]), ("button", "off"))
        # the alert props take the values the other device components take (the same OpenBridge enumerations)
        for name in ("alertFrameStatus", "alertFrameMode"):
            self.assertEqual(props[name]["enum"], COMPONENTS["cadre.ob.filter"]["props"][name]["enum"], name)
            self.assertEqual(props[name]["default"], COMPONENTS["cadre.ob.filter"]["props"][name]["default"], name)
        self.assertEqual((props["on"]["default"], props["alert"]["default"], props["showStatus"]["default"]),
                         (False, False, True))

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.generator", "generator"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/generator.props.json").exists())
        self.assertIn("automation/indicator-generator/indicator-generator.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.generator","tag":"obc-indicator-generator"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-indicator-generator"\)\]')   # the element's registration decorator is in the bundle

    def test_the_wrapper_draws_the_state_and_the_alert_frame_without_changing_the_element(self):
        # the generator's wrapper flag is set for this component only
        specs = re.search(r"var COMPONENTS = (\[.*?\]);\n  var SHEETS", JS, re.S)
        comps = json.loads(specs.group(1))
        self.assertEqual([c["type"] for c in comps if c["generator"]], [self.ctype])
        # the running state selects the scheme; the frame and the readout are OpenBridge's own elements, added in the shadow root
        self.assertIn("var value = p.on ? (p.value === 'off' ? 'regular' : p.value) : 'off';", JS)
        self.assertIn("document.createElement('obc-alert-frame')", JS)
        self.assertIn("document.createElement('obc-automation-button-readout-stack')", JS)
        # the element is the pinned package's, untouched (CLAUDE.md non-negotiables 2 and 7): the pin stands
        self.assertIn('"@oicl/openbridge-webcomponents": "2.0.0-next.155"', (MODULE / "web/package.json").read_text(encoding="utf-8"))

    def test_the_alert_frame_takes_the_levels_the_page_gives_it(self):
        # `custom.alerts` gives the level `level-critical` ... `level-diagnostic` (`cadre.hmi.ALERT_NONE`), which the frame's own
        # classes colour (critical on the Cadre critical colour, high on alarm, medium on warning, low on caution)
        self.assertEqual(COMPONENTS[self.ctype]["props"]["alertFrameStatus"]["enum"][3:],
                         ["level-critical", "level-high", "level-medium", "level-low", "level-diagnostic"])


class ButtonComponent(unittest.TestCase):
    """The automation button (spike T0, wrap W3): `obc-automation-button`, whose one event `click` the wrapper carries to the
    Perspective component event `onPress`. The command is the page's script (the library's confirmed pulse, W18)."""
    ctype = "cadre.ob.button"
    MANIFEST_ATTRIBUTES = {"variant", "state", "static", "activated", "tag", "readoutPosition", "readoutSize", "alert",
                           "alertFrameType", "alertFrameThickness", "alertFrameStatus", "alertFrameMode", "showAlertIcon",
                           "progress", "progressMode", "progressValue", "direction", "positioning", "orientation",
                           "hasBadgeSpacer"}

    def decl(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        return next(d for m in manifest["modules"] if m["path"] == "src/automation/automation-button/automation-button.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-automation-button")

    def test_the_contract_names_the_element_and_its_attributes(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-automation-button")
        self.assertEqual(set(c["props"]) - {"componentSize"}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual({a["fieldName"] for a in self.decl()["attributes"]}, self.MANIFEST_ATTRIBUTES)

    def test_the_click_event_is_carried_as_on_press(self):
        self.assertEqual([e["name"] for e in self.decl()["events"]], ["click"])
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["events"], {"onPress": {"element": "click", "schema": "schemas/button.onPress.json"}})
        self.assertTrue((MODULE / "common/src/main/resources/schemas/button.onPress.json").exists())
        self.assertIn('"events":[{"dom":"click","name":"onPress","payload":"none"}]', JS)
        # the wrapper listens on the element and fires through Perspective's componentEvents (GF-37), as for the alert lists
        self.assertIn("el.addEventListener(ev.dom, f)", JS)
        self.assertIn("ce.fireComponentEvent(ev.name, payload(ev.payload, e, this.el))", JS)

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["variant"]["enum"], ["regular", "double", "forward", "square", "flat", "flat-forward"])
        self.assertEqual(props["state"]["enum"], ["closed", "open"])
        self.assertEqual(props["readoutPosition"]["enum"], ["top", "bottom", "left", "right"])
        self.assertEqual(props["positioning"]["enum"], ["point", "symbol", "button"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual((props["variant"]["default"], props["state"]["default"], props["static"]["default"],
                          props["positioning"]["default"]), ("regular", "open", False, "point"))
        for name in ("alertFrameStatus", "alertFrameMode"):
            self.assertEqual(props[name]["enum"], COMPONENTS["cadre.ob.filter"]["props"][name]["enum"], name)

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.button", "button"')
        self.assertIn('event("button", "onPress"', java)
        self.assertTrue((MODULE / "common/src/main/resources/schemas/button.props.json").exists())
        self.assertIn("automation/automation-button/automation-button.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.button","tag":"obc-automation-button"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-automation-button"\)\]')
        self.assertIn('"@oicl/openbridge-webcomponents": "2.0.0-next.155"', (MODULE / "web/package.json").read_text(encoding="utf-8"))

    def test_the_component_test_page_commands_the_test_generator_through_the_confirmed_pulse(self):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        from hmi import library_profile, screen, testbench
        contracts = screen.load_contracts()
        bench = testbench.build(contracts, library_profile.build(contracts), "[default]cadre_hmi_ctest")
        by_id = {b["id"]: b for b in bench.descriptor["buttons"]}
        b = by_id["TB_press_GEN_start"]
        self.assertEqual((b["render"], b["action"]["type"], b["action"]["tag"], b["action"]["ms"]),
                         ("module", "pulse", f"{testbench.FOLDER}/TB_GEN/cmdStart", testbench.PULSE_MS))
        self.assertEqual(testbench.PULSE_MS, 60000)
        self.assertIn(b["action"]["tag"], bench.pulse_tags)
        gen = next(k for k in bench.tags["tags"] if k["name"] == "TB_GEN")
        self.assertIn(("cmdStart", "Boolean"), [(t["name"], t["dataType"]) for t in gen["tags"]])   # the tag exists, a memory Boolean
        # the library's own pulse buttons of the page stay as they were
        self.assertNotIn("render", by_id["TB_pulse_TB_PUMP"])


class Release(unittest.TestCase):
    def test_the_version_is_plain_and_0_4_4(self):
        text = (MODULE / "build.gradle.kts").read_text(encoding="utf-8")
        self.assertIn('version = "0.4.4"', text)      # GF-27: plain major.minor.revision (spike T0: filter, generator, button)
        self.assertNotRegex(text, r'version = "[^"]*-')

    def test_the_description_names_the_canvas_zoom(self):
        text = (MODULE / "build.gradle.kts").read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if "moduleDescription" in ln)
        self.assertIn("canvas zoom", line)

    def test_the_description_names_the_wraps_of_spike_t0(self):
        text = (MODULE / "build.gradle.kts").read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if "moduleDescription" in ln)
        for word in ("filter", "generator", "automation button"):
            self.assertIn(word, line, word)


if __name__ == "__main__":
    unittest.main()
