# Catalogue: Automation

Interface facts for the 29 components of the reference family `Automation`, parsed from the reference documentation. Defaults and enumerations are parsed from prose by heuristic and are marked so; an empty cell means the page states none. Back to [05 Component Catalogue](../05-component-catalogue.md).

## 1. Analog Valve

<a id="analog-valve"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/AnalogValve` (`open`, `value`).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `open` | value | false |  |
| Properties | `value` | value | 0 |  |
| Properties | `labelDirection` | value | right | up, down, left, right, none |
| Properties | `variant` | value | regular |  |
| Properties | `vertical` | value | false |  |

## 2. Automation Badge

<a id="automation-badge"></a>

Disposition: `partial`. Cadre equivalent: Corner badges inside the symbols.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Type and Mode / Properties | `type` | value | auto |  |
| Type and Mode / Properties | `mode` | value | flat | flat, regular, enhanced |
| Size and Placement / Properties | `componentSize` | value | regular | regular, medium, large |
| Size and Placement / Properties | `style` | object |  |  |

## 3. Automation Readout

<a id="automation-readout"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Readout`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value and Unit / Properties | `value` | value | 0 |  |
| Value and Unit / Properties | `unit` | value |  |  |
| Value and Unit / Properties | `numberOfDigits` | value | 3 |  |
| Position / Properties | `position` | value | bottom | left, right, top, bottom |
| Position / Properties | `lineType` | value | fluid | fluid, electric, air, connector |
| Size / Properties | `componentSize` | value | regular | regular, medium, large |
| Size / Properties | `style` | object |  |  |

## 4. Automation Tank

