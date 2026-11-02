---
title: Parent project and library
type: wiki
updated: 2026-10-11
---
# 06 Parent Project and Component Library

| Field | Value |
|---|---|
| Document ID | COB-WIKI-06 |
| Revision | F |
| Status | Issued for use |
| Build | `python tools/hmi/parent.py --out build [--deploy]` writes `build/cadre_hmi_base`, `library/contracts.json` and `library/profile.json` |

## 1. Purpose

This page describes the inheritable parent project `cadre_hmi_base`: what it carries, the contract
of each library view, the device and faceplate contract, and the rules a child project follows.

The controller, the indicator, the maintenance functions, the write paths W12 to W17 and the
faceplates that list only the members a device carries were built on 2026-10-10 and are proven
offline only (unit tests, the parent build, gates G0 to G7). The sequence, its pulse command (write
path W18) and the sizes of the library profile followed on 2026-10-11, proven offline in the same
way. Page 13 section 9.8 lists what the gateway has proven and has yet to prove; until it has, the
statements of this page about them describe the build, not a measured result.

The layout keys of the profile (section 2, Table 1a), the identifiers of 16 characters (section 4.1)
and the static tank without a capacity (section 4.2) followed on 2026-10-11, after the first page
built from a plant's data. They were decided by rendering and looked at on the gateway: gate G8 on
every route of the sample projects and of the fixture, and gate G11 on the fixture and on
`cadre_hmi_sample` (page 13 section 9.8). A review of the same day added three keys (`grows`,
`identifier.share` of the tank and `diagram.overlap`), the readout that the generator grows and the
room an identifier has beside the next symbol (section 2).

## 2. Contents

Table 1. The parent project (239 files).

| Resource | Content |
|---|---|
| `project.json` | Title "Cadre HMI base", inheritable, no parent |
| `stylesheet.css` | Palettes, global tokens, the regular component sizes in use (page 03) and the rules of the two layout classes (section 4.1) |
| `style-classes/cadre/` | 77 classes (page 03 section 6) |
| `views/Automation/` | `Pump`, `Motor`, `Fan`, `Valve`, `AnalogValve`, `Damper`, `Filter`, `Switch`, `Indicator`, `Tank`, `Readout` |
| `views/Instrument/` | `Field`, `Controller`, `Sequence` |
| `views/Framework/` | `TopBar`, `NavMenu`, `NavItem`, `SideMenu`, `BrillianceMenu`, `UserMenu`, `AlertMenu`, `AlertsPage`, `TrendsPage` (the route `/trends` of a child with historised members, COB-064) |
| `views/Trend/` | `Card` (one member of the trend page) |
| `views/Faceplate/` | `Pump`, `Valve`, `Tank`, `Instrument`, `Controller`, `Input`, `Sequence`, `Empty`; `Alarms` (the device alarm list each faceplate embeds), `InterlockRow`, `LimitRow`, `SetpointRow` and `TankTile` (parts the faceplates embed) |
| `ignition/script-python/cadre/hmi` | Palette, device selection, page title, scoped alarm summary, acknowledge, a device's alarm patterns and count, the alarm list as OpenBridge `Alert` records and its acknowledge and row events; the interlock rows, summary and start permission (page 13 section 7); the instrument's unit, limit rows, history paths, limit series and the tank tile (page 13 section 8); the device read, the checked writes of the write paths W1 to W18, the force, the object error mask and the pulse command, and the trended members (page 13 section 9) |
| `ignition/script-python/cadre/icons` | Geometry of the 92 converted icons, `elements(name)` |
| `session-props` | `custom.palette` (day), `custom.nav` (items, footer with Alerts), the dock contract (`custom.selectedDevice`, `selectedKind`, `selectedTitle`, `selectedLabel`), `custom.alarmScope` (`*`), `custom.devices` (the device index, empty here; each child writes its own, page 13 section 6; with a device model each entry also carries `sources`, `write` and `members`, page 13 section 9.3), `custom.trends` (the trend index); `props.theme` light-cool |
| `page-config` | The shared docks and `/alerts` |

Every view passes the Ignition-Wiki registry validator (gate G1, 37 views, 0 errors).

