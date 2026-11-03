"""The plan of the generated operator walk: pure and offline (`walk.py plan`).

From the descriptors, the device model, the tag model, the effects file and the library profile this
module writes a plan (`cadre-hmi-walk/1`): the steps of the groups N, D, T, C, R, A and P, the parity
scenes, and what no step reaches, each with its reason. It reads no clock and no gateway, and the same
inputs give the same bytes. It also holds what both sides need: the format of a number on the glass,
the glass table (what the walk must know of the faceplates and the symbols, pinned by
`tests/test_walk.py`) and the validation of an effects file.

`walk.py` is the command line and exports every name of this module; `walk_run.py` runs a plan on the
gateway. Wiki page 08 section 9 is the manual.
"""
from __future__ import annotations

import json
import math
import re
import struct
import sys
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))

SCHEMA = "cadre-hmi-walk/1"
EFFECTS_SCHEMA = "cadre-hmi-walk-effects/1"
RESULT_SCHEMA = "cadre-hmi-walk-result/1"
GROUPS = ("N", "D", "T", "C", "R", "A", "P")



# ---------------------------------------------------------------------------------------
# The format of a number on the glass
# ---------------------------------------------------------------------------------------
# The library's views format with the expression function `numberFormat` and a Java decimal pattern
# (`tools/hmi/library.py`: '0', '0.0', '0.00', '#,##0', '#,##0.0'). The subset implemented: an integer
# part of `#`, `0` and one grouping comma, with every `0` after every `#`; an optional fraction of `0`
# then `#`. Java rounds half even on the value of the double, so the value is taken through
# `Decimal(float)`; a Float4 tag hands Java its 32 bit value widened, so a value of such a tag is
# taken through its 32 bit form first (`data_type`). Anything else (a percent, an exponent, a prefix, a
# second pattern for negatives) is refused: a guess would make the parity check agree with itself.
# Refused as well, because Java's `DecimalFormat` was measured to differ there (JDK 17.0.20.1, locale
# en_AU, 2026-10-11, 237,364 comparisons agreeing elsewhere): a value other than zero below one unit of
# the pattern (0.0005 under three fraction digits is '0.000' in Java), a negative zero ('-0' in Java),
# and a magnitude of 1e15 or more, where the double has no digit to spare.
_PATTERN = re.compile(r"^(?P<int>[#,]*[0,]*0)(?:\.(?P<zeros>0*)(?P<hashes>#*))?$")


def number_format(value, pattern: str, data_type: str | None = None) -> str:
    """`value` as the expression function `numberFormat(value, pattern)` writes it, for the patterns
    the descriptors use. Raises ValueError for a pattern or a value outside what is implemented."""
    m = _PATTERN.match(pattern or "")
    if not m or ("." in pattern and not (m.group("zeros") or m.group("hashes"))):
        raise ValueError(f"number pattern {pattern!r} is not implemented")
    integer = m.group("int")
    if integer.startswith(",") or integer.count(",") > 1:
        raise ValueError(f"number pattern {pattern!r} is not implemented (its grouping)")
    group = len(integer) - integer.rindex(",") - 1 if "," in integer else 0
    min_int = integer.count("0")
    min_frac = len(m.group("zeros") or "")
    max_frac = min_frac + len(m.group("hashes") or "")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{value!r} is not a number")
    number = float(value)
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"{value!r} has no decimal form")
    if data_type == "Float4":   # the 32 bit value, as Java widens it
        number = struct.unpack("<f", struct.pack("<f", number))[0]
    if abs(number) >= 1e15:
        raise ValueError(f"{value!r} has more digits than a double holds exactly: what Java writes for it "
                         "was measured to differ")
    if number == 0 and math.copysign(1.0, number) < 0:
        raise ValueError("a negative zero: Java writes '-0' for it")
    unit = Decimal(1).scaleb(-max_frac)
    d = Decimal(number)
    if number != 0 and abs(d) < unit:
        raise ValueError(f"{value!r} is below one unit of {pattern!r}: what Java writes for it was measured "
                         "to differ from half even on the exact value")
    q = d.quantize(unit, rounding=ROUND_HALF_EVEN)
    whole, _, frac = format(abs(q), "f").partition(".")
    frac = frac.rstrip("0").ljust(min_frac, "0") if max_frac else ""
    whole = whole.zfill(min_int)
    if group:
        parts = []
        while len(whole) > group:
            parts.insert(0, whole[-group:])
            whole = whole[:-group]
        whole = ",".join([whole] + parts)
    return ("-" if q < 0 else "") + whole + ("." + frac if frac else "")


def decimals_of(pattern: str) -> int:
    """The fraction digits a pattern writes at most."""
    m = _PATTERN.match(pattern or "")
    return len(m.group("zeros") or "") + len(m.group("hashes") or "") if m else 0


# ---------------------------------------------------------------------------------------
# The glass table: what the walk must know of the faceplates and the symbols
# ---------------------------------------------------------------------------------------
# One row per fact, so that `tests/test_walk.py` can pin each against the built view that draws it. It
# lives here for now: `tools/hmi/` holds the same strings in code (`framework.faceplate`,
# `faceplate_controller`, `_maintenance_pane`, `scripts.LIMITS`), and a profile that states them would
# replace this table.
KIND_ALIAS = {"readout": "instrument", "instrument-field": "instrument"}
FIRST_TAB = {"Faceplate/Pump": "Control", "Faceplate/Valve": "Control", "Faceplate/Controller": "Control",
             "Faceplate/Instrument": "Values", "Faceplate/Tank": "Values", "Faceplate/Input": "Status",
             "Faceplate/Sequence": "Status", "Faceplate/ASM/Generator": "Home"}
# The tabs of an `asm` faceplate (COBD-045) under the names this table gives them: the plan writes a
# step of a device in that style with the tab the device shows (`framework.ASM_TABS`).
ASM_TAB = {"Control": "Home", "Maintenance": "Config", "Interlocks": "Interlock", "Status": "Home", "Values": "Home"}
# F029 (COBD-045): the faceplate's Confirm row and a row's Set, which the walk presses after a command and
# after an entry (`glass.Confirmed`, `glass.type_into`), and whose handlers a crafted client calls.
CONFIRM, CANCEL, SET = "Confirm", "Cancel", "Set"
# W1: the two command buttons, on then off
COMMANDS = {"Faceplate/Pump": ("Start", "Stop"), "Faceplate/Valve": ("Open", "Close")}
# the State row: its caption, and what it reads for true and for false
STATE_ROW = {"Faceplate/Pump": ("State", "Running", "Stopped"), "Faceplate/Valve": ("State", "Open", "Closed"),
             "Faceplate/Input": ("State", "On", "Off")}
# W2: the mode buttons with the value each writes; the row reads the caption of the mode
MODES = (("Auto", 0), ("Manual", 1), ("Local", 2))
MODE_ROW = "Control mode"
# W3, W12, W14, W15: a setpoint row's caption and the format of its field, by member
SETPOINTS = {"speedSp": ("W3", "Control", "Speed setpoint (%)", "0.0"),
             "sp": ("W12", "Control", "Setpoint", "0.00"),
             "manOut": ("W14", "Control", "Manual output (%)", "0.0"),
             "gain": ("W15", "Tuning", "Gain", "0.000"),
             "ti": ("W15", "Tuning", "Integral time (ms)", "0"),
             "td": ("W15", "Tuning", "Derivative time (ms)", "0")}
SETPOINT_VIEW = {"speedSp": "Faceplate/Pump", "sp": "Faceplate/Controller", "manOut": "Faceplate/Controller",
                 "gain": "Faceplate/Controller", "ti": "Faceplate/Controller", "td": "Faceplate/Controller"}
# the range `cadre.hmi.command` enforces for a member (`scripts.MEMBER_BOUNDS`); None is open
BOUNDS = {"speedSp": (0, 100), "manOut": (0, 100), "ti": (0, None), "td": (0, None),
          # a limit's on-delay in seconds (F028, COB-140)
          "hiHiLimitDelay": (0, 3600), "hiLimitDelay": (0, 3600), "loLimitDelay": (0, 3600), "loLoLimitDelay": (0, 3600)}
# W4: a limit row's caption by member (`scripts.LIMITS`), the field's format, what its lamp reads
LIMITS = {"hiHiLimit": "High high limit", "hiLimit": "High limit", "loLimit": "Low limit", "loLoLimit": "Low low limit"}
LIMIT_FORMAT = "0.00"
LIMIT_LAMP = ("Normal", "Active")
REFUSED = "Refused"
# the member whose value the limits of a faceplate stand beside
VALUE_MEMBER = {"Faceplate/Instrument": "value", "Faceplate/Controller": "value", "Faceplate/Tank": "level"}
# W5
FAULT = {"button": "Reset fault", "row": "Fault", "set": "Fault", "clear": "Normal"}
# W10: one button whose caption follows the state, and the lamp of a bypassed condition
BYPASS = {"tab": "Interlocks", "set": "Bypass", "clear": "Unbypass", "lamp": "Bypassed"}
# W11 by a trip (`--trip`, COB-204): the lamp of a condition's row (`Faceplate/InterlockRow`) for each of its
# states, the faceplate head while the device is held (`HeadInterlock`), and the Interlocks tab's reset row
# (`framework._interlocks_pane`)
TRIP = {"tab": "Interlocks", "met": "Met", "tripped": "Not met", "latched": "Latched", "head": "Interlocked",
        "reset": "Reset", "cleared": "A latched trip has cleared"}
# the data types of `ilk/resetAt` that take the walk's integer of milliseconds since the epoch (a 32 bit
# integer overflows: 1.8e12 is far beyond 2**31)
RESET_TYPES = frozenset({"Int8", "Float8"})
# W13: the controller's loop mode
LOOP = (("Auto", False), ("Manual", True))
# W16 and W17, on the Maintenance tab. "Automatic" is the caption of two buttons: `sibling` names
# another button of the group meant.
FORCE = {"tab": "Maintenance", "row": "Force",
         "states": (("auto", "Automatic", "Automatic", "Force on"), ("on", "Force on", "Forced on", None),
                    ("off", "Force off", "Forced off", None))}
MASK = {"tab": "Maintenance", "row": "Object error mask",
        "states": ((True, "Mask", "Masked", None), (False, "Automatic", "Automatic", "Mask"))}
FORCE_VIEWS = ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/Input")
# what the status row of a library symbol reads for its state (`library._status_row`)
SYMBOL_STATE = ("On", "Off")
# the generator set (`params.picture` genset, COB-158) writes its state in words, beneath its identifier
GENSET_STATE = ("Running", "Stopped")
AUTOMATION = ("pump", "motor", "fan", "valve", "analogvalve", "damper", "filter", "switch", "indicator",
              "generator")
