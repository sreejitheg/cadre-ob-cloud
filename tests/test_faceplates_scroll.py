"""Tests of the G11 opener's scroll (`faceplates.py`, COB-201): each leaf is scrolled into view before it is clicked, so the
sweep opens every device of a tall page (the component test page is 8,600 px high). A fake page stands in for the browser
in the offline tests; headless Chromium (ctig's `.venv`, Playwright) runs the real measure and locators on a tall static
page when Playwright is importable. Synthetic names only.

    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe -m unittest tests.test_faceplates_scroll
"""
import http.server
import re
import sys
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT  # noqa: E402

sys.path.insert(0, str(ROOT / "tools" / "compare"))
import faceplates  # noqa: E402
from test_faceplates_shallow import FakePage  # noqa: E402

try:
    import playwright.sync_api  # noqa: F401
    HAVE_BROWSER = True
except ImportError:
    HAVE_BROWSER = False

GAP = 1000   # px between two leaves of the tall fake page


class LeafLocator:
    def __init__(self, page, index):
        self.page, self.index = page, index

    @property
    def first(self):
        return self

    def count(self):
        return 1 if self.index < len(self.page.titles) else 0

    def scroll_into_view_if_needed(self, timeout=None):
        self.page.scroll = GAP * self.index
        self.page.events.append(("scroll", self.index))


class TallMouse:
    def __init__(self, page):
        self.page = page

    def click(self, x, y):
        """A click lands on a leaf only inside the viewport; the fake leaf `x` is at row `x` of the page."""
        if 0 <= y < self.page.viewport_size["height"]:
            self.page.current = self.page.titles[x]
            self.page.clicks.append(self.page.current)
            self.page.events.append(("click", x))
        else:
            self.page.missed.append((x, y))


class TallPage(FakePage):
    """Leaf `i` stands `GAP * i` px down the page, 100 px from the top of the viewport once scrolled to."""

    def __init__(self, titles, height=1400):
        super().__init__(titles)
        self.viewport_size = {"width": 2700, "height": height}
        self.scroll, self.events, self.missed = 0, [], []
        self.mouse = TallMouse(self)

    def evaluate(self, script, *a):
        return [[i, 100 + GAP * i - self.scroll] for i in range(len(self.titles))]

    def locator(self, sel):
        m = re.fullmatch(r"\[data-g11-leaf='(\d+)'\]", sel)
        return LeafLocator(self, int(m.group(1))) if m else super().locator(sel)


class ScrollOfflineTests(unittest.TestCase):
    TITLES = ["DEV_1", "DEV_2", "DEV_3", "DEV_4"]

    def sweep(self, page):
        with mock.patch.object(faceplates, "open_tabs", lambda *a, **k: ({}, [])):
            return faceplates.sweep(page, "http://x/y", "/tall", set(self.TITLES))

    def test_every_leaf_is_scrolled_to_before_it_is_clicked(self):
        page = TallPage(self.TITLES)
        res = self.sweep(page)
        self.assertEqual((res["missing"], res["faults"], res["ok"]), ([], [], True))
        self.assertEqual(sorted(res["opened"]), self.TITLES)
        self.assertEqual(page.missed, [])
        order = [e for e in page.events]
        self.assertEqual(order, [(k, i) for i in range(4) for k in ("scroll", "click")])   # a scroll, then its click, each time

    def test_without_the_scroll_the_leaves_below_the_fold_are_not_opened(self):
        page = TallPage(self.TITLES)
        with mock.patch.object(faceplates, "bring_into_view", lambda p, i: False):
            res = self.sweep(page)
        self.assertEqual(res["missing"], ["DEV_3", "DEV_4"])     # 2,100 and 3,100 px down a 1,400 px window
        self.assertFalse(res["ok"])
        self.assertEqual(len(page.missed), 2)

    def test_a_leaf_that_cannot_scroll_is_clicked_where_it_was_measured(self):
        class Broken(LeafLocator):
            def scroll_into_view_if_needed(self, timeout=None):
                raise TimeoutError("Element is not attached")

        page = TallPage(["DEV_1", "DEV_2"], height=1400)
        page.locator = lambda sel: Broken(page, int(re.search(r"\d+", sel).group(0))) if "g11-leaf" in sel else FakePage.locator(page, sel)
        res = self.sweep_titles(page, {"DEV_1", "DEV_2"})
        self.assertEqual(sorted(res["opened"]), ["DEV_1", "DEV_2"])      # both are inside the window: the failure costs nothing

    def sweep_titles(self, page, expected):
        with mock.patch.object(faceplates, "open_tabs", lambda *a, **k: ({}, [])):
            return faceplates.sweep(page, "http://x/y", "/tall", expected)

    def test_the_measure_stamps_each_clicked_element_with_its_index(self):
        self.assertIn("data-g11-leaf", faceplates.LEAF_POINTS)
        self.assertIn(faceplates.LEAF_MARK, faceplates.LEAF_POINTS)


PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%%;overflow:hidden;font:14px sans-serif}
#sc{position:absolute;left:0;top:0;right:0;bottom:0;overflow:auto}
#tall{position:relative;height:%(height)dpx}
.v{position:absolute;left:300px;width:120px;height:40px;background:#cde}
.docked-view-right{box-sizing:border-box;position:fixed;top:0;right:-400px;width:400px;height:300px;background:#fff;border:1px solid #888;z-index:5}
.docked-view-right.open{right:0}
</style></head><body>
<div id="sc"><div id="tall">
%(leaves)s
</div></div>
<div class="docked-view-right" id="dock"><div data-component="ia.display.label" id="t"></div>
<div data-component="ia.container.coord" id="close" style="width:60px;height:20px;background:#ccc">close</div></div>
<script>
var dock = document.getElementById('dock');
document.querySelectorAll('.v').forEach(function (v) { v.addEventListener('click', function () {
  document.getElementById('t').textContent = v.dataset.title; dock.classList.add('open'); }); });
document.getElementById('close').addEventListener('click', function () { dock.classList.remove('open'); });
</script></body></html>"""


@unittest.skipUnless(HAVE_BROWSER, "Playwright is not importable here; run under ctig's .venv")
class ScrollInChromiumTests(unittest.TestCase):
    """The real measure and the real locators on a page whose leaves lie far below the first window, in a scroller of its
    own (as Perspective's page is): a click below the window's edge reaches nothing."""
    TITLES = [f"DEV_{n}" for n in range(1, 6)]

    @classmethod
    def setUpClass(cls):
        leaves = "\n".join(f'<div class="v" data-component="ia.display.view" data-title="{t}" style="top:{100 + 900 * i}px">{t}</div>'
                           for i, t in enumerate(cls.TITLES))
        html = (PAGE % {"height": 100 + 900 * len(cls.TITLES) + 400, "leaves": leaves}).encode("utf-8")

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)

        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def sweep(self, scroll=True):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_context(viewport={"width": 1280, "height": 700}).new_page()
                real = page.wait_for_timeout
                page.wait_for_timeout = lambda ms: real(min(ms, 40))
                patch = mock.patch.object(faceplates, "bring_into_view", lambda pg, i: False) if not scroll else mock.MagicMock()
                with mock.patch.object(faceplates, "open_tabs", lambda *a, **k: ({}, [])), patch:
                    return faceplates.sweep(page, self.base, "/tall", set(self.TITLES))
            finally:
                browser.close()

    def test_g11_opens_every_device_of_a_page_many_windows_tall(self):
        res = self.sweep()
        self.assertEqual((res["missing"], res["unexpected"], res["faults"], res["ok"]), ([], [], [], True))
        self.assertEqual(res["leaf_views"], len(self.TITLES))
        self.assertEqual(sorted(res["opened"]), self.TITLES)

    def test_the_same_page_without_the_scroll_misses_the_leaves_below_the_first_window(self):
        res = self.sweep(scroll=False)
        self.assertEqual(res["missing"], self.TITLES[1:])        # only the first leaf (100 px down) lies in a 700 px window
        self.assertFalse(res["ok"])


if __name__ == "__main__":
    unittest.main()
