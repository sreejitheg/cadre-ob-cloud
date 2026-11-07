"""Tests of the survey mode of `tools/hmi/library_gaps.py` (NOTE-WFB-10 sections 7.5 to 7.8, 10.2 and 11.4; threats T3
(tool side), T15; work package WP-W05). The ctig survey is written by hand (Table 7.2); the library's real catalogue,
profile, module parts, map and elements list are read. All names are synthetic.

Assumptions the note leaves to the builder, flagged in the work package's report: the file names of the survey mode's
side outputs (`unmapped.json` and `proposal_source.json` beside `survey.json` in `--out`), the shapes of the changes
and proposals files (`{"changes": [...]}`, `{"proposals": [...]}`), and that a run given `--changes` is a final survey."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import dump  # noqa: E402
from survey_support import (ELEMENTS, NAMES_OF_PAGES, PROFILE, REAL_MAP, ROW_PROPERTIES, ROW_STATES, STEMS,  # noqa: E402
                            SURVEY_SCHEMA, by_kind, ctig_survey, dev, feature_of, has_token, kind_row, library_head,
                            load_json, make_map, row, run, run_cli, sha256_of, standard_kinds, survey_argv)


class SurveyCase(unittest.TestCase):
    """One temporary folder per class, one named run per scenario."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.ctig = dump(cls.dir / "ctig-survey.json", ctig_survey(standard_kinds()))
        cls.map = make_map(cls.dir / "map.json", [row("benchwrap", "obc-switch")])
        cls.default = cls.survey("default")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    @classmethod
    def survey(cls, name, ctig=None, mapf=None, profile=None, extra=()):
        out = cls.dir / name
        code, text = run(survey_argv(ctig or cls.ctig, out, mapf or cls.map, profile, *extra))
        path = out / "survey.json"
        doc = load_json(path) if path.exists() else None
        return {"code": code, "text": text, "out": out, "doc": doc}

    def doc_of(self, result):
        self.assertEqual(result["code"], 0, result["text"])
        self.assertIsNotNone(result["doc"], "survey.json was not written: " + result["text"])
        return result["doc"]


