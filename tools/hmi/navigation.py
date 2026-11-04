"""The ASM frame (COB-160): navigation dock, crumb popup, global search, page header, alarm banner and the
floating faceplates, switched on per child by `screen.py --frame asm` (the default frame is unchanged).

The views are part of the parent (`views()`, written by `parent.py`) and cost a child nothing until its page
configuration names them: `page_config` writes the ASM docks for a child built with `--frame asm`, and
`session_custom` writes the data the views read (the page information, the search index, the frame flag).
The scripts the views call are `cadre.hmi.*` functions of `navigation_scripts.py`.

Everything is stock Perspective: docks (IGW:11-navigation-and-pages section 3: `top`, `left`, `right` and
`bottom` edges, several docks to an edge), popups opened with the keywords the corpus shows (IGW:23-perspective-
scripting sections 4 and 5), flex repeaters, the text field with a bidirectional property binding
(IGW:components ia.input.text-field section 5.9) and the alarm status table of the faceplate and alerts pages.

Design: `projects/eng02/work/asm/DESIGN.md` sections 3 to 6 (local only), gaps GX-02, GX-09 and GX-10.
"""
from __future__ import annotations

import copy

from . import framework, library, pv, scripts
from .framework import (SEARCH_VIEW, search_panel, _badges_embed, _icon_button, _label, _pin_button, _table_actions, CAN_CFG, CAN_DEFAULT,
                        FACEPLATE_HEIGHT, FACEPLATE_OF_SELECTION, NAV_DOCK, NO_COUNTS, POPUP_SIZE, TABLE_PROPS,
                        root_classes)
from .library import icon_svg, open_device, svg

FRAMES = ("openbridge", "asm", "ob", "obasm")   # ob, obasm: the module frame components (obframe.py, obasm.py); need --render module
ASM_FRAMES = ("asm", "obasm")   # the frames that carry the ASM rules: the hierarchy, the pivot pages, search, banner, floating faceplates
MODULE_FRAMES = ("ob", "obasm")   # the frames drawn with the module's components
FLOAT_VIEW = "Framework/ASM/FloatFaceplate"
CRUMB_POPUP = "crumbPopup"
# a row's `close` that means the in-page search panel (L4): the query is cleared and the panel closes
SEARCH_CLOSE = "search"
SEARCH_OPEN, SEARCH_QUERY = "self.session.custom.searchOpen", "self.session.custom.searchQuery"
# the two lists of the one navigation dock (`session.custom.navPanel`): the page tree, and the support pages
NAV_PAGES, NAV_SUPPORT = "pages", "support"
NODE_ALARMS_ROUTE, NODE_TREND_ROUTE = "/node/alarms", "/node/trend"
PAGE_HEADER_DOCK, BANNER_DOCK = "pageheader", "alarmbanner"
HEADER_HEIGHT, BANNER_HEIGHT, SEARCH_WIDTH = 36, 76, 300
# the tab a tag opens its device's faceplate on (DESIGN section 5): a tag that raises alarms the Alarms tab,
# a configuration member (`cfg/`) the Config tab, an interlock member (`ilk/`) the Interlock tab, else Home
TAG_TABS = (("cfg/", "config"), ("ilk/", "interlocks"), ("mnt/", "config"))
ROW_PARAMS = {**scripts.constant("ROW_DEFAULT"), "counts": dict(NO_COUNTS)}   # the keys `cadre.hmi._row` writes
HEAD_DEFAULT = {"title": "", "level": "", "nodeId": "", "mode": "mimic", "mimicRoute": "", "tabs": [],
                "previous": {"route": "", "title": "", "enabled": False},
                "next": {"route": "", "title": "", "enabled": False}}
BANNER_DEFAULT = {"rows": [], "counts": dict(NO_COUNTS)}


# ---------------------------------------------------------------------------------------------------------
# Row actions: one script serves a list row's click and the search field's Enter
# ---------------------------------------------------------------------------------------------------------
def action_lines(get, indent: str = "") -> list[str]:
    """The lines of a row's action. `get(field)` names a field of the row in the script (`p.route`, or
    `r['route']`). The row navigates to its route, or to the Alarms or Trend pivot page of its node
    (`session.custom.contentNode`), then opens its device's faceplate on the row's tab through
    `library.open_device` (the shared opener of COB-158 to COB-160), then closes what it came from."""
    ind = indent
    out = [f"{ind}if {get('action')} == 'alarms' or {get('action')} == 'trend':",
           f"{ind}\tself.session.custom.contentNode = {get('nodeId')}",
           f"{ind}\tsystem.perspective.navigate('/node/' + {get('action')})",
           f"{ind}elif {get('route')}:",
           f"{ind}\tsystem.perspective.navigate({get('route')})",
           f"{ind}if {get('deviceId')}:"]
    out += open_device(get("deviceId"), get("deviceKind"), get("deviceTitle"), get("deviceLabel"), get("tab"),
                       indent=ind + "\t")
    out += [f"{ind}if {get('close')} == '{NAV_DOCK}':",
            f"{ind}	system.perspective.closeDock('{NAV_DOCK}')",
            f"{ind}elif {get('close')} == '{SEARCH_CLOSE}':",
            f"{ind}	{SEARCH_QUERY} = ''",
            f"{ind}	{SEARCH_OPEN} = False",
            f"{ind}elif {get('close')}:",
            f"{ind}	system.perspective.closePopup({get('close')})"]
    return out


def _popup_line(popup_id: str, view: str, params: str, position: str) -> str:
    """A frame popup opens modal: a non-modal popup does not close on a click outside it, whatever its
    `overlayDismiss` (measured on 8.3.6, 2026-10-24), and a modal one does (L4)."""
    return (f"system.perspective.openPopup(id='{popup_id}', view='{view}', params={params}, position={position}, "
            "showCloseIcon=False, draggable=False, modal=True, overlayDismiss=True)")


