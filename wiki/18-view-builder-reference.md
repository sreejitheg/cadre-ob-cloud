---
title: View builder reference
type: wiki
updated: 2026-11-06
---
# 18 View Builder Reference

| Field | Value |
|---|---|
| Document ID | COB-WIKI-18 |
| Revision | B |
| Status | Issued for use |
| Built | Cloud session of 2026-11-05, branch `claude/keen-cori-cibeff` over `main` at `d9f8655`; revision B of 2026-11-06 (tranche T3, branch `port/sandbox-0.8.0`, merge `11005e3`) adds the local assemblies, the option `--local-kinds` and the two gate rules of section 12 |
| Code | `tools/hmi/screen.py` (generator, command line), `tools/hmi/gates.py` (G0 to G7), `tools/hmi/parts.py`, `tools/hmi/diagram.py`, `tools/hmi/navigation.py`, `tools/hmi/library.py`, `tools/hmi/assembly.py`, `tools/hmi/testbench.py`, `schemas/screen-descriptor.schema.json`, `schemas/devices.schema.json`, `library/contracts.json`, `library/profile.json`, `module/components.json` |
| Companions | Page 08 (the pipeline, the device model and the gates in prose), page 06 (the parent project, the library contract, the faceplate contract), page 05 (the component catalogue and the page parts), page 04 (the frames), page 12 (the module), page 16 (component selection), page 17 (the tag model: the members of each device kind), `module/CATALOGUE.md` (every module component), `CONFIGURATION.md` (commands) |

## 1. Purpose

This page is the key by key reference for a tool that writes the JSON files `tools/hmi/screen.py` turns into a
Perspective child project over the parent `cadre_hmi_base`: the screen descriptors (`cadre-hmi-screen/1`) and the device
model (`cadre-hmi-devices/1`). A tool such as ctig, converting a Citect project, can write a descriptor from this page
without reading the Python, and have it pass gates G0 to G7 the first time. The module is 0.8.0, with 97 components
(`module/components.json`).

Page 08 explains the pipeline, the device model and the gates in prose; this page does not repeat that. It adds what page 08
lacks: every key with its type, whether it is required, its constraint and its meaning; the parameters each kind accepts;
the arithmetic that places symbols; the rules the generator checks beyond the schema; and a checklist by gate. Member
tables of the device kinds are on page 17 and are not repeated here.

Every fact below traces to a source named beside it: the schemas, `library/contracts.json` (generated), `library/profile.json`
(generated), `module/components.json` (generated) or the code of `tools/hmi/`. The key tables are generated from the
schemas and the contracts, so names, types, required flags, enumerations, patterns, minimums and defaults are exact; the
meaning column is written from the schema descriptions and the code. A rule found in the code that the schema does not state
is marked as such (section 3.3).

Conventions. A member is a tag path relative to the descriptor's `tagRoot`. A box is `x`, `y`, `w`, `h` in px of the page,
origin at its top left. A relative member never starts with `[`; an absolute one is `[provider]path`.

## 2. Inputs, Outputs and the Command Line

### 2.1 Inputs and Outputs

Table 1. What a builder gives the generator and what it receives.

| Item | Form | Notes |
|---|---|---|
| Screen descriptors | One JSON file per page, repeatable `--descriptor` | The files of one build share one provider and one top tag folder (a build that writes tags refuses two, section 2.3) |
| Device model | One JSON file, `--devices-file` | Optional. Without it a device symbol keeps the faceplates' default members (page 08 section 3.1) |
| External tag model | One folder document, `--tags-file`, with `tagModel` `external` in the descriptors | Optional. The gates read it (G7 devices, interlocks, libraries); `--deploy` imports it before the project |
| Local kinds list | One JSON file, `--local-kinds`: a list of kind names | Required by any descriptor with `assemblies` (section 10.8); the kinds a page may draw as a local assembly |
| The parent | The folder `<out>/cadre_hmi_base`, written by `python tools/hmi/parent.py --out <out>` | Required beside the child: gate G4 reads its `project.json`, and a missing parent stops the run with a `FileNotFoundError`, not a message |
| The child project | `<out>/<project>`, the files of a Perspective project | The generator is deterministic: the same inputs give the same bytes |
| The report | The file named by `--report` | Section 2.4 |

The project name must start with `cadre_hmi` to be deployed (`deploy.py` refuses any other); an offline build does not check it.

### 2.2 The Command Line

`python tools/hmi/screen.py --project <name> --descriptor <file> [--descriptor <file> ...] [options]`. Every option, from the
argument parser of `main()` in `tools/hmi/screen.py`:

Table 2. The options of `screen.py`.

| Option | Default | Effect |
|---|---|---|
| `--project` | required | The child project's name. It must start with `cadre_hmi` for `--deploy` |
| `--descriptor` | none | A screen descriptor; repeat for each page. Required unless `--component-test` is given with `--tag-root` |
| `--app-name` | `App` | The project's title is `Cadre HMI <app-name>`; it is also the application name of the page configuration |
| `--out` | `build` under the repository | The folder the child is written into (as `<out>/<project>`), and the folder the parent is read from |
| `--report` | none | A JSON file with each route's result and the gates (section 2.4) |
| `--deploy` | off | After the gates pass: ensure the trial, import the external tag model if given, import the generated test tags, import the project. Needs a gateway; never part of an offline proof |
| `--alarm-scope` | `*` | The source pattern of the alarms the frame shows, for example `*cadre_hmi_wtp*`; written to `session.custom.alarmScope`. G7 devices warns of an alarm source outside it |
| `--tags-file` | none | An external tag model (folder JSON). The gates read it, and `--deploy` imports it |
| `--devices-file` | none | A device model; validated by G0 and checked by G7 devices |
| `--render` | `stock` | `stock` draws every kind with the library views; `module` draws the kinds of section 11 with the module's components and accepts module-only kinds. The descriptor does not change |
| `--faceplate` | `openbridge` | The project's default faceplate style: `openbridge` or `asm`. A device of the model may set its own with `faceplate` |
| `--faceplate-mode` | `dock` | Where a session opens a faceplate until its pin moves it: `dock` (the right dock) or `popup` |
| `--frame` | `openbridge` | The application frame: `openbridge` (the default), `asm`, `ob` or `obasm`. `ob` and `obasm` need `--render module`. `asm` and `obasm` carry the ASM rules and check `previous` and `next` (section 4.3) |
| `--parent` | `cadre_hmi_base` | The parent project the child inherits; it must exist in `--out` |
| `--component-test` | off | Adds the component test page generated from the library catalogue (page 13 section 13). Not needed to build a plant's pages |
| `--tag-root` | none | With `--component-test`: the folder `[provider]folder` of the test devices; with it and no `--descriptor`, the page is built alone |
| `--write-descriptor` | none | With `--component-test`: write the test page's descriptor to `DIR/component-test.json` |
| `--local-kinds` | none | `FILE`: a JSON list of kind names (strings) a page may draw as a local assembly (section 10.8). Gate G0 refuses an assembly of any other kind and every assembly when the option is absent (Table 56i). The component test page's own kind `benchlocal` (`testbench.LOCAL_KIND`) is allowed whatever the file holds |
| `--write-devices` | none | With `--component-test`: write the build's device model to `FILE` |

The exit code is 0 when the gates pass (warnings do not fail) and 1 on any refusal.

### 2.3 What Is Refused

Table 3. The refusals of the command line and the build, in the order they happen.

| Refusal | Message or effect |
|---|---|
| No `--descriptor` | `--descriptor is required, unless --component-test is given with --tag-root`; exit 1 |
| `--tag-root`, `--write-descriptor` or `--write-devices` without `--component-test` | A message; exit 1 |
| `--frame ob` or `obasm` without `--render module` | `--frame <name> draws the module frame components of the module: it needs --render module`; exit 1 |
| `--component-test` with descriptors of several tag roots | A message; exit 1 |
| `--local-kinds` names a file that cannot be read or parsed, or that is not a JSON list of strings | `--local-kinds <file>: <the error>` or `--local-kinds <file>: a JSON list of kind names`; exit 1 before any descriptor is read |
| G0: a descriptor or the device model fails its schema | `G0_descriptor_schema FAIL` or `G0_devices_schema FAIL` and the first 20 errors as `file: path: message`; exit 1 before anything is built |
| G0: an assembly breaks a rule of Table 56i | `G0_descriptor_schema FAIL`, then the first 20 rule errors as `  <rule>: <page>: <assembly>: <message>`, listed in the order of Table 56i; exit 1 before anything is built. Schema errors, where there are any, print first, and the rules are checked as well |
| `--frame asm` or `obasm` with a `previous` or `next` that is no route of the set | A `ValueError` from `build_child` (a traceback), naming the route and the key |
| A contract error in a page (section 12, G7 contract) | `CONTRACT ERRORS: not deploying`; exit 1, before gates G1 to G7 run |
| A gate fails | `GATES FAIL: not deploying`; exit 1 |
| `--deploy` with descriptors that do not share one provider and one top tag folder | A `ValueError` from the test tag document (`descriptors of one build must share one top tag folder and provider`) |
| No parent in `--out` | A `FileNotFoundError` from G4 after the child is written |

### 2.4 The Report File

`--report` writes one JSON object. Each key that starts with `/` is a route and holds that page's result, and the key
`gates` holds the gates (page 08 section 5). A route's entry has `errors` (strings; any one stops the build), `gaps` (a list
of `{id, kind, reason}` for each symbol drawn as a gap box), `notes` (what the page shows that its descriptor does not state),
`flow` (`gates`, `pipes`, `vectors`, `mode`, `mismatches`, `ok`), and for a diagram `diagram` (graph size) and `expressions`
(the compiled flow expression of each pipe). `gates.<gate>.warnings` is a list on every gate, empty where the gate has none.
A builder that must prove a clean build reads `errors`, `gaps` and `gates` from this file:

```python
report = json.load(open("report.json"))
clean = not any(g["warnings"] for g in report["gates"].values() if isinstance(g, dict)) \
    and not any(v["gaps"] for r, v in report.items() if r.startswith("/"))
```

A gap is not a failure: a symbol of an unknown kind passes every gate as a dashed box, so a builder checks `gaps`.

A build that fails gate G0 writes the report before `screen.py` exits, and the file then holds the key `gates` alone (no route is built):

```json
{"gates": {"G0": {"ok": false, "errors": [{"rule": "assembly-without-local-kinds", "page": "cooling.json",
                                               "assembly": "CH1", "message": "an assembly needs screen.py --local-kinds"}],
                  "warnings": []},
           "ok": false}}
```

`gates.G0.errors[]` holds every error, not the first 20 that the console prints. The rule of an entry is `schema` (a descriptor fails its
schema; `message` is the line `file: path: message`), `devices-schema` (the device model fails its schema) or one of the assembly rules of Table 56i,
in which case `page` is the descriptor file as given on the command line, `assembly` is the assembly's `id` and `message` says what is wrong. A report of a
build that passes G0 has no `G0` entry. A builder reads the rule, not the message text.

### 2.5 The Device Model Keys

The device model is validated by G0 against `schemas/devices.schema.json` and checked by G7 devices. Only its keys are listed
here; the members each kind knows, their types and the write paths are on page 17.

Table 4. The top-level keys of a device model (`schemas/devices.schema.json`).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `schema` | string | yes | value `cadre-hmi-devices/1` | Value `cadre-hmi-devices/1`. |
| `tagRoot` | string | yes | pattern `^\[[^\]]+\][^/].*[^/]$` | The folder, with provider, that the device folders sit under; it equals the descriptors' `tagRoot`. |
| `devices` | array of device object | yes |  | The devices. |