SPEED_KINDS = ("pump", "motor", "fan")
# The module component's property that carries each parameter the walk reads, by kind (the glass reads `on`
# for a valve's `open`: `glass.SYMBOL_AT`)
_MOTORISED_PROP = {"on": "on", "speed": "speed", "alert": "frame"}
MODULE_PROP = {"pump": _MOTORISED_PROP, "motor": _MOTORISED_PROP, "fan": _MOTORISED_PROP,
               "tank": {"value": "value"}, "valve": {"open": "on", "alert": "frame"},
               "analogvalve": {"open": "on", "value": "value", "alert": "frame"},
               "damper": {"on": "on", "alert": "frame"},
               "generator": {"on": "on", "alert": "frame"},
               # module 0.3.1 (COB-127): the element's `value` and `setpoint` are the tags' values as bound
               "readout": {"value": "value"}, "instrument-field": {"value": "value", "setpoint": "setpoint"}}
STATE_PARAM = {"valve": "open", "analogvalve": "open"}   # every other automation kind: "on"
FINDABLE = AUTOMATION + ("readout", "instrument-field", "controller", "tank", "sequence")   # kinds `find_text` knows
# W18, a pulse command: one button for each pulse member a device may write, on the first tab of its
# faceplate; its caption is the device model's (`caption`), else the member's name (`cadre.hmi.device`,
# `pulses`). The faceplate of a sequence reads the step number in the row `Step`, and its block
# writes "Step " before it.
PULSE_VIEWS = ("Faceplate/Sequence", "Faceplate/ASM/Generator")
# a pulse button of an `asm` faceplate that stands on a tab other than the first: the generator's service
# data are on Config (`devices_asm.faceplate_generator`, `config_rows`), beside the hours since service
PULSE_TAB = {"cmdServiceDone": "Config"}
# W19, the Config rows of an `asm` faceplate (F010, COB-158): a row's caption, format and bounds are the device
# model's (`config`); the tab is Config
CONFIG_PATH, CONFIG_TAB = "W19", "Config"
# W18 on a page (COB-159, wiki page 05 section 5.1): a descriptor's `buttons` of the type `pulse`. The press asks
# the question with Confirm and Cancel in the button's place; Confirm holds the tag true for the pulse length
PAGE_PULSE = "page-pulse"
STEP_VIEWS = ("Faceplate/Sequence",)   # the faceplates with a Step row
STEP_ROW = ("Step", "0")
BLOCK_STEP = "Step "
# the line a faceplate writes under its buttons when the gateway refuses a command (`_message_line`,
# the text of `cadre.hmi` REFUSED and of every other refusal begins with this word)
MESSAGE_REFUSED = "Refused"
# what the stock alarm table reads in the state column of an alarm nobody acknowledged (GF-40)
UNACKED_ROW = "Active, Unacknowledged"
SETPOINT_MARK = "\u25b8 "   # the mark an instrument field and a controller block put before a setpoint
OUTPUT_TEXT = ("Out ", "0", " %")   # the controller block's output line
QUALITY_LINE = "Bad quality:"
EMPTY_FACEPLATE = "Select a device"
# The frame's own pages carry no symbol of a descriptor, and the top bar's page name is computed from
# the route (`cadre.hmi.page_title`), so on them a title proves no more than the address. What each
# must hold outside the docks instead: the view that draws it, the component and what a row calls it
# (measured 2026-10-11 on the pilot and on both renderings of the sample: /alerts holds one alarm
# status table that is shown, /trends one time series chart for each card, no other page either).
PAGE_HOLDS = {"/trends": ("Trend/Card", "ia.chart.timeseries", "a trend card"),
              "/alerts": ("Framework/AlertsPage", "ia.display.alarmstatustable", "the alarm status table")}
# The seconds a capability step gives the evidence of its own write (the faceplate polls its device
# once a second, a symbol follows its tag). A step waits for the longest `within` of its effects and
# never less than this, so an effect's `within` below it changes nothing.
WAIT_FLOOR = 8
# the path an acknowledgement in the device's own list takes, by rendering (NOTE-COB-04 Table 7)
ACK_PATH = {"stock": "W7", "module": "W8"}
# write paths that belong to no device member: why no generated step reaches them
FRAME_PATHS = {
    "W6": "the top bar's ACK acknowledges the most severe alarm of the frame, not the alarm the walk "
          "raised: pressing it could acknowledge an alarm of the plant (gate G10 F7 covers it on the sample)",
    "W9": "ACK visible acknowledges every alarm the menu shows, the plant's own among them (gate G10 F14 "
          "covers it on the sample)",
    "W11": "the Interlocks tab offers Reset only after a latched trip has cleared, a state only the "
           "plant's logic produces (gate G10 F12 covers it on the sample); `--trip` plans a trip where a "
           "tag document gives one the walk can raise"}


def glass_facts() -> list[tuple[str, str, str]]:
    """Every (view, what, text) the table above states, for the unit test that pins each against the
    built view: `button` a caption, `caption` a row's label, `text` a text an expression writes, `tab`
    a tab's name, `setpoint` and `limit` a row caption a script hands a repeater."""
    out: list[tuple[str, str, str]] = []
    for view, name in FIRST_TAB.items():
        out.append((view, "tab", name))
    for view, pair in COMMANDS.items():
        out += [(view, "button", c) for c in pair]
    for view, (caption, on, off) in STATE_ROW.items():
        out += [(view, "caption", caption), (view, "text", on), (view, "text", off)]
    for view in COMMANDS:
        out += [(view, "button", c) for c, _v in MODES] + [(view, "text", c) for c, _v in MODES]
        out += [(view, "caption", MODE_ROW), (view, "button", FAULT["button"]), (view, "caption", FAULT["row"]),
                (view, "text", FAULT["set"]), (view, "text", FAULT["clear"]), (view, "tab", BYPASS["tab"])]
    for member, (_path, tab, caption, fmt) in SETPOINTS.items():
        out += [(SETPOINT_VIEW[member], "setpoint", caption), (SETPOINT_VIEW[member], "tab", tab),
                (SETPOINT_VIEW[member], "format", f"{member}:{fmt}")]
    for caption in LIMITS.values():
        out.append(("cadre/hmi", "limit", caption))
    out += [("Faceplate/LimitRow", "text", t) for t in LIMIT_LAMP + (REFUSED,)]
    out += [("Faceplate/LimitRow", "format", LIMIT_FORMAT), ("Faceplate/SetpointRow", "text", REFUSED)]
    out += [("Faceplate/InterlockRow", "text", BYPASS[k]) for k in ("set", "clear", "lamp")]
    out += [("Faceplate/Controller", "button", c) for c, _v in LOOP] + [("Faceplate/Controller", "text", c) for c, _v in LOOP]
    out.append(("Faceplate/Controller", "caption", MODE_ROW))
    for view in FORCE_VIEWS:
        out += [(view, "tab", FORCE["tab"]), (view, "caption", FORCE["row"])]
        for _v, button, text, _s in FORCE["states"]:
            out += [(view, "button", button), (view, "text", text)]
    for view in ("Faceplate/Pump", "Faceplate/Valve"):
        out.append((view, "caption", MASK["row"]))
        for _v, button, text, _s in MASK["states"]:
            out += [(view, "button", button), (view, "text", text)]
    out += [("Automation/Pump", "text", t) for t in SYMBOL_STATE] + [("Automation/Valve", "text", t) for t in SYMBOL_STATE]
    out += [("Automation/GeneratorSet", "text", t) for t in GENSET_STATE]
    out += [("Instrument/Controller", "text", OUTPUT_TEXT[0]), ("Instrument/Controller", "text", SETPOINT_MARK),
            ("Instrument/Field", "text", SETPOINT_MARK), ("Faceplate/Empty", "text", EMPTY_FACEPLATE)]
    out += [(view, "caption", STEP_ROW[0]) for view in STEP_VIEWS]
    # the Config tab of the asm faceplates (W19 rows, the generator's service data), and the button each page pulse
    # shows once pressed: the question's Confirm and Cancel (`parts.button_node`)
    out += [(f"Faceplate/ASM/{k}", "tab", CONFIG_TAB) for k in ("Generator", "Sequence", "Instrument")]
    out.append(("Instrument/Sequence", "text", BLOCK_STEP))
    out += [(view, "button", CONFIRM) for view in ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/Controller",
                                                   "Faceplate/Input", "Faceplate/Sequence")]
    out += [("Faceplate/SetpointRow", "button", SET), ("Faceplate/LimitRow", "button", SET),
            ("Faceplate/InterlockRow", "button", CONFIRM)]
    out += [("Faceplate/InterlockRow", "text", TRIP[k]) for k in ("met", "tripped", "latched")]
    out += [(view, k, TRIP[t]) for view in ("Faceplate/Pump", "Faceplate/ASM/Pump")
            for k, t in (("button", "reset"), ("caption", "cleared"))]
    out.append(("Faceplate/ASM/Pump", "text", TRIP["head"]))   # the asm header only (`_asm_header`)
    return out


# ---------------------------------------------------------------------------------------
# Reading the inputs
# ---------------------------------------------------------------------------------------
def split_path(path: str) -> tuple[str, str]:
    """('[default]a/b') gives ('default', 'a/b')."""
    if path.startswith("["):
        prov, rest = path[1:].split("]", 1)
        return prov, rest.strip("/")
    return "default", path.strip("/")


def tag_nodes(doc: dict | None, parent: str = "") -> dict[str, dict]:
    """Every atomic tag of a tag document by its path below the provider (`cadre_hmi_x/P1/state`). The
    document is a folder lying at the provider's root, as the tag model is imported, or under `parent`."""
    out: dict[str, dict] = {}

    def walk(node, path):
        here = f"{path}/{node['name']}" if path else node["name"]
        if node.get("tagType") == "Folder" or "tags" in node:
            for t in node.get("tags", []):
                walk(t, here)
        else:
            out[here] = node
    if doc:
        walk(doc, parent.strip("/"))
    return out


def resolve(path: str, nodes: dict[str, dict]) -> dict:
    """Follow a tag to where its value lives: a memory tag, an expression tag, or a reference tag
    followed through `sourceTagPath` (absolute, or `[.]` relative to the tag's folder, GF-46). Answers
    `kind` (the value source at the end of the chain, `missing` for a tag no document defines,
    `unknown` for a reference whose source no document defines), `end` (the full path of the last tag
    found) and `node` (its definition)."""
    prov, rel = split_path(path)
    seen: list[str] = []
    while True:
        node = nodes.get(rel)
        if node is None:
            return {"kind": "unknown" if seen else "missing", "end": f"[{prov}]{rel}", "node": None, "chain": seen}
        source = node.get("valueSource", "memory")
        if source != "reference" or rel in seen:
            return {"kind": source, "end": f"[{prov}]{rel}", "node": node, "chain": seen}
        seen.append(rel)
        target = node.get("sourceTagPath")
        if not isinstance(target, str):   # bound to a UDT parameter: not a path this tool can follow
            return {"kind": "unknown", "end": f"[{prov}]{rel}", "node": None, "chain": seen}
        if target.startswith("[.]"):
            parts = rel.split("/")[:-1]
            for seg in target[3:].split("/"):
                if seg == "..":
                    parts = parts[:-1]
                elif seg:
                    parts.append(seg)
            rel = "/".join(parts)
        else:   # an absolute path: the source may lie with another provider, as `Tags.source` follows it
            prov, rel = split_path(target)


