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
                   "cadre.ob.filter": ("showStatus",), "cadre.ob.resistor": ("showStatus",),
                   "cadre.ob.damper": ("showStatus",), "cadre.ob.switch": ("showStatus",), "cadre.ob.capacitor": ("showStatus",),
                   "cadre.ob.diodes": ("showStatus",), "cadre.ob.ground": ("showStatus",), "cadre.ob.source": ("showStatus",), "cadre.ob.converter": ("showStatus",), "cadre.ob.transformer": ("showStatus",), "cadre.ob.bipolartransistor": ("showStatus",), "cadre.ob.mosfet": ("showStatus",), "cadre.ob.logic": ("showStatus",), "cadre.ob.router": ("showStatus",),
                   "cadre.ob.generator": ("showStatus", "statusText")}
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


class DamperComponent(unittest.TestCase):
    """The damper symbol (batch B1): `obc-damper`, no events, no command of its own, on the attribute set of the filter less
    `alternativeIcon` (the element has one drawing)."""
    ctype = "cadre.ob.damper"

    # the element's attributes in the manifest (src/automation/damper/damper.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES - {"alternativeIcon"}

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-damper")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/damper/damper.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-damper")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertNotIn("alternativeIcon", props)      # the element declares none
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.damper", "damper"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/damper.props.json").exists())
        self.assertIn("automation/damper/damper.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.damper","tag":"obc-damper"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-damper"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class SwitchComponent(unittest.TestCase):
    """The static switch symbol (batch B1): `obc-switch`, no events, no command of its own, on the attribute set of the filter."""
    ctype = "cadre.ob.switch"

    # the element's attributes in the manifest (src/automation/switch/switch.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves
    MANIFEST_ATTRIBUTES = {
        "alternativeIcon", "on", "variant", "orientation", "readoutPosition", "readoutSize", "tag", "positioning",
        "activated", "alert", "alertFrameType", "alertFrameThickness", "alertFrameStatus", "alertFrameMode",
        "showAlertIcon", "progress", "progressMode", "progressValue", "badgeControl", "badgeCommandLocked",
        "badgeInterlock", "badgeAlert"}

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-switch")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/switch/switch.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-switch")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["regular", "s1", "s2", "s3"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.switch", "switch"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/switch.props.json").exists())
        self.assertIn("automation/switch/switch.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.switch","tag":"obc-switch"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-switch"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class DamperComponent(unittest.TestCase):
    """The damper symbol (batch B1): `obc-damper`, no events, no command of its own, on the attribute set of the switch less
    `alternativeIcon` (the element has one drawing)."""
    ctype = "cadre.ob.damper"

    # the element's attributes in the manifest (src/automation/damper/damper.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves
    MANIFEST_ATTRIBUTES = SwitchComponent.MANIFEST_ATTRIBUTES - {"alternativeIcon"}

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-damper")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/damper/damper.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-damper")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertNotIn("alternativeIcon", props)      # the element declares none
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.damper", "damper"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/damper.props.json").exists())
        self.assertIn("automation/damper/damper.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.damper","tag":"obc-damper"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-damper"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class ResistorComponent(unittest.TestCase):
    """The static resistor symbol (batch B0, the pilot of the module-only kinds): `obc-resistor`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.resistor"

    # the element's attributes in the manifest (src/automation/resistor/resistor.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-resistor")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/resistor/resistor.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-resistor")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["resistor1", "resistor2", "resistor3", "resistor4", "resistor5"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.resistor", "resistor"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/resistor.props.json").exists())
        self.assertIn("automation/resistor/resistor.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.resistor","tag":"obc-resistor"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-resistor"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class CapacitorComponent(unittest.TestCase):
    """The static capacitor symbol (batch B1, a module-only kind): `obc-capacitor`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.capacitor"

    # the element's attributes in the manifest (src/automation/capacitor/capacitor.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-capacitor")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/capacitor/capacitor.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-capacitor")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["capacitor01", "capacitor02", "capacitor03", "capacitor04"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.capacitor", "capacitor"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/capacitor.props.json").exists())
        self.assertIn("automation/capacitor/capacitor.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.capacitor","tag":"obc-capacitor"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-capacitor"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class DiodesComponent(unittest.TestCase):
    """The static diodes symbol (batch B2, a module-only kind): `obc-diodes`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.diodes"

    # the element's attributes in the manifest (src/automation/diodes/diodes.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-diodes")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/diodes/diodes.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-diodes")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["diodes01", "diodes02", "diodes03", "diodes04", "diodes05", "diodes06"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.diodes", "diodes"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/diodes.props.json").exists())
        self.assertIn("automation/diodes/diodes.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.diodes","tag":"obc-diodes"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-diodes"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class GroundComponent(unittest.TestCase):
    """The static ground symbol (batch B2, a module-only kind): `obc-ground`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.ground"

    # the element's attributes in the manifest (src/automation/ground/ground.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-ground")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/ground/ground.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-ground")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["ground1", "ground2", "ground3"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.ground", "ground"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/ground.props.json").exists())
        self.assertIn("automation/ground/ground.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.ground","tag":"obc-ground"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-ground"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class SourceComponent(unittest.TestCase):
    """The static source symbol (batch B2, a module-only kind): `obc-source`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.source"

    # the element's attributes in the manifest (src/automation/source/source.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-source")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/source/source.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-source")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["sources01", "sources02", "sources03", "sources04", "sources05"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.source", "source"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/source.props.json").exists())
        self.assertIn("automation/source/source.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.source","tag":"obc-source"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-source"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class ConverterComponent(unittest.TestCase):
    """The static converter symbol (batch B2, a module-only kind): `obc-converter`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.converter"

    # the element's attributes in the manifest (src/automation/converter/converter.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-converter")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/converter/converter.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-converter")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["converterDcdc", "converterDcac", "converterAcdc", "converterFilter1"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.converter", "converter"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/converter.props.json").exists())
        self.assertIn("automation/converter/converter.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.converter","tag":"obc-converter"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-converter"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class TransformerComponent(unittest.TestCase):
    """The static transformer symbol (batch B2, a module-only kind): `obc-transformer`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.transformer"

    # the element's attributes in the manifest (src/automation/transformer/transformer.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-transformer")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/transformer/transformer.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-transformer")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["transformer01", "transformer02"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.transformer", "transformer"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/transformer.props.json").exists())
        self.assertIn("automation/transformer/transformer.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.transformer","tag":"obc-transformer"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-transformer"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class BipolarTransistorComponent(unittest.TestCase):
    """The static bipolar transistor symbol (batch B3, a module-only kind): `obc-bipolar-transistor`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.bipolartransistor"

    # the element's attributes in the manifest (src/automation/bipolar-transistor/bipolar-transistor.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-bipolar-transistor")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/bipolar-transistor/bipolar-transistor.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-bipolar-transistor")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["bipolarTransistor01", "bipolarTransistor02", "bipolarTransistor03", "bipolarTransistor04", "bipolarTransistor03Flat", "bipolarTransistor04Flat"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.bipolartransistor", "bipolartransistor"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/bipolartransistor.props.json").exists())
        self.assertIn("automation/bipolar-transistor/bipolar-transistor.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.bipolartransistor","tag":"obc-bipolar-transistor"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-bipolar-transistor"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class MosfetComponent(unittest.TestCase):
    """The static MOSFET symbol (batch B3, a module-only kind): `obc-mosfet`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.mosfet"

    # the element's attributes in the manifest (src/automation/mosfet/mosfet.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-mosfet")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/mosfet/mosfet.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-mosfet")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["mosfetNtype1", "mosfetNtype2", "mosfetNtype3", "mosfetNtype4", "mosfetPtype1", "mosfetPtype2", "mosfetPtype3", "mosfetPtype4"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.mosfet", "mosfet"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/mosfet.props.json").exists())
        self.assertIn("automation/mosfet/mosfet.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.mosfet","tag":"obc-mosfet"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-mosfet"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class LogicComponent(unittest.TestCase):
    """The static logic symbol (batch B3, a module-only kind): `obc-logic`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.logic"

    # the element's attributes in the manifest (src/automation/logic/logic.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-logic")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/logic/logic.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-logic")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["logic01", "logic02", "logic03", "logic04", "logic05", "logic06"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.logic", "logic"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/logic.props.json").exists())
        self.assertIn("automation/logic/logic.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.logic","tag":"obc-logic"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-logic"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class RouterComponent(unittest.TestCase):
    """The static router symbol (batch B3, a module-only kind): `obc-router`, no events, no command of
    its own, on the attribute set of the filter."""
    ctype = "cadre.ob.router"

    # the element's attributes in the manifest (src/automation/router/router.ts), less none; `showStatus` is the field
    # the module adds as it does on the valves and the filter
    MANIFEST_ATTRIBUTES = FilterComponent.MANIFEST_ATTRIBUTES

    def test_the_contract_names_the_element_and_every_attribute_of_the_manifest(self):
        c = COMPONENTS[self.ctype]
        self.assertEqual(c["element"], "obc-router")
        self.assertEqual(set(c["props"]) - {"componentSize", "showStatus"}, self.MANIFEST_ATTRIBUTES)
        self.assertNotIn("events", c)
        self.assertEqual(c["defaultSize"], {"width": 96, "height": 96})

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = next(d for m in manifest["modules"] if m["path"] == "src/automation/router/router.ts"
                    for d in m.get("declarations", []) if d.get("tagName") == "obc-router")
        self.assertEqual({a["fieldName"] for a in decl["attributes"]}, self.MANIFEST_ATTRIBUTES)
        self.assertEqual(decl.get("events", []), [])

    def test_the_enumerations_come_from_the_element(self):
        props = schema_of(self.ctype)["properties"]
        self.assertEqual(props["alternativeIcon"]["enum"], ["router", "router2"])
        self.assertEqual(props["variant"]["enum"], ["square", "flat"])
        self.assertEqual(props["orientation"]["enum"], ["horizontal", "verticalRight", "verticalLeft"])
        self.assertEqual(props["variant"]["default"], "square")
        self.assertEqual(props["orientation"]["default"], "horizontal")
        self.assertEqual(props["alertFrameStatus"]["default"], "alarm")

    def test_the_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.router", "router"')
        self.assertTrue((MODULE / "common/src/main/resources/schemas/router.props.json").exists())
        self.assertIn("automation/router/router.js", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        self.assertIn('"type":"cadre.ob.router","tag":"obc-router"', JS)
        self.assertRegex(JS, r'\(\[\w+\("obc-router"\)\]')   # the element's registration decorator is in the bundle

    def test_it_carries_no_speed_status_text_or_duty_props(self):
        props = COMPONENTS[self.ctype]["props"]
        for name in ("statusText", "badgeDuty", "outOfService", "hasSpeed", "speed", "selectable"):
            self.assertNotIn(name, props, name)
        self.assertEqual(props["showStatus"], {"type": "boolean", "default": True})


class GlyphComponents(unittest.TestCase):
    """The four glyphs of batch B4 (module-only kinds whose attributes differ from the filter's): each carries exactly
    the attributes its manifest declares, no events, and none of the symbol's properties."""
    # component type: (tag, manifest path, the manifest's attributes, default size)
    SPECIALTY = {"medium", "static", "tag", "positioning", "activated", "badgeControl", "badgeAlert", "badgeInterlock",
                 "badgeCommandLocked", "alert", "alertFrameType", "alertFrameThickness", "alertFrameStatus", "showAlertIcon"}
    GAUGE = {"type", "setpoint", "newSetpoint", "touching", "autoAtSetpointDeadband", "setpointAtZeroDeadband",
             "setpointOverride", "animateSetpoint", "value", "maxValue", "minValue", "secondaryValue", "state", "sector",
             "alignment", "priority", "showLabels", "primaryTickmarkInterval", "secondaryTickmarkInterval", "tickmarkStyle",
             "hasReadout", "label", "unit", "secondaryLabel", "secondaryUnit", "fractionDigits", "name", "faceDiameter",
             "large", "tag"}
    GAUGE_VALVE = {"type", "priority", "barStyle", "scalePosition", "value", "bottomValue", "large", "label", "unit", "tag",
                   "faceDiameter", "setpoint", "newSetpoint", "touching", "autoAtSetpointDeadband", "setpointAtZeroDeadband",
                   "setpointOverride", "animateSetpoint"}
    # the one DOM event of an element, which is not carried (display only)
    CLICK = {"cadre.ob.automationreadout", "cadre.ob.heatexchanger", "cadre.ob.heatpump",
             "cadre.ob.hydraulicseparator"}
    # B8: the valve selectors' one event, `position-selected`, which is not carried either (a write is deferred)
    SHUFFLE = {"type", "ariaLabel", "selectedPosition", "vertical"}
    SELECTED = {"cadre.ob.hydraulicvalve43", "cadre.ob.hydraulicvalvex2"}
    # B8: the transmitter button declares no event at all (its inner `button` has a native click that nobody listens to)
    TRANSMITTER = {"variant", "size", "value", "unit", "fractionDigits", "maxDigits", "hintedZeros", "hasSignSpacer", "hasIcon",
                   "hasAdvice", "adviceValue", "hasSetPoint", "setpointValue", "label"}
    GLYPHS = {
        "cadre.ob.automationbadge": ("obc-automation-badge", "src/automation/automation-badge/automation-badge.ts",
                                     {"mode", "type"}, {"width": 32, "height": 32}),
        "cadre.ob.checkvalve": ("obc-hydraulic-check-valve", "src/automation/hydraulic-check-valve/hydraulic-check-valve.ts",
                                {"ariaLabel", "vertical"}, {"width": 48, "height": 48}),
        "cadre.ob.valvetwoway": ("obc-valve-analog-two-way-icon",
                                 "src/automation/valve-analoge-two-way-icon/valve-analog-two-way-icon.ts",
                                 {"value", "closed", "vertical"}, {"width": 48, "height": 48}),
        "cadre.ob.valvethreeway": ("obc-valve-analog-three-way-icon",
                                   "src/automation/valve-analog-three-way-icon/valve-analog-three-way-icon.ts",
                                   {"value", "value2", "closed", "horisontal"}, {"width": 48, "height": 48}),
        # batch B5: the stateful indicators and the readout (module-only, display only)
        "cadre.ob.battery": ("obc-indicator-battery", "src/automation/indicator-battery/indicator-battery.ts",
                             {"direction", "variant", "value", "level", "data", "hasIcon"}, {"width": 48, "height": 48}),
        "cadre.ob.engine": ("obc-indicator-engine", "src/automation/indicator-engine/indicator-engine.ts",
                            {"value", "direction"}, {"width": 48, "height": 48}),
        "cadre.ob.tankatmospheric": ("obc-indicator-tank-atmospheric",
                                     "src/automation/indicator-tank-atmospheric/indicator-tank-atmospheric.ts",
                                     {"direction", "variant", "value", "level", "data", "hasIcon"}, {"width": 48, "height": 48}),
        # `lineType` is left out: an object type the generator does not map, and the readout sits on no line
        "cadre.ob.automationreadout": ("obc-automation-readout", "src/automation/automation-readout/automation-readout.ts",
                                       {"value", "unit", "numberOfDigits", "position"}, {"width": 72, "height": 48}),
        # batch B6: the specialty tank equipment (module-only, display only): the tank's own tag, alert and badge attributes
        "cadre.ob.heatexchanger": ("obc-heat-exchanger", "src/automation/heat-exchanger/heat-exchanger.ts",
                                   SPECIALTY, {"width": 152, "height": 96}),
        "cadre.ob.heatpump": ("obc-heat-pump", "src/automation/heat-pump/heat-pump.ts", SPECIALTY, {"width": 152, "height": 96}),
        "cadre.ob.hydraulicseparator": ("obc-hydraulic-separator", "src/automation/hydraulic-separator/hydraulic-separator.ts",
                                        SPECIALTY, {"width": 152, "height": 96}),
        # batch B7: the gauges (module-only, display only): the setpoint is shown, never written
        "cadre.ob.gaugegenerator": ("obc-gauge-generator", "src/automation/gauge-generator/gauge-generator.ts",
                                    GAUGE, {"width": 240, "height": 280}),
        "cadre.ob.gaugemotorspumps": ("obc-gauge-motors-and-pumps",
                                      "src/automation/gauge-motors-and-pumps/gauge-motors-and-pumps.ts",
                                      GAUGE, {"width": 240, "height": 280}),
        "cadre.ob.gaugevalve": ("obc-gauge-valve", "src/automation/gauge-valve/gauge-valve.ts",
                                GAUGE_VALVE, {"width": 240, "height": 280}),
        # batch B8: the control elements (module-only, display only): the selected position is shown, never written
        "cadre.ob.hydraulicvalve43": ("obc-hydraulic-valve-4-3", "src/automation/hydraulic-valve-4-3/hydraulic-valve-4-3.ts",
                                      SHUFFLE, {"width": 144, "height": 48}),
        "cadre.ob.hydraulicvalvex2": ("obc-hydraulic-valve-x-2", "src/automation/hydraulic-valve-x-2/hydraulic-valve-x-2.ts",
                                      SHUFFLE, {"width": 96, "height": 48}),
        "cadre.ob.transmitterbutton": ("obc-transmitter-button", "src/automation/transmitter-button/transmitter-button.ts",
                                       TRANSMITTER, {"width": 96, "height": 40}),
    }
    NAMES = {"cadre.ob.automationbadge": "automationbadge", "cadre.ob.checkvalve": "checkvalve",
             "cadre.ob.valvetwoway": "valvetwoway", "cadre.ob.valvethreeway": "valvethreeway",
             "cadre.ob.battery": "battery", "cadre.ob.engine": "engine", "cadre.ob.tankatmospheric": "tankatmospheric",
             "cadre.ob.automationreadout": "automationreadout", "cadre.ob.heatexchanger": "heatexchanger",
             "cadre.ob.heatpump": "heatpump",
             "cadre.ob.hydraulicseparator": "hydraulicseparator",
             "cadre.ob.gaugegenerator": "gaugegenerator",
             "cadre.ob.gaugemotorspumps": "gaugemotorspumps", "cadre.ob.gaugevalve": "gaugevalve",
             "cadre.ob.hydraulicvalve43": "hydraulicvalve43",
             "cadre.ob.hydraulicvalvex2": "hydraulicvalvex2",
             "cadre.ob.transmitterbutton": "transmitterbutton"}

    def test_the_contract_names_the_element_and_exactly_the_attributes_of_the_manifest(self):
        for ctype, (tag, _path, attrs, size) in self.GLYPHS.items():
            c = COMPONENTS[ctype]
            self.assertEqual(c["element"], tag)
            self.assertEqual(set(c["props"]) - {"componentSize"}, attrs, ctype)
            self.assertNotIn("events", c)
            self.assertEqual(c["defaultSize"], size, ctype)

    def test_the_manifest_and_the_contract_agree(self):
        manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        for ctype, (tag, path, attrs, _size) in self.GLYPHS.items():
            decl = next(d for m in manifest["modules"] if m["path"] == path
                        for d in m.get("declarations", []) if d.get("tagName") == tag)
            declared = {a["fieldName"] for a in decl["attributes"]}
            self.assertEqual(declared - ({"lineType"} if ctype == "cadre.ob.automationreadout" else set()), attrs, ctype)
            # a `click` is the only event among them, and it is not wired (display only, wiki 17.18 and 17.19)
            self.assertEqual([e["name"] for e in decl.get("events", [])],
                             ["click"] if ctype in self.CLICK else ["position-selected"] if ctype in self.SELECTED else [], ctype)

    def test_the_enumerations_and_defaults_come_from_the_element(self):
        badge = schema_of("cadre.ob.automationbadge")["properties"]
        self.assertEqual(badge["mode"]["enum"], ["flat", "regular", "enhanced"])
        self.assertEqual(len(badge["type"]["enum"]), 17)
        self.assertEqual(badge["type"]["enum"][:3], ["auto", "manual", "manual-only"])
        self.assertEqual((badge["mode"]["default"], badge["type"]["default"]), ("flat", "auto"))
        self.assertEqual(schema_of("cadre.ob.checkvalve")["properties"]["ariaLabel"]["default"], "Check valve")
        for ctype in ("cadre.ob.valvetwoway", "cadre.ob.valvethreeway"):
            props = schema_of(ctype)["properties"]
            self.assertEqual((props["value"]["type"], props["value"]["default"]), ("number", 0), ctype)
            self.assertEqual(props["closed"]["default"], False, ctype)

    def test_each_component_is_registered_in_java_bundled_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        entry = (MODULE / "web/entry.js").read_text(encoding="utf-8")
        for ctype, (tag, path, _attrs, _size) in self.GLYPHS.items():
            name = self.NAMES[ctype]
            self.assertRegex(java, rf'descriptor\("{ctype.replace(".", chr(92) + ".")}", "{name}"')
            self.assertTrue((MODULE / f"common/src/main/resources/schemas/{name}.props.json").exists(), ctype)
            self.assertIn(path.replace("src/", "").replace(".ts", ".js"), entry)
            self.assertIn(f'"type":"{ctype}","tag":"{tag}"', JS)
            self.assertRegex(JS, rf'\(\[\w+\("{tag}"\)\]')

    def test_a_glyph_carries_none_of_the_symbols_properties(self):
        for ctype in self.GLYPHS:
            props = COMPONENTS[ctype]["props"]
            for name in ("on", "tag", "readoutPosition", "showStatus", "statusText", "badgeDuty", "outOfService", "alert",
                         "alertFrameStatus", "alertFrameMode", "variant", "orientation", "positioning", "selectable"):
                if name in self.GLYPHS[ctype][2]:   # an attribute of the element itself (the indicators' `variant`)
                    continue
                self.assertNotIn(name, props, f"{ctype}.{name}")

    def test_the_indicators_and_the_readout_carry_the_enumerations_defaults_and_series_of_the_element(self):
        for ctype in ("cadre.ob.battery", "cadre.ob.tankatmospheric"):
            props = schema_of(ctype)["properties"]
            self.assertEqual(props["direction"]["enum"], ["vertical", "horizontal"])
            self.assertEqual((props["variant"]["enum"], props["variant"]["default"]), (["bar", "trend"], "bar"), ctype)
            self.assertEqual((props["level"]["type"], props["level"]["default"]), ("number", 0), ctype)
            self.assertEqual(props["hasIcon"]["default"], False)
            self.assertEqual((props["data"]["type"], props["data"]["items"], props["data"]["default"]),
                             ("array", {"type": "number"}, []), ctype)
        self.assertEqual(schema_of("cadre.ob.battery")["properties"]["value"]["enum"], ["regular", "enhanced", "categorical"])
        self.assertEqual(schema_of("cadre.ob.tankatmospheric")["properties"]["value"]["enum"], ["regular", "enhanced", "medium"])
        engine = schema_of("cadre.ob.engine")["properties"]
        self.assertEqual((engine["value"]["enum"], engine["value"]["default"]), (["static", "regular", "enhanced"], "static"))
        readout = schema_of("cadre.ob.automationreadout")["properties"]
        self.assertEqual(readout["position"]["enum"], ["left", "right", "top", "bottom"])
        self.assertEqual((readout["position"]["default"], readout["numberOfDigits"]["default"], readout["unit"]["default"]),
                         ("bottom", 3, ""))
        for ctype in self.CLICK | self.SELECTED:
            self.assertNotIn("events", COMPONENTS[ctype], ctype)    # the click and the position selection are not carried

    def test_the_wrapper_converts_a_series_to_numbers_and_reads_it_as_data(self):
        for ctype in ("cadre.ob.battery", "cadre.ob.tankatmospheric"):
            self.assertIn('"data":[{"name":"data","kind":"numbers"}]', self.spec_of(ctype), ctype)
        self.assertIn("numbers: function (v)", JS)

    @staticmethod
    def spec_of(ctype):
        start = JS.index('{"type":"%s"' % ctype)
        return JS[start:JS.index('"events":', start)]


class ModuleOnlyKinds(unittest.TestCase):
    """The module-only kinds (batch B0, wiki page 12 section 17.13): a descriptor kind with no library view, drawn by the
    module's component alone. The table is `screen.MODULE_ONLY`; the tests run over its rows, so a later row is covered."""

    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        from hmi import library_profile, screen, testbench
        cls.screen, cls.testbench, cls.library_profile = screen, testbench, library_profile
        cls.contracts = screen.load_contracts()

    def tearDown(self):
        self.screen.RENDER["target"] = "stock"

    def symbol(self, kind, **kw):
        params = {"tag": "X-1"} if self.is_symbol(kind) else {}   # a glyph has no tag
        return dict({"id": "X1", "kind": kind, "x": 100, "y": 100, "w": 48, "h": 48, "params": params}, **kw)

    def is_symbol(self, kind):
        return self.screen.module_geometry(self.screen.MODULE_ONLY[kind]) == "symbol"

    def symbol_kinds(self):
        return [k for k in self.screen.MODULE_ONLY if self.is_symbol(k)]

    def glyph_kinds(self):
        return [k for k in self.screen.MODULE_ONLY if not self.is_symbol(k)]

    def embed(self, sym, render):
        self.screen.RENDER["target"] = render
        rep = self.screen.Report()
        node, _custom, _cfg = self.screen.embed_symbol(sym, self.contracts, "[default]t", rep, toolbar=True)
        return node, rep

    def test_the_table_names_components_of_the_module_and_no_library_kind(self):
        self.assertIn("resistor", self.screen.MODULE_ONLY)
        for kind, ctype in self.screen.MODULE_ONLY.items():
            self.assertIn(ctype, COMPONENTS, kind)
            self.assertNotIn(kind, self.screen.KIND_VIEW, kind)
            self.assertNotIn(kind, self.screen.MODULE_KIND, kind)

    def test_the_contract_is_derived_from_the_modules_contract(self):
        for kind in self.symbol_kinds():
            ctype = self.screen.MODULE_ONLY[kind]
            c = self.contracts[self.screen.view_of({"kind": kind})]
            props = COMPONENTS[ctype]["props"]
            self.assertEqual(self.screen.view_of({"kind": kind}), "Module/" + kind)
            self.assertEqual((c["anchor"], c["symbolSize"], c["state"], c["kind"]), ("symbol-centre", 48, "on", kind), kind)
            for name, p in props.items():     # every property with its default, but the positioning the generator states
                if name != "positioning":
                    self.assertEqual(c["params"][name], p["default"], f"{kind}.{name}")
            self.assertNotIn("positioning", c["params"])
            self.assertEqual(set(c["params"]) - set(props), set(self.screen._MODULE_ONLY_MARKS) - set(props), kind)
        # the library's own contracts are not changed, and its profile lists no module-only kind
        self.assertNotIn("resistor", self.library_profile.build(self.contracts)["kinds"])

    def test_a_glyph_contract_holds_exactly_the_properties_its_component_declares(self):
        self.assertEqual(sorted(self.glyph_kinds()), [
            "automation-badge", "automation-readout", "gauge-generator", "gauge-motors-and-pumps", "gauge-valve", "heat-exchanger", "heat-pump", "hydraulic-check-valve",
            "hydraulic-separator", "hydraulic-valve-4-3", "hydraulic-valve-x-2", "indicator-battery", "indicator-engine", "indicator-tank-atmospheric",
            "transmitter-button", "valve-analog-three-way-icon", "valve-analog-two-way-icon"])
        for kind in self.glyph_kinds():
            spec = COMPONENTS[self.screen.MODULE_ONLY[kind]]
            c = self.contracts[self.screen.view_of({"kind": kind})]
            # `positioning` is the generator's to state, for a symbol only (`screen.module_contract`): a tank-based glyph fills its box
            self.assertEqual(c["params"], {k: p["default"] for k, p in sorted(spec["props"].items()) if k != "positioning"}, kind)
            self.assertEqual((c["anchor"], c["flow"], c["size"], c["kind"]),
                             ("box", "none", [spec["defaultSize"]["width"], spec["defaultSize"]["height"]], kind))
            for key in ("state", "symbolSize", "identifier", "readoutExtent", "statusMode"):
                self.assertNotIn(key, c, f"{kind}.{key}")
            self.assertFalse(set(c["params"]) & set(self.screen._MODULE_ONLY_MARKS), kind)

    def test_the_contracts_of_the_other_kinds_are_the_same_as_before_the_glyph_geometry(self):
        # the symbol branch of `module_contract` is the one B0 wrote: the filter's geometry and marks, the component's properties
        for kind in self.symbol_kinds():
            c = self.contracts[self.screen.view_of({"kind": kind})]
            template = self.contracts[self.screen.KIND_VIEW["filter"]]
            props = COMPONENTS[self.screen.MODULE_ONLY[kind]]["props"]
            want = {**self.screen._MODULE_ONLY_MARKS, **{k: p["default"] for k, p in props.items() if k != "positioning"}}
            self.assertEqual(c, {**{k: template[k] for k in ("anchor", "identifier", "readoutExtent", "size", "symbolSize",
                                                              "state", "statusMode")},
                                 "kind": kind, "view": "Module/" + kind, "params": dict(sorted(want.items()))}, kind)

    def test_the_module_rendering_draws_the_component(self):
        for kind in self.glyph_kinds():
            ctype = self.screen.MODULE_ONLY[kind]
            stated = {"automation-badge": {"type": "manual", "mode": "regular"}, "hydraulic-check-valve": {"vertical": True},
                      "valve-analog-two-way-icon": {"value": 50, "closed": True},
                      "valve-analog-three-way-icon": {"value": 50, "value2": 25, "horisontal": True},
                      "indicator-battery": {"level": 40, "variant": "trend", "data": [10, 20, 30]},
                      "indicator-engine": {"value": "regular", "direction": "horizontal"},
                      "indicator-tank-atmospheric": {"level": 60, "value": "medium"},
                      "automation-readout": {"value": 12, "unit": "kn", "position": "left"},
                      "heat-exchanger": {"medium": "graphic", "alert": True, "alertFrameStatus": "warning"},
                      "heat-pump": {"medium": "medium", "activated": True, "badgeControl": "auto"},
                      "hydraulic-separator": {"medium": "regular", "static": True, "badgeInterlock": "interlock"},
                      "gauge-generator": {"value": 60, "type": "double", "priority": "enhanced", "label": "kW", "large": True},
                      "gauge-motors-and-pumps": {"value": 40, "type": "negative", "sector": "270", "unit": "rpm"},
                      "gauge-valve": {"value": 50, "bottomValue": 25, "type": "three-way", "barStyle": "fill"},
                      "hydraulic-valve-4-3": {"type": "3", "selectedPosition": 2, "vertical": True},
                      "hydraulic-valve-x-2": {"type": "3/2", "selectedPosition": 0, "vertical": True},
                      "transmitter-button": {"variant": "value", "size": "large", "value": 12.5, "unit": "bar", "hasAdvice": True,
                                             "adviceValue": 10, "hasSetPoint": True, "setpointValue": 11}}[kind]
            node, rep = self.embed(self.symbol(kind, params=dict(stated)), "module")
            self.assertEqual((node["type"], rep.errors, rep.gaps), (ctype, [], []), kind)
            self.assertEqual(node["props"], stated, kind)           # nothing is added: no positioning, no tag, no status
            self.assertNotIn("events", node)
            node, rep = self.embed(self.symbol(kind, params={"on": True}), "module")      # a symbol's property is refused
            self.assertTrue(any("'on' is not in the" in e for e in rep.errors), kind)
        for kind in self.symbol_kinds():
            ctype = self.screen.MODULE_ONLY[kind]
            node, rep = self.embed(self.symbol(kind, params={"tag": "X-1", "on": True, "variant": "flat"}), "module")
            self.assertEqual((node["type"], rep.errors, rep.gaps), (ctype, [], []), kind)
            self.assertEqual(node["props"]["variant"], "flat")
            self.assertEqual(node["props"]["positioning"], "symbol")
            self.assertNotIn("deviceId", node["props"])

    # The live attributes of the B5 kinds, read from the pinned `dist/` sources (wiki 12 section 17.18): what a screen binds to a tag.
    LIVE = {"indicator-battery": ("level", "value", "data"), "indicator-engine": ("value",),
            "indicator-tank-atmospheric": ("level", "value", "data"), "automation-readout": ("value", "unit"),
            # B6: the scheme, the activation and the element's own alert frame (it has no device state of its own)
            "heat-exchanger": ("medium", "activated", "alert", "alertFrameStatus"),
            "heat-pump": ("medium", "activated", "alert", "alertFrameStatus"),
            "hydraulic-separator": ("medium", "activated", "alert", "alertFrameStatus"),
            # B7: the measurement, the optional second measurement, the state and the scheme; the setpoints are shown only
            "gauge-generator": ("value", "secondaryValue", "state", "priority", "setpoint", "newSetpoint"),
            "gauge-motors-and-pumps": ("value", "secondaryValue", "state", "priority", "setpoint", "newSetpoint"),
            "gauge-valve": ("value", "bottomValue", "priority", "setpoint", "newSetpoint"),
            # B8: the selected position is shown from a tag; the `position-selected` event is not wired, nothing is written
            "hydraulic-valve-4-3": ("selectedPosition",), "hydraulic-valve-x-2": ("selectedPosition",),
            # the transmitter button's three segments; its click is not wired, so nothing is written
            "transmitter-button": ("value", "adviceValue", "setpointValue")}

    def test_a_descriptor_symbol_of_a_live_kind_binds_each_live_attribute_to_its_tag(self):
        # `embed_module` turns `bind` into the tag binding of the component's property (`props.<name>`) for any component, a
        # module-only glyph included: the symbol states no value beside the binding (GF-61)
        for kind, live in self.LIVE.items():
            ctype = self.screen.MODULE_ONLY[kind]
            for name in live:
                sym = self.symbol(kind, bind={name: f"Plant/{kind}/{name}"})
                node, rep = self.embed(sym, "module")
                self.assertEqual((node["type"], rep.errors, rep.gaps), (ctype, [], []), (kind, name))
                self.assertEqual(node["propConfig"], {f"props.{name}": {"binding": {"type": "tag", "config": {
                    "mode": "direct", "tagPath": f"[default]t/Plant/{kind}/{name}"}}}}, (kind, name))
                self.assertNotIn(name, node["props"], (kind, name))
                self.assertNotIn("events", node)
            # all the live attributes at once, with a static one beside them
            sym = self.symbol(kind, params={"direction": "horizontal"} if "direction" in COMPONENTS[ctype]["props"] else {},
                              bind={n: f"Plant/{kind}/{n}" for n in live})
            node, rep = self.embed(sym, "module")
            self.assertEqual((rep.errors, set(node["propConfig"])), ([], {f"props.{n}" for n in live}), kind)
            desc = {"tagRoot": "[default]t", "tagModel": "external", "screen": {"width": 400, "height": 300}, "symbols": [sym]}
            self.screen.RENDER["target"] = "module"
            _doc, info = self.screen.build_screen(desc, self.contracts)
            self.assertEqual((info["errors"], info["gaps"]), ([], []), kind)

    def test_a_tank_based_glyph_takes_its_identifier_through_the_toolbar_as_the_other_tanks_do(self):
        for kind in ("heat-exchanger", "heat-pump", "hydraulic-separator"):
            node, rep = self.embed(self.symbol(kind, params={"tag": "HX-1"}), "module")
            self.assertEqual((rep.errors, rep.gaps, node["props"]), ([], [], {}), kind)
            self.assertEqual(node["custom"], {"idText": "HX-1"}, kind)
            self.assertIn("{view.custom.showTag}", node["propConfig"]["props.tag"]["binding"]["config"]["expression"], kind)

    def test_the_transmitter_buttons_tag_case_carries_a_label_and_its_nullable_numbers_are_stated(self):
        cases = {c.caption: c.params for c in self.testbench.module_only_cases(
            "transmitter-button", self.contracts[self.screen.view_of({"kind": "transmitter-button"})])}
        self.assertEqual(cases["variant tag"]["label"], "TT")
        self.assertNotIn("label", cases["variant value"])
        self.assertEqual({cases[f"{k} {v}"][k] for k in ("value", "adviceValue", "setpointValue") for v in (50, 100)}, {50, 100})
        # a nullable number outside `GLYPH_NULLABLE` (a gauge's setpoint) stays unstated
        gauge = self.testbench.module_only_cases("gauge-valve", self.contracts[self.screen.view_of({"kind": "gauge-valve"})])
        self.assertFalse(any("setpoint" in c.params for c in gauge))

    def test_the_live_attributes_are_properties_of_their_component(self):
        for kind, live in self.LIVE.items():
            self.assertLessEqual(set(live), set(COMPONENTS[self.screen.MODULE_ONLY[kind]]["props"]), kind)

    def test_the_stock_rendering_is_refused_with_an_error_not_a_silent_gap(self):
        for kind, ctype in self.screen.MODULE_ONLY.items():
            node, rep = self.embed(self.symbol(kind), "stock")
            self.assertEqual(len(rep.errors), 1, kind)
            self.assertIn(f"kind {kind!r} is module only ({ctype})", rep.errors[0])
            self.assertIn("--render module", rep.errors[0])
            self.assertEqual(node["type"], "ia.display.label")      # the counted gap box stands in the view
            self.assertEqual([g["kind"] for g in rep.gaps], [kind])

    def test_a_symbol_the_component_cannot_draw_is_refused_under_the_module_rendering_too(self):
        for kind in self.screen.MODULE_ONLY:
            node, rep = self.embed(self.symbol(kind, render="view"), "module")
            self.assertEqual((len(rep.errors), node["type"]), (1, "ia.display.label"), kind)
            self.assertIn("module only", rep.errors[0])

    def test_the_stock_build_names_the_error_in_the_report_gate_g7_contract_reads(self):
        for kind in self.screen.MODULE_ONLY:
            self.screen.RENDER["target"] = "stock"
            desc = {"tagRoot": "[default]t", "tagModel": "external", "screen": {"width": 400, "height": 300},
                    "symbols": [self.symbol(kind)]}
            _doc, info = self.screen.build_screen(desc, self.contracts)
            self.assertTrue(any("is module only" in e for e in info["errors"]), kind)
            self.screen.RENDER["target"] = "module"
            _doc, info = self.screen.build_screen(desc, self.contracts)
            self.assertEqual((info["errors"], info["gaps"]), ([], []), kind)

    def test_the_component_test_page_has_one_module_only_section_under_the_module_rendering_only(self):
        prof = self.library_profile.build(self.contracts)
        stock = self.testbench.build(self.contracts, prof, "[default]cadre_hmi_ctest")
        self.assertNotIn("ModuleOnly", {s["id"] for s in stock.descriptor["sections"]})
        self.assertFalse(any(s["kind"] in self.screen.MODULE_ONLY for s in stock.descriptor["symbols"]))
        mod = self.testbench.build(self.contracts, prof, "[default]cadre_hmi_ctest", render="module")
        sections = [s for s in mod.descriptor["sections"] if s["id"] == "ModuleOnly"]
        self.assertEqual(len(sections), 1)
        self.assertTrue(sections[0]["label"].startswith("Module only"))
        for kind in self.glyph_kinds():
            # a case for each value of each enumerated attribute (the module's own componentSize apart), the numbers and the flags
            mine = [s for s in mod.descriptor["symbols"] if s["kind"] == kind]
            props = COMPONENTS[self.screen.MODULE_ONLY[kind]]["props"]
            stated = {}
            for s in mine:
                for k, v in {**s["params"], **{b: mod.gallery[s["id"]][b] for b in s.get("bind", {})}}.items():
                    stated.setdefault(k, set()).add(tuple(v) if isinstance(v, list) else v)
            self.assertEqual(self.testbench.check(mod.descriptor, self.contracts), [])
            for name, p in props.items():
                if name == "positioning":
                    self.assertNotIn(name, stated, kind)     # the page leaves the default, which fills the box
                elif "enum" in p and name != "componentSize":
                    self.assertEqual(stated[name], set(p["enum"]), (kind, name))
                elif p["type"] == "boolean":
                    self.assertIn(not p["default"], stated[name], (kind, name))
                elif p["type"] == "number" or (p["type"] == ["number", "null"] and name in self.testbench.GLYPH_NULLABLE):
                    self.assertTrue(set(self.testbench.GLYPH_NUMBER_VALUES.get(name, self.testbench.GLYPH_NUMBERS)) <= stated[name],
                                    (kind, name))
            self.assertEqual({k for s in mine for k in s["params"]} - set(props), set(), kind)
            if "data" in props:   # a trend case carries the series; no other case does
                self.assertEqual({tuple(s["params"]["data"]) for s in mine if "data" in s["params"]},
                                 {tuple(self.testbench.GLYPH_SERIES)}, kind)
                self.assertTrue(all(s["params"].get("variant") == "trend" for s in mine if "data" in s["params"]), kind)
            self.assertEqual(len(mine), {"automation-badge": 21, "hydraulic-check-valve": 2, "valve-analog-two-way-icon": 5,
                                         "valve-analog-three-way-icon": 7, "indicator-battery": 11, "indicator-engine": 6,
                                         "indicator-tank-atmospheric": 11, "automation-readout": 10, "heat-exchanger": 44, "heat-pump": 44, "hydraulic-separator": 44, "gauge-generator": 37, "gauge-motors-and-pumps": 38, "gauge-valve": 26, "hydraulic-valve-4-3": 10, "hydraulic-valve-x-2": 8, "transmitter-button": 22}[kind], kind)
        for kind in self.symbol_kinds():
            mine = [s for s in mod.descriptor["symbols"] if s["kind"] == kind]
            self.assertGreaterEqual(len(mine), 10, kind)
            self.assertEqual(self.testbench.check(mod.descriptor, self.contracts), [])
            enums = COMPONENTS[self.screen.MODULE_ONLY[kind]]["props"]
            for param in ("orientation", "readoutPosition"):      # every value of the component's enumeration is a case
                self.assertEqual({s["params"].get(param, self.contracts[f"Module/{kind}"]["params"][param]) for s in mine},
                                 set(enums[param]["enum"]), (kind, param))
            # the state and mark parameters of a static grid are bound to gallery tags that start at the case's value
            self.assertEqual({mod.gallery[s["id"]]["alertFrameStatus"] for s in mine if "alertFrameStatus" in mod.gallery.get(s["id"], {})},
                             set(enums["alertFrameStatus"]["enum"]))

    def test_the_glass_gates_find_a_module_only_kind_by_its_element(self):
        import sys
        sys.path.insert(0, str(ROOT / "tools" / "compare"))
        import glass_gates
        for kind, ctype in self.screen.MODULE_ONLY.items():
            self.assertEqual(glass_gates.MODULE_TAGS[kind], COMPONENTS[ctype]["element"], kind)


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
    def test_the_version_is_plain_and_0_5_0(self):
        text = (MODULE / "build.gradle.kts").read_text(encoding="utf-8")
        self.assertIn('version = "0.5.0"', text)      # GF-27: plain major.minor.revision (T1 B0 and B1)
        self.assertNotRegex(text, r'version = "[^"]*-')

    def test_the_description_names_the_canvas_zoom(self):
        text = (MODULE / "build.gradle.kts").read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if "moduleDescription" in ln)
        self.assertIn("canvas zoom", line)

    def test_the_description_names_the_wraps_of_spike_t0(self):
        text = (MODULE / "build.gradle.kts").read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if "moduleDescription" in ln)
        for word in ("filter", "generator", "automation button", "damper", "switch", "resistor", "capacitor"):
            self.assertIn(word, line, word)


if __name__ == "__main__":
    unittest.main()
