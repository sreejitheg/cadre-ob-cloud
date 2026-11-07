# NOTE-WFB-14: Gaps Found by the Recorded One-Page Migration and the Plan to Close Them, Gap Analysis and Plan

| Item | Value |
|---|---|
| Document ID | NOTE-WFB-14 |
| Revision | 0.3 |
| Status | Approved by the owner on 2026-11-07 (WFBD-146): R1 to R11 at their defaults, R12 a second parent `cadre_hmi_base_asm_080` (deployed); the groups run autonomously, in sub-sessions where fit |
| Issued | 2026-11-06 |
| Author | The demo support session (Opus 5.5) |
| Approver | The owner |
| Register | New: WFB-313 to WFB-325 (section 9). Planned here as well: WFB-293, WFB-298, WFB-301, WFB-303, WFB-305, WFB-307, WFB-308, WFB-310, WFB-312, WFB-294 |
| Decisions | WFBD-146 on approval (section 10); reopens NOTE-WFB-13 Table 3.1 option B |
| Basis | WorkflowBuilder main at `b4bf10a`; Cadre-Sandbox-OpenBridge main at `9727312`; Citect-Ignition-Migrator main at `0931236`; cadre-ob-cloud main at `e172346` for revisions 0.1 and 0.2, at `dd1958d` (the port of tranche T3 merged) for revision 0.3; the eng04 step 3 run `20261105T145504Z-1f76`, its rerun `20261105T164103Z-61af` and page child `20261105T164137Z-229d` (local) |

The revisions of this document are listed below.

| Rev | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-11-06 | Demo support session | First draft: the losses of the recorded run traced to their stage, the ties to one project, the steps outside the migration page, seven root causes, principles, a phased plan and the owner's rulings |
| 0.2 | 2026-11-06 | Demo support session | The owner's second request: where the design rules live today (section 4.6) and how the library is bound (section 4.7); a switchable library (WP-L1, WP-L2) and an HMI standard for screens, alarms, tag structure and UDTs (WP-S1 to WP-S3); the packages set in five change groups with three live runs in all (section 8.2); rulings R7 to R9 |
| 0.3 | 2026-11-07 | Demo support session | The cloud port merged (`cloud/REPORT-T3.md`, cadre-ob-cloud `dd1958d`): section 4.6 corrected, since the one library line now states a component selection guide (page 16) and a tag model with one UDT per kind (page 17); WP-S1 and WP-S2 narrowed to what the library does not state; WP-0 done; WP-0b added (the Sandbox follows the cloud line on this PC, with the parent comparison of the pre-flight and the parent on the gateway); the report's open items placed in packages; rulings R10 to R12 |

