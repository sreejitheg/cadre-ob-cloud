"""The descriptors, tag model, device model and walk plan entries of an ASM project, built from the ASM model and the
page designs.

Generalised from the eng02 slice's descriptor builder (ARCH-WFB-01 revision B8 Table 109, WFBD-091). The slice drew
three pages by hand; here a design (`wfb.migration.design/1`) per page gives every element's box, component and tags,
and the model (`cadre-hmi-asm-model/1`) says which device each element is, so that:

  * a device's symbol with its node (`device`) is drawn on the device's own page only; on every other page the device
    is drawn plain and still opens its faceplate through the Level 5 `faceplate` key;
  * a kind the library lacks is drawn as the library's counted gap box and listed as a gap, which must be accepted;
  * items of one column share a width and items of one row a height within 4 px (`--equalise`);
  * a pipe takes the medium the understanding established (`--medium`);
  * the kinds the module draws are drawn by the module (`--render module`), and the audit says so per kind.

Writes under `O/bridge/` the layout the generator and gate blocks read in place (B8 section 29.3.3):
`build.json` (`ctig.bridge.build/1`), `descriptors/*.json` (`cadre-hmi-screen/1`), `tags_devices.json`,
`devices.json` (`cadre-hmi-devices/1`), `tags.json`, `coverage_map.json`, `route_map.json` and `walk/walk.json`
(`ctig.bridge.walk/1`, the plan commands `openbridge.walk_plan` runs), and under `O` `coverage.json`
(`cadre-hmi-descriptor-coverage/1`), `tags-document.json` and `gaps-after.json`.

Exit codes: 0; 2 the run finished with findings (a row no element carries, a route that does not resolve, a gap not
accepted, a column that differs); 1 an input fault. Nothing here contacts a gateway.

Run:  python tools/hmi/asm_descriptors.py --model M --designs L --tables T --project cadre_hmi_x --parent P
          --tag-root '[default]cadre_hmi_x' --window 1920x1080 --render module --frame asm --faceplate asm
          [--faceplates F --gaps F --accepted F --inventory D --module-first --equalise --medium --simulation
          --component-test] --out O
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import provenance, testbench  # noqa: E402
    from hmi.asm_model import InputFault, load, path_list, slug, variable_rows  # noqa: E402
    from hmi.library_gaps import read_accepted  # noqa: E402
else:
    from . import provenance, testbench
    from .asm_model import InputFault, load, path_list, slug, variable_rows
    from .library_gaps import read_accepted

ROOT = Path(__file__).resolve().parents[2]
TOOL = "tools/hmi/asm_descriptors.py"
EQ_TOL = 4                                   # px: boxes whose x (a column) or y (a row) differ by no more than this
DEFAULT_FIT = {"reserveX": 0, "reserveY": 216}
LEVEL_WORD = {1: "Level 1 overview", 2: "Level 2 unit", 3: "Level 3 faceplate", 4: "Level 4 support"}
MEDIA = {"neutral", "fresh-water", "sea-water", "fuel", "oil", "steam", "hot", "cold", "air", "waste"}
#: Source tag types (`ctig.tables/1`) to Ignition data types.
DTYPE = {"DIGITAL": "Boolean", "REAL": "Float8", "INT": "Int4", "LONG": "Int4", "STRING": "String", "BYTE": "Int4"}
#: Device kinds that take their state from a Boolean `state` member.
STATE_KINDS = {"pump", "motor", "fan", "valve", "analogvalve", "damper", "indicator", "generator"}
VALUE_KINDS = {"instrument-field", "readout", "instrument"}
SAFE = re.compile(r"[^A-Za-z0-9_]")
COMPARE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*(<=|>=|!=|==|<|>|=)\s*(-?\d+(?:\.\d+)?)\s*$")
PRIORITY = {"high": "High", "medium": "Medium", "low": "Low", "diagnostic": "Diagnostic", "critical": "Critical"}


def profile_for(parent: str) -> dict:
    """The library profile of the parent the project inherits (WFB-153), built from the repository's catalogue."""
    from hmi import library_profile
    from hmi.screen import load_contracts
    return library_profile.build(load_contracts(), parent)


def ident(text: str) -> str:
    out = SAFE.sub("_", str(text))
    return out if out[:1].isalpha() else "i_" + out


def ctx_units(ctx, reads):
    return ctx.display(reads).get("units")


def kind_of_component(component: str) -> str:
    return (component or "").lower()


def part_name(kind: str) -> str:
    return "cadre.ob." + kind.replace("-", "")


def node_path(model: dict, node_id: str) -> str:
    by = {n["id"]: n for n in model["nodes"]}
    names = []
    while node_id:
        names.append(by[node_id]["name"].replace("/", " "))
        node_id = by[node_id]["parent"]
    return "/".join(reversed(names))


