"""Experiment E2: the parent library live, plus probes for the facts E1 did not cover.

  Q6   A script transform returning a list of element objects drives `ia.shapes.svg`
       `props.elements` (the dynamic icon of the navigation item).
  Q7   A coordinate container in `percent` mode scales fractional positions (the tank).
  Q8   Which accessors an alarm event returned by `system.alarm.queryStatus` answers to
       (introspected with `dir()`; the top bar's message uses only measured ones).
  Q9   `queryStatus(priority=[...])` filters by priority name.
  Q10  A binding on `props.elements[1].d` redraws a path (the tank level).
  Q11  The style class animation flashes an alert frame.
  Q12  The shared docks, the top bar, the navigation menu and the faceplate dock work.

Child project `cadre_hmi_lab` (parent `cadre_hmi_base`), test tags under
`[default]cadre_hmi_lab/`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from hmi import pv, parent as par  # noqa: E402
from hmi.framework import root_classes  # noqa: E402

ROOT = HERE.parent
CHILD = "cadre_hmi_lab"
TAGS = "[default]cadre_hmi_lab"


def sym(kind, name, x, y, w, h, **params):
    return pv.node("ia.display.view", name, pv.cpos(x, y, w, h),
                   {"path": f"Automation/{kind}", "params": params})


def symbols_view() -> dict:
    kids = []
    states = [
        ("off", {}), ("on", {"on": True}), ("speed", {"on": True, "hasSpeed": True, "speed": 75}),
        ("alarm", {"on": True, "alert": True, "alertFrameStatus": "alarm", "alertFrameMode": "unacked-active"}),
        ("warning", {"alert": True, "alertFrameStatus": "warning", "alertFrameMode": "acked-active"}),
        ("caution", {"alert": True, "alertFrameStatus": "caution", "alertFrameMode": "unacked-rectified"}),
        ("auto", {"on": True, "badgeControl": "auto"}), ("manual", {"badgeControl": "manual"}),
        ("local", {"badgeControl": "local", "badgeInterlock": "interlock"}),
        ("locked", {"badgeCommandLocked": "command-locked"}), ("progress", {"progress": True}),
        ("activated", {"activated": True, "on": True}), ("vertical", {"vertical": True, "on": True}),
        ("flat", {"variant": "flat", "on": True}),
    ]
    kinds = ["Pump", "Motor", "Fan", "Valve", "AnalogValve", "Damper", "Filter", "Switch"]
    for r, kind in enumerate(kinds):
        for c, (label, p) in enumerate(states):
            params = dict(p)
            if kind in ("Valve", "AnalogValve") and "on" in params:
                params["open"] = params.pop("on")
            if kind == "AnalogValve":
                params["value"] = 40
            params.update({"hasTag": True, "tag": f"{kind[:2]}{r}{c:02d}", "readoutPosition": "bottom"})
            kids.append(sym(kind, f"{kind}_{label}", 24 + c * 96, 16 + r * 100, 72, 92, **params))
    # Readout positions
    for i, pos in enumerate(("right", "left", "top", "none")):
        kids.append(sym("Pump", f"Readout_{pos}", 24 + i * 140, 830, 120, 64, on=True, hasSpeed=True,
                        speed=50, readoutPosition=pos, hasTag=True, tag="P-101"))
    # Tanks at the reference demo's sizes
    for i, (w, h, v) in enumerate(((168, 216, 30), (130, 95, 50), (72, 138, 95), (248, 220, 70))):
        kids.append(pv.node("ia.display.view", f"Tank{i}", pv.cpos(1400 + (i % 2) * 260, 16 + (i // 2) * 240, w, h),
                            {"path": "Automation/Tank", "params": {
                                "value": v * 100, "max": 10000, "unit": "m³", "tag": f"#40{10 + i}",
                                "trend": ("rising", "stable", "falling", "fast-rising")[i]}}))
    kids.append(pv.node("ia.display.view", "TankChart", pv.cpos(1400, 520, 180, 220), {
        "path": "Automation/Tank", "params": {"value": 9000, "max": 10000, "unit": "m³", "tag": "#4014",
                                              "trend": "rising", "chart": True,
                                              "history": [20, 40, 35, 60, 55, 80, 70, 90]}}))
    for i, (lab, val, unit, sp) in enumerate((("HDG", 22, "DEG", None), ("Speed", 5, "m/s", 6),
                                               ("Pressure", 86, "hPa", None))):
        kids.append(pv.node("ia.display.view", f"Field{i}", pv.cpos(700 + i * 120, 830, 104, 64), {
            "path": "Instrument/Field", "params": {"label": lab, "value": val, "unit": unit,
                                                   "hasSetpoint": sp is not None, "setpoint": sp or 0,
                                                   "size": "enhanced" if i == 0 else "regular"}}))
    kids.append(pv.node("ia.display.view", "Readout0", pv.cpos(1100, 840, 96, 28), {
        "path": "Automation/Readout", "params": {"value": 12.5, "unit": "bar", "tag": "PT-101", "hasTag": False}}))
    root = pv.node("ia.container.coord", "root", {}, {"style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")}, children=kids)
    return pv.view(root, size={"width": 1920, "height": 920})


def probe_view() -> dict:
    lines_dir = [
        "evs = system.alarm.queryStatus(state=['ActiveUnacked', 'ActiveAcked'])",
        "if len(evs) == 0:",
        "\treturn 'no active alarms'",
        "e = evs[0]",
        "names = [n for n in dir(e) if n.startswith('get') or n.startswith('is')]",
        "return str(type(e)) + ' | ' + ', '.join(sorted(names))",
    ]
    lines_prio = [
        "out = []",
        "for p in ['Critical', 'High', 'Medium', 'Low', 'Diagnostic']:",
        "\tout.append(p + '=' + str(len(system.alarm.queryStatus(state=['ActiveUnacked', 'ActiveAcked'], priority=[p]))))",
        "return ', '.join(out)",
    ]
    lines_acc = [
        "evs = system.alarm.queryStatus(state=['ActiveUnacked', 'ActiveAcked'])",
        "if len(evs) == 0:",
        "\treturn 'none'",
        "e = evs[0]",
        "out = []",
        "for n in ['getId', 'getLabel', 'getDisplayPath', 'getSource', 'getName', 'getPriority', 'getState', 'isAcked', 'getActiveData']:",
        "\ttry:",
        "\t\tout.append(n + '=' + unicode(getattr(e, n)()))",
        "\texcept Exception as ex:",
        "\t\tout.append(n + '!' + type(ex).__name__)",
        "try:",
        "\tts = e.getActiveData().getTimestamp()",
        "\tout.append('activeData.getTimestamp=' + unicode(type(ts)) + ':' + unicode(ts))",
        "except Exception as ex:",
        "\tout.append('activeData.getTimestamp!' + type(ex).__name__)",
        "out.append('priorityType=' + unicode(type(e.getPriority())))",
        "return ' | '.join(out)",
    ]
    def probe_label(name, y, lines):
        return pv.node("ia.display.label", name, pv.cpos(24, y, 1500, 64), {
            "style": {"classes": "cadre/font/label cadre/text/active", "whiteSpace": "normal"}},
            prop_config={"props.text": pv.bind(pv.expr("now(5000)"), [pv.script_transform(lines)])})
    kids = [probe_label("AlarmType", 16, lines_dir), probe_label("PriorityFilter", 96, lines_prio),
            probe_label("Accessors", 176, lines_acc),
            pv.node("ia.display.label", "Summary", pv.cpos(24, 256, 1500, 48), {
                "style": {"classes": "cadre/font/label cadre/text/active"}},
                prop_config={"props.text": pv.bind(pv.expr("now(5000)"), [pv.script_transform([
                    "return unicode(cadre.hmi.alarm_summary())"])])}),
            pv.node("ia.shapes.svg", "DynamicIcon", pv.cpos(24, 320, 48, 48), {
                "viewBox": "0 0 24 24", "elements": []},
                prop_config={"props.elements": pv.bind(pv.expr("'pump-on-horizontal'"), [pv.script_transform([
                    "return cadre.icons.elements(value)"])])})]
    root = pv.node("ia.container.coord", "root", {}, {"style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")}, children=kids)
    return pv.view(root, size={"width": 1600, "height": 800})


def lab_tags() -> dict:
    def mem(name, dtype, value, alarms=None):
        t = {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dtype, "value": value}
        if alarms:
            t["alarms"] = alarms
        return t
    return {"name": "cadre_hmi_lab", "tagType": "Folder", "tags": [
        mem("AlarmHigh", "Boolean", True, [{"name": "Lab high alarm", "priority": "High", "setpointA": 1.0,
                                             "label": "Lab high alarm"}]),
        mem("AlarmMedium", "Boolean", True, [{"name": "Lab medium alarm", "priority": "Medium",
                                               "setpointA": 1.0, "label": "Lab medium alarm"}]),
        {"name": "P101", "tagType": "Folder", "tags": [
            mem("state", "Boolean", True), mem("cmd", "Boolean", True), mem("mode", "Int4", 0),
            mem("speed", "Float8", 75.0)]},
    ]}


def build() -> pv.Project:
    child = pv.Project(CHILD, "Cadre HMI lab", parent=par.PARENT, description="E2 experiment child")
    nav = {"items": [{"label": "Symbols", "path": "/", "icon": "dashboard"},
                     {"label": "Probe", "path": "/probe", "icon": "search"}],
           "footer": [{"label": "Alerts", "path": "/alerts", "icon": "alert-list"}]}
    sp = par.session_defaults()
    sp["custom"]["nav"] = nav
    child.set_session_props(sp)
    child.set_page_config(par.page_config("Lab", {
        "/": {"title": "Symbols", "viewPath": "Lab/Symbols"},
        "/probe": {"title": "Probe", "viewPath": "Lab/Probe"}}))
    child.add_view("Lab/Symbols", symbols_view())
    child.add_view("Lab/Probe", probe_view())
    return child


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "build"))
    ap.add_argument("--deploy", action="store_true")
    a = ap.parse_args()
    child = build()
    print("wrote", child.write(Path(a.out)), len(child.files), "files")
    if a.deploy:
        from hmi import deploy
        print(deploy.ensure_trial())
        print(deploy.import_tags("default", "", lab_tags()))
        print(deploy.import_project(child))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
