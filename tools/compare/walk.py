"""The generated operator walk: gate G10's proof for a project built from data.

`functional.py` walks one plant, the water treatment sample, with its device identifiers and its
scenario in the code. A project generated from descriptors, a device model and a tag model needs the
same proof generated from the same data. This tool writes a plan from those files and the library
profile, then runs it on the gateway.

    plan      pure and offline: the same inputs give the same bytes. A plan (`cadre-hmi-walk/1`) is data
              a person can read and overrule: delete a step, change a value, add an effect.
    run       a session signed in with the test login (NEEDS N-COB-9) and a session with nobody signed
              in walk the plan; every step is a row of `walk.json`.
    selftest  the negative controls: checks that must fail, run against a live project.

Groups of steps:

  N  every route reached as an operator reaches it (the navigation menu's entry, a card's title): the
     top bar reads the page's name, the page shows what belongs on it (a symbol the descriptor places,
     or the chart or the alarm table of a page of the frame), and it renders with no quality overlay
     and no error. A menu step begins on another route.
  D  for each device kind, the first device in document order opens its faceplate from its symbol with
     its identifier, its description and the tabs its members call for.
  T  the trend page draws one card per historised member, and the Trend tab of one device of each
     trended kind draws its series. T runs before C, so that no sample the walk itself wrote draws a line.
  C  for each device kind and each write path of the library profile that one of its devices can use,
     the first such device: the action as an operator does it, what the glass and the tag show
     afterwards, and the action that puts it back. A step never commands the state a device is in: it
     reads the state first and visits every other one, so no step passes without a write.
  R  for each step of C, with nobody signed in: the control is disabled, a crafted client's action
     reaches the gateway, which answers with a refusal, and the tag and the glass are as before.
  A  an alarm raised and cleared without touching the plant's logic (an instrument's limit written
     beyond its value, or an alarm scene of the effects file): it shows in the device's Alarms tab and in
     the frame's list, it is acknowledged, and it leaves nothing behind.
  P  parity: for every symbol parameter bound to a tag the walk can set, two scenes of values, and in
     each the text the symbol shows equals the value under the symbol's own format.

Evidence comes from two places, and each row says which it had: the glass (the text an operator
reads) and the tag (the gateway's export of the tag: a memory tag's value, a reference tag followed to
its source; an expression tag's value cannot be read that way). The control a step operated is
recorded too and is never enough: a step whose only evidence is the field it typed into, or the
button it found disabled, fails. What the walk must know of the glass (captions, row labels, tab
names, state texts) is the glass table of `walk_plan.py`; `tests/test_walk.py` pins every entry against
the views the generator's code writes and against the generator's own tables. Wiki page 08 section 9
is the manual.

The code is in three modules: `walk_plan.py` (the plan, pure and offline), `walk_run.py` (the runner,
the tags and the negative controls) and this one, the command line, which exports the names of both.

Usage (plan: any Python; run and selftest: ctig's .venv for Playwright):
    python tools/compare/walk.py plan --descriptor screens/wtp/overview.json [--descriptor ...]
        [--devices-file f] [--tags-file f] [--source-tags f[@parent/folder]]
        [--source-folder [provider]folder] [--effects f] [--render stock|module] [--profile f] [--trip]
        --out plan.json
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/walk.py run
        --plan plan.json --base http://localhost:8088/data/perspective/client/cadre_hmi_x --out folder
        [--trial seconds] [--no-login]
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/walk.py selftest
        --plan plan.json --base ... --out folder [--trial seconds]
Exit 1 when any step fails, a test login does not sign in or a tag is left unrestored (run), or any
negative control passes where it must fail (selftest). A run with nobody signed in ends `PASS, READ
ONLY`: the write groups C, A and P did not run, which is no pass of them.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# The plan and the runner live in two modules (`walk_plan.py`, pure and offline; `walk_run.py`, the
# gateway and the browser). This module is the command line, and exports every name of both, so that
# `walk.build_plan`, `walk.run`, `walk.Tags` and the rest stay where callers and tests look for them.
import walk_plan  # noqa: E402
import walk_run  # noqa: E402
from walk_plan import *  # noqa: E402,F401,F403
from walk_plan import _generator, _PATTERN  # noqa: E402,F401
from walk_run import *  # noqa: E402,F401,F403


# ---------------------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------------------
def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 epilog="Exit 0 on PASS (and on PASS, READ ONLY where --no-login asked for it), "
                                        "1 on any failed step, on a login that did not sign in, or on a negative "
                                        "control that did not fail.")
    sub = ap.add_subparsers(dest="command", required=True)
    pl = sub.add_parser("plan", help="write a plan from the descriptors and their models (offline)")
    pl.add_argument("--descriptor", action="append", required=True, metavar="FILE",
                    help="a screen descriptor (cadre-hmi-screen/1); repeat for each page, in the order of the build")
    pl.add_argument("--devices-file", default=None, metavar="FILE",
                    help="the device model (cadre-hmi-devices/1) the project was built with; without one the devices "
                         "are those the descriptors' symbols name, with the members their tag folders carry")
    pl.add_argument("--tags-file", default=None, metavar="FILE",
                    help="the tag model, a folder document lying at the provider's root; without one, the tags the "
                         "generator would create for the descriptors")
    pl.add_argument("--source-tags", action="append", default=[], metavar="FILE[@parent/folder]",
                    help="a tag document that defines the sources of reference tags, as FILE or FILE@parent/folder "
                         "when its root folder lies below the provider's root; repeatable; fills in only the tags "
                         "the tag model lacks")
    pl.add_argument("--source-folder", action="append", default=[], metavar="[provider]folder",
                    help="a folder outside the descriptors' tag root that the walk may import into, for the source "
                         "tags a device layer of reference tags stands on; repeatable; recorded in the plan as "
                         "sourceFolders; without it a reading or a step whose tag lies there is listed as not "
                         "checked or not reached")
    pl.add_argument("--effects", default=None, metavar="FILE",
                    help="the effects file (cadre-hmi-walk-effects/1): what only the plant decides")
    pl.add_argument("--render", choices=["stock", "module"], default="stock",
                    help="the rendering the project was built with (screen.py --render); default stock")
    pl.add_argument("--profile", default=None, metavar="FILE", help="the library profile (default library/profile.json)")
    pl.add_argument("--faceplate", choices=["openbridge", "asm"], default="openbridge",
                    help="the project's default faceplate style (screen.py --faceplate); default openbridge")
    pl.add_argument("--trip", action="store_true",
                    help="plan a trip (write path W11) for each device kind with interlocks: a latched trip raised "
                         "from its memory source tag, read on the Interlocks tab, put back and reset (COB-204)")
    pl.add_argument("--out", required=True, metavar="FILE", help="the plan to write (cadre-hmi-walk/1)")
    for name, text in (("run", "walk a plan on the gateway"), ("selftest", "the negative controls, on the gateway")):
        rn = sub.add_parser(name, help=text)
        rn.add_argument("--plan", required=True, metavar="FILE", help="a plan written by `plan`")
        rn.add_argument("--base", required=True, metavar="URL",
                        help="the project's client address, http://host:8088/data/perspective/client/<project>")
        rn.add_argument("--out", required=True, metavar="FOLDER",
                        help="where walk.json (run) or selftest.json (selftest) and the failure screenshots go")
        rn.add_argument("--trial", type=int, default=1200, metavar="SECONDS",
                        help="seconds of trial the run needs; with fewer left it waits for the expiry and resets "
                             "(GF-33); default 1200")
        if name == "run":
            rn.add_argument("--no-login", action="store_true",
                            help="walk with nobody signed in although a test login exists: N, D, T and R only, "
                                 "verdict PASS, READ ONLY")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="backslashreplace")   # a console page without the setpoint mark still prints
    if a.command == "plan":
        effects = _load(a.effects) if a.effects else None
        bad = effects_errors(effects) if effects else []
        if bad:
            print("\n".join(bad))
            return 1
        sources = []
        for item in a.source_tags:
            f, _, parent = item.partition("@")
            sources.append((_load(f), parent))
        try:
            source_folders_of(a.source_folder)
        except ValueError as e:
            print(e)
            return 1
        plan = build_plan([_load(d) for d in a.descriptor],
                          devices=_load(a.devices_file) if a.devices_file else None,
                          tags=_load(a.tags_file) if a.tags_file else None, effects=effects, source_tags=sources,
                          render=a.render, profile=load_profile(Path(a.profile)) if a.profile else None,
                          source_folders=a.source_folder, faceplate=a.faceplate, trip=a.trip,
                          names={"descriptors": [Path(d).name for d in a.descriptor],
                                 "devices": Path(a.devices_file).name if a.devices_file else None,
                                 "tags": Path(a.tags_file).name if a.tags_file else None,
                                 "sourceTags": [Path(s.partition("@")[0]).name for s in a.source_tags],
                                 "effects": Path(a.effects).name if a.effects else None})
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(plan_text(plan), encoding="utf-8", newline="\n")
        print("PLAN", " ".join(f"{g}:{n}" for g, n in plan["counts"].items()),
              f"parity {plan['parity']['checked']} checked, {len(plan['parity']['notChecked'])} not checked;",
              f"not reached {[n.get('path') or n.get('device') or n.get('scene') for n in plan['notReached']]}"
              + (f"; source folders {plan['sourceFolders']}" if plan["sourceFolders"] else "")
              + (f"; no Trend tab for {plan['trendTabAbsent']}" if plan.get("trendTabAbsent") else ""))
        return 0
    import glass
    plan = _load(a.plan)
    trial = settle_trial(a.trial, a.base)
    print("trial", trial)
    if not trial["settled"]:
        print("WALK FAIL: a fresh session still shows the trial page; nothing was walked")
        return 1
    login = None if getattr(a, "no_login", False) else glass.read_login()
    if a.command == "selftest":
        rep = selftest(plan, a.base, Path(a.out), login)
        for c in rep["controls"]:
            print(f"control {c['control']:14s} {'NOT APPLICABLE ' if c['ok'] is None else 'FAILS AS IT MUST' if c['ok'] else 'DID NOT FAIL    '}  "
                  + json.dumps({k: v for k, v in c.items() if k not in ('control', 'ok', 'glass')})[:300])
        print("SELFTEST", "PASS" if rep["ok"] else "FAIL", rep.get("note", ""),
              f"unrestored {rep['unrestored']}" if rep.get("unrestored") else "")
        return 0 if rep["ok"] else 1
    rep = run(plan, a.base, Path(a.out), login)
    for r in rep["rows"]:
        print(f"{r['id']:8s} {'PASS' if r['ok'] else 'FAIL'}  {r['path'] or '':4s} {r['device']:10s} {r['done'][:70]}  "
              f"[{r['evidence']}] {r['detail'][:200]}")
    print("WALK", rep["verdict"], " ".join(
        f"{g}:{c['passed']}/{c['rows']}" for g, c in rep["counts"].items()), rep["note"],
        f"; steps not run: {', '.join(rep['not_run'])}" if rep["not_run"] else "",
        f"; STEPS OF THE PLAN WITHOUT A ROW {rep['missing']}" if rep["missing"] else "",
        f"; refused by {rep['refused_by']}" if rep["refused_by"] else "",
        f"; NOT RESTORED {rep['unrestored']}" if rep["unrestored"] else "")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
