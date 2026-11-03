"""The component test page (L4 item 10): every library component with the features to test, generated from the
library's own catalogue, so that any migration can add it with `screen.py --component-test`.

The page is a descriptor (`cadre-hmi-screen/1`), a diagram of labelled sections, built from:

  library/contracts.json    the views, their kinds, parameters and defaults, state, status mode and size
  library/profile.json      the kinds (embed boxes, identifier widths), the device kinds with their members,
                            pulses and binding rules, the faceplates and their tabs, the alarm priorities
  screen.KIND_VIEW, GENSET_VIEW, MODULE_KIND   which view draws a kind, and what the module renders instead

It states nothing that a contract lacks: a parameter a case sets is checked against the contract of its view
(`check`), and the module's enumerations are read from `module/components.json`, so a case the module cannot draw
is left to the library's view or left out (`module_value_ok`).

Four kinds of content, in labelled sections (wiki page 13 section 13):

  static grids      one section for each kind, a cell for each state and each feature a symbol can state
                    (`cases`), the notification (alert frames, every priority colour and mode), the badges and
                    marks, and a pipe for each medium (the Color toggle of the toolbar paints them)
  test devices      a device for each device kind and one for each alarm priority, on memory tags (and
                    expression tags that follow their commands) in a folder of the project's own tag root,
                    `_componentTest`, so that the project's alarm scope includes them and no plant tag is
                    touched; their symbols open the faceplates, the faceplates' commands change their states,
                    and the alarms are tag alarms in the library's one form (`alarms.definition`)
  gallery tags      each state and mark parameter a gallery symbol states is a memory tag of its own under
                    `_componentTest/gallery/<symbol>/<param>`, with the case's value as its starting value (L5):
                    the symbols read tags, and the layout parameters (position, variant, vertical, identifiers)
                    stay fixed in the view
  page buttons      pulses of the test tags only (`Bench.pulse_tags`): raise an alarm for a minute, set a fault
                    (the library's `page_pulse`, write path W18, asks first and holds the tag true)

`build` returns the descriptor, the device model entries, the tag folder and the pulse tags. `screen.py` adds
them to the build (`--component-test`): the descriptor to the set (tag model `external`, so that the
generator writes none of its tags), the entries to the device model where the project has one, and the folder to
the tag model the gates read and to a file beside the build, which the deploy imports into the tag root.
"""
from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import alarms, library, screen  # noqa: E402
else:
    from . import alarms, library, screen

ROOT = Path(__file__).resolve().parents[2]
FOLDER = "_componentTest"            # the test tags' folder under the project's tag root
PAGE = {"id": "ComponentTest", "route": "/component-test", "view": "Screens/ComponentTest",
        "title": "Component test", "navLabel": "Tools: Component test", "icon": "placeholder",
        "level": "Level 4 support", "nav": True, "layout": "diagram"}
WIDTH = 1580                          # the width of the sample frames' pages
MARGIN, GAP, HEAD = 12, 12, 30        # px: the page margin, between sections, and a section's heading
CAPTION = 16                          # px: the height of a case's caption line
PULSE_MS = 60000                      # how long a page button holds a test tag true
RAISE_ALL = f"{FOLDER}/ALM_ALL/raise"  # one tag raises every test alarm

# Enumerations the contracts do not state (a contract holds the default only). Each is a fact of the library's own
# drawing code, not of a vendor document: the alert colours (`library.ALERT_COLOURS`), the control badges
# (`library.CONTROL_BADGES`), the alert modes `library._alert_frame` reads, the interlock badges `library._badges` reads.
ALERT_STATUS = tuple(library.ALERT_COLOURS)
ALERT_MODE = ("acked-active", "unacked-active", "unacked-rectified")
BADGE_INTERLOCK = ("interlock", "interlock-inhibit")
BADGE_LOCKED = "command-locked"       # the library shows any value but none; the module has this one
# A symbol's readout sides (the keys of `readoutExtent` in its contract) and the variants of its holder
POSITIONS = ("bottom", "top", "left", "right", "none")
VARIANTS = ("regular", "flat", "double")
MODULE_STATUS = ("alarm", "warning", "caution")   # the alert statuses both renderings draw (`critical` is the library's)
# The parameters of a gallery symbol that read a memory tag (L5): the state, its readings and the marks. Everything
# else (the position of the readout, the variant, vertical, the identifier, the status text) is layout, fixed in the view.
GALLERY_PARAMS = frozenset({
    "on", "open", "speed", "value", "trend", "setpoint", "output", "manual", "text", "step", "activated", "alert",
    "alertFrameStatus", "alertFrameMode", "badgeControl", "badgeInterlock", "badgeCommandLocked", "badgeDuty",
    "outOfService", "progress",
    "value2", "closed",   # the state of the valve glyphs (B4), which no earlier kind has
    "level",              # the level of the battery and tank indicators (B5); their `value` is the scheme and is bound too
    "state", "priority", "medium", "bottomValue",   # the live state of the specialty tanks and the gauges (B6, B7)
    "selectedPosition", "adviceValue", "setpointValue"})   # the hydraulic valves' position and the transmitter button's segments (B8)
GALLERY_PREFIXES = ("S_", "N_", "B_")   # the ids of the symbols of the static grids


# ---------------------------------------------------------------------------------------
# The product
# ---------------------------------------------------------------------------------------
@dataclass
class Bench:
    descriptor: dict
    devices: list[dict]                       # device model entries (`cadre-hmi-devices/1` devices)
    tags: dict                                # the folder document of the test tags, named FOLDER
    pulse_tags: list[str] = field(default_factory=list)   # the tags the page buttons pulse, relative to the tag root
    notes: list[str] = field(default_factory=list)
    gallery: dict = field(default_factory=dict)           # symbol id -> {parameter: starting value} of its gallery tags

    def extend_devices(self, model: dict | None) -> dict | None:
        """The device model with the test devices added (a copy); None where the project has no device model, whose
        devices then keep the rules of a project without one (their members are the faceplates' defaults)."""
        if model is None:
            return None
        out = copy.deepcopy(model)
        known = {d["id"] for d in out["devices"]}
        out["devices"] += [copy.deepcopy(d) for d in self.devices if d["id"] not in known]
        return out

    def extend_tags(self, tag_model: dict | None) -> dict | None:
        """The tag model with the test folder added (a copy), for the gates that read it."""
        if tag_model is None:
            return None
        out = copy.deepcopy(tag_model)
        out["tags"] = [t for t in out.get("tags", []) if t.get("name") != FOLDER] + [copy.deepcopy(self.tags)]
        return out


# ---------------------------------------------------------------------------------------
# Tags and the device model
# ---------------------------------------------------------------------------------------
def mem(name: str, dtype: str, value, **extra) -> dict:
    return {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dtype, "value": value, **extra}


def expr(name: str, dtype: str, expression: str, **extra) -> dict:
    return {"name": name, "tagType": "AtomicTag", "valueSource": "expr", "dataType": dtype,
            "expression": expression, "executionMode": "FixedRate", **extra}


def member(dtype: str, access: str = "read", **extra) -> dict:
    return {"type": dtype, "access": access, **extra}


def pulse(caption: str) -> dict:
    return member("Boolean", "write", pulse=True, caption=caption)


def cmd_state(extra: str = "") -> str:
    """A device's state follows its command (a fault stops it): the form of the sample plants (`ref` in wtp.py)."""
    return "coalesce({[.]cmd}, false) && !coalesce({[.]fault}, false)" + extra


def latch(on: str, off: str, name: str) -> str:
    """A state set by one pulse and cleared by another, holding between them (a self reference, GF-16)."""
    return (f"if(coalesce({{[.]{off}}}, false), false, if(coalesce({{[.]{on}}}, false), true, "
            f"coalesce({{[.]{name}}}, false)))")


MODES = [{"value": 0, "name": "Program", "owner": "program"}, {"value": 1, "name": "Operator", "owner": "operator"},
         {"value": 2, "name": "Maintenance", "owner": "maintenance"}, {"value": 3, "name": "Local", "owner": "local"}]


