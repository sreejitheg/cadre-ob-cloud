"""The functional check of the showcase project (wiki page 15): a clean render is not a working page.

On every page of `cadre_hmi_showcase`, in a fresh Perspective session (GF-10), the check
  * switches the Live simulation of each card off, so that nothing but the editors changes a component;
  * changes at least one editor of each input kind the page has (dropdown, toggle, numeric field, text field and the
    preset dropdown of an array property), through the browser as a user does, and asserts that the component's rendered
    DOM changed (its attributes, text and shadow tree, and its box); a property that draws nothing in the state the card
    holds (a readout size with no readout) is passed over for the next property of the kind, and a kind that no
    property changes is a failure;
  * clicks each component that has events and asserts that a line appears in its event log (`log_<card>`).

The model of the project (pages, cards, editors by kind, events) is the file `tools/hmi/showcase.py --write-descriptor DIR`
writes (`showcase-model.json`); the DOM ids are the node names (`meta.domId`).

Usage (Playwright for Python and the installed Chrome):
    python tools/compare/showcase_check.py --base http://localhost:8088/data/perspective/client/cadre_hmi_showcase
        --model workspace/showcase/showcase-model.json --out workspace/showcase/check [--route /charts]
Exit 1 when any page fails.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

SNAP = """(id) => {
  const el = document.getElementById(id); if (!el) return null;
  const ser = (n) => {
    if (n.nodeType === 3) return n.textContent;
    if (n.nodeType !== 1) return '';
    let s = '<' + n.tagName + ' ' + [...n.attributes].filter(a => a.name !== 'style' || true).map(a => a.name + '=' + a.value).join(' ') + '>';
    if (n.shadowRoot) s += '#' + [...n.shadowRoot.childNodes].map(ser).join('');
    return s + [...n.childNodes].map(ser).join('');
  };
  const r = el.getBoundingClientRect();
  return ser(el) + '|' + Math.round(r.width) + 'x' + Math.round(r.height);
}"""
KINDS = ("enum", "bool", "number", "text", "preset")
EDIT_TEXT = "QA-7"
CLICKS = ("button", "[role=button]", "[role=switch]", "a", "li", "input", "[tabindex]")
CLICKS_EACH = 5   # the matches of a selector tried, in order, until one writes a log line


def snap(page, ids) -> str | None:
    """The rendered state of a card's component (and the elements it acts on): one string, None when the component is absent."""
    parts = [page.evaluate(SNAP, i) for i in ([ids] if isinstance(ids, str) else ids)]
    return None if parts[0] is None else "\n".join(p or "" for p in parts)


def stable(page, ids, pause: int = 700) -> bool:
    a = snap(page, ids)
    page.wait_for_timeout(pause)
    return a is not None and a == snap(page, ids)


# A value that draws only in a state of its card: the editors to set first, (property, kind, value to choose).
NEEDS = {"progressValue": [("progress", "bool", None), ("progressMode", "enum", "determinate")]}


def edit(page, cid: str, prop: str, kind: str, want: str | None = None) -> str | None:
    """Change one editor as a user would; the value it was set to, or None when the editor could not be driven."""
    eid = f"e_{cid}_{prop}"
    loc = page.locator(f"#{eid}")
    if not loc.count():
        return None
    loc.first.scroll_into_view_if_needed(timeout=5000)
    if kind == "bool":
        loc.first.click(timeout=5000)
        return "toggled"
    if kind in ("enum", "preset"):
        loc.first.click(timeout=5000)
        page.wait_for_timeout(300)
        opts = page.locator(".ia_dropdown__option")
        n = opts.count()
        pick = None
        for i in range(n):
            if want is not None:
                if opts.nth(i).inner_text().strip() == want:
                    pick = i
                    break
            elif "selected" not in (opts.nth(i).get_attribute("class") or "").split():
                pick = i
                break
        if pick is None:
            page.keyboard.press("Escape")
            return None
        label = opts.nth(pick).inner_text()
        opts.nth(pick).click(timeout=5000)
        return label
    field = page.locator(f"#{eid} input") if kind == "number" else loc
    inner = field.first if field.count() else loc.first
    if kind == "number":   # a numeric field is read only until it is clicked
        loc.first.click(timeout=5000)
        page.wait_for_timeout(200)
        inner.press("Control+a")
    old = inner.input_value()
    new = EDIT_TEXT if kind == "text" else str(7 if old.strip() != "7" else 8)
    if kind == "text" and old == EDIT_TEXT:
        new = "QA-8"
    inner.fill(new, timeout=5000)
    inner.press("Enter")
    page.keyboard.press("Tab")
    return new


def log_text(page, cid: str) -> str:
    loc = page.locator(f"#log_{cid}")
    return loc.first.inner_text() if loc.count() else ""


def fire(page, cid: str) -> str | None:
    """Click the component until a line stands in its log; the way that did it, or None."""
    loc = page.locator(f"#{cid}")
    loc.first.scroll_into_view_if_needed(timeout=5000)
    before = log_text(page, cid)
    tries = [("centre", lambda: loc.first.click(timeout=4000))]
    for sel in CLICKS:
        for k in range(CLICKS_EACH):
            tries.append((f"{sel}[{k}]", lambda sel=sel, k=k: page.locator(f"#{cid} >> {sel}").nth(k).click(timeout=2500, force=True)))
    for sel in ("[role=switch]", "button", "[tabindex]"):   # a press and hold switch answers the keyboard, not a click
        for k in range(2):
            tries.append((f"{sel}[{k}] with Space", lambda sel=sel, k=k: (
                page.locator(f"#{cid} >> {sel}").nth(k).focus(timeout=2000), page.keyboard.press("Space"))))
    for name, act in tries:
        try:
            act()
        except Exception:
            continue
        page.wait_for_timeout(700)
        now = log_text(page, cid)
        if now != before and not now.startswith("No event"):
            return name
    return None


