"""One-to-one comparison of a generated screen with its reference rendering.

Inputs (all captured at the same viewport, 1600 x 900, scroll 0,0):
    --ref-fp / --ours-fp     fingerprints from tools/compare/fingerprint.js
    --ref-img / --ours-img   screenshots from the same browser at the same scale (optional)
    --descriptor             the screen descriptor (names and kinds for the table)

Structural measures, per symbol: centre offset (px), box size, readout text equality after
normalisation (spacing, thousands separators and hinted leading zeros removed), and whether
the raw text matches exactly. Visual measures (PIL needed; set CADRE_PIL_PYTHON to an
interpreter that has it): mean absolute grey difference, share of pixels differing by more
than 32 grey levels, a side-by-side image, a difference heat map, and a crop grid with each
symbol's reference rendering beside ours.

Usage:
    python tools/compare/compare.py --ref-fp a.json --ours-fp b.json --descriptor d.json
        [--ref-img a.jpg --ours-img b.jpg] --out workspace/compare/<screen>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PIL_PY = os.environ.get("CADRE_PIL_PYTHON", "F:/repos/ProgramAudit/.venv/Scripts/python.exe")


def norm_text(t: str) -> str:
    t = t.replace("\u00a0", " ").replace("\u00b3", "3").replace("\u00b2", "2")   # superscripts
    t = re.sub(r"(?<=\d),(?=\d{3})", "", t)          # thousands separators
    t = re.sub(r"\b0+(?=\d)", "", t)                   # hinted leading zeros
    t = re.sub(r"\b0{3}\b", "", t)                     # hinted fraction placeholders
    t = re.sub(r"\s+", "", t)
    return t


def structural(ref: dict, ours: dict, desc: dict) -> dict:
    syms = desc.get("symbols", [])
    r_rows = {r[0]: r for r in ref["rows"]}
    o_rows = {r[0]: r for r in ours["rows"]}
    table, deltas = [], []
    for i, s in enumerate(syms):
        r, o = r_rows.get(i), o_rows.get(i)
        if not r or not o:
            table.append({"id": s["id"], "kind": s["kind"], "missing": "ref" if not r else "ours"})
            continue
        d = ((r[1] - o[1]) ** 2 + (r[2] - o[2]) ** 2) ** 0.5
        deltas.append(d)
        rt, ot = r[5], o[5]
        table.append({"id": s["id"], "kind": s["kind"], "centre_offset_px": round(d, 1),
                      "ref_box": [r[3], r[4]], "ours_box": [o[3], o[4]],
                      "ref_text": rt, "ours_text": ot,
                      "text_equal_normalised": tokens_equal(rt, ot),
                      "text_equal_exact": rt == ot})
    n = len([t for t in table if "missing" not in t])
    return {"symbols": len(syms), "compared": n,
            "centre_exact": sum(1 for t in table if t.get("centre_offset_px", 99) == 0),
            "centre_within_2px": sum(1 for t in table if t.get("centre_offset_px", 99) <= 2),
            "max_centre_offset_px": round(max(deltas), 1) if deltas else None,
            "text_equal_normalised": sum(1 for t in table if t.get("text_equal_normalised")),
            "text_equal_exact": sum(1 for t in table if t.get("text_equal_exact")),
            "table": table}


def tokens_equal(ref: str, ours: str) -> bool:
    """The reference text contains every word of ours (vendor components repeat values for
    accessibility and hinting), after normalisation."""
    r = norm_text(ref)
    o = [norm_text(w) for w in ours.split()]
    return all(w in r for w in o if w)


VISUAL = r'''
import json, sys
from PIL import Image, ImageChops, ImageOps, ImageDraw
ref, ours, out, boxes = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
a = Image.open(ref).convert("RGB"); b = Image.open(ours).convert("RGB")
if a.size != b.size:
    b = b.resize(a.size)
ga, gb = ImageOps.grayscale(a), ImageOps.grayscale(b)
d = ImageChops.difference(ga, gb)
hist = d.histogram(); total = sum(hist)
mean = sum(i * c for i, c in enumerate(hist)) / total
over = sum(c for i, c in enumerate(hist) if i > 32) / total
side = Image.new("RGB", (a.width * 2 + 8, a.height), "white"); side.paste(a, (0, 0)); side.paste(b, (a.width + 8, 0))
side.save(out + "/side-by-side.png")
heat = ImageOps.colorize(ImageOps.autocontrast(d), black="white", white="red"); heat.save(out + "/difference.png")
scale = a.width / 1600.0
cells = []
for name, cx, cy, w, h in boxes:
    pad = 34
    box = (int((cx - w / 2 - pad) * scale), int((cy - h / 2 - pad) * scale),
           int((cx + w / 2 + pad) * scale), int((cy + h / 2 + pad) * scale))
    if box[0] < 0 or box[1] < 0 or box[2] > a.width or box[3] > a.height:
        continue
    ca, cb = a.crop(box), b.crop(box)
    z = 3
    ca = ca.resize((ca.width * z, ca.height * z)); cb = cb.resize((cb.width * z, cb.height * z))
    cell = Image.new("RGB", (ca.width * 2 + 6, ca.height + 18), "white")
    cell.paste(ca, (0, 18)); cell.paste(cb, (ca.width + 6, 18))
    ImageDraw.Draw(cell).text((2, 2), name + "   reference | ours", fill="black")
    cells.append(cell)
if cells:
    cw = max(c.width for c in cells); ch = max(c.height for c in cells); cols = 4
    rows = (len(cells) + cols - 1) // cols
    grid = Image.new("RGB", (cw * cols, ch * rows), "white")
    for i, c in enumerate(cells):
        grid.paste(c, ((i % cols) * cw, (i // cols) * ch))
    grid.save(out + "/symbol-crops.png")
print(json.dumps({"size": a.size, "mean_abs_grey_diff": round(mean, 2), "share_pixels_over_32": round(over, 4),
                  "crops": len(cells)}))
'''


def visual(ref_img: Path, ours_img: Path, out: Path, boxes: list) -> dict:
    if not Path(PIL_PY).exists():
        return {"skipped": f"no PIL interpreter at {PIL_PY}"}
    r = subprocess.run([PIL_PY, "-c", VISUAL, str(ref_img), str(ours_img), str(out), json.dumps(boxes)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": r.stderr[-400:]}
    return json.loads(r.stdout.strip().splitlines()[-1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-fp", required=True)
    ap.add_argument("--ours-fp", required=True)
    ap.add_argument("--descriptor", required=True)
    ap.add_argument("--ref-img")
    ap.add_argument("--ours-img")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ref = json.loads(Path(a.ref_fp).read_text(encoding="utf-8"))
    ours = json.loads(Path(a.ours_fp).read_text(encoding="utf-8"))
    desc = json.loads(Path(a.descriptor).read_text(encoding="utf-8"))
    res = {"structural": structural(ref, ours, desc)}
    if a.ref_img and a.ours_img:
        boxes = [[t["id"], r[1], r[2], r[3], r[4]] for t, r in
                 zip(res["structural"]["table"], sorted(ref["rows"])) if "missing" not in t]
        res["visual"] = visual(Path(a.ref_img), Path(a.ours_img), out, boxes)
    (out / "comparison.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    s = res["structural"]
    print(json.dumps({k: v for k, v in s.items() if k != "table"}, indent=1))
    if "visual" in res:
        print(json.dumps(res["visual"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
