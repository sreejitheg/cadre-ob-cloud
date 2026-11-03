"""Screen generator: a screen descriptor becomes a child project page over the parent library.

A descriptor (schema `schemas/screen-descriptor.schema.json`, wiki page 06) names a route,
a layout (`diagram` or `cards`), and the content: sections, symbols with static parameters and
tag bindings, junctions and pipes, or cards with items. The generator:

  1. checks every symbol against its library contract (unknown kind or parameter is an error,
     never silently dropped; a kind the library lacks is drawn as a visible, counted gap box);
  2. resolves tag bindings against the descriptor's tag root (never invents a path: a binding
     names a member, and `--tags` writes exactly the members bound);
  3. routes the pipes and compiles one flow expression per pipe (diagram.py);
  4. emits the view, the page route, the navigation entry and the test tag document.

A device model (schema `schemas/devices.schema.json`, `--devices-file`) may stand beside the
descriptors: it names each device's kind, the members its tag folder carries with their types and
whether they may be written, its pulse commands with the captions of their buttons, the source tags
its alarms stay on, and the members historised. The
device index then carries what the faceplates and the checked writes need of it (wiki page 08
section 3.1).

Usage (PowerShell, from the repository root):
    python tools/hmi/screen.py --project cadre_hmi_demo --descriptor <a.json> [--descriptor <b.json>]
        [--app-name Demo] [--out build] [--tags-file <tags.json>] [--devices-file <devices.json>] [--deploy]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import pv, diagram, framework, library, scripts, navigation, devices_asm, parent as par, parts  # noqa: E402
    from hmi.framework import root_classes, search_panel  # noqa: E402
    from hmi.library import svg, icon_svg, block_size, identifier_width, identifier_shown, STATIC_TILE  # noqa: E402
else:
    from . import pv, diagram, framework, library, scripts, navigation, devices_asm, parent as par, parts
    from .framework import root_classes, search_panel
    from .library import svg, icon_svg, block_size, identifier_width, identifier_shown, STATIC_TILE

ROOT = Path(__file__).resolve().parents[2]
KIND_VIEW = {"pump": "Automation/Pump", "motor": "Automation/Motor", "fan": "Automation/Fan",
             "valve": "Automation/Valve", "analogvalve": "Automation/AnalogValve",
             "damper": "Automation/Damper", "filter": "Automation/Filter", "switch": "Automation/Switch",
             "tank": "Automation/Tank", "readout": "Automation/Readout",
             "instrument-field": "Instrument/Field", "controller": "Instrument/Controller",
             "indicator": "Automation/Indicator", "sequence": "Instrument/Sequence",
             "generator": "Automation/Generator"}
# A generator with `params.picture = "genset"` is drawn as the larger vector generator set (COB-158, gap GG-01)
GENSET_VIEW = "Automation/GeneratorSet"


def view_of(sym: dict) -> str:
    """The library view that draws a descriptor symbol: its kind's (KIND_VIEW), or for a generator that asks for
    `picture` `genset` the generator set. Empty for a kind the library lacks."""
    kind = sym["kind"].lower()
    if kind == "generator" and (sym.get("params") or {}).get("picture") == "genset":
        return GENSET_VIEW
    if kind in MODULE_ONLY:
        return MODULE_VIEW + kind
    return KIND_VIEW.get(kind, "")

READOUT_EXTENT = {"right": (64, 0), "left": (64, 0), "bottom": (24, 44), "top": (24, 44), "none": (0, 0)}


# Two boxes of a diagram overlap when they share more than this many px on both axes: the tolerance of
# gate G5 (`gates.g5_layout`), which the generator keeps when it widens an embed (`embed_limits`).
OVERLAP = 4


def readout_extent(sym: dict, contract: dict, limit: float | None = None) -> tuple[float, float]:
    """How far the embed of an automation symbol reaches beyond its 48 px symbol box, across and down,
    for the symbol's `readoutPosition`: `READOUT_EXTENT`, and across as much more as the symbol's
    identifier needs to be read in full (`library.identifier_width`). Beneath or above the symbol the
    readout is centred on it, so the embed is as wide as the identifier needs and never narrower than
    48 px plus the default; beside the symbol the readout itself is that wide. An identifier the symbol
    does not show (`hasTag` false) or that fits the default changes nothing, so a page whose identifiers
    fitted is built as before. `limit` is the most the identifier may add to the default (`embed_limits`:
    the room the next symbol leaves); the identifier then ends in an ellipsis."""
    params = sym.get("params", {})
    pos = params.get("readoutPosition", "bottom")
    ex, ey = READOUT_EXTENT.get(pos, (0, 0))
    tag = str(params.get("tag") or "")
    if pos not in READOUT_EXTENT or pos == "none" or not tag or params.get("hasTag") is False \
            or "identifier" not in contract:
        return ex, ey
    need = identifier_width(contract, len(tag))
    wide = max(ex, need) if pos in ("left", "right") else max(ex, need - 48)
    return (wide if limit is None else min(wide, ex + limit)), ey


def grown_box(sym: dict, contract: dict, limit: float | None = None) -> tuple[float, float, float, float]:
    """The embed of a block whose contract says `grows` (a readout): the box the descriptor gives, and
    where that is smaller than the block needs, the box grown about its centre, so that the readout
    stays on its line. The block needs the size its flags ask for (`library.block_size`, where they ask
    for more than the default size) and the width of the identifier it shows
    (`library.identifier_width`); `limit` is the most the identifier may add (`embed_limits`). A box
    that holds its block is returned as given, so a page whose readouts fitted is built as before."""
    x, y, w, h = sym["x"], sym["y"], sym["w"], sym["h"]
    params = sym.get("params", {})
    need = block_size(contract, params)
    w2, h2 = (max(w, need[0]), max(h, need[1])) if need != list(contract["size"]) else (w, h)
    tag = str(params.get(contract["identifier"]["param"]) or "") if "identifier" in contract else ""
    if tag and identifier_shown(contract, params):
        wide = max(w2, identifier_width(contract, len(tag)))
        w2 = wide if limit is None else min(wide, w2 + limit)
    if (w2, h2) == (w, h):
        return x, y, w, h
    return x + (w - w2) / 2, y + (h - h2) / 2, w2, h2
# The faceplate contract (wiki page 06 section 5): the members each faceplate reads, by device kind.
# Every member is optional on a device (a faceplate lists what the device carries); these are the
# members a generated tag model creates for a device of a build without tags, with their defaults. A
# device binds its faceplate members by these names (`bind_rule`, checked under G7).
_SWITCHED = {"state": ("Boolean", False), "cmd": ("Boolean", False), "mode": ("Int4", 0)}
_MOTORISED = {**_SWITCHED, "speed": ("Float8", 0.0), "speedSp": ("Float8", 80.0), "fault": ("Boolean", False)}
_INSTRUMENT = {"value": ("Float8", 0.0)}   # limits are optional: the faceplate lists those present
_CONTROLLER = {"value": ("Float8", 0.0), "sp": ("Float8", 0.0), "out": ("Float8", 0.0), "manual": ("Boolean", False),
               "manOut": ("Float8", 0.0), "gain": ("Float8", 1.0), "ti": ("Float8", 0.0), "td": ("Float8", 0.0)}
# A sequence (wiki page 13 section 9.7): the step number, its text (computed in the tag model), the
# pulse command that starts a cycle, and a fault.
_SEQUENCE = {"step": ("Int4", 0), "stepText": ("String", ""), "trigger": ("Boolean", False),
             "fault": ("Boolean", False)}
FACEPLATE_MEMBERS = {"pump": _MOTORISED, "motor": _MOTORISED, "fan": _MOTORISED,
                     "valve": _SWITCHED, "analogvalve": _SWITCHED, "damper": _SWITCHED,
                     "tank": {"level": ("Float8", 50.0), "hiLimit": ("Float8", 90.0), "loLimit": ("Float8", 10.0)},
                     "readout": _INSTRUMENT, "instrument-field": _INSTRUMENT, "instrument": _INSTRUMENT,
                     "controller": _CONTROLLER, "indicator": {"state": ("Boolean", False)},
                     "sequence": _SEQUENCE, "generator": devices_asm.GENERATOR_CORE}
# Members a device may also carry, which no generated model creates: the alarm limits, the maintenance
# members of `mnt/` (wiki page 13 section 9), a valve's fault, the members the tank tile reads.
_LIMITS = {m: "Float8" for m, _label in scripts.constant("LIMITS")}
# and the on-delay of each (F028): `<limit>Delay`, seconds
_LIMITS.update({m + scripts.constant("DELAY_SUFFIX"): "Float8" for m, _label in scripts.constant("LIMITS")})
_MAINTENANCE = {m: "Boolean" for m in scripts.constant("MEMBER_DEFAULTS") if m.startswith("mnt/")}
_VALVE = {"fault": "Boolean", **_MAINTENANCE}
_INSTRUMENT_OPTIONAL = {**_LIMITS, **devices_asm.INSTRUMENT_OPTIONAL}   # the limits, the flags and the range of the bar
OPTIONAL_MEMBERS = {"pump": _MAINTENANCE, "motor": _MAINTENANCE, "fan": _MAINTENANCE,
                    "valve": _VALVE, "analogvalve": _VALVE, "damper": _VALVE,
                    "tank": {**_LIMITS, "volume": "Float8", "capacity": "Float8", "trend": "String"},
                    "readout": _INSTRUMENT_OPTIONAL, "instrument-field": _INSTRUMENT_OPTIONAL,
                    "instrument": _INSTRUMENT_OPTIONAL,
                    "controller": _LIMITS, "indicator": _MAINTENANCE,
                    # the members of the asm faceplates of COB-158 (`devices_asm`)
                    "sequence": devices_asm.SEQUENCE_OPTIONAL,
                    "generator": {**devices_asm.GENERATOR_OPTIONAL, **_MAINTENANCE}}
# the controller acknowledgement bit, which any device with alarms may carry (F049, `cadre.hmi.ACK_MEMBER`)
for _kind in list(FACEPLATE_MEMBERS):
    OPTIONAL_MEMBERS[_kind] = {**OPTIONAL_MEMBERS.get(_kind, {}), scripts.constant("ACK_MEMBER"): "Boolean"}
# a tank's `value` may be its volume: the check applies only where the member is in the kind's contract
FACEPLATE_BIND = {"on": "state", "open": "state", "speed": "speed", "value": "value"}
# the controller's block binds three more of its members; the sequence's block binds its step and its text
KIND_BIND = {"controller": {"setpoint": "sp", "output": "out", "manual": "manual"},
             "sequence": {"text": "stepText", "step": "step"}}
# The members a session pulses (`cadre.hmi.pulse`, write path W18), in the table of the code that writes them.
PULSE_MEMBERS = tuple(scripts.constant("FUNCTION_MEMBERS")[scripts.constant("PULSE_PATH")])


def known_members(kind: str) -> dict[str, str]:
    """Every member the library knows for a device kind, with its type."""
    return {**{m: t for m, (t, _default) in FACEPLATE_MEMBERS.get(kind, {}).items()},
            **OPTIONAL_MEMBERS.get(kind, {})}


def bind_rule(kind: str) -> dict[str, str]:
    """Symbol parameter to faceplate member, for a device of `kind`."""
    return {**FACEPLATE_BIND, **KIND_BIND.get(kind, {})}


def pulse_members(kind: str) -> list[str]:
    """The pulse members the library knows for a device kind: each gets a button on its faceplate."""
    return [m for m in PULSE_MEMBERS if m in known_members(kind)]


# Module-only kinds: a descriptor kind that has no library view, only a component of the module. The table maps the kind
# to the component id; everything else is derived. The contract is `module_contract` (from `module/components.json`),
# its pseudo view path `Module/<kind>` (`view_of`), the symbol is drawn by `embed_module` under `--render module`, and
# under `--render stock` the build refuses it (`embed_symbol`, an error gate G7 contract reports). The component test
# page shows these kinds in one section (`testbench.module_only_block`) and the glass gates find them by the
# component's element. A later wrap adds one row here (wiki page 12 section 17.13, `cloud/WRAP-RECIPE.md` section 8).
MODULE_ONLY = {"resistor": "cadre.ob.resistor", "capacitor": "cadre.ob.capacitor", "diodes": "cadre.ob.diodes", "ground": "cadre.ob.ground", "source": "cadre.ob.source", "converter": "cadre.ob.converter", "transformer": "cadre.ob.transformer", "bipolar-transistor": "cadre.ob.bipolartransistor", "mosfet": "cadre.ob.mosfet", "logic": "cadre.ob.logic", "router": "cadre.ob.router",
               "automation-badge": "cadre.ob.automationbadge", "hydraulic-check-valve": "cadre.ob.checkvalve",
               "valve-analog-two-way-icon": "cadre.ob.valvetwoway", "valve-analog-three-way-icon": "cadre.ob.valvethreeway",
               "indicator-battery": "cadre.ob.battery", "indicator-engine": "cadre.ob.engine",
               "indicator-tank-atmospheric": "cadre.ob.tankatmospheric", "automation-readout": "cadre.ob.automationreadout",
               "heat-exchanger": "cadre.ob.heatexchanger", "heat-pump": "cadre.ob.heatpump",
               "hydraulic-separator": "cadre.ob.hydraulicseparator",
               "gauge-generator": "cadre.ob.gaugegenerator",
               "gauge-motors-and-pumps": "cadre.ob.gaugemotorspumps", "gauge-valve": "cadre.ob.gaugevalve",
               "hydraulic-valve-4-3": "cadre.ob.hydraulicvalve43", "hydraulic-valve-x-2": "cadre.ob.hydraulicvalvex2",
               "transmitter-button": "cadre.ob.transmitterbutton",
               "area-graph": "cadre.ob.areagraph",
               "line-graph": "cadre.ob.linegraph",
               "donut-chart": "cadre.ob.donutchart",
               "pie-chart": "cadre.ob.piechart",
               "polar-chart": "cadre.ob.polarchart",
               "radial-bar-chart": "cadre.ob.radialbarchart",
               "bar-horizontal": "cadre.ob.barhorizontal",
               "bar-vertical": "cadre.ob.barvertical",
               "circular-progress": "cadre.ob.circularprogress",
               "instrument-radial": "cadre.ob.instrumentradial",
               "readout-block": "cadre.ob.readoutblock"}
MODULE_VIEW = "Module/"
# The parameters the library's symbols carry beside the component's own, which a module-only symbol may state too: the
# device and status marks, all in `_STATUS_DROP` (they reach no property of the component).
_MODULE_ONLY_MARKS = {"hasTag": False, "deviceId": "", "deviceKind": "", "deviceLabel": "", "statusText": "",
                       "badgeDuty": False, "outOfService": False}
# The render target. `stock` draws every kind with the library views of the parent; `module`
# draws the kinds in MODULE_KIND with the Cadre OpenBridge module's components (module/, wiki
# page 12) and every other kind as before. The descriptor does not change.
RENDER = {"target": "stock", "devices": {}}
MODULE_KIND = {"pump": "cadre.ob.pump", "tank": "cadre.ob.tank", "motor": "cadre.ob.motor", "fan": "cadre.ob.fan",
               "valve": "cadre.ob.valve", "analogvalve": "cadre.ob.analogvalve", "filter": "cadre.ob.filter",
               "damper": "cadre.ob.damper", "switch": "cadre.ob.switch",
               "generator": "cadre.ob.generator", "readout": "cadre.ob.readout", "instrument-field": "cadre.ob.instrumentfield"}
# The two kinds of module 0.3.1 (COB-127): a value with its unit, drawn in the box the library gives the block
# (`symbol_box`) with a digit count in place of a number format, and opening the faceplate of the device
# kind its parameter names.
MODULE_INSTRUMENTS = ("readout", "instrument-field")
# The module draws a symbol only where its component can show it truthfully; otherwise the library's own
# view draws it under the module rendering as well:
#   MODULE_EXCEPT  parameter sets that keep a symbol on the library's view. The module's fan has no vertical
#                  artwork, so a vertical fan stays on the library's view.
#   MODULE_NEEDS   parameter values the component needs. The module's valves draw only the variants `regular`
#                  and `flat`, and its tank prints whole numbers. A parameter the symbol does not give counts as its default in the library
#                  view's contract. The instrument field's rows end at the end of the element or are centred by the
#                  wrapper, so `align` start stays on the library's view (measured, COB-127).
# Module 0.3.0 lifted the three cases the first plant renders found (COB-110): the module's pump and motor take
# `hasSpeed` (a device with no speed prints none), its tank takes `unit` and `hasCapacity` (a level in any
# unit, and a vessel that states no capacity draws no capacity line).
# Both are published in the library profile (`moduleExcept`, `moduleNeeds`).
# Module 0.3.1 adds two cases of its own. The element prints a number with a digit count: a number format it cannot
# translate (`fraction_digits`), and a field whose setpoint has other digits than its value (the element has one
# count), keep the library's view (`module_digits`). The enhanced field with a setpoint is 6 px higher than the
# library's box and the other cases at most 4 px (`module/web/instruments.json`, `measure_instruments.py`): the
# element is not cut, since its box does not clip, but it is not fitted either, so that case stays on the library's view.
# The module's filter, damper and switch have three orientations (`horizontal`, `verticalRight`, `verticalLeft`) where the library's
# has a `vertical` flag, which does not say which side, so a vertical filter, damper or switch stays on the library's view like a
# vertical fan.
# The generator set (`picture` `genset`) is a drawing of the library's own and stays on its view (wiki page 12 section 17.11).
MODULE_EXCEPT = {"fan": [{"vertical": True}], "filter": [{"vertical": True}], "damper": [{"vertical": True}],
                 "switch": [{"vertical": True}], "generator": [{"picture": "genset"}],
                 "instrument-field": [{"size": "enhanced", "hasSetpoint": True}]}
MODULE_NEEDS = {"valve": {"variant": ["regular", "flat"]}, "analogvalve": {"variant": ["regular", "flat"]},
                "filter": {"variant": ["regular", "flat"]}, "damper": {"variant": ["regular", "flat"]},
                "switch": {"variant": ["regular", "flat"]},
                # The module's generator is the indicator disc: the library's other variants, the activated ground, the
                # progress ring and the three badges are marks it does not draw, so a symbol that asks for one keeps the
                # library's view (the duty mark and the out of service greying do so through `parts.SYMBOL_PARAMS`).
                "generator": {"variant": ["regular"], "activated": [False], "progress": [False],
                              "badgeControl": ["none"], "badgeInterlock": ["none"], "badgeCommandLocked": ["none"]},
                "tank": {"valueFractionDigits": [0]}, "instrument-field": {"align": ["center", "end"]}}
# Parameters the module's component states with the contract's default where the symbol gives none: the
# component's own default differs from the library view's (the module's pump prints a speed, the library's
# does not).
MODULE_STATE = {"pump": ("hasSpeed",), "motor": ("hasSpeed",), "fan": ("hasSpeed",),
                "tank": ("unit", "hasCapacity"), "readout": ("value",), "instrument-field": ("value",)}

# Parameter values the library and the component name differently: the library's `regular` variant of a filter is the
# element's `square` (its enumeration is `square` and `flat`, `SquaredVariant`), and `flat` is `flat` in both.
MODULE_VALUE = {"filter": {"variant": {"regular": "square"}}, "damper": {"variant": {"regular": "square"}},
               "switch": {"variant": {"regular": "square"}}}

_DIGITS = re.compile(r"(?:#,##)?0(?:\.(0+))?")


def fraction_digits(pattern) -> int | None:
    """The digit count after the point of a `numberFormat` pattern the module's elements can print: `#,##0` 0,
    `#,##0.0` 1, `0.00` 2. The elements print `toFixed(fractionDigits)`, so a pattern of anything else (a percent,
    an exponent, literal text, an optional digit) is None and the symbol keeps the library's view. Thousands are
    not grouped by the elements: 1,234 in the library is 1234 in the module (measured, `instruments.json`)."""
    m = _DIGITS.fullmatch(pattern) if isinstance(pattern, str) else None
    return len(m.group(1) or "") if m else None


def module_digits(kind: str, params: dict, defaults: dict | None = None) -> int | None:
    """The digit count the module's element prints for a readout or an instrument field, or None where it cannot
    print the symbol's number format. A field with a setpoint has one count for both numbers."""
    defaults = defaults or {}
    digits = fraction_digits(params.get("format", defaults.get("format")))
    if digits is None or kind != "instrument-field" or not params.get("hasSetpoint", defaults.get("hasSetpoint")):
        return digits
    return digits if fraction_digits(params.get("setpointFormat", defaults.get("setpointFormat"))) == digits else None


