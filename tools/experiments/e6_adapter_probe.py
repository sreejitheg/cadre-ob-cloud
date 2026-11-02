"""Experiment E6: how a device member that stands for a source tag reads and writes on this gateway
(SPEC-CLS-01 open item O-4), measured before the device adapter of the Citect rebuild is chosen
(COB-050, prompt D stage 1).

The Ignition-Wiki records reference and derived tags and UDT parameters as observations of exports
only (IGW:26 section 5: two reference nodes, four derived nodes) and says nothing of writing through
them, of quality, or of alarms and history on them. A probe tag folder `[default]cadre_hmi_probe`
and a probe project `cadre_hmi_probe` (child of `cadre_hmi_base`, both deleted after use) measure:

  R1  a reference tag (`valueSource` reference, `sourceTagPath`) follows its source, with an absolute
      and with a relative source path, and how soon after a write of the source;
  R2  a write to the reference tag reaches the source;
  R3  a derived tag (`deriveExpressionGetter`, `deriveExpressionSetter`) reads and writes through its
      expressions;
  R4  an expression tag refuses a write;
  R5  a reference to a source that does not exist: its quality, and what `system.tag.exists` answers
      for it, for a real member and for a missing one;
  R6  a UDT whose members take the source path from a parameter (`bindType` parameter on
      `sourceTagPath` and on `expression`, neither attested for those keys): whether it imports, where
      its definition may live, and whether its instance reads and writes;
  R7  alarms: an alarm on a source tag and one on a reference tag, and `system.alarm.queryStatus` with
      one source pattern, a list of two, and two in one comma separated string (the form the alarm
      status table documents);
  R8  the alarm status table's `filters.active.conditions.source` with one pattern and with two
      separated by a comma, read on the glass;
  R9  history on a reference tag (`historyEnabled`, `historyProvider`): whether it records;
  R10 how the gateway stores each tag (`system.tag.getConfiguration`, and the REST export).

Usage:
    python tools/experiments/e6_adapter_probe.py --deploy          (tags, then the project)
    <ctig .venv python> tools/experiments/e6_adapter_probe.py --measure --out workspace/e6
    python tools/experiments/e6_adapter_probe.py --delete          (the project; press Cleanup first)
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
BASE = f"[default]{FOLDER}"
HISTORY = "Sample_SQLite_Database"
GATEWAY = "http://localhost:8088"


def _mem(name, dtype, value, **extra):
    return {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dtype, "value": value, **extra}


def _ref(name, dtype, source, **extra):
    return {"name": name, "tagType": "AtomicTag", "valueSource": "reference", "dataType": dtype,
            "sourceTagPath": source, **extra}


def tags_document(with_udt: bool = True, udt_at_root: bool = False) -> dict:
    """The probe's tag folder. `with_udt` adds the UDT definition and instance of R6 inside the folder
    (`_types_` as a child of it); a second import tries the definition where the gateway may want it."""
    alarm = lambda n: [{"name": n, "label": "probe " + n, "priority": "Low", "setpointA": 1.0}]  # noqa: E731
    src = {"name": "src", "tagType": "Folder", "tags": [
        _mem("a", "Float8", 12.5),
        _mem("b", "Boolean", False, alarms=alarm("SrcB")),
        _mem("P1_Q", "Boolean", False),
        _mem("P1_SP", "Float8", 5.0)]}
    dev = {"name": "dev", "tagType": "Folder", "tags": [
        _ref("ref", "Float8", f"{BASE}/src/a"),
        _ref("refRel", "Float8", "[.]../src/a"),
        {"name": "der", "tagType": "AtomicTag", "valueSource": "derived", "dataType": "Float8",
         "sourceTagPath": f"{BASE}/src/a", "deriveExpressionGetter": "{source} * 2",
         "deriveExpressionSetter": "{value} / 2"},
        {"name": "exp", "tagType": "AtomicTag", "valueSource": "expr", "dataType": "Float8",
         "expression": "{" + BASE + "/src/a}"},
        _ref("refMiss", "Float8", f"{BASE}/src/none"),
        _ref("refB", "Boolean", f"{BASE}/src/b", alarms=alarm("RefB")),
        _ref("refHist", "Float8", f"{BASE}/src/a", historyEnabled=True, historyProvider=HISTORY)]}
    kids = [src, dev]
    if with_udt:
        par_path = lambda suffix: {"bindType": "parameter", "binding": f"{BASE}/src/{{Stem}}{suffix}"}  # noqa: E731
        udt = {"name": "ProbeDev", "tagType": "UdtType",
               "parameters": {"Stem": {"dataType": "String", "value": ""}},
               "tags": [
                   {"name": "state", "tagType": "AtomicTag", "valueSource": "reference", "dataType": "Boolean",
                    "sourceTagPath": par_path("_Q")},
                   {"name": "sp", "tagType": "AtomicTag", "valueSource": "reference", "dataType": "Float8",
                    "sourceTagPath": par_path("_SP")},
                   {"name": "spx", "tagType": "AtomicTag", "valueSource": "expr", "dataType": "Float8",
                    "expression": {"bindType": "parameter",
                                   "binding": "{" + BASE + "/src/{Stem}_SP} * 2"}},
                   {"name": "spy", "tagType": "AtomicTag", "valueSource": "expr", "dataType": "Float8",
                    "expression": "{" + BASE + "/src/{Stem}_SP} * 3"}]}
        inst = {"name": "U1", "tagType": "UdtInstance",
                "typeId": f"{FOLDER}/ProbeDev",
                "parameters": {"Stem": {"dataType": "String", "value": "P1"}},
                "tags": [{"name": n, "tagType": "AtomicTag"} for n in ("state", "sp", "spx", "spy")]}
        if udt_at_root:      # the definition goes to the provider's own `_types_` folder (`types_document`)
            kids.append(inst)
        else:
            kids += [{"name": "_types_", "tagType": "Folder", "tags": [udt]}, inst]
    return {"name": FOLDER, "tagType": "Folder", "tags": kids}


def types_document() -> dict:
    """The UDT definition of R6 where the gateway looks for it (GF-51): `[default]_types_/<folder>/ProbeDev`.
    The owner authorised writing there on 2026-10-10 (COBD-035)."""
    udt = next(t for t in tags_document(True, False)["tags"] if t["name"] == "_types_")["tags"][0]
    return {"name": "_types_", "tagType": "Folder", "tags": [{"name": FOLDER, "tagType": "Folder", "tags": [udt]}]}


# ---------------------------------------------------------------------------------------------
# The probe page. Every script runs in gateway scope; the functions are those IGW:22 documents
# (system.tag.readBlocking, writeBlocking, exists, getConfiguration, queryTagHistory, deleteTags;
# system.alarm.queryStatus).
# ---------------------------------------------------------------------------------------------
HELPERS = [
    f"B = '{BASE}/'",
    "def rd(names):",
    "\tout = {}",
    "\tqv = system.tag.readBlocking([B + n for n in names])",
    "\tfor n, v in zip(names, qv):",
    "\t\tout[n] = unicode(v.value) + ' | ' + unicode(v.quality)",
    "\treturn out",
    "def wr(name, value):",
    "\ttry:",
    "\t\treturn [unicode(c) for c in system.tag.writeBlocking([B + name], [value])]",
    "\texcept Exception as ex:",
    "\t\treturn '! ' + type(ex).__name__ + ' ' + unicode(ex)[:160]",
    "def ex(name):",
    "\ttry:",
    "\t\treturn unicode(system.tag.exists(B + name))",
    "\texcept Exception as e2:",
    "\t\treturn '! ' + type(e2).__name__",
    "import time",
]
ALL = "['src/a', 'dev/ref', 'dev/refRel', 'dev/der', 'dev/exp', 'dev/refMiss', 'dev/refB', 'dev/refHist', " \
      "'src/P1_Q', 'src/P1_SP', 'U1/state', 'U1/sp', 'U1/spx', 'U1/spy']"

RUN = HELPERS + [
    "o = {}",
    f"o['00 initial'] = rd({ALL})",
    "o['01 write src/a 20'] = wr('src/a', 20.0)",
    "o['02 at once'] = rd(['dev/ref', 'dev/refRel', 'dev/der', 'dev/exp'])",
    "time.sleep(2)",
    "o['03 after 2 s'] = rd(['src/a', 'dev/ref', 'dev/refRel', 'dev/der', 'dev/exp', 'dev/refHist'])",
    "o['04 write dev/ref 30'] = wr('dev/ref', 30.0)",
    "o['05 at once'] = rd(['src/a', 'dev/ref'])",
    "time.sleep(2)",
    "o['06 after 2 s'] = rd(['src/a', 'dev/ref', 'dev/refRel', 'dev/der', 'dev/exp'])",
    "o['07 write dev/refRel 40'] = wr('dev/refRel', 40.0)",
    "time.sleep(2)",
    "o['08 after 2 s'] = rd(['src/a', 'dev/ref', 'dev/refRel'])",
    "o['09 write dev/der 50'] = wr('dev/der', 50.0)",
    "time.sleep(2)",
    "o['10 after 2 s'] = rd(['src/a', 'dev/der', 'dev/ref'])",
    "o['11 write dev/exp 99'] = wr('dev/exp', 99.0)",
    "time.sleep(2)",
    "o['12 after 2 s'] = rd(['src/a', 'dev/exp'])",
    "o['13 write dev/refMiss 1'] = wr('dev/refMiss', 1.0)",
    "o['14 refMiss'] = rd(['dev/refMiss'])",
    "o['15 exists'] = dict((n, ex(n)) for n in ['dev/ref', 'dev/refMiss', 'dev/none', 'src/none', 'U1', "
    "'U1/state', 'U1/none', 'dev'])",
    "o['16 write src/P1_Q true'] = wr('src/P1_Q', True)",
    "time.sleep(2)",
    "o['17 after 2 s'] = rd(['src/P1_Q', 'U1/state'])",
    "o['18 write U1/state false'] = wr('U1/state', False)",
    "o['19 write U1/sp 7.5'] = wr('U1/sp', 7.5)",
    "time.sleep(2)",
    "o['20 after 2 s'] = rd(['src/P1_Q', 'U1/state', 'src/P1_SP', 'U1/sp', 'U1/spx', 'U1/spy'])",
    "o['21 restore'] = [wr('src/a', 12.5), wr('src/P1_SP', 5.0)]",
    "self.view.custom.run = system.util.jsonEncode(o, 1)",
]

_SRC_B = f"prov:default:/tag:{FOLDER}/src/b:/alm:*"
_REF_B = f"prov:default:/tag:{FOLDER}/dev/refB:/alm:*"
ALARMS = HELPERS + [
    "o = {}",
    "o['write src/b true'] = wr('src/b', True)",
    "time.sleep(3)",
    "o['read'] = rd(['src/b', 'dev/refB'])",
    "def qs(label, **kw):",
    "\ttry:",
    "\t\tev = system.alarm.queryStatus(state=['ActiveUnacked', 'ActiveAcked'], **kw)",
    "\t\to[label] = sorted([unicode(e.getSource()) for e in ev])",
    "\texcept Exception as e3:",
    "\t\to[label] = '! ' + type(e3).__name__ + ' ' + unicode(e3)[:160]",
    f"qs('source one, the source tag', source=['{_SRC_B}'])",
    f"qs('source one, the reference tag', source=['{_REF_B}'])",
    f"qs('source list of two', source=['{_SRC_B}', '{_REF_B}'])",
    f"qs('source two in one comma string', source=['{_SRC_B},{_REF_B}'])",
    f"qs('path list of two', path=['{_SRC_B}', '{_REF_B}'])",
    f"qs('source folder wildcard', source=['prov:default:/tag:{FOLDER}/*'])",
    "self.view.custom.alarms = system.util.jsonEncode(o, 1)",
]
CLEAR = HELPERS + ["self.view.custom.alarms = system.util.jsonEncode({'write src/b false': wr('src/b', False)}, 1)"]

HISTORY_LINES = HELPERS + [
    "o = {}",
    "for n in ['dev/refHist', 'src/a']:",
    "\ttry:",
    "\t\tds = system.tag.queryTagHistory(paths=[B + n], rangeMinutes=30, returnSize=-1)",
    "\t\to[n] = 'rows ' + unicode(ds.getRowCount())",
    "\texcept Exception as e4:",
    "\t\to[n] = '! ' + type(e4).__name__ + ' ' + unicode(e4)[:200]",
    "self.view.custom.history = system.util.jsonEncode(o, 1)",
]

CONFIG = HELPERS + [
    "o = {}",
    "for n in ['dev', 'U1', '_types_']:",
    "\ttry:",
    "\t\to[n] = system.util.jsonEncode(system.tag.getConfiguration(B + n, True))[:4000]",
    "\texcept Exception as e5:",
    "\t\to[n] = '! ' + type(e5).__name__ + ' ' + unicode(e5)[:200]",
    "self.view.custom.config = system.util.jsonEncode(o, 1)",
]

CLEANUP = [
    "o = {}",
    f"for p in ['{BASE}', '[default]_types_/{FOLDER}']:",
    "\ttry:",
    "\t\to[p] = [unicode(c) for c in system.tag.deleteTags([p])]",
    "\texcept Exception as e6:",
    "\t\to[p] = '! ' + type(e6).__name__ + ' ' + unicode(e6)[:160]",
    "self.view.custom.run = system.util.jsonEncode(o, 1)",
]


def probe_view() -> dict:
    style = {"classes": "cadre/font/label cadre/text/active", "whiteSpace": "pre-wrap", "overflow": "hidden"}

    def text(name, x, y, w, h, prop):
        return pv.node("ia.display.label", name, pv.cpos(x, y, w, h), {"style": style},
                       prop_config={"props.text": pv.bind(pv.expr("{view.custom.%s}" % prop))})

    def button(name, x, caption, lines):
        return pv.node("ia.input.button", name, pv.cpos(x, 8, 150, 36), {"text": caption}, events=pv.on_action(lines))

    def table(name, x, source):
        return pv.node("ia.display.alarmstatustable", name, pv.cpos(x, 1300, 520, 240),
                       {"filters": {"active": {"conditions": {"source": source}}}})

    live = pv.node("ia.display.label", "Live", pv.cpos(16, 56, 520, 420), {"style": style},
                   prop_config={"props.text": pv.bind(pv.expr("now(2000)"), [pv.script_transform(
                       HELPERS + [f"return system.util.jsonEncode(rd({ALL}), 1)"])])})
    bound = [pv.node("ia.display.label", "Bound" + n, pv.cpos(16 + 180 * i, 490, 170, 28), {"style": style},
                     prop_config={"props.text": pv.bind(pv.tag(f"{BASE}/dev/{n}"))})
             for i, n in enumerate(("ref", "refMiss", "der"))]
    kids = [button("Run", 16, "Run", RUN), button("Alarms", 176, "Alarms", ALARMS),
            button("Clear", 336, "Clear alarm", CLEAR), button("History", 496, "History", HISTORY_LINES),
            button("Config", 656, "Config", CONFIG), button("Cleanup", 816, "Cleanup", CLEANUP),
            live, *bound,
            text("RunOut", 552, 56, 520, 1230, "run"), text("AlarmOut", 1088, 56, 500, 600, "alarms"),
            text("HistoryOut", 1088, 670, 500, 120, "history"), text("ConfigOut", 16, 530, 520, 760, "config"),
            table("TSrc", 16, _SRC_B), table("TBoth", 544, _SRC_B + "," + _REF_B), table("TRef", 1072, _REF_B)]
    root = pv.node("ia.container.coord", "root", {}, {"style": {"overflow": "auto"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")}, children=kids)
    return pv.view(root, size={"width": 1600, "height": 1560},
                   custom={"run": "", "alarms": "", "history": "", "config": ""})


def build() -> pv.Project:
    prj = pv.Project(CHILD, "Cadre HMI probe (E6)", parent=par.PARENT,
                     description="Experiment E6 adapter probe; deleted after use")
    prj.add_view("Probe", probe_view())
    prj.set_page_config({"pages": {"/": {"title": "Probe", "viewPath": "Probe"}}})
    return prj


def measure(out: Path) -> dict:
    """Press the probe's buttons in a new session and read what each wrote (Playwright)."""
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    res = {}

    def label(page, name):
        return page.locator(f'[data-component-path$=":{name}"], [data-component-path$=".{name}"]').first

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 1600, "height": 1600}).new_page()
        page.goto(f"{GATEWAY}/data/perspective/client/{CHILD}/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)
        body = page.inner_text("body")
        res["trial_expired"] = "Trial Expired" in body

        def press(caption, wait_ms):
            page.get_by_role("button", name=caption, exact=True).click()
            page.wait_for_timeout(wait_ms)

        def texts():
            return [t for t in page.locator(".ia_labelComponent").all_inner_texts() if t.strip()]

        res["overlays_before"] = page.locator(".ia_qualityOverlay").count()
        res["labels_before"] = texts()
        press("Run", 22000)
        res["after_run"] = texts()
        press("Config", 4000)
        res["after_config"] = texts()
        press("Alarms", 12000)
        res["after_alarms"] = texts()
        res["table_rows"] = page.evaluate(
            "() => [...document.querySelectorAll('.ia_alarmStatusTableComponent, [class*=alarmStatusTable]')]"
            ".slice(0, 3).map(t => t.querySelectorAll('.ia_table__body__row').length)")
        res["table_text"] = page.evaluate(
            "() => [...document.querySelectorAll('.ia_table__body')].map(t => t.innerText.slice(0, 300))")
        page.screenshot(path=str(out / "alarms.png"), full_page=True)
        press("Clear alarm", 4000)
        page.wait_for_timeout(45000)       # let the historian store a few samples
        press("History", 5000)
        res["after_history"] = texts()
        page.screenshot(path=str(out / "final.png"), full_page=True)
        browser.close()
    (out / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--no-udt", action="store_true", help="import without the UDT of R6")
    ap.add_argument("--udt-at-root", action="store_true",
                    help="import the UDT definition under the provider's own _types_ folder (GF-51)")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--export", action="store_true", help="print the REST export of the probe folder (R10)")
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE.parent / "workspace" / "e6")
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
        print(json.dumps(deploy.export_tags("default", FOLDER), indent=1)[:12000])
        print(json.dumps(deploy.export_tags("default", f"_types_/{FOLDER}"), indent=1)[:6000])
        return 0
    if a.deploy:
        print(deploy.ensure_trial())
        if a.udt_at_root:
            print("types", deploy.import_tags("default", "", types_document()))
        print(deploy.import_tags("default", "", tags_document(not a.no_udt, a.udt_at_root)))
        print(deploy.import_project(build()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
