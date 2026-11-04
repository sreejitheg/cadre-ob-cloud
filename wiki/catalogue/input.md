# Catalogue: Input

Interface facts for the 33 components of the reference family `Input`, parsed from the reference documentation. Defaults and enumerations are parsed from prose by heuristic and are marked so; an empty cell means the page states none. Back to [05 Component Catalogue](../05-component-catalogue.md).

## 1. App Button

<a id="app-button"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Icon and Label / Properties | `icon` | object |  |  |
| Icon and Label / Properties | `icon.path` | value | placeholder |  |
| Icon and Label / Properties | `label` | value | Button |  |
| Icon and Label / Properties | `showLabel` | value | true |  |
| Size / Properties | `size` | value | normal | normal, small |
| Checked / Properties | `checked` | value | false |  |
| Integration Style / Properties | `integration` | value | false |  |

Events: `onActionPerformed`.

## 2. Breadcrumb

<a id="breadcrumb"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Items | `label` | value |  |  |
| Items | `href` | value |  |  |
| Items / Properties | `items` | array |  |  |
| Icon Only / Properties | `iconOnly` | value | false |  |
| Component Events | `label` | value |  |  |
| Component Events | `href` | value |  |  |

Events: `onBreadcrumbClick`.

## 3. Button

<a id="button"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.button` with `cadre/button/normal`, `raised`, `flat` or `selected`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Label and Icons / Properties | `label` | value |  |  |
| Label and Icons / Properties | `hasLeadingIcon` | value | false |  |
| Label and Icons / Properties | `leadingIcon` | value | placeholder |  |
| Label and Icons / Properties | `hasTrailingIcon` | value | false |  |
| Label and Icons / Properties | `trailingIcon` | value | placeholder |  |
| Variant / Properties | `variant` | value | normal | normal, raised, flat |
| Width / Properties | `fullWidth` | value | false |  |

Events: `onActionPerformed`.

## 4. Chat Message

<a id="chat-message"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Message / Properties | `message` | value |  |  |
| Sender / Properties | `self` | value | false |  |
| Name and Date / Properties | `showName` | value | false |  |
| Name and Date / Properties | `name` | value |  |  |
| Name and Date / Properties | `showDate` | value | false |  |
| Name and Date / Properties | `date` | value |  |  |
| Name and Date / Properties | `format` | value | HH:mm |  |
| Name and Date / Properties | `timezone` | value | UTC |  |
| Position in a Group / Properties | `position` | value | single | single, top, middle, bottom |

## 5. Checkbox

<a id="checkbox"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.checkbox`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| State / Properties | `checked` | value | false |  |
| State / Properties | `mixed` | value | false |  |
| State / Properties | `status` | value |  |  |
| Label / Properties | `label` | value |  |  |

Events: `onActionPerformed`.

## 6. Checkbox List

