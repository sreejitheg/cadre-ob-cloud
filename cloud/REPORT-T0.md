# Spike T0 Report: the Library Build in a Cloud Session

Session of 2026-11-03, branch `spike/t0`, from the copy of `Cadre-Sandbox-OpenBridge` `main` at `d9f8655` (cloud
commit `26f38c8`). This report replaces the stop report of 2026-11-02, whose only cause was the absent licence
variable. The daily record is `cloud/PROGRESS.md`.

## 1. The Environment

### 1.1 Summary

A cloud session can build, install and prove the module and the parents on its own Ignition gateway. Every step
of the brief's section 3 worked inside the container, with the Docker daemon started by the session itself. The
environment was working about 25 minutes after the session started, well inside the two hour limit.

### 1.2 Tools

| Item | Outcome |
|---|---|
| Licence | `ACCEPT_IGNITION_EULA` is `Y` in the session environment; it is passed through to the container by name (`-e ACCEPT_IGNITION_EULA`) and never given a value by the session |
| Docker | No daemon runs at session start. `dockerd` started by the session works (overlayfs snapshotter, cgroup v1, bridge network, port publishing to `localhost`) |
| Network | Docker Hub, `nexus.inductiveautomation.com`, `services.gradle.org`, the Gradle plugin portal, Maven Central, PyPI, the npm registry and the Ubuntu archive are admitted by the network policy |
| Image | `inductiveautomation/ignition:8.3.6` pulled in about 1 min |
| Python | 3.13.18; Pillow 12.3.0; Playwright for Python pinned to 1.63.0 (see 1.3) |
| Browser | The image's Playwright Chromium build 1243 (Chrome for Testing 153); no browser downloaded |
| Java | OpenJDK 17.0.20.1 from the Ubuntu packages, beside the image's JDK 21 |
| Node | 22.23.4 with npm 10.9.9; `npm ci` in `module/web` installs the pinned 2.0.0-next.155 (Apache-2.0) in 5 s |
| Gradle | 8.2.1 by the wrapper; one online build (2 min 11 s) fills the cache, after which `build_module.py` builds offline in under 15 s |

### 1.3 Unknowns of Section 3 and Their Answers

1. **Playwright.** `pip install playwright` gives 1.64.1, which expects browser build 1248 and cannot launch: the
   first offline run had 34 errors from this one cause. Version 1.63.0 expects build 1243, the image's own, so the
   pin replaces a browser download. `CHROME_PATH` is kept in the session variables but the tools launch Playwright's
   own Chromium and do not read it.
2. **Commissioning variables of 8.3.** Read from the image (the entrypoint script and the gateway's commissioning
   classes): `ACCEPT_IGNITION_EULA`, `GATEWAY_ADMIN_USERNAME`, `GATEWAY_ADMIN_PASSWORD`, `IGNITION_EDITION`,
   `GATEWAY_MODULES_ENABLED` and the port variables. The container was commissioned with the first four (edition
   `standard`, all modules) and the gateway started in 24 s.
3. **Unsigned modules.** The JVM system property `ignition.allowunsignedmodules=true`, given after `--` on the
   container's command line (the entrypoint passes arguments that start with `-D` to the JVM). The gateway's
   `GET /data/api/v1/gateway-info` then reports `allowUnsignedModules` true.
4. **API token without the web interface.** An 8.3 token is a configuration resource
   `config/resources/core/ignition/api-token/<name>/` with `config.json`
   `{"profile": {"type": "basic-token", "securityLevels": [...], "secureChannelRequired": false, "timestamp": ...},
   "settings": {"tokenHash": ...}}`. The hash is the URL safe Base64 of the SHA-256 of the raw 32 byte key; the
   request header is `X-Ignition-API-Token: <name>:<key>`. The key was generated locally and only its hash written
   to the gateway's volume, then the container restarted. The gateway refuses to grant `Authenticated/Roles` to a
   token from configuration (it logs and ignores the level), so a custom security level `CadreApi` was declared and
   added to the gateway's read and write permissions, and granted to the token. The token then passes every route
   `deploy.py`, `install_module.py` and `restart_gateway.py` use. The gateway also offers
   `POST /data/api/v1/api-token/generate`, which needs a token already.