# How high the module's element is, measured (`module/web/instruments.json`): the readout's chip is 26 px, 44 px with
# the identifier beneath it; the instrument field 40 px, 52 px enhanced, 60 px with a setpoint, 72 px enhanced with one.
# A box more than MODULE_SHORT px shorter keeps the library's view: the element would lie over its neighbours, and
# gate G5 does not look at a module component's height.
MODULE_SHORT = 4


def module_height(kind: str, params: dict, defaults: dict | None = None) -> int | None:
    """The height in px of the module's element for a readout or an instrument field, or None for another kind."""
    defaults = defaults or {}
    get = lambda k: params.get(k, defaults.get(k))
    if kind == "readout":
        return 44 if get("hasTag") else 26
    if kind == "instrument-field":
        return {("regular", False): 40, ("enhanced", False): 52, ("regular", True): 60,
                ("enhanced", True): 72}.get((get("size") or "regular", bool(get("hasSetpoint"))))
    return None


def _same(value, want) -> bool:
    return type(value) is type(want) and value == want


def module_probe(kind: str, params: dict, bound: dict) -> dict:
    """The symbol's parameters as `module_draws` is asked about them: a bound page part mark (`parts.SYMBOL_PARAMS`) counts
    as stated (None), and so does a bound parameter that `MODULE_NEEDS` names and the kind's component drops, such as the
    generator's progress ring: the binding would reach no property of the component, so the symbol keeps the library's view."""
    marks = set(parts.SYMBOL_PARAMS) | (set(MODULE_NEEDS.get(kind, {})) & MODULE_DROP.get(kind, set()))
    return {**params, **{k: None for k in bound if k in marks}}


def module_drawn(sym: dict) -> bool:
    """Whether a descriptor's symbol is drawn as the module's component under the module rendering: not asked to stay
    on the library's view (`render: view`), and one the component can draw (`module_draws`, with the same probe of the
    page parts' marks as `embed_symbol`). For a caller that reads descriptors and builds nothing, such as the glass
    gates, whose selectors find module components only (COB-198)."""
    kind = sym.get("kind")
    params = sym.get("params") or {}
    return sym.get("render") != "view" and module_draws(kind, module_probe(kind, params, sym.get("bind", {})), target="module")


def module_draws(kind: str, params: dict, defaults: dict | None = None, target: str | None = None,
                 height: float | None = None) -> bool:
    """Whether the module's component draws a symbol under the module rendering. `defaults` are the
    parameter defaults of the kind's library view (its contract); without them those of the library.
    `target` is the rendering asked about, for a caller that builds nothing (the walk's plan); without
    it the rendering of the build in hand. `height` is the height of the box the symbol is drawn in, where the
    caller knows it (`module_height`)."""
    if (target or RENDER["target"]) != "module" or module_type(kind) is None:
        return False
    listed = module_props(module_type(kind))
    if any(params.get(k, False) is not False for k in parts.SYMBOL_PARAMS if k not in listed):
        return False   # the page parts' marks (COB-159; None: bound) of a component that has no such property
    if any(all(_same(params.get(k), v) for k, v in keep.items()) for keep in MODULE_EXCEPT.get(kind, [])):
        return False
    if defaults is None:
        from hmi import library
        defaults = {"tank": library.TANK_PARAMS, "readout": library.AUTOMATION_READOUT_PARAMS,
                    "instrument-field": library.READOUT_PARAMS}.get(kind, library.SYMBOL_PARAMS)
    if kind in MODULE_INSTRUMENTS and module_digits(kind, params, defaults) is None:
        return False
    if height is not None and kind in MODULE_INSTRUMENTS:
        need = module_height(kind, params, defaults)
        if need is not None and height < need - MODULE_SHORT:
            return False
    return all(params.get(k, defaults.get(k)) in ok for k, ok in MODULE_NEEDS.get(kind, {}).items())


MODULE_COMPONENTS = ROOT / "module" / "components.json"
_MODULE_SCHEMA: dict = {}


def module_type(kind: str) -> str | None:
    """The module component that draws a descriptor kind under the module rendering: a library kind's (`MODULE_KIND`) or
    a module-only kind's (`MODULE_ONLY`); None for a kind the module does not draw."""
    return MODULE_KIND.get(kind) or MODULE_ONLY.get(kind)


def module_element(ctype: str) -> str:
    """The custom element a module component draws (`obc-resistor`), as `module/components.json` states it."""
    module_props(ctype)
    return _MODULE_SCHEMA.get(ctype, {}).get("element", "")


# What a module-only kind's contract states beyond its component's own properties, by the kind of element (decided from
# the component's properties, `module_geometry`). A symbol is an element on the filter's attribute set (`on`, `tag`,
# `readoutPosition`): it takes the marks of `_MODULE_ONLY_MARKS` and the geometry of the library's static symbol (48 px
# symbol box, `symbol-centre`, a state `on`, the readout and identifier boxes). A glyph is an element without them (a
# badge, a valve icon): its contract holds only the properties its component declares, a box anchor, no flow and no
# state, and its size is the component's default size (`defaultSize` of `module/components.json`).
_MODULE_SYMBOL_PROPS = ("on", "tag", "readoutPosition")
_MODULE_GLYPH = {"anchor": "box", "flow": "none"}


def module_geometry(ctype: str) -> str:
    """`symbol` for a component on the filter's attribute set, `glyph` for any other (see above)."""
    listed = module_props(ctype)
    return "symbol" if all(k in listed for k in _MODULE_SYMBOL_PROPS) else "glyph"


def module_contract(kind: str, template: dict) -> dict:
    """The contract of a module-only kind, derived from the module's own contract (`module/components.json`): the
    component's properties with their defaults, and the geometry of its class (`module_geometry`). A symbol also takes
    the marks of `_MODULE_ONLY_MARKS` and the geometry of `template`, the library's static symbol. A glyph takes
    neither: it carries exactly the properties its component declares. `positioning` is the generator's to state
    (`embed_module`), so it is no parameter."""
    ctype = MODULE_ONLY[kind]
    module_props(ctype)
    spec = _MODULE_SCHEMA.get(ctype, {})
    props = spec.get("props", {})
    own = {k: p["default"] for k, p in props.items() if k != "positioning" and "default" in p}
    if module_geometry(ctype) == "glyph":
        size = spec.get("defaultSize", {"width": 48, "height": 48})
        return {**_MODULE_GLYPH, "kind": kind, "view": MODULE_VIEW + kind, "size": [size["width"], size["height"]],
                "params": dict(sorted(own.items()))}
    keep = {k: template[k] for k in ("anchor", "identifier", "readoutExtent", "size", "symbolSize", "state", "statusMode")}
    return {**keep, "kind": kind, "view": MODULE_VIEW + kind, "params": dict(sorted({**_MODULE_ONLY_MARKS, **own}.items()))}


def module_props(ctype: str) -> set[str]:
    """The properties the module's component `ctype` has (`module/components.json`, the schema gate G1 reads). The
    generator emits a property that the library's contract has and the component may lack (`MODULE_IF_LISTED`) only
    where this lists it, so a build is the same before and after a module release adds the property. Read once per
    run; a test patches this function."""
    if not _MODULE_SCHEMA:
        _MODULE_SCHEMA.update(json.loads(MODULE_COMPONENTS.read_text(encoding="utf-8")) if MODULE_COMPONENTS.exists() else {})
    return set(_MODULE_SCHEMA.get(ctype, {}).get("props", {}))


# Library parameter to module property where the names differ; parameters with no module
# property are dropped (the faceplate and selection parameters move to the component's custom).
_SPEED_RENAME = {"speed": "speedInPercent"}
_STATUS_DROP = {"showStatus", "statusText", "hasTag", "deviceId", "deviceKind", "deviceLabel",
                "badgeDuty", "outOfService"}   # the last two: the page parts' marks, which keep a symbol on the library's view
