"""Experiment E8: does an embedded view keep a parameter its embedding leaves out? (register COB-112).

The generated walk opened a device with no label and read another device's label in the faceplate
header. The symbol hands its `deviceLabel` parameter to the faceplate, and the generator left that
parameter out of the embedding where the device has no label. The question is where the value came
from: the view's own default is the empty text.

Questions:
  P1  In a new session, does the first embedded view of a page show only what its embedding states?
  P2  After another page is loaded by URL in the same browser tab, does an embedded view of the same
      view path at the same place of the page keep the earlier instance's value for a parameter its
      own embedding leaves out?
  P3  Does the same happen after navigation by the frame's menu, with no load by URL?

The probe reads only: it loads two routes of a project and prints the text of the first embedded
views of each page. Give it two cards pages whose first card holds the same kind of symbol first, one
stating a parameter that shows (a unit) and the other leaving it out.

Usage (an interpreter with Playwright):
    python tools/experiments/e8_param_leak_probe.py --base <client URL of the project> \
        --first / --second /other-route [--menu "Label of the first" "Label of the second"]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "compare"))

FIRST_VIEWS = r"""(n) => [...document.querySelectorAll('[data-component="ia.display.view"]')]
  .filter(e => !e.closest('[class*="docked-view"]')).slice(0, n)
  .map(e => e.innerText.replace(/\s+/g, ' ').trim())"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", required=True, help="the client URL of the project, without a route")
    ap.add_argument("--first", default="/", help="the route whose embedding states the parameter")
    ap.add_argument("--second", required=True, help="the route whose embedding leaves it out")
    ap.add_argument("--menu", nargs=2, metavar=("FIRST_LABEL", "SECOND_LABEL"),
                    help="the navigation menu's labels of the two routes, for question P3")
    ap.add_argument("--views", type=int, default=2, help="how many embedded views of each page to print")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    import glass

    def load(page, route):
        page.goto(a.base.rstrip("/") + route, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(4000)
        return page.evaluate(FIRST_VIEWS, a.views)

    def new_page(browser):
        return browser.new_context(viewport={"width": 1600, "height": 900}).new_page()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = new_page(browser)
            print("P1 new session, the second route first:", load(page, a.second), flush=True)
            print("P2 then the first route by URL:", load(page, a.first), flush=True)
            print("P2 then the second route by URL:", load(page, a.second), flush=True)
            print("P2 the second route loaded again:", load(page, a.second), flush=True)
            if a.menu:
                page = new_page(browser)
                print("P3 new session, the first route:", load(page, a.first), flush=True)
                print("P3 by the menu to the second:", glass.navigate_by_menu(page, a.menu[1]),
                      page.evaluate(FIRST_VIEWS, a.views), flush=True)
                print("P3 by the menu to the first:", glass.navigate_by_menu(page, a.menu[0]),
                      page.evaluate(FIRST_VIEWS, a.views), flush=True)
                print("P3 by the menu to the second again:", glass.navigate_by_menu(page, a.menu[1]),
                      page.evaluate(FIRST_VIEWS, a.views), flush=True)
        finally:
            browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
