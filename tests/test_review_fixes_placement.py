"""Regression tests of the cold review's findings 2, 3, 5, 6, 8 and 9 on the placement tool (NOTE-WFB-10 sections 9.2
item 3 and 11.4 items 1 to 5): `tools/hmi/library_gaps.py` and `tools/hmi/placement_survey.py`.

    2  a reviewed or approved map row whose element is null or not in the elements list is an input fault, never a wrap
    3  release mode refuses a draft survey (`approval` null)
    5  page mode with `--project-survey` and no `--openbridge-map` is an input fault
    6  a `--prior-local` or `--late` file of another schema is refused
    8  survey mode refuses a tree whose map, elements list or profile differs from HEAD
    9  stemless survey instances absorb design devices that match no stemmed instance

Run from the repository root:  python -m unittest discover -s tests
Names are synthetic; nothing here needs a gateway or a browser.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump  # noqa: E402
from survey_support import (CATALOGUE, ELEMENTS, MODULE, PROFILE, REAL_MAP, ctig_survey, library_head, load_json,  # noqa: E402
                            make_map, release_argv, row, run, standard_kinds, survey_argv)
from test_library_gaps_features import design  # noqa: E402
from test_library_gaps_project_survey import (PageCase, device_row, kind_entry, local_entry,  # noqa: E402
                                              survey_doc)

from hmi import provenance  # noqa: E402


COUNTER = [0]


class Case(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.ctig = dump(cls.dir / "ctig.json", ctig_survey(standard_kinds()))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def out(self) -> Path:
        COUNTER[0] += 1
        return self.dir / f"out{COUNTER[0]}"

    def survey(self, mapf=None, profile=None, extra=(), ctig=None, elements=None):
        out = self.out()
        argv = survey_argv(ctig or self.ctig, out, mapf, profile, *extra)
        if elements is not None:
            argv[argv.index("--elements") + 1] = str(elements)
        code, text = run(argv)
        return {"code": code, "text": text, "out": out}

    def refused(self, r, *words):
        self.assertEqual(r["code"], 1, r["text"])
        self.assertFalse((r["out"] / "survey.json").exists(), "a refused run writes no survey")
        for w in words:
            self.assertIn(w, r["text"])


class MapRowElementTests(Case):
    """Finding 2: a placing row names an element of the pinned elements list (11.4 item 1; T3, T15)."""

    def test_a_reviewed_row_with_an_element_that_is_not_in_the_pin_is_an_input_fault_naming_the_row(self):
        mapf = make_map(self.dir / "notinpin.json", [row("benchwrap", "obc-not-in-pin")])
        self.refused(self.survey(mapf), "benchwrap", "obc-not-in-pin")

    def test_an_approved_row_with_an_element_that_is_not_in_the_pin_is_an_input_fault(self):
        mapf = make_map(self.dir / "approved.json", [row("benchwrap", "obc-not-in-pin", state="approved")])
        self.refused(self.survey(mapf), "benchwrap", "obc-not-in-pin")

    def test_a_reviewed_row_with_no_element_is_an_input_fault_and_never_places_openbridge(self):
        mapf = make_map(self.dir / "nullelement.json", [row("benchwrap", None)])
        r = self.survey(mapf)
        self.refused(r, "benchwrap")

    def test_a_feature_row_with_an_element_that_is_not_in_the_pin_is_an_input_fault_naming_the_feature(self):
        mapf = make_map(self.dir / "feature.json", [row("pump", "obc-not-in-pin", feature="member:benchLocalMember")])
        self.refused(self.survey(mapf), "pump", "member:benchLocalMember")

    def test_a_proposed_row_is_not_checked_because_it_never_places(self):
        mapf = make_map(self.dir / "proposed.json", [row("benchwrap", "obc-not-in-pin", state="proposed")])
        r = self.survey(mapf)
        self.assertEqual(r["code"], 0, r["text"])

    def test_a_reviewed_row_with_a_pinned_element_still_places(self):
        mapf = make_map(self.dir / "honest.json", [row("benchwrap", "obc-switch")])
        r = self.survey(mapf)
        self.assertEqual(r["code"], 0, r["text"])
        kinds = {k["kind"]: k for k in load_json(r["out"] / "survey.json")["kinds"]}
        self.assertEqual(kinds["benchwrap"]["placement"], "openbridge")

    def test_release_mode_refuses_a_row_with_no_element(self):
        mapf = make_map(self.dir / "honest-release.json", [row("benchwrap", "obc-switch")])
        made = self.survey(mapf, extra=["--changes", dump(self.dir / "changes.json", {"changes": []})])
        self.assertEqual(made["code"], 0, made["text"])
        bad = make_map(self.dir / "bad-release.json", [row("benchwrap", None)])
        out = self.out()
        code, text = run(release_argv(made["out"] / "survey.json", out, bad))
        self.assertEqual(code, 1, text)
        self.assertFalse((out / "gaps.json").exists())
        self.assertIn("benchwrap", text)

    def test_release_mode_refuses_a_row_whose_element_is_not_in_the_list_when_the_list_is_given(self):
        mapf = make_map(self.dir / "honest-release2.json", [row("benchwrap", "obc-switch")])
        made = self.survey(mapf, extra=["--changes", dump(self.dir / "changes2.json", {"changes": []})])
        bad = make_map(self.dir / "bad-release2.json", [row("benchwrap", "obc-not-in-pin")])
        out = self.out()
        code, text = run(release_argv(made["out"] / "survey.json", out, bad, None, "--elements", ELEMENTS))
        self.assertEqual(code, 1, text)
        self.assertIn("obc-not-in-pin", text)


class DraftReleaseTests(Case):
    """Finding 3: release mode refuses a survey whose `approval` is not an object (11.4 item 4; T3)."""

    def test_a_draft_survey_is_refused_in_release_mode(self):
        mapf = make_map(self.dir / "draft.map.json", [row("benchwrap", "obc-switch")])
        made = self.survey(mapf)
        draft = load_json(made["out"] / "survey.json")
        self.assertIsNone(draft["approval"])
        out = self.out()
        code, text = run(release_argv(made["out"] / "survey.json", out, mapf))
        self.assertEqual(code, 1, text)
        self.assertFalse((out / "gaps.json").exists(), "a draft survey releases nothing")
        self.assertRegex(text.lower(), r"draft|approval")

    def test_a_final_survey_is_still_released(self):
        mapf = make_map(self.dir / "final.map.json", [row("benchwrap", "obc-switch")])
        made = self.survey(mapf, extra=["--changes", dump(self.dir / "final.changes.json", {"changes": []})])
        self.assertEqual(made["code"], 0, made["text"])
        out = self.out()
        code, text = run(release_argv(made["out"] / "survey.json", out, mapf))
        self.assertEqual(code, 0, text)


class SurveyFileSchemaTests(Case):
    """Finding 6: `--prior-local` and `--late` files carry the schema they are read as (11.4 item 3; T7)."""

    def test_a_prior_local_file_of_another_schema_is_refused(self):
        wrong = dump(self.dir / "prior-wrong.json", {"schema": "cadre-hmi-library-gaps/2", "kinds": [], "local": []})
        mapf = make_map(self.dir / "p.map.json", [])
        self.refused(self.survey(mapf, extra=["--prior-local", wrong]), "prior-wrong.json")

    def test_a_prior_local_file_of_an_unknown_schema_is_refused(self):
        wrong = dump(self.dir / "prior-unknown.json", {"schema": "something/9", "kinds": [], "local": []})
        mapf = make_map(self.dir / "p2.map.json", [])
        self.refused(self.survey(mapf, extra=["--prior-local", wrong]), "prior-unknown.json")

    def test_a_late_file_of_another_schema_is_refused(self):
        wrong = dump(self.dir / "late-wrong.json", {"schema": "cadre-hmi-project-survey/1", "kinds": [], "late": []})
        mapf = make_map(self.dir / "l.map.json", [])
        self.refused(self.survey(mapf, extra=["--late", wrong]), "late-wrong.json")

    def test_a_late_file_of_the_right_schema_is_read(self):
        right = dump(self.dir / "late-right.json", {"schema": "cadre-hmi-library-gaps/2", "late": []})
        mapf = make_map(self.dir / "l2.map.json", [])
        r = self.survey(mapf, extra=["--late", right])
        self.assertEqual(r["code"], 0, r["text"])


class PageModeMapTests(PageCase):
    """Finding 5 and finding 2 in page mode (11.4 items 1 and 5)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.late_model = dump(cls.dir / "rv.model.json", {
            "schema": "cadre-hmi-asm-model/1", "mapping": [], "devices": {"MAP01": {"tag": "MAP01", "kind": "x", "type": "x"}}})

    def run_page(self, extra):
        out = self.out()
        doc = design([], [device_row("MAP01", "benchmapped")])
        argv = ["--model", str(self.late_model), "--design", str(self.put(doc, "design")),
                "--descriptor-schema", str(self.descriptor_schema), "--catalogue", str(CATALOGUE),
                "--profile", str(PROFILE), "--module", str(MODULE), "--out", str(out),
                "--project-survey", str(self.put(survey_doc())), *map(str, extra)]
        code, text = run(argv)
        return {"code": code, "text": text, "out": out}

    def test_project_survey_without_a_map_is_an_input_fault(self):
        r = self.run_page([])
        self.assertEqual(r["code"], 1, r["text"])
        self.assertIn("--openbridge-map", r["text"])
        self.assertFalse((r["out"] / "gaps.json").exists())

    def test_project_survey_with_a_map_is_read(self):
        mapf = make_map(self.dir / "pm.map.json", [row("benchmapped", "obc-switch")])
        r = self.run_page(["--openbridge-map", mapf])
        self.assertEqual(r["code"], 0, r["text"])

    def test_a_reviewed_row_with_no_element_is_an_input_fault_in_page_mode(self):
        mapf = make_map(self.dir / "pm.null.map.json", [row("benchmapped", None)])
        r = self.run_page(["--openbridge-map", mapf])
        self.assertEqual(r["code"], 1, r["text"])
        self.assertIn("benchmapped", r["text"])
        self.assertFalse((r["out"] / "gaps.json").exists())

    def test_a_reviewed_row_with_an_element_outside_the_given_list_is_an_input_fault_in_page_mode(self):
        mapf = make_map(self.dir / "pm.pin.map.json", [row("benchmapped", "obc-not-in-pin")])
        r = self.run_page(["--openbridge-map", mapf, "--elements", ELEMENTS])
        self.assertEqual(r["code"], 1, r["text"])
        self.assertIn("obc-not-in-pin", r["text"])


