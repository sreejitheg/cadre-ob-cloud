---
title: Cadre-Sandbox-OpenBridge wiki index
type: wiki-index
updated: 2026-10-09
---
# Cadre-Sandbox-OpenBridge: Wiki Index

An OpenBridge-inspired Ignition Perspective parent project, component library, application frame
and screen generator, built on stock Perspective components after a study of the OpenStudio
product (the commercial "OpenBridge for Ignition" module), and tested one to one against the
vendor's own demo on a live 8.3.6 gateway.

## 1. Reading Order

| Page | Question it answers |
|---|---|
| [01 OpenStudio anatomy](01-openstudio-anatomy.md) | What OpenStudio is, how it is built, and what its licences permit |
| [02 Export feasibility](02-export-feasibility.md) | To what extent its information and configuration can be exported, and how |
| [03 Design system](03-design-system.md) | The OpenBridge palettes, typography, sizes and icons in a stock project |
| [04 Navigation and frame](04-navigation-and-frame.md) | The navigation philosophy and the recreated application frame |
| [05 Component catalogue](05-component-catalogue.md) | All 135 vendor catalogue entries, their 1,788 properties, and the Cadre equivalents; property tables in [catalogue/](catalogue/) |
| [06 Parent project and library](06-parent-project-and-library.md) | What `cadre_hmi_base` carries and the contract of each library view |
| [07 Gateway facts](07-gateway-facts.md) | 41 facts measured on the gateway, and feedback for the Ignition-Wiki |
| [08 Generation and validation](08-generation-and-validation.md) | The screen descriptor, the generator, the twelve gates, and use by the Cadre tools |
| [09 One-to-one comparison](09-one-to-one-comparison.md) | The vendor process overview rebuilt and measured, and the exact gap register |
| [10 Roadmap](10-roadmap.md) | What to build next, and the owner's decisions |
| [11 Water treatment sample](11-water-treatment-sample.md) | How good a project the library supports: a small water treatment plant, simulated, run from the glass and gated |
| [12 Module spike](12-module-spike.md) | Assessment report: a Perspective module of our own wrapping the OpenBridge pump and tank, compared with the stock library; version 0.2.0 adds the alarm lists |
| [13 Faceplates, alarm lists and interlocks](13-faceplates-alarm-lists-interlocks.md) | How a faceplate is tabbed, how it finds and lists the device's alarms, the module's alarm components, the provisional interlock contract, and the instrument faceplate with its limits and trend |

## 2. Summary

The vendor product is a module wrapping the OpenBridge web components as native Perspective
components, plus an inheritable demo project that serves as its parent template. Its component
interface, its parent project and its live page structure can all be read without the module; its
design tokens and icon artwork are Apache-2.0 at a pinned release. On that basis this repository
builds `cadre_hmi_base`, an inheritable parent of 217 files (28 views, 75 style classes, the four
OpenBridge palettes, 92 icons, two script modules), and a generator that turns a JSON screen
descriptor into a child project, with twelve gates from schema to faceplate sweep. Rebuilt from a
converted copy of the vendor's process overview, the generated screen places all 39 symbols at
the vendor's exact pixel centres with the same states and readouts; the vendor's card page is
reproduced within 2.8 px per card. Every remaining difference is registered with its closing
action (page 09). A small water treatment plant built on the library runs from the glass: four
pages and alerts over 147 simulated tags, every gate passing, an operator's walk of nine checks
and all 26 faceplates clean (page 11). A module spike (page 12) hosts the OpenBridge pump and
tank themselves in Perspective: the same descriptors render either way, and every gate passes.
On 2026-10-08 the faceplates gained tabs, an exact alarm list per device, the module's OpenBridge
alarm lists, a provisional interlock contract, and an instrument faceplate with alarm limits and a
trend (page 13); the sample now has 30 devices with faceplates (44 faceplates over its four pages)
and an operator's walk of up to 13 checks. On 2026-10-09 the second session made the module's
faceplate alarm tab display only, made trips latch until reset, put every write path behind the
gateway's admin role with a signed in operator walk and an anonymous refusal, fixed the faceplate
trend's labels, added a trend page, and released module 0.2.1 with one restart; the walk now has up
to 19 checks (pages 11 and 13, NOTE-COB-04 revision E).

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
   gate and were found only by the one-to-one comparison (page 09 section 4).
6. **A clean screen is not a working one.** The water treatment sample rendered without a fault
   while ACK acknowledged nothing and the overview's faceplates bound a missing tag folder; an
   operator's walk and the faceplate contract found both (page 11 section 6).
