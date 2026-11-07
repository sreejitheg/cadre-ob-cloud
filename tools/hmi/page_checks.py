"""The offline page checks of a built page set: coverage of the mapping rows, the navigation table walked, and every
value component on a tag.

Extends the descriptor coverage of `asm_descriptors.py` (`cadre-hmi-descriptor-coverage/1`) with the two checks the
reconstruction exercise ran by hand at Level 5: every original navigation target resolves to a route of the page set
or to a device a symbol opens, and every value component reads a tag (the exercise's view classifier). One command
line serves the page builder's exit check and the evidence pack. Nothing here contacts a gateway.

    page_checks.py --descriptors DIR --devices F --tags F --navtable F
                   [--design F --coverage-map F --mapping F --gaps F --route-map F] [--built DIR]
                   [--canvas WxH [--require-stretch]] --project P --out DIR

    --descriptors DIR  `cadre-hmi-screen/1` files
    --devices F        `cadre-hmi-devices/1`
    --tags F           the tag model (a tag folder document, as Ignition's tag export writes it)
    --navtable F       `wfb.migration.navtable/1`: `entries[]` with id, kind, source_window, source_object, label and
                       target, plus `route` (a page) or `device` (a faceplate) once resolved. An entry that names
                       neither is resolved by `--route-map`. A bare list of such entries is read as well
    --design F         `wfb.migration.project_design/1`: its `routes` table (`{target, treatment, route | device}`,
                       the target being a navigation entry's `id`) gives each entry its route or device; the
                       navigation table itself names no route, a route is the design's decision
    --route-map F      `{pages: {target: route}, faceplates: {target: device}, library_routes: [route]}`
    --mapping F        the mapping rows (a list, or `{mapping: [...]}` as the ASM model holds them): uid, source,
                       section, label
    --coverage-map F   `{uid: {drawn: [{kind, id}]}}`: the elements that carry each row
    --gaps F           `cadre-hmi-library-gaps/1` or `{gaps: [{id, mapping_rows}]}`: rows a gap accepts
    --built DIR        the generated project (the `com.inductiveautomation.perspective` folder or its parent):
                       the navigation is also checked against its page configuration and device index, and the
                       tags-bound count classifies each view's components as the exercise did
    --canvas WxH       the page canvas of the library frame at the profile's window (for example 1900x860): runs the
                       layout family L1 to L8 over every diagram page that draws a symbol (a stub page is skipped);
                       without it the family does not run and `layout` is null
    --inventory DIR    with `--canvas`: the original's text objects, `<DIR>/<page>/inventory.json` or `<DIR>/<page>.json`
                       (`objects` with `text`, `x`, `y`, `w`, `h`); it enables rule L11 for the pages it holds
    --require-stretch  with `--canvas`: every readout must state `params.stretch` true (rule L5)
    --project P        the project name (the built device index holds `[provider]<project>/<device>`)
    --out DIR          writes `checks.json`

`checks.json` is `cadre-hmi-descriptor-coverage/1` plus `coverage {rows, covered, missing}`, `navigation {total,
resolved, unresolved[]}`, `tags_bound {value_components, bound, unbound[], unresolved_tags[]}` and, with `--canvas`,
`layout {canvas, pages, findings[{page, rule, id, reason}], count}` (the `columns` key then holds one row for each
column of readouts). The layout rules: L1 the page fits the canvas; L2 the page fills it and the elements fill the page;
L3 a free line is only dashed or gated; L4 the readouts of one column share one width; L5 each readout stretches; L6 a
switch states `vertical`; L7 a device symbol states `readoutPosition`; L8 the toolbar is on; L9 symbols meet their pipes
on their axis, their orientation follows the pipes and an in-line switch has no readout; L10 a text fits its box and text
boxes (labels, symbols, section titles) do not overlap, a label drawn wholly inside a vessel (kind `tank`) clear of the
vessel's own texts and level being placed there on purpose; L11 (with `--inventory`) labels keep the original's order;
L12 a loose pipe end carries an arrow and a feeder ends in an arrow above its motor.

Exit codes: 0 every check passes; 2 a finding; 1 an input fault.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import assembly, provenance, vessel  # noqa: E402
else:
    from . import assembly, provenance, vessel

TOOL = "tools/hmi/page_checks.py"
SCHEMA = "cadre-hmi-descriptor-coverage/1"
# the kinds of element a mapping row names, and the descriptor list that holds each; an `assembly` entry names one
# part of a local assembly, `<assembly>/<part>` (NOTE-WFB-10 section 11.2 item 7)
KINDS = {"symbol": "symbols", "section": "sections", "label": "labels", "pipe": "pipes", "junction": "junctions",
         "button": "buttons", "link": "links", "line": "lines", "bracket": "brackets", "well": "wells",
         "trend": "trends", "bar": "bars", "assembly": "assemblies"}
# the library's own kinds: a symbol of any other kind is the counted gap box
LIBRARY_KINDS = {"pump", "motor", "fan", "valve", "analogvalve", "damper", "filter", "switch", "indicator", "tank",
                 "readout", "instrument-field", "controller", "sequence", "generator"}
# built components that read history or the frame, not a tag: the canvas zoom, the frame's views, the trends
UNBOUND_OK = ("cadre.ob.canvaszoom", "view:Framework/", "view:Parts/Trend")
MAX_LISTED = 200
LIBRARY_ROUTES = ("/alerts", "/trends")      # the frame's own pages: no descriptor draws them


class Fault(Exception):
    """An input the command cannot work with: exit 1."""


def read_json(path: str | Path, what: str):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Fault(f"{what} {path}: {e}") from None


def read_descriptors(folder: Path) -> tuple[dict[str, dict], list[str]]:
    """The screen descriptors by id, and the files that are none: a file without the schema or in the cards layout
    (`rows` and no drawn element) is a finding, never silently skipped."""
    if not folder.is_dir():
        raise Fault(f"--descriptors {folder} is not a folder")
    out: dict[str, dict] = {}
    refused: list[str] = []
    for f in sorted(folder.glob("*.json")):
        doc = read_json(f, "descriptor")
        cards = isinstance(doc, dict) and "rows" in doc and not any(doc.get(key) for key in KINDS.values())
        if isinstance(doc, dict) and doc.get("schema") == "cadre-hmi-screen/1" and not cards:
            out[doc.get("screen", {}).get("id") or f.stem] = doc
        elif cards:
            refused.append(f"{f.stem}: a cards layout, no drawn element (not cadre-hmi-screen/1)")
        else:
            refused.append(f"{f.stem}: not a cadre-hmi-screen/1 descriptor")
    if not out and not refused:
        raise Fault(f"--descriptors {folder}: no descriptor")
    return out, refused


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def device_of(symbol: dict) -> str | None:
    """The device a symbol opens: its `device` (true means its own id) or its plain `faceplate` key."""
    dev = symbol.get("device")
    dev = symbol["id"] if dev is True else dev
    return dev or symbol.get("faceplate") or None


# ---- coverage -------------------------------------------------------------------------------------------------
def check_coverage(rows: list[dict], cover: dict, gap_rows: set[str], descs: dict[str, dict]) -> tuple[list, list]:
    elements: dict[str, set[tuple[str, str]]] = {}
    gapboxes: dict[str, set[str]] = {}
    for pid, d in descs.items():
        elements[pid] = {(kind, e["id"]) for kind, key in KINDS.items() if kind != "assembly"
                         for e in d.get(key, []) if isinstance(e, dict) and "id" in e}
        elements[pid] |= {("assembly", f"{a.get('id')}/{p.get('id')}") for a in assembly.assemblies(d)
                          for _where, _array, p in assembly.parts_of(a)}
        gapboxes[pid] = {e["id"] for e in d.get("symbols", []) if str(e.get("kind", "")).lower() not in LIBRARY_KINDS}
    carried, missing = [], []
    for r in rows:
        uid, page = r["uid"], r.get("source")
        c = cover.get(uid) or {}
        drawn = c.get("drawn") or []
        by = [f"{e['kind']}:{e['id']}" for e in drawn]
        ok = bool(drawn) and all((e["kind"], e["id"]) in elements.get(page, set()) for e in drawn)
        gap = None
        if ok and all(e["kind"] == "symbol" and e["id"] in gapboxes.get(page, set()) for e in drawn):
            ok = uid in gap_rows   # only a counted gap box carries the row: a gap must say so
            gap = uid if ok else None
            if not ok:
                missing.append(f"{uid} [{r.get('section')}] drawn only as a gap box and not in a gap")
                carried.append({"uid": uid, "carried_by": by, "gap": None})
                continue
        if not ok and uid in gap_rows:
            ok, gap = True, c.get("gap") or "gap"
        carried.append({"uid": uid, "carried_by": by if ok else [], "gap": gap})
        if not ok:
            missing.append(f"{uid} [{r.get('section')}] {str(r.get('label', ''))[:70]}")
    return carried, missing


# ---- navigation -----------------------------------------------------------------------------------------------
def built_folder(path: Path) -> Path:
    for candidate in (path, path / "com.inductiveautomation.perspective"):
        if (candidate / "page-config").is_dir():
            return candidate
    for sub in sorted(path.glob("*/com.inductiveautomation.perspective")):
        if (sub / "page-config").is_dir():
            return sub
    raise Fault(f"--built {path}: no page-config folder (the generated project's perspective folder)")


def opened_devices(descs: dict[str, dict]) -> set[str]:
    """Every device some symbol or faceplate button of the descriptors opens."""
    opened: set[str] = set()
    for d in descs.values():
        symbols = {s["id"]: s for s in d.get("symbols", [])}
        for s in symbols.values():
            if device_of(s):
                opened.add(device_of(s))  # type: ignore[arg-type]
        for b in d.get("buttons", []):
            act = b.get("action") or {}
            if act.get("type") == "faceplate":
                sym = symbols.get(act.get("device"))
                opened.add((device_of(sym) if sym else None) or act.get("device"))
    opened.discard(None)
    return opened


def check_navigation(entries: list[dict], descs: dict[str, dict], devices: set[str], rmap: dict, cover: dict,
                     built: Path | None, project: str) -> tuple[int, list[dict]]:
    routes = {d.get("screen", {}).get("route") for d in descs.values()} | set(rmap.get("library_routes") or [])
    opened = opened_devices(descs)
    carriers: dict[tuple[str, str], str] = {}     # (page, element id) of a section, link or route button -> route
    button_devices: dict[tuple[str, str], str] = {}
    for pid, d in descs.items():
        for s in d.get("sections", []) + d.get("links", []):
            if s.get("route"):
                carriers[(pid, s["id"])] = s["route"]
        symbols = {s["id"]: s for s in d.get("symbols", [])}
        for b in d.get("buttons", []):
            act = b.get("action") or {}
            if act.get("type") == "route":
                carriers[(pid, b["id"])] = act.get("route")
            elif act.get("type") == "faceplate":
                sym = symbols.get(act.get("device"))
                button_devices[(pid, b["id"])] = (device_of(sym) if sym else None) or act.get("device")
    pages: set[str] = set()
    index: set[str] = set()
    if built:
        pages = set(read_json(built / "page-config" / "config.json", "page configuration").get("pages") or {})
        props = read_json(built / "session-props" / "props.json", "session properties").get("custom") or {}
        index = {d.get("folder") for d in props.get("devices") or []}
    bad: list[dict] = []
    for e in entries:
        target = e.get("target")
        device = e.get("device") or (rmap.get("faceplates") or {}).get(target)
        route = e.get("route") or (rmap.get("pages") or {}).get(target)
        why = None
        if device:
            if device not in devices:
                why = f"device {device} is not in the device model"
            elif device not in opened:
                why = f"device {device} is opened by no symbol or button of the descriptors"
            elif built and f"[default]{project}/{device}" not in index and not any(
                    i and str(i).endswith(f"/{device}") for i in index):
                why = f"device {device} is not in the built device index"
        elif route:
            if route not in routes:
                why = f"route {route} is no page of the descriptors or the library"
            elif built and route not in pages and route not in (rmap.get("library_routes") or []):
                why = f"route {route} is no page of the built project"
        else:
            why = ("the design has no route for this target" if e.get("no_design_row")
                   else "the target resolves to no route and no device")
        uid = e.get("uid")
        drawn = (cover.get(uid) or {}).get("drawn") if uid else None
        if why is None and drawn:
            page = str(uid).split(":")[0]
            ids = [(page, x["id"]) for x in drawn if x["kind"] in ("section", "link", "button")]
            if device and ids and not any(button_devices.get(k) == device for k in ids) and not any(
                    x["kind"] == "symbol" and device_of(next((s for s in descs.get(page, {}).get("symbols", [])
                                                              if s["id"] == x["id"]), {})) == device
                    for x in drawn):
                why = f"the element that carries it does not open device {device}"
            elif route and ids and not any(carriers.get(k) == route for k in ids):
                why = f"the element that carries it names no section with route {route}"
        if why:
            bad.append({"id": str(e.get("id", target)), "target": str(target), "reason": why})
    return len(entries), bad


# ---- tags bound -----------------------------------------------------------------------------------------------
def tag_paths(doc: dict) -> set[str]:
    leaves: set[str] = set()

    def walk(node: dict, prefix: str) -> None:
        for c in node.get("tags", []) or []:
            if c.get("tagType") == "Folder":
                walk(c, prefix + c["name"] + "/")
            else:
                leaves.add(prefix + c["name"])
    walk(doc, "")
    return leaves


def resolves(path: str, leaves: set[str], devices: dict[str, dict]) -> bool:
    if path in leaves:
        return True
    first, _, rest = path.partition("/")
    members = (devices.get(first) or {}).get("members") or {}
    return bool(rest) and (rest in members or rest.split("/")[0] in members or any(m.startswith(rest + "/") for m in members))


def descriptor_tags(descs: dict[str, dict]) -> list[tuple[str, str, list[str]]]:
    """(page, component id, the tag paths it reads) for every value component of the descriptors. Each dynamic part
    of a local assembly (a symbol or a button, its Home's included) is one, `<assembly>/<part>`, reading
    `<device>/<member>`; a part with no member reads none (T4)."""
    out: list[tuple[str, str, list[str]]] = []
    for pid, d in descs.items():
        for s in d.get("symbols", []):
            out.append((pid, s["id"], [str(v) for v in (s.get("bind") or {}).values() if v]))
        for t in d.get("trends", []):
            out.append((pid, t["id"], [p["tag"] for p in t.get("pens") or [] if p.get("tag")]))
        for w in d.get("wells", []):
            out.append((pid, w["id"], [m["tag"] for m in w.get("marks") or [] if m.get("tag")]))
        for b in d.get("bars", []):
            out.append((pid, b["id"], [str(b["tag"])] if b.get("tag") else []))
        for a in assembly.assemblies(d):
            device = a.get("device")
            for _array, p in assembly.dynamic_parts(a):
                member = p.get("member")
                out.append((pid, f"{a.get('id')}/{p.get('id')}",
                            [f"{device}/{member}"] if member and isinstance(device, str) and device else []))
    return out


def classify(c: dict, tagcustom: set[str]) -> str:
    """The exercise's view classifier (`vtree.py`, `tagcount.py`): how one built component reads its value."""
    reads_tag = via_custom = False
    for k, v in (c.get("propConfig") or {}).items():
        b = v.get("binding")
        if not b:
            continue
        cfg = b.get("config") or {}
        expr = cfg.get("expression") or cfg.get("tagPath") or cfg.get("path") or ""
        if b.get("type") == "tag":
            reads_tag = True
        elif b.get("type") in ("expr", "property"):
            refs = re.findall(r"\{view\.custom\.([A-Za-z0-9_]+)\}", expr)
            if b.get("type") == "property" and "view.custom." in expr:
                refs.append(expr.split("view.custom.")[1])
            via_custom = via_custom or any(r in tagcustom for r in refs)
            reads_tag = reads_tag or bool(re.search(r"\{\[", expr) or "tag(" in expr)
        elif b.get("type") == "expr-struct":
            s = json.dumps(b)
            reads_tag = reads_tag or "[default]" in s
            via_custom = via_custom or any(f"view.custom.{r}" in s for r in tagcustom)
    params = (c.get("props") or {}).get("params") or {} if c.get("type") == "ia.display.view" else {}
    own = params.get("deviceId") or params.get("device") or params.get("tagPath") or params.get("basePath")
    if reads_tag:
        return "tag binding on the component"
    if via_custom:
        return "tag via view.custom"
    return "device view (binds its own tags)" if own else "no tag"


def built_tags(built: Path, pages: list[str]) -> tuple[Counter, list[str]]:
    """The view classes of the built pages' components, and the value components that read no tag: the views
    `Screens/<page>` of the pages and every view under `Local/` (the local assemblies' kinds and their Homes,
    NOTE-WFB-10 section 11.2 item 7), each entry named by its view (`<page>`, `Local/<Kind>/Assembly` or `Local/<Kind>/Home`)."""
    counts: Counter = Counter()
    unbound: list[str] = []
    views = [(page, built / "views" / "Screens" / page / "view.json") for page in pages]
    local = built / "views" / assembly.VIEW_ROOT
    if local.is_dir():
        views += [(f.parent.relative_to(built / "views").as_posix(), f) for f in sorted(local.rglob("view.json"))]
    for page, f in views:
        if not f.is_file():
            continue
        v = read_json(f, "view")
        pc = v.get("propConfig") or {}
        tagcustom = {k.split(".", 1)[1] for k, c in pc.items()
                     if k.startswith("custom.") and (c.get("binding") or {}).get("type") == "tag"}

        def walk(c: dict) -> None:
            t = c.get("type", "")
            cls = classify(c, tagcustom)
            if t.startswith("cadre.ob.") or t == "ia.display.view" or (
                    t in ("ia.display.label", "ia.shapes.svg") and cls != "no tag"):
                kind = t if t != "ia.display.view" else "view:" + str((c.get("props") or {}).get("path"))
                counts[(page, kind, cls)] += 1
                if cls == "no tag" and not kind.startswith(UNBOUND_OK):
                    unbound.append(f"{page}:{(c.get('meta') or {}).get('name')} ({kind})")
            for ch in c.get("children") or []:
                walk(ch)
        walk(v.get("root") or {})
    return counts, unbound


# ---- layout ---------------------------------------------------------------------------------------------------
LAYOUT_SCREEN_FILL = 0.95       # the page is at least this share of the canvas, each way
LAYOUT_FILL_X = 0.90            # the elements reach this share of the page width (the largest right edge)
LAYOUT_FILL_Y = 0.85            # and this share of its height (the largest bottom edge)
COLUMN_TOLERANCE = 4            # readouts whose x lie within this many pixels form a column
STATUS_KINDS = {"motor", "pump", "fan", "valve", "switch", "generator", "indicator"}   # kinds that state a status position
BOXED = ("symbols", "labels", "sections", "buttons", "links", "brackets", "wells", "trends", "bars", "alarmPanels",
         "assemblies")


def page_extent(d: dict) -> tuple[float, float]:
    """The largest right and bottom edge of the drawn elements: boxes (a bracket is x to x + w), the points of lines,
    the `via` points and the coordinate ends of pipes, and junctions."""
    xs: list[float] = [0]
    ys: list[float] = [0]
    for key in BOXED:
        for e in d.get(key) or []:
            if isinstance(e.get("x"), (int, float)) and isinstance(e.get("y"), (int, float)):
                xs.append(e["x"] + (e.get("w") or 0))
                ys.append(e["y"] + (e.get("h") or 0))
    for e in d.get("junctions") or []:
        xs.append(e.get("x", 0))
        ys.append(e.get("y", 0))
    points = [p for ln in d.get("lines") or [] for p in ln.get("points") or []]
    for pipe in d.get("pipes") or []:
        points += pipe.get("via") or []
        points += [[end["x"], end["y"]] for end in (pipe.get("from"), pipe.get("to"))
                   if isinstance(end, dict) and "x" in end and "y" in end]
    for p in points:
        xs.append(p[0])
        ys.append(p[1])
    return max(xs), max(ys)


def readout_columns(page: str, symbols: list[dict]) -> list[dict]:
    """The readouts whose x lie within COLUMN_TOLERANCE of the next one's, grouped; a group of one is no column."""
    readouts = sorted((s for s in symbols if str(s.get("kind", "")).lower() == "readout"), key=lambda s: s.get("x", 0))
    groups: list[list[dict]] = []
    for s in readouts:
        if groups and s.get("x", 0) - groups[-1][-1].get("x", 0) <= COLUMN_TOLERANCE:
            groups[-1].append(s)
        else:
            groups.append([s])
    cols = []
    for g in groups:
        if len(g) > 1:
            widths = sorted({s.get("w") for s in g}, key=lambda w: (w is None, w))
            cols.append({"page": page, "x": g[0].get("x", 0), "widths": widths, "ok": len(widths) == 1,
                         "ids": [s.get("id") for s in g]})
    return cols


# ---- layout: alignment, text and label order (L9 to L11) ----------------------------------------------------------
AXIS_TOL = 2                    # L9: a pipe's adjacent point lies on the symbol's axis within this many pixels
SYMBOL_PX = 48                  # the box of an automation symbol when the descriptor gives none (`screen.symbol_box`)
OPPOSITE = {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}
# L9c: library views whose icon is centred together with its identifier inside an embed that the generator sizes for the
# full readout extent (`screen.symbol_box`, `readout_extent`). Any readout position but none moves the icon off a line
# that runs through the descriptor box: measured 28 px for a horizontal switch with the readout on top, 13 px and 9 px
# for vertical switches with it left and right. Add another kind here when it is measured to do the same.
INLINE_VIEW_KINDS = {"switch"}
CHAR_PX = 6.0                   # L10: the width of a character at a 12 px font; a lower bound (the render: 6.0 to 6.9)
FONT_PX = {"label": 12, "body": 16, "heading": 24}   # the label styles of `screen.text_label` (tokens: label, body, subtitle)
LINE_RATIO = 4 / 3              # line height over font size (16 px lines at 12 px, 32 px at 24 px)
TEXT_FIT_SLACK = 4              # a text may exceed its box by this many pixels
OVERLAP_TOL = 2                 # L10: boxes overlap when they share more than this many pixels each way
SECTION_PAD = (8, 4)            # the title of a section: padding x and y, top right inside it (`screen.section_node`)
# symbols whose view draws one of their params as a title across the symbol's width (Instrument/Sequence, Instrument/Field)
TITLE_PARAMS = {"sequence": "label", "instrument-field": "label"}
ORDER_MIN = 8                   # L11: positions must differ by this many pixels to count
ORDER_SPAN_Y = 200              # L11: labels of one column of the original this far apart in y are compared
ORDER_SPAN_X = 300              # and labels of one row this far apart in x


def sym_box(s: dict) -> tuple[float, float, float, float] | None:
    default = SYMBOL_PX if str(s.get("kind", "")).lower() in STATUS_KINDS else None
    w, h = s.get("w") or default, s.get("h") or default
    if not (w and h and isinstance(s.get("x"), (int, float)) and isinstance(s.get("y"), (int, float))):
        return None
    return s["x"], s["y"], w, h


def side_point(box: tuple[float, float, float, float], side: str | None) -> tuple[float, float]:
    x, y, w, h = box
    return {"left": (x, y + h / 2), "right": (x + w, y + h / 2), "top": (x + w / 2, y),
            "bottom": (x + w / 2, y + h)}.get(side or "", (x + w / 2, y + h / 2))


def end_point(end, symbols: dict, junctions: dict) -> tuple[float, float] | None:
    """Where a pipe end is: its coordinates, a junction's, or a symbol's side point (its centre without a side)."""
    if not isinstance(end, dict):
        return None
    if "ref" in end:
        if end["ref"] in junctions:
            return junctions[end["ref"]]
        box = sym_box(symbols[end["ref"]]) if end["ref"] in symbols else None
        if box:
            return side_point(box, end.get("side"))
    if isinstance(end.get("x"), (int, float)) and isinstance(end.get("y"), (int, float)):
        return end["x"], end["y"]
    return None


def alignment_findings(d: dict) -> list[tuple[str, str]]:
    """L9: (symbol id, reason) for the symbols a pipe meets off their axis, with a wrong orientation, or in line with
    a readout position that moves their icon off the line."""
    symbols = {s["id"]: s for s in d.get("symbols") or [] if isinstance(s, dict) and "id" in s}
    junctions = {j["id"]: (j["x"], j["y"]) for j in d.get("junctions") or [] if "id" in j and "x" in j and "y" in j}
    out: list[tuple[str, str]] = []
    sides: dict[str, list[str]] = {}
    for pipe in d.get("pipes") or []:
        ends = (pipe.get("from"), pipe.get("to"))
        via = [tuple(p) for p in pipe.get("via") or []]
        for i, end in enumerate(ends):
            if not isinstance(end, dict) or end.get("ref") not in symbols or not end.get("side"):
                continue
            sid, side = end["ref"], end["side"]
            sides.setdefault(sid, []).append(side)
            box = sym_box(symbols[sid])
            adj = (via[0] if i == 0 else via[-1]) if via else end_point(ends[1 - i], symbols, junctions)
            if not box or not adj:
                continue
            cx, cy = side_point(box, None)
            here = "h" if side in ("left", "right") else "v"
            off = abs(adj[1] - cy) if here == "h" else abs(adj[0] - cx)
            # the router (`diagram.route`) bends a pipe at a corner of its own, so a point off the axis is a defect only
            # where the pipe would jog or enter sideways: a Z (both ends on one axis), or a via point reached along x
            # first (a vertical side left sideways, a horizontal side entered vertically)
            other = ends[1 - i]
            other_axis = ("h" if other.get("side") in ("left", "right") else "v") if other.get("side") \
                and other.get("ref") in symbols else "-"
            if via:
                bad = here == "v" if i == 0 else here == "h"
            else:
                bad = here == other_axis
            if bad and off > AXIS_TOL:
                axis = f"y {cy:g}" if here == "h" else f"x {cx:g}"
                out.append((sid, f"Pipe {pipe.get('id')} meets the {side} of {sid} {off:g} px off its centre line: put "
                                 f"the pipe's next point at {axis}, or move the symbol onto the pipe."))
    for sid, ss in sides.items():
        s = symbols[sid]
        params = s.get("params") or {}
        kind = str(s.get("kind", "")).lower()
        vertical = [x in ("top", "bottom") for x in ss]
        if kind == "switch" or "vertical" in params:
            if all(vertical) != any(vertical):
                out.append((sid, f"The pipes meet {sid} on mixed sides ({', '.join(sorted(set(ss)))}): a symbol takes "
                                 "its pipes on top and bottom (vertical true) or on left and right (vertical false)."))
            elif isinstance(params.get("vertical"), bool) and params["vertical"] != all(vertical):
                out.append((sid, f"Set params.vertical {str(all(vertical)).lower()} on {sid}: its pipes meet it on "
                                 f"{'/'.join(sorted(set(ss)))}."))
        inline = any(OPPOSITE[x] in ss for x in set(ss))
        if kind in INLINE_VIEW_KINDS and inline and params.get("readoutPosition") != "none":
            out.append((sid, f"Set params.readoutPosition none on {sid}, an in-line {kind}: with a readout beside it the "
                             "view moves the icon off the line; draw its name as a label instead."))
    return out


def text_lines(text: str, w: float, px: float) -> tuple[float, int]:
    """(the widest line's estimated width, the lines the text needs in a box w wide) at a font of px."""
    scale = CHAR_PX * px / 12
    widths = [len(line) * scale for line in str(text).split("\n")]
    return max(widths), sum(max(1, math.ceil(width / (w + TEXT_FIT_SLACK))) for width in widths)


def label_style_px(t: dict) -> int:
    return FONT_PX.get(t.get("style", "label"), FONT_PX["label"])


def text_extent(t: dict) -> tuple[float, float, float, float]:
    """Where the text of a label lies: its estimated width placed in the box by its alignment (it overflows the box
    that way when wider), the box's height; a box tall enough for two lines is taken whole."""
    x, y, w, h = t["x"], t["y"], t["w"], t["h"]
    px = label_style_px(t)
    wide, _ = text_lines(t["text"], w, px)
    if int(h // (px * LINE_RATIO)) >= 2:
        return x, y, w, h
    align = t.get("align", "left")
    return {"left": (x, y, wide, h), "right": (x + w - wide, y, wide, h),
            "center": (x + (w - wide) / 2, y, wide, h)}.get(align, (x, y, wide, h))


def overlaps(a: tuple, b: tuple) -> bool:
    return (min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]) > OVERLAP_TOL
            and min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]) > OVERLAP_TOL)


