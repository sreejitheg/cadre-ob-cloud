"""Install the Cadre OpenBridge module on the gateway through its REST API.

The flow is the gateway's own (ModuleInstallRoutes of gateway-8.3.6.jar, read with javap):
upload the file (`POST /data/api/v1/modules/upload?fileName=`), accept the module's certificate
and EULA (`POST /modules/certificate?moduleId=`, `POST /modules/eula?moduleId=`), then install
(`POST /modules/install?moduleId=`). Uninstalling (`POST /modules/uninstall`) takes effect at the
next gateway restart.

Usage:  python module/tools/install_module.py [--file module/build/CadreOpenBridge.modl]
        python module/tools/install_module.py --list [--id MODULE_ID] [--data-dir DIR]

`--list` is read only (GET requests and file reads; nothing is uploaded, installed, enabled or written, and no
trial is touched). It prints one JSON document, `cadre-hmi-installed-modules/1`, to standard output:

    {"schema": ..., "gateway": URL, "modules_json": path or null, "modules": [
        {"id", "name", "version", "state", "license_state",       # as the gateway's module list answers
         "file", "bytes", "sha256", "file_version", "file_matches_version", "note"}]}

The gateway's module list (`GET /data/api/v1/modules/healthy`) names each module and its version and carries no file
digest. The digest is that of the file the gateway holds the module in: `<gateway data folder>/modules.json`, the gateway's
own record, names it (`filename`), and the tool hashes that file with SHA-256 (the gateway's data folder is `--data-dir`,
else `CADRE_IGNITION_DATA`, else the parent of `ignition.projects_dir` in `~/.cadre/gateway.json`). Where the folder
cannot be read (a gateway on another host) `file`, `bytes` and `sha256` are null and `note` says why. `file_version` is
the version in the file's own `module.xml`; `file_matches_version` is true when the two agree (`0.4.2 (b0)` and `0.4.2` do).
Exit 0 listed; 1 the gateway did not answer the list.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / "tools"))
from hmi import deploy  # noqa: E402

MODULE_ID = "cadre.hmi.ob"
API = "/data/api/v1/modules"


def call(gw, method, path, body=None, ctype=None):
    code, data = gw._req(method, path, body=body, ctype=ctype)
    text = data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)
    return code, text


def module_items(text: str) -> list[dict]:
    """The modules of the gateway's list (`GET /modules/healthy`): the answer is a list, or an object whose list holds them."""
    data = json.loads(text)
    items = data if isinstance(data, list) else next((v for v in data.values() if isinstance(v, list)), [])
    return [m for m in items if isinstance(m, dict)]


def module_state(gw) -> str | None:
    code, text = call(gw, "GET", f"{API}/healthy")
    items = module_items(text) if code == 200 else []
    return next((m.get("state") for m in items if m.get("id") == MODULE_ID), None)


# ---- --list: the installed modules, read only ---------------------------------------------------------------------
LIST_SCHEMA = "cadre-hmi-installed-modules/1"


def data_dir_of(explicit: str | None = None) -> Path | None:
    """The gateway's data folder: the argument, else `CADRE_IGNITION_DATA`, else the parent of `ignition.projects_dir` in
    `~/.cadre/gateway.json` (read for that one key). None where none of them names a folder."""
    for given in (explicit, os.environ.get("CADRE_IGNITION_DATA")):
        if given:
            return Path(given)
    try:
        cfg = json.loads((Path.home() / ".cadre" / "gateway.json").read_text(encoding="utf-8"))
        projects = (cfg.get("ignition") or {}).get("projects_dir")
    except (OSError, ValueError, AttributeError):
        projects = None
    return Path(projects).parent if projects else None


def file_facts(path: Path) -> dict:
    """The size and SHA-256 of an installed module file, and the version its own `module.xml` names."""
    data = path.read_bytes()
    version = None
    try:
        with zipfile.ZipFile(path) as z:
            found = re.search(r"<version>([^<]+)</version>", z.read("module.xml").decode("utf-8", "replace"))
            version = found.group(1).strip() if found else None
    except (zipfile.BadZipFile, KeyError, OSError):
        pass
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "file_version": version}


