"""The survey and release modes of the library's placement tool (NOTE-WFB-10 sections 7.5 to 7.8, 8.2, 10.2 and 11.4).

`library_gaps.py --survey <ctig survey>` places every kind and feature of a ctig survey (`ctig.survey/1`) by Table 7.5
and writes the project survey (`cadre-hmi-project-survey/1`), the unmapped items and the proposal source.
`library_gaps.py --release <survey.json>` turns an approved survey into the gap list of the project release
(`cadre-hmi-library-gaps/2`). Both are deterministic and offline: no model, no gateway, no client name beyond the
stems the ctig survey itself holds. The approval record is not written here: the manager's block writes it (section
7.8), and the hashes are compared there (sections 8.2 and 9.2).

Placement (Table 7.5), the first row that applies: 1 the library (module part or library view) draws the kind or
feature; 2 a map row in state `reviewed` or `approved` (an accepted proposal makes the state `approved`); 3 and 5 more
than `local_max` instances is a shared gap; 4 and 6 `local_max` instances or fewer is local; 7 an unnamed feature, an
unclassified template and a kind with no instance are `unclassified` (a feature of a kind with no resolution travels
with its kind: placement null). `prior_local` and the owner's changes override the table.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import provenance  # noqa: E402
    from hmi.asm_model import InputFault, load  # noqa: E402
    from hmi.screen import KIND_VIEW  # noqa: E402
else:
    from . import provenance
    from .asm_model import InputFault, load
    from .screen import KIND_VIEW

SURVEY_SCHEMA = "cadre-hmi-project-survey/1"
GAPS_SCHEMA = "cadre-hmi-library-gaps/2"
CTIG_SCHEMA = "ctig.survey/1"
KIND_NAME = re.compile(r"^[a-z][a-z0-9-]*$")
PLACING_STATES = ("reviewed", "approved")
LIBRARY_PLACEMENTS = ("module", "library")


def part_name(kind: str) -> str:
    return "cadre.ob." + kind.replace("-", "")


def fold(text) -> str:
    return (text or "").casefold()


def gap_id(kind: str, feature: str | None) -> str:
    """`GAP-<kind>` for a kind, `GAP-<kind>-<feature>` with each `:` of the feature replaced by `-` (section 8.2)."""
    return f"GAP-{kind}" if not feature else f"GAP-{kind}-{feature.replace(':', '-')}"


def row_name(r: dict) -> str:
    feature = r.get("feature")
    return f"{r.get('kind')}" + (f" / {feature}" if feature else "")


def check_map_rows(omap, tags: set | None, path="") -> None:
    """Section 11.4 item 1: a map row of state `reviewed` or `approved` names an element, and (where the elements list
    is given as `tags`) an element of that list. Such a row places `openbridge`, so a row that fails is an input fault
    naming the row and the run places nothing (T3, T15)."""
    for r in (omap.get("rows") if isinstance(omap, dict) else None) or []:
        if not isinstance(r, dict) or r.get("state") not in PLACING_STATES:
            continue
        element = r.get("element")
        where = f"element map{': ' + str(path) if path else ''}: row {row_name(r)} ({r.get('state')})"
        if not isinstance(element, str) or not element:
            raise InputFault(f"{where}: no element; a {r.get('state')} row names a tag of openbridge-elements.json")
        if tags is not None and element not in tags:
            raise InputFault(f"{where}: element {element!r} is not a tag of openbridge-elements.json")


def element_tags(elements) -> set:
    return {e.get("tag") for e in (elements.get("elements") if isinstance(elements, dict) else None) or []}


def check_schema_of(docs: list, paths: list, want: str, what: str) -> None:
    """Section 11.4 item 3: a `--prior-local` or `--late` file carries the schema it is read as. A file that names
    another schema is refused, as is a file that is neither an object nor a list."""
    for doc, path in zip(docs, paths):
        if isinstance(doc, dict):
            if "schema" in doc and doc["schema"] != want:
                raise InputFault(f"{what}: {path}: schema {doc['schema']!r}, not {want}")
        elif not isinstance(doc, list):
            raise InputFault(f"{what}: {path}: not a {want} document")


def read_list(path, key: str) -> list:
    """The list in a `--proposals` or `--changes` file: `{key: [...]}` (a bare list is taken too)."""
    doc = load(path, key)
    items = doc.get(key) if isinstance(doc, dict) else doc
    if not isinstance(items, list):
        raise InputFault(f"{key}: {path}: no list `{key}`")
    return [x for x in items]


# ----------------------------------------------------------------------------------------------------------------
# The items of a survey: kinds and their features.

class Item:
    """A kind (`feature` None) or one feature of a kind."""

    def __init__(self, kind: str, feature: str | None) -> None:
        self.kind, self.feature = kind, feature
        self.count = 0
        self.instances: list[tuple[str | None, str | None]] = []   # (stem, first operator page)
        self.placement: str | None = None
        self.source = "table"
        self.library: str | None = None       # `module` or `library` when the library draws it
        self.resolution: str | None = None
        self.map_row: dict | None = None      # {element, state}
        self.unmapped = False

    @property
    def key(self) -> tuple:
        return (self.kind, self.feature)

    def sort_key(self) -> tuple:
        return (fold(self.kind), fold(self.feature))


class Kind(Item):
    def __init__(self, name: str) -> None:
        super().__init__(name, None)
        self.stemless = 0
        self.faceplate_only = 0
        self.pages = 0
        self.features: dict[str, Item] = {}

    def feature_item(self, feature: str) -> Item:
        if feature not in self.features:
            self.features[feature] = Item(self.kind, feature)
        return self.features[feature]


def first_page(pages, operator: set) -> str | None:
    ordered = sorted(pages or [], key=fold)
    for p in ordered:
        if p in operator:
            return p
    return ordered[0] if ordered else None


def read_ctig(path) -> tuple[dict, str]:
    doc = load(path, "ctig survey")
    if not isinstance(doc, dict) or doc.get("schema") != CTIG_SCHEMA or not isinstance(doc.get("kinds"), list):
        raise InputFault(f"ctig survey: {path}: not a {CTIG_SCHEMA} document")
    for row in doc["kinds"]:
        if not isinstance(row, dict) or not KIND_NAME.match(str(row.get("kind", ""))):
            raise InputFault(f"ctig survey: {path}: a kind name that is not lower case with hyphens: {row!r}")
    return doc, provenance.sha256_of(Path(path))


def census_kinds(ctig: dict) -> dict[str, Kind]:
    operator = {p["page"] for p in ctig.get("page_class") or [] if p.get("class") == "operator"}
    kinds: dict[str, Kind] = {}
    for row in ctig["kinds"]:
        k = kinds.setdefault(row["kind"], Kind(row["kind"]))
        k.count += int(row.get("instances") or 0)
        k.stemless += int(row.get("stemless") or 0)
        k.faceplate_only += int(row.get("faceplate_only") or 0)
        k.pages += int(row.get("pages_operator") or 0)
        for d in row.get("devices") or []:
            instance = (d.get("stem"), first_page(d.get("pages"), operator))
            k.instances.append(instance)
            features = {"member:" + m for m in (d.get("members") or []) + (d.get("unknown_members") or [])}
            features |= {"unnamed:" + u for u in d.get("unnamed") or []}
            if d.get("popups"):
                features.add("faceplate")
            for f in features:
                item = k.feature_item(f)
                item.instances.append(instance)
                item.count += 1
    return kinds


def read_late(docs: list, kinds: dict[str, Kind]) -> list[dict]:
    """Add the late rows of the `late` files (section 7.5 key 5) to the kinds; return the design features (rule
    `feature`: a descriptor element, a view, a faceplate tab, a key) that no Table 7.5 row can place."""
    unplaced: list[dict] = []
    for doc in docs:
        entries = doc.get("late") if isinstance(doc, dict) else doc
        for e in entries or []:
            kind = str(e.get("kind") or "").lower()
            feature = e.get("feature")
            if not kind:
                continue
            count = int(e.get("count") or 0)
            stems = [s for s in e.get("stems") or []]
            instances = [(s, None) for s in stems] + [(None, None)] * max(0, count - len(stems))
            if feature is not None and not (feature.startswith(("member:", "unnamed:")) or feature == "faceplate"):
                unplaced.append({"kind": kind, "feature": feature, "count": count})
                continue
            k = kinds.setdefault(kind, Kind(kind))
            if feature is None:
                k.count += count
                k.instances.extend(instances)
            else:
                item = k.feature_item(feature)
                item.count += count
                item.instances.extend(instances)
    return unplaced


# ----------------------------------------------------------------------------------------------------------------
# Resolution and placement.

class Rules:
    """The library, the module and the map, as Table 7.5 reads them."""

    def __init__(self, catalogue: dict, profile: dict, module: dict, omap: dict, module_first: bool,
                 local_max: int) -> None:
        self.catalogue, self.profile, self.module = catalogue, profile, module
        self.rows = [r for r in omap.get("rows") or [] if isinstance(r, dict)]
        self.module_first, self.local_max = module_first, local_max

    def library_of(self, kind: str) -> tuple[str | None, str | None]:
        """`(placement, resolution)` of a kind the library draws (key 1); `(None, None)` otherwise."""
        view = KIND_VIEW.get(kind)
        if kind not in (self.profile.get("kinds") or {}) or view not in self.catalogue:
            return None, None
        part = part_name(kind)
        if self.module_first and part in self.module:
            return "module", part
        return "library", view

    def feature_resolution(self, kind: str, feature: str) -> str | None:
        """Key 2: a member the profile's device kind lists; the faceplate the profile gives the kind."""
        device_kind = (self.profile.get("deviceKinds") or {}).get(kind) or {}
        if feature.startswith("member:"):
            name = feature[len("member:"):]
            return name if name in (device_kind.get("members") or {}) else None
        if feature == "faceplate":
            for source in (device_kind, (self.profile.get("kinds") or {}).get(kind) or {}):
                view = source.get("faceplate") or next(iter((source.get("faceplates") or {}).values()), None)
                if view:
                    return view
        return None

    def rows_of(self, kind: str, feature: str | None) -> list[dict]:
        return [r for r in self.rows if r.get("kind") == kind and (r.get("feature") or None) == feature]

    def placing_row(self, kind: str, feature: str | None) -> dict | None:
        return next((r for r in self.rows_of(kind, feature) if r.get("state") in PLACING_STATES), None)


