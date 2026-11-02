"""Side-by-side pictures: for each page and faceplate, the original runtime picture beside up to three renderings.

Generalised from the eng02 slice's side-by-side scripts (ARCH-WFB-01 revision B8 Table 109, WFBD-091). Usage:

    sidebyside.py --original DIR [--column NAME=DIR ...] (--pages LIST | --model F) --window WxH [--sheets] --out O

    --original DIR     the original's pictures, `<name>.png` in DIR or DIR/pictures, or the windows named by a
                       `manifest.json` (`windows[]` with `target` and `picture`, ctig's capture)
    --column NAME=DIR  a rendering's pictures, `<name>.png` in DIR or DIR/pictures; NAME is one of preview, asm,
                       ignition (the order given is the order shown; the original always comes first)
    --pages LIST       a list file of what to show: one name to a line (`page:Name` or `faceplate:Name`; a bare name is
                       a page), or a JSON array of names or {"name", "kind"}
    --model F          without --pages: the built pages and the faceplates of the devices of an ASM model
    --window WxH       the size the renderings were taken at; the sheets' cells keep its aspect
    --sheets           also write `sheet-a.png` and `sheet-b.png`: the last two columns tiled page by page in one
                       fixed grid, so that one image comparison covers every page

Writes `O/<name>.png` for each page (and `O/<name>-faceplate.png` when a faceplate shares a page's name),
`O/manifest.json` (`cadre-hmi-sidebyside/1`: each picture's sources by path and SHA-256, what is missing) and with
`--sheets` the two contact sheets. The pictures are composed in headless Chromium (Playwright, ctig's `.venv`): a
picture is shown at its own size, a missing one as a labelled gap, never replaced by another.

Exit codes: 0 every picture of every column is there; 2 a picture is missing; 1 a fault.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from hmi import provenance  # noqa: E402

TOOL = "tools/compare/sidebyside.py"
COLUMN_NAMES = ("original", "preview", "asm", "ignition")
CAPTION = {"original": "Original runtime", "preview": "One-to-one preview", "asm": "ASM preview",
           "ignition": "Ignition (G8)"}


class Fault(Exception):
    pass


def read_pages(path: str | None, model: str | None) -> list[dict]:
    """`[{"name", "kind"}]` from a list file or from the model."""
    if path:
        text = Path(path).read_text(encoding="utf-8").strip()
        try:
            raw = json.loads(text) if text.startswith("[") else [ln.strip() for ln in text.splitlines() if ln.strip()]
        except ValueError as e:
            raise Fault(f"--pages {path}: {e}") from None
        out = []
        for x in raw:
            if isinstance(x, dict) and x.get("name"):
                out.append({"name": x["name"], "kind": x.get("kind") or "page"})
            elif isinstance(x, str):
                kind, _, name = x.partition(":") if x.partition(":")[0] in ("page", "faceplate") else ("page", "", x)
                out.append({"name": name, "kind": kind})
            else:
                raise Fault(f"--pages {path}: cannot read {x!r}")
        return out
    if model:
        try:
            m = json.loads(Path(model).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise Fault(f"--model {model}: {e}") from None
        pages = [{"name": p["id"], "kind": "page"} for p in m.get("pages", []) if p.get("built")]
        fps = [{"name": t, "kind": "faceplate"} for t, d in m.get("devices", {}).items()
               if d.get("faceplate") not in (None, "empty")]
        return pages + fps
    raise Fault("--pages or --model is needed")


def find_picture(folder: Path, name: str) -> Path | None:
    for c in (folder / f"{name}.png", folder / "pictures" / f"{name}.png"):
        if c.is_file():
            return c
    manifest = folder / "manifest.json"
    if manifest.is_file():
        try:
            doc = json.loads(manifest.read_text(encoding="utf-8"))
        except ValueError:
            return None
        for w in doc.get("windows", []):
            if w.get("target") == name and w.get("picture"):
                p = folder / w["picture"]
                if p.is_file():
                    return p
    return None


def file_name(item: dict, used: set[str]) -> str:
    base = item["name"] if item["name"] not in used else f"{item['name']}-{item['kind']}"
    used.add(item["name"])
    return base + ".png"


def row_html(item: dict, cols: list[str], pics: dict[str, Path | None]) -> str:
    cells = []
    for c in cols:
        p = pics[c]
        body = (f'<img src="{p.as_uri()}" style="display:block;border:1px solid #999">' if p else
                '<div style="width:480px;height:270px;border:1px dashed #b33;color:#b33;display:flex;'
                'align-items:center;justify-content:center">picture missing</div>')
        cells.append(f'<figure style="margin:0"><figcaption style="padding:4px 0 8px">{html.escape(CAPTION[c])}'
                     f'</figcaption>{body}</figure>')
    return ('<html><body style="margin:0;background:#fff;font:600 20px sans-serif;display:flex;gap:16px;'
            'align-items:flex-start;padding:12px">' + "".join(cells) + "</body></html>")


def sheet_html(items: list[dict], col: str, pics: dict[str, dict[str, Path | None]], grid: dict) -> str:
    w, h, cols = grid["cell_w"], grid["cell_h"], grid["cols"]
    cells = []
    for it in items:
        p = pics[it["key"]][col]
        inner = (f'<img src="{p.as_uri()}" style="width:{w}px;height:{h}px;object-fit:contain;display:block">' if p
                 else f'<div style="width:{w}px;height:{h}px;color:#b33;display:flex;align-items:center;'
                      f'justify-content:center">missing</div>')
        cells.append(f'<div style="width:{w}px;height:{h + 22}px;border:1px solid #ccc">'
                     f'<div style="font:12px sans-serif;height:22px;padding:3px 6px">{html.escape(it["name"])}</div>'
                     f'{inner}</div>')
    return (f'<html><body style="margin:0;background:#fff"><div style="display:grid;grid-template-columns:'
            f'repeat({cols},{w + 2}px);gap:0">' + "".join(cells) + "</div></body></html>")


def main(argv: list[str] | None = None) -> int:
    clock = provenance.Clock()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--original", required=True, metavar="DIR")
    ap.add_argument("--column", action="append", default=[], metavar="NAME=DIR")
    ap.add_argument("--pages", default=None, metavar="LIST")
    ap.add_argument("--model", default=None)
    ap.add_argument("--window", default="1920x1080")
    ap.add_argument("--sheets", action="store_true")
    ap.add_argument("--out", required=True)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    args_line = sys.argv[1:] if argv is None else list(argv)
    try:
        try:
            ww, wh = (int(n) for n in a.window.lower().split("x"))
        except ValueError:
            raise Fault(f"--window is WIDTHxHEIGHT, not {a.window!r}") from None
        folders = {"original": Path(a.original)}
        for c in a.column:
            name, eq, folder = c.partition("=")
            if not eq or name not in COLUMN_NAMES[1:]:
                raise Fault(f"--column is NAME=DIR with NAME one of {', '.join(COLUMN_NAMES[1:])}, not {c!r}")
            if name in folders:
                raise Fault(f"--column {name} is given twice")
            folders[name] = Path(folder)
        for n, f in folders.items():
            if not f.is_dir():
                raise Fault(f"column {n}: {f} is not a folder")
        if a.sheets and len(folders) < 2:
            raise Fault("--sheets needs at least two columns")
        items = read_pages(a.pages, a.model)
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise Fault("composing the pictures needs Playwright: run under ctig's .venv") from None
    except Fault as e:
        print(f"sidebyside: {e}")
        return 1
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cols = list(folders)
    used: set[str] = set()
    pics: dict[str, dict[str, Path | None]] = {}
    manifest_pictures, missing = [], []
    for it in items:
        it["file"] = file_name(it, used)
        it["key"] = it["file"]
        pics[it["key"]] = {c: find_picture(folders[c], it["name"]) for c in cols}
        sources = []
        for c in cols:
            p = pics[it["key"]][c]
            if p is None:
                missing.append({"name": it["name"], "kind": it["kind"], "column": c})
            else:
                sources.append({"column": c, "path": p.as_posix(), "sha256": provenance.sha256_of(p)})
        manifest_pictures.append({"name": it["name"], "kind": it["kind"], "file": it["file"], "sources": sources})
    sheets = None
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 600})
        tmp = out / "_compose.html"
        for it in items:
            tmp.write_text(row_html(it, cols, pics[it["key"]]), encoding="utf-8")
            page.goto(tmp.as_uri())
            page.wait_for_timeout(100)
            page.screenshot(path=str(out / it["file"]), full_page=True)
        if a.sheets:
            n = max(len(items), 1)
            ncol = max(1, math.ceil(math.sqrt(n)))
            cell_w = 480
            grid = {"cols": ncol, "rows": math.ceil(n / ncol), "cell_w": cell_w, "cell_h": round(cell_w * wh / ww),
                    "order": [it["name"] for it in items]}
            pair = cols[-2:]
            for label, col in zip(("a", "b"), pair):
                tmp.write_text(sheet_html(items, col, pics, grid), encoding="utf-8")
                page.goto(tmp.as_uri())
                page.wait_for_timeout(100)
                page.screenshot(path=str(out / f"sheet-{label}.png"), full_page=True)
            sheets = {"a": "sheet-a.png", "b": "sheet-b.png", "columns": pair, "grid": grid}
        tmp.unlink()
        browser.close()
    doc = {"schema": "cadre-hmi-sidebyside/1", "columns": cols,
           "pictures": [{k: v for k, v in m.items()} for m in manifest_pictures], "missing": missing,
           "sheets": sheets, "provenance": clock.provenance(TOOL, args_line, [])}
    provenance.write_json(out / "manifest.json", doc)
    print(f"sidebyside: columns {', '.join(cols)}, pictures {len(items)}, missing {len(missing)}"
          + (", sheets 2" if sheets else ""))
    return 2 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
