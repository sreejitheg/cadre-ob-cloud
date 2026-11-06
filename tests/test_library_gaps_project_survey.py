"""Tests of page mode with `--project-survey` of `tools/hmi/library_gaps.py` (NOTE-WFB-10 sections 9.2 items 2 to 6,
10.2 and 11.4; corpus items 1 and 6; threat T7; work package WP-W05). The block's hash checks (9.2 item 1) are not
tested here. Names are synthetic.

Assumptions the note leaves to the builder, flagged in the report: page mode takes the map for the late rule `map` as
`--openbridge-map <file>` (section 10.2's page command lists no map argument); a design device's tag folder is the
`tag` of its model device (its device id here, so either reading holds); a component of `devices[]` that is no
descriptor element and no catalogue view is a kind when a survey is given."""
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump  # noqa: E402
from survey_support import (CATALOGUE, MODULE, PROFILE, REAL_MAP, SURVEY_SCHEMA, library_head, load_json,  # noqa: E402
                            make_map, row as map_row, run, run_cli, sha256_of)
from test_library_gaps import prepare  # noqa: E402
from test_library_gaps_features import CATALOGUE as STUB_CATALOGUE  # noqa: E402
from test_library_gaps_features import SCHEMA as STUB_SCHEMA  # noqa: E402
from test_library_gaps_features import design, row  # noqa: E402

#: The tool as it was when this package began: the reference for corpus item 1. At the source that was the tip of WP-W02
#: (`b2b9b2e`, not in this repository); here it is this line's `main` before the port (`e172346`, tranche T3), whose
#: page mode the port must leave unchanged.
BASE_COMMIT = "e172346"
COMMIT = "c" * 40


def kind_entry(kind, placement, count=1) -> dict:
    return {"kind": kind, "count": count, "stemless": 0, "faceplate_only": 0, "pages": 1,
            "library_resolution": None, "map_row": None, "placement": placement, "placement_source": "table",
            "resolution": None, "features": []}


def survey_doc(kinds=(), local=(), local_max=1) -> dict:
    return {"schema": SURVEY_SCHEMA, "library_commit": COMMIT, "openbridge_release": {"version": "x", "commit": "y"},
            "ctig_survey_sha256": "0" * 64, "local_max": local_max, "pages": {}, "kinds": list(kinds),
            "wraps": [], "shared_gaps": [], "local": list(local), "unclassified": [], "unclassified_features": [],
            "proposals": [], "approval": {"decision": "approve", "changes": [], "refused": []},
            "totals": {"kinds": len(kinds), "instances": 0, "wraps": 0, "shared_gaps": 0, "local": len(list(local)),
                       "unclassified_objects": 0}}


def local_entry(kind, stem, page="PumpStation") -> dict:
    return {"kind": kind, "feature": None, "stem": stem, "page": page}


def device_row(device, component) -> dict:
    return {"device": device, "component": component, "gap": None, "faceplate": None}


class PageCase(unittest.TestCase):
    n = 0

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls._tmp.name)
        cls.model, cls.lst = prepare(cls.dir)
        cls.descriptor_schema = ROOT / "schemas" / "screen-descriptor.schema.json"
        cls.stub_catalogue = dump(cls.dir / "stub.contracts.json", STUB_CATALOGUE)
        cls.stub_schema = dump(cls.dir / "stub.schema.json", STUB_SCHEMA)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def put(self, doc, name="survey") -> Path:
        PageCase.n += 1
        return dump(self.dir / f"{PageCase.n}-{name}.json", doc)

    def out(self) -> Path:
        PageCase.n += 1
        return self.dir / f"out{PageCase.n}"

    def designs_argv(self, out, *extra, module_first=False):
        argv = ["--model", str(self.model), "--designs", str(self.lst), "--catalogue", str(CATALOGUE),
                "--profile", str(PROFILE), "--module", str(MODULE), "--out", str(out), *map(str, extra)]
        return argv + (["--module-first"] if module_first else [])

    def page_run(self, argv, out):
        code, text = run(argv)
        path = out / "gaps.json"
        if not path.exists():
            self.fail(f"gaps.json was not written (exit {code}): {text}")
        return {"code": code, "text": text, "doc": load_json(path), "out": out}

    def with_survey(self, survey, *extra, module_first=False):
        out = self.out()
        path = self.put(survey)
        extra = extra if "--openbridge-map" in extra else (*extra, "--openbridge-map", REAL_MAP)   # finding 5: the map is required
        result = self.page_run(self.designs_argv(out, "--project-survey", path, *extra, module_first=module_first), out)
        result["survey_path"] = path
        return result


