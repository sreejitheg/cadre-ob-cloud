"""Check that the pinned element package (`@oicl/openbridge-webcomponents`) in `module/web` is exactly the pinned release, unmodified.

The pin is `@oicl/openbridge-webcomponents` 2.0.0-next.155 (COBD-003). The check (NOTE-WFB-10 section 11.1 item 3)
exits 0 when every test holds and exits 1, printing each failing path, when:

  * `package.json` does not name the exact string `2.0.0-next.155` for the package, or `package-lock.json`
    (`packages[""].dependencies` and `packages["node_modules/@oicl/openbridge-webcomponents"]`),
    `node_modules/.package-lock.json` or the installed package's `package.json` gives another version, or another
    `resolved` or `integrity` than the constants below;
  * a file listed in the manifest is missing or its SHA-256 differs, or a file under the package's `dist/` is not
    listed.

The manifest `module/web/openbridge-2.0.0-next.155.sha256.json` is `{package, version, integrity, files}`; each key of
`files` is a path relative to `module/web/node_modules` (forward slashes), each value a SHA-256. `--generate` writes it
once: the package's own files are hashed from the release tarball's members (after the tarball's SHA-512 is checked against
the lock's integrity and the constant), and the other packages the bundle can reach are hashed from the installed tree
(after `npm ci` has verified them against the lock).

Standard library only. Usage:

    python module/tools/verify_pin.py [--root module/web] [--manifest <file>]
    python module/tools/verify_pin.py --generate [--tarball <file>] [--root module/web] [--manifest <file>]

Other tools call `require_pin()` as their first statement.

Reading the installed package from another checkout. `node_modules` is installed in the main checkout only, so a
worktree has none. Setting the environment variable `CADRE_OB_WEB_ROOT` to that checkout's `module/web` folder makes
`web_root()` return it: this script's default `--root`, `require_pin()` and the build tools that read the package
(`gen_module_assets.py`, `measure_defaults.py`) then read the installed package and the built `dist/` bundle there,
read only. The pin is checked against the manifest tracked beside this script exactly as before; only the place of
`node_modules` moves. The version files (`package.json`, `package-lock.json`) are always those of the checkout being
built, this script's sibling `web` folder, never the other checkout's (NOTE-WFB-10 section 13 invariant 4). Nothing is
written under that root.

The bundle record (section 13 invariant 4). `npm run build` ends with `--record-bundle`, which writes
`dist/ob-components.build.json` beside the bundle: `{lock_sha256, entry_sha256, bundle_sha256}`, the SHA-256 of the
checkout's `package-lock.json`, of its `entry.js` and of `dist/ob-components.js`. `check_bundle_record` compares a
record with the checkout's lock and entry files and with the bundle; `build_module.py` and `gen_module_assets.py`
(without `--allow-stale-bundle`) refuse a bundle that has no record or whose record does not match, since a bundle
built from another lock or entry file is not the pinned release bundled as the pin says.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import tarfile
from pathlib import Path, PurePosixPath

PACKAGE = "@oicl/openbridge-webcomponents"
VERSION = "2.0.0-next.155"
RESOLVED = "https://registry.npmjs.org/@oicl/openbridge-webcomponents/-/openbridge-webcomponents-2.0.0-next.155.tgz"
INTEGRITY = "sha512-PwHJx4APgm+OmHPDdbLQHjVGzaeGaAuRgPfxs1w8ucdW+ZA+ZJPAN9erd3/qvPgjCR/+RjYhsexSIu0wKk2xug=="

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent / "web"
ROOT_ENV = "CADRE_OB_WEB_ROOT"


def web_root() -> Path:
    """The `module/web` folder that holds `node_modules` and `dist/`: the one named by `CADRE_OB_WEB_ROOT` (a read only
    root in another checkout) when it is set, else the sibling `web` folder of this script's module."""
    named = os.environ.get(ROOT_ENV, "").strip()
    return Path(named) if named else DEFAULT_ROOT


MANIFEST_NAME = f"openbridge-{VERSION}.sha256.json"
DEFAULT_MANIFEST = DEFAULT_ROOT / MANIFEST_NAME
LOCK_KEY = f"node_modules/{PACKAGE}"
# Files of the package outside dist/ that every manifest must list.
REQUIRED = ("package.json", "custom-elements.json", "bundle/openbridge-webcomponents.bundle.js")
# Files of the package the manifest covers besides everything under dist/.
EXTRA_MEMBERS = REQUIRED


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load(path: Path, label: str, failures: list):
    try:
        return read_json(path)
    except (OSError, ValueError) as e:
        failures.append(f"{label}: cannot be read ({type(e).__name__}: {e})")
        return None


