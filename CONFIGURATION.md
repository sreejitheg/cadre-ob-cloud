# Cadre OpenBridge Library: Configuration Reference

| Field | Value |
|---|---|
| Subject | The operational configuration of the Cadre OpenBridge library as built in the cloud sessions of 2026-11-02 and 2026-11-03 (spike T0 and tranches T1 and T2) |
| Library state | Repository `cadre-ob-cloud`, branch `spike/t0` at `4cdda21`, a copy of `Cadre-Sandbox-OpenBridge` `main` at `d9f8655` |
| Module | Cadre OpenBridge 0.7.0 (`cadre.hmi.ob`), 88 components |
| Gateway | Ignition 8.3.6 in Docker, trial mode |
| Companions | `module/CATALOGUE.md` (every component, generated), `wiki/14-library-configuration.md` (the same configuration as a wiki chapter), `wiki/07-gateway-facts.md` (measured facts GF-99 onward), `cloud/PROGRESS.md` (the dated record) |

This document states what each configuration is, where it is set, what it requires and what it refuses. It does not repeat
the component list: see `module/CATALOGUE.md`. Secrets are described by where they are kept, never by value (`CLAUDE.md`
rule 6). Facts are measured in the cloud sessions unless a section says otherwise; each cites its date in `cloud/PROGRESS.md`.

## 1. The Cloud Environment

### 1.1 The Setup Script

`cloud/setup.sh` has three modes. It is idempotent: a second run changes nothing.

| Mode | What it does | Measured time |
|---|---|---|
| `environment` (default) | Installs JDK 17 (Ubuntu package `openjdk-17-jdk-headless`), Playwright 1.63.0 and Pillow, starts the Docker daemon if none answers, pulls the Ignition image, runs `npm ci` in `module/web`, marks `module/gradlew` executable, warms the Gradle cache with one online build, and writes `$CADRE_HOME/env.sh` | 0.3 s warm; about 5 min cold (JDK about 1 min, image pull about 1 min, Gradle warm-up 2 min 11 s, `npm ci` 5 s) |
| `gateway` | Creates and commissions the gateway container, writes the API token and the test user as configuration resources, creates the history provider, restarts the container once if a resource changed, and checks that the token answers 200. Stops with exit 3 unless `ACCEPT_IGNITION_EULA` is `Y` in the environment | 24 s to start; 48 s from nothing to a token that answers 200 (tested on a throwaway gateway on port 8089); 1 min 41 s after a daemon restart |
| `trust-module` | After an unsigned module is installed and the gateway restarted: if the gateway reports `COMMISSIONING`, posts the module trust step and restarts the container; then waits for `RUNNING` | A restart of about 15 to 30 s |

The body of the `environment` mode is what to paste into the cloud environment's setup script, so that later sessions start
warm. Whether the Docker image and volume survive into a later session depends on the cloud environment's caching of
`/var/lib/docker`, which no session could test; `gateway` recreates the gateway in under a minute either way.

### 1.2 Variables

`$CADRE_HOME/env.sh` (default `/root/.cadre/env.sh`) is written by `setup.sh environment`. Source it before every command:
`. /root/.cadre/env.sh`. It keeps the Windows defaults of the source repository when a variable is absent.

Table 1. Variables of the session and the tools.

| Variable | Set by | Value in the cloud | Meaning |
|---|---|---|---|
| `ACCEPT_IGNITION_EULA` | The owner, on the cloud environment | `Y` | The Ignition licence acceptance. Passed to the container by name; the session never sets it and `setup.sh gateway` stops without it |
| `CTIG_SRC` | `env.sh` | `<repo>/cloud/vendor` | ctig's gateway REST client (`ctig/gateway/rest.py`, copied unchanged from ctig `046a3a5`); `tools/hmi/deploy.py` puts it on `sys.path` |
| `CTIG_IGNITION_TOKEN_FILE` | `env.sh` | `/root/.cadre/ignition-token` | The file holding the API token. Resolution order of ctig: environment `CTIG_IGNITION_TOKEN` or `IGNITION_API_TOKEN`, then this file, then the Windows Credential Manager |
| `CADRE_IGNITION_GATEWAY_URL` | `env.sh` | `http://localhost:8088` | The gateway every tool addresses; the owner's local gateway is never reached from the cloud |
| `CADRE_TEST_LOGIN` | `env.sh` | `/root/.cadre/test-login.properties` | The properties file (`user`, `password`) of the gateway's own test user, used by G10 and the walk to sign in. See 1.4 for its effect on one offline test |
| `CADRE_PIL_PYTHON` | `env.sh` | The `python3` that has Pillow | The interpreter the picture tools use |
| `CADRE_IGNITION_WIKI` | `env.sh` | `<repo>/cloud/vendor/ignition-wiki` | The Ignition-Wiki validator and schemas (copied unchanged from Ignition-Wiki `62939dc`). Read by `tools/hmi/gates.py` (gate G1) and `tests/test_hmi.py`; default `F:/repos/Ignition-Wiki` at the source |
| `CADRE_JDK17` | `env.sh` | `/usr/lib/jvm/java-17-openjdk-amd64` | The JDK 17 home that `module/tools/build_module.py` passes to Gradle where the owner's Windows locations do not exist |
| `CHROME_PATH` | `env.sh` | `/usr/bin/google-chrome` (kept if already set) | Kept for the brief's wording. The tools launch Playwright's own Chromium and do not read it |
| `CADRE_HOME` | Optional, for `setup.sh` | `/root/.cadre` | The folder of secrets, logs and `env.sh`. A second value sets up a second, throwaway gateway beside the first |
| `CADRE_GW_CONTAINER` | Optional, for `setup.sh` | `cadre-gw` | The container name |
| `CADRE_GW_VOLUME` | Optional, for `setup.sh` | `cadre-gw-data` | The Docker volume that holds the gateway's data folder |
| `CADRE_GW_PORT` | Optional, for `setup.sh` | `8088` | The published HTTP port (the container always listens on 8088) |
| `CADRE_IGNITION_DATA` | Optional | Not set | The gateway data folder, read by `install_module.py --list` to hash the installed module file. Unnecessary in the cloud: the list then reports the file fields as null with a note |
| `CTIG_IGNITION_TOKEN` | Not used | | Would carry the token value in the environment; the token file is used instead so that the value is not in a process listing |

