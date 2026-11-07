# STD-WFB-01: House HMI Standard for Migrated Projects, Standard

| Item | Value |
|---|---|
| Document ID | STD-WFB-01 |
| Version | 0.2 |
| Status | Draft for the owner's approval; every ruling of section 15 in force on its default until the owner rules |
| Issued | 2026-11-07 |
| Author | The G1 contracts session (Opus 5.5) |
| Approver | The owner |
| Package | NOTE-WFB-14 WP-S1 (change group G1) |
| Register | WFB-325 (planned by NOTE-WFB-14); WFB-328 (this standard); WFB-338, WFB-339 (raised here) |
| Machine-readable copy | `standards/hmi/rules.json` (the rule index), `standards/hmi/client-layer.schema.json` (the client layer) |
| Basis | WorkflowBuilder main at `9cb3696`; the library line at Cadre-Sandbox-OpenBridge `506076c`, equal to cadre-ob-cloud `dd1958d` for every library path (module 0.8.0) |

The revisions of this document are listed below.

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-11-07 | G1 contracts session | First draft: rules in seven areas, the check catalogue, the client layer, the map from the fourteen principles and the house decisions, rulings |
| 0.2 | 2026-11-07 | G1 contracts session | The cold read's findings mended: acknowledgement and confirmation made consistent with the library; deadbands and the delays the library cannot hold reported, not required; UDT adoption bounded by the measured shapes; the frame chosen (HMI-DSP-25); rules that restated the library reduced to the house choice; the layout check split by rule; typed parameters (section 3.5); the tag root, depth, collisions and the plant with no areas stated; the tests outside the schema stated; check results placed by ruling R4 |

Conventions: no client, site, project, page or tag name appears in this document. "The library" is the Cadre HMI
library on its one line (the cloud repository and the Sandbox that follows it). "Wiki page 16" and "wiki page 17" are
the library's wiki pages 16 (component selection guide, COB-WIKI-16 revision B) and 17 (tag model and UDTs, COB-WIKI-17
revision B); a citation names their section and states only the house choice made within them. A "page" alone is a
page of the target. "The original" is the Citect project being migrated; "the target" is the Ignition Perspective
project the workflow builds.

Contents: 1 Purpose and Scope; 2 Terms and Abbreviations; 3 Structure of a Rule; 4 Sources and Their Precedence;
5 Display Philosophy; 6 Navigation; 7 Visibility; 8 Alarm Philosophy; 9 Tag Hierarchy and Naming; 10 User Defined
Types and History; 11 Check Catalogue; 12 Client Layer; 13 Map from Today's Sources; 14 Adoption and Open Items;
15 Owner Rulings; 16 References.

## 1. Purpose and Scope

### 1.1 Purpose

This standard states once, with an identifier for each rule, the house rules that a migrated project's screens,
alarms, tag structure, user defined types and history follow. It replaces, for the design of a migration, the five
scattered places NOTE-WFB-14 section 4.6 lists: the fourteen principles inside the design brief, the study of one
Ignition project read as a rulebook, the library's wiki read as house policy, the copied house decisions, and the
empty client style guide input. Every rule that can be checked names its check, so that a design, a page build and
the final review report each rule's result by its identifier (NOTE-WFB-14 principle 8, WP-S3).

### 1.2 Scope

In scope: the house layer that the library does not state. That is the display philosophy (display levels, colour,
layout, text, motion, commands, faceplates, the frame), navigation, the visibility rule of NOTE-WFB-14 principle 1,
the alarm philosophy, the tag hierarchy and naming above the device folder, the choice of user defined types, and
history and trends.

Out of scope:

1. What the library already states. Which component draws a plant object, the frames, the faceplate styles, the
   members of each device kind, the write paths, the alarm form, the five priorities and their colours, and the UDT
   names and shapes belong to the library (wiki pages 04, 13, 16, 17 and 18). This standard cites them and states the
   house choice within them.
2. How a rule is enforced. The checks are catalogued in section 11 with the package that builds each; their
   implementation is WP-S3 (change group G2b), the visibility measure is NOTE-WFB-15, and the classification that
   proposes a device's place in the plant hierarchy is NOTE-WFB-16.
3. Alarm rationalisation and alarm system performance monitoring, which are activities of the site that runs the
   target (rule HMI-ALM-08).
4. Any one client's style. A client's rules enter through the client layer of section 12.

### 1.3 Modal Verbs

"Shall" marks a mandatory rule; "should" marks a recommended rule whose departure is reported as advice; "may" marks a
permission; "cannot" marks what the client layer is not permitted to do. A rule marked fixed (section 3.4) cannot be
changed by a client layer.

## 2. Terms and Abbreviations

Table 2.1 defines the terms this standard uses in a narrowed sense.

Table 2.1. Terms and abbreviations.

| Term | Meaning |
|---|---|
| ASM | Abnormal Situation Management: the consortium guidance on operator displays and alarms |
| ASM frame | The library's frame `asm` (stock rendering) or `obasm` (module rendering), wiki page 16 section 3.1 Table 4 |
| ASMP study | The study of one existing Ignition project built to ASM, ISA-88 and ISA-101 practice: report ASMP-REPORT-01 revision A and the study wiki, in `F:\repos\Ignition-ASM-Primary` |
| Census | ctig's classification of the original's templates, symbols and tags into devices, members and roles, with the original's tag records |
| Check | A test that decides a rule's result on a design, a descriptor set, a built project or a run; named `CK-<AREA>-<nn>` |
| Client layer | The file of one engagement that changes overridable rules of this standard by identifier (section 12) |
| Design gap | A gap row of the design (block 18): an item the design does not draw or carry, with its reason |
| Device | A plant object the operator commands or whose alarms the operator acknowledges; a tag folder (wiki page 17 section 2.1) |
| EEMUA 191 | EEMUA Publication 191, Alarm Systems: A Guide to Design, Management and Procurement |
| Effective standard | This standard with one engagement's client layer applied; what a run designs and checks against |
| Gap accepted by name | A design gap that the person accepted at the design review, listed by its identifier and reason |
| HMI | Human machine interface |
| ISA-101 | ANSI/ISA-101.01-2015, Human Machine Interfaces for Process Automation Systems |
| ISA-18.2 | ANSI/ISA-18.2-2016, Management of Alarm Systems for the Process Industries |
| Migration report | The final review's report of a run, which lists the advice items of this standard |
| Node | A node of the plant hierarchy: an area, or a unit within an area (wiki page 04 section 7) |
| Node path | The slash-separated names of a node from the area down, for example `<area>/<unit>` |
| Original | The Citect project being migrated |
| Principle P1 to P14 | The fourteen principles of `src/workflows/briefs/v3/project-design.md` section 3, as numbered there |
| Target | The Ignition Perspective project the workflow builds |
| UDT | User defined type: an Ignition tag type with members and parameters |

## 3. Structure of a Rule

### 3.1 Fields

Every rule has the fields of Table 3.1, in this document and in `rules.json`. The two copies never disagree; where
they do, this document is right and `rules.json` is written again from its tables (WP-S3 builds the generator and a
test that compares the two).

Table 3.1. The fields of a rule.

