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
        return dict({"id": "X1", "kind": kind, "x": 100, "y": 100, "w": 48, "h": 48, "params": {"tag": "X-1"}}, **kw)

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
        for kind, ctype in self.screen.MODULE_ONLY.items():
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

    def test_the_module_rendering_draws_the_component(self):
        for kind, ctype in self.screen.MODULE_ONLY.items():
            node, rep = self.embed(self.symbol(kind, params={"tag": "X-1", "on": True, "variant": "flat"}), "module")
            self.assertEqual((node["type"], rep.errors, rep.gaps), (ctype, [], []), kind)
            self.assertEqual(node["props"]["variant"], "flat")
            self.assertEqual(node["props"]["positioning"], "symbol")
            self.assertNotIn("deviceId", node["props"])

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
        for kind in self.screen.MODULE_ONLY:
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
