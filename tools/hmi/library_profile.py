"""The library profile: what `cadre_hmi_base` offers a tool that writes screen descriptors.

A bridge that turns a source project into devices and descriptors (ctig, COB-050) must know which
device kinds the library draws, which faceplate each opens, which tag members that faceplate binds
and which of them a device may omit, which members a session may write and through which write
path, and which functions (alarm list, interlocks, trend) come with a kind. The profile states
exactly that, generated from the generator's own tables so it cannot drift from the code:

    kinds        symbol kind -> view, flow role, faceplate, members, pulse members, trended member,
                 default size, the sizes its flags need, its identifier and embed boxes
    text         the fonts a block is sized against and the length an identifier may have
    diagram      where a pipe meets a symbol and how a pipe is routed
    deviceKinds  device kind (the `kind` of a device model) -> faceplate, members, pulse members,
                 binding rule, trended members; the kind `local` (a local assembly's device, NOTE-WFB-10
                 section 11.2) names no member and takes any (`openMembers`)
    faceplates   faceplate view -> its tabs
    writePaths   write path -> the members it may write, the role it needs, the checked function
    forceEncodings  the two forms of a force, each a pair of members a device carries whole or not at all
    functions    the device functions the frame provides

Every member is optional (`required` false): a faceplate lists what a device carries (wiki page 13
section 9). Gate G7 devices checks a device model against `deviceKinds` and `writePaths`.

`parent.py` writes it to `library/profile.json` beside `library/contracts.json`; ctig keeps a copy
as a target profile (`profiles/target/cadre-hmi-base/library.json`).

Usage:
    python tools/hmi/library_profile.py [--out library/profile.json] [--out <other copy>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import alarms, diagram, framework, library, parts, scripts, screen  # noqa: E402
else:
    from . import alarms, diagram, framework, library, parts, scripts, screen

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "cadre-hmi-library/1"
LOCAL_KIND = "local"   # the device kind of a local assembly (`assembly.LOCAL_KIND`)


def _members(kind: str) -> dict:
    return {name: {"type": dtype, "required": False} for name, dtype in sorted(screen.known_members(kind).items())}


def build(contracts: dict, parent: str = "cadre_hmi_base") -> dict:
    """The profile of `contracts`, naming the parent project it describes (`library`): `cadre_hmi_base` unless a second
    parent is given, for example the ASM build `cadre_hmi_base_asm` (WFB-153)."""
    if not parent.startswith("cadre_hmi"):
        raise ValueError(f"a parent's name starts cadre_hmi: {parent}")
    kinds = {}
    for kind, view in sorted(screen.KIND_VIEW.items()):
        c = contracts.get(view, {})
        members = _members(kind)
        role = diagram.node_role(kind)
        kinds[kind] = {"view": view,
                       "flow": role,
                       "gate": diagram.GATED.get(kind),
                       "anchor": c.get("anchor"),
                       "faceplate": framework.FACEPLATE_VIEW.get(kind),
                       "members": members,
                       "bind": {p: m for p, m in sorted(screen.bind_rule(kind).items())
                                if p in c.get("params", {}) and m in members},
                       "trend": screen.TREND_KINDS.get(kind),
                       "interlocks": has_interlocks(kind),
                       "maintenance": any(m.startswith("mnt/") for m in members),
                       "pulses": screen.pulse_members(kind),
                       "module": screen.MODULE_KIND.get(kind),
                       # when the library's own view draws the symbol under the module rendering instead:
                       # parameter sets that keep it there, and parameter values the module's component needs
                       "moduleExcept": screen.MODULE_EXCEPT.get(kind, []),
                       "moduleNeeds": screen.MODULE_NEEDS.get(kind, {}),
                       "params": sorted(c.get("params", {})),
                       # what a layouter needs: the view's default size, and for an automation symbol the
                       # box the descriptor gives (the symbol) and the box the embed occupies on each side
                       "size": c.get("size"),
                       "symbolSize": c.get("symbolSize"),
                       "embedBox": embed_boxes(kind, c),
                       # the sizes the block needs with flags that the default size does not hold, the
                       # first entry whose `when` the symbol's parameters meet (`library.block_size`)
                       "sizes": c.get("sizes", []),
                       # whether the generator grows a box smaller than the block needs, about its centre
                       # (`screen.grown_box`); false: the box is used as given and gate G5 warns
                       "grows": bool(c.get("grows", False)),
                       # where the kind draws its identifier and how many characters its default size holds
                       "identifier": identifier(kind, c),
                       "value": c.get("value")}
    device_kinds = {}
    for kind, view in sorted(framework.FACEPLATE_VIEW.items()):
        if kind == LOCAL_KIND:   # below: the device of a local assembly knows no member
            continue
        members = _members(kind)
        main = screen.TREND_KINDS.get(kind)
        device_kinds[kind] = {"faceplate": view,
                              # the faceplate of each style (COBD-045): `asm` falls back to `openbridge`
                              "faceplates": {s: framework.faceplate_view(kind, s) for s in framework.FACEPLATE_STYLES},
                              "members": members,
                              "bind": {p: m for p, m in sorted(screen.bind_rule(kind).items()) if m in members},
                              "trend": ([main] if main else []) + sorted(screen.TREND_ALSO.get(kind, {})),
                              "interlocks": has_interlocks(kind),
                              "maintenance": any(m.startswith("mnt/") for m in members),
                              # the members a session pulses (W18): a device model marks each `pulse`
                              "pulses": screen.pulse_members(kind),
                              # its faceplate draws the Config rows of members marked `config` (F010)
                              "config": framework.has_config(kind)}
    # the device of a local assembly (NOTE-WFB-10 section 11.2 item 4): no member is required or known, so gate G7
    # devices accepts every member a devices file lists for it (`openMembers`); its faceplate is the library's local
    # one where the library has it
    device_kinds[LOCAL_KIND] = {"faceplate": framework.faceplate_view(LOCAL_KIND),
                                "faceplates": {s: framework.faceplate_view(LOCAL_KIND, s) for s in framework.FACEPLATE_STYLES},
                                # the controller acknowledgement bit is optional on every device (F049, `ackRelay`)
                                "members": {scripts.constant("ACK_MEMBER"): {"type": "Boolean", "required": False}},
                                "bind": {}, "trend": [], "interlocks": False, "maintenance": False,
                                "pulses": [], "config": False, "openMembers": True}
    faceplates = {}
    for key, tabs in sorted(framework.FACEPLATE_TABS.items()):
        faceplates["Faceplate/" + key.capitalize()] = {"tabs": [t for t, _label in tabs]}
    for view in sorted(set(framework.ASM_VIEW.values())):
        faceplates[view] = {"tabs": [t for t, _label in framework.asm_tabs(view)], "style": "asm"}
    write_paths = scripts.constant("WRITE_PATHS")
    members = {**scripts.constant("PATH_MEMBERS"), **scripts.constant("FUNCTION_MEMBERS")}
    role = scripts.constant("ADMIN_ROLE")
    return {"schema": SCHEMA,
            "library": parent,
            "descriptor": "cadre-hmi-screen/1",
            "devices": "cadre-hmi-devices/1",
            "kinds": kinds,
            "deviceKinds": device_kinds,
            "faceplates": faceplates,
            # the controller acknowledgement bit (F049): optional per device, written true on an acknowledgement
            "ackRelay": {"member": scripts.constant("ACK_MEMBER"), "value": True,
                         "paths": sorted(w for w, m in scripts.constant("FUNCTION_MEMBERS").items()
                                         if scripts.constant("ACK_MEMBER") in m)},
            # the one form of an alarm in a tag model over the library (F028, F042, F043, F045; tools/hmi/alarms.py)
            "alarms": alarms.form(),
            # the configuration members (F010): their folder, their write path and the types they take
            "config": {"prefix": framework.CONFIG_PREFIX, "path": framework.CONFIG_PATH,
                       "types": list(CONFIG_TYPES), "captionMax": CONFIG_CAPTION_MAX},
            # the faceplate's style and place (COBD-045): the defaults, and the popup the pin opens
            "faceplate": {"styles": list(framework.FACEPLATE_STYLES), "style": "openbridge",
                          "modes": list(library.FACEPLATE_MODES), "mode": "dock",
                          "popup": {"view": library.FACEPLATE_POPUP_VIEW, "id": library.FACEPLATE_POPUP_ID,
                                    "size": [framework.POPUP_SIZE["width"], framework.POPUP_SIZE["height"]]}},
            "writePaths": {w: {"members": members.get(w, []), "role": role, "what": WRITE_WHAT.get(w, ""),
                               "function": WRITE_FUNCTION.get(w, "command" if w in members else "")}
                           for w in write_paths},
            "forceEncodings": [scripts.constant("MNT_FORCE_PAIR"), scripts.constant("MNT_FORCE_MODE")],
            # ownership by mode (COBD-044): the owners a device model's `modes` may name, the write paths
            # an owner gates and those each owner lets write; W2 moves ownership between them
            "ownership": {"owners": scripts.constant("OWNERS"), "gated": scripts.constant("OWNER_GATED"),
                          "paths": scripts.constant("OWNER_PATHS"), "move": "W2"},
            "frame": FRAME,
            "text": {"identifierChars": library.IDENTIFIER_CHARS, "fonts": library.FONTS},
            "diagram": {"ring": diagram.RING, "symbol": 48, "staticTile": list(library.STATIC_TILE),
                        "routes": dict(diagram.ROUTES), "via": diagram.VIA,
                        # two boxes overlap when they share more than this many px on both axes (gate G5,
                        # and the room an identifier has beside the next symbol, `screen.embed_limits`)
                        "overlap": screen.OVERLAP},
            "functions": sorted(FUNCTIONS),
            # the page parts a descriptor may add to a diagram (COB-159): buttons, bars, trends, lines, and the
            # keys of a symbol (`bar`, `alarm`); the history a trend's pens need
            "parts": parts.profile()}


def identifier(kind: str, contract: dict) -> dict | None:
    """Where a kind draws its identifier: the parameter that holds it (`param`), the flag that shows it
    (`flag`, None where it is always drawn), its font (a key of `text.fonts`), the width in px the block
    takes beside the text (`pad`), and the number of characters the default size holds (`fits`). The
    width a block needs for n characters is `n * text.fonts[font].charWidth + pad`
    (`library.identifier_width`), n no more than `text.identifierChars`. For an automation symbol the
    width is the readout's: beneath or above the symbol the embed is at least that wide, beside the
    symbol the embed is 48 px wider than it (`screen.readout_extent`), and `fits` counts the default
    embed beneath the symbol. A tank alone has `share`: the identifier of a live tank takes that share
    of the tile's width at any size (n characters need `n * charWidth / share` px; a static tank gives
    its identifier the whole width), and `pad` and `fits` are the same fact at the default width."""
    ident = contract.get("identifier")
    if not ident:
        return None
    boxes = embed_boxes(kind, contract)
    width = boxes["bottom"][2] if boxes else contract["size"][0]
    return {**ident, "fits": int((width - ident["pad"]) // library.FONTS[ident["font"]]["charWidth"])}


def embed_boxes(kind: str, contract: dict) -> dict | None:
    """The box an automation symbol's embed occupies for each `readoutPosition`, as offsets from the 48 px
    symbol box the descriptor gives (`screen.symbol_box`, computed here by calling it, never restated):
    `[dx, dy, width, height]`. None for a kind whose box is used as given."""
    if contract.get("anchor") != "symbol-centre" or kind == "readout":
        return None
    out = {}
    for pos in ("bottom", "top", "left", "right", "none"):
        x, y, w, h = screen.symbol_box({"kind": kind, "x": 0, "y": 0, "params": {"readoutPosition": pos}}, contract)
        out[pos] = [x, y, w, h]
    return out


# Facts of the frame and of the existing diagrams that bound a page: the docks (`framework.shared_docks`),
# the viewport the render gate captures (`tools/compare/capture.py`), and the canvas of the sample plant's
# diagrams (`tools/plants/wtp.py`), which fits that viewport beside the open faceplate dock.
FRAME = {"topDock": 48, "faceplateDock": 400, "viewport": [1600, 900], "diagramCanvas": [1580, 600],
         "cardsCanvas": [1600, 852]}
ILK_FACEPLATES = ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/ASM/Sequence")   # the sequence's asm faceplate (COB-158)


def has_interlocks(kind: str) -> bool:
    """A faceplate of the kind in some style carries the Interlock tab: a device of the kind may list `ilk`."""
    return any(framework.faceplate_view(kind, s) in ILK_FACEPLATES for s in framework.FACEPLATE_STYLES)
# The types a configuration member may take (the setpoint row is a numeric entry field) and the length
# of its caption (the row's label is 132 px wide).
CONFIG_TYPES = ("Int1", "Int2", "Int4", "Int8", "Float4", "Float8")
CONFIG_CAPTION_MAX = 24
# What each write path writes (NOTE-COB-04 Table 7).
WRITE_WHAT = {"W1": "start, stop, open, close", "W2": "control mode", "W3": "speed setpoint", "W4": "alarm limit",
              "W5": "fault reset", "W6": "acknowledge from the top bar", "W7": "stock alarm table actions",
              "W8": "acknowledge a row of the alarm menu", "W9": "acknowledge the visible alarms",
              "W10": "interlock bypass", "W11": "trip reset", "W12": "controller setpoint", "W13": "loop mode",
              "W14": "manual output", "W15": "controller tuning", "W16": "force", "W17": "object error mask",
              "W18": "pulse command", "W19": "configuration value"}
# The checked function of `cadre.hmi` behind a write path; `command` where the path has members and no
# function of its own, and none for the stock table, which acts itself (W7).
WRITE_FUNCTION = {"W6": "ack_top", "W8": "ack_event", "W9": "ack_event", "W10": "bypass", "W11": "reset_interlocks",
                  "W16": "force", "W17": "error_mask", "W18": "pulse", "W19": "configure"}
# Device functions of the frame (wiki pages 06 and 13).
FUNCTIONS = {"alarm-list", "alarm-limits", "interlocks", "trend", "trend-page", "force", "error-mask",
             "pid-faceplate", "pid-tuning", "pulse-command"}


def write(contracts: dict, outs: list[Path] | None = None, parent: str = "cadre_hmi_base") -> list[Path]:
    """Write the profile for `contracts`, by default to library/profile.json. Another tool may read
    the file while it is rewritten (ctig reads it for its census), so the text goes to a file beside
    it, which then replaces it in one step: a reader meets the old profile or the new one, never half
    of one. Where the replacement is refused (Windows refuses it while a reader holds the file open)
    it is tried again, and the file is written in place only as the last resort."""
    text = json.dumps(build(contracts, parent), indent=1, sort_keys=True) + "\n"
    outs = outs or [ROOT / "library" / "profile.json"]
    for out in outs:
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text(text, encoding="utf-8", newline="\n")
        for _attempt in range(10):
            try:
                os.replace(tmp, out)
                break
            except PermissionError:
                time.sleep(0.1)
        else:
            out.write_text(text, encoding="utf-8", newline="\n")
            tmp.unlink()
    return outs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", action="append", type=Path,
                    help="where to write the profile; repeatable (default library/profile.json)")
    ap.add_argument("--parent", default="cadre_hmi_base",
                    help="the parent project the profile names (default cadre_hmi_base; the ASM build is cadre_hmi_base_asm)")
    a = ap.parse_args()
    contracts = json.loads((ROOT / "library" / "contracts.json").read_text(encoding="utf-8"))
    for out in write(contracts, a.out, a.parent):
        print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
