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
    --project-survey F           the approved project survey (`cadre-hmi-project-survey/1`), page mode only: a kind the
                                 library lacks is placed by the survey (local, or unbuilt), and a kind or feature the
                                 survey does not hold is a late gap (NOTE-WFB-10 section 9.2); the gap list is
                                 `cadre-hmi-library-gaps/2`
    --openbridge-map F           required with --project-survey: the map whose reviewed rows make the late rule `map`
    --elements F                 with the map (every mode): the elements list; a reviewed or approved map row whose
                                 element is not one of its tags is an input fault (always one with no element)
    --out O                      writes O/gaps.json (`cadre-hmi-library-gaps/1`) and O/audit.json (the table)

Two more modes, written in `placement_survey.py` (NOTE-WFB-10 sections 7.5 to 7.8 and 8.2):

    --survey F    the ctig survey (`ctig.survey/1`); with --catalogue --profile --module --openbridge-map --elements
                  [--local-max N] [--module-first] [--prior-local F]... [--late F]... [--proposals F] [--changes F]
                  --out O: writes O/survey.json (`cadre-hmi-project-survey/1`), O/unmapped.json and
                  O/proposal_source.json. A run given --changes (even an empty list) is a final survey
    --release F   the project survey: with --catalogue --profile --module --openbridge-map --out O writes O/gaps.json
                  (`cadre-hmi-library-gaps/2`), one open gap per `openbridge` and `shared_gap` placement

