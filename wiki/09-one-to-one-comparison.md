---
title: One-to-one comparison
type: wiki
updated: 2026-10-07
---
# 09 One-to-One Comparison with the Vendor Process Overview

| Field | Value |
|---|---|
| Document ID | COB-WIKI-09 |
| Revision | A |
| Status | Issued for use |
| Reference | The vendor demo's `/` route ("Process Overview") and `/card` route ("Home"), observed 2026-10-07 at 1,600 x 900 px |
| Rebuild | Child project `cadre_hmi_demo` on `cadre_hmi_base`, routes `/` and `/card`, the same viewport |
| Evidence | `workspace/compare/process-overview/` and `workspace/compare/home/` (local only: they hold vendor screenshots): `comparison.json`, `side-by-side.png`, `difference.png`, `symbol-crops.png` |

## 1. Purpose

The test asks one question: built only from the wiki, the parent library and the generator, how
close does a screen come to the vendor's own, and what exactly is missing? The aim is the gap
list, not the screen.

## 2. Method

1. **Fixture.** `tools/import_openstudio.py` converted the vendor's `Page/ProcessOverview` view
   (study copy) into a descriptor: 39 symbols, 18 junctions, 61 pipes, 5 sections, 0 unmapped. The
   states of the 39 symbols were read from the running demo's web components and became the
   values of 138 memory tags under `[default]cadre_hmi_demo/process`.
2. **Build and gates.** The generator built the child; G0 to G7 passed (G6: 27 gates, 61 pipes,
   4,096 sampled gate states, 0 mismatches); the parent, the tags and the child were imported.
3. **Capture.** The vendor page was observed in the built-in browser (a page script read the
   symbol geometry and readout text; a screenshot was taken). The rebuild was captured by
   `tools/compare/capture.py` in a new session (G8: 1,037 components rendered, 0 error badges).
4. **Comparison.** `tools/compare/compare.py` matched the symbols by child order and measured the
   centre offset, the box size and the readout text (normalised for spacing, thousands
   separators, hinted leading zeros and superscripts); then the grey-level difference of the two
   screenshots at 800 x 450 px, a side-by-side image, a difference heat map, and a crop grid of the
   17 symbols in the viewport.

## 3. Results

Table 1. Measured agreement, first comparison and final.

| Measure | First | Final |
|---|---|---|
| Symbols compared | 39 of 39 | 39 of 39 |
| Symbol centre identical to the pixel | 39 | 39 |
| Largest centre offset | 0 px | 0 px |
| Readout text equal after normalisation | 33 | 39 |
| Readout text equal exactly | 23 | 23 |
| Mean absolute grey difference (0 to 255) | 11.56 | 11.03 |
| Share of pixels differing by more than 32 grey levels | 7.2 per cent | 6.31 per cent |

The 16 texts that differ exactly differ only in form: the vendor writes the cubic metre as `m`
followed by a separate superscript `3`, pads pump speeds with hinted zeros (`075`), and repeats
values for screen readers. The remaining pixel difference is dominated by live data that differs
by design (alarm text, alarm count, clock and time zone, section 5 item 13), the pump size and
frame (items 1 and 2), the tank chart (item 4) and the toolbar (item 8).

## 4. Defects Found by the Comparison

The comparison found ten defects that every offline gate had passed. Each was fixed in the generator
or the library and the build repeated.

Table 2. Defects found by the comparison.

| No. | Seen in the comparison | Cause | Fix |
|---|---|---|---|
| 1 | A small up and down glyph after every status text | A sub-pixel scrollbar in a 20 px flex row (GF-09) | Every container defaults to `overflow: hidden` in the emitter |
| 2 | `3,000 / 10,000 m³`, `30%` | Grouped number format, no space before `%` | `numberFormat(value, '0')`, a separate `%` label |
| 3 | Bold percentages | Active instead of neutral type style | The OpenBridge tank typography (`instrument-value-enhanced-neutral`, unit style `%`) |
| 4 | Two small tanks showing `100%` in large type | No static mode | `static`: a plain tile with the capacity and the tag below |
| 5 | Vertical valves drawn as a square | The horizontal and the rotated icon both visible | The horizontal artwork hidden when `vertical` |
| 6 | Pumps without the direction triangle | No `double` variant | `variant: double`, a direction icon over a smaller pump icon |
| 7 | Outline segments across pipe T-joints | Each pipe's outline drawn after the previous pipe's inner stroke | All outlines first, then all inner strokes |
| 8 | Inverted level box (grey above, white fill) | Pipe tokens used for the tank | The instrument frame tokens of the OpenBridge tank |
| 9 | Stopped pumps showing a speed; one vendor pump imported as stopped | The status row ignored the running state, and the importer read "running" from the direction icon property | The OpenBridge rule (`abstract-automation-button-motorized.ts`): the speed only while `on`, otherwise `Off`; the importer takes the observed `on`, or a displayed speed |
| 10 | A pump that should run showing `Off` after the second screen was added | With two descriptors the tag document put every member under the last tag root, so the first screen's tags kept stale values | One subtree per tag root, merged under the common top folder; a unit test |

## 5. Gap Register

Table 3. The remaining differences, by kind. Kind: L library, F frame, G generator, P platform
(stock Perspective works differently), D data (not a defect).

