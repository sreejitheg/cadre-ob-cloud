"""Measure the runtime default of every property of the wrapped OpenBridge elements.

The custom elements manifest gives names and types but, for enum-typed fields, no default: the
default is an initialiser in the element's constructor. Creating each element in a browser and
reading its properties measures the defaults instead of guessing them.

Usage (ctig's .venv for Playwright), after `npm run build` in module/web:
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe module/tools/measure_defaults.py [--bundle <file>]
Writes module/web/defaults.json.

`node_modules` and `dist/` are read from `verify_pin.web_root()` (the sibling `web` folder, or the read only folder named
by `CADRE_OB_WEB_ROOT`, see `verify_pin.py`); the result is always written to this module's own `web/defaults.json`.
`--bundle` names a bundle other than `dist/ob-components.js`, for a host whose `dist/` was built before an element was
added to `entry.js`: the package's own `bundle/openbridge-webcomponents.bundle.js` (an ES module, which this loads as a
module) defines every element from the same pinned source, so it measures the same defaults. The build step on the
host that runs esbuild uses the default bundle. Only those two bundles are measured: the package's own (its hash is in
the pin manifest, which `require_pin` checks first) and a `dist/ob-components.js` that `npm run build` recorded for this
checkout's lock and entry file; any other file is refused (NOTE-WFB-10 section 13 invariant 4).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_pin  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
WEB = verify_pin.web_root()
BUNDLE = WEB / "dist/ob-components.js"
MANIFEST = WEB / "node_modules/@oicl/openbridge-webcomponents/custom-elements.json"
TAGS = ["obc-pump", "obc-automation-tank", "obc-motor", "obc-fan", "obc-digital-valve", "obc-analog-valve", "obc-transmitter", "obc-instrument-field", "obc-alert-list-details", "obc-alert-list-page-small", "obc-automation-button"]


def fields(tag: str) -> list[str]:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for mod in m["modules"]:
        for d in mod.get("declarations", []):
            if d.get("tagName") == tag:
                return [a["fieldName"] for a in d.get("attributes", []) if a.get("fieldName")]
    raise SystemExit(f"{tag} not in the manifest")


def require_trusted_bundle(bundle: Path, web: Path | None = None, checkout: Path | None = None) -> None:
    """End the process unless `bundle` is the pinned package's own bundle or the recorded `dist` bundle of `web`."""
    web = Path(web) if web else WEB
    own = web / "node_modules" / verify_pin.PACKAGE / "bundle" / "openbridge-webcomponents.bundle.js"
    built = web / verify_pin.BUNDLE_REL
    chosen = Path(bundle).resolve()
    if chosen == own.resolve():
        return   # listed in the pin manifest, which require_pin has checked
    if chosen == built.resolve():
        verify_pin.require_bundle_record(web, checkout or HERE / "web")
        return
    raise SystemExit(f"measure_defaults: {bundle} is neither the pinned package's own bundle nor the recorded "
                     f"{verify_pin.BUNDLE_REL}; refusing to measure it")


def main() -> int:
    verify_pin.require_pin()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bundle", type=Path, default=BUNDLE, help="the bundle to measure (default dist/ob-components.js)")
    bundle = ap.parse_args().bundle
    require_trusted_bundle(bundle)
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.set_content("<html><body></body></html>")
        text = bundle.read_text(encoding="utf-8")
        if "\nexport {" in text:     # the package's ES module bundle: its elements are defined once the module has run
            page.add_script_tag(content=text, type="module")
            page.wait_for_function("(tags) => tags.every((t) => customElements.get(t))", arg=TAGS, timeout=120000)
        else:
            page.add_script_tag(content=text)
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
