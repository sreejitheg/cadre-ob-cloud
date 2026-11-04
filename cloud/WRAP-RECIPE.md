# Wrap Recipe and T1 Survey

Prepared 2026-11-03 for tranche T1 of the Cadre OpenBridge library build. It records the pattern of wraps W1 to W3
(commits `743e0f4`, `ad6a5b6`, `3723234`; `wiki/12-module-spike.md` subsections 17.10 to 17.12; `cloud/REPORT-T0.md`
section 3) so that a subagent wraps one element without reading the generator, `tools/hmi/screen.py` and the tests
to rediscover it. Sections 1 to 6 are the recipe; section 7 is the survey of the 31 T1 elements. Read `CLAUDE.md`
first: its non-negotiables bind every wrap. The shape of a change can always be read again with
`git show <commit> -- <path>`.

## 1. Ground Rules of a Wrap

1. A wrap changes sources only. It does not build the module, change `module/build.gradle.kts`, touch the gateway
   or commit. The orchestrator builds once per batch.
2. Facts come from the pinned manifest `module/web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json`
   (attributes, enumerations, events, slots). Nothing is taken from recall or from the upstream repository.
3. A batch runs in one subagent, one element after another, or in sequential subagents. Wraps never run in
   parallel: they edit the same twelve files (section 5.4).
4. Edit all the sources of the batch first, then run the generation steps (sections 2.3 and 2.5) once for the batch.
   Generation is deterministic and rewrites whole files, so a run per element costs tokens and adds nothing.
5. Append a dated line to `cloud/PROGRESS.md` after each element: what was done, test counts, tokens if known.

## 2. The Steps in Order

### 2.1 Bundle import: `module/web/entry.js`

One import per element, in the file's order, from `dist` of the package:

```js
import '@oicl/openbridge-webcomponents/dist/automation/filter/filter.js';
```

The path is `dist/<folder of the manifest path>/<file>.js`. Two manifest folders differ from the tag
(`valve-analoge-two-way-icon` holds `valve-analog-two-way-icon`); take the path from `modules[].path`.

### 2.2 Measured defaults: `module/tools/measure_defaults.py`

Add the tag to the list `TAGS` (one line, `"obc-filter"` was inserted after `"obc-analog-valve"`). The tool builds
a throwaway page with the bundle and reads every attribute's default from a created element, so it needs the bundle
first:

```
cd module/web && npm run build && cd ../..
python module/tools/measure_defaults.py        # rewrites module/web/defaults.json (all tags; additions only)
```

`defaults.json` gains an entry keyed by tag. Do not edit it by hand. Review the diff: it must add entries and leave
the existing ones unchanged.

### 2.3 The contract entry: `module/tools/gen_module_assets.py`

Add one dictionary to the list `COMPONENTS` (shape copied from W1; the key set is `tag`, `type`, `name`, `title`,
`palette`, `size`, `exclude`, and optionally `properties`, `extra`, `events`, `describe`, `data`, `generator`):

```python
{"tag": "obc-filter", "type": "cadre.ob.filter", "name": "filter", "title": "OB Filter",
 "palette": "OpenBridge filter: a static symbol on a diagram, with readout, badges and alert frame",
 "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
```

Rules for each key:

1. Properties are the manifest's attributes, taken by `schema_for`. An enumeration comes from the element's own
   declaration (`enums()`); a property whose type the generator cannot map is printed as `skipped` and left out:
   read the generator's output and decide for each skipped one (for example `number | null | undefined` is mapped,
   an object type is not).
2. `exclude` lists attributes the component must not carry (the readout excludes `data` and `lineType`).
3. `properties: ["showStatus"]` adds the element's own boolean `showStatus` field (table `PROPERTIES`). It requires
   the manifest to declare that field as a boolean, or the generator stops. Use it for any element that draws a
   state readout beside the symbol (the electrical symbols do, as the filter and the valves do).
4. `extra` names properties the module adds that the element lacks (table `EXTRA`: `on`, `tag`, `readoutPosition`,
   `alert`, `alertFrameStatus`, `alertFrameMode`, `showStatus`, `statusText` and others). A new entry in `EXTRA` has
   `kind`, `def` and `schema`; where its values are an OpenBridge enumeration, give `"enum": "AlertType"` and so on.
   W2 is the example; use it only for an element without those attributes.
5. `events` lists the element's DOM events by name; each needs a row in the table `ALERT_EVENTS` (despite its name,
   the table of every event the wrapper carries): the DOM name maps to the component event name, the payload kind
   (`none` for no detail) and a description. W3 added
   `"click": ("onPress", "none", "The button was pressed. The event carries nothing; ...")`. The name is never
   `onClick`, which Perspective already uses. A row also needs the event schema file (section 2.4).
