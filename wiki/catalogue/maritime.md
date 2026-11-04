# Catalogue: Maritime

Interface facts for the 50 components of the reference family `Maritime`, parsed from the reference documentation. Defaults and enumerations are parsed from prose by heuristic and are marked so; an empty cell means the page states none. Back to [05 Component Catalogue](../05-component-catalogue.md).

## 1. Azimuth Thruster

<a id="azimuth-thruster"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Angle and Thrust / Properties | `angle` | value | 0 |  |
| Angle and Thrust / Properties | `thrust` | value | 0 |  |
| Angle and Thrust / Properties | `singleDirection` | value | false |  |
| Angle Setpoint / Properties | `hasAngleSetpoint` | value | false |  |
| Angle Setpoint / Properties | `angleSetpoint` | value |  |  |
| Angle Setpoint / Properties | `autoAtAngleSetpoint` | value | true |  |
| Angle Setpoint / Properties | `autoAtAngleSetpointDeadband` | value | 2 |  |
| Angle Setpoint / Properties | `atAngleSetpoint` | value | false |  |
| Angle Setpoint / Properties | `hasNewAngleSetpoint` | value | false |  |
| Angle Setpoint / Properties | `newAngleSetpoint` | value |  |  |
| Angle Setpoint / Properties | `angleSetpointAtZeroDeadband` | value |  |  |
| Angle Setpoint / Properties | `angleSetpointOverride` | value | false |  |
| Angle Setpoint / Properties | `angleAdvices` | array |  |  |
| Thrust Setpoint / Properties | `hasThrustSetpoint` | value | false |  |
| Thrust Setpoint / Properties | `thrustSetpoint` | value |  |  |
| Thrust Setpoint / Properties | `autoAtThrustSetpoint` | value | true |  |
| Thrust Setpoint / Properties | `autoAtThrustSetpointDeadband` | value | 1 |  |
| Thrust Setpoint / Properties | `atThrustSetpoint` | value | false |  |
| Thrust Setpoint / Properties | `hasNewThrustSetpoint` | value | false |  |
| Thrust Setpoint / Properties | `newThrustSetpoint` | value |  |  |
| Thrust Setpoint / Properties | `thrustSetpointAtZeroDeadband` | value |  |  |
| Thrust Setpoint / Properties | `thrustSetpointOverride` | value | false |  |
| Thrust Setpoint / Properties | `thrustAdvices` | array |  |  |
| Thrust Setpoint / Properties | `touching` | value | false |  |
| Thrust Setpoint / Properties | `animateSetpoint` | value | false |  |
| Scale / Properties | `hasPrimaryTickmarkInterval` | value | false |  |
| Scale / Properties | `primaryTickmarkInterval` | value | 90 |  |
| Scale / Properties | `hasSecondaryTickmarkInterval` | value | false |  |
| Scale / Properties | `secondaryTickmarkInterval` | value |  |  |
| Scale / Properties | `hasTertiaryTickmarkInterval` | value | false |  |
| Scale / Properties | `tertiaryTickmarkInterval` | value |  |  |
| Scale / Properties | `hasLabelSpacer` | value | true |  |
| Scale / Properties | `starboardPortIndicator` | value | false |  |
| Propellers / Properties | `topPropeller` | value | none | none, cap, single |
| Propellers / Properties | `bottomPropeller` | value | none | none, cap, single |
| Properties | `loading` | value | 0 |  |

## 2. Azimuth Thruster Labeled

<a id="azimuth-thruster-labeled"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `label` | value |  |  |
| Properties | `commandStatus` | value | in-command |  |
| Properties | `size` | value | medium | medium, large |
| Properties | `readoutSize` | value | large |  |
| Properties | `angle` | value | 0 |  |
| Properties | `thrust` | value | 0 |  |
| Properties | `hasAngleSetpoint` | value | false |  |
| Properties | `angleSetpoint` | value |  |  |
| Properties | `hasNewAngleSetpoint` | value | false |  |
| Properties | `newAngleSetpoint` | value |  |  |
| Properties | `autoAtAngleSetpoint` | value | true |  |
| Properties | `autoAtAngleSetpointDeadband` | value | 2 |  |
| Properties | `atAngleSetpoint` | value | false |  |
| Properties | `angleSetpointAtZeroDeadband` | value |  |  |
| Properties | `angleSetpointOverride` | value | false |  |
| Properties | `touching` | value | false |  |
| Properties | `hasThrustSetpoint` | value | false |  |
| Properties | `thrustSetpoint` | value |  |  |
| Properties | `autoAtThrustSetpoint` | value | true |  |
| Properties | `autoAtThrustSetpointDeadband` | value | 1 |  |
| Properties | `atThrustSetpoint` | value | false |  |
| Properties | `thrustSetpointAtZeroDeadband` | value |  |  |
| Properties | `thrustSetpointOverride` | value | false |  |
| Properties | `angleAdvices` | array |  |  |
| Properties | `thrustAdvices` | array |  |  |
| Properties | `tickmarkStyle` | value | regular | regular, enhanced |
| Properties | `singleDirection` | value | false |  |
| Properties | `topPropeller` | value | none | none, cap, single |
| Properties | `bottomPropeller` | value | none | none, cap, single |
| Properties | `style` | object |  |  |

## 3. Bearing Indicator

<a id="bearing-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Bearing / Properties | `bearingDeg` | value | 0 |  |
| Properties | `style` | object |  |  |

## 4. Common Features

<a id="maritime"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Common features page of the maritime family.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| State / Properties | `state` | value | active | active, loading, off |
| Priority / Properties | `priority` | value | regular | regular, enhanced |
| Setpoint / Properties | `hasSetpoint` | value | false |  |
| Setpoint / Properties | `setpoint` | value |  |  |
| Setpoint / Properties | `autoAtSetpoint` | value | false |  |
| Setpoint / Properties | `autoAtSetpointDeadband` | value |  |  |
| Setpoint / Properties | `atSetpoint` | value | false |  |
| Setpoint / Properties | `touching` | value | false |  |
| Setpoint / Properties | `hasNewSetpoint` | value | false |  |
| Setpoint / Properties | `newSetpoint` | value |  |  |
| Setpoint / Properties | `animateSetpoint` | value | false |  |
| Setpoint / Properties | `setpointAtZeroDeadband` | value |  |  |
| Setpoint / Properties | `setpointOverride` | value | false |  |
| Advice Zones | `minAngle` | value |  |  |
| Advice Zones | `maxAngle` | value |  |  |
| Advice Zones | `type` | value |  |  |
| Advice Zones | `hinted` | value |  |  |
| Scale | `showLabels` |  |  |  |
| Scale | `tickmarksInside` |  |  |  |
| Scale | `tickmarkStyle` |  |  |  |
| Size / Properties | `hasFaceDiameter` | value | false |  |
| Size / Properties | `faceDiameter` | value |  |  |
| Style and Events | `style` | object |  |  |

## 5. Compass

