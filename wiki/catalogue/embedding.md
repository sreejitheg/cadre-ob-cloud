# Catalogue: Embedding

Interface facts for the 6 components of the reference family `Embedding`, parsed from the reference documentation. Defaults and enumerations are parsed from prose by heuristic and are marked so; an empty cell means the page states none. Back to [05 Component Catalogue](../05-component-catalogue.md).

## 1. Accordion Card

<a id="accordion-card"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.accordion`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Embedded View / Properties | `viewPath` | value | empty |  |
| Embedded View / Properties | `viewParams` | object | {} |  |
| Expanding and Collapsing / Properties | `expanded` | value | false |  |
| Expanding and Collapsing / Properties | `disabled` | value | false |  |
| Header / Properties | `cardTitle` | value | Accordion Card |  |
| Header / Properties | `size` | value | single-line | single-line, large |
| Header / Properties | `hasDescription` | value | false |  |
| Header / Properties | `description` | value |  |  |
| Header / Properties | `hasStatusLabel` | value | false |  |
| Header / Properties | `statusLabel` | value |  |  |
| Header / Properties | `hasLeadingIcon` | value | false |  |
| Header / Properties | `leadingIcon` | object |  |  |
| Stacking Cards / Properties | `position` | value | regular | regular, top, center, bottom |
| Properties | `style` | object |  |  |

Events: `onActionPerformed`.

## 2. Accordion Item

<a id="accordion-item"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.accordion`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Opening and Closing / Properties | `title` | value | Accordion Item |  |
| Opening and Closing / Properties | `open` | value | false |  |
| Opening and Closing / Properties | `disabled` | value | false |  |
| Divider / Properties | `showDivider` | value | false |  |
| Properties | `style` | object |  |  |

Events: `onActionPerformed`.

## 3. Alert Detail

<a id="alert-detail"></a>

Disposition: `gap`. Cadre equivalent: None.

The stock alarm tables offer a details option (`enableDetails`).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Which Alarm Is Shown / Properties | `eventId` | value | empty |  |
| Which Alarm Is Shown / Properties | `titleSource` | value | label | label, name, notes, displayPath |
| Which Alarm Is Shown / Properties | `descriptionSource` | value | notes | label, name, notes, displayPath |
| Times / Properties | `dateFormat` | value | DD/MM/YYYY HH:mm:ss |  |
| Times / Properties | `showTimeInUtc` | value | false |  |
| Trend / Properties | `historyWindowSeconds` | value | 10800 |  |
| Trend / Properties | `historyPollSeconds` | value | 30 |  |
| Acknowledging / Properties | `canAcknowledge` | value | true |  |
| Acknowledging / Properties | `alertConvention` | value | levels | levels, bam |
| Acknowledging / Properties | `canComment` | value | true |  |
| Shelving / Properties | `canShelf` | value | true |  |
| Properties | `style` | object |  |  |

Events: `onAckAlarmClick`.

## 4. Alert Frame Container

<a id="alert-frame-container"></a>

Disposition: `implemented`. Cadre equivalent: Alert frame of the automation symbols (status colour, flashing when unacknowledged, dashed when rectified).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Content / Properties | `showFrame` | value | true |  |
| Alert Frame / Properties | `type` | value | regular | regular, small-side-flip, large-side-flip, bottom-flip, top-flip |
| Alert Frame / Properties | `status` | value | alarm | alarm, warning, caution |
| Alert Frame / Properties | `mode` | value | acked-active | acked-active, unacked-active, unacked-rectified |
| Alert Frame / Properties | `thickness` | value | small | small, large |
| Flap Content / Properties | `showAlertCategoryIcon` | value | true |  |
| Flap Content / Properties | `showIcon` | value | false |  |
| Flap Content / Properties | `icon` | object |  |  |
| Flap Content / Properties | `label` | value | empty |  |
| Flap Content / Properties | `timer` | value | empty |  |
| Corners / Properties | `sharpEdgeTopLeft` | value | false |  |
| Corners / Properties | `sharpEdgeTopRight` | value | false |  |
| Corners / Properties | `sharpEdgeBottomLeft` | value | false |  |
| Corners / Properties | `sharpEdgeBottomRight` | value | false |  |
| Properties | `style` | object |  |  |

## 5. Alert List

<a id="alert-list"></a>

Disposition: `framework`. Cadre equivalent: `Framework/AlertsPage` and `Framework/AlertMenu` over `ia.display.alarmstatustable` and `ia.display.alarmjournaltable`.