def source_folders_of(folders: list[str] | None) -> list[str]:
    """The source folders a caller named (`--source-folder`), each as `[provider]folder`, sorted and
    once. Raises ValueError for one that is not written that way or names no folder: a provider's
    root would allow an import anywhere in the provider."""
    out = []
    for f in folders or []:
        m = re.fullmatch(r"\[([^\[\]]+)\]/?(.*?)/?", f or "")
        if not m or not m.group(2):
            raise ValueError(f"a source folder is written [provider]folder and names a folder: {f!r}")
        out.append(f"[{m.group(1)}]{m.group(2)}")
    return sorted(dict.fromkeys(out))


NOT_SETTABLE = {"expr": "an expression tag: its value is the plant's to compute",
                "unknown": "a reference tag whose source no tag document given to the plan defines",
                "missing": "no tag document given to the plan defines the tag",
                "derived": "a derived tag", "opc": "an OPC tag", "db": "a query tag"}


def folder_members(nodes: dict[str, dict], folder: str) -> dict[str, dict]:
    """The members a device folder carries in a tag document, by name relative to the folder."""
    _prov, rel = split_path(folder)
    return {k[len(rel) + 1:]: v for k, v in nodes.items() if k.startswith(rel + "/")}


def load_profile(path: Path | None = None) -> dict:
    return json.loads((path or ROOT / "library" / "profile.json").read_text(encoding="utf-8"))


def _generator():
    """The generator's own readers of a descriptor (`tools/hmi/screen.py`): the walk takes document
    order, device folders, the device index and the trend index from the code that built the project."""
    from hmi import screen
    return screen


def find_text(kind: str, params: dict, show_tags: bool = True) -> str | None:
    """The line by which a symbol is found on the glass (`glass.find_symbol`): the identifier it shows,
    or for an instrument field, which shows none, its label and unit. None when it shows neither. `show_tags`
    false is a diagram whose toolbar's ID-tag button starts off: an automation symbol's, a tank's and a readout's
    identifier and a field's label are hidden then (`screen.ID_TAG_BLOCKS`), and a field's unit alone finds nothing."""
    tag = str(params.get("tag") or "")
    if kind == "instrument-field":
        label = str(params.get("label") or "")
        unit = str(params.get("unit") or "")
        if not (params.get("hasTag", True) and show_tags):
            return None
        return (label + (" " + unit if unit else "")).strip() or None
    if kind in ("controller", "sequence"):
        return tag if params.get("hasTag", True) and tag else (str(params.get("label") or "") or None)
    if kind == "tank":
        return tag if tag and params.get("hasTag", True) and show_tags else None
    if kind in AUTOMATION:
        return tag if tag and params.get("hasTag") and show_tags and params.get("readoutPosition") != "none" else None
    if kind == "readout":
        return tag if tag and params.get("hasTag") and show_tags else None
    return None


def reading_rule(kind: str, params: dict, param: str, render: str, running: bool = False,
                 height: float | None = None) -> tuple[dict | None, str]:
    """How the glass shows one parameter of a symbol, or why the walk cannot read it. A rule is
    `line` (prefix, number pattern, suffix: one of the symbol's text lines), `state` (the line for
    true and for false), `icon` (the 16 px icon for true and for false), `frame` (the alert frame
    drawn or not) or `module` (the bound property of a module component's element). `running` is for
    an effect, which states what a running device shows: its status row then reads the speed. `height` is the
    height of the symbol's box, where the plan knows it (`screen.module_draws`)."""
    if kind in MODULE_PROP and _generator().module_draws(kind, params, target=render, height=height):
        # the generator's own rule: under the module rendering the library's view still draws a symbol the
        # module's component cannot show (`screen.MODULE_NEEDS`, `MODULE_EXCEPT`), and such a symbol is read as
        # under the stock rendering
        prop = MODULE_PROP[kind].get(param)
        if prop == "setpoint" and not params.get("hasSetpoint"):
            return None, "the field draws no setpoint (`hasSetpoint` is false)"
        if prop == "speed" and not params.get("hasSpeed"):
            return None, "the symbol states no speed, so the module's component prints none"
        if prop:
            return {"how": "module", "prop": prop}, ""
        return None, "a component of the Cadre OpenBridge module draws it inside its own shadow DOM"
    if kind == "generator" and params.get("picture") == "genset":
        if param == "on":
            return {"how": "state", "on": {"line": GENSET_STATE[0]}, "off": {"line": GENSET_STATE[1]}}, ""
        if param == "alert":
            return {"how": "frame"}, ""
        return None, "the generator set draws only its state and its alarm frame"
    if kind in AUTOMATION:
        state = STATE_PARAM.get(kind, "on")
        shown = params.get("showStatus", True) and params.get("readoutPosition", "bottom") != "none"
        if param == state:
            if not shown or params.get("statusText"):
                return None, "the symbol's status row is hidden or carries a fixed text"
            if kind == "analogvalve":
                return None, "an analogue valve's status row shows its opening, not its state"
            if kind in SPEED_KINDS and params.get("hasSpeed"):
                return {"how": "state", "on": {"pattern": r"^-?[\d,]+ %$"}, "off": {"line": SYMBOL_STATE[1]}}, ""
            return {"how": "state", "on": {"line": SYMBOL_STATE[0]}, "off": {"line": SYMBOL_STATE[1]}}, ""
        if param == "value" and kind == "analogvalve" and shown and not params.get("statusText"):
            return {"how": "line", "format": ["", "0", " %"]}, ""
        if param == "alert":
            return {"how": "frame"}, ""
        if param == "speed":
            if running and shown and kind in SPEED_KINDS and params.get("hasSpeed") and not params.get("statusText"):
                return {"how": "line", "format": ["", "0", " %"]}, ""
            return None, "the symbol shows the speed only while the device is on"
        return None, "the symbol draws it as an icon, or not at all"
    unit = str(params.get("unit") or "")
    if kind == "readout" and param == "value":
        return {"how": "line", "format": ["", params.get("format", "#,##0.0"), " " + unit if unit else ""]}, ""
    if kind == "instrument-field":
        if param == "value":
            return {"how": "line", "format": ["", params.get("format", "#,##0"), ""]}, ""
        if param == "setpoint":
            if not params.get("hasSetpoint"):
                return None, "the field draws no setpoint (`hasSetpoint` is false)"
            return {"how": "line", "format": [SETPOINT_MARK, params.get("setpointFormat", "#,##0"), ""]}, ""
    if kind == "controller":
        fmt = params.get("format", "#,##0.0")
        if param == "value":
            return {"how": "line", "format": ["", fmt, ""]}, ""
        if param == "setpoint":
            if not params.get("hasSetpoint"):
                return None, "the block draws no setpoint (`hasSetpoint` is false)"
            return {"how": "line", "format": [SETPOINT_MARK, fmt, ""]}, ""
        if param == "output":
            if not params.get("hasOutput"):
                return None, "the block draws no output (`hasOutput` is false)"
            return {"how": "line", "format": list(OUTPUT_TEXT)}, ""
        if param == "manual":
            return {"how": "icon", "on": "manual", "off": "auto"}, ""
    if kind == "sequence":
        if param == "text":
            return {"how": "text"}, ""
        if param == "step":
            if not params.get("hasStep"):
                return None, "the block draws no step number (`hasStep` is false)"
            return {"how": "line", "format": [BLOCK_STEP, "0", ""]}, ""
    if kind == "tank" and param == "value":
        if params.get("compact") or params.get("static"):
            return None, "a compact or a static tank draws no value"
        return {"how": "line", "format": ["", "0", ""]}, ""
    return None, "no rule of the walk reads this parameter on the glass"


def expect_of(rule: dict, value, data_type: str | None = None) -> dict:
    """What a rule expects of the glass for a value: `line`, `pattern`, `icon`, `frame` or `module`.
    Raises ValueError where the number format is not implemented (`number_format`). `data_type` is
    the tag's, where the caller knows it: a Float4 is formatted from its 32 bit value."""
    how = rule["how"]
    if how == "line":
        prefix, pattern, suffix = rule["format"]
        return {"line": (prefix + number_format(value, pattern, data_type) + suffix).strip()}
    if how == "text":
        return {"line": str(value).strip()}
    if how == "state":
        return dict(rule["on"] if value else rule["off"])
    if how == "icon":
        return {"icon": rule["on"] if value else rule["off"]}
    if how == "frame":
        return {"frame": bool(value)}
    return {"module": rule["prop"], "value": value}


# ---------------------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------------------
def _symbols(descs: list[dict], contracts: dict, render: str) -> list[dict]:
    """Every symbol of the descriptors in document order, with what the plan needs of it."""
    gen = _generator()
    out = []
    for desc in descs:
        root = desc.get("tagRoot", "")
        route = desc.get("screen", {}).get("route", "")
        show_tags = gen.tags_shown_at_start(desc)        # the generator's own rule, its defaults included
        for s in gen.descriptor_items(desc):
            kind = s["kind"].lower()
            defaults = contracts.get(gen.KIND_VIEW.get(kind, ""), {}).get("params", {})
            params = {**defaults, **s.get("params", {})}
            if kind == "tank" and params.get("static") and "max" not in s.get("params", {}) \
                    and "max" not in s.get("bind", {}) and "hasCapacity" not in s.get("params", {}):
                params["hasCapacity"] = False     # as `screen.embed_symbol` settles it: no capacity nobody states
            folder = gen.device_folder(s)
            view = contracts.get(gen.KIND_VIEW.get(kind, ""))
            height = None     # the box the generator draws a readout or a field in (`screen.embed_symbol`)
            if view and kind in gen.MODULE_INSTRUMENTS:
                height = gen.symbol_box(s, view)[3] if all(k in s for k in "xywh") else None   # a card lays its own
            out.append({"id": s["id"], "kind": kind, "route": route, "params": params, "label": s.get("label", ""),
                        "height": height,
                        "find": find_text(kind, params, show_tags),
                        "bind": {k: gen.tag_path(root, m) for k, m in s.get("bind", {}).items()},
                        "folder": (s.get("params", {}).get("deviceId") or gen.tag_path(root, folder)) if folder else None,
                        "folderId": folder,
                        "deviceKind": gen.device_kind(s) if folder else None, "render": render})
    return out


def _style_of(spec: dict, want: str) -> str:
    """The style of the faceplate a device opens: `asm` only where its kind has an `asm` faceplate
    (`faceplates` of the profile's kind), since any other kind keeps its `openbridge` one."""
    plates = spec.get("faceplates", {})
    return "asm" if want == "asm" and plates.get("asm", spec["faceplate"]) != spec["faceplate"] else "openbridge"


