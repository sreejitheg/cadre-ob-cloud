"""Own tests of WP-W06 (the generator's module wrap, NOTE-WFB-10 section 16.3), adapted to module 0.8.0 (rulings R1 and R4):
what the builder added beyond the tester's `tests/test_module_generator.py`. The status word of a generator symbol (On or Off
from `state`), the symbols that stay on the library's view, the generator's guards (bundle tags and the tag in the pinned
manifest) and the pin check's named root. The generator is wrapped on the indicator element here, not on the automation
button with two icon files as the Sandbox had it. Needs no gateway, no Gradle, no esbuild and no npm.

Run from the repository root:  python -m unittest tests.test_module_generator_wrap
"""
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
# The main checkout's `module/web`: the owner's Windows path, or that of the folder named by CADRE_OB_MAIN_CHECKOUT
# (CLAUDE.md section 4; the cloud names this repository).
MAIN_WEB = Path(os.environ.get("CADRE_OB_MAIN_CHECKOUT") or r"F:\repos\Cadre-Sandbox-OpenBridge") / "module" / "web"


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
    """The component is the indicator disc: it cannot show these, so the generator's symbol keeps the library view."""

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def drawn(self, **params) -> bool:
        return screen.module_drawn({"kind": "generator", "params": params})

    def test_the_plain_symbol_is_drawn_by_the_module(self):
        self.assertTrue(self.drawn())
        self.assertTrue(self.drawn(on=True, variant="regular", alert=True))

    def test_the_variants_the_marks_and_the_progress_ring_the_indicator_lacks_stay_on_the_view(self):
        # 0.8.0: the Sandbox's component drew the flat variant, the duty mark and the out of service greying; the indicator
        # draws none of them (MODULE_NEEDS, and `parts.SYMBOL_PARAMS` for the two marks), so the symbol keeps the view
        self.assertFalse(self.drawn(variant="flat"))
        self.assertFalse(self.drawn(badgeDuty=True))
        self.assertFalse(self.drawn(outOfService=True))
        self.assertFalse(self.drawn(activated=True))
        self.assertFalse(self.drawn(progress=True))

    def test_a_generator_set_and_the_double_variant_stay_on_the_view_and_a_vertical_symbol_does_not(self):
        self.assertFalse(self.drawn(picture="genset"))
        self.assertFalse(self.drawn(variant="double"))
        # the Sandbox kept a vertical generator on the view; a disc has no orientation, so `vertical` is dropped (MODULE_DROP)
        self.assertTrue(self.drawn(vertical=True))

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

    def test_a_bundle_that_lacks_an_element_is_reported(self):
        tags = [c["tag"] for c in self.gen.COMPONENTS]
        full = " ".join(f'customElement("{t}")' for t in tags)
        self.assertEqual(self.gen.check_bundle(full), [])
        # 0.8.0 wraps the generator on the indicator: its tag is checked like every other (no icon tags are checked)
        self.assertEqual(self.gen.check_bundle(full.replace('"obc-indicator-generator"', '"x"')), ["obc-indicator-generator"])
        self.assertEqual(self.gen.check_bundle(""), sorted(set(tags)))

    @unittest.skipUnless((MAIN_WEB / "node_modules").is_dir(), "the main checkout's node_modules is absent")
    def test_the_generators_tag_is_declared_by_the_pinned_manifest(self):
        # in place of the Sandbox's check of the two icon tags against the pinned icon files (`check_icons`, which this
        # generator lacks): the element tag is looked up in the pinned package's manifest, and an unknown tag ends the run
        manifest = json.loads((MAIN_WEB / "node_modules/@oicl/openbridge-webcomponents/custom-elements.json")
                              .read_text(encoding="utf-8"))
        decl = self.gen.declaration(manifest, "obc-indicator-generator")
        self.assertEqual(decl["tagName"], "obc-indicator-generator")
        with self.assertRaises(SystemExit):
            self.gen.declaration(manifest, "obc-indicator-generator-nonesuch")

    def test_the_status_row_of_the_indicator_is_the_wrappers_not_the_elements(self):
        js = (MODULE / "gateway/src/main/resources/mounted/js/cadre-ob.js").read_text(encoding="utf-8")
        wrapper = js.split("var COMPONENTS =")[1]
        self.assertNotIn("applyButtonStatus", wrapper)      # the Sandbox's wrap on the button
        self.assertIn("stack.readouts = show ? [{ type: p.on ? 'state-on' : 'state-off', value: word, hasIcon: true }] : [];",
                      wrapper)
        self.assertIn("if (spec.generator) this.applyGenerator(el, p);", wrapper)


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