<a id="compass"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Heading and Course / Properties | `heading` | value | 0 |  |
| Heading and Course / Properties | `courseOverGround` | value | 0 |  |
| Heading and Course / Properties | `hdgArrowStyle` | value | arrowHead | arrowHead, needle, vector, beamLine |
| Heading and Course / Properties | `cogArrowStyle` | value | arrowHead | arrowHead, needle, vector, velocityVector |
| Orientation / Properties | `direction` | value | northUp | northUp, headingUp, courseUp |
| Orientation / Properties | `showLabels` | value | false |  |
| Orientation / Properties | `tickmarksInside` | value | false |  |
| Heading Setpoint / Properties | `headingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `autoAtHeadingSetpoint` | value | true |  |
| Heading Setpoint / Properties | `autoAtHeadingSetpointDeadband` | value | 2 |  |
| Heading Setpoint / Properties | `atHeadingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `touching` | value | false |  |
| Heading Setpoint / Properties | `hasNewHeadingSetpoint` | value | false |  |
| Heading Setpoint / Properties | `newHeadingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `animateSetpoint` | value | false |  |
| Heading Setpoint / Properties | `headingSetpointAtZeroDeadband` | value |  |  |
| Heading Setpoint / Properties | `headingSetpointOverride` | value | false |  |
| Heading Setpoint / Properties | `headingAdvices` | array |  |  |
| Rate of Turn / Properties | `hasRateOfTurnDegreesPerMinute` | value | false |  |
| Rate of Turn / Properties | `rateOfTurnDegreesPerMinute` | value |  |  |
| Rate of Turn / Properties | `rotType` | value | dots | dots, bar |
| Rate of Turn / Properties | `rotPosition` | value | innerCircle | innerCircle, scale |
| Rate of Turn / Properties | `rotDotAnimationFactor` | value | 18 |  |
| Rate of Turn / Properties | `rotMaxValue` | value | 60 |  |
| Rate of Turn / Properties | `rotArcExtent` | value | 60 |  |
| Rate of Turn / Properties | `rotAtZeroDeadband` | value |  |  |
| Rate of Turn / Properties | `rotPortStarboard` | value | false |  |
| Rate of Turn / Properties | `rotationsPerMinute` | value | 1 |  |
| Wind and Current / Properties | `windFromDirection` | value |  |  |
| Wind and Current / Properties | `currentWindSpeedKnots` | value |  |  |
| Wind and Current / Properties | `currentFromDirection` | value |  |  |
| Wind and Current / Properties | `currentSpeed` | value |  |  |
| Centre / Properties | `vesselImage` | value | generic-top |  |
| Centre / Properties | `centerReadouts` | array |  | hdg, cog, rot |
| State and Priority / Properties | `priorityElements` | array |  |  |

## 6. Compass Flat

<a id="compass-flat"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Heading and Course / Properties | `heading` | value | 0 |  |
| Heading and Course / Properties | `courseOverGround` | value | 0 |  |
| Heading and Course / Properties | `minFOV` | value | 45 |  |
| Heading and Course / Properties | `maxFOV` | value | 180 |  |
| Heading and Course / Properties | `FOV` | value | 45 |  |
| Heading and Course / Properties | `FOVIndicator` | value | false |  |
| Heading and Course / Properties | `tickInterval` | value | 5 |  |
| Rate of Turn / Properties | `rotType` | value | dots | dots, bar |
| Rate of Turn / Properties | `hasRateOfTurnDegreesPerMinute` | value | false |  |
| Rate of Turn / Properties | `rateOfTurnDegreesPerMinute` | value |  |  |
| Rate of Turn / Properties | `rotDotAnimationFactor` | value | 18 |  |
| Rate of Turn / Properties | `rotMaxValue` | value | 60 |  |
| Rate of Turn / Properties | `rotArcExtent` | value | 60 |  |
| Rate of Turn / Properties | `rotAtZeroDeadband` | value |  |  |
| Rate of Turn / Properties | `rotPortStarboard` | value | false |  |
| Rate of Turn / Properties | `rotationsPerMinute` | value | 1 |  |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |
| Priority / Properties | `priority` | value | regular | regular, enhanced |
| Priority / Properties | `priorityElements` | array |  |  |
| Properties | `style` | object |  |  |

## 7. Compass Indicator

<a id="compass-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Direction and Type / Properties | `angle` | value | 0 |  |
| Direction and Type / Properties | `direction` | value | heading | heading, course, north |
| Direction and Type / Properties | `type` | value | regular | regular, labeled |
| North Up or Heading Up / Properties | `northUp` | value | true |  |
| Properties | `style` | object |  |  |

## 8. Compass Sector

<a id="compass-sector"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Heading and Course / Properties | `heading` | value | 0 |  |
| Heading and Course / Properties | `courseOverGround` | value | 0 |  |
| Heading and Course / Properties | `minFOV` | value | 30 |  |
| Heading and Course / Properties | `tickmarksInside` | value | false |  |
| Heading Setpoint / Properties | `headingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `autoAtHeadingSetpoint` | value | true |  |
| Heading Setpoint / Properties | `autoAtHeadingSetpointDeadband` | value | 2 |  |
| Heading Setpoint / Properties | `atHeadingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `touching` | value | false |  |
| Heading Setpoint / Properties | `hasNewHeadingSetpoint` | value | false |  |
| Heading Setpoint / Properties | `newHeadingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `animateSetpoint` | value | false |  |
| Heading Setpoint / Properties | `headingSetpointAtZeroDeadband` | value |  |  |
| Heading Setpoint / Properties | `headingSetpointOverride` | value | false |  |
| Heading Setpoint / Properties | `headingAdvices` | array |  |  |
| Rate of Turn / Properties | `rotType` | value | dots | dots, bar |
| Rate of Turn / Properties | `rotPosition` | value | innerCircle | innerCircle, scale |
| Rate of Turn / Properties | `hasRateOfTurnDegreesPerMinute` | value | false |  |
| Rate of Turn / Properties | `rateOfTurnDegreesPerMinute` | value |  |  |
| Rate of Turn / Properties | `rotDotAnimationFactor` | value | 18 |  |
| Rate of Turn / Properties | `rotMaxValue` | value | 60 |  |
| Rate of Turn / Properties | `rotAtZeroDeadband` | value |  |  |
| Rate of Turn / Properties | `rotPortStarboard` | value | false |  |
| Rate of Turn / Properties | `rotationsPerMinute` | value | 1 |  |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |
| State and Priority / Properties | `priorityElements` | array |  |  |
| Size / Properties | `zoomToFitArc` | value | false |  |

## 9. Depth Actual

<a id="depth-actual"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Depth and Draught / Properties | `depth` | value | 0 |  |
| Depth and Draught / Properties | `draft` | value | 0 |  |
| Range / Properties | `autoRange` | value | false |  |
| Range / Properties | `hasInstrumentRange` | value | false |  |
| Range / Properties | `instrumentRange` | value |  |  |
| Range / Properties | `hasMaxDepth` | value | false |  |
| Range / Properties | `maxDepth` | value |  |  |
| Range / Properties | `ranges` | array |  |  |
| Range / Properties | `hasPrimaryTickmarkInterval` | value | false |  |
| Range / Properties | `primaryTickmarkInterval` | value |  |  |
| Range / Properties | `hasSecondaryTickmarkInterval` | value | false |  |
| Range / Properties | `secondaryTickmarkInterval` | value |  |  |
| Vessel / Properties | `vesselImage` | value | psv-fore |  |
| Vessel / Properties | `vesselScale` | value | 1 |  |
| Labels, Advice Zones and Priority / Properties | `showLabels` | value | true |  |
| Labels, Advice Zones and Priority / Properties | `advice` | array |  |  |
| Labels, Advice Zones and Priority / Properties | `priority` | value | regular | regular, enhanced |
| Properties | `style` | object |  |  |

