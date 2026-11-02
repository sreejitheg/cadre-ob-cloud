"""Write the component test page's descriptor and devices file for gate G11 (COB-181).

    python tools/hmi/bench_descriptor.py --tag-root [default]cadre_hmi_x --devices devices.json --out DIR [--margin 200]

Builds the page with `testbench.build` from the library's contracts and profile, and writes
`DIR/ComponentTest.desc.json` and `DIR/devices_with_bench.json`: the project's devices (`--devices`) with the test
devices added by `Bench.extend_devices`, each test device that states no faceplate style set to `faceplate: asm`, so
that the sweep opens the asm faceplates. Prints the viewport height the page needs (the page's height from the
descriptor plus `--margin`), for `tools/compare/faceplates.py --height`. Offline: no gateway.

Exit codes: 0 written, 2 the generator's own check of the page found problems (listed; the files are still written),
1 a fault.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hmi import library_profile, screen, testbench  # noqa: E402


def build(tag_root: str, devices: dict, style: str = "asm") -> tuple[dict, dict, list[str]]:
    contracts = screen.load_contracts()
    bench = testbench.build(contracts, library_profile.build(contracts), tag_root)
    extended = bench.extend_devices(devices)
    prefix = testbench.FOLDER + "/"
    for d in extended["devices"]:
        if d["id"].startswith(prefix) and not d.get("faceplate"):
            d["faceplate"] = style
    return bench.descriptor, extended, testbench.check(bench.descriptor, contracts)


def dump(path: Path, doc) -> None:
    path.write_bytes((json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tag-root", required=True, help="[provider]folder the project's tags sit under")
    ap.add_argument("--devices", required=True, help="the project's devices file (cadre-hmi-devices/1)")
    ap.add_argument("--out", required=True, help="the folder to write into")
    ap.add_argument("--margin", type=int, default=200, help="px added to the page height (default 200)")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 1 if e.code else 0
    try:
        devices = json.loads(Path(a.devices).read_text(encoding="utf-8"))
        desc, extended, problems = build(a.tag_root, devices)
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        dump(out / "ComponentTest.desc.json", desc)
        dump(out / "devices_with_bench.json", extended)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"bench_descriptor: {e}", file=sys.stderr)
        return 1
    height = int(desc["screen"]["height"]) + a.margin
    for p in problems:
        print(f"bench_descriptor: {p}", file=sys.stderr)
    print(f"bench_descriptor: wrote {out / 'ComponentTest.desc.json'} and {out / 'devices_with_bench.json'}; "
          f"route {desc['screen'].get('route')}; faceplates.py --height {height}")
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
