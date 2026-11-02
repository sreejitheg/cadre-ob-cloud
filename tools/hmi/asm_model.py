"""The ASM model of a migrated plant: the hierarchy, pages, devices, alarms, the tag search index, trend sets, the
navigation of the original and the mapping of every understanding entry to its place in the ASM design.

Generalised from the eng02 slice's model builder (ARCH-WFB-01 revision B8 Table 109, WFBD-091): the slice hard coded
its pages, devices and mapping; here they come from the documents of the migration workflow:

    --understandings LIST   a list file (one path a line, or a JSON array) of `wfb.migration.understanding/1` documents
    --faceplates F          `wfb.migration.faceplates/1`: which pop-up rows form which faceplate tab
    --tables F              `ctig.tables/1`: the variables and alarms of each device
    --openers F             `ctig.popup-openers/1`: the commands that open a pop-up
    --inventory DIR         `ctig.inventory/1`: the geometry; copied into the page folders
    --menu F                the runtime menu (`ctig.capture.runtime/1` `menu[]`, or the document holding it)
    --contract F            the areas of the contract (hierarchy `contract`): {"site", "areas": [{"name", "pages",
                            "children"}], "pages": [{"id", "prev", "next"}]}
    --device-model F        ctig's device model (`cadre-hmi-devices/1`): the kind of a device it names wins
    --pictures DIR          the one-to-one preview's `<page>.png`
    --support-routes F      {original support target (a name or a part of one): library route}; default Alarm to
                            /alerts and Trend to /trends, the routes of the library's own pages
    --tag-root R --hierarchy menu|contract --out O

writes `O/model.json` (`cadre-hmi-asm-model/1`) and `O/pages/<page>/` (`page.json`, `understanding.json`,
`inventory.json`, `runtime.png`, `preview.png`).

Exit codes: 0; 2 the run finished with findings (an entry that cannot be mapped, a target that cannot be resolved);
1 an input fault. Nothing here contacts a gateway.

Run:  python tools/hmi/asm_model.py --understandings L --faceplates F --tables T --openers O --inventory D --out O
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import provenance  # noqa: E402
else:
    from . import provenance

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "cadre-hmi-asm-model/1"
TOOL = "tools/hmi/asm_model.py"

#: The sections whose entries carry an `id`; `static` and `dropped` carry `ans` only.
ID_SECTIONS = ("regions", "devices", "flows", "readouts", "indicators", "navigation")
#: The sections whose entries the design places on a page (`page.json` `items`).
PLACEABLE = ("devices", "flows", "readouts", "indicators", "navigation")
#: A static object of these classes is drawn; a frame is replaced by the ASM frame.
STATIC_DRAWN = ("label", "heading", "legend", "artwork")
#: A device type of the closed list (B8 Table 105) to the symbol kind of the library; None where it has none.
TYPE_KIND = {"pump": "pump", "motor": "motor", "generator": "generator", "breaker": "switch", "isolator": "switch",
             "ats": "switch", "fuse": None, "vsd": "motor", "dol-starter": "motor", "valve": "valve",
             "actuator": "valve", "wet-well": "tank", "tank": "tank", "level-switch": "indicator",
             "level-instrument": "instrument-field", "temperature-instrument": "instrument-field",
             "flow-instrument": "instrument-field", "pressure-instrument": "instrument-field",
             "power-meter": "readout", "ups": None, "plc": None, "duty-selector": None, "sequence": "sequence",
             "lamp": "indicator", "other": None}
#: The faceplate a library device kind opens, by the kind's name (`library/profile.json` `deviceKinds`).
FACEPLATE_OF_KIND = {"instrument-field": "instrument", "readout": "instrument"}
#: The routes of the library's own support pages, by a word in the original target's name.
LIBRARY_ROUTES = {"alarm": "/alerts", "trend": "/trends"}
#: Priorities by the rank of a category when the tables give no category table (the slice's reading, inferred).
RANKED = ["high", "medium", "low", "diagnostic"]
MAX_PENS = 3


class InputFault(Exception):
    """An input that cannot be read or is not what the command needs: exit 1."""


# ---- reading --------------------------------------------------------------------------------------------------
def load(path, what: str):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise InputFault(f"{what}: {path}: {e}") from None


def path_list(path) -> list[Path]:
    text = Path(path).read_text(encoding="utf-8").strip()
    try:
        items = json.loads(text) if text.startswith("[") else [ln.strip() for ln in text.splitlines() if ln.strip()]
    except ValueError as e:
        raise InputFault(f"understandings: {path}: {e}") from None
    return [Path(i) for i in items]


def check_understanding(doc, path) -> dict:
    unit = doc.get("unit") if isinstance(doc, dict) else None
    if not isinstance(unit, dict) or not unit.get("id") or unit.get("kind") not in ("page", "popup_set"):
        raise InputFault(f"understanding: {path}: no unit with an id and a kind of page or popup_set")
    for sec in ID_SECTIONS + ("static", "dropped"):
        if not isinstance(doc.get(sec, []), list):
            raise InputFault(f"understanding: {path}: {sec} is not a list")
    return doc


def menu_rows(doc) -> list[dict]:
    rows = doc if isinstance(doc, list) else (doc.get("menu") or doc.get("menus") or [])
    return [r for r in rows if isinstance(r, dict) and r.get("target")]


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "page"


def seconds(text) -> int:
    m = re.match(r"(\d+):(\d+):(\d+)", str(text or ""))
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) if m else 0


def ans_number(entry: dict) -> str:
    """The object number of an `ans` entry written `<target>:<an>` (the first)."""
    ans = entry.get("ans") or [""]
    return str(ans[0]).rsplit(":", 1)[-1]


def entry_uid(unit: str, section: str, entry: dict) -> str | None:
    if section in ID_SECTIONS:
        return f"{unit}:{entry['id']}" if entry.get("id") else None
    n = ans_number(entry)
    return f"{unit}:{'s' if section == 'static' else 'x'}{n}" if n else None


def entry_label(section: str, e: dict) -> str:
    return str(e.get("label") or e.get("title") or e.get("what") or e.get("reason") or e.get("medium") or "")


# ---- the hierarchy --------------------------------------------------------------------------------------------
def hierarchy_from_menu(rows: list[dict], site: str) -> list[dict]:
    """Nodes in the menu's order: the site, then one node for each menu group that holds a target."""
    groups: dict[str, list[str]] = {}
    for r in rows:
        groups.setdefault(r.get("menu") or "Menu", [])
        if r["target"] not in groups[r.get("menu") or "Menu"]:
            groups[r.get("menu") or "Menu"].append(r["target"])
    nodes = [{"name": site, "parent": None, "level": 1, "targets": []}]
    for name, targets in groups.items():
        nodes.append({"name": name, "parent": 0, "level": 2, "targets": targets})
    return nodes