class TableRowTests(SurveyCase):
    def test_the_run_exits_0_and_writes_a_survey_with_the_fields_of_table_7_6(self):
        doc = self.doc_of(self.default)
        self.assertEqual(self.default["code"], 0)
        for key in ("schema", "library_commit", "openbridge_release", "ctig_survey_sha256", "local_max", "pages",
                    "kinds", "wraps", "shared_gaps", "local", "unclassified", "unclassified_features", "proposals",
                    "approval", "totals"):
            self.assertIn(key, doc)
        self.assertEqual(doc["schema"], SURVEY_SCHEMA)
        self.assertEqual(doc["local_max"], 1)
        self.assertIsNone(doc["approval"], "a draft survey has no approval")

    def test_the_survey_names_the_library_commit_the_pin_the_ctig_hash_and_ctigs_page_totals(self):
        doc = self.doc_of(self.default)
        self.assertEqual(doc["library_commit"], library_head())
        elements = load_json(ELEMENTS)
        self.assertEqual(doc["openbridge_release"], {"version": elements["release"], "commit": elements["commit"]})
        self.assertEqual(doc["ctig_survey_sha256"], sha256_of(self.ctig))
        self.assertEqual(doc["pages"], load_json(self.ctig)["pages"])

    def test_row_1_a_library_kind_is_placed_library_with_its_view_and_no_map_row(self):
        kinds = by_kind(self.doc_of(self.default))
        for name, view in (("pump", "Automation/Pump"), ("sequence", "Instrument/Sequence")):
            k = kinds[name]
            self.assertEqual((k["placement"], k["library_resolution"], k["map_row"], k["resolution"],
                              k["placement_source"]), ("library", "library", None, view, "table"), name)

    def test_row_1_with_module_first_a_kind_that_has_a_module_part_is_placed_module(self):
        result = self.survey("module-first", extra=["--module-first"])
        kinds = by_kind(self.doc_of(result))
        pump = kinds["pump"]
        self.assertEqual((pump["placement"], pump["library_resolution"], pump["resolution"]),
                         ("module", "module", "cadre.ob.pump"))
        self.assertEqual(kinds["sequence"]["placement"], "library", "the module has no part for a sequence")

    def test_row_1_wins_over_a_map_row_for_a_kind_the_library_resolves(self):
        mapf = make_map(self.dir / "row1.map.json", [row("pump", "obc-button")])
        kinds = by_kind(self.doc_of(self.survey("row1", mapf=mapf)))
        self.assertEqual(kinds["pump"]["placement"], "library")

    def test_row_2_a_kind_with_a_reviewed_map_row_is_placed_openbridge_whatever_its_count(self):
        doc = self.doc_of(self.default)
        k = by_kind(doc)["benchwrap"]
        self.assertEqual(k["count"], 1)
        self.assertEqual((k["placement"], k["library_resolution"], k["placement_source"], k["resolution"]),
                         ("openbridge", None, "table", "obc-switch"))
        self.assertEqual(k["map_row"], {"element": "obc-switch", "state": "reviewed"})
        self.assertEqual(doc["wraps"], [{"kind": "benchwrap", "feature": None, "element": "obc-switch",
                                         "state": "reviewed"}])

    def test_row_2_a_row_in_state_approved_places_and_a_row_in_state_proposed_does_not(self):
        approved = make_map(self.dir / "approved.map.json", [row("benchwrap", "obc-switch", state="approved")])
        k = by_kind(self.doc_of(self.survey("approved", mapf=approved)))["benchwrap"]
        self.assertEqual((k["placement"], k["map_row"]), ("openbridge", {"element": "obc-switch", "state": "approved"}))
        proposed = make_map(self.dir / "proposed.map.json", [row("benchwrap", "obc-switch", state="proposed")])
        doc = self.doc_of(self.survey("proposed", mapf=proposed))
        self.assertEqual(by_kind(doc)["benchwrap"]["placement"], "local", "only reviewed or approved rows place (T3)")
        self.assertEqual(doc["wraps"], [])

    def test_a_rejected_entry_of_the_map_places_nothing(self):
        rejected = load_json(REAL_MAP)["rejected"][0]["kind"]
        ctig = dump(self.dir / "rejected.ctig.json", ctig_survey([kind_row(rejected, [dev("stemX1", ["pgBeta"])])]))
        k = by_kind(self.doc_of(self.survey("rejected", ctig=ctig)))[rejected]
        self.assertEqual(k["placement"], "local")
        self.assertIsNone(k["map_row"])

    def test_row_3_an_unresolved_kind_above_local_max_is_a_shared_gap(self):
        kinds = by_kind(self.doc_of(self.default))
        for name, count in (("benchshared", 3), ("benchtwo", 2), ("benchrej", 2)):
            k = kinds[name]
            self.assertEqual((k["count"], k["placement"], k["placement_source"], k["library_resolution"],
                              k["map_row"], k["resolution"]), (count, "shared_gap", "table", None, None, None), name)

    def test_row_4_an_unresolved_kind_with_local_max_instances_or_fewer_is_local(self):
        kinds = by_kind(self.doc_of(self.default))
        for name in ("benchlocal", "benchprop", "benchnull"):
            k = kinds[name]
            self.assertEqual((k["count"], k["placement"], k["placement_source"]), (1, "local", "table"), name)

    def test_kind_counts_stemless_and_faceplate_only_come_from_ctig(self):
        kinds = by_kind(self.doc_of(self.default))
        self.assertEqual((kinds["pump"]["count"], kinds["pump"]["stemless"], kinds["pump"]["faceplate_only"]), (3, 0, 0))
        self.assertEqual(kinds["sequence"]["faceplate_only"], 1)
        self.assertEqual(kinds["benchlocal"]["stemless"], 1)

    def test_row_1_features_member_and_faceplate_of_a_placed_kind_that_the_profile_resolves(self):
        pump = by_kind(self.doc_of(self.default))["pump"]
        for feature, count in (("member:cmd", 3), ("member:fault", 2), ("faceplate", 2)):
            f = feature_of(pump, feature)
            self.assertIsNotNone(f, feature)
            self.assertEqual((f["count"], f["placement"], f["placement_source"]), (count, "library", "table"), feature)
            self.assertIsNotNone(f["resolution"], feature)

    def test_row_5_a_feature_of_a_placed_kind_that_the_profile_lacks_is_a_shared_gap_above_local_max(self):
        f = feature_of(by_kind(self.doc_of(self.default))["pump"], "member:benchSharedMember")
        self.assertEqual((f["count"], f["placement"], f["placement_source"], f["resolution"]),
                         (3, "shared_gap", "table", None))

    def test_row_6_a_feature_of_a_placed_kind_that_the_profile_lacks_is_local_up_to_local_max(self):
        f = feature_of(by_kind(self.doc_of(self.default))["pump"], "member:benchLocalMember")
        self.assertEqual((f["count"], f["placement"], f["placement_source"]), (1, "local", "table"))

    def test_row_2_also_places_a_feature_of_a_placed_kind_by_a_reviewed_row(self):
        mapf = make_map(self.dir / "feature.map.json", [row("pump", "obc-badge", feature="member:benchLocalMember")])
        doc = self.doc_of(self.survey("feature-row", mapf=mapf))
        f = feature_of(by_kind(doc)["pump"], "member:benchLocalMember")
        self.assertEqual((f["placement"], f["resolution"]), ("openbridge", "obc-badge"))
        self.assertIn({"kind": "pump", "feature": "member:benchLocalMember", "element": "obc-badge",
                       "state": "reviewed"}, doc["wraps"])
        self.assertNotIn("member:benchLocalMember", [e["feature"] for e in doc["local"]])

    def test_a_faceplate_feature_is_unresolved_when_the_profile_gives_the_kind_no_faceplate(self):
        profile = load_json(PROFILE)
        for key in ("faceplate", "faceplates"):
            profile["deviceKinds"]["pump"].pop(key, None)
            profile["kinds"]["pump"].pop(key, None)
        profile_path = dump(self.dir / "no-faceplate.profile.json", profile)
        doc = self.doc_of(self.survey("no-faceplate", profile=profile_path))
        f = feature_of(by_kind(doc)["pump"], "faceplate")
        self.assertEqual((f["count"], f["placement"], f["resolution"]), (2, "shared_gap", None))
        self.assertIn("GAP-pump-faceplate", [g["id"] for g in doc["shared_gaps"]])
        wider = self.survey("no-faceplate-2", profile=profile_path, extra=["--local-max", "2"])
        self.assertEqual(feature_of(by_kind(self.doc_of(wider))["pump"], "faceplate")["placement"], "local")

    def test_a_feature_of_an_unresolved_kind_travels_with_its_kind_with_no_placement(self):
        shared = by_kind(self.doc_of(self.default))["benchshared"]
        f = feature_of(shared, "member:benchTravel")
        self.assertIsNotNone(f)
        self.assertEqual((f["count"], f["placement"], f["resolution"]), (2, None, None))
        self.assertEqual(feature_of(shared, "member:benchAlso")["count"], 2)

    def test_row_7_unnamed_features_are_listed_unclassified_with_counts_and_place_nothing(self):
        doc = self.doc_of(self.default)
        self.assertEqual(doc["unclassified_features"], [
            {"kind": "benchshared", "feature": "unnamed:ab", "count": 3},
            {"kind": "pump", "feature": "unnamed:zq", "count": 2}])
        for k in doc["kinds"]:
            for f in k["features"]:
                if f["feature"].startswith("unnamed:"):
                    self.assertEqual(f["placement"], "unclassified", (k["kind"], f))
        self.assertNotIn("unnamed:zq", [g["feature"] for g in doc["shared_gaps"]])
        self.assertNotIn("unnamed:zq", [e["feature"] for e in doc["local"]])

    def test_row_7_unclassified_templates_static_templates_and_unplaced_devices_are_listed_with_counts(self):
        rows = self.doc_of(self.default)["unclassified"]
        by = {r["kind"]: r for r in rows}
        self.assertEqual(set(by), {"template", "static", "no_kind", "stem_not_recovered"})
        self.assertEqual((by["template"]["template"], by["template"]["instances"], by["template"]["pages"]),
                         ("TplA", 4, 2))
        self.assertEqual((by["static"]["template"], by["static"]["instances"], by["static"]["pages"]),
                         ("TplS", 3, 1))
        self.assertEqual(by["no_kind"]["instances"], 2)
        self.assertEqual(by["stem_not_recovered"]["instances"], 1)

    def test_wraps_shared_gaps_and_local_are_listed_as_table_7_6_gives(self):
        doc = self.doc_of(self.default)
        self.assertEqual(doc["shared_gaps"], [
            {"id": "GAP-benchrej", "kind": "benchrej", "feature": None, "count": 2, "stems": ["stemj1", "stemJ2"]},
            {"id": "GAP-benchshared", "kind": "benchshared", "feature": None, "count": 3,
             "stems": ["stemH1", "stemH2", "stemH3"]},
            {"id": "GAP-benchtwo", "kind": "benchtwo", "feature": None, "count": 2, "stems": ["stema2", "stemB2"]},
            {"id": "GAP-pump-member-benchSharedMember", "kind": "pump", "feature": "member:benchSharedMember",
             "count": 3, "stems": ["stemP1", "stemP2", "stemP3"]}])
        # One entry per local instance; the page is the first operator page of the instance in case-insensitive order
        # (stemP1 draws pgZeta, pgalpha and the pop-up pgPop), and a stemless instance has a null stem.
        self.assertEqual(doc["local"], [
            {"kind": "benchlocal", "feature": None, "stem": None, "page": "pgZeta"},
            {"kind": "benchnull", "feature": None, "stem": "stemN1", "page": "pgZeta"},
            {"kind": "benchprop", "feature": None, "stem": "stemR1", "page": "pgBeta"},
            {"kind": "pump", "feature": "member:benchLocalMember", "stem": "stemP1", "page": "pgalpha"}])

    def test_totals_count_kinds_instances_wraps_shared_gaps_local_and_unclassified_objects(self):
        self.assertEqual(self.doc_of(self.default)["totals"], {
            "kinds": 9, "instances": 15, "wraps": 1, "shared_gaps": 4, "local": 4, "unclassified_objects": 9})

    def test_arrays_are_sorted_case_insensitively_by_kind_feature_and_stem(self):
        doc = self.doc_of(self.default)
        names = [k["kind"] for k in doc["kinds"]]
        self.assertEqual(names, sorted(names, key=str.casefold))
        self.assertEqual(names[0], "benchlocal")
        features = [f["feature"] for f in by_kind(doc)["pump"]["features"]]
        self.assertEqual(features, sorted(features, key=str.casefold))
        ids = [(g["kind"], g["feature"] or "") for g in doc["shared_gaps"]]
        self.assertEqual(ids, sorted(ids, key=lambda x: (x[0].casefold(), x[1].casefold())))
        two = next(g for g in doc["shared_gaps"] if g["kind"] == "benchtwo")
        self.assertEqual(two["stems"], ["stema2", "stemB2"], "case-insensitive, not by code point")

    def test_the_same_inputs_give_the_same_survey(self):
        again = self.survey("again")
        a, b = dict(self.doc_of(self.default)), dict(self.doc_of(again))
        a.pop("provenance", None)
        b.pop("provenance", None)
        self.assertEqual(a, b)
        self.assertNotIn(b"\r", (again["out"] / "survey.json").read_bytes())

    def test_a_missing_ctig_survey_is_an_input_fault_with_exit_1(self):
        code, text = run(survey_argv(self.dir / "none.json", self.dir / "none", self.map))
        self.assertEqual(code, 1)
        self.assertTrue(text.strip(), "a fault is explained on standard output")
        self.assertFalse((self.dir / "none" / "survey.json").exists())

    def test_the_command_line_exits_0_and_survey_mode_needs_no_model(self):
        r = run_cli(survey_argv(self.ctig, self.dir / "cli", self.map))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.dir / "cli" / "survey.json").exists())