5. **Test user.** Added to the internal user source `default` (`users.json` of the resource) with the
   `Administrator` role; the stored form is `[SALT]` followed by the hexadecimal SHA-256 of the password and the
   salt, verified against the commissioned admin user before use. The test user signs in through the project's
   identity provider `default` (proved in the W3 write check, section 3.4).
6. **Installing an unsigned module.** The REST install of `install_module.py` works, and the gateway asks for a
   restart (GF-28). After the restart the gateway stops at a commissioning step: the unsigned module's certificate
   must be trusted before the gateway starts. The commissioning page's own call does it:
   `POST /post-step` with `{"id": "modules", "step": "modules", "data": {"acceptedLicenses": [],
   "acceptedCertificates": ["cadre.hmi.ob"]}}` (found by driving the page with Playwright), then a container
   restart. Module 0.4.3 then started, "Registered 11 Cadre OpenBridge components", and its script was served.
   A signed module would not need the step; the source host signs, the cloud does not.

### 1.4 The Setup Script

`cloud/setup.sh` has three modes. `environment` installs the JDK, Playwright 1.63.0 and Pillow, starts `dockerd`,
pulls the image, runs `npm ci`, warms the Gradle cache and writes `/root/.cadre/env.sh`; it is idempotent (0.3 s
on a warm machine) and takes about five minutes cold, most of it the Gradle warm-up and the image pull. It is the
part to paste into the cloud environment's setup script. `gateway` creates and commissions the gateway, the token
and the test user; tested from scratch on a throwaway gateway beside the first (port 8089), it gave a gateway whose
token answers 200 in 48 s, and a second run changed nothing. `trust-module` performs the commissioning step of
1.3 item 6. Whether a gateway started by the setup script survives into a later session depends on the cloud
environment's caching of `/var/lib/docker`, which this session could not test; `gateway` recreates it in under a
minute either way.

### 1.5 Portability Changes

Each keeps the source host's behaviour when its variable is absent.

| Path | Change |
|---|---|
| `tools/hmi/gates.py` | The validator's location from `CADRE_IGNITION_WIKI` (default `F:/repos/Ignition-Wiki`) |
| `tests/test_hmi.py` | The registry schemas of the time series test from the same variable and default |
| `module/tools/build_module.py` | `CADRE_JDK17` names the JDK where the Windows locations do not exist; the built file is `CadreOpenBridge.unsigned.modl` when there are no signing properties (the tool looked for the signed name and failed after a successful unsigned build) |
| `module/gradlew` | Marked executable in the index (mode 100755); Windows ignores the bit |
| `tools/compare/faceplates.py` | Option `--faceplate {openbridge,asm}`, default `openbridge` as before (section 2.3) |

The session variables of `CLAUDE.md` section 4 were set in `/root/.cadre/env.sh` and no other path needed a change.
`CADRE_TEST_LOGIN` set in the shell makes one offline test fail (section 2.1).

## 2. The Baseline

### 2.1 Offline Tests

