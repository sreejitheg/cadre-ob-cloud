---
title: Navigation and frame
type: wiki
updated: 2026-10-26
---
# 04 Navigation Philosophy and the Application Frame

| Field | Value |
|---|---|
| Document ID | COB-WIKI-04 |
| Revision | D |
| Status | Issued for use |
| Implementation | `tools/hmi/framework.py` (views `Framework/*`, `Faceplate/*`), `tools/hmi/scripts.py` (`cadre.hmi`) |

## 1. The Philosophy

The vendor's application frame, as its documentation and demo show it, rests on six rules. The
Cadre frame adopts all six.

1. **One frame for every page.** The header and the navigation are docked views shared by all
   pages, so they stay in place while the operator moves between pages.
2. **Navigation on demand.** A menu button at the far left of the header opens the navigation menu
   in a left dock that floats over the page; the menu closes when a page is chosen, on Escape and on
   a click outside it.
3. **Navigation by page.** Every destination is a route of the page configuration; the item of the
   current route is shown selected.
4. **Pages built from cards and diagrams.** Content is grouped in cards; process content is a
   diagram whose sections can drill down to detail pages.
5. **One palette per session.** The operator chooses day, dusk, night or bright in a brilliance menu
   in the header; every component follows.
6. **Alerts always visible.** The header shows the most severe active alert with an acknowledge
   button and an alert count coloured by the highest priority; the count opens an alert menu, and
   an alerts page holds the full list.

## 2. Frame Layout

Table 1. The docks of the frame (`framework.shared_docks`), written into every child's page
configuration by the generator.

| Dock | Identifier | View | Size | Display | Content |
|---|---|---|---|---|---|
| Top | `topbar` | `Framework/TopBar` | 48 px | visible | push |
| Left | `nav` | `Framework/NavMenu` | 320 px | on demand | cover |
| Right | `faceplate` | `Framework/SideMenu` | 400 px | on demand | push |

The route `/alerts` (`Framework/AlertsPage`) is added to every child.

## 3. Components of the Frame

Table 2. Frame views and the vendor equivalents.