The other keys of `CLAUDE.md` section 4 (the table of paths from the source repository) are the same variables.

### 1.3 Pinned Tools

| Tool | Version | Reason |
|---|---|---|
| Playwright for Python | 1.63.0, pinned in `setup.sh` as `PW_VERSION` | The image's own Chromium is build 1243, which 1.63.0 expects. The newest PyPI release (1.64.1) expects build 1248 and cannot launch: the first offline run had 34 errors from this one cause. The pin replaces a browser download |
| Pillow | 12.3.0 (unpinned in the script; this was the version installed) | Picture comparison tools |
| JDK | 17.0.20.1 (Ubuntu) beside the image's JDK 21 | The module builds under JDK 17 |
| Gradle | 8.2.1, by the wrapper | One online build fills the cache; `build_module.py` then builds offline (`--offline`) in under 15 s |
| Node and npm | 22.23.4 and 10.9.9 | `npm ci` only (`CLAUDE.md` rule 2) |
| Python | 3.13.18 | |
| OpenBridge web components | `@oicl/openbridge-webcomponents` 2.0.0-next.155, commit `2c98dda1`, Apache-2.0 | The only permitted source of OpenBridge material (COBD-003). Never change the version in `module/web/package.json` or `package-lock.json`; never run `npm install` |

### 1.4 Offline Tests and the Test Login

`python -m unittest discover -s tests` is offline. One test, `test_glass_gates_plan.FakeGatewayTests.test_without_the_test_login_the_ack_gate_fails_and_says_why`,
assumes `CADRE_TEST_LOGIN` is absent from the shell, so run the full suite as
`env -u CADRE_TEST_LOGIN python -m unittest discover -s tests`. Recorded counts: 1081 at the T0 baseline, 1102 after T0, 1191
after T1, 1299 after T2 (2026-11-03 12:57 to 13:02 UTC, 304 s), 1304 with the catalogue tests, 1318 at delivery (the fixes of the final gateway runs, 2026-11-03 19:50 UTC).

### 1.5 The Docker Daemon

No daemon runs at session start. `setup.sh` starts `dockerd` with `setsid nohup`, logging to `$CADRE_HOME/logs/dockerd.log`,
and waits up to 60 s for `docker info`. The daemon uses the overlayfs snapshotter, cgroup v1 and the bridge network, and publishes ports
to `localhost`. A plain background `dockerd` stopped with the session's worker process (the pause of 2026-11-03 02:02, and a running suite once in T1);
a daemon in its own session survives a restart of the worker, and a stopped daemon is restarted by `setup.sh environment` in 9 s with the
container, volume and module intact.

Long runs are started the same way (`setsid nohup`), because a worker restart also stops background gate runs. The scripts
`run-*.sh` kept under `/root/.cadre/` do so.

### 1.6 Network Policy

The cloud network policy admits Docker Hub, `nexus.inductiveautomation.com`, `services.gradle.org`, the Gradle plugin portal,
Maven Central, PyPI, the npm registry and the Ubuntu archive. Nothing else is needed. The OpenBridge 6.1 Figma file is a design
reference only and is not fetched.

## 2. The Gateway

### 2.1 Image and Container

`inductiveautomation/ignition:8.3.6` (about 1 min to pull). `setup.sh gateway` runs:

```
docker run -d --name cadre-gw -p 8088:8088 -v cadre-gw-data:/usr/local/bin/ignition/data \
  -e ACCEPT_IGNITION_EULA --env-file $CADRE_HOME/gateway.env -e IGNITION_EDITION=standard -e TZ=Australia/Sydney \
  inductiveautomation/ignition:8.3.6 -n cadre-cloud -m 2048 -- -Dignition.allowunsignedmodules=true
```

The gateway name is `cadre-cloud`, the heap 2048 MB, the edition `standard` with all modules, the time zone `Australia/Sydney`.
The gateway is throwaway and unrelated to the owner's local gateway: installing a module, restarting and recreating the container
are allowed in the cloud without asking (`CLAUDE.md` section 3). A second run of `gateway` starts an existing container and
does not recreate it.

### 2.2 Commissioning Variables (8.3)

Read from the image's entrypoint and the gateway's commissioning classes (GF-99): `ACCEPT_IGNITION_EULA`,
`GATEWAY_ADMIN_USERNAME`, `GATEWAY_ADMIN_PASSWORD`, `IGNITION_EDITION`, `GATEWAY_MODULES_ENABLED` and the port variables.
The container is commissioned with the first four. The admin user is `admin`; its password is generated at run time (2.9).

### 2.3 Unsigned Modules

The cloud builds the module unsigned (no signing properties). The gateway allows it through the JVM system property
`ignition.allowunsignedmodules=true`, given as `-Dignition.allowunsignedmodules=true` after `--` on the container command line
(the entrypoint passes arguments that start with `-D` to the JVM). `GET /data/api/v1/gateway-info` then reports
`allowUnsignedModules` true (GF-100).

### 2.4 The API Token

An 8.3 API token is a configuration resource, so the session writes it into the volume without the web interface (GF-101).
`setup.sh gateway` creates:

* `config/resources/core/ignition/api-token/cadre/config.json`: profile type `basic-token`, `secureChannelRequired` false,
  the security level `CadreApi`, and `settings.tokenHash`, the URL-safe Base64 (no padding) of the SHA-256 of the raw 32-byte key.
* `resource.json` beside it: scope `A`, version 1, enabled, description "Cadre cloud deploy token".
* The request header is `X-Ignition-API-Token: <name>:<key>`; the file `ignition-token` holds exactly that string. Only the hash
  is written to the gateway's volume. The gateway's `POST /data/api/v1/api-token/generate` needs a token already.

The gateway refuses to grant `Authenticated/Roles` to a token from configuration: it logs and ignores the level (GF-102). The script
therefore declares a custom security level `CadreApi` in `security-levels/config.json` and adds it to the read and write permissions in
`security-properties/config.json`, and grants it to the token. The token then passes every route that `deploy.py`,
`install_module.py` and `restart_gateway.py` use. Every write path also needs the gateway's `Administrator` role (COBD-024). After
the resources are written the container is restarted once and the token is checked with `GET /data/api/v1/projects/names`
(expected 200). The script sets the ownership of the resources folder to uid and gid 2003 (`chown -R`) after writing, so that the gateway's
user can read them.