# A readout's identifier is the element's `idTag` (beneath the value; the transmitter's `tag` draws nothing in a value
# chip), a field's label its `tag` (the caption). The number formats become `fractionDigits`, the field's `align`
# becomes `center`, and the field's own `tag` and `source` are drawn by neither (`embed_module`).
MODULE_PARAM = {"pump": _SPEED_RENAME, "motor": _SPEED_RENAME, "fan": _SPEED_RENAME, "tank": {},
                "valve": {}, "analogvalve": {}, "filter": {}, "damper": {}, "switch": {}, "generator": {}, "readout": {"tag": "idTag"}, "instrument-field": {"label": "tag"}}
MODULE_DROP = {"pump": _STATUS_DROP | {"value"}, "motor": _STATUS_DROP | {"value"},
               "fan": _STATUS_DROP | {"value", "vertical"},
               "valve": _STATUS_DROP | {"hasSpeed", "speed", "value"},
               "analogvalve": _STATUS_DROP | {"hasSpeed", "speed"},
               "filter": _STATUS_DROP | {"hasSpeed", "speed", "value", "vertical"},
               "damper": _STATUS_DROP | {"hasSpeed", "speed", "value", "vertical"},
               "switch": _STATUS_DROP | {"hasSpeed", "speed", "value", "vertical"},
               "generator": _STATUS_DROP | {"hasSpeed", "speed", "value", "vertical", "variant", "picture", "activated",
                                            "progress", "badgeControl", "badgeInterlock", "badgeCommandLocked"},
               "tank": {"medium", "showPercent", "chart", "history", "hasTag", "deviceId", "deviceKind",
                        "deviceLabel", "valueFractionDigits"},
               "readout": {"format", "hasTag", "label", "deviceId", "deviceKind", "deviceLabel", "stretch"},
               "instrument-field": {"format", "setpointFormat", "align", "source", "tag", "hasTag", "deviceId",
                                    "deviceKind", "deviceLabel"}}
# The property in which each module element draws the symbol's identifier: a readout's `idTag` (the transmitter's `tag`
# draws nothing in a value chip), a field's caption `tag` (the library's label, `MODULE_PARAM`), every other kind's `tag`.
MODULE_IDENT = {"readout": "idTag", "instrument-field": "tag"}
# Parameters that MODULE_DROP drops only while the component lacks the property (L4 items 3, 4 and 9, module 3.2 of the
# builders' contract): the status words and their mute (`showStatus`, `statusText`), the duty and out of service marks, and
# the readout's `stretch`. `module_drop` is the drop in force for the schema in hand.
_STATUS_PROPS = ("showStatus", "statusText", "badgeDuty", "outOfService")
MODULE_IF_LISTED = {"pump": _STATUS_PROPS, "motor": _STATUS_PROPS, "fan": _STATUS_PROPS, "valve": _STATUS_PROPS,
                    "analogvalve": _STATUS_PROPS, "filter": _STATUS_PROPS, "damper": _STATUS_PROPS, "switch": _STATUS_PROPS,
                    "generator": ("showStatus", "statusText"), "readout": ("stretch",)}


def module_drop(kind: str) -> set[str]:
    """The parameters of the library's contract that the component of `kind` is not given: `MODULE_DROP`, less those
    of `MODULE_IF_LISTED` that the component's schema lists."""
    listed = module_props(module_type(kind))
    if kind in MODULE_ONLY:   # a module-only kind states the status marks that its component lists
        return _STATUS_DROP - {k for k in _STATUS_PROPS if k in listed}
    return MODULE_DROP[kind] - {k for k in MODULE_IF_LISTED.get(kind, ()) if k in listed}


# A device symbol's alarm state (F016 of the ASMP study, COB-140): a device symbol whose descriptor binds
# and states none of its alert parameters follows the device's own alarms. Each such symbol takes a key in
# the page's `custom.alerts`, which one binding polls for the whole page (`cadre.hmi.alert_states`, one
# alarm query), so a page of many symbols costs one query a poll. A library symbol shows a frame for an
# alarm of a priority with an alert colour; a module component shows OpenBridge's level, Diagnostic too.
ALERT_PARAMS = ("alert", "alertFrameStatus", "alertFrameMode")
ALERT_FIELDS = {"library": {"alert": "alert", "alertFrameStatus": "status", "alertFrameMode": "mode"},
                "module": {"alert": "alertAny", "alertFrameStatus": "level", "alertFrameMode": "mode"}}
ALERT_POLL = "if(toMillis(now(2000)) > 0, '', '')"


def derived_alert(sym: dict, params: dict, contract_params: dict) -> str | None:
    """The key of a device symbol in the page's `custom.alerts`, where its alert parameters follow the
    device's alarms; None for a symbol that takes no alert, is no device, or whose descriptor binds or
    states its alert."""
    if "alert" not in contract_params or not (params.get("deviceId") or sym.get("alarm")):
        return None
    if sym["kind"].lower() == "indicator":
        return None   # a lamp draws no alert frame (L5): its tag's alarms still reach the lists and the banner
    if any(k in sym.get("bind", {}) for k in ALERT_PARAMS) or "alert" in sym.get("params", {}):
        return None
    return "a_" + re.sub(r"[^A-Za-z0-9_]", "_", sym["id"])


def alert_bindings(key: str, prefix: str, rendering: str) -> dict:
    """The bindings of a symbol's alert parameters to its entry of `custom.alerts`."""
    return {f"{prefix}{k}": pv.bind(pv.expr("{view.custom.alerts.%s.%s}" % (key, field)))
            for k, field in ALERT_FIELDS[rendering].items()}


def merge_custom(custom: dict, more: dict) -> None:
    """A symbol's view custom defaults merged into the page's: the `alerts` entries add up."""
    alerts = {**custom.get("alerts", {}), **more.get("alerts", {})}
    custom.update(more)
    if alerts:
        custom["alerts"] = alerts


def alert_poll(doc: dict) -> None:
    """The page's one poll of its device symbols' alarm states, where any symbol follows them: the
    defaults before the first answer, and the binding over the devices by key."""
    devices = (doc.get("custom") or {}).get("alerts")
    if not devices:
        return
    doc["custom"]["alerts"] = {k: dict(scripts.constant("ALERT_NONE")) for k in sorted(devices)}
    doc["propConfig"]["custom.alerts"] = pv.bind(pv.expr(ALERT_POLL), [pv.script_transform([
        f"return cadre.hmi.alert_states(self.session, {dict(sorted(devices.items()))!r})"])])


def device_nodes(descs: list[dict], devices: dict | None = None) -> dict[str, str]:
    """The node of the plant hierarchy of each device the descriptors draw (F033, F042): the node of the
    deepest page that draws it (`screen.node`), by the device's tag path. A device a page without a node
    draws has none there. A symbol that only opens a device's faceplate (`faceplate`) draws nothing. A device of the
    devices file that carries `node` and that no page draws with `device` has that node (L5)."""
    out: dict[str, str] = {}
    for desc in descs:
        node = desc["screen"].get("node", "")
        for s in descriptor_items(desc):
            folder = device_folder(s)
            if folder and node:
                path = tag_path(desc.get("tagRoot", ""), folder)
                if len(node.split("/")) > len(out.get(path, "").split("/")) or path not in out:
                    out[path] = node
    drawn = {tag_path(d.get("tagRoot", ""), device_folder(s)) for d in descs for s in descriptor_items(d)
             if device_folder(s)}
    for path, model in model_devices(devices).items():
        if model.get("node") and path not in drawn:
            out[path] = model["node"]
    return out


def hierarchy(descs: list[dict], devices: dict | None = None) -> list[dict]:
    """The plant hierarchy the descriptor set makes (F033 of the ASMP study, COB-141): a node for every
    `screen.node` and every node above one, root first, each with an `id` an expression may name
    (`n0`, `n1`, ...), its `name`, `path`, `parentId`, its pages (`label`, `route`) and the devices it
    owns (`screen.device_nodes`: the devices whose deepest page is one of its own). The generator writes it
    into `session.custom.hierarchy`, where `cadre.hmi.node_counts` counts each node's alarms."""
    paths: set[str] = set()
    owned = device_nodes(descs, devices)
    for node in [d["screen"].get("node", "") for d in descs] + sorted(set(owned.values())):
        parts = node.split("/") if node else []
        paths.update("/".join(parts[:i]) for i in range(1, len(parts) + 1))
    ids = {p: f"n{i}" for i, p in enumerate(sorted(paths, key=lambda p: (p.count("/"), p)))}
    out = []
    for p in sorted(paths, key=lambda p: (p.count("/"), p)):
        parent = p.rsplit("/", 1)[0] if "/" in p else ""
        pages = [{"label": d["screen"].get("navLabel", d["screen"].get("title", d["screen"]["route"])),
                  "route": d["screen"]["route"]} for d in descs if d["screen"].get("node") == p]
        out.append({"id": ids[p], "name": p.rsplit("/", 1)[-1], "path": p, "parentId": ids.get(parent, ""),
                    "pages": pages, "devices": sorted(f for f, n in owned.items() if n == p)})
    return out


def device_folder(sym: dict) -> str | None:
    """The tag folder of a device symbol, relative to the tag root: `device` names it, or `true`
    means the symbol's id."""
    d = sym.get("device")
    return d if isinstance(d, str) else (sym["id"] if d else None)


def faceplate_folder(sym: dict) -> str | None:
    """The device a plain symbol opens (L5): the symbol key `faceplate`, a device of the devices file by its id. The
    symbol does not draw the device: `device_nodes` and `hierarchy` ignore it, the node stays where the page that draws the
    device with `device` puts it (or the devices file's `node`)."""
    f = sym.get("faceplate")
    return f if isinstance(f, str) and f else None


def drawn_folder(sym: dict) -> str | None:
    """The device folder a symbol opens the faceplate of: its own device, or the one its `faceplate` names."""
    return device_folder(sym) or faceplate_folder(sym)


def device_kind(sym: dict) -> str:
    """The kind of the device a symbol opens: `params.deviceKind` where the symbol names one (a
    readout of a controller's process value), else the symbol's own kind."""
    return str(sym.get("params", {}).get("deviceKind") or sym["kind"]).lower()


def model_devices(model: dict | None) -> dict[str, dict]:
    """The devices of a device model by tag folder, `<tagRoot>/<id>`, the form of `deviceId`."""
    if not model:
        return {}
    return {tag_path(model.get("tagRoot", ""), d["id"]): d for d in model.get("devices", [])}


def descriptor_items(desc: dict) -> list[dict]:
    """Every symbol of a descriptor: diagram symbols, card items and the leaves of card bodies."""
    def walk(g):
        for it in g.get("items", []):
            if "items" in it:
                yield from walk(it)
            elif "kind" in it:
                yield it
    items = list(desc.get("symbols", []))
    for row in desc.get("rows", []):
        for card in row:
            items += card.get("items", [])
            if "body" in card:
                items += list(walk(card["body"]))
    return items


def device_symbols(descs: list[dict], devices: dict | None = None) -> list[dict]:
    """Every symbol marked `device`, as gate G7 devices reads it: its route and id, its kind, the
    device kind it names, the device's tag folder, its parameters, its bindings and the tag path each
    binding resolves to."""
    out = []
    known = model_devices(devices)
    for desc in descs:
        for s in descriptor_items(desc):
            folder = drawn_folder(s)
            if folder:
                out.append({"faceplate": bool(faceplate_folder(s) and not device_folder(s)), "route": desc.get("screen", {}).get("route", ""), "id": s["id"], "kind": s["kind"].lower(),
                            "deviceKind": s.get("params", {}).get("deviceKind") or (
                                str(known.get(tag_path(desc.get("tagRoot", ""), folder), {}).get("kind", "")).lower() or None
                                if faceplate_folder(s) and not device_folder(s) else None),
                            "folder": s.get("params", {}).get("deviceId") or tag_path(desc.get("tagRoot", ""), folder),
                            "params": dict(s.get("params", {})), "bind": dict(s.get("bind", {})),
                            "paths": {k: tag_path(desc.get("tagRoot", ""), m) for k, m in s.get("bind", {}).items()}})
    return out


MEDIUM_VAR = {"neutral": None, "fresh-water": "--automation-medium-fresh-water",
              "sea-water": "--automation-medium-sea-water", "fuel": "--automation-medium-fuel",
              "oil": "--automation-medium-oil", "steam": "--automation-medium-steam",
              "hot": "--automation-medium-hot", "cold": "--automation-medium-cold",
              "air": "--automation-medium-air-ventilation", "waste": "--automation-medium-waste"}


class Report:
    def __init__(self):
        self.errors, self.gaps, self.notes = [], [], []

    def as_dict(self):
        return {"errors": self.errors, "gaps": self.gaps, "notes": self.notes}


def library_contracts() -> dict:
    """The library's own contracts, as the parent generator wrote them (`library/contracts.json`)."""
    return json.loads((ROOT / "library" / "contracts.json").read_text(encoding="utf-8"))


def load_contracts() -> dict:
    """The contracts a build reads: the library's and those of the module-only kinds (`module_contract`)."""
    contracts = library_contracts()
    for kind in MODULE_ONLY:
        contracts[MODULE_VIEW + kind] = module_contract(kind, contracts[KIND_VIEW["filter"]])
    return contracts


def tag_path(root: str, member: str) -> str:
    return member if member.startswith("[") else f"{root}/{member}"


# ---------------------------------------------------------------------------------------
# Symbols
# ---------------------------------------------------------------------------------------
def symbol_box(sym: dict, contract: dict, limit: float | None = None) -> tuple[float, float, float, float]:
    """The embed box. For an automation symbol the descriptor gives the 48 px symbol box and
    the readout extends it on its side (the symbol stays on the line, OpenStudio's
    `positioning: symbol`); a readout's box is grown where it is too small for the readout
    (`grown_box`); every other component uses its box as given. `limit` is the most the identifier may
    widen the embed (`embed_limits`), none where nothing stands in its way."""
    if contract.get("grows"):
        return grown_box(sym, contract, limit)
    if contract.get("anchor") != "symbol-centre" or sym["kind"] == "readout":
        return sym["x"], sym["y"], sym["w"], sym["h"]
    pos = sym.get("params", {}).get("readoutPosition", "bottom")
    ex, ey = readout_extent(sym, contract, limit)
    x, y, s = sym["x"], sym["y"], 48
    if pos == "right":
        return x, y, s + ex, s
    if pos == "left":
        return x - ex, y, s + ex, s
    if pos == "bottom":
        return x - ex / 2, y, s + ex, s + ey
    if pos == "top":
        return x - ex / 2, y - ey, s + ex, s + ey
    return x, y, s, s