def label_on_symbol(a: str, ba: tuple, s: dict, bb: tuple) -> str | None:
    """The L10 reason for a label whose text overlaps a symbol's box, or None where it is placed there on purpose: a
    label wholly inside a vessel and clear of the vessel's own bands."""
    b = str(s.get("id"))
    if str(s.get("kind", "")).lower() not in vessel.CONTAINER_KINDS:
        return f"The label {a} lies over the symbol {b}: move it clear of the symbol's box."
    within, covered = vessel.placed_inside(ba, bb, s.get("params"), OVERLAP_TOL)
    if not within:
        return (f"The label {a} lies across the outline of the vessel {b}: draw it wholly inside the vessel or clear "
                "of it.")
    if covered:
        return (f"The label {a} covers the {' and the '.join(covered)} of the vessel {b}: move it to a free part of "
                "the vessel.")
    return None


def title_band(sec: dict) -> tuple[float, float, float, float] | None:
    """Where a section's title sits: top right inside the section, in the label font with the section's padding."""
    if not sec.get("label"):
        return None
    wide = min(len(str(sec["label"])) * CHAR_PX + 2 * SECTION_PAD[0], sec["w"])
    return (sec["x"] + sec["w"] - wide, sec["y"], wide, FONT_PX["label"] * LINE_RATIO + 2 * SECTION_PAD[1])


