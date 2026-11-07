# Proposal for the Element Map and the Placement, Against the 0.8.0 Module

## 1. Purpose and Basis

1.1 This document proposes what `module/openbridge-map.json` (schema `cadre-hmi-openbridge-map/1`) and the placement tool's
survey mode would need to say so that they agree with the 97 component types that this repository's module (release 0.8.0)
registers. It is a proposal for the owner. It changes no file: under ruling R2 the map is carried unchanged and its tests keep
asserting it, so every change below is a decision for the owner and, where it touches an asserted fact, names the test that
asserts it (section 6).

1.2 The basis is the merge commit `11005e3` of branch `port/sandbox-0.8.0` (measured in its working tree just before it was
committed). The map, the elements list, `module/components.json`, `library/profile.json` and `library/contracts.json` are
unchanged from that commit to the branch's later commits; `tools/hmi/placement_survey.py`, `library_gaps.py` and `screen.py`
changed only in message texts and one comment, on the same lines, so the line numbers below hold.

1.3 Files read: `module/openbridge-map.json`, `module/openbridge-elements.json` (281 element tags), `module/components.json`
(97 types, 96 with an `element`), `library/profile.json`, `library/contracts.json` (74 views), `tools/hmi/placement_survey.py`,
`tools/hmi/library_gaps.py`, `tools/hmi/screen.py` (tables `KIND_VIEW` at line 44, `FRAME_ONLY` at 186, `MODULE_ONLY` at 210,
`MODULE_KIND` at 250), `tests/test_openbridge_pin.py`, `tests/test_module_generator.py` and `cloud/import/NOTE-WFB-10-standard-migration-workflow.md`
(sections 7.5 and 11.1).

1.4 Method. Every table was computed by read-only Python that imports `hmi.screen` and `hmi.placement_survey` and calls
`Rules` and `build_survey` directly on a synthetic survey of one entry per kind (99 kinds: the 15 of `KIND_VIEW`, the 81 of
`MODULE_ONLY` and `command-button`, `range-bar`, `generator-set`), with the instance count 1 and 2, `local_max` 1, and the
module-first flag on and off. Nothing was written. The survey command itself (`run_survey`, `placement_survey.py:581`) refused
while the merge was uncommitted, because `provenance.differing_from_head` (`placement_survey.py:588`) found the map, the
elements list and the profile different from HEAD. Once the merge was committed, the command run over one kind per type of
`module/components.json` (two instances each, `--module-first`, `local_max` 1) placed 12 kinds `module` and 85 `shared_gap`, with no
wrap and one pending proposal (the `bus` row, source `map`); with `--local-max 2` the same 85 kinds were placed `local`
(`cloud/REPORT-T3.md` section 6, item 5).

1.5 Two facts differ from the brief and from the note. First, the `generator` row is not `proposed`: it is `reviewed`, with
four states and the reference `WFBD-137`, so three rows are `proposed`, not four. Second, the note (section 7.7) describes
`properties` as an object from a kind's parameter to an element property, whereas the file and its test hold the empty list
`[]` for every row.

## 2. The Rules of Placement as the Code Applies Them

2.1 Inputs. `Rules` (`placement_survey.py:208`) takes the catalogue (`library/contracts.json`), the profile, the module
(`module/components.json`, a dictionary keyed by type name, used only for a membership test), the map, the flag
`module_first` (`--module-first`, off unless given, `library_gaps.py:497`) and `local_max` (default 1, `library_gaps.py:506`).

2.2 Library resolution (Table 7.5 row 1). `Rules.library_of` (`placement_survey.py:217`) returns a resolution only when all
three hold: `KIND_VIEW.get(kind)` names a view (the table of `screen.py:44`), the kind is a key of the profile's `kinds`, and
that view is a key of the catalogue. The placement is then `module` when `module_first` holds and `part_name(kind)`
(`placement_survey.py:40`, `cadre.ob.` plus the kind without hyphens) is a key of the module, otherwise `library`. The
tables `MODULE_KIND`, `MODULE_ONLY` and `FRAME_ONLY` are not read anywhere in the placement code.

