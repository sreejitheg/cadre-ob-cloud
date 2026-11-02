"""Experiment E9: the probes of the ASMP build (COB-143), measured before the features that rest on them are
built or relied on (COBD-044: suppression and out of service each proved on the gateway first).

The Ignition-Wiki does not record any of the facts below, and the leads come from the study's research
return DR1, which stays UNVERIFIED (COB-PLAN-03 section 14.1). A probe tag folder `[default]cadre_hmi_probe9`
and a probe project `cadre_hmi_probe9` (child of `cadre_hmi_base`; both deleted after use) measure:

  M1  ASMP-009: whether an alarmed tag folder carries alarm metrics: the folder browsed (`system.tag.browse`,
      IGW:22) with every child it lists, and the DR1 candidate names read where the browse shows a home
      for them (`ActiveAckCount`, `ActiveUnackCount`, `ClearUnackCount`, `HasActive`,
      `HighestActivePriority`, `ShelvedCount`);
  M2  F028: an alarm whose `timeOnDelaySeconds` is bound by expression to a member (the form
      `tools/hmi/alarms.py` writes): the seconds between the condition and the alarm's activation, with
      the member at 8 s;
  M3  F045 suppression by design: an alarm whose `enabled` is bound by expression to a member: active,
      then the member set, then whether the alarm leaves `queryStatus`;
  M4  F045 out of service: a tag imported with `alarmEvalEnabled` false (the DR1 lead's property) beside
      one without it, both in alarm, and the property read and written as `<tag>.AlarmEvalEnabled`;
  M5  F045 shelving: `system.alarm.shelve` (IGW:22, signature only) on an alarm that allows shelving and
      on one whose `shelvingAllowed` is false (the library's Critical), and what `queryStatus` answers;
  M6  F001, F003: candidate bit operators of the expression language on an Int4 word (`&`, `|`, `>>`,
      `getBit`), each an expression tag whose value and quality are read.

Every script runs in gateway scope from a button of the probe page and writes its answer into a label.

Usage:
    python tools/experiments/e9_asmp_probe.py --deploy          (tags, then the project)
    <ctig .venv python> tools/experiments/e9_asmp_probe.py --measure --out workspace/e9
    python tools/experiments/e9_asmp_probe.py --delete          (the project; press Cleanup first)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from hmi import alarms, pv, parent as par  # noqa: E402
from hmi.framework import root_classes  # noqa: E402

CHILD = "cadre_hmi_probe9"
FOLDER = "cadre_hmi_probe9"
BASE = f"[default]{FOLDER}"
GATEWAY = "http://localhost:8088"
METRICS = ["ActiveAckCount", "ActiveUnackCount", "ClearUnackCount", "HasActive", "HighestActivePriority",
           "ShelvedCount"]
BITS = {"and4": "{[.]word} & 4", "or1": "{[.]word} | 1", "shr1": "{[.]word} >> 1", "bit2": "getBit({[.]word}, 2)"}


def _mem(name, dtype, value, **extra):
    return {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dtype, "value": value, **extra}


def _folder(name, tags):
    return {"name": name, "tagType": "Folder", "tags": tags}


def tags_document() -> dict:
    hi = alarms.definition("Hi", "PRB-1", "High level", "High", "Probe", mode="AboveValue", limit="hiLimit", delay=True)
    sup = dict(alarms.definition("Sup", "PRB-2", "Suppressed by design", "High", "Probe"),
               enabled={"bindType": "Expression", "value": "!{[.]suppress}"})
    shelf = alarms.definition("Shelf", "PRB-4", "Shelvable", "High", "Probe")
    noshelf = alarms.definition("NoShelf", "PRB-4", "Not shelvable", "Critical", "Probe")
    return _folder(FOLDER, [
        _folder("alm", [_mem("level", "Float8", 0.0, alarms=[hi]), _mem("hiLimit", "Float8", 50.0),
                        _mem("hiLimitDelay", "Float8", 8.0)]),
        _folder("sup", [_mem("cond", "Boolean", True, alarms=[sup]), _mem("suppress", "Boolean", False)]),
        _folder("oos", [_mem("cond", "Boolean", True, alarms=[alarms.definition("Oos", "PRB-3", "In service", "High", "Probe")]),
                        _mem("cond2", "Boolean", True, alarmEvalEnabled=False,
                             alarms=[alarms.definition("Oos2", "PRB-3", "Out of service", "High", "Probe")])]),
        _folder("shelf", [_mem("a", "Boolean", True, alarms=[shelf]), _mem("b", "Boolean", True, alarms=[noshelf])]),
        _folder("bits", [_mem("word", "Int4", 6)] + [
            {"name": n, "tagType": "AtomicTag", "valueSource": "expr", "dataType": "Int4", "expression": e,
             "executionMode": "FixedRate"} for n, e in BITS.items()]),
    ])


# The probe page. The functions are those IGW:22 documents (system.tag.browse, readBlocking, writeBlocking,
# deleteTags; system.alarm.queryStatus, shelve, unshelve); every name this probe tries beyond them is a
# DR1 lead and is the measurement.
HELPERS = [
    f"B = '{BASE}/'",
    "import time",
    "def src(folder):",
    f"\treturn ['prov:default:/tag:{FOLDER}/' + folder + '/*']",
    "def active(folder):",
    "\ttry:",
    "\t\treturn [[unicode(e.getName()), unicode(e.getPriority()), bool(e.isAcked()), bool(e.isCleared())]",
    "\t\t\tfor e in system.alarm.queryStatus(path=src(folder))]",
    "\texcept Exception as x:",
    "\t\treturn 'error: ' + unicode(x)",
    "def rd(paths):",
    "\ttry:",
    "\t\treturn dict((p, unicode(v.value) + ' | ' + unicode(v.quality)) for p, v in zip(paths, system.tag.readBlocking(paths)))",
    "\texcept Exception as x:",
    "\t\treturn 'error: ' + unicode(x)",
    "def wr(path, value):",
    "\ttry:",
    "\t\treturn [unicode(c) for c in system.tag.writeBlocking([path], [value])]",
    "\texcept Exception as x:",
    "\t\treturn 'error: ' + unicode(x)",
]
METRICS_LINES = HELPERS + [
    "o = {}",
    "try:",
    "\to['browse'] = [[unicode(r['name']), unicode(r['tagType']), unicode(r.get('fullPath'))]",
    "\t\tfor r in system.tag.browse(B + 'alm').getResults()]",
    "except Exception as x:",
    "\to['browse'] = 'error: ' + unicode(x)",
    "o['active'] = active('alm')",
    f"o['read'] = rd([B + 'alm/' + m for m in {METRICS!r}])",
    "self.view.custom.metrics = system.util.jsonEncode(o, 1)",
]
DELAY_LINES = HELPERS + [
    "o = {'write': wr(B + 'alm/level', 60.0), 'seen': []}",
    "t0 = time.time()",
    "for k in range(16):",
    "\ttime.sleep(1)",
    "\ta = active('alm')",
    "\to['seen'].append([round(time.time() - t0, 1), a])",
    "o['clear'] = wr(B + 'alm/level', 0.0)",
    "self.view.custom.delay = system.util.jsonEncode(o, 1)",
]
SUPPRESS_LINES = HELPERS + [
    "o = {'before': active('sup'), 'write': wr(B + 'sup/suppress', True)}",
    "time.sleep(4)",
    "o['suppressed'] = active('sup')",
    "o['back'] = wr(B + 'sup/suppress', False)",
    "time.sleep(4)",
    "o['after'] = active('sup')",
    "self.view.custom.suppress = system.util.jsonEncode(o, 1)",
]
OOS_LINES = HELPERS + [
    "o = {'before': active('oos')}",
    "o['property'] = rd([B + 'oos/cond.AlarmEvalEnabled', B + 'oos/cond2.AlarmEvalEnabled'])",
    "o['write'] = wr(B + 'oos/cond.AlarmEvalEnabled', False)",
    "time.sleep(4)",
    "o['after'] = active('oos')",
    "o['restore'] = wr(B + 'oos/cond.AlarmEvalEnabled', True)",
    "self.view.custom.oos = system.util.jsonEncode(o, 1)",
]
SHELVE_LINES = HELPERS + [
    "o = {'before': active('shelf')}",
    "for n in ('a', 'b'):",
    "\ttry:",
    f"\t\to['shelve_' + n] = unicode(system.alarm.shelve(path=['prov:default:/tag:{FOLDER}/shelf/' + n + ':/alm:*'], timeoutMinutes=1))",
    "\texcept Exception as x:",
    "\t\to['shelve_' + n] = 'error: ' + unicode(x)",
    "time.sleep(3)",
    "o['after'] = active('shelf')",
    "try:",
    f"\to['unshelve'] = unicode(system.alarm.unshelve(path=['prov:default:/tag:{FOLDER}/shelf/*']))",
    "except Exception as x:",
    "\to['unshelve'] = 'error: ' + unicode(x)",
    "self.view.custom.shelve = system.util.jsonEncode(o, 1)",
]
BITS_LINES = HELPERS + [f"self.view.custom.bits = system.util.jsonEncode(rd([B + 'bits/' + n for n in {['word'] + list(BITS)!r}]), 1)"]
CLEANUP = HELPERS + [
    "try:",
    f"\tself.view.custom.cleanup = system.util.jsonEncode([unicode(c) for c in system.tag.deleteTags(['{BASE}'])], 1)",
    "except Exception as x:",
    "\tself.view.custom.cleanup = 'error: ' + unicode(x)",
]
PROBES = [("Metrics", "metrics", METRICS_LINES), ("Delay", "delay", DELAY_LINES), ("Suppress", "suppress", SUPPRESS_LINES),
          ("OOS", "oos", OOS_LINES), ("Shelve", "shelve", SHELVE_LINES), ("Bits", "bits", BITS_LINES),
          ("Cleanup", "cleanup", CLEANUP)]


def probe_view() -> dict:
    style = {"classes": "cadre/font/label cadre/text/active", "whiteSpace": "pre-wrap", "overflow": "hidden"}
    kids = []
    for i, (caption, key, lines) in enumerate(PROBES):
        kids.append(pv.node("ia.input.button", f"B{caption}", pv.cpos(16 + 150 * i, 8, 140, 36), {"text": caption},
                            events=pv.on_action(lines)))
        kids.append(pv.node("ia.display.label", f"Out{caption}", pv.cpos(16 + 530 * (i % 3), 56 + 420 * (i // 3), 520, 410),
                            {"style": style}, prop_config={"props.text": pv.bind(pv.expr("{view.custom.%s}" % key))}))
    root = pv.node("ia.container.coord", "root", {}, {"style": {"overflow": "auto"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")}, children=kids)
    return pv.view(root, size={"width": 1600, "height": 1340}, custom={key: "" for _c, key, _l in PROBES})


def build() -> pv.Project:
    prj = pv.Project(CHILD, "Cadre HMI probe (E9)", parent=par.PARENT,
                     description="Experiment E9, the probes of the ASMP build; deleted after use")
    prj.add_view("Probe", probe_view())
    prj.set_page_config({"pages": {"/": {"title": "Probe", "viewPath": "Probe"}}})
    return prj


def measure(out: Path) -> dict:
    """Press each probe's button in a new session, in order, and read what it wrote (Playwright)."""
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 1600, "height": 1400}).new_page()
        page.goto(f"{GATEWAY}/data/perspective/client/{CHILD}/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)
        res["trial_expired"] = "Trial Expired" in page.inner_text("body")
        for caption, key, _lines in PROBES[:-1]:
            page.get_by_role("button", name=caption, exact=True).click()
            page.wait_for_timeout(22000 if caption == "Delay" else 12000)
            res[key] = page.locator(f'[data-component-path$=":Out{caption}"], [data-component-path$=".Out{caption}"]').first.inner_text()
        page.screenshot(path=str(out / "probe.png"), full_page=True)
        browser.close()
    (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE.parent / "workspace" / "e9")
    a = ap.parse_args()
    if a.measure:
        print(json.dumps(measure(a.out), indent=1, ensure_ascii=False)[:8000])
        return 0
    from hmi import deploy
    if a.delete:
        gw, _ = deploy._gateway()
        print(gw._req("DELETE", f"/data/api/v1/projects/{CHILD}"))
        return 0
    if a.deploy:
        print(deploy.ensure_trial())
        print(deploy.import_tags("default", "", tags_document()))
        print(deploy.import_project(build()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