# ---------------------------------------------------------------------------------------------------------
# The list row, shared by the navigation dock, the crumb popup and the search popup
# ---------------------------------------------------------------------------------------------------------
def _icon_node(name: str, pos: dict, icon_expr: str) -> dict:
    return pv.node("ia.shapes.svg", name, pos, {"viewBox": "0 0 24 24", "elements": [], "style": {"height": "20px"}},
                   prop_config={"props.elements": pv.bind(pv.expr(icon_expr), [pv.script_transform([
                       "return cadre.icons.elements(value)"])]),
                                "position.display": pv.bind(pv.expr(f"len({icon_expr}) > 0"))})


def list_row() -> dict:
    """`Framework/ASM/ListRow`: one row of a list of the frame (`ROW_PARAMS`). A `group` row is a title; a
    `node`, `page`, `show`, `area`, `device` or `tag` row is a button that runs `action_lines`; a disabled row
    does nothing. Depth indents; the counts draw the node's badges; a second line says where the row is."""
    p = "{view.params.%s}"
    icon = _icon_node("Icon", pv.fpos(basis="20px", shrink=0), "{view.params.icon}")
    texts = pv.node("ia.container.flex", "Texts", pv.fpos(grow=1, basis="0px"), {
        "direction": "column", "justify": "center", "style": {"overflow": "hidden"}}, children=[
        pv.node("ia.display.label", "Label", pv.fpos(shrink=0), {
            "style": {"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"}},
            prop_config={"props.text": pv.bind(pv.expr(p % "label")),
                         "props.style.classes": pv.bind(pv.expr(
                             "if({view.params.kind} = 'group', 'cadre/font/overline cadre/text/neutral', "
                             "if({view.params.disabled}, 'cadre/font/body cadre/text/neutral', "
                             "'cadre/font/body-active cadre/text/active'))"))}),
        pv.node("ia.display.label", "Second", pv.fpos(shrink=0), {
            "style": {"classes": "cadre/font/label cadre/text/neutral", "whiteSpace": "nowrap", "overflow": "hidden",
                      "textOverflow": "ellipsis"}},
            prop_config={"props.text": pv.bind(pv.expr(p % "second")),
                         "position.display": pv.bind(pv.expr("len({view.params.second}) > 0"))})])
    badges = _badges_embed(pv.fpos(basis="120px", shrink=0))
    badges["propConfig"]["position.display"] = pv.bind(pv.expr(
        "{view.params.kind} != 'group' && {view.params.counts.total} > 0"))
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "row", "alignItems": "center", "style": {"gap": "10px", "overflow": "hidden", "padding": "0 8px"}},
        prop_config={"props.style.classes": pv.bind(pv.expr(
            "if({view.params.kind} = 'group', 'cadre/divider/bottom', "
            "if({view.params.selected}, 'cadre/nav/item-selected', 'cadre/nav/item cadre/text/active'))")),
                     "props.style.paddingLeft": pv.bind(pv.expr("toStr(8 + 16 * {view.params.depth}) + 'px'"))},
        events={"dom": {"onClick": pv.script_handler([
            "p = self.view.params",
            "if p.kind != 'group' and not p.disabled:",
            *action_lines(lambda f: "p." + f, "\t")])}},
        children=[icon, texts, badges])
    return pv.view(root, params=copy.deepcopy(ROW_PARAMS), param_dirs={k: "input" for k in ROW_PARAMS},
                   size={"width": 304, "height": 44})


def _rows_repeater(name: str, pos: dict, instances_cfg: dict, basis: str = "44px", direction: str = "column",
                   extra_style: dict | None = None) -> dict:
    return pv.node("ia.display.flex-repeater", name, pos, {
        "path": "Framework/ASM/ListRow", "direction": direction, "useDefaultViewHeight": False,
        "useDefaultViewWidth": False, "elementPosition": {"basis": basis, "shrink": 0}, "instances": [],
        "style": {"gap": "2px", "overflow": "auto", **(extra_style or {})}},
        prop_config={"props.instances": instances_cfg})


def _polled(value_expr: str, script: str) -> dict:
    """A binding that re-runs `script` (a `cadre.hmi` call on `value`) each 2 s and when `value_expr` changes."""
    return pv.bind(pv.expr(f"if(toMillis(now(2000)) > 0, {value_expr}, '')"), [pv.script_transform([script])])


# ---------------------------------------------------------------------------------------------------------
# The navigation dock (DESIGN section 3)
# ---------------------------------------------------------------------------------------------------------
def nav_dock() -> dict:
    """`Framework/ASM/NavDock`: the one left dock, in two states (`session.custom.navPanel`, L4). `pages`, which
    the top bar's menu button opens, is for navigation only: a header with close, a search box that turns the
    tree into a flat list of the matching nodes and pages, and the tree (nodes with badges, pages beneath, the
    current page selected). `support`, which the second button opens, lists the support pages: all alarms,
    trends, tools, alerts. Closes on a selection (the row's `close`), on Escape and on a click outside (the
    dock's own behaviour, modal)."""
    pages = f"coalesce({{session.custom.navPanel}}, '{NAV_PAGES}') != '{NAV_SUPPORT}'"
    support = f"coalesce({{session.custom.navPanel}}, '{NAV_PAGES}') = '{NAV_SUPPORT}'"
    title = _label("Title", pv.fpos(grow=1), text="Navigation", classes="cadre/font/title cadre/text/active")
    title["propConfig"] = {"props.text": pv.bind(pv.expr(f"if({support}, 'Tools and support', 'Navigation')"))}
    head = pv.node("ia.container.flex", "Header", pv.fpos(basis="56px", shrink=0), {
        "direction": "row", "alignItems": "center",
        "style": {"classes": "cadre/divider/bottom", "padding": "0 8px 0 16px"}},
        children=[title,
                  _icon_button("Close", "close-google", {"dom": {"onClick": pv.script_handler([
                      f"system.perspective.closeDock('{NAV_DOCK}')"])}})])
    box = pv.node("ia.input.text-field", "Search", pv.fpos(basis="36px", shrink=0), {
        "placeholder": "Search pages and areas", "deferUpdates": False, "rejectUpdatesWhileFocused": False,
        "text": "", "style": {"margin": "8px 8px 4px 8px"}},
        prop_config={"props.text": pv.bind(pv.prop("session.custom.navQuery", True)),
                     "position.display": pv.bind(pv.expr(pages))})
    tree_cfg = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {page.props.path} + '|' + coalesce({session.custom.navQuery}, ''), '')"),
                       [pv.script_transform(["parts = (value or '').split('|', 1)",
                                             "return cadre.hmi.nav_tree(self.session, parts[1] if len(parts) > 1 else '', parts[0])"])])
    support_cfg = _polled("{page.props.path}", "return cadre.hmi.nav_support(self.session, value)")
    tree = _rows_repeater("Tree", pv.fpos(grow=1, basis="0px"), tree_cfg)
    tree["propConfig"]["position.display"] = pv.bind(pv.expr(pages))
    sup = _rows_repeater("Support", pv.fpos(grow=1, basis="0px"), support_cfg)
    sup["propConfig"]["position.display"] = pv.bind(pv.expr(support))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"padding": "0 0 8px 0", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/menu")},
                   children=[head, box, tree, sup])
    return pv.view(root, size={"width": 320, "height": 800})


