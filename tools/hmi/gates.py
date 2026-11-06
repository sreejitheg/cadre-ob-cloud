"""The gates every build passes before anything reaches the gateway.

  G1 registry    `F:/repos/Ignition-Wiki/tools/validate_view.py --project`, zero errors, and the same
                 registry below the top level of a component's props (`_deep_findings`)
  G2 references  every embedded view path, style class and `var(--token)` resolves in the
                 child or its parent (the stylesheet's declared variables, the style classes,
                 the views of both projects)
  G3 view keys   view-level propConfig keys are `custom.` or `params.` (a `view.` key passes G1
                 and fails at runtime: GF-07)
  G4 project     routes and docks name existing views; navigation items name existing routes;
                 the child's parent is the base and the base is inheritable
  G5 layout      in a generated diagram, symbol boxes lie inside the canvas and do not overlap; a symbol wholly inside
                 a vessel and clear of the vessel's own texts and level is placed there on purpose (`vessel.py`)
  G6 flow        compiled pipe expressions agree with the reference solver (screen report)
  G7 contract    no unknown kind or parameter (screen report)
  G7 devices     with a device model: every device symbol names a device of the model, binds members
                 the model lists and opens the faceplate of the device's kind; every member is one the
                 library profile knows for the kind, and a writable one has a write path; a force is
                 one whole encoding; a pulse is a writable Boolean pulse member of the kind; an alarm
                 source names a tag; with a tag model, the members exist there with their types and
                 no writable one is an expression tag

Usage:
    python tools/hmi/gates.py --project build/cadre_hmi_demo --parent build/cadre_hmi_base
        [--screen-report workspace/reports/x.json] [--report out.json]
Exit 1 when any gate fails.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import vessel  # noqa: E402
else:
    from . import vessel

VALIDATOR = Path("F:/repos/Ignition-Wiki/tools/validate_view.py")
ROOT = Path(__file__).resolve().parents[2]
MODULE_CONTRACT = ROOT / "module" / "components.json"
MODULE_SCHEMAS = ROOT / "module" / "common" / "src" / "main" / "resources"
P = "com.inductiveautomation.perspective"
VAR_DEF = re.compile(r"(--[\w-]+)\s*:")
VAR_USE = re.compile(r"var\(\s*(--[\w-]+)")
VIEW_PATH_PROP = ("path",)


def views_of(prj: Path) -> dict[str, dict]:
    out = {}
    base = prj / P / "views"
    for f in base.rglob("view.json"):
        out[f.parent.relative_to(base).as_posix()] = json.loads(f.read_text(encoding="utf-8"))
    return out


def classes_of(prj: Path) -> set[str]:
    base = prj / P / "style-classes"
    return {f.parent.relative_to(base).as_posix() for f in base.rglob("style.json")} if base.exists() else set()


def walk(n, path="root"):
    yield n, path
    for i, c in enumerate(n.get("children") or []):
        yield from walk(c, f"{path}/{c.get('meta', {}).get('name', i)}")


PROP_SEGMENT = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def _deep_props(value, schema, path: str, out: list, depth: int = 0) -> None:
    """A component's props below the top level, against its registry schema: a text value outside the
    enumerated domain of its property, and a key a closed object does not declare (for example
    `plots[].trends[].interpolation` of the time series chart). The validator of the Ignition-Wiki
    reads the top level only. A part of the schema this walk cannot follow (a reference, a choice)
    is left alone, never failed."""
    if not isinstance(schema, dict):
        return
    if depth > 1 and isinstance(schema.get("enum"), list) and isinstance(value, str) and value not in schema["enum"]:
        out.append(("ENUM_VIOLATION", f"{path} is {value!r}; declared domain is {schema['enum']}"))
    if isinstance(value, dict) and isinstance(schema.get("properties"), dict):
        for k, v in value.items():
            if k in schema["properties"]:
                _deep_props(v, schema["properties"][k], f"{path}.{k}", out, depth + 1)
            elif depth and schema.get("additionalProperties") is False:
                out.append(("UNDECLARED_PROP", f"{path}.{k} is not declared"))
    elif isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, v in enumerate(value):
            _deep_props(v, schema["items"], f"{path}[{i}]", out, depth + 1)


def _bound_undeclared(target: str, schema) -> str | None:
    """The first part of a bound property path (`props.plots[0].trends[0].interpolation`) that a
    closed schema does not declare, else None: the path is declared, or the schema cannot tell."""
    if not target.startswith("props."):
        return None
    at = "props"
    for name, index in PROP_SEGMENT.findall(target[len("props."):]):
        if not isinstance(schema, dict):
            return None
        if index:
            schema, at = schema.get("items"), f"{at}[{index}]"
            continue
        declared = schema.get("properties")
        if not isinstance(declared, dict):
            return None
        if name not in declared:
            return f"{at}.{name}" if schema.get("additionalProperties") is False else None
        schema, at = declared[name], f"{at}.{name}"
    return None


def _deep_findings(node, reg, view: str, findings: list, path: str = "root") -> None:
    """`_deep_props` and `_bound_undeclared` on every component of a view, as findings of the
    validator's form (the node path by child index, as the validator writes it)."""
    if not isinstance(node, dict):
        return
    ctype = node.get("type")
    schema = reg.schema(ctype) if isinstance(ctype, str) and ctype in reg.components else None
    if schema:
        out: list = []
        if isinstance(node.get("props"), dict):
            _deep_props(node["props"], schema, "props", out)
        for target in (node.get("propConfig") or {}):
            bad = _bound_undeclared(str(target), schema)
            if bad:
                out.append(("UNDECLARED_PROP", f"{target} is bound; {bad} is not declared by {ctype}"))
        findings += [{"view": view, "node": path, "severity": "ERROR", "check": check, "detail": detail}
                     for check, detail in out]
    for i, child in enumerate(node.get("children") or []):
        _deep_findings(child, reg, view, findings, f"{path}/{i}")


