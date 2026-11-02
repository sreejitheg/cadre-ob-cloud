"""The one form of an alarm in a tag model over the Cadre HMI library (COB-140; findings F028, F042, F043
and F045 of the ASMP study, COBD-044).

A tool that writes the tag model of a project over this library (the sample plants of `tools/plants`, ctig
for a migrated plant) writes each alarm through `definition`, so that the alarms of every project read
alike and the frame can rely on them:

1. One label form, `<identifier> <text>` (F042): the studied project wrote eight forms by hand.
2. A display path of the device's node in the plant hierarchy, `<node>/<identifier>` (F042; the node of a
   page is `screen.node` of its descriptor, page 08 section 3): the alarms of one area group and filter
   together on the alerts page.
3. One of the five priorities of `cadre.hmi.PRIORITIES`. A report of a state takes Diagnostic (F043),
   which draws no alert colour (F053) and so does not compete with the alarms an operator must answer.
4. Shelving allowed for every priority but Critical (F045: shelving with a time limit), and the
   library's alarm tables offer only the times of SHELVE_SECONDS, eight hours the longest, so no alarm is
   shelved without an end.
5. Where the device carries a limit's delay member (`<limit>Delay`, seconds), the alarm's on-delay
   follows it (F028), as its setpoint follows the limit (COB-062). Both are alarm properties bound by
   expression; the setpoint's form is measured on the gateway, the on-delay's is to be (COB-143).

The library profile states the same form under `alarms` (`form`), for a tool that does not import this
module.
"""
from __future__ import annotations

from . import scripts

PRIORITIES = tuple(scripts.constant("PRIORITIES"))
STATE_REPORT = "Diagnostic"
NOT_SHELVED = ("Critical",)
# The shelving times the library's alarm status tables offer, in seconds (`shelvingTimes`,
# IGW ia.display.alarmstatustable): from 5 minutes to 8 hours.
SHELVE_SECONDS = [300, 900, 1800, 3600, 7200, 14400, 28800]
DELAY_SUFFIX = scripts.constant("DELAY_SUFFIX")
LABEL_FORM = "{identifier} {text}"
DISPLAY_PATH_FORM = "{node}/{identifier}"


def label(identifier: str, text: str) -> str:
    """The alarm's label: the device's identifier and the alarm's text."""
    return LABEL_FORM.format(identifier=identifier, text=text)


def display_path(node: str, identifier: str) -> str:
    """The alarm's display path: the device's node and its identifier; the identifier alone without a node."""
    return DISPLAY_PATH_FORM.format(node=node, identifier=identifier) if node else identifier


def definition(name: str, identifier: str, text: str, priority: str, node: str = "", *, mode: str | None = None,
               setpoint: float = 1.0, limit: str | None = None, delay: bool = False) -> dict:
    """One alarm of a tag in the library's form. With `limit`, the setpoint follows that member of the
    device folder; with `delay` as well, the on-delay follows the limit's delay member."""
    if priority not in PRIORITIES:
        raise ValueError(f"priority {priority!r} is not one of {list(PRIORITIES)}")
    a = {"name": name, "label": label(identifier, text), "displayPath": display_path(node, identifier),
         "priority": priority, "shelvingAllowed": priority not in NOT_SHELVED,
         "setpointA": {"bindType": "Expression", "value": "{[.]" + limit + "}"} if limit else setpoint}
    if mode:
        a["mode"] = mode
    if delay:
        if not limit:
            raise ValueError("an on-delay follows the delay member of a limit; name the limit")
        a["timeOnDelaySeconds"] = {"bindType": "Expression", "value": "{[.]" + limit + DELAY_SUFFIX + "}"}
    return a


def form() -> dict:
    """The form, as the library profile states it."""
    return {"label": LABEL_FORM, "displayPath": DISPLAY_PATH_FORM, "priorities": list(PRIORITIES),
            "stateReport": STATE_REPORT, "shelvable": {p: p not in NOT_SHELVED for p in PRIORITIES},
            "shelvingTimes": list(SHELVE_SECONDS), "delaySuffix": DELAY_SUFFIX}
