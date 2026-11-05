---
title: Library configuration
type: wiki
updated: 2026-11-05
---
# 14 Library Configuration

| Field | Value |
|---|---|
| Document ID | COB-WIKI-14 |
| Revision | B |
| Status | Issued for use |
| Built | Cloud sessions of 2026-11-02 and 2026-11-03 (spike T0, tranches T1 and T2), branch `spike/t0` at `4cdda21`; revision B of 2026-11-05 brings it to module 0.8.0 (`c595afa`) |
| Code | `cloud/setup.sh`, `module/tools/` (`gen_module_assets.py`, `gen_catalogue.py`, `build_module.py`, `install_module.py`, `restart_gateway.py`), `tools/hmi/` (`screen.py`, `parent.py`, `navigation.py`, `obframe.py`, `obasm.py`), `tools/compare/` (the gates) |
| Companions | `CONFIGURATION.md` (the operational reference, with every command), `module/CATALOGUE.md` (every component, generated), page 07 (GF-99 to GF-114), page 15 (the showcase project), page 16 (the selection criteria), page 17 (the tag model and the UDT of each device kind), page 18 (the view builder reference) |

## 1. Purpose

This page records, as a chapter of the wiki, every configuration that the Cadre HMI Components library needs to be built, installed, deployed
and tested: the cloud environment, the Ignition gateway, the module, the build and deploy options, the four frames, the gates, the owner's
decisions and the known limits. `CONFIGURATION.md` at the repository root is the same material as a reference to keep beside the code, with
the commands in full; this page gives the reasons and points to the pages that hold each design. The components themselves are not listed here:
`module/CATALOGUE.md` holds, for each of the 97 components, its package element, kind, default size, properties, events and what is not carried,
and a test (`tests/test_catalogue.py`) holds it equal to its generator.

The design-time references are pages 16 to 18: the selection criteria (which rendering, frame, faceplate style, layout and kind to choose for a
plant object), the tag model with one UDT for each device kind, and the complete JSON reference of the screen descriptor and device model for an
automatic view builder.

No secret appears in the repository. This page names the files that hold them (section 3.8) and never their contents.

## 2. The Cloud Environment

### 2.1 The Setup Script

`cloud/setup.sh` has three modes, each idempotent.

Table 1. The modes of `cloud/setup.sh`.

| Mode | Effect | Time |
|---|---|---|
| `environment` | JDK 17, Playwright 1.63.0 and Pillow, the Docker daemon, the Ignition image, `npm ci`, the Gradle cache, `env.sh` | 0.3 s warm, about 5 min cold |
| `gateway` | Creates and commissions the gateway; writes the API token and the test user; creates the history provider; checks that the token answers 200. Stops unless the owner's `ACCEPT_IGNITION_EULA` is `Y` | 48 s from nothing |
| `trust-module` | Trusts an unsigned module at the commissioning step and restarts the container | one restart |

The licence acceptance is the owner's: the variable is set on the cloud environment, passed to the container by name, and never set or
accepted by a session (`CLAUDE.md` section 3).

### 2.2 Variables

Table 2. The variables. Each keeps the source repository's Windows default when absent, so the source behaves as before.

| Variable | Cloud value or role |
|---|---|
| `ACCEPT_IGNITION_EULA` | `Y`, the owner's |
| `CTIG_SRC` | `cloud/vendor`, ctig's REST client (copied unchanged from ctig `046a3a5`) |
| `CTIG_IGNITION_TOKEN_FILE` | `/root/.cadre/ignition-token` |
| `CADRE_IGNITION_GATEWAY_URL` | `http://localhost:8088` |
| `CADRE_TEST_LOGIN` | `/root/.cadre/test-login.properties` |
| `CADRE_PIL_PYTHON` | the Python that has Pillow |
| `CADRE_IGNITION_WIKI` | `cloud/vendor/ignition-wiki`, the validator and schemas (Ignition-Wiki `62939dc`); read by `tools/hmi/gates.py` (G1) and `tests/test_hmi.py` |
| `CADRE_JDK17` | the JDK 17 home that `build_module.py` uses |
| `CHROME_PATH` | kept; the tools launch Playwright's own Chromium and do not read it |
| `CADRE_HOME`, `CADRE_GW_CONTAINER`, `CADRE_GW_VOLUME`, `CADRE_GW_PORT` | optional, for `setup.sh`: the folder of secrets, the container, the volume and the published port (defaults `/root/.cadre`, `cadre-gw`, `cadre-gw-data`, `8088`); a second set builds a throwaway gateway beside the first |
| `CADRE_IGNITION_DATA` | optional, the gateway data folder for `install_module.py --list` |

