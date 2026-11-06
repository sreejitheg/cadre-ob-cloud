"""Write `module/openbridge-elements.json` (`cadre-hmi-openbridge-elements/1`) from the pinned OpenBridge package.

NOTE-WFB-10 section 11.1 item 1. The list holds every declaration of the package's `custom-elements.json` that has
`customElement: true` and a `tagName`, in every group:

  tag         the declaration's `tagName`
  class       the declaration's `name`
  path        the module's `path` with `src/` replaced by `dist/` and `.ts` by `.js`
  group       the path's segment after `dist/`
  status      the first of stable, beta, experimental, deprecated found among the class's JSDoc tags, else null. The
              manifest does not carry the tags (only a `deprecated` key); they are in the package's `dist/**/*.d.ts`
              on the class declaration, which is read here, and a `deprecated` key counts as that tag
  properties  the declaration's `members` of kind `field` that are neither static nor private nor protected, each
              {name, type (type.text), enum (the string literals when type.text is a union of them, else null),
              default (the `default` text parsed as JSON where it parses, else the text)}

Elements and properties are sorted by tag and by name. The package is read only. Usage:

    python module/tools/gen_openbridge_elements.py [--package <dir>] [--out <file>]

`--package` is the installed `@oicl/openbridge-webcomponents` folder (default `module/web/node_modules/...` beside this
script); the pin check `verify_pin.py` is the guard that the folder is the pinned release.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_pin  # noqa: E402

MODULE = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = MODULE / "web" / "node_modules" / "@oicl" / "openbridge-webcomponents"
DEFAULT_OUT = MODULE / "openbridge-elements.json"
# The commit of the pinned release (NOTICE, COBD-003).
COMMIT = "2c98dda1ac33b2a931bea2532fc78961f097e548"
STATUSES = ("stable", "beta", "experimental", "deprecated")
LITERAL = re.compile(r"""^(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")$""")


def string_union(text) -> list | None:
    """The string literals of a union type text such as `'a' | 'b'`, else None."""
    if not isinstance(text, str) or "'" not in text and '"' not in text:
        return None
    parts = [p.strip() for p in text.split("|")]
    out = []
    for p in parts:
        m = LITERAL.match(p)
        if not m:
            return None
        out.append(m.group(1) if m.group(1) is not None else m.group(2))
    return out


def parse_default(text):
    """The `default` text parsed as JSON where it parses to a JSON value, else the text: `NaN` and `Infinity` parse in
    Python but are not JSON, so they stay text and the list stays strict JSON."""
    if text is None:
        return None
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return text
    if isinstance(value, float) and not math.isfinite(value):
        return text
    return value


def class_status(package: Path, js_path: str, decl: dict) -> str | None:
    tags = set()
    if decl.get("deprecated"):
        tags.add("deprecated")
    dts = package / (js_path[:-3] + ".d.ts")
    if dts.is_file():
        text = dts.read_text(encoding="utf-8")
        at = text.find(f"export declare class {decl['name']}")
        start = text.rfind("/**", 0, at) if at >= 0 else -1
        # Only the comment block that ends right before the class counts.
        if start >= 0 and text[text.rfind("*/", 0, at) + 2:at].strip() == "":
            tags.update(re.findall(r"@(stable|beta|experimental|deprecated)\b", text[start:at]))
    return next((s for s in STATUSES if s in tags), None)


def properties(decl: dict) -> list:
    out: dict = {}
    for m in decl.get("members", []):
        if m.get("kind") != "field" or m.get("static") or m.get("privacy") in ("private", "protected"):
            continue
        name = m["name"]
        if name in out:
            continue
        text = (m.get("type") or {}).get("text")
        out[name] = {"name": name, "type": text, "enum": string_union(text), "default": parse_default(m.get("default"))}
    return [out[k] for k in sorted(out)]


def build(package: Path) -> dict:
    pkg = json.loads((package / "package.json").read_text(encoding="utf-8"))
    if pkg.get("version") != verify_pin.VERSION:
        raise SystemExit(f"{package}: version {pkg.get('version')!r} is not the pin {verify_pin.VERSION!r}")
    manifest = json.loads((package / "custom-elements.json").read_text(encoding="utf-8"))
    elements = []
    for mod in manifest["modules"]:
        for d in mod.get("declarations", []):
            if d.get("customElement") is True and d.get("tagName"):
                path = re.sub(r"\.ts$", ".js", mod["path"].replace("src/", "dist/", 1))
                elements.append({
                    "tag": d["tagName"], "class": d["name"], "path": path, "group": path.split("/")[1],
                    "status": class_status(package, path, d), "properties": properties(d)})
    elements.sort(key=lambda e: e["tag"])
    tags = [e["tag"] for e in elements]
    if len(tags) != len(set(tags)):
        raise SystemExit("a tag is declared twice in custom-elements.json")
    return {"release": verify_pin.VERSION, "commit": COMMIT, "elements": elements}


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--package", type=Path, default=DEFAULT_PACKAGE, help="the installed OpenBridge package folder")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args(argv)
    doc = build(a.package)
    a.out.write_bytes((json.dumps(doc, indent=1, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))
    print(f"wrote {a.out}: {len(doc['elements'])} elements, release {doc['release']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
