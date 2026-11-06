# NOTE-WFB-10: The Standard Migration Workflow, Survey, Project Release and Page Runs by the Elephant-Goldfish Method, Design Description

| Item | Value |
|---|---|
| Document ID | NOTE-WFB-10 |
| Revision | 0.5 |
| Status | Approved by the owner with rulings RW-01 to RW-05 (WFBD-137); WP-W01 to WP-W10 built; WP-W11's replay and the wrap's release cut (WFBD-138) |
| Issued | 2026-11-02 |
| Author | The NOTE-WFB-09 build session (Opus 5.5), as the elephant of WFBD-134 |
| Approver | The owner |
| Register | WFB-271, WFB-272 (NOTE-WFB-09); WFB-273 (the block type `ctig.survey`); WFB-274 (this revision of the workflow) |
| Decisions | WFBD-136 (this direction); WFBD-137 (the approval and the rulings); WFBD-134 (the elephant-goldfish method); WFBD-130 to WFBD-133, WFBD-135 (NOTE-WFB-09); WFBD-128 (no dodged gate); WFBD-104 (replay before an integrated run); WFBD-033 (four agents at a time); WFBD-012 (permissive licences only); WFBD-005 (reuse by invocation) |
| Basis | WorkflowBuilder main at `9bf8c17`; Cadre-Sandbox-OpenBridge main at `d9f8655`; Citect-Ignition-Migrator main at `046a3a5`; NOTE-WFB-09 revision 0.4; spike WP-S01 of 2026-11-02 (section 3) |

The revisions of this document are listed below.

| Rev | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-11-02 | NOTE-WFB-09 build session | First draft: the spike's answers, the three stages, the method inside the workflow, the block contracts, cost and reuse, the packages re-planned |
| 0.2 | 2026-11-02 | NOTE-WFB-09 build session | The cold read's findings mended: NOTE-WFB-09's placement table and rules restated here; one feature identifier; the hash checks in the block; field shapes, exit codes, refusals and their observables; the local faceplate's binding; the wrap's state table; wiring tables for stage B; dependencies and offline acceptance per package |
| 0.3 | 2026-11-02 | NOTE-WFB-09 build session | The second cold read's findings mended: placement sources and overrides; late counts; the record written by the block; the faceplate flag; field rules of the elements list; ordering; observables; the tester and builder on one branch; the plan check over any data chain; the survey and release checks before block 18; the release record's wiring; the wrap's states and version |
| 0.4 | 2026-11-03 | NOTE-WFB-09 build session | Approved (WFBD-137). RW-03 and RW-04 ruled against their defaults: stage B has no cold code review and no tester agent; the gap builder writes its own tests as before, and block 19's proofs stay the acceptance facts written apart from the builder. The tester role, the cold review block, their schema and briefs, T13 and corpus item 12 removed or restated |
| 0.5 | 2026-11-03 | NOTE-WFB-09 build session | The testers' and builders' questions mended during the build: the survey on both census paths (`work_final`, `site_final`, `survey_late`); key 4 on rows 4 and 6 only; the release workflow's copied blocks, start inputs and helper set blocks; the shorthand of conditions and merges as the engine builds them; `m_design_read`; the page child's own pages for the review; the profile's `survey` in its schema; stemless survey instances absorbed by count; the placement tool's refusals, dot segments in assembly paths, every device opener passing `local`, the pin check's own version files and the bundle record (the library's cold review); WP-W11 cut (WFBD-138) |

Conventions: the ISO/IEC Directives regime applies ("shall" states what the design does once built). Block numbers are
those of NOTE-WFB-04 Table 1; a new block has an identifier and no number. "The library" is Cadre-Sandbox-OpenBridge;
"the module" is its Ignition module `cadre.hmi.ob`; "OpenBridge" is the package `@oicl/openbridge-webcomponents` at
the pinned release 2.0.0-next.155; "ctig" is Citect-Ignition-Migrator; "the manager" is WorkflowBuilder. No page,
tag, device or site name of an engagement appears in this document. A builder or tester needs no other document to
build or test a package: where NOTE-WFB-09 is cited, its content is restated here.

## 1. Purpose and Scope

### 1.1 The Owner's Direction

The owner directed on 2026-11-02 (WFBD-136), verbatim: "So before we build anything, this will be a standard approach
in the citect ignition migration workflow, or lets say we will be modifing the workflow to incorporate the changes.
This will also incorporate Elephant - goldfish appraoach throughout".

This document therefore designs a revision of the Citect to Ignition screen migration workflow, not a one-off
addition. It makes three stages (a whole-project survey, one project release, page runs that expect no open gap) the
standard form of every migration, and it builds the elephant-goldfish method of WFBD-134 into the workflow's own
blocks: elephant blocks write contracts that stand on their own; goldfish blocks build, test and review from those
contracts alone; a goldfish that would have to guess asks instead; the acceptance facts are written apart from
builders; and reviewers see the result and the contract but never the builder's reasoning. The owner ruled that stage
B's gap builders keep writing their own unit tests and that stage B has no cold code review (RW-03, RW-04).

### 1.2 Relation to NOTE-WFB-09

NOTE-WFB-09 designed the three stages and the owner ruled its eleven choices (Annex A). This document keeps its
placement rules, OpenBridge source rules, ASM rules and local assemblies, restates each where it is used, amends them
where the spike found the facts different (section 3), adds every block contract, and replaces its work packages with
section 16. Where the two differ, this document governs.

### 1.3 Scope

In scope: the assessment workflow (stage A), a new project release workflow (stage B), the revision 3 parent and its
two child workflows (stage C), the block types they add or change, the library and ctig changes those blocks invoke,
the guards with their threats and corpus, the cost, the reuse of the stopped six-page run, and the work packages.

Out of scope: the translation of Cicode; the provider-neutral build mode (WFB-220); NOTE-WFB-08's waves 4 to 6, which
stay as planned and may later absorb this design's blocks; any OpenBridge release later than the pin; an automatic
return of a question to its elephant (ruling RW-02); local assemblies on cards pages (ruling RW-05); automating the
fast-forward of the library's main branch after a release.

## 2. Basis

### 2.1 What Was Found

Two thirds of the eng02 exercise's 7.9 million tokens went into library gaps and their review rounds, and the
three-page run of WFB-245 stalled for 12 h on gaps found inside a page run, passing one gap package only by switching
its gaps off (a dodged gate, WFBD-128). Finding gaps once per project, building the shared ones once before any page
run, wrapping what OpenBridge already defines, and drawing one-off kinds locally removes that cost from the page runs.

WFBD-134 records the second cause: packages built from briefs that said what to change but not the contracts cost
about a third of the build spend in rework. The same pattern sits inside the workflow: block 20's builders wrote their
own tests and dodged gates three ways, and a builder that met an unstated point improvised.

### 2.2 The Method in One Paragraph

An elephant holds the whole context and writes a contract that a reader with no other context can act on. A goldfish
receives only the contract and the facts the contract names, and acts on them. A gap in the contract is mended in the
contract, never improvised in the goldfish's work. A test is written from the contract by someone other than the
builder, before the builder builds. A review is cold: it sees the contract and the result, never the builder's account
of its work.

## 3. Spike Findings (WP-S01)

The spike read the library, ctig and the manager on 2026-11-02 with three read-only agents and wrote no product code.

### 3.1 OpenBridge Elements Against the Kinds

Table 3.1 gives each candidate element NOTE-WFB-09 named against the kind's states and the ASM rules. Every element's
tag is `obc-` with its folder name; its import path is `@oicl/openbridge-webcomponents/dist/<group>/<name>/<name>.js`.

Table 3.1: Two candidates fit, one fits through another element, three do not fit

| Kind | Candidate | Finding | Verdict |
|---|---|---|---|
| Switch | `obc-switch` (`dist/automation/switch/switch.js`, stable) | The squared automation button: `on`, `variant` (`square` or `flat`), `orientation` (`horizontal`, `verticalRight`, `verticalLeft`), the readout stack, the alert frame and flap, badges, progress | Fits, with a value map (library `regular` to element `square`; library `vertical: true` to `orientation: verticalRight`) and the module's tables (section 8.5) |
| Generator symbol | `obc-indicator-generator` | A 48 px glyph on `LitElement`: no `on`, tag, readout stack, badges or alert frame | Does not fit. `obc-automation-button` (`dist/automation/automation-button/automation-button.js`, stable) with the pinned generator icons in `dist/icons/` fits, with new wrapper code that places the icon element in the button's icon slots |
| Generator set | `obc-gauge-generator` (experimental) | A radial load gauge | Does not fit: a different information type from the library's engine and alternator picture |
| Range bar | `linear-indicator` | A module of SVG helpers, not an element | Does not fit: no pinned element draws a normal band and limit marks |
| Command button | `obc-automation-button` | A process symbol holder with no label | Does not fit. `obc-button` (`dist/components/button/button.js`, stable: `variant`, `disabled`, a label slot, a `click` event) is the candidate, with a new event entry in the wrapper |
| Bus line | `obc-bus` (`dist/automation/bus/bus.js`, beta) | A straight bar: `label`, `size` (`small`, `medium`), `variant` (`regular`, `enhanced`, `medium`), `tint`, `vertical` | Fits for straight bars, with a new descriptor form and a dashed cue for the dead state; corners need the pinned line elements |

Three facts settle the wrap work. First, a wrap is mostly generated: the JavaScript wrapper is the template `WRAPPER`
in `module/tools/gen_module_assets.py`, and the ASM rules of the existing wraps (the state word, the duty badge, the
out-of-service veil) are template functions a component takes with `status: True`. Second, the alarm priority by rank
and the alert state are not in the module: the generator binds `alert`, `alertFrameStatus` and `alertFrameMode` to the
page's alert poll (`screen.ALERT_FIELDS["module"]`), and OpenBridge draws each level's shape and colour. Third, the
generator is already a library kind (`Automation/Generator`, its ASM faceplate, the members of
`devices_asm.GENERATOR_CORE`), so the survey places it `library` (Table 7.5 row 1); a generator wrap is a module-first
upgrade of a library kind, not the closing of a gap (ruling RW-01).

The pinned release's manifest (`custom-elements.json`) lists 50 tagged element classes under `src/automation`; the
module wraps seven of them (pump, tank, motor, fan, digital valve, analogue valve, transmitter) and four others
(instrument field, alert list, small alert page, its own canvas zoom). NOTE-WFB-09's "57" counted directory entries.

### 3.2 The Pin and Its Integrity

No check of the pin exists beyond npm's own install check. `module/web/package.json` names the exact version;
`package-lock.json` holds `resolved` `https://registry.npmjs.org/@oicl/openbridge-webcomponents/-/openbridge-webcomponents-2.0.0-next.155.tgz`
and `integrity` `sha512-PwHJx4APgm+OmHPDdbLQHjVGzaeGaAuRgPfxs1w8ucdW+ZA+ZJPAN9erd3/qvPgjCR/+RjYhsexSIu0wKk2xug==`.
The bundle pulls 245 files, 195 of them OpenBridge `dist/*.js`; `gen_module_assets.py` also reads the package's
`custom-elements.json`, `bundle/openbridge-webcomponents.bundle.js`, `dist/openbridge.css`, `dist/NotoSans.ttf` and
2,556 `dist/**/*.d.ts`. The verified tarball sits in this host's npm cache, and the installed tree matches it member
for member. uPlot 1.6.32 (MIT) and `@lit-labs/observers` 2.1.0 (BSD-3-Clause) are bundled but named neither in the
bundle's legal file nor in `NOTICE`.

### 3.3 The Generator and a Local Assembly

The generator writes each page into the child with `pv.Project.add_view` (any path, nested paths included), and G1,
G2, G3 and G7's view scans walk every view of the child, so a view `Local/<Kind>` is checked by them unchanged. A new
element needs: a schema entry (the descriptor's root admits no undeclared key); registration through
`screen.descriptor_items`, which every device structure reads (the hierarchy, the device nodes, the device index, the
alarm roll-up, the banner, the search index, the tag document, the walk plan); and changes to `parts.PART_ARRAYS`,
`page_checks.BOXED` and `KINDS`, and the identifier list of `testbench.check`.

The library has no generic faceplate shell whose Home tab takes an arbitrary view: the shell is the builder
`framework._tabbed(kind, control_rows, ...)`, which writes one view per kind with a fixed Home, opened through the
closed tables `FACEPLATE_VIEW`, `ASM_VIEW` and `FACEPLATE_OF_KIND`; a kind outside them opens `Faceplate/Empty`. The
opener is `library.open_device(device, kind, title, label, tab)`, which calls
`cadre.hmi.select_device(session, device_id, kind, title, label, tab)`; the floating faceplate's parameters are
`navigation.FLOAT_PARAMS` (`popupId`, `deviceId`, `kind`, `style`, `title`, `label`, `tab`).

The tags bound check (`page_checks.descriptor_tags`) counts only symbols, trends, wells and bars, and `built_tags`
reads only `views/Screens/<page>/view.json`, so neither would see an assembly's parts. The only free colour of a
descriptor is an indicator's `states[].colour` and `stateDefault`.

Unsettled by reading: whether a parent-project view resolves a child-project view path bound at run time. WP-W11
measures it before any page relies on it (section 11.3).

### 3.4 The Census and the Whole-Project Facts

ctig's census writes de-duplicated devices (`census/devices.json`: per device the stem, kind, instances, pages, tags
with `member_role`) and genie instances (`instances.json`), with unclassed and static templates in
`device_types.json` and unrecovered stems in `findings.json`. On eng02 its second census, with the ratified rules,
matches REPORT-WFB-03: 158 pages (36 operator or navigation, 72 pop-up, 50 super genie by a name-prefix rule), 110
decoded, 6,230 top-level objects, 1,411 genie instances of eight kinds (readout 1,029, indicator 186, instrument field
71, motor 55, valve 44, pump 12, sequence 9, analogue valve 5), 165 stems not recovered and 1,206 static instances.