`library/profile.json` (`tools/hmi/library_profile.py`, written with the contracts) states the library
to a tool that writes descriptors and device models: every symbol kind with its view, flow role,
faceplate and members; every device kind (the `kind` of a device model) with its faceplate, members
and binding rule; the pulse members of each kind (`pulses`); the tabs of each faceplate; the write
paths W1 to W18 with their members, role and checked function; and the device functions (`alarm-list`,
`alarm-limits`, `interlocks`, `trend`, `trend-page`, `force`, `error-mask`, `pid-faceplate`,
`pid-tuning`, `pulse-command`). Every member is stated with `required` false, since a faceplate lists
what a device carries. It is generated from the tables the code uses, and a unit test fails when the
file on disk differs from them.

The profile also states what a tool needs to lay symbols out without reading the views. Each symbol
kind carries `size`, the default size of its view in pixels, taken from the built view; an
automation symbol carries `symbolSize`, the 48 px box a descriptor gives it, and `embedBox`, the box
its embed occupies for each `readoutPosition` as an offset from that symbol box, `[dx, dy, width,
height]`, computed by `screen.symbol_box`. A kind whose box is used as the descriptor gives it (the
tank, the instrument field, the controller, the sequence) carries no embed box, and neither does the
readout, whose box the generator grows only where it is too small (`grows`, Table 1a). The
`frame` section gives the heights and widths that bound a page: the top dock, the faceplate dock, the
viewport of the render gate and the canvases of a diagram and of a cards page. Unit tests hold each
size to the built view, each embed box to `screen.symbol_box`, and the embeds of the fixture page to
the boxes the profile gives. The file is replaced in one step when it is rewritten, so that a tool
reading it meets a whole profile.

Since the first page built from a plant's data (2026-10-11) the profile states the true size of a
block as well. Table 1a lists the keys; every value is taken from the code or was measured on the
glass, and a unit test holds it to the built views (`FirstRenderTests`).

Table 1a. Layout keys of the library profile.

| Key | Content | Use by a layouter |
|---|---|---|
| `kinds.<kind>.sizes` | A list of `{"when": {parameter: value}, "size": [width, height]}`, empty for most kinds. `size` holds a block with every flag at its default; an entry states the size the block needs when the symbol's parameters meet its `when` (a parameter not given has the contract's default; no `when` names a default, so a parameter the symbol does not give meets none). A readout with `hasTag` true needs 72 by 40 px; an instrument field with `size` `enhanced` and `hasSetpoint` true needs 96 by 66 px | Take the size of the first entry whose `when` the parameters meet, otherwise `size` (`library.block_size`) |
| `kinds.<kind>.grows` | True for the readout, false for every other kind. True: the generator grows a box smaller than the block needs about its centre, to at least the size of `sizes` for its flags and, where the block shows its identifier, to the width the identifier needs (`screen.grown_box`); a box that holds the block is used as given. False: the box is used as given and gate G5 warns of one too small | Reserve for a readout the larger of the box and what it needs, about the centre of the box; a readout given what it needs is not moved |
| `kinds.<kind>.identifier` | Where the kind draws its identifier: `param` (the parameter that holds it: `tag`, or `label` for an instrument field, whose caption is the label, a space and the `suffix` parameter, the unit), `flag` (the parameter that shows it, null where it is always drawn), `font` (a key of `text.fonts`), `pad` (the width in px the block takes beside the text) and `fits` (the characters the default size holds) | A block shows an identifier of n characters in full when it is at least `n * text.fonts[font].charWidth + pad` px wide; narrower, the identifier ends in an ellipsis |
| `kinds.tank.identifier.share` | 0.86, on the tank alone: the share of the tile's width that the identifier of a live tank takes, whatever the tile's size. A static tank gives its identifier the whole width of its box. `pad` (24) and `fits` (19) are the same fact at the default width of 168 px | A live tank shows n characters in full when it is at least `n * charWidth / share` px wide, a static one when it is `n * charWidth` px wide. `n * charWidth + pad` is never less than either for n up to 16, so the general rule is safe at any size |
| `kinds.readout.value` | The `font` and the `pad` of the readout's value (null for every other kind) | The width the value needs, by the same rule, from the characters of the formatted value and its unit |
| `text.identifierChars` | 16: the longest identifier the library draws in full under a symbol | An automation symbol's embed grows for no more than 16 characters |
| `text.fonts.<font>` | `px` and `line` (the font size and the height of a line), `charWidth` (the width allowed for one character) and `measured` (the mean width of an upper case letter, a lower case letter and a digit, and the widest glyph, as measured) | The widths above. For the identifier fonts `charWidth` is the upper case mean rounded up to half a pixel; for the value font it is the digit mean rounded up likewise |
| `diagram.ring` | 18: the distance in px from the centre of an automation symbol at which a pipe ends (the round holder, `diagram.RING`) | The end of a pipe at a symbol is the symbol's centre moved 18 px towards the side named |
| `diagram.symbol` | 48: the side of the symbol box | The centre of a symbol is its box's corner plus 24 px |
| `diagram.staticTile` | `[0.06, 0.06, 0.88, 0.66]`: the tile of a static tank as fractions of its box (x, y, width, height) | A pipe at the left, the right or the top of a static tank ends at the tile's edge, on the centre lines of the box; at the bottom it ends at the box, beneath the identifier |
| `diagram.routes` | The shape of a pipe without via points, by the axis each end leaves on (`v` a top or bottom side, `h` a left or right side, `-` an end with no side), start then end: `vv` `Z_Y`, `hh` `Z_X`, `vh` and `v-` `L_Y`, `hv` and `h-` `L_X`, `-v` `L_X`, `-h` and `--` `L_Y` (`diagram.ROUTES`) | Two ends that share x or y are joined straight. `Z_Y` runs to the rounded mean of the two y, across, then on; `Z_X` runs to the rounded mean of the two x, up or down, then on; `L_Y` has one corner at the x of the start and the y of the end; `L_X` one corner at the x of the end and the y of the start |
| `diagram.via` | `L_X`: the shape between two consecutive via points that share neither x nor y (`diagram.VIA`) | As above |
| `diagram.overlap` | 4: two boxes of a diagram overlap when they share more than this many px on both axes (gate G5, `gates.OVERLAP`; the generator keeps the same tolerance, `screen.OVERLAP`) | Two symbols are on one row when their boxes without the widening share more than 4 px down the page; such a pair needs the room of the next paragraphs |