Conventions: no client, site, project, page or tag name appears in this document. "The pilot" is the one Citect
project of eng02, eng03 and eng04. Its three pages of the recorded run are called the electrical overview page, the
well page and the generator page. Stages A to C and steps 1 to 3 are those of NOTE-WFB-11 section 6.1; block numbers
are those of NOTE-WFB-06 Table 4.3. "Understanding", "device model", "design", "descriptor" and "renderer" name the
five stages an item of the original passes through in step 3 (blocks 13, 17, 18, 24 and the library's generator).

## 1. Purpose and Scope

### 1.1 The Request

On 2026-11-06, after the recorded run of eng04 passed blocks 1 to 30, the owner asked for every issue of the run to be
checked and a plan made to fix each at its cause, with three requirements:

1. a new, clean project is created from the migration page, with no command;
2. the workflow is never limited to, or dependent on, one particular project;
3. the gaps are identified and closed, not patched.

The owner gave two examples: the tank of the well page lost its boundary, and the fuses and fault current limiters of
the electrical overview page keep their text but lose their symbol. The pilot's pages are not to be fixed now.

On the same day, after revision 0.1, the owner added four points:

1. the library is being fixed in the cloud session as planned, so the library must be switchable;
2. a set of rules is needed for SCADA screen design, tag grouping, UDTs and the like: where they are defined today,
   and, where they are not, a package in the plan;
3. the owner waits for the library work to complete, so that it is incorporated in this plan;
4. the changes are made in groups, runs are made only where necessary, since each run costs time and tokens, and
   nothing starts before the owner's go.

### 1.2 Scope

In scope: the causes of what the run lost, the ties of the workflow to the pilot, the steps a new project needs outside
the migration page, and the plan. Out of scope: building any fix, and the library 0.8.0 port, which has its own prompt
(`workspace/progress/prompt-port-sandbox-to-cloud.md` revision 2) and appears here only as a precondition.

## 2. Sources

1. The rehearsal record `workspace/progress/rehearsal-2026-11-05.md`, sections 3 and 8 to 11.
2. The recorded run's files: the original pictures, the understandings, the device model, the approved design, the
   descriptors, the built pictures, the evidence of both passes and the visual review of both passes.
3. Two read-only sweeps on Sonnet 5.5: the trace of every lost element of the three pages (each picture of the
   original against the built page, each item traced through the five stages), and the sweep of every tie to one
   project in the tracked code, the workflows, the briefs, ctig's site profiles and the set-up path.
4. The checks made by this session on the sweeps' key claims: the library's section style
   (`tools/hmi/library.py`, class `cadre/surface/section`: a fill and a corner radius, no border), the well part
   (`tools/hmi/parts.py`, `well_node`: two fill paths, no outline), the device model's catalogue (holds `tank`, holds
   no `fuse`), the gap list of block `gaps` (the kinds of the design's chosen components only), and the evidence
   block's setting `fail_on_items: false` (`src/workflows/screen-page-build-v3.json`).
5. The register rows WFB-293 to WFB-312.

## 3. Findings: What the Recorded Run Lost

### 3.1 The Owner's Two Examples

Table 3.1 traces both examples through the five stages.

| Stage | The well page's tank | The electrical overview page's fuses and limiters |
|---|---|---|
| Understanding | A device of type `wet-well`, with its box on the page | Two devices of type `fuse`, with their boxes |
| Device model | Kind `tank`, a kind of the catalogue | Kind `fuse`, not a kind of the catalogue |
| Design | Overrides the kind with the `well` part and writes a gap row claiming "the catalogue holds no kind", which is false; the row is closed | Maps each to a `section` titled with its label; gap row open, "needed: an in-line fuse symbol" |
| Descriptor | A `wells` entry with four level marks | Two `sections` entries |
| Renderer | `well_node` draws the liquid only, never the walls; with no live mark it draws a grey band at the floor | A section has the page's own fill and no border, so only the label shows |
| Result | No vessel; a band and four lamps | The text without a symbol |

Neither loss stopped a gate (section 3.3).

### 3.2 The Count Over the Three Pages

The trace found 28 items of the original missing, invisible or materially changed. Table 3.2 groups them by cause.

| Cause | Items | Examples |
|---|---|---|
| The library lacks the kind, and the stand-in draws nothing visible | 7 | Protective devices, motor starters, UPS panels, the power monitor panel, the duty selector panel, breakers and the transfer switch drawn as plain switch icons |
| A section used as a box for static artwork; a section draws no border | 4 | A generator status box, a bus status box, a source box, a panel border and status strip |
| A library part incomplete or stylised | 5 | The well's walls, section titles as small right-aligned captions instead of heading bands, pipes grey unless colour mode is on, the generator picture, the motor glyph |
| A library feature lacking, declared as a gap | 5 | A status badge beside instrument and pump labels, a threshold lamp, PLC state lamps, a button's state colour, a generator state text |
| The device model's kind approximate | 2 | Starters classed as motors, an actuator as a valve |
| A design claim not checked against the catalogue | 1 | The well |
| Lost between the understanding and the descriptor, with no gap | 3 | A caption, the labels of three generator readouts, a pump state icon row |
| A deliberate design choice | 1 | Cell borders absorbed into tables |

Of the 169 mapping rows of the pop-ups built as faceplates, 82 carry a gap: run time and start tables, current and load
tables, setpoint tables, command pulses, and tabs the design listed but the faceplate does not show.

### 3.3 Why Every Gate Passed

1. **Coverage counts presence.** A row is covered when an element of the named kind and id exists in the descriptor,
   or the row is in a gap (library `tools/hmi/page_checks.py`, `check_coverage`). Whether the element draws anything
   is not tested, so the invisible section and the wall-less well count as drawn.
2. **The design check trusts the gap rows.** Block 18 accepts any gap id for a device without a catalogue kind
   (`src/wfb_blocks/migration/project_design.py`, `placed`); it never compares a row's claim about the library with
   the catalogue it was given.
3. **The gap list counts the design's choices, not the original's needs.** Block `gaps` resolves the kinds of the
   components the design chose. A design that draws a missing kind as a `section` leaves no open kind, so no local
   assembly is licensed (NOTE-WFB-10 section 9.4) and nothing is queued for the library. Stage B had already reported
   "nothing to build", because stage A's survey reads ctig's census of genies and symbols, which never sees equipment
   drawn as plain shapes.
4. **The render gates test errors and layout.** G8 counts quality overlays and error badges; L1 to L12 test clipping,
   overlap, alignment and pipe ends. None tests that a box or a symbol is visible.
5. **Failed evidence does not stop a run.** The evidence block runs with `fail_on_items: false`: both passes reported
   14 failed items (7 of the page, 5 of the library, 2 of a tool) and the run passed. One of the 14, offline coverage,
   reads 157 of 191 on every run because its rows and the design key static artwork differently, so it carries no
   signal.
6. **The visual review is advice and partly blind.** It sees reduced pictures, is told that presence is measured
   elsewhere, and is given neither the gap list nor the catalogue. It reported the well as a "shallow band" (medium)
   and did not report the fuses, the invisible panels or the status badges.

### 3.4 Other Defects of the Rehearsal and the Recorded Run

Table 3.4 lists the remaining defects; the first eight are registered.

| Defect | Register |
|---|---|
| The trends route the design names is not generated ("View Not Found") | WFB-293 |
| The tracked page build workflow shows a problem in the manager (block `fix`, `settings.build`) | WFB-298 |
| The migration page's check passes a file input that the start refuses by rule 5 | WFB-301 |
| The check passes a closure holding windows that are neither in the project nor substituted | WFB-305 |
| Block 18 passes a design that block 24 then refuses (untagged value components) | WFB-307 |
| A bind to an invented memory tag, or a constant expression over a real tag, counts as bound | WFB-308 |
| The design sheet's pictures do not load from the migration page | WFB-310 |
| The page builder names its pages by descriptor path and loses a round each pass | WFB-312 |
| A sequence's commands and setpoint built as memory tags while the census holds the original's command tags; a bind to a tag name no table holds passed | WFB-323 (new) |
| The contained build mode's default of 300 turns is reached on three pages with their pop-ups | WFB-322 (new) |
| No check of the 5-hour usage window before step 3's model stages; a round can be cut by the limit | WFB-322 (new) |
| The final review needs a decision on every page, unbuilt stubs included, before Approve all | WFB-322 (new) |
| The design sheet shows the first pass's redraw, not the redraw after the return pass | WFB-322 (new) |
| Library evidence items: alarm rows absent after a one-tag import, the alarm list and its acknowledgement; tool items: search and zoom time-outs | Library register, through WP-F5 |

## 4. Findings: What Ties the Workflow to One Project

### 4.1 Classification Knowledge

The tracked code, workflows and briefs carry no name of the pilot. The knowledge that classes a Citect project's
templates and tags, however, exists only for the pilot:

1. ctig's base site profile holds no census section;
2. the only census is the pilot's tracked site profile in ctig, about 165 rules (81 stem rules, 27 template rules, 18
   signature rules, 9 member roles, 7 pop-up rules and others), with about 10 template rules and 45 waivers that eng02
   ratified by hand in three local layers;
