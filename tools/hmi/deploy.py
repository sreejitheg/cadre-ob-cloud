"""Deploy projects to the gateway through ctig's proven REST lane.

The lane (project import as a zip, project names, tag import and export) was proven on
8.3.6 by `F:/repos/Citect-Ignition-Migrator` (`ctig.gateway.rest`, 2026-09-23) and is used
here as a library rather than copied, so there is one implementation of it. The API token
is resolved by ctig (environment, token file, then Windows Credential Manager) and is never
printed or written.

Safety rule (as in Cadre-Sandbox-SCADA's sync tool): a project name must carry the
`cadre_hmi` prefix, so this can never overwrite a project that is not ours.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

CTIG_SRC = Path(os.environ.get("CTIG_SRC", "F:/repos/Citect-Ignition-Migrator/src"))
GATEWAY = os.environ.get("CADRE_IGNITION_GATEWAY_URL", "http://localhost:8088")
ACCOUNTS = ["ignition_gateway::Demo-Citect-Ignition-2.0", "ignition_gateway::Cadre",
            "ignition_gateway::default"]
PREFIX = "cadre_hmi"


def _gateway():
    if str(CTIG_SRC) not in sys.path:
        sys.path.insert(0, str(CTIG_SRC))
    from ctig.gateway.rest import Gateway, resolve_token  # noqa: E402
    token, source = resolve_token(ACCOUNTS)
    if not token:
        raise SystemExit("no gateway API token (environment, token file or credential manager)")
    return Gateway(GATEWAY, token), source


# The identity provider a session signs in with (command security, COB-063). The gateway carries one,
# "default", an internal provider over the user source "default" (read 2026-10-09, wiki page 07 GF-43); a
# project names it through `PUT /data/api/v1/projects/{name}` (the gateway's own OpenAPI document,
# `/openapi.json`). The PUT writes the project's global properties, a resource `ignition/global-props`
# (`data.bin`) that our generated projects do not carry, so every import deletes it and the project loses
# its provider at runtime while the projects list still names it; and the PUT replaces every property it is
# not given (no parent, not inheritable, no title). Measured on 2026-10-09 (GF-44): the provider is set
# after every import, with the project's own `project.json` in the body. The owner agreed on 2026-10-09
# that our projects name the provider.
IDENTITY_PROVIDER = "default"


def set_identity_provider(project, idp: str = IDENTITY_PROVIDER) -> dict:
    """Name the identity provider of one of our projects, after its import; nothing else on the
    gateway changes, and the project keeps its own properties (GF-44)."""
    import json
    if not project.name.startswith(PREFIX):
        raise SystemExit(f"refusing to change {project.name!r}: it lacks the {PREFIX!r} prefix")
    gw, _ = _gateway()
    body = dict(json.loads(project.files["project.json"]), identityProvider=idp)
    code, data = gw._req("PUT", f"/data/api/v1/projects/{project.name}", body=json.dumps(body).encode(),
                         ctype="application/json")
    return {"project": project.name, "identityProvider": idp, "status": code}


def project_settings(name: str) -> dict:
    """The gateway's record of one project (identity provider, parent, inheritable)."""
    import json
    gw, _ = _gateway()
    code, data = gw._req("GET", "/data/api/v1/projects/list")
    for p in json.loads(data).get("items", []):
        if p.get("name") == name:
            return {k: p.get(k) for k in ("name", "parent", "inheritable", "identityProvider", "userSource")}
    return {}


def import_project(project) -> dict:
    if not project.name.startswith(PREFIX):
        raise SystemExit(f"refusing to import {project.name!r}: it lacks the {PREFIX!r} prefix")
    gw, source = _gateway()
    body = project.zip_bytes()
    reply = gw.project_import(project.name, body)
    names = gw.project_names()
    present = project.name in [n if isinstance(n, str) else n.get("name") for n in names]
    idp = set_identity_provider(project)
    return {"project": project.name, "bytes": len(body), "token_source": source,
            "reply": reply[:200], "listed": present, "identityProvider": idp["status"]}


def trial(reset: bool = False) -> dict:
    """Read, or reset, the gateway's two hour trial timer. `POST /data/api/v1/trial` resets it
    with the API token alone, no web login (measured 2026-10-07, wiki page 07 GF-03).
    IGW:28-gateway-development-surface lists the route under `LicensingRoutes`."""
    import json
    gw, _ = _gateway()
    code, data = gw._req("POST" if reset else "GET", "/data/api/v1/trial",
                         body=b"{}" if reset else None,
                         ctype="application/json" if reset else None)
    out = json.loads(data) if code == 200 else {"status": code}
    return {k: out.get(k) for k in ("licenseMode", "trialSecondsLeft", "expired", "status") if k in out}