def _devices(symbols: list[dict], model: dict | None, nodes: dict[str, dict], profile: dict,
             style: str = "openbridge") -> list[dict]:
    """The devices the pages draw, in document order (the first symbol of each folder): identifier,
    description, kind, faceplate, the members the device carries with what the plan knows of each, and
    the symbol that opens it. With a device model the members and their access are the model's; without
    one they are the tags the tag document carries in the device's folder."""
    gen = _generator()
    known = gen.model_devices(model)
    out: dict[str, dict] = {}
    for s in symbols:
        folder = s["folder"]
        if not folder:
            continue
        if folder in out:
            if out[folder]["find"] is None and s["find"]:   # a later symbol that can be found opens it
                out[folder].update({"find": s["find"], "symbol": s["id"], "route": s["route"]})
            continue
        m = known.get(folder)
        kind = str((m or {}).get("kind") or s["deviceKind"]).lower()
        kind = KIND_ALIAS.get(kind, kind)
        spec = profile.get("deviceKinds", {}).get(kind)
        if not spec or not spec.get("faceplate"):
            continue
        if m is not None:
            members = {name: {"access": v.get("access", "read")} for name, v in m["members"].items()}
        else:
            members = {name: {"access": None} for name in folder_members(nodes, folder)}
        for name, info in members.items():
            info["tag"] = f"{folder}/{name}"
            info["source"] = resolve(info["tag"], nodes)["kind"]
        out[folder] = {"id": (m or {}).get("id") or s["folderId"], "folder": folder, "kind": kind, "faceplate": spec["faceplate"],
                       "title": (m or {}).get("title") or s["params"].get("tag") or folder.split("/")[-1],
                       "label": (m or {}).get("label") or s["label"],
                       "route": s["route"], "symbol": s["id"], "find": s["find"], "members": members,
                       "model": m, "style": _style_of(spec, (m or {}).get("faceplate") or style)}
    return list(out.values())


def _usable(dev: dict, member: str) -> bool:
    """A device can use a write path through `member`: it carries the member, a device model marks it
    `write`, and the tag is not an expression tag, which refuses a write (GF-49)."""
    info = dev["members"].get(member)
    if info is None or info["access"] == "read":
        return False
    return info["source"] not in ("expr", "derived")


def _expected_tabs(dev: dict, trend_members: list[str]) -> list[str] | None:
    """The tabs the device's members call for (`framework.expected_tabs`, the expectation of gate G11);
    None for a device whose members no document states."""
    if not dev["members"]:
        return None
    from hmi import framework
    return framework.expected_tabs(dev["kind"], list(dev["members"]), trend_members, dev.get("style", "openbridge"))


def _config_of(dev: dict, member: str) -> dict | None:
    """The configuration the device model states for a member (`config`: caption, unit, bounds, format), else None."""
    return (((dev.get("model") or {}).get("members") or {}).get(member) or {}).get("config")


def _line_decimals(readings: list[dict]) -> list[int]:
    """The fraction digits of each reading that writes the value typed as a formatted line."""
    return [decimals_of(r["rule"]["format"][1]) for r in readings if r.get("rule", {}).get("how") == "line"]


def _step_delta(configured, fmt: str, bounds: tuple, coarsest: int | None = None) -> float:
    """How far a setpoint step moves a value: a tenth of the member's range where it has one, else a
    tenth of the configured value, and never less than one unit of the field's last digit, nor than
    one unit of the coarsest format among the symbols that show the member (`coarsest`, its fraction
    digits): a step finer than a symbol's format leaves the symbol's text as it was, and the symbol
    could not tell whether the write was made."""
    unit = 10.0 ** -min(decimals_of(fmt), decimals_of(fmt) if coarsest is None else coarsest)
    lo, hi = bounds
    if lo is not None and hi is not None:
        return round(max((hi - lo) / 10.0, unit), decimals_of(fmt))
    base = abs(float(configured)) / 10.0 if isinstance(configured, (int, float)) and not isinstance(configured, bool) else 0.0
    return round(max(base, unit), decimals_of(fmt))


def _symbol_readings(symbols: list[dict], route: str, tag: str, running: bool = False) -> list[dict]:
    """The symbols of a page that bind a parameter to exactly `tag`, each with the rule that reads it."""
    out = []
    for s in symbols:
        if s["route"] != route or not s["find"]:
            continue
        for param, path in s["bind"].items():
            if path != tag:
                continue
            rule, _why = reading_rule(s["kind"], s["params"], param, s["render"], running, s.get("height"))
            if rule:
                out.append({"symbol": s["id"], "find": s["find"], "param": param, "rule": rule})
    return out


def _effects_for(effects: dict | None, symbols: list[dict], dev: dict, path: str, route: str, value=None,
                 member: str | None = None) -> tuple[list[dict], list[str]]:
    """The effects an effects file states for one action (a device, a write path, and for a command the
    value written), each resolved to the symbols of the step's page that show the member; and the
    members no symbol of that page shows."""
    out, unseen = [], []
    root = (effects or {}).get("tagRoot", "")
    for e in (effects or {}).get("effects", []):
        if e.get("device") != dev["id"] or e.get("path") != path:
            continue
        if "value" in e and e["value"] != value:
            continue
        if "member" in e and e["member"] != member:
            continue
        for x in e.get("expect", []):
            tag = x["member"] if x["member"].startswith("[") else f"{root}/{x['member']}"
            if x.get("changes"):   # read on the tag itself: it holds another value than before the action
                out.append({"member": x["member"], "tag": tag, "changes": True, "within": e.get("within", WAIT_FLOOR)})
                continue
            readings = _symbol_readings(symbols, route, tag, running=True)
            if not readings:
                unseen.append(x["member"])
            for r in readings:
                want = {k: x[k] for k in ("value", "min", "max", "written", "leaves", "returnsWithin") if k in x}
                if x.get("leaves") and r["rule"]["how"] == "text":
                    # a text has no shape of its own to be found by: its line is the one that is neither a
                    # line the symbol draws from its parameters nor the line of another bound parameter
                    sym = next(s for s in symbols if s["id"] == r["symbol"] and s["route"] == route)
                    want.update(_other_lines(sym, r["param"]))
                out.append({**r, "member": x["member"], "within": e.get("within", WAIT_FLOOR), **want})
    return out, unseen


def _restores_for(effects: dict | None, dev: dict, path: str, member: str) -> list[str]:
    """The tags an effects file says a pulse leaves changed (`restores`: the plant's own flags that a command
    moves and nothing returns, such as a sequence's in service flag), as full tag paths; the runner imports
    each back from its definition of before once the step is done."""
    root = (effects or {}).get("tagRoot", "")
    out: list[str] = []
    for e in (effects or {}).get("effects", []):
        if e.get("device") != dev["id"] or e.get("path") != path or e.get("member", member) != member:
            continue
        for m in e.get("restores", []):
            tag = m if m.startswith("[") else f"{root}/{m}"
            if tag not in out:
                out.append(tag)
    return out


def _other_lines(sym: dict, param: str) -> dict:
    """For a text a symbol writes as it is: `fixed`, the lines the symbol draws from its parameters
    (its identifier, its label, its unit), and `others`, the formats of the lines its other bound
    parameters write. What is left of the symbol's lines is the text's own line."""
    p = sym["params"]
    label, unit = str(p.get("label") or ""), str(p.get("unit") or "")
    fixed = {str(sym["find"] or ""), str(p.get("tag") or ""), label, unit, (label + " " + unit).strip()} - {""}
    others = []
    for q in sym["bind"]:
        rule, _why = reading_rule(sym["kind"], p, q, sym["render"], True, sym.get("height")) if q != param else (None, "")
        if rule and rule["how"] == "line":
            others.append(rule["format"])
    return {"fixed": sorted(fixed), "others": others}


def scene_values(tags: list[dict]) -> None:
    """Two scenes of values for the tags of the parity group, written into each entry as `values`.
    A number takes one value in the lower half of its range and one in the upper half, so the two
    differ; every number of the plan is distinct, so a symbol bound to the wrong tag reads a value
    that is not its own; no value ends in 0 or 5 at its third decimal, so none sits on a rounding tie.
    The range is the one the tag states (`engLow`, `engHigh`), or without one a tenth either side of
    the configured value. A Boolean takes the opposite of its configured value, then that value."""
    used: set[float] = set()
    for i, t in enumerate(tags):
        node = t["node"]
        dtype = str(node.get("dataType", "Float8"))
        v0 = node.get("value")
        if dtype == "Boolean":
            t["values"] = [not bool(v0), bool(v0)]
            t["range"] = None
            continue
        v0 = float(v0) if isinstance(v0, (int, float)) and not isinstance(v0, bool) else 0.0
        if isinstance(node.get("engLow"), (int, float)) and isinstance(node.get("engHigh"), (int, float)) \
                and node["engHigh"] > node["engLow"]:
            lo, hi, stated = float(node["engLow"]), float(node["engHigh"]), "engLow and engHigh"
        else:
            span = max(abs(v0) / 10.0, 1.0)
            lo, hi, stated = v0 - span, v0 + span, "a tenth either side of the configured value"
        frac = ((i + 1) * 0.6180339887) % 1.0
        values = []
        for base in (0.05, 0.55):
            v = lo + (hi - lo) * (base + 0.4 * frac)
            if dtype.startswith("Int"):
                v = float(int(round(v)))
                while v in used or (values and v == values[0]):
                    v += 1.0
            else:
                v = round(v, 3)
                while v in used or int(round(v * 1000)) % 5 == 0:
                    v = round(v + 0.001, 3)
            used.add(v)
            values.append(int(v) if dtype.startswith("Int") else v)
        t["values"] = values
        t["range"] = {"low": lo, "high": hi, "from": stated}


# ---------------------------------------------------------------------------------------
# The trip (`--trip`, COB-204): which source tag drives a condition's `ok`, and the value that trips it
# ---------------------------------------------------------------------------------------
# The Boolean expressions a condition's `ok` is read in: references, true and false, `!`, `&&`, `||`,
# parentheses and `coalesce`. Anything else is not read: the walk cannot tell what would trip it.
_OK_TOKEN = re.compile(r"\s*(\{[^{}]+\}|&&|\|\||!(?!=)|\(|\)|,|true\b|false\b|coalesce\b)", re.IGNORECASE)