def embed_limits(symbols: list[dict], contracts: dict) -> dict[str, float]:
    """The most the identifier of a symbol may widen its embed, for each symbol of a diagram whose
    identifier does not get the width it needs (`symbol_box` takes it as `limit`).

    An embed is as wide as its identifier needs (`readout_extent`, `grown_box`), and on a row of
    symbols closer together than that, two widened embeds would lie over each other and their
    identifiers would run together. So an embed is widened only into the gap that separates it from the
    embed of the next symbol on its row: two embeds that both want more than half of the gap take half
    each, and where one wants less the other takes the rest. The identifier that does not get its width
    ends in an ellipsis and gate G5 says so. A readout centred on its symbol or on its box stays
    centred, so it gives up on both sides what it lacks on one.

    Two symbols are on one row when the boxes they have without the widening share more than `OVERLAP`
    px down the page; a pair whose boxes already overlap across the page is left alone (no narrower
    identifier would part them, and gate G5 reports it)."""
    spans = []
    for s in symbols:
        c = contracts.get(view_of(s))
        least = full = (s["x"], s["y"], s["w"], s["h"])
        if c:
            least, full = symbol_box(s, c, 0), symbol_box(s, c)
        spans.append((s["id"], least, least[0] - full[0], (full[0] + full[2]) - (least[0] + least[2])))
    room = {i: [left, right] for i, _box, left, right in spans}
    for k, a in enumerate(spans):
        for b in spans[k + 1:]:
            (ax, ay, aw, ah), (bx, by, bw, bh) = a[1], b[1]
            if min(ay + ah, by + bh) - max(ay, by) <= OVERLAP:
                continue
            if ax + aw <= bx:
                first, second = a, b
            elif bx + bw <= ax:
                first, second = b, a
            else:
                continue
            gap = second[1][0] - (first[1][0] + first[1][2])
            reach, back = first[3], second[2]     # what the first wants to its right, the second to its left
            if reach + back <= gap:
                continue
            room[first[0]][1] = min(room[first[0]][1], max(gap / 2, gap - back))
            room[second[0]][0] = min(room[second[0]][0], max(gap / 2, gap - reach))
    out = {}
    for i, _box, left, right in spans:
        got_left, got_right = room[i]
        if got_left < left or got_right < right:
            out[i] = 2 * min(got_left, got_right) if left and right else (got_left if left else got_right)
    return out


def gap_box(sym: dict, rep: Report, pos: dict | None = None) -> dict:
    rep.gaps.append({"id": sym["id"], "kind": sym["kind"], "reason": "no library component"})
    pos = pos or pv.cpos(sym["x"], sym["y"], sym["w"], sym["h"])
    return pv.node("ia.display.label", f"GAP_{sym['id']}", pos, {
        "text": f"GAP: {sym['kind']}", "textStyle": {"textAlign": "center"},
        "style": {"classes": "cadre/font/label cadre/text/inactive", "justifyContent": "center",
                  "border": "1px dashed var(--element-inactive-color)", "borderRadius": "4px"}})


# The blocks besides the automation symbols whose identifier the diagram toolbar's ID-tag button hides and shows. A
# controller and a sequence show their label in place of the identifier when `hasTag` is false, so the button would
# swap a box's name rather than hide it; they keep theirs.
ID_TAG_BLOCKS = ("tank", "readout", "instrument-field")


def identifier_own(contract: dict, params: dict) -> bool:
    """Whether a block may draw its identifier by the descriptor alone (`library.identifier_shown`): an automation
    symbol unless the descriptor says no, every other kind as its `hasTag` or the contract's default. The ID-tag
    button's binding ends in this answer (`toolbar_flag`)."""
    from hmi import library
    return library.identifier_shown(contract, params) if contract.get("identifier") else bool(params.get("hasTag", True))


def toolbar_flag(button: str, own) -> str:
    """The expression of a symbol flag that a button of the diagram toolbar switches (`view.custom.<button>`, see
    `toolbar_node`): the button's state, and false where the descriptor refuses the flag, so a symbol with `hasTag`
    false shows no identifier whichever way the button stands."""
    return f"{{view.custom.{button}}} && {'true' if own else 'false'}"
