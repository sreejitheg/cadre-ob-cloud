"""Tests of the page checks for the assembly element (NOTE-WFB-10 section 11.2 item 7; acceptance corpus 7; threat T4).
Work package WP-W03, written from the note before the feature exists.

`page_checks.KINDS` gains `assembly`; a coverage map entry may be `{kind: "assembly", id: "<assembly>/<part>"}`;
`descriptor_tags` counts each dynamic part of an assembly (a symbol or a button) with the tag `<device>/<member>`;
`built_tags` reads the child's `views/Local/**` as well as `views/Screens/<page>`; a dynamic part with no `member`, or
whose tag does not resolve, is listed in `unbound` as `<assembly>/<part>`.

Synthetic names only. Nothing here needs the gateway.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import local_support as L  # noqa: E402
from local_support import assembly, devices, page  # noqa: E402

from hmi import page_checks  # noqa: E402


def dump(path: Path, doc) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8", newline="\n")
    return path


def run(d: Path, desc: dict, *extra: str, cover=None, mapping=None) -> tuple[int, dict]:
    """page_checks on one descriptor with the device `Skid1` (members value, state, cmdStart) and an empty tag model."""
    dump(d / "descriptors" / "PageA.json", desc)
    args = ["--descriptors", str(d / "descriptors"), "--devices", str(dump(d / "devices.json", devices("Skid1"))),
            "--tags", str(dump(d / "tags.json", {"name": "cadre_hmi_loc", "tagType": "Folder", "tags": []})),
            "--navtable", str(dump(d / "nav.json", [])), "--project", "cadre_hmi_loc", "--out", str(d / "out")]
    if cover is not None:
        args += ["--coverage-map", str(dump(d / "cover.json", cover)),
                 "--mapping", str(dump(d / "mapping.json", mapping))]
    code = page_checks.main([*args, *extra])
    out = d / "out" / "checks.json"
    return code, json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}


def is_part(entry: str, name: str) -> bool:
    """An `unbound` or `unresolved_tags` entry names the part as `<assembly>/<part>`, with or without the page before it."""
    return name in entry.replace(":", " ").split() or entry == name


class AssemblyChecksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    # ---- tags bound --------------------------------------------------------------------------------------------
    def test_a_bound_assembly_counts_its_dynamic_parts_and_passes(self):
        code, doc = run(self.d, page(assembly()))
        self.assertEqual(code, 0, doc.get("tags_bound"))
        bound = doc["tags_bound"]
        # the readout, the indicator and the button are dynamic; the label, the line and the shape are static
        self.assertEqual((bound["value_components"], bound["bound"]), (3, 3))
        self.assertEqual((bound["unbound"], bound["unresolved_tags"]), ([], []))

    def test_a_readout_with_no_member_is_listed_in_unbound_as_assembly_slash_part(self):
        a = assembly()
        del a["parts"]["symbols"][0]["member"]
        code, doc = run(self.d, page(a))
        self.assertEqual(code, 2)
        bound = doc["tags_bound"]
        self.assertEqual([u for u in bound["unbound"] if is_part(u, "A1/RO")].__len__(), 1, bound["unbound"])
        self.assertEqual(len(bound["unbound"]), 1)
        self.assertEqual((bound["value_components"], bound["bound"]), (3, 2))

    def test_a_button_with_no_member_is_listed_in_unbound(self):
        a = assembly()
        del a["home"]["parts"]["buttons"][0]["member"]   # the button lives in the Home
        code, doc = run(self.d, page(a))
        self.assertEqual(code, 2)
        self.assertEqual([u for u in doc["tags_bound"]["unbound"] if is_part(u, "A1/BT")].__len__(), 1)

    def test_a_static_part_is_never_listed_unbound(self):
        a = assembly()
        a["parts"]["symbols"] = []
        a["home"]["parts"]["buttons"] = []   # the button lives in the Home
        code, doc = run(self.d, page(a))
        self.assertEqual(code, 0, doc.get("tags_bound"))
        self.assertEqual((doc["tags_bound"]["value_components"], doc["tags_bound"]["unbound"]), (0, []))

    def test_a_member_the_device_does_not_carry_is_a_tag_that_does_not_resolve(self):
        a = assembly()
        a["parts"]["symbols"][0]["member"] = "noSuchMember"
        code, doc = run(self.d, page(a))
        self.assertEqual(code, 2)
        bad = doc["tags_bound"]["unresolved_tags"]
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("Skid1/noSuchMember", bad[0])
        self.assertIn("A1/RO", bad[0])

    def test_the_tag_of_a_part_is_the_device_folder_joined_with_its_member(self):
        a = assembly("A1", device="Skid1")
        a["parts"]["symbols"][1]["member"] = "state"
        a["home"]["parts"]["buttons"][0]["member"] = "cmdStart"   # the button lives in the Home
        code, doc = run(self.d, page(a))
        self.assertEqual(code, 0, doc["tags_bound"])
        # the same member under another device folder is another tag, unknown to the device model
        b = assembly("A1", device="Skid9")
        code, doc = run(self.d, page(b))
        self.assertEqual(code, 2)
        self.assertTrue(all("Skid9/" in t for t in doc["tags_bound"]["unresolved_tags"]), doc["tags_bound"])
        self.assertEqual(len(doc["tags_bound"]["unresolved_tags"]), 3)

    def test_an_assembly_and_a_plain_symbol_on_one_page_are_counted_together(self):
        desc = page(assembly())
        desc["symbols"] = [{"id": "R9", "kind": "readout", "x": 10, "y": 10, "w": 100, "h": 40,
                            "bind": {"value": "Skid1/value"}}]
        code, doc = run(self.d, desc)
        self.assertEqual(code, 0, doc.get("tags_bound"))
        self.assertEqual((doc["tags_bound"]["value_components"], doc["tags_bound"]["bound"]), (4, 4))

    # ---- built views (T4) ---------------------------------------------------------------------------------------
    def built(self, local_children, home_children=(), page_children=()):
        built = self.d / "build" / "cadre_hmi_loc" / "com.inductiveautomation.perspective"
        dump(built / "page-config" / "config.json", {"pages": {"/a": {}}})
        dump(built / "session-props" / "props.json", {"custom": {"devices": [{"folder": "[default]cadre_hmi_loc/Skid1"}]}})

        def view(children):
            return {"root": {"type": "ia.container.coord", "meta": {"name": "Diagram"}, "children": list(children)}}
        dump(built / "views" / "Screens" / "PageA" / "view.json", view(page_children))
        dump(built / "views" / "Local" / "Skid" / "view.json", view(local_children))
        dump(built / "views" / "Local" / "Skid" / "Home" / "view.json", view(home_children))
        return built

    @staticmethod
    def tagged(name):
        return {"type": "cadre.ob.readout", "meta": {"name": name},
                "propConfig": {"props.value": {"binding": {"type": "tag", "config": {
                    "tagPath": "[default]x/{view.params.deviceId}/value"}}}}}

    @staticmethod
    def bare(name):
        return {"type": "cadre.ob.readout", "meta": {"name": name}}

    def test_built_tags_reads_the_views_under_local_as_well_as_the_page_views(self):
        self.built([self.tagged("RO")], [self.tagged("HR")], [self.tagged("P")])
        code, doc = run(self.d, page(assembly()), "--built", str(self.d / "build"))
        self.assertEqual(code, 0, doc["tags_bound"])
        # one component in the page view, one in Local/Skid and one in Local/Skid/Home are all counted
        self.assertEqual(sum(doc["tags_bound"]["view_classes"].values()), 3, doc["tags_bound"]["view_classes"])

    def test_a_component_with_no_tag_in_a_local_view_is_listed_unbound(self):
        self.built([self.tagged("RO"), self.bare("STATIC_VALUE")])
        code, doc = run(self.d, page(assembly()), "--built", str(self.d / "build"))
        self.assertEqual(code, 2)
        self.assertEqual([u for u in doc["tags_bound"]["unbound"] if "STATIC_VALUE" in u].__len__(), 1,
                         doc["tags_bound"]["unbound"])

    def test_a_component_with_no_tag_in_a_local_home_view_is_listed_unbound(self):
        self.built([self.tagged("RO")], [self.bare("HOME_STATIC")])
        code, doc = run(self.d, page(assembly()), "--built", str(self.d / "build"))
        self.assertEqual(code, 2)
        self.assertEqual([u for u in doc["tags_bound"]["unbound"] if "HOME_STATIC" in u].__len__(), 1,
                         doc["tags_bound"]["unbound"])

    def test_built_tags_returns_the_local_views_components_directly(self):
        built = self.built([self.tagged("RO"), self.bare("STATIC_VALUE")])
        counts, unbound = page_checks.built_tags(built, ["PageA"])
        self.assertEqual(sum(counts.values()), 2)      # RO and the bare component; the bare one is also in `unbound`
        self.assertTrue(any("STATIC_VALUE" in u for u in unbound), unbound)

    def test_a_build_with_no_local_views_is_read_as_it_was(self):
        built = self.built([], [], [self.tagged("P")])
        for f in (built / "views" / "Local").rglob("view.json"):
            f.unlink()
        counts, unbound = page_checks.built_tags(built, ["PageA"])
        self.assertEqual((sum(counts.values()), unbound), (1, []))

    # ---- coverage -------------------------------------------------------------------------------------------------
    def rows(self):
        return [{"uid": "PageA:r1", "source": "PageA", "section": "readouts", "label": "Pressure"},
                {"uid": "PageA:r2", "source": "PageA", "section": "buttons", "label": "Start"}]

    def test_a_coverage_entry_of_kind_assembly_carries_a_row(self):
        self.assertIn("assembly", page_checks.KINDS)
        cover = {"PageA:r1": {"drawn": [{"kind": "assembly", "id": "A1/RO"}]},
                 "PageA:r2": {"drawn": [{"kind": "assembly", "id": "A1/BT"}]}}
        code, doc = run(self.d, page(assembly()), cover=cover, mapping=self.rows())
        self.assertEqual(code, 0, doc["coverage"])
        self.assertEqual((doc["coverage"]["covered"], doc["coverage"]["rows"]), (2, 2))
        self.assertEqual([r["carried_by"] for r in doc["rows"]], [["assembly:A1/RO"], ["assembly:A1/BT"]])

    def test_a_coverage_entry_naming_a_part_the_assembly_lacks_is_missing(self):
        cover = {"PageA:r1": {"drawn": [{"kind": "assembly", "id": "A1/RO"}]},
                 "PageA:r2": {"drawn": [{"kind": "assembly", "id": "A1/GONE"}]}}
        code, doc = run(self.d, page(assembly()), cover=cover, mapping=self.rows())
        self.assertEqual(code, 2)
        self.assertEqual([m.split()[0] for m in doc["coverage"]["missing"]], ["PageA:r2"])
        cover["PageA:r2"] = {"drawn": [{"kind": "assembly", "id": "NOPE/BT"}]}      # an assembly the page lacks
        code, doc = run(self.d, page(assembly()), cover=cover, mapping=self.rows())
        self.assertEqual([m.split()[0] for m in doc["coverage"]["missing"]], ["PageA:r2"])


if __name__ == "__main__":
    unittest.main()
