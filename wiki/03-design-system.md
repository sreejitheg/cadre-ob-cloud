---
title: Design system
type: wiki
updated: 2026-10-07
---
# 03 Design System: The Design Tokens in a Stock Perspective Project

| Field | Value |
|---|---|
| Document ID | COB-WIKI-03 |
| Revision | A |
| Status | Issued for use |
| Source | `@oicl/openbridge-webcomponents` 2.0.0-next.155, commit `2c98dda1ac33b2a931bea2532fc78961f097e548`, Apache-2.0, Copyright 2024 OICL (decision COBD-003) |

## 1. Purpose

This page records which parts of the maritime design guidance the Cadre parent project carries,
how they are carried without a module, and how a palette is switched at runtime.

## 2. Token Sets

`tools/build_tokens.py` reads `src/palettes/variables.css` and `src/mixins/fonts.css` of the pinned
commit into `library/tokens/openbridge-tokens.json`.

Table 1. The token sets.

| Set | Selector in the source | Tokens | Examples |
|---|---|---|---|
| Global | `*` | 211 | `--font-size-100` 16 px, `--font-family-main` Noto Sans, weights 370, 570 and 700 |
| Component sizes | `.obc-component-size-regular`, `-medium`, `-large`, `-xl` | 1,710 each | `--automation-components-button-touch-target-size` 48 px regular, 72 px medium |
| Palettes | `:root[data-obc-theme="day"]`, `dusk`, `night`, `bright` | 875 each | `--container-background-color` day `rgb(247, 247, 247)`, night `rgb(0, 0, 0)` |
| Type styles | `@define-mixin font-*` | 48 | `body`, `label`, `title`, `automation-value-regular`, `instrument-value-enhanced-neutral` |

Data URI icon tokens (`--icon-*: url(data:...)`) are dropped at extraction; icons come from the
icon converter (section 5).

## 3. The Parent Stylesheet

`tools/hmi/theme.py` writes the inheritable parent project's `stylesheet.css`:

1. `:root` carries the 211 global tokens and those regular component-size tokens that any emitted
   file references (a transitive closure over `var()` references).
2. `:root` and `.psc-cadre\/palette\/day` carry the day palette; `.psc-cadre\/palette\/dusk`,
   `night` and `bright` carry the others.

The file is 209,820 bytes. Perspective renders a style class `cadre/palette/night` as the CSS class
`psc-cadre/palette/night`, so the selector form above matches it.

## 4. Palette Switching

Decision COBD-005: every page, dock and popup root carries the style class
`cadre/palette/<name>`, bound to the expression
`'cadre/palette/' + coalesce({session.custom.palette}, 'day')`. CSS custom properties inherit
through the document tree, so the whole subtree, embedded views included, takes the palette. The
brilliance menu writes `session.custom.palette` and, through `cadre.hmi.set_palette`, keeps
`session.props.theme` in step (day and bright to `light-cool`, dusk and night to `dark-cool`), so
stock components follow the same light or dark scheme. The reference demo uses the shipped
`light-cool` theme for its stock components in the same way.

Experiment E1 measured the mechanism on the gateway (page 07, GF-01 to GF-05): with `day`, the
page root resolved `--container-background-color` to `rgb(247, 247, 247)` and an inherited pump
icon's fill to `rgb(83, 83, 83)`; after the Night button, the root resolved to `rgb(0, 0, 0)`,
text to `rgb(234, 167, 94)`, and the same icon fills changed without a reload.

## 5. Icons

`tools/convert_icons.py` turns a package icon source (`src/icons/icon-<name>.ts`) into an
`ia.shapes.svg` element list. Each source carries two bodies: `icon`, every fill `currentColor`,
and `iconCss`, each fill a palette variable such as `var(--automation-device-primary-color)`. The
palette-aware body is converted, so an icon re-colours with the palette. Circles, rectangles,
lines and polygons are rewritten as path data, so only attested element keys are emitted (`type`,
`d`, `fill.paint`, `fill.rule`, `stroke.*`, `transform`).

92 icons are converted today (`library/icons/ICONS.txt`): every on and off state of the eight
device kinds in the library, the control and lock badges, the trend arrows, the frame icons
(menu, alerts, palettes, user, close), and two water sensor icons the water treatment sample uses
for navigation (page 11). They use seven palette variables between them. A further 2,009 icons are
available at the pinned commit; adding a name to `ICONS.txt` and re-running the
converter adds it to the library and to the `cadre.icons` script module.

## 6. Typography and Colour Classes

The parent carries 77 style classes:

| Group | Classes | Content |
|---|---|---|
| `cadre/font/*` | 48 | One per package type style, values as token references |
| `cadre/text/*` | 4 | `active`, `neutral`, `inactive`, `disabled` element colours |
| `cadre/surface/*` | 5 | `page`, `card`, `section`, `bar`, `menu` |
| `cadre/button/*` | 4 | `flat`, `normal`, `raised` (each with a hover variant) and `selected` |
| `cadre/alert/*` | 6 | `flash-*` animations and `badge-*` fills for alarm, warning and caution |
| `cadre/nav/*`, `cadre/divider/*`, `cadre/anim/*` | 4 | Navigation items, divider, spin |
| `cadre/palette/*` | 4 | The palette selectors (empty bodies; the stylesheet supplies the variables) |
| `cadre/text/ellipsis`, `cadre/box/within` | 2 | The layout classes (empty bodies; the stylesheet supplies the rules): a label that ends in an ellipsis, and a container no wider than its own (page 06 section 4.1) |

The idiom follows the reference: a component takes one `cadre/font/*` class for typography and one
`cadre/text/*` class for colour, space-separated in `style.classes`.

## 7. Attribution

`NOTICE` records the Apache-2.0 attribution for the derived token file and icon geometry, and
`LICENSES/Apache-2.0.txt` carries the licence text from the pinned commit. Every generated
stylesheet and icon module repeats the attribution in its header.
