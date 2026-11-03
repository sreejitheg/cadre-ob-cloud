# Frame Design for Tranche T2: the OpenBridge Frame Option

Prepared 2026-11-03 as a read-only survey. It changes no code, test, schema, wiki page or generated file. Sources:
`tools/hmi/framework.py`, `parent.py`, `navigation.py`, `navigation_scripts.py`, `screen.py`; `wiki/04` sections 2, 3, 7
to 9; `wiki/13` sections 10 and 11; `tools/compare/glass.py`, `glass_gates.py`, `functional.py`; the pinned manifest
`module/web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json` and the `dist/` sources of the 33
elements; `module/tools/gen_module_assets.py`; `cloud/REPORT-T1.md` and `cloud/WRAP-RECIPE.md` section 6.1.

## 1. The Current Frame

### 1.1 Parts of the `openbridge` frame

The frame is five docks and popups written by `framework.shared_docks` into every child's page configuration (top 48 px
`Framework/TopBar`, left 320 px modal `Framework/NavMenu`, right 400 px `Framework/SideMenu`), and the route `/alerts`.

| Part | View | What it does |
|---|---|---|
| Top bar | `Framework/TopBar` (flex row of 10 children) | Menu button (dock `toggle` action on `nav`), `AppName`, `PageName` (`cadre.hmi.page_title`, hidden when crumbs exist), `Crumbs` repeater, spacer, alert message, `AlertButton`, `BrillianceButton`, `UserButton`, `Clock` |
| Alert message | `AlertMessage` in the top bar | The most severe active alarm (icon coloured by `PRIORITY_VAR`, text, time) and an ACK button (path W6, `cadre.hmi.ack_top`); shown while `custom.alarm.count > 0` |
| Alert button | `AlertButton` | Bell and count, flashing `cadre/alert/flash-alarm` while any alarm is unacknowledged; opens `alertMenu` |
| Alarm summary | `custom.alarm` | Bound to `cadre.hmi.alarm_summary(session.custom.alarmScope)` every 2 s (`now(2000)`): `count`, `unacked`, `highest`, `topLabel`, `topTime` |
| Breadcrumb | `Framework/Crumb` and `Framework/Badges` | `cadre.hmi.crumbs(session, page path)` every 2 s: the nodes root to page, each with priority badges; a click navigates to the node's first page (wiki 04 section 7) |
| Navigation menu | `Framework/NavMenu`, `NavItem` | Two flex repeaters over `session.custom.nav.items` (polled through `cadre.hmi.nav_items`, which adds node badges) and `.footer`; item selected when its path equals `page.props.path`; click calls `system.perspective.navigate` then `closeDock('nav')` |
| Alert menu | `Framework/AlertMenu` popup, 640 by 468 | Stock `ia.display.alarmstatustable` (module rendering: `Framework/AlertMenu` overridden by `alert_menu_module`, the alert page of `cadre.ob.alertpanel`), Ack selected and Ack all (W7; W8 and W9 on the module panel), link to `/alerts` |
| Alerts page | `Framework/AlertsPage` | Active and History tabs over the alarm status and journal tables |
| Brilliance | `Framework/BrillianceMenu` popup | Day, dusk, night, bright; `cadre.hmi.set_palette(session, key)` writes `session.custom.palette` and the Ignition theme |
| User menu | `Framework/UserMenu` popup | User name, Sign in (`system.perspective.login()`), Sign out (`logout()`), by `session.props.auth.authenticated` |
| Clock | `Clock` label | `dateFormat(now(1000), 'HH:mm') + clockLabel` |
| Docks and popups | `_open_menu` | Popups open `modal=True, overlayDismiss=True`, top 48, right 8 or 56 (GF-70); the nav dock is modal (GF-71) |
| Faceplate dock and popup | `SideMenu`, `FaceplatePopup` | Out of scope here: they are device views, not the frame; they stay as they are |

Session properties read: `alarmScope`, `nav.items` and `.footer`, `hierarchy`, `palette`, `faceplateMode`, `selected*`;
`session.props.auth.*`; `page.props.path`. Scripts called: `cadre.hmi.alarm_summary`, `ack_top`, `page_title`,
`crumbs`, `nav_items`, `set_palette`, `permissions` (the `custom.can` flags, CAN_CFG), `ack` and `alarm_list`.
The alarm query is `system.alarm.queryStatus` through `alarm_summary` and `alarm_list`; the acknowledge path is
`cadre.hmi.ack` (W6 top bar, W7 stock tables, W8 and W9 module panels) with the `Administrator` check of COBD-024.

### 1.2 Parts of the `asm` frame (`--frame asm`)

`navigation.py` replaces the docks (Table 4 of wiki 04): top `Framework/ASM/Head` (84 px: `ASM/TopBar` 48 px over
`ASM/PageHeader` 36 px, one dock because two top docks show only the first, GF-90), left `ASM/NavDock` (320 px modal,
two states `pages` and `support`), right `SideMenu`, bottom `ASM/AlarmBanner` (76 px).