The embed of an automation symbol follows from `embedBox` and the identifier. With `need` the width
the identifier asks for (`min(n, 16) * charWidth + pad`, where the symbol has a `tag` and `hasTag` is
not false), a readout beneath or above the symbol makes the embed `max(embedBox width, need)` px
wide, centred on the symbol; a readout beside the symbol makes it `48 + max(embedBox width - 48,
need)` px wide, growing away from the symbol. An identifier that fits the default (8 characters
beneath a symbol, 7 beside it) changes nothing. A unit test holds the rule to `screen.symbol_box` for
every automation kind, side and length.

The embed of a readout follows from its box, `sizes` and the identifier. A readout whose parameters
meet a `when` is at least that entry's size, and one that shows its identifier (`hasTag` true and a
`tag`) is at least `need` px wide; the generator grows a smaller box about its centre and leaves a
box that is large enough alone. A readout of the default 72 by 24 px with an identifier of 15
characters is therefore drawn 130 by 40 px, 29 px wider at each side and 8 px higher above and below.
The same unit test holds this rule to `screen.symbol_box` for every box, length and flag.

Both rules give the embed a symbol has with nothing beside it. On a row, the widening stops at the
embed of the next symbol (`screen.embed_limits`, page 08 section 3): with `gap` the distance between
the boxes the two have without the widening (`embedBox` for an automation symbol; for a readout its
box, or the size of `sizes` where that is larger), and each wanting `(embed width - width without
the widening) / 2` px towards the other (for a readout beside its symbol the whole difference on the
side the readout lies, and nothing on the other), the two are widened in full when the two wants
are together no more than `gap`; otherwise each takes `gap / 2`, or the one that wants less than
that takes its want and the other the rest. An embed centred on its symbol or on its box is then
narrowed alike at both sides, and gate G5 names each identifier that ends in an ellipsis. A layouter
that keeps `gap` at least the sum of the two wants gets every identifier whole and no warning.

## 3. Automation Symbol Contract

The nine device views are generated from one factory (`library.automation_symbol`) and share one
contract, the Cadre form of the vendor's "automation button". The ninth, `Indicator`, is a digital
input shown as a lamp (page 13 section 9.5): its artwork is drawn in the library, and it passes the
medium whatever its state.

