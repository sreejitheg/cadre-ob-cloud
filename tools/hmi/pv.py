"""Perspective emit primitives: component nodes, views, bindings, resources, projects.

Every shape here traces to the Ignition-Wiki (`F:/repos/Ignition-Wiki`), cited as
`IGW:<page> section`, or to a measurement on the 8.3.6 gateway recorded in this
repository's wiki page 07. Nothing is written from recall.

The module is stdlib only and deterministic: the same input gives the same bytes.
"""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

ACTOR = "Cadre HMI Library tools/hmi"
STAMP = "2026-10-07T00:00:00Z"   # fixed, so a rebuild is byte identical
PERSPECTIVE = "com.inductiveautomation.perspective"
CONTAINERS = {"ia.container.flex", "ia.container.coord"}


# --------------------------------------------------------------------------
# Component nodes. IGW:02-view-anatomy section 5: type, meta, position, props,
# propConfig, events, custom, children; a node writes only what it carries.
# --------------------------------------------------------------------------
def node(ctype: str, name: str, position: dict, props: dict | None = None, *,
         prop_config: dict | None = None, events: dict | None = None,
         children: list | None = None, custom: dict | None = None) -> dict:
    props = dict(props or {})
    if ctype in CONTAINERS:
        # DEF-04 of Cadre-Sandbox-SCADA, generalised: a container left at the browser's
        # automatic overflow draws a sub-pixel scrollbar when content is a fraction of a pixel
        # larger than its box (measured again 2026-10-07 in a 20 px flex row, GF-09). Every
        # container is `hidden` unless it asks for scrolling explicitly.
        style = dict(props.get("style") or {})
        style.setdefault("overflow", "hidden")
        props["style"] = style
    n = {"type": ctype, "meta": {"name": name}, "position": position, "props": props}
    if prop_config:
        n["propConfig"] = prop_config
    if events:
        n["events"] = events
    if custom:
        n["custom"] = custom
    if children is not None:
        n["children"] = children
    return n


def view(root: dict, *, params: dict | None = None, param_dirs: dict | None = None,
         size: dict | None = None, custom: dict | None = None,
         custom_config: dict | None = None, param_change: dict | None = None) -> dict:
    """A view.json document. IGW:02-view-anatomy section 1 and 1.1: the configuration
    key is `propConfig` at the view level as at the component level. `param_change` attaches a
    change script to a parameter: `{"enabled": null, "script": ...}` with `self` the view, the
    shape IGW:09-params-and-custom section 6 shows on a view parameter."""
    pc = {}
    for k, d in (param_dirs or {}).items():
        pc[f"params.{k}"] = {"paramDirection": d, "persistent": True}
    for k, lines in (param_change or {}).items():
        pc.setdefault(f"params.{k}", {"persistent": True})["onChange"] = {
            "enabled": None, "script": "".join("\t" + ln + "\n" for ln in lines).rstrip("\n")}
    for k in (custom_config or {}):
        # IGW:02-view-anatomy section 3: view-level keys are `custom.<name>` and
        # `params.<name>`; `view.custom...` is the reference form used inside expressions.
        # A `view.`-prefixed key passes the registry validator and fails at runtime
        # (measured 2026-10-07, wiki page 07 GF-07).
        if not k.startswith(("custom.", "params.")):
            raise ValueError(f"view-level propConfig key {k!r} must start with custom. or params.")
    pc.update(custom_config or {})
    doc = {"custom": custom or {}, "params": params or {}, "propConfig": pc, "props": {},
           "root": root}
    if size:
        doc["props"]["defaultSize"] = size
    return doc


# --------------------------------------------------------------------------
# Position contracts. IGW:04-position-contract sections 3.3 and 3.4.
# --------------------------------------------------------------------------
def cpos(x: float, y: float, w: float, h: float) -> dict:
    """Child of ia.container.coord: x, y, width, height (the corpus majority)."""
    return {"x": x, "y": y, "width": w, "height": h}


