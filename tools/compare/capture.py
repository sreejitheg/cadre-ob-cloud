"""Live render gate and capture for pages on our own gateway (G8).

Opens each route in a fresh browser context (a fresh Perspective session: an open session
keeps the inherited views it loaded, GF-10), waits for the view, then records:

  * the render verdict: no view error badge (`.view-state-display`), no "Trial Expired",
    no "View Not Found", and the count of rendered components;
  * the structural fingerprint (tools/compare/fingerprint.js);
  * a 1600 x 900 screenshot.

Runs under an interpreter with Playwright (ctig's `.venv`, Chromium 1228). Only for our own
gateway: the vendor demo is observed interactively, never automated (its robots.txt
disallows automated access).

Usage:
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/capture.py
        --base http://localhost:8088/data/perspective/client/cadre_hmi_demo --route /
        --out workspace/compare/process-overview/ours [--viewport 1600x900]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def settle_badges(page, cap_ms: int = 60000, step_ms: int = 1000):
    """Wait while the page still shows view state badges, at most `cap_ms`: an embedded view that is still loading
    shows the same badge (`.view-state-display`) as one that failed, and on a large page (the component test page of
    T2, 2372 tags) the loading badges outlast the fixed wait (82 after 6 s, none after 26 s, measured 2026-11-03). A
    badge that is still shown at the cap is counted by the verdict as before. Returns the extra wait in ms, or None when
    the badges did not clear."""
    waited = 0
    while page.locator(".view-state-display").count() and waited < cap_ms:
        page.wait_for_timeout(step_ms)
        waited += step_ms
    return waited if not page.locator(".view-state-display").count() else None


def capture(base: str, route: str, out: Path, width: int = 1600, height: int = 900,
            settle_ms: int = 6000) -> dict:
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    js = (HERE / "fingerprint.js").read_text(encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": width, "height": height})
        page = ctx.new_page()
        page.goto(base.rstrip("/") + route, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(settle_ms)
        loading_ms = settle_badges(page)
        body = page.inner_text("body")
        verdict = {
            "trial_expired": "Trial Expired" in body,
            "view_not_found": "View Not Found" in body,
            "view_error_badges": page.locator(".view-state-display").count(),
            "components": page.locator("[data-component]").count(),
            # A binding with bad quality draws an ERROR or NOTICES overlay (class ia_qualityOverlay):
            # the page renders and is still broken (measured on the first plant build, 2026-10-08).
            "quality_overlays": page.locator(".ia_qualityOverlay").count(),
            "badges_cleared_after_ms": loading_ms,
        }
        verdict["ok"] = (not verdict["trial_expired"] and not verdict["view_not_found"]
                         and verdict["view_error_badges"] == 0 and verdict["components"] > 0
                         and verdict["quality_overlays"] == 0)
        try:
            fp = json.loads(page.evaluate(js))
        except Exception as e:  # recorded, never hidden
            fp = {"error": str(e)[:200]}
        page.screenshot(path=str(out / "screenshot.png"))
        browser.close()
    (out / "fingerprint.json").write_text(json.dumps(fp, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "render.json").write_text(json.dumps(verdict, indent=1), encoding="utf-8")
    return verdict


def parse_viewport(text: str) -> tuple[int, int]:
    """`WIDTHxHEIGHT` as two integers; anything else is an argparse error."""
    try:
        w, h = (int(n) for n in text.lower().split("x"))
    except ValueError:
        raise argparse.ArgumentTypeError(f"a viewport is WIDTHxHEIGHT, not {text!r}")
    if w < 1 or h < 1:
        raise argparse.ArgumentTypeError(f"a viewport is positive, not {text!r}")
    return w, h


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--route", default="/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--viewport", type=parse_viewport, default=(1600, 900),
                    help="the browser window, WIDTHxHEIGHT (default 1600x900, the size of the screenshots so far)")
    a = ap.parse_args()
    v = capture(a.base, a.route, Path(a.out), width=a.viewport[0], height=a.viewport[1])
    print(json.dumps(v))
    return 0 if v["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
