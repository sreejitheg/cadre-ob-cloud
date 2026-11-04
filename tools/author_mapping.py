"""Author `catalogue/mapping.json`: the disposition of every reference component in the Cadre
HMI library. This file is the authored record (judgement, not parsed fact); re-run it after
editing to regenerate the JSON, then `tools/render_catalogue.py` to regenerate the wiki pages.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = {}


def put(slugs, status, cadre, note=None):
    for s in slugs.split():
        M[s] = {"status": status, "cadre": cadre}
        if note:
            M[s]["note"] = note


# Connector diagram
put("connector-diagram", "generator",
    "`tools/hmi/screen.py` diagram layout: sections, symbols, routed pipes, compiled flow (`tools/hmi/diagram.py`)",
    "Pipes are drawn by the generator, not in the Designer; flow is compiled into one expression per pipe "
    "and verified against a reference solver (gate G6).")
# App
put("app", "framework", "`Framework/*` views and the shared docks (wiki page 04)",
    "Overview page of the application frame.")
put("topbar", "framework", "`Framework/TopBar` in the shared top dock",
    "Menu button, app and page name, most severe alarm with ACK, alarm count, brilliance menu, user menu "
    "and clock are implemented; the command button, the apps button and the narrow-screen breakpoints are "
    "not (register COB-020).")
put("navbar", "framework", "`Framework/NavMenu` and `Framework/NavItem` in the shared left dock",
    "Items and footer from `session.custom.nav`; the selected item from `page.props.path`; groups, flyouts "
    "and alert badges are not implemented (register COB-021).")
put("card", "generator", "Card pattern of the cards layout (`cadre/surface/card` plus a title)",
    "The dialog option is not implemented.")
put("tabbed-card", "stock", "`ia.container.tab` with `cadre/surface/card`")
put("modal", "stock", "`system.perspective.openPopup` with a `cadre/surface/card` root")
put("badge", "partial", "Corner badges of the automation symbols",
    "A free-standing badge view is not implemented.")
put("app-bar integration-bar integration-button fleet-button", "gap", "None",
    "Multi-application integration chrome; no requirement in process automation screens so far.")
put("pagination", "stock", "Table pager of `ia.display.table` and the alarm tables")
# Input
put("input", "stock", "Stock `ia.input.*` components with `cadre/button/*` and `cadre/font/*` classes",
    "Common features page of the input family.")
put("button", "stock", "`ia.input.button` with `cadre/button/normal`, `raised`, `flat` or `selected`")
put("icon-button", "implemented",
    "Icon button pattern: an `ia.shapes.svg` icon in a flat button container (`tools/hmi/framework.py`)")
put("icon", "implemented", "`ia.shapes.svg` fed by `cadre.icons.elements(name)` (92 converted icons)")
put("checkbox", "stock", "`ia.input.checkbox`")
put("checkbox-list", "stock", "`ia.input.checkbox` instances in an `ia.container.flex`")
put("radio-button-group", "stock", "`ia.input.radio-group`")
put("dropdown-button", "stock", "`ia.input.dropdown`")
put("slider", "stock", "`ia.input.slider`")
put("double-slider", "gap", "None", "The stock `ia.input.slider` has one handle.")
put("number-input-field", "stock", "`ia.input.numeric-entry-field`")
put("text-input-field", "stock", "`ia.input.text-field`")
put("textarea-field", "stock", "`ia.input.text-area`")
put("toggle-switch", "stock", "`ia.input.toggle-switch`")
put("toggle-button-horizontal toggle-button-vertical tab-row pivot-item-group", "implemented",
    "Selected-state button row pattern (faceplate commands, alerts page tabs, diagram toolbar)")
put("progress-bar", "stock", "`ia.display.progress`")
put("sequence-loading-spinner", "partial", "`cadre/anim/spin` animation class (the progress ring of the symbols)")
put("stepper-box", "stock", "`ia.input.numeric-entry-field` (spinner mode)")
put("status-indicator", "partial", "Status row of the automation symbols")
put("user-button user-menu", "framework", "`Framework/TopBar` user button and the `Framework/UserMenu` popup")
put("app-button breadcrumb chat-message filter-chip floating-item icon-check-button message-menu-item "
    "slide-button tag", "gap", "None",
    "No requirement in process screens so far; each is a small view when needed.")
# Automation
put("automation-button", "implemented", "Common contract of every `Automation/*` symbol view",
    "Readout (status row and tag), readout side, activated, alert frame (status, mode), progress, and the "
    "four corner badges.")
put("valve digital-valve", "implemented", "`Automation/Valve` (`open`)")
put("analog-valve", "implemented", "`Automation/AnalogValve` (`open`, `value`)")
put("pump", "implemented", "`Automation/Pump` (`on`, `speed`, `variant` regular or double)",
    "`componentSize` medium (52 px holder) is not implemented (register COB-030).")
put("motor", "implemented", "`Automation/Motor`")
put("fan", "implemented", "`Automation/Fan`")
put("damper", "implemented", "`Automation/Damper`")
put("filter", "implemented", "`Automation/Filter`")
put("switch", "implemented", "`Automation/Switch`")
put("automation-tank", "implemented", "`Automation/Tank` (level, trend, chart, compact, static)",
    "The chart is a line sparkline, not the reference filled area chart (register COB-031).")
put("automation-readout", "implemented", "`Automation/Readout`")
put("automation-badge", "partial", "Corner badges inside the symbols")
put("bipolar-transistor capacitor converter diodes ground logic mosfet resistor router source transformer "
    "heat-pump", "factory",
    "One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists",
    "Electrical single-line symbols; add when a screen needs them.")
put("gauge-valve hydraulic-check-valve transmitter transmitter-stack", "gap", "None",
    "Each needs its own layout beyond a two-state icon.")
# Maritime
put("instrument-field readout", "implemented", "`Instrument/Field`")
put("readout-list-item", "stock", "`Instrument/Field` rows in an `ia.container.flex`")
put("gauge-radial gauge-radial-indicator speed-gauge", "stock",
    "`ia.chart.gauge` or `ia.chart.simple-gauge` with Cadre colours",
    "Visual parity with the reference gauge is not claimed.")
put("gauge-horizontal gauge-vertical gauge-bar-indicator", "stock", "`ia.display.linear-scale` or `ia.display.progress`")
put("gauge-trend gauge-trend-indicator", "stock", "`ia.display.sparkline` beside an `Instrument/Field`")
put("maritime", "out-of-scope", "None", "Common features page of the maritime family.")
put("azimuth-thruster azimuth-thruster-labeled bearing-indicator compass compass-flat compass-indicator "
    "compass-sector depth-actual depth-indicator heading heading-indicator heave heave-indicator main-engine "
    "main-engine-indicator pitch pitch-indicator pitch-roll pitch-roll-heave pitch-roll-yaw "
    "propulsion-azimuth-indicator rate-of-turn roll roll-indicator rot-indicator rot-linear rot-sector rudder "
    "rudder-indicator speed-arrows speed-indicator surge-sway-yaw thruster tunnel-thruster "
    "velocity-projection-plot wind wind-indicator wind-propulsion", "out-of-scope", "None",
    "Ship navigation instrument; drawn as a visible gap box if a descriptor names it.")
# Chart
put("donut-chart", "stock", "`ia.chart.pie`")
put("graph-mini", "stock", "`ia.display.sparkline`")
put("indicator-graph radial-bar-chart", "gap", "None")
# Embedding
put("alert-list alert-list-page", "framework",
    "`Framework/AlertsPage` and `Framework/AlertMenu` over `ia.display.alarmstatustable` and "
    "`ia.display.alarmjournaltable`",
    "Reference row styling, alert categories and the detail pane are not reproduced (register COB-022).")
put("alert-detail", "gap", "None", "The stock alarm tables offer a details option (`enableDetails`).")
put("alert-frame-container", "implemented",
    "Alert frame of the automation symbols (status colour, flashing when unacknowledged, dashed when rectified)")
put("accordion-card accordion-item", "stock", "`ia.display.accordion`")

out = {"meta": {"source": "catalogue/reference-interface.json", "authored": "2026-10-07",
                "statuses": ["implemented", "framework", "generator", "stock", "factory", "partial", "gap",
                             "out-of-scope"]},
       "components": M}
(ROOT / "catalogue/mapping.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(len(M), "components mapped")