def literal(v) -> str:
    """The expression literal of a state value: a boolean, a number or a quoted string."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'") + "'"


def state_default(sym: dict) -> tuple[str, object]:
    """The data type and the starting value of the tag an indicator's `bind.state` reads (L5): boolean and false
    where the symbol has no `states`; a string where any state value is one, else a number."""
    values = [st["value"] for st in sym.get("states") or []]
    if any(isinstance(v, str) for v in values):
        return "String", ""
    if any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
        return "Float8", 0
    return "Boolean", False


def state_bindings(sym: dict, gname: str) -> dict:
    """The embed bindings of an indicator coloured by its state (L5, wiki 13 section 9): `on` for the lamp's icon (the
    state is one of the states whose colour is not `off`; the boolean itself without `states`), and, with `states`,
    `colour` as a `case` over the same custom property that reads the tag. No script transform."""
    g = "{view.custom.%s}" % gname
    states = sym.get("states") or []
    if not states:
        return {"props.params.on": pv.bind(pv.expr(g))}
    on = [f"{g} = {literal(st['value'])}" for st in states if st.get("colour", "on") != "off"]
    paints = "".join(f"{literal(st['value'])}, {literal(library.state_paint(st['colour']))}, " for st in states
                     if st.get("colour"))
    default = library.state_paint(sym.get("stateDefault", "off"))
    return {"props.params.on": pv.bind(pv.expr(" || ".join(on) if on else "false")),
            "props.params.colour": pv.bind(pv.expr(f"case({g}, {paints}{literal(default)})"))}


def embed_symbol(sym: dict, contracts: dict, tag_root: str, rep: Report, *, toolbar: bool,
                 pos=None, limit: float | None = None) -> tuple[dict | None, dict, dict]:
    """(node, view custom defaults, view custom bindings). `limit` is the symbol's entry of
    `embed_limits`, where it has one."""
    kind = sym["kind"].lower()
    view_path = view_of(sym) or None
    if not view_path or view_path not in contracts:
        return gap_box(sym, rep, pos), {}, {}
    c = contracts[view_path]
    params = dict(sym.get("params", {}))
    lamp = kind == "indicator"   # a lamp coloured by its state (L5): `bind.state` is read like `bind.on`
    for k in list(params) + [b for b in sym.get("bind", {}) if not (lamp and b == "state")]:
        if k not in c["params"]:
            rep.errors.append(f"{sym['id']}: parameter {k!r} is not in the {view_path} contract")
    folder = device_folder(sym)
    opens = faceplate_folder(sym)
    if opens and not folder:   # a plain symbol that opens a device's faceplate (L5): the device is not this symbol's own
        dev = params.setdefault("deviceId", tag_path(tag_root, opens))
        model = RENDER["devices"].get(dev)
        if model and not params.get("deviceKind"):
            params["deviceKind"] = str(model["kind"]).lower()
    if folder:
        dev = params.setdefault("deviceId", tag_path(tag_root, folder))
        rel = dev[len(tag_root) + 1:] if dev.startswith(tag_root + "/") else None
        # the rule of the device's kind, not the symbol's: a readout that shows a controller's process
        # value (`deviceKind` controller) binds the controller's member
        members, rule = FACEPLATE_MEMBERS.get(device_kind(sym), {}), bind_rule(device_kind(sym))
        for k, member in sym.get("bind", {}).items():
            want = rule.get(k)
            if rel is not None and want in members and member != f"{rel}/{want}":
                rep.errors.append(f"{sym['id']}: {k!r} is bound to {member!r}; the faceplate reads "
                                  f"'{rel}/{want}' (faceplate contract)")
    if sym.get("label"):
        params["deviceLabel"] = sym["label"]
    if kind == "tank" and params.get("static") and "max" not in params and "max" not in sym.get("bind", {}):
        # a static tank shows its capacity, and the view's default (100) is no capacity of any vessel: a
        # descriptor that states none draws none, and one that asks for the line without stating it is refused
        if params.setdefault("hasCapacity", False):
            rep.errors.append(f"{sym['id']}: 'hasCapacity' is true and the descriptor states no 'max': "
                              f"the tile would show the default of the {view_path} contract")
    height = None
    if kind in MODULE_INSTRUMENTS and pos is None:   # the box the library gives the block; a card lays its own out
        height = symbol_box(sym, c, limit)[3]
    # a symbol that states the duty mark or the out of service greying stays on the library's view: the module's
    # components have neither (COB-159); a bound one counts as stated
    probe = module_probe(kind, params, sym.get("bind", {}))
    if kind in MODULE_ONLY and not (sym.get("render") != "view" and module_draws(kind, probe, c["params"], height=height)):
        # no library view exists to fall back on: refuse, never a silent gap (gate G7 contract reports the error)
        why = ("build it with --render module" if RENDER["target"] != "module" else
               "the component cannot draw these parameters (or the symbol asks for the library's view)")
        rep.errors.append(f"{sym['id']}: kind {kind!r} is module only ({MODULE_ONLY[kind]}); {why}")
        return gap_box(sym, rep, pos), {}, {}
    if sym.get("render") != "view" and module_draws(kind, probe, c["params"], height=height):
        return embed_module(sym, kind, params, c, tag_root, toolbar=toolbar, pos=pos, limit=limit)
    x, y, w, h = symbol_box(sym, c, limit) if pos is None else (0, 0, 0, 0)
    prop_cfg, custom, custom_cfg = {}, {}, {}
    state = c.get("state")
    for k, member in sym.get("bind", {}).items():
        tp = tag_path(tag_root, member)
        if lamp and k == "state":   # the lamp's state, of any type: its icon and its colour follow one subscription
            custom[f"g_{sym['id']}"] = state_default(sym)[1]
            custom_cfg[f"custom.g_{sym['id']}"] = pv.bind(pv.tag(tp))
            prop_cfg.update(state_bindings(sym, f"g_{sym['id']}"))
        elif k == state:   # a gate: one subscription on the view, read by the symbol and the pipes
            custom[f"g_{sym['id']}"] = bool(params.get(k, False))
            custom_cfg[f"custom.g_{sym['id']}"] = pv.bind(pv.tag(tp))
            prop_cfg[f"props.params.{k}"] = pv.bind(pv.expr(f"{{view.custom.g_{sym['id']}}}"))
        else:
            prop_cfg[f"props.params.{k}"] = pv.bind(pv.tag(tp))
    if state and state in params and f"props.params.{state}" not in prop_cfg:
        custom[f"g_{sym['id']}"] = bool(params[state])
        prop_cfg[f"props.params.{state}"] = pv.bind(pv.expr(f"{{view.custom.g_{sym['id']}}}"))
    if toolbar and (c.get("symbolSize") or kind in ID_TAG_BLOCKS) and not sym.get("alarm"):
        # the ID-tag button reaches every block that draws an identifier (owner's request of 2026-10-22); a fault
        # row (COB-159) keeps its text and its status as the descriptor states them: its text is the condition, not
        # an ID tag the toolbar may hide
        prop_cfg["props.params.hasTag"] = pv.bind(pv.expr(toolbar_flag("showTag", identifier_own(c, params))))
    if toolbar and c.get("anchor") == "symbol-centre" and kind != "readout" and not sym.get("alarm") and not lamp:
        # (a lamp has no status row for the Readout toggle to bring back, L5)
        prop_cfg["props.params.showStatus"] = pv.bind(pv.expr(toolbar_flag("showReadout", params.get("showStatus", True))))
    key = derived_alert(sym, params, c["params"])
    if key:   # F016: the symbol's alert follows the device's alarms
        prop_cfg.update(alert_bindings(key, "props.params.", "library"))
        params = {k: v for k, v in params.items() if k not in ALERT_PARAMS}
        # a fault row names the tag its alarms are on, as `tag:<path>` (`cadre.hmi.device_sources`)
        custom["alerts"] = {key: ("tag:" + tag_path(tag_root, sym["alarm"]) if sym.get("alarm") and not params.get("deviceId")
                                  else params["deviceId"])}
    # Every parameter of the contract that is not bound is stated, with its default where the descriptor
    # gives none. After a page is loaded by URL in the same browser tab, an embedded view keeps the value of
    # each parameter its embedding leaves out from the instance that stood at the same place of the page
    # before (GF-60): a field with no unit read the unit of another display's field, and a device with no
    # label opened its faceplate under another device's label.
    # A parameter the generator binds is left to its binding. A default stated beside a binding showed
    # instead of the bound value on the second of two symbols of the same view at the same place of two
    # displays (GF-61): a lamp read Off with its tag true.
    # That holds for a parameter the descriptor states too: its `hasTag` or `showStatus` lives in the toolbar's binding.
    stated = {k: v for k, v in {**c["params"], **params}.items() if f"props.params.{k}" not in prop_cfg}
    # the notification's flap stands outside the symbol's box, as the module's does (L5): the embed does not clip it
    node = pv.node("ia.display.view", sym["id"], pos or pv.cpos(x, y, w, h),
                   {"path": view_path, "params": stated, "style": {"overflow": "visible"}}, prop_config=prop_cfg or None)
    return node, custom, custom_cfg


def status_words(kind: str, state_expr: str, has_speed: bool) -> str | None:
    """The expression of the words the library view's status row shows (`library._status_row`): `On` or `Off`, and for a
    pump, motor or fan that has a speed the speed in per cent while it runs. None for a kind whose row shows another
    reading (an analogue valve's opening)."""
    mode = library.DEVICE_KINDS[{"analogvalve": "AnalogValve"}.get(kind, kind.capitalize())][4]
    if mode == "speed" and has_speed:
        return f"if({state_expr}, numberFormat({{this.props.speedInPercent}}, '0') + ' %', 'Off')"
    return f"if({state_expr}, 'On', 'Off')" if mode in ("speed", "onoff") else None


def module_status(sym: dict, kind: str, props: dict, prop_cfg: dict, *, toolbar: bool, drop: set[str],
                  gated: bool) -> None:
    """The status row of a module symbol (L4 items 3 and 9). The element draws its own word only when stopped ("Off"), and
    none while it runs, and has no mute. Where the component's schema lists `showStatus` and `statusText`, the symbol
    states the library row's words and follows the toolbar's Readout toggle (`view.custom.showReadout`), as the
    library view does. A descriptor that states the words keeps them. `gated` is whether the symbol has a state to
    follow (`view.custom.g_<id>`)."""
    if toolbar and "showStatus" not in drop:
        # the toolbar's Readout button, as on the library's view (`embed_symbol`): false where the descriptor says so,
        # and no value beside the binding (GF-61)
        prop_cfg["props.showStatus"] = pv.bind(pv.expr(toolbar_flag("showReadout", props.pop("showStatus", True))))
    if "statusText" not in drop and "statusText" not in props:
        words = status_words(kind, f"{{view.custom.g_{sym['id']}}}" if gated else "false",
                             props.get("hasSpeed") is True)
        if words:
            prop_cfg["props.statusText"] = pv.bind(pv.expr(words))


def embed_module(sym: dict, kind: str, params: dict, c: dict, tag_root: str, *, toolbar: bool,
                 pos=None, limit: float | None = None) -> tuple[dict, dict, dict]:
    """A Cadre OpenBridge module component for a library kind. An automation symbol (pump, motor, fan,
    valves) uses OpenBridge's `symbol` positioning: its box is the 48 px symbol box and the readout lies
    outside it, so the symbol centre is where the descriptor puts it. A tank fills the descriptor's box. A readout
    and an instrument field fill the box the library gives the block (`symbol_box`, `limit` as for the library's
    view). Selection (faceplate dock contract) is a DOM click script reading the component's custom properties."""
    rename, drop = MODULE_PARAM.get(kind, {}), module_drop(kind)
    props = {rename.get(k, k): v for k, v in params.items() if k not in drop}
    bound = sym.get("bind", {})
    for k in MODULE_STATE.get(kind, ()):
        if k not in bound:            # a default stated beside a binding shows instead of the bound value (GF-61)
            props.setdefault(k, c["params"][k])
    for k, values in MODULE_VALUE.get(kind, {}).items():
        if props.get(k) in values:
            props[k] = values[props[k]]
    if kind == "instrument-field" and params.get("hasSetpoint") and "setpoint" not in bound:
        props.setdefault("setpoint", c["params"]["setpoint"])
    if kind in MODULE_INSTRUMENTS:
        props["fractionDigits"] = module_digits(kind, params, c["params"])
    if kind == "instrument-field" and params.get("align") == "center":
        props["center"] = True
    prop_cfg, custom, custom_cfg = {}, {}, {}
    state = c.get("state")
    for k, member in sym.get("bind", {}).items():
        tp = tag_path(tag_root, member)
        if k == state:
            custom[f"g_{sym['id']}"] = bool(params.get(k, False))
            custom_cfg[f"custom.g_{sym['id']}"] = pv.bind(pv.tag(tp))
            prop_cfg[f"props.{state}"] = pv.bind(pv.expr(f"{{view.custom.g_{sym['id']}}}"))
        elif k not in drop:
            props.pop(rename.get(k, k), None)
            prop_cfg[f"props.{rename.get(k, k)}"] = pv.bind(pv.tag(tp))
    if state and state in params and f"props.{state}" not in prop_cfg:
        custom[f"g_{sym['id']}"] = bool(params[state])
        prop_cfg[f"props.{state}"] = pv.bind(pv.expr(f"{{view.custom.g_{sym['id']}}}"))
    # an automation symbol: the 48 px symbol and its readout (the kind `readout` also says `symbol-centre`: its
    # contract centres it on its point, but the readout is the block, not a symbol with one)
    symbol = c.get("anchor") == "symbol-centre" and kind != "readout"
    # The identifier the element draws (a symbol's or a tank's `tag`, a readout's `idTag`, a field's caption `tag`): where
    # the descriptor refuses it none, under a toolbar the ID-tag button's binding. The text lies in the component's
    # custom, so no text enters an expression, and no value is stated beside the binding (GF-61).
    ident, own_custom = MODULE_IDENT.get(kind, "tag"), {}
    if props.get(ident) and not identifier_own(c, params):
        props.pop(ident)
    elif props.get(ident) and toolbar:
        own_custom["idText"] = props.pop(ident)
        prop_cfg[f"props.{ident}"] = pv.bind(pv.expr(f"if({toolbar_flag('showTag', True)}, {{this.custom.idText}}, '')"))
    if symbol:
        module_status(sym, kind, props, prop_cfg, toolbar=toolbar, drop=drop, gated=state in bound or state in params)
    if symbol:
        # `symbol` positioning makes the element's box the 48 px symbol, centred on our box for
        # every readout side; `point` draws the symbol 24 px off its anchor (measured, wiki page 12). The
        # generator indicator is the 48 px disc already and has no such property.
        if "positioning" in module_props(module_type(kind)):
            props["positioning"] = "symbol"
        box = pv.cpos(sym["x"], sym["y"], 48, 48)
    elif pos is not None:
        box = None                     # a card lays the symbol out: its position is the flex item's
    elif kind in MODULE_INSTRUMENTS:
        box = pv.cpos(*symbol_box(sym, c, limit))
    else:
        box = pv.cpos(sym["x"], sym["y"], sym["w"], sym["h"])
    key = derived_alert(sym, params, c["params"]) if "alert" not in drop else None
    if key:   # F016: the component's alert follows the device's alarms, at OpenBridge's own level
        prop_cfg.update(alert_bindings(key, "props.", "module"))
        for k in ALERT_PARAMS:
            props.pop(k, None)
        custom["alerts"] = {key: params["deviceId"]}
    node = pv.node(module_type(kind), sym["id"], pos or box, props, prop_config=prop_cfg or None)
    if params.get("deviceId"):
        if kind in MODULE_INSTRUMENTS:   # as `library.SELECT_INSTRUMENT`: the kind the symbol names, tag else label
            shows, title = params.get("deviceKind") or "instrument", params.get("tag") or params.get("label") or ""
        else:
            # the kind the device names, as on the library's view (the test page's alarm lamps are `switch` symbols of
            # indicator devices, and the switch has no faceplate of its own)
            shows, title = params.get("deviceKind") or kind, params.get("tag") or params["deviceId"].split("/")[-1]
        own_custom.update({"deviceId": params["deviceId"], "deviceKind": shows, "title": title,
                           "label": params.get("deviceLabel", "")})
        node["events"] = pv.on_click([
            "cadre.hmi.select_device(self.session, self.custom.deviceId, self.custom.deviceKind, "
            "self.custom.title, self.custom.label)",
            *library.open_faceplate()])
    if own_custom:
        node["custom"] = own_custom
    return node, custom, custom_cfg


# ---------------------------------------------------------------------------------------
# Pipes
# ---------------------------------------------------------------------------------------
def static_tile(sym: dict) -> bool:
    """Whether a symbol is drawn as the library's static tank, whose tile lies inside its box. The module's
    tank fills its box, so where the module draws the tank a pipe ends at the box as before. A static tank
    that states no capacity is the library's tile under either rendering (`module_draws`)."""
    kind = sym["kind"].lower()
    params = dict(sym.get("params", {}))
    if kind == "tank" and params.get("static") and "max" not in params and "max" not in sym.get("bind", {}):
        params.setdefault("hasCapacity", False)                                  # as `embed_symbol` settles it
    return kind == "tank" and bool(params.get("static")) and not module_draws(kind, params)


def pipes_svg(desc: dict, contracts: dict, rep: Report) -> tuple[dict | None, dict, dict]:
    syms = []
    for s in desc.get("symbols", []):
        c = contracts.get(view_of(s), {})
        s2 = dict(s)
        if c.get("anchor") == "symbol-centre" and s["kind"].lower() != "readout":
            s2.update({"w": 48, "h": 48, "anchor": "symbol-centre"})
        if static_tile(s):
            s2["tile"] = STATIC_TILE
        syms.append(s2)
    d2 = dict(desc, symbols=syms)
    g, geo = diagram.build_graph(d2, contracts)
    try:
        dnf = diagram.compile_flow(g)
    except OverflowError:
        rep.errors.append("flow: path enumeration limit reached; split the diagram")
        dnf = {e: [frozenset()] for e in g.edges}
    exprs = {e: diagram.dnf_expression(t, lambda n: f"{{view.custom.g_{n}}}") for e, t in dnf.items()}
    W, H = desc["screen"]["width"], desc["screen"]["height"]
    # Every outline first, then every inner stroke, then the end marks: an outline drawn after
    # another pipe's inner stroke would cross it at a T-joint (seen in the one-to-one comparison).
    outlines, inners, marks, cfg = [], [], [], {}
    pipes = desc.get("pipes", [])
    n_out = len(pipes)
    for k, p in enumerate(pipes):
        p0, s0, p1, s1 = geo[p["id"]]
        pts = diagram.route(p0, s0, p1, s1, p.get("via", ()))
        d = diagram.path_d(pts)
        size = {"small": 2, "medium": 4, "large": 6, "xl": 10}.get(p.get("size", "medium"), 4)
        outlines.append({"type": "path", "name": f"{p['id']}_outline", "d": d, "fill": {"paint": "none"},
                         "stroke": {"paint": "var(--automation-pipe-tertiary-color)", "width": size + 2,
                                    "linejoin": "miter", "linecap": "square"}})
        inners.append({"type": "path", "name": p["id"], "d": d, "fill": {"paint": "none"},
                       "stroke": {"paint": "var(--automation-pipe-primary-color)", "width": size,
                                  "linejoin": "miter", "linecap": "square"}})
        i = n_out + k
        medium = MEDIUM_VAR.get(p.get("medium", "neutral"))
        flow_col = (f"if({{view.custom.colorMode}}, 'var({medium})', 'var(--automation-pipe-primary-color)')"
                    if medium else "'var(--automation-pipe-primary-color)'")
        if p.get("state") == "closed":
            ex = "'var(--automation-pipe-tertiary-color)'"
        elif p["id"] in exprs:
            ex = f"if({exprs[p['id']]}, {flow_col}, 'var(--automation-pipe-primary-inverted-color)')"
        else:
            ex = "'var(--automation-pipe-primary-inverted-color)'"
        cfg[f"props.elements[{i}].stroke.paint"] = pv.bind(pv.expr(ex))
        for end, pt, other in (("from", p0, pts[1] if len(pts) > 1 else p1), ("to", p1, pts[-2] if len(pts) > 1 else p0)):
            mark = p[end].get("end") if "ref" not in p[end] else None
            if mark in ("arrow-in", "arrow-out", "cap"):
                marks.append(end_mark(pt, other, mark, size))
    els = outlines + inners + marks
    node = svg("Pipes", pv.cpos(0, 0, W, H), els, view_box=f"0 0 {W} {H}",
               extra_config=cfg, props={"preserveAspectRatio": "none"})
    flow = diagram.check_flow(g, exprs)
    return node, flow, {"graph_nodes": len(g.nodes), "gates": len(g.gate_of), "pipes": len(g.edges),
                        "expressions": exprs}


def end_mark(pt, towards, mark, size):
    (x, y), (tx, ty) = pt, towards
    dx, dy = (x - tx), (y - ty)
    horiz = abs(dx) >= abs(dy)
    s = size + 6
    if mark == "cap":
        d = (f"M{x} {y - s}L{x} {y + s}" if horiz else f"M{x - s} {y}L{x + s} {y}")
        return {"type": "path", "name": "cap", "d": d, "fill": {"paint": "none"},
                "stroke": {"paint": "var(--automation-pipe-tertiary-color)", "width": 2}}
    out = (mark == "arrow-out")
    sgn = (1 if dx >= 0 else -1) if horiz else (1 if dy >= 0 else -1)
    if not out:
        sgn = -sgn
    if horiz:
        tip = (x + sgn * s, y)
        d = f"M{tip[0]} {tip[1]}L{x} {y - s}L{x} {y + s}Z"
    else:
        tip = (x, y + sgn * s)
        d = f"M{tip[0]} {tip[1]}L{x - s} {y}L{x + s} {y}Z"
    return {"type": "path", "name": mark, "d": d, "fill": {"paint": "var(--automation-pipe-tertiary-color)"}}


# ---------------------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------------------
def section_node(sec: dict) -> dict:
    kids = []
    if sec.get("label"):
        kids.append(pv.node("ia.display.label", "Label", pv.fpos(shrink=0), {
            "text": sec["label"], "style": {"classes": "cadre/font/label cadre/text/neutral",
                                             "padding": "4px 8px"}}))
    ev = None
    if sec.get("route"):
        ev = pv.on_click([f"system.perspective.navigate('{sec['route']}')"])
    return pv.node("ia.container.flex", f"Section_{sec['id']}", pv.cpos(sec["x"], sec["y"], sec["w"], sec["h"]), {
        "direction": "column", "alignItems": "flex-end",
        "style": {"classes": "cadre/surface/section", **({"cursor": "pointer"} if ev else {})}},
        events=ev, children=kids)


LABEL_CLASSES = {"heading": "cadre/font/subtitle cadre/text/active",
                 "body": "cadre/font/body cadre/text/active",
                 "label": "cadre/font/label cadre/text/neutral"}


def text_label(t: dict) -> dict:
    """A free text label on a diagram (a stream destination, an equipment name)."""
    align = t.get("align", "left")
    return pv.node("ia.display.label", f"Text_{t['id']}", pv.cpos(t["x"], t["y"], t["w"], t["h"]), {
        "text": t["text"], "textStyle": {"textAlign": align},
        "style": {"classes": LABEL_CLASSES.get(t.get("style", "label"), LABEL_CLASSES["label"]),
                  "whiteSpace": "nowrap",
                  "justifyContent": {"left": "flex-start", "center": "center", "right": "flex-end"}[align]}})


def has_media(desc: dict) -> bool:
    """Whether a pipe of a diagram names a medium with a colour: only then does colour mode change anything."""
    return any(MEDIUM_VAR.get(p.get("medium", "neutral")) for p in desc.get("pipes", []))


def tags_shown_at_start(desc: dict) -> bool:
    """Whether a page shows its identifiers when it opens: a diagram's toolbar starts its ID-tag button as the
    descriptor's `showTags` says (off where it says nothing); a page without a toolbar always shows them. The walk's
    plan reads the same rule (`walk_plan.find_text`)."""
    return bool(desc.get("showTags", False)) or not desc.get("toolbar", True)


# The frame the child in hand is built with: a page of the ASM frame carries the in-page search panel (L4).
FRAME = {"name": "openbridge"}
MODULE_COMPONENTS = ROOT / "module" / "components.json"
CANVAS_ZOOM = "cadre.ob.canvaszoom"


def module_registry() -> dict:
    """The module's component registry (`module/components.json`): type to its description and props. Read on
    each call, so that a test may patch this function with a registry of its own."""
    try:
        return json.loads(MODULE_COMPONENTS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def canvas_zoom_node() -> dict | None:
    """The module's canvas zoom component (contract 3.1), or None unless the module rendering is in hand and the
    registry lists the component. Nothing visible: a flex item of no size, the last child of the canvas. It
    writes `zoom` (bound both ways to `view.custom.zoom`) on Ctrl+wheel, pinch and Ctrl+plus, minus, 0 over the
    canvas whose DOM identifier it is given, and keeps the browser from zooming the frame. A prop the registry
    does not list for it is not written."""
    entry = module_registry().get(CANVAS_ZOOM)
    if RENDER["target"] != "module" or not entry:
        return None
    listed = entry.get("props", {})
    props = {k: v for k, v in (("min", parts.ZOOM_MIN), ("max", parts.ZOOM_MAX), ("targetDomId", parts.CANVAS_DOM_ID),
                               ("guardBrowserZoom", True)) if k in listed}
    prop_config = {"props.zoom": pv.bind(pv.prop("view.custom.zoom", True))} if "zoom" in listed else {}
    # the canvas the page really has, measured in the browser (module 0.4.1): the fit reads it (parts.fit_expression)
    for prop, custom in (("viewWidth", parts.CANVAS_W), ("viewHeight", parts.CANVAS_H)):
        if prop in listed:
            prop_config[f"props.{prop}"] = pv.bind(pv.prop(custom.strip("{}"), True))
    prop_config = prop_config or None
    return pv.node(CANVAS_ZOOM, "CanvasZoom", pv.fpos(basis="0px", grow=0, shrink=0), props, prop_config=prop_config)


def _zoom_button(name: str, text: str, lines: list[str], *, enabled: str | None = None, text_expr: str | None = None,
                 width: str = "36px") -> dict:
    cfg = {}
    if enabled:
        cfg["props.enabled"] = pv.bind(pv.expr(enabled))
    if text_expr:
        cfg["props.text"] = pv.bind(pv.expr(text_expr))
    return pv.node("ia.input.button", name, pv.fpos(shrink=0, basis=width), {
        "text": text, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "32px", "padding": "0 4px"}},
        prop_config=cfg or None, events=pv.on_action(lines))


def zoom_controls() -> dict:
    """Minus, the percentage (a click returns to 100 %) and plus: the toolbar's zoom of the canvas, outside the
    scaled box. A step is 1.25 times, held to 0.5 to 4."""
    lo, hi, step = parts.ZOOM_MIN, parts.ZOOM_MAX, parts.ZOOM_STEP
    z = parts.ZOOM_VIEW
    return pv.node("ia.container.flex", "Zoom", pv.fpos(shrink=0, basis="auto"), {
        "direction": "row", "alignItems": "center", "style": {"gap": "2px", "marginLeft": "8px"}}, children=[
        _zoom_button("ZoomOut", "−", [
            "z = self.view.custom.zoom or 1",
            f"self.view.custom.zoom = max({lo:g}, round(z / {step:g}, 4))"], enabled=f"{z} > {lo:g}"),
        _zoom_button("ZoomReset", "100%", ["self.view.custom.zoom = 1"], width="72px",
                     text_expr=f"numberFormat({z} * 100, '0') + '%'"),   # "100 %" wrapped in 64 px (glass)
        _zoom_button("ZoomIn", "+", [
            "z = self.view.custom.zoom or 1",
            f"self.view.custom.zoom = min({hi:g}, round(z * {step:g}, 4))"], enabled=f"{z} < {hi:g}")])


def toolbar_node(color: bool = True) -> dict:
    """The page's toolbar. The Color toggle is on a page whose pipes carry a medium only (`color`); the zoom
    controls are on every diagram page."""
    def toggle(name, label, prop):
        return pv.node("ia.input.button", name, pv.fpos(shrink=0, basis="auto"), {
            "text": label, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "32px",
                                     "padding": "0 8px"}},
            prop_config={"props.style.classes": pv.bind(pv.expr(
                f"if({{view.custom.{prop}}}, 'cadre/button/selected cadre/font/button', 'cadre/button/flat cadre/font/button')"))},
            events=pv.on_action([f"self.view.custom.{prop} = not self.view.custom.{prop}"]))
    toggles = ([toggle("Color", "Color", "colorMode")] if color else []) + [
        toggle("IdTag", "ID-tag", "showTag"), toggle("Readout", "Readout", "showReadout")]
    return pv.node("ia.container.flex", "UserToolbar", pv.fpos(basis="48px", shrink=0), {
        "direction": "row", "alignItems": "center",
        "style": {"classes": "cadre/surface/card", "gap": "4px", "padding": "0 8px", "margin": "0 0 8px 8px",
                  "alignSelf": "flex-start"}},
        children=[*toggles, zoom_controls()])


