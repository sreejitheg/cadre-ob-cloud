"""The runner of the generated operator walk: a plan walked on the gateway (`walk.py run`), and the
negative controls (`walk.py selftest`).

`Tags` is the REST side (the gateway's export of a tag as evidence, a scene imported as whole tag
definitions, every restore read back); `Walk` holds the two sessions and one method for each type of
step; `summarise` writes the result (`cadre-hmi-walk-result/1`); `settle_trial` waits until a session
shows the project and not the trial page. The rules of evidence are in the methods' docstrings and in
wiki page 08 section 9.4.

Runs under an interpreter with Playwright (ctig's `.venv`), as the other gateway gates do. `walk.py`
is the command line and exports every name of this module; `walk_plan.py` writes the plan.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from walk_plan import (CANCEL, CONFIRM, SET, EMPTY_FACEPLATE, GROUPS, MESSAGE_REFUSED, QUALITY_LINE, REFUSED, RESULT_SCHEMA, UNACKED_ROW,
                       WAIT_FLOOR, decimals_of, expect_of, number_format, split_path)


# ---------------------------------------------------------------------------------------
# The gateway's side: tags read and written through the REST lane
# ---------------------------------------------------------------------------------------
class TagFolderRefused(ValueError):
    """An import the walk refuses: its tag lies outside the folders the plan allows."""


def import_failed(reply) -> str:
    """Why an import's reply is not a success ('' when it is): the gateway answers
    `{"successCount", "failureCount", "failures"}`."""
    if not isinstance(reply, dict):
        return f"the reply was {reply!r}"
    if reply.get("failureCount"):
        return f"{reply['failureCount']} failures: {str(reply.get('failures'))[:200]}"
    return "" if reply.get("successCount") else "the gateway counted no tag imported"


class Tags:
    """The tag evidence and the scenes. A tag's value is the gateway's export of the tag
    (`deploy.export_tags`): a memory tag exports its live value, a reference tag is followed to its
    source, and an expression tag exports no value, so its evidence is the glass alone. A scene is
    imported as whole tag definitions (an import replaces a listed tag whole and leaves its siblings,
    GF-55), built from the definition the gateway exported before.

    `allowed` names the folders an import may touch (the plan's `tagRoot` and the source folders its
    caller named, `allowed_folders`): a reference chain or an effects file that leads elsewhere is
    refused here, by the code, whatever the steps of the plan say. A read that
    fails (anything but a tag the gateway does not carry, which exports as `tagType` Unknown, GF-25) is
    kept in `errors`: the runner fails the step it happened in, since a gateway that cannot be read
    is no evidence, not a tag without a value."""

    def __init__(self, allowed: list[str] | None = None, deploy=None):
        if deploy is None:
            from hmi import deploy
        self.deploy = deploy
        self.allowed = [split_path(a) for a in (allowed or []) if a and split_path(a)[1]]
        self.before: dict[str, dict] = {}   # the definitions exported before the walk first changed a tag
        self.errors: list[dict] = []        # reads the gateway failed
        self.unrestored: list[dict] = []    # definitions of before that could not be imported back, or did not hold

    def check(self, path: str) -> None:
        """Refuse a tag outside the allowed folders."""
        prov, rel = split_path(path)
        if not any(prov == p and (rel == r or rel.startswith(r + "/")) for p, r in self.allowed):
            raise TagFolderRefused(f"{path} lies outside the folders this walk may import into "
                                   f"({', '.join(f'[{p}]{r}' for p, r in self.allowed) or 'none'})")

    def node(self, path: str) -> dict | None:
        prov, rel = split_path(path)
        try:
            n = self.deploy.export_tags(prov, rel)
        except Exception as e:   # the gateway could not be read: kept, and the step fails on it
            self.errors.append({"tag": path, "error": f"{type(e).__name__}: {str(e)[:160]}"})
            return None
        if not isinstance(n, dict) or not n.get("name") or n.get("tagType") == "Unknown":
            return None          # a tag the gateway does not carry: no evidence, said as such
        return n

    def source(self, path: str) -> tuple[str, dict | None]:
        """The tag at the end of a reference chain, and its exported definition."""
        prov, rel = split_path(path)
        for _ in range(8):
            n = self.node(f"[{prov}]{rel}")
            if not n or n.get("valueSource") != "reference" or not isinstance(n.get("sourceTagPath"), str):
                return f"[{prov}]{rel}", n
            target = n["sourceTagPath"]
            if target.startswith("[.]"):
                parts = rel.split("/")[:-1]
                for seg in target[3:].split("/"):
                    parts = parts[:-1] if seg == ".." else parts + ([seg] if seg else [])
                rel = "/".join(parts)
            else:
                prov, rel = split_path(target)
        return f"[{prov}]{rel}", None

    def value(self, path: str):
        """(readable, value): the value a tag holds, where the export states one."""
        _end, n = self.source(path)
        if n is None or n.get("valueSource", "memory") != "memory" or "value" not in n:
            return False, None
        return True, n["value"]

    def set(self, values: dict[str, object]) -> dict:
        """Import a scene: each tag's exported definition with the scene's value, in one document for
        each top folder. The definitions of before are kept for `restore`. `failed` lists the imports
        the gateway did not count as made."""
        docs: dict[tuple[str, str], dict] = {}
        missing = []
        for path, value in values.items():
            end, n = self.source(path)
            if n is None or n.get("valueSource", "memory") != "memory":
                missing.append(path)
                continue
            self.check(end)
            self.before.setdefault(end, json.loads(json.dumps(n)))
            prov, rel = split_path(end)
            parts = rel.split("/")
            doc = docs.setdefault((prov, parts[0]), {"name": parts[0], "tagType": "Folder", "tags": []})
            for seg in parts[1:-1]:
                nxt = next((t for t in doc["tags"] if t["name"] == seg and t.get("tagType") == "Folder"), None)
                if nxt is None:
                    nxt = {"name": seg, "tagType": "Folder", "tags": []}
                    doc["tags"].append(nxt)
                doc = nxt
            doc["tags"].append({**n, "value": value})
        replies = [self.deploy.import_tags(prov, "", doc) for (prov, _top), doc in sorted(docs.items())]
        failed = [f for f in (import_failed(r) for r in replies) if f]
        return {"imported": len(values) - len(missing), "missing": missing, "replies": replies, "failed": failed}

    def keep(self, path: str) -> str:
        """Keep the definition a tag has now, for `restore`, without changing it. Answers the end of
        the tag's reference chain."""
        end, n = self.source(path)
        if n is not None:
            self.check(end)
            self.before.setdefault(end, json.loads(json.dumps(n)))
        return end

    def put(self, path: str, node: dict) -> dict:
        """Import one whole tag definition at its place (an alarm scene's document). Refused where the
        document's name is not the tag's: it would be imported beside the tag, and stay."""
        end, n = self.source(path)
        self.check(end)
        prov, rel = split_path(end)
        if node.get("name") != rel.split("/")[-1]:
            raise TagFolderRefused(f"the document names {node.get('name')!r}, the tag is {end}")
        if n is not None:
            self.before.setdefault(end, json.loads(json.dumps(n)))
        reply = self.deploy.import_tags(prov, "/".join(rel.split("/")[:-1]), node)
        why = import_failed(reply)
        if why:
            raise RuntimeError(f"the import on {end} failed: {why}")
        return reply

    def restore(self, paths: list[str] | None = None) -> list[str]:
        """Import back the definitions of before, for `paths` or for every tag the walk changed, and
        read each back: a definition leaves `before` only once the gateway's export equals it. What
        could not be imported, or did not hold, is listed in `unrestored` and stays in `before`, so a
        later restore tries it again."""
        done = []
        for end in list(self.before):
            if paths is not None and end not in paths:
                continue
            want = self.before[end]
            prov, rel = split_path(end)
            try:
                self.check(end)
                why = import_failed(self.deploy.import_tags(prov, "/".join(rel.split("/")[:-1]), want))
                if not why:
                    got = self.node(end)
                    why = "" if not differing(want, got) else f"the export after the import differs on {differing(want, got)}"
            except Exception as e:   # the next definition is still tried
                why = f"{type(e).__name__}: {str(e)[:160]}"
            self.unrestored = [u for u in self.unrestored if u["tag"] != end]
            if why:
                self.unrestored.append({"tag": end, "why": why})
                continue
            del self.before[end]
            done.append(end)
        return done


def allowed_folders(plan: dict) -> list[str]:
    """The folders a walk of this plan may import into: the plan's `tagRoot` and exactly the source
    folders its caller named (`sourceFolders`, `walk.py plan --source-folder`). Nothing else: not a
    folder a reference chain leads to, not one an effects file names."""
    return [plan.get("tagRoot", ""), *plan.get("sourceFolders", [])]


def differing(want: dict, got: dict | None) -> list[str]:
    """The keys on which an exported definition differs from the one imported ([] when none does)."""
    if not isinstance(got, dict):
        return ["the tag did not export"]
    return sorted(k for k in set(want) | set(got) if not same(want.get(k), got.get(k)))


def line_number(fmt, line: str) -> float | None:
    """The number a line of a symbol carries, when the line has the shape of a format (its prefix, a
    number, its suffix); None when it has not."""
    prefix, _pattern, suffix = fmt
    m = re.fullmatch(re.escape(prefix.strip()) + r"\s*(-?[\d,]*\.?\d+)\s*" + re.escape(suffix.strip()), line)
    return float(m.group(1).replace(",", "")) if m else None