3. eng03 and eng04 ran on that knowledge, carried because their backup was the pilot's, byte for byte (WFB-302);
4. a different project starts with none, and the mapping stage that should propose it failed to converge in three
   rounds on 42 unclassed templates (WFB-303).

This is the strongest tie to one project.

### 4.2 Missing Pop-ups

A pop-up the project calls but does not hold needs a stand-in in the base profile's `scope.substitutes`, written by
hand (WFB-305); `--like` carries them only for the same backup (WFB-304).

### 4.3 Host Values Copied from an Earlier Engagement

`wfb engagement new` copies the gateway, the library pin and reference commit, the accepted differences, the build
options, the parent project, the connections and the house decisions from the `--like` engagement. A host with no
earlier engagement has nothing to copy, and a new client's owner never sees the house decisions, which block 3 asks
only when a value is null.

### 4.4 Host Paths in a Tracked Workflow

The tracked page build workflow names command lines under `F:/repos/` for ctig and the library
(`src/workflows/screen-page-build-v3.json`, lines 66 to 68 and 94 to 96), where every other block takes its tool
repository from the manager's settings.

### 4.5 Other Ties

1. **The design standard.** The design is given the alarm management study as the pilot's exercise applied it; whether
   the study is general is not yet confirmed. The client style guide input is empty for every project, and nothing
   supplies it.
2. **Fixed names.** The parent project default, the child prefix and the six workflow ids are the target library's
   and are acceptable as the product's target, provided they come from the profile.
3. **Constants set on a six-page pilot.** The rounds per block, the build's 300 turns and the review wait of 7,500 s
   are unmeasured on a larger project.
4. **The client-term guard** is as strong as the terms the person types; the backup itself is not scanned.

### 4.6 Where the Design Rules Live Today

No single rulebook for screen design, tag structure or UDTs exists. The rules a run applies are spread over five
places, none versioned as a standard or approved as one:

1. **Screen design:** fourteen principles inside the design brief (`src/workflows/briefs/v3/project-design.md`
   section 3), introduced as coming "from the alarm management study as the exercise applied it". The design model
   restates them in each design, so they can drift from run to run, and only the few that a check tests are enforced.
2. **The design standard input:** the study of one existing Ignition project (`F:/repos/Ignition-ASM-Primary`, its
   report and four wiki pages). It describes how that project is built; it is not a set of rules.
3. **The library's wiki pages** 03, 04, 05 and 13 (design system, navigation and frame, catalogue, faceplates), given
   to the design as the library's own rules.