def check_page(browser, base: str, page_model: dict, width: int, height: int) -> dict:
    ctx = browser.new_context(viewport={"width": width, "height": height})
    page = ctx.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)[:200]))
    route = page_model["route"]
    page.goto(base.rstrip("/") + route, wait_until="networkidle", timeout=90000)
    first = next(iter(page_model["cards"]))
    page.wait_for_selector(f"#{first}", timeout=60000)
    page.wait_for_timeout(5000)
    cards = page_model["cards"]
    for cid, card in cards.items():   # Live off: nothing but the editors moves a component
        if card["live"] and page.locator(f"#live_{cid}").count():
            page.locator(f"#live_{cid}").first.scroll_into_view_if_needed(timeout=5000)
            page.locator(f"#live_{cid}").first.click(timeout=5000)
    page.wait_for_timeout(800)
    result = {"route": route, "kinds": {}, "events": {}, "errors": errors}
    # the events first, while every card holds the state it was drawn in (an editor may take a row or an action away)
    for cid, card in cards.items():
        if not card["events"]:
            continue
        how = fire(page, cid)
        result["events"][cid] = {"ok": how is not None, "how": how, "events": card["events"],
                                 "log": log_text(page, cid)[:200]}
    for kind in KINDS:
        cands = [(cid, p) for cid, card in cards.items() for p, e in card["editors"].items() if e["kind"] == kind]
        if not cands:
            continue
        seen: dict[str, int] = {}
        ranked = []
        for i, (cid, prop) in enumerate(cands):   # each property name once before any is tried on a second card
            ranked.append((cards[cid]["editors"][prop]["live"], seen.get(prop, 0), i, cid, prop))
            seen[prop] = seen.get(prop, 0) + 1
        cands = [(cid, prop) for _l, _r, _i, cid, prop in sorted(ranked)]   # properties the simulation moves last
        tried = []
        for cid, prop in cands[:30]:
            watch = cards[cid].get("watch", [cid])
            if not stable(page, watch):
                tried.append({"card": cid, "prop": prop, "note": "the component changes by itself"})
                continue
            before = snap(page, watch)
            try:
                value = edit(page, cid, prop, kind)
            except Exception as e:
                tried.append({"card": cid, "prop": prop, "note": f"editor not driven: {str(e)[:80]}"})
                page.keyboard.press("Escape")
                continue
            if value is None:
                tried.append({"card": cid, "prop": prop, "note": "editor not driven"})
                continue
            page.wait_for_timeout(900)
            after = snap(page, watch)
            changed = before != after
            if not changed and prop in NEEDS and all(q in cards[cid]["editors"] for q, _k, _v in NEEDS[prop]):
                for q, qk, want in NEEDS[prop]:   # the state in which the value draws
                    edit(page, cid, q, qk, want)
                    page.wait_for_timeout(500)
                before = snap(page, watch)
                value = edit(page, cid, prop, kind)
                page.wait_for_timeout(900)
                after = snap(page, watch)
                changed = before != after
                value = f"{value} after {', '.join(q for q, _k, _v in NEEDS[prop])}"
            tried.append({"card": cid, "prop": prop, "value": value, "changed": changed})
            if changed:
                break
        result["kinds"][kind] = {"ok": bool(tried and tried[-1].get("changed")), "tried": tried}
    result["ok"] = (all(k["ok"] for k in result["kinds"].values()) and bool(result["kinds"]) and not errors
                    and all(e["ok"] for e in result["events"].values()))
    ctx.close()
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--route", action="append", default=[], help="only these routes (default: every page)")
    ap.add_argument("--viewport", default="1600x900")
    a = ap.parse_args()
    width, height = (int(n) for n in a.viewport.lower().split("x"))
    model = json.loads(Path(a.model).read_text(encoding="utf-8"))
    from playwright.sync_api import sync_playwright
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for pg in model["pages"]:
            if a.route and pg["route"] not in a.route:
                continue
            t0 = time.time()
            r = check_page(browser, a.base, pg, width, height)
            results.append(r)
            kinds = " ".join(f"{k}={'ok' if v['ok'] else 'FAIL'}" for k, v in r["kinds"].items())
            ev = r["events"]
            print(f"{r['route']:12s} {'PASS' if r['ok'] else 'FAIL'}  {kinds}  events {sum(e['ok'] for e in ev.values())}/{len(ev)}"
                  f"  page errors {len(r['errors'])}  {time.time() - t0:.0f} s", flush=True)
            for cid, e in ev.items():
                if not e["ok"]:
                    print(f"    no log line after clicking {cid}")
            for k, v in r["kinds"].items():
                if not v["ok"]:
                    print(f"    {k}: {v['tried'][-3:]}")
        browser.close()
    ok = all(r["ok"] for r in results)
    totals = {"pages": len(results),
              "kindsChecked": sum(1 for r in results for v in r["kinds"].values() if v["ok"]),
              "eventsFired": sum(1 for r in results for e in r["events"].values() if e["ok"]),
              "eventsTotal": sum(len(r["events"]) for r in results)}
    (out / "showcase-check.json").write_text(json.dumps({"ok": ok, "totals": totals, "pages": results}, indent=1), encoding="utf-8")
    print("SHOWCASE CHECK", "PASS" if ok else "FAIL", json.dumps(totals))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
