"""Helpers shared by the tests of the ASM pipeline (S10-B): the synthetic inputs of `tests/fixtures/asm-*.json`
written as a run folder, tiny pictures, and a validator for the `cadre-hmi-*` schemas. Placeholder names only."""
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
FIXTURES = ROOT / "tests" / "fixtures"
UNITS = {"Overview": "page", "PumpStation": "page", "PUMP01_FP": "popup_set", "SEQ01_SP": "popup_set"}
UNIT_FILES = {"Overview": "asm-understanding-overview.json", "PumpStation": "asm-understanding-pumpstation.json",
              "PUMP01_FP": "asm-understanding-pump01-fp.json", "SEQ01_SP": "asm-understanding-seq01-sp.json"}


def fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def dump(path: Path, doc) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    return path


def png(w: int = 64, h: int = 48, colour: tuple = (200, 200, 200)) -> bytes:
    """A valid PNG of one flat colour."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + bytes(colour) * w for _ in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def write_inventory(folder: Path) -> Path:
    """A ctig inventory folder (`ctig.inventory/1`): manifest.json, and per unit a folder with unit.json, one
    inventory.json per window and the two pictures."""
    units = []
    for uid, kind in UNITS.items():
        u = folder / "units" / uid
        windows = []
        for target in [uid]:
            objects = [{"an": str(n), "class": "Text", "x": 10 * n, "y": 10, "w": 40, "h": 20, "text": f"obj {n}",
                        "nodes": [], "parent": None, "behaviour": {}, "tags": []} for n in range(1, 4)]
            dump(u / f"{target}.inventory.json", {"page": target, "objects": objects})
            (u / f"{target}.runtime.png").write_bytes(png(80, 60, (180, 190, 200)))
            (u / f"{target}.design.png").write_bytes(png(80, 60, (200, 190, 180)))
            windows.append({"target": target, "inventory": f"{target}.inventory.json",
                            "runtime_picture": f"{target}.runtime.png", "design_picture": f"{target}.design.png",
                            "page_size": [1024, 768], "frame_rows": []})
        dump(u / "unit.json", {"id": uid, "kind": kind, "host_page": None if kind == "page" else "PumpStation",
                               "windows": windows})
        units.append({"id": uid, "kind": kind, "host_page": None, "folder": f"units/{uid}",
                      "windows": [w["target"] for w in windows]})
    dump(folder / "manifest.json", {"units": units, "objects": 12, "provenance": {"tool": "ctig"}})
    return folder


def write_pictures(folder: Path) -> Path:
    """The one-to-one preview's pictures, a PNG per page."""
    folder.mkdir(parents=True, exist_ok=True)
    for page in ("Overview", "PumpStation"):
        (folder / f"{page}.png").write_bytes(png(96, 54, (190, 200, 190)))
    return folder


def inputs(base: Path) -> dict:
    """The fixtures written as files under `base`; the paths by the option name they go with."""
    ups = [dump(base / "in" / "understandings" / n, fixture(n)) for n in UNIT_FILES.values()]
    lst = base / "in" / "understandings.txt"
    lst.write_text("\n".join(str(p) for p in ups) + "\n", encoding="utf-8", newline="\n")
    return {"understandings": lst,
            "faceplates": dump(base / "in" / "faceplates.json", fixture("asm-faceplates.json")),
            "tables": dump(base / "in" / "tables.json", fixture("asm-tables.json")),
            "device-model": dump(base / "in" / "device_model.json", fixture("asm-device-model.json")),
            "openers": dump(base / "in" / "openers.json", fixture("asm-openers.json")),
            "menu": dump(base / "in" / "menu.json", fixture("asm-menu.json")),
            "contract": dump(base / "in" / "contract.json", fixture("asm-contract.json")),
            "inventory": write_inventory(base / "in" / "inventory"),
            "pictures": write_pictures(base / "in" / "pictures")}


def validate(doc, schema_file: str) -> list[str]:
    """The errors of `doc` against `schemas/<schema_file>` (empty when it validates)."""
    import jsonschema
    schema = json.loads((ROOT / "schemas" / schema_file).read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path))}: {e.message[:200]}" for e in v.iter_errors(doc)]