| Part | View | What it does |
|---|---|---|
| Top bar | `ASM/TopBar` | The library bar with `Titles` (app name over site note), a menu button opening the dock on `pages`, a second button on `support` (`session.custom.navPanel`), the trail, the 300 px search field before the alarm summary; the alert message, bell, brilliance, user and clock unchanged |
| Trail | `ASM/Crumb`, `ASM/CrumbPopup` | `cadre.hmi.frame_crumbs`; a click opens the popup with Show (Mimic, Alarms, Trend of the node) and Areas, from `cadre.hmi.crumb_menu` |
| Navigation dock | `ASM/NavDock`, `ASM/ListRow` | `cadre.hmi.nav_tree(session, query, route)` (every node, badges, pages beneath), search box on `navQuery`, support list `nav_support`; row click navigates, opens the device faceplate (`library.open_device`) and closes the dock |
| Search | `ASM/SearchResults` | `cadre.hmi.search`, `search_first`; `searchQuery`, `searchOpen` |
| Page header | `ASM/PageHeader` | Title and level word, the pivot Mimic, Alarms, Trend of the node (writes `contentNode`, routes `/node/alarms`, `/node/trend`), page tabs, previous and next (`cadre.hmi.page_header`) |
| Alarm banner | `ASM/AlarmBanner`, `BannerRow` | `cadre.hmi.banner_alarms(session, route)`: three most important alarms of the page's node subtree, priority counts, All alarms |
| Floating faceplates | `ASM/FloatFaceplate` | Popup per device (`float_id`, `float_position`); not frame chrome |
| Node alarm and trend pages | `ASM/NodeAlarms`, `ASM/NodeTrend` | Pages, not frame chrome; they stay |

ASM rules the frame must keep (wiki 04 sections 7 to 9; wiki 13 sections 10 and 11): the hierarchy and its
`session.custom.hierarchy`; counts per node rolled up over the subtree (`node_counts`); badges by priority colour
rank (13 section 11.1); the breadcrumb of nodes with badges; one top dock holding the bar and the header (GF-90); modal
popups (GF-70); the faceplate style and pin; Ack selected and Ack all behind the Confirm row (13 section 10.5, 04
section 8.12); `contentNode` for the pivot pages.

### 1.3 What the glass and G10 rely on

1. `glass.BELL = '[data-component-path="T[0].0:6"]'`: the seventh child of the top bar's root. A unit test
   (`test_walk` TopBarPathTests) holds the index to `framework.top_bar()`; the alert message moved it in T0.
   `open_alarm_menu` clicks it and polls `obc-alert-list-page-small` (`PANEL`); `functional.frame_steps` (F21) calls it.
2. `glass.sign_in` and `_open_user_menu`: the user button is the third `ia.container.coord` of the top dock
   (`by_container`), or the last of three SVG icons whose centres lie within 44 px of the top (`TOP_ICONS`, the ASM
   fallback `by_icon`); the entry is looked up in `.ia_popup` as a button or text `Sign in` or `Sign out`, then the
   gateway login page (`input[name=username]`, `password`) is filled.
3. F16 (nobody signed in): top bar ACK disabled, the alerts page offers no Acknowledge, the module alarm menu
   offers no ACK and ACK visible is disabled. F17 and F18: signed in, the acknowledgement carries the user name.