class TreeStateTests(Case):
    """Finding 8: survey mode records `library_commit` as the tree's state, so a tree whose map, elements list or
    profile differs from HEAD is refused (11.4 item 2; T3). A temporary repository stands for the library."""

    FILES = {"module/openbridge-map.json": REAL_MAP, "module/openbridge-elements.json": ELEMENTS,
             "library/profile.json": PROFILE}

    def git(self, *args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.autocrlf=false",
                        "-c", "commit.gpgsign=false", *args], cwd=self.repo, check=True, capture_output=True, text=True)

    def setUp(self):
        COUNTER[0] += 1
        self.repo = self.dir / f"repo{COUNTER[0]}"
        for rel, src in self.FILES.items():
            dest = self.repo / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
        (self.repo / "other.txt").write_text("x\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "tree")
        patch = mock.patch.object(provenance, "ROOT", self.repo)
        patch.start()
        self.addCleanup(patch.stop)

    def run_in_repo(self):
        out = self.out()
        argv = ["--survey", str(self.ctig), "--catalogue", str(CATALOGUE), "--profile",
                str(self.repo / "library/profile.json"), "--module", str(MODULE), "--openbridge-map",
                str(self.repo / "module/openbridge-map.json"), "--elements",
                str(self.repo / "module/openbridge-elements.json"), "--out", str(out)]
        code, text = run(argv)
        return {"code": code, "text": text, "out": out}

    def test_a_clean_tree_is_surveyed_and_the_commit_is_its_head(self):
        r = self.run_in_repo()
        self.assertEqual(r["code"], 0, r["text"])
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, capture_output=True, text=True).stdout.strip()
        self.assertEqual(load_json(r["out"] / "survey.json")["library_commit"], head)

    def test_a_map_that_differs_from_head_is_refused(self):
        f = self.repo / "module/openbridge-map.json"
        f.write_text(f.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        r = self.run_in_repo()
        self.refused(r, "openbridge-map.json")

    def test_an_elements_list_that_differs_from_head_is_refused(self):
        f = self.repo / "module/openbridge-elements.json"
        f.write_text(f.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.refused(self.run_in_repo(), "openbridge-elements.json")

    def test_a_profile_that_differs_from_head_is_refused(self):
        f = self.repo / "library/profile.json"
        f.write_text(f.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.refused(self.run_in_repo(), "profile.json")

    def test_a_staged_change_to_the_map_is_refused_too(self):
        f = self.repo / "module/openbridge-map.json"
        f.write_text(f.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.git("add", "module/openbridge-map.json")
        self.refused(self.run_in_repo(), "openbridge-map.json")

    def test_another_changed_or_untracked_file_does_not_refuse(self):
        (self.repo / "other.txt").write_text("changed\n", encoding="utf-8")
        (self.repo / "untracked.txt").write_text("new\n", encoding="utf-8")
        r = self.run_in_repo()
        self.assertEqual(r["code"], 0, r["text"])

    def test_files_outside_the_repository_are_not_judged_against_head(self):
        mapf = make_map(self.dir / f"outside{COUNTER[0]}.json", [])
        r = self.survey(mapf)
        self.assertEqual(r["code"], 0, r["text"])


class StemlessAbsorptionTests(PageCase):
    """Finding 9: a stemless survey instance absorbs one design device that matches no stemmed instance (9.2 item 3)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tags = ["UPS01", "UPS02", "UPS03", "UPS08", "UPS09"]
        cls.sl_model = dump(cls.dir / "sl.model.json", {
            "schema": "cadre-hmi-asm-model/1", "mapping": [],
            "devices": {t: {"tag": t, "kind": "x", "type": "x"} for t in tags}})
        cls.sl_map = make_map(cls.dir / "sl.map.json", [])

    def late_run(self, devices, survey):
        out = self.out()
        doc = design([], [device_row(d, "ups") for d in devices])
        argv = ["--model", str(self.sl_model), "--design", str(self.put(doc, "design")),
                "--descriptor-schema", str(self.descriptor_schema), "--catalogue", str(CATALOGUE),
                "--profile", str(PROFILE), "--module", str(MODULE), "--out", str(out),
                "--project-survey", str(self.put(survey)), "--openbridge-map", str(self.sl_map)]
        return self.page_run(argv, out)

    def survey(self, stems, local_max=1):
        return survey_doc([kind_entry("ups", "local", len(stems))], [local_entry("ups", s) for s in stems],
                          local_max=local_max)

    def sources(self, r):
        return [e["source"] for e in r["doc"]["local"] if e["kind"] == "ups"]

    def test_a_kind_of_stemless_survey_instances_matches_as_many_design_devices_with_no_late_rule(self):
        r = self.late_run(["UPS01", "UPS02"], self.survey([None, None]))
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(r["doc"]["late"], [], "two stemless survey instances cover two design devices")
        self.assertEqual(self.sources(r), ["survey", "survey"])

    def test_a_design_device_beyond_the_stemless_instances_is_late_rule_second(self):
        r = self.late_run(["UPS01", "UPS02", "UPS03"], self.survey([None, None]))
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(len(r["doc"]["late"]), 1)
        e = r["doc"]["late"][0]
        self.assertEqual((e["kind"], e["rule"], e["status"], e["count"]), ("ups", "second", "accepted", 1))
        self.assertEqual(sorted(self.sources(r)), ["late", "survey", "survey"])

    def test_the_stemless_instance_absorbs_the_first_device_of_the_design_that_matches_no_stemmed_instance(self):
        r = self.late_run(["UPS09", "UPS01", "UPS08"], self.survey(["ups01", None]))
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(len(r["doc"]["late"]), 1)
        e = r["doc"]["late"][0]
        self.assertEqual((e["rule"], e["count"]), ("second", 1))
        self.assertEqual([s.lower() for s in e["stems"]], ["ups08"], "UPS09 is first in devices[] and is absorbed")
        self.assertEqual(sorted(self.sources(r)), ["late", "survey", "survey"])

    def test_a_stemmed_instance_still_wins_over_a_stemless_one_for_its_own_device(self):
        r = self.late_run(["UPS01"], self.survey([None, "ups01"]))
        self.assertEqual(r["doc"]["late"], [])
        self.assertEqual(self.sources(r), ["survey"])

    def test_a_stemless_survey_kind_with_no_design_device_is_not_late(self):
        r = self.late_run(["UPS01"], self.survey([None, None]))
        self.assertEqual(r["doc"]["late"], [])


if __name__ == "__main__":
    unittest.main()