class ThresholdAndHistoryTests(SurveyCase):
    def test_local_max_2_moves_a_kind_with_two_instances_from_shared_gap_to_local(self):
        before = by_kind(self.doc_of(self.default))["benchtwo"]["placement"]
        doc = self.doc_of(self.survey("lm2", extra=["--local-max", "2"]))
        self.assertEqual((before, doc["local_max"]), ("shared_gap", 2))
        kinds = by_kind(doc)
        self.assertEqual(kinds["benchtwo"]["placement"], "local", "a count equal to local_max is local")
        self.assertEqual(kinds["benchrej"]["placement"], "local")
        self.assertEqual(kinds["benchshared"]["placement"], "shared_gap", "three is more than two")
        self.assertEqual([e["stem"] for e in doc["local"] if e["kind"] == "benchtwo"], ["stema2", "stemB2"])
        self.assertEqual(doc["totals"]["shared_gaps"], 2)

    def test_prior_local_makes_a_kind_a_shared_gap_whatever_its_count(self):
        prior_a = dump(self.dir / "prior-a.json", {"schema": SURVEY_SCHEMA, "kinds": [
            {"kind": "benchlocal", "count": 1, "placement": "local", "placement_source": "table", "features": []}],
            "local": [{"kind": "benchlocal", "feature": None, "stem": None, "page": "pgOld"}]})
        prior_b = dump(self.dir / "prior-b.json", {"schema": SURVEY_SCHEMA, "kinds": [
            {"kind": "benchprop", "count": 1, "placement": "local", "placement_source": "table", "features": []}],
            "local": [{"kind": "benchprop", "feature": None, "stem": "stemOld", "page": "pgOld"}]})
        doc = self.doc_of(self.survey("prior", extra=["--prior-local", prior_a, "--prior-local", prior_b]))
        kinds = by_kind(doc)
        for name in ("benchlocal", "benchprop"):
            self.assertEqual((kinds[name]["count"], kinds[name]["placement"], kinds[name]["placement_source"]),
                             (1, "shared_gap", "prior_local"), name)
        self.assertEqual((kinds["benchnull"]["placement"], kinds["benchnull"]["placement_source"]),
                         ("local", "table"))
        ids = [g["id"] for g in doc["shared_gaps"]]
        self.assertIn("GAP-benchlocal", ids)
        self.assertIn("GAP-benchprop", ids)
        self.assertEqual(next(g for g in doc["shared_gaps"] if g["kind"] == "benchprop")["stems"], ["stemR1"])
        self.assertEqual([e["kind"] for e in doc["local"]], ["benchnull", "pump"])

    def test_a_prior_local_file_that_names_no_kind_of_this_survey_changes_nothing(self):
        prior = dump(self.dir / "prior-other.json", {"schema": SURVEY_SCHEMA, "kinds": [
            {"kind": "benchelsewhere", "count": 1, "placement": "local", "placement_source": "table",
             "features": []}], "local": []})
        doc = self.doc_of(self.survey("prior-other", extra=["--prior-local", prior]))
        base = self.doc_of(self.default)
        self.assertEqual([(k["kind"], k["placement"]) for k in doc["kinds"]],
                         [(k["kind"], k["placement"]) for k in base["kinds"]])

    def late_file(self):
        return dump(self.dir / "late-gaps.json", {"schema": "cadre-hmi-library-gaps/2", "late": [
            {"kind": "benchlate", "feature": None, "id": "GAP-benchlate", "rule": "twice", "status": "accepted",
             "reason": "two instances", "count": 3, "stems": ["stemL1", "stemL2", "stemL3"]},
            {"kind": "benchlocal", "feature": None, "id": "GAP-benchlocal", "rule": "second", "status": "accepted",
             "reason": "a second instance", "count": 1, "stems": ["stemL9"]},
            {"kind": "benchonce", "feature": None, "id": "GAP-benchonce", "rule": "once", "status": "local",
             "reason": "one instance", "count": 1, "stems": ["stemO1"]},
            {"kind": "pump", "feature": "member:benchLateMember", "id": "GAP-pump-member-benchLateMember",
             "rule": "twice", "status": "accepted", "reason": "a late member", "count": 2,
             "stems": ["stemQ1", "stemQ2"]}]})

    def test_late_rows_are_added_with_their_counts_summed_with_the_census_and_placed_by_the_same_table(self):
        doc = self.doc_of(self.survey("late", extra=["--late", self.late_file()]))
        kinds = by_kind(doc)
        self.assertEqual((kinds["benchlate"]["count"], kinds["benchlate"]["placement"]), (3, "shared_gap"))
        self.assertEqual((kinds["benchlocal"]["count"], kinds["benchlocal"]["placement"]), (2, "shared_gap"),
                         "one in the census and one late: more than local_max")
        self.assertEqual((kinds["benchonce"]["count"], kinds["benchonce"]["placement"]), (1, "local"))
        f = feature_of(kinds["pump"], "member:benchLateMember")
        self.assertEqual((f["count"], f["placement"]), (2, "shared_gap"))
        gaps = {g["id"]: g for g in doc["shared_gaps"]}
        self.assertEqual(gaps["GAP-benchlate"]["stems"], ["stemL1", "stemL2", "stemL3"])
        self.assertEqual(gaps["GAP-benchlate"]["count"], 3)
        self.assertEqual(gaps["GAP-benchlocal"]["count"], 2)
        self.assertIn("stemL9", gaps["GAP-benchlocal"]["stems"])
        self.assertEqual(gaps["GAP-pump-member-benchLateMember"]["stems"], ["stemQ1", "stemQ2"])
        self.assertIn({"kind": "benchonce", "feature": None, "stem": "stemO1"},
                      [{k: e[k] for k in ("kind", "feature", "stem")} for e in doc["local"]])
        self.assertEqual(doc["totals"]["kinds"], 11)

    def test_a_late_row_for_a_kind_with_a_reviewed_map_row_is_placed_openbridge(self):
        late = dump(self.dir / "late-wrap.json", {"late": [
            {"kind": "benchwrap", "feature": None, "id": "GAP-benchwrap", "rule": "map", "status": "accepted",
             "reason": "reviewed", "count": 1, "stems": ["stemL5"]}]})
        k = by_kind(self.doc_of(self.survey("late-wrap", extra=["--late", late])))["benchwrap"]
        self.assertEqual((k["count"], k["placement"]), (2, "openbridge"))

    def test_two_late_files_are_both_read(self):
        one = dump(self.dir / "late-1.json", {"late": [
            {"kind": "benchlate", "feature": None, "id": "GAP-benchlate", "rule": "twice", "status": "accepted",
             "reason": "r", "count": 2, "stems": ["stemL1", "stemL2"]}]})
        two = dump(self.dir / "late-2.json", {"late": [
            {"kind": "benchonce", "feature": None, "id": "GAP-benchonce", "rule": "once", "status": "local",
             "reason": "r", "count": 1, "stems": ["stemO1"]}]})
        kinds = by_kind(self.doc_of(self.survey("late-two", extra=["--late", one, "--late", two])))
        self.assertIn("benchlate", kinds)
        self.assertIn("benchonce", kinds)