class Context:
    """What the builders share: the model, the catalogue and the tag registry."""

    def __init__(self, model: dict, tables: dict, profile: dict, module: dict, gaps: dict, accepted: set[str],
                 args) -> None:
        self.model, self.tables, self.profile, self.module = model, tables, profile, module
        self.args = args
        self.accepted = accepted
        self.gap_by_kind = {g["kind"]: g for g in (gaps or {}).get("gaps", [])}
        self.mapping = {r["uid"]: r for r in model["mapping"]}
        self.pages = {p["id"]: p for p in model["pages"]}
        self.devices = model["devices"]
        self.alarms = {a["tag"]: a for a in model["alarms"]}
        self.root = args.tag_root.split("]", 1)[-1].strip("/")
        self.signals: dict[str, dict] = {}          # source variable -> {"type", "doc"...}
        self.vars = variable_rows(tables)
        self.members: dict[str, dict[str, tuple[str, str]]] = {}   # device -> member -> (data type, source variable)
        self.flow_by_an = {f["an"]: f for f in model.get("flows", {}).values() if f.get("an")}
        self.kinds_used: dict[str, dict] = {}
        self.gaps_open: dict[str, dict] = {}

    # ---- signals ------------------------------------------------------------------------------
    def signal(self, name: str, want: str | None = None) -> str:
        """Register a source variable and return its tag path below the tag root."""
        if name not in self.signals:
            v = self.vars.get(name, {})
            dtype = DTYPE.get(str(v.get("type") or "").upper()) or want or "Float8"
            self.signals[name] = {"dtype": dtype, "var": v}
        return f"src/{name}"

    def display(self, reads: list[str]) -> dict:
        """The unit and the format of what a readout shows, from the tags document's variable (`ctig.tables/1`) that the
        item reads. No display precision comes from the model: a variable with no format states none."""
        v = self.vars.get(reads[0], {}) if reads else {}
        return {k: v[k] for k in ("units", "format") if v.get(k)}

    def has_folder(self, tag: str) -> bool:
        d = self.devices.get(tag)
        return bool(d) and d["kind"] in self.profile["deviceKinds"]

    # ---- module audit -------------------------------------------------------------------------
    def audit(self, kind: str) -> dict:
        if kind not in self.kinds_used:
            lib = kind in self.profile["kinds"]
            part = part_name(kind)
            if not lib:
                row = {"kind": kind, "rendered_by": "gap", "reason": "the library has no symbol of this kind"}
            elif self.args.render == "module" and part in self.module:
                row = {"kind": kind, "rendered_by": "module", "reason": f"the module draws it ({part})"}
            elif self.args.render == "module":
                row = {"kind": kind, "rendered_by": "library", "reason": "the module has no part for this kind"}
            else:
                row = {"kind": kind, "rendered_by": "library", "reason": "the project renders with the library's views"}
            self.kinds_used[kind] = row
        return self.kinds_used[kind]

    def gap_for(self, kind: str) -> str | None:
        """The id of the open or accepted gap of a kind the library lacks, else None."""
        if kind in self.profile["kinds"]:
            return None
        g = self.gap_by_kind.get(kind)
        gid = g["id"] if g else f"GAP-{ident(kind)}"
        status = "accepted" if (gid in self.accepted or (g or {}).get("status") in ("accepted", "closed")) else "open"
        self.gaps_open.setdefault(gid, {"id": gid, "kind": kind, "status": status})
        return gid


# ---- the tags -------------------------------------------------------------------------------------------------
def mem(name, dtype, value, **kw):
    return testbench.mem(name, dtype, value, **kw)


def condition(ctx: Context, source: str | None) -> tuple[str, list[str]]:
    """The expression of an alarm tag for a source condition, and the variables it reads."""
    ref = lambda n: "{" + f"[.]../../src/{n}" + "}"   # noqa: E731  (alm/<tag> inside the device folder)
    m = COMPARE.match(source or "")
    if m:
        op = "=" if m.group(2) == "==" else m.group(2)
        ctx.signal(m.group(1), "Float8")
        return f"coalesce({ref(m.group(1))}, 0) {op} {m.group(3)}", [m.group(1)]
    if source and re.fullmatch(r"[A-Za-z0-9_]+", source):
        ctx.signal(source, "Boolean")
        return f"coalesce({ref(source)}, false)", [source]
    return "false", []


def alarm_tag(ctx: Context, a: dict, label: str, node: str) -> dict:
    expression, _ = condition(ctx, a.get("source"))
    name = ident(a["tag"])
    al = {"name": name, "label": f"{label} {a['desc']}", "displayPath": f"{node}/{label}" if node else label,
          "priority": PRIORITY[a["priority"]], "shelvingAllowed": a["priority"] != "critical", "setpointA": 1.0}
    if a["delay"]:
        al["timeOnDelaySeconds"] = a["delay"]
    doc = f"category {a['category']}" if a.get("category") else ""
    return testbench.expr(name, "Boolean", expression, alarms=[al],
                          documentation=(doc + ("; priority inferred from the category's rank" if a["inferred"] else "")).strip("; "))


def sim_script(ctx: Context) -> str:
    """The value-changed script of sim/tick: the analogue sources with a range move as a sine about their middle,
    once a second, in one writeBlocking (Jython 2.7, tab indented, gateway scope)."""
    waves = []
    for i, (name, s) in enumerate(sorted(ctx.signals.items())):
        v = s["var"]
        if s["dtype"] == "Float8" and v.get("eng_hi") not in (None, ""):
            lo, hi = float(v.get("eng_lo") or 0), float(v["eng_hi"])
            waves.append((f"src/{name}", round((lo + hi) / 2, 3), round((hi - lo) * 0.05, 3), 40 + 3 * (i % 7)))
    lines = ["# plant simulation: one write, once a second (value of sim/tick changes)", "import math",
             f"base = {ctx.root + '/'!r}", "ms = system.date.toMillis(system.date.now())", "out = {}",
             f"for path, mean, amp, div in {waves!r}:", "\tout[path] = mean + amp * math.sin(ms / (div * 159.15))",
             "keys = sorted(out)", "system.tag.writeBlocking([base + k for k in keys], [out[k] for k in keys])"]
    return "".join("\t" + ln + "\n" for ln in lines)


