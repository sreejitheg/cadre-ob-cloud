"""Tests of the assembly element of the screen descriptor and its registration (NOTE-WFB-10 section 3.3 and section 11.2
items 1 to 4 and 6; acceptance corpus 3 (offline part, G0 to G7), 5, 7 and 8; threats T1, T2, T4 and T5). Work package
WP-W03, written from the note before the feature exists.

The assembly is a part set drawn on a diagram page for a device kind of its own (`skid` here, a synthetic name), written
once per kind as the views `Local/<Kind>/Assembly` and `Local/<Kind>/Home` (siblings: GF-117). `screen.py --local-kinds <file>` lists the kinds a page
may draw as an assembly; G0 refuses any other, with a rule name in the screen report's `gates.G0.errors[]`.

Run from the repository root:  python -m unittest discover -s tests
Nothing here needs the gateway or a browser. The faceplate (`Faceplate/ASM/Local`, item 5) and the assembly's click belong
to WP-W04 and are not tested here.
"""
import copy
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import local_support as L  # noqa: E402
from local_support import KIND, KIND_VIEW, RULES, TAG_ROOT, assembly, devices, nodes, page, parts  # noqa: E402

from hmi import gates, library_profile, screen  # noqa: E402


def ordered(rules):
    """True when the rule names are listed in the order of NOTE-WFB-10 section 11.2 item 6."""
    return rules == sorted(rules, key=RULES.index)


def texts(view: dict) -> list:
    return [n.get("props", {}).get("text") for n in nodes(view)]


