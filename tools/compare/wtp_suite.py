"""The gateway gates of the water treatment sample, in one run per rendering (wiki page 11).

For each project: reset the trial when it is low (GF-03); import the tag model, which returns the
plant to its initial state (P-502 faulted); G8 on the five routes, each in a fresh session (GF-10);
G11 over the four descriptors; G10, the operator's walk, which changes the plant; then the tag
model again, so the next gate and the next rendering start from the initial state. Both renderings
bind the same tags (`[default]cadre_hmi_wtp`), so the re-import between them is required.

After G10 the generated walk (`walk.py`, COB-088) runs on the same project: its plan is built here from
the four descriptors, the tag model and the plant's effects file (`screens/wtp/walk-effects.json`), for
the rendering the project was built with, and written beside its result. The plant is restored before
it and after it, the last time in a `finally`, and that restore is verified by an export of the plant's
folder (`verify_plant`).

Before each gate the trial is asked for and a fresh session is probed until it shows the project
(`walk.settle_trial`): for about a minute after a reset the REST route reports a healthy trial while a
new session still shows the trial page, which gate G8 once measured as six routes with no component.
A trial page that stays fails the project by name; it is never taken for a page that passes.

G9 does not apply to the sample: its gate members are expression tags (wiki page 11 Table 3).

Usage (ctig's .venv for Playwright):
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/wtp_suite.py
        [--project cadre_hmi_wtp] [--project cadre_hmi_wtpob] --out workspace/wtp/suite
Exit 1 when any gate fails.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))

import capture  # noqa: E402
import faceplates  # noqa: E402
import functional  # noqa: E402
import walk  # noqa: E402
from hmi import deploy  # noqa: E402
from plants import wtp  # noqa: E402

GATEWAY = "http://localhost:8088/data/perspective/client"
ROUTES = ["/", "/intake", "/filtration", "/disinfection", "/trends", "/alerts"]
DESCRIPTORS = [ROOT / "screens" / "wtp" / f"{n}.json" for n in ("overview", "intake", "filtration", "disinfection")]
TAGS = ROOT / "screens" / "wtp" / "tags.json"
TAGS_FOLDER = "cadre_hmi_wtp"   # both renderings bind the tags of this one folder
EFFECTS = ROOT / "screens" / "wtp" / "walk-effects.json"
# The rendering each project was built with (`screen.py --render`): the generated walk reads a module
# component from its element, a library symbol from its text.
RENDER = {"cadre_hmi_wtpob": "module",
          # the samples of the two new frames (T2: `--frame ob` and `--frame obasm`), built with the module rendering
          "cadre_hmi_wtpobf": "module", "cadre_hmi_wtpoba": "module"}
# The Alarms tab in the plant's initial state (COB-PLAN-01 6.2 acceptance): P-502 starts faulted,
# so its list shows its one fault alarm; the sludge pump P-202 has none.
EXPECT_INITIAL = {"P-502": 1, "P-202": 0}
# The Interlocks tab in the initial state (COB-079): the conditions each device carries (G11 also
# checks the tab's count of conditions not met against the rows).
EXPECT_ILK = {"P-101": 2, "P-301": 1, "P-502": 1}
# The trend page (COB-064): one card per historised member of the descriptors' devices, 11 instruments
# and 6 tanks (wiki page 11 section 3).
EXPECT_TRENDS = 17


def restore_plant() -> dict:
    """Return the plant to its initial state. An import returns every memory member to its configured
    value but leaves a self-referencing expression tag (a tank level, a dead band) at the value it holds
    (wiki page 07), so the model is imported first with `sim/reset` true, which sends those members to
    their initial values, and then as tracked, with it false."""
    model = json.loads(TAGS.read_text(encoding="utf-8"))
    deploy.import_tags("default", "", wtp.with_reset(model, True))
    time.sleep(3)   # expression tags evaluate once a second
    r = deploy.import_tags("default", "", model)
    time.sleep(8)   # alarms follow their members
    return r


def verify_plant() -> dict:
    """The plant's folder as the gateway exports it, against the tag model: every tag of the model is
    there, and each key the model states (the value of a memory tag, an expression, a source path, the
    alarms, the history keys) exports as stated. `differences` lists what does not; `extra` the tags
    the gateway carries that the model does not define, which a tag import cannot remove (GF-25)."""
    model = walk.tag_nodes(json.loads(TAGS.read_text(encoding="utf-8")))
    live = walk.tag_nodes(deploy.export_tags("default", TAGS_FOLDER))
    differences = []
    for path, want in sorted(model.items()):
        got = live.get(path)
        if got is None:
            differences.append({"tag": path, "why": "not on the gateway"})
            continue
        keys = [k for k in want if not walk.same(want[k], got.get(k))]
        if keys:
            differences.append({"tag": path, "why": f"differs on {keys}"})
    return {"ok": not differences, "tags": len(model), "differences": differences,
            "extra": sorted(set(live) - set(model))}


def keep_initial(max_age: float = 240.0):
    """A hook for the generated walk (`walk.run(before_step=...)`): the plant restored whenever more than
    `max_age` seconds have passed since it last was. Left alone, the sample raises an alarm of its own:
    P-502 starts faulted, so the potable water tank TK-501 takes 100 m3/h and gives 77, and reaches its
    high limit of 95 per cent some six minutes after a restore. The next restore clears that alarm
    unacknowledged, and its event stays in the lists (seen on 2026-10-11 after a walk of nine minutes). A
    step puts back what it changed before the next begins, so a restore between two steps loses nothing."""
    last = [time.time()]

    def hook(_step: dict) -> None:
        if time.time() - last[0] > max_age:
            restore_plant()
            last[0] = time.time()
    return hook


def walk_plan(project: str) -> dict:
    """The generated walk's plan for one rendering of the sample (`walk.build_plan`)."""
    return walk.build_plan([json.loads(d.read_text(encoding="utf-8")) for d in DESCRIPTORS],
                           tags=json.loads(TAGS.read_text(encoding="utf-8")),
                           effects=json.loads(EFFECTS.read_text(encoding="utf-8")),
                           render=RENDER.get(project, "stock"),
                           # the keys the command line writes, so that both ways give the same bytes
                           names={"descriptors": [d.name for d in DESCRIPTORS], "devices": None, "tags": TAGS.name,
                                  "sourceTags": [], "effects": EFFECTS.name})


