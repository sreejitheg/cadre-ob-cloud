# Tranche T2 Report: Displays, Frame Components and the New Frames

Session of 2026-11-03, branch `spike/t0`, after the T1 report (`c5d29a8`). T2 ran on the owner's word ("Proceed with
T2") and the owner's answers to the questions of the session, and closes with the delivery documentation the owner asked
for ("the library delivered clean, with all configurations documented in a file as well as a wiki"). The record of each
step is `cloud/PROGRESS.md`; the configuration of everything delivered is `CONFIGURATION.md` and
`wiki/14-library-configuration.md`; the component list is the generated `module/CATALOGUE.md`.

## 1. Scope and Decisions

1.1 **Scope.** The 6 bars and graphs and the 6 building blocks of the pinned release; all 33 of its frame components; a
new frame built on them, in an OpenBridge variant and an ASM variant; and the gates and glass for the new frames.

1.2 **The owner's decisions for T2** (`cloud/WRAP-RECIPE.md` section 6.1, `cloud/FRAME-DESIGN.md` Owner's Answers):

1. The parent framework moves onto OpenBridge's frame components through **new frame options** beside
   `--frame openbridge` and `--frame asm`, which stay unchanged; existing projects change only when switched over.
2. **All 33 frame components** are wrapped, not only the set the current frame uses.
3. The new frame comes in **both variants** now: OpenBridge (`--frame ob`) and ASM (`--frame obasm`).
4. The new frame keeps the **Cadre crumb** with its node badges and the **Cadre alert strip** with its ACK.
5. The alert button's **silence** control is hidden until a silence function exists.
6. The displays are module-only kinds, display only, as in T1; every command control asks on press and writes on Confirm
   through the existing write paths (the rule of T1).

## 2. What Was Built

Module 0.7.0, **88 components** (44 after T1). T2 added 44 elements; one was examined and not wrapped.

| Batch | Contents | Notes |
|---|---|---|
| C1 | `area-graph`, `line-graph`, `donut-chart`, `pie-chart`, `polar-chart`, `radial-bar-chart` | Module-only glyphs; data as lists of objects; the stylesheet now keeps the CSS variables the bundle names in strings (every series drew black without them) |
| C2 | `bar-horizontal`, `bar-vertical`, `circular-progress`, `instrument-radial`, `readout-block` | Module-only glyphs; `obc-alert-list` not wrapped (its rows are slotted children and it has no data property) |
| F0 | `cloud/FRAME-DESIGN.md` | The current frames, the 33 components, the mapping, the build plan |
| F1 | `tooltip`, `toggletip`, `clock`, `user-button`, `app-button`, `notification-button`, `notification-badge-button` | The frame mechanisms: `items` (child elements from a list), text and icon slot properties (icons from an allow list checked against the pinned package), component events |
| F2 | `alert-button-item`, `alert-button`, `alert-menu-item`, `alert-menu` | First parent with `items`; item events that do not bubble; priorities mapped as wiki 13 section 11.1; silence hidden |
| F3 | `navigation-item`, `navigation-item-group`, `navigation-menu`, `tree-navigation-item`, `tree-navigation-group`, `tree-navigation`, `breadcrumb` | Nesting to any depth; per-row alarm count objects (measured on the gateway) |
| F4 | `brilliance-menu`, `user-menu`, `system-menu`, `app-menu`, `command-menu`, `top-bar` | Credentials excluded from every property; the top bar composes its own alert button and clock; 48 px high |
| F5 | `tab-item`, `tab-row`, `pivot-item`, `pivot-item-group`, `modal-window`, `context-menu-input`, the three notification items | Array attributes; the modal window is not used for commands |
| F6a | `--frame ob` | Head: the module top bar (48 px) over a 36 px strip with the Cadre crumb and the alert message; navigation, alert, user and brilliance menus on the module components, every event wired to the existing script |
| F6b | `--frame obasm` | Head of 132 px: the top bar, the crumb with search and the alert strip, and the page header on the pivot and tab row; the hierarchy on the tree navigation with its counts; the support list on the navigation menu; Cadre crumb popup, banner and floating faceplates kept |
| F7 | Glass and gates | `glass.frame_variant` tells the four frames apart by the top dock; variants of every frame helper, of G10 F6 to F21 and of the glass gates; the old frames' selectors held by tests |
| F8 | G10 and the walk on the new frames | Two glass fixes (section 5.1 items 5 and 6); the frames needed no change |
| Docs | `CONFIGURATION.md`, `module/CATALOGUE.md` (generated), `wiki/14`, GF-99 to GF-114 | The owner's delivery request |

What a frame component cannot carry (free slot content, icon template functions, the user menu's credential fields, the
system menu's battery slot, the navigation menu's logo) is recorded per component in `module/CATALOGUE.md` and wiki 12
sections 17.23 to 17.27.

## 3. Cost

Each step ran in one Sonnet 5.5 subagent at medium effort; tokens are the Agent tool's totals.

