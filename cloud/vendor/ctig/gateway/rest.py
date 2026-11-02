"""Ignition 8.3 gateway REST client: only the routes proven on 8.3.6 (target profile `rest`).

Token resolution, first hit wins, and the token is never printed or written:

1. environment `CTIG_IGNITION_TOKEN` or `IGNITION_API_TOKEN`;
2. the file named by `CTIG_IGNITION_TOKEN_FILE`;
3. Windows Credential Manager generic credentials, targets `<account>@<service>` as written by
   the Python `keyring` package (service `Cadre`, account `ignition_gateway::<name>`), read with
   `CredReadW` so no third-party package is needed.
"""
from __future__ import annotations

import ctypes
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def _cred_read(target: str) -> str | None:
    if sys.platform != "win32":
        return None
    from ctypes import wintypes

    class CREDENTIAL(ctypes.Structure):
        _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD), ("TargetName", wintypes.LPWSTR),
                    ("Comment", wintypes.LPWSTR), ("LastWritten", wintypes.FILETIME),
                    ("CredentialBlobSize", wintypes.DWORD), ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
                    ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
                    ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR)]

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    pcred = ctypes.POINTER(CREDENTIAL)()
    if not advapi.CredReadW(target, 1, 0, ctypes.byref(pcred)):
        return None
    try:
        c = pcred.contents
        blob = bytes(c.CredentialBlob[i] for i in range(c.CredentialBlobSize))
        for enc in ("utf-16-le", "utf-8"):
            try:
                text = blob.decode(enc).strip("\x00").strip()
                if text and text.isprintable():
                    return text
            except UnicodeDecodeError:
                continue
        return None
    finally:
        advapi.CredFree(pcred)


def resolve_token(accounts: list[str] | None = None, service: str = "Cadre") -> tuple[str | None, str]:
    """(token, source description). The description never contains the token."""
    for var in ("CTIG_IGNITION_TOKEN", "IGNITION_API_TOKEN"):
        if os.environ.get(var):
            return os.environ[var].strip(), f"env {var}"
    tf = os.environ.get("CTIG_IGNITION_TOKEN_FILE")
    if tf and Path(tf).exists():
        return Path(tf).read_text(encoding="utf-8").strip(), "token file"
    for acct in accounts or []:
        tok = _cred_read(f"{acct}@{service}")
        if tok:
            return tok, f"credential manager {acct}@{service}"
    return None, "none"


class GatewayError(RuntimeError):
    pass


class Gateway:
    def __init__(self, base_url: str, token: str | None, timeout: float = 120.0):
        self.base = base_url.rstrip("/")
        self._token = token
        self.timeout = timeout

    def _req(self, method: str, path: str, *, query: dict[str, str] | None = None,
             body: bytes | None = None, ctype: str | None = None) -> tuple[int, bytes]:
        url = self.base + path + ("?" + urllib.parse.urlencode(query) if query else "")
        req = urllib.request.Request(url, data=body, method=method)
        if self._token:
            req.add_header("X-Ignition-API-Token", self._token)
        if ctype:
            req.add_header("Content-Type", ctype)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except urllib.error.URLError as e:
            raise GatewayError(f"{method} {path}: {e.reason}") from None

    def status_ping(self) -> str:
        code, data = self._req("GET", "/StatusPing")
        return data.decode("utf-8", "replace") if code == 200 else f"HTTP {code}"

    def gateway_info(self) -> dict[str, Any]:
        code, data = self._req("GET", "/data/api/v1/gateway-info")
        if code != 200:
            raise GatewayError(f"gateway-info HTTP {code}: {data[:200]!r}")
        return json.loads(data)

    def tags_import(self, provider: str, path: str, doc: dict, policy: str = "Overwrite") -> dict:
        code, data = self._req("POST", "/data/api/v1/tags/import",
                               query={"provider": provider, "path": path, "type": "json",
                                      "collisionPolicy": policy},
                               body=json.dumps(doc).encode("utf-8"), ctype="application/json")
        if code != 200:
            raise GatewayError(f"tags/import HTTP {code}: {data[:300]!r}")
        return json.loads(data) if data else {}

    def tags_export(self, provider: str, path: str) -> dict:
        code, data = self._req("GET", "/data/api/v1/tags/export",
                               query={"provider": provider, "path": path, "type": "json", "recursive": "true"})
        if code != 200:
            raise GatewayError(f"tags/export HTTP {code}: {data[:300]!r}")
        return json.loads(data)

    def project_import(self, name: str, zip_bytes: bytes) -> str:
        code, data = self._req("POST", f"/data/api/v1/projects/import/{urllib.parse.quote(name)}",
                               query={"overwrite": "true"}, body=zip_bytes, ctype="application/zip")
        if code != 200:
            raise GatewayError(f"projects/import HTTP {code}: {data[:300]!r}")
        return data.decode("utf-8", "replace")

    def project_export(self, name: str) -> bytes:
        code, data = self._req("GET", f"/data/api/v1/projects/export/{urllib.parse.quote(name)}")
        if code != 200:
            raise GatewayError(f"projects/export HTTP {code}: {data[:300]!r}")
        return data

    def project_names(self) -> list[str]:
        code, data = self._req("GET", "/data/api/v1/projects/names")
        if code != 200:
            raise GatewayError(f"projects/names HTTP {code}")
        d = json.loads(data)
        return d.get("items", d) if isinstance(d, dict) else d
