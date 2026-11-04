"""The Cadre HMI component library: style classes and parent project views.

Each library view is built from stock components that the Ignition-Wiki registry declares
(`F:/repos/Ignition-Wiki/schemas/components`), checked by `validate_view.py` before it is
written. Visual design follows the maritime design guidance (tokens, icons, geometry) taken
from the Apache-2.0 release pinned in decisions COBD-003; interface names (`on`, `open`,
`readoutPosition`, `alertFrameStatus` ...) follow the reference component catalogue so a
design written against that catalogue maps one to one (wiki page 05).

Geometry of an automation symbol (the package `automation-button.css`, regular size tokens):
touch target 48 px, round holder 36 px with a 1 px border, icon 24 px, corner badges 16 px.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import pv
from .theme import palette_root_binding

ROOT = Path(__file__).resolve().parents[2]
ICONS = ROOT / "library" / "icons"

# ---------------------------------------------------------------------------------------
# Opening a faceplate
# ---------------------------------------------------------------------------------------
# A faceplate opens where the session keeps it (COBD-045): in the right dock, the default, or in the
# floating popup the pin chose (`session.custom.faceplateMode`). Every symbol, alarm row and trend
# title that opens a faceplate ends with `open_faceplate`, after `cadre.hmi.select_device`. The popup
# takes the size of its view (`Framework/FaceplatePopup`, 450 by 600 px, ASMP-REPORT-01 section 5.2);
# `position` names sides only (IGW:23-perspective-scripting section 4).
FACEPLATE_DOCK_ID = "faceplate"
FACEPLATE_POPUP_ID = "faceplatePopup"
FACEPLATE_POPUP_VIEW = "Framework/FaceplatePopup"
FLOAT_POPUP_VIEW = "Framework/ASM/FloatFaceplate"   # the ASM frame's popup, one for each device (COB-160)
FACEPLATE_MODES = ("dock", "popup")
# Whether the faceplate dock is open: every script that opens or closes it writes this, which a fitted page reads to
# leave the dock's width (parts.FIT_DOCKED, GP-10).
DOCKED = "self.session.custom.faceplateDocked"
POPUP_POSITION = {"top": 56, "right": 16}


def open_popup_line() -> str:
    """The call that floats the selected device's faceplate, titled with its identifier."""
    return (f"system.perspective.openPopup(id='{FACEPLATE_POPUP_ID}', view='{FACEPLATE_POPUP_VIEW}', "
            f"title=self.session.custom.selectedTitle, position={POPUP_POSITION!r}, showCloseIcon=True, "
            "draggable=True, resizable=True, modal=False, overlayDismiss=False, viewportBound=True)")


def open_float_lines(indent: str = "") -> list[str]:
    """The lines that float the selected device's faceplate in the ASM frame (COB-160): one popup for each
    device (`cadre.hmi.float_id`), whose view parameters carry the device, kind, style, title, label and tab
    (`cadre.hmi.float_params`), offset 24 px from the one before (`float_position`). A device already
    floating is closed and opened again, which brings it to the front on the asked tab."""
    return [f"{indent}fid = cadre.hmi.float_id(self.session.custom.selectedDevice)",
            f"{indent}system.perspective.closePopup(fid)",
            f"{indent}system.perspective.openPopup(id=fid, view='{FLOAT_POPUP_VIEW}', "
            "params=cadre.hmi.float_params(self.session, fid), title=self.session.custom.selectedTitle, "
            "position=cadre.hmi.float_position(self.session, self.session.custom.selectedDevice), "
            "showCloseIcon=True, draggable=True, resizable=True, modal=False, overlayDismiss=False, "
            "viewportBound=True)"]


def open_faceplate(indent: str = "") -> list[str]:
    """The lines that open the selected device's faceplate in the session's place for it: the right dock, or
    a popup; in the ASM frame (`session.custom.frame`, COB-160) a popup of its own for each device."""
    return [f"{indent}if self.session.custom.faceplateMode == 'popup':",
            f"{indent}\tif cadre.hmi.asm_frame(self.session):",
            *open_float_lines(indent + "\t\t"),
            f"{indent}\telse:",
            f"{indent}\t\t{open_popup_line()}",
            f"{indent}else:",
            f"{indent}\tsystem.perspective.openDock(id='{FACEPLATE_DOCK_ID}')",
            f"{indent}\t{DOCKED} = True"]


def open_device(device: str, kind: str, title: str = "''", label: str = "''", tab: str = "''",
                indent: str = "") -> list[str]:
    """The lines that open a device's faceplate on a named tab (COB-158 to COB-160): every opener that
    names a tab (a command button, a search row, a row of the alarm banner) calls this. Each argument
    is a script expression, for example `"'[default]plant/P1'"` or `"d['kind']"`; `tab` is a tab key
    of the faceplate (`home`, `config`, `alarms`, ...), and a key the faceplate lacks opens its first
    tab. The tab travels in `session.custom.selectedTab`, which `cadre.hmi.select_device` writes last
    (empty for a plain symbol click), and every faceplate view takes it as `params.tab`."""
    return [f"{indent}cadre.hmi.select_device(self.session, {device}, {kind}, {title}, {label}, {tab})",
            *open_faceplate(indent)]

# ---------------------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------------------
_ICON_CACHE: dict[str, dict] = {}


def circle_d(cx: float, cy: float, r: float) -> str:
    return f"M{cx - r} {cy}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0Z"


# Artwork drawn here from primitives, in the two tone style of the package automation icons (a
# body in the device's primary colour inside an outline in its tertiary colour, the inverted pair
# while off): the pin has no lamp. A lit lamp carries a filled centre; an unlit one is a ring.
DRAWN_ICONS = {
    "lamp-on": {"name": "lamp-on", "viewBox": "0 0 24 24", "elements": [
        {"type": "path", "d": circle_d(12, 12, 9), "fill": {"paint": "var(--automation-device-tertiary-color)"}},
        {"type": "path", "d": circle_d(12, 12, 8), "fill": {"paint": "var(--automation-device-primary-color)"}},
        {"type": "path", "d": circle_d(12, 12, 5), "fill": {"paint": "var(--automation-device-tertiary-color)"}}]},
    "lamp-off": {"name": "lamp-off", "viewBox": "0 0 24 24", "elements": [
        {"type": "path", "d": circle_d(12, 12, 9),
         "fill": {"paint": "var(--automation-device-tertiary-inverted-color)"}},
        {"type": "path", "d": circle_d(12, 12, 8),
         "fill": {"paint": "var(--automation-device-primary-inverted-color)"}}]},
}


# The generator: a circle with a G (COB-158, gap GG-01), in the same two tone as the lamp. The package pin has
# an icon `generator` (a G beside a lightning bolt, converted to library/icons) but no automation symbol with a
# running and a stopped form, so the symbol is drawn here: the G is a stroked arc (an open circle with a bar) in
# the outline colour, the body filled in the device's primary colour while running and in the inverted pair
# while stopped.
GENERATOR_G = "M15.25 8.75A4.6 4.6 0 1 0 16.6 12H12.4"


def _generator_icon(name: str, inverted: bool) -> dict:
    tail = "-inverted" if inverted else ""
    outline = f"var(--automation-device-tertiary{tail}-color)"
    return {"name": name, "viewBox": "0 0 24 24", "elements": [
        {"type": "path", "d": circle_d(12, 12, 9), "fill": {"paint": outline}},
        {"type": "path", "d": circle_d(12, 12, 8), "fill": {"paint": f"var(--automation-device-primary{tail}-color)"}},
        {"type": "path", "d": GENERATOR_G, "fill": {"paint": "none"},
         "stroke": {"paint": outline, "width": 1.8, "linecap": "round"}}]}


DRAWN_ICONS["generator-on"] = _generator_icon("generator-on", False)
DRAWN_ICONS["generator-off"] = _generator_icon("generator-off", True)


def icon(name: str) -> dict:
    if name in DRAWN_ICONS:
        return DRAWN_ICONS[name]
    if name not in _ICON_CACHE:
        _ICON_CACHE[name] = json.loads((ICONS / f"{name}.json").read_text(encoding="utf-8"))
    return _ICON_CACHE[name]


def svg(name: str, pos: dict, elements: list, *, view_box: str = "0 0 24 24",
        visible: str | None = None, extra_config: dict | None = None, props: dict | None = None,
        events: dict | None = None) -> dict:
    """One ia.shapes.svg. `visible` is an expression bound to meta.visible."""
    p = {"viewBox": view_box, "elements": elements}
    p.update(props or {})
    pc = dict(extra_config or {})
    if visible:
        pc[vis_key(pos)] = pv.bind(pv.expr(visible))
    return pv.node("ia.shapes.svg", name, pos, p, prop_config=pc or None, events=events)


def vis_key(pos: dict) -> str:
    """A flex child is hidden with `position.display` (IGW:04-position-contract section 3.4:
    excluded from the flex calculation); `meta.visible` keeps the space (visibility hidden,
    measured 2026-10-07, wiki page 07 GF-08). A coordinate child keeps `meta.visible`."""
    return "meta.visible" if "x" in pos else "position.display"


def icon_svg(name: str, icon_name: str, pos: dict, *, visible: str | None = None,
             transform: str | None = None, paint: str | None = None, events: dict | None = None,
             extra_config: dict | None = None) -> dict:
    ic = icon(icon_name)
    els = json.loads(json.dumps(ic["elements"]))
    if paint:
        for e in _walk(els):
            if "fill" in e and e["fill"].get("paint") not in (None, "none"):
                e["fill"]["paint"] = paint
    if transform:
        els = [{"type": "group", "transform": transform, "elements": els}]
    return svg(name, pos, els, view_box=ic["viewBox"], visible=visible, events=events,
               extra_config=extra_config)


