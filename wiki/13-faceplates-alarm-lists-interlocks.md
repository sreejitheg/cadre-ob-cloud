---
title: Faceplates, alarm lists and interlocks
type: wiki
updated: 2026-10-23
---
# 13 Faceplates, Alarm Lists and Interlocks

| Field | Value |
|---|---|
| Document ID | COB-WIKI-13 |
| Revision | I |
| Status | Issued for use |
| Built | Overnight session of 2026-10-08 under COB-PLAN-01 (work packages WP1 to WP6); second session of 2026-10-09 (the display only module tab, the latch); third session of 2026-10-10 (section 9) and its stage 2b of 2026-10-11 (section 9.7, the sequence and the pulse command, built and tested offline, not yet proven on the gateway); the ASMP build of 2026-10-22 and 2026-10-23 (section 10, offline) |
| Register | COB-062, COB-064, COB-076, COB-077, COB-078, COB-079, COB-138, COB-139, COB-140, COB-158 |
| Code | `tools/hmi/testbench.py` (the component test page, section 13), `tools/hmi/framework.py` (faceplates, module alarm views), `tools/hmi/scripts.py` (`cadre.hmi`), `tools/hmi/library.py` (the controller block, the indicator, the sequence block), `tools/hmi/screen.py` (the device model, the device index), `tools/hmi/gates.py` (G7), `tools/plants/wtp.py` (interlocks), `module/` (alarm list components), `tools/compare/faceplates.py` (G11), `tools/compare/functional.py` (G10) |

## 1. Purpose

This page records how a device faceplate is laid out, how it finds the device's alarms, the alarm
list functions and the Cadre HMI Components module's alarm components, the provisional interlock
and permissive contract, and, in section 9, how a faceplate lists only the members its device
carries, with the controller, the digital input, the maintenance functions and the sequence built on
that. Page 06
holds the faceplate contract; page 07 holds the gateway facts each design rests on.

## 2. Faceplate Tabs

Every device faceplate keeps the dock's header (identifier, description, close) and gains a tab row
beneath it, built on the tab row of the alerts page: `view.custom.tab` holds the selected key, the
buttons take the classes `cadre/button/selected` and `cadre/button/flat`, and one pane per tab is
shown through `position.display` (GF-08). Table 1 lists the tabs by faceplate.

Table 1. Tabs by faceplate.

| Faceplate | Kinds | Tabs |
|---|---|---|
| `Faceplate/Pump` | pump, motor, fan | Control, Alarms, Interlocks (only for a device with interlocks), Maintenance (only for a device with a `mnt/` member, section 9.6) |
| `Faceplate/Valve` | valve, analogue valve, damper | Control, Alarms, Interlocks (only for a device with interlocks), Maintenance (only for a device with a `mnt/` member) |
| `Faceplate/Tank` | tank | Values, Trend (only for a tank with `level`), Alarms (section 8) |
| `Faceplate/Instrument` | readout and instrument field marked as devices | Values, Trend (only for an instrument with `value`), Alarms (section 8) |
| `Faceplate/Controller` | controller | Control, Trend (only where a member of the loop is historised), Tuning (only for a loop with `gain`, `ti` or `td`), Alarms (section 9.4) |
| `Faceplate/Input` | indicator | Status, Maintenance (only for an input with a `mnt/` member), Alarms (section 9.5) |
| `Faceplate/Sequence` | sequence | Status, Trend (only where the step number is historised), Alarms (section 9.7) |

Rules:

1. The first tab is the default. A change of the view parameter `deviceId`, which follows the
   session's selected device, resets the faceplate to it through a change script on the parameter
   (the shape IGW:09 section 6 records).
2. The Control tab holds the status, command, mode, setpoint and reset rows of the faceplate before
   tabs, with the same texts; since 2026-10-10 each row shows only where the device carries its
   member (section 9.1).
3. The Alarms tab's label carries the device's alarm count, so the operator sees it without
   switching tabs (`cadre.hmi.alarm_count`, polled every 2 s).

## 3. The Device's Alarms

A device's alarms are every alarm whose source lies under the device's tag folder. The source of a
tag alarm reads `prov:<provider>:/tag:<folder>/<member>:/alm:<alarm>` (GF-34), so the pattern
`prov:<provider>:/tag:<folder>/*` selects them exactly; without the trailing slash, a folder P50
would also match P501. `cadre.hmi.device_source(deviceId)` writes the pattern, and a folder without
a provider gives a pattern that matches nothing, never the whole scope.

A device model (page 08 section 3.1) may leave a device's alarms on source tags outside its folder
and name them. An alarm configured on a reference tag is a second alarm beside the one on its source
(GF-52), so the alarms of such a device stay on the source tags only. The device index then carries the
device's patterns as `sources`, for example `prov:default:/tag:site/P1_OE:/alm:*`, and
`cadre.hmi.device_sources(session, deviceId)` returns them: the list of the index where the entry has
one, else the one folder pattern above. A list given empty matches nothing: the device has no alarm.
`system.alarm.queryStatus` takes the patterns as a list and returns nothing for two patterns in one
comma separated string; the stock table's `filters.active.conditions.source` takes them separated by
commas (GF-52; the Ignition-Wiki documents the comma form for the table). The faceplate therefore
hands `Faceplate/Alarms` the patterns joined with commas, and `alarm_count` and `alarm_list` split
that text, or take a list, before they query.

The list shows the states of the stock alarm status table's defaults: active and unacknowledged,
active and acknowledged, cleared and unacknowledged; every priority, Diagnostic included. The title
text no longer filters anything.

Under stock rendering the Alarms tab embeds `Faceplate/Alarms`, the stock alarm status table at the
dock's full height with `filters.active.conditions.source` bound to the pattern (GF-34 measured the
filter on the glass).

## 4. Alarm List Functions

`cadre.hmi.alarm_list(scope, source, states, max_items, no_ack, session)` returns alarm events as records of the
Package `Alert` type of the pinned package (`dist/types.d.ts`), most severe first, then newest
first. Table 2 maps each field to its Ignition source; every accessor was measured by experiment E4
before use (GF-34 to GF-36).

Table 2. The `Alert` record and its Ignition source.

| Field | Source |
|---|---|
| `id` | `getId()`, the event UUID |
| `tagId` | The device folder, from `getSource()`: `[default]cadre_hmi_wtp/P502`. With `session`, the folder of the device whose `sources` match the alarm's source, so an alarm on a source tag names its device (`cadre.hmi.tag_id`) |
| `source` | `getDisplayPathOrSource()` |
| `text` | `getLabel()`, else `getName()` |
| `note` | `getNotes()`, the alarm's own notes, when not empty |
| `type` | The priority: Critical `level-critical`, High `level-high`, Medium `level-medium`, Low `level-low`, Diagnostic `level-diagnostic` |
| `time` | `getActiveData().getTimestamp()`, epoch milliseconds |
| `acknowledged` | `false`, or `acknowledgedBy` (the raw `ackUser` without its `usr:` prefix) and `acknowledgedAt` (`getAckData().getTimestamp()`) |
| `active` | `true`, or `rectifiedTime` (`getClearedData().getTimestamp()`) once `isCleared()` |
| `shelved` | `false`: `queryStatus` leaves shelved events out unless asked (IGW:22 section 3.1) |

`cadre.hmi.ack(ids, session, notes)` acknowledges with the session's user, as the top bar does
(GF-21): the signed in user's name, or "operator" when nobody is signed in (command security,
COB-063, NOTE-COB-04). Only the second has been measured: nobody was signed in on 2026-10-08, and
the signed in path (`session.props.auth.user.userName`) is unverified (NOTE-COB-04 Table 1). The raw value map of event data is keyed by property objects, not strings, so
`acknowledgedBy` is found by matching the keys' text (GF-35); the probe found the string lookup
returning nothing before any view used it.

## 5. Module Alarm Components

The Cadre HMI Components module (page 12) gains two components in version 0.2.0, generated from the
manifest of the pinned component package like the pump and the tank. Table 3 lists them.

Table 3. The module's alarm components.

| Component | Element | Properties | Events |
|---|---|---|---|
| `cadre.ob.alertlist` | `obc-alert-list-details` | `alerts` (data), `selectedMode` (`unacked`, `all`, `shelved`, `blocked`, `rectified`), `showTime`, `small`, `componentSize` | `onAckClick`, `onRowClick` |
| `cadre.ob.alertpanel` | `obc-alert-list-page-small` | `alerts` (data), `selectedMode` (`unacked`, `all`, `shelved`), `showTime`, `hasShelved`, `componentSize` | `onAckClick`, `onRowClick`, `onSilenceClick`, `onAckAllClick` |

The generator gained two capabilities for them:

1. **Data properties.** A property declared as data in the component list carries JSON rather
   than a scalar attribute. The wrapper reads it from the property tree as plain data
   (`readArray`, GF-38), converts the epoch millisecond times of each `Alert` record into `Date`
   objects, and assigns the result to the element when its content changes.
2. **Event forwarding.** The wrapper listens for the element's own events and fires the matching
   Perspective component event through `componentEvents.fireComponentEvent(name, payload)` (GF-37).
   The payload carries `ids` (the alert ids), and for an alert event also `id`, `tagId`, `source`
   and `text`. For ACK visible it carries `mode` and the ids of every unacknowledged alert the
   element holds, which in mode `all` includes the cleared ones (`payload('visible')` of the
   generated wrapper), not the set the element's own event carries. The Java descriptors declare the events with `ComponentEventDescriptor`, as the
   SDK's perspective-component example does, with one generated schema per event.

Each element's enumerations are read from its own declaration file first: the two elements declare
an `AlertListMode` of the same name with five and three values.

The package's list draws, in mode `all`, the active alerts that are not shelved, and in mode
`rectified` the cleared ones (`getAlertListModeData` of the pinned release). The faceplate's module
view therefore shows two lists of the same data: the active alarms, and below them, only while
there are any, the cleared alarms not yet acknowledged. No alarm the stock table lists is hidden.
The small layout is used in the 368 px dock: status, time and the action column, without the "Tag
ID" column, which would show the alert id (an event UUID). The module's wrapper centres its element,
which suits a symbol; the rule that makes a list fill its box, top aligned, is in the module's own
stylesheet since version 0.2.1 (page 12 section 13).

A row's action column follows the record, as `render()` of the pinned `alert-list-details.js`
decides it: an active, unacknowledged alert of a type that needs acknowledgement shows an ACK
button, unless the record carries `noAck`, in which case the row draws the package's
no-acknowledgement icon (`obi-alarm-noack-iec` for the alarm, critical and high types,
`obi-warning-noack-iec` otherwise) in its place; every other row shows nothing there. The Alert type
of the pin declares `noAck` as an optional field, and the module's wrapper copies every field of a
record unchanged, so the display only list of section 6 needs no module change.

## 6. Module Rendering of the Faceplate and the Alarm Menu

A child built with `--render module` writes three views over the parent's: `Faceplate/Alarms` and
`Framework/AlertMenu`, the only views that carry a module alarm component, and `Faceplate/TankTile`
(section 8 rule 5). The parent stays stock,
and the stock rendering keeps the alarm status table (page 06 section 6 rule 3).

1. **Faceplate.** `Faceplate/Alarms` polls `cadre.hmi.alarm_list` for the device's pattern every
   2 s into one view property, and two `cadre.ob.alertlist` components draw it: the active alarms
   in mode `all`, and below them, only while there are any, the cleared alarms not yet acknowledged
   in mode `rectified`. The tab is display only (COBD-025, since 2026-10-09): the poll asks for
   records marked `noAck` (`alarm_list(..., no_ack=True)`), so a row draws the no-acknowledgement
   icon where it would offer ACK (section 5), and neither list carries an acknowledge event, so a
   crafted client that fires one reaches no script. Gate G7 refuses a module faceplate list with an
   acknowledge event or without the `noAck` marking; G10 check F10 proves on the glass that the tab
   offers no ACK and that a click on the action cell acknowledges nothing.
2. **Alarm menu.** The top bar's bell opens `Framework/AlertMenu`: a `cadre.ob.alertpanel` over the
   project scope, then the cleared alarms not yet acknowledged, then the link to the alerts page.
   ACK and ACK visible run `cadre.hmi.ack_event`. ACK visible acknowledges every unacknowledged
   alarm the menu holds, the cleared ones listed below the panel included: the module's wrapper
   builds the identifiers from the element's own alerts and does not use the set the pin's event
   carries (`getVisibleAlerts`, the active alarms only). The menu shows both lists, so the button
   acknowledges what the menu shows; the owner kept ACK and ACK visible in the menu (COBD-025), and
   G10 check F14 presses ACK visible. A row opens the device's faceplate: `cadre.hmi.select_alarm_device` finds
   the alarm's device folder in the device index the generator writes into the session
   (`session.custom.devices`: folder, kind, identifier, description), and the script closes the
   popup and opens the dock. The menu's poll passes the session to `alarm_list`, so the record of an
   alarm on a source tag already carries its device's folder (section 3). Since WP6 the instruments are devices too, so an analyser's alarm opens
   the instrument faceplate (section 8); an alarm whose folder is in no descriptor opens nothing.
3. **What stays stock.** The top bar's banner, count and ACK (`alarm_summary`, `ack_top`) and the
   alerts page's status and journal tables. A fault in the module cannot hide the existence of an
   alarm.