def g1_registry(prj: Path) -> dict:
    """The Ignition-Wiki validator, run as a library so that the components of our own module
    (module/components.json, schemas generated from the OpenBridge manifest) join its registry
    and are checked like stock components: declared props and enumerated domains. The validator
    reads the top level of a component's props; `_deep_findings` adds the levels below it (an
    enumerated value, a key of a closed object, a bound path), so that the chart's
    `plots[].trends[]` are checked too."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("validate_view", VALIDATOR)
    vv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vv)
    reg = vv.Registry(vv.SCHEMA_DIR)
    added = []
    if MODULE_CONTRACT.exists():
        for ctype, c in json.loads(MODULE_CONTRACT.read_text(encoding="utf-8")).items():
            reg.components[ctype] = {"component": ctype, "schema": str(MODULE_SCHEMAS / c["schema"])}
            added.append(ctype)
    findings: list = []
    views = sorted(prj.rglob("view.json"))
    for v in views:
        before = len(findings)
        vv.validate_view(v, reg, findings)
        if not any(f["check"] in ("UNREADABLE", "NOT_A_VIEW") for f in findings[before:]):
            _deep_findings(json.loads(v.read_text(encoding="utf-8-sig"))["root"], reg, str(v), findings)
    errors =[f for f in findings if f["severity"] == "ERROR"]
    summary = [f"views checked: {len(views)}", f"ERROR: {len(errors)}"] + [
        f"[ERROR] {f['check']} {f['view'].split('views', 1)[-1]} @{f['node']}: {f['detail']}" for f in errors[:10]]
    return {"ok": not errors, "summary": summary, "module_components": added}


def g2_references(child: Path, parent: Path | None) -> dict:
    views = {**(views_of(parent) if parent else {}), **views_of(child)}
    classes = classes_of(child) | (classes_of(parent) if parent else set())
    css = ""
    for prj in (parent, child):
        if prj and (prj / P / "stylesheet" / "stylesheet.css").exists():
            css += (prj / P / "stylesheet" / "stylesheet.css").read_text(encoding="utf-8")
    defined = set(VAR_DEF.findall(css))
    problems = []
    for vp, doc in views_of(child).items():
        text = json.dumps(doc)
        for v in set(VAR_USE.findall(text)) - defined:
            problems.append(f"{vp}: var({v}) is not defined by any stylesheet")
        for n, path in walk(doc["root"]):
            p = n.get("props", {})
            if n.get("type") in ("ia.display.view", "ia.display.flex-repeater") and p.get("path") \
                    and "props.path" not in (n.get("propConfig") or {}):
                if p["path"] not in views:
                    problems.append(f"{vp} {path}: embedded view {p['path']!r} does not exist")
            cls = (p.get("style") or {}).get("classes")
            for c in (cls.split() if isinstance(cls, str) else []):
                if c not in classes:
                    problems.append(f"{vp} {path}: style class {c!r} does not exist")
            for k, cfg in (n.get("propConfig") or {}).items():
                ex = (cfg.get("binding") or {}).get("config", {}).get("expression", "")
                for c in re.findall(r"'(cadre/[\w/-]+)'", ex):
                    if c not in classes and not c.endswith("/"):
                        problems.append(f"{vp} {path}: bound style class {c!r} does not exist")
    return {"ok": not problems, "problems": problems[:40], "count": len(problems),
            "variables_defined": len(defined), "classes": len(classes), "views": len(views)}


def expressions_of(node) -> list[str]:
    """Every expression string under `node` (a binding's `config.expression`, in a property binding or a transform)."""
    found = []
    if isinstance(node, dict):
        found += [v for k, v in node.items() if k == "expression" and isinstance(v, str)]
        found += [e for v in node.values() for e in expressions_of(v)]
    elif isinstance(node, list):
        found += [e for v in node for e in expressions_of(v)]
    return found


CUSTOM_REF = re.compile(r"\{view\.custom\.([^.}\[\s]+)")   # the top-level key: a name may hold a hyphen (`g_ind-level-high`)


def g3_view_keys(child: Path) -> dict:
    """G3: a view-level `propConfig` key is `custom.` or `params.` (GF-07); and every `{view.custom.<name>}` an
    expression of the view names is a key of the view's `custom` (COB-212; a key that only a binding would make is
    undefined until the binding delivers, and for ever when its tag is bad: a pipe that names the state of a switch the
    view never defines is a failed binding, and Perspective frames the component)."""
    bad = []
    for vp, doc in views_of(child).items():
        for k in (doc.get("propConfig") or {}):
            if not k.startswith(("custom.", "params.")):
                bad.append(f"{vp}: view-level key {k!r}")
        defined = set(doc.get("custom") or {})
        undefined = sorted({n for e in expressions_of(doc) for n in CUSTOM_REF.findall(e)} - defined)
        bad += [f"{vp}: an expression names view.custom.{n}, which the view does not define" for n in undefined]
    return {"ok": not bad, "problems": bad}


def g4_project(child: Path, parent: Path | None) -> dict:
    problems = []
    pj = json.loads((child / "project.json").read_text(encoding="utf-8"))
    if parent:
        ppj = json.loads((parent / "project.json").read_text(encoding="utf-8"))
        if not ppj.get("inheritable"):
            problems.append("parent is not inheritable")
        if pj.get("parent") != parent.name:
            problems.append(f"child parent {pj.get('parent')!r} is not {parent.name!r}")
    views = {**(views_of(parent) if parent else {}), **views_of(child)}
    pc_file = child / P / "page-config" / "config.json"
    pc = json.loads(pc_file.read_text(encoding="utf-8")) if pc_file.exists() else {"pages": {}}
    for route, page in pc.get("pages", {}).items():
        if page.get("viewPath") not in views:
            problems.append(f"route {route}: view {page.get('viewPath')!r} missing")
    for side, docks in (pc.get("sharedDocks") or {}).items():
        if isinstance(docks, list):
            for d in docks:
                if d.get("viewPath") not in views:
                    problems.append(f"dock {d.get('id')}: view {d.get('viewPath')!r} missing")
    sp_file = child / P / "session-props" / "props.json"
    if sp_file.exists():
        sp = json.loads(sp_file.read_text(encoding="utf-8"))
        for grp in ("items", "footer"):
            for it in sp.get("custom", {}).get("nav", {}).get(grp, []):
                if it.get("path") and it["path"] not in pc.get("pages", {}):
                    problems.append(f"nav {grp} {it.get('label')!r}: route {it['path']!r} missing")
    return {"ok": not problems, "problems": problems, "routes": len(pc.get("pages", {}))}


# Two boxes of a diagram overlap when they share more than this many px on both axes. The generator
# keeps the same tolerance when it widens an embed (`screen.OVERLAP`, pinned equal by the tests), and
# the library profile publishes it (`diagram.overlap`).
OVERLAP = 4


def block_warnings(vp: str, c: dict, contracts: dict) -> list[str]:
    """What a diagram's block is too small for, by the sizes the library states (its contract, which the
    library profile publishes): a box smaller than the size its flags need (`sizes`: a readout with its
    identifier), and an identifier or a caption wider than the embed, which then ends in an ellipsis
    (`library.identifier_needs`). The generator sizes the embed of an automation symbol and of a readout
    itself, so those are named only where the next symbol left the identifier no room
    (`screen.embed_limits`) or the identifier is longer than the library allows for."""
    if __package__ in (None, ""):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from hmi import library
    else:
        from . import library
    contract = contracts.get(c.get("props", {}).get("path", ""))
    if not contract or "size" not in contract:
        return []
    params = c["props"].get("params", {})
    name, w, h = c["meta"]["name"], c["position"]["width"], c["position"]["height"]
    out = []
    ident = contract.get("identifier")
    shown = params
    if ident and ident.get("flag"):
        # A flag the generator binds (the toolbar's ID-tag button, `screen.embed_symbol`) is judged by its
        # binding, whose expression ends in the descriptor's own answer; no value is stated beside it (GF-61).
        # The block's size is judged the same way: a readout keeps the identifier's room while the button hides it.
        bound = (c.get("propConfig") or {}).get(f"props.params.{ident['flag']}", {}).get("binding", {}) \
            .get("config", {}).get("expression", "")
        if bound:
            shown = dict(params, **{ident["flag"]: not bound.rstrip().endswith("&& false")})
    need = library.block_size(contract, shown)
    if need != list(contract["size"]) and (w < need[0] or h < need[1]):
        when = next(e["when"] for e in contract["sizes"] if list(e["size"]) == need)
        flags = ", ".join(f"{k} {json.dumps(v)}" for k, v in sorted(when.items()))
        out.append(f"{vp}: {name} is {w:g} x {h:g} px and needs {need[0]:g} x {need[1]:g} px with {flags}")
    if ident and library.identifier_shown(contract, shown):
        text = str(params.get(ident["param"], "") or "")
        tail = str(params.get(ident.get("suffix", ""), "") or "")
        chars = len(text) + (len(tail) + 1 if text and tail else len(tail))
        wide = library.identifier_needs(contract, params, chars)        # the whole text, however long
        if text and wide > w:
            out.append(f"{vp}: {name} is {w:g} px wide and its {ident['param']} of {chars} characters needs "
                       f"{wide:g} px: it ends in an ellipsis")
    return out


def g5_layout(child: Path) -> dict:
    problems, warnings, checked = [], [], 0
    lib = ROOT / "library" / "contracts.json"
    contracts = json.loads(lib.read_text(encoding="utf-8")) if lib.exists() else {}
    for vp, doc in views_of(child).items():
        for n, path in walk(doc["root"]):
            if n.get("meta", {}).get("name") != "Diagram":
                continue
            st = n.get("props", {}).get("style", {})
            W, H = (float(str(st.get("width", "0")).rstrip("px")), float(str(st.get("height", "0")).rstrip("px")))
            boxes, embeds, vessels = [], [], {}
            for c in n.get("children", []):
                module = str(c.get("type", "")).startswith("cadre.ob.")   # its box is the symbol box
                if c.get("type") != "ia.display.view" and not module:
                    continue
                p = c["position"]
                e = (p["x"], p["y"], p["x"] + p["width"], p["y"] + p["height"], c["meta"]["name"])
                if e[0] < 0 or e[1] < 0 or e[2] > W or e[3] > H:
                    problems.append(f"{vp}: {e[4]} outside the canvas")
                embeds.append(e)
                boxes.append(e if module else symbol_box_of(c, e))
                if (c.get("type") if module else c["props"].get("path")) in vessel.CONTAINER_VIEWS:
                    props = c.get("props") or {}
                    vessels[e[4]] = props if module else props.get("params") or {}
                if not module:
                    warnings += block_warnings(vp, c, contracts)
            for group, sink, label in ((boxes, problems, "symbol"), (embeds, warnings, "readout area")):
                for i, a in enumerate(group):
                    for b in group[i + 1:]:
                        checked += 1
                        ix = min(a[2], b[2]) - max(a[0], b[0])
                        iy = min(a[3], b[3]) - max(a[1], b[1])
                        if ix > OVERLAP and iy > OVERLAP:
                            why = vessel_overlap(a, b, vessels)
                            if why != "":
                                sink.append(f"{vp}: {label} {a[4]} overlaps {b[4]} ({ix:.0f} x {iy:.0f} px)"
                                            + (f": {why}" if why else ""))
    return {"ok": not problems, "problems": problems[:30], "warnings": warnings[:30], "pairs": checked}


def vessel_overlap(a: tuple, b: tuple, vessels: dict[str, dict]) -> str | None:
    """For two overlapping boxes (x0, y0, x1, y1, name): "" where one lies wholly inside a vessel that is the other and
    clear of the vessel's own bands (placed there on purpose), the reason where it crosses the vessel's outline or covers
    a band, None for two boxes that are no vessel and its content."""
    for box, held in ((b, a), (a, b)):
        params = vessels.get(box[4])
        if params is None or held[4] in vessels:
            continue
        rect = (box[0], box[1], box[2] - box[0], box[3] - box[1])
        within, covered = vessel.placed_inside((held[0], held[1], held[2] - held[0], held[3] - held[1]), rect, params,
                                               OVERLAP)
        if not within:
            return f"it crosses the outline of the vessel {box[4]}"
        return f"it covers the {' and the '.join(covered)} of the vessel {box[4]}" if covered else ""
    return None


def symbol_box_of(c: dict, e: tuple) -> tuple:
    """The 48 px symbol inside an automation symbol embed, from its readout side (the inverse
    of screen.symbol_box); every other embed is its own box."""
    path = c["props"].get("path", "")
    if not path.startswith("Automation/") or path in ("Automation/Tank", "Automation/Readout"):
        return e
    pos = c["props"].get("params", {}).get("readoutPosition", "bottom")
    x0, y0, x1, y1, name = e
    w = x1 - x0
    if pos == "right":
        return (x0, y0, x0 + 48, y0 + 48, name)
    if pos == "left":
        return (x1 - 48, y0, x1, y0 + 48, name)
    if pos == "top":
        return (x0 + (w - 48) / 2, y1 - 48, x0 + (w + 48) / 2, y1, name)
    return (x0 + (w - 48) / 2, y0, x0 + (w + 48) / 2, y0 + 48, name)


FACEPLATES = ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/Tank", "Faceplate/Instrument",
              "Faceplate/Controller", "Faceplate/Input", "Faceplate/Sequence",
              "Faceplate/ASM/Pump", "Faceplate/ASM/Valve",   # the `asm` style (COBD-045)
              "Faceplate/ASM/Generator", "Faceplate/ASM/Sequence", "Faceplate/ASM/Instrument",   # COB-158
              "Faceplate/ASM/Local")   # the local assembly's device (NOTE-WFB-10 section 11.2 item 5)
