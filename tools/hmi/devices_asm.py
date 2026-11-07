"""The generator, and the asm faceplates of the sequence and the instrument (COB-158).

The eng02 proving slice (an ASM reimagining, gaps GG-01, GM-07 and GX-01) needed three device faceplates the
library lacked in the `asm` style:

* **generator**, a new device kind: its members, its symbol (`library.py`, `Automation/Generator` and the
  larger `Automation/GeneratorSet`) and `Faceplate/ASM/Generator`;
* **sequence**, `Faceplate/ASM/Sequence`: the state rows, In service and Enable with their opposites, a Config
  row for a run time setpoint (W19) and the prerequisite as a permissive on the Interlock tab;
* **instrument**, `Faceplate/ASM/Instrument`: the value, the remote auto state, a trend and the diagnostic flags.

The member tables below are read by `screen.py` (the faceplate contract of a generated tag model, the members
the device model may list) and the views are built here from the helpers of `framework.py`. The write paths are
the library's: a command is a pulse (W18, `cadre.hmi.pulse`) and a setpoint a configuration row (W19). Every
command asks first (the Confirm row of wiki page 13 section 10.5), and every write is Administrator gated like
the others (COBD-024). Wiki page 13 section 12 records the whole.
"""
from __future__ import annotations

from . import framework as fw
from . import parts, pv, scripts
from .framework import _dv, _label, _section_title, _value_row

# ---------------------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------------------
# The generator. Core members are those a generated tag model creates for a generator; every member is optional on
# a device (a faceplate lists what the device carries).
GENERATOR_CORE = {"state": ("Boolean", False), "runText": ("String", ""), "switchText": ("String", ""),
                  "faultCode": ("Int4", 0), "cmdStart": ("Boolean", False), "cmdStop": ("Boolean", False),
                  "cmdReset": ("Boolean", False)}
GENERATOR_OPTIONAL = {"fault": "Boolean", "engineSpeed": "Float8", "voltageLL": "Float8", "fuelLevel": "Float8",
                      "fuelLowLimit": "Float8", "startDelay": "Float8", "stopDelay": "Float8",
                      "timeLeft": "Float8", "runHours": "Float8", "startsToday": "Int4", "startsYesterday": "Int4",
                      "serviceHours": "Float8", "cmdServiceDone": "Boolean", "oilPressureOk": "Boolean",
                      "readyToRun": "Boolean", "genComm": "Boolean", "plcComm": "Boolean"}
GENERATOR_PULSES = ("cmdStart", "cmdStop", "cmdReset", "cmdServiceDone")
GENERATOR_READS = list(GENERATOR_CORE) + list(GENERATOR_OPTIONAL)
GENERATOR_TREND = ("engineSpeed", "fuelLevel")

# The sequence and the instrument gain optional members for their asm faceplates: the state of the device
# (in service, enabled, normal) and the pulse commands that change it; the instrument's remote auto state, its
# diagnostic flags and the range of its bar.
SEQUENCE_OPTIONAL = {"inService": "Boolean", "enabled": "Boolean", "normal": "Boolean", "cmdInService": "Boolean",
                     "cmdOutOfService": "Boolean", "cmdEnable": "Boolean", "cmdDisable": "Boolean"}
SEQUENCE_PULSES = ("trigger", "cmdInService", "cmdOutOfService", "cmdEnable", "cmdDisable")
SEQUENCE_READS = ["step", "stepText", "trigger", "fault", "inService", "enabled", "normal", "cmdInService",
                  "cmdOutOfService", "cmdEnable", "cmdDisable"]
INSTRUMENT_OPTIONAL = {"remoteAuto": "Boolean", "oos": "Boolean", "badValue": "Boolean", "ioFault": "Boolean",
                       "overRange": "Boolean", "underRange": "Boolean", "rangeLo": "Float8", "rangeHi": "Float8"}
INSTRUMENT_FLAGS = (("oos", "Out of service"), ("badValue", "Bad value"), ("ioFault", "I/O fault"),
                    ("overRange", "Over range"), ("underRange", "Under range"))
