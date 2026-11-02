"""Convert OpenBridge icons into `ia.shapes.svg` element lists.

Source: `@oicl/openbridge-webcomponents` 2.0.0-next.155, commit 2c98dda1, Apache-2.0
(NOTICE; decision COBD-003). Each `src/icons/icon-<name>.ts` carries two SVG bodies:
`icon` (every fill `currentColor`) and `iconCss` (each fill a palette variable such as
`var(--automation-device-primary-color)`). The palette-aware `iconCss` is converted;
an icon without one falls back to `icon`, with `currentColor` mapped to the
`--element-active-color` palette variable.

Output elements use only attested shapes (IGW:components/ia.shapes.svg and
IGW:06-bindings section 5): `type`, `d`, `fill.paint`, `fill.rule`, `stroke.paint`,
`stroke.width`, `transform`, and `group` with `elements`. Circles, ellipses, rects,
lines and polygons are rewritten as path data, so no unattested attribute is emitted.

Usage:
    python tools/convert_icons.py --names-file library/icons/ICONS.txt --out library/icons
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SHA = "2c98dda1ac33b2a931bea2532fc78961f097e548"
RAW = ("https://raw.githubusercontent.com/Ocean-Industries-Concept-Lab/openbridge-webcomponents/"
       f"{SHA}/packages/openbridge-webcomponents/src/icons/icon-{{name}}.ts")
CACHE = Path("reference/openbridge-webcomponents-2.0.0-next.155/src/icons")
NS = "{http://www.w3.org/2000/svg}"
CURRENT = "var(--element-active-color)"


def fetch(name: str) -> str:
    f = CACHE / f"icon-{name}.ts"
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(RAW.format(name=name), timeout=30) as r:
            f.write_bytes(r.read())
        time.sleep(0.05)
    return f.read_text(encoding="utf-8")


def svg_body(ts: str, which: str) -> str | None:
    m = re.search(rf"private {which} = svg`(.*?)`;", ts, re.S)
    return m.group(1).strip() if m else None


def num(v) -> float:
    return float(str(v).replace("px", "")) if v not in (None, "") else 0.0


def f(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def shape_to_d(tag: str, a: dict) -> str | None:
    if tag == "path":
        return a.get("d")
    if tag in ("circle", "ellipse"):
        cx, cy = num(a.get("cx")), num(a.get("cy"))
        rx = num(a.get("r")) if tag == "circle" else num(a.get("rx"))
        ry = num(a.get("r")) if tag == "circle" else num(a.get("ry"))
        return (f"M{f(cx - rx)} {f(cy)}a{f(rx)} {f(ry)} 0 1 0 {f(2 * rx)} 0"
                f"a{f(rx)} {f(ry)} 0 1 0 {f(-2 * rx)} 0Z")
    if tag == "rect":
        x, y, w, h = num(a.get("x")), num(a.get("y")), num(a.get("width")), num(a.get("height"))
        rx = num(a.get("rx") or a.get("ry"))
        if rx <= 0:
            return f"M{f(x)} {f(y)}H{f(x + w)}V{f(y + h)}H{f(x)}Z"
        rx = min(rx, w / 2, h / 2)
        return (f"M{f(x + rx)} {f(y)}H{f(x + w - rx)}A{f(rx)} {f(rx)} 0 0 1 {f(x + w)} {f(y + rx)}"
                f"V{f(y + h - rx)}A{f(rx)} {f(rx)} 0 0 1 {f(x + w - rx)} {f(y + h)}"
                f"H{f(x + rx)}A{f(rx)} {f(rx)} 0 0 1 {f(x)} {f(y + h - rx)}"
                f"V{f(y + rx)}A{f(rx)} {f(rx)} 0 0 1 {f(x + rx)} {f(y)}Z")
    if tag == "line":
        return f"M{f(num(a.get('x1')))} {f(num(a.get('y1')))}L{f(num(a.get('x2')))} {f(num(a.get('y2')))}"
    if tag in ("polygon", "polyline"):
        pts = re.split(r"[\s,]+", a.get("points", "").strip())
        pairs = [(pts[i], pts[i + 1]) for i in range(0, len(pts) - 1, 2)]
        if not pairs:
            return None
        d = "M" + " L".join(f"{x} {y}" for x, y in pairs)
        return d + ("Z" if tag == "polygon" else "")
    return None


def paint_of(a: dict, prop: str) -> str | None:
    style = a.get("style", "")
    m = re.search(rf"(?:^|;)\s*{prop}\s*:\s*([^;]+)", style)
    v = (m.group(1).strip() if m else a.get(prop))
    if v is None:
        return None
    v = v.strip()
    if v == "currentColor":
        return CURRENT
    return v


def convert_el(el, inherited_fill: str | None, vars_used: set) -> dict | None:
    tag = el.tag.replace(NS, "")
    a = dict(el.attrib)
    if tag in ("defs", "title", "desc", "clipPath", "mask"):
        return None
    fill = paint_of(a, "fill") or inherited_fill
    if tag == "g":
        kids = [k for k in (convert_el(c, fill, vars_used) for c in el) if k]
        if not kids:
            return None
        g = {"type": "group", "elements": kids}
        if a.get("transform"):
            g["transform"] = a["transform"]
        return g
    d = shape_to_d(tag, a)
    if not d:
        return None
    out = {"type": "path", "d": d}
    if fill and fill != "none":
        out["fill"] = {"paint": fill}
        rule = a.get("fill-rule")
        if rule in ("evenodd", "nonzero"):
            out["fill"]["rule"] = rule
    else:
        out["fill"] = {"paint": "none"}
    stroke = paint_of(a, "stroke")
    if stroke and stroke != "none":
        out["stroke"] = {"paint": stroke}
        if a.get("stroke-width"):
            out["stroke"]["width"] = a["stroke-width"]
    if a.get("transform"):
        out["transform"] = a["transform"]
    for p in (out.get("fill", {}).get("paint"), out.get("stroke", {}).get("paint")):
        if p:
            vars_used.update(re.findall(r"var\((--[\w-]+)", p))
    return out


def convert(name: str) -> dict:
    ts = fetch(name)
    body = svg_body(ts, "iconCss")
    mode = "iconCss"
    if body is None:
        body, mode = svg_body(ts, "icon"), "icon"
    if body is None:
        raise ValueError(f"{name}: no svg body")
    root = ET.fromstring(body)
    vars_used: set = set()
    root_fill = paint_of(dict(root.attrib), "fill")
    if root_fill == "none":
        root_fill = None
    els = [e for e in (convert_el(c, root_fill, vars_used) for c in root) if e]
    return {"name": name, "viewBox": root.attrib.get("viewBox", "0 0 24 24"), "mode": mode,
            "vars": sorted(vars_used), "elements": els,
            "source": {"file": f"src/icons/icon-{name}.ts", "commit": SHA, "licence": "Apache-2.0"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--names-file", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    names = [n.strip() for n in Path(a.names_file).read_text().split() if n.strip()]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    index, failed = {}, []
    for n in sorted(set(names)):
        try:
            ic = convert(n)
        except Exception as e:  # recorded, never silent
            failed.append((n, str(e)[:120]))
            continue
        (out / f"{n}.json").write_text(json.dumps(ic, indent=1) + "\n", encoding="utf-8")
        index[n] = {"vars": ic["vars"], "mode": ic["mode"], "elements": len(ic["elements"])}
    (out / "index.json").write_text(json.dumps({"source_commit": SHA, "licence": "Apache-2.0",
                                                "icons": index, "failed": failed}, indent=1) + "\n",
                                    encoding="utf-8")
    print(f"converted {len(index)} icons, failed {len(failed)}: {failed[:5]}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
