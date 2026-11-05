---
title: Component selection guide
type: wiki
updated: 2026-11-05
---
# 16 Component Selection Guide

| Field | Value |
|---|---|
| Document ID | COB-WIKI-16 |
| Revision | A |
| Status | Issued for use |
| Built | Cloud session of 2026-11-05, from the library at `c595afa` (Cadre HMI Components 0.8.0, 97 components) |
| Code | `library/profile.json` (`kinds`, `deviceKinds`, `faceplates`, `frame`), `tools/hmi/screen.py` (`KIND_VIEW`, `MODULE_KIND`, `MODULE_ONLY`, `FRAME_ONLY`, `MODULE_EXCEPT`, `MODULE_NEEDS`, `MODULE_VALUE`), `module/components.json`, `tools/hmi/parts.py` (`FIT_TOP_DOCK`, `FIT_TOOLBAR`) |
| Companions | Page 17 (the tag model and the UDT of each device kind), page 18 (the descriptor and device model reference for an automatic view builder), `module/CATALOGUE.md` (every component and property, generated), page 14 (the configuration as delivered) |

## 1. Purpose

This page states the selection criteria of the library: for each decision an engineer or an automatic view builder makes when a plant is
drawn, the choices the library offers, the facts that separate them and the rule to apply. It does not repeat the property lists
(`module/CATALOGUE.md`), the members (page 17) or the descriptor keys (page 18); it says which of them to reach for.

The decisions are taken in the order of Table 1: the earlier ones are made once for a project and bound the later ones.

Table 1. The decisions, their scope and where each is stated.

| Order | Decision | Scope | Stated by | Section |
|---|---|---|---|---|
| 1 | Rendering: stock views or module components | Project | `screen.py --render {stock,module}` | 2 |
| 2 | Frame | Project | `screen.py --frame {openbridge,asm,ob,obasm}` | 3 |
| 3 | Faceplate style and place | Project default, device override | `--faceplate {openbridge,asm}`, `--faceplate-mode {dock,popup}`, the device model's `faceplate` | 4 |
| 4 | Page layout: diagram or cards | Page | `screen.layout` | 5 |
| 5 | Kind of each plant object | Symbol | `kind` | 6 and 7 |
| 6 | Device, second drawing or plain drawing | Symbol | `device`, `faceplate` | 8 |
| 7 | Instrument presentation | Symbol | `kind`, `deviceKind`, `bar` | 9 |
| 8 | Page parts: pipes, buttons, bars, trends, alarm panels, links | Page | the descriptor's part keys | 10 |
| 9 | Ownership, configuration rows and interlocks | Device | the device model and the tag model | 11 |

## 2. The Rendering

### 2.1 The Two Renderings

The same descriptors build either rendering (page 12 section 9 item 1). `--render stock` draws every kind with the parent's views;
`--render module` draws the kinds of `MODULE_KIND` with the module's components and every other kind with the parent's views as before.

Table 2. The renderings compared (page 12 section 8 Table 6, page 14, `CONFIGURATION.md` sections 3 and 4).

| Criterion | Stock (`--render stock`) | Module (`--render module`) |
|---|---|---|
| What the gateway must accept | A project import only | The module `cadre.hmi.ob` 0.8.0 installed, a gateway restart (GF-28), a signed module or a gateway that allows unsigned modules (GF-100) |
| Drawing of a symbol | The library's approximation of the package drawing | The package's own drawing, states, readouts and alert frame (page 12 section 7.2) |
| Perspective components per symbol | 10 to 30 | 1; pages of seven module symbols carry 54 to 67 per cent fewer components (page 12 Table 4) |
| First load of a project session | Baseline | The module's script, stylesheet and font; the script is 2,779,218 bytes at 0.8.0 and loads on every page of a project that uses a component (GF-29, page 14 section 4.2) |
| Module-only kinds (section 7) | Refused, one error per symbol (G7 contract) | Drawn |
| Frames `ob` and `obasm` (section 3) | Refused by the command line and by `build_child` | Available |
| Change to how a symbol is drawn | A project import; possible in the Designer | A module release and a gateway restart |
| Faceplates, alarm logic, write paths | The parent's | The same; the child overrides the parent's alarm views and tank tile with the module's (page 06 section 6 rule 3, COBD-014, COBD-025) |
| Gates | G0 to G11 | G0 to G11, G1 also reading the module schemas |