def diagram_screen(desc: dict, contracts: dict, rep: Report) -> tuple[dict, dict]:
    scr = desc["screen"]
    W, H = scr["width"], scr["height"]
    tag_root = desc.get("tagRoot", "")
    toolbar = bool(desc.get("toolbar", True))
    kids = [section_node(s) for s in desc.get("sections", [])]
    kids += [text_label(t) for t in desc.get("labels", []) if "emphasis" not in t]   # (emphasised: `parts`, GP-12)
    pipes, flow, info = pipes_svg(desc, contracts, rep)
    if pipes:
        kids.append(pipes)
    custom = {"colorMode": False, "showTag": tags_shown_at_start(desc), "showReadout": True}
    custom_cfg = {}
    limits = embed_limits(desc.get("symbols", []), contracts)
    # COB-159: lines, bars, trends, buttons; a pulse button may be the module's (W3) where the page is built for the module
    extra = parts.diagram_parts(desc, contracts, limits, rep,
                                module=RENDER["target"] == "module" and bool(module_props("cadre.ob.button")))
    kids += extra["under"]
    for s in desc.get("symbols", []):
        node, c_def, c_cfg = embed_symbol(s, contracts, tag_root, rep, toolbar=toolbar, limit=limits.get(s["id"]))
        kids.append(node)
        merge_custom(custom, c_def)
        custom_cfg.update(c_cfg)
    kids += extra["over"]
    merge_custom(custom, extra["custom"])
    custom_cfg.update(extra["custom_cfg"])
    diagram_node = pv.node("ia.container.coord", "Diagram", pv.fpos(shrink=0, basis=f"{H}px"),
                           {"style": {"overflow": "hidden", "width": f"{W}px", "minWidth": f"{W}px",
                                      "height": f"{H}px"}}, children=kids)
    # L4 (contract 3.1): the canvas scrolls and holds a sizer of the scaled size of the diagram, which holds the
    # diagram at `s = fit * zoom` (a CSS transform changes no layout size, so the sizer stands for it)
    sizer = pv.node("ia.container.flex", "Sizer", pv.fpos(shrink=0, grow=0, basis=f"{H}px"), {
        "direction": "column", "style": {"overflow": "hidden", "width": f"{W}px", "height": f"{H}px"}},
        children=[diagram_node])
    canvas_kids = [sizer]
    zoom = canvas_zoom_node()
    if zoom:
        canvas_kids.append(zoom)
    canvas = pv.node("ia.container.flex", "Canvas", pv.fpos(grow=1, basis="0px"), {
        "direction": "column", "style": {"overflow": "auto"}}, children=canvas_kids)
    scale = parts.apply_fit(diagram_node, canvas, desc, sizer)   # GP-10 and the zoom: scale the page
    merge_custom(custom, scale["custom"])
    custom_cfg.update(scale["custom_config"])
    root_kids = [canvas] + ([toolbar_node(has_media(desc))] if toolbar else [])
    if FRAME["name"] == "asm":
        root_kids.append(search_panel())
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")}, children=root_kids)
    doc = pv.view(root, size={"width": W, "height": H}, custom=custom, custom_config=custom_cfg)
    return doc, {"flow": flow, "diagram": {k: v for k, v in info.items() if k != "expressions"},
                 "expressions": info["expressions"]}


# A cards page (wiki page 08 section 2.1). A row is as high as its tallest card needs, and a card needs its
# title, its body and the body's padding; the rows stand at the top of the page and a page taller than
# the viewport scrolls. The sizes below are those `card_node` and `flex_group` write.
CARD_TITLE, CARD_PAD, CARD_MARGIN, GROUP_GAP, LABEL_LINE = 40, 8, 8, 4, 16


def _px(v) -> float | None:
    """A flex basis in px (`"24px"`), or None for one that is not a length in px (none given, `auto`)."""
    if isinstance(v, str) and v.endswith("px"):
        try:
            return float(v[:-2])
        except ValueError:
            return None
    return None


def leaf_height(it: dict, contracts: dict) -> float | None:
    """The height a leaf of a card body needs: a line for a label, the embed of an automation symbol
    with its readout, the size the library states for any other kind with the leaf's flags
    (`library.block_size`). None for a kind the library lacks: a gap box has no size of its own."""
    if "kind" not in it:
        return LABEL_LINE
    kind = it["kind"].lower()
    c = contracts.get(view_of(it))
    if not c:
        return None
    if c.get("anchor") == "symbol-centre" and kind != "readout":
        return 48 + readout_extent(it, c)[1]
    return block_size(c, it.get("params", {}))[1]


def group_height(group: dict, contracts: dict) -> float | None:
    """The height the items of a group need, by the arithmetic of the flex container `flex_group` writes:
    across a row the tallest item; down a column the items and the gaps between them, where an item
    that grows takes its share of the space left, so the column is high enough for the item that needs
    the largest share. None when an item has no size of its own."""
    sized = []
    for it in group.get("items", []):
        h = group_height(it, contracts) if "items" in it else leaf_height(it, contracts)
        if h is None:
            return None
        sized.append((it, h))
    if not sized:
        return 0
    if group.get("direction", "row") == "row":
        return max(h for _it, h in sized)
    fixed, share, grows = GROUP_GAP * (len(sized) - 1), 0.0, 0.0
    for it, h in sized:
        nested = "items" in it
        basis = _px(it.get("basis", "0px" if nested else None))
        grow = it.get("grow", 1 if nested else 0) or 0
        if basis is None:          # no basis: the item is as high as its content
            basis = h
        fixed += basis
        if grow > 0:
            share, grows = max(share, (h - basis) / grow), grows + grow
    return fixed + share * grows


def card_height(card: dict, contracts: dict) -> float | None:
    """The height a card needs: its title, and its body with the padding beneath it; a card of `items`
    states its body's height itself. None when its body has an item with no size of its own."""
    title = CARD_TITLE if card.get("title") else 0
    if "body" not in card:
        return title + card["bodyHeight"] if "bodyHeight" in card else None
    body = group_height(card["body"], contracts)
    return None if body is None else title + body + CARD_PAD


def row_height(row: list, contracts: dict) -> int | None:
    """The height of a row of cards: its tallest card and the cards' margins. None when a card has no
    height of its own (a gap box in its body): the row then shares the height the page has left."""
    import math
    needs = [card_height(c, contracts) for c in row]
    if not needs or any(n is None for n in needs):
        return None
    return math.ceil(max(needs)) + 2 * CARD_MARGIN


def flex_group(group: dict, contracts: dict, tag_root: str, rep: Report, custom, custom_cfg,
               name: str = "Body") -> dict:
    """A card body as nested flex groups: a group is a flex container, a leaf is a library symbol
    (embedded by flex basis and grow), a label, or a counted gap box."""
    kids = []
    for i, it in enumerate(group.get("items", [])):
        pos = pv.fpos(basis=it.get("basis"), grow=it.get("grow"), shrink=1)
        if "items" in it:
            kids.append(flex_group(it, contracts, tag_root, rep, custom, custom_cfg, name=f"Group{i}"))
        elif "label" in it and "kind" not in it:
            kids.append(pv.node("ia.display.label", f"Label{i}", pos, {
                "text": it["label"], "style": {"classes": "cadre/font/label cadre/text/neutral"}}))
        else:
            view_path = view_of(it)
            c = contracts.get(view_path, {})
            natural = c.get("anchor") == "symbol-centre" and it["kind"].lower() != "readout"
            inner_pos = pv.fpos(basis="0px", grow=1) if not natural else pv.fpos(shrink=0)
            node, c_def, c_cfg = embed_symbol(dict(it, x=0, y=0, w=0, h=0), contracts, tag_root, rep,
                                              toolbar=False, pos=inner_pos if natural else pos)
            if node["type"] == "ia.display.view":
                node["props"]["useDefaultViewHeight"] = False
                node["props"]["useDefaultViewWidth"] = False
            if natural and node["type"] == "ia.display.view":
                ex, ey = readout_extent(it, c)
                node["props"]["style"] = {"width": f"{48 + ex}px", "height": f"{48 + ey}px"}
                node = pv.node("ia.container.flex", f"Cell{i}", pos, {
                    "direction": "column", "justify": "center", "alignItems": "center"}, children=[node])
            kids.append(node)
            merge_custom(custom, c_def)
            custom_cfg.update(c_cfg)
    return pv.node("ia.container.flex", name, pv.fpos(basis=group.get("basis", "0px"), grow=group.get("grow", 1)), {
        "direction": group.get("direction", "row"), "alignItems": "stretch",
        "justify": group.get("justify", "flex-start"), "style": {"gap": f"{GROUP_GAP}px"}}, children=kids)


