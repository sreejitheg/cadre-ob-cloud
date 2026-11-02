"""Sample plant: a small village water treatment plant on the Cadre HMI parent library.

The plant is defined once, here, and two things are generated from the definition so they
cannot drift apart: the tag model (`screens/wtp/tags.json`) and the four screen descriptors
(`screens/wtp/*.json`). The process follows a conventional surface water train, of the kind the
owner's reference screens show (raw water storage, coagulation, clarification, media filtration,
disinfection and pH correction, potable storage, distribution); it recreates none of them.

Simulation (measured on the gateway, wiki page 07 GF-16 to GF-18): every value is a plain tag.
Command feedback is an expression tag on `cmd`; a tank level is a self-referencing expression
tag, seeded with `coalesce`, that integrates inflow minus outflow once a second; analysers vary
around their normal values and drift out of range when the dosing that controls them stops. Auto
mode is a hysteresis on a level, again a self-referencing expression. Alarms are tag alarms;
symbols carry their alarm state through expression tags on the alarm properties.

Usage:
    python tools/plants/wtp.py            writes screens/wtp/
"""
from __future__ import annotations

import functools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from hmi import alarms, screen  # noqa: E402

OUT = ROOT / "screens" / "wtp"
TOP = "cadre_hmi_wtp"
P = f"[default]{TOP}"
RATE = 0.004          # level change in per cent per second per (m3/h) of net flow
NOW = "toMillis(now())"
# History on the analogue members (analyser, flow and pressure values; tank levels), for the
# trends of COB-064. The two keys are written together, as the tag grammar requires
# (Cadre-Sandbox-ASM TAG-GRAMMAR section 4.5); the provider is the one this gateway carries
# (REST resources list of historian-provider, 2026-10-08).
HISTORY = {"historyEnabled": True, "historyProvider": "Sample_SQLite_Database"}
ILK_DEVICES = ("P101", "P301", "P502")   # the devices that carry interlocks (interlocks() below)
# The simulation's reset (session 2, 2026-10-09). Importing the tag model returns every memory member to
# its configured value but leaves a self-referencing expression tag at the value it holds (measured, wiki
# page 07): tank levels drained or filled across imports, so an import alone no longer restored the plant.
# While `sim/reset` is true every self-referencing member that holds plant state (levels, dead bands, the
# latch times) returns to its initial value (a pump's `state` follows its command); a restore imports
# the model with it true, then with it false (`with_reset`, tools/compare/wtp_suite.py).
RESET_PATH = "sim/reset"


DEFAULTS = {"state": "false", "level": "50", "value": "0", "speed": "0"}


def ref(path: str, default: str | None = None) -> str:
    """A cross-folder reference with a default. At start-up a chain of expression tags reads
    null from members not yet evaluated, and null spreads through every expression that reads it
    (measured on the first build, GF-19); `coalesce` stops it at the first step."""
    d = default if default is not None else DEFAULTS.get(path.split("/")[-1], "0")
    return "coalesce({" + f"{P}/{path}" + "}, " + d + ")"


def clamp(x: str) -> str:
    return f"if(({x}) > 100, 100, if(({x}) < 0, 0, ({x})))"


def mem(name, dt, value):
    return {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dt, "value": value}


def expr(name, dt, expression, alarms=None, history=False):
    t = {"name": name, "tagType": "AtomicTag", "valueSource": "expr", "dataType": dt,
         "expression": expression, "executionMode": "FixedRate"}
    if alarms:
        t["alarms"] = alarms
    if history:
        t.update(HISTORY)
    return t


# The sample's plant hierarchy (F033, COB-141): the plant at the overview, an area for each page beneath it.
NODES = {"Overview": "WTP", "Intake": "WTP/Intake", "Filtration": "WTP/Filtration", "Disinfection": "WTP/Disinfection"}


@functools.lru_cache(maxsize=1)
def device_nodes() -> dict[str, str]:
    """Each device folder's node: that of the deepest page that draws it (`screen.device_nodes`)."""
    return {path.split("/", 1)[-1]: node for path, node in
            screen.device_nodes([overview(), intake(), filtration(), disinfection()]).items()}


def alarm(name, tag, text, priority, mode=None, setpoint=1.0, limit=None, delay=False):
    """A tag alarm in the library's one form (`tools/hmi/alarms.py`): the label, the display path of the
    device's node, shelving by priority. With `limit`, the setpoint follows that member of the folder, so
    a limit written from the faceplate moves the alarm (COB-062): an expression-bound alarm property,
    measured on the gateway for `setpointA` before use (wiki page 07); with `delay`, the on-delay follows
    the limit's delay member (F028), the same form, to be measured in the combined run (COB-143)."""
    return alarms.definition(name, tag, text, priority, device_nodes().get(tag.replace("-", ""), "WTP"),
                             mode=mode, setpoint=setpoint, limit=limit, delay=delay)


