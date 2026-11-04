"""Page parts of a diagram (COB-159, the eng02 ASM gaps GP, GM and GG): what a descriptor adds to a diagram
page beside its symbols, pipes and sections.

  buttons   a label and one action: the pulse of a tag (asked first, administrator gated), a faceplate
            opened on a named tab, or a route
  bars      a range bar (`Parts/RangeBar`): a value on its track with the normal band and the limits
  trends    an embedded trend of one or two pens (`Parts/Trend`, `Parts/Trend2`, `Parts/Trend2Axes`)
  lines     a dashed line, or a line gated by a tag or a symbol: solid while energised, light and dashed
            while dead
  links     an icon (a chevron) that navigates to a route
  brackets  a thin bracket under or over a group, with its name
  wells     the liquid of a well that has level switches: filled to the highest mark reached, a lighter band
            up to the next mark

the keys a symbol takes: `bar` on a readout (a range bar beside it), `alarm` on an indicator (a fault
row: the lamp's alert frame follows the alarms on a tag), and the key `emphasis` of a label (bold while a
Boolean holds). The screen option `fit` scales a diagram page to its window. Wiki page 05, section "Page parts".

The module imports `screen` only inside functions: `screen` imports this module.
"""
from __future__ import annotations

import re

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import pv, library, framework, scripts  # noqa: E402
else:
    from . import pv, library, framework, scripts

PART_ARRAYS = ("buttons", "bars", "trends", "lines", "links", "brackets", "wells", "alarmPanels")   # the top-level arrays of a descriptor
SYMBOL_KEYS = ("bar", "alarm")                         # the keys a symbol takes
# L5: the keys of an indicator coloured by state (`states`, `stateDefault`), of a plain symbol that opens a device's faceplate
# (`faceplate`) and of one forced onto the library's view (`render`); they need no diagram layout, and `bind.state` is the
# indicator's state member
SYMBOL_MORE = ("states", "stateDefault", "faceplate", "render")
SYMBOL_PARAMS = ("badgeDuty", "outOfService")          # contract parameters the module's components lack
PULSE_PATH = scripts.constant("PULSE_PATH")            # W18: the write path of a page pulse
ACTIONS = ("pulse", "faceplate", "route")
BAR_PARAMS = {"value": 0, "min": 0, "max": 100, "normalLo": None, "normalHi": None, "loLimit": None,
              "hiLimit": None, "unit": "", "format": "#,##0.0", "vertical": False, "showValue": False}
BAR_NUMBERS = ("min", "max", "normalLo", "normalHi", "loLimit", "hiLimit")
BAR_THICKNESS, BAR_LENGTH, BAR_GAP = 10, 64, 4          # px: the default size of a bar beside a readout
TREND_VIEWS = {"one": "Parts/Trend", "same": "Parts/Trend2", "two": "Parts/Trend2Axes"}
LINE_DASH = "6 4"
LINK_ICON, LINK_SIZE = "chevron-right-google", 24
BRACKET_TICK, BRACKET_LABEL = 6, 16                      # px: the end ticks of a bracket and the height of its name
WELL_FILL, WELL_BAND = 0.5, 0.2                          # the opacity of the liquid and of the band to the next mark
FIT_TOP_DOCK, FIT_TOOLBAR = 48, 56                      # px the frame and the toolbar take of the viewport
# The faceplate dock pushes the page by its width while it is open; the library's scripts that open and close it keep
# `session.custom.faceplateDocked` (the viewport the fit reads does not change with a dock: gateway, 2026-10-24).
FIT_FACEPLATE_DOCK = 400
FIT_DOCKED = "coalesce({session.custom.faceplateDocked}, false)"
CANVAS_W, CANVAS_H = "{view.custom.canvasW}", "{view.custom.canvasH}"   # the measured canvas (module 0.4.1)
# The canvas zoom (L4, contract 3.1): the user's factor on top of the fit, 0.5 to 4, steps of 1.25 times.
ZOOM_MIN, ZOOM_MAX, ZOOM_STEP = 0.5, 4.0, 1.25
CANVAS_DOM_ID = "cadre-canvas"
ZOOM_VIEW = "{view.custom.zoom}"
SCALE_VIEW = "{view.custom.scale}"


def safe(name: str) -> str:
    """A part's id as a name an expression may use."""
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def quote(text: str) -> str:
    """A string literal of the expression language."""
    return "'" + str(text).replace("\\", "\\\\").replace("'", "\\'") + "'"


def present(desc: dict) -> bool:
    """Whether a descriptor uses a page part or a key of one."""
    return any(desc.get(k) for k in PART_ARRAYS) or any(
        k in s for s in desc.get("symbols", []) for k in SYMBOL_KEYS) or any(
        "emphasis" in t for t in desc.get("labels", []))


# ---------------------------------------------------------------------------------------
# Library views: the range bar and the embedded trends
# ---------------------------------------------------------------------------------------
def _label(name, pos, text_expr, classes, extra_cfg=None, style=None):
    return pv.node("ia.display.label", name, pos, {"style": {"classes": classes, "whiteSpace": "nowrap", **(style or {})}},
                   prop_config={"props.text": pv.bind(pv.expr(text_expr)), **(extra_cfg or {})})


def _spec_expression() -> str:
    """The range bar's parameters joined into the one text its elements are drawn from (a script transform
    splits it again; `scripts.PARTS_HMI.range_bar_elements`). A number is written by `toStr`, which keeps
    no locale; an absent one is empty."""
    names = ("value", "min", "max", "normalLo", "normalHi", "loLimit", "hiLimit")
    fields = [f"if(isNull({{view.params.{n}}}), '', toStr({{view.params.{n}}}))" for n in names]
    fields.append("toStr({view.params.vertical})")
    return " + '|' + ".join(fields)