<a id="automation-tank"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Tank` (level, trend, chart, compact, static).

The chart is a line sparkline, not the reference filled area chart (register COB-031).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Level / Properties | `value` | value | 0 |  |
| Level / Properties | `max` | value | 100 |  |
| Level / Properties | `valueFractionDigits` | value | 0 |  |
| Level / Properties | `maxFractionDigits` | value | 0 |  |
| Level / Properties | `percentFractionDigits` | value | 0 |  |
| Level / Properties | `hasCustomUnit` | value | false |  |
| Level / Properties | `unitText` | value | m³ |  |
| Trend / Properties | `trend` | value | stable | fast-rising, rising, stable, falling, fast-falling, closed |
| Trend / Properties | `showTrendSymbol` | value | true |  |
| Tag / Properties | `tag` | value |  |  |
| Type / Properties | `type` | value | generic | generic, atmospheric, pressurized, battery |
| Type / Properties | `hasGraphIcon` | value | false |  |
| Type / Properties | `medium` | value | water | normal, empty, water, air |
| Layout / Properties | `orientation` | value | vertical | vertical, horizontal |
| Layout / Properties | `compact` | value | false |  |
| Layout / Properties | `static` | value | false |  |
| Positioning / Properties | `positioning` | value | button |  |
| Chart / Properties | `chartMode` | value | bar | bar, graph, graph-and-bar |
| Chart / Properties | `chartData` | object |  |  |
| Chart / Properties | `priority` | value | regular | regular, enhanced |
| Chart / Properties | `hasAdvice` | value | false |  |
| Chart / Properties | `advice` | array |  |  |
| Chart / Properties | `advice[].min` | value | 0 |  |
| Chart / Properties | `advice[].max` | value | 10 |  |
| Chart / Properties | `advice[].type` | value | advice | advice, caution |
| Chart / Properties | `advice[].hinted` | value | false |  |
| Detail Rows / Properties | `readout` | array |  |  |
| Detail Rows / Properties | `readout[].label` | value | Label |  |
| Detail Rows / Properties | `readout[].value` | value | 0 |  |
| Detail Rows / Properties | `readout[].unit` | value |  |  |
| Detail Rows / Properties | `readout[].hasDegree` | value | false |  |
| Detail Rows / Properties | `readout[].numberFormat` | value | #,##0 |  |
| Clickable and Activated / Properties | `clickable` | value | true |  |
| Clickable and Activated / Properties | `activated` | value | false |  |
| Alert Frame / Properties | `alert` | value | false |  |
| Alert Frame / Properties | `alertFrameType` | value | small-side-flip | regular, small-side-flip, large-side-flip, bottom-flip, top-flip |
| Alert Frame / Properties | `alertFrameStatus` | value | alarm | value, alarm, warning, caution |
| Alert Frame / Properties | `alertFrameMode` | value | acked-active |  |
| Alert Frame / Properties | `alertFrameThickness` | value | small | small, large |
| Alert Frame / Properties | `showAlertCategoryIcon` | value | true |  |
| Alert Frame / Properties | `showAlertIcon` | value | false | large-side-flip, bottom-flip, top-flip |
| Alert Frame / Properties | `alertIcon` | object |  |  |
| Alert Frame / Properties | `alertIcon.path` | value | placeholder |  |
| Alert Frame / Properties | `alertLabel` | value | empty |  |
| Alert Frame / Properties | `alertTimer` | value | empty |  |
| Properties | `style` | object |  |  |

## 5. Bipolar Transistor

<a id="bipolar-transistor"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | bipolarTransistor01 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 6. Capacitor

<a id="capacitor"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | capacitor01 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 7. Common Features

<a id="automation-button"></a>

Disposition: `implemented`. Cadre equivalent: Common contract of every `Automation/*` symbol view.

Readout (status row and tag), readout side, activated, alert frame (status, mode), progress, and the four corner badges.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Readout / Properties | `showReadoutStack` | value | true |  |
| Readout / Properties | `readoutPosition` | value | bottom | top, bottom, left, right |
| Readout / Properties | `showStatus` | value | true |  |
| Readout / Properties | `readoutSize` | value | regular | small, regular, enhanced |
| Readout / Properties | `hasTag` | value | false |  |
| Readout / Properties | `tag` | value |  |  |
| Positioning / Properties | `positioning` | value | symbol | symbol, button, point |
| Size / Properties | `componentSize` | value | regular | regular, medium, large |
| Activated / Properties | `activated` | value | false |  |
| Alert Frame / Properties | `alert` | value | false |  |
| Alert Frame / Properties | `alertFrameType` | value | small-side-flip | regular, small-side-flip, large-side-flip, bottom-flip, top-flip |
| Alert Frame / Properties | `alertFrameStatus` | value | alarm | alarm, warning, caution |
| Alert Frame / Properties | `alertFrameMode` | value | acked-active | acked-active, unacked-active, unacked-rectified |
| Alert Frame / Properties | `alertFrameThickness` | value | small | small, large |
| Alert Frame / Properties | `showAlertCategoryIcon` | value | true |  |
| Alert Frame / Properties | `showAlertIcon` | value | false | large-side-flip, bottom-flip, top-flip |
| Alert Frame / Properties | `alertIcon` | object |  |  |
| Alert Frame / Properties | `alertIcon.path` | value | placeholder |  |
| Alert Frame / Properties | `alertLabel` | value | empty |  |
| Alert Frame / Properties | `alertTimer` | value | empty |  |
| Progress / Properties | `progress` | value | false |  |
| Progress / Properties | `progressMode` | value | indeterminate | determinate, indeterminate, progressive-indeterminate |
| Progress / Properties | `progressValue` | value | 0 |  |
| Badges / Properties | `badgeControl` | value | none | none, local, local-only, manual, manual-only, auto |
| Badges / Properties | `badgeAlert` | value | none | value, alarm, warning, caution, silence |
| Badges / Properties | `badgeInterlock` | value | none | none, interlock, interlock-inhibit |
| Badges / Properties | `badgeCommandLocked` | value | none | none, command-locked |
| Style | `style` | object |  |  |

## 8. Converter

<a id="converter"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | converterDcdc |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 9. Damper

<a id="damper"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Damper`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 10. Digital Valve

<a id="digital-valve"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Valve` (`open`).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `open` | value | false |  |
| Properties | `variant` | value | regular |  |
| Properties | `vertical` | value | false |  |

## 11. Diodes

<a id="diodes"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | diodes01 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 12. Fan

<a id="fan"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Fan`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `hasSpeed` | value | false |  |
| Properties | `speed` | value | 0 |  |
| Properties | `speedUnit` | value |  |  |
| Properties | `speedMaxDigits` | value | 3 |  |
| Properties | `speedInPercent` | value | 0 |  |
| Properties | `labelDirection` | value | right | up, down, left, right, none |
| Properties | `variant` | value | regular | regular, double, forward, flat, flat-forward |
| Properties | `direction` | value | forward | forward, forward-fast, forward-stopped, backward, backward-fast, backward-stopped, standby |

## 13. Filter

<a id="filter"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Filter`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | filter1 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 14. Gauge Valve

<a id="gauge-valve"></a>

Disposition: `gap`. Cadre equivalent: None.

Each needs its own layout beyond a two-state icon.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value | 0 |  |
| Value / Properties | `type` | value | two-way | two-way, three-way |
| Value / Properties | `bottomValue` | value | 0 |  |
| Compact and Large / Properties | `large` | value | false |  |
| Compact and Large / Properties | `label` | value |  |  |
| Compact and Large / Properties | `unit` | value |  |  |
| Compact and Large / Properties | `hasLabelStack` | value | true |  |
| Compact and Large / Properties | `tag` | value |  |  |
| Size / Properties | `hasFaceDiameter` | value | false |  |
| Size / Properties | `faceDiameter` | value | 0 |  |
| Size / Properties | `componentSize` | value | regular | regular, medium, large |
| Priority and Bar Style / Properties | `priority` | value | regular | regular, enhanced, medium, off |
| Priority and Bar Style / Properties | `barStyle` | value | tint | tint, fill |
| Scale Position / Properties | `scalePosition` | value | top | top, right, bottom, left |
| Setpoint / Properties | `hasSetpoint` | value | false |  |
| Setpoint / Properties | `setpoint` | value | 0 |  |
| Setpoint / Properties | `hasNewSetpoint` | value | false |  |
| Setpoint / Properties | `newSetpoint` | value | 0 |  |
| Setpoint / Properties | `atSetpoint` | value | false |  |
| Setpoint / Properties | `autoAtSetpoint` | value | false |  |
| Setpoint / Properties | `autoAtSetpointDeadband` | value | 0 |  |
| Setpoint / Properties | `touching` | value | false |  |
| Setpoint / Properties | `setpointOverride` | value | false |  |
| Setpoint / Properties | `setpointAtZeroDeadband` | value | 0 |  |
| Setpoint / Properties | `animateSetpoint` | value | false |  |
| Icon / Properties | `hasIcon` | value | false |  |
| Icon / Properties | `icon` | object |  |  |
| Icon / Properties | `icon.path` | value | placeholder |  |
| Properties | `style` | object |  |  |

## 15. Ground

<a id="ground"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | ground1 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 16. Heat Pump

<a id="heat-pump"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Medium / Properties | `medium` | value | regular | regular, graphic, medium |
| Medium / Properties | `showIcon` | value | true |  |
| Medium / Properties | `static` | value | false |  |
| Tag / Properties | `tag` | value |  |  |
| Positioning / Properties | `positioning` | value |  |  |
| Size / Properties | `componentSize` | value | regular | regular, medium, large |
| Clickable and Activated / Properties | `clickable` | value | true |  |
| Clickable and Activated / Properties | `activated` | value | false |  |
| Badges / Properties | `badgeControl` | value | none | none, local, local-only, manual, manual-only, auto |
| Badges / Properties | `badgeAlert` | value | none | value, alarm, warning, caution, silence |
| Badges / Properties | `badgeInterlock` | value | none | none, interlock, interlock-inhibit |
| Badges / Properties | `badgeCommandLocked` | value | none | none, command-locked |
| Alert Frame / Properties | `alert` | value | false |  |
| Alert Frame / Properties | `alertFrameType` | value | small-side-flip | regular, small-side-flip, large-side-flip, bottom-flip, top-flip |
| Alert Frame / Properties | `alertFrameStatus` | value | alarm | value, alarm, warning, caution |
| Alert Frame / Properties | `alertFrameMode` | value | acked-active |  |
| Alert Frame / Properties | `alertFrameThickness` | value | small | small, large |
| Alert Frame / Properties | `showAlertCategoryIcon` | value | true |  |
| Alert Frame / Properties | `showAlertIcon` | value | false |  |
| Alert Frame / Properties | `hasAlertIcon` | value | false |  |
| Alert Frame / Properties | `alertIcon` | object |  |  |
| Alert Frame / Properties | `alertIcon.path` | value | placeholder |  |
| Alert Frame / Properties | `alertLabel` | value | empty |  |
| Alert Frame / Properties | `alertTimer` | value | empty |  |
| Properties | `style` | object |  |  |

## 17. Hydraulic Check Valve

<a id="hydraulic-check-valve"></a>

Disposition: `gap`. Cadre equivalent: None.

Each needs its own layout beyond a two-state icon.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Orientation / Properties | `vertical` | value | false |  |
| Size and Placement / Properties | `componentSize` | value | regular | regular, medium, large |
| Size and Placement / Properties | `style` | object |  |  |

## 18. Logic

<a id="logic"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | logic01 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 19. Mosfet

<a id="mosfet"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | mosfetNtype1 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 20. Motor

<a id="motor"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Motor`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `hasSpeed` | value | false |  |
| Properties | `speed` | value | 0 |  |
| Properties | `speedUnit` | value |  |  |
| Properties | `speedMaxDigits` | value | 3 |  |
| Properties | `speedInPercent` | value | 0 |  |
| Properties | `labelDirection` | value | right | up, down, left, right, none |
| Properties | `variant` | value | regular | regular, double, forward, flat, flat-forward |
| Properties | `direction` | value | forward | forward, forward-fast, forward-stopped, backward, backward-fast, backward-stopped, standby |
| Properties | `vertical` | value | false |  |

## 21. Pump

<a id="pump"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Pump` (`on`, `speed`, `variant` regular or double).

`componentSize` medium (52 px holder) is not implemented (register COB-030).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `hasSpeed` | value | false |  |
| Properties | `speed` | value | 0 |  |
| Properties | `speedUnit` | value |  |  |
| Properties | `speedMaxDigits` | value | 3 |  |
| Properties | `speedInPercent` | value | 0 |  |
| Properties | `labelDirection` | value | right | up, down, left, right, none |
| Properties | `variant` | value | regular | regular, double, forward, flat, flat-forward |
| Properties | `direction` | value | forward | forward, forward-fast, forward-stopped, backward, backward-fast, backward-stopped, standby |
| Properties | `vertical` | value | false |  |

## 22. Resistor

<a id="resistor"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | resistor1 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 23. Router

<a id="router"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | router |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 24. Source

<a id="source"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | sources01 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 25. Switch

<a id="switch"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Switch`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | regular |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 26. Transformer

<a id="transformer"></a>

Disposition: `factory`. Cadre equivalent: One row in `DEVICE_KINDS` (`tools/hmi/library.py`); the on and off artwork exists.

Electrical single-line symbols; add when a screen needs them.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `on` | value | false |  |
| Properties | `alternativeIcon` | value | transformer01 |  |
| Properties | `variant` | value | square |  |
| Properties | `orientation` | value | horizontal | horizontal, verticalRight, verticalLeft |

## 27. Transmitter

<a id="transmitter"></a>

Disposition: `gap`. Cadre equivalent: None.

Each needs its own layout beyond a two-state icon.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Type / Properties | `type` | value | value | indicator, value, horizontal-graph, vertical-graph |
| Type / Properties | `data` | object |  |  |
| Value / Properties | `value` | value | 0 |  |
| Value / Properties | `unit` | value |  |  |
| Value / Properties | `numberFormat` | value |  |  |
| Value / Properties | `hintedZeros` | value | false |  |
| Value / Properties | `hasSignSpacer` | value | false |  |
| Value / Properties | `hasDegree` | value | false |  |
| Value / Properties | `hasIcon` | value | false |  |
| Value / Properties | `icon` | object |  |  |
| Value / Properties | `icon.path` | value | placeholder |  |
| Tags / Properties | `idTag` | value |  |  |
| Tags / Properties | `tag` | value |  |  |
| Advice and Setpoint / Properties | `hasAdvice` | value | false |  |
| Advice and Setpoint / Properties | `adviceValue` | value | 0 |  |
| Advice and Setpoint / Properties | `hasSetPoint` | value | false |  |
| Advice and Setpoint / Properties | `setpointValue` | value | 0 |  |
| Alert / Properties | `hasAlert` | value | false |  |
| Alert / Properties | `alertFrameStatus` | value | alarm | value, alarm, warning, caution |
| Alert / Properties | `alertFrameType` | value | regular | regular, small-side-flip, large-side-flip, bottom-flip, top-flip |
| Alert / Properties | `alertFrameThickness` | value | small | small, large |
| Alert / Properties | `alertFrameMode` | value | acked-active |  |
| Alert / Properties | `showAlertCategoryIcon` | value | true |  |
| Alert / Properties | `showAlertIcon` | value | false | large-side-flip, bottom-flip, top-flip |
| Alert / Properties | `alertIcon` | object |  |  |
| Alert / Properties | `alertIcon.path` | value | placeholder |  |
| Alert / Properties | `alertLabel` | value | empty |  |
| Alert / Properties | `alertTimer` | value | empty |  |
| Orientation / Properties | `orientation` | value | bottom | top, right, bottom, left |
| Size / Properties | `size` | value | regular | regular, medium, large |
| Size / Properties | `componentSize` | value | regular | regular, medium, large |
| Size / Properties | `style` | object |  |  |

Events: `onActionPerformed`.

## 28. Transmitter Stack

<a id="transmitter-stack"></a>

Disposition: `gap`. Cadre equivalent: None.

Each needs its own layout beyond a two-state icon.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Values / Properties | `values` | array |  |  |
| Values / Properties | `values[].value` | value | 0 |  |
| Values / Properties | `values[].unit` | value |  |  |
| Values / Properties | `values[].idTag` | value |  |  |
| Values / Properties | `values[].numberFormat` | value |  |  |
| Values / Properties | `values[].hintedZeros` | value | false |  |
| Values / Properties | `values[].hasSignSpacer` | value | false |  |
| Values / Properties | `values[].hasDegree` | value | false |  |
| Values / Properties | `values[].hasIcon` | value | false |  |
| Values / Properties | `values[].icon` | object |  |  |
| Values / Properties | `values[].icon.path` | value | placeholder |  |
| Orientation / Properties | `orientation` | value | bottom | top, right, bottom, left |
| Properties | `componentSize` | value | regular | regular, medium, large |
| Properties | `style` | object |  |  |

Events: `onValueClick`.

## 29. Valve

<a id="valve"></a>

Disposition: `implemented`. Cadre equivalent: `Automation/Valve` (`open`).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `valveType` | value | analog | analog, digital |
| Properties | `open` | value | false |  |
| Properties | `value` | value | 0 |  |
| Properties | `labelDirection` | value | right |  |
| Properties | `variant` | value | regular |  |
| Properties | `vertical` | value | false |  |