def tag_model(ctx: Context, simulation: bool) -> tuple[dict, dict]:
    """`(full, devices_only)`: the folder documents of the tag model."""
    a = ctx.args
    devs, alarm_root = [], []
    for tag, d in ctx.devices.items():
        members = ctx.members.get(tag, {})
        alm = [alarm_tag(ctx, al, tag, node_path(ctx.model, d["node"])) for al in ctx.model["alarms"] if al["device"] == tag]
        if not ctx.has_folder(tag):
            if alm:
                alarm_root.append({"name": ident(tag), "tagType": "Folder", "tags": alm})
            continue
        tags = [testbench.expr(m, dt, "coalesce({" + f"{a.tag_root}/src/{src}" + "}, " + ("false" if dt == "Boolean"
                               else "''" if dt == "String" else "0") + ")") for m, (dt, src) in members.items()]
        for name in [src for _, src in members.values()]:
            ctx.signal(name)
        if alm:
            tags.append({"name": "alm", "tagType": "Folder", "tags": alm})
        devs.append({"name": ident(tag), "tagType": "Folder", "tags": tags})
    for al in ctx.model["alarms"]:   # alarms of a device no page draws, or of none
        if al["device"] is None:
            alarm_root.append(alarm_tag(ctx, al, al["tag"], ""))
    src = []
    for name, s in sorted(ctx.signals.items()):
        v = s["var"]
        init = False if s["dtype"] == "Boolean" else "" if s["dtype"] == "String" else (
            0 if s["dtype"].startswith("Int") else float(v.get("eng_lo") or 0))
        t = mem(name, s["dtype"], init)
        if v.get("comment"):
            t["documentation"] = v["comment"]
        if v.get("units"):
            t["engUnit"] = v["units"]
        if v.get("eng_hi") not in (None, "") and s["dtype"] != "Boolean":
            t["engLow"], t["engHigh"] = float(v.get("eng_lo") or 0), float(v["eng_hi"])
        src.append(t)
    base = [{"name": "src", "tagType": "Folder", "tags": src}, *devs]
    if alarm_root:
        base.append({"name": "alm", "tagType": "Folder", "tags": alarm_root})
    name = ctx.root.rsplit("/", 1)[-1]
    devices_only = {"name": name, "tagType": "Folder", "tags": base}
    sim = [{"name": "sim", "tagType": "Folder", "tags": [
        mem("reset", "Boolean", False),
        testbench.expr("tick", "DateTime", "now(1000)", eventScripts=[{"eventid": "valueChanged",
                                                                     "script": sim_script(ctx)}],
                       documentation="The plant simulation: its value-changed script writes the analogue sources")]}]
    full = {"name": name, "tagType": "Folder", "tags": (sim if simulation else []) + base}
    return full, devices_only