| No. | Kind | Difference | What closing it takes | Register |
|---|---|---|---|---|
| 1 | L | Pumps use `componentSize: medium`: 52 px holder, 72 px target, 36 px icon; ours are regular size (36 px holder) | A medium size in the symbol factory (the medium tokens exist) and a 72 px symbol box | COB-030 |
| 2 | L | The vendor alert frame (`small-side-flip`) encloses the symbol and its readout, with the flap outside the top right corner; ours is a 45 px frame inside the symbol box with the flap inside the corner | Frame and flap drawn around the whole embed box; the frame types `regular`, `large-side-flip`, `bottom-flip`, `top-flip` | COB-032 |
| 3 | L | Pump readout: a double chevron, hinted leading zeros in a lighter tone, `%` in unit style; ours a single triangle, no hinted zeros | A speed readout block (value, hint, unit labels) and the double chevron icon | COB-033 |
| 4 | L | Tank chart: a filled area in `--instrument-enhanced-tertiary-color`; ours a sparkline with markers | `ia.chart.timeseries` or an SVG area path from the history | COB-031 |
| 5 | L | Tank vessel: straight sides and a shallow cap, text a few pixels lower; ours a domed top | Vessel path and text positions from `automation-tank.css` geometry | COB-034 |
| 6 | L | Value row: the vendor renders the current value and `/ max unit` at one size; ours sizes them differently | Re-read the vendor tank rows in a close-up and align | COB-034 |
| 7 | F | Section label: placed at the top right of the visible part of the section; ours at the section's own top right, off screen for a wide section | Label position rule | COB-040 |
| 8 | F | Diagram toolbar: Color, legend swatches (On, Off and the mediums), ID-tag, Readout, zoom level, mini-map and right panel buttons; ours Color, ID-tag and Readout | Legend from the mediums in use, zoom and pan, mini-map, panel button bound to the faceplate dock | COB-035 |
| 9 | P | The vendor canvas pans and zooms without scroll bars; ours scrolls with native scroll bars | Zoom and pan need a scripted transform on the diagram container; scroll bars can be styled in the stylesheet as the vendor demo does | COB-036 |
| 10 | F | Top bar icons: a framed alert icon with silence, a bell count box, a sun brilliance icon; ours a triangle, a filled bell and the dimming icon | Icon choices and the silence event | COB-038 |
| 11 | P | Connector editing in the Designer (draw, route, medium palette editor); ours only from a descriptor | By design: the descriptor is the editing surface. A Designer editor would need a module | COB-041 |
| 12 | G | Flow is compared with our reference solver (G6, G9), not pipe by pipe with the vendor's rendering | Read the vendor pipe states from its shadow DOM and compare per connection | COB-039 |
| 13 | D | Alarm text, alarm count, clock time and time zone | None: two gateways, two alarm sets; the vendor clock shows UTC, ours local time with a UTC label | COB-042 (clock offset) |
| 14 | P | Font weight: measured after the comparison (GF-26), Noto Sans is served and drawn, but only at 400, 500 and 700, so the OpenBridge weights 370 and 570 draw as 400 and 700 | A variable Noto Sans served as a project or theme font, or an explicit weight map | COB-068 |

## 6. Second Test: the Home Page (Cards)

The vendor `Home` page is two rows of two cards whose bodies are flex columns of instrument
fields, labels, a compass, a pitch and roll indicator, four pumps and a speed gauge. The importer
(`--layout cards`) converted it into a cards descriptor with flex card bodies (2 rows, 4 cards,
18 tag values from the running demo); the generator built it into the same child at `/card`.

Table 4. Home page agreement.

| Measure | Result |
|---|---|
| Cards | 4 of 4, titles equal |
| Card centre offset | 2.8 px each |
| Card size | 780 x 406 px against 792 x 418 px (the Cadre card carries its own 8 px margin) |
| Words on each Cadre card found in the vendor card (titles, labels, units, `Off`) | 4 of 4 cards, no word missing |
| Components without a Cadre equivalent, drawn as counted gap boxes | 3: compass, pitch and roll, speed gauge |
| Mean absolute grey difference; share over 32 levels | 10.47; 4.99 per cent (dominated by the three gap boxes) |

Table 5. Home page gaps (register items in `REGISTER.md`).

| No. | Kind | Difference | Register |
|---|---|---|---|
| H1 | L | Ship instruments (compass, pitch and roll): out of scope for process automation | N-COB-3 |
| H2 | L | Speed gauge: the stock `ia.chart.gauge` or `ia.chart.simple-gauge` is the candidate | COB-056 |
| H3 | L | Instrument field colour: the vendor draws some values in the enhanced colour (blue); Cadre draws all in the active colour | COB-055 |
| H4 | F | Card spacing model: the vendor card's surface is inset in its box; the Cadre card has a margin | COB-054 |
| H5 | D | Roll, pitch and pressure change live on the vendor demo (simulated tags); the fixture holds the values of one moment | None |

## 7. Conclusions

1. The parent library and the generator reproduce the vendor process overview's structure
   exactly: every symbol is in the same place, in the same state, with the same readout.
2. The visible differences are listed in Table 3 and each has a defined closing action; none
   needs a module, apart from Designer editing of diagrams, which the descriptor replaces.
3. The comparison earns its cost: it found ten defects that the offline gates and the live
   render gate had passed.
4. The cards layout reproduces the vendor card page's structure within 2.8 px; its gaps are ship
   instruments and one stock gauge.
