"""The HTML preview of a migration, both modes from one renderer (ARCH-WFB-01 revision B8 Table 109, WFBD-092).

    --mode recon   the one to one view: every page of the understandings at the original's geometry, every
                   pop-up set as the content of a faceplate, with the simulation.
                   Inputs: --understandings LIST --faceplates F --inventory DIR --tables F
    --mode asm     the ASM view: the model's hierarchy, the page designs, faceplates that dock and float, search.
                   Inputs: --model F --designs LIST --faceplates F --tables F
    --window WxH --checks LIST --bundle --pictures --out O

Writes `O/site/` (index.html, style.css, renderer.js and the pictures: the multi-file preview with the simulation),
`O/preview.html` with `--bundle` (one self-contained file: the fixed style and scripts inline, the run's data in
`application/json` blocks, nothing external), `O/pictures/<page>.png` and `<faceplate>.png` with `--pictures`, and
`O/checks.json` (`cadre-hmi-preview-checks/1`).

The bundle is inert (B8 section 29.9, ARCH-D168 as revised, finding R17): its scripts are the renderer's fixed text,
pinned by SHA-256 in `checks.json` (`script_hashes`); every value of the run sits in a `type="application/json"`
block with `<`, `>` and `&` escaped and is read through `textContent`; there is no inline handler, no external
reference and no `javascript:` address. `checks.json` counts all three, and a bundle that fails them fails the run.

The checks run in headless Chromium under Playwright (ctig's `.venv`) with real input: clicks, typing, a drag.
    coverage    every uid of the model (or of the understandings) is drawn as a `data-uid`, or given a treatment
    navigation  every navigation row is walked and ends where its resolution says
    search      a page, a device and a tag are found and open
    dock        a faceplate opens in the right dock inside the window and closes
    float       the faceplate floats, can be dragged, and docks again

Exit codes: 0 every check passes; 2 a check or the bundle failed; 1 a fault.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import asm_model, provenance  # noqa: E402
    from hmi.asm_model import InputFault, load, path_list  # noqa: E402
else:
    from . import asm_model, provenance
    from .asm_model import InputFault, load, path_list

ASSETS = Path(__file__).resolve().parent / "preview_assets"
TOOL = "tools/hmi/preview.py"
DEFAULT_CHECKS = {"recon": ["coverage", "navigation"], "asm": ["coverage", "navigation", "search", "dock", "float"]}
ALL_CHECKS = ("coverage", "navigation", "search", "dock", "float")
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
STATES = [{"value": True, "colour": "on"}, {"value": False, "colour": "off"}]


# ---- the data of a preview ------------------------------------------------------------------------------------
def tag_info(tables: dict) -> dict:
    return {name: {"type": v.get("type"), "lo": v.get("eng_lo"), "hi": v.get("eng_hi"), "units": v.get("units") or ""}
            for name, v in asm_model.variable_rows(tables).items()}


def tokens_in(text, info: dict) -> list[str]:
    found = [t for t in TOKEN.findall(str(text or "")) if t in info]
    return found or ([TOKEN.findall(str(text))[0]] if TOKEN.findall(str(text or "")) else [])


def faceplate_ids(model: dict, faceplates: dict) -> dict[str, str]:
    """Device tag to the id of its faceplate: the faceplates document's id, else the device's tag."""
    out = {t: t for t, d in model["devices"].items() if d["faceplate"] != "empty"}
    for f in (faceplates or {}).get("faceplates", []):
        if f.get("device_tag") in model["devices"]:
            out[f["device_tag"]] = f["id"]
    return out


def build_faceplates(model: dict, faceplates: dict, tables: dict, info: dict) -> list[dict]:
    fp_of = faceplate_ids(model, faceplates)
    by_tab: dict[tuple[str, str], list[dict]] = {}
    for r in model["mapping"]:
        p = (r["place"] or "").split()
        if len(p) >= 4 and p[0] == "faceplate" and p[2] == "tab":
            by_tab.setdefault((p[1], " ".join(p[3:]).split(":")[0].strip()), []).append(
                {"uid": r["uid"], "label": r["label"], "section": r["section"],
                 "reads": [], "format": None})
    out, seen = [], set()
    for f in (faceplates or {}).get("faceplates", []):
        dev = model["devices"].get(f.get("device_tag") or "", {})
        tabs = [{"name": t["name"], "rows": by_tab.get((f["id"], t["name"]), [])} for t in f.get("tabs") or []]
        out.append({"id": f["id"], "title": f"{f.get('device_tag') or f['id']}  {dev.get('label', '')}".strip(),
                    "kind": f.get("kind"), "node": dev.get("node"), "tabs": tabs or [{"name": "Home", "rows": []}]})
        seen.add(f.get("device_tag"))
    for tag, d in model["devices"].items():
        if tag in seen or d["faceplate"] == "empty":
            continue
        rows = [{"uid": f"{tag}:{v['tag']}", "label": v.get("comment") or v["tag"], "section": "variables",
                 "reads": [v["tag"]], "format": None}
                for v in ((tables or {}).get("devices", {}).get(tag) or {}).get("variables", [])]
        out.append({"id": fp_of[tag], "title": f"{tag}  {d['label']}", "kind": d["faceplate"], "node": d["node"],
                    "tabs": [{"name": "Home", "rows": rows}]})
    return out


def nav_rows(model: dict) -> list[dict]:
    return [{"i": i, "from": n["from"], "target": n["target"], "resolution": n["resolution"], "uid": n.get("uid"),
             "route": n.get("route"), "faceplate": n.get("faceplate"), "tab": n.get("tab"), "reason": n.get("reason")}
            for i, n in enumerate(model["nav"])]


def row_index(nav: list[dict]) -> dict[str, int]:
    return {n["uid"]: n["i"] for n in nav if n.get("uid")}


def marker(uid: str, treatment: str) -> dict:
    return {"uid": uid, "kind": "hidden", "treatment": treatment}


def accounted_markers(model: dict, page: str, drawn: set[str]) -> list[dict]:
    """Rows a page does not draw because the model accounts for them: dropped objects, the frame, a link to a page
    that is not migrated."""
    nav_state = {n.get("uid"): n["resolution"] for n in model["nav"] if n.get("uid")}
    out = []
    for r in model["mapping"]:
        if r["source"] != page or r["uid"] in drawn:
            continue
        place = r["place"] or ""
        if place.startswith("dropped"):
            out.append(marker(r["uid"], "dropped"))
        elif place.startswith("frame"):
            out.append(marker(r["uid"], "frame"))
        elif r["section"] == "navigation" and nav_state.get(r["uid"]) == "not_migrated":
            out.append(marker(r["uid"], "not_migrated"))
    return out


def popup_markers(model: dict) -> list[dict]:
    """The dropped and frame rows of the pop-up sets: no faceplate tab draws them, so they are marked as a page marks
    its own (the treatment, not a drawing)."""
    pages = {p["id"] for p in model["pages"]}
    out = []
    for r in model["mapping"]:
        place = r["place"] or ""
        if r["source"] not in pages and (place.startswith("dropped") or place.startswith("frame")):
            out.append(marker(r["uid"], "dropped" if place.startswith("dropped") else "frame"))
    return out


def device_fp(model: dict, tag: str | None, fps: dict[str, str]) -> str | None:
    return fps.get(tag) if tag else None


STATUS_ROW = 20     # the least pitch of the rows of a status list, in px


def search_index(model: dict, fps: dict[str, str]) -> list[dict]:
    out = [{"kind": "page", "text": p["title"], "sub": p["id"], "page": p["id"]} for p in model["pages"]]
    for tag, d in model["devices"].items():
        tab = (d["openers"] or [{}])[0].get("tab")
        out.append({"kind": "device", "text": tag, "sub": d["label"], "page": d["page"], "faceplate": fps.get(tag),
                    "tab": tab})
    for t in model["tags"]:
        out.append({"kind": "tag", "text": t["name"], "sub": t["comment"], "page": t["page"],
                    "faceplate": fps.get(t["device"]) if t.get("device") else None, "tab": t.get("tab")})
    return out


def prepare_asm(model: dict, designs: dict[str, dict], faceplates: dict, tables: dict, window: tuple[int, int]) -> dict:
    info = tag_info(tables)
    fps = faceplate_ids(model, faceplates)
    nav = nav_rows(model)
    by_uid = row_index(nav)
    mapping = {r["uid"]: r for r in model["mapping"]}
    pages = []
    for p in model["pages"]:
        d = designs.get(p["id"])
        items: list[dict] = []
        if d is not None:
            nav_design = {n["uid"]: n for n in d.get("navigation", [])}
            for r in d.get("regions", []):
                if r.get("source_region"):
                    b = r["bbox"]
                    items.append({"uid": f"{p['id']}:{r['source_region']}", "kind": "region", "label": r.get("kind", ""),
                                  "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"]})
            for it in d["items"]:
                b = it["bbox"]
                row = mapping.get(it["uid"], {})
                tag = row.get("device")
                dev = model["devices"].get(tag) if tag else None
                base = {"uid": it["uid"], "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"],
                        "reads": it.get("reads") or [], "label": it.get("label") or row.get("label") or "",
                        "unit": (info.get((it.get("reads") or [None])[0]) or {}).get("units") or None, "format": None}
                kind = it["kind"]
                if kind == "symbol":
                    base.update({"kind": "symbol", "component": it["component"], "label": tag or base["label"]})
                    fid = device_fp(model, tag, fps) or fps.get(it.get("faceplate") or "")
                    if fid:
                        base["faceplate"] = fid
                        base["plain"] = bool(dev and dev["page"] != p["id"])
                        base["tab"] = next((o["tab"] for o in (dev or {}).get("openers", [])
                                            if o.get("uid") == it["uid"] and o.get("tab")), None)
                elif kind in ("readout", "indicator"):
                    base["kind"] = kind
                    if kind == "indicator":
                        base["states"] = it.get("states") or STATES
                        base["state_default"] = it.get("state_default")
                elif kind == "label":
                    base.update({"kind": "label", "text": it.get("text") or base["label"], "style": it.get("style")})
                elif kind in ("link", "button"):
                    nd = nav_design.get(it["uid"], {})
                    base.update({"kind": kind, "nav": by_uid.get(it["uid"])})
                    if nd.get("faceplate"):
                        base["faceplate"] = fps.get(nd["faceplate"]) or nd["faceplate"]
                elif kind == "pipe":
                    flow = next((f for f in model.get("flows", {}).values() if f.get("an") == it.get("original_an")), {})
                    k = d["canvas"].get("scale") or 1.0
                    base.update({"kind": "pipe", "path": [[pt["x"] * k, pt["y"] * k] for pt in flow.get("path", [])],
                                 "medium": flow.get("medium")})
                else:
                    base.update({"kind": "symbol", "component": kind})
                items.append(base)
            items += accounted_markers(model, p["id"], {i["uid"] for i in items})
        width, height = (d["canvas"]["w"], d["canvas"]["h"]) if d else (1580, 600)
        pages.append({"id": p["id"], "title": p["title"], "node": p["node"], "level": f"Level {p['level']}",
                      "route": p["route"], "kind": p["kind"], "built": p["built"], "width": width, "height": height,
                      "items": items})
    return {"mode": "asm", "nodes": model["nodes"], "pages": pages, "nav": nav,
            "faceplates": build_faceplates(model, faceplates, tables, info), "search": search_index(model, fps),
            "taginfo": info, "pictures": {}, "home": model.get("home"), "markers": popup_markers(model),
            "expected": sorted(r["uid"] for r in model["mapping"])}


def inventory_objects(inventory: Path, unit: str) -> tuple[dict, list[int] | None, Path | None]:
    """The objects of a unit's first window by `an`, its page size and its runtime picture."""
    files = asm_model.unit_files(inventory, unit)
    if not files.get("inventory") or not files["inventory"].is_file():
        return {}, None, files.get("runtime_picture")
    doc = load(files["inventory"], "inventory")
    manifest = load(inventory / "manifest.json", "inventory manifest")
    row = next(u for u in manifest["units"] if u["id"] == unit)
    info = load(inventory / row["folder"] / "unit.json", "inventory unit")
    size = (info.get("windows") or [{}])[0].get("page_size")
    if isinstance(size, dict):      # ctig's inventory states it as {"w", "h"}; a pair [w, h] is read as well
        size = [size["w"], size["h"]] if "w" in size and "h" in size else None
    return {str(o["an"]): o for o in doc.get("objects", [])}, size, files.get("runtime_picture")