# ---- the descriptors ------------------------------------------------------------------------------------------
class PageBuilder:
    def __init__(self, ctx: Context, page: dict, design: dict | None) -> None:
        self.ctx, self.page, self.design = ctx, page, design
        self.sym: dict[str, dict] = {}
        self.arrays: dict[str, list] = {k: [] for k in ("labels", "symbols", "pipes", "buttons", "links", "bars",
                                                        "trends", "wells", "lines", "alarmPanels")}
        self.carried: dict[str, list[str]] = {}
        self.gap: dict[str, str] = {}
        self.item_el: dict[str, str] = {}
        self.uid_of: dict[str, str] = {}       # an element id to the uid of the design item it carries
        self.findings: list[str] = []

    def carry(self, uid: str, element: str, gap: str | None = None) -> None:
        self.carried.setdefault(uid, []).append(element)
        self.item_el.setdefault(uid, element)
        self.uid_of.setdefault(element.split(":", 1)[-1], uid)
        if gap:
            self.gap[uid] = gap

    # one element per design item
    def run(self) -> dict:
        d = self.design
        later = ("button", "link", "pipe")   # these refer to symbols: drawn after them
        for it in sorted(d["items"], key=lambda i: i["kind"] in later):
            fn = getattr(self, "do_" + it["kind"].replace("-", "_"), None)
            if fn is None:
                self.findings.append(f"{it['uid']}: the item kind {it['kind']!r} has no element")
                continue
            fn(it)
        self.fit_findings()
        return self.descriptor()

    def fit_findings(self) -> None:
        """A box stays the design's. Where the library draws a kind larger than its box (`size` of the profile: a lamp
        is 48 by 48 whatever the box) and the larger drawing touches another symbol, say so, so that the design stage can
        move or resize it; the box is never grown here (the generator's gate G5 would refuse the overlap)."""
        kinds = self.ctx.profile["kinds"]
        syms = self.arrays["symbols"]
        for a in syms:
            size = (kinds.get(a["kind"]) or {}).get("size") or [0, 0]
            aw, ah = max(a["w"], size[0]), max(a["h"], size[1])
            if (aw, ah) == (a["w"], a["h"]):
                continue
            for b in syms:       # only what the growth itself reaches: the design's own boxes do not overlap
                if b is a:
                    continue
                ix = min(a["x"] + aw, b["x"] + b["w"]) - max(a["x"], b["x"])
                iy = min(a["y"] + ah, b["y"] + b["h"]) - max(a["y"], b["y"])
                dx = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
                dy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
                if ix > 4 and iy > 4 and not (dx > 4 and dy > 4):
                    self.findings.append(
                        f"{self.uid_of.get(a['id'], a['id'])}: the library draws a {a['kind']} {aw:g} x {ah:g} px and it "
                        f"then overlaps {b['id']}; the design's box is {a['w']:g} x {a['h']:g} px")

    def box(self, it: dict) -> dict:
        b = it["bbox"]
        return {"x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"]}

    def row(self, it: dict) -> dict:
        return self.ctx.mapping.get(it["uid"], {})

    def do_symbol(self, it: dict) -> None:
        ctx = self.ctx
        kind = kind_of_component(it["component"])
        ctx.audit(kind)
        gap = ctx.gap_for(kind)
        row = self.row(it)
        tag = row.get("device")
        dev = ctx.devices.get(tag) if tag else None
        own = bool(dev) and ctx.has_folder(tag) and dev["page"] == self.page["id"] and not any(
            s.get("device") is True and s["id"] == ident(tag) for s in self.arrays["symbols"])
        sid = ident(tag) if own else "i_" + ident(it["uid"].split(":", 1)[-1])
        s = {"id": sid, "kind": kind, **self.box(it)}
        reads = it.get("reads") or []
        label = it.get("label") or (dev or {}).get("label") or tag
        if label:
            s["label"] = label
        params = {}
        if tag and ctx.profile["kinds"].get(kind, {}).get("identifier", {}).get("param") == "tag":
            params.update({"tag": tag, "hasTag": True})
        bind_params = ctx.profile["kinds"].get(kind, {}).get("bind", {})
        folder = ctx.has_folder(tag) if tag else False
        member = None
        if kind in STATE_KINDS or kind in ("switch",):
            member = ("state", "Boolean")
        elif kind == "tank":
            member = ("level", "Float8")
        elif kind in VALUE_KINDS:
            member = ("value", "Float8")
        elif kind == "sequence":
            member = ("stepText", "String")
        if kind == "tank":
            bind_params = {"value": "level"}
        elif kind == "switch":   # the profile states no default binding for a switch; its `on` parameter takes the state
            bind_params = {"on": "state"}
        if folder and member and reads:
            ctx.members.setdefault(tag, {}).setdefault(member[0], (member[1], reads[0]))
            if kind == "sequence":
                ctx.members[tag].setdefault("step", ("Int4", reads[0]))
            s["bind"] = {p: f"{tag}/{m}" for p, m in bind_params.items() if m in ctx.members[tag]}
            if kind == "sequence":
                s["bind"] = {"text": f"{tag}/stepText"}
        elif reads and bind_params:
            first = next(iter(bind_params))
            s["bind"] = {first: ctx.signal(reads[0], member[1] if member else None)}
        if own:
            s["device"] = True
        elif folder:
            s["faceplate"] = tag
        elif it.get("faceplate"):
            s["faceplate"] = it["faceplate"]
        shown = ctx.display(reads)
        if shown.get("units") and kind in ("tank", "readout", "instrument-field"):
            params["unit"] = shown["units"]
        if shown.get("format") and kind in ("readout", "instrument-field"):
            params["format"] = shown["format"]
        if params:
            s["params"] = params
        self.arrays["symbols"].append(s)
        self.carry(it["uid"], f"symbols:{sid}", gap)

    def do_readout(self, it: dict) -> None:
        ctx = self.ctx
        ctx.audit("readout")
        reads = it.get("reads") or []
        sid = "i_" + ident(it["uid"].split(":", 1)[-1])
        params = {"hasTag": False}
        shown = ctx.display(reads)
        if shown.get("units"):
            params["unit"] = shown["units"]
        if shown.get("format"):
            params["format"] = shown["format"]
        if it.get("label"):
            params["label"] = it["label"]
        s = {"id": sid, "kind": "readout", **self.box(it), "params": params}
        if reads:
            s["bind"] = {"value": ctx.signal(reads[0], "Float8")}
        self.arrays["symbols"].append(s)
        self.carry(it["uid"], f"symbols:{sid}")

    def do_indicator(self, it: dict) -> None:
        ctx = self.ctx
        ctx.audit("indicator")
        reads = it.get("reads") or []
        sid = "i_" + ident(it["uid"].split(":", 1)[-1])
        s = {"id": sid, "kind": "indicator", **self.box(it)}
        if reads:
            s["bind"] = {"state": ctx.signal(reads[0], "Boolean")}
        if it.get("states"):
            s["states"] = [{k: v for k, v in st.items() if k in ("value", "colour", "label")} for st in it["states"]]
        if it.get("state_default"):
            s["stateDefault"] = it["state_default"]
        if it.get("label"):
            s["label"] = it["label"]
        al = next((a for a in ctx.model["alarms"] if a.get("source") in reads), None)   # the alarm the lamp follows
        if al:
            s["alarm"] = (f"{al['device']}/alm/{ident(al['tag'])}" if al["device"] and ctx.has_folder(al["device"])
                          else f"alm/{ident(al['device'])}/{ident(al['tag'])}" if al["device"]
                          else f"alm/{ident(al['tag'])}")
        self.arrays["symbols"].append(s)
        self.carry(it["uid"], f"symbols:{sid}")

    def do_label(self, it: dict) -> None:
        lid = "l_" + ident(it["uid"].split(":", 1)[-1])
        row = self.row(it)
        style = "heading" if (row.get("section") == "static" and "heading" in (row.get("label") or "").lower()) or \
            it.get("style") == "heading" else "label"
        self.arrays["labels"].append({"id": lid, **self.box(it), "text": it.get("text") or it.get("label") or "",
                                      "style": style})
        self.carry(it["uid"], f"labels:{lid}")

    def action_of(self, it: dict) -> dict | None:
        nav = next((n for n in self.design.get("navigation", []) if n["uid"] == it["uid"]), None)
        if nav and nav.get("faceplate"):
            return {"type": "faceplate", "device": nav["faceplate"],
                    "tab": next((o["tab"] for o in (self.ctx.devices.get(nav["faceplate"]) or {}).get("openers", [])
                                 if o.get("uid") == it["uid"] and o.get("tab")), None) or "home"}
        route = nav.get("route") if nav else None
        if route:
            return {"type": "route", "route": route}
        return None

    def accounted(self, it: dict) -> bool:
        """A navigation entry whose target the model says is not migrated needs no element."""
        return any(n.get("uid") == it["uid"] and n["resolution"] == "not_migrated" for n in self.ctx.model["nav"])

    def do_button(self, it: dict) -> None:
        bid = "b_" + ident(it["uid"].split(":", 1)[-1])
        action = self.action_of(it)
        if action is None:
            if not self.accounted(it):
                self.findings.append(f"{it['uid']}: a button without a navigation row")
            return
        if action["type"] == "faceplate":
            action["tab"] = str(action["tab"]).lower()
            action["label"] = it.get("label") or self.row(it).get("label") or ""
            action = {k: v for k, v in action.items() if v}
            if not any(sy["id"] == action["device"] and sy.get("device") is True for sy in self.arrays["symbols"]):
                action["kind"] = (self.ctx.devices.get(action["device"]) or {}).get("kind", "pump")
        self.arrays["buttons"].append({"id": bid, **self.box(it), "label": it.get("label") or self.row(it).get("label")
                                       or "Open", "action": action})
        self.carry(it["uid"], f"buttons:{bid}")

    def do_link(self, it: dict) -> None:
        lid = "k_" + ident(it["uid"].split(":", 1)[-1])
        action = self.action_of(it)
        if not action or action["type"] != "route":
            if not self.accounted(it):
                self.findings.append(f"{it['uid']}: a link without a route")
            return
        self.arrays["links"].append({"id": lid, **self.box(it), "route": action["route"]})
        self.carry(it["uid"], f"links:{lid}")

    def do_pipe(self, it: dict) -> None:
        ctx = self.ctx
        pid = "p_" + ident(it["uid"].split(":", 1)[-1])
        flow = ctx.flow_by_an.get(it.get("original_an"))
        if flow is None:
            self.findings.append(f"{it['uid']}: no flow of the model for {it.get('original_an')!r}")
            return
        k = self.design["canvas"].get("scale") or 1.0      # the original's routing, scaled by the design's canvas
        path = [[pt["x"] * k, pt["y"] * k] for pt in flow["path"]]
        if len(path) < 2:
            self.findings.append(f"{it['uid']}: a pipe with fewer than two points")
            return

        def end(uid, point, towards):
            el = self.item_el.get(uid) if uid else None
            sym = next((s for s in self.arrays["symbols"] if f"symbols:{s['id']}" == el), None)
            if sym is None:
                return {"x": point[0], "y": point[1], "end": "none"}
            cx, cy = sym["x"] + sym["w"] / 2, sym["y"] + sym["h"] / 2
            dx, dy = towards[0] - cx, towards[1] - cy
            side = ("right" if dx > 0 else "left") if abs(dx) >= abs(dy) else ("bottom" if dy > 0 else "top")
            return {"ref": sym["id"], "side": side}
        medium = flow.get("medium") if ctx.args.medium and flow.get("medium") in MEDIA else "neutral"
        p = {"id": pid, "from": end(flow.get("from"), path[0], path[1]), "to": end(flow.get("to"), path[-1], path[-2]),
             "medium": medium}
        if len(path) > 2:
            p["via"] = [[round(x, 1), round(y, 1)] for x, y in path[1:-1]]
        self.arrays["pipes"].append(p)
        self.carry(it["uid"], f"pipes:{pid}")

    def do_bar(self, it: dict) -> None:
        bid = "r_" + ident(it["uid"].split(":", 1)[-1])
        reads = it.get("reads") or []
        if not reads:
            self.findings.append(f"{it['uid']}: a bar without a tag")
            return
        self.arrays["bars"].append({"id": bid, **self.box(it), "value": self.ctx.signal(reads[0], "Float8"),
                                    **{k: v for k, v in (("unit", ctx_units(self.ctx, reads)), ("format", self.ctx.display(reads).get("format")))
                                       if v}})
        self.carry(it["uid"], f"bars:{bid}")

    def do_trend(self, it: dict) -> None:
        tid = "t_" + ident(it["uid"].split(":", 1)[-1])
        pens = [{"tag": self.ctx.signal(t, "Float8"), "label": t} for t in (it.get("reads") or [])[:2]]
        self.arrays["trends"].append({"id": tid, **self.box(it), "title": it.get("label") or "Trend", "minutes": 60,
                                      "pens": pens})
        self.carry(it["uid"], f"trends:{tid}")

    def do_alarm_panel(self, it: dict) -> None:
        aid = "a_" + ident(it["uid"].split(":", 1)[-1])
        self.arrays["alarmPanels"].append({"id": aid, **self.box(it), "sources": [self.ctx.root]})
        self.carry(it["uid"], f"alarmPanels:{aid}")

    def descriptor(self) -> dict:
        ctx, p, d = self.ctx, self.page, self.design
        w, h = d["canvas"]["w"], d["canvas"]["h"]
        node = node_path(ctx.model, p["node"])
        sections = [{"id": ident("sec_" + r["id"]), **{k: r["bbox"][k] for k in ("x", "y", "w", "h")}}
                    for r in d.get("regions", [])]
        screen = {"id": ident(p["id"]), "route": p["route"], "title": p["title"], "view": f"Screens/{ident(p['id'])}",
                  "layout": "diagram", "width": w, "height": h, "icon": "dashboard", "nav": True,
                  "navLabel": p["title"], "node": node, "fit": ctx.args.fit,
                  "level": LEVEL_WORD.get(p["level"], f"Level {p['level']}")}
        if p.get("previous"):
            screen["previous"] = p["previous"]
        if p.get("next"):
            screen["next"] = p["next"]
        desc = {"schema": "cadre-hmi-screen/1", "screen": screen, "tagRoot": ctx.args.tag_root, "tagModel": "external",
                "toolbar": True, "showTags": True, "sections": sections}
        for k, v in self.arrays.items():
            if v:
                desc[k] = v
        return desc