# ---------------------------------------------------------------------------------------------------------
# The breadcrumb and its popup (DESIGN section 4)
# ---------------------------------------------------------------------------------------------------------
def crumb(top: int = 48) -> dict:
    """`Framework/ASM/Crumb`: one node of the trail. A click opens the node's popup beneath the crumb (`top`: the page row of the crumb's lower edge)."""
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "row", "alignItems": "center", "style": {"gap": "6px", "overflow": "hidden", "cursor": "pointer"}},
        events={"dom": {"onClick": pv.script_handler([
            "x = 0",
            "try:",
            "\tx = int(event.clientX)",
            "except Exception:",
            "\tx = 48",
            f"system.perspective.closePopup('{CRUMB_POPUP}')",
            _popup_line(CRUMB_POPUP, "Framework/ASM/CrumbPopup", "{'nodeId': self.view.params.nodeId}",
                        f"{{'top': {top}, 'left': max(0, x - 24)}}")])}},
        children=[icon_svg("Chevron", "chevron-right-google", pv.fpos(basis="16px", shrink=0), visible="!{view.params.first}"),
                  _label("Name", pv.fpos(shrink=1), "{view.params.name}", classes="cadre/font/body-active cadre/text/active",
                         style={"overflow": "hidden", "textOverflow": "ellipsis"}),
                  _badges_embed(pv.fpos(basis="0px", grow=1))])
    params = {"name": "", "route": "", "nodeId": "", "counts": dict(NO_COUNTS), "first": True, "last": False}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params}, size={"width": 220, "height": 40})


def crumb_popup() -> dict:
    """`Framework/ASM/CrumbPopup`: Show (Mimic, Alarms, Trend of the node) and Areas (its child nodes)."""
    rows = _rows_repeater("Rows", pv.fpos(grow=1, basis="0px"), pv.bind(pv.expr("{view.custom.rows}")))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"padding": "4px", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/card")}, children=[rows])
    return pv.view(root, params={"nodeId": ""}, param_dirs={"nodeId": "input"}, size={"width": 320, "height": 360},
                   custom={"rows": []}, custom_config={"custom.rows": _polled(
                       "{view.params.nodeId}", "return cadre.hmi.crumb_menu(self.session, value)")})


# ---------------------------------------------------------------------------------------------------------
# The global search (DESIGN section 5)
# ---------------------------------------------------------------------------------------------------------
SEARCH_PANEL_WIDTH, SEARCH_PANEL_HEIGHT = 420, 480


def search_results() -> dict:
    """`Framework/ASM/SearchResults`: the results of the top bar's field, in the page (L4). The view fills the page
    it is embedded in (`search_panel`) and draws nothing but the panel, 420 px wide at its top right corner; the
    transparent regions to the left of the panel and beneath it close the panel on a click, so that a click on the
    page outside the panel closes it. A click on a row acts and closes (the row's `close`). The rows follow the
    field only while the panel is open, so that a closed panel costs no search."""
    close = pv.script_handler([f"{SEARCH_OPEN} = False"])
    rows = _rows_repeater("Rows", pv.fpos(grow=1, basis="0px"), pv.bind(pv.expr("{view.custom.rows}")), basis="48px")
    empty = _label("Empty", pv.fpos(basis="40px", shrink=0), text="No page, device or tag matches",
                   classes="cadre/font/label cadre/text/neutral", style={"padding": "0 12px"},
                   visible="len({view.custom.rows}) = 0 && len(coalesce({session.custom.searchQuery}, '')) > 0")
    panel = pv.node("ia.container.flex", "Panel", pv.fpos(basis=f"{SEARCH_PANEL_WIDTH}px", shrink=0), {
        "direction": "column", "style": {"padding": "4px", "overflow": "hidden", "margin": "4px 8px 0 0"}},
        prop_config={"props.style.classes": root_classes("cadre/surface/card")}, children=[rows, empty])
    left = pv.node("ia.container.flex", "ScrimLeft", pv.fpos(grow=1, basis="0px"), {}, events={"dom": {"onClick": close}})
    top = pv.node("ia.container.flex", "PanelRow", pv.fpos(basis=f"{SEARCH_PANEL_HEIGHT}px", shrink=1), {
        "direction": "row"}, children=[left, panel])
    below = pv.node("ia.container.flex", "ScrimBelow", pv.fpos(grow=1, basis="0px"), {}, events={"dom": {"onClick": close}})
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes()}, children=[top, below])
    cfg = pv.bind(pv.expr("if(coalesce({session.custom.searchOpen}, false), coalesce({session.custom.searchQuery}, ''), '')"),
                  [pv.script_transform(["return cadre.hmi.search(self.session, value)"])])
    return pv.view(root, size={"width": 1600, "height": 788}, custom={"rows": []}, custom_config={"custom.rows": cfg})


