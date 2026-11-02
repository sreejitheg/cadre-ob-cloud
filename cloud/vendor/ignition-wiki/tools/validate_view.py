"""Validate a Perspective view.json against the emitted component schemas.

This is the point of the wiki made executable: a generated view can be checked
against the registry BEFORE it is deployed, rather than discovered to be wrong on
a gateway.

It is a targeted checker, not a general JSON Schema implementation, and it says
so. It asserts the defect classes that were actually measured in real projects
during the harvest:

  1. the component `type` exists in the registry
  2. no `props` key is written that the component schema does not declare, on a
     schema that closes itself with additionalProperties false
  3. no enumerated property carries a value outside its declared domain
  4. a child's `position` keys are those its PARENT container declares, which is
     the single most common defect in generated Perspective JSON
  5. a binding `type` is one of the seven declared, and its config keys are
     declared by that binding's schema
  6. a deprecated component is flagged

What it does NOT do: full JSON Schema evaluation, type coercion checks, or any
judgement about whether the view is sensible. A clean result means the view is
structurally admissible, not that it is correct.

Usage:
    python tools/validate_view.py <view.json> [more.json ...]
    python tools/validate_view.py --project <dir>     recurse a project tree

Exit 1 if any ERROR is found.

stdlib only. Python 3.9+.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent.parent
SCHEMA_DIR = HERE / "schemas"

BINDING_SCHEMAS = {
    "tag": "binding-tag", "property": "binding-property", "expr": "binding-expr",
    "expr-struct": "binding-expr-struct", "query": "binding-query",
    "tag-history": "binding-tag-history", "http": "binding-http",
}


def load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


class Registry:
    def __init__(self, schema_dir: Path):
        idx = load(schema_dir / "index.json")
        self.components = {c["component"]: c for c in idx["components"]}
        self.positions = load(schema_dir / "positions.json")["containers"]
        self.schema_dir = schema_dir
        self._cache: dict[str, Any] = {}
        self.bindings: dict[str, Any] = {}
        for key, name in BINDING_SCHEMAS.items():
            f = schema_dir / "bindings" / f"{name}.json"
            if f.exists():
                self.bindings[key] = load(f)

    def schema(self, cid: str) -> Any:
        if cid not in self._cache:
            rec = self.components.get(cid)
            self._cache[cid] = load(self.schema_dir / rec["schema"]) if rec else None
        return self._cache[cid]

    def position_keys(self, parent_type: str) -> set[str] | None:
        cps = self.positions.get(parent_type)
        if not isinstance(cps, dict):
            return None
        props = cps.get("properties")
        return set(props) if isinstance(props, dict) else None


def enum_map(schema: Any) -> dict[str, list]:
    """Top level properties that declare an enumerated domain."""
    out = {}
    for k, v in (schema.get("properties") or {}).items():
        if isinstance(v, dict) and isinstance(v.get("enum"), list):
            out[k] = v["enum"]
    return out


def check_node(node: Any, reg: Registry, findings: list, view: str,
               parent_type: str = "", path: str = "root") -> None:
    if not isinstance(node, dict):
        return

    def add(sev: str, code: str, detail: str) -> None:
        findings.append({"view": view, "node": path, "severity": sev,
                         "check": code, "detail": detail})

    ctype = node.get("type")
    if isinstance(ctype, str) and ctype:
        rec = reg.components.get(ctype)
        if rec is None:
            add("ERROR", "UNKNOWN_COMPONENT",
                f"'{ctype}' is not declared by any registry")
        else:
            if rec.get("deprecated"):
                add("WARNING", "DEPRECATED_COMPONENT",
                    f"'{ctype}' is flagged deprecated in the registry")
            schema = reg.schema(ctype) or {}
            declared = set((schema.get("properties") or {}).keys())
            closed = schema.get("additionalProperties") is False
            props = node.get("props")
            if isinstance(props, dict):
                for k in props:
                    if k not in declared:
                        add("ERROR" if closed else "WARNING", "UNDECLARED_PROP",
                            f"props.{k} is not declared by {ctype}"
                            + ("" if closed else "; the schema is open, so this is "
                                                 "undeclared rather than prohibited"))
                for k, allowed in enum_map(schema).items():
                    if k in props and isinstance(props[k], str) and props[k] not in allowed:
                        add("ERROR", "ENUM_VIOLATION",
                            f"props.{k} is {props[k]!r}; declared domain is {allowed}")

        # position is governed by the PARENT container
        pos = node.get("position")
        if isinstance(pos, dict) and parent_type:
            allowed_pos = reg.position_keys(parent_type)
            if allowed_pos is not None:
                for k in pos:
                    if k not in allowed_pos:
                        add("ERROR", "BAD_POSITION_KEY",
                            f"position.{k} is not declared by the parent "
                            f"{parent_type}; it declares {sorted(allowed_pos)}")

    # bindings
    pc = node.get("propConfig")
    if isinstance(pc, dict):
        for target, cfg in pc.items():
            if not isinstance(cfg, dict):
                continue
            b = cfg.get("binding")
            if not isinstance(b, dict):
                continue
            btype = b.get("type")
            if btype not in reg.bindings:
                add("ERROR", "UNKNOWN_BINDING_TYPE",
                    f"{target}: binding type {btype!r} is not one of "
                    f"{sorted(reg.bindings)}")
                continue
            bs = reg.bindings[btype]
            declared = set((bs.get("properties") or {}).keys())
            closed = bs.get("additionalProperties") is False
            conf = b.get("config")
            if isinstance(conf, dict):
                for k in conf:
                    if k not in declared:
                        add("ERROR" if closed else "WARNING", "UNDECLARED_BINDING_KEY",
                            f"{target}: {btype} binding sets {k!r}, not declared by "
                            f"{BINDING_SCHEMAS[btype]}.json")

    for i, child in enumerate(node.get("children") or []):
        check_node(child, reg, findings,
                   view, ctype if isinstance(ctype, str) else parent_type,
                   f"{path}/{i}")


def validate_view(path: Path, reg: Registry, findings: list) -> None:
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError) as e:
        findings.append({"view": str(path), "node": "", "severity": "ERROR",
                         "check": "UNREADABLE", "detail": str(e)})
        return
    if not isinstance(doc, dict) or "root" not in doc:
        findings.append({"view": str(path), "node": "", "severity": "ERROR",
                         "check": "NOT_A_VIEW", "detail": "no 'root' key"})
        return
    check_node(doc["root"], reg, findings, str(path))


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if not (SCHEMA_DIR / "index.json").exists():
        print(f"no schemas at {SCHEMA_DIR}. Run tools/emit_schemas.py first.",
              file=sys.stderr)
        return 2
    reg = Registry(SCHEMA_DIR)

    targets: list[Path] = []
    if argv[0] == "--project":
        for d in argv[1:]:
            found = sorted(Path(d).rglob("view.json"))
            if not found:
                # A harvested corpus stores view documents under content
                # addressed names rather than as view.json, so fall back to any
                # JSON file that actually carries a root node.
                found = [f for f in sorted(Path(d).rglob("*.json"))
                         if f.name not in ("index.json", "positions.json")]
            targets.extend(found)
    else:
        targets = [Path(a) for a in argv]

    findings: list = []
    for t in targets:
        validate_view(t, reg, findings)

    errors = [f for f in findings if f["severity"] == "ERROR"]
    warns = [f for f in findings if f["severity"] == "WARNING"]
    print(f"views checked: {len(targets)}")
    print(f"ERROR: {len(errors)}   WARNING: {len(warns)}")
    by_check: dict[str, int] = {}
    for f in findings:
        by_check[f["check"]] = by_check.get(f["check"], 0) + 1
    if by_check:
        print("\nby check:")
        for k, v in sorted(by_check.items(), key=lambda x: -x[1]):
            print(f"  {v:6d}  {k}")
    for f in (errors + warns)[:25]:
        short = f["view"].split("views", 1)[-1]
        print(f"\n[{f['severity']}] {f['check']}  {short}  @{f['node']}")
        print(f"    {f['detail']}")
    if len(errors) + len(warns) > 25:
        print(f"\n... {len(errors) + len(warns) - 25} more")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