def _walk(els):
    for e in els:
        yield e
        if e.get("elements"):
            yield from _walk(e["elements"])


def rrect_d(x: float, y: float, w: float, h: float, r: float) -> str:
    return (f"M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}"
            f"A{r} {r} 0 0 1 {x + w - r} {y + h}H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}"
            f"V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z")


# ---------------------------------------------------------------------------------------
# Style classes
# ---------------------------------------------------------------------------------------
# The four Cadre alert colours (F053, COBD-044): the priorities map onto them by rank, Critical the
# critical colour (`cadre.hmi.PRIORITY_STATUS`), as package colours its own alert levels.
ALERT_COLOURS = {"alarm": "--alert-alarm-color", "warning": "--alert-warning-color",
                 "caution": "--alert-caution-color", "critical": "--alert-critical-color"}


BLINK_TEMPOS = {"fast": ("0.4s", 50), "slow": ("0.8s", 25), "very-slow": ("1.6s", 12.5)}


def style_classes(tokens: dict) -> dict[str, dict]:
    """name -> {"base": style, "variants": [...]} (variants optional)."""
    out: dict[str, dict] = {}
    for name, decl in tokens["fonts"].items():
        out[f"cadre/font/{name}"] = {"base": dict(decl)}
    for c in ("active", "neutral", "inactive", "disabled"):
        out[f"cadre/text/{c}"] = {"base": {"color": f"var(--element-{c}-color)"}}
    out["cadre/surface/page"] = {"base": {"backgroundColor": "var(--container-background-color)"}}
    out["cadre/surface/card"] = {"base": {
        "backgroundColor": "var(--container-global-color)", "borderRadius": "8px",
        "boxShadow": "var(--shadow-floating-x) var(--shadow-floating-y) var(--shadow-floating-blur) var(--shadow-floating-color)",
        "overflow": "hidden"}}
    out["cadre/surface/section"] = {"base": {
        "backgroundColor": "var(--container-section-color)", "borderRadius": "8px"}}
    out["cadre/surface/bar"] = {"base": {
        "backgroundColor": "var(--container-global-color)",
        "borderBottom": "1px solid var(--border-divider-color)"}}
    out["cadre/surface/menu"] = {"base": {
        "backgroundColor": "var(--container-global-color)",
        "borderRight": "1px solid var(--border-divider-color)"}}
    out["cadre/divider/bottom"] = {"base": {"borderBottom": "1px solid var(--border-divider-color)"}}
    text = {"flat": "--element-active-color", "normal": "--on-normal-active-color",
            "raised": "--on-raised-active-color"}
    for kind in ("flat", "normal", "raised"):
        out[f"cadre/button/{kind}"] = {
            "base": {"backgroundColor": f"var(--{kind}-enabled-background-color)",
                     "border": f"1px solid var(--{kind}-enabled-border-color)",
                     "color": f"var({text[kind]})",
                     "borderRadius": "6px", "cursor": "pointer"},
            "variants": [{"pseudo": "hover", "style": {
                "backgroundColor": f"var(--{kind}-hover-background-color)"}}]}
    out["cadre/button/selected"] = {"base": {
        "backgroundColor": "var(--selected-enabled-background-color)",
        "border": "1px solid var(--selected-enabled-border-color)", "borderRadius": "6px",
        "color": "var(--on-selected-active-color)", "cursor": "pointer"}}
    out["cadre/nav/item"] = {
        "base": {"borderRadius": "6px", "cursor": "pointer", "padding": "0 12px"},
        "variants": [{"pseudo": "hover", "style": {
            "backgroundColor": "var(--flat-hover-background-color)"}}]}
    out["cadre/nav/item-selected"] = {"base": {
        "backgroundColor": "var(--selected-enabled-background-color)", "borderRadius": "6px",
        "cursor": "pointer", "padding": "0 12px", "color": "var(--on-selected-active-color)"}}
    # Alert flashing (unacknowledged): the animation shape proven on 8.3.6 by Cadre-Sandbox-ASM-2
    # (IGW:27-runtime-facts section 7.7): `duration` and `keyframes`, the runtime adds
    # alternate, infinite.
    for st, var in ALERT_COLOURS.items():
        out[f"cadre/alert/flash-{st}"] = {"base": {"animation": {"duration": "0.6s", "keyframes": {
            "0%": {"opacity": "1"}, "100%": {"opacity": "0.25"}}}}}
        out[f"cadre/alert/badge-{st}"] = {"base": {"backgroundColor": f"var({var})",
                                                   "color": f"var(--on-{st}-color)"}}
    # The module's flash tempos (`obc-alert-frame`, L5): the frame grows 2 px for 400 ms, then is thin for 400 ms (fast), 1200 ms
    # (slow) or 2800 ms (very slow). The runtime adds `alternate, infinite`, so the animation runs forward and back: it
    # shows from 0 to `on` of its duration, hence on for twice that at the turn, and `duration` is half the period.
    for tempo, (duration, on) in BLINK_TEMPOS.items():
        out[f"cadre/alert/blink-{tempo}"] = {"base": {"animation": {"duration": duration, "keyframes": {
            "0%": {"opacity": "1"}, f"{on - 1}%": {"opacity": "1"}, f"{on}%": {"opacity": "0"}, "100%": {"opacity": "0"}}}}}
    out["cadre/anim/spin"] = {"base": {"animation": {"duration": "1.2s", "keyframes": {
        "0%": {"transform": "rotate(0deg)"}, "100%": {"transform": "rotate(360deg)"}}}}}
    for p in ("day", "dusk", "night", "bright"):
        out[f"cadre/palette/{p}"] = {"base": {}}
    # Their rules are in the stylesheet (`theme.layout_css`), as the palettes' are: a rule on a label's
    # inner element cannot be written as a style property.
    for name in LAYOUT_CLASSES:
        out[name] = {"base": {}}
    return out


# ---------------------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------------------
# An identifier (the `tag` parameter) may be as long as a plant's tag stem, 16 characters, and is read
# from its first character wherever it is drawn: a label that cannot hold it ends in an ellipsis
# (`cadre/text/ellipsis`), never cut at the start, and the faceplate header shows it whole.
IDENTIFIER_CHARS = 16
ELLIPSIS = "cadre/text/ellipsis"     # on a label: no wider than its container, an ellipsis where it is cut
WITHIN = "cadre/box/within"          # on a container: no wider than its own container
LAYOUT_CLASSES = (ELLIPSIS, WITHIN)
# The fonts a layouter sizes a block against, as measured on the glass on 2026-10-11 (Chromium, the
# 1600 by 900 px viewport of gate G8, Noto Sans as the stylesheet loads it): the mean width in px of
# an upper case letter, a lower case letter and a digit, the widest glyph of the three sets, and the
# height of a line. `charWidth` is the width the library allows for one character: for an identifier
# or a caption the upper case mean rounded up to half a pixel, so an identifier of mixed case and
# digits fits and one of the widest letters alone ends in the ellipsis; for a value the digit mean
# rounded up likewise. `tests/test_hmi.py` pins each font's size against the tokens: a token that
# changes asks for a new measurement.
FONTS = {
    "automation-label": {"px": 12, "line": 16, "charWidth": 8,
                         "measured": {"upper": 7.61, "lower": 6.36, "digit": 6.61, "widest": 11.22}},
    "instrument-label": {"px": 11.5, "line": 16, "charWidth": 7.5,
                         "measured": {"upper": 7.3, "lower": 6.1, "digit": 6.33, "widest": 10.76}},
    "instrument-unit": {"px": 11.5, "line": 16, "charWidth": 7.5,
                        "measured": {"upper": 7.3, "lower": 6.1, "digit": 6.33, "widest": 10.76}},
    "automation-value-regular": {"px": 16, "line": 22, "charWidth": 9.5,
                                 "measured": {"upper": 10.62, "lower": 9.09, "digit": 9.15, "widest": 15.6}},
}


# The heights a block needs beyond its default size (`sizes` of its contract): a readout with its
# identifier is the value's line, the identifier's line and the two 1 px borders; an instrument field
# with a setpoint and the enhanced value is the setpoint's line (16 px, the small value font), the value
# (34 px, its font size at a line height of 1) and the caption's line.
READOUT_TAGGED = FONTS["automation-value-regular"]["line"] + FONTS["automation-label"]["line"] + 2
FIELD_ENHANCED_SETPOINT = 16 + 34 + FONTS["instrument-unit"]["line"]


def text_width(font: str, chars: int) -> float:
    """The width in px the library allows for `chars` characters of `font`."""
    return chars * FONTS[font]["charWidth"]


def block_size(contract: dict, params: dict | None = None) -> list:
    """The size `[width, height]` in px a block of a kind needs with the parameters given: the size of
    the first entry of the contract's `sizes` whose `when` the parameters meet (a parameter not given
    has the contract's default), or the view's default `size`. The default size holds a block with
    every flag at its default; `sizes` lists the flags that need more."""
    params, defaults = params or {}, contract.get("params", {})
    for entry in contract.get("sizes", []):
        if all(params.get(k, defaults.get(k)) == v for k, v in entry["when"].items()):
            return list(entry["size"])
    return list(contract["size"])


def identifier_width(contract: dict, chars: int) -> float:
    """The width in px a block of a kind needs to show an identifier of `chars` characters in full: the
    characters, no more than `IDENTIFIER_CHARS` of them, and the kind's own padding (`identifier.pad` of
    its contract). For an automation symbol it is the width of the readout beside or beneath the symbol."""
    ident = contract["identifier"]
    return text_width(ident["font"], min(chars, IDENTIFIER_CHARS)) + ident["pad"]


