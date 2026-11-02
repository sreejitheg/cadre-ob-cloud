"""The library gaps of a migration: which kinds the designs use, who draws each (the Cadre OpenBridge module, the
library's own view, or nobody), and the gaps that remain.

Generalised from the eng02 slice's gaps file and the module audit of its Level 4 (ARCH-WFB-01 revision B8 Table 109,
WFBD-091). The commands reads the catalogue from the repository (`library/contracts.json`, `library/profile.json`,
`module/components.json`), so that a library change is seen by the next run.

    --model F --designs LIST     the ASM model and the page designs (a list file of paths)
    --catalogue F --profile F --module F   the library's views, its profile, the module's parts
    --design F                   the project design (`wfb.migration.project_design/1`, block 18): its parts and
                                 features, `mapping[].component`, `mapping[].properties`, `devices[].component`
                                 and `faceplates[]`, are resolved against the catalogue and the descriptor schema;
                                 `--designs` may then be left out
    --descriptor-schema F        the descriptor schema (`schemas/screen-descriptor.schema.json`), needed with --design
    --module-first               prefer the module's part where it has one (OpenBridge first)
    --parent P         the parent project the profile must name (default: not checked)
    --accepted LIST              the gaps the owner accepted: a JSON array of ids (or of {"id", "reason"}), a JSON
                                 object with `accepted` or `gaps_settled`, or one id to a line
    --out O                      writes O/gaps.json (`cadre-hmi-library-gaps/1`) and O/audit.json (the table)

Exit codes: 0 no open gap; 2 open (or partial) gaps; 1 a fault. Nothing here contacts a gateway.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import provenance  # noqa: E402
    from hmi.asm_model import InputFault, load, path_list  # noqa: E402
    from hmi.screen import KIND_VIEW  # noqa: E402
    from hmi.framework import faceplate_view as library_faceplate  # noqa: E402
else:
    from . import provenance
    from .asm_model import InputFault, load, path_list
    from .screen import KIND_VIEW
    from .framework import faceplate_view as library_faceplate

TOOL = "tools/hmi/library_gaps.py"
#: Item kinds of a design that are descriptor arrays of their own and not library kinds.
BUILTIN = {"label", "link", "button", "pipe", "bar", "trend", "alarm-panel", "well", "line"}


def read_accepted(path) -> dict[str, str]:
    """`{gap id: reason}` of the accepted gaps in `path` (see the module's docstring for the forms)."""
    if not path:
        return {}
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        doc = json.loads(text)
    except ValueError:
        doc = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
    if isinstance(doc, dict):
        doc = doc.get("accepted") or doc.get("gaps_settled") or []
    out = {}
    for x in doc:
        if isinstance(x, str):
            out[x] = ""
        elif isinstance(x, dict) and x.get("id"):
            out[x["id"]] = x.get("reason") or ""
    return out


def part_name(kind: str) -> str:
    return "cadre.ob." + kind.replace("-", "")


# Design component names for what the library itself draws, never a descriptor element: a pop-up's rows and whole tabs
# land on the device's faceplate (the faceplate check covers it by the device's kind), and the frame is the parent's.
LIBRARY_CONTENT = {"faceplate-row": "faceplate", "faceplate-tab": "faceplate", "frame": "frame"}


def element_key(name: str) -> str:
    """The descriptor key of an element kind: `bar` is `bars`, `alarm-panel` is `alarmPanels`."""
    head, *rest = name.split("-")
    return head + "".join(w[:1].upper() + w[1:] for w in rest) + "s"


def _feature_gap(gid, name, first, library_today, needed, rows, accepted):
    status = "accepted" if gid in accepted else "open"
    return {"id": gid, "kind": name, "item": first, "library_today": library_today, "needed": needed,
            "status": status,
            "reason": accepted.get(gid) or ("accepted without a reason" if status == "accepted"
                                            else "the catalogue lacks it and no owner decision accepts it"),
            "mapping_rows": rows}


def item_properties(schema: dict, key: str) -> dict | None:
    """The item properties of the descriptor element `key` (a `$ref` into `$defs` followed), or None for an element
    the schema lacks."""
    element = (schema.get("properties") or {}).get(key)
    if element is None:
        return None
    item = element.get("items") or {}
    ref = item.get("$ref")
    if ref:
        item = (schema.get("$defs") or schema.get("definitions") or {}).get(ref.rsplit("/", 1)[-1]) or {}
    return item.get("properties") or {}


def property_resolves(props: dict, name: str) -> bool:
    """`a` among `props`; `a.b` inside the property `a` (an object without listed properties takes any key)."""
    head, _, rest = name.partition(".")
    if head not in props:
        return False
    if not rest:
        return True
    inner = props[head] or {}
    return "properties" not in inner or property_resolves(inner["properties"], rest)


def properties_of(design: dict, schema: dict, accepted: dict[str, str]) -> tuple[list, list]:
    """`mapping[].properties` (S11-D addendum): each descriptor key an entry needs on its element (a device kind's
    element is `symbols`) resolves among the element's item properties; a key that does not is a gap row. A view's
    properties, and those of an element the schema lacks (its own gap), are not counted."""
    seen: dict[tuple[str, str], list] = {}
    for r in design.get("mapping") or []:
        name = (r.get("component") or "").strip()
        if not name or "/" in name or not r.get("properties"):
            continue
        key = "symbols" if name.lower() in KIND_VIEW else element_key(name)
        if item_properties(schema, key) is None:
            continue
        for prop in r.get("properties") or []:
            seen.setdefault((key, str(prop)), []).append(r.get("entry"))
    found, gaps = [], []
    for (key, prop), entries in sorted(seen.items()):
        ok = property_resolves(item_properties(schema, key) or {}, prop)
        found.append({"name": f"{key}.{prop}", "class": "property", "count": len(entries), "pages": [], "resolved": ok})
        if not ok:
            gaps.append(_feature_gap(f"GAP-property-{key}.{prop}", f"{key}.{prop}", entries[0],
                                     f"the descriptor schema gives the element {key} no property {prop}",
                                     f"the property {prop} on {key}", entries, accepted))
    return found, gaps


def features(design: dict, catalogue: dict, schema: dict, used: dict, accepted: dict[str, str]):
    """The parts and features of a project design against the catalogue (S11-D addendum): every component name of
    `mapping[]` and `devices[]` resolves as a device kind (added to `used`, for the kind analysis), a catalogue view
    (a name with a `/`) or a descriptor element (its key among the descriptor schema's properties); a name that
    resolves nowhere is a gap. Every faceplate kind needs the view the library opens for it in the asm style
    (`framework.faceplate_view`: motor and fan open the pump's), in the catalogue, and a tab other than `home` needs
    that view's `tab` parameter; a kind the library's map lacks is a gap. Names are compared, never judged."""
    keys = set(schema.get("properties") or {})
    seen: dict[str, dict] = {}
    rows = [(r.get("entry"), r.get("component"), r.get("page")) for r in design.get("mapping") or []]
    rows += [(d.get("device"), d.get("component"), None) for d in design.get("devices") or []]
    for entry, component, page in rows:
        name = (component or "").strip()
        if not name:
            continue
        target = used if name.lower() in KIND_VIEW else seen
        key = name.lower() if target is used else name
        f = target.setdefault(key, {"count": 0, "pages": [], "items": []})
        f["count"] += 1
        if page and page not in f["pages"]:
            f["pages"].append(page)
        f["items"].append(entry)
    found, gaps = [], []
    for name in sorted(seen):
        f = seen[name]
        if name.lower() in LIBRARY_CONTENT:  # a faceplate's rows and tabs, the frame: never descriptor elements
            found.append({"name": name, "class": LIBRARY_CONTENT[name.lower()], "count": f["count"],
                          "pages": f["pages"], "resolved": True})
            continue
        if "/" in name:
            cls, resolved, gid = "view", name in catalogue, f"GAP-view-{name}"
            today = f"the catalogue holds no view {name}"
        else:
            key = element_key(name)
            cls, resolved, gid = "element", key in keys, f"GAP-element-{key}"
            today = (f"the descriptor schema has no element {key}; the name is no kind, view or descriptor element "
                     "of the library")
        found.append({"name": name, "class": cls, "count": f["count"], "pages": f["pages"], "resolved": resolved})
        if not resolved:
            gaps.append(_feature_gap(gid, name, f["items"][0], today, f"the library to draw {name}", f["items"],
                                     accepted))
    for fp in design.get("faceplates") or []:
        kind = (fp.get("kind") or "").strip()
        if not kind:
            continue
        view, users = library_faceplate(kind, "asm"), [str(u) for u in fp.get("used_by") or []]
        first = users[0] if users else kind
        if not view:
            gaps.append(_feature_gap(f"GAP-faceplate-{kind}", kind, first, "the library has no faceplate for the kind",
                                     f"a faceplate for {kind}", users, accepted))
            continue
        if view not in catalogue:
            found.append({"name": view, "class": "faceplate", "count": len(users), "pages": [], "resolved": False})
            gaps.append(_feature_gap(f"GAP-faceplate-{kind}", kind, first, f"the catalogue holds no view {view}",
                                     f"a faceplate for {kind}", users, accepted))
            continue
        found.append({"name": view, "class": "faceplate", "count": len(users), "pages": [], "resolved": True})
        tabbed = "tab" in ((catalogue[view] or {}).get("params") or {})
        for tab in fp.get("tabs") or []:
            ok = tab == "home" or tabbed
            found.append({"name": f"{view}#{tab}", "class": "tab", "count": len(users), "pages": [], "resolved": ok})
            if not ok:
                gaps.append(_feature_gap(f"GAP-tab-{kind}-{tab}", kind, first,
                                         f"the view {view} takes no tab parameter: one pane only",
                                         f"the {tab} tab of the {kind} faceplate", users, accepted))
    more, more_gaps = properties_of(design, schema, accepted)
    return found + more, gaps + more_gaps


def analyse(model: dict, designs: list[dict], catalogue: dict, profile: dict, module: dict, module_first: bool,
            accepted: dict[str, str], design: dict | None = None, schema: dict | None = None) -> dict:
    mapping = {r["uid"]: r for r in model["mapping"]}
    used: dict[str, dict] = {}
    found, feature_gaps = features(design, catalogue, schema or {}, used, accepted) if design else ([], [])
    for d in designs:
        for it in d.get("items", []):
            kind = (it.get("component") or "").lower()
            if it.get("kind") in BUILTIN or not kind:
                continue
            u = used.setdefault(kind, {"count": 0, "pages": [], "items": []})
            u["count"] += 1
            if d["page"] not in u["pages"]:
                u["pages"].append(d["page"])
            u["items"].append(it["uid"])
    kinds, gaps = [], []
    for kind in sorted(used):
        u = used[kind]
        view = KIND_VIEW.get(kind)
        in_library = kind in profile["kinds"] and view in catalogue
        part = part_name(kind) if part_name(kind) in module else None
        if not in_library:
            choice, resolution = "gap", "gap"
            reason = ("the library has no symbol of this kind: the generator draws a counted gap box" if
                      kind not in profile["kinds"] else f"the catalogue holds no view {view} for the kind")
        elif part and module_first:
            choice, resolution = "module", "module"
            reason = f"OpenBridge first: the module draws the kind with {part}"
        elif part:
            choice, resolution = "library", "library"
            reason = f"the library's view is chosen; the module's {part} is not preferred (module-first is off)"
        else:
            choice, resolution = "library", "library"
            reason = "the module has no part for this kind; the library draws it"
        kinds.append({"kind": kind, "count": u["count"], "pages": u["pages"], "resolution": resolution,
                      "part": part if resolution == "module" else view if in_library else None,
                      "audit": {"module_part": part, "library_part": view if in_library else None,
                                "choice": choice, "reason": reason}})
        if not in_library:
            gid = f"GAP-{kind}"
            first = u["items"][0]
            types = sorted({(mapping.get(uid) or {}).get("device") or "" for uid in u["items"]} - {""})
            status = "accepted" if gid in accepted else "open"
            gaps.append({"id": gid, "kind": kind, "item": first,
                         "library_today": "no symbol of this kind; drawn as a counted gap box",
                         "needed": f"a library symbol for {kind}" + (f" (devices {', '.join(types)})" if types else ""),
                         "status": status,
                         "reason": accepted.get(gid) or ("accepted without a reason" if status == "accepted"
                                                         else "the library lacks the kind and no owner decision accepts the box"),
                         "mapping_rows": u["items"]})
    gaps += feature_gaps
    open_count = sum(1 for g in gaps if g["status"] in ("open", "partial"))
    return {"schema": "cadre-hmi-library-gaps/1", "kinds": kinds, "gaps": gaps, "open_count": open_count,
            "features": found}


def main(argv: list[str] | None = None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--model", required=True)
    ap.add_argument("--designs", default=None, metavar="LIST")
    ap.add_argument("--design", default=None, help="the project design (wfb.migration.project_design/1)")
    ap.add_argument("--descriptor-schema", default=None, help="schemas/screen-descriptor.schema.json, with --design")
    ap.add_argument("--catalogue", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--module", required=True)
    ap.add_argument("--module-first", action="store_true")
    ap.add_argument("--accepted", default=None)
    ap.add_argument("--parent", default=None, help="the parent project the profile must name (`library`); not checked "
                                                   "without it")
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args_line = sys.argv[1:] if argv is None else list(argv)
    try:
        if not a.designs and not a.design:
            raise InputFault("give --designs, --design or both")
        if a.design and not a.descriptor_schema:
            raise InputFault("--design needs --descriptor-schema: an element name resolves against its keys")
        model = load(a.model, "model")
        designs = [load(p, "design") for p in path_list(a.designs)] if a.designs else []
        design = load(a.design, "project design") if a.design else None
        schema = load(a.descriptor_schema, "descriptor schema") if a.descriptor_schema else None
        catalogue = load(a.catalogue, "catalogue")
        profile = load(a.profile, "profile")
        module = load(a.module, "module components")
        accepted = read_accepted(a.accepted)
        if a.parent and profile.get("library") != a.parent:
            raise InputFault(f"--profile names the parent {profile.get('library')!r}, not {a.parent!r}")
    except (InputFault, OSError) as e:
        print(f"library_gaps: {e}")
        return 1
    doc = analyse(model, designs, catalogue, profile, module, a.module_first, accepted, design, schema)
    given = [a.designs, a.design, a.descriptor_schema, a.accepted]
    doc["provenance"] = clock.provenance(TOOL, args_line, [Path(a.model), Path(a.catalogue), Path(a.profile),
                                                           Path(a.module)] + [Path(p) for p in given if p])
    out = Path(a.out)
    provenance.write_json(out / "gaps.json", doc)
    provenance.write_json(out / "audit.json", [{"kind": k["kind"], "count": k["count"],
                                                "module_part": k["audit"]["module_part"],
                                                "library_part": k["audit"]["library_part"],
                                                "choice": k["audit"]["choice"], "reason": k["audit"]["reason"]}
                                               for k in doc["kinds"]])
    print(f"library_gaps: kinds {len(doc['kinds'])}, module {sum(k['resolution'] == 'module' for k in doc['kinds'])}, "
          f"library {sum(k['resolution'] == 'library' for k in doc['kinds'])}, gaps {len(doc['gaps'])}, "
          f"features {len(doc['features'])}, open {doc['open_count']}")
    return 2 if doc["open_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