Reference row styling, alert categories and the detail pane are not reproduced (register COB-022).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Which Alarms Are Shown / Properties | `filter` | object |  |  |
| Which Alarms Are Shown / Properties | `maxAlerts` | value | 50 |  |
| Which Alarms Are Shown / Properties | `emptyTitle` | value | No unacknowledged alerts |  |
| Which Alarms Are Shown / Properties | `emptyDescription` | value | Go to the 'Alert list' for more details or to manage existin |  |
| Which Alarms Are Shown / Properties | `states.activeUnacked` | value | true |  |
| Which Alarms Are Shown / Properties | `states.activeAcked` | value | true |  |
| Which Alarms Are Shown / Properties | `states.clearUnacked` | value | true |  |
| Which Alarms Are Shown / Properties | `states.clearAcked` | value | false |  |
| Which Alarms Are Shown / Properties | `priorities.diagnostic` | value | false |  |
| Which Alarms Are Shown / Properties | `priorities.low` | value | true |  |
| Which Alarms Are Shown / Properties | `priorities.medium` | value | true |  |
| Which Alarms Are Shown / Properties | `priorities.high` | value | true |  |
| Which Alarms Are Shown / Properties | `priorities.critical` | value | true |  |
| Which Alarms Are Shown / Properties | `conditions.source` | value | * |  |
| Which Alarms Are Shown / Properties | `conditions.displayPath` | value | * |  |
| Which Alarms Are Shown / Properties | `conditions.provider` | value |  |  |
| Text and Time / Properties | `titleSource` | value | label | label, name, notes, displayPath |
| Text and Time / Properties | `descriptionSource` | value | notes | label, name, notes, displayPath |
| Text and Time / Properties | `dateFormat` | value | DD/MM/YYYY HH:mm:ss |  |
| Text and Time / Properties | `showTimeInUtc` | value | false |  |
| Acknowledging / Properties | `canAcknowledge` | value | true |  |
| Acknowledging / Properties | `alertConvention` | value | levels | levels, bam |
| Properties | `style` | object |  |  |

Events: `onItemClick`, `onAcknowledgeClick`.

## 6. Alert List Page

<a id="alert-list-page"></a>

Disposition: `framework`. Cadre equivalent: `Framework/AlertsPage` and `Framework/AlertMenu` over `ia.display.alarmstatustable` and `ia.display.alarmjournaltable`.

Reference row styling, alert categories and the detail pane are not reproduced (register COB-022).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Tabs / Properties | `mode` | value | unacked | unacked, active, shelved, history |
| Tabs / Properties | `filter` | object |  |  |
| Tabs / Properties | `priorities.diagnostic` | value | false |  |
| Tabs / Properties | `priorities.low` | value | true |  |
| Tabs / Properties | `priorities.medium` | value | true |  |
| Tabs / Properties | `priorities.high` | value | true |  |
| Tabs / Properties | `priorities.critical` | value | true |  |
| Tabs / Properties | `conditions.source` | value | * |  |
| Tabs / Properties | `conditions.displayPath` | value | * |  |
| Tabs / Properties | `conditions.provider` | value |  |  |
| Tabs / Properties | `journalProfile` | value | empty |  |
| Tabs / Properties | `historyLookbackHours` | value | 24 |  |
| Columns / Properties | `titleSource` | value | label | label, name, notes, displayPath |
| Columns / Properties | `descriptionSource` | value | notes |  |
| Columns / Properties | `dateFormat` | value | HH:mm:ss |  |
| Columns / Properties | `historyDateFormat` | value | DD/MM/YYYY HH:mm:ss |  |
| Columns / Properties | `showTimeInUtc` | value | false |  |
| Columns / Properties | `showCondition` | value | true |  |
| Columns / Properties | `canComment` | value | true |  |
| Acknowledging / Properties | `canAcknowledge` | value | true |  |
| Acknowledging / Properties | `alertConvention` | value | levels | levels, bam |
| Paging / Properties | `pageSize` | value | 50 |  |
| Paging / Properties | `page` | value | 1 |  |
| Detail Panel / Properties | `selectedEventId` | value | empty |  |
| Detail Panel / Properties | `canShelf` | value | true |  |
| Detail Panel / Properties | `historyWindowSeconds` | value | 10800 (3 hours) |  |
| Detail Panel / Properties | `historyPollSeconds` | value | 30 |  |
| Properties | `style` | object |  |  |

Events: `onItemClick`, `onAcknowledgeClick`.