MODE_BADGE = "case({[.]mode}, 0, 'auto', 1, 'manual', 2, 'local', 'none')"
ALERT_MODE = ("if(coalesce({[.]fault/Alarms/Fault.isActive}, false), "
              "if(coalesce({[.]fault/Alarms/Fault.isAcked}, false), 'acked-active', 'unacked-active'), "
              "if(coalesce({[.]fault/Alarms/Fault.isAcked}, true), 'none', 'unacked-rectified'))")


def hysteresis(level: str, on_below: float | None = None, off_above: float | None = None,
               on_above: float | None = None, off_below: float | None = None) -> str:
    """Self-referencing on/off with a dead band (GF-16); its start value while the simulation resets."""
    reset = ref(RESET_PATH, "false")
    if on_below is not None:
        return (f"if({reset}, true, if({level} < {on_below}, true, if({level} > {off_above}, false, "
                f"coalesce({{[.]state}}, true))))")
    return (f"if({reset}, false, if({level} > {on_above}, true, if({level} < {off_below}, false, "
            f"coalesce({{[.]state}}, false))))")


# Interlocks and permissives (COB-079): the contract of wiki page 13 section 7, with the member names of
# the core device contract (SPEC-CLS-01 Table 4) where both define one. One condition per folder
# `<device>/ilk/Cnn/` (kind, text, action, ok, liveText, requiredText, bypassed, bypassable, latched,
# resetRequired) and the device summary in `<device>/ilk/`. A condition holds the device while it is not
# met and not bypassed, or while it is latched and waits for a reset. `unsatisfied` counts the conditions
# not met and not bypassed. The badge follows OpenBridge's own drawing of its two values: `interlock`
# (drawn with the duty icon) while the device is held, `interlock-inhibit` (the standby icon) while a
# condition is bypassed (COBD-023).
#
# The latch (COBD-023: a trip latches until it is reset). `notMetAt` holds the gateway time at which the
# condition was last seen not met and not bypassed (a self reference, GF-16); the faceplate's Reset writes
# the time of the request to `ilk/resetAt`; `ilk/resetSeen`, a self reference, keeps the latest request, so
# that an import, which returns the memory member `resetAt` to 0 but leaves a self reference at its value
# (GF-42), latches no trip again. A latched condition requires a reset while it is met and was
# last not met after the last reset, so a Reset pressed while the cause persists releases nothing, and
# no request member has to be cleared by the plant (the core contract's `cmd/reset` request, CDC-011, is
# a controller's to clear; this simulation has no controller).
def ilk_condition(dev, cid, kind, text, action, ok, live, required, *, bypassable=False):
    not_met = "!coalesce({[.]ok}, true) && !coalesce({[.]bypassed}, false)"
    return {"name": cid, "tagType": "Folder", "tags": [
        mem("kind", "String", kind), mem("text", "String", text), mem("action", "String", action),
        expr("ok", "Boolean", f"coalesce({ok}, false)"), expr("liveText", "String", live),
        mem("requiredText", "String", required), mem("bypassed", "Boolean", False),
        mem("bypassable", "Boolean", bypassable), mem("latched", "Boolean", kind == "trip"),
        expr("notMetAt", "Int8", f"if({ref(RESET_PATH, 'false')}, 0, if({not_met}, {NOW}, "
                                 "coalesce({[.]notMetAt}, 0)))"),
        expr("resetRequired", "Boolean",
             "coalesce({[.]latched}, false) && coalesce({[.]ok}, true) && !coalesce({[.]bypassed}, false) && "
             f"coalesce({{[.]notMetAt}}, 0) > {ref(dev + '/ilk/resetSeen', '0')}")]}


def ilk_folder(conditions: list[dict]) -> dict:
    def member(c, m, default):
        return f"coalesce({{[.]{c['name']}/{m}}}, {default})"

    def held(c):
        return (f"((!{member(c, 'ok', 'true')} && !{member(c, 'bypassed', 'false')}) || "
                f"{member(c, 'resetRequired', 'false')})")
    kinds = {c["name"]: next(t["value"] for t in c["tags"] if t["name"] == "kind") for c in conditions}
    perm = [c for c in conditions if kinds[c["name"]] == "permissive"]
    trips = [c for c in conditions if kinds[c["name"]] == "trip"]
    permitted = " && ".join(f"!{held(c)}" for c in perm) or "true"
    interlocked = " || ".join(held(c) for c in trips) or "false"
    bypassed = " || ".join(member(c, "bypassed", "false") for c in conditions) or "false"
    unsatisfied = " + ".join(f"if(!{member(c, 'ok', 'true')} && !{member(c, 'bypassed', 'false')}, 1, 0)"
                             for c in conditions) or "0"
    reset_required = " || ".join(member(c, "resetRequired", "false") for c in conditions) or "false"
    badge = ("if(!coalesce({[.]permitted}, true) || coalesce({[.]interlocked}, false), 'interlock', "
             "if(coalesce({[.]bypassed}, false), 'interlock-inhibit', 'none'))")
    return {"name": "ilk", "tagType": "Folder", "tags": conditions + [
        expr("permitted", "Boolean", permitted), expr("interlocked", "Boolean", interlocked),
        expr("bypassed", "Boolean", bypassed), expr("unsatisfied", "Int4", unsatisfied),
        expr("resetRequired", "Boolean", reset_required), mem("resetAt", "Int8", 0),
        expr("resetSeen", "Int8", f"if({ref(RESET_PATH, 'false')}, 0, if(coalesce({{[.]resetAt}}, 0) > "
                                  "coalesce({[.]resetSeen}, 0), coalesce({[.]resetAt}, 0), coalesce({[.]resetSeen}, 0)))"),
        expr("badge", "String", badge)]}