def hierarchy_from_contract(contract: dict) -> list[dict]:
    nodes = [{"name": contract.get("site") or "Site", "parent": None, "level": 1, "targets": []}]

    def walk(areas, parent, level):
        for a in areas:
            nodes.append({"name": a["name"], "parent": parent, "level": level, "targets": list(a.get("pages") or [])})
            walk(a.get("children") or [], len(nodes) - 1, level + 1)
    walk(contract.get("areas") or [], 0, 2)
    return nodes


def is_support(target: str, support: dict) -> str | None:
    """The library route of an original support target, by exact name or by a word of it."""
    if target in support:
        return support[target]
    low = target.lower()
    return next((route for word, route in support.items() if word.lower() in low), None)


# ---- the build ------------------------------------------------------------------------------------------------
def build(units: list[dict], faceplates: dict, tables: dict, openers: dict, menu: list[dict], contract: dict | None,
          device_model: dict | None, hierarchy: str, tag_root: str, support: dict, catalogue: dict,
          site: str = "Site") -> tuple[dict, dict]:
    """`(model, slices)`: the model document without its provenance, and for each built page the slice that goes
    to `pages/<page>/page.json`."""
    by_unit = {u["unit"]["id"]: u for u in units}
    page_units = [u for u in units if u["unit"]["kind"] == "page"]
    popup_units = [u for u in units if u["unit"]["kind"] == "popup_set"]
    model_kinds = {d["id"]: d.get("kind") for d in (device_model or {}).get("devices", [])}
    fplates = list((faceplates or {}).get("faceplates") or [])

    # nodes and pages
    spec = hierarchy_from_menu(menu, site) if hierarchy == "menu" else hierarchy_from_contract(contract or {})
    placed: dict[str, int] = {}
    for i, n in enumerate(spec):
        for t in n["targets"]:
            placed.setdefault(t, i)
    for u in page_units:   # a built page no node lists belongs to the root
        placed.setdefault(u["unit"]["id"], 0)
        if u["unit"]["id"] not in spec[0]["targets"] and placed[u["unit"]["id"]] == 0:
            spec[0]["targets"].append(u["unit"]["id"])
    menu_label = {}
    for r in menu:
        menu_label.setdefault(r["target"], r.get("item") or r["target"])
    pages_table = {p["id"]: p for p in (contract or {}).get("pages", []) if isinstance(p, dict) and p.get("id")}
    nodes, pages = [], []
    node_of_page: dict[str, str] = {}
    for i, n in enumerate(spec):
        targets = [t for t in n["targets"]
                   if t in by_unit and by_unit[t]["unit"]["kind"] == "page" or (t not in by_unit and not is_support(t, support))]
        if i and not targets:   # a node with no page of the migration (the support menu) is not a node
            n["skip"] = True
            continue
        nid = f"n{len(nodes)}"
        n["id"] = nid
        parent = spec[n["parent"]].get("id") if n["parent"] is not None else None
        nodes.append({"id": nid, "parent": parent, "name": n["name"], "level": n["level"], "pages": targets})
        for t in targets:
            built = t in by_unit
            node_of_page[t] = nid
            pages.append({"id": t, "title": menu_label.get(t) or t, "node": nid, "route": "/" + slug(t),
                          "kind": "mimic" if built else "stub", "built": built,
                          "folder": f"pages/{t}" if built else None,
                          "level": n["level"]})
    routes = {p["id"]: p["route"] for p in pages}
    seen_routes: set[str] = set()
    for p in pages:   # two ids that slug alike keep distinct routes
        base = p["route"]
        k = 2
        while p["route"] in seen_routes:
            p["route"] = f"{base}-{k}"
            k += 1
        seen_routes.add(p["route"])
        routes[p["id"]] = p["route"]
    page_ids = {p["id"] for p in pages}

    # faceplate tabs of the pop-up sets; the openers of each faceplate
    popup_tab: dict[str, tuple[str, str]] = {}
    for f in fplates:
        for tab in f.get("tabs") or []:
            for pop in tab.get("source_popups") or []:
                popup_tab.setdefault(pop, (f["id"], tab["name"]))
    popup_names = set(popup_tab) | {o.get("popup") for o in (openers or {}).get("openers", []) if o.get("popup")} \
        | {u["unit"]["id"] for u in popup_units} | {w for u in popup_units for w in u["unit"].get("windows", [])}
    opener_popup = {(o.get("page"), str(o.get("an"))): o.get("popup") for o in (openers or {}).get("openers", [])}

    # devices: the home page is the faceplate's owner page, else the first page that draws the device
    devices: dict[str, dict] = {}
    for u in page_units:
        unit = u["unit"]["id"]
        for e in u.get("devices", []):
            key = e.get("tag") or e.get("id")
            if not key or not e.get("id"):
                continue
            d = devices.setdefault(key, {"tag": key, "label": e.get("label") or key, "type": e.get("type"),
                                         "drawn_on": []})
            if unit not in d["drawn_on"]:
                d["drawn_on"].append(unit)
            d.setdefault("first", (unit, f"{unit}:{e['id']}"))
    for key, d in devices.items():
        owner = next((f.get("owner_page") for f in fplates if f.get("device_tag") == key and f.get("owner_page")), None)
        home = owner if owner in d["drawn_on"] else d["first"][0]
        entry = next(e for e in by_unit[home].get("devices", []) if (e.get("tag") or e.get("id")) == key)
        fp = next((f for f in fplates if f.get("device_tag") == key), None)
        kind = model_kinds.get(key) or TYPE_KIND.get(d["type"]) or d["type"]
        deviceKinds = catalogue.get("device_kinds", [])
        fp_kind = (fp or {}).get("kind") or (FACEPLATE_OF_KIND.get(kind, kind) if kind in deviceKinds
                                              or kind in FACEPLATE_OF_KIND else "empty")
        openers_out = []
        for o in (fp or {}).get("openers", []):
            pop = opener_popup.get((o.get("page"), str(o.get("an"))))
            tab = popup_tab.get(pop, (None, None))[1] or ((fp or {}).get("tabs") or [{}])[0].get("name")
            src = by_unit.get(o.get("page"))
            nav_e = next((n for n in (src or {}).get("navigation", []) if f"{o.get('page')}:{o.get('an')}" in
                          (n.get("ans") or [])), None)
            openers_out.append({"page": o.get("page"), "an": str(o.get("an")), "tab": tab,
                                "uid": f"{o['page']}:{nav_e['id']}" if nav_e and nav_e.get("id") else None,
                                "command": o.get("command")})
        d.update({"label": entry.get("label") or key, "kind": kind, "node": node_of_page.get(home),
                  "page": home, "uid": f"{home}:{entry['id']}", "faceplate": fp_kind, "openers": openers_out})
        for k in ("first",):
            d.pop(k, None)

    # the flows of the pages: the original's routing, medium and ends, by the flow's uid (a design item of kind pipe
    # takes them from here by its `original_an`, so that the design states none of them)
    flows = {f"{u['unit']['id']}:{e['id']}": {"an": (e.get("ans") or [None])[0], "path": e.get("path") or [],
                                              "medium": e.get("medium"),
                                              "from": f"{u['unit']['id']}:{e['from']}" if e.get("from") else None,
                                              "to": f"{u['unit']['id']}:{e['to']}" if e.get("to") else None}
             for u in page_units for e in u.get("flows", []) if e.get("id")}

    # mapping of every entry
    mapping, unmapped, slices = [], [], {p["id"]: {"items": [], "devices": [], "nav": []} for p in pages if p["built"]}
    fp_of_unit: dict[str, tuple[str, str] | None] = {}
    for u in popup_units:
        uid = u["unit"]["id"]
        fp_of_unit[uid] = next((popup_tab[w] for w in [uid] + list(u["unit"].get("windows", [])) if w in popup_tab), None)
    for u in units:
        unit, kind = u["unit"]["id"], u["unit"]["kind"]
        for sec in ID_SECTIONS + ("static", "dropped"):
            for idx, e in enumerate(u.get(sec, [])):
                uid = entry_uid(unit, sec, e)
                if uid is None:
                    unmapped.append({"source": unit, "section": sec, "index": idx, "reason": "the entry has no id"
                                     if sec in ID_SECTIONS else "the entry names no object"})
                    continue
                row = {"source": unit, "id": uid.split(":", 1)[1], "uid": uid, "section": sec,
                       "label": entry_label(sec, e), "place": None, "device": None}
                if sec == "dropped":
                    row["place"] = f"dropped: {e.get('reason_class') or 'dropped'}: {e.get('reason') or ''}".rstrip(": ")
                elif sec == "static" and e.get("class") == "frame":
                    row["place"] = "frame: replaced by the ASM frame"
                elif kind == "page":
                    page = unit
                    row["place"] = f"page {page}"
                    if sec == "devices":
                        key = e.get("tag") or e.get("id")
                        row["device"] = key
                        d = devices.get(key)
                        if d and d["page"] != page:
                            row["place"] = f"page {page}: plain symbol opening faceplate {key}"
                        elif d:
                            row["place"] = f"page {page}: device symbol of {key} with its node"
                    elif sec == "navigation":
                        row["place"] = f"page {page}: " + ("faceplate opener" if e.get("kind") in ("popup", "faceplate")
                                                          else "link")
                else:
                    hit = fp_of_unit.get(unit)
                    if hit is None:
                        unmapped.append({"source": unit, "section": sec, "index": idx,
                                         "reason": "the pop-up set is in no tab of the faceplates document"})
                        continue
                    row["place"] = f"faceplate {hit[0]} tab {hit[1]}"
                mapping.append(row)
                if kind == "page" and sec in PLACEABLE + ("static",) and not (
                        sec == "static" and e.get("class") not in STATIC_DRAWN):
                    item = {k: v for k, v in e.items() if k not in ("basis",)}
                    item.update({"uid": uid, "section": sec, "label": row["label"],
                                 "kind": ("link" if e.get("kind") == "page" else "button") if sec == "navigation"
                                 else ITEM_KIND[sec],
                                 "original_an": (e.get("ans") or [None])[0]})
                    slices[unit]["items"].append(item)
    for key, d in devices.items():
        if d["page"] in slices:
            slices[d["page"]]["devices"].append({k: v for k, v in d.items() if k != "drawn_on"})

    # alarms
    priorities = ranked_priorities(tables)
    number_rank = ranked_numbers(tables)
    alarms = []
    for stem, t in (tables or {}).get("devices", {}).items():
        d = devices.get(stem)
        cat_map = (t.get("priority") or {}).get("by_category") or {}
        cat_inferred = bool((t.get("priority") or {}).get("inferred", True))
        for sec in ("digital_alarms", "advanced_alarms"):
            for a in t.get(sec, []):
                cat = str(a.get("category") or "")
                if cat in cat_map:
                    pri, inferred = named_priority(cat_map[cat], number_rank, cat_inferred)
                else:
                    pri, inferred = priorities.get(cat, "low"), True
                alarms.append({"tag": a["tag"], "desc": a.get("desc") or a.get("name") or a["tag"], "priority": pri,
                               "inferred": inferred, "delay": seconds(a.get("delay")), "device": stem if d else None,
                               "node": d["node"] if d else None, "uid": d["uid"] if d else None,
                               "category": cat or None,
                               "source": a.get("var_a") or a.get("expression") or None})

    # search index
    alarm_tags = {a["tag"]: a for a in alarms}
    index: dict[str, dict] = {}
    mentions: dict[str, str] = {}   # a variable's first drawn place, from the expressions of the entries
    rows = variable_rows(tables)
    var_names = set(rows)
    for u in page_units:
        unit = u["unit"]["id"]
        for sec in ("readouts", "indicators", "devices"):
            for e in u.get(sec, []):
                text = " ".join(str(e.get(k) or "") for k in ("expr", "tag"))
                for name in sorted(var_names):
                    if name in text and name not in mentions and e.get("id"):
                        mentions[name] = f"{unit}:{e['id']}"
    for stem, t in (tables or {}).get("devices", {}).items():
        d = devices.get(stem)
        for v in t.get("variables", []):
            uid = mentions.get(v["tag"])
            lo, hi = v.get("eng_lo"), v.get("eng_hi")
            index[v["tag"]] = {"name": v["tag"], "comment": v.get("comment") or "", "units": v.get("units") or "",
                               "range": [lo, hi] if hi not in (None, "") else None,
                               "device": stem if d else None,
                               "tab": ((d["openers"] or [{}])[0].get("tab") or "Home") if d and d["faceplate"] != "empty"
                               else None,
                               "page": uid.split(":")[0] if uid else (d["page"] if d else None), "uid": uid,
                               "alarm": v["tag"] in alarm_tags}
    for name, v in rows.items():      # a tag the pages read that no device lists: in the index with no device
        if name not in index:
            uid = mentions.get(name)
            lo, hi = v.get("eng_lo"), v.get("eng_hi")
            index[name] = {"name": name, "comment": v.get("comment") or "", "units": v.get("units") or "",
                           "range": [lo, hi] if hi not in (None, "") else None, "device": None, "tab": None,
                           "page": uid.split(":")[0] if uid else None, "uid": uid, "alarm": name in alarm_tags}
    for a in alarms:
        d = devices.get(a["device"]) if a["device"] else None
        index.setdefault(a["tag"], {"name": a["tag"], "comment": a["desc"], "units": "", "range": None,
                                    "device": a["device"], "tab": "Alarms" if d and d["faceplate"] != "empty" else None,
                                    "page": d["page"] if d else None, "uid": a["uid"], "alarm": True})
    tags = sorted(index.values(), key=lambda t: t["name"])

    # trends: up to three analogue variables of the devices of each node
    trends = []
    for n in nodes:
        pens = []
        for stem, d in devices.items():
            if d["node"] != n["id"]:
                continue
            for v in ((tables or {}).get("devices", {}).get(stem) or {}).get("variables", []):
                if v.get("units") and v.get("eng_hi") not in (None, "") and len(pens) < MAX_PENS:
                    pens.append({"label": v.get("comment") or v["tag"], "expr": v["tag"], "units": v["units"],
                                 "min": v.get("eng_lo") or 0, "max": v["eng_hi"]})
        if pens:
            trends.append({"node": n["id"], "pens": pens})

    # navigation
    fp_of_popup = {pop: {"faceplate": fid, "tab": tab} for pop, (fid, tab) in popup_tab.items()}
    nav: list[dict] = []

    def resolve(target: str) -> dict:
        if target in popup_names:
            hit = fp_of_popup.get(target)
            if hit:
                return {"resolution": "faceplate", **hit}
            return {"resolution": None, "reason": "the pop-up is in no tab of the faceplates document"}
        if target in page_ids:
            return {"resolution": "page", "route": routes[target]}
        route = is_support(target, support)
        if route:
            return {"resolution": "support", "route": route}
        return {"resolution": "not_migrated", "reason": "the target is outside the pages of the migration and the "
                                                        "library's support pages"}
    for r in menu:
        nav.append({"from": f"menu {r.get('menu') or 'Menu'} > {r.get('item') or r['target']}", "target": r["target"],
                    "priv": r.get("priv"), "uid": None, **resolve(r["target"])})
    for u in page_units:
        unit = u["unit"]["id"]
        for e in u.get("navigation", []):
            if not e.get("target"):
                continue
            nav.append({"from": f"{unit} {e.get('label') or e.get('id') or ''}".rstrip(), "target": e["target"],
                        "priv": e.get("priv"), "uid": f"{unit}:{e['id']}" if e.get("id") else None,
                        **resolve(e["target"])})
    for o in (openers or {}).get("openers", []):
        if o.get("popup"):
            nav.append({"from": f"opener {o.get('page')}:{o.get('an')}", "target": o["popup"],
                        "priv": o.get("privilege"), "uid": None, **resolve(o["popup"])})
    for pid, p in pages_table.items():
        for k in ("prev", "next"):
            if p.get(k):
                nav.append({"from": f"{pid} {'previous' if k == 'prev' else 'next'}", "target": p[k], "priv": None,
                            "uid": None, **resolve(p[k])})
    for p in pages:
        row = pages_table.get(p["id"], {})
        p["previous"] = routes.get(row.get("prev"))
        p["next"] = routes.get(row.get("next"))
    unresolved = [{"from": n["from"], "target": n["target"], "reason": n.get("reason") or "no resolution"}
                  for n in nav if n["resolution"] is None]

    model = {"schema": SCHEMA, "site": spec[0]["name"], "home": next((p["id"] for p in pages if p["built"]), None),
             "tag_root": tag_root, "nodes": nodes, "pages": pages, "devices": devices, "alarms": alarms, "tags": tags,
             "trends": trends, "nav": nav, "flows": flows, "mapping": mapping, "unmapped": unmapped, "unresolved": unresolved,
             "catalogue": {k: catalogue[k] for k in ("kinds", "device_kinds", "module_parts")}}
    return model, slices


