"""Glass gates: what an operator would see and do on the deployed ASM project, checked with real input.

Generalised from the eng02 slice's Level 4 and Level 5 gate scripts (ARCH-WFB-01 revision B8 Table 109, WFBD-091),
rewritten in Python Playwright for ctig's `.venv`. Usage:

    glass_gates.py --base URL --model F --build DIR --window WxH --gates LIST [--raise-alarm] [--accepted-rows F]
                   [--navtable F] [--design F] [--allowed-root [provider]folder ...] [--settle S] [--only-routes LIST]
                   --out O

    --base URL        the project's client address, http://host:8088/data/perspective/client/<project>
    --model F         the ASM model (`cadre-hmi-asm-model/1`): the pages, devices, alarms and navigation table
    --build DIR       the `bridge/` folder of `asm_descriptors.py` (or its parent): the descriptors give each page's
                      columns, media and module symbols
    --navtable F      `wfb.migration.navtable/1`: an entry's own route joins the model's and the descriptors' in the routes gate
    --design F        `wfb.migration.project_design/1`: its `routes` table gives the routes of the navigation table; given, the plan lists the project's
                      routes only (built model pages, the design's, the descriptors', `/alerts`), COB-211
    --gates LIST      comma list of the gates to run, default all: search, zoom, menus, panels, readouts, colour,
                      sizes, fill, routes, symbols, alarm, ack, banner, lamps, testpanel
    --raise-alarm     allow the gates that write: raise alarms through their source tags (only with the simulation
                      on) and press the component test page's buttons. `alarm`, `ack`, `banner`, `lamps` and
                      `testpanel` need it and are skipped without it, and said so
    --accepted-rows F rows of the plan an earlier run accepted (a JSON list of "<gate>:<step action>")
    --allowed-root    a tag folder the raise may write into (default: the model's tag root)
    --settle S        a multiplier of every wait (default 1.0; the fake client page of the tests uses a small one)
    --only-routes LIST  comma list of page routes: the gates that visit page by page (readouts, colour, sizes, fill,
                      routes, symbols) visit only these, an empty list none; the routes gate also keeps every route that
                      no page descriptor draws (a frame page such as the alert list). The gates of the frame and the
                      project (search, zoom, menus, panels, the dock steps of fill) and the gates that write are
                      unchanged. For a sweep of the pages that changed, whose other pages an earlier sweep proved
                      (COB-192, COB-193)

The plan (`O/plan.json`) is written before any input. The test login reaches the acknowledgement gate through
`CADRE_TEST_LOGIN` (a path) and is never printed or written. The raise and its restore go through the walk's lane
(`walk_run.Tags` over ctig's `Gateway` class, with `CTIG_SRC` and the token variable the block prepares): the one
tag the plan names, under the allowed roots, put back whatever happens.

Input is a mouse, a keyboard, a wheel and, for the pinch, the browser's own gesture synthesis
(`Input.synthesizePinchGesture`): nothing sets a value or fires an event from script. The pages are read, never
written, apart from the one tag above.

Exit codes: 0 every gate passes; 2 a gate failed; 1 a fault.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from hmi import provenance  # noqa: E402
from hmi import screen  # noqa: E402
from hmi.screen import module_drawn  # noqa: E402
import glass  # noqa: E402  (the frame variant of a page: `glass.frame_variant`; the gates' own helpers stay in this file)

TOOL = "tools/compare/glass_gates.py"
GATES = ("search", "zoom", "menus", "panels", "readouts", "colour", "sizes", "fill", "routes", "symbols", "alarm", "ack",
         "banner", "lamps", "testpanel")
NEEDS_ALARM = ("alarm", "ack", "banner")
PAGE_GATES = ("readouts", "colour", "sizes", "fill", "routes", "symbols")   # page by page: `--only-routes` limits them (COB-192, COB-193)
WRITES = NEEDS_ALARM + ("lamps", "testpanel")      # the gates that write (an alarm tag, or the test page's buttons)
ALARMS_RAISED = 3                                  # the alarm gate raises up to this many, so Ack all has some left
ALERTS_ROUTE = "/alerts"                           # the library frame's alert list
ZOOM_STEPS = ["buttons", "ctrl_wheel_canvas", "ctrl_wheel_header", "ctrl_minus", "pinch_canvas", "pinch_header",
              "float", "ctrl_wheel_float", "ctrl_0", "dock"]
NO_MATCH = "No page, device or tag matches"
# The custom element each module kind draws (`module/components.json`, `module/tools/gen_module_assets.py`). The two valves
# are `obc-digital-valve` and `obc-analog-valve`: no element named `obc-valve` or `obc-analogvalve` exists, so a selector
# built from those names counted no valve and the readouts gate expected one device more than it found (COB-194).
MODULE_TAGS = {"pump": "obc-pump", "motor": "obc-motor", "fan": "obc-fan", "valve": "obc-digital-valve",
               "analogvalve": "obc-analog-valve", "filter": "obc-filter", "damper": "obc-damper", "switch": "obc-switch",
               "generator": "obc-indicator-generator"}
# A module-only kind (`screen.MODULE_ONLY`) is found by the element of its component.
MODULE_TAGS.update({kind: screen.module_element(ctype) for kind, ctype in screen.MODULE_ONLY.items()})
EQ_TOL = 4
TEST_ROUTE = "/component-test"                     # the library's component test page (`screen.py --component-test`)
# The ASM gates were written for the `asm` frame. The new frames (`--frame ob`, `--frame obasm`, wiki 04 sections 10 and 11) draw
# the head with the module's top bar, so the selectors that find its parts differ (`TOP_ICONS` has no SVG to find: the bar's
# icons are in a shadow root) and the head of the obasm frame is 132 px, not 84. A gate asks the page which frame it shows
# (`Session.frame`, `glass.frame_variant`: the structure of the top dock) and takes the variant; on the older frames every
# selector below is the one it was. The `ob` frame is not an ASM frame (no search field, tree, pivot, floating faceplate or
# banner dock: wiki 04 section 10), so the gates that exercise those parts are not run on it and say so.
ASM_ONLY = ("search", "zoom", "panels")


class Fault(Exception):
    """An input the command cannot work with: exit 1."""


# ---- the plan -------------------------------------------------------------------------------------------------
def origin_of(base: str) -> str:
    u = urlsplit(base)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise Fault(f"--base {base!r} is not an http address")
    return f"{u.scheme}://{u.netloc}"


def descriptors_of(build: Path) -> list[dict]:
    folder = build / "bridge" / "descriptors" if (build / "bridge").is_dir() else build / "descriptors"
    if not folder.is_dir():
        folder = build
    files = sorted(folder.glob("*.json"))
    docs = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    return [d for d in docs if d.get("schema") == "cadre-hmi-screen/1"]


def columns_of(desc: dict) -> list[dict]:
    """The readout columns of a descriptor: symbols of kind readout that share an x within EQ_TOL."""
    xs = sorted((s["x"], s["id"]) for s in desc.get("symbols", []) if s.get("kind") == "readout")
    groups: list[list] = []
    for x, sid in xs:
        if groups and x - groups[-1][0][0] <= EQ_TOL:
            groups[-1].append((x, sid))
        else:
            groups.append([(x, sid)])
    return [{"x": g[0][0], "count": len(g), "ids": [i for _, i in g]} for g in groups if len(g) > 1]


def alarm_sources(model: dict, n: int = ALARMS_RAISED) -> list[dict]:
    """The alarms the gates raise: the first n whose condition is one Boolean source tag. Each tag is
    `<tag root>/src/<variable>`, the memory tag the alarm's expression reads."""
    root = (model.get("tag_root") or "").rstrip("/")
    found: list[dict] = []
    for a in model.get("alarms", []):
        src = a.get("source") or ""
        if re.fullmatch(r"[A-Za-z0-9_]+", src) and a.get("node") and root:
            found.append({"alarm": a["tag"], "desc": a["desc"], "priority": a["priority"], "device": a.get("device"),
                          "node": a["node"], "tag": f"{root}/src/{src}", "raise": True, "clear": False})
            if len(found) == n:
                break
    return found


def alarm_source(model: dict) -> dict | None:
    return next(iter(alarm_sources(model, 1)), None)


def device_of(symbol: dict) -> str | None:
    """The device a symbol opens: its `device` (true means its own id) or its plain `faceplate` key."""
    dev = symbol.get("device")
    dev = symbol["id"] if dev is True else dev
    return dev or symbol.get("faceplate") or None


