"""Restart the Ignition gateway through its REST API, after an installed module asks for one.

Installing or upgrading a module leaves the gateway with a pending restart task (wiki page 07, GF-28:
`GET /data/api/v1/restart-tasks/pending` lists "Module Installed" or "Module Upgraded"), and
`POST /data/api/v1/restart-tasks/restart?confirm=true` restarts it. A restart interrupts every
project on the gateway, so the tool lists the pending tasks and stops unless `--confirm` is given:
ask the owner first (CLAUDE.md, "The module").

The gateway address is an argument. The API token is resolved the way `tools/hmi/deploy.py`
resolves it, by ctig (environment, token file, then Windows Credential Manager), and is never
printed or written. With `--wait N` the tool then polls `GET /StatusPing` until the gateway has
gone down and answers `RUNNING` again, for at most N seconds.

Usage:  python module/tools/restart_gateway.py --gateway-url http://localhost:8088 [--confirm] [--wait 300]
Exit 0 on success (or when nothing was asked to restart), 1 on a fault or a timeout.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / "tools"))
from hmi import deploy  # noqa: E402

PENDING = "/data/api/v1/restart-tasks/pending"
RESTART = "/data/api/v1/restart-tasks/restart"
PING = "/StatusPing"
DEFAULT_POLL_S = 5.0


def gateway(base_url: str):
    """A ctig `Gateway` for `base_url` and the token source (a description, never the token)."""
    parts = urllib.parse.urlsplit(base_url)
    if parts.scheme not in ("http", "https") or not parts.netloc or parts.query or parts.fragment:
        raise SystemExit(f"{base_url!r} is not a gateway base URL such as http://localhost:8088")
    if str(deploy.CTIG_SRC) not in sys.path:
        sys.path.insert(0, str(deploy.CTIG_SRC))
    from ctig.gateway.rest import Gateway, resolve_token  # noqa: E402

    token, source = resolve_token(deploy.ACCOUNTS)
    if not token:
        raise SystemExit("no gateway API token (environment, token file or credential manager)")
    return Gateway(base_url, token, timeout=30.0), source


def ping(gw) -> str | None:
    """The body of `/StatusPing`, or None when the gateway does not answer it (it is down)."""
    try:
        code, data = gw._req("GET", PING)
    except Exception:  # a refused connection while the gateway restarts
        return None
    return data.decode("utf-8", "replace").strip() if code == 200 else None


def wait_for_restart(gw, seconds: float, poll_s: float) -> bool:
    """True when the gateway went down and came back `RUNNING` within `seconds`. A gateway that
    never stops answering is not taken for a restarted one."""
    deadline = time.monotonic() + seconds
    went_down = False
    while time.monotonic() < deadline:
        state = ping(gw)
        if state is None:
            went_down = True
        elif went_down and state == "RUNNING":
            return True
        time.sleep(poll_s)
    return False


def pending_tasks(gw) -> list:
    code, data = gw._req("GET", PENDING)
    if code != 200:
        raise SystemExit(f"restart-tasks/pending answered HTTP {code}")
    document = json.loads(data.decode("utf-8", "replace") or "[]")
    if isinstance(document, dict):
        document = next((v for v in document.values() if isinstance(v, list)), [])
    return document if isinstance(document, list) else []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gateway-url", required=True, help="the gateway base URL, e.g. http://localhost:8088")
    ap.add_argument("--confirm", action="store_true", help="request the restart (without it, only list)")
    ap.add_argument("--wait", type=float, default=0.0, help="seconds to wait for the gateway to be RUNNING again")
    ap.add_argument("--poll", type=float, default=DEFAULT_POLL_S, help="seconds between StatusPing polls")
    a = ap.parse_args(argv)
    gw, source = gateway(a.gateway_url)
    print("token source", source)
    tasks = pending_tasks(gw)
    print("pending", json.dumps(tasks)[:400])
    if not a.confirm:
        print("not restarting: pass --confirm after the owner approves")
        return 0
    code, data = gw._req("POST", RESTART, query={"confirm": "true"})
    print("restart requested", time.strftime("%H:%M:%S UTC", time.gmtime()), "HTTP", code)
    if code != 200:
        print(data.decode("utf-8", "replace")[:300])
        return 1
    if a.wait > 0:
        if not wait_for_restart(gw, a.wait, a.poll):
            print(f"the gateway was not RUNNING again within {a.wait:g} s")
            return 1
        print("gateway RUNNING")
    return 0


if __name__ == "__main__":
    sys.exit(main())