def variable_rows(tables: dict) -> dict[str, dict]:
    """The variable row of every tag the tables state, by the tag's name: `tables.tags` (ctig 95fa79c, the row of every
    tag the scoped pages read) and the variables listed under each device, which carry the same fields. A tag in both
    takes the device's row over the map's."""
    out = {name: {**row, "tag": name} for name, row in ((tables or {}).get("tags") or {}).items()}
    for t in (tables or {}).get("devices", {}).values():
        for v in t.get("variables", []):
            out[v["tag"]] = {**out.get(v["tag"], {}), **v}
    return out


def priority_number(value) -> int | None:
    """The number of a `by_category` value: ctig writes an object `{"basis", "inferred", "priority": n}`; a bare number
    or a numeric string is read as that number."""
    n = value.get("priority") if isinstance(value, dict) else value
    return int(n) if isinstance(n, (int, float)) and not isinstance(n, bool) else (int(n) if str(n).isdigit() else None)


def ranked_numbers(tables: dict) -> dict[int, str]:
    """Priority names by the rank of each priority number the category tables give, by the ranking that names
    categories when there is no table (lowest number most severe)."""
    nums = sorted({priority_number(v) for t in (tables or {}).get("devices", {}).values()
                   for v in ((t.get("priority") or {}).get("by_category") or {}).values()} - {None})
    return {n: RANKED[min(i, len(RANKED) - 1)] for i, n in enumerate(nums)}


