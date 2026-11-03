"""Tests of the page parts (COB-159, the eng02 ASM gaps GP, GM and GG): command buttons, range bars,
embedded trends, line styles, the duty and out of service marks, fault rows and the scale to the window.

Run from the repository root:  python -m unittest discover -s tests
"""
import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from hmi import framework, gates, library, library_profile, navigation, parent as par, parts, pv, screen, scripts  # noqa: E402

DOCKED_TERM = "if(coalesce({session.custom.faceplateDocked}, false), 400, 0)"

SAMPLE = ROOT / "tests" / "fixtures" / "page-parts.json"


def sample():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------
# The library scripts, Jython held as text, run under CPython against fakes
# ---------------------------------------------------------------------------------------

# The fit's expression evaluated in Python: if() and && of the expression language, the measured canvas as CW and CH.
EXPR_NS = {"iff": lambda c, a, b: a if c else b, "coalesce": lambda x, d: d if x is None else x}


def expr_py(e: str) -> str:
    return (e.replace("if(coalesce({view.custom.canvasW}, 0)", "iff(coalesce({view.custom.canvasW}, 0)")
            .replace("{view.custom.canvasW}", "CW").replace("{view.custom.canvasH}", "CH").replace("&&", " and "))


class Auth:
    def __init__(self, roles):
        self.authenticated = roles is not None
        self.user = type("U", (), {"roles": roles, "userName": "someone" if roles is not None else None})()


def session(roles, commands=(), devices=()):
    custom = type("C", (), {"devices": [dict(d) for d in devices], "commands": [dict(c) for c in commands],
                            "alarmScope": "*"})()
    return type("S", (), {"props": type("P", (), {"auth": Auth(roles)})(), "custom": custom})()


def hmi(tags=None, refuse=(), events=()):
    """`cadre.hmi` against a fake gateway: `tags` {path: value}; a write to a path in `refuse` answers a bad
    quality; `system.util.invokeAsynchronous` records the call and runs nothing."""
    tags = dict(tags or {})
    log = {"writes": [], "async": [], "queries": []}

    class QV:
        def __init__(self, v):
            self.value = v

    class Tag:
        exists = staticmethod(lambda p: p in tags)
        readBlocking = staticmethod(lambda paths: [QV(tags.get(p)) for p in paths])

        @staticmethod
        def writeBlocking(paths, values):
            out = []
            for p, v in zip(paths, values):
                log["writes"].append((p, v))
                if p in refuse:
                    out.append('Bad_ReadOnly("Tag value source does not support writing.")')
                else:
                    tags[p] = v
                    out.append("Good")
            return out

    class Util:
        @staticmethod
        def invokeAsynchronous(function, args=None, kwargs=None, description=None):
            log["async"].append((function, list(args or [])))

    class Alarm:
        @staticmethod
        def queryStatus(path=None, state=None, priority=None):
            log["queries"].append(list(path))
            return list(events)

    class System:
        tag, util, alarm = Tag, Util, Alarm
    ns = {"unicode": str, "long": int, "system": System}
    exec(scripts.HMI, ns)
    return ns, log, tags


COMMAND = {"path": "[default]plant/sim/reset", "ms": 5000}


class PagePulseTests(unittest.TestCase):
    """`cadre.hmi.page_pulse`, write path W18: the role is asked first, a tag the descriptors did not declare is
    never written, true is written and false follows after the declared length."""

    def test_role_first_then_the_declared_tag(self):
        ns, log, tags = hmi({COMMAND["path"]: False})
        for roles in (None, [], ["Operator"]):
            self.assertEqual(ns["page_pulse"](session(roles, [COMMAND]), COMMAND["path"]), ns["REFUSED"], roles)
        self.assertEqual(ns["page_pulse"](session(None), "[default]anything"), ns["REFUSED"])   # asked first: no news of a tag
        self.assertEqual(log["writes"], [])
        admin = session(["Administrator"], [COMMAND])
        self.assertEqual(ns["page_pulse"](admin, COMMAND["path"]), "")
        self.assertEqual(log["writes"], [(COMMAND["path"], True)])
        self.assertTrue(tags[COMMAND["path"]])

    def test_false_follows_after_the_length(self):
        import time
        ns, log, tags = hmi({COMMAND["path"]: False})
        ns["page_pulse"](session(["Administrator"], [COMMAND]), COMMAND["path"])
        (release, args), = log["async"]
        self.assertEqual(args, [COMMAND["path"], 5000])
        slept = []
        real = time.sleep
        time.sleep = slept.append
        try:
            release(*args)
        finally:
            time.sleep = real
        self.assertEqual(slept, [5.0])
        self.assertEqual(log["writes"], [(COMMAND["path"], True), (COMMAND["path"], False)])
        self.assertFalse(tags[COMMAND["path"]])

    def test_a_tag_the_descriptors_did_not_declare_is_never_written(self):
        other = "[default]plant/sim/other"
        ns, log, _ = hmi({COMMAND["path"]: False, other: False})
        admin = session(["Administrator"], [COMMAND])
        for path in (other, "", None, COMMAND["path"] + "/x", COMMAND["path"].upper(), 12):
            self.assertEqual(ns["page_pulse"](admin, path), "Refused: not a command of this project", path)
        self.assertEqual(ns["page_pulse"](session(["Administrator"]), COMMAND["path"]),
                         "Refused: not a command of this project")   # a project with no commands
        self.assertEqual(log["writes"], [])
        self.assertEqual(log["async"], [])

    def test_a_missing_tag_a_bad_length_and_a_refusing_gateway(self):
        ns, log, _ = hmi({})
        self.assertEqual(ns["page_pulse"](session(["Administrator"], [COMMAND]), COMMAND["path"]), "Refused: no such tag")
        ns, log, _ = hmi({COMMAND["path"]: False})
        for ms in (0, 99, 600001, "x", None):
            self.assertTrue(ns["page_pulse"](session(["Administrator"], [{"path": COMMAND["path"], "ms": ms}]),
                                             COMMAND["path"]).startswith("Refused: the "), ms)
        self.assertEqual(log["writes"], [])
        ns, log, _ = hmi({COMMAND["path"]: False}, refuse=[COMMAND["path"]])
        msg = ns["page_pulse"](session(["Administrator"], [COMMAND]), COMMAND["path"])
        self.assertIn("Refused: the gateway did not write", msg)
        self.assertEqual(log["async"], [])   # nothing is released that was not written

    def test_the_gate_reads_the_call_as_write_path_w18(self):
        self.assertEqual(gates.NAME_PATH["page_pulse"], "W18")
        self.assertEqual(gates._paths_called("msg = cadre.hmi.page_pulse(self.session, 'x')"), ["W18"])
        self.assertEqual(gates._paths_called("f = cadre.hmi.page_pulse"), ["W18"])
        self.assertEqual(parts.PULSE_PATH, "W18")


