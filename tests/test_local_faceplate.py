"""Tests of the local faceplate and the assembly's click (NOTE-WFB-10 section 3.3 and section 11.2 item 5; acceptance
corpus 3, offline part: G7 faceplates for `Faceplate/ASM/Local`). Work package WP-W04, written from the note before the
feature exists.

The library builds one faceplate for every local device, `Faceplate/ASM/Local`, in the ASM style with the tabs Home,
Alarms and Info. Its view parameter `localKind` names the kind; Home embeds the view `Local/<Kind>/Home` through the
expression `'Local/' + {view.params.localKind} + '/Home'`, with the view's `deviceId`. `local` enters the closed tables
`FACEPLATE_VIEW`, `ASM_VIEW`, `FACEPLATE_OF_KIND` and `gates.FACEPLATES`. The openers `library.open_device` and
`cadre.hmi.select_device` gain the keyword-only last argument `local`, which writes `session.custom.selectedLocal`; the
dock and the popup pass `localKind` from it and the float from its own parameter. An assembly embedded on a page carries a
click that opens the faceplate for the kind `local` and its `<Kind>`.

Run from the repository root:  python -m unittest discover -s tests
Nothing here needs the gateway or a browser; every test is offline.
"""
import copy
import hashlib
import inspect
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import local_support as L  # noqa: E402
from local_support import KIND, KIND_VIEW, TAG_ROOT, assembly, devices, nodes, page  # noqa: E402
from test_hmi import hmi_ns, session  # noqa: E402  (helpers only: no test class is imported)

from hmi import framework, gates, library, library_profile, navigation, screen, testbench  # noqa: E402
from hmi import parent as par  # noqa: E402

LOCAL_FACEPLATE = "Faceplate/ASM/Local"
HOME_PATH = "'Local/' + {view.params.localKind} + '/Home'"
VIEWS = "com.inductiveautomation.perspective/views/"

# The faceplate views before this package, hashed as canonical JSON (the guard of "the existing kinds' faceplates are
# unchanged"): the parent of WP-W03's branch.
EXISTING_FACEPLATE_HASHES = {
    "Faceplate/ASM/Generator": "0d57b0826a9e86f3", "Faceplate/ASM/Instrument": "adeb26f127c67c3e",
    "Faceplate/ASM/Pump": "3917b6f50eb05c9c", "Faceplate/ASM/Sequence": "9fe4bb67115f292e",
    "Faceplate/ASM/Valve": "b2749b783f1f5581", "Faceplate/Alarms": "d386829494bbf86e",
    "Faceplate/Controller": "b5ae42ea05325c9b", "Faceplate/Empty": "052207094b8bc723",
    "Faceplate/Input": "72ad25f3ce74fcb2", "Faceplate/Instrument": "d8b79a8a55af63e7",
    "Faceplate/InterlockRow": "e8f71b8aa7f01be0", "Faceplate/LimitRow": "91277899c938becf",
    "Faceplate/Pump": "ff4acb159b7546ac", "Faceplate/Sequence": "35d7e64efc3dad2c",
    "Faceplate/SetpointRow": "fad283e11bef6b7b", "Faceplate/Tank": "f24f9339651e2b24",
    "Faceplate/TankTile": "8c2132c1b2cc0b72", "Faceplate/Valve": "18f34279c639914a"}
EXISTING_FACEPLATE_VIEW = {
    "pump": "Faceplate/Pump", "motor": "Faceplate/Pump", "fan": "Faceplate/Pump", "valve": "Faceplate/Valve",
    "analogvalve": "Faceplate/Valve", "damper": "Faceplate/Valve", "tank": "Faceplate/Tank",
    "instrument": "Faceplate/Instrument", "readout": "Faceplate/Instrument", "instrument-field": "Faceplate/Instrument",
    "controller": "Faceplate/Controller", "indicator": "Faceplate/Input", "sequence": "Faceplate/Sequence",
    "generator": "Faceplate/ASM/Generator"}