### 2.2 The Rule

1. Render with the module where the gateway accepts a module and its restart; render stock where it cannot (the hybrid the owner adopted,
   COBD-022, page 12 section 9).
2. A project that needs a module-only kind, a module chart or the frames `ob` or `obasm` must render with the module.
3. A project that must be changed in the field without a gateway restart, or whose symbols are customised in the Designer, renders stock.
4. Under the module rendering a single symbol can keep the library's view with `"render": "view"` (used by the component test page's side by side
   comparison).

### 2.3 Where the Module Keeps the Library's View

Under `--render module` a symbol stays on the library's view wherever the component cannot show its parameters truthfully. A builder that
wants every symbol drawn by the module avoids the parameter sets of Table 3. The profile publishes the same facts as `kinds.<kind>.moduleExcept`
and `moduleNeeds`.

Table 3. The parameter sets that keep a symbol on the library's view (`screen.py` `MODULE_EXCEPT`, `MODULE_NEEDS`, `module_digits`).

| Kind | Stays on the library's view when | Why |
|---|---|---|
| `fan`, `filter`, `damper`, `switch` | `vertical` is true | The component has no vertical artwork for the fan; the others have three orientations where the library's flag names no side |
| `valve`, `analogvalve`, `filter`, `damper`, `switch` | `variant` is other than `regular` or `flat` | The component draws only those two (the library's `regular` is the component's `square` for the filter, damper and switch, `MODULE_VALUE`) |
| `generator` | `picture` is `genset`; or `variant` other than `regular`, `activated`, `progress`, or a control, interlock or command locked badge | The component is the indicator disc and draws none of these marks; the generator set is a library drawing |
| `tank` | `valueFractionDigits` other than 0 | The component prints whole numbers |
| `instrument-field` | `size` `enhanced` with `hasSetpoint` true; `align` `start` | The enhanced field with a setpoint is 6 px higher than the library's box; the element cannot align its rows at the start |
| `readout`, `instrument-field` | A number format that is not `0`, `0.0`, `0.00` and so on (with or without `#,##`), or a setpoint with other digits than the value | The element takes a digit count, not a format (`fraction_digits`) |
| Any library kind | `badgeDuty` or `outOfService` given | The page parts' duty mark and out of service greying are library drawing |
| `indicator`, `controller`, `sequence` | Always | The module has no component for these kinds; they are library views in both renderings |

## 3. The Frame

### 3.1 The Four Frames

Table 4. The frames and what separates them (page 04 sections 2 to 11, page 14 section 6).

| Criterion | `openbridge` (stock frame) | `asm` (stock ASM frame) | `ob` (module frame) | `obasm` (module ASM frame) |
|---|---|---|---|---|
| Needs `--render module` | No | No | Yes | Yes |
| Top dock | 48 px | 84 px (bar 48, page header 36) | 84 px (module top bar 48, Cadre strip 36) | 132 px (top bar 48, strip 36, page header 48) |
| Bottom alarm banner | No | 76 px | No | 76 px |
| Navigation | Menu in a left dock | Navigation dock in two states: the pages tree and the support list | The module's navigation menu | The module's tree navigation or navigation menu |
| Plant hierarchy, crumb and node badges | Where pages name a `node` | Yes, with crumb popups | Yes (the Cadre crumb) | Yes, with crumb popups |
| Global search | No | Yes | No | Yes |
| Page header with title, level word, previous and next, and the pivot pages Alarms and Trend of a node | No | Yes | No | Yes |
| Several floating faceplates | No (one popup) | Yes, six slots | No | Yes |
| Canvas zoom and its toolbar | No | Yes | No | Yes |
| ASM glass gates (`search`, `zoom`, `panels`) | Not applicable | Run | Skipped with the reason recorded | Run (read only gates; the writing gates need an ASM model, page 14 section 9 item 3) |

### 3.2 The Rule

1. Without the module, choose `openbridge` for a plain operator frame and `asm` for an ASM operation (a hierarchy of display levels, an alarm
   banner, a global search, pivot pages per node).