def range_bar() -> tuple[dict, dict]:
    """`Parts/RangeBar` (shared contract 2.3): a value against its range, in the package tokens: the track,
    the normal band, a mark at each limit, the value marker (in the warning colour beyond a limit). Drawn as
    one `ia.shapes.svg` whose elements a script transform lays out from the parameters, so that the bar
    scales to any box: 100 by 10 along its length, high end at the top when `vertical`. A parameter that is
    null is absent (no band, no mark). `showValue` adds the value and its unit beside the bar."""
    bar = pv.node("ia.shapes.svg", "Bar", pv.fpos(grow=1, basis="0px"), {
        "viewBox": "0 0 100 10", "preserveAspectRatio": "none", "elements": []},
        prop_config={"props.elements": pv.bind(pv.expr(_spec_expression()), [pv.script_transform([
                         "return cadre.hmi.range_bar_elements(value)"])]),
                     "props.viewBox": pv.bind(pv.expr("if({view.params.vertical}, '0 0 10 100', '0 0 100 10')"))})
    text = _label("Value", pv.fpos(shrink=0, basis="auto"),
                  "numberFormat(coalesce({view.params.value}, 0), {view.params.format}) + if(len({view.params.unit}) > 0, ' ' + "
                  "{view.params.unit}, '')", "cadre/font/automation-label cadre/text/active",
                  {"position.display": pv.bind(pv.expr("{view.params.showValue}"))}, {"padding": "0 4px"})
    root = pv.node("ia.container.flex", "root", {}, {"direction": "row", "alignItems": "center",
                                                      "style": {"overflow": "hidden"}},
                   prop_config={"props.direction": pv.bind(pv.expr("if({view.params.vertical}, 'column', 'row')"))},
                   children=[bar, text])
    params = dict(BAR_PARAMS)
    doc = pv.view(root, params=params, param_dirs={k: "input" for k in params}, size={"width": BAR_LENGTH, "height": BAR_THICKNESS})
    return doc, {"view": "Parts/RangeBar", "kind": "rangebar", "params": params,
                 "size": [BAR_LENGTH, BAR_THICKNESS]}


TREND_PARAMS = {"title": "", "minutes": 10, "tag1": "", "label1": "", "unit1": "",
                "tag2": "", "label2": "", "unit2": ""}
TREND_SIZE = (340, 130)
SECOND_AXIS = {"name": "second", "alignment": "right", "tick": {"count": 5, "label": {"format": ".3~g"}}}


def _pen_cfg(n: int) -> dict:
    """`custom.pen<n>`: the tag history list of one pen, from its tag path (a list of path objects, never a
    path string, gate G7 history)."""
    return {f"custom.pen{n}": pv.bind(pv.expr(f"{{view.params.tag{n}}}"), [pv.script_transform([
        f"return [{{'path': value or '', 'alias': 'p{n}'}}]"])])}


def _history(n: int) -> dict:
    return pv.bind(pv.tag_history("{view.custom.pen%d}" % n, "{view.params.minutes}", "MIN"))


def trend_view(pens: int, second_axis: bool) -> tuple[dict, dict]:
    """An embedded trend: a title, the pens' labels with their units, and the stock time series chart over the
    last `minutes` minutes of the pens' tag history. One pen, two pens on the one value axis (their units
    agree), or two pens with an axis each at the left and the right (they differ). The pens' tags need
    history: see `history_needs`."""
    legend = ("{view.params.label1} + if(len({view.params.unit1}) > 0, ' (' + {view.params.unit1} + ')', '')"
              + (" + if(len({view.params.tag2}) > 0, '   ' + {view.params.label2} + "
                 "if(len({view.params.unit2}) > 0, ' (' + {view.params.unit2} + ')', ''), '')" if pens > 1 else ""))
    head = pv.node("ia.container.flex", "Head", pv.fpos(basis="20px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px"}}, children=[
        _label("Title", pv.fpos(shrink=0), "{view.params.title}", "cadre/font/label cadre/text/active"),
        _label("Legend", pv.fpos(grow=1), legend, "cadre/font/label cadre/text/neutral",
               style={"overflow": "hidden", "textOverflow": "ellipsis"})])
    extra = []
    if pens > 1:
        extra = [{"name": "p2", "binding": _history(2), "axis": "second" if second_axis else "value",
                  "visible": pv.bind(pv.expr("len({view.params.tag2}) > 0"))}]
    chart = framework.trend_chart(_history(1), None, column="p1", extra=tuple(extra))
    if second_axis:
        chart["props"]["plots"][0]["axes"].append(dict(SECOND_AXIS))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"padding": "4px", "gap": "2px"}},
                   prop_config={"props.style.classes": framework.root_classes("cadre/surface/card")},
                   children=[head, chart])
    custom = {f"pen{n}": [{"path": "", "alias": f"p{n}"}] for n in range(1, pens + 1)}
    custom_cfg = {}
    for n in range(1, pens + 1):
        custom_cfg.update(_pen_cfg(n))
    params = dict(TREND_PARAMS) if pens > 1 else {k: v for k, v in TREND_PARAMS.items() if not k.endswith("2")}
    key = "two" if second_axis else ("same" if pens > 1 else "one")
    doc = pv.view(root, params=params, param_dirs={k: "input" for k in params},
                  size={"width": TREND_SIZE[0], "height": TREND_SIZE[1]}, custom=custom, custom_config=custom_cfg)
    return doc, {"view": TREND_VIEWS[key], "kind": "trend", "params": params, "size": list(TREND_SIZE)}


def library_views() -> dict[str, tuple[dict, dict]]:
    """The views of the page parts, registered with the library's (`library.library_views`)."""
    return {"Parts/RangeBar": range_bar(),
            TREND_VIEWS["one"]: trend_view(1, False),
            TREND_VIEWS["same"]: trend_view(2, False),
            TREND_VIEWS["two"]: trend_view(2, True)}


def history_needs() -> dict:
    """What a pen's tag needs in an external tag model for the trend to draw it: the tag's history enabled
    on a history provider the gateway has, with the provider's name; a tag without it gives the chart an
    empty series (GF-53: history on a reference tag records, its source with no history keys records
    nothing). A generated test build writes memory tags without history, so its trends draw nothing."""
    return {"historyEnabled": True, "historyProvider": "<the gateway's history provider>",
            "sampleMode": "on change, or periodic (the chart interpolates between samples)"}


