"""Local assemblies (NOTE-WFB-10 section 11.2, WP-W03): a part set a diagram page draws for a device kind the library
lacks, written once per kind into the child as the views `Local/<Kind>/Assembly` and `Local/<Kind>/Home`.

The two are siblings in the folder `Local/<Kind>`: Ignition 8.3.6 does not find a view whose folder also holds another
view (measured at T3, `wiki/07` GF-117), so the source's design, with the page's view at `Local/<Kind>` and its Home
beneath it, drew a view-not-found badge on the page. The Home keeps its path, which `Faceplate/ASM/Local` builds.

A descriptor's `assemblies[]` gives each instance: `{id, kind, device, title, label, x, y, w, h, parts, home}`
(`schemas/screen-descriptor.schema.json`, `$defs.assembly`). A part set is `{labels[], symbols[], lines[], buttons[],
shapes[]}` in pixels from the assembly's (or the Home's) top left corner. The parts are drawn with the diagram page's
own part functions: a label with `screen.text_label`, a readout, an indicator or an instrument field with
`screen.embed_symbol`, a line with `parts.line_node`, a button with `parts.button_node` (a pulse with the Confirm step,
`cadre.hmi.page_pulse`, write path W18) and a shape with `library.svg`. The views take the parameter `deviceId`, the
instance's tag folder; every dynamic part binds `deviceId` joined with its member through an indirect tag binding
(`{0}/<member>` with the reference `{view.params.deviceId}`, IGW:06-bindings section 4, the form of the faceplate rows
in `framework.py`). On the page each assembly is an `ia.display.view` of `Local/<Kind>/Assembly` with `deviceId`.

A shape is one SVG element in the palette's neutral stroke and no fill: `rect` (`x`, `y`, `width`, `height`) and
`ellipse` (`cx`, `cy`, `rx`, `ry`) and `polygon` (`points` as `x,y x,y`) in the attributes the Ignition-Wiki corpus
records for `ia.shapes.svg` elements (`wiki/components/ia.shapes.svg.md`, `harvest/corpus`), and a polyline as a
`path` (`d`), the element the page's lines already use, since the corpus records no `polyline` element.

Gate G0 (`g0_errors`) refuses, with a rule name each, in this order: `assembly-kind-not-local` (the kind is not in the
`--local-kinds` list), `assembly-kind-is-library` (the kind is one of the library profile's kinds),
`assembly-without-local-kinds` (an assembly with the option absent), `assembly-style` (a colour, class or style key on a
part), `assembly-parts-differ` (two assemblies of one kind that differ in `w`, `h`, `parts` or `home`, compared as
canonical JSON), `assembly-on-cards` (an assembly on a page whose layout is not `diagram`) and `assembly-part-ids` (a
part identifier used twice within an assembly, `parts` and `home` together).

The module imports `screen` and `parts` only inside functions: `screen` imports this module.
"""
from __future__ import annotations

import json

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import pv, library  # noqa: E402
else:
    from . import pv, library

RULES = ("assembly-kind-not-local", "assembly-kind-is-library", "assembly-without-local-kinds", "assembly-style",
         "assembly-parts-differ", "assembly-on-cards", "assembly-part-ids", "assembly-button-on-page")
ARRAYS = ("labels", "symbols", "lines", "buttons", "shapes")   # the arrays of a part set
DYNAMIC = ("symbols", "buttons")                                # the parts that read or write a member
LOCAL_KIND = "local"                                            # the device kind of an assembly's device
VIEW_ROOT = "Local"
PAGE_VIEW = "Assembly"   # the view a page embeds, beside `Home` in the kind's folder (GF-117)
PARAM = "deviceId"
DEVICE_REF = "{view.params.%s}" % PARAM
# the keys a part may not carry (T5): a colour, a class or a style; `style` of a label or a line is an enumeration
# (a word the schema checks), any other `style` is a style key
STYLE_KEYS = ("colour", "color", "class", "classes", "className", "style", "styles", "fill", "stroke", "font",
              "background")