## 10. Depth Indicator

<a id="depth-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Values / Properties | `values` | array |  |  |
| Variant / Properties | `variant` | value | outline | outline, filled |
| Properties | `style` | object |  |  |

## 11. Gauge Bar Indicator

<a id="gauge-bar-indicator"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.linear-scale` or `ia.display.progress`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value | 50 |  |
| Direction and Type / Properties | `direction` | value |  | vertical, horizontal |
| Direction and Type / Properties | `type` | value |  | fill, tinted |
| Properties | `style` | object |  |  |

## 12. Gauge Horizontal

<a id="gauge-horizontal"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.linear-scale` or `ia.display.progress`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value and Range / Properties | `hasValue` | value | false |  |
| Value and Range / Properties | `value` | value |  |  |
| Value and Range / Properties | `minValue` | value | 0 |  |
| Value and Range / Properties | `maxValue` | value | 100 |  |
| Value and Range / Properties | `reverse` | value | false |  |
| Fill / Properties | `fillMode` | value | fill | fill, tint |
| Fill / Properties | `highlightCurrentValue` | value | false |  |
| Fill / Properties | `hasFillMin` | value | false |  |
| Fill / Properties | `fillMin` | value |  |  |
| Fill / Properties | `hasFillMax` | value | false |  |
| Fill / Properties | `fillMax` | value |  |  |
| Scale / Properties | `side` | value | bottom | bottom, top |
| Scale / Properties | `showLabels` | value | true |  |
| Scale / Properties | `hasPrimaryTickmarkInterval` | value | false |  |
| Scale / Properties | `primaryTickmarkInterval` | value |  |  |
| Scale / Properties | `hasSecondaryTickmarkInterval` | value | false |  |
| Scale / Properties | `secondaryTickmarkInterval` | value |  |  |
| Scale / Properties | `hasTertiaryTickmarkInterval` | value | false |  |
| Scale / Properties | `tertiaryTickmarkInterval` | value |  |  |
| Scale / Properties | `mainTickmarks` | array |  |  |
| Scale / Properties | `borderRadiusPosition` | value | innerFirstChild | innerFirstChild, middleChild, middleRoundedChild, outerLastChild |

## 13. Gauge Radial

<a id="gauge-radial"></a>

Disposition: `stock`. Cadre equivalent: `ia.chart.gauge` or `ia.chart.simple-gauge` with Cadre colours.

Visual parity with the reference gauge is not claimed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Range and Scale / Properties | `value` | value | 0 |  |
| Range and Scale / Properties | `minValue` | value | 0 |  |
| Range and Scale / Properties | `maxValue` | value | 100 |  |
| Range and Scale / Properties | `primaryTickmarkInterval` | value | 50 |  |
| Range and Scale / Properties | `secondaryTickmarkInterval` | value | 10 |  |
| Range and Scale / Properties | `hasTertiaryTickmarkInterval` | value | false |  |
| Range and Scale / Properties | `tertiaryTickmarkInterval` | value |  |  |
| Type / Properties | `type` | value | filled | filled, bar, needle |
| Sector / Properties | `sector` | value | 270 |  |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |
| Size and Alignment / Properties | `horizontalAlignment` | value | center | left, center, right |
| Size and Alignment / Properties | `verticalAlignment` | value | center | top, center, bottom |

## 14. Gauge Radial Indicator

<a id="gauge-radial-indicator"></a>

Disposition: `stock`. Cadre equivalent: `ia.chart.gauge` or `ia.chart.simple-gauge` with Cadre colours.

Visual parity with the reference gauge is not claimed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value | 33 |  |
| Value / Properties | `minValue` | value | 0 |  |
| Value / Properties | `maxValue` | value | 100 |  |
| Sector and Style / Properties | `sector` | value | 270 |  |
| Sector and Style / Properties | `styleType` | value | regular |  |
| Icon / Properties | `hasIcon` | value | false |  |
| Icon / Properties | `icon` | value |  |  |
| Properties | `style` | object |  |  |

## 15. Gauge Trend

<a id="gauge-trend"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.sparkline` beside an `Instrument/Field`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Data / Properties | `data` | object |  |  |
| Scale and Value / Properties | `hasScale` | value | false |  |
| Scale and Value / Properties | `hasValue` | value | false |  |
| Scale and Value / Properties | `value` | value |  |  |
| Scale and Value / Properties | `minValue` | value | 0 |  |
| Scale and Value / Properties | `maxValue` | value | 100 |  |
| Scale and Value / Properties | `hasBar` | value | false |  |
| Scale and Value / Properties | `fillMode` | value | fill | fill, tint |
| Scale and Value / Properties | `fillMin` | value | 0 |  |
| Scale and Value / Properties | `hasFillMax` | value | false |  |
| Scale and Value / Properties | `fillMax` | value |  |  |
| Scale and Value / Properties | `scaleType` | value | regular | regular, condensed |
| Scale and Value / Properties | `hasPrimaryTickmarkInterval` | value | false |  |
| Scale and Value / Properties | `primaryTickmarkInterval` | value |  |  |
| Scale and Value / Properties | `secondaryTickmarkInterval` | value |  |  |
| Scale and Value / Properties | `hasTertiaryTickmarkInterval` | value | false |  |
| Scale and Value / Properties | `tertiaryTickmarkInterval` | value |  |  |
| Scale and Value / Properties | `hasYStepSize` | value | false |  |
| Scale and Value / Properties | `yStepSize` | value |  |  |
| Chart / Properties | `chartFill` | value | false |  |
| Chart / Properties | `lineMode` | value | smooth | smooth, straight, stepped |
| Chart / Properties | `showPoints` | value | false |  |
| Chart / Properties | `showGrid` | value | false |  |
| Chart / Properties | `showGridX` | value | false |  |
| Chart / Properties | `showGridY` | value | false |  |
| Chart / Properties | `instrumentMode` | value | false |  |
| Setpoint and Advice Zones / Properties | `hasAdvice` | value | false |  |
| Setpoint and Advice Zones / Properties | `advice` | array |  |  |
| Size / Properties | `width` | value | 480 |  |
| Size / Properties | `height` | value | 320 |  |
| Size / Properties | `fixedAspectRatioScaling` | value | false |  |
| Size / Properties | `scaleReferenceSize` | value | 384 |  |
| Size / Properties | `hasLabelPadding` | value | true |  |
| Properties | `legend` | value | false |  |
| Properties | `showTickMarks` | value | false |  |
| Properties | `frameStyle` | value | regular | regular, flat, framed, instrument |
| Properties | `hasXTicksLimit` | value | false |  |
| Properties | `xTicksLimit` | value |  |  |
| Properties | `hasXStepSize` | value | false |  |
| Properties | `xStepSize` | value |  |  |
| Properties | `hasYTicksLimit` | value | false |  |
| Properties | `yTicksLimit` | value |  |  |
| Properties | `style` | object |  |  |

## 16. Gauge Trend Indicator

<a id="gauge-trend-indicator"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.sparkline` beside an `Instrument/Field`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Data and Value / Properties | `data` | array |  |  |
| Data and Value / Properties | `minValue` | value | 0 |  |
| Data and Value / Properties | `maxValue` | value | 100 |  |
| Data and Value / Properties | `hasChartMinValue` | value | false |  |
| Data and Value / Properties | `chartMinValue` | value |  |  |
| Data and Value / Properties | `hasChartMaxValue` | value | false |  |
| Data and Value / Properties | `chartMaxValue` | value |  |  |
| Data and Value / Properties | `hasValue` | value | false |  |
| Data and Value / Properties | `value` | value |  |  |
| Type / Properties | `type` | value | Fill |  |
| Properties | `style` | object |  |  |