# ---------------------------------------------------------------------------------------
# Descriptor checks and indexes
# ---------------------------------------------------------------------------------------
def _screen():
    if __package__ in (None, ""):
        from hmi import screen
    else:
        from . import screen
    return screen


def command_tags(desc: dict) -> list[dict]:
    """The pulse commands a descriptor declares, each `{path, ms}` with the full tag path."""
    screen = _screen()
    root = desc.get("tagRoot", "")
    return [{"path": screen.tag_path(root, b["action"]["tag"]), "ms": int(b["action"].get("ms", 1000))}
            for b in desc.get("buttons", []) if b.get("action", {}).get("type") == "pulse"]


def commands_index(descs: list[dict]) -> list[dict]:
    """`session.custom.commands`: every pulse tag the descriptors declare, once, with its length. The
    library's `page_pulse` writes no other tag. The same tag with two lengths is an error (`check`)."""
    out: dict[str, dict] = {}
    for desc in descs:
        for c in command_tags(desc):
            out.setdefault(c["path"], c)
    return [out[k] for k in sorted(out)]


def tag_members(desc: dict) -> dict[str, tuple[str, object]]:
    """The tags the parts of a descriptor read or pulse, member -> (data type, test value), for the test tag
    document of a generated build (`screen.tags_document`): a bar's and a pen's number, a gate's and a pulse's
    Boolean, a fault row's Boolean. Nothing beyond what the parts name."""
    out: dict[str, tuple[str, object]] = {}
    values = desc.get("tagValues", {})
    for b in desc.get("buttons", []):
        a = b.get("action", {})
        if a.get("type") == "pulse":
            out[a["tag"]] = ("Boolean", bool(values.get(a["tag"], False)))
    for b in desc.get("bars", []):
        if isinstance(b.get("value"), str):
            out[b["value"]] = ("Float8", float(values.get(b["value"], 0)))
    for t in desc.get("trends", []):
        for p in t.get("pens", []):
            out[p["tag"]] = ("Float8", float(values.get(p["tag"], 0)))
    for ln in desc.get("lines", []):
        for g in _gates(ln):
            if "tag" in g:
                out[g["tag"]] = ("Boolean", bool(values.get(g["tag"], False)))
    for w in desc.get("wells", []):
        for m in w.get("marks", []):
            out[m["tag"]] = ("Boolean", bool(values.get(m["tag"], False)))
    for lb in desc.get("labels", []):
        if "tag" in lb.get("emphasis", {}):
            out[lb["emphasis"]["tag"]] = ("Boolean", bool(values.get(lb["emphasis"]["tag"], False)))
    for s in desc.get("symbols", []):
        if s.get("alarm") and not str(s["alarm"]).startswith("["):
            out.setdefault(s["alarm"], ("Boolean", bool(values.get(s["alarm"], False))))
    return out


def _gates(line: dict) -> list[dict]:
    g = line.get("gate")
    return [] if g is None else (g if isinstance(g, list) else [g])


def check(desc: dict, rep) -> None:
    """The errors of a descriptor's parts (generator checks, beside the schema's G0): a part on a cards page,
    a repeated id, a symbol key on a kind that cannot take it, a symbol referenced that is not there, a
    pulse length outside the library's range, a bar that cannot be placed."""
    screen = _screen()
    layout = desc.get("screen", {}).get("layout", "diagram")
    used = [k for k in PART_ARRAYS if desc.get(k)] + [f"symbol {k}" for s in desc.get("symbols", []) for k in SYMBOL_KEYS if k in s]
    used += ["label emphasis" for lb in desc.get("labels", []) if "emphasis" in lb]
    if layout != "diagram":
        if used or desc.get("screen", {}).get("fit"):
            rep.errors.append(f"page parts and fit are for a diagram layout; this page is {layout}: {sorted(set(used))}")
        return
    ids: set[str] = set()
    symbols = {s["id"]: s for s in desc.get("symbols", [])}
    for k in PART_ARRAYS:
        for p in desc.get(k, []):
            if p["id"] in ids:
                rep.errors.append(f"{k}: the id {p['id']!r} is used twice among the page parts")
            ids.add(p["id"])
            if p["id"] in symbols:
                rep.errors.append(f"{k}: the id {p['id']!r} is also a symbol's")
    for b in desc.get("buttons", []):
        a = b["action"]
        if b.get("render") == "module" and a["type"] != "pulse":
            rep.errors.append(f"button {b['id']}: `render: module` is for a pulse button; this action is {a['type']}")
        if a["type"] == "faceplate":
            sym, _folder = _device_of(desc, a["device"])
            if sym is None and not a.get("kind"):
                rep.errors.append(f"button {b['id']}: the faceplate action names {a['device']!r}, which is no symbol of "
                                  "the page; state its `kind`")
    for ln in desc.get("lines", []):
        for g in _gates(ln):
            if "symbol" in g and g["symbol"] not in symbols:
                rep.errors.append(f"line {ln['id']}: the gate names the symbol {g['symbol']!r}, which the page lacks")
            elif "symbol" in g and not _has_gate(symbols[g["symbol"]], screen):
                rep.errors.append(f"line {ln['id']}: the symbol {g['symbol']!r} has no state to gate on")
    for s in desc.get("symbols", []):
        if "alarm" in s and s["kind"].lower() != "indicator":
            rep.errors.append(f"{s['id']}: `alarm` is a key of an indicator; this symbol is a {s['kind']}")
        if "bar" in s:
            if s["kind"].lower() not in ("readout", "instrument-field"):
                rep.errors.append(f"{s['id']}: `bar` is a key of a readout or an instrument field; this symbol is a {s['kind']}")
            elif "value" not in s.get("bind", {}) and "value" not in s["bar"]:
                rep.errors.append(f"{s['id']}: `bar` needs the symbol to bind `value` (or the bar to name its own)")
    for lk in desc.get("links", []):
        if not (library.ICONS / f"{lk.get('icon', LINK_ICON)}.json").exists():
            rep.errors.append(f"link {lk['id']}: no library icon {lk.get('icon')!r}")
    for w in desc.get("wells", []):
        levels = [m["level"] for m in w["marks"]]
        if levels != sorted(set(levels)):
            rep.errors.append(f"well {w['id']}: the marks run from the lowest level up, each level once: {levels}")
    for lb in desc.get("labels", []):
        g = lb.get("emphasis", {})
        if "symbol" in g and g["symbol"] not in symbols:
            rep.errors.append(f"label {lb['id']}: the emphasis names the symbol {g['symbol']!r}, which the page lacks")
        elif "symbol" in g and not _has_gate(symbols[g["symbol"]], screen):
            rep.errors.append(f"label {lb['id']}: the symbol {g['symbol']!r} has no state to emphasise on")
    for b in desc.get("bars", []):
        if not isinstance(b.get("value"), str):
            rep.errors.append(f"bar {b['id']}: `value` names a tag member")
    for t in desc.get("trends", []):
        if not 1 <= len(t["pens"]) <= 2:
            rep.errors.append(f"trend {t['id']}: one or two pens, not {len(t['pens'])}")
    # a lone pulse tag with two lengths across the page
    seen: dict[str, int] = {}
    for c in command_tags(desc):
        if seen.setdefault(c["path"], c["ms"]) != c["ms"]:
            rep.errors.append(f"pulse {c['path']}: two lengths, {seen[c['path']]} and {c['ms']} ms")