def resolve(kinds: dict[str, Kind], rules: Rules) -> None:
    """The library resolution and the map row of every item, and whether it is unmapped (no resolution, no row)."""
    for k in kinds.values():
        k.library, k.resolution = rules.library_of(k.kind)
        if k.library is None and k.count > 0:
            k.unmapped = not rules.rows_of(k.kind, None)
        for f in k.features.values():
            if f.feature.startswith("unnamed:"):
                continue
            if k.library is None:
                continue  # a feature of a kind with no resolution travels with its kind
            f.resolution = rules.feature_resolution(k.kind, f.feature)
            f.library = k.library if f.resolution else None
            f.unmapped = f.resolution is None and not rules.rows_of(k.kind, f.feature) and f.count > 0


def table_placement(item: Item, kind: Kind, rules: Rules, row: dict | None) -> None:
    """Set `placement`, `source`, `map_row` and `resolution` of one item by Table 7.5 (the owner's changes and the
    prior surveys come after)."""
    item.source, item.map_row = "table", None
    if item.feature is None:
        if item.library:
            item.placement = item.library
            return
        item.resolution = None
        if item.count == 0:
            item.placement = "unclassified"
            return
    else:
        if item.feature.startswith("unnamed:") or item.count == 0:
            item.placement, item.resolution = "unclassified", None
            return
        if kind.library is None:
            item.placement, item.resolution = None, None   # travels with its kind
            return
        if item.library:
            item.placement = item.library
            return
    if row is not None:
        item.placement, item.resolution = "openbridge", row.get("element")
        item.map_row = {"element": row.get("element"), "state": row.get("state")}
    else:
        item.placement = "shared_gap" if item.count > rules.local_max else "local"
        item.resolution = None


