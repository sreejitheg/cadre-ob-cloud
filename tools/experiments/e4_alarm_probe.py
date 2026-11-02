"""Experiment E4: the alarm event accessors the alarm list needs (COB-PLAN-01 WP2, Table 6).

A probe project `cadre_hmi_probe` (child of `cadre_hmi_base`, deleted after use, GF-24) shows, in
gateway scope (the scope of every Perspective script), for the active alarms of the water treatment
sample:

  A1  every `get*` and `is*` method of the event object, from `dir()`, never from recall, and the
      answer of each one that takes no argument (value and type);
  A2  the same for every event data object the event answers (`get*Data` methods found by A1);
  A3  `queryStatus` with candidate source patterns for one device folder, counted;
  A4  an alarm status table whose `filters.active.conditions.source` is the device pattern of
      P502, and one for P202 (the pattern under test, read on the glass);
  A5  an acknowledge button for the P502 fault (notes and user passed, GF-21), so that A1 and A2
      show the acknowledgement data afterwards;
  A6  `cadre.hmi.alarm_list` and `cadre.hmi.alarm_count` for P502, once the parent carries them.

The probe writes nothing but the acknowledgement of A5. Re-importing the sample's tag model
restores the plant (wiki page 11 section 8).

Usage:
    python tools/experiments/e4_alarm_probe.py [--pattern-p502 X --pattern-p202 Y] --deploy
    python tools/experiments/e4_alarm_probe.py --delete
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from hmi import pv, parent as par  # noqa: E402
from hmi.framework import root_classes  # noqa: E402

CHILD = "cadre_hmi_probe"
SCOPE = "*cadre_hmi_wtp*"
STATES = "['ActiveUnacked', 'ActiveAcked', 'ClearUnacked', 'ClearAcked']"


def _dump_lines(selector: str) -> list[str]:
    """A1 and A2 for the first event whose source contains `selector`."""
    return [
        f"evs = system.alarm.queryStatus(path=['{SCOPE}'], state={STATES})",
        f"evs = [e for e in evs if '{selector}' in unicode(e.getSource())]",
        "if len(evs) == 0:",
        "\treturn 'no event'",
        "e = evs[0]",
        "def answers(o):",
        "\tout = {'type': unicode(type(o))}",
        "\tfor n in sorted(set(dir(o))):",
        "\t\tif not (n.startswith('get') or n.startswith('is')):",
        "\t\t\tcontinue",
        "\t\ttry:",
        "\t\t\tv = getattr(o, n)()",
        "\t\t\tout[n] = unicode(v)[:160] + ' <' + type(v).__name__ + '>'",
        "\t\texcept Exception as ex:",
        "\t\t\tout[n] = '! ' + type(ex).__name__",
        "\treturn out",
        "res = {'event': answers(e)}",
        "for n in sorted(set(dir(e))):",
        "\tif n.startswith('get') and n.endswith('Data'):",
        "\t\ttry:",
        "\t\t\td = getattr(e, n)()",
        "\t\t\tres[n] = answers(d) if d is not None else 'None'",
        "\t\texcept Exception as ex:",
        "\t\t\tres[n] = '! ' + type(ex).__name__",
        "return system.util.jsonEncode(res, 1)",
    ]


def _patterns_lines() -> list[str]:
    """A3: candidate patterns for the folder of P502, by the `path` and the `source` filter."""
    return [
        "out = {}",
        "cands = ['*cadre_hmi_wtp/P502/*', 'prov:default:/tag:cadre_hmi_wtp/P502/*',",
        "\t'prov:default:/tag:cadre_hmi_wtp/P502:*', '*cadre_hmi_wtp/P50*', '*:/tag:cadre_hmi_wtp/P502/*']",
        "for c in cands:",
        f"\tout['path ' + c] = len(system.alarm.queryStatus(path=[c], state={STATES}))",
        f"\tout['source ' + c] = len(system.alarm.queryStatus(source=[c], state={STATES}))",
        f"out['scope'] = len(system.alarm.queryStatus(path=['{SCOPE}'], state={STATES}))",
        f"out['sources'] = sorted([unicode(e.getSource()) for e in system.alarm.queryStatus(path=['{SCOPE}'], state={STATES})])",
        "return system.util.jsonEncode(out, 1)",
    ]


def probe_view(p502: str, p202: str) -> dict:
    def label(name, y, h, lines):
        return pv.node("ia.display.label", name, pv.cpos(16, y, 1560, h), {
            "style": {"classes": "cadre/font/label cadre/text/active", "whiteSpace": "pre-wrap",
                      "overflow": "hidden"}},
            prop_config={"props.text": pv.bind(pv.expr("now(3000)"), [pv.script_transform(lines)])})

    def table(name, x, pattern):
        return pv.node("ia.display.alarmstatustable", name, pv.cpos(x, 980, 760, 260), {
            "filters": {"active": {"conditions": {"source": pattern}}}})

    ack = pv.node("ia.input.button", "AckP502", pv.cpos(16, 1250, 200, 40), {"text": "Ack P502"},
                  events=pv.on_action([
                      f"evs = system.alarm.queryStatus(path=['{SCOPE}'], state=['ActiveUnacked', 'ClearUnacked'])",
                      "ids = [unicode(e.getId()) for e in evs if '/P502/' in unicode(e.getSource())]",
                      "system.alarm.acknowledge(ids, 'probe note', 'probe')"]))
    reset = pv.node("ia.input.button", "ResetP502", pv.cpos(232, 1250, 200, 40), {"text": "Reset P502"},
                    events=pv.on_action(["system.tag.writeBlocking(['[default]cadre_hmi_wtp/P502/fault'], [False])"]))
    raw = label("RawAck", 1504, 120, [
        f"evs = system.alarm.queryStatus(path=['{SCOPE}'], state={STATES})",
        "evs = [e for e in evs if '/P502/' in unicode(e.getSource())]",
        "out = {'n': len(evs)}",
        "for i, e in enumerate(evs):",
        "\td = e.getAckData()",
        "\tv = None",
        "\tif d is not None:",
        "\t\tfor k in d.getProperties():",
        "\t\t\tif unicode(k) == 'ackUser':",
        "\t\t\t\tv = d.getRawValueMap().get(k)",
        "\tc = e.getClearedData()",
        "\tout[str(i)] = [unicode(v), type(v).__name__, unicode(e.getState()),",
        "\t\tunicode(c.getTimestamp()) if c is not None else None, type(c.getTimestamp()).__name__ if c is not None else None]",
        f"out['listStates'] = len(system.alarm.queryStatus(path=['{SCOPE}'], state=['ActiveUnacked', 'ActiveAcked', 'ClearUnacked']))",
        "return system.util.jsonEncode(out, 1)"])
    hist = label("History", 1628, 100, [
        "out = {}",
        "for p in ['[default]cadre_hmi_wtp/TK101/level', '[default]cadre_hmi_wtp/FIT101/value']:",
        "\ttry:",
        "\t\tds = system.tag.queryTagHistory(paths=[p], rangeMinutes=60, returnSize=-1)",
        "\t\tout[p] = [ds.getRowCount(), unicode(ds.getValueAt(0, 0)) if ds.getRowCount() else None,",
        "\t\t\tunicode(ds.getValueAt(ds.getRowCount() - 1, 0)) if ds.getRowCount() else None]",
        "\texcept Exception as ex:",
        "\t\tout[p] = '! ' + unicode(ex)[:160]",
        "return system.util.jsonEncode(out, 1)"])
    lst = label("AlarmList", 1300, 200, [
        "try:",
        "\treturn system.util.jsonEncode({'list': cadre.hmi.alarm_list('" + SCOPE + "', '"
        + p502 + "'), 'count': cadre.hmi.alarm_count('" + SCOPE + "', '" + p502 + "')}, 1)",
        "except Exception as ex:",
        "\treturn 'not available: ' + unicode(ex)[:200]"])
    kids = [label("Dump", 8, 640, _dump_lines("/P502/")),
            label("Patterns", 656, 316, _patterns_lines()),
            table("TableP502", 16, p502), table("TableP202", 800, p202), ack, reset, lst, raw, hist]
    root = pv.node("ia.container.coord", "root", {}, {"style": {"overflow": "auto"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")}, children=kids)
    return pv.view(root, size={"width": 1600, "height": 1740})


def build(p502: str, p202: str) -> pv.Project:
    prj = pv.Project(CHILD, "Cadre HMI probe (E4)", parent=par.PARENT,
                     description="Experiment E4 alarm accessor probe; deleted after use")
    prj.add_view("Probe", probe_view(p502, p202))
    pages = {"/": {"title": "Probe", "viewPath": "Probe"}}
    prj.set_page_config({"pages": pages})
    return prj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern-p502", default="*cadre_hmi_wtp/P502/*")
    ap.add_argument("--pattern-p202", default="*cadre_hmi_wtp/P202/*")
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--delete", action="store_true")
    a = ap.parse_args()
    from hmi import deploy
    if a.delete:
        gw, _ = deploy._gateway()
        print(gw._req("DELETE", f"/data/api/v1/projects/{CHILD}"))
        return 0
    prj = build(a.pattern_p502, a.pattern_p202)
    if a.deploy:
        print(deploy.ensure_trial())
        print(deploy.import_project(prj))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
