"""The application frame: top bar, navigation menu, faceplate dock, menus, alerts page.

The navigation philosophy is OpenBridge's, as the OpenStudio documentation describes it
(wiki page 04): a header in a top dock shared by every page; a navigation menu in a left
dock opened on demand from the header's menu button and closed on navigation; pages that
group content in cards; device detail in a right dock; one session-wide palette chosen in
the brilliance menu; alarms summarised in the header and listed on an alerts page.

Everything is stock Perspective: docks and the `dock` toggle action (IGW:12-events-and-actions
section 5, seven corpus uses), `system.perspective.navigate`, `openDock`, `closeDock`,
`openPopup`, `closePopup` (IGW:23-perspective-scripting section 1), `system.alarm.queryStatus`
with its `priority` and `state` filters (IGW:22-system-api-reference section 3.1), and the
alarm status and journal tables (IGW:13-alarms).
"""
from __future__ import annotations

from . import alarms, pv, scripts
from .library import icon_svg, svg, rrect_d, open_faceplate, open_popup_line, ALERT_COLOURS
from .library import FACEPLATE_POPUP_ID, FACEPLATE_POPUP_VIEW, FACEPLATE_MODES, DOCKED

NAV_DOCK, FACEPLATE_DOCK = "nav", "faceplate"


def root_classes(extra: str = "") -> dict:
    """Palette class plus any surface classes, on every page, dock and popup root."""
    pre = (extra + " ") if extra else ""
    return pv.bind(pv.expr(f"'{pre}cadre/palette/' + coalesce({{session.custom.palette}}, 'day')"))


def _label(name, pos, text_expr=None, classes="cadre/font/body cadre/text/active", text=None,
           style=None, visible=None):
    props = {"style": {"classes": classes, "whiteSpace": "nowrap", **(style or {})}}
    if text is not None:
        props["text"] = text
    pc = {}
    if text_expr:
        pc["props.text"] = pv.bind(pv.expr(text_expr))
    if visible:
        pc["meta.visible" if "x" in pos else "position.display"] = pv.bind(pv.expr(visible))
    return pv.node("ia.display.label", name, pos, props, prop_config=pc or None)


def _icon_button(name, icon_name, events, *, visible=None, extra_config=None, classes="cadre/button/flat"):
    ib = icon_svg("Icon", icon_name, pv.cpos(8, 8, 24, 24))
    return pv.node("ia.container.coord", name, pv.fpos(basis="40px", shrink=0),
                   {"style": {"classes": classes, "width": "40px", "height": "40px",
                              "overflow": "hidden", "margin": "0 2px"}},
                   prop_config={**({"position.display": pv.bind(pv.expr(visible))} if visible else {}),
                                **(extra_config or {})},
                   events=events, children=[ib])


# The priority's colour by rank (F053, COBD-044; `cadre.hmi.PRIORITY_STATUS`): Diagnostic has none.
PRIORITY_VAR = ("case({view.custom.alarm.highest}, " + ", ".join(
    f"'{p}', 'var({ALERT_COLOURS[s]})'" for p, s in scripts.constant("PRIORITY_STATUS").items() if s)
    + ", 'var(--element-neutral-color)')")


# Command security (COB-063, COBD-024): a view that offers a write path polls the session's permissions
# into `custom.can` (one Boolean per write path of NOTE-COB-04), and each command control binds `enabled`
# to its path. The binding is advisory: every write goes through a checked function of `cadre.hmi`,
# which refuses a session whose user lacks the admin role.
CAN_DEFAULT = {w: False for w in scripts.constant("WRITE_PATHS")}
# Ownership by mode (COBD-044): the paths a device's owner gates, and the confirmation a faceplate
# holds between the click on a move (Take control, Release, Maintenance) and its Confirm.
OWNER_GATED = scripts.constant("OWNER_GATED")
# Confirmation (F029 of the ASMP study, COBD-045): a command that changes the state of the process, and a
# setpoint, is written only once the operator confirms it. A command button sets `custom.pending` and
# writes nothing; the Confirm row beneath the tabs shows the question and makes the one checked write
# (`cadre.hmi.command`, which hands W11, W16, W17 and W18 to their own functions), and Cancel clears it.
# A row's field (a setpoint, a limit, a configuration value) holds what was typed until Set writes it,
# or until the cancel button puts the tag's value back; a bypass waits for its own Confirm.
PENDING_DEFAULT = {"active": False, "device": "", "path": "", "member": "", "value": 0, "text": ""}
CONFIRMED_PATHS = ("W1", "W2", "W5", "W11", "W13", "W16", "W17", "W18")
CONFIRM, CANCEL, SET, UNDO = "Confirm", "Cancel", "Set", "\u00d7"


def _pend(path: str, member: str, value: str, text: str = "self.props.text + ': ' + self.session.custom.selectedTitle + '?'") -> str:
    """The line of a command button: the write it asks for, pending until Confirm. `value` and `text`
    are Python source: by default the question is the button's caption and the device's identifier."""
    return ("self.view.custom.pending = {'active': True, 'device': self.view.params.deviceId, "
            f"'path': '{path}', 'member': '{member}', 'value': {value}, 'text': {text}}}")


def _confirm_row() -> dict:
    """The question of the pending command and its answers, on every tab of the faceplate. Confirm
    makes the one checked write, enabled by the permission of the pending path; a pending command
    shows only for the device it was asked on, and a new device clears it (`_tabbed`)."""
    enabled = ("case({view.custom.pending.path}, " + ", ".join(f"'{w}', {{view.custom.can.{w}}}" for w in CONFIRMED_PATHS)
               + ", false)")
    clear = f"self.view.custom.pending = {PENDING_DEFAULT!r}"
    return pv.node("ia.container.flex", "Confirm", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "alignItems": "center",
        "style": {"gap": "8px", "classes": "cadre/alert/badge-caution", "padding": "0 8px", "borderRadius": "4px"}},
        prop_config={"position.display": pv.bind(pv.expr(
            "{view.custom.pending.active} && {view.custom.pending.device} = {view.params.deviceId}"))},
        children=[_label("ConfirmText", pv.fpos(grow=1, basis="0px"), "{view.custom.pending.text}",
                         classes="cadre/font/body-active cadre/text/active", style={"whiteSpace": "normal"}),
                  pv.node("ia.input.button", "ConfirmYes", pv.fpos(basis="96px", shrink=0), {
                      "text": CONFIRM, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "36px"}},
                      prop_config={"props.enabled": pv.bind(pv.expr(enabled))},
                      events=pv.on_action([
                          "p = self.view.custom.pending",
                          "msg = cadre.hmi.command(self.session, p.path, self.view.params.deviceId, p.member, p.value)",
                          clear,
                          "self.view.custom.message = msg"])),
                  pv.node("ia.input.button", "ConfirmNo", pv.fpos(basis="96px", shrink=0), {
                      "text": CANCEL, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "36px"}},
                      events=pv.on_action([clear]))])
CAN_CFG = pv.bind(pv.expr("now(2000)"), [pv.script_transform(["return cadre.hmi.permissions(self.session)"])])


def _can(path: str) -> dict:
    return pv.bind(pv.expr(f"{{view.custom.can.{path}}}"))


# Shelving with a time limit (F045 of the ASMP study, COBD-044): a stock table shelves only for the
# library's times (`alarms.SHELVE_SECONDS`, 5 minutes to 8 hours; IGW ia.display.alarmstatustable).
TABLE_PROPS = {"shelvingTimes": list(alarms.SHELVE_SECONDS)}


def _table_actions(path: str = "W7") -> dict:
    """The stock alarm status table's own actions, bound to the permission of write path W7: the
    component acknowledges and shelves itself, so no project script can check it (GF-40)."""
    return {f"props.{k}": _can(path) for k in ("enableAcknowledge", "enableShelve", "enableUnshelve")}


# The alarm tables take the project scope as a source path condition; `*` means every alarm.
SCOPE_SOURCE = "if(coalesce({session.custom.alarmScope}, '*') = '*', '', {session.custom.alarmScope})"


def _open_menu(popup_id: str, view: str, right: int) -> str:
    """The call that opens a top bar menu. A menu is modal so that a click outside it lands on the overlay and
    closes it (`overlayDismiss`); without the overlay nothing outside the menu closed it but Escape (GF-70)."""
    return (f"system.perspective.openPopup('{popup_id}', '{view}', params={{}}, position={{'top': 48, 'right': {right}}}, "
            "showCloseIcon=False, draggable=False, modal=True, overlayDismiss=True)")


def _panel_header(name: str, title: str, close: str) -> dict:
    """A menu's or a panel's title and its close button, which runs the script line `close`."""
    return pv.node("ia.container.flex", name, pv.fpos(basis="40px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"padding": "0 0 0 8px"}},
        children=[_label("Title", pv.fpos(grow=1), text=title, classes="cadre/font/body-active cadre/text/active"),
                  _icon_button("Close", "close-google", {"dom": {"onClick": pv.script_handler([close])}})])
# The in-page results panel of the ASM frame's search field (L4; `navigation.search_results`). The embed is
# defined here because the library's own pages (alerts, trends) carry it as well: out of the flow
# (`position: absolute`, the four sides 0, above the canvas), shown while `session.custom.searchOpen` is true and
# the query is not empty, which only the ASM frame's field makes it. In the default frame it never shows.
SEARCH_VIEW = "Framework/ASM/SearchResults"
SEARCH_SHOWN = "coalesce({session.custom.searchOpen}, false) && len(coalesce({session.custom.searchQuery}, '')) > 0"


def search_panel() -> dict:
    """The embed of `Framework/ASM/SearchResults` as the last child of a page's root."""
    return pv.node("ia.display.view", "SearchPanel", pv.fpos(basis="0px", shrink=0), {
        "path": SEARCH_VIEW, "useDefaultViewHeight": False, "useDefaultViewWidth": False,
        "style": {"position": "absolute", "top": "0px", "left": "0px", "right": "0px", "bottom": "0px", "zIndex": 50}},
        prop_config={"position.display": pv.bind(pv.expr(SEARCH_SHOWN))})


def top_bar() -> dict:
    alarm_cfg = {"custom.alarm": pv.bind(pv.expr("now(2000)"), [pv.script_transform([
        "return cadre.hmi.alarm_summary(self.session.custom.alarmScope)"])])}
    menu = _icon_button("MenuButton", "menu", {"dom": {"onClick": {
        "config": {"id": NAV_DOCK, "type": "toggle"}, "scope": "C", "type": "dock"}}})
    app = _label("AppName", pv.fpos(shrink=0), "{view.params.appName}",
                 classes="cadre/font/body cadre/text/neutral", style={"marginLeft": "8px"})
    page = pv.node("ia.display.label", "PageName", pv.fpos(shrink=0), {
        "style": {"classes": "cadre/font/body-active cadre/text/active", "whiteSpace": "nowrap",
                  "marginLeft": "8px"}},
        prop_config={"props.text": pv.bind(pv.prop("page.props.path"), [pv.script_transform([
            "return cadre.hmi.page_title(self.session, value)"])]),
                     "position.display": pv.bind(pv.expr("len({view.custom.crumbs}) = 0"))})
    # F036: the nodes from the root to the page's own, each with its badges, where the page names a node
    trail = pv.node("ia.display.flex-repeater", "Crumbs", pv.fpos(shrink=1), {
        "path": "Framework/Crumb", "direction": "row", "useDefaultViewHeight": False, "useDefaultViewWidth": True,
        "elementPosition": {"shrink": 0}, "instances": [], "style": {"marginLeft": "8px", "gap": "4px"}},
        prop_config={"props.instances": pv.bind(pv.expr("{view.custom.crumbs}")),
                     "position.display": pv.bind(pv.expr("len({view.custom.crumbs}) > 0"))})
    spacer = pv.node("ia.container.flex", "Spacer", pv.fpos(grow=1), {})
    # Alert message: the most severe active alarm, its time, and an ACK button.
    msg_icon = svg("Icon", pv.fpos(basis="20px", shrink=0), [
        {"type": "path", "name": "tri", "d": "M10 2L19 18H1Z", "fill": {"paint": "var(--alert-alarm-color)"}},
        {"type": "path", "name": "mark", "d": "M9.2 7H10.8V12.5H9.2ZM9.2 13.8H10.8V15.4H9.2Z",
         "fill": {"paint": "var(--on-alarm-color)"}}], view_box="0 0 20 20",
        extra_config={"props.elements[0].fill.paint": pv.bind(pv.expr(PRIORITY_VAR))})
    msg = pv.node("ia.container.flex", "AlertMessage", pv.fpos(basis="420px", shrink=1), {
        "direction": "row", "alignItems": "center",
        "style": {"border": "1px solid var(--border-outline-color)", "borderRadius": "6px",
                  "height": "32px", "padding": "0 4px 0 8px", "gap": "8px",
                  "backgroundColor": "var(--normal-enabled-background-color)", "margin": "0 8px"}},
        prop_config={"position.display": pv.bind(pv.expr("{view.custom.alarm.count} > 0"))},
        children=[
            msg_icon,
            _label("Text", pv.fpos(grow=1), "{view.custom.alarm.topLabel}",
                   classes="cadre/font/body-active cadre/text/active",
                   style={"overflow": "hidden", "textOverflow": "ellipsis"}),
            _label("Time", pv.fpos(shrink=0), "{view.custom.alarm.topTime}",
                   classes="cadre/font/label cadre/text/neutral"),
            pv.node("ia.input.button", "Ack", pv.fpos(basis="56px", shrink=0), {
                "text": "ACK", "style": {"classes": "cadre/button/normal cadre/font/button", "height": "28px"}},
                prop_config={"position.display": pv.bind(pv.expr("{view.custom.alarm.unacked} > 0")),
                             "props.enabled": _can("W6")},
                events=pv.on_action(["cadre.hmi.ack_top(self.session.custom.alarmScope, self.session)"])),
        ])
    bell = pv.node("ia.container.flex", "AlertButton", pv.fpos(basis="56px", shrink=0), {
        "direction": "row", "alignItems": "center", "justify": "center",
        "style": {"classes": "cadre/button/normal", "height": "32px", "gap": "2px",
                  "margin": "0 4px", "cursor": "pointer"}},
        prop_config={"props.style.classes": pv.bind(pv.expr(
            "'cadre/button/normal' + if({view.custom.alarm.unacked} > 0, ' cadre/alert/flash-alarm', '')"))},
        events={"dom": {"onClick": pv.script_handler([_open_menu("alertMenu", "Framework/AlertMenu", 8)])}},
        children=[
            icon_svg("Bell", "notification-filled", pv.fpos(basis="20px", shrink=0),
                     extra_config={"props.elements[0].fill.paint": pv.bind(pv.expr(PRIORITY_VAR))}),
            _label("Count", pv.fpos(shrink=0), "toStr({view.custom.alarm.count})",
                   classes="cadre/font/body-active cadre/text/active"),
        ])
    bright = _icon_button("BrillianceButton", "palette-dimming", {"dom": {"onClick": pv.script_handler([
        _open_menu("brilliance", "Framework/BrillianceMenu", 56)])}})
    user = _icon_button("UserButton", "user", {"dom": {"onClick": pv.script_handler([
        _open_menu("userMenu", "Framework/UserMenu", 8)])}}, visible="{view.params.showUser}")
    clock = _label("Clock", pv.fpos(shrink=0),
                   "dateFormat(now(1000), 'HH:mm') + ' ' + {view.params.clockLabel}",
                   classes="cadre/font/body-active cadre/text/active",
                   style={"margin": "0 12px 0 8px"})
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "row", "alignItems": "center", "style": {"overflow": "hidden", "padding": "0 4px"}},
        prop_config={"props.style.classes": root_classes("cadre/surface/bar")},
        children=[menu, app, page, trail, spacer, msg, bell, bright, user, clock])
    params = {"appName": "App", "showUser": True, "clockLabel": "UTC", "alertsPath": "/alerts"}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params},
                   size={"width": 1600, "height": 48},
                   custom={"alarm": {"count": 0, "unacked": 0, "highest": "", "topLabel": "", "topTime": ""},
                           "can": dict(CAN_DEFAULT), "crumbs": []},
                   custom_config={**alarm_cfg, "custom.can": CAN_CFG, "custom.crumbs": CRUMBS_CFG})