def stub_descriptor(ctx: Context, p: dict) -> dict:
    screen = {"id": ident(p["id"]), "route": p["route"], "title": p["title"], "view": f"Screens/{ident(p['id'])}",
              "layout": "diagram", "width": 1580, "height": 600, "icon": "dashboard", "nav": True,
              "navLabel": p["title"], "node": node_path(ctx.model, p["node"]), "fit": ctx.args.fit,
              "level": LEVEL_WORD.get(p["level"], f"Level {p['level']}")}
    return {"schema": "cadre-hmi-screen/1", "screen": screen, "tagRoot": ctx.args.tag_root, "tagModel": "external",
            "toolbar": False, "sections": [{"id": "stub", "x": 40, "y": 40, "w": 600, "h": 160}],
            "labels": [{"id": "title", "x": 60, "y": 60, "w": 560, "h": 32, "text": p["title"], "style": "heading"},
                       {"id": "note", "x": 60, "y": 110, "w": 560, "h": 60,
                        "text": "This display is outside the scope of the migration.", "style": "body"}]}


# ---- equal sizes ----------------------------------------------------------------------------------------------
def clusters(values: list[tuple[float, int]]) -> list[list[int]]:
    """Indexes grouped by a value within EQ_TOL of the group's first, in ascending order of value."""
    groups: list[list[int]] = []
    first = None
    for v, i in sorted(values):
        if groups and first is not None and v - first <= EQ_TOL:
            groups[-1].append(i)
        else:
            groups.append([i])
            first = v
    return groups


