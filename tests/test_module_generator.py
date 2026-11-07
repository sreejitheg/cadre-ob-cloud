"""Tests of the generator's module wrap (module 0.8.0; the work package WP-W06 of the Sandbox, ruled R1 and R4).

The generator symbol is drawn by `obc-indicator-generator`, as component `cadre.ob.generator` (schema name `generator`,
palette title "Generator"). The Sandbox wrapped it on `obc-automation-button` with two pinned icon elements (module 0.4.4);
this repository keeps its own wrap on the indicator element (ruling R1: the module sources of this repository win), whose
wrapper selects the element's `value` scheme from `on` and draws the identifier, the status word and the alert frame itself
(`applyGenerator` and `drawGenerator` in `gen_module_assets.py`). The checklist of NOTE-WFB-10 section 8.5 names the files a
wrap changes; these tests hold each of them, offline: the entry in `COMPONENTS` of `gen_module_assets.py` with its `generator`
flag, the files the generator writes (`components.json`, `generator.props.json`, `cadre-ob.js`), the descriptor in
`CadreOb.java`, the version, the module tables of `screen.py`, `MODULE_TAGS` of the glass gates, the map row and the
component test page. The map row (`openbridge-map.json`) is carried unchanged from the Sandbox (ruling R2) and still names
the automation button and the `out_of_service` state; the tests assert the exact differences between it and this component.
Threat T10 (a wrap that fails an ASM rule) is held by the page test that every state of the map row that the component can
show is drawn by the module's component.

Needs no gateway, no Gradle, no esbuild and no npm. The browser harness run skips, with its reason, where Node, Chromium,
`module/web/node_modules` or the harness' React 18 vendor files are absent.

Run from the repository root:  python -m unittest discover -s tests
"""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "module"
MOUNTED = MODULE / "gateway/src/main/resources/mounted"
sys.path.insert(0, str(ROOT / "tools"))

sys.path.insert(0, str(ROOT / "tools" / "compare"))
import glass_gates  # noqa: E402  (as tests/test_glass_gates_plan.py: "compare" also names tools/compare/compare.py)
from hmi import gates, library_profile, screen, testbench  # noqa: E402

CTYPE = "cadre.ob.generator"
TAG = "obc-indicator-generator"
MAP_TAG = "obc-automation-button"      # the element the Sandbox's map row names (carried unchanged, ruling R2)
PIN_PKG = MODULE / "web/node_modules/@oicl/openbridge-webcomponents"
# the pin is installed in the main checkout only; a worktree has no node_modules (the tests read it where it is)
PIN_CANDIDATES = [PIN_PKG, Path(r"F:\repos\Cadre-Sandbox-OpenBridge\module\web\node_modules\@oicl\openbridge-webcomponents")]
PINNED = next((p for p in PIN_CANDIDATES if (p / "dist/automation/indicator-generator/indicator-generator.js").exists()), None)

# Table 16.3 and section 16.3: the map row's states, exactly
STATES = [
    {"name": "running", "props": {"on": True}},
    {"name": "stopped", "props": {"on": False}},
    {"name": "fault", "props": {"on": True, "alert": True, "alertFrameStatus": "alarm"}},
    {"name": "out_of_service", "props": {"on": False, "outOfService": True}},
]
# the status properties of the device template (3.2 of the builders' contract) that the indicator generator carries: the
# wrapper draws its status word itself. The other two (the duty mark and the out of service greying) belong to the device
# wraps (pump, motor, fan) and are not carried (the Sandbox's wrap on the automation button carried all four).
TEMPLATE_EXTRAS = {"showStatus": ("boolean", True), "statusText": ("string", "")}
NOT_CARRIED = ("badgeDuty", "outOfService")


def element_tag(path: str) -> str:
    """The element tag the pinned file `dist/<path>` defines (its `customElement(...)` name)."""
    text = (PINNED / "dist" / path).read_text(encoding="utf-8")
    return re.search(r'customElement\("([^"]+)"\)', text).group(1)