def _search_field() -> dict:
    """The 300 px field of the top bar. It opens no popup (a popup took the keyboard focus, and only the first
    character landed): the text goes to `session.custom.searchQuery` at each key (`deferUpdates` false), a key
    opens the results panel of the page (`session.custom.searchOpen`), Enter acts on the first row, Escape
    clears the field and closes the panel, and a click on the field opens the panel again where a query is
    left. A change of the text that brings no key event (a paste, measured on the glass 2026-10-24) opens the
    panel through the text's change script."""
    click = [f"if len({SEARCH_QUERY} or '') > 0:",
             f"	{SEARCH_OPEN} = True"]
    keys = ["k = ''",
            "try:",
            "	k = event.key",
            "except Exception:",
            "	k = ''",
            "if k == 'Escape':",
            f"	{SEARCH_QUERY} = ''",
            f"	{SEARCH_OPEN} = False",
            "elif k == 'Enter':",
            f"	r = cadre.hmi.search_first(self.session, {SEARCH_QUERY})",
            "	if r is not None:",
            *action_lines(lambda f: f"r['{f}']", "		"),
            "else:",
            f"	{SEARCH_OPEN} = True"]
    return pv.node("ia.input.text-field", "SearchField", pv.fpos(basis=f"{SEARCH_WIDTH}px", shrink=0), {
        "placeholder": "Search pages, devices, tags", "deferUpdates": False, "rejectUpdatesWhileFocused": False,
        "text": "", "style": {"height": "32px", "margin": "0 8px"}},
        prop_config={"props.text": {**pv.bind(pv.prop("session.custom.searchQuery", True)), "onChange": {
            "enabled": None, "script": f"\tif currentValue is not None and currentValue.value:\n\t\t{SEARCH_OPEN} = True"}}},
        events={"dom": {"onClick": pv.script_handler(click), "onKeyDown": pv.script_handler(keys)}})


# ---------------------------------------------------------------------------------------------------------
# The top bar (DESIGN section 3 item 1)
# ---------------------------------------------------------------------------------------------------------
CRUMBS_ASM_CFG = pv.bind(pv.expr(
    "if(toMillis(now(2000)) > 0, {page.props.path} + '|' + coalesce({session.custom.contentNode}, ''), '')"), [
    pv.script_transform(["return cadre.hmi.frame_crumbs(self.session, (value or '').split('|')[0])"])])


SUPPORT_ICON = "dashboard"   # the nearest of the library's icons to the package's `apps`


def _open_nav(panel: str) -> list[str]:
    """The lines of a top bar button that opens the one navigation dock on `panel`."""
    return [f"self.session.custom.navPanel = '{panel}'", f"system.perspective.openDock(id='{NAV_DOCK}')"]


def top_bar() -> dict:
    """`Framework/ASM/TopBar`: the library's top bar with the trail of crumbs that open their popups, the
    300 px search field before the alarm summary, and the site note beneath the application's name. The menu
    button opens the navigation dock on the page tree and a second button, beside it, on the support pages
    (`session.custom.navPanel`). The alarm summary, the alert menu, the brilliance and user buttons and the
    clock are the library's own."""
    doc = framework.top_bar()
    kids = doc["root"]["children"]
    by = {k["meta"]["name"]: i for i, k in enumerate(kids)}
    app = kids[by["AppName"]]
    kids[by["AppName"]] = pv.node("ia.container.flex", "Titles", pv.fpos(shrink=0), {
        "direction": "column", "justify": "center", "style": {"marginLeft": "8px"}}, children=[
        _label("AppName", pv.fpos(shrink=0), "{view.params.appName}", classes=app["props"]["style"]["classes"]),
        _label("SiteNote", pv.fpos(shrink=0), "{view.params.siteNote}", classes="cadre/font/label cadre/text/neutral",
               visible="len(coalesce({view.params.siteNote}, '')) > 0")])
    trail = kids[by["Crumbs"]]
    trail["props"]["path"] = "Framework/ASM/Crumb"
    kids.insert(by["Spacer"] + 1, _search_field())
    kids[by["MenuButton"]] = _icon_button("MenuButton", "menu", {"dom": {"onClick": pv.script_handler(
        _open_nav(NAV_PAGES))}})
    kids.insert(by["MenuButton"] + 1, _icon_button("SupportButton", SUPPORT_ICON, {"dom": {"onClick": pv.script_handler(
        _open_nav(NAV_SUPPORT))}}))
    doc["params"]["siteNote"] = ""
    doc["propConfig"]["params.siteNote"] = {"paramDirection": "input", "persistent": True}
    doc["propConfig"]["custom.crumbs"] = CRUMBS_ASM_CFG
    return doc


TOP_BAR_HEIGHT = 48


def head() -> dict:
    """`Framework/ASM/Head`: the top bar above the page header, in the one top dock. The gateway draws one
    dock of a side at a time (measured on 8.3.6, 2026-10-24: of two top docks both `visible`, only the first
    showed), so the two rows share a dock of 84 px. The dock's parameters pass to the top bar."""
    params = dict(top_bar()["params"])   # the ASM top bar adds siteNote
    bar = pv.node("ia.display.view", "TopBar", pv.fpos(basis=f"{TOP_BAR_HEIGHT}px", shrink=0), {
        "path": "Framework/ASM/TopBar", "params": dict(params), "useDefaultViewHeight": False,
        "useDefaultViewWidth": False},
        prop_config={f"props.params.{k}": pv.bind(pv.expr(f"{{view.params.{k}}}")) for k in params})
    header = pv.node("ia.display.view", "PageHeader", pv.fpos(basis=f"{HEADER_HEIGHT}px", shrink=0), {
        "path": "Framework/ASM/PageHeader", "params": {}, "useDefaultViewHeight": False, "useDefaultViewWidth": False})
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   children=[bar, header])
    return pv.view(root, params=params, param_dirs={k: "input" for k in params},
                   size={"width": 1600, "height": TOP_BAR_HEIGHT + HEADER_HEIGHT})