| Field | Content |
|---|---|
| `id` | `HMI-<AREA>-<nn>`; stable, never reused; a withdrawn rule keeps its identifier with the status withdrawn |
| `area` | One of `DSP`, `NAV`, `VIS`, `ALM`, `TAG`, `UDT`, `HIS` (section 3.2) |
| `level` | `shall` or `should` |
| `statement` | The rule, one sentence or two |
| `sources` | The sources, each a key of section 4 Table 4.1 followed by its section, as the tables write them |
| `check` | A check id of section 11, or `none` with the reason (a judgement of the design review, or the library carries it) |
| `carried_by` | `workflow` (WorkflowBuilder's checks enforce it), `library` (the library's code carries it and its manifest declares it, NOTE-WFB-15), or `both` |
| `fixed` | `true` when a client layer cannot change it (section 3.4) |
| `parameters` | The named values the rule takes, from Table 3.5 |

### 3.2 Areas

Table 3.2 lists the seven areas and the section that states each.

Table 3.2. The areas of the standard.

| Area | Subject | Section |
|---|---|---|
| `DSP` | Display philosophy: levels, colour, layout, values and text, motion, commands, faceplates, the frame | 5 |
| `NAV` | Navigation | 6 |
| `VIS` | Visibility of the original's items | 7 |
| `ALM` | Alarm philosophy | 8 |
| `TAG` | Tag hierarchy and naming above the device folder | 9 |
| `UDT` | The choice and use of user defined types | 10.1 |
| `HIS` | History and trends | 10.2 |

Section 11 is the check catalogue of every area.

### 3.3 Check Identifiers

A check id has the form `CK-<AREA>-<nn>`. One check may decide several rules; one rule names one check. A check id
names what is measured, not the code that measures it; section 11 names where each check runs and which package
builds it. A check that decides a rule of several clauses reports each failed item with the clause it breaks.

### 3.4 Fixed Rules

A rule is fixed where the workflow's honesty or the operator's safety depends on it. The 14 fixed rules are the
visibility rules (HMI-VIS-01 to HMI-VIS-05); the rules that no item of the original is dropped or invented silently
(HMI-DSP-15, HMI-NAV-02, HMI-NAV-04, HMI-ALM-01, HMI-TAG-05); the confirmation of commands (HMI-DSP-18); shelving only
through the library (HMI-ALM-07); the rule that no unmeasured UDT shape reaches a site (HMI-UDT-05); and the
authorisation of writes under `_types_` (HMI-UDT-06). A change to a fixed rule is a change of this standard, made by a
new version and approved by the owner, never by a client layer.

### 3.5 Parameters

Table 3.5 lists every parameter, its type, its allowed values and its default. A parameter's value for a run is taken,
first that applies, from the client layer, then from the engagement profile's house decision of the same meaning
(section 13.2), then from this default. A parameter with no default is stated per engagement; while it is unset,
block 3 asks for it on its decisions card. A client layer may set a parameter of any rule, fixed or not.

Table 3.5. The parameters.

| Rule | Parameter | Type | Allowed values | Default |
|---|---|---|---|---|
| HMI-DSP-01 | `overview_markers` | array of string | Words matched in any case in an original page's menu label or title | `["overview"]` |
| HMI-DSP-06 | `pipe_colour` | string | `by_medium_buses_grey`, `neutral` | `by_medium_buses_grey` |
| HMI-DSP-08 | `fit` | string | `fill_never_above_1`, `fill`, `none` | `fill_never_above_1` |
| HMI-DSP-17 | `pipe_animation` | boolean | `true`, `false` | `false` |
| HMI-DSP-21 | `popups_as_faceplates` | boolean | `true`, `false` | `true` |
| HMI-DSP-24 | `faceplates_on_plain_symbols` | string | `all`, `none` | `all` |
| HMI-ALM-02 | `priorities_by_rank` | object | Keys: the original's priority ranks as decimal strings; values: `critical`, `high`, `medium`, `low`, `diagnostic` | None |
| HMI-ALM-03 | `inferred_alarm_priorities` | string | `labelled_inferred`, `refused` | `labelled_inferred` |
| HMI-ALM-06 | `acknowledge` | string | `selected_and_all_after_confirm`, `selected_only` | `selected_and_all_after_confirm` |
| HMI-ALM-13 | `priority_distribution` | object | Keys `low`, `medium`, `high`; values: numbers from 0 to 1 that sum to 1 | `{"low": 0.80, "medium": 0.15, "high": 0.05}` |
| HMI-TAG-01 | `unplaced_area` | string | An area name of HMI-TAG-02's characters | `Unassigned` |
| HMI-TAG-04 | `values_folder` | string | A folder name of HMI-TAG-02's characters | `Values` |
| HMI-TAG-05 | `unsourced_folder` | string | A folder name of HMI-TAG-02's characters | `Unsourced` |
| HMI-TAG-08 | `max_levels` | integer | 1 to 4 | 2 |
| HMI-UDT-01 | `adopt_udts` | boolean | `true`, `false` | `true` |
| HMI-HIS-03 | `history_provider` | string | The name of a history provider of the gateway | None |

## 4. Sources and Their Precedence

### 4.1 Source Keys

Table 4.1 gives the key each rule uses for its sources.

Table 4.1. The sources of the rules.

| Key | Source | How it is used |
|---|---|---|
| `ISA101` | ANSI/ISA-101.01-2015 | The display hierarchy, the style of a high performance display, the HMI philosophy and style guide structure; cited by topic (ruling SR7) |
| `ISA182` | ANSI/ISA-18.2-2016 | The alarm philosophy, the alarm states, shelving, suppression and out of service, rationalisation; cited by topic (ruling SR7) |
| `EEMUA191` | EEMUA Publication 191 | The guidance on the distribution of alarm priorities; cited by topic (ruling SR7) |
| `ASMP` | ASMP-REPORT-01 revision A and the study wiki (pages B1/udt-design, B2/alarm-configuration, B3/alarm-display, B5/navigation-and-hierarchy) | Evidence of one project built to ASM practice, with its defects (report section 6); never a rule by itself |
| `P1` to `P14` | The fourteen principles of `src/workflows/briefs/v3/project-design.md` section 3 | The house practice the exercise applied; each now has its rule ids (section 13) |
| `HD` | A house decision of the engagement profile (`decisions`, schema `wfb.migration.profile/1`), by key | Each becomes a rule or a parameter (section 13.2) |
| `L04`, `L13`, `L16`, `L17` | The library's wiki pages 04, 13, 16 and 17, by section | What the library offers and reads; the house rule chooses among it |
| `WFB` | A finding or decision of this repository (NOTE-WFB-14, a WFBD or WFB item) | The reason a house rule exists |

### 4.2 Order of Precedence

1. The library's contract bounds every rule: a rule never asks for what the library cannot draw or read, and where a
   rule and the library's pages differ on what the library does, the library's code and profile govern (wiki page 17
   section 1) and the difference is a register item here.
2. The client layer overrides this standard for an overridable rule, by identifier (section 12).
3. This standard governs the design of every engagement.
4. The ASMP study, the ISA standards, EEMUA 191 and the principles are the evidence behind the rules; none of them
   binds a design except through a rule of this standard.

## 5. Display Philosophy

### 5.1 Display Levels and the Frame

Table 5.1 states the rules for the display hierarchy and the frame. A page's display level is recorded in the design's
entry for the page, and under an ASM frame also as the descriptor's level word (wiki page 16 section 3.2 rule 4).

Table 5.1. Display levels and the frame.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-DSP-01 | shall | Every page of the target is given one display level of ISA-101: level 1 the site overview and each overview that spans the site for one discipline; level 2 area and unit pages; level 3 faceplates; level 4 diagnostics, information, alarm lists and help pages | ISA101 display hierarchy; P3; ASMP report section 5.7 item 5 | CK-DSP-01 | workflow | No |
| HMI-DSP-02 | shall | Where the plant has areas, every process page names its node, and under an ASM frame its level word, by the keys of wiki page 16 section 3.2 rules 3 and 4 | P2; L16 section 3.2; L04 section 7 | CK-DSP-01 | both | No |
| HMI-DSP-25 | shall | A project whose plant has areas is built with an ASM frame, chosen between `asm` and `obasm` by the rendering as wiki page 16 section 3.2 rules 1 and 2 state; that frame's top bar carries principle P11 | P2; P11; L16 sections 3.1 and 3.2; L04 sections 3 and 8 | CK-DSP-25 | both | No |