ALARM_LISTS = {"ia.display.alarmstatustable": "props.filters.active.conditions.source",
               "cadre.ob.alertlist": "props.alerts"}


def _bound_expr(n: dict, key: str) -> str | None:
    b = ((n.get("propConfig") or {}).get(key) or {}).get("binding")
    return (b or {}).get("config", {}).get("expression") if b else None


def g7_faceplates(child: Path, parent: Path | None) -> dict:
    """The faceplate contract of COB-076, on the views a session of the child resolves (a child
    view overrides the parent's): each device faceplate carries the tab row and one pane per tab
    shown by `{view.custom.tab}`; the first tab is the default and a new device resets to it; the
    Alarms pane embeds `Faceplate/Alarms`, which holds one alarm list narrowed by the device's
    source pattern and carries no text filter."""
    views = {**(views_of(parent) if parent else {}), **views_of(child)}
    problems, checked = [], {}
    for fp in FACEPLATES:
        doc = views.get(fp)
        if not doc:
            problems.append(f"{fp}: missing")
            continue
        nodes = {n.get("meta", {}).get("name"): n for n, _ in walk(doc["root"])}
        tabs = [c["meta"]["name"][4:] for c in (nodes.get("Tabs") or {}).get("children", [])
                if c.get("meta", {}).get("name", "").startswith("Tab_")]
        checked[fp] = tabs
        if not tabs:
            problems.append(f"{fp}: no tab row")
            continue
        if (doc.get("custom") or {}).get("tab") != tabs[0]:
            problems.append(f"{fp}: the default tab is not the first, {tabs[0]!r}")
        reset = (((doc.get("propConfig") or {}).get("params.deviceId") or {}).get("onChange") or {}).get("script", "")
        if f"self.custom.tab = '{tabs[0]}'" not in reset:
            problems.append(f"{fp}: a new device does not reset the tab to {tabs[0]!r}")
        for k in tabs:
            pane = nodes.get(f"Pane_{k}")
            if not pane:
                problems.append(f"{fp}: tab {k!r} has no pane")
            elif _bound_expr(pane, "position.display") != f"{{view.custom.tab}} = '{k}'":
                problems.append(f"{fp}: pane {k!r} is not shown by its tab")
            elif not pane.get("children"):
                problems.append(f"{fp}: pane {k!r} is empty")
        if "alarms" in tabs:
            embeds = [n for n, _ in walk(nodes.get("Pane_alarms") or {"children": []})
                      if n.get("type") == "ia.display.view" and (n.get("props") or {}).get("path") == "Faceplate/Alarms"]
            if not embeds or _bound_expr(embeds[0], "props.params.source") is None:
                problems.append(f"{fp}: the Alarms pane does not embed Faceplate/Alarms with the device's source")
    lists = views.get("Faceplate/Alarms")
    found = [n for n, _ in walk(lists["root"]) if n.get("type") in ALARM_LISTS] if lists else []
    if not found or len({n["type"] for n in found}) != 1:
        problems.append(f"Faceplate/Alarms: alarm lists {[n['type'] for n in found]}, expected one kind")
    for n in found:   # the module rendering draws active and cleared alerts in two lists of one data
        if not ((n.get("propConfig") or {}).get(ALARM_LISTS[n["type"]]) or {}).get("binding"):
            problems.append(f"Faceplate/Alarms: {n['type']} {n['meta']['name']} is not bound to the device")
        if n["type"] == "ia.display.alarmstatustable" and (
                "props.filters.active.text" in (n.get("propConfig") or {})
                or ((n.get("props") or {}).get("filters") or {}).get("active", {}).get("text")):
            problems.append("Faceplate/Alarms: the table still filters by text")
        if n["type"] == "cadre.ob.alertlist":   # display only (COBD-025): no acknowledge event
            acks = [e for e in ((n.get("events") or {}).get("component") or {}) if "ack" in e.lower()]
            if acks:
                problems.append(f"Faceplate/Alarms: {n['meta']['name']} carries {acks}; the module tab is display only")
    if any(n["type"] == "cadre.ob.alertlist" for n in found):
        # every record is marked noAck, so OpenBridge draws no ACK in a row (the pin's rule)
        cfg = ((lists.get("propConfig") or {}).get("custom.alarms") or {}).get("binding") or {}
        code = " ".join(t.get("code", "") for t in cfg.get("transforms") or [])
        if "no_ack=True" not in code:
            problems.append("Faceplate/Alarms: the module list's records are not marked noAck")
    return {"ok": not problems, "problems": problems, "tabs": checked,
            "alarm_list": [n["type"] for n in found]}


