"""Generate the Cadre OpenBridge module's component assets from the OpenBridge package.

From the package's custom elements manifest (`custom-elements.json`), its enum declarations and
the measured element defaults (`module/web/defaults.json`, `measure_defaults.py`) this writes,
for every wrapped element:

  common/src/main/resources/schemas/<name>.props.json   Perspective property schema (Designer
                                                        property editor, validation, defaults)
  gateway/src/main/resources/mounted/js/cadre-ob.js     the OpenBridge bundle followed by the
                                                        React wrappers and their registration
  gateway/src/main/resources/mounted/css/cadre-ob.css   OpenBridge's stylesheet, scoped and trimmed
  gateway/src/main/resources/mounted/fonts/NotoSans-OB.ttf   OpenBridge's variable Noto Sans
  components.json                                       the contract: id, element, properties
  web/canvaszoom.js                                     (read, not written) the canvas zoom component, appended to
                                                        cadre-ob.js; its schema and contract entry are written here

A module's browser resources load in every Perspective session of the gateway, so the
stylesheet is scoped: OpenBridge declares its palettes and sizes on `:root` and some variables on
`*`; here they are declared on the wrapper (`.cadre-ob`) and keyed to the Cadre palette classes,
and only the variables the bundled elements use (with their dependencies) are kept.

Usage:  python module/tools/gen_module_assets.py
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PKG = HERE / "web/node_modules/@oicl/openbridge-webcomponents"
MOUNTED = HERE / "gateway/src/main/resources/mounted"
SCHEMAS = HERE / "common/src/main/resources/schemas"

# The wrapped elements: Perspective component id, short name, palette text, default size. `data`
# declares properties that carry JSON data rather than a scalar attribute (read from the property
# tree as plain JSON, `readArray`, measured GF-38, and converted for the element); `events` maps an
# element's custom event to the Perspective component event it fires (`componentEvents.
# fireComponentEvent`, measured GF-37) and the payload built from the event detail.
ALERT_EVENTS = {
    "ack-click": ("onAckClick", "alert", "The ACK button of an alert was clicked. event.ids holds its alert id; "
                                         "event.id, event.tagId, event.source and event.text describe it."),
    "row-click": ("onRowClick", "alert", "An alert row was clicked. event.ids holds its alert id; event.tagId is "
                                         "the device folder of the alarm."),
    "silence-click": ("onSilenceClick", "none", "The Silence button was clicked."),
    "ack-all-visible-click": ("onAckAllClick", "visible", "The ACK visible button was clicked. event.mode is the "
                                                          "list mode; event.ids holds the unacknowledged alerts it shows."),
    # The command button (spike T0 wrap W3): the element's own `click`, with no detail to carry.
    "click": ("onPress", "none", "The button was pressed. The event carries nothing; the page's script decides what it "
                                 "commands (the library's confirmed pulse, write path W18)."),
}
COMPONENTS = [
    {"tag": "obc-pump", "type": "cadre.ob.pump", "name": "pump", "title": "OB Pump",
     "palette": "OpenBridge pump: state, speed readout, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "extra": ["hasSpeed", "showStatus", "statusText", "badgeDuty", "outOfService"], "speedless": True, "status": True},
    {"tag": "obc-automation-tank", "type": "cadre.ob.tank", "name": "tank", "title": "OB Tank",
     "palette": "OpenBridge tank: level, trend, value and maximum, badges and alert frame",
     "size": {"width": 168, "height": 216}, "exclude": ["touching"], "extra": ["unit", "hasCapacity"],
     "tankSlots": True},
    {"tag": "obc-motor", "type": "cadre.ob.motor", "name": "motor", "title": "OB Motor",
     "palette": "OpenBridge motor: state, speed readout, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "extra": ["hasSpeed", "showStatus", "statusText", "badgeDuty", "outOfService"], "speedless": True, "status": True},
    {"tag": "obc-fan", "type": "cadre.ob.fan", "name": "fan", "title": "OB Fan",
     "palette": "OpenBridge fan: state, speed readout, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "extra": ["hasSpeed", "showStatus", "statusText", "badgeDuty", "outOfService"], "speedless": True, "status": True},
    {"tag": "obc-digital-valve", "type": "cadre.ob.valve", "name": "valve", "title": "OB Valve",
     "palette": "OpenBridge digital valve: open or closed, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-analog-valve", "type": "cadre.ob.analogvalve", "name": "analogvalve", "title": "OB Analog Valve",
     "palette": "OpenBridge analogue valve: opening readout, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-filter", "type": "cadre.ob.filter", "name": "filter", "title": "OB Filter",
     "palette": "OpenBridge filter: a static symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-indicator-generator", "type": "cadre.ob.generator", "name": "generator", "title": "OB Generator",
     "palette": "OpenBridge generator indicator: running state, readout and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "generator": True,
     "extra": ["on", "tag", "readoutPosition", "showStatus", "statusText", "alert", "alertFrameStatus", "alertFrameMode"],
     "describe": {"showStatus": "Whether the symbol draws its status word (On or Off, or statusText). False hides the "
                               "word; the identifier stays. The diagram toolbar's Readout button binds it.",
                  "statusText": "When not empty, the status word drawn beside the symbol in place of On or Off."}},
    {"tag": "obc-automation-button", "type": "cadre.ob.button", "name": "button", "title": "OB Button",
     "palette": "OpenBridge automation button: a command button with identifier, state, progress and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "events": ["click"]},
    {"tag": "obc-transmitter", "type": "cadre.ob.readout", "name": "readout", "title": "OB Readout",
     "palette": "OpenBridge transmitter: value chip with unit and an identifier beneath it",
     "size": {"width": 72, "height": 24}, "exclude": ["data", "lineType"], "extra": ["stretch"], "sheet": "readout",
     "chipSheet": "readoutchip"},
    {"tag": "obc-instrument-field", "type": "cadre.ob.instrumentfield", "name": "instrumentfield",
     "title": "OB Instrument Field", "palette": "OpenBridge instrument field: value, optional setpoint, caption and unit",
     "size": {"width": 96, "height": 64}, "exclude": [], "sheet": "instrumentfield", "endAligned": True},
    {"tag": "obc-alert-list-details", "type": "cadre.ob.alertlist", "name": "alertlist", "title": "OB Alert List",
     "palette": "OpenBridge alert list: Alert records with ACK and row click", "size": {"width": 368, "height": 480},
     "exclude": [], "dts": "components/alert-list-details/alert-list-details.d.ts",
     "data": {"alerts": "alerts"}, "events": ["ack-click", "row-click"],
     "extra": ["selectable", "selectedIds"], "selection": True},
    {"tag": "obc-alert-list-page-small", "type": "cadre.ob.alertpanel", "name": "alertpanel", "title": "OB Alert Panel",
     "palette": "OpenBridge alert panel: mode tabs, alert list, ACK visible and Silence",
     "size": {"width": 640, "height": 420}, "exclude": [], "dts": "pages/alert-list-page-small/alert-list-page-small.d.ts",
     "data": {"alerts": "alerts"}, "events": ["ack-click", "row-click", "silence-click", "ack-all-visible-click"],
     "extra": ["selectable", "selectedIds"], "selection": True},
    {"tag": "obc-resistor", "type": "cadre.ob.resistor", "name": "resistor", "title": "OB Resistor",
     "palette": "OpenBridge resistor: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-damper", "type": "cadre.ob.damper", "name": "damper", "title": "OB Damper",
     "palette": "OpenBridge damper: an air damper symbol on a diagram, open or closed, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-switch", "type": "cadre.ob.switch", "name": "switch", "title": "OB Switch",
     "palette": "OpenBridge switch: an electrical switch symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-capacitor", "type": "cadre.ob.capacitor", "name": "capacitor", "title": "OB Capacitor",
     "palette": "OpenBridge capacitor: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-diodes", "type": "cadre.ob.diodes", "name": "diodes", "title": "OB Diodes",
     "palette": "OpenBridge diodes: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-ground", "type": "cadre.ob.ground", "name": "ground", "title": "OB Ground",
     "palette": "OpenBridge ground: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-source", "type": "cadre.ob.source", "name": "source", "title": "OB Source",
     "palette": "OpenBridge source: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-converter", "type": "cadre.ob.converter", "name": "converter", "title": "OB Converter",
     "palette": "OpenBridge converter: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-transformer", "type": "cadre.ob.transformer", "name": "transformer", "title": "OB Transformer",
     "palette": "OpenBridge transformer: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-bipolar-transistor", "type": "cadre.ob.bipolartransistor", "name": "bipolartransistor", "title": "OB Bipolar Transistor",
     "palette": "OpenBridge bipolar transistor: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-mosfet", "type": "cadre.ob.mosfet", "name": "mosfet", "title": "OB MOSFET",
     "palette": "OpenBridge MOSFET: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-logic", "type": "cadre.ob.logic", "name": "logic", "title": "OB Logic",
     "palette": "OpenBridge logic: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-router", "type": "cadre.ob.router", "name": "router", "title": "OB Router",
     "palette": "OpenBridge router: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-automation-badge", "type": "cadre.ob.automationbadge", "name": "automationbadge", "title": "OB Automation Badge",
     "palette": "OpenBridge automation badge: the small corner badge of an automation symbol, drawn on its own (mode and type)",
     "size": {"width": 32, "height": 32}, "exclude": []},
    {"tag": "obc-hydraulic-check-valve", "type": "cadre.ob.checkvalve", "name": "checkvalve", "title": "OB Check Valve",
     "palette": "OpenBridge hydraulic check valve: a display-only glyph on a hydraulic diagram",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-valve-analog-two-way-icon", "type": "cadre.ob.valvetwoway", "name": "valvetwoway", "title": "OB Two-Way Valve Glyph",
     "palette": "OpenBridge analog two-way valve glyph: the valve with its opening, without readout or alert frame",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-valve-analog-three-way-icon", "type": "cadre.ob.valvethreeway", "name": "valvethreeway", "title": "OB Three-Way Valve Glyph",
     "palette": "OpenBridge analog three-way valve glyph: the valve with two openings, without readout or alert frame",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-indicator-battery", "type": "cadre.ob.battery", "name": "battery", "title": "OB Battery Indicator",
     "palette": "OpenBridge battery indicator: a battery drawn as a level bar or a trend graph, display only",
     "size": {"width": 48, "height": 48}, "exclude": [], "data": {"data": "numbers"}},
    {"tag": "obc-indicator-engine", "type": "cadre.ob.engine", "name": "engine", "title": "OB Engine Indicator",
     "palette": "OpenBridge engine indicator: an engine block drawn in a static, regular or enhanced scheme, display only",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-indicator-tank-atmospheric", "type": "cadre.ob.tankatmospheric", "name": "tankatmospheric",
     "title": "OB Atmospheric Tank Indicator",
     "palette": "OpenBridge atmospheric tank indicator: a tank drawn as a level bar or a trend graph, display only",
     "size": {"width": 48, "height": 48}, "exclude": [], "data": {"data": "numbers"}},
    {"tag": "obc-automation-readout", "type": "cadre.ob.automationreadout", "name": "automationreadout",
     "title": "OB Automation Readout",
     "palette": "OpenBridge automation readout: a value with its unit in a bordered chip, display only",
     "size": {"width": 72, "height": 48}, "exclude": ["lineType"]},
]
# The canvas zoom component is not an OpenBridge element: a leaf component whose browser side is
# `web/canvaszoom.js`. Its properties are fixed by the Level 4 contract (the stock screens bind `zoom` two ways).
CANVAS_ZOOM = {
    "type": "cadre.ob.canvaszoom", "name": "canvaszoom", "title": "OB Canvas Zoom",
    "palette": "Canvas zoom: Ctrl+wheel, pinch and Ctrl+plus, minus, 0 scale only the canvas, not the browser page",
    "size": {"width": 1, "height": 1},
    "props": {
        "zoom": {"type": "number", "default": 1, "description":
                 "The canvas scale, written by the component and bound two ways to the view's zoom property."},
        "min": {"type": "number", "default": 0.5, "description": "The smallest zoom."},
        "max": {"type": "number", "default": 4, "description": "The largest zoom."},
        "targetDomId": {"type": "string", "default": "cadre-canvas", "description":
                        "The DOM id of the scrolling canvas the gestures act on (a Perspective component's domId)."},
        "guardBrowserZoom": {"type": "boolean", "default": True, "description":
                             "Prevent the same gestures anywhere else on the document, so the browser never zooms "
                             "the frame; on touch devices the viewport meta gains maximum-scale=1."},
        "viewWidth": {"type": "number", "default": 0, "description":
                      "The target's measured width in px, written by the component when it changes (0 until measured); "
                      "the page's fit reads it, so a docked faceplate or a reload needs no session flag."},
        "viewHeight": {"type": "number", "default": 0, "description":
                       "The target's measured height in px, written by the component when it changes (0 until measured)."},
    },
}
DATA_SCHEMA = {"alerts": {"type": "array", "default": [], "items": {"type": "object"},
                          "description": "Alert records (OpenBridge types.d.ts Alert): id, tagId, source, text, note, "
                                         "acknowledged, active, type, time (epoch milliseconds), shelved."},
             "numbers": {"type": "array", "default": [], "items": {"type": "number"},
                         "description": "The samples of a trend graph, oldest first, as plain numbers (the element's `data`)."}}
# Properties of the module's own, not the element's: the wrapper applies them (`speedless`, `tankSlots` in the
# WRAPPER below). Each lifts a case the element cannot show (COB-110): a device with no speed reads no speed, a
# tank states the unit of its level, and a vessel that states no capacity draws no capacity line.
EXTRA = {
    "hasSpeed": {"kind": "boolean", "def": True, "schema": {"type": "boolean", "default": True, "description":
                 "Whether the element prints a speed while it runs. False leaves the speed readout out (the "
                 "state readout stays); the OpenBridge element has no such switch."}},
    "showStatus": {"kind": "boolean", "def": True, "schema": {"type": "boolean", "default": True, "description":
                   "Whether the symbol draws its status readouts. False hides every status word, including the "
                   "element's own Off, and the speed readout (the element's showStatus); the tag stays."}},
    "statusText": {"kind": "string", "def": "", "schema": {"type": "string", "default": "", "description":
                   "When not empty, the status word drawn in the element's status place (for example On or Off) "
                   "in place of its own readout; empty keeps the element's own."}},
    "badgeDuty": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
                  "The OpenBridge duty badge on the symbol, in the first free corner (bottom left, bottom right, "
                  "top left, top right); not drawn while the interlock badge, which is the same icon, is."}},
    "outOfService": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
                     "The symbol greyed and marked with the word OOS, as the stock library view draws an out of "
                     "service symbol."}},
    "stretch": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
                "The readout fills its component box (chip and identifier centred in it), so readouts of equal "
                "boxes show equal widths with their values aligned, instead of sizing to the content."}},
    # Row selection of the two alarm lists (module 0.4.2, eng02 ASM Level 5): OpenBridge's table has the tick column
    # (an obc-checkbox) itself; the alert list does not switch it on, so the wrapper does (`applySelection`).
    "selectable": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
                   "Whether each row starts with a tick box (the OpenBridge checkbox) that selects it. A click on the "
                   "tick toggles only the selection; a click elsewhere on the row is the row click as before."}},
    "selectedIds": {"kind": "array", "def": [], "schema": {"type": "array", "default": [], "items": {"type": "string"},
                    "description": "The ids of the selected rows. Written by the component when a tick is toggled "
                                   "(bind it two ways); ticks show the ids in it, and an id of an alert the list no "
                                   "longer shows is dropped."}},
    # The indicator generator draws a disc and nothing else (no state, no readout, no alert attributes), so the
    # wrapper adds them (`generator` in the WRAPPER below): the running state selects the element's `value`
    # scheme, and its identifier, status word and alert frame are drawn from OpenBridge's own readout stack and
    # alert frame elements, unchanged, inside the element's shadow root.
    "on": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
           "Whether the generator is running. A generator that runs draws the scheme of `value` (the regular "
           "scheme where `value` is off); one that does not run draws the element's off scheme."}},
    "tag": {"kind": "string", "def": "", "schema": {"type": "string", "default": "", "description":
            "The identifier printed with the symbol; empty prints none."}},
    "readoutPosition": {"kind": "string", "def": "bottom", "schema": {"type": "string", "enum": [
                        "top", "bottom", "left", "right", "none"], "default": "bottom", "description":
                        "The side of the symbol on which the identifier and the status word lie; none draws neither."}},
    "alert": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
              "Whether the symbol is framed by the OpenBridge alert frame."}},
    "alertFrameStatus": {"kind": "string", "def": "alarm", "enum": "AlertType", "schema": {
                         "type": "string", "default": "alarm", "description": "Available when alert==true."}},
    "alertFrameMode": {"kind": "string", "def": "acked-active", "enum": "ObcAlertFrameMode", "schema": {
                       "type": "string", "default": "acked-active", "description": "Available when alert==true."}},
    "unit": {"kind": "string", "def": "m³", "schema": {"type": "string", "default": "m³", "description":
             "The unit printed after the capacity, in place of the cubic metres of the OpenBridge tank."}},
    "hasCapacity": {"kind": "boolean", "def": True, "schema": {"type": "boolean", "default": True, "description":
                    "Whether a static tank prints its capacity. False draws the vessel and its tag with no "
                    "capacity line, where the OpenBridge tank always prints one."}},
}
# Element properties the manifest declares as fields with no attribute (`attribute: false` in the element), which the
# attribute loop of `schema_for` therefore does not see. The wrapper sets them on the element as it sets every field.
# `showStatus` hides the state readout of an automation button (On or Off, the speed, the opening) and keeps the
# identifier: the diagram toolbar's Readout button binds it, as it binds the library view's `showStatus`. The two
# valves take it here (0.3.2); the pump, motor and fan take it as an extra (0.4.0), which `applyStatus` passes on.
PROPERTIES = {
    "showStatus": {"type": "boolean", "default": True, "description":
                   "Whether the element draws its state readout (On or Off, the speed, the opening) beside the "
                   "symbol. The identifier stays. The diagram toolbar's Readout button binds it."},
}
# Rules added to the shadow root of an element, where the element draws something a process diagram's box
# cannot use as it stands (COB-127). The transmitter is built to hang from a line by a leader line: it
# offsets itself by half its width and 8 px, which puts it beside the box a diagram gives it. The module
# draws it centred in its box with no leader line, as the library's readout is. The instrument field aligns
# its value and its setpoint to the end of the element, and `center` moves only the caption, so the wrapper
# sets `data-center` on the host of a centred symbol and the value and setpoint centre with it.
SHEETS = {
    "readout": ".transmitter { transform: none !important; top: auto !important; right: auto !important; "
               "padding: 0 !important; }\n.transmitter::before { display: none !important; }\n"
               ":host([data-stretch]), :host([data-stretch]) .transmitter, :host([data-stretch]) .content, "
               ":host([data-stretch]) .body { width: 100% !important; }\n"
               ":host([data-stretch]) .chip { display: block; flex: 1 1 auto; width: 100%; }",
    # the chip's own shadow root: its button is as wide as its content unless it is told to fill the chip
    "readoutchip": ":host([data-stretch]) { display: block; width: 100%; }\n"
                   ":host([data-stretch]) .button { display: flex; width: 100%; }\n"
                   ":host([data-stretch]) .visible-wrapper { width: 100%; justify-content: center; }",
    "instrumentfield": ":host([data-center]) .setpoint, :host([data-center]) .value { justify-content: center "
                       "!important; }",
}

SIZES = ["regular", "medium", "large", "xl"]
PALETTES = ["day", "dusk", "night", "bright"]


# ------------------------------------------------------------------------------- manifest
def declaration(manifest: dict, tag: str) -> dict:
    for mod in manifest["modules"]:
        for d in mod.get("declarations", []):
            if d.get("tagName") == tag:
                return d
    raise SystemExit(f"{tag} not in the manifest")


def enums() -> dict[str, list[str]]:
    """Enum values from the full bundle (esbuild's enum pattern) and the type declarations."""
    out: dict[str, list[str]] = {}
    bundle = (PKG / "bundle/openbridge-webcomponents.bundle.js").read_text(encoding="utf-8")
    for m in re.finditer(r"var (\w+?)(?:\$\d+)? = /\* @__PURE__ \*/ \(\((\w+)\) => \{(.*?)return \2;", bundle, re.S):
        vals = re.findall(re.escape(m.group(2)) + r'\["[^"]+"\] = "([^"]+)"', m.group(3))
        if vals:
            out.setdefault(m.group(1), vals)
    for f in (PKG / "dist").rglob("*.d.ts"):
        for m in re.finditer(r"export declare enum (\w+) \{(.*?)\}", f.read_text(encoding="utf-8"), re.S):
            vals = re.findall(r'=\s*"([^"]+)"', m.group(2))
            if vals:
                out.setdefault(m.group(1), vals)
    return out


def local_enums(spec: dict) -> dict[str, list[str]]:
    """The enums an element's own declaration file declares. Two elements may declare an enum of
    the same name with different values (`AlertListMode`: five values in the alert list, three in
    the small alert page), so an element's own declaration wins over the package-wide map."""
    if not spec.get("dts"):
        return {}
    text = (PKG / "dist" / spec["dts"]).read_text(encoding="utf-8")
    return {m.group(1): re.findall(r'=\s*"([^"]+)"', m.group(2))
            for m in re.finditer(r"export declare enum (\w+) \{(.*?)\}", text, re.S)}


def clean(text: str | None) -> str:
    if not text:
        return ""
    t = re.sub(r"\s+", " ", text.replace("`", "")).strip()
    return t if len(t) <= 220 else t[:217].rsplit(" ", 1)[0] + "..."


def schema_for(spec: dict, decl: dict, enum_map: dict, defaults: dict) -> tuple[dict, list[dict]]:
    members = {m["name"]: m for m in decl.get("members", []) if m.get("kind") == "field"}
    props: dict[str, dict] = {}
    fields: list[dict] = []
    enum_map = {**enum_map, **local_enums(spec)}
    for a in decl.get("attributes", []):
        name = a.get("fieldName")
        if not name or name in spec["exclude"] or name in spec.get("data", {}):
            continue
        ttext = ((a.get("type") or {}).get("text") or "").strip()
        desc = clean((members.get(name) or {}).get("description") or a.get("description"))
        default = defaults.get(name)
        base = ttext.replace(" | undefined", "").replace(" | null", "")
        nullable = ttext != base
        if base == "boolean":
            p, kind = {"type": "boolean", "default": bool(default)}, "boolean"
        elif base == "number" and not nullable:
            p, kind = {"type": "number", "default": default if isinstance(default, (int, float)) else 0}, "number"
        elif base == "number":
            p, kind = {"type": ["number", "null"], "default": None}, "nnumber"
        elif base == "string":
            p, kind = {"type": "string", "default": default if isinstance(default, str) else ""}, ("nstring" if nullable else "string")
        elif base in enum_map:
            vals = enum_map[base]
            d = default if default in vals else vals[0]
            p, kind = {"type": "string", "enum": vals, "default": d}, "string"
        else:
            print(f"  skipped {spec['tag']}.{name}: type {ttext!r} not mapped")
            continue
        p["description"] = desc or f"OpenBridge `{spec['tag']}` property `{name}`."
        props[name] = p
        fields.append({"name": name, "kind": kind, "def": p["default"]})
    for name in spec.get("properties", []):
        want = PROPERTIES[name]
        if ((members.get(name) or {}).get("type") or {}).get("text") != want["type"]:
            raise SystemExit(f"{spec['tag']} declares no {want['type']} field {name!r} in the manifest")
        props[name] = dict(want)
        fields.append({"name": name, "kind": want["type"], "def": want["default"]})
    for name, kind in spec.get("data", {}).items():
        props[name] = dict(DATA_SCHEMA[kind])
    for name in spec.get("extra", []):
        props[name] = dict(EXTRA[name]["schema"])
        if EXTRA[name].get("enum"):      # the enumeration of OpenBridge's own declaration, as for an attribute
            vals = enum_map[EXTRA[name]["enum"]]
            props[name] = {"type": "string", "enum": vals, "default": EXTRA[name]["def"],
                           "description": props[name]["description"]}
        if name in spec.get("describe", {}):
            props[name]["description"] = spec["describe"][name]
    props["componentSize"] = {"type": "string", "enum": SIZES, "default": "regular",
                              "description": "OpenBridge component size: regular, medium, large or xl."}
    props["style"] = {"$ref": "urn:ignition-schema:schemas/style-properties.schema.json",
                      "default": {"classes": ""}}
    return {"type": "object", "additionalProperties": False, "properties": props}, fields


# ------------------------------------------------------------------------------- stylesheet
def parse_rules(css: str) -> list[tuple[str, str]]:
    """Top-level rules as (prelude, body); nested at-rule bodies are kept whole."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules, depth, start, prelude = [], 0, 0, ""
    for i, ch in enumerate(css):
        if ch == "{":
            if depth == 0:
                prelude, start = css[start:i].strip(), i + 1
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                rules.append((prelude, css[start:i]))
                start = i + 1
    return rules


def declarations(body: str) -> list[tuple[str, str]]:
    out = []
    for part in body.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out.append((k.strip(), v.strip()))
    return out


def scoped_css(bundle_js: str) -> tuple[str, dict]:
    css = (PKG / "dist/openbridge.css").read_text(encoding="utf-8")
    rules = parse_rules(css)
    used = set(re.findall(r"var\(\s*(--[\w-]+)", bundle_js))
    defs: dict[str, set[str]] = {}
    for _, body in rules:
        for k, v in declarations(body):
            if k.startswith("--"):
                defs.setdefault(k, set()).update(re.findall(r"var\(\s*(--[\w-]+)", v))
    keep, todo = set(), [v for v in used if v in defs]
    while todo:
        v = todo.pop()
        if v in keep:
            continue
        keep.add(v)
        todo += [d for d in defs.get(v, ()) if d not in keep and d in defs]

    def sel(prelude: str) -> str | None:
        parts = [p.strip() for p in prelude.split(",")]
        out = []
        for p in parts:
            m = re.fullmatch(r':root\[data-obc-theme="(\w+)"\]', p)
            if p in (":root", "html"):      # `html` carries `--obc-can-hover`, which the chip's hover colours read
                out.append(".cadre-ob.cadre-ob")
            elif m:
                out.append(f".psc-cadre\\/palette\\/{m.group(1)} .cadre-ob.cadre-ob")
            elif p == "*":
                out += [".cadre-ob", ".cadre-ob *"]
            elif re.fullmatch(r"\.obc-component-size-\w+", p):
                out.append(f".cadre-ob{p}")
            else:
                return None
        return ", ".join(dict.fromkeys(out))

    blocks, stats = [], {"rules_in": len(rules), "rules_out": 0, "vars_defined": len(defs),
                         "vars_used_by_bundle": len(used), "vars_kept": len(keep)}
    for prelude, body in rules:
        if prelude.startswith("@property"):
            name = prelude.split()[1]
            if name in keep:
                blocks.append(f"{prelude} {{{body.strip()}}}")
            continue
        s = sel(prelude) if not prelude.startswith("@") else None
        if not s:
            continue
        decls = [f"{k}: {v}" for k, v in declarations(body) if k in keep]
        if decls:
            blocks.append(f"{s} {{\n  " + ";\n  ".join(decls) + ";\n}")
    stats["rules_out"] = len(blocks)
    head = ("/* Cadre OpenBridge module stylesheet. Generated by module/tools/gen_module_assets.py from\n"
            "   @oicl/openbridge-webcomponents 2.0.0-next.155 dist/openbridge.css (Apache-2.0, Copyright 2024 OICL),\n"
            "   scoped to .cadre-ob and the Cadre palette classes, trimmed to the variables the bundled elements use. */\n")
    font = ('@font-face {\n  font-family: "Noto Sans OB";\n  src: url("../fonts/NotoSans-OB.ttf") format("truetype");\n'
            '  font-weight: 100 900;\n  font-style: normal;\n  font-display: swap;\n}\n'
            '.cadre-ob.cadre-ob, .cadre-ob * {\n  --global-typography-font-family: "Noto Sans OB", "Noto Sans", sans-serif;\n'
            '  --font-family-main: "Noto Sans OB", "Noto Sans", sans-serif;\n}\n'
            '.cadre-ob {\n  width: 100%;\n  height: 100%;\n  display: flex;\n  align-items: center;\n'
            '  justify-content: center;\n  box-sizing: border-box;\n}\n')
    # The wrapper centres its element, which suits a symbol; an alarm list fills its component box, top
    # aligned (COB-078). The parent project's stylesheet carried this rule until version 0.2.1 (COB-082).
    lists = ('/* The alarm lists fill the component box, top aligned. */\n'
             '.cadre-ob > obc-alert-list-details,\n.cadre-ob > obc-alert-list-page-small {\n'
             '  align-self: stretch;\n  flex: 1 1 auto;\n  width: 100%;\n  min-height: 0;\n}\n')
    # The device components. The out of service veil lies over the 48 px symbol at the centre of the box and takes
    # no pointer; a readout that is told to stretch fills the box.
    devices = ("/* Out of service: the library view's veil and word (COB-159) over the symbol. */\n"
               ".cadre-ob { position: relative; }\n"
               ".cadre-ob > .cadre-ob-oos {\n  position: absolute;\n  left: 50%;\n  top: 50%;\n  width: 48px;\n"
               "  height: 48px;\n  margin: -24px 0 0 -24px;\n  border-radius: 6px;\n  display: flex;\n"
               "  align-items: center;\n  justify-content: center;\n  pointer-events: none;\n"
               "  background: color-mix(in srgb, var(--container-background-color, #fff) 72%, transparent);\n"
               "  color: var(--element-active-color, #1f1f1f);\n"
               "  font: 570 12px/14px var(--global-typography-font-family, sans-serif);\n}\n"
               "/* A stretched readout fills its component box. */\n"
               ".cadre-ob > obc-transmitter[data-stretch] {\n  align-self: stretch;\n  flex: 1 1 auto;\n  width: 100%;\n}\n")
    return head + "\n".join(blocks) + "\n" + font + lists + devices, stats


# ------------------------------------------------------------------------------- wrappers
WRAPPER = r"""
/* Cadre OpenBridge module: Perspective wrappers for OpenBridge web components.
   Generated by module/tools/gen_module_assets.py; do not edit. */
(function () {
  'use strict';
  var PC = window.PerspectiveClient;
  var h = window.React.createElement;
  var COMPONENTS = __COMPONENTS__;
  var SHEETS = __SHEETS__;

  function read(tree, f) {
    switch (f.kind) {
      case 'boolean': return tree.readBoolean(f.name, f.def);
      case 'number': return tree.readNumber(f.name, f.def);
      case 'array': return tree.readArray(f.name, f.def);
      case 'nnumber': { var v = tree.read(f.name); return (v === null || v === undefined || v === '') ? undefined : Number(v); }
      case 'nstring': { var s = tree.readString(f.name, ''); return s === '' ? null : s; }
      default: return tree.readString(f.name, f.def);
    }
  }

  // Alert records arrive with epoch millisecond times (cadre.hmi.alarm_list); the elements expect Dates.
  function toDate(v) { return (v === null || v === undefined || v === '') ? v : new Date(Number(v)); }
  function toAlerts(list) {
    if (!Array.isArray(list)) return [];
    return list.map(function (a) {
      var o = Object.assign({}, a);
      o.time = toDate(a.time);
      if (a.lastModified !== undefined) o.lastModified = toDate(a.lastModified);
      if (a.acknowledged && typeof a.acknowledged === 'object')
        o.acknowledged = Object.assign({}, a.acknowledged, { acknowledgedAt: toDate(a.acknowledged.acknowledgedAt) });
      if (a.active && typeof a.active === 'object')
        o.active = Object.assign({}, a.active, { rectifiedTime: toDate(a.active.rectifiedTime) });
      if (a.shelved && typeof a.shelved === 'object')
        o.shelved = Object.assign({}, a.shelved, { shelvedStartTime: toDate(a.shelved.shelvedStartTime),
                                                    shelvedEndTime: toDate(a.shelved.shelvedEndTime) });
      return o;
    });
  }
  var CONVERT = { alerts: toAlerts, numbers: function (v) { return Array.isArray(v) ? v.map(Number) : []; } };

  // The payload of a Perspective component event, from the element's event detail.
  function payload(kind, e, el) {
    var d = (e && e.detail) || {};
    if (kind === 'alert') {
      var a = d.alert || {};
      return { ids: a.id ? [String(a.id)] : [], id: String(a.id || ''), tagId: String(a.tagId || ''),
               source: String(a.source || ''), text: String(a.text || '') };
    }
    if (kind === 'visible') {
      var mode = d.mode || 'unacked';
      var shown = (el && el.alerts || []).filter(function (a) {
        return mode === 'shelved' ? !!a.shelved : (mode === 'all' ? true : !a.acknowledged);
      });
      return { mode: String(mode), ids: shown.filter(function (a) { return !a.acknowledged; })
                                            .map(function (a) { return String(a.id); }) };
    }
    return {};
  }

  function wrapper(spec) {
    class ObWrapper extends PC.Component {
      constructor(props) {
        super(props);
        this.el = null;
        this.handlers = [];
        this.applied = {};
        // row selection (alarm lists, module 0.4.2): the ids shown and sent, the table and what watches it
        this.selIds = [];
        this.selSent = [];
        this.selOn = false;
        this.selTouched = false;
        this.selQueued = false;
        this.table = null;
        this.selHost = null;
        this.tableKey = null;
        this.onTick = (e) => {
          var t = this.table;
          if (!t) return;
          this.writeSelection(((e && e.detail && e.detail.selectedRowIds) || []).map(String));
          this.showSelection(t);
        };
        this.selWatch = (spec.selection && typeof MutationObserver === 'function')
          ? new MutationObserver(() => { if (this.selOn || this.selTouched) this.syncSelection(); }) : null;
        this.setRef = (el) => {
          this.unlisten();
          this.selDetach();
          this.el = el;
          this.applied = {};
          if (el && spec.sheet) this.sheets();
          if (el) {
            (spec.events || []).forEach((ev) => {
              var f = (e) => this.fire(ev, e);
              el.addEventListener(ev.dom, f);
              this.handlers.push([el, ev.dom, f]);
            });
          }
          this.apply();
        };
      }
      componentDidUpdate() { this.apply(); }
      componentWillUnmount() { this.unlisten(); this.selDetach(); }
      // Rules added to the shadow root of the element, and of the chip inside a readout (spec.chipSheet). The
      // shadow root exists once the element is connected and has drawn once, so the work waits for that; it
      // runs again after each update, because an alert frame around a readout draws a new chip.
      sheets() {
        var el = this.el;
        if (!el) return;
        Promise.resolve(el.updateComplete).then(() => {
          var put = function (root, css) {
            if (!root || root.querySelector('style[data-cadre]')) return;
            var st = document.createElement('style');
            st.setAttribute('data-cadre', '');
            st.textContent = css;
            root.appendChild(st);
          };
          put(el.shadowRoot, SHEETS[spec.sheet]);
          if (spec.chipSheet && el.shadowRoot) {
            var chip = el.shadowRoot.querySelector('obc-transmitter-button');
            if (chip) {
              put(chip.shadowRoot, SHEETS[spec.chipSheet]);
              chip.toggleAttribute('data-stretch', el.hasAttribute('data-stretch'));
            }
          }
        });
      }
      unlisten() {
        this.handlers.forEach(function (h) { h[0].removeEventListener(h[1], h[2]); });
        this.handlers = [];
      }
      fire(ev, e) {
        var ce = this.props.componentEvents;
        if (ce && typeof ce.fireComponentEvent === 'function') ce.fireComponentEvent(ev.name, payload(ev.payload, e, this.el));
      }
      apply() {
        var el = this.el;
        if (!el) return;
        var p = this.props.props;
        // no speed: the element prints one unless both its speed properties are undefined
        var speedless = spec.speedless && p.hasSpeed === false;
        for (var i = 0; i < spec.fields.length; i++) {
          var n = spec.fields[i].name;
          if (speedless && (n === 'speed' || n === 'speedInPercent')) { if (el[n] !== undefined) el[n] = undefined; continue; }
          if (spec.generator && n === 'value') continue;      // set from the running state (applyGenerator)
          if (el[n] !== p[n]) el[n] = p[n];
        }
        if (spec.endAligned) el.toggleAttribute('data-center', !!p.center);
        if (spec.chipSheet) { el.toggleAttribute('data-stretch', !!p.stretch); this.sheets(); }
        if (spec.status) this.applyStatus(el, p);
        if (spec.generator) this.applyGenerator(el, p);
        (spec.data || []).forEach((d) => {
          var key = JSON.stringify(p[d.name] === undefined ? null : p[d.name]);
          if (this.applied[d.name] !== key) { this.applied[d.name] = key; el[d.name] = CONVERT[d.kind](p[d.name]); }
        });
        if (spec.selection) this.applySelection(p);
      }
      // ---- Row selection of the two alarm lists (module 0.4.2). OpenBridge's table draws the tick column (an
      // obc-checkbox in each row, and one in the header of the full list) when its `selectable` is true, takes the
      // ticked ids from `selectedRowIds` and reports a toggle as `selection-change`; the alert list sets none of the
      // three, so the wrapper sets them on the table inside the list (the alert panel nests the list in its shadow
      // root). A tick stops its own click, so a toggle never reaches the row click. The wrapper keeps the ids itself,
      // shows a toggle at once and writes it to `selectedIds`; a value that comes back is either the wrapper's own
      // echo (ignored) or an outside change, such as the library clearing the selection after an acknowledgement
      // (it wins). Ids of rows the list no longer shows are dropped (pruneSelection).
      applySelection(p) {
        var on = !!p.selectable;
        if (!on && !this.selTouched) return;
        this.selTouched = true;
        this.selOn = on;
        var incoming = Array.isArray(p.selectedIds) ? p.selectedIds.map(String) : [];
        var at = this.selSent.indexOf(JSON.stringify(incoming));
        if (at >= 0) this.selSent.splice(0, at + 1);
        else { this.selSent = []; this.selIds = incoming; }
        this.syncSelection();
      }
      selectionHost() {
        var el = this.el;
        if (!el) return null;
        if (el.tagName === 'OBC-ALERT-LIST-DETAILS') return el;
        return el.shadowRoot ? el.shadowRoot.querySelector('obc-alert-list-details') : null;
      }
      // Waits until the element, the list inside it and the table have drawn, then binds the table.
      syncSelection() {
        var el = this.el;
        if (!el || this.selQueued) return;
        this.selQueued = true;
        var table = null;
        Promise.resolve(el.updateComplete).then(() => {
          var host = this.selectionHost();
          return host && host !== el ? host.updateComplete : null;
        }).then(() => {
          var host = this.selectionHost();
          table = host && host.shadowRoot ? host.shadowRoot.querySelector('obc-table') : null;
          return table ? table.updateComplete : null;
        }).then(() => {
          this.selQueued = false;
          if (this.el === el) this.bindSelection(table);
        }).catch(() => { this.selQueued = false; });
      }
      bindSelection(t) {
        var host = this.selectionHost();
        if (this.table !== t || this.selHost !== host) {
          if (this.table) this.table.removeEventListener('selection-change', this.onTick);
          if (this.selWatch) this.selWatch.disconnect();
          this.table = t;
          this.selHost = host;
          this.tableKey = null;
          if (t) t.addEventListener('selection-change', this.onTick);
          // the list draws a new table when it was empty, and the table draws new rows when its data changes
          if (this.selWatch && host && host.shadowRoot) this.selWatch.observe(host.shadowRoot, { childList: true, subtree: true });
          if (this.selWatch && t && t.renderRoot) this.selWatch.observe(t.renderRoot, { childList: true, subtree: true });
        }
        // no table: the list shows no row (an empty list draws a message instead), so nothing stays selected
        if (!t) { if (host && this.selOn && this.selIds.length) this.writeSelection([]); return; }
        if (t.selectable !== this.selOn) t.selectable = this.selOn;
        if (!this.selOn) { if (t.selectedRowIds !== undefined) t.selectedRowIds = undefined; this.tableKey = null; return; }
        this.pruneSelection(t);
        this.showSelection(t);
      }
      // The table's own ids (as the rows carry them) for the selected strings that its rows still show.
      rowIds(t, ids) {
        var byKey = {};
        (t.data || []).forEach(function (r) { byKey[String(r.id)] = r.id; });
        return ids.filter(function (i) { return Object.prototype.hasOwnProperty.call(byKey, i); })
                  .map(function (i) { return byKey[i]; });
      }
      showSelection(t) {
        var ids = this.rowIds(t, this.selIds), key = JSON.stringify(ids);
        if (this.tableKey !== key) { this.tableKey = key; t.selectedRowIds = ids; }
      }
      pruneSelection(t) {
        var kept = this.rowIds(t, this.selIds).map(String);
        if (kept.length !== this.selIds.length) this.writeSelection(kept);
      }
      writeSelection(ids) {
        this.selIds = ids;
        this.selSent.push(JSON.stringify(ids));
        this.put('selectedIds', ids);
      }
      put(name, value) {
        try {
          var store = this.props.store;
          if (store && store.props && typeof store.props.write === 'function') store.props.write(name, value);
        } catch (e) { /* a write refused is not a reason to break the page */ }
      }
      selDetach() {
        if (this.table) this.table.removeEventListener('selection-change', this.onTick);
        if (this.selWatch) this.selWatch.disconnect();
        this.table = null;
        this.selHost = null;
        this.selQueued = false;
      }

      // The status word of a pump, motor or fan. The element draws its status readouts from `extraReadouts`:
      // its speed while it runs and the word Off while it stands, none at all when its showStatus is false. The
      // wrapper passes showStatus on, and, when statusText is given, replaces the element's readouts with the one
      // word in the element's status place (the stock library view's status row does the same).
      applyStatus(el, p) {
        var show = p.showStatus !== false;
        if (el.showStatus !== show) el.showStatus = show;
        var text = typeof p.statusText === 'string' ? p.statusText : '';
        if (!this.statusInstalled) {
          this.statusInstalled = true;
          var base = null;
          for (var o = Object.getPrototypeOf(el); o && !base; o = Object.getPrototypeOf(o)) {
            var d = Object.getOwnPropertyDescriptor(o, 'extraReadouts');
            if (d && d.get) base = d.get;
          }
          var self = this;
          Object.defineProperty(el, 'extraReadouts', { configurable: true, get: function () {
            var own = base ? base.call(el) : [];
            if (!self.statusText || el.showStatus === false) return own;
            return [{ type: el.on ? 'state-on' : 'state-off', value: self.statusText, hasIcon: true }];
          } });
        }
        if (this.statusText !== text) { this.statusText = text; if (el.requestUpdate) el.requestUpdate(); }
      }
      // The indicator generator (module 0.4.4, spike T0 wrap W2). The element draws a disc whose scheme is its `value`
      // (`off` hides the rings and greys the disc) and knows nothing of a running state, an identifier, a status word
      // or an alert. The wrapper selects the scheme from `on` (a generator that is not running draws `off`; one that
      // runs draws `value`, the regular scheme where `value` is off), and draws the rest with OpenBridge's own elements,
      // unchanged, in the shadow root of the indicator: `obc-alert-frame` over the 48 px symbol, which colours its
      // levels as the other device components do, and `obc-automation-button-readout-stack`, the identifier and the
      // status word as the other symbols print them. The plain fields `tag`, `on`, `alert` and `alertFrameMode`
      // are set on the element as well, which is where the glass gates read a device component's state.
      applyGenerator(el, p) {
        var value = p.on ? (p.value === 'off' ? 'regular' : p.value) : 'off';
        if (el.value !== value) el.value = value;
        el.tag = p.tag || '';
        el.on = !!p.on;
        el.alert = !!p.alert;
        el.alertFrameMode = p.alertFrameMode;
        el.alertFrameStatus = p.alertFrameStatus;
        Promise.resolve(el.updateComplete).then(() => { if (this.el === el) this.drawGenerator(el, p); });
      }
      drawGenerator(el, p) {
        var root = el.shadowRoot;
        if (!root) return;
        var frame = root.querySelector('obc-alert-frame[data-cadre]');
        if (p.alert) {
          if (!frame) {
            frame = document.createElement('obc-alert-frame');
            frame.setAttribute('data-cadre', '');
            root.appendChild(frame);
          }
          frame.type = 'small-side-flip';
          frame.thickness = 'small';
          frame.status = p.alertFrameStatus;
          frame.mode = p.alertFrameMode;
        } else if (frame) frame.remove();
        var stack = root.querySelector('obc-automation-button-readout-stack[data-cadre]');
        var side = p.readoutPosition || 'bottom';
        var show = p.showStatus !== false;
        if (side === 'none' || (!show && !p.tag)) { if (stack) stack.remove(); return; }
        if (!stack) {
          stack = document.createElement('obc-automation-button-readout-stack');
          stack.setAttribute('data-cadre', '');
          root.appendChild(stack);
        }
        var word = (typeof p.statusText === 'string' && p.statusText) ? p.statusText : (p.on ? 'On' : 'Off');
        stack.tag = p.tag || null;
        stack.readouts = show ? [{ type: p.on ? 'state-on' : 'state-off', value: word, hasIcon: true }] : [];
        stack.size = 'regular';
        stack.idTagOrientation = side === 'top' ? 'top' : 'bottom';    // as obc-automation-button does
        var at = { top: 'bottom:100%;left:50%;transform:translateX(-50%)', bottom: 'top:100%;left:50%;transform:translateX(-50%)',
                   left: 'right:100%;top:50%;transform:translateY(-50%)', right: 'left:100%;top:50%;transform:translateY(-50%)' };
        stack.style.cssText = 'position:absolute;pointer-events:none;' + (at[side] || at.bottom);
      }
      // The duty badge goes into the first free corner of the element, unless its interlock badge, which draws
      // the same icon, is already there.
      dutySlot(p) {
        if (p.badgeInterlock === 'interlock') return null;
        var corners = [['badge-bottom-left', p.badgeInterlock], ['badge-bottom-right', p.badgeCommandLocked],
                       ['badge-top-left', p.badgeControl], ['badge-top-right', p.badgeAlert]];
        for (var i = 0; i < corners.length; i++) if (!corners[i][1] || corners[i][1] === 'none') return corners[i][0];
        return null;
      }
      render() {
        var size = this.props.props.componentSize || 'regular';
        var p = this.props.props, kids = [];
        if (spec.tankSlots) {
          // slotted content replaces the tank's own: its unit (cubic metres by default) and, for a static
          // tank with no capacity, its whole readout
          if (p.unit && p.unit !== 'm\u00b3') kids.push(h('span', { slot: 'unit', key: 'unit' }, p.unit));
          if (p.static && p.hasCapacity === false) kids.push(h('span', { slot: 'readout', key: 'readout' }));
        }
        if (spec.status && p.badgeDuty) {
          var slot = this.dutySlot(p);
          if (slot) kids.push(h('obc-automation-badge', { slot: slot, key: 'duty', type: 'interlock' }));
        }
        // an out of service symbol: the library view's veil of the page colour and the word OOS, over the symbol
        var oos = (spec.status && p.outOfService) ? h('div', { className: 'cadre-ob-oos', key: 'oos' }, 'OOS') : null;
        // an element that sits at the end of its box unless the symbol is centred
        var at = spec.endAligned ? { justifyContent: p.center ? 'center' : 'flex-end' } : undefined;
        return h('div', this.props.emit(),
          h('div', { className: 'cadre-ob obc-component-size-' + size, style: at },
            h.apply(null, [spec.tag, { ref: this.setRef }].concat(kids)), oos));
      }
    }
    return ObWrapper;
  }

  COMPONENTS.forEach(function (spec) {
    var View = wrapper(spec);
    PC.ComponentRegistry.register({
      getComponentType: function () { return spec.type; },
      getViewComponent: function () { return View; },
      getDefaultSize: function () { return spec.size; },
      getPropsReducer: function (tree) {
        var out = { componentSize: tree.readString('componentSize', 'regular') };
        spec.fields.forEach(function (f) { out[f.name] = read(tree, f); });
        (spec.extras || []).forEach(function (f) { out[f.name] = read(tree, f); });
        (spec.data || []).forEach(function (d) { out[d.name] = tree.readArray(d.name, []); });
        return out;
      }
    });
  });
})();
"""


def main() -> int:
    manifest = json.loads((PKG / "custom-elements.json").read_text(encoding="utf-8"))
    defaults = json.loads((HERE / "web/defaults.json").read_text(encoding="utf-8"))
    enum_map = enums()
    bundle_js = (HERE / "web/dist/ob-components.js").read_text(encoding="utf-8")
    shutil.copyfile(HERE / "web/dist/ob-components.js.LEGAL.txt", MOUNTED / "js/ob-components.js.LEGAL.txt")
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    contract, js_specs = {}, []
    for spec in COMPONENTS:
        d = {k: (None if v == "__undefined__" else v) for k, v in defaults[spec["tag"]].items()}
        decl = declaration(manifest, spec["tag"])
        schema, fields = schema_for(spec, decl, enum_map, d)
        (SCHEMAS / f"{spec['name']}.props.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        declared = {e.get("name") for e in decl.get("events", [])}
        events = []
        for dom in spec.get("events", []):
            if dom not in declared:
                raise SystemExit(f"{spec['tag']} declares no event {dom!r} in the manifest")
            name, kind, text = ALERT_EVENTS[dom]
            events.append({"dom": dom, "name": name, "payload": kind})
            props = ({"ids": {"type": "array", "description": "The alert ids of the event."},
                      "id": {"type": "string"}, "tagId": {"type": "string", "description": "The device folder."},
                      "source": {"type": "string"}, "text": {"type": "string"}} if kind == "alert" else
                     {"ids": {"type": "array", "description": "The alert ids of the event."},
                      "mode": {"type": "string", "description": "The list mode."}} if kind == "visible" else {})
            (SCHEMAS / f"{spec['name']}.{name}.json").write_text(json.dumps(
                {"type": "object", "description": text, "properties": props}, indent=2) + "\n", encoding="utf-8")
        js_specs.append({"type": spec["type"], "tag": spec["tag"], "size": spec["size"], "fields": fields,
                         "extras": [{"name": n, "kind": EXTRA[n]["kind"], "def": EXTRA[n]["def"]} for n in spec.get("extra", [])],
                         "speedless": bool(spec.get("speedless")), "generator": bool(spec.get("generator")), "tankSlots": bool(spec.get("tankSlots")),
                         "sheet": spec.get("sheet", ""), "chipSheet": spec.get("chipSheet", ""),
                         "selection": bool(spec.get("selection")),
                         "status": bool(spec.get("status")), "endAligned": bool(spec.get("endAligned")),
                         "data": [{"name": n, "kind": k} for n, k in spec.get("data", {}).items()],
                         "events": events})
        contract[spec["type"]] = {"element": spec["tag"], "title": spec["title"], "palette": spec["palette"],
                                  "schema": f"schemas/{spec['name']}.props.json",
                                  "defaultSize": spec["size"],
                                  "props": {k: {kk: vv for kk, vv in v.items() if kk != "description"}
                                            for k, v in schema["properties"].items() if k != "style"}}
        if events:
            contract[spec["type"]]["events"] = {e["name"]: {"element": e["dom"], "schema": f"schemas/{spec['name']}.{e['name']}.json"}
                                                for e in events}
        print(f"{spec['type']}: {len(fields)} properties, {len(spec.get('data', {}))} data, {len(events)} events from {spec['tag']}")
    zoom = CANVAS_ZOOM
    zschema = {"type": "object", "additionalProperties": False,
               "properties": {**{k: dict(v) for k, v in zoom["props"].items()},
                              "style": {"$ref": "urn:ignition-schema:schemas/style-properties.schema.json",
                                        "default": {"classes": ""}}}}
    (SCHEMAS / f"{zoom['name']}.props.json").write_text(json.dumps(zschema, indent=2) + "\n", encoding="utf-8")
    contract[zoom["type"]] = {"element": None, "title": zoom["title"], "palette": zoom["palette"],
                              "schema": f"schemas/{zoom['name']}.props.json", "defaultSize": zoom["size"],
                              "props": {k: {kk: vv for kk, vv in v.items() if kk != "description"}
                                        for k, v in zoom["props"].items()}}
    print(f"{zoom['type']}: {len(zoom['props'])} properties (web/canvaszoom.js)")
    canvas_zoom_js = (HERE / "web/canvaszoom.js").read_text(encoding="utf-8")
    wrappers = WRAPPER.replace("__COMPONENTS__", json.dumps(js_specs, separators=(",", ":")))         .replace("__SHEETS__", json.dumps(SHEETS, separators=(",", ":")))
    (MOUNTED / "js/cadre-ob.js").write_text(bundle_js + "\n" + wrappers + "\n" + canvas_zoom_js, encoding="utf-8")
    css, stats = scoped_css(bundle_js)
    (MOUNTED / "css").mkdir(parents=True, exist_ok=True)
    (MOUNTED / "css/cadre-ob.css").write_text(css, encoding="utf-8")
    (MOUNTED / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PKG / "dist/NotoSans.ttf", MOUNTED / "fonts/NotoSans-OB.ttf")
    (HERE / "components.json").write_text(json.dumps(contract, indent=1) + "\n", encoding="utf-8")
    print("stylesheet", stats, f"{len(css) / 1024:.0f} KiB")
    print("cadre-ob.js", f"{(MOUNTED / 'js/cadre-ob.js').stat().st_size / 1024:.0f} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
