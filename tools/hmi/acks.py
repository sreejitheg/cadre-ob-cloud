"""Ack selected and Ack all under an alarm list (L5, COB-166; wiki page 13 section 10.6).

Two buttons in the library's style under each alarm list, and the library's Confirm row for Ack all:

* **Ack selected** acknowledges the rows the operator selected: the stock table's `selection.active.data`, or the
  module list's `selectedIds` (`selectable`, module 0.4.2). It is disabled while nothing is selected.
* **Ack all** acknowledges the unacknowledged alarms the list shows (the node and its subtree, the filters applied), after
  "Acknowledge N alarms?" with Confirm and Cancel. The stock table writes what it shows back to its props
  (`filters.active.results`); the module's list shows the alerts its view polled.

Privileges: the stock tables acknowledge under W7 (their own `enableAcknowledge`), so the pages and the stock panels use
W7 for both buttons; the module's panels use W8 for Ack selected and W9 for Ack all (the paths of the module's own ACK
and ACK visible). The buttons show to everyone and are disabled without the privilege, as every other command is
(`framework._can`); the checked write (`cadre.hmi.ack`) refuses again.
"""
from __future__ import annotations

from . import pv

CAPTION_SELECTED, CAPTION_ALL = "Ack selected", "Ack all"
PENDING = {"active": False, "ids": [], "text": ""}


def custom(*selections: str) -> dict:
    """The view custom the bar reads and writes: the selection of each list, the unacknowledged ids shown, the pending
    question and the message under the buttons."""
    return {**{name: [] for name in selections}, "shown": [], "unacked": 0, "ackPending": dict(PENDING),
            "ackMessage": ""}


def stock_props() -> dict:
    """The props of a stock alarm status table that has the bar: the table writes what it shows back to its props
    (`filters.active.results`, off by default), which Ack all reads."""
    from .framework import TABLE_PROPS
    return {**TABLE_PROPS, "filters": {"active": {"results": {"enabled": True}}}}


def stock_config(table: str) -> dict:
    """The view's custom bindings for a bar over the stock table named `table`, a child of the view's root: the
    selected rows, the rows it shows and how many of them are unacknowledged."""
    return {"custom.selected": pv.bind(pv.prop(f"/root/{table}.props.selection.active.data")),
            "custom.shown": pv.bind(pv.prop(f"/root/{table}.props.filters.active.results.data")),
            "custom.unacked": unacked_binding("{view.custom.shown}")}


def bar(*, selections: list[str], can_selected: str, can_all: str, path_selected: str, path_all: str,
        selectable: bool = True, display: str | None = None) -> list[dict]:
    """The bar and the Confirm row, two children of the view's root column. `selections` are the view custom
    properties that hold a list's selection; `can_selected` and `can_all` the write paths whose permission enables the
    buttons and which the acknowledgement is made under. Without `selectable` (a module list that has no tick boxes)
    there is no Ack selected."""
    from .framework import CANCEL, CONFIRM, _can, _label

    chosen = " + ".join(f"len({{view.custom.{n}}})" for n in selections) or "0"
    groups = ", ".join(f"self.view.custom.{n}" for n in selections)
    note = _label("AckMessage", pv.fpos(grow=1, basis="0px"), "{view.custom.ackMessage}",
                  classes="cadre/font/label cadre/text/neutral", style={"whiteSpace": "normal"})
    kids = [note]
    if selectable:
        kids.append(pv.node("ia.input.button", "AckSelected", pv.fpos(basis="116px", shrink=0), {
            "text": CAPTION_SELECTED, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "32px"}},
            prop_config={"props.enabled": pv.bind(pv.expr(f"{{view.custom.can.{can_selected}}} && {chosen} > 0"))},
            events=pv.on_action([
                f"ids = cadre.hmi.selected_ids({groups})",
                f"self.view.custom.ackMessage = cadre.hmi.ack_listed(ids, self.session, '{path_selected}')"])))
    kids.append(pv.node("ia.input.button", "AckAll", pv.fpos(basis="96px", shrink=0), {
        "text": CAPTION_ALL, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "32px"}},
        prop_config={"props.enabled": pv.bind(pv.expr(
            f"{{view.custom.can.{can_all}}} && {{view.custom.unacked}} > 0"))},
        events=pv.on_action([
            "ids = cadre.hmi.unacked_ids(self.view.custom.shown)",
            "if len(ids) > 0:",
            "\tself.view.custom.ackPending = {'active': True, 'ids': ids, "
            "'text': 'Acknowledge ' + str(len(ids)) + (' alarm?' if len(ids) == 1 else ' alarms?')}"])))
    row = pv.node("ia.container.flex", "AckBar", pv.fpos(basis="40px", shrink=0), {
        "direction": "row", "alignItems": "center", "style": {"gap": "8px", "padding": "0 4px"}}, children=kids,
        prop_config={"position.display": pv.bind(pv.expr(display))} if display else None)
    clear = f"self.view.custom.ackPending = {PENDING!r}"
    confirm = pv.node("ia.container.flex", "AckConfirm", pv.fpos(basis="44px", shrink=0), {
        "direction": "row", "alignItems": "center",
        "style": {"gap": "8px", "classes": "cadre/alert/badge-caution", "padding": "0 8px", "borderRadius": "4px"}},
        prop_config={"position.display": pv.bind(pv.expr("{view.custom.ackPending.active}"
                                                         + (f" && ({display})" if display else "")))},
        children=[
            _label("AckConfirmText", pv.fpos(grow=1, basis="0px"), "{view.custom.ackPending.text}",
                   classes="cadre/font/body-active cadre/text/active", style={"whiteSpace": "normal"}),
            pv.node("ia.input.button", "AckConfirmYes", pv.fpos(basis="96px", shrink=0), {
                "text": CONFIRM, "style": {"classes": "cadre/button/normal cadre/font/button", "height": "36px"}},
                prop_config={"props.enabled": pv.bind(pv.expr(f"{{view.custom.can.{can_all}}}"))},
                events=pv.on_action([
                    "self.view.custom.ackMessage = cadre.hmi.ack_listed("
                    f"self.view.custom.ackPending.ids, self.session, '{path_all}')",
                    clear])),
            pv.node("ia.input.button", "AckConfirmNo", pv.fpos(basis="96px", shrink=0), {
                "text": CANCEL, "style": {"classes": "cadre/button/flat cadre/font/button", "height": "36px"}},
                events=pv.on_action([clear]))])
    return [row, confirm]


def unacked_binding(shown: str) -> dict:
    """`custom.unacked`: how many unacknowledged alarms the list shows, which enables Ack all."""
    return pv.bind(pv.expr(shown), [pv.script_transform(["return len(cadre.hmi.unacked_ids(value))"])])
