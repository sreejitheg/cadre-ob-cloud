"""Experiment E1: does the parent project carry the design system to a child?

Questions, each answered by measurement on the 8.3.6 gateway (recorded in wiki page 07):

  Q1  A child inherits the parent's `stylesheet.css`.
  Q2  A child inherits the parent's style classes, views and session props.
  Q3  Palette variables set by a class on a page root reach an embedded view's SVG fill.
  Q4  `props.elements[0].fill.paint` accepts a `var()` and a binding on that path works.
  Q5  Switching `session.custom.palette` re-themes the page.

Writes two projects to `workspace/e1/` and, with `--deploy`, imports both through the
gateway REST lane (parent first).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from hmi import pv, theme  # noqa: E402

ROOT = HERE.parent
PARENT, CHILD = "cadre_hmi_e1base", "cadre_hmi_e1lab"


def icon(name: str) -> dict:
    return json.loads((ROOT / "library/icons" / f"{name}.json").read_text(encoding="utf-8"))


def pump_view() -> dict:
    on = "{view.params.on}"
    holder = pv.node("ia.shapes.svg", "Holder", pv.cpos(6, 6, 36, 36), {
        "viewBox": "0 0 36 36",
        "elements": [{"type": "path", "name": "ring",
                      "d": "M0.5 18a17.5 17.5 0 1 0 35 0a17.5 17.5 0 1 0 -35 0Z",
                      "fill": {"paint": "var(--automation-button-off-background-color)"},
                      "stroke": {"paint": "var(--automation-button-off-border-color)", "width": 1}}]},
        prop_config={
            "props.elements[0].fill.paint": pv.bind(pv.expr(
                f"if({on}, 'var(--on-background-color)', 'var(--automation-button-off-background-color)')")),
            "props.elements[0].stroke.paint": pv.bind(pv.expr(
                f"if({on}, 'var(--on-border-color)', 'var(--automation-button-off-border-color)')")),
        })
    ion, ioff = icon("pump-on-horizontal"), icon("pump-off-horizontal")
    icon_on = pv.node("ia.shapes.svg", "IconOn", pv.cpos(12, 12, 24, 24),
                      {"viewBox": ion["viewBox"], "elements": ion["elements"]},
                      prop_config={"meta.visible": pv.bind(pv.expr(on))})
    icon_off = pv.node("ia.shapes.svg", "IconOff", pv.cpos(12, 12, 24, 24),
                       {"viewBox": ioff["viewBox"], "elements": ioff["elements"]},
                       prop_config={"meta.visible": pv.bind(pv.expr(f"!{on}"))})
    root = pv.node("ia.container.coord", "root", {}, {"style": {"overflow": "hidden"}},
                   children=[holder, icon_on, icon_off])
    return pv.view(root, params={"on": False, "tagName": ""},
                   param_dirs={"on": "input", "tagName": "input"}, size={"width": 48, "height": 48})


def lab_view() -> dict:
    kids = []
    for i, on in enumerate((True, False)):
        kids.append(pv.node("ia.display.view", f"Pump{i}", pv.cpos(40 + 80 * i, 40, 48, 48),
                            {"path": "Symbols/Pump", "params": {"on": on, "tagName": f"P{i}"}}))
    kids.append(pv.node("ia.display.label", "PaletteLabel", pv.cpos(40, 120, 400, 32),
                        {"style": {"color": "var(--element-active-color)",
                                   "fontFamily": "var(--font-family-main)", "fontSize": "16px"}},
                        prop_config={"props.text": pv.bind(pv.expr(
                            "'Palette: ' + coalesce({session.custom.palette}, 'unset')"))}))
    for i, p in enumerate(theme.PALETTES):
        kids.append(pv.node("ia.input.button", f"Btn_{p}", pv.cpos(40 + 110 * i, 180, 100, 36),
                            {"text": p},
                            events=pv.on_action([f"self.session.custom.palette = '{p}'"])))
    root = pv.node("ia.container.coord", "root", {},
                   {"style": {"overflow": "hidden", "backgroundColor": "var(--container-background-color)"}},
                   prop_config={"props.style.classes": theme.palette_root_binding()},
                   children=kids)
    return pv.view(root, size={"width": 600, "height": 260})


def build() -> tuple[pv.Project, pv.Project]:
    tokens = theme.load_tokens(ROOT / "library/tokens/openbridge-tokens.json")
    parent = pv.Project(PARENT, "Cadre HMI E1 base", inheritable=True,
                        description="E1 inheritance experiment, parent")
    parent.set_stylesheet(theme.stylesheet(tokens, size_vars=set()))
    for p in theme.PALETTES:
        parent.add_style_class(f"cadre/palette/{p}", {})
    parent.set_session_props({"custom": {"palette": "day"}, "props": {}})
    parent.add_view("Symbols/Pump", pump_view())
    child = pv.Project(CHILD, "Cadre HMI E1 lab", parent=PARENT,
                       description="E1 inheritance experiment, child")
    child.set_page_config({"pages": {"/": {"title": "Lab", "viewPath": "Lab/Main"}}})
    child.add_view("Lab/Main", lab_view())
    return parent, child


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "workspace/e1"))
    ap.add_argument("--deploy", action="store_true")
    a = ap.parse_args()
    parent, child = build()
    for p in (parent, child):
        d = p.write(Path(a.out))
        print("wrote", d, len(p.files), "files")
    if a.deploy:
        from hmi import deploy
        for p in (parent, child):
            print(p.name, deploy.import_project(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
