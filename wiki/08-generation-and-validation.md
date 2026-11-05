---
title: Generation and validation
type: wiki
updated: 2026-10-23
---
# 08 Screen Generation and Validation

| Field | Value |
|---|---|
| Document ID | COB-WIKI-08 |
| Revision | I |
| Status | Issued for use |
| Code | `tools/hmi/` (generator), `tools/compare/` (live gates and comparison), `schemas/screen-descriptor.schema.json`, `schemas/devices.schema.json` |

## 1. Purpose

This page describes how a Cadre tool builds and proves a screen on the parent library: the
descriptor it writes, what the generator does with it, and the gates every build passes before
and after it reaches the gateway.

The device model of section 3.1, gate G7 devices and the additions to gate G11 were built on
2026-10-10; the kind `sequence`, the pulse members of a device model and their rules in gate G7
devices followed on 2026-10-11; of these only the sequence's block and faceplate have been on the
gateway (gates G8 and G11 on the fixture). Page 13 section 9.8 states what the
gateway has proven of them and what it has yet to prove.

The height of a row of cards (section 3.2), the warnings of gate G5 on a block too small and the
gates in the `--report` file (section 5) followed on 2026-10-11, after the first page built from a
plant's data; gate G8 ran on every route of the sample projects and of the fixture afterwards. A
review of the same day added the readout that the generator grows, the room an identifier has beside
the next symbol (section 3) and the notes of a route (section 5).

The generated operator walk (section 9) followed on 2026-10-11: gate G10's proof for a project built
from data, with its plan, its rules of evidence, its effects file and its negative controls.

## 2. Pipeline

1. A descriptor (JSON) is written by ctig or by hand. A tool
   that knows the devices' tags may write a device model beside the descriptors (section 3.1).
2. Gate G0 validates each against its schema.
3. The generator writes the child project files.
4. Gates G1 to G7 check the files offline.
5. The project is imported through the gateway REST lane, after the tag model when one is given
   (`--tags-file`).
6. Gates G8 to G11 check the rendered pages, the live flow, an operator's functions and every
   faceplate.

The generator is deterministic: the same descriptor gives the same bytes (a unit test checks the
zip of a rebuild against the first build).

## 3. The Screen Descriptor

The descriptor (`cadre-hmi-screen/1`) names one screen; `screens/sample-pump-station.json` is a
complete example, and `screens/wtp/` holds the four generated pages of the water treatment sample
(page 11).

This section explains the descriptor; page 18 gives every key of the descriptor and the device model, the
parameters of each kind and the placement arithmetic as a reference for a tool that writes them, page 17 the
tag structure (one UDT per device kind) and page 16 the criteria for choosing a kind.

Table 1. Descriptor sections.

