"""Tests of the recon preview's hotspots and status lists (COB-180, WorkflowBuilder WFB-175): an invisible navigation
hotspot paints no opaque box and never lies above the object it covers; a status list of N labelled indicators is
drawn as N lamp and label rows. Synthetic inputs only. The browser tests run under ctig's `.venv` (Playwright)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import UNIT_FILES, fixture, inputs  # noqa: E402

from hmi import asm_model, preview  # noqa: E402
from test_preview import HAVE_BROWSER, recon_args  # noqa: E402


def units(extra_indicators=0):
    us = [asm_model.check_understanding(fixture(n), n) for n in UNIT_FILES.values()]
    if extra_indicators:
        st = next(u for u in us if u["unit"]["id"] == "PumpStation")
        for i in range(extra_indicators):
            st["indicators"].append({"id": f"sl{i}", "label": f"Status {i}", "expr": "BRK01_CLOSED", "on": "On",
                                     "off": "Off", "bbox": {"x": 900, "y": 400, "w": 24, "h": 24},
                                     "ans": [], "basis": {}, "inferred": False})
    return us


def recon(us, d):
    return preview.prepare_recon(us, fixture("asm-faceplates.json"), fixture("asm-tables.json"), inputs(d)["inventory"])


class DataTests(unittest.TestCase):
    def test_every_recon_navigation_item_is_a_hotspot(self):
        with tempfile.TemporaryDirectory() as t:
            data, _ = recon(units(), Path(t))
        navs = [i for p in data["pages"] for i in p["items"] if i["kind"] in ("link", "button")]
        self.assertTrue(navs)
        self.assertTrue(all(i.get("hotspot") for i in navs))

    def test_indicators_that_share_a_box_are_laid_out_as_rows_each_with_its_label(self):
        with tempfile.TemporaryDirectory() as t:
            data, _ = recon(units(4), Path(t))
        rows = [i for p in data["pages"] for i in p["items"] if i["kind"] == "indicator" and i["uid"].split(":")[1].startswith("sl")]
        self.assertEqual([r["label"] for r in rows], [f"Status {i}" for i in range(4)])
        ys = [r["y"] for r in rows]
        self.assertEqual(ys, sorted(set(ys)))
        self.assertTrue(all(b - a >= 20 for a, b in zip(ys, ys[1:])))

    def test_a_single_indicator_keeps_its_box(self):
        with tempfile.TemporaryDirectory() as t:
            data, _ = recon(units(), Path(t))
        lamp = next(i for p in data["pages"] for i in p["items"] if i["uid"] == "Overview:i1")
        self.assertEqual((lamp["x"], lamp["y"]), (60, 244))


@unittest.skipUnless(HAVE_BROWSER, "Playwright is not importable here; run under ctig's .venv")
class BrowserTests(unittest.TestCase):
    def render(self, us, d):
        ins = inputs(d)
        out = d / "o"
        self.assertEqual(preview.main(recon_args(ins, out, "--bundle", "--checks", "")), 0)
        return out / "preview.html"

    def probe(self, html, page_id, script, arg):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 1280, "height": 720})
            page.goto(html.as_uri() + "#frozen")
            page.wait_for_selector("body[data-ready='1']")
            page.click(f"#tree button[data-page='{page_id}']")
            r = page.evaluate(script, arg)
            b.close()
        return r

    def test_a_hotspot_is_transparent_and_has_its_label_as_a_title(self):
        with tempfile.TemporaryDirectory() as t:
            html = self.render(units(), Path(t))
            r = self.probe(html, "Overview", """(uid) => { const e = document.querySelector("[data-uid='" + uid + "']");
                const b = e.querySelector('button'); const s = getComputedStyle(b);
                return {bg: s.backgroundColor, title: e.title, text: b.textContent}; }""", "Overview:n2")
        self.assertIn(r["bg"], ("rgba(0, 0, 0, 0)", "transparent"))
        self.assertEqual(r["title"], "Pump 1")
        self.assertEqual(r["text"], "")

    def test_a_hotspot_lies_under_the_object_it_covers(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            html = self.render(units(), d)
            r = self.probe(html, "Overview", """(uid) => {
                const h = document.querySelector("[data-uid='" + uid + "']"); const r = h.getBoundingClientRect();
                const cover = document.createElement('div'); cover.className = 'it readout'; cover.dataset.uid = 'cover';
                cover.style.cssText = 'left:' + h.offsetLeft + 'px;top:' + h.offsetTop + 'px;width:' + h.offsetWidth + 'px;height:' + h.offsetHeight + 'px';
                h.parentNode.appendChild(cover);
                const e = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
                return e.closest('[data-uid]').dataset.uid; }""", "Overview:n1")
        self.assertEqual(r, "cover")

    def test_a_status_list_draws_every_label_on_one_line(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            ins = inputs(d)
            lst = Path(ins["understandings"])
            names = [Path(x) for x in lst.read_text(encoding="utf-8").split("\n") if x.strip()]
            for n in names:
                doc = json.loads(n.read_text(encoding="utf-8"))
                if doc["unit"]["id"] == "PumpStation":
                    for i in range(3):
                        doc["indicators"].append({"id": f"sl{i}", "label": f"Status {i}", "expr": "BRK01_CLOSED",
                                                  "on": "On", "off": "Off", "bbox": {"x": 900, "y": 400, "w": 24, "h": 24},
                                                  "ans": [], "basis": {}, "inferred": False})
                    n.write_text(json.dumps(doc), encoding="utf-8")
            out = d / "o"
            self.assertEqual(preview.main(recon_args(ins, out, "--bundle", "--checks", "")), 0)
            r = self.probe(out / "preview.html", "PumpStation", """() => Array.from(document.querySelectorAll("[data-uid*=':sl']")).map(e => {
                const w = e.querySelector('.w'); const b = w.getBoundingClientRect();
                return {text: w.textContent, h: b.height, top: e.getBoundingClientRect().top}; })""", None)
        self.assertEqual(len(r), 3)
        self.assertEqual(len({x["top"] for x in r}), 3)
        self.assertTrue(all(x["h"] < 20 for x in r), r)


if __name__ == "__main__":
    unittest.main()