def named_priority(value, ranks: dict[int, str], default_inferred: bool) -> tuple[str, bool]:
    """`(priority name, inferred)` of one `by_category` value: a name stands for itself, a number takes its rank."""
    inferred = value.get("inferred", default_inferred) if isinstance(value, dict) else default_inferred
    if isinstance(value, str) and not value.isdigit():
        return value.lower(), bool(inferred)
    n = priority_number(value)
    return (ranks.get(n, "low") if n is not None else "low"), bool(inferred)


def ranked_priorities(tables: dict) -> dict[str, str]:
    """Priority names by the rank of each category found in the tables, lowest number most severe. The tables'
    `priority.inferred` says whether a category table existed; without one this reading is an inference."""
    cats = set()
    for t in (tables or {}).get("devices", {}).values():
        for sec in ("digital_alarms", "advanced_alarms"):
            cats |= {str(a.get("category")) for a in t.get(sec, []) if a.get("category") not in (None, "")}
    ordered = sorted(cats, key=lambda c: (int(c) if c.isdigit() else 10 ** 9, c))
    return {c: RANKED[min(i, len(RANKED) - 1)] for i, c in enumerate(ordered)}


def catalogue_of() -> dict:
    """The library's kinds and the module's parts, read from the repository so that a library change is seen."""
    profile = load(ROOT / "library" / "profile.json", "profile")
    module = load(ROOT / "module" / "components.json", "module components")
    return {"kinds": sorted(profile["kinds"]), "device_kinds": sorted(profile["deviceKinds"]),
            "module_parts": sorted(module)}


