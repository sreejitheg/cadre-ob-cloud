"""Set one Boolean memory tag from a tags file, inside a root the caller allows (COB-181).

    python tools/hmi/tag_set.py --tags-file F.json --tag-root [default]cadre_hmi_x --tag src/Name --value true
                                --allowed-root [default]cadre_hmi_x/src [--dry-run]

`--tags-file` is a tag document (a folder export or the generator's `tags.json`); `--tag` is the tag's path in it
from the file's top (folders separated by `/`); `--tag-root` is the gateway path of the file's top. The tag is
imported through the gateway (ctig's lane, via `deploy._gateway`) into its folder with its definition from the file
and the new value. The write is refused, before any call to the gateway, unless the tag's full path lies under
`--allowed-root` (`[provider]folder`, matched by whole path parts, no `..`) and the tag is a Boolean memory tag; a
host that is not the local machine is refused as well. No credential is printed. `--dry-run` prints what would be
written and writes nothing.

Exit codes: 0 written (or a dry run that would write), 2 refused, 1 a fault.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tag_values  # noqa: E402

split_path = tag_values.split_path


class Refused(Exception):
    pass


def find_tag(doc: dict, path: str) -> dict:
    """The tag at `path` (folders by name, separated by `/`) in the document."""
    node = doc
    for part in [p for p in path.split("/") if p]:
        nxt = next((c for c in node.get("tags", []) if c.get("name") == part), None)
        if nxt is None:
            raise Refused(f"no tag {path!r} in the tags file (stopped at {part!r})")
        node = nxt
    return node


def check_scope(tag_root: str, tag: str, allowed_root: str) -> tuple[str, str]:
    """The (provider, full path) of the tag, or Refused when it is not inside the allowed root."""
    prov, root = split_path(tag_root)
    aprov, aroot = split_path(allowed_root)
    parts = [p for p in (root + "/" + tag).split("/") if p]
    allowed = [p for p in aroot.split("/") if p]
    if ".." in parts or "." in parts or ".." in allowed or not allowed:
        raise Refused("the tag path or the allowed root is not a plain path")
    if prov != aprov or parts[:len(allowed)] != allowed or len(parts) <= len(allowed):
        raise Refused(f"[{prov}]{'/'.join(parts)} is not under the allowed root [{aprov}]{'/'.join(allowed)}")
    return prov, "/".join(parts)


def plan(a) -> dict:
    prov, full = check_scope(a.tag_root, a.tag, a.allowed_root)      # before the file is read
    doc = json.loads(Path(a.tags_file).read_text(encoding="utf-8"))
    tag = copy.deepcopy(find_tag(doc, a.tag))
    if tag.get("tagType", "AtomicTag") != "AtomicTag" or tag.get("valueSource") != "memory" \
            or tag.get("dataType") != "Boolean":
        raise Refused(f"{full} is not a Boolean memory tag")
    tag["value"] = a.value == "true"
    return {"provider": prov, "folder": full.rpartition("/")[0], "tag": tag, "path": f"[{prov}]{full}"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tags-file", required=True)
    ap.add_argument("--tag-root", required=True, help="[provider]folder: the gateway path of the file's top")
    ap.add_argument("--tag", required=True, help="the tag's path in the file, folders separated by /")
    ap.add_argument("--value", required=True, choices=("true", "false"))
    ap.add_argument("--allowed-root", required=True, help="[provider]folder: the only place a write may land")
    ap.add_argument("--dry-run", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    try:
        p = plan(a)
    except Refused as e:
        print(f"tag_set: refused: {e}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as e:
        print(f"tag_set: {e}", file=sys.stderr)
        return 1
    if a.dry_run:
        print(f"tag_set: dry run: would set {p['path']} = {p['tag']['value']} "
              f"(import into [{p['provider']}]{p['folder']})")
        return 0
    try:
        gw, _ = tag_values.local_gateway()
        reply = gw.tags_import(p["provider"], p["folder"], {"tags": [p["tag"]]})
    except (SystemExit, Exception) as e:
        print(f"tag_set: {e}", file=sys.stderr)
        return 1
    print(f"tag_set: set {p['path']} = {p['tag']['value']}: {json.dumps(reply, default=str)[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