### 2.5 The Test User

Added to the internal user source `default` (`user-source/default/users.json`) as `cadre_test` with the `Administrator` role. The
stored password form is `[SALT]` followed by the hexadecimal SHA-256 of the password and the salt (SALT eight hexadecimal digits);
this was verified against the commissioned admin user before use (GF-103). The user signs in through each project's identity provider
`default`, which `deploy.py` sets after every import (GF-44). Without it, G10 and the walk prove the refusal only and run no write group.

### 2.6 The History Provider

The sample tag models record history to `Sample_SQLite_Database`, which the source gateway has and a fresh one does not; without it no
trend draws (G10 F19, walk T-01 to T-03). `setup.sh gateway` creates it through the REST resource routes, without a restart (GF-104):

* `POST /data/api/v1/resources/ignition/database-connection`: an SQLite connection of that name to
  `jdbc:sqlite:${data}/local/cadre/history.db`.
* `POST /data/api/v1/resources/com.inductiveautomation.historian/historian-provider`: an SQL historian of the same name over the
  connection.

The configuration is minimal and our own, not the vendor's quick start, which would also install a sample project. Existing names
are listed first with `GET .../resources/names/<module>/<type>`, so a second run adds nothing.

### 2.7 The Trust Step of an Unsigned Module

A module that is installed for the first time by REST and is unsigned stops the gateway at a commissioning step after the restart:
`GET /StatusPing` answers a state with `COMMISSIONING` in place of `{"state":"RUNNING"}` (GF-105). `trust-module` does what the
commissioning page does:

1. `GET /bootstrap` and `GET /get-step?step=modules&name=modules` with a cookie jar.
2. `POST /post-step` with `{"id":"modules","step":"modules","data":{"acceptedLicenses":[],"acceptedCertificates":["cadre.hmi.ob"]}}`.
3. `docker restart cadre-gw`; wait for `RUNNING`.

The module then starts and logs "Registered N Cadre OpenBridge components". An upgrade of a module already trusted needs no step
(GF-106). A signed module would need none; the source host signs and the cloud does not.

### 2.8 Restart Behaviour and Times

Installing or upgrading a module leaves a pending restart task (GF-28). `module/tools/restart_gateway.py --confirm --wait 300`
restarts through REST and polls `StatusPing`. Measured (GF-107): a REST restart for an upgraded module reached "Registered" about 15 s
(0.5.0) and 28 s (0.4.4) after the request; a container start from cold took 24 s; `setup.sh gateway` brought the gateway back in 1 min 41 s after a daemon restart; a first install with the
trust step took one more restart. The wait loop of `setup.sh` allows 300 s (100 polls at 3 s).

### 2.9 Where Each Secret Is Kept

All under `$CADRE_HOME` (default `/root/.cadre`), a folder of mode 700, created with `umask 077`; none is in the repository or in a
log, and none is printed in full.

| File | Holds | Written by |
|---|---|---|
| `admin-password` | The admin user's generated password | `setup.sh gateway` (once, 18 random URL-safe bytes) |
| `gateway.env` | `GATEWAY_ADMIN_USERNAME` and `GATEWAY_ADMIN_PASSWORD` for the container's `--env-file` | `setup.sh gateway` |
| `ignition-token` | The API token string, `<name>:<key>` | `setup.sh gateway` |
| `test-login.properties` | `user` and `password` of the test user | `setup.sh gateway` |
| `env.sh`, `logs/` | Variables and logs; no secret | `setup.sh environment` |

The gateway's own volume holds only the token's hash and the test user's salted hash. The Ignition licence acceptance is the owner's
environment variable, not a file.

### 2.10 The Trial and Its Reset

A trial gateway runs two hours. `POST /data/api/v1/trial` resets it only after it has expired and answers 403 while it runs
(GF-03, GF-33); `deploy.ensure_trial()` waits for expiry and resets. For about a minute after a reset the route reports a healthy
trial while a new session still shows the trial page, which gate G8 once measured as six routes with no component; the gate tools
call `walk.settle_trial` and probe a fresh session before each gate. A long run crosses several resets: the trial expired during the
module run of G10 on 0.6.0 and the gateway was reset once during F7. In the cloud, recreating the container is the simpler reset
(`docker rm -f cadre-gw`, `docker volume rm cadre-gw-data`, `setup.sh gateway`), at the price of reinstalling the module and every
project.

### 2.11 Gateway Resources Kept by Convention

* Project names start `cadre_hmi`. The parent is `cadre_hmi_base`; a second parent `cadre_hmi_base_asm` can be built beside it
  (`parent.py --name`, COB-157). After importing the parent, re-import the children and verify in a new session (GF-10).
* Every project names the identity provider `default` (GF-44).
* The sample tags live under `[default]cadre_hmi_wtp`; the component test page under `[default]cadre_hmi_ctest`.

## 3. The Module

### 3.1 Identity

| Item | Value |
|---|---|
| Name and id | Cadre OpenBridge, `cadre.hmi.ob` |
| Version | 0.7.0 (`allprojects.version` in `module/build.gradle.kts`); a plain `major.minor.revision` (GF-27) |
| Required Ignition | 8.3.0; framework version 8; free module; licence `module/license.html` |
| Dependency | `com.inductiveautomation.perspective` in the gateway and designer scopes (`GD`) |
| Scopes | `:gateway` G, `:common` DG, `:designer` D |
| Hooks | `cadre.hmi.ob.gateway.CadreObGatewayHook` (G), `cadre.hmi.ob.designer.CadreObDesignerHook` (D) |
| Components | 88: 13 device and instrument components mapped to library kinds, 28 module-only symbols and glyphs, 11 charts and building blocks, 33 frame components, 3 alarm lists and canvas zoom. Per component: `module/CATALOGUE.md` |
| Registration | One `descriptor(...)` line for each component in `module/common/src/main/java/cadre/hmi/ob/common/CadreOb.java`, with one `event(...)` for each event |
| Upstream | OpenBridge web components 2.0.0-next.155 (Apache-2.0), attribution in `NOTICE` and `module/gateway/src/main/resources/mounted/js/ob-components.js.LEGAL.txt` |

### 3.2 Generated Files and How to Regenerate Them