def ok_expression(text: str):
    """(the one tag the expression references, a function of that tag's Boolean value), or a reason
    (a str) where the expression is not of the subset above or references no tag or more than one.
    Pure: it parses, it never evaluates the text as code."""
    tokens, at = [], 0
    while at < len(text):
        if not text[at:].strip():
            break
        m = _OK_TOKEN.match(text, at)
        if not m:
            return f"its expression holds {text[at:at + 24].strip()!r}, which the walk does not read"
        tokens.append(m.group(1).lower() if m.group(1)[0] != "{" else m.group(1))
        at = m.end()
    refs = sorted({t[1:-1].strip() for t in tokens if t[0] == "{"})
    if len(refs) != 1:
        return f"its expression references {len(refs)} tags, and a trip the walk raises sets one"
    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def take(want=None):
        t = peek()
        if t is None or (want is not None and t != want):
            raise ValueError(f"expected {want or 'more'}")
        pos[0] += 1
        return t

    def either():
        left = both()
        while peek() == "||":
            take()
            right = both()
            left = (lambda a, b: lambda x: bool(a(x)) or bool(b(x)))(left, right)
        return left

    def both():
        left = unary()
        while peek() == "&&":
            take()
            right = unary()
            left = (lambda a, b: lambda x: bool(a(x)) and bool(b(x)))(left, right)
        return left

    def unary():
        if peek() == "!":
            take()
            inner = unary()
            return lambda x: (None if inner(x) is None else not inner(x))
        return primary()

    def primary():
        t = take()
        if t == "(":
            inner = either()
            take(")")
            return inner
        if t in ("true", "false"):
            return lambda _x, v=(t == "true"): v
        if t[0] == "{":
            return lambda x: x
        if t == "coalesce":
            take("(")
            parts = [either()]
            while peek() == ",":
                take()
                parts.append(either())
            take(")")
            return lambda x: next((v for v in (p(x) for p in parts) if v is not None), None)
        raise ValueError(f"unexpected {t!r}")
    try:
        f = either()
        if peek() is not None:
            raise ValueError("trailing text")
    except ValueError as e:
        return f"its expression is not one the walk reads ({e})"
    return refs[0], f


def trip_source(ok_path: str, ok_node: dict | None) -> tuple[str, bool] | str:
    """(the tag that drives a condition's `ok`, the Boolean value of that tag at which `ok` is false), or
    the reason there is none. A memory `ok` is its own source and trips at false; an expression `ok`
    names one tag (absolute, or `[.]` relative to the condition's folder) whose two values give `ok`
    false at one and true at the other."""
    if not ok_node:
        return "no tag document defines the condition's ok"
    source = ok_node.get("valueSource", "memory")
    if source == "memory":
        return ok_path, False
    if source != "expr" or not isinstance(ok_node.get("expression"), str):
        return f"its ok is {NOT_SETTABLE.get(source, 'a ' + str(source) + ' tag')}"
    read = ok_expression(ok_node["expression"])
    if isinstance(read, str):
        return read
    ref, f = read
    if ref.startswith("[.]"):
        prov, rel = split_path(ok_path)
        parts = rel.split("/")[:-1]
        for seg in ref[3:].split("/"):
            if seg == "..":
                parts = parts[:-1]
            elif seg:
                parts.append(seg)
        ref = f"[{prov}]" + "/".join(parts)
    elif not ref.startswith("["):
        return f"its expression references {ref!r}, which names no provider"
    at_true, at_false = f(True), f(False)
    if at_true is False and at_false is True:
        return ref, True
    if at_true is True and at_false is False:
        return ref, False
    return "its expression does not turn on its one tag"


