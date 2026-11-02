"""Measure the readout and the instrument field of the module against the library's boxes (COB-127).

The module draws the library kinds `readout` and `instrument-field` with `obc-transmitter` and
`obc-instrument-field` where the element shows the symbol truthfully (`screen.MODULE_KIND`). This measures,
offline, in a browser page that holds the built bundle, the module's stylesheet and the rules the wrapper adds
to the element's shadow root (`gen_module_assets.SHEETS`), what each element draws in the box the library
gives the block (`library.block_size`, `screen.grown_box`):

  * which of the transmitter's two identifier properties draws the identifier (`tag`, `idTag`);
  * whether a value is grouped by thousands (the library's `#,##0` groups, the elements do not);
  * the size of the value chip and of the identifier, and of the field's rows, against the library's box and
    against the width the library allows for the same text (`library.text_width`);
  * where the field's rows lie for `align` end and centre.

Usage (ctig's .venv for Playwright), after `npm run build` in module/web and gen_module_assets.py:
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe module/tools/measure_instruments.py
Writes module/web/instruments.json.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_module_assets as gen  # noqa: E402
from hmi import library  # noqa: E402

CSS = HERE / "gateway/src/main/resources/mounted/css/cadre-ob.css"
BUNDLE = HERE / "web/dist/ob-components.js"

PAGE = r"""async ([tag, props, box, sheet, endAligned, center]) => {
  const holder = document.createElement('div');
  holder.style.cssText = `position:absolute;left:100px;top:100px;width:${box[0]}px;height:${box[1]}px`;
  const wrap = document.createElement('div');
  wrap.className = 'cadre-ob obc-component-size-regular';
  if (endAligned) wrap.style.justifyContent = center ? 'center' : 'flex-end';
  const el = document.createElement(tag);
  for (const k in props) el[k] = props[k];
  if (endAligned) el.toggleAttribute('data-center', !!center);
  wrap.appendChild(el); holder.appendChild(wrap); document.body.appendChild(holder);
  await el.updateComplete;
  const st = document.createElement('style'); st.textContent = sheet; el.shadowRoot.appendChild(st);
  await new Promise(r => setTimeout(r, 450));
  const r = (n) => { if (!n) return null; const b = n.getBoundingClientRect();
    return [Math.round((b.x - 100) * 10) / 10, Math.round((b.y - 100) * 10) / 10,
            Math.round(b.width * 10) / 10, Math.round(b.height * 10) / 10]; };
  const sr = el.shadowRoot, out = {};
  for (const s of ['.transmitter', '.chip', '.id-tag', '.wrapper', '.value', '.value-blue', '.label', '.setpoint'])
    out[s] = r(sr.querySelector(s));
  out.text = sr.textContent.replace(/\s+/g, ' ').trim();
  // everything printed, down through the nested shadow roots (the chip is an element of its own)
  const all = (root, top) => { let t = '';
    if (top) { for (const c of root.children) if (c.tagName !== 'STYLE') t += ' ' + c.textContent; }
    else t += ' ' + root.textContent;
    for (const n of root.querySelectorAll('*')) if (n.shadowRoot) t += ' ' + all(n.shadowRoot, false);
    return t; };
  out.chipText = all(sr, true).replace(/\s+/g, ' ').trim();
  out.printed = el.valueBlueNumbers === undefined ? null : el.valueBlueNumbers;
  holder.remove();
  return out; }"""


def main() -> int:
    from playwright.sync_api import sync_playwright
    html = Path(tempfile.mkdtemp()) / "m.html"
    html.write_text(f'<!doctype html><html><head><link rel="stylesheet" href="{CSS.as_uri()}"></head><body>'
                    f'<script src="{BUNDLE.as_uri()}"></script></body></html>', encoding="utf-8")
    contracts = {k: v for k, v in json.loads((ROOT / "library/contracts.json").read_text(encoding="utf-8")).items()}
    contracts = contracts.get("views", contracts)
    ro, fi = contracts["Automation/Readout"], contracts["Instrument/Field"]
    out: dict = {"readout": {}, "instrumentfield": {}}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 900, "height": 700})
        pg.goto(html.as_uri())
        pg.wait_for_function("!!customElements.get('obc-transmitter') && !!customElements.get('obc-instrument-field')")
        pg.evaluate("document.fonts.ready")

        def measure(tag, props, box, sheet, end=False, center=False):
            return pg.evaluate(PAGE, [tag, props, box, sheet, end, center])

        # 1. which property draws the identifier, and grouping
        for key, props in (("tag", {"value": 1234.5, "unit": "m3/h", "tag": "FT-101"}),
                           ("idTag", {"value": 1234.5, "unit": "m3/h", "idTag": "FT-101"})):
            m = measure("obc-transmitter", props, ro["size"], gen.SHEETS["readout"])
            out["readout"]["identifier_" + key] = {"drawsIdentifier": "FT-101" in (m["chipText"] or ""),
                                                   "idTagBox": m[".id-tag"]}
        m = measure("obc-transmitter", {"value": 1234.5, "unit": "m3/h", "fractionDigits": 1}, ro["size"],
                    gen.SHEETS["readout"])
        out["readout"]["valueText"] = m["chipText"]
        out["readout"]["groupsThousands"] = "1,234" in (m["chipText"] or "")
        m = measure("obc-instrument-field", {"value": 1234.5, "fractionDigits": 1}, fi["size"],
                    gen.SHEETS["instrumentfield"], True)
        out["instrumentfield"]["valueText"] = m["printed"]
        out["instrumentfield"]["groupsThousands"] = "," in (m["printed"] or "")

        # 2. the readout: the chip and the identifier against the library's box and text widths
        rows = []
        for tagged in (False, True):
            box = list(library.block_size(ro, {"hasTag": tagged}))
            for value, unit in (("0.0", ""), ("12.5", "%"), ("1234.5", "m3/h"), ("123456.7", "mg/L"), ("-12.5", "")):
                for tag in (("FT-101", "FIT-3011-A") if tagged else ("",)):
                    props = {"value": float(value), "unit": unit, "fractionDigits": 1}
                    if tag:
                        props["idTag"] = tag
                    m = measure("obc-transmitter", props, box, gen.SHEETS["readout"])
                    chip, ident = m[".chip"], m[".id-tag"]
                    lib_value = library.text_width("automation-value-regular", len(value) + 1 + len(unit)) \
                        + ro["value"]["pad"]
                    lib_ident = library.identifier_width(ro, len(tag)) if tag else 0
                    top = min(chip[1], ident[1] if ident else chip[1])
                    bottom = max(chip[1] + chip[3], (ident[1] + ident[3]) if ident else 0)
                    rows.append({"box": box, "value": value, "unit": unit, "idTag": tag,
                                 "chip": chip[2:], "idTagSize": ident[2:] if ident else None,
                                 "libraryValueWidth": lib_value, "libraryIdWidth": lib_ident,
                                 "narrowerThanLibrary": chip[2] <= lib_value and (not ident or ident[2] <= lib_ident),
                                 "heightOver": round(bottom - top - box[1], 1), "text": m["chipText"]})
        out["readout"]["cases"] = rows

        # 3. the instrument field: regular and enhanced, with and without a setpoint, end and centre
        rows = []
        for size in ("regular", "enhanced"):
            for sp in (False, True):
                box = list(library.block_size(fi, {"size": size, "hasSetpoint": sp}))
                for value, caption in (("12", ("Flow", "m3/h")), ("1234.5", ("Raw water flow", "m3/h")),
                                       ("123456.7", ("", "")), ("12", ("Level", "")), ("12", ("Turbidity", "NTU"))):
                    for center in (False, True):
                        props = {"value": float(value), "tag": caption[0], "unit": caption[1], "size": size,
                                 "fractionDigits": 1, "hasSetpoint": sp, "setpoint": 1200.0, "center": center}
                        m = measure("obc-instrument-field", props, box, gen.SHEETS["instrumentfield"], True, center)
                        w = m[".wrapper"]
                        text = (caption[0] + (" " + caption[1] if caption[1] else "")).strip()
                        lib_caption = library.text_width("instrument-unit", len(text))
                        rows.append({"size": size, "hasSetpoint": sp, "box": box, "center": center, "value": value,
                                     "caption": text, "element": w[2:], "overBox": [round(w[2] - box[0], 1),
                                                                                  round(w[3] - box[1], 1)],
                                     "valueRight": round(m[".value"][0] + m[".value"][2], 1),
                                     "valueLeft": m[".value"][0], "boxWidth": box[0],
                                     "libraryCaptionWidth": lib_caption, "labelRow": m[".label"][2:]})
        out["instrumentfield"]["cases"] = rows
        b.close()
    (HERE / "web/instruments.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    bad = [r for r in out["readout"]["cases"] if not r["narrowerThanLibrary"]]
    print(f"readout: {len(out['readout']['cases'])} cases, {len(bad)} wider than the library's text width; "
          f"identifier property: {[k for k, v in out['readout'].items() if k.startswith('identifier_') and v['drawsIdentifier']]}; "
          f"groups thousands: {out['readout']['groupsThousands']} / {out['instrumentfield']['groupsThousands']}")
    worst = max(out["readout"]["cases"], key=lambda r: r["heightOver"])
    print("readout height over the box (px):", sorted({(tuple(r["box"]), r["heightOver"]) for r in out["readout"]["cases"]}))
    print("field over the box (w, h), worst:", max((r["overBox"] for r in out["instrumentfield"]["cases"]),
                                                  key=lambda o: o[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