Never hand edit a generated file (`CLAUDE.md` rule 4). Change the generator and rebuild.

| Generated file | Generator | Command |
|---|---|---|
| `module/gateway/src/main/resources/mounted/js/cadre-ob.js` (the OpenBridge bundle, the React wrappers and `module/web/canvaszoom.js`), `mounted/css/cadre-ob.css`, `mounted/fonts/NotoSans-OB.ttf`, `ob-components.js.LEGAL.txt` | `module/tools/gen_module_assets.py` from `module/web/dist/ob-components.js` | `cd module/web && npm ci && npm run build && cd ../.. && python module/tools/gen_module_assets.py` |
| `module/components.json` (the contract) and `module/common/src/main/resources/schemas/*.json` (88 property schemas and 94 event schemas) | the same | the same |
| `module/web/dist/` | `npm run build` (esbuild) in `module/web` from `module/web/entry.js` and `module/web/icons.js` | `cd module/web && npm run build` |
| `module/web/defaults.json` | `module/tools/measure_defaults.py` (additions only; needs the harness page in Chromium) | `python module/tools/measure_defaults.py` |
| `module/CATALOGUE.md` | `module/tools/gen_catalogue.py` | `python module/tools/gen_catalogue.py` (`--check` exits 1 when stale); `tests/test_catalogue.py` holds it equal |
| `library/contracts.json`, `library/profile.json`, `build/cadre_hmi_base/` | `tools/hmi/parent.py` | `python tools/hmi/parent.py --out build` |
| `build/<project>/` | `tools/hmi/screen.py` | section 4 |

The Gradle outputs (`module/build/`) are not tracked.

### 3.3 Build, Install and Restart

```bash
. /root/.cadre/env.sh
cd module/web && npm ci && npm run build && cd ../..
python module/tools/gen_module_assets.py            # a second run must change nothing
python module/tools/gen_catalogue.py
python module/tools/build_module.py                 # JDK 17 (CADRE_JDK17), offline, unsigned: module/build/CadreOpenBridge.unsigned.modl
python module/tools/install_module.py --file module/build/CadreOpenBridge.unsigned.modl
python module/tools/restart_gateway.py --gateway-url "$CADRE_IGNITION_GATEWAY_URL" --confirm --wait 300
cloud/setup.sh trust-module                          # only after a first install; waits for RUNNING
python module/tools/install_module.py --list         # read only; the installed modules and their digests
```

`build_module.py` reads signing properties from `~/.cadre/signing/signing.properties` when present (the source host) and passes them as
`ORG_GRADLE_PROJECT_<name>` variables, so no secret is on a command line. Without them the built file is
`CadreOpenBridge.unsigned.modl` (the tool once looked for the signed name and failed after a successful unsigned build). `install_module.py`
uploads, accepts the certificate and the EULA, and installs (`POST /modules/upload`, `/modules/certificate`, `/modules/eula`,
`/modules/install`, GF-28). A restart interrupts every project on the gateway: at the source ask the owner first; in the cloud it is allowed.
Each registration logs "Registered N Cadre OpenBridge components"; N must equal the component count (88 at 0.7.0).

### 3.3.1 The Built File in the Repository

A copy of the unsigned 0.7.0 build, the exact file tested at the end of T2, is kept with its SHA-256 in `cloud/release/`
(cloud only, outside the merge back); its `README.md` says how a gateway accepts an unsigned module.

### 3.4 Sizes

Measured on the build of 2026-11-03 12:45 UTC (0.7.0).

| File | Bytes |
|---|---|
| `mounted/js/cadre-ob.js` | 2,753,602 (1,954,229 at 0.6.0; 1,056,955 at 0.4.4; 997,469 at 0.4.3) |
| `mounted/css/cadre-ob.css` | 237,048 |
| `mounted/fonts/NotoSans-OB.ttf` | 625,312 |
| `CadreOpenBridge.unsigned.modl` | 988,279 (775,929 at 0.6.0; 617,070 at 0.4.4; 607,393 at 0.4.3) |

A module's browser resources load on every Perspective page of a project that uses one of its components (GF-29), and the bundle has
grown to 2.75 MB: see 9.

### 3.5 Version History

| Version | Content |
|---|---|
| 0.4.3 | The source's release: 11 components (pump, tank, motor, fan, valves, readout, instrument field, alert lists, canvas zoom) |
| 0.4.4 | T0: filter, generator indicator, automation button (14) |
| 0.5.0 | T1 B0 and B1: module-only mechanism, resistor, damper, switch, capacitor (18) |
| 0.6.0 | T1 complete: 30 elements wrapped (44) |
| 0.6.1 to 0.6.6 | Gateway test builds of T2 batches C1 to F5 (55, 62, 66, 73, 79, 88 components), not released |
| 0.7.0 | T2: the charts and building blocks, all 33 frame components, the two new frames' support (88) |

## 4. Building and Deploying

### 4.1 The Parents

```bash
python tools/hmi/parent.py --out build                                   # cadre_hmi_base; runs G1 on the parent
python tools/hmi/parent.py --out build --name cadre_hmi_base_asm         # a second parent beside it (COB-157)
python tools/hmi/parent.py --out build --deploy                          # import into the gateway
```

`parent.py` writes `library/contracts.json` and `library/profile.json`, and fails if G1 fails. The parent carries the views of every
frame: `Framework/OB/*` (5 views) and `Framework/OBASM/*` (3 views) are inert until a child names them, so the parent has 73 views at 0.7.0
(65 before T2, 70 after the `ob` frame). Children of the older frames are byte-identical to builds before the frame options.

### 4.2 `screen.py` Options

`python tools/hmi/screen.py --project <cadre_hmi_x> --descriptor <file.json> ... [options]`

