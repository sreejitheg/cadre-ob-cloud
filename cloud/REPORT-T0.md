# Spike T0 Report: Stop at the Licence Check

Session of 2026-11-02, branch `spike/t0` from `main` at `26f38c8`. This is a stop report under the task's first
stop rule. It is superseded by the full report when the spike is rerun.

## 1. The Environment

1.1 **Licence acceptance.** The variable `ACCEPT_IGNITION_EULA` is not present in the session environment. It is
absent from the shell environment and from the environment of the session's own processes, and no profile file
defines it. The task requires the session to stop with a short report in that case and never to set the
variable, so no step of section 3 was started.

1.2 **Observations made while stopping.** A read-only probe found the following; nothing was installed or
started.

| Item | Finding |
|---|---|
| Docker | CLI 29.9.2 and `/usr/bin/dockerd` installed; no daemon running (`/var/run/docker.sock` absent) |
| Java | OpenJDK 21.0.12.1 only; JDK 17 not installed |
| Python | 3.13.18; Playwright and Pillow not checked |
| Node | 22.23.4 with npm 10.9.9 |
| Browser | Playwright Chromium 1243 under `/opt/pw-browsers` |

1.3 **Conditions for a rerun.**

1. The owner sets `ACCEPT_IGNITION_EULA=Y` as an environment variable of the cloud environment (the environment
   menu in the session's title bar, then Edit). A new session reads it at start.
2. The gateway needs a running Docker daemon. Whether `dockerd` starts inside this container, and whether the
   network policy admits Docker Hub (`inductiveautomation/ignition:8.3.6`) and `nexus.inductiveautomation.com`,
   remains unknown; the rerun answers both in section 3, and `cloud/setup.sh` records the result.

1.4 **Portability changes.** None.

## 2. The Baseline

Not run. The offline test suite and the gates were not started.

## 3. The Wraps

Not started: W1 `obc-filter`, W2 `obc-indicator-generator` and W3 `obc-automation-button` have no files, gates
or measurements. No subagent was launched, so no wrap tokens or minutes exist. The main session's spend is small
(about ten short turns over the session's standing context); the owner reads the exact figure from the account's
usage page.

## 4. The Extrapolation

No cost per class was measured, so the feasibility review's estimate for T1 and T2 (7 to 14 million tokens)
stands unchanged and unverified.

## 5. The Merge Back

No mirrored path changed. The session added only `cloud/PROGRESS.md` and `cloud/REPORT-T0.md`, which exist only
for the cloud and are not merged into the source repository.