| Step | Contents | Tokens | Tool calls | Minutes |
|---|---|---|---|---|
| C1 | 6 charts | 241,237 | 107 | 17 |
| C2 | 5 blocks (1 examined) | 210,088 | 76 | 17 |
| F0 | Frame design | 159,726 | 23 | 3 |
| F1 | 7 leaves and the mechanisms | 303,036 | 93 | 20 |
| F2 | 4 alert components | 204,259 | 67 | 13 |
| F3 | 7 navigation components | 248,658 | 71 | 17 |
| F4 | 6 menus and the top bar | 347,175 | 119 | 33 |
| F5 | 9 components | 333,976 | 126 | 44 |
| F6a | `--frame ob` | 295,458 | 80 | 21 |
| F6b | `--frame obasm` | 263,501 | 77 | 28 |
| F7 | Glass and gate variants | 364,709 | 133 | 45 |
| F8 | G10 and the walk on the new frames | 137,116 | 46 | 80 |
| Docs | Configuration file, catalogue, wiki | 301,005 | 72 | 22 |
| A-02 | Diagnosis and fix of the intermittent walk row | 190,435 | 105 | 119 |
| Total | | 3,600,379 | 1,195 | about 8 h |

The T1 report estimated T2 at 3 to 5 million tokens, and the frame design (F0) at about 3.3 million before the owner
asked for the ASM variant as well; the subagents spent 3.6 million, and the main session's orchestration, joint builds,
gateway checks and diagnosis add an estimated 0.5 million by the same measure. Wall time was about 12 hours (07:20 to
19:40 UTC), with the gate runs overlapping the batches; the final runs alone took about 4 hours. The owner reads the billed figure from the
account's usage page.

## 4. Gates

### 4.1 Offline

The full suite passes: 1318 tests (1191 after T1). G0 to G7 pass on the component test page after every batch (19
devices, 21 device symbols) and on the samples of all four frames. A stock build of a module-only kind, and any build with
`--frame ob` or `--frame obasm` without `--render module`, is refused with an error, as decided.

### 4.2 On the Gateway During T2

Each batch was checked on a test build installed from a clean worktree of its commit (0.6.1 to 0.6.6): G8 on the
component test page passed every time (5160 to 6068 components, no overlay or error badge), and every wrapped element
was found and drawn with a size (counts in `cloud/PROGRESS.md`). These checks found and fixed: the radial instrument
drawn at 0 by 0 (now fills its box), the loading badges of the larger page read as error badges (G8 now waits for them),
the sweep starting on an unsettled page, and the sweep clicking animated frame components (section 5.1).

### 4.3 The Final Run, Module 0.7.0

| Check | Outcome |
|---|---|
| Install | "Registered 88 Cadre OpenBridge components", script 2,753,602 bytes |
| The full suite, four projects | 123 min, the code of `068b48a`; the trial reset once by the suite |
| `cadre_hmi_wtp` (`openbridge`, stock) | PASS: G8 6 of 6 routes, G11 44 of 44, G10 17 of 17 signed in, the walk in every group, the plant restored |
| `cadre_hmi_wtpob` (`openbridge`, module) | G8 6 of 6, G11 44 of 44, G10 21 of 21 signed in; the walk in every group but A-02, an intermittent glass defect then fixed (5.1 item 7) and proved by three full walks in a row passing every group |
| `cadre_hmi_wtpobf` (`ob`) | PASS: G8 6 of 6, G11 44 of 44, G10 21 of 21 signed in, the walk in every group, the plant restored |
| `cadre_hmi_wtpoba` (`obasm`) | PASS: G8 6 of 6, G11 44 of 44, G10 21 of 21 signed in, the walk in every group, the plant restored |
| G11 on `/component-test` | PASS on a fresh run after the fixes of 5.1 items 4 and 8: 21 of 21 devices, 274 leaves, nothing missing or unexpected, no fault (62 min) |

## 5. Findings

### 5.1 Fixed

1. **Chart colours**: `scoped_css` dropped the CSS variables the bundle names in strings; every series drew black (C1).
2. **The radial instrument** drew at 0 by 0, centred in its box; it now fills the box (gateway check of C2).
3. **G8 read loading badges as errors** on the larger test page (82 after 6 s, none after 26 s); `capture.settle_badges`
   waits for them, at most 60 s, and a badge that stays still fails.
4. **G11 swept animated non-device components**: the frame components and glyphs open no faceplate and some animate,
   so the leaf count moved under the sweep's guard; the sweep now clicks only the module components that draw a device
   (`faceplates.DEVICE_COMPONENTS`, held to `screen.MODULE_KIND`).
5. **The new alert menu's rows were pressed by their text**, which the element keeps in a shadow root with no size, so
   the menu stayed open over the faceplate dock (G10 on `ob`); `glass.click_alert_row` presses the row's body.
6. **The ASM variant's Trends and Alerts pages** are in the support list, not the tree; the walk now opens it
   (`glass.open_support_list`).