# A device with interlocks starts only while permitted and stops when interlocked; a running device
# keeps running when a permissive is lost (a permissive is a start condition). The faceplate also
# refuses Start while not permitted, so no start is left pending. A trip latches (COBD-023): the device
# stays interlocked after the cause clears until the Interlocks tab's Reset.
ILK_HOLD = ("if(coalesce({[.]state}, false), !coalesce({[.]ilk/interlocked}, false), "
            "coalesce({[.]ilk/permitted}, true) && !coalesce({[.]ilk/interlocked}, false))")


def motor_folder(fid, tag, *, cmd=True, mode=1, speed_sp=80.0, fault=False, auto=None, ilk=None):
    run = "{[.]cmd}" if auto is None else f"if({{[.]mode}} = 0, {auto}, {{[.]cmd}})"
    state = f"!coalesce({{[.]fault}}, false) && coalesce({run}, false)" + (f" && {ILK_HOLD}" if ilk else "")
    return {"name": fid, "tagType": "Folder", "tags": [
        mem("cmd", "Boolean", cmd), mem("mode", "Int4", mode), mem("speedSp", "Float8", speed_sp),
        mem("fault", "Boolean", fault) | {"alarms": [alarm("Fault", tag, "Fault", "High")]},
        expr("state", "Boolean", state),
        expr("speed", "Float8", "if(coalesce({[.]state}, false), coalesce({[.]speedSp}, 0), 0)"),
        expr("modeBadge", "String", MODE_BADGE),
        expr("alertMode", "String", ALERT_MODE),
        expr("alert", "Boolean", "coalesce({[.]alertMode}, 'none') != 'none'"),
    ] + ([ilk_folder(ilk)] if ilk else [])}


def valve_folder(fid, *, cmd=True, mode=1, auto=None):
    run = "{[.]cmd}" if auto is None else f"if({{[.]mode}} = 0, {auto}, {{[.]cmd}})"
    return {"name": fid, "tagType": "Folder", "tags": [
        mem("cmd", "Boolean", cmd), mem("mode", "Int4", mode),
        expr("state", "Boolean", f"coalesce({run}, false)"), expr("modeBadge", "String", MODE_BADGE)]}


def tank_folder(fid, tag, *, init, inflow, outflow, capacity, hi, lo, hi_prio="Medium", lo_prio="High"):
    net = f"(({inflow}) - ({outflow}))"
    return {"name": fid, "tagType": "Folder", "tags": [
        mem("hiLimit", "Float8", hi), mem("loLimit", "Float8", lo), mem("capacity", "Float8", capacity),
        expr("level", "Float8", f"if({ref(RESET_PATH, 'false')}, {init}, "
             + clamp(f"coalesce({{[.]level}}, {init}) + {net} * {RATE}") + ")",
             alarms=[alarm("High level", tag, "High level", hi_prio, "AboveValue", hi, limit="hiLimit"),
                     alarm("Low level", tag, "Low level", lo_prio, "BelowValue", lo, limit="loLimit")], history=True),
        expr("volume", "Float8", "coalesce({[.]level}, 0) * coalesce({[.]capacity}, 0) / 100"),
        expr("trend", "String", f"if({net} > 5, 'rising', if({net} < -5, 'falling', 'stable'))"),
    ]}


def analog_folder(fid, expression, alarms=None, limits=None):
    """An instrument: `value`, historised, and the limit members its alarms follow (COB-062)."""
    return {"name": fid, "tagType": "Folder", "tags": [expr("value", "Float8", expression, alarms, history=True)]
            + [mem(m, "Float8", v) for m, v in (limits or {}).items()]}


def wave(mean, amp, period_s):
    return f"({mean} + {amp} * sin({NOW} / {period_s * 159.15:.1f}))"