def versions_agree(gateway: str | None, in_file: str | None) -> bool:
    """The gateway writes a version as `0.4.2 (b0)` or `7.3.6 (b2026042713)` where the file's `module.xml` has `0.4.2` or
    `7.3.6.2026042713`: the file's version is the gateway's number alone, or the number and the build joined by a dot."""
    if not gateway or not in_file:
        return False
    found = re.fullmatch(r"(?P<number>[^ ]+)(?: [(]b(?P<build>[^)]*)[)])?", gateway.strip())
    if not found:
        return gateway.strip() == in_file
    number, build = found.group("number"), found.group("build")
    return in_file == number or (build is not None and in_file == f"{number}.{build}")


def list_modules(gw, data_dir: Path | None = None, only: str | None = None) -> dict:
    """The installed modules: name, version and state as the gateway's list answers, and the digest of the file the gateway
    holds each module in (its `modules.json`). Read only: one GET, and file reads."""
    code, text = call(gw, "GET", f"{API}/healthy")
    if code != 200:
        raise RuntimeError(f"the gateway answered {code} to GET {API}/healthy")
    record, record_path, why = {}, None, "no gateway data folder is known (--data-dir, CADRE_IGNITION_DATA)"
    if data_dir is not None:
        record_path = data_dir / "modules.json"
        try:
            record, why = json.loads(record_path.read_text(encoding="utf-8")), None
        except (OSError, ValueError) as e:
            record, why = {}, f"{record_path} could not be read: {type(e).__name__}"
    modules = []
    for m in module_items(text):
        if only and m.get("id") != only:
            continue
        row = {"id": m.get("id"), "name": m.get("name"), "version": m.get("version"), "state": m.get("state"),
               "license_state": m.get("licenseState"), "file": None, "bytes": None, "sha256": None,
               "file_version": None, "file_matches_version": None, "note": why}
        name = (record.get(m.get("id")) or {}).get("filename") if isinstance(record, dict) else None
        if why is None and not name:
            row["note"] = "the gateway's modules.json names no file for this module"
        elif name:
            path = Path(name)
            try:
                row.update(file_facts(path), file=str(path), note=None)
                row["file_matches_version"] = versions_agree(row["version"], row["file_version"])
            except OSError as e:
                row.update(file=str(path), note=f"{path.name} could not be read: {type(e).__name__}")
        modules.append(row)
    return {"schema": LIST_SCHEMA, "gateway": getattr(gw, "base_url", None) or getattr(gw, "base", None),
            "modules_json": str(record_path) if record_path else None, "modules": modules}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(HERE / "build" / "CadreOpenBridge.modl"))
    ap.add_argument("--list", action="store_true", help="read only: list the installed modules with version and file digest")
    ap.add_argument("--id", default=None, help="with --list: only this module id")
    ap.add_argument("--data-dir", default=None, help="with --list: the gateway's data folder (holds modules.json)")
    a = ap.parse_args()
    if a.list:
        try:
            gw, _ = deploy._gateway()
            listing = list_modules(gw, data_dir_of(a.data_dir), a.id)
        except Exception as e:   # the gateway is down, or answered the list with an error
            print(f"install_module: --list: {type(e).__name__}: {str(e)[:300]}", file=sys.stderr)
            return 1
        print(json.dumps(listing, indent=1))
        return 0
    f = Path(a.file)
    gw, _ = deploy._gateway()
    print("trial", deploy.ensure_trial())
    code, text = call(gw, "POST", f"{API}/upload?fileName={f.name}", body=f.read_bytes(),
                      ctype="application/octet-stream")
    print("upload", code, text[:300])
    code, text = call(gw, "GET", f"{API}/certificate?moduleId={MODULE_ID}")
    print("certificate", code, text[:300])
    code, text = call(gw, "POST", f"{API}/certificate?moduleId={MODULE_ID}")
    print("accept certificate", code, text[:200])
    code, text = call(gw, "POST", f"{API}/eula?moduleId={MODULE_ID}")
    print("accept eula", code, text[:200])
    code, text = call(gw, "POST", f"{API}/install?moduleId={MODULE_ID}")
    print("install", code, text[:300])
    # An installed module is INACTIVE until enabled (measured: /modules/healthy state INACTIVE).
    code, text = call(gw, "PUT", f"{API}/toggle-state", body=json.dumps({"enable": [MODULE_ID], "disable": []}).encode(),
                      ctype="application/json")
    print("enable", code, text[:300])
    print("state", module_state(gw))
    for path in ("/res/cadreob/js/cadre-ob.js", "/res/cadreob/css/cadre-ob.css", "/res/cadreob/fonts/NotoSans-OB.ttf"):
        code, data = gw._req("GET", path)
        print("GET", path, code, len(data) if isinstance(data, (bytes, str)) else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
