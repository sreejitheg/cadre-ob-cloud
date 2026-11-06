"""Tests of the release mode of `tools/hmi/library_gaps.py` (NOTE-WFB-10 section 8.2, 10.2 and 11.4; work package
WP-W05): one open gap per `openbridge` and `shared_gap` placement of an approved survey, none else, exit 0, schema
`cadre-hmi-library-gaps/2`. The release block (not the tool) compares the hashes (T3, T16); nothing of that is tested
here. The surveys are made by the survey mode from a hand-written ctig survey. All names are synthetic."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import dump  # noqa: E402
from survey_support import (PROFILE, ROW_PROPERTIES, ROW_STATES, ctig_survey, dev, kind_row, load_json,  # noqa: E402
                            make_map, release_argv, row, run, run_cli, sha256_of, standard_kinds, survey_argv)

BADGE_PROPERTIES = {"label": "text"}


class ReleaseCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.map = make_map(cls.dir / "map.json", [
            row("benchwrap", "obc-switch"),
            row("pump", "obc-badge", feature="member:benchLocalMember", properties=BADGE_PROPERTIES, states=[])])
        cls.ctig = dump(cls.dir / "ctig.json", ctig_survey(standard_kinds()))
        cls.survey_path = cls.make_survey("survey-a")
        cls.released = cls.release("release-a", cls.survey_path)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    @classmethod
    def make_survey(cls, name, ctig=None, profile=None, proposals=True):
        """A final survey: `benchprop` accepted at the card on a model proposal, the rest placed by the table."""
        out = cls.dir / name
        extra = []
        if proposals:
            props = dump(cls.dir / f"{name}.proposals.json", {"proposals": [
                {"kind": "benchprop", "feature": None, "element": "obc-switch", "properties": {"state": "checked"},
                 "states": ROW_STATES, "reason": "A switch fits."}]})
            changes = dump(cls.dir / f"{name}.changes.json", {"changes": []})
            extra = ["--proposals", props, "--changes", changes]
        else:   # finding 3: release mode refuses a draft, so the survey without proposals is final too
            extra = ["--changes", dump(cls.dir / f"{name}.changes.json", {"changes": []})]
        code, text = run(survey_argv(ctig or cls.ctig, out, cls.map, profile, *extra))
        assert code == 0, text
        return out / "survey.json"

    @classmethod
    def release(cls, name, survey, mapf=None):
        out = cls.dir / name
        code, text = run(release_argv(survey, out, mapf or cls.map))
        path = out / "gaps.json"
        return {"code": code, "text": text, "out": out, "doc": load_json(path) if path.exists() else None}

    def gaps(self, released=None):
        released = released or self.released
        self.assertEqual(released["code"], 0, released["text"])
        self.assertIsNotNone(released["doc"], "gaps.json was not written: " + released["text"])
        return {g["id"]: g for g in released["doc"]["gaps"]}


class ReleaseGapTests(ReleaseCase):
    def test_exit_0_and_the_gap_list_is_version_2(self):
        self.assertEqual(self.released["code"], 0)
        doc = self.released["doc"]
        self.assertEqual(doc["schema"], "cadre-hmi-library-gaps/2")
        self.assertEqual(doc["open_count"], len(doc["gaps"]))

    def test_there_is_exactly_one_open_gap_per_openbridge_and_shared_gap_placement_and_no_other(self):
        gaps = self.gaps()
        self.assertEqual(sorted(gaps), sorted([
            "GAP-benchprop", "GAP-benchwrap", "GAP-pump-member-benchLocalMember",
            "GAP-benchrej", "GAP-benchshared", "GAP-benchtwo", "GAP-pump-member-benchSharedMember"]))
        self.assertEqual(len(self.released["doc"]["gaps"]), 7, "one gap each, no duplicate")
        self.assertEqual(self.released["doc"]["open_count"], 7)
        self.assertEqual({g["status"] for g in gaps.values()}, {"open"})

    def test_a_kind_gap_is_gap_kind_and_a_feature_gap_replaces_each_colon_with_a_hyphen(self):
        gaps = self.gaps()
        self.assertEqual((gaps["GAP-benchshared"]["kind"], gaps["GAP-benchshared"].get("feature")),
                         ("benchshared", None))
        g = gaps["GAP-pump-member-benchSharedMember"]
        self.assertEqual((g["kind"], g["feature"]), ("pump", "member:benchSharedMember"))

    def test_each_gap_carries_its_placement_and_count(self):
        gaps = self.gaps()
        expected = {"GAP-benchprop": ("openbridge", 1), "GAP-benchwrap": ("openbridge", 1),
                    "GAP-pump-member-benchLocalMember": ("openbridge", 1), "GAP-benchrej": ("shared_gap", 2),
                    "GAP-benchshared": ("shared_gap", 3), "GAP-benchtwo": ("shared_gap", 2),
                    "GAP-pump-member-benchSharedMember": ("shared_gap", 3)}
        self.assertEqual({k: (g["placement"], g["count"]) for k, g in gaps.items()}, expected)

    def test_a_wrap_needs_its_element_properties_and_states_from_the_map_row_or_the_accepted_proposal(self):
        gaps = self.gaps()
        self.assertEqual(gaps["GAP-benchwrap"]["needed"],
                         {"element": "obc-switch", "properties": ROW_PROPERTIES, "states": ROW_STATES})
        self.assertEqual(gaps["GAP-benchprop"]["needed"],
                         {"element": "obc-switch", "properties": {"state": "checked"}, "states": ROW_STATES})
        self.assertEqual(gaps["GAP-pump-member-benchLocalMember"]["needed"],
                         {"element": "obc-badge", "properties": BADGE_PROPERTIES, "states": []})
        for gid in ("GAP-benchwrap", "GAP-benchprop", "GAP-pump-member-benchLocalMember"):
            self.assertEqual(gaps[gid]["element"], gaps[gid]["needed"]["element"], gid)

    def test_a_shared_gap_needs_the_members_of_its_instances_and_their_number(self):
        gaps = self.gaps()
        self.assertEqual(gaps["GAP-benchshared"]["needed"], {"members": ["benchAlso", "benchTravel"], "instances": 3})
        self.assertEqual(gaps["GAP-benchtwo"]["needed"], {"members": [], "instances": 2})
        self.assertEqual(gaps["GAP-benchrej"]["needed"], {"members": [], "instances": 2})
        self.assertEqual(gaps["GAP-pump-member-benchSharedMember"]["needed"],
                         {"members": ["benchSharedMember"], "instances": 3})

    def test_a_faceplate_shared_gap_needs_no_members(self):
        profile = load_json(PROFILE)
        for key in ("faceplate", "faceplates"):
            profile["deviceKinds"]["pump"].pop(key, None)
            profile["kinds"]["pump"].pop(key, None)
        profile_path = dump(self.dir / "no-faceplate.profile.json", profile)
        survey = self.make_survey("survey-faceplate", profile=profile_path)
        gaps = self.gaps(self.release("release-faceplate", survey))
        self.assertEqual(gaps["GAP-pump-faceplate"]["needed"], {"members": [], "instances": 2})
        self.assertEqual(gaps["GAP-pump-faceplate"]["placement"], "shared_gap")

    def test_the_gap_list_names_the_survey_hash_and_its_library_commit(self):
        survey = load_json(self.survey_path)
        self.assertEqual(self.released["doc"]["survey"],
                         {"sha256": sha256_of(self.survey_path), "library_commit": survey["library_commit"]})

    def test_local_library_unclassified_and_unnamed_items_make_no_gap(self):
        ids = set(self.gaps())
        for name in ("benchlocal", "benchnull", "pump", "sequence"):
            self.assertNotIn(f"GAP-{name}", ids)
        self.assertNotIn("GAP-pump-unnamed-zq", ids)
        self.assertNotIn("GAP-pump-member-cmd", ids)
        self.assertNotIn("GAP-pump-faceplate", ids)

    def test_a_survey_with_nothing_to_build_gives_no_gap_and_still_exits_0(self):
        ctig = dump(self.dir / "quiet.ctig.json", ctig_survey([
            kind_row("pump", [dev("stemP1", ["pgBeta"], members=["cmd"])]),
            kind_row("benchlocal", [dev("stemX1", ["pgBeta"])])]))
        survey = self.make_survey("survey-quiet", ctig=ctig, proposals=False)
        released = self.release("release-quiet", survey)
        self.assertEqual(released["code"], 0, released["text"])
        self.assertEqual((released["doc"]["gaps"], released["doc"]["open_count"]), ([], 0))
        self.assertEqual(released["doc"]["schema"], "cadre-hmi-library-gaps/2")

    def test_a_rejected_proposal_leaves_a_shared_gap_and_no_wrap_for_its_kind(self):
        props = dump(self.dir / "rej.proposals.json", {"proposals": [
            {"kind": "benchrej", "feature": None, "element": "obc-button", "properties": {}, "states": [],
             "reason": "A button fits."}]})
        changes = dump(self.dir / "rej.changes.json", {"changes": [
            {"action": "reject_proposal", "kind": "benchrej", "feature": None, "reason": "It does not fit."}]})
        out = self.dir / "survey-rej"
        code, text = run(survey_argv(self.ctig, out, self.map, None, "--proposals", props, "--changes", changes))
        self.assertEqual(code, 0, text)
        gaps = self.gaps(self.release("release-rej", out / "survey.json"))
        self.assertEqual(gaps["GAP-benchrej"]["placement"], "shared_gap")
        self.assertNotIn("GAP-benchprop", gaps, "no proposal for benchprop here: it is local")

    def test_a_survey_that_cannot_be_read_is_an_input_fault_with_exit_1(self):
        code, _ = run(release_argv(self.dir / "none.json", self.dir / "none", self.map))
        self.assertEqual(code, 1)
        self.assertFalse((self.dir / "none" / "gaps.json").exists())

    def test_the_command_line_exits_0_and_release_mode_needs_no_model_or_design(self):
        r = run_cli(release_argv(self.survey_path, self.dir / "cli", self.map))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.dir / "cli" / "gaps.json").exists())

    def test_the_same_survey_gives_the_same_gap_list(self):
        again = self.release("release-again", self.survey_path)
        a, b = dict(self.released["doc"]), dict(again["doc"])
        a.pop("provenance", None)
        b.pop("provenance", None)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
