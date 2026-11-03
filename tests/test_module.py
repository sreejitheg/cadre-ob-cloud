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
    # batch C1: the bars and graphs. The chart elements' series are fields without an attribute (`data`, `datasets`, `labels`,
    # `colors`, `yAxes`), carried as JSON lists by the generator; the attributes the module does not carry are left out.
    LINE_DATA = {"data", "datasets", "labels", "colors", "yAxes"}
    LINE = {"legend", "width", "height", "fixedAspectRatioScaling", "scaleReferenceSize", "xAxisType",
            "yAxisPosition", "showGrid", "showGridX", "showGridY", "showTickMarks", "rangeLabels", "showPoints", "lineMode",
            "unit", "timeDisplay", "xTicksLimit", "xStepSize", "yTicksLimit", "yStepSize", "priority"}
    LINE_LEFT_OUT = {"state", "frameStyle", "borderRadiusPosition", "borderRadiusPositionExternalScales", "instrumentMode",
                     "borderRadius", "showDebugOverlay"}
    DONUT = {"priority", "half", "showOuterLabels", "showUnit", "outerLabelUnit", "outerLabelMaxLength", "outerLabelDecimalPlaces",
             "centerReadoutLabel", "centerReadoutUnit", "max", "thickness", "legend", "fixedHeight"}
    PIE = {"priority", "showOuterLabels", "showUnit", "sunburst", "outerLabelUnit", "outerLabelMaxLength", "outerLabelDecimalPlaces",
           "legend", "fixedHeight"}
    POLAR = {"priority", "monochrome", "discreteColorStops", "showSectorLabels", "showUnit", "showOuterLabels", "outerLabelUnit",
             "outerLabelMaxLength", "outerLabelDecimalPlaces", "fixedHeight", "legend"}
    RADIAL = {"priority", "max", "circumference", "legend", "fixedHeight", "minRingThickness"}
    # batch C2: the building blocks. A bar's scale flags and advice zones are fields without an attribute (hasScale, showLabels,
    # advices); the attributes left out are the nullable enumerations and the instrument mode (`gen_module_assets.BAR_LEFT_OUT`).
    SCALE_EVENT = {"cadre.ob.barhorizontal", "cadre.ob.barvertical"}
    FRAME_EVENT = {"cadre.ob.instrumentradial"}      # `frame-changed` reports the computed frame to a parent; nothing listens
    BAR_FIELDS = {"hasScale", "showLabels", "advices"}
    BAR_LEFT_OUT = {"barContainerStyle", "borderRadiusPosition", "instrumentMode", "borderRadius"}
    BAR = {"minValue", "maxValue", "side", "fixedAspectRatio", "scaleReferenceSize", "showMainTickmarkLabels", "hasBar",
           "scaleBackground", "barThickness", "tickThickness", "labelThickness", "primaryTickmarkInterval",
           "secondaryTickmarkInterval", "tertiaryTickmarkInterval", "scaleType", "frameStyle", "priority", "fillMode", "fillMin",
           "fillMax", "value", "state", "advicePosition", "highlightCurrentValue", "setpoint", "newSetpoint", "touching",
           "autoAtSetpointDeadband", "setpointAtZeroDeadband", "setpointOverride", "animateSetpoint"} | BAR_FIELDS
    RADIAL_INSTRUMENT = {"state", "priority", "value", "maxValue", "minValue", "needleColor", "barColor", "showLabels",
                         "primaryTickmarkInterval", "secondaryTickmarkInterval", "tertiaryTickmarkInterval", "type", "needleType",
                         "tickmarksInside", "tickmarkStyle", "clipTop", "clipBottom", "clipLeft", "clipRight", "endLabelsMaxMin",
                         "zoomToFitArc", "faceDiameter", "setpoint", "newSetpoint", "touching", "autoAtSetpointDeadband",
                         "setpointAtZeroDeadband", "setpointOverride", "animateSetpoint", "advices"}
    READOUT_BLOCK = {"variant", "value", "valueType", "size", "enhanced", "weight", "hasDegree", "hasIcon", "fractionDigits",
                     "maxDigits", "hintedZeros", "hasSignSpacer", "spaceReserver", "off", "offText", "alignment", "category",
                     "active", "touching", "hidePhase"}
    CHART_DATA = {"cadre.ob.instrumentradial": {"advices"}, "cadre.ob.barhorizontal": BAR_FIELDS, "cadre.ob.barvertical": BAR_FIELDS, "cadre.ob.areagraph": LINE_DATA, "cadre.ob.linegraph": LINE_DATA, "cadre.ob.donutchart": {"data", "colors"},
                  "cadre.ob.piechart": {"data", "colors"}, "cadre.ob.polarchart": {"data", "colors"},
                  "cadre.ob.radialbarchart": {"data", "colors"}}
    CHART_LEFT_OUT = {"cadre.ob.instrumentradial": set(), "cadre.ob.readoutblock": {"valueSize", "dataQuality", "alert"}, "cadre.ob.barhorizontal": BAR_LEFT_OUT, "cadre.ob.barvertical": BAR_LEFT_OUT, "cadre.ob.areagraph": LINE_LEFT_OUT, "cadre.ob.linegraph": LINE_LEFT_OUT,
                      "cadre.ob.donutchart": {"showDebugOverlay"}, "cadre.ob.piechart": {"showDebugOverlay"},
                      "cadre.ob.polarchart": {"showDebugOverlay"}, "cadre.ob.radialbarchart": {"showDebugOverlay"}}
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
        # batch C1: the bars and graphs (module-only, display only)
        "cadre.ob.areagraph": ("obc-area-graph", "src/bars-graphs/area-graph/area-graph.ts",
                               LINE | LINE_DATA | {"fillMode", "stacked"}, {"width": 480, "height": 320}),
        "cadre.ob.donutchart": ("obc-donut-chart", "src/bars-graphs/donut-chart/donut-chart.ts",
                                DONUT | {"data", "colors"}, {"width": 480, "height": 320}),
        "cadre.ob.piechart": ("obc-pie-chart", "src/bars-graphs/pie-chart/pie-chart.ts",
                              PIE | {"data", "colors"}, {"width": 480, "height": 320}),
        "cadre.ob.polarchart": ("obc-polar-chart", "src/bars-graphs/polar-chart/polar-chart.ts",
                                POLAR | {"data", "colors"}, {"width": 480, "height": 320}),
        "cadre.ob.radialbarchart": ("obc-radial-bar-chart", "src/bars-graphs/radial-bar-chart/radial-bar-chart.ts",
                                    RADIAL | {"data", "colors"}, {"width": 480, "height": 320}),
        "cadre.ob.linegraph": ("obc-line-graph", "src/bars-graphs/line-graph/line-graph.ts",
                               LINE | LINE_DATA, {"width": 480, "height": 320}),
        # batch C2: the building blocks (module-only, display only)
        "cadre.ob.barhorizontal": ("obc-bar-horizontal", "src/building-blocks/bar-horizontal/bar-horizontal.ts",
                                   BAR | {"width", "paddingLeft", "paddingRight"}, {"width": 480, "height": 128}),
        "cadre.ob.barvertical": ("obc-bar-vertical", "src/building-blocks/bar-vertical/bar-vertical.ts",
                                 BAR | {"height", "paddingTop", "paddingBottom"}, {"width": 128, "height": 320}),
        "cadre.ob.instrumentradial": ("obc-instrument-radial", "src/building-blocks/instrument-radial/instrument-radial.ts",
                                      RADIAL_INSTRUMENT, {"width": 240, "height": 240}),
        "cadre.ob.readoutblock": ("obc-readout-block", "src/building-blocks/readout-block/readout-block.ts",
                                  READOUT_BLOCK, {"width": 144, "height": 64}),
        "cadre.ob.circularprogress": ("obc-circular-progress", "src/building-blocks/circular-progress/circular-progress.ts",
                                      {"mode", "value", "strokeWidth", "viewBoxSize", "padding"}, {"width": 48, "height": 48}),
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
             "cadre.ob.transmitterbutton": "transmitterbutton", "cadre.ob.areagraph": "areagraph",
             "cadre.ob.linegraph": "linegraph",
             "cadre.ob.donutchart": "donutchart",
             "cadre.ob.piechart": "piechart",
             "cadre.ob.polarchart": "polarchart",
             "cadre.ob.radialbarchart": "radialbarchart",
             "cadre.ob.barhorizontal": "barhorizontal",
             "cadre.ob.barvertical": "barvertical",
             "cadre.ob.circularprogress": "circularprogress",
             "cadre.ob.instrumentradial": "instrumentradial",
             "cadre.ob.readoutblock": "readoutblock"}

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
            left_out = {"lineType"} if ctype == "cadre.ob.automationreadout" else self.CHART_LEFT_OUT.get(ctype, set())
            self.assertEqual(declared - left_out, attrs - self.CHART_DATA.get(ctype, set()), ctype)
            # the series of a chart are public fields the manifest lists without an attribute
            fields = {m["name"] for m in decl.get("members", []) if m.get("kind") == "field"}
            self.assertLessEqual(self.CHART_DATA.get(ctype, set()), fields, ctype)
            # a `click` is the only event among them, and it is not wired (display only, wiki 17.18 and 17.19)
            # C2: a bar reports the size its scale needs to a parent chart (`scale-dimensions-changed`); nothing listens
            self.assertEqual([e["name"] for e in decl.get("events", [])],
                             ["click"] if ctype in self.CLICK else ["position-selected"] if ctype in self.SELECTED
                             else ["scale-dimensions-changed"] if ctype in self.SCALE_EVENT
                             else ["frame-changed"] if ctype in self.FRAME_EVENT else [], ctype)

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

    def test_the_charts_carry_their_series_as_json_lists_and_the_wrapper_hands_the_element_a_copy(self):
        line = {"data": "points", "datasets": "datasets", "labels": "labels", "colors": "colors", "yAxes": "yaxes"}
        kinds = {"cadre.ob.areagraph": line, "cadre.ob.linegraph": line,
                 "cadre.ob.donutchart": {"data": "segments", "colors": "colors"},
                 "cadre.ob.piechart": {"data": "piesegments", "colors": "colors"},
                 "cadre.ob.polarchart": {"data": "segments", "colors": "colors"},
                 "cadre.ob.radialbarchart": {"data": "rings", "colors": "colors"}}
        for ctype, data in kinds.items():
            props = schema_of(ctype)["properties"]
            for name, kind in data.items():
                self.assertEqual((props[name]["type"], props[name]["default"]), ("array", []), (ctype, name))
                self.assertIn(f'{{"name":"{name}","kind":"{kind}"}}', self.spec_of(ctype), (ctype, name))
            self.assertEqual(props["colors"]["items"], {"type": "string"}, ctype)
            if ctype == "cadre.ob.radialbarchart":     # one number for each ring
                self.assertEqual(props["data"]["items"], {"type": "number"})
            elif "datasets" in props:
                self.assertEqual(props["data"]["items"]["required"], ["value"], ctype)
                self.assertEqual(props["datasets"]["items"]["required"], ["data"], ctype)
                self.assertEqual(sorted(props["yAxes"]["items"]["properties"]), ["grid", "id", "max", "min", "position"], ctype)
            else:
                self.assertEqual(props["data"]["items"]["required"], ["label", "value"], ctype)
            if ctype == "cadre.ob.piechart":     # the sunburst's subsegments
                self.assertEqual(props["data"]["items"]["properties"]["children"]["items"]["required"], ["label", "value"])
            for left_out in self.CHART_LEFT_OUT[ctype]:
                self.assertNotIn(left_out, props, (ctype, left_out))
        # Chart.js writes to the arrays it is given: the wrapper copies the list the property tree holds
        self.assertIn("function toRecords(v)", JS)
        self.assertIn("rings: function (v)", JS)
        self.assertIn("points: toRecords, datasets: toRecords", JS)

    def test_the_bars_carry_the_scale_flags_and_the_advice_zones_the_manifest_gives_as_fields(self):
        # C2: `hasScale` and `showLabels` are true by default in the element and have no attribute; `advices` is a list of zones
        for ctype in ("cadre.ob.barhorizontal", "cadre.ob.barvertical"):
            props = schema_of(ctype)["properties"]
            for flag in ("hasScale", "showLabels"):
                self.assertEqual((props[flag]["type"], props[flag]["default"]), ("boolean", True), (ctype, flag))
                self.assertIn(f'{{"name":"{flag}","kind":"boolean","def":true}}', self.spec_of(ctype), (ctype, flag))
            self.assertEqual((props["advices"]["type"], props["advices"]["default"]), ("array", []), ctype)
            self.assertEqual(props["advices"]["items"]["required"], ["min", "max", "type"], ctype)
            self.assertEqual(props["advices"]["items"]["properties"]["type"]["enum"], ["advice", "caution"], ctype)
            self.assertIn('{"name":"advices","kind":"linearadvices"}', self.spec_of(ctype), ctype)
            for left_out in self.BAR_LEFT_OUT:
                self.assertNotIn(left_out, props, (ctype, left_out))
            # the setpoint and the value are nullable numbers: undefined (no marker, no fill) until a tag gives one
            for name in ("value", "setpoint", "newSetpoint"):
                self.assertEqual((props[name]["type"], props[name]["default"]), (["number", "null"], None), (ctype, name))
        self.assertIn("linearadvices: toRecords", JS)
        # the radial instrument names its zone limits `minValue` and `maxValue` (the pinned `GaugeRadialAdvice`)
        radial = schema_of("cadre.ob.instrumentradial")["properties"]["advices"]
        self.assertEqual(radial["items"]["required"], ["minValue", "maxValue", "type"])
        self.assertIn('{"name":"advices","kind":"radialadvices"}', self.spec_of("cadre.ob.instrumentradial"))
        self.assertIn("radialadvices: toRecords", JS)

    def test_the_readout_block_carries_a_number_or_a_text_as_its_value(self):
        # C2: the element's `value` is `number | string | null`, which no earlier element had; the wrapper hands it a number as a
        # number, anything else as text, and a blank or missing value as null (the unavailable dash)
        props = schema_of("cadre.ob.readoutblock")["properties"]
        self.assertEqual((props["value"]["type"], props["value"]["default"]), (["number", "string", "null"], None))
        self.assertIn('{"name":"value","kind":"nvalue","def":null}', self.spec_of("cadre.ob.readoutblock"))
        self.assertIn("case 'nvalue':", JS)
        # a frame configuration, the size of the number, and the data quality are not carried
        for left_out in ("alert", "valueSize", "dataQuality"):
            self.assertNotIn(left_out, props)

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
        # the frame components (T2, F1) are module-only kinds too, tested by `FrameComponents` with their own cases
        return [k for k in self.screen.MODULE_ONLY if not self.is_symbol(k) and k not in self.screen.FRAME_ONLY]

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
            "area-graph", "automation-badge", "automation-readout", "bar-horizontal", "bar-vertical", "circular-progress", "donut-chart", "gauge-generator", "gauge-motors-and-pumps", "gauge-valve", "heat-exchanger", "heat-pump", "hydraulic-check-valve",
            "hydraulic-separator", "hydraulic-valve-4-3", "hydraulic-valve-x-2", "indicator-battery", "indicator-engine", "indicator-tank-atmospheric",
            "instrument-radial", "line-graph", "pie-chart", "polar-chart", "radial-bar-chart", "readout-block", "transmitter-button", "valve-analog-three-way-icon", "valve-analog-two-way-icon"])
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
                                             "adviceValue": 10, "hasSetPoint": True, "setpointValue": 11},
                      "area-graph": {"fillMode": "solid", "stacked": True, "legend": True, "xAxisType": "time",
                                     "data": [{"x": 1767225600000, "value": 12}, {"x": 1767226200000, "value": 18}],
                                     "datasets": [{"label": "A", "data": [{"x": 1767225600000, "y": 3}]}],
                                     "colors": ["#7a4aa8"], "yAxes": [{"id": "a", "position": "right", "min": 0}]},
                      "line-graph": {"lineMode": "stepped", "showPoints": True, "xAxisType": "number", "unit": "m3/h",
                                     "data": [{"x": 1, "value": 12}, {"x": 5, "value": 18}],
                                     "datasets": [{"label": "A", "data": [{"x": 1, "y": 3}]}],
                                     "colors": ["#7a4aa8"], "yAxes": [{"id": "a", "min": 0, "max": 40, "grid": True}]},
                      "donut-chart": {"half": True, "showOuterLabels": True, "max": 200, "thickness": 40, "centerReadoutLabel": "Load",
                                      "data": [{"label": "Pumps", "value": 42}, {"label": "Fans", "value": 18}],
                                      "colors": ["#7a4aa8", "#2e8b57"]},
                      "pie-chart": {"sunburst": True, "showOuterLabels": True, "showUnit": True, "outerLabelUnit": "kW",
                                    "data": [{"label": "Pumps", "value": 42, "children": [{"label": "Duty", "value": 30}]},
                                             {"label": "Fans", "value": 18}]},
                      "polar-chart": {"discreteColorStops": True, "showOuterLabels": True, "showSectorLabels": True,
                                      "monochrome": True, "outerLabelUnit": "deg",
                                      "data": [{"label": "A", "value": 20}, {"label": "B", "value": 35}],
                                      "colors": ["#3a6ea5", "#2e8b57"]},
                      "radial-bar-chart": {"max": 200, "circumference": 360, "minRingThickness": 8, "data": [120, 80, 40],
                                           "colors": ["#7a4aa8"]},
                      "bar-horizontal": {"hasBar": True, "value": 42, "setpoint": 70, "width": 400, "showLabels": False,
                                         "advices": [{"min": 60, "max": 80, "type": "advice", "hinted": False}]},
                      "bar-vertical": {"hasBar": True, "value": 42, "setpoint": 70, "height": 240, "showLabels": False,
                                       "advices": [{"min": 60, "max": 80, "type": "caution", "hinted": True}]},
                      "circular-progress": {"mode": "determinate", "value": 65, "strokeWidth": 6},
                      "instrument-radial": {"type": "needle", "value": 42, "showLabels": True, "setpoint": 70, "needleColor": "#7a4aa8",
                                            "advices": [{"minValue": 60, "maxValue": 80, "type": "caution", "hinted": True}]},
                      "readout-block": {"variant": "advice", "category": "caution", "active": True, "value": "AUTO", "valueType": "text"}}[kind]
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
            "transmitter-button": ("value", "adviceValue", "setpointValue"),
            # C1: the series and the colours of a chart are lists of JSON (a Document tag or a binding that returns one)
            "area-graph": ("data", "datasets", "labels", "colors", "yAxes", "legend", "unit"),
            "line-graph": ("data", "datasets", "labels", "colors", "yAxes", "legend", "unit"),
            "donut-chart": ("data", "colors", "max", "centerReadoutLabel", "centerReadoutUnit"),
            "pie-chart": ("data", "colors", "legend"), "polar-chart": ("data", "colors", "legend"),
            "radial-bar-chart": ("data", "colors", "max", "legend"),
            # C2: the level, the setpoint marker and the advice zones of a bar (the scheme is `state`)
            "bar-horizontal": ("value", "setpoint", "newSetpoint", "state", "priority", "advices"),
            "bar-vertical": ("value", "setpoint", "newSetpoint", "state", "priority", "advices"),
            # the ring fills with `value` (0 to 100) in the determinate and progressive modes
            "circular-progress": ("value", "mode"),
            # the needle or arc at `value`, the setpoint marker, the scheme and the advice zones of the dial
            "instrument-radial": ("value", "setpoint", "newSetpoint", "state", "priority", "advices"),
            # the block's number or text, whether it reads as off, its advice category and whether the advice is triggered
            "readout-block": ("value", "off", "category", "active")}

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
                    stated.setdefault(k, set()).add(json.dumps(v) if isinstance(v, list) else v)
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
            if "data" in props and "variant" in props:   # a trend case carries the series; no other case does
                self.assertEqual({tuple(s["params"]["data"]) for s in mine if "data" in s["params"]},
                                 {tuple(self.testbench.GLYPH_SERIES)}, kind)
                self.assertTrue(all(s["params"].get("variant") == "trend" for s in mine if "data" in s["params"]), kind)
            self.assertEqual(len(mine), {"automation-badge": 21, "hydraulic-check-valve": 2, "valve-analog-two-way-icon": 5,
                                         "valve-analog-three-way-icon": 7, "indicator-battery": 11, "indicator-engine": 6,
                                         "indicator-tank-atmospheric": 11, "automation-readout": 10, "heat-exchanger": 44, "heat-pump": 44, "hydraulic-separator": 44, "gauge-generator": 37, "gauge-motors-and-pumps": 38, "gauge-valve": 26, "hydraulic-valve-4-3": 10, "hydraulic-valve-x-2": 8, "transmitter-button": 22, "area-graph": 39, "line-graph": 35, "donut-chart": 22, "pie-chart": 17, "polar-chart": 20, "radial-bar-chart": 15, "bar-horizontal": 58, "bar-vertical": 58, "circular-progress": 12, "instrument-radial": 42, "readout-block": 40}[kind], kind)
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
        self.assertIn("ce.fireComponentEvent(ev.name, payload(ev.payload, e, this.el, node, ev))", JS)

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


