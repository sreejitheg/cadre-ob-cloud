"""The alarm chain probe: per priority rank, one alarm raised by a one-tag import, read through the four states of an
alarm (Active Unacked, Active Acked, Cleared Unacked, Cleared Acked) on the alert list, and on the banner of the
device's page and of one other page, then acknowledged and cleared.

Level 2 and Level 5 of the reconstruction exercise did this by hand: a tag import raised a plant alarm, the banner of
the alarm's own page listed it, the banner of a page of another branch did not, and a second import cleared it.
Usage:

    alarm_probe.py --base URL --model F --build DIR --window WxH [--priority [RANKS]] [--dry-run]
                   [--allowed-root [provider]folder ...] [--settle S] --out O

    --base URL        the project's client address, http://host:8088/data/perspective/client/<project>
    --model F         the ASM model (`cadre-hmi-asm-model/1`): the alarms, nodes and pages
    --build DIR       the `bridge/` folder of `asm_descriptors.py` (the descriptors give the plan's pages)
    --priority        run once per priority rank of the model (each rank's first alarm on a Boolean source tag);
                      `--priority high,low` runs those ranks only; without it the rank of the first such alarm is run
    --dry-run         write the plan (per rank the one tag, the page that shows the alarm and the page that does not)
                      and stop: no browser, no gateway, no write
    --allowed-root    a tag folder the raise may write into (default: the model's tag root)

Each rank is run in two passes over its alarm, so all four states are walked: the first raises, acknowledges and clears
(Active Unacked, Active Acked, Cleared Acked); the second raises, clears and acknowledges (Active Unacked, Cleared
Unacked, Cleared Acked). A state is read from the alarm's row on the alert list (`/alerts`, the stock status table: the
words "Active, Unacknowledged" and the like, GF-36); a row that has left the list reads as cleared and acknowledged.
The acknowledgement ticks the alarm's own row and presses Ack selected, signed in with the test login when
`CADRE_TEST_LOGIN` names it (a path; the file is read by the sign-in, never printed). A rank whose alarms are all on
analogue or expression sources is skipped with its reason, and a model with no alarm on a Boolean source tag gives a
document `skipped`, not a fault: the exit code is 0.

The plan (`O/plan.json`) is written before any input. The tags are raised through the walk's lane (`walk_run.Tags` over
ctig's `Gateway` class) and put back whatever happens. The pages are read with a real browser, never written.
Writes `O/probe.json` (`cadre-hmi-alarm-probe/1`): `steps` (as before), `rows` (one per rank, state and pass: rank,
state, pass, alarm, observed, expected, ok) and `ranks` (one per rank: the states it covered, ok or skipped).

Exit codes: 0 the chain held and the tags are back (or the probe was skipped); 2 a step failed or a tag could not be put
back; 1 a fault.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import glass_gates as gg  # noqa: E402
from hmi import provenance  # noqa: E402

TOOL = "tools/compare/alarm_probe.py"
SCHEMA = "cadre-hmi-alarm-probe/1"
RAISE_WAIT_MS = 5000
CLEAR_WAIT_MS = 5000
ACK_WAIT_MS = 1000
POLLS = 12                       # a state is read up to this many times, a second apart (scaled by --settle)
RANK_ORDER = ("critical", "high", "medium", "low", "diagnostic")   # wiki/04 section 8.7
AU, AA, CU, CA = "Active Unacked", "Active Acked", "Cleared Unacked", "Cleared Acked"
STATES = (AU, AA, CU, CA)
WORDS = {AU: "Active, Unacknowledged", AA: "Active, Acknowledged", CU: "Cleared, Unacknowledged",
         CA: "Cleared, Acknowledged"}
# What a state is expected to read as. A cleared and acknowledged event leaves the stock table's states (GF-36), so a row
# that has gone is the same state as a row that reads Cleared, Acknowledged.
EXPECTED = {**WORDS, CA: "Cleared, Acknowledged, or no longer listed"}
PASSES = (("acked_then_cleared", ("raise", "ack", "clear")),
          ("cleared_then_acked", ("raise", "clear", "ack")))
ALERTS = gg.ALERTS_ROUTE

# The rows of the alert list that carry an alarm's description, one entry per row (the widest element of that height):
# the words of the row and its box. Read only.
ROWS_OF = """(desc) => { const t = document.querySelector('[data-component="ia.display.alarmstatustable"]') || document;
  const found = [...t.querySelectorAll('[data-alarm-row], .ia_table__body__row, div, tr')].filter((e) => { const b = e.getBoundingClientRect();
    return b.width > 150 && b.height > 20 && b.height < 40 && e.innerText.includes(desc) && e.innerText.split('\\n').length < 12; });
  const byY = new Map();
  for (const e of found) { const b = e.getBoundingClientRect(), k = Math.round(b.top);
    if (!byY.has(k) || byY.get(k).getBoundingClientRect().width < b.width) byY.set(k, e); }
  return [...byY.values()].sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top)
    .map((e) => { const b = e.getBoundingClientRect();
      return {text: e.innerText.replace(/\\s+/g, ' ').trim(), rect: {x: b.x, y: b.y, w: b.width, h: b.height}}; }); }"""


def classify(text: str | None) -> str | None:
    """The state a row's words give: 'Active' or 'Cleared', 'Unacknowledged' or 'Acknowledged'. None for no row, or for
    words that name no state."""
    if not text:
        return None
    unacked = re.search(r"\bunacknowledged\b", text, re.I)
    acked = re.search(r"\backnowledged\b", text, re.I)
    if not (unacked or acked):
        return None
    cleared = re.search(r"\bcleared?\b", text, re.I)
    return {(False, True): AU, (False, False): AA, (True, True): CU, (True, False): CA}[(bool(cleared), bool(unacked))]


def ranks_of(model: dict) -> list[str]:
    """The priority ranks the model's alarms carry, most severe first; a rank outside the wiki's five follows them."""
    found = list(dict.fromkeys(str(a["priority"]).lower() for a in model.get("alarms", [])))
    return sorted(found, key=lambda r: (RANK_ORDER.index(r) if r in RANK_ORDER else len(RANK_ORDER), r))


def boolean_alarms(model: dict) -> dict[str, dict]:
    """The first alarm of each rank whose condition is one Boolean source tag (`glass_gates.alarm_sources`)."""
    first: dict[str, dict] = {}
    for a in gg.alarm_sources(model, len(model.get("alarms", [])) or 1):
        first.setdefault(str(a["priority"]).lower(), a)
    return first


def probe_plan(model: dict, descriptors: list[dict], base: str, window: tuple[int, int],
               priorities: list[str] | str | None = None) -> dict:
    """The plan: per rank the one alarm, the page of its device (which shows it), one page of another branch (which does
    not). `priorities` is None for the rank of the first Boolean alarm, 'all' for every rank of the model, or a list.
    The plan includes the acknowledgement (the glass gates' `ack` gate) and the two passes that walk the four states.
    A rank without a Boolean alarm, or whose alarm no built page shows, is `skipped` with its reason; a plan with no
    rank to run is `skipped` as a whole (it is not a fault: the probe cannot drive such a model)."""
    plan = gg.plan_of(model, descriptors, base, window, ["alarm", "ack", "banner"], True)
    present, by_rank = ranks_of(model), boolean_alarms(model)
    if priorities is None:
        asked = [str(plan["alarm"]["priority"]).lower()] if plan["alarm"] else present[:1]
    elif priorities == "all":
        asked = present
    else:
        asked = [p.lower() for p in priorities]
        unknown = [p for p in asked if p not in present]
        if unknown:
            raise gg.Fault(f"--priority {unknown[0]!r}: the model's alarms are of priority {', '.join(present) or 'none'}")
    pages = {p["id"]: p for p in model["pages"] if p["built"]}
    ranks: list[dict] = []
    for rank in asked:
        a = by_rank.get(rank)
        if a is None:
            ranks.append({"rank": rank, "skipped": "no alarm of this priority is on a Boolean source tag"})
            continue
        shows_ids, hides_ids = gg.banner_pages(model, a)
        shows = [pages[i]["route"] for i in shows_ids]
        hides = [pages[i]["route"] for i in hides_ids]
        own = next((p["route"] for p in pages.values() if p["id"] == (model["devices"].get(a["device"]) or {}).get("page")), None)
        page = own if own in shows else (shows[0] if shows else None)
        if page is None:
            ranks.append({"rank": rank, "skipped": "no built page shows the alarm's node, so the banner cannot be read"})
            continue
        ranks.append({"rank": rank, "alarm": a, "page": page, "other": hides[0] if hides else None})
    runnable = [r for r in ranks if "alarm" in r]
    first = runnable[0] if runnable else None
    skipped = None
    if first is None:
        skipped = ("the model has no alarm on a Boolean source tag" if not by_rank
                   else "no rank asked has an alarm on a Boolean source tag that a built page shows")
    return {"base": plan["base"], "window": plan["window"], "alarm": first["alarm"] if first else None,
            "page": first["page"] if first else None, "other": first["other"] if first else None,
            "ranks": ranks, "states": list(STATES), "ack": plan["ack"] if runnable else None,
            "passes": [{"name": n, "order": list(o)} for n, o in PASSES], "skipped": skipped}


class Prober:
    """The browser side of the probe: reads an alarm's row on the alert list, ticks it, presses Ack selected."""

    def __init__(self, s, lane, steps: list, rows: list):
        self.s, self.lane, self.steps, self.rows = s, lane, steps, rows

    def rows_of(self, desc: str) -> list[dict]:
        return self.s.p.evaluate(ROWS_OF, desc) or []

    def read(self, desc: str, accept: tuple, fresh: bool = True) -> tuple[str | None, str | None]:
        """Poll the alarm's row on the alert list until its state is one of `accept` (None in `accept` accepts a row that
        has gone), at most POLLS times. Answers the last state read and the row's words."""
        state, text = None, None
        for n in range(POLLS):
            if (fresh and n == 0) or n == POLLS // 2:   # the table refreshes its rows on its own rate: read it in place
                self.s.go(ALERTS, 5000)
            states = [(classify(r["text"]) or "?", r["text"]) for r in self.rows_of(desc)]
            state, text = next((x for x in states if x[0] in accept), None) or (states[0] if states else (None, None))
            if state in accept:
                break
            self.s.wait(1000)
        return state, text

    def row(self, rank: str, a: dict, state: str, pass_name: str, got: str | None, text: str | None, picture=None) -> bool:
        ok = got == state or (state == CA and got is None)
        observed = text if got else "absent"
        self.rows.append({"rank": rank, "state": state, "pass": pass_name, "alarm": a["alarm"], "observed": observed,
                          "expected": EXPECTED[state], "ok": ok, "picture": picture})
        return gg.step(self.steps, f"{rank}: {pass_name}: {state}", EXPECTED[state], observed, ok, picture)

    def acknowledge(self, rank: str, a: dict) -> bool:
        """Tick the alarm's own unacknowledged row and press Ack selected: a mouse click on the row enables the button."""
        s = self.s
        s.go(ALERTS, 6000)
        target = next((r for r in self.rows_of(a["desc"]) if classify(r["text"]) in (AU, CU)), None)
        if target is None:
            return gg.step(self.steps, f"{rank}: acknowledge the alarm", "an unacknowledged row of the alarm to tick",
                           "none", False)
        box = target["rect"]
        s.p.mouse.click(box["x"] + 16, box["y"] + box["h"] / 2)
        s.wait(1500)
        btn = s.custom("Ack selected")
        for _ in range(8):      # the selection reaches the button's store over the socket
            if btn and btn["enabled"]:
                break
            s.wait(1000)
            btn = s.custom("Ack selected")
        if not (btn and btn["enabled"]):
            return gg.step(self.steps, f"{rank}: acknowledge the alarm", "Ack selected enabled by the ticked row",
                           {"button": btn and btn["enabled"], "selected": btn and btn["selected"]}, False)
        s.press_near("Ack selected")
        s.wait(ACK_WAIT_MS)
        return gg.step(self.steps, f"{rank}: acknowledge the alarm", "Ack selected pressed on the ticked row", "pressed", True)

    def write(self, rank: str, a: dict, what: str, value, wait_ms: int) -> bool:
        reply = self.lane.set({a["tag"]: value})
        ok = not reply.get("failed") and not reply.get("missing")
        gg.step(self.steps, f"{rank}: {what} the alarm by a one-tag import", "the gateway takes the import",
                reply.get("failed") or reply.get("missing") or "imported", ok)
        self.s.wait(wait_ms)
        return ok

    def banners(self, rank: str, a: dict, entry: dict, n0: int) -> None:
        """The raised alarm on the banner of its page, absent from the banner of another branch, and counted by the frame."""
        s, text = self.s, self.s.banner_text
        s.go(entry["page"], 5000)
        n1 = s.p.evaluate(gg.ALERT_COUNT)
        shown = a["desc"] in text()
        gg.step(self.steps, f"{rank}: the banner of the alarm's page lists the alarm", a["desc"], "shown" if shown else "absent",
                shown, s.shot(f"probe_{rank}_page"))
        gg.step(self.steps, f"{rank}: the frame's alert count rises", f"above {n0}", n1, n1 > n0)
        if entry["other"]:
            s.go(entry["other"], 5000)
            gone = a["desc"] not in text()
            gg.step(self.steps, f"{rank}: the banner of a page of another branch does not list it", "absent",
                    "absent" if gone else "shown", gone, s.shot(f"probe_{rank}_other"))

    def run_pass(self, rank: str, entry: dict, name: str, order: tuple, covered: dict, first_pass: bool) -> None:
        """One pass over the rank's alarm. The state each action leaves is read from the alert list and recorded as a row."""
        s, a = self.s, entry["alarm"]
        s.go(entry["page"], 5000)
        n0 = s.p.evaluate(gg.ALERT_COUNT)
        if first_pass:
            state, text = self.read(a["desc"], (None,))
            gg.step(self.steps, f"{rank}: before: the alarm is not on the alert list", "absent", text or "absent", state is None)
        active = False
        acked = False
        for action in order:
            if action == "raise":
                self.write(rank, a, "raise", a["raise"], RAISE_WAIT_MS)
                active, acked = True, False
                want = AU
            elif action == "clear":
                self.write(rank, a, "clear", a["clear"], CLEAR_WAIT_MS)
                active = False
                want = CA if acked else CU
            else:
                self.acknowledge(rank, a)
                acked = True
                want = AA if active else CA
            got, text = self.read(a["desc"], (want, None) if want == CA else (want,), fresh=action != "ack")
            ok = self.row(rank, a, want, name, got, text, s.shot(f"probe_{rank}_{name}_{action}"))
            covered[want] = ok and covered.get(want, True)
            if action == "raise" and first_pass:
                self.banners(rank, a, entry, n0)


def run_probe(plan: dict, base: str, window: tuple[int, int], out: Path, settle: float, lane) -> dict:
    from playwright.sync_api import sync_playwright
    steps: list = []
    rows: list = []
    ranks: list = []
    restored, why = True, []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            ctx = browser.new_context(viewport={"width": window[0], "height": window[1]}, has_touch=True)
            page = ctx.new_page()
            s = gg.Session(page, ctx, ctx.new_cdp_session(page), base, window, out / "pictures", settle, plan["base"])
            pr = Prober(s, lane, steps, rows)
            if os.environ.get("CADRE_TEST_LOGIN"):   # the acknowledgement signs in with the test login, when one is named
                s.go(plan["page"], 5000)
                gg.sign_in(s, steps)
            for entry in plan["ranks"]:
                if "alarm" not in entry:
                    ranks.append({"rank": entry["rank"], "skipped": entry["skipped"]})
                    continue
                covered: dict = {}
                try:
                    for n, (name, order) in enumerate(PASSES):
                        pr.run_pass(entry["rank"], entry, name, order, covered, n == 0)
                except Exception as e:   # a rank that could not run is a failed step, with the reason
                    steps.append({"action": f"{entry['rank']}: the probe ran to its end", "expected": "no exception",
                                  "found": f"{type(e).__name__}: {str(e).splitlines()[0][:200]}", "ok": False, "picture": None})
                    try:   # best effort: leave the alarm cleared before the next rank
                        lane.set({entry["alarm"]["tag"]: entry["alarm"]["clear"]})
                    except Exception:
                        pass
                states = {st: bool(covered.get(st)) for st in STATES}
                ranks.append({"rank": entry["rank"], "alarm": entry["alarm"]["alarm"], "tag": entry["alarm"]["tag"],
                              "states": states, "ok": all(states.values())})
        except Exception as e:   # a probe that could not run is a failed step, with the reason
            steps.append({"action": "the probe ran to its end", "expected": "no exception",
                          "found": f"{type(e).__name__}: {str(e).splitlines()[0][:200]}", "ok": False, "picture": None})
        finally:
            lane.restore()
            restored, why = not lane.unrestored, lane.unrestored
            browser.close()
    return {"steps": steps, "rows": rows, "ranks": ranks, "restored": restored, "unrestored": why}


def priorities_of(text: str | None) -> list[str] | str | None:
    if text is None:
        return None
    return "all" if text == "all" else [r.strip() for r in text.split(",") if r.strip()]


def main(argv: list[str] | None = None, *, deploy=None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--build", required=True, metavar="DIR")
    ap.add_argument("--window", default="1920x1080")
    ap.add_argument("--priority", nargs="?", const="all", default=None, metavar="RANKS")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allowed-root", action="append", default=[])
    ap.add_argument("--settle", type=float, default=1.0)
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args_line = sys.argv[1:] if argv is None else list(argv)
    out = Path(a.out)
    try:
        window = gg.parse_window(a.window)
        gg.origin_of(a.base)
        try:
            model = json.loads(Path(a.model).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise gg.Fault(f"--model {a.model}: {e}") from None
        if model.get("schema") != "cadre-hmi-asm-model/1":
            raise gg.Fault(f"--model {a.model} is not a cadre-hmi-asm-model/1 document")
        descriptors = gg.descriptors_of(Path(a.build))
        if not descriptors:
            raise gg.Fault(f"--build {a.build}: no descriptor of cadre-hmi-screen/1")
        plan = probe_plan(model, descriptors, a.base, window, priorities_of(a.priority))
        lane = None
        if not a.dry_run and not plan["skipped"]:
            from walk_run import Tags
            lane = Tags(allowed=a.allowed_root or [model["tag_root"]], deploy=deploy)
            for r in plan["ranks"]:
                if "alarm" in r:
                    lane.check(r["alarm"]["tag"])   # refused here, before any process, outside the allowed roots
    except gg.Fault as e:
        print(f"alarm_probe: {e}")
        return 1
    except Exception as e:   # TagFolderRefused and the like: a refusal, before any input
        print(f"alarm_probe: {type(e).__name__}: {str(e)[:300]}")
        return 1
    out.mkdir(parents=True, exist_ok=True)
    provenance.write_json(out / "plan.json", plan)   # first: before any input
    prov = clock.provenance(TOOL, args_line, [Path(a.model)])
    if plan["skipped"] or a.dry_run:
        doc = {"schema": SCHEMA, "dry_run": a.dry_run, "skipped": plan["skipped"], "plan": plan, "steps": [], "rows": [],
               "ranks": [], "restored": True, "provenance": prov}
        provenance.write_json(out / "probe.json", doc)
        if plan["skipped"]:
            print(f"alarm_probe: skipped, {plan['skipped']}; nothing was written to a gateway")
        else:
            run = [r for r in plan["ranks"] if "alarm" in r]
            print(f"alarm_probe: dry run, the plan is written ({len(run)} rank(s): "
                  + ", ".join(f"{r['rank']} {r['alarm']['tag']} read on {r['page']}" for r in run)
                  + "); nothing was written to a gateway")
        return 0
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        print("alarm_probe: the probe needs Playwright: run under ctig's .venv")
        return 1
    res = run_probe(plan, a.base, window, out, a.settle, lane)
    doc = {"schema": SCHEMA, "dry_run": False, "skipped": None, "plan": plan, "steps": res["steps"], "rows": res["rows"],
           "ranks": res["ranks"], "restored": res["restored"], "unrestored": res["unrestored"], "provenance": prov}
    provenance.write_json(out / "probe.json", doc)
    failed = [x["action"] for x in res["steps"] if not x["ok"]]
    print(f"alarm_probe: ranks {len([r for r in res['ranks'] if 'states' in r])}, steps {len(res['steps'])}, "
          f"failed {len(failed)}, restored {res['restored']}")
    return 0 if not failed and res["restored"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