def build_plan(descs: list[dict], devices: dict | None = None, tags: dict | None = None,
               effects: dict | None = None, source_tags: list[tuple[dict, str]] | None = None,
               render: str = "stock", profile: dict | None = None, names: dict | None = None,
               source_folders: list[str] | None = None, faceplate: str = "openbridge",
               trip: bool = False) -> dict:
    """The plan of the walk, from the descriptors, the device model, the tag model, the effects file
    and the library profile. Pure: no clock, no gateway, and the same inputs give the same plan.

    `source_folders` names the folders outside the descriptors' `tagRoot` that the walk may import
    into (`[provider]folder` each): a device layer of reference tags stands on a source layer in
    another folder, and the walk sets a source tag there only when the caller names the folder. The
    plan records them as `sourceFolders`, and the runner allows exactly the tag root and these
    (`walk_run.allowed_folders`). They are never inferred from the source tag documents: a document
    says where a value lives, not that this walk may write there.

    `faceplate` is the project's default faceplate style (`screen.py --faceplate`); a device model may
    give a device its own. A step of a device in the `asm` style names the tab that style shows (ASM_TAB).

    `trip` (`walk.py plan --trip`, COB-204) adds, for each device kind with interlocks, a step of write
    path W11 on the first device whose latched trip the walk can raise from a memory source tag
    (`trip_source`): the trip is raised by an import of the source, read on the condition's row and the
    head, the source put back, the latch read, and cleared by the Interlocks tab's Reset. A kind none of
    whose devices qualifies is listed in `notReached` with each device's reason. No refusal (group R)
    mirrors it: Reset shows only while a trip is latched."""
    gen = _generator()
    profile = profile or load_profile()
    contracts = gen.load_contracts()
    generated = False
    if tags is None:   # a build that generates its tags: the document the generator would import
        tags = gen.tags_document(descs, devices)
        generated = tags is not None
    nodes = tag_nodes(tags)
    for doc, parent in source_tags or []:
        for k, v in tag_nodes(doc, parent).items():
            nodes.setdefault(k, v)
    symbols = _symbols(descs, contracts, render)
    devs = _devices(symbols, devices, nodes, profile, faceplate)
    provider, top = split_path(descs[0].get("tagRoot", "")) if descs else ("default", "")
    trends = gen.trend_index(descs, tags, devices)
    trended: dict[str, list[str]] = {}
    for t in trends:
        trended.setdefault(t["deviceId"], []).append(t["member"])
    steps: list[dict] = []
    not_reached: list[dict] = []
    count = {g: 0 for g in GROUPS}
    tag_root = descs[0].get("tagRoot", "") if descs else ""

    folders = source_folders_of(source_folders)
    allowed = ([(provider, top)] if top else []) + [split_path(f) for f in folders]

    def inside(path: str) -> bool:
        """A tag lies below the plan's `tagRoot` or below a source folder the caller named: the only
        folders the runner imports into (`Tags.check`)."""
        prov, rel = split_path(path)
        return any(prov == p and (rel == r or rel.startswith(r + "/")) for p, r in allowed)
    outside = (f"outside the plan's tag folder {tag_root}"
               + (f" and the source folders named ({', '.join(folders)})" if folders else "")
               + ": the walk imports only below " + ("them" if folders else "it")
               + ", so it could neither set the tag nor put it back"
               + ("" if folders else " (`--source-folder` names a folder it may import into)"))

    def add(group: str, step: dict, sid: str | None = None) -> dict:
        count[group] += 1
        step = {"id": sid or f"{group}-{count[group]:02d}", "group": group, **step}
        steps.append(step)
        return step

    # N: every route by the navigation menu, and a card's title where a cards page links one. A step
    # proves the page, not the address alone: the top bar reads the page's name (the menu's label of
    # the route, else the route: `cadre.hmi.page_title`), a symbol the descriptor places on the page is
    # found on it, and a menu step starts from another route, so that it cannot pass without moving.
    menu = [(scr["route"], scr.get("navLabel", scr.get("title", scr["route"])))
            for scr in (d["screen"] for d in descs) if scr.get("nav", True)]
    menu += ([("/trends", "Trends")] if trends else []) + [("/alerts", "Alerts")]
    shown = dict(menu)
    placed = {}
    for sym in symbols:
        if sym["find"]:
            placed.setdefault(sym["route"], sym["find"])

    def holds(route: str) -> dict | None:
        """What a page of the frame must hold outside the docks (`PAGE_HOLDS`): the pages that carry
        no symbol of a descriptor, where the title and the address are one fact."""
        if route not in PAGE_HOLDS:
            return None
        _view, component, what = PAGE_HOLDS[route]
        return {"component": component, "what": what}
    for i, (route, label) in enumerate(menu):
        add("N", {"type": "route", "session": "any", "via": "menu", "route": route, "label": label,
                  "from": menu[(i + 1) % len(menu)][0] if len(menu) > 1 else None,
                  "title": shown[route], "symbol": placed.get(route), "holds": holds(route)})
    for desc in descs:
        for row in desc.get("rows", []):
            for card in row:
                if card.get("route") and card.get("title"):
                    add("N", {"type": "route", "session": "any", "via": "card", "from": desc["screen"]["route"],
                              "route": card["route"], "label": card["title"],
                              "title": shown.get(card["route"], card["route"]), "symbol": placed.get(card["route"]),
                              "holds": holds(card["route"])})

    # D: the first device of each kind opens its faceplate from its symbol
    first: dict[str, dict] = {}
    for d in devs:
        if d["find"] is None:
            known = all(s["kind"] in FINDABLE for s in symbols if s["folder"] == d["folder"])
            not_reached.append({"device": d["title"], "why": "no symbol of the device shows a text by which the "
                                "walk can find it on the glass (its identifier is hidden)" if known else
                                "the walk's table does not say how a symbol of its kind shows its identifier"})
            continue
        first.setdefault(d["kind"], d)
    openable = [d for d in devs if d["find"] is not None]
    for kind, d in first.items():
        add("D", {"type": "open", "session": "any", "device": d["title"], "kind": kind, "route": d["route"],
                  "find": d["find"], "expect": {"title": d["title"], "label": d["label"],
                                                "tabs": _expected_tabs(d, trended.get(d["folder"], []))}})

    # T: the trend page, and the Trend tab of one trended device of each kind whose faceplate has one. A
    # kind without a Trend tab (an indicator) shows its history on the trend page alone, which the first
    # step reads card by card; the plan lists such kinds (`trendTabAbsent`).
    no_trend_tab: dict[str, list[str]] = {}
    if trends:
        add("T", {"type": "trend-page", "session": "any", "route": "/trends",
                  "cards": [{"title": t["title"], "member": t["member"]} for t in trends]})
        seen_kinds = set()
        for d in openable:
            members = trended.get(d["folder"])
            tabs = _expected_tabs(d, list(members or []))
            if members and tabs is not None and "Trend" not in tabs:
                no_trend_tab.setdefault(d["kind"], []).append(d["title"])
                continue
            if members and d["kind"] not in seen_kinds:
                seen_kinds.add(d["kind"])
                add("T", {"type": "trend-tab", "session": "any", "device": d["title"], "kind": d["kind"],
                          "route": d["route"], "find": d["find"], "series": list(members)})

    # C: the write paths each kind's devices can use, and R: the refusal of each
    choose = {(c["kind"], c["path"]): c["device"] for c in (effects or {}).get("choose", [])}
    unseen_effects: list[dict] = []

    def pick(kind: str, path: str, usable) -> dict | None:
        cands = [d for d in openable if d["kind"] == kind and usable(d)]
        want = choose.get((kind, path))
        return next((d for d in cands if d["id"] == want), cands[0] if cands else None)

    def base(d: dict, path: str, tab: str) -> dict:
        return {"session": "signed", "path": path, "device": d["title"], "kind": d["kind"], "route": d["route"],
                "find": d["find"], "tab": tab}

    def states_step(d: dict, path: str, tab: str, member: str, states: list[dict], row: str | None) -> None:
        for s in states:
            tag = next(iter(s["tags"]))
            s["symbols"] = _symbol_readings(symbols, d["route"], tag) if len(s["tags"]) == 1 else []
            s["effects"], unseen = _effects_for(effects, symbols, d, path, d["route"], s["value"])
            unseen_effects.extend({"device": d["title"], "path": path, "member": m} for m in unseen)
        c = add("C", {**base(d, path, tab), "type": "states", "member": member, "row": row, "states": states})
        add("R", {"type": "refusal", "session": "anonymous", "mirrors": c["id"], "path": path, "device": d["title"],
                  "kind": d["kind"], "route": d["route"], "find": d["find"], "tab": tab, "row": row,
                  "controls": [{"button": s["button"], "sibling": s.get("sibling")} for s in states],
                  "any": path == "W10", "states": [{"value": s["value"], "button": s["button"],
                                                    "sibling": s.get("sibling"), "tags": s["tags"],
                                                    "text": s.get("text"), "symbols": s["symbols"]} for s in states]},
            sid="R-" + c["id"][2:])

    def entry_step(d: dict, path: str, tab: str, member: str, caption: str, fmt: str, prefer: str,
                   requires: dict | None = None, lamp: bool = False, bounds: tuple | None = None) -> None:
        tag = d["members"][member]["tag"]
        node = resolve(tag, nodes)["node"] or {}
        bounds = BOUNDS.get(member, (None, None)) if bounds is None else bounds
        syms = _symbol_readings(symbols, d["route"], tag)
        eff, unseen = _effects_for(effects, symbols, d, path, d["route"], member=member)
        unseen_effects.extend({"device": d["title"], "path": path, "member": m} for m in unseen)
        # the step is at least one unit of the coarsest format that shows the value typed: the symbols of
        # the member, and the effects that read the value written
        shows = _line_decimals(syms + [e for e in eff if e.get("written")])
        c = add("C", {**base(d, path, tab), "type": "entry", "member": member, "tag": tag, "field": caption,
                      "format": fmt, "dataType": node.get("dataType"),
                      "delta": _step_delta(node.get("value"), fmt, bounds, min(shows) if shows else None),
                      "prefer": prefer,
                      "bounds": list(bounds), "requires": requires, "lamp": lamp, "symbols": syms,
                      "effects": eff})
        # A field that a condition enables (the manual output, in manual) is refused for the role only
        # while the condition holds: its refusal runs inside the step that holds it, as W5's does.
        held = {"during": c["id"], "requires": {k: requires[k] for k in ("tag", "value", "row", "set")}} if requires else {}
        add("R", {"type": "refusal", "session": "anonymous", "mirrors": c["id"], **held, "path": path,
                  "device": d["title"], "kind": d["kind"], "route": d["route"], "find": d["find"], "tab": tab,
                  "field": caption, "tag": tag, "format": fmt, "dataType": node.get("dataType"),
                  "delta": c["delta"], "prefer": prefer, "bounds": list(bounds), "symbols": syms},
            sid="R-" + c["id"][2:])

    def tag_of(d: dict, member: str) -> str:
        return d["members"][member]["tag"]

    def trip_of(x: dict) -> dict | str | None:
        """The first trip of a device the walk can raise, as the step's fields; else why none can be
        (None for a device with no trip). The source must be a memory Boolean inside the plan's folders,
        not at its trip value as configured, and carry no alarm (the trip would leave an alarm event)."""
        conds = sorted({k.split("/")[1] for k in folder_members(nodes, x["folder"])
                        if re.fullmatch(r"ilk/C\d{2}/kind", k)})
        trips = [c for c in conds
                 if (resolve(f"{x['folder']}/ilk/{c}/kind", nodes)["node"] or {}).get("value") == "trip"]
        if not trips:
            return None
        if not _usable(x, "ilk/resetAt"):
            return ("the Interlocks tab's Reset writes ilk/resetAt, which "
                    + ("the device model does not mark write" if x["model"] is not None
                       else "no tag document gives as a memory tag"))
        reset_node = resolve(f"{x['folder']}/ilk/resetAt", nodes)["node"] or {}
        if reset_node.get("dataType") not in RESET_TYPES:   # the walk writes an integer of milliseconds into it
            return (f"ilk/resetAt is a {reset_node.get('dataType') or 'tag of no stated type'}, which does not take "
                    f"an integer of milliseconds (it must be one of {', '.join(sorted(RESET_TYPES))})")
        reasons = []
        for c in trips:
            here = f"{x['folder']}/ilk/{c}"
            text = (resolve(here + "/text", nodes)["node"] or {}).get("value")
            if not isinstance(text, str) or not text.strip():
                reasons.append(f"{c} has no text, by which its row is found")
                continue
            if (resolve(here + "/latched", nodes)["node"] or {}).get("value") is not True:
                reasons.append(f"{c} does not latch")
                continue
            src = trip_source(f"[{split_path(x['folder'])[0]}]{split_path(here)[1]}/ok",
                              resolve(here + "/ok", nodes)["node"])
            if isinstance(src, str):
                reasons.append(f"{c}: {src}")
                continue
            path, value = src
            r = resolve(path, nodes)
            node = r["node"] or {}
            if r["kind"] != "memory":
                reasons.append(f"{c}: its source {r['end']} is {NOT_SETTABLE.get(r['kind'], r['kind'])}")
            elif node.get("dataType") != "Boolean":
                reasons.append(f"{c}: its source {r['end']} is a {node.get('dataType')} tag")
            elif not inside(r["end"]):
                reasons.append(f"{c}: its source {r['end']} lies {outside}")
            elif node.get("alarms"):
                reasons.append(f"{c}: its source {r['end']} carries an alarm, which the trip would leave as an event")
            elif node.get("value") is value:
                reasons.append(f"{c}: its source {r['end']} rests at the value that trips it")
            else:
                return {"condition": c, "text": text, "source": r["end"], "trip": value}
        return "; ".join(reasons)

    kinds = list(dict.fromkeys(d["kind"] for d in openable))
    for kind in kinds:
        plate = profile["deviceKinds"][kind]["faceplate"]
        # W1 commands
        d = pick(kind, "W1", lambda x: _usable(x, "cmd")) if plate in COMMANDS else None
        if d:
            on, off = COMMANDS[plate]
            states_step(d, "W1", "Control", "cmd", [
                {"value": True, "button": on, "tags": {tag_of(d, "cmd"): True}},
                {"value": False, "button": off, "tags": {tag_of(d, "cmd"): False}}], None)
        # W2 control mode
        d = pick(kind, "W2", lambda x: _usable(x, "mode")) if plate in COMMANDS else None
        if d:
            states_step(d, "W2", "Control", "mode", [
                {"value": v, "button": c, "text": c, "tags": {tag_of(d, "mode"): v}} for c, v in MODES], MODE_ROW)
        # W3, W12, W14, W15 setpoints
        for member, (path, tab, caption, fmt) in SETPOINTS.items():
            if SETPOINT_VIEW[member] != plate:
                continue
            d = pick(kind, path, lambda x, m=member: _usable(x, m))
            if not d:
                continue
            requires = None
            if member == "manOut":   # the field is enabled, and the write accepted, only in manual
                if not _usable(d, "manual"):
                    not_reached.append({"path": path, "device": d["title"], "why": "the manual output is "
                                        "written only while the loop is in manual, and the device's `manual` "
                                        "is not one the walk may write"})
                    continue
                requires = {"tag": tag_of(d, "manual"), "value": True, "row": MODE_ROW,
                            "set": {"button": LOOP[1][0], "text": LOOP[1][0]},
                            "back": {"button": LOOP[0][0], "text": LOOP[0][0]}}
            entry_step(d, path, tab, member, caption, fmt, "down", requires)
        # W19 Config rows (F010): each configuration member of the `asm` devices of the kind, on the first device
        # that carries it; the row's caption, format and bounds are the device model's
        # A device with modes takes a configuration change in its maintenance mode only (`OWNER_PATHS`, wiki page 13
        # section 10.4): its rows are listed, not walked, since the walk enters no mode to write one.
        for x in openable:
            if x["kind"] == kind and x["style"] == "asm" and (x["model"] or {}).get("modes")                     and any(_config_of(x, m) is not None for m in x["members"]):
                not_reached.append({"path": CONFIG_PATH, "device": x["title"], "why": "the device has modes, and its "
                                    "Config rows are written only in its maintenance mode, which no step enters"})
        for member in dict.fromkeys(m for x in openable if x["kind"] == kind and x["style"] == "asm"
                                    and not (x["model"] or {}).get("modes")
                                    for m in x["members"] if _config_of(x, m) is not None):
            d = pick(kind, CONFIG_PATH, lambda x, m=member: x["style"] == "asm" and _usable(x, m)
                     and not (x["model"] or {}).get("modes") and _config_of(x, m) is not None)
            if d:
                cfg = _config_of(d, member)
                entry_step(d, CONFIG_PATH, CONFIG_TAB, member, cfg.get("caption") or member, cfg.get("format") or "0.0",
                           "down", bounds=(cfg.get("minimum"), cfg.get("maximum")))
        # W13 loop mode
        d = pick(kind, "W13", lambda x: _usable(x, "manual")) if plate == "Faceplate/Controller" else None
        if d:
            states_step(d, "W13", "Control", "manual", [
                {"value": v, "button": c, "text": c, "tags": {tag_of(d, "manual"): v}} for c, v in LOOP], MODE_ROW)
        # W4 limits: each limit member, on the first device of the kind that carries it. A step moves
        # the limit away from the value, so that it raises no alarm (group A crosses it on purpose).
        if plate in VALUE_MEMBER:
            for member, caption in LIMITS.items():
                d = pick(kind, "W4", lambda x, m=member: _usable(x, m) and VALUE_MEMBER[plate] in x["members"])
                if d:
                    entry_step(d, "W4", FIRST_TAB[plate], member, caption, LIMIT_FORMAT,
                               "up" if member.startswith("hi") else "down", lamp=True)
        # W5 fault reset: the button shows only while the device is faulted, so the step raises the
        # fault itself, by a tag import, where the fault is a memory tag
        d = None
        if plate in COMMANDS:
            cands = [x for x in openable if x["kind"] == kind and _usable(x, "fault")]
            memory = [x for x in cands if resolve(tag_of(x, "fault"), nodes)["kind"] == "memory"]
            settable = [x for x in memory if inside(resolve(tag_of(x, "fault"), nodes)["end"])]
            # a device that is not faulted as configured, so that the walk leaves no fault behind
            quiet = [x for x in settable if not resolve(tag_of(x, "fault"), nodes)["node"].get("value")]
            want = choose.get((kind, "W5"))
            d = next((x for x in settable if x["id"] == want), (quiet or settable or [None])[0])
            if cands and not d:
                not_reached.append({"path": "W5", "kind": kind, "why": "Reset fault shows only while the device "
                                    "is faulted, and " + (
                                        "the memory tag that would raise the fault "
                                        f"({resolve(tag_of(memory[0], 'fault'), nodes)['end']}) lies {outside}" if memory else
                                        "no tag document gives the walk a memory tag to raise the fault with")})
        if d:
            r = resolve(tag_of(d, "fault"), nodes)
            c = add("C", {**base(d, "W5", "Control"), "type": "fault-reset", "member": "fault",
                          "tag": tag_of(d, "fault"), "source": r["end"], "alarm": bool(r["node"].get("alarms")),
                          "button": FAULT["button"], "row": FAULT["row"], "set": FAULT["set"], "clear": FAULT["clear"],
                          "symbols": _symbol_readings(symbols, d["route"], tag_of(d, "fault"))})
            add("R", {"type": "refusal", "session": "anonymous", "mirrors": c["id"], "during": c["id"], "path": "W5",
                      "device": d["title"], "kind": kind, "route": d["route"], "find": d["find"], "tab": "Control",
                      "row": FAULT["row"], "controls": [{"button": FAULT["button"], "sibling": None}], "any": False,
                      "states": [{"value": False, "button": FAULT["button"], "sibling": None,
                                  "tags": {tag_of(d, "fault"): False}, "text": FAULT["clear"], "symbols": []}]},
                sid="R-" + c["id"][2:])
        # W10 bypass: the first condition a tag document marks bypassable
        if profile["deviceKinds"][kind].get("interlocks"):
            def bypassable(x):
                for m in sorted(x["members"]):
                    parts = m.split("/")
                    if len(parts) == 3 and parts[0] == "ilk" and parts[2] == "bypassed" and _usable(x, m):
                        node = resolve(f"{x['folder']}/ilk/{parts[1]}/bypassable", nodes)["node"]
                        if x["model"] is not None or (node and node.get("value") is True):
                            return m
                return None
            d = pick(kind, "W10", lambda x: bypassable(x) is not None)
            if d:
                m = bypassable(d)
                states_step(d, "W10", BYPASS["tab"], m, [
                    {"value": True, "button": BYPASS["set"], "tags": {tag_of(d, m): True},
                     "pane": {"contains": BYPASS["lamp"]}},
                    {"value": False, "button": BYPASS["clear"], "tags": {tag_of(d, m): False},
                     "pane": {"lacks": BYPASS["lamp"]}}], None)
        # W11 by a trip (`trip`, COB-204): the first device of the kind with a latched trip whose source the
        # walk can raise. The step raises the source, reads the row and the head, puts the source back,
        # reads the latch, and presses the Interlocks tab's Reset, so the device must let it write ilk/resetAt.
        if trip and profile["deviceKinds"][kind].get("interlocks"):
            found, why_not = None, []
            for x in (o for o in openable if o["kind"] == kind):
                hit = trip_of(x)
                if isinstance(hit, dict):
                    found = (x, hit)
                    break
                if hit:
                    why_not.append(f"{x['title']}: {hit}")
            if found:
                d, hit = found
                add("C", {**base(d, "W11", TRIP["tab"]), "type": "trip", "member": "ilk/resetAt",
                          "tag": tag_of(d, "ilk/resetAt"), **hit, "button": TRIP["reset"],
                          # the header that reads Interlocked is the asm style's; the openbridge style's
                          # Interlocks tab shows the row and the reset row alone
                          "head": TRIP["head"] if d["style"] == "asm" else None,
                          "cleared": TRIP["cleared"],
                          "lamps": {k: TRIP[k] for k in ("met", "tripped", "latched")}})
            elif why_not:
                not_reached.append({"path": "W11", "kind": kind,
                                    "why": "no trip the walk can raise: " + "; ".join(why_not[:4])})
        # W16 force and W17 mask, on the Maintenance tab
        if profile["deviceKinds"][kind].get("maintenance"):
            encodings = [tuple(e) for e in profile.get("forceEncodings", [])]
            mode_first = sorted(encodings, key=lambda e: "mnt/forceMode" not in e)

            def force_of(x):
                return next((e for e in mode_first if all(_usable(x, m) for m in e)), None)
            d = pick(kind, "W16", lambda x: force_of(x) is not None)
            if d:
                a, b = force_of(d)
                if a == "mnt/forceMode":
                    tags = {"auto": {tag_of(d, a): False}, "on": {tag_of(d, a): True, tag_of(d, b): True},
                            "off": {tag_of(d, a): True, tag_of(d, b): False}}
                else:
                    tags = {"auto": {tag_of(d, a): False, tag_of(d, b): False},
                            "on": {tag_of(d, a): True, tag_of(d, b): False},
                            "off": {tag_of(d, a): False, tag_of(d, b): True}}
                states_step(d, "W16", FORCE["tab"], "force", [
                    {"value": v, "button": button, "sibling": sib, "text": text, "tags": tags[v]}
                    for v, button, text, sib in FORCE["states"]], FORCE["row"])
            d = pick(kind, "W17", lambda x: _usable(x, "mnt/errorMask"))
            if d:
                states_step(d, "W17", MASK["tab"], "mnt/errorMask", [
                    {"value": v, "button": button, "sibling": sib, "text": text,
                     "tags": {tag_of(d, "mnt/errorMask"): v}} for v, button, text, sib in MASK["states"]], MASK["row"])

    # W18 pulse commands: the button of each pulse member the first device of the kind may write. A
    # pulse leaves nothing in its own tag where the plant returns it, so what proves it is what the
    # effects file names (a member that changes, a reading that leaves its resting text), or, without
    # one, the member itself read true before anything returned it.
    for kind in kinds:
        spec = profile["deviceKinds"][kind]
        if spec["faceplate"] not in PULSE_VIEWS:
            continue
        for member in spec.get("pulses", []):
            d = pick(kind, "W18", lambda x, m=member: _usable(x, m))
            if not d:
                continue
            tag = tag_of(d, member)
            # the button's caption: the device model's, else the library's for an asm faceplate (COB-158), else
            # the member's name
            asm_plate = d.get("style") == "asm" or spec["faceplate"].startswith("Faceplate/ASM/")
            caption = (((d["model"] or {}).get("members", {}).get(member, {}).get("caption"))
                       or (_generator().devices_asm.CAPTIONS.get(member, member) if asm_plate else member))
            eff, unseen = _effects_for(effects, symbols, d, "W18", d["route"], member=member)
            unseen_effects.extend({"device": d["title"], "path": "W18", "member": m} for m in unseen)
            rest = [r for s in symbols if s["folder"] == d["folder"] and s["route"] == d["route"] and s["find"]
                    for r in [{"symbol": s["id"], "find": s["find"]}]]
            tab = PULSE_TAB[member] if asm_plate and member in PULSE_TAB else FIRST_TAB[spec["faceplate"]]
            # `returns`: the effects file says that the plant returns the member to false by itself
            returns = any(e.get("returns") for e in (effects or {}).get("effects", [])
                          if e.get("device") == d["id"] and e.get("path") == "W18" and e.get("member", member) == member)
            c = add("C", {**base(d, "W18", tab), "type": "pulse", "member": member, "tag": tag, "button": caption,
                          "row": STEP_ROW[0] if "step" in d["members"] else None, "rest": rest, "effects": eff,
                          "returns": returns, "restores": _restores_for(effects, d, "W18", member)})
            add("R", {"type": "refusal", "session": "anonymous", "mirrors": c["id"], "path": "W18",
                      "device": d["title"], "kind": kind, "route": d["route"], "find": d["find"], "tab": tab,
                      "row": c["row"], "controls": [{"button": caption, "sibling": None}], "any": False,
                      "watch": sorted({e["tag"] for e in eff if e.get("changes")}), "rest": rest,
                      "states": [{"value": True, "button": caption, "sibling": None, "tags": {tag: True},
                                  "text": None, "symbols": []}]},
                sid="R-" + c["id"][2:])

    # W18 on a page: each pulse button of the descriptors' `buttons`. It asks first, then holds its tag true for the
    # length the descriptor gives and lets it go; the step reads all of that on the tag and on the button, and the
    # refusal mirrors it with nobody signed in.
    for desc in descs:
        route = desc.get("screen", {}).get("route", "")
        for b in desc.get("buttons", []):
            act = b.get("action", {})
            if act.get("type") != "pulse":
                continue
            tag = gen.tag_path(desc.get("tagRoot", ""), act["tag"])
            if not inside(tag):
                not_reached.append({"path": "W18", "page": route, "button": b["label"],
                                    "why": f"its tag {tag} lies {outside}"})
                continue
            c = add("C", {"session": "signed", "path": "W18", "device": "", "kind": "page", "route": route,
                          "type": PAGE_PULSE, "button": b["label"], "question": act.get("confirm") or f"{b['label']}?",
                          "tag": tag, "ms": act.get("ms", 1000)})
            add("R", {"type": "page-refusal", "session": "anonymous", "mirrors": c["id"], "path": "W18", "device": "",
                      "kind": "page", "route": route, "button": b["label"], "tag": tag},
                sid="R-" + c["id"][2:])

    # A: an alarm from a limit the tag document binds an alarm's setpoint to, and the effects file's scenes
    for kind in kinds:
        plate = profile["deviceKinds"][kind]["faceplate"]
        vm = VALUE_MEMBER.get(plate)
        if not vm:
            continue
        for d in (x for x in openable if x["kind"] == kind):
            node = resolve(f"{d['folder']}/{vm}", nodes)["node"] or {}
            hit = None
            for alarm in node.get("alarms", []):
                sp = alarm.get("setpointA")
                ref = re.fullmatch(r"\{\[\.\](\w+)\}", sp.get("value", "")) if isinstance(sp, dict) else None
                if ref and ref.group(1) in LIMITS and _usable(d, ref.group(1)) \
                        and alarm.get("mode") in ("AboveValue", "BelowValue"):
                    hit = (ref.group(1), alarm)
                    break
            if hit:
                member, alarm = hit
                add("A", {"type": "alarm", "by": "limit", "session": "signed", "device": d["title"], "kind": kind,
                          "route": d["route"], "find": d["find"], "tab": FIRST_TAB[plate], "path": "W4",
                          "ack": ACK_PATH[render], "member": member, "tag": tag_of(d, member),
                          "field": LIMITS[member], "format": LIMIT_FORMAT, "above": alarm["mode"] == "AboveValue",
                          "alarm": alarm.get("label") or alarm.get("name", ""),
                          "sources": (d["model"] or {}).get("alarmSources")})
                break
    by_id = {d["id"]: d for d in openable}
    for scene in (effects or {}).get("alarmScenes", []):
        d = by_id.get(scene.get("device"))
        if not d:
            not_reached.append({"scene": scene.get("device"), "why": "the alarm scene names a device no page draws"})
            continue
        if not inside(resolve(scene["tag"], nodes)["end"]):
            not_reached.append({"scene": scene.get("device"), "why": f"the alarm scene's tag {scene['tag']} lies {outside}"})
            continue
        add("A", {"type": "alarm", "by": "scene", "session": "signed", "device": d["title"], "kind": d["kind"],
                  "route": d["route"], "find": d["find"], "ack": ACK_PATH[render], "tag": scene["tag"],
                  "raise": scene["raise"], "clear": scene["clear"], "alarm": scene.get("text", ""),
                  "sources": (d["model"] or {}).get("alarmSources"),
                  "symbols": _symbol_readings(symbols, d["route"], f"{d['folder']}/{scene['member']}")
                  if scene.get("member") else []})

    # P: every symbol parameter bound to a tag the walk can set
    settable: dict[str, dict] = {}
    readings, not_checked = [], []
    for s in symbols:
        for param, tag in s["bind"].items():
            who = {"route": s["route"], "symbol": s["id"], "param": param, "tag": tag}
            r = resolve(tag, nodes)
            if r["kind"] != "memory":
                not_checked.append({**who, "why": NOT_SETTABLE.get(r["kind"], f"a {r['kind']} tag")})
                continue
            if not inside(r["end"]):
                not_checked.append({**who, "why": f"its value lies in {r['end']}, {outside}"})
                continue
            node = r["node"]
            if node.get("alarms"):
                not_checked.append({**who, "why": "its tag carries an alarm: a scene would raise and clear it "
                                    "(group A raises an alarm where an alarm scene is given)"})
                continue
            if str(node.get("dataType")) not in ("Boolean", "Float4", "Float8", "Int1", "Int2", "Int4", "Int8"):
                not_checked.append({**who, "why": f"a {node.get('dataType')} tag: the scenes hold numbers and Booleans"})
                continue
            if not s["find"]:
                not_checked.append({**who, "why": "the symbol shows no text by which the walk can find it"})
                continue
            rule, why = reading_rule(s["kind"], s["params"], param, render, height=s.get("height"))
            if not rule:
                not_checked.append({**who, "why": why})
                continue
            if rule["how"] == "text":
                not_checked.append({**who, "why": "a text the symbol writes as it is: the scenes hold numbers and Booleans"})
                continue
            if rule["how"] == "line":
                try:
                    number_format(1.0, rule["format"][1])
                except ValueError as e:
                    not_checked.append({**who, "why": str(e)})
                    continue
            settable.setdefault(r["end"], {"tag": r["end"], "node": node})
            readings.append({**who, "find": s["find"], "source": r["end"], "rule": rule})
    tags_set = [settable[k] for k in sorted(settable)]
    scene_values(tags_set)
    values = {t["tag"]: t["values"] for t in tags_set}
    dtypes = {t["tag"]: t["node"].get("dataType") for t in tags_set}
    # What each reading expects in each scene. A reading is a check only if the glass can tell: its
    # two scenes must read differently (a range narrower than one unit of the format gives one text
    # for both), and no other tag's reading on the same symbol may read the same text in a scene (a
    # symbol bound to the wrong tag would pass). Such a reading is listed as not checked.
    kept = []
    for r in readings:
        who = {k: r[k] for k in ("route", "symbol", "param", "tag")}
        try:
            r["expects"] = [expect_of(r["rule"], values[r["source"]][n], dtypes[r["source"]]) for n in (0, 1)]
        except ValueError as e:
            not_checked.append({**who, "why": str(e)})
            continue
        if r["expects"][0] == r["expects"][1]:
            not_checked.append({**who, "why": "its two scenes read the same on the glass "
                                f"({json.dumps(r['expects'][0], ensure_ascii=False)}): the tag's range is narrower "
                                "than one unit of the format, so the check could not fail"})
            continue
        kept.append(r)
    alike = set()
    for i, r in enumerate(kept):
        for q in kept[i + 1:]:
            if (q["route"], q["symbol"]) == (r["route"], r["symbol"]) and q["source"] != r["source"] \
                    and any(a == b for a, b in zip(r["expects"], q["expects"])):
                alike |= {id(r), id(q)}
    for r in kept:
        if id(r) in alike:
            not_checked.append({**{k: r[k] for k in ("route", "symbol", "param", "tag")},
                                "why": "another tag's reading on the same symbol reads the same text in a scene: "
                                       "the glass could not tell the two apart"})
    readings = [r for r in kept if id(r) not in alike]
    tags_set = [t for t in tags_set if any(r["source"] == t["tag"] for r in readings)]
    for n in (0, 1):
        if not readings:
            break
        rs = []
        for i, r in enumerate(readings):
            rs.append({"id": f"P-{n + 1}.{i + 1:02d}", "route": r["route"], "symbol": r["symbol"], "find": r["find"],
                       "param": r["param"], "tag": r["tag"], "source": r["source"], "value": values[r["source"]][n],
                       "expect": r["expects"][n]})
        add("P", {"type": "parity", "session": "signed", "scene": n + 1,
                  "set": {t["tag"]: t["values"][n] for t in tags_set}, "readings": rs}, sid=f"P-{n + 1}")

    # the write paths no step reaches, each with its reason
    reached = {s["path"] for s in steps if s["group"] == "C"} | {s["ack"] for s in steps if s["group"] == "A"} \
        | {s["path"] for s in steps if s["group"] == "A" and s.get("path")}
    for path in sorted(profile.get("writePaths", {}), key=lambda p: int(p[1:])):
        if path in reached or any(n.get("path") == path for n in not_reached):
            continue
        if path in FRAME_PATHS:
            why = FRAME_PATHS[path]
        elif path in ACK_PATH.values():
            why = (f"the acknowledgement of the {'module' if path == 'W8' else 'stock'} rendering's list; this plan "
                   f"is for the {render} rendering" if any(s["group"] == "A" for s in steps)
                   else "no alarm the walk can raise: no limit a tag document binds an alarm to, and no alarm scene")
        elif path == "W10":
            why = ("no device on the pages carries an interlock condition that may be bypassed "
                   + ("and is marked `write` in the device model" if devices is not None else "in the tag document"))
        else:
            members = profile["writePaths"][path].get("members", [])
            carried = [d["title"] for d in devs if any(_usable(d, m) for m in members)]
            if carried or not members:   # a path the library gained after this table was written
                why = ("the walk's glass table has no entry for this write path"
                       + (f" ({', '.join(carried)} could use it)" if carried else ""))
            else:
                why = ("no device on the pages carries " + ", ".join(f"`{m}`" for m in members)
                       + (" marked `write` in the device model" if devices is not None else " in the tag document"))
        not_reached.append({"path": path, "why": why})

    asm = {d["title"] for d in devs if d["style"] == "asm"}
    for s in steps:   # the tab an `asm` faceplate shows for the one the glass table names (COBD-045)
        if s.get("device") in asm and s.get("tab") in ASM_TAB:
            s["tab"] = ASM_TAB[s["tab"]]
    return {"schema": SCHEMA, "render": render, "provider": provider, "tagRoot": tag_root, "sourceFolders": folders,
            "inputs": {**(names or {}), "tagsGenerated": generated},
            "devices": [{"title": d["title"], "id": d["id"], "kind": d["kind"], "faceplate": d["faceplate"], "style": d["style"],
                         "route": d["route"], "find": d["find"]} for d in devs],
            "counts": {g: count[g] for g in GROUPS},
            "steps": steps,
            "parity": {"tags": [{"tag": t["tag"], "dataType": t["node"].get("dataType"), "values": t["values"],
                                 "range": t["range"]} for t in tags_set],
                       "checked": len(readings), "notChecked": not_checked},
            "notReached": not_reached, "effectsUnseen": unseen_effects,
            # present only where a trended device's faceplate has no Trend tab: kind to device titles
            **({"trendTabAbsent": {k: sorted(v) for k, v in sorted(no_trend_tab.items())}} if no_trend_tab else {})}


