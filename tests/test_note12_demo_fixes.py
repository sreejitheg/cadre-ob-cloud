"""Tests written from NOTE-WFB-12 revision 0.3 alone (sections 6.1 item 3 and 7), apart from the builder.

T4.4: `tools/compare/glass_gates.py` `plan_of` with a design takes the project's routes (the built model pages, the
navigation table's and the design's routes, every descriptor route and the alert list) and no unbuilt model page or
model support route the design does not name; without a design the routes are as before.
T5.1 to T5.5 and invariants I6, I7 (section 7.6): a gate symbol with no state passes (`diagram.build_graph`,
`compile_flow`, `screen.build_screen`) while one that binds or states its state stays a gate; G3 fails a view whose
expression names an undefined `view.custom` property; the generator and a pump are drawn as their module types under
`--render module` (revision 0.4: nothing is held).

Every name is synthetic (the library's own sample plant and invented routes). Needs no gateway.

Run from the repository root:  python -m unittest tests.test_note12_demo_fixes
"""
import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "compare"))

from hmi import diagram, gates, screen  # noqa: E402
import glass_gates  # noqa: E402

VIEW = "com.inductiveautomation.perspective/views/Screens/Intake/view.json"
BASE = "http://localhost:8088/data/perspective/client/cadre_hmi_note12"
WINDOW = (1280, 800)


# ---- T4.4: the glass plan takes the project's routes ------------------------------------------------------------

def model() -> dict:
    """A synthetic model: two built pages, one unbuilt page, and one support route the navigation names."""
    return {
        "pages": [
            {"id": "pa", "route": "/built-a", "title": "Built A", "built": True, "node": "n1"},
            {"id": "pb", "route": "/built-b", "title": "Built B", "built": True, "node": "n1"},
            {"id": "pu", "route": "/unbuilt-u", "title": "Unbuilt U", "built": False, "node": "n1"},
        ],
        "nav": [
            {"resolution": "support", "route": "/support-s"},
            {"resolution": "page", "route": "/built-a"},
        ],
        "devices": {}, "tags": [], "nodes": [{"id": "n1", "parent": None}],
    }


def descriptor(route: str) -> dict:
    return {"screen": {"route": route, "title": "D", "width": 1280, "height": 800}, "symbols": [], "pipes": []}


def plan_routes(design, navtable=None, descriptors=None) -> list:
    descriptors = descriptors if descriptors is not None else [descriptor("/desc-c")]
    return glass_gates.plan_of(model(), descriptors, BASE, WINDOW, ["routes"], False,
                               navtable=navtable, design=design)["routes"]


def design_of(*routes: tuple) -> dict:
    return {"routes": [{"route": r, "treatment": t} for r, t in routes]}


class PlanRoutesWithADesign(unittest.TestCase):
    def test_an_unbuilt_model_page_and_a_model_support_route_are_dropped(self):
        routes = plan_routes(design_of(("/design-d", "page")))
        self.assertNotIn("/unbuilt-u", routes)
        self.assertNotIn("/support-s", routes)

    def test_built_pages_design_routes_descriptor_routes_and_alerts_are_kept(self):
        routes = plan_routes(design_of(("/design-d", "page"), ("/design-s", "support")))
        for kept in ("/built-a", "/built-b", "/design-d", "/design-s", "/desc-c", glass_gates.ALERTS_ROUTE):
            self.assertIn(kept, routes)

    def test_a_route_the_design_names_is_kept_even_when_the_project_lacks_it(self):
        # a real broken link (the design's /trends of WFB-293): the evidence keeps reporting it
        routes = plan_routes(design_of(("/missing-in-project", "support")))
        self.assertIn("/missing-in-project", routes)

    def test_a_support_route_the_design_names_is_kept(self):
        routes = plan_routes(design_of(("/support-s", "support")))
        self.assertIn("/support-s", routes)

    def test_the_order_is_built_pages_navtable_design_descriptors_then_alerts_without_repeats(self):
        design = design_of(("/design-d", "page"), ("/built-a", "page"))      # one repeats a built page
        navtable = [{"route": "/nav-e"}, {"route": "/built-b"}]              # one repeats a built page
        routes = plan_routes(design, navtable=navtable)
        self.assertEqual(routes, ["/built-a", "/built-b", "/nav-e", "/design-d", "/desc-c", "/alerts"])
        self.assertEqual(len(routes), len(set(routes)))

    def test_alerts_is_last_and_present_without_a_descriptor(self):
        routes = plan_routes(design_of(("/design-d", "page")), descriptors=[])
        self.assertEqual(routes[-1], glass_gates.ALERTS_ROUTE)

    def test_an_empty_design_still_drops_the_unbuilt_and_support_routes(self):
        routes = plan_routes({})
        self.assertEqual(routes, ["/built-a", "/built-b", "/desc-c", "/alerts"])