def equalise(desc: dict) -> None:
    """Items of one array and one kind that share an x (a column) get the widest width; sharing a y (a row), the
    tallest height. Sizes only grow, so no label loses room."""
    for array in ("symbols", "labels", "buttons", "links"):
        items = desc.get(array, [])
        by_kind: dict[str, list[dict]] = {}
        for it in items:
            if "w" in it:
                by_kind.setdefault(it.get("kind", array), []).append(it)
        for group in by_kind.values():
            for axis, size in (("x", "w"), ("y", "h")):
                for cl in clusters([(it[axis], i) for i, it in enumerate(group)]):
                    if len(cl) > 1:
                        top = max(group[i][size] for i in cl)
                        for i in cl:
                            group[i][size] = top


def columns_of(design: dict, desc: dict, page: str, item_el: dict[str, str]) -> list[dict]:
    """The stated columns of the design (`balance.columns`, lists of uids) with the widths the descriptor holds."""
    width = {}
    for array in ("symbols", "labels", "buttons", "links"):
        for it in desc.get(array, []):
            width[it["id"]] = it["w"]
    out = []
    for i, col in enumerate((design.get("balance") or {}).get("columns") or []):
        ids = [item_el[uid].split(":", 1)[1] for uid in col if uid in item_el]
        widths = [width[e] for e in ids if e in width]
        if widths:
            out.append({"page": page, "column": f"c{i + 1}", "widths": widths})
    return out


# ---- the build ------------------------------------------------------------------------------------------------
def walk_entries(ctx: Context, files: list[Path], bridge: Path) -> dict:
    args = ctx.args
    modes = []
    for mode in ("static", "dynamic"):
        effects = bridge / "walk" / f"effects-{mode}.json"
        provenance.write_json(effects, {"schema": "cadre-hmi-walk-effects/1"})
        argv = ["python", "tools/compare/walk.py", "plan"]
        for f in files:
            argv += ["--descriptor", f.as_posix()]
        argv += ["--devices-file", (bridge / "devices.json").as_posix(),
                 "--tags-file", (bridge / "tags_devices.json").as_posix(),
                 "--effects", effects.as_posix(), "--render", args.render, "--faceplate", args.faceplate,
                 "--out", (bridge / "walk" / "plans" / f"{args.project}-{mode}.json").as_posix()]
        modes.append({"mode": mode, "overlay": "imported" if mode == "dynamic" else "not imported",
                      "source_tags": None, "effects": effects.name, "plan": {"argv": argv}})
    return {"schema": "ctig.bridge.walk/1",
            "renderings": [{"render": args.render, "project": args.project, "base": "", "modes": modes}]}