2. With the module, choose `ob` for the plain frame drawn by the package's own top bar and menus, and `obasm` for the ASM operation on the same
   components.
3. Give every page a `node` whenever the plant has areas: the crumb, the node badges and the alarm roll up follow the hierarchy in every frame
   (page 04 section 7).
4. Under `asm` and `obasm` give each page its `level` word and, where the operator steps through a sequence of pages, `previous` and `next`:
   both must name a route of the descriptor set, or the build is refused.
5. The ASM rules (ownership by mode, the faceplate style, priority colours, hierarchy, counts, crumb) are in the library's data and scripts, not
   in a component (`CLAUDE.md` rule 7), so the choice of frame never changes a device's behaviour.

### 3.3 The Room a Frame Leaves

The render gate's viewport is 1600 by 900 px (`frame.viewport`); the diagram canvas is 1580 by 600 px and the cards canvas 1600 by 852 px
(`frame.diagramCanvas`, `frame.cardsCanvas`). A diagram page that should scale to its window states `fit`. `fit: true` reserves the default
frame's 48 px top dock and, where the page has the toolbar, 56 px more (`parts.FIT_TOP_DOCK`, `FIT_TOOLBAR`); under another frame the page
states its reservation as an object.

Table 5. The height the docks take, and the `fit` reservation that follows from it (arithmetic from the measured dock heights; the toolbar
included).

| Frame | Docks at the top and bottom | `reserveY` with the toolbar |
|---|---|---|
| `openbridge` | 48 px | `fit: true` (104 px) |
| `asm` | 84 + 76 px | 216 px (`asm_descriptors.DEFAULT_FIT`) |
| `ob` | 84 px | 140 px |
| `obasm` | 132 + 76 px | 264 px |

An open faceplate dock takes 400 px of the width while it is docked (`parts.FIT_FACEPLATE_DOCK`, GP-10); `reserveX` reserves a dock that stays
open.

## 4. The Faceplate Style and Place

### 4.1 The Style

A device's faceplate is drawn in one of two styles (page 13 section 10.2). `openbridge` is the tabbed faceplate of page 13 sections 2 to 9;
`asm` is the anatomy of the ASMP study: a header strip and the tabs Home, Config, Diagnostics, Alarms, Interlock and Info. The project's
default is `--faceplate`; a device model entry may override it with `faceplate`.

Table 6. The faceplate each device kind opens in each style (`library/profile.json` `deviceKinds.<kind>.faceplates`).

| Device kinds | `openbridge` | `asm` |
|---|---|---|
| `pump`, `motor`, `fan` | `Faceplate/Pump` | `Faceplate/ASM/Pump` |
| `valve`, `analogvalve`, `damper` | `Faceplate/Valve` | `Faceplate/ASM/Valve` |
| `instrument`, `readout`, `instrument-field` | `Faceplate/Instrument` | `Faceplate/ASM/Instrument` |
| `sequence` | `Faceplate/Sequence` | `Faceplate/ASM/Sequence` |
| `generator` | `Faceplate/ASM/Generator` | `Faceplate/ASM/Generator` |
| `tank` | `Faceplate/Tank` | `Faceplate/Tank` (gate G7 devices warns) |
| `controller` | `Faceplate/Controller` | `Faceplate/Controller` (gate G7 devices warns) |
| `indicator` | `Faceplate/Input` | `Faceplate/Input` (gate G7 devices warns) |

Rule: choose `asm` for a project built for an ASM operation (usually with the frame `asm` or `obasm`), and `openbridge` otherwise. Run G11 with
the same `--faceplate` the project was built with. A `filter` or a `switch` is a symbol kind without a device kind: it opens no faceplate of its
own (section 8).

### 4.2 The Place

`--faceplate-mode dock` (the default) opens one faceplate at a time in the 400 px right dock; a new device replaces it. `popup` opens a 450 by
600 px floating faceplate, and under the ASM frames each device gets its own popup in one of six slots (page 04 section 8.2, page 13 section
10.3). The operator can move between the two with Float and Dock; the choice holds for the session.

Rule: keep `dock` unless the operator compares several devices side by side; G10 and G11 read the right dock, so a project built with `popup`
needs its own check of the pin (page 13 section 10.3 item 5).