EXISTING_ASM_VIEW = {
    "pump": "Faceplate/ASM/Pump", "motor": "Faceplate/ASM/Pump", "fan": "Faceplate/ASM/Pump",
    "valve": "Faceplate/ASM/Valve", "analogvalve": "Faceplate/ASM/Valve", "damper": "Faceplate/ASM/Valve",
    "sequence": "Faceplate/ASM/Sequence", "instrument": "Faceplate/ASM/Instrument",
    "readout": "Faceplate/ASM/Instrument", "instrument-field": "Faceplate/ASM/Instrument",
    "generator": "Faceplate/ASM/Generator"}


def canon_hash(doc) -> str:
    return hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def walk(node):
    yield node
    for c in node.get("children") or []:
        yield from walk(c)


def named(doc, name):
    return next((n for n in walk(doc["root"]) if n.get("meta", {}).get("name") == name), None)


def bound(node, key):
    """The expression bound to `key` of a node's propConfig, or None."""
    b = ((node.get("propConfig") or {}).get(key) or {}).get("binding")
    return (b or {}).get("config", {}).get("expression") if b else None


def scripts_of(node) -> list[str]:
    """Every script an event of the node holds, whichever event it is."""
    found: list[str] = []

    def collect(x):
        if isinstance(x, dict):
            if isinstance(x.get("script"), str):
                found.append(x["script"])
            for v in x.values():
                collect(v)
        elif isinstance(x, list):
            for v in x:
                collect(v)
    collect(node.get("events") or {})
    return found


def clicks(view: dict) -> list[str]:
    """The scripts of the page that call `select_device`: the symbol clicks and the assemblies' clicks."""
    return [s for n in walk(view["root"]) for s in scripts_of(n) if "select_device" in s]


def kind_name(kind: str) -> str:
    return kind[:1].upper() + kind[1:]