def prior_local_keys(docs: list) -> set[tuple]:
    """The kinds and features that earlier surveys placed local (key 4)."""
    keys: set[tuple] = set()
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        for k in doc.get("kinds") or []:
            if k.get("placement") == "local":
                keys.add((k.get("kind"), None))
            for f in k.get("features") or []:
                if f.get("placement") == "local":
                    keys.add((k.get("kind"), f.get("feature")))
        for e in doc.get("local") or []:
            keys.add((e.get("kind"), e.get("feature") or None))
    return keys


# ----------------------------------------------------------------------------------------------------------------
# Proposals (section 7.7) and changes (section 7.8).

def all_items(kinds: dict[str, Kind]):
    for k in sorted(kinds.values(), key=lambda x: fold(x.kind)):
        yield k
        for f in sorted(k.features.values(), key=lambda x: fold(x.feature)):
            yield f


def unmapped_rows(kinds: dict[str, Kind]) -> list[dict]:
    out = []
    for item in all_items(kinds):
        if not item.unmapped:
            continue
        if item.feature is None:
            members = sorted(f.feature[len("member:"):] for f in item_features(kinds, item)
                             if f.feature.startswith("member:"))
            unnamed = sorted(f.feature[len("unnamed:"):] for f in item_features(kinds, item)
                             if f.feature.startswith("unnamed:"))
        else:
            members = [item.feature[len("member:"):]] if item.feature.startswith("member:") else []
            unnamed = []
        out.append({"kind": item.kind, "feature": item.feature, "count": item.count, "members": members,
                    "unnamed": unnamed})
    return out