def same(a, b, tolerance: float = 1e-6) -> bool:
    """Two tag values agree: Booleans exactly, two integers exactly, other numbers within a relative
    tolerance (a Float4 is not exact). Integers are never compared with a tolerance: two time stamps
    in milliseconds a few minutes apart differ by less than a millionth of their size, and the walk
    took them for the same value (2026-10-11, the stamp a pulse leaves)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, int) and isinstance(b, int):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tolerance * max(1.0, abs(float(a)), abs(float(b)))
    return a == b


# ---------------------------------------------------------------------------------------
# The trial, as a session sees it
# ---------------------------------------------------------------------------------------
TRIAL_TEXT = "Trial Expired"


def trial_page_shown(base: str) -> bool:
    """Whether a fresh session on the project shows the gateway's trial page."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
            page.goto(base.rstrip("/") + "/", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            return TRIAL_TEXT in page.inner_text("body")
        finally:
            browser.close()


def settle_trial(seconds: int, base: str, ensure=None, probe=trial_page_shown, sleep=time.sleep,
                 tries: int = 12, pause: float = 15.0, rounds: int = 2) -> dict:
    """`deploy.ensure_trial(seconds)`, then a fresh session probed until it no longer shows the trial
    page. The REST route is not what a session sees: on 2026-10-11 the route reported a healthy trial
    straight after a reset (7,199 s left) while every new session showed "Trial Expired" for about a
    minute more, and gate G8 measured that page as six routes with no component. So a gate begins only
    once a session shows the project: up to `tries` probes `pause` seconds apart, then the trial asked
    for again, `rounds` times in all. The answer carries `session_probes` and `settled`; a caller must
    fail on `settled` false, and never take the trial page for a page of the project."""
    if ensure is None:
        from hmi import deploy
        ensure = deploy.ensure_trial
    out, probes = {}, 0
    for _ in range(rounds):
        out = dict(ensure(seconds))
        for _n in range(tries):
            probes += 1
            if not probe(base):
                return {**out, "session_probes": probes, "settled": True}
            sleep(pause)
    return {**out, "session_probes": probes, "settled": False}


# ---------------------------------------------------------------------------------------
# The runner
# ---------------------------------------------------------------------------------------
class Walk:
    """One run of a plan: the two sessions, the rows, and one method for each type of step."""

    def __init__(self, plan: dict, base: str, out: Path, signed, anon, tags: Tags, signed_in: bool):
        import glass
        self.g = glass
        self.plan, self.base, self.out = plan, base.rstrip("/"), out
        self.signed, self.anon, self.tags, self.signed_in = signed, anon, tags, signed_in
        self.module = plan.get("render") == "module"
        self.rows: list[dict] = []
        self.during = {s["during"]: s for s in plan["steps"] if s.get("during")}
        self.skip_write = False      # negative control: a capability step that writes nothing
        self.no_crafted = False      # negative control: a refusal step in a session that may write
        self.force_crafted = False   # negative control: the crafted action made on a control that is enabled
        self.before_step = None      # a caller's hook, called with each step before it runs (`run`)
        # the rows this walk had the gateway refuse, by session and device: a row keeps "Refused" until
        # its next accepted write, so these may read it when a later step opens the device again
        self.refused: dict[tuple[int, str], set[str]] = {}
        self.restored: list[str] = []

    # -- bookkeeping ------------------------------------------------------------------
    def row(self, step: dict, done: str, expected: str, glass_seen, tag_seen, ok: bool, evidence: set,
            detail: str = "", page=None, sid: str | None = None, extra: dict | None = None) -> dict:
        kinds = [k for k in ("glass", "control", "tag") if k in evidence]
        r = {"id": sid or step["id"], "group": step["group"], "path": step.get("path") or step.get("ack"),
             "device": step.get("device", ""),
             "done": done, "expected": expected, "glass": glass_seen, "tag": tag_seen,
             "evidence": " and ".join(kinds) if kinds else "none", "ok": bool(ok), "detail": detail, **(extra or {})}
        if not ok and page is not None:
            shot = self.out / f"{r['id'].replace('.', '_')}.png"
            try:
                page.screenshot(path=str(shot))
                r["screenshot"] = shot.name
            except Exception as e:   # recorded, never hidden
                r["screenshot"] = f"not taken: {type(e).__name__}"
        self.rows.append(r)
        return r

    def page_for(self, step: dict):
        if step.get("session") == "anonymous":
            return self.anon
        return self.signed if self.signed_in else self.anon

    def at(self, page) -> str:
        """The route a page shows, as the plan writes routes."""
        if not page.url.startswith(self.base):
            return ""
        return "/" + page.url[len(self.base):].split("?")[0].strip("/")

    def goto(self, page, route: str, fresh: bool = False) -> None:
        """Show a route. A page already on it is kept, with its session and its faceplate."""
        url = self.base + route
        if fresh or page.url.rstrip("/") != url.rstrip("/"):
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(4000)

    def wait(self, page, check, seconds: float = 8.0, step_ms: int = 500):
        """Poll `check` (which answers (ok, seen)) until it holds or the time is up."""
        deadline = time.time() + seconds
        ok, seen = check()
        while not ok and time.time() < deadline:
            page.wait_for_timeout(step_ms)
            ok, seen = check()
        return ok, seen

    def open(self, page, step: dict, tab: str | None = None):
        """The step's device open on its page, on the tab named: (dock, why not)."""
        self.goto(page, step["route"])
        right = self.g.open_faceplate(page, step["find"], step["device"])
        if right is None:
            return None, f"no faceplate opened on {step['device']} from the symbol showing {step['find']!r}"
        if tab and not self.g.tab(right, tab):
            return None, f"the faceplate shows no {tab} tab (tabs {self.g.tabs_shown(right)})"
        return right, ""

    def reopen(self, page, step: dict):
        """The step's device opened again by way of another device of the plan, on the same page where
        there is one: (dock, why not)."""
        others = [d for d in self.plan.get("devices", []) if d.get("find") and d["title"] != step["device"]]
        other = next((d for d in others if d["route"] == step["route"]), others[0] if others else None)
        if other is None:
            return None, "the plan has no other device to show in the faceplate, so an earlier refusal could not be cleared"
        _dock, why = self.open(page, {"route": other["route"], "find": other["find"], "device": other["title"]})
        if why:
            return None, why
        self.refused = {k: v for k, v in self.refused.items() if k[0] != id(page)}
        return self.open(page, step, step["tab"])

    def stale(self, page, step: dict) -> list[str]:
        """The faults of a faceplate that shows "Refused" before the step acts: a row keeps the word
        until its next accepted write, so a row that reads it without this walk having had it refused
        on this device, in this session, carried it over from another device (the library defect the
        walk found on 2026-10-11, since fixed) or from another client."""
        mine = self.refused.get((id(page), step.get("device", "")), set())
        rows = [r for r in self.g.refused_rows(page) if r not in mine]
        return [f"the faceplate read {REFUSED!r} on {', '.join(rows)} before the step acted"] if rows else []

    def read(self, page, reading: dict, expect: dict) -> tuple[bool, str]:
        """One symbol against what a rule expects of it: (agrees, what the glass shows)."""
        s = self.g.find_symbol(page, reading["find"])
        if s is None:
            return False, f"no symbol shows {reading['find']!r}"
        if "module" in expect:
            got = s.get({"frame": "frame"}.get(expect["module"], expect["module"]))
            want = expect["value"]
            if isinstance(want, bool) or got is None or isinstance(got, bool):
                return got is not None and bool(got) == bool(want), f"{expect['module']} {got}"
            # the element's property is the tag's value as bound, not a formatted text: it agrees to
            # the precision of a Float4, which is finer than any format's rounding
            return same(float(got), float(want)), f"{expect['module']} {got}"
        if "frame" in expect:
            return s["frame"] is not None and s["frame"] == expect["frame"], f"alert frame {'drawn' if s['frame'] else 'not drawn'}"
        if "icon" in expect:
            want = self.g.badge_icon(expect["icon"])
            names = [n for n in ("auto", "manual") if self.g.badge_icon(n) in s["icons"]]
            return want in s["icons"], f"badge {names or s['icons']}"
        shown = " | ".join(s["lines"])
        if "line" in expect:
            return expect["line"] in s["lines"], shown
        if "pattern" in expect:
            return any(re.search(expect["pattern"], ln) for ln in s["lines"]), shown
        return False, shown

    def shown(self, page, e: dict):
        """What a reading that is compared with itself shows now. None without the symbol.

        With a rule (an effect that `leaves`): the member's own reading on its symbol, and nothing
        else of it, so that another line of the symbol that moves does not count for the member (on
        2026-10-11 a sequence block's step number changed one scan before its text, and the walk took
        the block's change for the text's; an analogue line beside it would have met the effect by
        noise). A line is found by the prefix and suffix of its format, a state by its two texts, a
        text by being neither a line the symbol draws from its parameters nor another parameter's
        line; a module component by the property bound. Without a rule (the `rest` of a pulse's
        refusal): everything the symbol shows, since nothing of the block may move there."""
        s = self.g.find_symbol(page, e["find"])
        if s is None:
            return None
        rule = e.get("rule")
        if rule is None:
            return [s.get(k) for k in ("on", "speed", "value", "frame")] if s["module"] else list(s["lines"])
        how = rule["how"]
        if how == "module":
            return [s.get(rule["prop"])]
        if how == "frame":
            return [s["frame"]]
        if how == "icon":
            both = [self.g.badge_icon(rule[k]) for k in ("on", "off")]
            return sorted(i for i in s["icons"] if i in both)
        if how == "line":
            return [ln for ln in s["lines"] if line_number(rule["format"], ln) is not None]
        if how == "state":
            texts = [x["line"] for x in (rule["on"], rule["off"]) if "line" in x]
            patterns = [x["pattern"] for x in (rule["on"], rule["off"]) if "pattern" in x]
            return [ln for ln in s["lines"] if ln in texts or any(re.search(p, ln) for p in patterns)]
        fixed = e.get("fixed", [])
        return [ln for ln in s["lines"] if ln not in fixed
                and not any(line_number(f, ln) is not None for f in e.get("others", []))]

    def read_effect(self, page, e: dict, written=None) -> tuple[bool, str]:
        """An effect of the effects file on the symbol that shows its member."""
        rule = e["rule"]
        if "min" in e or "max" in e:
            s = self.g.find_symbol(page, e["find"])
            if s is None:
                return False, f"no symbol shows {e['find']!r}"
            if s["module"]:
                got = s.get(rule.get("prop", ""))
            else:
                got = next((n for n in (line_number(rule["format"] if rule["how"] == "line" else ("", "", ""), ln)
                                        for ln in s["lines"]) if n is not None), None)
            ok = got is not None and (e.get("min") is None or got >= e["min"]) and (e.get("max") is None or got <= e["max"])
            return ok, f"{e['member']} reads {got}"
        value = written if e.get("written") else e.get("value")
        try:
            ok, seen = self.read(page, e, expect_of(rule, value))
        except ValueError as ex:
            return False, str(ex)
        return ok, f"{e['member']}: {seen}"

    def effects_before(self, page, effects: list[dict]) -> dict[int, object]:
        """What the effects that are compared with before read now, taken before the action: the tag
        of one that `changes` (readable, value), the member's own reading of one that `leaves`."""
        out: dict[int, object] = {}
        for i, e in enumerate(effects):
            if e.get("changes"):
                out[i] = self.tags.value(e["tag"])
            elif e.get("leaves"):
                out[i] = self.shown(page, e)
        return out

    def unreadable(self, effects: list[dict], before: dict[int, object]) -> list[str]:
        """Why an effect that is compared with before cannot be judged: nothing was read before."""
        out = []
        for i, b in before.items():
            if effects[i].get("changes") and not b[0]:
                out.append(f"{effects[i]['member']} could not be read before the action")
            elif effects[i].get("leaves") and b is None:
                out.append(f"no symbol shows {effects[i]['find']!r} before the action")
        return out

    def effect(self, page, e: dict, before=None, written=None) -> tuple[bool, str, str]:
        """One effect now: (met, what was seen, `tag` or `glass`, the evidence it is). An effect that
        `changes` is read on the member's tag against the value of before; one that `leaves` on the
        member's own reading against the reading of before; any other on the symbol against the value
        the effects file states."""
        if e.get("changes"):
            readable, held = before if before is not None else (False, None)
            r, v = self.tags.value(e["tag"])
            if not readable or not r:
                return False, f"{e['member']} could not be read", "tag"
            if same(v, held):
                return False, f"{e['member']} holds {v} as before", "tag"
            return True, f"{e['member']} went from {held} to {v}", "tag"
        if e.get("leaves"):
            now = self.shown(page, e)
            if before is None or now is None:
                return False, f"no symbol shows {e['find']!r}", "glass"
            was = " | ".join(map(str, before))
            if now == before:
                return False, f"{e['symbol']}.{e['param']} reads {was!r} as before", "glass"
            return True, f"{e['symbol']}.{e['param']} went from {was!r} to {' | '.join(map(str, now))!r}", "glass"
        ok, seen = self.read_effect(page, e, written)
        return ok, seen, "glass"

    # -- N and D ----------------------------------------------------------------------
    def route(self, step: dict) -> None:
        """A route reached as an operator reaches it. The address alone proves little (the frame
        renders around a blank view), and the top bar's page name is computed from the route, so it
        proves no more: the page must show what belongs on it. Where the descriptor places a symbol
        that shows a text, that symbol must be on the page (`symbol`); a page of the frame, which
        carries none, must hold the component the plan names for it (`holds`: the alarm status table
        of the alerts page, a chart of the trend page); and every page must hold components outside
        the docks. A menu step begins on another route, so that it cannot pass without the entry
        having moved the page. A page with neither `symbol` nor `holds` (a descriptor none of whose
        symbols shows a text) is proven by its address and its component count alone."""
        page = self.page_for(step)
        want = "/" + step["route"].strip("/")
        problems = []
        if step["via"] == "card":
            self.goto(page, step["from"])
            self.g.close_faceplate(page)
            started = self.at(page)
            moved = self.g.click_card_title(page, step["label"])
            done = f"the title of the card {step['label']} on {step['from']}"
        else:
            if self.at(page) in ("", want) and step.get("from"):
                self.goto(page, step["from"])
            elif self.at(page) == "":
                self.goto(page, "/alerts" if want != "/alerts" else "/")
            started = self.at(page)
            self.g.close_faceplate(page)
            moved = self.g.navigate_by_menu(page, step["label"])
            done = f"the navigation menu's entry {step['label']}, from {started}"
        if started == want:
            problems.append("the step began on the route itself, so the entry moved nothing")
        if not moved:
            problems.append("the entry was not found")
        page.wait_for_timeout(2500)
        at = self.at(page)
        if at != want:
            problems.append(f"the address is {at}")
        faults = self.g.page_faults(page)
        seen = {"at": at, "components outside the docks": faults["page_components"], "overlays": faults["overlays"],
                "error badges": faults["badges"]}
        if "title" in step:
            ok, name = self.wait(page, lambda: (self.g.page_name(page) == step["title"], self.g.page_name(page)), 5)
            seen["top bar"] = name
            if not ok:
                problems.append(f"the top bar reads {name!r}, the page is {step['title']!r}")
        if step.get("symbol"):
            ok, _s = self.wait(page, lambda: (self.g.find_symbol(page, step["symbol"]) is not None, None), 6)
            seen["symbol"] = f"{step['symbol']!r} {'shown' if ok else 'not shown'}"
            if not ok:
                problems.append(f"no symbol of the page shows {step['symbol']!r}, which the descriptor places on it")
        held = step.get("holds")
        if held:
            ok, count = self.wait(page, lambda: (self.g.page_holds(page, held["component"]) > 0,
                                                 self.g.page_holds(page, held["component"])), 6)
            seen[held["what"]] = count
            if not ok:
                problems.append(f"the page holds no {held['component']} ({held['what']}), which belongs on {step['route']}")
        if not faults["page_components"]:
            problems.append("the page holds no component outside the docks")
        if not self.g.clean(faults):
            problems.append("the page is not clean" + (": View Not Found" if faults["not_found"] else "")
                            + (": Trial Expired" if faults["trial"] else ""))
        expected = (f"the page {step['route']}" + (f", named {step['title']!r} in the top bar" if "title" in step else "")
                    + (f", showing the symbol {step['symbol']!r}" if step.get("symbol") else "")
                    + (f", holding {held['what']}" if held else "")
                    + ", components outside the docks, no quality overlay, no error")
        self.row(step, done, expected, seen, None, not problems, {"glass"}, "; ".join(problems), page)

    def open_step(self, step: dict) -> None:
        page = self.page_for(step)
        right, why = self.open(page, step)
        if right is None:
            self.row(step, "a click on its symbol", "its faceplate", why, None, False, {"glass"}, why, page)
            return
        title, label = self.g.dock_header(page)
        tabs = self.g.tabs_shown(right)
        text = self.g.dock_text(page)
        overlays = right.locator(".ia_qualityOverlay").count()
        want = step["expect"]
        faults = self.stale(page, step)
        if title != want["title"] or label != want["label"]:
            faults.append(f"header {title!r}, {label!r}")
        if want["tabs"] is not None and tabs != want["tabs"]:
            faults.append(f"tabs {tabs}, the members call for {want['tabs']}")
        if overlays or QUALITY_LINE in text or EMPTY_FACEPLATE in text:
            faults.append(f"{overlays} quality overlays" + (", a member of bad quality" if QUALITY_LINE in text else "")
                          + (", the empty faceplate" if EMPTY_FACEPLATE in text else ""))
        self.row(step, f"a click on the symbol showing {step['find']!r} on {step['route']}",
                 f"{want['title']}, {want['label']}, tabs {want['tabs'] if want['tabs'] is not None else 'not judged'}",
                 f"{title}, {label}, tabs {tabs}", None, not faults, {"glass"}, "; ".join(faults), page)

    # -- T ----------------------------------------------------------------------------
    def trend_page(self, step: dict) -> None:
        page = self.page_for(step)
        self.goto(page, step["route"], fresh=True)
        want = sorted(c["title"] for c in step["cards"])
        cards = []
        for _ in range(30):
            page.wait_for_timeout(1000)
            cards = page.evaluate(self.g.TREND_CARDS)
            if len(cards) >= len(want) and all(c["line"] > 200 for c in cards):
                break
        empty = [f"{c['title']} (card {i + 1})" for i, c in enumerate(cards) if c["line"] <= 200]
        ok = sorted(c["title"] for c in cards) == want and not empty
        self.row(step, "the trend page opened", f"{len(want)} cards, one for each historised member, each drawing a line",
                 f"{len(cards)} cards, {len(cards) - len(empty)} drawing", None, ok, {"glass"},
                 ("no line on " + ", ".join(empty)) if empty else ("" if ok else f"titles {[c['title'] for c in cards]}"), page)

    def trend_tab(self, step: dict) -> None:
        page = self.page_for(step)
        right, why = self.open(page, step, "Trend")
        if right is None:
            self.row(step, "the Trend tab", "its series drawn", why, None, False, {"glass"}, why, page)
            return
        want = len(step["series"])
        ok, drawn = self.wait(page, lambda: (self.g.series_drawn(page) >= want, self.g.series_drawn(page)), 12)
        self.row(step, "the Trend tab of its faceplate", f"{want} series drawn ({', '.join(step['series'])})",
                 f"{drawn} series drawn", None, ok and drawn == want, {"glass"}, "", page)

    # -- C ----------------------------------------------------------------------------
    def state_seen(self, page, step: dict, state: dict, before: dict | None = None) -> tuple[bool, dict]:
        """Whether the glass and the tags show one state of a `states` step, and what each showed.
        `before` is what the state's effects that are compared with before read ahead of the action
        (`effects_before`)."""
        seen, ok = {}, True
        if step.get("row") and state.get("text") is not None:
            seen["row"] = self.g.row_text(page, step["row"])
            ok = ok and seen["row"] == state["text"]
        if state.get("pane"):
            text = self.g.dock_text(page)
            word = state["pane"].get("contains") or state["pane"].get("lacks")
            seen["pane"] = f"{word!r} {'shown' if word in text else 'not shown'}"
            ok = ok and ((word in text) == ("contains" in state["pane"]))
        tags = {}
        for path, want in state["tags"].items():
            readable, got = self.tags.value(path)
            if readable:
                tags[path.split("]", 1)[-1]] = got
                ok = ok and same(got, want)
        seen["tags"] = tags
        syms = []
        for r in state.get("symbols", []):
            good, shown = self.read(page, r, expect_of(r["rule"], state["value"]))
            syms.append(f"{r['symbol']}.{r['param']}: {shown}")
            ok = ok and good
        for i, e in enumerate(state.get("effects", [])):
            good, shown, kind = self.effect(page, e, (before or {}).get(i))
            if kind == "tag":
                tags[e["member"]] = shown
            else:
                syms.append(shown)
            ok = ok and good
        seen["symbols"] = syms
        return ok, seen

    def current_state(self, page, step: dict) -> dict | None:
        """The state a device is in, by its tags where they can be read, else by its row."""
        for s in step["states"]:
            got = [self.tags.value(p) for p in s["tags"]]
            if got and all(r for r, _v in got) and all(same(v, w) for (_r, v), w in zip(got, s["tags"].values())):
                return s
        if step.get("row"):
            text = self.g.row_text(page, step["row"])
            return next((s for s in step["states"] if s.get("text") == text), None)
        return None

    def states(self, step: dict) -> None:
        page = self.signed
        right, why = self.open(page, step, step["tab"])
        expected = "; ".join(filter(None, [
            f"the row {step['row']} reads the state" if step.get("row") else "",
            "the pane shows the lamp" if any(s.get("pane") for s in step["states"]) else "",
            "the tag holds the value written",
            "the symbols and effects named follow" if any(s.get("symbols") or s.get("effects") for s in step["states"]) else ""]))
        if right is None:
            self.row(step, "nothing", expected, why, None, False, set(), why, page)
            return
        start = self.current_state(page, step)
        if start is None:
            self.row(step, "nothing", expected, f"row {self.g.row_text(page, step['row']) if step.get('row') else None}",
                     None, False, set(), "the state the device is in could not be read, so no other could be chosen", page)
            return
        order = [s for s in step["states"] if s is not start] + [start]
        done, glass_seen, tag_seen = [], [], []
        faults = self.stale(page, step)
        evidence: set = set()
        ended = False
        try:
            for target in ([] if faults else order):
                button, disabled = self.g.dock_button(page, target["button"], target.get("sibling"))
                if button is None or disabled:
                    faults.append(f"the button {target['button']} is {'disabled' if button is not None else 'not shown'}")
                    break
                before = self.effects_before(page, target.get("effects", []))
                unread = self.unreadable(target.get("effects", []), before)
                if unread:
                    faults.append(f"before {target['button']}: " + "; ".join(unread))
                    break
                if not self.skip_write:
                    button.click()
                done.append(target["button"])
                within = max([e.get("within", WAIT_FLOOR) for e in target.get("effects", [])] + [WAIT_FLOOR])
                ok, seen = self.wait(page, lambda t=target, b=before: self.state_seen(page, step, t, b), within)
                glass_seen.append({k: v for k, v in seen.items() if k != "tags" and v not in (None, [])})
                tag_seen.append(seen["tags"])
                if seen["tags"]:
                    evidence.add("tag")
                if seen.get("row") is not None or seen.get("pane") or seen.get("symbols"):
                    evidence.add("glass")
                if not ok:
                    faults.append(f"after {target['button']}: glass {glass_seen[-1]}, tag {seen['tags']}, "
                                  f"expected {target.get('text') or target['value']}")
                    break
            ended = not faults
        finally:   # as found, whatever broke the step: the start state commanded again
            if not ended and done and not self.skip_write:
                try:
                    if self.current_state(page, step) is not start:
                        button, disabled = self.g.dock_button(page, start["button"], start.get("sibling"))
                        if button is not None and not disabled:
                            button.click()
                            page.wait_for_timeout(3000)
                    if self.current_state(page, step) is not start:
                        faults.append(f"the device was not put back to {start.get('text') or start['value']}")
                except Exception as e:
                    faults.append(f"the device could not be put back: {type(e).__name__}")
        if not evidence:
            faults.append("neither the glass nor a tag showed the state: nothing was proven")
        self.row(step, ", then ".join(done) or "nothing", expected, glass_seen, tag_seen, not faults, evidence,
                 "; ".join(faults), page)

    def target_of(self, step: dict, current: float) -> float:
        """The value an entry step writes: the current one moved by the plan's step, the preferred way
        where the member's bounds allow it, rounded to the digits the field shows."""
        lo, hi = step["bounds"]
        digits = decimals_of(step["format"])
        down, up = round(current - step["delta"], digits), round(current + step["delta"], digits)
        for v in ((down, up) if step["prefer"] == "down" else (up, down)):
            if (lo is None or v >= lo) and (hi is None or v <= hi) and v != round(current, digits):
                return v
        return up

    def require(self, page, need: dict, which: str) -> tuple[bool, str]:
        """An entry step's condition (the loop in manual), set or put back as an operator does."""
        button, disabled = self.g.dock_button(page, need[which]["button"])
        if button is None or disabled:
            return False, f"the button {need[which]['button']} is not offered"
        button.click()
        ok, seen = self.wait(page, lambda: (self.g.row_text(page, need["row"]) == need[which]["text"],
                                            self.g.row_text(page, need["row"])), 8)
        return ok, f"{need['row']} reads {seen!r}"

    def entry(self, step: dict) -> None:
        """W3, W4, W12, W14, W15: a value typed into a field. The field showing what was typed proves
        nothing (it keeps its text whether or not the write was made, GF-56): the step passes only
        when the tag holds the value, or a symbol or an effect of the page shows it.

        A symbol or an effect counts as that second surface only when it can tell: each is read
        before the write against what the value to be typed calls for, and one that agrees already
        (a symbol whose format is coarser than the step, a bound the plant met before) is still
        checked afterwards but is no evidence of the write. An effect that `changes` or `leaves` is
        compared with what it read before the write, and so always can tell."""
        page = self.signed
        right, why = self.open(page, step, step["tab"])
        expected = (f"the field {step['field']} and the tag hold the value typed"
                    + (", the symbols and effects named follow" if step["symbols"] or step["effects"] else ""))
        if right is None:
            self.row(step, "nothing", expected, why, None, False, set(), why, page)
            return
        need, set_here, evidence = step.get("requires"), False, set()
        faults = self.stale(page, step)
        done, glass_seen, tag_seen = "nothing", {}, {}
        typed_over = None   # the value the field held, once the walk has typed over it
        dtype = step.get("dataType")
        unit = 10.0 ** -decimals_of(step["format"]) / 2

        def readings(want, before=None):
            """Each symbol and effect of the step against the value `want`: (key, agrees, what was
            seen, `glass` or `tag`). Without `before` (the put back) the effects that are compared
            with before are left out: the value of before does not make them hold again."""
            out = []
            for i, s in enumerate(step["symbols"]):
                try:
                    good, text_seen = self.read(page, s, expect_of(s["rule"], want, dtype))
                except ValueError as ex:   # a value the format refuses: said, and no agreement
                    good, text_seen = False, str(ex)
                out.append((("symbol", i), good, f"{s['symbol']}.{s['param']}: {text_seen}", "glass"))
            for i, e in enumerate(step["effects"]):
                compared = bool(e.get("changes") or e.get("leaves"))
                if compared and before is None:
                    continue
                good, text_seen, kind = self.effect(page, e, before.get(i) if compared else None, written=want)
                out.append((("effect", i), good, text_seen, kind))
            return out

        def check(want, before=None, blind=()):
            seen, ok = {}, True
            f, _d = self.g.dock_field(page, step["field"])
            seen["field"] = self.g.field_number(f) if f is not None else None
            ok = ok and seen["field"] is not None and abs(seen["field"] - want) <= unit
            note = self.g.row_text(page, step["field"])
            if step.get("lamp") or note == REFUSED:
                seen["note"] = note
            ok = ok and note != REFUSED
            r, v = self.tags.value(step["tag"])
            seen["tag"] = v if r else None
            ok = ok and (not r or same(v, want))
            seen["symbols"], seen["tags"], seen["told"] = [], {}, set()
            for key, good, text_seen, kind in readings(want, before):
                if kind == "tag":
                    seen["tags"][step["effects"][key[1]]["member"]] = text_seen
                else:
                    seen["symbols"].append(text_seen)
                if good and key not in blind:
                    seen["told"].add(kind)
                ok = ok and good
            return ok, seen
        try:
            if need and not faults:
                readable, held = self.tags.value(need["tag"])
                if not (readable and same(held, need["value"])) and self.g.row_text(page, need["row"]) != need["set"]["text"]:
                    set_here = True
                    ok, seen = self.require(page, need, "set")
                    if not ok:
                        faults.append(f"the condition of the step was not reached: {seen}")
            if not faults:
                # a field whose condition was just set is enabled by the faceplate's next poll
                self.wait(page, lambda: (self.g.dock_field(page, step["field"])[1] is False, None), 8 if need else 3)
                field, disabled = self.g.dock_field(page, step["field"])
                if field is None or disabled:
                    faults.append(f"the field {step['field']} is {'disabled' if field is not None else 'not shown'}")
            if not faults:
                readable, held = self.tags.value(step["tag"])
                shown = self.g.field_number(field)
                current = float(held) if readable and held is not None else shown
                if current is None:
                    faults.append("neither the tag nor the field gave the current value")
            if not faults:
                target = self.target_of(step, current)
                text = number_format(target, step["format"]).replace(",", "")
                before = self.effects_before(page, step["effects"])
                faults += self.unreadable(step["effects"], before)
            if not faults:
                # what agrees with the value to be typed before it is typed cannot tell whether it was written
                blind = {key: text_seen for key, good, text_seen, _k in readings(target, before) if good}
                if not self.skip_write:
                    typed_over = current
                    self.g.type_into(field, text)
                done = f"{text} typed (it held {current:g})"
                within = max([e.get("within", WAIT_FLOOR) for e in step["effects"]] + [WAIT_FLOOR])
                ok, seen = self.wait(page, lambda: check(target, before, blind), within)
                glass_seen = {k: seen[k] for k in ("field", "note", "symbols") if seen.get(k) not in (None, [])}
                if blind:
                    glass_seen["read the same before the write"] = sorted(blind.values())
                tag_seen = {step["tag"].split("]", 1)[-1]: seen["tag"]} if seen["tag"] is not None else {}
                tag_seen.update(seen["tags"])
                evidence.add("control")
                evidence |= seen["told"]
                if seen["tag"] is not None:
                    evidence.add("tag")
                if not ok:
                    faults.append(f"after {text}: glass {glass_seen}, tag {seen['tag']}")
                elif not ({"glass", "tag"} & evidence):
                    faults.append("only the field typed into showed the value: its tag could not be read and no "
                                  "symbol or effect of the page " + (
                                      f"could tell ({len(blind)} read what the value calls for before the write "
                                      "already: a format coarser than the step, or a bound met before)" if blind
                                      else "shows the member") + ", so nothing was proven")
            mirror = self.during.get(step["id"])
            if mirror is not None and not faults and not self.skip_write and not self.no_crafted:
                self.refusal(mirror)   # while the condition holds: the role alone keeps the field shut
        finally:   # as found, whatever broke the step
            try:
                if typed_over is not None:
                    field, _d = self.g.dock_field(page, step["field"])
                    back = number_format(typed_over, step["format"]).replace(",", "")
                    self.g.type_into(field, back)
                    # as long as the effects were given: a simulated loop that took 49 s to follow the value
                    # typed takes as long to follow the value put back (the plant project's first dynamic walk)
                    ok, seen = self.wait(page, lambda: check(typed_over),
                                         max([e.get("within", WAIT_FLOOR) for e in step["effects"]] + [WAIT_FLOOR]))
                    done += f", then {back}"
                    if not ok:
                        faults.append(f"putting {back} back: glass {seen.get('field')}, tag {seen['tag']}")
                if need and set_here:
                    ok, seen = self.require(page, need, "back")
                    if not ok:
                        faults.append(f"the condition of the step was not put back: {seen}")
            except Exception as e:
                faults.append(f"the step could not put back what it changed: {type(e).__name__}: {str(e)[:120]}")
        self.row(step, done, expected, glass_seen, tag_seen, not faults, evidence, "; ".join(faults), page)

    def pulse(self, step: dict) -> None:
        """W18: the button of a pulse command, found by its caption. A pulse leaves nothing where it
        was written (the plant returns the member to false), and its button reads the same before and
        after, so the proof is elsewhere: every effect the effects file names for it (a member's tag
        that changes, a member's own reading on a symbol that leaves its resting text and comes back),
        and the faceplate's own step row leaving its resting text where it has one. Without an effect
        the member itself must be read true before anything returns it. Where the effects file says
        that the plant returns the member (`returns`), a member still true once the effects are met
        fails the step: a trigger that stays set is a pulse the plant did not take. Whatever the
        verdict, a member nothing returned is put back by importing its definition of before."""
        page = self.signed
        right, why = self.open(page, step, step["tab"])
        effects = step.get("effects", [])
        expected = ("the pulse arrives: " + (", ".join(
            f"{e['member']} {'changes' if e.get('changes') else 'leaves its resting reading' if e.get('leaves') else 'follows'}"
            for e in effects) if effects else f"{step['member']} reads true")
            + (f"; the plant returns {step['member']} to false" if step.get("returns") else "")
            + ("; the faceplate's row " + step["row"] + " is recorded" if step.get("row") else ""))
        if right is None:
            self.row(step, "nothing", expected, why, None, False, set(), why, page)
            return
        faults, evidence, notes = self.stale(page, step), set(), []
        glass_seen, tag_seen, done = {}, {}, "nothing"
        try:
            end = self.tags.keep(step["tag"])
        except TagFolderRefused:   # a member whose source lies outside the plan's folder: pressed, never imported
            end = None
        kept: list[str] = []
        for path in step.get("restores", []):   # the plant's flags this pulse moves and nothing returns
            try:
                kept.append(self.tags.keep(path))
            except TagFolderRefused as ex:
                faults.append(f"{ex}: it could not be put back")
        try:
            button, disabled = self.g.dock_button(page, step["button"])
            if button is None or disabled:
                faults.append(f"the button {step['button']} is {'disabled' if button is not None else 'not shown'}")
            if not faults:
                rest_row = self.g.row_text(page, step["row"]) if step.get("row") else None
                before = self.effects_before(page, effects)
                rest = {i: b for i, b in before.items() if effects[i].get("leaves")}
                faults += self.unreadable(effects, before)
            if not faults:
                if not self.skip_write:
                    button.click()
                done = f"the button {step['button']}"
                met: dict[int, str] = {}
                left = {"row": None, "member": None}

                def check():
                    r, v = self.tags.value(step["tag"])
                    if r and v is True:
                        left["member"] = True
                    if step.get("row") and left["row"] is None:
                        now = self.g.row_text(page, step["row"])
                        if now != rest_row:
                            left["row"] = now
                    for i, e in enumerate(effects):   # an effect of a pulse passes by: once met, it is met
                        if i not in met:
                            good, shown, _kind = self.effect(page, e, before.get(i))
                            if good:
                                met[i] = shown
                    if effects:
                        return len(met) == len(effects), None
                    return left["member"] is True, None
                within = max([e.get("within", WAIT_FLOOR) for e in effects] + [WAIT_FLOOR])
                ok, _seen = self.wait(page, check, within, step_ms=300)
                if ok and step.get("row") and left["row"] is None:   # the faceplate polls its device once a second
                    self.wait(page, lambda: (check()[0] and left["row"] is not None, None), 4, step_ms=300)
                message = self.g.dock_message(page)
                glass_seen = {"effects": [met[i] for i in sorted(met) if not effects[i].get("changes")]}
                if step.get("row"):
                    glass_seen["row"] = [rest_row, left["row"]]
                if message:
                    glass_seen["message"] = message
                    faults.append(f"the faceplate reads {message!r}")
                tag_seen = {effects[i]["member"]: met[i] for i in sorted(met) if effects[i].get("changes")}
                if left["member"]:
                    tag_seen[step["tag"].split("]", 1)[-1]] = "read true after the press"
                if tag_seen:
                    evidence.add("tag")
                if glass_seen["effects"] or left["row"] is not None:
                    evidence.add("glass")
                if not ok:
                    missing = [effects[i]["member"] for i in range(len(effects)) if i not in met]
                    faults.append(f"within {within} s " + (f"no effect on {', '.join(missing)}" if effects else
                                  f"{step['member']} was not read true, and the effects file names no effect of the pulse"))
                elif not evidence:
                    faults.append("neither the glass nor a tag showed the pulse: nothing was proven")
                # back at rest: every reading that left comes back within the time the effects file gives
                for i, e in enumerate(effects):
                    if e.get("leaves") and e.get("returnsWithin") and i in met:
                        back, now = self.wait(page, lambda e=e, i=i: (self.shown(page, e) == rest[i], self.shown(page, e)),
                                              e["returnsWithin"])
                        glass_seen.setdefault("back at rest", []).append(
                            f"{e['symbol']}.{e['param']}: {' | '.join(map(str, now or []))}")
                        if not back:
                            faults.append(f"{e['symbol']}.{e['param']} did not come back to "
                                          f"{' | '.join(map(str, rest[i]))!r} within {e['returnsWithin']} s")
                # the member itself: where the effects file says the plant returns it, it must be false again
                if ok and step.get("returns") and not self.skip_write:
                    def returned():
                        r, v = self.tags.value(step["tag"])
                        return r and v is False, (r, v)
                    back, held = self.wait(page, returned, WAIT_FLOOR)
                    tag_seen[step["tag"].split("]", 1)[-1] + " (after the effects)"] = held[1] if held[0] else "not readable"
                    if not back:
                        faults.append(f"the plant did not return {step['member']} to false within {WAIT_FLOOR} s of its "
                                      "effects, which the effects file says it does (`returns`)" if held[0] else
                                      f"{step['member']} could not be read, so its return (`returns`) was not seen")
        finally:   # a member nothing returned is put back; one the plant returned is left as it is
            try:
                if kept and not self.skip_write:   # what the effects file says the pulse leaves changed
                    done_back = self.tags.restore(kept)
                    left = [u for u in self.tags.unrestored if u["tag"] in kept]
                    if left:
                        faults.append(f"the plant's flags the pulse moved could not be put back: {left}")
                    else:
                        tag_seen["put back"] = [t.split("]", 1)[-1] for t in done_back]
                r, v = self.tags.value(step["tag"])
                if r and v is True and not self.skip_write:
                    if end is not None and self.tags.restore([end]):
                        notes.append("nothing returned the member to false: its definition of before was imported")
                    else:
                        faults.append("nothing returned the member to false, and its definition of before could not "
                                      "be imported: " + ("its source lies outside the plan's tag folder" if end is None else
                                                         str([u["why"] for u in self.tags.unrestored if u["tag"] == end])))
                elif end is not None:
                    self.tags.before.pop(end, None)
            except Exception as e:
                faults.append(f"the pulse member could not be put back: {type(e).__name__}")
        self.row(step, done, expected, glass_seen, tag_seen, not faults, evidence, "; ".join(faults + notes), page)

    def page_pulse(self, step: dict) -> None:
        """W18 on a page: a command button of a diagram page (a descriptor's `buttons` of the type `pulse`,
        COB-159). The first press asks and writes nothing: the question shows with Confirm and Cancel in the
        button's place, and the tag still reads false. Cancel gives the button back and writes nothing. The
        press again and Confirm hold the tag true for the length the descriptor gives (`ms`) and let it go:
        the tag is read true, held about that long (it is read through the gateway's export, about half a
        second apart, so the hold is judged within a second and a half under and three seconds over) and read
        false again, and the button then shows its caption and no refusal. A tag left true is imported back
        from its definition of before."""
        page, g = self.signed, self.g
        caption, tag, length = step["button"], step["tag"], step["ms"] / 1000.0
        expected = (f"{caption} asks {step['question']!r} and writes nothing; Cancel writes nothing; Confirm holds "
                    f"the tag true for about {length:g} s and lets it go")
        self.goto(page, step["route"], fresh=True)
        faults, glass_seen, tag_seen, evidence, notes = [], {}, {}, set(), []
        done = "nothing"
        try:
            end = self.tags.keep(tag)
        except TagFolderRefused:   # a tag whose source lies outside the plan's folder: pressed, never imported
            end = None
        try:
            shown, disabled = g.page_button(page, caption)
            if not shown or disabled:
                faults.append(f"the button {caption} is {'disabled' if shown else 'not shown'}")
            readable, rest = self.tags.value(tag)
            if not faults and not (readable and rest is False):
                faults.append(f"the tag reads {rest if readable else 'nothing readable'} before the press, not false")

            def asked():
                question = g.page_label_shown(page, step["question"])
                yes, no = g.page_button(page, CONFIRM)[0], g.page_button(page, CANCEL)[0]
                return question and yes and no, (question, yes, no)
            if not faults:   # the press asks, and writes nothing
                g.page_button_click(page, caption)
                ok, seen = self.wait(page, asked, 4, step_ms=200)
                r1, v1 = self.tags.value(tag)
                glass_seen["asked"] = {"question": seen[0], "Confirm": seen[1], "Cancel": seen[2]}
                tag_seen["after the press"] = v1 if r1 else "not readable"
                if not ok:
                    faults.append(f"the press did not show the question {step['question']!r} with Confirm and Cancel ({seen})")
                elif r1 and v1 is not False:
                    faults.append(f"the tag read {v1} after the press, before Confirm: the press wrote")
                evidence |= {"glass"} | ({"tag"} if r1 else set())
            if not faults:   # Cancel gives the button back and writes nothing
                g.page_button_click(page, CANCEL)
                ok, _seen = self.wait(page, lambda: (g.page_button(page, caption)[0] and not g.page_button(page, CONFIRM)[0],
                                                     None), 4, step_ms=200)
                page.wait_for_timeout(1000)
                r2, v2 = self.tags.value(tag)
                tag_seen["after Cancel"] = v2 if r2 else "not readable"
                if not ok:
                    faults.append("Cancel did not give the button back")
                elif r2 and v2 is not False:
                    faults.append(f"the tag read {v2} after Cancel")
            if not faults:   # press and Confirm
                g.page_button_click(page, caption)
                self.wait(page, asked, 4, step_ms=200)
                g.page_button_click(page, CANCEL if self.skip_write else CONFIRM)
                done = f"{caption}, then {'Cancel' if self.skip_write else CONFIRM}"
                seen: dict[str, float] = {}

                def watch():
                    r, v = self.tags.value(tag)
                    now = time.time()
                    if r and v is True and "up" not in seen:
                        seen["up"] = now
                    if "up" in seen and r and v is False and "down" not in seen:
                        seen["down"] = now
                    return "down" in seen, None
                self.wait(page, watch, length + WAIT_FLOOR + 4, step_ms=300)
                if "up" not in seen:
                    faults.append(f"the tag was not read true within {length + WAIT_FLOOR + 4:g} s of Confirm")
                elif "down" not in seen:
                    faults.append("the tag was read true and not let go")
                else:
                    held = seen["down"] - seen["up"]
                    tag_seen["held true for"] = f"{held:.1f} s"
                    evidence.add("tag")
                    if not (length - 1.5 <= held <= length + 3.0):
                        faults.append(f"the tag was held true for {held:.1f} s, not about {length:g} s")
                page.wait_for_timeout(1500)
                texts = [b["text"] for b in g.page_buttons(page)]
                refused = [t for t in texts if t.startswith(MESSAGE_REFUSED)]
                back = caption in texts and CONFIRM not in texts
                glass_seen["afterwards"] = {"button": caption in texts, "question closed": CONFIRM not in texts,
                                            **({"refusal": refused[0]} if refused else {})}
                evidence.add("glass")
                if refused:
                    faults.append(f"the button reads {refused[0]!r}")
                elif not back and "down" in seen:
                    faults.append("the button did not return to its caption once the pulse was let go")
        finally:   # a tag nothing let go is put back; one the pulse released is left as it is
            try:
                r, v = self.tags.value(tag)
                if r and v is True and not self.skip_write:
                    if end is not None and self.tags.restore([end]):
                        notes.append("the tag was left true: its definition of before was imported")
                    else:
                        faults.append("the tag was left true, and its definition of before could not be imported")
                elif end is not None:
                    self.tags.before.pop(end, None)
            except Exception as e:
                faults.append(f"the pulse tag could not be put back: {type(e).__name__}")
        self.row(step, done, expected, glass_seen, tag_seen, not faults, evidence, "; ".join(faults + notes), page)

    def page_refusal(self, step: dict, page=None) -> None:
        """With nobody signed in: a page command button is disabled, and a crafted client's calls of its handlers
        (the press, then Confirm) reach the gateway, which refuses them on the button and leaves the tag as it was.
        A click on the disabled button runs no script (GF-45), so the handlers the client holds are called
        directly (`glass.page_crafted_call`, the page's counterpart of `crafted_call`, GF-59)."""
        page, g = page or self.anon, self.g
        caption, tag = step["button"], step["tag"]
        expected = "the button disabled; the crafted press and Confirm refused by the gateway on the button; the tag as before"
        self.goto(page, step["route"], fresh=True)
        page.wait_for_timeout(2500)   # the permissions poll every 2 s
        faults, glass_seen, tag_seen, evidence = [], {}, {}, {"control"}
        shown, disabled = g.page_button(page, caption)
        glass_seen["disabled"] = {caption: disabled}
        if not shown or not disabled:
            faults.append(f"the button {caption} is {'enabled' if shown else 'not shown'}")
        readable, before = self.tags.value(tag)
        refused_by, done = "nothing was crafted", "nothing"
        if not self.no_crafted and (not faults or self.force_crafted):
            called = g.page_crafted_call(page, caption)
            page.wait_for_timeout(1000)
            if called == "called":   # the press asked; the client's own Confirm is called as well
                called = g.page_crafted_call(page, CONFIRM)
            done = f"a crafted press of {caption}, then the handler of Confirm called directly ({called})"

            def refusal_shown():
                texts = [b["text"] for b in g.page_buttons(page)]
                return any(t.startswith(MESSAGE_REFUSED) for t in texts), texts
            answered, texts = self.wait(page, refusal_shown, 5, step_ms=300)
            glass_seen["message"] = next((t for t in texts if t.startswith(MESSAGE_REFUSED)), "")
            refused_by = "the gateway" if answered else "nothing" if called == "called" else "the client only"
            if called != "called":
                faults.append(f"the button's handler could not be called ({called}): only the client refused, and the "
                              "gateway's own check was not exercised")
            elif not answered:
                faults.append("the handlers were called and the button reads no refusal: nothing shows that the gateway "
                              "refused it")
            evidence.add("glass")
            after_readable, after = self.tags.value(tag)
            if readable and after_readable:
                tag_seen[tag.split("]", 1)[-1]] = [before, after]
                evidence.add("tag")
                if not same(before, after):
                    faults.append(f"the tag went from {before} to {after}")
        if self.no_crafted and not faults:
            done = "nothing (the disabled state only)"
        self.row(step, done, expected, glass_seen, tag_seen, not faults, evidence, "; ".join(faults), page,
                 extra={"refused_by": refused_by})

    def fault_reset(self, step: dict) -> None:
        """W5. The Reset fault button shows only while the device is faulted, so the fault is raised
        first by a tag import where the device is not faulted, and its alarm acknowledged, so that the
        reset leaves no cleared, unacknowledged event behind. The refusal of the same button, in the
        session with nobody signed in, runs while the fault is held. The definition the fault's tag
        had before the step is kept first, and imported back whatever happens."""
        page = self.signed
        right, why = self.open(page, step, step["tab"])
        expected = f"the row {step['row']} reads {step['clear']}, the tag holds false, the button is gone"
        if right is None:
            self.row(step, "nothing", expected, why, None, False, set(), why, page)
            return
        readable, before = self.tags.value(step["tag"])
        faults, evidence, notes = self.stale(page, step), set(), []
        if not readable:
            self.row(step, "nothing", expected, None, None, False, set(),
                     "the fault's tag could not be read, so the walk raised none", page)
            return
        done, glass_seen, tag_seen, restored = "nothing", {}, {}, []
        end = self.tags.keep(step["tag"])   # also for a device found faulted: its fault is imported back
        try:
            alarms0 = self.g.tab_count(right)
            if before is not True and not faults:
                self.tags.set({step["tag"]: True})
                ok, seen = self.wait(page, lambda: (self.g.row_text(page, step["row"]) == step["set"],
                                                    self.g.row_text(page, step["row"])), 10)
                notes.append("fault raised by a tag import")
                if not ok:
                    faults.append(f"the fault imported did not show: {step['row']} reads {seen!r}")
            if not faults and step.get("alarm"):
                if before is not True:   # the alarm the walk raised: counted on the tab before it is acknowledged
                    self.wait(page, lambda: (self.g.tab_count(right) == (alarms0 or 0) + 1, None), 10)
                acked = self.acknowledge(page, step)
                notes.append(f"its alarm acknowledged: {acked}")
                if not acked:   # the reset then clears an unacknowledged alarm, and its event stays in the lists
                    faults.append("the fault's alarm was not acknowledged: the reset leaves a cleared, unacknowledged event")
                page.wait_for_timeout(1500)
                right = self.g.dock(page, "right")
                if not self.g.tab(right, step["tab"]):
                    right, why = self.open(page, step, step["tab"])
            mirror = self.during.get(step["id"])
            if mirror is not None and not faults and not self.skip_write and not self.no_crafted:
                self.refusal(mirror)
            if not faults:
                button, disabled = self.g.dock_button(page, step["button"])
                if button is None or disabled:
                    faults.append(f"the button {step['button']} is {'disabled' if button is not None else 'not shown'}")
                else:
                    if not self.skip_write:
                        button.click()
                    done = step["button"]

                    def check():
                        seen = {"row": self.g.row_text(page, step["row"]),
                                "button": self.g.dock_button(page, step["button"])[0] is not None}
                        r, v = self.tags.value(step["tag"])
                        seen["tag"] = v if r else None
                        seen["symbols"] = []
                        ok = seen["row"] == step["clear"] and not seen["button"] and (not r or v is False)
                        for s in step["symbols"]:
                            good, shown = self.read(page, s, expect_of(s["rule"], False))
                            seen["symbols"].append(f"{s['symbol']}.{s['param']}: {shown}")
                            ok = ok and good
                        return ok, seen
                    ok, seen = self.wait(page, check, 10)
                    glass_seen = {"row": seen["row"], "button shown": seen["button"], "symbols": seen["symbols"]}
                    tag_seen = {step["tag"].split("]", 1)[-1]: seen["tag"]}
                    evidence |= {"glass", "tag"} if seen["tag"] is not None else {"glass"}
                    if not ok:
                        faults.append(f"after {step['button']}: {glass_seen}, tag {seen['tag']}")
                    if step.get("alarm") and before is not True and not self.skip_write:   # nothing left behind
                        ok, now = self.wait(page, lambda: (self.g.tab_count(right) == alarms0, self.g.tab_count(right)), 12)
                        glass_seen["alarms tab"] = [alarms0, now]
                        if not ok:
                            faults.append(f"after the reset the Alarms tab counts {now} (before the fault {alarms0}): "
                                          "an event of the walk's fault is left")
        finally:
            # as found: the definition of before (a fault the walk raised is cleared, a fault found is back)
            restored = self.tags.restore([end])
            if not restored:
                faults.append(f"the fault's definition of before was not restored: "
                              f"{[u['why'] for u in self.tags.unrestored if u['tag'] == end]}")
        if before is True:
            notes.append("the device was faulted when the step began: its fault was imported back, as a new alarm event")
        page.wait_for_timeout(2500)
        self.row(step, done, expected, glass_seen, tag_seen, not faults, evidence,
                 "; ".join(faults + notes + [f"definition of before imported and read back: {len(restored)}"]), page)

    def acknowledge(self, page, step: dict, tries: int = 6) -> bool:
        """Acknowledge the open device's unacknowledged alarm (`glass.ack_alarm`), tried again while the
        list has not caught up with an alarm raised a moment ago: the stock table polls every 5 s (gate
        G11 reads it the same way), and on 2026-10-11 a single try two seconds after a fault was
        imported found no row and left the walk's own alarm unacknowledged. A menu a failed try left
        open under module rendering is closed with Escape, which leaves the faceplate open."""
        for _ in range(tries):
            if self.g.ack_alarm(page, step["device"]):
                return True
            page.keyboard.press("Escape")
            page.wait_for_timeout(2500)
        return False

    # -- R ----------------------------------------------------------------------------
    def refusal(self, step: dict, page=None) -> None:
        """With nobody signed in: the control is disabled, and a crafted client's action on it reaches
        the gateway, which refuses it and leaves the tag as it was.

        An entry is crafted through the field (`glass.crafted_entry`): the commit runs the row's
        script, and the row must then read "Refused", the gateway's own answer. A button is crafted
        twice: the `disabled` flag removed in the page and the button clicked, which runs no script at
        all (GF-45), and then the handler the client holds for the button called directly
        (`glass.crafted_call`), which does run the button's script in the gateway (GF-59): the
        faceplate's message line must then read the refusal. `refused_by` on the row says which answered: the
        gateway, or the client only (no script ran, so the gateway's own check was not exercised).

        Evidence: the tag compared before and after where it can be read, the symbols of the page that
        show the member, another row of the faceplate; a step whose only evidence would be the control
        it operated fails. A refusal whose control a condition enables (the manual output, in manual)
        runs while the condition holds, and fails without it: the field would be shut for the mode."""
        page = page or self.anon
        right, why = self.open(page, step, step["tab"])
        expected = ("the control disabled; the crafted action refused by the gateway; the tag and the glass as before")
        if right is None:
            self.row(step, "nothing", expected, why, None, False, set(), why, page)
            return
        page.wait_for_timeout(2500)   # the permissions poll every 2 s
        faults, evidence, glass_seen, tag_seen = self.stale(page, step), set(), {}, {}
        if not self.no_crafted and not faults and (self.g.dock_message(page) or self.g.refused_rows(page)):
            # A refusal this walk caused earlier on this device still shows: a row's note and the
            # faceplate's message line stay until the next accepted write. Both clear when the faceplate
            # is handed another device (`framework._tabbed`, `ROW_RESET`), so the walk opens another
            # device and comes back; a reload of the page does not clear them (measured 2026-10-11: the
            # gateway keeps the page's views). The gateway's answer to this step can then be told from
            # the earlier one, and a refusal still shown after that fails the step.
            right, why = self.reopen(page, step)
            if right is None:
                self.row(step, "nothing", expected, why, None, False, set(), why, page)
                return
            page.wait_for_timeout(2500)
            left = self.g.refused_rows(page) + ([self.g.dock_message(page)] if self.g.dock_message(page) else [])
            if left:
                faults.append(f"the faceplate still reads a refusal after another device was shown in it: {left}")
        refused_by = "nothing was crafted"
        crafting = (lambda: (not faults or self.force_crafted) and not self.no_crafted)
        need = step.get("requires")
        if need:
            r, held = self.tags.value(need["tag"])
            row = self.g.row_text(page, need["row"])
            glass_seen["condition"] = f"{need['row']} reads {row!r}"
            if not ((r and same(held, need["value"])) or (not r and row == need["set"]["text"])):
                faults.append(f"the condition that enables the control does not hold ({need['row']} reads {row!r}): "
                              "the control would be shut for that, not for the role")
        dtype = step.get("dataType")
        done = "nothing"
        if "field" in step:
            field, disabled = self.g.dock_field(page, step["field"])
            glass_seen["disabled"] = {step["field"]: disabled}
            if field is None or not disabled:
                faults.append(f"the field {step['field']} is {'enabled' if field is not None else 'not shown'}")
            readable, before = self.tags.value(step["tag"])
            shown = self.g.field_number(field) if field is not None else None
            note0 = self.g.row_text(page, step["field"])
            if note0 == REFUSED:
                faults.append(f"the row read {REFUSED!r} before the crafted entry, so the gateway's answer to it could not be told")
            if field is not None and crafting():
                current = float(before) if readable and before is not None else (shown if shown is not None else 0.0)
                target = self.target_of(step, current)
                sent = self.g.crafted_entry(page, step["field"], number_format(target, step["format"]).replace(",", ""))
                # F029: the row holds the value; its Set makes the write, so the crafted client calls it. The Set
                # shows once the gateway has taken the entry (measured 2026-10-24: not at once, about a second)
                shown_set, _ = self.wait(page, lambda: (self.g.dock_button(page, SET)[0] is not None, None), 4, step_ms=200)                     if sent else (False, None)
                if sent and shown_set:
                    self.g.crafted_call(page, SET)
                done = f"a crafted entry of {target:g}" + ("" if sent else " (the client took no keys)")
                if not sent:
                    faults.append("the crafted entry could not be made, so the refusal was not exercised")
                self.refused.setdefault((id(page), step.get("device", "")), set()).add(step["field"])
                answered, note1 = self.wait(page, lambda: (self.g.row_text(page, step["field"]) == REFUSED,
                                                           self.g.row_text(page, step["field"])), 5)
                page.wait_for_timeout(1500)
                glass_seen["note"] = [note0, note1]
                refused_by = "the gateway" if answered and note0 != REFUSED else "nothing"
                if sent and not answered:
                    faults.append(f"the row did not read {REFUSED!r} after the crafted entry (it reads {note1!r}): "
                                  "nothing shows that the gateway refused it")
                r2, after = self.tags.value(step["tag"])
                if readable and r2:
                    tag_seen = {step["tag"].split("]", 1)[-1]: [before, after]}
                    evidence.add("tag")
                    if not same(before, after):
                        faults.append(f"the tag went from {before} to {after}")
                if readable:
                    for s in step.get("symbols", []):
                        good, text_seen = self.read(page, s, expect_of(s["rule"], before, dtype))
                        glass_seen.setdefault("symbols", []).append(f"{s['symbol']}.{s['param']}: {text_seen}")
                        evidence.add("glass")
                        if not good:
                            faults.append(f"the symbol {s['symbol']} no longer shows the value of before: {text_seen}")
            evidence.add("control")
        else:
            states = {}
            for c in step["controls"]:
                _b, disabled = self.g.dock_button(page, c["button"], c.get("sibling"))
                states[c["button"]] = disabled
            glass_seen["disabled"] = states
            shown = [k for k, v in states.items() if v is not None]
            if (not shown) or (not step.get("any") and len(shown) < len(states)) or any(states[k] is False for k in shown):
                faults.append("controls not shown or enabled: " + ", ".join(
                    f"{k} {'not shown' if v is None else 'enabled' if v is False else 'disabled'}" for k, v in states.items()))
            watched = [p for s in step["states"] for p in s["tags"]] + list(step.get("watch", []))
            before = {p: self.tags.value(p) for p in watched}
            row_before = self.g.row_text(page, step["row"]) if step.get("row") else None
            rest = {r["symbol"]: self.shown(page, r) for r in step.get("rest", [])}
            if shown and crafting():
                # the button that would change something: of a state the device is not in
                here = next((s for s in step["states"] if all(before[p][0] and same(before[p][1], w)
                                                              for p, w in s["tags"].items())), None)
                pick = next((s for s in step["states"] if s is not here and states.get(s["button"]) is not None
                             and (here is not None or s.get("text") != row_before)), None)
                pick = pick or next(s for s in step["states"] if states.get(s["button"]) is not None)
                message0 = self.g.dock_message(page)
                pressed = self.g.crafted_press(page, pick["button"], pick.get("sibling"))
                page.wait_for_timeout(1500)
                called = self.g.crafted_call(page, pick["button"], pick.get("sibling"))
                if called == "called":
                    # F029: the button asked and wrote nothing; the Confirm row makes the write, so the
                    # crafted client calls its handler too, and the gateway answers that call
                    page.wait_for_timeout(1500)
                    if self.g.dock_button(page, CONFIRM)[0] is not None:
                        called = self.g.crafted_call(page, CONFIRM)
                done = (f"a crafted click on {pick['button']}" + ("" if pressed else " (not found)")
                        + f", then its handler called directly ({called})")
                answered, message1 = self.wait(page, lambda: (self.g.dock_message(page).startswith(MESSAGE_REFUSED),
                                                              self.g.dock_message(page)), 5)
                page.wait_for_timeout(1500)
                glass_seen["message"] = [message0, message1]
                refused_by = ("the gateway" if answered and not message0 else
                              "nothing" if called == "called" else "the client only")
                if not pressed:
                    faults.append("the crafted click found no button")
                if called != "called":
                    faults.append(f"the button's handler could not be called ({called}): only the client refused, "
                                  "and the gateway's own check was not exercised")
                elif not answered:
                    faults.append(f"the button's handler was called and the faceplate's message line reads {message1!r}: "
                                  "nothing shows that the gateway refused it")
                after = {p: self.tags.value(p) for p in before}
                readable = {p: [before[p][1], after[p][1]] for p in before if before[p][0] and after[p][0]}
                if readable:
                    tag_seen = {p.split("]", 1)[-1]: v for p, v in readable.items()}
                    evidence.add("tag")
                    changed = {p: v for p, v in readable.items() if not same(v[0], v[1])}
                    if changed:
                        faults.append(f"tags changed: {changed}")
                if step.get("row"):
                    row_after = self.g.row_text(page, step["row"])
                    glass_seen["row"] = [row_before, row_after]
                    evidence.add("glass")
                    if row_after != row_before:
                        faults.append(f"{step['row']} went from {row_before!r} to {row_after!r}")
                for r in step.get("rest", []):
                    now = self.shown(page, r)
                    glass_seen.setdefault("symbols", []).append(f"{r['symbol']}: {' | '.join(map(str, now or []))}")
                    evidence.add("glass")
                    if now != rest[r["symbol"]]:
                        faults.append(f"the symbol {r['symbol']} went from {rest[r['symbol']]} to {now}")
                state_now = next((s for s in step["states"] if s is here), None)
                for s in (state_now or {}).get("symbols", []):
                    good, text_seen = self.read(page, s, expect_of(s["rule"], state_now["value"]))
                    glass_seen.setdefault("symbols", []).append(f"{s['symbol']}.{s['param']}: {text_seen}")
                    evidence.add("glass")
                    if not good:
                        faults.append(f"the symbol {s['symbol']} no longer shows the state of before: {text_seen}")
            evidence.add("control")
        if self.no_crafted and not faults:
            done = "nothing (the disabled state only)"
        elif not self.no_crafted and not faults and not ({"glass", "tag"} & evidence):
            faults.append("only the control operated showed the refusal: its tag could not be read and no row or "
                          "symbol shows the member, so nothing was proven")
        self.row(step, done, expected, glass_seen, tag_seen, not faults, evidence, "; ".join(faults), page,
                 extra={"refused_by": refused_by})

    # -- C: W11 by a trip -------------------------------------------------------------
    def trip(self, step: dict) -> None:
        """W11 by a trip (COB-204). The condition's source is raised to its trip value by a tag import:
        the condition's row must read Not met and the head Interlocked. The source is put back (its
        definition of before, read back): the row must read Latched, the reset row shows, and the head
        still reads Interlocked, since a trip latches (COBD-023). Then the Interlocks tab's Reset, as an
        operator presses it: the row reads Met and the head no longer Interlocked, and `ilk/resetAt`,
        which the Reset writes, holds a new value (the tag evidence of the write path). The head is read
        where the plan names one (the asm style's header); the openbridge style draws none on that tab.

        Nothing is left behind whatever happens: the source's definition of before is imported back;
        a latch the Reset did not clear is cleared by an import of `ilk/resetAt` with the time now (the
        latch's own rule: a reset later than the trip releases it), and the step fails; and
        `ilk/resetAt` is imported back to its definition of before, after which the row must still read
        Met (the latch keeps the latest reset it saw, so the put-back latches nothing again)."""
        page = self.signed
        lamps, head = step["lamps"], step["head"]
        expected = (f"the row {step['text']!r} reads {lamps['met']}; {lamps['tripped']}"
                    + (f" and the head {head}" if head else "") + " with "
                    f"the source raised; {lamps['latched']} and {step['cleared']!r} once it is put back; "
                    f"{lamps['met']} after {step['button']}, ilk/resetAt written, nothing left behind")
        right, why = self.open(page, step, step["tab"])
        if right is None:
            self.row(step, "nothing", expected, why, None, False, set(), why, page)
            return
        readable, rest = self.tags.value(step["source"])
        if not readable:
            self.row(step, "nothing", expected, None, None, False, set(),
                     "the trip's source could not be read, so the walk raised nothing", page)
            return
        if same(rest, step["trip"]):
            self.row(step, "nothing", expected, None, {step["source"]: rest}, False, {"tag"},
                     "the trip's source already holds its trip value: the device is tripped, so the walk raised nothing",
                     page)
            return
        _r, reset0 = self.tags.value(step["tag"])

        def seen():
            return self.g.interlock_lamp(page, step["text"]), self.g.dock_text(page)

        def state(lamp: str, held: bool, also: str | None = None):
            def check():
                got, text = seen()
                ok = got == lamp and (not head or (head in text) == held) and (also is None or also in text)
                return ok, {"row": got, "head": "none drawn" if not head else head if head in text else "not held",
                            **({"shows": also in text} if also else {})}
            return check
        faults, notes, done = self.stale(page, step), [], []
        glass_seen: list = []
        tag_seen: dict = {}
        evidence: set = set()
        source_end = self.tags.keep(step["source"])
        reset_end = self.tags.keep(step["tag"])
        raised = cleared = False
        try:
            ok, now = state(lamps["met"], False)()
            glass_seen.append(now)
            if not ok and not faults:
                faults.append(f"before the trip the row reads {now['row']!r} and the head {now['head']}")
            if not faults:
                if not self.skip_write:
                    reply = self.tags.set({step["source"]: step["trip"]})
                    if reply["missing"] or reply["failed"]:
                        faults.append(f"the source's import did not arrive ({reply['missing']}, {reply['failed']})")
                raised = True
                done.append("the source raised by a tag import")
            if not faults:
                r, v = self.tags.value(step["source"])
                tag_seen["source raised"] = v if r else None
                ok, now = self.wait(page, state(lamps["tripped"], True), 12)
                glass_seen.append(now)
                if not ok:
                    faults.append(f"with the source raised the row reads {now['row']!r} and the head {now['head']}")
            if not faults:
                if not self.tags.restore([source_end]):
                    faults.append("the source's definition of before was not restored")
                done.append("put back")
                ok, now = self.wait(page, state(lamps["latched"], True, step["cleared"]), 12)
                glass_seen.append(now)
                if not ok:
                    faults.append(f"with the source put back the row reads {now['row']!r}, the head {now['head']} "
                                  f"and the reset row {'shows' if now.get('shows') else 'does not show'}: no latch")
            if not faults:
                button, disabled = self.g.dock_button(page, step["button"])
                if button is None or disabled:
                    faults.append(f"the button {step['button']} is {'disabled' if button is not None else 'not shown'}")
                else:
                    button.click()
                    done.append(step["button"])
                    ok, now = self.wait(page, state(lamps["met"], False), 12)
                    glass_seen.append(now)
                    r, v = self.tags.value(step["tag"])
                    tag_seen["ilk/resetAt"] = [reset0, v if r else None]
                    if r and not same(v, reset0):
                        evidence.add("tag")
                    else:
                        faults.append(f"after {step['button']} ilk/resetAt holds {v if r else 'nothing readable'} "
                                      f"(before {reset0}): the write did not arrive")
                    if not ok:
                        faults.append(f"after {step['button']} the row reads {now['row']!r} and the head {now['head']}")
                    else:
                        cleared = True
            if len(glass_seen) > 1:
                evidence.add("glass")
        finally:   # as found, whatever broke the step
            try:
                if source_end in self.tags.before and not self.tags.restore([source_end]):
                    faults.append("the source's definition of before was not restored")
                if raised and not cleared and not self.skip_write:
                    got, _t = seen()
                    if got != lamps["met"]:
                        self.tags.set({step["tag"]: int(time.time() * 1000)})
                        ok, now = self.wait(page, state(lamps["met"], False), 12)
                        notes.append(f"the latch cleared by an import of ilk/resetAt: the row reads {now['row']!r}")
                        if not ok:
                            faults.append(f"the trip is still latched after an import of ilk/resetAt: {now}")
                if reset_end in self.tags.before:
                    if not self.tags.restore([reset_end]):
                        faults.append("ilk/resetAt was not restored to its definition of before")
                    elif raised:
                        page.wait_for_timeout(2000)
                        ok, now = state(lamps["met"], False)()
                        if not ok:
                            faults.append(f"after ilk/resetAt was put back the row reads {now['row']!r}: latched again")
                            # clear once more and read the latch again: a trip left latched is a state left behind
                            if not self.skip_write:
                                self.tags.set({step["tag"]: int(time.time() * 1000)})
                                ok, now = self.wait(page, state(lamps["met"], False), 12)
                                if not ok:
                                    why = (f"the trip is still latched (the row reads {now['row']!r}) after ilk/resetAt "
                                           f"was put back and cleared once more")
                                    faults.append(why)
                                    self.tags.unrestored.append({"tag": reset_end, "why": why})
                                else:
                                    notes.append("the latch cleared once more by an import of ilk/resetAt; the tag "
                                                 "keeps the time of that clear")
            except Exception as e:
                faults.append(f"the step could not put back what it changed: {type(e).__name__}: {str(e)[:120]}")
        r, v = self.tags.value(step["source"])
        if r:
            tag_seen["source (before, after the put-back)"] = [rest, v]
            if not same(rest, v):
                faults.append(f"the source held {rest} before the step and holds {v} after the put-back")
        if not evidence:
            faults.append("neither the glass nor a tag showed the trip: nothing was proven")
        self.row(step, ", then ".join(done) or "nothing", expected, glass_seen, tag_seen, not faults, evidence,
                 "; ".join(faults + notes), page)

    # -- A ----------------------------------------------------------------------------
    def belongs(self, row: str, step: dict) -> bool:
        """An alarm row is the device's: it carries the identifier as a whole word (P-1 is not P-10),
        or a source path of the device model."""
        import faceplates
        if re.search(r"(?<![\w-])" + re.escape(step["device"]) + r"(?![\w-])", row):
            return True
        return any(c and c in row for c in (faceplates.source_core(s) for s in step.get("sources") or []))

    def alarm(self, step: dict) -> None:
        """An alarm raised and cleared without the plant's logic. The row carries the write path of the
        acknowledgement (W7 in the faceplate's table, W8 in the alarm menu); the limit a step by limit
        writes is path W4, proven by group C. The acknowledgement is read back: under stock rendering
        the row of the faceplate's table must read acknowledged afterwards, under module rendering the
        alert of the menu (`glass.ack_alarm`). What the step changed is put back whatever happens."""
        page = self.signed
        tab = step.get("tab") or "Alarms"
        right, why = self.open(page, step, tab)
        expected = ("the Alarms tab counts and lists one more alarm of the device, the frame's count and list "
                    "show it, it is acknowledged and reads so, and after the clear both counts are as before")
        if right is None:
            self.row(step, "nothing", expected, why, None, False, set(), why, page)
            return
        faults, notes = self.stale(page, step), []
        tab0, frame0 = self.g.tab_count(right), self.g.frame_alarm_count(page)
        glass_seen = {"alarms tab": [tab0], "frame count": [frame0]}
        tag_seen, done = {}, "nothing"
        restore = None
        readable0, held0 = self.tags.value(step["tag"])
        try:
            if faults:
                pass
            elif step["by"] == "limit":
                value = self.g.big_value(page)
                field, disabled = self.g.dock_field(page, step["field"])
                if value is None or field is None or disabled:
                    faults.append(f"value {value}, the field {step['field']} "
                                  f"{'not shown' if field is None else 'disabled' if disabled else 'ready'}")
                else:
                    original = self.g.field_number(field)
                    margin = max(abs(value) * 0.5, 0.05)
                    target = round(value - margin if step["above"] else value + margin, decimals_of(step["format"]))
                    text = number_format(target, step["format"]).replace(",", "")

                    def restore():
                        r, _w = self.open(page, step, tab)
                        f, _d = self.g.dock_field(page, step["field"]) if r is not None else (None, None)
                        if f is not None:
                            self.g.type_into(f, number_format(original, step["format"]).replace(",", ""))
                        return f is not None
                    self.g.type_into(field, text)
                    done = f"{step['field']} {text} typed beside the value {value:g} (it held {original:g})"
            else:
                def restore():
                    self.tags.put(step["tag"], step["clear"])
                    return True
                self.tags.put(step["tag"], step["raise"])
                done = f"the scene's raise document imported on {step['tag'].split(']', 1)[-1]}"
            if not faults:
                ok, now = self.wait(page, lambda: (self.g.tab_count(right) == (tab0 or 0) + 1, self.g.tab_count(right)), 12)
                glass_seen["alarms tab"].append(now)
                if not ok:
                    faults.append(f"the Alarms tab counted {tab0}, then {now}")
            if not faults:
                import faceplates
                self.g.tab(right, "Alarms")
                rows = None
                for _ in range(20):
                    page.wait_for_timeout(500)
                    rows = faceplates.alarm_rows(page, right)
                    if rows and len(rows) == (tab0 or 0) + 1:
                        break
                glass_seen["alarm rows"] = rows
                if not rows or len(rows) != (tab0 or 0) + 1:
                    faults.append(f"the Alarms tab lists {None if rows is None else len(rows)} rows")
                elif not all(self.belongs(r, step) or (step.get("alarm") and step["alarm"] in r) for r in rows):
                    faults.append("the Alarms tab lists a row of another device")
                for s in step.get("symbols", []):
                    good, shown = self.read(page, s, expect_of(s["rule"], True))
                    glass_seen.setdefault("symbols", []).append(f"{s['symbol']}.{s['param']}: {shown}")
                    if not good:
                        faults.append(f"the symbol {s['symbol']} does not show the alarm's member: {shown}")
                frame1 = self.g.frame_alarm_count(page)
                glass_seen["frame count"].append(frame1)
                if frame0 is None or frame1 != frame0 + 1:
                    faults.append(f"the frame counted {frame0}, then {frame1}")
                acked = self.acknowledge(page, step)
                notes.append(f"acknowledged in the {'alarm menu' if self.module else 'faceplate table'}: {acked}")
                if not acked:
                    faults.append("the alarm was not acknowledged")
                elif not self.module:
                    # read back: the table still lists the alarm, and no row of it reads unacknowledged
                    # ("Active, Unacknowledged" is the text `glass.ack_alarm` finds the row by, GF-40)
                    states = None
                    for _ in range(16):
                        page.wait_for_timeout(500)
                        states = faceplates.alarm_rows(page, self.g.dock(page, "right"))
                        if states and not any(UNACKED_ROW in s for s in states):
                            break
                    glass_seen["after the acknowledgement"] = states
                    if not states or len(states) != len(rows or []) or any(UNACKED_ROW in s for s in states):
                        faults.append(f"after Acknowledge the faceplate's table reads {states}")
                menu = self.g.alarm_menu_rows(page, self.module)
                listed = [r for r in (menu or []) if self.belongs(r, step) or (step.get("alarm") and step["alarm"] in r)]
                glass_seen["frame list"] = f"{len(listed)} of {None if menu is None else len(menu)} rows are the device's"
                if not listed:
                    faults.append("the frame's alarm menu lists no row of the device")
        finally:
            if restore is not None:
                try:
                    put_back = restore()
                    if step["by"] == "scene":
                        end = self.tags.source(step["tag"])[0]
                        if end in self.tags.before and not self.tags.restore([end]):
                            faults.append(f"the definition of before was not restored: "
                                          f"{[u['why'] for u in self.tags.unrestored if u['tag'] == end]}")
                    right = self.g.dock(page, "right")
                    if not self.g.dock_open(page):
                        right, _w = self.open(page, step, tab)
                    if right is not None:
                        ok, now = self.wait(page, lambda: (self.g.tab_count(right) == tab0, self.g.tab_count(right)), 14)
                        glass_seen["alarms tab"].append(now)
                        frame2 = None
                        for _ in range(10):
                            frame2 = self.g.frame_alarm_count(page)
                            if frame2 == frame0:
                                break
                            page.wait_for_timeout(500)
                        glass_seen["frame count"].append(frame2)
                        if not ok or frame2 != frame0 or not put_back:
                            faults.append(f"after the clear the Alarms tab counts {now} (before {tab0}) and the frame "
                                          f"{frame2} (before {frame0})")
                    else:
                        faults.append("the faceplate did not open again after the clear")
                except Exception as e:
                    faults.append(f"the step could not put back what it changed: {type(e).__name__}: {str(e)[:120]}")
        # the tag after the put-back, against what it held before the step: evidence that nothing is left
        r, v = self.tags.value(step["tag"])
        if r and readable0:
            tag_seen = {step["tag"].split("]", 1)[-1] + " (before the step, after the put-back)": [held0, v]}
            if not same(held0, v):
                faults.append(f"the tag held {held0} before the step and holds {v} after the put-back")
        self.row(step, done, expected, glass_seen, tag_seen, not faults, {"glass"} | ({"tag"} if r and readable0 else set()),
                 "; ".join(faults + notes), page, extra={"path": step.get("ack"), "wrote": step.get("path")})

    # -- P ----------------------------------------------------------------------------
    def parity(self, step: dict, expect_from: dict | None = None) -> list[dict]:
        """One scene: its values imported, then every reading of the scene against the glass. With
        `expect_from` (the negative control) the readings expected are another scene's."""
        page = self.signed
        reply = self.tags.set(step["set"])
        time.sleep(2.5)
        held = {p: self.tags.value(p) for p in step["set"]}
        readings = (expect_from or step)["readings"]
        # what the other scene expects of each reading: a reading both scenes expect alike cannot fail,
        # so it fails (the plan lists such a reading as not checked; a plan written by hand may not)
        other = {(r["route"], r["symbol"], r["param"]): r["expect"] for s in self.plan["steps"]
                 if s.get("type") == "parity" and s.get("scene") != (expect_from or step).get("scene")
                 for r in s["readings"]}
        rows, route = [], None
        for r in readings:
            if r["route"] != route:
                route = r["route"]
                self.goto(page, route, fresh=True)
                self.g.close_faceplate(page)
            ok, seen = self.wait(page, lambda r=r: self.read(page, r, r["expect"]), 6)
            readable, got = held[r["source"]]
            arrived = readable and same(got, step["set"][r["source"]])
            if other.get((r["route"], r["symbol"], r["param"])) == r["expect"]:
                rows.append(self.row(step, f"scene {step['scene']}", f"{r['symbol']}.{r['param']}", seen, {}, False,
                                     {"glass"}, "both scenes expect the same of this reading, so the check could "
                                     "not fail: it proves nothing", page, sid=r["id"]))
                continue
            want = r["expect"].get("line") or r["expect"].get("pattern") or json.dumps(
                {k: v for k, v in r["expect"].items()})
            rows.append(self.row(step, f"scene {step['scene']}: {r['source'].split(']', 1)[-1]} imported as "
                                       f"{step['set'][r['source']]}",
                                 f"{r['symbol']}.{r['param']} shows {want}", seen,
                                 {r["source"].split("]", 1)[-1]: got} if readable else {},
                                 ok and (arrived or expect_from is not None),
                                 {"glass"} | ({"tag"} if readable else set()),
                                 "" if arrived else f"the import did not arrive ({reply.get('missing')}, {reply.get('failed')})",
                                 page, sid=r["id"]))
        return rows

    # -- the walk ---------------------------------------------------------------------
    STEP_TYPES = {"route": "route", "open": "open_step", "trend-page": "trend_page", "trend-tab": "trend_tab",
                  "states": "states", "entry": "entry", "pulse": "pulse", "fault-reset": "fault_reset",
                  "refusal": "refusal", "alarm": "alarm", "parity": "parity", "page-pulse": "page_pulse",
                  "page-refusal": "page_refusal", "trip": "trip"}

    def run_step(self, step: dict) -> None:
        """One step, by its type. A tag read the gateway failed during the step fails every row of the
        step: a tag that could not be read is no evidence, and must not pass as a tag without a value."""
        first_row, first_error = len(self.rows), len(self.tags.errors)
        method = self.STEP_TYPES.get(step["type"])
        if method is None:
            self.row(step, "nothing", "", None, None, False, set(), f"a step of unknown type {step['type']!r}")
        else:
            getattr(self, method)(step)
        errors = self.tags.errors[first_error:]
        if errors:
            for r in self.rows[first_row:]:
                r["ok"] = False
                r["detail"] = "; ".join(filter(None, [r["detail"], f"{len(errors)} tag reads failed, the first on "
                                                      f"{errors[0]['tag']}: {errors[0]['error']}"]))

    def walk(self) -> list[str]:
        not_run = []
        try:
            for step in self.plan["steps"]:
                if step.get("during"):
                    if not self.signed_in:
                        not_run.append(step["id"])
                    continue   # run by the step that holds its state (`fault_reset`, `entry`)
                if step.get("session") == "signed" and not self.signed_in:
                    not_run.append(step["id"])
                    continue
                try:
                    if self.before_step is not None:
                        self.before_step(step)
                    self.run_step(step)
                except Exception as e:   # a step that broke is a failed step, with what broke it
                    self.row(step, "the step broke", "", None, None, False, set(), f"{type(e).__name__}: {str(e)[:300]}",
                             self.page_for(step))
        finally:   # the definitions of before, for every tag a scene changed, also when the walk is interrupted
            try:
                self.restored = self.tags.restore()
            except Exception as e:
                self.tags.unrestored.append({"tag": "*", "why": f"restore failed: {type(e).__name__}: {str(e)[:200]}"})
        return not_run


def unaccounted(plan: dict, rows: list[dict], not_run: list[str]) -> list[dict]:
    """The steps of the plan that left neither a row nor an entry in `not_run`, each with why that can
    be. A plan is data a person may overrule, and a refusal that another step holds (`during`) is run
    by that step alone: with the holder deleted, or broken before it reached its refusal, the refusal
    left no row and the result counted one step fewer without a word (2026-10-11). A parity step is
    accounted for by a row for each of its readings, or by the row of a step that broke."""
    have = {r["id"] for r in rows}
    ids = {s["id"] for s in plan.get("steps", [])}
    out = []
    for s in plan.get("steps", []):
        if s["id"] in have or s["id"] in not_run:
            continue
        if s.get("type") == "parity" and s.get("readings") and all(x["id"] in have for x in s["readings"]):
            continue
        if s.get("during"):
            why = (f"a refusal held during {s['during']}, " + (
                "which ran and did not reach it" if s["during"] in have else
                "which was not run" if s["during"] in not_run else
                "which the plan does not hold" if s["during"] not in ids else "which left no row"))
        else:
            why = "the step left no row"
        out.append({"id": s["id"], "why": why})
    return out


def summarise(plan: dict, rows: list[dict], not_run: list[str], signed_in: bool, restored: list[str],
              tags: Tags | None = None, login_given: bool = False, why: str = "") -> dict:
    """The result of a run. `ok` is every row passing, with nothing left to restore and every step of
    the plan accounted for (`missing` lists a step that left neither a row nor an entry in `not_run`:
    `unaccounted`). `verdict` tells a full walk from a read only one: with nobody signed in the write
    groups C, A and P did not run, which is no pass of them; and a login that was given and did not
    sign in is a failure."""
    counts = {g: {"rows": 0, "passed": 0, "failed": 0} for g in GROUPS}
    evidence: dict[str, dict[str, int]] = {g: {} for g in GROUPS}
    for r in rows:
        c = counts[r["group"]]
        c["rows"] += 1
        c["passed" if r["ok"] else "failed"] += 1
        evidence[r["group"]][r["evidence"]] = evidence[r["group"]].get(r["evidence"], 0) + 1
    unrestored = list(tags.unrestored) if tags else []
    left = sorted(tags.before) if tags else []
    missing = unaccounted(plan, rows, not_run)
    ok = (all(r["ok"] for r in rows) and bool(rows) and not unrestored and not left and not missing
          and not (login_given and not signed_in))
    refusals: dict[str, int] = {}
    for r in rows:
        if r["group"] == "R":
            refusals[r.get("refused_by", "")] = refusals.get(r.get("refused_by", ""), 0) + 1
    note = ""
    if login_given and not signed_in:
        note = "the test login was given and did not sign in: the write groups C, A and P did not run"
        if why:
            note += f" ({why})"
    elif not signed_in:
        note = ("nobody signed in (no test login, NEEDS N-COB-9): the read only groups N, D and T and the "
                "refusals R ran; C, A and P did not, and this is no pass of them")
    return {"schema": RESULT_SCHEMA, "render": plan.get("render"), "signed_in": signed_in, "ok": ok,
            "verdict": "FAIL" if not ok else "PASS" if signed_in else "PASS, READ ONLY",
            "counts": counts, "evidence": evidence, "refused_by": refusals, "plan_steps": plan.get("counts"),
            "not_run": not_run, "missing": missing, "note": note, "restored": restored, "unrestored": unrestored + [
                {"tag": t, "why": "its definition of before was never imported back"} for t in left
                if not any(u["tag"] == t for u in unrestored)],
            "tag_read_errors": list(tags.errors) if tags else [], "rows": rows}


def run(plan: dict, base: str, out: Path, login: dict | None = None, before_step=None) -> dict:
    """Walk a plan against a project on the gateway. The first session signs in with `login` and runs
    N, D, T, C, A and P; the second, with nobody signed in, runs R. Without a login the read only
    groups and R run in the second session, and the result says so. `before_step`, when given, is
    called with each step before it runs: a simulated plant that drifts while it is left alone is
    returned to its initial state there (`wtp_suite.keep_initial`)."""
    import glass
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    tags = Tags(allowed_folders(plan))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            signed = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
            signed_in = glass.sign_in(signed, base.rstrip("/"), login) if login else False
            anon = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
            w = Walk(plan, base, out, signed, anon, tags, signed_in)
            w.before_step = before_step
            not_run = w.walk()
        finally:
            browser.close()
    rep = summarise(plan, w.rows, not_run, signed_in, w.restored, tags, login_given=login is not None,
                    why=glass.SIGN_IN_WHY)
    (out / "walk.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    return rep


# What the row of a capability step must name when its write was skipped (the controls `capability`,
# `entry` and `pulse`): the words of the fault each step type writes when what it wrote did not show.
SKIPPED_BECAUSE = {"states": ", expected ", "entry": "after ", "pulse": "no effect on ",
                   "pulse, no effect named": "was not read true"}


def control_verdict(name: str, step: dict, rows: list[dict], because=None) -> dict:
    """One negative control judged from the rows its step wrote: it holds when the step's row failed
    and, with `because` (a text, or several), the row's detail names every one of them. A control
    that fails for another reason (a faceplate that did not open, a button found disabled, a stale
    "Refused") proves nothing of the check it stands for, so it does not hold."""
    reasons = [because] if isinstance(because, str) else list(because or [])
    r = next((x for x in rows if x["id"] == step["id"]), rows[0] if rows else None)
    failed = r is not None and not r["ok"]
    for_reason = failed and all(b in r["detail"] for b in reasons)
    return {"control": name, "step": step["id"], "ok": bool(for_reason), "row_ok": None if r is None else r["ok"],
            "detail": "" if r is None else r["detail"], **({"must_name": because} if reasons else {})}


def route_controls(steps: list[dict], shows) -> list[tuple]:
    """The two controls of a navigation step, each as (name, the step to run, what its failure must
    name, why it does not apply). `route`: a menu step made to begin on its own route, so that the
    entry moves nothing. `route-content`: a route step told to expect what belongs to another page,
    the symbol another route's step names where this page does not show it (`shows(route, text)`
    answers what the glass shows now) and the component another page must hold (`holds`): the address
    and the top bar are right, and the step must fail on the content alone."""
    routes = [s for s in steps if s.get("type") == "route"]
    menu = next((s for s in routes if s.get("via") == "menu"), None)
    out = [("route", {**menu, "from": menu["route"]} if menu else None,
            "the step began on the route itself", "the plan has no route step by the navigation menu")]
    target = menu or (routes[0] if routes else None)
    step, reasons = None, []
    if target:
        step = dict(target)
        symbol = next((s["symbol"] for s in routes if s.get("symbol") and s["route"] != target["route"]
                       and s["symbol"] != target.get("symbol") and not shows(target["route"], s["symbol"])), None)
        holds = next((s["holds"] for s in routes if s.get("holds") and s["holds"] != target.get("holds")), None)
        if symbol:
            step["symbol"] = symbol
            reasons.append("no symbol of the page shows")
        if holds:
            step["holds"] = holds
            reasons.append("the page holds no")
    out.append(("route-content", step if reasons else None, tuple(reasons),
                "the plan has no other route whose symbol or component this page lacks"))
    return out


def selftest(plan: dict, base: str, out: Path, login: dict | None) -> dict:
    """The negative controls, against a live project. Each runs a check where it must fail, through
    the code of the real check, and fails the selftest when the check passes, or fails for another
    reason than the one it stands for (`control_verdict`):

      route           a menu step that begins on its own route: the entry moves nothing;
      route-content   a route step that expects another page's symbol or component: the address and
                      the title are right, the content is not;
      parity          scene 1 imported and scene 2 expected: every reading must fail;
      refusal         a refusal step in the signed in session, no crafted action: its control is
                      enabled, so it must fail on the disabled state;
      refusal-write   a refusal step of an entry in the signed in session, the crafted entry made:
                      the session may write, so the tag differs afterwards and the step must fail on the
                      tag comparison (the walk types the value of before back);
      capability      a `states` step whose click is skipped: neither glass nor tag changes;
      entry           an `entry` step whose typing is skipped: the field and the tag keep the value;
      entry-blind     an `entry` step no symbol or effect follows, written for real, with the tag reads
                      answering nothing: only the field typed into shows the value, so it must fail;
      pulse           a `pulse` step whose press is skipped: no effect follows.

    A control the plan has no step for is reported as not applicable, and does not fail the selftest.
    Everything a control changed is put back, also when one breaks."""
    import glass
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    controls = []
    if not login:
        rep = {"ok": False, "controls": [], "note": "no test login: the negative controls need the signed in session"}
        (out / "selftest.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
        return rep
    tags = Tags(allowed_folders(plan))
    steps = plan["steps"]

    def absent(name: str, why: str) -> None:
        controls.append({"control": name, "ok": None, "note": f"not applicable: {why}"})

    def must_fail(name: str, w: Walk, step: dict, call, because=None) -> None:
        """Run one step where it must fail; with `because`, its failure must name that reason."""
        n = len(w.rows)
        try:
            call()
        except Exception as e:
            controls.append({"control": name, "step": step["id"], "ok": False, "detail": f"the control broke: {type(e).__name__}: {str(e)[:200]}"})
            return
        controls.append(control_verdict(name, step, w.rows[n:], because))

    def put_back(tag: str, held: tuple, seconds: float = 12.0) -> bool:
        """Whether a tag a control wrote holds the value of before again. The write that puts a value
        back lands a moment after the field shows it, and a step whose tag reads are withheld cannot
        wait for it itself: on 2026-10-11 a control read the tag straight after its step, found the
        value of the control still there and reported a put back that had in fact been made. So the
        tag is read until it agrees, for a bounded time."""
        deadline = time.time() + seconds
        while True:
            now = tags.value(tag)
            if held[0] and now[0] and same(held[1], now[1]):
                return True
            if time.time() >= deadline:
                return False
            time.sleep(0.5)

    signed_in = False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        w = None
        try:
            signed = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
            signed_in = glass.sign_in(signed, base.rstrip("/"), login)
            w = Walk(plan, base, out, signed, signed, tags, signed_in)   # both roles in the signed in session

            def shows(route: str, text: str) -> bool:
                w.goto(signed, route)
                glass.close_faceplate(signed)
                return glass.find_symbol(signed, text) is not None
            for name, step, because, why in route_controls(steps, shows):
                if step is None:
                    absent(name, why)
                    continue
                w.goto(signed, step["route"])   # on the route itself: only then does a menu step go to its `from`
                must_fail(name, w, step, lambda step=step: w.route(step), because)

            scenes = [s for s in steps if s["type"] == "parity"]
            if len(scenes) == 2:
                a, b = scenes
                differ = [x["id"] for x, y in zip(a["readings"], b["readings"]) if x["expect"] != y["expect"]]
                try:
                    rows = w.parity(a, expect_from=b)
                finally:
                    w.tags.restore()
                failed = [r["id"] for r in rows if not r["ok"]]
                # the rows carry the ids of scene 2's readings: a differing reading that passed is a check that cannot fail
                passed_wrongly = [y["id"] for x, y in zip(a["readings"], b["readings"])
                                  if x["expect"] != y["expect"] and y["id"] not in failed]
                arrived = all(r["tag"] for r in rows)
                controls.append({"control": "parity", "ok": bool(differ) and len(differ) == len(rows) and not passed_wrongly and arrived,
                                 "readings": len(rows), "differ": len(differ), "failed": len(failed),
                                 "passed_wrongly": passed_wrongly, "scene_arrived": arrived})
            else:
                absent("parity", "the plan has no two parity scenes (no symbol parameter is bound to a tag the walk can set)")

            mirror = next((s for s in steps if s["type"] == "refusal" and not s.get("during")), None)
            if mirror:
                w.no_crafted = True
                must_fail("refusal", w, mirror, lambda: w.refusal(mirror, page=signed), "enabled")
                w.no_crafted = False
            else:
                absent("refusal", "the plan has no refusal step")

            written = next((s for s in steps if s["type"] == "refusal" and "field" in s and not s.get("during")), None)
            if written:
                readable, held = tags.value(written["tag"])
                w.force_crafted = True
                try:
                    must_fail("refusal-write", w, written, lambda: w.refusal(written, page=signed), "the tag went from")
                finally:
                    w.force_crafted = False
                    # the crafted entry was a real write in this session: the value of before typed back
                    r2, now = tags.value(written["tag"])
                    if readable and r2 and not same(held, now):
                        right, _why = w.open(signed, written, written["tab"])
                        field, _d = glass.dock_field(signed, written["field"]) if right is not None else (None, None)
                        if field is not None:
                            glass.type_into(field, number_format(float(held), written["format"]).replace(",", ""))
                            signed.wait_for_timeout(2500)
                    controls[-1]["put_back"] = put_back(written["tag"], (readable, held))
                    controls[-1]["ok"] = controls[-1]["ok"] and controls[-1]["put_back"]
            else:
                absent("refusal-write", "the plan has no refusal step of an entry outside another step")

            # each for its own reason: the state not shown after the button, the value not held after the
            # entry, no effect of the pulse; any other failure of the step is no proof of the check
            for name, kind in (("capability", "states"), ("entry", "entry"), ("pulse", "pulse")):
                cap = next((s for s in steps if s["type"] == kind), None)
                if cap:
                    w.skip_write = True
                    try:
                        must_fail(name, w, cap, lambda cap=cap: w.run_step(cap),
                                  SKIPPED_BECAUSE["pulse, no effect named" if kind == "pulse" and not cap.get("effects") else kind])
                    finally:
                        w.skip_write = False
                else:
                    absent(name, f"the plan has no `{kind}` step")

            blind = next((s for s in steps if s["type"] == "entry" and not s["symbols"] and not s["effects"]
                          and not s.get("requires")), None)
            if blind:
                real = tags.value
                held = real(blind["tag"])
                tags.value = lambda path: (False, None)   # the evidence of the tag withheld
                w.no_crafted = True                       # no refusal held inside the step
                try:
                    must_fail("entry-blind", w, blind, lambda: w.run_step(blind), "only the field typed into")
                finally:
                    tags.value = real
                    w.no_crafted = False
                controls[-1]["put_back"] = put_back(blind["tag"], held)
                controls[-1]["ok"] = controls[-1]["ok"] and controls[-1]["put_back"]
            else:
                absent("entry-blind", "the plan has no `entry` step without a symbol, an effect or a condition")
        finally:
            left = tags.restore()
            browser.close()
    applicable = [c for c in controls if c["ok"] is not None]
    rep = {"ok": bool(signed_in and applicable and all(c["ok"] for c in applicable) and not tags.unrestored and not tags.before),
           "signed_in": signed_in, "controls": controls, "restored": left, "unrestored": tags.unrestored,
           "rows": w.rows if w else []}
    (out / "selftest.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    return rep