`python -m unittest discover -s tests`, after the Playwright pin: 1081 tests run, 1080 passed, 1 failed, none
skipped, in 3 min 59 s (the source's last record is 671 passing on 2026-10-26; later commits added tests).

| Failure | Kind | Reason |
|---|---|---|
| `test_glass_gates_plan.FakeGatewayTests.test_without_the_test_login_the_ack_gate_fails_and_says_why` | Environmental | The test assumes `CADRE_TEST_LOGIN` absent from the shell, and the cloud sets it; with `env -u CADRE_TEST_LOGIN` the module passes 37 of 37 |

No real failure. The first run, before the pin, had 34 errors, all Playwright's missing browser build.

### 2.2 Builds and Offline Gates

| Project | Outcome |
|---|---|
| `cadre_hmi_base` | Rebuilt byte-identical to the committed build; G1 on 65 views clean; deployed |
| `cadre_hmi_base_asm` | Built and deployed |
| `cadre_hmi_wtp` | G0 to G7 pass (14 gates); deployed |
| `cadre_hmi_wtpob` (`--render module`) | G0 to G7 pass; deployed |
| `cadre_hmi_ctest` (component test page alone, ASM frame and faceplates, module rendering) | G0 to G7 pass, 19 devices and 21 device symbols; deployed with its 838 tags |
| Module 0.4.3 | Built offline, unsigned, 607,393 bytes; the generated assets reproduce the committed ones byte for byte |

The committed builds of the two samples predate the generator at `d9f8655`: a rebuild differs from them (the
navigation dock's `modal`, the session properties and the screens). The rebuilt files were deployed and not
committed, so that the merge back carries no regenerated sample.

### 2.3 Gateway Gates

| Gate | Project | Outcome |
|---|---|---|
| G8 | `cadre_hmi_wtpob` | PASS on 6 of 6 routes: 139, 158, 257, 155, 217 and 122 components, no quality overlay, no error badge |
| G11 | `cadre_hmi_wtpob` | PASS, 44 of 44 faceplates, no fault |
| G10 and walk | `cadre_hmi_wtpob` | Not run: `wtp_suite.py` stopped in G10 on a real defect of the tools (2.4) |
| G8 | `cadre_hmi_ctest`, `/component-test` | PASS, 5270 components, no quality overlay, no error badge |
| G11 | `cadre_hmi_ctest`, `/component-test` | 21 of 21 devices opened, 278 leaf views, no tab fault; FAIL on one identity (2.4) |

### 2.4 Real Findings of the Baseline

1. **G10 stops in `glass.button`.** `tools/compare/glass.py` line 226 returns `Confirmed(loc, scope.page)`, and
   `functional.frame_steps` passes a Playwright `Page`, which has no attribute `page`. G10 and the generated walk
   therefore cannot run from `wtp_suite.py`. G10 is outside T0, so this was reported and not fixed.
2. **The faceplate sweep could not judge an asm project.** The command line of `faceplates.py` judged every device
   against the `openbridge` faceplate, so the first sweep of the component test page reported 9 tab faults that were
   the style, not the page. Fixed at the cause with the option `--faceplate` (1.5); with `--faceplate asm` the tab
   faults are gone.
3. **The instrument field's faceplate title.** The faceplate opened from the module's instrument field `TB_FIELD`
   reads its title as `Temp`, the field's label, so G11 counts `TB_FIELD` missing and `Temp` unexpected. Present at
   0.4.3 before any wrap; the cause (the faceplate's title or the sweep's reading of it) was not established.
4. **One sweep of the component test page takes about 15 minutes** of wall time and almost no tokens.

## 3. The Wraps

### 3.1 Method

Each wrap ran in its own subagent on Sonnet 5.5 at medium effort, one after another, from a common brief (the
non-negotiables, the files to read, the generators, the offline gates) and a row of its own. The wraps share the
generator (`module/tools/gen_module_assets.py`), the contract, the bundle and the module tables of
`tools/hmi/screen.py`, so they cannot run in parallel without conflicts. The subagents changed no version, built
nothing, touched no gateway and committed nothing; the main session reviewed each diff, committed it alone, and then
built 0.4.4 once, installed it once and ran the gateway gates for all three. Tokens are the Agent tool's reported
totals for each subagent; minutes are its reported durations.

### 3.2 Measurements

| Wrap | Element | Component | Class | Tokens | Tool calls | Minutes | Tests after |
|---|---|---|---|---|---|---|---|
| W1 | `obc-filter` | `cadre.ob.filter` | Static symbol | 132,335 | 32 | 11.2 | 1086 |
| W2 | `obc-indicator-generator` | `cadre.ob.generator` | Stateful device | 235,754 | 81 | 11.7 | 1093 |
| W3 | `obc-automation-button` | `cadre.ob.button` | Shared control | 186,858 | 57 | 9.1 | 1101 |
| Total | | | | 554,947 | 170 | 32.0 | 1102 with the release test |

### 3.3 Files Changed

Every wrap touched the same core: `module/web/entry.js` (bundle import), `module/tools/measure_defaults.py` and
`module/web/defaults.json` (the element's measured defaults, additions only), `module/tools/gen_module_assets.py`
(the component entry), `module/common/src/main/java/cadre/hmi/ob/common/CadreOb.java` (registration: a new component
needs one line of Java), the regenerated `module/components.json`, schema and `cadre-ob.js`, `tests/test_module.py`,
and a subsection of `wiki/12-module-spike.md` (17.10 to 17.12). Beyond the core:

| Wrap | Further paths |
|---|---|
| W1 | `tools/hmi/screen.py` (the library's `filter` kind mapped in `MODULE_KIND`, a value table `MODULE_VALUE`: `regular` is the element's `square`), `tools/hmi/testbench.py`, `tools/compare/glass_gates.py`, `library/profile.json`, `tests/test_hmi.py` |
| W2 | `tools/hmi/screen.py` (`generator` in the module tables, `module_probe`), `tools/compare/glass_gates.py`, `tools/compare/walk_plan.py`, `module/.../mounted/css/cadre-ob.css`, `library/profile.json`, `tests/test_hmi.py`, `tests/test_asm_devices.py`, `wiki/13` section 12.2 |
| W3 | `tools/hmi/parts.py` (a pulse button with `render: module` draws its Press as the module button), `tools/hmi/screen.py`, `tools/hmi/testbench.py`, `schemas/screen-descriptor.schema.json` (key `render`), `tests/test_asm_parts.py`, `wiki/13` section 13.4 |

### 3.4 Gates

| Check | W1 filter | W2 generator | W3 button |
|---|---|---|---|
| Offline tests (each wrap, then the full suite on 0.4.4: 1102 passing) | Pass | Pass | Pass |
| G0 to G7 on the component test page (19 devices, 21 device symbols) | Pass | Pass | Pass |
| On the component test page, module 0.4.4 | 12 elements drawn | 12 elements drawn, one with its alarm frame | 1 element drawn |
| G8 on `/component-test` (4424 components, no overlay or error badge) | Pass | Pass | Pass |
| G11 (21 of 21 devices, no tab fault) | Not a device of the model | `GEN` opens `Faceplate/ASM/Generator` from the module component, four tabs, no overlay or badge | Not a device |
| Command write | Not applicable | Not applicable | Signed out: Confirm disabled, a forced click writes nothing. Signed in as `Administrator`: `TB_GEN/cmdStart` true for the 60 s pulse, the generator then draws running |

G11 reports FAIL for the page as a whole on the instrument field's identity alone, as it did before the wraps
(section 2.4 item 3); no fault comes from a wrap.

### 3.5 What the ASM Rules Needed

1. **W1.** Nothing new: the filter takes `alert`, `alertFrameStatus` and `alertFrameMode` like the valves, bound to the
   page's `custom.alerts` (wiki 13 section 11.2), and OpenBridge's own levels already colour by priority (section 11.1).
   A vertical filter stays on the library view, because the library's `vertical` flag does not say which of the
   element's two vertical orientations is meant.
2. **W2.** The element has no alert attributes, so the wrapper adds OpenBridge's unchanged `obc-alert-frame` in the
   indicator's shadow root, keyed to the Cadre palette classes (`level-critical` rgb(196, 36, 183), `level-high`
   rgb(227, 0, 25), measured offline), and the identifier and status word with the unchanged
   `obc-automation-button-readout-stack`. Only `state` is bound (`on`); the symbol has no fault parameter, so a fault
   shows through the alarm frame. The generator set picture stays on the library view. Rule 7 of `CLAUDE.md` held:
   no OpenBridge code was changed.
3. **W3.** The element has no `enabled` property, so a component event that called the write path itself would
   skip the confirmation and fail G7. The module button therefore replaces the Press of the library's pulse button
   (W18): Press asks, Confirm calls the existing `cadre.hmi.page_pulse` with its `Administrator` check (COBD-024), and
   the button is drawn `static` when the session may not write. This departs from the brief's wording ("the
   component event calls the path") and is recorded in wiki 12 section 17.12; it keeps the existing confirmation
   and role rule unchanged.

### 3.6 The Main Session

The main session ran section 3, the baseline, the reviews and commits, the release and every gateway gate. It took
about 150 turns. Its context ended at an estimated 0.3 million tokens, about two thirds of it the environment and
baseline work (image and jar inspection, gate output); every turn re-reads that context from the prompt cache, so the
billed figure is larger, and the owner reads the exact spend from the account's usage page. By the Agent tool's
measure the session's total is therefore about 0.85 million tokens (0.55 million in the wraps), above the target of
0.5 million and below the hard stop of 1.2 million. The session ran from 00:06 to about 01:45 UTC: about 25 minutes
to a working environment, 30 minutes of baseline, 32 minutes of wraps and 20 minutes of release and gates, with
gate sweeps overlapping the wraps.

## 4. The Extrapolation

### 4.1 The Remaining Elements by Class

The pinned release (2.0.0-next.155) declares 50 automation elements, 6 bars and graphs, 6 building blocks and 122
components, 33 of them parts of an application frame. After T0 the module wraps 10 of the automation elements, the
two alert lists and the canvas zoom of its own.

| Class | Measured on | Remaining automation elements (T1, 40) |
|---|---|---|
| Static symbol | W1 | Electrical symbols on the filter's base (on, readout, alert frame, badges): `bipolar-transistor`, `capacitor`, `converter`, `diodes`, `ground`, `logic`, `mosfet`, `resistor`, `router`, `source`, `switch`, `transformer` (12); line elements: `bus`, `corner-line`, `direction-line`, `end-point-line`, `horizontal-line`, `vertical-line`, `three-way-line`, `line-cross`, `line-overlap` (9); icons: `automation-badge`, `hydraulic-check-valve`, `valve-analog-two-way-icon`, `valve-analog-three-way-icon` (4). Total 25 |
| Stateful device | W2 | `damper`, `heat-exchanger`, `heat-pump`, `hydraulic-separator`, `hydraulic-valve-4-3`, `hydraulic-valve-x-2`, `indicator-battery`, `indicator-engine`, `indicator-tank-atmospheric`, `gauge-generator`, `gauge-motors-and-pumps`, `gauge-valve`, `automation-readout`. Total 13 |
| Shared control | W3 | `automation-input-modal`, `transmitter-button`. Total 2 |

T2, taken here as the rest of the recommended scope: the bars and graphs (`area-graph`, `donut-chart`, `line-graph`,
`pie-chart`, `polar-chart`, `radial-bar-chart`, 6, stateful devices with data arrays like the alert lists), the
building blocks (`alert-list`, `bar-horizontal`, `bar-vertical`, `circular-progress`, `instrument-radial`,
`readout-block`, 6, stateful devices), about 20 of the 33 frame components (`top-bar`, `navigation-menu`,
`navigation-item`, `navigation-item-group`, `breadcrumb`, `alert-button`, `alert-menu`, `alert-menu-item`,
`app-button`, `app-menu`, `user-button`, `user-menu`, `clock`, `tab-row`, `tab-item`, `modal-window`, `tooltip`,
`toggletip`, `notification-button`, `context-menu-input`; shared controls with events), and the parent framework's
move onto them. T1 and T2 together are about 72 wraps, near the feasibility review's 75.

### 4.2 Cost per Wrap

All in, a wrap costs its subagent's tokens plus the main session's share: the brief, the review and commit, and a
share of the joint build, install and gates (about 35,000 tokens a wrap at T0's scale).

| Class | Subagent (measured) | All in | Minutes, subagent and orchestration |
|---|---|---|---|
| Static symbol | 0.13 M | 0.17 M | 14 |
| Stateful device | 0.24 M | 0.28 M | 15 |
| Shared control | 0.19 M | 0.22 M | 12 |

A gateway step (build, install, restart, deploy, G8, and a G11 sweep of about 15 minutes) adds about 20 minutes of
wall time per batch and few tokens.

### 4.3 Estimate for T1 and T2

| Tranche | Wraps | One element per subagent | With batching | Wall time |
|---|---|---|---|---|
| T1 | 25 static, 13 stateful, 2 controls | 8.3 M | 6.5 M (the 25 static symbols in batches of four, at about twice a single wrap per batch) | 8 to 12 h |
| T2 | 12 stateful, about 20 frame controls, the framework | 7.8 M plus 1 to 2 M for the framework | 8 to 9 M | 9 to 11 h |
| T1 and T2 | about 72 | 17 to 18 M | 15 to 16 M | 17 to 23 h in about 8 to 12 sessions |

By the Agent tool's measure this is above the feasibility review's 7 to 14 million tokens. Two reductions are
within reach: a written wrap recipe drawn from W1 to W3, so that each subagent does not re-read the generator,
`screen.py` and the tests to rediscover the pattern (most of W2's 81 tool calls were reading), and batching the
elements that share a base class. Together they may lower the per-wrap cost by about a third, which would bring
T1 and T2 to about 10 to 12 million. The token measure itself should be confirmed against the account's usage page,
which counts cached re-reads at their own rate.

### 4.4 Risks Found

1. **Sequential wraps.** The shared generator, contract, bundle and module tables make parallel subagents conflict;
   wall time grows linearly with the wraps.
2. **Gate time.** One G11 sweep of the component test page takes about 15 minutes; it grows with the page, so gates
   should be batched, not run per wrap.
3. **Semantic mismatch.** An element and a library kind rarely match one to one (the vertical filter, the generator
   set, the button's missing `enabled`); each needs a decision, recorded in `MODULE_EXCEPT`, `MODULE_NEEDS` or the
   wiki, and some deserve the owner's review (W3's Press and Confirm).
4. **Elements without alert attributes** need the wrapper to add the alarm frame (W2); the stateful class costs most.
5. **Line elements** overlap the library's own pipes and its flow solver (G6); wrapping them may need a design
   decision first.
6. **Unsigned module on a fresh gateway** stops at a commissioning step after its first install; `cloud/setup.sh
   trust-module` handles it, and upgrades need no step.
7. **Trial.** The gateway's trial lasts two hours; the tools reset it after expiry (GF-03). A long tranche session
   crosses several resets.
8. **G10 and the walk** cannot run until the `glass.button` defect (section 2.4) is fixed, so the functional gate
   of the brief's section 5 remains unproved in the cloud.
9. **Merge back of generated files.** `cadre-ob.js` (about 1 MB minified) and `components.json` change with every
   wrap and do not merge textually; the source should regenerate them (section 5).

## 5. The Merge Back

### 5.1 Mirrored Paths Changed

All on branch `spike/t0`, from `26f38c8`. Paths under `cloud/` exist only for the cloud and are not merged.

| Path | Reason |
|---|---|
| `tools/hmi/gates.py` | Portability: `CADRE_IGNITION_WIKI` |
| `tests/test_hmi.py` | Portability (`CADRE_IGNITION_WIKI`); W1, W2 tests |
| `module/tools/build_module.py` | Portability: `CADRE_JDK17`; the unsigned file name |
| `module/gradlew` | Executable mode only |
| `tools/compare/faceplates.py` | Option `--faceplate` |
| `module/build.gradle.kts` | Version 0.4.4 and description |
| `module/web/entry.js` | W1, W2, W3 imports |
| `module/web/defaults.json` | W1, W2, W3 measured defaults |
| `module/tools/measure_defaults.py` | W1, W2, W3 elements |
| `module/tools/gen_module_assets.py` | W1, W2, W3 component entries; `click` as `onPress` |
| `module/common/src/main/java/cadre/hmi/ob/common/CadreOb.java` | W1, W2, W3 registration |
| `tools/hmi/screen.py` | W1, W2, W3 module tables |
| `tools/hmi/testbench.py` | W1, W3 |
| `tools/hmi/parts.py` | W3 |
| `tools/compare/glass_gates.py` | W1, W2 |
| `tools/compare/walk_plan.py` | W2 |
| `schemas/screen-descriptor.schema.json` | W3 key `render` |
| `tests/test_module.py` | W1, W2, W3 tests; release tests for 0.4.4 |
| `tests/test_asm_devices.py` | W2 |
| `tests/test_asm_parts.py` | W3 |
| `wiki/12-module-spike.md` | Subsections 17.10 to 17.12 |
| `wiki/13-faceplates-alarm-lists-interlocks.md` | Sections 12.2 and 13.4 |

Generated, to be regenerated at the source rather than merged: `module/components.json`,
`module/common/src/main/resources/schemas/filter.props.json`, `generator.props.json`, `button.props.json`,
`button.onPress.json`, `module/gateway/src/main/resources/mounted/js/cadre-ob.js`, `mounted/css/cadre-ob.css` and
`library/profile.json`.

### 5.2 Applying the Diff

1. `git diff 26f38c8 spike/t0 -- . ':!cloud' > t0.diff`, then apply the source paths of 5.1 to the source repository
   (its `main` at `d9f8655` plus whatever it has gained since).
2. Regenerate: `cd module/web && npm ci && npm run build && cd ../.. && python module/tools/gen_module_assets.py`,
   then `python tools/hmi/parent.py --out build` (the parent rebuilt byte-identical in the cloud).
3. `python -m unittest discover -s tests` (1102 passing in the cloud), then the signed build of 0.4.4 and its
   install with the owner's restart, as wiki 12 section 17.6 describes.
4. Not merged: the sample builds under `build/cadre_hmi_wtp` and `build/cadre_hmi_wtpob` (unchanged on the branch),
   and the cloud's `build/cadre_hmi_base_asm` and `build/cadre_hmi_ctest` (excluded locally).
