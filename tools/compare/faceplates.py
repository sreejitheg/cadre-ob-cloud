"""Faceplate sweep (G11): every device on a page opens its faceplate, and no faceplate shows a
binding quality overlay or the empty "Select a device" body. Every tab of every faceplate is
opened (COB-076): no pane may be empty or show an overlay or an error badge, and the Alarms tab
must list only the device's alarms, as many as its tab label counts, and the number
`--expect-alarms` names for a device in the plant's initial state.

The descriptors are the oracle. Each symbol marked `device` must open the faceplate dock with its
identifier (its `tag` parameter, else its `id`) as the title. The sweep clicks every leaf embedded
view on the page (a symbol at the centre of its 48 px box, any other view at its centre) and every
component of the Cadre HMI Components module (at the centre of its box), reads
the dock, counts `.ia_qualityOverlay` inside it, and closes the dock again before the next click.
A device that never opened is reported missing.

A faceplate polls its device and binds no member's tag, so a member of bad quality draws no overlay:
the faceplate names it on a line ("Bad quality: ..."), and the sweep fails on that line as on an
overlay. With a device model (`--devices-file`, wiki page 08 section 3.1) the sweep also expects of each
device the tabs its members give it, and checks each alarm row against the device's source patterns
(the stock table shows the source path in a column) instead of looking for the title in the row: a
device's alarms may stay on source tags that do not carry its identifier.

Usage (ctig's .venv for Playwright):
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/faceplates.py
        --base http://localhost:8088/data/perspective/client/cadre_hmi_wtp
        --descriptor screens/wtp/overview.json [--descriptor ...] --out workspace/wtp/faceplates
        [--devices-file devices.json] [--shallow TITLE,TITLE]
`--shallow` lists faceplate titles whose device an earlier sweep proved: such a device is clicked open and its title,
overlays and empty state are read, but its tabs are not walked (COB-195). Every other device is swept in full.
Exit 1 when any device is missing or any faceplate is faulty.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LEAF_MARK = "data-g11-leaf"   # the attribute the measure stamps on each leaf's clicked element: its index (COB-201)
# The module components a click opens a device's faceplate from: those of the kinds the module draws for the library
# (`screen.MODULE_KIND`; a unit test holds the two together). The module-only glyphs, the charts and the 33 frame
# components open no faceplate, and some animate (a blinking alert button, an indeterminate progress ring, a clock):
# swept as leaves they changed the count under the guard of `sweep` (T2, 1641 leaves, 2026-11-03).
DEVICE_COMPONENTS = ("cadre.ob.analogvalve", "cadre.ob.damper", "cadre.ob.fan", "cadre.ob.filter", "cadre.ob.generator",
                     "cadre.ob.instrumentfield", "cadre.ob.motor", "cadre.ob.pump", "cadre.ob.readout", "cadre.ob.switch",
                     "cadre.ob.tank", "cadre.ob.valve")
LEAF_POINTS = """() => {
  const out = [], seen = new Set();
  document.querySelectorAll('[data-g11-leaf]').forEach(e => e.removeAttribute('data-g11-leaf'));
  const mark = (e, p) => { e.setAttribute('data-g11-leaf', String(out.length)); out.push(p); };
  for (const v of document.querySelectorAll('[data-component="ia.display.view"]')) {
    if (v.closest('[class*="docked-view"]')) continue;
    if (v.querySelector('[data-component="ia.display.view"]')) continue;
    let r = v.getBoundingClientRect();
    if (r.width < 8 || r.height < 8) continue;
    const sym = [...v.querySelectorAll('[data-component="ia.container.coord"]')].find(c => {
      const b = c.getBoundingClientRect(); return Math.round(b.width) === 48 && Math.round(b.height) === 48 });
    if (sym) r = sym.getBoundingClientRect();
    const p = [Math.round(r.x + r.width / 2), Math.round(r.y + r.height / 2)];
    if (!seen.has(p.join(','))) { seen.add(p.join(',')); mark(sym || v, p); }
  }
  // components of the Cadre HMI Components module that draw a device: their box is the symbol (pump) or the tank
  for (const m of document.querySelectorAll('__DEVICE_COMPONENTS__')) {
    if (m.closest('[class*="docked-view"]')) continue;
    const r = m.getBoundingClientRect();
    const p = [Math.round(r.x + r.width / 2), Math.round(r.y + r.height / 2)];
    if (r.width >= 8 && !seen.has(p.join(','))) { seen.add(p.join(',')); mark(m, p); }
  }
  return out }"""
LEAF_POINTS = LEAF_POINTS.replace("__DEVICE_COMPONENTS__", ", ".join(f'[data-component="{c}"]' for c in DEVICE_COMPONENTS))


def bring_into_view(page, index: int) -> bool:
    """Scroll the index-th leaf (the element `LEAF_POINTS` stamped) into view, and say whether it was found: a leaf below
    the fold of a tall page (the component test page) is not under the pointer until it is scrolled to (COB-201)."""
    loc = page.locator(f"[{LEAF_MARK}='{index}']")
    try:
        if not loc.count():
            return False
        loc.first.scroll_into_view_if_needed(timeout=5000)
        return True
    except Exception:   # a leaf that cannot scroll is clicked where it was measured, as before
        return False


def expected_devices(desc: dict) -> set[str]:
    def walk(g):
        for it in g.get("items", []):
            if "items" in it:
                yield from walk(it)
            elif "kind" in it:
                yield it
    items = list(desc.get("symbols", []))
    for row in desc.get("rows", []):
        for card in row:
            items += card.get("items", [])
            if "body" in card:
                items += list(walk(card["body"]))
    # a plain symbol with `faceplate` (a device id, COB-165) opens that device's faceplate as a device symbol does
    return {faceplate_title(s) for s in items if s.get("device") or s.get("faceplate")}


# The instrument kinds, whose faceplate is titled by the symbol's tag, else its label (`library.SELECT_INSTRUMENT`, and
# `screen.embed_module` for `screen.MODULE_INSTRUMENTS`; a unit test holds the two lists together). Every other device
# symbol's faceplate is titled by its tag, else its identifier. The sweep expected the identifier for an instrument with
# a label and no tag, and so counted the component test page's field `TB_FIELD`, titled `Temp`, as missing (T0 to T2).
INSTRUMENT_KINDS = ("readout", "instrument-field")


def faceplate_title(sym: dict) -> str:
    """The title the faceplate a symbol opens carries, by the library's rule for its kind."""
    params = sym.get("params", {})
    if sym.get("kind") in INSTRUMENT_KINDS:
        return params.get("tag") or params.get("label") or sym["id"]
    return params.get("tag") or sym["id"]