The package's list offers ACK only on an active alarm that is not acknowledged. A cleared alarm not
yet acknowledged is shown in both module views and is acknowledged on the alerts page, with the
stock table's own Acknowledge, or with ACK visible in the menu, each by a session whose user holds the
admin role (COBD-024; the table's Acknowledge worked with nobody signed in until 2026-10-09, GF-40).

The owner decided on 2026-10-09 that alarm actions (acknowledge, shelve and the like) are taken on
the alerts page, in the top bar's alarm menu and with the top bar's ACK, and that the faceplate's
module Alarms tab is display only, listing the device's active and unacknowledged alarms
(COBD-025). The second session built it as item 1 describes (COB-082). The stock rendering's
faceplate tab is not changed by the decision: its alarm status table keeps its own Acknowledge, which
since command security (COBD-024) is offered to a session whose user holds the admin role only.

## 7. Interlock and Permissive Contract (Provisional)

The contract stays provisional (COB-079) while section 7.2 lists items open against the core device
contract of the library sets study (SPEC-CLS-01, COB-BRIEF-02 work package S5). The owner answered
the two questions of N-COB-8 on 2026-10-09 (COBD-023): a trip latches until it is reset, and
`interlock-inhibit` means a bypassed interlock. Table 4 gives the members of one condition, held
under `<device>/ilk/Cnn/` for nn from 01 without a gap; Table 5 gives the device summary under
`<device>/ilk/`. Where SPEC-CLS-01 Table 4 names a member, this contract uses its name (COBD-026).

Table 4. Members of one condition.

| Member | Type | Meaning |
|---|---|---|
| `kind` | String | `permissive`, required to start, or `trip`, which stops a running device |
| `text` | String | The condition in operator words |
| `action` | String | What the operator does when the condition is not met |
| `ok` | Boolean | The condition is met |
| `liveText` | String | The live value as text: `Closed`, `12.4 %` |
| `requiredText` | String | The required value as text: `Open`, `at least 20 %` |
| `bypassed` | Boolean | The condition is bypassed now (was `bypass` until 2026-10-09) |
| `bypassable` | Boolean | The condition may be bypassed |
| `latched` | Boolean | The condition latches until reset; true for every trip (COBD-023, gate G7) |
| `resetRequired` | Boolean | The condition is latched, met again, and waits for a reset |

Table 5. Device summary members.

| Member | Type | Meaning |
|---|---|---|
| `permitted` | Boolean | Every permissive is met or bypassed, and none waits for a reset |
| `interlocked` | Boolean | A trip is not met and not bypassed, or waits for a reset |
| `bypassed` | Boolean | A condition is bypassed |
| `unsatisfied` | Int4 | The conditions not met and not bypassed |
| `resetRequired` | Boolean | A latched condition waits for a reset |
| `resetAt` | Int8 | The gateway time (epoch milliseconds) of the last reset request, written by the Interlocks tab's Reset |
| `badge` | String | The symbol's badge: `interlock`, `interlock-inhibit` or `none` (sample model) |

Rules as built:

1. **Start.** A device with interlocks starts only while permitted and not interlocked: the
   sample's `state` expression holds a start (a self reference, GF-16), and the faceplate's Start
   writes nothing while `cadre.hmi.start_permitted` is false, so no start is left pending. The
   Control tab then states why: "Start not permitted: n conditions not met", "Interlocked: n
   conditions not met", or, once the causes have cleared, "Interlocked: reset required", with a link
   to the Interlocks tab; after a refused Start it reads "Start refused".
2. **Trip and latch.** A running device stops when it becomes interlocked. A permissive lost while
   running does not stop it. A trip latches (COBD-023): when its cause clears, the condition reads
   "Latched", the device stays interlocked, and the Interlocks tab shows Reset beneath its title. Reset writes the time of the request to `ilk/resetAt`
   (`cadre.hmi.reset_interlocks`). A latched condition waits for a reset while it is met and was last
   seen not met after the latest reset (the sample keeps that time in a member `notMetAt`, and the
   latest request in `ilk/resetSeen`, both self references). A Reset pressed while the cause persists
   therefore releases nothing (G10 F12 forces one), except within the expression tags' evaluation
   period of about 1 s: a cause that clears less than a second after a Reset can be released by it.
   No request member needs clearing by the plant, which suits a simulation without a controller.
   `resetSeen` keeps the latest request through an import, which returns `resetAt` to 0 but leaves a
   self reference at its value (GF-42); without it a bare import latched every trip ever reset
   again (found by the review of 2026-10-09, the fix measured on the gateway).
3. **Badge.** The symbol's `badgeInterlock` follows the summary: `interlock` while the device is held
   (not permitted, or interlocked, a latched trip included), `interlock-inhibit` while a condition is
   bypassed. The pinned manifest describes neither value; the package draws `interlock` with its duty
   icon and `interlock-inhibit` with its standby icon (`automation-badge.js`), and the library draws
   them the same way. The owner confirmed the reading of `interlock-inhibit` as a bypass on
   2026-10-09 (COBD-023).
4. **Bypass.** A bypass shows on its row ("Bypassed") and on the symbol. A bypassed condition never
   holds the device, latched or not. Writing `bypassed` is a maintenance action, write path W10 of
   NOTE-COB-04, which needs the admin role (COBD-024): a bypassable condition's row offers Bypass
   (Unbypass while bypassed), enabled for a session whose user holds the role, and
   `cadre.hmi.bypass` refuses any other session and any condition whose `bypassable` is false.
5. **The tab.** The Interlocks tab, labelled with the count of conditions that hold the device (not
   met, or latched and waiting for a reset; `holding` of `cadre.hmi.interlock_summary`), appears only
   for a device whose folder carries `ilk`;
   `cadre.hmi.interlock_rows` and `interlock_summary` look for the tags with `system.tag.exists`
   before reading, so a device without interlocks binds no missing tag. Each row shows the state
   (Met, Not met, Latched, Bypassed), the kind, the condition, the live and required values, and,
   while the condition holds the device, the action.

Table 6 lists the sample's interlocks (`tools/plants/wtp.py`, `interlocks()`).

Table 6. Interlocks of the water treatment sample.

| Device | Condition | Kind | Met when | Bypassable | Initial state |
|---|---|---|---|---|---|
| P-101 | C01 Raw water tank level at least 20 % | permissive (analogue) | TK-101 level at least 20 % | Yes | Met |
| P-101 | C02 Clarified water tank level below 95 % | trip (analogue), latching | TK-202 level below 95 % | No | Met |
| P-301 | C01 A filter inlet valve is open | permissive (discrete) | XV-301, XV-302 or XV-303 open | Yes | Met |
| P-502 | C01 Pump fault clear | trip (fault), latching | P-502 not faulted | No | Not met: P-502 starts faulted, so its badge shows at start, and after Reset fault it waits for the Interlocks tab's Reset |

### 7.1 Reconciliation with the Core Device Contract

Table 7 compares this contract with SPEC-CLS-01 (read on 2026-10-09; its section 7 lists the
differences) and records what the second session adopted.

Table 7. Reconciliation with SPEC-CLS-01.

| Item (SPEC-CLS-01 section 7) | Core contract | This contract | Status |
|---|---|---|---|
| 2 Bypass split | `bypassed`, `bypassable` | `bypassed`, `bypassable` | Adopted 2026-10-09 (the member `bypass` renamed; nothing outside this repository bound it) |
| 3 Latched | `ilk/Cnn/latched` | `latched` | Adopted, with COBD-023 |
| 4 Reset required | `ilk/resetRequired` | `resetRequired` on the summary, and the same name on each condition | Adopted; the per-condition member is an addition the core does not define |
| Reset request | `cmd/reset` (Boolean request, cleared by the adapter, CDC-011) | `ilk/resetAt` (the request time) | Different by design: Family O has a maintained `cmd` member, not a `cmd/` folder, and no controller clears a request (item 8 of SPEC-CLS-01 section 7) |
| 5 Optional texts | `liveText`, `requiredText`, `action` optional | Carried by every sample condition | Consistent |
| 7 Command refusal | The source system refuses; the faceplate explains (CDC-013) | The Family O simulation and the faceplate refuse | Consistent: SPEC-CLS-01 keeps the WP5 rule for Family O |
| 1 Condition type | `type`, eight PlantPAx types carrying the defaults for bypassable and latched | Not carried | Open |
| 3 I/O fault, first out | `ioFault`, `firstOut` per condition | Not carried | Open |
| 4 Summary | `nbOk`, `firstOut` (an index) | Not carried | Open; a first out needs the time each condition tripped first, which the sample does not keep |
| 6 Banks | Up to eight banks of 32, flat `Cnn` | Flat `Cnn` from 01 | Consistent; a `bank` member is not carried |
| 8 Command semantics | Request members (`cmd/start`, `cmd/stop`) | A maintained `cmd` | Open for the library sets study: its Family O adapter maps them |
| CDC-035 | The screens write no bypass until command security exists | W10 writes `bypassed` for the admin role only, on a bypassable condition | Consistent: command security exists since 2026-10-09 (COB-063) |

### 7.2 Open Items

The word provisional stays until these close: the condition `type`, `ioFault` and `firstOut`; the
summary's `nbOk` and `firstOut`; the request members of the core's command semantics; and the
owner's review of the latch and the reset as built against site PLC practice.

## 8. Analogue Instruments and the Trend

A readout or an instrument field marked as a device in the descriptor (`"device": true`, or the
folder for an overview field) opens `Faceplate/Instrument` (COB-062). The tank faceplate moves to the
same layout. Table 8 lists the tabs.

Table 8. Instrument and tank tabs.

| Tab | Content |
|---|---|
| Values | The value with its unit (the unit from the device index); the alarm limits the device has (`hiHiLimit`, `hiLimit`, `loLimit`, `loLoLimit`) as setpoint fields, each with a lamp lit while the value is beyond it; the tank adds its tile |
| Trend | The last hour of `value` (the tank's `level`) from the historian, 8 h selectable, with the limits drawn level across the chart |
| Alarms | As section 3 |

Rules:

1. **Limits are setpoints.** A limit field shows its member through a one way tag binding and
   writes it on commit through `cadre.hmi.command` (write path W4 of NOTE-COB-04, the admin role,
   COBD-024); a refused write puts the tag's value back and the row's lamp reads "Refused". Only
   the limits a device carries are listed (`cadre.hmi.limit_rows` looks for them first), so no
   faceplate binds a missing tag; a device without the member the limits belong to (`value`, or the
   tank's `level`) lists none, since each row also reads that member.
2. **The alarm follows its limit.** In the sample, every limit drives its alarm: the alarm's
   `setpointA` is bound to the member by an expression (`{"bindType": "Expression", "value":
   "{[.]hiLimit}"}`), the form the tag corpus writes for `displayPath`; page 07 records the
   measurement on the gateway.
3. **The trend.** A stock `ia.chart.timeseries`: series 0 comes from a tag history binding whose
   `tags` is the reference `{view.custom.historyTags}`, a view property holding a list of one path
   object (a path string is rejected by the runtime; `pv.tag_history` refuses one and gate G7 checks
   every history binding of every view); its date range is `{view.custom.hours}` hours, the form the
   corpus writes for a selectable range; 300 rows, averaged, polled every 10 s. Series 1 carries the
   limits as two points at the ends of the range (`cadre.hmi.limit_series`), each limit drawn as a
   dashed line (`plots[].trends[].columns[].styles`, `stroke.dashArray` 6 4, in the normal,
   highlighted and muted states). For the 368 px dock (COB-083) the time axis shows four labels in
   24 hour form (`timeAxis.tickCount` 4, `timeAxis.tick.label.format` `HH:mm`, a MomentJS string) and
   the value axis five, to three significant digits (`plots[].axes[].tick.count` 5,
   `tick.label.format` `.3~g`, a D3 format); every property is one the Ignition-Wiki documents for
   `ia.chart.timeseries`. `trend_chart` in `framework.py` builds this chart for the faceplate and
   the trend page.
4. **Markers (Cadre-Sandbox-ASM observation O5).** Measured on 2026-10-09 with a probe chart: the
   chart draws `plots[].markers` of type `line`, dashed by `line.dashArray`, with their label at the
   right, but only inside the value axis's range, which a marker does not extend: markers at 0.12 and
   0.18 beside data from 0.125 to 0.175 drew nothing, at 0.14 and 0.16 they drew. A limit far from
   the value (AIT-301's high limit 1.0 beside a value near 0.15) would therefore not show, so the
   limits stay a series, which the axis spans.
5. **History.** The 17 analogue members of the sample are historised since WP0 (page 11).
6. **The trend page (COB-064).** A child whose descriptors have devices with a trend (an
   instrument's `value`, a tank's `level`) that its tag model historises gets the route `/trends`,
   titled Trends, in its navigation menu. The generator builds the list from the descriptors' device
   index, keeping the members whose tag has `historyEnabled` (`screen.trend_index`; without a tag
   model there is no page, since only the model says what is historised), and writes it to
   `session.custom.trends`. The page (`Framework/TrendsPage`) has a range row (1, 8 or 24 h) and one
   card per member (`Trend/Card`: identifier, description and unit above the chart of rule 3, limits
   dashed); a card's title opens the device's faceplate. The water treatment sample has 17 cards. A
   device model may state the historised members itself (`trend`); the index then lists exactly those
   for the device, and a controller's setpoint and output get cards of their own (section 9.4). The
   card of a stepped member, a sequence's step number, draws its line as steps (section 9.7 rule 5).
7. **The tank's tile.** The tank faceplate draws its tile through `Faceplate/TankTile`: the library
   tank at the level in per cent under stock rendering; under module rendering a child overrides it
   with the module's tank, as the diagram draws it (the owner saw the stock tile beside the module's
   tank on 2026-10-08). The module's tank has no unit property and labels its value in m³
   (COB-075), so the tile shows the volume against the capacity where the folder carries both, and
   the trend where it carries one (`cadre.hmi.tank_tile`).

## 9. Member Lists, the Controller, the Digital Input, Maintenance and the Sequence

The third build session rebuilds a source project whose devices do not carry every member the
faceplates of sections 2 to 8 read: a pump with a run status and an object error and no command, a
valve with no mode, a loop with no tuning. This section records what was built for them on
2026-10-10, and in section 9.7 the sequence and its pulse command, built on 2026-10-11. It is built
and tested offline (unit tests, the parent build, gates G0 to G7 on four child builds); section 9.8
lists what the gateway has proven and has yet to prove.

### 9.1 Reading a Device

A tag binding to a missing tag draws null under a quality overlay, which gates G8 and G11 fail on.
No device faceplate therefore binds a member's tag. Each polls
`cadre.hmi.device_read(session, deviceId, members)` once a second into one view property,
`custom.dev`, and derives every row from it. The function looks for each member with
`system.tag.exists` and reads those present in one `system.tag.readBlocking` call. Table 9 gives the
structure it returns; a member's key is its name with the slash of `mnt/` written as an underscore.

Table 9. The structure of `custom.dev`.

| Key | Content |
|---|---|
| `has` | Member key to Boolean: the device carries the member |
| `value` | Member key to value, in the type of the member's default; the default itself where the member is absent or reads null, so that no expression meets null |
| `bad` | The present members whose quality is not good |
| `quality` | The line the faceplate shows for them, `Bad quality: state, fault`, else empty |
| `writable` | Member key to Boolean: the member exists, a write path writes it, the device is in the session's device index and the device model does not mark it read only. The member's control is shown |
| `write` | Member key to Boolean: `writable`, and the session's user holds the role of the member's write path. The member's control is enabled |
| `mnt` | The device carries a row of the Maintenance tab: a whole force, the object error mask or a flag |
| `force` | Empty, or `auto`, `on`, `off` (section 9.6); `writable.force` and `write.force` cover the force's members |
| `pulses` | Member key to text, for each pulse member among the members read: the caption of its button, which is the device model's caption or else the member's name (section 9.7). Empty for a faceplate that reads no pulse member |

Rules as built:

1. **Display.** A row, a section title, a command group or a tab is shown through
   `position.display` (GF-08) only while its member exists. A section title carries the condition of
   its rows, so a section with no row disappears with its title. A pump with `state` and `fault` only
   shows Status with State and Fault, and nothing else on the Control tab.
2. **Commands.** A command group shows only where its member may be written (`writable`), and each
   control binds `enabled` to the permission of its write path and to the member's `write` flag. A
   pump whose `fault` is a status of the source therefore offers no Reset fault. A setpoint row
   shows where its member exists, and its field is enabled only where the member may be written. The
   limit rows, a condition's Bypass and the Interlocks tab's Reset follow the same list through flags
   of their own (`writable` of `limit_rows` and `interlock_rows`, `resetWritable` of
   `interlock_summary`): each is disabled for every session where the device model marks its member
   read only.
3. **Quality.** A polled value draws no quality overlay. A reference tag whose source is missing
   still exists and reads null with a bad quality (GF-50), so the faceplate states the members of bad
   quality in words, on a line beneath the tab row that shows on every tab. Gate G11 fails on that
   line as it fails on an overlay. The quality is read as text (`Good`, or for example
   `Bad_NotFound`), the form experiment E6 measured.
4. **What keeps its own logic.** The limit rows, the interlock rows and the tank tile look for their
   members themselves, as before (`limit_rows`, `interlock_rows`, `tank_tile`).
5. **One pass over the index.** A poll looks the device up in the device index once
   (`_write_rule`) and answers every member from that one entry.
6. **A project without a device model.** Every member of the water treatment sample exists and no
   index entry carries a `write` list, so its faceplates show the rows and the texts they showed
   before; the walks of gates G10 and G11 read those texts on the glass.

### 9.2 Setpoint Rows

A setpoint field has to keep the text an operator is typing while the faceplate polls. The field is
therefore not bound to the polled structure at all. It keeps the one way indirect tag binding the
speed setpoint and the limit rows carried since command security (`mode` `indirect`, `tagPath`
`{0}/{1}`, `references`; IGW:06-bindings section 4, no `bidirectional` key), which hands the field a
value when the member changes and not at each poll; gate G10 has typed into that binding since
2026-10-09 (checks F5 and F13). The field sits in a row view of its own, `Faceplate/SetpointRow`
(parameters `deviceId`, `member`, `label`, `path`, `format`, `minimum`, `maximum`, `unit`, `enabled`),
and the faceplate holds a repeater with that one row while the device carries the member and with no
row otherwise, the pattern of the limit rows. The binding therefore never meets a missing tag. The
commit runs `cadre.hmi.command` with the row's write path; a refused write puts the tag's value back
and the row reads "Refused". The row serves the speed setpoint (W3), the controller's setpoint (W12),
its manual output (W14) and its tuning (W15).

The text of a refusal stays in the row view (`custom.message`), which shows the one word, as the
limit row always has. This is a change for the speed setpoint: before the row view, a refused speed
setpoint put the whole text, for example "Refused: sign in with the Administrator role", on the
faceplate's message line. The entry bounds of a field (`minimum`, `maximum`) are the range
`cadre.hmi.command` enforces for the member (`MEMBER_BOUNDS`), so a value the field would not take is
refused by the function as well.

### 9.3 The Device Model in the Session

With a device model the device index (`session.custom.devices`) carries, for each device the model
names: `sources` (the source patterns of its alarms, section 3), `write` (the members a session may
write) and `members` (every member it carries); the kind, identifier, description and unit come from
the model where it gives them. Every checked write refuses a member that is not in the `write` list of
its device: `command`, `force`, `error_mask`, `bypass` and `reset_interlocks`. A project built without
a model has no list on any device, and each keeps the rule of its write path alone. A build with a
model also sets `session.custom.deviceModel`; in such a project a device whose entry has no list may
write nothing, so a lost list refuses where it would otherwise permit.

### 9.4 The Controller

A PID loop is the kind `controller`. Table 10 gives its members; every one is optional.

Table 10. Members of a controller.

| Member | Type | Meaning | Written by |
|---|---|---|---|
| `value` | Float8 | The process value, under the name the instrument uses, so that readouts, limits and the trend apply | Not written |
| `sp` | Float8 | The setpoint | The setpoint field, W12 |
| `out` | Float8 | The output in per cent | Not written |
| `manual` | Boolean | False automatic, true manual | The Auto and Manual buttons, W13 |
| `manOut` | Float8 | The manual output in per cent | The manual output field, enabled only while `manual` is true, W14 |
| `gain`, `ti`, `td` | Float8 | Gain, integral time and derivative time, the times in milliseconds | The Tuning tab's fields, W15 |
| `hiHiLimit`, `hiLimit`, `loLimit`, `loLoLimit` | Float8 | The alarm limits of the process value, as section 8 | The limit rows, W4 |

1. **On a page.** `Instrument/Controller` draws the loop as one block in the manner of
   `Instrument/Field`: the package control badge (`auto`, or `manual`) beside the identifier or the
   label, the setpoint marked as the instrument field marks it, the process value large with its unit,
   and the output in per cent. Parameters: `value`, `setpoint`, `output`, `manual`, `hasSetpoint`,
   `hasOutput`, `unit`, `format`, `label`, `tag`, `hasTag`, `deviceId`, `deviceKind`, `deviceLabel`.
   `hasSetpoint` and `hasOutput` default false, as the instrument field's `hasSetpoint` does: the
   descriptor sets each for a loop that carries the member, and gate G7 devices fails one set for a
   device that does not list `sp` or `out`.
   It is a box and passes the medium in the flow graph. A device binds `value` to `value`, `setpoint`
   to `sp`, `output` to `out` and `manual` to `manual` (gate G7).
2. **A readout of the process value.** A readout or an instrument field whose `device` names a
   controller and whose `params.deviceKind` is `controller` opens the controller's faceplate. The
   binding rule then follows the device's kind, not the symbol's: the field's `setpoint` binds `sp`.
3. **Control tab.** The process value large with its unit; the setpoint field; the output as a value
   and as a bar (`ia.display.progress`, `min` 0, `max` 100); the control mode with its Auto and Manual
   buttons; the manual output field; the alarm limits. `cadre.hmi.command` refuses the manual output
   while `manual` does not read true, a value that is not a number, a manual output outside 0 to 100
   and an integral or derivative time below 0 (NOTE-COB-04 section 11.5 item 6).
4. **Trend tab.** One chart, built by `trend_chart`: the process value, the limits and the setpoint on
   the value axis, and the output on a second axis at the right from 0 to 100
   (`plots[].axes[].alignment`, `min`, `max`). Each member is a series of its own with its own tag
   history binding, and its trend is visible only where the trend index lists the member
   (`cadre.hmi.trended`, `trend_tags`); the tab shows only where it lists one. The index takes a
   controller's members from the device model's `trend` list, or without one from the members of
   `value`, `sp` and `out` that the tag model historises. A series whose member is not trended keeps
   a tag history binding with an empty path for the whole session (`trend_tags`), where the faceplates
   of section 8 held an empty path only before a device was selected (section 9.8 item 4).
5. **Tuning tab.** Gain, integral time (ms) and derivative time (ms) as setpoint rows, each only where
   the loop carries the member; the tab only where it carries one.

### 9.5 The Digital Input

A digital input shown as a lamp is the kind `indicator`: `Automation/Indicator`, a symbol of the
automation factory with the state parameter `on`, the status row On or Off, and every other parameter
of Table 2 of page 06 (`alert`, `badgeControl` and the rest). The pinned release has no lamp, so the
artwork is drawn in the library from primitives in the two tone style of the package automation
icons: a ring, with a filled centre while lit. Nothing was downloaded. The input passes the medium
whatever its state. Its faceplate, `Faceplate/Input`, has the tabs Status (the state as On or Off),
Maintenance and Alarms. Its members are `state` and the maintenance members of section 9.6.

**Colour by state (Level 5, COB-165).** The lamp's colour says its state: it draws no status row (`showStatus` defaults to
false and the Readout toggle does not bring it back) and no alert frame or flap. A descriptor binds `bind.state` and may give
`states`:

```json
{"id": "L1", "kind": "indicator", "x": 40, "y": 40, "w": 48, "h": 48, "params": {"hasTag": true, "tag": "L-1"},
 "bind": {"state": "plant/lamp1"},
 "states": [{"value": 0, "colour": "off", "label": "Off"}, {"value": 1, "colour": "on", "label": "On"},
            {"value": 2, "colour": "alarm", "label": "Alarm"}], "stateDefault": "neutral"}
```

The generator reads the tag once into `view.custom.g_<id>` and binds the embed's `colour` to
`case({view.custom.g_L1}, 0, <paint>, 1, <paint>, 2, <paint>, <default paint>)` (no script transform) and `on`, for the icon, to
the states whose colour is not `off`. Without `states`, false is `off` and true is `on` and `colour` is not bound. The palette
names map to the theme tokens of the parent:

Table 10a. The palette of an indicator's states.

| Name | Token |
|---|---|
| `off` | `--automation-button-off-background-color` |
| `on` | `--on-background-color` |
| `active` | `--element-active-color` |
| `alarm` | `--alert-alarm-color` |
| `warning` | `--alert-warning-color` |
| `caution` | `--alert-caution-color` |
| `critical` | `--alert-critical-color` |
| `neutral` | `--element-neutral-color` |

A value that is none of these names is used as a CSS paint. The lamp's fill and its border take the colour; the view's
`colour` parameter, empty by default, keeps today's on and off colours. A generated tag model types the state tag by the
values of `states` (Boolean, Float8 or String).

### 9.6 Maintenance Functions

A pump, a valve or an input may carry maintenance members in a subfolder `mnt/`. Table 11 lists them.

Table 11. Maintenance members.

| Member | Type | Meaning |
|---|---|---|
| `mnt/forceOn`, `mnt/forceOff` | Boolean | The force as a pair of flags: forced on, forced off, or automatic while both are false |
| `mnt/forceMode`, `mnt/forceValue` | Boolean | The force as a mode and a value (a newer interface): forced while the mode is true, to the value |
| `mnt/errorMask` | Boolean | The object error mask: masked while true |
| `mnt/simulated`, `mnt/alarmSuppress`, `mnt/manualMode` | Boolean | Read only flags |

The Maintenance tab shows only for a device with a row to show (a whole force, the mask or a flag: a
device that carries one member of a force and nothing else gets no tab), and each row only while its
members exist:

1. **Force.** The state in words (Automatic, Forced on, Forced off) and the buttons Force on, Force
   off and Automatic, write path W16. `cadre.hmi.force(session, deviceId, action)` writes a device with
   the mode and the value first: the value, then the mode, and for automatic the mode alone. A device
   with the pair gets the flag that clears, then the flag that sets. Each member is a write of its own
   and the second is made only when the gateway made the first, so a write that fails leaves the
   device as it was or automatic, never forced the other way and never with both flags true. A device
   that carries both interfaces is written through the mode and the value; gate G7 devices refuses a
   device model that lists both, one member of either, or the two members of one in different access.
2. **Object error mask.** Masked or Automatic, and the buttons Mask and Automatic, write path W17,
   `cadre.hmi.error_mask(session, deviceId, value)`.
3. **Flags.** Simulated, Alarms suppressed and Manual mode, each Yes or No.
4. **Refusal.** Each function refuses a session without the role (COBD-024), a device that is not in
   the session's device index, a device without the members, and a member the device model does not
   mark writable; the force is refused whole, whatever the action, where either of its members is
   read only. A write the gateway does not make (an expression tag, a reference tag without its
   source) is answered in the same way. The refusal shows on the tab.
5. **The symbol.** A forced device shows on its symbol where the descriptor binds `badgeControl`,
   which every automation symbol has, the indicator included. The fixture binds it to a text member
   of its own.

### 9.7 The Sequence and the Pulse Command

A device that runs through numbered steps, each with a text (a self cleaning filter, a boiler, a
steam letdown station, a softener), is the kind `sequence`, built on 2026-10-11. Table 12 gives its
members; every one is optional.

Table 12. Members of a sequence.

| Member | Type | Meaning | Written by |
|---|---|---|---|
| `step` | Int4; any integer type suits | The number of the current step | Not written |
| `stepText` | String | The text of the current step, computed in the tag model, which knows the steps | Not written |
| `trigger` | Boolean | A pulse command: set to start a cycle, and returned to false by the plant | The pulse button, W18 |
| `fault` | Boolean | The fault of the sequence | Not written by this faceplate |

1. **On a page.** `Instrument/Sequence` draws the sequence as one block in the manner of
   `Instrument/Controller`: the identifier or the label, the text of the current step large, and the
   step number small beneath it, for example "Step 2". Parameters: `text`, `step`, `hasStep`, `label`,
   `tag`, `hasTag`, `deviceId`, `deviceKind`, `deviceLabel`; like the controller's block it carries
   no alert parameters. `hasStep` defaults false, and gate G7 devices fails one set for a device that
   does not list `step`. The number is formatted whole, whatever type the tag holds. The default
   size is 144 by 72 px. The block is a box, a pass node in the flow graph, and no state of it gates
   the medium. A device binds `text` to `stepText` and `step` to `step` (gate G7). The text is one
   line of 16 px in 130 px: at the default width about 14 to 16 characters show, and a longer
   text ends in an ellipsis and has no tooltip. A step text for the block is therefore short
   ("Drive Out"), or the descriptor gives the block more width; the faceplate shows the text in full
   within the limit of rule 2. The identifier above it has the same 130 px, which hold the 16
   characters an identifier may have (page 06 section 4.1). Until 2026-10-11 both labels carried
   `text-overflow` themselves, which shows no ellipsis on a Perspective label: a text too long was
   cut with nothing to say so. They now carry the layout class `cadre/text/ellipsis`, as the head of
   the controller's block does.
2. **Status tab.** `Faceplate/Sequence` has the tabs Status, Trend and Alarms. Status shows the text
   of the step large, the step number, the fault as Normal or Fault where the device carries `fault`,
   and under Commands one button for each pulse member the device may write. Each shows only while
   its member exists. The step text wraps to two lines of 22 px in the 368 px dock, which hold about
   60 characters; a longer text, or one word wider than the dock, is clipped. Both limits are read
   from the built views and the stylesheet and remain to be confirmed on the glass (gates G8 and
   G11).
3. **The pulse command.** A pulse member is a Boolean member that a session sets and the plant, or a
   simulation, returns to false. `cadre.hmi.pulse(session, deviceId, member)` writes true to it and
   writes nothing else (write path W18, the admin role, COBD-024; NOTE-COB-04 section 11.5 items 11
   to 14). It refuses a session without the role, a member that is not a pulse member, a device that
   is not in the session's device index or does not carry the member, and a member the device model
   does not mark writable; a write the gateway does not make is answered in the same way, and the
   refusal shows on the tab. The library knew one pulse member when this section was written, `trigger` of a
   sequence; since section 12.5 it knows nine (`FUNCTION_MEMBERS` under `PULSE_PATH`, the `pulses` of the profile,
   page 17 Table 17). `cadre.hmi.command` writes no pulse member, and the
   private helper that makes the write refuses, on the pulse path, any value but the Boolean true, so
   no call of `cadre.hmi` writes one false. The function does not ask the kind of the device: in a
   project built without a device model a session with the role may pulse any device of the index
   whose folder carries a tag named `trigger`, as the rule of a write path stands alone there for
   every path; with a device model the `write` list decides, and gate G7 devices lets only a kind
   with the pulse member mark it.
4. **Captions.** In a device model a pulse member carries `"pulse": true` and may carry a `caption`
   (page 08 section 3.1). The device index lists the pulse members of a device with their captions
   (`pulses`), `device_read` answers the caption of each (`dev.pulses`), and the button shows it. A
   pulse member without a caption, and every pulse member of a project built without a device model,
   shows the member's name. A caption is one line of 1 to 32 characters, with no space at either end
   and no line break or other character that does not print: the button is 40 px high and draws one
   line of its 16 px font. The schema of the device model and gate G7 devices both state the bound
   (`gates.CAPTION_MAX`). The button shows only while its member may be written, and binds
   `enabled` to the permission of W18 and to the member's `write` flag.
5. **Trend tab.** The step number over time as a stepped line: the chart of `trend_chart` with
   `plots[].trends[].interpolation` set to `curveStepAfter` (IGW ia.chart.timeseries), so that a
   value holds until the next sample. The path object of the history binding carries the aggregate
   `LastValue` (IGW:06-bindings section 7; `cadre.hmi.history_tags`, `STEP_MEMBERS`), since the
   average of an interval that spans a change would draw a step the sequence never took. The tab
   shows only where the trend index lists `step` for the device: the device model's `trend` list, or
   without one the tag model's history. The trend page's card draws a stepped member in the same way
   and every other member as before.
6. **The fixture.** `tests/fixtures/pilot-*.json` carry a sequence, FLT-1, a self cleaning filter.
   `step` and `stepText` are expression tags with four steps (1 Standby, 2 Drive Out, 3 Drive Back,
   4 Fault), `trigger` is a memory tag marked a pulse with the caption "Start cycle", and `fault` is a
   reference to a source tag that carries the alarm. The fixture stands in for the controller with a
   value-changed event script on the trigger (GF-57): when the trigger turns true the script stamps a
   helper tag, `started`, with the time and returns the trigger to false. The step reads the time
   since the stamp: 2 for 5 s, 3 for 5 s, then 1 again, so every pulse runs one cycle. An
   expression tag could not do this, because it writes nothing (GF-49). On a plant the controller
   returns the trigger.
7. **The fixture and the first plant page.** Since 2026-10-11 the fixture also shows what the first
   page built from a plant's data showed (page 06 sections 4.1 and 4.2): the pump with the run command
   has an identifier of 14 characters (`SupplyPump_No2`), the instrument one of 15
   (`SupplyFlow_FT01`, in a readout 130 by 40 px) and the indicator one of 16 (`SuctionLowLvl_SW`),
   each also the device's title in the device model, so its faceplate header shows it; and a static
   tank that states no capacity (`Break tank`, no device) stands at the head of the line with a pipe
   at each side. The devices, their folders and their members are as before.

### 9.8 Status of This Section

Proven offline on 2026-10-10: 95 unit tests, which run the text of `cadre.hmi` against stand-ins for
the tag and alarm functions; the parent build with gate G1 clean over 35 views; and gates G0 to G7 on
`cadre_hmi_wtp`, `cadre_hmi_wtpob` and `cadre_hmi_sample`, built without a descriptor change, and on
the fixture `tests/fixtures/pilot-supply.json` with its tag model and device model, gate G7 devices
included.

Proven on the gateway on 2026-10-10 and 2026-10-11, in new sessions:

1. The fixture project `cadre_hmi_pilot`: gate G8 on its page (199 components, no overlay, no error
   badge) and gate G11 with its device model (6 of 6 devices, every tab: Control, Trend, Tuning,
   Status, Maintenance, Alarms). The pump whose object error stands on a source tag lists that alarm,
   and only that alarm, in its Alarms tab and shows its alert frame on the page.
2. The writes of W12 to W17, signed in with the test login (GF-56): force on, force off and automatic;
   mask and automatic; a setpoint; manual and automatic; a manual output and its bounds; a tuning
   value. A setpoint field keeps its text across polls.
3. The existing proofs on the changed parent: the water treatment suite on both renderings (gate G8 on 6
   of 6 routes, G11 on 44 of 44 faceplates, G10 with 15 of 15 and 19 of 19 checks signed in), and gates
   G8 and G11 on `cadre_hmi_sample` (5 of 5 devices) and `cadre_hmi_demo` (31 of 31 devices).

Proven offline on 2026-10-11, for section 9.7 and write path W18: 123 unit tests; the parent build
with gate G1 clean over 37 views; gates G0 to G7 on `cadre_hmi_wtp`, `cadre_hmi_wtpob` and
`cadre_hmi_sample`, whose tracked files are byte identical to those of 2026-10-10; and gates G0 to G7
on the fixture with its sequence (7 devices, 8 device symbols). The validator of the Ignition-Wiki
reads the top level of a component's props, so gate G1 now also walks the levels below it against
the registry (`gates._deep_findings`): an enumerated value such as the `interpolation` and the
`type` of `plots[].trends[]`, a key of a closed object, and a bound path. It does not read the
values an expression may answer (the card's interpolation) nor a key of an object the registry
leaves open (a column's `key`), so a unit test checks `curveStepAfter`, the card's expression, the
column and `LastValue` against the registry and the built views. Nothing of section 9.7 had run on
the gateway by then.

Proven on 2026-10-11 for the changes that the first plant page asked for (page 06 sections 2, 4.1 and
4.2, page 08 sections 3.2 and 5): 180 unit tests; the parent build with gate G1 clean over 37 views;
gates G0 to G7 on `cadre_hmi_wtp`, `cadre_hmi_wtpob`, `cadre_hmi_sample` and the fixture (7 devices,
8 device symbols), with no warning on any of them. On the gateway, in new sessions after the parent
and every child were imported again: gate G8 on every route of `cadre_hmi_wtp`, `cadre_hmi_wtpob`,
`cadre_hmi_sample`, `cadre_hmi_demo` and `cadre_hmi_pilot` (20 of 20 routes, no overlay, no error
badge; the fixture's page has 224 components), and gate G11 on the fixture with its device model
(7 of 7 devices, 9 leaf views) and on `cadre_hmi_sample` (5 of 5 devices). The sequence's block and
its faceplate were on the glass for the first time: the block shows the identifier, the text of the
step and "Step 1"; the faceplate shows the tabs Status, Trend and Alarms, the text of the step, the
step number, the fault as Normal and the button "Start cycle" under Commands, and its trend draws the
step number. The faceplate header shows an identifier of 16 characters whole. The tracked files of
`cadre_hmi_sample` are byte identical to those of 2026-10-10; of `cadre_hmi_wtp` the intake page
changed (two pipes now end at the tile of its static tank) and the overview (its rows), and of
`cadre_hmi_wtpob` the overview.

A review of the same day asked for more, and it was built and proven that day (page 06 section 2,
page 08 sections 3 and 5): the generator grows a readout whose box is too small for what it shows,
widens an embed for its identifier only into the room the next symbol leaves, and notes the capacity
line that the module's tank draws for a static tank without a capacity; gate G5 names an identifier
that ends in an ellipsis under a symbol, in a readout and in a tank; and the profile gained `grows`,
`identifier.share` of the tank and `diagram.overlap`. Proven: 183 unit tests; the parent build with
gate G1 clean over 37 views; gates G0 to G7 on `cadre_hmi_wtp`, `cadre_hmi_wtpob`, `cadre_hmi_sample`
and the fixture with no warning, every built file of theirs and of the parent byte identical to the
one before the round. On the gateway, in new sessions after the parent and every child were imported
again: gate G8 on every route of `cadre_hmi_wtp`, `cadre_hmi_wtpob`, `cadre_hmi_sample`,
`cadre_hmi_demo` and `cadre_hmi_pilot` (20 of 20 routes, no overlay, no error badge; the fixture's
page has 224 components), and gate G11 on the fixture with its device model
(7 of 7 devices, 9 leaf views) and on `cadre_hmi_sample` (5 of 5 devices). A scratch variant of the
fixture page, built for the look and never tracked, showed the three on the glass: two readouts given
72 by 24 px were drawn 130 by 40 px with their value and their identifier whole; three lamps 80 px
apart kept their embeds apart, the two identifiers of 14 characters ending in an ellipsis; and a live
tank 110 px wide ended its identifier of 16 characters in an ellipsis, as gate G5 had warned.

Not yet proven on the gateway:

1. The refusal of W12 to W17 with nobody signed in, and a walk that gate G10 runs for the new kinds:
   the generated operator walk of the rebuild programme covers both (COB-088).
2. The module list and the alarm menu over several source patterns, and a row of the alarm menu that
   opens the device of an alarm on a source tag. The stock table and the tab's count are proven by
   item 1 above.
3. A device that carries both interlocks and maintenance members: four tabs in the 368 px tab row.
4. A controller whose trend index lists only some of `value`, `sp` and `out`: the fixture's controller
   historises all three, and its Trend tab passed gate G11 with no overlay.
5. The sequence of section 9.7: a pulse signed in and its refusal with nobody signed in; the stepped
   line through a cycle, and the aggregate `LastValue` on a path object of a tag history binding. Its
   block, its faceplate with every tab and the caption on the button passed gates G8 and G11 on
   2026-10-11, and the fixture's expression model answers on the gateway (the step reads 1 and its
   text "Standby").
6. The proofs of 2026-10-10 on the parent as it now is. Every view that holds `custom.can` gained
   W18, every faceplate's `custom.dev` gained `pulses`, `Trend/Card` gained a binding on the
   interpolation of its line, and `cadre.hmi` changed: the parent and every child are to be imported
   again and gates G8, G10 and G11 run again in new sessions (GF-10).

## 10. Ownership by Mode and the Faceplate Style

### 10.1 Ownership by Mode

1. A device model may give a device its `modes`: each value of the member `mode`, its name and its
   owner, one of `program`, `operator`, `maintenance` and `local` (COBD-044, finding F005 option B of
   the ASMP study).
2. The checked writes refuse a command on a gated path (W1, W3, W5, W16, W17, W18 and, since the
   configuration rows of section 10.4, W19) that the owner does not allow, and say why. The operator may
   start and stop, set the speed, reset a fault and pulse; maintenance may also force, mask and set a
   configuration row; the program and the local station allow none of them (`ownership` of the profile,
   page 17 Table 14).
3. `cadre.hmi.device_read` answers who holds the device (`owned`, `owner`, `allowed`, `reason`) and
   the moves it offers: Take control, to the first mode of the operator, from the program or
   maintenance; Release, to the first mode of the program; and Maintenance, from the operator.
4. The pump and valve faceplates show the owner and the reason a command is disabled, and offer the
   moves behind a Confirm row. Confirm makes one W2 write, which the checked write refuses again if
   the mode is no longer one the operator may choose; a new device clears a pending move.
5. Gate G7 devices requires the member `mode` as a whole number, unique values and names and known
   owners, and warns of a device with no mode of the operator. A device without modes keeps the rules
   of its write paths alone.

### 10.2 The Faceplate Style

1. A device's faceplate has a style (COBD-045): `openbridge`, the faceplates of sections 2 to 9 and
   the default, or `asm`, the anatomy of the ASMP study (ASMP-REPORT-01 section 5.2). The device model
   gives a device its style (`faceplate`), and `screen.py --faceplate` gives the project's default
   (`session.custom.faceplateStyle`).
2. `cadre.hmi.select_device` writes `session.custom.selectedStyle` before the device, and the dock
   chooses the view by the selected kind and style (`framework.FACEPLATE_OF_SELECTION`). Pumps, motors
   and fans open `Faceplate/ASM/Pump`; valves, analogue valves and dampers open `Faceplate/ASM/Valve`.
   Every other kind opens its `openbridge` faceplate in either style, and gate G7 devices warns of a
   device that asks for `asm` there (the generator, the sequence and the instrument gained asm faceplates in section 12).
3. Table 1 gives the anatomy of an `asm` faceplate.

Table 1. The `asm` faceplate

| Part | Content | Shown |
|---|---|---|
| Header strip | The state; the mode or the owner; the words Fault and Interlocked; the count of the device's alarms | Each word while its member or condition holds |
| Home | The rows of the `openbridge` Control tab: status, commands, ownership and its Confirm, the speed setpoint, the fault reset | Always |
| Config | The maintenance functions of section 9.6 (force, object error mask, flags); the configuration rows of COB-139 join them | For a device with a maintenance member |
| Diagnostics | The raw value of every member the faceplate reads, in the groups Status, Command and Maintenance | Always; each row while its member exists |
| Alarms | `Faceplate/Alarms`, as in section 3 | Always |
| Interlock | The interlock pane of section 7 | For a device with interlocks |
| Info | Name, description, kind, tag folder, owner and the source patterns of the device's alarms | Always |

4. The source's faceplate is a 450 by 600 px popup with a rail of six tabs. In the 400 px dock the six
   tabs take two lines of three (`wrap` of the tab row, Ignition-Wiki `ia.container.flex`), so that the
   panes keep the width of the `openbridge` faceplate and its setpoint rows.
5. Gate G7 faceplates checks both `asm` views as it checks the others. Gate G11
   (`faceplates.device_expectations`) and the plan of the operator's walk (`walk_plan.build_plan`,
   `walk.py plan --faceplate`) expect the tabs of the style the device opens, and the plan names a
   step's tab as that style shows it: Home for Control, Config for Maintenance, Interlock for
   Interlocks.

### 10.3 The Pin

1. A faceplate opens in the right dock, the default, or in a floating popup (COBD-045). The session
   keeps the place in `session.custom.faceplateMode` (`dock` or `popup`), and `screen.py
   --faceplate-mode` gives the project's default.
2. Every opener of a faceplate (the symbols, the module's embedded symbols, the alarm menu's rows and
   the trend cards' titles) ends with the lines of `library.open_faceplate`, after
   `cadre.hmi.select_device`: `system.perspective.openPopup` with the popup's identifier while the
   mode is `popup`, else `system.perspective.openDock` (IGW:23-perspective-scripting sections 4 and 7).
3. The dock's header carries Float, which sets the mode to `popup`, closes the dock and opens the
   popup. The popup's bar carries Dock, which sets the mode to `dock`, closes the popup and opens the
   dock. The choice holds for the session, so the next device opens in the same place.
4. The popup is `Framework/FaceplatePopup`, 450 by 600 px, the size of the source's faceplate. Its
   title bar is the popup's own (the identifier, the close icon, the drag), opened with
   `position` naming the top and right sides only; beneath it a bar with the description and Dock,
   then the faceplate of the selected kind and style at its 720 px height in a body that scrolls. The
   size a popup takes from its view, and a second `openPopup` of the same identifier while the popup
   is open, are to be measured in the combined gateway run.
5. The faceplate sweep (G11) and the operator's walk (G10) read the right dock; a project built with
   `--faceplate-mode popup` is proven by the combined run's own check of the pin.

### 10.4 The Config Rows

1. A device model may mark a member `config` (finding F010 of the ASMP study, COBD-045): a number under
   the device's subfolder `cfg/`, with its caption (1 to 24 characters), unit, minimum, maximum and
   format. The device index carries the device's rows as `config`.
2. The rows head the Maintenance tab of the `openbridge` pump, valve and digital input faceplates, and
   the Config tab of an `asm` faceplate: a section CONFIGURATION and one `Faceplate/SetpointRow` per
   member (`cadre.hmi.config_rows`), the repeater as high as its rows (`dev.config`, the count
   `device_read` answers). The tab shows for a device with a maintenance row or a configuration row.
3. Write path W19 (`cadre.hmi.configure`, the Administrator role of COBD-024) writes a member the
   device's entry marks `config`, a number within the bounds the model gives, through the checked
   writes: the device model's write list and the owner apply. Of the owners only maintenance allows
   W19 (`OWNER_PATHS`), so a device with modes takes a configuration change in its maintenance mode; a
   device without modes takes it at any time. The setpoint row calls `command` with W19, which hands the
   value to `configure`.
4. Gate G7 devices requires a configuration member under `cfg/`, marked `config`, of a numeric type, on
   a kind whose faceplate draws the rows (`config` of the profile's kind), with a caption that is one
   line and not the label of a tab, and its minimum not above its maximum; it warns of a member without
   bounds. Gate G7 commands follows W19 through the row's `case` over its write path.
5. A Boolean configuration member (an enable) has no row yet: the setpoint row is a numeric entry
   field, and gate G7 refuses the type.

### 10.5 Confirmation

1. A command that changes the state of the process, and a setpoint, is written only once the operator
   confirms it, in both faceplate styles (finding F029 of the ASMP study, COBD-045). Acknowledgement
   is not confirmed.
2. A command button asks and writes nothing: it sets `custom.pending` (the device, the write path,
   the member, the value and the question, the button's caption and the device's identifier). The
   paths asked so are W1 (start, stop, open, close), W2 (the mode, the moves of ownership included),
   W5 (fault reset), W11 (interlock reset), W13 (loop mode), W16 (force), W17 (object error mask) and
   W18 (pulse); a start an interlock holds asks nothing and shows why, as before.
3. The Confirm row sits beneath the tabs on every tab of every faceplate, shown while a command is
   pending for the faceplate's device. Confirm makes the one checked write, `cadre.hmi.command` with
   the pending path, which hands W11, W16, W17 and W18 to their own functions (a pulse through it
   takes only true); its `enabled` is a `case` over the pending path, each path to its own
   permission, which gate G7 commands reads. Cancel clears the question, and a new device clears it.
4. A row's field (a setpoint of W3, W12, W14 or W15, an alarm limit of W4, a configuration value of
   W19) holds the value typed (`custom.typed`, `custom.pending`) and writes nothing. Set makes the
   checked write and, on a refusal, puts the tag's value back; the cancel button puts it back
   (`self.getSibling`, IGW:21-scripting-contexts). A row handed another device or member clears it.
5. A bypass, or its removal (W10), waits for the Confirm of its own interlock row, and Cancel beside
   it.
6. The glass presses a command as an operator does: `glass.button` and `glass.dock_button` hand back a
   press that cancels a question still open, presses the button and answers the Confirm it raises;
   `glass.type_into` presses the row's Set. Gate G10 and the generated walk therefore run unchanged.
   The refusal step's crafted client calls the Confirm's handler, or the Set's, after the button's or
   the field's, so that the gateway answers the write (GF-59). The captions are pinned together in
   `framework`, `glass` and the walk's glass table.

The same row asks before Ack all on an alarm list ("Acknowledge N alarms?", Confirm and Cancel; page 04 section 8.12).

### 10.6 Status of This Section

Proven offline on 2026-10-23: 344 unit tests; the parent build with gate G1 clean over 40 views;
gates G0 to G7 on the fixture built with `--faceplate asm --faceplate-mode popup --render module`
(7 devices, 8 device symbols); and gates G0 to G7 on both renderings of the water treatment sample. Nothing of
this section has run on the gateway; the combined gateway run (COB-143) is to prove it. Open items:

1. The combined gateway run is to measure the confirmation on the glass: the Confirm row's answer
   after a press, a row's Set and cancel, the bypass's Confirm, and the crafted calls of the refusal
   steps.
2. Gate G11 and the glass helpers find a tab by its label among every button of the dock. The move
   Maintenance of a device with modes carries the label of the `openbridge` Maintenance tab, so the
   search is to be narrowed to the tab row before the combined run proves a device with modes.

## 11. Alarms of the ASMP Build

This section records work package C of the ASMP build (COB-140, COBD-044): the alarm features the
study's catalogue selected, built and tested offline on 2026-10-23.

### 11.1 Priority Colours

The five priorities map onto the four Cadre alert colours by rank (F053): Critical the critical colour,
High alarm, Medium warning, Low caution, and Diagnostic none (`cadre.hmi.PRIORITY_STATUS`). The module's
Package alert levels already colour so (`level-critical` on the critical colour, `level-high` on
alarm), and the frame follows the same table: the top bar's colour (`framework.PRIORITY_VAR`), the
library symbols' frame and flap (the status `critical`, drawn with the alarm's triangle), and the
classes `cadre/alert/flash-critical` and `cadre/alert/badge-critical`.
The alert button and its item take the same mapping in their `alertType` property (wiki 12 section 17.24.1): the empty value is
Diagnostic, which has no alert colour.

### 11.2 A Symbol's Alarm State

A device symbol whose descriptor binds and states none of `alert`, `alertFrameStatus` and
`alertFrameMode` follows its device's own alarms (F016). Each such symbol takes a key in the page's
`custom.alerts`, which one binding polls every 2 s for the whole page through
`cadre.hmi.alert_states`: one alarm query over every device's source patterns, then each event matched
to its device. The state shown is that of the most severe unacknowledged active alarm, else of the
most severe active one, else of the most severe cleared and unacknowledged one, with the mode
`unacked-active`, `acked-active` or `unacked-rectified`. A library symbol draws a frame for an alarm
of a priority with an alert colour; a module component takes the package's level, Diagnostic included.
A symbol that binds its alert to a member keeps it: the pumps of the water treatment sample do.

### 11.3 The Alarm Form

`tools/hmi/alarms.py` writes an alarm of a tag model in one form, and the library profile states it
under `alarms` for a tool that does not import the module:

1. the label `<identifier> <text>` (F042);
2. the display path `<node>/<identifier>`, the node being that of the deepest page that draws the
   device (`screen.node` of the descriptor, `screen.device_nodes`; page 08 section 3);
3. one of the five priorities, a report of a state taking Diagnostic (F043);
4. `shelvingAllowed` true for every priority but Critical (F045);
5. `setpointA` bound to the limit member, and `timeOnDelaySeconds` to the limit's delay member where
   the device carries one (F028).

The water treatment sample takes the form: its alarms' display paths name their area
(`WTP/Filtration/AIT-301`), and AIT-301's high turbidity alarm follows its delay `hiLimitDelay`, 0 s at
the start.

### 11.4 Delays and Shelving

A limit's delay is the member `<limit>Delay` in seconds, 0 to 3600 (F028). W4 writes it as it writes
the limit, and the faceplates that list limits (instrument, tank, controller) list the delays beneath
them, one setpoint row each (`cadre.hmi.delay_rows`), behind the row's Set (section 10.5).

The library's alarm status tables (the faceplate's, the alarm menu's and the alerts page's) offer only
the shelving times of `alarms.SHELVE_SECONDS`, 5 minutes to 8 hours (`shelvingTimes`, IGW
ia.display.alarmstatustable), so no alarm is shelved without an end (F045). Suppression by design and
out of service are not built: the owner's decision is that each is proved on the gateway first, and
probe E9 (section 11.6) measures them.

### 11.5 The Controller Acknowledgement Bit

A device whose device model lists `alarmAck` (Boolean, `write`) is told of an acknowledgement of one of
its alarms made through `cadre.hmi` (F049): the top bar's ACK (W6) and the module's alarm menu (W8, W9)
write true to it through the checked writes, under the acknowledgement's path, and the controller
returns it to false. A device without the member, the default, is told nothing, and an acknowledgement
the gateway refuses relays nothing. The stock alarm table acknowledges by itself (W7, GF-40), so an
acknowledgement made there is not relayed. The profile states the relay under `ackRelay`.

### 11.6 The Alarm Test Device and Probe E9

The pilot fixture carries TST-1 (F059): a Boolean `state`, clear at the start, with one alarm of each
priority, Diagnostic included, and the acknowledgement bit. A gate that raises it sees every alert type
on the glass; the build never raises it, so the generated walk keeps its own top alarm.

Probe E9 (`tools/experiments/e9_asmp_probe.py`) holds the measurements the combined gateway run makes
first (COB-143): whether an alarmed folder carries alarm metrics (ASMP-009, the DR1 lead's names), the
on-delay bound by expression, suppression by an `enabled` bound to a member, out of service by
`alarmEvalEnabled`, `system.alarm.shelve` on an alarm whose `shelvingAllowed` is false, and the
candidate bit operators of the expression language (F001, F003).

### 11.7 Status of This Section

Proven offline on 2026-10-23: 357 unit tests; the parent build with gate G1 clean; gates G0 to G7 on the
fixture with its device model (8 devices, 9 device symbols, no warning) and on both renderings of the
water treatment sample; the probe project's view clean under gate G1. Nothing of this section has run
on the gateway. The combined run is to measure the on-delay binding, the derived symbol states, the
critical colour on the glass, TST-1's five alert types, the relay to TST-1's bit, and to run probe E9.

## 12. The Generator and the ASM Faceplates of the Sequence and the Instrument

This section records work package A of the eng02 library build (COB-158, branch `eng02/asm-lib-dev`, 2026-10-23): the
gaps GG-01, GM-07 and GX-01 of the ASM reimagining of the proving slice. It is built and tested offline (the unit tests of
`tests/test_asm_devices.py`, gates G0 to G7 on its sample and on the eng02 set); nothing of it has run on the gateway.
Code: `tools/hmi/devices_asm.py` (the member tables and the three faceplates), `tools/hmi/library.py` (the symbols),
`tools/hmi/framework.py` (`_tabbed`), `tools/hmi/scripts.py` (`select_device`, `tab_shown`).

### 12.1 The Generator Kind

A device of kind `generator` is an engine driven set: a run state, a run sequence word, a control switch word, an active
fault, and the commands Start, Stop and Reset. Table 13 gives its members; every one is optional on a device, and the
core members (the first seven) are those a generated tag model creates.

Table 13. Members of a generator.

| Member | Type | Meaning | Written by |
|---|---|---|---|
| `state` | Boolean | Running | Not written |
| `runText` | String | The run sequence word (Ready, Starting, Running), computed in the tag model | Not written |
| `switchText` | String | The control switch word (Auto, Manual, Off), computed in the tag model | Not written |
| `faultCode` | Int4 | The active fault code, 0 for none | Not written |
| `cmdStart`, `cmdStop`, `cmdReset` | Boolean | Pulse commands (section 12.5) | The pulse button, W18 |
| `fault` | Boolean | A fault flag where the source has no code | Not written |
| `engineSpeed` | Float8 | Engine speed, rpm | Not written |
| `voltageLL` | Float8 | Average line to line voltage, V | Not written |
| `fuelLevel`, `fuelLowLimit` | Float8 | Fuel level and its low limit, per cent | Not written |
| `startDelay`, `stopDelay`, `timeLeft` | Float8 | The delays in seconds and the time left in minutes | Not written |
| `runHours` | Float8 | Total run hours | Not written |
| `startsToday`, `startsYesterday` | Int4 | Starts of the day and of the day before | Not written |
| `serviceHours` | Float8 | Hours since the last service | Not written |
| `cmdServiceDone` | Boolean | The pulse command Service completed | The pulse button, W18 |
| `oilPressureOk`, `readyToRun`, `genComm`, `plcComm` | Boolean | The readiness flags of the Diagnostics tab | Not written |

A generator has no interlock (the Interlock tab is hidden unless a device model lists `ilk` members, which the profile
refuses for the kind), carries the maintenance members of `mnt/` and the controller acknowledgement bit like any device,
and its trend index names `engineSpeed` and `fuelLevel` (`screen.TREND_KINDS`, `TREND_ALSO`). The generator has the asm
faceplate only, and either style opens it (`framework.FACEPLATE_VIEW`).

### 12.2 The Symbol and the Generator Set

1. **The symbol.** `Automation/Generator` is an automation symbol in the two tone style of the pin's device symbols: a
   circle with a G, the body in the device's primary colour while running and in the inverted pair while stopped. The pin
   (Apache-2.0, commit `2c98dda1`) has an icon `generator`, a G beside a lightning bolt, which is converted to
   `library/icons/generator.json` with `tools/convert_icons.py` for use as a navigation icon; it has no running and stopped
   pair, so the two forms, `generator-on` and `generator-off`, are drawn in `library.py` from primitives (a stroked arc
   for the G). The symbol takes the alarm frame of F016 (section 11.2) and the click that opens its faceplate; it passes
   the medium (`PASS_KINDS`) and its status row reads On or Off like the others. Under `--render module` the plain symbol is drawn by the module's
   `cadre.ob.generator` (wiki page 12 section 17.11), which carries the state, the identifier, the status word, the alarm frame
   of section 11.2 and the click; a symbol that asks for what that disc lacks (another variant, the activated ground, a
   progress ring, a badge, the duty or out of service mark) and the generator set keep this stock view.
2. **The generator set.** A descriptor symbol of kind `generator` with `params.picture` set to `genset` is drawn by
   `Automation/GeneratorSet` (gap GG-01): a vector drawing of our own, an engine block with three cylinder heads and an
   exhaust, a coupling and an alternator with its terminal box and louvres, on a base frame, 240 by 150 px by default. It
   is running or stopped through the parameter `on`, which the generator's state binds, writes Running or Stopped beneath
   its identifier, carries the alarm frame around its whole box and opens the generator faceplate on a click. Its contract
   anchors at the box (`anchor` `box`), so the descriptor's box is used as given; `screen.view_of` chooses the view from
   the kind and the picture.

### 12.3 The Generator Faceplate

`Faceplate/ASM/Generator` has the six tabs of the asm anatomy (Table 1), on `framework._tabbed`. Table 14 gives their
content. The Home tab scrolls: its rows and the trend are more than the faceplate's height holds.

Table 14. The tabs of the generator faceplate.

| Tab | Content | Shown |
|---|---|---|
| Header strip | The state (Running or Stopped), the run sequence word, the control switch word, Fault, the count of the alarms | Each word while its member holds |
| Home | Status (run sequence, control switch, active fault); Commands Start, Stop and Reset; Engine and output; Timing (start delay, stop delay, time left); Fuel (level, low limit, and the place of the range bar); Totals (run hours, starts today and yesterday); the trend of engine speed and fuel level | Always; each row while its member exists |
| Config | Service (hours since the last service, Service completed), then the configuration rows of section 10.4 and the maintenance functions | For a device with service data, a configuration row or a maintenance row |
| Diagnostics | The raw values in the groups Status, Readiness, Measurements, Totals and Command | Always; each row while its member exists |
| Alarms | `Faceplate/Alarms` as in section 3 | Always |
| Interlock | The interlock pane of section 7 | For a device with interlocks |
| Info | As Table 1 | Always |

1. **Commands.** Start, Stop and Reset are pulse buttons (section 12.5). Each asks first (the Confirm row of section 10.5),
   shows only while its member may be written, is enabled by the permission of W18 (the Administrator role) and by the
   owner of the device where it has modes, and reads selected as the state of the generator says (Start while running).
   Service completed on the Config tab asks first as well.
2. **The fuel level.** The row turns to the alarm badge while the level is under the low limit. The range bar of the fuel
   level (`Parts/RangeBar`, with the low limit marked) is the work of COB-159: its place in `faceplate_generator` is
   marked in the source with `# COB-159 bar here`.
3. **The trend.** Engine speed on the value axis and the fuel level on the percent axis of the chart of section 8, each
   drawn where the trend index lists its member (`cadre.hmi.trended`, `trend_tags`).

### 12.4 The Sequence and the Instrument

1. **`Faceplate/ASM/Sequence`** (gap GM-07). Home: the step text, the step number, the state rows In service, Enabled,
   Prerequisites met (from the interlock contract, shown for a device with `ilk` members), Sequence normal and Fault; the
   commands In service and Out of service, Enable and Disable, and the sequence's own pulse (`trigger`), each shown where
   the device may be written at the member, each asking first. Config: the run time setpoint as a W19 row (a member
   `cfg/runTimeSP` the device model marks `config`, section 10.4) and the maintenance functions. Diagnostics: the members of
   the state and the prerequisite. Interlock: the prerequisite as a permissive of the library's contract
   (`ilk/C01/kind` `permissive`), with its live and required text. The header strip shows the step text, Out of service and
   Disabled while they hold, Fault, Interlocked or Not permitted, and the alarm count. New members: `inService`, `enabled`,
   `normal` (Boolean) and the pulse members `cmdInService`, `cmdOutOfService`, `cmdEnable` and `cmdDisable`. The stock
   faceplate of the sequence (section 9.7) is unchanged and still opens in that style.
2. **`Faceplate/ASM/Instrument`** (readouts, instrument fields and instruments). Home: the value with its unit, the remote
   auto state, the alarm limits and their delays that the device carries (sections 8 and 11.4), the place of the range bar
   (`# COB-159 bar here`: minimum `rangeLo`, maximum `rangeHi`) and the trend. Diagnostics: the value, the remote auto
   state, the range and the flags. Alarms and Info as Table 1; Config shows only for a device with maintenance or
   configuration rows. New optional members: `remoteAuto`, `oos`, `badValue`, `ioFault`, `overRange`, `underRange`
   (Boolean), `rangeLo` and `rangeHi` (Float8). The header strip shows the remote auto state, Out of service, Bad value,
   I/O fault and the range flags while they hold.
3. **Which faceplate a device opens.** In the asm style the sequence, the instrument and the generator open these views
   (`framework.ASM_VIEW`, `FACEPLATE_OF_SELECTION`); this changes section 10.2 item 2, which gave only the pumps and the
   valves an asm view. A kind with no asm view keeps its stock faceplate, and gate G7 devices still warns of a device
   that asks for `asm` there.

### 12.5 The Pulse Commands

The pulse path W18 (section 9.7 item 3) gained members. Table 15 gives them with the caption a button shows where the
device model gives none. Nothing else of the path changed: the Administrator role, a device in the session's index that
carries the member, the device model's write list, the owner by mode (the operator's mode allows W18), and the value true
only. A device model marks each pulse member `pulse` and `write`, and may give it a `caption` (section 9.7 item 4).

Table 15. The pulse members.

| Member | Kind | Default caption |
|---|---|---|
| `trigger` | sequence | Start |
| `cmdStart`, `cmdStop`, `cmdReset`, `cmdServiceDone` | generator | Start, Stop, Reset, Service completed |
| `cmdInService`, `cmdOutOfService`, `cmdEnable`, `cmdDisable` | sequence (asm faceplate) | In service, Out of service, Enable, Disable |

The stock faceplate of the sequence still draws a button for `trigger` alone and, with no caption, names it by the
member. The walk's plan names a button as the faceplate draws it (`walk_plan`, `devices_asm.CAPTIONS`).

### 12.6 Opening on a Named Tab

1. Every faceplate view built by `framework._tabbed` (the seven stock faceplates and the five asm ones) takes the input
   parameter `tab`; `Faceplate/Empty` takes it and ignores it. On a change of `params.deviceId` the view sets its tab to
   the first and then to `params.tab` where that is one of its tabs; on a change of `params.tab` it sets the tab asked for,
   else the first. The check is of the faceplate's own tab keys, which `framework._tab_lines` writes into both scripts.
2. The dock's faceplate (and the popup's) binds `params.tab` to `session.custom.selectedTab`.
3. `cadre.hmi.select_device(session, device_id, kind, title, label, tab)` writes `selectedTab` last. A plain symbol click
   passes none, so it clears the tab and the faceplate opens on its first. A tab the device does not show (`tab_shown`:
   Interlock for a device without `ilk` members; Config or Maintenance for one without a maintenance row, a configuration
   row or, for Config, service data) is cleared too, so the faceplate opens on its first tab. The scripts of the view
   cannot ask the device, and a tab key the faceplate lacks is refused by the view.
4. `library.open_device(device, kind, title, label, tab)` keeps its signature and passes the tab through `select_device`.

### 12.7 The Device Model and the Descriptor

A generator in a device model (`cadre-hmi-devices/1`), with names that stand for a plant:

```json
{"id": "GEN1", "kind": "generator", "title": "GEN-1", "label": "Standby generator",
 "members": {
  "state": {"type": "Boolean", "access": "read"},
  "runText": {"type": "String", "access": "read"},
  "switchText": {"type": "String", "access": "read"},
  "faultCode": {"type": "Int4", "access": "read"},
  "cmdStart": {"type": "Boolean", "access": "write", "pulse": true, "caption": "Start generator"},
  "cmdStop": {"type": "Boolean", "access": "write", "pulse": true, "caption": "Stop generator"},
  "cmdReset": {"type": "Boolean", "access": "write", "pulse": true, "caption": "Reset generator"},
  "engineSpeed": {"type": "Float8", "access": "read"}, "fuelLevel": {"type": "Float8", "access": "read"},
  "fuelLowLimit": {"type": "Float8", "access": "read"}, "serviceHours": {"type": "Float8", "access": "read"},
  "cmdServiceDone": {"type": "Boolean", "access": "write", "pulse": true, "caption": "Service done"}},
 "trend": ["engineSpeed", "fuelLevel"]}
```

and its two symbols in a descriptor, the symbol and the set:

```json
{"id": "GEN1", "kind": "generator", "x": 100, "y": 120, "w": 48, "h": 48, "device": true, "label": "Standby generator",
 "params": {"readoutPosition": "bottom", "hasTag": true, "tag": "GEN-1"}, "bind": {"on": "GEN1/state"}}
{"id": "GEN1", "kind": "generator", "x": 400, "y": 100, "w": 240, "h": 150, "device": true, "label": "Standby generator",
 "params": {"picture": "genset", "hasTag": true, "tag": "GEN-1"}, "bind": {"on": "GEN1/state"}}
```

A sequence adds `inService`, `enabled`, `normal`, the four pulse members of Table 15, a member `cfg/runTimeSP` with
`"config": {"caption": "Run time alarm", "unit": "min", "minimum": 0, "maximum": 1440, "format": "0"}` and the `ilk/`
members of section 7 (a condition of `kind` `permissive` for the prerequisite). The fixtures
`tests/fixtures/asm-devices.json` and `asm-screen.json` hold one of each kind.

### 12.8 Status of This Section

Proven offline on 2026-10-23: the unit tests of `tests/test_asm_devices.py` (generator tables, profile, symbols,
faceplate views, the tab parameter, the pulse path, the walk's table, the sample), the whole suite, gates G0 to G7 on the
sample under both renderings (4 devices, 4 device symbols, one device with interlocks) and on the eng02 set. Not proven,
because it needs the gateway:

1. The change scripts of the view parameters (`self.params.tab`, `currentValue.value`, `self.custom.tab`) and the
   scripts of `tab_shown` (`device_read` and `interlock_summary` called from `select_device`); the shapes follow the
   `onChange` examples of the Ignition wiki and the existing deviceId script.
2. The scrolling of the Home tab (`overflow` `auto` on a flex pane, as the popup's body) and the 272 px trend block.
3. The two coloured states of the generator set and of the symbol on the glass, and the click on the set.
4. A pulse that the plant does not return to false (the library never writes false), and the owner's refusal text.
5. The sweeps G8, G10 and G11 for the new views: the walk's glass table knows the generator (`walk_plan`), but no run has
   read it on the glass.

### 12.9 Proved on the Gateway (2026-10-24)

The generated walk (wiki page 08 section 9; COB-161) pressed, in the eng02 ASM project signed in with the test login,
the writes that no gate had pressed: Start, Stop, Reset and Service completed of the generator, In service, Out of
service, Enable and Disable of the sequence, the sequence's Config row `cfg/runTimeSP` (W19), and the page command
button of section 5.1 of page 05. Each asked first in the Confirm row (or the button's question) and wrote on Confirm;
each pulse left its stamp and returned its member to false, the run sequence of the generator followed (Ready,
Starting for 5 s, Running), a Config value typed and set was read back and put back, and every refusal with nobody
signed in came from the gateway with the tag unchanged. Two facts follow. The Service completed command stands on the
Config tab, not on Home with Start, Stop and Reset. A value above the row's maximum is stopped by the entry field itself
(its input bounds), so the gateway's own range check (`configure`) is reached by a crafted client alone. Items 4 and 5 of
section 12.8 stay open for what they name: a pulse that a plant never returns, and the sweeps G10 for the other views.

## 13. The Component Test Page

This section records work package D of Level 4 of the eng02 ASM build (items 3, 4, 9, 10 and 11 of the owner's list of
2026-10-24). Everything in it is built and tested offline; section 13.8 lists what only the glass or the gateway can prove.

### 13.1 Purpose

A page that shows every library component with the features to test, so that a person checks a library change, a module
release or a migration on one page, not by hunting for the screen that happens to use a feature. It is not written by hand
for a project: `tools/hmi/testbench.py` generates it from the library's own catalogue, `library/contracts.json` (the views,
their kinds, parameters, defaults, state, status mode and size) and `library/profile.json` (the kinds, their embed boxes, the
device kinds with their members, pulses and binding rules, the faceplates and their tabs, the ownership by mode, the alarm
priorities). A parameter a case sets is checked against the contract of its view (`testbench.check`), so a library that gains a
parameter or a kind changes the page by regenerating it.

### 13.2 What the Page Shows

The page is a diagram of labelled sections, with the toolbar, for the route `/component-test`, the navigation label
`Tools: Component test` and the display level `Level 4 support`; it belongs to no node of the plant hierarchy. It is
generated at 1580 px wide and as high as its content needs; the canvas scrolls.

| Section | Content |
|---|---|
| About this page | The way to read the page and the toolbar toggles |
| Indicator: colour by state | A Boolean lamp, a lamp of three states (0 off, 1 on, 2 alarm), a string-state lamp and a lamp painted by two CSS colours, each on a tag of its own, and the buttons that set the tags for a minute (Level 5) |
| Notification | The alarm frame and flap in every status and every mode, drawn statically on the pump, each cell twice: the symbol as the project draws it (the module's component under the module rendering) beside the same symbol forced onto the library's view (`render` `view`); acknowledged, unacknowledged and cleared. `critical` is the library's alone, so both cells are the library's view |
| Badges and marks | On the pump, module beside view as above: the five control badges, the two interlock badges, command locked, duty, out of service, progress, activated; the module has no duty mark and no out of service greying, so those cells are the library's view twice |
| One section for each kind | Pump, motor, fan, valve, analogue valve, damper, filter, switch, indicator, generator, tank, readout, instrument field, controller and sequence: the state both ways, the speed, the readout on each side, the variants, the vertical form, the ID tag, the status text and its hiding, the marks, and the kind's own values (a tank's levels, trend, static, compact and chart forms; the readout's content and `stretch` forms in equal boxes; the field's sizes, setpoint and alignment) |
| Generator set | The set in boxes of 240 by 150, 320 by 200, 180 by 112 and 440 by 275: it fits the box it is given |
| Colour by medium | A flowing pipe for each of the ten media and for each of the four sizes; the Color toggle paints them |
| Test alarms | A symbol for each of the five priorities with its own alarm (a switch, so that it draws the frame: the lamp draws none), the buttons that raise them, and beside them the alarm panel of the test alarms with Ack selected and Ack all |
| Test devices | A device of each device kind; the pump and the valve in a flowing line; the generator set; the buttons that open each faceplate on its Alarms tab; two plain motors, one that opens the test pump's faceplate and one that opens the faceplate of a motor with a state only, with a button that sets its state |

A case is drawn by the symbol's own view under either rendering. A value the module's component cannot take (the readout
side `none`, the status `critical`) is left to the kinds the module does not draw, and a case the module cannot show is shown
by the library's view (`testbench.module_value_ok`, the enumerations read from `module/components.json`).

### 13.3 Test Devices and Tags

The test devices run on memory tags, and on expression tags that follow their commands, in the folder `_componentTest` of
the project's own tag root. The project's alarm scope therefore covers them (the default source of a device is its folder) and
no plant tag is touched. Each device lists only members the library knows for its kind (gate G7 devices checks it):

1. Switched devices (pump, motor, fan, valve, analogue valve, damper): `cmd` (written from the faceplate), `state` (an
   expression of `cmd` and `fault`), `fault`, `alarmAck`, and for the pump, motor and valve the member `mode` with the modes
   Program, Operator, Maintenance and Local (ownership by mode, section 10.1); the pump and motor also `speedSp` and `speed`.
   The pump has a High alarm on `fault`.
2. The tank, the instrument and the controller: levels, values and limits as memory tags; the instrument's High and Low
   alarms follow its limits, so writing a limit on the faceplate raises or clears them; the controller's output follows its
   setpoint or its manual output.
3. The sequence and the generator: their pulse members, and states that a pulse sets or clears and holds (a self reference,
   GF-16). The Start pulse of the generator makes it run and the Stop pulse stops it.
4. The indicator `TB_IND` and five alarm devices, `ALM_CRITICAL`, `ALM_HIGH`, `ALM_MEDIUM`, `ALM_LOW` and `ALM_DIAGNOSTIC`:
   each is a lamp whose `state` follows its own `raise` tag, or the tag `ALM_ALL/raise`, and carries one tag alarm of its
   priority in the library's one form (`alarms.definition`). The display path is `Component test/<identifier>`.

### 13.4 Buttons

Every button of the page writes a test tag and no other. The pulse buttons use the page command of page 05 section 5.1: they
ask first, then the library's `page_pulse` (write path W18, administrator gated) holds the tag true for 60 s. The page raises
one alarm of each priority, or all five, and sets the pump's fault or the input `TB_IND`. To see the three alarm states on a
lamp: raise it (the frame flashes: active, unacknowledged), acknowledge it on the faceplate Alarms tab or on the alert
banner (steady: active, acknowledged), or let the minute pass without acknowledging (dashed: cleared, unacknowledged). The
faceplate buttons open each device's faceplate on its Alarms tab; a symbol opens the faceplate in the project's mode (dock),
and the pin on the faceplate floats it. Under the module rendering the page also has "Start generator", a pulse button drawn as
the module's `cadre.ob.button` (page 12 section 17.12): it asks first and holds `TB_GEN/cmdStart` true for 60 s through the same
`page_pulse`, and the test generator, whose state latches on that command, then runs.

### 13.5 Adding the Page to a Migration

The page needs the descriptors' tag root and nothing else. With the option `--component-test`, `screen.py` builds the page
from the catalogue, adds it to the descriptor set (tag model `external`, so that the generator writes none of its tags),
adds the test devices to the device model and the test tags to the tag model that the gates read, and writes the tag folder
to `<out>/<project>.component-test-tags.json`:

```
python tools/hmi/screen.py --project <cadre_hmi_x> --descriptor <a.json> --descriptor <b.json> \
    --devices-file <devices.json> --tags-file <tags.json> --alarm-scope '*<tagroot>*' \
    --frame asm --faceplate asm --render module --component-test --out build
```

1. The descriptors share one tag root; the option refuses a set with two.
2. Without `--devices-file` the page is still built, and its devices keep the faceplates' default members; the modes, which
   a device model carries, are then absent. A project that has a device model gains the test devices in it.
3. With `--deploy` the tag folder is imported into the tag root (`deploy.import_tags(provider, <root path>, folder)`), so that
   no other tag of the root is replaced. A build without `--deploy` leaves the file for the person who imports.
4. The navigation entry, the route and the page are those of the table in section 13.2; the support list of the ASM frame
   shows the page under `Tools: Component test`.
5. The page passes gates G0 to G7: the schema, the registry, the references, the view keys, the project, the layout (no
   overlap), the flow, the contract and the faceplate contract; its device symbols are device symbols of the model, so the
   faceplate sweep (G11) opens each.

### 13.6 The Library Changes of the Same Package

1. **Status words and the Readout toggle on the module's symbols.** The toolbar's Readout toggle flips `view.custom.showReadout`.
   The library's view binds `showStatus` to it and shows `On`, `Off` or the speed. A module component showed its own `Off` while
   stopped and nothing while running, and never muted. `screen.embed_module` now binds the component's `showStatus` to the
   toggle on a page with the toolbar, and its `statusText` to the words the library's status row shows (`screen.status_words`:
   `On` or `Off`, and the speed in per cent for a device with a speed). A descriptor that states `statusText` keeps its words.
2. **The duty and out of service marks.** They are parameters of the page parts (`parts.SYMBOL_PARAMS`) that kept a symbol on
   the library's view. For a component whose schema lists them, `module_draws` no longer refuses them, and `embed_module`
   passes them (a bound mark becomes a tag binding of the component's property). The pumps of the eng02 motor control page draw
   as `cadre.ob.pump` once the module has the properties.
3. **The readout's stretch.** `stretch` (default false) is a parameter of the readout contract. The module's readout fills its
   component box when it is true, so readouts of equal boxes show equal widths with aligned values. The library's readout view
   fills its box already, so there it changes nothing.
4. **Each of these is emitted only where the module's schema lists the property** (`screen.module_props` reads
   `module/components.json`, `screen.MODULE_IF_LISTED` names the properties and `screen.module_drop` is the drop in force),
   so that a build is valid before and after the module release that adds them; gate G1 refuses a property a component lacks.
5. **The generator set fits its box.** The view is a percent container: the picture is centred in its share of the box at its
   own proportions (`preserveAspectRatio` `xMidYMid`), the identifier and the state lie beneath it, and the alarm frame follows
   the box. In its 440 by 275 box on the unit page it fills the box, and not its top left corner. The 48 px generator symbol
   keeps its place at the centre of its embed, as every automation symbol does.

### 13.7 Level 5: the Gallery on Tags

Every symbol of the static grids (the ids `S_`, `N_` and `B_`) reads its state and its marks from memory tags (COB-165,
`testbench.galleryize`): `<tagRoot>/_componentTest/gallery/<symbol>/<parameter>`, one tag for each parameter in
`testbench.GALLERY_PARAMS` that the case states (the state, the speed and the value, the trend, the setpoint and the output, the
text and the step, the alert parameters, the badges, the duty, out of service, progress and activated marks), typed Boolean,
Float8 or String and starting at the case's own value. The position of the readout, the variant, the vertical form, the
identifier and the status text stay in the view. The gallery therefore shows today's values until a person writes a tag, and a
tag written in the Designer or a script moves one symbol on either rendering. The page holds about 460 gallery tags for about
250 symbols; the descriptor `Bench.gallery` lists them.

A plain motor, a lamp and the alarm panel use the symbol keys and the part of page 05 section 5.10. The page passes gates G0 to
G7 under both renderings (`tests/test_testbench.py`, `tests/test_l5_page.py`).

### 13.8 Status of This Section

Proven offline on 2026-10-24: the unit tests of `tests/test_testbench.py` (the catalogue coverage, the layout, the tags, the
buttons, the gates under both renderings with the asm frame, the command line), of `tests/test_hmi.py` (the module mapping
with a patched schema) and of `tests/test_asm_devices.py` (the generator set); gates G0 to G7 on the eng02 set with
`--component-test`. Not proven, because it needs the glass or the gateway:

1. The tag import of the test folder and the alarm scope's inclusion of it, and the expression tags that follow the commands.
2. The look of the page: the cells, captions and sections at 1580 px, the generator set in each box, the module's symbols with
   the status words and the mute (they need the module release that adds the properties), and the readouts with `stretch`.
3. The five alarms through the pulses and the acknowledgement, and the three states on the lamps and the banner.
4. The faceplate of each test device in the dock and floating, the mode moves, and the sweeps G10 and G11 over the page.
5. Level 5, which the glass proves: the frame, the flash and the flap of every library view beside the module's pump (the
   thickness, the radius, the flap outside the frame, the status row); the lamps' colours by their tags; the plain motors opening the test
   pump's faceplate and the state-only faceplate; the gallery's tags moving the symbols; and Ack selected and Ack all on the
   alarm panel, the pages and the menu, with the stock table's `selection` and `filters.active.results` rows.

### 13.9 The Test Page Built Alone

`screen.py --component-test --tag-root [provider]folder` builds the component test page without any descriptor: the page, its
test devices and its tags come from the catalogue and the tag root alone. `--write-descriptor DIR` writes the page's
descriptor as `DIR/component-test.json` and `--write-devices FILE` the device model of the build (the test devices
beside those of a given `--devices-file`), which gate G11 and the walk read. `--descriptor` stays required for every build
that does not name both `--component-test` and `--tag-root`, and a build that gives descriptors is unchanged.
`capture.py` and `faceplates.py` take `--viewport WIDTHxHEIGHT`; the defaults (1600 by 900 and 2700 by `--height`) are the
values they had.

### 13.10 The Glass Gates: `tools/compare/glass_gates.py`

The generalised Level 4 and Level 5 gates of the eng02 slice, in Python Playwright under ctig's `.venv`: `search`, `zoom`,
`menus`, `panels`, `readouts`, `colour`, `sizes`, `fill`, `routes`, `alarm`, `ack` and `banner`. The command writes
`plan.json` first, before any input (the search terms, the routes, the zoom steps, the alarm's tag and values, the
columns, the banner rule), then `gates.json` (`cadre-hmi-glass-gates/1`) and `pictures/`.

1. Input is real: mouse clicks, key events, the wheel, a pinch through `Input.synthesizePinchGesture`, and a reload after a
   dock. No gate sets a value or fires an event from script. The frame's rectangles are recorded before and after each zoom
   and must be equal.
2. One alarm is raised, only when `--raise-alarm` is given (the simulation is on): the memory tag its condition reads,
   under the allowed roots, written and put back through `walk_run.Tags` over ctig's `Gateway` class (the walk's lane).
   `alarm`, `ack` and `banner` are skipped, and said so, without it. The test login reaches the `ack` gate through
   `CADRE_TEST_LOGIN` and is never printed or written.
