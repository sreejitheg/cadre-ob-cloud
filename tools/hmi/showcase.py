"""The showcase project `cadre_hmi_showcase`: every component of the Cadre HMI Components module on a page of its
own group, each with an editor for every property, a live simulation and an event log.

The project is generated from three sources and states nothing that they do not:

  module/components.json       the components, their properties (type, default, enumeration, array items), their events
  module/CATALOGUE.md          the class of each component (the section it is in, symbol or glyph), its description
  tools/hmi/testbench.py       the samples of the component test page (`FRAME_SAMPLE`, `GLYPH_DATA`, `GLYPH_EXTRA`), which
                               are the presets of an array or object property, and the test devices of the faceplates

Each component is a card on a page (`Showcase/<Page>`, a coord container as the sample pages are): a header (the palette
title, the type id, the catalogue's description and a Live switch), a stage with the component, a grid of editors and, for
a component with events, an event log. The wiring, in view custom properties (GF-07, `custom.` keys only):

    custom.v_<card>_<prop>   the value of a property; its editor is bound to it both ways (property binding,
                             `binding-property.json`: `path`, `bidirectional`), and so is the component's property
    custom.s_<card>_<prop>   an array or object property: the name of the selected preset (a dropdown); the value above
                             is bound to it through a script transform that holds the presets
    custom.live_<card>       the Live switch: on, the live properties follow the simulation (an expression over `now()`,
                             or the device's own tags on the device page), off they follow their editors
    custom.log_<card>        the event log: the component's event handlers write a line to it (GF-37)
    custom.tick              `toMillis(now(1000))`, which the simulated arrays (trends, charts) are scripted from

The device page's components are the devices of the component test page, bound to memory tags of the project's own
folder `_componentTest` (their faceplates open as on the samples); gate G11 reads the page's descriptor
(`devices_descriptor`) and its device model.

Usage:
    python tools/hmi/showcase.py --out build [--deploy] [--write-descriptor DIR] [--write-devices FILE]
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
from pathlib import Path

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import framework, library, library_profile, navigation, obframe, pv, screen, testbench  # noqa: E402
    from hmi import parent as par  # noqa: E402
else:
    from . import framework, library, library_profile, navigation, obframe, pv, screen, testbench
    from . import parent as par

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "module" / "components.json"
CATALOGUE = ROOT / "module" / "CATALOGUE.md"
PROJECT = "cadre_hmi_showcase"
TAG_ROOT = f"[default]{PROJECT}"
PAGE_W = 1400                    # px: the width of every page
MARGIN, GAP = 12, 12             # px: the page margin and the space between cards
CARD_W = PAGE_W - 2 * MARGIN
PAD = 12                         # px: inside a card
HEAD_H = 56                      # px: the header of a card (title, id and description)
CELL_W, CELL_H = 232, 56         # px: an editor and the space it takes (label 16, input 32)
EDIT_W = 220                     # px: the width of an input
SIDE_MAX = 520                   # px: a stage wider than this puts the editors below it
MAX_PAGE = 12                    # a group of more components than this is split
LOG_H = 176                      # px: the event log
SCRIPT_LINE = "# GF-37: a component event runs this script on the gateway; its payload is the object `event`"

# The devices of the device page: the component, the test device of the component test page (`testbench.device_specs`),
# the descriptor kind and the parameters the page's symbol states (as `testbench.DEVICE_ROW` and `devices_block` do).
DEVICES = [
    ("pump", "TB_PUMP", "pump", {"hasTag": True, "tag": "P-001", "hasSpeed": True}),
    ("tank", "TB_TANK", "tank", {"tag": "T-001", "value": 62}),
    ("motor", "TB_MOTOR", "motor", {"hasTag": True, "tag": "M-001", "hasSpeed": True}),
    ("fan", "TB_FAN", "fan", {"hasTag": True, "tag": "F-001", "hasSpeed": True}),
    ("valve", "TB_VALVE", "valve", {"hasTag": True, "tag": "XV-001"}),
    ("analogvalve", "TB_AVALVE", "analogvalve", {"hasTag": True, "tag": "FV-001", "value": 50}),
    ("damper", "TB_DAMPER", "damper", {"hasTag": True, "tag": "D-001"}),
    ("switch", "ALM_HIGH", "switch", {"hasTag": True, "tag": "HIGH", "deviceKind": "indicator"}),
    ("generator", "TB_GEN", "generator", {"picture": "symbol", "hasTag": True, "tag": "GEN-1"}),
    ("readout", "TB_READOUT", "readout", {"hasTag": True, "tag": "PT-001", "unit": "bar"}),
    ("instrumentfield", "TB_FIELD", "instrument-field", {"label": "Temp", "unit": "degC", "format": "#,##0.0"}),
]
DEVICE_IDS = {c: (ident, kind, params) for c, ident, kind, params in DEVICES}

# Alert records of our own, in the form of the package `Alert` (scripts.alert_record): the samples of the alert lists.
T0 = 1767258000000
ALERT_SAMPLE = [
    {"id": "A-1001", "tagId": "P-101", "source": "Pump P-101", "text": "Bilge level very high", "type": "level-critical",
     "time": T0, "acknowledged": False, "active": True, "shelved": False},
    {"id": "A-1002", "tagId": "T-201", "source": "Tank T-201", "text": "High level", "type": "alarm",
     "time": T0 + 180000, "acknowledged": {"acknowledgedBy": "operator", "acknowledgedAt": T0 + 240000}, "active": True,
     "shelved": False},
    {"id": "A-1003", "tagId": "F-3", "source": "Filter F-3", "text": "Differential pressure rising", "type": "warning",
     "time": T0 + 420000, "acknowledged": False, "active": {"rectifiedTime": T0 + 600000}, "shelved": False},
    {"id": "A-1004", "tagId": "K-2", "source": "Fan K-2", "text": "Vibration above normal", "type": "caution",
     "time": T0 + 900000, "acknowledged": False, "active": True, "shelved": False},
]
FALLBACK = {   # presets for an array no sample of the component test page states: (property, name, value)
    "alerts": [("four alerts", ALERT_SAMPLE), ("one alert", ALERT_SAMPLE[:1])],
    "selectedIds": [("first alert", ["A-1001"]), ("two alerts", ["A-1001", "A-1002"])],
}


# ---------------------------------------------------------------------------------------
# The catalogue
# ---------------------------------------------------------------------------------------
def components() -> dict:
    return json.loads(COMPONENTS.read_text(encoding="utf-8"))


def catalogue() -> dict[str, dict]:
    """The components in the order of `module/CATALOGUE.md`: id -> {section, class, kind, title, description}. The class is
    `symbol`, `glyph`, `frame` or `library` (a component that draws a library kind) or `view` (placed by a view); the kind is
    the descriptor kind or None."""
    comps = components()
    out: dict[str, dict] = {}
    section, cur = "", None
    lines = CATALOGUE.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if m := re.match(r"## \d+\. (.*)$", line):
            section = m.group(1)
        elif m := re.match(r"### (cadre\.ob\.\w+)$", line):
            cur = m.group(1)
            if cur not in comps:
                cur = None
                continue
            text = next((x for x in lines[i + 1:] if x.strip()), "")
            title = comps[cur]["title"]
            out[cur] = {"section": section, "title": title, "class": "view", "kind": None,
                        "description": (text[len(title) + 2:] if text.startswith(title + ". ") else text).replace("`", "")}
        elif cur and (m := re.match(r"\* Descriptor kind: (.*)$", line)):
            kind = re.match(r"`([^`]+)`", m.group(1))
            out[cur]["kind"] = kind.group(1) if kind else None
            rest = m.group(1)
            out[cur]["class"] = ("library" if "library kind" in rest else "symbol" if "(symbol)" in rest else
                                 "glyph" if "(glyph)" in rest else "frame" if "(frame component)" in rest else "view")
    missing = sorted(set(comps) - set(out))
    if missing:
        raise ValueError(f"CATALOGUE.md lacks components: {missing}")
    return out


def chunks(items: list, size: int = MAX_PAGE) -> list[list]:
    """Equal parts of at most `size` (the first parts the longer), in order."""
    n = math.ceil(len(items) / size)
    each, extra = divmod(len(items), n)
    out, at = [], 0
    for i in range(n):
        take = each + (1 if i < extra else 0)
        out.append(items[at:at + take])
        at += take
    return out


def is_pipe(cid: str) -> bool:
    return cid.startswith("cadre.ob.pipe") or cid == "cadre.ob.bus"


def pages(cat: dict | None = None) -> list[dict]:
    """The pages: the catalogue's sections, a section of more than MAX_PAGE components split, the module-only kinds
    separated into symbols, pipes (the nine line elements and the bus) and the other glyphs. Stable for a given catalogue."""
    cat = cat or catalogue()
    groups: list[tuple[str, str, list[str]]] = []   # (slug, title, components)

    def add(slug: str, title: str, ids: list[str]):
        if not ids:
            return
        if len(ids) > MAX_PAGE + 1:
            parts = chunks(ids)
            for i, part in enumerate(parts, 1):
                groups.append((f"{slug}-{i}", f"{title} {i} of {len(parts)}", part))
        else:
            groups.append((slug, title, ids))
    sections: dict[str, list[str]] = {}
    for cid, c in cat.items():
        sections.setdefault(c["section"], []).append(cid)
    for name, ids in sections.items():
        low = name.lower()
        if "module-only" in low:
            add("symbols", "Electrical symbols", [i for i in ids if cat[i]["class"] == "symbol"])
            add("glyphs", "Glyphs", [i for i in ids if cat[i]["class"] == "glyph" and not is_pipe(i)])
            add("pipes", "Pipes and bus", [i for i in ids if is_pipe(i)])
        elif "device" in low:
            add("devices", "Devices", ids)
        elif "chart" in low:
            add("charts", "Charts and bars", ids)
        elif "frame" in low:
            add("frame", "Frame components", ids)
        elif "alarm" in low:
            add("alarms", "Alarm lists and zoom", ids)
        else:
            add(re.sub(r"\W+", "-", low).strip("-"), name, ids)
    out = []
    for i, (slug, title, ids) in enumerate(groups):
        out.append({"id": slug, "title": title, "route": "/" if i == 0 else f"/{slug}",
                    "view": "Showcase/" + "".join(w.capitalize() for w in slug.split("-")), "components": ids})
    return out


def view_paths(con: dict | None = None) -> list[str]:
    """The library's embedded symbol views, in the order of the contracts: every view of a library kind (the symbols and the
    blocks, the instrument views and the parts), not the faceplates and the frame's views (kind `framework`)."""
    con = con or screen.library_contracts()
    return [p for p, c in con.items() if c.get("kind") not in (None, "framework")]