4. **The house decisions** of the profile (alarm priorities by rank, simulation, pipe colour and animation, fit and
   others), copied from the like engagement (section 4.3).
5. **The client style guide input,** empty for every project.

**Tag grouping.** The library's device contract gives each device a tag folder under the child project's tag root,
with members named per kind (library wiki 06 Table 5, `library/profile.json`), and the pilot's bridge rules in ctig
map the original tags to those members. Tags of no device (a page's free readouts, the memory tags of a gap) are placed
by the page builder under no rule. No rule groups the folders by the plant hierarchy, names them or sets the provider.

**UDTs.** None in the target. The target project holds folders and atomic tags only (the build's `tags.json`, the
library's generator). The study's UDT design page describes the 34 UDT families of the studied project and their fit
to the library's device contract.

**The library line since 2026-11-06 (revision 0.3).** The cloud line, now the one library line, states two of these
rule sets on its own pages, which the Sandbox at `9727312` lacks and the workflow does not yet read (the profiles name
pages 03, 04, 05 and 13 only):

1. page 16, the component selection guide: the rendering, the frame, the faceplate style and place, the page layout,
   the kind of a plant object, the module-only kinds, the instrument presentation, the page parts, ownership and
   interlocks;
2. page 17, the tag model: a device is a tag folder `<tagRoot>/<id>` with its members (and the subfolders `mnt/`,
   `cfg/`, `ilk/`), one recommended UDT per kind (`Cadre/Pump`, `Cadre/Valve` and others, definitions under the
   provider's `_types_` folder), the members of each kind with type, access, write path, alarms and history, and the
   interlock structures. The UDT shapes are marked unmeasured until a gateway run, the library reads folders and never
   a UDT name, and the device path is flat under the tag root: no rule groups devices by the plant hierarchy.

What remains missing is the house layer above the library (the display and alarm philosophies, the tag hierarchy and
naming above the device folder, the choice to adopt UDTs), a target build that writes UDT definitions and instances,
and checks by rule id.

### 4.7 How the Library Is Bound

1. The manager knows one library: the tool repository `openbridge`, one path in the settings
   (`tool_repositories`), which about 70 places in the block library read.
2. An engagement pins that checkout's commit, and the pre-flight refuses a run whose checkout has moved; a commit in
   the library during a run fails the run, which is why no library work may go on while a run is live.
3. The profile carries library facts copied from the like engagement: the repository path, the reference commit, the
   accepted differences, the parent project's name, the build options (frame, faceplate style, rendering) and the
   paths of the library's wiki pages.
4. The tracked page build workflow names the library's path (section 4.4).
5. The module on the gateway is installed by hand, and nothing checks that it is the version the pinned library
   expects.

A second library line (cadre-ob-cloud with module 0.8.0) therefore cannot be chosen per engagement: a switch means
moving the one checkout and refreshing every engagement. The library is not yet a drop-in replacement.

## 5. Findings: What a New Project Needs Outside the Migration Page

Table 5.1 lists each step a new project needs today and what it could be.

| Step today | Could be |
|---|---|
| The command `wfb engagement new` in PowerShell | A button: the manager runs the same code in process |
| Name, backup path, Citect project name, include folder, client terms, like engagement typed as arguments | Fields of a form; the projects and include projects read from the backup (not built); client terms proposed from the project's register for the person to tick (not built) |
| Census rules for a project that is not the pilot: hand-made layers | Proposals ratified on a card; the manager writes the engagement's layer |
| Substitutes for missing pop-ups: a hand edit of the profile | A card listing each missing window with its choices; the manager writes the profile |
| After a library change: `wfb engagement refresh` | A button, then steps 1 and 2 again from the page |
| Graphics Builder open on the project, the Citect runtime started before step 3's Start, the desktop unlocked, the gateway module active, client consent | Stay a person's actions; the check names each with its fix |

NOTE-WFB-13 section 3 chose the command over a form (option B rejected: the migration page writes no inputs, profile,
setting or workflow, NOTE-WFB-11 section 5.4). The owner's request reopens that choice (ruling R1).

## 6. Root Causes

1. **RC1. Knowledge found late flows nowhere.** Equipment found only by the understanding (drawn as plain shapes,
   not genies) reaches neither the survey nor the gap list, and arrives after the library release of stage B; the
   design then turns a missing kind into a neutral element. Seven items of Table 3.2.
2. **RC2. Model claims pass unchecked against facts the run holds.** The design's claim about the catalogue was false;
   the same family holds WFB-307 (a design choice the build later refuses), WFB-308 (binds that only look bound) and
   WFB-323 (commands bound to memory tags while the census holds the real ones).
3. **RC3. Stand-ins draw nothing.** The library's neutral elements render without an outline, and the brief's rule
   "draw the nearest honest library part" does not require the stand-in to show the original's shape where it stood.
   Eleven items of Table 3.2.
4. **RC4. Gates measure presence, not what the operator sees,** and failed evidence items do not stop a run.
5. **RC5. Per-project knowledge is authored by hand in files:** census rules, substitutes, bridge rules and house
   decisions.
6. **RC6. A new project is set up by a command that copies an earlier engagement.**
7. **RC7. Two library lines (WFB-294).** A library fix made today would have to be made twice.
8. **RC8. No governed standard.** The rules for screens, alarms, tag structure and UDTs are spread over a prompt, a
   study of one project, the library's wiki and copied decisions; nothing states them once, versions them or checks
   them by id. The library line's own tag model (page 17, one UDT per kind) is not read by the workflow, the target
   writes no UDT, and the tag hierarchy above the device folder has no rule.
9. **RC9. The library is bound as one checkout, not through a declared interface,** so it cannot be switched per
   engagement and is not a drop-in replacement.

## 7. Principles of the Fix

1. **Nothing the original shows disappears silently.** Every understanding entry with a place on the page is drawn
   visibly at that place, by a library kind, a local assembly or the original's own geometry in a neutral style;
   otherwise it is a gap the person accepts by name at the design review.
2. **A model's claim is checked before it is used.** A claim about the library, the tags or the pages is checked
   against the facts the run holds (the catalogue, the census, the understandings).
3. **One check, two callers.** Every check a later block applies to a design choice is applied when the choice is
   made, by the same function.
4. **Knowledge flows back.** A kind the library lacks becomes an open gap of the run, drawn locally, and a queued
   library item; a rule a person ratifies is written by the manager to the engagement's layer.
5. **The person decides in the page; the manager writes the files.** No hand edit and no command.
6. **General only when proven general.** A change is proven on a Citect project that is not the pilot before it is
   called general.
7. **One library line before any library fix.**
8. **One standard.** The HMI rules (screens, alarms, tag structure, UDTs, history) are stated once, versioned and
   approved by the owner, with a client layer that overrides them by rule id; the briefs cite rule ids, and every rule
   that can be checked is checked.
9. **The library is chosen, not assumed.** Each engagement names a library and its commit; the workflow reads only
   what the library declares in its manifest, so any library that meets the interface is a drop-in replacement.

## 8. Plan

### 8.1 Work Packages

Table 8.1 lists the packages by phase. Sizes: S is one builder session of under an hour, M two or three, L more.

| Id | Package | Repositories | Closes | Size |
|---|---|---|---|---|
| WP-0 | One library line: the port prompt revision 2 on cadre-ob-cloud | Library | WFB-294 (cloud side) | Done 2026-11-06: tranche T3 merged at `dd1958d`, 1,817 tests passing, every verification item of the prompt passed (`cloud/REPORT-T3.md`) |
| WP-0b | The Sandbox follows the cloud line on this PC: a one-time merge of the two unrelated histories that takes the cloud's tree for the library paths (`tools/`, `library/`, `schemas/`, `module/`, `wiki/`, `tests/`, `catalogue/`, `screens/`, `build/`, `CONFIGURATION.md`) and keeps the Sandbox's own records, after which each later follow is a plain merge; then the library suite on Windows, `wfb check`, the pre-flight's parent comparison run offline, the parent redeployed on the owner's gateway (delete before import, GF-118) and each engagement's reference commit moved by `wfb engagement refresh` | Library (Sandbox), WorkflowBuilder | WFB-294 | Done 2026-11-07 up to the gateway: Sandbox `main` at `01ac62e` (merge `9e536ce`, COB-213); the library suite on Windows and `wfb check` green; the parent comparison replayed offline (the old pin gives the 17 accepted differences, the merge 188 of 325 files, 175 not accepted). The parent's redeploy and the refresh wait for R12 |
| WP-L1 | Library interface: a manifest the library publishes (catalogue, descriptor schema, library profile, generator command lines, wiki pages for the design, parent project, build options, module id and version, the rules of the standard it implements), and a conformance check run before a library or a commit is accepted. It takes in the report's map proposal (the placement reads the module-only kinds, `cloud/import/MAP-PROPOSAL.md`) and its item R8 (the generator's tables read from `module/components.json`) | Library, WorkflowBuilder | WFB-324 | M |
| WP-L2 | Library choice per engagement: the manager keeps a list of libraries; each engagement names one and its commit; a run reads a pinned read-only worktree of that commit under the workspace, so a development commit never fails a run; the blocks resolve the library through the engagement instead of the single `openbridge` setting; the migration page shows the library and offers a switch, which refreshes the engagement and runs steps 1 and 2 again; the check compares the gateway's module version with the manifest | WorkflowBuilder, editor | WFB-324, WFB-320 | M |
| WP-S1 | The HMI standard: a tracked, versioned rulebook approved by the owner for the house layer the library does not state: the display philosophy (display levels, colour, layout, text, navigation, alarm display, the visibility rule of principle 1), the alarm philosophy (priorities, states, acknowledgement, shelving), the tag hierarchy and naming above the device folder, the choice of UDTs, and history and trends. It cites the library's pages 16 (component selection) and 17 (tag model) by section instead of restating them. Each rule has an id, its source (ISA-101, ISA-18.2, the study, the library) and, where it can be checked, its check; a client layer overrides by rule id; the briefs and the profiles' wiki lists cite rule ids and pages 16 to 18 | WorkflowBuilder (`standards/hmi/`) | WFB-325 | M |
| WP-S2 | UDTs and tag structure in the target: the shapes of page 17 measured on the cloud gateway; the build writes the `_types_` definitions and the device instances (on the owner's gateway with the owner's authorisation, COBD-035) in folders by plant hierarchy; ctig's bridge maps the original tags to the members; the faceplates read the same members, as today | Library, ctig, WorkflowBuilder | WFB-325 | M |
| WP-S3 | The standard enforced: the checkable rules run by id in block 18's check, the page build's checks and the evidence; the design sheet and the final review show each rule's result | WorkflowBuilder | WFB-325 | M |
| WP-F1 | Visible drawing gate: the render capture measures, for each coverage row with a source box, the element's rendered box and whether it shows a border, a fill unlike its container, text or a symbol; an empty or invisible element fails the row. Offline coverage keyed as the design keys. Page evidence items fail the run; library and tool items stay advice and are listed on the final review | WorkflowBuilder, library (`page_checks`, capture) | WFB-316 | M |
| WP-F2 | Artwork element: a descriptor element that redraws the original's static artwork and unclassed equipment from the captured geometry (rectangles, lines, polylines, ellipses) at the original's place and size, in a neutral style; a section used as a box draws a border, and a section title can be a heading band | Library, design and page build briefs | WFB-314 | M |
| WP-F3 | Late kinds become run gaps: the gap list reads the device model's kinds and the design's gap rows as well as the chosen components; a kind with no part is an open gap placed `local` (a local assembly, or the artwork element of WP-F2) and is queued for the next survey; stage A's survey reads the understanding's equipment once a step 3 has run | WorkflowBuilder | WFB-315 | M |
| WP-F4 | Design claims checked: block 18 refuses a gap row claiming no kind where the device model's kind is a catalogue kind, a component block 24 will refuse (by calling block 24's own functions), and an entry with a box mapped to an element that draws nothing | WorkflowBuilder | WFB-313, WFB-307 | S |
| WP-F5 | Library parts: the well draws its vessel; a tank with discrete level marks; protective devices (fuse, limiter, breaker with state) for single-line pages; a starter box; a status badge; a threshold lamp; the alarm list and acknowledgement items of the evidence | Library, after WP-0 | WFB-314 (library part) | L |
| WP-F6 | Visual review as a check: given the gap list, the understanding's equipment and full-size pictures, it answers each item of the original as visible, missing or changed; a missing item is a page item that returns the page | WorkflowBuilder | WFB-317 | S |
| WP-F7 | Binds resolve to the census: a bind names a tag the tables hold or a memory tag a design gap declares; a constant expression over a tag is refused; a command member binds to the census's command tag where one exists | WorkflowBuilder, library (`page_checks.resolves`) | WFB-308, WFB-323 | S |
| WP-I1 | Classification for any project: generic rules in ctig's base profile from Citect's standard libraries and naming patterns, measured by how much of the pilot's ratified census they reproduce; the mapping stage in batches per template family; a card that ratifies the proposals; the manager writes the engagement's layer | ctig, WorkflowBuilder | WFB-303, WFB-318 | L |
| WP-I2 | Missing pop-ups on a card: step 1 lists each called window the project lacks; the card offers a stand-in made from the caller's census tags, a design-time picture, or "not migrated" with a reason; the manager writes `scope.substitutes`; the check runs block 5's closure | WorkflowBuilder | WFB-305 | M |
| WP-I3 | Host profile: the host values kept once in the manager's settings and set by a first-run form; the house decisions from a tracked default house profile, shown for confirmation on a new client's first card; `--like` optional, only to carry a client's ratified census | WorkflowBuilder | WFB-319 | M |
| WP-I4 | No host paths in tracked workflows: the page build workflow's command lines from the tool repository settings; its `fix` problem mended on the way | WorkflowBuilder | WFB-320, WFB-298 | S |
| WP-I5 | Limits by size and usage: the build's turn limit and rounds scale with the pages and entries in scope; a usage window check before step 3's model stages, with a warning and an offer to wait | WorkflowBuilder, editor | WFB-322 (part) | S |
| WP-N1 | Engagement service: `engagement.py` split into a plan returned as data and a commit; routes for both; the command becomes a client of them | WorkflowBuilder | WFB-321 (part) | M |
| WP-N2 | Backup reader: the Citect projects and include projects inside a backup listed, and client terms proposed from the project's register for the person to tick | ctig, WorkflowBuilder | WFB-321 (part) | M |
| WP-N3 | New project panel: pick a backup on this PC or upload it, then name, project, include projects, terms and connection; the plan shown; one confirmation; step 1 ready. A threat review of the write surface first (NOTE-WFB-13 Table 3.1 option B) | Editor, WorkflowBuilder | WFB-321 | M |
| WP-N4 | Library update from the page: a banner when the library moved, and one button that refreshes the engagement and runs steps 1 and 2 again | WorkflowBuilder, editor | WFB-321 (part) | S |
| WP-N5 | Environment guidance: the check names Graphics Builder, the Citect runtime, the desktop lock and the gateway module with their fix text, and shows the usage window | WorkflowBuilder, editor | WFB-322 (part), WFB-301 | S |
| WP-R1 | Run defects folded into the package that touches the same files: the page list naming (WFB-312), the design sheet's pictures (WFB-310) and its redraw after the return pass, the trends route (WFB-293), unbuilt stub pages decided by default at the final review, the check's rule 5 (WFB-301, its harness given a temporary repository root) | WorkflowBuilder, editor | WFB-293, WFB-301, WFB-310, WFB-312, WFB-322 (part) | S each |
| WP-P1 | Proof on a second project: a Citect project that is not the pilot, set up and run from the migration page only, then the pilot's three pages again | None (a run) | Closes the note | M |

### 8.2 Change Groups and Runs

The owner directed on 2026-11-06 that the changes are made in groups, that runs are made only where necessary, and
that nothing starts before the owner's go. The library work of the cloud session (WP-0) completes first and is
incorporated. Table 8.2 sets the groups in their order.

| Group | Packages | Waits for | Proven by | Live runs |
|---|---|---|---|---|
| G0 The library on this PC | WP-0b | The owner's go (WP-0 is done) | The library suite on Windows; `wfb check`; the pre-flight's parent comparison offline; the parent's import checked on the gateway (G8 of a known page, no run) | None |
| G1 Contracts | Two Fable notes: the library contract (WP-L1, WP-S2, the visibility measure of WP-F1, the artwork element of WP-F2) and classification for any project (WP-I1). The HMI standard WP-S1, drafted for the owner's approval | The owner's go; WP-0 merged, for the library contract | The owner's approval of the two notes and the standard | None |
| G2 WorkflowBuilder checks and flow | WP-F1 (WorkflowBuilder side), WP-F3, WP-F4, WP-F6, WP-F7, WP-I4, WP-L2, WP-S3, WP-R1 | G1 | Tests written first; the new checks replayed offline on the recorded run's files (the design check refuses the false tank claim, the gap list holds the fuse kind open, the coverage keys agree) | None |
| G3 Library | WP-L1, the measure of WP-F1, WP-F2, WP-F5, WP-S2 (library side) | G1; WP-0 merged | The library's own gates and tests on the one library line, through a prompt for a library session | None |
| G4 New project and independence | WP-N1 to WP-N5, WP-I1, WP-I2, WP-I3, WP-I5 | G1 for WP-I1; runs beside G2 and G3, on other files | Tests; a dry run of the New project panel on a throwaway manager with no run started; WP-I1 replayed offline on the pilot's census | One step 1 on the proof project (about 6 min with the mapping stage's model calls) |
| G5 Proof | WP-P1 | G2, G3, G4 | Section 8.4 | Two: the proof project, steps 1 to 3 on one page; then the pilot's three pages |

