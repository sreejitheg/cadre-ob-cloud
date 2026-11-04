# Catalogue: App

Interface facts for the 12 components of the reference family `App`, parsed from the reference documentation. Defaults and enumerations are parsed from prose by heuristic and are marked so; an empty cell means the page states none. Back to [05 Component Catalogue](../05-component-catalogue.md).

## 1. App Bar

<a id="app-bar"></a>

Disposition: `gap`. Cadre equivalent: None.

Multi-application integration chrome; no requirement in process automation screens so far.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Items | `label` | value |  |  |
| Items | `path` | value |  |  |
| Items | `icon` | object |  |  |
| Items | `tooltip` | object |  |  |
| Items / Properties | `items` | array |  |  |
| Labels / Properties | `showLabel` | value | true |  |
| Tooltip | `enabled` | value | false |  |
| Tooltip | `text` | value |  |  |
| Tooltip | `delay` | value | 0 |  |
| Tooltip | `sustain` | value | 4000 |  |
| Tooltip | `location` | value | bottom |  |
| Tooltip | `tail` | value | true |  |
| Tooltip | `style` | object |  |  |
| Tooltip | `type` | value | label | label, icon |
| Tooltip | `variant` | value | normal |  |
| Tooltip | `label` | value |  |  |
| Tooltip | `showIcon` | value | false |  |
| Tooltip | `icon` | object |  |  |
| Tooltip | `style` | object |  |  |
| Properties | `style` | object |  |  |

## 2. Badge

<a id="badge"></a>

Disposition: `partial`. Cadre equivalent: Corner badges of the automation symbols.

A free-standing badge view is not implemented.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Type / Properties | `type` | value |  |  |
| Type / Properties | `variant` | value | default | default, flat |
| Size / Properties | `size` | value |  | regular, large |
| Number / Properties | `showNumber` | value | true |  |
| Number / Properties | `number` | value | 0 |  |
| Icon / Properties | `showIcon` | value | false |  |
| Icon / Properties | `hasBadgeIcon` | value | false |  |
| Icon / Properties | `badgeIcon` | object |  |  |
| Properties | `style` | object |  |  |

## 3. Card

<a id="card"></a>

Disposition: `generator`. Cadre equivalent: Card pattern of the cards layout (`cadre/surface/card` plus a title).

The dialog option is not implemented.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Title / Properties | `hasTitle` | value | false |  |
| Title / Properties | `title` | value |  |  |
| Title / Properties | `hasIcon` | value | false |  |
| Title / Properties | `icon` | object |  |  |
| Dialog / Properties | `hasDialog` | value | false |  |
| Dialog / Properties | `dialog` | object |  |  |
| Dialog / Properties | `hasTitle` | value | false |  |
| Dialog / Properties | `title` | value |  |  |
| Dialog / Properties | `hasIcon` | value | false |  |
| Dialog / Properties | `icon` | object |  |  |
| Dialog / Properties | `viewPath` | value |  |  |
| Dialog / Properties | `viewParams` | object |  |  |
| Dialog / Properties | `autoClose` | value | false |  |
| Dialog / Properties | `timeOutSeconds` | value | 60 |  |
| Dialog / Properties | `visibleTimerSeconds` | value | 20 |  |
| Properties | `style` | object |  |  |

Events: `onDialogOpened`, `onDialogClosed`.

## 4. Fleet Button

<a id="fleet-button"></a>

Disposition: `gap`. Cadre equivalent: None.

Multi-application integration chrome; no requirement in process automation screens so far.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Name and Status / Properties | `fleetName` | value |  |  |
| Name and Status / Properties | `status` | value |  |  |
| Readouts | `label` | value |  |  |
| Readouts | `value` | value |  |  |
| Readouts | `unit` | value |  |  |
| Readouts / Properties | `readouts` | array |  |  |
| Alerts / Properties | `showAlerts` | value | true |  |
| Alerts / Properties | `alertTopic` | value |  |  |
| Alerts / Properties | `alertTopicIcon` | object |  |  |
| Alerts / Properties | `alerts` | object |  |  |
| Alerts / Properties | `alarm` | value | 0 |  |
| Alerts / Properties | `warning` | value | 0 |  |
| Alerts / Properties | `caution` | value | 0 |  |
| Selected / Properties | `selected` | value | false |  |
| Properties | `style` | object |  |  |

Events: `onActionPerformed`.

## 5. Integration Bar

<a id="integration-bar"></a>

Disposition: `gap`. Cadre equivalent: None.

