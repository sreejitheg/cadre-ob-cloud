# NOTE-WFB-15: The Library Contract, Design Description

| Item | Value |
|---|---|
| Document ID | NOTE-WFB-15 |
| Revision | 0.3 |
| Status | Draft for the owner's approval |
| Issued | 2026-11-07 |
| Author | The G1 design session (Fable 5.1, `wfb-architect`) |
| Approver | The owner |
| Register | Serves WFB-313, WFB-314, WFB-316, WFB-324, WFB-325 (NOTE-WFB-14 Table 9.1). New: WFB-329 to WFB-334 (section 15) |
| Decisions | None written here; the owner rules on section 14 |
| Basis | WorkflowBuilder main at `9cb3696`; Cadre-Sandbox-OpenBridge main at `506076c`, equal to cadre-ob-cloud main at `dd1958d` for every library path; Citect-Ignition-Migrator main at `0931236`; the step 3 run `20261105T145504Z-1f76`, its rerun `20261105T164103Z-61af` and the page child `20261105T164137Z-229d` (local, read only) |

The revisions of this document are listed below.

| Rev | Date | Author | Change |
|---|---|---|---|
| 0.1 | 2026-11-07 | G1 design session | First draft: the manifest, the conformance check, the visibility measure, the artwork element, the kinds of WP-F5 the module draws, UDTs to wiki page 17, the package split, invariants, tests, rulings LR1 to LR12 |
| 0.2 | 2026-11-07 | G1 contracts session (Opus 5.5) | The cold read's high findings mended: thresholds a palette can meet (3:1 non-text, 4.5:1 text) proven on every palette from the tokens; the manifest's digest in place of its own commit; one table of the eight device types and their paths; measured shapes and confirmed write paths declared (C17, C18); `id` keeps the full folder with `hierarchy` its checked prefix; section 8 an inventory, the new parts' contracts left to their own design; synthetic fixtures (F0-W). Aligned with STD-WFB-01 0.2 and NOTE-WFB-16 |
| 0.3 | 2026-11-07 | G1 contracts session (Opus 5.5) | The cold read's medium findings mended: the declared rule per element kind with its inputs (Table 6.2) and the source boxes; the rendered measure's shadow roots and join by order; the ASM model's keys left as they are; the Table 3.2 row 4 claim corrected; file lists completed; C07, C10, C11, C12 and the manifest's paths confined and completed; the carried rules from a library copy; WFB-333 stated precisely; the result vocabulary of the standard; the tests of HMI-HIS-05 and HMI-UDT-03 |

Conventions: no client, site, project, page or tag name appears in this document. "The pilot" is the one Citect project of
eng02, eng03 and eng04; its three pages of the recorded run are the electrical overview page, the well page and the generator
page. "The library" is the one library line (Cadre-Sandbox-OpenBridge following cadre-ob-cloud by merge, COBD-053); "the
manager" is WorkflowBuilder. "Understanding", "device model", "design", "descriptor" and "renderer" name the five stages of
NOTE-WFB-14. Block numbers are those of NOTE-WFB-06 Table 4.3. Requirement words follow ISO/IEC Directives Part 2: "shall"
states a requirement, "should" a recommendation, "may" a permission. Rule ids `HMI-<AREA>-<nn>` and check ids `CK-<AREA>-<nn>`
are those of the HMI standard (`standards/hmi/STD-WFB-01-hmi-standard.md`, version 0.2, and its index `rules.json`); the
standard states the house rule and this note the library's contract that carries it. Pixel values are page canvas pixels unless the text says otherwise.

## 1. Purpose and Scope

### 1.1 The Request

NOTE-WFB-14 (approved 2026-11-07, WFBD-146) groups its packages into five change groups. Group G1 asks for a self-standing
library contract from which builders in two repositories build with no other context: the manifest and the conformance check
(WP-L1), UDTs and tag structure in the target (WP-S2), the visibility measure of the drawing gate (WP-F1), the artwork element
(WP-F2), and which kinds of WP-F5 the 0.8.0 module already draws, with the package each remaining kind falls to. This document
is that contract.

### 1.2 Scope

In scope: the data shapes, schemas, command lines, file owners, invariants, threat lists and acceptance corpora of the five
items above, their split between the library and the manager, their tests, and the rulings the owner is asked for. Out of
scope, with the interface each consumes stated in section 11: library choice per engagement (WP-L2), the rules enforced by id
(WP-S3), the manager side of the visibility gate (WP-F1), late kinds as run gaps (WP-F3) and design claims checked (WP-F4). No
code is built here, no workflow run, no gateway touched.

### 1.3 Design Method

The contract follows WFBD-134: every check states its inputs, its outputs, what it refuses (a threat list) and what it must
pass (an acceptance corpus); every decision states the alternatives considered and the reason for the choice; the simplest
design that meets NOTE-WFB-14 sections 6 and 7 is preferred, with one host and one owner as the starting case. Section 17
names what the design leaves out.

## 2. Sources

1. NOTE-WFB-14 sections 3, 4.6, 4.7, 6 (RC1, RC3, RC4, RC7, RC8, RC9), 7 and 8, which bind this document.
2. The library: wiki pages 05, 06, 08, 14, 16, 17 and 18 (by section); `tools/hmi/screen.py` (the tables `KIND_VIEW`,
   `MODULE_KIND`, `MODULE_ONLY`, `FRAME_ONLY`, `section_node`, `gap_box`, `device_nodes`, `tags_document`),
   `tools/hmi/parts.py` (`well_node`, `line_node`), `tools/hmi/library.py` (the style classes), `tools/hmi/page_checks.py`
   (`KINDS`, `LIBRARY_KINDS`, `check_coverage`, the command line), `tools/hmi/library_gaps.py`,
   `tools/hmi/placement_survey.py` (`Rules.library_of`), `tools/hmi/assembly.py` (`_shape_node`),
   `tools/compare/capture.py` and `fingerprint.js`; `module/components.json`, `module/openbridge-elements.json`,
   `module/openbridge-map.json`, `module/build.gradle.kts`; `library/profile.json`, `library/contracts.json`,
   `library/tokens/openbridge-tokens.json`; the twelve schemas under `schemas/`; `cloud/import/MAP-PROPOSAL.md`;
   `cloud/REPORT-T3.md` section 10; `CONFIGURATION.md` sections 3.2 and 4.8; COBD-035 and COBD-053.
3. The manager: `src/wfb_blocks/openbridge/_support.py`, `evidence.py`, `capture.py`, `library_gaps.py`;
   `src/wfb_blocks/migration/page_build.py`, `project_design.py`, `understanding.py`, `_v3.py`, `preflight.py`,
   `layout.py`; the schemas under `src/wfb_blocks/migration/schemas/` and `src/wfb_blocks/openbridge/schemas/`;
   `src/wfb/engagement.py`; `src/workflows/screen-page-build-v3.json`; the briefs `project-design.md` and `page-build.md`.
4. The recorded run: the design's 24 gap rows and 191 mapping rows, the page child's descriptors and `coverage_map.json`,
   the evidence pack's 14 failed items and its `inputs/mapping.json`, the ASM model's 368 mapping rows, the six
   understandings and the twelve inventories.

## 3. Findings That Shape the Contract

### 3.1 The Reads of the Library in the Block Library

Twenty-eight files under `src/wfb_blocks/` name the tool repository `openbridge` (42 match the wider library reference
patterns, some for other reasons). They fall into five kinds, listed in
Table 3.1 with what each reads today.

| Kind of read | Where | What is read |
|---|---|---|
| The checkout's path | `openbridge/_support.py` (`configured_library`, `library_of_tools`), `migration/gap_contract.py`, `preflight.py`, `engagement.py` (`_library_state`) | The one setting `tool_repositories.openbridge.path`, and the commit of its HEAD |
| Script paths and scopes | `_support.py` (`GENERATOR_SCRIPT`, `GENERATOR_SCOPE`, `_ASM_PATHS`, `MERGE_GENERATED`, `PARENT_COPY`), `page_build.py` (`OFFLINE_SCRIPT`), `capture.py`, `faceplates.py`, `walk_plan.py`, `walk_run.py`, `library_gaps.py` (`_survey.MAP_PATH`, `ELEMENTS_PATH`), `screen-page-build-v3.json` (three host paths) | Where `screen.py`, `page_checks.py`, `capture.py`, `faceplates.py`, `walk.py`, the map and the elements list lie |
| Catalogue facts kept by hand | `project_design.py` (`COMPONENT_KINDS`, 17 element kinds), `library_gaps.py` (the resolutions), `_survey.py` (Table 7.5 recomputed) | The descriptor element kinds and the placement rules, which the library also keeps in `page_checks.KINDS`, `LIBRARY_KINDS` and `library_gaps.BUILTIN` |
| Build options | `asm_descriptors.py`, `testbench.py`, `walk_plan.py` (`--frame`, `--faceplate` literals), the workflow's `build_options` default | The option names and values of `screen.py` |
| Copied library facts in the profile | `engagement.py` lines 942 to 955; `wfb.migration.profile/1` | `target.library.{repository, commit, reference_commit, accepted_differences, survey}`, `target.parent_project`, `target.build_options`, `design_standard.library_wiki` (four globs: pages 03, 04, 05, 13) |

Only `openbridge/module_release.py` reads the module's id and version, to install it, so no check compares the gateway's module with the library (NOTE-WFB-14
section 4.7 item 5). The descriptor element kinds are kept in three hand-written lists in two repositories (WFB-334).

### 3.2 The Keying of Offline Coverage

The page build's own offline check reports 191 rows of 191 covered on the recorded page child. The evidence pack's offline
item reports 157 of 191 on the same descriptors. The difference is the source of the rows: the page build hands
`page_checks.py` the design's mapping rows, keyed `<unit>:<entry id>` and `<unit>:static.<n>` (the n-th static entry of the
understanding, from 0, `_v3.understanding_entries`); the evidence pack hands it the ASM model's mapping (368 rows, the
pop-up rows filtered out by `source`), whose static rows are keyed `<unit>:s<n>` (`tools/hmi/asm_model.py`). The 34 static
rows under `s<n>` match no key of `coverage_map.json`, and 191 less 34 is 157. The design and the coverage map agree; the
model differs from both. This is the cause behind WFB-316's third clause.

### 3.3 Where the Geometry of a Static Object Lives

An understanding's `static` entry carries `ans`, `what` and `class` (`label`, `frame`, `artwork`, `heading`, `legend`) and
no box. Its place and shape are recoverable only through the inventory objects its `ans` names (`<target>:<an>`), which carry
`class` (`Text`, `SquareV3`, `CircleV2`, `Line`, `PolyLineV2`, `Symbol`, `Genie`, `Set`, `Group`, `Button`, `Bitmap`), `x`,
`y`, `w`, `h`, `nodes` (the points of a line or polyline), `line_rgb`, `fill_rgb`, `line_width`, `text`, `font` and
`justify`, in the original page's pixels (`page_size`). A device entry of a kind the library lacks (the recorded run's types
`fuse`, `dol-starter`, `vsd`, `breaker`, `ups`, `duty-selector`, `power-meter`, `ats`, `actuator`, `wet-well`) carries a box
and the same `ans`. The artwork element of section 7 therefore reads the inventory, not the understanding (WFB-329).

### 3.4 What the Module Draws That the Placement Cannot See

`Rules.library_of` places a kind by `KIND_VIEW` (15 kinds), the profile's `kinds` and the catalogue's views; the 48
module-only kinds of `MODULE_ONLY` less `FRAME_ONLY` (the electrical symbols among them) have no view and are placed
`shared_gap` or `local` although the module draws them (MAP-PROPOSAL sections 5.2 and 6.1). The generator's tables
`MODULE_KIND`, `MODULE_ONLY`, `FRAME_ONLY` and the parameter rules are literals in `screen.py`, not read from
`module/components.json` (REPORT-T3 section 10 item 2). Section 4.5 takes both in.

## 4. The Manifest

### 4.1 Location and Generation

The library shall publish one file, `library/manifest.json`, schema `cadre-hmi-library-manifest/1`
(`schemas/cadre-hmi-library-manifest-1.json`). It is generated, never hand edited (library `CLAUDE.md` rule 5): `tools/hmi/parent.py`
writes it beside `library/contracts.json` and `library/profile.json`, through a new module `tools/hmi/library_manifest.py` that
reads the generator's own tables, the module's files, the schemas, the wiki folder and the git HEAD. A test holds the tracked file
equal to a fresh generation, as `tests/test_catalogue.py` holds `module/CATALOGUE.md`.

### 4.2 The Schema

Table 4.1 gives every field. Types are JSON Schema types; "req" marks a required field. Paths are relative to the library root
with forward slashes.