### 2.3 Tools and Pins

Playwright for Python is pinned to 1.63.0: the image's Chromium is build 1243, and the newest release (1.64.1) expects build 1248 and cannot
launch (34 errors in the first offline run, one cause). JDK 17.0.20.1 comes from the Ubuntu packages beside the image's JDK 21. Gradle is 8.2.1
by the wrapper, with one online build to fill the cache and offline builds after it. Node 22.23.4 installs the pinned component package only by
`npm ci`; the version in `module/web/package.json` never changes (`CLAUDE.md` rule 2).

### 2.4 The Docker Daemon

No daemon runs at session start. `setup.sh` starts one in its own session (`setsid nohup`), because a plain background daemon stopped with the
session's worker process. It uses overlayfs, cgroup v1 and the bridge network, and a restart of a stopped daemon takes 9 s with the container,
volume and module intact. Whether the image and volume survive into a later session depends on the cloud environment's caching and was not tested.

### 2.5 Offline Tests

`env -u CADRE_TEST_LOGIN python -m unittest discover -s tests` is the full offline suite: one test assumes the variable is absent. Recorded:
1081 (T0 baseline), 1102 (end of T0), 1191 (end of T1), 1299 (end of T2), 1304 with the catalogue tests, 1318 at delivery, 1321 with the pipe
components and 1333 with the showcase (2026-11-04).

## 3. The Gateway

### 3.1 Image, Container and Commissioning

The gateway is `inductiveautomation/ignition:8.3.6` in trial mode, named `cadre-cloud`, with 2048 MB of heap, edition `standard`, time zone
`Australia/Sydney`, the data folder on the Docker volume `cadre-gw-data` and port 8088 published. The 8.3 image commissions itself from
`ACCEPT_IGNITION_EULA`, `GATEWAY_ADMIN_USERNAME`, `GATEWAY_ADMIN_PASSWORD` and `IGNITION_EDITION` (GF-99). The gateway is throwaway and
unrelated to the owner's local gateway, which no cloud session reaches.

### 3.2 Unsigned Modules

The module is built unsigned in the cloud. The JVM property `ignition.allowunsignedmodules=true`, given as a `-D` argument after `--`, allows
it (GF-100).

### 3.3 The API Token

The token is a configuration resource `api-token/cadre` of type `basic-token` whose `tokenHash` is the SHA-256 of the raw key in URL-safe Base64;
the request header is `X-Ignition-API-Token: <name>:<key>` (GF-101). The gateway ignores a grant of `Authenticated/Roles` to such a token, so a
custom security level `CadreApi` is added to the gateway's read and write permissions and granted to the token (GF-102). Every write path still
needs the `Administrator` role of the user (COBD-024).

### 3.4 The Test User

`cadre_test` is added to the internal user source `default` with the `Administrator` role, in the gateway's stored password form (GF-103), and
signs in through each project's identity provider `default` (GF-44). It is the user of G10 and the walk. Without it they prove the refusal only.

### 3.5 The History Provider

The sample tag models name `Sample_SQLite_Database` (GF-53). `setup.sh gateway` creates an SQLite connection and an SQL historian of that name
through the REST resource routes, without a restart (GF-104). Without it no trend draws.

