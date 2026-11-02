"""Live flow gate (G9): the pipes the gateway draws as carrying match the reference solver.

For each tag state scenario: write the gate tags (memory tags, through the REST tag import
with overwrite), open the page in a fresh session, read each pipe's rendered inner stroke, and
compare "carrying" (the flow colour) with `diagram.solve` on the same states. A scenario
passes when every pipe agrees.

Runs under an interpreter with Playwright (ctig's .venv) and needs PYTHONPATH=tools.

Usage:
    F:/repos/Citect-Ignition-Migrator/.venv/Scripts/python.exe tools/compare/live_flow.py
        --descriptor screens/sample-pump-station.json --base http://localhost:8088/data/perspective/client/cadre_hmi_sample
        --scenarios 4 --out workspace/compare/sample-flow
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from hmi import diagram, deploy  # noqa: E402
from hmi.screen import load_contracts, tag_path  # noqa: E402

READ_JS = """() => {
  const out = {};
  document.querySelectorAll('path[name]').forEach(p => {
    const n = p.getAttribute('name');
    if (!n || n.endsWith('_outline')) return;
    out[n] = getComputedStyle(p).stroke;
  });
  const probe = document.createElement('div');
  probe.style.color = 'var(--automation-pipe-primary-color)';
  const root = document.querySelector('.ia_container--root') || document.body;
  root.appendChild(probe);
  const flow = getComputedStyle(probe).color;
  probe.style.color = 'var(--automation-pipe-primary-inverted-color)';
  const empty = getComputedStyle(probe).color;
  probe.remove();
  return JSON.stringify({strokes: out, flow, empty});
}"""


def gate_members(desc: dict, contracts: dict) -> dict:
    """symbol id -> (tag path, state parameter) for every bound gate."""
    out = {}
    for s in desc.get("symbols", []):
        kind = s["kind"].lower()
        if kind not in diagram.GATED:
            continue
        state = diagram.GATED[kind]
        member = s.get("bind", {}).get(state)
        if member:
            out[s["id"]] = (tag_path(desc["tagRoot"], member), state)
    return out


def write_states(desc: dict, states: dict, gates: dict) -> None:
    """Re-import the gate tags with the scenario values (memory tags, overwrite)."""
    root = desc["tagRoot"].split("]")[-1].split("/")
    folders: dict = {}
    for sid, (tp, _) in gates.items():
        rel = tp.split("]")[-1].split("/")[len(root):]
        folders.setdefault(tuple(rel[:-1]), []).append((rel[-1], bool(states[sid])))
    for path, members in folders.items():
        doc = {"name": path[-1], "tagType": "Folder", "tags": [
            {"name": n, "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Boolean", "value": v}
            for n, v in members]}
        parent = "/".join(root + list(path[:-1]))
        deploy.import_tags(desc["tagRoot"].split("]")[0].strip("["), parent, doc)


def run(desc: dict, base: str, n: int, out: Path, seed: int = 11) -> dict:
    from playwright.sync_api import sync_playwright
    contracts = load_contracts()
    syms = []
    for s in desc.get("symbols", []):
        c = contracts.get({"tank": "Automation/Tank"}.get(s["kind"], f"Automation/{s['kind'].capitalize()}"), {})
        s2 = dict(s)
        if s["kind"].lower() in diagram.GATED or s["kind"].lower() in ("readout",):
            s2.update({"w": 48, "h": 48, "anchor": "symbol-centre"})
        syms.append(s2)
    g, _ = diagram.build_graph(dict(desc, symbols=syms), contracts)
    gates = gate_members(desc, contracts)
    rnd = random.Random(seed)
    # Scenario 0 is the descriptor's own test state; the rest are seeded random gate states.
    scenarios = [{sid: desc.get("tagValues", {}).get(f"{sid}/state", False) for sid in gates}]
    for _ in range(n - 1):
        scenarios.append({sid: rnd.random() < 0.5 for sid in gates})
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for i, st in enumerate(scenarios):
            write_states(desc, st, gates)
            ctx = browser.new_context(viewport={"width": 1600, "height": 900})
            page = ctx.new_page()
            page.goto(base.rstrip("/") + desc["screen"]["route"], wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)
            got = json.loads(page.evaluate(READ_JS))
            ctx.close()
            expect = diagram.solve(g, st)
            mism = []
            for pid in g.edges:
                stroke = got["strokes"].get(pid)
                carrying = stroke not in (got["empty"],) and stroke is not None
                if carrying != (pid in expect):
                    mism.append({"pipe": pid, "rendered": stroke, "expected_carrying": pid in expect})
            results.append({"scenario": i, "open_gates": sorted(k for k, v in st.items() if v),
                            "pipes": len(g.edges), "carrying_expected": len(expect),
                            "mismatches": mism, "ok": not mism})
        browser.close()
    rep = {"scenarios": len(results), "passed": sum(r["ok"] for r in results), "results": results}
    out.mkdir(parents=True, exist_ok=True)
    (out / "live-flow.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--descriptor", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--scenarios", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    desc = json.loads(Path(a.descriptor).read_text(encoding="utf-8"))
    print(deploy.ensure_trial())
    rep = run(desc, a.base, a.scenarios, Path(a.out))
    for r in rep["results"]:
        print(f"scenario {r['scenario']}: open {r['open_gates']} expected carrying {r['carrying_expected']}"
              f"/{r['pipes']} -> {'PASS' if r['ok'] else 'FAIL ' + json.dumps(r['mismatches'][:3])}")
    print(f"LIVE FLOW {rep['passed']}/{rep['scenarios']}")
    return 0 if rep["passed"] == rep["scenarios"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