def view_pages(con: dict | None = None) -> list[dict]:
    """The pages of the library views: the paths in two parts at most MAX_PAGE each (the parent's views, `cadre_hmi_base`)."""
    paths = view_paths(con)
    parts = chunks(paths)
    return [{"id": f"views-{i}", "title": f"Library views {i} of {len(parts)}", "route": f"/views-{i}",
             "view": f"Showcase/Views{i}", "components": part, "kind": "views"} for i, part in enumerate(parts, 1)]


def view_enums(contract: dict) -> dict[str, tuple]:
    """The enumerations of a library view's string parameters. A contract holds defaults only, so these are the library's own
    tables: the readout sides the contract lists, the variants and the alert and badge values the component test page draws
    (`testbench`, `library.CONTROL_BADGES`)."""
    return {"readoutPosition": tuple(contract.get("readoutExtent") or testbench.POSITIONS), "variant": testbench.VARIANTS,
            "alertFrameStatus": testbench.ALERT_STATUS, "alertFrameMode": testbench.ALERT_MODE,
            "badgeInterlock": ("none",) + testbench.BADGE_INTERLOCK, "badgeCommandLocked": ("none", testbench.BADGE_LOCKED),
            "badgeControl": ("none",) + tuple(library.CONTROL_BADGES)}


