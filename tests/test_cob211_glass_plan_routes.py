"""COB-211 (NOTE-WFB-12 section 6.1 item 3): the glass plan takes the project's routes. With a design given,
`plan_of` lists the built model pages, the design's own routes, every descriptor route and the alert list, in that order
and without repeats; an unbuilt model page and a support route only the model names are no longer added. Without a design
the routes are as before.

Run from the repository root:  python -m unittest tests.test_cob211_glass_plan_routes
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT  # noqa: E402
from test_glass_gates_plan import make  # noqa: E402

sys.path.insert(0, str(ROOT / "tools" / "compare"))
import glass_gates  # noqa: E402

BASE = "http://x/y"


class GlassPlanRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.model, cls.bridge = make(Path(cls._tmp.name))
        cls.descs = glass_gates.descriptors_of(cls.bridge)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def routes(self, model, navtable=None, design=None):
        return glass_gates.plan_of(model, self.descs, BASE, (1280, 800), ["routes"], False, navtable, design)["routes"]

    def model_with(self, unbuilt="/not-built", support="/only-the-model-names-this"):
        model = {**self.model, "pages": [dict(p) for p in self.model["pages"]], "nav": [dict(n) for n in self.model["nav"]]}
        model["pages"].append({**model["pages"][0], "id": "unbuilt-page", "built": False, "route": unbuilt})
        model["nav"].append({"resolution": "support", "route": support})
        return model

    def test_with_a_design_an_unbuilt_page_and_a_model_support_route_drop(self):
        model = self.model_with()
        design = {"routes": [{"treatment": "page", "route": "/from-the-design"},
                             {"treatment": "support", "route": "/the-project-lacks-this"}]}
        got = self.routes(model, None, design)
        self.assertNotIn("/not-built", got)
        self.assertNotIn("/only-the-model-names-this", got)
        built = [p["route"] for p in model["pages"] if p["built"]]
        page_routes = [d["screen"]["route"] for d in self.descs]
        self.assertEqual(got, list(dict.fromkeys(built + ["/from-the-design", "/the-project-lacks-this"] + page_routes
                                                 + ["/alerts"])))

    def test_a_design_route_the_project_lacks_is_kept(self):
        got = self.routes(self.model, None, {"routes": [{"treatment": "support", "route": "/broken-link"}]})
        self.assertIn("/broken-link", got)

    def test_a_route_the_design_names_stays_though_the_model_page_is_unbuilt(self):
        got = self.routes(self.model_with(), None, {"routes": [{"treatment": "page", "route": "/not-built"}]})
        self.assertIn("/not-built", got)

    def test_without_a_design_the_routes_are_as_before(self):
        model = self.model_with()
        got = self.routes(model)
        self.assertIn("/not-built", got)
        self.assertIn("/only-the-model-names-this", got)
        self.assertIn("/alerts", got)
        self.assertEqual(len(got), len(set(got)))

    def test_every_route_is_listed_once(self):
        got = self.routes(self.model, None, {"routes": [{"treatment": "page", "route": "/alerts"}]})
        self.assertEqual(got.count("/alerts"), 1)


if __name__ == "__main__":
    unittest.main()
