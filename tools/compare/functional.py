"""Functional gate (G10) for the sample water treatment plant: an operator's walk, end to end.

Each step acts the way an operator would (clicks, typing) in a fresh session on our own gateway,
then checks a visible result. Checks:

  F1  A card title navigates (Production to /intake).
  F2  A symbol click opens the faceplate dock with the device identifier and description.
  F3  Stop: the pump reads Off, its flow reading falls to zero, the pipes it fed run empty.
  F4  Start: the pump runs again at its speed setpoint.
  F5  Speed setpoint: typing 60 in the faceplate changes the running speed to 60 per cent.
  F6  The navigation menu opens and navigates (to /filtration).
  F7  ACK in the top bar acknowledges the faulted pump: its frame stops flashing.
  F8  Reset fault in the faceplate clears the fault: the frame disappears.
  F9  The brilliance menu switches the session to the night palette.
  F10 Module rendering: P-502's OpenBridge alarm list in the faceplate is display only (COBD-025):
      it lists the fault, its row draws the no-acknowledgement icon and no ACK, and a click on that
      cell acknowledges nothing.
  F11 Module rendering: the alarm menu acknowledges an alarm, and a row opens its faceplate.
  F12 A broken permissive holds P-301: the held line, the Interlocks tab, the badge, Start refused;
      and a latched trip holds P-502 after its fault clears, until the Interlocks tab's Reset.
  F13 AIT-301's high limit written below its value raises its alarm, which is acknowledged (in the
      faceplate's stock table, or under module rendering in the alarm menu); the trend draws, with
      at most five time labels in 24 hour form and its limit dashed (COB-083); restoring the limit
      leaves no alarm behind.
  F14 Module rendering: ACK visible in the alarm menu acknowledges every unacknowledged alarm the
      menu shows.
  F15 Nobody signed in (COBD-024): every command control of P-101's faceplate is disabled, and a
      crafted click on the disabled Stop leaves P-101 running.
  F16 Nobody signed in: the top bar's ACK is disabled, the alerts page's table offers no Acknowledge,
      under module rendering the alarm menu offers no ACK and ACK visible is disabled; P-502's alarm
      stays as it was.
  F17 The test login of NEEDS N-COB-9 signs in through the project's identity provider, and its
      session may command (P-101's Start enabled).
  F18 Module rendering, signed in: F11's acknowledgement carries the signed in user's name (compared,
      never printed).
  F19 The trend page (COB-064): one card per historised member, each drawing its line, the time labels
      in 24 hour form; 8 h widens the range; a card's title opens its faceplate.
  F20 The diagram toolbar reaches every symbol: Readout hides and shows the state readout of each automation
      symbol of /filtration, module components and library views alike; ID-tag hides and shows the identifier
      of each symbol, tank and readout of /filtration and /intake; Color draws the pipes that name a medium in
      the medium's colour, and back.
  F21 The alarm menu and the navigation menu close on a click outside them and from their own close button.

Command security (COB-063) refuses every write to a session without the admin role, so F3 to F14
run in a session signed in with the test login (a local file outside the repository, never printed).
Without it, the walk runs F1, F2, F6, F9, F15, F16, F20 and F21 only and says so in its report.

With a restore function (wtp_suite.py), the walk starts and ends with the plant in its initial state.

Usage (ctig's .venv for Playwright):
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/functional.py
        --base http://localhost:8088/data/perspective/client/cadre_hmi_wtp --out workspace/wtp/functional
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # glass.py lies beside this file

# The glass helpers (signing in, the docks, symbols, readouts, the alarm menu, the page scripts) moved to
# glass.py on 2026-10-11, where the generated walk (walk.py) shares them. Every name stays importable
# from this module: the suite and the probes call functional.sign_in, functional.open_device and others.
import glass  # noqa: E402
from glass import (BADGE_AT, BELL, CHART_AXIS, CHART_LINE, CRAFTED_CLICK, DISABLED, LIST_INFO,  # noqa: E402,F401
                   LOGIN_FILE, MODULE_PUMP, PANEL, READOUT_AT, ROOT, ROW_ACTION, TREND_CARDS, ack_alarm,
                   badge_shown, button, click_text_in, control_tab, dock, dock_open, idents_shown, module_pump,
                   open_alarm_menu,
                   open_device, pipes_in, popup_open, pump_off, read_login, readout_text, sign_in, speed_shown,
                   status_shown, symbol, value_of, visible_text_count)
# The new frames (`--frame ob`, `--frame obasm`) draw the head with the module's top bar: the helpers below locate the same
# parts there (the bell, the menu and brilliance buttons, the alarm menu's rows and ACK, the palette) and fall back to the
# older selectors on the openbridge and asm frames, selected by the structure of the top dock (`glass.frame_variant`).
from glass import (alert_list, alert_row, bell, click_nav_entry, close_alarm_menu, dimming_button,  # noqa: E402
                   enabled_acks, frame_variant, menu_button, panel, pick_palette, press_ack)


def frame_state(page, tag: str = "P-502"):
    """[classes, visibility] of a pump's alert frame (`glass.frame_state`), by default of P-502, the
    pump the sample starts with faulted."""
    return glass.frame_state(page, tag)


def ensure_initial(page, base: str, restore) -> str:
    """F7 and F8 need P-502 faulted and unacknowledged. An import raises no new alarm event while the
    fault stays on (GF-36), so a P-502 left acknowledged by an earlier walk is reset first (its
    alarm clears and, being acknowledged, leaves the list), then the plant is restored. An
    unacknowledged P-502 is left as it is: clearing it would leave a cleared, unacknowledged event."""
    page.goto(base + "/disinfection", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    st = frame_state(page)
    if st and st[1] == "visible" and "flash-alarm" not in st[0]:
        _, (x, y) = symbol(page, "P-502")
        page.mouse.click(x, y)
        page.wait_for_timeout(2500)
        control_tab(dock(page, "right"))   # a faceplate reselected keeps its tab: Reset is on Control
        button(dock(page, "right"), "Reset fault").click()
        page.wait_for_timeout(3000)
        restore()
        return "reset and restored"
    return "already initial"


def module_steps(page, base: str, restore, check, user: str | None = None) -> None:
    """F10, F11 and F14, for the module rendering. The faceplate's OpenBridge alarm list is display
    only (COB-082, COBD-025); the top bar's alarm menu acknowledges an alarm from its row, opens a
    device's faceplate from a row, and acknowledges every unacknowledged alarm it shows with ACK
    visible. The plant is restored first, so P-502 is faulted and unacknowledged."""
    restore()
    page.goto(base + "/disinfection", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    _, (x, y) = symbol(page, "P-502")
    page.mouse.click(x, y)
    page.wait_for_timeout(2500)
    right = dock(page, "right")
    right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Alarms")).first.click()
    host = ".docked-view-right obc-alert-list-details"
    before = None
    for _ in range(20):
        page.wait_for_timeout(500)
        before = page.evaluate(LIST_INFO, host)
        if before:
            break
    first = (before or [{}])[0]
    shown = bool(before) and len(before) == 1 and "P-502" in str(first.get("source")) \
        and first.get("type") == "level-high" and not first.get("acked")
    cell = page.evaluate(ROW_ACTION, [host, "P-502"]) or {}
    acks = visible_text_count(page, host, "ACK")
    if cell.get("row"):   # where ACK would be: the click reaches the row, which carries no event here
        page.mouse.click(cell["x"], cell["y"])
    page.wait_for_timeout(3000)
    after = page.evaluate(LIST_INFO, host)
    frame = module_pump(page, "P-502")
    check("F10", "P-502's OpenBridge alarm list in the faceplate is display only: the fault listed, "
          "the no-acknowledgement icon and no ACK, a click acknowledges nothing",
          shown and cell.get("noAck") and cell.get("noAckIcon") and not cell.get("button") and acks == 0
          and after and not after[0].get("acked") and frame and frame.get("mode") == "unacked-active",
          f"before {before} cell {({k: cell.get(k) for k in ('noAck', 'noAckIcon', 'button', 'text')})} "
          f"ACK shown {acks} after {after} frame {frame and frame.get('mode')}")
    # F11: the alarm menu (Framework/AlertMenu holds the module's small alert page); P-502 is still
    # unacknowledged, since the faceplate acknowledged nothing.
    right.locator('[data-component="ia.container.coord"]').first.click()   # close the faceplate
    page.wait_for_timeout(1000)
    alerts = open_alarm_menu(page)
    unacked = [a for a in (alerts or []) if not a["acked"]]
    acked_one = press_ack(page, unacked[0]) if unacked else False
    later = None
    for _ in range(12):
        page.wait_for_timeout(500)
        later = alert_list(page)
        if later is not None and len([a for a in later if not a["acked"]]) == len(unacked) - 1:
            break
    fewer = later is not None and len([a for a in later if not a["acked"]]) == len(unacked) - 1
    newly = [a for a in (later or []) if a["acked"] and a["id"] in {u["id"] for u in unacked}]
    by_user = bool(newly) and all(a.get("by") == user for a in newly) if user else None
    row = click_text_in(page, panel(page), "P-502 Fault")
    page.wait_for_timeout(2500)
    txt = right.inner_text() if right.count() else ""
    check("F11", "The alarm menu acknowledges an alarm, and a row opens its device's faceplate",
          bool(unacked) and acked_one and fewer and row and "P-502" in txt and "Distribution pump 2" in txt,
          f"unacked {len(unacked)} then {len([a for a in (later or []) if not a['acked']])}; row {row}; dock {txt[:60]!r}")
    if user:
        check("F18", "The menu's acknowledgement carries the signed in user's name (compared, not printed)",
              by_user, f"acknowledged by the signed in user: {by_user}")
    # F14: ACK visible. P-502's alarm is acknowledged now, and an import raises no new event while its
    # fault stays on (GF-36): ensure_initial resets and restores it, so the menu holds an
    # unacknowledged alarm again.
    ensure_initial(page, base, restore)
    right = dock(page, "right")
    if right.count() and (right.bounding_box() or {}).get("x", 9999) < 1600:
        right.locator('[data-component="ia.container.coord"]').first.click()   # close the faceplate
        page.wait_for_timeout(1000)
    alerts = open_alarm_menu(page)
    unacked = [a for a in (alerts or []) if not a["acked"]]
    btn = page.locator(f'{panel(page)} [data-testid="ack-all-visible-button"]').first
    pressed = False
    if unacked and btn.count():
        btn.click()
        pressed = True
    later, frame = None, None
    for _ in range(16):
        page.wait_for_timeout(500)
        later = alert_list(page)
        frame = module_pump(page, "P-502")
        if later is not None and not [a for a in later if not a["acked"]] and frame and frame.get("mode") == "acked-active":
            break
    left = [a for a in (later or []) if not a["acked"]]
    check("F14", "ACK visible in the alarm menu acknowledges every unacknowledged alarm the menu shows",
          bool(unacked) and pressed and later is not None and not left and frame and frame.get("mode") == "acked-active",
          f"unacked {len(unacked)} pressed {pressed} left {len(left)} frame {frame and frame.get('mode')}")
    click_text_in(page, panel(page), "P-502 Fault")   # a row closes the menu
    page.wait_for_timeout(1500)
    ensure_initial(page, base, restore)


def trend_page_steps(page, base: str, expected: int, check) -> None:
    """F19 (COB-064): the trend page draws one card per historised member, each with a line of history
    and 24 hour time labels; the 8 h range widens every chart's span; a card's title opens its faceplate.
    Read only, so it runs in any session."""
    page.goto(base + "/trends", wait_until="networkidle", timeout=60000)
    cards = []
    for _ in range(30):
        page.wait_for_timeout(1000)
        cards = page.evaluate(TREND_CARDS)
        if len(cards) >= expected and all(c["line"] > 200 for c in cards):
            break
    drawn = [c for c in cards if c["line"] > 200]
    h24 = all(c["times"] and all(len(t) == 5 for t in c["times"]) for c in cards) if cards else False
    before = cards[0]["range"] if cards else ""
    button(page.locator("body"), "8 h").click()
    after = before
    for _ in range(20):
        page.wait_for_timeout(1000)
        now = page.evaluate(TREND_CARDS)
        after = now[0]["range"] if now else ""
        if after != before:
            break
    first = cards[0]["title"] if cards else ""
    at = page.evaluate("""(t) => {
      const l = [...document.querySelectorAll('[data-component="ia.display.flex-repeater"] [data-component="ia.display.label"]')]
        .find(e => !e.closest('[class*="docked-view"]') && e.innerText.trim() === t);
      if (!l) return null; const r = l.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2] }""", first)
    if at:
        page.mouse.click(*at)
    page.wait_for_timeout(2500)
    right = dock(page, "right")
    opened = bool(first) and first in (right.inner_text() if right.count() else "")
    check("F19", "The trend page: one card per historised member, each drawing its line in 24 hour time labels; "
          "8 h widens the range; a title opens its faceplate",
          len(cards) == expected and len(drawn) == expected and h24 and after != before and opened,
          f"cards {len(cards)} of {expected}, drawn {len(drawn)}, 24 h labels {h24}, "
          f"range {before[-24:]!r} then {after[-24:]!r}, faceplate {opened}")


def refusal_steps(page, base: str, check) -> None:
    """F15 and F16 (COB-063, COBD-024), in a session with nobody signed in."""
    page.goto(base + "/intake", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    right = open_device(page, "P-101")
    page.wait_for_timeout(2500)   # the permissions poll every 2 s
    names = ["Start", "Stop", "Auto", "Manual", "Local"]
    state = page.evaluate(DISABLED, names)
    running = not pump_off(page, "P-101")
    crafted = page.evaluate(CRAFTED_CLICK, "Stop")
    page.wait_for_timeout(3500)
    still = not pump_off(page, "P-101")
    refused = "Refused" in right.inner_text()
    tab = right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Interlocks")).first
    tab.click()
    page.wait_for_timeout(1500)
    ilk = page.evaluate(DISABLED, ["Bypass", "Unbypass"])
    # W5: P-502's Reset fault; W4: AIT-301's limit field
    page.goto(base + "/disinfection", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    open_device(page, "P-502")
    page.wait_for_timeout(2500)
    w5 = page.evaluate(DISABLED, ["Reset fault"]).get("Reset fault")
    page.goto(base + "/filtration", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    at = page.evaluate(READOUT_AT, "AIT-301")
    if at:
        page.mouse.click(*at)
    page.wait_for_timeout(3000)
    w4 = page.evaluate(DISABLED, []).get("setpoint")
    check("F15", "Nobody signed in: the faceplates' command controls are disabled (P-101's commands, modes, "
          "setpoint, Bypass; P-502's Reset fault; AIT-301's limit), and a crafted click on Stop leaves P-101 running",
          all(state.get(n) for n in names) and state.get("setpoint") is True and ilk.get("Bypass") is True
          and w5 is True and w4 is True and running and crafted and still,
          f"disabled {state} interlock buttons {ilk} reset fault {w5} limit {w4}; running {running}, "
          f"crafted click {crafted}, still running {still}, refusal shown {refused}")
    # F16: the alarm paths
    page.goto(base + "/disinfection", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    before = frame_state(page)
    top = dock(page, "top")
    ack = button(top, "ACK")   # the strip's ACK in the new frames (both keep the Cadre alert message), else the bar's
    ack_disabled = ack.count() == 0 or ack.is_disabled()
    if page.locator('[data-component^="cadre.ob."]').count():
        # "ack shown" counts the acknowledge controls the menu offers: the visible ACK texts of the older panel, the drawn and
        # enabled row ACK buttons of the new frames' alert menu (which draws them disabled); ACK visible disabled in both
        alerts = open_alarm_menu(page)
        btn = page.locator(f'{panel(page)} [data-testid="ack-all-visible-button"]').first
        menu = {"rows": len(alerts or []), "ack shown": enabled_acks(page),
                "ack visible disabled": btn.count() > 0 and btn.evaluate("e => !!e.disabled")}
    else:   # the stock menu: its alarm status table offers no Acknowledge
        bell(page).click()
        page.wait_for_timeout(4000)
        tbl = page.locator('.popup [data-component="ia.display.alarmstatustable"], '
                           '[class*="popup"] [data-component="ia.display.alarmstatustable"]').first
        rows = tbl.locator(".ia_table__body__row")
        if rows.count() and rows.first.locator(".ia_checkbox").count():
            rows.first.locator(".ia_checkbox").first.click()
            page.wait_for_timeout(500)
        mb = tbl.locator(".ackAlarmsButton")
        menu = {"rows": rows.count(), "ack shown": int(mb.count() > 0 and mb.first.is_visible() and mb.first.is_enabled()),
                "ack visible disabled": True}
    page.keyboard.press("Escape")
    page.wait_for_timeout(800)
    page.goto(base + "/alerts", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(5000)
    table = page.locator('[data-component="ia.display.alarmstatustable"]').first
    rows = table.locator(".ia_table__body__row")
    if rows.count() and rows.first.locator(".ia_checkbox").count():
        rows.first.locator(".ia_checkbox").first.click()
        page.wait_for_timeout(500)
    ackb = table.locator(".ackAlarmsButton")
    table_ack = ackb.count() > 0 and ackb.first.is_visible() and ackb.first.is_enabled()
    page.goto(base + "/disinfection", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    after = frame_state(page)
    menu_ok = menu["ack shown"] == 0 and menu["ack visible disabled"] and menu["rows"] > 0
    check("F16", "Nobody signed in: no acknowledge path is offered (top bar ACK, alerts page table, alarm "
          "menu), and P-502's alarm stays as it was",
          ack_disabled and not table_ack and menu_ok and before == after,
          f"top bar ACK disabled {ack_disabled}; table Acknowledge offered {table_ack}; menu {menu}; "
          f"frame {before} then {after}")


# The automation symbols of /filtration: under the module rendering the pump and the valves are module components and
# the filters the library's views, so the page holds both kinds of symbol the toolbar must reach.
FILTRATION_SYMBOLS = ("P-301", "XV-301", "XV-302", "XV-303", "F-301", "F-302", "F-303")
# The identifiers ID-tag hides and shows: the symbols and readouts of /filtration, the tanks (the clarifier a static
# one), readouts and symbols of /intake (owner's request of 2026-10-22)
FILTRATION_IDENTS = FILTRATION_SYMBOLS + ("PIT-301", "DPIT-301", "DPIT-302", "DPIT-303", "FIT-301", "AIT-301")
INTAKE_IDENTS = ("TK-101", "TK-201", "CL-201", "TK-202", "FIT-101", "AIT-101", "XV-101", "P-101", "DP-201", "M-201",
                 "P-202")
FRESH_WATER = "var(--automation-medium-fresh-water)"
FLOWING = "var(--automation-pipe-primary-color)"   # a pipe the medium flows through, out of colour mode
OUTSIDE = (300, 750)   # blank canvas below the sections of a sample page, clear of the menus and the docks


def frame_steps(page, base: str, check) -> None:
    """F20 and F21 (owner's report of 2026-10-22), read only. F20: the diagram toolbar's Readout button hides and
    shows the state readout of every automation symbol, module component and library view alike; ID-tag hides and
    shows the identifier of every symbol, tank and readout of /filtration and /intake; and Color draws every flowing
    pipe of the page (each names fresh water) in the medium's colour and back. F21: the alarm menu and
    the navigation menu close on a click outside them and from their own close button. A step whose control is not
    found fails its check; it does not stop the walk."""
    page.goto(base + "/filtration", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    readout, color = button(page, "Readout"), button(page, "Color")
    before = status_shown(page, FILTRATION_SYMBOLS)
    off = on = {}
    if readout.count():
        readout.click()
        page.wait_for_timeout(2000)
        off = status_shown(page, FILTRATION_SYMBOLS)
        readout.click()
        page.wait_for_timeout(2000)
        on = status_shown(page, FILTRATION_SYMBOLS)
    tags = {"/filtration": [idents_shown(page, FILTRATION_IDENTS)]}
    id_tag = button(page, "ID-tag")
    if id_tag.count():
        for _ in range(2):
            id_tag.click()
            page.wait_for_timeout(2000)
            tags["/filtration"].append(idents_shown(page, FILTRATION_IDENTS))
    flowing, plain = pipes_in(page, FLOWING), pipes_in(page, FRESH_WATER)
    coloured, back = [], None
    if color.count():
        color.click()
        page.wait_for_timeout(2000)
        coloured = pipes_in(page, FRESH_WATER)
        color.click()
        page.wait_for_timeout(2000)
        back = pipes_in(page, FLOWING)
    page.goto(base + "/intake", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    tags["/intake"] = [idents_shown(page, INTAKE_IDENTS)]
    id_tag = button(page, "ID-tag")
    if id_tag.count():
        for _ in range(2):
            id_tag.click()
            page.wait_for_timeout(2000)
            tags["/intake"].append(idents_shown(page, INTAKE_IDENTS))
    # each page: every identifier shown, then none, then every one again
    id_ok = all(len(v) == 3 and all(v[0].values()) and not any(v[1].values()) and all(v[2].values())
                for v in tags.values())
    readout_ok = bool(before) and all(before.values()) and bool(off) and not any(off.values()) and all(on.values())
    # the plant must be flowing for Color to show anything: a page with no flowing pipe fails, and says so
    color_ok = bool(flowing) and not plain and sorted(coloured) == sorted(flowing) and sorted(back or []) == sorted(flowing)
    check("F20", "The toolbar reaches every symbol: Readout hides and shows the state readout of each automation "
          "symbol (module and library), ID-tag the identifier of each symbol, tank and readout, Color draws every "
          "flowing pipe in its medium's colour and back",
          readout_ok and id_ok and color_ok,
          f"Readout {'found' if readout.count() else 'NOT FOUND'}: before {before} off {off} on {on}; "
          f"ID-tag (shown, off, on again): {tags}; "
          f"Color {'found' if color.count() else 'NOT FOUND'}: flowing {flowing}, in fresh water before {plain}, "
          f"with Color {coloured}, flowing after {back}")
    # F21: the menus. A menu counts as closed only after it was seen open, so a selector that finds no popup fails.
    open_alarm_menu(page)
    alerts = popup_open(page)
    page.mouse.click(*OUTSIDE)
    page.wait_for_timeout(1500)
    outside_closes = alerts and not popup_open(page)
    open_alarm_menu(page)
    again = popup_open(page)
    # its own close control: the header's close button (the first coordinate container of the popup); the new frames' alert
    # menu has none, and the bell that opened it is pressed again (`glass.close_alarm_menu`)
    close_closes = again and close_alarm_menu(page)
    menu = menu_button(page)                # the menu button: the top dock's first coordinate container, or the module bar's Menu
    menu.click()
    page.wait_for_timeout(1500)
    nav = dock_open(page, "left")
    page.mouse.click(OUTSIDE[0] + 600, OUTSIDE[1])
    page.wait_for_timeout(1500)
    nav_outside = nav and not dock_open(page, "left")
    menu = menu_button(page)
    menu.click()
    page.wait_for_timeout(1500)
    nav_again = dock_open(page, "left")
    close = dock(page, "left").locator('[data-component="ia.container.coord"]')     # its header's close button
    if nav_again and close.count():
        close.first.click()
        page.wait_for_timeout(1500)
    nav_close = nav_again and not dock_open(page, "left")
    check("F21", "The alarm menu and the navigation menu close on a click outside them and from their close button",
          outside_closes and close_closes and nav_outside and nav_close,
          f"alarm menu opened {alerts}, closed by a click outside {outside_closes}, opened {again}, closed by its "
          f"button {close_closes}; navigation menu opened {nav}, closed by a click outside {nav_outside}, opened "
          f"{nav_again}, closed by its button {nav_close}")


def interlock_steps(page, base: str, restore, check) -> None:
    """F12 (COB-079): break P-301's permissive by closing the filter inlet valves from their own
    faceplates; the faceplate says why P-301 will not start, its Interlocks tab shows the condition
    not met with live and required values, the badge shows on the symbol, and Start is refused. The
    plant is restored before and after."""
    restore()
    page.goto(base + "/filtration", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    right = open_device(page, "P-301")
    button(right, "Manual").click()
    page.wait_for_timeout(1500)
    button(right, "Stop").click()
    page.wait_for_timeout(3000)
    stopped = pump_off(page, "P-301")
    for valve in ("XV-301", "XV-302"):
        r = open_device(page, valve)
        button(r, "Close").click()
        page.wait_for_timeout(1500)
    page.wait_for_timeout(2500)
    right = open_device(page, "P-301")
    control = right.inner_text()
    held = "Start not permitted: 1 condition not met" in control
    badge = badge_shown(page, "P-301")
    tab = right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Interlocks")).first
    label = tab.inner_text().strip() if tab.count() else ""
    tab.click()
    page.wait_for_timeout(2000)
    pane = right.inner_text()
    row = all(t in pane for t in ("A filter inlet valve is open", "Not met", "Live: Closed", "Required: Open"))
    right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Control\s*$")).first.click()
    page.wait_for_timeout(800)
    button(right, "Start").click()
    page.wait_for_timeout(3500)
    refused = pump_off(page, "P-301") and "Start refused" in right.inner_text()
    permissive = stopped and held and badge and label == "Interlocks (1)" and row and refused
    detail = f"stopped {stopped} held {held} badge {badge} tab {label!r} row {row} refused {refused}"
    latch, ldetail = latch_steps(page, base, restore)
    check("F12", "A broken permissive holds P-301 (held line, Interlocks tab, badge, Start refused), and a "
          "latched trip holds P-502 after its fault clears, until reset", permissive and latch,
          detail + "; latch: " + ldetail)
    restore()


def latch_steps(page, base: str, restore) -> tuple[bool, str]:
    """The latch of F12 (COBD-023): P-502's trip on its own fault latches. Its fault is acknowledged
    first (top bar ACK; P-502 is the plant's only alarm in its initial state), so that the reset leaves
    no cleared, unacknowledged event. After Reset fault the trip's cause is gone but P-502 stays
    interlocked: the held line reads "reset required", the tab "Interlocks (1)", the row "Latched",
    and Start is refused. The tab's Reset releases it, and Start then runs the pump."""
    restore()
    page.goto(base + "/disinfection", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    button(dock(page, "top"), "ACK").click()
    page.wait_for_timeout(3000)
    right = open_device(page, "P-502")
    control_tab(right)
    button(right, "Manual").click()
    page.wait_for_timeout(1500)
    # a Reset while the cause persists releases nothing (the fault is still on)
    itab = right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Interlocks")).first
    itab.click()
    page.wait_for_timeout(1500)
    early = right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Reset\s*$"))
    early_shown = early.count() > 0 and early.first.is_visible()   # shown only once the cause has cleared
    w11 = page.evaluate("""(d) => { for (const b of document.querySelectorAll('[data-component="ia.input.button"]'))
      if (b.innerText.trim() === 'Reset') { b.disabled = false; b.removeAttribute('disabled'); b.click(); return true }
      return false }""", None)
    page.wait_for_timeout(2500)
    control_tab(right)
    button(right, "Reset fault").click()
    page.wait_for_timeout(3500)
    line = "Interlocked: reset required" in right.inner_text()
    button(right, "Start").click()
    page.wait_for_timeout(3500)
    held = pump_off(page, "P-502") and "Start refused: reset required" in right.inner_text()
    tab = right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Interlocks")).first
    label = tab.inner_text().strip() if tab.count() else ""
    tab.click()
    page.wait_for_timeout(2000)
    lamp = "Latched" in right.inner_text()
    button(right, "Reset").click()
    released = ""
    for _ in range(10):
        page.wait_for_timeout(500)
        released = tab.inner_text().strip()
        if released == "Interlocks":
            break
    control_tab(right)
    button(right, "Start").click()
    page.wait_for_timeout(3500)
    runs = not pump_off(page, "P-502")
    ok = line and held and label == "Interlocks (1)" and lamp and released == "Interlocks" and runs and not early_shown
    return ok, (f"Reset offered while faulted {early_shown} (forced click {w11}); line {line} refused {held} "
                f"tab {label!r} lamp {lamp} after reset {released!r} runs {runs}")


def instrument_steps(page, base: str, restore, check) -> None:
    """F13 (COB-062, COB-064): AIT-301's readout opens the instrument faceplate with its value and
    its high limit as a setpoint; a limit written below the value raises the High turbidity alarm,
    because the alarm's setpoint follows the limit; it is acknowledged (`ack_alarm`); the Trend tab
    draws the history. The plant is restored before and after; the restored limit clears the
    acknowledged alarm, so the Alarms label returns to its count before the step and the walk leaves
    no cleared, unacknowledged event behind."""
    restore()
    page.goto(base + "/filtration", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    at = page.evaluate(READOUT_AT, "AIT-301")
    if at:
        page.mouse.click(*at)
    page.wait_for_timeout(2500)
    right = dock(page, "right")
    values = right.inner_text() if right.count() else ""
    opened = "AIT-301" in values and "Filtered water turbidity" in values and "High limit" in values
    alarms = right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Alarms"))
    before = alarms.first.inner_text().strip() if alarms.count() else ""
    field = right.locator('[data-component="ia.input.numeric-entry-field"] input').first
    glass.type_into(field, "0.05")   # F029: the row holds the limit until its Set, which this presses
    def count(text):   # "Alarms (n)", or "Alarms" for none
        m = re.search(r"\((\d+)\)", text)
        return int(m.group(1)) if m else 0
    after = before
    for _ in range(16):
        page.wait_for_timeout(500)
        after = alarms.first.inner_text().strip()
        if count(after) == count(before) + 1:
            break
    acked = ack_alarm(page, "AIT-301") if count(after) == count(before) + 1 else False
    right.locator('[data-component="ia.input.button"]', has_text=re.compile(r"^\s*Trend\s*$")).first.click()
    line = -1
    for _ in range(16):
        page.wait_for_timeout(500)
        line = page.evaluate(CHART_LINE)
        if line > 200:
            break
    axis = page.evaluate(CHART_AXIS) or {"times": [], "dashed": 0}
    # COB-083: 24 hour labels (two digit hours, no AM or PM), at most five of them, and the limit dashed
    look = bool(axis["times"]) and len(axis["times"]) <= 5 and all(len(t) == 5 for t in axis["times"]) \
        and axis["dashed"] >= 1
    restore()
    final = after
    for _ in range(16):
        final = alarms.first.inner_text().strip()
        if count(final) == count(before):
            break
        page.wait_for_timeout(500)
    check("F13", "AIT-301: a high limit written below the value raises its alarm, which is "
          "acknowledged, the trend draws, and the restored limit leaves no alarm behind",
          bool(at) and opened and count(after) == count(before) + 1 and acked and line > 200 and look
          and count(final) == count(before),
          f"opened {opened} alarms {before!r} then {after!r}, acknowledged {acked}, after restore "
          f"{final!r}; trend path {line}, time labels {axis['times']}, dashed limit lines {axis['dashed']}")


def run(base: str, out: Path, restore=None, login: dict | None = None, trends: int = 0) -> dict:
    """The walk; with `restore` (a function that returns the plant to its initial state) also F12
    and F13, and under module rendering F10, F11 and F14. The refusal checks F15 and F16 run in a
    session with nobody signed in; the commands run in a session signed in with `login` (F17), and
    without it only the read only checks run."""
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    results = []

    def check(fid, desc, ok, detail=""):
        results.append({"id": fid, "check": desc, "ok": bool(ok), "detail": detail})

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
        signed = sign_in(page, base, login) if login else False
        initial = ensure_initial(page, base, restore) if restore is not None and signed else "not checked"
        anon = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
        refusal_steps(anon, base, check)
        if trends:   # F19, read only
            trend_page_steps(anon, base, trends, check)
        frame_steps(anon, base, check)   # F20 and F21, read only
        anon.context.close()
        if login:
            page.goto(base + "/intake", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(4000)
            open_device(page, "P-101")
            page.wait_for_timeout(2500)
            enabled = page.evaluate(DISABLED, ["Start"]).get("Start") is False
            check("F17", "The test login signs in through the identity provider, and its session may command",
                  signed and enabled, f"signed in {signed}, Start enabled {enabled}")
        commands = bool(login) and signed
        page.goto(base + "/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(4000)
        # F1 card title navigation
        page.locator('[data-component="ia.display.label"]', has_text="Production").first.click()
        page.wait_for_timeout(3000)
        check("F1", "Card title navigates to its page", page.url.rstrip("/").endswith("/intake"), page.url)
        # F2 faceplate
        _, (x, y) = symbol(page, "P-101")
        page.mouse.click(x, y)
        page.wait_for_timeout(2500)
        right = dock(page, "right")
        txt = right.inner_text() if right.count() else ""
        check("F2", "Symbol click opens the faceplate with identifier and description",
              "P-101" in txt and "Raw water feed pump" in txt, txt[:120].replace("\n", " | "))
        if not commands:   # COBD-024: every write needs the admin role; without the test login stop here
            top = dock(page, "top")
            menu_button(page).click()
            page.wait_for_timeout(1500)
            click_nav_entry(page, "Filtration")
            page.wait_for_timeout(3000)
            check("F6", "Navigation menu opens and navigates", page.url.rstrip("/").endswith("/filtration"), page.url)
            dimming_button(page).click()
            page.wait_for_timeout(1500)
            pick_palette(page, "Night")
            cls = page.evaluate("() => document.querySelector('.ia_container--root').className")
            check("F9", "Brilliance menu switches to the night palette", "palette/night" in cls, cls[:80])
            browser.close()
            rep = {"checks": len(results), "passed": sum(r["ok"] for r in results), "results": results,
                   "initial": initial, "final": "not checked", "signed_in": False,
                   "not_run": "F3 to F5, F7, F8, F10 to F14: no test login (NEEDS N-COB-9)"}
            (out / "functional.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
            return rep
        # F3 stop
        button(right, "Stop").click()
        page.wait_for_timeout(3500)
        p101 = readout_text(page, "P-101")
        fit = value_of(page, "FIT-101")
        stroke = page.evaluate("() => { const p = document.querySelector('path[name=\"p3\"]'); return p ? getComputedStyle(p).stroke : null }")
        empty = page.evaluate("() => { const d = document.createElement('div'); d.style.color = 'var(--automation-pipe-primary-inverted-color)'; document.querySelector('.ia_container--root').appendChild(d); const c = getComputedStyle(d).color; d.remove(); return c }")
        check("F3", "Stop: pump Off, flow 0, fed pipe empty",
              "Off" in p101 and fit.startswith("0.0") and stroke == empty, f"{p101} / {fit} / pipe {stroke} empty {empty}")
        # F4 start
        button(right, "Start").click()
        page.wait_for_timeout(3500)
        ok, detail = speed_shown(page, "P-101", 80)
        check("F4", "Start: pump runs at its setpoint", ok, detail)
        # F5 speed setpoint
        field = right.locator('[data-component="ia.input.numeric-entry-field"] input').first
        glass.type_into(field, "60")   # F029: typed, then Set
        page.wait_for_timeout(3500)
        ok, detail = speed_shown(page, "P-101", 60)
        check("F5", "Speed setpoint 60 changes the running speed", ok, detail)
        glass.type_into(field, "80")
        page.wait_for_timeout(1500)
        # F6 navigation menu
        top = dock(page, "top")
        menu_button(page).click()
        page.wait_for_timeout(1500)
        click_nav_entry(page, "Filtration")
        page.wait_for_timeout(3000)
        check("F6", "Navigation menu opens and navigates", page.url.rstrip("/").endswith("/filtration"), page.url)
        # F7 acknowledge from the top bar
        page.goto(base + "/disinfection", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(4000)
        v, (x, y) = symbol(page, "P-502")

        def frame_classes():
            return frame_state(page)
        before = frame_classes()
        button(top, "ACK").click()
        page.wait_for_timeout(4000)
        after = frame_classes()
        check("F7", "ACK stops the faulted pump's frame flashing",
              before and "flash-alarm" in before[0] and after and "flash-alarm" not in after[0] and after[1] == "visible",
              f"before {before} after {after}")
        # F8 reset fault
        page.mouse.click(x, y)
        page.wait_for_timeout(2500)
        right = dock(page, "right")
        button(right, "Reset fault").click()
        page.wait_for_timeout(4000)
        final = frame_classes()
        check("F8", "Reset fault clears the fault and the frame", final and final[1] == "hidden", f"{final}")
        # F9 palette
        dimming_button(page).click()
        page.wait_for_timeout(1500)
        pick_palette(page, "Night")
        cls = page.evaluate("() => document.querySelector('.ia_container--root').className")
        check("F9", "Brilliance menu switches to the night palette", "palette/night" in cls, cls[:80])
        page.screenshot(path=str(out / "night.png"))
        if restore is not None and page.locator('[data-component^="cadre.ob."]').count():
            module_steps(page, base, restore, check, login["user"] if login else None)
            page.screenshot(path=str(out / "module-steps.png"))
        if restore is not None:   # F12 (COB-079), both renderings
            interlock_steps(page, base, restore, check)
            page.screenshot(path=str(out / "interlock-steps.png"))
        if restore is not None:   # F13 (COB-062), both renderings
            instrument_steps(page, base, restore, check)
            page.screenshot(path=str(out / "instrument-steps.png"))
        # leave the plant as found: P-502 faulted and unacknowledged (F10 and F11 acknowledge it)
        final = ensure_initial(page, base, restore) if restore is not None else "not checked"
        browser.close()
    rep = {"checks": len(results), "passed": sum(r["ok"] for r in results), "results": results, "initial": initial,
           "final": final, "signed_in": True}
    (out / "functional.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rep = run(a.base.rstrip("/"), Path(a.out), login=read_login())
    for r in rep["results"]:
        print(f"{r['id']} {'PASS' if r['ok'] else 'FAIL'}  {r['check']}  [{r['detail'][:150]}]")
    print(f"FUNCTIONAL {rep['passed']}/{rep['checks']}")
    return 0 if rep["passed"] == rep["checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
