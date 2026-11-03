"""The ASM variant of the new frame (`screen.py --frame obasm`, tranche T2 batch F6b; `cloud/FRAME-DESIGN.md` section 1.2, the
owner's answers 1 to 4 and the departures at the end).

The frame carries every part of the ASM frame (`navigation.py`, wiki 04 section 8) and is drawn, where a component of the module
can carry the part faithfully, with the module's frame components (batches F1 to F5, as `obframe.py` uses them). It needs
`--render module`. The views belong to the parent (`views()`, written by `parent.py`) and cost a child nothing until its page
configuration names them (`page_config`); a child built with another frame is not touched.

Parts, and what carries each (the ASM rules stay in the data and the scripts: `cadre.hmi.node_counts`, `nav_tree`, `crumbs`,
the priority table of wiki 13 section 11.1; none is in a component):

    Framework/OBASM/Head      the one top dock (GF-90), three rows: the module top bar (48 px), a strip (36 px) of the Cadre
                              crumb with its node badges, the Cadre search field and the Cadre alert message with its ACK,
                              and the page header (48 px: the module pivot and tab row, the Cadre title, level and previous
                              and next buttons)
    Framework/OBASM/NavDock   the left modal dock in its two states (`session.custom.navPanel`): the Cadre title row and
                              search box over the module tree navigation (the hierarchy, a node's counts as its `alerts`)
                              or over the module navigation menu (the support pages)
    Framework/OBASM/Crumb     the ASM crumb, its popup opened beneath the strip (the popup is the ASM one, with its badges)
    Framework/OB/AlertMenu, UserMenu, Brilliance   the OpenBridge variant's popups, shared (`obframe`)
    Framework/ASM/...         the alarm banner, the floating faceplates, the pivot pages and the search results, as they are

Every component event is a script action that cites the event's measured shape (GF-37, wiki page 07) in its first comment
line and calls a function that exists: the dock's `openDock`, the library's `navigate`, `action_lines` (the ASM row action,
which also opens a device's faceplate), `ack_top` and the rest as `obframe` wires them. No write path is new, no credential is
a property, and the silence control is hidden.
"""
from __future__ import annotations

import copy

from . import framework, navigation, obframe, pv
from .framework import NAV_DOCK, root_classes

FRAME = "obasm"
HEAD_VIEW, NAV_VIEW, CRUMB_VIEW = "Framework/OBASM/Head", "Framework/OBASM/NavDock", "Framework/OBASM/Crumb"
TOP_BAR_HEIGHT, STRIP_HEIGHT = obframe.TOP_BAR_HEIGHT, obframe.STRIP_HEIGHT
HEADER_HEIGHT = 48     # the module's pivot group and tab row are 48 px high (wiki 12 section 17.27.5); the ASM header is 36
HEAD_HEIGHT = TOP_BAR_HEIGHT + STRIP_HEIGHT + HEADER_HEIGHT
CRUMB_POPUP_TOP = TOP_BAR_HEIGHT + STRIP_HEIGHT   # the crumb stands in the strip, so its popup opens beneath the strip
PIVOT_WIDTH, TABS_WIDTH = 240, 480

# the page header's own data and its poll (the ASM header's: `cadre.hmi.page_header`, every 2 s and on a change of page or node)
HEAD_CFG = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {page.props.path} + '|' + coalesce({session.custom.contentNode}, ''), '')"),
                   [pv.script_transform(["return cadre.hmi.page_header(self.session, (value or '').split('|')[0])"])])


def _bind_items(expression: str, call: str) -> dict:
    """A binding that shapes the value of `expression` into a component's items by `cadre.hmi.obasm_items`."""
    return pv.bind(pv.expr(expression), [pv.script_transform([f"return cadre.hmi.obasm_items({call})"])])


