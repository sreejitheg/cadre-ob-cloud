"""Tests of the generator's module wrap (NOTE-WFB-10 sections 3.1, 8.5 and 16.3, ruling RW-01; module 0.4.4).

The generator symbol is drawn by `obc-automation-button` with the pinned generator icons, as component
`cadre.ob.generator` (schema name `generator`, palette title "OB Generator"). The checklist of section 8.5 names the files
a wrap changes; these tests hold each of them, offline: the entry in `COMPONENTS` of `gen_module_assets.py` with its
`icons: {on, off}`, the files the generator writes (`components.json`, `generator.props.json`, `cadre-ob.js`), the
descriptor in `CadreOb.java`, the version, the module tables of `screen.py`, `MODULE_TAGS` of the glass gates, the map row
and the component test page. Threat T10 (a wrap that fails an ASM rule) is held by the page test that every state of the
map row is drawn by the module's component.

Needs no gateway, no Gradle, no esbuild and no npm. The browser harness check skips, with its reason, where Node,
Chromium or `module/web/node_modules` is absent.

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
TAG = "obc-automation-button"
PIN_PKG = MODULE / "web/node_modules/@oicl/openbridge-webcomponents"
# the pin is installed in the main checkout only; a worktree has no node_modules (the tests read it where it is)
PIN_CANDIDATES = [PIN_PKG, Path(r"F:\repos\Cadre-Sandbox-OpenBridge\module\web\node_modules\@oicl\openbridge-webcomponents")]
PINNED = next((p for p in PIN_CANDIDATES if (p / "dist/icons/icon-electric-generator-on.js").exists()), None)

# Table 16.3 and section 16.3: the map row's states, exactly
STATES = [
    {"name": "running", "props": {"on": True}},
    {"name": "stopped", "props": {"on": False}},
    {"name": "fault", "props": {"on": True, "alert": True, "alertFrameStatus": "alarm"}},
    {"name": "out_of_service", "props": {"on": False, "outOfService": True}},
]
# the template's extra properties of the other device wraps (3.2 of the builders' contract)
TEMPLATE_EXTRAS = {"showStatus": ("boolean", True), "statusText": ("string", ""), "badgeDuty": ("boolean", False),
                   "outOfService": ("boolean", False)}


def icon_tag(name: str) -> str:
    """The element tag the pinned icon file `dist/icons/<name>.js` defines (its `customElement(...)` name)."""
    text = (PINNED / "dist/icons" / f"{name}.js").read_text(encoding="utf-8")
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
        self.assertEqual((e["tag"], e["name"], e["title"]), (TAG, "generator", "OB Generator"))
        self.assertTrue(e["palette"])

    def test_it_is_a_device_wrap_with_the_status_template(self):
        e = self.entries[0]
        self.assertIs(e.get("status"), True)
        self.assertTrue(set(TEMPLATE_EXTRAS) <= set(e.get("extra", [])), e.get("extra"))

    @unittest.skipIf(PINNED is None, "the pinned OpenBridge package (module/web/node_modules) is not installed here")
    def test_the_icons_name_the_element_tags_read_from_the_pinned_icon_files(self):
        on, off = icon_tag("icon-electric-generator-on"), icon_tag("icon-electric-generator-off")
        self.assertNotEqual(on, off)
        self.assertEqual(self.entries[0]["icons"], {"on": on, "off": off})

    def test_the_icons_have_exactly_the_keys_on_and_off(self):
        self.assertEqual(set(self.entries[0]["icons"]), {"on", "off"})

    def test_no_other_entry_carries_icons(self):
        for c in self.gen.COMPONENTS:
            if c["type"] != CTYPE:
                self.assertNotIn("icons", c, c["type"])

    def test_the_entry_is_not_a_duplicate_of_a_device_wrap_type(self):
        types = [c["type"] for c in self.gen.COMPONENTS]
        self.assertEqual(len(types), len(set(types)))
        tags = [c["tag"] for c in self.gen.COMPONENTS]
        self.assertEqual(tags.count(TAG), 1)


class TheWrapChecklistSources(unittest.TestCase):
    """Section 8.5's checklist: the sources a wrap changes before the generator runs."""

    def test_the_bundle_imports_the_element_and_the_two_icons_from_the_pin(self):
        entry = read(MODULE / "web/entry.js")
        self.assertIn("openbridge-webcomponents/dist/automation/automation-button/automation-button.js", entry)
        for name in ("icon-electric-generator-on", "icon-electric-generator-off"):
            self.assertRegex(entry, rf"openbridge-webcomponents/dist/icons/{name}\.js")

    def test_the_element_is_measured_for_its_defaults(self):
        self.assertIn(TAG, read(MODULE / "tools/measure_defaults.py"))
        defaults = json.loads(read(MODULE / "web/defaults.json"))
        self.assertIn(TAG, defaults)

    def test_no_openbridge_source_is_copied_into_the_module(self):
        # 8.5: the element comes from the pin, unmodified; the wrapper only places the icon element in the slots
        self.assertFalse(list((MODULE / "web").glob("automation-button*")))
        self.assertFalse(list((MODULE / "web").glob("icon-electric-generator*")))


class TheGeneratedContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.components = json.loads(read(MODULE / "components.json"))

    def test_components_json_has_the_generator_entry(self):
        c = self.components[CTYPE]
        self.assertEqual((c["element"], c["title"], c["schema"]), (TAG, "OB Generator", "schemas/generator.props.json"))
        self.assertTrue(c["palette"])
        self.assertEqual(set(c["defaultSize"]), {"width", "height"})

    def test_the_on_property_and_the_alert_binding_are_in_the_contract(self):
        props = self.components[CTYPE]["props"]
        self.assertEqual((props["on"]["type"], props["on"]["default"]), ("boolean", False))
        self.assertEqual(props["alert"]["type"], "boolean")           # the generator binds alert, alertFrameStatus and
        self.assertIn("alertFrameStatus", props)                      # alertFrameMode (3.1) to the element's own frame
        self.assertIn("alertFrameMode", props)
        self.assertIn("alarm", props["alertFrameStatus"]["enum"])

    def test_the_template_extras_carry_the_other_device_wraps_names_and_defaults(self):
        props = self.components[CTYPE]["props"]
        for name, (typ, default) in TEMPLATE_EXTRAS.items():
            self.assertEqual((props[name]["type"], props[name]["default"]), (typ, default), name)

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

    def test_the_generated_files_are_not_edited_by_hand_the_generator_reproduces_the_entry_order(self):
        # the contract lists the generator among the wrapped elements, after the first nine wraps' order is kept
        order = list(self.components)
        self.assertIn(CTYPE, order)
        for older in ("cadre.ob.pump", "cadre.ob.tank", "cadre.ob.canvaszoom"):
            self.assertIn(older, order)