def view_comp(path: str, contract: dict) -> tuple[dict, dict]:
    """A library view as the cards see a component: (the component, the catalogue entry). Its scalar parameters are its
    properties (boolean, number, string with the enumerations above; a null default is a nullable number, as the range bar's
    limits are); a parameter that holds a list or an object stays stated in the view, as the samples state it."""
    enums = view_enums(contract)
    props, static = {}, {}
    for name, d in contract["params"].items():
        if isinstance(d, bool):
            t = {"type": "boolean"}
        elif isinstance(d, (int, float)):
            t = {"type": "number"}
        elif isinstance(d, str):
            t = {"type": "string"}
            if name in enums:
                t["enum"] = list(dict.fromkeys([d, *enums[name]]))
        elif d is None:
            t = {"type": ["number", "null"]}
        else:
            static[name] = d
            continue
        props[name] = {**t, "default": d}
    kind = contract["kind"]
    start = {}
    if contract.get("anchor") == "symbol-centre" and kind != "readout" and "hasTag" in props:
        start = {"hasTag": True, "tag": testbench.ident_of(kind)}
        if contract.get("statusMode") == "speed":
            start["hasSpeed"] = True
    comp = {"props": props, "static": static, "start": start, "defaultSize": {"width": contract["size"][0],
                                                                              "height": contract["size"][1]}}
    why = [f"anchor {contract['anchor']}"] if contract.get("anchor") else []
    why += [f"state {contract['state']}"] if contract.get("state") else []
    why += [f"status {contract['statusMode']}"] if contract.get("statusMode") else []
    title = path.split("/")[-1] + " (library view)"
    cat = {"title": title, "kind": None, "class": "view", "section": "Library views",
           "description": f"The parent's view of the kind {kind}: {', '.join(why) or 'its scalar parameters bound to the editors'}."}
    return comp, cat


# ---------------------------------------------------------------------------------------
# Properties, editors, presets, simulation
# ---------------------------------------------------------------------------------------
def short(cid: str) -> str:
    """The card's name: the component's short id, or `lib` and the path of a library view without its slash."""
    return "lib" + cid.replace("/", "") if "/" in cid else cid.split(".")[-1]


def types_of(p: dict) -> list[str]:
    t = p["type"]
    return list(t) if isinstance(t, list) else [t]


def editor_kind(p: dict) -> str:
    """The input a property gets: enum (dropdown), bool (toggle), number (numeric field), text (text field), preset (an
    array or object: a dropdown of named presets)."""
    t = types_of(p)
    if "array" in t or "object" in t:
        return "preset"
    if "enum" in p:
        return "enum"
    if set(t) <= {"boolean", "null"}:
        return "bool"
    if set(t) <= {"number", "null"}:
        return "number"
    return "text"