class PlanRoutesWithoutADesign(unittest.TestCase):
    def test_the_routes_are_as_before(self):
        routes = plan_routes(None)
        # every model page (built or not), the model's support routes (sorted), the descriptors', then the alert list
        self.assertEqual(routes, ["/built-a", "/built-b", "/unbuilt-u", "/support-s", "/desc-c", "/alerts"])

    def test_the_navigation_tables_own_routes_come_after_the_support_routes(self):
        routes = plan_routes(None, navtable=[{"route": "/nav-e"}])
        self.assertEqual(routes, ["/built-a", "/built-b", "/unbuilt-u", "/support-s", "/nav-e", "/desc-c", "/alerts"])


# ---- helpers for the screen tests -------------------------------------------------------------------------------

def screen_descriptor(symbols: list) -> dict:
    d = json.loads((ROOT / "screens/wtp/intake.json").read_text(encoding="utf-8"))
    d["symbols"], d["pipes"], d["junctions"], d["labels"] = symbols, [], [], []
    return d


def symbol(kind: str, n: int) -> dict:
    return {"id": f"S{n}", "kind": kind, "x": 50 + 60 * n, "y": 300, "w": 48, "h": 48,
            "params": {"hasTag": True, "tag": f"T{n}"}, "bind": {}}


# ---- T5.1, T5.2: a gate with no state passes --------------------------------------------------------------------

CUSTOM_REF = re.compile(r"\{view\.custom\.([\w-]+)")


def chain(*switches: dict) -> dict:
    """A tank, the given gate symbols in series on one pipe path, and a tank."""
    symbols = [{"id": "TA", "kind": "tank", "x": 0, "y": 0, "w": 100, "h": 100}]
    for n, extra in enumerate(switches):
        symbols.append({"id": f"SW{n + 1}", "kind": "switch", "x": 200 + 100 * n, "y": 14, "w": 48, "h": 48, **extra})
    symbols.append({"id": "TB", "kind": "tank", "x": 200 + 100 * len(switches) + 100, "y": 0, "w": 100, "h": 100})
    ids = [s["id"] for s in symbols]
    pipes = [{"id": f"p{n}", "from": {"ref": a, "side": "right"}, "to": {"ref": b, "side": "left"}}
             for n, (a, b) in enumerate(zip(ids, ids[1:]))]
    return {"screen": {"width": 1000, "height": 400}, "junctions": [], "symbols": symbols, "pipes": pipes}


def graph_of(desc: dict):
    return diagram.build_graph(desc, screen.load_contracts())[0]


def undefined_refs(doc: dict) -> set:
    """Every `{view.custom.<name>}` the document names that its `custom` does not define."""
    return set(CUSTOM_REF.findall(json.dumps(doc))) - set(doc.get("custom", {}))


