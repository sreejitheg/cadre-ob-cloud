"""Shared parts of the study toolset (COB-PLAN-03 section 7).

Parse only: nothing read from a backup is ever executed. Every tool runs under `python -I`.
The layout is that of a study repository (ASMP decision ASMPD-001):

    <study>/source/<one>.gwbk     the backup as received (ignored by git)
    <study>/private/              codenames, identifier map, review lists (ignored)
    <study>/extract/              manifest, census, full-fidelity cards, the internal database (ignored)
    <study>/study/corpus/         the sanitised cards Gemini reads
    <study>/study/ref/            the reference pack (ignored)
    <study>/study/out/            Gemini's drafts, one folder per batch
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
import textwrap
import zipfile
from pathlib import Path

PERSPECTIVE = "com.inductiveautomation.perspective"
# The stock Perspective themes, as found in the public 8.1.36 and 8.1.52 backups (COB-PLAN-03 3.1).
STOCK_THEMES = {"light", "dark", "light-cool", "light-warm", "dark-cool", "dark-warm"}
LETTER = {"project": "P", "page-config": "R", "session": "N", "view": "V", "style": "S", "theme": "T",
          "module": "M", "script": "X", "udt": "U", "instance": "I", "folder": "F", "alarm": "A",
          "images": "G", "provider": "Q"}
KIND_OF_LETTER = {v: k for k, v in LETTER.items()}
CARD_ID = re.compile(r"^[A-Z]\d{4}$")


class Study:
    """Paths of a study repository."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.source = self.root / "source"
        self.private = self.root / "private"
        self.extract = self.root / "extract"
        self.work = self.root / "study"
        self.corpus = self.work / "corpus"
        self.ref = self.work / "ref"
        self.out = self.work / "out"

    def backup(self) -> Path:
        found = sorted(self.source.glob("*.gwbk"))
        if len(found) != 1:
            raise SystemExit(f"expected exactly one .gwbk in {self.source}, found {len(found)}")
        return found[0]

    def codenames(self) -> dict:
        p = self.private / "codenames.json"
        data = read_json(p) if p.exists() else {}
        return {"projects": data.get("projects", {}), "providers": data.get("providers", {})}


# ------------------------------------------------------------------ files

def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def fresh_dir(path: Path) -> Path:
    """An empty folder the tool owns: removed and created again."""
    path = Path(path)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


# ------------------------------------------------------------------ the backup

def open_backup(path: Path) -> zipfile.ZipFile:
    return zipfile.ZipFile(path)


def backup_info(z: zipfile.ZipFile) -> dict:
    text = z.read("backupinfo.xml").decode("utf-8", "replace")
    def tag(name):
        m = re.search(rf"<{name}>(.*?)</{name}>", text, re.S)
        return m.group(1).strip() if m else None
    version = tag("version") or ""
    parts = [int(p) for p in re.findall(r"\d+", version)[:3]] or [0]
    return {"version": version, "major_minor": parts[:2], "backup_type": tag("backup-type"),
            "timestamp": tag("timestamp")}


def require_81(info: dict) -> None:
    if info["major_minor"][:1] != [8] or info["major_minor"][1:2] != [1]:
        raise SystemExit(f"backup version {info['version']}: only the 8.1 layout is measured (COB-PLAN-03 7.1); "
                         "an 8.3 backup stores its configuration differently and needs its own measured reader")


def zjson(z: zipfile.ZipFile, name: str):
    return json.loads(z.read(name).decode("utf-8"))


def ztext(z: zipfile.ZipFile, name: str) -> str:
    return z.read(name).decode("utf-8", "replace")


def open_idb(z: zipfile.ZipFile, study: Study) -> sqlite3.Connection:
    """Extract only the internal database, into an empty folder of its own, and open it read only."""
    dest = fresh_dir(study.extract / "db")
    p = Path(z.extract("db_backup_sqlite.idb", dest))
    return sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)


def table_rows(con: sqlite3.Connection, table: str, columns: str = "*") -> list:
    try:
        return list(con.execute(f'select {columns} from "{table}"'))
    except sqlite3.Error:
        return []


