"""Tests of `tools/hmi/page_checks.py` (S11-C, WFB-182): coverage of the mapping rows, the navigation table walked, and
every value component on a tag. Synthetic names only; the real build is replayed outside the repository."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from hmi import page_checks  # noqa: E402


def dump(path: Path, doc) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8", newline="\n")
    return path


def screen(pid: str, route: str, **lists) -> dict:
    return {"schema": "cadre-hmi-screen/1", "screen": {"id": pid, "route": route, "title": pid}, **lists}


def world(d: Path) -> dict:
    """Two pages: a plant page with a pump (a device), a readout, a link to the other page, and a stub page."""
    page = screen(
        "Plant", "/plant",
        symbols=[{"id": "P1", "kind": "pump", "bind": {"on": "DEV1/state"}, "device": "DEV1"},
                 {"id": "R1", "kind": "readout", "bind": {"value": "src/level"}},
                 {"id": "M1", "kind": "motor", "bind": {"on": "DEV2/state"}, "faceplate": "DEV2"}],
        sections=[{"id": "lnk", "route": "/other"}],
        labels=[{"id": "T1", "text": "Level"}],
        trends=[{"id": "TR", "pens": [{"tag": "src/level"}]}])
    other = screen("Other", "/other", sections=[{"id": "S", "label": "Other"}])
    for pid, doc in (("Plant", page), ("Other", other)):
        dump(d / "descriptors" / f"{pid}.json", doc)
    tags = {"name": "cadre_hmi_x", "tagType": "Folder", "tags": [
        {"name": "src", "tagType": "Folder", "tags": [{"name": "level", "tagType": "AtomicTag"}]}]}
    devices = {"schema": "cadre-hmi-devices/1", "devices": [
        {"id": "DEV1", "members": {"state": {}, "ilk/permitted": {}}}, {"id": "DEV2", "members": {"state": {}}}]}
    return {"descriptors": d / "descriptors", "tags": dump(d / "tags.json", tags),
            "devices": dump(d / "devices.json", devices),
            "mapping": dump(d / "mapping.json", [
                {"uid": "Plant:a", "source": "Plant", "section": "devices", "label": "Pump"},
                {"uid": "Plant:b", "source": "Plant", "section": "readouts", "label": "Level"}]),
            "cover": dump(d / "cover.json", {"Plant:a": {"drawn": [{"kind": "symbol", "id": "P1"}]},
                                              "Plant:b": {"drawn": [{"kind": "symbol", "id": "R1"}]}}),
            "navtable": dump(d / "nav.json", {"schema": "wfb.migration.navtable/1", "entries": [
                {"id": "n1", "kind": "link", "target": "Other", "route": "/other"},
                {"id": "n2", "kind": "popup", "target": "FP_DEV1", "device": "DEV1"},
                {"id": "n3", "kind": "menu", "target": "Trend"}]}),
            "routes": dump(d / "routes.json", {"pages": {"Trend": "/trends"}, "faceplates": {},
                                               "library_routes": ["/trends"]})}


def run(d: Path, w: dict, *extra: str, nav: Path | None = None) -> tuple[int, dict]:
    out = d / "out"
    code = page_checks.main(["--descriptors", str(w["descriptors"]), "--devices", str(w["devices"]),
                             "--tags", str(w["tags"]), "--navtable", str(nav or w["navtable"]),
                             "--route-map", str(w["routes"]), "--mapping", str(w["mapping"]),
                             "--coverage-map", str(w["cover"]), "--project", "cadre_hmi_x", "--out", str(out), *extra])
    return code, json.loads((out / "checks.json").read_text(encoding="utf-8")) if (out / "checks.json").exists() else {}


class PageChecksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_a_complete_build_passes_every_check(self):
        w = world(self.d)
        code, doc = run(self.d, w)
        self.assertEqual(code, 0, doc)
        self.assertEqual(doc["schema"], "cadre-hmi-descriptor-coverage/1")
        self.assertEqual((doc["coverage"]["covered"], doc["coverage"]["rows"]), (2, 2))
        self.assertEqual((doc["navigation"]["resolved"], doc["navigation"]["total"]), (3, 3))
        self.assertEqual((doc["tags_bound"]["bound"], doc["tags_bound"]["value_components"]), (4, 4))

    def test_a_row_no_element_carries_is_missing_unless_a_gap_accepts_it(self):
        w = world(self.d)
        dump(w["cover"], {"Plant:a": {"drawn": [{"kind": "symbol", "id": "P1"}]}})
        code, doc = run(self.d, w)
        self.assertEqual(code, 2)
        self.assertEqual([m.split()[0] for m in doc["coverage"]["missing"]], ["Plant:b"])
        gaps = dump(self.d / "gaps.json", {"gaps": [{"id": "G1", "mapping_rows": ["Plant:b"]}]})
        code, doc = run(self.d, w, "--gaps", str(gaps))
        self.assertEqual(code, 0, doc["coverage"])

    def test_an_element_named_but_not_in_the_descriptor_is_missing(self):
        w = world(self.d)
        dump(w["cover"], {"Plant:a": {"drawn": [{"kind": "symbol", "id": "GONE"}]},
                          "Plant:b": {"drawn": [{"kind": "symbol", "id": "R1"}]}})
        code, doc = run(self.d, w)
        self.assertEqual(code, 2)
        self.assertEqual(len(doc["coverage"]["missing"]), 1)

    def test_a_target_with_no_route_or_a_route_that_is_no_page_is_unresolved(self):
        w = world(self.d)
        nav = dump(self.d / "nav2.json", [
            {"id": "a", "target": "Nowhere"},
            {"id": "b", "target": "Far", "route": "/far"},
            {"id": "c", "target": "FP_X", "device": "NO_SUCH"},
            {"id": "d", "target": "Orphan", "device": "DEV3"}])
        # DEV3 is not in the device model; DEV2's symbol opens it, so n2 below stays resolved
        code, doc = run(self.d, w, nav=nav)
        self.assertEqual(code, 2)
        reasons = {u["target"]: u["reason"] for u in doc["navigation"]["unresolved"]}
        self.assertEqual(set(reasons), {"Nowhere", "Far", "FP_X", "Orphan"})
        self.assertIn("no route and no device", reasons["Nowhere"])
        self.assertIn("is no page", reasons["Far"])
        self.assertIn("not in the device model", reasons["FP_X"])

    def test_a_device_no_symbol_opens_is_unresolved(self):
        w = world(self.d)
        devices = json.loads(Path(w["devices"]).read_text(encoding="utf-8"))
        devices["devices"].append({"id": "DEV9", "members": {"state": {}}})
        dump(w["devices"], devices)
        nav = dump(self.d / "nav3.json", [{"id": "a", "target": "FP9", "device": "DEV9"}])
        code, doc = run(self.d, w, nav=nav)
        self.assertEqual(code, 2)
        self.assertIn("opened by no symbol", doc["navigation"]["unresolved"][0]["reason"])

    def test_a_faceplate_key_opens_its_device(self):
        w = world(self.d)
        nav = dump(self.d / "nav4.json", [{"id": "a", "target": "FP2", "device": "DEV2"}])
        code, doc = run(self.d, w, nav=nav)
        self.assertEqual(code, 0, doc["navigation"])

    def test_a_carrier_element_must_carry_the_route(self):
        w = world(self.d)
        dump(w["cover"], {"Plant:a": {"drawn": [{"kind": "symbol", "id": "P1"}]},
                          "Plant:b": {"drawn": [{"kind": "symbol", "id": "R1"}]},
                          "Plant:l": {"drawn": [{"kind": "section", "id": "lnk"}]}})
        nav = dump(self.d / "nav5.json", [{"id": "a", "target": "Other", "route": "/other", "uid": "Plant:l"},
                                          {"id": "b", "target": "Trend", "route": "/trends", "uid": "Plant:l"}])
        code, doc = run(self.d, w, nav=nav)
        self.assertEqual(code, 2)
        self.assertEqual([u["target"] for u in doc["navigation"]["unresolved"]], ["Trend"])

    def test_a_component_with_no_tag_and_a_tag_that_does_not_exist_are_findings(self):
        w = world(self.d)
        page = json.loads((w["descriptors"] / "Plant.json").read_text(encoding="utf-8"))
        page["symbols"].append({"id": "BARE", "kind": "indicator"})
        page["symbols"].append({"id": "LOST", "kind": "indicator", "bind": {"state": "src/missing"}})
        dump(w["descriptors"] / "Plant.json", page)
        code, doc = run(self.d, w)
        self.assertEqual(code, 2)
        self.assertEqual(doc["tags_bound"]["unbound"], ["Plant:BARE"])
        self.assertEqual(doc["tags_bound"]["unresolved_tags"], ["Plant:LOST src/missing"])

    def test_a_cards_only_build_is_refused(self):
        # session 9's output: descriptors of rows of cards with no drawn element
        w = world(self.d)
        for f in w["descriptors"].glob("*.json"):
            f.unlink()
        dump(w["descriptors"] / "cards.json", {"schema": "cadre-hmi-screen/1", "rows": [[{"body": {}}]]})
        code, doc = run(self.d, w)
        self.assertEqual(code, 2)
        self.assertIn("a cards layout", doc["tags_bound"]["unbound"][0])

    def test_the_built_views_are_classified_as_the_exercise_did(self):
        w = world(self.d)
        built = self.d / "build" / "cadre_hmi_x" / "com.inductiveautomation.perspective"
        dump(built / "page-config" / "config.json", {"pages": {"/plant": {}, "/other": {}}})
        dump(built / "session-props" / "props.json", {"custom": {"devices": [{"folder": "[default]cadre_hmi_x/DEV1"},
                                                                              {"folder": "[default]cadre_hmi_x/DEV2"}]}})

        def view(children):
            return {"propConfig": {"custom.p": {"binding": {"type": "tag", "config": {"tagPath": "[default]x/a"}}}},
                    "root": {"type": "ia.container.coord", "children": children}}
        tagged = {"type": "cadre.ob.readout", "meta": {"name": "R"},
                  "propConfig": {"props.value": {"binding": {"type": "tag", "config": {"tagPath": "[default]x/a"}}}}}
        custom = {"type": "cadre.ob.motor", "meta": {"name": "M"},
                  "propConfig": {"props.on": {"binding": {"type": "expr", "config": {"expression": "{view.custom.p}"}}}}}
        zoom = {"type": "cadre.ob.canvaszoom", "meta": {"name": "Z"}}
        dump(built / "views" / "Screens" / "Plant" / "view.json", view([tagged, custom, zoom]))
        code, doc = run(self.d, w, "--built", str(self.d / "build"))
        self.assertEqual(code, 0, doc["tags_bound"])
        self.assertEqual(doc["tags_bound"]["view_classes"]["Plant | cadre.ob.readout | tag binding on the component"], 1)
        self.assertEqual(doc["tags_bound"]["view_classes"]["Plant | cadre.ob.motor | tag via view.custom"], 1)
        bare = {"type": "cadre.ob.pump", "meta": {"name": "BARE"}}
        dump(built / "views" / "Screens" / "Plant" / "view.json", view([tagged, bare]))
        code, doc = run(self.d, w, "--built", str(self.d / "build"))
        self.assertEqual(code, 2)
        self.assertEqual(doc["tags_bound"]["unbound"], ["Plant:BARE (cadre.ob.pump)"])
        # a route the page configuration lacks
        dump(built / "page-config" / "config.json", {"pages": {"/plant": {}}})
        code, doc = run(self.d, w, "--built", str(self.d / "build"))
        self.assertIn("no page of the built project", json.dumps(doc["navigation"]))

    def test_the_route_of_an_entry_is_the_designs_decision_joined_on_the_entry_id(self):
        # block 12's entries carry no route; block 18's `routes` table decides it (treatment page, support, faceplate)
        w = world(self.d)
        nav = dump(self.d / "nav6.json", {"format": "wfb.migration.navtable/1", "entries": [
            {"id": "menu:a", "kind": "menu", "target": "Other"},
            {"id": "menu:b", "kind": "menu", "target": "Trend"},
            {"id": "popup:c", "kind": "popup", "target": "FP_DEV1"},
            {"id": "menu:d", "kind": "menu", "target": "Orphan"}]})
        design = dump(self.d / "design.json", {"routes": [
            {"target": "menu:a", "treatment": "page", "route": "/other"},
            {"target": "menu:b", "treatment": "support", "route": "/trends"},
            {"target": "popup:c", "treatment": "faceplate", "device": "DEV1", "tab": "home"}]})
        code, doc = run(self.d, w, "--design", str(design), nav=nav)
        self.assertEqual(code, 2)
        self.assertEqual((doc["navigation"]["resolved"], doc["navigation"]["total"]), (3, 4))
        self.assertEqual([u["target"] for u in doc["navigation"]["unresolved"]], ["Orphan"])
        self.assertIn("the design has no route", doc["navigation"]["unresolved"][0]["reason"])

    def test_a_shared_popup_entry_resolves_by_the_device_it_names(self):
        # one pop-up window opened per device by an argument: the entries share a target, each names its device
        w = world(self.d)
        nav = dump(self.d / "nav7.json", {"entries": [
            {"id": "popup:p1:a", "kind": "popup", "target": "SHARED", "device": "DEV1"},
            {"id": "popup:p2:a", "kind": "popup", "target": "SHARED", "device": "DEV2"},
            {"id": "popup:p3:a", "kind": "popup", "target": "SHARED", "device": "NO_SUCH"},
            {"id": "popup:p4:a", "kind": "popup", "target": "SHARED"}]})
        code, doc = run(self.d, w, nav=nav)
        self.assertEqual(code, 2)
        reasons = {u["reason"] for u in doc["navigation"]["unresolved"]}
        self.assertEqual((doc["navigation"]["resolved"], doc["navigation"]["total"]), (2, 4))
        self.assertTrue(any("NO_SUCH is not in the device model" in r for r in reasons))
        self.assertTrue(any("no route and no device" in r for r in reasons))   # without a device: today's rule

    def test_a_missing_input_is_a_fault(self):
        w = world(self.d)
        w["tags"].unlink()
        code, _ = run(self.d, w)
        self.assertEqual(code, 1)


CANVAS = (1000, 600)


def drawn(**over) -> dict:
    """A diagram page that satisfies every layout rule at the canvas 1000x600: a pump, a vertical switch, two readouts
    of one column and one width, a pipe and a dashed interlock line, drawn over the whole canvas."""
    page = screen(
        "Fit", "/fit",
        symbols=[{"id": "P1", "kind": "pump", "x": 40, "y": 60, "w": 80, "h": 80, "params": {"readoutPosition": "right"}},
                 {"id": "S1", "kind": "switch", "x": 300, "y": 60, "w": 40, "h": 80,
                  "params": {"vertical": False, "readoutPosition": "bottom"}},
                 {"id": "R1", "kind": "readout", "x": 700, "y": 100, "w": 120, "params": {"stretch": True}},
                 {"id": "R2", "kind": "readout", "x": 702, "y": 200, "w": 120, "params": {"stretch": True}}],
        pipes=[{"id": "L1", "from": {"ref": "P1", "side": "right"}, "to": {"ref": "S1", "side": "left"}}],
        lines=[{"id": "I1", "points": [[130, 100], [290, 100]], "style": "dashed"}],
        labels=[{"id": "T1", "x": 780, "y": 520, "w": 190, "h": 40, "text": "Footer"}])
    page["screen"].update({"layout": "diagram", "width": 1000, "height": 600})
    page["toolbar"] = True
    for key, value in over.items():
        if key == "screen":
            page["screen"].update(value)
        elif value is None:
            page.pop(key, None)
        else:
            page[key] = value
    return page


def layout(page: dict, require_stretch: bool = True) -> list[dict]:
    return page_checks.check_layout({"Fit": page}, *CANVAS, require_stretch)["findings"]


def rules(findings: list[dict]) -> list[str]:
    return sorted(f["rule"] for f in findings)


class LayoutChecksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_a_page_that_follows_every_rule_has_no_finding(self):
        self.assertEqual(layout(drawn()), [])

    def test_a_finding_names_its_page_rule_element_and_a_reason(self):
        found = layout(drawn(toolbar=False))
        self.assertEqual(len(found), 1)
        self.assertEqual(set(found[0]), {"page", "rule", "id", "reason"})
        self.assertEqual((found[0]["page"], found[0]["rule"]), ("Fit", "L8"))
        self.assertTrue(found[0]["reason"].endswith("."))

    def test_l1_a_page_larger_than_the_canvas_shrinks_and_is_a_finding(self):
        self.assertEqual(layout(drawn(screen={"width": 1000, "height": 600})), [])
        wide = [{"id": "T1", "x": 1000, "y": 520, "w": 190, "h": 40, "text": "Footer"}]
        tall = [{"id": "T1", "x": 780, "y": 600, "w": 190, "h": 90, "text": "Footer"}]
        self.assertEqual(rules(layout(drawn(screen={"width": 1200}, labels=wide))), ["L1"])
        self.assertEqual(rules(layout(drawn(screen={"height": 700}, labels=tall))), ["L1"])

    def test_l2_a_page_smaller_than_95_percent_of_the_canvas_is_a_finding(self):
        self.assertEqual(layout(drawn(screen={"width": 950, "height": 570})), [])
        self.assertEqual(rules(layout(drawn(screen={"width": 940}))), ["L2"])
        self.assertEqual(rules(layout(drawn(screen={"height": 560}))), ["L2"])

    def test_l2_elements_must_reach_90_percent_of_the_width_and_85_percent_of_the_height(self):
        page = drawn(labels=[{"id": "T1", "x": 780, "y": 520, "w": 100, "h": 40, "text": "Footer"}])   # right edge 880
        self.assertEqual(rules(layout(page)), ["L2"])
        self.assertIn("width", layout(page)[0]["reason"])
        page = drawn(labels=[{"id": "T1", "x": 780, "y": 400, "w": 190, "h": 40, "text": "Footer"}])   # bottom 440
        self.assertEqual(rules(layout(page)), ["L2"])
        self.assertIn("height", layout(page)[0]["reason"])
        self.assertEqual(page_checks.LAYOUT_FILL_X, 0.90)
        self.assertEqual(page_checks.LAYOUT_FILL_Y, 0.85)

    def test_l2_the_extent_counts_pipe_points_line_points_junctions_brackets_and_links(self):
        self.assertEqual(rules(layout(drawn(labels=[]))), ["L2"])     # nothing reaches the right or the bottom edge
        far = [[960, 570]]
        for key, items in (("junctions", [{"id": "J", "x": 950, "y": 560}]),
                           ("lines", [{"id": "I1", "points": [[130, 100], *far], "style": "dashed"}]),
                           ("pipes", [{"id": "L1", "from": {"x": 10, "y": 10, "end": "arrow-in"},
                                       "to": {"x": 10, "y": 20, "end": "arrow-out"}, "via": [[960, 20], *far]}]),
                           ("pipes", [{"id": "L1", "from": {"x": 10, "y": 10, "end": "arrow-in"},
                                       "to": {"x": 960, "y": 570, "end": "arrow-out"}}]),
                           ("buttons", [{"id": "B", "x": 800, "y": 520, "w": 150, "h": 40, "label": "B",
                                         "action": {"type": "route", "route": "/x"}}]),
                           ("links", [{"id": "K", "x": 900, "y": 520, "w": 60, "h": 40, "route": "/x"}]),
                           ("sections", [{"id": "S", "x": 10, "y": 10, "w": 940, "h": 560}])):
            self.assertEqual(layout(drawn(labels=[], **{key: items})), [], key)
        page = drawn(labels=[], brackets=[{"id": "BR", "x": 700, "y": 520, "w": 250, "label": "G"}],
                     junctions=[{"id": "J", "x": 10, "y": 570}])
        self.assertEqual(layout(page), [])       # a bracket runs x to x + w

    def test_l3_a_free_solid_line_is_a_finding_a_dashed_or_gated_line_is_not(self):
        self.assertEqual(layout(drawn(lines=[{"id": "I1", "points": [[0, 0], [1, 1]], "style": "dashed"},
                                             {"id": "I2", "points": [[0, 0], [1, 1]], "gate": {"tag": "a/b"}}])), [])
        found = layout(drawn(lines=[{"id": "F1", "points": [[0, 0], [1, 1]]},
                                    {"id": "F2", "points": [[0, 0], [1, 1]], "style": "solid"}]))
        self.assertEqual(rules(found), ["L3", "L3"])
        self.assertEqual(sorted(f["id"] for f in found), ["F1", "F2"])
        self.assertIn("pipe", found[0]["reason"])

    def test_l4_readouts_of_one_column_share_one_width(self):
        self.assertEqual(layout(drawn()), [])
        page = drawn()
        page["symbols"][3]["w"] = 90                       # x 700 and 702 are one column with two widths
        found = layout(page)
        self.assertEqual(rules(found), ["L4"])
        self.assertIn("R1", found[0]["id"])
        far = drawn()
        far["symbols"][3].update({"x": 720, "w": 90})      # 18 px apart: two columns
        self.assertEqual(layout(far), [])

    def test_l4_the_columns_key_has_one_row_for_each_column(self):
        page = drawn()
        page["symbols"][3]["w"] = 90
        page["symbols"].append({"id": "R3", "kind": "readout", "x": 100, "y": 300, "w": 50, "params": {"stretch": True}})
        page["symbols"].append({"id": "R4", "kind": "readout", "x": 100, "y": 340, "w": 50, "params": {"stretch": True}})
        cols = page_checks.check_layout({"Fit": page}, *CANVAS, True)["columns"]
        self.assertEqual(sorted((c["x"], c["widths"], c["ok"]) for c in cols), [(100, [50], True), (700, [90, 120], False)])
        self.assertTrue(all(c["page"] == "Fit" for c in cols))

    def test_l5_with_require_stretch_every_readout_has_stretch_true(self):
        page = drawn()
        del page["symbols"][2]["params"]["stretch"]
        page["symbols"][3]["params"]["stretch"] = False
        found = layout(page)
        self.assertEqual((rules(found), sorted(f["id"] for f in found)), (["L5", "L5"], ["R1", "R2"]))
        self.assertEqual(layout(page, require_stretch=False), [])

    def test_l6_a_switch_states_whether_it_is_vertical(self):
        page = drawn()
        del page["symbols"][1]["params"]["vertical"]
        found = layout(page)
        self.assertEqual((rules(found), found[0]["id"]), (["L6"], "S1"))
        page["symbols"][1]["params"]["vertical"] = False          # false is a statement
        self.assertEqual(layout(page), [])

    def test_l7_a_device_symbol_states_where_its_status_is_read(self):
        kinds = ["motor", "pump", "fan", "valve", "switch", "generator", "indicator"]
        page = drawn()
        page["symbols"] = [s for s in page["symbols"] if s["kind"] == "readout"] + [
            {"id": f"X{i}", "kind": k, "x": 10 + 100 * i, "y": 10, "w": 40, "h": 40,
             "params": {"vertical": True}} for i, k in enumerate(kinds)]
        found = layout(page)
        self.assertEqual(sorted(f["id"] for f in found if f["rule"] == "L7"), sorted(f"X{i}" for i in range(7)))
        for s in page["symbols"][2:]:
            s["params"]["readoutPosition"] = "none"
        self.assertEqual([f for f in layout(page) if f["rule"] == "L7"], [])
        page["symbols"].append({"id": "T", "kind": "tank", "x": 5, "y": 5})     # a tank states no position
        self.assertEqual([f for f in layout(page) if f["rule"] == "L7"], [])

    def test_l7_a_generator_drawn_as_a_picture_writes_its_own_status(self):
        page = drawn()
        page["symbols"].append({"id": "GS", "kind": "generator", "x": 5, "y": 5, "w": 440, "h": 275,
                                "params": {"picture": "genset"}})
        self.assertEqual([f for f in layout(page) if f["rule"] == "L7"], [])
        page["symbols"][-1]["params"] = {}
        self.assertEqual([f["id"] for f in layout(page) if f["rule"] == "L7"], ["GS"])

    def test_l8_the_toolbar_must_not_be_switched_off(self):
        self.assertEqual(layout(drawn(toolbar=None)), [])
        self.assertEqual(rules(layout(drawn(toolbar=False))), ["L8"])

    def test_stub_pages_and_other_layouts_are_skipped(self):
        stub = screen("Stub", "/stub", sections=[{"id": "S", "label": "x"}])
        cards = drawn(screen={"layout": "cards"})
        out = page_checks.check_layout({"Stub": stub, "Cards": cards, "Fit": drawn()}, *CANVAS, True)
        self.assertEqual((out["pages"], out["findings"]), (1, []))
        bare = drawn()
        del bare["screen"]["layout"]               # an absent layout is a diagram
        bare["toolbar"] = False
        self.assertEqual(rules(layout(bare)), ["L8"])

    def test_a_page_without_width_and_height_is_a_finding(self):
        page = drawn()
        del page["screen"]["width"]
        self.assertEqual(rules(layout(page)), ["L1"])

    def test_without_canvas_the_tool_behaves_as_before(self):
        w = world(self.d)
        code, doc = run(self.d, w, "--require-stretch")
        self.assertEqual(code, 0, doc)
        self.assertIsNone(doc["layout"])
        self.assertEqual(doc["columns"], [])

    def test_a_layout_finding_makes_the_exit_code_2_and_is_listed_in_checks_json(self):
        w = world(self.d)
        code, doc = run(self.d, w, "--canvas", "1000x600")       # the plant page states no size, no positions
        self.assertEqual(code, 2)
        lay = doc["layout"]
        self.assertEqual((lay["canvas"], lay["pages"]), ("1000x600", 1))      # the stub page is skipped
        self.assertEqual(lay["count"], len(lay["findings"]))
        self.assertTrue({"L1", "L7"} <= {f["rule"] for f in lay["findings"]})
        self.assertEqual(doc["coverage"]["missing"], [])           # nothing else failed

    def test_a_clean_page_set_with_canvas_exits_0(self):
        w = world(self.d)
        good = drawn()
        good["screen"].update({"id": "Plant", "route": "/plant"})
        good["symbols"][0].update({"bind": {"on": "DEV1/state"}, "device": "DEV1"})
        good["symbols"][1].update({"bind": {"on": "DEV2/state"}, "faceplate": "DEV2"})
        good["symbols"][2].update({"bind": {"value": "src/level"}})
        good["symbols"].pop(3)
        good["sections"] = [{"id": "lnk", "x": 0, "y": 0, "w": 5, "h": 5, "route": "/other"}]
        good["trends"] = [{"id": "TR", "x": 400, "y": 300, "w": 100, "h": 100, "pens": [{"tag": "src/level"}]}]
        dump(w["descriptors"] / "Plant.json", good)
        code, doc = run(self.d, w, "--canvas", "1000x600", "--require-stretch")
        self.assertEqual((code, doc["layout"]["count"]), (0, 0), doc["layout"])

    def test_the_findings_are_bounded_but_counted_and_the_summary_names_the_family(self):
        w = world(self.d)
        page = drawn()
        page["lines"] = [{"id": f"F{i}", "points": [[0, 0], [1, 1]]} for i in range(page_checks.MAX_LISTED + 5)]
        page["screen"].update({"id": "Plant", "route": "/plant"})
        dump(w["descriptors"] / "Plant.json", page)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code, doc = run(self.d, w, "--canvas", "1000x600")
        self.assertEqual(code, 2)
        self.assertEqual(len(doc["layout"]["findings"]), page_checks.MAX_LISTED)
        self.assertEqual(doc["layout"]["count"], page_checks.MAX_LISTED + 5)
        self.assertIn(f"layout {page_checks.MAX_LISTED + 5} findings", buf.getvalue().splitlines()[0])
        self.assertIn("layout Plant L3", buf.getvalue())

    def test_a_malformed_canvas_is_a_fault(self):
        w = world(self.d)
        for bad in ("1900", "axb", "0x0", "1900x"):
            code, _ = run(self.d, w, "--canvas", bad)
            self.assertEqual(code, 1, bad)


def lay2(page: dict, inventory: dict | None = None) -> list[dict]:
    return page_checks.check_layout({"Fit": page}, *CANVAS, True, inventory)["findings"]


def of(findings: list[dict], rule: str) -> list[dict]:
    return [f for f in findings if f["rule"] == rule]


def lab(ident: str, text: str, x: float, y: float, w: float = 190, h: float = 24, **more) -> dict:
    return {"id": ident, "x": x, "y": y, "w": w, "h": h, "text": text, **more}


def switch_page(sides=("left", "right"), vertical=False, position="none", ypos=100, xpos=100) -> dict:
    """A page with one switch SW at (200, 100) box 48 and two junctions wired to the sides given."""
    page = drawn(symbols=[
        {"id": "SW", "kind": "switch", "x": 200, "y": 100, "w": 48, "h": 48,
         "params": {"vertical": vertical, "readoutPosition": position}},
        {"id": "R1", "kind": "readout", "x": 700, "y": 100, "w": 120, "params": {"stretch": True}}],
        pipes=[], lines=[])
    at = {"left": (100, 124), "right": (400, 124), "top": (224, 20), "bottom": (224, 300)}
    page["junctions"] = [{"id": f"J{i}", "x": at[s][0], "y": at[s][1]} for i, s in enumerate(sides)]
    page["pipes"] = [{"id": f"P{i}", "from": {"ref": f"J{i}"}, "to": {"ref": "SW", "side": s}}
                     for i, s in enumerate(sides)]
    return page


class AlignmentTests(unittest.TestCase):
    @staticmethod
    def pair(dx=0, dy=0, a="right", b="left", via=None) -> dict:
        """Two motors, M1 at (100, 100) and M2 at (400 + dx, 100 + dy) (or stacked for top and bottom), one pipe."""
        page = switch_page(())
        stacked = a in ("top", "bottom")
        page["symbols"] = [
            {"id": "M1", "kind": "motor", "x": 100, "y": 100, "w": 48, "h": 48, "params": {"readoutPosition": "none"}},
            {"id": "M2", "kind": "motor", "x": 100 + dx if stacked else 400 + dx, "y": 300 + dy if stacked else 100 + dy,
             "w": 48, "h": 48, "params": {"readoutPosition": "none"}},
            page["symbols"][1]]
        page["pipes"] = [{"id": "P0", "from": {"ref": "M1", "side": a}, "to": {"ref": "M2", "side": b},
                          **({"via": via} if via else {})}]
        return page

    def test_l12_a_loose_pipe_end_carries_its_arrow(self):
        page = drawn()
        page["pipes"] += [{"id": "IN", "from": {"x": 60, "y": 20, "end": "arrow-in"}, "to": {"ref": "P1", "side": "top"}},
                          {"id": "OUT", "from": {"ref": "S1", "side": "right"}, "to": {"x": 600, "y": 100, "end": "arrow-out"}}]
        self.assertEqual(of(lay2(page), "L12"), [])
        page["pipes"][-1]["to"]["end"] = "cap"
        page["pipes"][-2]["from"].pop("end")
        self.assertEqual(sorted(f["id"] for f in of(lay2(page), "L12")), ["IN", "OUT"])

    def test_l12_a_feeder_ends_in_an_arrow_above_its_motor(self):
        page = drawn()
        page["symbols"].append({"id": "M9", "kind": "motor", "x": 400, "y": 400, "w": 48, "h": 48,
                                "params": {"readoutPosition": "bottom"}})
        page["pipes"].append({"id": "F9", "from": {"ref": "S1", "side": "bottom"}, "to": {"ref": "M9", "side": "top"}})
        self.assertEqual([f["id"] for f in of(lay2(page), "L12")], ["F9"])
        page["pipes"][-1]["medium"] = "waste"                  # a process flow through a machine is no feeder
        self.assertEqual(of(lay2(page), "L12"), [])
        page["pipes"][-1] = {"id": "F9", "from": {"ref": "S1", "side": "bottom"},
                             "to": {"x": 424, "y": 392, "end": "arrow-out"}}
        self.assertEqual(of(lay2(page), "L12"), [])

    def test_l9a_two_symbols_on_one_axis_are_joined_on_that_axis(self):
        self.assertEqual(of(lay2(self.pair()), "L9"), [])
        found = of(lay2(self.pair(dy=10)), "L9")             # the router would jog 10 px between them
        self.assertEqual(sorted(f["id"] for f in found), ["M1", "M2"])
        self.assertIn("P0", found[0]["reason"])
        self.assertEqual(of(lay2(self.pair(dy=2)), "L9"), [])        # within the tolerance
        self.assertEqual(len(of(lay2(self.pair(dx=6, a="bottom", b="top")), "L9")), 2)
        self.assertEqual(of(lay2(self.pair(a="bottom", b="top")), "L9"), [])

    def test_l9a_a_pipe_that_turns_at_a_junction_or_a_loose_end_is_the_routers_corner(self):
        page = switch_page(("left",))
        page["junctions"][0]["y"] = 160                    # an L: the pipe leaves along the axis and turns
        self.assertEqual(of(lay2(page), "L9"), [])
        page["pipes"] = [{"id": "P0", "from": {"x": 100, "y": 140}, "to": {"ref": "SW", "side": "left"}}]
        self.assertEqual(of(lay2(page), "L9"), [])
        mixed = self.pair(dx=0, dy=100, a="right", b="top")   # horizontal to vertical: an L
        self.assertEqual(of(lay2(mixed), "L9"), [])

    def test_l9a_a_via_point_is_reached_along_x_first(self):
        # a vertical side leaves sideways when the first via point is off its x; a horizontal side is entered upright
        self.assertEqual(of(lay2(self.pair(a="bottom", b="top", via=[[124, 220]])), "L9"), [])
        off = of(lay2(self.pair(a="bottom", b="top", via=[[160, 220]])), "L9")
        self.assertEqual([f["id"] for f in off], ["M1"])
        self.assertEqual(of(lay2(self.pair(a="right", b="left", via=[[250, 124]])), "L9"), [])    # on the axis both ways
        entered = of(lay2(self.pair(a="right", b="left", via=[[250, 160]])), "L9")
        self.assertEqual([f["id"] for f in entered], ["M2"])          # the last point is off the axis of the way in

    def test_l9b_the_orientation_follows_the_sides_of_the_pipe_ends(self):
        self.assertEqual(of(lay2(switch_page(("top", "bottom"), vertical=True)), "L9"), [])
        wrong = lay2(switch_page(("top", "bottom"), vertical=False))
        self.assertEqual([f["id"] for f in of(wrong, "L9")], ["SW"])
        self.assertIn("vertical", of(wrong, "L9")[0]["reason"])
        self.assertEqual(len(of(lay2(switch_page(("left", "right"), vertical=True)), "L9")), 1)
        mixed = switch_page(("left", "top"), vertical=False)
        mixed["junctions"][1].update({"x": 224, "y": 20})
        self.assertTrue(any("mixed" in f["reason"] or "both" in f["reason"] for f in of(lay2(mixed), "L9")))

    def test_l9b_applies_to_any_symbol_with_a_vertical_param(self):
        page = switch_page(("top", "bottom"), vertical=False)
        page["symbols"][0].update({"kind": "fan", "params": {"vertical": False, "readoutPosition": "none"}})
        self.assertEqual(len(of(lay2(page), "L9")), 1)
        del page["symbols"][0]["params"]["vertical"]          # no vertical param: nothing to compare
        self.assertEqual(of(lay2(page), "L9"), [])

    def test_l9c_an_in_line_switch_states_readout_position_none(self):
        self.assertEqual(of(lay2(switch_page(position="none")), "L9"), [])
        bad = lay2(switch_page(position="top"))
        self.assertEqual([f["id"] for f in of(bad, "L9")], ["SW"])
        self.assertIn("readoutPosition", of(bad, "L9")[0]["reason"])
        self.assertEqual(len(of(lay2(switch_page(("top", "bottom"), vertical=True, position="left")), "L9")), 1)
        # a switch at the end of a line (one pipe end) is not in line
        self.assertEqual(of(lay2(switch_page(("left",), position="right")), "L9"), [])
        self.assertIn("switch", page_checks.INLINE_VIEW_KINDS)


class TextFitTests(unittest.TestCase):
    def test_l10a_a_label_fits_its_box_by_the_character_estimate(self):
        self.assertEqual(page_checks.CHAR_PX, 6.0)
        ok = drawn(labels=[lab("T1", "x" * 31, 780, 520, 190)])          # 31 x 6 = 186 <= 194
        self.assertEqual(of(lay2(ok), "L10"), [])
        long = drawn(labels=[lab("T1", "x" * 33, 780, 520, 190)])        # 198 > 194
        found = of(lay2(long), "L10")
        self.assertEqual([f["id"] for f in found], ["T1"])
        self.assertIn("wider", found[0]["reason"])

    def test_l10a_a_taller_box_allows_the_text_across_lines_and_the_font_size_scales_it(self):
        tall = drawn(labels=[lab("T1", "x" * 40, 780, 500, 190, 40)])    # 240 over 194: two lines of 21 px fit
        self.assertEqual(of(lay2(tall), "L10"), [])
        three = drawn(labels=[lab("T1", "x" * 70, 780, 500, 190, 40)])   # 420 needs three lines
        self.assertEqual(len(of(lay2(three), "L10")), 1)
        body = drawn(labels=[lab("T1", "x" * 20, 780, 520, 190, style="body")])   # 16 px font: 8 px a character
        self.assertEqual(len(of(lay2(body), "L10")), 0)
        body = drawn(labels=[lab("T1", "x" * 25, 780, 520, 190, style="body")])   # 200 > 194
        self.assertEqual(len(of(lay2(body), "L10")), 1)
        heading = drawn(labels=[lab("T1", "x" * 17, 780, 500, 190, 40, style="heading")])   # 24 px: 12 px a character
        self.assertEqual(len(of(lay2(heading), "L10")), 1)

    def test_l10a_a_symbol_title_fits_the_width_of_the_symbol(self):
        page = drawn()
        page["symbols"].append({"id": "Q1", "kind": "sequence", "x": 100, "y": 300, "w": 144, "h": 72,
                                "params": {"label": "x" * 24, "hasTag": False}})
        self.assertEqual(of(lay2(page), "L10"), [])
        page["symbols"][-1]["params"]["label"] = "x" * 25
        found = of(lay2(page), "L10")
        self.assertEqual([f["id"] for f in found], ["Q1"])
        page["symbols"][-1].update({"kind": "instrument-field", "w": 96, "h": 64})
        self.assertEqual(len(of(lay2(page), "L10")), 1)
        page["symbols"][-1].update({"kind": "motor"})            # a motor draws no such title
        self.assertEqual(of(lay2(page), "L10"), [])

    def test_l10b_two_labels_must_not_overlap(self):
        a = lab("A", "x" * 15, 100, 300, 100)
        apart = lab("B", "y" * 15, 210, 300, 100)
        self.assertEqual(of(lay2(drawn(labels=[*drawn()["labels"], a, apart])), "L10"), [])
        over = lab("B", "y" * 15, 150, 310, 100)                # texts of 90 px at x 100 and 150: 40 px across, 14 down
        found = of(lay2(drawn(labels=[*drawn()["labels"], a, over])), "L10")
        self.assertEqual(found[0]["id"], "A, B")
        touching = lab("B", "y" * 15, 189, 300, 100)            # the texts share 1 px: within the 2 px tolerance
        self.assertEqual(of(lay2(drawn(labels=[*drawn()["labels"], a, touching])), "L10"), [])

    def test_l10b_text_that_overflows_its_box_is_measured_at_its_estimated_width(self):
        a = lab("A", "x" * 30, 100, 300, 60)                     # 180 px of text from x 100 (left aligned)
        b = lab("B", "other", 200, 300, 60)
        found = of(lay2(drawn(labels=[*drawn()["labels"], a, b])), "L10")
        self.assertTrue(any(f["id"] == "A, B" for f in found))

    def test_l10b_a_label_is_measured_at_the_width_of_its_text_not_of_its_box(self):
        near = [lab("A", "ab", 100, 300, 100), lab("B", "cd", 150, 300, 100)]      # the boxes overlap, the texts do not
        self.assertEqual(of(lay2(drawn(labels=[*drawn()["labels"], *near])), "L10"), [])
        right = [lab("A", "x" * 15, 100, 300, 200, align="right"), lab("B", "y" * 15, 120, 300, 100)]   # A's text 210..300
        self.assertEqual(of(lay2(drawn(labels=[*drawn()["labels"], *right])), "L10"), [])

    def test_l10b_a_label_against_a_symbol_box(self):
        page = drawn(labels=[*drawn()["labels"], lab("A", "text", 30, 70, 100)])      # over the pump at 40..120, 60..140
        found = of(lay2(page), "L10")
        self.assertEqual([f["id"] for f in found], ["A, P1"])
        clear = drawn(labels=[*drawn()["labels"], lab("A", "text", 30, 20, 100)])
        self.assertEqual(of(lay2(clear), "L10"), [])

    def test_l10b_the_title_band_of_a_section_is_kept_clear(self):
        outer = {"id": "outer", "x": 20, "y": 20, "w": 900, "h": 500, "label": "Outer title"}    # band x 838..920, y 20..44
        base = drawn(sections=[outer])
        self.assertEqual(of(lay2(base), "L10"), [])
        under = drawn(sections=[outer], labels=[*drawn()["labels"], lab("A", "x" * 10, 800, 30, 100)])
        self.assertEqual([f["id"] for f in of(lay2(under), "L10")], ["A, outer"])
        inside = drawn(sections=[outer], labels=[*drawn()["labels"], lab("A", "text", 800, 60, 100)])
        self.assertEqual(of(lay2(inside), "L10"), [])        # inside its own section, below the band

    def test_l10b_a_nested_section_must_not_cover_its_parents_title_band(self):
        outer = {"id": "outer", "x": 20, "y": 20, "w": 900, "h": 500, "label": "Outer title"}
        covering = {"id": "inner", "x": 700, "y": 30, "w": 200, "h": 200, "label": "Inner"}
        found = of(lay2(drawn(sections=[outer, covering])), "L10")
        self.assertIn("inner, outer", [f["id"] for f in found])
        below = {"id": "inner", "x": 700, "y": 60, "w": 200, "h": 200, "label": "Inner"}
        self.assertEqual(of(lay2(drawn(sections=[outer, below])), "L10"), [])
        beside = {"id": "inner", "x": 100, "y": 30, "w": 200, "h": 200, "label": "Inner"}
        self.assertEqual(of(lay2(drawn(sections=[outer, beside])), "L10"), [])
        unlabelled = {"id": "outer", "x": 20, "y": 20, "w": 900, "h": 500}
        self.assertEqual(of(lay2(drawn(sections=[unlabelled, covering])), "L10"), [])


class LabelOrderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    @staticmethod
    def inv(*texts) -> dict:
        """The original's text objects of one page: (text, x, y, w, h)."""
        return {"Fit": [{"class": "Text", "text": t, "x": x, "y": y, "w": w, "h": h} for t, x, y, w, h in texts]}

    @staticmethod
    def page(*labels) -> dict:
        return drawn(labels=[*drawn()["labels"], *[lab(i, t, x, y, 100) for i, t, x, y in labels]])

    def test_l11_a_column_of_the_original_keeps_its_order(self):
        inventory = self.inv(("3 PHASE\nSUPPLY", 613, 227, 60, 26), ("VALVE ONE", 605, 376, 60, 13))
        good = self.page(("A", "3 phase supply", 500, 300), ("B", "valve one", 510, 400))
        self.assertEqual(of(lay2(good, inventory), "L11"), [])
        bad = self.page(("A", "3 PHASE SUPPLY", 500, 444), ("B", "VALVE ONE", 510, 374))
        found = of(lay2(bad, inventory), "L11")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["id"], "A, B")
        self.assertIn("original", found[0]["reason"])

    def test_l11_a_row_of_the_original_keeps_its_order(self):
        inventory = self.inv(("LEFT TEXT", 100, 300, 50, 13), ("RIGHT TEXT", 300, 304, 50, 13))
        self.assertEqual(of(lay2(self.page(("A", "left text", 400, 300), ("B", "right text", 600, 300)), inventory), "L11"), [])
        found = of(lay2(self.page(("A", "left text", 600, 300), ("B", "right text", 400, 300)), inventory), "L11")
        self.assertEqual(len(found), 1)

    def test_l11_equal_built_positions_unrelated_pairs_and_far_pairs_are_no_finding(self):
        column = self.inv(("TOP", 100, 100, 50, 13), ("BOTTOM", 105, 200, 50, 13))
        same_row = self.page(("A", "top", 300, 300), ("B", "bottom", 450, 304))     # a column laid out as a row
        self.assertEqual(of(lay2(same_row, column), "L11"), [])
        near = self.inv(("TOP", 100, 100, 50, 13), ("BOTTOM", 105, 104, 50, 13))      # 4 px: under the 8 px floor
        self.assertEqual(of(lay2(self.page(("A", "top", 300, 400), ("B", "bottom", 300, 300)), near), "L11"), [])
        far = self.inv(("TOP", 100, 100, 50, 13), ("BOTTOM", 105, 100 + page_checks.ORDER_SPAN_Y + 1, 50, 13))
        self.assertEqual(of(lay2(self.page(("A", "top", 300, 400), ("B", "bottom", 300, 300)), far), "L11"), [])
        apart = self.inv(("TOP", 100, 100, 50, 13), ("BOTTOM", 400, 200, 50, 13))     # x ranges do not overlap
        self.assertEqual(of(lay2(self.page(("A", "top", 300, 400), ("B", "bottom", 300, 300)), apart), "L11"), [])
        self.assertEqual((page_checks.ORDER_SPAN_Y, page_checks.ORDER_SPAN_X), (200, 300))

    def test_l11_a_text_that_appears_twice_or_not_at_all_is_skipped(self):
        inventory = self.inv(("TOP", 100, 100, 50, 13), ("DUP", 105, 200, 50, 13), ("DUP", 105, 300, 50, 13))
        swapped = self.page(("A", "top", 300, 400), ("B", "dup", 300, 300), ("C", "only here", 300, 350))
        self.assertEqual(of(lay2(swapped, inventory), "L11"), [])
        twice_built = self.page(("A", "top", 300, 400), ("B", "x", 300, 300), ("C", "x", 300, 350))
        self.assertEqual(of(lay2(twice_built, self.inv(("TOP", 100, 100, 50, 13), ("X", 105, 200, 50, 13))), "L11"), [])

    def test_l11_needs_an_inventory_for_the_page(self):
        swapped = self.page(("A", "top", 300, 400), ("B", "bottom", 300, 300))
        self.assertEqual(of(lay2(swapped, None), "L11"), [])
        self.assertEqual(of(lay2(swapped, {"Other": []}), "L11"), [])

    def test_the_inventory_is_read_from_either_layout(self):
        objs = [{"class": "Text", "text": "A\nB", "x": 1, "y": 2, "w": 3, "h": 4},
                {"class": "Line", "x": 0, "y": 0, "w": 1, "h": 1},
                {"class": "Text", "text": "", "x": 0, "y": 0, "w": 1, "h": 1}]
        dump(self.d / "inv1" / "Fit" / "inventory.json", {"objects": objs})
        dump(self.d / "inv2" / "Fit.json", {"objects": objs})
        for name in ("inv1", "inv2"):
            got = page_checks.read_inventory(self.d / name, ["Fit", "Missing"])
            self.assertEqual(list(got), ["Fit"], name)
            self.assertEqual([o["text"] for o in got["Fit"]], ["A\nB"], name)
        with self.assertRaises(page_checks.Fault):
            page_checks.read_inventory(self.d / "nothing", ["Fit"])

    def test_the_command_line_refuses_a_swapped_pair_with_exit_code_2(self):
        w = world(self.d)
        good = drawn()
        good["screen"].update({"id": "Plant", "route": "/plant"})
        good["symbols"][0].update({"bind": {"on": "DEV1/state"}, "device": "DEV1"})
        good["symbols"][1].update({"bind": {"on": "DEV2/state"}, "faceplate": "DEV2"})
        good["symbols"][2].update({"bind": {"value": "src/level"}})
        good["symbols"].pop(3)
        good["sections"] = [{"id": "lnk", "x": 0, "y": 0, "w": 5, "h": 5, "route": "/other"}]
        good["trends"] = [{"id": "TR", "x": 400, "y": 300, "w": 100, "h": 100, "pens": [{"tag": "src/level"}]}]
        good["labels"] += [lab("UP", "upper text", 300, 400, 100), lab("DN", "lower text", 300, 300, 100)]
        dump(w["descriptors"] / "Plant.json", good)
        inv = {"objects": [{"class": "Text", "text": "UPPER TEXT", "x": 10, "y": 10, "w": 50, "h": 13},
                           {"class": "Text", "text": "LOWER TEXT", "x": 10, "y": 100, "w": 50, "h": 13}]}
        dump(self.d / "inv" / "Plant.json", inv)
        code, doc = run(self.d, w, "--canvas", "1000x600", "--require-stretch")
        self.assertEqual((code, doc["layout"]["count"]), (0, 0), doc["layout"])        # no inventory: no L11
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code, doc = run(self.d, w, "--canvas", "1000x600", "--require-stretch", "--inventory", str(self.d / "inv"))
        self.assertEqual(code, 2)
        self.assertEqual([f["rule"] for f in doc["layout"]["findings"]], ["L11"])
        self.assertIn("layout Plant L11", buf.getvalue())
        code, _ = run(self.d, w, "--canvas", "1000x600", "--inventory", str(self.d / "missing"))
        self.assertEqual(code, 1)