def identifier_shown(contract: dict, params: dict) -> bool:
    """Whether a block of a kind may draw its identifier with the parameters given. A kind without a
    flag always draws it. An automation symbol draws it unless the descriptor says no (`hasTag` false):
    the ID-tag button of a diagram shows the identifier of every symbol that does not refuse it, so the
    embed is sized for it. Every other kind draws it when its flag is set, the contract's default
    where the descriptor gives none."""
    ident = contract.get("identifier")
    if not ident:
        return False
    flag = ident["flag"]
    if flag is None:
        return True
    if contract.get("symbolSize"):
        return params.get("readoutPosition") != "none" and params.get(flag) is not False
    return bool(params.get(flag, contract.get("params", {}).get(flag)))


def identifier_needs(contract: dict, params: dict, chars: int) -> float:
    """The width in px the embed of a block must have to show `chars` characters of its identifier, however
    many they are (`identifier_width` stops at `IDENTIFIER_CHARS`, the widest the generator makes an
    embed). The characters and the kind's padding; beside an automation symbol the 48 px symbol too; for
    a tank the characters alone, across the whole of a static tank and across `identifier.share` of a
    live one, whatever the tile's size."""
    ident = contract["identifier"]
    text = text_width(ident["font"], chars)
    if "share" in ident:
        return text if params.get("static") else text / ident["share"]
    if contract.get("symbolSize") and params.get("readoutPosition") in ("left", "right"):
        return text + ident["pad"] + contract["symbolSize"]
    return text + ident["pad"]


# ---------------------------------------------------------------------------------------
# Automation symbols
# ---------------------------------------------------------------------------------------
# kind -> (state parameter, on icon, off icon, vertical icons or None, status mode)
DEVICE_KINDS = {
    "Pump": ("on", "pump-on-horizontal", "pump-off-horizontal",
             ("pump-on-vertical", "pump-off-vertical"), "speed"),
    "Motor": ("on", "motor-on-horizontal", "motor-off-horizontal",
              ("motor-on-vertical", "motor-off-vertical"), "speed"),
    "Fan": ("on", "fan-on", "fan-off", None, "speed"),
    "Valve": ("open", "twoway-digital-open", "twoway-digital-closed", None, "onoff"),
    "AnalogValve": ("open", "twoway-digital-open", "twoway-analog-closed", None, "opening"),
    "Damper": ("on", "damper-horizontal-on", "damper-horizontal-off", None, "onoff"),
    "Filter": ("on", "filter-1-on", "filter-1-off", None, "onoff"),
    "Switch": ("on", "switch-horizontal-on", "switch-horizontal-off", None, "onoff"),
    # a digital input shown as a lamp (wiki page 13 section 9); it gates no flow (PASS_KINDS)
    "Indicator": ("on", "lamp-on", "lamp-off", None, "onoff"),
    # a generator, shown running or stopped (COB-158); it passes no medium (PASS_KINDS)
    "Generator": ("on", "generator-on", "generator-off", None, "onoff"),
}
# Kinds of the factory that pass the medium whatever their state: their contract names no gate.
PASS_KINDS = ("Indicator", "Generator")

READOUT_DIRECTION = ("case({view.params.readoutPosition}, 'right', 'row', 'left', 'row-reverse', "
                     "'top', 'column-reverse', 'column')")

SYMBOL_PARAMS = {
    "readoutPosition": "bottom", "showStatus": True, "statusText": "", "hasTag": False, "tag": "",
    "vertical": False, "variant": "regular", "activated": False,
    "hasSpeed": False, "speed": 0, "value": 0,
    "alert": False, "alertFrameStatus": "alarm", "alertFrameMode": "acked-active",
    "badgeControl": "none", "badgeInterlock": "none", "badgeCommandLocked": "none",
    "badgeDuty": False, "outOfService": False,   # the duty mark and the out of service greying (COB-159, GM-05)
    "progress": False, "deviceId": "", "deviceKind": "", "deviceLabel": "",
}

CONTROL_BADGES = ("auto", "manual", "manual-only", "local", "local-only")

# The palette names an indicator's `states` may colour a state with (L5, wiki 13 section 9): each names a token of the
# parent's theme. A value that is none of these is used as a CSS paint.
STATE_COLOURS = {
    "off": "var(--automation-button-off-background-color)",
    "on": "var(--on-background-color)",
    "active": "var(--element-active-color)",
    "alarm": "var(--alert-alarm-color)",
    "warning": "var(--alert-warning-color)",
    "caution": "var(--alert-caution-color)",
    "critical": "var(--alert-critical-color)",
    "neutral": "var(--element-neutral-color)",
}


def state_paint(colour: str) -> str:
    """The CSS paint of a palette name, or the string itself where it is none."""
    return STATE_COLOURS.get(colour, colour)


# The notification of the module's pump, drawn as `obc-alert-frame` draws it (L5, wiki 13 section 4): a frame around the
# whole symbol and its readout, 2 px thick, the radius of the button (6 px), the colour of the status; while it is
# unacknowledged a second, 4 px frame shows for 400 ms in each period (`BLINK_TEMPOS`); dashed while rectified; at its
# top right the small side flap, a 20 px tab (16 px icon, 2 px padding, 2 px radius at its right) with the status's
# badge icon, outside the frame's right edge and 1 px above its top, as the module draws it (measured on the glass,
# 2026-10-26: the module's frame 54 by 69 px around its 48 px symbol and 20 px status row, the flap at its right edge).
# The view draws past its own box: the root, the layout, the content and the frame let their overflow show.
FRAME_THICKNESS = 2          # px: `--thickness` of `thickness-small`
FRAME_RADIUS = 6             # px: `--ui-components-button-border-radius`
FLAP = 20                    # px: the icon size 16 and the badge padding 2 on each side
FRAME_SIDE = 3               # px: the module's frame stands 3 px beside its 48 px symbol on each side
FRAME_BELOW = 1              # px: and 1 px below its status row
# The critical badge is the module's `obi-critical-badge` (the pin's icon, our module bundles it): an octagon.
CRITICAL_BADGE_D = ("M2.47717 12.8113C2.30349 12.516 2.21665 12.3684 2.18269 12.2111C2.15265 12.072 2.15265 11.9281 "
                    "2.18269 11.7889C2.21665 11.6317 2.30349 11.484 2.47717 11.1888L6.536 4.28877C6.7051 4.00128 "
                    "6.78966 3.85754 6.90703 3.75306C7.01089 3.66061 7.13288 3.59084 7.26522 3.54819C7.41479 3.5 "
                    "7.58155 3.5 7.91509 3.5L16.0849 3.5C16.4184 3.5 16.5852 3.5 16.7347 3.54819C16.8671 3.59084 "
                    "16.9891 3.66061 17.0929 3.75306C17.2103 3.85754 17.2948 4.00128 17.464 4.28877L21.5228 11.1888"
                    "C21.6965 11.484 21.7833 11.6317 21.8173 11.7889C21.8473 11.9281 21.8473 12.072 21.8173 12.2111"
                    "C21.7833 12.3684 21.6965 12.516 21.5228 12.8113L17.464 19.7112C17.2948 19.9987 17.2103 20.1425 "
                    "17.0929 20.2469C16.9891 20.3394 16.8671 20.4092 16.7347 20.4518C16.5852 20.5 16.4184 20.5 "
                    "16.0849 20.5H7.91509C7.58155 20.5 7.41479 20.5 7.26522 20.4518C7.13288 20.4092 7.01089 20.3394 "
                    "6.90703 20.2469C6.78966 20.1425 6.7051 19.9987 6.53599 19.7112L2.47717 12.8113Z")
FLAP_ICONS = {"alarm": "alarm-badge", "warning": "warning-badge", "caution": "caution-badge"}
ALERT_ST = "{view.params.alertFrameStatus}"
ALERT_MODE_P = "{view.params.alertFrameMode}"
ALERT_UNACKED = f"({ALERT_MODE_P} = 'unacked-active' || {ALERT_MODE_P} = 'unacked-rectified')"
# the status colour of the frame, the module's `--bg-color`
FRAME_COLOUR = ("case(" + ALERT_ST + ", 'warning', 'var(--alert-warning-color)', 'caution', "
                "'var(--alert-caution-color)', 'critical', 'var(--alert-critical-color)', 'var(--alert-alarm-color)')")
# the tempo of the flash (`obc-alert-frame` `resolvedFlashingSpeed`): unacknowledged and active, an alarm or a critical
# one flashes fast, a warning slow; rectified, very slow; a caution is steady
FRAME_BLINK = (f"if({ALERT_MODE_P} = 'unacked-active', if({ALERT_ST} = 'warning', 'cadre/alert/blink-slow', "
               "'cadre/alert/blink-fast'), 'cadre/alert/blink-very-slow')")


def _flap(status: str) -> dict:
    """The side flap of one status: the tab and the status's badge icon."""
    if status == "critical":
        els = [{"type": "path", "name": "mark", "d": CRITICAL_BADGE_D}]
    else:
        els = json.loads(json.dumps(icon(FLAP_ICONS[status])["elements"]))
        for e in _walk(els):
            e["name"] = "mark"
    for e in els:
        e["fill"] = {"paint": f"var(--on-{status}-active-color)"}
    tab = {"type": "path", "name": "frame", "d": "M0 0H18A2 2 0 0 1 20 2V18A2 2 0 0 1 18 20H0Z",
           "fill": {"paint": f"var({ALERT_COLOURS[status]})"}}
    shown = f"{ALERT_ST} = '{status}'" if status != "alarm" else         f"{ALERT_ST} != 'warning' && {ALERT_ST} != 'caution' && {ALERT_ST} != 'critical'"
    return svg(f"Flap_{status}", pv.fpos(basis=f"{FLAP}px", shrink=0), [
        tab, {"type": "group", "name": "badge", "transform": "translate(2 2) scale(0.666667)", "elements": els}],
        view_box=f"0 0 {FLAP} {FLAP}", visible=shown,
        # outside the frame: offsets from the frame's padding edge, so the border's width is added
        props={"style": {"width": f"{FLAP}px", "height": f"{FLAP}px", "position": "absolute",
                         "top": f"-{FRAME_BELOW + FRAME_THICKNESS}px", "right": f"-{FLAP + FRAME_THICKNESS}px"}})


