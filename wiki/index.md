---
title: Cadre HMI Library wiki index
type: wiki-index
updated: 2026-11-05
---
# Cadre HMI Library: Wiki Index

A maritime-inspired Ignition Perspective parent project, component library, application frame
and screen generator, built on stock Perspective components and tested on a live 8.3.6 gateway.

## 1. Reading Order

| Page | Question it answers |
|---|---|
| [03 Design system](03-design-system.md) | The maritime palettes, typography, sizes and icons in a stock project |
| [04 Navigation and frame](04-navigation-and-frame.md) | The navigation philosophy and the recreated application frame |
| [05 Component catalogue](05-component-catalogue.md) | All 135 reference catalogue entries, their 1,788 properties, and the Cadre equivalents; property tables in [catalogue/](catalogue/) |
| [06 Parent project and library](06-parent-project-and-library.md) | What `cadre_hmi_base` carries and the contract of each library view |
| [07 Gateway facts](07-gateway-facts.md) | The facts measured on the gateway (GF-01 to GF-114, including the cloud sessions' commissioning, token, trust step and history provider facts), and feedback for the Ignition-Wiki |
| [08 Generation and validation](08-generation-and-validation.md) | The screen descriptor, the generator, the twelve gates, and use by the Cadre tools |
| [10 Roadmap](10-roadmap.md) | What to build next, and the owner's decisions |
| [11 Water treatment sample](11-water-treatment-sample.md) | How good a project the library supports: a small water treatment plant, simulated, run from the glass and gated |
| [12 Module spike](12-module-spike.md) | Assessment report: a Perspective module of our own wrapping the module pump and tank, compared with the stock library; version 0.2.0 adds the alarm lists |
| [13 Faceplates, alarm lists and interlocks](13-faceplates-alarm-lists-interlocks.md) | How a faceplate is tabbed, how it finds and lists the device's alarms, the module's alarm components, the provisional interlock contract, and the instrument faceplate with its limits and trend |
| [14 Library configuration](14-library-configuration.md) | Every configuration of the library as delivered: the cloud environment, the gateway, the module (97 components), building and deploying, the four frames, the gates, the owner's decisions, the open items and the merge back; the generated component list is `module/CATALOGUE.md` and the operational reference `CONFIGURATION.md` |
| [15 Showcase project](15-showcase.md) | The project `cadre_hmi_showcase`: every one of the 97 components, and the parent's embedded symbol views, on grouped pages with an editor for each property, a live simulation and an event log, and the gates that prove it works |
| [16 Component selection guide](16-component-selection.md) | Which rendering, frame, faceplate style and place, page layout and kind to choose for each plant object; when a module-only kind, a module chart or a module line is the right choice; where the module keeps the library's view |
| [17 Tag model and UDTs](17-tag-model-and-udts.md) | The tag structure each device kind needs, stated as one UDT per kind: every member with its type, access, write path, faceplate tab and default; the maintenance, configuration and interlock folders; alarms and history; a worked UDT, instance and device model entry |
| [18 View builder reference](18-view-builder-reference.md) | Every key of the screen descriptor and the device model, the symbol parameters of each kind, the placement arithmetic, the module rendering rules and the gate checks, for a tool that writes descriptors automatically |

## 2. Summary

The design tokens and icon artwork are Apache-2.0 at a pinned release. On that basis this repository
builds `cadre_hmi_base`, an inheritable parent of 217 files (28 views, 75 style classes, the four
maritime palettes, 92 icons, two script modules), and a generator that turns a JSON screen
descriptor into a child project, with twelve gates from schema to faceplate sweep. Rebuilt from a
reference process overview, the generated screen places all 39 symbols at
the exact pixel centres with the same states and readouts; a reference card page is
reproduced within 2.8 px per card. Every remaining difference is registered with its closing
action. A small water treatment plant built on the library runs from the glass: four
pages and alerts over 147 simulated tags, every gate passing, an operator's walk of nine checks
and all 26 faceplates clean (page 11). A module spike (page 12) hosts the package pump and
tank themselves in Perspective: the same descriptors render either way, and every gate passes.
On 2026-10-08 the faceplates gained tabs, an exact alarm list per device, the module's
alarm lists, a provisional interlock contract, and an instrument faceplate with alarm limits and a
trend (page 13); the sample now has 30 devices with faceplates (44 faceplates over its four pages)
and an operator's walk of up to 13 checks. On 2026-10-09 the second session made the module's
faceplate alarm tab display only, made trips latch until reset, put every write path behind the
gateway's admin role with a signed in operator walk and an anonymous refusal, fixed the faceplate
trend's labels, added a trend page, and released module 0.2.1 with one restart; the walk now has up
to 19 checks (pages 11 and 13, NOTE-COB-04 revision E).

Since 2026-11-03 the cloud sessions have built the module Cadre HMI Components to version 0.8.0 (97 components: the device symbols,
the module-only symbols and glyphs, charts and building blocks, the 33 frame components, nine pipe components, the alarm lists and the
canvas zoom), two frames drawn with its components (`ob` and `obasm`) beside the two stock frames, and the showcase project (pages 12,
14 and 15). Pages 16 to 18 (2026-11-05) are the design-time references: the selection criteria, the tag model with one UDT per device
kind, and the complete JSON reference for an automatic view builder.

## 3. Six Findings Worth Carrying Forward

1. **The parent project is the product's real asset.** A stock inheritable project can carry a
   whole design system: stylesheet, style classes, views, scripts and session defaults all
   inherit (GF-01, GF-02).
2. **A palette is a class, not a theme.** One bound style class on each page, dock and popup root
   switches every token, SVG fills included, at runtime (GF-04).
3. **Flow can be compiled.** The connector diagram's runtime flow rule becomes one expression per
   pipe, proven equal to a reference solver offline (G6) and on the glass (G9, 4 of 4 scenarios).
4. **Open sessions keep old parents.** After a parent import, verify in a new session (GF-10).
5. **Compare against the reference, not only against gates.** Ten defects passed every offline
   gate and were found only by comparison with a reference rebuild.
6. **A clean screen is not a working one.** The water treatment sample rendered without a fault
   while ACK acknowledged nothing and the overview's faceplates bound a missing tag folder; an
   operator's walk and the faceplate contract found both (page 11 section 6).