STYLE_WORDS = ("labels", "lines")
# the parameter of the library view a symbol part binds its member to, and the type of the tag it reads
SYMBOL_BIND = {"readout": "value", "instrument-field": "value", "indicator": "state"}
MEMBER_TYPE = {"readout": ("Float8", 0.0), "instrument-field": ("Float8", 0.0), "indicator": ("Boolean", False)}
SYMBOL_PARAMS = ("unit", "format", "label")     # the keys of a symbol part the library view takes as parameters
PULSE_MS = 1000                                 # the length of a button's pulse (`parts.command_tags`' default)
NO_DETAIL = "No detail"
NO_DETAIL_SIZE = (360, 80)                      # the Home of a kind whose assemblies give none


def view_name(kind: str) -> str:
    """`<Kind>`: the kind with its first letter in upper case and the rest as written."""
    return kind[:1].upper() + kind[1:]


def kind_folder(kind: str) -> str:
    """`Local/<Kind>`: the folder of a kind's two views (a folder only, never a view itself: GF-117)."""
    return f"{VIEW_ROOT}/{view_name(kind)}"


def view_path(kind: str) -> str:
    """`Local/<Kind>/Assembly`: the view each assembly of the kind is drawn by on its page."""
    return f"{kind_folder(kind)}/{PAGE_VIEW}"


def home_path(kind: str) -> str:
    """`Local/<Kind>/Home`: the Home the local faceplate embeds (`devices_asm.LOCAL_HOME_PATH`)."""
    return f"{kind_folder(kind)}/Home"


def assemblies(desc: dict) -> list[dict]:
    """The assemblies of a descriptor (the entries that are objects)."""
    items = desc.get("assemblies") if isinstance(desc, dict) else None
    return [a for a in items if isinstance(a, dict)] if isinstance(items, list) else []


def part_sets(a: dict) -> list[tuple[str, dict]]:
    """The part sets of an assembly: `parts`, and the Home's where it has one."""
    out = [("parts", a.get("parts") if isinstance(a.get("parts"), dict) else {})]
    home = a.get("home")
    if isinstance(home, dict) and isinstance(home.get("parts"), dict):
        out.append(("home", home["parts"]))
    return out


def parts_of(a: dict) -> list[tuple[str, str, dict]]:
    """Every part of an assembly, its Home's included: (part set, array, part)."""
    out = []
    for where, ps in part_sets(a):
        for array in ARRAYS:
            items = ps.get(array)
            for p in items if isinstance(items, list) else []:
                if isinstance(p, dict):
                    out.append((where, array, p))
    return out


def dynamic_parts(a: dict) -> list[tuple[str, dict]]:
    """The dynamic parts of an assembly (symbols and buttons, its Home's included): (array, part)."""
    return [(array, p) for _where, array, p in parts_of(a) if array in DYNAMIC]


def part_members(a: dict) -> dict[str, tuple[str, object]]:
    """The members the dynamic parts of an assembly name, member -> (data type, starting value): a readout's and a
    field's number, an indicator's and a button's Boolean. Nothing beyond what the parts name."""
    out: dict[str, tuple[str, object]] = {}
    for array, p in dynamic_parts(a):
        m = p.get("member")
        if isinstance(m, str) and m:
            out.setdefault(m, MEMBER_TYPE.get(str(p.get("kind")), ("Float8", 0.0)) if array == "symbols"
                           else ("Boolean", False))
    return out


def canonical(a: dict) -> str:
    """What two assemblies of one kind must share, as canonical JSON: `w`, `h`, `parts` and `home`."""
    return json.dumps({k: a.get(k) for k in ("w", "h", "parts", "home")}, sort_keys=True, separators=(",", ":"))


def item(a: dict) -> dict:
    """The assembly as an item of `screen.descriptor_items`: kind `local`, its device, its faceplate title (the kind
    by default) and label (the id by default), and the parameter `localKind` (`<Kind>`)."""
    return {"id": a.get("id"), "kind": LOCAL_KIND, "device": a.get("device"),
            "title": a.get("title") or str(a.get("kind", "")), "label": a.get("label") or a.get("id", ""),
            "params": {"localKind": view_name(str(a.get("kind", "")))}}