INSTRUMENT_READS = ["value", "remoteAuto", "rangeLo", "rangeHi", "loLimit", "hiLimit"] + [m for m, _text in INSTRUMENT_FLAGS]
# (loLimit and hiLimit: the marks of the value's range bar, COB-159)

# Every asm faceplate carries the Config pane of the maintenance functions (framework._tabbed), whose controls bind the
# maintenance members in `custom.dev`: each faceplate reads them, so a device without them reads `has` false rather
# than a binding finding no key (six quality overlays per tab on the gateway, 2026-10-24).
MNT_READS = [m for m in fw.FACEPLATE_READS["pump"] if m.startswith("mnt/")]
GENERATOR_READS += [m for m in MNT_READS if m not in GENERATOR_READS]
SEQUENCE_READS += [m for m in MNT_READS if m not in SEQUENCE_READS]
INSTRUMENT_READS += [m for m in MNT_READS if m not in INSTRUMENT_READS]

# The caption of a pulse button where the device model gives none (`dev.pulses` is the member's name then).
CAPTIONS = {"trigger": "Start", "cmdStart": "Start", "cmdStop": "Stop", "cmdReset": "Reset",
            "cmdServiceDone": "Service completed", "cmdInService": "In service",
            "cmdOutOfService": "Out of service", "cmdEnable": "Enable", "cmdDisable": "Disable"}

# The asm faceplate views of the three kinds, by device kind.
VIEWS = {"generator": "Faceplate/ASM/Generator", "sequence": "Faceplate/ASM/Sequence",
         "instrument": "Faceplate/ASM/Instrument", "readout": "Faceplate/ASM/Instrument",
         "instrument-field": "Faceplate/ASM/Instrument"}
CONFIG_EXTRA = fw.ASM_CONFIG_EXTRA   # Config appears on the generator's faceplate for its service data as well


def config_shown(view: str) -> str:
    """The condition that shows the Config tab of an asm faceplate: a maintenance row, a configuration row or, for the
    generator, service data."""
    extra = "".join(" || " + _dv("has", m) for m in CONFIG_EXTRA.get(view.split("/")[-1].lower(), ()))
    return "{view.custom.dev.mnt} || {view.custom.dev.config} > 0" + extra


# ---------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------
def has(m):
    return _dv("has", m)


def val(m):
    return _dv("value", m)


def any_of(expr_of, members) -> str:
    return " || ".join(f"({expr_of(m)})" for m in members)


def bar_row(name: str, member: str, low: str = "0", high: str = "100", lo_limit: str | None = None,
            hi_limit: str | None = None) -> dict:
    """A faceplate row's range bar (COB-159, `Parts/RangeBar`): the member against its range, with the limits
    the device carries as marks. `low` and `high` are expressions; a limit member the device lacks binds an
    empty text, which the bar reads as absent. Shown only while the device carries the member."""
    def limit(m):
        return pv.bind(pv.expr(f"if({has(m)}, {val(m)}, '')")) if m else None
    cfg = {"props.params.value": pv.bind(pv.expr(val(member))), "props.params.min": pv.bind(pv.expr(low)),
           "props.params.max": pv.bind(pv.expr(high)), "position.display": pv.bind(pv.expr(has(member)))}
    for key, m in (("loLimit", lo_limit), ("hiLimit", hi_limit)):
        if m:
            cfg[f"props.params.{key}"] = limit(m)
    params = {k: v for k, v in parts.BAR_PARAMS.items() if k != "value"}
    return pv.node("ia.display.view", name, pv.fpos(basis="20px", shrink=0),
                   {"path": "Parts/RangeBar", "params": params, "style": {"margin": "0 16px"}}, prop_config=cfg)


def pulse_button(member: str, *, selected: str | None = None, name: str | None = None) -> dict:
    """The button of a pulse member: it asks (`custom.pending`) and the Confirm row writes (W18, `cadre.hmi.pulse`).
    The caption is the device model's, else the library's for the member (CAPTIONS). It shows only while the
    device may be written at the member."""
    caption = CAPTIONS[member]
    b = fw._cmd_button(name or f"Pulse_{member}", caption, [fw._pend(fw.PULSE_PATH, member, "True")],
                       selected_expr=selected, path=fw.PULSE_PATH, member=member)
    given = _dv("pulses", member)
    b["propConfig"]["props.text"] = pv.bind(pv.expr(f"if({given} = '{member}', '{caption}', {given})"))
    b["propConfig"]["position.display"] = pv.bind(pv.expr(_dv("writable", member)))
    return b


