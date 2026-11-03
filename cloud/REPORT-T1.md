# Tranche T1 Report: the Automation Set

Session of 2026-11-03, branch `spike/t0`, after the T0 report (`cc652a9`). T1 ran on the owner's word of the same day
("fix the glass.button defect and run G10, then build the whole library") and the owner's answers to the questions
of the session. It stops here for the owner's review before T2. The record of each step is `cloud/PROGRESS.md`.

## 1. Scope and Decisions

1.1 **G10 first.** The `glass.button` defect of the T0 report was fixed and G10 run before any wrap (section 4).

1.2 **The owner's decisions for T1**, recorded in `cloud/WRAP-RECIPE.md` section 6:

1. A wrap recipe first, then T1 in batches, with a review before T2.
2. The nine OpenBridge line elements (`bus` and the eight `*-line` elements) are skipped: they overlap the library's
   pipes and the flow solver (G6).
3. Every command control asks on press and writes on Confirm, through the existing write paths with the
   `Administrator` check (the rule of W3).
4. An element without a library kind becomes a **module-only kind**: its contract comes from `module/components.json`,
   the component test page shows it in a "Module only" section, and a stock build refuses it with an error.
5. Elements whose events or properties imply a write are wrapped for display and state only; the writes are open
   items.

## 2. What Was Built

Module 0.6.0, 44 components (11 before T0, 14 after T0). T1 added 30 elements; one was examined and not wrapped.

| Batch | Elements | Form | Library kind |
|---|---|---|---|
| B0 | The module-only mechanism (`screen.MODULE_ONLY`, `module_contract`, the stock refusal, the test page section); `resistor` | Symbol on the filter's base | None |
| B1 | `damper`, `switch`; `capacitor` | Symbol | `damper`, `switch` exist (mapped like the filter); `capacitor` none |
| B2 | `diodes`, `ground`, `source`, `converter`, `transformer` | Symbol | None |
| B3 | `bipolar-transistor`, `mosfet`, `logic`, `router` | Symbol | None |
| B4 | `automation-badge`, `hydraulic-check-valve`, `valve-analog-two-way-icon`, `valve-analog-three-way-icon`; the glyph form of `module_contract` | Glyph | None |
| B5 | `indicator-battery`, `indicator-engine`, `indicator-tank-atmospheric`, `automation-readout`; data kind `numbers` | Glyph | None |
| B6 and B7 | `heat-exchanger`, `heat-pump`, `hydraulic-separator`; `gauge-generator`, `gauge-motors-and-pumps`, `gauge-valve` | Glyph | None |
| B8 | `hydraulic-valve-4-3`, `hydraulic-valve-x-2`, `transmitter-button` | Glyph | None |
| Not wrapped | `automation-input-modal`: four bare slots and no attribute; a property cannot fill a slot, so it needs a container component | | |

A symbol carries the filter's set (`on`, the identifier, the status word, the readout position, the alert frame,
badges); a glyph carries exactly the properties its manifest declares, with no invented state or frame. Live values
of the module-only kinds bind through a descriptor's `bind`, as for the other module components.

## 3. Cost

Each batch ran in one Sonnet 5.5 subagent at medium effort, from the recipe; tokens are the Agent tool's totals.

| Step | Elements | Tokens | Tool calls | Minutes | Tokens per element |
|---|---|---|---|---|---|
| Recipe and survey | | 179,845 | 33 | 4.5 | |
| B0 | 1 and the mechanism | 168,997 | 45 | 12.4 | |
| B1 | 3 | 152,614 | 42 | 19.7 | 51,000 |
| B2 | 5 | 106,413 | 31 | 6.3 | 21,000 |
| B3 | 4 | 87,753 | 16 | 5.2 | 22,000 |
| B4 | 4 and the glyph form | 167,231 | 44 | 8.4 | 42,000 |
| B5 | 4 | 160,169 | 42 | 8.0 | 40,000 |
| B6 and B7 | 6 | 171,593 | 59 | 9.1 | 29,000 |
| B8 | 3 (and 1 examined) | 135,942 | 37 | 7.5 | 45,000 |
| Total | 30 | 1,330,557 | 349 | 81.1 | 44,000 with the recipe |