# Alarm badges of the plant hierarchy (F046 of the ASMP study, COB-141): a pill for each priority with active
# alarms in the node's devices and beneath, the count in the priority's colour by rank (F053), Diagnostic
# neutral, nothing at 0. One shape for every priority: the colour codes the rank, as the frame's do, so no
# second shape code stands beside OpenBridge's status shapes.
NO_COUNTS = {**{p: 0 for p in scripts.constant("PRIORITIES")}, "total": 0, "unacked": 0}
CRUMBS_CFG = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {page.props.path}, '')"), [pv.script_transform([
    "return cadre.hmi.crumbs(self.session, value)"])])


def badges() -> dict:
    """`Framework/Badges`: the counts of one node (`params.counts`, an entry of `cadre.hmi.node_counts`)."""
    kids = []
    for p, status in scripts.constant("PRIORITY_STATUS").items():
        neutral = not status
        kids.append(_label(f"Badge_{p}", pv.fpos(shrink=0), f"toStr({{view.params.counts.{p}}})",
                           classes="cadre/font/label " + ("cadre/text/neutral" if neutral else f"cadre/alert/badge-{status}"),
                           style={"padding": "0 6px", "borderRadius": "8px",
                                  **({"border": "1px solid var(--border-outline-color)"} if neutral else {})},
                           visible=f"{{view.params.counts.{p}}} > 0"))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "row", "alignItems": "center",
                                                      "style": {"gap": "4px", "overflow": "hidden"}}, children=kids)
    return pv.view(root, params={"counts": dict(NO_COUNTS)}, param_dirs={"counts": "input"},
                   size={"width": 160, "height": 20})


def _badges_embed(pos: dict) -> dict:
    return pv.node("ia.display.view", "Badges", pos, {
        "path": "Framework/Badges", "params": {"counts": dict(NO_COUNTS)}, "useDefaultViewHeight": False,
        "useDefaultViewWidth": False},
        prop_config={"props.params.counts": pv.bind(pv.expr("{view.params.counts}"))})


def crumb() -> dict:
    """`Framework/Crumb`: one node of the top bar's breadcrumb (F036): a chevron before every node but the
    first, the node's name, which opens the node's first page, and its badges."""
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "row", "alignItems": "center", "style": {"gap": "6px", "overflow": "hidden", "cursor": "pointer"}},
        events={"dom": {"onClick": pv.script_handler([
            "if self.view.params.route:",
            "\tsystem.perspective.navigate(self.view.params.route)"])}},
        children=[icon_svg("Chevron", "chevron-right-google", pv.fpos(basis="16px", shrink=0),
                           visible="!{view.params.first}"),
                  _label("Name", pv.fpos(shrink=1), "{view.params.name}", classes="cadre/font/body-active cadre/text/active",
                         style={"overflow": "hidden", "textOverflow": "ellipsis"}),
                  _badges_embed(pv.fpos(basis="0px", grow=1))])
    params = {"name": "", "route": "", "counts": dict(NO_COUNTS), "first": True}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params}, size={"width": 220, "height": 40})


def nav_item() -> dict:
    sel = "{page.props.path} = {view.params.path}"
    ic = pv.node("ia.shapes.svg", "Icon", pv.fpos(basis="24px", shrink=0), {
        "viewBox": "0 0 24 24", "elements": [], "style": {"height": "24px"}},
        prop_config={"props.elements": pv.bind(pv.expr("{view.params.icon}"), [pv.script_transform([
            "return cadre.icons.elements(value)"])]),
                     "position.display": pv.bind(pv.expr("len({view.params.icon}) > 0"))})
    lab = _label("Label", pv.fpos(grow=1), "{view.params.label}", classes="cadre/font/body")
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "row", "alignItems": "center", "style": {"gap": "12px", "overflow": "hidden"}},
        prop_config={"props.style.classes": pv.bind(pv.expr(
            f"if({sel}, 'cadre/nav/item-selected', 'cadre/nav/item cadre/text/active')"))},
        events={"dom": {"onClick": pv.script_handler([
            "if self.view.params.path:",
            "\tsystem.perspective.navigate(self.view.params.path)",
            f"system.perspective.closeDock('{NAV_DOCK}')"])}},
        children=[ic, lab, _badges_embed(pv.fpos(basis="120px", shrink=0))])
    params = {"label": "", "path": "", "icon": "", "counts": dict(NO_COUNTS)}   # counts: F046
    return pv.view(root, params=params, param_dirs={k: "input" for k in params},
                   size={"width": 304, "height": 48})


def nav_menu() -> dict:
    def rep(name, expr, counted=False):
        # the page items carry their node's counts (F046), polled as the top bar polls its own
        cfg = (pv.bind(pv.expr("if(toMillis(now(2000)) > 0, '', '')"), [pv.script_transform([
            "return cadre.hmi.nav_items(self.session)"])]) if counted else pv.bind(pv.expr(expr)))
        return pv.node("ia.display.flex-repeater", name, pv.fpos(shrink=0), {
            "path": "Framework/NavItem", "direction": "column", "useDefaultViewHeight": True,
            "useDefaultViewWidth": False, "elementPosition": {"basis": "48px", "shrink": 0},
            "style": {"gap": "4px"}},
            prop_config={"props.instances": cfg})
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "column", "style": {"padding": "8px", "overflow": "hidden"}},
        prop_config={"props.style.classes": root_classes("cadre/surface/menu")},
        children=[_panel_header("Header", "Menu", f"system.perspective.closeDock('{NAV_DOCK}')"),
                  rep("Items", "{session.custom.nav.items}", counted=True),
                  pv.node("ia.container.flex", "Spacer", pv.fpos(grow=1), {}),
                  pv.node("ia.container.flex", "Divider", pv.fpos(basis="9px", shrink=0),
                          {"style": {"classes": "cadre/divider/bottom", "marginBottom": "8px"}}),
                  rep("Footer", "{session.custom.nav.footer}")])
    return pv.view(root, size={"width": 320, "height": 800})


# The faceplate of each device kind; `instrument` is the kind a readout or an instrument field selects.
FACEPLATE_VIEW = {"pump": "Faceplate/Pump", "motor": "Faceplate/Pump", "fan": "Faceplate/Pump",
                  "valve": "Faceplate/Valve", "analogvalve": "Faceplate/Valve", "damper": "Faceplate/Valve",
                  "tank": "Faceplate/Tank", "instrument": "Faceplate/Instrument", "readout": "Faceplate/Instrument",
                  "instrument-field": "Faceplate/Instrument", "controller": "Faceplate/Controller",
                  "indicator": "Faceplate/Input", "sequence": "Faceplate/Sequence",
                  # the generator has the asm faceplate only (COB-158): either style opens it
                  "generator": "Faceplate/ASM/Generator"}
FACEPLATE_OF_KIND = ("case(coalesce({session.custom.selectedKind}, ''), "
                     + ", ".join(f"'{k}', '{v}'" for k, v in FACEPLATE_VIEW.items()) + ", 'Faceplate/Empty')")
# The faceplate styles (COBD-045). `openbridge`, the faceplates above, is the default. `asm` follows the
# anatomy of the ASMP study (ASMP-REPORT-01 section 5.2): a header strip of the device's state above six
# tabs, Home, Config, Diagnostics, Alarms, Interlock and Info. A kind without an `asm` view keeps its
# `openbridge` faceplate in either style. `cadre.hmi.select_device` writes the selected device's style.
FACEPLATE_STYLES = tuple(scripts.constant("FACEPLATE_STYLES"))
ASM_VIEW = {k: "Faceplate/ASM/" + v.split("/")[-1] for k, v in FACEPLATE_VIEW.items()
            if v in ("Faceplate/Pump", "Faceplate/Valve", "Faceplate/Sequence", "Faceplate/Instrument")}
ASM_VIEW["generator"] = FACEPLATE_VIEW["generator"]
# The asm faceplates `devices_asm` builds (COB-158): the generator's, the sequence's and the instrument's.
ASM_BUILT = ("Faceplate/ASM/Generator", "Faceplate/ASM/Sequence", "Faceplate/ASM/Instrument")
FACEPLATE_OF_SELECTION = ("if(coalesce({session.custom.selectedStyle}, '') = 'asm', "
                          "case(coalesce({session.custom.selectedKind}, ''), "
                          + ", ".join(f"'{k}', '{v}'" for k, v in ASM_VIEW.items()) + f", {FACEPLATE_OF_KIND}), "
                          f"{FACEPLATE_OF_KIND})")


def faceplate_view(kind: str, style: str = "openbridge") -> str:
    """The faceplate a device of `kind` opens in `style` (FACEPLATE_OF_SELECTION); empty for a kind
    without a faceplate."""
    return (ASM_VIEW.get(kind) if style == "asm" else None) or FACEPLATE_VIEW.get(kind, "")


def side_menu() -> dict:
    """The faceplate dock: a header with the device identifier and description and a close
    button, then the faceplate of the selected kind. The dock contract: `selectedDevice` (the
    device tag folder), `selectedKind`, `selectedTitle` and `selectedLabel` in
    `session.custom`, written by `cadre.hmi.select_device` before the dock opens. Kinds map
    to faceplates explicitly, because view paths are case sensitive; `selectedStyle` chooses the
    `asm` faceplate where the kind has one (COBD-045)."""
    titles = pv.node("ia.container.flex", "Titles", pv.fpos(grow=1), {"direction": "column"},
                     children=[_label("Title", pv.fpos(shrink=0), "{session.custom.selectedTitle}",
                                      classes="cadre/font/title cadre/text/active"),
                               _label("Description", pv.fpos(shrink=0), "{session.custom.selectedLabel}",
                                      classes="cadre/font/label cadre/text/neutral")])
    head = pv.node("ia.container.flex", "Header", pv.fpos(basis="64px", shrink=0), {
        "direction": "row", "alignItems": "center",
        "style": {"classes": "cadre/divider/bottom", "padding": "0 8px 0 16px"}},
        children=[titles,
                  _pin_button("Float", ["self.session.custom.faceplateMode = 'popup'",
                                        f"system.perspective.closeDock('{FACEPLATE_DOCK}')", f"{DOCKED} = False",
                                        *open_faceplate()]),
                  _icon_button("Close", "close-google", {"dom": {"onClick": pv.script_handler([
                      f"system.perspective.closeDock('{FACEPLATE_DOCK}')", f"{DOCKED} = False"])}})])
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/menu")},
                   children=[head, _faceplate_body(pv.fpos(grow=1))])
    return pv.view(root, size={"width": 400, "height": 800})


def _faceplate_body(pos: dict) -> dict:
    """The faceplate of the selected device's kind and style, for the dock and for the popup."""
    return pv.node("ia.display.view", "Faceplate", pos, {
        "path": "Faceplate/Empty", "params": {"deviceId": "", "tab": ""}, "useDefaultViewHeight": False,
        "useDefaultViewWidth": False},
        prop_config={"props.path": pv.bind(pv.expr(FACEPLATE_OF_SELECTION)),
                     "props.params.deviceId": pv.bind(pv.expr("{session.custom.selectedDevice}")),
                     # the tab to open on (COB-158): `cadre.hmi.select_device` writes it, empty for a plain click
                     "props.params.tab": pv.bind(pv.expr("coalesce({session.custom.selectedTab}, '')"))})


def _pin_button(name: str, script_lines: list[str]) -> dict:
    """The pin (COBD-045): Float in the dock's header, Dock in the popup's bar. It moves the open
    faceplate and keeps the choice for the session (`session.custom.faceplateMode`), so the next
    device opens in the same place."""
    return pv.node("ia.input.button", name, pv.fpos(basis="72px", shrink=0), {
        "text": name, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "40px"}},
        events=pv.on_action(script_lines))


# The popup's size: the source's faceplate (ASMP-REPORT-01 section 5.2 item 2). A faceplate view is
# 720 px high, so the popup's body scrolls.
POPUP_SIZE = {"width": 450, "height": 600}
FACEPLATE_HEIGHT = 720


def faceplate_popup() -> dict:
    """`Framework/FaceplatePopup`: the faceplate floating (COBD-045). The popup's own title bar carries
    the identifier, the close icon and the drag; beneath it the description and Dock, which puts the
    faceplate back in the right dock, then the faceplate of the selected kind and style."""
    bar = pv.node("ia.container.flex", "Bar", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "alignItems": "center",
        "style": {"classes": "cadre/divider/bottom", "padding": "0 8px 0 16px", "gap": "8px"}},
        children=[_label("Description", pv.fpos(grow=1), "{session.custom.selectedLabel}",
                         classes="cadre/font/label cadre/text/neutral"),
                  _pin_button("Dock", ["self.session.custom.faceplateMode = 'dock'",
                                       f"system.perspective.closePopup('{FACEPLATE_POPUP_ID}')",
                                       f"system.perspective.openDock(id='{FACEPLATE_DOCK}')", f"{DOCKED} = True"])])
    scroll = pv.node("ia.container.flex", "Scroll", pv.fpos(grow=1, basis="0px"), {
        "direction": "column", "style": {"overflow": "auto"}},
        children=[_faceplate_body(pv.fpos(basis=f"{FACEPLATE_HEIGHT}px", shrink=0))])
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/menu")},
                   children=[bar, scroll])
    return pv.view(root, size=dict(POPUP_SIZE))


def _cmd_button(name, text, script_lines, *, selected_expr=None, path=None, member=None):
    """A command button. `path` binds `enabled` to the write path's permission; with `member`, also to
    the member's `write` flag of `custom.dev`, so a member the device model marks read only stays
    disabled for every session."""
    pc = {"props.enabled": _can(path)} if path else {}
    if path and member:
        pc["props.enabled"] = pv.bind(pv.expr(f"{{view.custom.can.{path}}} && {_dv('write', member)}"))
    if path in OWNER_GATED:   # the device's owner lets the path write (COBD-044); always true without modes
        gate = pc["props.enabled"]["binding"]["config"]["expression"] if path and member else f"{{view.custom.can.{path}}}"
        pc["props.enabled"] = pv.bind(pv.expr(f"{gate} && {{view.custom.dev.allowed.{path}}}"))
    if selected_expr:
        pc["props.style.classes"] = pv.bind(pv.expr(
            f"if({selected_expr}, 'cadre/button/selected cadre/font/button', 'cadre/button/normal cadre/font/button')"))
    return pv.node("ia.input.button", name, pv.fpos(grow=1, basis="0px"), {
        "text": text, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "40px"}},
        prop_config=pc or None, events=pv.on_action(script_lines))


def _section_title(name, text, display=None):
    return _label(name, pv.fpos(shrink=0), text=text, classes="cadre/font/overline cadre/text/neutral",
                  style={"marginTop": "12px"}, visible=display)


def _value_row(name, label, expr, *, value_classes="cadre/font/body-active cadre/text/active", extra=None,
               display=None):
    kids = [_label(f"{name}Label", pv.fpos(basis="132px", shrink=0), text=label,
                   classes="cadre/font/label cadre/text/neutral"),
            pv.node("ia.display.label", f"{name}Value", pv.fpos(grow=1), {
                "style": {"classes": value_classes, "whiteSpace": "nowrap"}},
                prop_config={"props.text": pv.bind(pv.expr(expr))})]
    if extra:
        kids.append(extra)
    return pv.node("ia.container.flex", f"{name}Row", pv.fpos(basis="36px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px"}},
        prop_config={"position.display": pv.bind(pv.expr(display))} if display else None, children=kids)


# What a faceplate shows of its device (wiki page 13 section 9). A device carries the members its
# source has and no others, so no faceplate binds a member's tag: each polls
# `cadre.hmi.device_read` once a second into `custom.dev` and derives every row from it. A row, a
# section title, a command group or a tab is shown through `position.display` (GF-08) only while its
# member exists; a present member of bad quality is named on a line, since a polled value draws no
# quality overlay.
_MNT = (scripts.constant("MNT_FORCE_PAIR") + scripts.constant("MNT_FORCE_MODE") + [scripts.constant("MNT_MASK")]
        + [m for m, _label_text in scripts.constant("MNT_FLAGS")])
FACEPLATE_READS = {"pump": ["state", "cmd", "mode", "fault", "speed", "speedSp"] + _MNT,
                   "valve": ["state", "cmd", "mode", "fault"] + _MNT,
                   "tank": ["level"], "instrument": ["value"],
                   "controller": ["value", "sp", "out", "manual", "manOut", "gain", "ti", "td"],
                   "input": ["state"] + _MNT,
                   "sequence": ["step", "stepText", "trigger", "fault"]}
