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
   pipes and the flow solver (G6). Do not wrap them and do not add them to `MODULE_KIND`.
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
