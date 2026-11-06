"""Process diagrams: pipe routing, flow compilation and the reference flow solver.

The connector diagram idea (wiki page 04 section 5): symbols are placed, pipes join their
connection points, and a pipe carries the medium when it lies on a simple path from a source
to a different sink through open gates. Tanks are sources and sinks; a loose pipe end marked
`arrow-in` is a source and `arrow-out` a sink; valves pass while `open`, pumps, fans, motors,
switches and dampers while `on`; junctions and every other symbol always pass; a pipe whose
`state` is `closed` blocks.

Decision COBD-006: the generator compiles each pipe's condition into one expression over the
gate states, `OR` over the source-to-sink paths through the pipe of `AND` over the gates on
the path. `check_flow` evaluates the compiled expressions against `solve`, a solver that
enumerates paths on the concrete open graph, over every gate state vector (or a seeded
sample when there are many gates).
"""
from __future__ import annotations

import itertools
import random
import re
from dataclasses import dataclass, field

SIDES = ("top", "bottom", "left", "right")
GATED = {"valve": "open", "analogvalve": "open", "pump": "on", "motor": "on", "fan": "on",
         "switch": "on", "damper": "on"}
TERMINAL = {"tank"}
RING = 18  # pipe meets the round holder (36 px) of a 48 px automation symbol


@dataclass
class Graph:
    nodes: dict = field(default_factory=dict)      # id -> role: terminal | gate | pass | source | sink | end
    gate_of: dict = field(default_factory=dict)    # gate node id -> gate variable name
    edges: dict = field(default_factory=dict)      # pipe id -> (a, b)


def node_role(kind: str) -> str:
    k = kind.lower()
    if k in TERMINAL:
        return "terminal"
    if k in GATED:
        return "gate"
    return "pass"


def connection_point(sym: dict, side: str) -> tuple[float, float]:
    """Middle of a side. Automation symbols connect at the holder ring, boxes at the edge.

    A symbol with a `tile` (a static tank: fractions x, y, width, height of its box, `library.STATIC_TILE`)
    draws inside its box, so a pipe at the left, the right or the top ends at the tile's edge, on the same
    centre lines as the box's. The bottom stays at the box's edge: the identifier lies between the tile
    and it, and a pipe drawn up to the tile would run through the identifier."""
    x, y, w, h = sym["x"], sym["y"], sym["w"], sym["h"]
    cx, cy = x + w / 2, y + h / 2
    if sym.get("anchor") == "symbol-centre":
        r = RING
        return {"top": (cx, cy - r), "bottom": (cx, cy + r), "left": (cx - r, cy),
                "right": (cx + r, cy)}[side]
    if sym.get("tile"):
        fx, fy, fw, _fh = sym["tile"]
        return {"top": (cx, y + fy * h), "bottom": (cx, y + h), "left": (x + fx * w, cy),
                "right": (x + (fx + fw) * w, cy)}[side]
    return {"top": (cx, y), "bottom": (cx, y + h), "left": (x, cy), "right": (x + w, cy)}[side]