3. A step may be accepted by a list of rows of an earlier run (`--accepted-rows`); the step then carries `accepted`.
4. The routes of the plan: without `--design`, every model page, the model's support routes, the navigation table's and the descriptors'; with it (COB-211), the built model pages, the design's page and support routes, every descriptor route and `/alerts`, without repeats. An unbuilt model page is not planned; a route the design names is, though the project lacks it.
5. Exit codes: 0 every gate passes and the tag is restored; 2 otherwise; 1 a fault.

The control flow is proven on a fake gateway's client page (`tests/glass_fake.py`). The selectors and the measures were
lifted from the slice's scripts, which were measured on the glass; two readings of the alert list (the unacknowledged
rows and the state of the Ack selected button) are made from the page's text and attributes and not from its component
stores, and are the first thing the integrated run on the gateway must confirm.

### 13.11 The Glass on the New Frames (`--frame ob`, `--frame obasm`)

Built and tested offline on 2026-11-03 (tranche T2, batch F7; `cloud/FRAME-DESIGN.md` section 4.3). The two new frames (`wiki/04`
sections 10 and 11) draw the head with the module top bar, whose buttons, bell and clock are elements in a shadow root, not
Perspective children, so the positional selectors of the stock and stock ASM frames find nothing in it (G10 on `cadre_hmi_wtpobf`
stopped in `refusal_steps` at `open_alarm_menu`, the bell path `T[0].0:6` not existing). The glass takes a variant for each of those
selectors, chosen by the frame the page shows, and the older frames keep their selectors as they were. Code: `tools/compare/glass.py`,
`functional.py`, `glass_gates.py`; tests `tests/test_walk.py` (`FrameGlassTests`, held to `obframe.py`, `obasm.py` and the pinned elements).
The selectors were measured read only on the deployed samples `cadre_hmi_wtpobf` (`ob`) and `cadre_hmi_wtpoba` (`obasm`), nobody signed in
and nothing written (the trial was reset once, GF-03).

