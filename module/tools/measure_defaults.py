"""Measure the runtime default of every property of the wrapped OpenBridge elements.

The custom elements manifest gives names and types but, for enum-typed fields, no default: the
default is an initialiser in the element's constructor. Creating each element in a browser and
reading its properties measures the defaults instead of guessing them.

Usage (ctig's .venv for Playwright), after `npm run build` in module/web:
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe module/tools/measure_defaults.py
Writes module/web/defaults.json.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
BUNDLE = HERE / "web/dist/ob-components.js"
MANIFEST = HERE / "web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json"
TAGS = ["obc-pump", "obc-automation-tank", "obc-motor", "obc-fan", "obc-digital-valve", "obc-analog-valve", "obc-filter", "obc-indicator-generator", "obc-automation-button", "obc-transmitter", "obc-instrument-field", "obc-alert-list-details", "obc-alert-list-page-small", "obc-resistor", "obc-damper", "obc-switch", "obc-capacitor", "obc-diodes", "obc-ground", "obc-source", "obc-converter", "obc-transformer", "obc-bipolar-transistor", "obc-mosfet", "obc-logic", "obc-router", "obc-automation-badge", "obc-hydraulic-check-valve", "obc-valve-analog-two-way-icon", "obc-valve-analog-three-way-icon", "obc-indicator-battery", "obc-indicator-engine", "obc-indicator-tank-atmospheric", "obc-automation-readout"]


def fields(tag: str) -> list[str]:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for mod in m["modules"]:
        for d in mod.get("declarations", []):
            if d.get("tagName") == tag:
                return [a["fieldName"] for a in d.get("attributes", []) if a.get("fieldName")]
    raise SystemExit(f"{tag} not in the manifest")


def main() -> int:
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.set_content("<html><body></body></html>")
        page.add_script_tag(content=BUNDLE.read_text(encoding="utf-8"))
        for tag in TAGS:
            out[tag] = page.evaluate("""([tag, names]) => {
                const el = document.createElement(tag);
                document.body.appendChild(el);
                const r = {};
                for (const n of names) { const v = el[n]; r[n] = v === undefined ? '__undefined__' : v; }
                el.remove();
                return r }""", [tag, fields(tag)])
        b.close()
    (HERE / "web/defaults.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print({t: len(v) for t, v in out.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