def device_specs(root: str, node: str) -> dict[str, dict]:
    """The test devices: id -> {kind, title, label, members (device model), tags (the folder's tags), modes}.
    Each device carries only members the library knows for its kind (gate G7 devices); the tags beside them (the
    `raise` of an alarm device) are the test page's own."""
    def alarm(name, ident, text, priority, **kw):
        return alarms.definition(name, ident, text, priority, node, **kw)

    def sim(ident: str) -> str:
        return f"{root}/{FOLDER}/{ident}"

    def switched(kind, title, label, *, speed=True, fault_alarm=False, modes=True):
        members = {"state": member("Boolean"), "cmd": member("Boolean", "write"), "fault": member("Boolean", "write"),
                   "alarmAck": member("Boolean", "write")}
        tags = [expr("state", "Boolean", cmd_state()), mem("cmd", "Boolean", False),
                mem("fault", "Boolean", False, **({"alarms": [alarm("Fault", title, "Fault", "High")]}
                                                  if fault_alarm else {})),
                mem("alarmAck", "Boolean", False)]
        if modes:
            members["mode"] = member("Int4", "write")
            tags.append(mem("mode", "Int4", 1))
        if speed:
            members.update({"speed": member("Float8"), "speedSp": member("Float8", "write")})
            tags += [mem("speedSp", "Float8", 60.0),
                     expr("speed", "Float8", "if(coalesce({[.]state}, false), coalesce({[.]speedSp}, 0), 0)")]
        return {"kind": kind, "title": title, "label": label, "members": members, "tags": tags,
                "modes": MODES if modes else None}

    limits = {"hiLimit": member("Float8", "write"), "loLimit": member("Float8", "write")}
    instrument = {"kind": "instrument", "members": {"value": member("Float8"), **limits}, "modes": None,
                  "tags": [mem("value", "Float8", 42.5, alarms=[
                      alarm("High", "TB-READOUT", "High", "Medium", mode="AboveValue", setpoint=80.0, limit="hiLimit"),
                      alarm("Low", "TB-READOUT", "Low", "Low", mode="BelowValue", setpoint=20.0, limit="loLimit")]),
                      mem("hiLimit", "Float8", 80.0), mem("loLimit", "Float8", 20.0)]}
    specs: dict[str, dict] = {
        "TB_PUMP": switched("pump", "TB-PUMP", "Test pump: Start and Stop on the faceplate", fault_alarm=True),
        "TB_MOTOR": switched("motor", "TB-MOTOR", "Test motor"),
        "TB_FAN": switched("fan", "TB-FAN", "Test fan", modes=False),
        "TB_VALVE": switched("valve", "TB-VALVE", "Test valve: Open and Close on the faceplate", speed=False),
        "TB_AVALVE": switched("analogvalve", "TB-AVALVE", "Test analogue valve", speed=False, modes=False),
        "TB_DAMPER": switched("damper", "TB-DAMPER", "Test damper", speed=False, modes=False),
        "TB_TANK": {"kind": "tank", "title": "TB-TANK", "label": "Test tank: write the limits on the faceplate",
                    "members": {"level": member("Float8"), **limits}, "modes": None,
                    "tags": [mem("level", "Float8", 62.0, alarms=[
                        alarm("High level", "TB-TANK", "High level", "Medium", mode="AboveValue", setpoint=90.0,
                              limit="hiLimit")]), mem("hiLimit", "Float8", 90.0), mem("loLimit", "Float8", 10.0)]},
        "TB_READOUT": {**instrument, "title": "TB-READOUT", "label": "Test instrument: write the limits"},
        "TB_FIELD": {"kind": "instrument", "title": "TB-FIELD", "label": "Test instrument field",
                     "members": {"value": member("Float8")}, "modes": None, "tags": [mem("value", "Float8", 36.0)]},
        "TB_CTRL": {"kind": "controller", "title": "TB-CTRL", "label": "Test controller", "modes": None,
                    "members": {"value": member("Float8"), "sp": member("Float8", "write"), "out": member("Float8"),
                                "manual": member("Boolean", "write"), "manOut": member("Float8", "write"),
                                "gain": member("Float8", "write"), "ti": member("Float8", "write"),
                                "td": member("Float8", "write")},
                    "tags": [mem("value", "Float8", 50.0), mem("sp", "Float8", 55.0), mem("manual", "Boolean", False),
                             mem("manOut", "Float8", 30.0), mem("gain", "Float8", 1.0), mem("ti", "Float8", 10.0),
                             mem("td", "Float8", 0.0),
                             expr("out", "Float8", "if(coalesce({[.]manual}, false), coalesce({[.]manOut}, 0), "
                                                   "coalesce({[.]sp}, 0))")]},
        "TB_IND": {"kind": "indicator", "title": "TB-IND", "label": "Test digital input: a button sets it",
                   "members": {"state": member("Boolean")}, "modes": None, "tags": [mem("state", "Boolean", False)]},
        "TB_SEQ": {"kind": "sequence", "title": "TB-SEQ", "label": "Test sequence: the pulses change its state",
                   "modes": None,
                   "members": {"step": member("Int4"), "stepText": member("String"), "fault": member("Boolean"),
                               "inService": member("Boolean"), "enabled": member("Boolean"),
                               "normal": member("Boolean"), "trigger": pulse("Start cycle"),
                               "cmdInService": pulse("In service"), "cmdOutOfService": pulse("Out of service"),
                               "cmdEnable": pulse("Enable"), "cmdDisable": pulse("Disable")},
                   "tags": [mem("step", "Int4", 2), mem("stepText", "String", "Mixing"), mem("fault", "Boolean", False),
                            mem("normal", "Boolean", True), mem("trigger", "Boolean", False),
                            mem("cmdInService", "Boolean", False), mem("cmdOutOfService", "Boolean", False),
                            mem("cmdEnable", "Boolean", False), mem("cmdDisable", "Boolean", False),
                            expr("inService", "Boolean", latch("cmdInService", "cmdOutOfService", "inService")),
                            expr("enabled", "Boolean", latch("cmdEnable", "cmdDisable", "enabled"))]},
        "TB_GEN": {"kind": "generator", "title": "TB-GEN", "label": "Test generator: Start and Stop on the faceplate",
                   "modes": None,
                   "members": {"state": member("Boolean"), "runText": member("String"), "fault": member("Boolean"),
                               "faultCode": member("Int4"), "engineSpeed": member("Float8"),
                               "fuelLevel": member("Float8"), "cmdStart": pulse("Start generator"),
                               "cmdStop": pulse("Stop generator"), "cmdReset": pulse("Reset generator")},
                   "tags": [mem("cmdStart", "Boolean", False), mem("cmdStop", "Boolean", False),
                            mem("cmdReset", "Boolean", False), mem("fault", "Boolean", False),
                            mem("faultCode", "Int4", 0), mem("fuelLevel", "Float8", 75.0),
                            expr("state", "Boolean", latch("cmdStart", "cmdStop", "state")),
                            expr("runText", "String", "if(coalesce({[.]state}, false), 'Running', 'Stopped')"),
                            expr("engineSpeed", "Float8", "if(coalesce({[.]state}, false), 1500, 0)")]},
    }
    # a motor that carries only its state (L5, contract 3.3): a plain motor symbol opens its asm faceplate
    specs["TB_MSTATE"] = {"kind": "motor", "title": "TB-MS", "faceplate": "asm", "modes": None,
                          "label": "Test motor with a state only: a plain motor symbol opens this faceplate",
                          "members": {"state": member("Boolean")}, "tags": [mem("state", "Boolean", False)]}
    for prio in alarms.PRIORITIES:   # one alarm device for each priority: the state follows a button's pulse
        ident = f"ALM_{prio.upper()}"
        specs[ident] = {"kind": "indicator", "title": f"ALM-{prio.upper()}", "modes": None,
                        "label": f"Test alarm: one {prio} alarm; the button raises it for a minute",
                        "members": {"state": member("Boolean"), "alarmAck": member("Boolean", "write")},
                        "tags": [mem("raise", "Boolean", False), mem("alarmAck", "Boolean", False),
                                 expr("state", "Boolean", "coalesce({[.]raise}, false) || coalesce({"
                                      f"{sim('ALM_ALL')}/raise}}, false)",
                                      alarms=[alarm(f"{prio} test", f"ALM-{prio.upper()}", f"{prio} test", prio)])]}
    return specs