#### 13.11.1 Telling the Frames Apart

`glass.frame_variant(page)` reads the structure of the top dock: `obasm` where it holds the module top bar and a module pivot group or tab
row (the header of section 11, in the DOM whether or not drawn), `ob` where it holds the module top bar alone, `default` otherwise (the
stock and stock ASM frames). The module's elements load after the Perspective components, so a dock with no module bar and no coordinate
container (the older frames' buttons) is waited for, about four seconds, then taken for an older frame; the answer is kept on the page for its
project. `glass_gates.Session.frame()` is the same call, its wait following `--settle`.

#### 13.11.2 The Variants

Table 1. What each helper finds on the older frames and on the new ones.

| Helper | stock and stock ASM (unchanged) | module and module ASM |
|---|---|---|
| Bell, `glass.bell` | `BELL`, the top bar's seventh child `T[0].0:6` | `BELL_OB`: the host's `obc-alert-button` (64 by 48 px) |
| Menu, brilliance, user and apps buttons | first and second coordinate container of the top dock, the third (`by_container`) or the last of three SVG icons (`TOP_ICONS`) | `bar_button`: `obc-icon-button` in the shadow root of `obc-top-bar`, by `aria-label` (Menu, Dimming, User, Apps) |
| Alarm menu rows, `alert_list`, `alert_row`, `press_ack` | `obc-alert-list-page-small`, `LIST_INFO`, `ROW_ACTION` | `obc-alert-menu`, `ALERT_MENU_INFO`, `ALERT_MENU_ROW`: rows are `obc-alert-menu-item` (`data-item-id`, `status`, `title`, `description`); `by` is read from the popup view's `custom.alarms.alerts` |
| Acknowledge controls offered, `enabled_acks` | the visible `ACK` texts of the panel | the drawn and enabled row ACK buttons (the menu draws them disabled without the permission) |
| Alarm menu close, `close_alarm_menu` | the first coordinate container of the popup | the bell pressed again (the popup has no close button) |
| Sign in and Sign out, `_open_user_menu` | the older strategies, the entry a button or text of the popup | `by_bar` (User button), the entry the `obc-button` that carries the caption (the menu prints Sign in as its title too) |
| Navigation entries, `nav_labels`, `navigate_by_menu`, `click_nav_entry` | labels of the dock's repeaters | `obc-navigation-item`, `obc-tree-navigation-item` and group labels (`NAV_LABELS`); the page's item, never a group; a closed group is pressed first (`GROUP_OF`) |
| Palette, `pick_palette` | the label Night | the two `obc-button`s step through Night, Dusk, Day, Bright; pressed until `.value` shows the name |
| Page name, `page_name` | the second label of the top dock | `ob`: the bar's `.page-name`; `obasm`: the header's title, `T[0].0:2:0` |
| Alarm count, `frame_alarm_count` | the bell's text | the first whole number the bell prints in its shadow roots (`BELL_COUNT`) |
| Gates: icons, `Session.icons` | `TOP_ICONS` | `BAR_POINTS`: menu, apps, alert, dimming, user, so that the last three are as the older frames list them |
| Gates: head rectangle, `Session.measure` | `MEASURE` (head 80 to 90 px, which the ob head of 84 px meets) | `MEASURE_OBASM` (head 128 to 136 px, the obasm head of 132) |

#### 13.11.3 The Checks

1. F16 (nobody signed in) keeps its meaning: the strip's ACK, which both new frames keep (`T[0].0:1:2:3` on `ob`), is disabled, the alerts page
   offers no Acknowledge, and the alarm menu offers no acknowledge control: no enabled row ACK, ACK visible disabled, and rows listed.
2. F21 closes the alarm menu by a click outside and by a control of its own (the bell for the new menu, which has no close button), and the
   navigation dock by a click outside and by its header's close button, found where the Menu button opens it.
3. F6 and F9 press the Menu and Dimming buttons and the entry or palette through the variants; F11, F14 and F18 take the menu's rows and ACK
   through `alert_list`, `press_ack` and the store's `by`.
4. `glass_gates`: `menus` (user, brilliance and alert menus by the bar's points; the crumb popup step on `obasm` only, the `ob` crumb opening
   its node's page), `alarm` and `ack` (the bell's count, the Sign in entry), `banner` (on `obasm` the ASM banner dock; on `ob` the text of the
   strip and the alert menu, the shows steps only, since the frame has no subtree rule), `fill` (a device opened by its symbol on `ob`).
   `search`, `zoom` and `panels` are ASM gates: on `obasm` the field, the zoom measures (the header zoom steps use the head rectangle of 132 px)
   and the tree and support list (the page titles looked for among the tree's items, drawn or not, the support entries among the drawn items);
   on `ob`, which has no field, tree or floating faceplate, they are skipped with the reason in `gates.json`.

#### 13.11.4 Measured Facts

1. A press on a tree group only toggles it; the route is unchanged and the dock stays open (`wiki/04` section 11.3). Batch F7 had read a navigation
   and a closed dock; batch F8 measured otherwise (section 13.11.6 item 4).
2. Nobody signed in, the alarm menu draws every row's ACK disabled (`primaryActionState` disabled), unlike the default frame's panel, which hides it.
3. The alert menu closes on a click outside, on Escape and on the bell pressed again; no close button.
4. The bell and the menu count different things, as in the older frames: the bell is `custom.alarm.count` (`alarm_summary`, the active alarms
   of the scope), the menu lists `alarm_list`, which adds the cleared alarms not yet acknowledged and repeated events of one source (section 13.11.6
   item 5).
5. `obc-alert-menu-item`'s `title`, `description`, `status` and `primaryActionState` and the `obc-alert-icon` child's `type`, `active` and
   `acknowledged` are readable as properties of the elements.

#### 13.11.5 Not Verified Without a Signed In Run

The row ACK enabled and pressed, ACK visible pressed, Sign out offered after the login, the acknowledging user's name from `custom.alarms.alerts`
(F18), the strip's ACK pressed (F7, the latch step) and the palette's effect on the page (F9 was measured to reach `palette/night` and back to
`palette/day` in a throwaway session). Each is for the first G10 run on a sample of either frame. Measured by batch F8: all passed on both samples (section 13.11.6 item 3).

#### 13.11.6 Fixes of Batch F8

Measured and fixed on 2026-11-03 against `cadre_hmi_wtpobf` and `cadre_hmi_wtpoba` (module 0.7.0). The frames themselves needed no change; each
fix is in the glass.

1. The alert menu left open over the faceplate dock (G10 F13 on `ob`). Cause: F11 and F14 closed the menu by pressing the row's text with
   `click_text_in(panel, "P-502 Fault")`. The older panel prints the text as an element; the new menu keeps it in the item's `title` and
   `description` properties and in a shadow root, where Playwright finds the text but with no size, so nothing was pressed (F11 would also have
   failed). The frame behaves as the older frames do: a press on the row closes the popup and opens the device's faceplate (measured). Fix:
   `glass.click_alert_row`, which presses a point on the `obc-alert-menu-item` clear of its ACK (`ALERT_MENU_ROW_BODY`) in the new frames and the
   older text press otherwise; `functional` F11, F14 and `glass` (the sequence step) call it. Held by `tests.test_walk.FrameGlassTests`.
2. Walk rows N-05 and N-06 on `obasm` (Trends and Alerts not found). Cause: those pages are in the support list, which the apps button shows; the
   tree does not hold them. Fix: `glass.open_support_list`, which `navigate_by_menu` calls on `obasm` when the tree has no such entry. Held by
   `FrameGlassTests`.
3. The signed in steps (row ACK enabled and pressed, ACK visible, the strip's ACK, F18, Sign out) passed on both samples without a change.
4. The tree group press navigates (F7): not reproduced. A group press only toggles (section 11.3 of `wiki/04` corrected).
5. The bell read 2 where the menu listed 6 rows: not a defect. See 13.11.4 item 4.


#### 13.11.7 Walk Row A-02 and the Older Panel's Toolbar

Measured and fixed on 2026-11-03 against `cadre_hmi_wtpob` (the older frame, module 0.7.0). The frame and the module needed no change; the fix is in the glass.

1. Symptom. Row A-02 (TK-101's high level alarm, acknowledged from the top bar's alarm menu) failed in some runs with "acknowledged in the alarm menu:
   False", leaving a cleared, unacknowledged event; A-01 (AIT-301) never did. The generated project was the same in passing and failing runs.
2. Cause. The older frame's menu is the module's `obc-alert-list-page-small`. The panel draws its toolbar (the All filter, silence and ACK VISIBLE)
   over the bottom of its list, and the list shows one row clear of it. The walk's plant holds P-502's unacknowledged fault, which sorts first, so
   TK-101's row is the second, and the centre of its ACK cell (y 280) lay at the toolbar's lower edge. `glass.ack_alarm` pressed the cell's centre
   as read, the press landed on the toolbar's `div.action` (the pointer event's target, measured), no `ack-click` followed, and the six tries of
   `walk_run.acknowledge` read the same position. Whether the edge reached the cell varied between runs (a layout difference of a pixel or two, inferred), hence the
   intermittence; AIT-301's row is the first and was never covered. Each failed run left one more unacknowledged cleared event on TK-101, which
   the following runs counted (the Alarms tab read 2, 3 and 5 before the step).
3. Fix. `ROW_ACTION` also answers `clear`: whether the element at the cell's centre, followed through shadow roots, is the cell or inside it.
   `ROW_REVEAL` scrolls the row to the top of the list's own scroll area. `glass.ack_alarm`, on the older frames, scrolls the row and reads it again
   while `clear` is false, and returns False rather than press a covered cell. The new frames' menu (`ALERT_MENU_ROW`) has no toolbar over its rows
   and is unchanged. Held by `tests.test_walk.AlertMenuRowTests` (a covered cell is scrolled before the press; one that stays covered is not pressed).
4. Evidence. In the runs that failed, every press of the six tries had the same target (the toolbar) and the same position; the faceplate probe read
   the element at the cell's centre as the toolbar's `div.action` (49 px high) while the row query still said the ACK was drawn and enabled. The
   dependence on a pixel or two of layout is inferred from runs that passed at the same position. With the fix, see the runs recorded in
   `cloud/PROGRESS.md`.
5. For the product: an operator meets the same overlap in the small panel, where the second row's ACK is under the toolbar until the list is scrolled.
   The panel is the package's layout and is not changed here (rule 7 of the operating manual).
