"""Helpers for the tests of the placement tool's survey, release and project-survey modes (NOTE-WFB-10 sections 7.5 to
7.8, 8.2, 9.2, 10.2 and 11.4; work package WP-W05). Synthetic names only: `benchlocal`, `stemP1`, `pgBeta`.

The ctig survey (`ctig.survey/1`, Table 7.2) is written by hand here; ctig is not run."""
import contextlib
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm_support import ROOT, dump  # noqa: E402

from hmi import library_gaps  # noqa: E402

TOOL = ROOT / "tools" / "hmi" / "library_gaps.py"
CATALOGUE = ROOT / "library" / "contracts.json"
PROFILE = ROOT / "library" / "profile.json"
MODULE = ROOT / "module" / "components.json"
REAL_MAP = ROOT / "module" / "openbridge-map.json"
ELEMENTS = ROOT / "module" / "openbridge-elements.json"
SURVEY_SCHEMA = "cadre-hmi-project-survey/1"

#: The pages of the synthetic project and their class. Sorted case-insensitively: pgalpha, pgBeta, pgPop, pgZeta;
#: sorted by code point: pgBeta, pgPop, pgZeta, pgalpha.
PAGES = {"pgalpha": "operator", "pgBeta": "operator", "pgZeta": "operator", "pgPop": "faceplate_source"}
POPUPS = ["PopX"]
#: A reviewed row's properties and states (the map's form), used to prove the release gap's `needed`.
ROW_PROPERTIES = {"on": "checked"}
ROW_STATES = [{"name": "on", "props": {"checked": True}}]


def library_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()