QUALITY_LINE = "Bad quality:"   # framework._quality_line: a present member whose quality is not good


def source_core(pattern: str) -> str:
    """The tag path a source pattern names, without its wildcards: 'prov:default:/tag:site/P1_OE:/alm:*'
    gives 'site/P1_OE', and a device folder's 'prov:default:/tag:root/P1/*' gives 'root/P1/'. A row of
    the stock table that shows a source path under the pattern contains it."""
    tag = pattern.split(":/tag:", 1)[-1].split(":/alm:", 1)[0]
    return tag.replace("*", "")


def folder_pattern(folder: str) -> str:
    """The source pattern of a device folder, as `cadre.hmi.device_source` writes it."""
    prov, path = folder[1:].split("]", 1)
    return f"prov:{prov}:/tag:{path.strip('/')}/*"


def row_belongs(row: str, title: str, device: dict | None = None) -> bool:
    """An alarm row belongs to the open device. Without a device model the row carries the device's
    identifier (the sample's display paths). With one, the row carries a source path under one of the
    device's source patterns (the stock table), or the device's folder as the record's `tagId` (the
    module's list)."""
    if device is None:
        return title in row
    cores = [c for c in (source_core(s) for s in device["sources"]) if c]
    return any(c in row for c in cores) or device["folder"] in row