def interlocks() -> dict[str, list[dict]]:
    """The sample's interlocks (COB-PLAN-01 WP5 rule 6): an analogue permissive and an analogue
    trip on P-101, a discrete permissive on P-301, and a trip on P-502's fault."""
    filters_open = f"({ref('XV301/state')} || {ref('XV302/state')} || {ref('XV303/state')})"
    return {
        "P101": [ilk_condition("P101", "C01", "permissive", "Raw water tank level at least 20 %",
                               "Fill TK-101: open XV-101, or wait for the level to rise",
                               f"{ref('TK101/level')} >= 20",
                               f"numberFormat({ref('TK101/level')}, '0.0') + ' %'", "at least 20 %", bypassable=True),
                 ilk_condition("P101", "C02", "trip", "Clarified water tank level below 95 %",
                               "Stop the feed until TK-202 draws down",
                               f"{ref('TK202/level')} < 95",
                               f"numberFormat({ref('TK202/level')}, '0.0') + ' %'", "below 95 %")],
        "P301": [ilk_condition("P301", "C01", "permissive", "A filter inlet valve is open",
                               "Open XV-301, XV-302 or XV-303",
                               filters_open, f"if({filters_open}, 'Open', 'Closed')", "Open", bypassable=True)],
        "P502": [ilk_condition("P502", "C01", "trip", "Pump fault clear",
                               "Find the cause, then press Reset fault",
                               f"!{ref('P502/fault', 'false')}",
                               f"if({ref('P502/fault', 'false')}, 'Fault', 'Normal')", "Normal")],
    }


def tag_model() -> dict:
    flow = lambda pump, gain: f"({ref(pump + '/speed')} * {gain})"
    filters_open = f"({ref('XV301/state')} || {ref('XV302/state')} || {ref('XV303/state')})"
    ilk = interlocks()
    folders = [
        {"name": "sim", "tagType": "Folder", "tags": [mem("reset", "Boolean", False)]},
        valve_folder("XV101", mode=0, auto=hysteresis(ref("TK101/level"), on_below=50, off_above=80)),
        tank_folder("TK101", "TK-101", init=65, inflow=f"if({ref('XV101/state')}, 120, 0)",
                    outflow=ref("FIT101/value"), capacity=500, hi=90, lo=15),
        motor_folder("P101", "P-101", speed_sp=80, ilk=ilk["P101"]),
        analog_folder("FIT101", f"if({ref('P101/state')}, {flow('P101', 1.25)} + {wave(0, 0.6, 37)}, 0)"),
        analog_folder("AIT101", wave(8.0, 1.5, 90)),
        motor_folder("M201", "M-201", speed_sp=60),
        motor_folder("DP201", "DP-201", speed_sp=40),
        tank_folder("TK201", "TK-201", init=72, inflow="0", outflow=f"if({ref('DP201/state')}, 0.5, 0)",
                    capacity=10, hi=95, lo=20),
        motor_folder("P202", "P-202", cmd=False, speed_sp=60),
        tank_folder("TK202", "TK-202", init=55,
                    inflow=f"{ref('FIT101/value')} * 0.98 - if({ref('P202/state')}, 8, 0)",
                    outflow=ref("FIT301/value"), capacity=300, hi=90, lo=10),
        motor_folder("P301", "P-301", mode=0, speed_sp=80,
                     auto=hysteresis(ref("TK202/level"), on_above=30, off_below=15), ilk=ilk["P301"]),
        analog_folder("PIT301", f"if({ref('P301/state')}, {wave(310, 6, 53)}, 0)"),
        valve_folder("XV301", cmd=True), valve_folder("XV302", cmd=True), valve_folder("XV303", cmd=False),
        {"name": "F301", "tagType": "Folder", "tags": [expr("state", "Boolean", ref("XV301/state"))]},
        {"name": "F302", "tagType": "Folder", "tags": [expr("state", "Boolean", ref("XV302/state"))]},
        {"name": "F303", "tagType": "Folder", "tags": [expr("state", "Boolean", ref("XV303/state"))]},
        analog_folder("DPIT301", f"if({ref('XV301/state')} && {ref('P301/state')}, {wave(38, 3, 211)}, 0)"),
        analog_folder("DPIT302", f"if({ref('XV302/state')} && {ref('P301/state')}, {wave(44, 3, 233)}, 0)"),
        analog_folder("DPIT303", f"if({ref('XV303/state')} && {ref('P301/state')}, {wave(31, 3, 197)}, 0)"),
        analog_folder("FIT301", f"if({filters_open} && {ref('P301/state')}, {flow('P301', 1.25)} + {wave(0, 0.5, 41)}, 0)"),
        analog_folder("AIT301", f"if({ref('DP201/state')}, {wave(0.15, 0.03, 70)}, {wave(1.35, 0.1, 70)})",
                      [alarm("High turbidity", "AIT-301", "High turbidity", "High", "AboveValue", 1.0, limit="hiLimit",
                             delay=True)],
                      limits={"hiLimit": 1.0, "hiLimitDelay": 0.0}),   # no delay at the start (F028)
        motor_folder("DP401", "DP-401", speed_sp=35),
        tank_folder("TK401", "TK-401", init=64, inflow="0", outflow=f"if({ref('DP401/state')}, 0.4, 0)",
                    capacity=8, hi=95, lo=20),
        motor_folder("DP402", "DP-402", speed_sp=25),
        tank_folder("TK402", "TK-402", init=58, inflow="0", outflow=f"if({ref('DP402/state')}, 0.3, 0)",
                    capacity=8, hi=95, lo=20),
        tank_folder("TK501", "TK-501", init=60, inflow=ref("FIT301/value"), outflow=ref("FIT501/value"),
                    capacity=800, hi=95, lo=20),
        motor_folder("P501", "P-501", speed_sp=70),
        motor_folder("P502", "P-502", mode=0, speed_sp=70, fault=True,
                     auto=hysteresis(ref("TK501/level"), on_above=85, off_below=60), ilk=ilk["P502"]),
        analog_folder("FIT501", f"({flow('P501', 1.1)} + {flow('P502', 1.1)})"),
        analog_folder("AIT401", f"if({ref('DP401/state')}, {wave(1.2, 0.08, 110)}, {wave(0.25, 0.03, 110)})",
                      [alarm("Low chlorine", "AIT-401", "Low free chlorine", "High", "BelowValue", 0.5, limit="loLimit")],
                      limits={"loLimit": 0.5}),
        analog_folder("AIT402", f"if({ref('DP402/state')}, {wave(7.4, 0.05, 150)}, {wave(6.6, 0.05, 150)})",
                      [alarm("Low pH", "AIT-402", "Low pH", "Medium", "BelowValue", 6.8, limit="loLimit")],
                      limits={"loLimit": 6.8}),
    ]
    return {"name": TOP, "tagType": "Folder", "tags": folders}


