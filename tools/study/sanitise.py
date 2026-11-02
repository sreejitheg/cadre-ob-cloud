"""Stage S3: the sanitised corpus Gemini reads (COB-PLAN-03 sections 5.3, 5.4 and 8.2).

First run: harvests identifier candidates into private/identifiers.json (kept by the owner).
Every run: tokenises the cards, manifest, census, cross references and batch plan into
study/corpus/, checks that no token already occurs in the source, runs the leak check, and writes
private/token-review.md for the owner and study/corpus/LEAK-CHECK.json (counts only).
--ref copies the reference pack into study/ref/. --restore writes a de-tokenised copy of wiki/ to
private/wiki-restored/. Parse only; run with `python -I`.

    python -I tools/study/sanitise.py --study F:/repos/Ignition-ASM-Primary [--ref] [--restore]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import studylib as sl  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
IGNITION_WIKI = Path("F:/repos/Ignition-Wiki/wiki")
CADRE_REF = ["wiki/04-navigation-and-frame.md", "wiki/05-component-catalogue.md", "wiki/06-parent-project-and-library.md",
             "wiki/08-generation-and-validation.md", "wiki/13-faceplates-alarm-lists-interlocks.md",
             "library/contracts.json", "library/profile.json", "docs/BRIEF-COB-02-library-sets-programme.md"]
# Excluded tables read for identifiers only, never into the corpus: (table, column, token kind).
HARVEST = [("INTERNALUSERTABLE", "USERNAME", "USER"), ("INTERNALUSERTABLE", "FIRSTNAME", "USER"),
           ("INTERNALUSERTABLE", "LASTNAME", "USER"), ("DATASOURCES", "NAME", "DB"), ("DEVICESETTINGS", "NAME", "DEV"),
           ("SYSPROPS", "SYSTEMNAME", "GATEWAY"), ("OPCSERVERS", "NAME", "OPC")]
HOST_SCAN = ["DATASOURCES", "SYSPROPS", "SECURITYZONES", "WSCONNECTIONSETTINGS", "OPCUACONNECTIONSETTINGS",
             "AUTHPROFILEPROPERTIES_ADHYBRID", "CANARYPROVIDERS", "CANARYCOLLECTORS", "OPCUASERVERSETTINGS",
             "SMTPSETTINGS", "INTERNALUSEREXTRAPROPS"]
HOST = re.compile(r"\b(?=[A-Za-z0-9-]*[A-Za-z])[A-Za-z0-9-]{2,}(?:\.[A-Za-z0-9-]{2,})+\b")
GENERIC_OPC = {"ignition opc ua server", "ignition opc-ua server"}


def harvest(study: sl.Study, z, manifest: dict) -> list:
    """Candidate identifiers with a proposed token; the owner edits the result."""
    codes = study.codenames()
    found = []
    add = lambda text, token, match, source: found.append(
        {"text": text, "token": token, "match": match, "enabled": True, "source": source})
    for real, code in codes["projects"].items():
        add(real, code, "substring", "project name")
    for real, code in codes["providers"].items():
        if not real.startswith("("):
            add(real, code, "substring", "tag provider name")
    for t in manifest.get("custom_themes", []):
        add(t, "THEME_" + re.sub(r"\W", "_", t).upper(), "substring", "custom theme name")
    actors = collections.Counter()
    for n in z.namelist():
        if n.startswith("projects/") and n.endswith("resource.json"):
            try:
                meta = json.loads(z.read(n))
            except ValueError:
                continue
            a = ((meta.get("attributes") or {}).get("lastModification") or {}).get("actor")
            if a:
                actors[a] += 1
    con = sl.open_idb(z, study)
    seen = set()
    counter = collections.Counter()
    def numbered(kind, text, source, match="word"):
        if not text or text.lower() in seen or len(text) < 3:
            return
        seen.add(text.lower())
        counter[kind] += 1
        add(text, f"{kind}_{counter[kind]:02d}", match, source)
    for a in sorted(actors):
        numbered("USER", a, "designer actor in resource metadata")
    for table, col, kind in HARVEST:
        for (v,) in sl.table_rows(con, table, col):
            if isinstance(v, str) and v.strip() and not (kind == "OPC" and v.lower() in GENERIC_OPC):
                numbered(kind, v.strip(), f"{table}.{col}")
    for table in HOST_SCAN:
        for row in sl.table_rows(con, table):
            for v in row:
                if not isinstance(v, str):
                    continue
                for m in sl.EMAIL.finditer(v):
                    numbered("EMAIL", m.group(0), f"{table} value", "substring")
                for m in HOST.finditer(v):
                    h = m.group(0)
                    if not re.fullmatch(r"[\d.]+", h) and not any(s in h.lower() for s in sl.SAFE_HOSTS) \
                            and h.lower() != "opc.tcp" \
                            and not re.fullmatch(r"(?i)(com|net|org|java|javax|jdbc)\.[\w.]+", h):
                        numbered("HOST", h, f"{table} value", "substring")
                for m in sl.IPV4.finditer(v):
                    if m.group(0) not in sl.SAFE_IPS:
                        numbered("IP", m.group(0), f"{table} value", "substring")
    con.close()
    if len(study.backup().stem) >= 8:
        numbered("BACKUP", study.backup().stem, "backup file name", "substring")
    return found


def all_text(folder: Path) -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(folder.rglob("*.json")))


def occurrences(ids: sl.Identifiers, text: str) -> dict:
    return {e["text"]: len(re.findall(re.escape(e["text"]), text, re.I)) for e in ids.entries}


def collisions(ids: sl.Identifiers, text: str) -> list:
    tokens = sorted({e["token"] for e in ids.entries})
    return [t for t in tokens if re.search(rf"(?<![A-Za-z0-9_]){re.escape(t)}(?![A-Za-z0-9_])", text)]


def sanitise(study: sl.Study) -> dict:
    z = sl.open_backup(study.backup())
    manifest = sl.read_json(study.extract / "MANIFEST.json")
    idp = study.private / "identifiers.json"
    if not idp.exists():
        sl.write_json(idp, harvest(study, z, manifest))
        print(f"identifier candidates written to {idp}; review them, then run again")
    z.close()
    ids = sl.Identifiers.load(study)
    source_text = all_text(study.extract / "cards") + (study.extract / "CENSUS.md").read_text(encoding="utf-8")
    # The extractor writes codenames into the cards; they are not source text.
    source_text = re.sub(r'"(project|provider)_code": "[^"]*"', "", source_text)
    clash = collisions(ids, source_text)
    if clash:
        raise SystemExit(f"tokens already present in the source, choose others in {idp}: {clash}")
    corpus = sl.fresh_dir(study.corpus)
    for p in sorted((study.extract / "cards").rglob("*.json")):
        card = sl.read_json(p)
        sl.write_json(corpus / "cards" / p.parent.name / p.name, ids.tokenise_json(card))
    # The manifest: included entries by tokenised name; excluded entries by kind, counted.
    excl = collections.Counter((e["kind"], e["reason"]) for e in manifest["entries"] if not e["included"])
    clean = {"backup": {"file": "ASMP.gwbk", "version": manifest["backup"]["version"],
                        "backup_type": manifest["backup"]["backup_type"], "timestamp": manifest["backup"]["timestamp"]},
             "included_entries": [ids.tokenise(e["name"]) for e in manifest["entries"] if e["included"]],
             "excluded_entries": [{"kind": k, "reason": r, "count": n} for (k, r), n in sorted(excl.items())],
             "tables": [{"name": t["name"], "rows": t["rows"], "included": t["included"]} for t in manifest["tables"]],
             "counts": ids.tokenise_json(manifest["counts"]),
             "cards": dict(collections.Counter(p.parent.name for p in (corpus / "cards").rglob("*.json")))}
    sl.write_json(corpus / "MANIFEST.json", clean)
    census = (study.extract / "CENSUS.md").read_text(encoding="utf-8")
    census = re.sub(r"SHA-256 [0-9a-f]{64}", "SHA-256 recorded in the intake record", census)
    sl.write_text(corpus / "CENSUS.md", ids.tokenise(census))
    for name in ("xref.json", "BATCHES.json"):
        sl.write_json(corpus / name, ids.tokenise_json(sl.read_json(study.extract / name)))
    # Leak check over everything written.
    hits = []
    for p in sorted(corpus.rglob("*")):
        if p.is_file():
            hits += ids.leaks(p.read_text(encoding="utf-8"), str(p.relative_to(corpus)))
    files = sum(1 for p in corpus.rglob("*") if p.is_file())
    sl.write_json(corpus / "LEAK-CHECK.json", {"files": files, "identifiers": len(ids.entries), "hits": len(hits)})
    review(study, ids, source_text, hits)
    return {"files": files, "hits": len(hits), "identifiers": len(ids.entries), "dynamic": len(ids.dynamic)}


def review(study: sl.Study, ids: sl.Identifiers, source_text: str, hits: list) -> None:
    occ = occurrences(ids, source_text)
    lines = ["# Token review (local only)", "",
             "Each identifier the sanitiser replaces, its token and its occurrences in the extract. Add any",
             "missing identifier to `identifiers.json`, set `enabled` false for one that is not identifying,",
             "and run the sanitiser again. Approving this list is the stage S3 gate (NEEDS N-ASMP-1).", "",
             "| Identifier | Token | Match | Source | Occurrences |", "|---|---|---|---|---|"]
    lines += [f"| {e['text']} | {e['token']} | {e.get('match', 'substring')} | {e.get('source', '')} | {occ[e['text']]} |"
              for e in ids.entries]
    lines += ["", "## Values replaced as found", "", "| Value | Token |", "|---|---|"]
    lines += [f"| {v} | {t} |" for v, t in sorted(ids.dynamic.items(), key=lambda kv: kv[1])]
    codes = collections.Counter(re.findall(r"\b[A-Z]{2,}[A-Z0-9]*\d{2,}[A-Z0-9]*\b", source_text))
    lines += ["", "## Code-like Strings Left As They Are (top 40)", "",
              "Instrument and equipment tags are kept; any that identify a site belong in `identifiers.json`.", "",
              ", ".join(f"{c} ({n})" for c, n in codes.most_common(40)), "",
              f"## Leak Check", "", f"{len(hits)} hits."]
    lines += [f"- {h['where']}: {h['identifier']}: `{h['context']}`" for h in hits[:200]]
    sl.write_text(study.private / "token-review.md", "\n".join(lines) + "\n")


def reference_pack(study: sl.Study) -> int:
    dest = sl.fresh_dir(study.ref)
    n = 0
    for p in sorted(IGNITION_WIKI.glob("*.md")):
        shutil.copy2(p, dest / "ignition-wiki" / p.name) if (dest / "ignition-wiki").exists() else \
            ((dest / "ignition-wiki").mkdir(parents=True), shutil.copy2(p, dest / "ignition-wiki" / p.name))
        n += 1
    (dest / "cadre").mkdir(parents=True, exist_ok=True)
    for rel in CADRE_REF:
        shutil.copy2(REPO / rel, dest / "cadre" / Path(rel).name)
        n += 1
    tokens = REPO / "library" / "tokens"
    if tokens.exists():
        shutil.copytree(tokens, dest / "cadre" / "tokens")
        n += sum(1 for _ in (dest / "cadre" / "tokens").rglob("*") if _.is_file())
    return n


def restore(study: sl.Study) -> int:
    ids = sl.Identifiers.load(study)
    back = {}
    for e in ids.entries:
        back.setdefault(e["token"], e["text"])
    rx = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(t) for t in sorted(back, key=len, reverse=True)) + r")(?![A-Za-z0-9_])")
    dest = sl.fresh_dir(study.private / "wiki-restored")
    n = 0
    for p in sorted((study.root / "wiki").rglob("*.md")):
        out = dest / p.relative_to(study.root / "wiki")
        sl.write_text(out, rx.sub(lambda m: back[m.group(1)], p.read_text(encoding="utf-8")))
        n += 1
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--study", required=True)
    ap.add_argument("--ref", action="store_true", help="also copy the reference pack into study/ref/")
    ap.add_argument("--restore", action="store_true", help="only write a de-tokenised copy of wiki/ to private/")
    a = ap.parse_args(argv)
    study = sl.Study(a.study)
    if a.restore:
        print(f"restored {restore(study)} pages to {study.private / 'wiki-restored'}")
        return 0
    r = sanitise(study)
    print(f"corpus: {r['files']} files, {r['identifiers']} identifiers, {r['dynamic']} values replaced as found, "
          f"leak hits {r['hits']}; review: {study.private / 'token-review.md'}")
    if a.ref:
        print(f"reference pack: {reference_pack(study)} files in {study.ref}")
    return 1 if r["hits"] else 0


if __name__ == "__main__":
    sys.exit(main())