# the modules a migrated page needs: Perspective, and this library's module (COB-196)
NEEDED_MODULES = ("com.inductiveautomation.perspective", "cadre.hmi.ob")
LICENSED_STATES = ("activated", "free")


def modules() -> object:
    """The gateway's module list, `GET /data/api/v1/modules/healthy` (IGW:28 `ModuleRoutes`), or
    `{"status": code}` when the read fails."""
    import json
    gw, _ = _gateway()
    code, data = gw._req("GET", "/data/api/v1/modules/healthy")
    return json.loads(data) if code == 200 else {"status": code}


def module_states(body: object) -> dict:
    """Each module's licence state, lower case, under its id and its name (lower case). The answer
    of the real 8.3.6 gateway (2026-10-30) is `{"items": [...], "metadata": {...}}`, each module
    with `state` (`ACTIVE`, `INACTIVE`) and `licenseState` (`Activated`, `Free`, `Trial`, `n/a`
    for a disabled module); a module that is not `ACTIVE` reads `inactive` (COB-197)."""
    items = body.get("items") if isinstance(body, dict) else None
    states = {}
    for module in items if isinstance(items, list) else []:
        if not isinstance(module, dict) or not isinstance(module.get("licenseState"), str):
            continue
        state = module["licenseState"].strip().lower()
        if str(module.get("state") or "").strip().lower() != "active":
            state = "inactive"
        for key in ("id", "name"):
            if isinstance(module.get(key), str) and module[key]:
                states[module[key].strip().lower()] = state
    return states


def licensed(t: dict, needed=NEEDED_MODULES, read=None) -> bool:
    """Whether a gateway whose trial read is `t` needs no trial for `needed`: `licenseMode`
    Activated and every needed module active and activated or free. The modules are read only
    then; a read that fails, or a needed module inactive, on trial or absent, keeps the trial rules
    (COB-196, COB-197)."""
    if str(t.get("licenseMode") or "").strip().lower() != "activated":
        return False
    try:
        body = (read or modules)()
    except Exception:  # any fault keeps the trial rules
        return False
    states = module_states(body)
    return all(states.get(m.strip().lower()) in LICENSED_STATES for m in needed)


def ensure_trial(min_seconds: int = 900, wait: bool = True, needed=NEEDED_MODULES) -> dict:
    """Make sure at least `min_seconds` of trial remain, so a verification run never measures the
    'Trial Expired' page instead of the view. The gateway refuses a reset with 403 while the
    trial is still running and accepts it once the trial has expired (GF-33), so with fewer than
    `min_seconds` left this waits for the expiry, then resets. A gateway licensed for the modules
    `needed` (`licensed`) needs no trial: it is left alone, with no wait and no reset (COB-196)."""
    import time
    t = trial()
    if t.get("status") is not None:          # the read itself failed: retry once
        time.sleep(2)
        t = trial()
    if licensed(t, needed):
        return {**t, "licensed": True, "rule": "licensed: " + ", ".join(needed) + " active and activated or free"}
    left = t.get("trialSecondsLeft") or 0
    if not t.get("expired") and left >= min_seconds:
        return t
    r = trial(reset=True)
    if r.get("status") == 403 and wait and not t.get("expired"):
        print(f"trial: {left} s left and the gateway refuses a reset before expiry (GF-33); waiting", flush=True)
        deadline = time.time() + left + 120
        while time.time() < deadline:
            time.sleep(10)
            t = trial()
            if t.get("expired") or (t.get("trialSecondsLeft") or 1) <= 0:
                break
        r = trial(reset=True)
        if r.get("status") is not None:
            time.sleep(5)
            r = trial(reset=True)
    out = trial()
    out["reset"] = True
    out["reset_reply"] = r.get("status", 200)
    if out.get("expired") or (out.get("trialSecondsLeft") or 0) < min_seconds:
        raise SystemExit(f"trial could not be reset: {out}")
    return out


def import_tags(provider: str, path: str, doc: dict) -> dict:
    gw, _ = _gateway()
    return gw.tags_import(provider, path, doc)


def export_tags(provider: str, path: str) -> dict:
    gw, _ = _gateway()
    return gw.tags_export(provider, path)