def item_features(kinds: dict[str, Kind], item: Item):
    return kinds[item.kind].features.values() if item.feature is None else []


def element_rows(elements: dict) -> list[dict]:
    out = []
    for e in elements.get("elements") or []:
        out.append({"tag": e.get("tag"), "path": e.get("path"), "group": e.get("group"),
                    "properties": [{"name": p.get("name"), "type": p.get("type"), "enum": p.get("enum"),
                                    "default": p.get("default")} for p in e.get("properties") or []]})
    return out


def judge_proposals(model_proposals: list, rules: Rules, kinds: dict[str, Kind], tags: set) -> list[dict]:
    """The proposals of the model and the `proposed` rows of the map, each with a verdict `pending` or `dropped` (a
    dropped proposal's `why`); the owner's acceptance comes later."""
    unmapped = {(u["kind"], u["feature"]) for u in unmapped_rows(kinds)}
    out: list[dict] = []
    seen: set[tuple] = set()
    for p in model_proposals:
        if not isinstance(p, dict):
            continue
        key = (str(p.get("kind") or ""), p.get("feature") or None)
        entry = {"kind": key[0], "feature": key[1], "element": p.get("element"),
                 "properties": p.get("properties") if p.get("properties") is not None else {},
                 "states": p.get("states") if p.get("states") is not None else [],
                 "reason": p.get("reason") or "", "source": "model", "verdict": "pending", "why": None}
        why = None
        if key not in unmapped:
            why = "the kind or feature is not unmapped: the library or a map row already resolves it, or the survey lacks it"
        elif key in seen:
            why = "an earlier proposal names the same item"
        elif entry["element"] is None:
            why = "the model named no element: nothing is placed"
        elif entry["element"] not in tags:
            why = "the element is not in the pinned release's elements list"
        if why:
            entry["verdict"], entry["why"] = "dropped", why
        else:
            seen.add(key)
        out.append(entry)
    for r in rules.rows:
        if r.get("state") != "proposed":
            continue
        key = (r.get("kind"), r.get("feature") or None)
        k = kinds.get(key[0])
        if k is None:
            continue
        if key[1] is None:
            if k.library is not None or k.count == 0:
                continue
        else:
            f = k.features.get(key[1])
            if f is None or k.library is None or f.resolution:
                continue
        if rules.placing_row(*key) or any(x["source"] == "map" and (x["kind"], x["feature"]) == key for x in out):
            continue
        out.append({"kind": key[0], "feature": key[1], "element": r.get("element"),
                    "properties": r.get("properties") if r.get("properties") is not None else {},
                    "states": r.get("states") if r.get("states") is not None else [],
                    "reason": r.get("reason") or "", "source": "map", "verdict": "pending", "why": None})
    out.sort(key=lambda x: (fold(x["kind"]), fold(x["feature"]), x["source"]))
    return out


