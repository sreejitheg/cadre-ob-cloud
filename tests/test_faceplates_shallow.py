"""Tests of `faceplates.py --shallow` (COB-195): a device whose title is listed is checked by its opener only. A fake
page object stands in for the browser; nothing here uses Playwright or a gateway. Synthetic names only."""
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT  # noqa: E402

sys.path.insert(0, str(ROOT / "tools" / "compare"))
import faceplates  # noqa: E402


class FakeLocator:
    def __init__(self, page, kind):
        self.page, self.kind = page, kind

    def locator(self, sel):
        if "ia.display.label" in sel:
            return FakeLocator(self.page, "title")
        if "ia_qualityOverlay" in sel:
            return FakeLocator(self.page, "overlays")
        if "ia.container.coord" in sel:
            return FakeLocator(self.page, "close")
        return FakeLocator(self.page, "other")

    @property
    def first(self):
        return self

    def count(self):
        if self.kind == "overlays":
            return self.page.overlays.get(self.page.current, 0)
        return 1

    def bounding_box(self):
        return {"x": 2300 if self.page.current else 2700, "width": 400}

    def inner_text(self):
        if self.kind == "title":
            return f" {self.page.current} "
        return "Select a device" if self.page.empty.get(self.page.current) else f"{self.page.current} faceplate"

    def click(self):
        self.page.current = None


class FakeMouse:
    def __init__(self, page):
        self.page = page

    def click(self, x, y):
        self.page.current = self.page.titles[x]
        self.page.clicks.append(self.page.current)


class FakePage:
    viewport_size = {"width": 2700, "height": 1400}

    def __init__(self, titles, overlays=None, empty=None):
        self.titles, self.overlays, self.empty = titles, overlays or {}, empty or {}
        self.current, self.clicks = None, []
        self.mouse = FakeMouse(self)

    def goto(self, *a, **k):
        pass

    def wait_for_timeout(self, ms):
        pass

    def evaluate(self, script, *a):
        return [[i, 10] for i in range(len(self.titles))]

    def locator(self, sel):
        return FakeLocator(self, "dock")


class ShallowSweepTests(unittest.TestCase):
    def run_sweep(self, shallow, page=None, **kw):
        page = page or FakePage(["DEV_1", "DEV_2", "DEV_3"])
        walked = []

        def walk(pg, right, title, *a, **k):
            walked.append(title)
            return {"Control": {"overlays": 0, "badges": 0}}, []

        with mock.patch.object(faceplates, "open_tabs", walk):
            res = faceplates.sweep(page, "http://x/y", "/page_a", {"DEV_1", "DEV_2", "DEV_3"}, shallow=shallow, **kw)
        return res, walked, page

    def test_a_shallow_device_skips_the_tab_walk_and_a_deep_one_walks_it(self):
        res, walked, page = self.run_sweep({"DEV_2"})
        self.assertEqual(walked, ["DEV_1", "DEV_3"])
        self.assertEqual(page.clicks, ["DEV_1", "DEV_2", "DEV_3"])           # the opener is clicked for every device
        self.assertEqual(res["opened"]["DEV_2"], {"overlays": 0, "empty": False, "shallow": True})
        self.assertNotIn("tabs", res["opened"]["DEV_2"])
        self.assertEqual(res["opened"]["DEV_1"]["tabs"], {"Control": {"overlays": 0, "badges": 0}})
        self.assertNotIn("shallow", res["opened"]["DEV_1"])
        self.assertEqual((res["missing"], res["unexpected"], res["faults"], res["ok"]), ([], [], [], True))
        json.dumps(res)                                                        # the record is JSON

    def test_without_the_option_every_device_is_walked(self):
        for shallow in (None, set()):
            res, walked, _ = self.run_sweep(shallow)
            self.assertEqual(walked, ["DEV_1", "DEV_2", "DEV_3"])
            self.assertTrue(all("tabs" in v and "shallow" not in v for v in res["opened"].values()))

    def test_a_title_not_on_the_page_changes_nothing(self):
        res, walked, _ = self.run_sweep({"DEV_9"})
        base, base_walked, _ = self.run_sweep(None)
        self.assertEqual((res, walked), (base, base_walked))

    def test_a_shallow_device_still_fails_on_an_overlay_or_an_empty_faceplate(self):
        res, walked, _ = self.run_sweep({"DEV_1", "DEV_2"}, FakePage(["DEV_1", "DEV_2", "DEV_3"], overlays={"DEV_1": 2},
                                                                     empty={"DEV_2": True}))
        self.assertFalse(res["ok"])
        self.assertEqual(walked, ["DEV_3"])
        self.assertEqual(res["opened"]["DEV_1"], {"overlays": 2, "empty": False, "shallow": True})
        self.assertEqual(res["opened"]["DEV_2"], {"overlays": 0, "empty": True, "shallow": True})
        self.assertEqual(len(res["faults"]), 2)

    def test_missing_and_unexpected_are_unchanged(self):
        page = FakePage(["DEV_1", "DEV_2"])
        with mock.patch.object(faceplates, "open_tabs", lambda *a, **k: ({}, [])):
            res = faceplates.sweep(page, "http://x/y", "/page_a", {"DEV_1", "DEV_3"}, shallow={"DEV_1", "DEV_2", "DEV_3"})
        self.assertEqual((res["missing"], res["unexpected"], res["ok"]), (["DEV_3"], ["DEV_2"], False))

    def test_the_option_is_parsed_into_a_set_of_titles(self):
        seen = {}

        def fake_sweep(page, base, route, expected, expect, devices=None, shallow=None):
            seen["shallow"] = shallow
            return {"route": route, "leaf_views": 0, "expected": 0, "opened": {}, "missing": [], "unexpected": [],
                    "faults": [], "ok": True}

        import tempfile
        with tempfile.TemporaryDirectory() as t:
            desc = Path(t) / "d.json"
            desc.write_text(json.dumps({"screen": {"route": "/page_a"}, "symbols": []}), encoding="utf-8")
            fake_pw = mock.MagicMock()
            with mock.patch.object(faceplates, "sweep", fake_sweep), \
                    mock.patch.dict(sys.modules, {"playwright": mock.MagicMock(), "playwright.sync_api": fake_pw}), \
                    mock.patch.object(sys, "argv", ["faceplates.py", "--base", "http://x/y", "--descriptor", str(desc),
                                                    "--out", str(Path(t) / "o"), "--shallow", "DEV_1, Motor 1,,DEV_2"]), \
                    mock.patch("builtins.print"):
                self.assertEqual(faceplates.main(), 0)
            self.assertEqual(seen["shallow"], {"DEV_1", "Motor 1", "DEV_2"})
            self.assertTrue((Path(t) / "o" / "faceplates.json").exists())


if __name__ == "__main__":
    unittest.main()