class AGateWithNoStatePasses(unittest.TestCase):
    def test_t5_1_a_switch_with_no_state_is_a_pass_node_like_a_junction(self):
        g = graph_of(chain({}))
        self.assertEqual((g.nodes["SW1"], g.gate_of), ("pass", {}))
        self.assertEqual(diagram.compile_flow(g), {"p0": [frozenset()], "p1": [frozenset()]})   # always flowing
        self.assertEqual(diagram.solve(g, {}), {"p0", "p1"})                                    # the reference agrees

    def test_t5_1_no_pipe_expression_names_the_switch_and_g6_passes(self):
        doc, info = screen.build_screen(chain({}), screen.load_contracts())
        self.assertEqual((info["errors"], info["gaps"]), ([], []))
        self.assertTrue(info["flow"]["ok"])
        self.assertFalse("g_SW1" in json.dumps(doc))              # not defined, not named by any expression
        self.assertEqual(undefined_refs(doc), set())

    def test_t5_1_a_switch_that_only_declares_no_tag_still_passes(self):
        g = graph_of(chain({"params": {"hasTag": False}}))
        self.assertEqual((g.nodes["SW1"], g.gate_of), ("pass", {}))

    def test_t5_1_the_rule_holds_for_every_gated_kind(self):
        for kind in diagram.GATED:
            with self.subTest(kind=kind):
                desc = chain({})
                desc["symbols"][1]["kind"] = kind
                g = graph_of(desc)
                self.assertEqual((g.nodes["SW1"], g.gate_of), ("pass", {}))

    def test_t5_2_a_switch_that_binds_or_states_its_state_stays_a_gate(self):
        for label, extra in (("bind", {"bind": {"on": "SW1/state"}}), ("param", {"params": {"on": True}}),
                             ("param false", {"params": {"on": False}})):
            with self.subTest(label):
                desc = chain(extra)
                g = graph_of(desc)
                self.assertEqual((g.nodes["SW1"], g.gate_of), ("gate", {"SW1": "SW1"}))
                self.assertEqual(diagram.compile_flow(g), {"p0": [frozenset({"SW1"})], "p1": [frozenset({"SW1"})]})
                self.assertEqual(diagram.solve(g, {}), set())
                self.assertEqual(diagram.solve(g, {"SW1": True}), {"p0", "p1"})
                doc, info = screen.build_screen(desc, screen.load_contracts())
                self.assertEqual((info["errors"], info["gaps"]), ([], []))
                self.assertTrue(info["flow"]["ok"])
                self.assertIn("g_SW1", doc["custom"])                                   # defined ...
                self.assertIn("{view.custom.g_SW1}", json.dumps(doc))                   # ... and named by the pipe
                self.assertEqual(undefined_refs(doc), set())

    def test_a_stateless_switch_beside_a_bound_one_leaves_only_the_bound_one_a_gate(self):
        desc = chain({}, {"bind": {"on": "SW2/state"}})
        g = graph_of(desc)
        self.assertEqual((g.nodes["SW1"], g.nodes["SW2"], g.gate_of), ("pass", "gate", {"SW2": "SW2"}))
        self.assertEqual(diagram.compile_flow(g)["p0"], [frozenset({"SW2"})])
        doc, info = screen.build_screen(desc, screen.load_contracts())
        self.assertTrue(info["flow"]["ok"])
        self.assertFalse("g_SW1" in json.dumps(doc))
        self.assertEqual(undefined_refs(doc), set())

    def test_i6_a_built_screen_with_many_states_names_no_undefined_custom_property(self):
        extras = [{}, {"bind": {"on": "SW2/state"}}, {"params": {"on": True}}, {"params": {"hasTag": False}}]
        doc, info = screen.build_screen(chain(*extras), screen.load_contracts())
        self.assertTrue(info["flow"]["ok"])
        self.assertEqual(undefined_refs(doc), set())


# ---- T5.3: G3 fails a view naming an undefined custom property --------------------------------------------------