Table 5. The keys of a device of the device model.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*$` | The device's tag folder under the model's `tagRoot`: the string a symbol's `device` resolves to. |
| `kind` | string | yes |  | A device kind of the profile (`deviceKinds`). It selects the faceplate. |
| `title` | string | no |  | The identifier shown in the faceplate header. |
| `label` | string | no |  | The description beneath the identifier. |
| `unit` | string | no |  | The engineering unit of the device's value. |
| `members` | object | yes |  | Every member the folder carries that its faceplate reads (member keys: Table 6). Page 17 lists the members of each kind. |
| `alarmSources` | array of string | no |  | Source patterns of the device's alarms where they stay outside the folder. Absent, the alarms are those under the folder; empty, the device has none. |
| `trend` | array of string | no |  | The members the tag model historises; each gets a trend card. |
| `faceplate` | string | no | values `openbridge`, `asm` | The device's faceplate style: `openbridge` or `asm`. Absent, the project's `--faceplate`. |
| `modes` | array of object | no | at least items 1 | Ownership by mode: each value of the member `mode` with a name and an owner. |
| `node` | string | no |  | For a device no page draws with `device`: its node of the plant hierarchy. |

Table 6. The keys of a member of a device (page 17 gives the members each kind knows).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `type` | string | yes | values `Boolean`, `Int1`, `Int2`, `Int4`, `Int8`, `Float4`, `Float8`, `String` | The tag's data type. |
| `access` | string | yes | values `read`, `write` | `write`: a session with the member's write path may write it; `read`: nothing writes it. |
| `pulse` | boolean | no |  | A pulse command: Boolean, `write`, and a pulse member of the device's kind. |
| `caption` | string | no | pattern `^[^\s\x00-\x1f\x7f]([^\x00-\x1f\x7f]*[^\s\x00-\x1f\x7f])?$`; at most chars 32; at least chars 1 | The pulse button's text, one line of 1 to 32 characters. |
| `config` | object | no |  | A configuration row: a numeric member under `cfg/` with `caption`, `unit`, `minimum`, `maximum` and `format`. |

A `modes` entry is `{value: integer, name: 1 to 24 characters, owner: program, operator, maintenance or local}`. The device
model's `tagRoot` must equal the `tagRoot` of the descriptors that draw its devices.

### 2.6 What `--deploy` Imports

With `--deploy`, and only after every gate and the contract have passed, `screen.py` imports in this order (`screen.main`):

1. `deploy.ensure_trial()`, which resets an expired trial (GF-03, GF-33).
2. The tag model of `--tags-file`, where one is given, at the root of the provider `default`: `deploy.import_tags("default", "", document)`. The
   document is one folder object, whose top folder therefore sits at the root of `[default]`.
3. The generated tags of `tags_document` (section 5.4 and page 17 section 4), for every descriptor whose `tagModel` is not `external`, again at the
   root of `default`. Only the component test page's tags go to the provider and path of its own tag root.
4. The child project (`deploy.import_project`), and the identity provider `default` set on it (GF-44).

Every tag import posts with the collision policy `Overwrite` (`cloud/vendor/ctig/gateway/rest.py`, `tags_import`), which merges at folder level and
replaces at tag level (GF-55). Three consequences for a builder:

1. The provider named in `tagRoot` is not the provider the tags are imported to: a build whose `tagRoot` names another provider binds that provider
   while its tag model and generated tags land in `default`.
2. A build whose tags are generated (no `tagModel` `external`) deployed over a folder that already holds real tags replaces each tag of the same
   name with a memory tag.
3. A UDT set needs its `_types_` document imported on its own (page 17 section 3.1), since `--tags-file` carries one folder.

## 3. The Descriptor Top Level

### 3.1 The Keys

Table 7. The top-level keys of a descriptor (`schemas/screen-descriptor.schema.json`; the object allows no other key).

| Key | Type | Required | Constraint | Layout | Meaning |
|---|---|---|---|---|---|
| `schema` | string | yes | value `cadre-hmi-screen/1` | both | The descriptor version. Any other value fails G0. |
| `screen` | object | yes |  | both | The page's identity, route and place in navigation (section 4). |
| `tagRoot` | string | no |  | both | The tag folder, with its provider, that a relative binding member resolves under (section 5.4). State it whenever any binding is relative. |
| `tagValues` | object | no |  | both | The value a generated test tag starts with, by binding member. Read only when `tagModel` is `generated`. |
| `toolbar` | boolean | no | default `true` | diagram | Whether the diagram carries the operator toolbar: Color (only where a pipe names a medium), ID-tag, Readout and the zoom controls. A cards page has none. |
| `sections` | array of object | no |  | diagram | Background panels that group equipment, optionally opening a route when clicked (section 9.1). |
| `symbols` | array of symbol object | no |  | diagram | The equipment, instruments and blocks of a diagram (section 5). |
| `junctions` | array of object | no |  | diagram | Named points where pipes meet (section 9.2). |
| `pipes` | array of object | no |  | diagram | Connections between symbol sides, junctions and free ends; they carry the flow logic (section 9.2). |
| `rows` | array of arrays | no |  | cards | The rows of cards of a cards page (section 8). |
| `unmapped` | array of any | no |  | neither | An importer's record of source objects that have no library kind. No code in `tools/hmi` reads it; it is for the reader of the file. |
| `showTags` | boolean | no | default `false` | diagram | Whether identifier tags show when the page opens; the toolbar button still toggles them (section 9.5). |
| `tagModel` | string | no | values `generated`, `external`; default `generated` | both | `external` when the tags exist already (imported from a tag model file): the generator then writes no memory tags for the descriptor's bindings. |
| `labels` | array of object | no |  | diagram | Free text on a diagram, optionally emphasised while a Boolean holds (section 9.3). |
| `buttons` | array of object | no |  | diagram | Command buttons: a pulse with a question, a faceplate opener or a route (section 10.1). |
| `bars` | array of object | no |  | diagram | Range bars with their own box (section 10.2). |
| `trends` | array of object | no |  | diagram | Embedded trends of one or two pens (section 10.3). |
| `lines` | array of object | no |  | diagram | Free lines, dashed or gated by a tag or a symbol (section 10.4). |
| `links` | array of object | no |  | diagram | Icons that navigate to a route (section 10.5). |
| `brackets` | array of object | no |  | diagram | A thin bracket with a name beside a group of symbols (section 10.5). |
| `wells` | array of object | no |  | diagram | The liquid of a well with level switches (section 10.5). |
| `alarmPanels` | array of object | no |  | diagram | An alarm list with Ack selected and Ack all over the alarms under tag folders (section 10.6). |
| `assemblies` | array of assembly object | no |  | diagram | Local assemblies: part sets drawn for a device kind the library lacks, one view per kind, one embed per assembly (section 10.8). Needs `screen.py --local-kinds`. |

The object allows no other key (`additionalProperties` false). A descriptor needs `schema` and `screen`; the layout decides
the rest. A page part (`buttons`, `bars`, `trends`, `lines`, `links`, `brackets`, `wells`, `alarmPanels`, `assemblies`), a label `emphasis`,
a symbol `bar` or `alarm`, and the screen option `fit` belong to the diagram layout: on a cards page the generator reports
`page parts and fit are for a diagram layout` as a contract error (`parts.check`); for `assemblies` gate G0 refuses the page first, by the rule
`assembly-on-cards`.

### 3.2 Which Layout Uses What

A diagram places every box at a pixel position on a page of `screen.width` by `screen.height` and joins symbols with pipes.
A cards page lays out rows of cards by flex rules, so it needs no coordinates for its card bodies and has no pipes or sections.
Both lay out symbols from the same library views. Tags are bound the same way on both.

### 3.3 Rules the Code Reads That the Schema Does Not State

Table 8. Keys the schema leaves optional that the generator needs. Each is a build failure of the kind named, not a gate message.

| Key | When it is needed | What happens without it |
|---|---|---|
| `screen.width`, `screen.height` | Diagram layout | A `KeyError` in the generator (G0 passes) |
| `w`, `h` of every diagram symbol | Always on a diagram, including the 48 px automation symbols, whose size the generator then ignores | A `KeyError` in `screen.embed_limits` (G0 passes) |
| `bodyWidth` and `bodyHeight`, or `body` | Every card of a cards page, even one with no items | A `KeyError` in `item_positions_percent` for a card with neither |
| `tagRoot` | Any relative binding member | The path becomes `/<member>`, which no tag has |
| `x`, `y`, `w`, `h` of an item | Card `items` (they are in card body pixels) | The schema requires `x` and `y`; `w` and `h` are read |

## 4. The Screen Object

### 4.1 The Keys

Table 9. The keys of the `screen` object.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z][A-Za-z0-9_]*$` | A short name: a letter, then letters, digits and underscores. The generator does not read it; `tools/hmi/page_checks.py` keys the descriptors of a set by it. |
| `route` | string | yes | pattern `^/` | The page's route. It keys the page configuration, the navigation item, the report and the targets of `previous`, `next`, section and card routes. Routes of one build must be distinct: the generator does not check it, and a repeated route replaces the earlier page. |
| `title` | string | yes |  | The page title; it is the navigation label when `navLabel` is absent. |
| `view` | string | yes |  | The view path in the child project, for example `Screens/Overview`. View paths are case sensitive (GF-22). |
| `layout` | string | yes | values `diagram`, `cards` | `diagram` places boxes at pixel positions with pipes between them; `cards` lays out rows of cards (section 8). |
| `width` | number | no | minimum 1 | The page's width in px. Required in practice for a diagram (section 3.3); a cards page takes 1600 where it is absent. |
| `height` | number | no | minimum 1 | The page's height in px. Required in practice for a diagram; a cards page takes 852 where it is absent. |
| `icon` | string | no |  | The icon name, from `library/icons`, of the navigation item. Absent, the item has an empty icon. |
| `nav` | boolean | no | default `true` | Whether the page has a navigation item. |
| `navLabel` | string | no |  | The navigation item's label; the title where absent. |
| `node` | string | no | pattern `^[^/]+(/[^/]+)*$`; at most chars 120 | The node of the plant hierarchy the page shows, root first and `/` between names (section 4.2). |
| `fit` | boolean or object | no |  | Diagram only: scale the page down to its window, keeping the aspect ratio and never above 1. `true` takes the top dock (48 px) and the toolbar (56 px) off the viewport's height; an object states the pixels to reserve (section 7.6). |
| `level` | string | no | at most chars 40 | The level word the page header of the ASM frames shows beside the title, for example `Level 2 unit`. Read by `--frame asm` and `--frame obasm` only. |
| `previous` | string | no | pattern `^/` | The route of the page the header's previous button opens under the ASM frames; without it the button is disabled. |
| `next` | string | no | pattern `^/` | The route of the page the header's next button opens under the ASM frames; without it the button is disabled. |

`id`, `route`, `title`, `view` and `layout` are required by the schema. A route starts with `/` (pattern `^/`). The set
`/alerts` and, for a build with historised members, `/trends` are the library's own routes and should not be reused.

### 4.2 Node Paths and the Hierarchy

`node` names the node of the plant hierarchy the page shows, from the root and separated by `/`, for example `WTP/Filtration`
(pattern `^[^/]+(/[^/]+)*$`, at most 120 characters). The descriptors of a set make the hierarchy (`screen.hierarchy`): a node
exists for every named node and for every node above one, root first, each holding the pages that name it. A device belongs to
the node of the deepest page that draws it with `device` (a page that names no node places no device). A device that no page
draws with `device` takes the `node` of its entry in the device model, if it has one. A project whose descriptors name no node
has no hierarchy. The node also gives the alarm counts and the breadcrumb their data (page 04 section 7).

Rules for a builder: use the same spelling for the same node on every page; give a drill-down page a longer path than its
overview (`WTP` for the overview, `WTP/Intake` for the intake), so that a device drawn on both belongs to the intake; and
name the node on every page of a plant so that its devices have one.

### 4.3 Routes, Previous and Next, Navigation

The navigation item of a page is `{label: navLabel or title or route, path: route, icon, node}`; a page with `nav` false has
no item. A section's `route`, a card's `route`, a link's `route` and a button's route action are not checked against the set
of routes. `previous` and `next` are checked only under `--frame asm` and `--frame obasm`: each must be the route of another
descriptor in the same build (`navigation.frame_errors`); a build under any other frame ignores them. `level` is shown by the
same two frames only (page 04 section 8.8).

The library writes routes of its own beside those of the descriptors: `/alerts` (`Framework/AlertsPage`, every frame), `/trends`
(`Framework/TrendsPage`, when a device is historised), `/node/alarms` and `/node/trend` (`Framework/ASM/NodeAlarms`, `NodeTrend`, under `asm`
and `obasm`) and `/component-test` (with `--component-test`). A descriptor routed `/alerts` replaces the library's alerts page, and the footer's
Alerts item then opens it; under the ASM frames the library's node routes, written after the pages, replace a descriptor of the same route. Two
descriptors with the same `screen.view` leave one view, the later, under both routes. No gate refuses either case, so a builder keeps every route
and every view path of a set distinct and clear of the library's routes.

### 4.4 Icon Names

`screen.icon` and `links[].icon` name an icon of `library/icons` (93 icons, `library/icons/ICONS.txt`; page 03 section 5). A link whose icon has no
file there is a build error (`link <id>: no library icon`); `screen.icon` is not checked, and an unknown name draws an empty icon. Under the frames
`openbridge` and `asm` a navigation icon is drawn by `cadre.icons.elements(name)` from the 93. Under `ob` and `obasm` the item is
`cadre.ob.navigationitem`, whose `iconName` takes only the 34 icons the module bundles; an icon outside them is left out (`cadre.hmi.ob_items`).

Table 4a. The icon names.

| Set | Names |
|---|---|
| The library's 93 (`screen.icon`, `links[].icon`, navigation under `openbridge` and `asm`) | `alarm-acknowledged-outlined`, `alarm-badge`, `alert-list`, `alert-off-filled`, `alerts`, `arrow-down-google`, `arrow-left-google`, `arrow-right-google`, `arrow-up-google`, `auto`, `backward`, `backward-fast`, `backward-stopped`, `caution-badge`, `check-google`, `chevron-double-down-google`, `chevron-double-up-google`, `chevron-down-google`, `chevron-left-google`, `chevron-right-google`, `chevron-up-google`, `close-google`, `command-locked-f`, `damper-horizontal-off`, `damper-horizontal-on`, `dashboard`, `display-brilliance-low`, `duty`, `energy-battery`, `fan-off`, `fan-on`, `filter`, `filter-1-off`, `filter-1-on`, `forward`, `forward-fast`, `forward-stopped`, `generator`, `heatexhanger`, `heatpump`, `home`, `hydraulic-separator`, `local`, `local-only`, `manual`, `manual-only`, `media-play`, `media-stop`, `menu`, `more-google`, `more-vertical-google`, `motor-off-horizontal`, `motor-off-vertical`, `motor-on-horizontal`, `motor-on-vertical`, `motor-static-horizontal`, `motor-static-vertical`, `notification`, `notification-filled`, `off`, `on`, `palette-day`, `palette-day-bright`, `palette-dimming`, `palette-dusk`, `palette-night`, `placeholder`, `pump-off-horizontal`, `pump-off-vertical`, `pump-on-horizontal`, `pump-on-vertical`, `pump-static-horizontal`, `pump-static-vertical`, `search`, `sensor-water-drop-google`, `sensor-water-ph-google`, `speed`, `standby`, `support-google`, `switch-horizontal-off`, `switch-horizontal-on`, `tank`, `trend`, `trend-down`, `trend-up`, `twoway-analog-closed`, `twoway-digital-closed`, `twoway-digital-open`, `user`, `user-google`, `warning-badge`, `warning-rectified-outlined`, `warning-unacknowledged-outlined` |
| The module navigation item's 34 (navigation under `ob` and `obasm`) | `menu`, `user`, `user-settings`, `notification`, `notification-filled`, `applications`, `alerts`, `alarm`, `alert-list`, `info`, `help`, `home`, `search`, `dashboard`, `palette-day`, `palette-dusk`, `palette-night`, `palette-day-bright`, `palette-dimming`, `time`, `silence-iec`, `settings-default-iec`, `chevron-left-google`, `chevron-right-google`, `close-google`, `check-google`, `placeholder`, `command-in`, `command-no`, `command-take`, `command-request`, `command-shared`, `command-locked`, `joystick` |
| The 19 that draw in all four frames | `alert-list`, `alerts`, `check-google`, `chevron-left-google`, `chevron-right-google`, `close-google`, `dashboard`, `home`, `menu`, `notification`, `notification-filled`, `palette-day`, `palette-day-bright`, `palette-dimming`, `palette-dusk`, `palette-night`, `placeholder`, `search`, `user` |

A page meant for any frame takes its `icon` from the last row. The generated Trends item uses `trend`, which draws no icon under `ob` and `obasm`.

## 5. Diagram Symbols

### 5.1 The Keys

Table 10. The keys of a diagram symbol (`$defs/symbol`; no other key is allowed).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The symbol's name, unique on the page. It names the embedded view, the gate variable `custom.g_<id>`, the device folder when `device` is `true`, and the targets of pipes, `gate` and `emphasis`. |
| `kind` | string | yes |  | The library kind (Table 11) or a module-only kind (section 11.4). Matched without regard to case. Any other value is drawn as a dashed, labelled gap box and counted in the report; it is not an error. |
| `x` | number | yes |  | The left edge for a box kind; for an automation symbol the left edge of its 48 px symbol box (section 5.2). |
| `y` | number | yes |  | The top edge, read like `x`. |
| `w` | number | no | minimum 1 | The width of the box. Not read for the 48 px symbol itself, but required in practice on every diagram symbol (section 3.3). |
| `h` | number | no | minimum 1 | The height of the box; read like `w`. |
| `params` | object | no |  | Static parameters of the kind's view. A name outside the view's contract is a G7 error (section 6). The values are not checked against enumerations. |
| `bind` | object | no |  | Parameter name to tag member. A relative member resolves under `tagRoot`; one that starts with `[` is an absolute path (section 5.4). |
| `device` | boolean or string | no |  | `true` marks the symbol as a device whose tag folder is its id; a string names the folder (relative to `tagRoot`) for a second symbol of a device drawn elsewhere. A device symbol opens the faceplate dock (section 5.5). |
| `label` | string | no |  | The device description shown in the faceplate header; it becomes the view parameter `deviceLabel`. |
| `bar` | object | no |  | A readout or an instrument field only: a range bar beside the symbol (section 10.2). |
| `alarm` | string | no |  | An indicator only: the tag whose alarms the lamp follows (a fault row, section 5.7). |
| `states` | array of object | no |  | An indicator only: the colours its state takes (section 5.7). |
| `stateDefault` | string | no |  | An indicator with `states`: the colour of a value no entry names (a palette name or a CSS paint; default `off`). |
| `faceplate` | string | no |  | A symbol that is not itself a device but opens the faceplate of a device of the device model, by its id under `tagRoot` (section 5.5). |
| `render` | string | no | values `view`, `module` | `view` keeps the library view where the build renders with the module (section 11.3); `module` is the default behaviour. |

`id`, `kind`, `x` and `y` are required by the schema; section 3.3 adds `w` and `h`. The symbol allows no other key.

### 5.2 Kinds and Position

The library kinds are in Table 11; the module-only kinds, which exist only under `--render module`, are in section 11.4.

Table 11. The library kinds of a descriptor (`screen.KIND_VIEW`, `library/contracts.json`, `library/profile.json`). Flow is the role in the flow graph (section 9.2); State is the contract's gate or state parameter.

| Kind | View | Anchor | Flow | State | Default size (px) | Faceplate |
|---|---|---|---|---|---|---|
| `pump` | `Automation/Pump` | symbol-centre | gate | on | 48 by 48 | `Faceplate/Pump` |
| `motor` | `Automation/Motor` | symbol-centre | gate | on | 48 by 48 | `Faceplate/Pump` |
| `fan` | `Automation/Fan` | symbol-centre | gate | on | 48 by 48 | `Faceplate/Pump` |
| `valve` | `Automation/Valve` | symbol-centre | gate | open | 48 by 48 | `Faceplate/Valve` |
| `analogvalve` | `Automation/AnalogValve` | symbol-centre | gate | open | 48 by 48 | `Faceplate/Valve` |
| `damper` | `Automation/Damper` | symbol-centre | gate | on | 48 by 48 | `Faceplate/Valve` |
| `filter` | `Automation/Filter` | symbol-centre | pass | on | 48 by 48 | `none` |
| `switch` | `Automation/Switch` | symbol-centre | gate | on | 48 by 48 | `none` |
| `indicator` | `Automation/Indicator` | symbol-centre | pass | on | 48 by 48 | `Faceplate/Input` |
| `generator` | `Automation/Generator` | symbol-centre | pass | on | 48 by 48 | `Faceplate/ASM/Generator` |
| `tank` | `Automation/Tank` | box | terminal | none | 168 by 216 | `Faceplate/Tank` |
| `readout` | `Automation/Readout` | symbol-centre | pass | none | 72 by 24 | `Faceplate/Instrument` |
| `instrument-field` | `Instrument/Field` | box | pass | none | 96 by 64 | `Faceplate/Instrument` |
| `controller` | `Instrument/Controller` | box | pass | none | 120 by 96 | `Faceplate/Controller` |
| `sequence` | `Instrument/Sequence` | box | pass | none | 144 by 72 | `Faceplate/Sequence` |
| `generator` with `picture` `genset` | `Automation/GeneratorSet` | box | pass | on | 240 by 150 | `Faceplate/ASM/Generator` |