class FrameMechanisms(unittest.TestCase):
    """The mechanisms of the frame components (tranche T2, batch F1; wiki page 12 section 17.23): the slot properties (text and
    icon), the `items` property and the event payload kinds, all driven by tables of the generator, so that a later batch adds
    a component by entries only. The browser side is proved by `module/tools/harness/frame.mjs` and `items.mjs`."""

    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, str(MODULE / "tools"))
        import gen_module_assets
        cls.gen = gen_module_assets
        cls.manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                                  .read_text(encoding="utf-8"))

    def test_a_composite_renders_nested_elements_and_carries_their_properties_and_events(self):
        """The parts of the top bar (T2, batch F4): the entry key `parts`, checked against the manifest, and the wrapper."""
        g = self.gen
        top = next(c for c in g.COMPONENTS if c["tag"] == "obc-top-bar")
        enum_map = g.enums()
        g.MANIFEST.clear()
        g.MANIFEST.update(self.manifest)
        g.DEFAULTS.clear()
        g.DEFAULTS.update(json.loads((MODULE / "web/defaults.json").read_text(encoding="utf-8")))
        parts = g.part_specs(top, enum_map)
        self.assertEqual([(p["tag"], p["slot"]) for p in parts], [("obc-alert-button", "alerts"), ("obc-clock", "clock")])
        self.assertEqual([f["name"] for f in parts[0]["fields"]], ["nAlerts", "counter", "alertType", "blinking", "showSilenceButton"])
        self.assertEqual({f["name"]: f["kind"] for f in parts[0]["fields"]}["alertType"], "ustring")      # empty is idle
        self.assertIs(parts[0]["props"]["showSilenceButton"]["default"], False)
        self.assertIs(parts[0]["props"]["counter"]["default"], True)      # the composite's own default (the element's is false)
        self.assertEqual(parts[1]["fixed"], {"isClickable": False})
        # a property the element does not carry, a slot the host does not declare, a field that is no field and an event that is
        # not the element's are all refused
        for bad in ({"tag": "obc-alert-button", "slot": "alerts", "fields": ["noSuchProperty"]},
                    {"tag": "obc-alert-button", "slot": "no-such-slot", "fields": ["nAlerts"]},
                    {"tag": "obc-clock", "slot": "clock", "fields": ["date"], "fixed": {"noSuchField": True}},
                    {"tag": "obc-alert-button", "slot": "alerts", "fields": ["nAlerts"], "events": ["no-such-event"]},
                    {"tag": "obc-alert-button", "slot": "alerts", "fields": ["nAlerts"], "defaults": {"large": True}}):
            with self.assertRaises(SystemExit, msg=str(bad)):
                g.part_specs({"tag": "obc-top-bar", "parts": [bad]}, enum_map)
        # a carried property that the host already has is refused (the top bar's own `showDate` and the clock's)
        defaults = {k: (None if v == "__undefined__" else v) for k, v in g.DEFAULTS["obc-top-bar"].items()}
        clash = {**top, "exclude": [], "parts": [{"tag": "obc-clock", "slot": "clock", "fields": ["date", "showDate"]}]}
        with self.assertRaises(SystemExit):
            g.schema_for(clash, g.declaration(self.manifest, "obc-top-bar"), enum_map, defaults)
        # a field fixed by the wrapper cannot also be a property
        with self.assertRaises(SystemExit):
            g.schema_for({**top, "fixed": {"appTitle": "x"}}, g.declaration(self.manifest, "obc-top-bar"), enum_map, defaults)
        # an event of the kind detail needs its fields
        with self.assertRaises(SystemExit):
            g.event_fields({"tag": "obc-app-menu"}, "search")
        # the wrapper: refs for the parts, their listeners and their properties
        for text in ("this.partRefs = (spec.parts || []).map(", "setPart(i, n) {", "applyPart(i) {", "ev.part === i",
                     "(spec.parts || []).forEach((pt, i) => kids.push(h(pt.tag, { slot: pt.slot, key: 'part:' + i, ref: this.partRefs[i] })))"):
            self.assertIn(text, JS)

    def test_an_element_that_changes_itself_writes_its_property_back_and_a_detail_event_states_its_fields(self):
        self.assertRegex(JS, r'"dom":"palette-changed","name":"onPaletteChanged","payload":"detail","fields":\[\{"name":"value","type":"string"\}\],"write":"palette","from":"value"')
        self.assertRegex(JS, r'"dom":"brightness-changed","name":"onBrightnessChanged","payload":"detail","fields":\[\{"name":"value","type":"number"\}\],"write":"brightness","from":"value"')
        self.assertRegex(JS, r'"dom":"change","name":"onCommandChange","payload":"detail","fields":\[\{"name":"inCommand","type":"boolean"\}\],"write":"inCommand","from":"inCommand"')
        self.assertRegex(JS, r'"dom":"to-sub-menu-click","name":"onSubMenuClick","payload":"none","write":"activeSubMenu","from":"@element"')
        # a link switch changes no property of the component, so it writes nothing
        self.assertNotRegex(JS, r'"dom":"link-palette-changed"[^}]*"write"')
        self.assertIn("if (v !== undefined) this.put(ev.write, Array.isArray(v) ? v.slice() : v);", JS)
        rows = self.gen.event_fields({"tag": "x", "eventFields": {"e": [("a", "string", "A"), ("b", "number", "B", "detailKey")]}}, "e")
        self.assertEqual(rows, [{"name": "a", "type": "string", "text": "A"}, {"name": "b", "type": "number", "text": "B", "from": "detailKey"}])
        # the payload of a detail event is built from the fields and coerced to their types (a detail that is no object is the one value)
        for text in ("if (kind === 'detail') {", "(ev && ev.fields) || []", "f.type === 'boolean' ? !!v"):
            self.assertIn(text, JS)

    def test_the_stylesheet_stretches_the_top_bar_to_its_box_and_not_its_height(self):
        css = (MODULE / "gateway/src/main/resources/mounted/css/cadre-ob.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.cadre-ob > obc-top-bar \{\s*flex: 1 1 auto;\s*width: 100%;\s*\}")
        self.assertNotRegex(css, r"\.cadre-ob > obc-top-bar \{[^}]*height")

    def test_the_top_bar_carries_the_alert_button_and_the_clock_and_not_its_own_breadcrumb(self):
        c = COMPONENTS["cadre.ob.topbar"]
        self.assertEqual(c["parts"], {"obc-alert-button": {"slot": "alerts", "props": ["nAlerts", "counter", "alertType", "blinking",
                                                                                      "showSilenceButton"]},
                                      "obc-clock": {"slot": "clock", "props": ["date", "showSeconds", "timeZoneOffsetHours"]}})
        props = schema_of("cadre.ob.topbar")["properties"]
        self.assertIs(props["showSilenceButton"]["default"], False)      # owner's answer 4
        self.assertEqual(props["alertType"]["enum"][0], "")
        self.assertEqual(c["slots"], {"appIconName": {"slot": "app-icon", "kind": "icon"}, "commandButtonText": {"slot": "command-button", "kind": "text"}})
        self.assertNotIn("showDate", props)
        # the events of the nested alert button are listened to on the node (they do not bubble); the rest on the host
        self.assertRegex(JS, r'"dom":"click-alert","name":"onAlertClick","payload":"none","part":0')
        self.assertRegex(JS, r'"dom":"click-silence","name":"onSilenceClick","payload":"none","part":0')
        self.assertRegex(JS, r'"dom":"menu-button-clicked","name":"onMenuButtonClick","payload":"none"\}')
        self.assertRegex(JS, r'"parts":\[\{"tag":"obc-alert-button","slot":"alerts"')
        self.assertRegex(JS, r'"fixed":\{"isClickable":false\}')
        # the breadcrumb of the settings mode is data (label and href); the frame keeps the Cadre crumb and does not use it
        crumbs = props["breadcrumbItems"]
        self.assertEqual(set(crumbs["items"]["properties"]), {"label", "href"})
        self.assertIn("frame does not use", props["settings"]["description"])
        self.assertIn("frame keeps its own crumb row", crumbs["description"])
        self.assertIs(props["settings"]["default"], False)

    def test_the_icon_list_is_the_imports_of_icons_js_and_each_is_an_icon_of_the_pinned_package(self):
        names = self.gen.icon_names()
        text = (MODULE / "web/icons.js").read_text(encoding="utf-8")
        self.assertEqual(names, re.findall(r"dist/icons/icon-([a-z0-9-]+)\.js", text))
        self.assertIn("import './icons.js';", (MODULE / "web/entry.js").read_text(encoding="utf-8"))
        icons = MODULE / "web/node_modules/@oicl/openbridge-webcomponents/dist/icons"
        for n in names:
            self.assertTrue((icons / f"icon-{n}.js").is_file(), n)
        self.assertIn('var ICONS = ' + json.dumps(names, separators=(",", ":")) + ';', JS)

    def test_every_icon_slot_property_is_an_enumeration_of_exactly_those_icons(self):
        names = self.gen.icon_names()
        seen = 0
        for ctype, c in COMPONENTS.items():
            for prop, sl in c.get("slots", {}).items():
                p = schema_of(ctype)["properties"][prop]
                if sl["kind"] == "icon":
                    seen += 1
                    self.assertEqual((p["type"], p["default"], p["enum"]), ("string", "", [""] + names), f"{ctype}.{prop}")
                else:
                    self.assertEqual((p["type"], p["default"], "enum" in p), ("string", "", False), f"{ctype}.{prop}")
        self.assertGreaterEqual(seen, 6)

    def test_a_slot_must_be_one_the_manifest_declares_and_its_property_must_be_free(self):
        decl = self.gen.declaration(self.manifest, "obc-tooltip")
        spec = {"tag": "obc-tooltip", "slots": [{"slot": "nowhere", "kind": "text"}]}
        with self.assertRaises(SystemExit):
            self.gen.slot_specs(spec, decl, set())
        spec = {"tag": "obc-tooltip", "slots": [{"slot": "icon", "kind": "icon"}]}
        with self.assertRaises(SystemExit):
            self.gen.slot_specs(spec, decl, {"iconName"})
        spec = {"tag": "obc-tooltip", "slots": [{"slot": "icon", "kind": "icon", "property": "glyph"}]}
        self.assertEqual([s["name"] for s in self.gen.slot_specs(spec, decl, {"iconName"})], ["glyph"])
        with self.assertRaises(SystemExit):
            self.gen.slot_specs({"tag": "obc-tooltip", "slots": [{"slot": "icon", "kind": "picture"}]}, decl, set())

    def test_slot_property_names_follow_the_slot_names(self):
        decl = self.gen.declaration(self.manifest, "obc-toggletip")
        spec = {"tag": "obc-toggletip", "slots": [{"slot": "leading-icon", "kind": "icon"}, {"slot": "content", "kind": "text"}]}
        self.assertEqual([s["name"] for s in self.gen.slot_specs(spec, decl, set())], ["leadingIconName", "content"])
        decl = self.gen.declaration(self.manifest, "obc-notification-badge-button")
        spec = {"tag": "obc-notification-badge-button", "slots": [{"slot": "", "kind": "text"}, {"slot": "", "kind": "icon"}]}
        self.assertEqual([s["name"] for s in self.gen.slot_specs(spec, decl, set())], ["text", "iconName"])

    def test_the_item_table_holds_the_manifests_attributes_and_refuses_a_tag_it_does_not_declare(self):
        spec = {"items": {"items": {"tags": ["obc-app-button"]}}}
        old = dict(self.gen.ITEM_CHILDREN)
        try:
            self.gen.ITEM_CHILDREN.clear()      # the real rows (the alert menu's, F2) are not this test's subject
            self.gen.ITEM_CHILDREN["obc-app-button"] = ["obc-notification-badge-button"]
            table = self.gen.build_item_table(self.manifest, [spec])
            self.assertEqual(set(table), {"obc-app-button", "obc-notification-badge-button"})
            self.assertEqual(table["obc-app-button"], {"props": ["label", "checked", "integration", "size", "disabled",
                                                                  "showLabel"],      # the field `showLabel` is a row of ITEM_FIELDS (F4)
                                                       "kids": ["obc-notification-badge-button"]})
            with self.assertRaises(SystemExit):
                self.gen.build_item_table(self.manifest, [{"items": {"items": {"tags": ["obc-no-such-element"]}}}])
            schema = self.gen.items_schema({"tags": ["obc-app-button"], "describe": "Things"}, table)
        finally:
            self.gen.ITEM_CHILDREN.clear()
            self.gen.ITEM_CHILDREN.update(old)
        self.assertEqual((schema["type"], schema["default"], schema["items"]["properties"]["tag"]["enum"]),
                         ("array", [], ["obc-app-button"]))
        self.assertIn("Things", schema["description"])
        self.assertIn("label, checked", schema["description"])

    def test_the_wrapper_builds_items_as_properties_from_a_fixed_allow_list(self):
        for text in ("function buildItem(o, allowed, depth, slot)", "ITEM_DEPTH", "el.setAttribute('data-item-id'",
                     "applyItems(el, p)", "document.createElement(tag)", "if (names.indexOf(k) >= 0) el[k] = o[k];",
                     "out[d.name] = tree.readArray(d.name, []);"):
            self.assertIn(text, JS)
        self.assertIn('var ITEM_PLAIN = ["span"];', JS)
        self.assertIn("var ITEM_DEPTH = 8;", JS)
        self.assertRegex(JS, r"var ITEMS = \{[^;]*\};")
        self.assertNotIn("innerHTML = o", JS)          # an item is never markup

    def test_every_event_payload_kind_has_a_schema_and_every_carried_event_a_row(self):
        for dom, (name, kind, text) in self.gen.ALERT_EVENTS.items():
            self.assertIn(kind, self.gen.PAYLOAD_PROPS, dom)
            self.assertTrue(name.startswith("on") and name != "onClick", dom)
            self.assertTrue(text, dom)
        for ctype, c in COMPONENTS.items():
            for name, e in c.get("events", {}).items():
                schema = json.loads((MODULE / "common/src/main/resources" / e["schema"]).read_text(encoding="utf-8"))
                self.assertEqual(schema["type"], "object", name)
                self.assertTrue(schema["description"], name)
                self.assertIn(e["element"], self.gen.ALERT_EVENTS, name)
        for kind in ("notification", "label", "item"):
            self.assertIn("kind === '" + kind + "'", JS)

    def test_the_unset_while_empty_kind_gives_undefined(self):
        self.assertIn("case 'ustring': { var u = tree.readString(f.name, ''); return u === '' ? undefined : u; }", JS)
        self.assertIn('"name":"description","kind":"ustring"', JS.replace(" ", ""))
        self.assertIn('{"name":"label","kind":"ustring","def":""}'.replace(" ", ""), JS.replace(" ", ""))