## 17. Gauge Vertical

<a id="gauge-vertical"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.linear-scale` or `ia.display.progress`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value and Range / Properties | `hasValue` | value | false |  |
| Value and Range / Properties | `value` | value |  |  |
| Value and Range / Properties | `minValue` | value | 0 |  |
| Value and Range / Properties | `maxValue` | value | 100 |  |
| Value and Range / Properties | `reverse` | value | false |  |
| Fill / Properties | `fillMode` | value | fill | fill, tint |
| Fill / Properties | `highlightCurrentValue` | value | false |  |
| Fill / Properties | `hasFillMin` | value | false |  |
| Fill / Properties | `fillMin` | value |  |  |
| Fill / Properties | `hasFillMax` | value | false |  |
| Fill / Properties | `fillMax` | value |  |  |
| Scale / Properties | `side` | value | right | left, right |
| Scale / Properties | `showLabels` | value | true |  |
| Scale / Properties | `hasPrimaryTickmarkInterval` | value | false |  |
| Scale / Properties | `primaryTickmarkInterval` | value |  |  |
| Scale / Properties | `hasSecondaryTickmarkInterval` | value | false |  |
| Scale / Properties | `secondaryTickmarkInterval` | value |  |  |
| Scale / Properties | `hasTertiaryTickmarkInterval` | value | false |  |
| Scale / Properties | `tertiaryTickmarkInterval` | value |  |  |
| Scale / Properties | `mainTickmarks` | array |  |  |
| Scale / Properties | `borderRadiusPosition` | value | innerFirstChild | innerFirstChild, middleChild, middleRoundedChild, outerLastChild |

## 18. Heading

<a id="heading"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Heading and Course / Properties | `heading` | value | 0 |  |
| Heading and Course / Properties | `courseOverGround` | value | 0 |  |
| Heading and Course / Properties | `hdgArrowStyle` | value | needle | needle, arrowHead, vector, beamLine |
| Heading and Course / Properties | `cogArrowStyle` | value | needle | needle, arrowHead, vector, velocityVector |
| Orientation / Properties | `direction` | value | northUp | northUp, headingUp, courseUp |
| Orientation / Properties | `showLabels` | value | false |  |
| Orientation / Properties | `tickmarksInside` | value | false |  |
| Heading Setpoint / Properties | `headingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `autoAtHeadingSetpoint` | value | true |  |
| Heading Setpoint / Properties | `autoAtHeadingSetpointDeadband` | value | 2 |  |
| Heading Setpoint / Properties | `atHeadingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `touching` | value | false |  |
| Heading Setpoint / Properties | `hasNewHeadingSetpoint` | value | false |  |
| Heading Setpoint / Properties | `newHeadingSetpoint` | value |  |  |
| Heading Setpoint / Properties | `animateSetpoint` | value | false |  |
| Heading Setpoint / Properties | `headingSetpointAtZeroDeadband` | value |  |  |
| Heading Setpoint / Properties | `headingSetpointOverride` | value | false |  |
| Heading Setpoint / Properties | `headingAdvices` | array |  |  |
| Centre / Properties | `vesselImage` | value | car-ferry-aft |  |
| Centre / Properties | `centerReadouts` | array |  |  |
| Priority / Properties | `priorityElements` | array |  |  |

## 19. Heading Indicator

<a id="heading-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Type / Properties | `type` | value | HDG |  |
| Type / Properties | `angle` | value | 0 |  |
| Type / Properties | `xtd` | value | 0 |  |
| Properties | `style` | object |  |  |

## 20. Heave

<a id="heave"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Heave / Properties | `heave` | value | 0 |  |
| Heave / Properties | `instrumentRange` | value | 10 |  |
| Heave / Properties | `minTrendHeave` | value | 0 |  |
| Heave / Properties | `maxTrendHeave` | value | 0 |  |
| Variant / Properties | `type` | value | vessel | vessel, bar |
| Advice / Properties | `advice` | array |  |  |
| Vessel / Properties | `gainScale` | value | 10 |  |
| Vessel / Properties | `draftOffset` | value | 0 |  |
| Vessel / Properties | `vesselImage` | value | psv-fore |  |

## 21. Heave Indicator

<a id="heave-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value | 0 |  |
| Type / Properties | `type` | value | enhanced | enhanced, regular |
| Properties | `style` | object |  |  |

## 22. Instrument Field

<a id="instrument-field"></a>

Disposition: `implemented`. Cadre equivalent: `Instrument/Field`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Properties | `size` | value | regular | regular, enhanced |
| Properties | `hasValue` | value | false |  |
| Properties | `value` | value |  |  |
| Properties | `fractionDigits` | value | 0 |  |
| Properties | `maxDigits` | value | 1 |  |
| Properties | `showZeroPadding` | value | false |  |
| Properties | `tag` | value |  |  |
| Properties | `unit` | value |  |  |
| Properties | `hasSetpoint` | value | false |  |
| Properties | `setpoint` | value |  |  |
| Properties | `autoHideSetpoint` | value | false |  |
| Properties | `autoHideDeadband` | value | 0 |  |
| Properties | `hasSrc` | value | false |  |
| Properties | `src` | value |  |  |
| Properties | `neutralColor` | value | false |  |
| Properties | `horizontal` | value | false |  |
| Properties | `center` | value | false |  |
| Properties | `labelOnly` | value | false |  |
| Properties | `off` | value | false |  |
| Properties | `style` | object |  |  |

## 23. Main Engine

<a id="main-engine"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Speed / Properties | `speed` | value | 0 |  |
| Thrust / Properties | `thrust` | value | 0 |  |
| Thrust / Properties | `thrustAdvices` | array |  |  |
| Setpoints / Properties | `hasSpeedSetpoint` | value | false |  |
| Setpoints / Properties | `speedSetpoint` | value |  |  |
| Setpoints / Properties | `autoAtSpeedSetpoint` | value | true |  |
| Setpoints / Properties | `autoAtSpeedSetpointDeadband` | value | 1 |  |
| Setpoints / Properties | `atSpeedSetpoint` | value | false |  |
| Setpoints / Properties | `speedSetpointAtZeroDeadband` | value |  |  |
| Setpoints / Properties | `speedTouching` | value | false |  |
| Setpoints / Properties | `hasThrustSetpoint` | value | false |  |
| Setpoints / Properties | `thrustSetpoint` | value |  |  |
| Setpoints / Properties | `autoAtThrustSetpoint` | value | true |  |
| Setpoints / Properties | `autoAtThrustSetpointDeadband` | value | 1 |  |
| Setpoints / Properties | `atThrustSetpoint` | value | false |  |
| Setpoints / Properties | `thrustSetpointAtZeroDeadband` | value |  |  |
| Setpoints / Properties | `thrustTouching` | value | false |  |

## 24. Main Engine Indicator

<a id="main-engine-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Speed and Thrust / Properties | `speed` | value | 0 |  |
| Speed and Thrust / Properties | `thrust` | value | 0 |  |
| Speed and Thrust / Properties | `rpmValue` | value | 0 |  |
| Speed and Thrust / Properties | `pitchValue` | value | 0 |  |
| State and Priority / Properties | `state` | value | active | active, loading, off |
| State and Priority / Properties | `priority` | value | regular | regular, enhanced |
| Silhouette / Properties | `hasSilhouette` | value | false |  |
| Properties | `style` | object |  |  |

## 25. Pitch

<a id="pitch"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Pitch / Properties | `pitch` | value | 0 |  |
| Pitch / Properties | `type` | value | single-scale | single-scale, dual-scale |
| Average Band / Properties | `minAvgPitch` | value | 0 |  |
| Average Band / Properties | `maxAvgPitch` | value | 0 |  |
| Pitch Advice / Properties | `hasMaxPitchAdvice` | value | false |  |
| Pitch Advice / Properties | `maxPitchAdvice` | value |  |  |
| Pitch Advice / Properties | `triggerPitchAdvice` | value | false |  |
| Arc and Zoom / Properties | `arcAngle` | value | 45 |  |
| Arc and Zoom / Properties | `zoomToFitArc` | value | false |  |
| Vessel Image / Properties | `vesselImageSide` | value | psv-side |  |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |

## 26. Pitch Indicator

<a id="pitch-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value | 0 |  |
| Type / Properties | `type` | value | enhanced | enhanced, regular |
| Properties | `style` | object |  |  |

## 27. Pitch Roll

<a id="pitch-roll"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Pitch and Roll / Properties | `pitch` | value | 0 |  |
| Pitch and Roll / Properties | `roll` | value | 0 |  |
| Pitch and Roll / Properties | `type` | value | dual-scale | dual-scale, single-scale |
| Pitch and Roll / Properties | `minAvgPitch` | value | 0 |  |
| Pitch and Roll / Properties | `maxAvgPitch` | value | 0 |  |
| Pitch and Roll / Properties | `minAvgRoll` | value | 0 |  |
| Pitch and Roll / Properties | `maxAvgRoll` | value | 0 |  |
| Advice / Properties | `hasMaxPitchAdvice` | value | false |  |
| Advice / Properties | `maxPitchAdvice` | value |  |  |
| Advice / Properties | `triggerPitchAdvice` | value |  |  |
| Advice / Properties | `hasMaxRollAdvice` | value | false |  |
| Advice / Properties | `maxRollAdvice` | value |  |  |
| Advice / Properties | `triggerRollAdvice` | value |  |  |
| Arcs / Properties | `arcAngle` | value | 30 |  |
| Arcs / Properties | `zoomToFitArc` | value | false |  |
| Arcs / Properties | `hasPitchArcAngle` | value | false |  |
| Arcs / Properties | `pitchArcAngle` | value |  |  |
| Arcs / Properties | `hasRollArcAngle` | value | false |  |
| Arcs / Properties | `rollArcAngle` | value |  |  |
| Centre / Properties | `vesselImageSide` | value | psv-side |  |
| Centre / Properties | `vesselImageFore` | value | psv-fore |  |
| Centre / Properties | `scaleForeImage` | value | 1 |  |
| Centre / Properties | `hasReadout` | value | false |  |
| Centre / Properties | `pitchLabel` | value |  |  |
| Centre / Properties | `rollLabel` | value |  |  |
| Centre / Properties | `unit` | value |  |  |
| Centre / Properties | `fractionDigits` | value | 0 |  |
| Priority / Properties | `priorityElements` | array |  |  |

## 28. Pitch Roll Heave

<a id="pitch-roll-heave"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Layout / Properties | `type` | value | single-scale | single-scale, dual-scale |
| Pitch and Roll / Properties | `pitch` | value | 0 |  |
| Pitch and Roll / Properties | `roll` | value | 0 |  |
| Pitch and Roll / Properties | `minAvgPitch` | value | 0 |  |
| Pitch and Roll / Properties | `maxAvgPitch` | value | 0 |  |
| Pitch and Roll / Properties | `minAvgRoll` | value | 0 |  |
| Pitch and Roll / Properties | `maxAvgRoll` | value | 0 |  |
| Pitch and Roll / Properties | `pitchArcAngle` | value | 30 |  |
| Pitch and Roll / Properties | `rollArcAngle` | value | 45 |  |
| Pitch and Roll / Properties | `zoomToFitArc` | value | false |  |
| Pitch and Roll / Properties | `hasMaxPitchAdvice` | value | false |  |
| Pitch and Roll / Properties | `maxPitchAdvice` | value |  |  |
| Pitch and Roll / Properties | `triggerPitchAdvice` | value |  |  |
| Pitch and Roll / Properties | `hasMaxRollAdvice` | value | false |  |
| Pitch and Roll / Properties | `maxRollAdvice` | value |  |  |
| Pitch and Roll / Properties | `triggerRollAdvice` | value |  |  |
| Heave / Properties | `heave` | value | 0 |  |
| Heave / Properties | `heaveRange` | value | 10 |  |
| Heave / Properties | `minTrendHeave` | value | 0 |  |
| Heave / Properties | `maxTrendHeave` | value | 0 |  |
| Heave / Properties | `heaveAdvice` | array |  |  |
| Centre / Properties | `vesselImageSide` | value | psv-side |  |
| Centre / Properties | `vesselImageFore` | value | psv-fore |  |
| Centre / Properties | `scaleForeImage` | value | 1 |  |
| Centre / Properties | `hasReadout` | value | false |  |
| Centre / Properties | `pitchLabel` | value |  |  |
| Centre / Properties | `rollLabel` | value |  |  |
| Centre / Properties | `heaveLabel` | value |  |  |
| Centre / Properties | `unit` | value |  |  |
| Centre / Properties | `heaveUnit` | value |  |  |
| Centre / Properties | `fractionDigits` | value | 0 |  |
| Priority / Properties | `priorityElements` | array |  |  |

## 29. Pitch Roll Yaw

<a id="pitch-roll-yaw"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Variants / Properties | `type` | value | level | level, actual-motion, historical-motion |
| Pitch and Roll / Properties | `pitch` | value | 0 |  |
| Pitch and Roll / Properties | `roll` | value | 0 |  |
| Pitch and Roll / Properties | `range` | value | 20 |  |
| Pitch and Roll / Properties | `motionRadius` | value | 0 |  |
| Pitch and Roll / Properties | `motionHistory` | array |  |  |
| Yaw / Properties | `yaw` | value | 0 |  |
| Yaw / Properties | `minAvgYaw` | value | 0 |  |
| Yaw / Properties | `maxAvgYaw` | value | 0 |  |
| Yaw / Properties | `showLabels` | value | false |  |
| Vessel Image / Properties | `vesselImage` | value | psv-top |  |

## 30. Propulsion Azimuth Indicator

<a id="propulsion-azimuth-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Azimuth / Properties | `azimuth` | value | 0 |  |
| Value / Properties | `value` | value | 0 |  |
| Type and State / Properties | `type` | value | enhanced | enhanced, regular |
| Type and State / Properties | `state` | value | active | active, loading, off |
| Silhouette / Properties | `hasSilhouette` | value | false |  |
| Properties | `style` | object |  |  |

## 31. Rate Of Turn

<a id="rate-of-turn"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Rate of Turn / Properties | `hasRateOfTurnDegreesPerMinute` | value | false |  |
| Rate of Turn / Properties | `rateOfTurnDegreesPerMinute` | value |  |  |
| Rate of Turn / Properties | `rotDotAnimationFactor` | value | 18 |  |
| Rate of Turn / Properties | `rotType` | value | dots | dots, bar |
| Rate of Turn / Properties | `rotPosition` | value | scale |  |
| Rate of Turn / Properties | `barStartAngle` | value | 0 |  |
| Rate of Turn / Properties | `barEndAngle` | value | 30 |  |
| Rate of Turn / Properties | `rotAtZeroDeadband` | value |  |  |
| Rate of Turn / Properties | `rotationsPerMinute` | value | 1 |  |
| Track Bar / Properties | `hasTrackBar` | value | false |  |
| Track Bar / Properties | `rotMaxValue` | value | 60 |  |
| Track Bar / Properties | `rotArcExtent` | value | 60 |  |
| Track Bar / Properties | `rotPortStarboard` | value | false |  |
| Face / Properties | `watchCircleType` | value | single | single, double, doubleThin, triple |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |

## 32. Readout

<a id="readout"></a>

Disposition: `implemented`. Cadre equivalent: `Instrument/Field`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value | 10 |  |
| Value / Properties | `numberFormat` | value | #,##0 |  |
| Value / Properties | `maxDigits` | value | 0 |  |
| Value / Properties | `hasDegree` | value | false |  |
| Value / Properties | `hasDegreeSpacer` | value | false |  |
| Value / Properties | `hasValue` | value | true |  |
| Label and Unit / Properties | `label` | value | Label |  |
| Label and Unit / Properties | `unit` | value | empty |  |
| Size and Layout / Properties | `size` | value | small | small, medium, large |
| Size and Layout / Properties | `direction` | value | vertical | vertical, horizontal |
| Size and Layout / Properties | `stacking` | value | inline | inline, stacked |
| Size and Layout / Properties | `alignment` | value | vertical |  |
| Setpoint / Properties | `hasSetpoint` | value | false |  |
| Setpoint / Properties | `setpoint` | value |  |  |
| Setpoint / Properties | `setpointOptions.interaction` | value | always-visible | always-visible, flip-flop, pop-up |
| Setpoint / Properties | `setpointOptions.touching` | value | false |  |
| Advice / Properties | `hasAdvice` | value | false |  |
| Advice / Properties | `advice` | value |  |  |
| Source / Properties | `src` | value | empty (no source shown) |  |
| Source / Properties | `srcOptions.interaction` | value | none | none, picker, flyout |
| Priority and Weight / Properties | `priority` | value | regular | regular, enhanced |
| Priority and Weight / Properties | `valueOptions.weight` | value | regular | regular, semibold, bold |
| Off, Data Quality and Alerts / Properties | `off` | value | false |  |
| Off, Data Quality and Alerts / Properties | `offText` | value | Off |  |
| Off, Data Quality and Alerts / Properties | `dataQuality` | value | good | good, low-integrity, invalid |
| Off, Data Quality and Alerts / Properties | `hasAlert` | value | false |  |
| Off, Data Quality and Alerts / Properties | `alert` | object |  |  |
| Off, Data Quality and Alerts / Properties | `alert.status` | value | alarm |  |
| Off, Data Quality and Alerts / Properties | `alert.type` | value | regular | regular, small-side-flip, large-side-flip, bottom-flip, top-flip |
| Off, Data Quality and Alerts / Properties | `alert.mode` | value | acked-active | acked-active, unacked-active, unacked-rectified |
| Off, Data Quality and Alerts / Properties | `alert.thickness` | value | small | small, large |
| Off, Data Quality and Alerts / Properties | `alert.textSize` | value | regular | regular, large |

## 33. Readout List Item

<a id="readout-list-item"></a>

Disposition: `stock`. Cadre equivalent: `Instrument/Field` rows in an `ia.container.flex`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `hasValue` | value | true |  |
| Value / Properties | `value` | value | 0 |  |
| Value / Properties | `valueUndefined` | value | false |  |
| Value / Properties | `numberFormat` | value | #,##0 |  |
| Value / Properties | `maxDigits` | value | 0 |  |
| Value / Properties | `hasDegree` | value | false |  |
| Label, Unit and Source / Properties | `hasLabel` | value | true |  |
| Label, Unit and Source / Properties | `label` | value | Label |  |
| Label, Unit and Source / Properties | `hasUnit` | value | true |  |
| Label, Unit and Source / Properties | `unit` | value | empty |  |
| Label, Unit and Source / Properties | `hasSource` | value | false |  |
| Label, Unit and Source / Properties | `src` | value | empty |  |
| Label, Unit and Source / Properties | `stacking` | value | trailing-unit | trailing-unit, leading-unit, leading-src |
| Label, Unit and Source / Properties | `hasLeadingIcon` | value | false |  |
| Size / Properties | `size` | value | base, an older name that means small | small, medium, large |
| Setpoint / Properties | `hasSetpoint` | value | false |  |
| Setpoint / Properties | `setpoint` | value | 0 |  |
| Setpoint / Properties | `setpointUndefined` | value | false |  |
| Setpoint / Properties | `setpointOptions.interaction` | value | always-visible | always-visible, flip-flop, pop-up |
| Setpoint / Properties | `setpointOptions.touching` | value | false |  |
| Advice / Properties | `hasAdvice` | value | false |  |
| Advice / Properties | `advice` | value | 0 |  |
| Advice / Properties | `adviceUndefined` | value | false |  |
| Priority and Weight / Properties | `priority` | value | regular | regular, enhanced |
| Priority and Weight / Properties | `valueOptions.weight` | value | regular | regular, semibold, bold |
| Data Quality and Alerts / Properties | `dataQuality` | value | none | none, low-integrity, invalid |
| Data Quality and Alerts / Properties | `hasAlert` | value | false |  |
| Data Quality and Alerts / Properties | `alert` | object |  |  |
| Data Quality and Alerts / Properties | `alert.status` | value | alarm |  |
| Data Quality and Alerts / Properties | `alert.type` | value | small-side-flip | regular, small-side-flip, large-side-flip, bottom-flip, top-flip |
| Data Quality and Alerts / Properties | `alert.mode` | value | acked-active | acked-active, unacked-active, unacked-rectified |
| Data Quality and Alerts / Properties | `alert.thickness` | value | small | small, large |
| Data Quality and Alerts / Properties | `alert.textSize` | value | regular | regular, large |
| Data Quality and Alerts / Properties | `alert.showIcon` | value | false |  |

## 34. Roll

<a id="roll"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Roll / Properties | `roll` | value | 0 |  |
| Roll / Properties | `type` | value | single-scale | single-scale, dual-scale |
| Roll / Properties | `minAvgRoll` | value | 0 |  |
| Roll / Properties | `maxAvgRoll` | value | 0 |  |
| Roll Advice / Properties | `hasMaxRollAdvice` | value | false |  |
| Roll Advice / Properties | `maxRollAdvice` | value |  |  |
| Roll Advice / Properties | `triggerRollAdvice` | value | false |  |
| Arc and Zoom / Properties | `arcAngle` | value | 45 |  |
| Arc and Zoom / Properties | `zoomToFitArc` | value | false |  |
| Vessel Image / Properties | `vesselImageFore` | value | psv-fore |  |
| Vessel Image / Properties | `scaleForeImage` | value | 1 |  |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |

## 35. Roll Indicator

<a id="roll-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value | 0 |  |
| Type / Properties | `type` | value | enhanced | enhanced, regular |
| Properties | `style` | object |  |  |

## 36. Rot Indicator

<a id="rot-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Rate of Turn / Properties | `type` | value | radial | radial, linear |
| Rate of Turn / Properties | `hasRateOfTurnDegreesPerMinute` | value | false |  |
| Rate of Turn / Properties | `rateOfTurnDegreesPerMinute` | value |  |  |
| Rate of Turn / Properties | `rotDotAnimationFactor` | value | 18 |  |
| Rate of Turn / Properties | `rotationsPerMinute` | value | 0 |  |
| Properties | `style` | object |  |  |

## 37. Rot Linear

<a id="rot-linear"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Rate of Turn / Properties | `hasRateOfTurnDegreesPerMinute` | value | false |  |
| Rate of Turn / Properties | `rateOfTurnDegreesPerMinute` | value |  |  |
| Scale / Properties | `rotMaxValue` | value | 90 |  |
| Scale / Properties | `tickInterval` | value | 5 |  |
| Colour / Properties | `rotPortStarboard` | value | false |  |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |

## 38. Rot Sector

<a id="rot-sector"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value and Range / Properties | `value` | value | 0 |  |
| Value and Range / Properties | `maxValue` | value | 100 |  |
| Value and Range / Properties | `rotArcExtent` | value | 60 |  |
| Scale / Properties | `showLabels` | value | false |  |
| Scale / Properties | `tickmarksInside` | value | false |  |
| Scale / Properties | `tickmarkStyle` | value | regular | regular, enhanced |
| Scale / Properties | `hasPrimaryTickmarkInterval` | value | false |  |
| Scale / Properties | `primaryTickmarkInterval` | value | 50 |  |
| Scale / Properties | `hasSecondaryTickmarkInterval` | value | false |  |
| Scale / Properties | `secondaryTickmarkInterval` | value | 10 |  |
| Scale / Properties | `hasTertiaryTickmarkInterval` | value | false |  |
| Scale / Properties | `tertiaryTickmarkInterval` | value |  |  |
| Colour / Properties | `portStarboard` | value | false |  |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |
| Size / Properties | `zoomToFitArc` | value | false |  |

## 39. Rudder

<a id="rudder"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Angle / Properties | `angle` | value | 0 |  |
| Angle / Properties | `variant` | value | bar | bar, needle |
| Range / Properties | `maxAngle` | value | 90 |  |
| Range / Properties | `zoomToFitArc` | value | false |  |

## 40. Rudder Indicator

<a id="rudder-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Angle / Properties | `angle` | value | 0 |  |
| State / Properties | `state` | value | in-command | in-command, not-in-command, off |
| State / Properties | `setpoint` | value | 0 |  |
| Silhouette / Properties | `hasSilhouette` | value | false |  |
| Properties | `style` | object |  |  |

## 41. Speed Arrows

<a id="speed-arrows"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Number of Arrows / Properties | `nActiveArrows` | value | 0 |  |
| Number of Arrows / Properties | `tintedArrows` | value | false |  |
| Direction and Colour / Properties | `direction` | value | forward | forward, backward, left, right |
| Direction and Colour / Properties | `activeColor` | value | Regular |  |
| Readout / Properties | `readout` | value | false |  |
| Readout / Properties | `speedKnots` | value | 0 |  |
| Readout / Properties | `fractionDigits` | value | 0 |  |
| Readout / Properties | `maxDigits` | value | 2 |  |
| Properties | `style` | object |  |  |

## 42. Speed Gauge

<a id="speed-gauge"></a>

Disposition: `stock`. Cadre equivalent: `ia.chart.gauge` or `ia.chart.simple-gauge` with Cadre colours.

Visual parity with the reference gauge is not claimed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Speed and Range / Properties | `speed` | value | 0 |  |
| Speed and Range / Properties | `minSpeed` | value | 0 |  |
| Speed and Range / Properties | `maxSpeed` | value | 100 |  |
| Speed and Range / Properties | `hasTickmarkInterval` | value | false |  |
| Speed and Range / Properties | `tickmarkInterval` | value | 20 |  |
| Needle / Properties | `needleType` | value | full | full, bar |
| Readout / Properties | `hasReadout` | value | false |  |
| Readout / Properties | `label` | value |  |  |
| Readout / Properties | `unit` | value |  |  |
| Readout / Properties | `fractionDigits` | value | 1 |  |

## 43. Speed Indicator

<a id="speed-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Needle / Properties | `type` | value | Needle |  |
| Needle / Properties | `speed` | value | 0 |  |
| Needle / Properties | `maxSpeed` | value | 100 |  |
| Longitudinal and Lateral Speed / Properties | `longLatLevels` | array |  |  |
| Properties | `style` | object |  |  |

## 44. Surge Sway Yaw

<a id="surge-sway-yaw"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Variants / Properties | `type` | value | input | input, input-output |
| Values / Properties | `surge` | value | 0 |  |
| Values / Properties | `sway` | value | 0 |  |
| Values / Properties | `yaw` | value | 0 |  |
| Setpoints / Properties | `hasSurgeSetpoint` | value | false |  |
| Setpoints / Properties | `surgeSetpoint` | value |  |  |
| Setpoints / Properties | `hasNewSurgeSetpoint` | value | false |  |
| Setpoints / Properties | `newSurgeSetpoint` | value |  |  |
| Setpoints / Properties | `autoAtSurgeSetpoint` | value | true |  |
| Setpoints / Properties | `autoAtSurgeSetpointDeadband` | value | 1 (yaw 2) |  |
| Setpoints / Properties | `atSurgeSetpoint` | value | false |  |
| Setpoints / Properties | `surgeSetpointAtZeroDeadband` | value |  |  |
| Setpoints / Properties | `surgeSetpointOverride` | value | false |  |
| Setpoints / Properties | `touching` | value | false |  |
| Setpoints / Properties | `animateSetpoint` | value | false |  |
| Ring Scale / Properties | `hasPrimaryTickmarkInterval` | value | false |  |
| Ring Scale / Properties | `primaryTickmarkInterval` | value | 45 |  |
| Ring Scale / Properties | `hasSecondaryTickmarkInterval` | value | false |  |
| Ring Scale / Properties | `secondaryTickmarkInterval` | value | 15 |  |
| Ring Scale / Properties | `hasTertiaryTickmarkInterval` | value | false |  |
| Ring Scale / Properties | `tertiaryTickmarkInterval` | value | 5 |  |
| Ring Scale / Properties | `showLabels` | value | false |  |

## 45. Thruster

<a id="thruster"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Thrust / Properties | `thrust` | value | 0 |  |
| Shape / Properties | `singleSided` | value | false |  |
| Shape / Properties | `singleDirection` | value | false |  |
| Shape / Properties | `singleDirectionHalfSize` | value | false |  |
| Shape / Properties | `tunnel` | value | false |  |
| Propellers / Properties | `topPropeller` | value | none | none, cap, single |
| Propellers / Properties | `bottomPropeller` | value | none | none, cap, single |
| Setpoint / Properties | `hasSetpoint` | value | false |  |
| Setpoint / Properties | `setpoint` | value |  |  |
| Setpoint / Properties | `autoAtSetpoint` | value | false |  |
| Setpoint / Properties | `autoAtSetpointDeadband` | value | 0 |  |
| Setpoint / Properties | `atSetpoint` | value | false |  |
| Setpoint / Properties | `touching` | value | false |  |
| Setpoint / Properties | `hasNewSetpoint` | value | false |  |
| Setpoint / Properties | `newSetpoint` | value |  |  |
| Setpoint / Properties | `setpointAtZeroDeadband` | value | 0 |  |
| Setpoint / Properties | `setpointOverride` | value | false |  |
| Setpoint / Properties | `animateSetpoint` | value | false |  |
| Advice Zones / Properties | `advices` | array |  |  |

## 46. Tunnel Thruster

<a id="tunnel-thruster"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Thrust / Properties | `thrust` | value | 0 |  |
| Thrust / Properties | `value` | value | 0 |  |
| State / Properties | `state` | value |  | in-command, not-in-command, off |
| Silhouette / Properties | `hasSilhouette` | value | false |  |
| Properties | `style` | object |  |  |

## 47. Velocity Projection Plot

<a id="velocity-projection-plot"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Sectors | `startAngleDeg` | value |  |  |
| Sectors | `endAngleDeg` | value |  |  |
| Sectors | `ratioTotalEnergy` | value |  |  |
| Sectors | `ratioWindEnergyOrExcessSpeed` | value |  |  |
| Sectors / Properties | `dataPoints` | array | empty |  |
| Wind and Current / Properties | `currentWindFromDirection` | value |  |  |
| Wind and Current / Properties | `currentWindSpeedKnots` | value |  |  |
| Wind and Current / Properties | `currentFromDirection` | value |  |  |
| Wind and Current / Properties | `currentSpeedKnots` | value |  |  |
| Vessel / Properties | `vesselImage` | value | cargo-wind-top |  |
| Properties | `style` | object |  |  |

## 48. Wind

<a id="wind"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Wind / Properties | `currentWindFromDirection` | value | 0 |  |
| Wind / Properties | `currentWindSpeedKnots` | value | 25 |  |
| Histogram | `direction` | value |  |  |
| Histogram | `occurrences` | value |  |  |
| Histogram / Properties | `windHistogramData` | array |  |  |
| Histogram / Properties | `visualization` | value | histogram | histogram, forceGraphics |
| Vessel / Properties | `vesselHeadingDeg` | value | 0 |  |
| Vessel / Properties | `vesselImage` | value | generic-top |  |
| Size and Variant / Properties | `variant` | value | auto | auto, small, medium, large |
| Size and Variant / Properties | `smallVariantMaxPx` | value |  |  |
| Size and Variant / Properties | `mediumVariantMaxPx` | value |  |  |

## 49. Wind Indicator

<a id="wind-indicator"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Wind Direction / Properties | `currentWindFromDirection` | value | 0 |  |
| Wind Direction / Properties | `windFromAngle` | value | 0 |  |
| Wind Direction / Properties | `angle` | value | 0 |  |
| Wind Speed / Properties | `currentWindSpeedKnots` | value | 0 (calm) |  |
| Type and Direction / Properties | `type` | value | arrow | arrow, shaft, labeled |
| Type and Direction / Properties | `direction` | value | true |  |
| Type and Direction / Properties | `rotationAngle` | value | 0 |  |
| Priority / Properties | `priority` | value | regular | regular, enhanced |
| Properties | `style` | object |  |  |

## 50. Wind Propulsion

<a id="wind-propulsion"></a>

Disposition: `out-of-scope`. Cadre equivalent: None.

Ship navigation instrument; drawn as a visible gap box if a descriptor names it.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Sail / Properties | `sailAngle` | value | 0 |  |
| Sail / Properties | `sailType` | value | rotor-sail |  |
| Force / Properties | `forceAngle` | value | 0 |  |
| Force / Properties | `force` | value | 0 |  |
| Force / Properties | `maxForce` | value | 100 |  |
| Sail Angle Setpoint / Properties | `hasSailAngleSetpoint` | value | false |  |
| Sail Angle Setpoint / Properties | `sailAngleSetpoint` | value |  |  |
| Sail Angle Setpoint / Properties | `autoAtSailAngleSetpoint` | value | true |  |
| Sail Angle Setpoint / Properties | `autoAtSailAngleSetpointDeadband` | value | 2 |  |
| Sail Angle Setpoint / Properties | `atSailAngleSetpoint` | value | false |  |
| Sail Angle Setpoint / Properties | `touching` | value | false |  |
| Sail Angle Setpoint / Properties | `hasNewSailAngleSetpoint` | value | false |  |
| Sail Angle Setpoint / Properties | `newSailAngleSetpoint` | value |  |  |
| Sail Angle Setpoint / Properties | `animateSetpoint` | value | false |  |
| Sail Angle Setpoint / Properties | `sailAngleSetpointAtZeroDeadband` | value |  |  |
| Sail Angle Setpoint / Properties | `sailAngleSetpointOverride` | value | false |  |
| Sail Angle Setpoint / Properties | `sailAngleAdvices` | array |  |  |
| Wind / Properties | `currentWindFromDirection` | value |  |  |
| Wind / Properties | `currentWindSpeedKnots` | value |  |  |
| State and Priority / Properties | `priorityElements` | array |  |  |