Every mode refuses, as an input fault naming the file or the row (NOTE-WFB-10 section 11.4): a map row of state `reviewed`
or `approved` with no element, or (given `--elements`; always in survey mode) with an element that is not a tag of the
elements list; in survey mode a map, elements list or library profile that lies in the repository and differs from its
HEAD (the survey records `library_commit` as the tree's state); a `--prior-local` or `--late` file that names another
schema; in release mode a draft survey (its `approval` is null); in page mode `--project-survey` without
`--openbridge-map`.

Exit codes: 0 no open gap (survey and release modes always, once written); 2 open (or partial) gaps, page mode with
no survey; 3 page mode with a survey and a kind placed but not yet built (`unbuilt`); 1 a fault. Nothing here contacts
a gateway.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import provenance  # noqa: E402
    from hmi.asm_model import InputFault, load, path_list  # noqa: E402
    from hmi.screen import KIND_VIEW  # noqa: E402
    from hmi.framework import faceplate_view as library_faceplate  # noqa: E402
    from hmi.placement_survey import (GAPS_SCHEMA, PLACING_STATES, SURVEY_SCHEMA, check_map_rows,  # noqa: E402
                                      element_tags, fold, part_name, run_release, run_survey)
else:
    from . import provenance
    from .asm_model import InputFault, load, path_list
    from .screen import KIND_VIEW
    from .framework import faceplate_view as library_faceplate
    from .placement_survey import (GAPS_SCHEMA, PLACING_STATES, SURVEY_SCHEMA, check_map_rows, element_tags, fold,
                                   part_name, run_release, run_survey)

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


def features(design: dict, catalogue: dict, schema: dict, used: dict, accepted: dict[str, str],
             survey_kinds: set | None = None):
    """The parts and features of a project design against the catalogue (S11-D addendum): every component name of
    `mapping[]` and `devices[]` resolves as a device kind (added to `used`, for the kind analysis), a catalogue view
    (a name with a `/`) or a descriptor element (its key among the descriptor schema's properties); a name that
    resolves nowhere is a gap. Every faceplate kind needs the view the library opens for it in the asm style
    (`framework.faceplate_view`: motor and fan open the pump's), in the catalogue, and a tab other than `home` needs
    that view's `tab` parameter; a kind the library's map lacks is a gap. Names are compared, never judged.

    With a project survey (`survey_kinds`, the kinds it holds; NOTE-WFB-10 section 9.2 item 3) a name the survey holds
    is a kind, and so is the component of a `devices[]` row that is neither a library kind, a view nor a descriptor
    element."""
    keys = set(schema.get("properties") or {})
    seen: dict[str, dict] = {}
    rows = [(r.get("entry"), r.get("component"), r.get("page"), False) for r in design.get("mapping") or []]
    rows += [(d.get("device"), d.get("component"), None, True) for d in design.get("devices") or []]
    device_kinds = {(d.get("component") or "").strip().lower() for d in design.get("devices") or []
                    if (d.get("component") or "").strip() and "/" not in d["component"]
                    and element_key(d["component"].strip()) not in keys}
    for entry, component, page, _is_device in rows:
        name = (component or "").strip()
        if not name:
            continue
        is_kind = name.lower() in KIND_VIEW
        if survey_kinds is not None and not is_kind and name.lower() not in LIBRARY_CONTENT:
            is_kind = name.lower() in survey_kinds or name.lower() in device_kinds
        target = used if is_kind else seen
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


def stem_of(tag) -> str | None:
    """The last segment of a tag folder (`[default]Plant/Area/PUMP01` is `PUMP01`): a device's stem."""
    parts = [x for x in re.split(r"[/\\]", str(tag or "")) if x]
    return parts[-1] if parts else None


def design_instances(model: dict, designs: list[dict], design: dict | None, kinds: set) -> dict[str, list[dict]]:
    """The instances of each kind in `kinds` that the designs draw (NOTE-WFB-10 section 9.2 item 3): a distinct
    `device` of the design's `devices[]` rows (or of the model mapping row an item or entry names), over every page; a
    kind with mapping rows and no device is counted one instance per row. Each is `{key, stem, page, entry}`."""
    mapping = {r["uid"]: r for r in model.get("mapping") or []}
    devices = model.get("devices") or {}
    with_device: dict[str, dict] = {}
    plain: dict[str, dict] = {}

    def add(kind, device, entry, page):
        if kind not in kinds:
            return
        if device:
            d = devices.get(device) or {}
            with_device.setdefault(kind, {}).setdefault(device, {
                "key": device, "stem": stem_of(d.get("tag") or device), "entry": entry,
                "page": d.get("page") or next(iter(d.get("drawn_on") or []), None) or page})
        else:
            plain.setdefault(kind, {}).setdefault("@" + str(entry), {"key": "@" + str(entry), "stem": None,
                                                                    "entry": entry, "page": page})

    for d in designs:
        for it in d.get("items", []):
            kind = (it.get("component") or "").lower()
            if it.get("kind") not in BUILTIN and kind:
                add(kind, (mapping.get(it["uid"]) or {}).get("device"), it["uid"], d.get("page"))
    for r in (design or {}).get("mapping") or []:
        add((r.get("component") or "").strip().lower(), (mapping.get(r.get("entry")) or {}).get("device"),
            r.get("entry"), r.get("page"))
    for r in (design or {}).get("devices") or []:
        add((r.get("component") or "").strip().lower(), r.get("device"), r.get("device"), None)
    return {k: list((with_device.get(k) or plain.get(k) or {}).values()) for k in kinds}


class SurveyView:
    """The approved survey, and the map, as block 17 reads them in a page run (section 9.2)."""

    HELD = ("local", "openbridge", "shared_gap", "module", "library")

    def __init__(self, survey: dict, omap: dict | None) -> None:
        self.survey = survey
        self.local_max = int(survey.get("local_max") or 1)
        self.kinds = {k["kind"]: k for k in survey.get("kinds") or [] if k.get("placement") in self.HELD}
        self.local = [e for e in survey.get("local") or []]
        self.rows = [r for r in (omap or {}).get("rows") or [] if isinstance(r, dict)]

    def mapped(self, kind: str) -> dict | None:
        return next((r for r in self.rows if r.get("kind") == kind and not r.get("feature")
                     and r.get("state") in PLACING_STATES), None)

    def match(self, kind: str, instances: list[dict]) -> tuple[list, list]:
        """`(matched, unmatched)`: the design's instances that have a survey-local entry, as `(instance, entry)` and
        `instance`, both in the order of `instances`. An instance matches the entry of the same stem (compared
        case-insensitively). Each stemless entry of the kind then absorbs one instance that matches no stemmed entry,
        in the order of `instances` (NOTE-WFB-10 section 9.2 item 3)."""
        own = [e for e in self.local if e.get("kind") == kind and not e.get("feature")]
        entries = {fold(e.get("stem")): e for e in own if e.get("stem")}
        free = [e for e in own if not e.get("stem")]
        taken: set = set()
        found: dict[int, dict] = {}
        for n, i in enumerate(instances):
            key = fold(i["stem"]) if i["stem"] else None
            if key and key in entries and key not in taken:
                taken.add(key)
                found[n] = entries[key]
        for n, i in enumerate(instances):
            if n not in found and free:
                found[n] = free.pop(0)
        matched = [(i, found[n]) for n, i in enumerate(instances) if n in found]
        unmatched = [i for n, i in enumerate(instances) if n not in found]
        return matched, unmatched


def late_entry(kind, rule, status, reason, instances) -> dict:
    return {"kind": kind, "feature": None, "id": f"GAP-{kind}", "rule": rule, "status": status, "reason": reason,
            "count": len(instances), "stems": sorted({i["stem"] for i in instances if i["stem"]}, key=fold)}


def late_local(kind, instances, source) -> list[dict]:
    return [{"kind": kind, "feature": None, "instance": i["stem"] or i["key"], "page": i["page"], "source": source}
            for i in instances]


def place_with_survey(kind: str, instances: list[dict], view: SurveyView) -> dict:
    """The page run's placement of a kind the library at this commit does not draw (section 9.2 items 2 and 4):
    `{resolution, placement, reason, late, local, row}`."""
    held = view.kinds.get(kind)
    if held and held["placement"] == "local":
        matched, unmatched = view.match(kind, instances)
        local = [{"kind": kind, "feature": None, "instance": e.get("stem") or i["stem"] or i["key"],
                  "page": e.get("page"), "source": "survey"} for i, e in matched]
        out = {"resolution": "local", "placement": "local", "late": None, "row": None,
               "reason": "the approved survey places the kind local: one assembly per instance"}
        if unmatched:
            out["late"] = late_entry(kind, "second", "accepted",
                                     f"the design draws {len(unmatched)} instance(s) of a kind the survey placed "
                                     "local that match no survey instance: drawn as local assemblies in this run, "
                                     "queued for the next survey", unmatched)
            local += late_local(kind, unmatched, "late")
        out["local"] = local
        return out
    if held:
        return {"resolution": "unbuilt", "placement": held["placement"], "late": None, "row": None, "local": [],
                "reason": f"the approved survey places the kind {held['placement']}; the project release has not "
                          "built it"}
    row = view.mapped(kind)
    if row is not None:
        late = late_entry(kind, "map", "accepted",
                          f"the survey does not hold the kind and the map has a {row.get('state')} row for it "
                          f"({row.get('element')}): drawn as a local assembly in this run, a wrap with the next "
                          "release", instances)
    elif len(instances) > view.local_max:
        late = late_entry(kind, "twice", "accepted",
                          f"the survey does not hold the kind and the design draws {len(instances)} instances, more "
                          f"than {view.local_max}: drawn as a local assembly in this run, a shared gap with the next "
                          "release", instances)
    else:
        late = late_entry(kind, "once", "local",
                          f"the survey does not hold the kind and the design draws {len(instances)} instance(s), "
                          f"{view.local_max} or fewer: a local assembly", instances)
    return {"resolution": "local", "placement": "local", "late": late, "local": late_local(kind, instances, "late"),
            "row": row, "reason": "a late kind: " + late["reason"]}


def analyse(model: dict, designs: list[dict], catalogue: dict, profile: dict, module: dict, module_first: bool,
            accepted: dict[str, str], design: dict | None = None, schema: dict | None = None,
            view: SurveyView | None = None) -> dict:
    mapping = {r["uid"]: r for r in model["mapping"]}
    used: dict[str, dict] = {}
    found, feature_gaps = (features(design, catalogue, schema or {}, used, accepted,
                                    None if view is None else set(view.kinds))
                           if design else ([], []))
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
    instances = design_instances(model, designs, design, set(used)) if view is not None else {}
    kinds, gaps, late, local = [], [], [], []
    for kind in sorted(used):
        u = used[kind]
        view_name = KIND_VIEW.get(kind)
        in_library = kind in profile["kinds"] and view_name in catalogue
        part = part_name(kind) if part_name(kind) in module else None
        if not in_library and view is not None:
            placed = place_with_survey(kind, instances.get(kind, []), view)
            kinds.append({"kind": kind, "count": u["count"], "pages": u["pages"], "resolution": placed["resolution"],
                          "part": None, "placement": placed["placement"],
                          "audit": {"module_part": part, "library_part": None, "choice": placed["resolution"],
                                    "reason": placed["reason"]}})
            local += placed["local"]
            if placed["late"]:
                late.append(placed["late"])
                if placed["late"]["status"] == "accepted":
                    row = placed.get("row")
                    gaps.append({"id": placed["late"]["id"], "kind": kind, "item": u["items"][0],
                                 "library_today": "no symbol of this kind in the library at this commit",
                                 "needed": f"a local assembly of {kind} in this run; the next release builds it",
                                 "status": "accepted", "reason": placed["late"]["reason"],
                                 "mapping_rows": u["items"], "placement": "local",
                                 "element": row.get("element") if row else None,
                                 "map_row": {"element": row.get("element"), "state": row.get("state")} if row else None,
                                 "count": placed["late"]["count"]})
            continue
        if not in_library:
            choice, resolution = "gap", "gap"
            reason = ("the library has no symbol of this kind: the generator draws a counted gap box" if
                      kind not in profile["kinds"] else f"the catalogue holds no view {view_name} for the kind")
        elif part and module_first:
            choice, resolution = "module", "module"
            reason = f"OpenBridge first: the module draws the kind with {part}"
        elif part:
            choice, resolution = "library", "library"
            reason = f"the library's view is chosen; the module's {part} is not preferred (module-first is off)"
        else:
            choice, resolution = "library", "library"
            reason = "the module has no part for this kind; the library draws it"
        entry = {"kind": kind, "count": u["count"], "pages": u["pages"], "resolution": resolution,
                 "part": part if resolution == "module" else view_name if in_library else None,
                 "audit": {"module_part": part, "library_part": view_name if in_library else None,
                           "choice": choice, "reason": reason}}
        if view is not None:
            entry["placement"] = resolution
        kinds.append(entry)
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
    if view is None:
        gaps += feature_gaps
        open_count = sum(1 for g in gaps if g["status"] in ("open", "partial"))
        return {"schema": "cadre-hmi-library-gaps/1", "kinds": kinds, "gaps": gaps, "open_count": open_count,
                "features": found}
    for g in feature_gaps:   # section 9.2 item 5: a late feature is accepted and drawn with basic parts
        if g["status"] == "open":
            g["status"] = "accepted"
            g["reason"] = ("a late feature: drawn in this run with basic parts in a group beside its symbol, "
                           "declared at the review and queued for the next survey")
        g.update({"placement": "local", "element": None, "map_row": None, "count": len(g["mapping_rows"])})
        late.append({"kind": g["kind"], "feature": g["id"][len("GAP-"):], "id": g["id"], "rule": "feature",
                     "status": "accepted", "reason": g["reason"], "count": len(g["mapping_rows"]), "stems": []})
    gaps += feature_gaps
    resolved = {k["kind"] for k in kinds if k["resolution"] in ("module", "library")}
    # survey-local entries of a feature, and the wraps the project release built, for the kinds this run draws
    for e in view.local:
        if e.get("feature") and e["kind"] in instances:
            stems = {fold(i["stem"]) for i in instances[e["kind"]] if i["stem"]}
            if e.get("stem") is None or fold(e["stem"]) in stems:
                local.append({"kind": e["kind"], "feature": e["feature"], "instance": e.get("stem"),
                              "page": e.get("page"), "source": "survey"})
    wraps = [{"kind": w["kind"], "feature": w.get("feature"), "element": w["element"]}
             for w in view.survey.get("wraps") or []
             if (w["kind"] in resolved if not w.get("feature") else w["kind"] in used)]
    local.sort(key=lambda e: (fold(e["kind"]), fold(e["feature"]), fold(e["instance"]), fold(e["page"]), e["source"]))
    late.sort(key=lambda e: (fold(e["kind"]), fold(e["feature"]), e["id"]))
    wraps.sort(key=lambda w: (fold(w["kind"]), fold(w["feature"])))
    return {"schema": GAPS_SCHEMA, "kinds": kinds, "gaps": gaps, "open_count": 0, "features": found,
            "local": local, "late": late, "wraps": wraps}


def main(argv: list[str] | None = None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    ap.add_argument("--model", default=None)
    ap.add_argument("--designs", default=None, metavar="LIST")
    ap.add_argument("--design", default=None, help="the project design (wfb.migration.project_design/1)")
    ap.add_argument("--descriptor-schema", default=None, help="schemas/screen-descriptor.schema.json, with --design")
    ap.add_argument("--catalogue", default=None)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--module", default=None)
    ap.add_argument("--module-first", action="store_true")
    ap.add_argument("--accepted", default=None)
    ap.add_argument("--parent", default=None, help="the parent project the profile must name (`library`); not checked "
                                                   "without it")
    ap.add_argument("--project-survey", default=None, help="page mode: the approved project survey")
    ap.add_argument("--openbridge-map", default=None, help="the OpenBridge map (module/openbridge-map.json)")
    ap.add_argument("--survey", default=None, help="survey mode: the ctig survey (ctig.survey/1)")
    ap.add_argument("--release", default=None, help="release mode: the project survey")
    ap.add_argument("--elements", default=None, help="module/openbridge-elements.json: required in survey mode; in release and page mode it lets a map row be checked against the list")
    ap.add_argument("--local-max", type=int, default=1, help="survey mode: the most instances placed local (1 to 10)")
    ap.add_argument("--prior-local", action="append", default=None, help="survey mode: an earlier survey.json")
    ap.add_argument("--late", action="append", default=None, help="survey mode: a page run's gaps.json")
    ap.add_argument("--proposals", default=None, help='survey mode: {"proposals": [...]}')
    ap.add_argument("--changes", default=None, help='survey mode: {"changes": [...]}; given, the survey is final')
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args_line = sys.argv[1:] if argv is None else list(argv)
    try:
        if a.survey and a.release:
            raise InputFault("give --survey or --release, not both")
        if a.survey or a.release:
            if a.project_survey or a.model or a.designs or a.design:
                raise InputFault("--survey and --release take no page-mode input (--model, --designs, --design, "
                                 "--project-survey)")
            return (run_survey if a.survey else run_release)(a, clock, args_line)
        for flag, value in (("--model", a.model), ("--catalogue", a.catalogue), ("--profile", a.profile),
                            ("--module", a.module)):
            if not value:
                raise InputFault(f"page mode needs {flag}")
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
        survey = load(a.project_survey, "project survey") if a.project_survey else None
        omap = load(a.openbridge_map, "OpenBridge map") if a.openbridge_map else None
        if omap is not None:
            check_map_rows(omap, element_tags(load(a.elements, "OpenBridge elements")) if a.elements else None,
                           a.openbridge_map)
        if survey is not None and (not isinstance(survey, dict) or survey.get("schema") != SURVEY_SCHEMA):
            raise InputFault(f"project survey: {a.project_survey}: not a {SURVEY_SCHEMA} document")
        if survey is not None and omap is None:
            raise InputFault("--project-survey needs --openbridge-map: the map's reviewed rows make the late rule "
                             "`map`, and a run without it would apply no row")
        if a.parent and profile.get("library") != a.parent:
            raise InputFault(f"--profile names the parent {profile.get('library')!r}, not {a.parent!r}")
    except (InputFault, OSError) as e:
        print(f"library_gaps: {e}")
        return 1
    doc = analyse(model, designs, catalogue, profile, module, a.module_first, accepted, design, schema,
                  SurveyView(survey, omap) if survey is not None else None)
    given = [a.designs, a.design, a.descriptor_schema, a.accepted, a.project_survey, a.openbridge_map]
    if survey is not None:
        doc["survey"] = {"sha256": provenance.sha256_of(Path(a.project_survey)),
                         "library_commit": survey.get("library_commit")}
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
    if survey is not None:
        unbuilt = [k["kind"] for k in doc["kinds"] if k["resolution"] == "unbuilt"]
        if unbuilt:
            print("library_gaps: unbuilt (the project release has not built them): " + ", ".join(unbuilt))
        return 3 if unbuilt else 0
    return 2 if doc["open_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