# ---------------------------------------------------------------------------------------------------------
# The top dock
# ---------------------------------------------------------------------------------------------------------
def page_header_row() -> dict:
    """The page header row of the head (wiki 04 section 8.6): the title and its display level, the pivot Mimic, Alarms and Trend of
    the page's node (`obc-pivot-item-group`), the node's pages as tabs where it has several (`obc-tab-row`), and the previous and
    next pages. The title, level and the two step buttons are the ASM header's own nodes (`navigation.page_header`): the module
    has no component for a title or a step button that names its target."""
    ph = navigation.page_header()
    kids = {k["meta"]["name"]: k for k in ph["root"]["children"]}
    pivot = pv.node("cadre.ob.pivotitemgroup", "Pivot", pv.fpos(basis=f"{PIVOT_WIDTH}px", shrink=0), {"direction": "horizontal"},
                    prop_config={
                        "props.items": _bind_items("{view.custom.head.mimicRoute}", "'pivot', value"),
                        "props.selectedValue": pv.bind(pv.expr("{view.custom.head.mode}")),
                        "position.display": pv.bind(pv.expr("len({view.custom.head.nodeId}) > 0"))},
                    events=obframe._events(onChange=[
                        "# GF-37: event.selectedValue is the value of the pivot pressed: mimic, alarms or trend",
                        "v = event.selectedValue",
                        "if v == 'mimic':",
                        "\tif self.view.custom.head.mimicRoute:",
                        "\t\tsystem.perspective.navigate(self.view.custom.head.mimicRoute)",
                        "elif v == 'alarms' or v == 'trend':",
                        "\tself.session.custom.contentNode = self.view.custom.head.nodeId",
                        "\tsystem.perspective.navigate('/node/' + v)"]))
    tabs = pv.node("cadre.ob.tabrow", "Tabs", pv.fpos(basis=f"{TABS_WIDTH}px", shrink=1), {"hug": True},
                   prop_config={
                       "props.tabs": _bind_items("{view.custom.head.tabs}", "'tabs', value"),
                       "props.selectedTabId": _bind_items("{view.custom.head.tabs}", "'tab', value"),
                       "position.display": pv.bind(pv.expr("len({view.custom.head.tabs}) > 0"))},
                   events=obframe._events(onTabSelected=[
                       "# GF-37: event.id is the id of the tab pressed (the route of the page), event.index its place",
                       "if event.id:",
                       "\tsystem.perspective.navigate(event.id)"]))
    return pv.node("ia.container.flex", "PageHeader", pv.fpos(basis=f"{HEADER_HEIGHT}px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"classes": "cadre/divider/bottom", "padding": "0 8px", "overflow": "hidden"}},
        children=[kids["Title"], kids["Level"], pivot, tabs, kids["Spacer"], kids["Previous"], kids["Next"]])


def head() -> dict:
    """`Framework/OBASM/Head`: the module top bar over the strip over the page header, in the one top dock (the gateway draws
    one dock of a side at a time, GF-90). The bar is `obframe.bar_node` with the two buttons of the ASM bar: the menu button opens
    the navigation dock on the page tree and the apps button on the support pages (`session.custom.navPanel`, wiki 04 section 8.3);
    the bar's page name gives way to the crumb where the page names a node (section 7 item 4). The strip keeps the Cadre crumb
    (owner's answer 2), the Cadre search field (the module has none) and the Cadre alert message (answer 3)."""
    src = framework.top_bar()   # the strip's nodes and the data they read are the default bar's own
    kids = {k["meta"]["name"]: k for k in src["root"]["children"]}
    kids["Crumbs"]["props"]["path"] = CRUMB_VIEW
    bar = obframe.bar_node(
        menu=["# GF-37: the event carries nothing; the dock opens on the page tree, as the ASM top bar's menu button does",
              *navigation._open_nav(navigation.NAV_PAGES)],
        apps=["# GF-37: the event carries nothing; the dock opens on the support pages, as the ASM top bar's second button does",
              *navigation._open_nav(navigation.NAV_SUPPORT)],
        page_after_crumbs=True)
    strip = pv.node("ia.container.flex", "Strip", pv.fpos(basis=f"{STRIP_HEIGHT}px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"overflow": "hidden"}},
        children=[kids["Crumbs"], kids["Spacer"], navigation._search_field(), kids["AlertMessage"]])
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/bar")},
                   children=[bar, strip, page_header_row()])
    params = {"appName": "App", "showUser": True}
    config = {k: v for k, v in src["propConfig"].items() if k.startswith("custom.")}
    config["custom.crumbs"] = navigation.CRUMBS_ASM_CFG   # the trail follows the pivot pages' node (`contentNode`)
    config["custom.head"] = HEAD_CFG
    custom = {**src["custom"], "head": copy.deepcopy(navigation.HEAD_DEFAULT)}
    return pv.view(root, params=params, param_dirs={k: "input" for k in params},
                   size={"width": 1600, "height": HEAD_HEIGHT}, custom=custom, custom_config=config)


# ---------------------------------------------------------------------------------------------------------
# The navigation dock
# ---------------------------------------------------------------------------------------------------------
def _row_click(rows: str) -> list[str]:
    """The lines of a navigation row's press: the row whose `id` the event names runs the ASM row action
    (`navigation.action_lines`: its route, or the Alarms or Trend page of its node, its device's faceplate, then closing the dock)."""
    return ["# GF-37: event.id is the id of the row pressed, at any depth; cadre.hmi.obasm_items set it on the row",
            f"rows = [x for x in {rows} if x['id'] == event.id]",
            "if rows:",
            "\tr = rows[0]",
            *navigation.action_lines(lambda f: f"r['{f}']", "\t")]


def nav_dock() -> dict:
    """`Framework/OBASM/NavDock`: the one left dock in its two states (`session.custom.navPanel`). The title row and the search box
    are the ASM dock's own. `pages`: the module tree navigation over `cadre.hmi.nav_tree` (every node of the hierarchy, a node
    that holds pages or nodes as a group, its counts as `alerts`, the current page checked and its branch open; with a query a flat
    list of the matching nodes and pages). `support`: the module navigation menu over `cadre.hmi.nav_support`. A press runs the
    row's ASM action and closes the dock."""
    asm = navigation.nav_dock()
    kids = {k["meta"]["name"]: k for k in asm["root"]["children"]}
    pages = f"coalesce({{session.custom.navPanel}}, '{navigation.NAV_PAGES}') != '{navigation.NAV_SUPPORT}'"
    support = f"coalesce({{session.custom.navPanel}}, '{navigation.NAV_PAGES}') = '{navigation.NAV_SUPPORT}'"
    icons = obframe.nav_icons()
    tree = pv.node("cadre.ob.treenavigation", "Tree", pv.fpos(grow=1, basis="0px"), {"items": []},
                   prop_config={"props.items": pv.bind(pv.expr("{view.custom.tree.items}")),
                                "position.display": pv.bind(pv.expr(pages))},
                   events=obframe._events(onItemClick=_row_click("self.view.custom.tree.rows")))
    menu = pv.node("cadre.ob.navigationmenu", "Support", pv.fpos(grow=1, basis="0px"), {"items": [], "footerItems": []},
                   prop_config={"props.items": pv.bind(pv.expr("{view.custom.support.items}")),
                                "position.display": pv.bind(pv.expr(support))},
                   events=obframe._events(onItemClick=_row_click("self.view.custom.support.rows")))
    root = pv.node("ia.container.flex", "root", {}, {"direction": "column", "style": {"padding": "0 0 8px 0", "overflow": "hidden"}},
                   prop_config={"props.style.classes": root_classes("cadre/surface/menu")},
                   children=[kids["Header"], kids["Search"], tree, menu])
    tree_cfg = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {page.props.path} + '|' + coalesce({session.custom.navQuery}, ''), '')"), [
        pv.script_transform(["parts = (value or '').split('|', 1)",
                             "rows = cadre.hmi.nav_tree(self.session, parts[1] if len(parts) > 1 else '', parts[0])",
                             f"return cadre.hmi.obasm_items('tree', rows, parts[0], {icons!r})"])])
    support_cfg = pv.bind(pv.expr("if(toMillis(now(2000)) > 0, {page.props.path}, '')"), [
        pv.script_transform(["rows = cadre.hmi.nav_support(self.session, value)",
                             f"return cadre.hmi.obasm_items('support', rows, value, {icons!r})"])])
    empty = {"rows": [], "items": []}
    return pv.view(root, size={"width": 320, "height": 800}, custom={"tree": copy.deepcopy(empty), "support": copy.deepcopy(empty)},
                   custom_config={"custom.tree": tree_cfg, "custom.support": support_cfg})


