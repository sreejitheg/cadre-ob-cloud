---
title: Water treatment sample project
type: wiki
updated: 2026-10-09
---
# 11 Water Treatment Sample Project

| Field | Value |
|---|---|
| Document ID | COB-WIKI-11 |
| Revision | B |
| Status | Issued for use |
| Project | `cadre_hmi_wtp`, a child of `cadre_hmi_base`, on `Ignition-PCS_DEV_Station`; tags under `[default]cadre_hmi_wtp` |
| Code | `tools/plants/wtp.py` (the plant), `screens/wtp/` (its generated descriptors and tag model), `tools/compare/functional.py` (G10), `tools/compare/faceplates.py` (G11) |

## 1. Purpose

This page records a test of the parent library on a process plant: a small village water
treatment plant, built as a child project of `cadre_hmi_base` over a simulated process. The
question was how good a project the library supports, not how much of a plant it covers. The
measure is a project that is clean (no broken layout, page or binding) and functional (an
operator can run the plant from it). The owner's reference screens informed the process train
only; none was recreated.

## 2. Plant Definition

The plant is defined once, in Python (`tools/plants/wtp.py`). Running it writes the
tag model (`screens/wtp/tags.json`: 33 device folders with 150 tags, 7 interlock folders with 65 more, and the
simulation's `sim` folder with its `reset` member; 258 nodes with the root folder) and the four screen descriptors, so
screens and tags cannot drift apart. The generator and the parent library do the rest: no view is
written by hand, and every component is a stock Perspective component.

Table 1. Pages.

| Route | Page | Layout | Content |
|---|---|---|---|
| `/` | Plant Overview | Cards | Production (raw water, filtered water and distribution flows), Water quality (raw and filtered turbidity, free chlorine, pH), Storage (TK-101, TK-202, TK-501), Pumps (P-101, P-301, P-501, P-502). The Production and Water quality titles open their pages |
| `/intake` | Intake and Clarification | Diagram, 1580 x 600 px | Inlet valve XV-101, raw water tank TK-101, feed pump P-101, FIT-101 and AIT-101; coagulant dosing pump DP-201 and tank TK-201; flash mixer M-201; clarifier CL-201; clarified water tank TK-202; sludge pump P-202 |
| `/filtration` | Filtration | Diagram, 1580 x 600 px | Filter feed pump P-301 and PIT-301; media filters F-301 to F-303 with inlet valves XV-301 to XV-303 and DPIT-301 to DPIT-303; FIT-301 and AIT-301 |
| `/disinfection` | Disinfection and Storage | Diagram, 1580 x 600 px | Hypochlorite dosing pump DP-401 and tank TK-401; caustic dosing pump DP-402 and tank TK-402; potable water tank TK-501 with AIT-401 and AIT-402; distribution pumps P-501 and P-502; FIT-501 |
| `/trends` | Trends | Parent page, built by the generator | One trend card per historised member: the 11 instruments' values and the 6 tanks' levels (page 13 section 8 rule 6) |
| `/alerts` | Alerts | Parent page | The plant's active alarms (section 4) |

Each diagram carries three titled sections, text labels for the plant's inlets and outlets, and
routed pipes (12, 12 and 13). The navigation menu lists the four pages, with the alerts page in its
footer.

## 3. Simulated Process

Every value is a plain tag: there is no gateway script and no simulator device (GF-16 to GF-19).

Table 2. Simulation.

| Behaviour | Construction |
|---|---|
| Command feedback | Each device folder holds `cmd` and `mode` as memory tags; `state` is an expression on `cmd`, or in Auto on the automatic rule; a motorised device's `state` is also false while its `fault` is true |
| Speed | A motorised device runs at its `speedSp` while running, otherwise at 0 |
| Tank level | A self-referencing expression integrates inflow minus outflow once a second, clamped to 0 to 100 per cent; `volume` and `trend` follow from it |
| Automatic modes | A dead band on a level: XV-101 opens below 50 and closes above 80 per cent of TK-101; P-301 runs above 30 and stops below 15 per cent of TK-202; P-502 runs above 85 and stops below 60 per cent of TK-501 |
| Flows and pressures | Follow the pump speeds and valve states, with a slow sine variation |
| Water quality | Analysers hold normal values while their dosing runs and drift out of range when it stops: filtered turbidity above 1.0 NTU without coagulant, free chlorine below 0.5 mg/L without hypochlorite, pH below 6.8 without caustic |
| Alarms | Tag alarms: Fault (High) on every motorised device; High level (Medium) and Low level (High) on every tank; High turbidity (High), Low free chlorine (High) and Low pH (Medium) on the analysers. Each limit is a member of the device folder (`hiLimit`, `loLimit`) to which its alarm's setpoint is bound (GF-39), so a limit written from the faceplate moves the alarm. Each symbol's alert frame follows its fault alarm's active and acknowledged state through expression tags (GF-17) |
| Demonstration fault | P-502 starts faulted, so the alarm chain shows at once: flashing frame, top bar, acknowledge, Reset fault; its trip on the fault latches, so it restarts only after the Interlocks tab's Reset (COBD-023) |
| History | The 17 analogue members (analyser, flow and pressure values; tank levels) are historised on `Sample_SQLite_Database` since 2026-10-08 (COB-064) |
| Interlocks | P-101 (a permissive on TK-101's level, a trip on TK-202's level), P-301 (a permissive: a filter inlet valve open) and P-502 (a trip on its own fault) carry the provisional contract of page 13 section 7; a held device does not start, a tripped one stops, and a trip latches until reset |

Every cross reference carries a `coalesce` default, without which start up spreads null through
the cycles of the model (GF-19).

An import of the tag model returns every memory member to its configured value, but a
self-referencing expression tag (a tank level, an automatic dead band) keeps the value it holds
(GF-42). The members that hold plant state (tank levels, the automatic dead bands, the interlock
latch times) therefore obey `sim/reset`: while it is true, each returns to its initial value. A running
pump's own `state` also refers to itself (it holds a start, GF-16), but it follows its command and
interlocks and settles in the initial state without the reset. A restore of the plant imports the model with `sim/reset` true, waits three
seconds, then imports it as tracked (`restore_plant` in `tools/compare/wtp_suite.py`).

## 4. Operator Functions

All of these come from the parent; the child adds only its pages.

1. **Navigation.** The navigation menu and the card titles open pages.
2. **Device selection.** A symbol or a tank opens the faceplate dock with the device identifier and
   description. The pump faceplate (pumps, motors, fans) shows state, control mode, fault and speed
   and offers Start and Stop, Auto, Manual and Local, a speed setpoint, Reset fault and the device's
   alarms; the valve faceplate the state, mode and commands; the tank faceplate the level, the high
   and low limits with their state, and the alarms. Since 2026-10-08 every faceplate has a tab
   row (page 13 section 2), and a readout or an instrument field opens the instrument faceplate:
   the value, the alarm limits as setpoints, a trend of the last 1 or 8 hours, and the alarms
   (page 13 section 8).
3. **Alarms.** The top bar shows the most severe active alarm and the counts, and ACK acknowledges
   it; the alerts page lists every active alarm. Both are scoped to the plant by
   `session.custom.alarmScope` (GF-20).
4. **Signing in.** Every command, setpoint, limit, reset, bypass and acknowledgement needs the
   gateway's admin role (COB-063, COBD-024); the user menu signs in through the identity provider
   `default`. With nobody signed in the plant can be viewed but not operated.
5. **Display.** Day, dusk, night and bright palettes; on diagrams, colour mode, identifier tags and
   readouts.

## 5. Verification

Table 3. Gates and results, 2026-10-07.

| Gate | Result |
|---|---|
| G0 to G7, offline | Pass on all four descriptors; registry 0 errors |
| G8 render | 5 of 5 routes: 0 view error badges, 0 binding quality overlays; 287, 309, 282, 264 and 55 components |
| G9 live flow | Not applicable: the gate members are expression tags, and writing them would overwrite the model. Flow is proven by G6 offline and by check F3 on the glass |
| G10 functional | 9 of 9 checks (Table 4) |
| G11 faceplate sweep | 26 of 26 devices open their faceplate with their identifier as title; 0 overlays; no empty faceplate |

Table 4. The functional walk (G10), an operator's actions in a new session.

| Check | Action | Expected and observed |
|---|---|---|
| F1 | Click the Production card title | The intake page opens |
| F2 | Click P-101 | The faceplate shows P-101 and "Raw water feed pump" |
| F3 | Stop | P-101 reads Off, FIT-101 falls to 0.0, the pipe it fed runs empty |
| F4 | Start | P-101 runs at its 80 per cent setpoint |
| F5 | Type 60 in the speed setpoint | P-101 runs at 60 per cent |
| F6 | Open the navigation menu, choose Filtration | The filtration page opens |
| F7 | ACK in the top bar on the faulted P-502 | Its frame stops flashing and stays visible |
| F8 | Reset fault on P-502 | The frame disappears |
| F9 | Choose Night in the brilliance menu | The session switches to the night palette |
| F10 | Module rendering: open P-502's Alarms tab and click the action cell of its fault's row | The tab is display only (COBD-025): the fault is listed with OpenBridge's no-acknowledgement icon and no ACK; after the click the alarm is still unacknowledged and the frame still flashes |
| F11 | Module rendering: ACK one alarm in the top bar's alarm menu, then click P-502's row | One alarm fewer unacknowledged; P-502's faceplate opens |
| F12 | P-301 to Manual and Stop; close XV-301 and XV-302 from their faceplates; press Start on P-301. Then, after a restore: ACK in the top bar; P-502 to Manual; Reset fault; Start; the Interlocks tab's Reset; Start | "Start not permitted: 1 condition not met", "Interlocks (1)" with the row not met (live Closed, required Open), the interlock badge on P-301; Start refused, P-301 stays off. P-502: "Interlocked: reset required" once its fault clears, "Interlocks (1)" with the row "Latched", Start refused; after Reset the tab reads "Interlocks" and Start runs the pump |
| F13 | Click AIT-301's readout; type 0.05 in its high limit; acknowledge the alarm (stock rendering: in the faceplate's Alarms tab; module rendering: ACK on its row in the top bar's alarm menu, then the row); open the Trend tab; restore the plant | The instrument faceplate opens with "Filtered water turbidity" and the high limit; the Alarms label counts one alarm more; the alarm is acknowledged; the trend draws a line of history, with at most five time labels in 24 hour form and the limit dashed; after the restore the label is back to its count before, so no cleared, unacknowledged alarm is left |
| F14 | Module rendering: with P-502 faulted and unacknowledged, open the top bar's alarm menu and press ACK visible | Every alarm the menu shows is acknowledged; P-502's frame turns steady |
| F15 | Nobody signed in: open P-101's faceplate; read its controls; a crafted click on the disabled Stop | Start, Stop, the modes, the setpoint, Bypass are disabled; P-101 keeps running (COBD-024) |
| F16 | Nobody signed in: the top bar's ACK, the alerts page's table, under module rendering the alarm menu | ACK disabled; the table offers no Acknowledge; the menu shows no ACK and ACK visible is disabled; P-502's alarm unchanged |
| F17 | Sign in with the test login of NEEDS N-COB-9 through the top bar's user menu; open P-101 | Signed in; Start enabled. F3 to F14 then run in this session |
| F18 | Module rendering, signed in: F11's acknowledgement | The alarm is acknowledged by the signed in user (compared, never printed) |
| F19 | Open the trend page; press 8 h; click the first card's title | 17 cards, each drawing its line with 24 hour time labels; the range widens; the device's faceplate opens |

The same G8 and G11 gates pass on the two other children of the parent: the pump station sample
(1 route, 5 of 5 devices) and the rebuilt vendor demo (2 routes, 31 of 31 devices).

## 6. Defects Found and Fixed

Table 5. Defects found while building the sample. Each was fixed in the generator, the library or
the plant definition; no view was edited by hand.

| Defect | Found by | Fix |
|---|---|---|
| Null values and quality overlays along cycles of expression tags | Screenshot review; G8 did not count overlays then | `coalesce` defaults (GF-19); G8 now counts `.ia_qualityOverlay` and fails on any |
| Card symbols carrying a `label` drawn as text | Screenshot review | The generator recognises a symbol by `kind` before `label` |
| Faceplate not loading | Manual test | An explicit map from device kind to faceplate view (GF-22) |
| Top bar and alerts page counting every alarm on the gateway | Manual test | The alarm scope (GF-20) |
| Button text invisible (Color, History, ACK) | Screenshot review | A text colour in each button class |
| Text labels crossing a valve, a tile and a pipe | Screenshot review | Labels moved in the plant definition; no gate checks labels yet (COB-061) |
| A side readout clipping its per cent sign | Screenshot review | Side readouts widened from 56 to 64 px |
| ACK acknowledging nothing | G10, check F7 | The user passed to `system.alarm.acknowledge` (GF-21) |
| Acknowledged alarm frames still flashing | G10, check F7 | Frames flash only while unacknowledged |
| Overview card devices opening their faceplate on a missing tag folder | The faceplate contract check of G7 | `device` may name the tag folder (page 08 section 3); the check fails a device that binds outside its folder |
| Generated device folders lacking members their faceplate binds (pump station sample, demo) | Review of the faceplate contract | The generator writes every member the faceplate of the kind binds (page 06 section 5) |

## 7. Assessment

1. **Effort.** One file of 382 lines defines the plant, and one command builds, gates and deploys
   it. The frame (top bar, navigation, alarms, palettes, faceplates) costs a child project nothing.
2. **Fitness.** The project runs: commands, modes, setpoints, automatic control, alarms,
   acknowledgement and fault reset all work from the glass, and the screens are free of error
   badges and quality overlays.
3. **Gates and review.** Seven of the defects in Table 5 passed every gate then in place and were
   found by looking or by hand. Three of them would now fail a gate (the overlays in G8; the card
   symbol drawn as text and the faceplate that did not load in G11). The other four (alarm scope,
   invisible text, clipped text, label collisions) still need a screenshot review; COB-061 and
   COB-066 would gate the last three.
4. **Limits.** Table 6 lists what a process plant needs and the library does not yet provide.

Table 6. Library gaps for process plants.

| Gap | Effect today | Register |
|---|---|---|
| Label collision check | Free labels are checked against symbols and pipes by screenshot only | COB-061 |
| Analogue instrument faceplate (value, limits, alarms, trend) | Closed 2026-10-08: readouts and instrument fields open `Faceplate/Instrument` (page 13 section 8) | COB-062 |
| Command security | Closed 2026-10-09: every write path needs the admin role (COBD-024, page 06 section 5 rule 7) | COB-063 |
| Trends | Closed 2026-10-09: the faceplates draw a trend, and the trend page `/trends` holds every historised member | COB-064 |
| Faceplates for filters and switches | These kinds are drawn but are not devices | COB-065 |
| Text clipping and contrast check in the render gate | Clipped or unreadable text is found by screenshot review only | COB-066 |

## 8. Commands

Run from the repository root; in Git Bash set `MSYS_NO_PATHCONV=1` first (GF-15). The restore of
section 3 (two imports, the first with `sim/reset` true) returns the plant to its initial state,
P-502 faulted included; a single import of the tag model returns the memory members only (GF-42).

```bash
python tools/plants/wtp.py
```

```bash
python tools/hmi/screen.py --project cadre_hmi_wtp --descriptor screens/wtp/overview.json --descriptor screens/wtp/intake.json --descriptor screens/wtp/filtration.json --descriptor screens/wtp/disinfection.json --app-name "Village WTP" --alarm-scope "*cadre_hmi_wtp*" --tags-file screens/wtp/tags.json --out build --report workspace/reports/wtp.json --deploy
```

```bash
F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/functional.py --base http://localhost:8088/data/perspective/client/cadre_hmi_wtp --out workspace/wtp/functional
```

```bash
F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/faceplates.py --base http://localhost:8088/data/perspective/client/cadre_hmi_wtp --descriptor screens/wtp/overview.json --descriptor screens/wtp/intake.json --descriptor screens/wtp/filtration.json --descriptor screens/wtp/disinfection.json --out workspace/wtp/faceplates
```

The running plant: `http://localhost:8088/data/perspective/client/cadre_hmi_wtp`.