def check_all(descs: list[dict], reports: dict, devices: set[str], tag_model: dict | None) -> None:
    """The checks that need every page: a faceplate button names a device some symbol of the set marks (a
    device no page draws opens no faceplate), one pulse tag has one length, and the pens' tags are
    historised in the tag model, said as a note where they are not."""
    screen = _screen()
    lengths: dict[str, int] = {}
    hist = screen.historised(tag_model) if tag_model else None
    for desc in descs:
        rep = reports.get(desc["screen"]["route"], {"errors": [], "notes": []})
        root = desc.get("tagRoot", "")
        for b in desc.get("buttons", []):
            a = b["action"]
            if a["type"] == "faceplate":
                _sym, folder = _device_of(desc, a["device"])
                path = screen.tag_path(root, folder)
                if path not in devices:
                    rep["errors"].append(f"button {b['id']}: {path} is no device of the page set (no symbol marks it `device`)")
        for c in command_tags(desc):
            if lengths.setdefault(c["path"], c["ms"]) != c["ms"]:
                rep["errors"].append(f"pulse {c['path']}: two lengths across the page set, {lengths[c['path']]} and {c['ms']} ms")
        if hist is not None:
            for t in desc.get("trends", []):
                for p in t["pens"]:
                    rel = screen.tag_path(root, p["tag"]).split("]", 1)[-1].lstrip("/")
                    if rel not in hist:
                        rep["notes"].append(f"trend {t['id']}: the tag model does not historise {rel}; the pen draws nothing "
                                            "until historyEnabled and historyProvider are set on it")


def _has_gate(sym: dict, screen) -> bool:
    c = screen.load_contracts().get(screen.KIND_VIEW.get(sym["kind"].lower(), ""), {})
    return bool(c.get("state"))


def _device_of(desc: dict, ref: str):
    """(symbol, folder) for a faceplate action's device: a symbol of the page by its id, or by its tag
    folder, else (None, ref): the reference is a folder under the tag root."""
    screen = _screen()
    for s in desc.get("symbols", []):
        folder = screen.device_folder(s)
        if folder and (s["id"] == ref or folder == ref):
            return s, folder
    return None, ref


# ---------------------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------------------
BUTTON_HEIGHT = 36


def _button_classes(b: dict) -> str:
    return "cadre/button/%s cadre/font/button" % ("flat" if b.get("style") == "flat" else "normal")