<a id="checkbox-list"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.checkbox` instances in an `ia.container.flex`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Rows | `label` | value | empty |  |
| Rows | `description` | value | empty |  |
| Rows | `status` | value | unchecked | unchecked, checked, mixed |
| Rows | `level` | value | 0 |  |
| Rows | `expandable` | value | false |  |
| Rows | `expanded` | value | false |  |
| Rows | `disabled` | value | false |  |
| Rows / Properties | `rows` | array |  |  |
| Hover Style / Properties | `hoverStyle` | value | touch-target | touch-target, visual-target |
| Component Events | `index` | value |  |  |
| Component Events | `label` | value |  |  |
| Component Events | `status` | value |  | checked, unchecked |

Events: `onActionPerformed`.

## 7. Common Features

<a id="input"></a>

Disposition: `stock`. Cadre equivalent: Stock `ia.input.*` components with `cadre/button/*` and `cadre/font/*` classes.

Common features page of the input family.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Disabled | `disabled` | value | false |  |
| Appearance | `style` | object |  |  |

Events: `onActionPerformed`.

## 8. Double Slider

<a id="double-slider"></a>

Disposition: `gap`. Cadre equivalent: None.

The stock `ia.input.slider` has one handle.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Low, High and Range / Properties | `low` | value | 25 |  |
| Low, High and Range / Properties | `high` | value | 75 |  |
| Low, High and Range / Properties | `min` | value | 0 |  |
| Low, High and Range / Properties | `max` | value | 100 |  |
| Low, High and Range / Properties | `step` | value | 1 |  |
| Low, High and Range / Properties | `stepClick` | value | 10 |  |
| Variant / Properties | `variant` | value | normal | normal, enhanced, no-input |
| Labels / Properties | `labelUnit` | value |  |  |
| Labels / Properties | `labelDecimals` | value | 0 |  |
| Labels / Properties | `labelWidth` | value | 3ch |  |
| Pressing on the Track / Properties | `allowSeeking` | value | false |  |
| Pressing on the Track / Properties | `seekingSpeed` | value |  |  |

Events: `onActionPerformed`.

## 9. Dropdown Button

<a id="dropdown-button"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.dropdown`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Options / Properties | `options` | array |  |  |
| Options / Properties | `options[].label` | value |  |  |
| Options / Properties | `options[].value` | value |  |  |
| Value / Properties | `value` | value |  |  |
| Value / Properties | `allowEmptySelection` | value | false |  |
| Width / Properties | `fullWidth` | value | false |  |
| Integration Style / Properties | `integration` | value | false |  |

Events: `onActionPerformed`.

## 10. Filter Chip

<a id="filter-chip"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| State / Properties | `checked` | value | false |  |
| Label / Properties | `label` | value | Filter |  |
| Icon / Properties | `showIcon` | value | false |  |
| Icon / Properties | `icon` | object |  |  |
| Icon / Properties | `icon.path` | value | placeholder |  |
| Component Events | `label` | value |  |  |
| Component Events | `checked` | value |  |  |

Events: `onChipToggle`.

## 11. Floating Item

<a id="floating-item"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Text / Properties | `title` | value |  |  |
| Text / Properties | `description` | value |  |  |
| Text / Properties | `lineType` | value | single-line | single-line, multi-line |
| Type and Icons / Properties | `type` | value | regular | regular, application |
| Type and Icons / Properties | `primaryIcon` | object | placeholder |  |
| Type and Icons / Properties | `secondaryIcon` | object | placeholder |  |
| Time / Properties | `hasTimestamp` | value | false |  |
| Time / Properties | `time` | value |  |  |
| Time / Properties | `hasDay` | value | false |  |
| Time / Properties | `day` | value |  |  |
| Actions / Properties | `action` | value |  |  |
| Actions / Properties | `action2` | value |  |  |
| Actions / Properties | `direction` | value | horizontal | horizontal, vertical |

Events: `onActionClick`, `onAction2Click`, `onDismissClick`, `onActionPerformed`.

## 12. Icon

<a id="icon"></a>

Disposition: `implemented`. Cadre equivalent: `ia.shapes.svg` fed by `cadre.icons.elements(name)` (92 converted icons).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Choosing an Icon / Properties | `icon` | object |  |  |
| Choosing an Icon / Properties | `icon.path` | value | placeholder |  |
| Color / Properties | `useColor` | value | false |  |
| Properties | `style` | object |  |  |

## 13. Icon Button

<a id="icon-button"></a>

Disposition: `implemented`. Cadre equivalent: Icon button pattern: an `ia.shapes.svg` icon in a flat button container (`tools/hmi/framework.py`).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Icon and Label / Properties | `icon` | object |  |  |
| Icon and Label / Properties | `icon.path` | value | placeholder |  |
| Icon and Label / Properties | `hasLabel` | value | false |  |
| Icon and Label / Properties | `label` | value |  |  |
| Variant / Properties | `variant` | value | normal | normal, raised, flat, integration |
| Activated / Properties | `activated` | value | false |  |
| Activated / Properties | `activeColor` | value | false |  |
| Width and Corners / Properties | `wide` | value | false |  |
| Width and Corners / Properties | `cornerLeft` | value | false |  |
| Width and Corners / Properties | `cornerRight` | value | false |  |

Events: `onActionPerformed`.

## 14. Icon Check Button

<a id="icon-check-button"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Checked / Properties | `checked` | value | false |  |
| Icon and Label / Properties | `icon` | object |  |  |
| Icon and Label / Properties | `icon.path` | value | placeholder |  |
| Icon and Label / Properties | `hasLabel` | value | false |  |
| Icon and Label / Properties | `label` | value |  |  |
| Alert / Properties | `hasAlert` | value | false |  |

Events: `onActionPerformed`.

## 15. Message Menu Item

<a id="message-menu-item"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Text / Properties | `hasTitle` | value | true |  |
| Text / Properties | `title` | value | Title |  |
| Text / Properties | `hasDescription` | value | true |  |
| Text / Properties | `description` | value |  |  |
| Text / Properties | `size` | value | single-line | single-line, double-line |
| Expanding / Properties | `open` | value | false |  |
| Time / Properties | `hasTimestamp` | value | true |  |
| Time / Properties | `time` | value |  |  |
| Time / Properties | `hasDay` | value | true |  |
| Time / Properties | `day` | value |  |  |
| Icons / Properties | `hasPrimaryIcon` | value | false |  |
| Icons / Properties | `primaryIcon` | object | placeholder |  |
| Icons / Properties | `hasSecondaryIcon` | value | false |  |
| Icons / Properties | `secondaryIcon` | object | placeholder |  |
| Icons / Properties | `hasTrailingIcon` | value | false |  |
| Icons / Properties | `trailingIcon` | object | placeholder |  |
| Icons / Properties | `enhancedIcon` | value | false |  |
| Icons / Properties | `isShelved` | value | false |  |
| Actions / Properties | `hasActionLabel` | value | false |  |
| Actions / Properties | `primaryActionLabel` | value |  |  |
| Actions / Properties | `secondaryActionLabel` | value |  |  |
| Actions / Properties | `stackVertical` | value | false |  |

Events: `onMessageClick`, `onPrimaryActionClick`, `onSecondaryActionClick`, `onActionPerformed`.

## 16. Number Input Field

<a id="number-input-field"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.numeric-entry-field`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value |  |  |
| Value / Properties | `unit` | value |  |  |
| Value / Properties | `placeholder` | value |  |  |
| Value / Properties | `deferUpdates` | value | false |  |
| Value / Properties | `rejectUpdatesWhileFocused` | value | false |  |
| Value / Properties | `maxlength` | value |  |  |
| Value / Properties | `minlength` | value |  |  |
| Value / Properties | `validationPattern` | value |  |  |
| Number Format / Properties | `formatNumber` | value | true |  |
| Number Format / Properties | `numberFormat` | value |  |  |
| Field / Properties | `textAlign` | value | right | right, center, right-unit-outside |
| Field / Properties | `size` | value | regular | regular, large |
| Field / Properties | `hasLeadingIcon` | value | false |  |
| Field / Properties | `leadingIcon` | object |  |  |
| Field / Properties | `readonly` | value | false |  |
| Label and Helper Text / Properties | `label` | value |  |  |
| Label and Helper Text / Properties | `labelPlacement` | value | left | left, center, right |
| Label and Helper Text / Properties | `hasLabelIcon` | value | false |  |
| Label and Helper Text / Properties | `labelIcon` | object |  |  |
| Label and Helper Text / Properties | `helperText` | value |  |  |
| Label and Helper Text / Properties | `helperPlacement` | value | left | left, center, right |
| Label and Helper Text / Properties | `hasHelperIcon` | value | false |  |
| Label and Helper Text / Properties | `helperIcon` | object |  |  |
| Label and Helper Text / Properties | `required` | value | false |  |
| Error / Properties | `error` | value | false |  |
| Error / Properties | `errorText` | value |  |  |

Events: `onActionPerformed`.

## 17. Pivot Item Group

<a id="pivot-item-group"></a>

Disposition: `implemented`. Cadre equivalent: Selected-state button row pattern (faceplate commands, alerts page tabs, diagram toolbar).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Items | `value` | value |  |  |
| Items | `label` | value |  |  |
| Items | `hasLabel` | value | true |  |
| Items | `hasLeadingIcon` | value | false |  |
| Items | `icon` | object |  |  |
| Items | `disabled` | value | false |  |
| Items / Properties | `items` | array |  |  |
| Selection / Properties | `selectedValue` | value |  |  |
| Direction / Properties | `direction` | value | horizontal | horizontal, vertical |

Events: `onChange`.

## 18. Progress Bar

<a id="progress-bar"></a>

Disposition: `stock`. Cadre equivalent: `ia.display.progress`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Type / Properties | `type` | value | linear | linear, circular |
| Value / Properties | `value` | value | 0 |  |
| Linear Progress Bar / Properties | `mode` | value | determinate | determinate, indeterminate |
| Linear Progress Bar / Properties | `showValue` | value | false |  |
| Linear Progress Bar / Properties | `showState` | value | false |  |
| Linear Progress Bar / Properties | `stateLabel` | value | Open |  |
| Linear Progress Bar / Properties | `hasDescription` | value | false |  |
| Linear Progress Bar / Properties | `description` | value | Description text |  |
| Circular Progress Bar / Properties | `circularState` | value | determinate | determinate, indeterminate, icon |
| Circular Progress Bar / Properties | `progressiveIndeterminate` | value | false |  |

## 19. Radio Button Group

<a id="radio-button-group"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.radio-group`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Options | `label` | value | empty |  |
| Options | `value` | value |  |  |
| Options / Properties | `options` | array |  |  |
| Value / Properties | `value` | value | empty |  |
| Several Groups in One View / Properties | `name` | value | default |  |
| Several Groups in One View / Properties | `required` | value | false |  |

Events: `onActionPerformed`.

## 20. Sequence Loading Spinner

<a id="sequence-loading-spinner"></a>

Disposition: `partial`. Cadre equivalent: `cadre/anim/spin` animation class (the progress ring of the symbols).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Type / Properties | `type` | value | indicator | indicator, indicator-point, tag, tag-point, button, button-point |
| Progression / Properties | `progression` | value | determinate | determinate, scanning |
| Progression / Properties | `progressPercent` | value | 0 |  |
| Progression / Properties | `rotationDurationMs` | value | 1000 |  |
| Properties | `style` | object |  |  |

## 21. Slide Button

<a id="slide-button"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Sliding / Properties | `autoDisable` | value | false |  |
| Label and Icon / Properties | `label` | value | Slide to confirm |  |
| Label and Icon / Properties | `hasLeadingIcon` | value | true |  |
| Label and Icon / Properties | `icon` | object |  |  |
| Label and Icon / Properties | `icon.path` | value | placeholder |  |
| Width / Properties | `hugContent` | value | false |  |

Events: `onActionPerformed`.

## 22. Slider

<a id="slider"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.slider`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value and Range / Properties | `value` | value | 50 |  |
| Value and Range / Properties | `min` | value | 0 |  |
| Value and Range / Properties | `max` | value | 100 |  |
| Value and Range / Properties | `step` | value | 1 |  |
| Variant / Properties | `variant` | value | normal | normal, enhanced, no-input |
| Step Buttons / Properties | `hasLeftIcon` | value | false |  |
| Step Buttons / Properties | `leftIcon` | object |  |  |
| Step Buttons / Properties | `hasRightIcon` | value | false |  |
| Step Buttons / Properties | `rightIcon` | object |  |  |
| Step Buttons / Properties | `stepClick` | value | 10 |  |
| Pressing on the Track / Properties | `allowSeaking` | value | false |  |
| Pressing on the Track / Properties | `seekingSpeed` | value |  |  |

Events: `onActionPerformed`.

## 23. Status Indicator

<a id="status-indicator"></a>

Disposition: `partial`. Cadre equivalent: Status row of the automation symbols.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Status / Properties | `status` | value | active | active, inactive, running, caution, warning, alarm |
| Label / Properties | `label` | value | Label |  |

## 24. Stepper Box

<a id="stepper-box"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.numeric-entry-field` (spinner mode).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value and Steps / Properties | `value` | value | 50 |  |
| Value and Steps / Properties | `stepUp` | value | 1 |  |
| Value and Steps / Properties | `stepDown` | value | 1 |  |
| Value and Steps / Properties | `min` | value | 0 |  |
| Value and Steps / Properties | `max` | value | 100 |  |
| Type / Properties | `type` | value | plus-minus | plus-minus, left-right, up-down |
| Unit and Helper Text / Properties | `unit` | value |  |  |
| Unit and Helper Text / Properties | `helperText` | value |  |  |
| Unit and Helper Text / Properties | `placeholder` | value |  |  |
| Read-only and Disabled / Properties | `readonly` | value | false |  |

Events: `onActionPerformed`, `onUp`, `onDown`.

## 25. Tab Row

<a id="tab-row"></a>

Disposition: `implemented`. Cadre equivalent: Selected-state button row pattern (faceplate commands, alerts page tabs, diagram toolbar).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Tabs | `id` | value |  |  |
| Tabs | `title` | value |  |  |
| Tabs | `showSubtitle` | value | false |  |
| Tabs | `subtitle` | value |  |  |
| Tabs | `hasLeadingIcon` | value | false |  |
| Tabs | `leadingIcon` | object |  |  |
| Tabs | `badges` | array |  |  |
| Tabs | `disabled` | value | false |  |
| Tabs / Properties | `tabs` | array |  |  |
| Selection / Properties | `selectedTabId` | value |  |  |
| Badges | `type` | value | regular |  |
| Badges | `size` | value | regular | regular, large |
| Badges | `count` | value | 0 |  |
| Badges | `showIcon` | value | false |  |
| Badges | `badgeIcon` | object |  |  |
| Closing and Adding Tabs / Properties | `hasClose` | value | false |  |
| Closing and Adding Tabs / Properties | `hasAddNewTab` | value | false |  |
| Layout / Properties | `hug` | value | false |  |
| Layout / Properties | `centerContent` | value | false |  |
| Properties | `style` | object |  |  |

Events: `onTabSelected`, `onTabClosed`, `onAddNewTab`.

## 26. Tag

<a id="tag"></a>

Disposition: `gap`. Cadre equivalent: None.

No requirement in process screens so far; each is a small view when needed.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Label / Properties | `label` | value |  |  |
| Color / Properties | `color` | value | gray | gray, blue, cyan, teal, green, yellow, orange, red, purple, indigo |
| Size / Properties | `size` | value | regular | regular, large |
| Icon / Properties | `hasIcon` | value | false |  |
| Icon / Properties | `icon` | object |  |  |
| Icon / Properties | `icon.path` | value | placeholder |  |
| Properties | `style` | object |  |  |

## 27. Text Input Field

<a id="text-input-field"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.text-field`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value |  |  |
| Value / Properties | `placeholder` | value |  |  |
| Value / Properties | `deferUpdates` | value | false |  |
| Value / Properties | `rejectUpdatesWhileFocused` | value | false |  |
| Value / Properties | `convertToPrimitives` | value | true | number, boolean, null |
| Type / Properties | `type` | value | text | text, password, date, time |
| Field / Properties | `hasLeadingIcon` | value | false |  |
| Field / Properties | `leadingIcon` | object |  |  |
| Field / Properties | `hasClearButton` | value | false |  |
| Field / Properties | `textAlign` | value | left | left, center |
| Field / Properties | `readonly` | value | false |  |
| Label and Helper Text / Properties | `label` | value |  |  |
| Label and Helper Text / Properties | `labelPlacement` | value | left | left, center, right |
| Label and Helper Text / Properties | `hasLabelIcon` | value | false |  |
| Label and Helper Text / Properties | `labelIcon` | object |  |  |
| Label and Helper Text / Properties | `helperText` | value |  |  |
| Label and Helper Text / Properties | `helperPlacement` | value | left | left, center, right |
| Label and Helper Text / Properties | `hasHelperIcon` | value | false |  |
| Label and Helper Text / Properties | `helperIcon` | object |  |  |
| Label and Helper Text / Properties | `required` | value | false |  |
| Error / Properties | `error` | value | false |  |
| Error / Properties | `errorText` | value |  |  |

Events: `onActionPerformed`.

## 28. Textarea Field

<a id="textarea-field"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.text-area`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Value / Properties | `value` | value |  |  |
| Value / Properties | `placeholder` | value |  |  |
| Value / Properties | `deferUpdates` | value | false |  |
| Value / Properties | `rejectUpdatesWhileFocused` | value | false |  |
| Value / Properties | `convertToPrimitives` | value | true | number, boolean, null |
| Label / Properties | `showLabel` | value | false |  |
| Label / Properties | `label` | value |  |  |
| Label / Properties | `required` | value | false |  |
| Leading Icon / Properties | `hasLeadingIcon` | value | false |  |
| Leading Icon / Properties | `leadingIcon` | object |  |  |
| Toolbar / Properties | `showToolbar` | value | false |  |
| Error / Properties | `error` | value | false |  |
| Error / Properties | `errorText` | value |  |  |

Events: `onActionPerformed`, `onScreenshotClick`, `onImageClick`, `onAttachmentClick`, `onSendClick`.

## 29. Toggle Button Horizontal

<a id="toggle-button-horizontal"></a>

Disposition: `implemented`. Cadre equivalent: Selected-state button row pattern (faceplate commands, alerts page tabs, diagram toolbar).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Options | `label` | value |  |  |
| Options | `value` | value |  |  |
| Options | `icon` | object |  |  |
| Options | `disabled` | value | false |  |
| Options / Properties | `options` | array |  |  |
| Selection / Properties | `value` | value |  |  |
| Selection / Properties | `allowEmptySelection` | value | false |  |
| Type / Properties | `type` | value | text | text, icon, text-icon, icon-text-under |
| Variant / Properties | `variant` | value | regular | regular, flat, normal |
| Size / Properties | `large` | value | false |  |
| Size / Properties | `hugText` | value | false |  |

Events: `onActionPerformed`.

## 30. Toggle Button Vertical

<a id="toggle-button-vertical"></a>

Disposition: `implemented`. Cadre equivalent: Selected-state button row pattern (faceplate commands, alerts page tabs, diagram toolbar).

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Options | `label` | value |  |  |
| Options | `value` | value |  |  |
| Options | `icon` | object |  |  |
| Options | `disabled` | value | false |  |
| Options / Properties | `options` | array |  |  |
| Selection / Properties | `value` | value |  |  |
| Selection / Properties | `allowEmptySelection` | value | false |  |
| Icons / Properties | `hasIcon` | value | false |  |
| Icons / Properties | `labelPlace` | value | inline | inline, under |
| Type / Properties | `type` | value | regular | regular, flat, normal |
| Properties | `hugWidth` | value |  |  |

Events: `onActionPerformed`.

## 31. Toggle Switch

<a id="toggle-switch"></a>

Disposition: `stock`. Cadre equivalent: `ia.input.toggle-switch`.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| State / Properties | `checked` | value | false |  |
| Label / Properties | `label` | value |  |  |

Events: `onActionPerformed`.

## 32. User Button

<a id="user-button"></a>

Disposition: `framework`. Cadre equivalent: `Framework/TopBar` user button and the `Framework/UserMenu` popup.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Icon or Initials / Properties | `variant` | value | icon | icon, initials |
| Icon or Initials / Properties | `initials` | value |  |  |
| Icon or Initials / Properties | `icon` | object |  |  |
| Icon or Initials / Properties | `icon.path` | value | user |  |
| Label / Properties | `label` | value | User |  |
| Style / Properties | `styleType` | value | flat | flat, normal, selected |
| Static / Properties | `static` | value | false |  |

Events: `onActionPerformed`.

## 33. User Menu

<a id="user-menu"></a>

Disposition: `framework`. Cadre equivalent: `Framework/TopBar` user button and the `Framework/UserMenu` popup.

| Section | Property | Type | Default (parsed) | Values (parsed) |
|---|---|---|---|---|
| Type / Properties | `type` | value | sign-in | sign-in, user-sign-in, loading-sign-in, signed-in |
| Signing In | `username` | value |  |  |
| Signing In | `password` | value |  |  |
| Signing In / Properties | `username` | value |  |  |
| Signing In / Properties | `password` | value |  |  |
| Signing In / Properties | `usernameError` | value |  |  |
| Signing In / Properties | `passwordError` | value |  |  |
| User / Properties | `userInitials` | value |  |  |
| User / Properties | `userLabel` | value |  |  |
| Recent Users | `initials` | value |  |  |
| Recent Users | `label` | value |  |  |
| Recent Users / Properties | `hasRecentlySignedIn` | value | false |  |
| Recent Users / Properties | `recentUsers` | array |  |  |
| Actions | `id` | value |  |  |
| Actions | `label` | value |  |  |
| Actions | `hasIcon` | value | false |  |
| Actions | `icon` | object |  |  |
| Actions / Properties | `signedInActions` | array |  |  |
| Size of the Content / Properties | `size` | value | regular | regular, small |

Events: `onSignedInClick`, `onSignedOutClick`, `onRecentUserClick`, `onSignedInActionClick`.