class ProposalTests(SurveyCase):
    def proposals(self):
        return dump(self.dir / "proposals.json", {"proposals": [
            {"kind": "benchprop", "feature": None, "element": "obc-switch", "properties": {"state": "checked"},
             "states": ROW_STATES, "reason": "A switch fits."},
            {"kind": "benchrej", "feature": None, "element": "obc-button", "properties": {}, "states": [],
             "reason": "A button fits."},
            {"kind": "benchshared", "feature": None, "element": "obc-not-in-the-pin", "properties": {},
             "states": [], "reason": "An element the pin lacks."},
            {"kind": "pump", "feature": None, "element": "obc-button", "properties": {}, "states": [],
             "reason": "A library kind."},
            {"kind": "benchwrap", "feature": None, "element": "obc-button", "properties": {}, "states": [],
             "reason": "A kind with a map row."},
            {"kind": "ghostkind", "feature": None, "element": "obc-button", "properties": {}, "states": [],
             "reason": "A kind the survey lacks."},
            {"kind": "benchnull", "feature": None, "element": None, "properties": {}, "states": [],
             "reason": "No element fits."}]})

    _n = 0

    def changes(self, *changes):
        ProposalTests._n += 1
        return dump(self.dir / f"changes-{ProposalTests._n}.json", {"changes": list(changes)})

    def final(self, name, *changes, proposals=None):
        extra = ["--proposals", proposals or self.proposals(), "--changes", self.changes(*changes)]
        return self.survey(name, extra=extra)

    def verdicts(self, doc):
        return {(p["kind"], p["feature"]): p for p in doc["proposals"]}

    def test_an_accepted_proposal_places_its_kind_by_row_2_with_the_approved_state(self):
        doc = self.doc_of(self.final("proposals", {"action": "reject_proposal", "kind": "benchrej", "feature": None,
                                                   "reason": "A button does not fit."}))
        k = by_kind(doc)["benchprop"]
        self.assertEqual((k["placement"], k["resolution"], k["map_row"]),
                         ("openbridge", "obc-switch", {"element": "obc-switch", "state": "approved"}))
        wrap = next(w for w in doc["wraps"] if w["kind"] == "benchprop")
        self.assertEqual((wrap["element"], wrap["state"]), ("obc-switch", "approved"))
        self.assertEqual(self.verdicts(doc)[("benchprop", None)]["verdict"], "accepted")
        self.assertEqual(self.verdicts(doc)[("benchprop", None)]["source"], "model")
        self.assertEqual(self.verdicts(doc)[("benchprop", None)]["properties"], {"state": "checked"})
        self.assertEqual(doc["totals"]["wraps"], 2, "the reviewed benchwrap and the accepted benchprop")
        self.assertEqual(by_kind(doc)["benchwrap"]["map_row"], {"element": "obc-switch", "state": "reviewed"})

    def test_a_rejected_proposal_returns_its_kind_to_the_table_with_no_map_row(self):
        doc = self.doc_of(self.final("rejected", {"action": "reject_proposal", "kind": "benchrej", "feature": None,
                                                  "reason": "A button does not fit."}))
        k = by_kind(doc)["benchrej"]
        self.assertEqual((k["placement"], k["map_row"]), ("shared_gap", None))
        self.assertEqual(self.verdicts(doc)[("benchrej", None)]["verdict"], "rejected")
        self.assertEqual([c["action"] for c in doc["approval"]["changes"]], ["reject_proposal"])
        self.assertEqual(doc["approval"]["refused"], [])

    def test_an_approval_with_no_rejection_accepts_every_valid_proposal(self):
        doc = self.doc_of(self.final("all-accepted"))
        self.assertEqual(self.verdicts(doc)[("benchrej", None)]["verdict"], "accepted")
        self.assertEqual(by_kind(doc)["benchrej"]["placement"], "openbridge")
        self.assertIsNotNone(doc["approval"])

    def test_a_proposal_with_an_element_outside_the_elements_list_is_dropped_with_a_reason_and_places_nothing(self):
        doc = self.doc_of(self.final("outside"))
        p = self.verdicts(doc)[("benchshared", None)]
        self.assertEqual(p["verdict"], "dropped")
        self.assertTrue(p["why"])
        self.assertEqual((by_kind(doc)["benchshared"]["placement"], by_kind(doc)["benchshared"]["map_row"]),
                         ("shared_gap", None))
        self.assertNotIn("obc-not-in-the-pin", [w["element"] for w in doc["wraps"]])

    def test_a_proposal_for_a_kind_that_is_not_unmapped_is_dropped(self):
        doc = self.doc_of(self.final("not-unmapped"))
        verdicts = self.verdicts(doc)
        for name in ("pump", "benchwrap", "ghostkind"):
            self.assertEqual(verdicts[(name, None)]["verdict"], "dropped", name)
            self.assertTrue(verdicts[(name, None)]["why"], name)
        kinds = by_kind(doc)
        self.assertEqual(kinds["pump"]["placement"], "library")
        self.assertEqual(kinds["benchwrap"]["map_row"], {"element": "obc-switch", "state": "reviewed"})
        self.assertNotIn("ghostkind", kinds)

    def test_a_proposal_with_no_element_is_shown_and_places_nothing(self):
        doc = self.doc_of(self.final("null-element"))
        self.assertIn(("benchnull", None), self.verdicts(doc))
        self.assertIsNone(self.verdicts(doc)[("benchnull", None)]["element"])
        k = by_kind(doc)["benchnull"]
        self.assertEqual((k["placement"], k["map_row"]), ("local", None))

    def test_a_proposal_alone_never_places_a_kind(self):
        doc = self.doc_of(self.survey("proposals-only", extra=["--proposals", self.proposals()]))
        self.assertNotEqual(by_kind(doc)["benchprop"]["placement"], "openbridge", "only the owner's acceptance places")
        self.assertEqual([w["kind"] for w in doc["wraps"]], ["benchwrap"])

    def test_a_proposed_row_of_the_map_is_shown_as_a_pending_proposal_and_does_not_place(self):
        ctig = dump(self.dir / "bus.ctig.json", ctig_survey([
            kind_row("bus", [dev("stemU1", ["pgBeta"]), dev("stemU2", ["pgBeta"]), dev("stemU3", ["pgBeta"])])]))
        result = self.survey("bus", ctig=ctig, mapf=REAL_MAP)
        doc = self.doc_of(result)
        self.assertNotEqual(by_kind(doc)["bus"]["placement"], "openbridge")
        self.assertEqual(doc["wraps"], [])
        p = self.verdicts(doc)[("bus", None)]
        self.assertEqual((p["source"], p["verdict"], p["element"]), ("map", "pending", "obc-bus"))
        unmapped = json.loads((result["out"] / "unmapped.json").read_text(encoding="utf-8"))
        self.assertNotIn("bus", [u["kind"] for u in unmapped], "a kind with a map row in any state is not unmapped")


