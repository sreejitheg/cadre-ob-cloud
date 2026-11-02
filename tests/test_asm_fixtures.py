"""The synthetic `asm-*` fixtures validate against the manager's schemas (ARCH-WFB-01 revision B8 Table 105).

The three schemas are copies of WorkflowBuilder's `src/wfb_blocks/migration/schemas/wfb.migration.<name>-1.json` at
WorkflowBuilder commit `4e6d5cd` (branch `claude/s10-d-model-stages-af902d`, S10-D), kept in `tests/fixtures/schemas/`.
The manager's schemas govern; a difference is changed here, not there."""
import json
import unittest
from pathlib import Path

import jsonschema

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SOURCE_COMMIT = "4e6d5cd"
ARGS = {"understanding": ["asm-understanding-overview.json", "asm-understanding-pumpstation.json",
                          "asm-understanding-pump01-fp.json", "asm-understanding-seq01-sp.json"],
        "faceplates": ["asm-faceplates.json"],
        "design": ["asm-design-overview.json", "asm-design-pumpstation.json"]}
TABLES = "ctig.tables-1.json"       # ctig's schema, Citect-Ignition-Migrator 95fa79c (the `tags` map)


def schema(name: str) -> dict:
    return json.loads((FIXTURES / "schemas" / f"wfb.migration.{name}-1.json").read_text(encoding="utf-8"))


class FixtureSchemaTests(unittest.TestCase):
    def test_every_fixture_validates_against_its_schema(self):
        for name, files in ARGS.items():
            v = jsonschema.Draft202012Validator(schema(name))
            for f in files:
                doc = json.loads((FIXTURES / f).read_text(encoding="utf-8"))
                errors = [f"{'/'.join(map(str, e.path))}: {e.message[:140]}" for e in v.iter_errors(doc)]
                self.assertEqual(errors[:5], [], f)

    def test_the_tables_fixture_validates_against_ctigs_schema(self):
        v = jsonschema.Draft202012Validator(json.loads((FIXTURES / "schemas" / TABLES).read_text(encoding="utf-8")))
        doc = json.loads((FIXTURES / "asm-tables.json").read_text(encoding="utf-8"))
        self.assertEqual([f"{'/'.join(map(str, e.path))}: {e.message[:140]}" for e in v.iter_errors(doc)][:5], [])

    def test_every_asm_fixture_of_the_three_kinds_is_covered(self):
        covered = {f for files in ARGS.values() for f in files}
        found = {p.name for p in FIXTURES.glob("asm-*.json")
                 if p.name.split("-")[1].removesuffix(".json") in ("understanding", "design", "faceplates")}
        self.assertEqual(found, covered)

    def test_the_copies_name_their_ids_and_source(self):
        for name in ARGS:
            self.assertEqual(schema(name)["$id"], f"wfb.migration.{name}/1")
        self.assertRegex(SOURCE_COMMIT, r"^[0-9a-f]{7}$")


if __name__ == "__main__":
    unittest.main()
