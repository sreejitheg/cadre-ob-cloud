"""Parse the cached OpenStudio documentation pages into a component catalogue.

Two outputs, deliberately different:

* ``--full``: everything, descriptions included. Third-party text, so it is written
  under ``reference/`` (local only, never tracked).
* ``--facts``: interface facts only (component, group, palette name, property name,
  property type, parsed default, parsed enumeration, event names). No vendor prose.
  This one is tracked and feeds the wiki and the gap analysis.

Usage:
    python tools/parse_docs.py --html reference/openstudio-docs/html \
        --full reference/openstudio-docs/catalogue-full.json \
        --facts catalogue/openstudio-interface.json
"""
import argparse
import html as htmllib
import json
import pathlib
import re

GROUP_ORDER = ["Getting Started", "Connector Diagram", "App - OpenBridge", "Input - OpenBridge",
               "Automation - OpenBridge", "Maritime - OpenBridge", "Chart - OpenBridge",
               "Embedding - OpenBridge"]


def clean(fragment: str) -> str:
    t = re.sub(r"<br\s*/?>", " ", fragment)
    t = re.sub(r"<[^>]+>", "", t)
    t = htmllib.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def sidebar(page_html: str) -> dict:
    """Map slug -> (group, title) from the Starlight sidebar of any page."""
    a = page_html.find('<nav class="sidebar')
    b = page_html.find("<main", a)
    nav = page_html[a:b]
    out, group = {}, None
    for m in re.finditer(r'(<summary[^>]*>.*?</summary>)|<a href="(/[^"#]*)"[^>]*>(.*?)</a>', nav, re.S):
        if m.group(1):
            group = clean(m.group(1))
        else:
            slug = m.group(2).strip("/") or "index"
            out.setdefault(slug, (group or "Getting Started", clean(m.group(3))))
    return out


def tables_with_context(body: str):
    """Yield (section_path, header, rows) for each table, with the nearest h2/h3 above it."""
    pos = 0
    h2 = h3 = ""
    for m in re.finditer(r"<h([23])[^>]*>(.*?)</h\1>|<table[^>]*>(.*?)</table>", body, re.S):
        if m.group(1):
            if m.group(1) == "2":
                h2, h3 = clean(m.group(2)), ""
            else:
                h3 = clean(m.group(2))
            continue
        tbl = m.group(3)
        rows = []
        for r in re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, re.S):
            cells = [clean(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
            rows.append(cells)
        if rows:
            yield (h2 + (" / " + h3 if h3 else "")), rows[0], rows[1:]


DEFAULT_RE = re.compile(r"Default:? ([^.]*?)(?:\.(?:\s|$)|$)")


def parse_default(desc: str):
    m = DEFAULT_RE.search(desc)
    if not m:
        return None
    v = m.group(1).strip().strip("`")
    return v[:60]


def parse_enum(desc: str):
    """Pick up 'a, b or c' lists in the first sentence; heuristic, marked as such."""
    first = desc.split(". ")[0]
    first = first.split(":")[-1]
    m = re.search(r"((?:[a-z][\w-]*, )+[a-z][\w-]* or [a-z][\w-]*)", first)
    if not m:
        m = re.search(r"^([a-z][\w-]* or [a-z][\w-]*)\b", first.strip())
    if not m:
        return None
    vals = re.split(r", | or ", m.group(1))
    vals = [v.strip() for v in vals if v.strip()]
    return vals if 2 <= len(vals) <= 16 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--full", required=True)
    ap.add_argument("--facts", required=True)
    a = ap.parse_args()
    root = pathlib.Path(a.html)
    pages = {p.stem: p.read_text(encoding="utf-8") for p in sorted(root.glob("*.html"))}
    nav = sidebar(pages["valve"])
    full, facts = {}, {}
    for slug, page in pages.items():
        m = re.search(r'<div class="sl-markdown-content">(.*)', page, re.S)
        body = m.group(1) if m else ""
        cut = body.find("Found an error or something unclear?")
        body = body[:cut] if cut > 0 else body
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
        title = clean(title_m.group(1)) if title_m else slug
        group, nav_title = nav.get(slug, ("Getting Started", title))
        intro = clean(body)[:600]
        palette = re.search(r"as ([A-Z][\w ()0-9.-]{1,40}?)(?:\.| \(|,| in the)", clean(body))
        props, events, other = [], [], []
        for section, header, rows in tables_with_context(body):
            hl = [h.lower() for h in header]
            if hl[:1] == ["name"] and "description" in hl:
                ti = hl.index("property type") if "property type" in hl else None
                for r in rows:
                    if not r or not r[0]:
                        continue
                    desc = r[1] if len(r) > 1 else ""
                    props.append({"section": section, "name": r[0], "description": desc,
                                  "type": (r[ti] if ti is not None and ti < len(r) else None),
                                  "default": parse_default(desc), "enum": parse_enum(desc)})
            elif hl[:1] == ["event"]:
                for r in rows:
                    if r and r[0]:
                        events.append({"name": r[0], "description": r[1] if len(r) > 1 else "",
                                       "eventObject": r[2] if len(r) > 2 else ""})
            else:
                other.append({"section": section, "header": header, "rows": rows})
        full[slug] = {"slug": slug, "title": title, "navTitle": nav_title, "group": group,
                      "url": f"https://docs.openstudio.no/{'' if slug == 'index' else slug + '/'}",
                      "intro": intro, "properties": props, "events": events, "otherTables": other}
        facts[slug] = {"slug": slug, "title": nav_title, "group": group,
                       "url": full[slug]["url"],
                       "properties": [{k: p[k] for k in ("section", "name", "type", "default", "enum")}
                                      for p in props],
                       "events": [e["name"] for e in events]}
    order = {g: i for i, g in enumerate(GROUP_ORDER)}
    keyf = lambda kv: (order.get(kv[1]["group"], 99), kv[0])
    full = dict(sorted(full.items(), key=keyf))
    facts = dict(sorted(facts.items(), key=keyf))
    pathlib.Path(a.full).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.facts).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.full).write_text(json.dumps(full, indent=1, ensure_ascii=False), encoding="utf-8")
    meta = {"source": "https://docs.openstudio.no (sitemap, 137 pages, read 2026-10-07)",
            "note": "Interface facts only: names, property types, parsed defaults and enumerations. "
                    "Defaults and enumerations are parsed from prose by heuristic and are marked so.",
            "parsed": {"default": "heuristic", "enum": "heuristic"}}
    pathlib.Path(a.facts).write_text(json.dumps({"meta": meta, "components": facts}, indent=1,
                                                ensure_ascii=False), encoding="utf-8")
    n_props = sum(len(v["properties"]) for v in facts.values())
    n_ev = sum(len(v["events"]) for v in facts.values())
    print(f"pages {len(facts)}  properties {n_props}  events {n_ev}")
    by_group = {}
    for v in facts.values():
        by_group.setdefault(v["group"], 0)
        by_group[v["group"]] += 1
    print(json.dumps(by_group, indent=0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