def generated_walk(project: str, base: str, out: Path) -> dict:
    """The generated walk on one project: the plan written to `plan.json`, the rows to `walk.json`."""
    out.mkdir(parents=True, exist_ok=True)
    plan = walk_plan(project)
    (out / "plan.json").write_bytes(walk.plan_text(plan).encode("utf-8"))
    rep = walk.run(plan, base, out, login=functional.read_login(), before_step=keep_initial())
    return {"ok": rep["ok"], "verdict": rep["verdict"], "plan": plan["counts"], "counts": rep["counts"],
            "signed_in": rep["signed_in"], "refused_by": rep["refused_by"],
            "failed": [{"id": r["id"], "detail": r["detail"]} for r in rep["rows"] if not r["ok"]]
            + [{"id": m["id"], "detail": "no row: " + m["why"]} for m in rep["missing"]],
            "not_run": rep["not_run"], "note": rep["note"], "restored": rep["restored"],
            "unrestored": rep["unrestored"]}


def g11(base: str, out: Path) -> dict:
    from playwright.sync_api import sync_playwright
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 2700, "height": 1400}).new_page()
        for d in DESCRIPTORS:
            desc = json.loads(d.read_text(encoding="utf-8"))
            results.append(faceplates.sweep(page, base, desc["screen"]["route"], faceplates.expected_devices(desc),
                                            EXPECT_INITIAL, EXPECT_ILK))
        browser.close()
    ok = all(r["ok"] for r in results)
    (out / "faceplates.json").write_text(json.dumps({"ok": ok, "routes": results}, indent=1), encoding="utf-8")
    opened = sum(len(r["opened"]) for r in results)
    expected = sum(r["expected"] for r in results)
    return {"ok": ok, "opened": opened, "expected": expected,
            "faults": [f for r in results for f in r["faults"]],
            "missing": [m for r in results for m in r["missing"]],
            "unexpected": [m for r in results for m in r["unexpected"]]}