# The pulse members (`cadre.hmi.pulse`, write path W18): a faceplate that reads one draws its button.
PULSE_PATH = scripts.constant("PULSE_PATH")
PULSE_MEMBERS = tuple(scripts.constant("FUNCTION_MEMBERS")[PULSE_PATH])


def _dv(group: str, member: str) -> str:
    """The reference to one member in a group of `custom.dev` (`has`, `value`, `writable`, `write`)."""
    return "{view.custom.dev.%s.%s}" % (group, member.replace("/", "_"))


def ownership_default() -> dict:
    """The ownership part of `custom.dev` for a device without modes, as `cadre.hmi.ownership`
    answers it (COBD-044): not owned, every gated path allowed, no move offered."""
    move = {"offered": False, "value": 0, "name": ""}
    return {"owned": False, "owner": {"name": "", "owner": "", "text": ""},
            "allowed": {p: True for p in OWNER_GATED}, "reason": "",
            "take": dict(move), "release": dict(move), "maintain": dict(move)}


def dev_default(members) -> dict:
    """`custom.dev` before the first poll: what `cadre.hmi.device_read` answers while no device is
    selected (a unit test holds the two together)."""
    defaults = scripts.constant("MEMBER_DEFAULTS")
    keys = [m.replace("/", "_") for m in members]
    return {"has": {k: False for k in keys}, "value": {k: defaults.get(m, 0.0) for k, m in zip(keys, members)},
            "bad": [], "quality": "", "writable": {"force": False, **{k: False for k in keys}},
            "write": {"force": False, **{k: False for k in keys}}, "mnt": False, "force": "",
            "pulses": {k: m for k, m in zip(keys, members) if m in PULSE_MEMBERS}, "config": 0,
            **ownership_default()}


def _dev_cfg(members) -> dict:
    return pv.bind(pv.expr("if(toMillis(now(1000)) > 0, {view.params.deviceId}, '')"), [pv.script_transform([
        f"return cadre.hmi.device_read(self.session, value, {list(members)!r})"])])


def _quality_line() -> dict:
    """The members the device carries whose quality is not good, named in words on every tab. Gate
    G11 fails on this line as it fails on a quality overlay."""
    return _label("Quality", pv.fpos(basis="32px", shrink=0), "{view.custom.dev.quality}",
                  classes="cadre/font/body-active cadre/alert/badge-warning",
                  style={"padding": "4px 8px", "borderRadius": "4px", "whiteSpace": "normal"},
                  visible="len({view.custom.dev.quality}) > 0")


MODE_TEXT = "case({view.custom.dev.value.mode}, 0, 'Auto', 1, 'Manual', 2, 'Local', 'Unknown')"
OWNED = "{view.custom.dev.owned}"
# The moves of ownership a faceplate offers (COBD-044, F005 option B): each writes a mode of the
# device through W2, after a Confirm (F029), and only while `cadre.hmi.ownership` offers it.
MOVES = (("take", "Take control"), ("release", "Release"), ("maintain", "Maintenance"))


def _ownership_rows(mode_writable: str) -> list:
    """Take control, Release and Maintenance for a device with modes. A move sets `custom.pending`
    and writes nothing; the faceplate's Confirm row (`_confirm_row`) makes the one checked write (W2,
    the mode the move offered, which `cadre.hmi.command` refuses again if it is no longer a mode the
    operator may choose)."""
    can_move = f"{{view.custom.can.W2}} && {_dv('write', 'mode')}"
    moves = [pv.node("ia.input.button", f"Move_{key}", pv.fpos(grow=1, basis="0px"), {
        "text": text, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "40px"}},
        prop_config={"position.display": pv.bind(pv.expr(f"{{view.custom.dev.{key}.offered}}")),
                     "props.enabled": pv.bind(pv.expr(can_move))},
        events=pv.on_action([
            f"m = self.view.custom.dev.{key}",
            _pend("W2", "mode", "m.value", f"'{text}: ' + m.name + '?'")]))
             for key, text in MOVES]
    group = pv.node("ia.container.flex", "Ownership", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "style": {"gap": "8px"}},
        prop_config={"position.display": pv.bind(pv.expr(f"{mode_writable} && {OWNED}"))}, children=moves)
    return [group]
# A numeric entry field's `spinner` is an object, `spinner.enabled` defaulting to true
# (IGW ia.input.numeric-entry-field). The setpoint fields carried a bare `true` until 2026-10-08,
# which drew no spinner (measured); they keep that look explicitly.
SPINNER = {"enabled": False}

# Faceplate tabs (COB-076, COB-PLAN-01 Table 5): the tab row of the alerts page (`view.custom.tab`,
# the selected and flat button classes) beneath the dock's header, one pane per tab shown with
# `position.display` (GF-08). The first tab is the default, and a new device resets to it.
FACEPLATE_TABS = {"pump": [("control", "Control"), ("alarms", "Alarms"), ("interlocks", "Interlocks"),
                           ("maintenance", "Maintenance")],
                  "valve": [("control", "Control"), ("alarms", "Alarms"), ("interlocks", "Interlocks"),
                            ("maintenance", "Maintenance")],
                  "tank": [("values", "Values"), ("trend", "Trend"), ("alarms", "Alarms")],
                  "instrument": [("values", "Values"), ("trend", "Trend"), ("alarms", "Alarms")],
                  "controller": [("control", "Control"), ("trend", "Trend"), ("tuning", "Tuning"), ("alarms", "Alarms")],
                  "input": [("status", "Status"), ("maintenance", "Maintenance"), ("alarms", "Alarms")],
                  "sequence": [("status", "Status"), ("trend", "Trend"), ("alarms", "Alarms")]}
# The member each trend draws (COB-064): the instrument's value, the tank's level. The controller's trend
# draws three members and has its own pane; the sequence's draws its step number as a stepped line.
TREND_MEMBER = {"instrument": "value", "tank": "level"}
CONTROLLER_TREND = ("value", "sp", "out")
SEQUENCE_TREND = ("step",)
# The faceplates whose Trend tab follows the trend index (`cadre.hmi.trended`), each with the members
# it may draw: the tab shows only where the index lists one of them for the device.
TREND_INDEXED = {"controller": CONTROLLER_TREND, "sequence": SEQUENCE_TREND}
TUNING = ("gain", "ti", "td")
# The tabs a device may lack, each with the condition that shows it: an `ilk` folder, a row of the
# Maintenance tab (`dev.mnt`: a whole force, the object error mask or a flag; half a force is no row;
# `dev.config`: a configuration member, F010),
# the trended member, a tuning member. `expected_tabs` states the same rule over a device's members.
TAB_SHOWN = {"pump": {"interlocks": "{view.custom.ilk.present}", "maintenance": "{view.custom.dev.mnt} || {view.custom.dev.config} > 0"},
             "valve": {"interlocks": "{view.custom.ilk.present}", "maintenance": "{view.custom.dev.mnt} || {view.custom.dev.config} > 0"},
             "tank": {"trend": _dv("has", "level")}, "instrument": {"trend": _dv("has", "value")},
             "controller": {"trend": " || ".join("{view.custom.trend.%s}" % m for m in CONTROLLER_TREND),
                            "tuning": " || ".join(_dv("has", m) for m in TUNING)},
             "input": {"maintenance": "{view.custom.dev.mnt} || {view.custom.dev.config} > 0"},
             "sequence": {"trend": " || ".join("{view.custom.trend.%s}" % m for m in SEQUENCE_TREND)}}
# The tabs of an `asm` faceplate (COBD-045), the same for every kind that has one. Config holds the
# maintenance functions and shows by their rule; Interlock shows for a device with interlocks.
ASM_TABS = [("home", "Home"), ("config", "Config"), ("diagnostics", "Diagnostics"), ("alarms", "Alarms"),
            ("interlocks", "Interlock"), ("info", "Info")]
ASM_SHOWN = {"interlocks": "{view.custom.ilk.present}", "config": "{view.custom.dev.mnt} || {view.custom.dev.config} > 0"}
# Members that also show the Config tab of an asm faceplate, by faceplate: a generator's service data (COB-158,
# `cadre.hmi.CONFIG_SERVICE`).
ASM_CONFIG_EXTRA = {"generator": tuple(scripts.constant("CONFIG_SERVICE"))}


def trend_by_index(kind: str) -> bool:
    """The Trend tab of the faceplate of a device of `kind` follows the trend index (TREND_INDEXED),
    not a member of the device: without a device model's `trend` list the tag model decides it."""
    return FACEPLATE_VIEW.get(kind, "").split("/")[-1].lower() in TREND_INDEXED


def expected_tabs(kind: str, members, trend=(), style: str = "openbridge") -> list[str]:
    """The tab labels the faceplate of a device of `kind` shows in `style`, from the members the device
    carries and the members its trend draws: the rule of TAB_SHOWN (ASM_SHOWN for an `asm` faceplate),
    for the faceplate sweep (G11), which compares it with the glass. Empty for a kind without a
    faceplate."""
    view = faceplate_view(kind, style)
    key = view.split("/")[-1].lower()
    have = set(members)
    forces = (scripts.constant("MNT_FORCE_PAIR"), scripts.constant("MNT_FORCE_MODE"))
    rows = {scripts.constant("MNT_MASK")} | {m for m, _text in scripts.constant("MNT_FLAGS")}
    needs = {"interlocks": any(m.startswith("ilk/") for m in have),
             "maintenance": bool(have & rows) or any(set(pair) <= have for pair in forces)
             or any(m.startswith(CONFIG_PREFIX) for m in have),
             "tuning": bool(have & set(TUNING)),
             "trend": bool(set(trend) & set(TREND_INDEXED[key])) if key in TREND_INDEXED
             else TREND_MEMBER.get(key) in have}
    needs["config"] = needs["maintenance"] or bool(have & set(ASM_CONFIG_EXTRA.get(key, ())))
    tabs = ASM_TABS if view in ASM_VIEW.values() else FACEPLATE_TABS.get(key, [])
    return [label for k, label in tabs if needs.get(k, True)]


# The device's alarms: every alarm whose source matches one of the device's patterns
# (`cadre.hmi.device_sources`: the folder pattern measured as GF-34, or the source tags a device model
# names), in the states the list shows. The stock table takes the patterns separated by commas (IGW
# ia.display.alarmstatustable, `filters.active.conditions.source`; measured GF-52), so the faceplate
# hands `Faceplate/Alarms` that text. Polled like the top bar's summary.
DEVICE_SOURCE_CFG = pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
    "return ','.join(cadre.hmi.device_sources(self.session, value))"])])
ALARM_COUNT_CFG = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {view.params.deviceId}, '')"), [pv.script_transform([
    "return cadre.hmi.alarm_count(self.session.custom.alarmScope, cadre.hmi.device_sources(self.session, value))"])])


def _tab_row(tabs, shown: dict | None = None, wrap: bool = False) -> dict:
    """The tab row. With `wrap` (the six tabs of an `asm` faceplate) the tabs take two lines of three,
    so that the panes keep the width of the `openbridge` faceplate in the 400 px dock."""
    kids = []
    for key, label in tabs:
        pc = {"props.style.classes": pv.bind(pv.expr(
            f"if({{view.custom.tab}} = '{key}', 'cadre/button/selected cadre/font/button', "
            "'cadre/button/flat cadre/font/button')"))}
        if key in (shown or {}):   # a tab the device may lack (TAB_SHOWN)
            pc["position.display"] = pv.bind(pv.expr(shown[key]))
        if key == "alarms":   # the count is on the tab, so it shows without switching (COB-PLAN-01 6.2 item 5)
            pc["props.text"] = pv.bind(pv.expr(
                f"'{label}' + if({{view.custom.alarmCount}} > 0, ' (' + toStr({{view.custom.alarmCount}}) + ')', '')"))
        if key == "interlocks":   # only for a device with interlocks; the count of conditions not met
            pc["props.text"] = pv.bind(pv.expr(   # the conditions that hold the device: not met, or latched
                f"'{label}' + if({{view.custom.ilk.holding}} > 0, ' (' + toStr({{view.custom.ilk.holding}}) + ')', '')"))
        kids.append(pv.node("ia.input.button", f"Tab_{key}",
                            pv.fpos(grow=1, basis="112px", shrink=0) if wrap else pv.fpos(grow=1, basis="0px"), {
            "text": label, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "40px"}},
            prop_config=pc, events=pv.on_action([f"self.view.custom.tab = '{key}'"])))
    return pv.node("ia.container.flex", "Tabs", pv.fpos(basis="92px" if wrap else "48px", shrink=0), {
        "direction": "row", "alignItems": "center", **({"wrap": "wrap", "alignContent": "center"} if wrap else {}),
        "style": {"classes": "cadre/divider/bottom", "gap": "4px", "marginBottom": "4px"}}, children=kids)


def _pane(key: str, children: list, scroll: bool = False) -> dict:
    """A tab's pane, shown by `{view.custom.tab}`. With `scroll` the pane scrolls where its rows are more than
    the faceplate's height holds (the Home tab of the generator and of the instrument, COB-158)."""
    return pv.node("ia.container.flex", f"Pane_{key}", pv.fpos(grow=1, basis="0px"), {
        "direction": "column", "style": {"gap": "4px", **({"overflow": "auto"} if scroll else {})}},
        prop_config={"position.display": pv.bind(pv.expr(f"{{view.custom.tab}} = '{key}'"))},
        children=children)


def _alarms_pane() -> dict:
    """The Alarms tab: `Faceplate/Alarms` at the full height of the pane, given the device's
    source patterns, separated by commas. The parent's view is the stock table; a child built with
    `--render module` overrides that one view with the module's alarm list (COB-078)."""
    return _pane("alarms", [pv.node("ia.display.view", "AlarmList", pv.fpos(grow=1, basis="0px"), {
        "path": "Faceplate/Alarms", "params": {"source": "", "deviceId": ""},
        "useDefaultViewHeight": False, "useDefaultViewWidth": False},
        prop_config={"props.params.source": pv.bind(pv.expr("{view.custom.source}")),
                     "props.params.deviceId": pv.bind(pv.expr("{view.params.deviceId}"))})])