def fpos(basis=None, grow=None, shrink=None, align=None) -> dict:
    """Child of ia.container.flex: all keys optional."""
    p = {}
    for k, v in (("basis", basis), ("grow", grow), ("shrink", shrink), ("align", align)):
        if v is not None:
            p[k] = v
    return p


# --------------------------------------------------------------------------
# Bindings. IGW:06-bindings sections 2 to 4; transforms IGW:07-transforms.
# --------------------------------------------------------------------------
def bind(cfg: dict, transforms: list | None = None) -> dict:
    b = dict(cfg)
    if transforms:
        b["transforms"] = transforms
    return {"binding": b}


def expr(expression: str) -> dict:
    return {"config": {"expression": expression}, "type": "expr"}


def prop(path: str, bidirectional: bool = False) -> dict:
    cfg = {"path": path}
    if bidirectional:
        cfg["bidirectional"] = True
    return {"config": cfg, "type": "property"}


def tag(path: str, bidirectional: bool = False) -> dict:
    """Direct tag binding. IGW:06-bindings section 4; config keys are exactly those
    binding-tag.json declares (bidirectional, mode, references, tagPath)."""
    cfg = {"mode": "direct", "tagPath": path}
    if bidirectional:
        cfg["bidirectional"] = True
    return {"config": cfg, "type": "tag"}


def tag_indirect(path: str, refs: dict, bidirectional: bool = False) -> dict:
    """Indirect tag binding: `{name}` placeholders resolved from `references`."""
    cfg = {"mode": "indirect", "references": refs, "tagPath": path}
    if bidirectional:
        cfg["bidirectional"] = True
    return {"config": cfg, "type": "tag"}


def tag_history(tags, most_recent: str, units: str = "HOUR", *, polling_rate: str = "10",
                aggregate: str = "Average", return_format: str = "Wide", value_format: str = "DATASET",
                rows: str = "300") -> dict:
    """A tag history binding (IGW:06-bindings section 7, the corpus exemplar's keys). `tags` shall
    reference an array: a literal list of `{"path": ...}` objects, or a brace reference to a property
    that holds such a list. A reference to a property holding a tag path string is rejected by the
    8.3.6 runtime ("Tag history binding "tags" expression must reference array value",
    Cadre-Sandbox-ASM GATEWAY-01 section 5.2), so a bare string is refused here; a caller that passes
    a reference also gives that property a list default (gate G7 checks it)."""
    if isinstance(tags, list):
        if not tags or not all(isinstance(t, dict) and t.get("path") is not None for t in tags):
            raise ValueError("tag history tags: a list of objects that each carry 'path'")
    elif not (isinstance(tags, str) and tags.startswith("{") and tags.endswith("}")):
        raise ValueError(f"tag history tags {tags!r}: must be a list of path objects or a brace reference "
                         "to a property holding one")
    return {"config": {"aggregate": aggregate, "avoidScanClassValidation": True,
                       "dateRange": {"mostRecent": most_recent, "mostRecentUnits": units},
                       "ignoreBadQuality": False, "polling": {"enabled": True, "rate": polling_rate},
                       "preventInterpolation": False, "returnFormat": return_format,
                       "returnSize": {"numRows": rows, "type": "FIXED"}, "tags": tags,
                       "valueFormat": value_format},
            "type": "tag-history"}


def script_transform(lines: list[str]) -> dict:
    """A script transform, body indented one tab (IGW:02-view-anatomy section 3.1)."""
    return {"code": "".join("\t" + ln + "\n" for ln in lines).rstrip("\n"), "type": "script"}


def fmt_numeric(pattern: str) -> dict:
    """A format transform. `formatType` is required (IGW:07-transforms; SC-01 of
    Cadre-Sandbox-SCADA: without it the transform yields null)."""
    return {"formatType": "numeric", "formatValue": pattern, "type": "format"}