| Cadre view | Vendor equivalent | Behaviour implemented |
|---|---|---|
| `Framework/TopBar` | Top Bar | Menu button (`dock` toggle action on `nav`); app name; page name (the navigation label of `page.props.path`, `cadre.hmi.page_title`); the most severe active alarm with its time and an ACK button; the alarm count, coloured by the highest priority, flashing while any alarm is unacknowledged, opening `Framework/AlertMenu`; the brilliance button; the user button; the clock |
| `Framework/NavMenu`, `Framework/NavItem` | Navigation Bar | Items and footer from `session.custom.nav.items` and `.footer` in two flex repeaters; each item an icon (any converted icon by name, through `cadre.icons.elements`) and a label; selected when its path equals `page.props.path`; a click navigates and closes the dock. A header with a close button; the dock is modal, so a click outside it closes it (GF-71, since 2026-10-22) |
| `Framework/BrillianceMenu` | Brilliance Menu | Day, dusk, night and bright; the current palette highlighted; `cadre.hmi.set_palette` writes the palette and the Ignition theme. Like every top bar menu, a modal popup that a click outside it or Escape closes (GF-70) |
| `Framework/UserMenu` | User Menu | The signed-in user, Sign in (`system.perspective.login`), Sign out (`logout`) |
| `Framework/AlertMenu` | Alert Menu | A header with a close button, `ia.display.alarmstatustable` (under the module rendering OpenBridge's small alert page and the cleared alerts not acknowledged) and an "Alerts" link to `/alerts`; closed by a click outside it (GF-70) |
| `Framework/AlertsPage` | Alert List Page | Active and History tabs over `ia.display.alarmstatustable` and `ia.display.alarmjournaltable` |
| `Framework/SideMenu`, `Faceplate/*` | Side menu with pump and valve faceplates | The faceplate of the selected kind, a close button, state, commands (Run and Stop, Open and Close), mode (Manual, Local, Auto), speed for pumps, the device's alarms |

## 4. The Alarm Summary

The top bar binds `view.custom.alarm` to `now(2000)` with a script transform that calls
`cadre.hmi.alarm_summary()`. The function uses only measured or documented calls: alarm counts
from `system.alarm.queryStatus(state=...)`, the highest priority by querying each priority in
turn with `priority=[name]` (GF-06), and the message from the measured `PyAlarmEvent` accessors
`getLabel`, `getId` and `getActiveData().getTimestamp()` (GF-06). ACK calls
`system.alarm.acknowledge([id], notes)`. Live on 2026-10-07 the bar showed 18 active alarms,
highest priority High, and the label and time of the first High alarm.

## 5. The Faceplate Dock Contract

A symbol with a `deviceId` parameter opens the faceplate on click. The handler writes
`session.custom.selectedDevice` (the device's tag folder) and `session.custom.selectedKind` (the
library kind) through `cadre.hmi.select_device`, then opens the `faceplate` dock. The dock shows
`Faceplate/<kind>` with the device folder as a parameter. A faceplate binds the device members
`state`, `cmd`, `mode` and `speed` by indirect tag bindings (page 06 section 4).

## 6. Not Yet Implemented

Table 3. Frame behaviour the vendor frame has and the Cadre frame does not, with the register item.

| Behaviour | Register |
|---|---|
| Top bar command indicator, apps button, narrow-screen breakpoints | COB-020 |
| Navigation groups and flyouts (per-item alert badges: section 7) | COB-021 |
| Alert list styling by alert category, the detail pane, alert silence event | COB-022 |
| Brightness slider in the brilliance menu | COB-023 |
| Highlight of the menu button while the navigation dock is open | COB-024 |

## 7. The Plant Hierarchy, Its Counts and the Breadcrumb

Built and tested offline on 2026-10-23 under work package D of the ASMP build (COB-141; findings F033,
F036, F046 and F047 of the study; COBD-044).

1. **The hierarchy.** A descriptor names the node of the plant hierarchy its page shows (`screen.node`,
   page 08 section 3), for example `WTP/Filtration`. The generator makes a node for every named node
   and every node above one, root first, each with an `id` an expression may name (`n0`, `n1`, ...),
   its pages, and the devices it owns: those whose deepest page is one of its own (`screen.hierarchy`).
   It writes the hierarchy into `session.custom.hierarchy`, and each navigation item names its page's
   node. A project whose descriptors name no node has no hierarchy, and its frame is as before.
2. **Counts per node.** `cadre.hmi.node_counts` counts the active alarms of every node by priority, with
   the unacknowledged ones apart, in one query over the session's alarm scope: each alarm goes to its
   device (`tag_id` over the device index), the device to its node, and the count to the node and to
   every node above it. The roll-up follows the hierarchy, not a wildcard over display paths, so a node
   never counts a sibling's alarms. A native folder metric replaces it if probe E9 proves one (ASMP-009).
3. **Badges.** `Framework/Badges` draws a pill for each priority with active alarms, the count in the
   priority's colour by rank (page 13 section 11.1), Diagnostic neutral, nothing at 0. One shape serves
   every priority, so no second shape code stands beside OpenBridge's status shapes.
4. **The breadcrumb.** Where the page names a node, the top bar shows the nodes from the root to the
   page's own in place of the page's name (`cadre.hmi.crumbs`, polled every 2 s; `Framework/Crumb`):
   each with its name and its badges, a chevron before every node but the first, and a click that opens
   the node's first page. A page that names no node (the alerts page, the trend page) shows its name.
5. **The menu.** Each page item of the navigation menu carries the badges of its page's node
   (`cadre.hmi.nav_items`, polled every 2 s); the footer's items carry none.

Not built: the child popup of a crumb (the source's), and the narrow layout that keeps only the last
crumb. Nothing of this section has run on the gateway; the combined run (COB-143) is to see the
breadcrumb and the badges on the water treatment sample with an alarm raised in one area. The child
popup of a crumb is built in section 8, under the ASM frame.

## 8. The ASM Frame

Built and tested offline on 2026-10-23 (COB-160; gaps GX-02, GX-09 and GX-10 of the eng02 ASM
reimagining). The frame of sections 2 to 7 stays the default. The ASM frame is a second set of views and
docks that a child takes only when it is built with `screen.py --frame asm`; a child built without the
option, and every child already built, keeps the frame above. Code: `tools/hmi/navigation.py` (views,
page configuration, session data), `tools/hmi/navigation_scripts.py` (the `cadre.hmi` functions the views
call, appended to the library source), `tests/test_asm_frame.py`. Level 4 (2026-10-24) changed the search,
the navigation dock, the popups and the page canvas; sections 8.3 to 8.5 and 8.9 to 8.11 state the result.

### 8.1 The Option and the Docks

`screen.build_child(..., frame="asm")`, or `--frame asm` on the command line (`openbridge` is the default
and means no change). The option writes the page configuration of Table 4, the two pivot routes
`/node/alarms` and `/node/trend`, and the session data of section 8.9. The parent carries every ASM view
whether or not a child uses it (`navigation.views()`, written by `parent.py`).

Table 4. The docks of a child built with `--frame asm` (`navigation.shared_docks`).

| Edge | Identifier | View | Size | Display | Content |
|---|---|---|---|---|---|
| Top | `topbar` | `Framework/ASM/Head`: `Framework/ASM/TopBar` (48 px) above `Framework/ASM/PageHeader` (36 px) | 84 px | visible | push |
| Left | `nav` | `Framework/ASM/NavDock`, in two states (section 8.3) | 320 px, modal | on demand | cover |
| Right | `faceplate` | `Framework/SideMenu` | 400 px | on demand | push |
| Bottom | `alarmbanner` | `Framework/ASM/AlarmBanner` | 76 px | visible | push |

The top bar and the page header share the one top dock (`Framework/ASM/Head`, which passes the dock's parameters
to the top bar): the first gateway run (2026-10-24) showed only the first of two top docks that were both
visible (GF-90). The top bar is the library's own (`framework.top_bar`), with the trail of crumbs that open their popups,
the 300 px search field before the alarm summary, a second button beside the menu button (section 8.3), and
a site note beneath the application's name (view parameter `siteNote`, empty and hidden by default). The alarm
summary, the alert menu, the brilliance and user buttons and the clock are unchanged.

### 8.2 Several Floating Faceplates

In popup mode, a device opened in the ASM frame has a popup of its own: `Framework/ASM/FloatFaceplate`,
popup identifier `cadre.hmi.float_id(device)` (`fp_` and the device path with every character that is not
a letter or digit replaced by an underscore). The view takes the device, kind, style, title, label and
tab as view parameters (`cadre.hmi.float_params`), written when the popup opens from the selection that
`cadre.hmi.select_device` and `library.open_device` have just made. It never reads
`session.custom.selected*`, so a second device does not redraw the first.

1. **Place.** The first popup is 5 px from the right edge and 90 px from the top; each further device
   takes the next of six slots, 24 px to the left and 24 px lower (`cadre.hmi.float_position`). A device
   keeps its slot (`session.custom.floating`).
2. **Opening a device that is already floating.** The opener closes that device's popup and opens it again
   with the asked tab, which brings it to the front. The popup returns to its slot, so a drag is lost.
3. **Dock pin.** The popup's Dock button sets the session's mode to dock, selects the popup's device and
   opens the right dock through `library.open_device` on the popup's tab, then closes that popup. The
   other floating faceplates stay where they are.
4. **Dock mode** is unchanged: the right dock shows one faceplate, and a new device replaces it. The dock's
   Float button now opens the faceplate through the same lines as every opener (`library.open_faceplate`).
5. **Selection of the branch.** `library.open_faceplate` tests `cadre.hmi.asm_frame(session)`
   (`session.custom.frame`); a project built before the option answers false and keeps the single
   `Framework/FaceplatePopup`.

### 8.3 The Navigation Dock

`Framework/ASM/NavDock` (320 px) is the one dock of the left edge (one dock of an edge shows at a time, GF-90). It is
for navigation only; the support pages stand in a second state of the same dock. `session.custom.navPanel` says
which: `pages` or `support`. Two buttons of the top bar open the dock, each writing the state first and then calling
`system.perspective.openDock(id='nav')`: the menu button opens `pages`, and the button beside it (the library's
`dashboard` icon, the nearest of its 92 icons to OpenBridge's `apps`) opens `support`.

1. **Pages.** A header with Close, a search box bound to `session.custom.navQuery`, and the tree:
   `cadre.hmi.nav_tree(session, query, route)`, every node of `session.custom.hierarchy`, root first, each with its
   badges and its pages beneath it, the page of the current route selected. A node row opens the node's first
   page, or the node's Alarms page where it has none. The footer of earlier builds is gone: the tree holds
   nothing else.
2. **Search box.** With a query, a flat list of the nodes and pages whose name, path or route contains it,
   each with its node path as a second line.
3. **Support.** The title reads Tools and support, and one list stands in place of the search box and the tree:
   `cadre.hmi.nav_support(session, route)`, All alarms (the Alarms pivot page of the root node), then the rows of
   `cadre.hmi.nav_footer`: the navigation items that name no node (the trend page, a tools page, the component
   test page of a build that has one) and the frame's footer items (the alerts page). A project with no hierarchy
   lists its navigation items as the tree. The privilege of a support page is not shown (no descriptor key carries
   it). There is no help page in the library; one is a navigation item with no node and appears here.
4. **Closing.** A row carries `close = nav`, and its click closes the dock; Escape and a click outside
   are the dock's own behaviour (`modal`).

All three lists use one row view, `Framework/ASM/ListRow` (parameters `kind`, `label`, `second`, `icon`,
`depth`, `counts`, `selected`, `disabled`, `action`, `route`, `nodeId`, `deviceId`, `deviceKind`,
`deviceTitle`, `deviceLabel`, `tab`, `close`). A row's click navigates to its route, or to the Alarms or
Trend page of its node (`session.custom.contentNode`), then opens its device's faceplate on its tab
through `library.open_device`, then closes what it came from.

### 8.4 The Crumb Popup

A click on a crumb (`Framework/ASM/Crumb`) opens `Framework/ASM/CrumbPopup` beneath it (position from
`event.clientX`; opened `modal=True, overlayDismiss=True`, see section 8.10). Two groups: Show (Mimic, Alarms, Trend of
the node) and Areas (its child nodes, each with its badges), from `cadre.hmi.crumb_menu`. A row
navigates and closes the popup. On the pivot pages the trail follows `session.custom.contentNode`
(`cadre.hmi.frame_crumbs`).

### 8.5 The Global Search

A 300 px text field in the top bar, placeholder "Search pages, devices, tags", bound both ways to
`session.custom.searchQuery` with `deferUpdates` and `rejectUpdatesWhileFocused` false, so that the query follows each
key. The field opens no popup. The first design opened `Framework/ASM/SearchResults` as a popup on a click; the popup
took the keyboard focus, so only the first character reached the field, Enter and Escape never reached its
`onKeyDown`, and the popup never closed (measured on the gateway, 2026-10-24). The results now stand in the page.

1. **Panel.** `Framework/ASM/SearchResults` is embedded as the last child of the root of every page of an ASM child
   (`framework.search_panel`: diagram pages, stub pages, the Alarms and Trend pivot pages, the alerts and trends
   pages, the component test page). The embed is out of the flow (style `position: absolute`, the four sides 0, `zIndex`
   50, a declared value of the style property `position`) and shows while `session.custom.searchOpen` is true and the
   query is not empty. The view fills the page and draws one thing, a 420 px panel at the top right corner, above
   the canvas; the transparent regions to the left of the panel and beneath it close the panel on a click, so a
   click on the page outside the panel closes it. The rows are bound to the query only while the panel is open.
2. **Keys.** Any key but Enter and Escape sets `searchOpen`. Enter acts on the first row that acts
   (`cadre.hmi.search_first`) and, through the row's `close` of `search`, clears the query and closes the panel; with
   no row the panel stays and says so. Escape clears the field and closes the panel. A click on the field opens the panel
   again where a query is left. A row click acts and closes the same way.
3. **Index.** `session.custom.searchIndex`, written by the generator (`navigation.search_index`) in compact
   lists to keep the session small. Pages `[route, title, node path, level]`; devices `[folder, kind, title,
   label, route, node path, faceplate 0 or 1]`, one for each device in the device index, with the route of
   the page of the deepest node that draws it; tags `[path, description, unit, device index or -1, tab]`,
   from the tag model: every tag of a device, and every other tag with a description or an alarm. The eng02
   slice (311 tags) makes about 35 kB; a tag costs about 80 bytes.
4. **Match.** Case-insensitive on the fields of the entry. Rank: exact identifier, then prefix, then
   substring; groups Pages, Devices, Tags; at most nine results for each group, so that the 30 rows of the
   design include the three group titles.
5. **Actions.** A page opens its route. A device opens its page and then its faceplate on Home (where its
   kind has a faceplate). A tag opens its device's page and faceplate on the tag's tab: Alarms for a tag with
   an alarm, Config for a member under `cfg/` or `mnt/`, Interlock under `ilk/`, otherwise Home; a tag of no
   device is listed disabled. The faceplate is always opened through `library.open_device`.
6. **Not built.** The ring around the symbol (`api.locate` of the design) has no stock equivalent.

### 8.6 The Page Header and the Pivot Pages

`Framework/ASM/PageHeader` (36 px), from `cadre.hmi.page_header(session, route)`: the page title and its
display level word; the pivot Mimic, Alarms, Trend of the page's node; the node's pages as tabs where it
has more than one; and the previous and next pages, with the title of the target, disabled where the
descriptor names none. Alarms and Trend are two pages of every ASM child:

| Route | View | Content |
|---|---|---|
| `/node/alarms` | `Framework/ASM/NodeAlarms` | the alarm status table over the alarms of the devices of `session.custom.contentNode` and the nodes beneath it, with Ack selected and Ack all beneath it (section 8.12); the root, or an empty node, shows the whole alarm scope |
| `/node/trend` | `Framework/ASM/NodeTrend` | a `Trend/Card` for each historised member of those devices (`cadre.hmi.node_trends`), over 1, 8 or 24 h |

The pivot buttons write `contentNode` and navigate; the top bar's trail and the header follow it.

### 8.7 The Bottom Alarm Banner

`Framework/ASM/AlarmBanner` (76 px), from `cadre.hmi.banner_alarms`: one query over the alarms of the open page's
node and the nodes beneath it (section 8.12; the whole alarm scope on a page that names no node); the three most important alarms (unacknowledged first, a cleared and unacknowledged alarm among them, then
priority, then newest), each as `Framework/ASM/BannerRow` (24 px): the priority icon by rank (triangle for
Critical and High, circle for Medium, square for Low, neutral circle for Diagnostic), flashing while the
alarm is unacknowledged (`cadre/alert/flash-*`), the time, the node, the device tag, the description and
the state words (Unacknowledged, Acknowledged, Cleared, unacknowledged). A click opens the device's
faceplate on the Alarms tab through `library.open_device`. At the right: the counts of the active alarms by
priority (`Framework/Badges`) and All alarms, which shows the root node's Alarms page. The Simulation button
of the design belongs to the content. The rows' column stretches to the banner's height (`position.align`
`stretch`): in a row that centres its children, a column whose rows are a repeater with no basis had no
height, and its rows hung from the banner's middle beyond its edge (first gateway run, 2026-10-24).

### 8.8 Descriptor Keys

Three optional keys of `screen` (schema `screen-descriptor.schema.json`), used only by `--frame asm`:

| Key | Type | Meaning |
|---|---|---|
| `level` | string, at most 40 characters | the display level word of the header, for example `Level 2 unit` |
| `previous` | route, starts with `/` | the page of the header's previous button; the route of another descriptor of the set |
| `next` | route, starts with `/` | the page of the header's next button; the same rule |

```json
{"screen": {"id": "Intake", "route": "/intake", "title": "Intake", "view": "Screens/Intake", "layout": "diagram",
            "node": "Plant/Intake", "level": "Level 2 unit", "previous": "/", "next": "/filtration"}}
```

A `previous` or `next` that names no descriptor stops the build (`navigation.frame_errors`).

### 8.9 Session Data

Written by a child built with `--frame asm` (all have defaults in the parent's session properties):
`frame` (`asm`), `pageInfo` (by route: title, level, previous and next with their titles), `searchIndex`,
`contentNode` (empty means the root). Written at run time: `floating`, `searchQuery`, `searchOpen`, `navQuery`,
`navPanel`.

### 8.10 Popups Open Modal

Every frame popup (`crumbPopup`, `alertMenu`, `brilliance`, `userMenu`) opens with `modal=True, overlayDismiss=True`, so
that a click outside it closes it and the sign-in and sign-out component in the header collapses as an operator expects.
The library's top bar (`framework.top_bar`) opens its three popups this way as well, so the default frame has the
same behaviour. The overlay a modal popup draws is Perspective's default: neither the registry nor the repository's
measurements show how the overlay is styled, so the theme stylesheet does not restyle it. Whether the default overlay
dims the page is to be seen on the gateway; a clear overlay is then a stylesheet rule on the overlay's class, recorded
here once it is read from the DOM.

### 8.11 The Canvas Zoom and the Toolbar

Every diagram screen has a view property `custom.zoom` (number, default 1) and draws its diagram at the scale
`s = fit * zoom`, held in `custom.scale`. `fit` is the scale the descriptor key `screen.fit` asks for
(`parts.fit_expression`: the smaller ratio of the viewport, less what the frame takes, to the page, never above 1;
the viewport loses the faceplate dock's 400 px while `session.custom.faceplateDocked`); a page that states no `fit`
has a fit of 1. The zoom is held to 0.5 to 4.

1. **Structure.** `Canvas` (flex column, `meta.domId` `cadre-canvas`) holds `Sizer` and, under the module rendering, the
   module's zoom component. `Sizer` has the scaled size of the diagram: its width, height and flex basis are bound to
   `W * s` and `H * s`, since a CSS transform changes no layout size. `Sizer` holds `Diagram` (W by H px,
   `transformOrigin` top left, `transform: scale(s)`). `Canvas` scrolls; a fitted page keeps `overflow: hidden` until
   the zoom is above 1, so that a fraction of a pixel never draws a bar at the fit.
2. **Controls.** `UserToolbar` is a sibling of `Canvas`, outside the scaled box: minus, the percentage (a click returns
   to 100 %) and plus, each step 1.25 times. The header, the banner, the navigation dock, the faceplate dock and the
   floating faceplates are views of other docks and popups, so no zoom scales them.
3. **Module component.** `cadre.ob.canvaszoom` (Ctrl+wheel, two-pointer pinch, Ctrl+plus, Ctrl+minus, Ctrl+0 over the
   canvas) is emitted as the last child of `Canvas` only when the render is `module` and `module/components.json` lists
   it; its `zoom` is bound both ways to `view.custom.zoom`, and each of `min`, `max`, `targetDomId`, `guardBrowserZoom`
   only when the registry lists that prop for it (`screen.canvas_zoom_node`). It is a flex item of no size.
4. **Color.** The Color toggle of the toolbar paints the pipes in their medium (`pipes_svg`); it is shown only on a page
   with a pipe whose medium is not neutral (`screen.pipes_carry_medium`). The buses carry no medium and stay grey.

Code: `tools/hmi/screen.py` (`zoom_controls`, `toolbar_node`, `canvas_zoom_node`, `diagram_screen`),
`tools/hmi/parts.py` (`scale_expression`, `apply_fit`), `tests/test_asm_zoom.py`, the fit tests of
`tests/test_asm_parts.py`. Not proved offline: that the transform, the sizer and the scroll agree on the glass at a zoom
above and below 1, and the pinch.

The fit reads the canvas the module measures (module 0.4.1, `view.custom.canvasW` and `canvasH`, bound from the
canvas zoom component) wherever both are above zero, and only otherwise the viewport less the frame and the session's
`faceplateDocked` flag: that flag outlives a reload and is shared by every tab of a session (GF-94). On the gateway
(2026-10-24) the three eng02 pages fill a 1920 by 1080 window at 1.0, after a reload with a faceplate docked as well,
and refit to 0.8 beside the open dock.

### 8.12 Level 5: the Banner by Page, Ack Selected and Ack All

Two changes of the alarm surfaces of the ASM frame (COB-166; the owner's review of `cadre_hmi_eng02_asm`).

**The banner follows the page.** `cadre.hmi.banner_alarms(session, route)` takes the route of the open page, which the
banner binds from `{page.props.path}` (the form of the top bar's crumbs). The page's node is `frame_node(session, route)`;
the alarms are those of that node's devices and of every node beneath it (`node_sources`, the sources of each device). On
`/node/alarms` and `/node/trend` the node is `session.custom.contentNode`, and an empty one (the root of the pivot pages) shows
the whole alarm scope, as All alarms does. A page with no node (the support pages, the component test page), a project
without a hierarchy and a call without a route show the whole alarm scope as before. A node none of whose devices carries a
source matches nothing, never everything. The rows and the counts of priorities come from the same query, so the counts follow
the rows. All alarms and the top bar's alert count are unchanged: they stay over the whole scope.

**Ack selected and Ack all.** Two buttons in the library's style under each alarm list (`tools/hmi/acks.py`): on
`Framework/AlertsPage` (its Active tab), `Framework/ASM/NodeAlarms`, `Framework/AlertMenu` and `Faceplate/Alarms`, in both
renderings. They are shown to everyone and are disabled without the permission of their write path, as every command is; the
checked write (`cadre.hmi.ack`) refuses again. Ack selected acknowledges the rows the operator selected, and is disabled while
none is. Ack all acknowledges the unacknowledged alarms the list shows (the node and its subtree, the filters applied) after the
Confirm row of page 13 section 10.5, which reads "Acknowledge N alarms?" with Confirm and Cancel. The paths follow the
list: W7 on the pages and on the stock tables (the table's own acknowledge), W8 for Ack selected and W9 for Ack all on the module's
panels.

Table 5. Where each list takes its selection and its rows from.

| List | Selected rows | Rows it shows |
|---|---|---|
| Stock `ia.display.alarmstatustable` | `props.selection.active.data` | `props.filters.active.results.data`, with `filters.active.results.enabled` true |
| `cadre.ob.alertpanel` and `cadre.ob.alertlist` (module 0.4.2) | `props.selectedIds`, with `selectable` true (bound two ways to `view.custom.selected`) | the alerts the view's poll gave the list |

The module's properties are emitted only where `module/components.json` lists them (`screen.module_props`); a build before
module 0.4.2 has Ack all and no Ack selected. The ids of both forms go through `cadre.hmi.selected_ids` and
`unacked_ids`, then `cadre.hmi.ack` (`ack_listed`), which keeps only the ids of the session's alarm scope.

### 8.13 Not Verified Without the Gateway

Nothing of section 8 before 8.12 has run on the gateway, and neither has the selection and the written back rows of Table 5;
the checks are offline (`tests/test_asm_frame.py`, gates
G0 to G7). Each of these rests on the corpus or on an assumption, and is to be seen at G8 and G11:

1. A popup opened by an event script with the keywords of the corpus (`id`, `view`, `params`, `title`,
   `position`, `showCloseIcon`, `draggable`, `resizable`, `modal`, `overlayDismiss`, `viewportBound`);
   several popups open at once; `closePopup` on an identifier that is not open; the popup keeping its
   position across a page navigation.
2. `position` with `top` and `right` for a floating faceplate, and `left` from `event.clientX` for the
   crumb and search popups (the sides are documented; the pixel meaning is the existing frame's).
3. The text field's `dom.onClick` and `dom.onKeyDown` (the corpus lists both; `event.key` is read as a
   plain attribute), and `deferUpdates` false giving a binding update for each key.
4. Escape closing the dock; the `modal` navigation dock closing on a click outside (measured: it does).
   **Corrected 2026-10-24:** `overlayDismiss` does not close a non-modal popup on an outside click (measured on
   8.3.6: the search, crumb, alert and user popups all stayed open and stacked). A popup that must close on an outside
   click opens `modal=True, overlayDismiss=True`: the user menu, the brilliance menu, the alert menu and the crumb
   popup do (section 8.10). A floating faceplate stays non-modal, by design.
5. A binding on `props.style.paddingLeft` of a flex container (the indent of a list row), and the
   `props.params.tab` binding on an embedded faceplate whose view may not declare `tab` yet.
6. Several top docks and a bottom dock in `sharedDocks`, stacking in the order of the array.

## 9. The ASM Pipeline Commands

Five commands of the repository turn the documents of the migration workflow into an ASM project and its previews
(WorkflowBuilder revision B8 Table 109, rulings WFBD-091 and WFBD-092). Each generalises a tool that the eng02 proving
slice wrote by hand; each reads the library's own catalogue (`library/contracts.json`, `library/profile.json`,
`module/components.json`), so that a library change is seen by the next run. Each writes a document that carries a
`schema` of the form `cadre-hmi-<name>/<n>` (the schema file in `schemas/` carries the same identifier in `$id`) and a
`provenance` object (the tool, the repository commit, whether the tree was dirty, the command line without any secret,
the inputs by path and SHA-256, the interpreter). Nothing here contacts a gateway.

### 9.1 The Model: `tools/hmi/asm_model.py`

Inputs: the understandings (`wfb.migration.understanding/1`, one list file of paths), the faceplates, the tables
(`ctig.tables/1`), the openers (`ctig.popup-openers/1`), the inventory folder (`ctig.inventory/1`), and optionally the
runtime menu, the contract, the device model, the one to one pictures and a map of support targets to library routes.
Output: `model.json` (`cadre-hmi-asm-model/1`) and one folder `pages/<page>/` for each built page (`page.json`,
`understanding.json`, `inventory.json`, `runtime.png`, `preview.png`).

1. The hierarchy follows the menu's order (`--hierarchy menu`: the site, then one node for each menu group that holds a
   page of the migration) or the contract's areas (`--hierarchy contract`). A menu target with no understanding is a stub
   page; a target that names a library support page (Alarm, Trend by default) resolves to the library's route and is
   no node; a pop-up set is never a page.
2. Every entry of every section has a mapping row with a `uid` (`<unit>:<id>`; a static object is `<unit>:s<an>` and a
   dropped one `<unit>:x<an>`), and a place: a page, a faceplate tab, `dropped` or `frame`. An entry that cannot be mapped
   is in `unmapped`.
3. A device's home page is the owner page of its faceplate, else the first page that draws it, and its node is that
   page's node. A device drawn on another page is a plain symbol there that still opens its faceplate (Level 5).
4. Every original target (menu, navigation entry, opener, previous and next of the pages table) has a `nav` row with a
   resolution of `page`, `faceplate`, `support` or `not_migrated`, with its route, its faceplate and tab, or its reason. An
   opener the faceplates document cannot place has no resolution and is in `unresolved`.
5. A priority comes from the tables' category table, or, without one, from the category's rank (High, Medium, Low,
   Diagnostic) with `inferred` true.

Exit codes: 0; 2 an entry is unmapped or a target unresolved; 1 an input fault.

### 9.2 The Descriptors: `tools/hmi/asm_descriptors.py`

From the model and one design (`wfb.migration.design/1`) per page it writes the layout that the generator and the gate
blocks read in place, under `bridge/`: `build.json` (`ctig.bridge.build/1`, the `screen.py` command line with `--parent`,
`--frame asm`, `--faceplate asm`, `--render module` and, when asked, `--component-test`), `descriptors/*.json`,
`devices.json`, `tags.json` (the whole ASM tag model, with the simulation's `sim/tick` when asked), `tags_devices.json`
(the same without the simulation), `coverage_map.json`, `route_map.json` and `walk/walk.json` (`ctig.bridge.walk/1`, the
plan commands of the walk's two modes). Beside it: `coverage.json` (`cadre-hmi-descriptor-coverage/1`), `tags-document.json`
and `gaps-after.json`.

1. A device's symbol, with `device` and so its node, is drawn on the device's own page only; elsewhere the symbol is
   plain and carries `faceplate`. A device whose kind has no library device kind (a switch) stays a standalone symbol.
2. A kind the library lacks is drawn as the library's counted gap box and is a gap that must be accepted (`--accepted`);
   `coverage.json` names for each kind used whether the module, the library or nobody draws it (`module_first`).
3. `--equalise` gives the items of one column the widest width and the items of one row the tallest height (within 4 px);
   the design's stated columns are recorded with their widths. `--medium` gives a pipe the medium of its flow.
4. Every mapping row must be carried by an element, by a faceplate, by an accepted gap or by an accounted treatment
   (dropped, frame, a link to a page that is not migrated); every route of the navigation table must resolve. Otherwise the
   exit code is 2.
5. The designs state no unit, format, pipe routing or medium (the manager's schema refuses them). A readout's unit and
   format come from the tags document's variable that the item reads (a variable with no format states none, and none is
   invented); a pipe takes the original's routing, medium and ends from the model's `flows` (found by the item's
   `original_an`), its points scaled by the design's canvas. A lamp follows the alarm whose source variable it reads.
6. The walk's plan commands carry `--faceplate` (the planner `tools/compare/walk.py plan` already takes it), so an asm
   project is planned with the asm faceplate style. `openbridge.walk_plan` must allow the option.

### 9.3 The Gaps: `tools/hmi/library_gaps.py`

One row for each kind the designs use: its count and pages, whether the module's part (`cadre.ob.<kind>`), the library's
view or nobody draws it, and why (OpenBridge first with `--module-first`). A kind nobody draws is a gap with a status
(`open`, `partial`, `closed`, `accepted`) and a reason; `open_count` is the open and partial gaps that no accepted list
names. The audit table is also written as `audit.json`. Exit code 2 means open gaps.

Two further modes and one option serve the project survey (NOTE-WFB-10 sections 7.5 to 7.8, 8.2, 9.2 and 11.4; the code
is `tools/hmi/placement_survey.py`):

1. `--survey <ctig survey>` places each kind and feature of a ctig survey (`ctig.survey/1`) by the catalogue, then the
   reviewed or approved rows of `module/openbridge-map.json`, then the count against `--local-max` (Table 7.5), and
   writes `survey.json` (`cadre-hmi-project-survey/1`), `unmapped.json` and `proposal_source.json` to `--out`. Earlier
   surveys (`--prior-local`), a page run's late rows (`--late`), the model's `--proposals` and the owner's `--changes`
   are inputs; a run given `--changes`, even an empty list, is final. The tool writes no approval record. Exit 0, or 1
   for a fault.
2. `--release <survey.json>` writes the project release's gap list (`cadre-hmi-library-gaps/2`): one open gap for each
   `openbridge` and `shared_gap` placement, `GAP-<kind>` or `GAP-<kind>-<feature>` with each colon a hyphen. Exit 0, or 1.
3. Page mode with `--project-survey <survey.json>` (and `--openbridge-map` for the late rule `map`) places a kind the
   library does not draw by the survey: `local` is drawn as an assembly; `openbridge` and `shared_gap` are `unbuilt`
   and the run exits 3. A kind or feature the survey does not hold is a late gap (rules `map`, `twice`, `second`,
   `once`, `feature`) written to `late[]` for the next survey. Without a survey the output is `cadre-hmi-library-gaps/1`
   exactly as before.

### 9.4 The Preview: `tools/hmi/preview.py`

One renderer (`tools/hmi/preview_assets/renderer.js` and `style.css`) draws both previews from data: mode `recon`, the one
to one view at the original's geometry with the pop-up sets as faceplate content, and mode `asm`, the model's hierarchy,
the designs, faceplates that dock and float, and search. It writes `site/` (the multi-file preview), `preview.html` (one
self-contained file), `pictures/` and `checks.json` (`cadre-hmi-preview-checks/1`).

1. The bundle is inert (WorkflowBuilder section 29.9). Its one script is the renderer's fixed text, pinned by a content
   security policy and recorded by SHA-256 in `script_hashes`; the run's data is in one `type="application/json"` block with
   `<`, `>` and `&` escaped, read through `textContent`; there is no inline handler, no `javascript:` address and no external
   reference. The command counts all three itself and fails the run on any.
2. The checks run in headless Chromium with real input: `coverage` (every uid or treatment is a `data-uid`), `navigation`
   (every row is walked and ends where its resolution says), `search`, `dock` and `float` (the faceplate docks inside the
   window, floats, is dragged and docks again). The recon mode runs the first two by default.
3. Exit codes: 0; 2 a check or the bundle failed; 1 a fault. The checks and pictures need Playwright (ctig's `.venv`).
4. In the recon mode a navigation item is the original's touch area, not a drawn button (COB-180): a transparent hotspot with a thin
   dashed outline and its label as the title, under every drawn object it covers; the `navigation` check presses it directly.
   Indicators that share one box are a status list and are drawn one row each, a lamp's label on one line.

### 9.5 The Side by Side Pictures: `tools/compare/sidebyside.py`

For each page and faceplate, one picture of the original beside up to three renderings (preview, asm, ignition), composed
in headless Chromium at each picture's own size; a missing picture is a labelled gap and exit code 2. With `--sheets` the
last two columns are tiled page by page in one fixed grid (two sheets of equal size), so that one image comparison covers
every page. `manifest.json` (`cadre-hmi-sidebyside/1`) names each source by path and SHA-256.

### 9.6 The Page Checks: `tools/hmi/page_checks.py`

The offline checks of a built page set: the coverage of the mapping rows, the navigation table walked, and every value
component on a tag. With `--canvas WxH` (the page canvas of the frame at the profile's window, for example `1900x860`) it
also runs the layout family over each diagram page that draws a symbol, a stub page being skipped, and writes the findings
as `layout {canvas, pages, findings[{page, rule, id, reason}], count}` in `checks.json`; a finding gives exit code 2. The
rules are objective: L1 the page is no larger than the canvas, since a larger page renders below scale 1.0 and its text
shrinks; L2 the page is at least 95 per cent of the canvas each way and its elements reach 90 per cent of its width and
85 per cent of its height; L3 a free line is only an interlock (dashed) or a gated bus, every other flow being a pipe from
and to its symbols or junctions; L4 the readouts whose `x` lie within 4 px form a column and share one width (the
`columns` key lists each column); L5 with `--require-stretch` every readout states `params.stretch` true; L6 every switch
states `params.vertical`; L7 every motor, pump, fan, valve, switch, generator and indicator states `params.readoutPosition`;
L8 the toolbar is not switched off. A generator drawn as a picture is exempt from L7 because it writes its own status.

Three further rules measure what the first eight leave open. L9 (alignment): where the router bends a pipe of its own
(`diagram.route`), a symbol end joined to a symbol on the same axis, or to a via point it would reach sideways, has its
adjacent point on the symbol's centre line within 2 px, so that no jog results; a switch (or any symbol with a `vertical`
parameter) has `vertical` true when its pipes meet it on top and bottom, false on left and right, and mixed sides are a
finding; an in-line switch (pipes on two opposite sides) states `readoutPosition` none, because the `Automation/Switch`
view centres its icon with its identifier inside an embed that the generator sizes for the whole readout extent, which
measured 28 px off the line for a horizontal switch with the readout on top and 13 px and 9 px for vertical switches with
it left and right (`INLINE_VIEW_KINDS` holds the kinds measured to do this). L10 (text): a label's text, estimated at
6.0 px a character at the 12 px label font (a lower bound; the render measured 6.0 to 6.9) and scaled for the body (16 px)
and heading (24 px) styles, fits its box plus 4 px or the lines its height allows, and so does the title a sequence or an
instrument field draws across its symbol; the texts of labels, the boxes of symbols and the title band of a section (top
right inside it, label font, 8 px and 4 px of padding) overlap by no more than 2 px, and a section nested in another does
not cover that section's title band. L11 (label order, with `--inventory DIR`, the original's text objects as
`<DIR>/<page>/inventory.json` or `<DIR>/<page>.json`): labels matched to one text object each by their text with
whitespace collapsed and case folded (a text that occurs twice on either side is skipped), which the original has in one
column (x ranges overlap, y apart by 8 to 200 px) or one row (y ranges overlap, x apart by 8 to 300 px), keep that order
in the page, unless their built positions differ by less than 8 px. L12 (pipe ends): a loose pipe end (x and y, joined to
nothing) carries an arrow, `arrow-in` where the flow enters or `arrow-out` where it leaves, never a cap or a plain end;
and a feeder (a pipe with no medium or the neutral one) ends in an arrow just above the motor it feeds rather than
joining it. A process flow through a machine carries its medium and is no feeder.

### 9.7 What Is Proven Here

The commands are proven offline on synthetic inputs with placeholder names (`tests/fixtures/asm-*.json`): the descriptors
pass the generator's gates G0 to G7, and the previews pass their checks in a browser. A real run on the migrated slice is
the integrated run's work, not this section's.