def command_row(name: str, buttons: list, members) -> dict:
    """A row of pulse buttons, shown while the device may be written at one of `members`."""
    return pv.node("ia.container.flex", name, pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "style": {"gap": "8px"}},
        prop_config={"position.display": pv.bind(pv.expr(any_of(lambda m: _dv("writable", m), members)))},
        children=buttons)


def owner_reason() -> dict:
    """Why the owner disables the device's commands, in words (COBD-044: never a silent grey button)."""
    return _label("OwnerReason", pv.fpos(basis="32px", shrink=0), "{view.custom.dev.reason}",
                  classes="cadre/font/body-active cadre/alert/badge-caution",
                  style={"padding": "4px 8px", "borderRadius": "4px", "whiteSpace": "normal"},
                  visible="len({view.custom.dev.reason}) > 0")


def abnormal(row: dict, condition: str) -> dict:
    """A value row that turns to the alarm badge while `condition` holds (colour is for the abnormal, and the
    word carries it too: redundant coding)."""
    row["children"][1]["propConfig"]["props.style.classes"] = pv.bind(pv.expr(
        f"if({condition}, 'cadre/font/body-active cadre/alert/badge-alarm', 'cadre/font/body-active cadre/text/active')"))
    return row


def header(words: list) -> dict:
    """The header strip of an asm faceplate: each word `(name, text expression, classes, shown condition)` shows
    only while it holds, then the count of the device's alarms (COBD-045)."""
    badge = {"padding": "2px 8px", "borderRadius": "4px"}
    alarms = "{view.custom.alarmCount}"
    words = list(words) + [("HeadAlarms", f"toStr({alarms}) + if({alarms} = 1, ' alarm', ' alarms')",
                            "cadre/font/body-active cadre/alert/badge-alarm", f"{alarms} > 0")]
    return pv.node("ia.container.flex", "Header", pv.fpos(basis="40px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"classes": "cadre/divider/bottom", "gap": "8px"}},
        children=[_label(name, pv.fpos(shrink=0), expr, classes=classes, style=badge, visible=shown)
                  for name, expr, classes, shown in words])


WORD, NEUTRAL, ALARM, WARN = ("cadre/font/body-active cadre/text/active", "cadre/font/body cadre/text/neutral",
                              "cadre/font/body-active cadre/alert/badge-alarm",
                              "cadre/font/body-active cadre/alert/badge-warning")


def diagnostics(groups: list) -> dict:
    """The Diagnostics tab over groups `(name, title, [(member, text expression)])`: each row the member's name in
    the device folder and its raw value, shown only where the device carries the member."""
    rows = []
    for name, title, members in groups:
        members = [(m, e) for m, e in members]
        rows.append(_section_title(f"{name}Title", title, display=" || ".join(has(m) for m, _e in members)))
        rows += [_value_row(f"{name}{i}", m, e, display=has(m)) for i, (m, e) in enumerate(members)]
    return fw._pane("diagnostics", rows, scroll=True)


def raw(m: str) -> tuple:
    return m, f"toStr({val(m)})"


def yes_no(m: str) -> tuple:
    return m, f"if({val(m)}, 'Yes', 'No')"


def trend_block(chart: dict, shown: str, title: str = "TREND") -> list:
    """The trend on the Home tab: a title, the ranges and the chart in a block of fixed height (the pane scrolls)."""
    block = pv.node("ia.container.flex", "Trend", pv.fpos(basis="272px", shrink=0), {
        "direction": "column", "style": {"gap": "4px"}},
        prop_config={"position.display": pv.bind(pv.expr(shown))}, children=[fw._trend_ranges(), chart])
    return [_section_title("TrendTitle", title, display=shown), block]


def history(prop: str) -> dict:
    return pv.bind(pv.tag_history("{view.custom.%s}" % prop, "{view.custom.hours}", "HOUR"))


def trend_tags(member: str) -> dict:
    return pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
        f"return cadre.hmi.trend_tags(self.session, value, '{member}')"])])