## 5. The Page Layout

Table 7. The two layouts (page 08 section 3).

| Criterion | `diagram` | `cards` |
|---|---|---|
| Content | A process drawing: symbols at pixel positions, pipes with compiled flow, sections that drill down, page parts | Groups of content in cards: rows of cards, each with flex groups of items |
| Placement | The builder gives `x`, `y` (the symbol centre for an automation symbol) and, for blocks, `w`, `h`; gate G5 checks overlaps with a 4 px tolerance | The generator lays the items out; row heights follow from the content (`screen.row_height`) |
| Pipes, junctions, page parts | Yes | No |
| Toolbar (colour mode, ID tags, readouts) and `showTags` | Yes | No |
| `fit` to the window | Yes | No; a page taller than the viewport scrolls |
| Typical use | Process overviews and unit pages (levels 1 and 2) | Summary pages, instrument panels, overview cards of devices drawn elsewhere |

Rule: draw a process as a diagram; use cards for a page of values or devices with no process path between them. A card symbol showing a device
drawn on a diagram uses `device` with the folder name (section 8).

## 6. The Kind of a Plant Object

### 6.1 Plant Objects with a Library Kind

Table 8 is the selection table for the objects a plant usually has. Every kind in it has a library view, so it draws in both renderings;
the module column names the component that draws it under `--render module`.

Table 8. Plant objects, their kind, and what each kind brings (`KIND_VIEW`, `MODULE_KIND`, `library/profile.json` `kinds`).

| Plant object | Kind | Library view | Module component | Faceplate (`openbridge`) | Flow role | Choose it when |
|---|---|---|---|---|---|---|
| Pump of any type, fixed or variable speed | `pump` | `Automation/Pump` | `cadre.ob.pump` | Pump | Gates the flow by `on` | The object runs and stops on a command; give `hasSpeed` and bind `speed` for a variable speed drive |
| Motor driving anything other than a pump or fan (mixer, agitator, conveyor, compressor) | `motor` | `Automation/Motor` | `cadre.ob.motor` | Pump | Gates by `on` | As the pump, where the motor is the object the operator commands |
| Fan, blower | `fan` | `Automation/Fan` | `cadre.ob.fan` | Pump | Gates by `on` | As the pump; a vertical fan stays on the library's view under the module |
| On and off valve (isolating, actuated, solenoid) | `valve` | `Automation/Valve` | `cadre.ob.valve` | Valve | Gates by `open` | The object opens and closes on a command and reports open |
| Modulating valve with a position | `analogvalve` | `Automation/AnalogValve` | `cadre.ob.analogvalve` | Valve | Gates by `open` | The opening in per cent is shown on the symbol (`value`); the faceplate carries the valve's commands and modes, and a loop that positions it is operated from its `controller` |
| Damper | `damper` | `Automation/Damper` | `cadre.ob.damper` | Valve | Gates by `on` | An air path that opens and closes |
| Filter, strainer, screen | `filter` | `Automation/Filter` | `cadre.ob.filter` | None | Passes the flow | A static object in a pipe run; it may open another device's faceplate with `faceplate` |
| Breaker, isolator, electrical switch | `switch` | `Automation/Switch` | `cadre.ob.switch` | None | Gates by `on` | A switch whose state gates a line; no faceplate of its own, but it can be the drawing of an `indicator` device (section 8 rule 1) |
| Generator or generator set | `generator` | `Automation/Generator`, or `Automation/GeneratorSet` with `params.picture` `genset` | `cadre.ob.generator` (the indicator disc only) | ASM Generator, in both styles | Passes | A generating set with start, stop, reset and service commands (pulses) and engine, fuel and run hour members (page 13 section 12) |
| Tank, vessel, sump, silo, basin | `tank` | `Automation/Tank` | `cadre.ob.tank` | Tank | Terminal | A vessel with a level; `static` for a vessel with no level measurement, with `max` for its capacity |
| Analogue transmitter on a diagram (level, pressure, flow, temperature, analyser) | `readout` | `Automation/Readout` | `cadre.ob.readout` | Instrument | Passes | A value with its unit beside the equipment it measures (section 9) |
| Analogue value on a card, or a value with a setpoint | `instrument-field` | `Instrument/Field` | `cadre.ob.instrumentfield` | Instrument | Passes | A larger value with its caption and unit, optionally with its setpoint (section 9) |
| Control loop (PID) | `controller` | `Instrument/Controller` | None (library view) | Controller | Passes | A process value, setpoint, output and auto and manual mode as one block, with tuning |
| Digital input or status (level switch, limit switch, alarm contact, run feedback) | `indicator` | `Automation/Indicator` | None (library view) | Input | Passes | A state shown as a lamp; `states` gives its colours by value, `alarm` names a tag whose alarms it frames |
| Sequence, cycle, batch phase, clean in place | `sequence` | `Instrument/Sequence` | None (library view) | Sequence | Passes | A step number and its text, with pulse commands (start a cycle, enable, take out of service) |