### 5.2 Colour

Table 5.2 states the colour rules.

Table 5.2. Colour.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-DSP-03 | shall | A normal state is shown in the library's neutral palette; no normal state is shown in an alert colour, red or green; the media colours of pipes (HMI-DSP-06) are the one exception | ISA101 high performance display; P4; ASMP report section 5.9 | CK-DSP-03 | both | No |
| HMI-DSP-04 | should | Every state the operator acts on is coded by shape, line or text as well as colour | ISA101; P4 | none: judged at the design review; the library codes alarm priorities by colour with one badge shape (wiki page 04 section 7 item 3, WFB-339) | library | No |
| HMI-DSP-05 | shall | A descriptor sets no colour, class or style beyond the keys the library's schema offers for it (for example an indicator's `states`, wiki page 16 section 6.1 Table 8) | P11; L16 section 6.1 | CK-DSP-03 | both | No |
| HMI-DSP-06 | shall | Pipes are coloured as the parameter `pipe_colour` states, by the media of wiki page 16 section 10.1 Table 13 | HD `pipe_colour`; L16 section 10.1 | CK-DSP-06 | workflow | No |

### 5.3 Layout

Table 5.3 states the layout rules.

Table 5.3. Layout.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-DSP-07 | shall | A page keeps the original's topology and the order of its regions; a region moves only as a whole, into an empty band, and is never split; a flow keeps its sequence | P1; P13 | CK-DSP-07 | workflow | No |
| HMI-DSP-08 | shall | Each page renders on the page canvas of the library's frame at the profile's window as the parameter `fit` states | P13; HD `fit`; L16 section 3.3 | CK-DSP-08 | both | No |
| HMI-DSP-09 | shall | Repeated panels share one size and stand in one row or one column; a row of like devices spreads across the width | P13 | CK-DSP-09 | workflow | No |
| HMI-DSP-10 | shall | A symbol on a flow is centred on its line and turned along it; text never lies over other text, a symbol or a line | P13 | CK-DSP-10 | workflow | No |
| HMI-DSP-11 | shall | Every label names the item it stood beside in the original and keeps its order among its neighbours | P13; P1 | CK-DSP-11 | workflow | No |
| HMI-DSP-12 | should | An original page that shows a process path is drawn in the diagram layout of wiki page 16 section 5, never as cards | L16 section 5 | none: a design choice, shown at the design review | workflow | No |

### 5.4 Values and Text

Table 5.4 states the rules for values and text.

Table 5.4. Values and text.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-DSP-13 | shall | A value that has states is shown in words, never as a bare number | P14 | CK-DSP-13 | workflow | No |
| HMI-DSP-14 | shall | An analogue value carries the unit symbol of its tag; where the facts give a range, it carries a range bar with its normal band and limits, by the means wiki page 16 section 9 offers | P5; P14; L16 section 9 | CK-DSP-14 | workflow | No |
| HMI-DSP-15 | shall | No measurement is invented in the delivered target: a value the original shows from a tag is bound to that tag, and a value with no source is a gap accepted by name, never a constant or a simulated value drawn as live | HD `invented_measurements`; HD `simulation`; WFB-308; WFB-323 | CK-DSP-15 | workflow | Yes |

A simulation that the profile's decision `simulation` enables is a test layer of the gateway, removed before
delivery; the final review lists its tags, and HMI-DSP-15 applies to the target without it.

### 5.5 Motion

Table 5.5 states the rules for motion.

Table 5.5. Motion.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-DSP-16 | shall | Motion (flashing, blinking, animation) is used only for unacknowledged alarms | ISA101; P6; L04 section 3 Table 2 | CK-DSP-16 | both | No |
| HMI-DSP-17 | shall | Pipes are animated only where the parameter `pipe_animation` is true | P6; HD `pipe_animation` | CK-DSP-16 | workflow | No |

### 5.6 Commands

Table 5.6 states the rules for commands.

Table 5.6. Commands.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-DSP-18 | shall | Every state-changing command and every setpoint write asks the operator to confirm before it is written; of the acknowledgements, only Ack all asks (HMI-ALM-06) | P10; L13 section 10.5; L04 section 8.12; ASMP report section 5.3 item 1 (a source with no confirmation) | CK-DSP-18 | library | Yes |
| HMI-DSP-19 | shall | An original page button that commands a device becomes a command of that device's faceplate, where wiki page 16 section 10.2 places a device's command | L16 section 10.2 | CK-DSP-19 | workflow | No |
| HMI-DSP-20 | shall | Where the original has modes, the device carries ownership by mode as wiki page 16 section 11 Table 15 offers | L16 section 11; L17 section 5.5; ASMP report section 8.2 | none: decided by the device model's `modes`, shown at the design review | both | No |

### 5.7 Faceplates

Table 5.7 states the rules for faceplates.

Table 5.7. Faceplates.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-DSP-21 | shall | Where the parameter `popups_as_faceplates` is true, a pop-up of the original that serves a device becomes that device's faceplate, never a page; a pop-up that serves no device becomes a level 4 page or a gap accepted by name | P12; HD `popups_as_faceplates` | CK-DSP-21 | workflow | No |
| HMI-DSP-22 | shall | Faceplates are the library's, in the style wiki page 16 section 4.1 names for an ASM operation and in the place section 4.2 states | P9; L16 sections 4.1 and 4.2; ASMP report section 5.2 | none: the library's faceplates carry it | library | No |
| HMI-DSP-23 | shall | Each device's own drawing (wiki page 16 section 8 Table 11) stands on a page of the device's ratified node (HMI-TAG-01); every other page that shows the device draws a second drawing | HD `device_symbol_own_page_only`; L16 section 8; WFB-338 | CK-DSP-23 | workflow | No |
| HMI-DSP-24 | should | A plain symbol of the original that stood for a device opens that device's faceplate as the parameter `faceplates_on_plain_symbols` states | HD `faceplates_on_plain_symbols`; L16 section 8 | none: a design choice, shown at the design review | workflow | No |

## 6. Navigation

Table 6.1 states the navigation rules.

Table 6.1. Navigation.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-NAV-01 | shall | Under an ASM frame (HMI-DSP-25), the operator navigates by the plant hierarchy: the tree with search, the breadcrumb with alarm counts per priority, and the pivot pages of a node | P2; ISA101; L04 sections 7 and 8; ASMP report section 5.7 | CK-NAV-01 | both | No |
| HMI-NAV-02 | shall | Every navigation target of the original, including an opener whose target the navigation table lists as unresolved, is routed to a page or a faceplate of the target, or is a gap accepted by name | P1; WFB navigation table (`src/wfb_blocks/migration/navtable.py`) | CK-NAV-02 | workflow | Yes |
| HMI-NAV-03 | shall | A symbol opens its faceplate and a separate link navigates; the same click never does both | P8; L16 section 10.5 | CK-NAV-03 | both | No |
| HMI-NAV-04 | shall | Every route that a design names is generated; a page names no route that the target does not hold | WFB-293 (the trends route the design named and the build did not generate) | CK-NAV-02 | workflow | Yes |

## 7. Visibility

### 7.1 The Rules