### 3.6 The Trust Step and Restarts

A first install of an unsigned module stops the gateway at a commissioning step after its restart; `trust-module` posts the commissioning
page's own call and restarts the container (GF-105). A module whose licence page changed (0.8.0 changed `license.html`) also lists its licence at
that step, and `trust-module` accepts the module's own licence page when the step lists one (`CONFIGURATION.md` section 2.7). An upgrade of a module already trusted needs no step (GF-106). Restarts take 15 to 28 s
after a module upgrade, 24 s for a container from cold and 1 min 41 s for `setup.sh gateway` after a daemon restart (GF-107).

### 3.7 The Trial

The trial lasts two hours and resets only after expiry (GF-03, GF-33). The tools reset it (`deploy.ensure_trial`) and probe a fresh session before
each gate (`walk.settle_trial`). In the cloud, recreating the container is the simpler reset.

### 3.8 Where Each Secret Is Kept

Table 3. Secrets, all under `/root/.cadre/` (mode 700, outside the repository, never printed in full).

| File | Holds |
|---|---|
| `admin-password` and `gateway.env` | the admin user's generated password, for the container's environment |
| `ignition-token` | the API token string |
| `test-login.properties` | the test user's name and password |

## 4. The Module

### 4.1 Identity and Content

Cadre HMI Components, id `cadre.hmi.ob`, version 0.8.0, for Ignition 8.3.0 and later, free, depending on Perspective. It registers 97 components on the
pinned web components 2.0.0-next.155 (Apache-2.0, commit `2c98dda1`, attribution in `NOTICE`).

Table 4. The 97 components by class (`module/CATALOGUE.md`).

| Class | Components |
|---|---|
| Device and instrument components mapped to library kinds (pump, tank, motor, fan, valve, analogue valve, filter, damper, switch, generator, readout, instrument field) and the automation button | 13 |
| Module-only kinds: electrical symbols (11) and valve, indicator, tank, gauge and hydraulic glyphs (17) | 28 |
| Charts (6) and building blocks (5) | 11 |
| Frame components (the 33 of the pinned release) | 33 |
| Pipe components (nine, display only) | 9 |
| Alarm lists (2) and the canvas zoom | 3 |

### 4.2 Generated Files

The generator `module/tools/gen_module_assets.py` writes the script `cadre-ob.js` (2,779,218 bytes at 0.8.0), the stylesheet (238,012), the font
(625,312), `components.json` and the 97 property schemas and 94 event schemas. `gen_catalogue.py` writes `module/CATALOGUE.md`. `parent.py`
writes `library/contracts.json` and `library/profile.json`. None is hand edited (`CLAUDE.md` rule 4). The unsigned module file is 996,287 bytes
at 0.8.0 (988,279 at 0.7.0), built as `CadreHMIComponents.unsigned.modl` and kept with its checksum in `cloud/release/`.

### 4.3 Build, Install and Restart

`npm ci && npm run build` in `module/web`, then `gen_module_assets.py` and `gen_catalogue.py`, then `build_module.py` (JDK 17, offline, unsigned),
`install_module.py --file module/build/CadreHMIComponents.unsigned.modl`, `restart_gateway.py --confirm --wait 300`, and `setup.sh trust-module` after
a first install. The log line "Registered N Cadre HMI Components components" must show 97. The commands in full are in `CONFIGURATION.md` section 3.3.

## 5. Building and Deploying

### 5.1 The Parent and the Child Options

`parent.py` builds `cadre_hmi_base`, which carries the views of all four frames (73 views at 0.7.0); `--name` builds a second parent beside it.
`screen.py` builds a child. The options that decide what is drawn are `--render {stock,module}`, `--frame {openbridge,asm,ob,obasm}`,
`--faceplate {openbridge,asm}` and `--faceplate-mode {dock,popup}`; the rest are the descriptors, the tag and device models, the alarm scope, the
report and `--deploy` (full table in `CONFIGURATION.md` section 4.2).