# ---------------------------------------------------------------------------------------
# The generator
# ---------------------------------------------------------------------------------------
def _units(m: str, fmt: str, unit: str) -> str:
    return f"numberFormat({val(m)}, '{fmt}') + ' {unit}'"


def faceplate_generator() -> dict:
    """`Faceplate/ASM/Generator` (DESIGN section 6, generator row). Home: the status words (run sequence, control
    switch, active fault), Start, Stop and Reset confirmed, the delays, the fuel level (the range bar is the place
    marked COB-159), the totals and a trend of engine speed and fuel. Config: the service data and Service
    completed (confirmed), the configuration rows and the maintenance functions. Diagnostics, Alarms, Info; the
    Interlock tab is hidden for a device without interlocks, which a generator is."""
    fault_active = f"({has('faultCode')} && {val('faultCode')} > 0) || ({has('fault')} && {val('fault')})"
    fault_text = (f"if({has('faultCode')} && {val('faultCode')} > 0, 'Fault ' + toStr({val('faultCode')}), "
                  f"if({val('fault')}, 'Fault', 'None'))")
    status = ["state", "runText", "switchText", "faultCode", "fault"]
    rows = [_section_title("StatusTitle", "STATUS", display=any_of(has, status)),
            _value_row("RunSeq", "Run sequence", val("runText"), display=has("runText")),
            _value_row("Switch", "Control switch", val("switchText"), display=has("switchText")),
            abnormal(_value_row("ActiveFault", "Active fault", fault_text,
                                display=f"{has('faultCode')} || {has('fault')}"), fault_active),
            _section_title("CommandTitle", "COMMANDS", display=any_of(lambda m: _dv("writable", m),
                                                                      ("cmdStart", "cmdStop", "cmdReset"))),
            owner_reason(),
            command_row("Commands", [pulse_button("cmdStart", selected=val("state")),
                                     pulse_button("cmdStop", selected=f"!{val('state')}"),
                                     pulse_button("cmdReset")], ("cmdStart", "cmdStop", "cmdReset")),
            _section_title("EngineTitle", "ENGINE AND OUTPUT", display=any_of(has, ("engineSpeed", "voltageLL"))),
            _value_row("Speed", "Engine speed", _units("engineSpeed", "0", "rpm"), display=has("engineSpeed")),
            _value_row("Voltage", "L-L voltage", _units("voltageLL", "0", "V"), display=has("voltageLL")),
            _section_title("TimingTitle", "TIMING", display=any_of(has, ("startDelay", "stopDelay", "timeLeft"))),
            _value_row("StartDelay", "Start delay", _units("startDelay", "0", "s"), display=has("startDelay")),
            _value_row("StopDelay", "Stop delay", _units("stopDelay", "0", "s"), display=has("stopDelay")),
            _value_row("TimeLeft", "Genset time left", _units("timeLeft", "0", "min"), display=has("timeLeft")),
            _section_title("FuelTitle", "FUEL", display=any_of(has, ("fuelLevel", "fuelLowLimit"))),
            abnormal(_value_row("Fuel", "Fuel level", _units("fuelLevel", "0.0", "%"), display=has("fuelLevel")),
                     f"{has('fuelLevel')} && {has('fuelLowLimit')} && {val('fuelLevel')} < {val('fuelLowLimit')}"),
            _value_row("FuelLow", "Low limit", _units("fuelLowLimit", "0", "%"), display=has("fuelLowLimit")),
            bar_row("FuelBar", "fuelLevel", lo_limit="fuelLowLimit"),   # the low limit mark (COB-159)
            _section_title("TotalsTitle", "TOTALS", display=any_of(has, ("runHours", "startsToday", "startsYesterday"))),
            _value_row("RunHours", "Run hours", _units("runHours", "0.0", "h"), display=has("runHours")),
            _value_row("StartsToday", "Starts today", f"numberFormat({val('startsToday')}, '0')",
                       display=has("startsToday")),
            _value_row("StartsYesterday", "Starts yesterday", f"numberFormat({val('startsYesterday')}, '0')",
                       display=has("startsYesterday"))]
    shown = any_of(lambda m: "{view.custom.trend.%s}" % m, GENERATOR_TREND)
    chart = fw.trend_chart(history("historyTags"), None, pos=pv.fpos(grow=1, basis="0px"), column=GENERATOR_TREND[0],
                           extra=({"name": GENERATOR_TREND[1], "binding": history("historyFuel"), "axis": "out",
                                   "visible": pv.bind(pv.expr("{view.custom.trend.%s}" % GENERATOR_TREND[1]))},))
    chart["propConfig"]["props.plots[0].trends[0].visible"] = pv.bind(
        pv.expr("{view.custom.trend.%s}" % GENERATOR_TREND[0]))
    rows += trend_block(chart, shown, "ENGINE SPEED AND FUEL") + [fw._message_line()]
    custom = {"hours": 1, "trend": {m: False for m in GENERATOR_TREND},
              "historyTags": [{"path": "", "alias": GENERATOR_TREND[0]}],
              "historyFuel": [{"path": "", "alias": GENERATOR_TREND[1]}]}
    custom_cfg = {"custom.trend": pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
        f"return cadre.hmi.trended(self.session, value, {list(GENERATOR_TREND)!r})"])]),
        "custom.historyTags": trend_tags(GENERATOR_TREND[0]), "custom.historyFuel": trend_tags(GENERATOR_TREND[1])}
    service = [_section_title("ServiceTitle", "SERVICE",
                              display=f"{has('serviceHours')} || {_dv('writable', 'cmdServiceDone')}"),
        _value_row("ServiceHours", "Hours since service", _units("serviceHours", "0.0", "h"),
                   display=has("serviceHours")),
        command_row("ServiceCommands", [pulse_button("cmdServiceDone", name="Pulse_cmdServiceDone")],
                    ("cmdServiceDone",))]
    head = header([
        ("HeadState", f"if({val('state')}, 'Running', 'Stopped')", WORD, has("state")),
        ("HeadRun", val("runText"), NEUTRAL, f"{has('runText')} && len({val('runText')}) > 0"),
        ("HeadSwitch", val("switchText"), NEUTRAL, f"{has('switchText')} && len({val('switchText')}) > 0"),
        ("HeadFault", "'Fault'", ALARM, fault_active)])
    diag = diagnostics([
        ("DiagStatus", "STATUS", [raw("state"), raw("runText"), raw("switchText"), raw("faultCode"), raw("fault")]),
        ("DiagReady", "READINESS", [yes_no("oilPressureOk"), yes_no("readyToRun"), yes_no("genComm"),
                                    yes_no("plcComm")]),
        ("DiagMeasure", "MEASUREMENTS", [raw(m) for m in ("engineSpeed", "voltageLL", "fuelLevel", "fuelLowLimit",
                                                          "timeLeft", "startDelay", "stopDelay")]),
        ("DiagTotals", "TOTALS", [raw(m) for m in ("runHours", "startsToday", "startsYesterday", "serviceHours")]),
        ("DiagCommand", "COMMAND", [raw(m) for m in GENERATOR_PULSES])])
    return fw._tabbed("generator", rows, custom, custom_cfg, style="asm", reads=GENERATOR_READS, header=head,
                      config_rows=service, diagnostics=diag, shown={**fw.ASM_SHOWN, "config": config_shown("generator")},
                      scroll_home=True)