def table_counts(con: sqlite3.Connection) -> dict:
    names = [r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
    return {n: con.execute(f'select count(*) from "{n}"').fetchone()[0] for n in names}


# ------------------------------------------------------------------ JSON pointers

def ptr_escape(key) -> str:
    return str(key).replace("~", "~0").replace("/", "~1")


def ptr_join(base: str, *keys) -> str:
    return base + "".join("/" + ptr_escape(k) for k in keys)


def ptr_resolve(doc, pointer: str):
    """Resolve an RFC 6901 pointer; raises KeyError when it does not exist."""
    if pointer in ("", "#"):
        return doc
    if pointer.startswith("#"):
        pointer = pointer[1:]
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    cur = doc
    for raw in pointer[1:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list):
            if not key.isdigit() or int(key) >= len(cur):
                raise KeyError(pointer)
            cur = cur[int(key)]
        elif isinstance(cur, dict):
            if key not in cur:
                raise KeyError(pointer)
            cur = cur[key]
        else:
            raise KeyError(pointer)
    return cur


# ------------------------------------------------------------------ scripts

SYSTEM_CALL = re.compile(r"\bsystem\.[A-Za-z]+\.[A-Za-z]+")
COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|var\(--[\w-]+\)")


def normalise_script(text: str) -> str:
    lines = [ln.rstrip() for ln in str(text).replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    body = textwrap.dedent("\n".join(lines).expandtabs(4)).strip("\n")
    return body


def script_hash(text: str) -> str:
    return sha256_bytes(normalise_script(text).encode("utf-8"))[:16]


def python_functions(src: str) -> tuple[list, bool]:
    """Function signatures by text, so Jython 2 syntax is no obstacle; the second value says
    whether the module also parses as Python 3."""
    import ast
    sigs = [m.group(1) + "(" + re.sub(r"\s+", " ", m.group(2)).strip() + ")"
            for m in re.finditer(r"^\s*def\s+(\w+)\s*\((.*?)\)\s*:", src, re.M | re.S)]
    try:
        ast.parse(src)
        ok = True
    except SyntaxError:
        ok = False
    return sigs, ok


# ------------------------------------------------------------------ tag tree

class TagTree:
    """The tag configuration of an 8.1 internal database (table TAGCONFIG), as measured on the
    ASMP backup on 2026-10-21: a row's parent is the first segment of its FOLDERID (the rest is
    a second identifier); UDT definitions hang from the literal folder `_types_`; instance
    overrides are rows without a name; a provider is TAGPROVIDERSETTINGS_ID."""

    def __init__(self, con: sqlite3.Connection):
        self.providers = {}
        for pid, name, typ, enabled in table_rows(con, "TAGPROVIDERSETTINGS",
                                                  "TAGPROVIDERSETTINGS_ID, NAME, TYPEID, ENABLED"):
            self.providers[pid] = {"name": name, "type": typ, "enabled": bool(enabled), "orphan": False}
        self.rows, self.unparsed = {}, []
        for rid, prov, folder, cfg, name in table_rows(con, "TAGCONFIG", "ID, PROVIDERID, FOLDERID, CFG, NAME"):
            try:
                d = json.loads(cfg) if cfg else None
            except ValueError:
                d = None
            if not isinstance(d, dict):
                self.unparsed.append({"id": rid, "provider": prov})
                continue
            self.rows[rid] = {"id": rid, "provider": prov, "folder": folder, "cfg": d,
                              "name": name if name is not None else d.get("name")}
        for r in self.rows.values():
            if r["provider"] not in self.providers:
                self.providers[r["provider"]] = {"name": None, "type": None, "enabled": None, "orphan": True}
        self.children = {}
        for r in self.rows.values():
            self.children.setdefault(self.parent(r), []).append(r["id"])
        for ids in self.children.values():
            ids.sort(key=lambda i: (str(self.rows[i]["name"]), i))
        self._path = {}

    def parent(self, r) -> str | None:
        f = r["folder"]
        if f is None:
            return None
        if f == "_types_":
            return "_types_"
        first = f.split(".")[0]
        return first if first in self.rows else "?"

    def kind(self, r) -> str:
        t = r["cfg"].get("tagType")
        if t:
            return t
        return "Override" if r["name"] is None or self.inside_instance(r) else "AtomicTag"

    def ancestors(self, r):
        seen = 0
        p = self.parent(r)
        while p not in (None, "_types_", "?") and seen < 64:
            yield self.rows[p]
            p = self.parent(self.rows[p])
            seen += 1

    def root_marker(self, r) -> str | None:
        p = self.parent(r)
        seen = 0
        while p not in (None, "_types_", "?") and seen < 64:
            p = self.parent(self.rows[p])
            seen += 1
        return p

    def in_types(self, r) -> bool:
        return self.root_marker(r) == "_types_"

    def inside_instance(self, r) -> bool:
        return any(a["cfg"].get("tagType") == "UdtInstance" for a in self.ancestors(r))

    def path(self, r) -> str:
        if r["id"] in self._path:
            return self._path[r["id"]]
        names = [r["name"] if r["name"] is not None else "(override)"]
        names += [a["name"] if a["name"] is not None else "(override)" for a in self.ancestors(r)]
        marker = self.root_marker(r)
        prefix = {"_types_": ["_types_"], "?": ["(orphan)"]}.get(marker, [])
        p = "/".join(prefix + list(reversed(names)))
        self._path[r["id"]] = p
        return p

    def descendants(self, rid: str):
        for c in self.children.get(rid, []):
            yield self.rows[c]
            yield from self.descendants(c)

    def provider_name(self, pid) -> str:
        p = self.providers.get(pid) or {}
        return p.get("name") or f"(provider {pid})"


# ------------------------------------------------------------------ identifiers and leaks

IPV4 = re.compile(r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# A host starts with a letter, a digit or "["; "http://" + {Server} in an expression is no URL.
URL = re.compile(r"\b(?:https?|opc\.tcp|jdbc:[a-z]+|ldaps?)://[A-Za-z0-9\[][^\s\"'<>)\\]*", re.I)
SAFE_HOSTS = ("w3.org", "inductiveautomation.com", "localhost", "127.0.0.1", "0.0.0.0")
SAFE_IPS = {"0.0.0.0", "127.0.0.1", "255.255.255.255", "255.255.255.0"}
SECRET = re.compile(r"(?i)\b(password|passwd|pwd|secret|api_?key|token)\b(\s*[=:]\s*)(['\"])([^'\"]+)\3")


SEPARATOR = r"[\s_./-]?"


class Identifiers:
    """The identifier map of a study: private/identifiers.json, a list of
    {"text", "token", "match": "substring" | "word", "enabled"} kept by the owner."""

    def __init__(self, entries: list):
        self.entries = [e for e in entries if e.get("enabled", True) and e.get("text")]
        self.entries.sort(key=lambda e: len(e["text"]), reverse=True)
        self.rx = []
        for e in self.entries:
            pat = self.pattern(e["text"])
            if e.get("match") == "word":
                pat = rf"(?<![A-Za-z0-9]){pat}(?![A-Za-z0-9])"
            self.rx.append((re.compile(pat, re.I), e["token"]))
        self.dynamic = {}  # IPs, emails, URLs found while tokenising: value -> token

    @staticmethod
    def pattern(text: str) -> str:
        """A space in an identifier also matches no separator or another one, so that
        'North Pit' finds northPit, North_Pit and North-Pit."""
        return re.escape(text).replace(re.escape(" "), SEPARATOR)

    @classmethod
    def load(cls, study: "Study") -> "Identifiers":
        p = study.private / "identifiers.json"
        return cls(read_json(p) if p.exists() else [])

    def _dyn(self, kind: str, value: str) -> str:
        if value not in self.dynamic:
            n = 1 + sum(1 for t in self.dynamic.values() if t.startswith(kind + "_"))
            self.dynamic[value] = f"{kind}_{n:02d}"
        return self.dynamic[value]

    def tokenise(self, s: str) -> str:
        for rx, token in self.rx:
            s = rx.sub(token, s)
        s = URL.sub(lambda m: m.group(0) if any(h in m.group(0).lower() for h in SAFE_HOSTS) else self._dyn("URL", m.group(0)), s)
        s = EMAIL.sub(lambda m: self._dyn("EMAIL", m.group(0)), s)
        s = IPV4.sub(lambda m: m.group(0) if m.group(0) in SAFE_IPS else self._dyn("IP", m.group(0)), s)
        s = SECRET.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}REDACTED{m.group(3)}", s)
        return s

    def tokenise_json(self, obj):
        if isinstance(obj, str):
            return self.tokenise(obj)
        if isinstance(obj, list):
            return [self.tokenise_json(v) for v in obj]
        if isinstance(obj, dict):
            return {self.tokenise(k) if isinstance(k, str) else k: self.tokenise_json(v) for k, v in obj.items()}
        return obj

    def leaks(self, text: str, where: str = "") -> list:
        """Every occurrence of an identifier (also with separators removed, for identifiers of five
        characters or more), and of an unsafe IPv4 address, email address or URL."""
        hits = []
        squashed = re.sub(r"[^a-z0-9]", "", text.lower())
        for e in self.entries:
            t = e["text"]
            if e.get("match") == "word":
                rx = re.compile(rf"(?<![A-Za-z0-9]){self.pattern(t)}(?![A-Za-z0-9])", re.I)
            else:
                rx = re.compile(self.pattern(t), re.I)
            for m in rx.finditer(text):
                hits.append({"where": where, "identifier": t, "context": text[max(0, m.start() - 40):m.end() + 40]})
            key = re.sub(r"[^a-z0-9]", "", t.lower())
            if (e.get("match") != "word" and re.search(r"[a-z]", key) and len(key) >= 5
                    and key in squashed and not rx.search(text)):
                hits.append({"where": where, "identifier": t, "context": "(present with separators removed)"})
        for rx, kind in ((IPV4, "ip"), (EMAIL, "email"), (URL, "url")):
            for m in rx.finditer(text):
                v = m.group(0)
                if (kind == "ip" and v in SAFE_IPS) or (kind == "url" and any(h in v.lower() for h in SAFE_HOSTS)):
                    continue
                hits.append({"where": where, "identifier": f"({kind})", "context": text[max(0, m.start() - 40):m.end() + 40]})
        for m in SECRET.finditer(text):
            if m.group(4) != "REDACTED":
                hits.append({"where": where, "identifier": "(secret)", "context": m.group(1)})
        return hits