# ---------------------------------------------------------------------------------------------------------
# The page header (DESIGN section 3 item 2; GX-09)
# ---------------------------------------------------------------------------------------------------------
def page_tab() -> dict:
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "row", "alignItems": "center", "justify": "center", "style": {"padding": "0 12px", "cursor": "pointer"}},
        prop_config={"props.style.classes": pv.bind(pv.expr(
            "if({view.params.selected}, 'cadre/button/selected', 'cadre/button/flat')"))},
        events={"dom": {"onClick": pv.script_handler([
            "if self.view.params.route:",
            "\tsystem.perspective.navigate(self.view.params.route)"])}},
        children=[_label("Label", pv.fpos(shrink=0), "{view.params.label}", classes="cadre/font/button")])
    params = {"label": "", "route": "", "selected": False}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params}, size={"width": 160, "height": 32})


def page_header() -> dict:
    """`Framework/ASM/PageHeader`: 36 px under the top bar. The page title and its display level; the pivot
    Mimic, Alarms and Trend of the page's node (Alarms and Trend are the pages `/node/alarms` and
    `/node/trend` over `session.custom.contentNode`); the node's pages as tabs where it has several; and the
    previous and next pages, disabled where the descriptor names none."""
    def pivot(mode, text, lines):
        return pv.node("ia.input.button", f"Pivot_{mode}", pv.fpos(basis="84px", shrink=0), {
            "text": text, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "28px", "margin": "0 2px"}},
            prop_config={"props.style.classes": pv.bind(pv.expr(
                f"if({{view.custom.head.mode}} = '{mode}', 'cadre/button/selected cadre/font/button', "
                "'cadre/button/flat cadre/font/button')")),
                         "props.enabled": pv.bind(pv.expr(
                             "len({view.custom.head.mimicRoute}) > 0" if mode == "mimic" else "true"))},
            events=pv.on_action(lines))
    pv_box = pv.node("ia.container.flex", "Pivot", pv.fpos(basis="268px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"marginLeft": "16px"}},
        prop_config={"position.display": pv.bind(pv.expr("len({view.custom.head.nodeId}) > 0"))},
        children=[pivot("mimic", "Mimic", ["if self.view.custom.head.mimicRoute:",
                                           "\tsystem.perspective.navigate(self.view.custom.head.mimicRoute)"]),
                  pivot("alarms", "Alarms", ["self.session.custom.contentNode = self.view.custom.head.nodeId",
                                             f"system.perspective.navigate('{NODE_ALARMS_ROUTE}')"]),
                  pivot("trend", "Trend", ["self.session.custom.contentNode = self.view.custom.head.nodeId",
                                           f"system.perspective.navigate('{NODE_TREND_ROUTE}')"])])
    tabs = pv.node("ia.display.flex-repeater", "Tabs", pv.fpos(shrink=1), {
        "path": "Framework/ASM/PageTab", "direction": "row", "useDefaultViewHeight": False, "useDefaultViewWidth": True,
        "elementPosition": {"shrink": 0}, "instances": [], "style": {"marginLeft": "16px", "gap": "4px"}},
        prop_config={"props.instances": pv.bind(pv.expr("{view.custom.head.tabs}")),
                     "position.display": pv.bind(pv.expr("len({view.custom.head.tabs}) > 0"))})

    def step(name, key, glyph_first):
        text = (f"if({{view.custom.head.{key}.enabled}}, '‹ ' + {{view.custom.head.{key}.title}}, '‹')"
                if glyph_first else
                f"if({{view.custom.head.{key}.enabled}}, {{view.custom.head.{key}.title}} + ' ›', '›')")
        return pv.node("ia.input.button", name, pv.fpos(basis="200px", shrink=1), {
            "text": "", "style": {"classes": "cadre/button/flat cadre/font/button", "height": "28px", "margin": "0 2px",
                                  "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"}},
            prop_config={"props.text": pv.bind(pv.expr(text)),
                         "props.enabled": pv.bind(pv.expr(f"{{view.custom.head.{key}.enabled}}"))},
            events=pv.on_action([f"if self.view.custom.head.{key}.route:",
                                 f"\tsystem.perspective.navigate(self.view.custom.head.{key}.route)"]))
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "row", "alignItems": "center", "style": {"padding": "0 8px", "overflow": "hidden"}},
        prop_config={"props.style.classes": root_classes("cadre/surface/bar cadre/divider/bottom")},
        children=[_label("Title", pv.fpos(shrink=0), "{view.custom.head.title}", classes="cadre/font/body-active cadre/text/active",
                         style={"marginLeft": "8px"}),
                  _label("Level", pv.fpos(shrink=0), "{view.custom.head.level}", classes="cadre/font/label cadre/text/neutral",
                         style={"marginLeft": "12px"}, visible="len({view.custom.head.level}) > 0"),
                  pv_box, tabs, pv.node("ia.container.flex", "Spacer", pv.fpos(grow=1), {}),
                  step("Previous", "previous", True), step("Next", "next", False)])
    cfg = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {page.props.path} + '|' + coalesce({session.custom.contentNode}, ''), '')"),
                  [pv.script_transform(["return cadre.hmi.page_header(self.session, (value or '').split('|')[0])"])])
    return pv.view(root, size={"width": 1600, "height": HEADER_HEIGHT}, custom={"head": copy.deepcopy(HEAD_DEFAULT)},
                   custom_config={"custom.head": cfg})


# ---------------------------------------------------------------------------------------------------------
# The bottom alarm banner (DESIGN section 3 item 4; GX-10)
# ---------------------------------------------------------------------------------------------------------
BANNER_ROW_PARAMS = {"id": "", "priority": "", "status": "neutral", "unacked": False, "time": "", "node": "", "tag": "",
                     "text": "", "state": "", "deviceId": "", "deviceKind": "", "deviceTitle": "", "deviceLabel": ""}