6. `generator: True` is the W2 wrapper branch (a disc whose state selects the element's scheme) and applies to an
   indicator of that kind only; do not reuse the flag for another element without reading `applyGenerator` and
   `drawGenerator` in the `WRAPPER` string of the same file.
7. `data` declares array or JSON properties (the alert lists); an element with `number[]` attributes
   (`indicator-battery`, `indicator-tank-atmospheric`) uses it with the converters of `CONVERT`.
8. `size` is the default size in the Designer: 96 by 96 for a symbol, the element's own measured size otherwise.

### 2.4 Registration: `module/common/src/main/java/cadre/hmi/ob/common/CadreOb.java`

One line in the `DESCRIPTORS` list, after the last wrapped element. The arguments are the id, the short `name` of
the schema file (`schemas/<name>.props.json`), the palette title, the description, a meta name, and the events:

```java
descriptor("cadre.ob.filter", "filter", "OB Filter",
    "OpenBridge filter: a static symbol on a diagram, with readout, badges and alert frame.", "obFilter", List.of()),
```

An element with an event adds `List.of(event("button", "onPress", "The button was pressed; the event carries nothing."))`
and the file `module/common/src/main/resources/schemas/<name>.onPress.json`, which the generator writes (W3:
`{"type": "object", "description": "...", "properties": {}}`). The gateway hook logs the count, so the batch changes
"Registered 14 Cadre OpenBridge components" by the number of elements.

### 2.5 Regeneration

```
cd module/web && npm run build && cd ../.. && python module/tools/gen_module_assets.py
```

It writes `schemas/<name>.props.json`, `module/components.json` and `.../mounted/js/cadre-ob.js` (and the stylesheet
where a `sheet` is declared). Never edit these by hand (non-negotiable 4). `cadre-ob.js` changes by a large diff
because the bundle is re-emitted; that is normal. The run must also leave the earlier components unchanged.

### 2.6 The generator's tables: `tools/hmi/screen.py`

These tables connect a library kind (a descriptor's `kind`) to the module component under `--render module`. They are
read by `embed_symbol`, `embed_module` and `module_draws`. For an element with a library kind, add one entry to each
table that applies (W1 added the filter to all but `MODULE_STATE`):

| Table | Meaning | Add when |
|---|---|---|
| `MODULE_KIND` | library kind to component id; its presence makes the kind a candidate | always |
| `MODULE_PARAM` | library parameter to component property where the names differ (`{}` if none) | always (an empty dictionary) |
| `MODULE_DROP` | library parameters the component has no property for; they are not emitted. `_STATUS_DROP` is the common base (`showStatus`, `statusText`, `hasTag`, `deviceId`, `deviceKind`, `deviceLabel`, the duty and out of service marks). Add what the element lacks: `hasSpeed`, `speed`, `value`, `vertical`, `variant`, `progress`, `activated`, `badge*` | always |
| `MODULE_IF_LISTED` | properties emitted only if `module/components.json` lists them (`_STATUS_PROPS`); a build is then the same before and after a module release | when the component may or may not carry the status props |
| `MODULE_NEEDS` | `{kind: {param: [allowed values]}}`: a symbol whose parameter has any other value keeps the library view | when the component cannot draw a library value (the filter: `variant` in `regular`, `flat`) |
| `MODULE_EXCEPT` | `{kind: [{param: value, ...}]}`: a symbol whose parameters match one dictionary keeps the library view | when the library has a flag the element does not map (a vertical filter, the generator set) |
| `MODULE_VALUE` | `{kind: {param: {library value: component value}}}`: the same value under another name | when enumerations differ (library `regular` is the filter's `square`); applied in `embed_module` and in `testbench.module_value_ok` |
| `MODULE_STATE` | parameters the component states with the contract default where the symbol gives none | only if the component's own default differs from the library view's (pump `hasSpeed`) |
| `module_probe` | function, not a table: a bound parameter that `MODULE_NEEDS` names and `MODULE_DROP` drops counts as stated, so the symbol keeps the library view | no edit; it is why a bound parameter the component drops forces the library view |

If the component lacks `positioning`, `embed_module` states it only where the schema lists it (W2 changed that);
no edit is needed for a later element. If a library parameter has no component property and no table covers it, the
test `test_every_module_property_the_generator_states_is_in_the_components_schema` of `tests/test_hmi.py` fails: add
it to `MODULE_DROP` or `MODULE_PARAM`.

### 2.7 The test page: `tools/hmi/testbench.py`

For a library kind in `SYMBOL_KINDS` the page already has its cases and needs no block (W1). `testbench.py` is
touched when the module's enumeration differs from the library's: `module_value_ok` already honours `MODULE_VALUE`.
A new block (W3 added the Start generator button to `devices_block`) is needed only for something the library page
cannot show: a control, or an element with no library kind (section 7.2).

### 2.8 The glass gates: `tools/compare/glass_gates.py`

Add the element to the dictionary `MODULE_TAGS` (library kind to element tag), so that the readouts gate finds it:

```python
MODULE_TAGS = {..., "filter": "obc-filter", "generator": "obc-indicator-generator"}
```

### 2.9 The walk plan: `tools/compare/walk_plan.py`

Only for a stateful device the walk drives. Add the dictionary of component properties the walk reads, by kind, to
`MODULE_PROP` (W2: `"generator": {"on": "on", "alert": "frame"}`). A static symbol has no entry (W1 made none). A kind
whose state is not `on` also needs `STATE_PARAM`.

### 2.10 The profile: `library/profile.json`

Generated from the tables above; never edit it. Regenerate with `python tools/hmi/library_profile.py` (the default
output is `library/profile.json`). The diff shows `module`, `moduleExcept` and `moduleNeeds` filled for the kind. If
the kind is new to the library, `library/contracts.json` is regenerated by `python tools/hmi/parent.py --out <scratch>`
(section 7.2).

### 2.11 Tests

1. `tests/test_module.py`: copy the class `FilterComponent` (five tests: the contract and the manifest attributes,
   the manifest and the contract agree, the enumerations, Java and bundle registration, and the props the element
   must not carry). Change `ctype`, the `MANIFEST_ATTRIBUTES` set (the manifest's `fieldName`s, less none), the
   enumerations and defaults taken from the generated schema, and the tag in the regular expression
   `r'\(\[\w+\("obc-filter"\)\]'`. Where the element has `showStatus`, add the component to the tuple in
   `DeviceProps.test_the_other_components_do_not_carry_them`. W3's `ButtonComponent` is the template for an event
   (`events` entry, the schema file, the listener strings in `JS`).
2. `tests/test_hmi.py`: three places move with a mapping. In `FirstRenderTests` the loop
   `for kind in ("motor", "valve", "analogvalve", "fan", "filter", ...)` gains the kind; the equality
   `(screen.MODULE_NEEDS, screen.MODULE_EXCEPT)` (an exact dictionary) gains the new entries; and one case per
   `MODULE_VALUE` or `MODULE_EXCEPT` rule is added (W1: square, flat and vertical). In `ToolbarTests` the set
   `kinds == {...}` of component types the page's symbols use gains the new type. Run the module tests and
   `test_hmi` and read each failure: a new mapping changes only these.
3. `tests/test_asm_devices.py` (W2) holds the sample's expectations for a generator on both renderings; update only
   where the sample now draws the component.

### 2.12 The wiki: `wiki/12-module-spike.md`

Add a subsection after the last (17.13 onwards, or the T1 section the orchestrator names) in the register of
17.10 to 17.12: what the element draws, properties (count and enumerations), generator and bundle, the test page
(cases that become module components and cases that stay on the library view, with the reason), and tests. Facts only,
numbered, no em or en dashes, no arrows. Add a sentence to `wiki/13` only where the wrap changed an ASM rule
(W2 and W3 each added one).

## 3. Extras by Class

### 3.1 Static symbol (W1, 0.13 M tokens)

An element on the filter's attribute set (`on`, `variant`, `orientation`, `readoutPosition`, `tag`, `activated`,
`alert*`, `progress*`, four badges) needs sections 2.1 to 2.12 and nothing else: the element draws its own readout and
alert frame, and the page's `custom.alerts` bindings (wiki 13 section 11.2) colour it. Compare the library flags to
the element's enumerations (section 5.1) and map or except each mismatch. No `ALERT_EVENTS` row, no walk entry.

### 3.2 Stateful device (W2, 0.24 M tokens)

1. States come from the kind's members: `profile.json` `kinds.<kind>.members` and `bind` (the generator binds `on`
   to `state`); the symbol binds nothing the library kind does not bind. A fault shows through the alarm frame
   (wiki 13 section 12), not a new binding.
2. If the element has no `alert*` attributes, add `alert`, `alertFrameStatus`, `alertFrameMode` through `extra` and
   draw the frame in the wrapper with OpenBridge's unchanged `obc-alert-frame` (`drawGenerator`: type
   `small-side-flip`, thickness `small`, status and mode from the properties). Never change OpenBridge's code
   (non-negotiable 7). Set the plain fields the glass gates read (`tag`, `on`, `alert`, `alertFrameMode`) on the
   element as `applyGenerator` does.
3. The identifier and status word use OpenBridge's `obc-automation-button-readout-stack`, unchanged.
4. The faceplate click needs no recipe edit: `embed_module` gives every module component the `onClick` script that
   calls `cadre.hmi.select_device` and opens the faceplate for a symbol naming a device. Check `framework.FACEPLATE_VIEW`
   has the kind. G11 clicks the centre of every `cadre.ob.` box.
5. Add the walk entry (section 2.9) and `MODULE_NEEDS` for every library mark the element does not draw.
6. An element with its own `click` (the specialty tanks, `automation-readout`) is also a shared control for the
   wrapper: carry the event as `onPress` and keep the faceplate click.

### 3.3 Shared control (W3, 0.19 M tokens)

1. Carry the element's event as a component event: `events` in the spec, a row in `ALERT_EVENTS`, the schema file,
   the Java `event(...)`.
2. The owner's rule for every command control: it asks on press and writes only on Confirm, through the existing write
   paths with the `Administrator` check (COBD-024), never directly. The component event therefore never writes. It
   sets the pending flag, and the existing Confirm button calls `cadre.hmi.page_pulse` (write path W18) or the path of
   the command in question. G7 commands refuses any control that names a checked write and lacks `enabled` bound
   to the permission of that path.
3. An element without `enabled` (the button) is drawn `static` while the session lacks the permission, bound to
   `!{view.custom.can.<path>}`; the check itself stays in Confirm and in the path.
4. The descriptor reaches the control by a part, not a symbol: W3 added `render` to the pulse button of
   `schemas/screen-descriptor.schema.json` and `parts.button_node(..., module=False)` draws the Press as the module
   component. A new control follows that route (schema key, `parts.check`, `button_node`, a `testbench` button, a
   test in `tests/test_asm_parts.py`). An event that selects a value (the hydraulic valves' `position-selected`)
   carries a payload (`payload` kind in `ALERT_EVENTS`; the alert lists show `visible` and `ids`) and writes only
   after the same Press, Confirm.

## 4. Verification

### 4.1 Offline, by the wrap

1. `python -m unittest tests.test_module` after each element; then `tests.test_hmi tests.test_asm_devices
   tests.test_asm_parts` after the batch.
2. The component test page with G0 to G7, without `--deploy` (the command of T0, run from the repository root; the
   ASM parent must exist in `build/`, built by `python tools/hmi/parent.py --out build --name cadre_hmi_base_asm`):
   `python tools/hmi/screen.py --project cadre_hmi_ctest --component-test --tag-root "[default]cadre_hmi_ctest"
   --app-name "Component Test" --alarm-scope "*cadre_hmi_ctest*" --frame asm --faceplate asm --render module
   --parent cadre_hmi_base_asm --write-descriptor workspace/ctest --write-devices workspace/ctest/devices.json
   --out build --report workspace/reports/ctest.json`. All of G0 to G7 pass (19 devices and 21 device symbols at
   the end of T0). `build/cadre_hmi_ctest` and `workspace/` are excluded from git in the cloud copy.
3. The full suite once at the end of the batch: `env -u CADRE_TEST_LOGIN python -m unittest discover -s tests`
   (about 4 minutes; 1102 passing at the end of T0, more since the G10 fix; the variable breaks one environmental
   test).
4. A Chromium check of the wrapper where it adds drawing (W2): a stand-in page with the bundle, one element per case.

### 4.2 On the gateway, by the orchestrator, once per batch after the joint build

1. Build and install the module (`build_module.py`, `install_module.py`, restart), redeploy `cadre_hmi_base_asm` and
   `cadre_hmi_ctest`.
2. G8 on `/component-test` (`tools/compare/capture.py`): no quality overlay, no error badge (4424 components at the
   end of T0).
3. G11: `python tools/compare/faceplates.py --faceplate asm` for the stateful devices (about 15 minutes; the only
   accepted finding is the baseline's `TB_FIELD` identity).
4. A browser count of each new element on `/component-test`: `page.locator('obc-<name>').count()` equals the number of
   cases that became module components, each with a non-zero box and no console error (T0: 12 `obc-filter`, 12
   `obc-indicator-generator`, 1 `obc-automation-button`).
5. For a command control, the write check of W3: signed out, Confirm is disabled and a forced click writes nothing;
   signed in as the test user (`Administrator`), the tag is written and restored.

## 5. Pitfalls Met in T0

1. **Orientation and variant mismatches.** The library has a `vertical` flag; the filter has `horizontal`,
   `verticalRight`, `verticalLeft`, and the flag does not say which. Put `{"vertical": True}` in `MODULE_EXCEPT`
   and add `vertical` to `MODULE_DROP`. The variant `regular` of the library is `square` on the filter: `MODULE_VALUE`
   plus `MODULE_NEEDS`. Read each enumeration from the schema, never from the library.
2. **Elements with no `enabled`.** The button has none; a component event cannot be gated. Use `static` (section
   3.3). Any element that is a command and lacks `enabled` needs this.
3. **Elements with no `positioning`, no `alert` or no `tag`.** `embed_module` states `positioning` only where the
   schema lists it; the generator indicator needed `extra` for the rest.
4. **Glass probes read element fields.** The glass gates read `tag`, `on`, `alert`, `alertFrameMode` as plain fields
   of the element. A wrapper that draws state in the shadow root must also set them on the element (W2).
5. **Files that conflict between parallel wraps.** The twelve shared files: `entry.js`, `measure_defaults.py`,
   `defaults.json`, `gen_module_assets.py`, `CadreOb.java`, `components.json`, the schemas, `cadre-ob.js`,
   `screen.py`, `glass_gates.py`, `profile.json`, `tests/test_module.py` and `test_hmi.py`, and `wiki/12`. A batch
   runs in one subagent, or in sequential subagents; regenerate once at the end.
6. **A bound parameter the component drops** (`progress` on the generator) keeps the library view through
   `module_probe`; the test page counts such cases as library cases, not as failures.
7. **A name is not a tag.** `obc-digital-valve` is the valve; `MODULE_TAGS` maps kinds to real tags (COB-194).
8. **`playwright` version.** `measure_defaults.py` and the Chromium checks need Playwright 1.63.0 (CLAUDE.md,
   REPORT-T0 section 1.3).
9. **Counts in tests.** `test_hmi` asserts exact dictionaries and sets (section 2.11); update them, do not loosen them.

## 6. The Owner's Decisions for T1

1. The nine OpenBridge line elements (`bus`, `corner-line`, `direction-line`, `end-point-line`, `horizontal-line`,
   `vertical-line`, `three-way-line`, `line-cross`, `line-overlap`) are skipped for now: they overlap the library's
   pipes and the flow solver (G6). Do not wrap them and do not add them to `MODULE_KIND`. Superseded on 2026-11-04 by item 9 of section 6.1.
2. Command controls use Press then Confirm. No component event writes a tag.
3. An element without a library kind becomes a module-only kind (section 7.2, Option B, decided 2026-11-03): its
   contract comes from `module/components.json`, the component test page shows it in one "Module only" section,
   and under `--render stock` the build refuses it with an error rather than draw a gap silently. Batch B0 builds
   this once; every later batch adds its elements to the module-only table and follows section 2. A kind is
   promoted to a library kind later, and only when a stock screen needs it.
4. Elements whose events or properties imply a write (the `position-selected` event of `hydraulic-valve-4-3` and
   `hydraulic-valve-x-2`, the setpoints of the gauges) are wrapped for display and state only in T1; the write is
   recorded as an open item in the wiki subsection, and no binding writes. `automation-input-modal` is examined and,
   if it has no faithful wrap, recorded as not wrapped.

### 6.1 The Owner's Decisions for T2 (2026-11-03)

5. The parent framework moves onto OpenBridge's frame components through a **new frame option** beside
   `--frame openbridge` and `--frame asm`, which stay unchanged; the new frame has its own gates, with G10's frame
   checks adapted to it, and existing projects change only when switched over.
6. **All 33 frame components** of the pinned release are wrapped, not only the set the current frame uses.
7. The bars and graphs and the building blocks are module-only kinds, display only, as in T1.
8. The new frame comes in both variants (OpenBridge and ASM), keeps the Cadre crumb and the Cadre alert strip, and hides
   the silence control (`cloud/FRAME-DESIGN.md`, Owner's Answers).
9. (2026-11-04) The nine OpenBridge line elements are wrapped as **module-only components** (glyph or symbol form by their
   attributes, section 8.10), so that a pipe component exists in the module and on the component test page. The generator keeps
   drawing its own pipes as SVG paths and the flow solver (gate G6) is unchanged; the line elements are display only and
   are not added to `MODULE_KIND`. Wiki 12 section 17.28 records them.

## 7. The T1 Survey

### 7.1 The 31 elements

Counts come from the pinned manifest. "Filter set" means the 22 attributes of `obc-filter` (section 3.1). The class column uses the three classes of the recipe. Library kinds are those of `KIND_VIEW`:
pump, motor, fan, valve, analogvalve, damper, filter, switch, tank, readout, instrument-field, controller,
indicator, sequence, generator.

| Element (`obc-`) | Attributes | Filter set | Events | Same thing as a library kind | Class | Batch |
|---|---|---|---|---|---|---|
| damper | 21 | yes, less `alternativeIcon` | none | yes, `damper` (`Automation/Damper`) | Static symbol | B1 |
| switch | 22 | yes | none | yes, `switch` (`Automation/Switch`) | Static symbol | B1 |
| resistor | 22 | yes | none | none | Static symbol | B1 |
| capacitor | 22 | yes | none | none | Static symbol | B1 |
| diodes | 22 | yes | none | none | Static symbol | B2 |
| ground | 22 | yes | none | none | Static symbol | B2 |
| source | 22 | yes | none | none | Static symbol | B2 |
| converter | 22 | yes | none | none | Static symbol | B2 |
| transformer | 22 | yes | none | none | Static symbol | B2 |
| bipolar-transistor | 22 | yes | none | none | Static symbol | B3 |
| mosfet | 22 | yes | none | none | Static symbol | B3 |
| logic | 22 | yes | none | none | Static symbol | B3 |
| router | 22 | yes | none | none | Static symbol | B3 |
| automation-badge | 2 (`mode`, `type`) | no | none | none (the library draws corner badges inside its symbols) | Static symbol | B4 |
| hydraulic-check-valve | 2 (`ariaLabel`, `vertical`) | no | none | none | Static symbol | B4 |
| valve-analog-two-way-icon | 3 (`value`, `closed`, `vertical`) | no | none | partly: `analogvalve` draws the full valve; this is the glyph | Static symbol | B4 |
| valve-analog-three-way-icon | 4 (`value`, `value2`, `closed`, `horisontal`, sic) | no | none | none | Static symbol | B4 |
| indicator-battery | 6 (`direction`, `variant`, `value`, `level`, `data`, `hasIcon`) | no | none | none (the library holds only an `energy-battery` icon) | Stateful device | B5 |
| indicator-engine | 2 (`value`, `direction`) | no | none | none | Stateful device | B5 |
| indicator-tank-atmospheric | 6 (as the battery) | no | none | none (`tank` is another element) | Stateful device | B5 |
| automation-readout | 5 (`value`, `unit`, `numberOfDigits`, `position`, `lineType`) | no | `click` | similar: `readout` (drawn by `obc-transmitter`, wrap of 0.3.1); decide the mapping | Stateful device | B5 |
| heat-exchanger | 14 (12 shared, plus `medium`, `static`) | partly | `click` | none (icon `heatexhanger` only) | Stateful device | B6 |
| heat-pump | 14 (as above) | partly | `click` | none (icon `heatpump` only) | Stateful device | B6 |
| hydraulic-separator | 14 (as above) | partly | `click` | none (icon `hydraulic-separator` only) | Stateful device | B6 |
| gauge-generator | 30 | no | none | none | Stateful device | B7 |
| gauge-motors-and-pumps | 30 (the same set) | no | none | none | Stateful device | B7 |
| gauge-valve | 18 | no | none | none | Stateful device | B7 |
| hydraulic-valve-4-3 | 4 (`type`, `ariaLabel`, `selectedPosition`, `vertical`) | no | `position-selected` | none | Shared control | B8 |
| hydraulic-valve-x-2 | 4 (as above) | no | `position-selected` | none | Shared control | B8 |
| transmitter-button | 14 | no | none declared (the host's DOM `click`; verify in Chromium) | none | Shared control | B8 |
| automation-input-modal | 0 (four slots: `header`, `preview`, `action-primary`, `action-secondary`) | no | none | none | Shared control | B8 |

The twelve electrical elements share the filter's set exactly (the damper lacks only `alternativeIcon`), so their
wraps are copies of W1; the three specialty elements (`heat-*`, `hydraulic-separator`) extend the specialty tank and
carry `static`, `medium` and a `click`; the two valves and the modal need a decision in section 7.3.

### 7.2 How a descriptor reaches a symbol today, and the open question

1. **Today.** A descriptor symbol names a `kind` (`schemas/screen-descriptor.schema.json`: a free string whose
   description lists fifteen kinds). `screen.view_of` returns `KIND_VIEW[kind]`, a library view in
   `library/contracts.json`; `embed_symbol` embeds that view, and under `--render module` hands the symbol to
   `embed_module` when `MODULE_KIND` has the kind and `module_draws` allows it. A kind with no view is drawn as a
   counted gap box (`gap_box`, `Report.gaps`, the text `GAP: <kind>`). So `damper` and `switch` need only the
   `MODULE_KIND` rows of section 2.6, as the filter did.
2. **What `embed_module` needs from the library.** A contract `c` of the kind: `c["params"]` defaults, `c["state"]`,
   `c["anchor"]` (`symbol-centre`), `symbolSize`, and the block size of `symbol_box`. At least six places read
   `contracts.get(view_of(s))` (`pipes_svg`, the layout at lines near 600, 923, 1204, 1273 and 1406 of `screen.py`,
   `parts.py`, and `testbench.py`). The test page builds its cases from `prof["kinds"]` and `SYMBOL_KINDS`.
3. **The question.** Eleven electrical elements, three specialty elements, and most of the rest have no library kind,
   so the descriptor can name them only as gap boxes, and the component test page under `--render module` has nowhere
   to place them. The smallest faithful way is needed for (a) the page and (b) a screen descriptor.

#### Option A: library kinds (factory rows)

For each element a row in `library.DEVICE_KINDS` (state parameter, on and off icons, status mode; the catalogue
`catalogue/mapping.json` already files the eleven as "factory: one row in DEVICE_KINDS"), an entry in `screen.KIND_VIEW`,
`PASS_KINDS` (the solver passes no medium), `walk_plan.AUTOMATION`, `testbench.SYMBOL_KINDS`, two converted icons per
kind (`tools/convert_icons.py` reads `src/icons/icon-<name>.ts` from raw.githubusercontent.com at the pin, a host not
on the admitted list of REPORT-T0 section 1.2; the same artwork is in `dist/icons/*.js` of the installed package, so the
converter would need a local-read mode), then `python tools/hmi/parent.py` regenerates `contracts.json` and
`profile.json`.

1. Stock rendering: the two state icon drawing of the other automation kinds, with the library's readout, badges and
   alert frame; no variant or orientation parity with the element.
2. Cost: about 0.30 to 0.45 M tokens once for the eleven electrical kinds, about 0.03 M for each kind added later.
   Tests that count the kinds move (`test_hmi` lines near 3342, 3695, 3709, 3743, 4018; `test_l5_lib` 281;
   `test_walk` 339 to 344, which asserts `len(walk.AUTOMATION) == len(DEVICE_KINDS)`; `profile.json`). The test page
   gains 12 cases per kind in both renderings (about 130 extra symbols for eleven kinds), which raises the page's cost
   in G8 and G11.
3. Gain: a stock build draws every kind; the library stays the single catalogue.

#### Option B: module-only kinds

A table `MODULE_ONLY` in `screen.py` (kind to component id) and no library view. In the stock rendering the kind is the
existing counted gap box, and the build reports an error (so the gates fail) for a module-only kind under
`--render stock`, unless the descriptor accepts the gap deliberately. Under `--render module` a function
`module_contract(kind)` derives a contract from `module/components.json` and the manifest (size 48 symbol box,
anchor `symbol-centre`, state `on`, parameter defaults from the component schema) and `view_of` returns a
pseudo path (`Module/<Name>`) that `load_contracts` resolves, so the six readers above need no change. The profile
gains `moduleKinds` for tools that write descriptors (ctig); the descriptor schema description lists the kinds. The
test page gains one section, "Module only", built from `components.json`: one symbol per enumeration value
(`variant`, `orientation`, `readoutPosition`), the alert levels and the badges, omitted under `--render stock`.

1. Stock rendering: the gap box, counted and visible; nothing is drawn from recall.
2. Cost: about 0.25 to 0.35 M tokens once (one subagent, tests in `test_hmi` for the table, the contract and the
   error), then nothing extra per element: the element's wrap adds a row to `MODULE_ONLY` in place of the library
   rows of section 2.6, which is the cheaper path for the later batches.
3. Gain: no new artwork, no solver or walk ripple, no growth of the library catalogue; the screens that name the
   kind need the module (which the owner's plan has for every OpenBridge screen).
4. Cost to the owner: a screen using such a kind cannot be built `--render stock`; the mapping file marks these
   elements "add when a screen needs them", so none does today.

#### Recommendation

Option B for the eleven electrical elements, the three specialty elements and every other element with no library kind,
built as the pilot in batch B1 together with `resistor` (a one off task of about 0.3 M tokens, first of the tranche).
`damper` and `switch` use the existing library kinds (section 2.6 only). Promote a kind to Option A later, one kind at a
time, when a stock screen needs it; the `MODULE_ONLY` row then moves to `MODULE_KIND`. Option A for the whole set would
cost more than the wraps themselves for artwork no module screen uses.

### 7.3 Batch plan, cheapest first

| Batch | Elements | Class | Library kind | Note |
|---|---|---|---|---|
| B0 | Option B (module-only kinds), with `resistor` as its pilot | Infrastructure | none | one subagent, about 0.3 M |
| B1 | damper, switch, resistor, capacitor | Static symbol | damper, switch; none for the others | `damper` has no `alternativeIcon`; the first two are section 2.6 only |
| B2 | diodes, ground, source, converter, transformer | Static symbol | none | copies of W1 |
| B3 | bipolar-transistor, mosfet, logic, router | Static symbol | none | copies of W1 |
| B4 | automation-badge, hydraulic-check-valve, valve-analog-two-way-icon, valve-analog-three-way-icon | Static symbol | none | bare glyphs: no tag, readout or alert; the wrapper adds only what the descriptor needs, or none (decide per element) |
| B5 | indicator-battery, indicator-engine, indicator-tank-atmospheric, automation-readout | Stateful device | none (readout: similar) | W2 pattern (`extra` for `on`, `tag`, `alert*`); `data` arrays for the first and third; `click` on the readout |
| B6 | heat-exchanger, heat-pump, hydraulic-separator | Stateful device | none | specialty tank base: `static`, `medium`, `click` carried as `onPress`, faceplate click kept |
| B7 | gauge-generator, gauge-motors-and-pumps, gauge-valve | Stateful device | none | 18 and 30 attributes (setpoint, priority, deadbands); the largest schemas; check the members each binds |
| B8 | hydraulic-valve-4-3, hydraulic-valve-x-2, transmitter-button, automation-input-modal | Shared control | none | Press then Confirm; `position-selected` carries a payload; the modal has no attributes and four slots |

Order of cost: B1 to B3 about 0.10 M each per element (W1 measured 0.13 M including the rediscovery this recipe
removes), B4 to B6 about 0.15 M, B7 about 0.2 M, B8 about 0.2 M each. Run G8, G11 and the browser count after each
batch (section 4.2).

### 7.4 What could block T1

1. **The automation input modal** has no attributes: its content is four slots that a Perspective property cannot
   fill. The wrapper would have to build the slotted content itself (title, preview, two actions) from new
   properties it invents, which may fail the rule that every property traces to the manifest. If the pilot finds no
   faithful way, record why and stop that wrap, as the T0 brief required.
2. **The valve and gauge elements' command semantics.** `position-selected` and the gauges' `setpoint`/`newSetpoint`
   describe a write; each needs a member and a write path of the device model that may not exist (wiki 13 section 5).
   Without one, the control is a display only; ask the owner before binding a write.
3. **Network.** Option A's icon conversion needs `raw.githubusercontent.com` (not admitted) or a local-read mode; Option B
   needs none.
4. **G11 sweep time.** About 15 minutes a sweep; a batch of stateful devices needs one.
5. **Library mappings to decide.** `automation-readout` against `readout` (the transmitter), and the valve glyphs against
   `analogvalve`: the owner or the orchestrator names the mapping before the wrap.

## 8. Adding a Module-Only Kind (built in B0)

A module-only kind is a descriptor kind with no library view (section 7.2, Option B). Batch B0 built the mechanism and wrapped
`obc-resistor` as the pilot. A later batch follows sections 2.1 to 2.5 and 2.11 (the bundle, the measured defaults, the generator entry, the
Java registration, regeneration, the module test) for each element, and replaces sections 2.6 to 2.10 by the rows below. It reads no
implementation.

1. **One row**, in `tools/hmi/screen.py`, the table `MODULE_ONLY` (kind to component id), for example `"capacitor": "cadre.ob.capacitor"`.
   The kind is the tag without `obc-`, hyphens kept (`bipolar-transistor`). Nothing else in `screen.py`, `testbench.py` or
   `glass_gates.py` changes: the contract, the pseudo view `Module/<kind>`, the drawing under `--render module`, the refusal under
   `--render stock`, the "Module only" section of the test page and the glass gates' element all follow the row.
2. **The component id** is the `type` of the `gen_module_assets.py` entry (section 2.3); the row must name a component in
   `module/components.json`, which the module test `ModuleOnlyKinds` checks. The element must have `on`, `tag`, `readoutPosition` and
   the alert properties as the filter does (a static symbol on the filter's set). An element that does not (the badge, the check valve
   and the valve glyphs of B4) is outside this mechanism as it stands: it assumes the geometry of an automation symbol (a 48 px symbol box and a readout), so such an element needs its own
   contract keys in `screen.module_contract` before its row is added; report it to the orchestrator.
3. **The module test**: copy `ResistorComponent` of `tests/test_module.py` (section 2.11) and change `ctype`, the manifest path and tag, and
   the `alternativeIcon` enumeration. Add the type to the `carried` dictionary of `DeviceProps.test_the_other_components_do_not_carry_them`.
   The mechanism tests `ModuleOnlyKinds` run over the table and need no copy.
4. **Do not add** the kind to `MODULE_KIND`, `MODULE_PARAM`, `MODULE_DROP`, `MODULE_IF_LISTED`, `KIND_VIEW`, `glass_gates.MODULE_TAGS` or
   `SYMBOL_KINDS`; the profile and `contracts.json` do not change.
5. **Verification** (section 4.1): the test page gains the kind's symbols (19 for a filter-set element); the device and symbol counts of G7
   stay 19 and 21; a stock build of a descriptor that names the kind (the page's `workspace/ctest/component-test.json` written under
   `--render module`, built with `--render stock` into a scratch directory) stops with one error for each symbol.
6. **Gateway** (section 4.2): G8 on `/component-test` shows the section "Module only" with a count of `obc-<name>` elements equal to its
   symbols and no console error.

### 8.9 A Note from B2

When a test class of `tests/test_module.py` is copied for a new element, the copy ends at the line before the next
`class ` statement; a scripted copy that ran on into `ModuleOnlyKinds` duplicated its blocks in B2.

### 8.10 A Note from B4: an Element with Another Attribute Set

`screen.module_contract` decides the geometry from the component's properties (`screen.module_geometry`): an element with `on`, `tag`
and `readoutPosition` is a symbol (section 8, as above); any other is a glyph, and nothing more is added to the code for it. A later
element with a non-filter attribute set (a gauge, an indicator) is added by sections 2.1 to 2.5 and one `MODULE_ONLY` row, and its
contract then holds exactly the properties its manifest declares, a `box` anchor, no state and the component's `defaultSize` as its
size (give the entry in `gen_module_assets.py` the size the symbol should have on a diagram). Then:

1. Parameters the component lacks (`tag`, a status word) are refused by the contract check, so a descriptor states only what exists.
2. The test page's cases come from the schema (`testbench.glyph_cases`): every enumeration value, each number at 50 and 100, each flag
   once. A state attribute that a screen would bind (a number or flag read from a tag) is added to `testbench.GALLERY_PARAMS` so the
   page reads it from a gallery memory tag (B4 added `value2` and `closed`).
3. Copy the check of `GlyphComponents` (`tests/test_module.py`, one row of `GLYPHS`) and the counts of
   `ModuleOnlyKinds.test_the_component_test_page_has_one_module_only_section_under_the_module_rendering_only`.
4. An element that needs more than a box (a state word, an alert frame, a readout) is a stateful device (section 3.2): its wrapper
   adds `extra` properties, and the geometry check stays `glyph` unless it has the three symbol properties.

### 8.11 A Note from B5: Live Attributes and a Series

1. A symbol's `bind` needs no change for a module-only kind: `embed_module` turns every `bind` entry into the tag binding of the
   component's property `props.<name>` (a glyph has no `state`, so none takes the device-state route). Read the element's `dist/`
   source, list the attributes that are live (a level, a value, a scheme chosen by state), and add a test that a symbol with a `bind`
   for each produces the binding (`ModuleOnlyKinds.LIVE`).
2. An attribute of the type `number[]` (a trend's `data`) is skipped by `schema_for` unless the entry names it in `data`
   (`"data": {"data": "numbers"}`); the kind `numbers` of `DATA_SCHEMA` and `CONVERT` carries it. The test page states such a property
   as a fixed list (a gallery memory tag holds no array); `testbench.GLYPH_SERIES` is the sample.
3. A number whose scale is not a percentage (the readout's `numberOfDigits`) takes its own values in `testbench.GLYPH_NUMBER_VALUES`.
   An attribute of the element that has the name of a symbol property (the indicators' `variant`) is allowed by the "carries none of
   the symbol's properties" test through the row's attribute set.
4. An element's click event on a module-only kind is left unwired (display only, no device kind); record it as an open item.

### 8.12 A Note from C1: Lists of Objects and Charts

1. A property that is a list of objects or strings is declared in `data` of the entry (`"data": {"data": "segments"}`); the value is the
   key of `DATA_SCHEMA` (`points`, `datasets`, `yaxes`, `labels`, `colors`, `segments`, `piesegments`, `rings`, `numbers`, `alerts`), which
   carries the item schema and the description, and `CONVERT` holds the wrapper's conversion. A new shape is one entry in each table.
   The name of the property must be the element's field, because the wrapper sets `el[name]`. A chart's series are fields without an
   attribute in the manifest, so `schema_for` never sees them: name each one in `data`, and read the element's `dist/` source for its shape.
2. The wrapper copies a list with `JSON.parse(JSON.stringify(v))` (`toRecords`) before it reaches the element: Chart.js writes to its
   arrays and the property tree holds immutable data. A symbol binds a list with `bind` like any property (a Document tag), or states a
   fixed list as a parameter.
3. An element that reads a CSS variable by name from the computed style (`getComputedStyle(el).getPropertyValue('--x')`) needs that
   variable in `cadre-ob.css`; `scoped_css` keeps a variable the bundle writes as `var(--x)` or names in a string. Check a new
   element with a stand-in page that carries `class="psc-cadre/palette/day"` on its body: a chart that draws black has lost its palette.
4. A nullable enumeration (`borderRadiusPosition`, undefined by default, where any value changes the drawing) cannot be carried: the
   contract gives an enumeration its first value as default. Leave such an attribute out with `exclude` and record why.
5. A chart's box: `testbench.glyph_cases` takes the box from the properties `width` and `height` where both exist (the line charts);
   the other charts size themselves from `fixedHeight` (320 square, wider with a legend or outer labels), and the entry gives them 480 by 320.
   `GLYPH_DATA` states a kind's sample in every case but the default, `GLYPH_EXTRA` adds named cases, and the number pairs go in
   `GLYPH_NUMBER_VALUES` (the first is the element's default).
6. In `tests/test_module.py` the manifest test compares the contract with the attributes only: a chart's fields go in `CHART_DATA` and
   its excluded attributes in `CHART_LEFT_OUT`. The page's count test serialises a list value with `json.dumps`.


### 8.13 A Note from C2: Fields Without an Attribute, a Mixed Value, and an Element That Is Only a Container

1. A boolean field that the manifest lists without an attribute (a bar's `hasScale` and `showLabels`) is added with `"properties": [...]` and
   a row of `PROPERTIES` (`type`, `default`, `description`); the default must be the element's own (true for both), or the contract changes the
   drawing. A list field (`advices`) goes in `data`; the zones of the bars (`min`, `max`) and of the radial instrument (`minValue`, `maxValue`)
   have different item shapes and so two `DATA_SCHEMA` kinds.
2. An attribute of the type `number | string` (the readout block's `value`) is mapped by `schema_for` to the types number, string and null and
   the field kind `nvalue`; the page states it through `GLYPH_DATA` (every case but the default) and `GLYPH_EXTRA` (a text case).
3. An element whose host is positioned absolutely at 100 percent (the circular progress, the radial instrument) draws as large as its box, so
   the entry's `size` is the size on a diagram; the bars draw at their own `width` or `height` and the entry's size must cover the largest
   drawing the page states (measure with a stand-in page; the bars needed 128 for the scale with thick bar, ticks and labels).
4. An element with no attribute and no data property whose rows are slotted children (`obc-alert-list`) is not wrapped: see wiki 17.22.6.

### 8.14 A Note from the Pipes (2026-11-04): Leaving an Enumeration Value Out, and a Colour the Package Does Not Define

1. An element that throws on one value of an enumeration (the overlap, end point and direction lines on `connector`) leaves it out
   with `"without": {"lineType": ["connector"]}` in its entry; `schema_for` filters the values and keeps the element's own default.
2. A shadow root rule for an element goes in `SHEETS` and is named by `"sheet"` in the entry (as the readout's); the line elements
   use it to cancel the offset with which OpenBridge hangs a drawing off a grid point. Measure the host and the drawing in
   Chromium (`getBoundingClientRect` of the host and of the shadow root's `svg`) before and after.
3. Read the computed colour of a new element in a stand-in page that carries the module stylesheet and `class="psc-cadre/palette/day"`:
   the lines read `--automation-fresh-water`, which the pinned stylesheet does not define, and drew nothing for `water` and `air`.
   `FRESH_WATER` in `gen_module_assets.py` is the model for naming a variable under the name the element reads.

## 9. Frame Components (T2, batches F1 to F5)

Batch F1 built the mechanisms (wiki 12 section 17.23); a later batch adds a frame component by the entries below and reads no
implementation. The sections 2.1 to 2.5 and 2.11 of the recipe still apply (bundle import, measured defaults, generator entry, Java
registration, regeneration, module test); sections 2.6 to 2.10 are replaced by the rows here.

1. **Bundle and defaults.** One import line in `module/web/entry.js` (the path from the manifest's `modules[].path`, `src` to
   `dist`, `.ts` to `.js`) and the tag in `TAGS` of `module/tools/measure_defaults.py`; run `npm run build` in `module/web`, then
   `python module/tools/measure_defaults.py` (additions only), then the generator.
2. **The generator entry** (`COMPONENTS` of `gen_module_assets.py`). The keys of section 2.3 plus, as the element needs:
   * `"slots": [{"slot": "icon", "kind": "icon"}, {"slot": "content", "kind": "text"}]`: a text or icon slot becomes a string
     property (`content`; `iconName`, `leadingIconName`; `text` for the default slot; `"property": "label"` renames it). The slot must be
     in the manifest. An icon slot's values are the icons of `module/web/icons.js`; to offer another icon add its import line there (the
     file name after `icon-`, checked against `dist/icons` by the generator; the package's 2,104 icons are not all bundled).
   * `"items": {"items": {"tags": ["obc-pivot-item"], "slot": ""}}`: a list of objects the wrapper builds as child elements. Every tag
     must be in the manifest. Nested tags go in `ITEM_CHILDREN` (tag to the tags it may hold; the nesting is one row for each parent,
     a group lists itself), and a field with no attribute that an item may set in `ITEM_FIELDS`. An item object is `tag`, the
     attributes by their manifest field names, `text`, `id`, `slot`, `children`. A second list for another slot is a second entry
     (`"footerItems": {"tags": [...], "slot": "footer"}`). Events from an item reach the host only if they bubble (a native `click` does, a plain `CustomEvent` does not): carry them with
     payload kind `item` (the event reports the item's `id` and `tag`) and, for a non-bubbling event, the key `itemEvents` (item 9).
   * `"types": {"variant": "ToggletipVariant"}` for an attribute whose manifest type is missing (the enumeration is read from the
     `.d.ts`); `"dts"` when a generic enumeration name (`Size`, `Variant`) is declared by several elements (the user button).
   * `"undefinedWhenEmpty": ["description"]` for an optional text whose element tests `!== undefined`.
   * `"properties": ["isClickable"]` for a field with no attribute, with a row in `PROPERTIES` (the element's own default).
   * `"events": ["primary-action"]` (the element's DOM event, declared in the manifest) with a row in `ALERT_EVENTS`
     (`dom: (component event name, payload kind, text)`; the kinds are the keys of `PAYLOAD_PROPS`: `none`, `alert`, `visible`,
     `notification`, `label`, `item`; a new kind is one entry there and one branch of `payload` in the wrapper) and, to word the text for
     one component, `"eventText": {dom: text}`. The name is never `onClick`. Nothing is wired and no event writes a tag.
   * `"describe": {"date": "..."}` rewords any property's description; `"size"` is the largest drawing the page cases make (measure).
   * Credentials never enter a property: exclude `username` and `password` of the user menu with `"exclude"`.
3. **Java** (`CadreOb.java`): one `descriptor(...)` line, with one `event("<name>", "<componentEvent>", "<text>")` for each event
   (the schema file `schemas/<name>.<componentEvent>.json` is written by the generator). The count of the gateway hook log moves.
4. **The table row** (`tools/hmi/screen.py`): one entry of `FRAME_ONLY` (kind, the tag without `obc-`, hyphens kept, to the component
   id). It is merged into `MODULE_ONLY`, so the module-only mechanism (section 8) gives the contract and the refusal under
   `--render stock`; nothing is added to `MODULE_KIND`, the profile or `contracts.json`. The kind is not a library kind.
5. **The page cases** (`tools/hmi/testbench.py`): one entry of `FRAME_SAMPLE` (`base`: parameters stated in every case, our own text;
   `extra`: named cases, with the slot properties and any combination) and, where a number needs its own values or a property must
   be left out, `GLYPH_NUMBER_VALUES` and `FRAME_SKIP`. The cases are generated from the schema (every enumeration value, each
   flag, each number) without the icon slot properties. Every slot property must appear in some case (a test checks it). A bound
   parameter name of the gallery (`GALLERY_PARAMS`: `text`, `value`, `state`...) becomes a memory tag; name a text property
   something else (the badge button's default slot text is `label`) unless a tag is wanted.
6. **Tests** (`tests/test_module.py`): one row in `FrameComponents.ROWS` (tag, manifest path, attributes, fields, slot properties,
   events), the counts of its cases in `test_the_component_test_page_shows_them_in_one_frame_section...`, and a case in
   `module/tools/harness/frame.mjs` for its slots and events (run `node module/tools/harness/frame.mjs`, see the harness README;
   `items.mjs` proves the items mechanism on a synthetic host and needs no change). The kind's tests in `ModuleOnlyKinds` skip frame
   kinds (`glyph_kinds` excludes `FRAME_ONLY`).
7. **Gateway** (section 4.2): the section "Frame components" of `/component-test` shows `obc-<name>` with the count of its cases,
   a non-zero box and no console error. G10 and G11 are not affected (no frame component is a device or a descriptor symbol).
8. **Measured facts.** A component with a boolean attribute of a custom element must be set as a property, never as markup (React 18
   writes the string); the wrapper does, and so does the items builder. A slotted icon is `obi-<name>` with the slot on it and needs
   no size. An element that draws a bubble (tooltip, toggletip) is as wide as its content unless `customWidth` states it.
9. **Parents with children (F2).** A parent's `items` entry lists the child tag; the child's own tags go in `ITEM_CHILDREN` (the alert
   menu item holds `obc-alert-icon`, which is also an `items` entry of the leaf `alertmenuitem` with `"slot": "alert-icon"`, because
   that slot takes an element, not a bundled icon). Three entry keys were added for F2: `"itemEvents": [...]` for DOM events that the
   children fire and that do not bubble (a custom element's `new CustomEvent(name)` has `bubbles` false; the wrapper then listens on
   each built child, and the generator checks the event against the child elements of `ITEM_TABLE`); `"eventKinds": {dom: kind}` to
   change one event's payload kind for one component (`ALERT_EVENTS` is keyed by the DOM name, so the same name may be `none` on a
   leaf and `item` on its parent; the row of `ALERT_EVENTS` still gives the component event name); and `"undefinedWhenEmpty"` now
   also applies to an optional enumeration (`alertType`: the schema gains the empty string, the field is `ustring`). A boolean field
   whose module default differs from the element's (`showSilenceButton` of the alert menu, hidden on purpose) is a row of
   `PROPERTIES` with the module's default and a `describe` text. Measure the size of a parent: the alert menu draws 640 by 560
   whatever its box, and a child with no width of its own (the menu row) needs a stylesheet rule that stretches it (see `devices` in
   the generator's `scoped_css`). A decorator list of a registered element can hold more than the registration (`[v("tag"),Ui()]`), so
   `FrameComponents` looks for `v("tag")` inside a list.
10. **Nested parents, objects, non-bubbling events (F3).** A parent that holds groups lists the group in `ITEM_CHILDREN` under the group's
    own tag (the navigation group holds `obc-navigation-item` and itself; so does the tree group), and the nesting is built to `ITEM_DEPTH`
    (8). Two `items` entries on one parent give two slots (`items` with `"slot": "main"`, `footerItems` with `"slot": "footer"`: a slot on
    the entry overrides the item's own). A field with no attribute that a row may set (`hasLeadingIcon`, `hasIcon`) is a row of `ITEM_FIELDS`
    and, for the standalone component, a row of `PROPERTIES` at the element's own default. Entry keys added: `"enums": {"terminalType":
    "TreeTerminalType"}` (an attribute the manifest types `string` that is an enumeration in the package), `"eventNames": {dom: name}` (the
    component's name for a shared DOM event: the menu's `click` is `onItemClick`), `"customEvents": ["click"]` (only a `CustomEvent` of the
    element counts; the native click that also reaches the host is dropped, so one press is one event) and, for an excluded container
    attribute, `"exclude": ["treeBranches"]` (the container computes `treeBranches` and `branches`). Item events (`itemEvents`) are now heard
    on every built item at any depth, and an item answers only when it is the nearest item to the event's target (a native click bubbles
    through every group above); the payload kinds `item` and `itemexpanded` name the item that heard the event (an item without an `id`
    reports an empty one). New payload kinds: `expanded` (`{expanded}`), `itemexpanded` (`{id, tag, expanded}`), `crumb` (`{label, href,
    index}`). `TreeNavigationItemAlerts` is the field kind `object` (read with `tree.read`, copied as JSON, undefined while empty, written only
    when it changes); its fields are the pinned `AlertCounts` (`countAlarm` and the others) and `combine`, not the severity names of the
    design table. A native array property with no attribute (`obc-breadcrumb.items`) is a `data` entry with a `DATA_SCHEMA` kind and a
    `CONVERT` function (`crumbs`: label and href only, because the element calls a crumb's `icon`). A row component has no width of its own:
    add its tag to the stretch rule of `scoped_css`. Measure in Chromium with the harness page (`module/tools/harness/harness.html`), where
    a menu's flyout opens outside the component box.
11. **Menus and the composite top bar (F4).** Entry keys added: `"eventFields": {dom: [(name, type, text), (name, type, text, from)]}` for an
    event of the payload kind `detail` (the kind is set in `ALERT_EVENTS`; the fields come from the entry, so the same DOM name can carry
    other fields in another component; a detail that is not an object is the value of the one field); `"writeBack": {dom: (property,
    key)}` for an element that changes its own state on a press (the wrapper writes the value of the detail key to the component's own
    property, or the element's property when the key is `"@element"`, so that an update does not set the element back); `"fixed": {field:
    value}` for fields the wrapper sets and no property carries (the user menu's `showUsername` and `showPassword`, false); `"objects":
    ["wifiState"]` for a field without an attribute whose type is a row of `STATE_OBJECTS` (a plain object, the field kind `object`); and
    `"parts": [{"tag", "slot", "fields", "events", "fixed", "defaults"}]` for a composite that renders an element of the manifest in a slot
    itself (the top bar's `obc-alert-button` in `alerts` and `obc-clock` in `clock`). A part's property schemas, types and defaults are those
    of the element's own entry in `COMPONENTS` (so that entry must exist, before the composite's), a part's `defaults` replace the element's
    default for the composite, and the property names must not collide with the host's (the generator stops). A part's events are listed in
    the host's `events` and in the part's `events` and are heard on the node (a plain `CustomEvent` does not bubble). The rows of `PROPERTIES`
    gain `showBrightness`, `showPalette` and `showLocation`; `ITEM_FIELDS` gains `showLabel` for `obc-app-button`. An icon slot's allow list
    grows by an import line in `module/web/icons.js` (seven command icons in F4). A composite or a menu that is as wide as its content gets a
    rule in `scoped_css` (`obc-top-bar` spans its box; its height is its own). A slot of the element that is misspelt in the pinned release
    (`toogle-...`) is renamed with `"property"`. A manifest event that is no event (the system menu's `eventName`, a helper's parameter) is
    left out and said so in the wiki. Measure sizes in Chromium with the harness page; a test of the harness for each property that writes
    back uses `probeStore` of `frame.mjs`, which records the writes of the store.
12. **Arrays, tabs, tri-state flags, selection (F5).** An element's own array attribute is a `data` entry (`"data": {"tabs": "tabs"}`) with a
    `DATA_SCHEMA` kind and a `CONVERT` function, as the breadcrumb's `crumbs` (item 10): the kinds added are `tabs` (the pinned `TabData` less
    `badges`, plus the module's `iconName`; its badge enumerations are filled from the package), `menuoptions`, `columngroups` and `strings`.
    A converter keeps the fields the element reads and copies them. `"tabIcons": True` (the tab row only) builds an `obi-` element in the slot
    `tab-<id>-icon` for each tab that states `iconName`. A nullable boolean in `"undefinedWhenEmpty"` is the field kind `nboolean` (schema type
    `["boolean", "null"]`, default null: unset, the element decides). An event of the kind `detail` may state a field of the type `"array"` (a list
    of texts) and a detail key with dots (`("title", "string", "...", "tab.title")`). The wrapper asks an element with `updateChildItems` (the pivot
    group) to mark its children after it builds an `items` list. A slot whose name is also a flag (`action`, `action2` of the floating item) is
    renamed with `"property"` (`actionLabel`). A `PROPERTIES` row serves any element whose manifest lists the field (`hasCancelAction`,
    `hasCloseAction`, `showTitle`, `showDescription`, `showTimestamp`). A row-like element with no width of its own (the notification menu item)
    gets a rule in `scoped_css`. A selection that the element makes itself (a tab, a pivot, an option, an opened row) is carried by `writeBack`;
    for a list the value is copied; `"@element"` takes the element's own value when the event carries nothing the key can name (the tab row after
    a close). The modal window carries text and events only (its `content` slot is a text property): it is not used for commands. All 33 frame
    components are wrapped with this batch; what each does not carry is in the wiki subsection of its batch (12, 17.23 to 17.27).