# ---------------------------------------------------------------------------------------
# Gate G0
# ---------------------------------------------------------------------------------------
def _style_keys(array: str, p: dict) -> list[str]:
    out = []
    for k in STYLE_KEYS:
        if k not in p:
            continue
        if k == "style" and array in STYLE_WORDS and isinstance(p[k], str):
            continue   # the enumeration of a label's or a line's style (the schema checks the word)
        out.append(k)
    return out


def g0_errors(descs: list[dict], names: list[str], local_kinds: list[str] | None, library_kinds: set[str],
              exempt: dict[int, set[str]] | None = None) -> list[dict]:
    """The assembly rules of gate G0 over every descriptor of a build, each error `{rule, page, assembly, message}`,
    listed in the order of RULES. `local_kinds` is the `--local-kinds` list, None where the option is absent;
    `library_kinds` the library profile's kinds; `exempt` maps a descriptor's index to the kinds its own assemblies may
    draw whatever the option holds (the component test page's `benchlocal`)."""
    exempt = exempt or {}
    found: list[tuple[int, int, dict]] = []

    def err(rule: str, page: str, a: dict, message: str) -> None:
        found.append((RULES.index(rule), len(found), {"rule": rule, "page": page, "assembly": str(a.get("id", "")),
                                                       "message": message}))
    by_kind: dict[str, tuple[str, dict, str]] = {}
    for i, desc in enumerate(descs):
        page = names[i] if i < len(names) else str(i)
        layout = (desc.get("screen") or {}).get("layout", "diagram") if isinstance(desc, dict) else "diagram"
        own = exempt.get(i, set())
        for a in assemblies(desc):
            kind = a.get("kind")
            kind = kind if isinstance(kind, str) else ""
            mine = kind in own
            if local_kinds is not None and not mine and kind not in local_kinds:
                err("assembly-kind-not-local", page, a, f"kind {kind!r} is not in the local kinds file")
            if kind in library_kinds:
                err("assembly-kind-is-library", page, a, f"kind {kind!r} is a kind of the library: draw it with its "
                                                         "library symbol or its wrap")
            if local_kinds is None and not mine:
                err("assembly-without-local-kinds", page, a, "an assembly needs screen.py --local-kinds")
            for where, array, p in parts_of(a):
                keys = _style_keys(array, p)
                if keys:
                    err("assembly-style", page, a, f"{where} {array} {p.get('id')!r} carries {', '.join(keys)}: a part "
                                                   "takes the library's palette and fonts only")
            if kind:
                first = by_kind.setdefault(kind, (page, a, canonical(a)))
                if first[1] is not a and first[2] != canonical(a):
                    err("assembly-parts-differ", page, a, f"kind {kind!r}: w, h, parts and home differ from assembly "
                                                          f"{first[1].get('id')!r} of {first[0]}; one view per kind")
            if layout != "diagram":
                err("assembly-on-cards", page, a, f"the page's layout is {layout!r}; an assembly is drawn on a diagram")
            seen: set = set()
            twice: list[str] = []
            for _where, _array, p in parts_of(a):
                pid = p.get("id")
                if pid in seen and str(pid) not in twice:
                    twice.append(str(pid))
                seen.add(pid)
            if twice:
                err("assembly-part-ids", page, a, f"part identifiers used twice in parts and home: {', '.join(twice)}")
            on_page = [str(p.get("id")) for _where, array, p in parts_of(a) if array == "buttons" and _where == "parts"]
            if on_page:   # a command lives on the faceplate, as the library's symbols' do (section 11.2 item 1)
                err("assembly-button-on-page", page, a, f"parts holds the button(s) {', '.join(on_page)}: a button is "
                                                        "allowed in home only, so that a press never also opens the "
                                                        "faceplate")
    return [e for _r, _n, e in sorted(found, key=lambda x: (x[0], x[1]))]


# ---------------------------------------------------------------------------------------
# The views
# ---------------------------------------------------------------------------------------
def _screen():
    if __package__ in (None, ""):
        from hmi import screen
    else:
        from . import screen
    return screen


def _parts():
    if __package__ in (None, ""):
        from hmi import parts
    else:
        from . import parts
    return parts