| Option | Default | Meaning and refusals |
|---|---|---|
| `--project` | required | The child project's name |
| `--descriptor` | none, repeatable | A screen descriptor. Required unless `--component-test` is given with `--tag-root` |
| `--app-name` | `App` | The application name on the top bar |
| `--out` | `<repo>/build` | The build folder |
| `--report` | none | Writes the routes and the gates (key `gates`) as JSON |
| `--deploy` | off | After G0 to G7 pass, ensures the trial, imports the tags and the project. Not reached if any gate or contract fails |
| `--alarm-scope` | `*` | Source path pattern of the alarms the frame shows, for example `*cadre_hmi_wtp*` |
| `--tags-file` | none | An explicit tag model (folder JSON) imported before the project |
| `--devices-file` | none | A device model (`schemas/devices.schema.json`); the sweep and G7 devices read it |
| `--render {stock,module}` | `stock` | `module` draws the kinds of `MODULE_KIND` and the module-only kinds with the module's components. Under `stock`, a module-only kind is refused with one error for each symbol (G7 contract) |
| `--faceplate {openbridge,asm}` | `openbridge` | The project's default faceplate style (COBD-045); a device model may set a device's own |
| `--faceplate-mode {dock,popup}` | `dock` | Where a session opens a faceplate until its pin moves it |
| `--frame {openbridge,asm,ob,obasm}` | `openbridge` | The application frame (section 5). `ob` and `obasm` need `--render module`: the command line prints a message and returns 1, and `build_child` raises `ValueError`. `asm` and `obasm` also check that each `screen.previous` and `screen.next` names a route of the descriptor set |
| `--component-test` | off | Adds the component test page (4.4) |
| `--tag-root [provider]folder` | none | With `--component-test`: the tag folder of the test devices; with no `--descriptor` the page is built alone. Must match `[provider]folder` |
| `--write-descriptor DIR` | none | With `--component-test`: writes `DIR/component-test.json` for G11 and the walk |
| `--write-devices FILE` | none | With `--component-test`: writes the device model of the build |
| `--parent` | `cadre_hmi_base` | The parent the child inherits, built beside it in `--out` |

`--tag-root`, `--write-descriptor` and `--write-devices` without `--component-test` return 1. `--component-test` refuses descriptors that
do not share one `tagRoot`.

### 4.3 Frame, Rendering and Faceplate Combinations

| Frame | `--render stock` | `--render module` | `--faceplate` |
|---|---|---|---|
| `openbridge` | Allowed (the default) | Allowed; the alert menu is the module's `cadre.ob.alertpanel` | `openbridge` or `asm` |
| `asm` | Allowed | Allowed | Either; the component test page uses `asm` with this frame |
| `ob` | Refused | Required | Either |
| `obasm` | Refused | Required | Either; the sample `cadre_hmi_wtpoba` uses `asm` |

Other rules: a module-only kind or a frame component in a descriptor needs `--render module`; the ASM frames (`asm`, `obasm`) read
the descriptors' hierarchy and the `previous` and `next` routes; a project built with `--faceplate asm` is swept with
`faceplates.py --faceplate asm` (6.2).

### 4.4 The Component Test Page

`--component-test` generates a page at route `/component-test` (a level 4 support page) from the library catalogue: every kind with its
features, test devices on memory tags, and, under `--render module`, the sections "Module only" and "Frame components" generated from
`module/components.json`. The test tags are written to `<out>/<project>.component-test-tags.json` and imported into the tag root with
`--deploy`. As built in the cloud (alone, ASM frame and faceplates, module rendering):

```bash
python tools/hmi/screen.py --project cadre_hmi_ctest --component-test --tag-root '[default]cadre_hmi_ctest' \
  --frame asm --faceplate asm --render module --out build \
  --write-descriptor workspace/ctest --write-devices workspace/ctest/devices.json --deploy
```

At 0.7.0 the page has 19 devices and 21 device symbols (G7), 2374 tags at the F1 check, and thousands of components (5822 to 6068 at G8 across
the batches). One G11 sweep of it took 15 min at T0 and about 70 min at T1.

### 4.5 The Samples

| Project | Built with | Descriptors |
|---|---|---|
| `cadre_hmi_sample` | The original pump station sample | `screens/sample-pump-station.json` |
| `cadre_hmi_wtp` | stock | the four `screens/wtp` descriptors (`overview`, `intake`, `filtration`, `disinfection`), `--tags-file screens/wtp/tags.json`, `--alarm-scope "*cadre_hmi_wtp*"` |
| `cadre_hmi_wtpob` | `--render module` | the same four |
| `cadre_hmi_wtpobf` | `--render module --frame ob` | the same four |
| `cadre_hmi_wtpoba` | `--render module --frame obasm --faceplate asm` | the same four |
| `cadre_hmi_ctest` | 4.4 | none |

