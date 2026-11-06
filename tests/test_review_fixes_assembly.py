"""Regression tests of the cold review's findings 7 and 10 on the assembly element (NOTE-WFB-10 section 11.2 items 1, 6
and 8):

    7   `device` and a part's `member` hold no empty, `.` or `..` path segment (T1, T4)
    10  G0 rule `assembly-button-on-page`: a button is allowed in `home` only; the component test page's benchlocal
        carries its pulse button in its Home and none in its page parts

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import local_support as L  # noqa: E402
from local_support import KIND, TAG_ROOT, assembly, devices, page  # noqa: E402

from hmi import assembly as asm  # noqa: E402
from hmi import library_profile, screen, testbench  # noqa: E402

BUTTON = {"id": "BT", "x": 10, "y": 140, "w": 90, "h": 30, "label": "Start", "member": "cmdStart"}


def without_buttons(a: dict) -> dict:
    a = copy.deepcopy(a)
    a["parts"].pop("buttons", None)
    return a


def with_page_button(a: dict) -> dict:
    """The assembly with a button in its page parts (the fixture's button is in its Home)."""
    a = copy.deepcopy(a)
    a["parts"]["buttons"] = [dict(BUTTON, id="PB")]
    return a


def with_home_button(a: dict) -> dict:
    a = without_buttons(a)
    a["home"] = {"w": 200, "h": 100, "parts": {"buttons": [dict(BUTTON, id="HB")]}}
    return a


def clean(**more) -> dict:
    return with_home_button(assembly(**more))


def errors(descs, names=None, local_kinds=(KIND,)):
    names = names or [f"d{i}" for i in range(len(descs))]
    return asm.g0_errors(descs, names, list(local_kinds), set())


class SegmentTests(unittest.TestCase):
    """Finding 7: no empty, `.` or `..` segment in `device` or in a part's `member`."""

    BAD = ("../Plant/PUMP01", "Plant/../PUMP01", "..", "./Skid1", "Plant/./Skid1", "Plant//Skid1", "Plant/..", "a/../../b")
    GOOD = ("Skid1", "Plant/Skid1", "Plant/Area.2/Skid-1", "a.b/c", "Plant/..x", "Plant/x..")

    def schema_errors(self, a):
        return screen.schema_errors([page(a)], ["d"])

    def test_a_device_with_a_dot_or_empty_segment_is_refused_by_the_schema(self):
        for device in self.BAD:
            with self.subTest(device=device):
                self.assertNotEqual(self.schema_errors(clean(device=device)), [], device)

    def test_a_device_without_such_a_segment_is_accepted(self):
        for device in self.GOOD:
            with self.subTest(device=device):
                self.assertEqual(self.schema_errors(clean(device=device)), [], device)

    def test_a_symbol_member_with_a_dot_or_empty_segment_is_refused(self):
        for member in self.BAD + ("a/../../b",):
            a = clean()
            a["parts"]["symbols"][0]["member"] = member
            with self.subTest(member=member):
                self.assertNotEqual(self.schema_errors(a), [], member)

    def test_a_button_member_in_the_home_with_a_dot_or_empty_segment_is_refused(self):
        for member in self.BAD:
            a = clean()
            a["home"]["parts"]["buttons"][0]["member"] = member
            with self.subTest(member=member):
                self.assertNotEqual(self.schema_errors(a), [], member)

    def test_a_home_symbol_member_with_a_dot_segment_is_refused(self):
        a = clean()
        a["home"]["parts"]["symbols"] = [{"id": "HS", "kind": "readout", "x": 0, "y": 0, "w": 50, "h": 20,
                                          "member": "a/../../b"}]
        self.assertNotEqual(self.schema_errors(a), [])

    def test_a_member_without_such_a_segment_is_accepted(self):
        for member in ("value", "sub/value", "a.b", "x/y.z"):
            a = clean()
            a["parts"]["symbols"][0]["member"] = member
            with self.subTest(member=member):
                self.assertEqual(self.schema_errors(a), [], member)


class ButtonOnPageTests(unittest.TestCase):
    """Finding 10: G0 rule `assembly-button-on-page` (item 1; Table 11.2's order of rules)."""

    def test_the_rule_is_the_last_of_the_rules_in_the_order_of_item_6(self):
        self.assertEqual(asm.RULES[-2:], ("assembly-part-ids", "assembly-button-on-page"))

    def test_a_button_in_parts_fails_g0_with_the_rule_name(self):
        got = errors([page(with_page_button(assembly()))])
        self.assertEqual([e["rule"] for e in got], ["assembly-button-on-page"], got)
        self.assertEqual(got[0]["assembly"], "A1")
        self.assertIn("PB", got[0]["message"])

    def test_a_button_in_the_home_only_passes_g0(self):
        self.assertEqual(errors([page(clean())]), [])

    def test_each_button_of_parts_is_named_and_a_button_in_the_home_beside_it_is_not(self):
        a = clean()
        a["parts"]["buttons"] = [dict(BUTTON, id="B1"), dict(BUTTON, id="B2")]
        got = errors([page(a)])
        self.assertEqual([e["rule"] for e in got], ["assembly-button-on-page"])
        self.assertIn("B1", got[0]["message"])
        self.assertIn("B2", got[0]["message"])
        self.assertNotIn("HB", got[0]["message"])

    def test_the_rule_is_listed_after_the_other_rules_that_apply(self):
        a = with_page_button(assembly(kind="widget"))
        got = errors([page(a)], local_kinds=("other",))
        self.assertEqual([e["rule"] for e in got], ["assembly-kind-not-local", "assembly-button-on-page"])

    def test_screen_py_refuses_a_page_with_a_button_in_parts_and_reports_the_rule(self):
        base = L.Parent()
        try:
            res = base.screen(page(with_page_button(assembly())), dev=devices("Skid1"), local_kinds=[KIND])
            self.assertNotEqual(res.code, 0, res.text[-1500:])
            self.assertIn("assembly-button-on-page", json.dumps(res.g0_errors()))
            ok = base.screen(page(clean()), dev=devices("Skid1"), local_kinds=[KIND])
            self.assertEqual(ok.code, 0, ok.text[-1500:])
        finally:
            base.close()


class BenchHomeTests(unittest.TestCase):
    """Finding 10 (11.2 item 8): benchlocal's pulse button lives in its Home."""

    @classmethod
    def setUpClass(cls):
        contracts = screen.load_contracts()
        cls.prof = library_profile.build(contracts)
        cls.bench = testbench.build(contracts, cls.prof, TAG_ROOT)
        cls.asm = next(a for a in cls.bench.descriptor["assemblies"] if a["kind"] == testbench.LOCAL_KIND)

    def test_the_page_parts_hold_no_button(self):
        self.assertEqual(self.asm["parts"].get("buttons", []), [])

    def test_the_home_holds_the_pulse_button_of_cmd_start(self):
        self.assertEqual([b["member"] for b in self.asm["home"]["parts"].get("buttons", [])], ["cmdStart"])

    def test_the_page_passes_g0_rule_assembly_button_on_page(self):
        names = ["<component test>"]
        got = asm.g0_errors([self.bench.descriptor], names, [], set(self.prof["kinds"]) | set(self.prof["deviceKinds"]),
                            {0: {testbench.LOCAL_KIND}})
        self.assertEqual(got, [])


if __name__ == "__main__":
    unittest.main()