# ---------------------------------------------------------------------------------------
# The sequence
# ---------------------------------------------------------------------------------------
def faceplate_sequence_asm() -> dict:
    """`Faceplate/ASM/Sequence` (DESIGN section 6, sequence row). Home: the step text and number, the state rows
    (In service, Enabled, Prerequisites met, Sequence normal), In service and Out of service, Enable and Disable
    (each confirmed, where the device carries the member) and the sequence's own pulse. Config: the run time
    setpoint as a W19 row (gap GM-07) and the maintenance functions. Diagnostics: the members of the state.
    Interlock: the prerequisite as a permissive through the library's interlock contract."""
    ilk_ok = "{view.custom.ilk.present} && {view.custom.ilk.permitted} && !{view.custom.ilk.interlocked}"
    text = pv.node("ia.display.label", "StepText", pv.fpos(basis="56px", shrink=0), {
        "style": {"classes": "cadre/font/instrument-value-m-active cadre/text/active", "whiteSpace": "normal",
                  "overflow": "hidden"}},
        prop_config={"props.text": pv.bind(pv.expr(val("stepText"))),
                     "position.display": pv.bind(pv.expr(has("stepText")))})
    state = ["stepText", "step", "inService", "enabled", "normal", "fault"]
    rows = [_section_title("StateTitle", "SEQUENCE", display=any_of(has, state) + " || {view.custom.ilk.present}"),
            text,
            _value_row("Step", "Step", f"numberFormat({val('step')}, '0')", display=has("step")),
            abnormal(_value_row("InService", "In service", f"if({val('inService')}, 'Yes', 'No')",
                                display=has("inService")), f"!{val('inService')}"),
            abnormal(_value_row("Enabled", "Enabled", f"if({val('enabled')}, 'Yes', 'No')", display=has("enabled")),
                     f"!{val('enabled')}"),
            abnormal(_value_row("Prerequisites", "Prerequisites met", f"if({ilk_ok}, 'Yes', 'No')",
                                display="{view.custom.ilk.present}"), f"!({ilk_ok})"),
            abnormal(_value_row("Normal", "Sequence normal", f"if({val('normal')}, 'Yes', 'No')",
                                display=has("normal")), f"!{val('normal')}"),
            abnormal(_value_row("Fault", "Fault", f"if({val('fault')}, 'Fault', 'Normal')", display=has("fault")),
                     val("fault")),
            _section_title("CommandTitle", "COMMANDS", display=any_of(lambda m: _dv("writable", m), SEQUENCE_PULSES)),
            owner_reason(),
            command_row("ServiceCommands", [pulse_button("cmdInService", selected=val("inService")),
                                            pulse_button("cmdOutOfService", selected=f"!{val('inService')}")],
                        ("cmdInService", "cmdOutOfService")),
            command_row("EnableCommands", [pulse_button("cmdEnable", selected=val("enabled")),
                                           pulse_button("cmdDisable", selected=f"!{val('enabled')}")],
                        ("cmdEnable", "cmdDisable")),
            command_row("Commands", [pulse_button("trigger")], ("trigger",)),
            fw._message_line()]
    head = header([
        ("HeadStep", val("stepText"), WORD, f"{has('stepText')} && len({val('stepText')}) > 0"),
        ("HeadOos", "'Out of service'", WARN, f"{has('inService')} && !{val('inService')}"),
        ("HeadDisabled", "'Disabled'", WARN, f"{has('enabled')} && !{val('enabled')}"),
        ("HeadFault", "'Fault'", ALARM, f"{has('fault')} && {val('fault')}"),
        ("HeadInterlock", "if({view.custom.ilk.interlocked}, 'Interlocked', 'Not permitted')", WARN, fw.ILK_HELD)])
    diag = diagnostics([
        ("DiagStatus", "STATUS", [raw("step"), raw("stepText"), raw("inService"), raw("enabled"), raw("normal"),
                                  raw("fault")]),
        ("DiagCommand", "COMMAND", [raw(m) for m in SEQUENCE_PULSES])])
    diag["children"].append(_value_row("DiagInterlock", "Prerequisites (ilk)", "toStr({view.custom.ilk.permitted})",
                                       display="{view.custom.ilk.present}"))
    return fw._tabbed("sequence", rows, {}, {}, style="asm", reads=SEQUENCE_READS, header=head, diagnostics=diag,
                      shown={**fw.ASM_SHOWN, "config": config_shown("sequence")})