2.3 The table. `table_placement` (`placement_survey.py:263`) takes the first row that applies. A kind with a library resolution
is placed by row 1 before its count or its map row is looked at. A kind with no instance is `unclassified`. Otherwise
`placing_row` (`placement_survey.py:243`) returns the first map row of the kind in a state of `PLACING_STATES` (`reviewed` or
`approved`, line 36) and the kind is placed `openbridge` with the element as its resolution (row 2). With no such row the kind
is `shared_gap` when its count exceeds `local_max` (row 3) and `local` otherwise (row 4). A kind that earlier surveys placed `local` (`prior_local_keys`, `placement_survey.py:293`) becomes a shared gap when row 4 would
place it local (`placement_survey.py:478`).

2.4 Map rows. A row in state `proposed` never places. `judge_proposals` (`placement_survey.py:351`, rows at lines 379 to 398)
shows a `proposed` kind row as a pending proposal (source `map`) only when the kind is in the survey, has instances, has no
library resolution and has no placing row; it is otherwise skipped silently. `check_map_rows` (`placement_survey.py:58`)
refuses the run when a `reviewed` or `approved` row has no element or an element that is not a tag of the elements list.
`wrap_needed` (`placement_survey.py:615`) hands the placing row's `element`, `properties` and `states` to the release as what
the wrap needs.

2.5 `rejected[]`. No tool reads it. The only occurrences of the word in the two tools are the handling of the owner's
`reject_proposal` changes (`placement_survey.py:424` to `465`). A rejected entry therefore has no effect on any placement: it
is documentation, asserted by tests.

2.6 Page mode. `library_gaps.analyse` (`library_gaps.py:378`) applies the same test at line 401 (`in_library`) and 402 (the
module part), and the late rule `SurveyView.mapped` (`library_gaps.py:300`, used at line 359) looks up only `reviewed` and
`approved` rows of kinds that have no library resolution.

2.7 Agreement with the note. Table 7.5 and its keys 1 to 3 describe what the code does. The one reading to avoid is row 1's
wording "module part or library view": the code needs the profile, the `KIND_VIEW` entry and the catalogue view, so a module
part alone, with no library view, never reaches row 1.

## 3. The Four Proposed Rows

The common finding is that rows 1 and 2 are exclusive: a map row is read only for a kind with no library resolution. Of the
four kinds, `switch` and `generator` are profile kinds with a view and a module part, so their rows can never place anything;
`bus` and `command-button` have no library resolution, so theirs are the only rows that matter. Where a proposed JSON gives
`properties`, it is the object form of the note (kind parameter to element property), with the names the type and the element
share (computed from `module/components.json` and `module/openbridge-elements.json`); the module adds `componentSize` to every type,
which has no element property and is left out. The state names are for the owner to settle: only the properties in `props` are
drawn from the type.

### 3.1 Switch

3.1.1 As it stands: kind `switch`, element `obc-switch`, import `dist/automation/switch/switch.js`, state `proposed`, empty
`properties` and `states`, reference null.

3.1.2 What this repository builds: `cadre.ob.switch` on `obc-switch` (24 properties, 23 shared with the element), the kind
`switch` in `MODULE_KIND` (drawn under `--render module`) and in `KIND_VIEW` (`Automation/Switch`). The profile lists the kind
with `moduleExcept` for a vertical switch and `moduleNeeds` for the variants `regular` and `flat`.

3.1.3 Placement today: row 1. The kind is in the profile, `Automation/Switch` is in the catalogue and `cadre.ob.switch` is in
the module, so the result is `module` with module-first and `library` without it (measured at both counts). The row is
unreachable: `table_placement` returns at row 1 and `judge_proposals` skips the kind (line 387).

3.1.4 Proposal. Remove the row, because row 1 already places the kind. If the owner wants the map to record the wrap, change
the state to `reviewed`; it is then inert and changes no placement:

```json
{
  "kind": "switch",
  "feature": null,
  "element": "obc-switch",
  "import": "@oicl/openbridge-webcomponents/dist/automation/switch/switch.js",
  "properties": {"alternativeIcon": "alternativeIcon", "on": "on", "variant": "variant", "orientation": "orientation", "readoutPosition": "readoutPosition", "readoutSize": "readoutSize", "tag": "tag", "positioning": "positioning", "activated": "activated", "alert": "alert", "alertFrameType": "alertFrameType", "alertFrameThickness": "alertFrameThickness", "alertFrameStatus": "alertFrameStatus", "alertFrameMode": "alertFrameMode", "showAlertIcon": "showAlertIcon", "progress": "progress", "progressMode": "progressMode", "progressValue": "progressValue", "badgeControl": "badgeControl", "badgeCommandLocked": "badgeCommandLocked", "badgeInterlock": "badgeInterlock", "badgeAlert": "badgeAlert", "showStatus": "showStatus"},
  "states": [
    {"name": "off", "props": {"on": false}},
    {"name": "on", "props": {"on": true}},
    {"name": "alarm", "props": {"on": true, "alert": true, "alertFrameStatus": "alarm"}}
  ],
  "state": "reviewed",
  "reason": "Drawn by the module type cadre.ob.switch. The kind is a library kind, so the survey places it by row 1 and this row is a record of the wrap, not a placement.",
  "reference": null
}
```