def tank_page(params: dict, labels: list[dict], symbols: tuple = ()) -> dict:
    """The fitting page with a vessel V1 at (400, 250), 360 by 300, of the given parameters, and more labels and symbols."""
    page = drawn(labels=[*drawn()["labels"], *labels])
    page["symbols"] += [{"id": "V1", "kind": "tank", "x": 400, "y": 250, "w": 360, "h": 300, "params": params},
                        *symbols]
    return page


class VesselTests(unittest.TestCase):
    """L10 and G5 on a vessel that holds its instruments, as the original draws a wet well (COB-191; WorkflowBuilder
    WFB-213): what lies wholly inside the vessel and clear of its own texts and level is placed there on purpose."""

    STATIC = {"static": True, "hasTag": False, "hasCapacity": False, "showPercent": False}

    def test_labels_wholly_inside_a_static_vessel_are_placed_there_on_purpose(self):
        inside = [lab("A", "Level high", 420, 270, 150), lab("B", "Duty level", 420, 470, 150)]
        self.assertEqual(of(lay2(tank_page(self.STATIC, inside)), "L10"), [])

    def test_a_label_across_the_outline_of_a_vessel_is_a_finding(self):
        across = [lab("A", "Level high", 380, 270, 150)]                       # its text starts 20 px left of the vessel
        found = of(lay2(tank_page(self.STATIC, across)), "L10")
        self.assertEqual([f["id"] for f in found], ["A, V1"])
        self.assertIn("across the outline of the vessel V1", found[0]["reason"])

    def test_a_label_over_the_vessels_own_identifier_or_capacity_is_a_finding(self):
        shown = {"static": True, "hasTag": True, "hasCapacity": True}
        low = [lab("A", "Level low", 420, 250 + 0.8 * 300, 150)]               # in the identifier's band, 0.76 to 0.96
        found = of(lay2(tank_page(shown, low)), "L10")
        self.assertEqual([f["id"] for f in found], ["A, V1"])
        self.assertIn("covers the identifier of the vessel V1", found[0]["reason"])
        middle = [lab("A", "Level", 420, 250 + 0.3 * 300, 150)]                # in the capacity's band, 0.26 to 0.50
        self.assertIn("capacity", of(lay2(tank_page(shown, middle)), "L10")[0]["reason"])
        top = [lab("A", "Level", 420, 250 + 0.08 * 300, 150)]                  # above both bands
        self.assertEqual(of(lay2(tank_page(shown, top)), "L10"), [])
        bare = [lab("A", "Level low", 420, 250 + 0.8 * 300, 150)]              # no identifier drawn: the band is free
        self.assertEqual(of(lay2(tank_page({**shown, "hasTag": False}, bare)), "L10"), [])

    def test_a_live_vessel_keeps_its_readings_and_level_clear(self):
        found = of(lay2(tank_page({}, [lab("A", "Level", 420, 250 + 0.2 * 300, 150)])), "L10")   # the view's defaults
        self.assertIn("covers the percentage", found[0]["reason"])
        found = of(lay2(tank_page({}, [lab("A", "Level", 420, 250 + 0.7 * 300, 150)])), "L10")
        self.assertIn("covers the level", found[0]["reason"])
        chart = of(lay2(tank_page({"chart": True}, [lab("A", "Level", 420, 250 + 0.55 * 300, 150)])), "L10")
        self.assertIn("covers the trend chart", chart[0]["reason"])

    def test_a_label_over_any_other_symbol_is_still_a_finding(self):
        page = tank_page(self.STATIC, [lab("A", "text", 30, 70, 100)])          # over the pump P1, beside the vessel
        self.assertEqual([f["id"] for f in of(lay2(page), "L10")], ["A, P1"])
        lamp = {"id": "L1", "kind": "indicator", "x": 420, "y": 300, "w": 48, "h": 48, "params": {"readoutPosition": "right"}}
        over = tank_page(self.STATIC, [lab("A", "Level high", 430, 310, 150)], (lamp,))   # inside the vessel, over the lamp
        self.assertEqual([f["id"] for f in of(lay2(over), "L10")], ["A, L1"])
        beside = tank_page(self.STATIC, [lab("A", "Level high", 474, 314, 150)], (lamp,))
        self.assertEqual(of(lay2(beside), "L10"), [])

    def test_the_bands_and_defaults_are_the_tank_views(self):
        from hmi import library, vessel
        doc, _contract = library.tank()
        at = {c["meta"]["name"]: c["position"] for c in doc["root"]["children"]}
        boxes = {name: box for kind in vessel.BANDS.values() for name, box, _p, _w in kind}
        names = {"capacity": "StaticValue", "identifier": "StaticTag", "percentage": "Header", "value": "ValueRow",
                 "level": "Level", "trend chart": "Chart"}
        for band, node in names.items():
            p = at[node]
            self.assertEqual(tuple(p[k] for k in ("x", "y", "width", "height")),
                             boxes[band] if band != "identifier" else (0.0, 0.76, 1.0, 0.2), band)
        live_tag = next(box for name, box, _p, _w in vessel.BANDS["live"] if name == "identifier")
        self.assertEqual(tuple(at["Tag"][k] for k in ("x", "y", "width", "height")), live_tag)
        self.assertEqual({k: library.TANK_PARAMS[k] for k in vessel.DEFAULTS}, vessel.DEFAULTS)
        self.assertEqual(vessel.CONTAINER_VIEWS, {"Automation/Tank", __import__("hmi.screen").screen.MODULE_KIND["tank"]})