def _frame_box(name: str, width: int, extra: dict, children: list | None = None, *, wrap: bool = False,
               outset: int = 0, **cfg) -> dict:
    """One layer of the frame, with a border, taking no click: with `wrap` a box over the content (the symbol with its
    3 px sides and its readout, 1 px lower), else over the whole view (the generator set)."""
    style = {"borderStyle": "solid", "borderWidth": f"{width}px", "borderRadius": f"{FRAME_RADIUS}px",
             "boxSizing": "border-box", "pointerEvents": "none", "overflow": "visible"}
    if wrap:
        # `outset`: a thicker layer grows outward by its extra width, so its inner edge stays the frame's
        style.update({"position": "absolute", "top": f"{-outset}px", "left": f"{-outset}px", "right": f"{-outset}px",
                      "bottom": f"-{FRAME_BELOW + outset}px"})
    return pv.node("ia.container.flex", name, pv.fpos(shrink=0) if wrap else pv.cpos(0, 0, 1, 1), {
        "direction": "row", "justify": "flex-end", "alignItems": "flex-start", "style": style},
        prop_config={**cfg, **extra}, children=children)


def _alert_frame(*, wrap: bool = False) -> list:
    """The notification: `Pulse` (the second, thicker frame that shows while unacknowledged) under `AlertFrame` (the
    frame and the flaps), both a layer over the whole box of a percent container (the symbol's view and the generator
    set). `AlertFrame` is shown while `alert` holds; the tab path of a flap is named `frame` (the walk reads it)."""
    base = {"props.style.borderColor": pv.bind(pv.expr(FRAME_COLOUR)),
            "props.style.borderStyle": pv.bind(pv.expr(f"if({ALERT_MODE_P} = 'unacked-rectified', 'dashed', 'solid')"))}
    pulse = _frame_box("AlertPulse", FRAME_THICKNESS + 2, {
        **base, "props.style.classes": pv.bind(pv.expr(FRAME_BLINK))},
        wrap=wrap, outset=2 if wrap else 0,
        **{"meta.visible": pv.bind(pv.expr(f"{{view.params.alert}} && {ALERT_UNACKED} && {ALERT_ST} != 'caution'"))})
    frame = _frame_box("AlertFrame", FRAME_THICKNESS, base, [_flap(k) for k in ALERT_COLOURS], wrap=wrap,
                       **{"meta.visible": pv.bind(pv.expr("{view.params.alert}"))})
    return [pulse, frame]


def _badges() -> list:
    out = []
    for b in CONTROL_BADGES:
        out.append(icon_svg(f"Badge_{b.replace('-', '_')}", b, pv.cpos(0, 0, 16, 16),
                            visible=f"{{view.params.badgeControl}} = '{b}'"))
    # Package draws `interlock` with its duty icon and `interlock-inhibit` with its standby icon
    # (automation-badge.js of the pin); the library follows it (COB-079)
    out.append(icon_svg("Badge_interlock", "duty", pv.cpos(0, 32, 16, 16),
                        visible="{view.params.badgeInterlock} = 'interlock'"))
    out.append(icon_svg("Badge_interlockInhibit", "standby", pv.cpos(0, 32, 16, 16),
                        visible="{view.params.badgeInterlock} = 'interlock-inhibit'"))
    out.append(icon_svg("Badge_commandLocked", "command-locked-f", pv.cpos(32, 32, 16, 16),
                        visible="{view.params.badgeCommandLocked} != 'none'"))
    # the duty mark (COB-159): The package's `duty` icon between the interlock and command locked badges
    out.append(icon_svg("Badge_duty", "duty", pv.cpos(16, 32, 16, 16), visible="{view.params.badgeDuty}"))
    return out


def _out_of_service() -> list:
    """An out of service symbol is greyed and says so (COB-159, GM-05): a veil of the page colour over the
    symbol, then the word OOS, under the badges and the alert frame."""
    veil = svg("OosVeil", pv.cpos(0, 0, 48, 48), [
        {"type": "path", "name": "veil", "d": rrect_d(0, 0, 48, 48, 6),
         "fill": {"paint": "var(--container-background-color)", "opacity": 0.72}}],
        view_box="0 0 48 48", visible="{view.params.outOfService}")
    word = pv.node("ia.display.label", "OosWord", pv.cpos(0, 17, 48, 14), {
        "text": "OOS", "textStyle": {"textAlign": "center"},
        "style": {"classes": "cadre/font/automation-label cadre/text/active", "justifyContent": "center"}},
        prop_config={"meta.visible": pv.bind(pv.expr("{view.params.outOfService}"))})
    return [veil, word]


def _status_row(mode: str, state: str) -> dict:
    s = f"{{view.params.{state}}}"
    if mode == "speed":
        text = (f"if(len({{view.params.statusText}}) > 0, {{view.params.statusText}}, "
                f"if({s}, if({{view.params.hasSpeed}}, numberFormat({{view.params.speed}}, '0') + ' %', 'On'), 'Off'))")
    elif mode == "opening":
        text = (f"if(len({{view.params.statusText}}) > 0, {{view.params.statusText}}, "
                f"numberFormat({{view.params.value}}, '0') + ' %')")
    else:
        text = (f"if(len({{view.params.statusText}}) > 0, {{view.params.statusText}}, "
                f"if({s}, 'On', 'Off'))")
    # the module's state readout (package state-on and state-off): obi-on or obi-off, the value 16 px at weight 400
    # on a 20 px line, 4 px from the icon (glass, 2026-10-26); a symbol with a speed keeps the run and stopped icons
    on_icon = "forward" if mode == "opening" else "on"
    off_icon = "forward-stopped" if mode == "opening" else "off"
    plain = "!{view.params.hasSpeed}" if mode == "speed" else "true"
    kids = [
        icon_svg("IconOn", on_icon, pv.fpos(basis="16px", shrink=0),
                 visible=f"({s} || ({mode!r} = 'opening')) && {plain}", paint="var(--element-active-color)"),
        icon_svg("IconOff", off_icon, pv.fpos(basis="16px", shrink=0),
                 visible=f"!{s} && ({mode!r} != 'opening') && {plain}", paint="var(--element-active-color)"),
    ]
    if mode == "speed":
        kids += [icon_svg("IconRun", "forward", pv.fpos(basis="16px", shrink=0),
                          visible=f"{s} && {{view.params.hasSpeed}}", paint="var(--element-active-color)"),
                 icon_svg("IconStopped", "forward-stopped", pv.fpos(basis="16px", shrink=0),
                          visible=f"!{s} && {{view.params.hasSpeed}}", paint="var(--element-active-color)")]
    # On in the active colour, Off in the inactive one, as the module's state readouts (glass, 2026-10-26)
    word = s
    kids.append(pv.node("ia.display.label", "Text", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/automation-value-regular-off cadre/text/active",
                  "whiteSpace": "nowrap", "lineHeight": "20px"}},
        prop_config={"props.text": pv.bind(pv.expr(text)),
                     "props.style.classes": pv.bind(pv.expr(
                         "'cadre/font/automation-value-regular-off ' + "
                         f"if({word}, 'cadre/text/active', 'cadre/text/inactive')"))}))
    return pv.node("ia.container.flex", "Status", pv.fpos(shrink=0),
                   {"direction": "row", "alignItems": "center",
                    "style": {"gap": "4px", "height": "20px"}},
                   prop_config={"position.display": pv.bind(pv.expr("{view.params.showStatus}"))},
                   children=kids)