def crumb() -> dict:
    """`Framework/OBASM/Crumb`: the ASM crumb, whose popup (Show and Areas, with the areas' badges) opens beneath the strip."""
    return navigation.crumb(top=CRUMB_POPUP_TOP)


def views() -> dict[str, dict]:
    """The views of the ASM variant, written into the parent beside the library's own."""
    return {HEAD_VIEW: head(), NAV_VIEW: nav_dock(), CRUMB_VIEW: crumb()}


# ---------------------------------------------------------------------------------------------------------
# The child: page configuration and session data
# ---------------------------------------------------------------------------------------------------------
def shared_docks(app_name: str = "App") -> dict:
    """`navigation.shared_docks` (the ASM docks) with this variant's head in the one top dock and its navigation in the left
    dock (modal, GF-71); the faceplate dock at the right and the 76 px alarm banner at the bottom are the ASM frame's."""
    docks = navigation.shared_docks(app_name)
    docks["top"][0].update(viewPath=HEAD_VIEW, size=HEAD_HEIGHT, viewParams={"appName": app_name, "showUser": True})
    docks["left"][0].update(viewPath=NAV_VIEW)
    return docks


def page_config(app_name: str, pages: dict) -> dict:
    """The page configuration of a child built with `--frame obasm`: the pages, the alerts route, the two pivot pages and the docks above."""
    cfg = navigation.page_config(app_name, pages)
    cfg["sharedDocks"] = shared_docks(app_name)
    return cfg


def session_custom(*args, **kw) -> dict:
    """The `session.custom` keys of a child built with `--frame obasm`: the ASM frame's own (the page information, the search
    index, `contentNode`) with this frame's name."""
    return {**navigation.session_custom(*args, **kw), "frame": FRAME}