def _asm_header(kind: str) -> dict:
    """The header strip of an `asm` faceplate (COBD-045): the device's state, its mode or owner, and,
    while they hold, the words Fault, Interlocked and the count of its alarms, each only where the
    device carries the member."""
    state = "if({view.custom.dev.value.state}, " + (
        "'Open', 'Closed')" if kind == "valve" else "'Running', 'Stopped')")
    badge = {"padding": "2px 8px", "borderRadius": "4px"}
    alarms = "{view.custom.alarmCount}"
    words = [("HeadState", state, "cadre/font/body-active cadre/text/active", _dv("has", "state")),
             ("HeadMode", f"if({OWNED}, {{view.custom.dev.owner.name}}, {MODE_TEXT})",
              "cadre/font/body cadre/text/neutral", _dv("has", "mode")),
             ("HeadFault", "'Fault'", "cadre/font/body-active cadre/alert/badge-alarm",
              f"{_dv('has', 'fault')} && {_dv('value', 'fault')}"),
             ("HeadInterlock", "if({view.custom.ilk.interlocked}, 'Interlocked', 'Not permitted')",
              "cadre/font/body-active cadre/alert/badge-warning", ILK_HELD),
             ("HeadAlarms", f"toStr({alarms}) + if({alarms} = 1, ' alarm', ' alarms')",
              "cadre/font/body-active cadre/alert/badge-alarm", f"{alarms} > 0")]
    return pv.node("ia.container.flex", "Header", pv.fpos(basis="40px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"classes": "cadre/divider/bottom", "gap": "8px"}},
        children=[_label(name, pv.fpos(shrink=0), expr, classes=classes, style=badge, visible=shown)
                  for name, expr, classes, shown in words])


# The members a Diagnostics tab lists, in three groups like the source's status, command and feedback
# sections (ASMP-REPORT-01 section 5.2 item 2): each row the member's name in the device folder and its
# raw value, shown only where the device carries the member.
DIAGNOSTIC_GROUPS = (("DiagStatus", "STATUS", ("state", "mode", "fault", "speed")),
                     ("DiagCommand", "COMMAND", ("cmd", "speedSp")),
                     ("DiagMaintenance", "MAINTENANCE", tuple(_MNT)))


def _diagnostics_pane(kind: str) -> dict:
    reads = FACEPLATE_READS[kind]
    rows = []
    for name, title, members in DIAGNOSTIC_GROUPS:
        members = [m for m in members if m in reads]
        if not members:
            continue
        rows.append(_section_title(f"{name}Title", title, display=" || ".join(_dv("has", m) for m in members)))
        rows += [_value_row(f"{name}{i}", m, f"toStr({_dv('value', m)})", display=_dv("has", m))
                 for i, m in enumerate(members)]
    return _pane("diagnostics", rows)


def _info_pane() -> dict:
    """The Info tab: who the device is (the dock contract of `cadre.hmi.select_device`), its owner and
    the source patterns of its alarms."""
    rows = [_section_title("InfoTitle", "IDENTITY"),
            _value_row("InfoName", "Name", "{session.custom.selectedTitle}"),
            _value_row("InfoLabel", "Description", "{session.custom.selectedLabel}"),
            _value_row("InfoKind", "Kind", "{session.custom.selectedKind}"),
            _value_row("InfoFolder", "Tag folder", "{view.params.deviceId}"),
            _value_row("InfoOwner", "Owner", f"if({OWNED}, {{view.custom.dev.owner.text}}, 'Not gated by mode')"),
            _section_title("InfoSourceTitle", "ALARM SOURCES"),
            _label("InfoSources", pv.fpos(shrink=0), "replace({view.custom.source}, ',', ', ')",
                   classes="cadre/font/body cadre/text/active", style={"whiteSpace": "normal"})]
    return _pane("info", rows)


def _tab_lines(keys: list, requested: str) -> list:
    """The lines that set the faceplate's tab from the tab it was asked to open on (`params.tab`, COB-158): the
    tab asked, when it is one of the faceplate's tabs, else the first. A tab the device does not show is
    refused before it reaches the view (`cadre.hmi.select_device`, `tab_shown`)."""
    return [f"self.custom.tab = '{keys[0]}'", f"want = {requested}", f"if want in {tuple(keys)!r}:",
            "	self.custom.tab = want"]


def _tabbed(kind: str, control_rows: list, custom: dict, custom_cfg: dict, panes: dict | None = None,
            style: str = "openbridge", *, reads: list | None = None, header: dict | None = None,
            config_rows: list | None = None, diagnostics: dict | None = None, shown: dict | None = None,
            scroll_home: bool = False) -> dict:
    """A device faceplate: the tab row, the quality line and one pane per tab of FACEPLATE_TABS. The
    first pane holds `control_rows`; the Alarms, Interlocks, Maintenance and single member Trend
    panes are built here, and `panes` gives any other by its key. In the `asm` style (COBD-045) the
    header strip comes first and the tabs are ASM_TABS: Config holds the maintenance functions, and
    Diagnostics and Info are built here."""
    asm = style == "asm"
    tabs = ASM_TABS if asm else FACEPLATE_TABS[kind]
    keys = [k for k, _ in tabs]
    ilk = "interlocks" in keys
    built = {keys[0]: _pane(keys[0], ([_held_line()] if ilk else []) + control_rows, scroll_home),
             "alarms": _alarms_pane()}
    if ilk:
        built["interlocks"] = _interlocks_pane()
    if "maintenance" in keys or asm:
        built["config" if asm else "maintenance"] = _maintenance_pane("config" if asm else "maintenance",
                                                                      config_rows)
    if asm:
        built.update({"diagnostics": diagnostics or _diagnostics_pane(kind), "info": _info_pane()})
    trend = "trend" in keys and kind in TREND_MEMBER
    if trend:
        built["trend"] = _trend_pane(TREND_MEMBER[kind])
    built.update(panes or {})
    head = [header or _asm_header(kind)] if asm else []
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column",
                                                      "style": {"padding": "4px 16px 16px 16px", "gap": "4px"}},
                   prop_config={"props.style.classes": root_classes()},
                   children=head + [_tab_row(tabs, (shown or ASM_SHOWN) if asm else TAB_SHOWN.get(kind), wrap=asm),
                                    _quality_line(), _confirm_row()] + [built[k] for k in keys])
    reads = reads or FACEPLATE_READS[kind]
    custom = {**custom, "tab": tabs[0][0], "source": "", "alarmCount": 0, "can": dict(CAN_DEFAULT), "message": "",
              "dev": dev_default(reads), "pending": dict(PENDING_DEFAULT)}
    custom_cfg = {**custom_cfg, "custom.source": DEVICE_SOURCE_CFG, "custom.alarmCount": ALARM_COUNT_CFG,
                  "custom.can": CAN_CFG, "custom.dev": _dev_cfg(reads)}
    # a confirmation never outlives its device; the tab asked for (`params.tab`) opens on a new device
    reset = _tab_lines(keys, "self.params.tab") + ["self.custom.message = ''",
                                                   f"self.custom.pending = {PENDING_DEFAULT!r}"]
    if "limitRows" in custom:   # a faceplate that lists limits lists their delays beneath them (F028)
        custom["delayRows"] = []
        custom_cfg["custom.delayRows"] = DELAY_ROWS_CFG
    if ilk:
        custom.update({"ilk": dict(ILK_DEFAULT), "ilkRows": [], "refused": False})
        custom_cfg.update({"custom.ilk": ILK_SUMMARY_CFG, "custom.ilkRows": ILK_ROWS_CFG})
        reset.append("self.custom.refused = False")
    if trend:   # `tags` references this list (pv.tag_history; G7 checks the default is a list)
        custom.update({"hours": 1, "historyTags": [{"path": "", "alias": "value"}]})
        custom_cfg["custom.historyTags"] = pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
            f"return cadre.hmi.history_tags(value, '{TREND_MEMBER[kind]}')"])])
    # `tab` is the tab to open on (contract 2.1 of COB-158 to COB-160): the tab asked for, else the first
    return pv.view(root, params={"deviceId": "", "tab": ""}, param_dirs={"deviceId": "input", "tab": "input"},
                   param_change={"deviceId": reset, "tab": _tab_lines(keys, "currentValue.value")},
                   size={"width": 400, "height": 720}, custom=custom, custom_config=custom_cfg)


def faceplate_alarms() -> dict:
    """`Faceplate/Alarms`, stock: the alarm status table narrowed to the device's alarms by source
    path (`filters.active.conditions.source`, IGW component page; measured on the glass, GF-34;
    several patterns separated by commas, GF-52), every priority shown, no text filter."""
    from . import acks   # Ack selected and Ack all under the table (L5)
    tbl = pv.node("ia.display.alarmstatustable", "Table", pv.fpos(grow=1, basis="0px"), acks.stock_props(),
                  prop_config={"props.filters.active.conditions.source": pv.bind(pv.expr("{view.params.source}")),
                               "props.filters.active.priorities.diagnostic": pv.bind(pv.expr("true")),
                               **_table_actions()})
    bar = acks.bar(selections=["selected"], can_selected="W7", can_all="W7", path_selected="W7", path_all="W7")
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column"},
                   prop_config={"props.style.classes": root_classes()}, children=[tbl] + bar)
    return pv.view(root, params={"source": "", "deviceId": ""},
                   param_dirs={"source": "input", "deviceId": "input"}, size={"width": 368, "height": 560},
                   custom={"can": dict(CAN_DEFAULT), **acks.custom("selected")},
                   custom_config={"custom.can": CAN_CFG, **acks.stock_config("Table")})


def faceplate_alarms_module() -> dict:
    """`Faceplate/Alarms` for a child built with `--render module`: OpenBridge's alert list over the
    device's alarms (a pattern that matches nothing until the device is known, never the whole
    scope). Display only (COBD-025): alarm actions are taken on the alerts page, in the top bar's
    alarm menu and with the top bar's ACK. Every record carries `noAck`, so a row draws OpenBridge's
    no-acknowledgement icon where it would offer ACK (the pin's own rule), and no list carries an
    acknowledge event. OpenBridge's mode `all` draws the active alerts only, and its mode
    `rectified` the cleared ones, so a second list shows the cleared alarms still unacknowledged:
    no alarm the stock table lists is hidden."""
    # an empty source would mean the whole scope to alarm_list: use the no-match pattern instead
    # (cadre.hmi.NO_MATCH)
    poll = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, if(len(coalesce({view.params.source}, '')) > 0, "
                           "{view.params.source}, 'prov:none:/tag:none/none'), '')"), [pv.script_transform([
                               "alerts = cadre.hmi.alarm_list(self.session.custom.alarmScope, value, no_ack=True, "
                               "session=self.session)",
                               "return {'alerts': alerts, 'rectified': len([a for a in alerts if a['active'] is not True])}"])])

    from . import acks, screen   # Ack selected and Ack all under the lists (L5); the ticks need module 0.4.2
    ticks = "selectedIds" in screen.module_props("cadre.ob.alertlist")

    def lst(name, mode, pos, display=None, selection=None):
        # small: status, time and the action column; the large layout adds a "Tag ID" column that
        # shows the alert id (an event UUID here) and needs about 620 px
        pc = {"props.alerts": pv.bind(pv.expr("{view.custom.alarms.alerts}"))}
        props = {"alerts": [], "selectedMode": mode, "showTime": True, "small": True}
        if display:
            pc["position.display"] = pv.bind(pv.expr(display))
        if ticks and selection:
            props["selectable"] = True
            pc["props.selectedIds"] = pv.bind(pv.prop(f"view.custom.{selection}", True))
        return pv.node("cadre.ob.alertlist", name, pos, props, prop_config=pc)
    has = "{view.custom.alarms.rectified} > 0"
    title = _label("RectifiedTitle", pv.fpos(basis="28px", shrink=0), text="CLEARED, NOT ACKNOWLEDGED",
                   classes="cadre/font/overline cadre/text/neutral", visible=has)
    selections = ["selected", "selectedR"] if ticks else []
    bar = acks.bar(selections=selections, can_selected="W8", can_all="W9", path_selected="W8", path_all="W9",
                   selectable=ticks)
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"gap": "4px"}},
                   prop_config={"props.style.classes": root_classes()}, children=[
                       lst("List", "all", pv.fpos(grow=2, basis="0px"), selection="selected"), title,
                       lst("Rectified", "rectified", pv.fpos(grow=1, basis="0px"), has, selection="selectedR")] + bar)
    return pv.view(root, params={"source": "", "deviceId": ""},
                   param_dirs={"source": "input", "deviceId": "input"}, size={"width": 368, "height": 560},
                   custom={"alarms": {"alerts": [], "rectified": 0}, "can": dict(CAN_DEFAULT),
                           **acks.custom(*selections)},
                   custom_config={"custom.alarms": poll, "custom.can": CAN_CFG,
                                  "custom.shown": pv.bind(pv.expr("{view.custom.alarms.alerts}")),
                                  "custom.unacked": acks.unacked_binding("{view.custom.alarms.alerts}")})


def alert_menu_module() -> dict:
    """`Framework/AlertMenu` for a child built with `--render module` (COB-078, WP4): OpenBridge's
    small alert page over the project scope. ACK and ACK visible acknowledge with the session's
    user; a row opens the device's faceplate through the generated device index. The small page
    has no mode for cleared alerts, so a second list shows the cleared alarms still
    unacknowledged. The top bar's banner and count stay stock (`alarm_summary`), so a module fault
    never hides an alarm."""
    # a session whose user may not acknowledge (COBD-024) gets records marked noAck: no row offers ACK
    # and ACK visible stays disabled (the pin's own rule, page 13 section 5); the scripts refuse anyway
    poll = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, '', '')"), [pv.script_transform([
        "alerts = cadre.hmi.alarm_list(self.session.custom.alarmScope, value, "
        "no_ack=not cadre.hmi.allowed(self.session, 'W8'), session=self.session)",
        "return {'alerts': alerts, 'rectified': len([a for a in alerts if a['active'] is not True])}"])])
    from . import acks, screen   # Ack selected and Ack all under the panel (L5); the ticks need module 0.4.2
    ticks = "selectedIds" in screen.module_props("cadre.ob.alertpanel")
    ack = pv.script_handler(["cadre.hmi.ack_event(event, self.session, path='W8')"])
    ack_visible = pv.script_handler(["cadre.hmi.ack_event(event, self.session, path='W9')"])
    row = pv.script_handler(["if cadre.hmi.select_alarm_device(self.session, event):",
                             "	system.perspective.closePopup('alertMenu')",
                             *open_faceplate("\t")])
    has = "{view.custom.alarms.rectified} > 0"
    selections = ["selected", "selectedR"] if ticks else []
    bar = acks.bar(selections=selections, can_selected="W8", can_all="W9", path_selected="W8", path_all="W9",
                   selectable=ticks)
    panel = pv.node("cadre.ob.alertpanel", "Panel", pv.fpos(grow=2, basis="0px"),
                    {"alerts": [], "selectedMode": "all", "showTime": True, **({"selectable": True} if ticks else {})},
                    prop_config={"props.alerts": pv.bind(pv.expr("{view.custom.alarms.alerts}")),
                                 **({"props.selectedIds": pv.bind(pv.prop("view.custom.selected", True))}
                                    if ticks else {})},
                    events={"component": {"onAckClick": ack, "onAckAllClick": ack_visible, "onRowClick": row}})
    title = _label("RectifiedTitle", pv.fpos(basis="24px", shrink=0), text="CLEARED, NOT ACKNOWLEDGED",
                   classes="cadre/font/overline cadre/text/neutral", visible=has)
    rect = pv.node("cadre.ob.alertlist", "Rectified", pv.fpos(grow=1, basis="0px"),
                   {"alerts": [], "selectedMode": "rectified", "showTime": True, "small": True,
                    **({"selectable": True} if ticks else {})},
                   prop_config={"props.alerts": pv.bind(pv.expr("{view.custom.alarms.alerts}")),
                                "position.display": pv.bind(pv.expr(has)),
                                **({"props.selectedIds": pv.bind(pv.prop("view.custom.selectedR", True))}
                                   if ticks else {})},
                   events={"component": {"onAckClick": ack, "onRowClick": row}})
    go = pv.node("ia.input.button", "AllAlerts", pv.fpos(basis="40px", shrink=0), {
        "text": "Alerts ›", "style": {"classes": "cadre/button/flat cadre/font/button"}},
        events=pv.on_action(["system.perspective.closePopup('alertMenu')",
                             "system.perspective.navigate('/alerts')"]))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column",
                                                      "style": {"padding": "8px", "gap": "8px", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/card")},
                   children=[_panel_header("Header", "Alerts", "system.perspective.closePopup('alertMenu')"),
                             panel, title, rect] + bar + [go])
    return pv.view(root, size={"width": 640, "height": 468},
                   custom={"alarms": {"alerts": [], "rectified": 0}, "can": dict(CAN_DEFAULT), **acks.custom(*selections)},
                   custom_config={"custom.alarms": poll, "custom.can": CAN_CFG,
                                  "custom.shown": pv.bind(pv.expr("{view.custom.alarms.alerts}")),
                                  "custom.unacked": acks.unacked_binding("{view.custom.alarms.alerts}")})


def faceplate_tank_tile_module() -> dict:
    """`Faceplate/TankTile` for a child built with `--render module`: the module's tank, as the
    diagrams draw it."""
    tank = pv.node("cadre.ob.tank", "Tank", pv.fpos(grow=1, basis="0px"), {"value": 0, "max": 100},
                   prop_config={"props.value": pv.bind(pv.expr("{view.custom.tile.value}")),
                                "props.max": pv.bind(pv.expr("{view.custom.tile.max}")),
                                "props.trend": pv.bind(pv.expr("{view.custom.tile.trend}"))})
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column"},
                   prop_config={"props.style.classes": root_classes()}, children=[tank])
    poll = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {view.params.deviceId}, '')"), [pv.script_transform([
        "return cadre.hmi.tank_tile(value)"])])
    return pv.view(root, params={"level": 0, "deviceId": ""}, param_dirs={"level": "input", "deviceId": "input"},
                   size={"width": 180, "height": 220}, custom={"tile": {"value": 0, "max": 100, "trend": "stable"}},
                   custom_config={"custom.tile": poll})