def _indirect(x):
    """The direct tag bindings the part functions wrote under the device reference, made indirect: a tag path
    `{view.params.deviceId}/<member>` becomes `{0}/<member>` with the reference `{0}` = `{view.params.deviceId}`."""
    if isinstance(x, dict):
        if x.get("type") == "tag" and isinstance(x.get("config"), dict):
            cfg = x["config"]
            path = cfg.get("tagPath")
            if cfg.get("mode") == "direct" and isinstance(path, str) and path.startswith(DEVICE_REF + "/"):
                b = pv.tag_indirect("{0}/" + path[len(DEVICE_REF) + 1:], {"0": DEVICE_REF},
                                    bidirectional=bool(cfg.get("bidirectional")))
                x.clear()
                x.update(b)
                return x
        for v in x.values():
            _indirect(v)
    elif isinstance(x, list):
        for v in x:
            _indirect(v)
    return x


def _shape_node(s: dict) -> dict:
    w, h = float(s["w"]), float(s["h"])
    form = s["form"]
    paint = {"stroke": {"paint": "var(--element-neutral-color)", "width": 2}, "fill": {"paint": "none"}}
    if form == "rect":
        el = {"type": "rect", "x": 1, "y": 1, "width": max(w - 2, 0), "height": max(h - 2, 0)}
    elif form == "ellipse":
        el = {"type": "ellipse", "cx": w / 2, "cy": h / 2, "rx": max(w / 2 - 1, 0), "ry": max(h / 2 - 1, 0)}
    elif form == "polygon":
        el = {"type": "polygon", "points": " ".join(f"{x:g},{y:g}" for x, y in s["points"])}
    else:   # polyline: a path, as the page's lines draw
        el = {"type": "path", "d": "M" + "L".join(f"{x:g} {y:g}" for x, y in s["points"])}
    el = {"name": s["id"], **el, **paint}
    return library.svg(f"Shape_{s['id']}", pv.cpos(s["x"], s["y"], w, h), [el], view_box=f"0 0 {w:g} {h:g}",
                       props={"style": {"overflow": "visible"}})


def _root(width: float, height: float, kids: list[dict]) -> dict:
    """The coordinate root named `Diagram` at the view's size, as a diagram page's (gate G5 reads its size)."""
    return pv.node("ia.container.coord", "Diagram", {}, {"style": {"overflow": "hidden", "width": f"{width:g}px",
                                                                   "height": f"{height:g}px"}}, children=kids)


def part_view(ps: dict, width: float, height: float, contracts: dict, rep) -> dict:
    """One view of a part set: a coordinate root named `Diagram` of the given size, the parameter `deviceId`, the
    shapes and lines under the labels and the dynamic parts."""
    screen, parts = _screen(), _parts()
    kids: list[dict] = []
    custom: dict = {}
    custom_cfg: dict = {}
    for s in ps.get("shapes") or []:
        kids.append(_shape_node(s))
    for ln in ps.get("lines") or []:
        node, c, cc = parts.line_node({"id": ln["id"], "points": ln["points"], "style": ln.get("style", "solid")},
                                      width, height, "")
        kids.append(node)
        custom.update(c)
        custom_cfg.update(cc)
    for t in ps.get("labels") or []:
        kids.append(screen.text_label({k: t[k] for k in ("id", "x", "y", "w", "h", "text", "align", "style") if k in t}))
    for p in ps.get("symbols") or []:
        kind = p["kind"]
        sym = {"id": p["id"], "kind": kind, "x": p["x"], "y": p["y"], "w": p["w"], "h": p["h"],
               "params": {k: p[k] for k in SYMBOL_PARAMS if k in p},
               "bind": {SYMBOL_BIND[kind]: p["member"]} if p.get("member") else {}}
        node, c, cc = screen.embed_symbol(sym, contracts, DEVICE_REF, rep, toolbar=False,
                                          pos=pv.cpos(p["x"], p["y"], p["w"], p["h"]))   # the part's box as given
        kids.append(node)
        screen.merge_custom(custom, c)
        custom_cfg.update(cc)
    for b in ps.get("buttons") or []:
        button = {"id": b["id"], "x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"], "label": b["label"],
                  "action": {"type": "pulse", "tag": b.get("member", ""), "ms": PULSE_MS}}
        code = f"self.view.params.{PARAM} + {('/' + str(b.get('member', ''))) !r}"
        node, c, cc = parts.button_node(button, {}, rep, path_code=code)
        kids.append(node)
        custom.update(c)
        custom_cfg.update(cc)
    root = _root(width, height, kids)
    _indirect(root)
    _indirect(custom_cfg)
    return pv.view(root, params={PARAM: ""}, param_dirs={PARAM: "input"}, size={"width": width, "height": height},
                   custom=custom, custom_config=custom_cfg)


