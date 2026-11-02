"""Tests of the study toolset (tools/study, COB-124) on a synthetic 8.1 backup."""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "study"))
import census  # noqa: E402
import check  # noqa: E402
import extract  # noqa: E402
import sanitise  # noqa: E402
import studylib as sl  # noqa: E402

P = sl.PERSPECTIVE
SYMBOL = {"params": {"Path": ""}, "propConfig": {"params.Path": {"paramDirection": "input"}}, "props": {},
          "root": {"type": "ia.container.flex", "children": [
              {"type": "ia.display.label", "meta": {"name": "State"},
               "props": {"style": {"classes": "Alarm/High"}},
               "propConfig": {"props.text": {"binding": {"type": "tag", "config": {"mode": "indirect", "tagPath": "{1}/Running",
                                                                                     "references": {"1": "{view.params.Path}"}},
                                                         "transforms": [{"type": "script", "code": "\treturn 'On' if value else 'Off'"}]}}},
               "events": {"dom": {"onClick": {"type": "popup", "scope": "C",
                                              "config": {"id": "fp", "viewPath": "Lib/Motor Faceplate", "viewParams": {}}}}}},
              {"type": "ia.display.view", "props": {"path": "Lib/Missing View"}}]}}
FACEPLATE = {"params": {"Path": ""}, "props": {}, "root": {"type": "ia.container.flex", "children": [
    {"type": "ia.input.button", "events": {"component": {"onActionPerformed": {"type": "script", "scope": "G",
     "config": {"script": "\tsystem.tag.writeBlocking([self.view.params.Path + '/Speed'], [0])\n\tpassword = 'hunter2'"}}}}}]}}