# The lamps of the section "Indicator: colour by state" (L5): the state follows the pulses of the page's buttons, a
# Boolean, a number (0 off, 1 on, 2 alarm), a string and a number painted by CSS colours; each lamp binds `state` of its
# folder `lamps/<id>`.
LAMPS = {
    "L_BOOL": {"caption": "Boolean: off, on", "states": None,
               "tags": [mem("set", "Boolean", False),
                        expr("state", "Boolean", "coalesce({[.]set}, false)")],
               "buttons": [("set", "Boolean lamp on")]},
    "L_NUM": {"caption": "0 off, 1 on, 2 alarm",
              "states": [{"value": 0, "colour": "off", "label": "Off"}, {"value": 1, "colour": "on", "label": "On"},
                         {"value": 2, "colour": "alarm", "label": "Alarm"}],
              "tags": [mem("set1", "Boolean", False), mem("set2", "Boolean", False),
                       expr("state", "Float8", "if(coalesce({[.]set2}, false), 2, if(coalesce({[.]set1}, false), 1, 0))")],
              "buttons": [("set1", "Lamp to 1 (on)"), ("set2", "Lamp to 2 (alarm)")]},
    "L_STR": {"caption": "STOP, RUN, TRIP",
              "states": [{"value": "STOP", "colour": "off", "label": "Stopped"},
                         {"value": "RUN", "colour": "active", "label": "Running"},
                         {"value": "TRIP", "colour": "warning", "label": "Tripped"}],
              "tags": [mem("run", "Boolean", False), mem("trip", "Boolean", False),
                       expr("state", "String", "if(coalesce({[.]trip}, false), 'TRIP', "
                                               "if(coalesce({[.]run}, false), 'RUN', 'STOP'))")],
              "buttons": [("run", "String lamp: RUN"), ("trip", "String lamp: TRIP")]},
    "L_PAINT": {"caption": "0 grey, 1 green (CSS paints)",
                "states": [{"value": 0, "colour": "#7a7a7a"}, {"value": 1, "colour": "#1b8a3c"}],
                "tags": [mem("set", "Boolean", False),
                         expr("state", "Float8", "if(coalesce({[.]set}, false), 1, 0)")],
                "buttons": [("set", "Paint lamp to 1")]},
}


def gallery_tag(value) -> dict | None:
    """A gallery tag's data type and starting value for a parameter value, None for a value no memory tag holds."""
    if isinstance(value, bool):
        return {"dataType": "Boolean", "value": value}
    if isinstance(value, (int, float)):
        return {"dataType": "Float8", "value": float(value)}
    if isinstance(value, str):
        return {"dataType": "String", "value": value}
    return None


def tag_folder(specs: dict[str, dict], gallery: dict | None = None) -> dict:
    """The test folder: each device's tags beside the all-alarms tag, the lamps' tags and the gallery's."""
    kids = [{"name": ident, "tagType": "Folder", "tags": copy.deepcopy(s["tags"])} for ident, s in specs.items()]
    kids.append({"name": "ALM_ALL", "tagType": "Folder", "tags": [mem("raise", "Boolean", False)]})
    kids.append({"name": "lamps", "tagType": "Folder", "tags": [
        {"name": ident, "tagType": "Folder", "tags": copy.deepcopy(spec["tags"])} for ident, spec in LAMPS.items()]})
    if gallery:
        kids.append({"name": "gallery", "tagType": "Folder", "tags": [
            {"name": sid, "tagType": "Folder",
             "tags": [mem(p, gallery_tag(v)["dataType"], gallery_tag(v)["value"]) for p, v in params.items()]}
            for sid, params in gallery.items()]})
    return {"name": FOLDER, "tagType": "Folder", "tags": kids}


def model_entries(specs: dict[str, dict]) -> list[dict]:
    out = []
    for ident, s in specs.items():
        entry = {"id": f"{FOLDER}/{ident}", "kind": s["kind"], "title": s["title"], "label": s["label"],
                 "members": copy.deepcopy(s["members"])}
        if s.get("faceplate"):
            entry["faceplate"] = s["faceplate"]
        if s.get("modes"):
            entry["modes"] = copy.deepcopy(s["modes"])
        out.append(entry)
    return out


# ---------------------------------------------------------------------------------------
# Cases: what a symbol of a kind can state
# ---------------------------------------------------------------------------------------
@dataclass
class Case:
    caption: str
    params: dict
    bind: dict = field(default_factory=dict)
    size: tuple | None = None            # w, h of a box kind (the contract's size else)
    extra: dict = field(default_factory=dict)   # keys of the symbol beside params (device, label)


_COMPONENTS: dict = {}   # module/components.json, read once


def module_enum(kind: str, param: str) -> list | None:
    """The values the module's component accepts for `param`, None where its schema states no enumeration."""
    ctype = screen.module_type(kind)
    if not _COMPONENTS:
        _COMPONENTS.update(json.loads(screen.MODULE_COMPONENTS.read_text(encoding="utf-8"))
                           if screen.MODULE_COMPONENTS.exists() else {"": {}})
    prop = _COMPONENTS.get(ctype or "", {}).get("props", {}).get(screen.MODULE_PARAM.get(kind, {}).get(param, param), {})
    return prop.get("enum")


def module_value_ok(kind: str, params: dict, param: str) -> bool:
    """Whether the symbol is drawn right under both renderings: the library's view takes any value its contract
    allows, the module's component only those of its enumeration, unless the generator keeps the symbol on the
    library's view for it (`screen.module_draws`)."""
    enum = module_enum(kind, param)
    value = screen.MODULE_VALUE.get(kind, {}).get(param, {}).get(params.get(param), params.get(param))
    if enum is None or value in enum:
        return True
    return not screen.module_draws(kind, params, target="module")


def kind_cases(kind: str, contract: dict, prof: dict) -> list[Case]:
    """The cases of one kind, derived from its contract and the profile and then completed with the kind's own
    values (`EXTRAS`): the state both ways, every boolean parameter against its default, every enumeration of
    a symbol (`POSITIONS`, `VARIANTS`) and the readout's text. A case that sets a value a contract lacks is an
    error (`check`), and one the module cannot draw is dropped (`module_value_ok`)."""
    params = contract["params"]
    state = contract.get("state")
    out: list[Case] = []
    symbol = contract.get("anchor") == "symbol-centre" and kind != "readout"

    def add(caption, extra_params, **kw):
        p = {**base, **extra_params}
        if all(module_value_ok(kind, p, k) for k in extra_params):
            out.append(Case(caption, p, **kw))
    base: dict = {}
    if symbol:
        base = {"hasTag": True, "tag": ident_of(kind)}
        if state:
            add(f"{state_words(contract)[0]}", {state: False})
            add(f"{state_words(contract)[1]}", {state: True})
        mode = contract.get("statusMode")
        if mode == "speed":
            add("on, 60 %", {state: True, "hasSpeed": True, "speed": 60})
        if mode == "opening":
            add("50 %", {state: True, "value": 50})
        for pos in POSITIONS[1:]:
            if pos in (contract.get("readoutExtent") or {}):
                add(f"readout {pos}", {state: True, "readoutPosition": pos})
        for v in VARIANTS[1:]:
            if "variant" in params and (v != "double" or mode == "speed"):
                add(f"variant {v}", {state: True, "variant": v})
        if "vertical" in params:
            add("vertical", {state: True, "vertical": True})
        add("no ID tag", {state: True, "hasTag": False})
        add("status text", {state: True, "statusText": "Standby"})
        add("status hidden", {state: True, "showStatus": False})
        # the marks every automation symbol draws alike (the badges, the alert frame, the greying, the progress ring
        # and the activated ground); the notification and marks sections show each value on the pump and the lamp
        add("badges", {state: True, "badgeControl": "manual", "badgeInterlock": "interlock",
                       "badgeCommandLocked": BADGE_LOCKED, "badgeDuty": True})
        add("alert", {state: True, "alert": True, "alertFrameStatus": "warning", "alertFrameMode": "unacked-active"})
        add("out of service", {state: True, "outOfService": True})
        add("progress", {state: True, "progress": True})
        add("activated", {state: True, "activated": True})
    out += EXTRAS.get(kind, lambda c: [])(contract)
    return out


def ident_of(kind: str) -> str:
    """An identifier of at most 8 characters, which the default embed holds (`identifier.fits`)."""
    return {"pump": "P-101", "motor": "M-101", "fan": "F-101", "valve": "XV-101", "analogvalve": "FCV-101",
            "damper": "DM-101", "filter": "FL-101", "switch": "SW-101", "indicator": "LP-101",
            "generator": "GEN-1"}.get(kind, "T-101")


