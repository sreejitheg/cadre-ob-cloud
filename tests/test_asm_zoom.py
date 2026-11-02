"""Tests of the canvas zoom and the toolbar of a diagram screen (L4 contract 3.1 and 3.3, stock part): the zoom
property and its controls, the scaled canvas, the module's zoom component when the registry lists it, and the
Color button that shows only where a pipe carries a medium.

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
import json
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "plants"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_hmi as T  # noqa: E402
from hmi import parts, screen  # noqa: E402

REGISTRY = {"cadre.ob.canvaszoom": {"element": "cadre-canvaszoom", "title": "Canvas zoom", "schema": "schemas/canvaszoom.props.json",
                                    "props": {"zoom": {"type": "number", "default": 1}, "min": {"type": "number", "default": 0.5},
                                              "max": {"type": "number", "default": 4},
                                              "targetDomId": {"type": "string", "default": "cadre-canvas"},
                                              "guardBrowserZoom": {"type": "boolean", "default": True}}}}


def page(pipes=None, **screen_keys):
    d = {"schema": "cadre-hmi-screen/1", "screen": {"id": "Z", "route": "/z", "title": "Z", "view": "Screens/Z", "layout": "diagram",
                                                    "width": 1600, "height": 800, **screen_keys},
         "tagRoot": "[default]z", "symbols": [{"id": "T1", "kind": "tank", "x": 100, "y": 100, "w": 120, "h": 160},
                                              {"id": "T2", "kind": "tank", "x": 500, "y": 100, "w": 120, "h": 160}]}
    if pipes is not None:
        d["pipes"] = pipes
    return d


def pipe(medium=None):
    p = {"id": "p1", "from": {"ref": "T1", "side": "right"}, "to": {"ref": "T2", "side": "left"}}
    if medium:
        p["medium"] = medium
    return p


class ZoomCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = screen.load_contracts()

    def tearDown(self):
        screen.RENDER["target"] = "stock"
        screen.FRAME["name"] = "openbridge"

    def build(self, desc, render="stock"):
        screen.RENDER["target"] = render
        return screen.build_screen(copy.deepcopy(desc), self.contracts)[0]


class ZoomControlsTests(ZoomCase):
    def test_every_diagram_screen_has_a_zoom_of_one(self):
        for fit in (False, True):
            doc = self.build(page(fit=fit) if fit else page())
            self.assertEqual((doc["custom"]["zoom"], doc["custom"]["scale"]), (1, 1))

    def test_the_toolbar_holds_minus_the_percentage_and_plus_outside_the_scaled_box(self):
        doc = self.build(page())
        names = T.view_nodes(doc)
        tool = names["UserToolbar"]
        self.assertEqual([k["meta"]["name"] for k in tool["children"][-1]["children"]], ["ZoomOut", "ZoomReset", "ZoomIn"])
        inside = {k for k in T.view_nodes({"root": names["Sizer"]})}
        self.assertFalse({"UserToolbar", "ZoomOut", "ZoomReset", "ZoomIn"} & inside)     # the toolbar never scales
        self.assertEqual(names["ZoomReset"]["propConfig"]["props.text"]["binding"]["config"]["expression"],
                         "numberFormat({view.custom.zoom} * 100, '0') + '%'")
        self.assertEqual(names["ZoomOut"]["propConfig"]["props.enabled"]["binding"]["config"]["expression"], "{view.custom.zoom} > 0.5")
        self.assertEqual(names["ZoomIn"]["propConfig"]["props.enabled"]["binding"]["config"]["expression"], "{view.custom.zoom} < 4")

    def run_button(self, doc, name, zoom):
        code = T.view_nodes(doc)[name]["events"]["component"]["onActionPerformed"]["config"]["script"]
        view = types.SimpleNamespace(custom=types.SimpleNamespace(zoom=zoom))
        exec("def f(self):\n" + code + "\n", {"max": max, "min": min, "round": round}, ns := {})
        ns["f"](types.SimpleNamespace(view=view))
        return view.custom.zoom

    def test_the_buttons_step_by_1_25_inside_0_5_to_4_and_the_percentage_resets(self):
        doc = self.build(page())
        self.assertAlmostEqual(self.run_button(doc, "ZoomIn", 1), 1.25)
        self.assertAlmostEqual(self.run_button(doc, "ZoomOut", 1), 0.8)
        self.assertEqual(self.run_button(doc, "ZoomIn", 3.5), 4)          # held at the top
        self.assertEqual(self.run_button(doc, "ZoomOut", 0.6), 0.5)       # and at the bottom
        self.assertEqual(self.run_button(doc, "ZoomReset", 2.4414), 1)
        z = 1.0
        for _ in range(20):
            z = self.run_button(doc, "ZoomIn", z)
        self.assertEqual(z, 4)

    def test_a_page_without_a_toolbar_has_no_controls_but_keeps_the_zoom(self):
        doc = self.build(dict(page(), toolbar=False))
        self.assertEqual([k["meta"]["name"] for k in doc["root"]["children"]], ["Canvas"])
        self.assertEqual(doc["custom"]["zoom"], 1)


class CanvasZoomComponentTests(ZoomCase):
    def canvas(self, doc):
        return T.view_nodes(doc)["Canvas"]

    def test_the_module_component_is_the_last_child_of_the_canvas_when_the_registry_lists_it(self):
        with mock.patch.object(screen, "module_registry", return_value=REGISTRY):
            doc = self.build(page(), render="module")
        kids = self.canvas(doc)["children"]
        self.assertEqual([k["meta"]["name"] for k in kids], ["Sizer", "CanvasZoom"])
        z = kids[-1]
        self.assertEqual(z["type"], "cadre.ob.canvaszoom")
        self.assertEqual(z["props"], {"min": 0.5, "max": 4.0, "targetDomId": "cadre-canvas", "guardBrowserZoom": True})
        self.assertEqual(z["propConfig"]["props.zoom"]["binding"], {"config": {"path": "view.custom.zoom", "bidirectional": True},
                                                                    "type": "property"})   # the component writes the zoom
        self.assertEqual(z["position"], {"basis": "0px", "grow": 0, "shrink": 0})            # nothing visible
        self.assertEqual(self.canvas(doc)["meta"]["domId"], z["props"]["targetDomId"])

    def test_nothing_is_emitted_without_the_listing_or_off_the_module_rendering(self):
        with mock.patch.object(screen, "module_registry", return_value={}):
            doc = self.build(page(), render="module")
        self.assertEqual([k["meta"]["name"] for k in self.canvas(doc)["children"]], ["Sizer"])
        with mock.patch.object(screen, "module_registry", return_value=REGISTRY):
            doc = self.build(page(), render="stock")
        self.assertEqual([k["meta"]["name"] for k in self.canvas(doc)["children"]], ["Sizer"])

    def test_a_prop_the_registry_does_not_list_is_not_written(self):
        reg = copy.deepcopy(REGISTRY)
        del reg["cadre.ob.canvaszoom"]["props"]["guardBrowserZoom"]
        del reg["cadre.ob.canvaszoom"]["props"]["min"]
        with mock.patch.object(screen, "module_registry", return_value=reg):
            doc = self.build(page(), render="module")
        z = T.view_nodes(doc)["CanvasZoom"]
        self.assertEqual(set(z["props"]), {"max", "targetDomId"})

    def test_the_repository_registry_is_read_as_json(self):
        reg = screen.module_registry()
        self.assertIn("cadre.ob.pump", reg)         # the module's own registry (module/components.json)
        self.assertIsInstance(reg["cadre.ob.pump"]["props"], dict)


class ColorButtonTests(ZoomCase):
    def toolbar(self, desc):
        return [k["meta"]["name"] for k in T.view_nodes(self.build(desc))["UserToolbar"]["children"]]

    def test_color_shows_only_where_a_pipe_carries_a_medium_other_than_neutral(self):
        self.assertEqual(self.toolbar(page()), ["IdTag", "Readout", "Zoom"])                       # no pipes
        self.assertEqual(self.toolbar(page([pipe()])), ["IdTag", "Readout", "Zoom"])               # a pipe of no medium
        self.assertEqual(self.toolbar(page([pipe("neutral")])), ["IdTag", "Readout", "Zoom"])
        self.assertEqual(self.toolbar(page([pipe("fresh-water")])), ["Color", "IdTag", "Readout", "Zoom"])
        self.assertEqual(self.toolbar(page([pipe(), dict(pipe("steam"), id="p2")])), ["Color", "IdTag", "Readout", "Zoom"])

    def test_the_color_mode_still_paints_the_medium(self):
        doc = self.build(page([pipe("sea-water")]))
        cfg = json.dumps(T.view_nodes(doc)["Pipes"]["propConfig"])
        self.assertIn("{view.custom.colorMode}", cfg)
        self.assertIn("--automation-medium-sea-water", cfg)


if __name__ == "__main__":
    unittest.main()