def button_node(b: dict, desc: dict, rep, module: bool = False) -> tuple[dict, dict, dict]:
    """(node, view custom defaults, view custom bindings) of one command button, a flex row at the descriptor's
    box. A route or a faceplate opener is a button alone. A pulse is a button, a question with Confirm and
    Cancel in its place once pressed (P10), and the pulse made by `cadre.hmi.page_pulse` (write path W18):
    the buttons that call it bind `enabled` to the permission of that path (gate G7 commands). `module` is whether the
    page is built under the module rendering with the module's button available: a pulse that asks for `render: module`
    then has the module's `cadre.ob.button` as its question button, and the library's button otherwise."""
    screen = _screen()
    a, bid, label = b["action"], safe(b["id"]), b["label"]
    pos = pv.cpos(b["x"], b["y"], b["w"], b["h"])
    style = {"classes": _button_classes(b), "height": "100%"}
    if a["type"] == "route":
        node = pv.node("ia.input.button", f"Button_{b['id']}", pos, {"text": label, "style": style},
                       events=pv.on_action([f"system.perspective.navigate({a['route']!r})"]))
        return node, {}, {}
    if a["type"] == "faceplate":
        sym, folder = _device_of(desc, a["device"])
        root = desc.get("tagRoot", "")
        device = screen.tag_path(root, folder)
        kind = a.get("kind") or (screen.device_kind(sym) if sym else "")
        title = a.get("title") or (sym.get("params", {}).get("tag") if sym else None) or folder.split("/")[-1]
        flabel = a.get("label") or (sym.get("label", "") if sym else "")
        lines = library.open_device(repr(device), repr(kind), repr(title), repr(flabel), repr(a.get("tab", "")))
        node = pv.node("ia.input.button", f"Button_{b['id']}", pos, {"text": label, "style": style},
                       events=pv.on_action(lines))
        return node, {}, {}
    path = screen.tag_path(desc.get("tagRoot", ""), a["tag"])
    pend, msg = f"pend_{bid}", f"msg_{bid}"
    can = pv.bind(pv.expr("{view.custom.can.%s}" % PULSE_PATH))
    question = a.get("confirm") or f"{label}?"
    ask_lines = [f"self.view.custom.{msg} = ''", f"self.view.custom.{pend} = True"]
    shown = pv.bind(pv.expr("if(len({view.custom.%s}) > 0, {view.custom.%s}, %s)" % (msg, msg, quote(label))))
    if module and b.get("render") == "module":
        # The module's button (spike T0 wrap W3, wiki page 12 section 17.12) takes the place of the Press button: its
        # `onPress` asks the same question, and the Confirm button below makes the pulse through `page_pulse`, which
        # asks for the role again. The component has no `enabled`, so it is made static while the session lacks the
        # permission of the path (the role check is in the Confirm button and in `page_pulse`, not in this button).
        main = pv.node("cadre.ob.button", "Press", pv.fpos(grow=1, basis="0px"), {
            "tag": label, "positioning": "button", "readoutPosition": "right"},
            prop_config={"position.display": pv.bind(pv.expr("!{view.custom.%s}" % pend)),
                         "props.static": pv.bind(pv.expr("!{view.custom.can.%s}" % PULSE_PATH)),
                         "props.tag": shown},
            events={"component": {"onPress": pv.script_handler(ask_lines)}})
    else:
        main = pv.node("ia.input.button", "Press", pv.fpos(grow=1, basis="0px"), {"text": label, "style": style},
                       prop_config={"position.display": pv.bind(pv.expr("!{view.custom.%s}" % pend)),
                                    "props.enabled": can, "props.text": shown},
                       events=pv.on_action(ask_lines))
    ask = pv.node("ia.display.label", "Question", pv.fpos(grow=1, basis="0px"), {
        "text": question, "style": {"classes": "cadre/font/label cadre/text/active", "padding": "0 6px",
                                    "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"}},
        prop_config={"position.display": pv.bind(pv.expr("{view.custom.%s}" % pend))})
    yes = pv.node("ia.input.button", "Confirm", pv.fpos(basis="84px", shrink=0), {
        "text": framework.CONFIRM, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "100%"}},
        prop_config={"position.display": pv.bind(pv.expr("{view.custom.%s}" % pend)), "props.enabled": can},
        events=pv.on_action([f"msg = cadre.hmi.page_pulse(self.session, {path!r})",
                             f"self.view.custom.{pend} = False", f"self.view.custom.{msg} = msg"]))
    no = pv.node("ia.input.button", "Cancel", pv.fpos(basis="72px", shrink=0), {
        "text": framework.CANCEL, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "100%"}},
        prop_config={"position.display": pv.bind(pv.expr("{view.custom.%s}" % pend))},
        events=pv.on_action([f"self.view.custom.{pend} = False"]))
    node = pv.node("ia.container.flex", f"Button_{b['id']}", pos, {
        "direction": "row", "alignItems": "center", "style": {"gap": "4px"}}, children=[main, ask, yes, no])
    return node, {"can": dict(framework.CAN_DEFAULT), pend: False, msg: ""}, {"custom.can": framework.CAN_CFG}


# ---------------------------------------------------------------------------------------
# Range bars
# ---------------------------------------------------------------------------------------
def bar_node(name: str, pos: dict, value_path: str, spec: dict, bound: bool = True) -> dict:
    """An embedded `Parts/RangeBar`: the value bound to its tag, every other parameter stated (GF-60)."""
    params = {**BAR_PARAMS, **{k: spec[k] for k in (*BAR_NUMBERS, "unit", "format", "vertical", "showValue") if k in spec}}
    cfg = {"props.params.value": pv.bind(pv.tag(value_path))}
    del params["value"]
    return pv.node("ia.display.view", name, pos, {"path": "Parts/RangeBar", "params": params}, prop_config=cfg)


def bar_box(sym: dict, bar: dict, contracts: dict, limit=None) -> tuple[float, float, float, float]:
    """Where a bar beside a readout stands: against the readout's box (as the library gives it), on the side
    the descriptor names, without moving the readout or any other symbol. `x`, `y`, `w` and `h` of the bar
    override the side."""
    screen = _screen()
    c = contracts[screen.KIND_VIEW[sym["kind"].lower()]]
    bx, by, bw, bh = screen.symbol_box(sym, c, limit)
    vertical = bool(bar.get("vertical"))
    length = bar.get("length", BAR_LENGTH if not vertical else 2 * BAR_LENGTH)
    thick = bar.get("thickness", BAR_THICKNESS)
    gap = bar.get("gap", BAR_GAP)
    w, h = (thick, length) if vertical else (length, thick)
    side = bar.get("side", "right")
    if side == "right":
        x, y = bx + bw + gap, by + (bh - h) / 2
    elif side == "left":
        x, y = bx - gap - w, by + (bh - h) / 2
    elif side == "below":
        x, y = bx + (bw - w) / 2, by + bh + gap
        w = bar.get("length", bw) if not vertical else w
    else:   # above
        x, y = bx + (bw - w) / 2, by - gap - h
        w = bar.get("length", bw) if not vertical else w
    return (bar.get("x", x), bar.get("y", y), bar.get("w", w), bar.get("h", h))


# ---------------------------------------------------------------------------------------
# Embedded trends
# ---------------------------------------------------------------------------------------
def trend_node(t: dict, tag_root: str) -> dict:
    screen = _screen()
    pens = t["pens"]
    same = len(pens) < 2 or (pens[0].get("unit", "") == pens[1].get("unit", ""))
    key = "one" if len(pens) == 1 else ("same" if same else "two")
    params = {"title": t.get("title", ""), "minutes": t.get("minutes", 10)}
    for n, p in enumerate(pens, start=1):
        params[f"tag{n}"] = screen.tag_path(tag_root, p["tag"])
        params[f"label{n}"] = p.get("label", "")
        params[f"unit{n}"] = p.get("unit", "")
    return pv.node("ia.display.view", f"Trend_{t['id']}", pv.cpos(t["x"], t["y"], t["w"], t["h"]), {
        "path": TREND_VIEWS[key], "params": params})