def testpage_plan(descriptors: list[dict]) -> dict | None:
    """What the component test page offers the gates, read from its descriptor: the buttons of the lamp section and
    the 'Raise all' button of the alarm section (their captions and the seconds a pulse holds its tag)."""
    d = next((d for d in descriptors if d["screen"]["route"] == TEST_ROUTE), None)
    if d is None:
        return None

    def inside(box: dict, item: dict) -> bool:
        return box["x"] <= item["x"] < box["x"] + box["w"] and box["y"] <= item["y"] < box["y"] + box["h"]
    lamp = next((x for x in d.get("sections", []) if x.get("label", "").startswith("Indicator")), None)
    alarm = next((x for x in d.get("sections", []) if x.get("label", "").startswith("Test alarms")), None)
    buttons = [b for b in d.get("buttons", []) if (b.get("action") or {}).get("type") == "pulse"]
    lamp_buttons = sorted((b for b in buttons if lamp and inside(lamp, b)), key=lambda b: (b["y"], b["x"]))
    raise_all = next((b for b in buttons if alarm and inside(alarm, b) and b["label"].startswith("Raise all")), None)
    return {"route": TEST_ROUTE,
            "lamps": {"section": lamp["label"], "buttons": [b["label"] for b in lamp_buttons]} if lamp and lamp_buttons else None,
            "alarms": {"section": alarm["label"], "raise_all": raise_all["label"],
                       "hold_s": int(raise_all["action"].get("ms", 60000)) // 1000 + 5} if raise_all else None}


def symbols_plan(descriptors: list[dict]) -> dict:
    """Per page route: the count of each module-drawn kind and the device symbols that open a faceplate, in the order
    of their position (x, then y), so that the gate can click the n-th of its kind on the page."""
    out = {}
    for d in descriptors:
        route = d["screen"]["route"]
        if route == TEST_ROUTE:
            continue
        # only the symbols drawn as module components: one on the library's view (`render: view`) has no element
        # the selectors find, so counting it expected more than the page could show (COB-198)
        syms = sorted((s for s in d.get("symbols", []) if s["kind"] in MODULE_TAGS and module_drawn(s)),
                      key=lambda s: (s["x"], s["y"]))
        if not syms:
            continue
        kinds = Counter(s["kind"] for s in syms)
        opens = [{"kind": s["kind"], "rank": [t["id"] for t in syms if t["kind"] == s["kind"]].index(s["id"]),
                  "device": device_of(s)} for s in syms if device_of(s)]
        out[route] = {"counts": dict(kinds), "opens": opens}
    return out


def navtable_routes(navtable, design=None) -> list[str]:
    """The routes to open: an entry's own `route` and, since the navigation table names none (a route is the
    design's decision), the page and support routes of the project design's `routes` table."""
    entries = navtable if isinstance(navtable, list) else (navtable or {}).get("entries") or []
    found = [e["route"] for e in entries if isinstance(e, dict) and isinstance(e.get("route"), str) and e["route"]]
    for r in (design or {}).get("routes") or []:
        if isinstance(r, dict) and r.get("treatment") in ("page", "support") and isinstance(r.get("route"), str):
            found.append(r["route"])
    return list(dict.fromkeys(found))


def banner_pages(model: dict, alarm: dict) -> tuple[list[str], list[str]]:
    """The built pages (their ids) whose banner shows an alarm, and those whose banner does not: the alarm's node, its
    subtree and the nodes above it show it (wiki/04 section 8.7)."""
    pages = [p for p in model["pages"] if p["built"]]
    nodes = {n["id"]: n for n in model["nodes"]}
    subtree = {alarm["node"]} | {c["id"] for c in model["nodes"] if c["parent"] == alarm["node"]}
    above, n = set(), alarm["node"]
    while n:
        above.add(n)
        n = nodes[n]["parent"]
    shows = [p["id"] for p in pages if p["node"] in above or p["node"] in subtree]
    return shows, [p["id"] for p in pages if p["id"] not in shows]


def plan_of(model: dict, descriptors: list[dict], base: str, window: tuple[int, int], gates: list[str],
            raise_alarm: bool, navtable=None, design=None, only_routes: list[str] | None = None) -> dict:
    pages = [p for p in model["pages"] if p["built"]]
    if design is not None:
        # the project's routes (COB-211, NOTE-WFB-12 section 6.1): the built model pages, the design's own routes (one
        # the project lacks stays: a real broken link the evidence reports), every descriptor route and the alert
        # list; no unbuilt model page and no support route of the model's that the design does not name
        routes = [p["route"] for p in pages] + navtable_routes(navtable, design) + [d["screen"]["route"] for d in descriptors]
    else:
        routes = [p["route"] for p in model["pages"]]
        routes += sorted({n["route"] for n in model["nav"] if n["resolution"] == "support" and n.get("route")})
        routes += navtable_routes(navtable, design) + [d["screen"]["route"] for d in descriptors]   # never only the model's
    routes.append(ALERTS_ROUTE)
    routes = list(dict.fromkeys(routes))
    test = testpage_plan(descriptors)
    by_route = {d["screen"]["route"]: d for d in descriptors if d["screen"]["route"] != TEST_ROUTE}   # a library page: its own gates
    device_pages = [p for p in pages if any(d["page"] == p["id"] and d["faceplate"] != "empty"
                                           for d in model["devices"].values())]
    first = (device_pages or pages or [None])[0]      # the page of the zoom gate: one with a device that opens a faceplate
    device = next((d for d in model["devices"].values() if first and d["page"] == first["id"]
                   and d["faceplate"] != "empty"), None)
    start = (pages or [None])[0]                      # where the search gate starts; it searches for another page
    target = (pages[1:] or pages or [None])[0]
    tag = next((t for t in model["tags"] if t.get("page") and t.get("device")), None)
    alarms = alarm_sources(model) if raise_alarm else []
    alarm = alarms[0] if alarms else None
    shows, hides = banner_pages(model, alarm) if alarm else ([], [])
    plan = {
        "base": origin_of(base), "window": {"w": window[0], "h": window[1]}, "gates": gates,
        "search": {"route": start["route"] if start else "/",
                   "page": {"query": target["title"] if target else None, "route": target["route"] if target else None},
                   "device": ({"query": device["tag"], "row": device["label"], "faceplate": device["tag"]} if device else None),
                   "tag": ({"query": tag["name"], "route": next((p["route"] for p in pages if p["id"] == tag["page"]), None)}
                           if tag else None),
                   "none": "zzqq", "paste": (start["title"][:3] if start else "A")},
        "routes": routes,
        "zoom": {"steps": ZOOM_STEPS, "route": first["route"] if first else "/", "device": device["tag"] if device else None},
        "menus": ["user", "brilliance", "alert", "crumb"],
        "panels": {"pages": [p["title"] for p in pages[:2]],
                   "support": ["Trend"] + ([next(d["screen"]["title"] for d in descriptors
                                                 if d["screen"]["route"] == test["route"])] if test else [])},
        "readouts": {r: {"module": sum(1 for s in d.get("symbols", []) if s["kind"] in MODULE_TAGS and module_drawn(s))}
                     for r, d in by_route.items()
                     if any(s["kind"] in MODULE_TAGS and module_drawn(s) for s in d.get("symbols", []))},
        "colour": {"with_medium": [r for r, d in by_route.items() if any(p.get("medium", "neutral") != "neutral" for p in d.get("pipes", []))],
                   "without_medium": [r for r, d in by_route.items()
                                      if not any(p.get("medium", "neutral") != "neutral" for p in d.get("pipes", []))]},
        "columns": {r: columns_of(d) for r, d in by_route.items() if columns_of(d)},
        "fill": [{"route": p["route"], "canvas": next(({"w": d["screen"]["width"], "h": d["screen"]["height"]}
                                                       for r, d in by_route.items() if r == p["route"]), None)} for p in pages],
        "alarm": alarm, "alarms": alarms, "writes": raise_alarm,
        "testpage": test, "symbols": symbols_plan(descriptors),
        "banner": {"shows": [next(q["route"] for q in pages if q["id"] == i) for i in shows],
                   "hides": [next(q["route"] for q in pages if q["id"] == i) for i in hides]} if alarm else None,
        "ack": {"route": ALERTS_ROUTE, "tick": "a row's tick box with the mouse", "buttons": ["Ack selected", "Ack all", "Confirm"]}
        if alarm else None}
    if only_routes is not None:
        limit_to(plan, only_routes, {d["screen"]["route"] for d in descriptors})
    return plan


def limit_to(plan: dict, only_routes: list[str], page_routes: set[str] | None = None) -> None:
    """The plan of `--only-routes`: the page-by-page gates keep the routes listed, the others are unchanged; the fill
    gate's dock steps keep the route the whole plan gives them, and the plan records the filter. The routes gate keeps
    the routes listed and every route that no page descriptor (`page_routes`) draws, such as a frame page (COB-193)."""
    keep = set(only_routes)
    plan["only_routes"] = sorted(keep)
    plan["fill_after_dock"] = plan["fill"][-1]["route"] if plan["fill"] else None
    if page_routes is not None:
        plan["routes"] = [r for r in plan["routes"] if r in keep or r not in page_routes]
    plan["readouts"] = {r: v for r, v in plan["readouts"].items() if r in keep}
    plan["colour"] = {k: [r for r in v if r in keep] for k, v in plan["colour"].items()}
    plan["columns"] = {r: v for r, v in plan["columns"].items() if r in keep}
    plan["fill"] = [f for f in plan["fill"] if f["route"] in keep]
    plan["symbols"] = {r: v for r, v in plan["symbols"].items() if r in keep}


# ---- reading the page -----------------------------------------------------------------------------------------
MEASURE = """() => {
  const rect = (e) => { if (!e) return null; const r = e.getBoundingClientRect(); return r.width ? [r.left, r.top, r.width, r.height].map(Math.round).join(',') : null; };
  const docks = [...document.querySelectorAll('div')].filter((e) => e.getBoundingClientRect().width > 0);
  const find = (f) => docks.filter((e) => f(e.getBoundingClientRect()))
    .sort((a, b) => b.getBoundingClientRect().width - a.getBoundingClientRect().width)[0];   // the widest: a dock, not its content
  const d = document.querySelector('[style*="scale("]');
  const c = document.getElementById('cadre-canvas');
  const field = [...document.querySelectorAll('input')].find((i) => /Search pages, devices/.test(i.placeholder));
  const pops = [...document.querySelectorAll('.ia_popup')].map((p) => p.id + '@' + rect(p));
  return {
    head: rect(find((r) => r.top === 0 && r.height >= 80 && r.height <= 90)),
    banner: rect(find((r) => Math.round(r.bottom) === innerHeight && r.height >= 70 && r.height <= 80)),
    nav: rect(find((r) => Math.round(r.left) === 0 && r.width >= 300 && r.width <= 340 && r.top > 0)),
    faceplate: rect(find((r) => Math.round(r.right) === innerWidth && r.width >= 390 && r.width <= 410 && r.top > 0)),
    field: rect(field), pops: pops,
    scale: d ? +((d.style.transform.match(/scale\\(([\\d.]+)\\)/) || [])[1] || 0) : null,
    scroll: c ? [c.scrollWidth, c.scrollHeight] : null, vv: visualViewport.scale, iw: innerWidth };
}"""
# the obasm head is three rows of 48, 36 and 48 px: the head the measurement looks for is 132 px high, not 80 to 90
HEAD_HEIGHT = "r.height >= 80 && r.height <= 90"
MEASURE_OBASM = MEASURE.replace(HEAD_HEIGHT, "r.height >= 128 && r.height <= 136")
# the module top bar's buttons and bell (centres), for the new frames: the bar's buttons are in a shadow root, where TOP_ICONS cannot see an SVG
BAR_POINTS = """() => { const out = {}; const bar = document.querySelector('.docked-view-top [data-component="cadre.ob.topbar"]');
  if (!bar) return out;
  const pt = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 ? [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)] : null; };
  const sr = (bar.querySelector('obc-top-bar') || {}).shadowRoot;
  for (const [k, label] of [['menu', 'Menu'], ['apps', 'Apps'], ['dimming', 'Dimming'], ['user', 'User']]) {
    const b = sr && sr.querySelector('[aria-label="' + label + '"]'); if (b && pt(b)) out[k] = pt(b); }
  const bell = bar.querySelector('obc-alert-button'); if (bell && pt(bell)) out.alert = pt(bell);
  return out; }"""
FILL = """() => { const d = document.querySelector('[style*="scale("]'); const c = document.getElementById('cadre-canvas');
  if (!d || !c) return null; const r = d.getBoundingClientRect(), q = c.getBoundingClientRect();
  return {w: Math.round(r.width), h: Math.round(r.height), cw: Math.round(q.width), ch: Math.round(q.height)}; }"""
DEEP = """(sel) => [...document.querySelectorAll(sel)].map((el) => { const texts = [];
  const walk = (n) => { if (n.nodeType === 3 && n.textContent.trim()) { const pe = n.parentElement; const r = pe && pe.getBoundingClientRect();
      const cs = pe && getComputedStyle(pe); if (r && r.width > 0 && cs.visibility !== 'hidden' && cs.display !== 'none') texts.push(n.textContent.trim()); }
    if (n.shadowRoot) walk(n.shadowRoot); for (const k of n.childNodes || []) walk(k); };
  walk(el); const r = el.getBoundingClientRect();
  return {x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), text: texts.join(' ')}; })"""
TOP_ICONS = """() => [...document.querySelectorAll('svg')].map((s) => s.getBoundingClientRect())
  .filter((r) => r.top < 44 && r.top >= 0 && r.height > 8 && r.height < 44)
  .map((r) => [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)]).sort((a, b) => a[0] - b[0])"""
PANEL = """() => { const e = document.querySelector('[style*="z-index: 50"]');
  return !!e && getComputedStyle(e).display !== 'none' ? e.innerText.slice(0, 400) : null; }"""
ALERT_COUNT = """() => { const n = [...document.querySelectorAll('body *')].filter((e) => { const r = e.getBoundingClientRect();
    return r.top >= 0 && r.top < 44 && r.left > innerWidth * 0.6 && e.children.length === 0 && /^\\d+$/.test(e.textContent.trim()); })
    .map((e) => +e.textContent.trim()); return n.length ? Math.max(...n) : 0; }"""
ACK_STATE = """() => { const btn = (t) => [...document.querySelectorAll('button, [role=button], [data-component="ia.input.button"]')]
    .find((e) => e.innerText.trim() === t && e.getBoundingClientRect().width > 0);
  const off = (e) => !e || e.disabled || e.getAttribute('aria-disabled') === 'true' || /disabled/i.test(e.className);
  const rows = [...document.querySelectorAll('[data-alarm-row], tr, [role=row]')].filter((e) => /Unacknowledged/.test(e.innerText)).length;
  return {unacked: rows, ackSelectedEnabled: !off(btn('Ack selected')), ackAllShown: !!btn('Ack all'),
          confirmShown: !!btn('Confirm'), text: document.body.innerText.slice(0, 1500)}; }"""


# The exercise's Level 5 helpers: Perspective state is read from a component's store (the React fibre's
# `store.props.read` and `store.view.custom.read`), never written. Injected after every navigation.
STORE_JS = """() => {
  window.__deep = (sel, root = document) => { const out = []; const walk = (n) => { if (n.querySelectorAll) out.push(...n.querySelectorAll(sel));
    for (const e of (n.querySelectorAll ? n.querySelectorAll('*') : [])) if (e.shadowRoot) walk(e.shadowRoot); }; walk(root); return out; };
  window.__section = (title) => { const lab = [...document.querySelectorAll('.ia_labelComponent')].find((e) => e.innerText.trim().startsWith(title));
    if (!lab) return null; let e = lab; while (e && e.getBoundingClientRect().width < 500) e = e.parentElement; return e; };
  window.__rect = (e) => { const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; };
  window.__store = (el) => { const fk = Object.keys(el).find((k) => k.startsWith('__reactFiber')); let f = el[fk], n = 0;
    while (f && n < 40) { const mp = f.memoizedProps || {}; if (mp.store && mp.store.props) return mp.store; f = f.return; n++; } return null; };
  window.__btn = (text, near) => [...document.querySelectorAll('[data-component="ia.input.button"]')]
    .filter((e) => e.innerText.trim() === text && e.getBoundingClientRect().width > 0)
    .sort((a, b) => near ? Math.abs(a.getBoundingClientRect().y - near) - Math.abs(b.getBoundingClientRect().y - near) : 0)[0] || null;
  window.__custom = (text, near) => { const b = window.__btn(text, near); const s = b && window.__store(b); if (!s) return null;
    const c = s.view.custom.read('');
    return {enabled: !!s.props.read('enabled'), unacked: c.unacked, selected: (c.selected || []).length + (c.selectedR || []).length,
      shown: (c.shown || []).length, pending: c.ackPending && c.ackPending.text, message: c.ackMessage, y: b.getBoundingClientRect().y,
      rect: window.__rect(b)}; };
}"""
CUSTOM = "([t, y]) => window.__custom(t, y)"
BTN_RECT = "([t, y]) => { const b = window.__btn(t, y); return b ? window.__rect(b) : null; }"
LAMP_COLOURS = """(title) => { const s = window.__section(title); if (!s) return null; const b = s.getBoundingClientRect();
  return [...document.querySelectorAll('[data-component="ia.display.view"]')].filter((e) => { const r = e.getBoundingClientRect();
    const cx = r.x + r.width / 2, cy = r.y + r.height / 2; return r.width > 0 && r.width < 120 && cx > b.left && cx < b.right && cy > b.top && cy < b.bottom; })
    .map((e) => { const st = window.__store(e); return st ? String(st.props.read('params.colour')) : '?'; }); }"""
BANNER_TEXT = """() => { const e = [...document.querySelectorAll('div')].find((e) => { const r = e.getBoundingClientRect();
    return Math.round(r.bottom) === innerHeight && r.height >= 70 && r.height <= 80 && r.width > innerWidth * 0.5; });
  return e ? e.innerText : document.body.innerText; }"""
SCROLL_SECTION = "(title) => { const s = window.__section(title); if (s) s.scrollIntoView({block: 'start'}); return !!s; }"
TICKS = "() => window.__deep('obc-checkbox').filter((e) => e.getBoundingClientRect().width > 0).map(window.__rect)"
ALERT_ROW = """() => { const t = document.querySelector('[data-component="ia.display.alarmstatustable"]') || document;
  const rows = [...t.querySelectorAll('[data-alarm-row], div')].filter((e) => { const b = e.getBoundingClientRect();
    return b.width > 150 && b.height > 20 && b.height < 40 && /Unacknowledged/.test(e.innerText) && e.innerText.split('\\n').length < 12; });
  rows.sort((a, b) => b.getBoundingClientRect().width - a.getBoundingClientRect().width);
  return rows.length ? window.__rect(rows[0]) : null; }"""
KIND_RECTS = """([kind, tag]) => { const dc = [...document.querySelectorAll('[data-component="cadre.ob.' + kind + '"]')];
  const els = dc.length ? dc : window.__deep(tag);
  return els.map(window.__rect).filter((r) => r.w > 0).sort((a, b) => a.x - b.x || a.y - b.y); }"""
DOCK_TEXT = """() => { const d = [...document.querySelectorAll('div')].find((e) => { const r = e.getBoundingClientRect();
    return Math.round(r.right) === innerWidth && r.width >= 390 && r.width <= 410 && r.top > 0 && r.height > 300; });
  return d ? d.innerText.replace(/\\s+/g, ' ').slice(0, 400) : ''; }"""


class Session:
    """A Playwright page with the helpers the gates share. Every wait is scaled by `settle`."""

    def __init__(self, page, ctx, cdp, base, window, out, settle, origin):
        self.p, self.ctx, self.cdp, self.base, self.window, self.out = page, ctx, cdp, base.rstrip("/"), window, out
        self.settle, self.origin = settle, origin
        self.errors: list[str] = []
        page.on("pageerror", lambda e: self.errors.append(str(e)[:200]))

    def wait(self, ms):
        self.p.wait_for_timeout(max(1, int(ms * self.settle)))

    def go(self, route, ms=7000):
        self.p.goto(self.base + route)
        self.wait(ms)
        self.inject()

    def canvas_box(self):
        """The canvas's box: `#cadre-canvas`, else the scaled page element, else the window below the head."""
        box = self.p.evaluate("""() => { for (const sel of ['#cadre-canvas', '[style*="scale("]']) { const e = document.querySelector(sel);
            if (e) { const r = e.getBoundingClientRect(); if (r.width > 50 && r.height > 50) return {x: r.x, y: r.y, width: r.width, height: r.height}; } }
          return null; }""")
        return box or {"x": 200, "y": 150, "width": self.window[0] - 400, "height": self.window[1] - 300}

    def frame(self) -> str:
        """The frame the page shows: `default` (the asm frame, or the stock frame), `ob` or `obasm` (`glass.frame_variant`)."""
        return glass.frame_variant(self.p, tries=max(2, round(12 * self.settle)))   # the wait for the dock follows `--settle`

    def banner_text(self):
        """The text of the frame's banner (the dock along the foot), else of the whole page. The `ob` frame has no banner dock:
        what it shows an operator of an alarm is the alert message in its strip and the alert menu, so its text is theirs (the
        menu is opened and closed again)."""
        if self.frame() != glass.FRAME_OB:
            return self.p.evaluate(BANNER_TEXT)
        strip = self.p.evaluate("(document.querySelector('.docked-view-top') || document.body).innerText")
        alerts = glass.open_alarm_menu(self.p) or []
        self.p.keyboard.press("Escape")
        self.wait(800)
        return strip + " " + " ".join(f"{a.get('text')} {a.get('source')}" for a in alerts)

    def alert_count(self) -> int:
        """The count on the top bar's alert button: its digits in the older frames (`ALERT_COUNT`), the module bell's in the new."""
        if self.frame() != glass.FRAME_DEFAULT:
            return glass.frame_alarm_count(self.p) or 0
        return self.p.evaluate(ALERT_COUNT)

    def open_device(self, tag):
        """Open a device's faceplate in the dock: by the search field in the asm and obasm frames (their way, and the only one
        the older gates used); the `ob` frame has no search field, so the device's symbol is pressed (`glass.open_device`)."""
        if self.frame() == glass.FRAME_OB:
            glass.open_device(self.p, tag)
            return
        self.search(tag)

    def click_entry(self, caption):
        """Press the popup's entry `caption` (Sign in, Sign out): its text in the older frames; the module user menu prints
        Sign in as its title too, so in the new frames the entry is the `obc-button` that carries it."""
        if self.frame() == glass.FRAME_DEFAULT:
            return self.click_text(caption)
        loc = self.p.locator(".ia_popup obc-button", has_text=re.compile(rf"^\s*{re.escape(caption)}\s*$")).first
        bx = loc.bounding_box()
        self.p.mouse.click(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2)

    def inject(self):
        self.p.evaluate(STORE_JS)

    def click_box(self, box):
        self.p.mouse.click(box["x"] + box["w"] / 2, box["y"] + box["h"] / 2)

    def button(self, text):
        return self.p.locator('[data-component="ia.input.button"]', has_text=re.compile(rf"^\s*{re.escape(text)}\s*$"))

    def press(self, text, n=0):
        """A real mouse click at the centre of the n-th visible button with this caption."""
        loc = self.button(text).nth(n)
        loc.scroll_into_view_if_needed()
        bx = loc.bounding_box()
        self.p.mouse.click(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2)
        self.wait(1200)

    def press_near(self, text, y=None):
        box = self.p.evaluate(BTN_RECT, [text, y])
        if box:
            self.click_box(box)
        self.wait(1500)
        return bool(box)

    def confirm(self):
        loc = self.button("Confirm")
        for i in range(loc.count()):
            if loc.nth(i).is_visible():
                bx = loc.nth(i).bounding_box()
                self.p.mouse.click(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2)
                self.wait(1500)
                return True
        return False

    def custom(self, text, near=None):
        return self.p.evaluate(CUSTOM, [text, near])

    def measure(self):
        return self.p.evaluate(MEASURE_OBASM if self.frame() == glass.FRAME_OBASM else MEASURE)

    def shot(self, name):
        self.out.mkdir(parents=True, exist_ok=True)
        self.p.screenshot(path=str(self.out / f"{name}.png"))
        return f"pictures/{name}.png"

    def field(self):
        return self.p.locator('input[placeholder="Search pages, devices, tags"]')

    def click_field(self):
        bx = self.field().bounding_box()
        self.p.mouse.click(bx["x"] + 40, bx["y"] + bx["height"] / 2)
        self.wait(300)

    def search(self, q, enter=True):
        self.click_field()
        self.p.keyboard.type(q, delay=int(60 * self.settle))
        self.wait(1800)
        shown = self.p.evaluate(PANEL)
        if enter:
            self.p.keyboard.press("Enter")
            self.wait(3500)
        return shown

    def click_text(self, text, exact=True):
        loc = self.p.locator(f':text-is("{text}"):visible' if exact else f':text("{text}"):visible').first
        bx = loc.bounding_box()
        self.p.mouse.click(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2)

    def icons(self):
        """The top bar's icons, left to right as the older frames lay them out (menu, the second navigation button, then the alert
        menu, brilliance and user icons last): their SVGs by position in the older frames (`TOP_ICONS`); the module bar's
        own buttons in the new ones, in that order (the apps button stands at the right of the module bar, but it is the
        second navigation button of the ASM frame, so it is listed second)."""
        if self.frame() == glass.FRAME_DEFAULT:
            return self.p.evaluate(TOP_ICONS)
        pts = self.p.evaluate(BAR_POINTS)
        return [pts[k] for k in ("menu", "apps", "alert", "dimming", "user") if k in pts]

    def url(self):
        return self.p.url


def frame_of(m: dict) -> dict:
    return {k: m[k] for k in ("head", "banner", "field", "nav", "faceplate", "vv", "iw")} | {"pops": ";".join(m["pops"])}


def step(steps: list, action: str, expected, found, ok: bool, picture: str | None = None) -> bool:
    steps.append({"action": action, "expected": expected, "found": found, "ok": bool(ok), "picture": picture})
    return bool(ok)


# ---- the gates ------------------------------------------------------------------------------------------------
def gate_search(s: Session, plan: dict, steps: list, rec: dict) -> None:
    sp = plan["search"]
    s.go(sp["route"])
    if sp["page"]["query"]:
        shown = s.search(sp["page"]["query"])
        step(steps, "type a page's name after a mouse click in the field", "the panel shows a Pages group",
             (shown or "")[:80], shown and "Pages" in shown)
        step(steps, "Enter on a page opens it", sp["page"]["route"], s.url(), s.url().endswith(sp["page"]["route"]))
    if sp["device"]:
        s.go(sp["route"])
        s.search(sp["device"]["query"], enter=False)
        s.click_text(sp["device"]["row"], exact=False)
        s.wait(3500)
        m = s.measure()
        step(steps, "a click on a device row opens its faceplate in the dock", "a dock with the device",
             m["faceplate"], m["faceplate"] and s.p.evaluate("(t) => document.body.innerText.includes(t)", sp["device"]["query"]))
    if sp["tag"]:
        shown = s.search(sp["tag"]["query"])
        step(steps, "a tag query lists the tag", sp["tag"]["query"], (shown or "")[:80], shown and sp["tag"]["query"] in shown)
        step(steps, "Enter on a tag opens its page", sp["tag"]["route"], s.url(), s.url().endswith(sp["tag"]["route"] or "/"))
    s.go(sp["route"])
    shown = s.search(sp["none"], enter=False)
    step(steps, "no match says so", NO_MATCH, (shown or "")[:80], shown and NO_MATCH in shown)
    s.p.keyboard.press("Escape")
    s.wait(1200)
    step(steps, "Escape closes the panel and clears the field", "no panel, field empty",
         {"panel": bool(s.p.evaluate(PANEL)), "field": s.field().input_value()},
         not s.p.evaluate(PANEL) and s.field().input_value() == "")
    try:
        s.ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=plan["base"])
        s.p.evaluate("(t) => navigator.clipboard.writeText(t)", sp["paste"])
        s.click_field()
        s.p.keyboard.press("Control+V")
        s.wait(2000)
        step(steps, "a pasted query (Ctrl+V) opens the panel", "the panel", s.field().input_value(),
             bool(s.p.evaluate(PANEL)))
        s.p.keyboard.press("Escape")
        s.wait(800)
    except Exception as e:   # a browser that refuses the clipboard: said, and the step fails
        step(steps, "a pasted query (Ctrl+V) opens the panel", "the panel", str(e).splitlines()[0][:120], False)
    s.search("a", enter=False)
    s.p.mouse.click(300, 700)
    s.wait(1500)
    step(steps, "a click on the page outside the panel closes it", "no panel", bool(s.p.evaluate(PANEL)),
         not s.p.evaluate(PANEL))
    s.p.keyboard.press("Escape")
    s.wait(500)


def gate_zoom(s: Session, plan: dict, steps: list, rec: dict) -> None:
    z = plan["zoom"]
    w, h = s.window
    s.go(z["route"])
    if z["device"]:
        s.search(z["device"])
    before = s.measure()
    frames = rec.setdefault("frames", {})
    same = lambda a, b: frame_of(a) == frame_of(b)    # noqa: E731

    def record(name, m0, m1, expect, found, ok):
        frames[name] = {"before": frame_of(m0), "after": frame_of(m1)}
        step(steps, name, expect, found, ok and same(m0, m1))
    plus = s.p.locator(':text-is("+"):visible').first
    for _ in range(2):
        bx = plus.bounding_box()
        s.p.mouse.click(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2)
        s.wait(1500)
    m1 = s.measure()
    record("buttons scale the canvas only", before, m1, "scale up, frame unchanged", [before["scale"], m1["scale"]],
           (m1["scale"] or 0) > (before["scale"] or 0) * 1.05)
    cv = s.canvas_box()
    s.p.mouse.move(cv["x"] + cv["width"] / 3, cv["y"] + cv["height"] / 3)
    s.p.keyboard.down("Control")
    s.p.mouse.wheel(0, -300)
    s.p.keyboard.up("Control")
    s.wait(2000)
    m2 = s.measure()
    record("Ctrl+wheel over the canvas scales the canvas only", m1, m2, "scale up", [m1["scale"], m2["scale"]],
           (m2["scale"] or 0) > (m1["scale"] or 0))
    s.p.mouse.move(w / 2, 40)
    s.p.keyboard.down("Control")
    s.p.mouse.wheel(0, -300)
    s.p.keyboard.up("Control")
    s.wait(2000)
    m3 = s.measure()
    record("Ctrl+wheel over the header zooms nothing", m2, m3, "scale unchanged", [m2["scale"], m3["scale"]],
           m3["scale"] == m2["scale"])
    s.p.mouse.move(cv["x"] + cv["width"] / 2, cv["y"] + cv["height"] / 2)
    s.p.keyboard.press("Control+Minus")
    s.wait(1800)
    m4 = s.measure()
    record("Ctrl+minus zooms the canvas out", m3, m4, "scale down", [m3["scale"], m4["scale"]],
           (m4["scale"] or 0) < (m3["scale"] or 0))
    s.cdp.send("Input.synthesizePinchGesture", {"x": round(cv["x"] + cv["width"] / 2), "y": round(cv["y"] + cv["height"] / 2),
                                                "scaleFactor": 1.6, "gestureSourceType": "touch"})
    s.wait(2500)
    m5 = s.measure()
    record("a pinch on the canvas scales the canvas only", m4, m5, "scale up", [m4["scale"], m5["scale"]],
           (m5["scale"] or 0) > (m4["scale"] or 0))
    s.cdp.send("Input.synthesizePinchGesture", {"x": round(w / 2), "y": 40, "scaleFactor": 1.6, "gestureSourceType": "touch"})
    s.wait(2500)
    m6 = s.measure()
    record("a pinch on the header zooms nothing", m5, m6, "scale unchanged, page zoom 1", [m6["scale"], m6["vv"]],
           m6["scale"] == m5["scale"] and m6["vv"] == 1)
    pic = s.shot("zoom_docked")
    if z["device"]:
        s.click_text("Float")
        s.wait(2500)
        f0 = s.measure()
        s.p.mouse.move(cv["x"] + 200, cv["y"] + 200)
        s.p.keyboard.down("Control")
        s.p.mouse.wheel(0, 300)
        s.p.keyboard.up("Control")
        s.wait(2000)
        f1 = s.measure()
        record("a floating faceplate keeps its place and size", f0, f1, "one popup, scale down",
               [len(f0["pops"]), f0["scale"], f1["scale"]], len(f0["pops"]) == 1 and (f1["scale"] or 0) < (f0["scale"] or 0))
        s.p.keyboard.press("Control+0")
        s.wait(1800)
        f2 = s.measure()
        step(steps, "Ctrl+0 returns to the fit", "scale at most 1", f2["scale"], (f2["scale"] or 0) <= 1.02,
             s.shot("zoom_float"))
        try:
            s.click_text("Dock")
        except Exception:
            pass
        s.wait(1500)
    steps[0]["picture"] = pic


def gate_menus(s: Session, plan: dict, steps: list, rec: dict) -> None:
    s.go(plan["search"]["route"])
    icons = s.icons()
    right = icons[-3:]
    for name, xy in zip(("user menu", "brilliance menu", "alert menu"), (right[2], right[1], right[0]) if len(right) == 3 else []):
        s.p.mouse.click(xy[0], xy[1])
        s.wait(1500)
        opened = s.p.evaluate("[...document.querySelectorAll('.ia_popup')].map((e) => e.id)")
        s.p.mouse.click(700, 600)
        s.wait(1500)
        closed = s.p.evaluate("[...document.querySelectorAll('.ia_popup')].map((e) => e.id)")
        step(steps, f"the {name} opens and closes on an outside click", "one popup, then none", [len(opened), len(closed)],
             len(opened) == 1 and not closed)
    if len(right) < 3:
        step(steps, "the three menu icons are in the top bar", 3, len(right), False)
    root = next((n for n in [plan.get("root_name")] if n), None)
    if root and s.frame() != glass.FRAME_OB:   # the crumb popup is an ASM part: the ob frame's crumb opens its node's page
        s.click_text(root)
        s.wait(1500)
        crumb = s.p.evaluate("document.querySelectorAll('.ia_popup').length")
        s.p.mouse.click(700, 600)
        s.wait(1500)
        step(steps, "the crumb popup closes on an outside click", "one popup, then none",
             [crumb, s.p.evaluate("document.querySelectorAll('.ia_popup').length")],
             crumb == 1 and s.p.evaluate("document.querySelectorAll('.ia_popup').length") == 0)


# the labels the navigation dock holds in the obasm frame: the module tree's and menu's items and groups, all of them, and those with a
# size (the tree draws a page only inside an open group, and the support menu is not drawn while the dock is on the page tree)
NAV_DOCK_LABELS = """() => { const d = document.querySelector('.docked-view-left'); if (!d) return {all: [], drawn: []};
  const els = [...d.querySelectorAll('obc-navigation-item, obc-tree-navigation-item, obc-tree-navigation-group')];
  const lab = (e) => String(e.label || '').trim();
  return {all: els.map(lab).filter(Boolean), drawn: els.filter((e) => e.getBoundingClientRect().width > 0).map(lab).filter(Boolean)}; }"""


def gate_panels(s: Session, plan: dict, steps: list, rec: dict) -> None:
    s.go(plan["search"]["route"])
    pp = plan["panels"]
    icons = s.icons()
    if len(icons) < 2:
        step(steps, "the navigation buttons are in the top bar", 2, len(icons), False)
        return
    module = s.frame() != glass.FRAME_DEFAULT
    s.p.mouse.click(*icons[0])
    s.wait(2000)
    text = s.p.evaluate("document.body.innerText")
    m = s.measure()
    if module:   # the items draw their labels in shadow DOM, which `innerText` does not reach
        held = s.p.evaluate(NAV_DOCK_LABELS)
        tree_ok = all(t in held["all"] for t in pp["pages"]) and "Component test" not in held["drawn"]
        text = " ".join(held["drawn"])
    else:
        tree_ok = all(t in text for t in pp["pages"]) and "Component test" not in text.split(pp["pages"][0])[0][-200:]
    step(steps, "the menu button opens the page tree, with no support entry", pp["pages"],
         {"nav": m["nav"]}, m["nav"] and tree_ok,
         s.shot("nav_pages"))
    s.p.keyboard.press("Escape")
    s.p.mouse.click(1500, 600)
    s.wait(1500)
    icons = s.icons()
    s.p.mouse.click(*icons[1])
    s.wait(2000)
    text = s.p.evaluate("document.body.innerText")
    if module:
        text = " ".join(s.p.evaluate(NAV_DOCK_LABELS)["drawn"])
    m = s.measure()
    step(steps, "the second button opens the support list", pp["support"], {"nav": m["nav"]},
         m["nav"] and all(t in text for t in pp["support"]), s.shot("nav_support"))
    s.p.mouse.click(1500, 600)
    s.wait(1500)


ON_OFF = re.compile(r"\b(On|Off)\b")


def readout_found(devs: list[dict]) -> dict:
    """What the readouts step found: how many devices, and the texts (at most 8) of those that show neither On nor Off,
    so that a failed step names its cause (COB-194)."""
    return {"count": len(devs), "without_on_off": [d["text"] for d in devs if not ON_OFF.search(d["text"])][:8]}


def gate_readouts(s: Session, plan: dict, steps: list, rec: dict) -> None:
    for route, want in plan["readouts"].items():
        s.go(route, 9000)
        sel = ", ".join(sorted(set(MODULE_TAGS.values())))
        devs = s.p.evaluate(DEEP, sel)
        step(steps, f"{route}: every module device shows On or Off", want["module"], readout_found(devs),
             len(devs) == want["module"] and all(ON_OFF.search(d["text"]) for d in devs))
        s.click_text("Readout")
        s.wait(2000)
        muted = s.p.evaluate(DEEP, sel)
        step(steps, f"{route}: deselecting Readout mutes every status", "no On or Off",
             [d["text"] for d in muted][:8], all(not re.search(r"\b(On|Off)\b", d["text"]) for d in muted))
        s.click_text("Readout")
        s.wait(1500)


def gate_colour(s: Session, plan: dict, steps: list, rec: dict) -> None:
    stroke = "() => [...document.querySelectorAll('svg path, svg polyline, svg line')].map((e) => getComputedStyle(e).stroke).filter((v) => v && v !== 'none').sort().join('|')"
    for route in plan["colour"]["with_medium"]:
        s.go(route, 9000)
        s0 = s.p.evaluate(stroke)
        s.click_text("Color")
        s.wait(2000)
        s1 = s.p.evaluate(stroke)
        step(steps, f"{route}: Color repaints the pipes in their medium", "the strokes change", {"changed": s0 != s1},
             s0 != s1, s.shot("colour" + route.replace("/", "_")))
        s.click_text("Color")
        s.wait(1500)
    for route in plan["colour"]["without_medium"]:
        s.go(route, 4000)
        n = s.p.locator(':text-is("Color"):visible').count()
        step(steps, f"{route}: no Color button on a page without a medium", 0, n, n == 0)


def gate_sizes(s: Session, plan: dict, steps: list, rec: dict) -> None:
    sel = "obc-readout, obc-transmitter, cadre-ob-readout"
    for route, cols in plan["columns"].items():
        s.go(route, 9000)
        ro = s.p.evaluate(DEEP, sel)
        by: dict[int, set] = {}
        for r in ro:
            by.setdefault(round(r["x"] / EQ_TOL), set()).add(r["w"])
        step(steps, f"{route}: readouts of one column show one width", [c["count"] for c in cols],
             {str(k): sorted(v) for k, v in by.items()}, bool(ro) and all(len(v) == 1 for v in by.values()))


def gate_fill(s: Session, plan: dict, steps: list, rec: dict) -> None:
    for item in plan["fill"]:
        s.go(item["route"], 9000)
        f = s.p.evaluate(FILL)
        step(steps, f"{item['route']}: the page fills the window", "width or height at least 0.97 of the canvas", f,
             f and (f["w"] >= 0.97 * f["cw"] or f["h"] >= 0.97 * f["ch"]))
    z = plan["zoom"]
    if z["device"]:
        s.go(z["route"], 6000)
        s.open_device(z["device"])
        s.go(plan.get("fill_after_dock") or plan["fill"][-1]["route"], 3000)
        f = s.p.evaluate(FILL)
        step(steps, "a page loaded after a docked faceplate fills the window", "no stale dock width", f,
             f and (f["w"] >= 0.97 * f["cw"] or f["h"] >= 0.97 * f["ch"]))
        s.p.reload()
        s.wait(7000)
        f = s.p.evaluate(FILL)
        m = s.measure()
        step(steps, "a page reloaded after a dock fills the window", {"fills": True}, {"fill": f, "dock": m["faceplate"]},
             f and (f["w"] >= 0.97 * f["cw"] or f["h"] >= 0.97 * f["ch"]), s.shot("reload_after_dock"))


def gate_routes(s: Session, plan: dict, steps: list, rec: dict) -> None:
    """One step per route, `<route>: the route opens`, so that a sweep of the pages that changed can reuse the others."""
    for r in plan["routes"]:
        s.go(r, 3500)
        t = s.p.evaluate("document.body.innerText")[:2000]
        hit = re.search(r"not found|No view configured|Error", t, re.I)
        bad = bool(hit) and NO_MATCH not in t
        step(steps, f"{r}: the route opens", "opens", hit.group(0) if bad else "opened", not bad)


def alarm_present(s: Session, desc: str) -> bool:
    s.go("/alerts", 5000)
    return desc in s.p.evaluate("document.body.innerText")


def gate_alarm(s: Session, plan: dict, steps: list, rec: dict) -> None:
    a = plan["alarm"]
    lane = rec["lane"]
    s.go(plan["search"]["route"], 5000)
    n0 = s.alert_count()
    reply = lane.set({x["tag"]: x["raise"] for x in plan["alarms"]})
    step(steps, "raise the alarms through their source tags", "the gateway counts the import", reply.get("failed") or "imported",
         not reply.get("failed") and not reply.get("missing"))
    rec["raised"] = True
    s.wait(5000)
    step(steps, "definition: the alarm is listed on /alerts", a["desc"], "listed" if alarm_present(s, a["desc"]) else "absent",
         alarm_present(s, a["desc"]), s.shot("alarm_alerts"))
    s.go(plan["search"]["route"], 5000)
    n1 = s.alert_count()
    step(steps, "frame: the top bar's alert count rises", f"above {n0}", n1, n1 > n0)
    shows = (plan.get("banner") or {}).get("shows") or []
    if shows:
        s.go(shows[0], 5000)
    text = s.banner_text()
    step(steps, "banner: the alarm shows on the page of its node", a["desc"], "shown" if a["desc"] in text else "absent",
         a["desc"] in text, s.shot("alarm_banner"))
    step(steps, "roll-up: the node of the alarm counts it", "a count above 0", n1, n1 > 0)
    rec["alarm_seen"] = True


def sign_in(s: Session, steps: list) -> bool:
    path = os.environ.get("CADRE_TEST_LOGIN")
    login = None
    if path and Path(path).is_file():
        d = {}
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
        login = d if d.get("user") and d.get("password") else None
    if login is None:
        return step(steps, "sign in with the test login", "a login in CADRE_TEST_LOGIN", "none", False)
    icons = s.icons()
    s.p.mouse.click(*icons[-1])
    s.wait(1500)
    s.click_entry("Sign in")
    s.p.wait_for_url(re.compile(r"/idp/"), timeout=30000)
    s.p.locator('input[name="username"]').click()
    s.p.keyboard.type(login["user"])
    s.p.keyboard.press("Enter")
    s.p.locator('input[name="password"]').wait_for(state="visible", timeout=15000)
    s.p.locator('input[name="password"]').click()
    s.p.keyboard.type(login["password"])
    s.p.keyboard.press("Enter")
    s.p.wait_for_url(re.compile(re.escape(s.base)), timeout=30000)
    s.wait(5000)
    s.p.mouse.click(*s.icons()[-1])
    s.wait(1200)
    ok = s.p.locator(':text-is("Sign out"):visible').count() > 0
    s.p.keyboard.press("Escape")
    return step(steps, "sign in with the test login", "Sign out offered", "offered" if ok else "absent", ok)


def gate_ack(s: Session, plan: dict, steps: list, rec: dict) -> None:
    """Sign in, then on the alert list: a mouse click on a row enables Ack selected, which acknowledges the ticked rows;
    Ack all asks with the count, and acknowledges the rest. State is read from the buttons' stores."""
    s.go(plan["search"]["route"], 5000)
    if not sign_in(s, steps):
        return
    s.go(plan["ack"]["route"], 6000)
    a0 = s.custom("Ack selected")
    row = s.p.evaluate(ALERT_ROW)
    if row:
        s.p.mouse.click(row["x"] + 16, row["y"] + row["h"] / 2)
        s.wait(1500)
    a1 = s.custom("Ack selected")
    for _ in range(8):      # the selection reaches the button's store over the socket
        if a1 and a1["enabled"]:
            break
        s.wait(1000)
        a1 = s.custom("Ack selected")
    step(steps, "a ticked row enables Ack selected", "enabled, one row selected at least",
         {"before": a0 and a0["enabled"], "after": a1 and a1["enabled"], "selected": a1 and a1["selected"]},
         bool(a1 and a1["enabled"] and a1["selected"] >= 1), s.shot("ack_ticked"))
    if not a1:
        return
    s.press_near("Ack selected")
    a2: dict = {}
    for _ in range(12):      # the table refreshes its rows on its own rate
        s.wait(1000)
        a2 = s.custom("Ack all") or {}
        if a2.get("unacked") == a1["unacked"] - a1["selected"]:
            break
    step(steps, "Ack selected acknowledges the ticked rows", a1["unacked"] - a1["selected"],
         {"unacked": a2.get("unacked"), "message": a2.get("message")},
         a2.get("unacked") == a1["unacked"] - a1["selected"] and not a2.get("message"))
    if not a2.get("unacked"):
        step(steps, "Ack all has alarms left to acknowledge", "none left: Ack selected took them all", 0, True)
        return
    s.press_near("Ack all")
    a3 = s.custom("Ack all") or {}
    step(steps, "Ack all asks with the count", "Acknowledge N alarms?", a3.get("pending"),
         bool(re.fullmatch(r"Acknowledge \d+ alarms?\?", a3.get("pending") or "")), s.shot("ack_confirm"))
    s.confirm()
    a4: dict = {}
    for _ in range(12):      # the table refreshes its rows on its own rate
        s.wait(1000)
        a4 = s.custom("Ack all") or {}
        if a4.get("unacked") == 0:
            break
    step(steps, "Ack all acknowledges the listed alarms", 0, {"unacked": a4.get("unacked"), "message": a4.get("message")},
         a4.get("unacked") == 0 and not a4.get("message"), s.shot("ack_after_all"))


def gate_banner(s: Session, plan: dict, steps: list, rec: dict) -> None:
    a, b = plan["alarm"], plan["banner"]
    for route in b["shows"][:2]:
        s.go(route, 5000)
        step(steps, f"{route}: the banner shows the alarm of the page's node or subtree", a["desc"],
             "shown" if a["desc"] in s.banner_text() else "absent",
             a["desc"] in s.banner_text())
    if s.frame() == glass.FRAME_OB:
        return   # the ob frame's alarm surfaces (strip, menu) list the project's alarms: the subtree rule is the ASM frames' own
    for route in b["hides"][:2]:
        s.go(route, 5000)
        step(steps, f"{route}: the banner does not show an alarm of another branch", "absent",
             "shown" if a["desc"] in s.banner_text() else "absent",
             a["desc"] not in s.banner_text())


def gate_symbols(s: Session, plan: dict, steps: list, rec: dict) -> None:
    """On each page: the module-drawn symbols are as many as the descriptor says, and a device symbol opens its
    faceplate in the dock (the first and the last of the page, by position; measured again after the dock opens, since
    the page refits beside it)."""
    for route, item in plan["symbols"].items():
        s.go(route, 8000)
        for kind, want in item["counts"].items():
            found = len(s.p.evaluate(KIND_RECTS, [kind, MODULE_TAGS[kind]]))
            step(steps, f"{route}: {want} {kind} symbols drawn", want, found, found == want)
        opens = item["opens"]
        for o in ([opens[0], opens[-1]] if len(opens) > 1 else opens):
            rects = s.p.evaluate(KIND_RECTS, [o["kind"], MODULE_TAGS[o["kind"]]])
            if o["rank"] >= len(rects):
                step(steps, f"{route}: the {o['kind']} number {o['rank'] + 1} opens its faceplate", o["device"],
                     "not drawn", False)
                continue
            s.click_box(rects[o["rank"]])
            s.wait(3000)
            text = s.p.evaluate(DOCK_TEXT)
            step(steps, f"{route}: the {o['kind']} number {o['rank'] + 1} opens its faceplate", o["device"],
                 text[:120], o["device"] in text, s.shot(f"symbol{route.replace('/', '_')}_{o['kind']}{o['rank']}"))
            s.go(route, 5000)


def gate_lamps(s: Session, plan: dict, steps: list, rec: dict) -> None:
    """On the component test page, the lamps of the colour-by-state section change colour with their test tags
    after their buttons are pressed (each button asks first)."""
    lamps = plan["testpage"]["lamps"]
    s.go(plan["testpage"]["route"], 5000)
    if not sign_in(s, steps):      # a button writes a tag, and every write path needs the signed-in user
        return
    s.go(plan["testpage"]["route"], 8000)
    before = s.p.evaluate(LAMP_COLOURS, lamps["section"])
    s.p.evaluate(SCROLL_SECTION, lamps["section"])
    s.wait(800)
    for caption in lamps["buttons"]:
        s.press(caption)
        s.confirm()
    s.wait(2500)
    after = s.p.evaluate(LAMP_COLOURS, lamps["section"])
    step(steps, "the lamps change colour with their test tags", "the colours differ", {"before": before, "after": after},
         bool(before and after and before != after), s.shot("lamps_after"))


def gate_testpanel(s: Session, plan: dict, steps: list, rec: dict) -> None:
    """On the component test page, raise the test alarms and use the alarm panel's ticks: Ack selected is disabled
    until a tick, a tick enables it, it acknowledges one; Ack all asks with the count and acknowledges the rest."""
    alarms = plan["testpage"]["alarms"]
    s.go(plan["testpage"]["route"], 5000)
    if not sign_in(s, steps):
        return
    s.go(plan["testpage"]["route"], 8000)
    s.press(alarms["raise_all"])
    s.confirm()
    s.wait(5000)
    s.p.evaluate(SCROLL_SECTION, alarms["section"])
    s.wait(1000)
    ticks = s.p.evaluate(TICKS)
    c0 = s.custom("Ack selected")
    step(steps, "test panel: ticks shown, Ack selected disabled before a tick", "ticks and a disabled button",
         {"ticks": len(ticks), "enabled": c0 and c0["enabled"]}, bool(ticks and c0 and not c0["enabled"]))
    if not (ticks and c0):
        return
    s.click_box(ticks[0])
    s.wait(1500)
    c1 = s.custom("Ack selected", c0["y"]) or {}
    step(steps, "test panel: a tick selects and enables Ack selected", "enabled, one selected",
         {"enabled": c1.get("enabled"), "selected": c1.get("selected")}, bool(c1.get("enabled") and c1.get("selected") == 1))
    s.press_near("Ack selected", c0["y"])
    s.wait(1000)
    c2 = s.custom("Ack all", c0["y"]) or {}
    step(steps, "test panel: Ack selected acknowledges one alarm", (c1.get("unacked") or 0) - 1, c2.get("unacked"),
         c2.get("unacked") == (c1.get("unacked") or 0) - 1 and not c2.get("message"))
    s.press_near("Ack all", c0["y"])
    c3 = s.custom("Ack all", c0["y"]) or {}
    step(steps, "test panel: Ack all asks with the count", "Acknowledge N alarms?", c3.get("pending"),
         bool(re.fullmatch(r"Acknowledge \d+ alarms?\?", c3.get("pending") or "")), s.shot("panel_confirm"))
    s.confirm()
    s.wait(1500)
    c4 = s.custom("Ack all", c0["y"]) or {}
    step(steps, "test panel: Ack all acknowledges the panel's alarms", 0, c4.get("unacked"),
         c4.get("unacked") == 0 and not c4.get("message"), s.shot("test_alarms_acked"))


RUN = {"search": gate_search, "zoom": gate_zoom, "menus": gate_menus, "panels": gate_panels, "readouts": gate_readouts,
       "colour": gate_colour, "sizes": gate_sizes, "fill": gate_fill, "routes": gate_routes, "symbols": gate_symbols,
       "alarm": gate_alarm, "ack": gate_ack, "banner": gate_banner, "lamps": gate_lamps, "testpanel": gate_testpanel}


# ---- the run --------------------------------------------------------------------------------------------------
def run_gates(plan: dict, base: str, window: tuple[int, int], out: Path, settle: float, lane, root_name: str | None = None) -> dict:
    from playwright.sync_api import sync_playwright
    plan = dict(plan, root_name=root_name)
    gates, rec = [], {"lane": lane, "frames": {}}
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for name in plan["gates"]:
                steps: list = []
                entry = {"name": name, "ok": True, "steps": steps}
                skip = skip_reason(name, plan)
                if skip:
                    entry["skipped"] = skip
                    gates.append(entry)
                    continue
                # a fresh browser session for each gate: a docked faceplate, a sign-in or a zoom of an earlier gate
                # is session state, and the Level 5 frame keeps it (GF-10)
                ctx = browser.new_context(viewport={"width": window[0], "height": window[1]}, has_touch=True)
                page = ctx.new_page()
                s = Session(page, ctx, ctx.new_cdp_session(page), base, window, out / "pictures", settle, plan["base"])
                if name in ASM_ONLY:   # the ob frame has no search field, tree, pivot or floating faceplate: said, not run
                    page.goto(s.base + plan["search"]["route"])
                    s.wait(5000)
                    if s.frame() == glass.FRAME_OB:
                        entry["skipped"] = "the page shows the ob frame, which is not an ASM frame (wiki 04 section 10): no search field, tree, support list or floating faceplate to exercise"
                        gates.append(entry)
                        ctx.close()
                        continue
                try:
                    RUN[name](s, plan, steps, rec)
                except Exception as e:   # a gate that could not run is a failed gate, with the reason
                    steps.append({"action": "the gate ran to its end", "expected": "no exception",
                                  "found": f"{type(e).__name__}: {str(e).splitlines()[0][:200]}", "ok": False, "picture": None})
                errors += s.errors
                ctx.close()
                if not steps:
                    entry["skipped"] = "the plan holds nothing for this gate"
                entry["ok"] = all(x["ok"] for x in steps)
                gates.append(entry)
            if errors:
                gates.append({"name": "page_errors", "ok": False, "steps": [
                    {"action": "no page script error", "expected": 0, "found": errors[:5], "ok": False, "picture": None}]})
        finally:
            restored, why = True, []
            if lane is not None and (rec.get("raised") or lane.before):
                lane.restore()
                restored = not lane.unrestored
                why = lane.unrestored
            browser.close()
    frames = rec["frames"]
    return {"gates": gates, "restored": restored, "unrestored": why,
            "frame_before": {k: v["before"] for k, v in frames.items()},
            "frame_after": {k: v["after"] for k, v in frames.items()}}


def skip_reason(name: str, plan: dict) -> str | None:
    """Why a gate is not run, in words: the gates that write need --raise-alarm, and some need what the build lacks."""
    if name in NEEDS_ALARM and plan["alarm"] is None:
        return "no alarm is raised: the simulation is off or the model has no alarm on a source tag"
    test = plan.get("testpage")
    if name == "lamps" and not (test and test["lamps"] and plan["writes"]):
        return "the gate writes test tags and needs --raise-alarm and a component test page with a lamp section"
    if name == "testpanel" and not (test and test["alarms"] and plan["writes"]):
        return "the gate writes test tags and needs --raise-alarm and a component test page with a test alarm panel"
    if name == "symbols" and not plan["symbols"]:
        if plan.get("only_routes") is not None:
            return "no route of --only-routes draws a module symbol"
        return "the build draws no module symbol"
    return None


def parse_window(text: str) -> tuple[int, int]:
    try:
        w, h = (int(n) for n in text.lower().split("x"))
    except ValueError:
        raise Fault(f"--window is WIDTHxHEIGHT, not {text!r}") from None
    return w, h


def main(argv: list[str] | None = None, *, deploy=None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--base", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--build", required=True, metavar="DIR")
    ap.add_argument("--window", default="1920x1080")
    ap.add_argument("--gates", default=",".join(GATES))
    ap.add_argument("--raise-alarm", action="store_true")
    ap.add_argument("--accepted-rows", default=None)
    ap.add_argument("--navtable", default=None)
    ap.add_argument("--design", default=None)
    ap.add_argument("--allowed-root", action="append", default=[])
    ap.add_argument("--settle", type=float, default=1.0)
    ap.add_argument("--only-routes", default=None, metavar="LIST")
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args_line = sys.argv[1:] if argv is None else list(argv)
    out = Path(a.out)
    try:
        window = parse_window(a.window)
        gates = [g for g in a.gates.split(",") if g]
        unknown = [g for g in gates if g not in GATES]
        if unknown:
            raise Fault(f"unknown gate {unknown[0]!r}; the gates are {', '.join(GATES)}")
        try:
            model = json.loads(Path(a.model).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise Fault(f"--model {a.model}: {e}") from None
        if model.get("schema") != "cadre-hmi-asm-model/1":
            raise Fault(f"--model {a.model} is not a cadre-hmi-asm-model/1 document")
        descriptors = descriptors_of(Path(a.build))
        if not descriptors:
            raise Fault(f"--build {a.build}: no descriptor of cadre-hmi-screen/1")
        navtable = json.loads(Path(a.navtable).read_text(encoding="utf-8")) if a.navtable else None
        design = json.loads(Path(a.design).read_text(encoding="utf-8")) if a.design else None
        only = None if a.only_routes is None else [r for r in a.only_routes.split(",") if r]
        bad = [r for r in only or [] if not r.startswith("/")]
        if bad:
            raise Fault(f"--only-routes {bad[0]!r} is not a route")
        plan = plan_of(model, descriptors, a.base, window, gates, a.raise_alarm, navtable, design, only)
        accepted = json.loads(Path(a.accepted_rows).read_text(encoding="utf-8")) if a.accepted_rows else []
        lane = None
        if plan["alarm"]:
            from walk_run import Tags, split_path
            roots = a.allowed_root or [model["tag_root"]]
            lane = Tags(allowed=roots, deploy=deploy)
            lane.check(plan["alarm"]["tag"])   # refused here, before any process, if outside the allowed roots
    except Fault as e:
        print(f"glass_gates: {e}")
        return 1
    except Exception as e:   # TagFolderRefused and the like: a refusal, before any input
        print(f"glass_gates: {type(e).__name__}: {str(e)[:300]}")
        return 1
    out.mkdir(parents=True, exist_ok=True)
    provenance.write_json(out / "plan.json", plan)   # first: before any input
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        print("glass_gates: the gates need Playwright: run under ctig's .venv")
        return 1
    root = next((n["name"] for n in model["nodes"] if n["parent"] is None), None)
    res = run_gates(plan, a.base, window, out, a.settle, lane, root)
    for g in res["gates"]:
        for st in g["steps"]:
            if f"{g['name']}:{st['action']}" in accepted:
                st["ok"] = True
                st["accepted"] = True
        if g["steps"]:
            g["ok"] = all(st["ok"] for st in g["steps"])
    doc = {"schema": "cadre-hmi-glass-gates/1", "base": plan["base"], "window": plan["window"], "plan": plan,
           "gates": res["gates"], "frame_before": res["frame_before"], "frame_after": res["frame_after"],
           "restored": res["restored"], "provenance": clock.provenance(TOOL, args_line, [Path(a.model)])}
    provenance.write_json(out / "gates.json", doc)
    failed = [g["name"] for g in doc["gates"] if not g["ok"]]
    print(f"glass_gates: gates {len(doc['gates'])}, failed {len(failed)}" + (f" ({', '.join(failed)})" if failed else "")
          + f", restored {doc['restored']}")
    return 0 if not failed and doc["restored"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
