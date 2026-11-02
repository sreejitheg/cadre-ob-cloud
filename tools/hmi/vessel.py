"""A vessel as a container: what the layout rule L10 (`page_checks.py`) and the gate G5 (`gates.py`) allow inside it.

A vessel (the library's tank) holds what the original draws inside it, as a wet well holds its level instruments
(WorkflowBuilder WFB-213, COB-191). A label or a symbol wholly inside a vessel's box is placed there on purpose, provided
it keeps clear of the bands where the vessel draws its own texts and level. The bands are the positions of
`library.tank()`, as fractions of the vessel's box (x, y, width, height), each with the parameter and the value that
show it; a parameter the symbol does not give takes the view's default (`library.TANK_PARAMS`). `tests/test_page_checks.py`
pins both to the view. A box that crosses the vessel's outline, or covers one of its bands, is still an overlap.
"""
from __future__ import annotations

CONTAINER_KINDS = {"tank"}                               # the descriptor kinds
CONTAINER_VIEWS = {"Automation/Tank", "cadre.ob.tank"}   # the library view and the module component that draw them
DEFAULTS = {"static": False, "hasCapacity": True, "hasTag": True, "showPercent": True, "compact": False, "chart": False}
BANDS = {
    "static": [("capacity", (0.06, 0.26, 0.88, 0.24), "hasCapacity", True),
               ("identifier", (0.0, 0.76, 1.0, 0.2), "hasTag", True)],
    "live": [("identifier", (0.07, 0.06, 0.86, 0.09), "hasTag", True),
             ("percentage", (0.05, 0.15, 0.9, 0.2), "showPercent", True),
             ("value", (0.05, 0.36, 0.9, 0.11), "compact", False),
             ("level", (0.08, 0.62, 0.84, 0.3), "chart", False),
             ("trend chart", (0.08, 0.5, 0.84, 0.42), "chart", True)],
}


def bands(params: dict | None, box: tuple) -> list[tuple[str, tuple]]:
    """(name, (x, y, w, h) on the page) of each band where a vessel with these parameters draws its own text or level,
    for its box (x, y, w, h)."""
    shown = {**DEFAULTS, **(params or {})}
    out = []
    for name, (fx, fy, fw, fh), param, when in BANDS["static" if shown["static"] else "live"]:
        if shown[param] == when:
            out.append((name, (box[0] + fx * box[2], box[1] + fy * box[3], fw * box[2], fh * box[3])))
    return out


def inside(a: tuple, b: tuple, tol: float) -> bool:
    """Box a (x, y, w, h) lies wholly inside box b, within tol pixels."""
    return (a[0] >= b[0] - tol and a[1] >= b[1] - tol
            and a[0] + a[2] <= b[0] + b[2] + tol and a[1] + a[3] <= b[1] + b[3] + tol)


def crossing(a: tuple, b: tuple, tol: float) -> bool:
    """Boxes a and b (x, y, w, h) share more than tol pixels each way."""
    return (min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]) > tol
            and min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]) > tol)


def placed_inside(a: tuple, vessel_box: tuple, params: dict | None, tol: float) -> tuple[bool, list[str]]:
    """Whether box a lies wholly inside the vessel, and the vessel's bands it covers: (True, []) is a box placed in the
    vessel on purpose."""
    if not inside(a, vessel_box, tol):
        return False, []
    return True, [name for name, band in bands(params, vessel_box) if crossing(a, band, tol)]