def g7_history(child: Path, parent: Path | None) -> dict:
    """Every tag history binding's `tags` references an array: a literal list of objects that each
    carry `path`, or a brace reference to a view property whose default is such a list. A reference
    to a property holding a path string is rejected by the 8.3.6 runtime (Cadre-Sandbox-ASM
    GATEWAY-01 section 5.2; IGW:06-bindings section 7.1)."""
    problems, checked = [], 0
    views = {**(views_of(parent) if parent else {}), **views_of(child)}
    for vp, doc in views.items():
        configs = [(k, c) for k, c in (doc.get("propConfig") or {}).items()]
        for n, path in walk(doc["root"]):
            configs += [(f"{path}.{k}", c) for k, c in (n.get("propConfig") or {}).items()]
        for where, c in configs:
            b = (c or {}).get("binding") or {}
            if b.get("type") != "tag-history":
                continue
            checked += 1
            tags = (b.get("config") or {}).get("tags")
            if isinstance(tags, list):
                if not tags or not all(isinstance(t, dict) and "path" in t for t in tags):
                    problems.append(f"{vp} {where}: tags list entries need 'path'")
            elif isinstance(tags, str) and re.fullmatch(r"\{view\.custom\.([\w]+)\}", tags):
                name = re.fullmatch(r"\{view\.custom\.([\w]+)\}", tags).group(1)
                default = (doc.get("custom") or {}).get(name)
                if not (isinstance(default, list) and all(isinstance(t, dict) and "path" in t for t in default)):
                    problems.append(f"{vp} {where}: tags references view.custom.{name}, whose default is not a list of paths")
            else:
                problems.append(f"{vp} {where}: tags {tags!r} is neither a list of paths nor a reference to one")
    return {"ok": not problems, "problems": problems, "bindings": checked}


# Command security (COB-063, NOTE-COB-04 section 6.2 step 6 and Table 6 test T2): a view writes a tag or an
# alarm only through the checked functions of cadre.hmi, never directly and never through a two way tag
# binding (a binding write runs no check); every control that calls a checked function binds `enabled` to
# the permission of the write path it calls; every stock alarm status table binds its own actions to them
# (GF-40).
#
# What a view script may read of the tag, alarm and OPC systems. Every other name of them is a write or an
# action and is refused, as is the bare module (`t = system.tag`, `getattr(system.tag, ...)`), which would
# hide the name called from this gate.
SYSTEM_READS = {"tag": ("exists", "readBlocking", "readAsync", "browse", "queryTagHistory"),
                "alarm": ("queryStatus", "queryJournal"), "opc": ()}
DIRECT = re.compile(r"system\s*\.\s*(tag|alarm|opc)\b(?:\s*\.\s*(\w+))?")
# `system` is named only with a module after it (`system.perspective.openDock`): an import of it or
# from it, an alias (`s = system`), a lookup (`getattr(system, 'tag')`) and a private name of it would
# each reach a write under a name this gate does not read.
SYSTEM_BARE = re.compile(r"\bsystem\b(?!\s*\.\s*[A-Za-z])")
# `cadre` likewise: only as `cadre.hmi.<name>` or `cadre.icons.<name>` (`from cadre import hmi` hides
# every name called).
CADRE_BARE = re.compile(r"\bcadre\b(?!\s*\.\s*(?:hmi|icons)\b)")
# The private names of cadre.hmi (a leading underscore) are helpers of the checked functions and are not
# for a view; the bare module would hide the name called.
HMI_NAME = re.compile(r"cadre\s*\.\s*hmi\b(?:\s*\.\s*(\w+))?")
# Every name a script takes from a library of the project (F050 of the ASMP study, COB-142): the source's
# alarm handlers named functions their module lacked, and nothing told. A name is resolved against the
# library code the projects ship (`ignition/script-python/cadre/<module>/code.py`), never against a list.
LIBRARY_NAME = re.compile(r"\bcadre\s*\.\s*(hmi|icons)\s*\.\s*([A-Za-z_]\w*)")
LIBRARY_DEF = re.compile(r"^(?:def\s+([A-Za-z]\w*)\s*\(|([A-Za-z]\w*)\s*=)", re.M)
RUN_SCRIPT = re.compile(r"""runScript\s*\(\s*['"]([\w.]+)['"]""")


def library_names(*projects: Path | None) -> dict[str, set[str]]:
    """The public names each `cadre` library of the projects defines, by module (`hmi`, `icons`): its
    top-level functions and constants. A later project's library replaces an earlier one's, as a
    child's script overrides its parent's."""
    out: dict[str, set[str]] = {}
    for prj in projects:
        base = (prj / "ignition" / "script-python" / "cadre") if prj else None
        if not base or not base.is_dir():
            continue
        for code in sorted(base.glob("*/code.py")):
            names = {a or b for a, b in LIBRARY_DEF.findall(code.read_text(encoding="utf-8"))}
            out[code.parent.name] = {n for n in names if not n.startswith("_")}
    return out


def _unresolved(script: str, defined: dict[str, set[str]]) -> list[str]:
    """The `cadre.<module>.<name>` a script names that no library of the projects defines."""
    return sorted({f"cadre.{m}.{n}" for m, n in LIBRARY_NAME.findall(script)
                   if not n.startswith("_") and n not in defined.get(m, set())})
# The checked functions that write, each with its write path; `command` takes its path as an argument.
CALL_PATH = {"cadre.hmi.bypass(": "W10", "cadre.hmi.reset_interlocks(": "W11", "cadre.hmi.ack_top(": "W6",
             "cadre.hmi.force(": "W16", "cadre.hmi.error_mask(": "W17", "cadre.hmi.pulse(": "W18",
             "cadre.hmi.page_pulse(": "W18"}   # page_pulse: a page command button (COB-159)
CHECKED_CALLS = ("cadre.hmi.command(",) + tuple(CALL_PATH)
# A script calls a checked function wherever it names one, however the name is spelt and whatever
# follows it: `cadre.hmi.pulse (`, `cadre . hmi . pulse(`, `f = cadre.hmi.pulse` and
# `cadre.hmi.pulse.__call__(` each count as the call, so each needs the control's `enabled` binding.
NAME_PATH = {call[len("cadre.hmi."):-1]: w for call, w in CALL_PATH.items()}
CHECKED_NAMES = re.compile(r"cadre\s*\.\s*hmi\s*\.\s*(%s)\b"
                           % "|".join(call[len("cadre.hmi."):-1] for call in CHECKED_CALLS))
COMMAND_PATH = re.compile(r"cadre\s*\.\s*hmi\s*\.\s*command\s*\(\s*[^,()]+,\s*([^,()]+),")
TABLE_ACTIONS = ("enableAcknowledge", "enableShelve", "enableUnshelve")
TABLE_PATH = "W7"


def _scripts_of(n: dict) -> list[str]:
    """Every script of a node: its event handlers, the change scripts and script transforms of its
    bindings, its custom methods, message handlers and extension functions (every `script` under
    `scripts`), and any expression that calls `runScript`, which runs a script from a binding."""
    out = []
    for group in (n.get("events") or {}).values():
        for h in (group or {}).values():
            for one in (h if isinstance(h, list) else [h]):
                out.append(((one or {}).get("config") or {}).get("script", ""))

    def collect(x):
        if isinstance(x, dict):
            for k, v in x.items():
                out.append(v) if k == "script" and isinstance(v, str) else collect(v)
        elif isinstance(x, list):
            for v in x:
                collect(v)
    collect(n.get("scripts"))
    for c in (n.get("propConfig") or {}).values():
        out.append(((c or {}).get("onChange") or {}).get("script", ""))
        b = (c or {}).get("binding") or {}
        exprs = [(b.get("config") or {}).get("expression")]
        for t in (b.get("transforms") or []):
            out.append((t or {}).get("code", ""))
            exprs.append((t or {}).get("expression"))
        out += [e for e in exprs if isinstance(e, str) and "runScript" in e]
    return [s for s in out if s]