def banner_row() -> dict:
    """`Framework/ASM/BannerRow`: priority icon (the package shapes by rank, flashing while unacknowledged),
    time, node, device tag, description and state. A click opens the device's faceplate on Alarms."""
    st = "{view.params.status}"
    icons = []
    for k, d in {"alarm": "M8 1L15 14H1Z", "critical": "M8 1L15 14H1Z", "warning": library.circle_d(8, 8, 7),
                 "caution": "M1.5 1.5H14.5V14.5H1.5Z", "neutral": library.circle_d(8, 8, 6)}.items():
        paint = "var(--element-neutral-color)" if k == "neutral" else f"var({library.ALERT_COLOURS[k]})"
        icons.append(svg(f"Priority_{k}", pv.fpos(basis="18px", shrink=0), [
            {"type": "path", "name": "shape", "d": d, "fill": {"paint": paint}}], view_box="0 0 16 16",
            visible=f"{st} = '{k}'",
            extra_config={"props.style.classes": pv.bind(pv.expr(
                f"if({{view.params.unacked}}, 'cadre/alert/flash-' + if({st} = 'neutral', 'caution', {st}), '')"))}))

    def cell(name, key, basis=None, grow=None, cls="cadre/font/body cadre/text/active"):
        return _label(name, pv.fpos(basis=basis, grow=grow, shrink=0 if basis else 1), f"{{view.params.{key}}}", classes=cls,
                      style={"overflow": "hidden", "textOverflow": "ellipsis"})
    root = pv.node("ia.container.flex", "root", {}, {
        "direction": "row", "alignItems": "center", "style": {"gap": "10px", "padding": "0 8px", "cursor": "pointer"}},
        events={"dom": {"onClick": pv.script_handler([
            "p = self.view.params",
            "if p.deviceId:",
            *open_device("p.deviceId", "p.deviceKind", "p.deviceTitle", "p.deviceLabel", "'alarms'", indent="\t")])}},
        children=[*icons, cell("Time", "time", "72px", cls="cadre/font/label cadre/text/neutral"),
                  cell("Node", "node", "120px", cls="cadre/font/label cadre/text/neutral"),
                  cell("Tag", "tag", "140px", cls="cadre/font/body-active cadre/text/active"),
                  cell("Text", "text", grow=1), cell("State", "state", "170px", cls="cadre/font/label cadre/text/neutral")])
    return pv.view(root, params=copy.deepcopy(BANNER_ROW_PARAMS), param_dirs={k: "input" for k in BANNER_ROW_PARAMS},
                   size={"width": 1200, "height": 24})


def alarm_banner() -> dict:
    """`Framework/ASM/AlarmBanner`: 76 px at the bottom. The three most important alarms of the open page's node and
    the nodes beneath it (the whole alarm scope on a page that names no node; L5) at the left; at the right the counts by priority and All alarms (the Alarms pivot page of the root node)."""
    rows = pv.node("ia.display.flex-repeater", "Rows", pv.fpos(grow=1, basis="0px"), {
        "path": "Framework/ASM/BannerRow", "direction": "column", "useDefaultViewHeight": False,
        "useDefaultViewWidth": False, "elementPosition": {"basis": "24px", "shrink": 0}, "instances": [],
        "style": {"overflow": "hidden"}},
        prop_config={"props.instances": pv.bind(pv.expr("{view.custom.banner.rows}"))})
    none = _label("None", pv.fpos(basis="24px", shrink=0), text="No active alarms", classes="cadre/font/label cadre/text/neutral",
                  style={"padding": "0 8px"}, visible="len({view.custom.banner.rows}) = 0")
    left = pv.node("ia.container.flex", "Left", pv.fpos(grow=1, basis="0px", align="stretch"),   # full height (2026-10-24)
                   {"direction": "column", "justify": "center"},
                   children=[rows, none])
    counts = pv.node("ia.display.view", "Counts", pv.fpos(basis="160px", shrink=0), {
        "path": "Framework/Badges", "params": {"counts": dict(NO_COUNTS)}, "useDefaultViewHeight": False,
        "useDefaultViewWidth": False},
        prop_config={"props.params.counts": pv.bind(pv.expr("{view.custom.banner.counts}"))})
    all_alarms = pv.node("ia.input.button", "AllAlarms", pv.fpos(basis="110px", shrink=0), {
        "text": "All alarms", "style": {"classes": "cadre/button/normal cadre/font/button", "height": "32px", "margin": "0 8px"}},
        events=pv.on_action(["if len(self.session.custom.hierarchy) > 0:",
                             "\tself.session.custom.contentNode = ''",
                             f"\tsystem.perspective.navigate('{NODE_ALARMS_ROUTE}')",
                             "else:",
                             "\tsystem.perspective.navigate('/alerts')"]))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "row", "alignItems": "center",
                                                      "style": {"overflow": "hidden", "padding": "0 4px"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/bar")},
                   children=[left, counts, all_alarms])
    return pv.view(root, size={"width": 1600, "height": BANNER_HEIGHT}, custom={"banner": copy.deepcopy(BANNER_DEFAULT)},
                   custom_config={"custom.banner": pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {page.props.path}, '')"), [
                       pv.script_transform(["return cadre.hmi.banner_alarms(self.session, value)"])])})


# ---------------------------------------------------------------------------------------------------------
# Several floating faceplates (DESIGN section 6, float mode)
# ---------------------------------------------------------------------------------------------------------
FLOAT_PARAMS = {"popupId": "", "deviceId": "", "kind": "", "style": "openbridge", "title": "", "label": "", "tab": ""}
FLOAT_OF_PARAMS = (FACEPLATE_OF_SELECTION.replace("{session.custom.selectedStyle}", "{view.params.style}")
                   .replace("{session.custom.selectedKind}", "{view.params.kind}"))