def generator_module():
    """`gen_module_assets.py` imported by path: it only defines tables and functions until `main` is called."""
    spec = importlib.util.spec_from_file_location("gen_module_assets_under_test", MODULE / "tools/gen_module_assets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TheComponentsEntry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = generator_module()
        cls.entries = [c for c in cls.gen.COMPONENTS if c["type"] == CTYPE]

    def test_there_is_one_entry_for_the_generator_with_the_elements_tag_and_names(self):
        self.assertEqual(len(self.entries), 1)
        e = self.entries[0]
        self.assertEqual((e["tag"], e["name"], e["title"]), (TAG, "generator", "Generator"))
        self.assertTrue(e["palette"])

    def test_it_is_an_indicator_wrap_with_the_generator_flag_and_the_two_status_names(self):
        # 0.8.0: the wrapper draws the status word itself (`generator`), so the entry is not the device template (`status`)
        e = self.entries[0]
        self.assertIs(e.get("generator"), True)
        self.assertFalse(e.get("status"))
        self.assertTrue(set(TEMPLATE_EXTRAS) <= set(e.get("extra", [])), e.get("extra"))
        self.assertFalse(set(NOT_CARRIED) & set(e.get("extra", [])), e.get("extra"))
        self.assertEqual([c["type"] for c in self.gen.COMPONENTS if c.get("generator")], [CTYPE])

    @unittest.skipIf(PINNED is None, "the pinned package (module/web/node_modules) is not installed here")
    def test_the_entry_tag_is_the_one_the_pinned_indicator_file_defines(self):
        self.assertEqual(self.entries[0]["tag"], element_tag("automation/indicator-generator/indicator-generator.js"))

    def test_the_entry_names_no_icons(self):
        # the Sandbox's wrap carried `icons: {on, off}`; the indicator's scheme is chosen from `on` by the wrapper instead
        self.assertNotIn("icons", self.entries[0])

    def test_no_entry_carries_icons(self):
        for c in self.gen.COMPONENTS:
            self.assertNotIn("icons", c, c["type"])

    def test_the_entry_is_not_a_duplicate_of_a_device_wrap_type(self):
        types = [c["type"] for c in self.gen.COMPONENTS]
        self.assertEqual(len(types), len(set(types)))
        tags = [c["tag"] for c in self.gen.COMPONENTS]
        self.assertEqual(tags.count(TAG), 1)


class TheWrapChecklistSources(unittest.TestCase):
    """Section 8.5's checklist: the sources a wrap changes before the generator runs."""

    def test_the_bundle_imports_the_element_from_the_pin_and_no_generator_icon(self):
        entry = read(MODULE / "web/entry.js")
        self.assertIn("openbridge-webcomponents/dist/automation/indicator-generator/indicator-generator.js", entry)
        # the Sandbox's wrap imported the two pinned generator icons; this wrap draws the indicator itself
        self.assertNotIn("icon-electric-generator", entry)

    def test_the_element_is_measured_for_its_defaults(self):
        self.assertIn(TAG, read(MODULE / "tools/measure_defaults.py"))
        defaults = json.loads(read(MODULE / "web/defaults.json"))
        self.assertIn(TAG, defaults)

    def test_no_openbridge_source_is_copied_into_the_module(self):
        # 8.5: the element comes from the pin, unmodified; the wrapper only sets its properties and adds the package's own
        # alert frame and readout stack in its shadow root
        self.assertFalse(list((MODULE / "web").glob("indicator-generator*")))
        self.assertFalse(list((MODULE / "web").glob("icon-electric-generator*")))


class TheGeneratedContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.components = json.loads(read(MODULE / "components.json"))

    def test_components_json_has_the_generator_entry(self):
        c = self.components[CTYPE]
        self.assertEqual((c["element"], c["title"], c["schema"]), (TAG, "Generator", "schemas/generator.props.json"))
        self.assertTrue(c["palette"])
        self.assertEqual(set(c["defaultSize"]), {"width", "height"})

    def test_the_on_property_and_the_alert_binding_are_in_the_contract(self):
        props = self.components[CTYPE]["props"]
        self.assertEqual((props["on"]["type"], props["on"]["default"]), ("boolean", False))
        self.assertEqual(props["alert"]["type"], "boolean")           # the generator binds alert, alertFrameStatus and
        self.assertIn("alertFrameStatus", props)                      # alertFrameMode (3.1) to the element's own frame
        self.assertIn("alertFrameMode", props)
        self.assertIn("alarm", props["alertFrameStatus"]["enum"])

    def test_the_status_extras_carry_the_other_device_wraps_names_and_defaults_and_no_more(self):
        props = self.components[CTYPE]["props"]
        for name, (typ, default) in TEMPLATE_EXTRAS.items():
            self.assertEqual((props[name]["type"], props[name]["default"]), (typ, default), name)
        for name in NOT_CARRIED:
            self.assertNotIn(name, props, name)

    def test_the_schema_file_exists_is_closed_and_agrees_with_the_contract(self):
        path = MODULE / "common/src/main/resources/schemas/generator.props.json"
        self.assertTrue(path.exists())
        schema = json.loads(read(path))
        self.assertIs(schema["additionalProperties"], False)
        props = {k: v for k, v in schema["properties"].items() if k != "style"}
        contract = self.components[CTYPE]["props"]
        self.assertEqual(set(props), set(contract))
        for name, p in props.items():
            self.assertIn("default", p, name)
            self.assertTrue(p.get("description"), name)
            self.assertEqual(p["type"], contract[name]["type"], name)
            self.assertEqual(p["default"], contract[name]["default"], name)
            self.assertEqual(p.get("enum"), contract[name].get("enum"), name)
        for name, (typ, default) in TEMPLATE_EXTRAS.items():
            self.assertEqual((props[name]["type"], props[name]["default"]), (typ, default), name)
        for name in NOT_CARRIED:
            self.assertNotIn(name, props, name)

    def test_the_generated_files_are_not_edited_by_hand_the_generator_reproduces_the_entry_order(self):
        # the contract lists the generator among the wrapped elements, and the older wraps keep their place
        order = list(self.components)
        self.assertIn(CTYPE, order)
        for older in ("cadre.ob.pump", "cadre.ob.tank", "cadre.ob.canvaszoom"):
            self.assertIn(older, order)


class TheWrapperDrawsTheGenerator(unittest.TestCase):
    """The generated `mounted/js/cadre-ob.js` holds the code that selects the indicator's scheme from `on` (`applyGenerator`)
    and draws the identifier, the status word and the alert frame in its shadow root (`drawGenerator`). The Sandbox's wrap
    placed one of two icon elements in the button's icon slots instead; this repository does not."""

    @classmethod
    def setUpClass(cls):
        cls.js = read(MOUNTED / "js/cadre-ob.js")
        cls.specs = json.loads(re.search(r"var COMPONENTS = (\[.*?\]);\n  var SHEETS", cls.js, re.S).group(1))
        cls.by_type = {s["type"]: s for s in cls.specs}
        cls.wrapper = cls.js.split("var COMPONENTS =")[1]
        cls.apply = cls.wrapper[cls.wrapper.index("applyGenerator(el, p) {"):cls.wrapper.index("drawGenerator(el, p) {")]
        cls.draw = cls.wrapper[cls.wrapper.index("drawGenerator(el, p) {"):]
        cls.draw = cls.draw[:cls.draw.index("\n      }\n") + 8]

    def test_the_generated_specification_flags_the_generator_and_carries_no_icons(self):
        spec = self.by_type[CTYPE]
        self.assertEqual(spec["tag"], TAG)
        self.assertIs(spec["generator"], True)
        self.assertNotIn("icons", spec)

    @unittest.skipIf(PINNED is None, "the pinned package (module/web/node_modules) is not installed here")
    def test_the_specification_tag_is_that_of_the_pinned_indicator_file(self):
        self.assertEqual(self.by_type[CTYPE]["tag"], element_tag("automation/indicator-generator/indicator-generator.js"))

    def test_the_indicator_element_is_a_registered_element_in_the_bundle(self):
        # the bundle imports the element file (entry.js), so the element is defined in the bundle text
        self.assertIn(f'"{TAG}"', self.js.split("var COMPONENTS =")[0])

    def test_no_specification_carries_icons(self):
        for s in self.specs:
            self.assertFalse(s.get("icons"), s["type"])

    def test_the_wrapper_code_chooses_the_scheme_by_on(self):
        # a generator that runs draws `value` (the regular scheme where `value` is off); one that does not run draws `off`
        self.assertRegex(self.apply, r"var value = p\.on \? \(p\.value === 'off' \? 'regular' : p\.value\) : 'off';")
        self.assertIn("if (el.value !== value) el.value = value;", self.apply)
        self.assertNotIn("spec.icons", self.wrapper)
        # the generic field loop leaves `value` to this code
        self.assertIn("if (spec.generator && n === 'value') continue;", self.wrapper)
        self.assertIn("if (spec.generator) this.applyGenerator(el, p);", self.wrapper)

    def test_the_status_and_the_alert_frame_are_drawn_in_the_shadow_root_of_the_indicator(self):
        # the Sandbox placed an icon in each icon slot of the button; here the package's own frame and readout stack are
        # appended to the indicator's shadow root, marked `data-cadre`
        self.assertIn("var root = el.shadowRoot;", self.draw)
        self.assertIn("document.createElement('obc-alert-frame')", self.draw)
        self.assertIn("document.createElement('obc-automation-button-readout-stack')", self.draw)
        self.assertEqual(self.draw.count("root.appendChild("), 2)
        self.assertEqual(self.draw.count("setAttribute('data-cadre', '')"), 2)
        self.assertIn("frame.status = p.alertFrameStatus;", self.draw)
        self.assertIn("frame.mode = p.alertFrameMode;", self.draw)

    def test_the_drawing_is_replaced_when_the_state_changes_not_stacked(self):
        # the frame and the stack are looked up by their mark before one is created, and removed when no longer wanted, so
        # a change of `alert`, `readoutPosition` or `showStatus` updates or removes the one element and never adds another
        self.assertIn("root.querySelector('obc-alert-frame[data-cadre]')", self.draw)
        self.assertIn("root.querySelector('obc-automation-button-readout-stack[data-cadre]')", self.draw)
        self.assertIn("if (!frame) {", self.draw)
        self.assertIn("else if (frame) frame.remove();", self.draw)
        self.assertIn("if (!stack) {", self.draw)
        self.assertIn("stack.remove(); return; }", self.draw)

    def test_the_generators_status_word_is_the_wrappers_own_and_the_device_template_does_not_apply(self):
        spec = self.by_type[CTYPE]
        self.assertFalse(spec["status"])
        extras = {e["name"]: e["def"] for e in spec["extras"]}
        for name, (_typ, default) in TEMPLATE_EXTRAS.items():
            self.assertEqual(extras[name], default, name)
        for name in NOT_CARRIED:
            self.assertNotIn(name, extras, name)
        self.assertIn("(p.on ? 'On' : 'Off')", self.draw)
        self.assertIn("type: p.on ? 'state-on' : 'state-off'", self.draw)

    def test_the_other_wrappers_are_unchanged_by_the_wrap(self):
        for ctype in ("cadre.ob.pump", "cadre.ob.motor", "cadre.ob.fan"):
            self.assertTrue(self.by_type[ctype]["status"], ctype)
            self.assertFalse(self.by_type[ctype].get("icons"), ctype)
        for needle in ("applyStatus", "dutySlot", "cadre-ob-oos"):
            self.assertIn(needle, self.js, needle)


class TheDescriptorAndTheRelease(unittest.TestCase):
    def test_cadreob_java_registers_the_component_with_its_schema_and_palette_title(self):
        java = read(MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.generator", "generator", "Generator"')
        self.assertEqual(java.count('"cadre.ob.generator"'), 1)
        self.assertRegex(java, r'descriptor\("cadre\.ob\.pump", "pump", "Pump"')       # the older ones stay

    def test_the_module_version_is_0_8_0_and_plain(self):
        text = read(MODULE / "build.gradle.kts")
        self.assertIn('version = "0.8.0"', text)
        self.assertNotIn('version = "0.4.4"', text)      # the Sandbox's version of the wrap on the button
        self.assertNotRegex(text, r'version = "[^"]*-')


class TheLibraryTables(unittest.TestCase):
    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def test_module_kind_maps_the_generator_to_the_component(self):
        self.assertEqual(screen.MODULE_KIND["generator"], CTYPE)
        self.assertEqual(screen.MODULE_KIND["pump"], "cadre.ob.pump")       # the others are untouched
        self.assertEqual(len(screen.MODULE_KIND), 12)       # 0.8.0: the nine device kinds and the three of module 0.3.1 and 0.4.x

    def test_the_other_module_tables_have_a_row_for_the_generator(self):
        for table in (screen.MODULE_PARAM, screen.MODULE_DROP, screen.MODULE_NEEDS, screen.MODULE_EXCEPT):
            self.assertIn("generator", table)
        # the indicator lists the status words but not the two marks of the device template: `showStatus` and `statusText`
        # are dropped only while the component lacks them, and the marks are always dropped (they keep a symbol on the view)
        self.assertEqual(set(screen.MODULE_IF_LISTED["generator"]), {"showStatus", "statusText"})
        self.assertFalse({"badgeDuty", "outOfService"} & set(screen.MODULE_IF_LISTED["generator"]))
        for name in ("deviceId", "deviceKind", "deviceLabel", "hasTag", "badgeDuty", "outOfService"):
            self.assertIn(name, screen.MODULE_DROP["generator"], name)
        self.assertEqual(screen.module_drop("generator"), set(screen.MODULE_DROP["generator"]) - {"showStatus", "statusText"})
        self.assertEqual(screen.MODULE_EXCEPT["generator"], [{"picture": "genset"}])
        self.assertEqual(screen.MODULE_NEEDS["generator"]["variant"], ["regular"])

    def test_the_glass_gates_select_the_generator_by_the_elements_tag(self):
        self.assertEqual(glass_gates.MODULE_TAGS["generator"], TAG)
        self.assertEqual(glass_gates.MODULE_TAGS["pump"], "obc-pump")

    def test_the_module_component_has_the_properties_the_generator_gives_it(self):
        listed = screen.module_props(CTYPE)
        for name in ("on", "alert", "alertFrameStatus", "alertFrameMode", "showStatus", "statusText", "tag",
                     "readoutPosition"):
            self.assertIn(name, listed, name)
        for name in NOT_CARRIED:      # the Sandbox's component listed these two; the indicator does not
            self.assertNotIn(name, listed, name)


# ---- a generator symbol built from a descriptor --------------------------------------------------
def intake_with_generators() -> dict:
    d = json.loads(read(ROOT / "screens/wtp/intake.json"))
    d["symbols"], d["pipes"], d["junctions"], d["labels"] = [], [], [], []
    d["symbols"] += [
        {"id": "G1", "kind": "generator", "x": 300, "y": 300, "w": 48, "h": 48,
         "params": {"on": True, "hasTag": True, "tag": "G-1"}},
        {"id": "G2", "kind": "generator", "x": 400, "y": 300, "w": 48, "h": 48, "render": "view", "params": {"on": True}},
        {"id": "G3", "kind": "generator", "x": 500, "y": 300, "w": 48, "h": 48,
         "params": {"on": False, "outOfService": True, "alert": True, "alertFrameStatus": "alarm"}},
        {"id": "G5", "kind": "generator", "x": 700, "y": 300, "w": 48, "h": 48,
         "params": {"on": True, "alert": True, "alertFrameStatus": "alarm", "hasTag": True, "tag": "G-5"}},
        {"id": "G4", "kind": "generator", "x": 600, "y": 300, "w": 240, "h": 150,
         "params": {"picture": "genset", "on": True, "hasTag": True, "tag": "GEN-1"}},
    ]
    return d


class AGeneratorSymbolBuilt(unittest.TestCase):
    VIEW = "com.inductiveautomation.perspective/views/Screens/Intake/view.json"

    @classmethod
    def build(cls, render: str):
        child, reports = screen.build_child("cadre_hmi_t", [intake_with_generators()], "T", render=render)
        out = {}

        def walk(n):
            out[n.get("meta", {}).get("name")] = n
            for c in n.get("children") or []:
                walk(c)
        walk(json.loads(child.files[cls.VIEW])["root"])
        return out, reports, child

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def test_the_module_rendering_emits_the_component(self):
        nodes, reports, _ = self.build("module")
        g = nodes["G1"]
        self.assertEqual(g["type"], CTYPE)
        self.assertEqual(g["props"]["on"], True)
        # a module kind on a page with a toolbar binds its tag through custom.idText (as the pump does)
        if "tag" in g["props"]:
            self.assertEqual(g["props"]["tag"], "G-1")
        else:
            self.assertIn("props.tag", g.get("propConfig", {}))
        # G1 names no device, so like any module kind it carries no custom device kind (screen.embed_module)
        self.assertNotIn("deviceKind", g.get("custom", {}))
        self.assertEqual(reports["/intake"]["errors"], [])

    def test_the_component_gets_only_properties_it_lists_and_no_library_only_parameters(self):
        nodes, _, _ = self.build("module")
        listed = screen.module_props(CTYPE)
        for sid in ("G1", "G5"):
            props = nodes[sid]["props"]
            self.assertTrue(set(props) - {"style"} <= listed, (sid, set(props) - listed))
            for dropped in ("deviceId", "deviceKind", "deviceLabel", "hasTag"):
                self.assertNotIn(dropped, props, dropped)

    def test_the_alert_state_reaches_the_component_since_it_lists_it(self):
        nodes, _, _ = self.build("module")
        p = nodes["G5"]["props"]
        self.assertEqual((p["on"], p["alert"], p["alertFrameStatus"]), (True, True, "alarm"))

    def test_an_out_of_service_generator_stays_on_the_librarys_view_the_component_lacks_the_mark(self):
        # the Sandbox's component listed `outOfService` and drew it; the indicator has no such mark (R1), so the symbol keeps
        # the library's view, which greys it
        nodes, _, _ = self.build("module")
        g = nodes["G3"]
        self.assertEqual(g["type"], "ia.display.view")
        self.assertEqual(g["props"]["path"], "Automation/Generator")
        self.assertFalse(screen.module_drawn({"kind": "generator", "params": {"on": False, "outOfService": True}}))
        self.assertNotIn("outOfService", screen.module_props(CTYPE))

    def test_the_stock_rendering_keeps_the_library_view(self):
        nodes, _, _ = self.build("stock")
        self.assertEqual(nodes["G1"]["type"], "ia.display.view")
        self.assertEqual(nodes["G1"]["props"]["path"], "Automation/Generator")

    def test_the_library_view_stays_available_with_render_view(self):
        nodes, _, _ = self.build("module")
        g = nodes["G2"]
        self.assertEqual(g["type"], "ia.display.view")
        self.assertEqual(g["props"]["path"], "Automation/Generator")
        self.assertFalse(screen.module_drawn({"kind": "generator", "render": "view", "params": {"on": True}}))
        self.assertTrue(screen.module_drawn({"kind": "generator", "params": {"on": True}}))

    def test_the_generator_set_stays_on_the_librarys_view_the_wrap_does_not_fit_it(self):
        # 3.1: obc-gauge-generator is rejected; the set's own picture is the library's view under the module rendering
        nodes, _, _ = self.build("module")
        self.assertEqual(nodes["G4"]["type"], "ia.display.view")
        self.assertEqual(nodes["G4"]["props"]["path"], screen.GENSET_VIEW)
        self.assertFalse(screen.module_drawn({"kind": "generator", "params": {"picture": "genset"}}))

    def test_the_registry_gate_accepts_the_built_generator_and_refuses_an_unknown_property(self):
        with tempfile.TemporaryDirectory() as d:
            _, _, child = self.build("module")
            out = child.write(Path(d))
            self.assertTrue(gates.g1_registry(out)["ok"])
            vf = out / self.VIEW
            doc = json.loads(read(vf))

            def poison(n):
                if n.get("type") == CTYPE:
                    n["props"]["colour"] = "red"
                for c in n.get("children") or []:
                    poison(c)
            poison(doc["root"])
            vf.write_text(json.dumps(doc), encoding="utf-8")
            self.assertFalse(gates.g1_registry(out)["ok"])

    def test_other_kinds_are_drawn_as_before(self):
        d = intake_with_generators()
        d["symbols"].append({"id": "P1", "kind": "pump", "x": 100, "y": 100, "w": 48, "h": 48,
                             "params": {"on": True, "hasTag": True, "tag": "P-1"}})
        child, _ = screen.build_child("cadre_hmi_t", [d], "T", render="module")
        view = json.loads(child.files[self.VIEW])
        found = []

        def walk(n):
            if n.get("meta", {}).get("name") == "P1":
                found.append(n["type"])
            for c in n.get("children") or []:
                walk(c)
        walk(view["root"])
        self.assertEqual(found, ["cadre.ob.pump"])


class TheMapRow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.map = json.loads(read(MODULE / "openbridge-map.json"))
        cls.rows = [r for r in cls.map["rows"] if r["kind"] == "generator"]

    def test_there_is_one_generator_row_and_it_is_reviewed(self):
        self.assertEqual(len(self.rows), 1)
        self.assertEqual(self.rows[0]["state"], "reviewed")
        # the map is carried unchanged (ruling R2): it names the automation button, not the indicator this module wraps
        self.assertEqual((self.rows[0]["element"], self.rows[0]["import"].rsplit("/", 1)[-1]),
                         (MAP_TAG, "automation-button.js"))

    def test_the_states_are_the_four_of_section_16_3_exactly(self):
        self.assertEqual(self.rows[0]["states"], STATES)

    def test_the_reference_records_the_decision_of_rw_01(self):
        # 16.3: for WP-W06 the `reference` is the decision that records RW-01 (the survey hash is for stage B's wraps)
        ref = self.rows[0]["reference"]
        self.assertIsInstance(ref, str)
        self.assertTrue(ref.strip())
        self.assertNotRegex(ref, r"^[0-9a-f]{40,64}$")      # not a survey hash

    def test_the_other_rows_and_the_rejected_list_are_unchanged(self):
        by_kind = {r["kind"]: r for r in self.map["rows"]}
        self.assertEqual(set(by_kind), {"switch", "bus", "generator", "command-button"})
        for kind in ("switch", "bus", "command-button"):
            self.assertEqual(by_kind[kind]["state"], "proposed", kind)
            self.assertEqual(by_kind[kind]["states"], [], kind)
        self.assertEqual({r["kind"] for r in self.map["rejected"]}, {"range-bar", "generator-set", "generator"})

    def test_every_state_prop_is_a_property_of_the_component_but_the_named_differences(self):
        # The map row was written for the Sandbox's component on the automation button, which lists `outOfService`; the
        # indicator wrap of this repository does not (ruling R1). The exact difference is named, so that any further drift
        # between the map and the component fails here.
        listed = set(json.loads(read(MODULE / "components.json"))[CTYPE]["props"])
        missing = {state["name"]: sorted(set(state["props"]) - listed) for state in self.rows[0]["states"]
                   if set(state["props"]) - listed}
        self.assertEqual(missing, {"out_of_service": ["outOfService"]})

    def test_the_map_row_and_this_components_element_differ_exactly_by_the_named_element(self):
        # the map's `rejected` list also names the indicator for the Sandbox's reasons; both stay as carried (ruling R2)
        components = json.loads(read(MODULE / "components.json"))
        self.assertEqual((self.rows[0]["element"], components[CTYPE]["element"]), (MAP_TAG, TAG))
        rejected = {(r["kind"], r["element"]) for r in self.map["rejected"]}
        self.assertIn(("generator", TAG), rejected)


class TheTestPage(unittest.TestCase):
    """T10: the test page row drives every state of the map row, drawn by the module's component."""

    @classmethod
    def setUpClass(cls):
        cls.contracts = screen.load_contracts()
        cls.prof = library_profile.build(cls.contracts)
        cls.bench = testbench.build(cls.contracts, cls.prof, "[default]cadre_hmi_asmtest")
        cls.desc = cls.bench.descriptor
        cls.states = json.loads(read(MODULE / "openbridge-map.json"))
        cls.row = next(r for r in cls.states["rows"] if r["kind"] == "generator")

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def cells(self):
        return [s for s in self.desc["symbols"] if s["kind"] == "generator" and s.get("params", {}).get("picture") != "genset"
                and s["id"].startswith("S_generator_")]

    def stated(self, s):
        return {**s.get("params", {}), **self.bench.gallery.get(s["id"], {})}

    def test_the_page_draws_generator_cells_the_module_can_draw(self):
        cells = self.cells()
        self.assertTrue(cells)
        drawn = [s for s in cells if screen.module_drawn(s)]
        self.assertTrue(drawn, "no generator cell of the page is drawn by the module's component")

    def test_the_page_stays_consistent_with_the_catalogue(self):
        self.assertEqual(testbench.check(self.desc, self.contracts), [])

    def test_every_state_of_the_map_row_has_a_cell_and_all_but_out_of_service_a_module_cell(self):
        # The out of service state is not drawn by the indicator component (it lists no such mark, ruling R1): its cell
        # stays on the library's view, which greys the symbol. Every other state is drawn by the module's component.
        drawn = [s for s in self.cells() if screen.module_drawn(s)]
        kept = [s for s in self.cells() if not screen.module_drawn(s)]
        for state in STATES:
            want = state["props"]
            hit = [s["id"] for s in drawn if all(self.stated(s).get(k) == v for k, v in want.items())]
            on_view = [s["id"] for s in kept if all(self.stated(s).get(k) == v for k, v in want.items())]
            if state["name"] == "out_of_service":
                self.assertFalse(hit, f"a module cell drives the state {state['name']!r}: the named difference has closed")
                self.assertTrue(on_view, f"no library cell drives the state {state['name']!r} {want}")
            else:
                self.assertTrue(hit, f"no module cell drives the state {state['name']!r} {want}")

    def test_the_built_page_draws_the_generator_cells_as_the_component(self):
        d = json.loads(json.dumps(self.desc))
        keep = [s for s in d["symbols"] if s["kind"] == "generator" and s["id"].startswith("S_generator_")
                and s.get("params", {}).get("picture") != "genset"]
        self.assertTrue(keep)
        child, _ = screen.build_child("cadre_hmi_bench", [{**d, "symbols": keep, "pipes": [], "labels": [],
                                                          "buttons": [], "alarmPanels": []}], "T", render="module")
        types = []

        def walk(n):
            if (n.get("meta", {}).get("name") or "").startswith("S_generator_"):
                types.append(n["type"])
            for c in n.get("children") or []:
                walk(c)
        for path, text in child.files.items():
            if path.endswith("view.json") and "/Screens/" in path:
                walk(json.loads(text)["root"])
        self.assertIn(CTYPE, types)

    def test_the_generator_set_section_still_draws_the_librarys_set(self):
        sets = [s for s in self.desc["symbols"] if screen.view_of(s) == screen.GENSET_VIEW]
        self.assertTrue(sets)
        for s in sets:
            self.assertFalse(screen.module_drawn(s), s["id"])


class TheOfflineHarness(unittest.TestCase):
    HARNESS = MODULE / "tools/harness/devices.mjs"

    def test_the_harness_names_the_device_components_it_checks(self):
        # The Sandbox's harness checked the generator's two icons and four states in `devices.mjs`; the harness of this
        # repository checks the pump, motor and fan wrappers and the readout, and has no generator case (a gap, reported:
        # the wrapper's drawing of the generator is held by the offline text tests above and by the gateway gates).
        mjs = read(self.HARNESS)
        for ctype in ("cadre.ob.pump", "cadre.ob.motor", "cadre.ob.fan", "cadre.ob.readout"):
            self.assertIn(ctype, mjs, ctype)
        self.assertIn("devices.mjs", read(MODULE / "tools/harness/README.md"))

    def _skip_reason(self):
        if shutil.which("node") is None:
            return "Node is not installed"
        if not (MODULE / "web/node_modules").exists():
            return "module/web/node_modules is absent (the harness imports Playwright and the pinned package from it)"
        if not (MODULE / "web/dist/ob-components.js").exists():
            return "the module bundle module/web/dist/ob-components.js is not built here"
        if not (MODULE / "tools/harness/vendor/react.js").exists():
            return "the harness' React 18 vendor files are not copied (module/tools/harness/README.md)"
        return None

    def test_the_harness_run_passes_every_device_check_in_chromium(self):
        reason = self._skip_reason()
        if reason:
            self.skipTest(reason)
        run = subprocess.run(["node", str(self.HARNESS)], capture_output=True, text=True, timeout=300, cwd=str(MODULE))
        out = run.stdout
        if "browserType.launch" in run.stderr or "Executable doesn't exist" in run.stderr:
            self.skipTest("Chromium is absent (set CHROMIUM or install Playwright's browser)")
        self.assertEqual(run.returncode, 0, run.stderr[-2000:])
        self.assertNotIn("FAIL", out)
        for ctype in ("cadre.ob.pump", "cadre.ob.motor", "cadre.ob.fan"):
            lines = [ln for ln in out.splitlines() if ctype in ln]
            self.assertTrue(any(ln.startswith("PASS") for ln in lines), f"the harness printed no passing {ctype} check")


if __name__ == "__main__":
    unittest.main()