def prepare_recon(units: list[dict], faceplates: dict, tables: dict, inventory: Path) -> tuple[dict, dict]:
    info = tag_info(tables)
    model, slices = asm_model.build(units, faceplates, tables, {"openers": [], "unresolved": []}, [], {},
                                    None, "contract", "", {}, {"kinds": [], "device_kinds": [], "module_parts": []},
                                    "Pages")
    nav = nav_rows(model)
    by_uid = row_index(nav)
    fps = faceplate_ids(model, faceplates)
    pages, pictures = [], {}
    for u in units:
        unit = u["unit"]["id"]
        if u["unit"]["kind"] != "page":
            continue
        objects, size, runtime = inventory_objects(inventory, unit)
        items: list[dict] = []
        for r in u.get("regions", []):
            b = r["bbox"]
            items.append({"uid": f"{unit}:{r['id']}", "kind": "region", "label": r.get("title", ""),
                          "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"]})
        for e in u.get("devices", []):
            b = e["bbox"]
            tag = e.get("tag") or e["id"]
            dev = model["devices"].get(tag)
            vars_ = ((tables or {}).get("devices", {}).get(tag) or {}).get("variables", [])
            it = {"uid": f"{unit}:{e['id']}", "kind": "symbol", "component": e.get("type"), "label": tag,
                  "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"], "reads": [v["tag"] for v in vars_[:1]]}
            if dev and dev["faceplate"] != "empty":
                it.update({"faceplate": fps[tag], "plain": dev["page"] != unit})
            items.append(it)
        for e in u.get("flows", []):
            items.append({"uid": f"{unit}:{e['id']}", "kind": "pipe", "path": [[pt["x"], pt["y"]] for pt in e.get("path") or []],
                          "medium": e.get("medium"),
                          "x": 0, "y": 0, "w": 0, "h": 0})
        for e in u.get("readouts", []):
            b = e["bbox"]
            items.append({"uid": f"{unit}:{e['id']}", "kind": "readout", "label": e.get("label"), "unit": e.get("units"),
                          "format": e.get("format"), "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"],
                          "reads": tokens_in(e.get("expr"), info)})
        rows_of: dict[tuple, int] = {}      # indicators that share one box are a status list: one row each (COB-180)
        for e in u.get("indicators", []):
            b = e["bbox"]
            key = (b["x"], b["y"], b["w"], b["h"])
            n = rows_of[key] = rows_of.get(key, -1) + 1
            b = {**b, "y": b["y"] + n * max(b["h"], STATUS_ROW)}
            items.append({"uid": f"{unit}:{e['id']}", "kind": "indicator", "label": e.get("label"),
                          "states": [{"value": True, "colour": "on", "label": e.get("on") or ""},
                                     {"value": False, "colour": "off", "label": e.get("off") or ""}],
                          "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"], "reads": tokens_in(e.get("expr"), info)})
        for e in u.get("navigation", []):
            b = e["bbox"]
            uid = f"{unit}:{e['id']}"
            it = {"uid": uid, "kind": "link" if e.get("kind") == "page" else "button", "label": e.get("label"),
                  "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"], "nav": by_uid.get(uid),
                  "hotspot": True}     # the original's navigation object is a touch area, not a drawn button (COB-180)
            items.append(it)
        for e in u.get("static", []):
            n = asm_model.ans_number(e)
            o = objects.get(n) or {}
            items.append({"uid": f"{unit}:s{n}", "kind": "label", "text": o.get("text") or e.get("what") or "",
                          "style": "heading" if e.get("class") == "heading" else None,
                          "x": o.get("x", 0), "y": o.get("y", 0), "w": o.get("w", 100), "h": o.get("h", 20)})
        for e in u.get("dropped", []):
            items.append(marker(f"{unit}:x{asm_model.ans_number(e)}", f"dropped:{e.get('reason_class') or ''}"))
        page = next(p for p in model["pages"] if p["id"] == unit)
        w, h = (size or [max([i["x"] + i["w"] for i in items if "x" in i] + [1024]),
                         max([i["y"] + i["h"] for i in items if "y" in i] + [768])])
        pages.append({"id": unit, "title": unit, "node": page["node"], "level": "", "route": page["route"],
                      "kind": "mimic", "built": True, "width": w, "height": h, "items": items})
        if runtime and runtime.is_file():
            pictures[unit] = runtime
    data = {"mode": "recon", "nodes": model["nodes"], "pages": pages, "nav": nav,
            "faceplates": build_faceplates(model, faceplates, tables, info), "search": [], "taginfo": info,
            "pictures": {}, "home": pages[0]["id"] if pages else None, "markers": popup_markers(model),
            "expected": sorted(r["uid"] for r in model["mapping"])}
    return data, {k: v for k, v in pictures.items()}