class FaceplateViewTests(unittest.TestCase):
    """The view `Faceplate/ASM/Local` of the parent build."""

    @classmethod
    def setUpClass(cls):
        cls.views = framework.framework_views()
        cls._tmp = tempfile.TemporaryDirectory()
        cls.base = par.build_parent()[0].write(Path(cls._tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def local(self) -> dict:
        self.assertIn(LOCAL_FACEPLATE, self.views)
        return self.views[LOCAL_FACEPLATE]

    def test_the_parent_build_holds_the_local_faceplate_as_a_view_file(self):
        f = self.base / VIEWS / LOCAL_FACEPLATE / "view.json"
        self.assertTrue(f.is_file(), f)
        self.assertEqual(json.loads(f.read_text(encoding="utf-8")), self.local())

    def test_the_tab_row_is_home_alarms_info_and_each_tab_has_its_pane(self):
        doc = self.local()
        tabs = [c["meta"]["name"][4:] for c in named(doc, "Tabs")["children"] if c["meta"]["name"].startswith("Tab_")]
        self.assertEqual(tabs, ["home", "alarms", "info"])
        panes = [n["meta"]["name"][5:] for n in doc["root"]["children"] if n["meta"]["name"].startswith("Pane_")]
        self.assertEqual(panes, ["home", "alarms", "info"])
        self.assertEqual(doc["custom"]["tab"], "home")
        for key in tabs:
            self.assertEqual(bound(named(doc, f"Pane_{key}"), "position.display"), f"{{view.custom.tab}} = '{key}'")

    def test_the_view_is_in_the_asm_style_as_the_other_asm_faceplates_are(self):
        doc, other = self.local(), self.views["Faceplate/ASM/Sequence"]
        # the header strip comes first, then the tab row (framework._tabbed in the asm style)
        first = lambda d: [c["meta"]["name"] for c in d["root"]["children"]][:2]   # noqa: E731
        self.assertEqual(first(doc)[1], "Tabs")
        self.assertEqual(first(doc)[0], first(other)[0])
        self.assertEqual(named(doc, "Tabs")["props"].get("wrap"), named(other, "Tabs")["props"].get("wrap"))
        for name in ("Tab_home", "Tab_alarms", "Tab_info"):
            self.assertEqual(named(doc, name)["props"]["style"], named(other, name)["props"]["style"], name)

    def test_the_alarms_pane_embeds_faceplate_alarms_as_the_other_asm_faceplates_do(self):
        for path in (LOCAL_FACEPLATE, "Faceplate/ASM/Sequence"):
            pane = named(self.views[path], "Pane_alarms")
            embeds = [n for n in walk(pane) if n["type"] == "ia.display.view"]
            self.assertEqual([n["props"]["path"] for n in embeds], ["Faceplate/Alarms"], path)
            self.assertIsNotNone(bound(embeds[0], "props.params.source"), path)

    def test_the_view_takes_the_parameter_local_kind_beside_device_id_and_tab(self):
        doc = self.local()
        self.assertEqual(set(doc["params"]), {"deviceId", "tab", "localKind"})
        self.assertEqual(doc["params"]["localKind"], "")
        self.assertEqual(doc["propConfig"]["params.localKind"]["paramDirection"], "input")
        for other in ("deviceId", "tab"):
            self.assertEqual(doc["propConfig"][f"params.{other}"]["paramDirection"], "input")

    def test_home_embeds_the_local_home_view_by_an_expression_on_the_kind_with_the_views_device(self):
        home = named(self.local(), "Pane_home")
        embeds = [n for n in walk(home) if n["type"] == "ia.display.view"]
        self.assertEqual(len(embeds), 1)
        embed = embeds[0]
        self.assertEqual(embed["propConfig"]["props.path"]["binding"]["type"], "expr")
        self.assertEqual(bound(embed, "props.path"), HOME_PATH)
        self.assertEqual(bound(embed, "props.params.deviceId"), "{view.params.deviceId}")

    def test_no_other_faceplate_takes_the_local_kind(self):
        for path, doc in self.views.items():
            if path.startswith("Faceplate/") and path != LOCAL_FACEPLATE:
                self.assertNotIn("localKind", json.dumps(doc), path)

    # ---- G7 faceplates (corpus 3) ----------------------------------------------------------------------
    def test_g7_faceplates_checks_the_local_faceplate_and_passes_on_the_parent(self):
        self.assertIn(LOCAL_FACEPLATE, gates.FACEPLATES)
        res = gates.g7_faceplates(self.base, None)
        self.assertTrue(res["ok"], res["problems"])
        self.assertEqual(res["tabs"][LOCAL_FACEPLATE], ["home", "alarms", "info"])

    def _broken(self, mutate) -> list[str]:
        with tempfile.TemporaryDirectory() as d:
            copy_dir = Path(d) / "base"
            shutil.copytree(self.base, copy_dir)
            f = copy_dir / VIEWS / LOCAL_FACEPLATE / "view.json"
            doc = json.loads(f.read_text(encoding="utf-8"))
            mutate(doc, f)
            if f.exists():
                f.write_text(json.dumps(doc), encoding="utf-8")
            return gates.g7_faceplates(copy_dir, None)["problems"]

    def test_g7_faceplates_refuses_a_local_faceplate_missing_a_pane(self):
        def drop(doc, _f):
            doc["root"]["children"] = [c for c in doc["root"]["children"] if c["meta"]["name"] != "Pane_info"]
        self.assertIn(f"{LOCAL_FACEPLATE}: tab 'info' has no pane", self._broken(drop))

    def test_g7_faceplates_refuses_a_local_faceplate_whose_alarms_pane_embeds_something_else(self):
        def swap(doc, _f):
            for n in walk(named(doc, "Pane_alarms")):
                if n["type"] == "ia.display.view":
                    n["props"]["path"] = "Faceplate/Empty"
        self.assertTrue(any(p.startswith(LOCAL_FACEPLATE) and "Faceplate/Alarms" in p for p in self._broken(swap)))

    def test_g7_faceplates_refuses_a_parent_without_the_local_faceplate(self):
        self.assertIn(f"{LOCAL_FACEPLATE}: missing", self._broken(lambda doc, f: f.unlink()))


class TableTests(unittest.TestCase):
    """`local` in the closed tables, and the existing kinds untouched."""

    def test_local_is_mapped_to_the_local_faceplate_in_both_view_tables_whichever_the_style(self):
        self.assertEqual(framework.FACEPLATE_VIEW["local"], LOCAL_FACEPLATE)
        self.assertEqual(framework.ASM_VIEW["local"], LOCAL_FACEPLATE)
        self.assertEqual(framework.faceplate_view("local", "asm"), LOCAL_FACEPLATE)
        self.assertEqual(framework.faceplate_view("local", "openbridge"), LOCAL_FACEPLATE)

    def test_the_selection_expressions_open_the_local_faceplate_for_the_kind_local(self):
        entry = "'local', 'Faceplate/ASM/Local'"
        self.assertIn(entry, framework.FACEPLATE_OF_KIND)
        self.assertIn(entry, framework.FACEPLATE_OF_SELECTION)
        self.assertIn(entry, navigation.FLOAT_OF_PARAMS)
        self.assertTrue(framework.FACEPLATE_OF_KIND.endswith("'Faceplate/Empty')"))

    def test_the_profile_names_the_local_faceplate_for_the_device_kind_local_in_each_style(self):
        contracts = screen.load_contracts()
        kind = library_profile.build(contracts)["deviceKinds"]["local"]
        self.assertEqual(kind["faceplate"], LOCAL_FACEPLATE)
        self.assertEqual(kind["faceplates"], {"openbridge": LOCAL_FACEPLATE, "asm": LOCAL_FACEPLATE})
        self.assertIs(kind["openMembers"], True)

    def test_the_existing_kinds_keep_their_faceplates(self):
        self.assertEqual({k: v for k, v in framework.FACEPLATE_VIEW.items() if k != "local"}, EXISTING_FACEPLATE_VIEW)
        self.assertEqual({k: v for k, v in framework.ASM_VIEW.items() if k != "local"}, EXISTING_ASM_VIEW)
        for fp in ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/Tank", "Faceplate/Instrument", "Faceplate/Controller",
                   "Faceplate/Input", "Faceplate/Sequence", "Faceplate/ASM/Pump", "Faceplate/ASM/Valve",
                   "Faceplate/ASM/Generator", "Faceplate/ASM/Sequence", "Faceplate/ASM/Instrument"):
            self.assertIn(fp, gates.FACEPLATES)

    def test_the_existing_faceplate_views_are_unchanged(self):
        views = framework.framework_views()
        got = {k: canon_hash(v) for k, v in views.items() if k.startswith("Faceplate/") and k != LOCAL_FACEPLATE}
        self.assertEqual(got, EXISTING_FACEPLATE_HASHES)

    def test_the_session_declares_the_selected_local_kind_empty_by_default(self):
        self.assertEqual(par.session_defaults()["custom"]["selectedLocal"], "")
        self.assertEqual(par.session_defaults()["custom"]["selectedStyle"], "openbridge")   # the others as before


class OpenerTests(unittest.TestCase):
    """`library.open_device` and `cadre.hmi.select_device` with the keyword-only last argument `local`."""

    DEVICE = f"{TAG_ROOT}/Skid1"

    def test_open_device_takes_local_as_its_keyword_only_last_argument_defaulting_to_none(self):
        params = list(inspect.signature(library.open_device).parameters.values())
        self.assertEqual(params[-1].name, "local")
        self.assertEqual(params[-1].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIsNone(params[-1].default)
        with self.assertRaises(TypeError):
            library.open_device("x", "k", "t", "l", "tab", "", "'Skid'")   # not by position

    def test_the_opener_without_local_is_the_opener_of_before(self):
        plain = library.open_device("x", "k")
        self.assertEqual(plain[0], "cadre.hmi.select_device(self.session, x, k, '', '', '')")
        self.assertEqual(plain[1:], library.open_faceplate())
        lines = library.open_device("'[default]p/D1'", "d['kind']", "'D-1'", "'Pump 1'", "'alarms'", indent="\t")
        self.assertEqual(lines[0], "\tcadre.hmi.select_device(self.session, '[default]p/D1', d['kind'], 'D-1', 'Pump 1', 'alarms')")
        self.assertNotIn("local", "\n".join(lines))

    def test_the_opener_with_local_none_is_the_opener_without_it(self):
        self.assertEqual(library.open_device("x", "k", local=None), library.open_device("x", "k"))

    def test_the_opener_with_local_passes_the_kind_expression_to_select_device_and_then_opens_the_faceplate(self):
        lines = library.open_device("'[default]p/S1'", "'local'", "'Skid'", "'Skid 1'", "''", indent="\t", local="'Skid'")
        self.assertRegex(lines[0], r"^\tcadre\.hmi\.select_device\(self\.session, '\[default\]p/S1', 'local', 'Skid', "
                                   r"'Skid 1', '',\s*local\s*=\s*'Skid'\)$")
        self.assertEqual(lines[1:], library.open_faceplate("\t"))

    def test_select_device_takes_local_last_by_keyword_and_defaults_to_none(self):
        ns, _ = hmi_ns({})
        params = list(inspect.signature(ns["select_device"]).parameters.values())
        self.assertEqual([p.name for p in params][:6], ["session", "device_id", "kind", "title", "label", "tab"])
        self.assertEqual(params[-1].name, "local")
        self.assertIsNone(params[-1].default)

    def test_select_device_writes_the_selected_local_kind(self):
        ns, _ = hmi_ns({})
        entry = {"folder": self.DEVICE, "kind": "local", "title": "Skid", "label": "Skid 1", "unit": ""}
        s = session(["Administrator"], devices=[entry])
        ns["select_device"](s, self.DEVICE, "local", "Skid", "Skid 1", "", local="Skid")
        self.assertEqual((s.custom.selectedDevice, s.custom.selectedKind, s.custom.selectedLocal),
                         (self.DEVICE, "local", "Skid"))
        self.assertEqual(s.custom.selectedTab, "")
        ns["select_device"](s, self.DEVICE, "local", "Skid", "Skid 1", "alarms", local="Skid")   # the tab as before
        self.assertEqual((s.custom.selectedTab, s.custom.selectedLocal), ("alarms", "Skid"))

    def test_select_device_of_a_library_kind_behaves_as_before(self):
        device = f"{TAG_ROOT}/P1"
        ns, _ = hmi_ns({f"{device}/state": True})
        s = session(["Administrator"], devices=[{"folder": device, "kind": "pump", "title": "P-1", "label": "", "unit": ""}])
        ns["select_device"](s, device, "pump", "P-1", "Pump 1")
        self.assertEqual((s.custom.selectedDevice, s.custom.selectedKind, s.custom.selectedTitle, s.custom.selectedLabel,
                          s.custom.selectedTab), (device, "pump", "P-1", "Pump 1", ""))
        ns["select_device"](s, device, "pump", "P-1", "Pump 1", "alarms")
        self.assertEqual(s.custom.selectedTab, "alarms")

    def test_the_float_parameters_carry_the_selected_local_kind(self):
        ns, _ = hmi_ns({})
        entry = {"folder": self.DEVICE, "kind": "local", "title": "Skid", "label": "Skid 1", "unit": ""}
        s = session(["Administrator"], devices=[entry])
        ns["select_device"](s, self.DEVICE, "local", "Skid", "Skid 1", "", local="Skid")
        got = ns["float_params"](s, "fid")
        self.assertEqual(got["localKind"], "Skid")
        self.assertEqual((got["deviceId"], got["kind"], got["popupId"]), (self.DEVICE, "local", "fid"))

    def test_an_existing_symbols_click_is_unchanged(self):
        doc, _contract = library.library_views()["Automation/Generator"]
        script = doc["root"]["events"]["dom"]["onClick"]["config"]["script"]
        self.assertIn("cadre.hmi.select_device(self.session,", script)
        line = next(ln for ln in script.splitlines() if "select_device" in ln)
        self.assertNotIn("local", line)
        self.assertNotIn("selectedLocal", script)


class HostTests(unittest.TestCase):
    """The dock, the popup and the float pass the local kind on."""

    @classmethod
    def setUpClass(cls):
        cls.views = framework.framework_views()
        cls.float = navigation.float_faceplate()

    def body(self, doc):
        return named(doc, "Faceplate")

    def test_the_dock_and_the_popup_pass_the_local_kind_from_the_session(self):
        for path in ("Framework/SideMenu", framework.FACEPLATE_POPUP_VIEW):
            node = self.body(self.views[path])
            self.assertIn("{session.custom.selectedLocal}", bound(node, "props.params.localKind") or "", path)
            self.assertEqual(node["props"]["params"]["localKind"], "", path)
            self.assertEqual(bound(node, "props.path"), framework.FACEPLATE_OF_SELECTION, path)
            self.assertIn("props.params.tab", node["propConfig"], path)

    def test_the_float_takes_the_parameter_and_passes_it_on_from_its_own_parameter(self):
        self.assertIn("localKind", navigation.FLOAT_PARAMS)
        self.assertEqual(navigation.FLOAT_PARAMS["localKind"], "")
        self.assertEqual(list(navigation.FLOAT_PARAMS)[:7], ["popupId", "deviceId", "kind", "style", "title", "label", "tab"])
        self.assertEqual(self.float["params"]["localKind"], "")
        self.assertEqual(self.float["propConfig"]["params.localKind"]["paramDirection"], "input")
        node = self.body(self.float)
        expr = bound(node, "props.params.localKind") or ""
        self.assertIn("{view.params.localKind}", expr)
        self.assertNotIn("selected", expr)
        self.assertEqual(node["props"]["params"]["localKind"], "")
        self.assertEqual(bound(node, "props.path"), navigation.FLOAT_OF_PARAMS)


class ClickTests(unittest.TestCase):
    """An assembly embedded on a page opens the local faceplate."""

    @classmethod
    def setUpClass(cls):
        cls.base = L.Parent()

    @classmethod
    def tearDownClass(cls):
        cls.base.close()

    def build(self, *assemblies, **kw):
        kw.setdefault("dev", devices(*[a["device"] for a in assemblies]))
        kw.setdefault("local_kinds", sorted({a["kind"] for a in assemblies}))
        return self.base.screen(page(*assemblies), **kw)

    def test_the_assembly_carries_a_click_that_opens_the_faceplate_for_the_kind_local_and_its_kind(self):
        res = self.build(assembly())
        self.assertEqual(res.code, 0, res.text[-2000:])
        found = clicks(res.view("Screens/PageA"))
        self.assertEqual(len(found), 1, found)
        script = found[0]
        self.assertRegex(script, r"cadre\.hmi\.select_device\(self\.session, [^\n]*'local'[^\n]*local\s*=\s*'Skid'\)")
        self.assertIn(f"{TAG_ROOT}/Skid1", script)
        self.assertIn("openDock", script)      # the same lines as any opener: the dock, or the popup for the mode
        self.assertIn("openPopup", script)

    def test_the_click_is_the_librarys_opener_with_the_kind_in_the_view_name_case(self):
        res = self.build(assembly(kind="tank-skid"))
        self.assertEqual(res.code, 0, res.text[-2000:])
        found = clicks(res.view("Screens/PageA"))
        self.assertEqual(len(found), 1, found)
        script = found[0]
        self.assertIn("'local'", script)
        self.assertRegex(script, r"local\s*=\s*'Tank-skid'")
        for line in library.open_faceplate():
            self.assertIn(line.strip(), script)

    def test_each_assembly_has_its_own_click_with_its_own_device(self):
        a1 = assembly("A1", device="Skid1", x=40, y=40)
        a2 = assembly("A2", device="Skid2", title="Skid two", label="Second", x=320, y=200)
        res = self.build(a1, a2)
        self.assertEqual(res.code, 0, res.text[-2000:])
        found = clicks(res.view("Screens/PageA"))
        self.assertEqual(len(found), 2, found)
        for device in ("Skid1", "Skid2"):
            self.assertEqual(len([s for s in found if f"{TAG_ROOT}/{device}" in s]), 1, device)
        for s in found:
            self.assertRegex(s, r"local\s*=\s*'Skid'")

    def test_two_kinds_on_one_page_click_with_their_own_kind(self):
        res = self.build(assembly("A1", kind="skid", device="Skid1"),
                         assembly("A2", kind="tank-skid", device="Tank1", x=400, y=200),
                         dev=devices("Skid1", "Tank1"), local_kinds=["skid", "tank-skid"])
        self.assertEqual(res.code, 0, res.text[-2000:])
        found = clicks(res.view("Screens/PageA"))
        self.assertEqual(len(found), 2, found)
        by_device = {d: s for d in ("Skid1", "Tank1") for s in found if f"{TAG_ROOT}/{d}" in s}
        self.assertRegex(by_device["Skid1"], r"local\s*=\s*'Skid'")
        self.assertRegex(by_device["Tank1"], r"local\s*=\s*'Tank-skid'")

    def test_the_page_with_the_click_still_passes_g0_to_g7_including_the_local_faceplate(self):
        res = self.build(assembly())
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertIs(res.report["gates"]["ok"], True)
        fp = res.report["gates"]["G7_faceplates"]
        self.assertTrue(fp["ok"], fp["problems"])
        self.assertEqual(fp["tabs"][LOCAL_FACEPLATE], ["home", "alarms", "info"])

    def test_the_embed_still_draws_the_kind_view_with_the_device_folder(self):
        res = self.build(assembly(x=120, y=60, w=200, h=180))
        embeds = [n for n in nodes(res.view("Screens/PageA"))
                  if n["type"] == "ia.display.view" and n["props"]["path"] == f"Local/{KIND_VIEW}/Assembly"]
        self.assertEqual(len(embeds), 1)
        self.assertEqual(embeds[0]["props"]["params"]["deviceId"], f"{TAG_ROOT}/Skid1")
        self.assertEqual({k: embeds[0]["position"][k] for k in ("x", "y", "width", "height")},
                         {"x": 120, "y": 60, "width": 200, "height": 180})

    def test_the_component_test_pages_benchlocal_assembly_opens_the_local_faceplate(self):
        doc = page()
        doc.pop("assemblies")
        res = self.base.screen(doc, local_kinds=[testbench.LOCAL_KIND], extra=["--component-test"])
        self.assertEqual(res.code, 0, res.text[-2500:])
        found = [s for s in clicks(res.view("Screens/ComponentTest")) if "'local'" in s]
        self.assertEqual(len(found), 1, found)
        self.assertRegex(found[0], r"local\s*=\s*'Benchlocal'")
        self.assertIn("/Bench/Local1", found[0])
        fp = res.report["gates"]["G7_faceplates"]
        self.assertTrue(fp["ok"], fp["problems"])
        self.assertIn(LOCAL_FACEPLATE, fp["tabs"])

    def test_a_page_with_no_assembly_has_no_local_click(self):
        doc = page()
        doc.pop("assemblies")
        res = self.base.screen(doc)
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertEqual([s for s in clicks(res.view("Screens/PageA")) if "'local'" in s], [])


if __name__ == "__main__":
    unittest.main()