class RangeBarElementsTests(unittest.TestCase):
    """`cadre.hmi.range_bar_elements`: the bar's geometry from the parameters, in plain numbers."""

    def setUp(self):
        self.ns, _, _ = hmi()
        self.bar = self.ns["range_bar_elements"]

    def by_name(self, spec):
        return {e["name"]: e for e in self.bar(spec)}

    def test_track_band_limits_and_value(self):
        got = self.by_name("55|0|100|20|80|10|90|false")
        self.assertEqual(list(got), ["track", "normal", "lowLimit", "highLimit", "value"])
        self.assertEqual(got["track"]["d"], "M0.00 3.00H100.00V7.00H0.00Z")
        self.assertEqual(got["normal"]["d"], "M20.00 2.00H80.00V8.00H20.00Z")
        self.assertEqual(got["value"]["d"], "M54.00 0.00H56.00V10.00H54.00Z")
        self.assertEqual(got["value"]["fill"]["paint"], "var(--element-active-color)")
        self.assertEqual(got["lowLimit"]["d"], "M9.40 0.00H10.60V10.00H9.40Z")

    def test_a_value_beyond_a_limit_takes_the_warning_colour(self):
        for value in ("95", "5"):
            self.assertEqual(self.by_name(f"{value}|0|100|20|80|10|90|false")["value"]["fill"]["paint"],
                             "var(--alert-warning-color)", value)
        self.assertEqual(self.by_name("95|0|100|20|80||80|false")["value"]["fill"]["paint"], "var(--alert-warning-color)")
        self.assertEqual(self.by_name("95|0|100|20|80||||false")["value"]["fill"]["paint"], "var(--element-active-color)")

    def test_vertical_puts_the_high_end_at_the_top(self):
        got = self.by_name("75|0|100|||||true")
        self.assertEqual(got["track"]["d"], "M3.00 0.00H7.00V100.00H3.00Z")
        self.assertEqual(got["value"]["d"], "M0.00 24.00H10.00V26.00H0.00Z")   # 75 % up: 25 from the top, a 2 wide marker

    def test_what_is_absent_is_not_drawn(self):
        self.assertEqual(list(self.by_name("55|0|100||||||false")), ["track", "value"])
        self.assertEqual(list(self.by_name("|0|100|||||false")), ["track"])                  # no value: no marker
        self.assertEqual(list(self.by_name("5|0|0|||||false")), ["track"])                   # no span
        self.assertEqual(list(self.by_name("5|10|0|1|2|||false")), ["track"])                # reversed span
        self.assertEqual(list(self.by_name("55|0|100|80|20|||false")), ["track", "value"])   # a band that runs backwards
        self.assertEqual([e["name"] for e in self.bar("")], ["track"])
        self.assertEqual([e["name"] for e in self.bar(None)], ["track"])
        self.assertEqual([e["name"] for e in self.bar("not|a|number|at|all")], ["track"])

    def test_the_marker_stays_inside_the_bar_and_nothing_is_written_with_an_exponent(self):
        got = self.by_name("1000|0|100|||||false")
        self.assertEqual(got["value"]["d"], "M98.00 0.00H100.00V10.00H98.00Z")
        got = self.by_name("-1e9|0|100|||||false")
        self.assertEqual(got["value"]["d"], "M0.00 0.00H2.00V10.00H0.00Z")
        for e in self.bar("1.0E-4|0.0|1.0E-3|||||false"):
            self.assertNotIn("e", e["d"].replace("Z", "").replace("H", "").replace("V", "").replace("M", "").lower())


class FaultSourceTests(unittest.TestCase):
    """A fault row's alarms are on a tag: `tag_source`, `device_sources` and `alert_states` (F016)."""

    def test_tag_source(self):
        ns, _, _ = hmi()
        self.assertEqual(ns["tag_source"]("[default]site/gen/F1"), "prov:default:/tag:site/gen/F1:/alm:*")
        self.assertEqual(ns["tag_source"]("[default]site/gen/F1/"), "prov:default:/tag:site/gen/F1:/alm:*")
        for bad in ("site/gen/F1", "[]x", "[default]", "", None):
            self.assertEqual(ns["tag_source"](bad), ns["NO_MATCH"], bad)

    def test_device_sources_takes_a_tag_key_and_leaves_a_device_alone(self):
        ns, _, _ = hmi()
        s = session(["Administrator"])
        self.assertEqual(ns["device_sources"](s, "tag:[default]site/F1"), ["prov:default:/tag:site/F1:/alm:*"])
        self.assertEqual(ns["device_sources"](s, "[default]site/P1"), ["prov:default:/tag:site/P1/*"])

    def test_alert_states_follows_the_alarms_on_the_tag(self):
        class Event:
            def __init__(self, source, priority, acked=False):
                self.s, self.p, self.a = source, priority, acked

            def getSource(self): return self.s
            def getPriority(self): return self.p
            def isCleared(self): return False
            def isAcked(self): return self.a
        events = [Event("prov:default:/tag:site/F1:/alm:Low oil", "Medium"),
                  Event("prov:default:/tag:site/F2:/alm:High temp", "High", acked=True)]
        ns, log, _ = hmi(events=events)
        got = ns["alert_states"](session(["Administrator"]), {"a_F1": "tag:[default]site/F1",
                                                              "a_F2": "tag:[default]site/F2",
                                                              "a_F3": "tag:[default]site/F3"})
        self.assertEqual((got["a_F1"]["alert"], got["a_F1"]["status"], got["a_F1"]["mode"]), (True, "warning", "unacked-active"))
        self.assertEqual((got["a_F2"]["alert"], got["a_F2"]["status"], got["a_F2"]["mode"]), (True, "alarm", "acked-active"))
        self.assertFalse(got["a_F3"]["alert"])
        self.assertEqual(len(log["queries"]), 1)   # one query for the whole page, as for devices


# ---------------------------------------------------------------------------------------
# The generator
# ---------------------------------------------------------------------------------------
class GeneratorCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prj, cls.contracts = par.build_parent()

    def tearDown(self):
        screen.RENDER["target"] = "stock"

    def build(self, desc=None, render="stock"):
        screen.RENDER["target"] = render
        doc, info = screen.build_screen(copy.deepcopy(desc or sample()), self.contracts)
        return doc, info

    @staticmethod
    def nodes(doc):
        out = {}

        def walk(n):
            out[n["meta"]["name"]] = n
            for c in n.get("children") or []:
                walk(c)
        walk(doc["root"])
        return out

    def expr(self, node, key):
        return node["propConfig"][key]["binding"]["config"]["expression"]


class SchemaTests(GeneratorCase):
    def errors(self, desc):
        return screen.schema_errors([desc], ["d"])

    def test_the_sample_is_a_valid_descriptor(self):
        self.assertEqual(self.errors(sample()), [])

    def test_each_part_is_checked_by_the_schema(self):
        def broken(mutate):
            d = sample()
            mutate(d)
            return self.errors(d)
        self.assertTrue(broken(lambda d: d["buttons"][0]["action"].update(ms=50)))                  # a pulse under 100 ms
        self.assertTrue(broken(lambda d: d["buttons"][0]["action"].update(ms=700000)))
        self.assertTrue(broken(lambda d: d["buttons"][0]["action"].update(type="write")))          # not an action
        self.assertTrue(broken(lambda d: d["buttons"][0].pop("label")))
        self.assertTrue(broken(lambda d: d["buttons"][0].update(colour="red")))                     # no unknown key
        self.assertTrue(broken(lambda d: d["trends"][0]["pens"].append(d["trends"][0]["pens"][0]) or d["trends"][0]["pens"].append({"tag": "x"})))
        self.assertTrue(broken(lambda d: d["trends"][0].update(pens=[])))
        self.assertTrue(broken(lambda d: d["lines"][0].update(points=[[1, 2]])))
        self.assertTrue(broken(lambda d: d["lines"][1].update(gate={"tag": "a", "symbol": "b"})))
        self.assertTrue(broken(lambda d: d["bars"][0].pop("value")))
        self.assertTrue(broken(lambda d: d["symbols"][0]["bar"].update(side="diagonal")))
        self.assertTrue(broken(lambda d: d["screen"].update(fit="yes")))
        self.assertTrue(broken(lambda d: d["links"][0].pop("route")))
        self.assertTrue(broken(lambda d: d["wells"][0].update(marks=[])))
        self.assertTrue(broken(lambda d: d["wells"][0]["marks"][0].update(level=1.5)))
        self.assertTrue(broken(lambda d: d["labels"][0].update(emphasis={"tag": "a", "symbol": "b"})))
        self.assertTrue(broken(lambda d: d["brackets"][0].update(side="left")))
        self.assertEqual(broken(lambda d: d["screen"].update(fit={"reserveX": 400})), [])