# ---- the files ------------------------------------------------------------------------------------------------
SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{csp}<title>{title}</title>
{style}
</head>
<body>
<div id="app">
<header id="top"><h1 id="title"></h1><span id="crumb"></span><input id="search" type="search" placeholder="Search pages, devices, tags" aria-label="Search"><ul id="results" hidden></ul><button id="b-nav" type="button">Navigation table</button><button id="b-orig" type="button">Original</button></header>
<nav id="tree" aria-label="Plant hierarchy"></nav>
<main id="stage"><div id="canvas-wrap"></div><div id="support" class="support" hidden></div></main>
<aside id="dock" aria-label="Faceplate"></aside>
</div>
<div id="float" hidden></div>
<section id="navtable" hidden></section>
<div id="notice" hidden></div>
<div id="fpstore"></div>
{data}
{script}
</body>
</html>
"""


def data_block(data: dict) -> str:
    """The run's data as an inert `application/json` block: `<`, `>` and `&` escaped, every value text."""
    text = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    text = text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f'<script type="application/json" id="preview-data">{text}</script>'


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_csp(text: str) -> str:
    return "sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode()


def bundle_html(data: dict, title: str) -> tuple[str, list[str]]:
    script = (ASSETS / "renderer.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    style = (ASSETS / "style.css").read_text(encoding="utf-8").replace("\r\n", "\n")
    csp = ("<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; img-src data:; "
           f"style-src 'unsafe-inline'; script-src '{sha256_csp(script)}'\">\n")
    page = SHELL.format(csp=csp, title=html.escape(title), style=f"<style>\n{style}</style>",
                        data=data_block(data), script=f"<script>{script}</script>")
    return page, [sha256_text(script)]


def site_files(out: Path, data: dict, title: str, pictures: dict[str, Path]) -> None:
    site = out / "site"
    site.mkdir(parents=True, exist_ok=True)
    for name in ("renderer.js", "style.css"):
        (site / name).write_bytes((ASSETS / name).read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8"))
    d = json.loads(json.dumps(data))
    for page, src in pictures.items():
        (site / "pictures").mkdir(exist_ok=True)
        shutil.copyfile(src, site / "pictures" / f"{page}.png")
        d["pictures"][page] = f"pictures/{page}.png"
    page = SHELL.format(csp="", title=html.escape(title), style='<link rel="stylesheet" href="style.css">',
                        data=data_block(d), script='<script src="renderer.js"></script>')
    (site / "index.html").write_bytes(page.encode("utf-8"))


def data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


# ---- the bundle scan ------------------------------------------------------------------------------------------
EXTERNAL = [re.compile(r"""\b(?:src|href|action|poster|data|srcset|formaction|xlink:href)\s*=\s*["']?\s*(?:https?:|//|ftp:|file:|wss?:)""", re.I),
            re.compile(r"""url\(\s*["']?\s*(?:https?:|//|ftp:|file:)""", re.I),
            re.compile(r"""@import""", re.I),
            re.compile(r"<(?:link|iframe|object|embed|base)\b", re.I)]
HANDLER = re.compile(r"""<[a-z][^>]*\son[a-z]+\s*=""", re.I)
JSURL = re.compile(r"""(?:href|src|action)\s*=\s*["']?\s*javascript:""", re.I)
SCRIPT = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.I | re.S)


def scan_bundle(text: str) -> dict:
    """Counts of what an inert bundle must not hold, and the inline scripts that execute (not the JSON blocks)."""
    external = sum(len(p.findall(text)) for p in EXTERNAL)
    handlers = len(HANDLER.findall(text)) + len(JSURL.findall(text))
    scripts, with_src = [], 0
    for attrs, body_ in SCRIPT.findall(text):
        if re.search(r"""\bsrc\s*=""", attrs, re.I):
            with_src += 1
        elif not re.search(r"""type\s*=\s*["']application/json["']""", attrs, re.I):
            scripts.append(body_)
    return {"external_refs": external + with_src, "inline_handlers": handlers,
            "scripts": scripts, "script_hashes": [sha256_text(s) for s in scripts]}


# ---- the checks -----------------------------------------------------------------------------------------------
def result(name, ok, expected, found, detail=None):
    return {"name": name, "ok": bool(ok), "expected": expected, "found": found, "detail": detail or []}


def check_coverage(page, data):
    got = set(page.evaluate("[...document.querySelectorAll('[data-uid]')].map(e => e.dataset.uid)"))
    expected = set(data["expected"])
    missing = sorted(expected - got)
    detail = [f"not drawn: {u}" for u in missing[:30]]
    if len(missing) > 30:
        detail.append(f"{len(missing)} not drawn in all")
    return result("coverage", not missing, len(expected), len(expected & got), detail)


def reset_view(page):
    if page.evaluate("document.body.dataset.fp"):
        page.click("#dock.open .fp:not([hidden]) [data-act=close], #float:not([hidden]) [data-act=close]")
    if page.evaluate("!document.getElementById('navtable').hidden"):
        page.click("#b-nav")


def check_navigation(page, data):
    rows, bad = data["nav"], []
    ok = 0
    for r in rows:
        try:
            reset_view(page)
            pid = (r.get("uid") or "").split(":")[0]
            ctl = None
            if r.get("uid") and any(p["id"] == pid for p in data["pages"]):
                page.click(f"#tree button[data-page='{pid}']")
                ctl = page.query_selector(f"[data-uid='{r['uid']}'] button")
            if ctl is not None:
                if page.evaluate("(c) => !!c.closest('.hot')", ctl):
                    ctl.dispatch_event("click")     # a hotspot lies under what it covers: the walk presses it directly
                else:
                    ctl.click()
            else:
                page.click("#b-nav")
                page.click(f"#navtable button[data-row='{r['i']}']")
            st = page.evaluate("({page: document.body.dataset.page, route: document.body.dataset.route, "
                               "fp: document.body.dataset.fp, tab: document.body.dataset.tab, "
                               "notice: document.body.dataset.notice})")
            res = r["resolution"]
            good = ((res == "page" and st["page"] == r["target"]) or (res == "support" and st["route"] == r["route"])
                    or (res == "faceplate" and st["fp"] == r["faceplate"]) or (res == "not_migrated" and bool(st["notice"])))
            if good:
                ok += 1
            else:
                bad.append(f"row {r['i']} ({r['from']} > {r['target']}, {res}): ended at {json.dumps(st)}")
        except Exception as e:   # a control that cannot be clicked is a failed row, said and not hidden
            bad.append(f"row {r['i']} ({r['from']} > {r['target']}): {str(e).splitlines()[0][:160]}")
    reset_view(page)
    return result("navigation", not bad, len(rows), ok, bad[:30])


def check_search(page, data):
    if not data["search"]:
        return result("search", True, 0, 0, ["the recon preview has no search"])
    first = {k: next((s for s in data["search"] if s["kind"] == k), None) for k in ("page", "device", "tag")}
    bad, found = [], 0
    for kind, s in first.items():
        if s is None:
            bad.append(f"no {kind} to search for")
            continue
        try:
            reset_view(page)
            page.click("#search")
            page.fill("#search", "")
            page.keyboard.type(s["text"])
            li = page.query_selector(f"#results li[data-kind='{kind}']")
            if li is None:
                bad.append(f"{kind} {s['text']!r}: no result")
                continue
            li.click()
            st = page.evaluate("({page: document.body.dataset.page, fp: document.body.dataset.fp})")
            if (s.get("page") and st["page"] != s["page"] and not st["fp"]) or (s.get("faceplate") and st["fp"] != s["faceplate"]):
                bad.append(f"{kind} {s['text']!r}: opened {json.dumps(st)}")
            else:
                found += 1
        except Exception as e:
            bad.append(f"{kind}: {str(e).splitlines()[0][:160]}")
    reset_view(page)
    return result("search", not bad, 3, found, bad)


def open_by_symbol(page, data):
    """Clicks the first symbol that opens a faceplate; its page first. Returns the faceplate id or None."""
    for p in data["pages"]:
        for it in p["items"]:
            if it.get("faceplate") and it["kind"] == "symbol":
                page.click(f"#tree button[data-page='{p['id']}']")
                page.click(f"[data-uid='{it['uid']}']")
                return it["faceplate"]
    return None


def check_dock(page, data):
    reset_view(page)
    fid = open_by_symbol(page, data)
    if fid is None:
        return result("dock", False, 1, 0, ["no symbol opens a faceplate"])
    box = page.evaluate("(() => { const r = document.getElementById('dock').getBoundingClientRect();"
                        " return {x: r.x, w: r.width, vw: innerWidth, mode: document.body.dataset.fpmode,"
                        " fp: document.body.dataset.fp}; })()")
    bad = []
    if box["fp"] != fid or box["mode"] != "dock":
        bad.append(f"opened {box['fp']!r} in {box['mode']!r}, expected {fid!r} docked")
    if not (box["w"] > 300 and box["x"] >= 0 and box["x"] + box["w"] <= box["vw"] + 1):
        bad.append(f"the dock lies at x {box['x']} with width {box['w']} in a window {box['vw']} wide")
    page.click("#dock.open [data-act=close]")
    after = page.evaluate("document.getElementById('dock').getBoundingClientRect().width")
    if after > 1:
        bad.append(f"the dock is still {after}px wide after Close")
    return result("dock", not bad, 1, 0 if bad else 1, bad)


def check_float(page, data):
    reset_view(page)
    fid = open_by_symbol(page, data)
    if fid is None:
        return result("float", False, 1, 0, ["no symbol opens a faceplate"])
    bad = []
    page.click("#dock.open .fp:not([hidden]) [data-act=float]")
    rect = lambda: page.evaluate("(() => { const r = document.getElementById('float').getBoundingClientRect();"  # noqa: E731
                                 " return {x: r.x, y: r.y, w: r.width, h: r.height, vw: innerWidth, vh: innerHeight,"
                                 " hidden: document.getElementById('float').hidden,"
                                 " dock: document.getElementById('dock').getBoundingClientRect().width,"
                                 " mode: document.body.dataset.fpmode}; })()")
    r1 = rect()
    if r1["hidden"] or r1["mode"] != "float" or r1["dock"] > 1:
        bad.append(f"after Float: {json.dumps(r1)}")
    head = page.query_selector("#float .fp:not([hidden]) header")
    hb = head.bounding_box()
    page.mouse.move(hb["x"] + 8, hb["y"] + 8)
    page.mouse.down()
    page.mouse.move(hb["x"] + 68, hb["y"] + 48, steps=4)
    page.mouse.up()
    r2 = rect()
    if abs(r2["x"] - r1["x"]) < 20 or abs(r2["y"] - r1["y"]) < 10:
        bad.append(f"the dragged faceplate stayed at ({r1['x']}, {r1['y']})")
    if not (0 <= r2["x"] and r2["x"] + r2["w"] <= r2["vw"] + 1 and 0 <= r2["y"] and r2["y"] < r2["vh"]):
        bad.append(f"the floating faceplate lies outside the window: {json.dumps(r2)}")
    page.click("#float .fp:not([hidden]) [data-act=dock]")
    r3 = rect()
    if not r3["hidden"] or r3["dock"] < 300 or r3["mode"] != "dock":
        bad.append(f"after Dock: {json.dumps(r3)}")
    page.click("#dock.open .fp:not([hidden]) [data-act=close]")
    return result("float", not bad, 1, 0 if bad else 1, bad)


CHECKS = {"coverage": check_coverage, "navigation": check_navigation, "search": check_search, "dock": check_dock,
          "float": check_float}


def take_pictures(page, data, out: Path) -> list[dict]:
    pics = []
    folder = out / "pictures"
    folder.mkdir(parents=True, exist_ok=True)
    for p in data["pages"]:
        if not p["built"]:
            continue
        reset_view(page)
        page.click(f"#tree button[data-page='{p['id']}']")
        page.wait_for_timeout(100)
        name = f"{p['id']}.png"
        page.screenshot(path=str(folder / name))
        pics.append({"name": p["id"], "kind": "page", "file": f"pictures/{name}"})
    used = {p["name"] for p in pics}
    for f in data["faceplates"]:
        reset_view(page)
        page.evaluate("id => window.__preview.open(id)", f["id"])
        page.wait_for_timeout(100)
        name = f["id"] if f["id"] not in used else f"{f['id']}-faceplate"
        page.screenshot(path=str(folder / f"{name}.png"))
        pics.append({"name": name, "kind": "faceplate", "file": f"pictures/{name}.png"})
        reset_view(page)
    return pics


def run_browser(url: str, data: dict, checks: list[str], window: tuple[int, int], pictures: bool, out: Path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise InputFault("the checks and pictures need Playwright: run under ctig's .venv") from None
    results, pics = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": window[0], "height": window[1]}).new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)[:200]))
        page.goto(url + "#frozen")
        page.wait_for_selector("body[data-ready='1']", timeout=15000)
        for name in checks:
            results.append(CHECKS[name](page, data))
        if pictures:
            pics = take_pictures(page, data, out)
        if errors:
            results.append(result("script_errors", False, 0, len(errors), errors[:10]))
        browser.close()
    return results, pics


def parse_window(text: str) -> tuple[int, int]:
    try:
        w, h = (int(n) for n in text.lower().split("x"))
    except ValueError:
        raise InputFault(f"--window is WIDTHxHEIGHT, not {text!r}") from None
    return w, h


def main(argv: list[str] | None = None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mode", required=True, choices=("recon", "asm"))
    ap.add_argument("--understandings", default=None, metavar="LIST")
    ap.add_argument("--faceplates", default=None)
    ap.add_argument("--inventory", default=None, metavar="DIR")
    ap.add_argument("--tables", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--designs", default=None, metavar="LIST")
    ap.add_argument("--window", default="1920x1080")
    ap.add_argument("--checks", default=None, help="comma list of " + ", ".join(ALL_CHECKS) + "; default by mode")
    ap.add_argument("--bundle", action="store_true")
    ap.add_argument("--pictures", action="store_true")
    ap.add_argument("--title", default="Migration preview")
    ap.add_argument("--no-simulation", action="store_true")
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args_line = sys.argv[1:] if argv is None else list(argv)
    out = Path(a.out)
    try:
        window = parse_window(a.window)
        checks = [c for c in (a.checks.split(",") if a.checks is not None else DEFAULT_CHECKS[a.mode]) if c]
        unknown = [c for c in checks if c not in CHECKS]
        if unknown:
            raise InputFault(f"unknown check {unknown[0]!r}; the checks are {', '.join(ALL_CHECKS)}")
        need = {"recon": ("understandings", "faceplates", "inventory", "tables"),
                "asm": ("model", "designs", "faceplates", "tables")}[a.mode]
        for n in need:
            if not getattr(a, n):
                raise InputFault(f"--mode {a.mode} needs --{n}")
        faceplates, tables = load(a.faceplates, "faceplates"), load(a.tables, "tables")
        inputs = [Path(a.faceplates), Path(a.tables)]
        pictures: dict[str, Path] = {}
        if a.mode == "asm":
            model = load(a.model, "model")
            designs = {}
            for p in path_list(a.designs):
                d = load(p, "design")
                designs[d["page"]] = d
            data = prepare_asm(model, designs, faceplates, tables, window)
            inputs += [Path(a.model), Path(a.designs)]
        else:
            units = [asm_model.check_understanding(load(p, "understanding"), p) for p in path_list(a.understandings)]
            data, pictures = prepare_recon(units, faceplates, tables, Path(a.inventory))
            inputs += [Path(a.understandings), Path(a.inventory)]
        data.update({"title": a.title, "window": {"w": window[0], "h": window[1]},
                     "simulation": not a.no_simulation, "sim_ms": 1000})
    except InputFault as e:
        print(f"preview: {e}")
        return 1
    out.mkdir(parents=True, exist_ok=True)
    site_files(out, data, a.title, pictures)
    bundle = {"file": None, "bytes": 0, "external_refs": 0, "script_hashes": [], "inline_handlers": 0}
    bundle_ok = True
    target = out / "site" / "index.html"
    if a.bundle:
        bdata = json.loads(json.dumps(data))
        for page, src in pictures.items():
            bdata["pictures"][page] = data_uri(src)
        text, hashes = bundle_html(bdata, a.title)
        scan = scan_bundle(text)
        (out / "preview.html").write_bytes(text.encode("utf-8"))
        bundle = {"file": "preview.html", "bytes": len(text.encode("utf-8")), "external_refs": scan["external_refs"],
                  "script_hashes": scan["script_hashes"], "inline_handlers": scan["inline_handlers"]}
        bundle_ok = (scan["external_refs"] == 0 and scan["inline_handlers"] == 0 and scan["script_hashes"] == hashes)
        target = out / "preview.html"
    results, pics = [], []
    if checks or a.pictures:
        try:
            results, pics = run_browser(target.as_uri(), data, checks, window, a.pictures, out)
        except InputFault as e:
            print(f"preview: {e}")
            return 1
    doc = {"schema": "cadre-hmi-preview-checks/1", "mode": a.mode, "window": {"w": window[0], "h": window[1]},
           "checks": results, "pictures": pics, "bundle": bundle,
           "provenance": clock.provenance(TOOL, args_line, inputs)}
    provenance.write_json(out / "checks.json", doc)
    failed = [c["name"] for c in results if not c["ok"]]
    print(f"preview: mode {a.mode}, pages {len(data['pages'])}, faceplates {len(data['faceplates'])}, "
          f"checks {len(results) - len(failed)}/{len(results)} ok" + (f" (failed: {', '.join(failed)})" if failed else "")
          + (f", bundle {bundle['bytes']} bytes, external {bundle['external_refs']}, handlers {bundle['inline_handlers']}"
             if a.bundle else "") + f", pictures {len(pics)}")
    return 0 if not failed and bundle_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
