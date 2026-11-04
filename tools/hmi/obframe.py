"""The module variant of the new frame (`screen.py --frame ob`, tranche T2 batch F6a; `cloud/FRAME-DESIGN.md`
sections 3, 4.1 and the owner's answers).

The frame is drawn with the module's frame components (`cadre.ob.topbar`, `navigationmenu`, `alertmenu`, `usermenu`,
`brilliancemenu`, wrapped in batches F1 to F5) and needs `--render module`. The views belong to the parent
(`views()`, written by `parent.py`) and cost a child nothing until its page configuration names them (`page_config`);
a child built with `--frame openbridge` or `--frame asm` (the stock frames) is not touched.

Parts (design section 3, owner's answers 2 to 4):

    Framework/OB/Head        the one top dock (GF-90): the module top bar (48 px) over a strip (36 px) that holds the
                             Cadre crumb (`Framework/Crumb`, with its node badges) and the Cadre alert message (the latest
                             alarm and its ACK), both taken from `framework.top_bar`
    Framework/OB/NavDock     the left modal dock: the module navigation menu over the project's navigation
    Framework/OB/AlertMenu   the popup the top bar's bell opens: the module alert menu over the alarm query
    Framework/OB/UserMenu    the popup the top bar's user button opens: sign in and sign out
    Framework/OB/Brilliance  the popup the top bar's dimming button opens: the palette

The scripts are the library's own (`cadre.hmi`): the alarm summary and list, `ack`, `ack_event`, `ack_listed`,
`nav_items`, `page_title`, `crumbs`, `select_alarm_device`, `set_palette`, and the Perspective `login`, `logout`,
`navigate` and `openDock`. The only addition is `cadre.hmi.ob_items`, which shapes their rows into the components' item
lists. Every component event is a script action that cites the event's measured shape (GF-37, wiki page 07) in its first
comment line.
"""
from __future__ import annotations

import json

from . import acks, framework, pv, scripts
from .framework import CAN_CFG, CAN_DEFAULT, NAV_DOCK, _open_menu, _panel_header, root_classes
from .library import open_faceplate

FRAME = "ob"
HEAD_VIEW, NAV_VIEW = "Framework/OB/Head", "Framework/OB/NavDock"
ALERT_VIEW, USER_VIEW, BRILLIANCE_VIEW = "Framework/OB/AlertMenu", "Framework/OB/UserMenu", "Framework/OB/Brilliance"
TOP_BAR_HEIGHT = 48     # the module top bar, measured in Chromium and on the gateway (wiki 12 section 17.26.7)
STRIP_HEIGHT = 36       # the crumb and the alert message, beneath the bar
HEAD_HEIGHT = TOP_BAR_HEIGHT + STRIP_HEIGHT
# the popups' right offsets, as the default frame's top bar places them (framework.top_bar)
ALERT_RIGHT, BRILLIANCE_RIGHT, USER_RIGHT = 8, 56, 8
ALERT_POPUP, BRILLIANCE_POPUP, USER_POPUP = "alertMenu", "brilliance", "userMenu"
# the clock shows the gateway's wall time, as the default frame's clock does: the date is the wall time written as an
# instant, and the offset is 0
CLOCK_DATE = 'dateFormat(now(1000), "yyyy-MM-dd\'T\'HH:mm:ss\'Z\'")'
ALERT_SIZE = {"width": 640, "height": 600}   # the alert menu draws 640 by 560; the Ack all bar and its question follow


def _events(**handlers: list[str]) -> dict:
    """A node's component events (GF-37): `onName=[script lines]`, each a script action run on the gateway."""
    return {"component": {name: pv.script_handler(lines) for name, lines in handlers.items()}}


def nav_icons() -> list[str]:
    """The package icons the module bundles for a navigation item (the enumeration of its `iconName`, read from the
    module's contract, which the generator checks against the pinned package): a navigation item whose icon is one of them
    shows it, any other shows none."""
    from . import screen   # imported here: screen imports parent, which imports this module
    comp = json.loads(screen.MODULE_COMPONENTS.read_text(encoding="utf-8"))
    return [n for n in comp["cadre.ob.navigationitem"]["props"]["iconName"]["enum"] if n]


def alert_type_expr() -> str:
    """The top bar's `alertType` from the highest active priority, by wiki 13 section 11.1 (`PRIORITY_STATUS` says which
    priorities have an alert colour; `ALERT_TYPE` the package level of each): Diagnostic has none, so the bell is idle."""
    status, level = scripts.constant("PRIORITY_STATUS"), scripts.constant("ALERT_TYPE")
    return ("case({view.custom.alarm.highest}, "
            + ", ".join(f"'{p}', '{level[p]}'" for p in status if status[p]) + ", '')")