def float_faceplate() -> dict:
    """`Framework/ASM/FloatFaceplate`: a device's own floating faceplate, one popup per device
    (`cadre.hmi.float_id`). It reads the device, kind, style, title, label and tab from its view parameters,
    never from `session.custom.selected*`, so a second device does not redraw the first. Its Dock pin puts
    this faceplate in the right dock (and sets the session's mode to dock); the popup's own title bar
    carries the title, the close icon, the drag and the resize."""
    dock = _pin_button("Dock", [
        "p = self.view.params",
        "self.session.custom.faceplateMode = 'dock'",
        *open_device("p.deviceId", "p.kind", "p.title", "p.label", "p.tab"),
        "system.perspective.closePopup(p.popupId)"])
    bar = pv.node("ia.container.flex", "Bar", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "alignItems": "center",
        "style": {"classes": "cadre/divider/bottom", "padding": "0 8px 0 16px", "gap": "8px"}},
        children=[_label("Description", pv.fpos(grow=1), "{view.params.label}", classes="cadre/font/label cadre/text/neutral"),
                  dock])
    body = pv.node("ia.display.view", "Faceplate", pv.fpos(basis=f"{FACEPLATE_HEIGHT}px", shrink=0), {
        "path": "Faceplate/Empty", "params": {"deviceId": "", "tab": ""}, "useDefaultViewHeight": False,
        "useDefaultViewWidth": False},
        prop_config={"props.path": pv.bind(pv.expr(FLOAT_OF_PARAMS)),
                     "props.params.deviceId": pv.bind(pv.expr("{view.params.deviceId}")),
                     "props.params.tab": pv.bind(pv.expr("{view.params.tab}"))})
    scroll = pv.node("ia.container.flex", "Scroll", pv.fpos(grow=1, basis="0px"), {
        "direction": "column", "style": {"overflow": "auto"}}, children=[body])
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/menu")}, children=[bar, scroll])
    return pv.view(root, params=dict(FLOAT_PARAMS), param_dirs={k: "input" for k in FLOAT_PARAMS}, size=dict(POPUP_SIZE))


# ---------------------------------------------------------------------------------------------------------
# The pivot pages: a node's Alarms and Trend content
# ---------------------------------------------------------------------------------------------------------
def node_alarms() -> dict:
    """`Framework/ASM/NodeAlarms`, the route `/node/alarms`: the alarm status table over the alarms of the
    node's devices (`session.custom.contentNode`); the root shows the whole alarm scope."""
    from . import acks   # Ack selected and Ack all under the table (L5)
    tbl = pv.node("ia.display.alarmstatustable", "Table", pv.fpos(grow=1, basis="0px"), acks.stock_props(),
                  prop_config={"props.filters.active.conditions.source": pv.bind(
                      pv.expr("coalesce({session.custom.contentNode}, '')"), [pv.script_transform([
                          "return cadre.hmi.node_sources(self.session, value)"])]),
                               "props.filters.active.priorities.diagnostic": pv.bind(pv.expr("true")),
                               **_table_actions()})
    bar = acks.bar(selections=["selected"], can_selected="W7", can_all="W7", path_selected="W7", path_all="W7")
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"padding": "8px", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")},
                   children=[tbl] + bar + [search_panel()])
    return pv.view(root, size={"width": 1600, "height": 788},
                   custom={"can": dict(CAN_DEFAULT), **acks.custom("selected")},
                   custom_config={"custom.can": CAN_CFG, **acks.stock_config("Table")})


def node_trend() -> dict:
    """`Framework/ASM/NodeTrend`, the route `/node/trend`: one `Trend/Card` for each historised member of the
    node's devices, over a range of 1, 8 or 24 h."""
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
        prop_config={"props.instances": pv.bind(pv.expr("{view.custom.cards}"))})
    empty = _label("Empty", pv.fpos(basis="40px", shrink=0), text="No device of this node has a historised member",
                   classes="cadre/font/label cadre/text/neutral", style={"padding": "0 8px"}, visible="len({view.custom.cards}) = 0")
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"padding": "8px", "gap": "8px"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/page")},
                   children=[ranges, empty, cards, search_panel()])
    cfg = pv.bind(pv.expr("toStr({view.custom.hours}) + '|' + coalesce({session.custom.contentNode}, '')"), [
        pv.script_transform(["parts = (value or '').split('|', 1)",
                             "return cadre.hmi.node_trends(self.session, parts[1] if len(parts) > 1 else '', int(parts[0] or 1))"])])
    return pv.view(root, size={"width": 1600, "height": 788}, custom={"hours": 1, "cards": []},
                   custom_config={"custom.cards": cfg})


def views() -> dict[str, dict]:
    """The views of the ASM frame, written into the parent beside the library's own."""
    return {"Framework/ASM/Head": head(), "Framework/ASM/TopBar": top_bar(), "Framework/ASM/Crumb": crumb(), "Framework/ASM/CrumbPopup": crumb_popup(),
            "Framework/ASM/SearchResults": search_results(), "Framework/ASM/ListRow": list_row(),
            "Framework/ASM/NavDock": nav_dock(), "Framework/ASM/PageHeader": page_header(),
            "Framework/ASM/PageTab": page_tab(), "Framework/ASM/AlarmBanner": alarm_banner(),
            "Framework/ASM/BannerRow": banner_row(), FLOAT_VIEW: float_faceplate(),
            "Framework/ASM/NodeAlarms": node_alarms(), "Framework/ASM/NodeTrend": node_trend()}


# ---------------------------------------------------------------------------------------------------------
# The child: page configuration and session data
# ---------------------------------------------------------------------------------------------------------
def shared_docks(app_name: str = "App") -> dict:
    """`framework.shared_docks` with the ASM frame: the top bar and the 36 px page header in one top dock, the
    navigation dock at the left (modal), the faceplate dock at the right, the 76 px alarm banner at the
    bottom."""
    docks = framework.shared_docks(app_name)

    def dock(id_, view, size, show, content, params=None, modal=False, breakpoint=480):
        return {"anchor": "fixed", "autoBreakpoint": breakpoint, "content": content, "handle": "hide", "iconUrl": "",
                "id": id_, "modal": modal, "resizable": False, "show": show, "size": size,
                "viewParams": params or {}, "viewPath": view}
    docks["top"] = [dock("topbar", "Framework/ASM/Head", TOP_BAR_HEIGHT + HEADER_HEIGHT, "visible", "push",
                         {"appName": app_name, "showUser": True, "clockLabel": "UTC", "siteNote": ""})]
    docks["left"] = [dock(NAV_DOCK, "Framework/ASM/NavDock", 320, "onDemand", "cover", modal=True, breakpoint=768)]
    docks["bottom"] = [dock(BANNER_DOCK, "Framework/ASM/AlarmBanner", BANNER_HEIGHT, "visible", "push")]
    return docks