Table 2. Parameters of `Automation/<Kind>`.

| Parameter | Values | Default | Effect |
|---|---|---|---|
| `on` or `open` | boolean | false | State: `open` for `Valve` and `AnalogValve`, `on` for the others, `Indicator` included. Holder fill and icon follow it |
| `readoutPosition` | `bottom`, `right`, `left`, `top`, `none` | `bottom` | Side of the readout; drives the flex direction of the root |
| `showStatus` | boolean | true | Status row: On or Off, the speed for motorised devices, the opening for analogue valves |
| `statusText` | string | empty | Overrides the status text |
| `hasTag`, `tag` | boolean, string | false, empty | The identifier row of the readout |
| `hasSpeed`, `speed` | boolean, number | false, 0 | Speed in per cent on the status row (pump, motor, fan) |
| `value` | number | 0 | Opening in per cent (`AnalogValve`) |
| `vertical` | boolean | false | Vertical artwork, or the horizontal artwork rotated a quarter turn |
| `variant` | `regular`, `flat`, `double` | `regular` | `flat` hides the holder; `double` draws a direction icon over a smaller device icon (motorised kinds) |
| `activated` | boolean | false | Selected background |
| `alert` | boolean | false | Alert frame and flap |
| `alertFrameStatus` | `alarm`, `warning`, `caution` | `alarm` | Frame colour and flap shape (triangle, circle, square) |
| `alertFrameMode` | `acked-active`, `unacked-active`, `unacked-rectified` | `acked-active` | Steady, flashing, or dashed and flashing |
| `badgeControl` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only` | `none` | Top left badge |
| `badgeInterlock` | `none`, `interlock`, `interlock-inhibit` | `none` | Bottom left badge: OpenBridge's duty icon for `interlock`, its standby icon for `interlock-inhibit` (page 13 section 7) |
| `badgeCommandLocked` | `none`, `command-locked` | `none` | Bottom right badge |
| `progress` | boolean | false | Spinning progress ring |
| `deviceId`, `deviceKind`, `deviceLabel` | string | empty, the kind, empty | Faceplate contract (section 5); `deviceLabel` is the description in the faceplate header |

Geometry: the symbol box is 48 px, the holder ring 36 px with a 1 px border, the icon 24 px and the
badges 16 px, the regular-size OpenBridge tokens. The readout adds 64 px to the right or left, or
44 px below or above, and the generator places the embed so that the symbol centre falls on the
point the descriptor gives (page 08 section 3). An identifier longer than the default readout holds
widens the embed by what it needs, up to 16 characters (section 2, Table 1a), and no further than the
embed of the next symbol on its row: the readout is as wide as its content and never wider than the
embed, so an identifier that does not get its width ends in an ellipsis.

## 4. Other Library Views

Table 3. Tank, readouts, instrument field, controller and sequence.

| View | Parameters | Notes |
|---|---|---|
| `Automation/Tank` | `value`, `max`, `unit`, `tag`, `trend` (fast-rising, rising, stable, falling, fast-falling), `showPercent`, `chart`, `history`, `compact`, `static`, `hasCapacity`, `medium`, `deviceId`, `deviceLabel` | Percent coordinates, so one view serves any size; level box redrawn by a binding on `props.elements[1].d`; `static` draws a plain tile with the capacity and the identifier beneath it, and `hasCapacity` false (default true) draws no capacity (section 4.2); `chart` replaces the level box with a sparkline |
| `Automation/Readout` | `value`, `unit`, `format`, `tag`, `hasTag`, `label`, `deviceId`, `deviceKind`, `deviceLabel` | A value on a line, 72 by 24 px; with `hasTag` the identifier lies beneath the value and the block needs 72 by 40 px, and the width its identifier needs. On a diagram the generator grows a smaller box about its centre (section 2). `deviceKind` (default `instrument`) names the faceplate a device readout opens: `controller` for a readout of a loop's process value |
| `Instrument/Field` | `label`, `value`, `unit`, `format`, `size` (regular, enhanced), `hasSetpoint`, `setpoint`, `setpointFormat`, `source`, `align` (`start`, `center`, `end`), `tag`, `deviceId`, `deviceKind`, `deviceLabel` | Value, setpoint and unit stacked, aligned within its box; `deviceKind` as for the readout |
| `Instrument/Controller` | `value`, `setpoint`, `output`, `manual`, `hasSetpoint`, `hasOutput`, `unit`, `format`, `label`, `tag`, `hasTag`, `deviceId`, `deviceKind`, `deviceLabel` | A control loop as one block: the control badge (`auto`, or `manual`) beside the identifier, the setpoint, the process value large with its unit, the output in per cent (page 13 section 9.4) |
| `Instrument/Sequence` | `text`, `step`, `hasStep`, `label`, `tag`, `hasTag`, `deviceId`, `deviceKind`, `deviceLabel` | A sequence as one block, 144 by 72 px: the identifier or the label, the text of the current step large, the step number small beneath it where `hasStep` is true. It passes the medium and is never gated (page 13 section 9.7) |

The full parameter lists are generated into page 05 section 4 from `library/contracts.json`.

### 4.1 Identifiers

An identifier (the `tag` parameter) may be 16 characters long, the length of a plant's tag stem. It is
read from its first character wherever it is drawn: beneath or beside an automation symbol, in a
readout, in the head of a controller block and of a sequence block, in a tank tile and beneath a
static tank; the caption of an instrument field (its label and unit) is treated alike. A label too
narrow for its text ends in an ellipsis and is never cut at the start, and the faceplate header shows
the identifier whole.

Perspective draws a label as a flex box around one inner element that holds the text (read on the
glass on 2026-10-11), so `text-overflow` on the label itself shows no ellipsis. Two style classes
with empty bodies carry the rule through the stylesheet (`theme.layout_css`), as the palette classes
carry theirs: `cadre/text/ellipsis` keeps a label inside its container and puts the ellipsis on the
inner element; `cadre/box/within` keeps a container inside its own, which holds the readout of a
symbol to the width of its embed. Before, a readout wider than its embed was centred on it and cut at
both ends.

The widths are measured, not assumed. Table 3a gives the fonts as the gateway drew them (Chromium,
1600 by 900 px, Noto Sans) and the width the library allows for one character.

Table 3a. Fonts of the identifiers and of the readout's value.

| Font class | Size and line | Upper case | Lower case | Digit | Widest glyph | Allowed per character |
|---|---|---|---|---|---|---|
| `cadre/font/automation-label` | 12 px, 16 px | 7.61 px | 6.36 px | 6.61 px | 11.22 px | 8 px |
| `cadre/font/instrument-label` | 11.5 px, 16 px | 7.30 px | 6.10 px | 6.33 px | 10.76 px | 7.5 px |
| `cadre/font/instrument-unit` | 11.5 px, 16 px | 7.30 px | 6.10 px | 6.33 px | 10.76 px | 7.5 px |
| `cadre/font/automation-value-regular` | 16 px, 22 px | 10.62 px | 9.09 px | 9.15 px | 15.60 px | 9.5 px |

At 8 px a character an identifier of mixed case and digits fits the width the library gives it. Of
the strings of 16 characters measured in `cadre/font/automation-label`, `RawWaterFlow_FT1` took
107.8 px and `FilterBackwashSQ` 100.5 px of the 128 px allowed, and the fixture's `SuctionLowLvl_SW`
takes 102.9 px on its page; 16 upper case letters (`ABCDEFGHIJKLMNOP`) took 120.1 px. One written in
the widest letters alone (16 of `W` take 178.6 px) ends in the ellipsis. The default sizes hold 8
characters beneath a symbol, 7 in a readout, 10 in a controller block, 16 in a sequence block, 19 in
a tank tile and a caption of 12 in an instrument field (`identifier.fits` of the profile).

The identifier of a live tank lies in a label that takes 0.86 of the tile's width at any size
(`identifier.share` of the profile), and that of a static tank in one as wide as the box. The 19
characters and the `pad` of 24 px are that share at the default width of 168 px alone; at another
width a tank holds `share * width / charWidth` characters, and gate G5 measures a tank's identifier
by that rule.

### 4.2 The Static Tank

A static tank is a vessel with no measurement: a tile with the capacity centred and the identifier
beneath it. The capacity is the `max` parameter, whose default is 100, so a descriptor that states no
capacity would show a number nobody stated. The generator therefore sets `hasCapacity` false on a
static tank whose descriptor neither gives nor binds `max`, and refuses one that sets `hasCapacity`
true without it (gate G7 contract). A descriptor that gives `max` is built as before.

The tile lies inside the tank's box (`library.STATIC_TILE`: 6 per cent in from the left, the right
and the top, and 66 per cent of the height), where the vessel of a live tank fills its box. A pipe at
the left, the right or the top of a static tank therefore ends at the tile's edge
(`diagram.connection_point`), on the centre lines of the box; before, it ended at the box and stopped
short of the tile. A pipe at the bottom still ends at the box: the identifier lies between the tile
and it. Under the module rendering a tank is the module's own component, which fills its box and
draws its own capacity; `hasCapacity` does not reach it. A static tank without a capacity is
therefore drawn by the library's own tile under the module rendering as well
(`screen.MODULE_EXCEPT`, published in the library profile as `kinds.tank.moduleExcept`), so that
neither rendering shows a number the descriptor does not state. For the same reason the module
draws a pump only when the pump has a speed, and a tank only when its unit is cubic metres
(`screen.MODULE_NEEDS`, `moduleNeeds` in the profile): the module's pump always prints a speed and
its tank always prints `m³`, so a pump with no speed and a level in litres or per cent are drawn by
the library's views. A property on the module's components would lift both; that needs a module
build and a gateway restart.

## 5. Device and Faceplate Contract

A symbol or tank marked `device` opens the faceplate dock on click. The click writes the dock
contract to the session (`cadre.hmi.select_device`), then opens the dock.

Table 4. The dock contract.

| Session property | Value |
|---|---|
| `custom.selectedDevice` | The device's tag folder (`deviceId`) |
| `custom.selectedKind` | The library kind |
| `custom.selectedTitle` | The identifier shown on the symbol (`tag`), else the folder name |
| `custom.selectedLabel` | The description (`deviceLabel`) |

The side menu maps each kind to its faceplate by name, because view paths are case sensitive
(GF-22): pumps, motors and fans open `Faceplate/Pump`; valves, analogue valves and dampers
`Faceplate/Valve`; tanks `Faceplate/Tank`; readouts and instrument fields marked as devices
`Faceplate/Instrument`; controllers `Faceplate/Controller`; indicators `Faceplate/Input`; sequences
`Faceplate/Sequence`; any other kind `Faceplate/Empty`. A readout or an instrument field selects the
kind its `deviceKind` parameter names, `instrument` unless the descriptor says otherwise.

Table 5. The members each faceplate reads, under the device's tag folder. Every member is optional: a
faceplate lists the members its device carries (page 13 section 9.1).

| Member | Type | Faceplate | Meaning |
|---|---|---|---|
| `state` | Boolean | Pump, Valve, Input | Running, open, or on |
| `cmd` | Boolean | Pump, Valve | Command: run, or open; written by Start and Stop, Open and Close (W1) |
| `mode` | Int4 | Pump, Valve | 0 Auto, 1 Manual, 2 Local; written by the mode buttons (W2) |
| `fault` | Boolean | Pump, Valve, Sequence | Fault; Reset fault writes false (W5) where the member may be written. The sequence faceplate shows the fault and offers no reset |
| `speed` | Float8 | Pump | Speed in per cent |
| `speedSp` | Float8 | Pump | Speed setpoint in per cent; written by the setpoint field (W3) |
| `level` | Float8 | Tank | Level in per cent |
| `value` | Float8 | Instrument, Controller | The process value |
| `hiHiLimit`, `hiLimit`, `loLimit`, `loLoLimit` | Float8 | Tank, Instrument, Controller | Alarm limits of the level or the value; setpoints (W4), and in the sample the alarms follow them (page 13 section 8) |
| `sp` | Float8 | Controller | Setpoint; written by the setpoint field (W12) |
| `out` | Float8 | Controller | Output in per cent |
| `manual` | Boolean | Controller | False automatic, true manual; written by Auto and Manual (W13) |
| `manOut` | Float8 | Controller | Manual output in per cent; written by its field while the loop is in manual (W14) |
| `gain`, `ti`, `td` | Float8 | Controller | Gain, integral time and derivative time, the times in milliseconds; written by the Tuning tab (W15) |
| `mnt/forceOn`, `mnt/forceOff` | Boolean | Pump, Valve, Input | The force as a pair of flags; written by Force on, Force off and Automatic (W16) |
| `mnt/forceMode`, `mnt/forceValue` | Boolean | Pump, Valve, Input | The force as a mode and a value (W16) |
| `mnt/errorMask` | Boolean | Pump, Valve, Input | The object error mask; written by Mask and Automatic (W17) |
| `mnt/simulated`, `mnt/alarmSuppress`, `mnt/manualMode` | Boolean | Pump, Valve, Input | Read only flags |
| `step` | Int4 | Sequence | The number of the current step |
| `stepText` | String | Sequence | The text of the current step, computed in the tag model |
| `trigger` | Boolean | Sequence | A pulse command: the pulse button writes true (W18) and the plant returns it to false |
| `ilk/` members | | Pump, Valve | The interlock contract (page 13 section 7) |

The tank's tile also reads `volume`, `capacity` and `trend` where the folder carries them (page 13
section 8 rule 7).

Rules:

1. A descriptor marks a device with `"device": true`, the tag folder then being the symbol's id, or
   with the folder name (`"device": "P101"`) for a second symbol of a device drawn elsewhere, such
   as an overview card.
2. Gate G7 fails a device whose state (`on` or `open`), `speed` or `value`, a controller's
   `setpoint`, `output` or `manual`, or a sequence's `text` or `step`, is bound outside its folder or
   to another member name: the
   faceplate would show a different value from the symbol. The rule is that of the device's kind
   (`deviceKind` where the symbol names one), so a field that opens a controller binds `sp`. A tank's
   `value` may be any member, its volume for example; the tank faceplate reads `level` in per cent.
3. When the generator writes the tags (a test build), it creates for every device the members of its
   kind in `FACEPLATE_MEMBERS` of `tools/hmi/screen.py`, with their defaults (for a pump `state`,
   `cmd`, `mode`, `speed`, `speedSp` and `fault`; the limits beyond a tank's two and the `mnt/`
   members are never generated), and nothing beyond them and the bound members. A faceplate member
   that a symbol also binds keeps the value given and takes the member's own type, so a sequence's
   step number is an integer. For a device that a
   device model names it creates exactly the members the model lists. When the tags come from
   elsewhere (`tagModel` `external`), a faceplate shows what the folder carries (page 13 section 9.1);
   with a device model and a tag model, gate G7 devices checks the one against the other (page 08
   section 5).
4. Every faceplate carries a tab row beneath the dock's header (Table 6): one pane per tab, shown
   by `view.custom.tab` through `position.display` (GF-08). The first tab is the default, and a
   change of `params.deviceId` (another device selected) resets the faceplate to it.
5. The Alarms tab embeds `Faceplate/Alarms` at the full height of the dock. It lists every alarm
   whose source matches one of the device's patterns (`cadre.hmi.device_sources`): the one pattern
   of the device folder, `prov:<provider>:/tag:<folder>/*` (`cadre.hmi.device_source`, measured
   GF-34), or, for a device whose model names them, the patterns of the source tags its alarms stay
   on (page 13 section 3). The list shows the states active and unacknowledged, active and
   acknowledged, cleared and unacknowledged, and every priority. The tab label carries the same
   count (`cadre.hmi.alarm_count`, polled every 2 s). The title text no longer filters anything.
6. The top bar and the alerts page show the alarms of the session's scope:
   `session.custom.alarmScope`, a source pattern such as `*cadre_hmi_wtp*`, or `*` for every
   alarm (GF-20).
7. **Command security (COB-063, COBD-024).** Every write to the plant or to an alarm needs the
   gateway's admin role, `Administrator` (read from the gateway, GF-43): the write paths W1 to W18
   of NOTE-COB-04 (commands, modes, setpoints, limits, fault reset, the top bar's ACK, the stock
   tables' actions, the module lists' ACK and ACK visible, bypass and the trip reset; since
   2026-10-10 the controller's setpoint, loop mode, manual output and tuning, the force and the object
   error mask; since 2026-10-11 the pulse command). A view writes only through the checked functions
   of `cadre.hmi` (`command`, `bypass`, `reset_interlocks`, `ack_top`, `ack`, `force`, `error_mask`,
   `pulse`), which refuse a session whose signed in
   user lacks the role and answer the refusal, shown on the faceplate. Where a device model marks a
   member read only (the device's index entry carries a `write` list without it), the functions refuse
   it for every session, and the faceplate hides its command group or disables its field, its Bypass
   or its Reset (page 13 section 9.1 rule 2). A write the gateway does not make is answered as a
   refusal (NOTE-COB-04 section 11.5). Each command control binds `enabled` to the view's
   `custom.can`, which polls `cadre.hmi.permissions(self.session)` every 2 s; the stock alarm
   status tables bind `enableAcknowledge`, `enableShelve` and `enableUnshelve` to it, and the
   module's alarm menu marks its records `noAck` for a session that may not acknowledge. Viewing
   stays open to every session. Gate G7 refuses a direct tag write or alarm action in any script of a
   view, a private function of `cadre.hmi`, `system` or `cadre` named without its module (an import,
   an alias, a lookup), a bidirectional tag binding, and a control or table whose `enabled` is not
   the permission of the path its script names, alone or joined by `&&` (page 08 section 5). The gate
   is a check on generated views; the role check inside each function is the control.

Table 6. Faceplate tabs (COB-076).

| Faceplate | Kinds | Tabs |
|---|---|---|
| `Faceplate/Pump` | pump, motor, fan | Control (status, commands, modes, speed setpoint, fault reset), Alarms, Interlocks (only with an `ilk` folder), Maintenance (only with a `mnt/` member) |
| `Faceplate/Valve` | valve, analogue valve, damper | Control (status, commands, modes, fault reset), Alarms, Interlocks (only with an `ilk` folder), Maintenance (only with a `mnt/` member) |
| `Faceplate/Tank` | tank | Values (tile, level, alarm limits as setpoints), Trend (level), Alarms |
| `Faceplate/Instrument` | readout and instrument field marked as devices | Values (value, alarm limits as setpoints), Trend (value), Alarms |
| `Faceplate/Controller` | controller | Control (process value, setpoint, output, Auto and Manual, manual output, alarm limits), Trend (process value, setpoint and output, only where one is historised), Tuning (gain, integral and derivative time, only where the loop carries one), Alarms |
| `Faceplate/Input` | indicator | Status (the state as On or Off), Maintenance (only with a `mnt/` member), Alarms |
| `Faceplate/Sequence` | sequence | Status (the text of the step, the step number, the fault, a button for each pulse command), Trend (the step number as a stepped line, only where it is historised), Alarms |

Within a tab, a row, a section title or a command group shows only while the device carries its
member, and a member of bad quality is named on a line beneath the tab row (page 13 section 9.1).

A device with interlocks carries the provisional contract of page 13 section 7 under
`<device>/ilk/`; the faceplate's Start is refused while the device is not permitted or is
interlocked, the Control tab says why, and a latched trip waits for the Interlocks tab's Reset
(COBD-023).

Gate G7 checks the tab row, the panes, the reset and the alarm list of every faceplate offline, the
interlock contract of every `ilk` folder of the tag model, and a device model against the library
profile, the descriptors and the tag model;
gate G11 opens every tab of every device's faceplate on the glass and fails on a missing device,
an empty pane, a quality overlay, a line naming a member of bad quality, an error badge, an alarm of
another device, or a tab count that differs from the list (page 08 section 5).

## 6. Rules for a Child Project

1. `project.json` names `cadre_hmi_base` as its parent (gate G4 checks it).
2. A child carries its own `page-config` and `session-props`: both are single resources, so the
   child's copy replaces the parent's. The generator writes both, with the parent's shared docks
   and session defaults merged in (`parent.page_config`, `parent.session_defaults`).
3. A child may override any parent view by writing the same view path; the generator does so only
   under `--render module`, for the module's alarm views and tank tile (COBD-014).
4. Import order: the parent, then every child. A session that was open while the parent changed
   keeps the inherited views it loaded (GF-10): verify in a new session.
5. Every project names the identity provider `default`, so that a user can sign in (GF-43); the
   deploy module sets it after an import when it differs, with the project's own properties in the
   body (GF-44).
6. Every page, dock and popup root carries the palette class binding (page 03 section 4); the
   generator writes it on every screen root.