Multi-application integration chrome; no requirement in process automation screens so far.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Vessel Selector / Fleet | `name` | value |  |  |
| Vessel Selector / Fleet | `label` | value |  |  |
| Vessel Selector / Fleet | `status` | value |  |  |
| Vessel Selector / Fleet | `icon` | object |  |  |
| Vessel Selector / Fleet | `statuses` | array |  |  |
| Vessel Selector / Vessels | `value` | value |  |  |
| Vessel Selector / Vessels | `label` | value |  |  |
| Vessel Selector / Vessels | `status` | value |  |  |
| Vessel Selector / Vessels | `icon` | object |  |  |
| Vessel Selector / Vessels | `disabled` | value | false |  |
| Vessel Selector / Vessels | `statuses` | array |  |  |
| Vessel Selector / Properties | `selectedVessel` | value |  |  |
| Vessel Selector / Properties | `showFleet` | value | true |  |
| Vessel Selector / Properties | `fleet` | object |  |  |
| Vessel Selector / Properties | `vessels` | array |  |  |
| Status Fields | `label` | value |  |  |
| Status Fields | `icon` | object |  |  |
| Command Indicator / Properties | `showInCommand` | value | false |  |
| Command Indicator / Properties | `inCommand` | value | false |  |
| Command Indicator / Properties | `inCommandText` | value | In Command |  |
| Command Indicator / Properties | `noCommandText` | value | No Command |  |
| Buttons / Properties | `showHomeButton` | value | true |  |
| Buttons / Properties | `showLinkButton` | value | false |  |
| Buttons / Properties | `linkButtonActivated` | value | false |  |
| Buttons / Properties | `showAlertButton` | value | false |  |
| Buttons / Properties | `alertButtonActivated` | value | false |  |
| Buttons / Properties | `showNotificationButton` | value | false |  |
| Buttons / Properties | `notificationButtonActivated` | value | false |  |
| Buttons / Properties | `showNotificationCount` | value | false |  |
| Buttons / Properties | `notificationCount` | value | 0 |  |
| Buttons / Properties | `showScreenButton` | value | false |  |
| Buttons / Properties | `screenButtonActivated` | value | false |  |
| Buttons / Properties | `showSystemButton` | value | false |  |
| Buttons / Properties | `systemButtonActivated` | value | false |  |
| Brilliance Menu / Properties | `showBrillianceMenu` | value | true |  |
| Brilliance Menu / Properties | `palette` | value | day | bright, day, dusk, night |
| User Menu | `id` | value |  |  |
| User Menu | `label` | value |  |  |
| User Menu | `hasIcon` | value | false |  |
| User Menu | `icon` | object |  |  |
| User Menu / Properties | `showUserButton` | value | false |  |
| User Menu / Properties | `userMenu` | object |  |  |
| User Menu / Properties | `userInitials` | value |  |  |
| User Menu / Properties | `userLabel` | value |  |  |
| User Menu / Properties | `signedInActions` | array |  |  |
| Clock / Properties | `showClock` | value | false |  |
| Clock / Properties | `clock` | object |  |  |
| Clock / Properties | `showTimezone` | value | true |  |
| Clock / Properties | `showSeconds` | value | true |  |
| Clock / Properties | `utcHourOffset` | value | 0 |  |
| Clock / Properties | `time` | value |  |  |
| Properties | `style` | object |  |  |

Events: `homeButtonClick`, `linkButtonClick`, `onFleetButtonClick`, `onCommandClick`, `alertButtonClick`, `notificationButtonClick`, `screenButtonClick`, `systemButtonClick`, `brillianceButtonClick`, `userButtonClick`, `onSignedInActionClick`, `onSignOutClick`.

## 6. Integration Button

<a id="integration-button"></a>

Disposition: `gap`. Cadre equivalent: None.

Multi-application integration chrome; no requirement in process automation screens so far.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Type / Properties | `type` | value | rich | rich, regular, hug |
| Label and Status / Properties | `label` | value | Label |  |
| Label and Status / Properties | `hasStatus` | value | true |  |
| Label and Status / Properties | `status` | value | Status |  |
| Icons / Properties | `hasLeadingIcon` | value | false |  |
| Icons / Properties | `leadingIcon` | object |  |  |
| Icons / Properties | `hasTrailingIcon` | value | false |  |
| Icons / Properties | `trailingIcon` | object |  |  |
| Icons / Properties | `hasTrailingIcon2` | value | false |  |
| Icons / Properties | `trailingIcon2` | object |  |  |
| Info Field and Readouts | `label` | value |  |  |
| Info Field and Readouts | `value` | value |  |  |
| Info Field and Readouts | `unit` | value |  |  |
| Info Field and Readouts / Properties | `infoLabel` | value | Info Label |  |
| Info Field and Readouts / Properties | `infoStatus` | value | Info Status |  |
| Info Field and Readouts / Properties | `readouts` | array |  |  |
| Selected / Properties | `selected` | value | false |  |
| Disabled / Properties | `disabled` | value | false |  |
| Properties | `dividerBottom` | value | false |  |

