"""No generated view lies in the folder of another view (wiki/07 GF-117, tranche T3).

Ignition 8.3.6 does not find a view whose folder also holds another view: an embed of `A/B`, where `A/B/C` is also a
view, draws the view-not-found badge, while `A/B/C` itself is found. The local assembly's two views are therefore
siblings, `Local/<Kind>/Assembly` and `Local/<Kind>/Home`, in the folder `Local/<Kind>`, and the faceplate's Home path
(`'Local/' + localKind + '/Home'`) is unchanged. These tests hold the parent build and a child with assemblies to it.

Run from the repository root:  python -m unittest tests.test_view_nesting
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools"))

import local_support as L  # noqa: E402
from local_support import KIND, page  # noqa: E402
from hmi import assembly  # noqa: E402

VIEWS = "com.inductiveautomation.perspective/views"


def nested(paths: list[str]) -> list[tuple[str, str]]:
    """Each pair (view, view beneath it) of `paths`, the view paths of one project."""
    have = set(paths)
    return sorted((v, w) for w in have for v in have if w.startswith(v + "/"))


class NoViewInAViewsFolder(unittest.TestCase):
    def test_the_rule_finds_a_view_beneath_a_view(self):
        self.assertEqual(nested(["Local/Pumpstand", "Local/Pumpstand/Home", "Screens/A"]),
                         [("Local/Pumpstand", "Local/Pumpstand/Home")])
        self.assertEqual(nested(["Local/Pumpstand/Assembly", "Local/Pumpstand/Home"]), [])

    def test_the_tracked_parent_has_no_view_beneath_another(self):
        views = ROOT / "build" / "cadre_hmi_base" / VIEWS
        paths = [f.parent.relative_to(views).as_posix() for f in views.rglob("view.json")]
        self.assertTrue(len(paths) > 50, len(paths))
        self.assertEqual(nested(paths), [])

    def test_the_paths_of_a_kind_are_siblings_in_its_folder(self):
        self.assertEqual(assembly.view_path("pumpstand"), "Local/Pumpstand/Assembly")
        self.assertEqual(assembly.home_path("pumpstand"), "Local/Pumpstand/Home")
        self.assertEqual(assembly.kind_folder("pumpstand"), "Local/Pumpstand")


class AChildWithAssemblies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = L.Parent()

    @classmethod
    def tearDownClass(cls):
        cls.base.close()

    def test_a_built_child_has_no_view_beneath_another_and_its_kind_folder_is_no_view(self):
        res = self.base.screen(page(L.assembly()), local_kinds=[KIND])
        self.assertEqual(res.code, 0, res.text[-2500:])
        paths = [f[:-len("/view.json")] for f in res.view_files()]
        self.assertIn(assembly.view_path(KIND), paths)
        self.assertIn(assembly.home_path(KIND), paths)
        self.assertNotIn(assembly.kind_folder(KIND), paths)
        self.assertEqual(nested(paths), [])


if __name__ == "__main__":
    unittest.main()