# --------------------------------------------------------------------------
# Events. IGW:12-events-and-actions sections 4 and 5.
# --------------------------------------------------------------------------
def script_handler(lines: list[str]) -> dict:
    return {"config": {"script": "".join("\t" + ln + "\n" for ln in lines).rstrip("\n")},
            "scope": "G", "type": "script"}


def on_click(lines: list[str]) -> dict:
    """dom.onClick with one script action (the shape the demo census also shows)."""
    return {"dom": {"onClick": script_handler(lines)}}


def on_action(lines: list[str]) -> dict:
    """component.onActionPerformed for ia.input.button."""
    return {"component": {"onActionPerformed": script_handler(lines)}}


# --------------------------------------------------------------------------
# Resources and projects. Shapes proven on 8.3.6 by Cadre-Sandbox-SCADA (2026-09-07)
# and IGW:01-project-anatomy sections 2 to 9.
# --------------------------------------------------------------------------
def resource_json(files: list[str], scope: str = "G") -> dict:
    return {"attributes": {"lastModification": {"actor": ACTOR, "timestamp": STAMP}},
            "files": files, "overridable": True, "restricted": False, "scope": scope,
            "version": 1}


class Project:
    """An in-memory project tree: relative path -> bytes. Written or zipped at the end."""

    def __init__(self, name: str, title: str, *, inheritable: bool = False, parent: str = "",
                 description: str = ""):
        self.name = name
        self.files: dict[str, bytes] = {}
        pj = {"description": description, "enabled": True, "inheritable": inheritable,
              "parent": parent, "title": title}
        self.put("project.json", pj)

    def put(self, rel: str, body) -> None:
        if isinstance(body, (dict, list)):
            data = (json.dumps(body, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        elif isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = body
        self.files[rel.replace("\\", "/")] = data

    def add_view(self, path: str, doc: dict) -> None:
        base = f"{PERSPECTIVE}/views/{path}"
        self.put(f"{base}/view.json", doc)
        self.put(f"{base}/resource.json", resource_json(["view.json"]))

    def add_style_class(self, name: str, base_style: dict, variants: list | None = None) -> None:
        """A style class: folder path is the class name (IGW:08-style-and-themes section 3)."""
        body = {"base": {"style": base_style}}
        if variants:
            body["variants"] = variants
        base = f"{PERSPECTIVE}/style-classes/{name}"
        self.put(f"{base}/style.json", body)
        self.put(f"{base}/resource.json", resource_json(["style.json"]))

    def set_stylesheet(self, css: str) -> None:
        """The project stylesheet (IGW:01-project-anatomy section 6)."""
        base = f"{PERSPECTIVE}/stylesheet"
        self.put(f"{base}/stylesheet.css", css)
        self.put(f"{base}/resource.json", resource_json(["stylesheet.css"]))

    def set_page_config(self, cfg: dict) -> None:
        base = f"{PERSPECTIVE}/page-config"
        self.put(f"{base}/config.json", cfg)
        self.put(f"{base}/resource.json", resource_json(["config.json"]))

    def set_session_props(self, props: dict) -> None:
        base = f"{PERSPECTIVE}/session-props"
        self.put(f"{base}/props.json", props)
        self.put(f"{base}/resource.json", resource_json(["props.json"]))

    def add_script_library(self, path: str, code: str) -> None:
        """A project library script (IGW:01-project-anatomy; ignition/script-python)."""
        base = f"ignition/script-python/{path}"
        self.put(f"{base}/code.py", code)
        self.put(f"{base}/resource.json", resource_json(["code.py"], scope="A"))

    def write(self, root: Path) -> Path:
        out = root / self.name
        if out.exists():
            for p in sorted(out.rglob("*"), reverse=True):
                p.unlink() if p.is_file() else p.rmdir()
        for rel, data in sorted(self.files.items()):
            f = out / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
        return out

    def zip_bytes(self) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for rel, data in sorted(self.files.items()):
                info = zipfile.ZipInfo(rel, date_time=(2026, 10, 7, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, data)
        return buf.getvalue()