class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = L.Parent()

    @classmethod
    def tearDownClass(cls):
        cls.base.close()

    def build(self, descs, **kw):
        return self.base.screen(descs, **kw)

    def valid(self, *assemblies, **kw):
        kw.setdefault("dev", devices(*[a["device"] for a in assemblies]))
        kw.setdefault("local_kinds", sorted({a["kind"] for a in assemblies}))
        return self.build(page(*assemblies), **kw)

    # ---- corpus 3 (offline): a valid assembly passes G0 to G7 and writes its views ----------------------------
    def test_a_diagram_page_with_one_valid_assembly_passes_g0_to_g7_when_its_kind_is_listed(self):
        res = self.valid(assembly())
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertRegex(res.out, r"G0_descriptor_schema\s+PASS")
        self.assertIs(res.report["gates"]["ok"], True)
        self.assertEqual(res.g0_errors(), [])
        failing = {k: v for k, v in res.report["gates"].items() if isinstance(v, dict) and not v.get("ok", True)}
        self.assertEqual(failing, {})
        self.assertIn(f"Local/{KIND_VIEW}/Assembly/view.json", res.view_files())
        self.assertIn(f"Local/{KIND_VIEW}/Home/view.json", res.view_files())

    def test_the_kind_view_and_its_home_are_coordinate_roots_named_diagram(self):
        res = self.valid(assembly())
        self.assertEqual(res.code, 0, res.text[-2000:])
        for path in (f"Local/{KIND_VIEW}/Assembly", f"Local/{KIND_VIEW}/Home"):
            view = res.view(path)
            self.assertIsNotNone(view, path)
            self.assertEqual((view["root"]["type"], view["root"]["meta"]["name"]), ("ia.container.coord", "Diagram"), path)

    def test_a_home_is_one_label_no_detail_when_the_assembly_gives_none(self):
        a = assembly()
        a.pop("home")   # the fixture's Home holds the button (a button is allowed in a Home only); this one gives none
        res = self.valid(a)
        self.assertEqual(res.code, 0, res.text[-2000:])
        home = res.view(f"Local/{KIND_VIEW}/Home")
        self.assertEqual([t for t in texts(home) if t], ["No detail"])
        self.assertNotIn("No detail", [t for t in texts(res.view(f"Local/{KIND_VIEW}/Assembly")) if t])

    def test_a_home_the_assembly_gives_draws_its_parts_and_no_label_no_detail(self):
        home = {"w": 240, "h": 120, "parts": {
            "labels": [{"id": "HT", "x": 8, "y": 6, "w": 150, "h": 20, "text": "Detail heading", "style": "heading"}],
            "symbols": [{"id": "HR", "kind": "readout", "x": 8, "y": 40, "w": 120, "h": 40, "member": "value"}]}}
        res = self.valid(assembly(home=home))
        self.assertEqual(res.code, 0, res.text[-2000:])
        shown = [t for t in texts(res.view(f"Local/{KIND_VIEW}/Home")) if t]
        self.assertIn("Detail heading", shown)
        self.assertNotIn("No detail", shown)

    def test_the_page_embeds_the_kind_view_with_the_device_folder_and_the_assemblys_box(self):
        res = self.valid(assembly(x=120, y=60, w=200, h=180))
        self.assertEqual(res.code, 0, res.text[-2000:])
        embeds = [n for n in nodes(res.view("Screens/PageA"))
                  if n["type"] == "ia.display.view" and n["props"]["path"] == f"Local/{KIND_VIEW}/Assembly"]
        self.assertEqual(len(embeds), 1)
        self.assertEqual(embeds[0]["props"]["params"]["deviceId"], f"{TAG_ROOT}/Skid1")
        pos = embeds[0]["position"]
        self.assertEqual((pos["x"], pos["y"], pos["width"], pos["height"]), (120, 60, 200, 180))

    def test_the_parts_bind_the_device_folder_joined_with_their_member_and_hold_no_static_value(self):
        res = self.valid(assembly())
        self.assertEqual(res.code, 0, res.text[-2000:])
        body = json.dumps(res.view(f"Local/{KIND_VIEW}/Assembly")) + json.dumps(res.view(f"Local/{KIND_VIEW}/Home"))   # the button is in the Home
        self.assertIn("view.params.deviceId", body)
        for member in ("value", "state", "cmdStart"):
            self.assertIn(member, body)
        # T4: no value component of the built views reads no tag (the page check classifies the built views)
        from hmi import page_checks
        counts, unbound = page_checks.built_tags(res.child / "com.inductiveautomation.perspective", ["PageA"])
        self.assertEqual(unbound, [])
        self.assertTrue(sum(counts.values()) >= 3, counts)

    def test_two_assemblies_of_one_kind_write_the_kind_view_once(self):
        a1 = assembly("A1", device="Skid1", title="Skid one", label="First", x=40, y=40)
        a2 = assembly("A2", device="Skid2", title="Skid two", label="Second", x=300, y=200)
        res = self.valid(a1, a2)
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertEqual([f for f in res.view_files() if f.startswith("Local/")],
                         [f"Local/{KIND_VIEW}/Assembly/view.json", f"Local/{KIND_VIEW}/Home/view.json"])
        embeds = [n for n in nodes(res.view("Screens/PageA"))
                  if n["type"] == "ia.display.view" and n["props"]["path"] == f"Local/{KIND_VIEW}/Assembly"]
        self.assertEqual(sorted(n["props"]["params"]["deviceId"] for n in embeds), [f"{TAG_ROOT}/Skid1", f"{TAG_ROOT}/Skid2"])

    def test_the_project_holds_the_kind_view_once_in_the_generator(self):
        a1, a2 = assembly("A1", device="Skid1"), assembly("A2", device="Skid2", x=300)
        child, _ = screen.build_child("cadre_hmi_loc", [page(a1, a2)], "Loc", devices=devices("Skid1", "Skid2"))
        views = sorted(k for k in child.files if "/views/Local/" in k and k.endswith("/view.json"))
        self.assertEqual(len(views), 2, views)

    def test_the_view_name_is_the_kind_with_its_first_letter_in_upper_case_only(self):
        res = self.valid(assembly(kind="tank-skid"))
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertIn("Local/Tank-skid/Assembly/view.json", res.view_files())
        self.assertIn("Local/Tank-skid/Home/view.json", res.view_files())

    def test_canonical_json_decides_equality_so_the_order_of_keys_does_not_matter(self):
        a1 = assembly("A1", device="Skid1")
        a2 = assembly("A2", device="Skid2", x=300)
        a2["parts"] = {k: [dict(reversed(list(p.items()))) for p in a2["parts"][k]] for k in reversed(list(a2["parts"]))}
        res = self.valid(a1, a2)
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertNotIn("assembly-parts-differ", res.text)

    # ---- registration (item 3) ---------------------------------------------------------------------------------
    def test_descriptor_items_yield_an_assembly_as_an_item_of_kind_local(self):
        desc = page(assembly("A1", device="Skid1"))
        item = next(i for i in screen.descriptor_items(desc) if i["id"] == "A1")
        self.assertEqual((item["kind"], item["device"], item["params"]), ("local", "Skid1", {"localKind": KIND_VIEW}))

    def test_the_device_is_in_the_hierarchy_the_index_the_tag_document_and_the_session(self):
        desc, model = page(assembly("A1", device="Skid1")), devices("Skid1")
        folder = f"{TAG_ROOT}/Skid1"
        self.assertEqual(screen.device_nodes([desc], model), {folder: "Plant"})
        plant = next(n for n in screen.hierarchy([desc], model) if n["path"] == "Plant")
        self.assertEqual(plant["devices"], [folder])
        entry = next(e for e in screen.device_index([desc], model) if e["folder"] == folder)
        self.assertEqual((entry["kind"], entry["local"]), ("local", KIND_VIEW))
        self.assertEqual(entry["members"], ["cmdStart", "state", "value"])
        self.assertEqual(entry["pulses"], [{"member": "cmdStart", "caption": "Start"}])
        leaves = gates._tag_leaves(screen.tags_document([desc], model))
        self.assertEqual({k.split("/Skid1/", 1)[1] for k in leaves if "/Skid1/" in k and not k.endswith("/")}, {"value", "state", "cmdStart"})
        res = self.valid(assembly("A1", device="Skid1"))
        self.assertEqual(res.code, 0, res.text[-2000:])
        props = json.loads((res.child / "com.inductiveautomation.perspective" / "session-props" / "props.json")
                           .read_text(encoding="utf-8"))
        self.assertEqual([(d["kind"], d["local"]) for d in props["custom"]["devices"] if d["folder"] == folder],
                         [("local", KIND_VIEW)])
        plant = next(n for n in props["custom"]["hierarchy"] if n["path"] == "Plant")
        self.assertEqual(plant["devices"], [folder])

    def test_the_device_label_defaults_to_the_assembly_id_and_is_the_label_when_given(self):
        bare = assembly("A1", device="Skid1")
        del bare["title"], bare["label"]
        desc = page(bare, assembly("A2", device="Skid2", label="Second skid", x=300))
        index = {e["folder"].rsplit("/", 1)[1]: e for e in screen.device_index([desc])}
        self.assertEqual((index["Skid1"]["label"], index["Skid2"]["label"]), ("A1", "Second skid"))
        self.assertEqual(screen.schema_errors([desc], ["d"]), [])    # title and label are optional (item 1)

    def test_g7_devices_accepts_every_member_the_devices_file_lists_for_a_local_device(self):
        profile = library_profile.build(screen.load_contracts())
        self.assertIn("local", sorted(profile["deviceKinds"]))
        self.assertEqual([m for m, spec in profile["deviceKinds"]["local"]["members"].items() if spec.get("required")], [])
        model = devices("Skid1")
        model["devices"][0]["members"].update({
            "pressureOutlet": {"type": "Float8", "access": "read"}, "runText": {"type": "String", "access": "read"},
            "cmdOpen": {"type": "Boolean", "access": "write", "pulse": True, "caption": "Open"}})
        desc = page(assembly("A1", device="Skid1"))
        out = gates.g7_devices(model, profile, screen.device_symbols([desc], model))
        self.assertEqual(out["problems"], [])
        self.assertTrue(out["ok"])
        self.assertEqual(out["devices"], 1)

    # ---- G0 rules (item 6) and corpus 5, 8 -----------------------------------------------------------------------
    def test_a_kind_absent_from_the_local_kinds_file_is_refused(self):
        for listed in (["other"], []):
            res = self.build(page(assembly(kind="widget")), dev=devices("Skid1"), local_kinds=listed)
            self.assertNotEqual(res.code, 0, listed)
            self.assertEqual(res.g0_rules(), ["assembly-kind-not-local"], (listed, res.g0_errors()))

    def test_a_pump_drawn_as_an_assembly_breaks_both_rules_in_order_when_it_is_not_listed(self):
        res = self.build(page(assembly(kind="pump")), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        self.assertEqual(res.g0_rules(), ["assembly-kind-not-local", "assembly-kind-is-library"], res.g0_errors())

    def test_a_library_kind_is_refused_even_when_the_local_kinds_file_lists_it(self):
        for kind in ("pump", "valve", "readout", "instrument-field", "filter", "switch", "generator"):
            res = self.build(page(assembly(kind=kind)), dev=devices("Skid1"), local_kinds=[kind, KIND])
            self.assertNotEqual(res.code, 0, kind)
            self.assertEqual(res.g0_rules(), ["assembly-kind-is-library"], (kind, res.g0_errors()))

    def test_any_assembly_is_refused_when_the_option_is_absent(self):
        res = self.build(page(assembly()), dev=devices("Skid1"), local_kinds=None)
        self.assertNotEqual(res.code, 0)
        self.assertIn("assembly-without-local-kinds", res.g0_rules(), res.g0_errors())
        self.assertTrue(ordered(res.g0_rules()))
        res = self.build(page(assembly(kind="pump")), dev=devices("Skid1"), local_kinds=None)
        self.assertNotEqual(res.code, 0)
        self.assertTrue({"assembly-kind-is-library", "assembly-without-local-kinds"} <= set(res.g0_rules()), res.g0_errors())
        self.assertTrue(ordered(res.g0_rules()), res.g0_rules())

    def test_a_colour_key_on_a_part_is_refused_whatever_the_part(self):
        for array, mutate in (
                ("labels", lambda p: p.update(colour="red")),
                ("symbols", lambda p: p.update(colour="#ff0000")),
                ("buttons", lambda p: p.update(colour="blue")),
                ("lines", lambda p: p.update(colour="green")),
                ("shapes", lambda p: p.update(colour="black"))):
            a = assembly()
            mutate((a["home"] if array == "buttons" else a)["parts"][array][0])   # a button lives in the Home
            res = self.build(page(a), dev=devices("Skid1"), local_kinds=[KIND])
            self.assertNotEqual(res.code, 0, array)
            self.assertEqual(res.g0_rules(), ["assembly-style"], (array, res.g0_errors()))

    def test_a_colour_key_on_a_part_of_the_home_is_refused(self):
        home = {"w": 200, "h": 80, "parts": {"labels": [{"id": "HT", "x": 0, "y": 0, "w": 100, "h": 20, "text": "x",
                                                         "colour": "red"}]}}
        res = self.build(page(assembly(home=home)), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        self.assertEqual(res.g0_rules(), ["assembly-style"], res.g0_errors())

    def test_a_class_a_style_object_or_the_american_spelling_on_a_part_is_refused(self):
        control = self.valid(assembly())
        self.assertEqual(control.code, 0, control.text[-2000:])    # the same assembly without the key builds
        for array, key, value in (("symbols", "class", "danger"), ("labels", "classes", ["danger"]),
                                  ("labels", "style", {"color": "red"}), ("symbols", "style", {"fill": "red"}),
                                  ("shapes", "color", "red"), ("buttons", "class", "primary")):
            a = assembly()
            (a["home"] if array == "buttons" else a)["parts"][array][0][key] = value   # a button lives in the Home
            res = self.build(page(a), dev=devices("Skid1"), local_kinds=[KIND])
            self.assertNotEqual(res.code, 0, (array, key))
            self.assertTrue("assembly-style" in res.g0_rules() or re.search(r"G0_descriptor_schema\s+FAIL", res.out),
                            (array, key, res.text[-600:]))

    def test_the_other_style_values_a_part_may_state_are_not_refused(self):
        # `style` of a label (heading, body, label) and of a line (solid, dashed) is an enumeration, not a free style
        a = assembly()
        a["parts"]["labels"][0]["style"] = "body"
        a["parts"]["lines"][0]["style"] = "solid"
        res = self.valid(a)
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertNotIn("assembly-style", res.text)

    def test_assemblies_of_one_kind_that_differ_in_parts_or_size_are_refused(self):
        def other(**change):
            a2 = assembly("A2", device="Skid2", x=300)
            for k, v in change.items():
                a2[k] = v
            return a2
        differing = {
            "parts": other(parts={**parts(), "labels": [{"id": "T", "x": 10, "y": 8, "w": 120, "h": 20, "text": "Other"}]}),
            "w": other(w=210), "h": other(h=190),
            "home": other(home={"w": 100, "h": 40, "parts": {"labels": [{"id": "H", "x": 0, "y": 0, "w": 50, "h": 20,
                                                                          "text": "More"}]}})}
        for what, a2 in differing.items():
            res = self.build(page(assembly("A1", device="Skid1"), a2), dev=devices("Skid1", "Skid2"), local_kinds=[KIND])
            self.assertNotEqual(res.code, 0, what)
            self.assertEqual(res.g0_rules(), ["assembly-parts-differ"], (what, res.g0_errors()))

    def test_only_the_id_device_title_label_x_and_y_may_differ_between_assemblies_of_a_kind(self):
        a2 = assembly("A2", device="Skid2", title="Other title", label="Other label", x=500, y=300)
        res = self.valid(assembly("A1", device="Skid1"), a2)
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertEqual(res.g0_errors(), [])

    def test_assemblies_of_different_kinds_may_differ_in_parts(self):
        a2 = assembly("A2", kind="tank-skid", device="Skid2", x=300, w=250)
        a2["parts"]["labels"][0]["text"] = "Tank skid"
        res = self.valid(assembly("A1", device="Skid1"), a2)
        self.assertEqual(res.code, 0, res.text[-2000:])

    def test_an_assembly_on_a_cards_page_is_refused(self):
        self.assertEqual(self.valid(assembly()).code, 0)    # the same assembly on a diagram page builds
        cards = page(assembly(), layout="cards", rows=[])
        cards["screen"].pop("node", None)
        res = self.build(cards, dev=devices("Skid1"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        self.assertEqual(res.g0_rules(), ["assembly-on-cards"], res.g0_errors())

    def test_every_rule_that_applies_is_listed_in_the_order_of_the_note(self):
        bad = assembly("A1", kind="pump", device="Skid1")
        bad["parts"]["labels"][0]["colour"] = "red"
        s1, s2 = assembly("A2", device="Skid2", x=300), assembly("A3", device="Skid3", x=500, w=230)
        doc = page(bad, s1, s2, layout="cards", rows=[])
        doc["screen"].pop("node", None)
        res = self.build(doc, dev=devices("Skid1", "Skid2", "Skid3"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        self.assertEqual(res.g0_rules(), list(RULES[:2]) + ["assembly-style", "assembly-parts-differ", "assembly-on-cards"],
                         res.g0_errors())
        # with the option absent the third rule takes the place of the first
        res = self.build(doc, dev=devices("Skid1", "Skid2", "Skid3"), local_kinds=None)
        self.assertNotEqual(res.code, 0)
        rules = res.g0_rules()
        self.assertTrue(ordered(rules), rules)
        self.assertTrue({"assembly-kind-is-library", "assembly-without-local-kinds", "assembly-style",
                         "assembly-parts-differ", "assembly-on-cards"} <= set(rules), rules)

    def test_a_library_kind_with_other_letters_is_no_way_round_the_rule(self):
        self.assertEqual(screen.schema_errors([page(assembly(kind="pump"))], ["d"]), [])   # the schema admits the word
        for kind in ("Pump", "PUMP", "pump ", "pump_", "1pump", ""):
            a = assembly(kind=kind)
            self.assertNotEqual(screen.schema_errors([page(a)], ["d"]), [], repr(kind))   # the pattern of item 1
            res = self.build(page(a), dev=devices("Skid1"), local_kinds=[kind or KIND, KIND])
            self.assertNotEqual(res.code, 0, repr(kind))

    def test_a_kind_that_only_begins_like_a_library_kind_is_a_local_kind(self):
        res = self.valid(assembly(kind="pumpstand"))
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertIn("Local/Pumpstand/Assembly/view.json", res.view_files())

    # ---- the schema (item 1) ---------------------------------------------------------------------------------------
    def errors(self, mutate) -> list:
        self.assertEqual(screen.schema_errors([page(assembly())], ["d"]), [], "the unchanged assembly is valid")
        a = assembly()
        mutate(a)
        return screen.schema_errors([page(a)], ["d"])

    def test_the_schema_admits_the_assembly_with_every_part_array_and_every_shape_form(self):
        a = assembly()
        a["parts"]["shapes"] = [
            {"id": "S1", "x": 0, "y": 0, "w": 50, "h": 20, "form": "rect"},
            {"id": "S2", "x": 0, "y": 0, "w": 50, "h": 20, "form": "ellipse"},
            {"id": "S3", "x": 0, "y": 0, "w": 50, "h": 20, "form": "polyline", "points": [[0, 0], [10, 10], [20, 0]]},
            {"id": "S4", "x": 0, "y": 0, "w": 50, "h": 20, "form": "polygon", "points": [[0, 0], [10, 10], [20, 0]]}]
        a["home"] = {"w": 100, "h": 50, "parts": {"labels": [{"id": "HL", "x": 0, "y": 0, "w": 50, "h": 20, "text": "t"}]}}
        self.assertEqual(screen.schema_errors([page(a)], ["d"]), [])

    def test_points_are_forbidden_on_rect_and_ellipse_and_required_on_polyline_and_polygon(self):
        base = {"x": 0, "y": 0, "w": 50, "h": 20}
        self.assertEqual(self.errors(lambda a: a["parts"].update(shapes=[{"id": "S", "form": "polygon", **base,
                                                                           "points": [[0, 0], [5, 5], [9, 0]]}])), [])
        for form in ("rect", "ellipse"):
            errs = self.errors(lambda a: a["parts"].update(shapes=[{"id": "S", "form": form, **base,
                                                                     "points": [[0, 0], [5, 5]]}]))
            self.assertTrue(any("shapes" in e for e in errs), (form, errs))
        for form in ("polyline", "polygon"):
            errs = self.errors(lambda a: a["parts"].update(shapes=[{"id": "S", "form": form, **base}]))
            self.assertTrue(any("shapes" in e for e in errs), (form, errs))

    def test_a_refused_shape_stops_the_build_at_g0(self):
        a = assembly()
        a["parts"]["shapes"] = [{"id": "S", "x": 0, "y": 0, "w": 50, "h": 20, "form": "rect", "points": [[0, 0], [5, 5]]}]
        res = self.build(page(a), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        self.assertIn("FAIL", res.out)
        self.assertEqual(self.valid(assembly()).code, 0)    # the same page with a valid shape builds

    def test_the_schema_refuses_values_outside_the_enumerations(self):
        cases = {
            "align": lambda a: a["parts"]["labels"][0].update(align="justify"),
            "label style": lambda a: a["parts"]["labels"][0].update(style="bold"),
            "symbol kind pump": lambda a: a["parts"]["symbols"][0].update(kind="pump"),
            "symbol kind tank": lambda a: a["parts"]["symbols"][0].update(kind="tank"),
            "symbol states": lambda a: a["parts"]["symbols"][1].update(states=[{"value": 0, "colour": "red"}]),
            "symbol stateDefault": lambda a: a["parts"]["symbols"][1].update(stateDefault="red"),
            "symbol params": lambda a: a["parts"]["symbols"][0].update(params={"hasTag": True}),
            "line style": lambda a: a["parts"]["lines"][0].update(style="dotted"),
            "shape form": lambda a: a["parts"]["shapes"][0].update(form="star"),
            "a kind with capitals": lambda a: a.update(kind="Skid"),
            "a kind with an underscore": lambda a: a.update(kind="skid_one"),
            "a kind that starts with a digit": lambda a: a.update(kind="2skid"),
        }
        for what, mutate in cases.items():
            self.assertNotEqual(self.errors(mutate), [], what)

    def test_the_schema_accepts_the_symbol_kinds_the_note_lists(self):
        for kind in ("readout", "indicator", "instrument-field"):
            self.assertEqual(self.errors(lambda a: a["parts"]["symbols"][0].update(kind=kind)), [], kind)

    def test_the_assembly_keys_the_note_requires_are_required(self):
        # id, kind, device, x, y and w are required under every reading of "the first eight required"
        for key in ("id", "kind", "device", "x", "y", "w"):
            self.assertNotEqual(self.errors(lambda a: a.pop(key)), [], key)

    def test_a_part_set_holds_at_least_one_part(self):
        for empty in ({}, {"labels": []}, {"labels": [], "symbols": [], "lines": [], "buttons": [], "shapes": []}):
            self.assertNotEqual(self.errors(lambda a: a.update(parts=empty)), [], empty)

    def test_a_part_id_repeated_in_parts_and_home_or_within_parts_is_refused(self):
        dup_home = assembly(home={"w": 100, "h": 50, "parts": {"labels": [{"id": "T", "x": 0, "y": 0, "w": 50, "h": 20,
                                                                           "text": "same id as a part"}]}})
        res = self.build(page(dup_home), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        dup_within = assembly()
        dup_within["parts"]["symbols"][0]["id"] = dup_within["parts"]["labels"][0]["id"]   # the button moved to the Home
        res = self.build(page(dup_within), dev=devices("Skid1"), local_kinds=[KIND])
        self.assertNotEqual(res.code, 0)
        self.assertEqual(self.valid(assembly(home={"w": 100, "h": 50, "parts": {"labels": [
            {"id": "HOME_T", "x": 0, "y": 0, "w": 50, "h": 20, "text": "distinct"}]}})).code, 0)

    def test_the_page_without_assemblies_is_unchanged(self):
        doc = page()
        doc.pop("assemblies")
        self.assertEqual(screen.schema_errors([doc], ["d"]), [])
        res = self.build(doc, dev=None, local_kinds=None)
        self.assertEqual(res.code, 0, res.text[-2000:])
        self.assertEqual([f for f in res.view_files() if f.startswith("Local/")], [])

    def test_the_local_kinds_file_changes_nothing_for_a_page_with_no_assembly(self):
        doc = page()
        doc.pop("assemblies")
        res = self.build(doc, dev=None, local_kinds=[KIND])
        self.assertEqual(res.code, 0, res.text[-2000:])


if __name__ == "__main__":
    unittest.main()