def module_overrides() -> dict[str, dict]:
    """The views a child built with `--render module` writes over the parent's (wiki page 06
    section 6 rule 3): only those that carry a module component, so the parent stays stock."""
    return {"Faceplate/Alarms": faceplate_alarms_module(), "Framework/AlertMenu": alert_menu_module(),
            "Faceplate/TankTile": faceplate_tank_tile_module()}


# The module's wrapper centres its element, which suits a symbol; an alarm list fills its component
# box, top aligned. The rule lives in the module's own stylesheet since version 0.2.1 (COB-082); the
# parent's stylesheet carried it until then.


# Interlocks (COB-079, provisional; COB-PLAN-01 WP5). The Interlocks tab of a pump or valve faceplate
# lists the device's conditions; the tab and the Control tab's line appear only for a device whose tag
# folder carries `ilk` (`cadre.hmi.interlock_summary`, `interlock_rows`), so no faceplate binds a
# missing tag. Bypass is shown, never written: writing it waits for command security (COB-063).
# With the session, the summary and each row say whether the reset and the bypass may be written at all
# (`resetWritable`, `writable`: the device model's `write` list), which the two controls follow beside
# the permission of their write paths.
ILK_SUMMARY_CFG = pv.bind(pv.expr("if(toMillis(now(1000)) > 0, {view.params.deviceId}, '')"), [pv.script_transform([
    "return cadre.hmi.interlock_summary(value, self.session)"])])
ILK_ROWS_CFG = pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
    "return cadre.hmi.interlock_rows(value, self.session)"])])
ILK_DEFAULT = {"present": False, "permitted": True, "interlocked": False, "bypassed": False, "unsatisfied": 0,
               "resetRequired": False, "holding": 0, "resetWritable": False}
ILK_HELD = "{view.custom.ilk.present} && (!{view.custom.ilk.permitted} || {view.custom.ilk.interlocked})"


ILK_ROW_MEMBERS = ("kind", "text", "action", "ok", "liveText", "requiredText", "bypassed", "bypassable", "latched",
                   "resetRequired")


def faceplate_interlock_row() -> dict:
    """`Faceplate/InterlockRow`: one condition of `<device>/ilk/<cid>/`. A condition that holds the
    device (not met and not bypassed, or latched and waiting for its reset) is highlighted with its
    required action (ASM guideline 2.7: the live value against the required value, and what to do)."""
    refs = {"0": "{view.params.deviceId}", "1": "{view.params.cid}"}
    cfg = {f"custom.{m}": pv.bind(pv.tag_indirect("{0}/ilk/{1}/" + m, refs)) for m in ILK_ROW_MEMBERS}
    held = "(!{view.custom.ok} && !{view.custom.bypassed}) || {view.custom.resetRequired}"
    lamp = pv.node("ia.display.label", "State", pv.fpos(basis="88px", shrink=0), {
        "textStyle": {"textAlign": "center"},
        "style": {"classes": "cadre/font/label cadre/text/neutral", "borderRadius": "4px", "justifyContent": "center"}},
        prop_config={"props.text": pv.bind(pv.expr(
            "if({view.custom.bypassed}, 'Bypassed', if({view.custom.resetRequired}, 'Latched', "
            "if({view.custom.ok}, 'Met', 'Not met')))")),
            "props.style.classes": pv.bind(pv.expr(
                f"if({held}, 'cadre/font/label cadre/alert/badge-warning', if({{view.custom.bypassed}}, "
                "'cadre/font/label cadre/alert/badge-caution', 'cadre/font/label cadre/text/neutral'))"))})
    head = pv.node("ia.container.flex", "Head", pv.fpos(basis="28px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px"}}, children=[
        lamp,
        _label("Kind", pv.fpos(basis="72px", shrink=0), "if({view.custom.kind} = 'trip', 'Trip', 'Permissive')",
               classes="cadre/font/label cadre/text/neutral"),
        _label("Text", pv.fpos(grow=1), "{view.custom.text}", classes="cadre/font/body-active cadre/text/active",
               style={"overflow": "hidden", "textOverflow": "ellipsis"})])
    values = pv.node("ia.container.flex", "ValuesRow", pv.fpos(basis="28px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px"}}, children=[
        _label("Values", pv.fpos(grow=1),
               "'Live: ' + {view.custom.liveText} + '    Required: ' + {view.custom.requiredText}",
               classes="cadre/font/body cadre/text/active", style={"overflow": "hidden", "textOverflow": "ellipsis"}),
        # W10, a maintenance action (COBD-024: the admin role): only a bypassable condition shows it
        pv.node("ia.input.button", "Bypass", pv.fpos(basis="96px", shrink=0), {
            "text": "Bypass", "style": {"classes": "cadre/button/flat cadre/font/button", "height": "28px"}},
            prop_config={"position.display": pv.bind(pv.expr("{view.custom.bypassable} && !{view.custom.pending}")),
                         "props.enabled": pv.bind(pv.expr("{view.custom.can.W10} && {view.params.writable}")),
                         "props.text": pv.bind(pv.expr("if({view.custom.bypassed}, 'Unbypass', 'Bypass')"))},
            events=pv.on_action(["self.view.custom.pending = True"])),
        # F029: the bypass, or its removal, waits for this Confirm
        pv.node("ia.input.button", "BypassYes", pv.fpos(basis="88px", shrink=0), {
            "text": CONFIRM, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "28px"}},
            prop_config={"position.display": pv.bind(pv.expr("{view.custom.pending}")),
                         "props.enabled": pv.bind(pv.expr("{view.custom.can.W10} && {view.params.writable}"))},
            events=pv.on_action([
                "msg = cadre.hmi.bypass(self.session, self.view.params.deviceId, "
                "self.view.params.cid, not self.view.custom.bypassed)",
                "self.view.custom.pending = False",
                "self.view.custom.message = msg"])),
        pv.node("ia.input.button", "BypassNo", pv.fpos(basis="88px", shrink=0), {
            "text": CANCEL, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "28px"}},
            prop_config={"position.display": pv.bind(pv.expr("{view.custom.pending}"))},
            events=pv.on_action(["self.view.custom.pending = False"]))])
    action = _label("Action", pv.fpos(basis="44px", shrink=0),   # a refused bypass shows here (COB-063)
                    "if(len({view.custom.message}) > 0, {view.custom.message}, "
                    "'Action: ' + if({view.custom.resetRequired}, 'the trip has cleared; press Reset', "
                    "{view.custom.action}))",
                    classes="cadre/font/body-active cadre/text/active", style={"whiteSpace": "normal"},
                    visible=f"({held}) || len({{view.custom.message}}) > 0")
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column",
                                                      "style": {"classes": "cadre/divider/bottom", "padding": "6px 0", "gap": "2px"}},
                   prop_config={"props.style.classes": root_classes("cadre/divider/bottom")},
                   children=[head, values, action])
    custom = {"kind": "permissive", "text": "", "action": "", "ok": True, "liveText": "", "requiredText": "",
              "bypassed": False, "bypassable": False, "latched": False, "resetRequired": False,
              "can": dict(CAN_DEFAULT), "message": "", "pending": False}
    cfg["custom.can"] = CAN_CFG
    params = {"deviceId": "", "cid": "", "writable": False}
    clear = ["self.custom.pending = False"]   # a bypass asked never outlives its condition
    return pv.view(root, params=params, param_dirs={k: "input" for k in params},
                   param_change={"deviceId": clear, "cid": clear},
                   size={"width": 368, "height": 112}, custom=custom, custom_config=cfg)


def _interlocks_pane() -> dict:
    rows = pv.node("ia.display.flex-repeater", "Conditions", pv.fpos(grow=1, basis="0px"), {
        "path": "Faceplate/InterlockRow", "direction": "column", "useDefaultViewHeight": True,
        "useDefaultViewWidth": False, "elementPosition": {"basis": "112px", "shrink": 0}, "instances": []},
        prop_config={"props.instances": pv.bind(pv.expr("{view.custom.ilkRows}"))})
    # COBD-023: a latched trip holds the device after its cause clears, until this Reset
    reset = pv.node("ia.container.flex", "ResetRow", pv.fpos(basis="48px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px"}},
        prop_config={"position.display": pv.bind(pv.expr("{view.custom.ilk.resetRequired}"))}, children=[
        _label("ResetText", pv.fpos(grow=1), text="A latched trip has cleared", classes="cadre/font/body cadre/text/active",
               style={"overflow": "hidden", "textOverflow": "ellipsis"}),
        pv.node("ia.input.button", "ResetInterlocks", pv.fpos(basis="112px", shrink=0), {
            "text": "Reset", "style": {"classes": "cadre/button/normal cadre/font/button", "height": "36px"}},
            prop_config={"props.enabled": pv.bind(pv.expr(
                "{view.custom.can.W11} && {view.custom.ilk.resetWritable}"))},
            events=pv.on_action([_pend("W11", "ilk/resetAt", "True")]))])
    return _pane("interlocks", [_section_title("IlkTitle", "PERMISSIVES AND TRIPS"), reset, _message_line(), rows])


def _message_line() -> dict:
    """The refusal of the faceplate's last command (COB-063): shown while there is one; a new device
    clears it."""
    return _label("Message", pv.fpos(basis="32px", shrink=0), "{view.custom.message}",
                  classes="cadre/font/body-active cadre/alert/badge-warning",
                  style={"padding": "4px 8px", "borderRadius": "4px", "marginTop": "8px", "whiteSpace": "normal"},
                  visible="len({view.custom.message}) > 0")


def _held_line() -> dict:
    """The Control tab's answer to "why will it not start" (COB-079 rule 1): the count of conditions
    not met, and a link to the Interlocks tab."""
    text = ("if({view.custom.refused}, 'Start refused: ', if({view.custom.ilk.interlocked}, 'Interlocked: ', "
            "'Start not permitted: ')) + if({view.custom.ilk.unsatisfied} > 0, "
            "toStr({view.custom.ilk.unsatisfied}) + ' condition' + if({view.custom.ilk.unsatisfied} = 1, '', 's') + "
            "' not met', 'reset required')")
    return pv.node("ia.container.flex", "HeldRow", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px", "marginTop": "8px"}},
        prop_config={"position.display": pv.bind(pv.expr(ILK_HELD))}, children=[
        _label("HeldText", pv.fpos(grow=1), text, classes="cadre/font/body-active cadre/alert/badge-warning",
               style={"padding": "4px 8px", "borderRadius": "4px", "overflow": "hidden", "textOverflow": "ellipsis"}),
        pv.node("ia.input.button", "ToInterlocks", pv.fpos(basis="128px", shrink=0), {
            "text": "Interlocks ›", "style": {"classes": "cadre/button/normal cadre/font/button", "height": "36px"}},
            events=pv.on_action(["self.view.custom.tab = 'interlocks'"]))])


# Analogue instruments and the trend (COB-062, COB-064; COB-PLAN-01 WP6). A limit is a setpoint row
# (`Faceplate/LimitRow`) written by the checked command on commit (W4), as the speed setpoint is; only
# the limits a device carries are listed (`cadre.hmi.limit_rows`), so no faceplate binds a missing
# tag. The trend is a stock time series chart: series 0 from a tag history binding whose `tags`
# reference a list property (`pv.tag_history`), series 1 the limits as level lines.
TREND_LIMITS = ("hiLimit", "loLimit")
# The chart's look in the 368 px dock (COB-083), with properties the Ignition-Wiki documents for
# ia.chart.timeseries only: time labels in 24 hour form (`timeAxis.tick.label.format`, a MomentJS
# string) and four of them (`timeAxis.tickCount`); five value labels (`plots[].axes[].tick.count`) to
# three significant digits (`tick.label.format`, a D3 format); each limit a dashed line
# (`plots[].trends[].columns[].styles`, `stroke.dashArray`), drawn as a series so that the value axis
# spans it. Measured 2026-10-09 (wiki page 13 section 8): `plots[].markers` render as dashed lines, but
# only inside the axis range, which they do not extend (Cadre-Sandbox-ASM observation O5).
TREND_TIME_AXIS = {"tickCount": 4, "tick": {"label": {"format": "HH:mm"}}}
TREND_VALUE_AXIS = {"name": "value", "alignment": "left", "tick": {"count": 5, "label": {"format": ".3~g"}}}
# The controller's output, in per cent, on an axis of its own at the right (`plots[].axes[].alignment`,
# `min`, `max`; IGW ia.chart.timeseries).
TREND_OUTPUT_AXIS = {"name": "out", "alignment": "right", "min": 0, "max": 100,
                     "tick": {"count": 5, "label": {"format": ".3~g"}}}
DASHED = {k: {"fill": {"color": "", "opacity": None}, "stroke": {"color": "", "dashArray": "6 4", "opacity": None, "width": None}}
          for k in ("normal", "highlighted", "muted")}
# A stepped member's trend (`cadre.hmi.STEP_MEMBERS`: a sequence's step number): the value holds until
# the next sample, `curveStepAfter` of `plots[].trends[].interpolation` (IGW ia.chart.timeseries, whose
# default is `curveLinear`); its history comes as the last value of each interval (`history_tags`).
STEP_MEMBERS = tuple(scripts.constant("STEP_MEMBERS"))
STEPPED = "curveStepAfter"


def trend_chart(series_binding: dict, limits_binding: dict | None, name: str = "Chart", pos: dict | None = None,
                device: str = "{view.params.deviceId}", extra: tuple = (), column: str = "value",
                interpolation: str | None = None) -> dict:
    """The stock time series chart of a trend: series 0 the value from a tag history binding, series 1
    (with `limits_binding`) the limits as dashed level lines. The limits trend shows only for a device
    that carries a limit: an empty one drew a second value axis, 0 to 100 (measured 2026-10-09).
    `extra` adds series, each `{"name", "binding", "axis", "visible"}`: one trend per series, its
    column the series' name, on the value axis or on the output axis, shown by its own binding.
    `column` is the column of series 0 (the alias of its history path), and `interpolation` the curve
    of its line where that is not the chart's default (`plots[].trends[].interpolation`, IGW
    ia.chart.timeseries)."""
    trends = [{"series": "value", "axis": "value", "columns": [{"key": column}], "type": "line",
               "baselines": [], "visible": True}]
    if interpolation:
        trends[0]["interpolation"] = interpolation
    series = [{"name": "value", "data": []}]
    cfg = {"props.series[0].data": series_binding}
    axes = [TREND_VALUE_AXIS]
    if limits_binding is not None:
        series.append({"name": "limits", "data": []})
        trends.append({"series": "limits", "axis": "value", "columns": [{"key": k, "styles": DASHED} for k in TREND_LIMITS],
                       "type": "line", "baselines": [], "visible": True})
        cfg["props.series[1].data"] = limits_binding
        cfg["props.plots[0].trends[1].visible"] = pv.bind(pv.expr(device), [pv.script_transform([
            "return len(cadre.hmi.limit_rows(value)) > 0"])])
    for e in extra:
        i = len(series)
        series.append({"name": e["name"], "data": []})
        trends.append({"series": e["name"], "axis": e["axis"], "columns": [{"key": e["name"]}], "type": "line",
                       "baselines": [], "visible": True})
        cfg[f"props.series[{i}].data"] = e["binding"]
        cfg[f"props.plots[0].trends[{i}].visible"] = e["visible"]
        if e["axis"] == TREND_OUTPUT_AXIS["name"] and TREND_OUTPUT_AXIS not in axes:
            axes.append(TREND_OUTPUT_AXIS)
    return pv.node("ia.chart.timeseries", name, pos or pv.fpos(grow=1, basis="0px"), {
        "series": series, "plots": [{"axes": axes, "markers": [], "trends": trends}],
        "timeAxis": TREND_TIME_AXIS, "timeRange": {"dateFormat": "D-M-YYYY", "timeFormat": "HH:mm", "visible": True},
        "title": {}}, prop_config=cfg)


# A row's refusal is the refusal of one write to one member of one device. A repeater keeps a row's
# view while its instance changes (measured 2026-10-11 by the generated walk: a limit row refused on
# AIT-301 still read "Refused" on AIT-401, opened next), so the row clears its message when it is
# handed another device or another member, by a change script on the parameter, as the faceplate itself
# does for its own message (`_tabbed`; IGW:09-params-and-custom section 6, `pv.view` `param_change`).
ROW_RESET = {"deviceId": ["self.custom.message = ''", "self.custom.pending = False"],
             "member": ["self.custom.message = ''", "self.custom.pending = False"]}
