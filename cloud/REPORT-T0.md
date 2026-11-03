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
| Gradle | 8.2.1 by the wrapper; one online build (2 min 11 s) fills the cache, after which `build_module.py` builds offline (about 40 s) |

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
   salt, verified against the commissioned admin user before use. The sign in through the project's identity
   provider is proved by W3 (section 3.4).
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