Three facts change NOTE-WFB-09's counting. First, the census has no page class, and on eng02 1,171 of the 1,411
instances sit on pop-up and super genie pages; by distinct stem on operator pages, by the name-prefix rule, the project
holds readout 29, pump 12, motor 6 and indicator 5. Second, 371 instances are stemless (180 of the 240 on operator
pages). Third, eng02 opens its pop-ups through site Cicode functions, so the census's own pop-up rows are empty;
`ctig.citect.project.popups.resolve(work, pages)` follows those functions offline, and no ctig command exposes it.

Features follow ctig's device stage: `bridge.model.census_device` gives each device its members, named by the library's
member names through the site profile's `bridge` adapter, flags members the library profile lacks
(`library.unknown_members`) and reports tags no rule names (finding `tag-without-role`). It needs no capture, but keeps
only devices whose pages lie in the contract's pilot areas. Block 13's page-level device model (`asm_model.py`) needs
captured inventories and cannot run on the whole project offline.

### 3.5 Settlements

Table 3.5 gives each open point of NOTE-WFB-09 and where this document settles it.

Table 3.5: Every open point of NOTE-WFB-09 is settled

| Open point | Settlement | Section |
|---|---|---|
| The candidate elements | Switch and bus fit; the generator through `obc-automation-button`; the command button through `obc-button`; range bar and generator set do not | 3.1, 11.1 |
| The pin's checks (T8, T9) | `module/tools/verify_pin.py` with a tracked manifest, run before any bundle or asset is written | 11.1 |
| Static shapes | A part `shapes` inside an assembly only | 11.2 |
| Embedding a child view | `assemblies[]` in the descriptor; the generator writes `Local/<Kind>` and `Local/<Kind>/Home` into the child | 11.2 |
| Registering the device | `descriptor_items` yields each assembly as an item of kind `local` | 11.2 |
| The generic faceplate shell | None exists; this design's library package builds `Faceplate/ASM/Local` | 11.2 |
| Instances per kind | ctig's new command `survey` | 7.2, 7.3 |
| Feature rows | Members and unnamed tag groups from the device stage's derivation over every counted device; the faceplate flag from the resolved openers | 7.4 |

## 4. Terms

Table 4 defines the terms of this document. Each is used in this one sense.

Table 4: Terms

| Term | Meaning |
|---|---|
| Kind | A device kind of the census or the library's catalogue, by its lowercase name (pump, motor, generator) |
| Instance | One device of a kind in the whole project, counted by the rules of section 7.3 |
| Feature | A capability an instance needs, identified by the string `member:<name>`, `unnamed:<suffix>` or `faceplate` (section 7.4); null for an item that is a whole kind |
| Placement | Where a kind or feature is drawn: `module`, `library`, `openbridge`, `shared_gap`, `local` or `unclassified` (Table 7.5) |
| Wrap | A module component that bundles one pinned OpenBridge element unchanged, with the ASM rules in its wrapper |
| Shared gap | A kind or feature that neither the library nor the pinned release provides and the project needs for more than `local_max` instances |
| Local assembly | A view of the child project that draws one instance of a `local` kind from basic parts (section 11.2) |
| Basic part | An assembly part: a label, a readout, an indicator, an instrument field, a line, a static shape or a pulse button (section 11.2) |
| Late gap | A kind or feature a page run finds that the approved survey does not hold (section 9.2) |
| Elephant | A block (or the owner) that reads the whole context of its stage and writes a contract: the survey and its card, block 18, block 19 |
| Goldfish | A model block that acts on a contract alone: builders, testers, readers and reviewers |
| Contract | An elephant's output that a goldfish acts on, naming every fact the goldfish needs or the files that hold it |
| Cold read | A goldfish that reads a contract with the brief of the goldfish that will act on it and lists the questions that goldfish would have to ask |
| Question | An entry `{ref, question, would_guess}` of a goldfish's answer: `ref` names a contract item; `would_guess` states what it would otherwise assume |
| Question card | An approval card that shows questions, with the elephant as its return target |
| Tester | In building this design's packages (section 16.1), a different agent from the builder that writes a package's tests from this document; inside the workflow, block 19's proofs play this part |
| Cold review | A goldfish that judges a result against its contract from the result and the measured facts, never from the builder's report |
| Survey record | `survey-approval.json`: the hash of the approved `survey.json`, the decision and the owner's changes (section 7.8) |
| Release record | `project-release.json`: the library commit and module version a release produced (section 8.6) |
| Stage A, B, C | The survey; the project release; the page runs |

## 5. Design Overview

### 5.1 Stages

Table 5.1 gives the three stages as the standard migration. A project runs stage A once, stage B once, and stage C per
page group. Late gaps found by page runs enter a later stage A run and its stage B (section 9.2 item 6).

Table 5.1: Three stages, each with its elephant, its goldfish and its owner touch point

| Stage | Workflow | Elephant | Goldfish | Gateway | Owner touch point |
|---|---|---|---|---|---|
| A. Survey | `citect-assessment` (revised) | ctig's survey and the library's placement (deterministic), then the owner at the survey card | The map proposal (one bounded call) | No | One card: the placements, the proposed map rows, the owner's changes |
| B. Project release | `screen-project-release` (new) | Block 19 on the release gap list | The contract's cold read; per package a builder (block 20) | Yes: the component test page | The restart word when a wrap is added; the release review |
| C. Page runs | `citect-screen-migration-v3` (revised in place) | Block 18 on the survey | The design's cold read; page builders (block 24); visual reviewers (block 27); the glass fixer (block 28) | Yes | The final review |

### 5.2 Workflows Changed

Table 5.2 names every workflow file that changes. The revision 3 parent keeps its file and identifier
`citect-screen-migration-v3`, because a rerun reuses only a base run of the same workflow identifier; the revision is
called revision 4 in prose.

Table 5.2: Five workflow files change and one is new

| File | Identifier | Change |
|---|---|---|
| `src/workflows/citect-assessment.json` | `citect-assessment` | Stage A appended after `census2` (section 7.1) |
| `src/workflows/screen-project-release.json` | `screen-project-release` | New: stage B (section 8.1) |
| `src/workflows/screen-gap-build-v3.json` | `screen-gap-build-v3` | The gap child: the builder's questions end the package unbuilt (section 8.4) |
| `src/workflows/citect-screen-migration-v3.json` | `citect-screen-migration-v3` | Blocks 19 to 23 retired to stage B; block 17 on the survey; the design's cold read; the question channel; review rows (section 9.1) |
| `src/workflows/screen-page-build-v3.json` | `screen-page-build-v3` | The page builder's question ends the page unbuilt (section 9.4) |
| `src/workflows/briefs/v3/*.md` | | `project-design.md`, `gap-contract.md`, `gap-build.md`, `page-build.md` amended; `cold-read.md`, `map-proposal.md` new (section 10.9) |

## 6. The Elephant-Goldfish Method in the Workflow

### 6.1 Roles of the Blocks

Table 6.1 gives the role of every model block and person block of the three stages. A deterministic block (a tool, a
gate, a transform) has no role: its output is a fact, checked by its exit check.

Table 6.1: Each model block is an elephant or a goldfish, and each goldfish has one contract

| Block | Role | Its contract or source | What judges it |
|---|---|---|---|
| `survey_review` (stage A) | Elephant (the owner) | The draft survey, the proposals | Block 17's and `release_gaps`'s hash checks (T3) |
| `map_proposal` (stage A) | Goldfish | The unmapped kinds and features, the pinned elements list | The placement tool drops a proposal outside the list (T15) |
| 14 Page understanding | Goldfish reader | One unit's pictures and inventory | 16 Reading review (cold) |
| 16 Reading review | Cold review | The pictures and the understanding | The owner at the review |
| 18 Project design | Elephant | Every understanding, the device model, the navigation table, the faceplate groups, the survey | `design_read`; the page builders' questions |
| `design_read` | Goldfish reader | The design and the page builder's brief | Its questions reach the question card |
| 19 Gap contract | Elephant | The release gap list, the library index | `contract_read`; the builders' questions |
| `contract_read` | Goldfish reader | The contract and the gap builder's brief | Its questions reach the question card |
| 20 Gap builder | Goldfish builder | The package, the gap rows, the fixed interfaces | Block 19's proofs and samples, the base's own gates and gate tests (WFB-267), the code audit, the owner at the release review |
| 24 Page builder | Goldfish builder | The design's pages, the understandings, the facts, the gap list with its `local[]` | G0 to G7, the page checks, the evidence pack, block 27 |
| 27 Visual review | Cold review | The side-by-side pictures and the measured evidence | The owner at the review |
| 28 Glass fixer | Goldfish builder | One failed evidence item | The evidence pack of the next pass |
| 29 Owner review | Elephant (the owner) | Everything above | |

### 6.2 What a Contract Holds

A contract shall stand on its own: a goldfish given the contract, the files it names and its brief needs nothing else.
For every item a goldfish acts on, the contract names: the item's identifier (a page identifier, a package identifier,
a gap identifier, a design mapping row's `uid`); what is true when the item is done (the proof, or the design entry);
the files the goldfish may change; the interfaces it must keep; and the facts it may read. Each elephant's brief states
this rule (section 10.9), and its cold read tests it (section 6.3).

### 6.3 The Cold Read of a Contract

After block 18 and after block 19, a cold read shall read the contract with the brief of the goldfish that will act on
it, and list the questions that goldfish would have to ask or the guesses it would have to make. It is a
`wfb.model.extract` block (section 10.6) whose source is the contract and that brief only: no history, no facts beyond
the contract, no earlier answer.

A cold read with no question lets the stage go on. A cold read with a question stops the stage at a question card whose
return target is the elephant: a return reruns the elephant with the questions as its notes, then every block after
it; an approval records that the questions need no change and lets the stage go on.

### 6.4 The Question Channel

1. **The rule.** Every goldfish builder's answer shall carry `questions[]`. Its brief says, in one rule: where the
   contract is silent on a point you would otherwise decide, answer with a question naming the item, and change
   nothing.
2. **The round.** A question makes the whole item unbuilt, never part of it: a gap package or a page with any question
   is not built. The builder's exit check then passes the round with the output `built: false`, checks that each
   question's `ref` names an item of the contract (the valid references of section 10.3 and 10.4), checks that the
   item's work tree is unchanged (a round with a question and a change fails, defect "a question and a change in one
   round"), and runs no gate. A question starts no further round, so guessing gains the goldfish nothing.
3. **The card.** The workflow collects a loop's questions after the loop and stops at a question card with the
   elephant as its return target. The return reruns the elephant with the questions as its notes, then every block
   downstream of it (ARCH-WFB-01 section 8.7).
4. **No silent pass.** An item that asked is never counted as built: a page that asked is absent from the review's
   built pages, and a release in which a package asked ends failed when the owner approves the builders' question
   card instead of returning (section 8.1).

The first return is the owner's click in this revision; an automatic first return is ruling RW-02.

### 6.5 Testers Apart From Builders

A test that judges a goldfish's work shall be written from the contract by another agent or by a deterministic tool,
before the work.

1. **Gap packages (stage B).** Block 19, the elephant, writes each gap's proof (the facts asserted on the generated
   project) and the samples, and block 20's check builds the samples fresh from the contract and judges them by the
   base's own gates and gate tests (WFB-267). The builder writes its own unit tests first, as before (RW-04).
2. **Pages (stage C).** The page builder writes no test. Its work is judged by deterministic checks derived from the
   facts and the design: G0 to G7, the coverage of every mapping row, the navigation table walked, the tags bound, G8,
   G10, G11, the alarm probe and the glass gates.
3. **The survey (stage A).** The survey is judged by the acceptance corpus, whose synthetic fixture's expected counts
   are written by hand from the rules of section 7.3 by the tester, apart from the builder (section 14.2 item 4).

### 6.6 Cold Reviews

A reviewer shall receive the contract, the result and the measured facts, and never the builder's report, its `text`
output, its transcript or its notes. The workflow assembles each reviewer's source from the contract, the result and
the gate outputs, and the plan check refuses a link from a builder's `answer` or `text` port to a reviewer (section
10.8, T14).

1. **Block 16** sees the pictures and the understanding.
2. **Block 27** sees the side-by-side pictures and the evidence pack's measured facts.
3. **`design_read` and `contract_read`** see the contract and the goldfish's brief.

Stage B has no cold code review of a gap package (RW-03); the owner's release review reads each package's gate edits
and code allowances.

## 7. Stage A: Survey

### 7.1 Blocks Added to the Assessment Workflow

