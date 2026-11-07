"""Further tests of the survey, release and project-survey modes of `tools/hmi/library_gaps.py` (work package WP-W05,
NOTE-WFB-10 sections 7.5 to 7.8, 8.2, 9.2 and 10.2): the two new schema files against real outputs, the faults, the
accepted map proposals and the late features. Synthetic names only."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump, validate  # noqa: E402
from survey_support import (CATALOGUE, MODULE, PROFILE, REAL_MAP, ROW_STATES, SURVEY_SCHEMA, by_kind,  # noqa: E402
                            ctig_survey, dev, kind_row, load_json, make_map, release_argv, row, run, run_cli,
                            standard_kinds, survey_argv)
from test_library_gaps_project_survey import PageCase, device_row, kind_entry, local_entry, survey_doc  # noqa: E402
from test_library_gaps_features import design, row as design_row  # noqa: E402


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.ctig = dump(cls.dir / "ctig.json", ctig_survey(standard_kinds()))
        cls.map = make_map(cls.dir / "map.json", [row("benchwrap", "obc-switch")])
        props = dump(cls.dir / "p.json", {"proposals": [
            {"kind": "benchprop", "feature": None, "element": "obc-switch", "properties": {"state": "checked"},
             "states": ROW_STATES, "reason": "A switch fits."}]})
        changes = dump(cls.dir / "c.json", {"changes": [
            {"action": "to_local", "kind": "benchshared", "feature": None, "reason": "Rare."},
            {"action": "to_local", "kind": "nosuchkind", "feature": None, "reason": "None."}]})
        cls.draft = cls.survey("draft", [])
        cls.final = cls.survey("final", ["--proposals", props, "--changes", changes])

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    @classmethod
    def survey(cls, name, extra):
        out = cls.dir / name
        code, text = run(survey_argv(cls.ctig, out, cls.map, None, *extra))
        assert code == 0, text
        return out

    def test_a_draft_and_a_final_survey_validate_against_the_survey_schema(self):
        for out in (self.draft, self.final):
            self.assertEqual(validate(load_json(out / "survey.json"), "cadre-hmi-project-survey-1.json"), [])
        schema = load_json(ROOT / "schemas" / "cadre-hmi-project-survey-1.json")
        self.assertEqual(schema["$id"], SURVEY_SCHEMA)

    def test_a_release_gap_list_validates_against_the_version_2_schema(self):
        out = self.dir / "release"
        code, text = run(release_argv(self.final / "survey.json", out, self.map))
        self.assertEqual(code, 0, text)
        doc = load_json(out / "gaps.json")
        self.assertEqual(validate(doc, "cadre-hmi-library-gaps-2.json"), [])
        self.assertEqual(load_json(ROOT / "schemas" / "cadre-hmi-library-gaps-2.json")["$id"],
                         "cadre-hmi-library-gaps/2")

    def test_the_survey_names_no_provenance_so_its_bytes_do_not_change_between_runs(self):
        again = self.survey("again", [])
        self.assertEqual((again / "survey.json").read_bytes(), (self.draft / "survey.json").read_bytes())

    def test_a_survey_mode_run_in_the_final_state_still_writes_the_three_files(self):
        for name in ("survey.json", "unmapped.json", "proposal_source.json"):
            self.assertTrue((self.final / name).exists(), name)


class FaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.ctig = dump(cls.dir / "ctig.json", ctig_survey(standard_kinds()))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_a_document_that_is_not_a_ctig_survey_is_a_fault(self):
        other = dump(self.dir / "other.json", {"schema": "something/1", "kinds": []})
        code, text = run(survey_argv(other, self.dir / "o1"))
        self.assertEqual(code, 1)
        self.assertIn("ctig.survey/1", text)
        self.assertFalse((self.dir / "o1" / "survey.json").exists())

    def test_a_kind_name_that_is_not_lower_case_with_hyphens_is_a_fault(self):
        bad = dump(self.dir / "bad.json", ctig_survey([kind_row("Bad_Kind", [dev("stemA", ["pgBeta"])])]))
        code, text = run(survey_argv(bad, self.dir / "o2"))
        self.assertEqual(code, 1, text)

    def test_a_local_max_outside_1_to_10_is_a_fault(self):
        for value in ("0", "11"):
            code, _ = run(survey_argv(self.ctig, self.dir / ("lm" + value), None, None, "--local-max", value))
            self.assertEqual(code, 1, value)

    def test_survey_mode_needs_the_map_and_the_elements_list(self):
        argv = ["--survey", str(self.ctig), "--catalogue", str(CATALOGUE), "--profile", str(PROFILE), "--module",
                str(MODULE), "--out", str(self.dir / "o3")]
        code, text = run(argv)
        self.assertEqual(code, 1)
        self.assertIn("--openbridge-map", text)

    def test_survey_and_release_together_or_with_page_inputs_are_a_fault(self):
        survey = dump(self.dir / "s.json", {"schema": SURVEY_SCHEMA})
        argv = survey_argv(self.ctig, self.dir / "o4") + ["--release", str(survey)]
        self.assertEqual(run(argv)[0], 1)
        argv = survey_argv(self.ctig, self.dir / "o5") + ["--model", str(self.ctig)]
        self.assertEqual(run(argv)[0], 1)

    def test_a_release_of_a_document_that_is_not_a_survey_is_a_fault(self):
        other = dump(self.dir / "notasurvey.json", {"schema": "something/1"})
        self.assertEqual(run(release_argv(other, self.dir / "o6"))[0], 1)

    def test_changes_that_are_not_a_list_are_a_fault(self):
        bad = dump(self.dir / "badchanges.json", {"changes": "no"})
        code, _ = run(survey_argv(self.ctig, self.dir / "o7", None, None, "--changes", bad))
        self.assertEqual(code, 1)

    def test_page_mode_without_a_model_is_a_fault_with_exit_1(self):
        r = run_cli(["--catalogue", str(CATALOGUE), "--profile", str(PROFILE), "--module", str(MODULE), "--out",
                     str(self.dir / "o8"), "--designs", str(self.ctig)])
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)


class MapProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.ctig = dump(cls.dir / "ctig.json", ctig_survey([
            kind_row("bus", [dev("stemU1", ["pgBeta"]), dev("stemU2", ["pgBeta"])])]))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def final(self, name, changes):
        out = self.dir / name
        path = dump(self.dir / f"{name}.changes.json", {"changes": changes})
        code, text = run(survey_argv(self.ctig, out, REAL_MAP, None, "--changes", path))
        self.assertEqual(code, 0, text)
        return load_json(out / "survey.json")

    def test_an_approval_accepts_a_proposed_map_row_it_does_not_reject_and_places_the_kind(self):
        doc = self.final("accepted", [])
        k = by_kind(doc)["bus"]
        self.assertEqual((k["placement"], k["map_row"]), ("openbridge", {"element": "obc-bus", "state": "approved"}))
        p = doc["proposals"][0]
        self.assertEqual((p["source"], p["verdict"]), ("map", "accepted"))

    def test_the_owner_may_reject_a_proposed_map_row(self):
        doc = self.final("rejected", [{"action": "reject_proposal", "kind": "bus", "feature": None,
                                       "reason": "Not a bus here."}])
        self.assertEqual(by_kind(doc)["bus"]["placement"], "shared_gap")
        self.assertEqual(doc["proposals"][0]["verdict"], "rejected")
        self.assertEqual(doc["approval"]["refused"], [])

    def test_a_repeated_rejection_and_an_empty_reason_are_refused(self):
        doc = self.final("repeat", [
            {"action": "reject_proposal", "kind": "bus", "feature": None, "reason": "No."},
            {"action": "reject_proposal", "kind": "bus", "feature": None, "reason": "Again."},
            {"action": "reject_proposal", "kind": "bus", "feature": None, "reason": "  "}])
        self.assertEqual(len(doc["approval"]["changes"]), 1)
        self.assertEqual(len(doc["approval"]["refused"]), 2)


class LateFeatureAndWrapTests(PageCase):
    def test_a_design_feature_in_a_late_file_is_listed_unclassified_in_the_next_survey(self):
        run_out = self.out()
        path = self.put(survey_doc())
        argv = ["--model", str(self.model), "--design", str(self.put(design([design_row("u1:1", "bar")]), "design")),
                "--descriptor-schema", str(self.stub_schema), "--catalogue", str(self.stub_catalogue),
                "--profile", str(PROFILE), "--module", str(MODULE), "--out", str(run_out), "--project-survey", str(path),
                "--openbridge-map", str(REAL_MAP)]
        r = self.page_run(argv, run_out)
        late = r["doc"]["late"]
        self.assertEqual([e["rule"] for e in late], ["feature"])
        ctig = dump(self.dir / "ctig-late.json", ctig_survey([kind_row("sequence", [dev("stemS1", ["pgBeta"])])]))
        out = self.out()
        code, text = run(survey_argv(ctig, out, REAL_MAP, None, "--late", run_out / "gaps.json"))
        self.assertEqual(code, 0, text)
        doc = load_json(out / "survey.json")
        self.assertEqual([(u["kind"], u["count"]) for u in doc["unclassified_features"]], [("bar", 1)])
        self.assertNotIn("bar", by_kind(doc), "a design feature is no kind")

    def test_a_kind_the_survey_wrapped_and_the_library_now_draws_is_listed_as_a_wrap(self):
        survey = survey_doc([kind_entry("pump", "openbridge", 3)])
        survey["wraps"] = [{"kind": "pump", "feature": None, "element": "obc-pump", "state": "reviewed"}]
        r = self.with_survey(survey)
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(r["doc"]["wraps"], [{"kind": "pump", "feature": None, "element": "obc-pump"}])
        self.assertEqual({k["kind"]: k["resolution"] for k in r["doc"]["kinds"]}["pump"], "library")

    def test_a_page_run_gap_list_validates_against_the_version_2_schema(self):
        r = self.with_survey(survey_doc([kind_entry("ups", "local")], [local_entry("ups", "ups01")]))
        self.assertEqual(validate(r["doc"], "cadre-hmi-library-gaps-2.json"), [])

    def test_survey_mode_flags_do_not_change_a_page_run_with_a_survey_of_the_wrong_schema(self):
        bad = self.put({"schema": "something/1", "kinds": []})
        out = self.out()
        code, text = run(self.designs_argv(out, "--project-survey", bad))
        self.assertEqual(code, 1)
        self.assertIn(SURVEY_SCHEMA, text)


if __name__ == "__main__":
    unittest.main()