Table 5. What each combination requires or refuses.

| Combination | Result |
|---|---|
| `--frame ob` or `obasm` with `--render stock` | Refused: the command line stops with a message, `build_child` raises `ValueError` |
| A module-only kind or frame component with `--render stock` | Refused with one error for each symbol (G7 contract) |
| `--frame asm` or `obasm` with a `previous` or `next` that names no route | Refused with the route named |
| `--component-test` with descriptors of two tag roots | Refused |
| `--tag-root`, `--write-descriptor` or `--write-devices` without `--component-test` | Refused |
| No `--descriptor` without `--component-test` and `--tag-root` | Refused |
| `--deploy` after a failed gate or contract | Not reached |

### 5.2 The Component Test Page and the Samples

`--component-test` adds the page `/component-test`, generated from the catalogue, with test devices on memory tags; under `--render module` it
gains the sections "Module only" and "Frame components" from `module/components.json` (wiki 13 sections 13 and 13.9). The samples are the water
treatment plant built four ways (`cadre_hmi_wtp` stock, `cadre_hmi_wtpob` module, `cadre_hmi_wtpobf` module with `--frame ob`, `cadre_hmi_wtpoba`
module with `--frame obasm --faceplate asm`), the pump station sample, and the component test page alone (`cadre_hmi_ctest`: 19 devices, 21 device
symbols). Deploy the parent before the children and verify in a new session (GF-10).

## 6. The Four Frames

Table 6. The frames (heights measured).

| Frame | Top dock | Drawn by | Described in |
|---|---|---|---|
| `openbridge` (default; the stock frame) | 48 px | Stock components; the module's alert panel for the alert menu under `--render module` | 04 sections 2 to 7 |
| `asm` (the stock ASM frame) | 84 px (bar 48, header 36), left dock with two states, bottom banner 76 px | Stock components | 04 section 8 |
| `ob` (the module frame) | 84 px: `cadre.ob.topbar` (48) and the Cadre strip (36); left dock `cadre.ob.navigationmenu` | The module's top bar, navigation menu, alert menu, user and brilliance menus | 04 section 10 |
| `obasm` (the module ASM frame) | 132 px: top bar 48, strip 36, header 48 (pivot group and tab row); left dock tree navigation or navigation menu; bottom banner 76 px | The same components, plus the pivot group, tab row and tree navigation | 04 section 11 |