The flow role is the kind's part in the compiled flow of the pipes (`kinds.<kind>.flow` and `gate`): a gating kind passes flow only while its
state member is true, a passing kind always passes it, a tank is a terminal (page 08 section 4).

### 6.2 Reading the Kind from a Source Object

An automatic builder converting another system's objects chooses the kind by the signals the object carries. Table 9 is the order to test
them in; the members named are those of page 17.

Table 9. The kind of a source object by its signals (the first row that matches).

| The source object carries | Kind |
|---|---|
| A step number, or a step text | `sequence` |
| A process value, a setpoint and an output | `controller` |
| Start and stop commands with engine, fuel or run hour values | `generator` |
| A run feedback and a run command | `pump`, `motor` or `fan`, by the equipment |
| A position in per cent and an open feedback | `analogvalve` |
| An open feedback and an open command | `valve`, or `damper` for an air path |
| A level in per cent, or a volume and a capacity | `tank` |
| One analogue value with or without alarm limits | `readout` on a diagram, `instrument-field` on a card |
| One digital state and nothing to command | `indicator` |
| A state that gates a line and nothing to command | `switch` |
| No signal (a drawing only) | `filter`, a static `tank`, or a module-only kind (section 7) |
| Nothing the library has a kind for | Record it under `unmapped` and leave it out, or draw it as a gap box (an unknown kind is drawn as a counted gap box) |

## 7. The Module-Only Kinds

### 7.1 The Rule