def pump_child():
    desc = screen_descriptor([{"id": "P1", "kind": "pump", "x": 100, "y": 100, "w": 48, "h": 48,
                               "params": {"hasTag": True, "tag": "P-1"}, "bind": {"on": "P1/state"}}])
    with contextlib.redirect_stdout(io.StringIO()):
        child, _reports = screen.build_child("cadre_hmi_note12", [desc], "N")
    return child


def write_child(child, folder: Path) -> None:
    for rel, data in child.files.items():
        target = folder / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


class G3NamesAnUndefinedCustomProperty(unittest.TestCase):
    def test_t5_3_a_built_child_passes_and_a_view_that_lost_a_property_fails_naming_both(self):
        child = pump_child()
        view = json.loads(child.files[VIEW])
        self.assertIn("{view.custom.g_P1}", json.dumps(view))                  # the precondition: the pump names it
        self.assertIn("g_P1", view["custom"])
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write_child(child, folder)
            self.assertTrue(gates.g3_view_keys(folder)["ok"])
            del view["custom"]["g_P1"]
            (folder / VIEW).write_text(json.dumps(view), encoding="utf-8")
            result = gates.g3_view_keys(folder)
        self.assertFalse(result["ok"])
        named = [p for p in result["problems"] if "g_P1" in p and "Screens/Intake" in p]
        self.assertTrue(named, result["problems"])

    def test_g3_still_fails_a_view_level_key_that_is_neither_custom_nor_params(self):
        child = pump_child()
        view = json.loads(child.files[VIEW])
        view.setdefault("propConfig", {})["view.x"] = {"binding": {"type": "expr", "config": {"expression": "1"}}}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write_child(child, folder)
            (folder / VIEW).write_text(json.dumps(view), encoding="utf-8")
            result = gates.g3_view_keys(folder)
        self.assertFalse(result["ok"])
        self.assertTrue(any("view.x" in p for p in result["problems"]))


# ---- T5.4: the generator and a pump are drawn as their module types ---------------------------------------------

def build(kinds: list) -> str:
    """The Intake view text of a child that draws one symbol per kind with `--render module`."""
    symbols = [symbol(k, i) for i, k in enumerate(kinds)]
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        child, _reports = screen.build_child("cadre_hmi_note12", [screen_descriptor(symbols)], "N", render="module")
    return child.files[VIEW].decode("utf-8")


class ModuleKindsDrawAsModuleTypes(unittest.TestCase):
    def tearDown(self):
        screen.RENDER["target"] = "stock"
        screen.RENDER["devices"] = {}

    def test_t5_4_the_generator_is_drawn_as_its_module_type(self):
        text = build(["generator"])
        self.assertIn("cadre.ob.generator", text)
        self.assertNotIn("Automation/Generator", text)

    def test_t5_4_a_pump_is_drawn_as_its_module_type(self):
        self.assertIn("cadre.ob.pump", build(["pump"]))

    def test_t5_4_a_generator_and_a_pump_together_are_both_module_types(self):
        text = build(["pump", "generator"])
        self.assertIn("cadre.ob.pump", text)
        self.assertIn("cadre.ob.generator", text)

    def test_t5_4_every_module_kind_is_drawn_as_its_module_type(self):
        text = build(list(screen.MODULE_KIND))
        named = set(re.findall(r"cadre\.ob\.[A-Za-z]+", text))
        self.assertLessEqual(set(screen.MODULE_KIND.values()), named)

    def test_the_generator_is_not_held_and_module_drawn_agrees(self):
        self.assertFalse(hasattr(screen, "MODULE_HELD"))
        self.assertFalse(hasattr(screen, "MODULE_RELEASED"))
        self.assertTrue(screen.module_drawn({"kind": "generator", "params": {}}))
        self.assertTrue(screen.module_drawn({"kind": "pump", "params": {}}))

    def test_the_kind_tables_are_unchanged(self):
        self.assertEqual(screen.MODULE_KIND["generator"], "cadre.ob.generator")
        self.assertEqual(screen.KIND_VIEW["generator"], "Automation/Generator")


if __name__ == "__main__":
    unittest.main()