class ChangeTests(SurveyCase):
    def final(self, name, changes):
        path = dump(self.dir / f"{name}.changes.json", {"changes": changes})
        return self.survey(name, extra=["--changes", path])

    def test_changes_are_applied_with_placement_source_change_and_the_rest_are_refused_with_a_reason(self):
        doc = self.doc_of(self.final("changes", [
            {"action": "to_local", "kind": "benchshared", "feature": None, "reason": "Only drawn once per area."},
            {"action": "to_shared_gap", "kind": "benchlocal", "feature": None, "reason": "More are coming."},
            {"action": "to_local", "kind": "pump", "feature": "member:benchSharedMember", "reason": "Rarely used."},
            {"action": "to_local", "kind": "pump", "feature": None, "reason": "A library kind stays."},
            {"action": "to_shared_gap", "kind": "benchwrap", "feature": None, "reason": "A wrapped kind stays."},
            {"action": "to_local", "kind": "nosuchkind", "feature": None, "reason": "No such item."},
            {"action": "reject_proposal", "kind": "ghostkind", "feature": None, "reason": "No such proposal."},
            {"action": "to_shared_gap", "kind": "benchnull", "feature": None, "reason": ""}]))
        kinds = by_kind(doc)
        self.assertEqual((kinds["benchshared"]["placement"], kinds["benchshared"]["placement_source"]),
                         ("local", "change"))
        self.assertEqual((kinds["benchlocal"]["placement"], kinds["benchlocal"]["placement_source"]),
                         ("shared_gap", "change"))
        f = feature_of(kinds["pump"], "member:benchSharedMember")
        self.assertEqual((f["placement"], f["placement_source"]), ("local", "change"))
        # Not applied: placement unchanged and still from the table.
        for name, placement in (("pump", "library"), ("benchwrap", "openbridge"), ("benchnull", "local")):
            self.assertEqual((kinds[name]["placement"], kinds[name]["placement_source"]), (placement, "table"), name)
        applied, refused = doc["approval"]["changes"], doc["approval"]["refused"]
        self.assertEqual(len(applied), 3)
        self.assertEqual(len(refused), 5)
        applied_text, refused_text = json.dumps(applied), json.dumps(refused)
        for name in ("benchshared", "benchlocal"):
            self.assertIn(name, applied_text)
        for name in ("nosuchkind", "ghostkind", "benchwrap", "benchnull"):
            self.assertIn(name, refused_text)
        self.assertTrue(all(r for r in refused), "each refusal says what was refused and why")
        # The applied changes move instances into and out of the lists.
        self.assertEqual(sorted(e["stem"] for e in doc["local"] if e["kind"] == "benchshared"),
                         ["stemH1", "stemH2", "stemH3"])
        self.assertEqual([e["kind"] for e in doc["local"] if e["kind"] == "benchlocal"], [])
        self.assertIn("GAP-benchlocal", [g["id"] for g in doc["shared_gaps"]])
        self.assertNotIn("GAP-benchshared", [g["id"] for g in doc["shared_gaps"]])
        self.assertEqual(len([e for e in doc["local"] if e["feature"] == "member:benchSharedMember"]), 3)
        self.assertEqual(doc["totals"]["local"], len(doc["local"]))
        self.assertEqual(doc["totals"]["shared_gaps"], len(doc["shared_gaps"]))

    def test_a_final_survey_with_no_changes_has_an_approval_with_nothing_applied_or_refused(self):
        doc = self.doc_of(self.final("no-changes", []))
        self.assertIsNotNone(doc["approval"])
        self.assertEqual((doc["approval"]["changes"], doc["approval"]["refused"]), ([], []))
        base = self.doc_of(self.default)
        self.assertEqual([(k["kind"], k["placement"]) for k in doc["kinds"]],
                         [(k["kind"], k["placement"]) for k in base["kinds"]])

    def test_to_local_and_to_shared_gap_apply_only_to_an_item_placed_shared_gap_or_local(self):
        doc = self.doc_of(self.final("wrong-placement", [
            {"action": "to_shared_gap", "kind": "benchtwo", "feature": None, "reason": "Already a shared gap."},
            {"action": "to_local", "kind": "benchlocal", "feature": None, "reason": "Already local."}]))
        # A change to the placement the item already has is not a change of placement: it is applied as a no-op or
        # refused, and either way the placement does not move.
        kinds = by_kind(doc)
        self.assertEqual(kinds["benchtwo"]["placement"], "shared_gap")
        self.assertEqual(kinds["benchlocal"]["placement"], "local")
        self.assertEqual(len(doc["approval"]["changes"]) + len(doc["approval"]["refused"]), 2)

    def test_a_change_never_moves_a_kind_the_library_resolves(self):
        doc = self.doc_of(self.final("library-kind", [
            {"action": "to_shared_gap", "kind": "sequence", "feature": None, "reason": "Try."}]))
        self.assertEqual(by_kind(doc)["sequence"]["placement"], "library")
        self.assertEqual(len(doc["approval"]["refused"]), 1)