def with_reset(model: dict, value: bool = True) -> dict:
    """A copy of the tag model whose `sim/reset` is `value`: the first import of a restore."""
    out = json.loads(json.dumps(model))
    sim = next(t for t in out["tags"] if t["name"] == "sim")
    next(t for t in sim["tags"] if t["name"] == "reset")["value"] = value
    return out


# ---------------------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------------------
def pump(id_, x, y, label, *, readout="bottom", speed=True, kind="pump"):
    tag = f"{id_[:-3]}-{id_[-3:]}"
    return {"id": id_, "kind": kind, "x": x, "y": y, "w": 48, "h": 48, "device": True, "label": label,
            "params": {"readoutPosition": readout, "hasSpeed": speed, "hasTag": True, "tag": tag,
                       "alertFrameStatus": "alarm"},
            "bind": {"on": f"{id_}/state", **({"speed": f"{id_}/speed"} if speed else {}),
                     "alert": f"{id_}/alert", "alertFrameMode": f"{id_}/alertMode",
                     "badgeControl": f"{id_}/modeBadge",
                     **({"badgeInterlock": f"{id_}/ilk/badge"} if id_ in ILK_DEVICES else {})}}


def valve(id_, x, y, label, *, readout="bottom", vertical=False):
    tag = f"{id_[:-3]}-{id_[-3:]}"
    return {"id": id_, "kind": "valve", "x": x, "y": y, "w": 48, "h": 48, "device": True, "label": label,
            "params": {"readoutPosition": readout, "hasTag": True, "tag": tag, "vertical": vertical},
            "bind": {"open": f"{id_}/state", "badgeControl": f"{id_}/modeBadge"}}


def tank(id_, x, y, w, h, label, capacity, *, device=True, compact=False):
    tag = f"{id_[:-3]}-{id_[-3:]}"
    return {"id": id_, "kind": "tank", "x": x, "y": y, "w": w, "h": h, "device": device, "label": label,
            "params": {"max": capacity, "unit": "m³", "tag": tag, "compact": compact},
            "bind": {"value": f"{id_}/volume", "trend": f"{id_}/trend"}}


# Instrument descriptions for the faceplate header (COB-062): every readout and field opens it.
INSTRUMENTS = {"FIT101": "Raw water flow", "AIT101": "Raw water turbidity", "PIT301": "Filter feed pressure",
               "DPIT301": "Filter 1 differential pressure", "DPIT302": "Filter 2 differential pressure",
               "DPIT303": "Filter 3 differential pressure", "FIT301": "Filtered water flow",
               "AIT301": "Filtered water turbidity", "AIT401": "Free chlorine", "AIT402": "Treated water pH",
               "FIT501": "Distribution flow"}


