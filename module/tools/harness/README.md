# Browser harness for the module (offline)

`harness.html` loads the built bundle (`../../gateway/.../cadre-ob.js` and `cadre-ob.css`) in Chromium with a stub of the
Perspective client (`PerspectiveClient.Component`, `ComponentRegistry`, a property tree and a `store.props.write`) and React
18 from `vendor/` (UMD builds, not tracked: copy `react.production.min.js` as `vendor/react.js` and
`react-dom.production.min.js` as `vendor/react-dom.js` from any React 18 install).

Run after `npm run build` in `module/web` and `python module/tools/gen_module_assets.py`. `PLAYWRIGHT` names the Playwright module to import (a `file:///` URL of its `index.mjs` when it is not installed beside the harness); `CHROMIUM` names a Chromium executable when Playwright's own is absent:

    node module/tools/harness/devices.mjs   # status, duty, out of service and stretch on pump, motor, fan, readout
    node module/tools/harness/zoom.mjs      # canvas zoom: wheel, keys, pinch, point under the pointer, guard, unmount
    node module/tools/harness/alertselect.mjs   # alarm lists: row ticks, toggle, row click, stale ids, selectable false (0.4.2)
    node module/tools/harness/frame.mjs     # frame leaf components (T2, F1): slot properties, events and payloads, optional texts
    node module/tools/harness/items.mjs     # the `items` mechanism (T2, F1) on a synthetic host built by items_bundle.py (run from the repository root)

Each prints one PASS or FAIL line per check. The harness proves the wrappers and the zoom component against real
OpenBridge elements; it cannot prove the Perspective client's own behaviour (the property write, the binding round
trip, the Designer), which only the gateway shows.