class ButtonTests(GeneratorCase):
    def test_a_pulse_asks_first_and_is_gated_by_w18(self):
        doc, info = self.build()
        self.assertEqual(info["errors"], [])
        n = self.nodes(doc)
        b = n["Button_reset"]
        self.assertEqual((b["position"]["x"], b["position"]["y"], b["position"]["width"], b["position"]["height"]),
                         (1300, 20, 240, 36))
        press, ask, yes, no = n["Press"], n["Question"], n["Confirm"], n["Cancel"]
        # the first press writes nothing: it only asks
        script = press["events"]["component"]["onActionPerformed"]["config"]["script"]
        self.assertNotIn("cadre.hmi", script)
        self.assertIn("pend_reset = True", script)
        self.assertEqual(ask["props"]["text"], "Reset the plant?")
        self.assertEqual(self.expr(press, "position.display"), "!{view.custom.pend_reset}")
        for node in (ask, yes, no):
            self.assertEqual(self.expr(node, "position.display"), "{view.custom.pend_reset}")
        # Confirm makes the one checked write; both buttons that can reach it follow the permission of W18
        self.assertIn("cadre.hmi.page_pulse(self.session, '[default]cadre_hmi_parts/sim/reset')",
                      yes["events"]["component"]["onActionPerformed"]["config"]["script"])
        self.assertEqual(self.expr(yes, "props.enabled"), "{view.custom.can.W18}")
        self.assertEqual(self.expr(press, "props.enabled"), "{view.custom.can.W18}")
        self.assertEqual(no["events"]["component"]["onActionPerformed"]["config"]["script"], "\tself.view.custom.pend_reset = False")
        self.assertEqual(doc["custom"]["pend_reset"], False)
        self.assertIn("custom.can", doc["propConfig"])

    def module_sample(self, render="module"):
        d = sample()
        d["buttons"][0]["render"] = "module"
        return self.build(d, render=render)

    def test_the_module_button_asks_and_the_same_confirm_makes_the_pulse(self):
        """Spike T0 wrap W3: `render: module` under the module rendering draws the question button as `cadre.ob.button`.
        Its `onPress` only asks; the Confirm button, unchanged, calls `page_pulse` (write path W18, the role check,
        the declared tag) with `enabled` bound to the permission of W18; so nothing new writes."""
        doc, info = self.module_sample()
        self.assertEqual(info["errors"], [])
        n = self.nodes(doc)
        press, yes = n["Press"], n["Confirm"]
        self.assertEqual(press["type"], "cadre.ob.button")
        self.assertEqual(list(press["events"]), ["component"])
        self.assertEqual(list(press["events"]["component"]), ["onPress"])
        script = press["events"]["component"]["onPress"]["config"]["script"]
        self.assertNotIn("cadre.hmi", script)                       # a press writes nothing: it asks
        self.assertIn("pend_reset = True", script)
        self.assertEqual(gates._paths_called(script), [])
        confirm = yes["events"]["component"]["onActionPerformed"]["config"]["script"]
        self.assertIn("cadre.hmi.page_pulse(self.session, '[default]cadre_hmi_parts/sim/reset')", confirm)
        self.assertEqual(gates._paths_called(confirm), ["W18"])
        self.assertTrue(gates._follows_permissions(yes, "props.enabled", "W18"))
        # the component has no `enabled`: it is static while the session lacks the permission of W18, and shows the label or the answer
        self.assertEqual(self.expr(press, "props.static"), "!{view.custom.can.W18}")
        self.assertNotIn("props.enabled", press["propConfig"])
        self.assertIn("{view.custom.msg_reset}", self.expr(press, "props.tag"))
        self.assertEqual(press["props"]["tag"], "PLANTWIDE RESET")
        self.assertEqual(self.expr(press, "position.display"), "!{view.custom.pend_reset}")
        # the command list the pulse is checked against is the descriptor's, as for the library's button
        self.assertEqual(parts.command_tags(sample())[0]["path"], "[default]cadre_hmi_parts/sim/reset")

    def test_the_module_button_is_drawn_only_under_the_module_rendering(self):
        stock, _ = self.module_sample(render="stock")
        self.assertEqual(self.nodes(stock)["Press"]["type"], "ia.input.button")
        self.assertEqual(self.expr(self.nodes(stock)["Press"], "props.enabled"), "{view.custom.can.W18}")
        plain, _ = self.build(render="module")                       # a pulse that does not ask for it keeps the library's button
        self.assertEqual(self.nodes(plain)["Press"]["type"], "ia.input.button")

    def test_render_module_is_for_a_pulse(self):
        d = sample()
        d["buttons"][1]["render"] = "module"
        self.assertEqual(d["buttons"][1]["action"]["type"], "faceplate")
        _, info = self.build(d, render="module")
        self.assertTrue(any("render: module" in e for e in info["errors"]), info["errors"])
        d["buttons"][1]["render"] = "other"
        self.assertTrue(screen.schema_errors([d], ["d"]))

    def test_a_default_question_is_the_label(self):
        d = sample()
        d["buttons"][0]["action"].pop("confirm")
        n = self.nodes(self.build(d)[0])
        self.assertEqual(n["Question"]["props"]["text"], "PLANTWIDE RESET?")

    def test_a_label_with_a_quote_does_not_break_the_expression(self):
        d = sample()
        d["buttons"][0]["label"] = "Don't \\ stop"
        n = self.nodes(self.build(d)[0])
        self.assertIn("'Don\\'t \\\\ stop'", self.expr(n["Press"], "props.text"))

    def test_a_faceplate_button_calls_open_device_with_its_tab(self):
        n = self.nodes(self.build()[0])
        script = n["Button_alarms"]["events"]["component"]["onActionPerformed"]["config"]["script"]
        want = "\n".join("\t" + ln for ln in library.open_device(
            "'[default]cadre_hmi_parts/P1'", "'pump'", "'Pump 1'", "''", "'alarms'"))
        self.assertEqual(script, want)
        self.assertIn("'Pump 1', '', 'alarms')", script)   # the tab through select_device (COB-158)
        self.assertNotIn("page_pulse", script)
        self.assertNotIn("props.enabled", n["Button_alarms"].get("propConfig", {}))      # opening a faceplate writes nothing

    def test_a_device_by_folder_needs_its_kind(self):
        d = sample()
        d["buttons"][1]["action"] = {"type": "faceplate", "device": "elsewhere/T9", "tab": "home"}
        self.assertTrue(any("state its `kind`" in e for e in self.build(d)[1]["errors"]))
        d["buttons"][1]["action"]["kind"] = "tank"
        doc, info = self.build(d)
        self.assertEqual(info["errors"], [])
        script = self.nodes(doc)["Button_alarms"]["events"]["component"]["onActionPerformed"]["config"]["script"]
        self.assertIn("'[default]cadre_hmi_parts/elsewhere/T9', 'tank', 'T9'", script)

    def test_a_route_button_navigates(self):
        n = self.nodes(self.build()[0])
        self.assertIn("system.perspective.navigate('/alerts')", n["Button_next"]["events"]["component"]["onActionPerformed"]["config"]["script"])

    def test_the_commands_index_lists_each_declared_tag_once(self):
        d = sample()
        d2 = copy.deepcopy(d)
        d2["screen"].update(id="Two", route="/two", view="Screens/Two")
        index = parts.commands_index([d, d2])
        self.assertEqual(index, [{"path": "[default]cadre_hmi_parts/sim/reset", "ms": 5000}])
        d2["buttons"][0]["action"]["ms"] = 1000
        child, reports = screen.build_child("cadre_hmi_parts", [d, d2], "Parts")
        self.assertTrue(any("two lengths" in e for e in reports["/two"]["errors"]), reports["/two"]["errors"])
        sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
        self.assertEqual(sp["custom"]["commands"][0]["path"], "[default]cadre_hmi_parts/sim/reset")

    def test_a_faceplate_button_for_a_device_no_page_marks_is_an_error(self):
        d = sample()
        d["symbols"] = [s for s in d["symbols"] if s["id"] != "P1"]
        d["buttons"][1]["action"] = {"type": "faceplate", "device": "P1", "tab": "alarms", "kind": "pump"}
        child, reports = screen.build_child("cadre_hmi_parts", [d], "Parts")
        self.assertTrue(any("is no device of the page set" in e for e in reports["/page-parts"]["errors"]))