def readout(id_, x, y, unit, fmt="0.0"):
    tag = f"{id_[:-3]}-{id_[-3:]}"
    return {"id": id_, "kind": "readout", "x": x, "y": y, "w": 96, "h": 40, "device": True,
            "label": INSTRUMENTS[id_],
            "params": {"unit": unit, "format": fmt, "tag": tag, "hasTag": True},
            "bind": {"value": f"{id_}/value"}}


def with_media(pipes: list[dict], *, waste=(), dosing=()) -> list[dict]:
    """The pipes with the medium colour mode draws them in (the diagram toolbar's Color): fresh water, the sludge
    lines waste. A chemical dosing line names none and stays neutral: no medium of the palette is a dosing chemical."""
    for p in pipes:
        if p["id"] not in dosing:
            p["medium"] = "waste" if p["id"] in waste else "fresh-water"
    return pipes


def label(id_, x, y, w, text, align="left", style="label", h=24):
    return {"id": id_, "x": x, "y": y, "w": w, "h": h, "text": text, "align": align, "style": style}


def base(id_, route, title, icon, layout="diagram", w=1580, h=600):
    return {"schema": "cadre-hmi-screen/1",
            "screen": {"id": id_, "route": route, "title": title, "view": f"Screens/{id_}", "layout": layout,
                       "width": w, "height": h, "icon": icon, "node": NODES[id_]},
            "tagRoot": P, "tagModel": "external", "showTags": True, "toolbar": layout == "diagram"}


def intake() -> dict:
    d = base("Intake", "/intake", "Intake and Clarification", "tank")
    d["sections"] = [{"id": "Raw", "x": 20, "y": 20, "w": 620, "h": 540, "label": "Raw water intake"},
                     {"id": "Coag", "x": 660, "y": 20, "w": 300, "h": 540, "label": "Coagulation"},
                     {"id": "Clar", "x": 980, "y": 20, "w": 580, "h": 540, "label": "Clarification"}]
    d["symbols"] = [
        valve("XV101", 150, 156, "Raw water inlet valve"),
        tank("TK101", 260, 80, 150, 200, "Raw water tank", 500),
        pump("P101", 470, 156, "Raw water feed pump"),
        readout("FIT101", 536, 112, "m³/h"),
        readout("AIT101", 546, 228, "NTU", "0.0"),
        pump("DP201", 696, 276, "Coagulant dosing pump", readout="right"),
        tank("TK201", 665, 380, 110, 150, "Coagulant tank", 10, compact=True),
        pump("M201", 840, 156, "Flash mixer", speed=False, kind="motor"),
        {"id": "CL201", "kind": "tank", "x": 1040, "y": 80, "w": 200, "h": 200,
         "params": {"static": True, "max": 450, "unit": "m³", "tag": "CL-201"}},
        tank("TK202", 1300, 80, 150, 200, "Clarified water tank", 300),
        pump("P202", 1116, 376, "Sludge pump", readout="right"),
    ]
    d["junctions"] = [{"id": "J1", "x": 720, "y": 180}]
    d["pipes"] = [
        {"id": "p1", "from": {"x": 40, "y": 180, "end": "arrow-in"}, "to": {"ref": "XV101", "side": "left"}},
        {"id": "p2", "from": {"ref": "XV101", "side": "right"}, "to": {"ref": "TK101", "side": "left"}},
        {"id": "p3", "from": {"ref": "TK101", "side": "right"}, "to": {"ref": "P101", "side": "left"}},
        {"id": "p4", "from": {"ref": "P101", "side": "right"}, "to": {"ref": "J1"}},
        {"id": "p5", "from": {"ref": "J1"}, "to": {"ref": "M201", "side": "left"}},
        {"id": "p6", "from": {"ref": "TK201", "side": "top"}, "to": {"ref": "DP201", "side": "bottom"}},
        {"id": "p7", "from": {"ref": "DP201", "side": "top"}, "to": {"ref": "J1"}},
        {"id": "p8", "from": {"ref": "M201", "side": "right"}, "to": {"ref": "CL201", "side": "left"}},
        {"id": "p9", "from": {"ref": "CL201", "side": "right"}, "to": {"ref": "TK202", "side": "left"}},
        {"id": "p10", "from": {"ref": "TK202", "side": "right"}, "to": {"x": 1550, "y": 180, "end": "arrow-out"}},
        {"id": "p11", "from": {"ref": "CL201", "side": "bottom"}, "to": {"ref": "P202", "side": "top"}},
        {"id": "p12", "from": {"ref": "P202", "side": "bottom"}, "to": {"x": 1140, "y": 520, "end": "arrow-out"}},
    ]
    with_media(d["pipes"], waste=("p11", "p12"), dosing=("p6", "p7"))
    d["labels"] = [label("Supply", 36, 120, 170, "Raw water supply"),
                   label("TK101", 260, 288, 150, "Raw water tank", "center"),
                   label("TK201", 640, 534, 160, "Coagulant tank", "center"),
                   label("CL201", 1040, 50, 200, "Lamella clarifier", "center"),
                   label("TK202", 1300, 288, 150, "Clarified water tank", "center"),
                   label("ToFilt", 1460, 144, 96, "To filtration", "right"),
                   label("Sludge", 1156, 508, 140, "Sludge to waste")]
    return d