def _check_entry(entry, label: str, failures: list) -> None:
    if not isinstance(entry, dict):
        failures.append(f"{label}: no entry for {PACKAGE}")
        return
    for key, want in (("version", VERSION), ("resolved", RESOLVED), ("integrity", INTEGRITY)):
        if entry.get(key) != want:
            failures.append(f"{label}: {PACKAGE} {key} is {entry.get(key)!r}, the pin is {want!r}")


def check_versions(root: Path, versions_root: Path | None = None) -> list:
    """The version, resolved and integrity checks of the four JSON files; returns failure lines. `package.json` and
    `package-lock.json` are read from `versions_root` (the checkout being built; default `root`), the installed
    `node_modules` files from `root`."""
    failures: list = []
    versions_root = Path(versions_root) if versions_root else root
    pj = _load(versions_root / "package.json", "package.json", failures)
    if isinstance(pj, dict):
        found = False
        for section in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
            deps = pj.get(section)
            if isinstance(deps, dict) and PACKAGE in deps:
                found = True
                if deps[PACKAGE] != VERSION:
                    failures.append(f"package.json: {section}.{PACKAGE} is {deps[PACKAGE]!r}, the pin is the exact "
                                    f"string {VERSION!r}")
        if not found:
            failures.append(f"package.json: {PACKAGE} is not a dependency")
    lock = _load(versions_root / "package-lock.json", "package-lock.json", failures)
    if isinstance(lock, dict):
        pk = lock.get("packages") if isinstance(lock.get("packages"), dict) else {}
        top = pk.get("") if isinstance(pk.get(""), dict) else {}
        deps = top.get("dependencies") if isinstance(top.get("dependencies"), dict) else {}
        if deps.get(PACKAGE) != VERSION:
            failures.append(f"package-lock.json: packages[''].dependencies.{PACKAGE} is {deps.get(PACKAGE)!r}, "
                            f"the pin is {VERSION!r}")
        _check_entry(pk.get(LOCK_KEY), f"package-lock.json: packages['{LOCK_KEY}']", failures)
    hidden = _load(root / "node_modules" / ".package-lock.json", "node_modules/.package-lock.json", failures)
    if isinstance(hidden, dict):
        pk = hidden.get("packages") if isinstance(hidden.get("packages"), dict) else {}
        _check_entry(pk.get(LOCK_KEY), f"node_modules/.package-lock.json: packages['{LOCK_KEY}']", failures)
    inst = _load(root / "node_modules" / PACKAGE / "package.json", f"node_modules/{PACKAGE}/package.json", failures)
    if isinstance(inst, dict) and inst.get("version") != VERSION:
        failures.append(f"node_modules/{PACKAGE}/package.json: installed {PACKAGE} version is "
                        f"{inst.get('version')!r}, the pin is {VERSION!r}")
    return failures


def _safe_rel(rel: str) -> bool:
    p = PurePosixPath(rel)
    return bool(rel) and not p.is_absolute() and ".." not in p.parts and "\\" not in rel and ":" not in rel


def check_files(root: Path, manifest_path: Path) -> list:
    """The manifest checks; returns failure lines."""
    failures: list = []
    man = _load(manifest_path, f"manifest {manifest_path.name}", failures)
    if not isinstance(man, dict):
        return failures
    label = f"manifest {manifest_path.name}"
    for key, want in (("package", PACKAGE), ("version", VERSION), ("integrity", INTEGRITY)):
        if man.get(key) != want:
            failures.append(f"{label}: {key} is {man.get(key)!r}, the pin is {want!r}")
    files = man.get("files")
    if not isinstance(files, dict):
        failures.append(f"{label}: no files table")
        return failures
    for req in REQUIRED:
        if f"{PACKAGE}/{req}" not in files:
            failures.append(f"{label}: {PACKAGE}/{req} is not listed")
    nm = root / "node_modules"
    for rel in sorted(files):
        want = files[rel]
        if not _safe_rel(rel):
            failures.append(f"{rel}: the manifest names a path outside node_modules")
            continue
        f = nm / rel
        if not f.is_file():
            failures.append(f"{rel}: listed in the manifest and missing")
            continue
        got = sha256_of(f)
        if got != want:
            failures.append(f"{rel}: SHA-256 differs (installed {got}, manifest {want})")
    dist = nm / PACKAGE / "dist"
    prefix = f"{PACKAGE}/dist/"
    if dist.is_dir():
        for dirpath, _dirs, names in os.walk(dist):
            for name in names:
                rel = f"{PACKAGE}/" + (Path(dirpath) / name).relative_to(nm / PACKAGE).as_posix()
                if rel not in files:
                    failures.append(f"{rel}: under dist/ and not listed in the manifest")
    elif any(k.startswith(prefix) for k in files):
        failures.append(f"{PACKAGE}/dist: the folder is missing")
    return failures