# ---------------------------------------------------------------------------------------
# Embedded alarm panels (L5)
# ---------------------------------------------------------------------------------------
ALARM_PANEL_VIEW = "Faceplate/Alarms"


def source_pattern(path: str) -> str:
    """The alarm source pattern of every alarm under a tag folder, `[default]site/a` giving `prov:default:/tag:site/a/*`
    (`cadre.hmi.device_source`, GF-34)."""
    provider, rest = path[1:].split("]", 1)
    return f"prov:{provider}:/tag:{rest.strip('/')}/*"


def alarm_panel_node(a: dict, tag_root: str) -> dict:
    """An alarm panel on a page: the library's `Faceplate/Alarms` (the stock table, or the module's lists with
    `--render module`), with Ack selected and Ack all beneath it, over the alarms under the tag folders of `sources`
    (relative to the tag root, or absolute)."""
    screen = _screen()
    patterns = ",".join(source_pattern(screen.tag_path(tag_root, f)) for f in a["sources"])
    return pv.node("ia.display.view", f"Alarms_{a['id']}", pv.cpos(a["x"], a["y"], a["w"], a["h"]), {
        "path": ALARM_PANEL_VIEW, "params": {"source": patterns, "deviceId": ""}, "useDefaultViewHeight": False,
        "useDefaultViewWidth": False})


# ---------------------------------------------------------------------------------------
# Lines
# ---------------------------------------------------------------------------------------
def line_node(ln: dict, W: float, H: float, tag_root: str) -> tuple[dict, dict, dict]:
    """One line over the page: `points` joined by straight segments, `width` px (2), solid unless `style` is
    `dashed`. With a `gate` (a tag, a symbol of the page, or a list of them, all of which must hold) the
    line is solid while energised and light and dashed while dead (P4: the state is also in the stroke,
    not only its colour)."""
    screen = _screen()
    pts = ln["points"]
    d = "M" + "L".join(f"{x:g} {y:g}" for x, y in pts)
    width = ln.get("width", 2)
    custom, custom_cfg, terms = {}, {}, []
    for i, g in enumerate(_gates(ln)):
        if "symbol" in g:
            terms.append("{view.custom.g_%s}" % g["symbol"])
        else:
            key = f"ln_{safe(ln['id'])}_{i}"
            custom[key] = False
            custom_cfg[f"custom.{key}"] = pv.bind(pv.tag(screen.tag_path(tag_root, g["tag"])))
            terms.append("{view.custom.%s}" % key)
    el = {"type": "path", "name": ln["id"], "d": d, "fill": {"paint": "none"},
          "stroke": {"paint": "var(--element-neutral-color)", "width": width, "linejoin": "miter", "linecap": "butt",
                     "dasharray": LINE_DASH if ln.get("style") == "dashed" else ""}}
    cfg = {}
    if terms:
        live = " && ".join(terms)
        cfg["props.elements[0].stroke.paint"] = pv.bind(pv.expr(
            f"if({live}, 'var(--element-neutral-color)', 'var(--element-inactive-color)')"))
        cfg["props.elements[0].stroke.dasharray"] = pv.bind(pv.expr(f"if({live}, '', '{LINE_DASH}')"))
    node = library.svg(f"Line_{ln['id']}", pv.cpos(0, 0, W, H), [el], view_box=f"0 0 {W:g} {H:g}",
                       extra_config=cfg or None, props={"preserveAspectRatio": "none"})
    return node, custom, custom_cfg


# ---------------------------------------------------------------------------------------
# Links, brackets, wells and emphasised words
# ---------------------------------------------------------------------------------------
def link_node(lk: dict) -> dict:
    """An icon that navigates (an area chevron, GP-07): a click on it opens the route. A symbol opens its
    faceplate and a link navigates; the two are never the same click (P8)."""
    size = lk.get("w", LINK_SIZE), lk.get("h", LINK_SIZE)
    node = library.icon_svg(f"Link_{lk['id']}", lk.get("icon", LINK_ICON), pv.cpos(lk["x"], lk["y"], *size),
                            paint="var(--element-neutral-color)",
                            events=pv.on_click([f"system.perspective.navigate({lk['route']!r})"]))
    node["props"]["style"] = {"cursor": "pointer"}
    return node


def bracket_nodes(br: dict) -> list[dict]:
    """A thin bracket with its name (GP-09): a line with an end tick at each end pointing at the group it
    names, and the name centred beyond it. `side` below (default): the group is above the bracket."""
    w, below = br["w"], br.get("side", "below") == "below"
    tick = BRACKET_TICK
    d = f"M0 0V{tick}H{w:g}V0" if below else f"M0 {tick + 2}V2H{w:g}V{tick + 2}"
    line = library.svg(f"Bracket_{br['id']}", pv.cpos(br["x"], br["y"], w, tick + 2), [
        {"type": "path", "name": "bracket", "d": d, "fill": {"paint": "none"},
         "stroke": {"paint": "var(--element-inactive-color)", "width": 1}}],
        view_box=f"0 0 {w:g} {tick + 2}", props={"preserveAspectRatio": "none"})
    y = br["y"] + tick + 2 if below else br["y"] - BRACKET_LABEL
    name = pv.node("ia.display.label", f"BracketName_{br['id']}", pv.cpos(br["x"], y, w, BRACKET_LABEL), {
        "text": br["label"], "textStyle": {"textAlign": "center"},
        "style": {"classes": LABEL_STYLE, "whiteSpace": "nowrap", "justifyContent": "center"}})
    return [line, name]


LABEL_STYLE = "cadre/font/label cadre/text/neutral"