def filtration() -> dict:
    d = base("Filtration", "/filtration", "Filtration", "filter")
    d["sections"] = [{"id": "Feed", "x": 20, "y": 20, "w": 380, "h": 540, "label": "Filter feed"},
                     {"id": "Filters", "x": 420, "y": 20, "w": 560, "h": 540, "label": "Media filters"},
                     {"id": "Out", "x": 1000, "y": 20, "w": 560, "h": 540, "label": "Filtered water"}]
    sym = [pump("P301", 176, 276, "Filter feed pump"), readout("PIT301", 260, 228, "kPa", "0")]
    pipes = [{"id": "f1", "from": {"x": 40, "y": 300, "end": "arrow-in"}, "to": {"ref": "P301", "side": "left"}},
             {"id": "f2", "from": {"ref": "P301", "side": "right"}, "to": {"ref": "Jin"}}]
    for n, y in ((1, 140), (2, 300), (3, 460)):
        sym += [valve(f"XV30{n}", 516, y - 24, f"Filter {n} inlet valve"),
                {"id": f"F30{n}", "kind": "filter", "x": 676, "y": y - 24, "w": 48, "h": 48,
                 "params": {"readoutPosition": "bottom", "hasTag": True, "tag": f"F-30{n}", "statusText": ""},
                 "bind": {"on": f"F30{n}/state"}},
                readout(f"DPIT30{n}", 756, y - 66, "kPa", "0")]
        pipes += [{"id": f"f{n}a", "from": {"ref": "Jin"}, "to": {"ref": f"XV30{n}", "side": "left"}},
                  {"id": f"f{n}b", "from": {"ref": f"XV30{n}", "side": "right"}, "to": {"ref": f"F30{n}", "side": "left"}},
                  {"id": f"f{n}c", "from": {"ref": f"F30{n}", "side": "right"}, "to": {"ref": "Jout"}}]
    sym += [readout("FIT301", 1040, 236, "m³/h"), readout("AIT301", 1160, 236, "NTU", "0.00")]
    pipes.append({"id": "f9", "from": {"ref": "Jout"}, "to": {"x": 1550, "y": 300, "end": "arrow-out"}})
    d["symbols"] = sym
    d["junctions"] = [{"id": "Jin", "x": 440, "y": 300}, {"id": "Jout", "x": 880, "y": 300}]
    d["pipes"] = with_media(pipes)
    d["labels"] = [label("From", 36, 236, 220, "From clarified water tank"),
                   label("To", 1420, 264, 136, "To disinfection", "right")]
    return d