Three live runs are made in all: one step 1 at the end of G4 and the two runs of G5. A defect a group finds is fixed
and replayed offline on the run files that showed it, never proven by a new live run. WP-F1 lands first within G2 and
G3: it turns every silent loss into a failed item, which then measures WP-F2 to WP-F5. Each group ends with `wfb
check` green, one adversarial review and one commit set.

### 8.3 Models and Effort

1. **Fable 5.1, extra high effort (`wfb-architect`), for two design notes only,** where a wrong contract between
   repositories costs whole runs: the library contract (the manifest of WP-L1, the UDTs of WP-S2, the visibility
   measure of WP-F1 and the artwork element of WP-F2), and classification without hand-made rules (WP-I1, across
   ctig and WorkflowBuilder).
2. **Opus 5.5, high effort,** for the HMI standard (WP-S1, drafted by the orchestrating session from the principles,
   ISA-101, ISA-18.2, the study and the library's wiki), the other package designs (WP-F3's gap flow among them) and
   one adversarial review per group (`wfb-reviewer`).
3. **Sonnet 5.5, high effort,** for the builders (`wfb-block-builder`, `wfb-engine-builder`, `wfb-ui-builder`) and
   the testers.
4. **Haiku 4.5** for the dash, arrow and term scans.

### 8.4 Acceptance