def well_node(w: dict, tag_root: str) -> tuple[dict, dict, dict]:
    """The liquid of a well with level switches (GM-01): filled up to the highest mark reached, and a lighter
    band up to the next mark above it (below the first mark when none is reached). The original has no
    analogue level, so the fill steps from mark to mark and never states a percentage. The paths are fixed
    strings chosen by the marks' states, so no number is formatted in an expression."""
    screen = _screen()
    W, H = w["w"], w["h"]
    marks = sorted(w["marks"], key=lambda m: m["level"])
    custom, custom_cfg, keys = {}, {}, []
    for i, m in enumerate(marks):
        key = f"well_{safe(w['id'])}_{i}"
        custom[key] = False
        custom_cfg[f"custom.{key}"] = pv.bind(pv.tag(screen.tag_path(tag_root, m["tag"])))
        keys.append("{view.custom.%s}" % key)

    def y(level):
        return round(H * (1 - level), 2)

    def box(top, bottom):
        return f"M0 {top:g}H{W:g}V{bottom:g}H0Z"
    fill = "''"
    band = "'" + box(y(marks[0]["level"]), H) + "'"          # none reached: the floor to the first mark
    for i, k in enumerate(keys):                             # the last mark outermost: the highest reached decides
        fill = f"if({k}, '{box(y(marks[i]['level']), H)}', {fill})"
        above = "'" + box(y(marks[i + 1]["level"]), y(marks[i]["level"])) + "'" if i + 1 < len(marks) else "''"
        band = f"if({k}, {above}, {band})"
    node = library.svg(f"Well_{w['id']}", pv.cpos(w["x"], w["y"], W, H), [
        {"type": "path", "name": "liquid", "d": "", "fill": {"paint": "var(--element-inactive-color)", "opacity": WELL_FILL}},
        {"type": "path", "name": "next", "d": "", "fill": {"paint": "var(--element-inactive-color)", "opacity": WELL_BAND}}],
        view_box=f"0 0 {W:g} {H:g}", props={"preserveAspectRatio": "none"},
        extra_config={"props.elements[0].d": pv.bind(pv.expr(fill)), "props.elements[1].d": pv.bind(pv.expr(band))})
    return node, custom, custom_cfg


def emphasised_label(lb: dict, tag_root: str) -> tuple[dict, dict, dict]:
    """A text label whose weight and colour follow a Boolean (GP-12): bold and active while the tag, or the
    state of a symbol of the page, holds; the label's own style (neutral) otherwise. With `words`, its text is
    the first word while clear and the second while the Boolean holds."""
    screen = _screen()
    node = screen.text_label(lb)
    g = lb["emphasis"]
    custom, custom_cfg = {}, {}
    if "symbol" in g:
        live = "{view.custom.g_%s}" % g["symbol"]
    else:
        key = f"em_{safe(lb['id'])}"
        custom[key] = False
        custom_cfg[f"custom.{key}"] = pv.bind(pv.tag(screen.tag_path(tag_root, g["tag"])))
        live = "{view.custom.%s}" % key
    base = node["props"]["style"]["classes"]
    on = base.replace("cadre/text/neutral", "cadre/text/active")
    node["propConfig"] = {
        "props.style.fontWeight": pv.bind(pv.expr(f"if({live}, 'bold', 'normal')")),
        "props.style.classes": pv.bind(pv.expr(f"if({live}, {quote(on)}, {quote(base)})"))}
    if g.get("words"):   # a two-state text: the normal word while clear, the abnormal word while it holds
        clear, holds = g["words"]
        node["propConfig"]["props.text"] = pv.bind(pv.expr(f"if({live}, {quote(holds)}, {quote(clear)})"))
    return node, custom, custom_cfg


# ---------------------------------------------------------------------------------------
# The diagram's parts, and fit
# ---------------------------------------------------------------------------------------
def diagram_parts(desc: dict, contracts: dict, limits: dict, rep, module: bool = False) -> dict:
    """The nodes the parts add to a diagram page: `under` (lines, drawn with the pipes) and `over` (bars,
    trends, buttons, on top of the symbols), and the view custom they need. `module`: see `button_node`."""
    check(desc, rep)
    out = {"under": [], "over": [], "custom": {}, "custom_cfg": {}}
    if rep.errors and desc.get("screen", {}).get("layout", "diagram") != "diagram":
        return out
    screen = _screen()
    W, H = desc["screen"]["width"], desc["screen"]["height"]
    root = desc.get("tagRoot", "")
    for ln in desc.get("lines", []):
        node, c, cc = line_node(ln, W, H, root)
        out["under"].append(node)
        out["custom"].update(c)
        out["custom_cfg"].update(cc)
    for w in desc.get("wells", []):
        node, c, cc = well_node(w, root)
        out["under"].append(node)
        out["custom"].update(c)
        out["custom_cfg"].update(cc)
    for br in desc.get("brackets", []):
        out["under"] += bracket_nodes(br)
    for lb in desc.get("labels", []):
        if "emphasis" in lb:
            node, c, cc = emphasised_label(lb, root)
            out["under"].append(node)
            out["custom"].update(c)
            out["custom_cfg"].update(cc)
    for s in desc.get("symbols", []):
        if "bar" in s and (s["kind"].lower() in ("readout", "instrument-field")):
            bar = s["bar"]
            member = bar.get("value") or s.get("bind", {}).get("value")
            if member is None:
                continue
            x, y, w, h = bar_box(s, bar, contracts, limits.get(s["id"]))
            out["over"].append(bar_node(f"Bar_{s['id']}", pv.cpos(x, y, w, h), screen.tag_path(root, member), bar))
    for b in desc.get("bars", []):
        out["over"].append(bar_node(f"Bar_{b['id']}", pv.cpos(b["x"], b["y"], b["w"], b["h"]),
                                    screen.tag_path(root, b["value"]), b))
    for t in desc.get("trends", []):
        out["over"].append(trend_node(t, root))
    for a in desc.get("alarmPanels", []):
        out["over"].append(alarm_panel_node(a, root))
    for lk in desc.get("links", []):
        if (library.ICONS / f"{lk.get('icon', LINK_ICON)}.json").exists():   # (a missing icon is an error of `check`)
            out["over"].append(link_node(lk))
    for b in desc.get("buttons", []):
        node, c, cc = button_node(b, desc, rep, module)
        out["over"].append(node)
        out["custom"].update(c)
        out["custom_cfg"].update(cc)
    return out