def _top_level(expr: str, op: str) -> list[str]:
    """`expr` split at `op` wherever it stands outside every bracket, brace and quote."""
    parts, depth, quote, start, i = [], 0, None, 0, 0
    while i < len(expr):
        ch = expr[i]
        if quote:
            quote = None if ch == quote else quote
        elif ch in "'\"":
            quote = ch
        elif ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        elif depth == 0 and expr.startswith(op, i):
            parts.append(expr[start:i])
            i += len(op)
            start = i
            continue
        i += 1
    parts.append(expr[start:])
    return [p.strip() for p in parts]


def _paths_called(script: str) -> list[str]:
    """The write path of each checked write a script calls: `Wn`; `{view.params.x}` where `command`
    takes its path from a view parameter (the setpoint row); `?` where the path cannot be told. A
    checked function counts as called wherever it is named (CHECKED_NAMES): spaced, aliased or
    handed on, the name still needs the permission of its path."""
    named = CHECKED_NAMES.findall(script)
    out = [NAME_PATH[name] for name in named if name in NAME_PATH]
    found = COMMAND_PATH.findall(script)
    for arg in found:
        arg = arg.strip()
        literal = re.fullmatch(r"""['"](W\d+)['"]""", arg)
        param = re.fullmatch(r"self\.view\.params\.(\w+)", arg) or (
            re.fullmatch(r"p\.(\w+)", arg) if re.search(r"^\s*p = self\.view\.params\s*$", script, re.M) else None)
        # the faceplate's Confirm row (F029): the path of the pending command
        pending = re.fullmatch(r"p\.(path)", arg) if re.search(
            r"^\s*p = self\.view\.custom\.pending\s*$", script, re.M) else None
        out.append(literal.group(1) if literal else "{view.params.%s}" % param.group(1) if param
                   else "{view.custom.pending.%s}" % pending.group(1) if pending else "?")
    if named.count("command") != len(found):   # `command` named and not called with a path that can be read
        out.append("?")
    return out


def _case_follows(term: str, subject: str) -> bool:
    """`term` is `case(<subject>, 'Wa', {view.custom.can.Wa}, ..., false)`: each path to its own
    permission, and no permission for any other value."""
    m = re.fullmatch(r"case\((.*)\)", term, re.S)
    args = _top_level(m.group(1), ",") if m else []
    if len(args) < 4 or len(args) % 2 or args[0] != subject or args[-1] != "false":
        return False
    return all(re.fullmatch(r"'W\d+'", k) and v == "{view.custom.can.%s}" % k[1:-1]
               for k, v in zip(args[1:-1:2], args[2:-1:2]))


def _follows_permissions(n: dict, key: str, path: str) -> bool:
    """The property is bound, by an expression without a transform, to the permission of write path
    `path`: `{view.custom.can.<path>}` alone, or joined by `&&` to other conditions. An `||` beside it,
    another path's permission, a constant, or the permission inside a function does not follow it. For
    a path taken from a view parameter the term is a `case` over that parameter (`_case_follows`)."""
    b = ((n.get("propConfig") or {}).get(key) or {}).get("binding") or {}
    if b.get("type") != "expr" or b.get("transforms"):
        return False
    expr = str((b.get("config") or {}).get("expression", ""))
    if len(_top_level(expr, "||")) > 1:
        return False
    terms = _top_level(expr, "&&")
    if path.startswith("{"):
        return any(_case_follows(t, path) for t in terms)
    return "{view.custom.can.%s}" % path in terms


def g7_commands(child: Path, parent: Path | None) -> dict:
    """Command security on every view a session of the child resolves (a child view overrides the
    parent's): no direct tag write, alarm action or OPC call in any script (event, change script,
    transform, custom method, message handler, `runScript` expression), no `system` and no `cadre`
    named without its module (an import, an alias, a lookup), no private function of cadre.hmi, no
    bidirectional tag binding, the `enabled` of each control that names a checked write bound to the
    permission of the path it calls, no checked write at view level (where no control's `enabled` can
    follow it), and the actions of each stock alarm status table bound.

    The gate reads the text of the scripts the generator wrote. It is a check on generated views, not
    a defence against a script written by hand to evade it: a name built from text at run time
    (`getattr(x, 'sys' + 'tem')`, `eval`, `__import__`) is not seen. The role check inside each
    checked function is the control; this gate keeps the views honest about it."""
    views = {**(views_of(parent) if parent else {}), **views_of(child)}
    defined = library_names(parent, child)
    problems, checked = [], 0
    for vp, doc in views.items():
        nodes = [(doc, "view")] + [(n, p) for n, p in walk(doc["root"])]
        for n, where in nodes:
            for script in _scripts_of(n):
                checked += 1
                for mod, name in sorted(set(DIRECT.findall(script))):
                    if name not in SYSTEM_READS[mod]:
                        problems.append(f"{vp} {where}: a direct system.{mod}{'.' + name if name else ''} "
                                        "(use the checked functions of cadre.hmi)")
                if SYSTEM_BARE.search(script):
                    problems.append(f"{vp} {where}: system named without a module (an import, an alias or a "
                                    "lookup would hide the function called)")
                if CADRE_BARE.search(script):
                    problems.append(f"{vp} {where}: cadre named without cadre.hmi or cadre.icons (an import or "
                                    "an alias would hide the function called)")
                for name in sorted(set(HMI_NAME.findall(script))):
                    if not name or name.startswith("_"):
                        problems.append(f"{vp} {where}: cadre.hmi{'.' + name if name else ''} is not a function "
                                        "for a view (a private helper, or the module itself)")
                for name in _unresolved(script, defined):   # F050: a function the library lacks
                    problems.append(f"{vp} {where}: {name} is not defined by the project's library "
                                    f"(cadre/{name.split('.')[1]})")
                paths = sorted(set(_paths_called(script)))
                if "runScript" in script and CHECKED_NAMES.search(script):
                    problems.append(f"{vp} {where}: a checked write called from an expression (runScript)")
                elif paths and n is doc:
                    problems.append(f"{vp} {where}: a checked write called at view level, where no control's "
                                    "enabled can follow it")
                for path in ([] if n is doc else paths):
                    if path == "?" or not _follows_permissions(n, "props.enabled", path):
                        problems.append(f"{vp} {where}: a command control whose enabled does not follow the "
                                        f"permissions (write path {path})")
            for k, c in (n.get("propConfig") or {}).items():
                b = (c or {}).get("binding") or {}
                if b.get("type") == "tag" and (b.get("config") or {}).get("bidirectional"):
                    problems.append(f"{vp} {where} {k}: a bidirectional tag binding writes without a check")
            if n.get("type") == "ia.display.alarmstatustable":
                missing = [a for a in TABLE_ACTIONS if not _follows_permissions(n, f"props.{a}", TABLE_PATH)]
                if missing:
                    problems.append(f"{vp} {where}: alarm table actions {missing} not bound to the permissions")
    return {"ok": not problems, "problems": problems, "scripts": checked}


ILK_SUMMARY = {"permitted": "Boolean", "interlocked": "Boolean", "bypassed": "Boolean", "unsatisfied": "Int4",
               "resetRequired": "Boolean", "resetAt": "Int8"}
ILK_CONDITION = {"kind": "String", "text": "String", "action": "String", "ok": "Boolean",
                 "liveText": "String", "requiredText": "String", "bypassed": "Boolean", "bypassable": "Boolean",
                 "latched": "Boolean", "resetRequired": "Boolean"}