# ---- writing --------------------------------------------------------------------------------------------------
def unit_files(inventory: Path, unit: str) -> dict:
    """The inventory file and the two pictures of a unit's first window, as ctig's `unit.json` names them."""
    manifest = load(inventory / "manifest.json", "inventory manifest")
    row = next((u for u in manifest.get("units", []) if u.get("id") == unit), None)
    if row is None:
        return {}
    folder = inventory / row["folder"]
    info = load(folder / "unit.json", f"inventory unit {unit}")
    win = (info.get("windows") or [{}])[0]
    return {k: folder / win[k] for k in ("inventory", "runtime_picture", "design_picture") if win.get(k)}


def page_size(inventory: Path, unit: str) -> dict | None:
    """`{"w", "h"}` of a unit's first window: ctig writes the object, a pair is read as `[w, h]`."""
    manifest = load(inventory / "manifest.json", "inventory manifest")
    row = next((u for u in manifest.get("units", []) if u.get("id") == unit), None)
    if row is None:
        return None
    size = ((load(inventory / row["folder"] / "unit.json", f"inventory unit {unit}").get("windows") or [{}])[0]
            .get("page_size"))
    if isinstance(size, dict) and "w" in size and "h" in size:
        return {"w": size["w"], "h": size["h"]}
    if isinstance(size, (list, tuple)) and len(size) == 2:
        return {"w": size[0], "h": size[1]}
    return None