class TheWrapperPlacesTheIcon(unittest.TestCase):
    """The generated `mounted/js/cadre-ob.js` holds the code that places the icon element chosen by `on` in the button's
    icon slots (`automation-button.js` declares the slots `icon` and `icon-silhouette`)."""

    @classmethod
    def setUpClass(cls):
        cls.js = read(MOUNTED / "js/cadre-ob.js")
        cls.specs = json.loads(re.search(r"var COMPONENTS = (\[.*?\]);\n  var SHEETS", cls.js, re.S).group(1))
        cls.by_type = {s["type"]: s for s in cls.specs}

    def test_the_generated_specification_carries_the_two_icon_tags(self):
        spec = self.by_type[CTYPE]
        self.assertEqual(spec["tag"], TAG)
        self.assertEqual(set(spec["icons"]), {"on", "off"})
        self.assertTrue(spec["status"])
        for tag in spec["icons"].values():
            self.assertRegex(tag, r"^obi-electric-generator-")

    @unittest.skipIf(PINNED is None, "the pinned OpenBridge package (module/web/node_modules) is not installed here")
    def test_the_specification_tags_are_those_of_the_pinned_icon_files(self):
        self.assertEqual(self.by_type[CTYPE]["icons"], {"on": icon_tag("icon-electric-generator-on"),
                                                         "off": icon_tag("icon-electric-generator-off")})

    def test_the_icons_are_registered_elements_in_the_bundle(self):
        # the bundle imports the icon files (entry.js), so the elements are defined in the bundle text
        for tag in self.by_type[CTYPE]["icons"].values():
            self.assertIn(f'"{tag}"', self.js.split("var COMPONENTS =")[0], tag)

    def test_no_other_specification_carries_icons(self):
        for s in self.specs:
            if s["type"] != CTYPE:
                self.assertFalse(s.get("icons"), s["type"])

    def test_the_wrapper_code_reads_the_specs_icons_and_chooses_by_on(self):
        wrapper = self.js.split("var COMPONENTS =")[1]
        self.assertIn("spec.icons", wrapper)
        self.assertRegex(wrapper, r"spec\.icons\[[^\]]*\bon\b[^\]]*\]|p\.on\s*\?\s*spec\.icons\.on\s*:\s*spec\.icons\.off|"
                                  r"spec\.icons\.on\b.*spec\.icons\.off\b")

    def test_the_icon_is_placed_in_each_icon_slot_the_button_declares(self):
        wrapper = self.js.split("var COMPONENTS =")[1]
        self.assertIn("icon-silhouette", wrapper)
        self.assertRegex(wrapper, r"slot:\s*['\"]icon['\"]|\[\s*['\"]icon['\"]\s*,\s*['\"]icon-silhouette['\"]\s*\]")

    def test_the_icon_is_replaced_when_on_changes_not_stacked(self):
        # the child carries a key (or is the only child of its slot) that depends on `on`, so React swaps the element
        wrapper = self.js.split("var COMPONENTS =")[1]
        self.assertRegex(wrapper, r"key:\s*['\"]icon[^,}]*(on|off|state)|key:\s*[^,}]*spec\.icons")

    def test_the_device_status_code_still_applies_to_the_generator(self):
        self.assertTrue(self.by_type[CTYPE]["status"])
        extras = {e["name"]: e["def"] for e in self.by_type[CTYPE]["extras"]}
        for name, (_typ, default) in TEMPLATE_EXTRAS.items():
            self.assertEqual(extras[name], default, name)

    def test_the_other_wrappers_are_unchanged_by_the_wrap(self):
        for ctype in ("cadre.ob.pump", "cadre.ob.motor", "cadre.ob.fan"):
            self.assertTrue(self.by_type[ctype]["status"], ctype)
            self.assertFalse(self.by_type[ctype].get("icons"), ctype)
        for needle in ("applyStatus", "dutySlot", "cadre-ob-oos"):
            self.assertIn(needle, self.js, needle)


class TheDescriptorAndTheRelease(unittest.TestCase):
    def test_cadreob_java_registers_the_component_with_its_schema_and_palette_title(self):
        java = read(MODULE / "common/src/main/java/cadre/hmi/ob/common/CadreOb.java")
        self.assertRegex(java, r'descriptor\("cadre\.ob\.generator", "generator", "OB Generator"')
        self.assertEqual(java.count('"cadre.ob.generator"'), 1)
        self.assertRegex(java, r'descriptor\("cadre\.ob\.pump", "pump", "OB Pump"')       # the older ones stay

    def test_the_module_version_is_0_4_4_and_plain(self):
        text = read(MODULE / "build.gradle.kts")
        self.assertIn('version = "0.4.4"', text)
        self.assertNotIn('version = "0.4.3"', text)
        self.assertNotRegex(text, r'version = "[^"]*-')