All the water treatment samples bind the same tags (`[default]cadre_hmi_wtp`), so the plant must be restored (the tag model re-imported)
between gate runs on different projects. The committed `build/cadre_hmi_wtp` and `build/cadre_hmi_wtpob` predate the generator at
`d9f8655`: a rebuild differs from them (the navigation dock's `modal`, the session properties and the screens). The rebuilt files were
deployed and not committed so that the merge back carries no regenerated sample.

### 4.6 Deploy Order

Deploy the parent first, then the children (GF-10); verify in a new browser session, because an open session keeps the old parent's views.
`deploy.py` sets the identity provider after each import (GF-44). A child of a frame or a module component the installed module does not
yet have still imports (GF-72), but its component draws nothing until the module is installed.

## 5. The Four Frames

All four frames share one parent; the option chooses the child's docks and session data. Heights are measured.

Table 2. The frames.

| Part | `openbridge` (default) | `asm` | `ob` | `obasm` |
|---|---|---|---|---|
| Top dock | `Framework/TopBar`, 48 px | `Framework/ASM/Head`, 84 px (bar 48, header 36) | `Framework/OB/Head`, 84 px (bar 48, strip 36) | `Framework/OBASM/Head`, 132 px (bar 48, strip 36, header 48) |
| Top bar | Stock Perspective components | Stock components | `cadre.ob.topbar` (menu, dimming and user buttons, its own alert button and clock) | `cadre.ob.topbar` (plus apps button) |
| Strip | none (alert message in the bar) | alert message in the bar | Cadre crumb (`Framework/Crumb`, node badges) and alert message with ACK (W6) | Cadre crumb (node badges), the ASM search field and alert message with ACK |
| Left dock (320 px, modal) | `Framework/NavMenu` | `ASM/NavDock` (pages and support states) | `Framework/OB/NavDock`: `cadre.ob.navigationmenu` | `Framework/OBASM/NavDock`: `cadre.ob.treenavigation` (pages) or `cadre.ob.navigationmenu` (support) under a Cadre title row and search box |
| Right dock (400 px) | `Framework/SideMenu` (faceplate) | the same | the same | the same |
| Bottom dock | none | `ASM/AlarmBanner` (76 px) | none | `Framework/ASM/AlarmBanner` (76 px) |
| Alert menu | Stock alarm status table; module rendering: `cadre.ob.alertpanel` | the same | `cadre.ob.alertmenu` in the popup `Framework/OB/AlertMenu` | the same popup |
| Bell and count | Stock bell | Stock bell | The top bar's `obc-alert-button` | the same |
| Page header | none | `ASM/PageHeader` (pivot, tabs, previous and next) | none | `cadre.ob.pivotitemgroup` (Mimic, Alarms, Trend) and `cadre.ob.tabrow`; title, level, previous and next stay Cadre nodes |
| Brilliance and user menus | Stock popups | Stock popups | `cadre.ob.brilliancemenu` and `cadre.ob.usermenu` in the popups `Framework/OB/Brilliance` and `UserMenu` | the same popups |
| Needs | nothing | `previous` and `next` routes valid | `--render module` | `--render module` and the ASM keys |

What stays a Cadre view in the two new frames (owner's answers 2 to 4 and the F6b departures): the crumb with its node badges
(`obc-breadcrumb` is wrapped but not used); the alert message strip and its ACK, so G10 F16 keeps its check; the ASM search field
(the module has no search field); the alarm banner and the floating faceplate (no component carries them); the crumb popup (Show and
Areas, because `obc-context-menu-input` draws no priority badge); the page header's title, level and step buttons; the alerts page,
the faceplate dock and popups, the page canvas and toolbar, and the node alarm and trend pages. The silence control is hidden in both:
no Cadre function silences an alarm (owner's answer 4).

Rules held in the data and scripts, never in OpenBridge's code (`CLAUDE.md` rule 7): the hierarchy and counts per node
(`node_counts`), the priority colours by rank (`wiki/13` section 11.1, `cadre.hmi.PRIORITY_STATUS` and `ALERT_TYPE`), ownership by
mode, the faceplate style and pin, and the Confirm row for every command. Wired events are listed in `wiki/04` Tables 7 and 10; every
event calls an existing function (GF-37), so no write path is new.

Code: `tools/hmi/navigation.py` (`FRAMES = ("openbridge", "asm", "ob", "obasm")`, `ASM_FRAMES = ("asm", "obasm")`,
`MODULE_FRAMES = ("ob", "obasm")`), `obframe.py`, `obasm.py`, `framework.py`; the library functions `cadre.hmi.ob_items`,
`cadre.hmi.obasm_items`, and `cadre.hmi.asm_frame` (true for `asm` and `obasm`). Session data: `frame` is `ob` or `obasm`.

## 6. Gates

### 6.1 The Twelve Gates

G0 to G7 run offline inside `screen.py` (before any import); G8 to G11 run against the gateway with Playwright for Python.

| Gate | Checks | Run by |
|---|---|---|
| G0 descriptor | Descriptors (and the device model) validate against their JSON Schemas | `screen.py` |
| G1 registry | Every view of child and parent passes the Ignition-Wiki validator, including the module's property schemas (`module/components.json`, `schemas/*.props.json`) | `screen.py`, `parent.py` |
| G2 references | Embedded view paths, style classes and `var()` tokens resolve | `screen.py` |
| G3 view keys | View-level keys are `custom.` or `params.` (GF-07) | `screen.py` |
| G4 project | Routes, docks and navigation items name existing views; the parent is inheritable | `screen.py` |
| G5 layout | Symbol boxes inside the canvas and not overlapping | `screen.py` |
| G6 flow | The compiled flow expressions equal the reference solver | `screen.py` |
| G7 contract | Unknown kinds and parameters; device binding inside the device's folder; the faceplate contract; the module-only refusal under stock; every command control behind the `custom.can` case | `screen.py` |
| G8 render | In a fresh session: no view error badge, no quality overlay, no trial page, no "View Not Found", components rendered | `tools/compare/capture.py` |
| G9 live flow | Every pipe's rendered state against the solver, for memory tag gates | `tools/compare/live_flow.py` (not applicable to the water treatment sample, whose gates are expression tags) |
| G10 functional | An operator's walk in a new session: navigation, faceplate, commands, setpoint, acknowledge, palette, each checked on the glass; then the generated walk | `tools/compare/functional.py`, `walk.py` |
| G11 faceplates | Every leaf view clicked: each device opens its faceplate with its identifier as title; no overlay or empty body; every tab opened | `tools/compare/faceplates.py` |

A clean render is not a working screen: run G10 or G11 before calling anything functional (`CLAUDE.md` section 5). Never weaken a
gate to pass it.

### 6.2 How to Run Each

```bash
. /root/.cadre/env.sh
python tools/hmi/screen.py ...                                  # G0 to G7 (printed one line each)
python tools/compare/capture.py --base http://localhost:8088/data/perspective/client/<project> --route /component-test --out <dir>      # G8
python tools/compare/live_flow.py --descriptor <file.json> --base <client url> --scenarios 4 --out <dir>                                # G9
python tools/compare/functional.py --base <client url> --out <dir>                                                                      # G10 (signed in when CADRE_TEST_LOGIN is set)
python tools/compare/walk.py plan --descriptor <f> ... --render module --out plan.json                                                  # the generated walk: plan,
python tools/compare/walk.py run --plan plan.json --base <client url> --out <dir>                                                       # then run
python tools/compare/faceplates.py --base <client url> --descriptor <f> --devices-file <devices.json> --faceplate asm --out <dir>        # G11
python tools/compare/glass_gates.py --base <client url> --model <asm model> --build <dir> --gates <list> --out <dir>                    # Level 4 and 5 glass gates
python tools/compare/wtp_suite.py --project cadre_hmi_wtp --project cadre_hmi_wtpob --project cadre_hmi_wtpobf --project cadre_hmi_wtpoba --out <dir>   # G8, G11, G10 and the walk for each project
```

The suite restores the plant (re-imports the tag model, verifies an export of the plant's folder) before and after each gate that
changes it. Exit 1 when any gate fails. `faceplates.py --faceplate` defaults to `openbridge`; judge an ASM project with `--faceplate asm`
or every device reports tab faults that are the style, not the page. Results to date: `wtp_suite.py` on 0.6.0, both renderings, SUITE PASS (50
min: G8 6 of 6, G11 44 of 44, G10 17 of 17 stock and 21 of 21 module, walk PASS in every group, plant restored). The final run on 0.7.0
over the four projects (123 min): `cadre_hmi_wtp`, `cadre_hmi_wtpobf` (`ob`) and `cadre_hmi_wtpoba` (`obasm`) PASS in every gate (G8 6 of 6,
G11 44 of 44, G10 17 of 17 or 21 of 21 signed in, the walk in every group, the plant restored); `cadre_hmi_wtpob` PASS in G8, G11 and G10 and
in every walk group but A-02, an intermittent glass defect then fixed (section 9) and proved by three full walks in a row. G11 on the
component test page on a fresh run: 21 of 21 devices, 274 leaves, nothing missing or unexpected, no fault.

### 6.3 The Glass Variants for Each Frame

`glass.frame_variant(page)` reads the structure of the top dock and answers `obasm` (module top bar and a module pivot group or tab row),
`ob` (module top bar alone) or `default` (the `openbridge` and `asm` frames), kept per page and project. The older frames keep their
selectors exactly (`FrameGlassTests` holds their literal text). The variants (`wiki/13` section 13.11):

| Helper | `openbridge` and `asm` | `ob` and `obasm` |
|---|---|---|
| Bell | `BELL`, the top bar's child `T[0].0:6` (held to `framework.top_bar` by a test) | `BELL_OB`, the host's `obc-alert-button` |
| Bar buttons | Coordinate containers or the last of three SVG icons | `obc-icon-button` in the shadow root of `obc-top-bar`, by label |
| Alert rows and ACK | `obc-alert-list-page-small` | `obc-alert-menu` and its `obc-alert-menu-item` rows |
| Alarm menu close | The popup's first coordinate container | The bell pressed again |
| Sign in and out | Older strategies | `by_bar`, the `obc-button` that carries the caption |
| Navigation entries | Labels of the dock's repeaters | `obc-navigation-item`, `obc-tree-navigation-item` and group labels |
| Palette | The label Night | Two `obc-button`s stepped until `.value` shows the name |
| Page name | Second label of the top dock | `ob`: the bar's `.page-name`; `obasm`: the header title |
| Head rectangle | `MEASURE` (80 to 90 px) | `MEASURE_OBASM` (128 to 136 px) |

`search`, `zoom` and `panels` are ASM gates: on `ob` they are skipped with the reason in `gates.json`.

### 6.4 The Settle Waits Added in the Cloud

| Wait | Where | Rule |
|---|---|---|
| Loading view badges | `capture.settle_badges` (G8) | An embedded view that is still loading shows the same badge (`.view-state-display`) as a failed one. The gate polls every 1 s, at most 60 s; a badge still shown at the cap fails (GF-108). Added after 72 badges on a large page |
| Still leaf count | `faceplates.settled_points` (G11) | Before the sweep, measure the leaves up to 30 times, 1 s apart, until the count holds between two measures. The guard of the sweep is unchanged |
| Frame variant | `glass.frame_variant` | A dock with no module bar and no coordinate container is waited for, about 4 s, once, then taken for an older frame |
| Trial | `walk.settle_trial` (existing) | Probes a fresh session until the project shows, up to 1200 s |
| `--settle S` | `glass_gates.py` | Seconds the glass gates wait after navigation (default 1.0) |

## 7. The Owner's Decisions

### 7.1 Tranche T0 (2026-11-03)

1. Wrap three classes (static symbol, stateful device, shared control), each in a Sonnet 5.5 subagent at medium effort.
2. W3 departs from the brief's wording: the module button replaces the Press of the library's pulse button (W18), so Press asks and Confirm
   calls `cadre.hmi.page_pulse` with its `Administrator` check; no component event writes a tag.

### 7.2 Tranche T1 (`cloud/WRAP-RECIPE.md` section 6)

1. A wrap recipe first, then T1 in batches with a review before T2.
2. The nine line elements are skipped (they overlap the library's pipes and the flow solver, G6).
3. Press then Confirm for every command control; no component event writes a tag.
4. An element without a library kind becomes a module-only kind: contract from `module/components.json`, a "Module only" section on the test
   page, a stock build refuses it with an error.
5. Elements whose events or properties imply a write are wrapped for display and state only; the writes are open items.

### 7.3 Tranche T2 (`cloud/WRAP-RECIPE.md` section 6.1 and `cloud/FRAME-DESIGN.md`, Owner's Answers)

1. A new frame option beside `openbridge` and `asm`, which stay unchanged, with its own gates; existing projects change only when switched.
2. All 33 frame components are wrapped, not only the set the current frame uses.
3. The bars and graphs and the building blocks are module-only kinds, display only.
4. The new frame comes in both variants (`ob` and `obasm`).
5. The frame keeps the Cadre crumb with its node badges (`obc-breadcrumb` wrapped, not used).
6. The frame keeps a Cadre alert strip (the latest alarm and its ACK) beside the OpenBridge bar; G10 F16 keeps its check.
7. The silence control is hidden until a silence function exists.
8. Settled by existing rules, not asked: the five Cadre priorities map onto OpenBridge's levels as `wiki/13` section 11.1 says; G8 on the
   new frames is judged by its own rules and its pictures go to the owner; the frames are built into the existing parent.

## 8. Cost Record

Subagent tokens (the Agent tool's totals) are in `cloud/PROGRESS.md`; the reports hold the tables. T0 wraps 554,947; T1 1,330,557 (30
elements, 44,000 a wrap with the recipe); T2 batches C1, C2, F1 to F7 as logged (for example C1 241,237, C2 210,088, F1 303,036, F2
204,259, F3 248,658, F4 347,175, F5 333,976, F6a 295,458, F6b 263,501, F7 364,709). The main session's spend is read by the owner from the
account's usage page.

## 9. Known Open Items and Limits

Numbers refer to the record they come from.

1. **Fixed during delivery, kept here for the record.** The instrument field identity of G11 (the sweep now titles an instrument's
   faceplate by its tag else its label, as the library does; `faceplates.faceplate_title`) and the intermittent walk row A-02 (the module
   alert panel's toolbar covered the second row's ACK; the glass scrolls the row clear before pressing). Both are in `cloud/REPORT-T2.md`
   section 5.1.
2. **For an operator.** The module alert panel's own toolbar covers the second row's ACK until the list is scrolled (OpenBridge's layout,
   unchanged).
3. **The glass gates that write on the ASM variant** (alarm, ack, banner, and search and zoom with a raised alarm) need an ASM sample with an
   ASM model, which the cloud copy does not have; the read-only ASM gates (menus, panels, search, zoom) pass on `obasm`.
4. **The gauges overflow their boxes.** The 240 by 280 box of the three gauges is not measured; G5 checks boxes, not drawings.
5. **Deferred writes.** The hydraulic valves' `position-selected`, the gauges' setpoints, and the `click` of the heat exchanger, heat pump,
   hydraulic separator, automation readout and transmitter button are carried or shown and never wired. No event of a module-only kind writes a tag.
6. **Not wrapped:** the nine line elements (decision), `obc-automation-input-modal` (four bare slots, a container component), `obc-alert-list`
   (rows are slotted children). The automation readout overlaps the library's `readout` kind (for the owner).
7. **Not carried by a frame component:** the user menu's credential fields (fixed off; the Sign in button calls `system.perspective.login()`),
   the system menu's `eventName` (a helper parameter) and `battery-status`; the menu's `logo` slot and a breadcrumb crumb's icon; the system menu's
   15 events are carried unwired; the modal window carries text and events only and is not used for commands. The per-component list of excluded
   attributes is in `module/CATALOGUE.md`.
8. **Bundle size.** The script is 2.75 MB and loads on every page of a project that uses a module component (GF-29). Splitting by element or loading
   module-only kinds on demand would bound the cost; not measured on a page.
9. **The component test page is large.** A G11 sweep took about 70 min at T1 and grows with the page. The module-only gallery could move to a page
   of its own swept by G8 only.
10. **Cosmetic findings** for the owner's visual review: the toggletips float over the row above them on the test page; the line graph and donut chart
    draw in greys; the page title runs into the first tab on `obasm` ("Plant OverviewMimic"); the brilliance popup's size (320 by 280) is to be
    measured; the F4 top bar's command text ran on from the page name ("Engine roomCommand"), avoided in `ob` by leaving the text empty.
11. **A tree group press only toggles** (measured by F8 on five click points; `wiki/04` section 11.3 holds; GF-113): a node's first page is one
    press further on `obasm` than on `asm`.
12. **The bell and the alert menu count differently, by design**: the bell counts the active alarms (`custom.alarm.count`, `alarm_summary`), the
    menu lists `alarm_list`, which also holds cleared unacknowledged and repeated events; the old frames work the same way (`wiki/13` section
    13.11.6).
13. **Icons.** The icon allow list is the icons imported in `module/web/icons.js`, not the package's 2,104; a navigation item draws an icon only
    where its Cadre icon name is also a bundled icon.
14. **Tools of the source.** `CHROME_PATH` is ignored by the tools; the committed `build/cadre_hmi_wtp` and `build/cadre_hmi_wtpob` predate the generator.
15. **Environment.** The Docker image cache across sessions is untested; a worker restart stops background processes (use `setsid nohup`); the
    trial restarts every two hours; the Playwright pin must match the image's browser build.
16. **GF numbers.** The new gateway facts are numbered GF-99 onward in this copy. If the source has used those numbers since `d9f8655`, renumber at
    the merge and update the citations in this document and `wiki/14-library-configuration.md`.

## 10. Merge Back to the Source Repository

Work on `spike/t0` returns as a diff of the mirrored paths; `cloud/` is cloud only and is not merged. Ranges (commits on the branch):

| Tranche | Range | Report |
|---|---|---|
| T0 | `26f38c8..cc652a9` | `cloud/REPORT-T0.md` section 5 |
| T1 | `cc652a9..c5d29a8` | `cloud/REPORT-T1.md` section 7 |
| T2 | `c5d29a8..4cdda21` (and this documentation) | none yet |

Steps:

1. `git diff 26f38c8 <branch tip> -- . ':!cloud' > library.diff`, then apply to the source repository's `main` (at `d9f8655` plus whatever it has gained).
2. Do not merge generated files textually: regenerate them at the source (3.2): `module/components.json`, the schemas, `mounted/` (script, stylesheet and legal
   notes), `library/contracts.json`, `library/profile.json`, `module/CATALOGUE.md` and `build/cadre_hmi_base`.
3. Mirrored paths changed overall (238 files in all, including the generated ones): `module/` sources (`build.gradle.kts`, `web/entry.js`, `web/icons.js`,
   `web/defaults.json`, `tools/gen_module_assets.py`, `tools/measure_defaults.py`, `tools/build_module.py`, `tools/gen_catalogue.py`, `tools/harness/`,
   `CadreOb.java`, `gradlew` mode); `tools/hmi/` (`screen.py`, `parts.py`, `testbench.py`, `navigation.py`, `navigation_scripts.py`, `obframe.py`,
   `obasm.py`, `parent.py`, `gates.py`); `tools/compare/` (`glass.py`, `glass_gates.py`, `functional.py`, `walk_plan.py`, `capture.py`, `faceplates.py`,
   `wtp_suite.py`); `schemas/screen-descriptor.schema.json`; `tests/` (including `test_catalogue.py`, `test_ob_frame.py`, `test_obasm_frame.py`);
   `wiki/04`, `07`, `12`, `13`, `14` and `index.md`; this file.
4. Regenerate and test: the commands of 3.3, `python tools/hmi/parent.py --out build`, then
   `env -u CADRE_TEST_LOGIN python -m unittest discover -s tests` (1318 in the cloud), then the signed build and its install with the owner's restart, as
   `wiki/12` section 17.6 describes.
5. Not merged: the cloud's `build/cadre_hmi_base_asm`, `build/cadre_hmi_ctest` and the four sample builds rebuilt in the cloud.
6. Check that the new GF numbers do not collide (9 item 16).

## 11. What This Document Does Not Cover

The per-component properties, events and exclusions (see `module/CATALOGUE.md`); the 0.7.0 gateway results (in `cloud/REPORT-T2.md` section 4.3); the Figma file (a design
reference only); the signing certificate and the owner's local gateway, which no cloud session reaches.