4. F20 (toolbar of the page, not the frame) and F21 (the alarm menu and the nav dock close on an outside click and on
   their close button: `popup_open`, `dock_open`, `dock(page, "top")`, the first `coord` as the menu button, the
   header's close `coord`, `OUTSIDE = (300, 750)`).
5. `glass_gates.gate_menus` (ASM frame, right[2] of the three menu icons), `gate_banner`, `gate_search`, `gate_alarm`
   (the top bar's alert count rises: it reads the bell text), `gate_ack`.
6. Every command press goes through `glass.button` and `dock_button`, which answer the Confirm row (13 section 10.5).

## 2. The 33 Components

### 2.1 Classes

Counts come from the pinned manifest. Attribute types such as `TabData[]` are arrays of objects; the generator maps
`array` fields read by `tree.readArray` (GF-38) and prints `skipped` for a type it cannot map.

| Class | Components |
|---|---|
| Frame part (stands on a dock or popup alone) | `top-bar`, `alert-button`, `alert-menu`, `app-button`, `app-menu`, `brilliance-menu`, `breadcrumb`, `clock`, `command-menu`, `navigation-menu`, `system-menu`, `tree-navigation`, `user-button`, `user-menu`, `tab-row`, `pivot-item-group` |
| Child that lives only inside a parent | `alert-button-item`, `alert-menu-item`, `navigation-item`, `navigation-item-group`, `tree-navigation-item`, `tree-navigation-group`, `pivot-item`, `tab-item`, `notification-menu-item`, `notification-message-item` |
| General control | `modal-window`, `tooltip`, `toggletip`, `context-menu-input`, `notification-button`, `notification-badge-button`, `notification-floating-item` |

### 2.2 Attributes, events and slots (condensed from the manifest)

| Element | Attributes | Events | Slots |
|---|---|---|---|
| `top-bar` | 25: `appTitle`, `pageName`, `menuButtonIcon`, `*Activated` (5), `userButtonDisabled`, `tall`, `show*` (7), `inactive`, five `*BreakpointPx`, `settings`, `breadcrumbItems` (`{label, href, icon}[]`, shown only while `settings`) | `menu-button-clicked`, `dimming-button-clicked`, `apps-button-clicked`, `left-more-button-clicked`, `user-button-clicked`, `breadcrumb-click`, `back`, `close`, `emergency-brightness-start`, `emergency-brightness-stop` | `app-icon`, `command-button`, `alerts`, `clock` |
| `alert-button` | `nAlerts`, `alertType`, `type`, `large`, `showSilenceButton`, `silenceButtonDisabled`, `counter`, `globalCounter`, `shelvedCount`, `blinking`, `flashingSpeed`, two breakpoints | `click-alert`, `click-silence` | none |
| `alert-button-item` | `type`, `alertType`, `nAlerts`, `counter`, `globalCounter`, `shelvedCount`, `blinking`, `flashingSpeed`, `fillHeight`, `aria-label` | `click` | none |
| `alert-menu` | `hasShelved`, `canAckAll` | `ack-all-visible-click`, `silence-click`, `go-to-alert-list-click` | default (items), `empty-<tab>-title`, `-description`, `-icon` |
| `alert-menu-item` | `hasIcon`, `shelved`, `title`, `description`, `day`, `time`, `status`, `open`, `size`, `animateIntro`, `secondaryActionLabel`, two action states | `item-click`, `ack-click`, `ack-secondary-click` | `alert-icon`, `title`, `description`, `icon` |
| `app-button` | `label`, `checked`, `integration`, `size`, `disabled` | `click` | `icon` |
| `app-menu` | none | `search` | default (app buttons) |
| `breadcrumb` | none (property `items`, `{label, href, icon}[]`; `icon` is a template function) | `breadcrumb-click` | none |
| `brilliance-menu` | `palette`, `brightness`, `showLinkBrightness`, `showLinkPalette`, `variant`, `brightnessUnit`, `brightnessMax`, two steps, `brightnessInputVariant`, `showScreenControlLink` | `palette-changed`, `brightness-changed`, `link-palette-changed`, `link-brightness-changed`, `screen-control-link-clicked` | none |
| `clock` | `date`, `showSeconds`, `showDate`, `showTimezone`, `timeZoneOffsetHours`, `showYear`, `showWeekday`, `locale`, `hour12`, `selected`, `double`, `activated`, `integrationBarMode`, `blinkOnlyBreakpointPx` | none | default |
| `command-menu` | `inCommand` | `change` | nine text and icon slots (command icon, status, description, location, four toggle labels, toggle icon) |
| `context-menu-input` | `type`, `options` (`{value, label, level...}[]`), `selectedValues`, `hasTitleBar`, `title`, `columnGroups`, `itemsPerColumn`, `multiSelect`, `selectPerGroup` | `close`, `item-click`, `change` | default |
| `modal-window` | `size`, `hasOptionalAction`, `hasLeadingIcon` | `close-click`, `cancel-click`, `done-click`, `option-click` | `leading-icon`, `title`, `content`, `option-label`, `cancel-label`, `done-label` |
| `navigation-item` | `label`, `href`, `checked`, `variant`, `group`, `groupSelected`, `hasIcon`, `hasTrailingIcon`, `treeMode`, `treeBranches`, `terminalType`, `alerts` | `click` | `icon`, `trailing-icon` |
| `navigation-item-group` | the same plus `hug`, `defaultOpen` | `open` | `icon`, default (child items) |
| `navigation-menu` | `variant`, `flyoutVariant`, `smallScreen` | none | `main`, `footer`, `logo` (the menu reads `this.children` and their `slot` attribute) |
| `notification-button` | `buttonStyle`, `count`, `showCount`, `isActive`, `ariaLabel` | `obc-click` | `icon` |
| `notification-badge-button` | `openRight`, `openLeft`, `cornerLeft`, `cornerRight`, `icon`, `disabled`, `indent` | `click` | default |
| `notification-floating-item` | `type`, `direction`, `hasTimestamp`, `hasDay`, `action`, `action2`, `lineType` | `action-click`, `action2-click`, `dismiss-click` | `primary-icon`, `title`, `description`, `time`, `day`, `action`, `action2` |
| `notification-menu-item` | `hasIcon`, `title`, `description`, `day`, `time`, `open`, `size`, two action labels | `item-click`, `primary-action-click`, `secondary-action-click` | `icon` |
| `notification-message-item` | `title`, `description`, `time`, `timeSecondary`, `actionLabel`, `type`, `size`, `hasTimestamp2`, `hasSecondaryIcon`, `large`, `empty`, `emptyText` | `message-click`, `action-click` | `secondary-icon` |
| `pivot-item` | `value`, `selected`, `direction`, `hasLeadingIcon`, `hasLabel`, `label`, `disabled` | `selected` | `icon` |
| `pivot-item-group` | `direction`, `selectedValue`, `allowDeselect` | `change` | default (pivot items, found by `querySelectorAll`) |
| `system-menu` | `condensed`, `showSettingsButton`, `activeSubMenu`, `externalControl`, `smallScreen` | 16, among them `wifi-click`, `audio-volume-change`, `battery-mode-change`, `settings-click`, `to-sub-menu-click`, and one named `eventName` | `battery-status` |
| `tab-item` | `hug`, `centerContent`, `checked`, `has-close`, `has-leading-icon`, `has-title`, `has-divider`, `has-badge`, `icon`, `title`, `show-subtitle`, `subtitle`, `disabled`, badge fields | `tab-click`, `tab-close` | `leading-icon`, `title`, `badge-icon` |
| `tab-row` | `tabs` (`TabData[]`: `id`, `title`, `subtitle`, badge fields, `disabled`), `selected-tab-id`, `has-close`, `centerContent`, `hug`, `show-subtitle`, `has-add-new-tab` | `tab-selected`, `tab-closed`, `add-new-tab` | `tab-<id>-icon` |
| `toggletip` | `variant`, `title`, `description`, `hasContent`, `hasActions`, `hasLeadingIcon`, `hasTrailingIcon`, `customWidth`, two button labels | `primary-action`, `secondary-action` | `leading-icon`, `trailing-icon`, `content` |
| `tooltip` | `type`, `variant`, `label`, `showIcon` | none | `icon` |
| `tree-navigation` | none | none | default (rows; the container computes `branches` and a roving tabindex) |
| `tree-navigation-group` | `label`, `branches`, `expanded`, `checked`, `disabled`, `terminalType`, `alerts`, `href` | `expand-toggle` | `icon`, default (child rows) |
| `tree-navigation-item` | `label`, `branches`, `expandable`, `expanded`, `checked`, `disabled`, `terminalType`, `alerts` (`{critical, high, medium, low, diagnostic, combine}`), `href` | `expand-toggle`, `click` | `icon` |
| `user-button` | `variant`, `size`, `styleType`, `static`, `disabled`, `initials`, `label`, `sublabel` | none (a click is the host's) | `icon` |
| `user-menu` | `type`, `size`, `hasRecentlySignedIn`, `username`, `password`, `usernameError`, `passwordError`, `userInitials`, `userLabel`, `userRole`, `primaryActionId` | `sign-in-click`, `sign-out-click`, `recent-user-click`, `use-another-account-click`, `signed-in-action-click` | `signed-in-action-icon-<id>` |

### 2.3 How a Perspective component carries slotted children

The wrapper (`gen_module_assets.py`, `WRAPPER`) already does two things this needs. The `data` key of a spec declares a
property read as plain JSON (`tree.readArray`, GF-38) and converted by `CONVERT` (the alert lists turn alert records into
rows); and `render()` already builds slotted children with `h(tag, {slot, key})` (the tank's `unit` and `readout`, the
duty badge). The mechanism for T2 generalises the second step: a spec key `items` names a data property whose
objects are turned into child elements of the host, each object holding `tag` (from a fixed allow list, never free text),
the element's attributes and a nested `children` list. One mechanism serves:

1. **Menus of items**: `alert-menu` (default slot of `alert-menu-item`), `app-menu` (`app-button`), `pivot-item-group`
   (`pivot-item`), `navigation-menu` (`navigation-item` and `navigation-item-group` in `main` and `footer`, nested to any depth).
2. **Trees**: `tree-navigation` (`tree-navigation-group` and `-item`, with `alerts` as an object per row).
3. **Native array attributes**: `tab-row.tabs`, `breadcrumb.items`, `top-bar.breadcrumbItems`, `context-menu-input.options`
   and `columnGroups`: read as `array` fields, no child elements.
4. **Fixed composition**: `top-bar` renders `obc-alert-button` in its `alerts` slot and `obc-clock` in its `clock` slot
   itself, as the tank wrapper adds `obc-automation-badge`; the wrapper's properties include the nested element's own
   (`nAlerts`, `alertType`, `blinking`, `showSilenceButton`, `date`, `showSeconds`).
5. **Text slots**: a slot that takes text or an `obi-` icon (`title`, `description`, button labels, `command-*`,
   `leading-icon`) becomes a string property, and an icon slot a string name checked against the icons in `dist/icons/`
   (an allow list read from the package, so no icon name is from recall).

A Perspective component cannot hold another Perspective component inside a custom element's slot: the module has no
container component (T1 found the same limit for `automation-input-modal`). The cases that no property can carry:

| Component or slot | Why | Treatment |
|---|---|---|
| `modal-window` `content` slot | Arbitrary content; needs a container | Wrap `title`, labels and the four events; `content` is a text property. The command dialogue stays the Confirm row |
| `toggletip` `content`, `command-menu` toggle slots, `system-menu` `battery-status`, `navigation-menu` `logo`, `top-bar` `app-icon` and `command-button` | Free content or an element of its own | Text or allow-listed icon; `battery-status` and `logo` omitted and recorded as not carried |
| `breadcrumb` and `top-bar` item `icon` | A template function, not data | Omitted; items carry `label` and `href` |
| `user-menu` `password` and `username` | A password in a property tree and a client attribute | Never wired. The component shows only the signed in form and the Sign in button; the credentials page is the gateway's (section 3) |
| `top-bar` `breadcrumbItems` | Drawn only while `settings` is true (source line 118) | See section 5 |
| Leaf children (`alert-menu-item`, `tree-navigation-item` and the others) | Meaningful only inside a parent | Wrapped as leaf components on the component test page; the frame builds them through the parent's `items` |

## 3. The Mapping

Events are carried as component events (GF-37) named `on...`, which the existing table `ALERT_EVENTS` maps from the DOM
name; each event's script is configured in the view as a component event action, as the page buttons do today.

| Current part | New component | Events carried and the script they call |
|---|---|---|
| Top bar (menu button, app name, page name, brilliance, user, apps) | `top-bar` | `menu-button-clicked` (opens the `nav` dock: `system.perspective.openDock('nav')` or `toggleDock`; ASM variant writes `navPanel` first); `dimming-button-clicked` opens the brilliance popup; `user-button-clicked` opens the user popup; `apps-button-clicked` opens the support list (ASM) |
| Alert message, ACK of the top alarm | none (see section 5, question 3) | `cadre.hmi.ack_top` (W6) stays for a retained strip |
| Bell and count | `alert-button` inside `top-bar` | `click-alert` opens the alert menu popup; `click-silence` has no Cadre silence function, so it is not shown (`showSilenceButton` false) until the owner asks. `nAlerts`, `alertType`, `blinking` are bound to `custom.alarm.count`, the priority from `custom.alarm.highest`, `unacked > 0` |
| Alert menu | `alert-menu` with `alert-menu-item` rows | `ack-click` calls `cadre.hmi.ack` (W8) after Confirm; `ack-all-visible-click` calls the Ack all Confirm (W9); `go-to-alert-list-click` navigates to `/alerts`. Rows from `cadre.hmi.alarm_list`. Under the module rendering this replaces `alert_menu_module` for the new frame; the stock table stays for `--render stock` |
| Alerts page | unchanged | `Framework/AlertsPage` stays; `alert-menu` is the menu only |
| Navigation menu (flat) | `navigation-menu` with `navigation-item` | `click` navigates through `system.perspective.navigate(path)` then `closeDock('nav')`; selected = `page.props.path`. Footer items in the `footer` slot |
| Navigation tree and node badges (ASM) | `tree-navigation` with `tree-navigation-group` and `-item`, `alerts` per row | `click` runs the row's route (`cadre.hmi.nav_tree` already returns node, route, counts, depth); `alerts` is `{critical, high, medium, low, diagnostic}` from `node_counts`; the ASM support state keeps its list in a second `navigation-menu` |
| Breadcrumb | `breadcrumb` (or `top-bar` settings mode) | `breadcrumb-click` navigates to the item's route (`cadre.hmi.crumbs` or `frame_crumbs`); node badges cannot be drawn (section 5) |
| Crumb popup (ASM) | `context-menu-input` | `item-click` navigates and closes; Show and Areas become `columnGroups` or two groups |
| Page header pivots (ASM) | `pivot-item-group` with `pivot-item` | `change` writes `contentNode` and navigates to `/node/alarms` or `/node/trend` |
| Page header tabs, previous and next (ASM) | `tab-row` | `tab-selected` navigates to the tab's route; previous and next stay Cadre buttons |
| Brilliance menu | `brilliance-menu` | `palette-changed` calls `cadre.hmi.set_palette(session, key)`, mapping the component's palette names to day, dusk, night, bright from the measured enumeration (`ObcPalette`). `brightness-changed` has no Cadre counterpart and is hidden (`showLinkBrightness` false) |
| User menu, sign in and out | `user-menu`, `user-button` | `sign-in-click` calls `system.perspective.login()`; `sign-out-click` calls `system.perspective.logout()`. `type` signed in or out from `session.props.auth.authenticated`; `userLabel` from `session.props.auth.user.userName`; `userInitials` computed in the binding. No credential property is bound |
| Clock | `clock` in the `top-bar` slot | none. `date` bound to `now(1000)` as ISO text; `timeZoneOffsetHours` from the project's clock label (UTC is 0) |
| Alarm banner (ASM) | none | Stays `ASM/AlarmBanner`; `notification-message-item` could draw a row, but the rows carry priority icons, node and state words OpenBridge's item does not (section 5) |
| Command controls | `command-menu`, `modal-window`, `app-button` | Press raises the existing Confirm row (`custom.pending`); Confirm writes through the existing path with the `Administrator` check. `command-menu` `change` (in command or not) only asks; it writes nothing itself |
| Search (ASM) | `app-menu` (its `search` event) or kept | `search` writes `searchQuery`; results stay `ASM/SearchResults` |
| Notifications | `notification-button`, `notification-badge-button`, `notification-menu-item`, `-message-item`, `-floating-item` | Wrapped; no Cadre frame part uses them. `obc-click` and `item-click` carry no write |
| Tooltip, toggletip, system menu | `tooltip`, `toggletip`, `system-menu` | Wrapped; no Cadre part uses them. `system-menu` carries 16 events that write nothing (Wi-Fi, audio, battery are not process state) |

Parts with no OpenBridge counterpart stay: the faceplate dock and popups, the alerts page, the alarm banner, the page
canvas and toolbar, and the node alarm and trend pages.

## 4. The Build Plan

### 4.1 The frame option

Name: `--frame ob` (value `"ob"`, added to `navigation.FRAMES`; `openbridge` and `asm` unchanged).

1. **`tools/hmi/obframe.py`** (new): the views `Framework/OB/Head` (one top dock holding the `top-bar` module component,
   by the GF-90 rule), `Framework/OB/NavDock`, `Framework/OB/AlertMenu`, `Framework/OB/Brilliance`, `Framework/OB/UserMenu`,
   `shared_docks`, `page_config`, `session_custom`, `views()`. Each view is one module component plus bindings.
2. **`tools/hmi/parent.py`**: one loop line beside `navigation.views()` adds `obframe.views()`; `session_defaults` gains
   the keys the views read. The existing `--name` option remains. A second parent is not needed: `cadre_hmi_base_asm` was a
   parent built beside the deployed one (COB-157) so that ASM children could be tried without touching the first; the
   views of all frames sit in one parent. Build `--name cadre_hmi_base_ob` only to try the new views beside `cadre_hmi_base`.
3. **`tools/hmi/screen.py`**: `build_child` accepts `frame="ob"`, writes `obframe.page_config` and the session data of
   `obframe.session_custom`, and `--frame` takes the third choice. The module rendering is required: a stock build with
   `--frame ob` stops with an error (as `MODULE_ONLY`).
4. **`tools/hmi/framework.py`**: no change to `top_bar`; helper functions (`_open_menu`, `CAN_CFG`, `_can`) imported, not copied.
5. **`tools/hmi/navigation_scripts.py`**: no new function where `nav_tree`, `crumbs`, `alarm_list`, `node_counts` serve;
   at most one pure function that shapes rows into the components' item lists (`ob_items`), appended to the library source.
6. **`module/`**: the 33 wraps (section 4.2), the `items` mechanism, and `module/components.json` rows.
7. **Wiki**: a new subsection of wiki 04 section 8's pattern; not part of this survey.

### 4.2 Batches

Rates come from `REPORT-T1.md` section 3: 21,000 to 51,000 tokens per element, 44,000 with the recipe; a batch of a
new mechanism cost 169,000 for the mechanism and one element. The frame components carry events and child lists, so the
estimate uses 35,000 to 60,000 per element and the first-of-kind mechanism once.

| Batch | Components | Contents | Estimate (tokens) |
|---|---|---|---|
| F1 | `tooltip`, `toggletip`, `clock`, `user-button`, `app-button`, `notification-button`, `notification-badge-button` | The `items` mechanism and the text and icon slot properties (icon allow list from `dist/icons`); seven leaves with `click`, `obc-click`, `primary-action` events | 420,000 |
| F2 | `alert-button-item`, `alert-button`, `alert-menu-item`, `alert-menu` | Child item lists; events `click-alert`, `click-silence`, `ack-click`, `ack-all-visible-click`, `go-to-alert-list-click`; `alertType` and priority enumerations | 260,000 |
| F3 | `navigation-item`, `navigation-item-group`, `navigation-menu`, `tree-navigation-item`, `tree-navigation-group`, `tree-navigation`, `breadcrumb` | Nested item lists of two depths; `alerts` object; `treeBranches` left to the container | 370,000 |
| F4 | `brilliance-menu`, `user-menu`, `system-menu`, `app-menu`, `command-menu`, `top-bar` | Composite `top-bar` (alert button and clock inside); 16 `system-menu` events, display only; credential properties excluded by `exclude` | 400,000 |
| F5 | `tab-item`, `tab-row`, `pivot-item`, `pivot-item-group`, `modal-window`, `context-menu-input`, `notification-menu-item`, `notification-message-item`, `notification-floating-item` | Native array attributes; text slots; selection events | 340,000 |
| F6 | The frame option | Section 4.1 items 1 to 5, unit tests (each view against the registry, the docks, the option) | 450,000 |
| F7 | Gates and glass | Section 4.3 | 300,000 |
| F8 | Gateway run, diagnosis | Build, install, G8, G10, G11 on a sample, the fixes the first run finds (T1 spent about 0.4 million on gate waits and diagnosis) | 350,000 |
| | Main session orchestration | Builds, joint tests, records | 400,000 |
| | **Total** | | **about 3.3 million** (range 2.7 to 4.5 million) |

Batches F1 to F5 run one after another in the same twelve files (recipe section 1 item 3); the orchestrator builds the
bundle once per batch. F6 starts only after F2 to F4, as it uses their components.

### 4.3 Gates

G0 to G7 run offline inside `screen.py`: G1 reads the schemas of the new module components, which `module/components.json`
and the generated `*.props.json` feed (`gates.g1_registry`); G7 commands must see each command control's path in a `case`
over `custom.can` (the Confirm row stays, so the existing rule holds). No gate is weakened.

On a sample built with `--frame ob --render module`:

1. **G8** (`capture.py`): renders; new baselines for the new frame, accepted by the owner.
2. **G10 variants** (`functional.py`): F16 needs the top bar ACK replaced, where the strip is dropped, by the alert menu
   check "ACK visible and each row's ACK absent or disabled" (nobody signed in); F21 needs `open_alarm_menu`,
   `popup_open`, `dock_open` and the dock's menu button and close button located on the new components; F17 and F18 are
   unchanged once `sign_in` reaches the user menu. F20 (toolbar) is page content and unchanged.
3. **Glass helpers** (`glass.py`): `BELL` becomes a locator on the module `top-bar` host
   (`[data-component="cadre.ob.topbar"]`) and a pierce into its shadow root for the bell (`obc-alert-button`), by
   a variant `BELL_OB`; `_open_user_menu` gains a third strategy beside `by_container` and `by_icon`: the host's
   `user-button` inside `obc-top-bar`, then the popup's `obc-user-menu` Sign in or Sign out buttons (Playwright locators
   pierce open shadow roots). `sign_in` otherwise unchanged. `TOP_ICONS` counts SVGs by y position and works through
   shadow DOM only if the query descends into shadow roots; the variant should use the host's parts instead.
4. **Selected by frame**: the helpers read `session.custom.frame` (`ob`) through a function `frame_variant(page)`, so that
   `openbridge` and `asm` runs keep their selectors.
5. **G11** (faceplates) is independent of the frame and runs unchanged on the sample.
6. **`glass_gates`**: `gate_menus`, `gate_alarm`, `gate_ack` and `gate_banner` have an `ob` branch; `gate_search`, `gate_zoom`
   and the pivot checks are ASM-only and run only if the ob frame carries the ASM variant (section 5, question 1).
7. **Tests**: the new views are held to the generator by the pattern of `TopBarPathTests`, so a moved selector fails a unit test.

## 5. Risks and Questions for the Owner

### 5.1 Risks

1. **`top-bar` draws its own breadcrumb only in `settings` mode**, and its items carry no counts. The ASM rule of wiki 04
   section 7 item 4 (each crumb with its badges) cannot be drawn by `breadcrumb` or `top-bar`. Options: keep the Cadre
   `Framework/Crumb` row in the `ob` frame (a second view beside the bar, which GF-90 forbids as a second top dock unless
   the Head view holds both); or accept crumbs without badges, which loses F046; or show node alarms only through
   `tree-navigation`, whose `alerts` object does draw badges by severity.
2. **Alarm message and its ACK.** `top-bar` has no slot for the most severe alarm text, and the F16 top bar ACK check
   (W6) has no counterpart. The `alert-menu` carries Ack all visible (W9) and each row's ACK.
3. **Priority colours.** `alert-button` and `tree-navigation-item` colour by OpenBridge's `AlertType` and severity names
   (critical, high, medium, low, diagnostic); `framework.PRIORITY_VAR` and wiki 13 section 11.1 state colour by rank. The
   mapping of the five Cadre priorities to the five severities is a decision with a consequence for the ASM rule; it must be
   a table in the wrapper, not in OpenBridge's code (rule 7).
4. **Composition is shadow DOM.** Playwright reaches it, but G10's `data-component-path` selectors do not exist inside a
   single component; the stable hooks are the host's `data-component` and the elements' tags.
5. **Event payload names.** `eventName` of `system-menu` is a literal event name in the manifest, probably a defect of the
   pinned release; it is wrapped as it is, and recorded.
6. **No password path.** `user-menu` offers username and password fields that suit a built-in login, not the gateway's
   identity provider. The wrapper excludes them; the Sign in button calls `system.perspective.login()` (GF-44).
7. **Icons.** Slots take `obi-` icon elements the bundle must import; each icon added grows the bundle. The allow list is
   read from `dist/icons` and bounded to those the frame uses (menu, user, dimming, apps, alert, chevron) plus those
   the owner names.
8. **Walk row A-02** (REPORT-T1 section 5.2 item 1) depends on run order and may recur on the first runs of F8.
9. **Cost and mergeability.** Twelve files change in each batch (recipe section 5.4); the frame option adds one new
   file and about three lines to each of `parent.py`, `navigation.py` and `screen.py`, small for the diff back to the source.

### 5.2 Questions

1. **Is the new frame an OpenBridge only frame, or does it also carry the ASM variant?** Recommendation: OpenBridge only
   first (`ob`), keeping flat navigation, brilliance, user, alert menu and bell, with the tree and breadcrumb of the hierarchy
   as a second step (`ob` with a descriptor that names nodes uses `tree-navigation`). The ASM banner, pivots, search
   and floating faceplates are not part of the first step. The ASM rules of wiki 04 sections 7 to 9 that matter most
   (hierarchy, counts, ownership, the pin, the Confirm row) are in the data and scripts, so they hold in either case.
2. **Crumbs with badges:** accept the loss in the `ob` frame, or keep `Framework/Crumb` in the Head view?
3. **The alert message and its top bar ACK (F16):** drop it from the `ob` frame and move the check to the alert menu, or
   keep a small Cadre strip beside the bar?
4. **Silence:** does the project want `click-silence` (no Cadre function exists), or is the button hidden?
5. **Priority to severity mapping** for the five Cadre priorities.
6. **Baselines:** may G8 baselines for the new frame be accepted on first sight, as for the module frame?
7. **Two parents:** is trying the frame beside the deployed parent (`--name cadre_hmi_base_ob`) wanted, or only in the
   deployed parent (the views are inert until a child asks for `--frame ob`)?

## Owner's Answers (2026-11-03)

1. **Variants.** The new frame is built in both variants now: an OpenBridge variant and an ASM variant (the ASM frame's
   navigation dock, crumb popups, page header and the rules of `wiki/04` sections 7 to 9), each on the OpenBridge frame
   components. `--frame openbridge` and `--frame asm` stay unchanged.
2. **Breadcrumb.** The new frame keeps the Cadre `Framework/Crumb` view with its node badges; `obc-breadcrumb` is
   wrapped and available but not used by the frame.
3. **Alert strip.** The new frame keeps a Cadre alert message strip (the latest alarm and its ACK) beside the
   OpenBridge top bar; G10 F16 keeps its check.
4. **Silence.** The alert button's silence control is hidden until a silence function exists.
5. Settled by the existing rules, not asked: the five Cadre priorities map onto OpenBridge's levels as `wiki/13`
   section 11.1 says; G8 on the new frame is judged by its own rules and its pictures are sent to the owner; the frame
   is built into the existing parent, which already carries every frame's views, with a sample child on each new
   variant.

## Departures from the Design in Batch F6a (2026-11-03)

The OpenBridge variant (`--frame ob`, wiki 04 section 10) departed from sections 3 and 4.1 in these respects.

1. **Views and scripts.** The five views are `Framework/OB/Head`, `NavDock`, `AlertMenu`, `UserMenu` and `Brilliance`; `Head` holds
   the strip (crumb and alert message) beneath the bar, not beside it, so the dock is 84 px, as the ASM frame's. The design's
   `session_defaults` change is not made: the session keys the views read already exist, and a change would alter the older
   frames' children. `session_custom` is `{"frame": "ob"}`. One script function is added, `cadre.hmi.ob_items`, which shapes
   the alarm list and the navigation items into the components' item lists; `nav_tree` is not used (the ASM variant's source).
2. **Alert menu.** The design (section 3) wired `ack-click` to W8 "after Confirm". The default frame's module panel acknowledges
   a row and ACK visible at once, with the Confirm row on its own Ack all bar, and the frame follows that exactly: W8 and W9 as
   the panel, the bar and its Confirm row under the menu. A row is disabled, not hidden, without the permission.
3. **Clock.** The design bound `date` to ISO text with `timeZoneOffsetHours` from the clock label. The default bar's clock shows the
   gateway's wall time with a label, so `date` is the wall time written as an instant and the offset is 0 (the label "UTC" is dropped).
4. **Command text.** `commandButtonText` is left empty (the F4 run-on "Engine roomCommand" is avoided, not fixed in the wrapper).
5. **Brilliance.** The brightness section is hidden (`showBrightness` false), as the design said; the popup is 320 by 280, to be
   measured at the gateway step.
6. **Icons.** A navigation item draws an icon only where its Cadre icon name is also a bundled OpenBridge icon (`dashboard`,
   `alert-list`); the others draw none. No icon was added to the bundle in this batch.
7. **Parent.** The parent now holds views with module components (the five above), which it did not before; they are inert until a child
   names them, and G1 of the parent reads the module's schemas.

## Departures from the Design in Batch F6b (2026-11-03)

The ASM variant (`--frame obasm`, wiki 04 section 11) departed from sections 1.2, 3 and 4.1 in these respects.

1. **Name and views.** The option is `obasm`. Three views are new (`Framework/OBASM/Head`, `NavDock`, `Crumb`); the bell, user and
   brilliance popups are F6a's, and the banner, floating faceplate, search results and pivot pages are the ASM frame's. The module
   code is in `tools/hmi/obasm.py`, a sibling of `obframe.py`, which gains `bar_node` (the F6a bar, unchanged without arguments).
   `navigation.FRAMES` gains `obasm`, and `ASM_FRAMES` and `MODULE_FRAMES` name the frames that carry the ASM rules and the frames
   drawn with the module's components.
2. **Scripts.** One function is added, `cadre.hmi.obasm_items` (pivot, tabs, tree and support items). `cadre.hmi.asm_frame` answers true
   for `obasm` as well, so the floating faceplate per device holds; it is the only existing function changed, and it answers as before
   for the other frames. `navigation.crumb` takes the popup's top row (default 48, unchanged).
3. **Head.** The head is 132 px in three rows (bar 48, strip 36, header 48), not 84. The module top bar cannot hold the crumb, the search
   field or the alert message, so they stand in the strip; the header is 48 px because the module's pivot group and tab row are
   48 px high (the ASM header is 36). The bar's page name is empty while the page names a node.
4. **Tree.** A tree group fires only `expand-toggle`, so a node that holds pages is no longer a button that opens its first page (section
   8.3 item 1): the page is one press further. A node with no page of its own gets an Alarms leaf. A group draws its counts only while
   closed (the element's rule), so an open node shows its children's. Rows draw no icon.
5. **Crumb popup.** The popup stays the ASM view (Show and Areas), because `obc-context-menu-input` carries no priority badge on an
   option. The design (section 3) named the context menu; owner's answer 2 holds for the crumb, and the same reasoning holds for its popup.
6. **Search.** The module has no search field (`app-menu` has a `search` event but is a menu of apps), so the ASM text field stays, in the
   strip.
7. **Not carried by a component, kept as ASM views:** the alert message (answer 3), the alarm banner and the floating faceplate (design
   section 3), the title, level and the two step buttons of the header.