The readout's contract states the anchor `symbol-centre`, but the generator treats the readout as a box kind (`screen.symbol_box`).
The anchor decides what `x` and `y` mean.

- **`symbol-centre`** (every automation kind except the readout): `x` and `y` are the top left corner of the 48 px symbol box.
  The symbol's centre is `(x + 24, y + 24)`. The embed, the box the generator gives the view, is larger than the symbol by the
  readout (section 7.2) and is placed so that the symbol keeps its place. `w` and `h` are not used for the symbol but must be
  present (section 3.3). Pipes end 18 px from the centre.
- **`box`** (tank, instrument field, controller, sequence, the generator set, and the readout): `x`, `y`, `w` and `h` are the
  box the view is drawn in. A readout is the exception that the generator may grow about its centre (section 7.3); every other
  box kind is used as given, and G5 warns of one smaller than its block needs.

### 5.3 Parameters, Static and Bound

`params` states a value of the view's contract; `bind` gives a parameter a tag member instead. A parameter named in either
must be in the kind's contract (section 6), or the generator reports `<id>: parameter '<name>' is not in the <view> contract`
(G7 contract). The exception is `bind.state` on an indicator (section 5.7). Values are not validated: a gate checks names, not
enumerations, so `readoutPosition` `middle` or `variant` `bogus` passes every gate and draws wrongly (proved on 2026-11-05).
Write only the values section 6 lists.

A bound parameter becomes a direct tag binding of the embedded view's parameter. The gate parameter (`on` for pump, motor, fan,
switch, damper, filter, indicator and generator; `open` for valve and analogue valve) is bound once on the view as
`custom.g_<id>`, a direct tag binding, and the symbol and the pipes read that. A parameter the generator binds itself is left
to its binding: a value stated beside it is dropped. Every other contract parameter that is neither bound nor stated is written
with its default, so a symbol never inherits another's value (GF-60, GF-61).

For a device symbol the generator also derives the alert parameters (`alert`, `alertFrameStatus`, `alertFrameMode`) from the
device's own alarms through one query for the page, unless the descriptor states or binds any of them. A lamp (indicator) draws
no alert frame.

### 5.4 Tag Paths and Initial Values

`screen.tag_path(root, member)` is the rule: a member that starts with `[` is used as it is; any other is `<tagRoot>/<member>`.
The same rule resolves `bind`, `device` folders, `alarm`, `bar.value`, pen tags, gate tags, well marks, emphasis tags,
`alarmPanels.sources` and pulse tags.

`tagModel` `generated` (the default) makes the test build write memory tags. The generator creates a tag for every relative
bound member, typed from the contract default (Boolean for a Boolean default, Float8 for a number, String for a string), valued
from `tagValues[member]`, else the symbol's static `params` of the same name, else the default. For a device symbol marked
`device` it also creates the faceplate members of the device's kind with their defaults, or, for a device the model names,
exactly the members the model lists in the model's types. Absolute members are never created. With `tagModel` `external` the
tags exist and none is created, and the gates read the tag model when `--tags-file` gives it. A descriptor that uses `tagModel`
`external` should be given `--tags-file`, so that G7 can check the folders.

### 5.5 Devices and Faceplates

A symbol with `device` opens the faceplate dock on a click (page 06 section 5). The rules:

1. `device` `true`: the device's tag folder is the symbol's `id` under `tagRoot`. `device` a string: that folder, for a second
   symbol of a device drawn elsewhere (for example an overview card). Without `device`, the symbol is not a device.
