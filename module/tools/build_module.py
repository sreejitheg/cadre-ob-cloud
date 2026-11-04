"""Build and sign the Cadre HMI Components module offline.

Runs `gradlew build --offline` in `module/` under JDK 17, with the signing properties read from the
owner's file outside the repository (`~/.cadre/signing/signing.properties`) and handed to Gradle as
`ORG_GRADLE_PROJECT_<name>` environment variables, so no secret reaches the command line, the
console or a file. `--offline` uses only the Gradle cache: the build never downloads.

Usage:  python module/tools/build_module.py [--jdk C:/Users/<user>/.jdks/jdk-17...]
        (without --jdk: CADRE_JDK17, else the newest jdk-17 of the owner's Windows locations)
Prints the built file, its size and its SHA-256.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SIGNING = Path.home() / ".cadre" / "signing" / "signing.properties"


def jdk17() -> Path | None:
    # CADRE_JDK17 names the JDK where the owner's Windows locations below do not exist (a cloud session)
    if os.environ.get("CADRE_JDK17"):
        return Path(os.environ["CADRE_JDK17"])
    for base in (Path.home() / ".jdks", Path("C:/Program Files/Eclipse Adoptium"), Path("C:/Program Files/Java")):
        if base.exists():
            for d in sorted(base.iterdir(), reverse=True):
                if d.name.startswith("jdk-17") and (d / "bin" / "javac.exe").exists():
                    return d
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jdk", default=None)
    ap.add_argument("--task", default="build")
    a = ap.parse_args()
    jdk = Path(a.jdk) if a.jdk else jdk17()
    if not jdk:
        raise SystemExit("no JDK 17 found; pass --jdk")
    env = dict(os.environ, JAVA_HOME=str(jdk))
    if SIGNING.exists():
        for line in SIGNING.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env[f"ORG_GRADLE_PROJECT_{k.strip()}"] = v.strip()
    else:
        print("no signing properties: the module is built unsigned")
    gradlew = HERE / ("gradlew.bat" if os.name == "nt" else "gradlew")
    # always clean first: an incremental build after a version change packaged the previous
    # version's jars (module.xml 0.2.0 holding common-0.1.0.jar, 2026-10-08)
    r = subprocess.run([str(gradlew), "clean", a.task, "--offline", "--console=plain"], cwd=HERE, env=env)
    if r.returncode:
        return r.returncode
    # the module plugin names an unsigned build `<fileName>.unsigned.modl`
    out = HERE / "build" / ("CadreHMIComponents.modl" if SIGNING.exists() else "CadreHMIComponents.unsigned.modl")
    data = out.read_bytes()
    print(f"built {out} {len(data)} bytes sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