def g7_tag_libraries(tag_model: dict | None, child: Path, parent: Path | None) -> dict:
    """The tag model's scripts and expressions (F050): every `cadre.<module>.<name>` a tag names, and
    every `runScript` of a `cadre` function, is defined by a library the projects ship. A tag runs in
    the gateway, so a name it lacks fails at runtime with nothing on the glass."""
    defined = library_names(parent, child)
    problems, checked = [], 0

    def walk(node, path):
        nonlocal checked
        for t in node.get("tags", []) if isinstance(node, dict) else []:
            here = f"{path}/{t.get('name', '?')}"
            text = json.dumps({k: v for k, v in t.items() if k != "tags"})
            if "cadre" in text or "runScript" in text:
                checked += 1
            for name in _unresolved(text, defined):
                problems.append(f"{here}: {name} is not defined by the project's library")
            for fn in RUN_SCRIPT.findall(text):
                mod, _, name = fn.partition("cadre.")[2].partition(".")
                if fn.startswith("cadre.") and name not in defined.get(mod, set()):
                    problems.append(f"{here}: runScript of {fn}, which no library of the project defines")
            walk(t, here)
    walk(tag_model or {}, "")
    return {"ok": not problems, "problems": problems, "checked": checked}


def g7_interlocks(tag_model: dict | None) -> dict:
    """The interlock contract (COB-079, wiki page 13 section 7) on every `ilk` folder of the tag
    model: the summary members with their types, conditions C01, C02 ... without a gap (the faceplate
    lists them until the first missing one), each with its members, a kind of `permissive` or `trip`,
    and every trip latched (COBD-023: a trip latches until it is reset)."""
    problems, devices = [], []

    def walk(node, path):
        for t in node.get("tags", []):
            if t.get("tagType") == "Folder":
                if t["name"] == "ilk":
                    check(t, path + [node["name"]])
                else:
                    walk(t, path + [node["name"]])

    def check(ilk, path):
        dev = "/".join(path)
        devices.append(dev)
        leaves = {t["name"]: t for t in ilk.get("tags", []) if t.get("tagType") != "Folder"}
        for m, dt in ILK_SUMMARY.items():
            if leaves.get(m, {}).get("dataType") != dt:
                problems.append(f"{dev}/ilk: summary member {m} missing or not {dt}")
        conds = sorted(t["name"] for t in ilk.get("tags", []) if t.get("tagType") == "Folder")
        if not conds:
            problems.append(f"{dev}/ilk: no condition")
        if conds != [f"C{n:02d}" for n in range(1, len(conds) + 1)]:
            problems.append(f"{dev}/ilk: conditions {conds} are not C01, C02 ... without a gap")
        for c in (t for t in ilk.get("tags", []) if t.get("tagType") == "Folder"):
            mem = {t["name"]: t for t in c.get("tags", [])}
            for m, dt in ILK_CONDITION.items():
                if mem.get(m, {}).get("dataType") != dt:
                    problems.append(f"{dev}/ilk/{c['name']}: member {m} missing or not {dt}")
            kind = mem.get("kind", {}).get("value")
            if kind not in ("permissive", "trip"):
                problems.append(f"{dev}/ilk/{c['name']}: kind {kind!r} is not permissive or trip")
            if kind == "trip" and mem.get("latched", {}).get("value") is not True:
                problems.append(f"{dev}/ilk/{c['name']}: a trip that does not latch (COBD-023)")
    if tag_model:
        walk(tag_model, [])
    return {"ok": not problems, "problems": problems, "devices": devices}


# The device model (wiki page 08 section 3.1). A member's declared type must suit the type the library
# knows for it: a Boolean and a String exactly, an integer member any integer type, a Float8 member any
# number (a source may hold a value in a narrower type than the library's own).
INTEGERS = ("Int1", "Int2", "Int4", "Int8")
NUMBERS = INTEGERS + ("Float4", "Float8")
ILK_WRITABLE = {"resetAt": "W11", "bypassed": "W10"}


# The caption of a pulse member's button (`Faceplate/Sequence`): one line of the button font in the
# faceplate dock. The schema of the device model states the same bound (`caption`: maxLength, pattern).
CAPTION_MAX = 32


def _caption_fault(caption) -> str | None:
    """What is wrong with a pulse member's caption, else None: it is text of 1 to CAPTION_MAX
    characters, with no space at either end and no line break or other character that does not print
    (a blank caption would draw a button without a name, a long one would run out of it)."""
    if not isinstance(caption, str) or not caption.strip():
        return "is blank"
    if not caption.isprintable():
        return "holds a line break or another character that does not print"
    if caption != caption.strip():
        return "begins or ends with a space"
    if len(caption) > CAPTION_MAX:
        return f"is {len(caption)} characters long, over the {CAPTION_MAX} a button holds"
    return None


# A configuration member (F010, COBD-045): the profile's `config` gives its folder, its path and its types.
CONFIG_PREFIX = "cfg/"


def _config_faults(did: str, kind: str, name: str, spec: dict, kspec: dict, config: dict,
                   tab_label) -> tuple[list[str], list[str]]:
    """The problems and warnings of a member under `cfg/` or marked `config`: a row of the Config tab,
    written through W19 within its bounds."""
    problems, warnings = [], []
    prefix = config.get("prefix", CONFIG_PREFIX)
    if not name.startswith(prefix):
        problems.append(f"{did}: member {name!r} is marked config and is not under {prefix}")
    if "config" not in spec:
        problems.append(f"{did}: member {name!r} lies under {prefix} and is not marked config: no row shows it")
        return problems, warnings
    if not kspec.get("config"):
        problems.append(f"{did}: kind {kind!r} has no Config rows in its faceplate, so member {name!r} shows nowhere")
    if spec.get("type") not in config.get("types", NUMBERS):
        problems.append(f"{did}: configuration member {name!r} is {spec.get('type')}; a Config row takes a number")
    if spec.get("pulse") or "caption" in spec:
        problems.append(f"{did}: configuration member {name!r} carries pulse or a button caption; its caption "
                        "belongs in its config")
    c = spec["config"]
    fault = _caption_fault(c.get("caption"))
    if fault or len(str(c.get("caption", ""))) > config.get("captionMax", CAPTION_MAX):
        problems.append(f"{did}: the caption of configuration member {name!r} "
                        f"{fault or 'is longer than the row label holds'}")
    elif tab_label and tab_label.fullmatch(str(c["caption"])):
        problems.append(f"{did}: the caption {c['caption']!r} of configuration member {name!r} is the label of a "
                        "faceplate tab")
    low, high = c.get("minimum"), c.get("maximum")
    if low is not None and high is not None and low > high:
        problems.append(f"{did}: configuration member {name!r} has its minimum {low} above its maximum {high}")
    if low is None and high is None:
        warnings.append(f"{did}: configuration member {name!r} has no bounds: its row and W19 take any number")
    return problems, warnings


def _suits(declared: str, known: str) -> bool:
    if known in ("Boolean", "String"):
        return declared == known
    return declared in (INTEGERS if known in INTEGERS else NUMBERS)


def _ilk_member(name: str) -> str | None:
    """The type of a member of the interlock contract (`ilk/<summary>`, `ilk/Cnn/<member>`), else None."""
    parts = name.split("/")
    if parts[0] != "ilk":
        return None
    if len(parts) == 2:
        return ILK_SUMMARY.get(parts[1])
    if len(parts) == 3 and re.fullmatch(r"C\d\d", parts[1]):
        return ILK_CONDITION.get(parts[2])
    return None


def _tag_leaves(tag_model: dict | None) -> dict[str, dict]:
    """Every tag of a tag model that is not a folder, by its path below the provider."""
    out: dict[str, dict] = {}

    def walk(node, path):
        for t in node.get("tags", []):
            here = path + [t["name"]]
            if t.get("tagType") == "Folder":
                out["/".join(here) + "/"] = t
                walk(t, here)
            else:
                out["/".join(here)] = t
    if tag_model:
        walk({"tags": [tag_model]}, [])
    return out


def _covers(pattern: str, text: str) -> bool:
    """`text` matches a source pattern, in which `*` stands for any run of characters (the rule of
    `cadre.hmi._matches`). With another pattern as the text: every source it matches, this one matches."""
    return re.fullmatch(".*".join(re.escape(p) for p in pattern.split("*")), text, re.S) is not None