class FrameComponents(unittest.TestCase):
    """The seven leaf components of batch F1: `obc-tooltip`, `obc-toggletip`, `obc-clock`, `obc-user-button`, `obc-app-button`,
    `obc-notification-button` and `obc-notification-badge-button`. Each carries exactly the manifest's attributes, its fields
    without an attribute and its slot properties, and its events (unwired)."""
    # component type: (tag, manifest path, the manifest's attributes, fields without an attribute, slot properties, events)
    ROWS = {
        "cadre.ob.tooltip": ("obc-tooltip", "src/components/tooltip/tooltip.ts", {"type", "variant", "label", "showIcon"}, set(),
                             {"iconName"}, {}),
        "cadre.ob.toggletip": ("obc-toggletip", "src/components/toggletip/toggletip.ts",
                               {"variant", "title", "description", "hasContent", "hasActions", "hasLeadingIcon", "hasTrailingIcon",
                                "customWidth", "primaryButtonLabel", "secondaryButtonLabel"}, set(),
                               {"leadingIconName", "trailingIconName", "content"},
                               {"onPrimaryAction": "primary-action", "onSecondaryAction": "secondary-action"}),
        "cadre.ob.clock": ("obc-clock", "src/components/clock/clock.ts",
                           {"date", "showSeconds", "showDate", "showTimezone", "timeZoneOffsetHours", "showYear", "showWeekday", "locale",
                            "hour12", "selected", "double", "activated", "integrationBarMode", "blinkOnlyBreakpointPx"},
                           {"isClickable"}, set(), {}),
        "cadre.ob.userbutton": ("obc-user-button", "src/components/user-button/user-button.ts",
                                {"variant", "size", "styleType", "static", "disabled", "initials", "label", "sublabel"}, set(),
                                {"iconName"}, {}),
        "cadre.ob.appbutton": ("obc-app-button", "src/components/app-button/app-button.ts",
                               {"label", "checked", "integration", "size", "disabled"}, {"showLabel"}, {"iconName"},
                               {"onPress": "click"}),
        "cadre.ob.notificationbutton": ("obc-notification-button", "src/components/notification-button/notification-button.ts",
                                        {"buttonStyle", "count", "showCount", "isActive", "ariaLabel"}, set(), {"iconName"},
                                        {"onNotificationClick": "obc-click"}),
        "cadre.ob.notificationbadgebutton": ("obc-notification-badge-button",
                                             "src/components/notification-badge-button/notification-badge-button.ts",
                                             {"openRight", "openLeft", "cornerLeft", "cornerRight", "icon", "disabled", "indent"}, set(),
                                             {"label", "iconName"}, {"onPress": "click"}),
        # batch F2: the alert button and the alert menu; `items` properties are listed in the sixth row of each, after the slots
        "cadre.ob.alertbuttonitem": ("obc-alert-button-item", "src/components/alert-button-item/alert-button-item.ts",
                                     {"type", "alertType", "nAlerts", "counter", "globalCounter", "shelvedCount", "blinking",
                                      "flashingSpeed", "fillHeight", "ariaLabel"}, set(), set(), {"onPress": "click"}),
        "cadre.ob.alertbutton": ("obc-alert-button", "src/components/alert-button/alert-button.ts",
                                 {"nAlerts", "alertType", "type", "large", "showSilenceButton", "silenceButtonDisabled", "counter",
                                  "globalCounter", "shelvedCount", "blinking", "flashingSpeed", "flatMaxBreakpointPx",
                                  "silenceButtonMinBreakpointPx"}, set(), set(),
                                 {"onAlertClick": "click-alert", "onSilenceClick": "click-silence"}),
        "cadre.ob.alertmenuitem": ("obc-alert-menu-item", "src/components/alert-menu-item/alert-menu-item.ts",
                                   {"hasIcon", "shelved", "title", "description", "day", "time", "status", "open", "size", "animateIntro",
                                    "secondaryActionLabel", "primaryActionState", "secondaryActionState"}, set(), {"iconName"},
                                   {"onItemClick": "item-click", "onAckClick": "ack-click", "onAckSecondaryClick": "ack-secondary-click"}),
        "cadre.ob.alertmenu": ("obc-alert-menu", "src/components/alert-menu/alert-menu.ts", {"hasShelved", "canAckAll"},
                               {"showSilenceButton", "showAlertListButton"}, set(),
                               {"onAckAllClick": "ack-all-visible-click", "onSilenceClick": "silence-click",
                                "onGoToAlertListClick": "go-to-alert-list-click", "onItemClick": "item-click", "onAckClick": "ack-click",
                                "onAckSecondaryClick": "ack-secondary-click"}),
        # batch F3: navigation, tree navigation and the breadcrumb (the attributes include the ones the container computes, see EXCLUDED)
        "cadre.ob.navigationitem": ("obc-navigation-item", "src/components/navigation-item/navigation-item.ts",
                                    {"label", "href", "checked", "variant", "group", "groupSelected", "hasIcon", "hasTrailingIcon", "treeMode",
                                     "treeBranches", "terminalType", "alerts"}, set(), {"iconName", "trailingIconName"}, {"onPress": "click"}),
        "cadre.ob.navigationitemgroup": ("obc-navigation-item-group", "src/components/navigation-item-group/navigation-item-group.ts",
                                         {"label", "href", "checked", "variant", "hug", "hasIcon", "treeMode", "treeBranches", "terminalType",
                                          "alerts", "defaultOpen"}, set(), {"iconName"}, {"onOpen": "open"}),
        "cadre.ob.navigationmenu": ("obc-navigation-menu", "src/components/navigation-menu/navigation-menu.ts",
                                    {"variant", "flyoutVariant", "smallScreen"}, set(), set(),
                                    {"onItemClick": "click", "onGroupOpen": "open"}),
        "cadre.ob.treenavigationitem": ("obc-tree-navigation-item", "src/components/tree-navigation-item/tree-navigation-item.ts",
                                        {"label", "branches", "expandable", "expanded", "checked", "disabled", "terminalType", "alerts", "href"},
                                        {"hasLeadingIcon"}, {"iconName"}, {"onPress": "click", "onExpandToggle": "expand-toggle"}),
        "cadre.ob.treenavigationgroup": ("obc-tree-navigation-group", "src/components/tree-navigation-group/tree-navigation-group.ts",
                                         {"label", "branches", "expanded", "checked", "disabled", "terminalType", "alerts", "href"},
                                         {"hasIcon"}, {"iconName"}, {"onExpandToggle": "expand-toggle"}),
        "cadre.ob.treenavigation": ("obc-tree-navigation", "src/components/tree-navigation/tree-navigation.ts", set(), set(), set(),
                                    {"onItemClick": "click", "onExpandToggle": "expand-toggle"}),
        "cadre.ob.breadcrumb": ("obc-breadcrumb", "src/components/breadcrumb/breadcrumb.ts", set(), {"iconOnly"}, set(),
                                {"onBreadcrumbClick": "breadcrumb-click"}),
        # batch F4: the menus and the top bar
        "cadre.ob.brilliancemenu": ("obc-brilliance-menu", "src/components/brilliance-menu/brilliance-menu.ts",
                                    {"palette", "brightness", "showLinkBrightness", "showLinkPalette", "variant", "brightnessUnit",
                                     "brightnessMax", "brightnessMinorStep", "brightnessMajorStep", "brightnessInputVariant",
                                     "showScreenControlLink"}, {"showBrightness", "showPalette"}, set(),
                                    {"onPaletteChanged": "palette-changed", "onBrightnessChanged": "brightness-changed",
                                     "onLinkPaletteChanged": "link-palette-changed", "onLinkBrightnessChanged": "link-brightness-changed",
                                     "onScreenControlLinkClick": "screen-control-link-clicked"}),
        "cadre.ob.usermenu": ("obc-user-menu", "src/components/user-menu/user-menu.ts",
                              {"type", "size", "hasRecentlySignedIn", "username", "password", "usernameError", "passwordError",
                               "userInitials", "userLabel", "userRole", "primaryActionId"}, set(), set(),
                              {"onSignInClick": "sign-in-click", "onSignOutClick": "sign-out-click",
                               "onUseAnotherAccountClick": "use-another-account-click"}),
        "cadre.ob.systemmenu": ("obc-system-menu", "src/components/system-menu/system-menu.ts",
                                {"condensed", "showSettingsButton", "activeSubMenu", "externalControl", "smallScreen"}, set(), set(),
                                {"onWifiClick": "wifi-click", "onAudioClick": "audio-click", "onAudioVolumeChange": "audio-volume-change",
                                 "onMicrophoneClick": "microphone-click", "onPushToTalkChange": "push-to-talk-change",
                                 "onBatterySavingModeChange": "battery-saving-mode-change", "onBatteryUsageClick": "battery-usage-click",
                                 "onWifiNetworkChange": "wifi-network-change", "onAudioOutputChange": "audio-output-change",
                                 "onMicrophoneInputChange": "microphone-input-change", "onBatteryModeChange": "battery-mode-change",
                                 "onSettingsClick": "settings-click", "onSubMenuClick": "to-sub-menu-click",
                                 "onWifiOptionsClick": "wifi-options-click", "onWifiDisconnectClick": "wifi-disconnect-click"}),
        "cadre.ob.appmenu": ("obc-app-menu", "src/components/app-menu/app-menu.ts", set(), set(), set(),
                             {"onSearch": "search", "onAppClick": "click"}),
        "cadre.ob.commandmenu": ("obc-command-menu", "src/components/command-menu/command-menu.ts", {"inCommand"}, {"showLocation"},
                                 {"commandIconName", "commandStatus", "commandDescription", "commandLocation", "takeCommandLabel",
                                  "releaseCommandLabel", "inCommandLabel", "noCommandLabel", "inCommandIconName"},
                                 {"onCommandChange": "change"}),
        "cadre.ob.topbar": ("obc-top-bar", "src/components/top-bar/top-bar.ts",
                            {"appTitle", "pageName", "menuButtonIcon", "menuButtonActivated", "dimmingButtonActivated", "appsButtonActivated",
                             "leftMoreButtonActivated", "userButtonActivated", "userButtonDisabled", "tall", "wideMenuButton", "showAppsButton",
                             "showDimmingButton", "showUserButton", "showClock", "showDate", "showAppIcon", "inactive", "appButtonBreakpointPx",
                             "dimmingButtonBreakpointPx", "appTitleBreakpointPx", "userButtonBreakpointPx", "appIconBreakpointPx", "settings",
                             "breadcrumbItems"}, set(), {"appIconName", "commandButtonText"},
                            {"onMenuButtonClick": "menu-button-clicked", "onDimmingButtonClick": "dimming-button-clicked",
                             "onAppsButtonClick": "apps-button-clicked", "onMoreButtonClick": "left-more-button-clicked",
                             "onUserButtonClick": "user-button-clicked", "onEmergencyBrightnessStart": "emergency-brightness-start",
                             "onEmergencyBrightnessStop": "emergency-brightness-stop", "onAlertClick": "click-alert",
                             "onSilenceClick": "click-silence", "onBack": "back", "onClose": "close", "onBreadcrumbClick": "breadcrumb-click"}),
        # batch F5: tabs, pivots, the modal window, the context menu input and the notification items
        "cadre.ob.tabitem": ("obc-tab-item", "src/components/tab-item/tab-item.ts",
                             {"hug", "centerContent", "checked", "hasClose", "hasLeadingIcon", "hasTitle", "hasDivider", "hasBadge", "icon",
                              "title", "showSubtitle", "subtitle", "disabled", "badgeType", "badgeSize", "badgeCount",
                              "showLeadingBadgeIcon"}, set(), {"leadingIconName", "badgeIconName"},
                             {"onTabClick": "tab-click", "onTabClose": "tab-close"}),
        "cadre.ob.tabrow": ("obc-tab-row", "src/components/tab-row/tab-row.ts",
                            {"tabs", "selectedTabId", "hasClose", "centerContent", "hug", "showSubtitle", "hasAddNewTab"}, set(), set(),
                            {"onTabSelected": "tab-selected", "onTabClosed": "tab-closed", "onAddNewTab": "add-new-tab"}),
        "cadre.ob.pivotitem": ("obc-pivot-item", "src/components/pivot-item/pivot-item.ts",
                               {"value", "selected", "direction", "hasLeadingIcon", "hasLabel", "label", "disabled"}, set(), {"iconName"},
                               {"onSelected": "selected"}),
        "cadre.ob.pivotitemgroup": ("obc-pivot-item-group", "src/components/pivot-item-group/pivot-item-group.ts",
                                    {"direction", "selectedValue", "allowDeselect"}, set(), set(), {"onChange": "change"}),
        "cadre.ob.modalwindow": ("obc-modal-window", "src/components/modal-window/modal-window.ts",
                                 {"size", "hasOptionalAction", "hasLeadingIcon"}, {"hasCancelAction", "hasCloseAction"},
                                 {"leadingIconName", "title", "content", "optionLabel", "cancelLabel", "doneLabel"},
                                 {"onCloseClick": "close-click", "onCancelClick": "cancel-click", "onDoneClick": "done-click",
                                  "onOptionClick": "option-click"}),
        "cadre.ob.contextmenuinput": ("obc-context-menu-input", "src/components/context-menu-input/context-menu-input.ts",
                                      {"type", "options", "selectedValues", "hasTitleBar", "title", "columnGroups", "itemsPerColumn",
                                       "multiSelect", "selectPerGroup"}, set(), set(),
                                      {"onClose": "close", "onItemClick": "item-click", "onChange": "change"}),
        "cadre.ob.notificationmenuitem": ("obc-notification-menu-item", "src/components/notification-menu-item/notification-menu-item.ts",
                                          {"hasIcon", "title", "description", "day", "time", "open", "size", "primaryActionLabel",
                                           "secondaryActionLabel"}, set(), {"iconName"},
                                          {"onItemClick": "item-click", "onPrimaryActionClick": "primary-action-click",
                                           "onSecondaryActionClick": "secondary-action-click"}),
        "cadre.ob.notificationmessageitem": ("obc-notification-message-item",
                                             "src/components/notification-message-item/notification-message-item.ts",
                                             {"title", "description", "time", "timeSecondary", "actionLabel", "type", "size", "hasTimestamp2",
                                              "hasSecondaryIcon", "large", "empty", "emptyText"}, {"showTitle", "showDescription", "showTimestamp"},
                                             {"secondaryIconName"},
                                             {"onMessageClick": "message-click", "onActionClick": "action-click"}),
        "cadre.ob.notificationfloatingitem": ("obc-notification-floating-item",
                                              "src/components/notification-floating-item/notification-floating-item.ts",
                                              {"type", "direction", "hasTimestamp", "hasDay", "action", "action2", "lineType"}, set(),
                                              {"primaryIconName", "title", "description", "time", "day", "actionLabel", "action2Label"},
                                              {"onActionClick": "action-click", "onAction2Click": "action2-click",
                                               "onDismissClick": "dismiss-click"}),
    }
    # the properties of the nested elements a composite renders itself (the top bar's alert button and clock), and their tags
    PARTS = {"cadre.ob.topbar": {"nAlerts", "counter", "alertType", "blinking", "showSilenceButton", "date", "showSeconds", "timeZoneOffsetHours"}}
    PART_TAGS = {"cadre.ob.topbar": ["obc-alert-button", "obc-clock"]}
    # the attributes the container computes, left out of the contract (the navigation menu in the tree variant, the tree navigation)
    EXCLUDED = {"cadre.ob.navigationitem": {"treeBranches"}, "cadre.ob.navigationitemgroup": {"treeBranches"},
                "cadre.ob.treenavigationitem": {"branches"}, "cadre.ob.treenavigationgroup": {"branches"},
                # the user menu: no credential, no recent users, no signed in actions (see test_the_user_menu_carries_no_credential)
                "cadre.ob.usermenu": {"username", "password", "usernameError", "passwordError", "hasRecentlySignedIn", "primaryActionId"},
                # the top bar's own `showDate` is unused by the element (its clock is slotted)
                "cadre.ob.topbar": {"showDate"},
                # the tab item's `icon` attribute is never read by the element; its `badges` field has no attribute and is not carried
                "cadre.ob.tabitem": {"icon"}}
    # the properties that are plain data (a list read as JSON, not child elements): the breadcrumb's own array
    DATA = {"cadre.ob.breadcrumb": {"items"}, "cadre.ob.topbar": {"breadcrumbItems"},
            # the system menu's four sections: fields without an attribute, carried as state objects
            "cadre.ob.systemmenu": {"wifiState", "audioState", "microphoneState", "batteryState"},
            "cadre.ob.tabrow": {"tabs"},
            "cadre.ob.contextmenuinput": {"options", "columnGroups", "selectedValues"}}
    # the `items` properties of a frame component (a list of child elements), with the tags each allows at the top level
    ITEMS = {"cadre.ob.alertmenuitem": {"alertIcon": ["obc-alert-icon"]}, "cadre.ob.alertmenu": {"items": ["obc-alert-menu-item"]},
             "cadre.ob.navigationitemgroup": {"items": ["obc-navigation-item", "obc-navigation-item-group"]},
             "cadre.ob.navigationmenu": {"items": ["obc-navigation-item", "obc-navigation-item-group"],
                                         "footerItems": ["obc-navigation-item", "obc-navigation-item-group"]},
             "cadre.ob.treenavigationgroup": {"items": ["obc-tree-navigation-item", "obc-tree-navigation-group"]},
             "cadre.ob.treenavigation": {"items": ["obc-tree-navigation-group", "obc-tree-navigation-item"]},
             "cadre.ob.appmenu": {"items": ["obc-app-button"]},
             "cadre.ob.pivotitemgroup": {"items": ["obc-pivot-item"]}}

    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        from hmi import library_profile, screen, testbench
        cls.screen, cls.testbench, cls.library_profile = screen, testbench, library_profile
        cls.manifest = json.loads((MODULE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                                  .read_text(encoding="utf-8"))

    def decl(self, path, tag):
        return next(d for m in self.manifest["modules"] if m["path"] == path
                    for d in m.get("declarations", []) if d.get("tagName") == tag)

    def test_each_contract_carries_the_manifests_attributes_fields_and_slot_properties(self):
        for ctype, (tag, path, attrs, fields, slots, events) in self.ROWS.items():
            c = COMPONENTS[ctype]
            self.assertEqual(c["element"], tag)
            self.assertEqual({a["fieldName"] for a in self.decl(path, tag).get("attributes", [])}, attrs, ctype)
            self.assertEqual(set(c["props"]) - {"componentSize"},
                             (attrs - self.EXCLUDED.get(ctype, set())) | fields | slots | set(self.ITEMS.get(ctype, {}))
                             | self.DATA.get(ctype, set()) | self.PARTS.get(ctype, set()), ctype)
            self.assertEqual(set(c.get("slots", {})), slots, ctype)
            self.assertEqual({n: i["tags"] for n, i in c.get("items", {}).items()}, self.ITEMS.get(ctype, {}), ctype)

    def test_the_events_are_the_elements_own_carried_and_not_wired(self):
        for ctype, (tag, path, attrs, fields, slots, events) in self.ROWS.items():
            c = COMPONENTS[ctype]
            declared = {e["name"] for e in self.decl(path, tag).get("events", [])}
            for tags in list(self.ITEMS.get(ctype, {}).values()) + [self.PART_TAGS.get(ctype, [])]:      # an event of a row or a nested element
                for t in tags:
                    declared |= {e["name"] for m in self.manifest["modules"] for d in m.get("declarations", [])
                                 if d.get("tagName") == t for e in d.get("events", [])}
            self.assertEqual({n: e["element"] for n, e in c.get("events", {}).items()}, events, ctype)
            self.assertTrue(set(events.values()) <= declared, ctype)
            for name, e in c.get("events", {}).items():
                self.assertTrue((MODULE / "common/src/main/resources" / e["schema"]).is_file(), name)
        # the clock and the user button declare no event: a press is the host's own click (the frame binds Perspective's onClick)
        self.assertNotIn("events", COMPONENTS["cadre.ob.clock"])
        self.assertNotIn("events", COMPONENTS["cadre.ob.userbutton"])
        self.assertEqual(self.decl(self.ROWS["cadre.ob.userbutton"][1], "obc-user-button").get("events", []), [])
        self.assertEqual(self.decl(self.ROWS["cadre.ob.clock"][1], "obc-clock").get("events", []), [])

    def test_the_payloads(self):
        for name, props in (("notificationbutton.onNotificationClick", {"count": "number", "isActive": "boolean"}),
                            ("toggletip.onPrimaryAction", {"label": "string"}), ("toggletip.onSecondaryAction", {"label": "string"}),
                            ("appbutton.onPress", {}), ("notificationbadgebutton.onPress", {}),
                            ("alertbutton.onAlertClick", {}), ("alertbutton.onSilenceClick", {}), ("alertbuttonitem.onPress", {}),
                            ("alertmenuitem.onItemClick", {}), ("alertmenuitem.onAckClick", {}), ("alertmenuitem.onAckSecondaryClick", {}),
                            ("alertmenu.onAckAllClick", {"mode": "string", "ids": "array"}),
                            ("alertmenu.onSilenceClick", {}), ("alertmenu.onGoToAlertListClick", {}),
                            ("alertmenu.onItemClick", {"id": "string", "tag": "string"}),
                            ("alertmenu.onAckClick", {"id": "string", "tag": "string"}),
                            ("alertmenu.onAckSecondaryClick", {"id": "string", "tag": "string"}),
                            ("navigationitem.onPress", {}), ("navigationitemgroup.onOpen", {}),
                            ("navigationmenu.onItemClick", {"id": "string", "tag": "string"}),
                            ("navigationmenu.onGroupOpen", {"id": "string", "tag": "string"}),
                            ("treenavigationitem.onPress", {}), ("treenavigationitem.onExpandToggle", {"expanded": "boolean"}),
                            ("treenavigationgroup.onExpandToggle", {"expanded": "boolean"}),
                            ("treenavigation.onItemClick", {"id": "string", "tag": "string"}),
                            ("treenavigation.onExpandToggle", {"id": "string", "tag": "string", "expanded": "boolean"}),
                            ("breadcrumb.onBreadcrumbClick", {"label": "string", "href": "string", "index": "number"}),
                            ("brilliancemenu.onPaletteChanged", {"value": "string"}), ("brilliancemenu.onBrightnessChanged", {"value": "number"}),
                            ("brilliancemenu.onLinkPaletteChanged", {"value": "boolean"}),
                            ("brilliancemenu.onLinkBrightnessChanged", {"value": "boolean"}),
                            ("brilliancemenu.onScreenControlLinkClick", {}),
                            ("usermenu.onSignInClick", {}), ("usermenu.onSignOutClick", {}), ("usermenu.onUseAnotherAccountClick", {}),
                            ("systemmenu.onWifiClick", {"enabled": "boolean"}), ("systemmenu.onAudioClick", {"muted": "boolean"}),
                            ("systemmenu.onAudioVolumeChange", {"volume": "number"}), ("systemmenu.onMicrophoneClick", {"muted": "boolean"}),
                            ("systemmenu.onPushToTalkChange", {"pushToTalk": "boolean"}),
                            ("systemmenu.onBatterySavingModeChange", {"batterySavingMode": "boolean"}),
                            ("systemmenu.onBatteryUsageClick", {"usage": "boolean"}), ("systemmenu.onWifiNetworkChange", {"network": "string"}),
                            ("systemmenu.onAudioOutputChange", {"output": "string"}),
                            ("systemmenu.onMicrophoneInputChange", {"input": "string"}), ("systemmenu.onBatteryModeChange", {"mode": "string"}),
                            ("systemmenu.onSettingsClick", {}), ("systemmenu.onSubMenuClick", {}), ("systemmenu.onWifiOptionsClick", {}),
                            ("systemmenu.onWifiDisconnectClick", {}),
                            ("commandmenu.onCommandChange", {"inCommand": "boolean"}),
                            ("topbar.onMenuButtonClick", {}), ("topbar.onDimmingButtonClick", {}), ("topbar.onAppsButtonClick", {}),
                            ("topbar.onMoreButtonClick", {}), ("topbar.onUserButtonClick", {}), ("topbar.onEmergencyBrightnessStart", {}),
                            ("topbar.onEmergencyBrightnessStop", {}), ("topbar.onAlertClick", {}), ("topbar.onSilenceClick", {}),
                            ("topbar.onBack", {}), ("topbar.onClose", {}),
                            ("topbar.onBreadcrumbClick", {"label": "string", "href": "string", "index": "number"}), ("appmenu.onSearch", {"query": "string"}), ("appmenu.onAppClick", {"id": "string", "tag": "string"}),
                            ("tabitem.onTabClick", {"title": "string"}), ("tabitem.onTabClose", {"title": "string"}),
                            ("tabrow.onTabSelected", {"id": "string", "index": "number", "title": "string"}),
                            ("tabrow.onTabClosed", {"id": "string", "index": "number", "title": "string"}), ("tabrow.onAddNewTab", {}),
                            ("pivotitem.onSelected", {"value": "string"}),
                            ("pivotitemgroup.onChange", {"selectedValue": "string"}),
                            ("modalwindow.onCloseClick", {}), ("modalwindow.onCancelClick", {}), ("modalwindow.onDoneClick", {}),
                            ("modalwindow.onOptionClick", {}),
                            ("contextmenuinput.onClose", {}), ("contextmenuinput.onItemClick", {"value": "string", "label": "string"}),
                            ("contextmenuinput.onChange", {"selectedValues": "array"}),
                            ("notificationmenuitem.onItemClick", {"open": "boolean"}), ("notificationmenuitem.onPrimaryActionClick", {}),
                            ("notificationmenuitem.onSecondaryActionClick", {}),
                            ("notificationmessageitem.onMessageClick", {}), ("notificationmessageitem.onActionClick", {}),
                            ("notificationfloatingitem.onActionClick", {}), ("notificationfloatingitem.onAction2Click", {}),
                            ("notificationfloatingitem.onDismissClick", {})):
            schema = json.loads((MODULE / f"common/src/main/resources/schemas/{name}.json").read_text(encoding="utf-8"))
            self.assertEqual({k: v["type"] for k, v in schema["properties"].items()}, props, name)

    def test_the_enumerations_come_from_the_elements(self):
        self.assertEqual(schema_of("cadre.ob.tooltip")["properties"]["variant"]["enum"],
                         ["normal", "raised", "enhanced", "eco", "alarm", "warning", "caution"])
        self.assertEqual(schema_of("cadre.ob.toggletip")["properties"]["variant"]["enum"],
                         ["normal", "raised", "enhanced", "eco-feedback", "caution", "warning", "alarm"])
        self.assertEqual(schema_of("cadre.ob.userbutton")["properties"]["size"]["enum"], ["regular", "large"])
        self.assertEqual(schema_of("cadre.ob.userbutton")["properties"]["variant"]["enum"], ["icon", "initials"])
        self.assertEqual(schema_of("cadre.ob.appbutton")["properties"]["size"]["enum"], ["normal", "small"])
        self.assertEqual(schema_of("cadre.ob.notificationbutton")["properties"]["buttonStyle"]["enum"], ["flat", "normal", "enhanced"])
        levels = ["alarm", "warning", "caution", "level-critical", "level-high", "level-medium", "level-low", "level-diagnostic"]
        for ctype in ("alertbuttonitem", "alertbutton"):
            p = schema_of(f"cadre.ob.{ctype}")["properties"]
            self.assertEqual(p["alertType"]["enum"], [""] + levels, ctype)      # empty is the idle state (undefined)
            self.assertEqual(p["alertType"]["default"], "", ctype)
            self.assertEqual(p["type"]["enum"], ["flat", "normal", "enhanced"], ctype)
            self.assertEqual(p["flashingSpeed"]["enum"], ["default", "fast", "slow", "very-slow", "fixed"], ctype)
        self.assertEqual(schema_of("cadre.ob.alertmenuitem")["properties"]["status"]["enum"],
                         ["unacknowledged", "caution", "acknowledged", "no-ack-alarm", "no-ack-warning", "rectified"])
        self.assertEqual(schema_of("cadre.ob.alertmenuitem")["properties"]["primaryActionState"]["enum"], ["enabled", "disabled", "none"])

    def test_the_silence_control_is_hidden_by_default_and_the_priority_mapping_is_recorded(self):
        """Owner's answer 4 of the frame design: no Cadre silence function exists, so the control is off until one does."""
        self.assertIs(schema_of("cadre.ob.alertbutton")["properties"]["showSilenceButton"]["default"], False)
        self.assertIs(schema_of("cadre.ob.alertmenu")["properties"]["showSilenceButton"]["default"], False)
        self.assertIs(schema_of("cadre.ob.alertmenu")["properties"]["showAlertListButton"]["default"], True)
        self.assertIs(COMPONENTS["cadre.ob.alertbutton"]["props"]["showSilenceButton"]["default"], False)
        for ctype in ("alertbuttonitem", "alertbutton"):      # wiki 13 section 11.1: Critical level-critical, High alarm, Medium warning, Low caution
            text = schema_of(f"cadre.ob.{ctype}")["properties"]["alertType"]["description"]
            for word in ("Critical level-critical", "High alarm", "Medium warning", "Low caution", "Diagnostic empty"):
                self.assertIn(word, text, ctype)

    def test_the_navigation_and_tree_enumerations_and_the_alerts_object_come_from_the_pinned_package(self):
        variants = ["full", "icon-only", "icon-only-large", "compact", "tree"]
        terminals = ["regular", "aggregated-header", "group-header"]
        for ctype in ("navigationitem", "navigationitemgroup", "navigationmenu"):
            self.assertEqual(schema_of(f"cadre.ob.{ctype}")["properties"]["variant"]["enum"], variants, ctype)
        self.assertEqual(schema_of("cadre.ob.navigationmenu")["properties"]["flyoutVariant"]["enum"], ["full", "compact"])
        for ctype in ("navigationitem", "navigationitemgroup", "treenavigationitem", "treenavigationgroup"):
            p = schema_of(f"cadre.ob.{ctype}")["properties"]
            self.assertEqual(p["terminalType"]["enum"], terminals, ctype)
            # the object of counts is the pinned `AlertCounts` (not the design table's severity names) and `combine`
            self.assertEqual(p["alerts"]["type"], "object", ctype)
            self.assertEqual(set(p["alerts"]["properties"]), {"countLevelCritical", "countAlarm", "countLevelHigh", "countWarning",
                                                              "countLevelMedium", "countCaution", "countLevelLow", "countLevelDiagnostic",
                                                              "combine"}, ctype)
            for word in ("Critical countLevelCritical", "High countAlarm", "Medium countWarning", "Low countCaution",
                         "Diagnostic countLevelDiagnostic"):
                self.assertIn(word, p["alerts"]["description"], ctype)
            self.assertNotIn("branches", p)                    # the container computes them
            self.assertNotIn("treeBranches", p)
        # the leading icon of a tree row is a field at the element's own default (on); the header of a group likewise
        self.assertIs(schema_of("cadre.ob.treenavigationitem")["properties"]["hasLeadingIcon"]["default"], True)
        self.assertIs(schema_of("cadre.ob.treenavigationgroup")["properties"]["hasIcon"]["default"], True)
        # the navigation menu's logo slot is not carried
        self.assertNotIn("logo", json.dumps(COMPONENTS["cadre.ob.navigationmenu"].get("slots", {})))
        self.assertEqual(set(COMPONENTS["cadre.ob.navigationmenu"]["items"]), {"items", "footerItems"})
        self.assertEqual(COMPONENTS["cadre.ob.navigationmenu"]["items"]["items"]["slot"], "main")
        self.assertEqual(COMPONENTS["cadre.ob.navigationmenu"]["items"]["footerItems"]["slot"], "footer")

    def test_the_nested_item_lists_the_events_that_do_not_bubble_and_the_custom_click(self):
        sys_path = str(MODULE / "tools")
        import sys
        sys.path.insert(0, sys_path)
        import gen_module_assets
        # a group lists itself and its leaf: the nesting is to any depth (the wrapper builds up to ITEM_DEPTH)
        self.assertEqual(gen_module_assets.ITEM_CHILDREN["obc-navigation-item-group"], ["obc-navigation-item", "obc-navigation-item-group"])
        self.assertEqual(gen_module_assets.ITEM_CHILDREN["obc-tree-navigation-group"],
                         ["obc-tree-navigation-item", "obc-tree-navigation-group"])
        # item events are heard on each item at any depth; the tree's own click is a CustomEvent only (the native click also reaches the host)
        self.assertRegex(JS, r'"dom":"click","name":"onItemClick","payload":"item","onItems":true\}')
        self.assertRegex(JS, r'"dom":"open","name":"onGroupOpen","payload":"item","onItems":true\}')
        self.assertRegex(JS, r'"dom":"click","name":"onItemClick","payload":"item","onItems":true,"custom":true')
        self.assertRegex(JS, r'"dom":"expand-toggle","name":"onExpandToggle","payload":"itemexpanded","onItems":true')
        self.assertRegex(JS, r'"dom":"click","name":"onPress","payload":"none","custom":true')
        self.assertRegex(JS, r'"dom":"breadcrumb-click","name":"onBreadcrumbClick","payload":"crumb"')
        # the breadcrumb's crumbs are data, not child elements, and carry label and href only
        crumbs = schema_of("cadre.ob.breadcrumb")["properties"]["items"]
        self.assertEqual(set(crumbs["items"]["properties"]), {"label", "href"})
        self.assertNotIn("items", COMPONENTS["cadre.ob.breadcrumb"])
        # the sample rows use only tags and attributes the wrapper knows, and nest at least two levels
        known = {t: {a["fieldName"] for m in self.manifest["modules"] for d in m.get("declarations", []) if d.get("tagName") == t
                     for a in d.get("attributes", [])} | set(gen_module_assets.ITEM_FIELDS.get(t, []))
                 for t in ("obc-navigation-item", "obc-navigation-item-group", "obc-tree-navigation-item", "obc-tree-navigation-group")}

        def walk(rows, depth, seen, ids):
            for r in rows:
                tag = r["tag"]
                if tag.startswith("obi-"):
                    continue
                self.assertTrue(set(r) - {"tag", "id", "children"} <= known[tag], r)
                self.assertNotIn(r["id"], ids)
                ids.add(r["id"])
                seen.append(depth)
                walk(r.get("children", []), depth + 1, seen, ids)
        for rows in ([self.testbench.NAV_ITEMS, self.testbench.NAV_FOOTER], [self.testbench.NAV_ITEMS_OPEN], [self.testbench.TREE_ROWS]):
            depths, ids = [], set()
            for part in rows:
                walk(part, 0, depths, ids)
            self.assertGreaterEqual(max(depths), 2, rows)
        for crumb in self.testbench.CRUMBS:
            self.assertTrue(set(crumb) <= {"label", "href"}, crumb)

    def test_the_items_of_the_alert_menu_are_rows_of_the_menu_item_with_an_alert_icon_slot(self):
        sys_path = str(MODULE / "tools")
        import sys
        sys.path.insert(0, sys_path)
        import gen_module_assets
        self.assertEqual(gen_module_assets.ITEM_CHILDREN["obc-alert-menu-item"], ["obc-alert-icon"])
        menu = COMPONENTS["cadre.ob.alertmenu"]
        self.assertEqual(menu["items"], {"items": {"tags": ["obc-alert-menu-item"], "slot": ""}})
        self.assertEqual(COMPONENTS["cadre.ob.alertmenuitem"]["items"], {"alertIcon": {"tags": ["obc-alert-icon"], "slot": "alert-icon"}})
        # the rows are listed with their attributes in the schema, and the events of a row are heard on the row (they do not bubble)
        text = schema_of("cadre.ob.alertmenu")["properties"]["items"]["description"]
        for attr in ("status", "title", "description", "day", "time", "secondaryActionLabel"):
            self.assertIn(attr, text)
        for name, e in {n: e for n, e in menu["events"].items()}.items():
            self.assertTrue((MODULE / "common/src/main/resources" / e["schema"]).is_file(), name)
        self.assertRegex(JS, r'"dom":"ack-click","name":"onAckClick","payload":"item","onItems":true')
        self.assertRegex(JS, r'"dom":"ack-all-visible-click","name":"onAckAllClick","payload":"menuvisible"')
        self.assertNotRegex(JS, r'"dom":"ack-click","name":"onAckClick","payload":"item"\}')       # no host listener for a row's event
        # the sample rows use only tags and attributes the wrapper knows
        rows = self.testbench.ALERT_MENU_ROWS
        self.assertEqual({r["tag"] for r in rows}, {"obc-alert-menu-item"})
        self.assertEqual(len({r["id"] for r in rows}), len(rows))
        known = {a["fieldName"] for a in self.decl("src/components/alert-menu-item/alert-menu-item.ts", "obc-alert-menu-item")["attributes"]}
        for r in rows:
            self.assertTrue(set(r) - {"tag", "id", "children"} <= known, r)

    def test_the_user_menu_carries_no_credential(self):
        """Credentials never enter a property or an event (CLAUDE.md, the frame design section 2.3)."""
        schema = schema_of("cadre.ob.usermenu")
        names = set(schema["properties"])
        self.assertEqual(names, {"type", "size", "userInitials", "userLabel", "userRole", "componentSize", "style"})
        for word in ("username", "password", "Error", "recent", "Recent", "primaryAction"):
            self.assertFalse([n for n in names if word in n], word)
        # the two fields that draw the input boxes are fixed off by the wrapper, and the contract does not list them
        self.assertRegex(JS, r'"fixed":\{"showUsername":false,"showPassword":false\}')
        self.assertNotIn("showUsername", COMPONENTS["cadre.ob.usermenu"]["props"])
        # the sign in event carries nothing, and the wrapper builds its payload without reading the detail
        self.assertRegex(JS, r'"dom":"sign-in-click","name":"onSignInClick","payload":"none"')
        schema = json.loads((MODULE / "common/src/main/resources/schemas/usermenu.onSignInClick.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"], {})
        for event in ("onSignInClick", "onSignOutClick", "onUseAnotherAccountClick"):
            text = (MODULE / f"common/src/main/resources/schemas/usermenu.{event}.json").read_text(encoding="utf-8")
            self.assertNotRegex(text.lower(), r'"(user ?name|password)"')

    def test_the_system_menu_carries_fifteen_events_and_four_state_objects_of_the_pinned_declaration(self):
        tag, path = self.ROWS["cadre.ob.systemmenu"][:2]
        listed = {e["name"] for e in self.decl(path, tag)["events"]}
        self.assertEqual(len(listed), 16)
        # `eventName` is the parameter of a private helper of the element, not an event it fires
        self.assertIn("eventName", listed)
        self.assertNotIn("eventName", {e["element"] for e in COMPONENTS["cadre.ob.systemmenu"]["events"].values()})
        text = (MODULE / "web/node_modules/@oicl/openbridge-webcomponents/dist/components/system-menu/system-menu.js").read_text(encoding="utf-8")
        self.assertNotRegex(text, r'CustomEvent\("eventName"')
        self.assertRegex(text, r"dispatchClickEvent\(eventName\)")
        self.assertEqual(len(COMPONENTS["cadre.ob.systemmenu"]["events"]), 15)
        # the battery status slot is not carried
        self.assertNotIn("slots", COMPONENTS["cadre.ob.systemmenu"])
        # each state object has the fields of the interface in the pinned declaration
        dts = (MODULE / "web/node_modules/@oicl/openbridge-webcomponents/dist/components/system-menu/system-menu.d.ts").read_text(encoding="utf-8")
        for prop, name in (("wifiState", "WifiState"), ("audioState", "AudioState"), ("microphoneState", "MicrophoneState"),
                           ("batteryState", "BatteryState")):
            body = re.search(r"export interface " + name + r" \{(.*?)\n\}", dts, re.S).group(1)
            fields = set(re.findall(r"^ {4}(\w+)\??:", body, re.M))      # the fields of the interface, not of its inline object types
            self.assertEqual(set(schema_of("cadre.ob.systemmenu")["properties"][prop]["properties"]), fields, name)
            self.assertEqual(schema_of("cadre.ob.systemmenu")["properties"][prop]["type"], "object")
        self.assertRegex(JS, r'"name":"wifiState","kind":"object"')

    def test_the_app_menu_holds_app_buttons_whose_press_reports_the_button(self):
        menu = COMPONENTS["cadre.ob.appmenu"]
        self.assertEqual(menu["items"], {"items": {"tags": ["obc-app-button"], "slot": ""}})
        self.assertRegex(JS, r'"dom":"click","name":"onAppClick","payload":"item","onItems":true')
        self.assertRegex(JS, r'"dom":"search","name":"onSearch","payload":"detail","fields":\[\{"name":"query","type":"string"\}\]')
        self.assertNotRegex(JS, r'"dom":"click","name":"onAppClick","payload":"item"\}')      # no listener on the host for a button's press
        # the sample buttons use only attributes the item table lists, an icon of the bundled list in the slot `icon`, and unique ids
        import sys
        sys.path.insert(0, str(MODULE / "tools"))
        import gen_module_assets
        known = {a["fieldName"] for a in self.decl("src/components/app-button/app-button.ts", "obc-app-button")["attributes"]}
        known |= set(gen_module_assets.ITEM_FIELDS["obc-app-button"])
        icons = set(self.gen_icons())
        ids = [b["id"] for b in self.testbench.APP_BUTTONS]
        self.assertEqual(len(ids), len(set(ids)))
        for b in self.testbench.APP_BUTTONS:
            self.assertTrue(set(b) - {"tag", "id", "children"} <= known, b)
            self.assertEqual([(c["tag"][4:] in icons, c["slot"]) for c in b["children"]], [(True, "icon")], b)

    def test_the_arrays_of_batch_f5_are_data_with_the_fields_of_the_pinned_declarations(self):
        """Tabs, context menu options and column groups are the element's own array attributes: data, not child elements."""
        tabs = schema_of("cadre.ob.tabrow")["properties"]["tabs"]
        self.assertEqual(tabs["type"], "array")
        dts = (MODULE / "web/node_modules/@oicl/openbridge-webcomponents/dist/components/tab-row/tab-row.d.ts").read_text(encoding="utf-8")
        declared = set(re.findall(r"^    (\w+)\??:", re.search(r"export interface TabData \{(.*?)\n\}", dts, re.S).group(1), re.M))
        # every field of the pinned TabData but the `badges` list, plus the module's own `iconName`
        self.assertEqual(set(tabs["items"]["properties"]), (declared - {"badges"}) | {"iconName"})
        self.assertEqual(tabs["items"]["required"], ["id", "title"])
        self.assertEqual(tabs["items"]["properties"]["badgeType"]["enum"][:3], ["alarm", "warning", "caution"])
        self.assertEqual(tabs["items"]["properties"]["badgeSize"]["enum"], ["regular", "large"])
        self.assertRegex(JS, r'"type":"cadre.ob.tabrow".*?"tabIcons":true.*?"data":\[\{"name":"tabs","kind":"tabs"\}\]')
        self.assertEqual(JS.count('"tabIcons":true'), 1)         # only the tab row builds icons into per tab slots
        menu = COMPONENTS["cadre.ob.contextmenuinput"]
        self.assertEqual({n: menu["props"][n]["type"] for n in ("options", "columnGroups", "selectedValues")}, {n: "array" for n in ("options", "columnGroups", "selectedValues")})
        self.assertNotIn("items", menu)
        opts = schema_of("cadre.ob.contextmenuinput")["properties"]
        self.assertEqual(set(opts["options"]["items"]["properties"]), {"value", "label", "level", "children"})      # the icon (a template) is not carried
        self.assertEqual(set(opts["columnGroups"]["items"]["properties"]), {"title", "columns", "options"})
        for name in ("tabs", "menuoptions", "columngroups", "strings"):
            self.assertRegex(JS, name + r"[:,]")

    def test_the_tri_state_flags_of_the_context_menu_are_unset_by_default(self):
        """`multiSelect` and `selectPerGroup` are undefined in the element, which then decides from `type`."""
        props = schema_of("cadre.ob.contextmenuinput")["properties"]
        for name in ("multiSelect", "selectPerGroup"):
            self.assertEqual(props[name]["type"], ["boolean", "null"], name)
            self.assertIsNone(props[name]["default"], name)
            self.assertRegex(JS, rf'"name":"{name}","kind":"nboolean","def":null')
        self.assertEqual(props["type"]["enum"], ["regular", "checkboxes", "nested-checkboxes", "flyout", "multi", "multi-with-subtitles"])

    def test_a_selection_event_writes_the_components_selection_back_and_a_list_is_copied(self):
        for dom, name, field in (("tab-selected", "onTabSelected", "selectedTabId"), ("tab-closed", "onTabClosed", "selectedTabId"),
                                 ("change", "onChange", "selectedValue"), ("change", "onChange", "selectedValues"),
                                 ("item-click", "onItemClick", "open")):
            self.assertRegex(JS, rf'"dom":"{dom}","name":"{name}","payload":"detail","fields":\[[^\]]*\],"write":"{field}"')
        self.assertRegex(JS, r'"dom":"tab-closed","name":"onTabClosed","payload":"detail","fields":\[[^\]]*\],"write":"selectedTabId","from":"@element"')
        # a field of the detail may be read by a dotted path (the tab of a tab event), and a field may be a list of texts
        self.assertRegex(JS, r'\{"name":"title","type":"string","from":"tab.title"\}')
        self.assertRegex(JS, r'\{"name":"selectedValues","type":"array"\}')
        self.assertIn("(f.from || f.name).split('.')", JS)
        schema = json.loads((MODULE / "common/src/main/resources/schemas/contextmenuinput.onChange.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["selectedValues"], {"type": "array", "items": {"type": "string"}, "description": schema["properties"]["selectedValues"]["description"]})
        # no event of batch F5 writes a tag: the only writes are to the component's own properties
        self.assertNotIn("writeTag", JS)

    def test_the_modal_window_carries_text_and_events_and_is_not_a_command_dialogue(self):
        c = COMPONENTS["cadre.ob.modalwindow"]
        self.assertEqual(set(c["slots"]), {"leadingIconName", "title", "content", "optionLabel", "cancelLabel", "doneLabel"})
        self.assertEqual({n: c["slots"][n]["kind"] for n in c["slots"]}, {"leadingIconName": "icon", "title": "text", "content": "text",
                         "optionLabel": "text", "cancelLabel": "text", "doneLabel": "text"})
        props = schema_of("cadre.ob.modalwindow")["properties"]
        self.assertEqual(props["size"]["enum"], ["small", "medium", "large"])
        self.assertIs(props["hasCancelAction"]["default"], True)
        self.assertIs(props["hasCloseAction"]["default"], True)
        self.assertEqual(props["content"]["type"], "string")        # the content slot is text: a Perspective component cannot hold another
        self.assertNotIn("items", c)
        self.assertEqual(set(c["events"]), {"onCloseClick", "onCancelClick", "onDoneClick", "onOptionClick"})

    def test_the_floating_item_names_its_two_labels_apart_from_the_flags_that_draw_the_buttons(self):
        props = schema_of("cadre.ob.notificationfloatingitem")["properties"]
        for flag in ("action", "action2"):
            self.assertEqual(props[flag]["type"], "boolean", flag)
        for label in ("actionLabel", "action2Label", "title", "description", "time", "day"):
            self.assertEqual(props[label]["type"], "string", label)
        self.assertEqual(props["type"]["enum"], ["regular", "application"])
        self.assertEqual(props["direction"]["enum"], ["horizontal", "vertical"])
        self.assertEqual(props["lineType"]["enum"], ["single-line", "multi-line"])
        self.assertEqual(COMPONENTS["cadre.ob.notificationfloatingitem"]["slots"]["primaryIconName"], {"slot": "primary-icon", "kind": "icon"})

    def test_all_thirty_three_frame_components_of_the_pinned_release_are_wrapped(self):
        wrapped = {c["element"] for c in COMPONENTS.values()}
        frame = {"obc-top-bar", "obc-alert-button", "obc-alert-button-item", "obc-alert-menu", "obc-alert-menu-item", "obc-app-button",
                 "obc-app-menu", "obc-breadcrumb", "obc-brilliance-menu", "obc-clock", "obc-command-menu", "obc-context-menu-input",
                 "obc-modal-window", "obc-navigation-item", "obc-navigation-item-group", "obc-navigation-menu", "obc-notification-badge-button",
                 "obc-notification-button", "obc-notification-floating-item", "obc-notification-menu-item", "obc-notification-message-item",
                 "obc-pivot-item", "obc-pivot-item-group", "obc-system-menu", "obc-tab-item", "obc-tab-row", "obc-toggletip", "obc-tooltip",
                 "obc-tree-navigation", "obc-tree-navigation-group", "obc-tree-navigation-item", "obc-user-button", "obc-user-menu"}
        self.assertEqual(len(frame), 33)
        self.assertEqual(frame - wrapped, set())
        self.assertEqual({c["element"] for c in map(COMPONENTS.get, self.ROWS)}, frame)

    def test_the_components_are_registered_in_java_imported_and_wrapped(self):
        java = (MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java").read_text(encoding="utf-8")
        entry = (MODULE / "web/entry.js").read_text(encoding="utf-8")
        for ctype, (tag, path, attrs, fields, slots, events) in self.ROWS.items():
            name = COMPONENTS[ctype]["schema"].split("/")[-1].split(".")[0]
            self.assertRegex(java, rf'descriptor\("{re.escape(ctype)}", "{name}"')
            for ev in events:
                self.assertIn(f'event("{name}", "{ev}"', java)
            self.assertIn(path.replace("src/", "dist/").replace(".ts", ".js"), entry)
            self.assertIn(f'"type":"{ctype}","tag":"{tag}"', JS)
            # the element's registration decorator, alone or beside another (the alert button family has one more)
            self.assertRegex(JS, rf'[\[,]\w+\("{tag}"\)[,\]]')
        self.assertEqual(len(re.findall(r'^        descriptor\("', java, re.M)), len(COMPONENTS))

    def test_the_table_row_of_each_is_a_frame_kind_and_a_module_only_kind(self):
        self.assertEqual(set(self.screen.FRAME_ONLY.values()), set(self.ROWS))
        for kind, ctype in self.screen.FRAME_ONLY.items():
            self.assertEqual(self.screen.MODULE_ONLY[kind], ctype)
            self.assertEqual(COMPONENTS[ctype]["element"], "obc-" + kind)       # the kind is the tag without `obc-`
            self.assertNotIn(kind, self.screen.MODULE_KIND)

    def test_the_component_test_page_shows_them_in_one_frame_section_under_the_module_rendering_only(self):
        contracts = self.screen.load_contracts()
        prof = self.library_profile.build(contracts)
        bench = self.testbench.build(contracts, prof, "[default]cadre_hmi_ctest", render="module")
        ids = [s["id"] for s in bench.descriptor["sections"]]
        self.assertIn("FrameComponents", ids)
        self.assertLess(ids.index("ModuleOnly"), ids.index("FrameComponents"))
        title = next(s["label"] for s in bench.descriptor["sections"] if s["id"] == "FrameComponents")
        self.assertIn("Frame components: tooltip, toggletip, clock, user-button, app-button", title)
        only = next(s["label"] for s in bench.descriptor["sections"] if s["id"] == "ModuleOnly")
        for kind in self.screen.FRAME_ONLY:
            self.assertNotIn(kind, only.split(": ", 1)[1].split(", "))
        counts = {k: sum(1 for s in bench.descriptor["symbols"] if s["kind"] == k) for k in self.screen.FRAME_ONLY}
        self.assertEqual(counts, {"tooltip": 13, "toggletip": 14, "clock": 15, "user-button": 14, "app-button": 7,
                                  "notification-button": 11, "notification-badge-button": 9,
                                  "alert-button-item": 26, "alert-button": 31, "alert-menu-item": 22, "alert-menu": 8,
                                  "navigation-item": 17, "navigation-item-group": 15, "navigation-menu": 11,
                                  "tree-navigation-item": 12, "tree-navigation-group": 9, "tree-navigation": 3, "breadcrumb": 4,
                                  "brilliance-menu": 23, "user-menu": 8, "system-menu": 12, "app-menu": 3, "command-menu": 4, "top-bar": 39,
                                  "tab-item": 34, "tab-row": 10, "pivot-item": 9, "pivot-item-group": 6, "modal-window": 11, "context-menu-input": 18, "notification-menu-item": 7, "notification-message-item": 15, "notification-floating-item": 13})
        stock = self.testbench.build(contracts, prof, "[default]cadre_hmi_ctest", render="stock")
        self.assertNotIn("FrameComponents", [s["id"] for s in stock.descriptor["sections"]])
        self.assertEqual(self.testbench.check(bench.descriptor, contracts), [])

    def test_the_samples_are_ours_and_every_slot_property_is_exercised_on_the_page(self):
        used = set()
        for kind, sample in self.testbench.FRAME_SAMPLE.items():
            for params in [sample["base"]] + [p for _c, p in sample["extra"]]:
                used |= {(kind, k) for k in params}
        for kind, ctype in self.screen.FRAME_ONLY.items():
            for prop, sl in COMPONENTS[ctype].get("slots", {}).items():
                self.assertIn((kind, prop), used, f"{kind}.{prop}")
        for icon in ("info", "alarm", "close-google", "home", "user-settings"):
            self.assertIn(icon, self.gen_icons())

    def gen_icons(self):
        import sys
        sys.path.insert(0, str(MODULE / "tools"))
        import gen_module_assets
        return gen_module_assets.icon_names()

    def test_a_stock_build_refuses_a_frame_kind_with_an_error_and_no_silent_gap(self):
        contracts = self.screen.load_contracts()
        try:
            self.screen.RENDER["target"] = "stock"
            rep = self.screen.Report()
            sym = {"id": "X1", "kind": "tooltip", "x": 100, "y": 100, "w": 192, "h": 40, "params": {"label": "Hi"}}
            self.screen.embed_symbol(sym, contracts, "[default]t", rep, toolbar=True)
            self.assertEqual(len(rep.errors), 1)
            self.assertIn("kind 'tooltip' is module only (cadre.ob.tooltip)", rep.errors[0])
            self.screen.RENDER["target"] = "module"
            rep = self.screen.Report()
            node, _c, _cfg = self.screen.embed_symbol(sym, contracts, "[default]t", rep, toolbar=True)
            self.assertEqual((node["type"], node["props"], rep.errors), ("cadre.ob.tooltip", {"label": "Hi"}, []))
        finally:
            self.screen.RENDER["target"] = "stock"


class RadialInstrumentFillsItsBox(unittest.TestCase):
    """The radial instrument has no size of its own and drew at 0 by 0 when centred in its box (T2 gateway check)."""

    def test_the_stylesheet_stretches_the_radial_instrument(self):
        css = (MODULE / "gateway/src/main/resources/mounted/css/cadre-ob.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.cadre-ob > obc-instrument-radial \{[^}]*flex: 1 1 auto;[^}]*height: 100%;")


class Release(unittest.TestCase):
    def test_the_version_is_plain_and_0_6_0(self):
        text = (MODULE / "build.gradle.kts").read_text(encoding="utf-8")
        self.assertIn('version = "0.6.0"', text)      # GF-27: plain major.minor.revision (tranche T1, B0 to B8)
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