def no_detail_view() -> dict:
    """The Home of a kind whose assemblies give none: one label, "No detail"."""
    w, h = NO_DETAIL_SIZE
    label = _screen().text_label({"id": "NoDetail", "x": 8, "y": 8, "w": w - 16, "h": 24, "text": NO_DETAIL,
                                  "style": "body"})
    root = _root(w, h, [label])
    return pv.view(root, params={PARAM: ""}, param_dirs={PARAM: "input"}, size={"width": w, "height": h})


def kind_views(descs: list[dict], contracts: dict) -> dict[str, tuple[dict, str, list[str]]]:
    """`Local/<Kind>/Assembly` and `Local/<Kind>/Home` for each kind the descriptors draw, from its first assembly (G0 holds
    every other equal): view path -> (view, the route of the page that first draws the kind, the errors of its parts)."""
    screen = _screen()
    first: dict[str, tuple[dict, str]] = {}
    for desc in descs:
        if (desc.get("screen") or {}).get("layout", "diagram") != "diagram":
            continue
        for a in assemblies(desc):
            first.setdefault(a["kind"], (a, desc["screen"]["route"]))
    out: dict[str, tuple[dict, str, list[str]]] = {}
    for kind, (a, route) in sorted(first.items()):
        rep = screen.Report()
        out[view_path(kind)] = (part_view(a["parts"], a["w"], a["h"], contracts, rep), route, rep.errors)
        home = a.get("home")
        rep = screen.Report()
        doc = part_view(home["parts"], home["w"], home["h"], contracts, rep) if home else no_detail_view()
        out[home_path(kind)] = (doc, route, rep.errors)
    return out


def page_nodes(desc: dict) -> list[dict]:
    """The page's embeds: an `ia.display.view` of `Local/<Kind>/Assembly` at each assembly's box, with `deviceId` the device's
    tag folder."""
    screen = _screen()
    root = desc.get("tagRoot", "")
    return [pv.node("ia.display.view", a["id"], pv.cpos(a["x"], a["y"], a["w"], a["h"]),
                    {"path": view_path(a["kind"]), "params": {PARAM: screen.tag_path(root, a["device"])}},
                    events=click(a, screen.tag_path(root, a["device"])))
            for a in assemblies(desc)]


def click(a: dict, folder: str) -> dict:
    """The click of an assembly on a page: the library's opener (`library.open_device`) for the device `folder`, the kind
    `local` and the `<Kind>` of the assembly, with its title and label, so that the dock or the popup opens
    `Faceplate/ASM/Local` on the kind's Home (NOTE-WFB-10 section 11.2 item 5)."""
    quote = _parts().quote
    it = item(a)
    return pv.on_click(library.open_device(quote(folder), quote(LOCAL_KIND), quote(it["title"]), quote(it["label"]),
                                           local=quote(it["params"]["localKind"])))


def command_tags(desc: dict) -> list[dict]:
    """The pulse each button of an assembly declares, `{path, ms}` with the full tag path: `session.custom.commands`
    holds it, so that `cadre.hmi.page_pulse` writes it and no other tag."""
    screen = _screen()
    root = desc.get("tagRoot", "")
    out = []
    for a in assemblies(desc):
        for array, p in dynamic_parts(a):
            if array == "buttons" and p.get("member") and isinstance(a.get("device"), str):
                out.append({"path": screen.tag_path(root, f"{a['device']}/{p['member']}"), "ms": PULSE_MS})
    return out