1. A Citect project that is not the pilot is set up from the migration page with no command and no hand edit; step 1
   classes every template after one ratification card; step 2 builds or queues every missing kind; step 3 of one page
   passes with WP-F1 and WP-F6 blocking.
2. The pilot's three pages run again: the well's vessel, the fuses, the limiters, the starters and the panels are
   visible; every item of Table 3.2 is drawn or is a gap the person accepted by name.
3. An engagement switches between two libraries, or two commits of one, from the migration page with no edit, and
   its runs read the chosen one; a library commit made during a run does not fail it.
4. Every checkable rule of the HMI standard reports by id on the design sheet and the final review; the target
   project's devices are UDT instances in folders by plant hierarchy.
5. `wfb check` green; each package's tests written first.

## 9. Register Items

Table 9.1 lists the new register items; each is recorded in `REGISTER.md` with this note's revision 0.1.

| Id | Item | Package |
|---|---|---|
| WFB-313 | A design gap row's claim about the library is not checked against the catalogue (the well page's tank) | WP-F4 |
| WFB-314 | A section or a well used as a stand-in draws no visible outline; the library lacks the kinds of single-line pages | WP-F2, WP-F5 |
| WFB-315 | Kinds found only by the understanding never reach the gap list, the local assemblies or the survey | WP-F3 |
| WFB-316 | No gate checks that each item of the original is visibly drawn; page evidence items do not stop a run; offline coverage keys static artwork differently from the design | WP-F1 |
| WFB-317 | The visual review is advice only and is blind to missing equipment | WP-F6 |
| WFB-318 | Classification knowledge exists only for the pilot; ctig's base site profile holds no census | WP-I1 |
| WFB-319 | Host values come only from a like engagement; house decisions are never confirmed for a new client | WP-I3 |
| WFB-320 | The tracked page build workflow names host paths for its command lines | WP-I4 |
| WFB-321 | A new project needs the command line; nothing lists a backup's projects or proposes client terms | WP-N1 to WP-N4 |
| WFB-322 | Run limits and usage: the 300-turn default, no usage window check, final review decisions on stub pages, the design sheet's redraw of the first pass | WP-I5, WP-N5, WP-R1 |
| WFB-323 | A sequence's commands and setpoint built as memory tags while the census holds the original's tags; a bind to a tag no table holds passed | WP-F7 |
| WFB-324 | The library is bound as one manager-wide checkout with copied facts, not through a declared interface; it cannot be switched per engagement, and a library commit fails a live run | WP-L1, WP-L2 |
| WFB-325 | No HMI standard: screen rules live in a prompt, a study of one project, the library's wiki and copied decisions; tag grouping and UDTs have no rule, and the target holds no UDT | WP-S1 to WP-S3 |

