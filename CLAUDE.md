# Cadre OpenBridge library, cloud copy: operating manual (read every session)

This repository is a copy of the library repository Cadre-Sandbox-OpenBridge (its `main` at `d9f8655`) for
work in Claude Code cloud sessions. It holds the Perspective parent project generator, the component library,
the Cadre OpenBridge module (`module/`), the gates, the tests and the wiki. The records of the source repository
(status, register, decisions, documents, memory) are not copied; this repository has its own record under
`cloud/`. Work done here returns to the source repository as a diff of the mirrored paths, so keep each change
to a mirrored path small, portable and mergeable, and put anything that exists only for the cloud under `cloud/`.

## 1. Session Rituals

- **Start:** read this file, then `cloud/SPIKE-T0.md` (or the brief the session names), then
  `cloud/PROGRESS.md` if it exists.
- **During:** after each step, append a dated line to `cloud/PROGRESS.md` (what was done, test counts, tokens
  where known). A usage limit or an expired environment can stop the session without a report.
- **End:** write the brief's report, commit by explicit path, push the session's branch. Never push to `main`.

## 2. Non-negotiables

1. **Recreate, never reuse (COBD-002).** No OpenStudio module, demo project file or documentation prose enters
   a tracked file. Interface facts are recorded in our own words.
2. **OpenBridge material comes only from the Apache-2.0 pin** (`@oicl/openbridge-webcomponents`
   2.0.0-next.155, commit `2c98dda1`, COBD-003), with attribution in `NOTICE`. Releases from 2026-09-17 are
   AGPL-3.0: never change the version in `module/web/package.json` or `package-lock.json`, install with
   `npm ci` only, and never copy code or components from the upstream repository's later commits. The
   OpenBridge 6.1 Figma file (CC BY 4.0) is a design reference only: no copied assets.
3. **No Perspective component from recall.** Every type, prop, enumeration, binding shape and position key
   traces to the Ignition-Wiki schemas (vendored in `cloud/vendor/ignition-wiki/`, gate G1 enforces it) or to
   a measured gateway fact in `wiki/07`.
4. **Never hand edit a generated file** under `build/` or `library/contracts.json`; change the generator and
   rebuild.
5. **Never weaken a check to pass it.** A failing gate, test or schema is fixed at its cause or reported. No
   switched-off gap, stripped sample, edited gate, loosened schema or skipped test counts as a pass.
6. **Secrets never enter a file of this repository.** The cloud gateway's admin password and API token are
   generated at run time and kept under `/root/.cadre/` (outside the repository), never printed in full.
7. **The ASM rules go in the wrapper and the library tokens, never in OpenBridge's code.** The rules are
   `wiki/13` sections 10 to 12 (ownership by mode, faceplate style, the pin, priority colours, the generator)
   and `wiki/04` sections 7 to 9 (hierarchy, counts, breadcrumb, the ASM frame).

## 3. The Cloud Gateway

The session runs its own Ignition 8.3.6 gateway in Docker (official image `inductiveautomation/ignition`),
in trial mode. The owner accepts the Ignition licence agreement through the environment variable
`ACCEPT_IGNITION_EULA=Y`, which the owner sets on the cloud environment; never set or accept it on the owner's
behalf, and stop if it is absent. This gateway is throwaway and unrelated to the owner's local gateway:
installing a module, restarting the container and recreating it are allowed here without asking. The owner's
local gateway is never reached from here. Project names still start `cadre_hmi`.

## 4. Paths from the Source Repository

The tools default to Windows paths of the owner's host. In the cloud they are overridden by environment
variables, which keep the Windows defaults so the source repository behaves as before:

| Variable | Points to |
|---|---|
| `CTIG_SRC` | `cloud/vendor` (ctig's gateway REST client, `ctig/gateway/rest.py`, copied unchanged from ctig `046a3a5`) |
| `CTIG_IGNITION_TOKEN_FILE` | `/root/.cadre/ignition-token` |
| `CADRE_IGNITION_GATEWAY_URL` | `http://localhost:8088` |
| `CADRE_TEST_LOGIN` | `/root/.cadre/test-login.properties` (the cloud gateway's own test user) |
| `CADRE_PIL_PYTHON` | the Python that has Pillow |
| `CADRE_IGNITION_WIKI` | `cloud/vendor/ignition-wiki` (validator and schemas copied unchanged from Ignition-Wiki `62939dc`); `tools/hmi/gates.py` does not read it yet: adding it is the first portability change |

## 5. Building

```bash
python tools/hmi/parent.py --out build                # the parent; add --name cadre_hmi_base_asm for the ASM parent
python tools/hmi/screen.py --project <cadre_hmi_x> --descriptor <file.json> --app-name <Name> --out build --deploy
python -m unittest discover -s tests                   # last recorded at the source: 671 passing (2026-10-26)
cd module/web && npm ci && npm run build && cd ../.. && python module/tools/gen_module_assets.py
python module/tools/build_module.py                    # JDK 17; unsigned here (no signing properties)
python module/tools/install_module.py
```

The gates (wiki/08 section 5): G0 to G7 run offline inside `screen.py`; G8 render (`tools/compare/capture.py`),
G9 live flow, G10 functional walk and G11 faceplate sweep (`tools/compare/faceplates.py`) run against the
gateway with Playwright for Python, using the installed Chrome (`CHROME_PATH`). A clean render is not a working
screen: run G10 or G11 before calling anything functional.

## 6. Gateway Rules Learned at the Source (wiki/07)

- `POST /data/api/v1/trial` resets the trial only after it has expired (GF-03, GF-33); here, recreating the
  container is the simpler reset.
- After importing the parent, re-import the children and verify in a new session (GF-10).
- View-level `propConfig` keys are `custom.` or `params.` only (GF-07). Flex children hide with
  `position.display` (GF-08). View paths are case sensitive (GF-22).
- Every write path needs the gateway's `Administrator` role (COBD-024).
- Every project names the identity provider `default`, set by `deploy.py` after each import (GF-44).

## 7. Models and Writing

The main session orchestrates; each wrap runs in a subagent on Sonnet 5.5 at medium effort unless the brief
says otherwise, and its reported token total is recorded in `cloud/PROGRESS.md`. Reports and wiki pages are
formal and impersonal, Australian English, numbered sections, noun-phrase headings, no em or en dashes and no
arrow characters.
