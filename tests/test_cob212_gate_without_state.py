"""COB-212 (NOTE-WFB-12 section 7.2): a switch the design draws with no state passes in the flow, and gate G3 refuses a
view whose expression names a `view.custom` property the view does not define.

A symbol of a gated kind with neither `bind[<state>]` nor `params[<state>]` has no `custom.g_<id>` in the built view, so a
pipe expression that named it failed to bind and Perspective framed the pipe layer. The flow now treats such a symbol as a
junction (`diagram.build_graph`), so `compile_flow` and `solve` agree and no expression names it.

Run from the repository root:  python -m unittest tests.test_cob212_gate_without_state
"""
import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import diagram, gates, screen  # noqa: E402

CONTRACTS = screen.load_contracts()


def desc(switch: dict) -> dict:
    """A source tank, the switch and a sink tank on two pipes (the other symbols and pipes of the page removed)."""
    d = json.loads((ROOT / "screens/wtp/intake.json").read_text(encoding="utf-8"))
    tank = next(s for s in d["symbols"] if s["kind"] == "tank")
    d["symbols"] = [dict(tank, id="TK1", x=100, y=200), dict(switch, id="SW1", x=300, y=200, w=48, h=48),
                    dict(tank, id="TK2", x=500, y=200)]
    d["pipes"] = [{"id": "p1", "from": {"ref": "TK1", "side": "right"}, "to": {"ref": "SW1", "side": "left"}},
                  {"id": "p2", "from": {"ref": "SW1", "side": "right"}, "to": {"ref": "TK2", "side": "left"}}]
    d["junctions"], d["labels"] = [], []
    return d


NO_STATE = {"kind": "switch", "params": {"hasTag": False}}
BOUND = {"kind": "switch", "params": {"hasTag": False}, "bind": {"on": "SW1/state"}}
STATED = {"kind": "switch", "params": {"hasTag": False, "on": True}}


class TheFlow(unittest.TestCase):
    def graph(self, switch):
        g, _ = diagram.build_graph(desc(switch), CONTRACTS)
        return g

    def test_a_switch_with_no_state_is_a_junction_in_the_flow(self):
        g = self.graph(NO_STATE)
        self.assertEqual((g.nodes["SW1"], g.gate_of), ("pass", {}))
        self.assertEqual(diagram.compile_flow(g), {"p1": [frozenset()], "p2": [frozenset()]})   # always
        self.assertEqual(diagram.solve(g, {}), {"p1", "p2"})                                    # the solver agrees

    def test_a_switch_that_binds_or_states_its_state_stays_a_gate(self):
        for sw in (BOUND, STATED):
            g = self.graph(sw)
            self.assertEqual((g.nodes["SW1"], g.gate_of), ("gate", {"SW1": "SW1"}), sw)
            self.assertEqual(diagram.compile_flow(g)["p1"], [frozenset({"SW1"})])
            self.assertEqual(diagram.solve(g, {"SW1": False}), set())
            self.assertEqual(diagram.solve(g, {"SW1": True}), {"p1", "p2"})

    def test_every_gated_kind_follows_its_own_state_name(self):
        for kind, state in diagram.GATED.items():
            d = desc({"kind": kind, "params": {}})
            self.assertEqual(diagram.build_graph(d, CONTRACTS)[0].nodes["SW1"], "pass", kind)
            d = desc({"kind": kind, "params": {}, "bind": {state: "SW1/state"}})
            self.assertEqual(diagram.build_graph(d, CONTRACTS)[0].nodes["SW1"], "gate", kind)


class TheBuiltView(unittest.TestCase):
    def view(self, switch):
        doc, _info = screen.build_screen(desc(switch), CONTRACTS)
        text = json.dumps(doc)
        return doc, text

    def test_the_pipe_expressions_name_no_state_a_stateless_switch_lacks(self):
        doc, text = self.view(NO_STATE)
        self.assertNotIn("g_SW1", text)
        self.assertNotIn("g_SW1", doc["custom"])

    def test_a_bound_switch_defines_its_state_and_the_pipes_name_it(self):
        doc, text = self.view(BOUND)
        self.assertIn("g_SW1", doc["custom"])
        self.assertIn("{view.custom.g_SW1}", text)

    def test_every_custom_name_an_expression_uses_is_defined(self):
        for sw in (NO_STATE, BOUND, STATED):
            doc, text = self.view(sw)
            named = set(re.findall(r"\{view\.custom\.([^.}\[\s]+)", text))
            self.assertLessEqual(named, set(doc["custom"]), sw)


class GateG3(unittest.TestCase):
    def project(self, d: Path, custom: dict, expression: str) -> Path:
        v = d / gates.P / "views" / "Screens" / "A"
        v.mkdir(parents=True)
        doc = {"custom": custom, "params": {}, "propConfig": {}, "props": {},
               "root": {"type": "ia.container.coord", "children": [
                   {"type": "ia.shapes.svg", "propConfig": {"props.x": {"binding": {"type": "expr",
                                                                                   "config": {"expression": expression}}}}}]}}
        (v / "view.json").write_text(json.dumps(doc), encoding="utf-8")
        return d

    def run_g3(self, custom, expression):
        with tempfile.TemporaryDirectory() as t:
            return gates.g3_view_keys(self.project(Path(t), custom, expression))

    def test_an_expression_naming_an_undefined_custom_property_fails_naming_it(self):
        res = self.run_g3({"g_a": False}, "{view.custom.g_a} && {view.custom.g_missing}")
        self.assertFalse(res["ok"])
        self.assertEqual(len(res["problems"]), 1)
        self.assertIn("Screens/A", res["problems"][0])
        self.assertIn("view.custom.g_missing", res["problems"][0])

    def test_defined_names_pass_including_a_hyphen_and_a_nested_key(self):
        res = self.run_g3({"g_a": False, "g_ind-level-high": False, "can": {"W1": True}},
                          "{view.custom.g_a} || {view.custom.g_ind-level-high} || {view.custom.can.W1}")
        self.assertEqual(res, {"ok": True, "problems": []})

    def test_a_property_only_a_binding_would_make_is_undefined(self):
        with tempfile.TemporaryDirectory() as t:
            d = self.project(Path(t), {}, "{view.custom.g_bound} && {view.custom.g_none}")
            f = d / gates.P / "views" / "Screens" / "A" / "view.json"
            doc = json.loads(f.read_text(encoding="utf-8"))
            doc["propConfig"] = {"custom.g_bound": {"binding": {"type": "tag", "config": {"path": "[default]x"}}}}
            f.write_text(json.dumps(doc), encoding="utf-8")
            res = gates.g3_view_keys(d)
        self.assertEqual(len(res["problems"]), 2)  # contract 7.2 item 2: a key of the view's `custom` only
        self.assertIn("view.custom.g_bound", res["problems"][0])
        self.assertIn("view.custom.g_none", res["problems"][1])

    def test_the_view_level_key_rule_is_unchanged(self):
        with tempfile.TemporaryDirectory() as t:
            d = self.project(Path(t), {}, "true")
            f = d / gates.P / "views" / "Screens" / "A" / "view.json"
            doc = json.loads(f.read_text(encoding="utf-8"))
            doc["propConfig"] = {"view.bad": {}}
            f.write_text(json.dumps(copy.deepcopy(doc)), encoding="utf-8")
            res = gates.g3_view_keys(d)
        self.assertFalse(res["ok"])
        self.assertIn("view-level key 'view.bad'", res["problems"][0])


if __name__ == "__main__":
    unittest.main()