ITEM_KIND = {"devices": "symbol", "flows": "pipe", "readouts": "readout", "indicators": "indicator", "static": "label"}


def write(out: Path, model: dict, slices: dict, units: dict, inventory: Path | None, pictures: Path | None) -> list[str]:
    missing = []
    for p in model["pages"]:
        if not p["built"]:
            continue
        folder = out / p["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        files = unit_files(inventory, p["id"]) if inventory else {}
        nav = [n for n in model["nav"] if (n.get("uid") or "").startswith(p["id"] + ":")
               or n["from"].startswith(p["id"] + " ")]
        slice_ = {"page": p, "page_size": page_size(inventory, p["id"]) if inventory else None,
                  "items": slices[p["id"]]["items"], "devices": slices[p["id"]]["devices"],
                  "nav": nav, "navigation": nav, "alarms": [a for a in model["alarms"] if a["node"] == p["node"]]}
        provenance.write_json(folder / "page.json", slice_)
        provenance.write_json(folder / "understanding.json", units[p["id"]])
        for key, name in (("inventory", "inventory.json"), ("runtime_picture", "runtime.png")):
            if files.get(key) and files[key].is_file():
                shutil.copyfile(files[key], folder / name)
            else:
                missing.append(f"{p['folder']}/{name}")
        shot = (pictures / f"{p['id']}.png") if pictures else None
        if shot and shot.is_file():
            shutil.copyfile(shot, folder / "preview.png")
        else:
            missing.append(f"{p['folder']}/preview.png")
    return missing


def main(argv: list[str] | None = None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--understandings", required=True, metavar="LIST")
    ap.add_argument("--faceplates", required=True)
    ap.add_argument("--tables", required=True)
    ap.add_argument("--openers", required=True)
    ap.add_argument("--inventory", required=True, metavar="DIR")
    ap.add_argument("--device-model", default=None)
    ap.add_argument("--menu", default=None)
    ap.add_argument("--contract", default=None)
    ap.add_argument("--pictures", default=None, metavar="DIR")
    ap.add_argument("--support-routes", default=None)
    ap.add_argument("--tag-root", default="")
    ap.add_argument("--hierarchy", choices=("menu", "contract"), default="menu")
    ap.add_argument("--site-name", default="Site", help="the root node's name for the menu hierarchy")
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        if a.hierarchy == "menu" and not a.menu:
            raise InputFault("--hierarchy menu needs --menu")
        if a.hierarchy == "contract" and not a.contract:
            raise InputFault("--hierarchy contract needs --contract")
        paths = path_list(a.understandings)
        docs = [check_understanding(load(p, "understanding"), p) for p in paths]
        ids = [d["unit"]["id"] for d in docs]
        if len(ids) != len(set(ids)):
            raise InputFault("understandings: a unit id is given twice")
        faceplates = load(a.faceplates, "faceplates")
        tables = load(a.tables, "tables")
        openers = load(a.openers, "openers")
        menu = menu_rows(load(a.menu, "menu")) if a.menu else []
        contract = load(a.contract, "contract") if a.contract else None
        device_model = load(a.device_model, "device model") if a.device_model else None
        support = {**LIBRARY_ROUTES, **(load(a.support_routes, "support routes") if a.support_routes else {})}
        inventory = Path(a.inventory)
        if not (inventory / "manifest.json").is_file():
            raise InputFault(f"inventory: {inventory}: no manifest.json")
        model, slices = build(docs, faceplates, tables, openers, menu, contract, device_model, a.hierarchy,
                              a.tag_root, support, catalogue_of(), a.site_name)
    except InputFault as e:
        print(f"asm_model: {e}")
        return 1
    out = Path(a.out)
    units = {d["unit"]["id"]: d for d in docs}
    missing = write(out, model, slices, units, inventory, Path(a.pictures) if a.pictures else None)
    inputs = [Path(p) for p in paths] + [Path(x) for x in (a.faceplates, a.tables, a.openers, a.menu, a.contract,
                                                            a.device_model, a.support_routes) if x] + [inventory]
    inputs += [Path(a.understandings)]
    model["provenance"] = {**clock.provenance(TOOL, args, inputs), "missing_files": missing}
    provenance.write_json(out / "model.json", model)
    unresolved = len(model["unresolved"])
    print(f"asm_model: nodes {len(model['nodes'])}, pages {len(model['pages'])}, devices {len(model['devices'])}, "
          f"alarms {len(model['alarms'])}, tags {len(model['tags'])}, nav {len(model['nav'])}, "
          f"mapping {len(model['mapping'])}, unmapped {len(model['unmapped'])}, unresolved {unresolved}")
    return 2 if model["unmapped"] or unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
