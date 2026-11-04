"""One screenshot of each page of the showcase project, for wiki page 15: the top of the page in a fresh session, at device
scale factor 2, quantised to a palette PNG (Pillow) so that a page is a few hundred kilobytes.

Usage:
    python tools/compare/showcase_shots.py --base http://localhost:8088/data/perspective/client/cadre_hmi_showcase
        --model workspace/showcase/showcase-model.json --out wiki/img/showcase
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--viewport", default="1600x900")
    ap.add_argument("--colours", type=int, default=128)
    a = ap.parse_args()
    from PIL import Image
    from playwright.sync_api import sync_playwright
    width, height = (int(n) for n in a.viewport.lower().split("x"))
    model = json.loads(Path(a.model).read_text(encoding="utf-8"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for pg in model["pages"]:
            ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=2)
            page = ctx.new_page()
            page.goto(a.base.rstrip("/") + pg["route"], wait_until="networkidle", timeout=90000)
            page.wait_for_selector(f"#{next(iter(pg['cards']))}", timeout=60000)
            page.wait_for_timeout(7000)
            raw = page.screenshot()
            img = Image.open(io.BytesIO(raw)).convert("RGB").quantize(colors=a.colours, method=Image.Quantize.MEDIANCUT)
            target = out / f"{pg['id']}.png"
            img.save(target, optimize=True)
            print(f"{pg['id']:10s} {img.size[0]}x{img.size[1]}  {target.stat().st_size // 1024} KiB", flush=True)
            ctx.close()
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