def build_graph(desc: dict, contracts: dict) -> tuple[Graph, dict]:
    """Graph plus endpoint coordinates: pipe id -> (p0, side0, p1, side1)."""
    g = Graph()
    syms = {s["id"]: s for s in desc.get("symbols", [])}
    for s in syms.values():
        role = node_role(s["kind"])
        if role == "gate":
            # a gate has a state: bound to a member or stated as a parameter, the two cases in which `screen.py` defines
            # `custom.g_<id>`. A switch the design draws with neither has none to follow and passes, as a junction does
            # (COB-212): no expression may name a state that no view defines
            state = GATED[s["kind"].lower()]
            if state not in (s.get("bind") or {}) and state not in (s.get("params") or {}):
                role = "pass"
        g.nodes[s["id"]] = role
        if role == "gate":
            g.gate_of[s["id"]] = s["id"]
    for j in desc.get("junctions", []):
        g.nodes[j["id"]] = "pass"
    geo = {}
    for p in desc.get("pipes", []):
        ends = []
        for k, end in (("a", p["from"]), ("b", p["to"])):
            if "ref" in end and end["ref"] in syms:
                s = syms[end["ref"]]
                pt = (end["x"], end["y"]) if "x" in end else connection_point(s, end.get("side", "top"))
                ends.append((end["ref"], pt, end.get("side")))
            elif "ref" in end:   # a junction
                j = next(j for j in desc.get("junctions", []) if j["id"] == end["ref"])
                ends.append((end["ref"], (j["x"], j["y"]), end.get("side")))
            else:                # a loose end
                nid = f"{p['id']}.{k}"
                mark = end.get("end", "cap")
                g.nodes[nid] = {"arrow-in": "source", "arrow-out": "sink"}.get(mark, "end")
                ends.append((nid, (end["x"], end["y"]), end.get("side")))
        if p.get("state", "open") != "closed":
            g.edges[p["id"]] = (ends[0][0], ends[1][0])
        geo[p["id"]] = (ends[0][1], ends[0][2], ends[1][1], ends[1][2])
    return g, geo


def _is_source(role):
    return role in ("terminal", "source")


def _is_sink(role):
    return role in ("terminal", "sink")


def enumerate_paths(g: Graph, open_gate=lambda n: True, limit: int = 20000):
    """Simple paths between a source and a different sink; each path is (edge ids, gates).
    Terminals are path ends only: the medium arrives in or leaves a tank, it does not pass."""
    adj: dict = {}
    for eid, (a, b) in g.edges.items():
        adj.setdefault(a, []).append((eid, b))
        adj.setdefault(b, []).append((eid, a))
    out, count = [], 0
    for s, role in g.nodes.items():
        if not _is_source(role):
            continue
        stack = [(s, [s], [], [])]
        while stack:
            node, seen, path, gates = stack.pop()
            for eid, nxt in adj.get(node, []):
                if nxt in seen:
                    continue
                r = g.nodes.get(nxt, "pass")
                if _is_sink(r) and nxt != s:
                    out.append((path + [eid], gates))
                    count += 1
                    if count > limit:
                        raise OverflowError("path enumeration limit")
                if r in ("terminal", "source", "sink", "end"):
                    continue
                if r == "gate":
                    if not open_gate(nxt):
                        continue
                    stack.append((nxt, seen + [nxt], path + [eid], gates + [nxt]))
                else:
                    stack.append((nxt, seen + [nxt], path + [eid], gates))
    return out


def compile_flow(g: Graph) -> dict[str, list[frozenset]]:
    """pipe id -> minimal list of gate sets (a DNF); [] means never, [frozenset()] always."""
    terms: dict[str, set] = {e: set() for e in g.edges}
    for edges, gates in enumerate_paths(g):
        t = frozenset(gates)
        for e in edges:
            terms[e].add(t)
    out = {}
    for e, ts in terms.items():
        minimal = [t for t in ts if not any(o < t for o in ts)]
        out[e] = sorted(minimal, key=lambda t: (len(t), sorted(t)))
    return out


def dnf_expression(dnf: list[frozenset], ref) -> str:
    if not dnf:
        return "false"
    if any(len(t) == 0 for t in dnf):
        return "true"
    parts = []
    for t in dnf:
        lits = [ref(n) for n in sorted(t)]
        parts.append(lits[0] if len(lits) == 1 else "(" + " && ".join(lits) + ")")
    return " || ".join(parts)


def solve(g: Graph, state: dict) -> set:
    """Reference: the pipes on a source-to-sink path in the concrete open graph."""
    carried = set()
    for edges, _ in enumerate_paths(g, open_gate=lambda n: bool(state.get(n))):
        carried.update(edges)
    return carried


def eval_expression(expr: str, state: dict) -> bool:
    py = re.sub(r"\{view\.custom\.g_([\w-]+)\}", lambda m: repr(bool(state.get(m.group(1)))), expr)
    py = py.replace("&&", " and ").replace("||", " or ")
    return bool(eval(py, {"__builtins__": {}}, {"true": True, "false": False}))