# ---------------------------------------------------------------------------------------------------------
# The top dock
# ---------------------------------------------------------------------------------------------------------
def bar_node(menu: list[str] | None = None, apps: list[str] | None = None, page_after_crumbs: bool = False) -> dict:
    """The module top bar node of the head. `menu` is the script of the menu button (by default it opens the navigation dock), `apps`
    the script of the apps button (given, the button is shown and wired: the ASM variant's second button, `obasm.py`), and
    `page_after_crumbs` gives the page name way to the crumb where the page names a node (wiki 04 section 7 item 4), as the ASM
    bar's page name does. Called with no argument it is the module variant's bar."""
    page = pv.bind(pv.prop("page.props.path"), [pv.script_transform(["return cadre.hmi.page_title(self.session, value)"])])
    if page_after_crumbs:
        page = pv.bind(pv.expr("if(len({view.custom.crumbs}) > 0, '', {page.props.path})"), [pv.script_transform([
            "return cadre.hmi.page_title(self.session, value) if value else ''"])])
    handlers = {
        "onMenuButtonClick": menu or [
            "# GF-37: the event carries nothing; the dock is the one the ASM top bar's menu button opens",
            f"system.perspective.openDock(id='{NAV_DOCK}')"],
        "onAlertClick": [
            "# GF-37: the bell's event carries nothing; the popup is the default bar's, with the alert menu in it",
            _open_menu(ALERT_POPUP, ALERT_VIEW, ALERT_RIGHT)],
        "onDimmingButtonClick": [
            "# GF-37: the event carries nothing",
            _open_menu(BRILLIANCE_POPUP, BRILLIANCE_VIEW, BRILLIANCE_RIGHT)],
        "onUserButtonClick": [
            "# GF-37: the event carries nothing",
            _open_menu(USER_POPUP, USER_VIEW, USER_RIGHT)]}
    if apps:
        handlers["onAppsButtonClick"] = apps
    return pv.node("cadre.ob.topbar", "TopBar", pv.fpos(basis=f"{TOP_BAR_HEIGHT}px", shrink=0), {
        "showDimmingButton": True, "showClock": True, **({"showAppsButton": True} if apps else {})},
        prop_config={
            "props.appTitle": pv.bind(pv.expr("{view.params.appName}")),
            "props.pageName": page,
            "props.nAlerts": pv.bind(pv.expr("{view.custom.alarm.count}")),
            "props.alertType": pv.bind(pv.expr(alert_type_expr())),
            "props.blinking": pv.bind(pv.expr("{view.custom.alarm.unacked} > 0")),
            "props.date": pv.bind(pv.expr(CLOCK_DATE)),
            "props.showUserButton": pv.bind(pv.expr("{view.params.showUser}"))},
        events=_events(**handlers))


def head() -> dict:
    """`Framework/OB/Head`: the module top bar over the strip of the Cadre crumb and the Cadre alert message. The dock is
    one dock because the gateway draws one dock of a side at a time (GF-90), so the two rows share it, as the ASM frame's
    do. The bar carries the application's name, the page's name (`cadre.hmi.page_title`, as the default bar's), its own
    bell and clock, and the menu, dimming and user buttons. The bell's count and colour follow the library's alarm summary
    (`cadre.hmi.alarm_summary`, every 2 s) and the clock the gateway's time. The silence control is hidden (owner's answer
    4). The command text is left empty: the bar draws a text in that slot as it stands, and the gateway run found it run on
    from the page name ("Engine roomCommand"); the frame has no command to name there."""
    src = framework.top_bar()   # the strip's three nodes and the data they read are the default bar's own
    kids = {k["meta"]["name"]: k for k in src["root"]["children"]}
    bar = bar_node()
    strip = pv.node("ia.container.flex", "Strip", pv.fpos(basis=f"{STRIP_HEIGHT}px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"overflow": "hidden"}},
        children=[kids["Crumbs"], kids["Spacer"], kids["AlertMessage"]])
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/bar")}, children=[bar, strip])
    params = {"appName": "App", "showUser": True}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params},
                   size={"width": 1600, "height": HEAD_HEIGHT}, custom=src["custom"],
                   custom_config={k: v for k, v in src["propConfig"].items() if k.startswith("custom.")})