| Field | Type | Req | Content |
|---|---|---|---|
| `schema` | const `cadre-hmi-library-manifest/1` | yes | The manifest format's version; a reader refuses a value it does not know |
| `library.name` | string | yes | `cadre_hmi_base`: the profile's `library` |
| `library.digest` | string (64 hex) | yes | SHA-256 over the sorted lines `<path> <git blob hash>` of every tracked file under `library.paths`, `library/manifest.json` excluded. A file cannot hold the commit that adds it, so the manifest holds no commit: the reader records the commit of its own checkout, and C03 compares the digest |
| `library.generated` | string (ISO 8601 UTC) | yes | When the generator wrote the file; informative |
| `library.paths` | array of string | yes | The library paths a pinned worktree needs and the dirty check covers: `tools`, `library`, `schemas`, `module/components.json`, `module/openbridge-map.json`, `module/openbridge-elements.json`, `module/build.gradle.kts`, `module/CATALOGUE.md`, `wiki`, `tests/fixtures/conformance`, `NOTICE`: every tracked input of the conformance check (today `GENERATOR_SCOPE` and `_ASM_PATHS` of `_support.py`, less `build/<parent>`, which is generated and untracked: C11 and the pre-flight's parent comparison build it from the worktree). Every path is relative, normalised and inside the library root (invariant 12) |
| `module.id` | string | yes | `cadre.hmi.ob` |
| `module.version` | string | yes | `0.8.0`: `version` of `module/build.gradle.kts` |
| `module.components` | integer | yes | 97: the entries of `module/components.json` |
| `module.files.components` | string | yes | `module/components.json` |
| `module.files.elements` | string | yes | `module/openbridge-elements.json` (281 tags of the pinned package) |
| `module.files.map` | string | yes | `module/openbridge-map.json` |
| `module.files.release` | string or null | yes | The built `.modl` kept in `cloud/release/`, or null |
| `module.sha256` | string (64 hex) or null | yes | The digest of `module.files.release`; null with no release file |
| `module.pin` | object `{package, version, commit, licence}` | yes | `@oicl/openbridge-webcomponents`, `2.0.0-next.155`, `2c98dda1`, `Apache-2.0` (`CONFIGURATION.md` section 3.1) |
| `schemas` | object: name to `{id, file, sha256}` | yes | One entry for each file of `schemas/`: `descriptor` (`cadre-hmi-screen/1`, `screen-descriptor.schema.json`), `devices` (`cadre-hmi-devices/1`), `coverage`, `gaps1`, `gaps2`, `survey`, `installed_modules`, `glass_gates`, `alarm_probe`, `asm_model`, `preview_checks`, `sidebyside`, `manifest`, and from this contract `visibility`, `conformance`, `udt_types` |
| `catalogue.contracts` | string | yes | `library/contracts.json` (74 views) |
| `catalogue.profile` | string | yes | `library/profile.json` (`cadre-hmi-library/1`) |
| `catalogue.kinds` | array of string | yes | The 15 symbol kinds of `KIND_VIEW`, each a key of the profile's `kinds` |
| `catalogue.device_kinds` | array of string | yes | The 15 keys of the profile's `deviceKinds` |
| `catalogue.module_kinds` | array of string | yes | The 12 kinds the module draws in place of a library view (`MODULE_KIND`) |
| `catalogue.module_only_kinds` | array of string | yes | The 48 display-only kinds the module alone draws (`MODULE_ONLY` less `FRAME_ONLY`), each with its component in `catalogue.parts` |
| `catalogue.frame_kinds` | array of string | yes | The 33 frame components (`FRAME_ONLY`), never placed by a builder |
| `catalogue.parts` | object: kind to `{component, element, role}` | yes | For every kind of the three lists above: the module type (`cadre.ob.<name>`), its element tag and its role, `device`, `module-only` or `frame`; the source of the generator's tables (section 4.5) |
| `catalogue.element_kinds` | object: element kind to `{array, draws, box}` | yes | Every descriptor element kind (section 6.1 Table 6.1): the descriptor array that holds it, what it draws (`border`, `fill`, `text`, `glyph`, `stroke`, any subset, possibly empty), and whether it has a box (`x, y, w, h`) |
| `catalogue.gap_box` | object `{draws: ["border", "text"], honest: false}` | yes | The gap box the generator draws for an unknown kind: visible, never an honest drawing |
| `parents` | array of `{name, frame, build}` | yes | Every parent the library builds: `cadre_hmi_base` (frame `openbridge`), `cadre_hmi_base_asm` (frame `asm`), and any `--name` the build adds; `build` is `build/<name>` |
| `parents_default` | string | yes | The parent `screen.py --parent` takes by default (`cadre_hmi_base`) |
| `commands` | object: name to `{script, interpreter, modes, exit_codes, options}` | yes | Section 4.3 Table 4.2 |
| `build_options` | object | yes | `render: [stock, module]`, `frame: [openbridge, asm, ob, obasm]`, `faceplate: [openbridge, asm]`, `faceplate_mode: [dock, popup]`, `requires: {ob: module, obasm: module}`, `default: ["--frame", "asm", "--faceplate", "asm", "--faceplate-mode", "dock", "--render", "module"]` |
| `placement` | object `{module_first, local_max, local_max_range}` | yes | The placement tool's defaults: `false`, 1, `[1, 10]` (`CONFIGURATION.md` section 4.8) |
| `wiki.design` | array of string | yes | The pages a design reads: `wiki/03-design-system.md`, `04-navigation-and-frame.md`, `05-component-catalogue.md`, `13-faceplates-alarm-lists-interlocks.md`, `16-component-selection.md`, `17-tag-model-and-udts.md` |
| `wiki.builder` | array of string | yes | The pages a page builder reads: `wiki/18-view-builder-reference.md`, `08-generation-and-validation.md` |
| `wiki.tags` | array of string | yes | The pages a tag engineer reads: `wiki/17-tag-model-and-udts.md`, `06-parent-project-and-library.md` |
| `tag_model` | object | yes | `device_path: "<tagRoot>/<id>"` with `id` holding `<hierarchy>/<leaf>` (section 9.5); `types_root: "_types_/<parent>"`; `variants_root: "_types_/<child>"`; `types_file: "library/udt-types.json"`; `member_folders: [mnt]`; `shapes`: array of `{id, measured, fact, test}`, one per shape of section 9.2 (section 9.3); `write_paths`: array of `{path, confirmed}`, one per write path of the profile (C18) |
| `standard.version` | string | yes | `0.2` |
| `standard.implements` | array of `{rule, how, check}` | yes | Every rule the HMI standard marks `carried_by` `library` or `both` (STD-WFB-01 section 3.1, `rules.json`), each with how the library carries it and the rule's check. Among them: `HMI-VIS-01` and `HMI-VIS-02` (the visibility measure of section 6 and the artwork element of section 7; checks `CK-VIS-01`, `CK-VIS-02` by `page_checks.py`), `HMI-UDT-01` to `HMI-UDT-04` (`library/udt-types.json`; check `CK-UDT-01` by gate G7 devices with `--types-file`), `HMI-HIS-01` and `HMI-HIS-05` (the history keys of page 17 section 8; check `CK-HIS-01`), `HMI-TAG-01` and `HMI-TAG-02` (checks `CK-TAG-01`, `CK-TAG-02` by `page_checks.py`), and the display and alarm rules the library's frame, faceplates and alarm tables carry (`HMI-DSP-18`, `HMI-DSP-22`, `HMI-ALM-05`, `HMI-ALM-06`, `HMI-ALM-07` and the others so marked) (LR1). The library writes the list from `library/hmi-rules-carried.json`, a copy of the rows of STD-WFB-01's `rules.json` marked `library` or `both` (`id`, `check`, `how`), which the library session refreshes when the standard's version changes; the library never reads WorkflowBuilder's files |
| `visibility` | object | yes | The thresholds of section 6.3 Table 6.3, so that the manager reads them and never restates them |

### 4.3 The Commands

Table 4.2 lists the commands the manifest publishes. `interpreter` is `plain` (the standard library and `jsonschema`) or `gate`
(an interpreter with Playwright); the host decides which interpreter answers each, and the manifest never names a path on a
host.

| Name | Script | Interpreter | Modes or purpose | Exit codes |
|---|---|---|---|---|
| `parent` | `tools/hmi/parent.py` | plain | Builds a parent, `--name`, `--out`, `--deploy` | 0, 1 |
| `generator` | `tools/hmi/screen.py` | plain | Builds a child, gates G0 to G7, `--render`, `--frame`, `--faceplate`, `--faceplate-mode`, `--parent`, `--local-kinds`, `--devices-file`, `--tags-file`, `--types-file` (new, section 9.7), `--report` | 0, 1 |
| `page_checks` | `tools/hmi/page_checks.py` | plain | Coverage, navigation, tags bound, layout L1 to L12, and the visibility checks of section 6 (`--visibility`) | 0, 2, 1 |
| `library_gaps` | `tools/hmi/library_gaps.py` | plain | Page, survey and release modes | 0, 2, 3, 1 |
| `asm_model`, `asm_descriptors` | `tools/hmi/asm_model.py`, `asm_descriptors.py` | plain | The ASM model and its descriptors | 0, 1 |
| `conformance` | `tools/hmi/conformance.py` (new) | plain | Section 5 | 0, 2, 1 |
| `udt_types` | `tools/hmi/udt_types.py` (new) | plain | Writes `library/udt-types.json` and derives a site's variants (section 9.3) | 0, 1 |
| `capture` | `tools/compare/capture.py` | gate | G8 and, with `--visibility`, the rendered measure (section 6.2) | 0, 1 |
| `faceplates` | `tools/compare/faceplates.py` | gate | G11 | 0, 1 |
| `glass_gates`, `alarm_probe`, `sidebyside`, `walk` | `tools/compare/<name>.py` | gate | The evidence pack's sweeps and the walk | as today |
| `install_module_list` | `module/tools/install_module.py --list` | plain | The gateway's module list, `cadre-hmi-installed-modules/1` | 0, 1 |

### 4.4 What Each Read of Section 3.1 Becomes

Table 4.3 maps each read of the library in the manager to its manifest field and the package that moves it. A read that stays
is a host fact, never a library fact.

| Read today | Manifest field | Package |
|---|---|---|
| `tool_repositories.openbridge.path`, the checkout's HEAD | None: the engagement's library entry (name, commit, worktree) of WP-L2 | WP-L2 |
| `GENERATOR_SCRIPT`, `OFFLINE_SCRIPT`, the compare script paths, `MAP_PATH`, `ELEMENTS_PATH` | `commands.<name>.script`, `module.files.map`, `module.files.elements` | WP-L2 (the blocks read the manifest of the pinned worktree) |
| `GENERATOR_SCOPE`, `_ASM_PATHS`, `MERGE_GENERATED`, `PARENT_COPY` | `library.paths`, `parents[].build` | WP-L2 |
| The three host paths of `screen-page-build-v3.json` | `commands.generator`, `commands.page_checks` | WP-I4 |
| `COMPONENT_KINDS` of block 18; `KINDS`, `LIBRARY_KINDS` of `page_checks.py`; `BUILTIN` of `library_gaps.py` | `catalogue.element_kinds`, `catalogue.kinds` | WP-L1 (the library's two lists derive from the same tables), WP-F4 (block 18 reads the manifest) |
| The `--frame` and `--faceplate` literals of the blocks, the workflow's `build_options` default | `build_options` | WP-L2 |
| `target.parent_project` default, `PARENT = cadre_hmi_base` | `parents`, `parents_default` | WP-L2, WP-I3 |
| `design_standard.library_wiki` (four globs) | `wiki.design` | WP-L2 (the profile keeps a client layer only, `client_wiki`) |
| `openbridge/module_release.py` alone, to install the module | `module.id`, `module.version`, `module.sha256` | WP-L2 pre-flight check against the installed-modules list (C10) |
| The eight schemas under `src/wfb_blocks/openbridge/schemas/` that copy a library schema (asm model, descriptor coverage, glass gates, library gaps 1 and 2, preview checks, project survey, side by side); the three manager-only schemas stay the manager's | `schemas.<name>.sha256` | WP-L1 conformance block (WFB-333): a drift fails `wfb engagement new` and `refresh` and warns at the pre-flight; the first L1-W build writes the eight copies again from the library, `library-gaps-1` among them |
| `interpreter: ctig` and the manager's `python_environments` | None: a host fact of the manager settings | Stays |
| `target.library.reference_commit`, `accepted_differences`, `survey` | None: engagement facts about one gateway and one survey | Stay in the profile |

### 4.5 The Module-Only Kinds and the Generator's Tables

The manifest's `catalogue.parts` is the one source of the kind tables. To make it so, and to close MAP-PROPOSAL section 6.1 and
REPORT-T3 section 10 item 2:

1. `module/tools/gen_module_assets.py` shall write, for each component of `module/components.json`, a `library` block
   `{kind, role}` (`role` one of `device`, `module-only`, `frame`, `none`), from a table in the generator's sources; the 15
   kinds whose part name differs from `part_name(kind)` (MAP-PROPOSAL section 5.3) are named there, so `part_name` is no longer
   used to find a part.
2. `screen.py` shall derive `MODULE_KIND`, `MODULE_ONLY` and `FRAME_ONLY` from those blocks at import. A test holds the derived
   tables equal to today's literals before the literals are removed.
3. `placement_survey.Rules.library_of` shall place a kind of role `module-only` as `module` with the component as its resolution
   (MAP-PROPOSAL option (a)), with no `library` fall-back, since no library view exists for it. A kind of role `frame` is never
   placed. The design then maps the pilot's electrical components to the module-only kinds Table 10 of wiki 16 offers, and
   `check_coverage` counts them as library kinds.
4. The parameter rules (`MODULE_EXCEPT`, `MODULE_NEEDS`, `MODULE_PARAM`, `MODULE_DROP`, `MODULE_IF_LISTED`) stay literals in
   this revision; moving them is REPORT-T3's second step and is not needed by any package here (section 17).

### 4.6 Versioning of the Manifest Format

The `schema` constant carries a major version. A reader shall refuse a manifest whose major it does not know and shall accept
added optional fields within a major. A field is never removed or retyped within a major; a change of meaning takes a new
major and a new schema file beside the old one. The manager records the manifest's `schema` and `library.digest`, and the
worktree's commit, in every block record that ran a library command, so a run states which contract it read.

### 4.7 Decisions and Alternatives

1. **A generated file in the library, not a document the manager derives at read time.** Alternatives: (a) the manager reads
   `screen.py`'s tables by import, which binds the manager to the library's Python and its interpreter; (b) a hand-written
   manifest, which drifts as the map did (MAP-PROPOSAL section 1.5). The generated file cannot drift from the code, and a
   library that is not this one can publish the same shape (principle 9).
2. **One file for catalogue, commands, options, wiki and standard.** Alternative: one file per concern. One file gives one
   digest to pin and one schema to check; the file is about 60 KB, read once per block.
3. **Interpreters named by class, not path.** Alternative: the manifest names `F:/repos/Citect-Ignition-Migrator/.venv`, which
   ties the library to a host (the defect of NOTE-WFB-14 section 4.4).
4. **The engagement's library facts leave the profile.** Alternative: keep the copies and check them against the manifest. A
   copy that must equal its source is a second source; the profile keeps only what is the engagement's own (section 4.4).

## 5. The Conformance Check

### 5.1 Command Line

`python tools/hmi/conformance.py --library <root> --out <dir> [--installed-modules <file>] [--standard-version <v>]
[--standard <rules.json>] [--strict] [--fixtures <dir>]`. `--library` is the root of a checkout or worktree; `--installed-modules` is a
`cadre-hmi-installed-modules/1` file the caller obtained from a gateway (the tool contacts none; the manager's conformance block obtains it by
`install_module.py --list`, read only, through the lane `openbridge.module_release` uses); `--standard` is WorkflowBuilder's
`standards/hmi/rules.json`, given on the manager side only (C14); `--standard-version` is
the HMI standard version the caller requires (default: the manifest's); `--strict` makes a dirty tree a failure instead of a
warning; `--fixtures` is the folder of smoke descriptors (default `tests/fixtures/conformance/`).

### 5.2 The Checks

Table 5.1 lists every check with its id, what it compares and its verdict class. A `fail` fails the check; a `warn` is
reported and fails nothing; a check that cannot run for want of an input is `skipped`, never `pass`.

| Id | Check | Class |
|---|---|---|
| C01 | `library/manifest.json` exists and validates against `schemas/cadre-hmi-library-manifest-1.json`; its `schema` major is known | fail |
| C02 | The manifest is fresh: a generation in memory by `library_manifest.build()` equals the file byte for byte, `library.generated` excepted | fail |
| C03 | `library.digest` equals the digest computed on the checked-out tree; the tree is clean on `library.paths` (`--strict`: fail; else warn) | fail or warn |
| C04 | Every `catalogue.kinds` entry has a view in `library/contracts.json` and a key in the profile's `kinds`; every `device_kinds` entry has a profile `deviceKinds` entry with a `faceplate` that is a view of the catalogue | fail |
| C05 | Every `catalogue.parts` entry names a component of `module/components.json` whose `element` is a tag of `module/openbridge-elements.json`; every component's `library.kind` is in exactly one of the three kind lists or has role `none` | fail |
| C06 | Every `reviewed` or `approved` row of the map names an element of the elements list (as `check_map_rows`); a row that contradicts a component (the `generator` row of MAP-PROPOSAL section 6.3) is reported | fail, warn for the contradiction (WFB-331) |
| C07 | `schemas.descriptor.id` equals the `schema` const of the descriptor schema file (for example `cadre-hmi-screen/1`; the file's `$id` is a URL, recorded as `schemas.descriptor.url`); every key of `catalogue.element_kinds` is a top-level array of the schema and every top-level array of elements is a key (two-way); each `schemas.<name>.sha256` equals the file | fail |
| C08 | The generator emits the schema: each fixture descriptor of `--fixtures` (one per element kind, the artwork element and a local assembly among them) builds offline against the default parent with G0 to G7 passing and no contract error; the fixture set covers every element kind | fail |
| C09 | `module.version` equals `version` of `module/build.gradle.kts`, the version `module/CATALOGUE.md` states, and, with a release file, the version inside the `.modl` manifest; `module.sha256` equals the file's digest | fail |
| C10 | With `--installed-modules`: the module `module.id` is listed, `state` running, `version` equal to `module.version`; `sha256` equal where the gateway's data folder could be read | fail |
| C11 | Every parent of `parents` builds offline into a temporary folder (`parent.py --name --out`) with gate G1 of wiki page 08 passing, and its `project.json` has `inheritable` true; `parents_default` is one of them | fail |
| C12 | Every path the manifest names is relative, normalised and resolves inside the library root (no `..`, no absolute path, no link leaving it); every path of `wiki.*` exists and its first heading is a title; every `commands.*.script` exists and answers `--help` with exit 0 under the plain interpreter (gate scripts: their module imports, no browser) | fail |
| C13 | `catalogue.element_kinds[k].draws` agrees with the generator's style: a kind that declares `border` has a class with a `border` rule in `library.style_classes(tokens)` or, for an SVG element, a stroke in the node the generator emits for the kind's fixture (C08's build); `fill` a `backgroundColor` or an SVG fill; a `section` without `border: true` or `title` declares no visible drawing (no section tone reaches `stroke_ratio`, section 6.3) | fail |
| C14 | `standard.version` is the required version; every `standard.implements[].rule` matches `^HMI-(DSP|VIS|NAV|ALM|TAG|UDT|HIS)-[0-9]{2}$` and every `check` is `null` or `^CK-` with the same area. With `--standard <rules.json>` (an option of the command line of section 5.1) (the manager side, which holds the standard): the set of `implements[].rule` equals the set of rules `rules.json` marks `carried_by` `library` or `both`, and each `check` equals that rule's `check` | fail |
| C15 | `library/udt-types.json` validates against `cadre-hmi-udt-types/1` and holds the eight types of Table 9.1, each with members equal to the union of its kinds' profile `deviceKinds[kind].members` in name and type, `cfg/` and `ilk/` members excluded | fail |
| C16 | The licence of `module.pin` is one of WFBD-012's and `NOTICE` names the package and its commit | fail |
| C17 | Every shape of section 9.2 has an entry in `tag_model.shapes`; an entry marked `measured` names a gateway fact present on wiki page 07 and a test present under `tests/`; no type or variant of `udt-types.json` needs a shape that is not declared (`HMI-UDT-05`, `CK-UDT-05`) | fail |
| C18 | `tag_model.write_paths` lists every write path of the profile's `writePaths`; each that changes a state or a setpoint (W1, W3, W4, W5 and W10 to W19) is `confirmed` true, and a library test of its confirmation row (wiki page 13 section 10.5) exists (`HMI-DSP-18`, `CK-DSP-18`) | fail |

### 5.3 The Report

The tool writes `<out>/conformance.json`, schema `cadre-hmi-conformance/1`:

```json
{"schema": "cadre-hmi-conformance/1",
 "library": {"root": "...", "commit": "...", "digest": "...", "manifest_digest": "...", "clean": true},
 "manifest": {"schema": "cadre-hmi-library-manifest/1", "module": {"id": "cadre.hmi.ob", "version": "0.8.0"}},
 "checks": [{"id": "C01", "verdict": "pass", "detail": "...", "evidence": {"...": "..."}}],
 "summary": {"pass": 18, "fail": 0, "warn": 0, "skipped": 0, "ok": true},
 "provenance": {"tool": "tools/hmi/conformance.py", "argv": [], "started": "...", "duration_s": 0.0, "interpreter": "..."}}
```

`summary.ok` is true when no check failed. Exit codes: 0 `ok`; 2 a check failed; 1 an input fault (no manifest, no git, an
unreadable file). The report is strict JSON (COB-210).

### 5.4 Where It Runs

The check runs in both repositories from the one tool (principle 3):

1. **Library side.** `tests/test_conformance.py` runs C01 to C09 and C11 to C18 on every commit (C10 needs a gateway and is
   skipped). A library commit that fails is not merged; the Sandbox follows by merge only (COBD-053), so it never fails on its
   own.
2. **Manager side.** A new block `openbridge.conformance` runs the tool against the engagement's pinned worktree and adds
   C10 from the gateway's module list (the block `ignition.*` that lists modules supplies the file; the tool reads it). The
   block runs in `wfb engagement new` and `refresh` before a library or a commit is accepted, and as a pre-flight check of
   every run (the pre-flight gains `library_conformance`, which fails the run on exit 2). The block records the report and the
   manifest's `schema` and `commit`.

The reason for two callers: the library proves its own line; the manager proves the line it is about to read, at the commit
it pins, against the gateway it will deploy to, which only the manager knows.

### 5.5 Threat List

Table 5.2 names what the check refuses, and the check that refuses it.

| Threat | Refused by |
|---|---|
| A stale manifest: tables changed, file not regenerated | C02 |
| A hand-edited manifest, or one copied from another commit | C02, C03 |
| A kind in the catalogue with no view or no part | C04, C05 |
| A component whose element left the pinned package | C05 |
| A module version the manifest does not match: gradle, catalogue, release file or the gateway | C09, C10 |
| A gateway running the old module beside a library expecting the new (NOTE-WFB-14 section 4.7 item 5) | C10 |
| A schema the generator does not emit: an element kind in the schema with no node builder, or a builder with no schema | C07, C08 |
| A descriptor schema copy in the manager that drifted from the library's (WFB-333) | C07's digest, read by the block |
| A map row naming an element outside the list, or contradicting a component | C06 |
| A parent that no longer builds, or a default parent the list lacks | C11 |
| A wiki page moved or renamed after a design read it by path | C12 |
| A command the host cannot run (a renamed script) | C12 |
| An element kind declared to draw what its style does not (a `section` claimed visible) | C13 |
| A rule id outside the standard's areas, or a standard version the engagement does not require | C14 |
| UDT definitions whose members drifted from the profile | C15 |
| A pinned package under a licence outside WFBD-012 | C16 |
| A manifest path that leaves the worktree (`..`, an absolute path, a link) | C12; a traversal mutant in the corpus |
| A type that needs an unmeasured shape, or a state-changing write path with no confirmation | C17, C18 |
| A dirty library tree offered as a commit (a run would record a commit that does not hold the code it ran) | C03 `--strict` |

### 5.6 Acceptance Corpus

1. **The current line passes.** At Sandbox `506076c` (cloud `dd1958d`) the facts the check reads were measured for this
   document: 97 components, 96 with an element; 281 element tags; 15 kinds in `KIND_VIEW`, 12 in `MODULE_KIND`, 48 module-only
   and 33 frame kinds; 15 profile kinds and 15 device kinds, 13 faceplates, 19 write paths; 74 views in `contracts.json`;
   module `cadre.hmi.ob` 0.8.0; four map rows and three rejected entries, of which the `generator` row and the rejected
   `obc-indicator-generator` entry contradict the module (C06 warns, never fails, until the owner rules on the map proposal);
   parents `cadre_hmi_base` and `cadre_hmi_base_asm` build; wiki pages 03, 04, 05, 06, 08, 13, 16, 17 and 18 exist; twelve
   schema files. The first run of the tool records these as the corpus's expected values; C02 requires the manifest to be
   generated first, so the corpus is the generated manifest plus this list.
2. **One mutant per threat fails.** The library's test fixtures hold a mutated copy of the library for each row of Table 5.2
   that a file change can make (a manifest with `module.version` `0.7.0`; a `catalogue.kinds` entry `fuse`; a schema with an
   array `badges` no builder emits; a wiki path renamed; a `draws` of `section` with `border`), each asserted to fail on the
   named check and on no other.
3. **The gateway case.** With the installed list of the owner's gateway after WFBD-146 (module 0.8.0 active) C10 passes; with
   a list naming 0.7.0 it fails.

### 5.7 Decisions and Alternatives

1. **A library tool, called by a block, not a block that recomputes.** Alternative: the block reads the manifest and checks it
   with its own code, as `_survey.py` recomputes Table 7.5 today. That doubles the logic (WFBD-005); the block adds only the
   gateway fact.
2. **C08 builds fixtures rather than parsing `screen.py`.** Alternative: a static map of schema arrays to node builders. The
   build is the only proof the generator emits what the schema names; it runs offline in under a minute on the fixtures.
3. **A warning, not a failure, for the inert map contradiction.** The current line must pass (section 5.6), and the rows are
   read by no placement (MAP-PROPOSAL section 6.5); the owner's ruling on the proposal closes WFB-331.

## 6. Visibility

### 6.1 What Visible Means per Element Kind

Rule `HMI-VIS-01` requires every item of the original with a place on the page to be drawn visibly at that place, or to be a
gap the person accepts by name; `CK-VIS-01` is the measure of this section. Table 6.1 defines "visible" for every element kind
the descriptor holds, and the drawing the manifest's `catalogue.element_kinds[kind].draws` declares for it.

| Element kind | Descriptor array | Visible when | `draws` today | `draws` after WP-F2 and WP-F5 |
|---|---|---|---|---|
| `symbol` of a library or module kind | `symbols[]` | The component renders (`data-component` present), its SVG has a path with a stroke or a fill of alpha at least 0.3, its box is at least 24 by 24 px, and its identifier text shows where `hasTag` is true | `glyph`, `text` | unchanged |
| `symbol` of a kind the library lacks (the gap box) | `symbols[]` | Always visible (a dashed border and the text `GAP: <kind>`); counts as a gap only, never as the drawing of the row | `border`, `text` | unchanged |
| `section` | `sections[]` | A border of at least 1 px whose contrast against the surface beneath is at least `stroke_ratio` in every palette; a fill counts only at `stroke_ratio`, which no section tone of the library's palettes reaches (section 6.3); a label alone makes the label visible, not the section | `fill` (ratio 1.06:1 on the day palette, so invisible) | `border` when `border` is true; `text` and `border` (the band's rule) when `title` is set (section 7.5) |
| `label` | `labels[]` | At least one glyph after trimming, not `visibility: hidden`, an offset parent, text contrast at least `text_ratio` | `text` | unchanged |
| `well` | `wells[]` | A vessel outline (stroke at least 1 px, contrast at least `stroke_ratio`); the liquid and the band do not count | `fill` (the liquid at 0.5, the band at 0.2; with no mark reached only the band, which is below the 0.3 alpha floor, so invisible) | `stroke`, `fill` |
| `pipe` | `pipes[]` | Its path rendered with the stroke width of its size (small 2, medium 4, large 6, xl 10 px, plus a 2 px outline) and contrast at least `stroke_ratio` in the colour it takes with colour mode off | `stroke` | unchanged |
| `junction` | `junctions[]` | Never measured alone: a point the pipes meet at; visible through its pipes | none | unchanged |
| `line` | `lines[]` | A path with width at least 1 px and contrast at least `stroke_ratio`; dashed counts | `stroke` | unchanged |
| `button` | `buttons[]` | A border, or a fill, at `stroke_ratio` against its container, and its label text at `text_ratio` | `border`, `fill`, `text` | unchanged |
| `link` | `links[]` | The icon's SVG renders with a path of alpha at least 0.3 | `glyph` | unchanged |
| `bracket` | `brackets[]` | The bracket line and its label | `stroke`, `text` | unchanged |
| `bar` | `bars[]` | The track and the value fill, or the track and the value text | `fill`, `text` | unchanged |
| `trend` | `trends[]` | The chart renders with its axes and the title | `glyph`, `text` | unchanged |
| `alarmPanel` | `alarmPanels[]` | The list renders with its header row | `border`, `text` | unchanged |
| `assembly` part | `assemblies[].parts` | By the part's own kind above (`shapes` as `artwork` shapes) | by part | unchanged |
| `card` of a cards page | `rows[][]` | Its title text or at least one item visible | `fill`, `text` | unchanged |
| `artwork` (new) | `artwork[]` | Every shape renders with a stroke of at least 1 px, or a fill, at contrast at least `stroke_ratio`; every text by the label rule; one shape short fails the element | none | `stroke`, `fill`, `text` |

A readout is a `symbol` of kind `readout`: visible when its value text is non-empty; a value of bad quality is already G8's
quality overlay and is not counted twice.

### 6.2 The Measure

The measure runs twice, by the same rules, at two points of a run:

1. **The descriptor rule, offline, in block 24's exit check** (`page_checks.py`, new family `V1` to `V4`). For each coverage
   row with a source box, every element `coverage_map.json` names for it is judged by the manifest's `draws`: an element
   whose declared drawing is empty for the parameters it carries (a `section` without `border` or `title`, since no section
   tone reaches `stroke_ratio` against its page; a `well` without a vessel; a `label` with empty text) is `V1 invisible`. The element's
   box against the row's source box scaled to the canvas gives `V2 displaced` and `V3 undersized` (section 6.3). A row whose
   every element is invisible is a finding, as a row carried by nothing is today (`check_coverage`). `V4` is the gap case: a
   row drawn only by gap boxes and listed in no gap. The rule needs no gateway and stops a page before it is imported. Its inputs are the
   descriptor, `coverage_map.json`, the manifest and `facts/source-boxes/<unit>.json` (option `--source-boxes`), which block
   24's preparation writes from the inventory objects each row's entry names (their union box in canvas pixels, section
   6.3); a row with no source box is judged by `V1` and `V4` only. Table 6.2 states the declared rule per element kind.
2. **The rendered measure, on the glass, in the evidence pack** (`capture.py --visibility`, with its existing `--base`, `--route`, `--out` and `--viewport`; new script
   `tools/compare/visibility.js`, output `visibility.json`, schema `cadre-hmi-visibility/1`). The script walks the `Diagram`
   coordinate container's children in order and descends into each child's open shadow roots (the `cadre.ob.*` web
   components of the module rendering); a child whose root is closed is recorded `unmeasurable`, and the declared rule
   decides it. For each child it records its bounding box, the
   computed border width and colour of its root and of its first bordered descendant, its background colour and the colour
   of the surface beneath it (the nearest ancestor with a non-transparent background), its visible text, and for each SVG
   path its stroke width, stroke paint, fill paint and opacity. `capture.py` joins the children to the view's JSON (the
   `Diagram` root's children of the built page, by order alone, since the DOM carries no component name: `Section_<id>`,
   `Text_<id>`, `Well_<id>`, `Line_<id>`, `Shape_<id>`, `Artwork_<id>`, `GAP_<id>`, `Button_<id>`, `Link_<id>`, `Bracket_<id>`,
   `Bar_<id>`, `Trend_<id>`, `AlarmPanel_<id>`, the pipes SVG's paths by order and the symbol embeds) and writes one record per
   element with its measured facts and the verdict of Table 6.1. `page_checks.py --visibility <dir>` then judges each
   coverage row against `visibility.json` in place of the declared `draws`, so the glass confirms the rule. The join by
   order is the one assumption the first corpus run must confirm (section 6.8 item 4).

Table 6.2. The declared rule (`V1`) per element kind, from the descriptor and the manifest alone.

| Element kind | Declared visible when |
|---|---|
| `symbol` | Its `kind` is in `catalogue.kinds`, `module_kinds` or `module_only_kinds`, and its box (stated, or the kind's default size) is at least `symbol_min_box` |
| Gap box | Never the drawing of a row; it counts only through `V4` |
| `section` | `border` is true, or `title` is a non-empty string |
| `label` | Its text is non-empty after trimming |
| `well` | `catalogue.element_kinds.well.draws` holds `stroke` (the vessel of section 7.5 item 3) |
| `pipe` | Its two ends resolve to symbols, junctions or points |
| `line` | It holds at least two points |
| `button`, `bracket` | Its label is non-empty |
| `link` | Its icon names an icon of the library |
| `bar` | It binds a value |
| `trend` | It names at least one pen |
| `alarmPanel` | It names at least one folder |
| `card` | It has a title or at least one item |
| `artwork` | It holds at least one shape, and its shapes equal the facts file's (section 7.6 item 3) |
| `assembly` part | By the part's own kind above |

### 6.3 Thresholds

Table 6.3 gives the thresholds, their units and reasons. The manifest's `visibility` object carries them; the manager reads
them and never restates them.

| Name | Value | Unit | Reason |
|---|---|---|---|
| `stroke_ratio` | 3.0 | relative luminance ratio (WCAG 2.1) | The non-text contrast of WCAG 2.1 success criterion 1.4.11 (3:1 for the boundary of a component), for strokes and for fills. The recorded loss lay below it: on the day palette the section tone `rgb(240)` against the page `rgb(247)` is 1.06:1, a card `rgb(252)` 1.03:1, the largest fill step `rgb(255)` against `rgb(240)` 1.14:1, and the divider `rgb(221)` 1.27:1 against the page and 1.19:1 against a section; `--element-neutral-color` is 6.75:1 on the section tone. T-L1-06b proves the paints of Table 6.1 reach it in every palette (LR3) |
| `text_ratio` | 4.5 | relative luminance ratio | WCAG 2.1 success criterion 1.4.3 for text below 18 pt; the library's label font is the smallest text drawn |
| `alpha_floor` | 0.3 | opacity times paint alpha | The well's band is 0.2 and the liquid 0.5 (`WELL_BAND`, `WELL_FILL`): the band alone, the recorded loss, must not count as a drawing |
| `min_box` | 8 | px, each axis | Every element kind but symbols (`symbol_min_box`) and junctions (never measured alone): below the smallest glyph the library draws (the 32 px automation badge, the 10 px range bar track); a flex container of zero size is the common failure |
| `symbol_min_box` | 24 | px, each axis | Half the 48 px symbol box; a symbol squeezed below it has lost its artwork |
| `stroke_min` | 1 | px | A hairline; the artwork element draws 2 px |
| `place_tolerance`, `place_cap` | 0.25, 48 | fraction of the scaled source box's own width and height; px | The layout rules L9 and L10 move elements by tens of pixels to meet pipes and clear texts; an element whose centre leaves the scaled source box grown by 0.25 of its size on each side, at most 48 px, stands in another region. A fraction of the canvas (about 285 by 129 px at 1900 by 860) would pass an element moved across the page (to be confirmed by the corpus, LR4) |
| `size_floor`, `size_ceiling` | 0.5, 2.0 | ratio of rendered area to scaled source area | For `section`, `well`, `artwork`, `trend`, `bar`, `alarmPanel`, `card`: a panel drawn at a quarter of its original area no longer frames what it framed; symbols and labels are sized by the library and are exempt |

The scale from the original to the canvas is `sx = canvas_w / page_size_w` and `sy = canvas_h / page_size_h`, from the
inventory's `page_size` and the descriptor's `screen.width` and `screen.height` (1900 by 860 in the recorded run); the
place and size tests use the scaled source box. Each threshold applies in every palette of the library (day, dusk, night
and bright), with the paints that palette's tokens give.

### 6.4 Outputs

`page_checks.py` adds to `checks.json`: `visibility: {rows, visible, findings: [{uid, page, rule, hmi_rule, result, elements, reason}],
count, source: "declared" | "rendered"}`, where `rule` is `V1` to `V4`, `hmi_rule` the standard's rule id
(`HMI-VIS-01`) and `result` one of `pass`, `fail`, `advice` and `not_applicable` (STD-WFB-01 section 11.2). `capture.py --visibility` writes `visibility.json`:

```json
{"schema": "cadre-hmi-visibility/1", "route": "/...", "viewport": [1600, 900],
 "elements": [{"name": "Section_s1", "kind": "section", "index": 3, "box": [x, y, w, h],
               "border": {"width_px": 0, "ratio": null}, "fill": {"ratio": 1.06},
               "text": "", "paths": [{"stroke_px": 0, "stroke_ratio": null, "fill_alpha": 0}],
               "visible": false, "why": "fill ratio 1.06 under 3.0, no border, no text"}],
 "provenance": {"tool": "tools/compare/capture.py", "...": "..."}}
```

### 6.5 Blocking

`CK-VIS-01` is a page item: in block 24's exit check every `V1` to `V4` finding is a defect of the round, and in the evidence
pack the item `offline:visibility` has cause `page` and fails the run (NOTE-WFB-14 ruling R4). The manager side (the evidence
setting that fails the run on page items, the final review's list of library and tool items) is WP-F1's manager half
(section 11.3).

### 6.6 Coverage Keys

Every caller of `page_checks.py` shall hand it the same rows under the same keys: the design's mapping rows
(`wfb.migration.project_design/1`), each row `{uid: entry, source: page, section, label}`, where `entry` is `<unit>:<id>` for an
understanding entry with an id and `<unit>:static.<n>` for the n-th static entry from 0 (`_v3.understanding_entries`). One change
makes it so: the evidence block passes the design's rows, built by the function block 24 uses (`page_build.mapping_rows`,
moved to `_v3`), in place of the ASM model's (manager, section 11.3). The ASM model keeps its own keys (`s<an>` from an
entry's `ans`, `tools/hmi/asm_model.py` `entry_uid`) and its tests: no caller of `page_checks.py` reads the model's rows
any more. The 34 rows of section 3.2 are then one set under one key, and the item carries
signal again (WFB-316).

### 6.7 Threat List

Table 6.4 names each loss of NOTE-WFB-14 Tables 3.1 and 3.2 the measure must catch, and the rule that catches it.

| Loss (NOTE-WFB-14 row) | Caught by |
|---|---|
| Table 3.1, the well: liquid only, a grey band at the floor | `V1` on `well` (declared `fill` under `alpha_floor` with no mark reached; rendered: no stroke, band alpha 0.2) |
| Table 3.1, the fuses and limiters as titled sections | `V1` on `section` (fill ratio 1.06, no border); the label is visible but the row's element is the section |
| Table 3.2 row 1, seven stand-ins that draw nothing visible (protective devices, starters, UPS, power monitor, duty selector as sections; breakers and the transfer switch as plain switch icons) | `V1` for the sections; the switch icons pass `V1` and are caught by WP-F4 (a `switch` standing for a `breaker` is a kind claim, section 11.5) |
| Table 3.2 row 2, four sections used as boxes for static artwork | `V1` on `section` |
| Table 3.2 row 3, the well's walls | `V1` on `well` |
| Table 3.2 row 3, section titles as small captions | Not a visibility loss: the label is visible; the heading band is a style rule of section 7.5 and `HMI-DSP` |
| Table 3.2 row 3, pipes grey unless colour mode is on | `pipe` contrast measured with colour mode off: the grey passes `stroke_ratio` on the day palette (measured by the corpus); a pipe that fails it is a library item |
| Table 3.2 row 4, five lacking features declared as gaps (status badge, threshold lamp, PLC state lamps, button state colour, generator state text) | Not by `V4`, which passes a row in a gap: the five were declared gaps, which `check_coverage` already handles. They close by the parts of WP-F5 and by the person's acceptance by name, which `CK-VIS-04` lists on the final review (`HMI-VIS-04`) |
| Table 3.2 row 7, three items lost between the understanding and the descriptor with no gap | `check_coverage`'s missing row, as today, now a failing page item |
| Table 3.2 row 8, cell borders absorbed into tables | A deliberate design choice recorded as a design row with `treatment` and no element: passes as today |
| Section 3.3 item 5, offline coverage at 157 of 191 | Section 6.6 |

### 6.8 Acceptance Corpus

Honest drawings the measure shall pass, held as fixture descriptors with their expected `visibility.json` and the rendered
measure run once on the owner's gateway for the record:

1. A readout that is text only (`readout` with a value and no identifier): visible by its value text.
2. A section with `border: true` and the page fill: visible by its border; the same section without `border` and without
   `title`: invisible (the recorded loss, asserted as the negative control).
3. A section with `title` under the heading band style: visible by the band's fill and text.
4. A pipe of each size with colour mode off: visible by its stroke; a pipe of medium `fresh-water` with colour mode on: the
   same.
5. A well with its vessel (after WP-F5) and no mark reached: visible by the vessel's stroke; the well of the recorded page
   child (`p1-r2`, four marks) on today's renderer: invisible.
6. An artwork element of each form (rectangle, ellipse, polyline, polygon, text): visible by stroke or text.
7. A module-only electrical symbol (`resistor`) and a module `pump`: visible by glyph.
8. The join by index of section 6.2: on the component test page the names of the view's `Diagram` children equal the
   recorded elements one for one; a mismatch fails the corpus and the measure falls back to the declared rule until fixed.
9. The recorded run replayed: the page child's three built pages, judged by the declared rule on their descriptors, give
   the findings of Table 6.4 and no other.

### 6.9 Decisions and Alternatives

1. **Two measures, one rule.** Alternative: the rendered measure alone. It needs a gateway and an import, so a page would fail
   late and cost a round; the declared rule stops it in block 24's check. Alternative: the declared rule alone. It cannot see
   a style the palette hides or a component that renders empty; the glass is the proof `HMI-VIS-01` asks for.
2. **DOM facts, not pixel analysis of the screenshot.** Alternative: compare the screenshot's pixels inside each box with
   the background. Anti-aliasing and the palette's low contrast make a pixel count ambiguous, and it cannot name the
   element. The DOM gives the computed colours and paths and the box of each named node.
3. **Contrast as a luminance ratio.** Alternative: a colour distance (CIE delta E). The ratio has a public definition, one
   formula and known anchors (3:1 for text); the palette steps it must separate are tonal.
4. **A per-kind definition, not one rule.** A symbol, a pipe and a label are visible in different ways; one rule ("a border or
   a fill unlike the container") would fail every label and pass no pipe.

## 7. The Artwork Element

### 7.1 Purpose

Rule `HMI-VIS-02`: a stand-in for a kind the library lacks shows the original's shape at its place and size. The artwork
element is that stand-in (NOTE-WFB-14 ruling R3, principle 1): a descriptor element that redraws the original's static artwork
and unclassed equipment from the captured geometry, in a neutral style, with no state and no click. It replaces the `section`
the recorded design used as a box and the plain `switch` icon it used for a breaker.

### 7.2 The Schema Change

The descriptor schema (`cadre-hmi-screen/1`, within the major: an added optional array) gains `artwork[]`, a diagram layout
element. Table 7.1 gives its keys; Table 7.2 the keys of a shape.

| Key | Type | Req | Meaning |
|---|---|---|---|
| `id` | string | yes | The element's name; `coverage_map.json` names it as `{"kind": "artwork", "id": ...}` |
| `x`, `y`, `w`, `h` | number | yes | The element's box on the canvas; `w` and `h` at least 1 |
| `shapes` | array of shape | yes | At least one; coordinates in pixels from the element's top left corner |
| `title` | string | no | A heading band across the top of the box (section 7.5) |
| `source` | object `{unit, ans: [string]}` | no | The understanding entry's unit and the inventory objects redrawn (`<target>:<an>`), informative; never read by the renderer |

| Key | Type | Req | Meaning |
|---|---|---|---|
| `id` | string | yes | The shape's name within the element |
| `form` | enum `rect`, `ellipse`, `polyline`, `polygon`, `text` | yes | What is drawn |
| `x`, `y`, `w`, `h` | number | yes for `rect`, `ellipse`, `text` | The shape's box within the element |
| `points` | array of `[x, y]` | yes for `polyline`, `polygon` | At least two points (three for a polygon) |
| `text` | string | yes for `text` | The glyphs; `align` as for a label |
| `width` | number | no | Stroke width in px, default 2, minimum 1 |
| `style` | enum `solid`, `dashed` | no | Default `solid` |
| `filled` | boolean | no | Default false; true fills a `rect`, `ellipse` or `polygon` with the neutral fill (section 7.4) |

The shape set is the `partSet.shapes` of the local assembly (`rect`, `ellipse`, `polyline`, `polygon`) plus `text`, `width`,
`style` and `filled`. G0 rules for the element: every shape within the element's box (a point outside by more than 2 px is an
error); a `text` shape at least 8 px high; `id` unique within the page; no `bind`, `device` or `faceplate` key (an artwork
element has no state and opens nothing). `page_checks.KINDS` gains `"artwork": "artwork"`, so a coverage row may be carried by
one; `library_gaps.BUILTIN` gains `artwork`, so it is never a kind of the catalogue.

### 7.3 The Renderer's Contract

`screen.artwork_node(a)` returns one `ia.shapes.svg` node named `Artwork_<id>`, positioned by `pv.cpos(x, y, w, h)`, with
`viewBox 0 0 w h` and `preserveAspectRatio: none`, holding one SVG element per shape in the shape order: `rect`, `ellipse`,
`polygon` and `path` as `assembly._shape_node` draws them, a `text` shape as a `text` element in the label font. The stroke is
`var(--element-neutral-color)` at `width`, dashed with `LINE_DASH` for `style` `dashed`; the fill is `none`, or for `filled`
`var(--container-section-color)` at opacity 1. The node is drawn after the sections and before the pipes, so a box drawn as
artwork sits under the equipment the builder places on it. A `title` adds a heading band as section 7.5 defines. The element
takes no colour, class or style from the descriptor (as the local assembly, wiki 16 section 6.3 item 3): the neutral style is
the rule, not a default. The generator is deterministic: the same descriptor gives the same bytes (wiki 18 Table 1).

### 7.4 The Style Rule

Artwork is neutral: one stroke colour (`--element-neutral-color`), one fill (`--container-section-color`), the label font for
text, no state colour, no animation, no icon. The reason: the artwork says "this was here, with this shape"; a colour would
claim a state the page has no tag for (COBD-038: a page shows nothing the source does not state). The original's `line_rgb`
and `fill_rgb` are not carried. This is the rule the standard states as `HMI-VIS-02`'s style clause and the design brief cites.

### 7.5 Sections, Headings and the Well

Three parts of the library change beside the new element, each a small addition within the schema's major:

1. **A section may draw its border.** `sections[]` gains `border` (boolean, default false): true draws a 1 px border in
   `var(--element-neutral-color)` (6.75:1 on the day section tone; the divider tone `--border-divider-color` is 1.19:1 on it,
   too faint, section 6.3) on the section's container; T-L1-06b proves the paint in every palette. A section the design uses as a box for equipment states `border: true`; its `draws` then includes `border`.
2. **A section title may be a heading band.** `sections[]` and `artwork[]` take `title` (string): a band across the top of the
   box, the subtitle font (`cadre/font/subtitle cadre/text/active`), left aligned, with a 1 px rule beneath it in the border paint of item 1, in place of
   the small right-aligned caption of `label`. `label` stays for a caption. `page_checks.title_band` reads the band's box for
   rule L10. The band is visible by its text and its rule; its fill, the section tone, does not count (section 6.3).
3. **The well draws its vessel.** `parts.well_node` adds, before the liquid and band paths, an outline path of the well's box
   (a `rect` of stroke 2 px in `var(--element-neutral-color)`, no fill), so a well with no mark reached shows its walls. The
   `wells[]` schema does not change.

### 7.6 Where the Geometry Comes From in the Run

The geometry is the inventory's (section 3.3). The flow through the stages:

1. **Understanding (block 13):** unchanged. A static entry's `ans` and a device entry's `ans` name the inventory objects.
2. **Design (block 18):** a mapping row may name `component: "artwork"` for a static entry of class `frame`, `artwork` or
   `legend`, and for a device whose kind has no catalogue kind, no module-only kind and no local assembly; the row's `note`
   names the gap row where the kind is a gap (WP-F3 queues it). The brief's rule "draw the nearest honest library part"
   (`project-design.md` section 3 item 6) is amended: where no library kind or module-only kind is honest, the row names
   `artwork`, never `section`. The design check (WP-F4) refuses a `section` row for a device entry (section 11.5).
3. **Page build preparation (block 24, `open_tools`):** the manager writes `facts/artwork/<unit>.json`: for every design row
   with `component` `artwork` on a page of the group, the shapes of the entry's `ans` objects, each inventory object made a
   shape (`SquareV3` a `rect`, `CircleV2` an `ellipse`, `Line` and `PolyLineV2` a `polyline` from `nodes`, `Text` a `text`,
   `Symbol`, `Genie`, `Bitmap` and `Set` a `rect` at their box), in canvas pixels by the uniform scale `s = min(sx, sy)` of section 6.3,
   centred in the box scaled by `sx` and `sy` so that ellipses and text keep their aspect, relative to the union box of the
   objects; a `Line` whose `nodes` is empty becomes a straight segment along the longer side of its box, through its centre. The builder copies the element into the descriptor and may move the box; it shall not add,
   drop or restyle a shape (the check compares the descriptor's shapes with the facts file, as the coverage map is compared).
4. **Renderer:** section 7.3.

### 7.7 Decisions and Alternatives

1. **A new element, not `assemblies.partSet.shapes`.** The assembly is a part set per kind with a device, a faceplate and a
   local kinds list (G0 refuses it without one); artwork has no device and no kind. Reusing it would make every panel a
   device.
2. **A new element, not a bordered section.** A section with a border is one rectangle; the losses are polylines, ellipses,
   texts and groups (section 3.3). The bordered section is kept for the box case because it costs one key.
3. **Geometry prepared by the manager, not read by the library from the inventory.** The inventory is ctig's schema; a library
   tool that reads it binds the library to ctig (WFBD-005 in reverse). The descriptor stays the interface (wiki 08 section 7),
   and the manager, which already reads inventories, prepares the shapes.
4. **Shapes copied, not computed by the builder.** An agent redrawing geometry from a picture invents; the facts file is
   checked against the descriptor as the coverage map is.

## 8. The Kinds of WP-F5

Table 8.1 takes each kind of NOTE-WFB-14 Table 3.2 row 1 and WP-F5 and states whether the 0.8.0 module draws it today
(`module/components.json`, wiki 16 section 7 Table 10), what remains and the package. "Placement only" means the kind needs
no library part: section 4.5 item 3 makes it placeable and the design names it.

| Kind of the original | Drawn by the module today | What remains | Package |
|---|---|---|---|
| Resistor, capacitor, diode, ground, source, converter, transformer, transistor, logic, router (electrical symbols) | Yes: `cadre.ob.resistor` and the ten others, module-only, 48 by 48 px | Placement only | WP-L1 (section 4.5) |
| Busbar | Yes: `cadre.ob.bus`, 200 by 24 px | Placement only; the `bus` map row's state (MAP-PROPOSAL section 3.2) | WP-L1 |
| Breaker and transfer switch with open, closed and tripped states | No: the design used `switch` (two states) | A `breaker` kind: the switch glyph with a third, tripped state and the alert frame; drawn as a library view under both renderings | WP-F5 |
| Fuse and fault current limiter | No | An in-line `fuse` kind and a `limiter` variant, display only, with a blown state where a tag exists; until built, the artwork element draws them (WP-F2) | WP-F5 |
| Motor starter (direct on line, variable speed drive) | No: `converter` is a glyph, not a starter box | A `starter` kind: a labelled box above a motor with run, fault and mode marks, `params.variant` `dol` or `vsd` | WP-F5 |
| Status badge beside an instrument or pump label | Partly: `cadre.ob.automationbadge` is a module-only glyph with no binding | A `badge` option on `labels[]` (`badge: {tag, states}`), or the automation badge given a `bind` | WP-F5 |
| Threshold lamp (a lamp from an expression over a value) | No: `indicator` takes states of one tag | `indicator.params.threshold` `{member, op, value}`, evaluated in the view's expression, so no derived tag is invented | WP-F5 |
| Tank with discrete level marks | Partly: `cadre.ob.tank` draws an analogue level; the `well` part draws marks without a vessel | The well's vessel (section 7.5 item 3); a `marks` option on `tank` for level switches without an analogue level | WP-F5 (the vessel in G3's first package, section 10) |
| UPS panel, power monitor panel, duty selector panel | No | Not a library kind: each is a box of readouts and lamps; drawn as an artwork element with the readouts and indicators the design places on it (WP-F2); a `ups` kind waits for a second project that needs it (principle 6) | WP-F2 |
| PLC state lamps, a button's state colour, a generator state text | Partly: `indicator` and `labels[].emphasis` exist | A `words` map on labels for a state text (`emphasis.words` exists for two words); a button `state` colour is an `HMI-DSP` rule first | WP-F5 (words), WP-S1 (button colour) |
| Alarm list and acknowledgement items of the evidence | Yes: `cadre.ob.alertlist`, `alertpanel` | The five failed library items of the recorded pack (alarm rows after a one-tag import, the list, the acknowledgement) are library defects to fix, not kinds | WP-F5 |

The contracts of the new parts (`breaker`, `fuse` and `limiter`, `starter`, the label badge, the threshold, the tank marks and
the words map) are not stated here: each is designed in the library session's own design note before package G3-6 builds it
(WFBD-134), with its descriptor keys, enumerations, states, sizes, drawing and binding, its threat list and its corpus, and
its tests come from that design. Two constraints bind it. First, a part drawn by a new module component needs a module
release and a gateway restart, which need the owner's approval (the library's `CLAUDE.md`; non-negotiable 6 here), so each
part is first a library view under both renderings where it can be, and C09 and C10 follow any release. Second, a threshold
compares one member with a number by an operator from the fixed list `gt`, `ge`, `lt`, `le`, `eq`, `ne`, never a free
expression, so no descriptor text enters a view's expression.

## 9. UDTs and Tag Structure

### 9.1 Where Tags Live

Tags live in a tag provider, not in a project. A parent and a child project hold views; the provider `[default]` holds the
folders their bindings read. Definitions sit only under the provider's own `_types_` folder (wiki 17 section 3.1, GF-51); an
instance names its type by `typeId`, the path below `_types_`. NOTE-WFB-14 ruling R8 says "one UDT per library kind in the
parent project and device instances in the child": read literally it cannot be done. This contract reads it as follows and
reports the wording as a conflict (WFB-332): the definitions of the library's types sit at
`[default]_types_/<parent>/<Type>`, `<Type>` a name of Table 9.1 (for the parent `cadre_hmi_base_asm_080`:
`_types_/cadre_hmi_base_asm_080/Pump`, one folder below `_types_`, the depth GF-54 measured), are written only by the
manager's tag import block with the owner's approval (section 9.8), never by a parent deployment, and are shared by every
child of that parent on the gateway; an engagement's variants (section 9.3) sit at `[default]_types_/<child>/<Type>_<set>`; the instances sit under the child's tag root
`[default]<child>/<id>` (`id` holding the hierarchy, section 9.5). Pairing the definitions with the parent's name lets two parents coexist (WFBD-146) with
their own definitions.

### 9.2 The Measurement Plan

Page 17 section 11 item 2 marks the shapes unmeasured. Before any site imports a definition, a cloud gateway session (the
throwaway gateway of `cloud/setup.sh`, no authorisation needed) measures each shape by import and export, recording each as a
gateway fact `GF-nnn` on wiki page 07 and a test under `tests/`:

1. A `Folder` (`mnt`, `cfg`, `ilk`) inside a `UdtType`, with members under it.
2. A memory member with a `value` inside a type, and its instance value.
3. One `String` parameter per member (`Src_<member>`) in `sourceTagPath` bindings: the measured one-parameter form of GF-54
   applied to many parameters of one type.
4. An instance that overrides one member's `sourceTagPath` (the alternative of section 9.3 item 3).
5. `historyEnabled` and `historyProvider` on a type member, and their override on an instance.
6. An `alarms` list on a type member (page 17 section 7.3), to confirm that alarms stay on source tags (GF-52) and the type
   carries none.
7. `system.tag.exists` on an instance's member and on a member the type lacks (GF-54 again, on the new shapes).
8. Gate G7 devices with `--tags-file` on an export holding instances, before and after `--types-file` (section 9.7).
9. The import order types first, then instances, by `deploy.import_tags("default", "", document)`, and a re-import of the
   types with instances present (does the instance follow the changed type).

A shape that fails measurement is not used; the plan names its fall-back (item 4 for item 3, an expanded folder for the whole
scheme). Each shape is declared in the manifest's `tag_model.shapes` with `measured` false until its fact and its test
exist (C17). No definition sits deeper than one folder below `_types_`.

### 9.3 Definitions

The library shall publish `library/udt-types.json` (schema `cadre-hmi-udt-types/1`), generated by `tools/hmi/udt_types.py`
from the profile's `deviceKinds` through `parent.py`, beside the profile. It holds the eight device types of Table 9.1, one
per device row of page 17 Table 2, each named without a folder; the manager's tag import block prefixes the folder from the
manifest's `tag_model.types_root` or `variants_root` with the engagement's parent or child name (section 9.8).

Table 9.1. The device types, the kinds each serves and where each sits.

| Type | Device kinds | Definition path | Members |
|---|---|---|---|
| `Pump` | pump, motor, fan | `_types_/<parent>/Pump` | The union of the three kinds' profile `members` |
| `Valve` | valve, analogvalve, damper | `_types_/<parent>/Valve` | The union of the three kinds' profile `members` |
| `Tank` | tank | `_types_/<parent>/Tank` | The kind's profile `members` |
| `Instrument` | instrument, readout, instrument-field | `_types_/<parent>/Instrument` | The union of the three kinds' profile `members` |
| `Controller` | controller | `_types_/<parent>/Controller` | The kind's profile `members` |
| `Indicator` | indicator | `_types_/<parent>/Indicator` | The kind's profile `members` |
| `Sequence` | sequence | `_types_/<parent>/Sequence` | The kind's profile `members` |
| `Generator` | generator | `_types_/<parent>/Generator` | The kind's profile `members` |

The rules of the types:

1. Each member is an `AtomicTag` of its profile `type`, `valueSource` `reference`, its `sourceTagPath` bound to the parameter
   `Src_<member path with / as _>` (`{Src_mnt_forceOn}`), each parameter a `String` with the empty value (LR7); the `mnt/`
   members sit in a `Folder` member `mnt` (shape 1 of section 9.2).
2. The history keys of page 17 Table 22 sit on the kinds' trend members, with `historyProvider` bound to the parameter
   `HistoryProvider` (`HMI-HIS-01`).
3. No alarm sits on any member (GF-52).
4. The `cfg/` members differ from site to site (page 17 section 3.2 rule 3): they are in no full-set type and enter a site's
   variants only. The interlock structures (`ilk/`, page 17 Table 2's `InterlockCondition` and `InterlockSummary`) stay
   provisional (page 17 section 11 item 3) and are excluded from this contract: a device that carries `ilk/` members is built
   as a folder of atomic tags.
5. The local device has no type (page 17 Table 2, `HMI-UDT-04`).

A site derives its variants: `udt_types.py --derive --devices <device model> --types library/udt-types.json --out <dir>` writes,
for each distinct pair (type, member set) of the device model whose set differs from the type's full set, the definition
`<Type>_<set>` holding exactly that set (page 17 section 2.2 rule 2 and section 3.2 rule 2). `<set>` is the first eight hex
characters of the SHA-256 of the sorted lines `<member> <data type>`, unless the device model entry's `udt.variant` holds a
readable name the person chose on the design review card; the tool refuses two sets whose names collide. A device whose member
set equals the full set names `<Type>` (LR8). The reason for the hash: variant names must be stable across runs with no person
in the loop; the reason for the override: a person names what an operator will read in the Designer.

The tool marks each variant with the shapes of section 9.2 it needs. A device whose variant needs a shape that
`tag_model.shapes` does not mark `measured`, or whose engagement sets the standard's `adopt_udts` false, is built as a folder
of atomic tags, as today: its `udt` is null and its `udt_reason` names the shape (`unmeasured:<shape id>`) or `adopt_udts`
(`HMI-UDT-01`, `HMI-UDT-05`).

### 9.4 Instances and Folders by Hierarchy

The build writes one `UdtInstance` per device under `<tagRoot>/<id>` (`id` holding the hierarchy, section 9.5): `typeId` the definition's path below
`_types_`, `parameters` each `Src_<member>` set to the source tag path ctig's bridge mapped (section 9.6), `HistoryProvider`
set to the engagement's provider, and a stub per member as the export returns it (page 17 section 9.3). The folders of
`<hierarchy>` are plain `Folder` tags, `<area>/<unit>`, from the design's hierarchy nodes (`HMI-TAG-01`); the device folder's
name is the last segment of `id`, the original's equipment id made safe for Ignition names (`HMI-TAG-02`: letters, digits, underscore and hyphen,
the schema's pattern). Tags of no device sit as `HMI-TAG-04` and `HMI-TAG-05` state, so nothing lies loose at the root: a
page's free readouts in `<tagRoot>/<hierarchy>/Values/`, the memory tags of a design gap in `<tagRoot>/<hierarchy>/Unsourced/`
(the folder names are the standard's parameters `values_folder` and `unsourced_folder`; `CK-TAG-02` refuses a device whose
`id` equals either within one parent). A free readout shown on pages of several nodes sits under their deepest common
node, or under the tag root where they share none (`HMI-TAG-04`). The document is a folder document importable at the provider root after the types.

### 9.5 The Device Model Entry

`schemas/devices.schema.json` (`cadre-hmi-devices/1`, within the major) gains two optional keys on a device, which are the
contract between classification (NOTE-WFB-16) and the build:

| Key | Type | Meaning |
|---|---|---|
| `hierarchy` | string, `^[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*$` | The device's plant hierarchy path below the tag root, `<area>/<unit>`; NOTE-WFB-16 defines how classification proposes it and the person ratifies it. One segment where an area has no unit; each segment made safe by `HMI-TAG-02`; at most the standard's `max_levels` segments. Absent: the device sits at the root (today's flat path), which `CK-TAG-01` accepts only where the person ratified no area (`HMI-TAG-01`) |
| `udt` | object `{typeId, variant}` or null | The definition the instance names and, where the person named it, the variant; written by `udt_types.py --derive`, read by the build and by gate G7 devices; null with `udt_reason` (`unmeasured:<shape id>` or `adopt_udts`) where the device is built as a folder (section 9.3) |

`id` stays what the schema and the library read today, the device's tag folder relative to the tag root (`gates.py` builds
`folder = f"{root}/{d['id']}"`; `screen.model_devices` and the faceplate folder key on it), and now holds the hierarchy:
`id == hierarchy + "/" + leaf` where `hierarchy` is present, else `id == leaf`, `leaf` being the original's equipment id made
safe (`HMI-TAG-02`). A descriptor symbol's `device` names the same `id`. So the path needs no change in `gates.py`,
`screen.py` or the faceplates: `hierarchy` is a checked prefix that `CK-TAG-01` reads, and `CK-TAG-02` judges `leaf`. The ASM model (`cadre-hmi-asm-model/1`) carries the same two keys
on its device entries, beside `node`, which stays the display hierarchy of pages (F033). `hierarchy` is the path classification ratified
(NOTE-WFB-16 section 11, its ruling CR8); the design takes each device's `node` from it (the root followed by
`hierarchy`) and places the device's own drawing on a page of that node (`HMI-DSP-23`), so the two agree; a device whose
two differ is a finding of `CK-TAG-01` (`HMI-ALM-10`: the alarm display path and the tag path name one node).

### 9.6 ctig's Bridge

Stage B2-tags of ctig (`src/ctig/bridge/tags.py`) writes today one reference tag per member on its source tag, with the
history keys where the device model marks the member historised. With UDTs it writes: (1) `tags_devices.json` as the
instances document of section 9.4, the parameters carrying the source paths it maps today; (2) `types_site.json`, the variants
from `udt_types.py --derive` (ctig calls the library tool by its command line, as the manager calls ctig; no library logic
enters ctig); (3) the device model with `hierarchy` and `udt`. The mapping of original tags to members (the census roles of the
site profile, the adapter, the bridge rules) does not change: a member's source is the same tag; only its form (a parameter
value instead of a reference tag's `sourceTagPath`) changes. A member with no source is absent from the variant, so no
instance carries a member its definition lacks (page 17 section 2.2 rule 2). This is ctig's package of WP-S2 and is stated
here as the interface; its build is ctig's.

### 9.7 Faceplates and Gates

The faceplates read folders and member names and never a `typeId` (page 17 section 2.1), so they read a UDT instance as they
read a folder today: no faceplate changes. Gate G7 devices with `--tags-file` does not read instances (page 17 section 10
item 12, WFB-330): `screen.py` and `gates.py` gain `--types-file <document>`, with which the gate expands each `UdtInstance` by
its `typeId` and parameters into the member leaves the folder carries, and checks them as it checks a folder. `CK-UDT-01`
(every device of a library kind with a UDT on page 17 is an instance of that UDT) is the gate's new check: a device of the
model whose `udt` is null, or whose folder in the tag file is a plain folder, with no `udt_reason`, is a finding; a device
with `udt_reason` is reported `not_applicable` with its reason (`HMI-UDT-01`), and the option `--adopt-udts false`, from the
engagement, reports every device so. `CK-HIS-01` reads the expanded
members' history keys against the model's `trend` (closing page 17 section 11 item 5). `CK-TAG-01` and `CK-TAG-02` are
`page_checks.py` rules over the device model and the tag document: every device's `hierarchy` is its ratified node path (one
or two segments, at most `max_levels`), or is absent only where the person ratified no area; and every folder name matches
the safe pattern, the device's own folder equals the last segment of its `id`, and collides with no other name of its parent folder without regard to case.

### 9.8 Writes to the Owner's Gateway

Writing under `_types_` on the owner's gateway is outside the folders the library's sessions write and needs the owner's
authorisation (COBD-035 item R6 authorised the measurement; writing an engagement's types is a new write). The manager's tag
import block asks once per engagement, on its approval card, naming the types document and the folder, and records the
answer in the run; the cloud gateway needs none. No write happens in this note.

### 9.9 Decisions and Alternatives

1. **One parameter per member, not one `Stem`.** Page 17 section 3.3 binds every member from one `Stem`. Citect tags of one
   device rarely share a stem (the pilot's census maps members from roles over varied names), so one stem cannot name them.
   One parameter per member keeps the measured one-parameter binding form and lets each source be any path. Alternative:
   per-instance override of each member's `sourceTagPath` (unmeasured, item 4 of section 9.2); kept as the fall-back.
2. **Variants by member set, not optional members.** A member with no source must not exist (GF-50, G11 fails on it), so a
   type cannot carry members an instance lacks. Alternative: reference members pointing at a placeholder tag, which invents
   data (COBD-038).
3. **Definitions under the parent's name.** Alternative: `_types_/Cadre/<Type>` shared by every parent. Two parents of two
   library lines on one gateway (WFBD-146) would then fight over one definition.
4. **The path in `id`, with `hierarchy` as its checked prefix.** Alternative: `hierarchy` beside a leaf `id`. Every reader of
   the library (`gates.py`, `screen.model_devices`, the faceplate folder) takes `id` as the folder below the tag root, so a leaf
   `id` would break every symbol's match and need changes in three files; the prefix field lets `CK-TAG-01` and `CK-TAG-02`
   judge each part.
5. **The design's hierarchy, not a tag naming convention.** Alternative: derive the area and unit from the Citect tag name's
   prefixes. The names of the pilot encode the equipment, not its area; the design already holds the plant hierarchy as nodes.

## 10. The Split of Packages

Table 10.1 gives each package with its repository, files, the single owner of each shared file, its tests and its order
within the group. The library packages are built in the cloud repository (`sreejitheg/cadre-ob-cloud`); the Sandbox follows by
merge (COBD-053). The manager packages are G2b's. Tests are written apart from the builder, from this document (section 13).

| Order | Package | Repository | Files (owner of a shared file in brackets) | Tests |
|---|---|---|---|---|
| G0-1 | F0-W Fixtures | Manager (local) | `src/tests/fixtures/g1_fixtures.py` (new, the orchestrating session), the fixture folders the tests of section 13 name | T-F0-01 |
| G3-1 | L1-A Manifest | Library | `tools/hmi/library_manifest.py` (new), `tools/hmi/parent.py` (L1-A: the write call), `schemas/cadre-hmi-library-manifest-1.json`, `library/manifest.json`, `module/tools/gen_module_assets.py` (L1-A: the `library` block), `tools/hmi/screen.py` tables (L1-A), `tools/hmi/placement_survey.py` `library_of` (L1-A), `tools/hmi/page_checks.py` (L1-A: `LIBRARY_KINDS` read from the manifest, so module-only kinds count as library kinds; `KINDS` gains `alarmPanels` and `rows`) | T-L1-01 to T-L1-06 |
| G3-2 | L1-B Conformance | Library | `tools/hmi/conformance.py` (new), `schemas/cadre-hmi-conformance-1.json`, `tests/fixtures/conformance/` (one descriptor per element kind, the mutants), `tests/test_conformance.py` | T-L1-07 to T-L1-12 |
| G3-3 | F1-L Visibility | Library | `tools/compare/visibility.js` (new), `tools/compare/capture.py` (F1-L: `--visibility`), `tools/hmi/page_checks.py` (F1-L: `V1` to `V4`, `--visibility`, `KINDS`), `schemas/cadre-hmi-visibility-1.json`, `tests/fixtures/visibility/` | T-F1-01 to T-F1-09 |
| G3-4 | F2-L Artwork | Library | `schemas/screen-descriptor.schema.json` (F2-L: `artwork[]`, `sections[].border`, `title`), `tools/hmi/screen.py` (F2-L: `artwork_node`, `section_node`), `tools/hmi/parts.py` (F2-L: `well_node` vessel), `tools/hmi/library_gaps.py` `BUILTIN` (F2-L), `tools/hmi/assembly.py` G0 rules (F2-L), wiki 18 section 9, `tools/hmi/page_checks.py` (F2-L: `title_band` reads the band), `tools/hmi/library.py` (F2-L: the border and band style classes; a parent rebuild follows, deployed with the owner's approval) | T-F2-01 to T-F2-06 |
| G3-5 | S2-L UDTs | Library | `tools/hmi/udt_types.py` (new), `library/udt-types.json`, `schemas/cadre-hmi-udt-types-1.json`, `schemas/devices.schema.json` (S2-L: `hierarchy`, `udt`), `tools/hmi/gates.py` and `screen.py` (S2-L: `--types-file`, `CK-UDT-01`, `CK-HIS-01`), `tools/hmi/page_checks.py` (S2-L: `CK-TAG-01`, `CK-TAG-02`), wiki 17 sections 3 and 11, wiki 07 (the facts of section 9.2), `tools/hmi/parent.py` (S2-L: the types file beside the profile), `schemas/cadre-hmi-asm-model-1.json` (S2-L: `hierarchy` and `udt` on device entries) | T-S2-01 to T-S2-08 |
| G3-6 | F5-L Parts | Library | Named by each part's own design note (section 8); the alarm list and acknowledgement defects of the evidence | From the part designs |
| G2b-1 | L1-W Conformance block | Manager | `src/wfb_blocks/openbridge/conformance.py` (new), `src/wfb_blocks/openbridge/schemas/cadre-hmi-conformance-1.json` (copy, digest-checked), `src/wfb/engagement.py` (L2 owns; L1-W adds the call), `src/wfb_blocks/migration/preflight.py` (L1-W: `library_conformance`) | T-L1W-01 to T-L1W-04 |
| G2b-2 | F1-W Visibility gate | Manager | `src/wfb_blocks/openbridge/evidence.py` (F1-W: the design's rows, the `offline:visibility` item, page items fail), `src/wfb_blocks/migration/page_build.py` (F1-W: `V` findings as defects, `--visibility`), `src/workflows/screen-page-build-v3.json` (I4 owns; F1-W sets the evidence setting) | T-F1W-01 to T-F1W-05 |
| G2b-3 | F2-W Artwork facts | Manager | `src/wfb_blocks/migration/page_build.py` (F2-W: `facts/artwork/`, the shapes check), `src/workflows/briefs/v3/project-design.md` and `page-build.md` (F2-W: the artwork rule), `src/wfb_blocks/migration/project_design.py` (F4 owns; F2-W adds `artwork` to the element kinds through the manifest) | T-F2W-01 to T-F2W-04 |
| G2b-4 | S2-W UDT import | Manager and ctig | ctig `src/ctig/bridge/tags.py` and `model.py` (ctig's package), the manager's tags import block (S2-W: the types document first, the approval card of section 9.8), `src/wfb_blocks/openbridge/asm_model.py` (S2-W: passes `hierarchy` and `udt`, which the library's `asm_model.py` writes) | T-S2W-01 to T-S2W-04 |

Order within G3: L1-A first (every later package reads the tables it derives and regenerates the manifest, C02), then L1-B (so every later package is checked),
F1-L (so F2-L and F5-L are measured), F2-L, S2-L, F5-L. Order within G2b: L1-W first, then F1-W, F2-W, S2-W; L2 (section 11.1)
precedes L1-W because the block reads the pinned worktree L2 provides, or reads the configured checkout until L2 lands.

## 11. Interfaces Consumed by the Packages Out of Scope

### 11.1 WP-L2, Library Choice per Engagement

WP-L2 consumes: `library/manifest.json` at the pinned commit (section 4) for every path, command, option, kind list and
wiki page the blocks read today (Table 4.3); `library.paths` as the set a pinned read-only worktree needs and the dirty check
covers; `module.id` and `module.version` for the pre-flight's comparison with the gateway's module list; `parents` and
`parents_default` for the profile's parent; `build_options.default` and `requires` for the profile's options; `wiki.design` for
the design's library pages (the profile keeps `client_wiki` only). WP-L2 provides to this contract: the engagement's library
entry `{name, commit, worktree}` the conformance block runs against, and the manifest's `schema` and `digest`, and the worktree's commit,
recorded in each block record.

### 11.2 WP-S3, Rules Enforced by Id

WP-S3 consumes: the check ids this contract implements and where each reports: `CK-VIS-01` in `checks.json.visibility`
(declared and rendered); `CK-VIS-02` by the manager's artwork facts check (section 7.6 item 3) together with `V1` on
`artwork`; `CK-TAG-01`, `CK-TAG-02` in `checks.json` over the device model;
`CK-UDT-01`, `CK-HIS-01` in the generator's report under `gates.G7_devices`; and the manifest's `standard.implements[]` for the
rules the library carries. Each finding carries its rule id, so the design sheet and the final review show it by id.

### 11.3 WP-F1, the Manager Side of the Visibility Gate

WP-F1's manager half consumes: `checks.json.visibility` and `visibility.json` (sections 6.2 and 6.4); the thresholds from the
manifest's `visibility` object; the key rule of section 6.6 (the evidence block passes the design's rows through the same
function block 24 uses, `page_build.mapping_rows`, moved to `_v3`), for which the evidence block gains the input `design` (the approved design file). It provides: the evidence item `offline:visibility` with
cause `page`; `fail_on_items` true for page items (the setting splits into `fail_on_page_items` true and
`fail_on_library_items` false, ruling R4); the final review's list of library and tool items.

### 11.4 WP-F3, Late Kinds as Run Gaps

WP-F3 consumes: `catalogue.kinds`, `module_only_kinds` and `parts` from the manifest, so the gap list resolves a device
model kind against the library's full drawing set (the electrical kinds are no longer gaps); a design row with `component`
`artwork` for a device entry, which WP-F3 reads as an open gap placed `local` with the artwork as its drawing and queues for
the next survey.

### 11.5 WP-F4, Design Claims Checked

WP-F4 consumes: `catalogue.kinds` and `device_kinds` (the catalogue the design's gap claim is checked against; the well's
false claim fails because `tank` is a catalogue kind); `catalogue.element_kinds[kind].draws` (a row mapping an entry with a
box to an element whose declared drawing is empty is refused before any page is built: the recorded `section` rows for fuses);
the rule that a device entry maps to a catalogue kind, a module-only kind, an assembly or `artwork`, never to `section` or
`label`; and the rule that a device of type `breaker` or `ats` mapped to `switch` is a kind claim the design must state as a
gap row until WP-F5's `breaker` exists.

## 12. Invariants

1. The manifest equals a fresh generation at its commit (C02); nothing reads a library fact from any other file of the
   library except through a path the manifest names.
2. Every descriptor element kind (the schema's top-level arrays of drawn elements, `alarmPanels` and `rows` among them)
   appears exactly once in `catalogue.element_kinds`, in `page_checks.KINDS` and in the generator's node builders; the
   table `ELEMENT_DRAWS` of `library_manifest.py` (Table 6.1's last column) is the source, and T-L1-05, C07 and C08 compare
   the others with it.
3. Every kind of `catalogue.kinds`, `module_kinds` and `module_only_kinds` has exactly one drawing (a view or a component),
   and the placement places it by that drawing (C04, C05, section 4.5).
4. A coverage row is carried only by elements whose declared drawing is non-empty for their parameters, or by a gap the row
   is listed in (`V1`, `V4`).
5. Every caller of `page_checks.py` passes the design's rows, keyed by `_v3.understanding_entries`' rule (section 6.6).
6. An artwork element's shapes equal the facts file's shapes for its source, in number, form and points (section 7.6 item 3).
7. Artwork, sections and wells take no colour, class or style from a descriptor (section 7.4).
8. A device's folder is `<tagRoot>/<id>`, `id` being `<hierarchy>/<leaf>`, or `<leaf>` where no area is ratified; every
   segment matches the safe pattern; a UDT instance carries exactly the members
   its definition names, and no member without a source exists (section 9).
9. Definitions sit one folder below `_types_`, under `<parent>` or `<child>`, by the names of Table 9.1; no other folder holds a
   `UdtType` (GF-51).
10. The thresholds of Table 6.3 are read from the manifest; no copy exists in the manager.
11. No command line in a tracked workflow names a host path; every library command is `commands.<name>` of the manifest
    joined to the engagement's worktree and the host's interpreter for its class.
12. Every path the manifest names is relative, normalised and inside the library root (C12).

## 13. Tests

Each test names the NOTE-WFB-14 finding it proves closed; a test on the recorded run replays its files offline and never
needs a gateway. Fixtures that derive from run files are made by package F0-W (Table 10.1): a manager-side script,
`src/tests/fixtures/g1_fixtures.py`, owned by the orchestrating session, reads the recorded run under `workspace/runs/` on
this host and writes synthetic fixtures of the shape each test names (descriptors, inventory objects, coverage rows, device
models), every text replaced by a generated label (`Item 1`, `Page 1`, `T001`) and every tag path by a generated one, the
geometry kept. Test T-F0-01 scans every fixture for the client terms of every engagement's profile and for the run's page
titles and tag stems, and fails on any match. Only these fixtures reach the cloud repository; no run file leaves this host
(`CLAUDE.md` non-negotiable 4).

| Id | Test | Closes |
|---|---|---|
| T-F0-01 | Every fixture of F0-W is free of every engagement's client terms and of the recorded run's page titles and tag stems | `CLAUDE.md` non-negotiable 4 |
| T-L1-01 | `library/manifest.json` equals `library_manifest.build()` at HEAD (C02) | WFB-324, RC9 |
| T-L1-02 | Every table of section 4.5 derived from `components.json` equals today's literal (`MODULE_KIND`, `MODULE_ONLY`, `FRAME_ONLY`, the 15 differing part names) | REPORT-T3 item 2 |
| T-L1-03 | `Rules.library_of("resistor")` places `module` with `cadre.ob.resistor`; `library_of("tooltip")` places nothing; `library_of("pump")` unchanged | MAP-PROPOSAL 6.1, Table 3.2 row 1 (seven items) |
| T-L1-04 | The manifest validates against its schema; a manifest of major 2 is refused by the reader | Section 4.6 |
| T-L1-05 | `catalogue.element_kinds` keys equal the schema's top-level element arrays two-way | WFB-334 |
| T-L1-06 | The manifest's `visibility` equals Table 6.3 | Invariant 10 |
| T-L1-06b | From `library/tokens/openbridge-tokens.json`, for each palette (day, dusk, night, bright): the section border, the heading band's rule, the well's vessel, the artwork stroke and the pipe paints reach `stroke_ratio` against their surface, and the label text reaches `text_ratio` | Table 3.2 rows 2 and 3, WFB-316 |
| T-L1-13 | C17 fails a type that needs an undeclared shape and a `measured` entry with no fact; C18 fails a state-changing write path not `confirmed` | `HMI-UDT-05`, `HMI-DSP-18` |
| T-L1-07 to T-L1-12 | The conformance tool: the current line passes (section 5.6 item 1); each mutant fails on its check alone (item 2); C10 with an 0.8.0 list passes and with 0.7.0 fails; exit codes 0, 2, 1; the report validates; `--strict` on a dirty tree fails | WFB-324, section 4.7 item 5 of NOTE-WFB-14 |
| T-F1-01 | The recorded well page descriptor (`p1-r2`) with today's renderer: `V1` on its `well` (declared `fill` under the alpha floor) | Table 3.1 the tank, WFB-316 |
| T-F1-02 | The recorded electrical overview descriptor: `V1` on every `section` without `border` or `title` that carries a device row | Table 3.1 the fuses, Table 3.2 rows 1 and 2 |
| T-F1-03 | A label-only row passes; a `section` with `border: true` passes; the same section without it fails | Section 6.8 item 2 |
| T-F1-04 | `visibility.js` on the fixture page in a headless browser: the section's fill ratio is 1.06 and `visible` false; the bordered section `visible` true; the pipe strokes pass `stroke_ratio` | Section 6.8 items 2 and 4 |
| T-F1-05 | The join by order: on the component test page the count, order and root class of the `Diagram` children equal the view JSON's children one for one | Section 6.8 item 8 |
| T-F1-06 | On the F0-W fixture of the recorded run the evidence block's rows equal block 24's: 191 of 191 keys agree, the 34 static rows among them | Section 3.3 item 5, WFB-316 |
| T-F1-07 | A row drawn only by a gap box and in no gap is `V4`; the same row in `gaps.json` passes | The gap path of `check_coverage`, kept |
| T-F1-08 | Place and size: an element whose centre leaves the grown source box is `V2`; a panel at a quarter area is `V3`; a symbol of any size passes `V3` | Section 6.3 |
| T-F1-09 | `page_checks.py --visibility` with a rendered file gives the rendered verdicts precedence over the declared | Section 6.2 |
| T-F2-01 | A descriptor with `artwork[]` of every form validates and builds with G0 to G7 passing; a shape outside its box fails G0 | Section 7.2 |
| T-F2-02 | `artwork_node` is deterministic and carries only the neutral paints; a descriptor key `color` on a shape fails G0 | Section 7.4, invariant 7 |
| T-F2-03 | A `section` with `border: true` renders a 1 px border class; with `title` a heading band whose box `title_band` returns | Table 3.2 rows 2 and 3 |
| T-F2-04 | `well_node` emits the vessel path first; the band and liquid unchanged | Table 3.1 the tank, Table 3.2 row 3 |
| T-F2-05 | `check_coverage` counts an `artwork` element; `library_gaps` never resolves `artwork` as a kind | Section 7.2 |
| T-F2-06 | The recorded inventory objects of the two fuse entries made shapes by section 7.6 item 3 give two artwork elements of one rectangle and one text each at the boxes scaled by section 7.6 item 3 | WFB-314, WFB-329 |
| T-S2-01 | `library/udt-types.json` holds the eight types of Table 9.1 with the members C15 states | WFB-325, RC8 |
| T-S2-02 | `udt_types.py --derive` on the F0-W fixture of the recorded device model gives one variant per distinct member set, named by hash, `<Type>` for a full set, and `udt` null with its `udt_reason` for a set that needs an unmeasured shape | Section 9.3 |
| T-S2-03 | The instances document places every device at `<tagRoot>/<id>` with `id` beginning with its `hierarchy`, and nothing at the root except where the person ratified no area | `HMI-TAG-01`, `CK-TAG-01` |
| T-S2-04 | A device `id` with a character outside the safe pattern fails `CK-TAG-02` | `HMI-TAG-02` |
| T-S2-05 | Gate G7 devices with `--types-file` expands an instance and finds a member the model lists but the type lacks | WFB-330, `CK-UDT-01` |
| T-S2-06 | `CK-HIS-01`: a trend member whose expanded tag lacks `historyEnabled` is a finding, and so is a historised member absent from the device's `trend` list (`HMI-HIS-05`) | Page 17 section 11 item 5 |
| T-S2-07 | The nine measurements of section 9.2 each have a recorded fact and a test that reads the measured export | Page 17 section 11 item 2 |
| T-S2-08 | The faceplate sweep G11 on a UDT-based test build shows no quality line (run once on the cloud gateway, recorded) | Section 9.7 |
| T-S2-09 | `udt_types.py --derive` refuses a device model entry whose `udt.typeId` names a type outside `udt-types.json` and its variants | `HMI-UDT-03` |
| T-F5 | Written from each part's own design note (section 8), with the rendered measure on the glass (T-F1-04's harness), never the part's own declared `draws` alone | WFB-314, Table 3.2 rows 1, 3 and 4 |
| T-L1W-01 to T-L1W-04 | The block runs the tool on the pinned worktree, adds C10 from the gateway list, fails the pre-flight on exit 2, refuses a manifest major it does not know, and detects a drifted schema copy (WFB-333) | WFB-324 |
| T-F1W-01 to T-F1W-05 | The evidence block passes the design's rows (the recorded run's inputs give 191 of 191 for coverage and the Table 6.4 visibility findings); a page item fails the run and a library item does not; `offline:visibility` is a page item; block 24's check turns `V` findings into defects; the final review lists library and tool items | WFB-316, R4 |
| T-F2W-01 to T-F2W-04 | `facts/artwork/<unit>.json` from the recorded inventories for the design rows that would name `artwork`; a descriptor shape that differs from the facts is a defect; the brief names `artwork` in its stand-in rule; a `section` row for a device entry is refused by block 18 | WFB-314, WFB-313 |
| T-S2W-01 to T-S2W-04 | The import block imports the types document before the instances and asks the approval once; the ASM model carries `hierarchy` and `udt`; ctig's bridge output validates against `cadre-hmi-devices/1` with the two keys; the device folder invariant holds on the recorded model | WFB-325 |

## 14. Owner Rulings

Each ruling has a default; the work proceeds on the default unless the owner says otherwise.

| Ruling | Question | Default |
|---|---|---|
| LR1 | The manifest's `standard.implements[]` names every rule STD-WFB-01 marks `carried_by` `library` or `both`, and C14 compares the two on the manager side | Yes |
| LR2 | The map proposal (MAP-PROPOSAL sections 3 and 4): the conformance check warns on the contradiction and does not fail until the owner rules on the proposal | Yes; the proposal's recommendation (a) is taken by section 4.5 |
| LR3 | The contrast thresholds of Table 6.3, 3:1 for strokes and fills (WCAG 2.1 criterion 1.4.11) and 4.5:1 for text (criterion 1.4.3), proven on every palette from the tokens (T-L1-06b) and changed only with a recorded measurement | Yes |
| LR4 | The place tolerance 0.25 of the scaled source box with a 48 px cap, and the size floor and ceiling 0.5 and 2.0 | Yes, confirmed by the corpus |
| LR5 | The artwork style: neutral stroke and fill only, the original's colours not carried | Yes |
| LR6 | The eight device types of Table 9.1 under `_types_/<parent>/<Type>`, engagement variants under `_types_/<child>/<Type>_<set>`, written only by the import block with approval, in place of ruling R8's "in the parent project"; the interlock types excluded until page 17's interlock contract is final | Yes |
| LR7 | One `String` parameter per member (`Src_<member>`), with the per-instance override as the fall-back if measurement fails | Yes |
| LR8 | Variants named by an eight-character hash of the member names and types unless the person names one on the design review card | Yes |
| LR9 | The device model's `id` holds `<hierarchy>/<leaf>`, with `hierarchy` its checked prefix holding the path classification ratified (NOTE-WFB-16 CR8), from which the design takes each device's node | Yes |
| LR10 | Tags of no device in the folders `Values` and `Unsourced` of their node, as STD-WFB-01 HMI-TAG-04 and HMI-TAG-05 state (its ruling SR4) | Yes |
| LR11 | The UPS, power monitor and duty selector panels stay artwork with placed readouts and lamps; no `ups` kind until a second project needs it | Yes |
| LR12 | The measurement plan of section 9.2 runs on the cloud gateway in G3 before S2-L is merged; the owner's gateway is written only through the import block's approval card | Yes |

## 15. Register Items

Table 15.1 lists the items this document found; each is recorded in `REGISTER.md` with revision 0.1.

| Id | Item | Package |
|---|---|---|
| WFB-329 | An understanding's static entry carries no box; the geometry of a static object or an unclassed device is recoverable only from the inventory objects its `ans` names, which no stage after the understanding reads | WP-F2 (section 7.6) |
| WFB-330 | Gate G7 devices with `--tags-file` does not read UDT instances (library page 17 section 10 item 12), so a UDT-based target is unchecked; recorded here, fixed in the library | WP-S2 (section 9.7) |
| WFB-331 | The element map's `generator` row and the rejected `obc-indicator-generator` entry contradict the 0.8.0 module (MAP-PROPOSAL 6.3); the conformance check warns until the owner rules on the proposal | WP-L1 (LR2) |
| WFB-332 | Ruling R8 places UDT definitions "in the parent project"; tags live in a provider, so the definitions sit under `_types_/<parent>` of the provider (conflict reported, section 9.1) | WP-S2 (LR6) |
| WFB-333 | The manager keeps eleven schemas, eight of them copies of library schemas, under `src/wfb_blocks/openbridge/schemas/` with no check that they equal the library's | WP-L1 (C07's digests, the conformance block) |
| WFB-334 | The descriptor element kinds are kept in three hand-written lists in two repositories (`COMPONENT_KINDS`, `page_checks.KINDS`, `library_gaps.BUILTIN`) | WP-L1 (the manifest's `element_kinds`) |

## 16. Risks

1. **The join by index of the rendered measure fails on a frame that reorders the canvas's children** (section 6.2 item 2).
   Mitigation: the corpus test T-F1-05; the declared rule stands alone until fixed; a fix names each node by a `data-` attribute
   the generator can set, if Perspective carries it through.
2. **The UDT shapes fail measurement** (section 9.2). Mitigation: the fall-backs named per item; an expanded folder stays the
   last resort and is today's build.
3. **Variant explosion on a project with irregular member sets.** The pilot's eighteen devices give few; a project with
   hundreds of devices may give dozens of variants. Mitigation: the person names and merges variants on the design review
   card (LR8); the count is reported by `udt_types.py --derive`.
4. **The contrast thresholds reject an honest library drawing on one palette.** Mitigation: T-L1-06b computes every element
   kind's paint pairs from the token file for all four palettes before any page is measured, so a palette whose token misses
   3:1 is a library item found before a run; the rendered corpus runs on the day palette.
5. **The manifest's size and the number of commands grow with every tool.** Mitigation: section 4.6's versioning; a reader
   ignores fields it does not need.
6. **Two parents' definitions on one gateway double the types.** Deleting a project leaves its `_types_` folder in the provider
   (GF-118 concerns projects only). Mitigation: LR6 keeps each parent's types in its own folder; removing an old parent's types
   is a tag write of its own, made through the import block with the owner's approval.
7. **The artwork element invites a builder to redraw everything as artwork.** Mitigation: the design check refuses `artwork`
   for an entry whose kind the catalogue or the module draws (section 11.5), and WP-F3 queues every artwork device as a gap.

## 17. What the Design Leaves Out

1. Moving the generator's parameter rules (`MODULE_EXCEPT` and the rest) into `components.json` (REPORT-T3's second step).
2. The rendered corpus on the night, dusk and bright palettes: their paints are computed from the tokens (T-L1-06b), and the
   glass measures the day palette only.
3. OPC members in a UDT (`valueSource` `opc`), which page 17 marks unmeasured and no engagement needs.
4. A `ups`, `power-meter` or `duty-selector` kind (LR11).
5. A library-side classifier of inventory objects; the manager prepares the shapes (section 7.7 item 3).
6. The migration page's library switch, the library list and the pinned worktree (WP-L2), the gap flow (WP-F3) and the design
   check (WP-F4), beyond the interfaces of section 11.
7. Any change to ctig beyond the interface of section 9.6; ctig's package is written in ctig under its own rules.
8. The reading of a UDT by the faceplates (none is needed) and any change to the alarm model (alarms stay on source tags).

## 18. References

1. NOTE-WFB-14, Gaps Found by the Recorded One-Page Migration and the Plan to Close Them, revision 0.3, 2026-11-07.
2. NOTE-WFB-10, the standard migration workflow (`cloud/import/NOTE-WFB-10-standard-migration-workflow.md`), sections 7.5,
   9.2 and 11.2.
3. The library wiki, Cadre-Sandbox-OpenBridge main `506076c`: page 05 (component catalogue), 06 (parent project and library,
   sections 5 and 6), 08 (generation and validation, sections 3 to 7), 14 (library configuration, sections 4 and 5), 16
   (component selection, sections 2, 6, 7 and 8), 17 (tag model and UDTs, sections 2, 3, 8, 9, 10 and 11), 18 (view builder
   reference, sections 2, 9 and 10).
4. `cloud/import/MAP-PROPOSAL.md` (sections 2, 5 and 6) and `cloud/REPORT-T3.md` section 10, cadre-ob-cloud main `dd1958d`.
5. `CONFIGURATION.md` sections 3.1, 3.2 and 4.8 of the library.
6. Library decisions COBD-035 (2026-10-10, the owner's authorisation of `_types_` measurement), COBD-038 (a page shows nothing
   the source does not state), COBD-053 (2026-11-07, the Sandbox follows the cloud line).
7. WorkflowBuilder decisions WFBD-005 (reuse by invocation), WFBD-012 (permissive dependencies), WFBD-134 (the design method),
   WFBD-146 (NOTE-WFB-14 approved; the parent `cadre_hmi_base_asm_080`).
8. ARCH-WFB-01 sections 6.3 (`tool_repositories`), 27.4 and 29.6 (the tool blocks and command interfaces).
9. The HMI standard, `standards/hmi/`, version 0.2: rules `HMI-VIS-01`, `HMI-VIS-02`, `HMI-TAG-01`,
   `HMI-TAG-02`, `HMI-UDT-01`, `HMI-HIS-01`.
10. W3C Web Content Accessibility Guidelines 2.1, the relative luminance and contrast ratio definitions (section 6.3).
11. The recorded run's files, local only: `workspace/runs/20261105T164103Z-61af` (the design, the ASM model, the inventories,
    the understandings) and `workspace/runs/20261105T164137Z-229d` (the descriptors, the coverage map, the evidence pack).
