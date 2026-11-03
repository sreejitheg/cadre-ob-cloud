"""Glass helpers shared by the walks of the gateway gates: what a Playwright session needs to act as an
operator on a Cadre HMI project and to read what the operator would read.

Gate G10 (`functional.py`, written by hand for the water treatment sample) and the generated walk
(`walk.py`, built from a project's descriptors) both import this module, so one implementation signs in,
opens a device from its symbol, finds the docks, the buttons and the tabs, reads a symbol and a readout
under both renderings, types into an entry field, opens the alarm menu and counts quality overlays. The
first part was moved here from `functional.py` unchanged on 2026-10-11 (`functional` still exports every
name); the second part, from `page_faults` on, was written for the generated walk.

The two parts overlap on purpose. Gate G10 must behave exactly as it did before the move, so its
helpers stay as they were (`open_device`, `control_tab`, `button`, `CRAFTED_CLICK`, `DISABLED`,
`READOUT_AT`, `CHART_LINE`), and the generated walk has its own (`open_faceplate`, `tab`,
`dock_button`, `crafted_press`, `dock_field`, `SYMBOL_AT`, `DOCK_SERIES`), which find a control by its
caption and its group and answer what they saw instead of raising. `page_faults` and `clean` restate
the pass conditions of `capture.capture` for a page already open in a session; gate G8 itself stays
`capture.py`, which opens each route in a fresh session.

Every DOM fact used here was measured on the glass before use; a helper says where and when. Nothing
here emits a view, and nothing prints or returns the test login.

Runs under an interpreter with Playwright (ctig's `.venv`), as the gates do.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

# The test login of NEEDS N-COB-9: `user=` and `password=` lines in a local file outside the repository.
LOGIN_FILE = Path(os.environ.get("CADRE_TEST_LOGIN", "C:/Users/pcs_d/.cadre/test-login.properties"))


def read_login(path: Path = LOGIN_FILE) -> dict | None:
    """The test login, or None when the file is absent or incomplete. Its values are never printed."""
    if not path.exists():
        return None
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return {"user": out["user"], "password": out["password"]} if out.get("user") and out.get("password") else None


MODULE_PUMP = r"""(tag) => {
  // a symbol of the Cadre OpenBridge module (pump, motor, fan, valves: the elements that state `tag`) whose
  // (shadow DOM) text shows the tag; a valve states `open` where the others state `on`
  for (const m of document.querySelectorAll('[data-component^="cadre.ob."]')) {
    if (m.closest('[class*="docked-view"]')) continue;
    const el = [...m.querySelectorAll('*')].find(e => e.tagName.includes('-'));
    let txt = '';
    const walk = (r) => { for (const n of r.querySelectorAll('*')) { if (n.shadowRoot) { txt += ' ' + n.shadowRoot.textContent; walk(n.shadowRoot); } } };
    if (el && el.shadowRoot) { txt = el.shadowRoot.textContent; walk(el.shadowRoot); }
    if (el && el.tag !== undefined && (el.tag === tag || txt.includes(tag))) {
      const b = m.getBoundingClientRect();
      const on = el.on ?? el.open;
      return {x: b.x + b.width / 2, y: b.y + b.height / 2, text: txt.replace(/\s+/g, ' ').trim(),
              alert: el.alert, mode: el.alertFrameMode, on: on, speed: el.speedInPercent};
    }
  }
  return null }"""


def module_pump(page, tag):
    return page.evaluate(MODULE_PUMP, tag)


def symbol(page, tag):
    """The embedded symbol view whose readout shows `tag`, and the centre of its 48 px symbol;
    for a pump of the Cadre OpenBridge module, (None, centre of its symbol box)."""
    m = module_pump(page, tag)
    if m:
        return None, (m["x"], m["y"])
    views = page.locator('[data-component="ia.display.view"]', has_text=tag)
    for i in range(views.count()):
        v = views.nth(i)
        coords = v.locator('[data-component="ia.container.coord"]')
        for j in range(coords.count()):
            b = coords.nth(j).bounding_box()
            if b and round(b["width"]) == 48 and round(b["height"]) == 48:
                return v, (b["x"] + 24, b["y"] + 24)
    raise AssertionError(f"symbol {tag} not found")


def readout_text(page, tag):
    m = module_pump(page, tag)
    if m:
        return m["text"]
    v, _ = symbol(page, tag)
    return re.sub(r"\s+", " ", v.inner_text()).strip()


def speed_shown(page, tag, value):
    """The pump runs at `value` per cent: the readout text of a library symbol ('80 %'); for a
    module pump the element's bound state, since its readout text is split across shadow DOM
    nodes ('080' is a hinted zero and the digits)."""
    m = module_pump(page, tag)
    if m:
        return bool(m["on"]) and abs(float(m["speed"] or 0) - value) < 0.5, f"on {m['on']} speedInPercent {m['speed']}"
    text = readout_text(page, tag)
    return re.search(rf"(^|[^0-9])0*{value}\s*%", text) is not None, text


VALUE_AT = r"""(find) => {
  // what a readout or an instrument field of the Cadre OpenBridge module prints, found by its identifier (`idTag`),
  // its caption (the element's `tag` and `unit`), or the text it prints: the value, its unit, the identifier
  const printed = (root) => { let t = '';      // in document order, down the shadow roots, no style element
    for (const n of root.childNodes) {
      if (n.nodeType === 3) t += n.textContent;
      else if (n.nodeType === 1 && n.tagName !== 'STYLE') {
        if (n.shadowRoot) t += ' ' + printed(n.shadowRoot);
        t += ' ' + printed(n);
      }
    }
    return t; };
  for (const m of document.querySelectorAll('[data-component="cadre.ob.readout"], [data-component="cadre.ob.instrumentfield"]')) {
    if (m.closest('[class*="docked-view"]')) continue;
    const el = [...m.querySelectorAll('*')].find(e => e.tagName.includes('-'));
    if (!el || !el.shadowRoot) continue;
    const text = printed(el.shadowRoot).replace(/\s+/g, ' ').trim();
    if (el.idTag === find || [el.tag, el.unit].filter(Boolean).join(' ') === find || text.includes(find)) return text;
  }
  return null }"""


def value_of(page, tag):
    """The text a readout or a field shows for `tag`: the library's view prints it as its own text, the module's
    component down its shadow roots (`VALUE_AT`)."""
    text = page.evaluate(VALUE_AT, tag)
    if text is not None:
        return text
    box = page.locator('[data-component="ia.display.view"]', has_text=tag).first
    return re.sub(r"\s+", " ", box.inner_text()).strip()


STATUS_SHOWN = r"""(tags) => {
  // for each identifier, the text its automation symbol prints beside the symbol without the identifier itself: the
  // state readout (On or Off, a speed, an opening) or nothing; null where no symbol shows the identifier. A module
  // element prints into its shadow roots (style elements left out), a library view into its own labels.
  const printed = (root) => { let t = '';
    for (const n of root.childNodes) {
      if (n.nodeType === 3) t += n.textContent;
      else if (n.nodeType === 1 && n.tagName !== 'STYLE') { if (n.shadowRoot) t += ' ' + printed(n.shadowRoot); t += ' ' + printed(n); }
    }
    return t; };
  const out = {};
  for (const tag of tags) {
    let text = null;
    for (const m of document.querySelectorAll('[data-component^="cadre.ob."]')) {
      if (m.closest('[class*="docked-view"]')) continue;
      const el = [...m.querySelectorAll('*')].find(e => e.tagName.includes('-'));
      if (el && el.tag === tag && el.shadowRoot) { text = printed(el.shadowRoot); break; }
    }
    if (text === null) {
      const vs = [...document.querySelectorAll('[data-component="ia.display.view"]')]
        .filter(v => !v.closest('[class*="docked-view"]') && v.innerText.includes(tag));
      if (vs.length) text = vs[vs.length - 1].innerText;
    }
    out[tag] = text === null ? null : text.split(tag).join(' ').replace(/\s+/g, ' ').trim();
  }
  return out }"""


def status_shown(page, tags) -> dict:
    """For each identifier, whether its symbol prints a state readout (`STATUS_SHOWN`): None where no symbol shows it."""
    texts = page.evaluate(STATUS_SHOWN, list(tags))
    return {t: (None if v is None else bool(re.search(r"\b(On|Off)\b|%", v))) for t, v in texts.items()}


IDENTS_SHOWN = r"""(tags) => {
  // for each identifier, whether the page shows it outside the docks: in the rendered text of the library's views,
  // or in what a module element prints into its shadow roots (style elements left out)
  const printed = (root) => { let t = '';
    for (const n of root.childNodes) {
      if (n.nodeType === 3) t += n.textContent;
      else if (n.nodeType === 1 && n.tagName !== 'STYLE') { if (n.shadowRoot) t += ' ' + printed(n.shadowRoot); t += ' ' + printed(n); }
    }
    return t; };
  let text = '';
  for (const v of document.querySelectorAll('[data-component="ia.display.view"]'))
    if (!v.closest('[class*="docked-view"]')) text += ' ' + v.innerText;
  for (const m of document.querySelectorAll('[data-component^="cadre.ob."]')) {
    if (m.closest('[class*="docked-view"]')) continue;
    const el = [...m.querySelectorAll('*')].find(e => e.tagName.includes('-'));
    if (el && el.shadowRoot) text += ' ' + printed(el.shadowRoot);
  }
  // a whole identifier: "PIT-301" is not shown by "DPIT-301"
  const whole = (t) => new RegExp('(^|[^A-Za-z0-9])' + t.replace(/[.*+?^${}()|[\]\\-]/g, '\\$&') + '($|[^A-Za-z0-9])');
  return Object.fromEntries(tags.map(t => [t, whole(t).test(text)])) }"""


def idents_shown(page, tags) -> dict:
    """For each identifier, whether the page shows it outside the docks (`IDENTS_SHOWN`)."""
    return page.evaluate(IDENTS_SHOWN, list(tags))


PIPE_PAINTS = r"""(colour) => {
  // the pipes of the page whose inner stroke is drawn in `colour` (a CSS colour, resolved on the page's root)
  const d = document.createElement('div'); d.style.color = colour;
  document.querySelector('.ia_container--root').appendChild(d);
  const want = getComputedStyle(d).color; d.remove();
  return [...document.querySelectorAll('path[name]')].filter(p => !p.closest('[class*="docked-view"]')
    && !p.getAttribute('name').endsWith('_outline') && getComputedStyle(p).stroke === want).map(p => p.getAttribute('name')) }"""


def pipes_in(page, colour: str) -> list[str]:
    """The names of the pipes drawn in `colour` (`PIPE_PAINTS`), for example `var(--automation-medium-fresh-water)`."""
    return page.evaluate(PIPE_PAINTS, colour)


def popup_open(page) -> bool:
    """Whether a popup is shown (a top bar menu): Perspective draws one as `.ia_popup` (measured, GF-70)."""
    loc = page.locator(".ia_popup")
    return any((loc.nth(i).bounding_box() or {}).get("width", 0) > 0 for i in range(loc.count()))


def dock(page, side):
    return page.locator(f".docked-view-{side}")


def button(scope, text):
    """The first button of `scope` captioned `text`, pressed as a confirmed command (`Confirmed`, F029). `scope` is
    a locator (a dock, a faceplate) or the page itself (the frame's toolbar, `functional.frame_steps`); a Playwright
    page has no `page` of its own, so the page of a page is itself. A button that asks nothing (a toolbar toggle) is
    pressed once and `answer` finds no question."""
    loc = scope.locator('[data-component="ia.input.button"]', has_text=re.compile(rf"^\s*{text}\s*$")).first
    return Confirmed(loc, getattr(scope, "page", scope))


# ---------------------------------------------------------------------------------------
# Confirmation (F029 of the ASMP study, COBD-045; wiki page 13 section 10.5). A faceplate's command
# button asks and writes nothing; the Confirm row beneath the tabs makes the write. A row's field holds
# what was typed until its Set writes it. An operator's press of a command is therefore two presses, and
# the helpers that press one make both: `button` and `dock_button` hand back a `Confirmed` press, and
# `type_into` presses the row's Set. The captions are those of `framework.CONFIRM`, `CANCEL` and `SET`
# (a unit test holds them together). Not yet seen on the glass: the combined gateway run (COB-143) is
# the first to measure them.
# ---------------------------------------------------------------------------------------
CONFIRM, CANCEL, SET = "Confirm", "Cancel", "Set"


def shown_button(scope, caption: str):
    """The first visible button of `scope` captioned `caption`, else None."""
    b = scope.locator('[data-component="ia.input.button"]', has_text=re.compile(rf"^\s*{caption}\s*$"))
    for k in range(b.count()):
        if b.nth(k).is_visible():
            return b.nth(k)
    return None


def answer(page, caption: str = CONFIRM, tries: int = 10) -> bool:
    """Press the faceplate's `caption` (Confirm, or a row's Set) once it shows enabled, within about
    two seconds: True when pressed, False when the press asked nothing (a start an interlock holds)."""
    for _ in range(tries):
        page.wait_for_timeout(200)
        b = shown_button(dock(page, "right"), caption)
        if b is not None and b.is_enabled():
            b.click()
            page.wait_for_timeout(300)
            return True
    return False


class Confirmed:
    """A press of a faceplate's command, as an operator makes it: a question still open from an earlier
    press is cancelled first, so that it is never answered for this one; then the button; then the
    Confirm the faceplate shows for it. Anything else is the locator's."""

    def __init__(self, locator, page):
        self._locator, self._page = locator, page

    def click(self, *args, **kwargs):
        right = dock(self._page, "right")
        if shown_button(right, CONFIRM) is not None:
            stale = shown_button(right, CANCEL)
            if stale is not None:
                stale.click()
                self._page.wait_for_timeout(300)
        self._locator.click(*args, **kwargs)
        answer(self._page, CONFIRM)

    def __getattr__(self, name):
        return getattr(self._locator, name)


