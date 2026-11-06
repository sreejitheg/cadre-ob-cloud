"""Own tests of WP-W06 (the generator's module wrap, NOTE-WFB-10 section 16.3): what the builder added beyond the tester's
`tests/test_module_generator.py`. The status word of a generator symbol (On or Off from `state`), the symbols that stay on the library's view, the generator's guards (bundle tags and icon files) and the pin check's
named root. Needs no gateway, no Gradle, no esbuild and no npm.

Run from the repository root:  python -m unittest tests.test_module_generator_wrap
"""
import copy
import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "module"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(MODULE / "tools"))

from hmi import screen  # noqa: E402
import verify_pin  # noqa: E402

VIEW = "com.inductiveautomation.perspective/views/Screens/Intake/view.json"
MAIN_WEB = Path(r"F:\repos\Cadre-Sandbox-OpenBridge\module\web")


def generator_module():
    spec = importlib.util.spec_from_file_location("gen_module_assets_wrap", MODULE / "tools/gen_module_assets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def descriptor(symbols: list) -> dict:
    d = json.loads((ROOT / "screens/wtp/intake.json").read_text(encoding="utf-8"))
    d["symbols"], d["pipes"], d["junctions"], d["labels"] = symbols, [], [], []
    return d


def nodes_of(child) -> dict:
    out = {}

    def walk(n):
        out[n.get("meta", {}).get("name")] = n
        for c in n.get("children") or []:
            walk(c)
    walk(json.loads(child.files[VIEW])["root"])
    return out


def devices_model(members: dict) -> dict:
    root = "[default]cadre_hmi_wtp"
    return {"schema": "cadre-hmi-devices/1", "tagRoot": root,
            "devices": [{"id": "GEN1", "kind": "generator", "title": "GEN-1", "label": "Standby generator", "unit": "",
                         "members": {m: {"type": t, "access": "read"} for m, t in members.items()}}]}


def device_symbol(**params) -> dict:
    return {"id": "G1", "kind": "generator", "x": 300, "y": 300, "w": 48, "h": 48, "device": "GEN1",
            "bind": {"on": "GEN1/state"}, "params": {"hasTag": True, "tag": "GEN-1", **params}}


class TheStatusWordOfAGeneratorSymbol(unittest.TestCase):
    def tearDown(self):
        screen.RENDER["target"] = "stock"
        screen.RENDER["devices"] = {}

    def build(self, members, **params):
        child, reports = screen.build_child("cadre_hmi_t", [descriptor([device_symbol(**params)])], "T", render="module",
                                            devices=devices_model(members) if members else None)
        return child, nodes_of(child)["G1"]

    def words(self, node) -> str:
        return node["propConfig"]["props.statusText"]["binding"]["config"]["expression"]

    def test_with_a_run_text_member_the_word_is_still_on_or_off_from_the_state(self):
        child, node = self.build({"state": "Boolean", "runText": "String"})
        self.assertEqual(self.words(node), "if({view.custom.g_G1}, 'On', 'Off')")
        self.assertNotIn("rt_G1", json.loads(child.files[VIEW]).get("custom", {}))   # runText stays on the faceplate

    def test_without_a_devices_file_the_word_is_on_or_off_from_the_state(self):
        _, node = self.build(None)
        self.assertEqual(self.words(node), "if({view.custom.g_G1}, 'On', 'Off')")

    def test_a_statement_of_the_words_in_the_descriptor_is_kept(self):
        _, node = self.build({"state": "Boolean", "runText": "String"}, statusText="Standby")
        self.assertEqual(node["props"]["statusText"], "Standby")
        self.assertNotIn("props.statusText", node.get("propConfig", {}))


class SymbolsThatStayOnTheLibrarysView(unittest.TestCase):
    """The component is the automation button: it cannot show these, so the generator's symbol keeps the library view."""

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def drawn(self, **params) -> bool:
        return screen.module_drawn({"kind": "generator", "params": params})

    def test_the_plain_symbol_is_drawn_by_the_module(self):
        self.assertTrue(self.drawn())
        self.assertTrue(self.drawn(on=True, variant="flat", alert=True, outOfService=True, badgeDuty=True))

    def test_a_generator_set_a_vertical_symbol_and_the_double_variant_stay_on_the_view(self):
        self.assertFalse(self.drawn(picture="genset"))
        self.assertFalse(self.drawn(vertical=True))
        self.assertFalse(self.drawn(variant="double"))

    def test_a_control_interlock_or_command_lock_badge_stays_on_the_view(self):
        self.assertFalse(self.drawn(badgeControl="manual"))
        self.assertFalse(self.drawn(badgeInterlock="interlock"))
        self.assertFalse(self.drawn(badgeCommandLocked="command-locked"))

    def test_a_drawn_generator_is_given_none_of_the_library_only_parameters(self):
        d = descriptor([{"id": "G1", "kind": "generator", "x": 300, "y": 300, "w": 48, "h": 48,
                         "params": {"on": True, "picture": "symbol", "vertical": False, "hasSpeed": False, "speed": 0,
                                    "value": 0, "badgeControl": "none", "badgeInterlock": "none",
                                    "badgeCommandLocked": "none"}}])
        child, reports = screen.build_child("cadre_hmi_t", [d], "T", render="module")
        node = nodes_of(child)["G1"]
        self.assertEqual(node["type"], "cadre.ob.generator")
        listed = screen.module_props("cadre.ob.generator")
        self.assertTrue(set(node["props"]) <= listed, set(node["props"]) - listed)
        self.assertEqual(reports["/intake"]["errors"], [])


class TheGeneratorsGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = generator_module()

    def test_a_bundle_that_lacks_an_element_or_an_icon_is_reported(self):
        tags = [c["tag"] for c in self.gen.COMPONENTS] + ["obi-electric-generator-on", "obi-electric-generator-off"]
        full = " ".join(f'customElement("{t}")' for t in tags)
        self.assertEqual(self.gen.check_bundle(full), [])
        self.assertEqual(self.gen.check_bundle(full.replace('"obi-electric-generator-off"', '"x"')),
                         ["obi-electric-generator-off"])
        self.assertEqual(self.gen.check_bundle(""), sorted(set(tags)))

    @unittest.skipUnless((MAIN_WEB / "node_modules").is_dir(), "the main checkout's node_modules is absent")
    def test_the_icon_tags_are_checked_against_the_pinned_icon_files(self):
        with mock.patch.object(self.gen, "PKG", MAIN_WEB / "node_modules/@oicl/openbridge-webcomponents"):
            self.gen.check_icons()                         # the real tags: no exit
            bad = copy.deepcopy(self.gen.COMPONENTS)
            next(c for c in bad if c.get("icons"))["icons"]["on"] = "obi-electric-generator-nonesuch"
            with mock.patch.object(self.gen, "COMPONENTS", bad), self.assertRaises(SystemExit):
                self.gen.check_icons()

    def test_the_status_row_of_the_automation_button_is_the_wrappers_not_the_elements(self):
        js = (MODULE / "gateway/src/main/resources/mounted/js/cadre-ob.js").read_text(encoding="utf-8")
        wrapper = js.split("var COMPONENTS =")[1]
        self.assertIn("applyButtonStatus", wrapper)
        self.assertIn("el.readouts = rows", wrapper)
        self.assertIn("if (spec.icons) { this.applyButtonStatus(el, p); return; }", wrapper)


class ThePinChecksNamedRoot(unittest.TestCase):
    def test_the_environment_variable_names_the_root_and_unset_it_is_the_sibling_web_folder(self):
        with mock.patch.dict(os.environ, {verify_pin.ROOT_ENV: str(MAIN_WEB)}):
            self.assertEqual(verify_pin.web_root(), MAIN_WEB)
        env = {k: v for k, v in os.environ.items() if k != verify_pin.ROOT_ENV}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(verify_pin.web_root(), MODULE / "web")

    @unittest.skipUnless((MAIN_WEB / "node_modules").is_dir(), "the main checkout's node_modules is absent")
    def test_the_pin_holds_at_the_named_root_against_the_tracked_manifest(self):
        self.assertEqual(verify_pin.verify(MAIN_WEB), [])


if __name__ == "__main__":
    unittest.main()