A module-only kind has a module component and no library view (`MODULE_ONLY` less `FRAME_ONLY`, 48 kinds). It draws only under
`--render module`; the stock rendering refuses each such symbol with one error (gate G7 contract). Its parameters are the component's properties
(`module/CATALOGUE.md` sections 4 and 5). Every one of them is display only: no module-only kind writes to the plant, has a device kind of its own, or
takes part in the compiled flow (owner's decision of tranche T1, page 14 section 8). A module-only symbol that should open a device's faceplate
states `faceplate`, or is made the drawing of a device of another kind (section 8).

Choose a module-only kind only where Table 8 has no kind for the object, the project renders with the module, and the object is shown rather than
operated.

### 7.2 The Kinds by Purpose

Table 10. The module-only kinds (the descriptor kind, the component and its default size from `module/components.json`).

| Purpose | Descriptor kinds | Components | Default size | Notes |
|---|---|---|---|---|
| Electrical single line symbols | `resistor`, `capacitor`, `diodes`, `ground`, `source`, `converter`, `transformer`, `bipolar-transistor`, `mosfet`, `logic`, `router` | `cadre.ob.resistor` and the same names | 96 by 96 (48 px symbol box) | Static symbols on the filter's attribute set: `on`, `tag`, `readoutPosition`, badges and alert frame; placed like an automation symbol |
| Busbar or data bus | `bus` | `cadre.ob.bus` | 200 by 24 | A labelled bar |
| Pipe, cable and air lines | `horizontal-line`, `vertical-line`, `corner-line`, `three-way-line`, `line-cross`, `line-overlap`, `end-point-line`, `direction-line` | `cadre.ob.pipehorizontal`, `pipevertical`, `pipecorner`, `pipetee`, `pipecross`, `pipeoverlap`, `pipeend`, `pipedirection` | 24 px units | Display only lines; no compiled flow (section 10.1) |
| Valve glyphs without readout | `valve-analog-two-way-icon`, `valve-analog-three-way-icon` | `cadre.ob.valvetwoway`, `valvethreeway` | 48 by 48 | The valve and its opening as a small glyph |
| Hydraulic circuit | `hydraulic-check-valve`, `hydraulic-valve-4-3`, `hydraulic-valve-x-2` | `cadre.ob.checkvalve`, `hydraulicvalve43`, `hydraulicvalvex2` | 48 by 48, 144 by 48, 96 by 48 | The selected position is shown; its selection is not wired (page 14 section 9 item 5) |
| Specialty vessels | `heat-exchanger`, `heat-pump`, `hydraulic-separator` | `cadre.ob.heatexchanger`, `heatpump`, `hydraulicseparator` | 152 by 96 | A hot and a cold side for the first two |
| Small indicators | `indicator-battery`, `indicator-engine`, `indicator-tank-atmospheric`, `automation-badge` | `cadre.ob.battery`, `engine`, `tankatmospheric`, `automationbadge` | 48 by 48 (badge 32 by 32) | A level bar or a trend graph for the battery and the atmospheric tank |
| Value chips | `automation-readout`, `transmitter-button`, `readout-block` | `cadre.ob.automationreadout`, `transmitterbutton`, `readoutblock` | 72 by 48, 96 by 40, 144 by 64 | A value with its unit; the readout block also a setpoint or advice marker |
| Dials | `gauge-generator`, `gauge-motors-and-pumps`, `gauge-valve`, `instrument-radial` | `cadre.ob.gaugegenerator`, `gaugemotorspumps`, `gaugevalve`, `instrumentradial` | 240 by 280 (radial 240 by 240) | The gauges overflow their 240 by 280 box, which is not measured (page 14 section 9 item 4); setpoint marks are shown, not written |
| Bars and progress | `bar-horizontal`, `bar-vertical`, `circular-progress` | `cadre.ob.barhorizontal`, `barvertical`, `circularprogress` | 480 by 128, 128 by 320, 48 by 48 | A scale with value fill, advice zones and a setpoint marker |
| Charts of series | `line-graph`, `area-graph` | `cadre.ob.linegraph`, `areagraph` | 480 by 320 | Series given as properties; they read no tag history (section 10.3) |
| Charts of shares | `donut-chart`, `pie-chart`, `polar-chart`, `radial-bar-chart` | `cadre.ob.donutchart`, `piechart`, `polarchart`, `radialbarchart` | 480 by 320 | Segments or rings, each with its value |

### 7.3 The Frame Components

The 33 frame components (`FRAME_ONLY`: the top bar, menus, navigation, tree navigation, breadcrumb, alert button and menu, notifications,
tabs, pivots, modal window, context menu input, tooltip, toggletip, clock and the user and app buttons) are drawn by the frames `ob` and `obasm`
in their own views. They are not symbols of a process page; a builder does not place them. The alarm lists (`cadre.ob.alertlist`,
`cadre.ob.alertpanel`) are drawn by the frame and by the module's alarm views under the module rendering, and the canvas zoom
(`cadre.ob.canvaszoom`) by the ASM frames.

## 8. The Device and the Drawing

A symbol is one of four things to the faceplate dock. Table 11 gives the key that makes each.

Table 11. What a symbol is to its device (page 06 section 5, the descriptor schema).

| The symbol is | Key | Effect |
|---|---|---|
| The device's own drawing | `"device": true` | Its id is the device's tag folder; a click opens the device's faceplate; the device belongs to the node of the deepest page that draws it so |
| A second drawing of a device drawn elsewhere (an overview card) | `"device": "<folder>"` | Opens the same faceplate; the device's node stays where its own drawing puts it |
| A drawing that opens another device (a filter that opens its backwash sequence, an electrical symbol that opens its feeder) | `"faceplate": "<device id>"` | Opens that device's faceplate; the symbol is not the device's drawing |
| A plain drawing | Neither | No click action |

Rules:

1. Give `device` to every object the operator commands or whose alarms the operator acknowledges. A `filter`, a `switch` or a module-only
   symbol has no device kind: use `faceplate` to open a related device, or give `device` with `params.deviceKind` naming the device's kind
   (Table 6), which makes the symbol that device's drawing and opens its faceplate (the component test page draws its alarm lamps as `switch`
   symbols of `indicator` devices, `screen.embed_module`).