## 10. Owner Rulings

Each ruling has a default; work proceeds on the defaults unless the owner says otherwise.

| Ruling | Question | Default |
|---|---|---|
| R1 | Reopen NOTE-WFB-13's option B: a New project panel through which the manager writes the engagement's files | Yes |
| R2 | The proof project of WP-P1 | Citect's own example project, if installed on this PC (no client data); otherwise a second backup from the owner |
| R3 | Where the library has no kind, redraw the original's shape from its captured geometry in a neutral style rather than drop it | Yes |
| R4 | Page evidence items and the visual check stop a run | Yes, page items only; library and tool items stay advice listed on the final review |
| R5 | Fable 5.1 for the two design notes of section 8.3 only | Yes |
| R6 | The order of the change groups of section 8.2, every group waiting for the owner's go and the library packages for WP-0 | Yes |
| R7 | Where the HMI standard lives | Tracked in WorkflowBuilder under `standards/hmi/`, independent of any library, with a client layer per engagement |
| R8 | UDTs in the target: one UDT per library kind in the parent project and device instances in the child, in place of plain folders of atomic tags | Yes, built on the one library line after WP-0 |
| R9 | A run reads a pinned worktree of the chosen library commit, so library work can go on during a run | Yes |
| R10 | Ratify the cloud port's GF-117 change: a local assembly's page view at `Local/<Kind>/Assembly`, in place of NOTE-WFB-10 section 11.2 item 2's `Local/<Kind>` | Yes (measured on the gateway, held by a test) |
| R11 | WP-0b takes the cloud's tree for every library path, so the Sandbox-only files the cloud dropped (three documentation tools, wiki pages 01, 02 and 09, the old catalogue interface file, none read by WorkflowBuilder or ctig) leave the Sandbox's tree and stay in its history | Yes |
| R12 | After WP-0b, the new parent on the owner's gateway | Decided 2026-11-07 (WFBD-146): deployed beside the old one as `cadre_hmi_base_asm_080`; existing engagements keep `cadre_hmi_base_asm` |
