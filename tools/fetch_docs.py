"""Fetch the OpenStudio documentation pages listed in a URL file into a local cache.

The cache is source material (third-party copyright) and lives under reference/, which
is not tracked. The fetch is sequential and paced, and skips pages already cached.

Usage:
    python tools/fetch_docs.py --urls reference/openstudio-docs/urls.txt --out reference/openstudio-docs/html
"""
import argparse
import hashlib
import json
import pathlib
import time
import urllib.request

UA = "Mozilla/5.0 (Cadre-Sandbox-OpenBridge documentation study; contact owner)"


def slug(url: str) -> str:
    path = url.split("://", 1)[1].split("/", 1)[1].strip("/")
    return path.replace("/", "__") or "index"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--delay", type=float, default=1.0)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {}
    urls = [u.strip() for u in pathlib.Path(a.urls).read_text().splitlines() if u.strip()]
    for i, url in enumerate(urls, 1):
        target = out / f"{slug(url)}.html"
        if not target.exists():
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
            target.write_bytes(body)
            time.sleep(a.delay)
        data = target.read_bytes()
        manifest[url] = {"file": target.name, "bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest()}
        print(f"{i:3d}/{len(urls)} {len(data):7d} {url}")
    (out.parent / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