Table 7.1 states the visibility rules. They carry NOTE-WFB-14 principle 1 ("nothing the original shows disappears
silently"); NOTE-WFB-15 defines how each is measured.

Table 7.1. Visibility.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-VIS-01 | shall | Every item of the original with a place on the page is drawn visibly at that place, or is a gap the person accepts by name | WFB NOTE-WFB-14 principle 1, section 3; P1 | CK-VIS-01 | both | Yes |
| HMI-VIS-02 | shall | A stand-in for a kind the library lacks shows the original's shape at its place and size, from the captured geometry, in a neutral style | WFB NOTE-WFB-14 ruling R3, RC3 | CK-VIS-02 | both | Yes |
| HMI-VIS-03 | shall | A claim of the design about what the library holds or lacks agrees with the library's catalogue as the run holds it | WFB NOTE-WFB-14 RC2, WFB-313 | CK-VIS-03 | workflow | Yes |
| HMI-VIS-04 | shall | Every gap accepted by name is listed, with its identifier, reason and the person who accepted it, on the design sheet and on the final review | WFB NOTE-WFB-14 principle 1, WP-F6 | CK-VIS-04 | workflow | Yes |
| HMI-VIS-05 | shall | An item drawn from the original's geometry shows no live state unless it is bound to a tag the census holds | HMI-DSP-15; WFB NOTE-WFB-14 principle 2 | CK-DSP-15 | workflow | Yes |

### 7.2 Meaning of Visible

"Visible" is defined per descriptor element kind by NOTE-WFB-15 (the visibility measure of WP-F1): in outline, the
element's rendered box lies at its source box and shows a border, a fill unlike its container, text or a symbol. This
standard fixes the rule; NOTE-WFB-15 fixes the measure and its thresholds. A change to the measure is a change to
NOTE-WFB-15, not to HMI-VIS-01.

## 8. Alarm Philosophy

### 8.1 Basis

The house alarm philosophy is that of ISA-18.2 applied to a migration: the migration carries the original's alarms
faithfully into the library's one alarm form (wiki page 17 section 7.2, wiki page 13 section 11.3) and the five
priorities (wiki page 17 Table 21), and reports, without changing, what a rationalisation would need. One alarm of the
original is one alarm condition: each limit of an analogue alarm record counts once. The ASMP study is evidence of
what an ASM project configured and of its defects (ASMP report sections 5.4 to 5.6 and 6).

### 8.2 The Rules

Table 8.1 states the alarm rules.

Table 8.1. Alarm philosophy.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-ALM-01 | shall | Every alarm condition of the original's alarm tables becomes one alarm of the target in the library's form, on the member or source tag where wiki page 17 sections 7.3 and 7.4 place it, or is a gap accepted by name | ISA182 alarm philosophy; P1; L17 sections 7.3 and 7.4 | CK-ALM-01 | workflow | Yes |
| HMI-ALM-02 | shall | The original's alarm priorities map onto the five priorities of wiki page 17 Table 21 by the parameter `priorities_by_rank`; a rank the map does not name is a gap, never a guess | ISA182; P7; HD `priorities_by_rank`; L17 section 7.2 | CK-ALM-02 | workflow | No |
| HMI-ALM-03 | shall | A priority the design infers where the original states none is recorded in the design's alarm entry with `priority_source` `inferred`, and shown at the design review, as the parameter `inferred_alarm_priorities` states | HD `inferred_alarm_priorities`; ASMP report section 5.4 (22 alarms with no priority) | CK-ALM-02 | workflow | No |
| HMI-ALM-04 | shall | An alarm of the original that needs no operator action is carried with the Diagnostic priority of wiki page 17 section 7.2, through the map of HMI-ALM-02 | P7; L17 section 7.2; L13 section 11.1 | CK-ALM-02 | workflow | No |
| HMI-ALM-05 | shall | The target shows the ISA-18.2 states normal, unacknowledged active, acknowledged active and returned to normal unacknowledged; suppressed by design and out of service are offered only once the library has proved them on a gateway | ISA182 alarm states; L13 sections 11.2 and 11.4 | none: the library carries it | library | No |
| HMI-ALM-06 | shall | Where the parameter `acknowledge` is `selected_and_all_after_confirm`, every alarm list offers Ack selected and Ack all, Ack all after a confirmation, as wiki page 04 section 8.12 states | HD `acknowledge`; L04 section 8.12; L13 section 10.5 | CK-ALM-06 | both | No |
| HMI-ALM-07 | shall | Alarms are shelved only through the library's alarm tables, with their shelving times (wiki page 17 section 7.2 Table 21, wiki page 13 section 11.4); no script, tag write or page control of the target shelves an alarm | ISA182 shelving; L17 section 7.2; L13 section 11.4 | CK-ALM-07 | both | Yes |
| HMI-ALM-08 | should | The migration report lists every carried alarm, per priority, as not rationalised, for the site's rationalisation; the migration changes no alarm's priority, limit or text to rationalise it | ISA182 rationalisation | CK-ALM-08 | workflow | No |
| HMI-ALM-09 | shall | An alarm's text is the original's alarm description, placed in the label form of wiki page 13 section 11.3 item 1 | ISA182; L13 section 11.3 | CK-ALM-09 | workflow | No |
| HMI-ALM-10 | shall | An alarm's display path names the same node as the device's tag path (HMI-TAG-01), so that the counts, the breadcrumb and the tag browser agree | L17 section 7.2; L04 section 7; ASMP report section 5.5 | CK-TAG-01 | workflow | No |
| HMI-ALM-11 | shall | An on-delay the original states for a limit of a tank, an instrument or a controller is carried to that limit's delay member (wiki page 17 section 5.2) | L17 sections 5.2 and 7.2 Table 20; ASMP report section 5.4 | CK-ALM-11 | workflow | No |
| HMI-ALM-12 | shall | Where the census gives a device an acknowledgement member of the original, the device carries the acknowledgement relay of wiki page 17 section 5.3 bound to it | L17 section 5.3; L13 section 11.5; ASMP report section 5.5 items 2 and 3 | CK-ALM-12 | workflow | No |
| HMI-ALM-13 | should | The migration report states the distribution of the carried alarms over Low, Medium and High against the parameter `priority_distribution`, with the Critical alarms counted apart | EEMUA191; ISA182 alarm performance | CK-ALM-13 | workflow | No |
| HMI-ALM-14 | should | A deadband, or an on-delay of an alarm whose kind has no delay member, is listed on the migration report with its value, since the library holds neither | L17 section 5.2; L17 section 11 item 2 (the `timeOnDelaySeconds` binding unmeasured) | CK-ALM-14 | workflow | No |

## 9. Tag Hierarchy and Naming

### 9.1 Basis

Wiki page 17 section 2.1 makes a device a tag folder `<tagRoot>/<id>`, and its Table 1 lets the `id` hold folders,
with a slash only between them. The library reads the folder and never the path above it. The house rule places that
folder in the plant hierarchy. Classification proposes each device's node and the person ratifies it (NOTE-WFB-16);
the device model entry carries it (NOTE-WFB-15).

### 9.2 The Rules

Table 9.1 states the tag hierarchy and naming rules.

Table 9.1. Tag hierarchy and naming.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-TAG-01 | shall | Device folders are grouped by the plant hierarchy under the child project's tag root, at `<tagRoot>/<node path>/<device>`, the node path being the device's ratified node, area then unit (NOTE-WFB-16 section 11); a device that no source places sits in the area `unplaced_area` until the person places it, and the final review lists it; where the person ratifies no area for the plant, the folders sit directly under the tag root and the pages name no node | ISA101 (the display hierarchy follows the plant); ASMP report section 5.7 item 2; L17 section 2.4 Table 1; L04 section 7; L16 section 3.2 rule 3 | CK-TAG-01 | both | No |
| HMI-TAG-02 | shall | The device folder keeps the original's equipment id, made safe: each character outside the ASCII letters, digits, underscore and hyphen becomes an underscore; two names that become equal without regard to case within one parent folder are refused at the design check and renamed by the person on the ratification card | L17 section 2.4 Table 1 (the id pattern); GF-11 (no slash in a tag name); NOTE-WFB-16 | CK-TAG-02 | both | No |
| HMI-TAG-03 | shall | An area or unit folder takes the name of the original's area or unit as the person ratified it, made safe as HMI-TAG-02 states | HMI-TAG-02; NOTE-WFB-16 | CK-TAG-02 | both | No |
| HMI-TAG-04 | shall | A tag that belongs to no device (a free readout of a page) sits in the folder `values_folder` of the node of the pages that show it; where they are pages of several nodes, of their deepest common node, or of the tag root where they share none | WFB NOTE-WFB-14 section 4.6 (free tags placed under no rule) | CK-TAG-04 | workflow | No |
| HMI-TAG-05 | shall | A memory tag that stands in for a missing source (a design gap) sits in the folder `unsourced_folder` of its node; it is listed on the final review, is never counted as bound by CK-DSP-15, and a value read from it is drawn as a gap, never as live | HMI-DSP-15; WFB-323; L17 section 2.2 item 2 | CK-TAG-04 | workflow | Yes |
| HMI-TAG-06 | shall | A device member's source is a tag of the original or a memory tag of HMI-TAG-05; a member with neither is not created, as wiki page 17 section 2.2 item 2 requires | L17 section 2.2 | CK-TAG-06 | both | No |
| HMI-TAG-07 | shall | The child project's tags sit under the profile's `target.tag_root`, whose bracketed prefix names the tag provider | L17 section 2.1; profile schema `target.tag_root` | CK-TAG-01 | workflow | No |
| HMI-TAG-08 | should | The node path has at most `max_levels` levels; a deeper plant model of the original is ratified to that depth on the card (NOTE-WFB-16), so that the node path and the folder path stay one string | ASMP report section 5.7 item 2 (a four-level model); L04 section 7 | CK-TAG-01 | workflow | No |

## 10. User Defined Types and History

### 10.1 User Defined Types

Table 10.1 states the rules for the choice and use of UDTs. NOTE-WFB-14 ruling R8 adopted UDTs in the target (one per
library kind) on the one library line; wiki page 17 states their names, shapes and members, and marks which shapes are
measured.

Table 10.1. User defined types.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-UDT-01 | shall | Where `adopt_udts` is true, every device of a library kind with a UDT on wiki page 17 (section 3.2 Table 2) is an instance of the library's definition for its kind, placed and named as NOTE-WFB-15 section 9.3 states, whenever every shape the instance needs is marked measured in the library's manifest (HMI-UDT-05); otherwise the device is a folder of atomic tags and CK-UDT-01 reports `not_applicable` with the unmeasured shape named | WFB NOTE-WFB-14 ruling R8; L17 sections 3.1, 3.2 and 11 item 2 | CK-UDT-01 | both | No |
| HMI-UDT-02 | shall | A variant definition that wiki page 17 section 3.2 rules 1 to 3 call for is derived from the device model's member sets and named by the library's tool, as NOTE-WFB-15 section 9.3 states; the person may give a variant a readable name on the design review card | L17 section 3.2; NOTE-WFB-15 section 9.3 | CK-UDT-01 | both | No |
| HMI-UDT-03 | shall | The target's types are the library's; the original's own types (Citect genie and equipment types) and the UDT families of another project are never copied as types of the target | L17 section 3.2; ASMP report section 5.1 item 5 (no source member maps exactly to the library's) | CK-UDT-01 | both | No |
| HMI-UDT-04 | shall | No type is made for a kind to which the library gives none (the local device, wiki page 17 section 3.2 Table 2) | L17 sections 3.2 and 4.9 | CK-UDT-01 | both | No |
| HMI-UDT-05 | shall | No UDT shape that wiki page 17 section 11 item 2 marks unmeasured reaches a site's gateway before it is measured on the cloud gateway and marked measured in the library's manifest | L17 section 11 item 2; NOTE-WFB-15 | CK-UDT-05 | both | Yes |
| HMI-UDT-06 | shall | A write under the provider's `_types_` folder on the owner's gateway is made only with the owner's authorisation | L17 section 3.1; COBD-035 | none: COBD-035 governs; the write waits for the owner's authorisation | workflow | Yes |