Events: `onActionPerformed`.

## 7. Modal

<a id="modal"></a>

Disposition: `stock`. Cadre equivalent: `system.perspective.openPopup` with a `cadre/surface/card` root.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Size / Properties | `size` | value | large | small, medium, large |
| Header / Properties | `title` | value | Title |  |
| Header / Properties | `hasLeadingIcon` | value | false |  |
| Header / Properties | `icon` | object |  |  |
| Header / Properties | `hasCloseAction` | value | true |  |
| Actions / Properties | `doneLabel` | value | Done |  |
| Actions / Properties | `hasCancelAction` | value | true |  |
| Actions / Properties | `cancelLabel` | value | Cancel |  |
| Actions / Properties | `hasOptionalAction` | value | false |  |
| Actions / Properties | `optionLabel` | value | Option |  |
| Properties | `style` | object |  |  |

Events: `onCloseClick`, `onCancelClick`, `onDoneClick`, `onOptionClick`.

## 8. Navigation Bar

<a id="navbar"></a>

Disposition: `framework`. Cadre equivalent: `Framework/NavMenu` and `Framework/NavItem` in the shared left dock.

Items and footer from `session.custom.nav`; the selected item from `page.props.path`; groups, flyouts and alert badges are not implemented (register COB-021).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Items | `label` | value |  |  |
| Items | `path` | value |  |  |
| Items | `icon` | object |  |  |
| Items | `children` | array |  |  |
| Items | `alerts` | object |  |  |
| Footer / Properties | `footerItems` | array |  |  |
| Footer / Properties | `showAlertList` | value | false |  |
| Footer / Properties | `alertListPath` | value | /alarms |  |
| Variant / Properties | `variant` | value | full | full, icon-only, icon-only-large, compact, tree |
| Variant / Properties | `flyoutVariant` | value | full | full, compact |
| Alert Badges | `countLevelCritical` | value |  |  |
| Alert Badges | `countLevelHigh` | value |  |  |
| Alert Badges | `countLevelMedium` | value |  |  |
| Alert Badges | `countLevelLow` | value |  |  |
| Alert Badges | `countLevelDiagnostic` | value |  |  |
| Alert Badges | `countAlarm` | value |  |  |
| Alert Badges | `countWarning` | value |  |  |
| Alert Badges | `countCaution` | value |  |  |
| Logo / Properties | `companyImageUrl` | value |  |  |
| Logo / Properties | `companyImageAlt` | value | Company Logo |  |
| Properties | `items` | array |  |  |
| Properties | `style` | object |  |  |

## 9. Overview

<a id="app"></a>

Disposition: `framework`. Cadre equivalent: `Framework/*` views and the shared docks (wiki page 04).

Overview page of the application frame.

No property table on the page.

## 10. Pagination

<a id="pagination"></a>

Disposition: `stock`. Cadre equivalent: Table pager of `ia.display.table` and the alarm tables.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Pages / Properties | `pages` | value | 3 |  |
| Pages / Properties | `currentPage` | value | 1 |  |
| Variant / Properties | `variant` | value | regular | regular, flat, condensed |
| Width / Properties | `fullWidth` | value | false |  |
| Disabled / Properties | `disabled` | value | false |  |
| Properties | `style` | object |  |  |

Events: `onActionPerformed`.

## 11. Tabbed Card

<a id="tabbed-card"></a>

Disposition: `stock`. Cadre equivalent: `ia.container.tab` with `cadre/surface/card`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Tabs | `title` | value |  |  |
| Tabs | `icon` | object |  |  |
| Tabs | `viewPath` | value |  |  |
| Tabs | `viewParams` | object |  |  |
| Tabs / Properties | `tabs` | array |  |  |
| Tabs / Properties | `selectedTab` | value | 0 |  |
| Content / Components in the Card | `tabIndex` | value | 0 |  |
| Content / Components in the Card | `useDefaultSlot` | value | false |  |
| Content / Properties | `hasDefaultSlotOnly` | value | false |  |
| Properties | `hasTabIcons` | value | false |  |
| Properties | `style` | object |  |  |

Events: `onActionPerformed`.