def check_change(change, index: int) -> tuple[tuple | None, str | None]:
    """`(key, refusal)` of the shape of one change."""
    if not isinstance(change, dict):
        return None, "not an object"
    if change.get("action") not in ("reject_proposal", "to_local", "to_shared_gap"):
        return None, f"unknown action {change.get('action')!r}"
    if not str(change.get("reason") or "").strip():
        return None, "the reason is empty"
    if not str(change.get("kind") or ""):
        return None, "the change names no kind"
    return (change["kind"], change.get("feature") or None), None


def find_item(kinds: dict[str, Kind], key: tuple) -> Item | None:
    k = kinds.get(key[0])
    if k is None:
        return None
    return k if key[1] is None else k.features.get(key[1])


def apply_changes(changes: list, proposals: list[dict], kinds: dict[str, Kind]):
    """Phase 1: the `reject_proposal` changes (before the placement). Returns `(results, rejected_keys)`; `results` is
    a list parallel to `changes` of `None` (to be applied later), `"applied"` or the refusal text."""
    results: list = [None] * len(changes)
    rejected: set[tuple] = set()
    for i, c in enumerate(changes):
        key, bad = check_change(c, i)
        if bad:
            results[i] = bad
            continue
        if c["action"] != "reject_proposal":
            continue
        valid = [p for p in proposals if (p["kind"], p["feature"]) == key and p["verdict"] == "pending"]
        if key in rejected:
            results[i] = "the proposal is already rejected"
        elif not valid:
            results[i] = "no proposal names this item"
        else:
            rejected.add(key)
            results[i] = "applied"
    return results, rejected


def build_survey(ctig: dict, ctig_sha: str, rules: Rules, omap: dict, elements: dict, prior_docs: list,
                 late_docs: list, model_proposals: list, changes: list | None, library_commit: str | None) -> tuple:
    kinds = census_kinds(ctig)
    late_features = read_late(late_docs, kinds)
    resolve(kinds, rules)
    tags = {e.get("tag") for e in elements.get("elements") or []}
    proposals = judge_proposals(model_proposals, rules, kinds, tags)
    final = changes is not None
    results, rejected = apply_changes(changes or [], proposals, kinds)

    accepted: dict[tuple, dict] = {}
    for p in proposals:
        if p["verdict"] != "pending":
            continue
        key = (p["kind"], p["feature"])
        if not final:
            continue
        if key in rejected:
            p["verdict"] = "rejected"
            p["why"] = "rejected by the owner"
        else:
            p["verdict"] = "accepted"
            if p["element"] is not None:
                accepted[key] = {"element": p["element"], "state": "approved"}

    prior = prior_local_keys(prior_docs)
    for k in kinds.values():
        for item in [k, *k.features.values()]:
            row = rules.placing_row(*item.key)
            if row is None:
                row = accepted.get(item.key)
            table_placement(item, k, rules, row)
            if item.placement == "local" and item.key in prior:
                item.placement, item.source = "shared_gap", "prior_local"

    refused_at: dict[int, str] = {}
    for i, c in enumerate(changes or []):
        if results[i] is not None:
            continue
        key = (c["kind"], c.get("feature") or None)
        item = find_item(kinds, key)
        target = "local" if c["action"] == "to_local" else "shared_gap"
        if item is None:
            results[i] = "no such kind" if key[0] not in kinds else "the kind has no such feature"
        elif item.placement not in ("local", "shared_gap"):
            results[i] = (f"the item is placed {item.placement}: only a shared_gap or local item can change"
                          if item.placement else "the item travels with its kind and has no placement")
        elif item.placement == target:
            results[i] = f"the item is already placed {target}"
        else:
            item.placement, item.source = target, "change"
            results[i] = "applied"
    applied = [c for c, r in zip(changes or [], results) if r == "applied"]
    refused = [{**c, "why": r} if isinstance(c, dict) else {"change": c, "why": r}
               for c, r in zip(changes or [], results) if r != "applied"]

    survey = assemble(kinds, ctig, ctig_sha, rules, proposals, late_features, library_commit, elements,
                      None if not final else {"changes": applied, "refused": refused})
    unmapped = unmapped_rows(kinds)
    source = {"unmapped": unmapped, "elements": element_rows(elements)}
    return survey, unmapped, source