class RangeBarTests(GeneratorCase):
    def test_the_view_has_the_contract_params(self):
        c = self.contracts["Parts/RangeBar"]
        for k in ("value", "min", "max", "normalLo", "normalHi", "loLimit", "hiLimit", "unit", "format", "vertical"):
            self.assertIn(k, c["params"])
        self.assertIsNone(c["params"]["normalLo"])
        doc = json.loads(self.prj.files["com.inductiveautomation.perspective/views/Parts/RangeBar/view.json"])
        self.assertEqual(doc["params"], c["params"])
        bar = self.nodes(doc)["Bar"]
        self.assertEqual(bar["type"], "ia.shapes.svg")
        script = bar["propConfig"]["props.elements"]["binding"]["transforms"][0]["code"]
        self.assertIn("cadre.hmi.range_bar_elements(value)", script)
        expr = bar["propConfig"]["props.elements"]["binding"]["config"]["expression"]
        for p in ("value", "min", "max", "normalLo", "normalHi", "loLimit", "hiLimit"):
            self.assertIn("{view.params.%s}" % p, expr)
        self.assertNotIn("numberFormat", expr)   # no locale in the figures the script reads

    def test_a_bar_beside_a_readout_moves_nothing(self):
        d = sample()
        with_bar, without = self.nodes(self.build(d)[0]), None
        for s in d["symbols"]:
            s.pop("bar", None)
        without = self.nodes(self.build(d)[0])
        for name in ("RD1", "RD2", "P1", "P2", "SW1", "FL1"):
            self.assertEqual(with_bar[name]["position"], without[name]["position"], name)
        self.assertNotIn("Bar_RD1", without)
        bar, rd = with_bar["Bar_RD1"], with_bar["RD1"]
        self.assertEqual(bar["props"]["path"], "Parts/RangeBar")
        self.assertGreaterEqual(bar["position"]["x"], rd["position"]["x"] + rd["position"]["width"])   # to its right
        self.assertEqual(bar["props"]["params"]["normalLo"], 380)
        self.assertEqual(self.build(d)[1]["errors"], [])
        # the value is the readout's own tag
        self.assertEqual(with_bar["Bar_RD1"]["propConfig"]["props.params.value"]["binding"]["config"]["tagPath"],
                         "[default]cadre_hmi_parts/gen/voltage")

    def test_sides_and_overrides(self):
        d = sample()
        boxes = {}
        for side in ("right", "left", "below", "above"):
            d["symbols"][0]["bar"]["side"] = side
            n = self.nodes(self.build(d)[0])
            boxes[side] = n["Bar_RD1"]["position"]
        rd = self.nodes(self.build(d)[0])["RD1"]["position"]
        self.assertLess(boxes["left"]["x"] + boxes["left"]["width"], rd["x"] + 1)
        self.assertGreaterEqual(boxes["below"]["y"], rd["y"] + rd["height"])
        self.assertLessEqual(boxes["above"]["y"] + boxes["above"]["height"], rd["y"])
        d["symbols"][0]["bar"].update(x=10, y=11, w=12, h=13)
        self.assertEqual(self.nodes(self.build(d)[0])["Bar_RD1"]["position"], {"x": 10, "y": 11, "width": 12, "height": 13})

    def test_vertical_bar_is_tall(self):
        d = sample()
        d["symbols"][0]["bar"].update(vertical=True, side="right")
        pos = self.nodes(self.build(d)[0])["Bar_RD1"]["position"]
        self.assertGreater(pos["height"], pos["width"])

    def test_a_standalone_bar_and_the_errors(self):
        n = self.nodes(self.build()[0])
        self.assertEqual(n["Bar_load"]["props"]["params"]["hiLimit"], 90)
        self.assertEqual(n["Bar_load"]["props"]["params"]["unit"], "%")
        d = sample()
        d["symbols"][0]["bind"] = {}
        self.assertTrue(any("`bar` needs the symbol to bind `value`" in e for e in self.build(d)[1]["errors"]))
        d = sample()
        d["symbols"][2]["bar"] = {"min": 0, "max": 1}      # a bar on a pump
        self.assertTrue(any("`bar` is a key of a readout" in e for e in self.build(d)[1]["errors"]))

    def test_the_bar_does_not_overlap_its_readout_under_gate_g5(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.write_child(sample(), "stock", Path(tmp))
            g5 = gates.g5_layout(out)
            self.assertTrue(g5["ok"], g5)
            self.assertEqual(g5["warnings"], [])

    @staticmethod
    def write_child(desc, render, tmp):
        child, reports = screen.build_child("cadre_hmi_parts", [desc], "Parts", render=render, faceplate="asm")
        return child.write(tmp)


class TrendTests(GeneratorCase):
    def view(self, path):
        return json.loads(self.prj.files[f"com.inductiveautomation.perspective/views/{path}/view.json"])

    def test_the_variants_by_pens_and_units(self):
        n = self.nodes(self.build()[0])
        self.assertEqual(n["Trend_tr1"]["props"]["path"], "Parts/Trend2Axes")      # rpm and V differ
        self.assertEqual(n["Trend_tr2"]["props"]["path"], "Parts/Trend")
        d = sample()
        d["trends"][0]["pens"][1]["unit"] = "rpm"
        self.assertEqual(self.nodes(self.build(d)[0])["Trend_tr1"]["props"]["path"], "Parts/Trend2")
        p = n["Trend_tr1"]["props"]["params"]
        self.assertEqual((p["title"], p["minutes"], p["tag1"], p["unit1"], p["tag2"], p["label2"]),
                         ("Engine speed and voltage", 10, "[default]cadre_hmi_parts/gen/speed", "rpm",
                          "[default]cadre_hmi_parts/gen/voltage", "Voltage"))

    def test_the_chart_is_the_librarys_with_tag_history(self):
        doc = self.view("Parts/Trend2Axes")
        chart = self.nodes(doc)["Chart"]
        self.assertEqual(chart["type"], "ia.chart.timeseries")
        plot = chart["props"]["plots"][0]
        self.assertEqual([a["name"] for a in plot["axes"]], ["value", "second"])
        self.assertEqual([t["axis"] for t in plot["trends"]], ["value", "second"])
        for k, alias in (("props.series[0].data", "pen1"), ("props.series[1].data", "pen2")):
            b = chart["propConfig"][k]["binding"]
            self.assertEqual(b["type"], "tag-history")
            self.assertEqual(b["config"]["tags"], "{view.custom.%s}" % alias)
            self.assertEqual(b["config"]["dateRange"], {"mostRecent": "{view.params.minutes}", "mostRecentUnits": "MIN"})
            self.assertIsInstance(doc["custom"][alias], list)                   # gate G7 history wants a list
        one = self.nodes(self.view("Parts/Trend2"))["Chart"]["props"]["plots"][0]
        self.assertEqual([a["name"] for a in one["axes"]], ["value"])
        self.assertEqual([t["axis"] for t in one["trends"]], ["value", "value"])
        single = self.view("Parts/Trend")
        self.assertEqual(len(self.nodes(single)["Chart"]["props"]["series"]), 1)
        self.assertNotIn("tag2", single["params"])

    def test_pens_come_from_the_params_as_lists_of_paths(self):
        cfg = self.view("Parts/Trend")["propConfig"]["custom.pen1"]["binding"]
        self.assertEqual(cfg["config"]["expression"], "{view.params.tag1}")
        self.assertIn("'alias': 'p1'", cfg["transforms"][0]["code"])

    def test_the_note_for_a_pen_the_tag_model_does_not_historise(self):
        d = sample()
        d["tagRoot"] = "[default]plant"
        model = {"name": "plant", "tagType": "Folder", "tags": [
            {"name": "gen", "tagType": "Folder", "tags": [
                {"name": "speed", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Float8",
                 "historyEnabled": True, "historyProvider": "Hist"},
                {"name": "voltage", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Float8"},
                {"name": "current", "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Float8"}]}]}
        child, reports = screen.build_child("cadre_hmi_parts", [d], "Parts", tag_model=model)
        notes = reports["/page-parts"]["notes"]
        self.assertEqual(len([x for x in notes if "does not historise" in x]), 2, notes)
        self.assertTrue(any("gen/voltage" in x for x in notes))
        self.assertFalse(any("gen/speed" in x for x in notes))
        child, reports = screen.build_child("cadre_hmi_parts", [d], "Parts")   # no tag model: nothing to say
        self.assertEqual(reports["/page-parts"]["notes"], [])

    def test_history_needs_are_stated(self):
        needs = parts.history_needs()
        self.assertTrue(needs["historyEnabled"])
        self.assertIn("historyProvider", needs)


class LineTests(GeneratorCase):
    def test_a_static_dashed_line(self):
        n = self.nodes(self.build()[0])["Line_interlock"]
        el = n["props"]["elements"][0]
        self.assertEqual(el["stroke"]["dasharray"], "6 4")
        self.assertEqual(el["d"], "M724 520L884 520")
        self.assertNotIn("propConfig", n)

    def test_a_line_gated_by_a_symbol_is_solid_while_energised(self):
        n = self.nodes(self.build()[0])["Line_bus1"]
        cfg = n["propConfig"]
        live = "{view.custom.g_SW1}"
        self.assertEqual(self.expr(n, "props.elements[0].stroke.paint"),
                         f"if({live}, 'var(--element-neutral-color)', 'var(--element-inactive-color)')")
        self.assertEqual(self.expr(n, "props.elements[0].stroke.dasharray"), f"if({live}, '', '6 4')")
        self.assertEqual(n["props"]["elements"][0]["stroke"]["width"], 3)

    def test_a_line_gated_by_a_tag_reads_it_once(self):
        doc = self.build()[0]
        n = self.nodes(doc)["Line_bus2"]
        self.assertIn("{view.custom.ln_bus2_0}", self.expr(n, "props.elements[0].stroke.dasharray"))
        self.assertEqual(doc["propConfig"]["custom.ln_bus2_0"]["binding"]["config"]["tagPath"],
                         "[default]cadre_hmi_parts/sw2/closed")
        self.assertIn("ln_bus2_0", doc["custom"])

    def test_several_gates_need_all_of_them(self):
        d = sample()
        d["lines"][1]["gate"] = [{"symbol": "SW1"}, {"tag": "sw2/closed"}]
        n = self.nodes(self.build(d)[0])["Line_bus1"]
        self.assertIn("{view.custom.g_SW1} && {view.custom.ln_bus1_1}", self.expr(n, "props.elements[0].stroke.paint"))

    def test_a_gate_on_a_symbol_the_page_lacks_or_without_a_state(self):
        d = sample()
        d["lines"][1]["gate"] = {"symbol": "NOPE"}
        self.assertTrue(any("the page lacks" in e for e in self.build(d)[1]["errors"]))
        d["lines"][1]["gate"] = {"symbol": "RD1"}         # a readout has no state
        self.assertTrue(any("no state to gate on" in e for e in self.build(d)[1]["errors"]))

    def test_lines_lie_with_the_pipes_under_the_symbols(self):
        names = list(self.nodes(self.build()[0]))
        self.assertLess(names.index("Line_bus1"), names.index("RD1"))
        self.assertGreater(names.index("Bar_RD1"), names.index("FL2"))


class MarkTests(GeneratorCase):
    def test_the_symbol_views_carry_the_marks(self):
        for kind in ("Pump", "Motor", "Fan", "Valve", "Switch", "Indicator"):
            c = self.contracts[f"Automation/{kind}"]
            self.assertIs(c["params"]["badgeDuty"], False, kind)
            self.assertIs(c["params"]["outOfService"], False, kind)
            doc = json.loads(self.prj.files[f"com.inductiveautomation.perspective/views/Automation/{kind}/view.json"])
            n = self.nodes(doc)
            self.assertEqual(self.expr(n["Badge_duty"], "meta.visible"), "{view.params.badgeDuty}")
            self.assertEqual((n["Badge_duty"]["position"]["x"], n["Badge_duty"]["position"]["y"]), (16, 32))   # between the other badges
            self.assertEqual(self.expr(n["OosVeil"], "meta.visible"), "{view.params.outOfService}")
            self.assertEqual(n["OosWord"]["props"]["text"], "OOS")
            self.assertEqual(n["OosVeil"]["props"]["elements"][0]["fill"]["opacity"], 0.72)
            kids = [c["meta"]["name"] for c in n["Symbol"]["children"]]
            self.assertLess(kids.index("OosVeil"), kids.index("Badge_duty"))       # the badges stay readable over the veil
            self.assertEqual(kind == "Indicator", "AlertFrame" not in n)   # the frame is over the whole box (L5)
        # the duty badge is OpenBridge's own icon
        doc = json.loads(self.prj.files["com.inductiveautomation.perspective/views/Automation/Pump/view.json"])
        duty = library.icon("duty")["elements"]
        self.assertEqual(self.nodes(doc)["Badge_duty"]["props"]["elements"], duty)

    def test_marks_are_params_bound_to_a_tag_or_stated(self):
        n = self.nodes(self.build()[0])
        p1 = n["P1"]
        self.assertEqual(p1["propConfig"]["props.params.badgeDuty"]["binding"]["config"]["tagPath"], "[default]cadre_hmi_parts/P1/duty")
        self.assertEqual(p1["propConfig"]["props.params.outOfService"]["binding"]["config"]["tagPath"], "[default]cadre_hmi_parts/P1/oos")
        self.assertNotIn("badgeDuty", p1["props"]["params"])                           # a bound parameter is left to its binding (GF-61)
        self.assertIs(n["P2"]["props"]["params"]["outOfService"], True)
        self.assertIs(n["P2"]["props"]["params"]["badgeDuty"], False)

    def test_an_unknown_mark_is_refused_by_the_contract(self):
        d = sample()
        d["symbols"][2]["params"]["badgeStandby"] = True
        self.assertTrue(any("badgeStandby" in e for e in self.build(d)[1]["errors"]))

    def test_the_module_draws_a_marked_symbol_since_0_4_0(self):
        n = self.nodes(self.build(render="module")[0])
        self.assertEqual(n["P1"]["type"], "cadre.ob.pump")         # bound duty and out of service (module 0.4.0)
        self.assertEqual(n["P2"]["type"], "cadre.ob.pump")         # a stated out of service
        d = sample()
        for s in d["symbols"]:
            if s["id"] in ("P1", "P2"):
                s["params"].pop("outOfService", None)
                s["bind"] = {"on": s["bind"]["on"]}
        self.assertEqual(self.nodes(self.build(d, render="module")[0])["P1"]["type"], "cadre.ob.pump")   # without the marks
        self.assertTrue(screen.module_draws("pump", {}, target="module"))
        self.assertTrue(screen.module_draws("pump", {"badgeDuty": False, "outOfService": False}, target="module"))   # the contract's defaults
        self.assertTrue(screen.module_draws("pump", {"badgeDuty": None}, target="module"))                        # a bound mark
        self.assertTrue(screen.module_draws("pump", {"outOfService": True}, target="module"))

    def test_a_symbol_without_marks_is_drawn_as_before(self):
        d = sample()
        n = self.nodes(self.build(d)[0])
        self.assertNotIn("props.params.badgeDuty", n["SW1"]["propConfig"])
        self.assertIs(n["SW1"]["props"]["params"]["badgeDuty"], False)


class FaultRowTests(GeneratorCase):
    def test_the_lamp_follows_the_alarms_on_its_tag(self):
        doc, info = self.build()
        self.assertEqual(info["errors"], [])
        n = self.nodes(doc)
        fl = n["FL1"]
        # a lamp draws no alert frame (L5): nothing binds its alert parameters, and its tag's alarms reach the lists
        self.assertNotIn("props.params.alert", fl["propConfig"])
        self.assertNotIn("props.params.alertFrameStatus", fl["propConfig"])
        code = doc["propConfig"]["custom.alerts"]["binding"]["transforms"][0]["code"]
        self.assertNotIn("a_FL1", code)
        self.assertIn("cadre.hmi.alert_states(self.session", code)            # the one machinery, one query
        self.assertEqual(set(doc["custom"]["alerts"]), {"a_P1", "a_P2"})

    def test_the_text_and_status_are_the_rows_own(self):
        fl = self.nodes(self.build()[0])["FL1"]
        self.assertNotIn("props.params.hasTag", fl["propConfig"])              # the toolbar's ID tag does not hide a fault text
        self.assertNotIn("props.params.showStatus", fl["propConfig"])
        self.assertIs(fl["props"]["params"]["hasTag"], True)
        self.assertIs(fl["props"]["params"]["showStatus"], False)
        pump = self.nodes(self.build()[0])["P1"]
        self.assertIn("props.params.hasTag", pump["propConfig"])                # any other symbol keeps the toolbar's buttons

    def test_a_condition_that_holds_is_bold_only_on_a_lamp(self):
        lamp = json.loads(self.prj.files["com.inductiveautomation.perspective/views/Automation/Indicator/view.json"])
        self.assertEqual(self.expr(self.nodes(lamp)["Tag"], "props.style.fontWeight"), "if({view.params.on}, 'bold', 'normal')")
        pump = json.loads(self.prj.files["com.inductiveautomation.perspective/views/Automation/Pump/view.json"])
        self.assertNotIn("props.style.fontWeight", self.nodes(pump)["Tag"].get("propConfig", {}))

    def test_alarm_belongs_to_an_indicator(self):
        d = sample()
        d["symbols"][4]["alarm"] = "x"           # a switch
        self.assertTrue(any("`alarm` is a key of an indicator" in e for e in self.build(d)[1]["errors"]))

    def test_a_device_symbol_keeps_its_device_source(self):
        doc = self.build()[0]
        self.assertIn("'a_P1': '[default]cadre_hmi_parts/P1'", doc["propConfig"]["custom.alerts"]["binding"]["transforms"][0]["code"])


class FitTests(GeneratorCase):
    @staticmethod
    def scale_of(doc):
        return doc["propConfig"]["custom.scale"]["binding"]["config"]["expression"]

    def test_a_fitted_page_scales_from_its_corner_and_does_not_scroll(self):
        doc = self.build()[0]
        n = self.nodes(doc)
        e = self.scale_of(doc)                               # s = fit * zoom, one view property (L4)
        self.assertTrue(e.startswith("(if(coalesce({view.custom.canvasW}, 0) > 0"), e)   # the measured canvas first
        self.assertIn("(coalesce({page.props.dimensions.viewport.width}, 1580) - 0 - %s) / 1580.0" % DOCKED_TERM, e)
        self.assertIn("(coalesce({page.props.dimensions.viewport.height}, 740) - 104) / 740.0", e)   # top dock 48 + toolbar 56
        self.assertTrue(e.endswith("* min(4, max(0.5, coalesce({view.custom.zoom}, 1.0)))"), e)
        self.assertEqual(self.expr(n["Diagram"], "props.style.transform"), "'scale(' + toStr(round({view.custom.scale}, 4)) + ')'")
        self.assertEqual(n["Diagram"]["props"]["style"]["transformOrigin"], "top left")
        self.assertEqual(n["Canvas"]["props"]["style"]["overflow"], "hidden")         # at the fit, a fraction of a pixel draws no bar
        self.assertEqual(self.expr(n["Canvas"], "props.style.overflow"), "if({view.custom.zoom} > 1.0, 'auto', 'hidden')")
        self.assertEqual(n["Diagram"]["props"]["style"]["width"], "1580px")           # the page keeps its own box
        self.assertEqual(doc["custom"]["zoom"], 1)

    def test_the_canvas_holds_a_sizer_of_the_scaled_size_that_holds_the_diagram(self):
        doc = self.build()[0]
        n = self.nodes(doc)
        root = doc["root"]["children"]
        self.assertEqual([k["meta"]["name"] for k in root], ["Canvas", "UserToolbar"])
        canvas = root[0]
        self.assertEqual(canvas["meta"]["domId"], "cadre-canvas")
        self.assertEqual([k["meta"]["name"] for k in canvas["children"]], ["Sizer"])   # no module: no zoom component
        self.assertEqual([k["meta"]["name"] for k in n["Sizer"]["children"]], ["Diagram"])
        for key, size in (("props.style.width", 1580), ("props.style.height", 740), ("position.basis", 740)):
            self.assertEqual(self.expr(n["Sizer"], key),
                             "toStr(round(%d * {view.custom.scale}, 1)) + 'px'" % size, key)
        self.assertEqual(n["Sizer"]["position"], {"basis": "740px", "grow": 0, "shrink": 0})   # unzoomed: the diagram's own box

    def test_the_scale_runs_as_fit_times_zoom(self):
        e = self.scale_of(self.build()[0])
        py = (expr_py(e).replace("coalesce({page.props.dimensions.viewport.width}, 1580)", "VW")
              .replace("coalesce({page.props.dimensions.viewport.height}, 740)", "VH")
              .replace(DOCKED_TERM, "0").replace("coalesce({view.custom.zoom}, 1.0)", "ZM"))
        k = lambda vw, vh, zm: eval(py.replace("VW", str(vw)).replace("VH", str(vh)).replace("ZM", str(zm))
                                    .replace("CW", "0").replace("CH", "0"), EXPR_NS)
        self.assertEqual(k(1920, 1080, 1), 1.0)                      # a bigger window: never above 1 at zoom 1
        self.assertAlmostEqual(k(1280, 800, 1), 1280 / 1580)
        self.assertAlmostEqual(k(1280, 800, 2), 2 * 1280 / 1580)     # zoom multiplies the fit
        self.assertEqual(k(1920, 1080, 2), 2.0)
        self.assertEqual(k(1920, 1080, 9), 4.0)                      # held to the range, 0.5 to 4
        self.assertEqual(k(1920, 1080, 0.1), 0.5)

    def test_what_the_frame_takes_is_stated_or_defaulted(self):
        d = sample()
        d["toolbar"] = False
        self.assertIn("- 48) / 740.0", self.scale_of(self.build(d)[0]))
        d["screen"]["fit"] = {"reserveX": 400, "reserveY": 60}
        e = self.scale_of(self.build(d)[0])
        self.assertIn("- 400 - %s) / 1580.0" % DOCKED_TERM, e)
        self.assertIn("- 60) / 740.0", e)

    def test_the_scale_is_the_smaller_ratio_and_never_above_one(self):
        e = parts.fit_expression(1600, 900, {"reserveX": 0, "reserveY": 104})
        py = expr_py(e).replace("coalesce({page.props.dimensions.viewport.width}, 1600)", "VW").replace(
            "coalesce({page.props.dimensions.viewport.height}, 900)", "VH").replace(DOCKED_TERM, "DK")
        k = lambda vw, vh, dk=0, cw=0, ch=0: eval(py.replace("VW", str(vw)).replace("VH", str(vh)).replace("DK", str(dk))
                                                  .replace("CW", str(cw)).replace("CH", str(ch)), EXPR_NS)
        self.assertAlmostEqual(k(1920, 1080, 400, 1520, 864), 1520 / 1600)   # measured: no flag, the canvas it has
        self.assertAlmostEqual(k(1920, 1080, 400, 1920, 864), 864 / 900)     # a reload left the flag true: ignored
        self.assertEqual(k(1920, 1080), 1.0)                       # a bigger window does not enlarge the page
        self.assertAlmostEqual(k(1280, 800), min(1280 / 1600, (800 - 104) / 900))
        self.assertAlmostEqual(k(1600, 900), (900 - 104) / 900)    # 1600 by 900: the height decides, and it no longer scrolls
        self.assertAlmostEqual(k(800, 2000), 0.5)                  # the width decides
        self.assertAlmostEqual(k(1600, 900, 400), 1200 / 1600)     # the open faceplate dock takes 400 px (GP-10)

    def test_every_script_that_moves_the_faceplate_dock_keeps_its_flag(self):
        # GP-10 on the gateway (2026-10-24): the viewport keeps its width while the dock pushes the page, so the
        # library's own openers and closers of the faceplate dock say whether it is open
        self.assertEqual(DOCKED_TERM, "if(%s, %d, 0)" % (parts.FIT_DOCKED, parts.FIT_FACEPLATE_DOCK))
        dock = [d for d in framework.shared_docks("T")["right"] if d["id"] == "faceplate"][0]
        self.assertEqual(dock["size"], parts.FIT_FACEPLATE_DOCK)
        self.assertEqual(par.session_defaults()["custom"]["faceplateDocked"], False)
        scripts_text = []

        def collect(o):
            if isinstance(o, dict):
                if isinstance(o.get("script"), str):
                    scripts_text.append(o["script"])
                for v in o.values():
                    collect(v)
            elif isinstance(o, list):
                for v in o:
                    collect(v)
        collect({**framework.framework_views(), **navigation.views()})
        moves = 0
        for script in scripts_text:
            ls = [x.strip() for x in script.split("\n")]
            for i, x in enumerate(ls):
                if "openDock(id='faceplate')" in x:
                    moves += 1
                    self.assertEqual(ls[i + 1], "self.session.custom.faceplateDocked = True", script)
                if "closeDock('faceplate')" in x:
                    moves += 1
                    self.assertEqual(ls[i + 1], "self.session.custom.faceplateDocked = False", script)
        self.assertGreaterEqual(moves, 4)   # the opener, the Float pin, the close button, the popup's Dock pin

    def test_a_page_without_fit_scales_by_the_zoom_alone(self):
        d = sample()
        d["screen"].pop("fit")
        doc = self.build(d)[0]
        n = self.nodes(doc)
        self.assertEqual(self.scale_of(doc), "(1.0) * min(4, max(0.5, coalesce({view.custom.zoom}, 1.0)))")
        self.assertEqual(n["Canvas"]["props"]["style"]["overflow"], "auto")           # a page larger than the window scrolls
        self.assertNotIn("propConfig", n["Canvas"])
        self.assertEqual(n["Diagram"]["props"]["style"]["transformOrigin"], "top left")

    def test_parts_and_fit_are_for_a_diagram(self):
        d = {"schema": "cadre-hmi-screen/1", "screen": {"id": "C", "route": "/c", "title": "C", "view": "Screens/C",
                                                        "layout": "cards", "fit": True},
             "tagRoot": "[default]t", "buttons": [{"id": "b", "x": 0, "y": 0, "w": 10, "h": 10, "label": "x",
                                                   "action": {"type": "route", "route": "/x"}}], "rows": []}
        errors = self.build(d)[1]["errors"]
        self.assertTrue(any("for a diagram layout" in e for e in errors), errors)


def evaluate(expr, env):
    """A nested `if(...)` expression of string literals over `{view.custom.<key>}` Booleans, evaluated."""
    expr = expr.strip()
    if expr.startswith("if(") and expr.endswith(")"):
        cond, yes, no = gates._top_level(expr[3:-1], ",")
        key = re.fullmatch(r"\{view\.custom\.(\w+)\}", cond).group(1)
        return evaluate(yes if env[key] else no, env)
    return expr[1:-1]


class ExtraPartTests(GeneratorCase):
    """The area chevron (GP-07), the bracket (GP-09), the word that follows a state (GP-12) and the liquid of a
    well with level switches (GM-01)."""

    def test_a_link_is_an_icon_that_navigates(self):
        n = self.nodes(self.build()[0])["Link_toGen"]
        self.assertEqual(n["type"], "ia.shapes.svg")
        self.assertEqual(n["props"]["elements"][0]["fill"]["paint"], "var(--element-neutral-color)")
        self.assertEqual(n["props"]["elements"][0]["d"], library.icon("chevron-right-google")["elements"][0]["d"])
        self.assertEqual(n["props"]["style"]["cursor"], "pointer")
        self.assertEqual((n["position"]["width"], n["position"]["height"]), (24, 24))
        self.assertIn("system.perspective.navigate('/alerts')", n["events"]["dom"]["onClick"]["config"]["script"])
        self.assertNotIn("select_device", json.dumps(n))                  # P8: a link never opens a faceplate
        d = sample()
        d["links"][0]["icon"] = "no-such-icon"
        self.assertTrue(any("no library icon" in e for e in self.build(d)[1]["errors"]))

    def test_a_bracket_has_ticks_towards_its_group_and_its_name_beyond(self):
        n = self.nodes(self.build()[0])
        line, name = n["Bracket_grp"], n["BracketName_grp"]
        self.assertEqual(line["props"]["elements"][0]["d"], "M0 0V6H208V0")             # the ticks rise to the group above
        self.assertEqual(name["props"]["text"], "Pump group")
        self.assertGreaterEqual(name["position"]["y"], line["position"]["y"] + line["position"]["height"])
        d = sample()
        d["brackets"][0]["side"] = "above"
        n = self.nodes(self.build(d)[0])
        self.assertEqual(n["Bracket_grp"]["props"]["elements"][0]["d"], "M0 8V2H208V8")
        self.assertLessEqual(n["BracketName_grp"]["position"]["y"] + n["BracketName_grp"]["position"]["height"],
                             n["Bracket_grp"]["position"]["y"])

    def test_a_word_is_bold_and_active_while_its_state_holds(self):
        doc = self.build()[0]
        n = self.nodes(doc)
        ups, gen = n["Text_ups"], n["Text_gen"]
        self.assertEqual(self.expr(ups, "props.style.fontWeight"), "if({view.custom.em_ups}, 'bold', 'normal')")
        self.assertEqual(self.expr(ups, "props.style.classes"),
                         "if({view.custom.em_ups}, 'cadre/font/label cadre/text/active', 'cadre/font/label cadre/text/neutral')")
        self.assertEqual(doc["propConfig"]["custom.em_ups"]["binding"]["config"]["tagPath"], "[default]cadre_hmi_parts/ups/battery")
        self.assertIn("{view.custom.g_SW1}", self.expr(gen, "props.style.fontWeight"))   # a symbol's state is read once
        self.assertEqual(ups["props"]["style"]["classes"], "cadre/font/label cadre/text/neutral")   # off: the label's own style
        d = sample()
        d["labels"][0]["emphasis"] = {"symbol": "RD1"}
        self.assertTrue(any("no state to emphasise on" in e for e in self.build(d)[1]["errors"]))
        d["labels"][0]["emphasis"] = {"symbol": "NOPE"}
        self.assertTrue(any("which the page lacks" in e for e in self.build(d)[1]["errors"]))

    def test_a_two_state_word_reads_by_its_state(self):
        d = sample()
        d["labels"][0]["emphasis"]["words"] = ["Mains power in use", "Battery power in use"]
        doc, info = self.build(d)
        self.assertEqual(info["errors"], [])
        self.assertEqual(self.expr(self.nodes(doc)["Text_ups"], "props.text"),
                         "if({view.custom.em_ups}, 'Battery power in use', 'Mains power in use')")
        for bad in ({"tag": "a", "words": ["one"]}, {"words": ["a", "b"]}):   # two words, and a tag or a symbol
            d = sample()
            d["labels"][0]["emphasis"] = bad
            self.assertTrue(screen.schema_errors([d], ["d"]), bad)

    def test_a_label_without_emphasis_is_the_plain_label_as_before(self):
        d = sample()
        d["labels"][0].pop("emphasis")
        n = self.nodes(self.build(d)[0])
        self.assertNotIn("propConfig", n["Text_ups"])

    def test_the_liquid_rises_to_the_highest_mark_reached(self):
        n = self.nodes(self.build()[0])["Well_well"]
        fill, band = (self.expr(n, f"props.elements[{i}].d") for i in (0, 1))
        keys = ["well_well_0", "well_well_1", "well_well_2"]      # the marks at 50, 70 and 90 per cent of 220 px

        def state(duty, standby, high):
            env = dict(zip(keys, (duty, standby, high)))
            return evaluate(fill, env), evaluate(band, env)
        self.assertEqual(state(False, False, False), ("", "M0 110H200V220H0Z"))              # none: the band from the floor to the first mark
        self.assertEqual(state(True, False, False), ("M0 110H200V220H0Z", "M0 66H200V110H0Z"))   # duty: filled to 50, lighter to 70
        self.assertEqual(state(True, True, False), ("M0 66H200V220H0Z", "M0 22H200V66H0Z"))
        self.assertEqual(state(True, True, True), ("M0 22H200V220H0Z", ""))                   # the top mark: no band beyond
        self.assertEqual(state(False, True, False)[0], "M0 66H200V220H0Z")                    # a mark that is lit decides, whatever is below
        self.assertEqual(n["props"]["elements"][0]["fill"]["opacity"], 0.5)
        self.assertGreater(n["props"]["elements"][0]["fill"]["opacity"], n["props"]["elements"][1]["fill"]["opacity"])
        self.assertNotIn("numberFormat", fill + band)
        doc = self.build()[0]
        self.assertEqual(doc["propConfig"]["custom.well_well_1"]["binding"]["config"]["tagPath"], "[default]cadre_hmi_parts/well/standby")

    def test_well_marks_must_rise(self):
        d = sample()
        d["wells"][0]["marks"] = [{"level": 0.7, "tag": "a"}, {"level": 0.5, "tag": "b"}]
        self.assertTrue(any("from the lowest level up" in e for e in self.build(d)[1]["errors"]))
        d["wells"][0]["marks"] = [{"level": 0.5, "tag": "a"}, {"level": 0.5, "tag": "b"}]
        self.assertTrue(any("from the lowest level up" in e for e in self.build(d)[1]["errors"]))

    def test_an_emphasised_label_belongs_to_a_diagram(self):
        d = {"schema": "cadre-hmi-screen/1", "screen": {"id": "C", "route": "/c", "title": "C", "view": "Screens/C",
                                                        "layout": "cards"}, "tagRoot": "[default]t", "rows": [],
             "labels": [{"id": "l", "x": 0, "y": 0, "w": 9, "h": 9, "text": "x", "emphasis": {"tag": "a"}}]}
        self.assertTrue(any("for a diagram layout" in e for e in self.build(d)[1]["errors"]))


class WholeBuildTests(GeneratorCase):
    """The sample passes every offline gate under both renderings."""

    def run_gates(self, render):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            base = par.build_parent()[0].write(tmp)
            child, reports = screen.build_child("cadre_hmi_parts", [sample()], "Parts", render=render, faceplate="asm")
            self.assertEqual(reports["/page-parts"]["errors"], [])
            out = child.write(tmp)
            rep = tmp / "report.json"
            rep.write_text(json.dumps(reports, default=list), encoding="utf-8")
            return gates.run(out, base, rep), reports["/page-parts"]

    def test_stock(self):
        res, rep = self.run_gates("stock")
        self.assertTrue(res["ok"], {k: v for k, v in res.items() if isinstance(v, dict) and not v.get("ok", True)})
        for g in ("G1_registry", "G2_references", "G3_view_keys", "G4_project", "G5_layout", "G6_flow", "G7_contract",
                  "G7_faceplates", "G7_history", "G7_commands"):
            self.assertTrue(res[g]["ok"], g)
        self.assertEqual(res["G5_layout"]["warnings"], [])
        self.assertEqual(rep["gaps"], [])

    def test_module(self):
        res, rep = self.run_gates("module")
        self.assertTrue(res["ok"], {k: v for k, v in res.items() if isinstance(v, dict) and not v.get("ok", True)})
        self.assertEqual(res["G5_layout"]["warnings"], [])

    def test_the_command_gate_refuses_a_button_whose_enabled_ignores_the_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            base = par.build_parent()[0].write(tmp)
            child, _ = screen.build_child("cadre_hmi_parts", [sample()], "Parts", faceplate="asm")
            out = child.write(tmp)
            vf = out / "com.inductiveautomation.perspective/views/Screens/PageParts/view.json"
            text = vf.read_text(encoding="utf-8")
            self.assertTrue(gates.g7_commands(out, base)["ok"])
            vf.write_text(text.replace("{view.custom.can.W18}", "true"), encoding="utf-8")
            probs = gates.g7_commands(out, base)["problems"]
            self.assertTrue(any("does not follow the permissions (write path W18)" in p for p in probs), probs)
            # a direct write in a button's script is refused too
            vf.write_text(text.replace("cadre.hmi.page_pulse(self.session, ", "system.tag.writeBlocking([").replace(
                "sim/reset')", "sim/reset'], [True])"), encoding="utf-8")
            probs = gates.g7_commands(out, base)["problems"]
            self.assertTrue(any("direct system.tag.write" in p for p in probs), probs)

    def test_the_test_tag_document_has_the_tags_the_parts_name(self):
        tags = screen.tags_document([sample()])
        found = {}

        def walk(node, path):
            for t in node.get("tags", []):
                if t["tagType"] == "Folder":
                    walk(t, path + [t["name"]])
                else:
                    found["/".join(path + [t["name"]])] = (t["dataType"], t["value"])
        walk({"tags": [tags]}, [])
        base = "cadre_hmi_parts/"
        self.assertEqual(found[base + "sim/reset"], ("Boolean", False))      # the pulse tag
        self.assertEqual(found[base + "gen/load"], ("Float8", 62.0))          # a bar
        self.assertEqual(found[base + "gen/speed"], ("Float8", 1500.0))       # a pen
        self.assertEqual(found[base + "sw2/closed"], ("Boolean", False))      # a line's gate
        self.assertEqual(found[base + "gen/fault01"][0], "Boolean")           # a fault row

    def test_a_page_without_parts_builds_as_before(self):
        d = json.loads((ROOT / "screens" / "sample-pump-station.json").read_text(encoding="utf-8"))
        doc, info = screen.build_screen(d, self.contracts)
        self.assertEqual(info["errors"], [])
        n = self.nodes(doc)
        self.assertFalse(any(k.startswith(("Bar_", "Trend_", "Button_", "Line_")) for k in n))
        self.assertNotIn("custom.can", doc["propConfig"])

    def test_the_profile_states_the_parts(self):
        prof = library_profile.build(self.contracts)
        self.assertEqual(prof["parts"]["arrays"], ["buttons", "bars", "trends", "lines", "links", "brackets", "wells", "alarmPanels"])
        self.assertEqual(prof["parts"]["pulsePath"], "W18")
        self.assertIn("Parts/RangeBar", self.contracts)
        for v in parts.TREND_VIEWS.values():
            self.assertIn(v, self.contracts)


if __name__ == "__main__":
    unittest.main()