def page_config(app_name: str, pages: dict) -> dict:
    """The page configuration of a child built with `--frame asm`: the pages, the two pivot pages and
    the ASM docks."""
    p = {"/alerts": {"title": "Alerts", "viewPath": "Framework/AlertsPage"}}
    p.update(pages)
    p[NODE_ALARMS_ROUTE] = {"title": "Alarms", "viewPath": "Framework/ASM/NodeAlarms"}
    p[NODE_TREND_ROUTE] = {"title": "Trend", "viewPath": "Framework/ASM/NodeTrend"}
    return {"pages": p, "sharedDocks": shared_docks(app_name)}


def frame_errors(descs: list[dict]) -> list[str]:
    """Problems of the frame's `screen` keys: `previous` and `next` name a route of the descriptor set (a page
    the project does not have is a dead button)."""
    routes = {d["screen"]["route"] for d in descs}
    out = []
    for d in descs:
        s = d["screen"]
        for k in ("previous", "next"):
            if s.get(k) and s[k] not in routes:
                out.append(f"{s['route']}: screen.{k} {s[k]!r} is not the route of a descriptor")
    return out


def _tab_of(path: str, spec: dict) -> str:
    rel = path.split("/", 1)[-1] if "/" in path else path
    for prefix, tab in TAG_TABS:
        if ("/" + prefix) in ("/" + rel) or rel.startswith(prefix):
            return tab
    return "alarms" if spec.get("alarms") else "home"


def _tag_leaves(tag_model: dict | None) -> list[dict]:
    """Every atomic tag of the tag model with its path from the provider root (`historised` walks it alike)."""
    out: list[dict] = []

    def walk(node, path):
        for t in node.get("tags", []):
            here = path + [t["name"]]
            if t.get("tagType") == "Folder":
                walk(t, here)
            else:
                out.append({"path": "/".join(here), "doc": t.get("documentation", ""), "unit": t.get("engUnit", ""),
                            "alarms": bool(t.get("alarms"))})
    if tag_model:
        walk({"tags": [tag_model]}, [])
    return out


def device_routes(descs: list[dict]) -> dict[str, str]:
    """The route of the page that draws each device (by tag path): the page of the deepest node that draws it,
    else the first page; the page a search or a banner takes the operator to."""
    from . import screen as scr
    out: dict[str, tuple[int, str]] = {}
    for desc in descs:
        depth = len([x for x in desc["screen"].get("node", "").split("/") if x])
        for s in scr.descriptor_items(desc):
            folder = scr.device_folder(s)
            if folder:
                path = scr.tag_path(desc.get("tagRoot", ""), folder)
                if path not in out or depth > out[path][0]:
                    out[path] = (depth, desc["screen"]["route"])
    return {k: v[1] for k, v in out.items()}


def search_index(descs: list[dict], tag_model: dict | None, index: list[dict], trends: bool = False,
                 devices: dict | None = None) -> dict:
    """The search index (DESIGN section 5), compact lists to keep the session small (about 60 bytes a tag):
    pages `[route, title, node path, level]`, devices `[folder, kind, title, label, route, node path,
    faceplate 1 or 0]` and tags `[path, description, unit, device index or -1, tab]`. The tag index comes
    from the tag model: the tags with a description or an alarm, and every tag of a device, each with the
    device that holds it (the longest device folder that is a prefix of the tag's path)."""
    from . import screen as scr
    routes = device_routes(descs)
    nodes = scr.device_nodes(descs, devices)
    pages = [[d["screen"]["route"], d["screen"].get("title", ""), d["screen"].get("node", ""),
              d["screen"].get("level", "")] for d in descs]
    pages.append(["/alerts", "Alerts", "", ""])
    if trends:
        pages.append(["/trends", "Trends", "", ""])
    devices = [[d["folder"], d["kind"], d["title"], d["label"], routes.get(d["folder"], ""), nodes.get(d["folder"], ""),
                1 if framework.FACEPLATE_VIEW.get(d["kind"]) else 0] for d in index]
    where = sorted(((d["folder"].split("]", 1)[-1], i) for i, d in enumerate(index)), key=lambda x: -len(x[0]))
    tags = []
    for t in _tag_leaves(tag_model):
        owner = -1
        for rel, i in where:
            if t["path"].startswith(rel + "/"):
                owner = i
                break
        if owner < 0 and not t["doc"] and not t["alarms"]:
            continue
        tags.append([t["path"], t["doc"], t["unit"], owner, _tab_of(t["path"], t)])
    return {"pages": pages, "devices": devices, "tags": tags}


def page_info(descs: list[dict]) -> dict[str, dict]:
    """What the page header says of each route: title, display level, previous and next pages with their titles."""
    title = {d["screen"]["route"]: d["screen"].get("title", "") for d in descs}
    out = {}
    for d in descs:
        s = d["screen"]
        out[s["route"]] = {"title": s.get("title", ""), "level": s.get("level", ""),
                           "previous": s.get("previous", ""), "previousTitle": title.get(s.get("previous", ""), ""),
                           "next": s.get("next", ""), "nextTitle": title.get(s.get("next", ""), "")}
    return out


def session_custom(descs: list[dict], tag_model: dict | None, index: list[dict], trends: bool = False,
                   devices: dict | None = None) -> dict:
    """The `session.custom` keys a child built with `--frame asm` adds to the parent's defaults."""
    return {"frame": "asm", "pageInfo": page_info(descs), "searchIndex": search_index(descs, tag_model, index, trends, devices),
            "contentNode": ""}