def state_words(contract: dict) -> tuple[str, str]:
    return ("closed", "open") if contract.get("state") == "open" else ("off", "on")


def _tank(c):
    out = [Case(f"{v} %", {"value": v, "tag": "T-101", "trend": t}) for v, t in ((0, "stable"), (35, "falling"),
                                                                                 (80, "rising"), (100, "stable"))]
    out += [Case("static", {"static": True, "tag": "T-102", "hasCapacity": False}),
            Case("compact", {"value": 55, "compact": True, "tag": "T-103"}),
            Case("no percent", {"value": 55, "showPercent": False, "tag": "T-104"}),
            Case("capacity", {"value": 55, "max": 450, "unit": "m3", "tag": "T-105"}),
            Case("one decimal", {"value": 55.5, "valueFractionDigits": 1, "tag": "T-106"}),
            Case("chart", {"value": 55, "chart": True, "history": [40, 45, 52, 50, 55, 58], "tag": "T-107"}),
            Case("no ID tag", {"value": 55, "tag": "T-108", "hasTag": False})]
    return out


def _readout(c):
    out = [Case("value, unit", {"value": 12.3, "unit": "m3/h"}, size=(96, 24)),
           Case("ID tag", {"value": 7.5, "unit": "bar", "hasTag": True, "tag": "PT-101"}, size=(96, 40)),
           Case("long value", {"value": 12345.6, "unit": "kW", "hasTag": True, "tag": "ET-101"}, size=(96, 40)),
           Case("two digits", {"value": 3.14159, "unit": "bar", "format": "#,##0.00"}, size=(96, 24))]
    out += [Case(f"{'stretch' if s else 'content'}", {"value": v, "unit": "m", "stretch": s}, size=(96, 24))
            for s in (False, True) for v in (1.5, 123.4)]
    return out


def _field(c):
    return [Case("regular", {"value": 36.4, "unit": "degC", "label": "Temp", "format": "#,##0.0"}),
            Case("enhanced", {"value": 36.4, "unit": "degC", "label": "Temp", "size": "enhanced",
                              "format": "#,##0.0"}),
            Case("setpoint", {"value": 36.4, "unit": "degC", "label": "Temp", "hasSetpoint": True,
                              "setpoint": 40, "format": "#,##0.0", "setpointFormat": "#,##0.0"}),
            Case("enhanced setpoint", {"value": 36.4, "unit": "degC", "label": "Temp", "size": "enhanced",
                                       "hasSetpoint": True, "setpoint": 40, "format": "#,##0.0",
                                       "setpointFormat": "#,##0.0"}),
            Case("align start", {"value": 8, "unit": "bar", "label": "Press", "align": "start"}),
            Case("align center", {"value": 8, "unit": "bar", "label": "Press", "align": "center"}),
            Case("no label", {"value": 8, "unit": "bar", "label": "Press", "hasTag": False})]


def _controller(c):
    return [Case("auto", {"value": 50, "tag": "PIC-101", "hasTag": True}),
            Case("no ID tag", {"value": 50, "hasTag": False}),
            Case("manual", {"value": 50, "manual": True, "tag": "PIC-102", "hasTag": True}),
            Case("setpoint", {"value": 50, "hasSetpoint": True, "setpoint": 55, "tag": "PIC-103"}),
            Case("setpoint and output", {"value": 50, "hasSetpoint": True, "setpoint": 55, "hasOutput": True,
                                         "output": 40, "tag": "PIC-104", "unit": "bar"})]


def _sequence(c):
    return [Case("text", {"text": "Mixing", "tag": "SQ-101"}),
            Case("with step", {"text": "Mixing", "hasStep": True, "step": 3, "tag": "SQ-102"}),
            Case("no ID tag", {"text": "Idle", "hasTag": False})]


def _generator(c):
    return []


EXTRAS = {"tank": _tank, "readout": _readout, "instrument-field": _field, "controller": _controller,
          "sequence": _sequence, "generator": _generator}


# ---------------------------------------------------------------------------------------
# Layout: blocks of items in their own coordinates, packed into the page in sections
# ---------------------------------------------------------------------------------------
@dataclass
class Block:
    """The items of one section, in coordinates from its top left corner below the heading."""
    w: float = 0
    h: float = 0
    items: list = field(default_factory=list)   # (array name of the descriptor, item)

    def add(self, array: str, item: dict) -> None:
        self.items.append((array, item))

    def extend(self, other: "Block", dx: float, dy: float) -> None:
        for array, item in other.items:
            self.items.append((array, shifted(item, dx, dy)))
        self.w, self.h = max(self.w, other.w + dx), max(self.h, other.h + dy)


def shifted(item: dict, dx: float, dy: float) -> dict:
    out = copy.deepcopy(item)
    if "from" in out:   # a pipe: its loose ends and its via points
        for end in ("from", "to"):
            if "x" in out[end]:
                out[end]["x"] += dx
                out[end]["y"] += dy
        if "via" in out:
            out["via"] = [[x + dx, y + dy] for x, y in out["via"]]
    else:
        out["x"] += dx
        out["y"] += dy
    return out


def label(ident: str, text: str, x: float, y: float, w: float, h: float = CAPTION, *, style: str = "label",
          align: str = "center") -> dict:
    return {"id": ident, "x": x, "y": y, "w": w, "h": h, "text": text, "style": style, "align": align}


def text_width(text: str, per_char: float = 7.0) -> float:
    return math.ceil(len(text) * per_char + 8)


def button(ident: str, text: str, x: float, y: float, w: float, action: dict, h: float = 30) -> dict:
    return {"id": ident, "x": x, "y": y, "w": w, "h": h, "label": text, "action": action}


def case_symbol(sid: str, kind: str, case: Case, contract: dict) -> dict:
    """The descriptor symbol of a case at (0, 0): the 48 px symbol of an automation symbol, else the case's size or the
    block the contract's flags need."""
    params = dict(case.params)
    if contract.get("anchor") == "symbol-centre" and kind != "readout":
        w = h = 48
    else:
        w, h = case.size or tuple(library.block_size(contract, params))
    return {"id": sid, "kind": kind, "x": 0, "y": 0, "w": w, "h": h, "params": params, "bind": dict(case.bind),
            **case.extra}


