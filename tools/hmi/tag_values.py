"""Read the live values of a tag folder twice and report the tags that changed (COB-181).

    python tools/hmi/tag_values.py --path [default]cadre_hmi_x/src [--interval 3] [--out F.json]

Exports the folder through the gateway (ctig's lane, via `deploy._gateway`) two times, `--interval` seconds apart,
and lists the tags whose value differs: the way to tell a tag that the plant simulation drives from one that stands
still. `--path` is `[provider]folder`; the provider is `default` where the brackets are left out. Read only:
nothing is written to the gateway. The host is the one `deploy` uses (`CADRE_IGNITION_GATEWAY_URL`) and a host that
is not the local machine is refused before any call.

Writes `--out` (`cadre-hmi-tag-values/1`: path, interval, the count of tags, the changed tags with both values).
Exit codes: 0 at least one tag changed, 2 none changed (a static folder, or one without tags), 1 a fault.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy  # noqa: E402

SCHEMA = "cadre-hmi-tag-values/1"
LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")


def split_path(path: str) -> tuple[str, str]:
    """`[provider]folder` as (provider, folder); `default` where no provider is given."""
    if path.startswith("["):
        prov, _, rest = path[1:].partition("]")
        return prov or "default", rest.strip("/")
    return "default", path.strip("/")


def local_gateway():
    """`deploy._gateway()`, refused where the gateway's host is not this machine."""
    host = urlparse(deploy.GATEWAY).hostname
    if host not in LOCAL_HOSTS:
        raise SystemExit(f"the gateway host {host!r} is not local; these tools run against the local gateway only")
    return deploy._gateway()


def flatten(doc: dict) -> dict[str, object]:
    """The atomic tags of an exported folder by their path relative to it."""
    out: dict[str, object] = {}

    def walk(node: dict, prefix: str) -> None:
        for c in node.get("tags", []):
            if c.get("tagType") == "Folder" or "tags" in c:
                walk(c, prefix + c["name"] + "/")
            else:
                out[prefix + c["name"]] = c.get("value")
    walk(doc, "")
    return out


def compare(first: dict, second: dict) -> list[dict]:
    return [{"tag": k, "first": first[k], "second": second.get(k)} for k in first if first[k] != second.get(k)]


def read_twice(gw, path: str, interval: float, sleep=time.sleep) -> tuple[dict, dict]:
    prov, folder = split_path(path)
    a = flatten(gw.tags_export(prov, folder))
    sleep(interval)
    b = flatten(gw.tags_export(prov, folder))
    return a, b


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--path", required=True, help="[provider]folder to read")
    ap.add_argument("--interval", type=float, default=3.0, help="seconds between the two reads (default 3)")
    ap.add_argument("--out", default=None, help="write the report here (JSON)")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    if a.interval < 0:
        print("tag_values: --interval is not negative", file=sys.stderr)
        return 1
    try:
        gw, _ = local_gateway()
        first, second = read_twice(gw, a.path, a.interval, sleep=time.sleep)
    except (SystemExit, Exception) as e:    # a refused host, no token, an unreachable gateway
        print(f"tag_values: {e}", file=sys.stderr)
        return 1
    changed = compare(first, second)
    doc = {"schema": SCHEMA, "path": a.path, "interval": a.interval, "tags": len(first), "changed": changed}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_bytes((json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"tag_values: {a.path}: {len(first)} tags, {len(changed)} changed in {a.interval:g} s"
          + (f": {', '.join(c['tag'] for c in changed[:8])}" if changed else ""))
    return 0 if changed else 2


if __name__ == "__main__":
    sys.exit(main())