def make_study(root: Path) -> sl.Study:
    study = sl.Study(root)
    for d in (study.source, study.private, study.work):
        d.mkdir(parents=True)
    db = root / "db.idb"
    con = sqlite3.connect(db)
    con.executescript("""
        create table TAGPROVIDERSETTINGS (TAGPROVIDERSETTINGS_ID int, NAME text, PROVIDERID text, DESCRIPTION text,
                                          ENABLED int, TYPEID text, ALLOWBACKFILL int);
        create table TAGCONFIG (ID text, PROVIDERID int, FOLDERID text, CFG text, RANK int, NAME text);
        create table IMAGES (PATH text, TYPE text, DESCRIPTION text, PARENT text, DATA blob, WIDTH int, HEIGHT int, SIZE int);
        create table INTERNALUSERTABLE (USERID int, PROFILEID int, USERNAME text, FIRSTNAME text, LASTNAME text, PASSWORD text);
        create table SYSPROPS (ID int, SYSTEMNAME text);
        create table DATASOURCES (DATASOURCES_ID int, NAME text, CONNECTURL text);
        create table TAGGROUPS (NAME text);
    """)
    con.execute("insert into TAGPROVIDERSETTINGS values (0, 'default', 'x', '', 1, 'STANDARD', 0)")
    rows = [
        ("f1", 0, "_types_", {"name": "Lib", "tagType": "Folder"}, "Lib"),
        ("u1", 0, "f1.a", {"name": "Motor", "tagType": "UdtType", "parameters": {"Path": {"dataType": "String"}}}, "Motor"),
        ("m1", 0, "u1.b", {"name": "Running", "tagType": "AtomicTag", "dataType": "Boolean",
                           "alarms": [{"name": "Fault", "priority": "High",
                                       "displayPath": {"bindType": "UDTParameter", "value": "{Path}"}}],
                           "eventScripts": [{"eventid": "alarmActive", "script": "\tLib.Alarms.count(tagPath)"}]}, "Running"),
        ("m2", 0, "u1.c", {"name": "Speed", "tagType": "AtomicTag", "dataType": "Float4"}, "Speed"),
        ("a0", 0, None, {"name": "Acme", "tagType": "Folder"}, "Acme"),
        ("i1", 0, "a0.d", {"name": "Pump1", "tagType": "UdtInstance", "typeId": "Lib/Motor",
                           "parameters": {"Path": "Acme/Pump1"}}, "Pump1"),
        ("o1", 0, "i1.e", {"value": True}, None),
        ("t1", 0, "a0.f", {"name": "Level", "tagType": "AtomicTag", "dataType": "Float4",
                           "alarms": [{"name": "High", "priority": "Medium", "mode": "AboveValue"}]}, "Level"),
    ]
    con.executemany("insert into TAGCONFIG values (?, ?, ?, ?, 5, ?)",
                    [(i, p, f, json.dumps(c), n) for i, p, f, c, n in rows])
    con.execute("insert into IMAGES values ('Site/AcmeLogo.png', 'PNG', '', null, x'00', 10, 10, 1)")
    con.execute("insert into INTERNALUSERTABLE values (1, 1, 'jsmith', 'John', 'Smithers', 'hash')")
    con.execute("insert into SYSPROPS values (1, 'AcmeGateway')")
    con.execute("insert into DATASOURCES values (1, 'AcmeDB', 'jdbc:sqlserver://10.20.30.40:1433;db=x')")
    con.execute("insert into TAGGROUPS values ('Default')")
    con.commit()
    con.close()
    pj = f"projects/AcmeMaster/{P}"
    files = {
        "backupinfo.xml": "<gateway-backup><version>8.1.17.2022051210</version><backup-type>DATA_ONLY</backup-type>"
                          "<timestamp>2022-06-01 22:00:59</timestamp></gateway-backup>",
        "gateway.xml": "<gateway name='AcmeGateway'/>",
        "certificates/key.pem": "secret",
        "user-lib/pylib/os.py": "# stock",
        f"modules/{P}/themes/light/variables.css": ":root{--a:#fff;}",
        f"modules/{P}/themes/acme-theme/variables.css": ":root{--neutral-10:#333333;}",
        f"modules/{P}/themes/README.md": "readme",
        f"modules/{P}/fonts.digest.json": "{}",
        "projects/AcmeMaster/project.json": json.dumps({"title": "AcmeMaster", "parent": "", "inheritable": True, "enabled": True}),
        f"{pj}/page-config/config.json": json.dumps({"pages": {"/": {"viewPath": "Lib/Motor Symbol", "title": "Home"}}}),
        f"{pj}/page-config/resource.json": json.dumps({"attributes": {"lastModification": {"actor": "jsmith"}}}),
        f"{pj}/views/Lib/Motor Symbol/view.json": json.dumps(SYMBOL),
        f"{pj}/views/Lib/Motor Symbol/thumbnail.png": "png",
        f"{pj}/views/Lib/Motor Faceplate/view.json": json.dumps(FACEPLATE),
        f"{pj}/style-classes/Alarm/High/style.json": json.dumps({"base": {"style": {"color": "#FF0000"}}}),
        "projects/AcmeMaster/ignition/script-python/Lib/Alarms/code.py": "def count(tag):\n\tprint 'counting', tag\n",
    }
    with zipfile.ZipFile(study.source / "AcmeGatewayBackup.gwbk", "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
        z.write(db, "db_backup_sqlite.idb")
        z.writestr("projects/AcmeMaster/", "")
    sl.write_json(study.private / "codenames.json", {"projects": {"AcmeMaster": "P1"}, "providers": {"default": "PROV_A"}})
    sl.write_json(study.work / "batches.config.json", {"b4": {"project": "P1", "prefixes": ["Lib"]}})
    return study


class StudyToolset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.study = make_study(Path(cls.tmp.name) / "study")
        cls.manifest = census.census(cls.study, [])
        extract.main(["--study", str(cls.study.root)])
        cls.cards = {p.stem: sl.read_json(p) for p in (cls.study.extract / "cards").rglob("*.json")}
        sanitise.sanitise(cls.study)                     # first run harvests the identifiers
        ids = sl.read_json(cls.study.private / "identifiers.json")
        ids.append({"text": "Acme", "token": "CLIENT", "match": "substring", "enabled": True})
        sl.write_json(cls.study.private / "identifiers.json", ids)
        cls.result = sanitise.sanitise(cls.study)
        (cls.study.ref / "ignition-wiki").mkdir(parents=True)
        (cls.study.ref / "ignition-wiki" / "26-tag-authoring.md").write_text("## 4. Alarms\n", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def of(self, kind):
        return [c for c in self.cards.values() if c["kind"] == kind]

    def test_census_classifies_every_entry(self):
        m = self.manifest
        self.assertEqual(m["unclassified"], [])
        self.assertEqual(m["custom_themes"], ["acme-theme"])
        kinds = {e["name"]: (e["kind"], e["included"]) for e in m["entries"]}
        self.assertEqual(kinds["certificates/key.pem"], ("certificate", False))
        self.assertEqual(kinds[f"modules/{P}/themes/README.md"], ("theme-doc", False))
        self.assertEqual(m["counts"]["views"], 2)
        self.assertEqual(m["counts"]["udt_definitions"], 1)
        self.assertEqual(m["counts"]["alarm_definitions"], 2)
        self.assertFalse(next(t for t in m["tables"] if t["name"] == "INTERNALUSERTABLE")["included"])

    def test_tag_tree_resolves_compound_parents(self):
        con = sqlite3.connect(self.study.extract / "db" / "db_backup_sqlite.idb")
        tree = sl.TagTree(con)
        self.assertEqual(tree.path(tree.rows["m1"]), "_types_/Lib/Motor/Running")
        self.assertEqual(tree.kind(tree.rows["o1"]), "Override")
        self.assertTrue(tree.inside_instance(tree.rows["o1"]))
        con.close()

    def test_cards_and_cross_references(self):
        self.assertEqual(len(self.of("view")), 2)
        udt = self.of("udt")[0]
        self.assertEqual([m["path"] for m in udt["summary"]["members"]], ["Running", "Speed"])
        self.assertEqual(len(self.of("alarm")), 2)
        inst = self.of("instance")[0]
        self.assertEqual(inst["summary"]["type"], udt["id"])
        sym = next(c for c in self.of("view") if c["path"] == "Lib/Motor Symbol")
        fp = next(c for c in self.of("view") if c["path"] == "Lib/Motor Faceplate")
        self.assertEqual(sym["summary"]["opens_popups"], [fp["id"]])
        self.assertEqual(fp["summary"]["opened_by"], [sym["id"]])
        self.assertEqual(sym["summary"]["udt_hint"][0]["udt"], udt["id"])
        xref = sl.read_json(self.study.extract / "xref.json")
        self.assertEqual([v["path"] for v in xref["missing_views"]], ["Lib/Missing View"])
        scripts = self.of("script")
        locations = {loc for s in scripts for loc in s["summary"]["locations"]}
        self.assertIn("tag event: alarmActive", locations)
        self.assertIn("script transform", locations)
        mod = self.of("module")[0]
        self.assertFalse(mod["summary"]["parses_as_python3"])
        caller = next(s for s in scripts if "tag event: alarmActive" in s["summary"]["locations"])
        self.assertEqual(caller["summary"]["library_calls"], {mod["id"]: ["count"]})
        plan = sl.read_json(self.study.extract / "BATCHES.json")
        self.assertEqual(plan["uncovered"], [])

    def test_sanitised_corpus_has_no_identifier(self):
        self.assertEqual(self.result["hits"], 0)
        text = "\n".join(p.read_text(encoding="utf-8") for p in self.study.corpus.rglob("*") if p.is_file())
        for leaked in ("Acme", "jsmith", "Smithers", "10.20.30.40", "hunter2", "AcmeGatewayBackup"):
            self.assertNotIn(leaked.lower(), text.lower(), leaked)
        self.assertIn("CLIENT", text)
        self.assertIn("REDACTED", text)

    def test_token_collision_is_refused(self):
        ids = sl.read_json(self.study.private / "identifiers.json")
        sl.write_json(self.study.private / "identifiers.json", ids + [{"text": "Pump1", "token": "Speed", "enabled": True}])
        try:
            with self.assertRaises(SystemExit):
                sanitise.sanitise(self.study)
        finally:
            sl.write_json(self.study.private / "identifiers.json", ids)
            sanitise.sanitise(self.study)

    def write_part(self, part, body, cards_read):
        batch = part.split("-")[0]
        spec = sl.read_json(self.study.corpus / "BATCHES.json")["parts"][part]
        folder = self.study.out / batch
        folder.mkdir(parents=True, exist_ok=True)
        for f in folder.glob("*"):
            f.unlink()
        for cid in spec["cards"]:
            page = (f"---\nid: {cid}\nbatch: {part}\nkind: view\ncards_read: [{', '.join(cards_read)}]\nstatus: draft\n---\n"
                    f"# {cid}\n\n## 1. Role\n\n{body.format(cid=cid)}\n\n## Uncertain\n\nNone\n\n## Questions\n\nNone\n")
            (folder / f"{cid}.md").write_text(page, encoding="utf-8")
        (folder / f"{part}.json").write_text(json.dumps({"views": [{"id": c} for c in spec["cards"]]}), encoding="utf-8")
        (folder / "PROGRESS.json").write_text(json.dumps({"done": spec["cards"], "remaining": []}), encoding="utf-8")
        return spec

    def test_check_passes_a_good_part_and_fails_a_bad_one(self):
        c = check.Checker(self.study)
        self.assertEqual(c.corpus(), [])
        part = next(k for k, v in c.batches["parts"].items() if k.startswith("B4-") and v["cards"])
        spec = c.batches["parts"][part]
        everything = spec["cards"] + spec["attached"]
        self.write_part(part, "The view is a symbol [{cid}#/raw/root] [I]. Alarm rules [W:26-tag-authoring.md:4].", everything)
        self.assertEqual(check.Checker(self.study).part(part), [])
        self.write_part(part, "A symbol — for CLIENT Acme [{cid}#/raw/nowhere] [W:26-tag-authoring.md:9].", everything[:1])
        defects = [d for _, d in check.Checker(self.study).part(part)]
        self.assertTrue(any("em dash" in d for d in defects))
        self.assertTrue(any("does not resolve" in d for d in defects))
        self.assertTrue(any("not a heading" in d for d in defects))
        self.assertTrue(any("identifier leak" in d for d in defects))
        if len(everything) > 1:
            self.assertTrue(any("in no page's cards_read" in d for d in defects))


if __name__ == "__main__":
    unittest.main()