class SurveyPlacementTests(PageCase):
    def test_a_survey_local_kind_is_local_and_no_gap_and_the_run_ends_clean(self):
        r = self.with_survey(survey_doc([kind_entry("ups", "local")], [local_entry("ups", "ups01")]))
        self.assertEqual(r["code"], 0, r["text"])
        doc = r["doc"]
        self.assertEqual(doc["schema"], "cadre-hmi-library-gaps/2")
        self.assertEqual({k["kind"]: k["resolution"] for k in doc["kinds"]}["ups"], "local")
        self.assertNotIn("GAP-ups", [g["id"] for g in doc["gaps"]])
        self.assertEqual(doc["open_count"], 0)
        ups = [e for e in doc["local"] if e["kind"] == "ups"]
        self.assertTrue(ups)
        self.assertEqual({e["source"] for e in ups}, {"survey"})
        for e in doc["local"]:
            self.assertEqual(set(e), {"kind", "feature", "instance", "page", "source"})

    def test_the_gap_list_names_the_survey_hash_and_commit(self):
        r = self.with_survey(survey_doc([kind_entry("ups", "local")], [local_entry("ups", "ups01")]))
        self.assertEqual(r["doc"]["survey"], {"sha256": sha256_of(r["survey_path"]), "library_commit": COMMIT})

    def test_an_openbridge_or_shared_gap_kind_not_yet_built_is_unbuilt_and_the_tool_exits_3(self):
        for placement in ("openbridge", "shared_gap"):
            r = self.with_survey(survey_doc([kind_entry("ups", placement)]))
            self.assertEqual(r["code"], 3, (placement, r["text"]))
            kinds = {k["kind"]: k for k in r["doc"]["kinds"]}
            self.assertEqual(kinds["ups"]["resolution"], "unbuilt", placement)
            self.assertNotIn("ups", {e["kind"] for e in r["doc"]["local"]}, "no assembly for an unbuilt kind")

    def test_the_command_line_exits_3_for_an_unbuilt_kind_and_0_for_a_local_one(self):
        out = self.out()
        bad = self.put(survey_doc([kind_entry("ups", "shared_gap")]))
        r = run_cli(self.designs_argv(out, "--project-survey", bad, "--openbridge-map", REAL_MAP))
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        good = self.put(survey_doc([kind_entry("ups", "local")], [local_entry("ups", "ups01")]))
        r = run_cli(self.designs_argv(self.out(), "--project-survey", good, "--openbridge-map", REAL_MAP))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_the_library_places_a_kind_before_the_survey(self):
        base = self.page_run(self.designs_argv(out := self.out(), "--module-first"), out)
        # The survey calls the library's pump a shared gap; the library at the run's commit still draws it.
        r = self.with_survey(survey_doc([kind_entry("ups", "local"), kind_entry("pump", "shared_gap", 3)],
                                        [local_entry("ups", "ups01")]), module_first=True)
        self.assertEqual(r["code"], 0, r["text"])
        after = {k["kind"]: k["resolution"] for k in r["doc"]["kinds"]}
        before = {k["kind"]: k["resolution"] for k in base["doc"]["kinds"]}
        self.assertEqual(after["pump"], before["pump"])
        self.assertEqual(after["pump"], "module")

    def test_a_kind_the_survey_does_not_hold_and_the_designs_use_is_not_a_gap_that_stops_the_run(self):
        r = self.with_survey(survey_doc())
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(r["doc"]["open_count"], 0, "with a survey open_count is 0 by construction")

    def test_a_survey_feature_of_the_designs_is_accepted_late_and_drawn_beside_its_symbol(self):
        out = self.out()
        path = self.put(survey_doc())
        argv = ["--model", str(self.model), "--design", str(self.put(design([row("u1:1", "bar")]), "design")),
                "--descriptor-schema", str(self.stub_schema), "--catalogue", str(self.stub_catalogue),
                "--profile", str(PROFILE), "--module", str(MODULE), "--out", str(out), "--project-survey", str(path),
                "--openbridge-map", str(REAL_MAP)]
        r = self.page_run(argv, out)
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(r["doc"]["open_count"], 0)
        late = [e for e in r["doc"]["late"] if e["rule"] == "feature"]
        self.assertEqual([(e["id"], e["status"]) for e in late], [("GAP-element-bars", "accepted")])
        # The same design with no survey keeps version 1's open gap and exit 2.
        out2 = self.out()
        argv2 = argv[:-4]   # without the survey and the map (finding 5)
        argv2[argv2.index(str(out))] = str(out2)
        r2 = self.page_run(argv2, out2)
        self.assertEqual(r2["code"], 2)
        self.assertEqual(r2["doc"]["schema"], "cadre-hmi-library-gaps/1")