### 10.2 History and Trends

Table 10.2 states the history and trend rules.

Table 10.2. History and trends.

| Id | Level | Rule | Sources | Check | Carried by | Fixed |
|---|---|---|---|---|---|---|
| HMI-HIS-01 | shall | History is configured on the members wiki page 17 section 8 Table 22 marks for each kind; on a UDT instance only once the history keys on a type member are measured (HMI-UDT-05) | L17 sections 8 and 11 item 2 | CK-HIS-01 | both | No |
| HMI-HIS-02 | shall | Every tag the original trends (its trend tag records as ctig extracts them) is historised in the target and shown on the trend page, a node's trend pivot or an embedded trend, or is a gap accepted by name | P1; L16 section 10.3; L04 section 8.6 | CK-HIS-02 | workflow | No |
| HMI-HIS-03 | shall | History is written to the provider the parameter `history_provider` names | L17 section 8 | CK-HIS-03 | workflow | No |
| HMI-HIS-04 | should | The migration report lists each historised member with the sample period of the original's trend tag, since wiki page 17 section 8 gives the target no sample key | P1; L17 section 8 | none: a report item | workflow | No |
| HMI-HIS-05 | shall | A device model's `trend` list names only members whose tags are historised, and every historised member of a device is in its list | L17 section 8 item 2, section 11 item 5 | CK-HIS-01 | both | No |
| HMI-HIS-06 | shall | The trend page's route exists whenever a device has a trended member | L13 section 8 rule 6; WFB-293 | CK-NAV-02 | workflow | No |

## 11. Check Catalogue

### 11.1 The Checks

Table 11.1 lists every check id, what it measures, where it runs and its state. "Exists" names the code that already
measures it; "partly exists" names the code and what it lacks; "planned" names the package that builds it. The places
a check runs are block 18's design check, the page build's checks, the evidence block and the final review (WP-S3).

Table 11.1. The checks.