# ---------------------------------------------------------------------------------------------------------
# The navigation dock
# ---------------------------------------------------------------------------------------------------------
def nav_dock() -> dict:
    """`Framework/OB/NavDock`: the module navigation menu in the left dock. Its items are the project's navigation
    (`cadre.hmi.nav_items`, with the counts of each item's node, polled every 2 s and on a change of page) and its footer
    (`session.custom.nav.footer`), shaped by `cadre.hmi.ob_items`; the item for the open page is checked. A press
    navigates to the item's route, as the default menu's does, and closes the dock."""
    icons = nav_icons()

    def cfg(rows: str) -> dict:
        return pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {page.props.path}, '')"), [pv.script_transform([
            f"return cadre.hmi.ob_items('nav', {rows}, value, {icons!r})"])])
    menu = pv.node("cadre.ob.navigationmenu", "Menu", pv.fpos(grow=1, basis="0px"), {"items": [], "footerItems": []},
                   prop_config={"props.items": cfg("cadre.hmi.nav_items(self.session)"),
                                "props.footerItems": cfg("list(self.session.custom.nav['footer'])")},
                   events=_events(onItemClick=[
                       "# GF-37: event.id is the id of the item pressed, at any depth; ob_items sets it to the item's route",
                       "if event.id:",
                       "\tsystem.perspective.navigate(event.id)",
                       f"\tsystem.perspective.closeDock('{NAV_DOCK}')"]))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/menu")},
                   children=[_panel_header("Header", "Menu", f"system.perspective.closeDock('{NAV_DOCK}')"), menu])
    return pv.view(root, size={"width": 320, "height": 800})


# ---------------------------------------------------------------------------------------------------------
# The popups
# ---------------------------------------------------------------------------------------------------------
def alert_menu() -> dict:
    """`Framework/OB/AlertMenu`: the module alert menu over the alarm query. The rows come from `cadre.hmi.alarm_list`
    (the project scope, polled every 2 s) shaped by `cadre.hmi.ob_items`. The acknowledgements are the default frame's
    module panel's: a row's ACK is `ack` under write path W8, ACK visible is `ack_event` under W9, and a row opens its
    device's faceplate (`select_alarm_device`). The Ack all bar of the default frame's panels follows, with its Confirm row
    (`acks.bar`, wiki 13 section 10.6): the menu's own ACK visible acts at once, as the panel's does, and the bar asks
    first. The silence control is hidden and the Alerts button goes to `/alerts`."""
    poll = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, '', '')"), [pv.script_transform([
        "alerts = cadre.hmi.alarm_list(self.session.custom.alarmScope, value, session=self.session)",
        "may = cadre.hmi.allowed(self.session, 'W8')",
        "return {'alerts': alerts, 'items': cadre.hmi.ob_items('alerts', alerts, may)}"])])
    menu = pv.node("cadre.ob.alertmenu", "Menu", pv.fpos(basis="560px", shrink=0), {"items": []},
                   prop_config={"props.items": pv.bind(pv.expr("{view.custom.alarms.items}")),
                                "props.canAckAll": pv.bind(pv.expr("{view.custom.can.W9}"))},
                   events=_events(
                       onAckClick=[
                           "# GF-37: event.id is the id of the row whose ACK was pressed (the alarm event's id)",
                           "self.view.custom.ackMessage = cadre.hmi.ack_listed([event.id], self.session, 'W8')"],
                       onAckAllClick=[
                           "# GF-37: event.ids holds the id of each visible row that has one (ACK visible)",
                           "self.view.custom.ackMessage = cadre.hmi.ack_message(cadre.hmi.ack_event(event, self.session, path='W9'))"],
                       onItemClick=[
                           "# GF-37: event.id is the row's id; its record is in view.custom.alarms.alerts",
                           "rows = [a for a in self.view.custom.alarms.alerts if a['id'] == event.id]",
                           "if rows and cadre.hmi.select_alarm_device(self.session, rows[0]):",
                           f"\tsystem.perspective.closePopup('{ALERT_POPUP}')",
                           *open_faceplate("\t")],
                       onGoToAlertListClick=[
                           "# GF-37: the event carries nothing",
                           f"system.perspective.closePopup('{ALERT_POPUP}')",
                           "system.perspective.navigate('/alerts')"]))
    bar = acks.bar(selections=[], can_selected="W8", can_all="W9", path_selected="W8", path_all="W9", selectable=False)
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes()}, children=[menu] + bar)
    return pv.view(root, size=dict(ALERT_SIZE),
                   custom={"alarms": {"alerts": [], "items": []}, "can": dict(CAN_DEFAULT), **acks.custom()},
                   custom_config={"custom.alarms": poll, "custom.can": CAN_CFG,
                                  "custom.shown": pv.bind(pv.expr("{view.custom.alarms.alerts}")),
                                  "custom.unacked": acks.unacked_binding("{view.custom.alarms.alerts}")})