def text_findings(d: dict, symbols: list[dict]) -> list[tuple[str, str]]:
    """L10: (element ids, reason) for a text wider than its box and for texts, symbols and section titles that overlap
    (a label is measured at the width of its text, not of its box)."""
    out: list[tuple[str, str]] = []
    labels = [t for t in d.get("labels") or [] if isinstance(t, dict) and all(
        isinstance(t.get(k), (int, float)) for k in ("x", "y", "w", "h")) and t.get("text") is not None]
    for t in labels:
        px = label_style_px(t)
        wide, need = text_lines(t["text"], t["w"], px)
        if need > max(1, int(t["h"] // (px * LINE_RATIO))):
            out.append((str(t["id"]), f"The text of {t['id']} is wider than its box ({wide:g} px against {t['w']:g}): "
                                      "widen the box, shorten the text, or make the box tall enough for two lines."))
    for s in symbols:
        key = TITLE_PARAMS.get(str(s.get("kind", "")).lower())
        title = (s.get("params") or {}).get(key) if key else None
        box = sym_box(s)
        if title and box and text_lines(title, box[2], FONT_PX["label"])[1] > 1:
            out.append((str(s.get("id")), f"The title '{title}' of {s.get('id')} is wider than the symbol ({box[2]:g} px): "
                                          "shorten the title or widen the symbol."))
    boxes = [(str(t["id"]), text_extent(t)) for t in labels]
    for i, (a, ba) in enumerate(boxes):
        for b, bb in boxes[i + 1:]:
            if overlaps(ba, bb):
                out.append((f"{a}, {b}", f"The labels {a} and {b} overlap: move one of them clear of the other."))
    symboxes = [(str(s.get("id")), sym_box(s)) for s in symbols]
    for a, ba in boxes:
        for s, (b, bb) in zip(symbols, symboxes):
            reason = label_on_symbol(a, ba, s, bb) if bb and overlaps(ba, bb) else None
            if reason:
                out.append((f"{a}, {b}", reason))
    sections = [x for x in d.get("sections") or [] if isinstance(x, dict) and all(
        isinstance(x.get(k), (int, float)) for k in ("x", "y", "w", "h"))]
    for sec in sections:
        band = title_band(sec)
        if not band:
            continue
        covers = [(a, "label", ba) for a, ba in boxes] + [(b, "symbol", bb) for b, bb in symboxes if bb]
        covers += [(str(o["id"]), "section", (o["x"], o["y"], o["w"], o["h"])) for o in sections
                   if o is not sec and o["x"] >= sec["x"] - OVERLAP_TOL and o["y"] >= sec["y"] - OVERLAP_TOL
                   and o["x"] + o["w"] <= sec["x"] + sec["w"] + OVERLAP_TOL
                   and o["y"] + o["h"] <= sec["y"] + sec["h"] + OVERLAP_TOL]       # a section nested in this one
        for ident, what, box in covers:
            if overlaps(box, band):
                out.append((f"{ident}, {sec['id']}", f"The {what} {ident} covers the title of section {sec['id']} (top "
                                                     "right inside it): move it below the title band or aside."))
    return out


def norm_text(text) -> str:
    return " ".join(str(text).split()).casefold()


def read_inventory(folder: Path, pages) -> dict[str, list[dict]]:
    """The original's text objects of each page: `<folder>/<page>/inventory.json` or `<folder>/<page>.json`, each with
    `objects`; a text object is one with a `text`. A page with no file is left out."""
    if not folder.is_dir():
        raise Fault(f"--inventory {folder} is not a folder")
    out: dict[str, list[dict]] = {}
    for page in pages:
        for f in (folder / page / "inventory.json", folder / f"{page}.json"):
            if f.is_file():
                doc = read_json(f, "inventory")
                objs = doc.get("objects") if isinstance(doc, dict) else doc
                out[page] = [o for o in objs or [] if isinstance(o, dict) and isinstance(o.get("text"), str)
                             and o["text"].strip() and all(isinstance(o.get(k), (int, float)) for k in ("x", "y"))]
                break
    return out


def order_findings(d: dict, texts: list[dict]) -> list[tuple[str, str]]:
    """L11: (ids, reason) for two labels the original has in one column or row whose built order is the other way."""
    seen = Counter(norm_text(o["text"]) for o in texts)
    built = [t for t in d.get("labels") or [] if isinstance(t, dict) and isinstance(t.get("x"), (int, float))
             and isinstance(t.get("y"), (int, float)) and t.get("text")]
    seen_built = Counter(norm_text(t["text"]) for t in built)
    originals = {norm_text(o["text"]): o for o in texts if seen[norm_text(o["text"])] == 1}
    pairs = [(t, originals[norm_text(t["text"])]) for t in built
             if seen_built[norm_text(t["text"])] == 1 and norm_text(t["text"]) in originals]
    out: list[tuple[str, str]] = []

    def span(o: dict, axis: str) -> tuple[float, float]:
        return o[axis], o[axis] + (o.get("w" if axis == "x" else "h") or 0)

    for i, (ta, oa) in enumerate(pairs):
        for tb, ob in pairs[i + 1:]:
            for axis, other, limit in (("y", "x", ORDER_SPAN_Y), ("x", "y", ORDER_SPAN_X)):
                (a0, a1), (b0, b1) = span(oa, other), span(ob, other)
                if min(a1, b1) - max(a0, b0) <= 0:
                    continue                                    # not in one column (or row) of the original
                gap = ob[axis] - oa[axis]
                if not ORDER_MIN <= abs(gap) <= limit:
                    continue
                first, second = (ta, tb) if gap > 0 else (tb, ta)
                if first[axis] - second[axis] >= ORDER_MIN:
                    word = "above" if axis == "y" else "left of"
                    out.append((f"{ta['id']}, {tb['id']}", f"Put them back in the original's order: {first['id']} is "
                                                           f"{word} {second['id']} in the original."))
    return out


# L12: a feeder ends in an arrow just short of the machine it feeds; a pipe of these kinds with no medium (or the neutral
# one, an electrical bus or feeder) that joins the symbol hides the flow's direction. A process flow through a machine
# carries its medium and is no feeder.
FEEDER_KINDS = {"motor"}


def end_findings(d: dict) -> list[tuple[str, str]]:
    """L12: (pipe id, reason) for a loose pipe end (x and y, joined to nothing) with no arrow, and for a feeder that
    joins its motor instead of ending in an arrow above it."""
    kinds = {s.get("id"): str(s.get("kind", "")).lower() for s in d.get("symbols") or [] if isinstance(s, dict)}
    out: list[tuple[str, str]] = []
    for pipe in d.get("pipes") or []:
        pid = str(pipe.get("id"))
        for key, arrow, where in (("from", "arrow-in", "where the flow enters"), ("to", "arrow-out", "where it leaves")):
            end = pipe.get(key)
            if isinstance(end, dict) and "ref" not in end and end.get("end") not in ("arrow-in", "arrow-out"):
                out.append((pid, f"End the pipe's loose {key} end with an arrow ({arrow} {where}): a loose end drawn "
                                 f"{end.get('end') or 'plain'} ends the flow blunt in empty space."))
        to = pipe.get("to")
        if isinstance(to, dict) and kinds.get(to.get("ref")) in FEEDER_KINDS and pipe.get("medium") in (None, "neutral"):
            out.append((pid, f"End the feeder in an arrow-out just above {to['ref']} rather than joining it: the arrow "
                             "shows the supply going into the machine."))
    return out


def check_layout(descs: dict[str, dict], canvas_w: float, canvas_h: float, require_stretch: bool,
                 inventory: dict[str, list[dict]] | None = None) -> dict:
    """The objective layout rules L1 to L12 over every drawn diagram page (a page with no symbol is a stub and is
    skipped): {pages, findings [{page, rule, id, reason}], columns [{page, x, widths, ok}]}. `inventory` is the
    original's text objects by page (`read_inventory`); without it L11 does not run."""
    findings: list[dict] = []
    columns: list[dict] = []
    pages = 0

    for page, d in descs.items():
        scr = d.get("screen") or {}
        symbols = [s for s in d.get("symbols") or [] if isinstance(s, dict)]
        if scr.get("layout", "diagram") != "diagram" or not symbols:
            continue
        pages += 1

        def found(rule: str, ident: str, reason: str) -> None:
            findings.append({"page": page, "rule": rule, "id": ident, "reason": reason})

        w, h = scr.get("width"), scr.get("height")
        if not isinstance(w, (int, float)) or not isinstance(h, (int, float)):
            found("L1", page, f"State screen.width and screen.height: the page canvas is {canvas_w:g}x{canvas_h:g}.")
        else:
            if w > canvas_w or h > canvas_h:
                found("L1", page, f"Set screen.width and screen.height to at most {canvas_w:g}x{canvas_h:g}: a larger "
                                  f"page ({w:g}x{h:g}) renders below scale 1.0 and its text shrinks.")
            if w < LAYOUT_SCREEN_FILL * canvas_w or h < LAYOUT_SCREEN_FILL * canvas_h:
                found("L2", page, f"Set screen.width and screen.height to at least {LAYOUT_SCREEN_FILL * canvas_w:g}x"
                                  f"{LAYOUT_SCREEN_FILL * canvas_h:g}: the page ({w:g}x{h:g}) leaves the canvas "
                                  f"{canvas_w:g}x{canvas_h:g} unused.")
            right, bottom = page_extent(d)
            short = []
            if right < LAYOUT_FILL_X * w:
                short.append(f"width: the elements reach {right:g} of {w:g}, below {LAYOUT_FILL_X:.0%}")
            if bottom < LAYOUT_FILL_Y * h:
                short.append(f"height: the elements reach {bottom:g} of {h:g}, below {LAYOUT_FILL_Y:.0%}")
            if short:
                found("L2", page, "Spread the elements over the whole page (" + "; ".join(short) + ").")
        for ln in d.get("lines") or []:
            if ln.get("style") != "dashed" and not ln.get("gate"):
                found("L3", str(ln.get("id")), "Draw the flow as a pipe from and to its symbols or junctions; a free "
                      "line is only an interlock (dashed) or a gated bus.")
        for col in readout_columns(page, symbols):
            columns.append({k: col[k] for k in ("page", "x", "widths", "ok")})
            if not col["ok"]:
                shown = ", ".join("none" if x is None else f"{x:g}" for x in col["widths"])
                found("L4", ", ".join(col["ids"]), f"Give the readouts in the column at x {col['x']:g} one width "
                      f"(they have widths {shown}).")
        for s in symbols:
            kind, params = str(s.get("kind", "")).lower(), s.get("params") or {}
            if kind == "readout" and require_stretch and params.get("stretch") is not True:
                found("L5", s.get("id"), "Set params.stretch true on the readout so that it fills its column.")
            if kind == "switch" and not isinstance(params.get("vertical"), bool):
                found("L6", s.get("id"), "State params.vertical (true or false) on the switch: its orientation is not a default.")
            # a generator drawn as a picture (the genset) writes its own status under its identifier (wiki/13 12.2)
            pictured = kind == "generator" and params.get("picture")
            if kind in STATUS_KINDS and "readoutPosition" not in params and not pictured:
                found("L7", s.get("id"), f"State params.readoutPosition on the {kind} (a side, or none): its status "
                      "position is not a default.")
        for rule, items in (("L9", alignment_findings(d)), ("L10", text_findings(d, symbols)),
                            ("L11", order_findings(d, inventory[page]) if inventory and page in inventory else []),
                            ("L12", end_findings(d))):
            for ident, reason in items:
                found(rule, ident, reason)
        if d.get("toolbar") is False:
            found("L8", page, "Set toolbar true (or leave it out): the operator toolbar belongs on every page.")
    return {"pages": pages, "findings": findings, "columns": columns}


# ---- the run --------------------------------------------------------------------------------------------------
def join_design(entries: list[dict], design) -> list[dict]:
    """Give each navigation entry the route or device the design decided (`routes[]`, joined on the entry's id)."""
    rows = {str(r.get("target")): r for r in (design or {}).get("routes") or [] if isinstance(r, dict)}
    out = []
    for e in entries:
        row = rows.get(str(e.get("id")))
        e = dict(e)
        if row and row.get("treatment") in ("page", "support") and row.get("route"):
            e.setdefault("route", row["route"])
        elif row and row.get("treatment") == "faceplate" and row.get("device"):
            e.setdefault("device", row["device"])
        elif row is None:
            e["no_design_row"] = True
        out.append(e)
    return out


def navigation_entries(doc) -> list[dict]:
    entries = doc if isinstance(doc, list) else doc.get("entries") if isinstance(doc, dict) else None
    if not isinstance(entries, list):
        raise Fault("--navtable holds no entries")
    return [e for e in entries if isinstance(e, dict)]


def main(argv: list[str] | None = None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    ap.add_argument("--descriptors", required=True)
    ap.add_argument("--devices", required=True)
    ap.add_argument("--tags", required=True)
    ap.add_argument("--navtable", required=True)
    ap.add_argument("--route-map", default=None)
    ap.add_argument("--design", default=None)
    ap.add_argument("--mapping", default=None)
    ap.add_argument("--coverage-map", default=None)
    ap.add_argument("--gaps", default=None)
    ap.add_argument("--built", default=None)
    ap.add_argument("--canvas", default=None, help="WxH of the page canvas: runs the layout family")
    ap.add_argument("--inventory", default=None, help="with --canvas: the original's text objects, for rule L11")
    ap.add_argument("--require-stretch", action="store_true", help="with --canvas: every readout stretches (L5)")
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args_line = sys.argv[1:] if argv is None else list(argv)
    try:
        canvas = None
        if a.canvas is not None:
            m = re.fullmatch(r"(\d+)x(\d+)", a.canvas)
            if not m or not int(m[1]) or not int(m[2]):
                raise Fault(f"--canvas {a.canvas}: expected WxH in pixels, for example 1900x860")
            canvas = (int(m[1]), int(m[2]))
        descs, refused = read_descriptors(Path(a.descriptors))
        inventory = read_inventory(Path(a.inventory), list(descs)) if a.inventory and canvas else None
        devices_doc = read_json(a.devices, "--devices")
        devices = {d["id"]: d for d in devices_doc.get("devices") or []}
        leaves = tag_paths(read_json(a.tags, "--tags"))
        entries = navigation_entries(read_json(a.navtable, "--navtable"))
        rmap = read_json(a.route_map, "--route-map") if a.route_map else {}
        if a.design:
            entries = join_design(entries, read_json(a.design, "--design"))
        rmap = {**rmap, "library_routes": [*(rmap.get("library_routes") or []), *LIBRARY_ROUTES]}
        cover = read_json(a.coverage_map, "--coverage-map") if a.coverage_map else {}
        built = built_folder(Path(a.built)) if a.built else None
        rows: list[dict] = []
        if a.mapping:
            m = read_json(a.mapping, "--mapping")
            rows = [r for r in (m if isinstance(m, list) else m.get("mapping") or []) if isinstance(r, dict)]
            rows = [r for r in rows if r.get("source") in descs] or rows
        gap_rows: set[str] = set()
        if a.gaps:
            g = read_json(a.gaps, "--gaps")
            gap_rows = {r for gap in (g.get("gaps") if isinstance(g, dict) else g) or []
                        for r in (gap.get("mapping_rows") or [])}
    except Fault as e:
        print(f"page_checks: {e}")
        return 1
    carried, missing = check_coverage(rows, cover, gap_rows, descs)
    total, unresolved = check_navigation(entries, descs, set(devices), rmap, cover, built, a.project)
    components = descriptor_tags(descs)
    unbound = [f"{p}:{i}" for p, i, tags in components if not tags]
    unresolved_tags = sorted({f"{p}:{i} {t}" for p, i, tags in components for t in tags if not resolves(t, leaves, devices)})
    value_components = len(components)
    bound = value_components - len(unbound)
    view_counts = {}
    if built:
        counts, view_unbound = built_tags(built, list(descs))
        view_counts = {f"{p} | {k} | {c}": n for (p, k, c), n in sorted(counts.items())}
        unbound += view_unbound
    unbound = [*refused, *unbound]
    lay = check_layout(descs, *canvas, a.require_stretch, inventory) if canvas else None
    layout_total = len(lay["findings"]) if lay else 0
    findings = len(missing) + len(unresolved) + len(unbound) + len(unresolved_tags) + layout_total
    routes = [{"target": str(e.get("target")), "resolution": "faceplate" if e.get("device") else "page",
               **({"device": e["device"]} if e.get("device") else {"route": e.get("route", "")})} for e in entries]
    doc = {
        "schema": SCHEMA,
        "rows": carried, "missing": missing, "routes": routes,
        "unresolved": [{"target": u["target"], "reason": u["reason"]} for u in unresolved],
        "module_first": [], "columns": lay["columns"] if lay else [],
        "coverage": {"rows": len(rows), "covered": len(rows) - len(missing), "missing": missing[:MAX_LISTED]},
        "navigation": {"total": total, "resolved": total - len(unresolved), "unresolved": unresolved[:MAX_LISTED]},
        "tags_bound": {"value_components": value_components, "bound": bound, "unbound": unbound[:MAX_LISTED],
                       "unresolved_tags": unresolved_tags[:MAX_LISTED], "view_classes": view_counts},
        "layout": ({"canvas": a.canvas, "pages": lay["pages"], "findings": lay["findings"][:MAX_LISTED],
                    "count": layout_total} if lay else None),
        "provenance": clock.provenance(TOOL, args_line, [Path(a.descriptors)]),
    }
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    provenance.write_json(out / "checks.json", doc)
    print(f"page_checks: coverage {doc['coverage']['covered']} of {len(rows)}, "
          f"navigation {doc['navigation']['resolved']} of {total}, tags bound {bound} of {value_components}"
          f"{' (view classes counted)' if built else ''}, "
          f"{f'layout {layout_total} findings, ' if lay else ''}findings {findings}")
    for line in [*missing, *(f"{u['target']}: {u['reason']}" for u in unresolved), *(f"unbound {u}" for u in unbound),
                 *(f"tag not found {t}" for t in unresolved_tags)][:40]:
        print("   ", line)
    for f in (lay["findings"][:40] if lay else []):
        print("   ", f"layout {f['page']} {f['rule']} {f['id']}: {f['reason']}")
    return 2 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