def card_node(card: dict, contracts: dict, tag_root: str, rep: Report, custom, custom_cfg) -> dict:
    if "body" in card:
        body = flex_group(card["body"], contracts, tag_root, rep, custom, custom_cfg)
        body["props"]["style"]["padding"] = f"0 8px {CARD_PAD}px 8px"
        route = card.get("route")
        title = pv.node("ia.display.label", "Title", pv.fpos(basis=f"{CARD_TITLE}px", shrink=0), {
            "text": card.get("title", "") + ("  ›" if route else ""), "textStyle": {"textAlign": "center"},
            "style": {"classes": "cadre/font/body-active cadre/text/active", "justifyContent": "center",
                      **({"cursor": "pointer"} if route else {})}},
            events=pv.on_click([f"system.perspective.navigate('{route}')"]) if route else None)
        return pv.node("ia.container.flex", f"Card_{card['id']}",
                       pv.fpos(grow=card.get("grow", 1), basis=card.get("basis", "0px")), {
            "direction": "column", "style": {"classes": "cadre/surface/card", "margin": f"{CARD_MARGIN}px"}},
            children=([title] if card.get("title") else []) + [body])
    items = []
    for it in card.get("items", []):
        node, c_def, c_cfg = embed_symbol(it, contracts, tag_root, rep, toolbar=False)
        items.append(node)
        merge_custom(custom, c_def)
        custom_cfg.update(c_cfg)
    body = pv.node("ia.container.coord", "Body", pv.fpos(grow=1, basis="0px"),
                   {"mode": "percent", "style": {"overflow": "hidden"}}, children=items)
    title = pv.node("ia.display.label", "Title", pv.fpos(basis=f"{CARD_TITLE}px", shrink=0), {
        "text": card.get("title", ""), "textStyle": {"textAlign": "center"},
        "style": {"classes": "cadre/font/body-active cadre/text/active", "justifyContent": "center"}})
    return pv.node("ia.container.flex", f"Card_{card['id']}", pv.fpos(grow=1, basis="0px"), {
        "direction": "column", "style": {"classes": "cadre/surface/card", "margin": f"{CARD_MARGIN}px"}},
        children=([title] if card.get("title") else []) + [body])


def cards_screen(desc: dict, contracts: dict, rep: Report) -> tuple[dict, dict]:
    tag_root = desc.get("tagRoot", "")
    custom, custom_cfg = {}, {}
    rows, heights = [], []
    for r, row in enumerate(desc.get("rows", [])):
        # as high as its content needs, at the top of the page; a row with a gap box shares what is left
        need = row_height(row, contracts)
        heights.append(need)
        pos = pv.fpos(grow=1, basis="0px") if need is None else pv.fpos(basis=f"{need}px", grow=0, shrink=0)
        rows.append(pv.node("ia.container.flex", f"Row{r}", pos, {
            "direction": "row", "style": {"overflow": "hidden"}},
            children=[card_node(c, contracts, tag_root, rep, custom, custom_cfg) for c in row]))
    # rows of stated height may be taller than the viewport together: the page then scrolls. A row that
    # shares the height left keeps the page at the viewport, and the root hidden (GF-09).
    scroll = bool(heights) and all(h is not None for h in heights)
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column",
                                                      "style": {"overflow": "auto" if scroll else "hidden",
                                                                "padding": "4px"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")},
                   children=rows + ([search_panel()] if FRAME["name"] == "asm" else []))
    scr = desc["screen"]
    doc = pv.view(root, size={"width": scr.get("width", 1600), "height": scr.get("height", 852)},
                  custom=custom, custom_config=custom_cfg)
    return doc, {}


def item_positions_percent(desc: dict) -> None:
    """Card items are written in card pixels by the descriptor; the card body is a percent
    container, so positions are converted to fractions of the card body."""
    for row in desc.get("rows", []):
        for card in row:
            if "body" in card:
                continue
            bw, bh = card["bodyWidth"], card["bodyHeight"]
            for it in card.get("items", []):
                it["_pct"] = (it["x"] / bw, it["y"] / bh, it["w"] / bw, it["h"] / bh)


def build_screen(desc: dict, contracts: dict) -> tuple[dict, dict]:
    rep = Report()
    layout = desc["screen"].get("layout", "diagram")
    if layout == "diagram":
        doc, info = diagram_screen(desc, contracts, rep)
    else:
        parts.check(desc, rep)   # page parts and `fit` are for a diagram
        item_positions_percent(desc)
        for row in desc.get("rows", []):
            for card in row:
                for it in card.get("items", []):
                    if "_pct" in it:
                        x, y, w, h = it.pop("_pct")
                        it["x"], it["y"], it["w"], it["h"] = x, y, w, h
        doc, info = cards_screen(desc, contracts, rep)
    alert_poll(doc)
    info.update(rep.as_dict())
    return doc, info


TYPE_DEFAULT = {"Boolean": False, "String": ""}   # every other type of a device model is a number


def tags_document(descs: list[dict], devices: dict | None = None) -> dict | None:
    """Memory tags for every bound member, typed from the library contract's parameter
    default, and for every device the members of its kind's faceplate (FACEPLATE_MEMBERS), or,
    for a device the device model names, exactly the members the model lists, with its types.
    Nothing else is written: no member is invented beyond the descriptor, the contract and the model.
    Each descriptor's members sit under its own `tagRoot`; roots that share a prefix share
    folders. A tag name cannot contain '/' (GF-11), so every path segment is a folder."""
    contracts = load_contracts()
    leaves: dict[tuple, tuple] = {}   # full path (segments) -> (dataType, value)
    provider_roots = set()
    known = model_devices(devices)

    for desc in descs:
        root = desc.get("tagRoot")
        if not root or desc.get("tagModel") == "external":
            continue
        provider_roots.add(root.split("]")[0].strip("["))
        base = [x for x in root.split("]")[-1].split("/") if x]
        values = desc.get("tagValues", {})
        for s in descriptor_items(desc):
            c = contracts.get(view_of(s), {"params": {}})
            for k, member in s.get("bind", {}).items():
                if member.startswith("["):
                    continue
                default = c["params"].get(k, s.get("params", {}).get(k))
                dtype = "Boolean" if isinstance(default, bool) else (
                    "Float8" if isinstance(default, (int, float)) else "String")
                if k == "state" and s["kind"].lower() == "indicator":   # a lamp's state of any type (L5)
                    dtype, default = state_default(s)
                val = values.get(member, s.get("params", {}).get(k, default))
                leaves[tuple(base + member.split("/"))] = (dtype, val)
            if drawn_folder(s):
                at = base + drawn_folder(s).split("/")
                model = known.get(tag_path(root, drawn_folder(s)))
                if model is not None:   # the members the device carries, no others, in the model's types
                    for m, spec in model["members"].items():
                        key = tuple(at + m.split("/"))
                        value = leaves.get(key, (None, TYPE_DEFAULT.get(spec["type"], 0)))[1]
                        leaves[key] = (spec["type"], values.get(f"{drawn_folder(s)}/{m}", value))
                    continue
                for m, (dt, dv) in FACEPLATE_MEMBERS.get(device_kind(s), {}).items():
                    if not device_folder(s):
                        break   # a plain symbol that opens a faceplate: only a device model gives that device members
                    # a member a symbol binds keeps the value given and takes the member's own type (a
                    # sequence's step number is an integer, where a parameter's default says a number)
                    key = tuple(at + [m])
                    leaves[key] = (dt, leaves[key][1] if key in leaves else dv)
    for desc in descs:   # the tags the page parts read or pulse (COB-159), under the descriptor's tag root
        root = desc.get("tagRoot")
        if root and desc.get("tagModel") != "external":
            base = [x for x in root.split("]")[-1].split("/") if x]
            for member, leaf in parts.tag_members(desc).items():
                leaves.setdefault(tuple(base + member.split("/")), leaf)
    if not leaves:
        return None
    tops = {k[0] for k in leaves}
    if len(tops) != 1 or len(provider_roots) != 1:
        raise ValueError(f"descriptors of one build must share one top tag folder and provider: {tops}, {provider_roots}")
    outer = {"name": tops.pop(), "tagType": "Folder", "tags": []}

    def folder(path):
        node = outer
        for seg in path:
            nxt = next((t for t in node["tags"] if t["name"] == seg and t["tagType"] == "Folder"), None)
            if not nxt:
                nxt = {"name": seg, "tagType": "Folder", "tags": []}
                node["tags"].append(nxt)
            node = nxt
        return node

    for path, (dt, val) in sorted(leaves.items()):
        v = bool(val) if dt == "Boolean" else (int(val) if dt.startswith("Int") else
                                              (float(val) if dt.startswith("Float") else str(val)))
        folder(path[1:-1])["tags"].append({"name": path[-1], "tagType": "AtomicTag", "valueSource": "memory",
                                           "dataType": dt, "value": v})
    return outer


def device_index(descs: list[dict], devices: dict | None = None) -> list[dict]:
    """Every device of the descriptors: its tag folder, kind, identifier and description, the
    dock contract of `cadre.hmi.select_device`. The alarm panel's row click opens a device's
    faceplate from it (COB-PLAN-01 WP4). A device drawn twice (a diagram symbol and an overview
    card) is listed once, with the first description given.

    With a device model, a device the model names takes its kind, identifier, description and unit
    from the model where the model gives them, and gains `sources` (the source patterns of its
    alarms, where the model lists them), `write` (the members a session may write), `members`
    (every member it carries) and, for a device with pulse members, `pulses` (each with the caption of
    its button, the member's name where the model gives none): what `cadre.hmi.device_sources`, the
    checked writes and `device_read` read. Without a model no entry carries them, and the functions
    keep the rules of a project without one. A build
    with a model also sets `session.custom.deviceModel` (`build_child`), so that a device of such a
    project whose entry has no `write` list may write nothing, where the list would otherwise fail open."""
    out: dict[str, dict] = {}
    for desc in descs:
        root = desc.get("tagRoot", "")
        for s in descriptor_items(desc):
            folder = drawn_folder(s)
            if not folder:
                continue
            path = tag_path(root, folder)
            entry = out.setdefault(path, {"folder": path, "kind": device_kind(s),
                                          "title": (s.get("params", {}).get("tag") if device_folder(s) else "") or folder.split("/")[-1],
                                          "label": "", "unit": ""})
            entry["label"] = entry["label"] or s.get("label", "")
            entry["unit"] = entry["unit"] or s.get("params", {}).get("unit", "")
    for path, model in model_devices(devices).items():
        entry = out.get(path)
        if entry is None and model.get("node"):   # a device of a node no page draws (L5): the node's lists know its sources
            entry = out[path] = {"folder": path, "kind": str(model["kind"]).lower(),
                                 "title": path.split("/")[-1], "label": "", "unit": ""}
        if entry is None:   # a device no page draws opens no faceplate
            continue
        for k in ("kind", "title", "label", "unit"):
            if model.get(k):
                entry[k] = model[k].lower() if k == "kind" else model[k]
        if "alarmSources" in model:
            entry["sources"] = list(model["alarmSources"])
        entry["write"] = sorted(m for m, spec in model["members"].items() if spec.get("access") == "write")
        entry["members"] = sorted(model["members"])
        pulses = [{"member": m, "caption": spec.get("caption") or m}
                  for m, spec in sorted(model["members"].items()) if spec.get("pulse")]
        if pulses:
            entry["pulses"] = pulses
        config = [{"member": m, "caption": spec["config"].get("caption") or m.split("/")[-1],
                   "unit": spec["config"].get("unit", ""), "minimum": spec["config"].get("minimum"),
                   "maximum": spec["config"].get("maximum"), "format": spec["config"].get("format", "0.0")}
                  for m, spec in sorted(model["members"].items()) if "config" in spec]
        if config:   # the Config rows (F010, COBD-045): `cadre.hmi.config_rows` and `configure` read them
            entry["config"] = config
        if model.get("faceplate"):   # the device's faceplate style (COBD-045): `cadre.hmi.faceplate_style`
            entry["faceplate"] = model["faceplate"]
        if model.get("modes"):   # ownership by mode (COBD-044): `cadre.hmi.ownership` reads them
            entry["modes"] = [{"value": int(m["value"]), "name": m["name"], "owner": m["owner"]}
                              for m in model["modes"]]
    return [out[k] for k in sorted(out)]


# The member a device's trend draws (framework.TREND_MEMBER): an instrument's value, a tank's level, a
# controller's process value, a sequence's step number; a controller's trend also draws its setpoint
# and its output.
TREND_KINDS = {"readout": "value", "instrument-field": "value", "instrument": "value", "tank": "level",
               "controller": "value", "sequence": "step", "generator": "engineSpeed"}
TREND_ALSO = {"controller": {"sp": "setpoint", "out": "output"}, "generator": {"fuelLevel": "fuel level"}}


def historised(tag_model: dict | None) -> set[str]:
    """The paths (`<folder>/<member>`, relative to the provider) of the tag model's members with
    history enabled."""
    out: set[str] = set()

    def walk(node, path):
        for t in node.get("tags", []):
            here = path + [t["name"]]
            if t.get("tagType") == "Folder":
                walk(t, here)
            elif t.get("historyEnabled"):
                out.add("/".join(here))
    if tag_model:
        walk({"tags": [tag_model]}, [])
    return out