### 3.2 Bus

3.2.1 As it stands: kind `bus`, element `obc-bus` (beta), import `dist/automation/bus/bus.js`, state `proposed`, empty `properties`
and `states`. Its reason speaks of corners needing the pinned line elements.

3.2.2 What this repository builds: `cadre.ob.bus` on `obc-bus` (display only; the properties `label`, `size`, `variant`, `tint`
and `vertical` are the element's own), the kind `bus` in `MODULE_ONLY` (`screen.py:210`, the last row before the frame
components). It is not in `KIND_VIEW`, not in `MODULE_KIND` and not a profile kind. The same module draws the corners and
other pipe shapes as separate types (`cadre.ob.pipecorner`, `pipetee` and the rest).

3.2.3 Placement today: no library resolution, so row 2 is looked for and the `proposed` row does not count. A survey kind
`bus` is therefore `local` at one instance and `shared_gap` at two or more (rows 4 and 3), and the row surfaces as a pending
proposal on the owner's card (measured). The module already holds the part, which the placement does not see.

3.2.4 Proposal. Change the state to `reviewed`, with the properties above and no states (no property of the type encodes a
process state; the existing reason's "dead state" cue has no property to draw from). The kind is then placed `openbridge`
(row 2), which Table 7.5 reads as a wrap still to be built by the project release. That is redundant for this repository, because the type
exists; see section 6.1 and 6.2 for the alternative of letting the tool see the existing type.

```json
{
  "kind": "bus",
  "feature": null,
  "element": "obc-bus",
  "import": "@oicl/openbridge-webcomponents/dist/automation/bus/bus.js",
  "properties": {"label": "label", "size": "size", "variant": "variant", "tint": "tint", "vertical": "vertical"},
  "states": [],
  "state": "reviewed",
  "reason": "Drawn by the module type cadre.ob.bus (display only). The library has no bus kind or view, so this row is what places the kind.",
  "reference": null
}
```

### 3.3 Generator

3.3.1 As it stands: kind `generator`, element `obc-automation-button`, import `dist/automation/automation-button/automation-button.js`,
state `reviewed`, the four states `running`, `stopped`, `fault` and `out_of_service`, reference `WFBD-137`.

3.3.2 What this repository builds: `cadre.ob.generator` on `obc-indicator-generator`, not on `obc-automation-button`. The kind is
in `MODULE_KIND` and `KIND_VIEW` (`Automation/Generator`, with `Automation/GeneratorSet` for `picture` `genset`, `screen.py:52`).
Of the type's 13 properties only four (`variant`, `value`, `level`, `secondaryLevel`) belong to the element; the wrapper adds `on`,
`tag`, `readoutPosition`, `showStatus`, `statusText`, `alert`, `alertFrameStatus`, `alertFrameMode` and `componentSize`. The
element `obc-automation-button` is wrapped here by another type, `cadre.ob.button`.

3.3.3 Placement today: row 1, `module` (module-first) or `library`, at both counts. The `reviewed` row is never read. Were
it read, it would name an element that the generator does not use. Its state `out_of_service` uses `outOfService`, which is not a
property of `cadre.ob.generator` (the pump, motor and fan types have it; the generator's `outOfService` is a library mark,
`wiki/16-component-selection.md` line 86).

3.3.4 Proposal. Remove the row (row 1 places the kind and the row's element is not the generator's). If the owner prefers a
record, re-point it as follows; the fourth state cannot be drawn from the type's properties and is dropped, to be recorded
as a library mark:

```json
{
  "kind": "generator",
  "feature": null,
  "element": "obc-indicator-generator",
  "import": "@oicl/openbridge-webcomponents/dist/automation/indicator-generator/indicator-generator.js",
  "properties": {"variant": "variant", "value": "value", "level": "level", "secondaryLevel": "secondaryLevel"},
  "states": [
    {"name": "running", "props": {"on": true}},
    {"name": "stopped", "props": {"on": false}},
    {"name": "fault", "props": {"on": true, "alert": true, "alertFrameStatus": "alarm"}}
  ],
  "state": "reviewed",
  "reason": "Drawn by the module type cadre.ob.generator, which adds the on state, the tag, the readout and the alert frame to the element. The kind is a library kind, so this row is a record of the wrap, not a placement.",
  "reference": "WFBD-137"
}
```

### 3.4 Command button

3.4.1 As it stands: kind `command-button`, element `obc-button` (stable), import `dist/components/button/button.js`, state
`proposed`, empty `properties` and `states`. Its reason holds that the automation button has no label and does not fit.

3.4.2 What this repository builds: no type on `obc-button` (no entry of `module/components.json` has that element). The command button
is `cadre.ob.button`, on `obc-automation-button` (20 properties shared with the element). It is in none of `KIND_VIEW`,
`MODULE_KIND` or `MODULE_ONLY`: `screen.py` draws it only as the question button of the page parts (`parts.py:425`,
`screen.py:1292`), never as a descriptor symbol (`view_of` returns an empty view for `command-button`).

3.4.3 Placement today: no library resolution and no placing row, so `local` at one instance and `shared_gap` at two or more; the
`proposed` row surfaces as a pending proposal (measured).

3.4.4 Proposal (preferred). Point the row at the element the module wraps and mark it `reviewed`. The kind is then `openbridge`,
and the existing type is the wrap; the generator cannot draw the kind as a symbol, so the row serves the survey only:

```json
{
  "kind": "command-button",
  "feature": null,
  "element": "obc-automation-button",
  "import": "@oicl/openbridge-webcomponents/dist/automation/automation-button/automation-button.js",
  "properties": {"variant": "variant", "state": "state", "static": "static", "activated": "activated", "tag": "tag", "readoutPosition": "readoutPosition", "readoutSize": "readoutSize", "alert": "alert", "alertFrameType": "alertFrameType", "alertFrameThickness": "alertFrameThickness", "alertFrameStatus": "alertFrameStatus", "alertFrameMode": "alertFrameMode", "showAlertIcon": "showAlertIcon", "progress": "progress", "progressMode": "progressMode", "progressValue": "progressValue", "direction": "direction", "positioning": "positioning", "orientation": "orientation", "hasBadgeSpacer": "hasBadgeSpacer"},
  "states": [
    {"name": "open", "props": {"state": "open"}},
    {"name": "closed", "props": {"state": "closed"}},
    {"name": "activated", "props": {"activated": true}},
    {"name": "fault", "props": {"alert": true, "alertFrameStatus": "alarm"}}
  ],
  "state": "reviewed",
  "reason": "Drawn by the module type cadre.ob.button, the command button of the page parts. No descriptor kind of that name is drawn by the generator, so the row serves a survey kind only.",
  "reference": null
}
```

Alternative: keep the row unchanged (`obc-button`, `proposed`), which stays correct as a candidate for a label-bearing button
that no type yet wraps.

## 4. The Three Rejected Entries

4.1 `range-bar` on `linear-indicator`. `linear-indicator` is not a tag of the elements list (281 tags), and no type of the module has it as an
element. The statement stands. The library draws a range bar as the page part `Parts/RangeBar` (kind `rangebar`,
`library/contracts.json` line 1391, `wiki/05-component-catalogue.md` line 258). It is not a profile kind, so the survey does
not see it: a survey kind `range-bar` is placed `local` or `shared_gap`. No change to the entry; whether the part should
count as a library resolution is question 6.7.

4.2 `generator-set` on `obc-gauge-generator`. This repository now wraps `obc-gauge-generator`, as the module-only kind `gauge-generator`
(`cadre.ob.gaugegenerator`, `MODULE_ONLY`). The set itself is still drawn by the library (`Automation/GeneratorSet`, a
generator with `picture` `genset`) and the module's generator does not draw it (`wiki/16-component-selection.md` line 82), so the
rejection of the element as the set's drawing remains true, but its reason ("experimental") now reads as though the element is
unused. Proposed entry, same key set, so the test that asserts the key set (`test_openbridge_pin.py:309`) is unaffected:

```json
{
 "kind": "generator-set",
 "element": "obc-gauge-generator",
 "reason": "Rejected as the drawing of the generator set, which stays the library view Automation/GeneratorSet (a generator with picture genset). The element itself is wrapped by the module as the separate module-only kind gauge-generator (cadre.ob.gaugegenerator), a radial load gauge."
}
```

The survey kind `generator-set` is not a profile kind and so is placed `local` or `shared_gap`, although the library draws
the set under the kind `generator`.

4.3 `generator` on `obc-indicator-generator`. This entry contradicts the 0.8.0 module: `cadre.ob.generator` is exactly this
element (`MODULE_KIND`). Its reason ("no on state, tag, readout stack, badges or alert frame") is true of the element and false of the
type, because the wrapper supplies the on state, the tag, the readout, the status text and the alert frame (3.3.2). The entry
also shares its kind with the map's `generator` row. Proposed: remove the entry. If the owner adopts the re-pointed `generator` row of 3.3.4, removal is required, not optional:
the entry and that row would name the same element, and `test_rejected_elements_are_not_proposed`
(`test_openbridge_pin.py:318`) asserts that no rejected element is proposed.

## 5. The 97 Types

5.1 One row per type of `module/components.json`, in its order. "Kind it serves" is the key of the table in `screen.py` that
names the type as its value; "placement today" is the placement the survey gives a plant object of that kind (rows of Table
7.5), measured at instance counts 1 and 2 with `local_max` 1. Module-first off changes only the first category, from `module`
to `library`.

| # | Type | Element | Kind it serves in `screen.py` | Placement today | What the map would need |
|---|---|---|---|---|---|
| 1 | `cadre.ob.pump` | `obc-pump` | `pump` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 2 | `cadre.ob.tank` | `obc-automation-tank` | `tank` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 3 | `cadre.ob.motor` | `obc-motor` | `motor` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 4 | `cadre.ob.fan` | `obc-fan` | `fan` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 5 | `cadre.ob.valve` | `obc-digital-valve` | `valve` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 6 | `cadre.ob.analogvalve` | `obc-analog-valve` | `analogvalve` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 7 | `cadre.ob.filter` | `obc-filter` | `filter` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 8 | `cadre.ob.generator` | `obc-indicator-generator` | `generator` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 9 | `cadre.ob.button` | `obc-automation-button` | none | not a plant kind | a `reviewed` row only if the owner wants `command-button` placed (section 3.4) |
| 10 | `cadre.ob.readout` | `obc-transmitter` | `readout` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 11 | `cadre.ob.instrumentfield` | `obc-instrument-field` | `instrument-field` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 12 | `cadre.ob.alertlist` | `obc-alert-list-details` | none | not a plant kind | not applicable |
| 13 | `cadre.ob.alertpanel` | `obc-alert-list-page-small` | none | not a plant kind | not applicable |
| 14 | `cadre.ob.resistor` | `obc-resistor` | `resistor` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 15 | `cadre.ob.damper` | `obc-damper` | `damper` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 16 | `cadre.ob.switch` | `obc-switch` | `switch` (`MODULE_KIND`) | row 1, `module` (`library` if module-first is off) | nothing |
| 17 | `cadre.ob.capacitor` | `obc-capacitor` | `capacitor` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 18 | `cadre.ob.diodes` | `obc-diodes` | `diodes` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 19 | `cadre.ob.ground` | `obc-ground` | `ground` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 20 | `cadre.ob.source` | `obc-source` | `source` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 21 | `cadre.ob.converter` | `obc-converter` | `converter` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 22 | `cadre.ob.transformer` | `obc-transformer` | `transformer` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 23 | `cadre.ob.bipolartransistor` | `obc-bipolar-transistor` | `bipolar-transistor` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 24 | `cadre.ob.mosfet` | `obc-mosfet` | `mosfet` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 25 | `cadre.ob.logic` | `obc-logic` | `logic` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 26 | `cadre.ob.router` | `obc-router` | `router` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 27 | `cadre.ob.automationbadge` | `obc-automation-badge` | `automation-badge` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 28 | `cadre.ob.checkvalve` | `obc-hydraulic-check-valve` | `hydraulic-check-valve` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 29 | `cadre.ob.valvetwoway` | `obc-valve-analog-two-way-icon` | `valve-analog-two-way-icon` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 30 | `cadre.ob.valvethreeway` | `obc-valve-analog-three-way-icon` | `valve-analog-three-way-icon` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 31 | `cadre.ob.battery` | `obc-indicator-battery` | `indicator-battery` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 32 | `cadre.ob.engine` | `obc-indicator-engine` | `indicator-engine` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 33 | `cadre.ob.tankatmospheric` | `obc-indicator-tank-atmospheric` | `indicator-tank-atmospheric` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 34 | `cadre.ob.automationreadout` | `obc-automation-readout` | `automation-readout` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 35 | `cadre.ob.heatexchanger` | `obc-heat-exchanger` | `heat-exchanger` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 36 | `cadre.ob.heatpump` | `obc-heat-pump` | `heat-pump` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 37 | `cadre.ob.hydraulicseparator` | `obc-hydraulic-separator` | `hydraulic-separator` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 38 | `cadre.ob.gaugegenerator` | `obc-gauge-generator` | `gauge-generator` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 39 | `cadre.ob.gaugemotorspumps` | `obc-gauge-motors-and-pumps` | `gauge-motors-and-pumps` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 40 | `cadre.ob.gaugevalve` | `obc-gauge-valve` | `gauge-valve` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 41 | `cadre.ob.hydraulicvalve43` | `obc-hydraulic-valve-4-3` | `hydraulic-valve-4-3` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 42 | `cadre.ob.hydraulicvalvex2` | `obc-hydraulic-valve-x-2` | `hydraulic-valve-x-2` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 43 | `cadre.ob.transmitterbutton` | `obc-transmitter-button` | `transmitter-button` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 44 | `cadre.ob.areagraph` | `obc-area-graph` | `area-graph` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 45 | `cadre.ob.linegraph` | `obc-line-graph` | `line-graph` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 46 | `cadre.ob.donutchart` | `obc-donut-chart` | `donut-chart` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 47 | `cadre.ob.piechart` | `obc-pie-chart` | `pie-chart` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 48 | `cadre.ob.polarchart` | `obc-polar-chart` | `polar-chart` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 49 | `cadre.ob.radialbarchart` | `obc-radial-bar-chart` | `radial-bar-chart` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 50 | `cadre.ob.barhorizontal` | `obc-bar-horizontal` | `bar-horizontal` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 51 | `cadre.ob.barvertical` | `obc-bar-vertical` | `bar-vertical` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 52 | `cadre.ob.circularprogress` | `obc-circular-progress` | `circular-progress` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 53 | `cadre.ob.instrumentradial` | `obc-instrument-radial` | `instrument-radial` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 54 | `cadre.ob.readoutblock` | `obc-readout-block` | `readout-block` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row |
| 55 | `cadre.ob.tooltip` | `obc-tooltip` | frame (`tooltip`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 56 | `cadre.ob.toggletip` | `obc-toggletip` | frame (`toggletip`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 57 | `cadre.ob.clock` | `obc-clock` | frame (`clock`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 58 | `cadre.ob.userbutton` | `obc-user-button` | frame (`user-button`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 59 | `cadre.ob.appbutton` | `obc-app-button` | frame (`app-button`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 60 | `cadre.ob.notificationbutton` | `obc-notification-button` | frame (`notification-button`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 61 | `cadre.ob.notificationbadgebutton` | `obc-notification-badge-button` | frame (`notification-badge-button`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 62 | `cadre.ob.alertbuttonitem` | `obc-alert-button-item` | frame (`alert-button-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 63 | `cadre.ob.alertbutton` | `obc-alert-button` | frame (`alert-button`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 64 | `cadre.ob.alertmenuitem` | `obc-alert-menu-item` | frame (`alert-menu-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 65 | `cadre.ob.alertmenu` | `obc-alert-menu` | frame (`alert-menu`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 66 | `cadre.ob.navigationitem` | `obc-navigation-item` | frame (`navigation-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 67 | `cadre.ob.navigationitemgroup` | `obc-navigation-item-group` | frame (`navigation-item-group`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 68 | `cadre.ob.navigationmenu` | `obc-navigation-menu` | frame (`navigation-menu`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 69 | `cadre.ob.treenavigationitem` | `obc-tree-navigation-item` | frame (`tree-navigation-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 70 | `cadre.ob.treenavigationgroup` | `obc-tree-navigation-group` | frame (`tree-navigation-group`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 71 | `cadre.ob.treenavigation` | `obc-tree-navigation` | frame (`tree-navigation`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 72 | `cadre.ob.breadcrumb` | `obc-breadcrumb` | frame (`breadcrumb`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 73 | `cadre.ob.brilliancemenu` | `obc-brilliance-menu` | frame (`brilliance-menu`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 74 | `cadre.ob.usermenu` | `obc-user-menu` | frame (`user-menu`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 75 | `cadre.ob.systemmenu` | `obc-system-menu` | frame (`system-menu`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 76 | `cadre.ob.appmenu` | `obc-app-menu` | frame (`app-menu`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 77 | `cadre.ob.commandmenu` | `obc-command-menu` | frame (`command-menu`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 78 | `cadre.ob.topbar` | `obc-top-bar` | frame (`top-bar`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 79 | `cadre.ob.tabitem` | `obc-tab-item` | frame (`tab-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 80 | `cadre.ob.tabrow` | `obc-tab-row` | frame (`tab-row`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 81 | `cadre.ob.pivotitem` | `obc-pivot-item` | frame (`pivot-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 82 | `cadre.ob.pivotitemgroup` | `obc-pivot-item-group` | frame (`pivot-item-group`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 83 | `cadre.ob.modalwindow` | `obc-modal-window` | frame (`modal-window`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 84 | `cadre.ob.contextmenuinput` | `obc-context-menu-input` | frame (`context-menu-input`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 85 | `cadre.ob.notificationmenuitem` | `obc-notification-menu-item` | frame (`notification-menu-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 86 | `cadre.ob.notificationmessageitem` | `obc-notification-message-item` | frame (`notification-message-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 87 | `cadre.ob.notificationfloatingitem` | `obc-notification-floating-item` | frame (`notification-floating-item`, `FRAME_ONLY`) | not a plant kind | not applicable |
| 88 | `cadre.ob.pipehorizontal` | `obc-horizontal-line` | `horizontal-line` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 89 | `cadre.ob.pipevertical` | `obc-vertical-line` | `vertical-line` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 90 | `cadre.ob.pipecorner` | `obc-corner-line` | `corner-line` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 91 | `cadre.ob.pipetee` | `obc-three-way-line` | `three-way-line` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 92 | `cadre.ob.pipecross` | `obc-line-cross` | `line-cross` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 93 | `cadre.ob.pipeoverlap` | `obc-line-overlap` | `line-overlap` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 94 | `cadre.ob.pipeend` | `obc-end-point-line` | `end-point-line` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 95 | `cadre.ob.pipedirection` | `obc-direction-line` | `direction-line` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row; part name differs from the kind |
| 96 | `cadre.ob.bus` | `obc-bus` | `bus` (`MODULE_ONLY`) | row 3 `shared_gap` or row 4 `local`, by count | a `reviewed` row (a row exists as `proposed`) |
| 97 | `cadre.ob.canvaszoom` | none (own) | none | not a plant kind | not applicable |

5.2 Totals by category (97 types):

| Category | Types | Placement today | What the map would need |
|---|---|---|---|
| Plant kinds that are library kinds (`MODULE_KIND`) | 12 | row 1, `module` or `library` | nothing |
| Plant kinds that are module only, part name equals the kind's (`MODULE_ONLY`) | 33 | rows 3 and 4 | a `reviewed` row each, or a placement change |
| Plant kinds that are module only, part name differs from the kind's | 15 | rows 3 and 4 | as above, and a table, not `part_name`, if the tool is to find the part |
| Frame components (`FRAME_ONLY`) | 33 | not a plant kind | not applicable |
| No kind (`cadre.ob.button`, `alertlist`, `alertpanel`, `canvaszoom`) | 4 | not a plant kind | not applicable (`cadre.ob.button` only through the row of 3.4) |
| Total | 97 | 12 placed by row 1, 48 by rows 3 and 4, 37 not plant kinds | |

5.3 The 15 module-only types whose part name differs from `part_name(kind)` are: `hydraulic-check-valve` (`checkvalve`),
`valve-analog-two-way-icon` (`valvetwoway`), `valve-analog-three-way-icon` (`valvethreeway`), `indicator-battery` (`battery`),
`indicator-engine` (`engine`), `indicator-tank-atmospheric` (`tankatmospheric`), `gauge-motors-and-pumps` (`gaugemotorspumps`),
`horizontal-line` (`pipehorizontal`), `vertical-line` (`pipevertical`), `corner-line` (`pipecorner`), `three-way-line` (`pipetee`),
`line-cross` (`pipecross`), `line-overlap` (`pipeoverlap`), `end-point-line` (`pipeend`) and `direction-line` (`pipedirection`).
All 96 elements named by the types are tags of the elements list, so any `reviewed` row for them passes `check_map_rows`.

5.4 The three kinds of `KIND_VIEW` with no module type (`controller`, `indicator`, `sequence`) are library kinds placed by row 1
as `library` in every case; they are not among the 97 and need nothing.

## 6. Findings and Open Questions for the Owner

6.1 Module-only kinds cannot reach row 1. The 48 plant kinds of `MODULE_ONLY` are not profile kinds and have no view in the
tracked catalogue: their contracts are synthesised at build time (`screen.load_contracts`, `screen.py:684` to `689`, view name
`Module/<kind>`, `MODULE_VIEW` at line 241) and are not in `library/contracts.json`. `library_of` reads only `KIND_VIEW`. A
plant object of any of them is today `local` or `shared_gap`, which asks for a local assembly or a new library view for a kind the
module already draws. Question: should the placement see them?

6.2 Options for 6.1. (a) Let `library_of` also consult `MODULE_ONLY`, minus `FRAME_ONLY`, and return `module` with the type as
resolution; this needs the table's value, not `part_name`, for the 15 kinds of 5.3, and a decision on module-first (a
module-only kind has no library drawing to fall back on, so `library` has no meaning for it). The placement tool already
imports `KIND_VIEW` from `screen.py` (line 26), so reading the other table is a small change in `placement_survey.py:217`, but
it changes the placement tool and the contract of Table 7.5. (b) Write 48 `reviewed` rows (section 5), each passing
`check_map_rows`; the kinds are then `openbridge`, which Table 7.5 reads as a wrap still to be built. (c) Add the kinds to the profile and
views to the catalogue; not recommended, as it makes the tracked contracts carry what the generator derives. The recommendation
is (a), because (b) reports a wrap as to be built that the module has already built.

6.3 The `generator` row and the rejected `obc-indicator-generator` entry contradict the 0.8.0 generator (3.3, 4.3): the map says
the generator is `obc-automation-button` and the element `obc-indicator-generator` is rejected, while the module draws the generator on
`obc-indicator-generator` and the other element is the command button. The map cannot be right in both places. The proposal of
3.3.4 and 4.3 (remove both, or re-point both) resolves it; leaving both is harmless to placement (neither is read) but false.

6.4 The command button. The map's candidate `obc-button` is not wrapped; the module's command button is on `obc-automation-button`
(3.4). Question: does the owner want the row to follow the module (proposal 3.4.4) or to stay a candidate for a label-bearing button?

6.5 Rows that cannot place: the `switch` and `generator` rows (3.1.3, 3.3.3) are dead for any survey, whatever their state, and
the `bus` and `command-button` rows are the only ones with an effect (3.2.3, 3.4.3). A map that carries only rows that can
place would hold `bus` and `command-button`.

6.6 Tests and ruling R2. The proposals touch these assertions, which would have to change together with the map:
`tests/test_openbridge_pin.py:283` (exactly the four kinds, the element and import of each, the generator `reviewed` with its
four states and reference, the others `proposed` with empty states and `properties == []`), `:309` (exactly three rejected
entries, with the element set) and `:318`; `tests/test_module_generator.py:400` (`TheMapRow`: one `reviewed` generator row on
`obc-automation-button`, its four states, the rejected kinds) and `:436` (`TheTestPage`, which drives the map row's states). When this was measured (before the merge
commit), 27 of the 80 tests of `tests.test_openbridge_pin` and `tests.test_module_generator` failed, all in
`test_module_generator.py`, which asserted the other line's generator wrap. They were ported under ruling R4 in commit `0a442c1`
and pass: `TheMapRow` asserts the map as carried, and the row's state properties that `cadre.ob.generator` lacks as the exact named
difference (`outOfService` of `out_of_service`). Any change proposed here changes those assertions with the map.

6.7 Smaller questions. (i) Should `properties` be the object of the note or the list `[]` of the file and test? `wrap_needed`
passes whatever the row holds to the release (`placement_survey.py:625`). (ii) Should `Parts/RangeBar` and the library's
generator set count as library resolutions for the survey kinds `range-bar` and `generator-set`? The profile has no entry for either, so the
survey places both `local` or `shared_gap`. (iii) Should the survey refuse an uncommitted tree only for the three files it
names (`placement_survey.py:588`), as now, or also for `library/contracts.json`, which row 1 reads but the check does not
name? (iv) `rejected[]` is read by no tool; should the placement refuse a `reviewed` row whose element is in `rejected[]`, so that the
list has an effect?