The T0 report estimated T1 at 6.5 to 8.3 million tokens and 8 to 12 hours. It cost 1.33 million subagent tokens and
81 minutes of subagent time; with the main session's orchestration, the joint builds and the gateway gates (an
estimated 0.4 million tokens by the same measure, most of it waiting on gates and the diagnosis of section 5), T1 is
about 1.7 million tokens and about 3 hours of wall time. Three things made the difference: the recipe (no subagent
re-read the generator to find the pattern), the module-only kinds (no library view, contract or icon per element),
and display only (no write path per element). The owner reads the billed figure from the account's usage page.

## 4. Gates

### 4.1 Offline

The full suite passes: 1191 tests (1102 after T0, 1104 after the G10 fixes). G0 to G7 pass on the component test page
after every batch (19 devices, 21 device symbols). A stock build of the page descriptor stops with one "module only"
error per module-only symbol (515 at the end of B7), as decided.

### 4.2 On the Gateway, Module 0.6.0

| Check | Outcome |
|---|---|
| Install | REST, restart about 15 s, no commissioning step for an upgrade, "Registered 44 Cadre OpenBridge components", script 1,954,229 bytes |
| Deploy | `cadre_hmi_base_asm`, `cadre_hmi_ctest` (2052 tags), `cadre_hmi_wtp` and `cadre_hmi_wtpob`, all G0 to G7 clean |
| G8 `/component-test` | PASS, 4444 components, no quality overlay, no error badge |
| Elements drawn | All 33 wrapped elements found and drawn with a size, no console error: filter 12, generator 12, button 1, resistor 19, damper 13, switch 17, capacitor 19, diodes 19, ground 19, source 19, converter 19, transformer 19, bipolar transistor 19, MOSFET 19, logic 19, router 19, badge 23, check valve 2, two-way glyph 5, three-way glyph 7, battery 11, engine 6, atmospheric tank 11, automation readout 10, heat exchanger 44, heat pump 44, hydraulic separator 44, generator gauge 37, motor and pump gauge 38, valve gauge 26, hydraulic valve 4/3 10, hydraulic valve x/2 8, transmitter button 22 |
| G11 `/component-test` | 21 of 21 devices, 831 leaf views, no fault (`--faceplate asm`, about 70 min); FAIL only on the instrument field identity carried from T0 (5.2 item 7). The first attempt stopped at once on an unsettled page (5.1 item 6) |
| `wtp_suite.py`, both renderings | SUITE PASS (50 min): stock G8 6 of 6 routes, G11 44 of 44, G10 17 of 17, the walk PASS in every group; module G8 6 of 6, G11 44 of 44, G10 21 of 21, the walk PASS in every group (A-02 included); the plant restored with no difference |

On module 0.5.0 (after B1): G11 21 of 21 devices, 314 leaf views, no fault (the damper device and the five alarm
lamps included); the only finding the instrument field identity carried from T0.

## 5. Findings

### 5.1 G10 and the Walk

1. **`glass.button`** (T0 report 2.4 item 1): fixed; a page is its own page. A test reproduces the error.
2. **The top bar's alarm button** was found by a stale component path (`T[0].0:5`, now the alert message); the
   alarm menu never opened (F16, F21, F11, F14, A-01, A-02). Fixed (`T[0].0:6`) and held to `framework.top_bar` by a
   test.
3. **No history provider** on the fresh gateway (environmental): `Sample_SQLite_Database`, which the tag model names,
   created as an SQLite connection and an SQL historian of our own configuration; now part of `setup.sh gateway`.
4. **The walk could not read a module filter** (C-10): `walk_plan.MODULE_PROP` had no row for the filter (W1) or
   the switch (B1). Fixed, and a test holds every kind of `MODULE_KIND` to a row.
5. With 1 to 4: G10 PASS 17 of 17 (stock) and 21 of 21 (module), signed in, and the walk PASS in every group on both
   renderings in the full suite on 0.6.0 (5.2 item 1).
6. **The faceplate sweep started on an unsettled page.** The component test page of 0.6.0 (830 leaves) still sized an
   element after the load and the fixed wait, and the sweep's guard took that for a change made by its first click.
   `faceplates.settled_points` now waits for a still count before the sweep; the guard itself is unchanged (tests
   added).

### 5.2 Open

1. **Walk row A-02 on the module rendering depends on the order of the runs.** Acknowledging TK-101's high level
   alarm from the alarm menu passed inside the full suite on 0.4.4 and on 0.6.0, and failed in four runs of the walk
   alone on 0.5.0 (one from a clean alarm state, one with the walk tools of the passing commit). The generated project
   was byte-identical throughout. The suite runs G8, G11 and G10 before the walk; the walk alone does not. Not
   diagnosed; to be watched in T2's regressions.
