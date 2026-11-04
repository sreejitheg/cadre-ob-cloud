"""Compare the stock library rendering of a project with its Cadre HMI Components module rendering.

The same descriptors are built twice (`screen.py --render stock` and `--render module`) into two
projects bound to the same tags. For every route this measures, in fresh browser contexts:

  ready_ms        navigation start to the moment the count of Perspective components stops
                  changing (stable for 800 ms), cold cache
  components      Perspective components on the page (`[data-component]`)
  dom_elements    elements in the light DOM and in every shadow root
  heap_mb         JavaScript heap in use after ready (Chromium)
  transfer_kb     bytes transferred by the page load (resource timing)
  module_assets   whether the module's script and stylesheet were loaded

and writes a side-by-side screenshot per route and crops of named symbols.

Usage (ctig's .venv for Playwright and Pillow):
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/module_compare.py
        --stock cadre_hmi_wtp --module cadre_hmi_wtpob --route / --route /intake --runs 4
        --out workspace/spike/compare
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

PIL_PY = os.environ.get("CADRE_PIL_PYTHON", "F:/repos/ProgramAudit/.venv/Scripts/python.exe")

BASE = "http://localhost:8088/data/perspective/client"

READY = """async () => {
  const t0 = performance.timeOrigin;
  let last = -1, lastChange = performance.now(), start = performance.now();
  while (performance.now() - start < 30000) {
    const n = document.querySelectorAll('[data-component]').length;
    if (n !== last) { last = n; lastChange = performance.now(); }
    else if (n > 20 && performance.now() - lastChange > 800) break;
    await new Promise(r => setTimeout(r, 50));
  }
  const obc = [...document.querySelectorAll('obc-pump, obc-automation-tank')];
  await Promise.all(obc.map(e => e.updateComplete));
  let dom = 0;
  const walk = (root) => { for (const n of root.querySelectorAll('*')) { dom++; if (n.shadowRoot) walk(n.shadowRoot); } };
  walk(document);
  const res = performance.getEntriesByType('resource');
  const nav = performance.getEntriesByType('navigation')[0];
  return {ready_ms: Math.round(lastChange), components: last, dom_elements: dom,
          obc_elements: obc.length,
          heap_mb: performance.memory ? +(performance.memory.usedJSHeapSize / 1048576).toFixed(1) : null,
          transfer_kb: Math.round((res.reduce((a, r) => a + (r.transferSize || 0), 0) + (nav ? nav.transferSize : 0)) / 1024),
          module_assets: res.filter(r => r.name.includes('/res/cadreob/')).map(r => r.name.split('/res/cadreob/')[1])};
}"""

BOX = """(name) => {
  // a symbol's box: module component root, or the embedded view whose readout shows the name
  const mods = [...document.querySelectorAll('[data-component^="cadre.ob."]')];
  for (const m of mods) {
    const txt = [m.innerText];
    const walk = (r) => { for (const n of r.querySelectorAll('*')) { if (n.shadowRoot) { txt.push(n.shadowRoot.textContent); walk(n.shadowRoot); } } };
    walk(m);
    if (txt.join(' ').includes(name)) { const b = m.getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; }
  }
  const views = [...document.querySelectorAll('[data-component="ia.display.view"]')].filter(v => v.innerText.includes(name));
  if (!views.length) return null;
  views.sort((a, b) => a.querySelectorAll('*').length - b.querySelectorAll('*').length);
  const b = views[0].getBoundingClientRect();
  return [b.x, b.y, b.width, b.height];
}"""


def measure(browser, url: str) -> dict:
    ctx = browser.new_context(viewport={"width": 1600, "height": 900})
    page = ctx.new_page()
    page.goto(url, wait_until="load", timeout=60000)
    m = page.evaluate(READY)
    ctx.close()
    return m


def shoot(browser, url: str, path: Path, crops: list[str]) -> dict:
    ctx = browser.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=2)
    page = ctx.new_page()
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    page.screenshot(path=str(path))
    boxes = {n: page.evaluate(BOX, n) for n in crops}
    ctx.close()
    return boxes


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--compose":
        return compose(Path(sys.argv[2]))
    ap = argparse.ArgumentParser()
    ap.add_argument("--stock", required=True)
    ap.add_argument("--module", required=True)
    ap.add_argument("--route", action="append", required=True)
    ap.add_argument("--crop", action="append", default=[])
    ap.add_argument("--runs", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {"routes": {}}
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--enable-precise-memory-info"])
        for route in a.route:
            slug = route.strip("/") or "overview"
            r = {}
            for variant, prj in (("stock", a.stock), ("module", a.module)):
                url = f"{BASE}/{prj}{route}"
                runs = [measure(browser, url) for _ in range(a.runs)]
                agg = {k: statistics.median([x[k] for x in runs]) for k in ("ready_ms", "components", "dom_elements",
                                                                            "obc_elements", "transfer_kb")}
                heaps = [x["heap_mb"] for x in runs if x["heap_mb"] is not None]
                agg["heap_mb"] = statistics.median(heaps) if heaps else None
                agg["ready_ms_runs"] = [x["ready_ms"] for x in runs]
                agg["module_assets"] = runs[0]["module_assets"]
                shot = out / f"{slug}-{variant}.png"
                agg["boxes"] = shoot(browser, url, shot, a.crop)
                r[variant] = agg
                print(slug, variant, {k: v for k, v in agg.items() if k not in ("boxes",)})
            report["routes"][route] = r
        browser.close()
    report["crops"] = a.crop
    (out / "module_compare.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    # Images need Pillow, which lives in another environment (as for tools/compare/compare.py).
    return subprocess.call([PIL_PY, __file__, "--compose", str(out)])


def compose(out: Path) -> int:
    from PIL import Image
    report = json.loads((out / "module_compare.json").read_text(encoding="utf-8"))
    for route, r in report["routes"].items():
        slug = route.strip("/") or "overview"
        a_img, b_img = Image.open(out / f"{slug}-stock.png"), Image.open(out / f"{slug}-module.png")
        side = Image.new("RGB", (a_img.width + b_img.width + 40, max(a_img.height, b_img.height)), "white")
        side.paste(a_img, (0, 0))
        side.paste(b_img, (a_img.width + 40, 0))
        side.save(out / f"{slug}-side-by-side.png")
        pairs = []
        for n in report["crops"]:
            bs, bm = r["stock"]["boxes"].get(n), r["module"]["boxes"].get(n)
            if not bs or not bm:
                continue
            pad = 40
            crops = []
            for img, bx in ((a_img, bs), (b_img, bm)):
                x0, y0 = max(0, (bx[0] - pad) * 2), max(0, (bx[1] - pad) * 2)
                x1, y1 = (bx[0] + bx[2] + pad + 80) * 2, (bx[1] + bx[3] + pad + 40) * 2
                crops.append(img.crop((int(x0), int(y0), int(x1), int(y1))))
            pairs.append((n, crops))
        if pairs:
            w = max(c[0].width + c[1].width + 30 for _, c in pairs)
            h = sum(max(c[0].height, c[1].height) + 20 for _, c in pairs)
            grid = Image.new("RGB", (w, h), "white")
            y = 0
            for _, (cs, cm) in pairs:
                grid.paste(cs, (0, y))
                grid.paste(cm, (cs.width + 30, y))
                y += max(cs.height, cm.height) + 20
            grid.save(out / f"{slug}-symbols.png")
    print("composed", len(report["routes"]), "routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