class VesselGateTests(unittest.TestCase):
    """G5 on the generated page: lamps inside a vessel pass, a lamp across its outline fails."""

    def g5(self, lamp_x: float, render: str) -> dict:
        from hmi import gates, screen as gen
        desc = {"schema": "cadre-hmi-screen/1",
                "screen": {"id": "W", "route": "/w", "title": "W", "view": "Screens/W", "layout": "diagram", "width": 1000,
                           "height": 600},
                "symbols": [{"id": "V1", "kind": "tank", "x": 400, "y": 200, "w": 400, "h": 300,
                             "params": dict(VesselTests.STATIC, valueFractionDigits=0)},
                            {"id": "L1", "kind": "indicator", "x": lamp_x, "y": 230, "w": 48, "h": 48,
                             "params": {"readoutPosition": "right"}}]}
        child, _reports = gen.build_child("cadre_hmi_vessel", [desc], "Vessel", render=render)
        with tempfile.TemporaryDirectory() as tmp:
            return gates.g5_layout(child.write(Path(tmp)))

    def test_a_lamp_inside_a_vessel_passes_and_one_across_its_outline_fails(self):
        for render in ("stock", "module"):
            inside = self.g5(430, render)
            self.assertTrue(inside["ok"], (render, inside))
            across = self.g5(380, render)
            self.assertFalse(across["ok"], render)
            self.assertTrue(any("crosses the outline of the vessel" in p for p in across["problems"]), across)

if __name__ == "__main__":
    unittest.main()