The survey shall run in `citect-assessment.json` once the census is final on either path: after `census2` when the
first census had a gap, and after `census` when it had none. That is the only point where the ratified device rules
and the whole decoded project are both present. Table 7.1 lists the blocks added; the existing blocks are unchanged. The
`start` block's input `engagement` (json) gains the optional key `survey`: `{local_max: integer (default 1),
prior_local: [path of an earlier survey.json] (default empty), late: [path of a page run's gaps.json] (default
empty)}`.

Table 7.1: The blocks that add the survey to the assessment

| Id | Type | Inputs (from) | Settings | Outputs used |
|---|---|---|---|---|
| `work_final` | `wfb.flow.merge` | `in_1` (`census2.work`), `in_2` (`census.work`) | `mode: first`; `type: folder:ctig` | `value` |
| `site_final` | `wfb.flow.merge` | `in_1` (`mapping.site_path`), `in_2` (`start.site`) | `mode: first`; `type: string` | `value` |
| `survey_late` | `wfb.data.transform` | `value` (`start.engagement`) | `expression: survey.late || \`[]\`` | `result` |
| `survey_facts` | `ctig.survey` (new, WFB-273) | `work` (`work_final.value`) | `site` (`$from site_final.value`); `library` (`$from start.library_profile`) | `survey`, `openers`, `summary` |
| `survey_draft` | `openbridge.library_gaps` version 2 | `ctig_survey` (`survey_facts.survey`), `late` (`survey_late.result`) | `mode: survey`; `local_max` and `prior_local` (`$from start.engagement` at `survey.*`, defaults as above) | `survey`, `unmapped`, `proposal_source`, `totals` |
| `needs_proposal` | `wfb.flow.if` | `value` (`survey_draft.unmapped`) | `condition: length(@) > \`0\`` (section 8.1's shorthand) | `true`, `false` |
| `map_proposal` | `wfb.model.extract` | `source` (`survey_draft.proposal_source`), after `needs_proposal.true` | Sonnet 5.5, medium; `output_schema: cadre-hmi-openbridge-map-proposal/1`; 2 rounds | `answer` |
| `no_proposal` | `wfb.data.set` | after `needs_proposal.false` | `fields: [{name: proposals, value: []}]`, so its value is `{"proposals": []}` | `value` |
| `m_proposals` | `wfb.flow.merge` | `in_1` (`map_proposal.answer`), `in_2` (`no_proposal.value`) | | `value` |
| `survey_review` | `wfb.flow.approval` | after `m_proposals.done` | `title: Survey of the whole project`; `show`: `survey_draft.totals`, `survey_draft.survey`, `m_proposals.value`; `form_schema: cadre-hmi-survey-changes/1`; `return_targets: []`; `require_notes_on_reject: true`; `once_per_run: true` | `decision`, `form`, `by` |
| `survey_final` | `openbridge.library_gaps` version 2 | `ctig_survey`, `late` as `survey_draft`; `proposals` (`m_proposals.value`); `changes` (`survey_review.form`); `decision` (`survey_review.decision`); `decided_by` (`survey_review.by`) | as `survey_draft`, and `approval_block: survey_review` | `survey`, `record`, `totals` |
| `save_survey`, `save_record` | `wfb.data.write_file` | `file` (`survey_final.survey`, `survey_final.record`) | `target_folder: projects/ENGAGEMENT/work/survey` (local), names `survey.json` and `survey-approval.json`, the same pattern as `save_site` | `file` |
| `survey_json`, `survey_report` | `wfb.data.read_file`, `wfb.verify.report` | `file` (`survey_final.survey`); `context` (`survey_json.content`) | Section 7.9; the report then copied by the `wfb.data.write_file` block `save_report` to `projects/ENGAGEMENT/work/survey`, name `survey-report.md` (local, beside the survey: a block never writes a tracked path, rule 6; a copy into `projects/<engagement>/reports/` is a person's act, NOTE-WFB-12 section 3) | `markdown` |

A decision other than `approve` at `survey_review` ends the run failed at that block; no record is written.

### 7.2 The ctig Survey Command

ctig shall provide `python -m ctig survey --work <dir> [--site <name|path>] [--library <name|path>] --out <dir>`
(defaults `default` and `cadre-hmi-base`, as the census). It reads the census outputs (`census/devices.json`,
`instances.json`, `device_types.json`, `findings.json`), the decoded pages and Cicode (`cpm/pages/*.json`,
`cpm/cicode.json`, `cpm/tables.json`), the indexes (`itm/tag_index.json`, `itm/alarm_index.json`), the merged site
profile and the library profile. It exits 0 with its outputs written; 2 with `{"error": "survey input missing",
"missing": [...]}` on standard output when any of the four census files, `cpm/pages`, `cpm/cicode.json`,
`cpm/tables.json`, `cpm/project.json`, `itm/tag_index.json` or `itm/alarm_index.json` is absent; 1, with `{"error":
<text>}` on standard output, on any other fault. It builds both outputs before writing either, and on a write fault removes any output it wrote. `provenance.command` is
`ctig survey` with its options, each path argument replaced by its final component, so the bytes do not depend on
where the work and output folders lie. It writes:

1. `openers.json` (`ctig.popup-openers/1`): the result of `popups.resolve(work, every decoded page name)`: `openers[]`
   (`{page, an, command, function, popup, device_arg, privilege, resolved}`), `unresolved[]` (`{page, an, command,
   reason}`) and `hosts` (`{lowercase pop-up page name: host page name}`);
2. `survey.json` (`ctig.survey/1`), with the fields of Table 7.2.

Table 7.2: The fields of `ctig.survey/1`

| Field | Content |
|---|---|
| `schema`, `project`, `site`, `provenance` | The schema identifier; the project name; the merged site profile's `name` key, else its file stem; `{commit, command}` |
| `pages` | `{total, decoded, operator, faceplate_source, undecoded}` (integers) |
| `page_class[]` | `{page, class, why}` for every decoded page: `class` is `operator` or `faceplate_source`; `why` is `operator_pattern`, `faceplate_pattern`, `opener`, `association` or `default` |
| `kinds[]` | `{kind, instances, stemless, faceplate_only, pages_operator, alarms, devices[]}`: integers but `devices`; `pages_operator` the number of distinct operator pages drawing the kind's instances; `alarms` the number of rows of `itm/alarm_index.json` whose tag, mapped through `itm/tag_index.json` from the Ignition path to the Citect tag name, is one of the kind's instances' tags (census `devices[].tags`) |
| `kinds[].devices[]` | `{key, stem, stemless, pages[], operator_pages, popups[], members[], unnamed[], unknown_members[]}`: `key` the census device key (`@page/id` for a stemless instance); `stem` a string or null; `pages` every page name drawing it; `operator_pages` the count of those that are operator pages; `popups` the union of the pop-up page names from resolved openers whose `device_arg` matches the stem (section 7.4 item 3) and from the census's `popups`; `members` library member names; `unnamed` census suffixes with tags and no role; `unknown_members` the members the library profile lacks |
| `unclassified` | `{unclassed_templates[{template, instances, pages}], static_templates[{template, kind, instances, pages}], no_kind_devices, stems_not_recovered}`: instances counted on every page, faceplate sources included, and only where the instance's device has no kind; a template with `device: false` is listed under `static_templates` only, never also under `unclassed_templates`; `template` the census's short template name (`template_short`, the part after `::`); `pages` the count of distinct pages; `no_kind_devices` the count of census devices with no kind drawn on at least one page, not counting the entries the census writes for instances of unclassed or static templates; `stems_not_recovered` the count of `stem-not-recovered` findings |
| `features_computed`, `features_reason` | `true` and null when the site profile has a `bridge` section with a non-empty adapter; else `false` and the reason, and every `members`, `unnamed` and `unknown_members` is an empty list |
| `totals` | `{kinds, instances, stemless, faceplate_only, unclassified_objects}`; `kinds` counts the kinds with at least one instance (a kind with only `faceplate_only` devices is listed with `instances: 0`); `unclassified_objects` is the sum of the instances of unclassed and static templates and `no_kind_devices` (`stems_not_recovered` is not added) |

Kind names are normalised: lower case, with `_` and spaces replaced by `-`; a census kind that still fails
`^[a-z][a-z0-9-]*$` makes the command exit 1 naming it. Every array is sorted, case-insensitively, by kind, then
feature, then stem or key, then page. `survey.json` and `openers.json` name client tag stems and page names and are
local only.

### 7.3 Counting Rules

The survey shall count by these rules.

1. **Page class.** Each decoded page takes the first class that applies, in this order: a pattern of the site profile's
   `census.page_classes` (`[{pattern, class}]`; `pattern` a glob matched case-insensitively against the page name)
   whose class is `operator`; such a pattern whose class is `faceplate_source`; `faceplate_source` when a resolved
   opener names the page as its `popup`; `faceplate_source` when a census association call names it with `asspopup`,
   `asschainpopup`, `asswin`, `asschainwin` or `asschainwinfree` (never `asspage`); otherwise `operator`. `why` records
   the rule that applied. An undecoded page is counted in `pages.undecoded` only. Pages of include projects are pages
   of the project.
2. **Instance with a stem.** A census device of `devices.json` with a kind, a stem, `device` not false, and at least
   one operator page in its `pages` (the census's pages: those of its genie instances and of free objects reading its
   tags) is one instance, however many pages draw it.
3. **Stemless instance.** A genie instance of `instances.json` with a kind, `device` not false and no stem, on an
   operator page, is one instance with `stemless: true` and the key `@page/id`. It owns no tags, as in the census
   (`devices[].tags` is empty), so no alarm or feature is joined to it.
4. **Faceplate only.** A device or stemless instance drawn only on faceplate source pages is not an instance; it adds
   one to its kind's `faceplate_only`.
5. **Unclassified.** Unclassed templates, static templates (`device: false`), devices with no kind and stems not
   recovered are listed in `unclassified` and counted against no kind.

### 7.4 Features

A feature is the string of one of three classes; it is counted per kind as the number of instances that have it.

1. **`member:<name>`**: a member that `bridge.model.census_device`, with the site profile's adapter, without the
   contract's page scope and without its source root restriction (every source accepted), gives an instance with a
   stem. `<name>` is the library's member name.
2. **`unnamed:<suffix>`**: a census suffix of the instance's tags with no member role and not waived by a site rule
   (a waived suffix is accounted and is no feature).
3. **`faceplate`**: the instance's `popups` is not empty. An opener's pop-up joins an instance's `popups` when the
   opener's `device_arg`, trimmed of quotes and spaces, equals the stem case-insensitively; the census's own active
   `popups` rows (not `inactive`, and not `asspage`, which navigates) join it. A device whose pages are all undecoded
   or off-page is counted nowhere.

A stemless instance has neither member nor unnamed features.

### 7.5 Placement

The library's placement tool shall place each kind and each feature by Table 7.5, deterministically, taking the first
row that applies. No agent and no setting of a page run may change a placement (NOTE-WFB-09 Table 5.3, restated).

Table 7.5: A kind or feature is placed by the catalogue, then by the OpenBridge map, then by its count

| Row | Library resolution | Map row | Count | Placement | Built where |
|---|---|---|---|---|---|
| 1 | Module part or library view | any | any | `module` or `library` | Already built |
| 2 | None | `reviewed` or `approved` | any | `openbridge` | A wrap in the project release (section 8.5) |
| 3 | None, a kind | None | more than `local_max` | `shared_gap` | A library view in the project release |
| 4 | None, a kind | None | 1 to `local_max` | `local` | A local assembly in the page run |
| 5 | None, a feature of a placed kind | None | more than `local_max` | `shared_gap` | The project release |
| 6 | None, a feature of a placed kind | None | 1 to `local_max` | `local` | Basic parts in a `group` beside the kind's symbol on its page (section 9.3) |
| 7 | Unclassified template or static instance; `unnamed:` feature; a kind with no instance (only `faceplate_only`) and no library resolution | not looked up | not counted | `unclassified` | Decided at page time |

The keys and resolutions are these.

1. **Kind resolution.** As page mode today: `module` when the library profile's `kinds` lists the kind, its catalogue
   view exists in `library/contracts.json`, the module has the part `cadre.ob.` joined with the kind without hyphens,
   and `module_first` holds; `library` when the profile lists the kind and its view exists; otherwise none.
2. **Feature resolution.** `member:<name>` is resolved when the library profile's `deviceKinds[kind].members` has the
   name; `faceplate` when the profile gives the kind a faceplate. A feature of a kind with no resolution travels with
   its kind (it is built by the kind's wrap, view or assembly): its `placement` and `resolution` are null.
3. **Map rows.** Only `reviewed` rows of `module/openbridge-map.json`, and rows the owner accepted at the card
   (`approved`), place by row 2. A kind or feature is unmapped when it has no library resolution and no map row in any
   state; a map row in state `proposed` is shown on the card as a proposal with its source `map`, only when its kind or
   feature is in the survey and unmapped, and is not sent to the model; a final survey accepts it unless the owner
   rejects it. A kind with no instance takes row 1 or row 7, never row 2. A proposal with `element: null` is `dropped`.
   A late feature row (rule `feature`) enters the next survey's `unclassified_features`.
4. **Earlier engagements (RS-06).** A kind that rows 4 or 6 would place `local` here, and that a survey named by
   `prior_local` placed `local`, is a shared gap here whatever its count. Rows 1 and 2 still win: a kind with a library
   resolution, a `reviewed` map row or an accepted proposal keeps that placement.
5. **Late rows.** Each late kind or feature of the `late` files (section 9.2 item 6) is added with the `count` and
   `stems` of its `late[]` entry, its count summed with any count the census gives it, and placed by the same table.
6. **Overrides.** Key 4 (on rows 4 and 6 only) and the owner's changes (section 7.8) override the table; key 5 adds
   counts and then places by the table. Each kind and feature records
   `placement_source`: `table`, `prior_local` or `change`.

### 7.6 The Survey File

`survey.json` (`cadre-hmi-project-survey/1`) shall hold the fields of Table 7.6.

Table 7.6: The survey file names every kind and feature with its count and placement

| Field | Content |
|---|---|
| `schema`, `library_commit`, `openbridge_release` | The schema identifier; the library commit whose catalogue and map were read; `{version, commit}` of the pin |
| `ctig_survey_sha256`, `local_max`, `pages` | The SHA-256 of the ctig survey file; the threshold; ctig's page totals |
| `kinds[]` | `{kind, count, stemless, faceplate_only, pages, library_resolution, map_row, placement, placement_source, resolution, features[]}`: `count` the instances; `pages` the operator pages; `library_resolution` `module`, `library` or null; `map_row` `{element, state}` or null; `resolution` the module part, library view or element, or null |
| `kinds[].features[]` | `{feature, count, placement, placement_source, resolution}` |
| `wraps[]` | `{kind, feature, element, state}` for every `openbridge` placement |
| `shared_gaps[]` | `{id, kind, feature, count, stems[]}`; `id` as section 8.2 |
| `local[]` | `{kind, feature, stem, page}`: one entry per instance; its stem (null when stemless) and the first operator page drawing it in sort order |
| `unclassified[]` | `{kind: "template" or "static" or "no_kind" or "stem_not_recovered", template, instances, pages}` |
| `unclassified_features[]` | `{kind, feature, count}` for every `unnamed:` feature |
| `proposals[]` | `{kind, feature, element, properties, states, reason, source ("model" or "map"), verdict ("pending", "accepted", "rejected" or "dropped"), why}` |
| `approval` | null in a draft (a run without `--changes`); in a final survey (a run with `--changes`, even an empty list) `{changes[], refused[]}`; the decision lives in the record only |
| `totals` | `{kinds, instances, wraps, shared_gaps, local, unclassified_objects}` |

Every array is sorted as section 7.2 gives.

### 7.7 The Map Proposal

The proposal is one bounded call (RS-09). `survey_draft` writes `proposal_source`: `{unmapped[{kind, feature, count,
members[], unnamed[]}], elements[{tag, path, group, properties[{name, type, enum, default}]}]}`, from the unmapped
items and `module/openbridge-elements.json`; it holds no stem, page or client name. `map_proposal` answers
`cadre-hmi-openbridge-map-proposal/1`: `{proposals[{kind, feature, element, properties, states, reason}]}`, with
`element` a tag or null, `properties` an object from the kind's parameter to the element's property, and `states` a
list of `{name, props}` (the map's form). The placement tool marks a proposal `dropped`, with `why`, when its element
is not in the elements list or its kind or feature is not unmapped; a proposal with `element: null` is shown and places
nothing. A proposal never places a kind: only the owner's acceptance at the card makes it a row. The block's
`instructions` are the text of the new brief `map-proposal.md`: name only an element of the list, or null when none
fits; never place a kind; give the reason in one sentence.

### 7.8 The Survey Card and the Record

The card shows the draft's totals, wraps, shared gaps, local placements, unclassified lists and every proposal. Its form
(`cadre-hmi-survey-changes/1`) is `{changes[]}`, each change one of `{action: "reject_proposal", kind, feature,
reason}`, `{action: "to_local", kind, feature, reason}` or `{action: "to_shared_gap", kind, feature, reason}`, with
`reason` a non-empty string. An approval accepts every proposal it does not reject.

`survey_final` applies the changes: `reject_proposal` returns the item to the placement Table 7.5 gives with no map
row; `to_local` and `to_shared_gap` apply only to an item placed `shared_gap` or `local`. A change that names no item,
or another placement, or has an empty reason, or a `reject_proposal` naming no proposal, is not applied and is listed
in `approval.refused[]` with the reason, which the report shows.

The `survey_final` block (not the tool) then writes `survey-approval.json` (`cadre-hmi-survey-approval/1`) from its
inputs: `{schema, survey_sha256 (of the final file's bytes), decision, decided_by, changes, refused, library_commit
(the survey's), run_id (the run identifier the engine gives the block's context), workflow: "citect-assessment",
approval_block (the setting)}`. The page runs' profile names the file, its hash and the record (section 9.2).

### 7.9 The Counts-Only Report

`survey_report` shall write the totals, the kinds with their counts and placements, the wraps with their element tags,
the shared gaps and local placements by kind and feature, the unclassified counts, the proposals and their verdicts,
and the refused changes. It names no stem, page, device, site or client: a test scans it for every stem and page name of
four characters or more in the two survey files, as whole tokens compared case-insensitively, and fails on any hit. Its
`context` is the final survey's content, read by a `wfb.data.read_file` block `survey_json` from `survey_final.survey`.

## 8. Stage B: Project Release

### 8.1 Blocks of the Release Workflow

`screen-project-release.json` shall build every approved `openbridge` and `shared_gap` placement in one library and
module release, before the project's first page run. Table 8.1 gives its blocks and links; the blocks from
`library_merge` to `testbench_glass` are copied from the revision 3 parent with their settings and links, their
upstream links renamed as shown.

Table 8.1: The release workflow's blocks and links

| Id | Type | Inputs (from) | Settings and notes |
|---|---|---|---|
| `start` | `wfb.trigger.manual` | | Inputs `profile` (json, the engagement's page run profile), `survey` (file), `survey_record` (file), and each `start` input the copied blocks read (`gateway_url`, `module_marker`) with revision 3's name, type and requiredness |
| `preflight` | `wfb.migration.preflight` | `profile` (`start.profile`) | The profile's `target.library.commit` at the library's HEAD; the gateway; the trial |
| `release_gaps` | `openbridge.library_gaps` v2 | `survey`, `survey_record` (`start.*`), after `preflight.done` | `mode: release` |
| `has_open` | `wfb.flow.if` | `value` (`release_gaps.open_count`) | `condition: value > \`0\`` |
| `nothing` | `wfb.data.set` | after `has_open.false` | `value: {"built": []}` |
| `gap_contract` | `wfb.migration.gap_contract` (19) | `gaps` (`release_gaps.gaps`), after `has_open.true` | Profile `agents.blocks."19"` as today |
| `contract_read` | `wfb.model.extract` | `source` (`gap_contract.answer`) | Section 10.6; the goldfish's brief `gap-build.md` given through the block's `attachments` setting, or, where that setting cannot name a repository file, through a `wfb.data.read_file` block `contract_brief` joined to the source by a `wfb.data.transform` |
| `contract_asked` | `wfb.flow.if` | `value` (`contract_read.answer`) | `length(value.questions) > \`0\`` |
| `contract_return` | `wfb.flow.approval` | after `contract_asked.true` | `return_targets: [gap_contract]`; `max_returns: 2`; an approval goes on |
| `m_contract` | `wfb.flow.merge` | `contract_asked.false`, `contract_return.done` | |
| `gap_packages` | `wfb.data.transform` | `value` (`gap_contract.answer`), after `m_contract.done` | `packages` as today |
| `gap_build_loop` | `wfb.flow.loop` | `items` (`gap_packages.result`) | Child `screen-gap-build-v3`; inputs `gaps` (`release_gaps.gaps`), `library` and `interfaces` as today; outputs `build`, `questions` per item |
| `builder_questions` | `wfb.data.transform` | `value` (`gap_build_loop.results`) | The items' `questions`, flattened with their package |
| `builders_asked` | `wfb.flow.if` | `value` (`builder_questions.result`) | `length(value) > \`0\`` |
| `builder_return` | `wfb.flow.approval` | after `builders_asked.true` | `return_targets: [gap_contract]`; `max_returns: 2`; an approval leads to `release_failed` |
| `release_failed` | `wfb.flow.stop` | after `builder_return.done` (it fires on an approval only; a rejection returns to `gap_contract`) | Ends the run failed: a package asked and was not built |
| `library_merge` (21) to `testbench_glass` (23) | as revision 3, and `library_merge` refuses any build with `built: false` | `builds` (`gap_build_loop.results`), after `builders_asked.false`; `contract` (`gap_contract.contract`) | `release_approval` is the owner's restart word |
| `release_review` | `wfb.flow.approval` | after `testbench_glass.done` | Shows the test page evidence and each package's gate edits and code allowances |
| `record_built` | `wfb.data.transform` | `library_merge.build`, `module_settled.value`, `testbench_g8.result`, `testbench_g11.result`, `testbench_glass.result`, `release_gaps.gaps`, after `release_review.done` | `cadre-hmi-project-release/1` with the built gaps (section 8.6) |
| `record_nothing` | `wfb.data.transform` | `nothing.value`, `release_gaps.gaps` (its provenance commit is the library's HEAD at the round) | `cadre-hmi-project-release/1` with `built: []` (section 8.6) |
| `m_record` | `wfb.flow.merge` | `in_1` (`record_built.result`), `in_2` (`record_nothing.result`) | |
| `save_release` | `wfb.data.write_file` | `value` (`m_record.value`) | `projects/<engagement>/work/release/project-release.json` |
| `report` | `wfb.verify.report` | after `save_release.done` | The release report |

In the copied blocks, each reference to `profile_final.value` reads `start.profile` instead. Where a row of Table
8.1 or Table 9.1 gives a `wfb.data.transform` several inputs, a `wfb.data.set` block named `<id>_in` gathers them as
named fields and feeds the transform's one input `value`.

The tables of sections 7 to 9 write conditions and merges in a shorthand that is built as follows. A `wfb.flow.if`
evaluates its condition on its input itself, so `value > \`0\`` is built `@ > \`0\``, `length(value) > \`0\`` is built
`length(@) > \`0\``, and `length(value.questions) > \`0\`` is built `length(questions) > \`0\``. A merge written as joining
two signals (`X.false`, `Y.done`) is built as a data merge of the If's `result` and the approval's `decision`, since a
merge reached only by signals is skipped when one branch is skipped. A `start` input of type json that feeds a typed
input passes through a `wfb.data.schema_check` block (`profile_check` before `preflight` in the release). The test page
gates' outputs are `testbench_g8.results` and `testbench_glass.evidence`. The release `start` also takes `model` and
`navtable` (files: the engagement's ASM model and navigation table, as revision 3's `device_model` and `navtable`
blocks write them), which `testbench_glass` needs when a package is built. On a builder's question, `m_record` may pass
empty; no record is written, and the run ends failed at `release_failed` on the approval. The release record's `run_id`
is null until a block can read its run's identifier; the record lies in the run's folder.

The profile's `target.library.commit` names the library's HEAD before the release, which `preflight` checks. After the
release review the orchestrating session fast-forwards the library's main branch to the merge commit and writes that
commit into the profile's `target.library.commit` for stage C, whose own pre-flight checks it against the new HEAD.

### 8.2 The Release Gap List

The block (not the tool) shall compute the SHA-256 of the `survey` input's bytes, read the record, and fail before
invoking the tool unless the record's `survey_sha256` equals it and its `decision` is `approve` (T3, T16). The tool then
writes a gap list in `cadre-hmi-library-gaps/2` (section 10.2) with exactly one open gap per approved `openbridge` and
`shared_gap` placement: the identifier `GAP-<kind>` for a kind, and `GAP-<kind>-<feature>` for a feature with each `:`
of the feature replaced by `-` (for example `GAP-pump-member-runHours`). Each gap carries `placement`, `count`, and
`needed`: for a wrap `{element, properties, states}` from its map row or accepted proposal; for a shared gap
`{members: [string], instances: integer}`, where `members` is, for a whole kind, the sorted names of the kind's
`member:` features in the survey; for `member:<name>`, `[<name>]`; for `faceplate`, `[]`.

### 8.3 Block 19 on the Release Gap List

Block 19 shall read the release gap list as it reads a page run's list today, with no design. Its brief gains three
rules: a wrap is a module package of its own, never grouped with library views; a wrap follows section 8.5; and every
proof of a wrap names the component test page row that drives each state of its map row. Its exit check is
unchanged.

### 8.4 The Gap Child

`screen-gap-build-v3.json` shall run per package, as Table 8.4 gives.

Table 8.4: The gap child's blocks and links

| Id | Type | Inputs (from) | Settings and notes |
|---|---|---|---|
| `start` | `wfb.trigger.manual` | | Inputs as today: `package`, `library`, `gaps`, `interfaces` |
| `build` (20) | `wfb.migration.gap_build` v2 | `package`, `library`, `gaps`, `interfaces` (`start.*`) | The profile's block 20 model and effort, as today |
| `asked` | `wfb.flow.if` | `value` (`build.questions`) | `length(value) > \`0\``; true ends the child |
| `m_end` | `wfb.flow.merge` | `asked.true`, `asked.false` | |

The child's outputs are `build` (`build.build` when the package was built; null when the builder asked) and
`questions` (the builder's questions, each with its package).

### 8.5 Wraps

A wrap shall take its element only from the pinned release, unmodified: the bundle imports the element from the package
at the pin; no OpenBridge source file is copied, edited or patched; a later release enters only by a library item that
moves the pin and updates `NOTICE` after its Apache change date (NOTE-WFB-09 section 7.1). The ASM rules shall live in
the wrapper and the library's tokens, never in OpenBridge's code: the alarm priority by the Citect category's rank
(drawn by OpenBridge from the generator's alert binding); a quiet normal state (colour only for state and alarm); the
state words the device model gives; and the ASM faceplate opened by the library's opener (NOTE-WFB-09 section 7.3).

Block 20's brief gains this checklist of the files a wrap changes, in order: the import in `module/web/entry.js`; the
tag in `module/tools/measure_defaults.py`, then the measured `module/web/defaults.json`; the entry in `COMPONENTS` of
`gen_module_assets.py` (with `status: True` for a device); the generated schema, `module/components.json` and mounted
assets, written by `gen_module_assets.py` and never edited by hand; the descriptor in `CadreOb.java`; the version in
`module/build.gradle.kts`; the module tables of `screen.py` (`MODULE_KIND`, `MODULE_PARAM`, `MODULE_DROP`,
`MODULE_IF_LISTED`, and a value map where the library's and the element's values differ); `MODULE_TAGS` of
`tools/compare/glass_gates.py`; the test page row; the facts `tests/test_module.py` pins (the release version, the
device list), mended through the hooks block 19's contract names (its brief, rule 2.3); and the map row set to
`reviewed` with the survey record's hash as its `reference`. A builder stops before the module's Gradle build: the orchestrating session
builds, signs and installs on the owner's word.

A wrap's evidence is the module's tests, its properties schema, a test page row that drives every state of its map row,
G8 and G11 on that page, and one raised alarm through the alarm probe.

### 8.6 The Release Record

`project-release.json` (`cadre-hmi-project-release/1`, local) shall hold `{schema, survey_sha256, library: {repository,
merge_commit, branch}, module: {version, installed}, built[{gap, placement, kind, feature, element}], test_page: {g8,
g11, glass, alarm_probe}, run_id}`. With nothing to build it holds `built: []`, `merge_commit` the library's HEAD at
`preflight`, `branch` null and `module` and `test_page` fields null.

## 9. Stage C: Page Runs

### 9.1 Blocks Added, Changed and Retired in the Parent

Table 9.1 lists the changes to `citect-screen-migration-v3.json`. Blocks 1 to 16 and their helpers (the `reuse_*`
conditions and the `m_*` merges) are unchanged in code, settings, briefs and links.

Table 9.1: The parent loses the library path and gains the survey, the cold read and the question channel

| Block | Change |
|---|---|
| `has_open`, `open_gaps`, `no_gaps`, `gap_contract`, `gap_packages`, `gap_build_loop`, `library_merge`, `library_settled`, `module_flag`, `needs_module`, `no_module`, `module_release`, `module_settled`, `release_approval`, `release_go`, `trial`, `testbench`, `testbench_import`, `testbench_tags`, `testbench_g8`, `testbench_g11`, `testbench_glass`, `gaps_final` | Retired from the parent (23 blocks) |
| `survey_check` (new, `openbridge.library_gaps` version 2, `mode: check`) | Before block 18: the checks of section 9.2 item 1 and the release record's checks, with no design; outputs `survey` (the checked file) and `content` |
| 18 `design` | New optional input `survey` (`survey_check.content`); brief section on placements (section 9.3) |
| `design_read`, `design_asked`, `design_return`, `m_design_read` (new) | As `contract_read` to `m_contract` of Table 8.1, on `design.answer` with `page-build.md`, return target `design`; the existing `m_design` (the merge of the design-time pictures) stays |
| 17 `gaps` | Version 2, `mode: page`, after `m_design_read.done`; `survey` (`$from profile_final.value`, `select: target.library.survey`); `require_survey: true` (section 9.2) |
| `gaps_json` | Reads `gaps.gaps` |
| `page_loop` | After `gaps_json.done`; the input `merged_library` removed |
| `final_g8` | The input `merged_library` removed, so it reads the configured library checkout, as `LIBRARY_PORT` does when unlinked |
| `page_questions`, `pages_asked`, `page_return` (new) | As `builder_questions` to `builder_return` of Table 8.1 on `page_loop.results`, return target `design`; an approval goes on to the review with the asking pages unbuilt. `page_questions` gives `[{group, ref, question, would_guess}]` |
| `review_pages` | Lists only the pages of loop items whose `questions` is empty: the page child gains the output `pages` (its group's design pages `{page, route, level, rules}` when built, null when its builder asked), and `review_pages` reads `page_loop.results[].pages[]` |
| `design_sheet` (`wfb.verify.report`) and `design_review` (`wfb.flow.approval`), added 2026-11-04 | After `gaps_json`, before `page_loop`: the owner's review of the design as an HTML sheet beside the original; a rejection returns to `design` with the notes, and the design is revised from the reviewed one (NOTE-WFB-12 section 5, WFB-291) |
| `review_placements` (new, `wfb.data.transform`) and 29 `review` | The review shows the wraps, the local assemblies and the late gaps (section 9.5) |
| 30 `report` | A placements section |

### 9.2 Block 17 on the Survey

The profile shall name the approved survey and the release under `target.library.survey`: `{"file": <path of
survey.json>, "sha256": <hex>, "record": <path of survey-approval.json>, "release": <path of project-release.json>}`.
Paths are absolute, or relative to the manager's workspace; each, and each `prior_local` and `late` path, shall lie
under the workspace (`wfb.paths.default_workspace()`) or the repository's `projects/` folder, or the block refuses it.
Release mode's hash or decision failure names "survey record". Block 17 (version 2, page mode), and `survey_check` before block 18,
shall:

1. **Check the hashes.** Before invoking the tool, fail unless the SHA-256 of the file's bytes equals `sha256`, the
   record's `survey_sha256` equals it too, the record's `decision` is `approve`, the release record's `survey_sha256`
   equals it, and the release record's `library.merge_commit` equals the library commit the round records (which the pre-flight
   holds at `target.library.commit`) (T3). With
   `require_survey: true` and no `survey`, fail. A failure ends the block failed before the tool runs, with a message
   that holds the words "survey hash", "survey record" or "release record".
2. **Place a kind of the design.** By the library at the run's commit first, as today. Else by the survey: `local`
   gives the resolution `local`, listed in `local[]` with `source: survey`, not a gap; `openbridge` or `shared_gap`
   gives `unbuilt`, and the tool exits 3 (no page run builds a library gap, RS-07).
3. **Count instances of a late kind.** An instance is a distinct `device` of the design's `devices[]` whose component
   is the kind, over every page of the run; a kind with mapping rows and no device rows counts one instance per row. A
   design device matches a survey instance when the last segment of its tag folder (the device model's
   `devices{}[device].tag`) equals the survey's `stem`, case-insensitively. A stemless survey instance matches no device
by name; instead each stemless survey instance of the kind absorbs one design device that matches no stemmed instance,
in the order of the design's `devices[]`, and an absorbed device counts as matched (`source: survey`). With
   a survey, a design device's component that is neither a library kind nor a descriptor element is a kind.
4. **Place a late kind.** A kind the survey does not hold is a gap of status `accepted` with a `reviewed` map row
   (rule `map`) or with more than `local_max` instances (rule `twice`). A survey-local kind whose design instances
   exceed the survey's count for it (the instances that match no survey instance) is a gap of status `accepted` (rule
   `second`), its `count` the number of unmatched instances. Each such gap is one `late[]` entry per kind with its `count` and `stems`, and each of its instances is
   in `local[]` with `source: late`: drawn in this run as a local assembly (a mapped kind too; its wrap comes with the
   next release), declared at the review, queued for the next release. A kind the survey does not hold with
   `local_max` instances or fewer and no row is `local` (rule `once`), each instance listed in `local[]` with
   `source: late`, and is also one `late[]` entry with status `local`.
5. **Place a late feature.** A design feature unresolved at the commit (version 1's keys: an element, `view#tab`,
   `key.prop`) is a gap of status `accepted` with version 1's identifier, listed in `late[]` with rule `feature`, drawn
   with basic parts in a `group` beside its symbol (section 9.3).
6. **Queue the late gaps.** `late[]` is written into the run's `gaps.json`; the next stage A names that file in the
   engagement's `survey.late`, and the late items enter the survey (Table 7.5 key 5).

With a survey, `open_count` is 0 by construction: every late gap is `accepted`.

### 9.3 Block 18 on the Survey and Its Cold Read

Block 18 shall receive the survey's content. Its brief gains: a kind placed `local` is mapped to the component
`assembly` with the kind's name, one assembly per instance; a kind placed by a wrap or a library view is mapped to that
kind as today; a feature placed `local` is mapped to basic parts in a `group` beside its kind's symbol, bound to the
instance's tags, never changing the symbol, the wrap or its faceplate (NOTE-WFB-09 section 8.5); and the design is the
page builders' contract (section 6.2). `design_read` reads the design with `page-build.md`.

### 9.4 Block 24 and the Local Assembly

Block 24 (version 2) shall:

1. write the kinds of the gap list's `local[]` entries whose `feature` is null (both sources) into
   `.wfb/local-kinds.json` of its copy and pass
   `--local-kinds <file>` to `screen.py` in its own check build, so that G0 refuses an assembly of any other kind
   (T1); it writes the same list to `facts/local-kinds.json` of the builder's folder, and the brief's build command
   passes it, so the builder's own checks judge as the block does;
2. accept `questions[]` in its answer (`wfb.migration.page_build/2`), with the round rule of section 6.4: valid
   references are the run's page identifiers, the design's mapping rows' `entry` values and the gap list's identifiers; with a
   question nothing is copied from `out/` to the run folder and no gate runs;
3. keep every other rule of its check.

Its brief gains section 11.2's assembly form, parts, device and faceplate, the threats T1, T2, T4 and T5 as rules, and
the question rule. The page child gains `asked` (`wfb.flow.if` on `length(build.questions) > 0`) after `build`: true
ends the child with its questions; false goes on as today. The child's outputs add `questions`.

### 9.5 The Review and the Report

`review_placements` shall gather from the gap list: `wraps[]`; the local assemblies (`local[]` with kind, page and
source); and `late[]` with status, rule and reason. Block 29 shows them as one item, and the report lists them; a late
gap is a declaration the owner sees before Approve all (NOTE-WFB-08 section 6.2).

## 10. Block Contracts

### 10.1 `ctig.survey` (New Type, WFB-273)

| Item | Value |
|---|---|
| Kind | Tool block; tool repository `ctig`; reusable |
| Settings | `site` (name or path, default `default`); `library` (name or path, default `cadre-hmi-base`) |
| Inputs | `work` (folder: a ctig work folder in which `census` has run) |
| Command | `<ctig python> -m ctig survey --work <work copy> --site <site> --library <library> --out out/ctig` from ctig's root with `PYTHONPATH=src` |
| Outputs | `survey` (`file:application/json`, `ctig.survey/1`); `openers` (`file:application/json`, `ctig.popup-openers/1`); `summary` (json: `pages` and `totals` copied verbatim) |
| Exit check | `ctig.survey/1`; the sum of `kinds[].instances` equals `totals.instances`; `pages.operator + pages.faceplate_source` equals `pages.decoded` and the length of `page_class[]`; every kind name matches `^[a-z][a-z0-9-]*$` |
| Limits | 1 round, 600 s |

### 10.2 `openbridge.library_gaps` Version 2

| Item | Value |
|---|---|
| Settings | `mode` (`page`, `survey`, `release` or `check`; default `page`); `interpreter`; `module_first`; `accepted_gaps` (page); `local_max` (integer 1 to 10, default 1; survey and page); `prior_local` (list of paths; survey); `approval_block` (string; survey, final run only); `survey` (`{file, sha256, record, release}` or null; page and check); `require_survey` (bool, default false; page) |
| Conversion from version 1 | `mode: page`, `survey: null`, `require_survey: false`; every other setting kept |
| Inputs | Page: `model` (required), `designs`, `design`, `merged_library` (as version 1). Survey: `ctig_survey` (file, required), `late` (json list of paths), `proposals` (json), `changes` (json), `decision` (string), `decided_by` (json). Release: `survey` (file, required), `survey_record` (file, required) |
| Command, page | version 1's, plus `--project-survey <file> --openbridge-map module/openbridge-map.json` when `survey` is set |
| Command, survey | `tools/hmi/library_gaps.py --survey <ctig survey> --catalogue library/contracts.json --profile library/profile.json --module module/components.json --openbridge-map module/openbridge-map.json --elements module/openbridge-elements.json --local-max <n> [--module-first] [--prior-local <f>]... [--late <f>]... [--proposals <f>] [--changes <f>] --out out/survey`; `--proposals` and `--changes` name files `{"proposals": [...]}` and `{"changes": [...]}`; it writes `survey.json`, `unmapped.json` (a list) and `proposal_source.json` in `--out`; a proposal places nothing unless `--changes` is given |
| Command, release | `tools/hmi/library_gaps.py --release <survey.json> --catalogue ... --profile ... --module ... --openbridge-map ... --out out/gaps` |
| Tool exit codes | 0: written (survey and release modes always; page mode with no open gap); 2: page mode with open or partial gaps (no survey only); 3: page mode with an `unbuilt` kind; 1: an input fault. The block treats 0, 2 and 3 as ran and lets the check judge; 1 fails the block |
| Outputs | Page: `gaps` (file), `audit`, `open`, `open_count`, `local`, `late`, `wraps`. Survey: `survey` (file), `unmapped`, `proposal_source`, `totals`, and `record` (file, written by the block) when `decision` is linked. Release: `gaps` (file), `open`, `open_count`. Check: `survey` (file), `content` (json); the tool is not run |
| Exit check, page | version 1's; with a survey: no kind `unbuilt` (a defect per kind: "the project release has not built it"); every `local[]` entry is survey-local or late; `open_count` is 0 |
| Exit check, survey | `cadre-hmi-project-survey/1`; each kind's and feature's placement whose `placement_source` is `table` equals Table 7.5 recomputed from its own `library_resolution`, `map_row`, count and `local_max`; each `prior_local` placement names a kind of a `prior_local` file; each `change` placement matches an applied change, which names an item and carries a reason; no accepted proposal names an element outside the elements list; with `record`, its `survey_sha256` equals the survey file's |
| Exit check, release | every approved `openbridge` and `shared_gap` placement is exactly one open gap, and there is no other gap |
| Exit check, check | the checks of section 9.2 item 1 passed |

The block, not the tool, compares hashes and writes the record (sections 7.8, 8.2 and 9.2). `cadre-hmi-library-gaps/2`
is version 1's schema with `placement` per kind; `local[]` (`{kind, feature, instance, page, source}`); `late[]`
(`{kind, feature, id, rule, status, reason, count, stems}`); `wraps[]` (`{kind, element}`); `survey` (`{sha256,
library_commit}` or null); and per gap `placement`, `element`, `map_row`, `count` and `needed`. Page mode with no
survey writes version 1. The manager's copy of the schema is checked against the library's file by a manager test
when the library is configured (skipped otherwise).

### 10.3 `wfb.migration.gap_build` Version 2

| Item | Value |
|---|---|
| Conversion from version 1 | No setting changes |
| `build` output | Version 1's, plus `built` (bool, false when the builder asked) |
| New output | `questions` (json) |
| Builder | Brief `gap-build.md` with section 8.5's checklist and the question rule, in place of its rule "Do not ask questions". Check: version 1's, with section 6.4's round rule for a question; the work tree is unchanged when it equals the round's starting commit and tree, `.wfb/` scratch aside, in every round |
| Valid question references | The package's identifier; its gap identifiers; `<gap identifier>#proof`; its sample names; its interface names |

### 10.4 `wfb.migration.page_build` Version 2

| Item | Value |
|---|---|
| Answer schema | `wfb.migration.page_build/2`: version 1 with `questions[]`; with a non-empty `questions` every other field is optional, so `{questions: [...]}` alone is valid. Conversion: a version 1 setting `output_schema` of `wfb.migration.page_build/1` becomes `/2` |
| Check | Section 9.4 |
| New outputs | `questions` (json); `built` (bool) |
| Valid question references | The run's page identifiers; the design's mapping rows' `entry` values; the gap list's identifiers |
| Local kinds file | Sorted and without duplicates |

### 10.5 Schemas

Table 10.5 lists every new or changed schema. Manager schemas live in the manager, library schemas in the library, ctig
schemas in ctig.

Table 10.5: Thirteen schemas are new or changed

| Schema | Owner | Content |
|---|---|---|
| `ctig.survey/1` | ctig | Table 7.2 |
| `ctig.popup-openers/1` | ctig, with a manager copy | Gains the optional key `hosts`; `provenance` stays required, and the survey writes it |
| `cadre-hmi-project-survey/1` | library | Table 7.6 |
| `cadre-hmi-library-gaps/2` | library, with a manager copy | Section 10.2 |
| `cadre-hmi-openbridge-map/1` | library | `{release, rows[{kind, feature, element, import, properties, states[{name, props}], state ("proposed" or "reviewed"), reason, reference}], rejected[{kind, element, reason}]}` |
| `cadre-hmi-openbridge-elements/1` | library | `{release, commit, elements[{tag, class, path, group, status, properties[{name, type, enum, default}]}]}` |
| `cadre-hmi-openbridge-map-proposal/1` | manager | Section 7.7 |
| `cadre-hmi-survey-changes/1` | manager | Section 7.8 |
| `cadre-hmi-survey-approval/1` | manager | Section 7.8 |
| `cadre-hmi-project-release/1` | manager | Section 8.6 |
| `wfb.migration.profile/1` | manager | `target.library` gains the optional object `survey` of section 9.2: `{file, sha256, record, release}`, each a string |
| `wfb.migration.contract_questions/1` | manager | `{read[], questions[{ref, question, would_guess}]}`: `read` lists the contract items read, `ref` names one |
| `wfb.migration.page_build/2` and the gap builder's report | manager | Gain `questions[]` of the form of `contract_questions` |

### 10.6 The Cold Read as a Configured Block

A cold read uses `wfb.model.extract`, so no block type is added: Sonnet 5.5, medium, two rounds, `instructions` the
text of `cold-read.md`, `output_schema: wfb.migration.contract_questions/1`, `source` the contract, and the goldfish's
brief as section 8.1's `contract_read` row gives. The extract block's check fails a round that leaves a required field
empty.

### 10.7 `wfb.flow.approval` Use

No change to the type. A question card is an approval with `return_targets` naming the elephant, `max_returns: 2`, and
`show` the questions. After two returns it cannot return again; the owner approves (the stage goes on, or fails where
Table 8.1 says) or rejects (the run ends failed).

### 10.8 The Plan Check Rule for Cold Reviews

`wfb.migration.plan_check` shall refuse a workflow in which the `answer` or `text` output of a block of type
`wfb.migration.gap_build`, `wfb.migration.page_build` or `wfb.migration.glass_fix` reaches an input of a reviewer,
directly or through any chain of data links through blocks of any type (a link to an `after` port carries no data and
is not followed), inside a loop's child workflow as in the parent, and across the loop's boundary (a child's port
exposed through the loop's `outputs`). A reviewer is a
block whose identifier is `visual`, `visual_again`, `reading_review`, `design_read` or `contract_read` (T14).

### 10.9 Briefs

Table 10.9 gives each brief's change. Every brief keeps its numbered rules; a new rule takes the next number. The
question rule is this sentence in every goldfish builder's brief: "Where the contract is silent on a
point you would otherwise decide, answer with a question naming the item, and change nothing." A brief's tester checks
that each new brief has numbered sections and that the question rule stands in `gap-build.md` and `page-build.md`.

Table 10.9: Four briefs amended and two new

| Brief | Change |
|---|---|
| `project-design.md` | Section 9.3's placements; the design is a contract (section 6.2) |
| `gap-contract.md` | Section 8.3's four rules; the licence boundary (OpenBridge only at the pin; no AGPL-3.0 code) |
| `gap-build.md` | Section 8.5's source rules and checklist; the question rule |
| `page-build.md` | Section 11.2's assembly; T1, T2, T4, T5 as rules; the question rule |
| `cold-read.md` (new) | Read the contract as the named goldfish would; list each point it would have to ask or guess, naming the item; list every item read |
| `map-proposal.md` (new) | Section 7.7's three rules |

## 11. Library Changes

### 11.1 The OpenBridge Map, the Elements List and the Pin

1. **Elements list.** `module/tools/gen_openbridge_elements.py` shall write `module/openbridge-elements.json`
   (`cadre-hmi-openbridge-elements/1`) from the pinned `custom-elements.json`: every declaration with `customElement:
   true` and a `tagName`, in every group. `tag` is the `tagName`; `class` the declaration's `name`; `path` the module's
   `path` with `src/` replaced by `dist/` and `.ts` by `.js`; `group` the path's segment after `dist/`; `status` the
   first of `stable`, `beta`, `experimental`, `deprecated` found among the class's JSDoc tags in the package's
   `dist/**/*.d.ts` (the manifest carries only a `deprecated` key, which also counts), else null;
   `properties` its `members` of kind `field`, neither static nor private nor protected, each `{name, type (the
   `type.text`), enum (the string literals when `type.text` is a union of them, else null; this release names every such type, so all
   are null), default (the `default`
   text parsed as JSON where it parses, else the text)}`. Elements and properties are sorted by tag and name. The file
   is tracked. Its test: the number of elements equals the number of such declarations, counted by the test from the
   manifest.
2. **Map.** `module/openbridge-map.json` (`cadre-hmi-openbridge-map/1`) shall hold four rows in state `proposed`, each
   with `element`, `import` and the reason of Table 3.1 and empty `properties` and `states` (filled by the package that
   builds the wrap): `switch` (`obc-switch`), `bus` (`obc-bus`), `generator` (`obc-automation-button`) and
   `command-button` (`obc-button`); and in `rejected[]`: the range bar (`linear-indicator`), the generator set
   (`obc-gauge-generator`) and `obc-indicator-generator` for the generator, each with its reason. Its test asserts
   these four row kinds, their states and the three rejected entries exactly.
3. **Pin check.** `module/tools/verify_pin.py` (standard library only; options `--root <module/web folder>`, default
   the script's sibling `web`, and `--manifest <file>`, default the tracked manifest) shall exit 0 when every check
   holds, and exit 1, listing each failing path, when:
   - `package.json`'s dependency is not the exact string `2.0.0-next.155`, or `package-lock.json`'s entries
     (`packages[""].dependencies` and `packages["node_modules/@oicl/openbridge-webcomponents"]`),
     `node_modules/.package-lock.json`, or the installed package's `package.json` give another version, or another
     `resolved` or `integrity` than the constants of section 3.2, which the script holds;
   - a file listed in the manifest is missing or its SHA-256 differs; or a file under the package's `dist/` is not
     listed.
   The manifest `module/web/openbridge-2.0.0-next.155.sha256.json` is `{package, version, integrity, files: {path
   relative to module/web/node_modules: sha256}}` over every file of the package under `dist/`, the package's
   `custom-elements.json`, `bundle/openbridge-webcomponents.bundle.js` and `package.json`, and the other bundle
   inputs under `node_modules` that esbuild's metafile names at generation time; never `entry.js` or other files of the
   module. `--generate` writes it once: the OpenBridge files are hashed from the tarball's members (`--tarball <path>`,
   or found in npm's cache at `%LOCALAPPDATA%/npm-cache/_cacache/content-v2/sha512/<h[0:2]>/<h[2:4]>/<h[4:]>`, `h` the
   hexadecimal of the lock's integrity) after checking the tarball's SHA-512 against the lock and the constant, and the
   other bundle inputs are hashed from the installed `node_modules` after `npm ci` has verified them against the lock
   (every file of each non-development package that `node_modules/.package-lock.json` lists, a superset of the bundle's
   inputs, since esbuild's metafile is not read);
   a missing tarball or a mismatch exits 1. Its tests build a temporary root holding the four JSON files and a few
   synthetic files listed in a synthetic manifest given by `--manifest`, then move the version and change one byte
   (corpus item 10); one further test runs on the real tree, read only. The check runs as the `prebuild` script of `module/web/package.json`, as the first statement of
   `gen_module_assets.main` and as the first statement of `build_module.main`.
4. **Notices.** `NOTICE` and the mounted `NOTICE.txt` shall name uPlot 1.6.32 (MIT) and `@lit-labs/observers` 2.1.0
   (BSD-3-Clause), and list the components the module wraps. Its test finds both names with their licences in both
   files.

### 11.2 The Assembly Element and the Local Faceplate

1. **Schema.** `schemas/screen-descriptor.schema.json` gains `assemblies[]` and `$defs.assembly`: `{id, kind, device,
   title, label, x, y, w, h, parts, home}`; `id`, `kind`, `device`, `x`, `y`, `w`, `h` and `parts` required. `kind` matches `^[a-z][a-z0-9-]*$`; `device` is
   the instance's tag folder; `x`, `y`, `w`, `h` are page pixels, as a symbol's; `title` is the faceplate's title
   (default the kind) and `label` the device's label in the device index (default the `id`). `parts` is a part set
   holding at least one part; `home` is `{w, h, parts}` or absent. A part set is `{labels[], symbols[], lines[],
   buttons[], shapes[]}`, each array optional, coordinates in pixels from the assembly's (or the Home's) top-left
   corner:
   - `labels[]`: `{id, x, y, w, h, text, align, style}` with `align` `left` (default), `center` or `right` and `style`
     `heading`, `body` or `label` (default);
   - `symbols[]`: `{id, kind, x, y, w, h, member, unit, format, label}` with `kind` one of `readout`, `indicator`,
     `instrument-field`; `unit`, `format` (a number format as the library's readout takes) and `label` optional; no
     `states`, `stateDefault` or `params`;
   - `lines[]`: `{id, points, style}` with `points` `[[x, y], ...]` and `style` `solid` or `dashed`;
   - `buttons[]`: `{id, x, y, w, h, label, member}`: a pulse with the Confirm step, allowed in `home` only (commands
     live on the faceplate, as the library's symbols' do, so a press never also opens the faceplate; G0 rule
     `assembly-button-on-page`);
   - `shapes[]`: `{id, x, y, w, h, form, points}` with `form` one of `rect`, `ellipse`, `polyline`, `polygon`;
     `points` required for `polyline` and `polygon` and forbidden otherwise; drawn by `library.svg` with the palette's
     neutral stroke and no fill.
   No part admits a colour, a class or a style object (T5). Part identifiers are unique within an assembly, `parts` and
   `home` together (G0 rule `assembly-part-ids`). A symbol or button is dynamic and must name a `member`, relative to `device`.
   Neither `device` nor `member` may hold an empty, `.` or `..` path segment, so an assembly never binds another
   device's tags (T1, T4).
2. **One view per kind.** Assemblies of one kind shall have equal `w`, `h`, `parts` and `home` (compared as canonical
   JSON); only `id`, `device`, `title`, `label`, `x` and `y` differ. The generator writes `Local/<Kind>` and
   `Local/<Kind>/Home` once per kind, `<Kind>` the kind with its first letter in upper case; with no `home`,
   `Local/<Kind>/Home` holds one label "No detail". Each is a coordinate root named `Diagram`, built with the diagram
   page's part functions. On the page each assembly is an `ia.display.view` of `Local/<Kind>` with the parameter
   `deviceId` (the tag folder), whose parts bind `deviceId` joined with their `member`.
3. **Registration.** `descriptor_items` yields each assembly as an item `{id, kind: "local", device, params:
   {localKind: <Kind>}}`, so that the hierarchy, the device nodes, the device index, the alarm roll-up, the banner, the
   search index, the tag document and the walk plan read it; `device_index` records `local: <Kind>` for the device. A
   local device's alarms come from its tags in the tag document, as any device's do.
4. **Profile.** The library profile gains the device kind `local` with no required member; G7 devices accepts every
   member the devices file lists for a `local` device.
5. **Faceplate.** The library shall build `Faceplate/ASM/Local` with `framework._tabbed` in the ASM style, with the tabs
   Home, Alarms and Info as the other ASM faceplates draw them (Alarms embeds `Faceplate/Alarms`). The view gains the
   parameter `localKind`; Home embeds an `ia.display.view` whose `props.path` is the expression
   `'Local/' + {view.params.localKind} + '/Home'` and whose parameter `deviceId` is the view's. `local` enters
   `FACEPLATE_VIEW`, `ASM_VIEW`, `FACEPLATE_OF_KIND` and `gates.FACEPLATES`. The opener gains the local kind:
   `library.open_device` and `cadre.hmi.select_device` take an optional `local` argument that writes
   `session.custom.selectedLocal`; `navigation.FLOAT_PARAMS` gains `localKind`; the dock and the popup pass
   `localKind` from `session.custom.selectedLocal`, the float from its parameter. `local` is the last argument of both,
   keyword-only in the Python `library.open_device` (`*, local: str | None = None`) and a plain last argument with the
   default None in the Jython `select_device` (Jython 2.7 has no keyword-only form); `select_device` writes
   `session.custom.selectedLocal` as the given kind, or `""` when it is not given, and the session default is `""`;
   `cadre.hmi.float_params` returns `localKind` from it; the float's dock pin passes `local` from its `localKind`. Every
   other opener of a device passes the device index's `local` too: the alarm panel's and the banner's row clicks
   (`select_alarm_device`) and the search rows, whose row data carry it. The
   local faceplate's tabs are exactly Home, Alarms and Info, so `_tabbed` and the library profile take a tab list for it
   in place of the six ASM tabs. The assembly's click, which calls `open_device` with the
   kind `local` and its `<Kind>`, is added to the generator's assembly embed by this item (WP-W04); before it, an
   assembly has no click and no faceplate. Every Perspective expression and binding traces to the wiki (G1).
6. **Allowed kinds.** `screen.py --local-kinds <file>` (a JSON list of kind names). G0 shall refuse, as an error in
   the screen report's `gates.G0.errors[]` with its rule name, and `screen.py` exits non-zero as for any gate failure:
   `assembly-kind-not-local` (kind not in the list); `assembly-kind-is-library` (kind in the library profile's kinds);
   `assembly-without-local-kinds` (any assembly with the option absent); `assembly-style` (a colour, class or style
   key on a part); `assembly-parts-differ` (item 2); `assembly-on-cards` (an assembly on a page whose descriptor's
   layout is not `diagram`); `assembly-part-ids` (item 1); `assembly-button-on-page` (item 1). `errors[]` lists every rule that applies, in this order.
   A G0 failure writes the screen report, with `gates.G0.errors[]`, before `screen.py` exits. The component test page
   (`--component-test`) allows its own `benchlocal` kind whatever `--local-kinds` holds; every other assembly needs the
   option.
7. **Page checks.** `page_checks.KINDS` gains `assembly`; a coverage map entry may be `{kind: "assembly", id:
   "<assembly>/<part>"}`; `descriptor_tags` counts each dynamic part of an assembly, its Home's included, with the tag `<device>/<member>`;
   `built_tags` reads the child's `views/Local/**` as well as `views/Screens/<page>`; a dynamic part with no `member`,
   or whose tag does not resolve, is listed in `unbound` as `<assembly>/<part>`, prefixed with the page as the check
   prefixes its other entries (T4).
8. **Test page.** `testbench` gains a row with the synthetic local kind `benchlocal`, device `_componentTest/Bench/Local1`
   (the test page's device convention), members `value` (Float8, a readout), `state` (Boolean, an indicator), `cmdStart` (Boolean,
   a pulse button) and `alarm` (Boolean, with one alarm of priority High), and a Home with a readout of `value`, an
   indicator of `state` and the pulse button. The test page's tag document creates the four members as memory tags
   with the defaults `value` 42.0, `state` true, `cmdStart` false and `alarm` false, through `testbench`'s device
   specifications, tag folder and model entries.

### 11.3 The Gateway Probe

WP-W11 shall open `Faceplate/ASM/Local` for `benchlocal` on the gateway. It passes when the Home pane shows the readout
of `value` (42.0) with no view-not-found error, G8 on the test page reports no error badge, and G11 opens and reads the
faceplate. The module is built, signed, installed and the gateway restarted by the commands of the library's
`CLAUDE.md`, section "The module" (`npm run build`, `gen_module_assets.py`, `module/gradlew build` under JDK 17 with the
signing properties, `install_module.py`, `module/tools/restart_gateway.py`), in the orchestrating session after the
owner's word. If it fails, WP-W11 stops, a register item opens, and the design is revised (the generator would write the
shell into the child per local kind) before any change.

### 11.4 The Placement Tool's Modes

`tools/hmi/library_gaps.py` shall gain the survey mode (sections 7.5 to 7.8), the release mode (section 8.2) and page
mode's `--project-survey` (section 9.2), with the exit codes of section 10.2. Run with no survey, page mode gives the
same `gaps.json` as today. Each mode refuses, as an input fault naming the file or row:

1. a map row of state `reviewed` (or a row an approved survey accepted) whose `element` is null or is not a tag of
   `openbridge-elements.json`; such a row never places (T3, T15);
2. in survey mode, a working tree whose map, elements list or library profile differs from its HEAD, since the survey
   records `library_commit` as the tree's state (T3);
3. a `--prior-local` file whose `schema` is not `cadre-hmi-project-survey/1`, and a `--late` file whose `schema` is not
   `cadre-hmi-library-gaps/2` (T7);
4. in release mode, a survey whose `approval` is not an object (a draft) (T3);
5. in page mode, `--project-survey` given without `--openbridge-map` (T7).

## 12. ctig Changes

ctig shall gain the command `survey` (section 7.2) in a new module that calls `popups.resolve` over every decoded page
and the device derivation of `bridge.model.census_device` (or a function both share) over every counted device with a
stem, without the contract's page scope. The census is unchanged. The site profile's `census` section gains the
optional `page_classes`.

## 13. Invariants

The design holds these invariants.

1. A placement comes from the survey, the catalogue and the reviewed or approved map rows, or from the owner's change
   at the survey card; never from an agent or a page run's setting.
2. A kind with a library resolution is drawn by the library, never as an assembly.
3. No page run commits to the library, wraps a component or releases the module.
4. The module bundles OpenBridge only at the pin, verified file by file before any bundle is written. The pin check
   reads the version files (`package.json`, `package-lock.json`) of the checkout being built, and only the
   `node_modules` tree from `CADRE_OB_WEB_ROOT` where that is set. The bundle build records the SHA-256 of the lock file,
   of `entry.js` and of the bundle beside the bundle; `build_module.py` refuses a bundle whose record does not match the
   checkout's lock and entry files, and refuses `--allow-stale-bundle`, which stays an offline option of
   `gen_module_assets.py` only.
5. A local assembly writes only under the child's `Local/` folder and the run's descriptor folder.
6. Every dynamic part of an assembly is bound.
7. Every model block is an elephant or a goldfish of Table 6.1, and every goldfish's source is its contract and the
   facts it names.
8. No reviewer receives a builder's report, text, transcript or notes.
9. A gap package's acceptance facts (its proofs and samples) are written by block 19, never by its builder.
10. A question ends its item unbuilt and reaches a card; it is never counted as a built item.

## 14. Guards

### 14.1 Threat List

Table 14.1 gives each threat and the one guard that refuses it.

Table 14.1: Sixteen threats, each refused by one guard

| No. | Threat | Guard |
|---|---|---|
| T1 | An assembly drawn for a kind placed `openbridge`, `shared_gap`, `module` or `library` | `screen.py --local-kinds` from block 17's `local[]` (section 11.2 item 6) |
| T2 | A library kind or wrap redrawn as an assembly to escape its gates | `assembly-kind-is-library` (section 11.2 item 6) |
| T3 | An edited `survey.json`, an edited map, or a setting that changes a placement | The hash checks of sections 8.2 and 9.2; only reviewed or approved rows place; no page run setting places |
| T4 | An assembly that draws a live value as static | Section 11.2 item 7 |
| T5 | An assembly with its own colour, font or style | `assembly-style` and the part schemas |
| T6 | A builder that edits library files, gates, schemas or samples to pass | The contained build mode and the code audit (WFB-267, WFB-270), unchanged |
| T7 | An undercounted kind kept `local` | Block 17's late rules `twice` and `second` |
| T8 | An OpenBridge release past the pin, or AGPL-3.0 code, in the bundle | `verify_pin.py`'s version checks |
| T9 | An edited or patched OpenBridge file | `verify_pin.py`'s manifest |
| T10 | A wrap that fails an ASM rule | The test page row drives every state of the map row; G8 and the glass gates read the drawn state |
| T11 | A goldfish that guesses where the contract is silent | The question rule at no cost, the cold read before, block 19's proofs and the base's gates after |
| T12 | A question used to escape a failing gate | A question ends the item unbuilt on a card; `ref` must be valid; a question with a change fails |
| T13 | A builder that edits its proofs or samples to pass | Block 20's check writes the samples fresh from the contract and asserts the proofs on the generated project (WFB-267), unchanged |
| T14 | A reviewer that sees the builder's reasoning | Section 10.8's plan check rule |
| T15 | A proposal that places a kind, or names an element outside the pin | Section 7.7: dropped, and only the owner's acceptance makes a row |
| T16 | A survey record forged or copied from another survey | The record's `survey_sha256` must equal the survey's bytes; the record names its run and approval block, which `wfb verify-run` checks |

### 14.2 Acceptance Corpus

The corpus is built before any guard code (WFBD-104). Each item names the package whose tester writes it; offline items
run in the package's own suite; gateway items run in WP-W11.

1. **Pass (WP-W05 tool; WP-W07 block):** the Level 5 descriptors and designs of the exercise give, in page mode with no
   survey, the same `gaps.json` as version 1.
2. **Pass (WP-W06 offline; WP-W11 gateway):** the wrap of ruling RW-01 passes `tests/test_module.py`, its schema, and
   G0 to G7 on the test page descriptor offline; on the gateway, its test page row, G8, G11 and the alarm probe.
3. **Pass (WP-W03 and WP-W04 offline; WP-W11 gateway):** `benchlocal` passes G0 to G7, coverage and tags bound offline,
   and G7 faceplates for `Faceplate/ASM/Local`; on the gateway, G8, G11 and the alarm probe (section 11.3).
4. **Pass (WP-W01):** (a) a synthetic ctig work folder holding a device with a stem on two operator pages, a stemless
   operator instance, a device on pop-up pages only, a device with no kind, a static template, an unclassed template,
   an undecoded page and an opener resolved through a site function gives the hand-written expected `ctig.survey/1`
   counts. (b), a report, not an acceptance: eng02's whole project, run offline by the orchestrating session in
   WP-W11, gives totals whose sums hold, with per-kind counts reported beside the figures of section 3.4.
5. **Refuse (WP-W03):** a pump drawn as an assembly (`assembly-kind-is-library`), and a kind absent from the local
   kinds file (`assembly-kind-not-local`).
6. **Pass and refuse (WP-W05):** page mode given a design with two instances of a kind the survey does not hold lists
   it in `late[]` with status `accepted` and rule `twice`; `screen.py` with a local kinds file without it refuses its
   assemblies.
7. **Refuse (WP-W03):** an assembly with one readout with no `member` is listed in `unbound`.
8. **Refuse (WP-W03):** an assembly part with a `colour` key (`assembly-style`).
9. **Refuse (WP-W07):** page mode with the profile's `sha256` unequal to the file's: the block ends failed before the
   tool runs, its message holding "survey hash".
10. **Refuse (WP-W02):** `verify_pin.py --root <copy>` with the version moved in `package-lock.json`, and with one byte
    of a `dist/` file changed.
11. **Refuse (WP-W08):** a gap builder's question whose `ref` is not a valid reference.
12. **Refuse (WP-W08):** a gap builder's round that has both a question and a change to the work tree.
13. **Refuse (WP-W08):** a workflow linking `build.answer` into `contract_read`'s source through a transform.
14. **Pass (WP-W10):** a page builder's question ends the page unbuilt: its group's entry appears in
    `page_questions.result`, and its pages are absent from `review_pages`'s output.
15. **Refuse (WP-W07):** a record whose `survey_sha256` differs from the file's, a record whose `decision` is not
    `approve`, and a release record whose `survey_sha256` differs: each ends the block failed before the tool runs, its
    message holding "survey record" or "release record".

## 15. Cost and Reuse

### 15.1 Cost of the Design Step

The spike (three Sonnet 5.5 agents at high effort, about 1.1 million tokens), the cold reads of revisions 0.1 and 0.2
(two Sonnet 5.5 agents, about 0.24 million tokens) and the orchestrating session's reading and writing took the
account's weekly usage from 3 to about 6 per cent, in about two hours.

### 15.2 Cost of the Method Inside the Workflow

Table 15.2 gives the method's added model work per stage against revision 3.

Table 15.2: The method adds a cold read per contract and two goldfish per gap package, and removes gap work from page runs

| Stage | Added | Removed | Expected net |
|---|---|---|---|
| A | One proposal call (about 20 to 60 thousand tokens); one owner card | | Small; once per project |
| B | Per contract one cold read (about 50 thousand) | Rounds lost to improvised builds | Small; once per project |
| C | One cold read of the design (0.05 to 0.15 million) | Every gap path of every page run | Cheaper whenever a page meets a feature the library lacked |

A question costs one owner click and a rerun of its elephant and the blocks after it.

### 15.3 Reuse of the Stopped Six-Page Run

Stage C of the six-page run shall restart as a rerun of the stopped run from block 18. Two conditions keep the reading
work reused.

1. **Tool commits.** A block's reuse key holds the HEAD of each tool repository it declares, so this design's commits
   in ctig and the library change the key of every ctig and library block among blocks 4 to 15, and a capture block
   that ran again would need the live Citect runtime. The restart's profile shall therefore name the stopped run's
   outputs in its `reuse` map for blocks 4, 6, 7, 8, 9, 10, 13, 14 and 15 and the census (the mechanism of
   `start_profile`, WFB-213), so those blocks are linked, not run.
2. **The profile.** The profile gains `target.library.survey` and a new `target.library.commit`. Blocks 1, 2, 3 and 5
   read the whole profile and run again (seconds, deterministic); where their outputs are unchanged, the blocks after
   them keep their keys.

Table 15.3: The reading work reuses; the design and everything after it runs again

| Blocks | Outcome | Why |
|---|---|---|
| 1, 2, 3, 5 | Run again, seconds | They read the whole profile |
| 4, 6, 7, 8, 9, 10, 13, 14, 15, census | Linked from the stopped run | The profile's `reuse` map |
| 11, 12 | Reused by key, or run again in seconds | Deterministic; their inputs are the linked outputs |
| 16 Reading review | Reused by key | Its inputs are unchanged |
| 18, `design_read`, 17, 24 to 30 | Run again | Block 18 gains the survey and the profile changed |
| 19 to 23 | Not in the parent | Stage B replaces them; the stopped run's block 19 and package rounds are not reused, because the release gap list replaces the page run's gap list |

The run's order: stage A on eng02 (offline, ending at the survey card for the owner); stage B (with its one restart on
the owner's word when a wrap is added; ending quickly with nothing built when the approved survey has no `openbridge` or
`shared_gap` placement); stage C (the six pages).

## 16. Work Packages

### 16.1 Method

Each package is built by the elephant-goldfish method (WFBD-134). A builder works from this document and the code it
names. A tester, a different agent, writes the package's tests from this document's section for the package and its
corpus items, before or beside the builder, never from the builder's code. A package is accepted when those tests and
its offline corpus items pass. An adversarial review per repository batch is given the code and this document, not the
orchestrator's conclusions. Before every manager commit `uv run wfb check` is green with the editor; commits are by
explicit path with each repository's records. Builders forbid themselves `git checkout`, `stash`, `restore` and `reset`,
and each shared file has one owner at a time. Module builds, installs and restarts run in the orchestrating session on
the owner's word. No package starts while a manager run is live in a checkout it touches.

### 16.2 Packages

Table 16.2 lists the packages. Sizes are agent work: S under an hour, M one to two hours. Models follow PLAN-WFB-01
section 7 and `F:\repos\AGENT-MODELS.md`. At most four agents run at once (WFBD-033).

Table 16.2: Eleven packages in four waves

| No. | Wave | Repository | Package | Needs | Offline acceptance | Size | Builder; tester |
|---|---|---|---|---|---|---|---|
| WP-W01 | 1 | ctig | `ctig survey` (sections 7.2 to 7.4, 12) | none | Corpus 4 | M | Sonnet 5.5 high; Sonnet 5.5 high |
| WP-W02 | 1 | Library | Elements list, map, `verify_pin.py`, notices (section 11.1) | none | Corpus 10 | S | Sonnet 5.5 high; Sonnet 5.5 medium |
| WP-W03 | 1 | Library | The assembly element, registration, the `local` kind, `--local-kinds`, page checks, the test page row (section 11.2 items 1 to 4, 6 to 8) | none | Corpus 3 (offline part), 5, 7, 8 | M | Opus 5.5 high; Sonnet 5.5 high |
| WP-W08 | 1 | Manager | `gap_build` v2, `page_build` v2, the plan check rule, the briefs (sections 10.3, 10.4, 10.8, 10.9) | none | Corpus 11, 12, 13 | M | Opus 5.5 high; Sonnet 5.5 high |
| WP-W04 | 2 | Library | `Faceplate/ASM/Local` and the opener's local kind (section 11.2 item 5) | WP-W03 | Corpus 3: G7 faceplates | S | Sonnet 5.5 high; WP-W03's tester |
| WP-W05 | 2 | Library | The placement tool's modes (section 11.4) | WP-W02 | Corpus 1, 6; the placement of corpus 4 on its fixture | M | Sonnet 5.5 high; Sonnet 5.5 high |
| WP-W06 | 2 | Library | The wrap of ruling RW-01 (section 8.5, Table 16.3) | WP-W02; RW-01 ruled | Corpus 2 offline: the generated assets, the tester's `tests/test_module_generator.py`, `tests/test_module.py`, G0 to G7 on the test page descriptor, and the icon element in the offline harness (`module/tools/harness/devices.mjs`); the defaults are measured in local Chromium as a build step, not an acceptance; no Gradle build | M | Sonnet 5.5 high; Sonnet 5.5 medium |
| WP-W07 | 2 | Manager | `ctig.survey` (WFB-273), `library_gaps` v2, the schemas (sections 10.1, 10.2, 10.5) | WP-W01 and WP-W05 command lines (fakes until they land) | Corpus 1, 9, 15; unit and adjacent tests | M | Sonnet 5.5 high; Sonnet 5.5 high |
| WP-W09 | 3 | Manager | Stage A in the assessment (section 7.1) | WP-W01, WP-W05, WP-W07 | Plan check; a fixture survey with one unmapped kind and a recorded provider answer covers the proposal branch; the report scan; then an offline run on eng02 to the survey card | S | Sonnet 5.5 high; Sonnet 5.5 medium |
| WP-W10 | 3 | Manager | The release workflow, the gap child, the revised parent and page child (sections 8, 9) | WP-W07, WP-W08 | Corpus 14; proof runs on fakes: no-gap release; one package passing; a builder question; a contract question; a page run with a survey hash mismatch; a page question; a late gap in the review; plan checks on the eng02 copies | M | Sonnet 5.5 high; Sonnet 5.5 high |
| WP-W11 | 4 | All | Replay: stage A on eng02 to the card; the module with the wrap built, signed, installed and restarted on the owner's word; the probe of section 11.3; corpus 1 to 15 run | all | Every offline item rerun; the gateway items of corpus 2 and 3 | M | The orchestrating session runs the testers' tests; the owner reviews |

Reviews: one adversarial review per repository batch (ctig after WP-W01; the library after WP-W06; the manager after
WP-W10), Sonnet 5.5 high, given the code and this document.

### 16.3 The Wrap of RW-01

Under the default of RW-01, the generator's wrap shall draw `obc-automation-button` with the pinned generator icons, as
Table 16.3 gives. The component specification in `COMPONENTS` gains `icons: {on: <element tag>, off: <element tag>}`,
the tags read from the icon files `dist/icons/icon-electric-generator-on.js` and `-off.js`; the wrapper creates the
icon element chosen by `on` as the button's child in each icon slot that `automation-button.js` declares, and replaces
it when `on` changes. The component is `cadre.ob.generator` (schema name `generator`, palette title "OB Generator"),
with the element's properties and the template's extra properties as the other device wraps; the module's version
moves from 0.4.3 to 0.4.4. The map row's `states` are `[{name: "running", props: {on: true}}, {name: "stopped", props:
{on: false}}, {name: "fault", props: {on: true, alert: true, alertFrameStatus: "alarm"}}, {name: "out_of_service",
props: {on: false, outOfService: true}}]`. For WP-W06 this section governs the row's `reference` (section 8.5's
survey hash applies to stage B's wraps): it becomes `reviewed` with `reference` `WFBD-137`, the decision that records RW-01. The status word is the template's
`statusText`, On or Off from `state`, as every module device's (the glass gates read On or Off); the generator's
`runText` stays on its faceplate. A generator with `picture: genset` stays on the library's `Automation/GeneratorSet`
(the gauge was rejected). The test page draws a generator cell for each of the four states.

Table 16.3: The generator's states drawn by the wrap

| Generator state (library members) | The wrap's `on` (a module property; the element has none) | Icon | Status word | Alert |
|---|---|---|---|---|
| Running (`state` true) | true | `icon-electric-generator-on` | On | From the page's alert poll |
| Stopped (`state` false) | false | `icon-electric-generator-off` | Off | From the page's alert poll |
| Fault (`fault` true or `faultCode` not 0) | as `state` | as `state` | as above | The alarm's level through the alert binding; the symbol adds no colour of its own |
| Out of service (`mnt/` member set) | as `state` | as `state` | as above | The out-of-service veil of the template |

Under the alternative of the switch, Table 16.3 is replaced by `obc-switch` with section 3.1's value map. Under no wrap,
WP-W06 is dropped and corpus item 2 waits for the first real stage B with a wrap.

### 16.4 Estimate

Eleven builders, nine testers and three reviews, at the rate of NOTE-WFB-08's waves (about one weekly point per two or
three agents of 0.2 to 0.4 million tokens), come to about 8 to 11 weekly points with WP-W11 and the fixes. The owner's
stop is 20 per cent of the weekly limit; the build starts at about 6.

## 17. Owner Rulings

Table 17 lists the choices, the default first. NOTE-WFB-09's rulings stand as Annex A gives them.

Table 17: Five rulings, each with a default

| No. | Ruling | Default | Alternative |
|---|---|---|---|
| RW-01 | The wrap that proves the route | The generator through `obc-automation-button` with the pinned generator icons (the owner's "Yes, wrap it"), a module-first upgrade of the library's generator with new icon-slot code (Table 16.3) | The switch (`obc-switch`), which fits with no new wrapper mechanism; or no wrap before the first real stage B |
| RW-02 | The first return of a question | The owner's click on the question card (no engine change) | An automatic first return by the engine, then the owner (an engine package of size M) |
| RW-03 | The cold code review per gap package | Ruled (WFBD-137): off | |
| RW-04 | Tests of a gap package | Ruled (WFBD-137): the builder writes them, as before | |
| RW-05 | Local assemblies on cards pages | Diagram pages only in this revision | Both layouts |

## 18. Risks

1. **The faceplate's child path.** Unmeasured; section 11.3 measures it first and gives the route if it fails.
2. **Features depend on the site's adapter.** A capability the adapter never names appears only as an unnamed suffix.
   Mitigated by the unnamed list on the card and the late feature rule.
3. **Page classes.** A project with neither openers nor association calls defaults its pages to `operator`, which
   overcounts instances on undetected pop-ups; the site's `page_classes` corrects it, and the card shows the classes by
   count.
4. **Stemless instances.** Counted one per genie instance, they may count one device twice; the totals state the
   stemless count.
5. **The icon slots of RW-01.** No wrap places an icon in a slot today; the test page row proves it before any page
   uses it, and the switch is the fallback.
6. **Questions stall a run for the owner.** Each costs one click; RW-02 is the route to fewer.
7. **eng02 may need no wrap.** Its eight census kinds are all library kinds, so its stage B may build feature gaps
   only, and the wrap route is proven by WP-W11 rather than by eng02's stage B.
8. **Trademarks.** Neither the Apache License 2.0 nor the terms of `openbridge.no` grant a right to the OpenBridge name
   or logo; a name shown to a client's operators is a question for the owner before delivery (NOTE-WFB-09 section 14).

## 19. References

1. WFBD-136: the owner's direction of 2026-11-02 (`decisions/DECISIONS.md`).
2. NOTE-WFB-09 revision 0.4: Whole-project survey, OpenBridge wrapping and local assemblies.
3. NOTE-WFB-08: Final whole-workflow review (section 6.2, library-first composition).
4. NOTE-WFB-04: Screen migration workflow, revision 3 (Table 1, the block numbers).
5. ARCH-WFB-01 section 8.5 (reuse keys) and section 8.7 (approvals and returns).
6. Cadre-Sandbox-OpenBridge at `d9f8655`: `tools/hmi/screen.py`, `framework.py`, `parts.py`, `page_checks.py`,
   `gates.py`, `library_gaps.py`, `testbench.py`, `devices_asm.py`, `navigation.py`, `library.py`, `scripts.py`;
   `module/tools/gen_module_assets.py`; `module/web/package.json`; `NOTICE`.
7. Citect-Ignition-Migrator at `046a3a5`: `src/ctig/citect/census.py`, `src/ctig/bridge/model.py`,
   `src/ctig/citect/project/popups.py`, `src/ctig/cli.py`.
8. OpenBridge web components 2.0.0-next.155, commit `2c98dda1`, Apache License 2.0.
9. REPORT-WFB-03 revision B: eng02 migration assessment.

## Annex A. NOTE-WFB-09's Rulings

Table A.1 restates the rulings of NOTE-WFB-09 as the owner gave them (WFBD-131, WFBD-132, WFBD-135).

Table A.1: NOTE-WFB-09's eleven rulings

| No. | Ruling | Outcome |
|---|---|---|
| RS-01 | `local_max` | 1 |
| RS-02 | How a gap kind is built | A wrap when the pinned release defines it, whatever its count; else a library view when shared; else a local assembly |
| RS-03 | The faceplate of a local assembly | The library's generic shell with a local Home tab |
| RS-04 | A feature used by one instance of a library kind, with no map row | Basic parts beside the symbol |
| RS-05 | A picture pass in the survey | Off: offline facts only |
| RS-06 | A kind local in an earlier engagement and needed again | A shared gap |
| RS-07 | A late gap found in a page run | Drawn as an assembly, declared, queued for the next release |
| RS-08 | The order of the work | Superseded by WFBD-135, now by WFBD-136: this revision is the standard workflow |
| RS-09 | How new map rows are proposed | One bounded model call in the survey (Sonnet 5.5, medium), each row approved on the survey card |
| RS-10 | The OpenBridge Figma kit as a design source | Not a source until its terms were recorded (recorded: CC BY 4.0) |
| RS-11 | The use of the Figma kit under CC BY 4.0 | Open; default: a design reference for wraps and library views, with an attribution in `NOTICE` for any derived design, no asset copied, the pinned code winning where they differ |