def automation_symbol(kind: str) -> tuple[dict, dict]:
    state, ion, ioff, vert, mode = DEVICE_KINDS[kind]
    s = f"{{view.params.{state}}}"
    holder_fill = (f"if({{view.params.progress}}, 'var(--automation-pipe-primary-color)', "
                   f"if({s}, 'var(--on-background-color)', 'var(--automation-button-off-background-color)'))")
    holder_stroke = (f"if({{view.params.progress}}, 'transparent', "
                     f"if({s}, 'var(--on-border-color)', 'var(--automation-button-off-border-color)'))")
    if kind == "Indicator":   # a lamp coloured by its state (L5): the `colour` param, where it is stated, fills it
        holder_fill = f"if(len({{view.params.colour}}) > 0, {{view.params.colour}}, {holder_fill})"
        holder_stroke = f"if(len({{view.params.colour}}) > 0, {{view.params.colour}}, {holder_stroke})"
    holder = svg("Holder", pv.cpos(6, 6, 36, 36), [
        {"type": "path", "name": "ring", "d": circle_d(18, 18, 17.5),
         "fill": {"paint": "var(--automation-button-off-background-color)"},
         "stroke": {"paint": "var(--automation-button-off-border-color)", "width": 1}}],
        view_box="0 0 36 36", visible="{view.params.variant} != 'flat'",
        extra_config={"props.elements[0].fill.paint": pv.bind(pv.expr(holder_fill)),
                      "props.elements[0].stroke.paint": pv.bind(pv.expr(holder_stroke))})
    activated = svg("Activated", pv.cpos(0, 0, 48, 48), [
        {"type": "path", "name": "bg", "d": rrect_d(0, 0, 48, 48, 6),
         "fill": {"paint": "var(--flat-activated-background-color)"}}],
        view_box="0 0 48 48", visible="{view.params.activated}")
    progress = svg("Progress", pv.cpos(4, 4, 40, 40), [
        {"type": "path", "name": "arc", "d": "M20 2A18 18 0 0 1 38 20", "fill": {"paint": "none"},
         "stroke": {"paint": "var(--element-active-color)", "width": 2, "linecap": "round"}}],
        view_box="0 0 40 40", visible="{view.params.progress}",
        props={"style": {"classes": "cadre/anim/spin"}})
    icons = []
    single = "{view.params.variant} != 'double'"
    hv = f"!{{view.params.vertical}} && {single}"   # horizontal artwork: not vertical, not double
    icons.append(icon_svg("IconOn", ion, pv.cpos(12, 12, 24, 24), visible=f"{s} && {hv}"))
    icons.append(icon_svg("IconOff", ioff, pv.cpos(12, 12, 24, 24), visible=f"!{s} && {hv}"))
    if mode == "speed":
        # Package `variant-double` (automation-button.css): a direction icon over a smaller
        # device icon inside the holder, sized by the `new-icon-double-*` tokens (16 and 12 px).
        dbl = "{view.params.variant} = 'double'"
        icons.append(icon_svg("DirOn", "forward", pv.cpos(16, 9, 16, 16), visible=f"{dbl} && {s}"))
        icons.append(icon_svg("DirOff", "forward-stopped", pv.cpos(16, 9, 16, 16), visible=f"{dbl} && !{s}"))
        icons.append(icon_svg("SmallOn", ion, pv.cpos(18, 25, 12, 12), visible=f"{dbl} && {s}"))
        icons.append(icon_svg("SmallOff", ioff, pv.cpos(18, 25, 12, 12), visible=f"{dbl} && !{s}"))
    if vert:
        icons.append(icon_svg("IconOnV", vert[0], pv.cpos(12, 12, 24, 24),
                              visible=f"{s} && {{view.params.vertical}}"))
        icons.append(icon_svg("IconOffV", vert[1], pv.cpos(12, 12, 24, 24),
                              visible=f"!{s} && {{view.params.vertical}}"))
    else:
        # A symbol with no vertical artwork is rotated a quarter turn about its centre.
        icons.append(icon_svg("IconOnV", ion, pv.cpos(12, 12, 24, 24), transform="rotate(90 12 12)",
                              visible=f"{s} && {{view.params.vertical}}"))
        icons.append(icon_svg("IconOffV", ioff, pv.cpos(12, 12, 24, 24), transform="rotate(90 12 12)",
                              visible=f"!{s} && {{view.params.vertical}}"))
    lamp = kind == "Indicator"
    symbol = pv.node("ia.container.coord", "Symbol", pv.fpos(basis="48px", shrink=0),
                     {"style": {"overflow": "hidden", "width": "48px", "height": "48px",
                                "minWidth": "48px", "cursor": "pointer",
                                **({} if lamp else {"margin": f"0px {FRAME_SIDE}px"})}},
                     children=[activated, holder, progress] + icons + _out_of_service() + _badges())
    # The readout is as wide as its content and no wider than the embed (`cadre/box/within`, and it may
    # shrink beside the symbol): an identifier too long for it then ends in an ellipsis, where a readout
    # wider than the embed was centred on it and cut at both ends.
    readout = pv.node("ia.container.flex", "Readout", pv.fpos(shrink=1),
                      {"direction": "column", "alignItems": "flex-start",
                       "style": {"classes": WITHIN, "padding": "2px 4px" if lamp else "0px 4px", "gap": "0px"}},
                      prop_config={"position.display": pv.bind(pv.expr(
                          "{view.params.readoutPosition} != 'none'"))},
                      children=[
                          _status_row(mode, state),
                          pv.node("ia.display.label", "Tag", pv.fpos(shrink=0), {
                              "style": {"classes": f"cadre/font/automation-label cadre/text/neutral {ELLIPSIS}",
                                        "whiteSpace": "nowrap"}},
                              prop_config={"props.text": pv.bind(pv.expr("{view.params.tag}")),
                                           "position.display": pv.bind(pv.expr("{view.params.hasTag}")),
                                           # a fault row (COB-159, GG-04): the text of a condition that holds is bold
                                           **({"props.style.fontWeight": pv.bind(pv.expr(
                                               f"if({s}, 'bold', 'normal')"))} if kind == "Indicator" else {})}),
                      ])
    click = pv.on_click([
        "if self.view.params.deviceId:",
        "	cadre.hmi.select_device(self.session, self.view.params.deviceId, "
        "self.view.params.deviceKind, self.view.params.tag, self.view.params.deviceLabel)",
        *open_faceplate("	")])
    if kind == "Indicator":   # a lamp draws no frame or flap (L5)
        root = pv.node("ia.container.flex", "root", {},
                       {"alignItems": "center", "direction": "column", "justify": "flex-start",
                        "style": {"overflow": "hidden"}},
                       prop_config={"props.direction": pv.bind(pv.expr(READOUT_DIRECTION))},
                       events=click, children=[symbol, readout])
    else:
        # The notification frames the whole symbol and its readout, as the module's frame does: the layout of the
        # symbol and the readout, and over it the frame's layers (`_alert_frame`), in a percent container
        # the content (the symbol with its 3 px sides and the readout) carries the frame's layers as the module's
        # wrapper does, centred in the box; the flap shows past the box, so nothing on the way clips it
        content = pv.node("ia.container.flex", "Content", pv.fpos(shrink=0),
                          {"alignItems": "flex-start", "direction": "column", "justify": "flex-start",
                           "style": {"position": "relative", "overflow": "visible"}},
                          prop_config={"props.direction": pv.bind(pv.expr(READOUT_DIRECTION))},
                          children=[symbol, readout] + _alert_frame(wrap=True))
        layout = pv.node("ia.container.flex", "Layout", pv.cpos(0, 0, 1, 1),
                         {"alignItems": "center", "direction": "column", "justify": "flex-start",
                          "style": {"overflow": "visible"}},
                         children=[content])
        root = pv.node("ia.container.coord", "root", {}, {"mode": "percent",
                                                          "style": {"overflow": "visible", "cursor": "pointer"}},
                       events=click, children=[layout])
    params = dict(SYMBOL_PARAMS)
    params[state] = False
    params["deviceKind"] = kind.lower()
    if kind == "Indicator":   # no status row (the lamp's colour says the state) and a colour from the descriptor's states
        params["showStatus"] = False
        params["colour"] = ""
    if kind == "Generator":   # `genset` draws the larger picture instead (`generator_set`, gap GG-01)
        params["picture"] = "symbol"
    doc = pv.view(root, params=params, param_dirs={k: "input" for k in params},
                  size={"width": 48, "height": 48})
    contract = {
        "view": f"Automation/{kind}", "kind": kind.lower(), "state": state, "statusMode": mode,
        "params": params, "anchor": "symbol-centre", "symbolSize": 48,
        "readoutExtent": {"right": [64, 48], "left": [64, 48], "bottom": [48, 44], "top": [48, 44],
                          "none": [0, 0]},
        "gate": {"on": "on", "open": "open"}[state] if mode and kind not in PASS_KINDS else None,
        "flow": "pass" if kind in PASS_KINDS else "gated",
        # the identifier lies in the readout, whose padding is 4 px at each side
        "identifier": {"param": "tag", "flag": "hasTag", "font": "automation-label", "pad": 8},
    }
    return doc, contract


# ---------------------------------------------------------------------------------------
# Generator set
# ---------------------------------------------------------------------------------------
# The larger picture of a generator for a unit page (COB-158, gap GG-01): a descriptor symbol of kind
# `generator` with `params.picture = "genset"` draws this view instead of the 48 px symbol. It is our own
# vector drawing of a set: an engine block with its cylinder heads and exhaust, a coupling, an alternator
# with its terminal box and louvres, on a base frame. Running, the bodies take the device's primary colour;
# stopped, the inverted pair, as the automation symbols do. It opens the generator faceplate on a click and
# takes the alarm frame of F016 around its whole box.
GENSET_SIZE = (240, 150)
GENSET_PICTURE = (240, 120)   # the drawing's own proportions; the identifier and the state take the 30 px beneath it
GENSET_PARAMS = {"on": False, "picture": "genset", "tag": "", "hasTag": False, "alert": False,
                 "alertFrameStatus": "alarm", "alertFrameMode": "acked-active", "deviceId": "",
                 "deviceKind": "generator", "deviceLabel": ""}
# (name, path, role): a body part has an outline, a detail only a fill
GENSET_PARTS = (
    ("Skid", rrect_d(6, 98, 228, 10, 2), "detail"),
    ("FootLeft", rrect_d(24, 108, 24, 6, 1), "detail"),
    ("FootRight", rrect_d(192, 108, 24, 6, 1), "detail"),
    ("Engine", rrect_d(22, 48, 104, 50, 6), "body"),
    ("Head1", rrect_d(30, 34, 22, 14, 2), "body"),
    ("Head2", rrect_d(58, 34, 22, 14, 2), "body"),
    ("Head3", rrect_d(86, 34, 22, 14, 2), "body"),
    ("Exhaust", rrect_d(112, 12, 8, 36, 2), "body"),
    ("Coupling", rrect_d(126, 66, 14, 22, 2), "detail"),
    ("Alternator", rrect_d(140, 50, 82, 48, 8), "body"),
    ("Terminals", rrect_d(166, 36, 32, 14, 2), "body"),
    ("Louvre1", rrect_d(152, 58, 3, 32, 1), "detail"),
    ("Louvre2", rrect_d(162, 58, 3, 32, 1), "detail"),
    ("Louvre3", rrect_d(172, 58, 3, 32, 1), "detail"),
    ("Louvre4", rrect_d(182, 58, 3, 32, 1), "detail"),
)