2. **The gauges overflow their boxes.** Their 240 by 280 box is not measured (B7); on the page the lower part of a
   gauge (the setpoint row) runs under the next section. G5 checks boxes, not drawings, so it cannot see it. The fix
   is a measurement of the element's size, as `measure_instruments.py` did for the instruments.
3. **Deferred writes** (decision 1.2 item 5): the hydraulic valves' `position-selected`, the gauges' setpoints, the
   `click` of the heat exchanger, heat pump, hydraulic separator, automation readout and transmitter button. Each is
   recorded with its later wiring in wiki 12 sections 17.18 to 17.20.
4. **The automation readout overlaps the `readout` kind** (`obc-transmitter`); recorded for the owner (wiki 12
   17.18).
5. **The input modal** needs a container component (section 2).
6. **The nine line elements** wait for a design decision on the pipes (decision 1.2 item 2).
7. **The instrument field's faceplate identity** (T0 report 2.4 item 3) remains.
8. **The bundle doubled**: the module's script is 1.95 MB (0.99 MB at 0.4.3), and a module's browser resources load
   in every Perspective session of the gateway (wiki 12 section 7.4). Splitting the bundle by element, or loading the
   module-only kinds on demand, would bound the cost; not measured on a page.
9. **The component test page is large**: 4444 components, 831 leaves and 2052 tags; a G11 sweep now takes about 70
   minutes, since it clicks every leaf. The module-only gallery could move to a page of its own, swept by G8 only.
10. **The worker restart of the session stops background processes**: the Docker daemon and a running suite stopped
    once. `setup.sh` now starts `dockerd` in its own session, and long gate runs were started the same way.

## 6. T2 Re-estimated

T2 as the T0 report took it: the 6 bars and graphs and the 6 building blocks (stateful displays, several with data
arrays, which B5's `numbers` kind already carries), about 20 frame components (controls with events), and the move of
the parent framework onto them. At T1's measured rate, the 12 displays cost about 0.5 to 0.7 million tokens. The frame
components are the expensive part: they carry events and must replace parts of the generated frame (`framework.py`)
without breaking G10, so they are closer to W3 (0.19 million) than to a glyph, about 2 to 4 million with the framework
move. With orchestration and gates, T2 is estimated at 3 to 5 million tokens and 6 to 10 hours, against 8 to 10 million
in the T0 report. The framework move needs its own brief and the owner's decisions on which frame parts change.

## 7. The Merge Back

The T1 range is `cc652a9..ac509f9` on `spike/t0` (plus the commit of this report). Mirrored paths changed:

| Path | Reason |
|---|---|
| `tools/compare/glass.py` | `button` on a page; `BELL` at the generated top bar's index |
| `tools/compare/walk_plan.py` | Walk rows of the filter and the switch |
| `tools/compare/glass_gates.py` | Module tags of the new elements |
| `tools/hmi/screen.py` | `MODULE_ONLY`, `module_contract` (symbol and glyph forms), the stock refusal, the faceplate kind of a module symbol, the tables of the damper and the switch |
| `tools/hmi/testbench.py` | The "Module only" section and its cases |
| `module/web/entry.js`, `module/tools/measure_defaults.py`, `module/tools/gen_module_assets.py`, `module/common/src/main/java/cadre/hmi/ob/common/CadreOb.java` | The 30 elements; the data kind `numbers`; nullable numeric defaults |
| `module/web/defaults.json` | Measured defaults (additions only) |
| `module/build.gradle.kts` | Version 0.6.0 and description |
| `tests/test_module.py`, `tests/test_hmi.py`, `tests/test_walk.py`, `tests/test_testbench.py`, `tests/test_glass_gates_plan.py` | Tests of the above |
| `wiki/12-module-spike.md` | Subsections 17.13 to 17.20 |

Generated, to be regenerated at the source rather than merged: `module/components.json`, the 30 new schemas under
`module/common/src/main/resources/schemas/`, `module/gateway/src/main/resources/mounted/` (script, stylesheet and
legal notes) and `library/profile.json`. Regenerate as the T0 report's section 5.2 describes, then run the full suite
(1191 in the cloud).
