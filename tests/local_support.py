"""Helpers of the tests of the local assembly (NOTE-WFB-10 section 11.2, WP-W03): a synthetic diagram page with one
assembly of the synthetic local kind `skid`, its device model, and a runner for `tools/hmi/screen.py` and
`tools/hmi/page_checks.py` as command lines. Placeholder names only (`skid`, `Skid1`, `PageA`); nothing here needs a
gateway or a browser."""
import copy
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import parent as par  # noqa: E402

PYTHON = sys.executable
SCREEN = ROOT / "tools" / "hmi" / "screen.py"
CHECKS = ROOT / "tools" / "hmi" / "page_checks.py"
TAG_ROOT = "[default]cadre_hmi_loc"
VIEW = "com.inductiveautomation.perspective/views/"
KIND = "skid"
KIND_VIEW = "Skid"       # the kind with its first letter in upper case: the view name
RULES = ("assembly-kind-not-local", "assembly-kind-is-library", "assembly-without-local-kinds", "assembly-style",
         "assembly-parts-differ", "assembly-on-cards")   # the order of NOTE-WFB-10 section 11.2 item 6

_names = itertools.count(1)


def dump(path: Path, doc) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    return path


def parts(prefix: str = "", buttons: bool = False) -> dict:
    """A part set with one part of each array but the buttons; the dynamic parts name a member of the device. A button
    is allowed in a Home only (G0 rule `assembly-button-on-page`, review finding 10), so `buttons=True` is for a Home."""
    out = {
        "labels": [{"id": f"{prefix}T", "x": 10, "y": 8, "w": 120, "h": 20, "text": "Skid", "align": "left",
                    "style": "heading"}],
        "symbols": [{"id": f"{prefix}RO", "kind": "readout", "x": 10, "y": 40, "w": 120, "h": 40, "member": "value",
                     "unit": "kPa", "format": "0.0", "label": "Pressure"},
                    {"id": f"{prefix}IN", "kind": "indicator", "x": 10, "y": 90, "w": 60, "h": 30, "member": "state"}],
        "lines": [{"id": f"{prefix}LN", "points": [[0, 130], [200, 130]], "style": "dashed"}],
        "shapes": [{"id": f"{prefix}SH", "x": 0, "y": 0, "w": 200, "h": 180, "form": "rect"}],
    }
    if buttons:
        out["buttons"] = [{"id": f"{prefix}BT", "x": 10, "y": 140, "w": 90, "h": 30, "label": "Start", "member": "cmdStart"}]
    return out


def assembly(ident: str = "A1", kind: str = KIND, device: str = "Skid1", **more) -> dict:
    a = {"id": ident, "kind": kind, "device": device, "title": "Skid", "label": f"Skid {ident}",
         "x": 100, "y": 100, "w": 200, "h": 180, "parts": parts(),
         "home": {"w": 200, "h": 60, "parts": {"buttons": parts(buttons=True)["buttons"]}}}
    a.update(more)
    return a


def page(*assemblies: dict, layout: str = "diagram", **more) -> dict:
    doc = {"schema": "cadre-hmi-screen/1",
           "screen": {"id": "PageA", "route": "/a", "title": "Page A", "view": "Screens/PageA", "layout": layout,
                      "width": 800, "height": 500, "node": "Plant"},
           "tagRoot": TAG_ROOT, "assemblies": list(assemblies)}
    doc.update(more)
    return doc


def devices(*folders: str) -> dict:
    members = {"value": {"type": "Float8", "access": "read"}, "state": {"type": "Boolean", "access": "read"},
               "cmdStart": {"type": "Boolean", "access": "write", "pulse": True, "caption": "Start"}}
    return {"schema": "cadre-hmi-devices/1", "tagRoot": TAG_ROOT,
            "devices": [{"id": f, "kind": "local", "title": f, "label": f"Device {f}",
                         "members": copy.deepcopy(members)} for f in (folders or ("Skid1",))]}


class Parent:
    """The parent project, built once into a folder every run of a test case shares."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        subprocess.run([PYTHON, str(ROOT / "tools" / "hmi" / "parent.py"), "--out", str(self.dir)],
                       check=True, capture_output=True, text=True, cwd=str(ROOT))

    def close(self):
        self._tmp.cleanup()

    def screen(self, descs, *, dev=None, local_kinds=None, extra=(), tag: str | None = None):
        """Run screen.py on the descriptors (documents) and return a Result. `local_kinds` is a list written to a file
        and passed as `--local-kinds`, or None to leave the option out."""
        n = next(_names)
        project = tag or f"cadre_hmi_loc{n}"
        work = self.dir / f"run{n}"
        argv = [PYTHON, str(SCREEN), "--project", project, "--app-name", "Loc", "--out", str(self.dir),
                "--report", str(work / "report.json")]
        for i, d in enumerate(descs if isinstance(descs, list) else [descs]):
            argv += ["--descriptor", str(dump(work / f"d{i}.json", d))]
        if dev is not None:
            argv += ["--devices-file", str(dump(work / "devices.json", dev))]
        if local_kinds is not None:
            argv += ["--local-kinds", str(dump(work / "local-kinds.json", local_kinds))]
        argv += list(extra)
        p = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT))
        return Result(p, self.dir / project, work / "report.json")


class Result:
    def __init__(self, proc, child: Path, report: Path):
        self.code, self.out, self.err = proc.returncode, proc.stdout, proc.stderr
        self.child, self.report_path = child, report

    @property
    def text(self) -> str:
        return self.out + self.err

    @property
    def report(self) -> dict:
        return json.loads(self.report_path.read_text(encoding="utf-8")) if self.report_path.is_file() else {}

    def g0_errors(self) -> list:
        """`gates.G0.errors[]` of the screen report, as the note states it (section 11.2 item 6)."""
        return list((self.report.get("gates") or {}).get("G0", {}).get("errors", []))

    def g0_rules(self) -> list[str]:
        """The rule names in `gates.G0.errors[]`, in the order they are listed (a rule once, at its first entry)."""
        seen: list[str] = []
        for e in self.g0_errors():
            for rule in RULES:
                if rule in json.dumps(e) and rule not in seen:
                    seen.append(rule)
        return seen

    def view(self, path: str) -> dict | None:
        f = self.child / "com.inductiveautomation.perspective" / "views" / path / "view.json"
        if not f.is_file():
            f = self.child / "views" / path / "view.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else None

    def view_files(self) -> list[str]:
        base = self.child / "com.inductiveautomation.perspective" / "views"
        return sorted(p.relative_to(base).as_posix() for p in base.rglob("view.json")) if base.is_dir() else []


def nodes(view: dict) -> list[dict]:
    out: list[dict] = []

    def walk(n):
        out.append(n)
        for c in n.get("children") or []:
            walk(c)
    walk(view["root"])
    return out