def trend_index(descs: list[dict], tag_model: dict | None, devices: dict | None = None) -> list[dict]:
    """The trend page's members (COB-064), built from the descriptors: every device whose kind has a
    trend (an instrument's value, a tank's level, a controller's process value, setpoint and output,
    a sequence's step number) and whose member the tag model historises; none without a tag model,
    which alone says what is historised. A device model says it too: a device whose model entry
    carries `trend` lists exactly those members. Ordered as the device index; `cadre.hmi.trended`
    reads the list for a faceplate."""
    hist = historised(tag_model)
    known = model_devices(devices)
    out = []
    for d in device_index(descs, devices):
        main = TREND_KINDS.get(d["kind"])
        also = TREND_ALSO.get(d["kind"], {})
        rel = d["folder"].split("]", 1)[-1]
        if "trend" in known.get(d["folder"], {}):
            members = list(known[d["folder"]]["trend"])
        else:
            members = [m for m in ([main] if main else []) + list(also) if f"{rel}/{m}" in hist]
        for member in members:
            label = d["label"] if member == main else f"{d['label']} ({also.get(member, member)})".strip()
            out.append({"deviceId": d["folder"], "member": member, "kind": d["kind"], "title": d["title"],
                        "label": label,   # a level and an output are in per cent
                        "unit": "%" if member in ("level", "out", "fuelLevel") else d["unit"]})
    return out


def build_child(name: str, descs: list[dict], app_name: str, alarm_scope: str = "*",
                render: str = "stock", tag_model: dict | None = None,
                devices: dict | None = None, faceplate: str = "openbridge",
                faceplate_mode: str = "dock", parent: str = par.PARENT,
                frame: str = "openbridge") -> tuple[pv.Project, dict]:
    if frame not in navigation.FRAMES:
        raise ValueError(f"frame {frame!r}: one of {navigation.FRAMES}")
    if frame == "asm" and (bad := navigation.frame_errors(descs)):
        raise ValueError("; ".join(bad))
    RENDER["target"] = render
    RENDER["devices"] = model_devices(devices)
    FRAME["name"] = frame
    contracts = load_contracts()
    child = pv.Project(name, f"Cadre HMI {app_name}", parent=parent,
                       description="Generated by Cadre-Sandbox-OpenBridge tools/hmi/screen.py")
    pages, nav, reports = {}, [], {}
    for desc in descs:
        scr = desc["screen"]
        doc, info = build_screen(desc, contracts)
        child.add_view(scr["view"], doc)
        pages[scr["route"]] = {"title": scr.get("title", ""), "viewPath": scr["view"]}
        if scr.get("nav", True):
            nav.append({"label": scr.get("navLabel", scr.get("title", scr["route"])), "path": scr["route"],
                        "icon": scr.get("icon", ""), "node": scr.get("node", "")})
        reports[scr["route"]] = info
    if render == "module":
        # the alarm lists of the module (COB-078): child views over the parent's stock ones
        for path, doc in framework.module_overrides().items():
            child.add_view(path, doc)
    parts.check_all(descs, reports, {d["folder"] for d in device_index(descs, devices)}, tag_model)
    trends = trend_index(descs, tag_model, devices)
    if trends:   # COB-064: the trend page, when the plant historises members of its devices
        pages["/trends"] = {"title": "Trends", "viewPath": "Framework/TrendsPage"}
        nav.append({"label": "Trends", "path": "/trends", "icon": "trend"})
    sp = par.session_defaults()
    sp["custom"]["nav"]["items"] = nav
    sp["custom"]["alarmScope"] = alarm_scope
    sp["custom"]["devices"] = device_index(descs, devices)
    sp["custom"]["hierarchy"] = hierarchy(descs, devices)   # the plant hierarchy (F033, COB-141)
    sp["custom"]["deviceModel"] = devices is not None   # `cadre.hmi._may`: then every device has a write list
    sp["custom"]["faceplateStyle"] = faceplate   # the project's default faceplate style (COBD-045)
    sp["custom"]["faceplateMode"] = faceplate_mode   # where a faceplate opens until the pin moves it
    sp["custom"]["trends"] = trends
    sp["custom"]["commands"] = parts.commands_index(descs)   # the pulse tags the page buttons may write (COB-159)
    if frame == "asm":   # the ASM frame (COB-160): its docks, pivot pages and the data its views read
        sp["custom"].update(navigation.session_custom(descs, tag_model, sp["custom"]["devices"], bool(trends), devices))
    child.set_session_props(sp)
    child.set_page_config(navigation.page_config(app_name, pages) if frame == "asm" else par.page_config(app_name, pages))
    return child, reports


# The key of the gates in the `--report` file. Every other key of the file is a route, and a route
# starts with "/" (the descriptor schema), so the key can never be one.
GATES_KEY = "gates"


def gate_record(g: dict) -> dict:
    """The gates of a build as the `--report` file states them: each gate's result as `gates.run`
    gave it, with a `warnings` list on every gate (empty where the gate has none), and `ok` for the
    whole. A tool proves "no warning" with `not any(v["warnings"] for v in report["gates"].values()
    if isinstance(v, dict))`."""
    return {k: ({**v, "warnings": list(v.get("warnings", []))} if isinstance(v, dict) else v) for k, v in g.items()}


def schema_errors(descs: list[dict], names: list[str]) -> list[str]:
    """Gate G0: every descriptor validates against schemas/screen-descriptor.schema.json."""
    import jsonschema
    schema = json.loads((ROOT / "schemas" / "screen-descriptor.schema.json").read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    out = []
    for d, n in zip(descs, names):
        for e in sorted(v.iter_errors(d), key=lambda e: list(e.path)):
            out.append(f"{n}: {'/'.join(map(str, e.path))}: {e.message[:160]}")
    return out


def devices_schema_errors(model: dict, name: str) -> list[str]:
    """Gate G0 for a device model: it validates against schemas/devices.schema.json."""
    import jsonschema
    schema = json.loads((ROOT / "schemas" / "devices.schema.json").read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    return [f"{name}: {'/'.join(map(str, e.path))}: {e.message[:160]}"
            for e in sorted(v.iter_errors(model), key=lambda e: [str(x) for x in e.path])]


def main() -> int:
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--project", required=True)
    ap.add_argument("--descriptor", action="append", default=[],
                    help="a screen descriptor, repeatable; required unless --component-test is given with --tag-root")
    ap.add_argument("--app-name", default="App")
    ap.add_argument("--out", default=str(ROOT / "build"))
    ap.add_argument("--report", default=None)
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--alarm-scope", default="*",
                    help="source path pattern of the alarms the frame shows, for example *cadre_hmi_wtp*")
    ap.add_argument("--tags-file", default=None,
                    help="an explicit tag model (folder JSON) imported before the project")
    ap.add_argument("--devices-file", default=None,
                    help="a device model (schemas/devices.schema.json): each device's members, the members "
                         "a session may write, its alarm sources and its historised members")
    ap.add_argument("--render", choices=["stock", "module"], default="stock",
                    help="module: draw pumps and tanks with the Cadre OpenBridge module (wiki page 12)")
    ap.add_argument("--faceplate", choices=list(framework.FACEPLATE_STYLES), default="openbridge",
                    help="the project's default faceplate style (COBD-045); a device model may set a device's own")
    ap.add_argument("--faceplate-mode", choices=list(library.FACEPLATE_MODES), default="dock",
                    help="where a session opens a faceplate until its pin moves it: the right dock or a popup")
    ap.add_argument("--frame", choices=list(navigation.FRAMES), default="openbridge",
                    help="asm: the ASM application frame (COB-160): navigation dock, crumb popups, global search, "
                         "page header, alarm banner and a floating faceplate for each device; the default is unchanged")
    ap.add_argument("--component-test", action="store_true",
                    help="add the component test page (route /component-test, a level 4 support page) generated from "
                         "the library catalogue (tools/hmi/testbench.py, wiki page 13 section 13): every kind with its "
                         "features, and test devices on memory tags in the tag root's folder _componentTest, "
                         "written to <out>/<project>.component-test-tags.json and imported with --deploy")
    ap.add_argument("--parent", default=par.PARENT,
                    help="the parent project the child inherits, built beside it in --out (COB-157)")
    ap.add_argument("--tag-root", default=None, metavar="[provider]folder",
                    help="with --component-test: the tag folder the page's test devices sit under; with it and no "
                         "--descriptor the page is built alone, from the catalogue (S10-B, B8 Table 109)")
    ap.add_argument("--write-descriptor", default=None, metavar="DIR",
                    help="with --component-test: write the page's descriptor to DIR/component-test.json, for gate "
                         "G11 and the walk")
    ap.add_argument("--write-devices", default=None, metavar="FILE",
                    help="with --component-test: write the device model of the build (the test devices beside the "
                         "devices file given, if any) to FILE, for gate G11 and the walk")
    a = ap.parse_args()
    if not a.descriptor and not (a.component_test and a.tag_root):
        print("--descriptor is required, unless --component-test is given with --tag-root")
        return 1
    if (a.tag_root or a.write_descriptor or a.write_devices) and not a.component_test:
        print("--tag-root, --write-descriptor and --write-devices go with --component-test")
        return 1
    descs = [json.loads(Path(d).read_text(encoding="utf-8")) for d in a.descriptor]
    names = list(a.descriptor)
    bench = None
    if a.component_test:   # the page is built from the catalogue and joins the set before the gates read it
        from hmi import library_profile, testbench
        roots = {d["tagRoot"] for d in descs if d.get("tagRoot")}
        if a.tag_root:
            if not re.fullmatch(r"\[[^\]]+\][^/].*[^/]", a.tag_root):
                print(f"--tag-root is [provider]folder, for example [default]cadre_hmi_x, not {a.tag_root!r}")
                return 1
            roots = {a.tag_root}
        if len(roots) != 1:
            print(f"--component-test needs the descriptors to share one tagRoot, not {sorted(roots)}")
            return 1
        bench = testbench.build(load_contracts(), library_profile.build(load_contracts(), a.parent), roots.pop(),
                                render=a.render)
        descs.append(bench.descriptor)
        names.append("<component test>")
    bad = schema_errors(descs, names)
    print("  G0_descriptor_schema  ", "PASS" if not bad else "FAIL")
    if bad:
        print("\n".join(bad[:20]))
        return 1
    devices = json.loads(Path(a.devices_file).read_text(encoding="utf-8")) if a.devices_file else None
    if devices is None and bench and not a.descriptor:   # the page alone: its test devices are the device model
        devices = {"schema": "cadre-hmi-devices/1", "tagRoot": bench.descriptor["tagRoot"], "devices": bench.devices}
    if devices is not None:
        bad = devices_schema_errors(devices, a.devices_file or "<component test>")
        print("  G0_devices_schema     ", "PASS" if not bad else "FAIL")
        if bad:
            print("\n".join(bad[:20]))
            return 1
    model = json.loads(Path(a.tags_file).read_text(encoding="utf-8")) if a.tags_file else None
    if bench:   # the test devices join the device model and the tag model the gates read, where the project has them
        devices, model = bench.extend_devices(devices), bench.extend_tags(model)
        print("  component test:", *bench.notes)
        if a.write_descriptor:   # what G11 and the walk read of the page, written as generated
            target = Path(a.write_descriptor) / "component-test.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(bench.descriptor, indent=1) + "\n", encoding="utf-8", newline="\n")
        if a.write_devices and devices is not None:
            Path(a.write_devices).parent.mkdir(parents=True, exist_ok=True)
            Path(a.write_devices).write_text(json.dumps(devices, indent=1) + "\n", encoding="utf-8", newline="\n")
    child, reports = build_child(a.project, descs, a.app_name, a.alarm_scope, a.render, tag_model=model,
                                 devices=devices, faceplate=a.faceplate, faceplate_mode=a.faceplate_mode,
                                 parent=a.parent, frame=a.frame)
    out = child.write(Path(a.out))
    if bench:   # the test tags, beside the project: `--deploy` imports them into the tag root, a gateway does the rest
        tags_out = Path(a.out) / f"{a.project}.component-test-tags.json"
        tags_out.write_text(json.dumps(bench.tags, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print("wrote", tags_out)
    summary = {r: {"errors": v["errors"], "gaps": len(v["gaps"]),
                   "flow": {k: v.get("flow", {}).get(k) for k in ("gates", "pipes", "vectors", "mode", "ok")}}
               for r, v in reports.items()}
    print("wrote", out, len(child.files), "files")
    print(json.dumps(summary, indent=1))
    for r, v in reports.items():   # what a page shows that its descriptor does not state: said, never silent
        print("".join(f"  note: {r}: {n}\n" for n in v.get("notes", [])), end="")
    if a.report:
        Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.report).write_text(json.dumps(reports, indent=1, default=list), encoding="utf-8")
    if any(v["errors"] for v in reports.values()):
        print("CONTRACT ERRORS: not deploying")
        return 1
    from hmi import gates
    rep_path = Path(a.report) if a.report else None
    profile = None
    if devices is not None:   # gate G7 devices reads the kinds, members and write paths the library states
        from hmi import library_profile
        profile = library_profile.build(load_contracts(), a.parent)
    g = gates.run(out, Path(a.out) / a.parent, rep_path, tag_model=model, devices=devices,
                  symbols=device_symbols(descs, devices), profile=profile, alarm_scope=a.alarm_scope)
    for k, v in g.items():
        if isinstance(v, dict):
            note = f"  {v['devices']} devices, {v['symbols']} device symbols" if k == "G7_devices" else ""
            print(f"  {k:22s} {'PASS' if v.get('ok') else 'FAIL'}{note}")
            if k == "G7_devices" and not v.get("ok"):
                print("\n".join("    " + x for x in v["problems"][:20]))
            if v.get("warnings"):   # of any gate: G5 (overlapping readout areas, a box too small), G7 devices
                print("\n".join("    warning: " + x for x in v["warnings"][:20]))
    if rep_path:   # the gates beside the routes, so a tool that must prove "no warning" needs no second call
        rep_path.write_text(json.dumps({**reports, GATES_KEY: gate_record(g)}, indent=1, default=list),
                            encoding="utf-8")
    if not g["ok"]:
        print("GATES FAIL: not deploying")
        return 1
    if a.deploy:
        from hmi import deploy
        print(deploy.ensure_trial())
        if a.tags_file:
            print("tag model", deploy.import_tags("default", "", json.loads(Path(a.tags_file).read_text(encoding="utf-8"))))
        tags = tags_document(descs, devices)
        if tags:
            print("tags", deploy.import_tags("default", "", tags))
        if bench:   # into the project's tag root, so that no other tag of it is replaced
            provider, _, path = descs[-1]["tagRoot"].strip("[").partition("]")
            print("component test tags", deploy.import_tags(provider, path.strip("/"), bench.tags))
        print(deploy.import_project(child))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
