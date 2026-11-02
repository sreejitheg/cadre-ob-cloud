"""Stage S1: census of a gateway backup (COB-PLAN-03 section 6).

Classifies every archive entry and every internal database table as included or excluded, with a
reason, and counts what the study will cover. Writes extract/MANIFEST.json and extract/CENSUS.md.
Exits 1 if any entry is unclassified. Parse only; run with `python -I`.

    python -I tools/study/census.py --study F:/repos/Ignition-ASM-Primary [--reference other.gwbk ...]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import studylib as sl  # noqa: E402

GATEWAY_FILES = {
    "gateway.xml": "gateway configuration: name and settings",
    "ignition.conf": "gateway configuration: service and memory settings",
    "redundancy.xml": "gateway configuration: redundancy addresses",
    "log4j.properties": "gateway configuration: logging",
    "logback.xml": "gateway configuration: logging",
    "jnlp-exports.conf": "gateway configuration: client launch settings",
    "jnlp-opens.conf": "gateway configuration: client launch settings",
    "backupinfo.xml": None,  # included: version facts only
    "db_backup_sqlite.idb": None,  # included in part: see the table classification
}
EXCLUDED_PREFIX = [
    ("certificates/", "certificate", "gateway configuration: certificates and keys"),
    ("gateway-network/", "gateway-network", "gateway configuration: gateway network certificates and connections"),
    ("opcua/", "opcua", "gateway configuration: OPC UA certificates and settings"),
    ("user-lib/jdbc/", "jdbc-driver", "third-party JDBC driver"),
    (f"modules/{sl.PERSPECTIVE}/fonts/", "font", "font files"),
]
# Tables read into cards. Every other table is excluded as gateway configuration; the sanitiser
# reads a few of those for identifiers only, never into the corpus.
INCLUDED_TABLES = {
    "TAGCONFIG": "tag configuration: folders, tags, UDT definitions and instances, alarms, tag scripts",
    "TAGPROVIDERSETTINGS": "tag provider names and types (names become tokens)",
    "IMAGES": "image inventory: path, format and size only, never the data",
    "TAGGROUPS": "tag group names and rates",
    "SCRIPTSETTINGSRECORD": "which project runs gateway scripts",
    "GENERALALARMSETTINGS": "alarm system settings",
    "ALARMNOTIFICATIONPROFILES": "alarm notification profiles",
    "ALARMJOURNALS": "alarm journals",
    "SQLTAGALARMS": "legacy alarm rows",
}
PROJECT_RESOURCE_SKIP = {"thumbnail.png": "view thumbnail image"}


def classify(name: str, custom_themes: set, stock_pylib: set | None) -> tuple[str, bool, str]:
    if name.endswith("/"):
        return "folder-entry", False, "folder entry of the archive"
    if name in GATEWAY_FILES:
        reason = GATEWAY_FILES[name]
        if reason is None:
            return ("backup-info" if name == "backupinfo.xml" else "internal-database"), True, "read by the tools"
        return "gateway-file", False, reason
    for prefix, kind, reason in EXCLUDED_PREFIX:
        if name.startswith(prefix):
            return kind, False, reason
    if name.startswith("user-lib/pylib/"):
        rel = name[len("user-lib/pylib/"):]
        if stock_pylib is not None and rel not in stock_pylib:
            return "pylib-custom", True, "Python library file absent from the reference backups: possibly the integrator's"
        return "pylib", False, "Jython library (stock unless listed as custom)"
    m = re.match(rf"modules/{re.escape(sl.PERSPECTIVE)}/themes/([^/]+)", name)
    if m and "." in m.group(1) and not m.group(1).endswith(".css"):
        return "theme-doc", False, "file in the themes folder that is not a theme"
    if m:
        theme = re.sub(r"\.css$", "", m.group(1))
        if theme in custom_themes:
            return "theme-custom", True, "custom theme"
        return "theme-stock", False, "stock theme"
    if name.startswith(f"modules/{sl.PERSPECTIVE}/icons/"):
        return "icons", True, "icon library"
    if re.match(rf"modules/{re.escape(sl.PERSPECTIVE)}/[^/]+\.digest\.json$", name):
        return "module-digest", False, "checksum digest of module data"
    if name == "projects/conversion-report.txt":
        return "conversion-log", False, "project conversion log"
    m = re.match(r"projects/([^/]+)/(.+)$", name)
    if m:
        rest = m.group(2)
        if rest == "project.json":
            return "project", True, "project definition"
        parts = rest.split("/")
        base = parts[-1]
        if base in PROJECT_RESOURCE_SKIP:
            return "thumbnail", False, PROJECT_RESOURCE_SKIP[base]
        if len(parts) >= 3:
            return "resource:" + "/".join(parts[:2]), True, "project resource"
        return "project-file", True, "project file"
    return "unclassified", False, "no rule"


def custom_theme_names(names: list) -> set:
    found = set()
    for n in names:
        m = re.match(rf"modules/{re.escape(sl.PERSPECTIVE)}/themes/([^/]+)", n)
        if m and ("." not in m.group(1) or m.group(1).endswith(".css")):
            found.add(re.sub(r"\.css$", "", m.group(1)))
    return {t for t in found if t not in sl.STOCK_THEMES}


def stock_pylib_from(references: list) -> set | None:
    if not references:
        return None
    stock = set()
    for ref in references:
        with sl.open_backup(Path(ref)) as rz:
            stock |= {n[len("user-lib/pylib/"):] for n in rz.namelist() if n.startswith("user-lib/pylib/")}
    return stock


def census(study: sl.Study, references: list) -> dict:
    bpath = study.backup()
    z = sl.open_backup(bpath)
    info = sl.backup_info(z)
    sl.require_81(info)
    names = z.namelist()
    themes = custom_theme_names(names)
    stock = stock_pylib_from(references)
    entries = []
    for n in names:
        kind, inc, reason = classify(n, themes, stock)
        entries.append({"name": n, "size": z.getinfo(n).file_size, "kind": kind, "included": inc, "reason": reason})
    con = sl.open_idb(z, study)
    tables = [{"name": t, "rows": n, "included": t in INCLUDED_TABLES,
               "reason": INCLUDED_TABLES.get(t, "gateway configuration: excluded")}
              for t, n in sl.table_counts(con).items()]
    tree = sl.TagTree(con)
    counts = measures(z, names, tree, themes, con)
    con.close()
    z.close()
    manifest = {"backup": {"file": bpath.name, "sha256": sl.sha256_file(bpath), **info},
                "entries": entries, "tables": tables, "custom_themes": sorted(themes),
                "unclassified": [e["name"] for e in entries if e["kind"] == "unclassified"],
                "counts": counts}
    sl.write_json(study.extract / "MANIFEST.json", manifest)
    sl.write_text(study.extract / "CENSUS.md", render(manifest))
    return manifest


def measures(z, names, tree: sl.TagTree, themes: set, con) -> dict:
    C = collections.Counter
    projects = sorted({n.split("/")[1] for n in names if n.startswith("projects/") and n.count("/") >= 2})
    per_project = {}
    for p in projects:
        meta = sl.zjson(z, f"projects/{p}/project.json") if f"projects/{p}/project.json" in names else {}
        views = [n for n in names if n.startswith(f"projects/{p}/{sl.PERSPECTIVE}/views/") and n.endswith("/view.json")]
        styles = [n for n in names if n.startswith(f"projects/{p}/{sl.PERSPECTIVE}/style-classes/") and n.endswith("/style.json")]
        mods = [n for n in names if n.startswith(f"projects/{p}/ignition/script-python/") and n.endswith("/code.py")]
        per_project[p] = {"parent": meta.get("parent"), "inheritable": meta.get("inheritable"),
                          "enabled": meta.get("enabled"), "views": len(views), "style_classes": len(styles),
                          "script_modules": len(mods)}
    kinds = C(tree.kind(r) for r in tree.rows.values())
    alarms = [a for r in tree.rows.values() for a in (r["cfg"].get("alarms") or [])]
    events = C(s.get("eventid", "?") for r in tree.rows.values()
               for s in (r["cfg"].get("eventScripts") or []) if isinstance(s, dict))
    images = C(r[0] for r in sl.table_rows(con, "IMAGES", "TYPE"))
    return {
        "projects": per_project,
        "views": sum(v["views"] for v in per_project.values()),
        "style_classes": sum(v["style_classes"] for v in per_project.values()),
        "script_modules": sum(v["script_modules"] for v in per_project.values()),
        "custom_themes": len(themes),
        "tag_rows": len(tree.rows) + len(tree.unparsed), "tag_rows_unparsed": len(tree.unparsed),
        "tag_kinds": dict(kinds),
        "providers": {str(k): {"name": v["name"], "orphan": v["orphan"]} for k, v in tree.providers.items()},
        "udt_definitions": sum(1 for r in tree.rows.values() if r["cfg"].get("tagType") == "UdtType" and tree.in_types(r)),
        "alarm_definitions": len(alarms),
        "alarm_priorities": dict(C(str(a.get("priority", "(unset)")) for a in alarms)),
        "tag_event_scripts": dict(events),
        "images": {str(k): v for k, v in images.items()},
    }


def render(m: dict) -> str:
    b, c = m["backup"], m["counts"]
    inc = collections.Counter((e["kind"], e["included"]) for e in m["entries"])
    lines = ["# Census", "",
             f"Backup version {b['version']}, type {b['backup_type']}, taken {b['timestamp']}; "
             f"{len(m['entries'])} archive entries; SHA-256 {b['sha256']}.", "",
             "## 1. Archive Entries", "", "| Kind | Included | Entries |", "|---|---|---|"]
    lines += [f"| {k} | {'yes' if i else 'no'} | {n} |" for (k, i), n in sorted(inc.items())]
    lines += ["", f"Unclassified entries: {len(m['unclassified'])}.", "",
              "## 2. Internal Database Tables Read", "", "| Table | Rows | Reason |", "|---|---|---|"]
    lines += [f"| {t['name']} | {t['rows']} | {t['reason']} |" for t in m["tables"] if t["included"]]
    excluded = [t for t in m["tables"] if not t["included"]]
    lines += ["", f"{len(excluded)} other tables ({sum(t['rows'] for t in excluded)} rows) are excluded as gateway configuration.",
              "", "## 3. Projects", "", "| Project | Parent | Inheritable | Enabled | Views | Style classes | Script modules |",
              "|---|---|---|---|---|---|---|"]
    lines += [f"| {p} | {v['parent'] or ''} | {v['inheritable']} | {v['enabled']} | {v['views']} | {v['style_classes']} | {v['script_modules']} |"
              for p, v in c["projects"].items()]
    lines += ["", "## 4. Tags", "",
              f"{c['tag_rows']} configuration rows ({c['tag_rows_unparsed']} not parsed); kinds {json.dumps(c['tag_kinds'])}; "
              f"{c['udt_definitions']} UDT definitions; {c['alarm_definitions']} alarm definitions, priorities "
              f"{json.dumps(c['alarm_priorities'])}; tag event scripts {json.dumps(c['tag_event_scripts'])}.", "",
              "| Provider ID | Name | Orphan (no settings row) |", "|---|---|---|"]
    lines += [f"| {k} | {v['name'] or ''} | {v['orphan']} |" for k, v in c["providers"].items()]
    lines += ["", "## 5. Other", "", f"Custom themes {c['custom_themes']}; images {json.dumps(c['images'])}.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--study", required=True)
    ap.add_argument("--reference", action="append", default=[], help="a public backup whose pylib is stock")
    a = ap.parse_args(argv)
    m = census(sl.Study(a.study), a.reference)
    print(f"census: {len(m['entries'])} entries, {len(m['unclassified'])} unclassified, "
          f"{m['counts']['views']} views, {m['counts']['udt_definitions']} UDT definitions, "
          f"{m['counts']['alarm_definitions']} alarms")
    for n in m["unclassified"][:20]:
        print("  unclassified:", n)
    return 1 if m["unclassified"] else 0


if __name__ == "__main__":
    sys.exit(main())