def generator_set() -> tuple[dict, dict]:
    """`Automation/GeneratorSet`: the vector generator set, running or stopped (gap GG-01)."""
    on = "{view.params.on}"
    elements, cfg = [], {}
    for i, (name, d, role) in enumerate(GENSET_PARTS):
        fill = ("var(--automation-device-primary-color)" if role == "body"
                else "var(--automation-device-tertiary-color)")
        el = {"type": "path", "name": name, "d": d, "fill": {"paint": fill}}
        if role == "body":
            el["stroke"] = {"paint": "var(--automation-device-tertiary-color)", "width": 1.5}
            cfg[f"props.elements[{i}].fill.paint"] = pv.bind(pv.expr(
                f"if({on}, 'var(--automation-device-primary-color)', 'var(--automation-device-primary-inverted-color)')"))
            cfg[f"props.elements[{i}].stroke.paint"] = pv.bind(pv.expr(
                f"if({on}, 'var(--automation-device-tertiary-color)', 'var(--automation-device-tertiary-inverted-color)')"))
        else:
            cfg[f"props.elements[{i}].fill.paint"] = pv.bind(pv.expr(
                f"if({on}, 'var(--automation-device-tertiary-color)', 'var(--automation-device-tertiary-inverted-color)')"))
        elements.append(el)
    w, h = GENSET_SIZE
    # A percent container (as the tank's): the set fits the box it is given, the picture centred in its share of
    # the box at its own proportions (`xMidYMid`, the schema's meet), the identifier and the state beneath it (gap GG-01, COB-158; a
    # pixel container left it at the top left of a larger box, L4 item 11)
    picture = pv.node("ia.shapes.svg", "Picture", pv.cpos(0, 0, 1, GENSET_PICTURE[1] / h), {
        "viewBox": f"0 0 {GENSET_PICTURE[0]} {GENSET_PICTURE[1]}", "preserveAspectRatio": "xMidYMid",
        "elements": elements}, prop_config=cfg)
    tag = pv.node("ia.display.label", "Tag", pv.cpos(0, round(122 / h, 6), 1, round(16 / h, 6)), {
        "textStyle": {"textAlign": "center"},
        "style": {"classes": f"cadre/font/automation-label cadre/text/neutral {ELLIPSIS}", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr("{view.params.tag}")),
                     "meta.visible": pv.bind(pv.expr("{view.params.hasTag}"))})
    status = pv.node("ia.display.label", "Status", pv.cpos(0, round(136 / h, 6), 1, round(14 / h, 6)), {
        "textStyle": {"textAlign": "center"},
        "style": {"classes": "cadre/font/automation-value-regular cadre/text/neutral", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr(f"if({on}, 'Running', 'Stopped')"))})
    root = pv.node("ia.container.coord", "root", {}, {"mode": "percent",
                                                       "style": {"overflow": "hidden", "cursor": "pointer"}},
                   events=pv.on_click([
                       "if self.view.params.deviceId:",
                       "	cadre.hmi.select_device(self.session, self.view.params.deviceId, "
                       "self.view.params.deviceKind or 'generator', self.view.params.tag, "
                       "self.view.params.deviceLabel)",
                       *open_faceplate("	")]),
                   children=[picture, tag, status] + _alert_frame())
    doc = pv.view(root, params=dict(GENSET_PARAMS), param_dirs={k: "input" for k in GENSET_PARAMS},
                  size={"width": w, "height": h})
    return doc, {"view": "Automation/GeneratorSet", "kind": "generator", "params": dict(GENSET_PARAMS),
                 "anchor": "box", "flow": "pass", "gate": None, "state": "on",
                 "identifier": {"param": "tag", "flag": "hasTag", "font": "automation-label", "pad": 0}}


# ---------------------------------------------------------------------------------------
# Tank
# ---------------------------------------------------------------------------------------
TANK_PARAMS = {"value": 0, "max": 100, "unit": "m³", "valueFractionDigits": 0, "tag": "", "hasTag": True,
               "trend": "stable", "showPercent": True, "medium": "normal",
               "chart": False, "history": [], "deviceId": "", "compact": False, "static": False,
               "hasCapacity": True, "deviceLabel": ""}
# The tile of a static tank inside the tank's box, as fractions of the box (x, y, width, height): the
# identifier lies beneath it. A pipe at the left, the right or the top of a static tank ends at the tile
# (`diagram.connection_point`), where it ends at the box of a live one, whose vessel fills its box.
STATIC_TILE = (0.06, 0.06, 0.88, 0.66)

TANK_TAG_WIDTH = 0.86   # of the tile's width: the identifier's label of a live tank
# The room a static tank needs: a vessel with no measurement draws only its tile and its identifier, so it
# needs far less than a live tank: the size the fixture's break tank is drawn at, seen on the gateway on
# 2026-10-11 (a tile of about 53 px above the identifier's line). The view is in percent coordinates and
# draws at any size; this is the least a layouter may give it, and a longer identifier needs its own width
# (`identifier`).
STATIC_TANK_SIZE = (96, 80)

TREND_ICONS = {"fast-rising": "chevron-double-up-google", "rising": "arrow-up-google",
               "stable": "arrow-right-google", "falling": "arrow-down-google",
               "fast-falling": "chevron-double-down-google"}


def tank() -> tuple[dict, dict]:
    """An atmospheric tank tile in percent coordinates, so one view serves every size the
    reference demo uses (72x138 to 248x220): vessel outline, ID tag, trend and percentage,
    value over maximum, and a level box filled to value/max."""
    pct = "if({view.params.max} > 0, 100.0 * {view.params.value} / {view.params.max}, 0)"
    vessel = svg("Vessel", pv.cpos(0, 0, 1, 1), [
        {"type": "path", "name": "outline", "d": "M2 22C2 10 12 3 24 2H76C88 3 98 10 98 22V97C98 98 97 99 96 99H4C3 99 2 98 2 97Z",
         "fill": {"paint": "var(--instrument-frame-primary-color)"},
         "stroke": {"paint": "var(--instrument-frame-tertiary-color)", "width": 1},
         "vectorEffect": "non-scaling-stroke"}],
        view_box="0 0 100 100", props={"preserveAspectRatio": "none"},
        visible="!{view.params.static}")
    # A static tank (the package `.tank-frame.static`): a plain tile in the section colour with
    # the capacity centred and the ID tag below it. `hasCapacity` false draws no capacity: a vessel
    # whose capacity nobody states shows none (the parameter's default would be an invented number).
    static_tile = svg("StaticTile", pv.cpos(*STATIC_TILE), [
        {"type": "path", "name": "tile", "d": "M4 0H96Q100 0 100 4V96Q100 100 96 100H4Q0 100 0 96V4Q0 0 4 0Z",
         "fill": {"paint": "var(--container-section-color)"},
         "stroke": {"paint": "var(--instrument-frame-tertiary-color)", "width": 1},
         "vectorEffect": "non-scaling-stroke"}],
        view_box="0 0 100 100", props={"preserveAspectRatio": "none"}, visible="{view.params.static}")
    static_value = pv.node("ia.display.label", "StaticValue", pv.cpos(0.06, 0.26, 0.88, 0.24), {
        "textStyle": {"textAlign": "center"},
        "style": {"classes": "cadre/font/instrument-value-small-neutral cadre/text/neutral",
                  "whiteSpace": "nowrap", "justifyContent": "center"}},
        prop_config={"props.text": pv.bind(pv.expr("numberFormat({view.params.max}, '0') + ' ' + {view.params.unit}")),
                     "meta.visible": pv.bind(pv.expr("{view.params.static} && {view.params.hasCapacity}"))})
    static_tag = pv.node("ia.display.label", "StaticTag", pv.cpos(0.0, 0.76, 1.0, 0.2), {
        "textStyle": {"textAlign": "center"},
        "style": {"classes": f"cadre/font/instrument-label cadre/text/neutral {ELLIPSIS}", "whiteSpace": "nowrap",
                  "justifyContent": "center"}},
        prop_config={"props.text": pv.bind(pv.expr("{view.params.tag}")),
                     "meta.visible": pv.bind(pv.expr("{view.params.static} && {view.params.hasTag}"))})
    level_box = svg("Level", pv.cpos(0.08, 0.62, 0.84, 0.3), [
        {"type": "path", "name": "box", "d": "M0 0H100V100H0Z",
         "fill": {"paint": "var(--instrument-frame-primary-color)"},
         "stroke": {"paint": "var(--instrument-frame-tertiary-color)", "width": 1},
         "vectorEffect": "non-scaling-stroke"},
        {"type": "path", "name": "fill", "d": "M0 100H100V100H0Z",
         "fill": {"paint": "var(--instrument-regular-tertiary-color)"}}],
        view_box="0 0 100 100", props={"preserveAspectRatio": "none"},
        extra_config={"props.elements[1].d": pv.bind(pv.expr(
            f"'M0 ' + toStr(100 - if({pct} > 100, 100, if({pct} < 0, 0, {pct}))) + 'H100V100H0Z'"))})
    # Typography follows the package `automation-tank.css`: tag in instrument-label neutral; the
    # header's percentage in instrument-value-enhanced-neutral with a smaller unit-styled `%`;
    # the value row as the current value (regular-active) then `/ max unit` (unit style).
    full = "!{view.params.compact} && !{view.params.static}"
    tag = pv.node("ia.display.label", "Tag", pv.cpos(0.07, 0.06, TANK_TAG_WIDTH, 0.09), {
        "style": {"classes": f"cadre/font/instrument-label cadre/text/neutral {ELLIPSIS}", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr("{view.params.tag}")),
                     "meta.visible": pv.bind(pv.expr("!{view.params.static} && {view.params.hasTag}"))})
    trends = [icon_svg(f"Trend_{k.replace('-', '_')}", ic, pv.fpos(basis="24px", shrink=0),
                       visible=f"{{view.params.trend}} = '{k}' && !{{view.params.static}}",
                       paint="var(--element-neutral-color)")
              for k, ic in TREND_ICONS.items()]
    number = pv.node("ia.display.label", "Number", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/instrument-value-enhanced-neutral cadre/text/neutral",
                  "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr(f"numberFormat({pct}, '0')")),
                     "props.style.classes": pv.bind(pv.expr(
                         "if({view.params.compact}, 'cadre/font/instrument-value-regular-neutral', "
                         "'cadre/font/instrument-value-enhanced-neutral') + ' cadre/text/neutral'")),
                     "position.display": pv.bind(pv.expr("!{view.params.static}"))})
    pct_sign = pv.node("ia.display.label", "PercentSign", pv.fpos(shrink=0), {
        "text": "%", "style": {"classes": "cadre/font/instrument-unit cadre/text/neutral"}},
        prop_config={"position.display": pv.bind(pv.expr("!{view.params.static}"))})
    header = pv.node("ia.container.flex", "Header", pv.cpos(0.05, 0.15, 0.9, 0.2), {
        "direction": "row", "alignItems": "baseline", "justify": "flex-end", "style": {"gap": "4px"}},
        prop_config={"props.justify": pv.bind(pv.expr(
            "if({view.params.compact} || {view.params.static}, 'center', 'flex-end')")),
                     "meta.visible": pv.bind(pv.expr("{view.params.showPercent} && !{view.params.static}"))},
        children=trends + [number, pct_sign])
    value_row = pv.node("ia.container.flex", "ValueRow", pv.cpos(0.05, 0.36, 0.9, 0.11), {
        "direction": "row", "alignItems": "flex-end", "justify": "flex-end", "style": {"gap": "2px"}},
        prop_config={"meta.visible": pv.bind(pv.expr(full))},
        children=[
            pv.node("ia.display.label", "Current", pv.fpos(shrink=0), {
                "style": {"classes": "cadre/font/instrument-value-regular-active cadre/text/active",
                          "whiteSpace": "nowrap"}},
                prop_config={"props.text": pv.bind(pv.expr("numberFormat({view.params.value}, '0')"))}),
            pv.node("ia.display.label", "OfMax", pv.fpos(shrink=0), {
                "style": {"classes": "cadre/font/instrument-unit cadre/text/neutral", "whiteSpace": "nowrap"}},
                prop_config={"props.text": pv.bind(pv.expr(
                    "' / ' + numberFormat({view.params.max}, '0') + ' ' + {view.params.unit}"))}),
        ])
    chart = pv.node("ia.display.sparkline", "Chart", pv.cpos(0.08, 0.5, 0.84, 0.42), {
        "color": "var(--instrument-enhanced-secondary-color)"},
        prop_config={"props.points": pv.bind(pv.expr("{view.params.history}")),
                     "meta.visible": pv.bind(pv.expr("{view.params.chart}"))})
    root = pv.node("ia.container.coord", "root", {}, {"mode": "percent", "style": {"overflow": "hidden"}},
                   children=[vessel, static_tile, level_box, chart, tag, header, value_row,
                             static_value, static_tag],
                   events=pv.on_click(["if self.view.params.deviceId:",
                                       "\tcadre.hmi.select_device(self.session, self.view.params.deviceId, 'tank', "
                                       "self.view.params.tag, self.view.params.deviceLabel)",
                                       *open_faceplate("\t")]))
    for c in root["children"]:
        if c["meta"]["name"] == "Level":
            c["propConfig"]["meta.visible"] = pv.bind(pv.expr("!{view.params.chart} && !{view.params.static}"))
    doc = pv.view(root, params=dict(TANK_PARAMS), param_dirs={k: "input" for k in TANK_PARAMS},
                  size={"width": 168, "height": 216})
    contract = {"view": "Automation/Tank", "kind": "tank", "params": dict(TANK_PARAMS),
                "anchor": "box", "flow": "source-sink",
                # the identifier's label takes TANK_TAG_WIDTH of a live tank's tile, whatever the tile's size
                # (`share`), and the whole width of a static one: `pad` is the rest at the view's default
                # width alone, where n characters and `pad` are never less than the n characters need at
                # any width, for n up to IDENTIFIER_CHARS (`tests/test_hmi.py` pins it)
                # `hasTag` hides it (the diagram toolbar's ID-tag button binds it); the faceplate keeps the identifier
                "identifier": {"param": "tag", "flag": "hasTag", "font": "instrument-label",
                               "pad": round(168 * (1 - TANK_TAG_WIDTH)), "share": TANK_TAG_WIDTH},
                # a vessel with no measurement needs less room than a live tank (`STATIC_TANK_SIZE`)
                "sizes": [{"when": {"static": True}, "size": list(STATIC_TANK_SIZE)}]}
    return doc, contract


