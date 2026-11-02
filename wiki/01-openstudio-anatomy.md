---
title: OpenStudio anatomy
type: wiki
updated: 2026-10-07
---
# 01 OpenStudio Anatomy

| Field | Value |
|---|---|
| Document ID | COB-WIKI-01 |
| Revision | A |
| Status | Issued for use |
| Evidence | `reference/openstudio-docs/` (137 pages), `reference/openstudio-demo-project/` (179 files), the running demo observed on 2026-10-07; all local only |

## 1. Purpose

This page records what the OpenStudio product is, how it is built, and which parts of it a
Cadre project may and may not use. It is the starting point for every other page in this wiki.

## 2. Product Composition

OpenStudio ("Next-Gen HMI for Ignition", openstudio.no, a company in Drammen, Norway) is sold as
four parts that work together.

Table 1. The four parts of the product.

| Part | What it is | Evidence |
|---|---|---|
| Ignition module | `ObComponents-<version>-8.3.modl` and `-8.1.modl`, named "OpenBridge for Ignition" in the module list. It registers native Perspective components. EUR 2,000 per gateway, EUR 200 per edge device, both perpetual, maintenance 16 per cent a year. Without a licence it runs in the two hour trial mode | Getting Started page; product page |
| Component library | 130 and more components in seven palette sections: Connector Diagram, App, Input, Automation, Maritime, Chart and Embedding | Documentation sidebar (section 3) |
| Application framework | A shared top dock with a Top Bar, a navigation menu opened from it, pages built from cards, a brilliance menu for the palette, alerts in the bar and on an alerts page | App overview and Top Bar pages; demo project |
| Design system | The OpenBridge design system (Ocean Industries Concept Lab, Oslo School of Architecture and Design): palettes, typography, component sizes and icons, implemented as Lit web components | Footer of every documentation page; the module's `obc-*` elements in the running demo |

The module wraps the OpenBridge web components. In the running demo the Top Bar is the custom
element `obc-top-bar` with `obc-alert-button`, `obc-clock` and `obc-topbar-message-item` inside
its shadow root, and each automation symbol is an `obc-*` element (`obc-pump`,
`obc-digital-valve`, `obc-automation-tank`).

## 3. Component Families

Table 2. The documented catalogue by palette section (`catalogue/openstudio-interface.json`).

| Section | Components | Documented properties | Perspective type prefix in the demo |
|---|---|---|---|
| Connector Diagram | 1 | 30 | `openbridge.manual.connector-diagram` |
| App | 12 | 239 | `openbridge.manual.*` |
| Input | 33 | 326 | `openbridge.manual.*` |
| Automation | 29 | 286 | `automation.<name>.<name>` |
| Maritime | 50 | 769 | `navigation-instruments.<name>.<name>` |
| Chart | 4 | 41 | `openbridge.manual.*` |
| Embedding | 6 | 97 | `openbridge.manual.*` |
| Total | 135 | 1,788 | |

The 135 entries include four common-feature pages (App overview, Input, Automation Buttons and
Maritime), so the component count proper is 131. The documentation also declares 80 component
events.

## 4. The Demo Project as a Parent Template

On an 8.3 gateway the module creates a project named `OpenBridge_template` from a demo project it
bundles (release v1.2.0) and never overwrites it afterwards. The project is inheritable: it is
meant as the parent of customer projects or as a project to duplicate. The same project is
published as `OpenBridge_demo_v1.2.0.zip` on GitHub (`Ocean-Industries-Concept-Lab/Ignition-demo-project`).

Table 3. The demo project's resources.

| Resource | Content |
|---|---|
| `project.json` | Title `OpenBridge`, inheritable, no parent |
| `page-config` | Routes `/`, `/alerts`, `/alerts/:alarmId`, `/card`, `/ias`, `/maritime`; shared top dock `Docks/Header` (48 px, visible, push) and left dock `Docks/Menu` (320 px, on demand, cover); a right dock `Docks/Sidemenu` (500 px, on demand, push) on the `/` route only |
| `views` | 17: two docks, the side menu with pump and valve faceplates and device list items, six pages, and two symbol sub-views used by the process overview |
| `style-classes` | 60, in the idiom one `font/*` class (typography only) plus one `text-color/*` class (colour only) |
| `stylesheet.css` | 5,073 bytes: card, flat button and scrollbar rules over OpenBridge CSS variables the module supplies |
| `session-props` | `theme: light-cool`, and custom `hoverId`, `showReadout`, `showTag` |
| Tags | Not included: the views bind to the default provider (`process`, `Project`) and to a provider named `Sample_Tags` |

The repository also carries a `CLAUDE.md` and three Claude Code skills (project scan, trial reset,
style classes): the vendor builds the demo with an agent, as this work does.

## 5. Licences and Their Consequences

Table 4. What each source permits.

| Source | Licence | Consequence for Cadre |
|---|---|---|
| OpenStudio module | Commercial, per gateway | Not installed, not downloaded, not decompiled. The owner asked for inspiration, not the product |
| Documentation site | No licence statement; its `robots.txt` carries the content-signal preamble with no signal set, and an EU directive 2019/790 reservation note | Read for interface facts. Prose is not reproduced in tracked files (decision COBD-002) |
| Demo project (GitHub) | No licence file: all rights reserved | Read for study under `reference/` (local only). Nothing is copied into tracked files; layout facts reach only a local test fixture (COBD-007) |
| Running demo site | `robots.txt` disallows all automated access | Observed interactively in a browser at the owner's request; never automated |
| OpenBridge web components | Apache-2.0 for 281 of 309 npm versions; from 2026-09-17 AGPL-3.0 with each version becoming Apache-2.0 180 days after publication | Tokens, typography and icon artwork are taken from 2.0.0-next.155 (2026-09-16, Apache-2.0), with attribution in `NOTICE` (COBD-003) |

## 6. Related Pages

- [02 Export feasibility](02-export-feasibility.md): what each source yields and how it was extracted.
- [03 Design system](03-design-system.md): the OpenBridge tokens as adopted.
- [04 Navigation and frame](04-navigation-and-frame.md): the application frame recreated.
- [05 Component catalogue](05-component-catalogue.md): all 135 entries with their properties.