| Key | Content |
|---|---|
| `screen` | `id`, `route`, `title`, `view` (path in the child), `layout` (`diagram` or `cards`), `width`, `height`, navigation `icon`, and `node`, the node of the plant hierarchy the page shows (`WTP/Filtration`; page 04 section 7): a device belongs to the node of the deepest page that draws it, which its alarms' display path names (page 13 section 11.3) |
| `tagRoot` | The tag folder relative binding members resolve under |
| `tagModel` | `generated` (default): the generator writes memory tags for a test build; `external`: the tags exist, imported from a tag model file, and none are generated |
| `tagValues` | Initial memory tag values for a test build |
| `toolbar`, `showTags` | Diagram operator toolbar (colour mode, identifier tags, readouts); identifier tags shown at start, off where `showTags` is not stated. ID-tag reaches the automation symbols, tanks, readouts and the label of an instrument field; Color is drawn only where a pipe names a medium (COBD-050, COBD-051) |
| `sections` | Background sections: box, `label`, optional drill-down `route` |
| `symbols` | `id`, `kind`, box (`x`, `y`, `w`, `h`), `params` (static), `bind` (parameter to tag member), `device` (`true` or the tag folder: opens the faceplate, page 06 section 5), `label` (the device description in the faceplate header). A readout or an instrument field that shows a member of a device of another kind names that kind in `params.deviceKind` (`controller` for a loop's process value) |
| `labels` | Free text on a diagram: `id`, box, `text`, `align` (`left`, `center`, `right`), `style` (`heading`, `body`, `label`) |
| `junctions` | Pipe junctions: `id`, point |
| `pipes` | `id`, `from`, `to` (a symbol side, a junction, or a free point with an end mark `cap`, `arrow-in`, `arrow-out`), `via` points, `medium`, `size`, `state` |
| `rows` | Cards layout: rows of cards, each with a title, an optional `route` (the title then opens that page), flex sizing (`basis`, `grow`) and a `body`: nested flex groups (`direction`, `basis`, `grow`, `items`) whose leaves are library symbols, labels, or kinds without an equivalent (counted gap boxes). Cards may instead carry `items` in card-body pixels. Section 3.2 gives the height of a row |

For an automation symbol the box is the 48 px symbol box; the generator adds the readout on the
side `readoutPosition` names and offsets the embed so the symbol keeps its place on the line. Where
the symbol's identifier is longer than the default readout holds, the generator widens the embed by
what the identifier needs, up to 16 characters (page 06 section 2, Table 1a): the symbol keeps its
place, and a tool that spaces symbols reads the width from the profile.

Every other kind is drawn in the box the descriptor gives, so the descriptor gives a box the block
fits. The profile states the size each kind needs: `size` with every flag at its default, `sizes` for
the flags that need more (a readout with `hasTag` needs 72 by 40 px, where its default is 72 by
24 px), and the width an identifier of n characters needs (`identifier`). Gate G5 warns of a box that
is smaller (section 5).

A readout is the exception (`grows` of the profile). A readout with its identifier in a box of the
default size had its value cut at the top and its identifier at the bottom, which no ellipsis
mends, so the generator grows a box that is too small about its centre (`screen.grown_box`): to the
size the flags need, and to the width the identifier needs, up to 16 characters. The readout stays on
its line, the pipes still end at the sides of the box the descriptor gave, and a box that holds its
readout is used as given.

An embed is widened for its identifier only into the room the next symbol leaves
(`screen.embed_limits`). Two symbols stand on one row when the boxes they have without the widening
share more than 4 px down the page (`diagram.overlap` of the profile, the tolerance of gate G5).
Where the widened embeds of two such symbols would lie over each other, they share the gap between
those boxes: each takes half, and where one needs less than half the other takes the rest. An embed
centred on its symbol, or a readout centred on its box, gives up at both sides what it lacks at one.
The identifier that does not get its width ends in an ellipsis and gate G5 names it; before, the
identifiers of two lamps 80 px apart ran together as one text. A tool that wants no warning gives
each symbol the width its embed needs (page 06 section 2).

A static tank (`"static": true`) whose descriptor gives no `max` shows no capacity: the generator
sets `hasCapacity` false, since the default of `max` is no capacity of any vessel (page 06
section 4.2).

The kinds are those of `library/profile.json`: `pump`, `motor`, `fan`, `valve`, `analogvalve`,
`damper`, `filter`, `switch`, `indicator`, `tank`, `readout`, `instrument-field`, `controller` and
`sequence`. The profile gives each kind's default size, the sizes its flags need, the width its
identifier needs, and for an automation symbol the box its embed occupies on each readout side
(page 06 section 2), so a tool can place symbols from the profile alone.

### 3.1 The Device Model

A device of a source project seldom carries every member a faceplate can show, and its alarms may
stay on source tags outside its folder. The device model (`cadre-hmi-devices/1`,
`schemas/devices.schema.json`, option `--devices-file`) states what each device's tag folder
carries. A build without one behaves as before.

```json
{"schema": "cadre-hmi-devices/1", "tagRoot": "[default]cadre_hmi_x",
 "devices": [{"id": "P1", "kind": "pump", "title": "P-1", "label": "Deep well pump 1", "unit": "",
   "members": {"state": {"type": "Boolean", "access": "read"},
               "cmd": {"type": "Boolean", "access": "write"},
               "mnt/errorMask": {"type": "Boolean", "access": "write"}},
   "alarmSources": ["prov:default:/tag:ctig/SITE/P1_OE:/alm:*"]},
  {"id": "F1", "kind": "sequence", "title": "FLT-1", "label": "Self cleaning filter",
   "members": {"step": {"type": "Int4", "access": "read"},
               "stepText": {"type": "String", "access": "read"},
               "trigger": {"type": "Boolean", "access": "write", "pulse": true,
                           "caption": "Start cycle"}},
   "trend": ["step"]}]}
```

The example passes gate G7 devices. Until revision E of this page its pump listed one member of a
force and a trended member it did not carry, both of which the gate refuses (Table 4).

Table 2. Keys of a device.

| Key | Content |
|---|---|
| `id` | The device's tag folder under `tagRoot`: the string a symbol's `device` resolves to |
| `kind` | A device kind of the library profile (`deviceKinds`): `pump`, `motor`, `fan`, `valve`, `analogvalve`, `damper`, `tank`, `instrument` (`readout` and `instrument-field` open the same faceplate), `controller`, `indicator`, `sequence` |
| `title`, `label`, `unit` | The identifier, the description and the unit of the device index, where given; else those of the descriptors |
| `members` | Every member the folder carries that the faceplate reads, by name relative to the folder, each with its `type` (the tag's data type) and `access`, `read` or `write`. A pulse command also carries `"pulse": true`, and may carry a `caption`, the text of its button: one line of 1 to 32 characters, with no space at either end; the profile lists the pulse members of each kind (`pulses`) |
| `alarmSources` | The source patterns of the device's alarms. Left out, the alarms are those under the folder; given empty, the device has no alarm |
| `trend` | The members the tag model historises. Left out, the tag model says it |

What the generator does with it:

1. **Device index.** For a device the model names, the entry of `session.custom.devices` takes the
   kind, identifier, description and unit the model gives, and gains `sources`, `write` (the
   members marked `write`), `members` and, for a device with pulse members, `pulses` (each member
   with the caption of its button, the member's name where the model gives none; page 13 section
   9.7). The index lists the devices the descriptors draw: a
   device of the model that no page draws is checked by gate G7 devices and is not listed.
2. **Alarms.** The faceplate's count and list, and the row of the alarm menu that opens a device,
   use the `sources` (page 13 section 3).
3. **Writes.** A checked write refuses a member that is not in the device's `write` list, and the
   faceplate hides or disables its control (page 13 sections 9.1 and 9.3). The generator also sets
   `session.custom.deviceModel` for a build with a device model: a device of such a project whose
   entry carries no `write` list may write nothing.
4. **Trend index.** A device whose entry carries `trend` gets one trend card per member listed.
5. **Test tags.** For a build that generates its tags, a device of the model gets exactly the members
   the model lists, in the model's types.

### 3.2 The Height of a Row of Cards

A row of a cards page is as high as its tallest card needs, the rows stand at the top of the page in
their order, and a page whose rows are together taller than the viewport scrolls. Before 2026-10-11
the rows shared the height of the viewport, so the cards of a page with little content stretched to
it and their content stood in the middle, far below the titles.

The generator computes the height from the descriptor and the sizes the library states
(`screen.row_height`): a card needs its title (40 px, where it has one), its body and 8 px of padding
beneath it, and a row adds the cards' margins of 8 px above and below. A body needs what its groups
need by the arithmetic of the flex containers the generator writes: across a group of direction `row`
the tallest item; down a group of direction `column` the items and the 4 px gaps between them, where
an item that grows takes its share of the space left, so the column is as high as the item that needs
the largest share asks. A leaf needs one line of 16 px for a label, 92 px for an automation symbol
with its readout beneath or above it (48 px with the readout beside it), and for any other kind the
height the profile states for its flags (64 px for an instrument field, 216 px for a tank); an item
with a `basis` in px down a column takes that height. A card of `items` needs its `bodyHeight`.

A kind the library lacks is drawn as a gap box, which has no size of its own. A row with such a card
shares the height the page has left, as every row did before, and the page then does not scroll.

Table 2a. Heights of the rows of the water treatment overview (`screens/wtp/overview.json`).

| Row | Cards | Tallest body | Row |
|---|---|---|---|
| 1 | Production, Water quality (instrument fields) | 64 px | 40 + 64 + 8 + 16 = 128 px |
| 2 | Storage (tanks), Pumps (pumps with a readout beneath) | 216 px | 40 + 216 + 8 + 16 = 280 px |

## 4. What the Generator Does

1. **Contract check (G7).** Every symbol kind resolves to a library view; every static or bound
   parameter is in that view's contract; a device binds its state, its speed, its value, for a
   controller its setpoint, output and loop mode, and for a sequence its text and step number, inside
   its own tag folder, by the rule of the
   device's kind (the faceplate contract, page 06 section 5). An unknown parameter or a broken faceplate
   contract is an error and stops the build; an unknown kind becomes a dashed, labelled gap box,
   counted in the report.
2. **Bindings.** A gate parameter (`on` or `open`) is bound once on the view (`custom.g_<id>`,
   a direct tag binding) and read by both the symbol and the pipes; other parameters bind directly
   to their tags. Relative members resolve under `tagRoot`; nothing else is invented.
3. **Routing.** A pipe end on a symbol side meets the holder ring of an automation symbol (18 px
   from the centre) or the edge of any other box; at the left, the right and the top of a static tank
   it meets the tile, which lies inside the box (page 06 section 4.2). Without via points the route
   is a Z between two ends that leave on the same axis and an L otherwise; via points add orthogonal
   elbows. The table `diagram.ROUTES` names the shape for each pair of axes, and the library profile
   publishes it with the ring's radius (`diagram` of the profile, page 06 section 2), so a tool that
   must know where a pipe will run reads it and restates nothing.
4. **Flow (decision COBD-006).** The process graph has tanks (source and sink), free ends marked
   `arrow-in` (source) or `arrow-out` (sink), gates (valves on `open`; pumps, motors, fans,
   switches and dampers on `on`) and pass-through nodes. Every simple path from a source to a
   different sink is enumerated; each pipe's condition is the minimal OR of the AND of the gates on
   the paths through it, written as one expression on the pipe's inner stroke. A closed pipe blocks.
5. **Drawing.** All pipes of a screen are one `ia.shapes.svg`, two paths each: a 6 px outline in
   `--automation-pipe-tertiary-color` and a 4 px inner stroke, `--automation-pipe-primary-color`
   while the medium flows (or the medium's colour in colour mode) and
   `--automation-pipe-primary-inverted-color` while empty, the package line drawing.
6. **Frame and project.** The screen root carries the palette class and a scrolling canvas; the
   diagram toolbar toggles colour mode, identifier tags and readouts. The child's page
   configuration and session props merge the parent's frame with the screen's route and
   navigation item; `--alarm-scope` writes the session's alarm scope (page 06 section 5). For a
   test build a tag document lists every bound member and the faceplate members of every device
   (for a device of a device model, the members the model lists); `--tags-file` imports an external
   tag model instead, before the project.
7. **Render target.** `--render module` draws pumps and tanks with the components of the Cadre
   package module (page 12) instead of the library views; the descriptor does not change. G1
   then validates the module components against their generated schemas. A kind without a module
   component, the controller, the indicator and the sequence among them, is drawn with its library
   view under either target. The module's tank has no property that hides the capacity line, so a
   static tank without a capacity is drawn with the library's own tile under this target too
   (`kinds.tank.moduleExcept` in the library profile). The module's pump always prints a speed and
   its tank always prints `m³`: a pump with no speed and a tank in another unit are drawn with
   their library views as well (`moduleNeeds`).

## 5. Gates

Table 3. The gates. G0 to G7 run offline before any import; G8 to G11 run against the gateway.

| Gate | Checks | Tool |
|---|---|---|
| G0 descriptor | Each descriptor validates against its JSON Schema, and the device model, when one is given, against `schemas/devices.schema.json` | `tools/hmi/screen.py` |
| G1 registry | Every view of the child and the parent passes the Ignition-Wiki validator: component types, declared props, enumerations, position keys, binding keys. The validator reads the top level of a component's props; the gate also walks the levels below it against the same registry: a text value outside the enumerated domain of its property, a key a closed object does not declare, and a bound property path a closed object does not declare (for example `plots[].trends[].interpolation` of the time series chart). A part of a schema the walk cannot follow is left alone. It does not read the values an expression may answer | `F:/repos/Ignition-Wiki/tools/validate_view.py`; `tools/hmi/gates.py` (`g1_registry`, `_deep_findings`) |
| G2 references | Every embedded view path, style class (also inside class expressions) and `var()` token resolves in the child or its parent | `tools/hmi/gates.py` |
| G3 view keys | View-level keys are `custom.` or `params.` (GF-07) | `tools/hmi/gates.py` |
| G4 project | Routes and docks name existing views; navigation items name existing routes; the parent is inheritable and is the child's parent | `tools/hmi/gates.py` |
| G5 layout | Symbol boxes inside the canvas and not overlapping (two boxes overlap when they share more than 4 px on both axes). Reported as warnings: overlapping readout areas (the embeds of two symbols whose default embeds already overlap); a block in a box smaller than the size its flags need (`sizes` of the profile: an instrument field with a setpoint and the enhanced value in a 96 by 64 px box); and an identifier, or the caption of an instrument field, wider than its embed, which then ends in an ellipsis. The last names an automation symbol or a readout only where the next symbol left the identifier no room or the identifier has more than 16 characters, since the generator sizes those embeds itself; a tank's identifier is measured against the share of the tile it takes (page 06 section 4.1) | `tools/hmi/gates.py` |
| G6 flow | The compiled expressions equal the reference solver on every gate state (exhaustive up to 12 gates, a seeded sample of 4,096 above) | `tools/hmi/diagram.py` |
| G7 contract | No unknown kind or parameter; every device binds inside its own tag folder; gaps counted. The faceplate contract: each device faceplate the child resolves carries its tab row, one pane per tab, the reset to the first tab, and one kind of alarm list narrowed by the device's source with no text filter. Every tag history binding references an array, and a property it references has a list default. Command security (COB-063): no script of a view (event, change script, transform, custom method, message handler, `runScript` expression) writes a tag or acts on an alarm directly or calls a private function of `cadre.hmi`, no script names `system` without a module or `cadre` other than as `cadre.hmi` or `cadre.icons` (an import, an alias or a lookup would hide the function called), no tag binding is bidirectional, every control whose script names a checked write, however the call is spelt, binds `enabled` to the permission of the write path it calls, alone or joined by `&&`, no checked write is called at view level, and every stock alarm table binds its own actions (`g7_commands`; NOTE-COB-04 section 11.5 item 8). Every `cadre.hmi` and `cadre.icons` name a script takes, however it is spelt, is one the library code the parent and the child ship defines (`ignition/script-python/cadre/<module>/code.py`, its top-level functions and constants; `library_names`), so a call of a function the library lacks fails the build (F050 of the ASMP study, COB-142); a confirmed command's path is read from the Confirm row's `p = self.view.custom.pending` (page 13 section 10.5). The gate reads the text of generated scripts: it is a check on generated views, not a defence against a script written by hand to evade it. With `--tags-file`, the interlock contract of every `ilk` folder (page 13 section 7), every trip latched (COBD-023), and every `cadre` name and `runScript` of a `cadre` function in the tag model's expressions and scripts resolved against the same libraries (`g7_tag_libraries`), since a tag runs in the gateway, where a missing function fails with nothing on the glass. The faceplate and command checks cover `Faceplate/Controller`, `Faceplate/Input`, `Faceplate/Sequence` and `Faceplate/SetpointRow`, and the checked functions `force`, `error_mask` and `pulse`. With `--devices-file`, G7 devices (Table 4) | `tools/hmi/screen.py`, `tools/hmi/gates.py` (`g7_faceplates`, `g7_history`, `g7_commands`, `g7_interlocks`, `g7_tag_libraries`, `g7_devices`) |
| G8 render | In a new session: no view error badge, no binding quality overlay, no trial page, no "View Not Found", components rendered; structural fingerprint and screenshot recorded | `tools/compare/capture.py` |
| G9 live flow | For each scenario the gate tags are written, the page opened in a new session, and every pipe's rendered state compared with the reference solver. For memory tag gates only; where the gates are expression tags of a simulation, G6 and G10 cover flow | `tools/compare/live_flow.py` |
| G10 functional | An operator's walk in a new session: navigation, faceplate, commands, setpoint, acknowledge, fault reset, palette, each checked on the glass (page 11 section 5); under module rendering the faceplate's package list display only, with no ACK (F10, COBD-025), ACK in the alarm menu with a row that opens a faceplate (F11), and ACK visible in the alarm menu (F14); a broken permissive that holds a pump, and a latched trip that holds P-502 after its fault clears until reset (F12); an instrument's limit written from its faceplate that raises its alarm, and its trend (F13); with nobody signed in, every command control disabled and a crafted click refused (F15), and no acknowledge path offered (F16); the test login of N-COB-9 signed in and commanding (F17), its name on an acknowledgement (F18, module rendering); the trend page's cards (F19). The commands run signed in; without the login only F1, F2, F6, F9, F15 and F16 run. Written for the water treatment sample; it starts from P-502's initial alarm state and restores the plant | `tools/compare/functional.py` |
| G11 faceplates | Every leaf view of every page clicked: each `device` of the descriptors opens the faceplate with its identifier as title, no other view does, and no faceplate shows a quality overlay or the empty body. Every tab of every faceplate is opened: no pane may be empty or show an overlay or an error badge; the Alarms tab lists only the device's alarms, as many as its label counts, and the expected rows of the plant's initial state (`--expect-alarms`). The tabs Maintenance, Tuning and Status are opened like the others, and a line naming a member of bad quality fails the sweep as an overlay does. With `--devices-file`, each faceplate shows the tabs its device's members give it, and each alarm row carries a source path under one of the device's source patterns, in place of the device's identifier | `tools/compare/faceplates.py`; `tools/compare/wtp_suite.py` runs G8, G11 and G10 for the water treatment sample |

`screen.py` runs G0 and G2 to G7 itself and refuses to import on any failure; `parent.py` runs G1
on the parent before importing it.

A warning fails nothing, and a tool can read every one. `screen.py` prints the warnings of each gate
beneath the gate's line, each as `    warning: <text>` (gate G5 and gate G7 devices have warnings
today), and writes the gates into its `--report` file beside the routes, under the key `gates`: each
gate's result as `tools/hmi/gates.py` reports it, with a `warnings` list on every gate, empty where
the gate has none, and `ok` for the whole. A route starts with `/`, so the key is never one, and
`gates.py --screen-report` reads the same file and skips it. A tool that must prove that a build has
no warning reads `gates` of the report and needs no second call:

```python
report = json.load(open("workspace/reports/pilot.json"))
clean = not any(g["warnings"] for g in report["gates"].values() if isinstance(g, dict))
```

A note is what a page shows that its descriptor does not state and that no layout can cure; today
there is one, the capacity line of a static tank under the module rendering (section 4 item 7).
`screen.py` prints each as `  note: <route>: <text>` and the route's entry of the report lists them
under `notes`. A note fails nothing and is no warning.

Table 4. Gate G7 devices: the device model against the library profile, the descriptors and the tag
model. The gate prints the number of devices and device symbols it checked, and its warnings.

| Against | Check |
|---|---|
| The library profile | No device is listed twice. The kind has a faceplate. Every member is a name the profile knows for the kind, and an unknown name is an error, never accepted in silence; an interlock member (`ilk/`) is known for a pump or a valve kind. The declared type suits the member: a Boolean and a String exactly, an integer member any integer type, a Float8 member any number. Every member marked `write` belongs to a write path. Every member of `trend` is a member of the device. A force is one whole encoding (`forceEncodings` of the profile): both members of the pair, or of the mode and the value, in one access, and not both encodings. Every alarm source names a tag: a pattern whose tag part is only wildcards is an error. A member marked `pulse` is a pulse member of the device's kind (`pulses` of the profile), Boolean and marked `write`; a caption stands only on a member marked `pulse`, is one line of 1 to 32 characters with no space at either end and no character that does not print, and is not the label of a faceplate tab, which an operator and the faceplate sweep would read as a tab; a pulse member of the kind that is marked `write` is marked `pulse`, since its faceplate draws its button |
| The descriptors | Every symbol marked `device` names a device of the model. The symbol's kind, or the `deviceKind` it carries, opens the faceplate of the device's kind. Every faceplate parameter the symbol binds points at a member the model lists. Any other parameter bound inside the device folder (`alert`, `badgeControl`) points at a member the model lists or, with a tag model, at a tag of the folder that the tag model carries; a name the library knows for the kind must be listed. A block that draws a setpoint, an output or a step number (`hasSetpoint`, `hasOutput`, `hasStep` true) belongs to a device that lists `sp`, `out` or `step` |
| The tag model (`--tags-file`) | Every device folder exists. Every listed member exists in the declared type. No member marked `write` is an expression tag, which refuses a write (GF-49). The folder carries no faceplate member that the model leaves out, since the faceplate would show it; a tag whose name the library does not know for the kind is outside the check |
| Warnings (reported, not failed) | An alarm source that another device's source also matches, by its own pattern or by its folder: the alarm is listed on both faceplates, and its row in the alarm menu opens the first of the two in the device index. An alarm source outside the build's `--alarm-scope`: the top bar and the alerts page leave its alarms out |

## 6. Commands

Run from the repository root. In Git Bash, set `MSYS_NO_PATHCONV=1` first (GF-15); PowerShell
needs nothing.

```bash
python tools/hmi/parent.py --out build --deploy
```

```bash
python tools/hmi/screen.py --project cadre_hmi_sample --descriptor screens/sample-pump-station.json --app-name Sample --out build --report workspace/reports/sample.json --deploy
```

```bash
F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/capture.py --base http://localhost:8088/data/perspective/client/cadre_hmi_sample --route /pump-station --out workspace/compare/sample
```

```bash
F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/faceplates.py --base http://localhost:8088/data/perspective/client/cadre_hmi_sample --descriptor screens/sample-pump-station.json --out workspace/sample/faceplates
```

```bash
python -m unittest discover -s tests
```

The fixture of the new kinds (a status only pump with the force and the mask, a pump with a run
command, a valve of the newer force interface, a controller with tuning, an indicator with the force,
an instrument, and a sequence with a pulse command), with its tag model and device model. It also
shows what the first page built from a plant's data showed: identifiers of 14, 15 and 16 characters
on a pump (`SupplyPump_No2`), a readout (`SupplyFlow_FT01`) and a lamp (`SuctionLowLvl_SW`), and a
static tank without a capacity (`Break tank`) with a pipe at each side:

```bash
python tools/hmi/screen.py --project cadre_hmi_pilot --descriptor tests/fixtures/pilot-supply.json --app-name Pilot --alarm-scope "*cadre_hmi_pilot*" --tags-file tests/fixtures/pilot-tags.json --devices-file tests/fixtures/pilot-devices.json --out build --report workspace/reports/pilot.json
```

```bash
F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/faceplates.py --base http://localhost:8088/data/perspective/client/cadre_hmi_pilot --descriptor tests/fixtures/pilot-supply.json --devices-file tests/fixtures/pilot-devices.json --out workspace/pilot/faceplates
```

The water treatment sample's commands are on page 11 section 8.

## 7. Use by the Cadre Tools

The descriptor is the interface. A tool that knows a screen's equipment, positions, connections
and tags writes a descriptor and calls the generator; the gates prove the result.

1. **ctig (Citect to Ignition).** The decoded page model already carries symbol positions, genie
   types and tag bindings. A mapping from genie type to library kind (the role of ctig's open item
   CIM-011, stock symbols) and from pipe primitives to `pipes` gives a descriptor per page, and the
   whole project inherits `cadre_hmi_base`. The devices of the source, with the members each one
   has, give the device model (section 3.1); `library/profile.json` states the kinds, members and
   write paths to map onto.
2. **New screens.** An engineer or an agent writes the descriptor directly; the schema and the
   contract gate catch mistakes before the gateway does.

## 8. Extending the Library

1. A two-state device with package artwork: add the icon names to `library/icons/ICONS.txt`, run
   `tools/convert_icons.py`, add one row to `DEVICE_KINDS` in `tools/hmi/library.py` and one to
   `KIND_VIEW` in `tools/hmi/screen.py`, and to `GATED` in `tools/hmi/diagram.py` if it gates flow
   (to `PASS_KINDS` in `library.py` if it does not). A device kind also needs its rows in
   `FACEPLATE_MEMBERS` and `OPTIONAL_MEMBERS` (`screen.py`) and in `FACEPLATE_VIEW`, `FACEPLATE_TABS`
   and `FACEPLATE_READS` (`framework.py`), a default in `MEMBER_DEFAULTS` of `cadre.hmi` for each new
   member, and its faceplate in `FACEPLATES` of `gates.py`; the library profile and gate G7 devices
   read those tables. A pulse member is one more name under `PULSE_PATH` in `FUNCTION_MEMBERS` of
   `cadre.hmi`: the faceplate that reads it draws its button.
2. Any other component: a function in `library.py` returning the view and its contract, registered
   in `library_views()`. Every component type it uses must exist in the Ignition-Wiki registry;
   G1 fails otherwise.
3. Rebuild the parent, run the unit tests, deploy the parent and the children, and verify in a new
   session (GF-10).

## 9. The Generated Operator Walk

### 9.1 Purpose

Gate G10 (`tools/compare/functional.py`) is written by hand for the water treatment sample: its device
identifiers and its scenario are in the code. A project generated from descriptors, a device model and
a tag model needs the same proof generated from the same data. `tools/compare/walk.py` writes a plan
from those files and the library profile, and runs the plan on the gateway. Its code is in three
modules: `walk_plan.py` (the plan, pure and offline, with the glass table and the number format),
`walk_run.py` (the runner, the tags and the negative controls) and `walk.py` (the command line, which
exports the names of both). The helpers both walks
share (signing in, opening a device from its symbol, the docks, buttons, tabs, entry fields, the alarm
menu, the reading of a symbol under both renderings, the quality checks) are in
`tools/compare/glass.py`; `functional.py` imports them and exports every name it exported before.

### 9.2 Commands

The plan is pure and offline: it reads no clock and no gateway, and the same inputs give the same
bytes. A plan is data that a person may read and overrule before a run. The run and the negative
controls need an interpreter with Playwright, as gates G8 to G11 do.

```bash
python tools/compare/walk.py plan --descriptor <file> [--descriptor <file>] [--devices-file <file>] [--tags-file <file>] [--source-tags <file>[@parent/folder]] [--source-folder [provider]folder] [--effects <file>] [--render stock|module] [--profile <file>] --out plan.json
```

```bash
F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/walk.py run --plan plan.json --base http://localhost:8088/data/perspective/client/<project> --out <folder> [--trial <seconds>] [--no-login]
```

```bash
F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/walk.py selftest --plan plan.json --base http://localhost:8088/data/perspective/client/<project> --out <folder> [--trial <seconds>]
```

Table 5. Options of the three commands.

| Option | Command | Meaning |
|---|---|---|
| `--descriptor` | plan | A screen descriptor; repeated for each page, in the order of the build. Required |
| `--devices-file` | plan | The device model the project was built with (section 3.1). Without one, the devices are those the descriptors' symbols name, and the members of each are the tags its folder carries in the tag model |
| `--tags-file` | plan | The tag model: a folder document lying at the provider's root, as it is imported. Without one, the plan uses the tags the generator would create for the descriptors |
| `--source-tags` | plan | A tag document that defines the sources of reference tags (section 9.6); repeatable |
| `--source-folder` | plan | A folder outside the descriptors' tag root that the walk may import into, written `[provider]folder` (section 9.6); repeatable. The plan records the folders as `sourceFolders` |
| `--effects` | plan | The effects file (section 9.5) |
| `--render` | plan | The rendering the project was built with, `stock` (the default) or `module` |
| `--profile` | plan | The library profile; `library/profile.json` by default |
| `--out` | plan | The plan file to write |
| `--plan` | run, selftest | A plan written by `plan` |
| `--base` | run, selftest | The client address of the project |
| `--out` | run, selftest | The folder for `walk.json` or `selftest.json` and the screenshots of failed rows |
| `--trial` | run, selftest | The seconds of trial the run needs, 1,200 by default. With fewer left the command waits for the expiry and resets (GF-33), then probes a fresh session until it no longer shows the trial page (section 9.9) |
| `--no-login` | run | Walk with nobody signed in although a test login exists |

The exit code of `plan` is 1 when the effects file is not valid or a source folder is not written
as `[provider]folder`. The exit code of `run` is 0 for the
verdicts `PASS` and `PASS, READ ONLY` and 1 for `FAIL`; that of `selftest` is 1 when a control that
applies did not fail, when nobody signed in, or when something could not be restored.

### 9.3 Groups of Steps

Table 6. The groups, in the order a run takes them.

| Group | Steps | Pass condition |
|---|---|---|
| N navigation | Every route by the entry of the navigation menu that carries its label, and each card title that links a page. A menu step begins on another route | The address is the route, the top bar reads the page's name, the page shows what belongs on it (the step's `symbol` or `holds`, below), it holds components outside the docks, and it shows no quality overlay, no error badge, no "View Not Found" and no trial page |
| D devices | For each device kind, the first device in document order, opened from its symbol | The dock's header reads the identifier and the description, the tabs are those the device's members call for (`framework.expected_tabs`, as gate G11), and no row reads "Refused" |
| T trends | The trend page; the Trend tab of the first trended device of each kind whose faceplate has one (a kind without a Trend tab, an indicator, is listed in the plan under `trendTabAbsent` and its history is read on the trend page alone) | One card for each historised member, each drawing a line; as many series drawn as the device has trended members. T runs before C, so that no sample the walk itself wrote draws a line |
| C capabilities | For each device kind and each write path one of its devices can use, the first such device: the action as an operator performs it, then the action that puts it back | Section 9.4. A step reads the state first and visits every other state, so no step passes without a write |
| R refusals | For each step of C, in the session with nobody signed in | The control is disabled; a crafted action on it reaches the gateway, which answers with a refusal; the tag and the glass are as before |
| A alarms | An instrument's or a tank's limit written beyond its value, where the tag model binds an alarm's setpoint to the limit; an alarm scene of the effects file | The Alarms tab counts and lists one more alarm of the device, the top bar's count and its menu show it, it is acknowledged and reads acknowledged, and after the clear both counts and the tag are as before |
| P parity | Two scenes of values, imported as whole tag definitions, for every tag a symbol parameter is bound to and the walk can set | In each scene every symbol shows its value under its own format; a state shows the text or the icon of its kind |

The address and the top bar's page name are one fact: the name is computed from the route
(`cadre.hmi.page_title`), so neither tells a page from a blank view under the right address. A step
of group N therefore names what the page must show. On a page of a descriptor it is `symbol`, the
text of the first symbol of the page that shows one (an identifier, or the label and unit of an
instrument field). On the two pages of the frame, which carry no symbol of a descriptor, it is
`holds`, a component the page must show outside the docks and outside a popup: a time series chart
on the trend page (one for each card) and the alarm status table on the alerts page (measured on
2026-10-11 on the fixture and on both renderings of the sample; no other page holds either). A page
of a descriptor none of whose symbols shows a text has neither, and is proven by its address and its
count of components alone.

A device can use a write path when it carries the member, a device model marks the member `write`,
and the tag is not an expression tag (GF-49). Three kinds of step hold a state while they act.

1. **The fault reset (W5).** The button shows only while the device is faulted, so the step raises the
   fault itself by a tag import where the fault is a memory tag, acknowledges its alarm, runs the
   refusal of the same button while the fault stands, and then resets. The definition the fault's tag
   had before the step is kept first and imported back afterwards, also for a device found faulted.
2. **The manual output (W14).** The field is enabled only in manual, so the step sets the loop to
   manual first and back to automatic afterwards. Its refusal runs while the loop is in manual and
   fails when it is not: in automatic the field is shut for every user, and a refusal there would
   prove the mode and not the role.
3. **The pulse command (W18).** A pulse leaves nothing in its own tag where the plant returns it, and
   its button reads the same before and after. The step presses the button found by its caption (the
   device model's `caption`, else the member's name) and passes on what the effects file names for it:
   a member whose tag holds another value than before (`changes`) and a member's own reading on a
   symbol that leaves its resting text and returns to it (`leaves`, `returnsWithin`). The faceplate's
   row `Step` is recorded beside them. Without an effect the member itself must be read true. Where
   the effects file says that the plant returns the member (`returns`), a member that is still true
   once the effects are met fails the step. Whatever the verdict, a member nothing returned is put
   back by an import of its definition of before. The refusal of a pulse watches the tags the effects
   name, the row and every line of the block, since a pulse that arrived and was returned leaves its
   own member false and nothing of the block may move.

4. **A command button of a page (W18).** A descriptor's `buttons` of the type `pulse` (wiki page 05 section 5.1) are a
   step of their own, `page-pulse`, on the page that holds them, with the question and the length of the pulse the
   descriptor gives. The step reads the tag false, presses the button and finds the question with Confirm and Cancel
   in its place and the tag still false, presses Cancel and finds the button back and the tag still false, presses
   again and Confirm, and reads the tag: true, held about the length asked (within a second and a half under and
   three seconds over, since the tag is read through the gateway's export), and false again. The button must then
   read its caption and no refusal. A tag left true is imported back from its definition of before. Its refusal
   (`page-refusal`) loads the page with nobody signed in: the button is disabled, and the handlers the client holds
   for the button and for Confirm are called directly (a click on a disabled button runs no script, GF-45), which
   must make the gateway refuse on the button with the tag unchanged. A button of the type `faceplate` or `route`
   writes nothing and has no step.
5. **A configuration row (W19).** In the `asm` style a device model's `config` member is a row of the Config tab: an
   entry step with the caption, format and bounds of the model, run as any entry (a value typed and set, the tag
   read, the value put back). A device with modes takes a configuration change in its maintenance mode only, which
   no step enters: its rows are listed under `notReached` with that reason. The Set of a crafted entry shows about
   a second after it (GF-91), and the refusal waits for it.

A pulse that moves a flag of the plant which nothing returns (a sequence's in service flag) names the flag in the
effects file under `restores`; the step keeps its definition before the press and imports it back afterwards, so
that the walk leaves the plant as it found it. A pulse whose only effect is the strobe of a PLC bit for a few
milliseconds leaves nothing to read, and the tag model of the project stamps the time of the command on a tag of its
own (`startAt`, `resetAt` and the like), which the effects file names as a member that `changes`. The Service
completed command of the generator stands on the Config tab, and the plan says so (`walk_plan.PULSE_TAB`).

The plan lists under `notReached` every write path no step reaches, each with its reason: the top
bar's ACK (W6) and ACK visible (W9) acknowledge alarms of the plant, and the trip reset (W11) needs a
state only the plant's logic produces; gate G10 covers the three on the sample.

### 9.4 Evidence

Each row of a result states where its evidence came from.

1. **The glass.** The text an operator reads on a surface other than the control operated: a value row
   of the faceplate, a line of a symbol, the icon a controller block shows, an alert frame, the bound
   state of a module component's element. Whether the module's component or the library's view draws
   a pump or a tank under the module rendering is the generator's own rule (`screen.module_draws`):
   a pump with no speed and a tank in a unit the module cannot show are read as library views.
   An entry step waits for the value it puts back as long as it waited for its effects.
2. **The tag.** The gateway's export of the tag (`deploy.export_tags`). A memory tag exports its live
   value; a reference tag is followed to its source; an expression tag exports no value.
3. **The control.** The control the step operated: the field that was typed into, the disabled state of
   a button. It is recorded and is never sufficient.

A step whose only evidence is the control it operated fails. An entry step (W3, W4, W12, W14, W15)
passes only when the tag holds the value typed or a symbol or an effect of the page shows it: a
setpoint field keeps the text typed into it whether or not the write was made (GF-56). A symbol or
an effect counts as that second surface only where it can tell. Each is read before the write
against what the value to be typed calls for, and one that agrees already (a symbol whose format is
coarser than the step, a bound the plant met before) is still checked afterwards and is no evidence
of the write; the row lists it under `read the same before the write`. The plan makes the step of an
entry at least one unit of the coarsest format among the symbols and the effects that show the value
typed, so that a symbol of the member can tell. A read of a tag that the gateway fails (anything but
a tag it does not carry) fails every row of the step it happened in.

A refusal proves that the gateway refused, and not only that the client disabled a control.

1. **An entry.** The `disabled` and `readonly` flags are removed in the page and the value is typed
   and committed. The commit runs the row's script, and the row must then read "Refused", the answer
   of `cadre.hmi.command`.
2. **A button.** A click on a button with its `disabled` flag removed runs no script (GF-45): the
   client drops a click on a button whose properties say disabled. The walk therefore also calls the
   click handler the client holds for the button directly, which does run the button's script in the
   gateway (GF-59, measured 2026-10-11 on `cadre_hmi_pilot` with nobody signed in). The faceplate's
   message line must then read the refusal.
3. **The comparison.** The tag is compared before and after where it can be read; the symbols of the
   page that show the member, and another row of the faceplate where the plan names one, must read as
   before.

Each refusal row carries `refused_by`: `the gateway` when the answer was read, `the client only` when
a button's handler could not be called and no script ran, and `nothing` when a crafted action got no
answer; the last two fail the row. A row's note and a faceplate's message line stay until the next
accepted write, so before a refusal step acts on a device that an earlier step of the walk had
refused, the walk shows another device in the faceplate and comes back; a refusal still shown after
that fails the step. A faceplate that reads "Refused" on a row before a step acts, without the walk
having caused it on that device in that session, fails the step.

Every state changing step puts back what it changed in a `finally` clause, so a step that breaks
leaves the device as found. A tag the walk changed by import is restored from the definition the
gateway exported before, and the restore is verified: the tag is exported again and must equal the
definition imported. What could not be restored is listed under `unrestored` and fails the run. The
walk imports only below the plan's `tagRoot` and the source folders the plan names (`sourceFolders`,
section 9.6); a reference chain or an effects file that leads to another folder is refused by the
code.

### 9.5 The Effects File

The optional effects file (`cadre-hmi-walk-effects/1`) carries what only the plant's logic or a
simulation decides. Without it a capability step checks that the write arrived and that the glass
shows the member written. `screens/wtp/walk-effects.json` is the file of the water treatment sample
and `tests/fixtures/pilot-walk-effects.json` that of the fixture of the new kinds.

Table 7. Keys of an effects file.

| Key | Content |
|---|---|
| `schema` | `cadre-hmi-walk-effects/1`. Required |
| `about` | Free text for the reader; not read |
| `tagRoot` | The tag folder under which the relative members of `expect` resolve, for example `[default]cadre_hmi_pilot` |
| `choose` | A list of choices. Each names `kind` (a device kind), `path` (a write path) and `device` (the device's identifier in the device model, or its folder's name without one): the device the kind's step for that path uses in place of the first in document order. `why` is free text |
| `effects` | A list of effects, each of the keys below |
| `effects[].device` | The identifier of the device acted on. Required |
| `effects[].path` | The write path of the action. Required. One of the paths whose step reads effects: `W1`, `W2`, `W3`, `W4`, `W10` and `W12` to `W19`. The fault reset (`W5`) reads none, and no step is generated for `W6` to `W9` or `W11` |
| `effects[].value` | Narrows the effect to one state written: `true` or `false` for a command, `"on"`, `"off"` or `"auto"` for a force. Without it the effect applies to every state |
| `effects[].member` | Narrows the effect to one member of a path that has several (a setpoint path, a pulse member) |
| `effects[].within` | The seconds allowed for the effects of the action, a number above 0. A step waits for the longest `within` of its effects and never fewer than 8 seconds (`walk_plan.WAIT_FLOOR`: the faceplate polls its device once a second and a symbol follows its tag), so a value below 8 changes nothing; 8 by default |
| `effects[].returns` | `true`, on a pulse (W18) only: the plant returns the pulse member to false by itself. The step then fails when the member is still true 8 seconds after its effects were met |
| `effects[].restores` | A list of tag paths (relative to `tagRoot`, or beginning `[`), on a pulse (W18) only: the plant's own flags that the command moves and nothing returns. The step keeps each flag's definition before the press and imports it back after the step, and fails when one cannot be put back |
| `effects[].expect` | A list of expectations. Each names `member` (a tag path relative to `tagRoot`, or a full path beginning `[`) and exactly one of the keys below (`min` and `max` count as one) |
| `expect[].value` | The symbol of the step's page that binds the member shows this value under its own format |
| `expect[].min`, `expect[].max` | The number that symbol shows lies within the bounds |
| `expect[].written` | `true`: that symbol shows the value the step wrote |
| `expect[].changes` | `true`: the member's tag, read through the gateway's export, holds another value than before the action. The member needs no symbol. In a step of any type |
| `expect[].leaves` | `true`: the member's own reading on that symbol is otherwise than before the action. In a step of any type |
| `expect[].returnsWithin` | With `leaves`, on a pulse (W18) only: a number of seconds within which the reading must be as before again |
| `alarmScenes` | A list of scenes, each of the keys below |
| `alarmScenes[].device` | The identifier of the device whose faceplate lists the alarm. Required |
| `alarmScenes[].tag` | The full path of the tag that carries the alarm. Required |
| `alarmScenes[].raise`, `alarmScenes[].clear` | Whole tag definitions of that tag, each with its `name`, imported at the tag's folder to raise and to clear the alarm. Required |
| `alarmScenes[].member` | The device member whose symbols show the alarm (an alert frame) |
| `alarmScenes[].text` | The alarm's label, by which a row of the frame's list is recognised |

An expectation with `value`, `min`, `max`, `written` or `leaves` is resolved at planning time to the
symbols of the step's page that bind the member. A member no symbol of that page shows is listed
under `effectsUnseen` and is not checked. `walk.py plan` refuses an effects file whose expectation
states none or several of the keys, whose `written`, `changes`, `leaves` or `returns` is not `true`,
whose `within` is not a number above 0, which gives `returns` or `returnsWithin` to an action other
than a pulse, or which names a write path whose step reads no effect. An effect that names a device
or a member no step of the plan acts on is not refused and is not checked: the plan does not list
it.

An expectation with `changes` or `leaves` is compared with what was read before the action, in a
command or mode step (for each state it names), in an entry step and in a pulse step alike. The
runner reads the tag or the reading before it acts, and a step whose tag or symbol cannot be read
then fails without acting. A reading that `leaves` is the member's own and nothing else of its
symbol: a line is found by the prefix and the suffix of its format, a state by its two texts, an
icon by its two icons, a module component by the property bound, and a text a symbol writes as it is
(the step text of a sequence block) by being neither a line the symbol draws from its parameters nor
the line of another bound parameter. Another line of the same symbol that moves does not meet the
expectation.

### 9.6 Source Tags

A member of a device is often a reference tag whose source lies outside the tag model. The walk can
read and set such a member only where it knows the source, so `--source-tags` gives the plan further
tag documents. The option takes `FILE`, a folder document lying at the provider's root, or
`FILE@parent/folder`, a folder document whose root folder lies below `parent/folder`. A document
fills in only the tags the tag model does not define. The keys of a tag the plan reads are those of
Table 8; a document may carry any other key.

A source tag document says where a value lives. It does not allow the walk to write there: the
runner imports only below the plan's `tagRoot`, the tag root of the first descriptor. A parity
reading whose value lies in a tag outside that folder is listed under `parity.notChecked` with the
folder as the reason, and a fault reset or an alarm scene whose tag lies outside it is listed under
`notReached`; a step that only reads such a tag, or types into a field bound to it, is planned as
before. A plant project's device layer is commonly reference tags on a source layer in another
folder, so `--source-folder [provider]folder` names a folder the walk may import into, once for each
folder. The plan records the folders named as `sourceFolders`, sorted, and the runner allows the tag
root and exactly these. A source folder is never inferred from a source tag document, and a
provider's root (`[default]`) is refused. Without the option `sourceFolders` is empty and a plan is
otherwise as it was. A walk restores every tag it imported from the definition the gateway exported
before, in a source folder as below the tag root (section 9.4); the owner of a source folder decides
whether a walk may be given it.

Table 8. Keys of a tag in a tag model or a source tag document, as the plan reads them.

| Key | Use |
|---|---|
| `name` | The tag's or the folder's name: a path is the names from the root joined by `/` |
| `tagType`, `tags` | A node with `tagType` `Folder`, or with `tags`, is a folder; every other node is a tag |
| `valueSource` | `memory` (the default), `expr`, `reference`, `opc`, `db` or `derived`. Only a memory tag is set by a scene, and only a memory tag exports a value |
| `sourceTagPath` | For a reference tag, the path of its source: absolute (`[default]folder/tag`) or relative to the tag's folder (`[.]tag`, `[.]../folder/tag`, GF-46). A chain of references is followed to its end |
| `dataType` | `Boolean`, `Float4`, `Float8`, `Int1`, `Int2`, `Int4` or `Int8` for a tag of a parity scene; a Float4 is formatted from its 32 bit value |
| `value` | The configured value: the centre of a scene's range where the tag states none, and the state a Boolean returns to |
| `engLow`, `engHigh` | The range a scene's two values are taken from |
| `alarms` | A tag that carries an alarm is not set by a parity scene. An alarm of mode `AboveValue` or `BelowValue` whose `setpointA` is bound to `{[.]<limit member>}` gives a step of group A |
| `historyEnabled` | A historised member of a device gives a card of the trend page (the generator's trend index) |

### 9.7 Parity

Parity does not set an expression tag, a reference whose source no document defines, a tag that
carries an alarm (a scene would raise and clear it), a text tag, or a symbol that shows no text by
which it can be found. Each is listed under `parity.notChecked` with its reason. A number's two
values lie in the range the tag states or, without one, within a tenth either side of its configured
value; every number of a plan is distinct, and none sits on a rounding tie.

A reading is a check only where the glass can tell. A reading whose two scenes give the same text (a
range narrower than one unit of the format) is listed as not checked, and so is a reading that
another tag's reading on the same symbol matches in a scene. The runner fails a reading that both
scenes of a plan expect alike, for a plan edited by hand. A module component is read from the
bound property of its element, which is the tag's value and not a formatted text: it must agree to
the precision of a Float4.

The walk's formatter implements the Java decimal patterns the descriptors use (`0`, `0.0`, `0.00`,
`#,##0`, `#,##0.0` and their like, rounding half even) and refuses any other pattern in place of a
guess. It also refuses the values for which Java's `DecimalFormat` was measured to differ from that
rule (JDK 17.0.20.1, 2026-10-11): a value other than zero below one unit of the pattern, a negative
zero, and a magnitude of 1e15 or more.

### 9.8 Negative Controls

`walk.py selftest` runs checks where each must fail, through the code of the real check, and fails
itself when one passes. A control holds only when the row of its step failed and the row's detail
names the reason the control stands for (`walk_run.control_verdict`): a step that fails because a
faceplate did not open, a button was disabled or a row read a stale refusal proves nothing of the
check. A control the plan has no step for is reported as not applicable. A control that wrote a
value reads the tag until it holds the value of before again, for a bounded time, and reports
`put_back`; a put back that does not hold fails the control.

Table 9. The negative controls.

| Control | What is run | Why it must fail | What the row must name |
|---|---|---|---|
| `route` | The first menu step of group N, begun on its own route | The entry moves nothing | `the step began on the route itself` |
| `route-content` | The same step, told to expect the symbol of another route's step (one the page was seen not to show) and the component another page must hold | The address and the top bar are right, the content is not | `no symbol of the page shows`, `the page holds no`, each where it applies |
| `parity` | Scene 1 imported, scene 2 expected | Every reading differs between the scenes | Every reading fails, and the scene arrived |
| `refusal` | A refusal step in the signed in session, without a crafted action | Its control is enabled | `enabled` |
| `refusal-write` | A refusal step of an entry in the signed in session, with the crafted entry | The session may write, so the tag differs afterwards; the value of before is typed back | `the tag went from` |
| `capability` | A `states` step whose click is skipped | Neither the glass nor the tag changes | `, expected ` (the state not shown after the button) |
| `entry` | An `entry` step whose typing is skipped | The field and the tag keep the value | `after ` (the value not held after the entry) |
| `pulse` | A `pulse` step whose press is skipped | No effect follows | `no effect on `, or `was not read true` for a pulse without effects |
| `entry-blind` | An `entry` step that no symbol follows, written for real, with the reads of the tag withheld | Only the field typed into shows the value | `only the field typed into` |

### 9.9 Results and the Suite

A run writes `walk.json` (`cadre-hmi-walk-result/1`): one row for each step and each parity reading
(`id`, `group`, `path`, `device`, `done`, `expected`, `glass`, `tag`, `evidence`, `ok`, `detail`, and
`refused_by` on a refusal), the counts and the kinds of evidence by group, the steps not run
(`not_run`), the steps of the plan that left neither a row nor an entry in `not_run` (`missing`, each
with its reason), what was restored and what was not, the tag reads that failed, and a screenshot for
each failed row.

The result is reconciled with the plan. A plan is data that a person may overrule, and a refusal
that another step holds (W5, W14) is run by that step alone: where the holding step was deleted from
the plan, or broke before it reached its refusal, the refusal leaves no row. Such a step is listed
under `missing` and fails the run. A parity step is accounted for by a row for each of its readings.

The verdict is `PASS` when every row passed in a signed in session, every step of the plan is
accounted for and nothing is left to restore.
Without the test login (NEEDS N-COB-9), or with `--no-login`, the read only groups N, D and T and the
refusals R run and the verdict is `PASS, READ ONLY`: the write groups C, A and P did not run, which
is no pass of them, and the refusals that another step holds (W5, W14) did not run either. A test
login that is given and does not sign in is a failure.

Before a run, and before each gate of the suite, the trial is asked for and a fresh session is probed
until it no longer shows the trial page (`walk.settle_trial`). For about a minute after a reset the
REST route reports a healthy trial while a new session still shows "Trial Expired"; gate G8 once
measured that page as six routes with no component. The probe is bounded (twelve probes fifteen
seconds apart, then the trial asked for again, twice in all), and a trial page that stays fails the
gate by name.

`tools/compare/wtp_suite.py` runs the generated walk after gate G10 on both renderings of the water
treatment sample, with the plan built from `screens/wtp/*.json`, the plant's tag model and its effects
file. The plant is restored before the walk and, in a `finally` clause, after it; the last restore is
verified by an export of the plant's folder against the tag model (`verify_plant`). The suite also
restores the plant between two steps whenever four minutes have passed since the last restore
(`keep_initial`): left alone, the sample raises an alarm of its own, because P-502 starts faulted and
the potable water tank TK-501 then reaches its high limit some six minutes after a restore. With a
test login on the machine the suite fails a walk in which nobody signed in; without one it passes
read only and says so.

### 9.10 The Glass Table

What the walk must know of the glass (the caption of each command button, the label of each row and
field, the tab each control is on, the state texts of each kind) is a table in `walk_plan.py`
(`glass_facts`). `tests/test_walk.py` pins every entry against the views the generator's code writes
now (`framework.framework_views`, `library.library_views`) and against the generator's own tables
(`FACEPLATE_TABS`, `MEMBER_BOUNDS`, `LIMITS`, `DEVICE_KINDS`), pins a row's state texts against the
expression of that row, and checks that the views of the build folder are those the code writes. A
library change that renames a caption therefore fails a unit test before it fails a walk on the
gateway. A write path the library gains after the table was written is listed under `notReached` as a
path the table has no entry for.

### 9.11 Limits

1. A device is found on the glass by the identifier its symbol shows (an instrument field by its
   label and unit). A device whose symbols show none is listed under `notReached` and gets no step.
2. A write path is exercised on one device of each kind, the first in document order that can use
   it, not on every device.
3. A refusal proves that the session with nobody signed in cannot write through the control. It does
   not prove what a signed in user without the role may do: the gateway has one role (COBD-024).
4. The steps of groups N, D and T have glass evidence only: no tag states which page a session shows,
   which tabs a faceplate draws or what a chart plots. The trend checks read whether a line is drawn,
   not whether its values are right. A step of group N proves the alerts page by its alarm status
   table being shown, not by what the table lists.
5. Parity reaches only members whose value lies in a memory tag the walk was given. On the water
   treatment sample every bound member is an expression tag, so the sample has no parity check.
6. The walk raises no alarm through the plant's logic and operates no interlock beyond a bypass. An
   acknowledgement has no refusal step.
7. An earlier refusal is cleared from a faceplate by showing another device in it, so a plan with a
   single device can run one refusal on it and no more.
8. The refusal of a pulse compares every line of the device's block before and after. A block that
   carries a live analogue line would fail such a refusal by its own movement; the sequence block,
   the one kind with a pulse, carries none.
9. A command button of a page is found by its caption among the buttons outside the docks and the popups. The press and
   Confirm are the button's own, so the step proves the library's button and its gateway function, not a particular
   plant: what the plant does with the tag (a reset that the model acts on) is for the effects file of a later
   revision. The step reads the hold at the rate of the gateway's export, about half a second.
10. A configuration row of a device with modes, and any row that needs another state of the device, is listed and not
    walked.