# A row's field asks before it writes (F029): its commit keeps the value typed (`custom.typed`) and
# sets `custom.pending`; Set makes the checked write, and the cancel button puts the tag's value back.
ROW_HOLD = ["self.view.custom.typed = self.props.value", "self.view.custom.pending = True"]


def _row_answers(path_arg: str, enabled: str) -> list:
    """Set and the cancel button of a row, shown while the row holds a value typed. `path_arg` is the
    write path as the script names it (a literal, or `p.path`); `enabled` is the field's own rule."""
    back = "self.getSibling('Setpoint').props.value = system.tag.readBlocking([p.deviceId + '/' + p.member])[0].value"
    shown = {"position.display": pv.bind(pv.expr("{view.custom.pending}"))}
    return [pv.node("ia.input.button", "Set", pv.fpos(basis="56px", shrink=0), {
                "text": SET, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "32px"}},
                prop_config={**shown, "props.enabled": pv.bind(pv.expr(enabled))},
                events=pv.on_action([
                    "p = self.view.params",
                    f"msg = cadre.hmi.command(self.session, {path_arg}, p.deviceId, p.member, self.view.custom.typed)",
                    "self.view.custom.pending = False",
                    "self.view.custom.message = msg",
                    "if msg:",
                    "\t" + back])),
            pv.node("ia.input.button", "Undo", pv.fpos(basis="32px", shrink=0), {
                "text": UNDO, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "32px"}},
                prop_config=shown,
                events=pv.on_action(["p = self.view.params", "self.view.custom.pending = False", back]))]


def faceplate_limit_row() -> dict:
    """`Faceplate/LimitRow`: one alarm limit, `<device>/<member>`, as a setpoint field, and a lamp lit
    while the value (`<device>/<valueMember>`) is beyond it. `writable` (from `cadre.hmi.limit_rows`)
    keeps the field disabled for a limit the device model marks read only. A refused write reads
    "Refused" in the lamp until the row's next accepted write, or until the row shows another device
    or another member (ROW_RESET)."""
    refs = {"0": "{view.params.deviceId}", "1": "{view.params.member}", "2": "{view.params.valueMember}"}
    beyond = ("if({view.params.high}, {view.custom.value} >= {view.custom.limit}, "
              "{view.custom.value} <= {view.custom.limit})")
    entry = pv.node("ia.input.numeric-entry-field", "Setpoint", pv.fpos(basis="120px", shrink=0), {
        "format": "0.00", "spinner": SPINNER, "style": {"height": "32px"}},
        prop_config={"props.value": pv.bind(pv.tag_indirect("{0}/{1}", refs)),
                     "props.enabled": pv.bind(pv.expr("{view.custom.can.W4} && {view.params.writable}"))},
        events=pv.on_action(ROW_HOLD))
    lamp = pv.node("ia.display.label", "Lamp", pv.fpos(basis="72px", shrink=0), {
        "textStyle": {"textAlign": "center"},
        "style": {"classes": "cadre/font/label cadre/text/neutral", "borderRadius": "4px", "justifyContent": "center"}},
        prop_config={"props.text": pv.bind(pv.expr(   # a refused write shows here (COB-063)
            f"if(len({{view.custom.message}}) > 0, 'Refused', if({beyond}, 'Active', 'Normal'))")),
                     "props.style.classes": pv.bind(pv.expr(
                         f"if({beyond}, 'cadre/font/label cadre/alert/badge-warning', 'cadre/font/label cadre/text/neutral')")),
                     "position.display": pv.bind(pv.expr("!{view.custom.pending}"))})
    root = pv.node("ia.container.flex", "root", {}, {"direction": "row", "alignItems": "center", "style": {"gap": "8px"}},
                   prop_config={"props.style.classes": root_classes()},
                   children=[_label("Label", pv.fpos(basis="132px", shrink=0), "{view.params.label}",
                                    classes="cadre/font/label cadre/text/neutral"), entry, lamp]
                   + _row_answers("'W4'", "{view.custom.can.W4} && {view.params.writable}"))
    cfg = {"custom.limit": pv.bind(pv.tag_indirect("{0}/{1}", refs)),
           "custom.value": pv.bind(pv.tag_indirect("{0}/{2}", refs)), "custom.can": CAN_CFG}
    params = {"deviceId": "", "member": "", "label": "", "valueMember": "value", "high": True, "writable": False}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params}, param_change=ROW_RESET,
                   size={"width": 368, "height": 44},
                   custom={"limit": 0, "value": 0, "can": dict(CAN_DEFAULT), "message": "", "pending": False,
                           "typed": 0}, custom_config=cfg)


def _limit_block(value_member: str) -> list:
    rows = pv.node("ia.display.flex-repeater", "Limits", pv.fpos(basis="180px", shrink=0), {
        "path": "Faceplate/LimitRow", "direction": "column", "useDefaultViewHeight": True,
        "useDefaultViewWidth": False, "elementPosition": {"basis": "44px", "shrink": 0}, "instances": []},
        prop_config={"props.instances": pv.bind(pv.expr("{view.custom.limitRows}"))})
    title = _label("LimitTitle", pv.fpos(shrink=0), text="ALARM LIMITS", classes="cadre/font/overline cadre/text/neutral",
                   style={"marginTop": "12px"}, visible="len({view.custom.limitRows}) > 0")
    # F028: the on-delay of each limit the device carries the delay of, a setpoint row written through W4
    delays = pv.node("ia.display.flex-repeater", "Delays", pv.fpos(basis="0px", shrink=0), {
        "path": "Faceplate/SetpointRow", "direction": "column", "useDefaultViewHeight": True,
        "useDefaultViewWidth": False, "elementPosition": {"basis": f"{ROW_HEIGHT}px", "shrink": 0}, "instances": []},
        prop_config={"props.instances": pv.bind(pv.expr("{view.custom.delayRows}")),
                     "position.basis": pv.bind(pv.expr(f"toStr(len({{view.custom.delayRows}}) * {ROW_HEIGHT}) + 'px'"))})
    return [title, rows, delays]


DELAY_ROWS_CFG = pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
    "return cadre.hmi.delay_rows(value, self.session)"])])


def _limit_rows_cfg(value_member: str) -> dict:
    return pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
        f"return [dict(r, valueMember='{value_member}', high=r['member'].startswith('hi')) "
        f"for r in cadre.hmi.limit_rows(value, '{value_member}', self.session)]"])])


def _trend_ranges() -> dict:
    def rng(h):
        return pv.node("ia.input.button", f"Range_{h}h", pv.fpos(basis="72px", shrink=0), {
            "text": f"{h} h", "style": {"classes": "cadre/button/flat cadre/font/button", "height": "32px"}},
            prop_config={"props.style.classes": pv.bind(pv.expr(
                f"if({{view.custom.hours}} = {h}, 'cadre/button/selected cadre/font/button', "
                "'cadre/button/flat cadre/font/button')"))},
            events=pv.on_action([f"self.view.custom.hours = {h}"]))
    return pv.node("ia.container.flex", "Ranges", pv.fpos(basis="40px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px"}}, children=[rng(1), rng(8)])


def _limit_series_cfg() -> dict:
    return pv.bind(pv.expr("if(toMillis(now(10000)) > 0, {view.params.deviceId} + '|' + toStr({view.custom.hours}), '')"), [
        pv.script_transform(["parts = (value or '').split('|')",
                             "return cadre.hmi.limit_series(parts[0], int(parts[1]) if len(parts) > 1 and parts[1] else 1)"])])


def _trend_pane(member: str) -> dict:
    """The Trend tab: the last hour of `<device>/<member>` from the historian, 8 h selectable, with the
    device's limits drawn level across the chart."""
    chart = trend_chart(
        pv.bind(pv.tag_history("{view.custom.historyTags}", "{view.custom.hours}", "HOUR")), _limit_series_cfg())
    return _pane("trend", [_trend_ranges(), chart])


def trend_card() -> dict:
    """`Trend/Card`: one historised member of the trend page (COB-064): the device's identifier,
    description and unit, and the chart of the faceplate trend (its limits dashed) over the page's
    range. The title opens the device's faceplate."""
    head = pv.node("ia.container.flex", "Head", pv.fpos(basis="28px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px", "cursor": "pointer"}},
        events={"dom": {"onClick": pv.script_handler([
            "p = self.view.params",
            "cadre.hmi.select_device(self.session, p.deviceId, p.kind, p.title, p.label)",
            *open_faceplate()])}},
        children=[_label("Title", pv.fpos(shrink=0), "{view.params.title}", classes="cadre/font/body-active cadre/text/active"),
                  _label("Label", pv.fpos(grow=1), "{view.params.label}", classes="cadre/font/label cadre/text/neutral",
                         style={"overflow": "hidden", "textOverflow": "ellipsis"}),
                  _label("Unit", pv.fpos(shrink=0), "{view.params.unit}", classes="cadre/font/label cadre/text/neutral")])
    chart = trend_chart(
        pv.bind(pv.tag_history("{view.custom.historyTags}", "{view.params.hours}", "HOUR")),
        pv.bind(pv.expr("if(toMillis(now(10000)) > 0, {view.params.deviceId} + '|' + toStr({view.params.hours}), '')"), [
            pv.script_transform(["parts = (value or '').split('|')",
                                 "return cadre.hmi.limit_series(parts[0], int(parts[1]) if len(parts) > 1 and parts[1] else 1)"])]))
    # a stepped member (a sequence's step number) is drawn as steps, every other as the chart's default
    chart["propConfig"]["props.plots[0].trends[0].interpolation"] = pv.bind(pv.expr(
        "if(" + " || ".join(f"{{view.params.member}} = '{m}'" for m in STEP_MEMBERS)
        + f", '{STEPPED}', 'curveLinear')"))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"padding": "8px", "gap": "4px"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/card")}, children=[head, chart])
    params = {"deviceId": "", "member": "value", "kind": "", "title": "", "label": "", "unit": "", "hours": 1}
    cfg = {"custom.historyTags": pv.bind(pv.expr("{view.params.deviceId} + '|' + {view.params.member}"), [
        pv.script_transform(["parts = (value or '').split('|')",
                             "return cadre.hmi.history_tags(parts[0], parts[1] if len(parts) > 1 else 'value')"])])}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params}, size={"width": 380, "height": 240},
                   custom={"historyTags": [{"path": "", "alias": "value"}]}, custom_config=cfg)


def trends_page() -> dict:
    """`Framework/TrendsPage`, the route `/trends` of a child whose descriptors have historised members
    (COB-064): a range row (1, 8 or 24 h) and one `Trend/Card` per member of `session.custom.trends`, the
    list the generator writes (`screen.trend_index`)."""
    def rng(h):
        return pv.node("ia.input.button", f"Range_{h}h", pv.fpos(basis="80px", shrink=0), {
            "text": f"{h} h", "style": {"classes": "cadre/button/flat cadre/font/button", "height": "32px"}},
            prop_config={"props.style.classes": pv.bind(pv.expr(
                f"if({{view.custom.hours}} = {h}, 'cadre/button/selected cadre/font/button', "
                "'cadre/button/flat cadre/font/button')"))},
            events=pv.on_action([f"self.view.custom.hours = {h}"]))
    ranges = pv.node("ia.container.flex", "Ranges", pv.fpos(basis="48px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px", "padding": "0 8px"}},
        children=[_label("Title", pv.fpos(grow=1), text="HISTORISED MEMBERS", classes="cadre/font/overline cadre/text/neutral"),
                  rng(1), rng(8), rng(24)])
    cards = pv.node("ia.display.flex-repeater", "Cards", pv.fpos(grow=1, basis="0px"), {
        "path": "Trend/Card", "direction": "row", "wrap": "wrap", "useDefaultViewHeight": True,
        "useDefaultViewWidth": False, "elementPosition": {"basis": "380px", "grow": 1, "shrink": 0},
        "instances": [], "style": {"overflow": "auto", "gap": "8px"}},
        prop_config={"props.instances": pv.bind(pv.expr("{view.custom.hours}"), [pv.script_transform([
            "return [dict(t, hours=value) for t in (self.session.custom.trends or [])]"])])})
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"padding": "8px", "gap": "8px"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")},
                   children=[ranges, cards, search_panel()])
    return pv.view(root, size={"width": 1600, "height": 852}, custom={"hours": 1})


UNIT_CFG = pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
    "return cadre.hmi.device_unit(self.session, value)"])])


def _big_value() -> dict:
    """The process value of an instrument or a controller, large, with its unit from the device index."""
    return pv.node("ia.display.label", "Value", pv.fpos(basis="56px", shrink=0), {
        "style": {"classes": "cadre/font/instrument-value-enhanced-active cadre/text/active"}},
        prop_config={"props.text": pv.bind(pv.expr(
            f"numberFormat({_dv('value', 'value')}, '0.00') + ' ' + {{view.custom.unit}}")),
                     "position.display": pv.bind(pv.expr(_dv("has", "value")))})


# Setpoints (W3 the speed setpoint, W12 the controller's setpoint, W14 its manual output, W15 its
# tuning). A setpoint field shows its member through a one way tag binding, as the limit row does, and
# that binding is the only one that may sit on the field: the tag hands the field a value when the
# member changes, not at each poll, so the text an operator is typing is kept. The field lives in a row
# view of its own, and the faceplate holds a repeater with that one row while the device carries the
# member and with none otherwise, so the binding never meets a missing tag.
SETPOINT_PATHS = ("W3", "W4", "W12", "W14", "W15", "W19")   # W4: a limit's delay (F028); W19: the Config rows (F010)
# A field's entry bounds are the range `cadre.hmi.command` enforces for its member (MEMBER_BOUNDS).
SETPOINT_BOUNDS = scripts.constant("MEMBER_BOUNDS")


def faceplate_setpoint_row() -> dict:
    """`Faceplate/SetpointRow`: one setpoint, `<device>/<member>`, written on commit by the checked
    command of its write path; a refused write puts the tag's value back and the row reads "Refused",
    until its next accepted write or until it shows another device or another member (ROW_RESET).
    `enabled` is the faceplate's own condition (the member writable, the loop in manual)."""
    refs = {"0": "{view.params.deviceId}", "1": "{view.params.member}"}
    can = ("case({view.params.path}, " + ", ".join(f"'{w}', {{view.custom.can.{w}}}" for w in SETPOINT_PATHS)
           + ", false)")
    entry = pv.node("ia.input.numeric-entry-field", "Setpoint", pv.fpos(basis="120px", shrink=0), {
        "format": "0.0", "spinner": SPINNER, "style": {"height": "32px"}},
        prop_config={"props.value": pv.bind(pv.tag_indirect("{0}/{1}", refs)),
                     "props.enabled": pv.bind(pv.expr(f"{can} && {{view.params.enabled}}")),
                     "props.format": pv.bind(pv.prop("view.params.format")),
                     "props.inputBounds.minimum": pv.bind(pv.prop("view.params.minimum")),
                     "props.inputBounds.maximum": pv.bind(pv.prop("view.params.maximum"))},
        events=pv.on_action(ROW_HOLD))
    refused = "len({view.custom.message}) > 0"
    note = pv.node("ia.display.label", "Note", pv.fpos(basis="72px", shrink=0), {
        "textStyle": {"textAlign": "center"},
        "style": {"classes": "cadre/font/label cadre/text/neutral", "borderRadius": "4px", "justifyContent": "center"}},
        prop_config={"props.text": pv.bind(pv.expr(f"if({refused}, 'Refused', {{view.params.unit}})")),
                     "props.style.classes": pv.bind(pv.expr(
                         f"if({refused}, 'cadre/font/label cadre/alert/badge-warning', 'cadre/font/label cadre/text/neutral')")),
                     "position.display": pv.bind(pv.expr("!{view.custom.pending}"))})
    root = pv.node("ia.container.flex", "root", {}, {"direction": "row", "alignItems": "center", "style": {"gap": "8px"}},
                   prop_config={"props.style.classes": root_classes()},
                   children=[_label("Label", pv.fpos(basis="132px", shrink=0), "{view.params.label}",
                                    classes="cadre/font/label cadre/text/neutral"), entry, note]
                   + _row_answers("p.path", f"{can} && {{view.params.enabled}}"))
    params = {"deviceId": "", "member": "", "label": "", "path": "", "format": "0.0", "minimum": None,
              "maximum": None, "unit": "", "enabled": False}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params}, param_change=ROW_RESET,
                   size={"width": 368, "height": 44},
                   custom={"can": dict(CAN_DEFAULT), "message": "", "pending": False, "typed": 0},
                   custom_config={"custom.can": CAN_CFG})