def grid(prefix: str, kind: str, cases: list[Case], contracts: dict, avail: float = WIDTH - 2 * MARGIN - 24,
         group: int = 1) -> Block:
    """A grid of cases, a symbol and its caption in each cell, as many columns as `avail` holds. Automation symbols
    are aligned on their centre line (the readout may lie on any side of the symbol), other blocks on their top left."""
    symbols = [case_symbol(f"{prefix}{i + 1}", kind, c, contracts[screen.view_of({"kind": kind, "params": c.params})])
               for i, c in enumerate(cases)]
    for s in symbols:
        if not s["bind"]:
            del s["bind"]
    boxes = [screen.symbol_box(s, contracts[screen.view_of(s)]) for s in symbols]   # (x, y, w, h) with the symbol at 0, 0
    contract = contracts[screen.view_of(symbols[0])]
    symbol = contract.get("anchor") == "symbol-centre" and kind != "readout"
    up = 0
    if symbol:
        left, right = max(-b[0] for b in boxes), max(b[0] + b[2] - 48 for b in boxes)
        up, down = max(-b[1] for b in boxes), max(b[1] + b[3] - 48 for b in boxes)
        cw, ch = 48 + 2 * max(left, right), up + 48 + down
    else:
        cw, ch = max(b[2] for b in boxes), max(b[3] for b in boxes)
    cw = max(cw + 8, 96, *(text_width(c.caption) for c in cases))
    cols = max(group, int(avail // cw))
    cols -= cols % group    # a group of cases (a pair side by side) never breaks across two rows
    block = Block()
    for i, (s, c, b) in enumerate(zip(symbols, cases, boxes)):
        r, k = divmod(i, cols)
        ox, oy = k * cw, r * (ch + CAPTION + 10)
        if symbol:
            s["x"], s["y"] = ox + cw / 2 - 24, oy + up
        else:
            s["x"], s["y"] = ox + (cw - b[2]) / 2 - b[0], oy - b[1]
        block.add("symbols", s)
        block.add("labels", label(f"{s['id']}_c", c.caption, ox, oy + ch + 2, cw))
        block.w, block.h = max(block.w, ox + cw), oy + ch + CAPTION + 10
    return block


def kind_block(kind: str, contracts: dict, prof: dict) -> Block:
    view = screen.view_of({"kind": kind})
    cases = kind_cases(kind, contracts[view], prof)
    return grid(f"S_{kind.replace('-', '_')}_", kind, cases, contracts)


def module_only_cases(kind: str, contract: dict) -> list[Case]:
    """The cases of a module-only kind, derived from its contract (`screen.module_contract`, the module's own schema): the
    state both ways, each other value of `variant`, `orientation` and `readoutPosition` the component lists, each alert
    level, the badges, and the identifier and status hidden. A kind needs no case list of its own."""
    schema = json.loads(screen.MODULE_COMPONENTS.read_text(encoding="utf-8"))[screen.MODULE_ONLY[kind]]["props"]
    if contract.get("anchor") == "box":   # a glyph (`screen.module_geometry`): only the component's own properties
        return glyph_cases(schema, contract)
    base = {"hasTag": True, "tag": ident_of(kind)}
    out = [Case("off", {**base, "on": False}), Case("on", {**base, "on": True})]
    for param in ("variant", "orientation", "readoutPosition"):
        values = schema.get(param, {}).get("enum", [])
        out += [Case(f"{param} {v}", {**base, "on": True, param: v}) for v in values if v != contract["params"].get(param)]
    out += [Case(f"alert {v}", {**base, "on": True, "alert": True, "alertFrameStatus": v, "alertFrameMode": "unacked-active"})
            for v in schema.get("alertFrameStatus", {}).get("enum", [])]
    out += [Case("badges", {**base, "on": True, "badgeControl": "manual", "badgeInterlock": "interlock",
                            "badgeCommandLocked": BADGE_LOCKED}),
            Case("no ID tag", {**base, "on": True, "hasTag": False}),
            Case("status hidden", {**base, "on": True, "showStatus": False})]
    return [c for c in out if all(k in contract["params"] for k in c.params)]


# The values a glyph's number properties are shown at: the element draws them as a percentage of travel (the pinned
# `dist/` source of the valve icons divides by 100) or of a level (the indicators), so mid travel and full travel show the
# drawing change. A number whose scale is not a percentage has its own pair (the readout's digit count is a width).
GLYPH_NUMBERS = (50, 100)
GLYPH_NUMBER_VALUES = {"numberOfDigits": (1, 6),
                       # the gauges' scale and their deadbands (B7): the first value is the element's own default
                       "maxValue": (100, 200), "minValue": (0, -50), "autoAtSetpointDeadband": (2, 5),
                       "setpointAtZeroDeadband": (0.5, 1), "fractionDigits": (0, 2),
                       # the selected position of the hydraulic valves (B8): a zero-based index, the first is the element's own default
                       "selectedPosition": (1, 0, 2),
                       # the transmitter button's reserved integer digits (B8)
                       "maxDigits": (0, 4)}
# The samples of a trend graph (the pinned indicators draw `data` as a polyline over the bar's rectangle) and the text a
# free string property is shown with, where a glyph has one (the readout's unit).
GLYPH_SERIES = [20, 35, 30, 55, 70, 60, 85]
GLYPH_TEXT = {"unit": "kn"}
# The nullable numbers a glyph shows live and so states at the values of `GLYPH_NUMBERS` (B8: the transmitter button's three
# segments, which draw dashes while empty). A nullable number outside this set (a gauge's setpoint) is left unstated.
GLYPH_NULLABLE = ("value", "adviceValue", "setpointValue")
# A companion a value of an enumeration needs to show anything: the tag variant of the transmitter button is its label.
GLYPH_COMPANION = {("variant", "tag"): {"label": "TT"}}


def glyph_cases(schema: dict, contract: dict) -> list[Case]:
    """The cases of a glyph, table driven from its component's schema: the defaults, each value of each enumerated
    property (the module's `componentSize` is no attribute of the element and is left out), each number at the values of
    `GLYPH_NUMBERS`, each boolean against its default, and a text for a property of `GLYPH_TEXT`. Every case but the
    default and the numbers' own carries the numbers at their first value, so that a flag which changes only what an
    opening looks like (orientation, a second opening) or a level drawn in another scheme shows. A case that sets the
    value `trend` also carries `GLYPH_SERIES` for each array of numbers. A glyph has no tag, readout or alert frame, so
    none of those is stated."""
    props = {k: p for k, p in schema.items() if k not in ("positioning", "componentSize")}
    default = {k: p["default"] for k, p in props.items()}
    numbers = {k: GLYPH_NUMBER_VALUES.get(k, GLYPH_NUMBERS) for k, p in props.items()
               if p["type"] == "number" or (p["type"] == ["number", "null"] and k in GLYPH_NULLABLE)}
    series = [k for k, p in props.items() if p["type"] == "array" and p.get("items", {}).get("type") == "number"]
    mid = {k: v[0] for k, v in numbers.items()}
    out = [Case("default", {})]
    for k, p in props.items():
        if "enum" in p:
            out += [Case(f"{k} {v}", {**mid, k: v, **({a: GLYPH_SERIES for a in series} if v == "trend" else {}),
                                      **GLYPH_COMPANION.get((k, v), {})})
                    for v in p["enum"]]
        elif k in numbers:
            out += [Case(f"{k} {v}", {k: v}) for v in numbers[k]]
        elif p["type"] == "boolean":
            out.append(Case(k if not default[k] else f"not {k}", {**mid, k: not default[k]}))
        elif p["type"] == "string" and k in GLYPH_TEXT:
            out.append(Case(f"{k} {GLYPH_TEXT[k]}", {**mid, k: GLYPH_TEXT[k]}))
    return [c for c in out if all(k in contract["params"] for k in c.params)]


def module_only_block(kind: str, contracts: dict) -> Block:
    """One kind of `screen.MODULE_ONLY` as a grid of its cases."""
    return grid(f"S_{kind.replace('-', '_')}_", kind, module_only_cases(kind, contracts[screen.view_of({"kind": kind})]), contracts)


def genset_block() -> Block:
    """The generator set in boxes of several sizes: it fits the box it is given (item 11)."""
    sizes = [(240, 150, False), (240, 150, True), (320, 200, True), (180, 112, True), (440, 275, True)]
    block, x = Block(), 0
    for i, (w, h, on) in enumerate(sizes):
        sid = f"S_genset_{i + 1}"
        block.add("symbols", {"id": sid, "kind": "generator", "x": x, "y": 0, "w": w, "h": h,
                              "params": {"picture": "genset", "on": on, "hasTag": True, "tag": "GEN-1"}})
        block.add("labels", label(f"{sid}_c", f"{w} by {h}, {'running' if on else 'stopped'}", x, h + 2, max(w, 150)))
        x += max(w, 150) + GAP
        block.w, block.h = x - GAP, max(block.h, h + CAPTION + 10)
    return block


def pairs(kind: str, cases: list[Case]) -> list[Case]:
    """Each case twice, side by side (L5, contract 3.2): as the project draws it (the module's component under the module
    rendering) and forced onto the library's view (`render` `view`), so that the two can be compared at once. A case with
    a value the module's component cannot take (`module_value_ok`: the status `critical`) is the library's view in both
    cells, the first said so."""
    out = []
    for c in cases:
        module = all(module_value_ok(kind, c.params, k) for k in c.params)
        out.append(Case(f"{c.caption}: module" if module else f"{c.caption}: library only", dict(c.params), dict(c.bind),
                        extra={} if module else {"render": "view"}))
        out.append(Case(f"{c.caption}: view", dict(c.params), dict(c.bind), extra={"render": "view"}))
    return out


def notification_block(contracts: dict, prof: dict) -> Block:
    """The alarm frame and flap of every status in every mode, drawn statically on a pump, each beside the same symbol on
    the library's view: a symbol that states `alert`, `alertFrameStatus` and `alertFrameMode` follows no alarm
    (`screen.derived_alert`). `critical` is the library's alone, so both of its cells are the library's view (the
    module has no such status); the lamp draws no frame (L5)."""
    short = {"acked-active": "acked", "unacked-active": "unacked", "unacked-rectified": "cleared"}
    cases = [Case(f"{st} {short[m]}", {"hasTag": False, "alert": True, "alertFrameStatus": st,
                                       "alertFrameMode": m, "on": True})
             for st in ALERT_STATUS for m in ALERT_MODE]
    return grid("N_pump_", "pump", pairs("pump", cases), contracts, group=2)


def marks_block(contracts: dict, prof: dict) -> Block:
    """The badges and marks a pump states: control, interlock, command locked, duty, out of service, progress, activated,
    each beside the same symbol on the library's view. The module has no duty mark and no out of service greying, so
    those two cells are the library's view twice."""
    base = {"on": True, "hasTag": True, "tag": "P-101"}
    cases = ([Case(f"badge {b}", {**base, "badgeControl": b}) for b in library.CONTROL_BADGES]
             + [Case(f"badge {b}", {**base, "badgeInterlock": b}) for b in BADGE_INTERLOCK]
             + [Case("command locked", {**base, "badgeCommandLocked": BADGE_LOCKED}),
                Case("duty", {**base, "badgeDuty": True}), Case("out of service", {**base, "outOfService": True}),
                Case("progress", {**base, "progress": True}), Case("activated", {**base, "activated": True}),
                Case("duty and OOS", {**base, "badgeDuty": True, "outOfService": True})])
    return grid("B_pump_", "pump", pairs("pump", cases), contracts, group=2)


def lamp_block() -> tuple[Block, list[str]]:
    """The indicator coloured by state (L5, contract 3.1): a Boolean lamp, a three-state lamp (0 off, 1 on, 2 alarm), a
    string-state lamp and a lamp painted by CSS colours, each on a tag of its own, and the buttons that write the tags
    (a pulse holds a tag true for a minute, and the state follows it)."""
    block, pulses, cw = Block(), [], 220
    for i, (ident, spec) in enumerate(LAMPS.items()):
        x = i * cw
        sym = {"id": ident, "kind": "indicator", "x": x + cw / 2 - 24, "y": 0, "w": 48, "h": 48,
               "params": {"hasTag": True, "tag": ident.replace("L_", "")[:8]},
               "bind": {"state": f"{FOLDER}/lamps/{ident}/state"}}
        if spec["states"]:
            sym["states"] = copy.deepcopy(spec["states"])
        block.add("symbols", sym)
        block.add("labels", label(f"{ident}_c", spec["caption"], x, 66, cw))
        for k, (member_, caption) in enumerate(spec["buttons"]):
            tag = f"{FOLDER}/lamps/{ident}/{member_}"
            pulses.append(tag)
            block.add("buttons", button(f"{ident}_{member_}", caption, x + 6, 90 + 36 * k, cw - 12,
                                        {"type": "pulse", "tag": tag, "ms": PULSE_MS,
                                         "confirm": f"{caption} for a minute?"}))
    note = ("A lamp draws no status row and no frame: its colour is its state. Each button holds one test tag true for a "
            "minute; the lamp returns to its first state after it.")
    block.add("labels", label("L_help", note, 0, 90 + 36 * 2 + 6, len(LAMPS) * cw, 16, style="body", align="left"))
    block.w, block.h = len(LAMPS) * cw, 90 + 36 * 2 + 28
    return block, pulses


def medium_block() -> Block:
    """One pipe for each medium and one for each size: flowing pipes (a source arrow to a sink arrow), which the Color
    toggle of the toolbar paints in their medium; the neutral pipe keeps its colour."""
    block = Block()
    for i, medium in enumerate(screen.MEDIUM_VAR):
        x, y = (0 if i < 5 else 620), (i % 5) * 34 + 14
        key = medium.replace("-", "_")
        block.add("labels", label(f"M_{key}_l", medium, x, y - 8, 110, 16, align="left"))
        block.add("pipes", {"id": f"M_{key}", "medium": medium, "size": "medium",
                            "from": {"x": x + 120, "y": y, "end": "arrow-in"},
                            "to": {"x": x + 480, "y": y, "end": "arrow-out"}})
    for j, size in enumerate(("small", "medium", "large", "xl")):
        y = 5 * 34 + 28 + j * 30
        block.add("labels", label(f"M_size_{size}_l", f"size {size}", 0, y - 8, 110, 16, align="left"))
        block.add("pipes", {"id": f"M_size_{size}", "medium": "fresh-water", "size": size,
                            "from": {"x": 120, "y": y, "end": "arrow-in"}, "to": {"x": 600, "y": y, "end": "arrow-out"}})
    block.w, block.h = 1100, 5 * 34 + 28 + 4 * 30
    return block


def alarm_block(specs: dict) -> tuple[Block, list[str]]:
    """A lamp for each alarm priority, its own alarm, and the buttons that raise them for a minute."""
    block, pulses, cw = Block(), [], 150
    for i, prio in enumerate(alarms.PRIORITIES):
        ident = f"ALM_{prio.upper()}"
        x = i * cw
        # a switch symbol shows the alarm's frame (a lamp draws none, L5); the device is still an indicator
        block.add("symbols", {"id": ident, "kind": "switch", "x": x + cw / 2 - 24, "y": 0, "w": 48, "h": 48,
                              "device": f"{FOLDER}/{ident}", "label": specs[ident]["label"],
                              "params": {"hasTag": True, "tag": prio[:4].upper(), "deviceKind": "indicator"},
                              "bind": {"on": f"{FOLDER}/{ident}/state"}})
        block.add("labels", label(f"{ident}_c", prio, x, 70, cw))
        tag = f"{FOLDER}/{ident}/raise"
        pulses.append(tag)
        block.add("buttons", button(f"{ident}_raise", f"Raise {prio}", x + 8, 94, cw - 16,
                                    {"type": "pulse", "tag": tag, "ms": PULSE_MS,
                                     "confirm": f"Raise the {prio} test alarm for a minute?"}))
    pulses.append(RAISE_ALL)
    block.add("buttons", button("ALM_ALL_raise", "Raise all five", 5 * cw + 8, 94, 160,
                                {"type": "pulse", "tag": RAISE_ALL, "ms": PULSE_MS,
                                 "confirm": "Raise all five test alarms for a minute?"}))
    steps = ["Raise: the frame flashes (active, unacknowledged). Acknowledge on the faceplate Alarms tab or on the alert banner:",
             "the frame is steady (active, acknowledged). Let the minute pass without acknowledging: the frame turns dashed",
             "(cleared, unacknowledged). Acknowledge it to clear the symbol. Each lamp has one alarm, of one priority."]
    for i, text in enumerate(steps):
        block.add("labels", label(f"ALM_help{i + 1}", text, 0, 136 + 18 * i, 1000, 16, style="body", align="left"))
    # the panel of the test alarms (L5, contract 3.6): the list with Ack selected and Ack all, beside the buttons
    px = max(5 * cw + 176, 1000) + 12
    block.add("alarmPanels", {"id": "ALM_panel", "x": px, "y": 0, "w": 420, "h": 380, "sources": [FOLDER]})
    block.add("labels", label("ALM_help4", "Ack selected and Ack all: the list's own buttons.", 0, 136 + 18 * 3, 1000, 16,
                              style="body", align="left"))
    block.w, block.h = px + 420, 380
    return block, pulses


def device_bind(ident: str, kind: str, spec: dict, contract: dict) -> dict:
    """A test symbol's bindings: each parameter the kind's rule (`screen.bind_rule`) binds to a member the device
    lists. Only the state parameter the contract names binds the state (the rule names `on` and `open` for both)."""
    bind = {}
    for param, m in screen.bind_rule(spec["kind"]).items():
        if param in contract["params"] and m in spec["members"] and (
                param not in ("on", "open") or param == contract.get("state")):
            bind[param] = f"{FOLDER}/{ident}/{m}"
    if kind == "tank":
        bind["value"] = f"{FOLDER}/{ident}/level"
    return bind


def device_symbol(sid: str, ident: str, kind: str, contracts: dict, specs: dict, *, x: float, y: float,
                  params: dict | None = None) -> dict:
    """The symbol of a test device: bound to its faceplate members, opening its faceplate. `sid` is the symbol's own id
    (the device may have two symbols); a block kind has the contract's size."""
    params = dict(params or {})
    contract = contracts[screen.view_of({"kind": kind, "params": params})]
    if contract.get("anchor") == "symbol-centre" and kind != "readout":
        w = h = 48
    else:
        w, h = library.block_size(contract, params)
    if "size" in params and kind == "generator":
        w, h = params.pop("size")
    return {"id": sid, "kind": kind, "x": x, "y": y, "w": w, "h": h, "device": f"{FOLDER}/{ident}",
            "label": specs[ident]["label"], "params": params,
            "bind": device_bind(ident, kind, specs[ident], contract)}


DEVICE_ROW = [("motor", "TB_MOTOR", {"hasSpeed": True}), ("fan", "TB_FAN", {"hasSpeed": True}),
              ("analogvalve", "TB_AVALVE", {"value": 50}), ("damper", "TB_DAMPER", {}),
              ("indicator", "TB_IND", {}), ("generator", "TB_GEN", {"picture": "symbol"}),
              ("controller", "TB_CTRL", {"hasSetpoint": True, "hasOutput": True}),
              ("sequence", "TB_SEQ", {"hasStep": True})]


def devices_block(specs: dict, contracts: dict) -> tuple[Block, list[str]]:
    """A device of each kind, with the pump and the valve in a flowing line, and the buttons that open each faceplate on
    its Alarms tab. The symbols open the faceplates in the project's mode (dock; the pin floats it)."""
    block, pulses = Block(), []
    fy = 40   # the row of automation symbols
    block.add("symbols", device_symbol("TB_PUMP", "TB_PUMP", "pump", contracts, specs, x=140, y=fy,
                                       params={"hasTag": True, "tag": "P-001", "hasSpeed": True}))
    block.add("symbols", device_symbol("TB_VALVE", "TB_VALVE", "valve", contracts, specs, x=300, y=fy,
                                       params={"hasTag": True, "tag": "XV-001"}))
    block.add("pipes", {"id": "F_in", "medium": "fresh-water", "from": {"x": 20, "y": fy + 24, "end": "arrow-in"},
                        "to": {"ref": "TB_PUMP", "side": "left"}})
    block.add("pipes", {"id": "F_mid", "medium": "fresh-water", "from": {"ref": "TB_PUMP", "side": "right"},
                        "to": {"ref": "TB_VALVE", "side": "left"}})
    block.add("pipes", {"id": "F_out", "medium": "fresh-water", "from": {"ref": "TB_VALVE", "side": "right"},
                        "to": {"x": 440, "y": fy + 24, "end": "arrow-out"}})
    block.add("labels", label("F_c", "Start the pump and open the valve on their faceplates: the pipes fill",
                              0, fy + 100, 460, 16, align="left"))
    x = 500
    for kind, ident, extra in DEVICE_ROW:
        sym = device_symbol(ident, ident, kind, contracts, specs, x=x, y=fy,
                            params={"hasTag": True, "tag": specs[ident]["title"].replace("TB-", "")[:8], **extra})
        box = sym["w"] != 48
        if not box:
            sym["x"] += 24
        block.add("symbols", sym)
        block.add("labels", label(f"{ident}_c", kind, x, fy + (sym["h"] + 8 if box else 104), max(sym["w"], 96) + 8))
        x += (max(sym["w"], 96) + 24) if box else 110
    y2 = 220   # the tank, the instruments and the generator set
    block.add("symbols", device_symbol("TB_TANK", "TB_TANK", "tank", contracts, specs, x=0, y=y2,
                                       params={"tag": "T-001", "value": 62}))
    block.add("labels", label("TB_TANK_c", "tank", 0, y2 + 218, 168))
    block.add("symbols", device_symbol("TB_READOUT", "TB_READOUT", "readout", contracts, specs, x=200, y=y2 + 8,
                                       params={"hasTag": True, "tag": "PT-001", "unit": "bar"}))
    block.add("labels", label("TB_READOUT_c", "readout", 200, y2 + 52, 96))
    block.add("symbols", device_symbol("TB_FIELD", "TB_FIELD", "instrument-field", contracts, specs, x=200, y=y2 + 80,
                                       params={"label": "Temp", "unit": "degC", "format": "#,##0.0"}))
    block.add("labels", label("TB_FIELD_c", "instrument field", 200, y2 + 146, 96))
    gen = device_symbol("TB_GEN_SET", "TB_GEN", "generator", contracts, specs, x=330, y=y2,
                        params={"picture": "genset", "hasTag": True, "tag": "GEN-1"})
    gen["w"], gen["h"] = 300, 188
    block.add("symbols", gen)
    block.add("labels", label("TB_GEN_SET_c", "generator set (the device of the symbol above)", 330, y2 + 190, 300))
    bx = 660   # the faceplate buttons and the pulses
    block.add("labels", label("TB_btn_head", "Open a faceplate on its Alarms tab", bx, y2 - 2, 460, 16, style="body",
                              align="left"))
    for i, ident in enumerate(("TB_PUMP", "TB_MOTOR", "TB_FAN", "TB_VALVE", "TB_AVALVE", "TB_DAMPER", "TB_TANK",
                               "TB_READOUT", "TB_FIELD", "TB_CTRL", "TB_IND", "TB_SEQ", "TB_GEN")):
        r, k = divmod(i, 4)
        block.add("buttons", button(f"TB_open_{ident}", specs[ident]["title"], bx + k * 150, y2 + 20 + r * 38, 140,
                                    {"type": "faceplate", "device": f"{FOLDER}/{ident}", "tab": "alarms"}))
    py = y2 + 20 + 4 * 38 + 12
    for i, (ident, caption, member_) in enumerate((("TB_PUMP", "Set pump fault", "fault"),
                                                   ("TB_IND", "Set input TB-IND", "state"))):
        tag = f"{FOLDER}/{ident}/{member_}"
        pulses.append(tag)
        block.add("buttons", button(f"TB_pulse_{ident}", caption, bx + i * 230, py, 220,
                                    {"type": "pulse", "tag": tag, "ms": PULSE_MS, "confirm": f"{caption} for a minute?"}))
    # a plain motor that opens a device's faceplate (L5, contract 3.3): the test pump's, and a motor with a state only
    pm = {"id": "TB_PLAIN_PUMP", "kind": "motor", "x": 140, "y": y2 + 250, "w": 48, "h": 48,
          "faceplate": f"{FOLDER}/TB_PUMP", "label": specs["TB_PUMP"]["label"],
          "params": {"hasTag": True, "tag": "PLAIN-P"}, "bind": {"on": f"{FOLDER}/TB_PUMP/state"}}   # reads the pump's state
    block.add("symbols", pm)
    block.add("labels", label("TB_PLAIN_PUMP_c", "plain motor: opens the test pump's faceplate", 40, y2 + 302, 248, 16))
    ms = {"id": "TB_PLAIN_MOTOR", "kind": "motor", "x": 360, "y": y2 + 250, "w": 48, "h": 48,
          "faceplate": f"{FOLDER}/TB_MSTATE", "label": specs["TB_MSTATE"]["label"],
          "params": {"hasTag": True, "tag": "PLAIN-M"}, "bind": {"on": f"{FOLDER}/TB_MSTATE/state"}}
    block.add("symbols", ms)
    block.add("labels", label("TB_PLAIN_MOTOR_c", "plain motor: opens a faceplate that shows its state only", 280, y2 + 302, 208, 16))
    tag = f"{FOLDER}/TB_MSTATE/state"
    pulses.append(tag)
    block.add("buttons", button("TB_pulse_TB_MSTATE", "Set the motor's state", 280, y2 + 326, 208,
                                {"type": "pulse", "tag": tag, "ms": PULSE_MS, "confirm": "Set the motor's state for a minute?"}))
    block.add("labels", label("TB_modes_1", "Pump and motor modes: Program, Operator, Maintenance, Local. Take control, Release and "
                                            "Maintenance are on the faceplate;", bx, py + 40, 840, 16, style="body", align="left"))
    block.add("labels", label("TB_modes_2", "a command a mode does not allow is refused with its reason.",
                              bx, py + 58, 840, 16, style="body", align="left"))
    # the module's command button (spike T0 wrap W3, wiki page 12 section 17.12): the same confirmed pulse of the library
    # (`page_pulse`, write path W18) on the test generator's Start command, which its state tag latches; drawn as the
    # module's `cadre.ob.button` under `--render module` and as the library's button otherwise
    tag = f"{FOLDER}/TB_GEN/cmdStart"
    pulses.append(tag)
    block.add("buttons", {**button("TB_press_GEN_start", "Start generator", bx, y2 + 270, 220,
                                   {"type": "pulse", "tag": tag, "ms": PULSE_MS,
                                    "confirm": "Start the test generator?"}, h=56), "render": "module"})
    block.add("labels", label("TB_press_GEN_start_c", "OB button: Start generator pulses TB_GEN/cmdStart for a minute; the "
                                                      "generator then runs.", bx + 230, y2 + 288, 600, 16,
                              style="body", align="left"))
    block.w, block.h = 1500, y2 + 365
    return block, pulses


# ---------------------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------------------
SYMBOL_KINDS = ("pump", "motor", "fan", "valve", "analogvalve", "damper", "filter", "switch", "indicator")
BLOCK_KINDS = ("tank", "readout", "instrument-field", "controller", "sequence")
PAD = 12


def about_block(prof: dict, contracts: dict) -> Block:
    kinds = sorted(prof["kinds"])
    lines = ["Every library component with the features to test. The page is generated from the library catalogue "
             "(library/contracts.json and library/profile.json) by screen.py --component-test.",
             f"Kinds shown: {', '.join(kinds)}, and the generator set. Toolbar: Color paints the pipes in their medium, "
             "ID-tag shows the identifiers, Readout shows the status words (and mutes them when off).",
             f"Test devices run on memory tags in {FOLDER} under the project's tag root; page buttons write only those tags. "
             "Click a symbol to open its faceplate in the dock; the pin on the faceplate floats it."]
    block = Block()
    for i, text in enumerate(lines):
        block.add("labels", label(f"About_{i + 1}", text, 0, i * 20, WIDTH - 2 * MARGIN - 2 * PAD, 16, style="body",
                                  align="left"))
    block.w, block.h = WIDTH - 2 * MARGIN - 2 * PAD, len(lines) * 20
    return block


def pack(sections: list[tuple[str, str, Block]]) -> tuple[list[dict], dict[str, list], float]:
    """Place the blocks in sections left to right, wrapping at the page width: the section boxes, the items of
    each descriptor array in page coordinates, and the page height."""
    boxes, arrays = [], {}
    x, y, row_h = MARGIN, MARGIN, 0
    for ident, title, block in sections:
        w, h = block.w + 2 * PAD, block.h + HEAD + PAD
        if x > MARGIN and x + w > WIDTH - MARGIN:
            x, y, row_h = MARGIN, y + row_h + GAP, 0
        boxes.append({"id": ident, "x": x, "y": y, "w": w, "h": h, "label": title})
        for array, item in block.items:
            arrays.setdefault(array, []).append(shifted(item, x + PAD, y + HEAD))
        x, row_h = x + w + GAP, max(row_h, h)
    return boxes, arrays, y + row_h + MARGIN


def galleryize(symbols: list[dict]) -> dict[str, dict]:
    """Move the state and mark parameters of every gallery symbol (the static grids') from its params to its `bind`, on
    a memory tag `<FOLDER>/gallery/<symbol>/<param>` that starts at the case's value (L5, contract 3.4). Returns
    {symbol id: {param: starting value}}; the symbols are changed in place."""
    out: dict[str, dict] = {}
    for s in symbols:
        if not s["id"].startswith(GALLERY_PREFIXES) or s.get("device") or s.get("faceplate"):
            continue
        moved = {k: v for k, v in s.get("params", {}).items() if k in GALLERY_PARAMS and gallery_tag(v) is not None}
        for k in moved:
            del s["params"][k]
            s.setdefault("bind", {})[k] = f"{FOLDER}/gallery/{s['id']}/{k}"
        if moved:
            out[s["id"]] = moved
    return out


def build(contracts: dict, prof: dict, tag_root: str, *, node: str = "Component test", render: str = "stock") -> Bench:
    """The component test page, its test devices and its tags for a project whose tags sit under `tag_root`
    (for example `[default]cadre_hmi_eng02_asm`). Everything comes from `contracts` (library/contracts.json) and
    `prof` (library/profile.json)."""
    root = tag_root.split("]", 1)[-1]
    specs = device_specs(tag_root, node)
    sections: list[tuple[str, str, Block]] = [("About", "About this page", about_block(prof, contracts))]
    lamps, lamp_pulses = lamp_block()
    sections.append(("Lamps", "Indicator: colour by state (the lamp has no status row and no frame)", lamps))
    sections.append(("Notification", "Notification: alarm frame and flap, every status and mode, module beside view",
                     notification_block(contracts, prof)))
    sections.append(("Marks", "Badges and marks (pump), module beside view", marks_block(contracts, prof)))
    for kind in SYMBOL_KINDS + BLOCK_KINDS:
        if kind in prof["kinds"]:
            sections.append((f"Kind_{kind.replace('-', '_')}", f"{kind.capitalize()}  ({screen.view_of({'kind': kind})})",
                             kind_block(kind, contracts, prof)))
    gen = kind_block("generator", contracts, prof) if "generator" in prof["kinds"] else None
    if gen is not None:
        sections.append(("Kind_generator", f"Generator  ({screen.view_of({'kind': 'generator'})})", gen))
        sections.append(("Kind_genset", f"Generator set  ({screen.GENSET_VIEW}) in boxes of several sizes", genset_block()))
    if render == "module" and screen.MODULE_ONLY:   # the kinds with no library view: only the module draws them
        only = Block()
        for kind in screen.MODULE_ONLY:
            only.extend(module_only_block(kind, contracts), 0, only.h)
        sections.append(("ModuleOnly", "Module only: " + ", ".join(screen.MODULE_ONLY), only))
    sections.append(("Media", "Colour by medium (toolbar: Color)", medium_block()))
    alarm_part, alarm_pulses = alarm_block(specs)
    sections.append(("Alarms", "Test alarms: one lamp for each priority (Critical, High, Medium, Low, Diagnostic)", alarm_part))
    dev_part, dev_pulses = devices_block(specs, contracts)
    sections.append(("Devices", "Test devices: faceplates (dock and floating), modes, commands, flow", dev_part))
    boxes, arrays, height = pack(sections)
    gallery = galleryize(arrays.get("symbols", []))
    desc = {"schema": prof.get("descriptor", "cadre-hmi-screen/1"),
            "screen": {**PAGE, "width": WIDTH, "height": math.ceil(height)},
            "tagRoot": tag_root, "tagModel": "external", "toolbar": True, "showTags": True, "sections": boxes}
    desc.update({k: v for k, v in arrays.items() if v})
    pulses = lamp_pulses + alarm_pulses + dev_pulses
    n_tags = sum(len(p) for p in gallery.values())
    return Bench(descriptor=desc, devices=model_entries(specs), tags=tag_folder(specs, gallery), pulse_tags=pulses,
                 gallery=gallery,
                 notes=[f"{root}/{FOLDER}: {len(specs)} test devices on memory tags; {len(pulses)} pulse tags; "
                        f"{n_tags} gallery tags of {len(gallery)} symbols"])


# ---------------------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------------------
def check(desc: dict, contracts: dict) -> list[str]:
    """Problems of the page against the catalogue it came from: a parameter a contract lacks, a repeated id, a symbol
    of a kind the library lacks. Empty for a page the generator built from the catalogue it was given."""
    out, seen = [], set()
    for array in ("sections", "labels", "symbols", "pipes", "buttons", "alarmPanels"):
        for item in desc.get(array, []):
            if item["id"] in seen:
                out.append(f"{array}: the id {item['id']!r} is used twice")
            seen.add(item["id"])
    for s in desc.get("symbols", []):
        view = screen.view_of(s)
        if view not in contracts:
            out.append(f"{s['id']}: no view for kind {s['kind']!r}")
            continue
        for k in list(s.get("params", {})) + [b for b in s.get("bind", {}) if not (b == "state" and view.endswith("Indicator"))]:
            if k not in contracts[view]["params"]:
                out.append(f"{s['id']}: parameter {k!r} is not in the {view} contract")
    return out


def kinds_drawn(desc: dict) -> set[str]:
    """The kinds the page draws (the generator set counted as `genset`)."""
    return {("genset" if screen.view_of(s) == screen.GENSET_VIEW else s["kind"].lower()) for s in desc.get("symbols", [])}