# ---------------------------------------------------------------------------------------
# The instrument
# ---------------------------------------------------------------------------------------
def faceplate_instrument_asm() -> dict:
    """`Faceplate/ASM/Instrument` (DESIGN section 6, instrument row). Home: the value with its unit (the range
    bar is the place marked COB-159), the remote auto state, the alarm limits the device carries and a trend.
    Diagnostics: the value, the remote auto state and the diagnostic flags (out of service, bad, I/O fault, over
    and under range). Alarms and Info; Config appears only for a device with maintenance or configuration rows."""
    rows = [_section_title("ValueTitle", "VALUE", display=has("value")), fw._big_value(),
            bar_row("ValueBar", "value", f"if({has('rangeLo')}, {val('rangeLo')}, 0)",
                    f"if({has('rangeHi')}, {val('rangeHi')}, 100)", "loLimit", "hiLimit"),   # COB-159
            _value_row("RemoteAuto", "Remote auto", f"if({val('remoteAuto')}, 'Remote auto', 'Remote manual')",
                       display=has("remoteAuto"))]
    rows += fw._limit_block("value")
    chart = fw.trend_chart(pv.bind(pv.tag_history("{view.custom.historyTags}", "{view.custom.hours}", "HOUR")),
                           fw._limit_series_cfg(), pos=pv.fpos(grow=1, basis="0px"))
    rows += trend_block(chart, has("value")) + [fw._message_line()]
    custom_cfg = {"custom.unit": fw.UNIT_CFG, "custom.limitRows": fw._limit_rows_cfg("value"),
                  "custom.historyTags": pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
                      "return cadre.hmi.history_tags(value, 'value')"])])}
    custom = {"unit": "", "limitRows": [], "hours": 1, "historyTags": [{"path": "", "alias": "value"}]}
    head = header([
        ("HeadRemote", f"if({val('remoteAuto')}, 'Remote auto', 'Remote manual')", NEUTRAL, has("remoteAuto")),
        ("HeadOos", "'Out of service'", WARN, f"{has('oos')} && {val('oos')}"),
        ("HeadBad", "'Bad value'", ALARM, f"{has('badValue')} && {val('badValue')}"),
        ("HeadIo", "'I/O fault'", ALARM, f"{has('ioFault')} && {val('ioFault')}"),
        ("HeadRange", "if({over}, 'Over range', 'Under range')".format(over=val("overRange")), WARN,
         f"({has('overRange')} && {val('overRange')}) || ({has('underRange')} && {val('underRange')})")])
    diag = diagnostics([
        ("DiagValue", "VALUE", [raw("value"), yes_no("remoteAuto"), raw("rangeLo"), raw("rangeHi")]),
        ("DiagFlags", "FLAGS", [yes_no(m) for m, _t in INSTRUMENT_FLAGS])])
    return fw._tabbed("instrument", rows, custom, custom_cfg, style="asm", reads=INSTRUMENT_READS, header=head,
                      diagnostics=diag, shown={**fw.ASM_SHOWN, "config": config_shown("instrument")})