## 12. Top Bar

<a id="topbar"></a>

Disposition: `framework`. Cadre equivalent: `Framework/TopBar` in the shared top dock.

Menu button, app and page name, most severe alarm with ACK, alarm count, brilliance menu, user menu and clock are implemented; the command button, the apps button and the narrow-screen breakpoints are not (register COB-020).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Navigation Menu / Properties | `navMenuButtonPressed` | value |  |  |
| Navigation Menu / Properties | `bindNavMenuToDock` | value |  |  |
| Navigation Menu / Properties | `navDock` | value |  |  |
| Navigation Menu / Properties | `autocloseNavMenu` | value | true |  |
| Alert Menu / Properties | `showAlerts` | value | true |  |
| Alert Menu / Properties | `showAlertsButton` | value | true |  |
| Alert Menu / Properties | `showAlertListButton` | value | true |  |
| Alert Menu / Properties | `showAlertSilenceButton` | value | true |  |
| Alert Menu / Properties | `allowAlertAcknowledge` | value | true |  |
| Alert Menu / Properties | `canAcknowledge` | value | true |  |
| Alert Menu / Properties | `alertConvention` | value | levels | levels, bam |
| Alert Menu / Properties | `alertPath` | value | /alarms |  |
| Alert Menu / Properties | `titleSource` | value | label | label, name, notes, displayPath |
| Alert Menu / Properties | `descriptionSource` | value | notes |  |
| Alert Menu / Properties | `dateFormat` | value |  |  |
| Alert Menu / Properties | `showTimeInUtc` | value | false |  |
| Alert Menu / Properties | `maxAlerts` | value | 50 |  |
| Alert Menu / Properties | `filter` | object |  |  |
| Alert Menu / Properties | `states.activeUnacked` | value | true |  |
| Alert Menu / Properties | `states.activeAcked` | value | true |  |
| Alert Menu / Properties | `states.clearUnacked` | value | true |  |
| Alert Menu / Properties | `states.clearAcked` | value | false |  |
| Alert Menu / Properties | `priorities.diagnostic` | value | false |  |
| Alert Menu / Properties | `priorities.low` | value | true |  |
| Alert Menu / Properties | `priorities.medium` | value | true |  |
| Alert Menu / Properties | `priorities.high` | value | true |  |
| Alert Menu / Properties | `priorities.critical` | value | true |  |
| Alert Menu / Properties | `conditions.source` | value | * |  |
| Alert Menu / Properties | `conditions.displayPath` | value | * |  |
| Alert Menu / Properties | `conditions.provider` | value |  |  |
| Brilliance Menu / Properties | `showBrillianceMenu` | value | true |  |
| Brilliance Menu / Properties | `palette` | value | day | bright, day, dusk, night |
| Brilliance Menu / Properties | `showBrightness` | value | false |  |
| Brilliance Menu / Properties | `brightness` | value | 100 |  |
| Brilliance Menu / Properties | `useIgnitionTheme` | value | false |  |
| Brilliance Menu / Properties | `theme` | value |  |  |
| Brilliance Menu / Properties | `palletteToTheme` | object | bright/day  to  light, dusk/night  to  dark |  |
| User Menu / Properties | `showUserButton` | value | false |  |
| User Menu / Properties | `bindUserButtonToAuth` | value | false |  |
| User Menu / Properties | `isLoggedIn` | value | false |  |
| User Menu / Properties | `userFullName` | value |  |  |
| Apps Button / Properties | `showAppsButton` | value | false |  |
| Apps Button / Properties | `appsButtonPressed` | value |  |  |
| Command Button | `showInCommand` | value | false |  |
| Command Button | `inCommand` | value |  |  |
| Clock | `showClock` | value | true |  |
| Clock | `showTimezone` | value | true |  |
| Clock | `utcHourOffset` | value | 0 |  |
| Narrow Screens | `appIconBreakpointPx` | value | 500 |  |
| Narrow Screens | `appTitleBreakpointPx` | value | 500 |  |
| Narrow Screens | `dimmingButtonBreakpointPx` | value | 500 |  |
| Narrow Screens | `userButtonBreakpointPx` | value | 500 |  |
| Narrow Screens | `appsButtonBreakpointPx` | value | 500 |  |
| Properties | `appName` | value | App |  |
| Properties | `pageName` | value | Page |  |
| Properties | `hasAppIcon` | value | false |  |
| Properties | `appIcon` | value |  |  |
| Properties | `style` | object |  |  |

Events: `onSignInClick`, `onSignOutClick`, `onAlertSilenceClick`.
