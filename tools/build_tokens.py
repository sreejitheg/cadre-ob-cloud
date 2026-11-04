"""Extract the package design tokens from the pinned Apache-2.0 stylesheet.

Input is `src/palettes/variables.css` of `@oicl/openbridge-webcomponents` 2.0.0-next.155
(commit 2c98dda1, Apache-2.0; see NOTICE and decisions COBD-003). Output is a JSON token
file the parent project generator reads:

    global       the `*` block: font sizes, line heights, font family, spacing
    sizes        one map per component size (regular, medium, large, xl)
    palettes     one map per palette (day, dusk, night, bright)

Data URI icon tokens (`--icon-*: url(data:...)`) are dropped: they are images, not tokens,
and our icons come from the icon converter.

Usage:
    python tools/build_tokens.py --css reference/openbridge-webcomponents-2.0.0-next.155/palettes/variables.css \
        --out library/tokens/openbridge-tokens.json
"""
import argparse
import hashlib
import json
import pathlib
import re

PIN = {"package": "@oicl/openbridge-webcomponents", "version": "2.0.0-next.155",
       "commit": "2c98dda1ac33b2a931bea2532fc78961f097e548",
       "file": "packages/openbridge-webcomponents/src/palettes/variables.css",
       "licence": "Apache-2.0", "copyright": "Copyright 2024 OICL"}

VAR_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);")
REF_RE = re.compile(r"var\(\s*(--[\w-]+)")


def norm(v: str) -> str:
    """Collapse whitespace, and `var( --x )` to `var(--x)`."""
    v = " ".join(v.split())
    return re.sub(r"var\(\s*(--[\w-]+)\s*\)", lambda m: "var(" + m.group(1) + ")", v)


def parse(css: str) -> dict:
    out = {"global": {}, "sizes": {}, "palettes": {}}
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        sel = " ".join(sel.split())
        decls = {n: norm(v) for n, v in VAR_RE.findall(body)}
        decls = {n: v for n, v in decls.items() if not v.startswith("url(")}
        if not decls:
            continue
        if sel == "*":
            out["global"].update(decls)
            continue
        m = re.search(r"obc-component-size-(\w+)", sel)
        if m:
            out["sizes"][m.group(1)] = decls
            continue
        m = re.search(r'data-obc-theme="(\w+)"', sel)
        if m:
            out["palettes"][m.group(1)] = decls
    return out


def closure(names, *maps) -> set:
    """Every variable reachable from `names` through var() references in any of `maps`."""
    seen, todo = set(), list(names)
    while todo:
        n = todo.pop()
        if n in seen:
            continue
        seen.add(n)
        for m in maps:
            v = m.get(n)
            if v:
                todo.extend(REF_RE.findall(v))
    return seen


def parse_fonts(css: str) -> dict:
    """`@define-mixin font-<name> { prop: value; ... }` from src/mixins/fonts.css, as
    camelCase style maps; `font-feature-settings` is dropped (cosmetic, multi-line)."""
    out = {}
    for name, body in re.findall(r"@define-mixin font-([\w-]+)\s*\{(.*?)\}", css, re.S):
        decl = {}
        for prop, val in re.findall(r"([\w-]+)\s*:\s*([^;]+);", body):
            if prop == "font-feature-settings":
                continue
            camel = re.sub(r"-(\w)", lambda m: m.group(1).upper(), prop)
            decl[camel] = norm(val)
        if decl:
            out[name] = decl
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--css", required=True)
    ap.add_argument("--fonts", help="src/mixins/fonts.css of the same commit")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = pathlib.Path(a.css).read_bytes()
    tokens = parse(raw.decode("utf-8"))
    if a.fonts:
        tokens["fonts"] = parse_fonts(pathlib.Path(a.fonts).read_text(encoding="utf-8"))
    tokens = {"meta": dict(PIN, sha256=hashlib.sha256(raw).hexdigest()), **tokens}
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tokens, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print("global", len(tokens["global"]), "| sizes",
          {k: len(v) for k, v in tokens["sizes"].items()}, "| palettes",
          {k: len(v) for k, v in tokens["palettes"].items()}, "|", out.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
