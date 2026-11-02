"""Convert an OpenStudio connector-diagram view into a Cadre HMI screen descriptor.

The mapping is the reusable part: an OpenStudio design (a `view.json` whose root, or child,
is `openbridge.manual.connector-diagram`) becomes our descriptor, so the Cadre generator can
rebuild it on the stock parent library. Component mapping (wiki page 05 section 3):

    automation.automation-tank.automation-tank    -> tank
    automation.digital-valve.digital-valve, valve -> valve        (open)
    automation.analog-valve.analog-valve          -> analogvalve  (open, value)
    automation.pump.pump                          -> pump         (on, speed)
    automation.motor.motor, fan.fan               -> motor, fan
    ia.display.view of a symbol sub-view          -> the kind of the symbol inside it
    connections                                   -> pipes (component side, junction node, free end)
    nodes                                         -> junctions;  zones -> sections

States: a symbol in the vendor demo reads its state from tags this repository does not have.
`--state` supplies the states observed on the running demo, which become the test tag values.
The converted descriptor contains vendor layout facts, so it is written under `workspace/`
(local only, decision COBD-007).

Usage:
    python tools/import_openstudio.py --view <view.json> --views-root <views dir> --state <state.json>
        --route / --title "Process Overview" --tag-root "[default]cadre_hmi_demo/process"
        --out workspace/fixtures/process-overview.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TYPE_KIND = {
    "automation.automation-tank.automation-tank": "tank",
    "automation.digital-valve.digital-valve": "valve",
    "automation.valve.valve": "valve",
    "automation.analog-valve.analog-valve": "analogvalve",
    "automation.pump.pump": "pump",
    "automation.motor.motor": "motor",
    "automation.fan.fan": "fan",
}
LEVEL_TO_STATUS = {"level-critical": "alarm", "level-high": "alarm", "level-medium": "warning",
                   "level-low": "caution", "alarm": "alarm", "warning": "warning", "caution": "caution"}
MEDIUM = {"neutral": "neutral", "warm": "hot", "cold": "cold", "fresh-water": "fresh-water"}


def inner_kind(views_root: Path, path: str) -> str | None:
    f = views_root / path / "view.json"
    if not f.exists():
        return None
    v = json.loads(f.read_text(encoding="utf-8"))
    stack = [v["root"]]
    while stack:
        n = stack.pop()
        if n.get("type") in TYPE_KIND:
            return TYPE_KIND[n["type"]]
        stack.extend(n.get("children") or [])
    return None


def convert(view: dict, views_root: Path, state: dict, route: str, title: str, tag_root: str) -> dict:
    root = view["root"]
    diag = root if root.get("type") == "openbridge.manual.connector-diagram" else next(
        c for c in root.get("children", []) if c.get("type") == "openbridge.manual.connector-diagram")
    size = view.get("props", {}).get("defaultSize", {})
    desc = {"schema": "cadre-hmi-screen/1",
            "screen": {"id": title.replace(" ", ""), "route": route, "title": title,
                       "view": "Screens/" + title.replace(" ", ""), "layout": "diagram",
                       "width": size.get("width", 1600), "height": size.get("height", 852),
                       "icon": "dashboard"},
            "tagRoot": tag_root, "toolbar": True, "sections": [], "symbols": [], "junctions": [],
            "pipes": [], "tagValues": {}, "unmapped": []}
    for zid, z in (diag["props"].get("zones") or {}).items():
        desc["sections"].append({"id": zid, "x": z["x"], "y": z["y"], "w": z["w"], "h": z["h"],
                                 "label": z.get("label", "")})
    tanks = iter(sorted(state.get("tanks", {}).items(), key=lambda kv: int(kv[0])))
    for i, ch in enumerate(diag.get("children", [])):
        name, pos, props = ch["meta"]["name"], ch["position"], ch.get("props", {})
        t = ch["type"]
        kind = TYPE_KIND.get(t) or (inner_kind(views_root, props.get("path", "")) if t == "ia.display.view" else None)
        if not kind:
            desc["unmapped"].append({"name": name, "type": t})
            continue
        sym = {"id": name, "kind": kind, "x": pos["x"], "y": pos["y"], "w": pos.get("width", 48),
               "h": pos.get("height", 48), "params": {}, "bind": {}, "device": kind != "tank"}
        st = state.get({"tank": "tanks", "valve": "valves", "pump": "pumps"}.get(kind, ""), {}).get(str(i), {})
        if kind == "tank":
            sym["params"] = {"max": st.get("max", props.get("max", 100)), "tag": st.get("tag", props.get("tag", "")),
                             "trend": st.get("trend", "stable"), "compact": bool(st.get("compact", props.get("compact", False))),
                             "static": bool(props.get("static", False)),
                             "unit": props.get("unitText", "m³") if props.get("hasCustomUnit") and props.get("unitText") else "m³"}
            if props.get("chartData"):
                sym["params"]["chart"] = True
                sym["params"]["history"] = [d.get("value", 0) for d in props["chartData"]]
            sym["bind"] = {"value": f"{name}/level"}
            desc["tagValues"][f"{name}/level"] = st.get("value", props.get("value", 0))
            sym["device"] = False
        elif kind in ("valve", "analogvalve"):
            sym["params"] = {"readoutPosition": st.get("readoutPosition", "bottom"),
                             "vertical": bool(st.get("vertical", False)),
                             "badgeControl": st.get("badgeControl", "none")}
            sym["bind"] = {"open": f"{name}/state"}
            desc["tagValues"][f"{name}/state"] = bool(st.get("open", False))
        elif kind == "pump":
            # The running state is `on`; `direction` is only the direction icon. Where `on` was not
            # captured, a readout showing a speed means running (OpenBridge draws the speed only when on).
            running = bool(st["on"]) if "on" in st else st.get("speed") is not None
            sym["params"] = {"readoutPosition": "bottom", "hasSpeed": True, "variant": "double",
                             "badgeControl": st.get("badgeControl", "none"),
                             "alert": bool(st.get("alert", False)),
                             "alertFrameStatus": LEVEL_TO_STATUS.get(st.get("alertFrameStatus", "alarm"), "alarm"),
                             "alertFrameMode": st.get("alertFrameMode", "acked-active")}
            sym["bind"] = {"on": f"{name}/state", "speed": f"{name}/speed"}
            desc["tagValues"][f"{name}/state"] = running
            desc["tagValues"][f"{name}/speed"] = st.get("speed", 0)
        desc["symbols"].append(sym)
    for nid, n in (diag["props"].get("nodes") or {}).items():
        desc["junctions"].append({"id": nid, "x": n["x"], "y": n["y"]})
    for cid, c in (diag["props"].get("connections") or {}).items():
        ends = []
        for k in ("from", "to"):
            e = c[k]
            if "componentId" in e:
                ends.append({"ref": e["componentId"], "side": e.get("direction", "top"), "x": e["x"], "y": e["y"]})
            elif e.get("kind") == "node":
                ends.append({"ref": e["nodeId"], "x": e["x"], "y": e["y"]})
            else:
                ends.append({"x": e["x"], "y": e["y"], "end": e.get("terminal", "cap")})
        via = [(p["x"], p["y"]) for p in (c.get("path") or c.get("viaPoints") or [])]
        pts = [(ends[0]["x"], ends[0]["y"]), (ends[1]["x"], ends[1]["y"])]
        via = [v for v in via if v not in pts]
        pipe = {"id": cid, "from": ends[0], "to": ends[1], "medium": MEDIUM.get(c.get("mediumId", "neutral"), "neutral")}
        if via:
            pipe["via"] = via
        if c.get("state") == "closed":
            pipe["state"] = "closed"
        desc["pipes"].append(pipe)
    return desc


LEAF_KIND = {"navigation-instruments.instrument-field.instrument-field": "instrument-field",
             "navigation-instruments.readout.readout": "instrument-field",
             "automation.pump.pump": "pump", "automation.motor.motor": "motor", "automation.fan.fan": "fan",
             "automation.digital-valve.digital-valve": "valve", "automation.valve.valve": "valve",
             "automation.automation-tank.automation-tank": "tank"}


def convert_cards(view: dict, state: dict, route: str, title: str, tag_root: str, screen_id: str) -> dict:
    """A vendor card page (flex rows of `openbridge.manual.card`) as a cards-layout descriptor.
    Flex containers become groups, instrument fields and symbols become library leaves, labels
    stay labels; any other vendor component becomes a leaf of its own kind, which the generator
    draws as a counted gap box. Live values are matched by document order."""
    fields = iter(state.get("instrumentFields", []))
    pumps = iter(state.get("pumps", []))
    desc = {"schema": "cadre-hmi-screen/1",
            "screen": {"id": screen_id, "route": route, "title": title, "view": f"Screens/{screen_id}",
                       "layout": "cards", "width": 1600, "height": 852, "icon": "home"},
            "tagRoot": tag_root, "rows": [], "tagValues": {}}
    counter = {"n": 0}

    def flexpos(n):
        p = n.get("position", {})
        out = {}
        if "basis" in p:
            out["basis"] = str(p["basis"])
        if "grow" in p:
            out["grow"] = p["grow"]
        return out

    def leaf(n):
        t = n["type"]
        if t == "ia.display.label":
            return {"label": (n.get("props") or {}).get("text", ""), **flexpos(n)}
        if t == "ia.container.flex":
            return group(n)
        counter["n"] += 1
        kind = LEAF_KIND.get(t, t.split(".")[-1])
        item = {"id": f"{kind.replace('-', '_')}_{counter['n']}", "kind": kind, **flexpos(n)}
        if kind == "instrument-field":
            st = next(fields, {})
            v = st.get("value", (n.get("props") or {}).get("value", 0))
            item["params"] = {"label": st.get("tag", ""), "unit": st.get("unit", (n.get("props") or {}).get("unit", "")),
                              "size": "enhanced", "format": "0" if float(v).is_integer() else "0.0"}
            member = f"{item['id']}/value"
            item["bind"] = {"value": member}
            desc["tagValues"][member] = v
        elif kind == "pump":
            st = next(pumps, {})
            item["params"] = {"readoutPosition": "bottom", "hasSpeed": True}
            for k in ("alert", "alertFrameStatus", "alertFrameMode"):
                if k in st:
                    item["params"][k] = st[k]
            item["bind"] = {"on": f"{item['id']}/state", "speed": f"{item['id']}/speed"}
            item["device"] = True
            desc["tagValues"][f"{item['id']}/state"] = bool(st.get("on", False))
            desc["tagValues"][f"{item['id']}/speed"] = st.get("speed", 0)
        return item

    def group(n):
        g = {"direction": (n.get("props") or {}).get("direction", "row"), **flexpos(n),
             "items": [leaf(c) for c in n.get("children", []) or []]}
        if g["direction"] not in ("row", "column"):
            g["direction"] = "row"
        return g

    for r, row in enumerate(view["root"].get("children", [])):
        cards = []
        for c, card in enumerate(row.get("children", []) or []):
            if card.get("type") != "openbridge.manual.card":
                continue
            body = (card.get("children") or [{}])[0]
            cards.append({"id": f"r{r}c{c}", "title": (card.get("props") or {}).get("title", ""),
                          **flexpos(card), "body": group(body) if body else {"items": []}})
        if cards:
            desc["rows"].append(cards)
    return desc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--view", required=True)
    ap.add_argument("--views-root", required=True)
    ap.add_argument("--layout", choices=["diagram", "cards"], default="diagram")
    ap.add_argument("--screen-id", default=None)
    ap.add_argument("--state", default=None)
    ap.add_argument("--route", default="/")
    ap.add_argument("--title", required=True)
    ap.add_argument("--tag-root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    view = json.loads(Path(a.view).read_text(encoding="utf-8"))
    state = json.loads(Path(a.state).read_text(encoding="utf-8")) if a.state else {}
    if a.layout == "cards":
        desc = convert_cards(view, state, a.route, a.title, a.tag_root, a.screen_id or a.title.replace(" ", ""))
    else:
        desc = convert(view, Path(a.views_root), state, a.route, a.title, a.tag_root)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(desc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if a.layout == "cards":
        print(f"rows {len(desc['rows'])}, cards {sum(len(r) for r in desc['rows'])}, tag values {len(desc['tagValues'])}")
    else:
        print(f"symbols {len(desc['symbols'])}, junctions {len(desc['junctions'])}, pipes {len(desc['pipes'])}, "
              f"sections {len(desc['sections'])}, unmapped {len(desc['unmapped'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