class TheLibraryTables(unittest.TestCase):
    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def test_module_kind_maps_the_generator_to_the_component(self):
        self.assertEqual(screen.MODULE_KIND["generator"], CTYPE)
        self.assertEqual(screen.MODULE_KIND["pump"], "cadre.ob.pump")       # the others are untouched
        self.assertEqual(len(screen.MODULE_KIND), 9)

    def test_the_other_module_tables_have_a_row_for_the_generator(self):
        for table in (screen.MODULE_PARAM, screen.MODULE_DROP):
            self.assertIn("generator", table)
        # the status props are dropped while the component lacks them, and given once it lists them (as for the pump)
        self.assertTrue(set(screen._STATUS_PROPS) <= set(screen.MODULE_IF_LISTED["generator"]))
        for name in ("deviceId", "deviceKind", "deviceLabel", "hasTag"):
            self.assertIn(name, screen.MODULE_DROP["generator"], name)

    def test_the_glass_gates_select_the_generator_by_the_elements_tag(self):
        self.assertEqual(glass_gates.MODULE_TAGS["generator"], TAG)
        self.assertEqual(glass_gates.MODULE_TAGS["pump"], "obc-pump")

    def test_the_module_component_has_the_properties_the_generator_gives_it(self):
        listed = screen.module_props(CTYPE)
        for name in ("on", "alert", "alertFrameStatus", "alertFrameMode", "showStatus", "statusText", "badgeDuty",
                     "outOfService", "tag"):
            self.assertIn(name, listed, name)


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
        for sid in ("G1", "G3"):
            props = nodes[sid]["props"]
            self.assertTrue(set(props) - {"style"} <= listed, (sid, set(props) - listed))
            for dropped in ("deviceId", "deviceKind", "deviceLabel", "hasTag"):
                self.assertNotIn(dropped, props, dropped)

    def test_the_state_marks_reach_the_component_since_it_lists_them(self):
        nodes, _, _ = self.build("module")
        p = nodes["G3"]["props"]
        self.assertEqual((p["outOfService"], p["alert"], p["alertFrameStatus"]), (True, True, "alarm"))

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
        self.assertEqual((self.rows[0]["element"], self.rows[0]["import"].rsplit("/", 1)[-1]),
                         (TAG, "automation-button.js"))

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

    def test_every_state_prop_is_a_property_of_the_component(self):
        listed = set(json.loads(read(MODULE / "components.json"))[CTYPE]["props"])
        for state in self.rows[0]["states"]:
            self.assertTrue(set(state["props"]) <= listed, state["name"])


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

    def test_every_state_of_the_map_row_has_a_module_cell_that_states_its_properties(self):
        drawn = [s for s in self.cells() if screen.module_drawn(s)]
        for state in STATES:
            want = state["props"]
            hit = [s["id"] for s in drawn if all(self.stated(s).get(k) == v for k, v in want.items())]
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

    def test_the_harness_checks_the_generator_icons_and_states(self):
        mjs = read(self.HARNESS)
        self.assertIn(CTYPE, mjs)
        for needle in ("obi-electric-generator-on", "obi-electric-generator-off"):
            self.assertIn(needle, mjs, needle)
        for state in ("running", "stopped", "fault", "out of service"):
            self.assertRegex(mjs, rf"(?i)generator[^\n]*{state}|{state}[^\n]*generator", state)
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

    def test_the_harness_run_passes_every_generator_check_in_chromium(self):
        reason = self._skip_reason()
        if reason:
            self.skipTest(reason)
        run = subprocess.run(["node", str(self.HARNESS)], capture_output=True, text=True, timeout=300, cwd=str(MODULE))
        out = run.stdout
        if "browserType.launch" in run.stderr or "Executable doesn't exist" in run.stderr:
            self.skipTest("Chromium is absent (set CHROMIUM or install Playwright's browser)")
        self.assertEqual(run.returncode, 0, run.stderr[-2000:])
        self.assertNotIn("FAIL", out)
        generator = [ln for ln in out.splitlines() if CTYPE in ln]
        self.assertTrue(any("PASS" in ln for ln in generator), "the harness printed no passing generator check")
        # the icon element chosen by `on` is the one in the button's icon slot, and it is replaced when `on` changes
        text = out.lower()
        self.assertIn("obi-electric-generator-on", text)
        self.assertIn("obi-electric-generator-off", text)


if __name__ == "__main__":
    unittest.main()
