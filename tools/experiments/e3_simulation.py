"""Experiment E3: can plain tags simulate a process, and can alarm state drive a symbol?

  Q14  An expression tag that reads its own value (`{[.]acc} + 1`, fixed rate) accumulates,
       so a tank level can integrate inflow minus outflow without a gateway script.
  Q15  `{[.]fault/Alarms/Fault.isActive}` and `.isAcked` resolve in an expression tag
       (IGW:14a section 5 and IGW:29 attest the path form in view expressions).
  Q16  An expression tag `{[.]cmd}` gives command feedback (state follows the command).

Tags under `[default]cadre_hmi_e3`; a probe page at `/e3` in `cadre_hmi_lab` reads them.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from hmi import pv, deploy, parent as par  # noqa: E402
from hmi.framework import root_classes  # noqa: E402
from experiments import e2_lab  # noqa: E402


def tags() -> dict:
    def mem(name, dt, v, alarms=None):
        t = {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dt, "value": v}
        if alarms:
            t["alarms"] = alarms
        return t

    def ex(name, dt, expression):
        return {"name": name, "tagType": "AtomicTag", "valueSource": "expr", "dataType": dt,
                "expression": expression, "executionMode": "FixedRate"}
    return {"name": "cadre_hmi_e3", "tagType": "Folder", "tags": [
        ex("acc", "Int4", "{[.]acc} + 1"),
        mem("fault", "Boolean", True, [{"name": "Fault", "priority": "High", "setpointA": 1.0,
                                         "label": "E3 test fault"}]),
        ex("faultActive", "Boolean", "{[.]fault/Alarms/Fault.isActive}"),
        ex("faultAcked", "Boolean", "{[.]fault/Alarms/Fault.isAcked}"),
        mem("cmd", "Boolean", False),
        ex("state", "Boolean", "{[.]cmd}"),
    ]}


def probe() -> dict:
    rows = []
    for i, t in enumerate(("acc", "fault", "faultActive", "faultAcked", "cmd", "state")):
        rows.append(pv.node("ia.display.label", f"L_{t}", pv.cpos(24, 16 + 40 * i, 600, 32), {
            "style": {"classes": "cadre/font/body cadre/text/active"}},
            prop_config={"props.text": pv.bind(pv.tag(f"[default]cadre_hmi_e3/{t}"), [pv.script_transform([
                f"return '{t}=' + unicode(value)"])])}))
    root = pv.node("ia.container.coord", "root", {}, {}, prop_config={
        "props.style.classes": root_classes("cadre/surface/page")}, children=rows)
    return pv.view(root, size={"width": 800, "height": 300})


def main() -> int:
    child = e2_lab.build()
    pc = par.page_config("Lab", {"/": {"title": "Symbols", "viewPath": "Lab/Symbols"},
                                 "/probe": {"title": "Probe", "viewPath": "Lab/Probe"},
                                 "/e3": {"title": "E3", "viewPath": "Lab/E3"}})
    child.set_page_config(pc)
    child.add_view("Lab/E3", probe())
    child.write(HERE.parent / "build")
    print(deploy.ensure_trial())
    print(deploy.import_tags("default", "", tags()))
    print(deploy.import_project(child))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