class LateKindTests(PageCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tags = ["LATE01", "LATE02", "ONCE01", "MAP01", "MAP02", "UPS01", "UPS02", "MORE01", "MORE02", "PUMPX1"]
        cls.late_model = dump(cls.dir / "late.model.json", {
            "schema": "cadre-hmi-asm-model/1", "mapping": [],
            "devices": {t: {"tag": t, "kind": "x", "type": "x"} for t in tags}})
        cls.map = make_map(cls.dir / "late.map.json", [map_row("benchmapped", "obc-switch")])

    def late_run(self, devices, survey=None, mapping=(), mapf=None, local_max=None):
        out = self.out()
        doc = design(list(mapping), [device_row(d, c) for d, c in devices])
        sdoc = survey if survey is not None else survey_doc()
        if local_max:
            sdoc["local_max"] = local_max
        argv = ["--model", str(self.late_model), "--design", str(self.put(doc, "design")),
                "--descriptor-schema", str(self.descriptor_schema), "--catalogue", str(CATALOGUE),
                "--profile", str(PROFILE), "--module", str(MODULE), "--out", str(out),
                "--project-survey", str(self.put(sdoc)), "--openbridge-map", str(mapf or self.map)]
        return self.page_run(argv, out)

    def entry(self, r, kind):
        found = [e for e in r["doc"]["late"] if e["kind"] == kind]
        self.assertEqual(len(found), 1, (kind, r["doc"]["late"]))
        return found[0]

    def local_of(self, r, kind, source):
        return [e for e in r["doc"]["local"] if e["kind"] == kind and e["source"] == source]

    def test_rule_twice_a_kind_the_survey_lacks_with_more_than_local_max_instances_is_accepted(self):
        r = self.late_run([("LATE01", "benchlate"), ("LATE02", "benchlate")])
        self.assertEqual(r["code"], 0, r["text"])
        e = self.entry(r, "benchlate")
        self.assertEqual((e["rule"], e["status"], e["count"], e["feature"]), ("twice", "accepted", 2, None))
        self.assertEqual(sorted(s.lower() for s in e["stems"]), ["late01", "late02"])
        self.assertEqual(e["id"], "GAP-benchlate")
        self.assertTrue(e["reason"])
        self.assertEqual(len(self.local_of(r, "benchlate", "late")), 2, "each instance is drawn as a local assembly")
        self.assertEqual(r["doc"]["open_count"], 0)

    def test_rule_twice_counts_distinct_devices_not_mapping_rows(self):
        mapping = [row("u1:1", "benchlate"), row("u1:2", "benchlate"), row("u1:3", "benchlate"),
                   row("u1:4", "benchlate")]
        r = self.late_run([("LATE01", "benchlate"), ("LATE02", "benchlate")], mapping=mapping)
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(self.entry(r, "benchlate")["count"], 2)

    def test_rule_twice_follows_the_surveys_local_max(self):
        r = self.late_run([("LATE01", "benchlate"), ("LATE02", "benchlate")], local_max=2)
        e = self.entry(r, "benchlate")
        self.assertEqual((e["rule"], e["status"], e["count"]), ("once", "local", 2),
                         "two instances do not exceed a local_max of two")

    def test_rule_once_a_kind_the_survey_lacks_with_one_instance_and_no_row_is_local(self):
        r = self.late_run([("ONCE01", "benchonce")])
        self.assertEqual(r["code"], 0, r["text"])
        e = self.entry(r, "benchonce")
        self.assertEqual((e["rule"], e["status"], e["count"]), ("once", "local", 1))
        self.assertEqual(len(self.local_of(r, "benchonce", "late")), 1)
        self.assertEqual(r["doc"]["open_count"], 0)

    def test_rule_map_a_kind_the_survey_lacks_with_a_reviewed_map_row_is_accepted_whatever_its_count(self):
        r = self.late_run([("MAP01", "benchmapped")])
        self.assertEqual(r["code"], 0, r["text"])
        e = self.entry(r, "benchmapped")
        self.assertEqual((e["rule"], e["status"], e["count"]), ("map", "accepted", 1))
        self.assertEqual(len(self.local_of(r, "benchmapped", "late")), 1,
                         "drawn as a local assembly in this run; its wrap comes with the next release")

    def test_a_map_row_that_is_only_proposed_does_not_make_rule_map(self):
        mapf = make_map(self.dir / "proposed.late.map.json", [map_row("benchmapped", "obc-switch", state="proposed")])
        r = self.late_run([("MAP01", "benchmapped")], mapf=mapf)
        self.assertEqual(self.entry(r, "benchmapped")["rule"], "once")

    def test_rule_second_a_survey_local_kind_with_an_instance_the_survey_does_not_know_is_accepted(self):
        survey = survey_doc([kind_entry("ups", "local")], [local_entry("ups", "ups01")])
        r = self.late_run([("UPS01", "ups"), ("UPS02", "ups")], survey=survey)
        self.assertEqual(r["code"], 0, r["text"])
        e = self.entry(r, "ups")
        self.assertEqual((e["rule"], e["status"]), ("second", "accepted"))
        self.assertEqual([s.lower() for s in e["stems"]], ["ups02"])
        self.assertEqual(e["count"], 1)
        self.assertEqual(len(self.local_of(r, "ups", "survey")), 1, "the matched instance is the survey's")
        self.assertEqual(len(self.local_of(r, "ups", "late")), 1, "the unmatched instance is late")
        self.assertEqual(r["doc"]["open_count"], 0)

    def test_a_design_device_matches_a_survey_instance_by_its_stem_ignoring_case(self):
        survey = survey_doc([kind_entry("ups", "local")], [local_entry("ups", "Ups01")])
        r = self.late_run([("UPS01", "ups")], survey=survey)
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(r["doc"]["late"], [], "every design instance matches a survey instance")
        self.assertEqual(len(self.local_of(r, "ups", "survey")), 1)

    def test_a_survey_local_kind_with_a_stem_the_design_does_not_use_is_not_late(self):
        survey = survey_doc([kind_entry("ups", "local", 2)],
                            [local_entry("ups", "ups01"), local_entry("ups", "ups09")])
        r = self.late_run([("UPS01", "ups")], survey=survey)
        self.assertEqual(r["doc"]["late"], [])

    def test_a_late_kind_the_library_resolves_is_never_late(self):
        r = self.late_run([("PUMPX1", "pump")])
        self.assertEqual(r["code"], 0, r["text"])
        self.assertEqual(r["doc"]["late"], [])
        self.assertEqual({k["kind"]: k["resolution"] for k in r["doc"]["kinds"]}["pump"], "library")

    def test_a_late_gap_is_written_into_gaps_json_for_the_next_survey(self):
        r = self.late_run([("LATE01", "benchlate"), ("LATE02", "benchlate")])
        written = load_json(r["out"] / "gaps.json")
        self.assertEqual(written["late"], r["doc"]["late"])
        self.assertEqual({k for e in written["late"] for k in e},
                         {"kind", "feature", "id", "rule", "status", "reason", "count", "stems"})

    def test_a_survey_unbuilt_kind_beside_late_kinds_still_exits_3(self):
        survey = survey_doc([kind_entry("ups", "shared_gap", 3)])
        r = self.late_run([("LATE01", "benchlate"), ("LATE02", "benchlate"), ("UPS01", "ups")], survey=survey)
        self.assertEqual(r["code"], 3, r["text"])


class NoSurveyUnchangedTests(PageCase):
    """Corpus item 1: page mode with no survey gives the same `gaps.json` and `audit.json` as the tool at the base."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        probe = subprocess.run(["git", "cat-file", "-t", BASE_COMMIT], capture_output=True, text=True, cwd=ROOT)
        cls.base_ok = probe.stdout.strip() == "commit"
        cls.base_tool = None
        if cls.base_ok:
            cls.base_dir = cls.dir / "base"
            cls.base_dir.mkdir()
            tar = subprocess.run(["git", "archive", "--format=tar", BASE_COMMIT, "tools"], capture_output=True,
                                 cwd=ROOT).stdout
            archive = cls.dir / "base.tar"
            archive.write_bytes(tar)
            with tarfile.open(archive) as t:
                t.extractall(cls.base_dir)
            cls.base_tool = cls.base_dir / "tools" / "hmi" / "library_gaps.py"

    def setUp(self):
        if not self.base_ok:
            self.skipTest(f"the base commit {BASE_COMMIT} is not in this repository")

    def both(self, argv_of):
        """Run the base tool and the current tool on the same arguments; return both results."""
        base_out, now_out = self.out(), self.out()
        base = subprocess.run([sys.executable, str(self.base_tool), *argv_of(base_out)], capture_output=True,
                              text=True, cwd=ROOT)
        code, _ = run(argv_of(now_out))
        self.assertEqual(code, base.returncode, base.stdout + base.stderr)
        docs = []
        for out in (base_out, now_out):
            doc = load_json(out / "gaps.json")
            doc.pop("provenance", None)
            docs.append((doc, (out / "audit.json").read_bytes()))
        return docs

    def test_page_mode_with_the_page_designs_gives_the_same_files_as_version_1(self):
        for flag in ([], ["--module-first"]):
            (base_doc, base_audit), (doc, audit) = self.both(lambda out: self.designs_argv(out, *flag))
            self.assertEqual(doc, base_doc, flag)
            self.assertEqual(audit, base_audit, flag)
            self.assertEqual(doc["schema"], "cadre-hmi-library-gaps/1")
            for key in ("local", "late", "wraps", "survey"):
                self.assertNotIn(key, doc, "version 1 has no field " + key)

    def test_page_mode_with_a_project_design_gives_the_same_files_as_version_1(self):
        project = self.put(design(
            [row("u1:1", "bar"), row("u1:2", "alarm-panel"), row("u1:3", "Parts/Trend"), row("u1:4", "Parts/RangeBar"),
             row("u1:5", "label"), row("u1:6", "pump")],
            [device_row("D1", "pump"), device_row("D2", "valve")],
            [{"kind": "pump", "tabs": ["home", "config"], "used_by": ["D1"]},
             {"kind": "conveyor", "tabs": ["home"], "used_by": ["C1"]}]), "design")

        def argv(out):
            return ["--model", str(self.model), "--design", str(project), "--designs", str(self.lst),
                    "--descriptor-schema", str(self.stub_schema), "--catalogue", str(self.stub_catalogue),
                    "--profile", str(PROFILE), "--module", str(MODULE), "--out", str(out)]
        (base_doc, base_audit), (doc, audit) = self.both(argv)
        self.assertEqual(doc, base_doc)
        self.assertEqual(audit, base_audit)
        self.assertEqual(doc["schema"], "cadre-hmi-library-gaps/1")
        self.assertTrue(doc["open_count"])

    def test_page_mode_with_accepted_gaps_gives_the_same_files_as_version_1(self):
        accepted = self.put({"accepted": [{"id": "GAP-ups", "reason": "the owner accepts a counted box"}]}, "accepted")
        (base_doc, base_audit), (doc, audit) = self.both(lambda out: self.designs_argv(out, "--accepted", accepted))
        self.assertEqual((doc, audit), (base_doc, base_audit))
        self.assertEqual(doc["open_count"], 0)

    def test_page_mode_with_no_survey_exits_2_for_an_open_gap_never_3(self):
        out = self.out()
        r = self.page_run(self.designs_argv(out), out)
        self.assertEqual(r["code"], 2)


if __name__ == "__main__":
    unittest.main()