def plan_text(plan: dict) -> str:
    return json.dumps(plan, indent=1, ensure_ascii=False) + "\n"


EXPECT_KINDS = ("value", "written", "changes", "leaves")   # and the bounds `min`, `max`, which go together
PULSE_PATH = "W18"
# The write paths whose step reads the effects of an effects file: the command, mode, bypass, force and
# mask steps (`states`), the setpoint and limit steps (`entry`) and the pulse. The fault reset (W5)
# reads none (it raises its fault by a tag import, and the plant is not what clears it), and no step is
# generated for the frame's own paths (`FRAME_PATHS`) or for an acknowledgement (group A).
EFFECT_PATHS = tuple(sorted({"W1", "W2", "W4", "W10", "W13", "W16", "W17", PULSE_PATH, CONFIG_PATH}
                            | {v[0] for v in SETPOINTS.values()},
                            key=lambda p: int(p[1:])))


def effects_errors(effects: dict) -> list[str]:
    """What is wrong with an effects file, by the schema this module documents (wiki page 08 section
    9.5). An expectation states one thing: a `value`, bounds (`min`, `max` or both), `written`,
    `changes` or `leaves`. `returns` and `returnsWithin` belong to a pulse (W18): no other action
    returns by itself. An effect names a write path whose step reads effects (`EFFECT_PATHS`): one on
    any other path would never be checked, and is refused here."""
    bad = []
    if effects.get("schema") != EFFECTS_SCHEMA:
        bad.append(f"schema is {effects.get('schema')!r}, expected {EFFECTS_SCHEMA!r}")
    for i, c in enumerate(effects.get("choose", [])):
        if not all(isinstance(c.get(k), str) for k in ("kind", "path", "device")):
            bad.append(f"choose[{i}]: kind, path and device are required")
    for i, e in enumerate(effects.get("effects", [])):
        if not isinstance(e.get("device"), str) or not isinstance(e.get("path"), str):
            bad.append(f"effects[{i}]: device and path are required")
        elif e["path"] not in EFFECT_PATHS:
            bad.append(f"effects[{i}]: no step of write path {e['path']} reads an effect (the paths whose steps do: "
                       f"{', '.join(EFFECT_PATHS)}); the effect would be dropped without a check")
        pulse = e.get("path") == PULSE_PATH
        if "within" in e and (isinstance(e["within"], bool) or not isinstance(e["within"], (int, float)) or e["within"] <= 0):
            bad.append(f"effects[{i}]: within is a number of seconds above 0")
        if "returns" in e and (e["returns"] is not True or not pulse):
            bad.append(f"effects[{i}]: returns is true or absent, and belongs to a pulse ({PULSE_PATH})")
        if "restores" in e and (not pulse or not isinstance(e["restores"], list) or not e["restores"]
                                or not all(isinstance(m, str) and m for m in e["restores"])):
            bad.append(f"effects[{i}]: restores is a list of tag paths, and belongs to a pulse ({PULSE_PATH})")
        for j, x in enumerate(e.get("expect", [])):
            where = f"effects[{i}].expect[{j}]"
            kinds = [k for k in EXPECT_KINDS if k in x] + (["min"] if {"min", "max"} & set(x) else [])
            if not isinstance(x.get("member"), str) or len(kinds) != 1:
                bad.append(f"{where}: a member and exactly one of value, min and max, written, changes and leaves "
                           "are required")
            for k in ("written", "changes", "leaves"):
                if k in x and x[k] is not True:
                    bad.append(f"{where}: {k} is true or absent")
            if "returnsWithin" in x and not (x.get("leaves") is True and pulse):
                bad.append(f"{where}: returnsWithin belongs to an expectation with leaves, of a pulse ({PULSE_PATH})")
    for i, s in enumerate(effects.get("alarmScenes", [])):
        if not all(k in s for k in ("device", "tag", "raise", "clear")):
            bad.append(f"alarmScenes[{i}]: device, tag, raise and clear are required")
        elif not all(isinstance(s[k], dict) and s[k].get("name") == str(s["tag"]).split("/")[-1] for k in ("raise", "clear")):
            bad.append(f"alarmScenes[{i}]: raise and clear are whole definitions of the tag named, each with its name")
    return bad