class SideOutputTests(SurveyCase):
    def side(self, result, name):
        path = result["out"] / name
        self.assertTrue(path.exists(), f"the survey mode writes {name} beside survey.json")
        return load_json(path)

    def test_unmapped_lists_every_kind_and_feature_with_no_resolution_and_no_map_row(self):
        unmapped = self.side(self.default, "unmapped.json")
        items = [(u["kind"], u["feature"], u["count"]) for u in unmapped if not (u["feature"] or "").startswith("unnamed:")]
        self.assertEqual(items, [
            ("benchlocal", None, 1), ("benchnull", None, 1), ("benchprop", None, 1), ("benchrej", None, 2),
            ("benchshared", None, 3), ("benchtwo", None, 2), ("pump", "member:benchLocalMember", 1),
            ("pump", "member:benchSharedMember", 3)])
        shared = next(u for u in unmapped if u["kind"] == "benchshared" and u["feature"] is None)
        self.assertEqual(sorted(shared["members"]), ["benchAlso", "benchTravel"])
        self.assertEqual(shared["unnamed"], ["ab"])
        for u in unmapped:
            self.assertEqual(set(u), {"kind", "feature", "count", "members", "unnamed"})

    def test_a_survey_with_no_unmapped_item_has_an_empty_unmapped_list(self):
        ctig = dump(self.dir / "mapped.ctig.json", ctig_survey([
            kind_row("pump", [dev("stemP1", ["pgBeta"], members=["cmd"])]),
            kind_row("sequence", [dev("stemS1", ["pgBeta"])])]))
        result = self.survey("mapped", ctig=ctig)
        self.assertEqual(self.doc_of(result)["totals"]["shared_gaps"], 0)
        self.assertEqual(self.side(result, "unmapped.json"), [])
        self.assertEqual(self.side(result, "proposal_source.json")["unmapped"], [])

    def test_proposal_source_holds_the_unmapped_items_and_the_pinned_elements_and_nothing_else(self):
        source = self.side(self.default, "proposal_source.json")
        self.assertEqual(set(source), {"unmapped", "elements"})
        self.assertEqual(source["unmapped"], self.side(self.default, "unmapped.json"))
        tags = {e["tag"] for e in load_json(ELEMENTS)["elements"]}
        self.assertTrue(source["elements"])
        for e in source["elements"]:
            self.assertEqual(set(e), {"tag", "path", "group", "properties"})
            self.assertIn(e["tag"], tags)
            for p in e["properties"]:
                self.assertEqual(set(p), {"name", "type", "enum", "default"})

    def test_the_proposal_source_and_unmapped_hold_no_stem_page_or_popup_name(self):
        late = dump(self.dir / "late-scan.json", {"late": [
            {"kind": "benchlate", "feature": None, "id": "GAP-benchlate", "rule": "twice", "status": "accepted",
             "reason": "r", "count": 2, "stems": ["stemL1", "stemL2"]}]})
        result = self.survey("scan", extra=["--late", late])
        for name in ("unmapped.json", "proposal_source.json"):
            self.assertTrue((result["out"] / name).exists(), f"the survey mode writes {name}")
            text = (result["out"] / name).read_text(encoding="utf-8")
            for token in STEMS + NAMES_OF_PAGES + ["stemL1", "stemL2", "benchproj", "benchsite"]:
                self.assertFalse(has_token(text, token), f"{name} holds {token}")
            self.assertNotRegex(text, re.compile(r"@pg", re.IGNORECASE))
        self.assertTrue(has_token((result["out"] / "unmapped.json").read_text(encoding="utf-8"), "benchlate"))


if __name__ == "__main__":
    unittest.main()
