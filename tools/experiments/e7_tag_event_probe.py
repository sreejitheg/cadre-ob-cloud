"""Experiment E7: can a tag return its own pulse? (register COB-095, ctig CIM-067).

A sequence's trigger is a pulse command: the faceplate writes true (`cadre.hmi.pulse`, write path W18)
and the plant returns the tag to false. A simulated plant needs something that does the same. An
expression tag cannot be written (GF-49), so the candidate is a value-changed event script on the
memory tag itself. The Ignition-Wiki does not document tag event scripts, so the tag document's key
for one is a guess here and the gateway decides: the probe imports a tag with the key, exports it to
see whether the gateway kept it, pulses it from a session and reads what followed.

Questions:
  T1  Does a tag import keep the key `eventScripts` (a list of `{eventid, script}`), and does the
      export show it?
  T2  Does a write of true from a Perspective session run the `valueChanged` script: the counter
      rises, the start time is stamped and the tag is false again within a second?
  T3  Does a control tag without a script stay true (so that T2 is the script's doing)?
  T4  Does an expression tag that reads the stamped start time walk a step number through its
      states (2 for 5 s, 3 for 5 s, then 1), and does a second pulse start it again?

Usage:
    python tools/experiments/e7_tag_event_probe.py --deploy
    <ctig .venv python> tools/experiments/e7_tag_event_probe.py --measure
    python tools/experiments/e7_tag_event_probe.py --export
    python tools/experiments/e7_tag_event_probe.py --delete     (the project; the measure run deletes the tags)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from hmi import pv, parent as par  # noqa: E402
from hmi.framework import root_classes  # noqa: E402

CHILD = "cadre_hmi_probe"
FOLDER = "cadre_hmi_probe"
BASE = f"[default]{FOLDER}/e7"
GATEWAY = "http://localhost:8088"

# The body of the value-changed event, tab indented the way a script body is stored. The names
# `currentValue` and `initialChange` are part of the guess; if they are wrong the script fails and
# T2 reads "no".
EVENT = (f"\tif currentValue.value and not initialChange:\n"
         f"\t\tn = system.tag.readBlocking(['{BASE}/count'])[0].value\n"
         f"\t\tsystem.tag.writeBlocking(['{BASE}/count', '{BASE}/started', '{BASE}/pulse'],\n"
         f"\t\t\t[n + 1, system.date.toMillis(system.date.now()), False])\n")
ELAPSED = "(toMillis(now(1000)) - coalesce({[.]started}, 0))"
STEP = f"if(coalesce({{[.]started}}, 0) = 0, 1, if({ELAPSED} < 5000, 2, if({ELAPSED} < 10000, 3, 1)))"
NAMES = ["pulse", "plain", "count", "started", "step"]


def tags_document() -> dict:
    def mem(name, dtype, value, **extra):
        return {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dtype, "value": value,
                **extra}
    return {"name": FOLDER, "tagType": "Folder", "tags": [{"name": "e7", "tagType": "Folder", "tags": [
        mem("pulse", "Boolean", False, eventScripts=[{"eventid": "valueChanged", "script": EVENT}]),
        mem("plain", "Boolean", False), mem("count", "Int4", 0), mem("started", "Int8", 0),
        {"name": "step", "tagType": "AtomicTag", "valueSource": "expr", "dataType": "Int4", "expression": STEP},
    ]}]}


READ = [
    "def rd():",
    "\to = {}",
    f"\tqv = system.tag.readBlocking(['{BASE}/' + n for n in {NAMES}])",
    f"\tfor n, v in zip({NAMES}, qv):",
    "\t\to[n] = unicode(v.value) + ' | ' + unicode(v.quality)",
    "\treturn o",
]
PULSE = READ + [
    "import time",
    "o = {'before': rd()}",
    f"o['write'] = [unicode(c) for c in system.tag.writeBlocking(['{BASE}/pulse', '{BASE}/plain'], [True, True])]",
    "time.sleep(1.5)",
    "o['after'] = rd()",
    "self.view.custom.run = system.util.jsonEncode(o, 1)",
]
READ_NOW = READ + ["self.view.custom.run = system.util.jsonEncode({'now': rd()}, 1)"]
CLEANUP = [
    "try:",
    f"\to = [unicode(c) for c in system.tag.deleteTags(['{BASE}'])]",
    "except Exception as e7:",
    "\to = '! ' + type(e7).__name__ + ' ' + unicode(e7)[:160]",
    "self.view.custom.run = system.util.jsonEncode({'deleted': o}, 1)",
]


def probe_view() -> dict:
    style = {"classes": "cadre/font/label cadre/text/active", "whiteSpace": "pre-wrap", "overflow": "hidden"}

    def button(name, x, caption, lines):
        return pv.node("ia.input.button", name, pv.cpos(x, 8, 150, 36), {"text": caption}, events=pv.on_action(lines))

    out = pv.node("ia.display.label", "RunOut", pv.cpos(16, 56, 900, 600), {"style": style},
                  prop_config={"props.text": pv.bind(pv.expr("{view.custom.run}"))})
    root = pv.node("ia.container.coord", "root", {}, {"style": {"overflow": "auto"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")},
                   children=[button("Pulse", 16, "Pulse", PULSE), button("Read", 176, "Read", READ_NOW),
                             button("Cleanup", 336, "Cleanup", CLEANUP), out])
    return pv.view(root, size={"width": 1000, "height": 700}, custom={"run": ""})


def build() -> pv.Project:
    prj = pv.Project(CHILD, "Cadre HMI probe (E7)", parent=par.PARENT,
                     description="Experiment E7 tag event probe; deleted after use")
    prj.add_view("Probe", probe_view())
    prj.set_page_config({"pages": {"/": {"title": "Probe", "viewPath": "Probe"}}})
    return prj


def measure(out: Path) -> dict:
    """Press the probe's buttons in a new session and read what each wrote (Playwright)."""
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 1000, "height": 700}).new_page()
        page.goto(f"{GATEWAY}/data/perspective/client/{CHILD}/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)

        def press(caption, wait_ms):
            page.get_by_role("button", name=caption, exact=True).click()
            page.wait_for_timeout(wait_ms)
            return [t for t in page.locator(".ia_labelComponent").all_inner_texts() if t.strip()]

        res["read_first"] = press("Read", 2500)
        res["pulse_1"] = press("Pulse", 4500)          # about 3 s after the pulse: step 2 expected
        page.wait_for_timeout(3500)
        res["read_7s"] = press("Read", 2500)           # about 7 to 8 s: step 3 expected
        page.wait_for_timeout(4000)
        res["read_14s"] = press("Read", 2500)          # past 10 s: step 1 expected
        res["pulse_2"] = press("Pulse", 4500)          # the counter reads 2, step 2 again
        page.screenshot(path=str(out / "e7.png"))
        res["cleanup"] = press("Cleanup", 3000)
        browser.close()
    (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--export", action="store_true", help="print the REST export of the probe folder (T1)")
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE.parent / "workspace" / "e7")
    a = ap.parse_args()
    if a.measure:
        print(json.dumps(measure(a.out), indent=1, ensure_ascii=False)[:6000])
        return 0
    from hmi import deploy
    if a.delete:
        gw, _ = deploy._gateway()
        print(gw._req("DELETE", f"/data/api/v1/projects/{CHILD}"))
        return 0
    if a.export:
        print(json.dumps(deploy.export_tags("default", f"{FOLDER}/e7"), indent=1)[:6000])
        return 0
    if a.deploy:
        print(deploy.ensure_trial())
        print(deploy.import_tags("default", "", tags_document()))
        print(deploy.import_project(build()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