def _setpoint(name: str, member: str, label: str, path: str, *, fmt: str = "0.0",
              unit: str = "''", enabled: str | None = None) -> dict:
    """One setpoint of a faceplate: a repeater that holds one `Faceplate/SetpointRow` while the device
    carries `member`, and none otherwise. `unit` is an expression; `enabled` (an expression, by
    default the member's `writable` flag) reaches the row beside the permission of its write path.
    The entry bounds are those of the member in SETPOINT_BOUNDS, the range the checked write enforces."""
    shown = _dv("has", member)
    minimum, maximum = SETPOINT_BOUNDS.get(member, [None, None])
    row = {"member": member, "label": label, "path": path, "format": fmt, "minimum": minimum, "maximum": maximum}
    spec = (f"if({shown}, {{view.params.deviceId}} + '|' + if({enabled or _dv('writable', member)}, '1', '0') "
            f"+ '|' + {unit}, '')")
    return pv.node("ia.display.flex-repeater", name, pv.fpos(basis="44px", shrink=0), {
        "path": "Faceplate/SetpointRow", "direction": "column", "useDefaultViewHeight": True,
        "useDefaultViewWidth": False, "elementPosition": {"basis": "44px", "shrink": 0}, "instances": []},
        prop_config={"position.display": pv.bind(pv.expr(shown)),
                     "props.instances": pv.bind(pv.expr(spec), [pv.script_transform([
                         "parts = (value or '').split('|')",
                         "if len(parts) < 3 or not parts[0]:",
                         "	return []",
                         f"return [dict({row!r}, deviceId=parts[0], enabled=parts[1] == '1', unit=parts[2])]"])])})


def faceplate_instrument() -> dict:
    """`Faceplate/Instrument` (COB-062): readouts and instrument fields marked as devices. Values (the
    value with its unit, the alarm limits as setpoints), Trend, Alarms. Members: `value`, and
    `hiLimit`, `loLimit`, `hiHiLimit`, `loLoLimit` where the instrument has them."""
    rows = [_section_title("ValueTitle", "VALUE", display=_dv("has", "value")), _big_value()] + _limit_block("value")
    custom_cfg = {"custom.unit": UNIT_CFG, "custom.limitRows": _limit_rows_cfg("value")}
    return _tabbed("instrument", rows, {"unit": "", "limitRows": []}, custom_cfg)


def faceplate(kind: str, style: str = "openbridge") -> dict:
    """A device faceplate over the device folder contract (wiki page 06 section 5), each member shown
    only where the device carries it: `state`, `mode`, `fault`, and for motorised devices `speed`, as
    status rows; Start and Stop (Open and Close) where `cmd` may be written, the mode buttons where
    `mode` may, the speed setpoint where `speedSp` exists, and Reset fault while a writable `fault` is
    set. Every write goes through `cadre.hmi.command`. Tabs: Control, Alarms, Interlocks and
    Maintenance, the last two only for a device that carries them. In the `asm` style (COBD-045) the
    same rows are the Home tab, beneath the header strip, and the tabs are those of ASM_TABS."""
    motor = kind == "pump"

    def has(m):
        return _dv("has", m)

    def val(m):
        return _dv("value", m)

    def writable(m):
        return _dv("writable", m)
    status = ("state", "mode", "fault") + (("speed",) if motor else ())
    rows = [_section_title("StatusTitle", "STATUS", display=" || ".join(has(m) for m in status)),
            _value_row("State", "State", f"if({val('state')}, " + (
                "'Open', 'Closed')" if kind == "valve" else "'Running', 'Stopped')"), display=has("state")),
            _value_row("Mode", "Control mode", f"if({OWNED}, {{view.custom.dev.owner.name}}, {MODE_TEXT})",
                       display=has("mode")),
            # ownership by mode (COBD-044): who holds the device, for a device whose model gives its modes
            _value_row("Owner", "Owner", "{view.custom.dev.owner.text}", display=f"{has('mode')} && {OWNED}")]
    fault_row = _value_row("Fault", "Fault", f"if({val('fault')}, 'Fault', 'Normal')", display=has("fault"))
    fault_row["children"][1]["propConfig"]["props.style.classes"] = pv.bind(pv.expr(
        f"if({val('fault')}, 'cadre/font/body-active cadre/alert/badge-alarm', "
        "'cadre/font/body-active cadre/text/active')"))
    rows.append(fault_row)
    if motor:
        rows.append(_value_row("Speed", "Speed", f"numberFormat({val('speed')}, '0.0') + ' %'",
                               value_classes="cadre/font/instrument-value-regular-active cadre/text/active",
                               display=has("speed")))
    on_text, off_text = ("Open", "Close") if kind == "valve" else ("Start", "Stop")
    reset = f"{val('fault')} && {writable('fault')}"   # a fault that is a status of the source offers no reset
    commands = [writable("cmd"), writable("mode")] + ([has("speedSp")] if motor else []) + [f"({reset})"]
    rows.append(_section_title("CommandTitle", "COMMANDS", display=" || ".join(commands)))
    # why the owner disables the device's commands, in words (COBD-044: never a silent grey button)
    rows.append(_label("OwnerReason", pv.fpos(basis="32px", shrink=0), "{view.custom.dev.reason}",
                       classes="cadre/font/body-active cadre/alert/badge-caution",
                       style={"padding": "4px 8px", "borderRadius": "4px", "whiteSpace": "normal"},
                       visible="len({view.custom.dev.reason}) > 0"))
    rows.append(pv.node("ia.container.flex", "Commands", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "style": {"gap": "8px"}},
        prop_config={"position.display": pv.bind(pv.expr(writable("cmd")))},
        children=[_cmd_button("On", on_text, [   # refused while interlocks hold the device (COB-079 rule 1)
                                  "if cadre.hmi.start_permitted(self.view.params.deviceId):",
                                  "	self.view.custom.refused = False",
                                  "	" + _pend("W1", "cmd", "True"),
                                  "else:",
                                  "	self.view.custom.refused = True"],
                              selected_expr=val("state"), path="W1", member="cmd"),
                  _cmd_button("Off", off_text, [
                      _pend("W1", "cmd", "False")],
                      selected_expr=f"!{val('state')}", path="W1", member="cmd")]))
    rows.append(pv.node("ia.container.flex", "Modes", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "style": {"gap": "8px"}},
        prop_config={"position.display": pv.bind(pv.expr(f"{writable('mode')} && !{OWNED}"))},
        children=[_cmd_button(m, m, [
            _pend("W2", "mode", str(v))],
            selected_expr=f"{val('mode')} = {v}", path="W2", member="mode")
                  for m, v in (("Auto", 0), ("Manual", 1), ("Local", 2))]))
    rows += _ownership_rows(writable("mode"))
    if motor:
        # W3: the commit runs the checked write, and a refusal puts the tag's value back in the field (a
        # binding write would run no check, NOTE-COB-04 6.2 step 4); the owner gates it (COBD-044)
        rows.append(_setpoint("SpeedSp", "speedSp", "Speed setpoint (%)", "W3",
                              enabled=f"{writable('speedSp')} && {{view.custom.dev.allowed.W3}}"))
    rows.append(pv.node("ia.input.button", "Reset", pv.fpos(basis="40px", shrink=0), {
        "text": "Reset fault", "style": {"classes": "cadre/button/normal cadre/font/button"}},
        prop_config={"position.display": pv.bind(pv.expr(reset)),
                     "props.enabled": pv.bind(pv.expr(
                         f"{{view.custom.can.W5}} && {_dv('write', 'fault')} && {{view.custom.dev.allowed.W5}}"))},
        events=pv.on_action([
            _pend("W5", "fault", "False")])))
    rows.append(_message_line())
    return _tabbed(kind, rows, {}, {}, style=style)


# Maintenance functions (wiki page 13 section 9): the force, the object error mask and the read only
# flags a device carries under `mnt/`. The tab shows only for a device with such a member, and each
# row only while its members exist. The writes are `cadre.hmi.force` (W16) and `error_mask` (W17).
# The configuration rows (F010 of the ASMP study, COBD-045): one `Faceplate/SetpointRow` per member
# the device model marks `config`, written through W19 (`cadre.hmi.configure`) within the bounds
# the model gives; the rows head the Maintenance tab, and the Config tab of an `asm` faceplate.
CONFIG_PATH = scripts.constant("CONFIG_PATH")
CONFIG_PREFIX = scripts.constant("CONFIG_PREFIX")
ROW_HEIGHT = 44


def _config_rows() -> list:
    shown = "{view.custom.dev.config} > 0"
    spec = f"{{view.params.deviceId}} + '|' + if({{view.custom.dev.allowed.{CONFIG_PATH}}}, '1', '0')"
    rows = pv.node("ia.display.flex-repeater", "ConfigRows", pv.fpos(basis="0px", shrink=0), {
        "path": "Faceplate/SetpointRow", "direction": "column", "useDefaultViewHeight": True,
        "useDefaultViewWidth": False, "elementPosition": {"basis": f"{ROW_HEIGHT}px", "shrink": 0}, "instances": []},
        prop_config={"position.display": pv.bind(pv.expr(shown)),
                     "position.basis": pv.bind(pv.expr(f"toStr({{view.custom.dev.config}} * {ROW_HEIGHT}) + 'px'")),
                     "props.instances": pv.bind(pv.expr(spec), [pv.script_transform([
                         "parts = (value or '').split('|')",
                         "return cadre.hmi.config_rows(self.session, parts[0], len(parts) > 1 and parts[1] == '1')"])])})
    return [_section_title("ConfigTitle", "CONFIGURATION", display=shown), rows]


def has_config(kind: str) -> bool:
    """The faceplate of a device of `kind` draws configuration rows: its Maintenance tab, or the
    Config tab of its `asm` faceplate."""
    key = FACEPLATE_VIEW.get(kind, "").split("/")[-1].lower()
    return "maintenance" in [k for k, _ in FACEPLATE_TABS.get(key, [])] or kind in ASM_VIEW


def _maintenance_pane(key: str = "maintenance", extra: list | None = None) -> dict:
    """The Maintenance tab, or the Config tab of an `asm` faceplate (`key`): the configuration rows,
    then the maintenance functions. `extra` rows (the generator's service data) come first."""
    force = "{view.custom.dev.force}"
    mask = scripts.constant("MNT_MASK")
    flags = scripts.constant("MNT_FLAGS")
    forced = "cadre/font/body-active cadre/alert/badge-caution"

    def stated(row, abnormal):
        row["children"][1]["propConfig"]["props.style.classes"] = pv.bind(pv.expr(
            f"if({abnormal}, '{forced}', 'cadre/font/body-active cadre/text/active')"))
        return row

    def group(name, display, buttons):
        return pv.node("ia.container.flex", name, pv.fpos(basis="44px", shrink=0), {
            "direction": "row", "style": {"gap": "8px"}},
            prop_config={"position.display": pv.bind(pv.expr(display))}, children=buttons)

    def force_button(name, text, action):
        return _cmd_button(name, text, [
            _pend("W16", "force", repr(action))],
            selected_expr=f"{force} = '{action}'", path="W16", member="force")

    def mask_button(name, text, value):
        return _cmd_button(name, text, [
            _pend("W17", mask, str(value))],
            selected_expr=("" if value else "!") + _dv("value", mask), path="W17", member=mask)
    has_force = f"len({force}) > 0"
    rows = [_section_title("ForceTitle", "FORCE", display=has_force),
            stated(_value_row("Force", "Force", f"case({force}, 'on', 'Forced on', 'off', 'Forced off', 'Automatic')",
                              display=has_force), f"{force} = 'on' || {force} = 'off'"),
            group("ForceCommands", _dv("writable", "force"), [
                force_button("ForceOn", "Force on", "on"), force_button("ForceOff", "Force off", "off"),
                force_button("ForceAuto", "Automatic", "auto")]),
            _section_title("MaskTitle", "OBJECT ERROR MASK", display=_dv("has", mask)),
            stated(_value_row("Mask", "Object error mask", f"if({_dv('value', mask)}, 'Masked', 'Automatic')",
                              display=_dv("has", mask)), _dv("value", mask)),
            group("MaskCommands", _dv("writable", mask), [
                mask_button("MaskOn", "Mask", True), mask_button("MaskAuto", "Automatic", False)]),
            _section_title("FlagTitle", "FLAGS", display=" || ".join(_dv("has", m) for m, _ in flags))]
    for i, (m, label) in enumerate(flags):
        rows.append(_value_row(f"Flag{i}", label, f"if({_dv('value', m)}, 'Yes', 'No')", display=_dv("has", m)))
    return _pane(key, (extra or []) + _config_rows() + rows + [_message_line()])


def faceplate_input() -> dict:
    """`Faceplate/Input`: a digital input (kind `indicator`). Status (the state as On or Off),
    Maintenance (the force and the flags, for an input that carries them), Alarms."""
    rows = [_section_title("StatusTitle", "STATUS", display=_dv("has", "state")),
            _value_row("State", "State", f"if({_dv('value', 'state')}, 'On', 'Off')", display=_dv("has", "state"))]
    return _tabbed("input", rows, {}, {})


def faceplate_sequence() -> dict:
    """`Faceplate/Sequence`: a sequence (a self cleaning filter, a boiler, a softener), every member
    optional. Status (the text of the current step large, the step number, the fault, and under
    Commands one button per pulse member the device may write, captioned by the device model), Trend
    (the step number as a stepped line, only where the trend index lists it) and Alarms. Members:
    `step`, `stepText`, `trigger` (a pulse command, write path W18) and `fault`."""
    def has(m):
        return _dv("has", m)

    def val(m):
        return _dv("value", m)
    text = pv.node("ia.display.label", "StepText", pv.fpos(basis="56px", shrink=0), {
        "style": {"classes": "cadre/font/instrument-value-m-active cadre/text/active", "whiteSpace": "normal",
                  "overflow": "hidden"}},
        prop_config={"props.text": pv.bind(pv.expr(val("stepText"))),
                     "position.display": pv.bind(pv.expr(has("stepText")))})
    fault_row = _value_row("Fault", "Fault", f"if({val('fault')}, 'Fault', 'Normal')", display=has("fault"))
    fault_row["children"][1]["propConfig"]["props.style.classes"] = pv.bind(pv.expr(
        f"if({val('fault')}, 'cadre/font/body-active cadre/alert/badge-alarm', "
        "'cadre/font/body-active cadre/text/active')"))
    pulses = [m for m in FACEPLATE_READS["sequence"] if m in PULSE_MEMBERS]
    buttons = []
    for m in pulses:   # the caption is the device model's, else the member's name (`dev.pulses`)
        b = _cmd_button(f"Pulse_{m.replace('/', '_')}", m, [
            _pend(PULSE_PATH, m, "True")],
            path=PULSE_PATH, member=m)
        b["propConfig"]["props.text"] = pv.bind(pv.expr(_dv("pulses", m)))
        b["propConfig"]["position.display"] = pv.bind(pv.expr(_dv("writable", m)))
        buttons.append(b)
    offered = " || ".join(_dv("writable", m) for m in pulses)
    rows = [_section_title("StepTitle", "SEQUENCE", display=" || ".join(has(m) for m in ("stepText", "step", "fault"))),
            text,
            _value_row("Step", "Step", f"numberFormat({val('step')}, '0')", display=has("step")),
            fault_row,
            _section_title("CommandTitle", "COMMANDS", display=offered),
            pv.node("ia.container.flex", "Commands", pv.fpos(basis="44px", shrink=0), {
                "direction": "row", "style": {"gap": "8px"}},
                prop_config={"position.display": pv.bind(pv.expr(offered))}, children=buttons),
            _message_line()]
    alias = SEQUENCE_TREND[0]
    chart = trend_chart(pv.bind(pv.tag_history("{view.custom.historyTags}", "{view.custom.hours}", "HOUR")), None,
                        column=alias, interpolation=STEPPED)
    custom = {"hours": 1, "trend": {m: False for m in SEQUENCE_TREND},
              "historyTags": [{"path": "", "alias": alias}]}
    custom_cfg = {"custom.trend": pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
                      f"return cadre.hmi.trended(self.session, value, {list(SEQUENCE_TREND)!r})"])]),
                  "custom.historyTags": pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
                      f"return cadre.hmi.trend_tags(self.session, value, '{alias}')"])])}
    return _tabbed("sequence", rows, custom, custom_cfg, panes={"trend": _pane("trend", [_trend_ranges(), chart])})


