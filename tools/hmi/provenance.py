"""The `provenance` object every package pipeline document carries (ARCH-WFB-01 revision B8 section 29.4): which
tool made the document, from which commit, with which inputs, so that a document read outside the manager still says
what produced it. Shared by the S10-B commands (`asm_model.py`, `preview.py`, `library_gaps.py`,
`asm_descriptors.py`, `glass_gates.py`, `sidebyside.py`).

`argv` holds the command line as given: the commands take no secret on the command line (the gateway token and the
test login reach `glass_gates.py` through the environment), and the names of secret variables only, never a value,
may be added by the caller.
"""
from __future__ import annotations

import hashlib
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = "Cadre HMI Library"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _git(*args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def repository_state() -> tuple[str | None, bool | None]:
    """`(commit, dirty)` of the repository the command runs from; None where git cannot say."""
    commit = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain", "--untracked-files=no")
    return commit, (bool(status) if status is not None else None)


def inputs_of(paths) -> list[dict]:
    """`[{"path", "sha256"}]` for each existing file of `paths`; a folder contributes its files, sorted."""
    out = []
    for p in paths:
        if p is None:
            continue
        p = Path(p)
        files = sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else [p]
        for f in files:
            if f.is_file():
                out.append({"path": f.as_posix(), "sha256": sha256_of(f)})
    return out


class Clock:
    """Started at construction; `provenance` closes it."""

    def __init__(self) -> None:
        self.started = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self._t = time.monotonic()

    def provenance(self, tool: str, argv: list[str], input_paths=()) -> dict:
        commit, dirty = repository_state()
        return {"tool": tool, "repository": REPOSITORY, "commit": commit, "dirty": dirty,
                "argv": list(argv), "inputs": inputs_of(input_paths), "started": self.started,
                "duration_s": round(time.monotonic() - self._t, 2),
                "interpreter": {"path": sys.executable, "version": sys.version.split()[0],
                                "bits": struct.calcsize("P") * 8}}


def write_json(path: Path, doc) -> Path:
    """A JSON document with LF line endings and a final newline (the repository's `eol=lf`)."""
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    return path
