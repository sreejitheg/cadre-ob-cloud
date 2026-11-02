"""Stage S5: mechanical checks of the corpus and of each part Gemini returns (COB-PLAN-03 section 9).

--corpus     the leak check passed and the batch plan covers every card
--part B1-1  coverage, citations, leak, sidecar, progress and format of one part; writes
             study/out/<B>/VERIFY-<part>.md with defects D1 to Dn; exits 1 on any defect
--promote    copy a part that passed to wiki/<B>/ with status verified

    python -I tools/study/check.py --study F:/repos/Ignition-ASM-Primary --part B4-1
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import studylib as sl  # noqa: E402

CITATION = re.compile(r"\[([^\[\]]+)\]")
CARD_REF = re.compile(r"^([A-Z]\d{4})(#.*)?$")   # a pointer may hold spaces: member names do
WIKI_REF = re.compile(r"^W:([^:\s]+\.md):(\d+(?:\.\d+)*)$")
LIB_REF = re.compile(r"^L:([^:#\s]+)(?::(\d+(?:\.\d+)*)|#(\S+))?$")
BANNED = {"\u2014": "em dash", "\u2013": "en dash", "\u2192": "arrow", "\u2190": "arrow", "\u21d2": "arrow"}
FRONT_FIELDS = ("id", "batch", "kind", "cards_read", "status")
PER_ITEM = {"V", "X", "M"}   # kinds whose cards each need a page of their own


def front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        meta[k.strip()] = v
    return meta, text[m.end():]


def binding_rows(body: str) -> int | None:
    """Rows of the first table in the section numbered 5, or None when the page has no such section."""
    m = re.search(r"^##\s+5\.?\s.*?$(.*?)(?=^##\s)", body, re.M | re.S)
    if not m:
        return None
    rows = [ln for ln in m.group(1).splitlines() if ln.strip().startswith("|")]
    rows = [ln for ln in rows if not re.match(r"^\|\s*:?-{3,}", ln.strip())]
    return max(len(rows) - 1, 0) if rows else 0


def headings(path: Path) -> set:
    nums = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{2,4}\s+(\d+(?:\.\d+)*)\.?\s", line)
        if m:
            nums.add(m.group(1))
    return nums


class Checker:
    def __init__(self, study: sl.Study):
        self.study = study
        self.cards = {p.stem: p for p in (study.corpus / "cards").rglob("*.json")}
        self.batches = sl.read_json(study.corpus / "BATCHES.json")
        self.ids = sl.Identifiers.load(study)
        self._docs = {}
        self._heads = {}

    def card(self, cid: str):
        if cid not in self._docs:
            self._docs[cid] = sl.read_json(self.cards[cid])
        return self._docs[cid]

    def corpus(self) -> list:
        defects = []
        leak = sl.read_json(self.study.corpus / "LEAK-CHECK.json")
        if leak.get("hits"):
            defects.append(f"leak check reports {leak['hits']} hits")
        covered = {i for p in self.batches["parts"].values() for i in p.get("cards", []) + p.get("attached", [])}
        missing = sorted(set(self.cards) - covered)
        if missing:
            defects.append(f"{len(missing)} cards in no part: {missing[:10]}")
        unknown = sorted(covered - set(self.cards))
        if unknown:
            defects.append(f"{len(unknown)} cards in the plan but not in the corpus: {unknown[:10]}")
        return defects

    def citation(self, ref: str) -> str | None:
        ref = ref.strip()
        m = CARD_REF.match(ref)
        if m:
            cid, ptr = m.group(1), m.group(2)
            if cid not in self.cards:
                return f"card {cid} does not exist"
            if ptr and ptr != "#":
                try:
                    sl.ptr_resolve(self.card(cid), ptr[1:])
                except KeyError:
                    return f"pointer {ptr} does not resolve in {cid}"
            return None
        m = WIKI_REF.match(ref)
        if m:
            f = self.study.ref / "ignition-wiki" / m.group(1)
            if not f.exists():
                return f"Ignition-Wiki page {m.group(1)} does not exist"
            if m.group(2) not in self._heads.setdefault(f, headings(f)):
                return f"section {m.group(2)} is not a heading of {m.group(1)}"
            return None
        m = LIB_REF.match(ref)
        if m:
            f = self.study.ref / "cadre" / m.group(1)
            if not f.exists():
                return f"Cadre reference {m.group(1)} does not exist"
            if m.group(2) and m.group(2) not in self._heads.setdefault(f, headings(f)):
                return f"section {m.group(2)} is not a heading of {m.group(1)}"
            if m.group(3):
                try:
                    sl.ptr_resolve(sl.read_json(f), "/" + m.group(3).lstrip("/"))
                except (KeyError, ValueError):
                    return f"pointer #{m.group(3)} does not resolve in {m.group(1)}"
            return None
        return "not a citation form of GEMINI.md section 3"

    @staticmethod
    def is_citation_like(inner: str) -> bool:
        first = inner.split(",")[0].split(";")[0].strip()
        return bool(re.match(r"^([A-Z]\d{4}\b|W:|L:|I$)", first))

    def part(self, part: str) -> list:
        batch = part.split("-")[0]
        spec = self.batches["parts"].get(part)
        if spec is None:
            return [("plan", f"part {part} is not in BATCHES.json")]
        folder = self.study.out / batch
        defects = []
        pages = []
        for p in sorted(folder.glob("*.md")):
            if p.name.startswith("VERIFY-"):
                continue
            meta, body = front_matter(p.read_text(encoding="utf-8"))
            if meta.get("batch") == part:
                pages.append((p, meta, body))
        if not pages:
            return [("pages", f"no page in {folder} has batch: {part}")]
        read = set()
        for p, meta, body in pages:
            name = p.name
            for f in FRONT_FIELDS:
                if f not in meta:
                    defects.append((name, f"front matter lacks {f}"))
            cr = meta.get("cards_read", [])
            read |= set(cr if isinstance(cr, list) else [])
            for title in ("## Uncertain", "## Questions"):
                if title not in body:
                    defects.append((name, f"no section {title[3:]}"))
            for ch, what in BANNED.items():
                if ch in body:
                    defects.append((name, f"contains an {what} ({body.count(ch)} times)"))
            for m in CITATION.finditer(body):
                inner = m.group(1)
                if not self.is_citation_like(inner):
                    continue
                for ref in re.split(r"[;,]\s*", inner):
                    if ref.strip() and ref.strip() != "I":
                        err = self.citation(ref)
                        if err:
                            line = body[:m.start()].count("\n") + 1
                            defects.append((name, f"line {line}: [{ref.strip()}]: {err}"))
            for h in self.ids.leaks(body, name):
                defects.append((name, f"identifier leak: {h['identifier']}"))
        expected = set(spec.get("cards", [])) | set(spec.get("attached", []))
        for cid in sorted(expected - read):
            defects.append(("coverage", f"card {cid} is in no page's cards_read"))
        if batch in ("B3", "B4", "B5"):   # the view page's section 5 has one row per binding
            for p, meta, body in pages:
                if p.stem in self.cards and p.stem.startswith("V"):
                    want = self.card(p.stem)["summary"]["binding_count"]
                    got = binding_rows(body)
                    if got is not None and got != want:
                        defects.append((p.name, f"section 5 has {got} binding rows, the card has {want} bindings"))
        names = {p.stem for p, _, _ in pages}
        for cid in spec.get("cards", []):
            if cid[0] in PER_ITEM and batch in ("B3", "B4", "B5", "B6", "B7") and cid not in names:
                defects.append(("coverage", f"card {cid} has no page {cid}.md"))
        sidecar = folder / f"{part}.json"
        if not sidecar.exists():
            defects.append(("sidecar", f"{sidecar.name} is missing"))
        else:
            try:
                text = sidecar.read_text(encoding="utf-8")
                json.loads(text)
                for cid in sorted(set(spec.get("cards", [])) - set(re.findall(r"[A-Z]\d{4}", text))):
                    defects.append(("sidecar", f"card {cid} is not in the sidecar"))
                for h in self.ids.leaks(text, sidecar.name):
                    defects.append(("sidecar", f"identifier leak: {h['identifier']}"))
            except ValueError as e:
                defects.append(("sidecar", f"not valid JSON: {e}"))
        prog = folder / f"PROGRESS-{part}.json"   # one per part: parts of a batch run side by side
        if not prog.exists():
            prog = folder / "PROGRESS.json"
        if not prog.exists():
            defects.append(("progress", f"PROGRESS-{part}.json is missing"))
        else:
            try:
                if json.loads(prog.read_text(encoding="utf-8")).get("remaining"):
                    defects.append(("progress", "PROGRESS.json lists remaining items"))
            except ValueError:
                defects.append(("progress", "PROGRESS.json is not valid JSON"))
        return defects

    def write_verify(self, part: str, defects: list) -> Path:
        batch = part.split("-")[0]
        lines = [f"# Verification of Part {part}", "",
                 f"Mechanical check by `check.py` on {datetime.date.today().isoformat()}: "
                 f"{len(defects)} defects. The sample review of the tier adds its own below.", "",
                 "| Defect | Page | Statement and reason |", "|---|---|---|"]
        lines += [f"| D{i} | {where} | {what} |" for i, (where, what) in enumerate(defects, 1)]
        out = self.study.out / batch / f"VERIFY-{part}.md"
        review = "## Sample Review\n\n(to be added by the reviewer)\n"
        if out.exists() and "## Sample Review" in out.read_text(encoding="utf-8"):
            review = "## Sample Review" + out.read_text(encoding="utf-8").split("## Sample Review", 1)[1]   # a rerun keeps the review
        sl.write_text(out, "\n".join(lines) + "\n\n" + review)
        return out

    def promote(self, part: str) -> int:
        if self.part(part):
            raise SystemExit(f"part {part} has defects; it cannot be promoted")
        batch = part.split("-")[0]
        n = 0
        for p in sorted((self.study.out / batch).glob("*.md")):
            text = p.read_text(encoding="utf-8")
            meta, _ = front_matter(text)
            if meta.get("batch") == part:
                text = re.sub(r"^status: draft$", f"status: verified\nverified: {datetime.date.today().isoformat()} check.py",
                              text, count=1, flags=re.M)
                sl.write_text(self.study.root / "wiki" / batch / p.name, text)
                n += 1
        return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--study", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--corpus", action="store_true")
    g.add_argument("--part")
    g.add_argument("--promote")
    a = ap.parse_args(argv)
    c = Checker(sl.Study(a.study))
    if a.corpus:
        d = c.corpus()
        print(f"corpus: {len(c.cards)} cards, {len(c.batches['parts'])} parts, {len(d)} defects")
        for x in d:
            print("  ", x)
        return 1 if d else 0
    if a.part:
        d = c.part(a.part)
        out = c.write_verify(a.part, d)
        print(f"part {a.part}: {len(d)} defects; {out}")
        return 1 if d else 0
    print(f"promoted {c.promote(a.promote)} pages of {a.promote}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