def local_entries(item: Item) -> list[dict]:
    instances = list(item.instances) + [(None, None)] * max(0, item.count - len(item.instances))
    return [{"kind": item.kind, "feature": item.feature, "stem": s, "page": p} for s, p in instances]


def assemble(kinds: dict[str, Kind], ctig: dict, ctig_sha: str, rules: Rules, proposals: list[dict],
             late_features: list[dict], library_commit: str | None, elements: dict, approval: dict | None) -> dict:
    kind_rows, wraps, shared, local = [], [], [], []
    unclassified_features = []
    for k in sorted(kinds.values(), key=lambda x: fold(x.kind)):
        features = []
        for f in sorted(k.features.values(), key=lambda x: fold(x.feature)):
            features.append({"feature": f.feature, "count": f.count, "placement": f.placement,
                             "placement_source": f.source, "resolution": f.resolution})
            if f.feature.startswith("unnamed:"):
                unclassified_features.append({"kind": k.kind, "feature": f.feature, "count": f.count})
            _collect(f, wraps, shared, local)
        _collect(k, wraps, shared, local)
        kind_rows.append({"kind": k.kind, "count": k.count, "stemless": k.stemless,
                          "faceplate_only": k.faceplate_only, "pages": k.pages, "library_resolution": k.library,
                          "map_row": k.map_row, "placement": k.placement, "placement_source": k.source,
                          "resolution": k.resolution, "features": features})
    for u in late_features:
        unclassified_features.append(u)
    unclassified_features.sort(key=lambda x: (fold(x["kind"]), fold(x["feature"])))
    wraps.sort(key=lambda x: (fold(x["kind"]), fold(x["feature"])))
    shared.sort(key=lambda x: (fold(x["kind"]), fold(x["feature"])))
    local.sort(key=lambda x: (fold(x["kind"]), fold(x["feature"]), fold(x["stem"]), fold(x["page"])))
    objects = (ctig.get("totals") or {}).get("unclassified_objects")
    unclassified = unclassified_rows(ctig.get("unclassified") or {})
    if objects is None:
        objects = sum(u["instances"] for u in unclassified if u["kind"] != "stem_not_recovered")
    return {
        "schema": SURVEY_SCHEMA, "library_commit": library_commit,
        "openbridge_release": {"version": elements.get("release"), "commit": elements.get("commit")},
        "ctig_survey_sha256": ctig_sha, "local_max": rules.local_max, "pages": ctig.get("pages") or {},
        "kinds": kind_rows, "wraps": wraps, "shared_gaps": shared, "local": local, "unclassified": unclassified,
        "unclassified_features": unclassified_features, "proposals": proposals, "approval": approval,
        "totals": {"kinds": sum(1 for k in kinds.values() if k.count > 0), "instances": sum(k.count for k in kinds.values()),
                   "wraps": len(wraps), "shared_gaps": len(shared), "local": len(local),
                   "unclassified_objects": objects}}


def _collect(item: Item, wraps: list, shared: list, local: list) -> None:
    if item.placement == "openbridge" and item.map_row:
        wraps.append({"kind": item.kind, "feature": item.feature, "element": item.map_row["element"],
                      "state": item.map_row["state"]})
    elif item.placement == "shared_gap":
        stems = sorted({s for s, _ in item.instances if s}, key=lambda s: (fold(s), s))
        shared.append({"id": gap_id(item.kind, item.feature), "kind": item.kind, "feature": item.feature,
                       "count": item.count, "stems": stems})
    elif item.placement == "local":
        local.extend(local_entries(item))


