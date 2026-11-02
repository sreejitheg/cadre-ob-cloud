# Catalogue: Connector Diagram

Interface facts for the 1 components of the vendor family `Connector Diagram`, parsed from the vendor documentation (source link per component). Defaults and enumerations are parsed from prose by heuristic and are marked so; an empty cell means the page states none. Back to [05 Component Catalogue](../05-component-catalogue.md).

## 1. Connector Diagram

<a id="connector-diagram"></a>

Source: <https://docs.openstudio.no/connector-diagram/>. Disposition: `generator`. Cadre equivalent: `tools/hmi/screen.py` diagram layout: sections, symbols, routed pipes, compiled flow (`tools/hmi/diagram.py`).

Pipes are drawn by the generator, not in the Designer; flow is compiled into one expression per pipe and verified against a reference solver (gate G6).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Finding a Pipe and Changing Its Properties / Pipe Properties | `state` | value | open | open, empty, closed |
| Finding a Pipe and Changing Its Properties / Pipe Properties | `flow` | value | auto |  |
| Finding a Pipe and Changing Its Properties / Pipe Properties | `mediumId` | value |  |  |
| Finding a Pipe and Changing Its Properties / Pipe Properties | `mediumColor` | value |  |  |
| Finding a Pipe and Changing Its Properties / Pipe Properties | `size` | value | inherit |  |
| Finding a Pipe and Changing Its Properties / Pipe Properties | `visible` | value | true |  |
| Finding a Pipe and Changing Its Properties / Pipe Properties | `direction` | value | none |  |
| Finding a Pipe and Changing Its Properties / Pipe Properties | `directionPosition` | value | center | start, center, end |
| Finding a Pipe and Changing Its Properties / Pipe Properties | `from, to` | object |  |  |
| User Toolbar / Properties | `showViewModeToggle` | value | true |  |
| User Toolbar / Properties | `showLegend` | value | true |  |
| User Toolbar / Properties | `showEmptyLegend` | value | false |  |
| User Toolbar / Properties | `showTagToggle` | value | true |  |
| User Toolbar / Properties | `showTag` | value | false |  |
| User Toolbar / Properties | `showReadoutToggle` | value | true |  |
| User Toolbar / Properties | `showReadout` | value | false |  |
| User Toolbar / Properties | `showZoomToggle` | value | false |  |
| User Toolbar / Properties | `showRightPanelOpenButton` | value | false |  |
| User Toolbar / Properties | `rightPanelOpen` | value | false |  |
| Sections and Mini-map / Properties | `zones` | object |  |  |
| Sections and Mini-map / Properties | `minimap.enabled` | value | false |  |
| Sections and Mini-map / Properties | `minimap.corner` | value | top-right |  |
| Sections and Mini-map / Properties | `view.zoom` | value | 1 |  |
| Properties | `editable` | value | true |  |
| Properties | `gridSize` | value | 24 |  |
| Properties | `viewMode` | value | regular | regular, medium |
| Properties | `flow` | object | on |  |
| Properties | `connections` | object |  |  |
| Properties | `nodes` | object |  |  |
| Properties | `style` | object |  |  |

Events: `onZoneExpanded`, `onZoneCollapsed`.
