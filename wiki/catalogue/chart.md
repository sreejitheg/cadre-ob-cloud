# Catalogue: Chart

Interface facts for the 4 components of the reference family `Chart`, parsed from the reference documentation. Defaults and enumerations are parsed from prose by heuristic and are marked so; an empty cell means the page states none. Back to [05 Component Catalogue](../05-component-catalogue.md).

## 1. Donut Chart

<a id="donut-chart"></a>

Disposition: `stock`. Cadre equivalent: `ia.chart.pie`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Data / Properties | `data` | array |  |  |
| Data / Properties | `max` | value | 100 |  |
| Layout / Properties | `half` | value | false |  |
| Layout / Properties | `thickness` | value | 24 |  |
| Colours / Properties | `priority` | value | regular |  |
| Colours / Properties | `colors` | array |  |  |
| Centre Readout / Properties | `centerReadoutLabel` | value | Total |  |
| Centre Readout / Properties | `centerReadoutUnit` | value | % |  |
| Outer Labels / Properties | `showOuterLabels` | value | false |  |
| Outer Labels / Properties | `showUnit` | value | false |  |
| Outer Labels / Properties | `outerLabelUnit` | value | % |  |
| Outer Labels / Properties | `outerLabelDecimalPlaces` | value | 0 |  |
| Outer Labels / Properties | `outerLabelMaxLength` | value | 0 |  |
| Legend / Properties | `legend` | value | false |  |
| Size / Properties | `fixedHeight` | value | 320 |  |
| Size / Properties | `showDebugOverlay` | value | false |  |

## 2. Graph Mini

<a id="graph-mini"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.sparkline`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Data / Properties | `data` | object |  |  |
| Range / Properties | `hasMinY` | value | false |  |
| Range / Properties | `minY` | value | 0 |  |
| Range / Properties | `hasMaxY` | value | false |  |
| Range / Properties | `maxY` | value | 0 |  |

## 3. Indicator Graph

<a id="indicator-graph"></a>

Disposition: `gap`. Cadre equivalent: None.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Data / Properties | `data` | object |  |  |
| Size and Priority / Properties | `layout` | object |  |  |
| Size and Priority / Properties | `layout.size` | value | medium | small, medium, large |
| Size and Priority / Properties | `layout.priority` | value | regular | regular, enhanced |
| Zero Line / Properties | `layout.y` | object |  |  |
| Zero Line / Properties | `layout.y.showZeroLine` | value | true |  |
| Range / Properties | `layout.y.hasMin` | value | false |  |
| Range / Properties | `layout.y.min` | value | 0 |  |
| Range / Properties | `layout.y.hasMax` | value | false |  |
| Range / Properties | `layout.y.max` | value | 100 |  |
| Properties | `style` | object |  |  |

## 4. Radial Bar Chart

<a id="radial-bar-chart"></a>

Disposition: `gap`. Cadre equivalent: None.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Data / Properties | `data` | array |  |  |
| Data / Properties | `max` | value | 100 |  |
| Arc / Properties | `circumference` | value | 270 |  |
| Rings / Properties | `minRingThickness` | value | 16 |  |
| Colours / Properties | `priority` | value | regular |  |
| Colours / Properties | `colors` | array |  |  |
| Legend / Properties | `legend` | value | false |  |
| Size / Properties | `fixedHeight` | value | 320 |  |
| Size / Properties | `showDebugOverlay` | value | false |  |