def device_expectations(descs: list[dict], model: dict, style: str = "openbridge") -> dict[str, dict]:
    """What a device model says of each device the descriptors draw, by the title its faceplate
    shows (the symbol's `tag`, else its id): the device's folder, the source patterns of its alarms,
    and the tabs its members give its faceplate (`framework.expected_tabs`). A controller or a
    sequence, whose Trend tab follows the trend index (`framework.trend_by_index`), leaves the tab to
    the tag model where its model entry names no `trend`; the sweep does not read the tag model, and
    `trend_open` then tells it not to judge that tab. A device's faceplate style is its model's, else
    `style`, the project's default (COBD-045)."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from hmi import framework
    root = model.get("tagRoot", "")
    devices = {f"{root}/{d['id']}": d for d in model.get("devices", [])}
    out: dict[str, dict] = {}

    def walk(g):
        for it in g.get("items", []):
            if "items" in it:
                yield from walk(it)
            elif "kind" in it:
                yield it
    for desc in descs:
        items = list(desc.get("symbols", []))
        for row in desc.get("rows", []):
            for card in row:
                items += card.get("items", [])
                if "body" in card:
                    items += list(walk(card["body"]))
        for s in items:
            dev = s.get("device") or s.get("faceplate")
            if not dev:
                continue
            rel = dev if isinstance(dev, str) else s["id"]
            folder = s.get("params", {}).get("deviceId") or f"{desc.get('tagRoot', '')}/{rel}"
            d = devices.get(folder)
            if d is None:
                continue
            kind = str(d.get("kind", "")).lower()
            out[s.get("params", {}).get("tag") or s["id"]] = {
                "folder": folder,
                "sources": list(d["alarmSources"]) if "alarmSources" in d else [folder_pattern(folder)],
                "tabs": framework.expected_tabs(kind, d["members"], d.get("trend", ()), d.get("faceplate", style)),
                "trend_open": framework.trend_by_index(kind) and "trend" not in d,
                "style": d.get("faceplate", style)}
    return out


def tab_names(names: list[str], device: dict | None) -> list[str]:
    """The tab captions among `names`: on an asm faceplate "Maintenance" is the move beside Take control and Release
    (its maintenance rows are on Config), never a tab."""
    if device and device.get("style") == "asm":
        return [n for n in names if n.strip() != "Maintenance"]
    return list(names)


def is_open(page, dock) -> bool:
    """A closed dock keeps its size and moves outside the viewport (measured: x equal to the
    viewport width), so open means inside the viewport."""
    if not dock.count():
        return False
    b = dock.first.bounding_box()
    return bool(b and b["width"] > 0 and b["x"] < page.viewport_size["width"] - 1)


# the tab labels of both faceplate styles; the `asm` style names its interlock tab Interlock (COBD-045)
TAB = re.compile(r"^\s*(Control|Alarms|Interlocks?|Values|Trend|Maintenance|Tuning|Status|Home|Config|Diagnostics|Info)"
                 r"(\s*\((\d+)\))?\s*$")
MODULE_LIST = """() => {
  const d = document.querySelector('.docked-view-right');
  const el = d && [...d.querySelectorAll('obc-alert-list-details, obc-alert-list-page-small')]
    .find(e => e.getBoundingClientRect().width > 0);
  if (!el) return null;
  return (el.alerts || []).map(a => (a.source || '') + ' ' + (a.text || '') + ' ' + (a.tagId || ''));
}"""


def alarm_rows(page, right) -> list[str] | None:
    """The rows the Alarms tab shows: the stock table's body rows, or the alerts of the module's
    alarm list (shadow DOM, read from the element). None while neither has rendered."""
    mod = page.evaluate(MODULE_LIST)
    if mod is not None:
        return mod
    if right.locator(".alarmTableEmptyMessage:visible").count():
        return []
    rows = right.locator(".ia_table__body__row:visible")
    return [re.sub(r"\s+", " ", rows.nth(k).inner_text()).strip() for k in range(rows.count())] or None


def tab_faults(title: str, shown: list[str], device: dict | None) -> list[str]:
    """The tabs a faceplate shows against those the device model gives the device; none to judge
    without a model."""
    if device is None:
        return []
    want, got = list(device["tabs"]), list(shown)
    if device.get("trend_open"):
        want, got = [t for t in want if t != "Trend"], [t for t in got if t != "Trend"]
    return [] if want == got else [f"{title}: tabs {shown}, the device model gives {device['tabs']}"]


def open_tabs(page, right, title: str, expect: dict, expect_ilk: dict | None = None,
              device: dict | None = None) -> tuple[dict, list[str]]:
    """Click every tab of the open faceplate. Each pane must render without a quality overlay, an
    error badge or a line naming a member of bad quality; the Alarms tab must show a list whose rows
    all belong to the device (`row_belongs`), agree with the count on the tab, and match `expect`
    (rows expected for a device in the plant's initial state). With `device` (its entry of
    `device_expectations`) the tabs shown must be those its members give it."""
    out, faults = {}, []
    buttons = right.locator('[data-component="ia.input.button"]')
    names = [buttons.nth(k).inner_text().strip() for k in range(buttons.count())]
    # a tab a device does not carry is hidden (the Interlocks tab without an `ilk` folder)
    keep = set(tab_names(names, device))
    tabs = [(k, n) for k, n in enumerate(names) if n in keep and TAB.match(n) and buttons.nth(k).is_visible()]
    if expect_ilk and title in expect_ilk and not any(TAB.match(n).group(1).startswith("Interlock") for _, n in tabs):
        faults.append(f"{title}: no Interlocks tab, expected {expect_ilk[title]} conditions")
    faults += tab_faults(title, [TAB.match(n).group(1) for _, n in tabs], device)
    for k, name in tabs:
        key = TAB.match(name).group(1)
        # by its name among the visible buttons: a tab's pane can add or hide buttons, so an index read before the
        # first click may name a hidden one later (a test device with four modes, Level 4 open item 2)
        same = [j for j in range(buttons.count()) if buttons.nth(j).inner_text().strip() == name and buttons.nth(j).is_visible()]
        if not same:      # hidden now: a button of a mode pane with a tab's name, not a tab the person can press
            continue
        buttons.nth(same[0]).click()
        rows = None
        for _ in range(35 if key == "Alarms" else 8):
            page.wait_for_timeout(200)
            if key == "Alarms":
                rows = alarm_rows(page, right)
                if rows is not None:
                    break
        page.wait_for_timeout(600)
        rec = {"overlays": right.locator(".ia_qualityOverlay").count(),
               "badges": right.locator(".view-state-display").count()}
        body = right.inner_text()
        if rec["overlays"] or rec["badges"] or "View Not Found" in body:
            faults.append(f"{title} {key}: {rec['overlays']} overlays, {rec['badges']} error badges")
        if QUALITY_LINE in body:   # a polled member of bad quality: said in words, no overlay
            line = next((ln.strip() for ln in body.splitlines() if QUALITY_LINE in ln), QUALITY_LINE)
            faults.append(f"{title} {key}: {line}")
        if key == "Alarms":
            # the count polls every 2 s and the stock table every 5 s: read both until they agree
            for _ in range(4):
                rows = alarm_rows(page, right)
                label = TAB.match(buttons.nth(k).inner_text().strip())
                if rows is not None and label and int(label.group(3) or 0) == len(rows):
                    break
                page.wait_for_timeout(2000)
            rec.update({"rows": rows, "label_count": int(label.group(3) or 0) if label else None})
            if rows is None:
                faults.append(f"{title} Alarms: no alarm list rendered")
            else:
                if rec["label_count"] != len(rows):
                    faults.append(f"{title} Alarms: tab says {rec['label_count']}, list shows {len(rows)}")
                foreign = [r for r in rows if not row_belongs(r, title, device)]
                if foreign:
                    faults.append(f"{title} Alarms: rows of another device {foreign[:2]}")
                if title in expect and len(rows) != expect[title]:
                    faults.append(f"{title} Alarms: {len(rows)} rows, expected {expect[title]}")
        elif key == "Interlocks":
            # each condition row shows its live and required values and its state; the tab counts the
            # conditions that hold the device, not met or latched (COBD-023)
            rows = body.count("Required:")
            held = body.count("Not met") + body.count("Latched")
            label = TAB.match(buttons.nth(k).inner_text().strip())
            rec.update({"rows": rows, "not_met": held, "label_count": int(label.group(3) or 0) if label else None})
            if rows == 0:
                faults.append(f"{title} Interlocks: empty pane")
            if rec["label_count"] != held:
                faults.append(f"{title} Interlocks: tab says {rec['label_count']}, {held} conditions not met or latched")
            if expect_ilk and title in expect_ilk and rows != expect_ilk[title]:
                faults.append(f"{title} Interlocks: {rows} conditions, expected {expect_ilk[title]}")
        elif not body.strip():
            faults.append(f"{title} {key}: empty pane")
        out[key] = rec
    if tabs:
        buttons.nth(tabs[0][0]).click()
        page.wait_for_timeout(300)
    return out, faults


def settled_points(page, tries: int = 30, pause: int = 1000) -> list:
    """The leaves of the page once their count holds still between two measures `pause` ms apart (at most `tries`
    measures). A large page (the component test page of tranche T1, 830 leaves) still sizes an element after the
    load and the fixed wait, and the guard of `sweep` then took that for a change made by a click."""
    points = page.evaluate(LEAF_POINTS)
    for _ in range(tries):
        page.wait_for_timeout(pause)
        again = page.evaluate(LEAF_POINTS)
        if len(again) == len(points):
            return again
        points = again
    return points


def sweep(page, base: str, route: str, expected: set[str], expect_alarms: dict | None = None,
          expect_ilk: dict | None = None, devices: dict | None = None, shallow: set[str] | None = None) -> dict:
    """Sweep one page. A device whose title is in `shallow` is checked by its opener only: its record is
    `{"overlays", "empty", "shallow": true}` with no `tabs`, and the tab walk (`open_tabs`) is not run for it."""
    page.goto(base + route, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    right = page.locator(".docked-view-right")
    points = settled_points(page)
    opened, faults = {}, []
    for i in range(len(points)):
        now = page.evaluate(LEAF_POINTS)
        if len(now) != len(points):
            faults.append(f"leaf views changed from {len(points)} to {len(now)} after click {i}")
            break
        if bring_into_view(page, i):
            now = page.evaluate(LEAF_POINTS)   # the scroll moved the leaf: measure it where it is now
        if len(now) != len(points):
            faults.append(f"leaf views changed from {len(points)} to {len(now)} after click {i}")
            break
        page.mouse.click(*now[i])
        for _ in range(10):
            page.wait_for_timeout(200)
            if is_open(page, right):
                break
        if not is_open(page, right):
            continue
        page.wait_for_timeout(1800)   # tag bindings settle; a bad one shows its overlay by now
        title = right.locator('[data-component="ia.display.label"]').first.inner_text().strip()
        body = right.inner_text()
        overlays = right.locator(".ia_qualityOverlay").count()
        opened[title] = {"overlays": overlays, "empty": "Select a device" in body}
        if overlays or "Select a device" in body:
            faults.append(f"{title}: {overlays} quality overlays" + (", empty faceplate" if "Select a device" in body else ""))
        if title in (shallow or ()):
            opened[title]["shallow"] = True
        else:
            tabs, found = open_tabs(page, right, title, expect_alarms or {}, expect_ilk, (devices or {}).get(title))
            opened[title]["tabs"] = tabs
            faults += found
        right.locator('[data-component="ia.container.coord"]').first.click()
        for _ in range(10):
            page.wait_for_timeout(200)
            if not is_open(page, right):
                break
    missing = sorted(expected - set(opened))
    extra = sorted(set(opened) - expected)
    return {"route": route, "leaf_views": len(points), "expected": len(expected), "opened": opened,
            "missing": missing, "unexpected": extra, "faults": faults,
            "ok": not missing and not faults and not extra}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--descriptor", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect-alarms", default="",
                    help="rows each named device's Alarms tab shows, for example P-502=1,P-202=0")
    ap.add_argument("--devices-file", default=None,
                    help="the device model of the build: alarm rows are checked against each device's "
                         "source patterns, and each faceplate's tabs against the device's members")
    ap.add_argument("--shallow", default="", metavar="TITLES",
                    help="comma list of faceplate titles (the label the sweep reads as the title) whose device is "
                         "checked by its opener only: the faceplate opens and is read, its tabs are not walked")
    ap.add_argument("--height", type=int, default=1400,
                    help="the viewport's height; a long page (the component test page, 8,600 px) needs its own")
    ap.add_argument("--viewport", default=None, metavar="WxH",
                    help="the viewport, WIDTHxHEIGHT (default 2700 wide and --height high, as before)")
    ap.add_argument("--faceplate", choices=("openbridge", "asm"), default="openbridge",
                    help="the project's default faceplate style (screen.py --faceplate, COBD-045), against which a "
                         "device without a style of its own in the device model is judged")
    a = ap.parse_args()
    width, height = 2700, a.height
    if a.viewport:
        try:
            width, height = (int(n) for n in a.viewport.lower().split("x"))
        except ValueError:
            ap.error(f"--viewport is WIDTHxHEIGHT, not {a.viewport!r}")
    shallow = {x.strip() for x in a.shallow.split(",") if x.strip()}
    expect = {k: int(v) for k, v in (p.split("=") for p in a.expect_alarms.split(",") if p)}
    from playwright.sync_api import sync_playwright
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    descs = [json.loads(Path(d).read_text(encoding="utf-8")) for d in a.descriptor]
    devices = None
    if a.devices_file:
        devices = device_expectations(descs, json.loads(Path(a.devices_file).read_text(encoding="utf-8")),
                                     a.faceplate)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": width, "height": height}).new_page()
        for desc in descs:
            r = sweep(page, a.base.rstrip("/"), desc["screen"]["route"], expected_devices(desc), expect,
                      devices=devices, shallow=shallow)
            results.append(r)
            print(f"{r['route']:16s} {'PASS' if r['ok'] else 'FAIL'}  devices {len(r['opened'])}/{r['expected']}"
                  f"  leaf views {r['leaf_views']}  missing {r['missing']}  unexpected {r['unexpected']}"
                  f"  faults {r['faults'][:6]}")
        browser.close()
    ok = all(r["ok"] for r in results)
    (out / "faceplates.json").write_text(json.dumps({"ok": ok, "routes": results}, indent=1), encoding="utf-8")
    print("FACEPLATES", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