2. A device symbol binds its state, speed, value, a controller's setpoint, output and loop mode, and a sequence's step and text inside its own
   folder by the kind's member names, or gate G7 refuses it (page 06 section 5 rule 2).
3. A device that no page draws can still be listed in the device model with a `node`, so that its alarms count and search finds it.

## 9. The Instrument Presentation

Table 12. The choices for an analogue value (page 06 Table 3, `library/profile.json` `kinds`).

| Choice | Size | Shows | Faceplate | Choose it for |
|---|---|---|---|---|
| `readout` | 72 by 24 px, 72 by 40 with `hasTag`; grows to its identifier | A value and its unit on one line, the identifier beneath | `instrument`, or the kind of `deviceKind` | A transmitter on a diagram beside its equipment |
| `instrument-field` | 96 by 64 px; 96 by 66 with `size` `enhanced` and `hasSetpoint` | A caption (label and unit), the value, optionally the setpoint | As the readout | A value on a card, or a value with its setpoint |
| `controller` | 120 by 96 px | The process value large, the setpoint, the output, the auto or manual badge | Controller | A control loop the operator adjusts |
| The symbol's `bar` key | Beside the readout or field | A range bar with its normal band and limit marks | None of its own | A value whose position in its range matters at a glance |
| `bars` part (`Parts/RangeBar`) | As placed | As above, for any tag | None | A range bar without a readout |
| Module `bar-horizontal`, `bar-vertical`, `instrument-radial`, gauges | As Table 10 | A scale, dial or gauge | None | Display of a value in the package's style, under the module rendering |

Rules:

1. A readout or field that shows a loop's process value opens the controller: give it `deviceKind` `controller` and bind its value to the
   controller's `value` (page 06 section 5 rule 2).
2. Alarm limits belong in the device's members (`hiHiLimit` to `loLoLimit` and their delays, page 17): the faceplate shows and writes them, and the
   bar's limit marks can follow them.
3. Under the module rendering keep number formats of the form `0.0` (Table 3), or the symbol stays on the library's view.

## 10. The Page Parts

### 10.1 Pipes

Table 13. The two ways to draw a pipe.

| Choice | Drawn by | Flow | Media | Gates |
|---|---|---|---|---|
| `pipes` and `junctions` of the descriptor | The generator, as SVG paths between symbol ends, junctions and via points | Compiled: one expression per pipe from the gating kinds' states (G6 offline, G9 on the glass) | `neutral`, `fresh-water`, `sea-water`, `fuel`, `oil`, `steam`, `hot`, `cold`, `air`, `waste` | G5, G6, G9 |
| Module line kinds (Table 10) | The package's line elements, placed as symbols | None | The element's own media | G5 only |

Rule: draw process piping with `pipes`, which carries the flow; use the module's line kinds only for a display that needs the package's line style
and shows no flow. `lines` draws free lines (dashed, or gated by a state).

### 10.2 Commands on a Page

A command that is not a device's (start a cycle, reset an area) is a `buttons` entry: a pulse asks Confirm or Cancel and writes through W18 with
the `Administrator` role on a tag the descriptors declare; `"render": "module"` draws the question button as `cadre.ob.button` under the module
rendering. A button can also open a device's faceplate on a named tab, or navigate to a route. A device's own command belongs on its faceplate, not
on a page button.

### 10.3 Trends

Table 14. The choices for history.

| Choice | Reads | Where |
|---|---|---|
| The device model's `trend` members | Tag history | A card on the trend page `/trends` and the faceplate's Trend tab |
| `trends` part | Tag history, the last `minutes` minutes, one or two pens (two units get an axis each) | Embedded on a diagram |
| Module `line-graph`, `area-graph` | The series bound to its properties | Display only; no history query |

Every trended tag needs `historyEnabled` and a `historyProvider` in the tag model (page 17).

### 10.4 Alarms on a Page

The frame always shows the alarms of the session's scope; a faceplate's Alarms tab shows the device's. On a page, `alarmPanels` draws the library's
alarm list over the alarms under the folders named, with Ack selected and Ack all beneath it; an `indicator` with `alarm` frames a fault row; the
symbols draw their alert frames from the library's alert states. The five priorities and their colours are those of page 13 section 11.1.