| Check | Rules | Measures | Runs at | State |
|---|---|---|---|---|
| CK-DSP-01 | HMI-DSP-01, 02 | Every page has a level in the design; every process page of a plant with areas names its node, and under an ASM frame its level word | Design check; page build | Planned, WP-S3 |
| CK-DSP-03 | HMI-DSP-03, 05 | No descriptor key sets a colour, class or style outside the library's schema; no normal state value of an indicator's `states` takes an alert colour, red or green | Page build | Planned, WP-S3 |
| CK-DSP-06 | HMI-DSP-06 | Each pipe's medium agrees with `pipe_colour`: a medium of wiki page 16 Table 13, buses `neutral` | Page build | Planned, WP-S3 |
| CK-DSP-07 | HMI-DSP-07 | The order of the original's regions and the sequence of each flow are kept; no region is split | Page build | Planned, WP-S3 |
| CK-DSP-08 | HMI-DSP-08 | The page canvas and its fill against the frame's canvas, as `fit` states | Page build | Exists: layout rules L1 and L2 of `tools/hmi/page_checks.py` `check_layout`, run with `--canvas` |
| CK-DSP-09 | HMI-DSP-09 | Repeated panels of one size in one row or column; a row of like devices across the width | Page build | Partly exists: L4 and L5 (readout columns); the panels and the spread planned, WP-S3 |
| CK-DSP-10 | HMI-DSP-10 | Symbols on their flow's axis and turned along it; no text over text, a symbol or a line | Page build | Exists: L9 and L10 of `check_layout` |
| CK-DSP-11 | HMI-DSP-11 | Each label keeps its order among its neighbours and names the item it stood beside | Page build | Partly exists: L11 of `check_layout`, run with `--inventory`, tests the order; the naming planned, WP-S3 |
| CK-DSP-13 | HMI-DSP-13 | A value whose census tag record has state texts is drawn with a state text, not a number | Page build | Planned, WP-S3 |
| CK-DSP-14 | HMI-DSP-14 | An analogue value has its tag record's unit; a value whose tag record gives an engineering range has a range bar | Page build | Planned, WP-S3 |
| CK-DSP-15 | HMI-DSP-15, HMI-VIS-05 | Every bind names a tag the census holds or a memory tag a design gap declares; a constant expression over a tag (as WP-F7 defines it) is not bound | Page build; evidence | Partly exists (`page_checks.resolves`, `built_tags`); completed by WP-F7 |
| CK-DSP-16 | HMI-DSP-16, 17 | No animation except on an unacknowledged alarm; pipe animation as `pipe_animation` states | Page build | Planned, WP-S3 |
| CK-DSP-18 | HMI-DSP-18 | Every write path that changes a state or a setpoint passes the library's confirmation, as the library's manifest declares | Conformance check of NOTE-WFB-15 | Planned, WP-L1 |
| CK-DSP-19 | HMI-DSP-19 | No page button writes a tag that is a member of a device of the device model | Page build | Planned, WP-S3 |
| CK-DSP-21 | HMI-DSP-21 | No pop-up of the original that serves a device is built as a page | Design check | Planned, WP-S3 |
| CK-DSP-23 | HMI-DSP-23 | Each device has one own drawing, on a page of its ratified node | Design check; page build | Planned, WP-S3 |
| CK-DSP-25 | HMI-DSP-25 | The profile's build options name an ASM frame wherever the ratified hierarchy has an area | Design check | Planned, WP-S3 |
| CK-NAV-01 | HMI-NAV-01 | Under an ASM frame, the frame's tree, search and breadcrumb are built and every page of a node is reachable from the tree | Page build | Planned, WP-S3 |
| CK-NAV-02 | HMI-NAV-02, 04, HMI-HIS-06 | Every original navigation target, the unresolved ones included, is routed or a gap accepted by name; every named route is generated | Design check; page build | Partly exists: `navtable.py` builds the table and lists the openers it cannot name as unresolved; `page_checks.check_navigation` tests the routed entries and reads no gap list. The unresolved entries and the gaps planned, WP-S3; the generated route test, WP-R1 (WFB-293) |
| CK-NAV-03 | HMI-NAV-03 | No element both opens a faceplate and navigates | Page build | Planned, WP-S3 (the library's schema states the rule for `links`, wiki page 16 section 10.5) |
| CK-VIS-01 | HMI-VIS-01 | Each item with a source box is drawn visibly at its place, by the measure of NOTE-WFB-15 | Page build (render capture); evidence | Planned: the measure in the library (G3), the gate in WorkflowBuilder (G2b), WP-F1. Precedent: `page_checks.check_coverage` counts presence only (NOTE-WFB-14 section 3.3 item 1) |
| CK-VIS-02 | HMI-VIS-02 | A stand-in for a missing kind is an artwork element from the captured geometry at the source box | Design check; page build | Planned, WP-F2 and WP-F4 |
| CK-VIS-03 | HMI-VIS-03 | A design gap row's claim about the library agrees with the catalogue | Design check | Planned, WP-F4 (WFB-313) |
| CK-VIS-04 | HMI-VIS-04 | Every gap accepted by name appears on the design sheet and the final review with its reason and acceptor | Final review | Planned, WP-F6 and WP-S3 |
| CK-ALM-01 | HMI-ALM-01 | The original's alarm conditions equal the target's alarms plus the gaps accepted by name, per tag | Evidence | Planned, WP-S3 |
| CK-ALM-02 | HMI-ALM-02, 03, 04 | Every alarm's priority comes from the map or carries `priority_source` `inferred`; no rank outside the map | Design check; evidence | Planned, WP-S3 |
| CK-ALM-06 | HMI-ALM-06 | Each alarm list has the acknowledgement controls `acknowledge` names, Ack all behind its confirmation | Page build | Planned, WP-S3 |
| CK-ALM-07 | HMI-ALM-07 | No script, tag write or page control of the target shelves an alarm | Page build | Planned, WP-S3 |
| CK-ALM-08 | HMI-ALM-08 | The list of carried alarms per priority as not rationalised | Final review (advice) | Planned, WP-S3 |
| CK-ALM-09 | HMI-ALM-09 | Each alarm's label keeps the original's description | Evidence | Planned, WP-S3 |
| CK-ALM-11 | HMI-ALM-11 | Each original on-delay of a tank, instrument or controller limit reaches its delay member | Evidence | Planned, WP-S3 |
| CK-ALM-12 | HMI-ALM-12 | A device with a census acknowledgement member lists `alarmAck` as `write`, bound to it | Design check | Planned, WP-S3 |
| CK-ALM-13 | HMI-ALM-13 | The priority distribution against `priority_distribution` | Final review (advice) | Planned, WP-S3 |
| CK-ALM-14 | HMI-ALM-14 | The deadbands and the on-delays the library cannot hold, with their values | Final review (advice) | Planned, WP-S3 |
| CK-TAG-01 | HMI-TAG-01, 07, 08, HMI-ALM-10 | Each device folder's path below the tag root is its ratified node path; the alarm display path names the same node; the depth is at most `max_levels` | Design check; page build | Planned, WP-S2: a rule of the library's `page_checks.py` over the device model's `hierarchy` and the tag document (NOTE-WFB-15 section 9.7), reported by WP-S3 |
| CK-TAG-02 | HMI-TAG-02, 03 | Folder names are the original's names made safe; no two collide without regard to case in one parent, the folders `values_folder` and `unsourced_folder` included | Design check; page build | Planned, WP-S2: a rule of the library's `page_checks.py` (NOTE-WFB-15 section 9.7), reported by WP-S3 |
| CK-TAG-04 | HMI-TAG-04, 05 | Free tags sit in `values_folder` of their node, unsourced memory tags in `unsourced_folder`; each unsourced tag is on the final review | Page build; final review | Planned, WP-S3 and WP-F7 |
| CK-TAG-06 | HMI-TAG-06 | Every member has a source or is not created | Page build | Partly exists: the library's gate G7 devices and G11 (wiki page 17 section 10 item 13); a reported check planned, WP-S2 |
| CK-UDT-01 | HMI-UDT-01 to 04 | Each device of a kind with a UDT is an instance of a library definition with exactly the device model's members, or a folder where a shape is unmeasured; a local device is a folder | Page build (the build's tag file, expanded as NOTE-WFB-15 states) | Planned, WP-S2: gate G7 devices with `--types-file` (NOTE-WFB-15 section 9.7), since today's G7 does not read instances (wiki page 17 section 10 item 12) |
| CK-UDT-05 | HMI-UDT-05 | Every UDT shape the build writes is one the library's manifest marks measured | Conformance check of NOTE-WFB-15 | Planned, WP-L1 and WP-S2 |
| CK-HIS-01 | HMI-HIS-01, 05 | The kind's trend members are historised; the `trend` list and the history keys agree | Page build (tag model) | Planned, WP-S2: gate G7 devices with `--types-file` reads the expanded members' history keys (NOTE-WFB-15 section 9.7), reported by WP-S3 |
| CK-HIS-02 | HMI-HIS-02 | Every original trend tag is historised and shown, or a gap accepted by name | Evidence | Planned, WP-S3 |
| CK-HIS-03 | HMI-HIS-03 | The named history provider exists on the gateway | Environment check of the migration page | Planned, WP-N5 |

