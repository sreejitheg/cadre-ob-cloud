---
title: Export feasibility
type: wiki
updated: 2026-10-07
---
# 02 Export Feasibility: What Can Be Extracted from OpenStudio

| Field | Value |
|---|---|
| Document ID | COB-WIKI-02 |
| Revision | A |
| Status | Issued for use |
| Question | To what extent can the information and configuration of OpenStudio be exported, and how |

## 1. Verdict

Nearly everything needed to recreate the product's interface and framework can be extracted,
without the module: the full component interface (names, property types, defaults and
enumerations) from the documentation, the full parent project (pages, docks, routes, styles,
diagram data) from the public demo repository, the live structure and state of every page from
the running demo, and the design system itself (palettes, typography, sizes, icon artwork) from
the Apache-2.0 OpenBridge source. What cannot be extracted is the module's own code, which this
work neither needs nor wants, and the demo's tags and medium palette, which are not published.
The legal position, not the technical one, decides what may be reused (page 01 section 5).

## 2. Sources and Yields

Table 1. Every source, the method, and the measured yield.

| Source | Method (tool) | Yield | Tracked output |
|---|---|---|---|
| Documentation, 137 pages (sitemap) | Paced fetch to a local cache (`tools/fetch_docs.py`); HTML table parse (`tools/parse_docs.py`) | 135 component and concept pages, 1,788 properties with section, type, parsed default and parsed enumeration; 80 events; the sidebar taxonomy | `catalogue/openstudio-interface.json` (facts only) |
| Demo project repository | GitHub API tree, raw file reads (176 text files) | Page configuration, 17 views, 60 style classes, stylesheet, session props; the connector diagram model (`connections`, `nodes`, `zones`) | None: study only, local cache |
| Running demo | Read-only page scripts in the built-in browser (`tools/compare/fingerprint.js`) | 295 rendered components on the process overview with type, path and geometry; the live state of 39 symbols read from their web components (open, on, speed, badges, alert status and mode, readout side, vertical, tank value, maximum, trend, compact) | None; local fixture only |
| OpenBridge web components, commit `2c98dda1` | Raw reads of `src/palettes/variables.css`, `src/mixins/fonts.css`, `src/automation/*`, `src/icons/*` (`tools/build_tokens.py`, `tools/convert_icons.py`) | 4 palettes of 875 colour tokens, 211 global tokens, 4 sizes of 1,710 component tokens, 48 type styles, 2,101 icon sources (90 converted) | `library/tokens/`, `library/icons/` with `NOTICE` |
| OpenStudio module | Not inspected | Nothing | Nothing |

## 3. The Connector Diagram Model

The demo's process overview is a connector diagram whose model is plain data in the view, which
makes it the most useful single export:

- `children`: the symbols, each a component or an embedded symbol view, with a box position.
  The process overview has 39: 12 tanks, 23 valves and 4 pumps.
- `nodes`: junctions, by identifier, with a point. 18 on the process overview.
- `connections`: pipes keyed by a generated identifier. Each end is a component side
  (`componentId`, `direction`, point), a junction (`kind: node`, `nodeId`), or a free end
  (`kind: free`, optionally `terminal: arrow-in` or `arrow-out`). A pipe may carry a hand-shaped
  route (`path`), a `mediumId`, a `size` and a `state`. 61 pipes; 6 with a hand route; 3 free ends.
- `zones`: background sections with a label and an optional drill-down view. 5 on the process overview.

`tools/import_openstudio.py` converts this model into the Cadre screen descriptor (page 08), so
any OpenStudio design can be rebuilt on the Cadre library. The medium palette is stored outside
the view, in the project folder (`no.openstudio.openbridge/medium-palette/palette.json`), and is
not in the published repository; the importer maps the two medium names it meets (`neutral`,
`warm`) to Cadre mediums.

## 4. What Cannot Be Extracted

Table 2. Information the exports do not carry.

| Item | Why | Handling |
|---|---|---|
| The module's Java and React code | Not published; commercial | Not needed: Cadre recreates the behaviour with stock components |
| The demo's tags (`process`, `Project`, `Sample_Tags`) | A project export carries no tags | The live states are read from the running demo and become memory tag values of the test fixture |
| Property bindings and scripts at runtime | Evaluated on the vendor's gateway | The repository views carry them as written; the running demo shows their results only |
| The medium palette | Stored in the project folder, not published | Mapped by name |
| Documentation prose | Copyright | Not reproduced; each catalogue entry links to its source page |

## 5. Extraction Facts Worth Keeping

1. The documentation is generated with an AI assistant and says so on every page ("has not been
   fully reviewed"); its parsed defaults and enumerations are therefore marked heuristic.
2. The demo's `robots.txt` disallows all automated access, while the documentation's sets no
   content signal. The two sources are treated differently for that reason (page 01 section 5).
3. The running demo exposes its component tree through two DOM attributes that Perspective
   writes on every component root, `data-component` (the type) and `data-component-path` (the
   position: `C` for the centre view, `T`, `L` and `R` for the top, left and right docks, `$`
   for an embedded view). A page script needs no access to the gateway to read a page's structure.
4. The OpenBridge web components keep their state as element properties (`open`, `on`, `speed`,
   `alertFrameStatus`), readable from a page script; readout text lives in shadow roots and must
   be read through them.