def unclassified_rows(u: dict) -> list[dict]:
    rows = [{"kind": "template", "template": t.get("template"), "instances": t.get("instances"), "pages": t.get("pages")}
            for t in u.get("unclassed_templates") or []]
    rows += [{"kind": "static", "template": t.get("template"), "instances": t.get("instances"),
              "pages": t.get("pages")} for t in u.get("static_templates") or []]
    if u.get("no_kind_devices"):
        rows.append({"kind": "no_kind", "template": None, "instances": u["no_kind_devices"], "pages": None})
    if u.get("stems_not_recovered"):
        rows.append({"kind": "stem_not_recovered", "template": None, "instances": u["stems_not_recovered"],
                     "pages": None})
    rows.sort(key=lambda r: (fold(r["kind"]), fold(r["template"])))
    return rows


# ----------------------------------------------------------------------------------------------------------------
# The commands.

def run_survey(a, clock: provenance.Clock, args_line: list[str]) -> int:
    for flag, value in (("--catalogue", a.catalogue), ("--profile", a.profile), ("--module", a.module),
                        ("--openbridge-map", a.openbridge_map), ("--elements", a.elements)):
        if not value:
            raise InputFault(f"--survey needs {flag}")
    if not 1 <= a.local_max <= 10:
        raise InputFault("--local-max is an integer from 1 to 10")
    differing = provenance.differing_from_head([a.openbridge_map, a.elements, a.profile])
    if differing:
        raise InputFault("the working tree differs from its HEAD in " + ", ".join(differing) + ": the survey records "
                         "library_commit as the tree's state, so commit or restore these files first")
    ctig, ctig_sha = read_ctig(a.survey)
    omap, elements = load(a.openbridge_map, "element map"), load(a.elements, "elements list")
    check_map_rows(omap, element_tags(elements), a.openbridge_map)
    rules = Rules(load(a.catalogue, "catalogue"), load(a.profile, "profile"), load(a.module, "module components"),
                  omap, a.module_first, a.local_max)
    prior = [load(p, "prior-local survey") for p in a.prior_local or []]
    check_schema_of(prior, a.prior_local or [], SURVEY_SCHEMA, "prior-local survey")
    late = [load(p, "late gaps") for p in a.late or []]
    check_schema_of(late, a.late or [], GAPS_SCHEMA, "late gaps")
    proposals = read_list(a.proposals, "proposals") if a.proposals else []
    changes = read_list(a.changes, "changes") if a.changes is not None else None
    survey, unmapped, source = build_survey(ctig, ctig_sha, rules, omap, elements, prior, late, proposals, changes,
                                            provenance.repository_state()[0])
    out = Path(a.out)
    provenance.write_json(out / "survey.json", survey, strict=True)
    provenance.write_json(out / "unmapped.json", unmapped, strict=True)
    provenance.write_json(out / "proposal_source.json", source, strict=True)
    t = survey["totals"]
    print(f"library_gaps survey: kinds {t['kinds']}, instances {t['instances']}, wraps {t['wraps']}, shared gaps "
          f"{t['shared_gaps']}, local {t['local']}, unclassified {t['unclassified_objects']}, proposals "
          f"{len(survey['proposals'])}, {'final' if survey['approval'] is not None else 'draft'}")
    return 0


def wrap_needed(survey: dict, omap_rows: list[dict], kind: str, feature: str | None, element: str) -> dict:
    """The element, properties and states a wrap needs: the accepted proposal's, else the map row's (section 8.2)."""
    for p in survey.get("proposals") or []:
        if (p["kind"], p.get("feature") or None) == (kind, feature) and p.get("verdict") == "accepted" \
                and p.get("element") == element:
            return {"element": element, "properties": p.get("properties") or {}, "states": p.get("states") or []}
    for r in omap_rows:
        if (r.get("kind"), r.get("feature") or None) == (kind, feature) and r.get("element") == element \
                and r.get("state") in PLACING_STATES:
            return {"element": element, "properties": r.get("properties") if r.get("properties") is not None else {},
                    "states": r.get("states") if r.get("states") is not None else []}
    return {"element": element, "properties": {}, "states": []}