def check_flow(g: Graph, exprs: dict[str, str], *, max_exhaustive: int = 12, samples: int = 4096,
               seed: int = 7) -> dict:
    gates = sorted(g.gate_of)
    if len(gates) <= max_exhaustive:
        vectors = itertools.product([False, True], repeat=len(gates))
        mode, n = "exhaustive", 2 ** len(gates)
    else:
        rnd = random.Random(seed)
        vectors = ([rnd.random() < 0.5 for _ in gates] for _ in range(samples))
        mode, n = f"sampled (seed {seed})", samples
    mismatches = []
    for vec in vectors:
        st = dict(zip(gates, vec))
        ref = solve(g, st)
        for e, ex in exprs.items():
            if eval_expression(ex, st) != (e in ref):
                mismatches.append({"pipe": e, "state": {k: v for k, v in st.items() if v}})
                break
        if len(mismatches) > 10:
            break
    return {"gates": len(gates), "pipes": len(exprs), "vectors": n, "mode": mode,
            "mismatches": mismatches, "ok": not mismatches}


# ---------------------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------------------
def _vertical(side):
    return side in ("top", "bottom")


# The shapes of a pipe between two points that share neither x nor y (two that do are joined STRAIGHT):
#   Z_Y      down or up to the rounded mean of the two y, across, then on to the end
#   Z_X      across to the rounded mean of the two x, down or up, then on to the end
#   L_Y      along y first: one corner at (x of the start, y of the end)
#   L_X      along x first: one corner at (x of the end, y of the start)
STRAIGHT, Z_Y, Z_X, L_Y, L_X = "STRAIGHT", "Z_Y", "Z_X", "L_Y", "L_X"
# The shape of a pipe without via points, by the axis each end leaves on, start then end: `v` a top or
# bottom side, `h` a left or right side, `-` an end with no side (a junction, a loose end). A layouter
# that must know where a pipe will run reads this table (the library profile publishes it) and need
# not restate the rule.
ROUTES = {"vv": Z_Y, "hh": Z_X,
          "vh": L_Y, "v-": L_Y, "hv": L_X, "h-": L_X,
          "-v": L_X, "-h": L_Y, "--": L_Y}
VIA = L_X   # between consecutive via points that share neither x nor y


def _axis(side) -> str:
    return "-" if not side else ("v" if _vertical(side) else "h")


def _shape(p0, p1, shape):
    (x0, y0), (x1, y1) = p0, p1
    if shape == Z_Y:
        ym = round((y0 + y1) / 2)
        return [p0, (x0, ym), (x1, ym), p1]
    if shape == Z_X:
        xm = round((x0 + x1) / 2)
        return [p0, (xm, y0), (xm, y1), p1]
    if shape == L_Y:
        return [p0, (x0, y1), p1]
    return [p0, (x1, y0), p1]


def route(p0, s0, p1, s1, via=()):
    """Orthogonal polyline. With via points, elbows (`VIA`) are inserted between consecutive points;
    without, the shape `ROUTES` names for the axes the two ends leave on: a Z when both leave on the
    same axis and an L when they differ."""
    pts = [p0] + [tuple(v) for v in via] + [p1]
    if via:
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            if a[0] != b[0] and a[1] != b[1]:
                out.append(_shape(a, b, VIA)[1])
            out.append(b)
        return _dedupe(out)
    if p0[0] == p1[0] or p0[1] == p1[1]:
        return [p0, p1]
    return _shape(p0, p1, ROUTES[_axis(s0) + _axis(s1)])


def _dedupe(pts):
    out = []
    for p in pts:
        if not out or out[-1] != p:
            out.append(p)
    return out


def path_d(pts) -> str:
    def f(v):
        return str(int(v)) if float(v).is_integer() else f"{v:.1f}"
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts)
