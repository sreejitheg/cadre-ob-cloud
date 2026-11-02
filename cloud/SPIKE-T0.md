# Spike T0: the Library Build in a Cloud Session

Brief for the first cloud session. Branch: `spike/t0`. Stop at the end of section 5 and report; tranches T1
and T2 start only on the owner's word after reading the report.

## 1. Purpose

The owner intends to build the OpenBridge automation set and the parent framework once, in cloud sessions, so
that the screen migration workflow uses a tested library instead of building gaps during a run. The spike
answers three questions before any money is committed to that build:

1. Can a cloud session build, install and prove the module and the parent on its own Ignition gateway?
2. What does one wrap cost, in tokens and time, for each of three classes of OpenBridge element?
3. What do tranches T1 and T2 (about 75 wraps with the framework) cost by extrapolation?

## 2. Budget and Stop Rules

- Target: about 0.5 million tokens. Hard stop: if the session's spend passes about 1.2 million tokens, or the
  environment (section 3) is not working after about two hours of effort, stop, write the report with what is
  known and push.
- Run each wrap (section 4) in its own subagent on Sonnet 5.5 at medium effort, and record the token total and
  duration the Agent tool reports for it in `cloud/PROGRESS.md`. The main session's own spend is read by the
  owner from the account's usage page; estimate it in the report from the number and size of its turns.
- Do not start a fourth wrap, a tranche or any refactoring beyond what the steps below need.

## 3. Environment

Each step records its outcome in `cloud/PROGRESS.md`; each unknown answered is written into the report.

1. **Tools.** Python 3 with `pip install playwright pillow` (use the installed Chrome through `CHROME_PATH`, do
   not download browsers if the network refuses it); JDK 17 for Gradle (the image has JDK 21; install 17 from
   the Ubuntu packages if the build needs it); `npm ci` in `module/web`.
2. **Portability.** Add `CADRE_IGNITION_WIKI` to `tools/hmi/gates.py` with the present Windows path as the
   default; set the variables of `CLAUDE.md` section 4. `module/tools/build_module.py` runs Gradle with
   `--offline`: the first build needs the network once (Inductive Automation's Maven repository,
   `nexus.inductiveautomation.com`). Make any further path or launch change the same way: an environment
   variable with the present default. List every such change in the report.
3. **Baseline offline.** `python -m unittest discover -s tests`: record passed, failed and skipped, and for each
   failure whether it is environmental (a Windows path, a missing service) or real. The source host's last
   recorded count is 671 passing (2026-10-26); later commits may have added tests.
4. **Gateway.** Stop if `ACCEPT_IGNITION_EULA` is not `Y` in the environment. Run
   `inductiveautomation/ignition:8.3.6` in Docker on port 8088, commissioned from environment variables (read
   the image's documentation for the 8.3 variable names), with unsigned modules allowed (find the 8.3 setting
   and record it). Create an admin user and a gateway API token with the write access `deploy.py` needs; find
   how 8.3 creates an API token without the web interface (the configuration files, a REST route or the web
   interface driven by Playwright) and record the way that worked. Create the test user of
   `CADRE_TEST_LOGIN` with the `Administrator` role. Secrets stay under `/root/.cadre/`.
5. **Baseline on the gateway.** Build the module (0.4.3) unsigned and install it. Build and deploy the parent
   `cadre_hmi_base`, the ASM parent `cadre_hmi_base_asm`, and the samples `cadre_hmi_wtp` and
   `cadre_hmi_wtpob`. Run G0 to G7, then G8 and G11 on `cadre_hmi_wtpob` (as `tools/compare/wtp_suite.py`
   does), and the component test page (`screen.py --component-test`) with G8 and G11. Record each result.
6. **Setup script.** Write `cloud/setup.sh`: what a fresh environment needs before the first command (packages,
   the image pull, `npm ci`), idempotent and under five minutes, so the owner can paste it into the cloud
   environment's setup script and later sessions start warm.

## 4. Three Wraps

Read `wiki/12` (the module spike), `module/components.json`, `module/web/entry.js`, the properties schemas in
`module/common/src/main/resources/schemas/` and the module's tests first; a wrap follows the pattern of the
existing eleven. Take each element's attributes, properties, events and states from
`module/web/node_modules/@oicl/openbridge-webcomponents/custom-elements.json` (the pinned release).

| Wrap | Element | Class | Done when |
|---|---|---|---|
| W1 | `obc-filter` | Static symbol | Wrapped, schema, tests, on the component test page, G8 clean |
| W2 | `obc-indicator-generator` | Stateful device | As W1, plus its states bound to the generator kind's members (wiki 13 section 12), ASM priority colours (section 11.1), the faceplate opens (G11) |
| W3 | `obc-automation-button` | Shared control | As W1, plus a command write through the existing write path with the `Administrator` role, refused when signed out |

If an element is missing from the pinned release or cannot carry what its row needs, record why and stop that
wrap; do not substitute another element without recording it. Build the module once for all three (0.4.4),
install it once, rerun the component test page and G8 and G11, then the full offline suite.

## 5. Report

Write `cloud/REPORT-T0.md` (house register, numbered sections) and push branch `spike/t0`:

1. The environment: what worked, the unknowns of section 3 with their answers, every portability change.
2. The baseline: tests and gates, with the environmental failures separated from real ones.
3. The wraps: for each, the files changed, the gates passed, the tokens and minutes, what the ASM rules needed.
4. The extrapolation: the remaining automation elements of the pinned release, the bars, building blocks and
   frame components, sorted into the three classes, with a token and time estimate for T1 and T2 from the
   measured cost per class, and the risks found.
5. The merge back: the list of mirrored paths changed, so the owner's local session can apply the diff to the
   source repository between workflow runs.
