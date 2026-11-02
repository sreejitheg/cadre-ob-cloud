"""Tests of `tools/hmi/preview.py` (S10-B, ARCH-WFB-01 revision B8 Table 109 and section 29.9, schema
`cadre-hmi-preview-checks/1`).

The offline tests need nothing but the synthetic fixtures. The browser tests drive the preview's own output in
headless Chromium and run when Playwright is importable (ctig's `.venv`); the library suite under the system
interpreter skips them:

    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe -m unittest tests.test_preview
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, UNIT_FILES, dump, fixture, inputs, validate  # noqa: E402

from hmi import asm_model, preview  # noqa: E402

try:
    import playwright.sync_api  # noqa: F401
    HAVE_BROWSER = True
except ImportError:
    HAVE_BROWSER = False

TAG_ROOT = "[default]cadre_hmi_plant"
DESIGNS = ("asm-design-overview.json", "asm-design-pumpstation.json")
WINDOW = "1280x720"


def make(d: Path, hostile: bool = False):
    ins = inputs(d)
    if hostile:
        t = fixture("asm-tables.json")
        t["devices"]["PUMP01"]["variables"][1]["comment"] = "</script><img src=x onerror=alert(1)> & \u2028 end"
        dump(ins["tables"], t)
        f = fixture("asm-faceplates.json")
        f["faceplates"][0]["tabs"][0]["name"] = "Home"
        dump(ins["faceplates"], f)
    out = d / "model"
    assert asm_model.main([a for k, v in ins.items() for a in (f"--{k}", str(v))] + ["--tag-root", TAG_ROOT,
                                                                                    "--out", str(out)]) == 0
    lst = d / "designs.txt"
    paths = [dump(d / "designs" / n, fixture(n)) for n in DESIGNS]
    lst.write_text("\n".join(str(p) for p in paths) + "\n", encoding="utf-8", newline="\n")
    return out / "model.json", lst, ins


def asm_args(d, model, lst, ins, out, *extra):
    return ["--mode", "asm", "--model", str(model), "--designs", str(lst), "--faceplates", str(ins["faceplates"]),
            "--tables", str(ins["tables"]), "--window", WINDOW, "--out", str(out), *extra]


def recon_args(ins, out, *extra):
    return ["--mode", "recon", "--understandings", str(ins["understandings"]), "--faceplates", str(ins["faceplates"]),
            "--inventory", str(ins["inventory"]), "--tables", str(ins["tables"]), "--window", WINDOW,
            "--out", str(out), *extra]


class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.model, cls.lst, cls.ins = make(cls.dir)
        cls.out = cls.dir / "asm"
        cls.code = preview.main(asm_args(cls.dir, cls.model, cls.lst, cls.ins, cls.out, "--bundle", "--checks", ""))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def doc(self):
        return json.loads((self.out / "checks.json").read_text(encoding="utf-8"))

    def test_the_bundle_and_the_site_are_written(self):
        self.assertEqual(self.code, 0)
        for rel in ("preview.html", "site/index.html", "site/renderer.js", "site/style.css", "checks.json"):
            self.assertTrue((self.out / rel).is_file(), rel)

    def test_checks_json_validates_against_its_schema_with_the_registry_identifier(self):
        self.assertEqual(validate(self.doc(), "cadre-hmi-preview-checks-1.json"), [])
        schema = json.loads((ROOT / "schemas" / "cadre-hmi-preview-checks-1.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "cadre-hmi-preview-checks/1")

    def test_the_bundle_holds_no_external_reference_and_no_inline_handler(self):
        b = self.doc()["bundle"]
        self.assertEqual((b["external_refs"], b["inline_handlers"]), (0, 0))
        self.assertEqual(b["file"], "preview.html")
        text = (self.out / "preview.html").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"(?i)https?:")
        self.assertNotRegex(text, r"(?i)\ssrc\s*=\s*[\"']?//")
        self.assertNotRegex(text, r"(?i)\son[a-z]+\s*=")
        self.assertNotIn("javascript:", text.lower())
        self.assertNotRegex(text, r"(?i)<(link|iframe|object|embed|base)\b")

    def test_the_inline_scripts_hash_to_the_recorded_values(self):
        text = (self.out / "preview.html").read_text(encoding="utf-8")
        scan = preview.scan_bundle(text)
        self.assertEqual(scan["script_hashes"], self.doc()["bundle"]["script_hashes"])
        self.assertEqual(len(scan["script_hashes"]), 1)
        renderer = (ROOT / "tools" / "hmi" / "preview_assets" / "renderer.js").read_text(encoding="utf-8")
        self.assertEqual(scan["script_hashes"][0], preview.sha256_text(renderer.replace("\r\n", "\n")))

    def test_a_content_security_policy_pins_the_one_script(self):
        text = (self.out / "preview.html").read_text(encoding="utf-8")
        renderer = (ROOT / "tools" / "hmi" / "preview_assets" / "renderer.js").read_text(encoding="utf-8")
        self.assertIn("script-src '" + preview.sha256_csp(renderer.replace("\r\n", "\n")) + "'", text)
        self.assertIn("default-src 'none'", text)

    def test_the_data_sits_in_an_application_json_block(self):
        text = (self.out / "preview.html").read_text(encoding="utf-8")
        blocks = re.findall(r'<script type="application/json" id="preview-data">(.*?)</script>', text, re.S)
        self.assertEqual(len(blocks), 1)
        data = json.loads(blocks[0])
        self.assertEqual(data["mode"], "asm")
        self.assertIn("PumpStation", {p["id"] for p in data["pages"]})

    def test_hostile_text_is_escaped_in_the_data_block_and_stays_inert(self):
        with tempfile.TemporaryDirectory() as t:
            model, lst, ins = make(Path(t), hostile=True)
            out = Path(t) / "o"
            self.assertEqual(preview.main(asm_args(Path(t), model, lst, ins, out, "--bundle", "--checks", "")), 0)
            text = (out / "preview.html").read_text(encoding="utf-8")
            self.assertNotIn("</script><img", text)
            self.assertNotIn("onerror=alert", text.split('id="preview-data">')[0])
            blocks = re.findall(r'<script type="application/json" id="preview-data">(.*?)</script>', text, re.S)
            self.assertEqual(len(blocks), 1)
            self.assertNotIn("<", blocks[0])
            data = json.loads(blocks[0])
            comments = [t["sub"] for t in data["search"] if t["kind"] == "tag"]
            self.assertIn("</script><img src=x onerror=alert(1)> & \u2028 end", comments)
            self.assertEqual(preview.scan_bundle(text)["inline_handlers"], 0)

    def test_the_scan_finds_what_an_inert_bundle_must_not_hold(self):
        text = (self.out / "preview.html").read_text(encoding="utf-8")
        cases = {
            "external_refs": ['<img src="https://example.test/x.png">', '<link rel="stylesheet" href="x.css">',
                              '<script src="a.js"></script>', "<style>@import 'x.css'; b{background:url(//h/x)}</style>"],
            "inline_handlers": ['<button onclick="f()">x</button>', '<a href="javascript:f()">x</a>']}
        for key, snippets in cases.items():
            for s in snippets:
                self.assertGreater(preview.scan_bundle(text.replace("</body>", s + "</body>"))[key], 0, s)

    def test_a_tampered_script_no_longer_hashes_to_the_recorded_value(self):
        text = (self.out / "preview.html").read_text(encoding="utf-8")
        tampered = text.replace("'use strict';", "'use strict'; var x = 1;", 1)
        self.assertNotEqual(preview.scan_bundle(tampered)["script_hashes"], self.doc()["bundle"]["script_hashes"])

    def test_the_site_is_the_multi_file_preview(self):
        index = (self.out / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn('src="renderer.js"', index)
        self.assertIn('href="style.css"', index)

    def test_the_data_of_the_asm_mode_places_every_design_item_and_accounts_for_the_rest(self):
        data = preview.prepare_asm(json.loads(self.model.read_text(encoding="utf-8")),
                                   {fixture(n)["page"]: fixture(n) for n in DESIGNS}, fixture("asm-faceplates.json"),
                                   fixture("asm-tables.json"), (1280, 720))
        drawn = {i["uid"] for p in data["pages"] for i in p["items"]}
        # the rows of the pop-up sets sit in the faceplates, the rest on the pages
        faceplate_rows = {r["uid"] for f in data["faceplates"] for t in f["tabs"] for r in t["rows"]}
        self.assertEqual(set(data["expected"]) - drawn - faceplate_rows - {m["uid"] for m in data["markers"]}, set())
        treatments = {i["uid"]: i["treatment"] for p in data["pages"] for i in p["items"] if i["kind"] == "hidden"}
        self.assertEqual(treatments["Overview:x10"], "dropped")
        self.assertEqual(treatments["PumpStation:n4"], "not_migrated")

    def test_a_device_symbol_on_another_page_is_plain_and_still_opens_its_faceplate(self):
        data = preview.prepare_asm(json.loads(self.model.read_text(encoding="utf-8")),
                                   {fixture(n)["page"]: fixture(n) for n in DESIGNS}, fixture("asm-faceplates.json"),
                                   fixture("asm-tables.json"), (1280, 720))
        pages = {p["id"]: {i["uid"]: i for i in p["items"]} for p in data["pages"]}
        self.assertTrue(pages["Overview"]["Overview:d_pump"]["plain"])
        self.assertEqual(pages["Overview"]["Overview:d_pump"]["faceplate"], "PUMP01")
        self.assertFalse(pages["PumpStation"]["PumpStation:d_p1"]["plain"])
        self.assertNotIn("faceplate", pages["Overview"]["Overview:d_brk"])   # a switch has no library faceplate

    def test_a_pipe_of_the_asm_data_takes_its_path_and_medium_from_the_model(self):
        data = preview.prepare_asm(json.loads(self.model.read_text(encoding="utf-8")),
                                   {fixture(n)["page"]: fixture(n) for n in DESIGNS}, fixture("asm-faceplates.json"),
                                   fixture("asm-tables.json"), (1280, 720))
        pipe = next(i for p in data["pages"] for i in p["items"] if i["uid"] == "PumpStation:f3")
        self.assertEqual((pipe["path"], pipe["medium"]), ([[368, 354], [520, 354], [520, 414]], "waste"))
        readout = next(i for p in data["pages"] for i in p["items"] if i["uid"] == "PumpStation:v1")
        self.assertEqual(readout["unit"], "m")

    def test_the_dropped_and_frame_rows_of_a_popup_set_are_marked_in_both_modes(self):
        model = json.loads(self.model.read_text(encoding="utf-8"))
        asm = preview.prepare_asm(model, {fixture(n)["page"]: fixture(n) for n in DESIGNS}, fixture("asm-faceplates.json"),
                                  fixture("asm-tables.json"), (1280, 720))
        units = [asm_model.check_understanding(fixture(n), n) for n in UNIT_FILES.values()]
        recon, _ = preview.prepare_recon(units, fixture("asm-faceplates.json"), fixture("asm-tables.json"), self.ins["inventory"])
        for data in (asm, recon):
            marks = {m["uid"]: m["treatment"] for m in data["markers"]}
            self.assertEqual(marks, {"PUMP01_FP:s3": "frame", "PUMP01_FP:x5": "dropped"})
            drawn = ({i["uid"] for p in data["pages"] for i in p["items"]}
                     | {r["uid"] for f in data["faceplates"] for t in f["tabs"] for r in t["rows"]} | set(marks))
            self.assertEqual(set(data["expected"]) - drawn, set())

    def test_page_size_in_ctigs_object_form_gives_the_page_its_size(self):
        with tempfile.TemporaryDirectory() as t:
            ins = inputs(Path(t))
            f = ins["inventory"] / "units" / "PumpStation" / "unit.json"
            u = json.loads(f.read_text(encoding="utf-8"))
            u["windows"][0]["page_size"] = {"w": 1280, "h": 720}
            dump(f, u)
            units = [asm_model.check_understanding(fixture(n), n) for n in UNIT_FILES.values()]
            data, _ = preview.prepare_recon(units, fixture("asm-faceplates.json"), fixture("asm-tables.json"), ins["inventory"])
            page = next(p for p in data["pages"] if p["id"] == "PumpStation")
            self.assertEqual((page["width"], page["height"]), (1280, 720))

    def test_the_preview_reads_the_tags_map_for_units(self):
        tb = fixture("asm-tables.json")
        del tb["devices"]["TANK01"]["variables"][0]
        data = preview.prepare_asm(json.loads(self.model.read_text(encoding="utf-8")),
                                   {fixture(n)["page"]: fixture(n) for n in DESIGNS}, fixture("asm-faceplates.json"),
                                   tb, (1280, 720))
        readout = next(i for p in data["pages"] for i in p["items"] if i["uid"] == "PumpStation:v1")
        self.assertEqual(readout["unit"], "m")

    def test_the_mode_decides_the_default_checks(self):
        self.assertEqual(preview.DEFAULT_CHECKS["recon"], ["coverage", "navigation"])
        self.assertEqual(preview.DEFAULT_CHECKS["asm"], ["coverage", "navigation", "search", "dock", "float"])

    def test_faults_exit_1(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(preview.main(["--mode", "asm", "--out", t]), 1)                      # inputs missing
            self.assertEqual(preview.main(asm_args(Path(t), self.model, self.lst, self.ins, Path(t) / "o",
                                                   "--checks", "bogus")), 1)
            self.assertEqual(preview.main(asm_args(Path(t), self.model, self.lst, self.ins, Path(t) / "o") + ["--window", "big"]), 1)

    def test_the_recon_data_draws_the_originals_geometry(self):
        units = [__import__("hmi.asm_model", fromlist=["x"]).check_understanding(fixture(n), n) for n in UNIT_FILES.values()]
        data, pictures = preview.prepare_recon(units, fixture("asm-faceplates.json"), fixture("asm-tables.json"),
                                               self.ins["inventory"])
        station = next(p for p in data["pages"] if p["id"] == "PumpStation")
        tank = next(i for i in station["items"] if i["uid"] == "PumpStation:d_tank")
        self.assertEqual((tank["x"], tank["y"], tank["w"], tank["h"]), (60, 300, 140, 200))
        self.assertEqual((station["width"], station["height"]), (1024, 768))
        self.assertEqual(set(pictures), {"Overview", "PumpStation"})
        self.assertEqual(len(data["expected"]), 39)
        self.assertEqual(len(station["items"]) >= 19, True)


@unittest.skipUnless(HAVE_BROWSER, "Playwright is not importable here; run under ctig's .venv")
class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.model, cls.lst, cls.ins = make(cls.dir)
        cls.asm = cls.dir / "asm"
        cls.asm_code = preview.main(asm_args(cls.dir, cls.model, cls.lst, cls.ins, cls.asm, "--bundle", "--pictures"))
        cls.recon = cls.dir / "recon"
        cls.recon_code = preview.main(recon_args(cls.ins, cls.recon, "--bundle", "--pictures"))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def checks(self, out):
        return {c["name"]: c for c in json.loads((out / "checks.json").read_text(encoding="utf-8"))["checks"]}

    def test_the_asm_mode_passes_every_check(self):
        self.assertEqual(self.asm_code, 0, json.dumps(self.checks(self.asm), indent=1)[:3000])
        c = self.checks(self.asm)
        self.assertEqual(set(c), {"coverage", "navigation", "search", "dock", "float"})
        self.assertTrue(all(x["ok"] for x in c.values()))

    def test_the_recon_mode_passes_its_checks(self):
        self.assertEqual(self.recon_code, 0, json.dumps(self.checks(self.recon), indent=1)[:3000])
        c = self.checks(self.recon)
        self.assertEqual(set(c), {"coverage", "navigation"})

    def test_coverage_counts_every_uid(self):
        c = self.checks(self.asm)["coverage"]
        self.assertEqual((c["expected"], c["found"]), (39, 39))
        c = self.checks(self.recon)["coverage"]
        self.assertEqual((c["expected"], c["found"]), (39, 39))

    def test_navigation_walks_every_row(self):
        c = self.checks(self.asm)["navigation"]
        self.assertEqual(c["expected"], 17)
        self.assertEqual(c["found"], 17)

    def test_pictures_are_taken_for_every_page_and_faceplate(self):
        doc = json.loads((self.asm / "checks.json").read_text(encoding="utf-8"))
        names = {(p["kind"], p["name"]) for p in doc["pictures"]}
        self.assertTrue({("page", "Overview"), ("page", "PumpStation"), ("faceplate", "PUMP01"),
                         ("faceplate", "SEQ01")} <= names)
        for p in doc["pictures"]:
            f = self.asm / p["file"]
            self.assertTrue(f.is_file())
            self.assertEqual(f.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertTrue((self.asm / "pictures" / "PumpStation.png").is_file())

    def test_the_bundle_of_the_run_is_self_contained(self):
        for out in (self.asm, self.recon):
            doc = json.loads((out / "checks.json").read_text(encoding="utf-8"))
            self.assertEqual((doc["bundle"]["external_refs"], doc["bundle"]["inline_handlers"]), (0, 0))
            self.assertEqual(validate(doc, "cadre-hmi-preview-checks-1.json"), [])

    def test_a_page_missing_from_the_design_fails_the_coverage_check(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model, lst, ins = make(d)
            station = fixture("asm-design-pumpstation.json")
            station["items"] = [i for i in station["items"] if i["uid"] != "PumpStation:v1"]
            dump(d / "designs" / "asm-design-pumpstation.json", station)
            out = d / "o"
            code = preview.main(asm_args(d, model, lst, ins, out, "--bundle", "--checks", "coverage"))
            self.assertEqual(code, 2)
            c = self.checks(out)["coverage"]
            self.assertFalse(c["ok"])
            self.assertIn("not drawn: PumpStation:v1", c["detail"])

    def test_a_navigation_row_that_ends_elsewhere_fails_the_check(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model, lst, ins = make(d)
            m = json.loads(model.read_text(encoding="utf-8"))
            row = next(n for n in m["nav"] if n["from"].startswith("menu Plant > Pump station"))
            row["route"] = "/not-this"      # the row says page; the route is only data, the page is the target
            row["target"] = "Aeration"
            m["pages"] = [p for p in m["pages"] if p["id"] != "Aeration"]   # the target page does not exist any more
            dump(model, m)
            out = d / "o"
            code = preview.main(asm_args(d, model, lst, ins, out, "--bundle", "--checks", "navigation"))
            self.assertEqual(code, 2)
            self.assertFalse(self.checks(out)["navigation"]["ok"])

    def top_at_centre(self, html: Path, page_id: str, uid: str) -> str | None:
        """The uid of the element that `elementFromPoint` finds at the centre of a control, after a real click on the
        page's entry of the tree."""
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 1280, "height": 720})
            page.goto(html.as_uri() + "#frozen")
            page.wait_for_selector("body[data-ready='1']")
            page.click(f"#tree button[data-page='{page_id}']")
            found = page.evaluate("""(uid) => { const c = document.querySelector("[data-uid='" + uid + "'] button");
                const r = c.getBoundingClientRect(); const e = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
                const o = e && e.closest('[data-uid]'); return o ? o.dataset.uid : null; }""", uid)
            b.close()
        return found

    def test_a_static_label_over_a_navigation_control_leaves_the_control_the_click_asm(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            model, lst, ins = make(d)
            des = fixture("asm-design-overview.json")
            for it in des["items"]:
                if it["uid"] == "Overview:s9":      # the heading, drawn after the controls, over the faceplate button
                    it["bbox"] = {"x": 240, "y": 170, "w": 120, "h": 50}
            dump(d / "designs" / "asm-design-overview.json", des)
            out = d / "o"
            self.assertEqual(preview.main(asm_args(d, model, lst, ins, out, "--bundle", "--checks", "")), 0)
            self.assertEqual(self.top_at_centre(out / "preview.html", "Overview", "Overview:n2"), "Overview:n2")

    def test_a_static_label_over_a_navigation_control_leaves_the_control_the_click_recon(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            ins = inputs(d)
            f = ins["inventory"] / "units" / "Overview" / "Overview.inventory.json"
            inv = json.loads(f.read_text(encoding="utf-8"))
            inv["objects"].append({"an": "9", "class": "Text", "x": 240, "y": 170, "w": 120, "h": 50, "text": "Heading",
                                   "nodes": [], "parent": None, "behaviour": {}, "tags": []})
            dump(f, inv)
            out = d / "o"
            self.assertEqual(preview.main(recon_args(ins, out, "--bundle", "--checks", "")), 0)
            self.assertEqual(self.top_at_centre(out / "preview.html", "Overview", "Overview:n2"), "Overview:n2")

    def test_the_simulation_changes_a_readout_over_time(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 1280, "height": 720})
            page.goto((self.asm / "preview.html").as_uri())
            page.wait_for_selector("body[data-ready='1']")
            page.click("#tree button[data-page='PumpStation']")
            first = page.inner_text("[data-uid='PumpStation:v1'] .val")
            page.evaluate("window.__preview && 0")
            page.wait_for_timeout(2300)
            self.assertNotEqual(page.inner_text("[data-uid='PumpStation:v1'] .val"), first)
            b.close()

    def test_nothing_in_the_page_reaches_the_network(self):
        from playwright.sync_api import sync_playwright
        seen = []
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page()
            page.on("request", lambda r: seen.append(r.url))
            page.goto((self.asm / "preview.html").as_uri())
            page.wait_for_selector("body[data-ready='1']")
            b.close()
        self.assertEqual([u for u in seen if not u.startswith(("file:", "data:"))], [])


if __name__ == "__main__":
    unittest.main()