def build(model: dict, designs: dict[str, dict], tables: dict, gaps: dict, accepted: set[str], args,
          out: Path) -> dict:
    profile = profile_for(args.parent)
    module = load(ROOT / "module" / "components.json", "module components")
    ctx = Context(model, tables, profile, module, gaps, accepted, args)
    bridge = out / "bridge"
    descs: dict[str, dict] = {}
    carried: dict[str, list[str]] = {}
    gap_of: dict[str, str] = {}
    findings: list[str] = []
    columns: list[dict] = []
    for p in model["pages"]:
        d = designs.get(p["id"])
        if not p["built"]:
            descs[p["id"]] = stub_descriptor(ctx, p)
            continue
        if d is None:
            findings.append(f"{p['id']}: no design for the page")
            descs[p["id"]] = stub_descriptor(ctx, p)
            continue
        if d["canvas"].get("scale", 1.0) > 1.0:
            findings.append(f"{p['id']}: the canvas scale {d['canvas']['scale']} is above 1.0")
        pb = PageBuilder(ctx, p, d)
        desc = pb.run()
        for it in d["items"]:    # a tag read but in neither map of the tables: said, never given a type or a unit
            for tag in dict.fromkeys(it.get("reads") or []):
                if tag not in ctx.vars:
                    findings.append(f"{it['uid']}: the tag {tag} is in neither the tables' devices nor its tags map")
        findings += pb.findings
        if args.equalise:
            equalise(desc)
        columns += columns_of(d, desc, p["id"], pb.item_el)
        carried.update(pb.carried)
        gap_of.update(pb.gap)
        descs[p["id"]] = desc
    # the symbols are now drawn: the device members they bound are known, so the tag model can be written
    full, devices_only = tag_model(ctx, args.simulation)
    device_rows = []
    drawn_own = {s["id"] for d in descs.values() for s in d.get("symbols", []) if s.get("device") is True}
    for tag, d in ctx.devices.items():
        if not ctx.has_folder(tag):
            continue
        members = {m: {"type": dt, "access": "read"} for m, (dt, _) in ctx.members.get(tag, {}).items()}
        row = {"id": ident(tag), "kind": d["kind"], "title": tag, "label": d["label"], "members": members,
               "faceplate": args.faceplate}
        if ident(tag) not in drawn_own:
            row["node"] = node_path(model, d["node"])
        device_rows.append(row)
    bench = None
    if args.component_test:
        from hmi.screen import load_contracts
        bench = testbench.build(load_contracts(), profile_for(args.parent), args.tag_root)
        have = {r["id"] for r in device_rows}
        device_rows += [r for r in bench.devices if r["id"] not in have]
    devices_doc = {"schema": "cadre-hmi-devices/1", "tagRoot": args.tag_root, "devices": device_rows}

    # files
    files = []
    for pid, desc in descs.items():
        files.append(provenance.write_json(bridge / "descriptors" / f"{slug(pid)}.json", desc))
    if bench is not None:
        files.append(provenance.write_json(bridge / "descriptors" / "component-test.json", bench.descriptor))
    provenance.write_json(bridge / "devices.json", devices_doc)
    provenance.write_json(bridge / "tags_devices.json", devices_only)
    provenance.write_json(bridge / "tags.json", full)
    provenance.write_json(out / "tags-document.json", full)
    report = (bridge / "generator" / f"{args.project}.json").as_posix()
    argv = ["python", "tools/hmi/screen.py", "--project", args.project]
    for f in files:
        if f.name != "component-test.json":
            argv += ["--descriptor", f.as_posix()]
    argv += ["--app-name", args.app_name, "--alarm-scope", f"*{args.project}*",
             "--tags-file", (bridge / "tags.json").as_posix(), "--devices-file", (bridge / "devices.json").as_posix(),
             "--parent", args.parent, "--frame", args.frame, "--faceplate", args.faceplate, "--render", args.render]
    if args.component_test:
        argv += ["--component-test"]
    argv += ["--out", "build", "--report", report]
    provenance.write_json(bridge / "build.json", {"schema": "ctig.bridge.build/1", "renderings": [
        {"render": args.render, "project": args.project, "argv": argv, "report": report}]})
    provenance.write_json(bridge / "walk" / "walk.json", walk_entries(ctx, files, bridge))

    # coverage
    rows, missing = [], []
    for r in model["mapping"]:
        uid = r["uid"]
        by = list(carried.get(uid, []))
        gap = gap_of.get(uid)
        place = r["place"] or ""
        if place.startswith("dropped"):
            by = ["dropped"]
        elif place.startswith("frame"):
            by = ["frame"]
        elif place.startswith("faceplate "):
            dev = next((t for t, d in ctx.devices.items() if place.split()[1] == t or place.split()[1] == ident(t)), None)
            by = [f"devices:{ident(dev)}"] if dev and ctx.has_folder(dev) else []
        elif r["section"] == "navigation" and not by and any(
                n.get("uid") == uid and n["resolution"] == "not_migrated" for n in model["nav"]):
            by = ["nav:not_migrated"]
        elif r["section"] == "regions" and r["source"] in descs:
            by = [f"sections:{ident('sec_' + r['id'])}"] if any(
                s["id"] == ident("sec_" + r["id"]) for s in descs[r["source"]].get("sections", [])) else by
        gapped = gap if gap and (gap in ctx.gaps_open and ctx.gaps_open[gap]["status"] == "accepted") else None
        rows.append({"uid": uid, "carried_by": by, "gap": gap})
        if not by or (gap and gapped is None):
            missing.append(uid)
    routes, unresolved = [], []
    route_map = {}
    page_routes = {d["screen"]["route"] for d in descs.values()}
    for n in model["nav"]:
        res = n["resolution"]
        row = {"target": n["target"], "resolution": res}
        if res in ("page", "support"):
            row["route"] = n["route"]
            if res == "page" and n["route"] not in page_routes:
                unresolved.append({"target": n["target"], "reason": "no descriptor serves the route"})
        elif res == "faceplate":
            row["device"] = n["faceplate"]
            if n["faceplate"] not in ctx.devices:
                unresolved.append({"target": n["target"], "reason": "the faceplate's device is not in the model"})
        elif res is None:
            unresolved.append({"target": n["target"], "reason": n.get("reason") or "no resolution"})
        routes.append(row)
        route_map[f"{n['from']} -> {n['target']}"] = row
    coverage = {"schema": "cadre-hmi-descriptor-coverage/1", "rows": rows, "missing": missing, "routes": routes,
                "unresolved": unresolved, "module_first": sorted(ctx.kinds_used.values(), key=lambda r: r["kind"]),
                "columns": columns, "findings": findings,
                "gaps": sorted(ctx.gaps_open.values(), key=lambda g: g["id"])}
    open_gaps = [g for g in coverage["gaps"] if g["status"] != "accepted"]
    return {"coverage": coverage, "route_map": route_map, "open_gaps": open_gaps, "files": files, "ctx": ctx,
            "findings": findings}