What stays a Cadre view in `ob` and `obasm` (owner's answers 2 to 4): the crumb with its node badges, the alert message and its ACK, the ASM search
field, the alarm banner, the floating faceplate, the crumb popup, the page header's title and step buttons, the alerts page and the faceplate dock.
The silence control is hidden. The ASM rules are in the data and the scripts, not in the package's code (`CLAUDE.md` rule 7).

### 6.1 Frame Names

Table 6a. The names used in prose and the option values they stand for. Prose in the library, the module and the wiki uses the names in the
first column; the option values are the code literals of `--frame` and of the faceplate style.

| Name in prose | Option value | Meaning |
|---|---|---|
| The stock frame | `openbridge` | The default frame, drawn by stock Perspective components (the default `--faceplate` style carries the same value) |
| The stock ASM frame | `asm` | The ASM frame, drawn by stock Perspective components |
| The module frame | `ob` | The frame drawn by the module components (`cadre.ob.*`) |
| The module ASM frame | `obasm` | The ASM frame drawn by the module components |

## 7. The Gates

### 7.1 The Twelve Gates

G0 to G7 run offline inside `screen.py` (descriptor, registry, references, view keys, project, layout, flow, contract). G8 render
(`capture.py`), G9 live flow (`live_flow.py`), G10 functional walk (`functional.py`, `walk.py`) and G11 faceplate sweep (`faceplates.py`) run
against the gateway with Playwright. `wtp_suite.py` runs G8, G11, G10 and the generated walk for each named project and restores the plant between
them. Page 08 section 5 holds the table and `CONFIGURATION.md` section 6.2 the commands. The sweep of an ASM project is run with `--faceplate asm`.

### 7.2 The Glass Variants

The older frames keep their selectors. `glass.frame_variant` tells `ob` and `obasm` from the older frames by the structure of the top dock, and the
helpers (bell, bar buttons, alert rows, sign in, navigation entries, palette, page name, head rectangle) choose a variant. Page 13 section 13.11 holds
the table. The ASM gates `search`, `zoom` and `panels` are skipped on `ob` with the reason recorded.

### 7.3 The Settle Waits Added in the Cloud

Table 7. The waits.

| Wait | Rule |
|---|---|
| `capture.settle_badges` | G8 waits, 1 s at a time and at most 60 s, for loading view badges to clear (GF-108) |
| `faceplates.settled_points` | G11 measures the leaves until the count holds still, up to 30 times at 1 s |
| `glass.frame_variant` | waits about 4 s once for the module's elements before taking a dock for an older frame (GF-110) |
| `walk.settle_trial` | probes a fresh session until the project shows (existing) |

### 7.4 Results to Date

The suite on module 0.6.0, both renderings: SUITE PASS (stock and module: G8 6 of 6, G11 44 of 44, G10 17 of 17 and 21 of 21, the walk passing in every
group, plant restored). G11 on the component test page at 0.6.0: 21 of 21 devices, 831 leaves, one finding (section 9 item 2). The final run on 0.7.0 over the
four samples: three PASS in every gate and the fourth in every gate but walk row A-02, an intermittent defect of the glass then fixed and proved by
three full walks in a row; G11 on the component test page on a fresh run: 21 of 21 devices, no fault (`cloud/REPORT-T2.md` section 4.3).

Module 0.8.0 (2026-11-04): the full offline suite 1321 passing; G0 to G7 pass on five samples; the module installed on the cloud gateway (active,
97 registered); G8 6 of 6 routes on `cadre_hmi_wtpobf`. The showcase project (page 15): G0 to G7 pass, G8 12 of 12 pages, G11 11 of 11 devices
with `--faceplate asm`, and its functional check 12 of 12 pages, 54 of 54 editor kinds and 33 of 33 events.

## 8. The Owner's Decisions

1. **T0.** Three classes wrapped in subagents; the automation button asks (Press) and writes on Confirm through the existing path (W3).
2. **T1.** A recipe first, then batches with a review; the nine line elements skipped; Press then Confirm for every command control; module-only kinds for
   elements without a library kind; display only for elements that imply writes.
3. **T2.** A new frame option beside the two older ones, which stay unchanged; all 33 frame components wrapped; charts and building blocks module-only and display
   only; both variants (`ob`, `obasm`); the Cadre crumb and alert strip kept; silence hidden; priorities mapped by wiki 13 section 11.1.

## 9. Open Items and Limits

1. Fixed during delivery: the instrument field identity of G11 (the sweep follows the library's title rule) and the intermittent walk row A-02
   (the glass scrolls an alarm row clear of the panel's toolbar before pressing its ACK).
2. For an operator, the module alert panel's toolbar covers the second row's ACK until the list is scrolled (the package's layout).
3. The glass gates that write on the ASM variant need an ASM sample with an ASM model, which the cloud copy does not have; the read-only ASM gates pass.
4. The gauges' 240 by 280 box is not measured and the gauges overflow it.
5. Writes of module-only kinds are deferred: the hydraulic valves' selection, the gauges' setpoints and several `click` events are carried or shown, never wired.
6. Not wrapped: `obc-automation-input-modal`, `obc-alert-list`. The nine line elements, skipped in T1, were wrapped on 2026-11-04 as display only
   pipe components (page 12 section 17.28). Not carried: the user menu's credentials and others listed per component in the catalogue.
7. The script is 2.75 MB and loads on every page of a project that uses a module component (GF-29).
8. The component test page is large; a G11 sweep of its 21 devices takes about 62 min.
9. Settled at the gateway run: a tree group press only toggles (GF-113; page 04 section 11.3 holds); the bell counts active alarms while the menu also lists
   cleared unacknowledged events, by design (page 13 section 13.11.6). Cosmetic: the toggletips float over the row above on the test page; the page title
   runs into the first tab on `obasm`.
10. The committed sample builds of `cadre_hmi_wtp` and `cadre_hmi_wtpob` predate the generator at `d9f8655`.
11. GF-99 to GF-114 may collide with numbers the source has used since `d9f8655`; renumber at the merge.

## 10. The Merge Back

Work returns to the source repository as a diff of the mirrored paths (`git diff 26f38c8 <tip> -- . ':!cloud'`). Generated files are regenerated at the source,
not merged: `module/components.json`, the schemas, `mounted/`, `library/contracts.json`, `library/profile.json`, `module/CATALOGUE.md` and the parent build.
Then the full suite (1318 in the cloud), the signed build and its install with the owner's restart (page 12 section 17.6). Ranges and the list of paths are in
`CONFIGURATION.md` section 10; the reports are `cloud/REPORT-T0.md` and `cloud/REPORT-T1.md`.

## 11. References

1. `CONFIGURATION.md` (root), `module/CATALOGUE.md`, `cloud/PROGRESS.md`, `cloud/REPORT-T0.md`, `cloud/REPORT-T1.md`, `cloud/WRAP-RECIPE.md`,
   `cloud/FRAME-DESIGN.md`, `cloud/setup.sh`.
2. This wiki: page 04 (frames), 07 (GF-99 to GF-114), 08 (gates), 12 (the module, sections 17.10 to 17.28), 13 (glass, section 13.11),
   15 (the showcase), 16 (the selection criteria), 17 (the tag model and UDTs), 18 (the view builder reference).
3. pinned web components, `@oicl/openbridge-webcomponents` 2.0.0-next.155, Apache-2.0 (COBD-003).

## 12. Third-party Names That Remain

Table 11a. The categories of third-party name that stay in the tracked text, and why. Each is an identifier, a code literal or a required attribution, not
a product name used in prose.

| Category | Examples | Why it stays |
|---|---|---|
| The pinned package name and path | `@oicl/openbridge-webcomponents`, `node_modules/@oicl/openbridge-webcomponents/...`, `dist/openbridge.css`, `openbridge-webcomponents.bundle.js` | The Apache-2.0 package the module bundles; its attribution is required (`NOTICE`, the module licence page, the third-party section of `README.md` and `CONFIGURATION.md`) |
| The package element tags | `obc-pump`, `obc-top-bar` and the other `obc-*` tags; `obi-*` icon names | Names defined by the pinned package; the wrappers register them |
| Option values and project names | `openbridge` (frame and faceplate style), `asm`, `ob`, `obasm`; `cadre_hmi_wtpob`, `cadre_hmi_wtpobf` | Identifiers that existing projects store; renaming them would break those projects |
| Component, module and resource identifiers | `cadre.ob.*`, `cadre.hmi.ob`, `cadre-ob.js`, `cadre-ob.css`, `Framework/OB/*`, `NotoSans-OB.ttf`, the Java package `cadre.hmi.ob`, the Gradle project name `cadre-openbridge` | Identifiers the gateway, the projects and the tools resolve by name |
| The token file | `library/tokens/openbridge-tokens.json` | A file name read by the generators; the tokens are from the pinned package |
| Attribution and licence text | `NOTICE`, `module/gateway/src/main/resources/mounted/NOTICE.txt`, `LICENSES/`, `ob-components.js.LEGAL.txt`, the package line of `module/web/package.json` | Licence obligations of the Apache-2.0 package |
| Reference DOM selectors | `openbridge.manual.*` in `tools/compare/fingerprint.js` | Selector strings for an external page that the comparison tool can read; no behaviour of the library depends on them |