def disinfection() -> dict:
    d = base("Disinfection", "/disinfection", "Disinfection and Storage", "sensor-water-drop-google")
    d["sections"] = [{"id": "Dose", "x": 20, "y": 20, "w": 520, "h": 540, "label": "Chemical dosing"},
                     {"id": "Store", "x": 560, "y": 20, "w": 300, "h": 540, "label": "Potable storage"},
                     {"id": "Dist", "x": 880, "y": 20, "w": 680, "h": 540, "label": "Distribution"}]
    d["symbols"] = [
        pump("DP401", 196, 276, "Hypochlorite dosing pump", readout="right"),
        tank("TK401", 165, 380, 110, 150, "Hypochlorite tank", 8, compact=True),
        pump("DP402", 376, 276, "Caustic dosing pump", readout="right"),
        tank("TK402", 345, 380, 110, 150, "Caustic tank", 8, compact=True),
        tank("TK501", 620, 80, 180, 200, "Potable water tank", 800),
        readout("AIT401", 610, 330, "mg/L", "0.00"), readout("AIT402", 730, 330, "pH", "0.00"),
        pump("P501", 1036, 156, "Distribution pump 1"),
        pump("P502", 1036, 356, "Distribution pump 2"),
        readout("FIT501", 1260, 200, "m³/h"),
    ]
    d["junctions"] = [{"id": "J1", "x": 220, "y": 180}, {"id": "J2", "x": 400, "y": 180},
                      {"id": "J3", "x": 920, "y": 180}, {"id": "J4", "x": 1220, "y": 180}]
    d["pipes"] = [
        {"id": "d1", "from": {"x": 40, "y": 180, "end": "arrow-in"}, "to": {"ref": "J1"}},
        {"id": "d2", "from": {"ref": "J1"}, "to": {"ref": "J2"}},
        {"id": "d3", "from": {"ref": "J2"}, "to": {"ref": "TK501", "side": "left"}},
        {"id": "d4", "from": {"ref": "TK401", "side": "top"}, "to": {"ref": "DP401", "side": "bottom"}},
        {"id": "d5", "from": {"ref": "DP401", "side": "top"}, "to": {"ref": "J1"}},
        {"id": "d6", "from": {"ref": "TK402", "side": "top"}, "to": {"ref": "DP402", "side": "bottom"}},
        {"id": "d7", "from": {"ref": "DP402", "side": "top"}, "to": {"ref": "J2"}},
        {"id": "d8", "from": {"ref": "TK501", "side": "right"}, "to": {"ref": "J3"}},
        {"id": "d9", "from": {"ref": "J3"}, "to": {"ref": "P501", "side": "left"}},
        {"id": "d10", "from": {"ref": "J3"}, "to": {"ref": "P502", "side": "left"}},
        {"id": "d11", "from": {"ref": "P501", "side": "right"}, "to": {"ref": "J4"}},
        {"id": "d12", "from": {"ref": "P502", "side": "right"}, "to": {"ref": "J4"}},
        {"id": "d13", "from": {"ref": "J4"}, "to": {"x": 1550, "y": 180, "end": "arrow-out", }},
    ]
    with_media(d["pipes"], dosing=("d4", "d5", "d6", "d7"))
    d["labels"] = [label("From", 36, 144, 160, "From filtration"),
                   label("TK401", 150, 534, 140, "Hypochlorite tank", "center"),
                   label("TK402", 330, 534, 140, "Caustic tank", "center"),
                   label("TK501", 620, 288, 180, "Potable water tank", "center"),
                   label("To", 1340, 144, 216, "To village distribution", "right")]
    return d


def field(id_, label_, unit, fmt):
    tag = f"{id_[:-3]}-{id_[-3:]}"
    return {"id": f"F_{id_}", "kind": "instrument-field", "basis": "0px", "grow": 1, "device": id_,
            "label": INSTRUMENTS[id_],
            "params": {"label": label_, "unit": unit, "format": fmt, "size": "enhanced", "align": "center",
                       "tag": tag},
            "bind": {"value": f"{id_}/value"}}


def card_tank(id_, label_, capacity):
    t = tank(id_, 0, 0, 0, 0, label_, capacity)
    return {"id": f"C_{id_}", "kind": "tank", "basis": "0px", "grow": 1, "device": id_, "label": label_,
            "params": t["params"], "bind": t["bind"]}


def card_pump(id_, label_):
    p = pump(id_, 0, 0, label_)
    return {"id": f"C_{id_}", "kind": "pump", "basis": "0px", "grow": 1, "device": id_, "label": label_,
            "params": p["params"], "bind": p["bind"]}


def overview() -> dict:
    d = base("Overview", "/", "Plant Overview", "dashboard", layout="cards", w=1600, h=852)
    d["toolbar"] = False
    d["rows"] = [
        [{"id": "Production", "title": "Production", "route": "/intake", "body": {"direction": "row", "items": [
            field("FIT101", "Raw water", "m³/h", "0.0"), field("FIT301", "Filtered water", "m³/h", "0.0"),
            field("FIT501", "Distribution", "m³/h", "0.0")]}},
         {"id": "Quality", "title": "Water quality", "route": "/disinfection", "body": {"direction": "row", "items": [
             field("AIT101", "Raw turbidity", "NTU", "0.0"), field("AIT301", "Filtered turbidity", "NTU", "0.00"),
             field("AIT401", "Free chlorine", "mg/L", "0.00"), field("AIT402", "pH", "", "0.00")]}}],
        [{"id": "Storage", "title": "Storage", "body": {"direction": "row", "items": [
            card_tank("TK101", "Raw water tank", 500), card_tank("TK202", "Clarified water tank", 300),
            card_tank("TK501", "Potable water tank", 800)]}},
         {"id": "Pumps", "title": "Pumps", "body": {"direction": "row", "justify": "space-around", "items": [
             card_pump("P101", "Raw water feed pump"), card_pump("P301", "Filter feed pump"),
             card_pump("P501", "Distribution pump 1"), card_pump("P502", "Distribution pump 2")]}}],
    ]
    return d


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tags.json").write_text(json.dumps(tag_model(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, fn in (("overview", overview), ("intake", intake), ("filtration", filtration),
                     ("disinfection", disinfection)):
        (OUT / f"{name}.json").write_text(json.dumps(fn(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tm = tag_model()
    n = sum(len(f["tags"]) for f in tm["tags"])
    print(f"wrote {OUT}: {len(tm['tags'])} tag folders, {n} tags, 4 screens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