### 10.5 Navigation from a Page

`sections` drill down from a region of a diagram to a route, `links` place an area chevron that navigates, a card may carry a `route`, and
`buttons` may navigate. Keep navigation and faceplate opening on different clicks (the schema's rule for `links`).

## 11. Ownership, Configuration and Interlocks

Table 15. The device options beyond the members (page 13 sections 7 and 10, `schemas/devices.schema.json`).

| Option | Choose it when | Stated by |
|---|---|---|
| Ownership by mode | The source system has modes owned by the program, the operator, maintenance or a local station, and commands must follow the owner | The device model's `modes` and the member `mode` |
| Configuration rows | A device has numeric configuration values the operator or maintenance may set within bounds (start delay, run on time) | Members under `cfg/`, marked `config` with caption, unit, minimum, maximum and format in the device model; written through W19 |
| Pulse commands | A command is a momentary request the plant resets | Members marked `pulse` with a `caption`; written through W18 |
| Interlocks and permissives | Starting depends on conditions, or trips stop the device | The tag folder `ilk/` with one `Cnn/` folder per condition (page 17); kinds with `interlocks` in the profile: `pump`, `motor`, `fan`, `valve`, `analogvalve`, `damper`, `sequence` |
| Maintenance functions | Force, object error mask and the simulation, suppression and manual flags exist in the source | Members under `mnt/`; kinds with `maintenance` in the profile: `pump`, `motor`, `fan`, `valve`, `analogvalve`, `damper`, `indicator`, `generator` |
| Alarms on source tags | The device's alarms stay on tags outside its folder | The device model's `alarmSources` |

## 12. The Selection Checklist

1. Can the gateway take the module and a restart? Then `--render module`; otherwise `--render stock` and no module-only kind.
2. Is the operation ASM? Then `--frame asm` (stock) or `obasm` (module), `--faceplate asm`, and `node`, `level`, `previous` and `next` on the pages.
3. For each page: a process is a `diagram`, a set of values or devices is `cards`.
4. For each object: the first matching row of Table 9 gives the kind; Table 8 confirms it has a library kind, else Table 10 offers a module-only
   kind, else the object is `unmapped`.
5. For each object the operator commands or acknowledges: `device`, and a device model entry with exactly the members its folder carries (page 17).
6. Under the module rendering, avoid the parameter sets of Table 3 for every symbol meant to be drawn by the module.
7. Pipes with flow are `pipes`; trends from history are `trends` or the device model's `trend`; a page command is a pulse `buttons` entry.
8. Build, then run G0 to G7 (offline, in `screen.py`), and on a gateway G8 and G11, then G10 for anything that writes (page 14 section 7).

## 13. Open Items

1. The profile names no member for the opening of an analogue valve; the symbol's `value` is a parameter the descriptor gives or binds, and a
   device model cannot list an opening member until the profile knows one (page 17).
2. The writes of the module-only kinds (hydraulic valve selection, gauge setpoints, the components' click events) are deferred (page 14 section 9
   item 5).
3. The gauges overflow their default box (page 14 section 9 item 4).
4. A project built with `--faceplate-mode popup` is not swept by G11; its pin needs its own check.

## 14. References

1. `library/profile.json`, `library/contracts.json`, `module/components.json`, `module/CATALOGUE.md`, `schemas/screen-descriptor.schema.json`,
   `schemas/devices.schema.json`, `tools/hmi/screen.py`, `tools/hmi/parts.py`, `tools/hmi/asm_descriptors.py`.
2. This wiki: pages 04 (frames), 06 (the symbol and faceplate contracts), 08 (the descriptor and the gates), 12 (the module and its
   comparison with the stock library), 13 (faceplates, ownership, the faceplate style), 14 (the configuration as delivered), 17 (the tag model and
   UDTs), 18 (the view builder reference).
3. The owner's decisions COBD-022 (the hybrid rendering), COBD-025 (the module's alarm views), COBD-044 (ownership by mode), COBD-045 (the faceplate
   style, the pin and the configuration rows), and those of tranches T1 and T2 (page 14 section 8).
