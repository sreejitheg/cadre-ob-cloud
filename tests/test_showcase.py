"""Tests of the showcase project (`tools/hmi/showcase.py`, wiki page 15): every module component is a card once, every property
has an editor bound to its value, every event has a log handler, the page grouping is stable and the views pass gate G1.

Run from the repository root:  python -m unittest discover -s tests
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import gates, showcase  # noqa: E402

COMPONENTS = json.loads((ROOT / "module" / "components.json").read_text(encoding="utf-8"))
# The grouping the catalogue gives today: page id -> component count. A change to it is deliberate (a new component, a new
# section), and this table changes with it.
GROUPING = {"devices": 13, "symbols": 11, "glyphs-1": 9, "glyphs-2": 8, "pipes": 9, "charts": 11, "frame-1": 11,
            "frame-2": 11, "frame-3": 11, "alarms": 3}
VIEW_GROUPING = {"views-1": 10, "views-2": 10}   # the parent's embedded symbol views, in two pages


def nodes(n):
    yield n
    for c in n.get("children", []):
        yield from nodes(c)


class ShowcaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        every, cls.views, cls.devices = showcase.build_pages()
        cls.pages = [p for p in every if p["kind"] == "module"]
        cls.view_pages = [p for p in every if p["kind"] == "views"]
        cls.cards = {cid: (p, card) for p in cls.pages for cid, card in p["cards"].items()}

    def view_nodes(self, page):
        return {n["meta"]["name"]: n for n in nodes(self.views[page["view"]]["root"])}

    def test_every_component_is_one_card(self):
        listed = [c["id"] for p in self.pages for c in p["cards"].values()]
        self.assertEqual(sorted(listed), sorted(COMPONENTS))
        self.assertEqual(len(listed), len(set(listed)))
        self.assertEqual(len(listed), 97)
        for page in self.pages:   # the component node of a card has the component's type, once on its page
            ns = self.view_nodes(page)
            for short, card in page["cards"].items():
                self.assertEqual(ns[short]["type"], card["id"])
                self.assertEqual(ns[short]["meta"]["domId"], short)

    def test_every_property_has_an_editor_bound_to_it(self):
        total = 0
        for page in self.pages:
            ns = self.view_nodes(page)
            custom, cfg = self.views[page["view"]]["custom"], self.views[page["view"]]["propConfig"]
            for short, card in page["cards"].items():
                props = COMPONENTS[card["id"]]["props"]
                self.assertEqual(set(card["editors"]), set(props), card["id"])
                for prop, e in card["editors"].items():
                    total += 1
                    self.assertEqual(e["kind"], showcase.editor_kind(props[prop]))
                    editor = ns[f"e_{short}_{prop}"]
                    key = {"enum": "props.value", "preset": "props.value", "number": "props.value", "bool": "props.selected",
                           "text": "props.text"}[e["kind"]]
                    b = editor["propConfig"][key]["binding"]   # both ways, to the custom property the editor owns
                    self.assertEqual(b["type"], "property")
                    self.assertTrue(b["config"]["bidirectional"])
                    self.assertEqual(b["config"]["path"], "view.custom." + e["path"])
                    self.assertIn(e["path"], custom)
                    # the component reads the value (or the preset it is chosen from) through its own binding
                    self.assertIn(f"props.{prop}", ns[short]["propConfig"])
                    if e["kind"] == "preset":
                        self.assertIn(f"custom.v_{short}_{prop}", cfg)
                        self.assertGreaterEqual(len(e["presets"]), 1)
                        self.assertIn(custom[e["path"]], e["presets"])
                    if e["kind"] == "enum":   # a dropdown of exactly the schema's values
                        self.assertEqual([o["value"] for o in editor["props"]["options"]], props[prop]["enum"])
        self.assertEqual(total, 1434)

    def test_editor_kinds_follow_the_schema(self):
        kinds = {"enum": 0, "bool": 0, "number": 0, "text": 0, "preset": 0}
        for c in COMPONENTS.values():
            for p in c["props"].values():
                kinds[showcase.editor_kind(p)] += 1
        got = showcase.model_summary({"pages": self.pages})["editors"]
        self.assertEqual(got, kinds)
        self.assertGreater(kinds["preset"], 0)

    def test_every_event_has_a_log_handler(self):
        count = 0
        for page in self.pages:
            ns = self.view_nodes(page)
            for short, card in page["cards"].items():
                events = COMPONENTS[card["id"]].get("events") or {}
                self.assertEqual(card["events"], list(events))
                handlers = (ns[short].get("events") or {}).get("component", {})
                self.assertEqual(set(handlers), set(events), card["id"])
                for name, h in handlers.items():
                    count += 1
                    script = h["config"]["script"]
                    self.assertEqual(h["type"], "script")
                    self.assertIn("GF-37", script)
                    self.assertIn(f"log_{short}", script)
                    self.assertIn(f"'  {name}  '", script)
                if events:   # the log the handlers write to, and the label that shows it
                    self.assertIn(f"log_{short}", self.views[page["view"]]["custom"])
                    self.assertEqual(ns[f"log_{short}"]["propConfig"]["props.text"]["binding"]["config"]["path"],
                                     f"view.custom.log_{short}")
        self.assertEqual(count, sum(len(c.get("events") or {}) for c in COMPONENTS.values()))
        self.assertEqual(count, 94)

    def test_page_grouping_is_stable(self):
        self.assertEqual({p["id"]: len(p["components"]) for p in self.pages}, GROUPING)
        again = showcase.pages()
        self.assertEqual([p["id"] for p in again], [p["id"] for p in self.pages])
        self.assertEqual([p["components"] for p in again], [p["components"] for p in self.pages])
        self.assertEqual([p["route"] for p in self.pages][0], "/")
        self.assertLessEqual(max(len(p["components"]) for p in self.pages), showcase.MAX_PAGE + 1)
        pipes = next(p for p in self.pages if p["id"] == "pipes")["components"]
        self.assertEqual(len(pipes), 9)
        self.assertIn("cadre.ob.bus", pipes)

    def test_the_library_views_have_two_pages_with_every_embedded_symbol_view_once(self):
        from hmi import screen
        lib = screen.library_contracts()
        want = [p for p, c in lib.items() if c["kind"] != "framework"]
        self.assertEqual({p["id"]: len(p["components"]) for p in self.view_pages}, VIEW_GROUPING)
        got = [p for page in self.view_pages for p in page["components"]]
        self.assertEqual(got, want)
        self.assertEqual(len(got), len(set(got)))
        for forbidden in ("Faceplate/", "Framework/", "Trend/"):   # the frame's and the faceplates' views are left out
            self.assertFalse([p for p in got if p.startswith(forbidden)])
        for page in self.view_pages:
            ns = self.view_nodes(page)
            custom = self.views[page["view"]]["custom"]
            for short, card in page["cards"].items():
                node = ns[short]
                self.assertEqual(node["type"], "ia.display.view")
                self.assertEqual(node["props"]["path"], card["id"])
                scalars = {k for k, v in lib[card["id"]]["params"].items() if not isinstance(v, (list, dict))}
                self.assertEqual(set(card["editors"]), scalars, card["id"])
                for prop, e in card["editors"].items():
                    self.assertEqual(node["propConfig"][f"props.params.{prop}"] is not None, True)
                    b = ns[f"e_{short}_{prop}"]["propConfig"]
                    key = {"enum": "props.value", "number": "props.value", "bool": "props.selected", "text": "props.text"}[e["kind"]]
                    self.assertTrue(b[key]["binding"]["config"]["bidirectional"])
                    self.assertIn(e["path"], custom)
                # a parameter the card does not edit (a list or an object) stays as the contract states it
                for k, v in lib[card["id"]]["params"].items():
                    if k not in scalars:
                        self.assertEqual(node["props"]["params"][k], v)

    def test_chunks_are_equal_and_ordered(self):
        self.assertEqual(showcase.chunks(list(range(17))), [list(range(9)), list(range(9, 17))])
        self.assertEqual(showcase.chunks(list(range(36)), 12), [list(range(i, i + 12)) for i in (0, 12, 24)])

    def test_views_pass_g1(self):
        child, model = showcase.build_project()
        with tempfile.TemporaryDirectory() as tmp:
            out = child.write(Path(tmp))
            g1 = gates.g1_registry(out)
        self.assertTrue(g1["ok"], g1["summary"])
        self.assertEqual(len(g1["module_components"]), 97)
        self.assertEqual(model["project"], "cadre_hmi_showcase")

    def test_view_keys_are_custom_and_names_are_unique(self):
        for page in self.pages:
            doc = self.views[page["view"]]
            for key in doc["propConfig"]:
                self.assertTrue(key.startswith(("custom.", "params.")), key)   # GF-07
            names = [n["meta"]["name"] for n in nodes(doc["root"])]
            self.assertEqual(len(names), len(set(names)), page["id"])

    def test_the_device_page_opens_faceplates_as_the_samples_do(self):
        page = next(p for p in self.pages if p["id"] == "devices")
        ns = self.view_nodes(page)
        opened = [short for short, card in page["cards"].items() if card["device"]]
        self.assertEqual(len(opened), len(showcase.DEVICES))
        for short in opened:
            script = ns[short]["events"]["dom"]["onClick"]["config"]["script"]
            self.assertIn("cadre.hmi.select_device", script)
            self.assertTrue(ns[short]["custom"]["deviceId"].startswith("[default]cadre_hmi_showcase/_componentTest/"))
        symbols = self.devices["descriptor"]["symbols"]
        self.assertEqual(len(symbols), len(showcase.DEVICES))
        ids = {d["id"] for d in self.devices["model"]["devices"]}
        for s in symbols:
            self.assertIn(s["device"], ids)

    def test_the_tag_document_lands_every_bound_tag_when_imported_at_the_provider_root(self):
        """The release's tags file is imported at the root of the `default` provider (wiki 15 section 4, GF-116): a document
        rooted at `_componentTest` landed at `[default]_componentTest` on the owner's gateway and gave all 11 device cards a
        bad-quality overlay. Every tag path the device page binds must resolve inside the document, from its root."""
        doc = showcase.tag_document(self.devices)
        self.assertEqual((doc["name"], doc["tagType"]), (showcase.PROJECT, "Folder"))
        self.assertEqual([t["name"] for t in doc["tags"]], ["_componentTest"])

        def resolves(path):   # a tag path below the provider, from a document that is imported at the provider root
            node, names = {"name": "", "tags": [doc]}, path.split("/")
            for n in names:
                node = next((t for t in node.get("tags", []) if t["name"] == n), None)
                if node is None:
                    return False
            return True

        page = next(p for p in self.pages if p["id"] == "devices")
        text = json.dumps(self.views[page["view"]])
        paths = set(re.findall(r"\[default\]([A-Za-z0-9_]+/_componentTest/[A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)?)", text))
        self.assertGreaterEqual(len(paths), 20)
        self.assertEqual([q for q in sorted(paths) if not resolves(q)], [])
        self.assertTrue(all(q.startswith(showcase.PROJECT + "/") for q in paths))

    def test_the_released_tags_file_is_the_tag_document(self):
        released = ROOT / "cloud" / "release" / "cadre_hmi_showcase-tags.json"
        if not released.exists():
            self.skipTest("cloud/release is not part of the source repository")
        self.assertEqual(json.loads(released.read_text(encoding="utf-8")), showcase.tag_document(self.devices))

    def test_live_properties_follow_the_switch(self):
        for page in self.pages:
            ns = self.view_nodes(page)
            custom = self.views[page["view"]]["custom"]
            for short, card in page["cards"].items():
                for prop in card["live"]:
                    expr = ns[short]["propConfig"][f"props.{prop}"]["binding"]["config"]["expression"]
                    self.assertTrue(expr.startswith(f"if({{view.custom.live_{short}}}"), expr)
                self.assertEqual(f"live_{short}" in custom, bool(card["live"]))
                if card["live"]:
                    self.assertIn(f"live_{short}", ns)

    def test_presets_come_from_the_component_test_samples(self):
        card = self.cards["alertmenu"][1]
        self.assertEqual(card["editors"]["items"]["presets"][0], "sample")
        self.assertIn("no rows", card["editors"]["items"]["presets"])
        self.assertIn([], showcase.presets_of(COMPONENTS["cadre.ob.alertmenu"], "alert-menu", "items", []).values())
        for _p, c in self.cards.values():
            for prop, e in c["editors"].items():
                if e["kind"] == "preset":
                    self.assertTrue(e["presets"], (c["id"], prop))


if __name__ == "__main__":
    unittest.main()