# ---------------------------------------------------------------------------------------
# Readouts
# ---------------------------------------------------------------------------------------
READOUT_PARAMS = {"label": "", "value": 0, "unit": "", "format": "#,##0", "size": "regular",
                  "hasSetpoint": False, "setpoint": 0, "setpointFormat": "#,##0", "source": "",
                  "align": "end", "tag": "", "hasTag": True, "deviceId": "", "deviceKind": "instrument",
                  "deviceLabel": ""}
# A readout or an instrument field marked as a device opens the instrument faceplate (COB-062), or
# the faceplate of the kind `deviceKind` names: a readout of a controller's process value opens the
# controller (`"deviceKind": "controller"`).
SELECT_INSTRUMENT = ["if self.view.params.deviceId:",
                     "	cadre.hmi.select_device(self.session, self.view.params.deviceId, "
                     "self.view.params.deviceKind or 'instrument', "
                     "self.view.params.tag or self.view.params.label, self.view.params.deviceLabel)",
                     *open_faceplate("\t")]


# The parameters of the automation readout (a value with its unit and, beneath it, its identifier), with their
# defaults, kept here so that the generator knows them without building the view.
# `stretch` (L4 item 4) is for the module's readout, which sizes to its content and centres in its box: true, it fills
# its component box, so readouts of equal boxes show equal widths with aligned values. The library's readout view
# already fills its box, so there it changes nothing.
AUTOMATION_READOUT_PARAMS = {"value": 0, "unit": "", "format": "#,##0.0", "tag": "", "hasTag": False, "label": "",
                             "stretch": False, "deviceId": "", "deviceKind": "instrument", "deviceLabel": ""}


def instrument_field() -> tuple[dict, dict]:
    """A value, its unit and label stacked, the instrument field idiom (value large,
    unit and label small), optionally with a setpoint in the enhanced colour."""
    big = "{view.params.size} = 'enhanced'"
    value = pv.node("ia.display.label", "Value", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/instrument-value-regular-active cadre/text/active",
                  "whiteSpace": "nowrap", "lineHeight": "1"}},
        prop_config={"props.text": pv.bind(pv.expr(
            "numberFormat({view.params.value}, {view.params.format})")),
                     "props.style.classes": pv.bind(pv.expr(
                         f"if({big}, 'cadre/font/instrument-value-enhanced-active', "
                         f"'cadre/font/instrument-value-regular-active') + ' cadre/text/active'"))})
    setpoint = pv.node("ia.display.label", "Setpoint", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/instrument-value-small-neutral", "whiteSpace": "nowrap",
                  "color": "var(--instrument-enhanced-secondary-color)"}},
        prop_config={"props.text": pv.bind(pv.expr(
            "'\u25b8 ' + numberFormat({view.params.setpoint}, {view.params.setpointFormat})")),
                     "position.display": pv.bind(pv.expr("{view.params.hasSetpoint}"))})
    unit = pv.node("ia.display.label", "UnitLabel", pv.fpos(shrink=0), {
        "style": {"classes": f"cadre/font/instrument-unit cadre/text/neutral {ELLIPSIS}", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr(
            "if({view.params.hasTag}, {view.params.label} + if(len({view.params.unit}) > 0, ' ' + {view.params.unit}, ''), "
            "{view.params.unit})"))})
    root = pv.node("ia.container.flex", "root", {},
                   {"direction": "column", "alignItems": "flex-end", "justify": "center",
                    "style": {"overflow": "hidden"}},
                   prop_config={"props.alignItems": pv.bind(pv.expr(
                       "case({view.params.align}, 'center', 'center', 'start', 'flex-start', 'flex-end')"))},
                   events=pv.on_click(SELECT_INSTRUMENT),
                   children=[setpoint, value, unit])
    doc = pv.view(root, params=dict(READOUT_PARAMS), param_dirs={k: "input" for k in READOUT_PARAMS},
                  size={"width": 96, "height": 64})
    return doc, {"view": "Instrument/Field", "kind": "instrument-field",
                 "params": dict(READOUT_PARAMS), "anchor": "box", "flow": "none",
                 # the caption is the label, then a space and the unit where there is one, across the box; `hasTag`
                 # false leaves the unit alone (the diagram toolbar's ID-tag button binds it)
                 "identifier": {"param": "label", "suffix": "unit", "flag": "hasTag", "font": "instrument-unit",
                                "pad": 0},
                 # the setpoint's line, the enhanced value and the caption's line: 16, 34 and 16 px, 2 px more
                 # than the default height (the regular value is 16 px high, and 48 px hold the three)
                 "sizes": [{"when": {"size": "enhanced", "hasSetpoint": True}, "size": [96, FIELD_ENHANCED_SETPOINT]}]}