LIST_INFO = r"""(sel) => {
  // the alerts an OpenBridge alarm list of the module shows: read from the element (shadow DOM)
  const el = [...document.querySelectorAll(sel)].find(e => e.getBoundingClientRect().width > 0);
  if (!el) return null;
  return (el.alerts || []).map(a => ({id: a.id, source: a.source, text: a.text, type: a.type,
                                      acked: !!a.acknowledged, active: a.active === true,
                                      by: a.acknowledged ? a.acknowledged.acknowledgedBy : null}));
}"""


def click_text_in(page, host, text):
    """Click the visible element whose text is exactly `text` inside a module element (Playwright's
    text selectors reach into open shadow roots), at its centre."""
    loc = page.locator(host).get_by_text(text, exact=True)
    for i in range(loc.count()):
        b = loc.nth(i).bounding_box()
        if b and b["width"] > 0:
            page.mouse.click(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
            return True
    return False


ROW_ACTION = r"""([host, match]) => {
  // the row of a module alarm list (shadow DOM) whose alert's source or text contains `match`, and
  // its action cell (the last cell): an ACK button, OpenBridge's no-acknowledgement icon, or nothing
  const el = [...document.querySelectorAll(host)].find(e => e.getBoundingClientRect().width > 0);
  if (!el) return null;
  const a = (el.alerts || []).find(x => String(x.source).includes(match) || String(x.text).includes(match));
  if (!a) return {found: false};
  const find = (root, sel) => {
    const hit = root.querySelector(sel); if (hit) return hit;
    for (const n of root.querySelectorAll('*')) if (n.shadowRoot) { const h = find(n.shadowRoot, sel); if (h) return h; }
    return null };
  const row = find(el.shadowRoot || el, `button[role="row"][data-row-id="${CSS.escape(String(a.id))}"]`);
  if (!row) return {found: true, row: false, id: a.id};
  const cells = [...row.children].filter(c => c.getAttribute('role') === 'cell');
  const cell = cells[cells.length - 1];
  const r = cell.getBoundingClientRect();
  return {found: true, row: true, id: a.id, noAck: !!a.noAck, acked: !!a.acknowledged, active: a.active === true,
          button: !!cell.querySelector('obc-button'),
          noAckIcon: !!cell.querySelector('obi-alarm-noack-iec, obi-warning-noack-iec'),
          text: cell.textContent.replace(/\s+/g, ' ').trim(), x: r.x + r.width / 2, y: r.y + r.height / 2} }"""


def visible_text_count(page, host, text) -> int:
    """How many visible elements inside a module element show exactly `text`."""
    loc = page.locator(host).get_by_text(text, exact=True)
    return sum(1 for i in range(loc.count()) if (loc.nth(i).bounding_box() or {}).get("width", 0) > 0)


# The top bar's alarm button (AlertButton): the 7th child of the top bar's root (`framework.top_bar`, after the alert
# message the generator added at index 5). A unit test holds the index to the generator (test_walk, TopBarPathTests).
BELL = '[data-component-path="T[0].0:6"]'
PANEL = "obc-alert-list-page-small"


def open_alarm_menu(page):
    """Open the top bar's alarm menu and wait for the module panel's alerts."""
    dock(page, "top").locator(BELL).first.click()
    alerts = None
    for _ in range(20):
        page.wait_for_timeout(500)
        alerts = page.evaluate(LIST_INFO, PANEL)
        if alerts:
            break
    return alerts


def frame_state(page, tag: str):
    """[classes, visibility] of a pump's alert frame: 'flash-alarm' while unacknowledged."""
    m = module_pump(page, tag)
    if m:   # the module's frame is drawn in shadow DOM; its state is the element's
        return ["flash-alarm" if m["alert"] and m["mode"] != "acked-active" else "",
                "visible" if m["alert"] else "hidden"]
    return page.evaluate("""(tag) => {
    const vs = [...document.querySelectorAll('[data-component="ia.display.view"]')].filter(e => e.innerText.includes(tag));
    const svgs = vs.length ? [...vs[0].querySelectorAll('[data-component="ia.shapes.svg"]')] : [];
    // the frame (L5): the flap of the status drawn, whose tab path is named `frame`, and the thick second frame
    // (the class `blink`) that shows while the alarm is unacknowledged
    const f = svgs.find(s => s.innerHTML.includes('name="frame"') && s.getBoundingClientRect().width > 0) ||
              svgs.find(s => s.innerHTML.includes('name="frame"'));
    if (!f) return null;
    const pulse = vs[0].querySelector('[class*="blink"]');
    const shown = !!pulse && getComputedStyle(pulse).visibility === 'visible' && pulse.getBoundingClientRect().width > 0;
    return [shown ? 'flash-alarm' : '', f.getBoundingClientRect().width > 0 ? getComputedStyle(f).visibility : 'hidden'] }""", tag)


def control_tab(right) -> None:
    """Show the faceplate's Control tab. A change of device resets the tab, but the same device
    selected again keeps the tab it was on."""
    tab = right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Control\s*$"))
    if tab.count():
        tab.first.click()
        right.page.wait_for_timeout(800)


def sign_in(page, base: str, login: dict) -> bool:
    """Sign in through the project's identity provider: the top bar's user button, Sign in
    (`system.perspective.login()`), the gateway's login page (user name, Continue, password, measured
    2026-10-09), and back to the project. True when the user menu then offers Sign out."""
    global SIGN_IN_WHY
    SIGN_IN_WHY = ""
    page.goto(base + "/", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    if not _open_user_menu(page, "Sign in"):
        return False
    page.wait_for_url(re.compile(r"/idp/"), timeout=30000)
    page.locator('input[name="username"]').fill(login["user"])
    page.locator('input[name="username"]').press("Enter")
    pw = page.locator('input[name="password"]')
    pw.wait_for(state="visible", timeout=15000)
    pw.fill(login["password"])
    pw.press("Enter")
    page.wait_for_url(re.compile(re.escape(base)), timeout=30000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4000)
    signed = _open_user_menu(page, "Sign out", press=False)
    page.keyboard.press("Escape")
    if not signed:
        SIGN_IN_WHY = "after the login the user menu does not offer Sign out: " + SIGN_IN_WHY
    return signed


# the top bar's icons, left to right: the asm frame's user menu is the last of them (as `glass_gates.TOP_ICONS`)
TOP_ICONS = """() => [...document.querySelectorAll('svg')].map((s) => s.getBoundingClientRect())
  .filter((r) => r.top < 44 && r.top >= 0 && r.height > 8 && r.height < 44)
  .map((r) => [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)]).sort((a, b) => a[0] - b[0])"""


SIGN_IN_WHY = ""   # why the last `sign_in` did not sign in, in words ("" after one that did)


def _open_user_menu(page, caption: str, press: bool = True) -> bool:
    """Open the top bar's user menu and find its entry `caption` (Sign in, Sign out); with `press`, press it.
    The openbridge frame's user button is the third coordinate container of the top dock; the asm frame's is
    the last of the top bar's three menu icons (COB-205, as `glass_gates.gate_menus`: right[2]). The entry is
    looked for in the opened popup alone (`.ia_popup`, GF-70), a text of the page behind it never counts, and
    the icon fallback is tried only where the top bar shows its three menu icons: otherwise nothing is clicked
    and `SIGN_IN_WHY` says what was seen. False when neither shows the entry."""
    global SIGN_IN_WHY
    popup = page.locator(".ia_popup")
    button = popup.locator('[data-component="ia.input.button"]', has_text=re.compile(rf"^\s*{caption}\s*$")).first
    text = popup.locator(f':text-is("{caption}"):visible').first
    holders = dock(page, "top").locator('[data-component="ia.container.coord"]')

    def by_container():
        if holders.count() <= 2:
            return f"the top dock holds {holders.count()} coordinate containers, not the user button's third"
        holders.nth(2).click()
        return ""

    def by_icon():
        icons = page.evaluate(TOP_ICONS)
        if len(icons) < 3:
            return f"the top bar shows {len(icons)} icons, not the three menu icons"
        page.mouse.click(*icons[-1])
        return ""

    reasons = []
    for open_menu in (by_container, by_icon):
        refused = open_menu()
        if refused:
            reasons.append(refused)
            continue
        page.wait_for_timeout(1500)
        for loc in (button, text):
            if loc.count() > 0 and loc.is_visible():
                if press:
                    loc.click()
                return True
        reasons.append(f"the opened menu offers no {caption!r}")
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    SIGN_IN_WHY = f"the user menu was not found ({'; '.join(reasons)})"
    return False


TREND_CARDS = r"""() => {
  // each trend card of the page: its title, the longest path its chart draws, its time axis labels
  // the page's repeater only: the navigation menu's dock holds a repeater too
  return [...document.querySelectorAll('[data-component="ia.display.flex-repeater"] [data-component="ia.chart.timeseries"]')]
    .filter(c => !c.closest('[class*="docked-view"]')).map(c => {
    // a repeater instance has no view wrapper: the card is the chart's parent, its first label the title
    const lab = c.parentElement ? c.parentElement.querySelector('[data-component="ia.display.label"]') : null;
    const texts = [...c.querySelectorAll('text')].map(t => t.textContent.trim());
    return {title: lab ? lab.innerText.trim() : '',
            line: Math.max(0, ...[...c.querySelectorAll('path')].map(p => (p.getAttribute('d') || '').length)),
            times: texts.filter(t => /^\d{1,2}:\d{2}$/.test(t)), range: (c.innerText || '').replace(/\s+/g, ' ').trim()} }) }"""


DISABLED = r"""(names) => {
  // the enabled state of the dock's buttons and entry fields, by their text or component name
  const out = {};
  const dock = document.querySelector('.docked-view-right');
  if (!dock) return out;
  for (const b of dock.querySelectorAll('[data-component="ia.input.button"]')) {
    const t = b.innerText.trim(); if (names.includes(t)) out[t] = b.disabled || b.getAttribute('disabled') !== null;
  }
  const f = dock.querySelector('[data-component="ia.input.numeric-entry-field"] input');
  if (f) out['setpoint'] = f.disabled;
  return out }"""
CRAFTED_CLICK = r"""(text) => {
  // a crafted client: the disabled button made clickable in the page, then clicked
  const b = [...document.querySelectorAll('.docked-view-right [data-component="ia.input.button"]')]
    .find(e => e.innerText.trim() === text);
  if (!b) return false;
  b.disabled = false; b.removeAttribute('disabled'); b.click(); return true }"""


ROOT = Path(__file__).resolve().parents[2]
BADGE_AT = r"""([tag, d]) => {
  // the visible 16 px badge at the bottom left of a library symbol's 48 px box, by its icon path
  const vs = [...document.querySelectorAll('[data-component="ia.display.view"]')].filter(e => e.innerText.includes(tag));
  for (const v of vs) {
    const box = [...v.querySelectorAll('[data-component="ia.container.coord"]')].find(c => {
      const b = c.getBoundingClientRect(); return Math.round(b.width) === 48 && Math.round(b.height) === 48 });
    if (!box) continue;
    const r = box.getBoundingClientRect();
    for (const s of v.querySelectorAll('[data-component="ia.shapes.svg"]')) {
      const b = s.getBoundingClientRect();
      if (Math.round(b.width) === 16 && Math.abs(b.x - r.x) < 1.5 && Math.abs(b.y - (r.y + 32)) < 1.5
          && getComputedStyle(s).visibility !== 'hidden' && s.innerHTML.includes(d.slice(0, 24))) return true;
    }
  }
  return false }"""


def badge_shown(page, tag: str) -> bool:
    """The interlock badge on a symbol: the element's `badgeInterlock` for a module pump, else the
    library symbol's duty icon at its bottom left corner (library.py `_badges`)."""
    m = page.evaluate("""(tag) => { for (const m of document.querySelectorAll('[data-component^="cadre.ob."]')) {
        const el = [...m.querySelectorAll('*')].find(e => e.tagName.includes('-'));
        if (el && el.tag === tag) return el.badgeInterlock; } return null }""", tag)
    if m is not None:
        return m == "interlock"
    duty = json.loads((ROOT / "library/icons/duty.json").read_text(encoding="utf-8"))["elements"][0]["d"]
    return page.evaluate(BADGE_AT, [tag, duty])


def pump_off(page, tag: str) -> bool:
    m = module_pump(page, tag)
    return (not m["on"]) if m else ("Off" in readout_text(page, tag))


def open_device(page, tag: str):
    _, (x, y) = symbol(page, tag)
    page.mouse.click(x, y)
    page.wait_for_timeout(2500)
    return dock(page, "right")


READOUT_AT = r"""(tag) => {
  // the centre of the innermost embedded view (a readout or an instrument field) showing `tag`; under the module
  // rendering a readout or a field is a component of the module (0.3.1), found by its element: the identifier
  // it draws (`idTag`) or the text its shadow roots print
  const printed = (root) => { let t = '';      // in document order, down the shadow roots, no style element
    for (const n of root.childNodes) {
      if (n.nodeType === 3) t += n.textContent;
      else if (n.nodeType === 1 && n.tagName !== 'STYLE') {
        if (n.shadowRoot) t += ' ' + printed(n.shadowRoot);
        t += ' ' + printed(n);
      }
    }
    return t; };
  for (const m of document.querySelectorAll('[data-component="cadre.ob.readout"], [data-component="cadre.ob.instrumentfield"]')) {
    if (m.closest('[class*="docked-view"]')) continue;
    const el = [...m.querySelectorAll('*')].find(e => e.tagName.includes('-'));
    if (el && (el.idTag === tag || (el.shadowRoot && printed(el.shadowRoot).includes(tag)))) {
      const b = m.getBoundingClientRect();
      return [b.x + b.width / 2, b.y + b.height / 2];
    }
  }
  const vs = [...document.querySelectorAll('[data-component="ia.display.view"]')]
    .filter(e => !e.closest('[class*="docked-view"]') && e.innerText.includes(tag)
                 && !e.querySelector('[data-component="ia.display.view"]'));
  if (!vs.length) return null;
  const r = vs[0].getBoundingClientRect();
  return [r.x + r.width / 2, r.y + r.height / 2] }"""
CHART_LINE = r"""() => {
  // the longest path the stock chart in the dock draws: a trend line of many points
  const c = document.querySelector('.docked-view-right [data-component="ia.chart.timeseries"]');
  if (!c) return -1;
  return Math.max(0, ...[...c.querySelectorAll('path')].map(p => (p.getAttribute('d') || '').length)) }"""
CHART_AXIS = r"""() => {
  // the dock chart's time labels and its dashed paths (COB-083)
  const c = document.querySelector('.docked-view-right [data-component="ia.chart.timeseries"]');
  if (!c) return null;
  const times = [...c.querySelectorAll('text')].map(t => t.textContent.trim()).filter(t => /^\d{1,2}:\d{2}( ?[AP]M)?$/i.test(t));
  const dashed = [...c.querySelectorAll('path')].filter(e => {
    const d = e.getAttribute('stroke-dasharray') || getComputedStyle(e).strokeDasharray;
    return d && d !== 'none' && d !== '0' && d !== '0px'; }).length;
  return {times, dashed} }"""


def ack_alarm(page, match: str) -> bool:
    """Acknowledge the open faceplate's active, unacknowledged alarm whose source or text contains
    `match`. Under module rendering the faceplate's list is display only (COBD-025): ACK on its row
    in the top bar's alarm menu, then the row, which closes the menu and keeps the device selected.
    Under stock rendering, in the faceplate's Alarms tab: the row ticked, then Acknowledge (GF-40)."""
    right = dock(page, "right")
    if page.locator('[data-component^="cadre.ob."]').count():
        open_alarm_menu(page)
        cell = {}
        for _ in range(12):
            cell = page.evaluate(ROW_ACTION, [PANEL, match]) or {}
            if cell.get("button"):
                break
            page.wait_for_timeout(500)
        if not cell.get("button"):
            return False
        page.mouse.click(cell["x"], cell["y"])
        acked = False
        for _ in range(12):
            page.wait_for_timeout(500)
            if (page.evaluate(ROW_ACTION, [PANEL, match]) or {}).get("acked"):
                acked = True
                break
        text = next((a["text"] for a in (page.evaluate(LIST_INFO, PANEL) or [])
                     if match in str(a["source"]) or match in str(a["text"])), match)
        click_text_in(page, PANEL, text)   # the row closes the menu; the device stays selected
        page.wait_for_timeout(2000)
        return acked
    right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Alarms")).first.click()
    page.wait_for_timeout(2000)
    table = right.locator('[data-component="ia.display.alarmstatustable"]').first
    rows = table.locator(".ia_table__body__row", has_text="Active, Unacknowledged")
    if not rows.count():
        return False
    rows.first.locator(".ia_checkbox").first.click()
    page.wait_for_timeout(400)
    table.locator(".ackAlarmsButton").first.click()
    page.wait_for_timeout(1500)
    return True


# ---------------------------------------------------------------------------------------
# Helpers of the generated walk (walk.py). The DOM facts below were measured on 2026-10-11 with read
# only page scripts on cadre_hmi_pilot, cadre_hmi_wtp and cadre_hmi_wtpob, each built from commit 9306240:
#
#   * A value row of a faceplate is a flex container whose children are two labels, the caption and
#     the value ("State", "Running"); a setpoint or limit row is a flex container whose children are
#     the caption label, the `ia.input.numeric-entry-field` (which holds one `input`) and a note label.
#     A row whose member the device lacks stays in the DOM with no size (`position.display`, GF-08).
#   * An entry field's `input` is `type="text"` until it is clicked and `type="number"` while it is
#     edited; a disabled field's carries `disabled` and `readonly` in both modes.
#   * The buttons of one command group are the children of one flex container; they are `button`
#     elements and carry `disabled`. The Maintenance tab has two buttons captioned "Automatic", one
#     beside "Force on" and one beside "Mask".
#   * A library symbol is the innermost embedded view on the page, and its text is one line for each
#     label it shows ("On", "P-1"; "12.5 L/s", "FT-1"; "PIC-1", "▸ 50.0", "50.0", "kPa", "Out 50 %").
#     A 16 px icon that a symbol does not show is either hidden (`meta.visible`, a coordinate child) or
#     has no size (`position.display`, a flex child: the controller block's control badge).
#   * A component of the Cadre OpenBridge module holds one custom element (`obc-pump`,
#     `obc-automation-tank`) whose `tag` property is the identifier; a pump's carries `on` and
#     `speedInPercent`, a tank's `value` and `max`.
#   * The navigation dock sits at x 0 while open and at minus its width while closed; Escape does not
#     close it, the top bar's menu button toggles it. The faceplate dock is at the viewport's right
#     edge while closed (`faceplates.is_open`) and pushes the page while open.
#   * The top bar's alarm button reads the count of active alarms in the project's scope as its text.
#     Its menu, a popup, closes on Escape under both renderings and leaves the faceplate dock open; a
#     reload of the page closes the dock and keeps the device selected.
#   * A drawn series of a stock time series chart is two paths of the same long `d` (some 11,000
#     characters for 300 rows, also for a constant value); a series with no sample in the range draws
#     no path at all.
# ---------------------------------------------------------------------------------------
PAGE_COMPONENTS = r"""() => [...document.querySelectorAll('[data-component]')]
  .filter(e => !e.closest('[class*="docked-view"]')).length"""


def page_faults(page) -> dict:
    """What gate G8 fails a page on (`capture.capture`): binding quality overlays, view error badges,
    the trial page and "View Not Found", beside the count of rendered components, and the count of
    those outside the docks (`page_components`): the frame renders its own around a blank view, so
    only the second count says that the page itself drew (measured 2026-10-11, see the end of this file)."""
    body = page.inner_text("body")
    return {"overlays": page.locator(".ia_qualityOverlay").count(),
            "badges": page.locator(".view-state-display").count(),
            "not_found": "View Not Found" in body, "trial": "Trial Expired" in body,
            "components": page.locator("[data-component]").count(),
            "page_components": page.evaluate(PAGE_COMPONENTS)}


def clean(faults: dict) -> bool:
    return (not faults["overlays"] and not faults["badges"] and not faults["not_found"] and not faults["trial"]
            and faults["components"] > 0)


def dock_open(page, side: str = "right") -> bool:
    """A dock is open while it lies inside the viewport: the faceplate dock closed sits at the right
    edge, the navigation dock closed at minus its width."""
    d = dock(page, side)
    if not d.count():
        return False
    b = d.first.bounding_box()
    if not b or b["width"] <= 0:
        return False
    return b["x"] < page.viewport_size["width"] - 1 if side == "right" else b["x"] > -1


def close_faceplate(page) -> None:
    """Close the faceplate dock with its own close button; the page takes its full width again."""
    if dock_open(page):
        dock(page, "right").locator('[data-component="ia.container.coord"]').first.click()
        for _ in range(15):
            page.wait_for_timeout(200)
            if not dock_open(page):
                break
        page.wait_for_timeout(400)   # a cards page lays its cards out again


SYMBOL_AT = r"""(find) => {
  // The symbol that shows the line `find` (an identifier, or a field's label and unit): where to click
  // it and what it shows. A component of the Cadre OpenBridge module is found by its element: a readout by
  // the `idTag` it draws beneath its value, an instrument field by its caption (the element's `tag` and `unit`),
  // every other component by its `tag`. `text` is what the element prints, down its shadow roots.
  const printed = (root) => { let t = '';      // in document order, down the shadow roots, no style element
    for (const n of root.childNodes) {
      if (n.nodeType === 3) t += n.textContent;
      else if (n.nodeType === 1 && n.tagName !== 'STYLE') {
        if (n.shadowRoot) t += ' ' + printed(n.shadowRoot);
        t += ' ' + printed(n);
      }
    }
    return t; };
  const named = (type, el) => type === 'cadre.ob.readout' ? el.idTag === find
    : type === 'cadre.ob.instrumentfield' ? [el.tag, el.unit].filter(Boolean).join(' ') === find
    : el.tag === find;
  for (const m of document.querySelectorAll('[data-component^="cadre.ob."]')) {
    if (m.closest('[class*="docked-view"]')) continue;
    const el = [...m.querySelectorAll('*')].find(e => e.tagName.includes('-'));
    if (el && named(m.getAttribute('data-component'), el)) {
      const b = m.getBoundingClientRect();
      return {x: b.x + b.width / 2, y: b.y + b.height / 2, module: m.getAttribute('data-component'), lines: [],
              icons: [], frame: el.alert === undefined ? null : !!el.alert,
              on: (el.on ?? el.open) === undefined ? null : !!(el.on ?? el.open),
              speed: el.speedInPercent === undefined ? null : el.speedInPercent,
              value: el.value === undefined ? null : el.value,
              setpoint: el.setpoint === undefined ? null : el.setpoint,
              text: el.shadowRoot ? printed(el.shadowRoot).replace(/\s+/g, ' ').trim() : ''};
    }
  }
  const lines = e => e.innerText.split('\n').map(s => s.trim()).filter(s => s.length);
  const v = [...document.querySelectorAll('[data-component="ia.display.view"]')]
    .filter(e => !e.closest('[class*="docked-view"]') && !e.querySelector('[data-component="ia.display.view"]'))
    .find(e => lines(e).includes(find));
  if (!v) return null;
  let r = v.getBoundingClientRect();
  const svgs = [...v.querySelectorAll('[data-component="ia.shapes.svg"]')];
  const box = [...v.querySelectorAll('[data-component="ia.container.coord"]')].find(c => {
    const b = c.getBoundingClientRect(); return Math.round(b.width) === 48 && Math.round(b.height) === 48 });
  if (box) r = box.getBoundingClientRect();
  const icons = svgs.filter(s => Math.round(s.getBoundingClientRect().width) === 16 && getComputedStyle(s).visibility !== 'hidden')
    .map(s => (s.innerHTML.match(/ d="([^"]{0,24})/) || [])[1] || '');
  const flaps = svgs.filter(s => s.innerHTML.includes('name="frame"'));   // the flaps of the frame (L5): one shows
  const drawn = flaps.some(s => s.getBoundingClientRect().width > 0 && getComputedStyle(s).visibility === 'visible');
  return {x: r.x + r.width / 2, y: r.y + r.height / 2, module: null, lines: lines(v), icons,
          frame: flaps.length ? drawn : null, on: null, speed: null, value: null} }"""


def find_symbol(page, find: str) -> dict | None:
    """The symbol on the page that shows the line `find`: its click point (the centre of the 48 px
    symbol box, of a module component's box, or of any other view), its text lines, the 16 px icons it
    shows (the first 24 characters of each path) and whether its alert frame is drawn; for a module
    component the element's bound state instead of text. None when no symbol shows the line."""
    return page.evaluate(SYMBOL_AT, find)


def dock_header(page) -> tuple[str, str]:
    """The identifier and the description in the faceplate dock's header (its first two labels)."""
    labs = dock(page, "right").locator('[data-component="ia.display.label"]')
    if labs.count() < 2:
        return "", ""
    return labs.nth(0).inner_text().strip(), labs.nth(1).inner_text().strip()


def open_faceplate(page, find: str, title: str):
    """Open a device's faceplate the way an operator does: the dock closed first (it covers part of a
    diagram and reflows a cards page), then a click on the symbol that shows `find`. Waits until the
    dock's header reads `title`, then for the faceplate's polls (1 s the device, 2 s the permissions).
    The dock's locator, or None when no symbol shows `find` or the dock did not open on the device."""
    close_faceplate(page)
    at = find_symbol(page, find)
    if not at:
        return None
    page.mouse.click(at["x"], at["y"])
    opened = False
    for _ in range(25):
        page.wait_for_timeout(200)
        if dock_open(page) and dock_header(page)[0] == title:
            opened = True
            break
    if not opened:
        return None
    page.wait_for_timeout(2500)
    return dock(page, "right")


# the tab labels of both faceplate styles (COBD-045), as `faceplates.TAB` reads them
TAB_NAME = re.compile(r"^\s*(Control|Alarms|Interlocks?|Values|Trend|Maintenance|Tuning|Status|Home|Config|Diagnostics|Info)"
                      r"(\s*\((\d+)\))?\s*$")


def tabs_shown(right) -> list[str]:
    """The names of the tabs the open faceplate shows, in order, without their counts."""
    buttons = right.locator('[data-component="ia.input.button"]')
    out = []
    for k in range(buttons.count()):
        m = TAB_NAME.match(buttons.nth(k).inner_text())
        if m and buttons.nth(k).is_visible():
            out.append(m.group(1))
    return out


def tab(right, name: str) -> bool:
    """Show the tab `name` of the open faceplate (its label may carry a count). False without it."""
    b = right.locator('[data-component="ia.input.button"]', has_text=re.compile(rf"^\s*{name}(\s*\(\d+\))?\s*$"))
    for k in range(b.count()):
        if b.nth(k).is_visible():
            b.nth(k).click()
            right.page.wait_for_timeout(1200)
            return True
    return False


def tab_count(right, name: str = "Alarms") -> int | None:
    """The count a tab's label carries ("Alarms (2)"), 0 for none, None without the tab."""
    b = right.locator('[data-component="ia.input.button"]', has_text=re.compile(rf"^\s*{name}(\s*\(\d+\))?\s*$"))
    for k in range(b.count()):
        if b.nth(k).is_visible():
            m = TAB_NAME.match(b.nth(k).inner_text())
            return int(m.group(3) or 0) if m else None
    return None


DOCK_ROW = r"""(caption) => {
  // the visible row of the faceplate whose first child is the label `caption`: the texts of its other
  // labels, and its entry field when it has one (its index among the dock's entry fields)
  const d = document.querySelector('.docked-view-right'); if (!d) return null;
  const shown = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 };
  const inputs = [...d.querySelectorAll('[data-component="ia.input.numeric-entry-field"] input')];
  for (const l of d.querySelectorAll('[data-component="ia.display.label"]')) {
    if (!shown(l) || l.innerText.trim() !== caption) continue;
    const p = l.parentElement;
    if (p.firstElementChild !== l) continue;
    const input = p.querySelector('[data-component="ia.input.numeric-entry-field"] input');
    return {texts: [...p.children].filter(c => c !== l && c.getAttribute('data-component') === 'ia.display.label')
                     .map(c => c.innerText.trim()),
            field: input ? {index: inputs.indexOf(input), value: input.value, disabled: input.disabled} : null};
  }
  return null }"""


def dock_row(page, caption: str) -> dict | None:
    """A row of the open faceplate by its caption: `texts` (what its other labels read) and `field`
    (index, value, disabled) for a setpoint or a limit row. None while the row is not shown."""
    return page.evaluate(DOCK_ROW, caption)


def row_text(page, caption: str) -> str | None:
    """What a value row reads beside its caption ("Running"), or a setpoint row's note."""
    row = dock_row(page, caption)
    return row["texts"][0] if row and row["texts"] else (None if row is None else "")


def dock_field(page, caption: str):
    """The entry field of the row `caption` (a locator on its `input`) and whether it is disabled;
    (None, None) while the row is not shown."""
    row = dock_row(page, caption)
    if not row or not row["field"]:
        return None, None
    inputs = dock(page, "right").locator('[data-component="ia.input.numeric-entry-field"] input')
    return inputs.nth(row["field"]["index"]), row["field"]["disabled"]


def type_into(field, value) -> None:
    """Type a value into an entry field and commit it, as gate G10 has since 2026-10-09 (F5, F13); the
    row then holds it until its Set writes it (F029), which this presses."""
    field.click()
    field.fill(str(value))
    field.press("Enter")
    answer(field.page, SET)


def field_number(field) -> float | None:
    """The number an entry field shows, None when it shows none."""
    try:
        return float(field.input_value().replace(",", ""))
    except ValueError:
        return None


DOCK_BUTTON = r"""([caption, sibling, press]) => {
  // the visible button of the faceplate captioned `caption`, in the group that also holds a button
  // captioned `sibling` when one is named: its index among the dock's buttons and whether it is
  // disabled. With `press`, a crafted client: the button made clickable in the page, then clicked.
  const all = [...document.querySelectorAll('.docked-view-right [data-component="ia.input.button"]')];
  for (let i = 0; i < all.length; i++) {
    const b = all[i]; const r = b.getBoundingClientRect();
    if (r.width <= 0 || b.innerText.trim() !== caption) continue;
    if (sibling && ![...b.parentElement.children].some(c => c !== b && (c.innerText || '').trim() === sibling)) continue;
    const disabled = b.disabled || b.getAttribute('disabled') !== null;
    if (press) { b.disabled = false; b.removeAttribute('disabled'); b.click(); }
    return {index: i, disabled};
  }
  return null }"""


def dock_button(page, caption: str, sibling: str | None = None):
    """A command button of the open faceplate (a locator) and whether it is disabled; (None, None)
    while it is not shown. `sibling` names another button of its group, for a caption the pane
    carries twice."""
    hit = page.evaluate(DOCK_BUTTON, [caption, sibling, False])
    if not hit:
        return None, None
    return Confirmed(dock(page, "right").locator('[data-component="ia.input.button"]').nth(hit["index"]), page), hit["disabled"]


def crafted_press(page, caption: str, sibling: str | None = None) -> bool:
    """A crafted client's click on a disabled button (the technique of G10 F15, GF-45): the `disabled`
    flag removed in the page, then `click()`. True when the button was found and clicked."""
    return page.evaluate(DOCK_BUTTON, [caption, sibling, True]) is not None


UNLOCK = "e => { e.disabled = false; e.removeAttribute('disabled'); e.readOnly = false; e.removeAttribute('readonly'); }"


def crafted_entry(page, caption: str, value) -> bool:
    """A crafted client's entry in a disabled field. Measured on 2026-10-11 (cadre_hmi_pilot, nobody
    signed in): the field's `input` carries `disabled` and `readonly`; with both removed in the page a
    click puts the field in its edit mode, where the client draws the input disabled again; with both
    removed a second time the value can be typed and committed, and the commit reaches the gateway:
    the row then reads "Refused" (`cadre.hmi.command` refused it) and the tag keeps its value. A
    disabled button, by contrast, runs no script at all (GF-45). True when the keys were sent."""
    field, _disabled = dock_field(page, caption)
    if field is None:
        return False
    try:
        field.evaluate(UNLOCK)
        field.click(timeout=3000)
        field, _disabled = dock_field(page, caption)   # the edit mode's input
        field.evaluate(UNLOCK)
        field.fill(str(value), timeout=3000)
        field.press("Enter", timeout=3000)
    except Exception:   # the client took no keys: nothing was sent
        return False
    return True


def dock_text(page) -> str:
    right = dock(page, "right")
    return right.inner_text() if right.count() else ""


INTERLOCK_LAMP = r"""(text) => {
  // the lamp of the open faceplate's condition row whose text reads `text`: the first label of the row's
  // head (`Faceplate/InterlockRow`: the lamp State, Kind, Text), else null
  const shown = l => { const r = l.getBoundingClientRect(); return r.width > 0 && r.height > 0 };
  const labels = [...document.querySelectorAll('.docked-view-right [data-component="ia.display.label"]')].filter(shown);
  for (const l of labels) {
    if (l.innerText.trim() !== text) continue;
    const head = l.parentElement && l.parentElement.closest('[data-component="ia.container.flex"]');
    if (!head) continue;
    const first = [...head.querySelectorAll('[data-component="ia.display.label"]')].filter(shown)[0];
    if (first && first !== l) return first.innerText.trim();
  }
  return null }"""


def interlock_lamp(page, text: str) -> str | None:
    """What the lamp of the Interlocks tab's row for the condition `text` reads (Met, Not met, Latched,
    Bypassed), or None while no such row is shown (COB-204)."""
    return page.evaluate(INTERLOCK_LAMP, text)


FIRST_NUMBER = r"""() => {
  // the first visible label of the faceplate, after its header, that reads a number: the big value
  // of an instrument or a controller ("0.13 NTU"), the level of a tank ("52.0 %")
  const d = document.querySelector('.docked-view-right'); if (!d) return null;
  const labels = [...d.querySelectorAll('[data-component="ia.display.label"]')]
    .filter(l => { const r = l.getBoundingClientRect(); return r.width > 0 && r.height > 0 });
  for (const l of labels.slice(2)) {
    const m = l.innerText.trim().match(/^(-?\d[\d,]*(\.\d+)?)(\s|$)/);
    if (m) return m[1].replace(/,/g, '');
  }
  return null }"""


def big_value(page) -> float | None:
    """The value the open faceplate shows large, as a number."""
    v = page.evaluate(FIRST_NUMBER)
    return float(v) if v is not None else None


def frame_alarm_count(page) -> int | None:
    """The count on the top bar's alarm button: the active alarms in the project's scope."""
    text = dock(page, "top").locator(BELL).first.inner_text().strip()
    return int(text) if text.isdigit() else None


def alarm_menu_rows(page, module: bool) -> list[str] | None:
    """The rows the top bar's alarm menu lists, the frame's own list: under stock rendering the rows
    of its alarm status table, under module rendering the alerts of OpenBridge's small alert page
    (source and text). The menu is closed again with Escape, which leaves the faceplate dock open
    (measured 2026-10-11 under both renderings). None when the menu rendered no list."""
    if module:
        alerts = open_alarm_menu(page)
        rows = None if alerts is None else [f"{a.get('source') or ''} {a.get('text') or ''}" for a in alerts]
    else:
        dock(page, "top").locator(BELL).first.click()
        tbl = page.locator('.popup [data-component="ia.display.alarmstatustable"], '
                           '[class*="popup"] [data-component="ia.display.alarmstatustable"]').first
        rows = None
        for _ in range(12):
            page.wait_for_timeout(500)
            if tbl.count():
                found = tbl.locator(".ia_table__body__row")
                rows = [re.sub(r"\s+", " ", found.nth(k).inner_text()).strip() for k in range(found.count())]
                if rows:
                    break
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)
    return rows


def nav_labels(page) -> list[str]:
    """The entries of the navigation menu, opened with the top bar's menu button and left open."""
    if not dock_open(page, "left"):
        dock(page, "top").locator('[data-component="ia.container.coord"]').first.click()
        for _ in range(10):
            page.wait_for_timeout(200)
            if dock_open(page, "left"):
                break
        page.wait_for_timeout(500)
    # the entries of the two repeaters, not the menu's header title
    labs = dock(page, "left").locator('[data-component="ia.display.flex-repeater"] [data-component="ia.display.label"]')
    return [labs.nth(k).inner_text().strip() for k in range(labs.count())]


def navigate_by_menu(page, label: str) -> bool:
    """Navigate as an operator does: the top bar's menu button, then the entry `label` of the
    navigation menu, which closes the menu. False when the menu has no such entry."""
    if label not in nav_labels(page):
        # the menu is modal (GF-71): left open, its overlay would take the next step's click
        dock(page, "top").locator('[data-component="ia.container.coord"]').first.click()
        page.wait_for_timeout(1000)
        return False
    dock(page, "left").locator('[data-component="ia.display.label"]',
                               has_text=re.compile(rf"^\s*{re.escape(label)}\s*$")).first.click()
    page.wait_for_timeout(3000)
    return True


CARD_TITLE_AT = r"""(title) => {
  // a card's title on a cards page: a label outside every embedded view whose text begins with it
  const l = [...document.querySelectorAll('[data-component="ia.display.label"]')]
    .find(e => !e.closest('[class*="docked-view"]') && !e.closest('[data-component="ia.display.view"]')
               && e.innerText.trim().replace(/\s*›$/, '') === title);
  if (!l) return null; const r = l.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2] }"""


def click_card_title(page, title: str) -> bool:
    at = page.evaluate(CARD_TITLE_AT, title)
    if not at:
        return False
    page.mouse.click(*at)
    page.wait_for_timeout(3000)
    return True


DOCK_SERIES = r"""() => {
  // the long paths of the faceplate's chart: two for each series it draws
  const c = document.querySelector('.docked-view-right [data-component="ia.chart.timeseries"]');
  if (!c) return -1;
  return [...c.querySelectorAll('path')].filter(p => (p.getAttribute('d') || '').length > 200).length }"""


def series_drawn(page) -> int:
    """How many series the open faceplate's chart draws (-1 without a chart): a drawn series is two
    paths of more than 200 characters, a limit line is shorter, an empty series draws nothing."""
    n = page.evaluate(DOCK_SERIES)
    return n if n < 0 else n // 2


def badge_icon(name: str) -> str:
    """The first 24 characters of an icon's first path, as `SYMBOL_AT` reports the icons a symbol shows."""
    return json.loads((ROOT / "library" / "icons" / f"{name}.json").read_text(encoding="utf-8"))["elements"][0]["d"][:24]


# ---------------------------------------------------------------------------------------
# Helpers added for the second pass of the generated walk. Measured on 2026-10-11 at 07:05 with page
# scripts on cadre_hmi_pilot and cadre_hmi_wtp, as deployed from the working tree, nobody signed in:
#
#   * The top bar's labels are, in order: the application's name, the page's name (the navigation
#     menu's label of the route: "Supply", "Plant Overview"), the text of the most severe alarm, its
#     time, the count on the alarm button and the clock.
#   * A page holds components outside the three docks (181 on the pilot's /supply, 242 on the sample's
#     overview); the frame alone holds about 40.
#   * A sequence block is three lines, "FLT-1", "Standby", "Step 1"; its faceplate shows the tabs Status,
#     Trend and Alarms, a row "Step" reading "1", a row "Fault" reading "Normal", and one button for its
#     pulse command, captioned by the device model ("Start cycle"), disabled with nobody signed in.
#   * React holds a button's handlers in a property of the element whose name begins `__reactProps$`,
#     with `onClick` among them and `disabled` true for a disabled button. React drops a click on a
#     button whose properties say disabled, whatever the DOM attribute says, which is why the click of
#     GF-45 runs no script. The handler called directly does reach the gateway: the button's script
#     ran, `cadre.hmi.pulse` refused it, the faceplate's message line read "Refused: sign in with the
#     Administrator role", and the member kept its value. That is a crafted client whose action the
#     gateway itself must refuse, which the click with the flag removed is not. Wiki page 07 records
#     the fact as GF-59.
# ---------------------------------------------------------------------------------------
def page_name(page) -> str:
    """The page's name in the top bar: its second label."""
    labs = dock(page, "top").locator('[data-component="ia.display.label"]')
    return labs.nth(1).inner_text().strip() if labs.count() > 1 else ""


REFUSED_ROWS = r"""(word) => {
  // the captions of the faceplate's visible rows one of whose other labels reads exactly `word`
  const d = document.querySelector('.docked-view-right'); if (!d) return [];
  const shown = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 };
  const out = [];
  for (const l of d.querySelectorAll('[data-component="ia.display.label"]')) {
    if (!shown(l) || l.innerText.trim() !== word) continue;
    const first = l.parentElement.firstElementChild;
    if (first && first !== l && first.getAttribute('data-component') === 'ia.display.label') out.push(first.innerText.trim());
  }
  return out }"""


def refused_rows(page, word: str = "Refused") -> list[str]:
    """The captions of the open faceplate's rows whose note reads "Refused" (a setpoint or a limit row
    the gateway refused a write of, until the row's next accepted write)."""
    return page.evaluate(REFUSED_ROWS, word)


def dock_message(page, word: str = "Refused") -> str:
    """The faceplate's message line when it reads a refusal ("Refused: sign in with the Administrator
    role"), else ''. A row's note reads the bare word and is not the message line."""
    for line in dock_text(page).splitlines():
        if line.strip().startswith(word) and line.strip() != word:
            return line.strip()
    return ""


CRAFTED_CALL = r"""([caption, sibling]) => {
  // a crafted client that reaches the gateway: the click handler React holds for the button, called
  // directly (GF-59, measured 2026-10-11: the button's script then runs in the gateway)
  const all = [...document.querySelectorAll('.docked-view-right [data-component="ia.input.button"]')];
  for (const b of all) {
    const r = b.getBoundingClientRect();
    if (r.width <= 0 || b.innerText.trim() !== caption) continue;
    if (sibling && ![...b.parentElement.children].some(c => c !== b && (c.innerText || '').trim() === sibling)) continue;
    const key = Object.keys(b).find(k => k.startsWith('__reactProps$'));
    if (!key || typeof b[key].onClick !== 'function') return 'no handler';
    try { b[key].onClick({type: 'click', target: b, currentTarget: b, preventDefault() {}, stopPropagation() {},
                          persist() {}, nativeEvent: new MouseEvent('click')}); }
    catch (e) { return 'threw: ' + e }
    return 'called';
  }
  return 'not found' }"""


def crafted_call(page, caption: str, sibling: str | None = None) -> str:
    """A crafted client's call of a button's handler, past the client's own `disabled`: 'called' when
    the handler ran, else why not. The gateway then runs the button's script (GF-59), and the
    library's checked function answers; a button the click of `crafted_press` leaves untouched
    (GF-45) is refused here by the gateway itself."""
    return page.evaluate(CRAFTED_CALL, [caption, sibling])


# ---------------------------------------------------------------------------------------
# Added for the route steps of the frame's own pages. Measured on 2026-10-11 at 09:03 with a page
# script on cadre_hmi_pilot, cadre_hmi_wtp and cadre_hmi_wtpob, nobody signed in: /alerts holds one
# `ia.display.alarmstatustable` outside the docks that has a size (its journal table is rendered too,
# with no size, while the Active tab shows); /trends holds one `ia.chart.timeseries` for each card
# (5 on the pilot, 17 on the sample); /supply and the sample's overview hold neither.
# ---------------------------------------------------------------------------------------
PAGE_HOLDS = r"""(type) => [...document.querySelectorAll('[data-component="' + type + '"]')]
  .filter(e => !e.closest('[class*="docked-view"]') && !e.closest('[class*="popup"]'))
  .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 }).length"""


def page_holds(page, component: str) -> int:
    """How many components of one type the page shows outside the docks and outside a popup: what
    tells the alerts page (its alarm status table) or the trend page (a chart for each card) from a
    blank view under the right address."""
    return page.evaluate(PAGE_HOLDS, component)


# ---------------------------------------------------------------------------------------
# Page command buttons (COB-159, wiki page 05 section 5.1): a button the diagram page itself carries, outside
# every dock. A `pulse` button is a row of four buttons of which two show at a time: the button, and, once
# pressed, the question with Confirm and Cancel in its place. Its refusal is the button's own text. Measured
# on the gateway on 2026-10-24 (cadre_hmi_eng02_asm, /poweroverview, 8.3.6): the button reads its caption;
# one press shows Confirm and Cancel and writes nothing; Confirm holds the tag true for the pulse length and
# lets it go; nobody signed in, the button is disabled, and the handlers called directly (as `crafted_call`
# does in a dock) make the gateway answer on the button: "Refused: sign in with the Administrator role". The
# button's own class list holds a word with "popup" in it, so the dock and popup filters look at its ancestors only.
# ---------------------------------------------------------------------------------------
PAGE_BUTTONS = r"""() => [...document.querySelectorAll('[data-component="ia.input.button"]')]
  .filter(b => !b.parentElement.closest('[class*="docked-view"]') && !b.parentElement.closest('[class*="popup"]'))
  .filter(b => { const r = b.getBoundingClientRect(); return r.width > 0 && r.height > 0 })
  .map(b => ({text: b.innerText.trim(), disabled: b.disabled || b.getAttribute('disabled') !== null}))"""


def page_buttons(page) -> list[dict]:
    """The buttons the page shows outside the docks and the popups: their text and whether each is disabled."""
    return page.evaluate(PAGE_BUTTONS)


def page_button(page, caption: str):
    """(shown, disabled) of the page's button captioned `caption` (a refusal replaces the caption, so the
    question's Confirm and Cancel are found by their own captions); (False, None) while it is not shown."""
    hit = next((b for b in page_buttons(page) if b["text"] == caption), None)
    return (True, hit["disabled"]) if hit else (False, None)


def page_button_click(page, caption: str) -> bool:
    """A click on the page's button captioned `caption`, as an operator makes it. False when none is shown."""
    loc = page.locator('[data-component="ia.input.button"]', has_text=re.compile(rf"^\s*{re.escape(caption)}\s*$"))
    for k in range(loc.count()):
        b = loc.nth(k)
        if b.is_visible() and not b.evaluate("e => !!e.parentElement.closest('[class*=\"docked-view\"]')"):
            b.click()
            return True
    return False


PAGE_CRAFTED_CALL = r"""(caption) => {
  // a crafted client that reaches the gateway: the click handler React holds for a page button, called
  // directly (as CRAFTED_CALL does for a dock's button, GF-59)
  const all = [...document.querySelectorAll('[data-component="ia.input.button"]')]
    .filter(b => !b.parentElement.closest('[class*="docked-view"]') && !b.parentElement.closest('[class*="popup"]'));
  for (const b of all) {
    const r = b.getBoundingClientRect();
    if (r.width <= 0 || b.innerText.trim() !== caption) continue;
    const key = Object.keys(b).find(k => k.startsWith('__reactProps$'));
    if (!key || typeof b[key].onClick !== 'function') return 'no handler';
    try { b[key].onClick({type: 'click', target: b, currentTarget: b, preventDefault() {}, stopPropagation() {},
                          persist() {}, nativeEvent: new MouseEvent('click')}); }
    catch (e) { return 'threw: ' + e }
    return 'called';
  }
  return 'not found' }"""


def page_crafted_call(page, caption: str) -> str:
    """A crafted client's call of a page button's handler, past the client's own `disabled`: 'called' when
    the handler ran, else why not. The gateway then runs the button's script and the library's checked
    function answers."""
    return page.evaluate(PAGE_CRAFTED_CALL, caption)


def page_label_shown(page, text: str) -> bool:
    """A label outside the docks and the popups reads `text` (the question of a page command button)."""
    loc = page.locator('[data-component="ia.display.label"]', has_text=text)
    for k in range(loc.count()):
        if loc.nth(k).is_visible():
            return True
    return False