def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run(argv) -> tuple[int, str]:
    """The tool's `main` in process: its exit code and what it printed."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = library_gaps.main([str(a) for a in argv])
    return code, buf.getvalue()


def run_cli(argv) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), *[str(a) for a in argv]], capture_output=True, text=True,
                          cwd=ROOT)


# ----- the ctig survey -------------------------------------------------------------------------------------------

def dev(stem, pages, members=(), unknown=(), unnamed=(), popups=(), key=None) -> dict:
    """A device of `kinds[].devices[]`; `stem` None is a stemless instance (key `@page/id`)."""
    return {"key": key or stem, "stem": stem, "stemless": stem is None, "pages": list(pages),
            "operator_pages": sum(PAGES[p] == "operator" for p in pages), "popups": list(popups),
            "members": list(members), "unnamed": list(unnamed), "unknown_members": list(unknown)}


def kind_row(name, devices, faceplate_only=0) -> dict:
    return {"kind": name, "instances": len(devices), "stemless": sum(1 for d in devices if d["stemless"]),
            "faceplate_only": faceplate_only,
            "pages_operator": len({p for d in devices for p in d["pages"] if PAGES[p] == "operator"}),
            "alarms": 0, "devices": devices}


def ctig_survey(kinds, unclassified=None) -> dict:
    unclassified = unclassified if unclassified is not None else {
        "unclassed_templates": [{"template": "TplA", "instances": 4, "pages": 2}],
        "static_templates": [{"template": "TplS", "kind": "label", "instances": 3, "pages": 1}],
        "no_kind_devices": 2, "stems_not_recovered": 1}
    objects = (sum(t["instances"] for t in unclassified["unclassed_templates"])
               + sum(t["instances"] for t in unclassified["static_templates"]) + unclassified["no_kind_devices"])
    return {
        "schema": "ctig.survey/1", "project": "benchproj", "site": "benchsite",
        "provenance": {"commit": "0" * 40, "command": "python -m ctig survey"},
        "pages": {"total": 5, "decoded": 4, "operator": 3, "faceplate_source": 1, "undecoded": 1},
        "page_class": [{"page": p, "class": c, "why": "default" if c == "operator" else "opener"}
                       for p, c in sorted(PAGES.items(), key=lambda x: x[0].lower())],
        "kinds": kinds,
        "unclassified": unclassified,
        "features_computed": True, "features_reason": None,
        "totals": {"kinds": len(kinds), "instances": sum(k["instances"] for k in kinds),
                   "stemless": sum(k["stemless"] for k in kinds),
                   "faceplate_only": sum(k["faceplate_only"] for k in kinds), "unclassified_objects": objects},
    }


def standard_kinds() -> list[dict]:
    """Nine kinds, deliberately unsorted. Placement with the real catalogue and profile, `local_max` 1 and a map that
    holds a reviewed row for `benchwrap` only:

    pump (3 instances) library, features cmd 3, fault 2, faceplate 2 (resolved), benchSharedMember 3 (shared_gap),
    benchLocalMember 1 (local), unnamed:zq 2; sequence (1) library; benchwrap (1) openbridge; benchshared (3)
    shared_gap; benchtwo (2) shared_gap (local with `local_max` 2); benchrej (2) shared_gap; benchlocal (1, stemless)
    local; benchprop (1) local; benchnull (1) local."""
    return [
        kind_row("sequence", [dev("stemS1", ["pgBeta"])], faceplate_only=1),
        kind_row("pump", [
            dev("stemP1", ["pgZeta", "pgalpha", "pgPop"], members=["cmd", "fault"],
                unknown=["benchSharedMember", "benchLocalMember"], unnamed=["zq"], popups=POPUPS),
            dev("stemP2", ["pgBeta"], members=["cmd"], unknown=["benchSharedMember"], unnamed=["zq"]),
            dev("stemP3", ["pgBeta", "pgZeta"], members=["cmd", "fault"], unknown=["benchSharedMember"],
                popups=POPUPS)]),
        kind_row("benchwrap", [dev("stemW1", ["pgBeta"])]),
        kind_row("benchtwo", [dev("stemB2", ["pgBeta"]), dev("stema2", ["pgalpha"])]),
        kind_row("benchshared", [
            dev("stemH1", ["pgBeta"], unknown=["benchTravel", "benchAlso"], unnamed=["ab"]),
            dev("stemH2", ["pgZeta"], unknown=["benchTravel"], unnamed=["ab"]),
            dev("stemH3", ["pgalpha"], unknown=["benchAlso"], unnamed=["ab"])]),
        kind_row("benchrej", [dev("stemJ2", ["pgBeta"]), dev("stemj1", ["pgZeta"])]),
        kind_row("benchprop", [dev("stemR1", ["pgBeta"])]),
        kind_row("benchnull", [dev("stemN1", ["pgZeta"])]),
        kind_row("benchlocal", [dev(None, ["pgPop", "pgZeta"], key="@pgZeta/7")]),
    ]


STEMS = ["stemS1", "stemP1", "stemP2", "stemP3", "stemW1", "stemB2", "stema2", "stemH1", "stemH2", "stemH3", "stemJ2",
         "stemj1", "stemR1", "stemN1"]
NAMES_OF_PAGES = list(PAGES) + POPUPS


def make_map(path: Path, extra_rows=(), drop_kinds=()) -> Path:
    """The library's real map with extra rows added."""
    doc = load_json(REAL_MAP)
    doc["rows"] = [r for r in doc["rows"] if r["kind"] not in drop_kinds] + list(extra_rows)
    return dump(path, doc)


def row(kind, element, feature=None, state="reviewed", properties=None, states=None) -> dict:
    return {"kind": kind, "feature": feature, "element": element, "import": f"@oicl/{element}.js",
            "properties": ROW_PROPERTIES if properties is None else properties,
            "states": ROW_STATES if states is None else states, "state": state, "reason": "a bench row",
            "reference": None}


def survey_argv(ctig, out, mapf=None, profile=None, *extra) -> list[str]:
    return ["--survey", str(ctig), "--catalogue", str(CATALOGUE), "--profile", str(profile or PROFILE),
            "--module", str(MODULE), "--openbridge-map", str(mapf or REAL_MAP), "--elements", str(ELEMENTS),
            "--out", str(out), *map(str, extra)]


def release_argv(survey, out, mapf=None, profile=None, *extra) -> list[str]:
    return ["--release", str(survey), "--catalogue", str(CATALOGUE), "--profile", str(profile or PROFILE),
            "--module", str(MODULE), "--openbridge-map", str(mapf or REAL_MAP), "--out", str(out), *map(str, extra)]


def by_kind(doc) -> dict:
    return {k["kind"]: k for k in doc["kinds"]}


def feature_of(kind_row_doc, feature) -> dict | None:
    return next((f for f in kind_row_doc.get("features") or [] if f["feature"] == feature), None)


def has_token(text: str, token: str) -> bool:
    return re.search(r"(?<![A-Za-z0-9_])" + re.escape(token) + r"(?![A-Za-z0-9_])", text, re.IGNORECASE) is not None