The layout rules L3, L6, L7, L8 and L12 of `check_layout` test the library's own descriptor contract (pipes as flows,
stated orientations and readout positions, the toolbar, pipe ends); they keep running and report under their own
names, outside this standard.

### 11.2 Result of a Check

Each check reports, per rule id, one of `pass`, `fail`, `advice` or `not_applicable`, with the items that failed and
the clause each breaks. A result is placed by NOTE-WFB-14 ruling R4:

1. a `fail` of a `shall` rule found at the design check returns the design to block 18 for another round with a
   defects brief (WFBD-004);
2. a `fail` of a `shall` rule carried by `workflow` or `both`, found by the page build or the evidence on an item of the
   page, is a page item and stops the run;
3. a `fail` of a rule carried by `library` alone is a library item: advice listed on the final review and queued for
   the library;
4. a `fail` of a `should` rule, and every result of a check that runs at the final review only, is `advice`, shown for
   the person's decision.

The design sheet and the final review show every rule's result by id (NOTE-WFB-14 section 8.4 item 4).

## 12. Client Layer

### 12.1 Permitted Changes

A client layer is one JSON file per engagement, of the schema `standards/hmi/client-layer.schema.json` (format
`wfb.hmi.client-layer/1`). It may:

1. set a parameter of any rule, within the type and allowed values of Table 3.5;
2. replace the statement of an overridable rule, with the reason and the client document it comes from;
3. withdraw an overridable rule for the engagement, with the reason;
4. add client rules, with identifiers of the form `CLI-<AREA>-<nn>` and the fields `id`, `level`, `statement`,
   `check`, `carried_by` and `parameters` of section 3.1. A client rule is never fixed, its source is the layer's
   document, and it is a judgement of the design review unless its `check` names a check whose measure decides it; a
   new measure is a register item of this repository.

It cannot change a fixed rule, change an identifier, or change the standard's version it targets.

### 12.2 Resolution

The manager builds the effective standard from this standard's `rules.json` at the version the layer names and the
layer's entries, in that order, and records the result with the run (its digest in the run's record). The design
block reads the effective standard instead of the fourteen principles of the brief; the checks read its parameters
(section 3.5). A layer that names a version other than the standard's current one is refused until it is moved to the
current version (ruling SR6).

### 12.3 Tests Outside the Schema

The schema checks the layer's form. The manager's resolver makes the tests the schema cannot express, and refuses the
layer, naming the entry, when any fails:

1. the layer's `standard_version` equals the standard's version;
2. every `rule` of a `set_parameter`, `replace_statement` or `withdraw` entry names a rule of `rules.json`, and no
   `replace_statement` or `withdraw` names a fixed rule;
3. every `parameter` names a parameter of that rule, and its `value` has the type and an allowed value of Table 3.5;
4. every `document` names an entry of the layer's `documents`;
5. no two entries set the same parameter of the same rule, and no rule is both replaced and withdrawn;
6. a client rule's `check` names a check of Table 11.1, and its identifier is unique in the layer;
7. a withdrawn rule is cited by no rule that stays in the effective standard (for example HMI-TAG-01, which HMI-ALM-10
   cites);
8. `ratified.at` is a date and time of RFC 3339, tested with a format checker.

A layer with no entries is valid and changes nothing.

### 12.4 Location of a Client Layer

By default the client layer sits in the engagement's local folder, `projects/<engagement>/work/hmi/client-layer.json`,
because a client's style guide may name the client (CLAUDE.md non-negotiable 4; ruling SR2). The person states its
entries through the migration page and the manager writes the file (NOTE-WFB-14 principle 5); WP-S3 adds the card.

## 13. Map from Today's Sources

### 13.1 The Fourteen Principles

Table 13.1 maps each principle of the design brief to the rules that now state it, and names what of a principle is
carried by the library rather than by a house rule. The brief's section 3 is replaced by the effective standard in
WP-S3.

Table 13.1. The principles of `project-design.md` section 3 and their rules.

| Principle | Subject | Rules | Carried by the library, or changed |
|---|---|---|---|
| P1 | Keep the original's information, flow and organisation | HMI-DSP-07, HMI-DSP-11, HMI-VIS-01, HMI-NAV-02, HMI-ALM-01, HMI-HIS-02 | None |
| P2 | Navigate by the plant hierarchy | HMI-NAV-01, HMI-DSP-02, HMI-DSP-25 | None |
| P3 | Display levels after ISA-101 | HMI-DSP-01 | None |
| P4 | A muted grey display, colour for abnormal states, redundant coding | HMI-DSP-03, HMI-DSP-04 | Redundant coding is a `should`: the library codes priorities by colour with one badge shape (WFB-339) |
| P5 | Analogue values against their range | HMI-DSP-14 | None |
| P6 | Motion only for unacknowledged alarms; no pipe animation | HMI-DSP-16, HMI-DSP-17 | None |
| P7 | Alarm priorities by the profile's ranking, each with its own colour and shape; Diagnostic without alert colour | HMI-ALM-02, HMI-ALM-04 | Changed: the library maps five priorities onto four alert colours and one badge shape (wiki page 13 section 11.1, wiki page 04 section 7 item 3); "its own colour and shape" is not carried (WFB-339) |
| P8 | A symbol opens its faceplate; a link navigates | HMI-NAV-03 | None |
| P9 | The faceplate's anatomy; docked or floating | HMI-DSP-22 | The anatomy and the dock or float are the library's (wiki page 16 sections 4.1 and 4.2) |
| P10 | Confirmation of commands and setpoints, not of acknowledgement | HMI-DSP-18, HMI-ALM-06 | Changed to the library's behaviour: Ack all is confirmed (wiki page 04 section 8.12) |
| P11 | The library's palettes and icons; a top bar with the most severe alarm, acknowledgement and the count | HMI-DSP-05, HMI-DSP-25 | The top bar is the library's frame (wiki page 04 section 3 Table 2) |
| P12 | Pop-ups are faceplates | HMI-DSP-21 | Narrowed: a pop-up that serves no device is a level 4 page or a gap |
| P13 | Scale, fill, topology, regions, symbols on flows, labels | HMI-DSP-07 to HMI-DSP-11 | None |
| P14 | States in words; units and range bars | HMI-DSP-13, HMI-DSP-14 | None |

### 13.2 The House Decisions

Table 13.2 maps each house decision of the engagement profile to the rule or parameter it becomes, and the decision's
present value to the parameter's allowed value. Decisions that are not display, alarm or tag rules stay decisions of
the profile.

Table 13.2. The house decisions of the profile.