def release_doc(survey: dict, survey_sha: str, omap: dict) -> dict:
    """The gap list of the project release: one open gap per `openbridge` and `shared_gap` placement (section 8.2)."""
    rows = [r for r in omap.get("rows") or [] if isinstance(r, dict)]
    gaps, wraps = [], []
    wrap_by = {(w["kind"], w.get("feature") or None): w for w in survey.get("wraps") or []}
    for k in survey.get("kinds") or []:
        members = sorted(f["feature"][len("member:"):] for f in k.get("features") or []
                         if f["feature"].startswith("member:"))
        items = [(None, k["placement"], k["count"], None)] + [(f["feature"], f["placement"], f["count"], f)
                                                              for f in k.get("features") or []]
        for feature, placement, count, _ in items:
            if placement not in ("openbridge", "shared_gap"):
                continue
            what = f"the kind {k['kind']}" if feature is None else f"the feature {feature} of {k['kind']}"
            gap = {"id": gap_id(k["kind"], feature), "kind": k["kind"], "feature": feature, "item": None,
                   "status": "open", "mapping_rows": [], "placement": placement, "count": count}
            if placement == "openbridge":
                w = wrap_by.get((k["kind"], feature)) or {}
                element = w.get("element") or (k.get("map_row") or {}).get("element")
                gap["element"], gap["map_row"] = element, {"element": element, "state": w.get("state")}
                gap["needed"] = wrap_needed(survey, rows, k["kind"], feature, element)
                gap["library_today"] = f"neither the library nor the module draws {what}"
                gap["reason"] = (f"the approved survey places {what} on the pinned element {element} "
                                 f"(map row {w.get('state')}): a wrap in the project release")
                wraps.append({"kind": k["kind"], "feature": feature, "element": element})
            else:
                needed_members = members if feature is None else ([feature[len("member:"):]]
                                                                  if feature.startswith("member:") else [])
                gap["element"], gap["map_row"] = None, None
                gap["needed"] = {"members": needed_members, "instances": count}
                gap["library_today"] = f"neither the library nor the module draws {what}"
                gap["reason"] = (f"the approved survey counts {count} instances, more than {survey.get('local_max')}: "
                                 "a shared gap built in the project release")
            gaps.append(gap)
    gaps.sort(key=lambda g: (fold(g["kind"]), fold(g["feature"])))
    kinds = [{"kind": k["kind"], "count": k["count"], "pages": [], "resolution": k["placement"] or "unclassified",
              "placement": k["placement"]} for k in survey.get("kinds") or [] if k["count"] > 0]
    return {"schema": GAPS_SCHEMA, "kinds": kinds, "gaps": gaps, "open_count": len(gaps), "features": [],
            "local": [], "late": [], "wraps": wraps,
            "survey": {"sha256": survey_sha, "library_commit": survey.get("library_commit")}}


def run_release(a, clock: provenance.Clock, args_line: list[str]) -> int:
    for flag, value in (("--catalogue", a.catalogue), ("--profile", a.profile), ("--module", a.module),
                        ("--openbridge-map", a.openbridge_map)):
        if not value:
            raise InputFault(f"--release needs {flag}")
    survey = load(a.release, "survey")
    if not isinstance(survey, dict) or survey.get("schema") != SURVEY_SCHEMA:
        raise InputFault(f"survey: {a.release}: not a {SURVEY_SCHEMA} document")
    if not isinstance(survey.get("approval"), dict):
        raise InputFault(f"survey: {a.release}: a draft survey (its approval is not an object): only an approved "
                         "survey is released")
    for path, what in ((a.catalogue, "catalogue"), (a.profile, "profile"), (a.module, "module components")):
        load(path, what)
    omap = load(a.openbridge_map, "element map")
    check_map_rows(omap, element_tags(load(a.elements, "elements list")) if a.elements else None,
                   a.openbridge_map)
    sha = provenance.sha256_of(Path(a.release))
    doc = release_doc(survey, sha, omap)
    doc["provenance"] = clock.provenance("tools/hmi/library_gaps.py", args_line,
                                         [Path(a.release), Path(a.catalogue), Path(a.profile), Path(a.module),
                                          Path(a.openbridge_map)])
    out = Path(a.out)
    provenance.write_json(out / "gaps.json", doc, strict=True)
    print(f"library_gaps release: gaps {len(doc['gaps'])}, wraps {len(doc['wraps'])}, open {doc['open_count']}")
    return 0