def automation_readout() -> tuple[dict, dict]:
    """A value with unit on a pipe line (the automation readout idiom)."""
    params = dict(AUTOMATION_READOUT_PARAMS)
    val = pv.node("ia.display.label", "Value", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/automation-value-regular cadre/text/active", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr(
            "numberFormat({view.params.value}, {view.params.format}) + ' ' + {view.params.unit}"))})
    tagl = pv.node("ia.display.label", "Tag", pv.fpos(shrink=0), {
        "style": {"classes": f"cadre/font/automation-label cadre/text/neutral {ELLIPSIS}", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr("{view.params.tag}")),
                     "position.display": pv.bind(pv.expr("{view.params.hasTag}"))})
    root = pv.node("ia.container.flex", "root", {},
                   {"direction": "column", "alignItems": "center", "justify": "center",
                    "style": {"overflow": "hidden", "backgroundColor": "var(--container-global-color)",
                              "border": "1px solid var(--automation-device-tertiary-color)",
                              "borderRadius": "2px", "padding": "0 4px"}},
                   events=pv.on_click(SELECT_INSTRUMENT),
                   children=[val, tagl])
    doc = pv.view(root, params=params, param_dirs={k: "input" for k in params},
                  size={"width": 72, "height": 24})
    return doc, {"view": "Automation/Readout", "kind": "readout", "params": params,
                 "anchor": "symbol-centre", "flow": "pass",
                 # 4 px of padding and the 1 px border at each side
                 "identifier": {"param": "tag", "flag": "hasTag", "font": "automation-label", "pad": 10},
                 "value": {"font": "automation-value-regular", "pad": 10},
                 # the value's line and the identifier's between the two borders: 22, 16 and 2 px
                 "sizes": [{"when": {"hasTag": True}, "size": [72, READOUT_TAGGED]}],
                 # a box smaller than the readout needs is grown about its centre (`screen.grown_box`): the
                 # readout stays on its line, and neither its value nor its identifier is cut by the box
                 "grows": True}


# ---------------------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------------------
# `hasSetpoint` and `hasOutput` default false, as the instrument field's `hasSetpoint` does: a loop
# without `sp` or `out` then draws neither, and a descriptor that sets one for a device without the
# member fails gate G7 devices.
CONTROLLER_PARAMS = {"value": 0, "setpoint": 0, "output": 0, "manual": False, "hasSetpoint": False,
                     "hasOutput": False, "unit": "", "format": "#,##0.0", "label": "", "tag": "", "hasTag": True,
                     "deviceId": "", "deviceKind": "controller", "deviceLabel": ""}


def instrument_controller() -> tuple[dict, dict]:
    """A control loop as one block, the instrument field idiom with the loop's own facts: the
    package control badge (auto, or manual) beside the identifier, the setpoint marked as the
    instrument field marks it, the process value large with its unit, and the output in per cent.
    A click opens the controller faceplate (wiki page 13 section 9)."""
    badges = [icon_svg(f"Badge_{b}", b, pv.fpos(basis="16px", shrink=0), visible=shown)
              for b, shown in (("auto", "!{view.params.manual}"), ("manual", "{view.params.manual}"))]
    name = pv.node("ia.display.label", "Tag", pv.fpos(grow=1, basis="0px"), {
        "style": {"classes": f"cadre/font/automation-label cadre/text/neutral {ELLIPSIS}", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr(
            "if({view.params.hasTag} && len({view.params.tag}) > 0, {view.params.tag}, {view.params.label})"))})
    head = pv.node("ia.container.flex", "Head", pv.fpos(basis="20px", shrink=0),
                   {"direction": "row", "alignItems": "center", "style": {"gap": "4px"}},
                   children=badges + [name])
    setpoint = pv.node("ia.display.label", "Setpoint", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/instrument-value-small-neutral", "whiteSpace": "nowrap",
                  "color": "var(--instrument-enhanced-secondary-color)"}},
        prop_config={"props.text": pv.bind(pv.expr(
            "'\u25b8 ' + numberFormat({view.params.setpoint}, {view.params.format})")),
                     "position.display": pv.bind(pv.expr("{view.params.hasSetpoint}"))})
    value = pv.node("ia.container.flex", "ValueRow", pv.fpos(shrink=0),
                    {"direction": "row", "alignItems": "baseline", "style": {"gap": "4px"}}, children=[
        pv.node("ia.display.label", "Value", pv.fpos(shrink=0), {
            "style": {"classes": "cadre/font/instrument-value-regular-active cadre/text/active",
                      "whiteSpace": "nowrap", "lineHeight": "1"}},
            prop_config={"props.text": pv.bind(pv.expr(
                "numberFormat({view.params.value}, {view.params.format})"))}),
        pv.node("ia.display.label", "Unit", pv.fpos(shrink=0), {
            "style": {"classes": "cadre/font/instrument-unit cadre/text/neutral", "whiteSpace": "nowrap"}},
            prop_config={"props.text": pv.bind(pv.expr("{view.params.unit}"))})])
    output = pv.node("ia.display.label", "Output", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/instrument-unit cadre/text/neutral", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr("'Out ' + numberFormat({view.params.output}, '0') + ' %'")),
                     "position.display": pv.bind(pv.expr("{view.params.hasOutput}"))})
    root = pv.node("ia.container.flex", "root", {},
                   {"direction": "column", "alignItems": "stretch", "justify": "center",
                    "style": {"overflow": "hidden", "backgroundColor": "var(--container-global-color)",
                              "border": "1px solid var(--automation-device-tertiary-color)",
                              "borderRadius": "4px", "padding": "2px 6px", "gap": "2px", "cursor": "pointer"}},
                   events=pv.on_click(["if self.view.params.deviceId:",
                                       "	cadre.hmi.select_device(self.session, self.view.params.deviceId, "
                                       "self.view.params.deviceKind or 'controller', "
                                       "self.view.params.tag or self.view.params.label, self.view.params.deviceLabel)",
                                       *open_faceplate("\t")]),
                   children=[head, setpoint, value, output])
    doc = pv.view(root, params=dict(CONTROLLER_PARAMS), param_dirs={k: "input" for k in CONTROLLER_PARAMS},
                  size={"width": 120, "height": 96})
    return doc, {"view": "Instrument/Controller", "kind": "controller", "params": dict(CONTROLLER_PARAMS),
                 "anchor": "box", "flow": "pass",
                 # 6 px of padding and the 1 px border at each side, the 16 px badge and its 4 px gap
                 "identifier": {"param": "tag", "flag": "hasTag", "font": "automation-label", "pad": 34}}


# ---------------------------------------------------------------------------------------
# Sequence
# ---------------------------------------------------------------------------------------
# `hasStep` defaults false, as the controller's `hasSetpoint` does: a sequence without `step` draws no
# number, and a descriptor that sets it for a device without the member fails gate G7 devices.
SEQUENCE_PARAMS = {"text": "", "step": 0, "hasStep": False, "label": "", "tag": "", "hasTag": True,
                   "deviceId": "", "deviceKind": "sequence", "deviceLabel": ""}


def instrument_sequence() -> tuple[dict, dict]:
    """A sequence as one block, in the manner of the controller's: the identifier or the label, the
    text of the current step large, and the step number small beneath it ("Step 2"). The text comes
    from the tag model, which knows the steps; the number is formatted whole, whatever type the tag
    holds. A click opens the sequence faceplate (wiki page 13 section 9.7)."""
    name = pv.node("ia.display.label", "Tag", pv.fpos(basis="20px", shrink=0), {
        "style": {"classes": f"cadre/font/automation-label cadre/text/neutral {ELLIPSIS}", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr(
            "if({view.params.hasTag} && len({view.params.tag}) > 0, {view.params.tag}, {view.params.label})"))})
    text = pv.node("ia.display.label", "Text", pv.fpos(shrink=0), {
        "style": {"classes": f"cadre/font/instrument-value-regular-active cadre/text/active {ELLIPSIS}",
                  "whiteSpace": "nowrap", "lineHeight": "1"}},
        prop_config={"props.text": pv.bind(pv.expr("{view.params.text}"))})
    step = pv.node("ia.display.label", "Step", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/instrument-unit cadre/text/neutral", "whiteSpace": "nowrap"}},
        prop_config={"props.text": pv.bind(pv.expr("'Step ' + numberFormat({view.params.step}, '0')")),
                     "position.display": pv.bind(pv.expr("{view.params.hasStep}"))})
    root = pv.node("ia.container.flex", "root", {},
                   {"direction": "column", "alignItems": "stretch", "justify": "center",
                    "style": {"overflow": "hidden", "backgroundColor": "var(--container-global-color)",
                              "border": "1px solid var(--automation-device-tertiary-color)",
                              "borderRadius": "4px", "padding": "2px 6px", "gap": "2px", "cursor": "pointer"}},
                   events=pv.on_click(["if self.view.params.deviceId:",
                                       "	cadre.hmi.select_device(self.session, self.view.params.deviceId, "
                                       "self.view.params.deviceKind or 'sequence', "
                                       "self.view.params.tag or self.view.params.label, self.view.params.deviceLabel)",
                                       *open_faceplate("\t")]),
                   children=[name, text, step])
    doc = pv.view(root, params=dict(SEQUENCE_PARAMS), param_dirs={k: "input" for k in SEQUENCE_PARAMS},
                  size={"width": 144, "height": 72})
    return doc, {"view": "Instrument/Sequence", "kind": "sequence", "params": dict(SEQUENCE_PARAMS),
                 "anchor": "box", "flow": "pass",
                 # 6 px of padding and the 1 px border at each side
                 "identifier": {"param": "tag", "flag": "hasTag", "font": "automation-label", "pad": 14}}


def library_views() -> dict[str, tuple[dict, dict]]:
    out = {}
    for k in DEVICE_KINDS:
        doc, c = automation_symbol(k)
        out[f"Automation/{k}"] = (doc, c)
    out["Automation/Tank"] = tank()
    out["Automation/Readout"] = automation_readout()
    out["Instrument/Field"] = instrument_field()
    out["Instrument/Controller"] = instrument_controller()
    out["Instrument/Sequence"] = instrument_sequence()
    out["Automation/GeneratorSet"] = generator_set()
    from . import parts   # the page parts (COB-159): the range bar and the embedded trends
    out.update(parts.library_views())
    return out