| Decision key | Becomes | Decision value today and the parameter value it maps to |
|---|---|---|
| `priorities_by_rank` | HMI-ALM-02 parameter `priorities_by_rank` | The same object, lower case priority names |
| `popups_as_faceplates` | HMI-DSP-21 parameter | The same boolean |
| `device_symbol_own_page_only` | HMI-DSP-23 (the rule itself) | true is the rule |
| `faceplates_on_plain_symbols` | HMI-DSP-24 parameter | "all" maps to `all` |
| `acknowledge` | HMI-ALM-06 parameter | "selected_and_all_after_confirm" maps to `selected_and_all_after_confirm` |
| `fit` | HMI-DSP-08 parameter | "fill the window, never above 1.0" maps to `fill_never_above_1` |
| `pipe_colour` | HMI-DSP-06 parameter | "by medium; buses grey" maps to `by_medium_buses_grey` |
| `pipe_animation` | HMI-DSP-17 parameter | The same boolean |
| `invented_measurements` | HMI-DSP-15 (fixed; the decision's value false is the rule) | false is the rule |
| `inferred_alarm_priorities` | HMI-ALM-03 parameter | "labelled inferred, shown at the review" maps to `labelled_inferred` |
| `simulation` | Stays a decision; its simulated tags are a test layer outside HMI-DSP-15 (section 5.4) | Unchanged |
| `standing_import_approval`, `module_restart`, `early_reading_review` | Stay decisions of the profile (run and gateway behaviour, not HMI rules) | Unchanged |

The decision keys stay in the profile in this version; each decision's `ref` names its rule id once WP-S3 lands, and
the tracked default house profile of WP-I3 takes its defaults from Table 3.5 (ruling SR5).

## 14. Adoption and Open Items

### 14.1 Adoption

The standard binds a run once WP-S3 (change group G2b) is built. Until then it is a reference for the design notes
NOTE-WFB-15 and NOTE-WFB-16, which cite its rule ids. WP-S3 makes these changes:

1. block 18's brief cites rule ids in place of its section 3 and is given the effective standard; the design's page
   entry gains its display level and the design's alarm entry gains `priority_source`;
2. the profile's `design_standard.library_wiki` lists the library's wiki pages 16, 17 and 18 beside 03, 04, 05 and
   13, the ASMP study stays as evidence under `design_standard.asm`, and the profile gains `target.history_provider`;
3. each check of Table 11.1 marked planned for WP-S3 reports by rule id on the design sheet and the final review;
4. the generator of `rules.json` from this document's tables (Tables 3.5, 5.1 to 10.2 and 11.1), and a test that
   compares the two.

### 14.2 Open Items Raised by This Standard

1. **WFB-338.** The library takes an alarm's display path from the node of the deepest page that draws the device as
   its own drawing (wiki page 13 section 11.3 item 2, wiki page 16 section 8 Table 11), and a device model's `node`
   only for a device no page draws (wiki page 17 section 2.4 Table 1). HMI-DSP-23 places the own drawing on a page of
   the device's ratified node, which keeps the two equal. Open: where the original draws a device's only symbol on a
   page of another node, the design makes that symbol a second drawing; whether the library then takes the device's
   node from the device model's `node` is to be stated by NOTE-WFB-15 and confirmed in the library.
2. **WFB-339.** Two library items: (a) no gate of the library reads the history keys against a device model's `trend`
   list (wiki page 17 section 8 item 2, section 11 item 5), so a trend card can show no data; CK-HIS-01 closes it in
   WorkflowBuilder (WP-S3); (b) the library codes the five priorities by four alert colours and one badge shape, so
   Low, Medium and High differ by colour alone and principle P7's shape per priority is not carried. Both are library
   items for change group G3.

## 15. Owner Rulings

Each ruling of Table 15.1 has a default; work proceeds on the defaults unless the owner says otherwise.

Table 15.1. Owner rulings.

| Ruling | Question | Default |
|---|---|---|
| SR1 | Approve version 0.2 as the house standard, with the fixed rules of section 3.4 | Yes |
| SR2 | Where a client layer lives | Local only, `projects/<engagement>/work/hmi/client-layer.json`; a client layer with no client name may be tracked under `projects/<engagement>/contracts/` at the owner's choice |
| SR3 | The depth of the node path above the device folder | At most two levels, area and unit (`max_levels` 2) |
| SR4 | The folder names for free tags and unsourced memory tags | `Values` and `Unsourced` (HMI-TAG-04, HMI-TAG-05) |
| SR5 | The house decisions become rules and parameters (Table 13.2), with the decision keys kept in the profile for this version | Yes |
| SR6 | A client layer names the standard version it was written for and is refused on another version until moved | Yes |
| SR7 | ISA-101, ISA-18.2 and EEMUA 191 are cited by topic, since their texts are not held in the portfolio; clause numbers are added when the owner supplies the texts | Cite by topic |
| SR8 | The priority distribution of HMI-ALM-13 is advice only, never blocking | Yes |
| SR9 | A project whose plant has areas is built with an ASM frame (HMI-DSP-25) | Yes |
| SR10 | Principle P7's shape per priority is dropped from the house rules until the library offers one (WFB-339) | Yes |

## 16. References

1. ANSI/ISA-101.01-2015, Human Machine Interfaces for Process Automation Systems. Not held in the portfolio; cited by
   topic (ruling SR7).
2. ANSI/ISA-18.2-2016, Management of Alarm Systems for the Process Industries. Not held in the portfolio; cited by
   topic (ruling SR7).
3. EEMUA Publication 191, Alarm Systems: A Guide to Design, Management and Procurement. Not held in the portfolio;
   cited by topic (ruling SR7).
4. ASMP-REPORT-01 revision A, Assessment Report: Study of the ASMP Ignition Project, 2026-10-22,
   `F:\repos\Ignition-ASM-Primary\docs\REPORT-ASMP-01-study.md`, sections 5.1 to 5.9, 6 and 8.2; the study wiki pages
   `B1/udt-design.md`, `B2/alarm-configuration.md`, `B3/alarm-display.md`, `B5/navigation-and-hierarchy.md`.
5. `src/workflows/briefs/v3/project-design.md` section 3, the fourteen principles (WorkflowBuilder `9cb3696`).
6. The library's wiki at Cadre-Sandbox-OpenBridge `506076c` (cloud `dd1958d`): page 04 (navigation and frame) sections
   3, 7, 8.6 and 8.12; page 13 (faceplates, alarm lists and interlocks) sections 8, 10.5 and 11; page 16 (component
   selection guide, COB-WIKI-16 revision B) sections 3 to 11; page 17 (tag model and UDTs, COB-WIKI-17 revision B)
   sections 2, 3, 5, 7, 8, 10 and 11; `tools/hmi/page_checks.py` (`check_coverage`, `check_navigation`, `resolves`,
   `built_tags`, `check_layout` and its rules L1 to L12).
7. The library's decision COBD-035 (writes under `_types_` on the owner's gateway) and gateway fact GF-11.
8. NOTE-WFB-14 revision 0.3, Gaps Found by the Recorded One-Page Migration and the Plan to Close Them (WFBD-146):
   principles 1, 2, 5 and 8, rulings R3, R4 and R8, packages WP-S1 to WP-S3, WP-F1 to WP-F7, WP-I3, WP-N5, WP-R1.
9. NOTE-WFB-15, the library contract (the visibility measure, the artwork element, the manifest and the UDT build),
   and NOTE-WFB-16, classification for any Citect project (the node of each device), both revision 0.1 of 2026-11-07.
10. The engagement profile schema `src/wfb_blocks/migration/schemas/wfb.migration.profile-1.json` (`decisions`,
    `design_standard`, `target.tag_root`, `target.build_options`); `src/wfb_blocks/migration/navtable.py`.
11. Register items WFB-293, WFB-308, WFB-313, WFB-323, WFB-325, WFB-338, WFB-339; decisions WFBD-004, WFBD-146.