def run_project(project: str, out: Path) -> dict:
    base = f"{GATEWAY}/{project}"
    out.mkdir(parents=True, exist_ok=True)
    res = {"project": project, "started": time.strftime("%H:%M:%S"), "trial_page_persists": []}

    def trial(gate: str) -> bool:
        """The trial asked for and a session probed before a gate; False when the trial page stays."""
        t = walk.settle_trial(1200, base)
        res["trial_" + gate] = t
        if not t["settled"]:
            res["trial_page_persists"].append(gate)
        return t["settled"]

    not_run = {"ok": False, "not_run": "a fresh session still showed the trial page"}
    try:
        res["restore_before"] = restore_plant()
        g8 = {}
        if trial("g8"):
            for r in ROUTES:
                v = capture.capture(base, r, out / ("g8" + (r.replace("/", "_") if r != "/" else "_overview")))
                g8[r] = {k: v[k] for k in ("ok", "components", "view_error_badges", "quality_overlays",
                                           "trial_expired", "view_not_found")}
        res["G8"] = {"ok": bool(g8) and all(v["ok"] for v in g8.values()), "routes": g8}
        res["G11"] = g11(base, out) if trial("g11") else {**not_run, "opened": 0, "expected": 0, "faults": [],
                                                          "missing": [], "unexpected": []}
        if trial("g10"):
            # the test login of N-COB-9 signs the commanding session in (COBD-024); without it G10 proves the refusal only
            rep = functional.run(base, out / "functional", restore=restore_plant, login=functional.read_login(),
                                 trends=EXPECT_TRENDS)
            res["G10"] = {"ok": rep["passed"] == rep["checks"], "passed": rep["passed"], "checks": rep["checks"],
                          "failed": [r for r in rep["results"] if not r["ok"]], "signed_in": rep.get("signed_in"),
                          "not_run": rep.get("not_run", "")}
        else:
            res["G10"] = {**not_run, "passed": 0, "checks": 0, "failed": [], "signed_in": False}
        res["restore_after"] = restore_plant()
        if trial("walk"):
            res["walk"] = generated_walk(project, base, out / "walk")
        else:
            res["walk"] = {**not_run, "verdict": "FAIL", "counts": {}, "signed_in": False, "failed": [], "not_run": [],
                           "refused_by": {}, "unrestored": []}
    finally:   # the plant as the next gate and the next rendering expect it, whatever broke
        res["restore_after_walk"] = restore_plant()
        res["plant"] = verify_plant()
    res["finished"] = time.strftime("%H:%M:%S")
    # A walk with nobody signed in walks no write group: with a test login on this machine that is a
    # failure of the suite; without one the suite passes read only, and says so.
    login = functional.read_login() is not None
    res["read_only"] = not login
    res["ok"] = bool(res["G8"]["ok"] and res["G11"]["ok"] and res["G10"]["ok"] and res["walk"]["ok"]
                     and (res["walk"]["signed_in"] or not login) and res["plant"]["ok"]
                     and not res["trial_page_persists"])
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", action="append", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="backslashreplace")   # a row's detail may carry a character the console lacks
    projects = a.project or ["cadre_hmi_wtp", "cadre_hmi_wtpob"]
    out = Path(a.out)
    results = []
    for prj in projects:
        r = run_project(prj, out / prj)
        results.append(r)
        g8 = r["G8"]["routes"]
        print(f"{prj}: G8 {'PASS' if r['G8']['ok'] else 'FAIL'} "
              + " ".join(f"{k}:{v['components']}/{v['quality_overlays']}ov/{v['view_error_badges']}err" for k, v in g8.items()))
        print(f"{prj}: G11 {'PASS' if r['G11']['ok'] else 'FAIL'} {r['G11']['opened']}/{r['G11']['expected']} "
              f"faults {r['G11']['faults'][:6]} missing {r['G11']['missing']} unexpected {r['G11']['unexpected']}")
        print(f"{prj}: G10 {'PASS' if r['G10']['ok'] else 'FAIL'} {r['G10']['passed']}/{r['G10']['checks']} "
              f"{'signed in' if r['G10'].get('signed_in') else 'nobody signed in; not run: ' + r['G10'].get('not_run', '')} "
              + "; ".join(f"{f['id']} {f['detail'][:120]}" for f in r["G10"]["failed"]))
        w = r["walk"]
        print(f"{prj}: WALK {w['verdict']} "
              + " ".join(f"{g}:{c['passed']}/{c['rows']}" for g, c in w["counts"].items())
              + ("" if w["signed_in"] else " nobody signed in: the write groups C, A and P were not walked; not run: "
                 + ", ".join(w["not_run"]))
              + (f" refused by {w['refused_by']}" if w["refused_by"] else "")
              + "".join(f"; {f['id']} {f['detail'][:160]}" for f in w["failed"])
              + (f"; NOT RESTORED {w['unrestored']}" if w["unrestored"] else ""))
        plant = r["plant"]
        print(f"{prj}: PLANT {'RESTORED' if plant['ok'] else 'NOT RESTORED'} {plant['tags']} tags exported, "
              f"{len(plant['differences'])} differ from the tag model {plant['differences'][:4]}; "
              f"{len(plant['extra'])} tags the model does not define")
        if r["trial_page_persists"]:
            print(f"{prj}: TRIAL PAGE PERSISTS before {', '.join(r['trial_page_persists'])}: those gates did not run")
    ok = all(r["ok"] for r in results)
    read_only = any(r["read_only"] for r in results)
    (out / "suite.json").write_text(json.dumps({"ok": ok, "read_only": read_only, "results": results}, indent=1),
                                    encoding="utf-8")
    print("SUITE", "PASS" if ok else "FAIL",
          "(READ ONLY: no test login, so no write group of G10 or of the walk ran)" if read_only else "")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