def _folder_source(folder: str) -> str:
    """The one source pattern of a device without `alarmSources` (`cadre.hmi.device_source`)."""
    prov, _, path = folder.strip("[").partition("]")
    return f"prov:{prov}:/tag:{path.strip('/')}/*"


def g7_devices(model: dict, profile: dict, symbols: list[dict], tag_model: dict | None = None,
               alarm_scope: str | None = None) -> dict:
    """The device model (`--devices-file`) against the library profile, the descriptors' device
    symbols (`screen.device_symbols`) and, when one is given, the tag model.

    Model: no device twice; a kind the profile gives a faceplate; every member a name the profile
    knows for the kind (an unknown name is an error, never accepted in silence) in a type that
    suits; every writable member one a write path writes; every trended member one the device lists;
    a force given as one whole encoding (both members of the pair, or of the mode and the value, in
    one access, and not both encodings); every alarm source a pattern that names a tag; a member
    marked `pulse` a pulse member of the kind (`pulses` of the profile), Boolean and writable; no
    caption on a member that is not marked `pulse`, none that is blank, longer than CAPTION_MAX
    characters or not one line of printing text, and none that is the label of a faceplate tab; and
    a pulse member of the kind that is writable marked `pulse`, since its faceplate draws its button.
    Symbols: each names a device of the model; its kind, or the `deviceKind` it carries, opens the
    faceplate of the device's kind; each faceplate parameter it binds points at a member the model
    lists; any other parameter it binds inside the device folder points at a member the model lists
    or, with a tag model, at a tag the tag model carries; a block that draws a setpoint, an output or
    a step number (`hasSetpoint`, `hasOutput`, `hasStep`) belongs to a device that lists the member.
    Tag model: each device folder exists, each listed member exists in the declared type, no member
    marked writable is an expression tag (it refuses a write, GF-49), and the folder carries no
    faceplate member the model leaves out (the faceplate would show it).

    Warnings, reported and not failed: an alarm source that another device's source also matches (the
    alarm is listed on both faceplates and its row opens one of them), and one outside the build's
    alarm scope (the frame's lists leave it out)."""
    problems: list[str] = []
    warnings: list[str] = []
    kinds = profile["deviceKinds"]
    written = {m: w for w, spec in profile["writePaths"].items() for m in spec["members"]}
    encodings = profile.get("forceEncodings", [])
    # the tab labels of the faceplates, as the sweep reads them (a word, and for some a count)
    tabs = sorted({t for f in profile.get("faceplates", {}).values() for t in f.get("tabs", [])})
    tab_label = re.compile(r"\s*(%s)(\s*\(\d+\))?\s*" % "|".join(map(re.escape, tabs)), re.I) if tabs else None
    leaves = _tag_leaves(tag_model)
    root = model.get("tagRoot", "")
    by_folder: dict[str, dict] = {}
    for d in model.get("devices", []):
        did, folder, kind = d["id"], f"{root}/{d['id']}", str(d.get("kind", "")).lower()
        if folder in by_folder:
            problems.append(f"{did}: listed twice")
        by_folder[folder] = d
        for p in d.get("alarmSources", []):
            tag = p.split(":/tag:", 1)[-1].split(":/alm:", 1)[0]
            if not tag.replace("*", "").strip("/"):
                problems.append(f"{did}: alarm source {p!r} names no tag: it would list the alarms of every device")
            elif alarm_scope not in (None, "", "*") and not _covers(alarm_scope, p):
                warnings.append(f"{did}: alarm source {p!r} lies outside the alarm scope {alarm_scope!r}: "
                                "the frame's lists leave its alarms out")
        if kind not in kinds:
            problems.append(f"{did}: kind {d.get('kind')!r} has no faceplate in the library profile")
            continue
        known = kinds[kind]["members"]
        pulsed = kinds[kind].get("pulses", [])
        # a kind that names no member and takes any (the local assembly's device, NOTE-WFB-10 section 11.2 item 4):
        # every member the model lists is accepted; a pulse is still Boolean, written and captioned as any pulse
        open_members = bool(kinds[kind].get("openMembers"))
        modes = d.get("modes")
        if modes is not None:   # ownership by mode (COBD-044)
            owners = profile.get("ownership", {}).get("owners", [])
            spec = d["members"].get("mode")
            if spec is None:
                problems.append(f"{did}: modes are given but the device lists no member 'mode'")
            elif not str(spec.get("type", "")).startswith("Int"):
                problems.append(f"{did}: member 'mode' is {spec.get('type')}; a mode is a whole number")
            for key in ("value", "name"):
                seen = [m.get(key) for m in modes]
                if len(set(map(str, seen))) != len(seen):
                    problems.append(f"{did}: a mode {key} is given twice")
            for m in modes:
                if m.get("owner") not in owners:
                    problems.append(f"{did}: mode {m.get('name')!r} names owner {m.get('owner')!r}, not one of {owners}")
            if "operator" not in [m.get("owner") for m in modes]:
                warnings.append(f"{did}: no mode is held by the operator: the faceplate shows the owner and offers "
                                "no Take control")
        plates = kinds[kind].get("faceplates", {})
        if d.get("faceplate") == "asm" and plates.get("asm") == kinds[kind]["faceplate"]:   # COBD-045
            warnings.append(f"{did}: kind {kind!r} has no faceplate in the asm style: the device opens its "
                            f"openbridge faceplate, {kinds[kind]['faceplate']}")
        for name, spec in d["members"].items():
            if name.startswith(CONFIG_PREFIX) or "config" in spec:   # a Config row (F010, W19)
                p, w = _config_faults(did, kind, name, spec, kinds[kind], profile.get("config", {}), tab_label)
                problems += p
                warnings += w
                continue
            # a pulse command (`cadre.hmi.pulse`, W18): the faceplate draws a button for it, with its caption
            if spec.get("pulse"):
                if name not in pulsed and not open_members:
                    problems.append(f"{did}: member {name!r} is marked a pulse; kind {kind!r} has no pulse "
                                    "member of that name")
                if spec["type"] != "Boolean":
                    problems.append(f"{did}: pulse member {name!r} is {spec['type']}; a pulse is Boolean")
                if spec.get("access") != "write":
                    problems.append(f"{did}: pulse member {name!r} is marked read only; a pulse is written")
                fault = _caption_fault(spec["caption"]) if "caption" in spec else None
                if fault:
                    problems.append(f"{did}: the caption {str(spec['caption'])[:40]!r} of pulse member {name!r} "
                                    f"{fault}: the button draws one line of text")
                if tab_label and tab_label.fullmatch(str(spec.get("caption", ""))):
                    problems.append(f"{did}: the caption {spec['caption']!r} of pulse member {name!r} is the label "
                                    "of a faceplate tab: the button would read as a tab, to an operator and to "
                                    "the faceplate sweep (G11)")
            else:
                if "caption" in spec:
                    problems.append(f"{did}: member {name!r} carries a caption and is not marked a pulse")
                if name in pulsed and spec.get("access") == "write":
                    problems.append(f"{did}: member {name!r} is a pulse member of kind {kind!r} and is marked "
                                    "writable without \"pulse\": true (its faceplate draws its button)")
            if open_members:
                continue
            ilk = _ilk_member(name) if kinds[kind].get("interlocks") else None
            want = known[name]["type"] if name in known else ilk
            if want is None:
                problems.append(f"{did}: member {name!r} is not a member the library knows for kind {kind!r}")
                continue
            if not _suits(spec["type"], want):
                problems.append(f"{did}: member {name!r} is {spec['type']}; the library reads it as {want}")
            path = written.get(name) or (ILK_WRITABLE.get(name.split("/")[-1]) if ilk else None)
            if spec.get("access") == "write" and not path:
                problems.append(f"{did}: member {name!r} is marked writable and no write path writes it")
        for m in d.get("trend", []):
            if m not in d["members"]:
                problems.append(f"{did}: trend names {m!r}, which the device does not list")
        whole = []
        for pair in encodings:   # the faceplate shows a force, and `cadre.hmi.force` writes one, only whole
            got = [m for m in pair if m in d["members"]]
            if len(got) == 1:
                problems.append(f"{did}: member {got[0]!r} without {[m for m in pair if m not in got][0]!r}: "
                                "a force needs both members")
            elif got and len({d["members"][m].get("access") for m in pair}) > 1:
                problems.append(f"{did}: {pair[0]!r} and {pair[1]!r} differ in access: a force is written "
                                "whole or not at all")
            whole += [pair] if len(got) == len(pair) else []
        if len(whole) > 1:
            problems.append(f"{did}: lists the force twice ({' and '.join(', '.join(p) for p in whole)}): "
                            "one encoding only")
    # an alarm two devices share is listed on both faceplates, and its row in the alarm menu opens the
    # first of them in the index (`cadre.hmi.tag_id`): reported, since a source may mean it
    sources = [(d, d.get("alarmSources"), folder) for folder, d in by_folder.items()]
    for i, (a, pa, fa) in enumerate(sources):
        for b, pb, fb in sources[i + 1:]:
            if pa is None and pb is None:   # two folders, as before the device model
                continue
            for x in (pa if pa is not None else [_folder_source(fa)]):
                for y in (pb if pb is not None else [_folder_source(fb)]):
                    if _covers(x, y) or _covers(y, x):
                        warnings.append(f"{a['id']} and {b['id']}: alarm sources {x!r} and {y!r} overlap: an alarm "
                                        "under both is listed on both faceplates")

    def faceplate(kind):
        return (kinds.get(str(kind or "").lower()) or {}).get("faceplate")
    for s in symbols:
        where = f"{s['route']} {s['id']}"
        d = by_folder.get(s["folder"])
        if d is None:
            problems.append(f"{where}: device {s['folder']!r} is not in the device model")
            continue
        kind = str(d.get("kind", "")).lower()
        opens = s.get("deviceKind") or s["kind"]
        if kind in kinds and faceplate(opens) != faceplate(kind):
            problems.append(f"{where}: opens {faceplate(opens) or 'no faceplate'} (kind {str(opens).lower()!r}); "
                            f"the device's kind {kind!r} opens {faceplate(kind)}"
                            + ("" if s.get("deviceKind") else ": name it in params.deviceKind"))
        rule = (kinds.get(kind) or {}).get("bind", {})
        known = (kinds.get(kind) or {}).get("members", {})
        rel = s["folder"].split("]", 1)[-1].strip("/")
        for param, member in s.get("bind", {}).items():
            if param in rule and rule[param] not in d["members"]:
                problems.append(f"{where}: {param!r} is bound to {member!r}; the model lists no member "
                                f"{rule[param]!r} for {d['id']}")
                continue
            # any other parameter bound inside the device folder (`alert`, `badgeControl`): a member the
            # model lists, or a tag of the folder that is no faceplate member and that the tag model carries
            path = (s.get("paths") or {}).get(param, "")
            name = path[len(s["folder"]) + 1:] if path.startswith(s["folder"] + "/") else ""
            if not name or name in d["members"]:
                continue
            if name in known or (_ilk_member(name) and (kinds.get(kind) or {}).get("interlocks")):
                problems.append(f"{where}: {param!r} is bound to {member!r}; the model lists no member "
                                f"{name!r} for {d['id']}")
            elif tag_model is not None and f"{rel}/{name}" not in leaves:
                problems.append(f"{where}: {param!r} is bound to {member!r}, which neither the device model "
                                "nor the tag model carries")
        for flag, param in (("hasSetpoint", "setpoint"), ("hasOutput", "output"), ("hasStep", "step")):
            if (s.get("params") or {}).get(flag) is True and param in rule and rule[param] not in d["members"]:
                problems.append(f"{where}: {flag} is true; the model lists no member {rule[param]!r} for {d['id']}")
    checked = 0
    if tag_model is not None:
        for folder, d in by_folder.items():
            rel = folder.split("]", 1)[-1].strip("/")
            if rel + "/" not in leaves:
                problems.append(f"{d['id']}: the tag model has no folder {rel!r}")
                continue
            for name, spec in d["members"].items():
                checked += 1
                tag = leaves.get(f"{rel}/{name}")
                if tag is None:
                    problems.append(f"{d['id']}: the tag model lacks member {name!r}")
                elif tag.get("dataType") != spec["type"]:
                    problems.append(f"{d['id']}: member {name!r} is {tag.get('dataType')} in the tag model, "
                                    f"{spec['type']} in the device model")
                if tag is not None and spec.get("access") == "write" and tag.get("valueSource") == "expr":
                    problems.append(f"{d['id']}: member {name!r} is marked writable and is an expression tag in "
                                    "the tag model, which refuses a write (GF-49)")
            known = (kinds.get(str(d.get("kind", "")).lower()) or {}).get("members", {})
            for name in known:
                if name not in d["members"] and f"{rel}/{name}" in leaves:
                    problems.append(f"{d['id']}: the tag folder carries {name!r}, which the device model does "
                                    "not list (its faceplate would show it)")
    return {"ok": not problems, "problems": problems, "warnings": warnings,
            "devices": len(model.get("devices", [])), "symbols": len(symbols), "members_in_tag_model": checked}