# ---------------------------------------------------------------------------------------
# The local device (NOTE-WFB-10 section 11.2 item 5)
# ---------------------------------------------------------------------------------------
LOCAL_HOME_PATH = "'Local/' + {view.params.localKind} + '/Home'"   # the Home view of the local kind the view names


def faceplate_local() -> dict:
    """`Faceplate/ASM/Local`, the one faceplate of every device of a local assembly (a kind the library lacks,
    `assembly.py`): the ASM style with the tabs Home, Alarms and Info. Home embeds the view `Local/<Kind>/Home` of the
    view parameter `localKind`, with the view's `deviceId`; Alarms and Info are those of every asm faceplate. The
    header strip holds the count of the device's alarms, the device carrying no member the library knows."""
    home = pv.node("ia.display.view", "LocalHome", pv.fpos(shrink=0), {
        "path": "", "params": {"deviceId": ""}, "useDefaultViewHeight": True, "useDefaultViewWidth": True},
        prop_config={"props.path": pv.bind(pv.expr(LOCAL_HOME_PATH)),
                     "props.params.deviceId": pv.bind(pv.expr("{view.params.deviceId}"))})
    return fw._tabbed(fw.LOCAL_KIND, [home], {}, {}, style="asm", reads=[], header=header([]),
                      tabs=fw.LOCAL_TABS, extra_params={"localKind": ""}, scroll_home=True)


def views() -> dict[str, dict]:
    """The asm faceplate views this module builds, by path."""
    return {"Faceplate/ASM/Generator": faceplate_generator(), "Faceplate/ASM/Sequence": faceplate_sequence_asm(),
            "Faceplate/ASM/Instrument": faceplate_instrument_asm(), fw.LOCAL_VIEW: faceplate_local()}