def pyrepr(v) -> str:
    """A Python literal for a JSON value (the script transforms hold the presets as literals)."""
    if isinstance(v, bool) or v is None:
        return repr(v)
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, list):
        return "[" + ", ".join(pyrepr(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{json.dumps(str(k))}: {pyrepr(x)}" for k, x in v.items()) + "}"
    raise TypeError(type(v))


def samples(kind: str | None) -> list[tuple[str, dict]]:
    """The named property sets the component test page states for a kind, base first (testbench tables)."""
    if not kind:
        return []
    out = []
    fs = testbench.FRAME_SAMPLE.get(kind)
    if fs:
        out.append(("sample", dict(fs["base"])))
        out += [(cap, dict(params)) for cap, params in fs["extra"]]
    data = testbench.GLYPH_DATA.get(kind)
    if data:
        out.append(("sample", dict(data)))
    out += [(cap, dict(params)) for cap, params in testbench.GLYPH_EXTRA.get(kind, [])]
    return out


# A component whose event source is not drawn in its base sample starts in the named case of the component test page (the
# toggletip's actions show with `hasActions`), so that its events can be fired as it stands.
EVENT_CASES = {"toggletip": "two actions"}


def initial_values(comp: dict, kind: str | None) -> dict:
    """The starting value of every property: the default, set by the component test page's sample where it states one."""
    props = comp["props"]
    vals = {p: copy.deepcopy(d.get("default")) for p, d in props.items()}
    for cap, params in samples(kind)[:2]:
        if cap == "sample":
            vals.update({k: copy.deepcopy(v) for k, v in params.items() if k in props})
    for cap, params in samples(kind):
        if EVENT_CASES.get(kind) == cap:
            vals.update({k: copy.deepcopy(v) for k, v in params.items() if k in props})
    alerts = props.get("alerts")
    if alerts and types_of(alerts) == ["array"] and not vals["alerts"]:
        vals["alerts"] = copy.deepcopy(ALERT_SAMPLE)   # the alert lists start with rows (their events fire from a row)
    data = props.get("data")
    if data and number_series(data.get("items") or {}) and "trend" in props.get("variant", {}).get("enum", []):
        vals.update({"variant": "trend", "data": copy.deepcopy(testbench.GLYPH_SERIES)})   # the series draws in the trend variant
    p = props.get("positioning")
    if p and "symbol" in p.get("enum", []) and comp["defaultSize"]["width"] <= 96 and comp["defaultSize"]["height"] <= 96:
        vals["positioning"] = "symbol"   # the 48 px symbol box of the samples (wiki 12): the readout lies outside it
    return vals


def number_series(items: dict) -> bool:
    return items.get("type") == "number"


def presets_of(comp: dict, kind: str | None, prop: str, init) -> dict[str, object]:
    """The named values of an array or object property: the starting value first, then the component test page's cases that
    state the property, and an empty value; a property no sample states gets a table of our own (`FALLBACK`) or, for a series
    of numbers, the test page's series."""
    out: dict[str, object] = {}

    def add(name: str, value):
        if any(value == v for v in out.values()):
            return
        base, n = name, 2
        while name in out:
            name, n = f"{base} {n}", n + 1
        out[name] = copy.deepcopy(value)
    empty = [] if types_of(comp["props"][prop]) == ["array"] else {}
    add("empty" if init == empty else "sample", init)
    for cap, params in samples(kind):
        if prop in params:
            add(cap, params[prop])
    for name, value in FALLBACK.get(prop, []):
        add(name, value)
    items = comp["props"][prop].get("items") or {}
    if number_series(items):
        add("rising series", testbench.GLYPH_SERIES)
        add("short series", testbench.GLYPH_SERIES[:3])
    add("empty", empty)
    return out


def wave(lo: float, hi: float, period_s: float, phase: float = 0.0, whole: bool = True) -> str:
    mid, amp = (hi + lo) / 2, (hi - lo) / 2
    core = f"{mid:g} + {amp:g} * sin(toMillis(now(1000)) / {period_s * 1000 / (2 * math.pi):.0f} + {phase:g})"
    return f"round({core})" if whole else f"({core})"


def live_expressions(cid: str, comp: dict) -> dict[str, str]:
    """The simulation of a component not bound to tags: expressions over `now()` for its state, alarm and level properties."""
    props, out = comp["props"], {}

    def has(name, *types):
        return name in props and set(types_of(props[name])) <= set(types) and "enum" not in props[name]
    for name, period in (("on", 6), ("open", 8)):
        if has(name, "boolean"):
            out[name] = f"floor(toMillis(now(1000)) / {period * 1000 // 2}) % 2 = 0"
    if has("alert", "boolean"):
        out["alert"] = "floor(toMillis(now(1000)) / 5000) % 4 = 3"
    for i, name in enumerate(("value", "speedInPercent", "speed", "level", "secondaryLevel", "secondaryValue")):
        if has(name, "number", "null") and name not in out:
            out[name] = wave(10, 90, 9 + 2 * i, phase=i * 0.7)
    if has("nAlerts", "number"):
        out["nAlerts"] = "floor(toMillis(now(1000)) / 3000) % 6"
    if cid == "cadre.ob.readoutblock" and "value" in out:
        out["value"] = wave(10, 90, 9, whole=False)
    return out


# The arrays a trend or chart draws from the clock: a script over `custom.tick` (shape of the sample series in testbench).
TICK = {
    "cadre.ob.areagraph": ("data", [
        "t = value / 1000.0", "days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']",
        "return [{'label': days[i], 'x': 1767225600000 + i * 600000, 'value': round(24 + 12 * math.sin(t / 5.0 + i * 0.9), 1)} for i in range(7)]"]),
    "cadre.ob.linegraph": ("data", [
        "t = value / 1000.0", "days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']",
        "return [{'label': days[i], 'x': 1767225600000 + i * 600000, 'value': round(24 + 12 * math.sin(t / 5.0 + i * 0.9), 1)} for i in range(7)]"]),
    "cadre.ob.donutchart": ("data", [
        "t = value / 1000.0", "names = ['Pumps', 'Fans', 'Lighting', 'Galley']",
        "return [{'label': names[i], 'value': round(20 + 15 * math.sin(t / 6.0 + i * 1.3), 1)} for i in range(4)]"]),
    "cadre.ob.piechart": ("data", [
        "t = value / 1000.0", "names = ['Pumps', 'Fans', 'Lighting', 'Galley']",
        "return [{'label': names[i], 'value': round(20 + 15 * math.sin(t / 6.0 + i * 1.3), 1)} for i in range(4)]"]),
    "cadre.ob.polarchart": ("data", [
        "t = value / 1000.0",
        "return [{'label': 'Zone ' + str(i + 1), 'value': round(50 + 35 * math.sin(t / 6.0 + i * 1.1), 1)} for i in range(6)]"]),
    "cadre.ob.battery": ("data", ["t = value / 1000.0",
                                  "return [round(55 + 35 * math.sin(t / 5.0 + i * 0.8)) for i in range(7)]"]),
    "cadre.ob.tankatmospheric": ("data", ["t = value / 1000.0",
                                          "return [round(55 + 35 * math.sin(t / 5.0 + i * 0.8)) for i in range(7)]"]),
    "cadre.ob.radialbarchart": ("data", [
        "t = value / 1000.0", "return [round(55 + 35 * math.sin(t / 6.0 + i * 1.5)) for i in range(3)]"]),
}


# ---------------------------------------------------------------------------------------
# A page
# ---------------------------------------------------------------------------------------
class Page:
    """The nodes, view custom properties and bindings of one page, and what it holds (for the tests and the check)."""

    def __init__(self, spec: dict):
        self.spec = spec
        self.nodes: list[dict] = []
        self.custom: dict = {"tick": 0}
        self.cfg: dict = {"custom.tick": pv.bind(pv.expr("toMillis(now(1000))"))}
        self.y = MARGIN
        self.cards: dict[str, dict] = {}

    def put(self, node: dict):
        self.nodes.append(node)


def label_node(name: str, x, y, w, h, text: str, *, classes="cadre/font/label cadre/text/neutral", style=None,
               text_cfg: str | None = None) -> dict:
    cfg = {"props.text": pv.bind(pv.expr(text_cfg))} if text_cfg else None
    return pv.node("ia.display.label", name, pv.cpos(x, y, w, h),
                   {"text": text, "style": {"classes": classes, "whiteSpace": "nowrap", "overflow": "hidden",
                                            "textOverflow": "ellipsis", **(style or {})}}, prop_config=cfg)


def with_dom_id(node: dict) -> dict:
    """The node's name as its DOM id (`meta.domId`, as `parts.canvas` does), so that a check addresses it by id."""
    node["meta"]["domId"] = node["meta"]["name"]
    return node


def box_node(name: str, x, y, w, h, classes: str = "", style=None) -> dict:
    return pv.node("ia.container.flex", name, pv.cpos(x, y, w, h),
                   {"style": {**({"classes": classes} if classes else {}), **(style or {})}})


def binding_expr(b: dict) -> str:
    """The expression a component's own binding stands for (the device page keeps the tags and expressions of the samples)."""
    cfg = b["binding"]
    if cfg["type"] == "expr":
        return cfg["config"]["expression"]
    if cfg["type"] == "tag" and not cfg["config"].get("bidirectional"):
        return "{" + cfg["config"]["tagPath"] + "}"
    raise ValueError(f"no expression for the binding {cfg['type']}")


def option_list(values: list) -> list[dict]:
    return [{"value": v, "label": v if v != "" else "(empty)"} for v in values]


def editor_node(cid: str, prop: str, p: dict, ek: str, x: float, y: float, path: str, names: list | None) -> list[dict]:
    """The label and the input of one property, the input bound both ways to `view.custom.<path>`."""
    nodes = [label_node(f"l_{cid}_{prop}", x, y, EDIT_W, 16, prop)]
    iy = y + 18
    if ek in ("enum", "preset"):
        opts = option_list(p["enum"] if ek == "enum" else names)
        nodes.append(pv.node("ia.input.dropdown", f"e_{cid}_{prop}", pv.cpos(x, iy, EDIT_W, 32), {"options": opts},
                             prop_config={"props.value": pv.bind(pv.prop(f"view.custom.{path}", True))}))
    elif ek == "bool":
        nodes.append(pv.node("ia.input.toggle-switch", f"e_{cid}_{prop}", pv.cpos(x, iy, EDIT_W, 32), {},
                             prop_config={"props.selected": pv.bind(pv.prop(f"view.custom.{path}", True))}))
    elif ek == "number":
        nodes.append(pv.node("ia.input.numeric-entry-field", f"e_{cid}_{prop}", pv.cpos(x, iy, EDIT_W, 32), {},
                             prop_config={"props.value": pv.bind(pv.prop(f"view.custom.{path}", True))}))
    else:
        nodes.append(pv.node("ia.input.text-field", f"e_{cid}_{prop}", pv.cpos(x, iy, EDIT_W, 32), {},
                             prop_config={"props.text": pv.bind(pv.prop(f"view.custom.{path}", True))}))
    return nodes


def event_lines(cid: str, name: str) -> list[str]:
    """The handler of one component event: a line (time, event, payload) at the top of the card's log, six lines kept."""
    return [
        SCRIPT_LINE,
        "stamp = system.date.format(system.date.now(), 'HH:mm:ss')",
        "try:",
        "\tbody = system.util.jsonEncode(event)",
        "except:",
        "\tbody = unicode(event)",
        f"line = stamp + '  {name}  ' + body[:150]",
        f"old = self.view.custom.log_{cid}",
        "rows = [line] + ([r for r in old.split(chr(10)) if r] if old and not old.startswith('No event') else [])",
        f"self.view.custom.log_{cid} = chr(10).join(rows[:6])",
    ]


NO_EVENTS = "No events yet: use the component."
ZOOM_TARGET = "zoom_target"   # the DOM id of the box the canvas zoom card scales


def add_card(page: Page, cid: str, cat: dict, comp: dict, con: dict, devices: dict) -> None:
    """One component's card: header, stage, editors and log, and the page's custom properties and bindings for them."""
    c = short(cid)
    is_view = "/" in cid
    prefix = "props.params." if is_view else "props."
    kind = cat["kind"]
    props = comp["props"]
    vals = initial_values(comp, kind)
    vals.update(comp.get("start", {}))
    if cid == "cadre.ob.canvaszoom":
        vals["targetDomId"] = ZOOM_TARGET
    node = None
    live: dict[str, str] = live_expressions(cid, comp)
    own_custom, own_cfg = {}, {}
    box = None
    if c in DEVICE_IDS and devices:   # a device: the sample's own node (tags, alerts, the click that opens the faceplate)
        ident, dkind, params = DEVICE_IDS[c]
        sym = devices["symbols"][c]
        node, own_custom, own_cfg = screen.embed_symbol(sym, con, TAG_ROOT, screen.Report(), toolbar=False)
        if not node["type"].startswith("cadre.ob."):
            raise ValueError(f"{c}: the sample draws {node['type']}, not a module component")
        for k, v in node["props"].items():
            if k in props:
                vals[k] = v
        live = {}
        for key, b in (node.get("propConfig") or {}).items():
            if key.startswith("props.") and key[6:] in props:
                live[key[6:]] = binding_expr(b)
        box = node["position"]
    symbol_box_ = box is None and vals.get("positioning") == "symbol"
    w, h = (48, 48) if symbol_box_ else (box["width"], box["height"]) if box else (comp["defaultSize"]["width"],
                                                                                   comp["defaultSize"]["height"])
    if box is None and not symbol_box_ and c == "canvaszoom":
        w = h = 48
    tick = TICK.get(cid)
    sim_prop = None
    if tick:
        sim_prop = tick[0]
        live[sim_prop] = "{view.custom.sim_%s_%s}" % (c, sim_prop)
        page.custom[f"sim_{c}_{sim_prop}"] = []
        page.cfg[f"custom.sim_{c}_{sim_prop}"] = pv.bind(pv.prop("view.custom.tick"), [pv.script_transform(
            ["import math"] + tick[1])])
    # ---- the layout
    stage_w, stage_h = max(240, w + 48), max(168, h + 48)
    side = stage_w <= SIDE_MAX
    events = comp.get("events") or {}
    editors = [(p, d) for p, d in props.items()]
    if side:
        cols = 3 if events else 4
        ex = PAD + stage_w + PAD
        log_x = ex + cols * CELL_W
        rows = math.ceil(len(editors) / cols)
        body_h = max(stage_h, rows * CELL_H, (LOG_H + 24) if events else 0)
        card_h = HEAD_H + body_h + PAD
        stage_x, stage_y = PAD, HEAD_H
        ey = HEAD_H
        log_y, log_w = HEAD_H, CARD_W - log_x - PAD
    else:
        stage_w = min(stage_w, CARD_W - 2 * PAD)
        cols = 4 if events else 5
        ex = PAD
        log_x = ex + cols * CELL_W
        rows = math.ceil(len(editors) / cols)
        stage_x, stage_y = PAD, HEAD_H
        ey = HEAD_H + stage_h + PAD
        body_h = stage_h + PAD + max(rows * CELL_H, (LOG_H + 24) if events else 0)
        card_h = HEAD_H + body_h + PAD
        log_y, log_w = ey, CARD_W - log_x - PAD
    y0 = page.y
    X = MARGIN
    page.put(box_node(f"card_{c}", X, y0, CARD_W, card_h, "cadre/surface/card", {"borderRadius": "6px"}))
    page.put(label_node(f"t_{c}", X + PAD, y0 + 8, 360, 24, cat["title"], classes="cadre/font/body-active cadre/text/active"))
    page.put(label_node(f"i_{c}", X + PAD, y0 + 32, 300, 18, cid, style={"fontFamily": "monospace"}))
    page.put(label_node(f"d_{c}", X + 330, y0 + 32, CARD_W - 330 - 160, 18, cat["description"]))
    # ---- the properties: custom values, bindings
    bound, kinds = {}, {}
    live_names = sorted(live)
    for pname, d in editors:
        ek = editor_kind(d)
        kinds[pname] = ek
        vpath = f"v_{c}_{pname}"
        if ek == "preset":
            names = presets_of(comp, kind, pname, vals[pname])
            first = next(iter(names))
            page.custom[f"s_{c}_{pname}"] = first
            page.custom[vpath] = copy.deepcopy(names[first])
            page.cfg[f"custom.{vpath}"] = pv.bind(pv.prop(f"view.custom.s_{c}_{pname}"), [pv.script_transform(
                [f"P = {pyrepr(names)}", "return P.get(value)"])])
            bound[pname] = {"path": f"s_{c}_{pname}", "presets": list(names)}
            nodes = editor_node(c, pname, d, ek, 0, 0, f"s_{c}_{pname}", list(names))
        else:
            page.custom[vpath] = vals[pname]
            bound[pname] = {"path": vpath}
            nodes = editor_node(c, pname, d, ek, 0, 0, vpath, None)
        bound[pname]["kind"] = ek
        bound[pname]["live"] = pname in live
        bound[pname]["nodes"] = [n["meta"]["name"] for n in nodes]
        bound[pname]["_nodes"] = nodes
    # editors placed on the grid
    for i, (pname, d) in enumerate(editors):
        r, k = divmod(i, cols)
        for n in bound[pname].pop("_nodes"):
            with_dom_id(n)
            n["position"]["x"] = X + ex + k * CELL_W
            n["position"]["y"] = y0 + ey + r * CELL_H + (0 if n["meta"]["name"].startswith("l_") else 18)
            page.put(n)
        if pname in live:   # the label says the property follows the simulation while Live is on
            lab = next(n for n in page.nodes[-2:] if n["meta"]["name"] == f"l_{c}_{pname}")
            lab["props"]["text"] = f"{pname} (live)"
    # ---- the component
    prop_cfg = {}
    for pname in props:
        manual = pv.bind(pv.prop(f"view.custom.v_{c}_{pname}"))
        if pname in live:
            prop_cfg[f"{prefix}{pname}"] = pv.bind(pv.expr(f"if({{view.custom.live_{c}}}, ({live[pname]}), "
                                                           f"{{view.custom.v_{c}_{pname}}})"))
        else:
            prop_cfg[f"{prefix}{pname}"] = manual
    sx = X + stage_x + (stage_w - w) / 2
    sy = y0 + stage_y + (stage_h - h) / 2
    stage = box_node(f"stage_{c}", X + stage_x, y0 + stage_y, stage_w, stage_h, "",
                     {"border": "1px dashed var(--border-outline-color)", "borderRadius": "4px"})
    watch = [c]
    if cid == "cadre.ob.canvaszoom":
        # the zoom component draws nothing: it turns the wheel, a pinch and Ctrl with plus or minus over its target into
        # the `zoom` property (module/web/canvaszoom.js), which the view's own binding applies. The card gives it a target
        # of its own that the zoom scales, and binds `zoom` both ways so that a gesture moves the editor too.
        stage["props"]["style"].update({"display": "flex", "alignItems": "center", "justifyContent": "center"})
        stage["props"]["direction"] = "column"
        stage["children"] = [with_dom_id(pv.node(
            "ia.display.label", ZOOM_TARGET, pv.fpos(shrink=0, basis="80px"),
            {"text": "Zoom target: wheel, pinch or Ctrl and plus here",
             "style": {"classes": "cadre/font/label cadre/text/neutral", "width": "160px", "textAlign": "center",
                       "whiteSpace": "normal", "border": "1px solid var(--border-outline-color)", "borderRadius": "4px"}},
            prop_config={"props.style.transform": pv.bind(pv.expr(
                "'scale(' + toStr(coalesce({view.custom.v_%s_zoom}, 1)) + ')'" % c))}))]
        prop_cfg["props.zoom"] = pv.bind(pv.prop(f"view.custom.v_{c}_zoom", True))
        watch.append(ZOOM_TARGET)
    page.put(stage)
    if is_view:   # a library view embedded as the samples embed it: its parameters bound, the rest stated
        comp_node = with_dom_id(pv.node("ia.display.view", c, pv.cpos(sx, sy, w, h), {
            "path": cid, "params": copy.deepcopy(comp.get("static", {})), "style": {"overflow": "visible"}},
            prop_config=prop_cfg))
    else:
        comp_node = with_dom_id(pv.node(cid, c, pv.cpos(sx, sy, w, h), {}, prop_config=prop_cfg))
    if node is not None:   # the device's click that opens its faceplate, and the custom it reads
        for k in ("events", "custom"):
            if node.get(k):
                comp_node[k] = copy.deepcopy(node[k])
    if events:
        comp_node.setdefault("events", {}).setdefault("component", {})
        for ev in events:
            comp_node["events"]["component"][ev] = pv.script_handler(event_lines(c, ev))
        page.custom[f"log_{c}"] = NO_EVENTS
        page.put(label_node(f"lh_{c}", X + log_x, y0 + log_y, log_w, 16, "Event log"))
        page.put(with_dom_id(pv.node("ia.display.label", f"log_{c}", pv.cpos(X + log_x, y0 + log_y + 20, log_w, LOG_H),
                         {"style": {"classes": "cadre/font/label cadre/text/neutral", "whiteSpace": "pre-wrap",
                                    "overflow": "hidden", "fontFamily": "monospace", "fontSize": "11px",
                                    "alignItems": "flex-start", "justifyContent": "flex-start",
                                    "border": "1px solid var(--border-outline-color)", "borderRadius": "4px",
                                    "padding": "4px"}},
                         prop_config={"props.text": pv.bind(pv.prop(f"view.custom.log_{c}"))})))
    page.put(comp_node)
    if live:
        page.custom[f"live_{c}"] = True
        page.put(with_dom_id(pv.node("ia.input.toggle-switch", f"live_{c}", pv.cpos(X + CARD_W - 140, y0 + 12, 128, 32),
                                     {"label": {"text": "Live", "position": "right"}},
                                     prop_config={"props.selected": pv.bind(pv.prop(f"view.custom.live_{c}", True))})))
    screen.merge_custom(page.custom, own_custom)
    page.cfg.update(own_cfg)
    page.cards[c] = {"id": cid, "title": cat["title"], "editors": {k: {kk: vv for kk, vv in v.items()} for k, v in bound.items()},
                     "events": list(events), "live": live_names, "device": c in DEVICE_IDS and bool(devices),
                     "watch": watch, "y": y0, "height": card_h}
    page.y = y0 + card_h + GAP


def view_doc(page: Page) -> dict:
    H = page.y + MARGIN - GAP
    diagram = pv.node("ia.container.coord", "Diagram", pv.fpos(shrink=0, basis=f"{H}px"),
                      {"style": {"overflow": "hidden", "width": f"{PAGE_W}px", "minWidth": f"{PAGE_W}px",
                                 "height": f"{H}px"}}, children=page.nodes)
    sizer = pv.node("ia.container.flex", "Sizer", pv.fpos(shrink=0, grow=0, basis=f"{H}px"), {
        "direction": "column", "style": {"overflow": "hidden", "width": f"{PAGE_W}px", "height": f"{H}px"}},
        children=[diagram])
    canvas = pv.node("ia.container.flex", "Canvas", pv.fpos(grow=1, basis="0px"), {
        "direction": "column", "style": {"overflow": "auto"}}, children=[sizer])
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": framework.root_classes("cadre/surface/page")}, children=[canvas])
    doc = pv.view(root, size={"width": PAGE_W, "height": H}, custom=page.custom, custom_config=page.cfg)
    screen.alert_poll(doc)   # the device symbols' alarm states, polled as on the samples (F016)
    return doc


# ---------------------------------------------------------------------------------------
# The device page's devices, the project
# ---------------------------------------------------------------------------------------
def device_set(con: dict) -> dict:
    """The test devices of the device page: their specs, tag folder, device model and symbols (testbench)."""
    specs_all = testbench.device_specs(TAG_ROOT, "Showcase")
    idents = [d[1] for d in DEVICES]
    specs = {i: specs_all[i] for i in idents}
    folder = {"name": testbench.FOLDER, "tagType": "Folder",
              "tags": [{"name": i, "tagType": "Folder", "tags": copy.deepcopy(s["tags"])} for i, s in specs.items()]}
    model = {"schema": "cadre-hmi-devices/1", "tagRoot": TAG_ROOT, "devices": testbench.model_entries(specs)}
    symbols = {}
    for c, ident, dkind, params in DEVICES:
        sym = testbench.device_symbol(ident, ident, dkind, con, specs, x=0, y=0, params=params)
        if dkind == "switch":   # the alarm lamps of the test page: a switch symbol over an indicator device
            sym = {"id": ident, "kind": "switch", "x": 0, "y": 0, "w": 48, "h": 48, "device": f"{testbench.FOLDER}/{ident}",
                   "label": specs[ident]["label"], "params": dict(params), "bind": {"on": f"{testbench.FOLDER}/{ident}/state"}}
        symbols[c] = sym
    descriptor = {"schema": "cadre-hmi-screen/1", "tagRoot": TAG_ROOT, "tagModel": "external",
                  "screen": {"id": "Devices", "route": "/", "view": "Showcase/Devices", "title": "Devices", "nav": True,
                             "width": PAGE_W, "height": 1000, "layout": "diagram"},
                  "symbols": list(symbols.values())}
    return {"specs": specs, "folder": folder, "model": model, "symbols": symbols, "descriptor": descriptor}


def build_pages(cat: dict | None = None, con: dict | None = None) -> tuple[list[dict], dict, dict]:
    """(pages, views, devices): each page's spec with its cards, the view documents by path, the device set."""
    cat = cat or catalogue()
    comps = components()
    con = con or screen.load_contracts()
    screen.RENDER["target"] = "module"
    devices = device_set(con)
    screen.RENDER["devices"] = screen.model_devices(devices["model"])
    out, views = [], {}
    lib = screen.library_contracts()   # the parent's own views (`con` adds the module-only kinds' derived contracts)
    for spec in [{**p, "kind": "module"} for p in pages(cat)] + view_pages(lib):
        page = Page(spec)
        for cid in spec["components"]:
            if spec["kind"] == "views":
                comp, entry = view_comp(cid, lib[cid])
                add_card(page, cid, entry, comp, con, {})
            else:
                add_card(page, cid, cat[cid], comps[cid], con, devices if spec["id"] == "devices" else {})
        views[spec["view"]] = view_doc(page)
        out.append({**spec, "cards": page.cards, "height": page.y + MARGIN - GAP})
    return out, views, devices


def build_project(name: str = PROJECT, parent: str = par.PARENT, faceplate: str = "asm") -> tuple[pv.Project, dict]:
    """The project: the pages as views, the frame `ob` (the module frame), the navigation with one entry for a page and the
    session properties the faceplates read. Returns it with the model (pages, cards, editors, the device set)."""
    pgs, views, devices = build_pages()
    screen.FRAME["name"] = "ob"
    child = pv.Project(name, "Cadre HMI Showcase", parent=parent,
                       description="Generated by Cadre HMI Library tools/hmi/showcase.py")
    pages_cfg, nav = {}, []
    for p in pgs:
        child.add_view(p["view"], views[p["view"]])
        pages_cfg[p["route"]] = {"title": p["title"], "viewPath": p["view"]}
        nav.append({"label": p["title"], "path": p["route"], "icon": "placeholder", "node": ""})
    descs = [devices["descriptor"]]
    for path, doc in framework.module_overrides().items():   # the alarm lists of the module (COB-078)
        child.add_view(path, doc)
    sp = par.session_defaults()
    sp["custom"]["nav"]["items"] = nav
    sp["custom"]["alarmScope"] = f"*{name}*"
    sp["custom"]["devices"] = screen.device_index(descs, devices["model"])
    sp["custom"]["hierarchy"] = screen.hierarchy(descs, devices["model"])
    sp["custom"]["deviceModel"] = True
    sp["custom"]["faceplateStyle"] = faceplate   # the test devices carry modes, which the asm faceplate judges (G11 of the test page)
    sp["custom"]["faceplateMode"] = "dock"
    sp["custom"]["trends"] = []
    sp["custom"]["commands"] = []
    sp["custom"].update(obframe.session_custom())
    child.set_session_props(sp)
    child.set_page_config(obframe.page_config("Showcase", pages_cfg))
    model = {"project": name, "pages": pgs, "devices": devices}
    return child, model


def model_summary(model: dict) -> dict:
    kinds: dict[str, int] = {}
    events = 0
    for p in model["pages"]:
        for card in p["cards"].values():
            events += len(card["events"])
            for e in card["editors"].values():
                kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    return {"pages": {p["id"]: len(p["components"]) for p in model["pages"]}, "editors": kinds,
            "editorsTotal": sum(kinds.values()), "events": events}


# ---------------------------------------------------------------------------------------
# The command line
# ---------------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--out", default=str(ROOT / "build"))
    ap.add_argument("--name", default=PROJECT)
    ap.add_argument("--parent", default=par.PARENT)
    ap.add_argument("--faceplate", choices=list(framework.FACEPLATE_STYLES), default="asm",
                    help="the faceplate style of the devices (default asm, as the component test page is swept)")
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--export", default=None, metavar="DIR",
                    help="write the importable files to DIR: the showcase project and the parent as project zips "
                         "(`<name>-<module version>.zip`, the form the gateway's project import takes) and the device "
                         "tags (`cadre_hmi_showcase-tags.json`, imported into the folder cadre_hmi_showcase)")
    ap.add_argument("--write-descriptor", default=None, metavar="DIR",
                    help="write the device page's descriptor to DIR/showcase-devices.json (gate G11), and the model "
                         "(pages, cards, editors) to DIR/showcase-model.json (the functional check)")
    ap.add_argument("--write-devices", default=None, metavar="FILE", help="write the device model of the page (gate G11)")
    a = ap.parse_args()
    child, model = build_project(a.name, a.parent, a.faceplate)
    out = child.write(Path(a.out))
    summary = model_summary(model)
    print("wrote", out, len(child.files), "files")
    print(json.dumps(summary))
    if a.write_descriptor:
        d = Path(a.write_descriptor)
        d.mkdir(parents=True, exist_ok=True)
        (d / "showcase-devices.json").write_text(json.dumps(model["devices"]["descriptor"], indent=1) + "\n", encoding="utf-8")
        slim = {"project": model["project"], "pages": [{k: v for k, v in p.items()} for p in model["pages"]]}
        (d / "showcase-model.json").write_text(json.dumps(slim, indent=1) + "\n", encoding="utf-8")
    if a.write_devices:
        Path(a.write_devices).parent.mkdir(parents=True, exist_ok=True)
        Path(a.write_devices).write_text(json.dumps(model["devices"]["model"], indent=1) + "\n", encoding="utf-8")
    from hmi import gates
    descs = [model["devices"]["descriptor"]]
    tag_model = {"name": a.name, "tagType": "Folder", "tags": [model["devices"]["folder"]]}
    g = gates.run(out, Path(a.out) / a.parent, None, tag_model=tag_model, devices=model["devices"]["model"],
                  symbols=screen.device_symbols(descs, model["devices"]["model"]),
                  profile=library_profile.build(screen.load_contracts(), a.parent), alarm_scope=f"*{a.name}*")
    for k, v in g.items():
        if isinstance(v, dict):
            print(f"  {k:22s} {'PASS' if v.get('ok') else 'FAIL'}")
            for key in ("problems", "summary", "errors"):
                if not v.get("ok") and v.get(key):
                    print("\n".join("    " + str(x) for x in v[key][:12]))
            if v.get("warnings"):
                print("\n".join("    warning: " + x for x in v["warnings"][:10]))
    if not g["ok"]:
        print("GATES FAIL: not deploying")
        return 1
    if a.export:
        version = re.search(r'version = "([\d.]+)"', (ROOT / "module" / "build.gradle.kts").read_text(encoding="utf-8")).group(1)
        d = Path(a.export)
        d.mkdir(parents=True, exist_ok=True)
        parent_prj, _contracts = par.build_parent(a.parent)
        for prj in (child, parent_prj):
            (d / f"{prj.name}-{version}.zip").write_bytes(prj.zip_bytes())
        (d / f"{a.name}-tags.json").write_text(json.dumps(model["devices"]["folder"], indent=1, sort_keys=True) + "\n",
                                               encoding="utf-8")
        print("exported to", d)
    if a.deploy:
        from hmi import deploy
        print(deploy.ensure_trial())
        provider, _, path = TAG_ROOT.strip("[").partition("]")
        print("tags", deploy.import_tags(provider, path.strip("/"), model["devices"]["folder"]))
        print(deploy.import_project(child))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