def verify(root: Path = DEFAULT_ROOT, manifest: Path | None = None, versions_root: Path | None = None) -> list:
    root = Path(root)
    manifest = Path(manifest) if manifest else DEFAULT_MANIFEST
    return check_versions(root, versions_root) + check_files(root, manifest)


def report(failures: list) -> int:
    if failures:
        print(f"verify_pin: FAILED, {len(failures)} finding(s) against the pin {PACKAGE} {VERSION}")
        for line in failures:
            print(f"  FAIL {line}")
        return 1
    print(f"verify_pin: ok, {PACKAGE} {VERSION} matches the lock and the manifest")
    return 0


def require_pin(root: Path | None = None, manifest: Path | None = None) -> None:
    """For the build tools: end the process with the findings listed when the pin check fails. `root` defaults to
    `web_root()`, whose `node_modules` is read while the version files are those of this checkout; a `root` given reads
    all of its files from there."""
    failures = verify(root, manifest) if root else verify(web_root(), manifest, DEFAULT_ROOT)
    if failures:
        report(failures)
        raise SystemExit(1)


# --- the bundle record -----------------------------------------------------------------------------------------

BUNDLE_REL = "dist/ob-components.js"
RECORD_REL = "dist/ob-components.build.json"
RECORD_KEYS = ("lock_sha256", "entry_sha256", "bundle_sha256")
RECORD_SOURCES = {"lock_sha256": "package-lock.json", "entry_sha256": "entry.js"}   # the checkout's own files


def write_bundle_record(root: Path = DEFAULT_ROOT) -> Path:
    """Write the record beside the bundle built in `root` (the build step of `npm run build`): the hashes of its
    `package-lock.json`, its `entry.js` and its `dist/ob-components.js`."""
    root = Path(root)
    record = {"lock_sha256": sha256_of(root / "package-lock.json"), "entry_sha256": sha256_of(root / "entry.js"),
              "bundle_sha256": sha256_of(root / BUNDLE_REL)}
    path = root / RECORD_REL
    path.write_bytes((json.dumps(record, indent=1) + "\n").encode("utf-8"))
    return path


def check_bundle_record(bundle_root: Path | None = None, checkout: Path | None = None) -> list:
    """The findings against the record of the bundle in `bundle_root` (default `web_root()`): it has none, it lacks a
    hash, the lock or entry file of `checkout` (default this checkout's `module/web`) has changed since the build, or
    the bundle is not the one recorded. Returns failure lines."""
    bundle_root = Path(bundle_root) if bundle_root else web_root()
    checkout = Path(checkout) if checkout else DEFAULT_ROOT
    bundle, record_path = bundle_root / BUNDLE_REL, bundle_root / RECORD_REL
    failures: list = []
    if not bundle.is_file():
        return [f"bundle {bundle}: missing; run npm run build in module/web"]
    if not record_path.is_file():
        return [f"bundle record {record_path}: missing, so the bundle is not known to be built from this checkout's "
                "lock and entry file; run npm run build in module/web, which writes it"]
    try:
        record = read_json(record_path)
    except (OSError, ValueError) as e:
        return [f"bundle record {record_path}: cannot be read ({type(e).__name__}: {e})"]
    if not isinstance(record, dict):
        return [f"bundle record {record_path}: not an object"]
    for key in RECORD_KEYS:
        value = record.get(key)
        if not isinstance(value, str) or len(value) != 64:
            failures.append(f"bundle record {record_path}: {key} is {value!r}, not a SHA-256")
    if failures:
        return failures
    for key, name in RECORD_SOURCES.items():
        f = checkout / name
        now = sha256_of(f) if f.is_file() else None
        if now != record[key]:
            failures.append(f"bundle record: {key.split('_')[0]} file {f} is {'missing' if now is None else 'not'} "
                            f"the one the bundle was built from (record {record[key]}, now {now})")
    now = sha256_of(bundle)
    if now != record["bundle_sha256"]:
        failures.append(f"bundle record: bundle {bundle} is not the recorded one (record {record['bundle_sha256']}, "
                        f"now {now})")
    return failures


def require_bundle_record(bundle_root: Path | None = None, checkout: Path | None = None) -> None:
    """For the build tools: end the process with the findings listed when the bundle has no matching record."""
    failures = check_bundle_record(bundle_root, checkout)
    if failures:
        print(f"verify_pin: the bundle is not known to be built from the pinned lock, {len(failures)} finding(s)")
        for line in failures:
            print(f"  FAIL {line}")
        raise SystemExit(1)