def faceplate_controller() -> dict:
    """`Faceplate/Controller`: a PID loop, every member optional. Control (the process value, the
    setpoint, the output as a value and a bar, the Auto and Manual buttons, the manual output, the
    alarm limits), Trend (the process value and the setpoint on the value axis, the output on an axis
    from 0 to 100, each where the member is historised), Tuning (gain, integral time and derivative
    time, where the loop carries one) and Alarms. Members: `value`, `sp`, `out`, `manual` (false
    automatic, true manual), `manOut`, `gain`, `ti`, `td`, and the instrument's limits."""
    def has(m):
        return _dv("has", m)

    def val(m):
        return _dv("value", m)
    out = val("out")
    bar = pv.node("ia.display.progress", "OutputBar", pv.fpos(basis="12px", shrink=0), {
        "min": 0, "max": 100, "value": 0, "bar": {"color": "var(--instrument-enhanced-secondary-color)"},
        "track": {"color": "var(--container-section-color)"}},
        prop_config={"props.value": pv.bind(pv.expr(f"if({out} > 100, 100, if({out} < 0, 0, {out}))")),
                     "position.display": pv.bind(pv.expr(has("out")))})
    modes = pv.node("ia.container.flex", "Modes", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "style": {"gap": "8px"}},
        prop_config={"position.display": pv.bind(pv.expr(_dv("writable", "manual")))},
        children=[_cmd_button(text, text, [
            _pend("W13", "manual", str(manual))],
            selected_expr=("" if manual else "!") + val("manual"), path="W13", member="manual")
                  for text, manual in (("Auto", False), ("Manual", True))])
    rows = [_section_title("ValueTitle", "PROCESS VALUE", display=has("value")), _big_value(),
            _section_title("LoopTitle", "LOOP", display=" || ".join(has(m) for m in ("sp", "out", "manual", "manOut"))),
            _setpoint("Sp", "sp", "Setpoint", "W12", fmt="0.00", unit="{view.custom.unit}"),
            _value_row("Output", "Output", f"numberFormat({out}, '0.0') + ' %'", display=has("out")), bar,
            _value_row("Mode", "Control mode", f"if({val('manual')}, 'Manual', 'Auto')", display=has("manual")),
            modes,
            _setpoint("ManOut", "manOut", "Manual output (%)", "W14",   # written only in manual (`command`)
                      enabled=f"{_dv('writable', 'manOut')} && {val('manual')}"),
            ] + _limit_block("value") + [_message_line()]

    def history(prop):
        return pv.bind(pv.tag_history("{view.custom.%s}" % prop, "{view.custom.hours}", "HOUR"))

    def drawn(member):
        return pv.bind(pv.expr("{view.custom.trend.%s}" % member))
    chart = trend_chart(history("historyTags"), _limit_series_cfg(), extra=(
        {"name": "sp", "binding": history("historySp"), "axis": "value", "visible": drawn("sp")},
        {"name": "out", "binding": history("historyOut"), "axis": "out", "visible": drawn("out")}))
    chart["propConfig"]["props.plots[0].trends[0].visible"] = drawn("value")
    tuning = _pane("tuning", [
        _section_title("TuningTitle", "TUNING"),
        _setpoint("Gain", "gain", "Gain", "W15", fmt="0.000"),
        _setpoint("Ti", "ti", "Integral time (ms)", "W15", fmt="0"),
        _setpoint("Td", "td", "Derivative time (ms)", "W15", fmt="0")])

    def tags(member):
        return pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
            f"return cadre.hmi.trend_tags(self.session, value, '{member}')"])])
    custom = {"unit": "", "limitRows": [], "hours": 1, "trend": {m: False for m in CONTROLLER_TREND},
              "historyTags": [{"path": "", "alias": "value"}], "historySp": [{"path": "", "alias": "sp"}],
              "historyOut": [{"path": "", "alias": "out"}]}
    custom_cfg = {"custom.unit": UNIT_CFG, "custom.limitRows": _limit_rows_cfg("value"),
                  "custom.trend": pv.bind(pv.expr("{view.params.deviceId}"), [pv.script_transform([
                      f"return cadre.hmi.trended(self.session, value, {list(CONTROLLER_TREND)!r})"])]),
                  "custom.historyTags": tags("value"), "custom.historySp": tags("sp"), "custom.historyOut": tags("out")}
    return _tabbed("controller", rows, custom, custom_cfg,
                   panes={"trend": _pane("trend", [_trend_ranges(), chart]), "tuning": tuning})


def faceplate_tank_tile() -> dict:
    """`Faceplate/TankTile`, stock: the library tank drawn at the faceplate's level. A child built
    with `--render module` overrides it with the module's tank, so the faceplate draws the tank as
    the diagram does (owner's observation, 2026-10-08)."""
    tile = pv.node("ia.display.view", "Tank", pv.fpos(grow=1, basis="0px"), {
        "path": "Automation/Tank", "params": {"max": 100, "unit": "%", "showPercent": False, "value": 0},
        "useDefaultViewHeight": False, "useDefaultViewWidth": False},
        prop_config={"props.params.value": pv.bind(pv.expr("{view.params.level}"))})
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column"},
                   prop_config={"props.style.classes": root_classes()}, children=[tile])
    return pv.view(root, params={"level": 0, "deviceId": ""}, param_dirs={"level": "input", "deviceId": "input"},
                   size={"width": 180, "height": 220})


def faceplate_tank() -> dict:
    """Tank faceplate on the instrument layout (COB-062): Values (the level as a large readout and as
    the library tank tile, the alarm limits `hiLimit` and `loLimit` as setpoints with their state),
    Trend (the level), Alarms."""
    shown, value = _dv("has", "level"), _dv("value", "level")
    level = pv.node("ia.display.label", "Level", pv.fpos(basis="56px", shrink=0), {
        "style": {"classes": "cadre/font/instrument-value-enhanced-active cadre/text/active"}},
        prop_config={"props.text": pv.bind(pv.expr(f"numberFormat({value}, '0.0') + ' %'")),
                     "position.display": pv.bind(pv.expr(shown))})
    tile = pv.node("ia.display.view", "Tile", pv.fpos(basis="220px", shrink=0), {
        "path": "Faceplate/TankTile", "params": {"level": 0, "deviceId": ""},
        "useDefaultViewHeight": False, "useDefaultViewWidth": False,
        "style": {"width": "180px", "alignSelf": "center"}},
        prop_config={"props.params.level": pv.bind(pv.expr(value)),
                     "props.params.deviceId": pv.bind(pv.expr("{view.params.deviceId}")),
                     "position.display": pv.bind(pv.expr(shown))})
    rows = [_section_title("LevelTitle", "LEVEL", display=shown), level, tile] + _limit_block("level")
    return _tabbed("tank", rows, {"limitRows": []}, {"custom.limitRows": _limit_rows_cfg("level")})


def faceplate_empty() -> dict:
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "justify": "center",
                                                      "alignItems": "center", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes()},
                   children=[_label("Hint", pv.fpos(shrink=0), text="Select a device",
                                    classes="cadre/font/body cadre/text/inactive")])
    return pv.view(root, params={"deviceId": "", "tab": ""}, param_dirs={"deviceId": "input", "tab": "input"},
                   size={"width": 400, "height": 200})


def brilliance_menu() -> dict:
    items = [("Day", "day", "palette-day"), ("Dusk", "dusk", "palette-dusk"),
             ("Night", "night", "palette-night"), ("Bright", "bright", "palette-day-bright")]
    kids = []
    for label, key, ic in items:
        kids.append(pv.node("ia.container.flex", f"Palette_{key}", pv.fpos(basis="64px", grow=1), {
            "direction": "column", "alignItems": "center", "justify": "center",
            "style": {"gap": "4px", "cursor": "pointer"}},
            prop_config={"props.style.classes": pv.bind(pv.expr(
                f"if(coalesce({{session.custom.palette}}, 'day') = '{key}', 'cadre/button/selected', 'cadre/button/flat')"))},
            events={"dom": {"onClick": pv.script_handler([f"cadre.hmi.set_palette(self.session, '{key}')"])}},
            children=[icon_svg("Icon", ic, pv.fpos(basis="24px", shrink=0)),
                      _label("Label", pv.fpos(shrink=0), text=label, classes="cadre/font/label")]))
    row = pv.node("ia.container.flex", "Palettes", pv.fpos(basis="72px", shrink=0), {
        "direction": "row", "style": {"gap": "8px"}}, children=kids)
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column",
                                                      "style": {"padding": "12px", "gap": "8px", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/card")},
                   children=[_label("Title", pv.fpos(shrink=0), text="Day/Night",
                                    classes="cadre/font/label cadre/text/neutral"), row])
    return pv.view(root, size={"width": 320, "height": 120})


def user_menu() -> dict:
    who = _label("User", pv.fpos(shrink=0),
                 "if({session.props.auth.authenticated}, {session.props.auth.user.userName}, 'Not signed in')",
                 classes="cadre/font/body-active cadre/text/active")
    sign_in = pv.node("ia.input.button", "SignIn", pv.fpos(basis="40px", shrink=0), {
        "text": "Sign in", "style": {"classes": "cadre/button/raised cadre/font/button"}},
        prop_config={"position.display": pv.bind(pv.expr("!{session.props.auth.authenticated}"))},
        events=pv.on_action(["system.perspective.login()"]))
    sign_out = pv.node("ia.input.button", "SignOut", pv.fpos(basis="40px", shrink=0), {
        "text": "Sign out", "style": {"classes": "cadre/button/normal cadre/font/button"}},
        prop_config={"position.display": pv.bind(pv.expr("{session.props.auth.authenticated}"))},
        events=pv.on_action(["system.perspective.logout()"]))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column",
                                                      "style": {"padding": "12px", "gap": "8px", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/card")},
                   children=[who, sign_in, sign_out])
    return pv.view(root, size={"width": 240, "height": 120})


def alert_menu() -> dict:
    from . import acks   # Ack selected and Ack all under the table (L5)
    tbl = pv.node("ia.display.alarmstatustable", "Alarms", pv.fpos(grow=1), acks.stock_props(),
                  prop_config={"props.filters.active.conditions.source": pv.bind(pv.expr(SCOPE_SOURCE)),
                               **_table_actions()})
    bar = acks.bar(selections=["selected"], can_selected="W7", can_all="W7", path_selected="W7", path_all="W7")
    go = pv.node("ia.input.button", "AllAlerts", pv.fpos(basis="40px", shrink=0), {
        "text": "Alerts ›", "style": {"classes": "cadre/button/flat cadre/font/button"}},
        events=pv.on_action(["system.perspective.closePopup('alertMenu')",
                             "system.perspective.navigate('/alerts')"]))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column",
                                                      "style": {"padding": "8px", "gap": "8px", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/card")},
                   children=[_panel_header("Header", "Alerts", "system.perspective.closePopup('alertMenu')"), tbl] + bar + [go])
    return pv.view(root, size={"width": 640, "height": 468}, custom={"can": dict(CAN_DEFAULT), **acks.custom("selected")},
                   custom_config={"custom.can": CAN_CFG, **acks.stock_config("Alarms")})


def alerts_page() -> dict:
    tabs = [("Active", "active"), ("History", "history")]
    tab_row = pv.node("ia.container.flex", "Tabs", pv.fpos(basis="48px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px", "padding": "0 8px"}},
        children=[pv.node("ia.input.button", f"Tab_{k}", pv.fpos(basis="120px", shrink=0), {
            "text": t, "style": {"classes": "cadre/button/flat cadre/font/button"}},
            prop_config={"props.style.classes": pv.bind(pv.expr(
                f"if({{view.custom.tab}} = '{k}', 'cadre/button/selected cadre/font/button', 'cadre/button/flat cadre/font/button')"))},
            events=pv.on_action([f"self.view.custom.tab = '{k}'"])) for t, k in tabs])
    from . import acks   # Ack selected and Ack all under the active table (L5)
    status = pv.node("ia.display.alarmstatustable", "Status", pv.fpos(grow=1), acks.stock_props(),
                     prop_config={"position.display": pv.bind(pv.expr("{view.custom.tab} = 'active'")),
                                  "props.filters.active.conditions.source": pv.bind(pv.expr(SCOPE_SOURCE)),
                                  **_table_actions()})
    journal = pv.node("ia.display.alarmjournaltable", "Journal", pv.fpos(grow=1), {},
                      prop_config={"position.display": pv.bind(pv.expr("{view.custom.tab} = 'history'"))})
    bar = acks.bar(selections=["selected"], can_selected="W7", can_all="W7", path_selected="W7", path_all="W7",
                   display="{view.custom.tab} = 'active'")
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column",
                                                      "style": {"padding": "8px", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")},
                   children=[tab_row, status] + bar + [journal, search_panel()])
    return pv.view(root, size={"width": 1600, "height": 852},
                   custom={"tab": "active", "can": dict(CAN_DEFAULT), **acks.custom("selected")},
                   custom_config={"custom.can": CAN_CFG, **acks.stock_config("Status")})


def framework_views() -> dict[str, dict]:
    from . import devices_asm   # imports this module: imported here, when the views are built (COB-158)
    return {
        "Framework/TopBar": top_bar(), "Framework/NavMenu": nav_menu(),
        "Framework/NavItem": nav_item(), "Framework/SideMenu": side_menu(),
        "Framework/BrillianceMenu": brilliance_menu(), "Framework/UserMenu": user_menu(),
        "Framework/AlertMenu": alert_menu(), "Framework/AlertsPage": alerts_page(),
        "Framework/Badges": badges(), "Framework/Crumb": crumb(),
        FACEPLATE_POPUP_VIEW: faceplate_popup(),
        "Faceplate/Pump": faceplate("pump"), "Faceplate/Valve": faceplate("valve"),
        **{view: faceplate(view.split("/")[-1].lower(), "asm") for view in sorted(set(ASM_VIEW.values()))
           if view not in ASM_BUILT},
        **devices_asm.views(),
        "Faceplate/Tank": faceplate_tank(), "Faceplate/Empty": faceplate_empty(),
        "Faceplate/Alarms": faceplate_alarms(), "Faceplate/InterlockRow": faceplate_interlock_row(),
        "Faceplate/Instrument": faceplate_instrument(), "Faceplate/LimitRow": faceplate_limit_row(),
        "Faceplate/TankTile": faceplate_tank_tile(), "Faceplate/SetpointRow": faceplate_setpoint_row(),
        "Faceplate/Controller": faceplate_controller(), "Faceplate/Input": faceplate_input(),
        "Faceplate/Sequence": faceplate_sequence(),
        "Trend/Card": trend_card(), "Framework/TrendsPage": trends_page(),
    }


def shared_docks(app_name: str = "App") -> dict:
    """Page configuration `sharedDocks`: the frame every page shares. Dock keys follow the
    shape the 8.3 page configuration resource uses (observed in the vendor demo's
    page-config and in this gateway's own projects)."""
    def dock(id_, view, size, show, content, params=None, breakpoint=480, modal=False):
        return {"anchor": "fixed", "autoBreakpoint": breakpoint, "content": content, "handle": "hide",
                "iconUrl": "", "id": id_, "modal": modal, "resizable": False, "show": show,
                "size": size, "viewParams": params or {}, "viewPath": view}
    # The navigation menu is modal: a click outside it lands on the dock's overlay and closes it (GF-71). The
    # faceplate dock is not, since the operator opens one device after another from the page beside it.
    return {"cornerPriority": "top-bottom",
            "top": [dock("topbar", "Framework/TopBar", 48, "visible", "push",
                         {"appName": app_name, "showUser": True, "clockLabel": "UTC"})],
            "left": [dock(NAV_DOCK, "Framework/NavMenu", 320, "onDemand", "cover", breakpoint=768, modal=True)],
            "right": [dock(FACEPLATE_DOCK, "Framework/SideMenu", 400, "onDemand", "push")]}