7. **Walk row A-02 was intermittent on the old frame's module rendering** (2 passes, 5 failures over all runs): the
   module alert panel draws its own toolbar over the bottom of its list, and the second row's ACK sometimes lay under
   it, so the press hit the toolbar. The glass now scrolls the row clear before pressing and refuses a covered cell;
   three full walks in a row passed after the fix.
8. **The instrument field's identity in G11** (open since T0): the sweep expected an instrument's faceplate under its
   tag else its identifier, while the library titles it by its tag else its label (`library.SELECT_INSTRUMENT`); the
   sweep now follows the library's rule (`faceplates.faceplate_title`).

### 5.2 Open, for the Owner's Review

1. **The bundle**: 2.75 MB at 0.7.0 (0.99 MB at 0.4.3, 1.95 MB at 0.6.0), loaded in every Perspective session of the
   gateway. Splitting it, or loading the frame components and module-only kinds only where a project uses them, would
   bound the cost; not measured on a page.
2. **Cosmetic, visible on the gateway**: the `obasm` page title runs into the first tab ("Plant OverviewMimic"); the
   toggletips float over the row above them on the test page; the charts draw in greys (the palette's data colours or a
   missing colour scheme: for a visual review); the gauges of T1 still overflow their unmeasured box.
3. **Departures recorded in `cloud/FRAME-DESIGN.md`**: the alert strip lies beneath the top bar, not beside it; the
   `obasm` head is 132 px; a row's ACK in the new alert menu acts at once as the module panel does, while Ack all keeps
   its Confirm; a tree group press only toggles, so a node's first page is one press further.
4. **For an operator**: the module alert panel's own toolbar covers the second row's ACK until the list is scrolled
   (OpenBridge's layout, found by the A-02 diagnosis, unchanged).
5. **Not wrapped**: `obc-alert-list` (slotted rows), `obc-automation-input-modal` (T1), and the nine line elements (the
   owner's decision of T1).
6. **The glass gates that write** (alarm, ack, banner, search and zoom with a raised alarm) need an ASM sample with an
   ASM model, which the cloud copy does not have; F7 measured the read-only ASM gates on `obasm` (menus, panels, search
   and zoom pass).
7. **GF numbering**: GF-99 to GF-114 may collide with numbers the source has used since `d9f8655`; renumber at merge.

## 6. The Merge Back

The T2 range is `c5d29a8..` the commit of this report on `spike/t0` (the T0 and T1 ranges are in their reports). Its
mirrored paths, besides `cloud/`:

| Path | Reason |
|---|---|
| `CONFIGURATION.md`, `wiki/14-library-configuration.md`, `wiki/index.md` | The delivery documentation |
| `wiki/04-navigation-and-frame.md` | Sections 10 and 11: the two new frames |
| `wiki/07-gateway-facts.md` | GF-99 to GF-114 |
| `wiki/12-module-spike.md` | Subsections 17.21 to 17.27 |
| `wiki/13-faceplates-alarm-lists-interlocks.md` | Section 11.1 (alert type mapping), 13.11 (the glass variants) |
| `tools/hmi/obframe.py`, `tools/hmi/obasm.py` (new), `tools/hmi/navigation.py`, `tools/hmi/navigation_scripts.py`, `tools/hmi/parent.py`, `tools/hmi/screen.py`, `tools/hmi/testbench.py` | The new frames, the frame-only table, the test page sections |
| `tools/compare/glass.py`, `functional.py`, `glass_gates.py`, `capture.py`, `faceplates.py`, `wtp_suite.py` | Frame variants, settle waits, the device-only sweep, the samples of the new frames |
| `module/tools/gen_module_assets.py`, `module/tools/measure_defaults.py`, `module/web/entry.js`, `module/web/icons.js` (new), `module/common/src/main/java/cadre/hmi/ob/common/CadreOb.java`, `module/build.gradle.kts` | The 44 components, the frame mechanisms, version 0.7.0 |
| `module/tools/gen_catalogue.py` (new), `module/tools/harness/` (`frame.mjs`, `items.mjs`, `items_bundle.py`, README) | The catalogue generator and the browser harness of the frame components |
| `tests/test_module.py`, `tests/test_walk.py`, `tests/test_faceplates_scroll.py`, `tests/test_ob_frame.py`, `tests/test_obasm_frame.py`, `tests/test_capture_settle.py`, `tests/test_catalogue.py` | Tests of the above |

Generated, to be regenerated at the source rather than merged: `module/components.json`, `module/web/defaults.json`, the
131 new schema files under `module/common/src/main/resources/schemas/`, `module/gateway/src/main/resources/mounted/`,
`library/contracts.json`, `build/cadre_hmi_base` (the new `Framework/OB` and `Framework/OBASM` views) and
`module/CATALOGUE.md`. Regenerate as `CONFIGURATION.md` section 10 describes, then run the full suite (1318 in the cloud).