# --- generation ------------------------------------------------------------------------------------------------

def tarball_in_cache() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    h = base64.b64decode(INTEGRITY.split("-", 1)[1]).hex()
    return Path(base) / "npm-cache" / "_cacache" / "content-v2" / "sha512" / h[0:2] / h[2:4] / h[4:]


def sha512_integrity(path: Path) -> str:
    h = hashlib.sha512()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha512-" + base64.b64encode(h.digest()).decode("ascii")


def hash_tarball(tarball: Path) -> dict:
    """SHA-256 of every member under dist/ and the extra members, keyed relative to node_modules."""
    out: dict = {}
    with tarfile.open(tarball, "r:gz") as tf:
        for m in tf:
            if not m.isfile() or not m.name.startswith("package/"):
                continue
            rel = m.name[len("package/"):]
            if not _safe_rel(rel) or not (rel.startswith("dist/") or rel in EXTRA_MEMBERS):
                continue
            data = tf.extractfile(m).read()  # type: ignore[union-attr]
            out[f"{PACKAGE}/{rel}"] = hashlib.sha256(data).hexdigest()
    return out


def hash_other_packages(root: Path) -> dict:
    """SHA-256 of every file of the other runtime packages in the lock (the bundle's third-party inputs)."""
    nm = root / "node_modules"
    hidden = read_json(nm / ".package-lock.json")
    out: dict = {}
    for key, entry in sorted(hidden.get("packages", {}).items()):
        if not key.startswith("node_modules/") or key == LOCK_KEY or entry.get("dev") or entry.get("optional"):
            continue
        name = key[len("node_modules/"):]
        if "/node_modules/" in key:
            continue
        pdir = nm / name
        installed = read_json(pdir / "package.json")
        if installed.get("version") != entry.get("version"):
            raise SystemExit(f"{name}: installed {installed.get('version')} differs from the lock {entry.get('version')}; "
                             "run npm ci first")
        for dirpath, dirs, names in os.walk(pdir):
            dirs[:] = [d for d in dirs if d != "node_modules"]
            for n in names:
                f = Path(dirpath) / n
                out[f.relative_to(nm).as_posix()] = sha256_of(f)
    return out


def generate(root: Path, manifest: Path, tarball: Path | None, versions_root: Path | None = None) -> int:
    failures = check_versions(root, versions_root)
    if failures:
        return report(failures)
    tarball = tarball or tarball_in_cache()
    if not tarball.is_file():
        print(f"verify_pin: the release tarball is missing: {tarball}")
        return 1
    got = sha512_integrity(tarball)
    if got != INTEGRITY:
        print(f"verify_pin: the tarball {tarball} has integrity {got}, the lock and the pin say {INTEGRITY}")
        return 1
    files = hash_tarball(tarball)
    for req in REQUIRED:
        if f"{PACKAGE}/{req}" not in files:
            print(f"verify_pin: the tarball has no member {req}")
            return 1
    files.update(hash_other_packages(root))
    doc = {"package": PACKAGE, "version": VERSION, "integrity": INTEGRITY, "files": dict(sorted(files.items()))}
    manifest.write_bytes((json.dumps(doc, indent=1) + "\n").encode("utf-8"))
    print(f"verify_pin: wrote {manifest} with {len(files)} files")
    # The installed tree must match the tarball member for member.
    return report(check_files(root, manifest))


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=None,
                    help=f"the module/web folder, all of whose files are read (default: ${ROOT_ENV} when set for "
                         "node_modules, with the version files of the sibling web folder; else the sibling web folder)")
    ap.add_argument("--record-bundle", action="store_true",
                    help="write the bundle record beside dist/ob-components.js in --root (default the sibling web "
                         "folder): the last step of npm run build")
    ap.add_argument("--manifest", type=Path, default=None, help="the manifest (default: the tracked module/web file beside this script)")
    ap.add_argument("--generate", action="store_true", help="write the manifest from the tarball and the installed tree")
    ap.add_argument("--tarball", type=Path, default=None, help="with --generate: the release tarball (default npm's cache)")
    a = ap.parse_args(argv)
    manifest = a.manifest or DEFAULT_MANIFEST
    if a.record_bundle:
        print(f"verify_pin: wrote {write_bundle_record(a.root or DEFAULT_ROOT)}")
        return 0
    root, versions = (a.root, None) if a.root else (web_root(), DEFAULT_ROOT)
    if a.generate:
        return generate(root, manifest, a.tarball, versions)
    return report(verify(root, manifest, versions))


if __name__ == "__main__":
    sys.exit(main())