def run(child: Path, parent: Path | None, screen_report: Path | None = None,
        tag_model: dict | None = None, devices: dict | None = None, symbols: list | None = None,
        profile: dict | None = None, alarm_scope: str | None = None) -> dict:
    res = {"G1_registry": g1_registry(child)}
    if parent:
        res["G1_registry_parent"] = g1_registry(parent)
    res["G2_references"] = g2_references(child, parent)
    res["G3_view_keys"] = g3_view_keys(child)
    res["G4_project"] = g4_project(child, parent)
    res["G5_layout"] = g5_layout(child)
    if screen_report and screen_report.exists():
        # the routes of the screen report: its other key holds the gates of the build that wrote it
        sr = {r: v for r, v in json.loads(screen_report.read_text(encoding="utf-8")).items() if r.startswith("/")}
        flows = {r: v.get("flow", {}) for r, v in sr.items()}
        res["G6_flow"] = {"ok": all(f.get("ok", True) for f in flows.values()),
                          "routes": {r: {k: f.get(k) for k in ("gates", "pipes", "vectors", "mode", "ok")}
                                     for r, f in flows.items() if f}}
        errs = [e for v in sr.values() for e in v.get("errors", [])]
        res["G7_contract"] = {"ok": not errs, "errors": errs,
                              "gaps": [g for v in sr.values() for g in v.get("gaps", [])]}
    res["G7_faceplates"] = g7_faceplates(child, parent)
    res["G7_history"] = g7_history(child, parent)
    res["G7_commands"] = g7_commands(child, parent)
    if tag_model is not None:
        res["G7_interlocks"] = g7_interlocks(tag_model)
        res["G7_tag_libraries"] = g7_tag_libraries(tag_model, child, parent)
    if devices is not None:
        res["G7_devices"] = g7_devices(devices, profile or {"deviceKinds": {}, "writePaths": {}}, symbols or [],
                                       tag_model, alarm_scope)
    res["ok"] = all(v.get("ok", True) for v in res.values() if isinstance(v, dict))
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--parent", default=None)
    ap.add_argument("--screen-report", default=None)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    res = run(Path(a.project), Path(a.parent) if a.parent else None,
              Path(a.screen_report) if a.screen_report else None)
    for k, v in res.items():
        if isinstance(v, dict):
            extra = v.get("problems") or v.get("errors") or v.get("summary") or ""
            print(f"{k:22s} {'PASS' if v.get('ok') else 'FAIL'}  {json.dumps(extra)[:300] if not v.get('ok') else ''}")
    print("ALL GATES", "PASS" if res["ok"] else "FAIL")
    if a.report:
        Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.report).write_text(json.dumps(res, indent=1), encoding="utf-8")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