2. The faceplate is chosen by the symbol's kind, or by `params.deviceKind` where the symbol shows a member of a device of
   another kind (a readout or an instrument field of a controller's process value names `controller`).
3. The binding rule of Table 13: a state, speed, value, setpoint, output, manual, step or text parameter that is bound
   must be bound to `<folder>/<member>` of the device's kind. Another member, or one outside the folder, is a contract error:
   `<id>: '<param>' is bound to '<member>'; the faceplate reads '<folder>/<member>' (faceplate contract)`. The check applies
   when the device folder lies under `tagRoot`.
4. With a device model: every symbol marked `device` or `faceplate` must name a device of the model (`<route> <id>: device
   '<folder>' is not in the device model`), the symbol's kind (or `deviceKind`) must open the faceplate of the device's kind,
   every faceplate parameter it binds must be a member the model lists, and a block that draws a setpoint, an output or a step
   (`hasSetpoint`, `hasOutput`, `hasStep` true) belongs to a device that lists `sp`, `out` or `step` (page 08 section 5, its Table 4).
5. `label` becomes the faceplate header's description. The identifier shown is `params.tag`, else the folder's last segment.
6. `faceplate` (a symbol key) makes a symbol that is not the device open the faceplate of a device of the model on a click. The
   device's node stays where the page that draws it with `device` puts it, and the model supplies its kind.

### 5.6 Label, Bar and Render

`label` is the faceplate description (above). `bar` adds a range bar beside a readout or an instrument field (section 10.2).
`render` `view` keeps the library view when the build is `--render module` (section 11.3). `faceplate` is section 5.5 item 6.

### 5.7 Indicators: Alarm, States and the Lamp's State

An indicator is a lamp. Without `states` it follows a Boolean (`bind.on` or `bind.state`). With `states`, `bind.state` is the
member the lamp reads, of any type: an entry matches a value and gives the lamp its colour and an optional word; a value no
entry matches takes `stateDefault`. The type of the generated tag follows the values: String if any value is a string, Float8
if any is a number, else Boolean. `alarm` makes a fault row: the lamp's alert frame follows the alarms on that tag and flashes
until acknowledged; a generated build creates the tag as a Boolean memory tag. `alarm`, `states` and `stateDefault` belong to
an indicator: `alarm` on another kind is the generator error `<id>: 'alarm' is a key of an indicator; this symbol is a <kind>`, and
`states` and `stateDefault` on another kind are ignored.

Table 12. The keys of an entry of a symbol's `states` list.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `value` | boolean or number or string | yes |  | The state value this entry matches: a Boolean, a number or a string, as the tag carries it. |
| `colour` | string | yes |  | A palette name (`off`, `on`, `active`, `alarm`, `warning`, `caution`, `critical`, `neutral`) or a CSS paint; a name the palette does not know is used as a paint. |
| `label` | string | no |  | An optional word for the state. |

## 6. Symbol Parameters by Kind

### 6.1 Reading the Tables

Each table lists the parameters a descriptor may set on the kind (the `params` of `library/contracts.json`, the contract gate
G7 enforces), with the type read from the default and the default itself. The values column gives the enumeration where the
sources state one (page 06 Tables 2 and 3, `tools/hmi/testbench.py`); where it is empty the parameter is free (a number, a
string or a pattern). The note column is short; the meaning of each parameter is on page 06 sections 3 and 4.

The device-binding rule of each kind is Table 13.

Table 13. The binding rule of a device symbol, by the kind (`deviceKinds.<kind>.bind` of `library/profile.json`, from `screen.bind_rule` and `FACEPLATE_MEMBERS`). A bound parameter named here must be bound to `<device folder>/<member>`; a parameter not named is not checked against the folder.

| Kind | Faceplate | Parameter is member |
|---|---|---|
| `pump` | `Faceplate/Pump` | `on` is `state`, `open` is `state`, `speed` is `speed` |
| `motor` | `Faceplate/Pump` | `on` is `state`, `open` is `state`, `speed` is `speed` |
| `fan` | `Faceplate/Pump` | `on` is `state`, `open` is `state`, `speed` is `speed` |
| `valve` | `Faceplate/Valve` | `on` is `state`, `open` is `state` |
| `analogvalve` | `Faceplate/Valve` | `on` is `state`, `open` is `state` |
| `damper` | `Faceplate/Valve` | `on` is `state`, `open` is `state` |
| `filter` | none | none: the kind has no faceplate and no device kind |
| `switch` | none | none: the kind has no faceplate and no device kind |
| `indicator` | `Faceplate/Input` | `on` is `state`, `open` is `state` |
| `generator` | `Faceplate/ASM/Generator` | `on` is `state`, `open` is `state` |
| `tank` | `Faceplate/Tank` | none checked: `value` may be any member (the volume, for example); the faceplate reads `level` |
| `readout` | `Faceplate/Instrument` | `value` is `value` |
| `instrument-field` | `Faceplate/Instrument` | `value` is `value` |
| `controller` | `Faceplate/Controller` | `manual` is `manual`, `output` is `out`, `setpoint` is `sp`, `value` is `value` |
| `sequence` | `Faceplate/Sequence` | `step` is `step`, `text` is `stepText` |

A device symbol binds the faceplate members in the rule (on or open to the state, speed, value, and for a controller setpoint,
output and manual, for a sequence step and text) and binds nothing else inside the device folder except members the model
lists or, with a tag model, tags the folder carries (G7 devices).

### 6.2 Pump

Table 14. Parameters of `Automation/Pump` (kind `pump`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"pump"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

### 6.3 Motor

Table 15. Parameters of `Automation/Motor` (kind `motor`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"motor"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

### 6.4 Fan

Table 16. Parameters of `Automation/Fan` (kind `fan`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"fan"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

### 6.5 Valve

Table 17. Parameters of `Automation/Valve` (kind `valve`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"valve"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `open` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

### 6.6 Analogue Valve

Table 18. Parameters of `Automation/AnalogValve` (kind `analogvalve`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"analogvalve"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `open` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Opening in per cent. |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

### 6.7 Damper

Table 19. Parameters of `Automation/Damper` (kind `damper`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"damper"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

### 6.8 Filter

Table 20. Parameters of `Automation/Filter` (kind `filter`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"filter"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

The filter has a contract state `on`, but the flow graph treats it as a pass-through node (section 9.2).

### 6.9 Switch

Table 21. Parameters of `Automation/Switch` (kind `switch`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"switch"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

### 6.10 Indicator

Table 22. Parameters of `Automation/Indicator` (kind `indicator`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `colour` | string | `""` | Set by the generator from `states`. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"indicator"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `false` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

The indicator adds `colour`, which the generator sets from `states`; do not state it. Its `showStatus` defaults to false.

### 6.11 Generator

Table 23. Parameters of `Automation/Generator` (kind `generator`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `activated` | boolean | `false` | Selected background. |
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `badgeCommandLocked` | string | `"none"` | `none`, `command-locked`; Bottom right badge. |
| `badgeControl` | string | `"none"` | `none`, `auto`, `manual`, `manual-only`, `local`, `local-only`; Top left badge. |
| `badgeDuty` | boolean | `false` | Duty badge; also keeps the symbol on the library view under module rendering. |
| `badgeInterlock` | string | `"none"` | `none`, `interlock`, `interlock-inhibit`; Bottom left badge. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"generator"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasSpeed` | boolean | `false` | Show the speed on the status row. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `outOfService` | boolean | `false` | Veil and the word OOS; also keeps the symbol on the library view under module rendering. |
| `picture` | string | `"symbol"` | `symbol`, `genset`; `genset` selects the larger generator set picture. |
| `progress` | boolean | `false` | Spinning progress ring. |
| `readoutPosition` | string | `"bottom"` | `bottom`, `top`, `left`, `right`, `none`; Side of the readout; sets the embed box (section 7.2). |
| `showStatus` | boolean | `true` | Status row (On or Off, speed, opening). |
| `speed` | number | `0` | Speed in per cent. |
| `statusText` | string | `""` | Overrides the status text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `value` | number | `0` | Used by the analogue valve only (opening in per cent). |
| `variant` | string | `"regular"` | `regular`, `flat`, `double` |
| `vertical` | boolean | `false` | Vertical artwork. |

### 6.12 Generator Set

Table 24. Parameters of `Automation/GeneratorSet` (kind `generator` with `params.picture` `genset`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `alert` | boolean | `false` | Alert frame and flap. |
| `alertFrameMode` | string | `"acked-active"` | `acked-active`, `unacked-active`, `unacked-rectified` |
| `alertFrameStatus` | string | `"alarm"` | `alarm`, `warning`, `caution`, `critical` |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"generator"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `on` | boolean | `false` | State (gate): holder fill and icon follow it. |
| `picture` | string | `"genset"` | `symbol`, `genset`; `genset` selects the larger generator set picture. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |

A generator whose `params.picture` is `genset` is drawn by `Automation/GeneratorSet`, a box kind of 240 by 150 px, not by the
48 px symbol. It has no readout position and no status row.

### 6.13 Tank

Table 25. Parameters of `Automation/Tank` (kind `tank`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `chart` | boolean | `false` | A sparkline replaces the level box. |
| `compact` | boolean | `false` | Compact tile. |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasCapacity` | boolean | `true` | Draw the capacity line; true without `max` on a static tank is a G7 error. |
| `hasTag` | boolean | `true` | Draw the identifier (section 7.4). |
| `history` | array | `[]` | History data for the sparkline. |
| `max` | number | `100` | Capacity; a static tank without it draws no capacity line. |
| `medium` | string | `"normal"` | Medium name; the sources enumerate no values. |
| `showPercent` | boolean | `true` | Show the percentage. |
| `static` | boolean | `false` | A plain tile with no measurement (section 7.2). |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `trend` | string | `"stable"` | `fast-rising`, `rising`, `stable`, `falling`, `fast-falling` |
| `unit` | string | `"m³"` | Unit text. |
| `value` | number | `0` | The level or volume shown, in `unit`. |
| `valueFractionDigits` | number | `0` | Digits of the value; the module prints whole numbers only. |

A static tank (`static` true) that gives no `max` is drawn with `hasCapacity` false; stating `hasCapacity` true without `max`
is a contract error. The tank binds `value` to any member; the faceplate reads `level`.

### 6.14 Readout

Table 26. Parameters of `Automation/Readout` (kind `readout`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"instrument"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `format` | string | `"#,##0.0"` | Number format pattern. |
| `hasTag` | boolean | `false` | Draw the identifier (section 7.4). |
| `label` | string | `""` | Caption. |
| `stretch` | boolean | `false` | Fill the component box (module readout). |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `unit` | string | `""` | Unit text. |
| `value` | number | `0` | The value shown. |

### 6.15 Instrument Field

Table 27. Parameters of `Instrument/Field` (kind `instrument-field`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `align` | string | `"end"` | `start`, `center`, `end` |
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"instrument"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `format` | string | `"#,##0"` | Number format pattern. |
| `hasSetpoint` | boolean | `false` | Draw a setpoint (the device must list the setpoint member). |
| `hasTag` | boolean | `true` | Draw the identifier (section 7.4). |
| `label` | string | `""` | Caption. |
| `setpoint` | number | `0` | The setpoint value. |
| `setpointFormat` | string | `"#,##0"` | Number format of the setpoint. |
| `size` | string | `"regular"` | Block size. |
| `source` | string | `""` | Source text. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `unit` | string | `""` | Unit text. |
| `value` | number | `0` | The value shown. |

The field's caption is its `label`, a space and its `unit`.

### 6.16 Controller

Table 28. Parameters of `Instrument/Controller` (kind `controller`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"controller"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `format` | string | `"#,##0.0"` | Number format pattern. |
| `hasOutput` | boolean | `false` | Draw the output (the device must list `out`). |
| `hasSetpoint` | boolean | `false` | Draw a setpoint (the device must list the setpoint member). |
| `hasTag` | boolean | `true` | Draw the identifier (section 7.4). |
| `label` | string | `""` | Caption. |
| `manual` | boolean | `false` | Loop mode: false automatic, true manual. |
| `output` | number | `0` | Output in per cent. |
| `setpoint` | number | `0` | The setpoint value. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `unit` | string | `""` | Unit text. |
| `value` | number | `0` | The process value. |

### 6.17 Sequence

Table 29. Parameters of `Instrument/Sequence` (kind `sequence`): defaults from `library/contracts.json`.

| Parameter | Type | Default | Values or note |
|---|---|---|---|
| `deviceId` | string | `""` | Set by the generator from `device`; do not state it. |
| `deviceKind` | string | `"sequence"` | Faceplate kind; the generator keeps the default unless the descriptor names another. |
| `deviceLabel` | string | `""` | Set from the symbol's `label`. |
| `hasStep` | boolean | `false` | Draw the step number (the device must list `step`). |
| `hasTag` | boolean | `true` | Draw the identifier (section 7.4). |
| `label` | string | `""` | Caption. |
| `step` | number | `0` | Step number. |
| `tag` | string | `""` | The identifier text; up to 16 characters are drawn in full. |
| `text` | string | `""` | Step text. |

## 7. The Placement Arithmetic

### 7.1 Sizes

Table 30. Sizes and identifier rules by kind (`kinds.<kind>.size`, `sizes` and `identifier` of `library/profile.json`). A box smaller than the size the flags need draws a G5 warning, except a readout, which the generator grows.

| Kind | Size (px) | Larger sizes (when: size) | Identifier parameter | Font | Pad (px) | Fits (characters) |
|---|---|---|---|---|---|---|
| `pump` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `motor` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `fan` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `valve` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `analogvalve` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `damper` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `filter` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `switch` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `indicator` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `generator` | 48 by 48 | none | `tag` (flag `hasTag`) | `automation-label` | 8 | 8 |
| `tank` | 168 by 216 | static true: 96 by 80 | `tag` (flag `hasTag`) | `instrument-label` | 24 | 19 |
| `readout` | 72 by 24 | hasTag true: 72 by 40 | `tag` (flag `hasTag`) | `automation-label` | 10 | 7 |
| `instrument-field` | 96 by 64 | hasSetpoint true/size "enhanced": 96 by 66 | `label` and `unit` (flag `hasTag`) | `instrument-unit` | 0 | 12 |
| `controller` | 120 by 96 | none | `tag` (flag `hasTag`) | `automation-label` | 34 | 10 |
| `sequence` | 144 by 72 | none | `tag` (flag `hasTag`) | `automation-label` | 14 | 16 |

A kind uses its default size with every flag at its default; an entry of the larger sizes applies when the symbol's parameters
(or the contract's defaults for the parameters it does not give) meet its condition. The first entry that fits is taken
(`library.block_size`). The automation kinds have a 48 px symbol box, whatever the descriptor's `w` and `h`.

### 7.2 The Embed Box of an Automation Symbol

An automation symbol's descriptor box is the 48 px symbol. The generator draws the view in an embed that adds the readout on the
side `readoutPosition` names, and offsets it so that the symbol stays at `(x, y)`.

Table 31. The embed box of an automation symbol at the default identifier width, as an offset from the 48 px symbol box `[dx, dy, width, height]` (`kinds.<kind>.embedBox` of `library/profile.json`; the same for every automation kind). The reach column is `screen.READOUT_EXTENT`, how far the embed reaches beyond the symbol box across and down.

| `readoutPosition` | Offset and size | Reach (across, down) | Embed box for a symbol at (x, y) |
|---|---|---|---|
| `bottom` | `[-12, 0, 72, 92]` | 24, 44 | (x - 12, y, 72, 92) |
| `top` | `[-12, -44, 72, 92]` | 24, 44 | (x - 12, y - 44, 72, 92) |
| `left` | `[-64, 0, 112, 48]` | 64, 0 | (x - 64, y, 112, 48) |
| `right` | `[0, 0, 112, 48]` | 64, 0 | (x, y, 112, 48) |
| `none` | `[0, 0, 48, 48]` | 0, 0 | (x, y, 48, 48) |

Where the identifier is longer than the default readout holds, the embed is widened (section 7.3). A symbol with
`readoutPosition` `none` has no readout and no identifier.

A static tank's tile lies inside the tank's box at the fractions `[0.06, 0.06, 0.88, 0.66]` of its width and height
(`diagram.staticTile`); a pipe at its left, right or top ends at the tile. The rule of every other box kind is that the pipe ends
at the middle of the box's side.

### 7.3 The Identifier Width

An identifier of n characters needs `min(n, 16) * charWidth + pad` px, with the font and the pad of the kind
(Table 30) and the character width of Table 32. No more than 16 characters are drawn in full
(`text.identifierChars`).

Table 32. Fonts of the identifiers (`text.fonts` of `library/profile.json`). The width allowed for n characters is n times `charWidth`.

| Font | Size (px) | Line (px) | Allowed per character (px) | Measured upper case | Lower case | Digit | Widest glyph |
|---|---|---|---|---|---|---|---|
| `automation-label` | 12 | 16 | 8 | 7.61 | 6.36 | 6.61 | 11.22 |
| `automation-value-regular` | 16 | 22 | 9.5 | 10.62 | 9.09 | 9.15 | 15.6 |
| `instrument-label` | 11.5 | 16 | 7.5 | 7.3 | 6.1 | 6.33 | 10.76 |
| `instrument-unit` | 11.5 | 16 | 7.5 | 7.3 | 6.1 | 6.33 | 10.76 |

For an automation symbol, with `need = min(n, 16) * 8 + 8` (font `automation-label`, pad 8) and the identifier shown (`tag` set
and `hasTag` not false):

- beneath or above the symbol: the embed is `max(24, need - 48) + 48` px wide, centred on the symbol (the default 72);
- beside the symbol: the embed is `48 + max(64, need)` px wide, growing away from the symbol (the default 112).

An identifier that fits the default (8 characters beneath a symbol, 7 beside it) changes nothing. For a readout the box grows
about its centre to the larger of the box and the size its flags need, and to the width `min(n, 16) * 8 + 10` of its identifier
when it shows one (`library.identifier_width`, `screen.grown_box`); a box that holds its block is used as given. A tank's
identifier is measured against the share `0.86` of the tile's width, or the whole box of a static tank. A controller, a sequence
and an instrument field do not grow: a box smaller than the block needs draws a G5 warning, and an identifier wider than the
box ends in an ellipsis.

### 7.4 When the Identifier Is Drawn

- With `toolbar` true (the default) the toolbar's ID-tag button binds `hasTag` for every automation symbol, tank, readout and
  instrument field, as the button's state and the descriptor's own answer. The own answer of an automation symbol is true
  unless the descriptor says `hasTag` false (or `readoutPosition` `none`); that of a tank, a readout and an instrument field is
  the stated `hasTag`, else the contract default, which is true for the tank and the field and false for the readout, so a
  readout needs `hasTag` true. The button starts on when `showTags` is true. A controller and a sequence keep their own `hasTag`.
- With `toolbar` false there is no button: the stated `hasTag` applies, and the contract default is false for the automation
  symbols and the readout (true for a tank, a field, a controller and a sequence). State `hasTag` true, with `tag`, on every
  symbol that should show an identifier (proved on 2026-11-05).
- A symbol with `alarm` keeps its text as stated; the toolbar does not hide it.

### 7.5 Overlap, Rows and Gate G5

Gate G5 measures the built page:

- **Inside the canvas.** The box of every embedded view (a module component's box is its symbol box) must lie within `0 <= x`, `x + w <= width`,
  `0 <= y`, `y + h <= height` of the page. A symbol whose widened embed passes an edge is an error: `<name> outside the canvas`.
- **Symbols do not overlap.** Two symbol boxes (the 48 px box of an automation symbol, the whole box of any other kind) overlap
  when they share more than `OVERLAP` = 4 px on both axes. That is an error: `symbol <a> overlaps <b> (<dx> x <dy> px)`. A
  symbol wholly inside a vessel and clear of the vessel's own texts and level is placed there on purpose and is not reported.
- **Readout areas** (the embeds) that overlap the same way are warnings, as is a block smaller than its flags need and an
  identifier that ends in an ellipsis.

Two symbols are on one row when the boxes they have without the widening share more than 4 px down the page. The widening of
an embed stops at the next symbol on its row (`screen.embed_limits`): with `gap` the distance between the two boxes without the
widening and each wanting `(embed width - width without the widening) / 2` towards the other, both are widened in full when the
wants together do not exceed `gap`; otherwise each takes `gap / 2`, or the one that wants less takes its want and the other the
rest. An embed centred on its symbol or box gives up on both sides what it lacks on one. A builder that keeps `gap` at least the
sum of the two wants gets every identifier whole and no warning.

### 7.6 The Canvas, the Viewport and Fit

`frame` of `library/profile.json` states the sizes that bound a page: the viewport of the render gate is 1600 by 900 px, the top
dock 48 px, the faceplate dock 400 px, the canvas of a cards page 1600 by 852 px, and the canvas of the sample plant's diagrams
1580 by 600 px (which fits beside the open faceplate dock). A diagram of any width and height is drawn at `screen.width` by
`screen.height` in a canvas that scrolls; `fit` scales it instead.

With `fit` the diagram keeps its box and takes a CSS scale from its top left corner. The scale is
`min(1, min((viewportWidth - reserveX - dock) / width, (viewportHeight - reserveY) / height))`, where `dock` is 400 while the
faceplate dock is open and 0 otherwise; `reserveY` defaults to 104 px with the toolbar (the 48 px top dock and the 56 px
toolbar) and 48 px without it, and `reserveX` to 0. Under the module rendering the measured canvas replaces the viewport:
`min(1, min((canvasWidth - reserveX) / width, canvasHeight / height))`. The user's zoom, from 0.5 to 4 in steps of 1.25, multiplies
the result. A 1580 by 740 page keeps its size at 1600 by 900 and scales to 0.81 at 1280 by 800, where the width decides.

### 7.7 A Worked Example

The fixture `tests/fixtures/pilot-supply.json` (a diagram 1580 by 600 px) holds three cases.

- **A pump with a 14 character identifier.** `P2` is a pump at `(300, 340)`, `readoutPosition` `bottom`, `tag` `SupplyPump_No2`.
  `need = 14 * 8 + 8 = 120`. The reach across is `max(24, 120 - 48) = 72`, so the embed is `48 + 72 = 120` px wide and
  `48 + 44 = 92` px high, with its left edge at `300 - 72 / 2 = 264`: the box `(264, 340, 120, 92)`. The pump `P1` above it
  (tag `P-1`, 3 characters) has the default embed `(288, 160, 72, 92)`, which ends at y = 252, above P2's top at 340, so the two
  are not on one row.
- **A lamp with a 16 character identifier.** `DI1` at `(1366, 160)`, `bottom`, `SuctionLowLvl_SW`: `need = 16 * 8 + 8 = 136`,
  the reach is `136 - 48 = 88`, the embed is 136 px wide from `1366 - 44 = 1322` to 1458, inside the 1580 px canvas.
- **A readout with a 15 character identifier.** `FT1` is a box kind at `(520, 164)` with `w` 130 and `h` 40, `tag`
  `SupplyFlow_FT01`: the width it needs is `15 * 8 + 10 = 130` and it needs 40 px with its identifier (`hasTag` true), so the box
  is used as given. Had it been given as 72 by 24 px at the same point, the generator would have grown it about its centre
  to 130 by 40 px, to `(491, 156)`.

## 8. The Cards Layout

### 8.1 Structure

A cards page has `rows`, an array of rows, each an array of cards. A card has a card body of one of two forms.

1. **A flex body** (`body`): a group of `direction` `row` or `column` whose `items` are nested groups, flex symbols and label
   leaves. This is the form that scales with the page. A leaf sizes by `basis` and `grow`.
2. **Items** (`items`, `bodyWidth`, `bodyHeight`): symbols at pixel positions inside a body of the stated size. The generator
   converts the positions to fractions of the body.

Table 33. The keys of a card (`$defs/card`).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes |  | The card's name. |
| `title` | string | no |  | The card's title; a titled card takes 40 px of height. |
| `bodyWidth` | number | no | minimum 1 | With `items`: the width in px of the card body that the items' coordinates refer to. |
| `bodyHeight` | number | no | minimum 1 | With `items`: the height of the card body; the card needs exactly this height. |
| `items` | array of symbol object | no |  | Symbols placed at pixel positions in the card body (the symbol object of Table 10; the generator converts the positions to fractions of the body). |
| `body` | group object | no |  | A flex group (Table 34) that lays out the card's leaves. A card carries `body` or `items` with both body sizes. |
| `basis` | string | no |  | The card's flex basis, for example `0px` or `320px` (default `0px`). |
| `grow` | number | no | minimum 0 | The card's flex grow (default 1). |
| `route` | string | no | pattern `^/` | With `body`: a click on the card's title opens this route, and the title shows a chevron. |

Table 34. The keys of a flex group (`$defs/group`).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `direction` | string | no | values `row`, `column` | `row` (default) or `column`. |
| `basis` | string | no |  | The group's flex basis as a nested group (default `0px`). |
| `grow` | number | no | minimum 0 | The group's flex grow (default 1 as a nested group). |
| `justify` | string | no | values `flex-start`, `flex-end`, `center`, `space-between`, `space-around`, `space-evenly` | Main-axis justification (default `flex-start`). |
| `items` | array of groups, flex symbols and label leaves | yes |  | Groups, flex symbols and label leaves, in order. |

Table 35. The keys of a flex symbol, a symbol leaf of a card body (`$defs/flexSymbol`).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes |  | The leaf's name (no pattern is applied). |
| `kind` | string | yes |  | As for a diagram symbol. |
| `basis` | string | no |  | The leaf's flex basis, for example `0px` or `64px`. |
| `grow` | number | no | minimum 0 | The leaf's flex grow. |
| `params` | object | no |  | As for a diagram symbol. |
| `bind` | object | no |  | As for a diagram symbol. |
| `device` | boolean or string | no |  | As for a diagram symbol. |
| `label` | string | no |  | The device description for the faceplate header. |
| `states` | array of object | no |  | As for an indicator (Table 12). |
| `stateDefault` | string | no |  | As for an indicator. |
| `faceplate` | string | no |  | As for a diagram symbol. |
| `render` | string | no | values `view`, `module` | As for a diagram symbol. |

Table 36. The keys of a label leaf of a card body (`$defs/label`).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `label` | string | yes |  | The text, one line in the label style. |
| `basis` | string | no |  | The leaf's flex basis. |
| `grow` | number | no | minimum 0 | The leaf's flex grow. |

A leaf is a group if it has `items`, a symbol if it has `kind`, a label if it has `label` and no `kind`. A flex symbol has no
`x`, `y`, `w` or `h`, no `bar` and no `alarm`; page parts are not allowed on a cards page. A symbol in a card has no toolbar,
so state `hasTag` true on one that should show its identifier.

### 8.2 The Height of a Row

A row is as high as its tallest card needs, and the rows stand at the top of the page in their order (page 08 section 3.2). The
arithmetic of `screen.row_height`:

- A card needs `40` px for its title (when it has one), its body and `8` px beneath the body; a card of `items` needs the
  title and its `bodyHeight` and no extra 8 px.
- A row is the tallest card, rounded up, plus `16` px (8 px of margin above and below).
- A leaf: `16` px for a label; for an automation symbol `48` plus the reach down of its readout (44 for `bottom` and `top`,
  0 beside or `none`); for any other kind the height the profile gives for its flags (64 for an instrument field, 216 for a
  tank).
- Across a group of direction `row` the tallest item. Down a group of direction `column`: `fixed + share * grows`, where
  `fixed` is the 4 px gaps between the items plus each item's basis (a basis in px, else the item's own height; a nested group's
  basis defaults to 0 px), `grows` is the sum of the items' `grow` (a nested group's defaults to 1, a leaf's to 0), and
  `share` is the largest `(height - basis) / grow` among the items that grow: the column is as high as the item that asks the
  largest share.
- A kind the library lacks is a gap box with no size of its own. A row that holds one shares the height the page has left, and
  the page does not scroll.

The rows together may be taller than the viewport; the page then scrolls.

### 8.3 A Worked Row

The cards example of section 13.2 has a card `Flows` and a card `Pumps`. `Flows` is a column of a label leaf (16 px) and a
nested row group with basis `64px` that holds two instrument fields: `40 + (16 + 4 + 64) + 8 = 132` px. `Pumps` is a card of
items with `bodyHeight` 140: `40 + 140 = 180` px. The row is `ceil(max(132, 180)) + 16 = 196` px, which `screen.row_height`
returned for the descriptor.

## 9. Pipes, Junctions, Sections, Labels, Toolbar and Tag Display

### 9.1 Sections

Table 37. The keys of an entry of `sections`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes |  | The section's name. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `label` | string | no |  | A caption in the section's top right. |
| `route` | string | no | pattern `^/` | A click on the section navigates to this route. |

A section is a background panel (surface class `cadre/surface/section`) drawn first, beneath the pipes. With `route` it is a
click target that navigates; the pointer shows it.

### 9.2 Junctions, Pipes and the Flow Rules

Table 38. The keys of an entry of `junctions`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes |  | The junction's name, used as `ref` by pipe ends. |
| `x` | number | yes |  | Its x. |
| `y` | number | yes |  | Its y. |

Table 39. The keys of an entry of `pipes`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes |  | The pipe's name; also the name of its path in the pipe drawing. |
| `from` | pipe end | yes |  | The start end (Table 40 and Table 41 give the two forms). |
| `to` | pipe end | yes |  | The finish end. |
| `via` | array of [x, y] pairs | no | each pair has exactly 2 numbers | Points the pipe passes through, in order; elbows are added between points that share neither x nor y. |
| `medium` | string | no | values `neutral`, `fresh-water`, `sea-water`, `fuel`, `oil`, `steam`, `hot`, `cold`, `air`, `waste` | The fluid, which colours the pipe when the toolbar's Color button is on. Default `neutral`, which has no colour. |
| `size` | string | no | values `small`, `medium`, `large`, `xl` | The line width: `small` 2 px, `medium` 4 px (default), `large` 6 px, `xl` 10 px, each with a 2 px wider outline. |
| `state` | string | no | values `open`, `closed` | `closed` blocks the flow and draws the pipe closed; default `open`. |

Table 40. A pipe end that refers to a symbol or a junction (the first form of `$defs/end`).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `ref` | string | yes |  | The id of a symbol or of a junction. |
| `side` | string | no | values `top`, `bottom`, `left`, `right` | The symbol side the pipe meets. Absent, `top` is taken. Ignored for a junction. |
| `x` | number | no |  | With `y`, a point that replaces the side's connection point for a symbol (an explicit attachment). |
| `y` | number | no |  | See `x`. |

Table 41. A free pipe end (the second form of `$defs/end`).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `x` | number | yes |  | The free end's x. |
| `y` | number | yes |  | The free end's y. |
| `end` | string | no | values `cap`, `arrow-in`, `arrow-out`, `none` | The end mark: `arrow-in` makes the end a source of flow, `arrow-out` a sink, `cap` (the default) and `none` neither; `cap`, `arrow-in` and `arrow-out` draw a mark. |

The route of a pipe is orthogonal. A pipe end on a symbol side meets the holder ring of an automation symbol (18 px from the
centre), the middle of the side of any other box, or, for a static tank, the tile (section 7.2). Without `via` points, two ends
that share an x or a y are joined straight; otherwise the shape follows the axis each end leaves on (`v` a top or bottom side,
`h` a left or right side, `-` a junction or a free end), start then end:

Table 42. The route of a pipe without `via` points (`diagram.ROUTES`, `diagram` of `library/profile.json`).

| Axes (start, end) | Shape | Path |
|---|---|---|
| `vv` | `Z_Y` | down or up to the rounded mean of the two y, across, then on |
| `hh` | `Z_X` | across to the rounded mean of the two x, up or down, then on |
| `vh`, `v-`, `-h`, `--` | `L_Y` | one corner at the x of the start and the y of the end |
| `hv`, `h-`, `-v` | `L_X` | one corner at the x of the end and the y of the start |

Between consecutive `via` points that share neither coordinate the shape is `L_X`.

The flow rules (decision COBD-006; page 08 section 4) decide whether a pipe draws as carrying the medium:

1. A tank is a source and a sink. A free end marked `arrow-in` is a source and one marked `arrow-out` a sink. Any other end is
   neither.
2. A valve and an analogue valve pass while `open`; a pump, a motor, a fan, a switch and a damper pass while `on`
   (`diagram.GATED`). The filter, the indicator, the generator, a readout, a field, a controller, a sequence and a junction
   always pass. A gated symbol that neither binds nor states its state parameter (`open` for the valves, `on` for the others) has no
   state to follow and passes as a junction does: the flow graph gives it no gate, so no expression names a variable for it
   (`diagram.build_graph`; the case is a switch drawn with neither, section 12 G3). An assembly is no node of the graph: a pipe
   ends at a junction or a free end beside its box, because a `ref` names a symbol or a junction.
3. A pipe carries the medium when it lies on a simple path from a source to a different sink through passing gates. A closed
   pipe (`state` `closed`) is left out of the graph and blocks.
4. Each pipe's condition is compiled to one expression over the gate variables (`custom.g_<id>`), drawn as the colour of the
   inner stroke; gate G6 proves it equals the reference solver for every state of up to 12 gates and for a sample of 4,096 above.
   A pipe on no such path is never energised (the expression is `false`); one on a path with no gate is always (`true`). A page
   needs a source (a tank or an `arrow-in` end) and a different sink (a tank or an `arrow-out` end) for any pipe to show flow.
5. A page with more than 20,000 source to sink paths is refused: `flow: path enumeration limit reached; split the diagram`.

### 9.3 Labels

Table 43. The keys of an entry of `labels`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes |  | The label's name. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `text` | string | yes |  | The text; one line, not wrapped. |
| `align` | string | no | values `left`, `center`, `right` | Horizontal alignment (default `left`). |
| `style` | string | no | values `heading`, `body`, `label` | The text style: `heading`, `body` or `label` (default `label`). |
| `emphasis` | any | no |  | Makes the label bold and active while a Boolean holds (Table 44). |

Table 44. The keys of a label's `emphasis` object. Exactly one of `tag` and `symbol` is required.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `tag` | string | no |  | A Boolean tag member. |
| `symbol` | string | no |  | A symbol of the page that has a state; the label follows its state. |
| `words` | array of string | no | at least items 2; at most items 2 | Two words: the first shows while the Boolean is clear, the second while it holds. |

An emphasised label needs a Boolean: a tag member or a symbol with a state (the pump, motor, fan, valve, analogue valve,
damper, filter, switch, indicator and generator have one; the tank and the readout have not). A label with `emphasis` and
`tag` makes the generator create a Boolean memory tag in a generated build.

### 9.4 The Toolbar

`toolbar` true puts an operator toolbar on a diagram: Color (only if some pipe names a `medium` with a colour, that is any
but `neutral`), ID-tag, Readout, and the zoom controls (minus, the percentage, plus). ID-tag and Readout flip
`custom.showTag` and `custom.showReadout`; the symbols' bindings follow them. A page with `toolbar` false has none of these and
always shows identifiers where `hasTag` is true.

### 9.5 Identifier Tags at Start

`showTags` true starts the ID-tag button on. The default is false. A page without a toolbar always shows the identifiers that
state `hasTag` true.

## 10. Page Parts

Page parts belong to the diagram layout (section 3.1) and work under both renderings. The ids of the parts are unique among
the parts and differ from every symbol's id: a repeat is `<array>: the id '<id>' is used twice among the page parts` or `is
also a symbol's`.

### 10.1 Command Buttons

Table 45. The keys of an entry of `buttons`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The button's name; unique among all page parts and not a symbol's id. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `label` | string | yes |  | The caption. |
| `style` | string | no | values `normal`, `flat` | `normal` (default) or `flat`. |
| `render` | string | no | values `view`, `module` | A pulse button only: `module` draws the question button with the module's button when the build is `--render module` and the registry lists it; `view` (default) keeps the library's button. Any other action with `render: module` is a generator error. |
| `action` | object | yes |  | One action: `pulse`, `faceplate` or `route` (Table 46). |

Table 46. The three actions of a button (`buttons[].action`; each type allows only its own keys).

| Type | Key | Required | Constraint | Meaning |
|---|---|---|---|---|
| `pulse` | `tag` | yes | string | The tag pulsed, relative to `tagRoot` or an absolute `[provider]path`. It is declared in `session.custom.commands`; a generated build creates it as a Boolean memory tag. |
| `pulse` | `ms` | no | integer 100 to 600000; default 1000 | How long the tag is held true. One tag has one length across the whole page set. |
| `pulse` | `confirm` | no | string | The question shown with Confirm and Cancel; default the label and a question mark. |
| `faceplate` | `device` | yes | string | A symbol of the page by its id, or a device folder relative to `tagRoot`. Some symbol of the page set must mark that folder `device`. |
| `faceplate` | `tab` | no | string | A faceplate tab key (`home`, `config`, `diagnostics`, `alarms`, `interlocks`, `info`, or a stock key); a key the faceplate lacks opens the first tab. |
| `faceplate` | `kind` | no | string | The device kind; required where `device` is no symbol of the page. |
| `faceplate` | `title`, `label` | no | string | The title and description shown in the faceplate header; absent, the symbol's identifier and label, else the folder name. |
| `route` | `route` | yes | pattern `^/` | The route the button navigates to. |

A pulse is never written on the first press. The press shows the question with Confirm and Cancel in the button's place;
Confirm calls `cadre.hmi.page_pulse` under write path W18, which needs the gateway's `Administrator` role and writes only a
tag listed in `session.custom.commands`, which the generator writes from the descriptors. The buttons that can reach the call
bind `enabled` to the permission of W18 (gate G7 commands). The same tag with two lengths is an error, on one page
(`pulse <path>: two lengths, <a> and <b> ms`) or across the set (`... two lengths across the page set ...`). A `faceplate` action names a device some symbol of
the set marks `device`, or the build reports `button <id>: <path> is no device of the page set`; where `device` is no symbol of
the page, `kind` is required (`button <id>: the faceplate action names '<x>', which is no symbol of the page; state its kind`).

### 10.2 Range Bars

A bar is placed in two ways. Beside a readout or an instrument field, the symbol takes a `bar` key and no position of the
descriptor moves; elsewhere the array `bars` holds a bar with its own box.

Table 47. The keys of an entry of `bars`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The bar's name; unique among page parts. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `value` | string | yes |  | The tag member shown (a string; a bar without one is a generator error). |
| `min` | number | no |  | Low end of the scale (default 0). |
| `max` | number | no |  | High end (default 100). |
| `normalLo` | number | no |  | Low end of the normal band. |
| `normalHi` | number | no |  | High end of the normal band. |
| `loLimit` | number | no |  | Low limit mark. |
| `hiLimit` | number | no |  | High limit mark. |
| `unit` | string | no |  | Unit text. |
| `format` | string | no |  | Number format of the value text (default `#,##0.0`). |
| `vertical` | boolean | no |  | Vertical bar. |
| `showValue` | boolean | no |  | Show the value beside the bar. |

Table 48. The keys of a symbol's `bar` object.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `min` | number | no |  | The low end of the scale (default 0). |
| `max` | number | no |  | The high end of the scale (default 100). |
| `normalLo` | number | no |  | The low end of the normal band. |
| `normalHi` | number | no |  | The high end of the normal band. |
| `loLimit` | number | no |  | A mark at the low limit. |
| `hiLimit` | number | no |  | A mark at the high limit. |
| `value` | string | no |  | The tag member the bar shows; absent, the symbol's bound `value`. |
| `unit` | string | no |  | The unit text beside the value when `showValue` is true. |
| `format` | string | no |  | The number format of the value text (default `#,##0.0`). |
| `vertical` | boolean | no |  | A vertical bar, the high end at the top. |
| `showValue` | boolean | no |  | Show the value and its unit beside the bar. |
| `side` | string | no | values `right`, `left`, `below`, `above` | The side of the readout's box the bar stands on (default `right`). |
| `length` | number | no | minimum 1 | The bar's length in px (default 64, or 128 when vertical). |
| `thickness` | number | no | minimum 1 | The bar's thickness in px (default 10). |
| `gap` | number | no | minimum 0 | The space in px between the readout's box and the bar (default 4). |
| `x` | number | no |  | Places the bar outright: its left edge, overriding `side`. |
| `y` | number | no |  | Its top edge. |
| `w` | number | no | minimum 1 | Its width. |
| `h` | number | no | minimum 1 | Its height. |

The bar of a symbol stands against the readout's box as the library gives it (`screen.symbol_box`): `right` at `x + w + gap`,
centred on the box's height; `left` at `x - gap - length`; `below` and `above` centred on the box's width, and `length`
defaulting to the box's width. `x`, `y`, `w` and `h` of the `bar` override the side. A `bar` needs the symbol to bind `value` or
the bar to name its own `value`; a `bar` on a symbol that is not a readout or a field is `<id>: 'bar' is a key of a readout or an
instrument field; this symbol is a <kind>`.

### 10.3 Embedded Trends

Table 49. The keys of an entry of `trends`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The trend's name. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `title` | string | no |  | The trend's title. |
| `minutes` | integer | no | minimum 1; default `10` | How many of the last minutes the chart shows. |
| `pens` | array of object | yes | at least items 1; at most items 2 | One or two pens. Two pens whose units differ get an axis each. |

Table 50. The keys of a pen of a trend.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `tag` | string | yes |  | The pen's tag member (relative or absolute); it needs history enabled and a history provider in the tag model. |
| `label` | string | no |  | The legend text. |
| `unit` | string | no |  | The unit; it decides whether two pens share an axis. |

The part is the stock time series chart over the tag history of the pens, in one of three library views chosen from the pens:
`Parts/Trend` (one pen), `Parts/Trend2` (two pens, one axis) and `Parts/Trend2Axes` (two pens whose units differ). A pen's tag
needs `historyEnabled` true and a `historyProvider` the gateway has in the tag model; a generated build writes memory tags
without history, so its trends draw nothing, and a build with a tag model reports a note naming each pen the tag model does not
historise. Three pens, or none, fail G0 (`pens` has one or two).

### 10.4 Lines

Table 51. The keys of an entry of `lines`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The line's name. |
| `points` | array of [x, y] pairs | yes | at least items 2; each pair has exactly 2 numbers | The vertices, joined by straight segments. |
| `width` | number | no | minimum 0.5; default `2` | Stroke width in px. |
| `style` | string | no | values `solid`, `dashed` | `solid` (default) or `dashed`. |
| `gate` | object or array | no |  | One gate or a list of gates, each `{"tag": <Boolean member>}` or `{"symbol": <id>}` (exactly one key each). The line is solid while every gate holds and light and dashed while not. |

Lines are drawn beneath the symbols with the pipes. A `gate` with a `symbol` needs a symbol that has a state; a `gate` naming a
symbol the page lacks is `line <id>: the gate names the symbol '<x>', which the page lacks`. A list of gates needs all of them.

### 10.5 Links, Brackets and Wells

Table 52. The keys of an entry of `links`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The link's name. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | no | minimum 1 | Width (default 24). |
| `h` | number | no | minimum 1 | Height (default 24). |
| `route` | string | yes | pattern `^/` | The route a click opens. A link never opens a faceplate. |
| `icon` | string | no | default `chevron-right-google` | An icon of `library/icons` (a missing file is a generator error). |

Table 53. The keys of an entry of `brackets`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The bracket's name. |
| `x` | number | yes |  | The bracket's left end. |
| `y` | number | yes |  | Its y. |
| `w` | number | yes | minimum 1 | Its length. |
| `label` | string | yes |  | The name shown beyond the bracket. |
| `side` | string | no | values `below`, `above` | `below` (default): the group is above the bracket; `above`: the group is below it. |

Table 54. The keys of an entry of `wells`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The well's name. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `marks` | array of object | yes | at least items 1 | Level switches from the lowest level up, each level once (a generator error otherwise). |

Table 55. The keys of a mark of a well.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `level` | number | yes | greater than 0; maximum 1 | A fraction of the well's height from its floor, above 0 and not above 1. |
| `tag` | string | yes |  | A Boolean tag member, true while the level is reached. |

A link's icon must be a file of `library/icons` (`<icon>.json`); the default is `chevron-right-google`. A well is filled up to
the highest mark whose tag is true, with a lighter band up to the next mark; it states no percentage. The marks must rise, each
level once: `well <id>: the marks run from the lowest level up, each level once`.

### 10.6 Alarm Panels

Table 56. The keys of an entry of `alarmPanels`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z0-9_-]+$` | The panel's name. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `sources` | array of string | yes | at least items 1 | Tag folders (relative to `tagRoot` or absolute) whose alarms the panel lists. |

The panel embeds `Faceplate/Alarms` (the stock table, or the module's lists under `--render module`) over the alarms under the
tag folders of `sources`, with Ack selected and Ack all beneath it.

### 10.7 Marks on a Symbol

Every automation symbol takes `badgeDuty` and `outOfService`, stated or bound. The module's components lack both unless their
schema lists them, so a symbol that states or binds one stays on the library view under `--render module` (section 11.2).

### 10.8 Local Assemblies

A local assembly draws a plant object for which the library has no kind (page 16 section 6.3). The descriptor gives the object's parts once per
kind, as pixel boxes of labels, shapes, lines, readouts, indicators, instrument fields and pulse buttons; the generator writes them as the views
`Local/<Kind>/Assembly` and `Local/<Kind>/Home` (section 10.11) and embeds the first at each assembly's box with the instance's tag folder. An assembly
is a device of the kind `local`: a click opens the faceplate `Faceplate/ASM/Local`, whose Home tab shows the kind's Home view. Assemblies
belong to the diagram layout, need `screen.py --local-kinds` (Table 2) and are the page part `assemblies` of Table 7.

Table 56a. The keys of an entry of `assemblies` (`$defs/assembly`; no other key is allowed).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z][A-Za-z0-9_]*$` | The assembly's name on the page and the prefix of its parts in a mapping (`<id>/<part id>`). It is a page part id: unique among the page parts and not a symbol's id (section 10), and it has no hyphen. |
| `kind` | string | yes | pattern `^[a-z][a-z0-9-]*$` | The local kind. Its views lie in the folder `Local/<Kind>`, the kind with its first letter in upper case and the rest as written. It must be in the `--local-kinds` list and must not be a kind of the library (Table 56i). |
| `device` | string | yes | pattern `^[^/\[{}]([^{}]*[^/{}])?$`; no empty, `.` or `..` segment | The instance's tag folder, relative to `tagRoot`: not absolute, no braces, no leading or trailing `/`, and no segment that is empty, `.` or `..`. |
| `title` | string | no |  | The identifier in the faceplate header. Default: the kind as written. |
| `label` | string | no |  | The device's description in the device index. Default: the `id`. |
| `x` | number | yes |  | Left edge on the page. |
| `y` | number | yes |  | Top edge on the page. |
| `w` | number | yes | minimum 1 | Width of the embed, and of the kind's view. |
| `h` | number | yes | minimum 1 | Height of the embed, and of the kind's view. |
| `parts` | part set | yes | at least one of the five arrays, with at least one entry | The parts drawn on the page, in pixels from the assembly's top left corner (Table 56c). |
| `home` | object | no |  | The Home tab of the local faceplate (Table 56b). Absent, the kind's Home is one label, No detail, in a view of 360 by 80 px. |

Table 56b. The keys of `home`.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `w` | number | yes | minimum 1 | Width of the Home view. |
| `h` | number | yes | minimum 1 | Height of the Home view. |
| `parts` | part set | yes |  | The Home's parts (Table 56c), in pixels from the Home's top left corner. The schema asks for no entry. |

### 10.9 The Part Set

A part set holds up to five arrays. A part carries geometry (`x`, `y`, `w`, `h`) and content only: it takes no colour, class or style. The library
draws the palette and fonts, and an input that carries one is refused by the schema and by rule `assembly-style` of Table 56i. The one `style` a part may
carry is the word of a label or of a line.

Table 56c. The keys of a part set (`$defs/partSet`; no other key is allowed).

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `labels` | array of label object | no |  | Text (Table 56d). |
| `symbols` | array of symbol object | no |  | A readout, an indicator or an instrument field bound to a member (Table 56e). |
| `lines` | array of line object | no |  | Straight segments (Table 56f). |
| `buttons` | array of button object | no |  | Pulse buttons (Table 56g); in `home` only. |
| `shapes` | array of shape object | no |  | Static outlines (Table 56h). |

Table 56d. The keys of a label of a part set.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z][A-Za-z0-9_]*$` | The part's name; unique within the assembly's `parts` and `home` together. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `text` | string | yes |  | The text. |
| `align` | string | no | values `left`, `center`, `right`; default `left` | Horizontal alignment. |
| `style` | string | no | values `heading`, `body`, `label`; default `label` | The library's text style. |

Table 56e. The keys of a symbol of a part set.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z][A-Za-z0-9_]*$` | The part's name; unique as above. |
| `kind` | string | yes | values `readout`, `indicator`, `instrument-field` | The library view that draws it: `Automation/Readout`, `Automation/Indicator` or `Instrument/Field`. |
| `x` | number | yes |  | Left edge of the part's box, used as given (the generator does not grow it). |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `member` | string | yes | pattern `^[A-Za-z0-9_][^{}\[\]]*$`; no empty, `.` or `..` segment | The member of the assembly's device that the part reads, relative to `device`. A readout and an instrument field bind it to `value`, an indicator to `state`. |
| `unit` | string | no |  | The engineering unit shown (a parameter of the library view). |
| `format` | string | no |  | A number format, as a readout takes (a parameter of the library view). |
| `label` | string | no |  | The caption (a parameter of the library view). |

Table 56f. The keys of a line of a part set.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z][A-Za-z0-9_]*$` | The part's name; unique as above. |
| `points` | array of [x, y] pairs | yes | at least items 2; each pair has exactly 2 numbers | The vertices, joined by straight segments, in pixels of the view. |
| `style` | string | no | values `solid`, `dashed`; default `solid` | The stroke. A line of a part set has no `width` and no `gate`. |

Table 56g. The keys of a button of a part set.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z][A-Za-z0-9_]*$` | The part's name; unique as above. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `label` | string | yes | at least chars 1 | The caption. |
| `member` | string | yes | pattern `^[A-Za-z0-9_][^{}\[\]]*$`; no empty, `.` or `..` segment | The Boolean member of the device that the button pulses (true for 1,000 ms, with the Confirm and Cancel question, write path W18, role `Administrator`). |

Table 56h. The keys of a shape of a part set.

| Key | Type | Required | Constraint | Meaning |
|---|---|---|---|---|
| `id` | string | yes | pattern `^[A-Za-z][A-Za-z0-9_]*$` | The part's name; unique as above. |
| `x` | number | yes |  | Left edge. |
| `y` | number | yes |  | Top edge. |
| `w` | number | yes | minimum 1 | Width. |
| `h` | number | yes | minimum 1 | Height. |
| `form` | string | yes | values `rect`, `ellipse`, `polyline`, `polygon` | The outline: a rectangle or an ellipse in the box, or a polyline or polygon through `points`. It is drawn in the library's neutral stroke with no fill. |
| `points` | array of [x, y] pairs | no | at least items 2; each pair has exactly 2 numbers | The vertices, in pixels from the shape's top left corner. Required for `polyline` and `polygon`, refused for `rect` and `ellipse`. |

### 10.10 The Rules of a Local Assembly

The rules that gate G0 checks beyond the schema have one name each (`assembly.RULES`). `screen.py` prints them in this order, all the errors
of a rule before those of the next, and the report file holds them as `gates.G0.errors[]` (section 2.4).

Table 56i. The assembly rules of gate G0, in the order they are listed.

| Order | Rule | Refused when |
|---|---|---|
| 1 | `assembly-kind-not-local` | `--local-kinds` is given and the assembly's `kind` is not in its list |
| 2 | `assembly-kind-is-library` | the `kind` is a kind of the library profile (a key of `kinds` or of `deviceKinds`, so `local` itself is refused too): draw it with its library symbol or its wrap |
| 3 | `assembly-without-local-kinds` | the option `--local-kinds` is absent; an empty list is a given option, so every assembly then fails rule 1 instead |
| 4 | `assembly-style` | a part of `parts` or `home` carries one of `colour`, `color`, `class`, `classes`, `className`, `style`, `styles`, `fill`, `stroke`, `font`, `background`; the word `style` of a label or a line is not one (the schema checks the word) |
| 5 | `assembly-parts-differ` | two assemblies of one kind differ in `w`, `h`, `parts` or `home`, compared as canonical JSON (keys sorted); one view is written per kind, so only `id`, `device`, `title`, `label`, `x` and `y` may differ |
| 6 | `assembly-on-cards` | the page's layout is not `diagram` |
| 7 | `assembly-part-ids` | a part `id` is used twice within one assembly, `parts` and `home` and all five arrays counted together |
| 8 | `assembly-button-on-page` | `parts` holds a button: a button is allowed in `home` only, so that a press on the page never also opens the faceplate |

The component test page's own kind `benchlocal` (the assembly `TB_LOCAL`, `tools/hmi/testbench.py`) is exempt from rules 1 and 3 whatever the option holds,
and only on that page.

Rules that the schema and the generator state and G0's list does not:

1. A symbol and a button name a `member` (required). The `member`, like `device`, has no empty, `.` or `..` segment, so that it cannot leave the
   device's folder; a brace or bracket in a `member`, or a brace in a `device`, is refused.
2. The assembly's `id` is also a page part id: a repeat among the page parts, or an id that is a symbol's, is a contract error (section 10).
3. A button's pulse is one length, 1,000 ms; the tag it pulses is declared in `session.custom.commands`, so that `cadre.hmi.page_pulse` writes that tag
   and no other.
4. Gate G5 reads the generated views as it reads a page: an embedded part (a symbol) lies inside the view's `w` by `h` and overlaps no other by more than
   4 px, and the assembly's own embed lies inside the page's canvas. A label, line, button or shape is not measured.

### 10.11 The Local Kind and the Generated Views

One pair of views is written for each local kind the descriptors draw, from the first assembly of the kind (rule 5 holds the others equal):

Table 56j. What the generator writes and registers for local assemblies.

| Item | Form |
|---|---|
| `Local/<Kind>/Assembly` | A view of `w` by `h` with the input parameter `deviceId`, the tag folder of the instance. Its root is the coordinate container `Diagram`. Parts are drawn in this order, later ones above: shapes, lines, labels, symbols, buttons (`assembly.part_view`) |
| `Local/<Kind>/Home` | The same, from `home` at its own `w` and `h`; where `home` is absent, one label, No detail, in 360 by 80 px |
| The folder `Local/<Kind>` | A folder only, never a view: the two views are siblings in it, because Ignition 8.3.6 does not find a view whose folder also holds another view (page 07 GF-117) |
| Member bindings | A tag binding of `{0}/<member>`, indirect, with the reference `{0}` = `{view.params.deviceId}`; a button writes the same path through `cadre.hmi.page_pulse` |
| The embed on the page | An `ia.display.view` named by the assembly's `id` at `x`, `y`, `w`, `h`, path `Local/<Kind>/Assembly`, parameter `deviceId` = the full tag folder (`[default]cadre_hmi_localdemo/CH1`) |
| The item | Each assembly is an item of kind `local` for every device structure (`screen.descriptor_items`): its `device`, `title` (the kind as written by default), `label` (the `id` by default) and `params.localKind`, the `<Kind>` |
| The device index entry | `{folder, kind: "local", title, label, unit, local: "<Kind>"}` (`screen.device_index`); the alarm panel's row click (`cadre.hmi.select_alarm_device`) selects the device from it with its `local` kind |
| The opener | A click calls `library.open_device(folder, 'local', title, label, local='<Kind>')`, that is `cadre.hmi.select_device(session, folder, 'local', title, label, tab, local)`, which writes `session.custom.selectedLocal` (every other call clears it); the faceplate host passes it to the faceplate as the view parameter `localKind`. A floating faceplate (the ASM frames) takes `localKind` as a view parameter of its own, and its Dock pin passes it back |
| The faceplate | `Faceplate/ASM/Local` in both styles, with the tabs Home, Alarms and Info. Home embeds `Local/<localKind>/Home` with the same `deviceId`. Gate G11 expects the device by its `title` (else the kind) and, with a device model, these three tabs |
| The device kind `local` | In `library/profile.json` `deviceKinds.local`, with `openMembers` true (page 17 section 4.9): gate G7 devices accepts every member that a device model lists for a device of this kind |

A device model may name the device (`kind` `local`, any members; page 17). It need not: without an entry the tags of the device are the members the
parts name (page 17 Table 11b). A local device that a model does name takes its kind, title, label and members from the model as any device does.

### 10.12 A Worked Example of One Assembly

A page with one assembly, a chiller of a kind the library lacks: an outline, a heading, an indicator of `running` and a readout of `supplyTemp` on the
page, and on the Home an instrument field of `supplyTemp` and a Reset button. The page is 800 by 400 px, with no toolbar; the example passed gates G0 to G7 on 2026-11-06. `cooling.json`:

```json
{
 "schema": "cadre-hmi-screen/1",
 "screen": {"id": "Cooling", "route": "/cooling", "title": "Cooling", "view": "Screens/Cooling",
            "layout": "diagram", "width": 800, "height": 400, "icon": "tank", "node": "Plant/Cooling"},
 "tagRoot": "[default]cadre_hmi_localdemo",
 "tagValues": {"CH1/supplyTemp": 7.5, "CH1/running": true},
 "toolbar": false,
 "assemblies": [
  {"id": "CH1", "kind": "chiller", "device": "CH1", "title": "CH-1", "label": "Chiller 1",
   "x": 60, "y": 60, "w": 240, "h": 120,
   "parts": {
    "shapes": [{"id": "Body", "x": 0, "y": 0, "w": 240, "h": 120, "form": "rect"}],
    "labels": [{"id": "Name", "x": 12, "y": 8, "w": 140, "h": 24, "text": "Chiller 1", "style": "heading"}],
    "symbols": [{"id": "Run", "kind": "indicator", "x": 190, "y": 8, "w": 40, "h": 40, "member": "running"},
                {"id": "Supply", "kind": "readout", "x": 12, "y": 60, "w": 120, "h": 40, "member": "supplyTemp",
                 "unit": "degC", "format": "0.0"}]},
   "home": {"w": 360, "h": 160,
            "parts": {
             "labels": [{"id": "HomeName", "x": 12, "y": 8, "w": 240, "h": 24, "text": "Chiller detail", "style": "heading"}],
             "symbols": [{"id": "HomeSupply", "kind": "instrument-field", "x": 12, "y": 48, "w": 120, "h": 64,
                          "member": "supplyTemp", "unit": "degC", "format": "0.0", "label": "Supply"}],
             "buttons": [{"id": "Reset", "x": 200, "y": 64, "w": 120, "h": 32, "label": "Reset", "member": "cmdReset"}]}}}
 ]
}
```

`local-kinds.json`:

```json
["chiller"]
```

Commands, with the result of each:

```bash
python tools/hmi/parent.py --out build
python tools/hmi/screen.py --project cadre_hmi_localdemo --descriptor cooling.json --local-kinds local-kinds.json --app-name LocalDemo --out build --report report.json
```

```text
  G0_descriptor_schema   PASS
  G1_registry            PASS
  G1_registry_parent     PASS
  G2_references          PASS
  G3_view_keys           PASS
  G4_project             PASS
  G5_layout              PASS
  G6_flow                PASS
  G7_contract            PASS
  G7_faceplates          PASS
  G7_history             PASS
  G7_commands            PASS
```

There is no device model, so no G7 devices line, and no flow, so G6 proves a page with no pipe. The build writes the views `Local/Chiller/Assembly` and
`Local/Chiller/Home` beside `Screens/Cooling`, and the generated tags of the device are the folder `CH1` with `cmdReset` (Boolean, false), `running`
(Boolean, true) and `supplyTemp` (Float8, 7.5). The device index lists `[default]cadre_hmi_localdemo/CH1` with kind `local` and `local` `Chiller`.

The same page without the option fails the gate before anything is built (exit 1):

```bash
python tools/hmi/screen.py --project cadre_hmi_localdemo --descriptor cooling.json --app-name LocalDemo --out build --report report.json
```

```text
  G0_descriptor_schema   FAIL

  assembly-without-local-kinds: cooling.json: CH1: an assembly needs screen.py --local-kinds
```

The report then holds the `gates.G0.errors` entry shown in section 2.4. With a `local-kinds.json` that lacks `chiller`, the rule is
`assembly-kind-not-local`.

## 11. Module Rendering

### 11.1 What Changes per Kind

`--render module` draws the kinds of Table 57 with the Cadre HMI Components module (page 12) instead of the library views;
the descriptor does not change. The controller, the indicator and the sequence have no component and keep their library views
under either rendering (`kinds.<kind>.module` is null in the profile).

Table 57. The module component of each library kind and what changes (`screen.MODULE_KIND`, `MODULE_PARAM`, `MODULE_DROP`, `MODULE_STATE`, `MODULE_VALUE`, `MODULE_EXCEPT`, `MODULE_NEEDS`).

| Kind | Component | Parameter renamed or valued differently | Stated with the contract default when not bound | Stays on the library view when |
|---|---|---|---|---|
| `pump` | `cadre.ob.pump` | `speed` as `speedInPercent` | `hasSpeed` | never by kind |
| `motor` | `cadre.ob.motor` | `speed` as `speedInPercent` | `hasSpeed` | never by kind |
| `fan` | `cadre.ob.fan` | `speed` as `speedInPercent`; `vertical` dropped | `hasSpeed` | `vertical` true |
| `valve` | `cadre.ob.valve` | none | none | `variant` is not `regular` or `flat` |
| `analogvalve` | `cadre.ob.analogvalve` | none | none | `variant` is not `regular` or `flat` |
| `filter` | `cadre.ob.filter` | `variant` `regular` as `square`; `vertical` dropped | none | `vertical` true; `variant` not `regular` or `flat` |
| `damper` | `cadre.ob.damper` | `variant` `regular` as `square`; `vertical` dropped | none | `vertical` true; `variant` not `regular` or `flat` |
| `switch` | `cadre.ob.switch` | `variant` `regular` as `square`; `vertical` dropped | none | `vertical` true; `variant` not `regular` or `flat` |
| `generator` | `cadre.ob.generator` | `variant`, `picture`, `activated`, `progress`, the three badges and `vertical` dropped | none | `picture` `genset`; `variant` not `regular`; `activated` or `progress` true; any badge not `none` |
| `tank` | `cadre.ob.tank` | `medium`, `showPercent`, `chart`, `history`, `valueFractionDigits` dropped | `unit`, `hasCapacity` | `valueFractionDigits` is not 0 |
| `readout` | `cadre.ob.readout` | `tag` as `idTag`; `format` becomes `fractionDigits`; `hasTag` and `label` dropped | `value` | the number format is not a plain digit pattern; the box is more than 4 px shorter than the element (26 px, or 44 px with an identifier) |
| `instrument-field` | `cadre.ob.instrumentfield` | `label` as `tag`; `align` `center` as `center` true; `format` and `setpointFormat` become `fractionDigits` | `value`, and `setpoint` when `hasSetpoint` | `size` `enhanced` with `hasSetpoint`; `align` `start`; a format that is not a plain digit pattern, or a setpoint format with other digits than the value; the box is more than 4 px shorter than the element (40, 52, 60 or 72 px) |

### 11.2 When a Symbol Stays on the Library View

A symbol is drawn by the module only where its component can show it truthfully (`screen.module_draws`). It stays on the
library view when any of these holds, and the build says nothing: it is not an error.

1. It sets `render` `view`.
2. It states or binds `badgeDuty` or `outOfService` and the component's schema lacks that property (a bound mark counts as
   stated).
3. Its parameters meet a `MODULE_EXCEPT` set or miss a `MODULE_NEEDS` value of Table 57. A parameter the symbol does
   not give counts as the contract's default.
4. A readout or an instrument field whose `format` is not `#,##0`, `#,##0.0`, `0`, `0.0` and so on (`#,##` optional, then `0`,
   then an optional point and zeros): the element prints a digit count and does not group thousands (1,234 prints as 1234).
5. A readout or field whose box is more than 4 px shorter than the element's measured height.
6. A bound parameter that `MODULE_NEEDS` names and the component drops (the generator's progress ring, for example).

Gate G5 does not look at a module component's height, so a builder that wants the module's element for a readout gives the
box the element needs.

### 11.3 Parameter Renames, Drops and Generated Properties

The symbol's parameters reach the component's properties by the renames of Table 57; a parameter the component has no
property for is dropped (the status and device marks `showStatus`, `statusText`, `hasTag`, `deviceId`, `deviceKind`, `deviceLabel`,
`badgeDuty`, `outOfService`, `vertical` of a fan, and the others listed in `screen.MODULE_DROP`). Of these, `showStatus`,
`statusText`, `badgeDuty`, `outOfService` and the readout's `stretch` are passed only when the component's schema lists them
(`MODULE_IF_LISTED`), so a build is the same before and after a module release adds them. The generator adds, whatever the
descriptor says: `positioning` `symbol` for an automation symbol; the identifier in the component's `idTag` or `tag`, under the
toolbar behind the ID-tag button; `showStatus` bound to the Readout button and `statusText` set to the library row's words (On or
Off, the speed in per cent) where the component lists them; the click script that opens the faceplate; and, for a device symbol,
the alert properties bound to the page's alarm query. `render` `view` on a symbol forces the library view (the component test
page uses it for side by side pairs).

### 11.4 Module-Only Kinds

A module-only kind has a component and no library view. Its contract is derived from the component's own properties
(`screen.module_contract`): every property with a default, less `positioning`. A `symbol` class kind (the eleven electrical
symbols) also takes the device and status marks and has the geometry of an automation symbol (anchor `symbol-centre`, a 48 px
symbol box, a state `on`, the readout and identifier boxes). A `glyph` class kind carries only the properties its component
declares, a `box` anchor, no flow and no state, and its size is the component's default size.

How a descriptor symbol of such a kind passes `params` to the component: each name in `params` must be a property of the
component (or, for a `symbol` class kind, one of the marks); it is written to the component's property of the same name, with no
rename. Each name in `bind` becomes a direct tag binding of `props.<name>`, except the state `on` of a `symbol` class kind,
which is read through `custom.g_<id>` as for a library symbol. A glyph is drawn in the box `x`, `y`, `w`, `h`; a symbol class
kind is drawn as a 48 px symbol with the readout beside it. A value outside an enumeration of the component is a G1 failure (`ENUM_VIOLATION ... props.orientation is 'diagonal'; declared
domain is ['horizontal', 'verticalRight', 'verticalLeft']`), and a name the component lacks is the G7 contract error
`<id>: parameter 'bogus' is not in the Module/resistor contract` (both proved on 2026-11-05). None of the module-only kinds is a
gate in the flow graph: all pass the medium.

Table 58. The module-only kinds of a descriptor (`screen.MODULE_ONLY` less `screen.FRAME_ONLY`; `module/components.json`). Class is `symbol` for a component with the automation attribute set (`on`, `tag`, `readoutPosition`) and `glyph` for any other (`screen.module_geometry`). Parameters is the number of names a descriptor may set (the contract: the component's properties with a default, less `positioning`, and for a `symbol` class kind the seven device and status marks). The default size is the component's; a `symbol` class kind is drawn as the 48 px symbol with its readout beside it, and a `glyph` in the box the descriptor gives. The last column lists the properties that carry the meaning; `module/CATALOGUE.md` has every property, type and default.

| Kind | Component | Component default size (px) | Class | Parameters | Properties that matter |
|---|---|---|---|---|---|
| `resistor` | `cadre.ob.resistor` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `capacitor` | `cadre.ob.capacitor` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `diodes` | `cadre.ob.diodes` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `ground` | `cadre.ob.ground` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `source` | `cadre.ob.source` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `converter` | `cadre.ob.converter` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `transformer` | `cadre.ob.transformer` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `bipolar-transistor` | `cadre.ob.bipolartransistor` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `mosfet` | `cadre.ob.mosfet` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `logic` | `cadre.ob.logic` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `router` | `cadre.ob.router` | 96 by 96 | symbol | 30 | `on`, `orientation`, `variant`, `alternativeIcon` |
| `automation-badge` | `cadre.ob.automationbadge` | 32 by 32 | glyph | 3 | `mode`, `type` |
| `hydraulic-check-valve` | `cadre.ob.checkvalve` | 48 by 48 | glyph | 3 | `vertical`, `ariaLabel` |
| `valve-analog-two-way-icon` | `cadre.ob.valvetwoway` | 48 by 48 | glyph | 4 | `value`, `closed`, `vertical` |
| `valve-analog-three-way-icon` | `cadre.ob.valvethreeway` | 48 by 48 | glyph | 5 | `value`, `value2`, `closed`, `horisontal` |
| `indicator-battery` | `cadre.ob.battery` | 48 by 48 | glyph | 7 | `value`, `level`, `direction`, `variant`, `hasIcon` |
| `indicator-engine` | `cadre.ob.engine` | 48 by 48 | glyph | 3 | `value`, `direction` |
| `indicator-tank-atmospheric` | `cadre.ob.tankatmospheric` | 48 by 48 | glyph | 7 | `value`, `level`, `direction`, `variant`, `hasIcon` |
| `automation-readout` | `cadre.ob.automationreadout` | 72 by 48 | glyph | 5 | `value`, `unit`, `numberOfDigits`, `position` |
| `heat-exchanger` | `cadre.ob.heatexchanger` | 152 by 96 | glyph | 14 | `medium`, `static`, `tag`, `activated`, `alert` |
| `heat-pump` | `cadre.ob.heatpump` | 152 by 96 | glyph | 14 | `medium`, `static`, `tag`, `activated`, `alert` |
| `hydraulic-separator` | `cadre.ob.hydraulicseparator` | 152 by 96 | glyph | 14 | `medium`, `static`, `tag`, `activated`, `alert` |
| `gauge-generator` | `cadre.ob.gaugegenerator` | 240 by 280 | glyph | 31 | `value`, `minValue`, `maxValue`, `setpoint`, `state`, `priority`, `label`, `unit` |
| `gauge-motors-and-pumps` | `cadre.ob.gaugemotorspumps` | 240 by 280 | glyph | 31 | `value`, `minValue`, `maxValue`, `setpoint`, `state`, `priority`, `label`, `unit` |
| `gauge-valve` | `cadre.ob.gaugevalve` | 240 by 280 | glyph | 19 | `value`, `bottomValue`, `setpoint`, `priority`, `label`, `unit` |
| `hydraulic-valve-4-3` | `cadre.ob.hydraulicvalve43` | 144 by 48 | glyph | 5 | `type`, `selectedPosition`, `vertical` |
| `hydraulic-valve-x-2` | `cadre.ob.hydraulicvalvex2` | 96 by 48 | glyph | 5 | `type`, `selectedPosition`, `vertical` |
| `transmitter-button` | `cadre.ob.transmitterbutton` | 96 by 40 | glyph | 15 | `value`, `unit`, `label`, `fractionDigits`, `hasSetPoint`, `setpointValue` |
| `area-graph` | `cadre.ob.areagraph` | 480 by 320 | glyph | 29 | `data`, `datasets`, `labels`, `colors`, `unit`, `legend` |
| `line-graph` | `cadre.ob.linegraph` | 480 by 320 | glyph | 27 | `data`, `datasets`, `labels`, `colors`, `unit`, `legend` |
| `donut-chart` | `cadre.ob.donutchart` | 480 by 320 | glyph | 16 | `data`, `colors`, `max`, `thickness`, `legend` |
| `pie-chart` | `cadre.ob.piechart` | 480 by 320 | glyph | 12 | `data`, `colors`, `legend` |
| `polar-chart` | `cadre.ob.polarchart` | 480 by 320 | glyph | 14 | `data`, `colors`, `legend` |
| `radial-bar-chart` | `cadre.ob.radialbarchart` | 480 by 320 | glyph | 9 | `data`, `colors`, `max`, `legend` |
| `bar-horizontal` | `cadre.ob.barhorizontal` | 480 by 128 | glyph | 38 | `value`, `minValue`, `maxValue`, `state`, `setpoint`, `advices` |
| `bar-vertical` | `cadre.ob.barvertical` | 128 by 320 | glyph | 38 | `value`, `minValue`, `maxValue`, `state`, `setpoint`, `advices` |
| `circular-progress` | `cadre.ob.circularprogress` | 48 by 48 | glyph | 6 | `value`, `mode` |
| `instrument-radial` | `cadre.ob.instrumentradial` | 240 by 240 | glyph | 31 | `value`, `minValue`, `maxValue`, `setpoint`, `state`, `advices` |
| `readout-block` | `cadre.ob.readoutblock` | 144 by 64 | glyph | 21 | `value`, `valueType`, `variant`, `fractionDigits`, `enhanced` |
| `horizontal-line` | `cadre.ob.pipehorizontal` | 96 by 24 | glyph | 4 | `medium`, `lineType`, `length` |
| `vertical-line` | `cadre.ob.pipevertical` | 24 by 96 | glyph | 4 | `medium`, `lineType`, `length` |
| `corner-line` | `cadre.ob.pipecorner` | 24 by 24 | glyph | 4 | `medium`, `direction`, `lineType` |
| `three-way-line` | `cadre.ob.pipetee` | 24 by 24 | glyph | 4 | `medium`, `direction`, `lineType` |
| `line-cross` | `cadre.ob.pipecross` | 24 by 24 | glyph | 3 | `medium`, `lineType` |
| `line-overlap` | `cadre.ob.pipeoverlap` | 24 by 24 | glyph | 3 | `medium`, `lineType` |
| `end-point-line` | `cadre.ob.pipeend` | 24 by 24 | glyph | 4 | `medium`, `direction`, `lineType` |
| `direction-line` | `cadre.ob.pipedirection` | 24 by 24 | glyph | 3 | `medium`, `lineType` |
| `bus` | `cadre.ob.bus` | 200 by 24 | glyph | 6 | `label`, `size`, `variant`, `tint`, `vertical` |

The table lists 48 kinds. Under `--render stock` the build refuses a module-only kind: for each symbol the
generator reports `<id>: kind '<kind>' is module only (<component>); build it with --render module`, draws a gap box and stops
with `CONTRACT ERRORS: not deploying` (proved on 2026-11-05 for `resistor` and `bar-horizontal`). Under `--render module` it
is refused in the same way when the component cannot draw the parameters or the symbol sets `render` `view`, since no library
view exists to fall back to. The component test page shows the kinds in one section (`testbench.module_only_block`).

### 11.5 Frame-Only Kinds

The 33 kinds of `screen.FRAME_ONLY` are in `MODULE_ONLY` (81 rows in all) but are not
descriptor symbols of a page: they are the parts the frame options `ob` and `obasm` draw in their own views (page 04 sections 10
and 11). A builder does not write them. They are: `tooltip`, `toggletip`, `clock`, `user-button`, `app-button`, `notification-button`, `notification-badge-button`, `alert-button-item`, `alert-button`, `alert-menu-item`, `alert-menu`, `navigation-item`, `navigation-item-group`, `navigation-menu`, `tree-navigation-item`, `tree-navigation-group`, `tree-navigation`, `breadcrumb`, `brilliance-menu`, `user-menu`, `system-menu`, `app-menu`, `command-menu`, `top-bar`, `tab-item`, `tab-row`, `pivot-item`, `pivot-item-group`, `modal-window`, `context-menu-input`, `notification-menu-item`, `notification-message-item`, `notification-floating-item`.

## 12. The Validation Checklist

A descriptor passes gates G0 to G7 when every line below holds. The messages are those the tools print.

Table 59. The checklist by gate.

| Gate | Rule |
|---|---|
| G0 | The descriptor has `schema` equal to `cadre-hmi-screen/1` and a `screen` object; no key outside Table 7 and the `$defs` tables |
| G0 | `screen` has `id` (letter, then letters, digits, underscores), `route` (starts with `/`), `title`, `view`, `layout` (`diagram` or `cards`) |
| G0 | `screen.width` and `height` at least 1; `node` has no empty segment and at most 120 characters; `level` at most 40 characters; `previous` and `next` start with `/` |
| G0 | A symbol has `id` (letters, digits, `_`, `-`), `kind`, `x`, `y`; `w` and `h` at least 1; `bind` values are strings; `device` is a Boolean or a string |
| G0 | A pipe has `id`, `from` and `to`; each end is a reference (`ref`, optional `side` of `top`, `bottom`, `left`, `right`) or a free point (`x`, `y`, optional `end`) and nothing else; `medium`, `size` and `state` are from their enumerations; each `via` is a pair of numbers |
| G0 | A section has `id`, `x`, `y`, `w`, `h`; a junction `id`, `x`, `y`; a label `id`, `x`, `y`, `w`, `h`, `text`; a card has `id`; a group has `items`; a flex symbol has `id` and `kind` |
| G0 | A part's `id` matches `^[A-Za-z0-9_-]+$`; a pulse `ms` is an integer from 100 to 600000; a trend has one or two pens; a line has at least two points; a well mark's `level` is above 0 and not above 1; an `emphasis` has exactly one of `tag` and `symbol` |
| G0 | An assembly has `id`, `kind`, `device`, `x`, `y`, `w`, `h` and `parts` (at least one part); each part has the required keys of Tables 56d to 56h; `device` and `member` have no empty, `.` or `..` segment; a `polyline` or `polygon` shape has `points`, a `rect` or `ellipse` has none |
| G0 | The assembly rules of Table 56i hold, in the order listed: the kind is in `--local-kinds` and is no library kind, the option is given, no part carries a colour, class or style key, assemblies of a kind share `w`, `h`, `parts` and `home`, the page is a diagram, part ids are unique within an assembly, `parts` holds no button. A failure is written to `gates.G0.errors[]` before `screen.py` exits (section 2.4) |
| G0 | The device model has `schema`, `tagRoot` (`[provider]folder`, no trailing `/`) and `devices`; each device has `id`, `kind`, `members`; each member has `type` and `access`; an alarm source matches `prov:<provider>:/tag:<path>`; a pulse caption is one line of 1 to 32 characters |
| G1 | Every view of the child passes the registry: component types, declared props, enumerations, position keys, binding keys. Under `--render module` a module-only kind's `params` must be properties of the component with values from its enumerations |
| G2 | Every embedded view path, style class and `var()` token resolves in the child or the parent (generated from the library; a descriptor cannot cause a failure) |
| G3 | View-level keys are `custom.` or `params.` (generated; a builder cannot cause this) |
| G3 | An expression of a view names `{view.custom.<name>}` only for a key the view's `custom` defines; otherwise `<view>: an expression names view.custom.<name>, which the view does not define`. A descriptor reaches it only through a gated symbol (for example a switch) that neither binds nor states its state parameter: the flow graph passes such a symbol as a junction (section 9.2), so no pipe expression names it, and the descriptor is accepted |
| G4 | The parent exists in `--out` and is inheritable and is the child's parent; every route names an existing view; every navigation item names an existing route |
| G5 | Every embed box lies inside `0, 0, screen.width, screen.height` (`<name> outside the canvas`) |
| G5 | No two symbol boxes share more than 4 px on both axes (`symbol <a> overlaps <b>`) |
| G5 | The same two checks in the views `Local/<Kind>/Assembly` and `Local/<Kind>/Home`: a symbol part lies inside the view (`Local/<Kind>/Assembly: <id> outside the canvas`) and overlaps no other by more than 4 px; labels, lines, buttons and shapes are not measured |
| G5 | Warnings, not failures: overlapping embeds; a block in a box smaller than its flags need; an identifier or an instrument field caption wider than its embed |
| G6 | The compiled flow expression of every pipe equals the reference solver (exhaustive to 12 gates, a seeded sample of 4,096 above) |
| G7 contract | Every symbol's kind resolves to a view, or is drawn as a counted gap (the build still passes) |
| G7 contract | Every name in `params` and `bind` is in the kind's contract (`<id>: parameter '<name>' is not in the <view> contract`); `bind.state` is allowed on an indicator |
| G7 contract | A device symbol binds the faceplate member of its kind inside its own folder (`'<param>' is bound to '<member>'; the faceplate reads '<folder>/<member>'`) |
| G7 contract | A static tank states no `hasCapacity` true without `max` |
| G7 contract | A module-only kind is built with `--render module` and its parameters are those of its component |
| G7 contract | Page parts only on a diagram; part ids unique and not a symbol's; `alarm` only on an indicator; `bar` only on a readout or an instrument field, with a `value`; a `bar` value or well mark is a string; a gate or emphasis names a symbol that is on the page and has a state; a link icon exists; well marks rise; a pulse tag has one length; a faceplate button names a device the set marks `device`; `render: module` only on a pulse button |
| G7 contract | `flow`: fewer than 20,000 source to sink paths |
| G7 faceplates, history, commands | The generated views carry each faceplate's tab row, one pane per tab, the alarm list narrowed by the device's source; every tag history binding references an array; no script writes a tag directly; every control that calls a checked write binds `enabled` to its permission. A builder cannot cause these with a descriptor; they fail only if the library code is changed |
| G7 devices | With `--devices-file`: no device listed twice; each `kind` has a faceplate; each member is a name the kind knows (page 17) in a suitable type; each `write` member has a write path; each `trend` member is a member; a force is one whole encoding; an alarm source names a tag; a pulse member is a Boolean `write` pulse member of the kind, and its caption is valid; a pulse member of the kind that is `write` is marked `pulse` |
| G7 devices | A device of kind `local` (the device of an assembly; `openMembers` in the profile) may list any member: its names, types and write paths are not checked, while a pulse member (Boolean, `write`, a caption of 1 to 32 characters) and a `cfg/` row are checked as for any kind; stating `faceplate` `asm` on it draws the warning that its asm faceplate is its stock one |
| G7 devices | Every symbol marked `device` or `faceplate` names a device of the model; its kind opens the faceplate of the device's kind (state the `deviceKind` where it differs); each faceplate parameter it binds is a listed member; `hasSetpoint`, `hasOutput` and `hasStep` true need `sp`, `out` and `step` |
| G7 devices | With `--tags-file`: each device folder exists; each listed member exists in the declared type; no `write` member is an expression tag; the folder carries no faceplate member the model leaves out |
| G7 tag model | With `--tags-file`: interlocks of every `ilk` folder, every trip latched, and every `cadre` name in the tag model's scripts resolve (page 17) |

## 13. Two Worked Examples

Each example passed gates G0 to G7 on 2026-11-05. The files are in the working folder; the tool is run by its path from the
repository root. The parent is built first, into the same `--out` folder (section 2.1).

### 13.1 A Diagram Page with a Device Model

A tank, a valve, a pump and a readout, each a device, with one pipe from the tank to a free end that is a sink, so that the pipe
carries the medium. The page is 800 by 400 px. `intake.json`:

```json
{
 "schema": "cadre-hmi-screen/1",
 "screen": {"id": "Intake", "route": "/intake", "title": "Intake", "view": "Screens/Intake",
            "layout": "diagram", "width": 800, "height": 400, "icon": "tank", "node": "Plant/Intake"},
 "tagRoot": "[default]cadre_hmi_example",
 "showTags": true,
 "tagValues": {"T1/level": 620, "V1/state": true, "P1/state": true, "P1/speed": 74, "FT1/value": 38.5},
 "symbols": [
  {"id": "T1", "kind": "tank", "x": 40, "y": 80, "w": 168, "h": 216, "device": true, "label": "Raw water tank",
   "params": {"tag": "TK-1", "max": 1000, "unit": "m³"}, "bind": {"value": "T1/level"}},
  {"id": "V1", "kind": "valve", "x": 320, "y": 40, "w": 48, "h": 48, "device": true, "label": "Inlet valve",
   "params": {"tag": "XV-1", "hasTag": true, "readoutPosition": "bottom"}, "bind": {"open": "V1/state"}},
  {"id": "P1", "kind": "pump", "x": 480, "y": 40, "w": 48, "h": 48, "device": true, "label": "Feed pump",
   "params": {"tag": "P-1", "hasTag": true, "hasSpeed": true, "readoutPosition": "bottom"},
   "bind": {"on": "P1/state", "speed": "P1/speed"}},
  {"id": "FT1", "kind": "readout", "x": 480, "y": 200, "w": 96, "h": 40, "device": true, "label": "Feed flow",
   "params": {"tag": "FT-1", "hasTag": true, "unit": "m³/h", "format": "0.0"}, "bind": {"value": "FT1/value"}}
 ],
 "pipes": [
  {"id": "p1", "from": {"ref": "T1", "side": "right"}, "to": {"x": 360, "y": 188, "end": "arrow-out"},
   "medium": "fresh-water", "size": "medium"}
 ]
}
```

`devices.json`:

```json
{
 "schema": "cadre-hmi-devices/1",
 "tagRoot": "[default]cadre_hmi_example",
 "devices": [
  {"id": "T1", "kind": "tank", "title": "TK-1", "label": "Raw water tank", "unit": "m³",
   "members": {"level": {"type": "Float8", "access": "read"}}},
  {"id": "V1", "kind": "valve", "title": "XV-1", "label": "Inlet valve",
   "members": {"state": {"type": "Boolean", "access": "read"}, "cmd": {"type": "Boolean", "access": "write"}}},
  {"id": "P1", "kind": "pump", "title": "P-1", "label": "Feed pump",
   "members": {"state": {"type": "Boolean", "access": "read"}, "cmd": {"type": "Boolean", "access": "write"},
               "speed": {"type": "Float8", "access": "read"}}},
  {"id": "FT1", "kind": "instrument", "title": "FT-1", "label": "Feed flow", "unit": "m³/h",
   "members": {"value": {"type": "Float8", "access": "read"}}}
 ]
}
```

Commands, with the result of each:

```bash
python tools/hmi/parent.py --out build
python tools/hmi/screen.py --project cadre_hmi_example --descriptor intake.json --devices-file devices.json --app-name Example --out build --report report.json
```

```text
  G0_descriptor_schema   PASS
  G0_devices_schema      PASS
  G1_registry            PASS
  G1_registry_parent     PASS
  G2_references          PASS
  G3_view_keys           PASS
  G4_project             PASS
  G5_layout              PASS
  G6_flow                PASS
  G7_contract            PASS
  G7_faceplates          PASS
  G7_history             PASS
  G7_commands            PASS
  G7_devices             PASS  4 devices, 4 device symbols
```

The report shows no gap, no warning and no note; the pipe `p1` compiles to `true` (a tank to a sink with no gate on the path)
and the flow check ran 4 vectors on 2 gates. The tank's `bind.value` is `T1/level` and the device model lists `level`; the
valve and the pump bind their state to `V1/state` and `P1/state`, the member `state` that the rule of Table 13 names; the
pump's speed is `P1/speed`; the readout's value is `FT1/value`, and its device kind `instrument` opens the instrument faceplate
that a `readout` symbol opens. The same descriptor and model passed with `--render module` (the build was made into a second
output folder with its own parent):

```bash
python tools/hmi/screen.py --project cadre_hmi_example --descriptor intake.json --devices-file devices.json --app-name Example --render module --out build --report report.json
```

with the same fourteen lines, all PASS.

### 13.2 A Cards Page

Two cards in one row: a card with a flex body (a label and two instrument fields side by side) and a card of items (one pump
at a pixel position). `overview.json`:

```json
{
 "schema": "cadre-hmi-screen/1",
 "screen": {"id": "Overview", "route": "/", "title": "Overview", "view": "Screens/Overview",
            "layout": "cards", "width": 1600, "height": 852, "icon": "dashboard", "node": "Plant"},
 "tagRoot": "[default]cadre_hmi_cards",
 "tagValues": {"F1/value": 38.5, "F2/value": 7.2, "P1/state": true, "P1/speed": 74},
 "rows": [[
  {"id": "Flows", "title": "Flows",
   "body": {"direction": "column", "items": [
    {"label": "Feed and return"},
    {"direction": "row", "basis": "64px", "items": [
     {"id": "F1", "kind": "instrument-field", "basis": "0px", "grow": 1,
      "params": {"label": "Feed", "unit": "m³/h", "format": "0.0", "size": "enhanced", "align": "center", "tag": "FT-1"},
      "bind": {"value": "F1/value"}},
     {"id": "F2", "kind": "instrument-field", "basis": "0px", "grow": 1,
      "params": {"label": "Return", "unit": "m³/h", "format": "0.0", "size": "enhanced", "align": "center", "tag": "FT-2"},
      "bind": {"value": "F2/value"}}]}]}},
  {"id": "Pumps", "title": "Pumps", "bodyWidth": 480, "bodyHeight": 140, "items": [
   {"id": "P1", "kind": "pump", "x": 40, "y": 20, "w": 48, "h": 48,
    "params": {"tag": "P-1", "hasTag": true, "hasSpeed": true, "readoutPosition": "bottom"},
    "bind": {"on": "P1/state", "speed": "P1/speed"}}]}
 ]]
}
```

```bash
python tools/hmi/parent.py --out build
python tools/hmi/screen.py --project cadre_hmi_cards --descriptor overview.json --app-name Cards --out build --report report.json
```

```text
  G0_descriptor_schema   PASS
  G1_registry            PASS
  G1_registry_parent     PASS
  G2_references          PASS
  G3_view_keys           PASS
  G4_project             PASS
  G5_layout              PASS
  G6_flow                PASS
  G7_contract            PASS
  G7_faceplates          PASS
  G7_history             PASS
  G7_commands            PASS
```

There is no device model, so no G7 devices line. The row's height is 196 px (section 8.3). The fields bind `F1/value` and
`F2/value`, which a generated build creates as Float8 memory tags with the values of `tagValues`.

## 14. Limits and Open Items

1. The gates are offline. Nothing in this page has been rendered on the gateway for the two examples; gates G8 to G11 (render,
   live flow, operator walk, faceplate sweep) prove the rest and are not covered by a descriptor check (page 08 section 5).
2. A gate checks parameter names, not values. A value outside an enumeration passes G0 to G7 for a library kind (section 5.3);
   write the values of section 6 only.
3. Three keys that the schema leaves optional are required by the code (section 3.3): `screen.width` and `height` on a diagram,
   `w` and `h` on every diagram symbol, and `bodyWidth` with `bodyHeight` on a card with no `body`. Each fails with a
   `KeyError`, not a gate message, and a builder should write them always.
4. A module-only kind has no library view, so the build under `--render stock` is refused. A builder that must support both
   renderings draws that content with a library kind or a label.
5. Routes are not checked for being distinct, and the targets of section, card, link and button routes are not checked against
   the routes of the set.
6. The filter's contract names a gate state (`flow` `gated`, gate `on` in `library/contracts.json`), but the flow graph and the
   profile treat the filter as a pass-through node (`diagram.GATED` does not list it). A builder that needs a filter to block
   flow gives the same condition to a valve.
7. The static tank without a capacity: pages 06 section 4.2 and 08 section 4 item 7 say it stays on the library view under
   `--render module`. The code and the profile (`moduleExcept` empty for the tank, `hasCapacity` carried by the component since
   module 0.3.0) draw it with the module's tank and `hasCapacity` false.
8. `unmapped` and `screen.id` are read by no generator code; they are for the importer and for `tools/hmi/page_checks.py`.
9. The `readoutExtent` entries of `library/contracts.json` (for example `right` `[64, 48]`) are the readout box's width and
   height, not the reach of `screen.READOUT_EXTENT` (`right` `(64, 0)`); the embed boxes of Table 31 are the ones to use.
10. `tools/hmi/parent.py` rewrites `library/profile.json` in the repository on every run, whatever `--out` says. The content is
    identical when the sources are unchanged.
11. Property tables of the 97 module components are not repeated; `module/CATALOGUE.md` holds them.
12. A local assembly is not part of the flow graph and its parts are not measured by gate G5 except the symbols (section 10.10). A label, line, button or
    shape placed outside its view passes G0 to G7 and is clipped on the glass; check the box of every part against the assembly's `w` and `h`.
13. One view is written for each local kind, from its first assembly; a second assembly that differs fails `assembly-parts-differ`. An instance that needs
    a different part set is a different kind.

## 15. References

1. `schemas/screen-descriptor.schema.json` and `schemas/devices.schema.json`, the schemas gate G0 enforces.
2. `tools/hmi/screen.py` (`KIND_VIEW`, `MODULE_KIND`, `MODULE_ONLY`, `FRAME_ONLY`, `MODULE_EXCEPT`, `MODULE_NEEDS`,
   `MODULE_STATE`, `MODULE_VALUE`, `MODULE_PARAM`, `MODULE_DROP`, `READOUT_EXTENT`, `OVERLAP`, `symbol_box`, `grown_box`,
   `embed_limits`, `row_height`, `bind_rule`, `tag_path`, `main`), `tools/hmi/gates.py`, `tools/hmi/parts.py`,
   `tools/hmi/diagram.py`, `tools/hmi/navigation.py`, `tools/hmi/library.py`, `tools/hmi/assembly.py` (`RULES`, `part_view`, `kind_views`, `item`).
3. `library/contracts.json` and `library/profile.json`, generated by `tools/hmi/parent.py`.
4. `module/components.json` and `module/CATALOGUE.md`.
5. Page 04 sections 7, 8.8, 10 and 11; page 05 section 5; page 06 sections 2 to 5; page 08; page 12 sections 14 to 17; page 13
   sections 12.7 and 13.5; page 16; page 17.
6. Examples: `screens/sample-pump-station.json`, `screens/wtp/`, `tests/fixtures/pilot-supply.json`,
   `tools/hmi/bench_descriptor.py`, `tools/hmi/testbench.py`, `tools/hmi/showcase.py`.