def fit_settings(desc: dict) -> dict | None:
    """The `fit` option of a diagram: None when the page keeps its size, else `{reserveX, reserveY}`, the
    pixels of the viewport the frame takes (the top dock, 48 px, and the toolbar, 56 px, by default)."""
    fit = desc.get("screen", {}).get("fit")
    if not fit:
        return None
    if fit is True:
        fit = {}
    toolbar = bool(desc.get("toolbar", True))
    return {"reserveX": fit.get("reserveX", 0),
            "reserveY": fit.get("reserveY", FIT_TOP_DOCK + (FIT_TOOLBAR if toolbar else 0))}


def fit_expression(W: float, H: float, fit: dict) -> str:
    """The scale a page of W by H px takes to fit the viewport less the frame: never above 1, the smaller of
    the two ratios (the aspect ratio is kept). The viewport is `page.props.dimensions` (Perspective's own
    page property; the corpus binds its `viewport.width` and `viewport.height`)."""
    vw = "coalesce({page.props.dimensions.viewport.width}, %g)" % W
    vh = "coalesce({page.props.dimensions.viewport.height}, %g)" % H
    dock = f"if({FIT_DOCKED}, {FIT_FACEPLATE_DOCK}, 0)"   # the open faceplate dock takes its width (GP-10)
    viewport = (f"min(1.0, min(({vw} - {fit['reserveX']:g} - {dock}) / {float(W):.1f}, "
                f"({vh} - {fit['reserveY']:g}) / {float(H):.1f}))")
    # Where the module's canvas zoom component measures the canvas (module 0.4.1), the fit reads that box: the
    # session's dock flag outlives a reload (the gateway keeps the page and starts no view again) and is shared by
    # every tab of a session (measured on the glass 2026-10-24); the viewport rule stays for the stock rendering.
    measured = (f"min(1.0, min(({CANVAS_W} - {fit['reserveX']:g}) / {float(W):.1f}, "
                f"{CANVAS_H} / {float(H):.1f}))")
    return f"if(coalesce({CANVAS_W}, 0) > 0 && coalesce({CANVAS_H}, 0) > 0, {measured}, {viewport})"


def scale_expression(desc: dict) -> str:
    """The scale a diagram is drawn at, `s = fit * zoom`: the fit of `fit_expression` (1 for a page that states no
    `fit`) times `view.custom.zoom`, held to the zoom range so that a stale value cannot draw the page off."""
    fit = fit_settings(desc)
    W, H = desc["screen"]["width"], desc["screen"]["height"]
    base = fit_expression(W, H, fit) if fit is not None else "1.0"
    return f"({base}) * min({ZOOM_MAX:g}, max({ZOOM_MIN:g}, coalesce({ZOOM_VIEW}, 1.0)))"


def apply_fit(diagram: dict, canvas: dict, desc: dict, sizer: dict | None = None) -> dict:
    """Scale the diagram to its window (GP-10) and to the user's zoom (L4): a CSS transform changes no layout
    size, so the canvas holds a sizer whose box is the scaled size of the diagram (`W * s` by `H * s`), and the
    diagram, a fixed pixel box, is drawn at `s` from its top left corner. Every symbol and text scales with the
    page (a coordinate container in percent mode would not scale an embedded view: the library symbols hold their
    sizes in px). The scale is one view property, `custom.scale`, which the transform and the sizer read. The
    canvas scrolls (`overflow: auto`, `meta.domId` `cadre-canvas`, the zoom component's target); a fitted page
    keeps `hidden` until it is zoomed above 1, so that a fraction of a pixel never draws a scroll bar. Returns the
    view's `custom` and `custom_config` the scale needs."""
    W, H = desc["screen"]["width"], desc["screen"]["height"]
    fitted = fit_settings(desc) is not None
    canvas["meta"]["domId"] = CANVAS_DOM_ID
    canvas["props"]["style"]["overflow"] = "hidden" if fitted else "auto"
    if fitted:
        canvas.setdefault("propConfig", {})["props.style.overflow"] = pv.bind(pv.expr(
            f"if({ZOOM_VIEW} > 1.0, 'auto', 'hidden')"))
    diagram["props"]["style"]["transformOrigin"] = "top left"
    diagram.setdefault("propConfig", {})["props.style.transform"] = pv.bind(pv.expr(
        "'scale(' + toStr(round(%s, 4)) + ')'" % SCALE_VIEW))
    if sizer is not None:
        width = "toStr(round(%g * %s, 1)) + 'px'" % (W, SCALE_VIEW)
        height = "toStr(round(%g * %s, 1)) + 'px'" % (H, SCALE_VIEW)
        sizer.setdefault("propConfig", {}).update({
            "props.style.width": pv.bind(pv.expr(width)), "props.style.height": pv.bind(pv.expr(height)),
            "position.basis": pv.bind(pv.expr(height))})
    return {"custom": {"zoom": 1, "scale": 1, "canvasW": 0, "canvasH": 0},
            "custom_config": {"custom.scale": pv.bind(pv.expr(scale_expression(desc)))}}


def profile() -> dict:
    """What the library profile states of the parts (`library_profile.build`): the descriptor keys, the
    views and the write path."""
    return {"arrays": list(PART_ARRAYS), "symbolKeys": list(SYMBOL_KEYS), "symbolParams": list(SYMBOL_PARAMS),
            "symbolMore": list(SYMBOL_MORE),
            "actions": list(ACTIONS), "pulsePath": PULSE_PATH, "function": "page_pulse",
            "views": {"rangeBar": "Parts/RangeBar", "trends": TREND_VIEWS},
            "screenKeys": ["fit"], "labelKeys": ["emphasis"], "history": history_needs()}