def parse_window(text: str) -> tuple[int, int]:
    try:
        w, h = (int(n) for n in text.lower().split("x"))
    except ValueError:
        raise InputFault(f"--window is WIDTHxHEIGHT, not {text!r}") from None
    return w, h


def main(argv: list[str] | None = None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--model", required=True)
    ap.add_argument("--designs", required=True, metavar="LIST")
    ap.add_argument("--faceplates", default=None)
    ap.add_argument("--tables", required=True)
    ap.add_argument("--gaps", default=None)
    ap.add_argument("--accepted", default=None)
    ap.add_argument("--inventory", default=None, metavar="DIR")
    ap.add_argument("--project", required=True)
    ap.add_argument("--parent", required=True)
    ap.add_argument("--tag-root", required=True, metavar="[provider]folder")
    ap.add_argument("--window", default="1920x1080")
    ap.add_argument("--render", choices=("stock", "module"), default="module")
    ap.add_argument("--frame", default="asm")
    ap.add_argument("--faceplate", default="asm")
    ap.add_argument("--app-name", default="ASM HMI")
    ap.add_argument("--fit", default=None, help="the fit as JSON, default " + json.dumps(DEFAULT_FIT))
    for flag in ("module-first", "equalise", "medium", "simulation", "component-test"):
        ap.add_argument("--" + flag, action="store_true")
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args_line = sys.argv[1:] if argv is None else list(argv)
    try:
        if not a.project.startswith("cadre_hmi"):
            raise InputFault(f"--project {a.project!r} must start with cadre_hmi")
        if not re.fullmatch(r"\[[^\]]+\][^/].*[^/]", a.tag_root):
            raise InputFault(f"--tag-root is [provider]folder, not {a.tag_root!r}")
        parse_window(a.window)
        a.fit = json.loads(a.fit) if a.fit else dict(DEFAULT_FIT)
        model = load(a.model, "model")
        if model.get("schema") != "cadre-hmi-asm-model/1":
            raise InputFault(f"model: {a.model}: not a cadre-hmi-asm-model/1 document")
        designs = {}
        for p in path_list(a.designs):
            d = load(p, "design")
            if "page" not in d or "items" not in d or "canvas" not in d:
                raise InputFault(f"design: {p}: no page, canvas and items")
            designs[d["page"]] = d
        tables = load(a.tables, "tables")
        gaps = load(a.gaps, "gaps") if a.gaps else {}
        accepted = set(read_accepted(a.accepted))
        out = Path(a.out)
        result = build(model, designs, tables, gaps, accepted, a, out)
    except InputFault as e:
        print(f"asm_descriptors: {e}")
        return 1
    cov = result["coverage"]
    cov["provenance"] = clock.provenance(TOOL, args_line, [Path(a.model), Path(a.designs), Path(a.tables)]
                                         + [Path(x) for x in (a.gaps, a.accepted, a.faceplates) if x])
    provenance.write_json(out / "coverage.json", cov)
    provenance.write_json(out / "bridge" / "coverage_map.json", {r["uid"]: r for r in cov["rows"]})
    provenance.write_json(out / "bridge" / "route_map.json", result["route_map"])
    provenance.write_json(out / "gaps-after.json", {"open": result["open_gaps"]})
    wide = [c for c in cov["columns"] if c["widths"] and max(c["widths"]) - min(c["widths"]) > EQ_TOL]
    bad = bool(cov["missing"] or cov["unresolved"] or result["open_gaps"] or wide or result["findings"])
    print(f"asm_descriptors: rows {len(cov['rows'])}, carried {len(cov['rows']) - len(cov['missing'])}, "
          f"missing {len(cov['missing'])}, routes {len(cov['routes'])}, unresolved {len(cov['unresolved'])}, "
          f"open gaps {len(result['open_gaps'])}, unequal columns {len(wide)}, findings {len(result['findings'])}")
    return 2 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