def user_menu() -> dict:
    """`Framework/OB/UserMenu`: the module user menu. It shows the signed in user (`session.props.auth`, GF-43) or the Sign in
    button; Sign in is `system.perspective.login()` and Sign out `system.perspective.logout()`, as the default frame's menu
    calls them (GF-44). The component has no credential property, and none is bound."""
    who = "{session.props.auth.user.userName}"
    signed = "{session.props.auth.authenticated}"
    menu = pv.node("cadre.ob.usermenu", "Menu", pv.fpos(grow=1, basis="0px"), {},
                   prop_config={
                       "props.type": pv.bind(pv.expr(f"if({signed}, 'signed-in', 'sign-in')")),
                       "props.userLabel": pv.bind(pv.expr(f"coalesce({who}, '')")),
                       "props.userInitials": pv.bind(pv.expr(who), [pv.script_transform([
                           "return (value or '')[:2].upper()"])]),
                       "props.userRole": pv.bind(pv.expr("{session.props.auth.user.roles}"), [pv.script_transform([
                           "return ', '.join([unicode(r) for r in (value or [])])"])])},
                   events=_events(
                       onSignInClick=["# GF-37: the event carries nothing (no credential); the gateway's login opens",
                                      "system.perspective.login()"],
                       onSignOutClick=["# GF-37: the event carries nothing", "system.perspective.logout()"]))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes()}, children=[menu])
    return pv.view(root, size={"width": 320, "height": 280})


def brilliance_menu() -> dict:
    """`Framework/OB/Brilliance`: the module brilliance menu. A palette pressed is `cadre.hmi.set_palette`, the default
    frame's path (the session's palette and the Ignition theme); the menu follows `session.custom.palette`. The brightness
    section is hidden: Cadre has no brightness function."""
    keys = tuple(scripts.constant("PALETTE_THEME"))
    menu = pv.node("cadre.ob.brilliancemenu", "Menu", pv.fpos(grow=1, basis="0px"), {"showBrightness": False},
                   prop_config={"props.palette": pv.bind(pv.expr("coalesce({session.custom.palette}, 'day')"))},
                   events=_events(onPaletteChanged=[
                       "# GF-37: event.value is the palette chosen: night, dusk, day or bright",
                       f"if event.value in {keys!r}:",
                       "\tcadre.hmi.set_palette(self.session, event.value)"]))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes()}, children=[menu])
    return pv.view(root, size={"width": 320, "height": 280})


def views() -> dict[str, dict]:
    """The views of the module frame, written into the parent beside the library's own."""
    return {HEAD_VIEW: head(), NAV_VIEW: nav_dock(), ALERT_VIEW: alert_menu(), USER_VIEW: user_menu(),
            BRILLIANCE_VIEW: brilliance_menu()}


# ---------------------------------------------------------------------------------------------------------
# The child: page configuration and session data
# ---------------------------------------------------------------------------------------------------------
def shared_docks(app_name: str = "App") -> dict:
    """`framework.shared_docks` with the module frame: the head (bar and strip) in the one top dock, the module
    navigation menu in the left dock (modal, GF-71), the faceplate dock at the right as it is."""
    docks = framework.shared_docks(app_name)
    docks["top"][0].update(viewPath=HEAD_VIEW, size=HEAD_HEIGHT, viewParams={"appName": app_name, "showUser": True})
    docks["left"][0].update(viewPath=NAV_VIEW)
    return docks


def page_config(app_name: str, pages: dict) -> dict:
    """The page configuration of a child built with `--frame ob`: the pages, the alerts route and the docks above."""
    p = {"/alerts": {"title": "Alerts", "viewPath": "Framework/AlertsPage"}}
    p.update(pages)
    return {"pages": p, "sharedDocks": shared_docks(app_name)}


def session_custom() -> dict:
    """The `session.custom` keys a child built with `--frame ob` adds to the parent's defaults: the frame's name. The
    navigation, the hierarchy, the alarm scope and the device index are the generator's own, as for every frame."""
    return {"frame": FRAME}
