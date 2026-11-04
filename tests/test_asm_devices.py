"""Tests of COB-158: the generator kind, its symbols and faceplate, the asm faceplates of the sequence and the
instrument, and the opener that names a tab (the shared contract of COB-158 to COB-160).

Run from the repository root:  python -m unittest discover -s tests
The sample is `tests/fixtures/asm-screen.json` with its device model `asm-devices.json` (synthetic names).
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "compare"))

from hmi import devices_asm, framework, gates, library, library_profile, scripts, screen  # noqa: E402
from hmi import parent as par  # noqa: E402
from test_hmi import hmi_ns, session, view_nodes  # noqa: E402  (helpers only: no test class is imported)

FIXTURES = ROOT / "tests" / "fixtures"
ROOT_TAG = "[default]cadre_hmi_asmtest"
GEN = f"{ROOT_TAG}/GEN1"
VIEW = "com.inductiveautomation.perspective/views/"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def faceplates():
    return framework.framework_views()


def walk(node):
    yield node
    for c in node.get("children") or []:
        yield from walk(c)


def texts(doc):
    """Every static text of a view: labels, buttons, section titles."""
    return [n["props"]["text"] for n in walk(doc["root"]) if isinstance(n.get("props", {}).get("text"), str)]


def button(doc, name):
    return next(n for n in walk(doc["root"]) if n["meta"]["name"] == name)


def script_of(node):
    return node["events"]["component"]["onActionPerformed"]["config"]["script"]


def tab_keys(doc):
    tabs = next(n for n in walk(doc["root"]) if n["meta"]["name"] == "Tabs")
    return [c["meta"]["name"][4:] for c in tabs["children"]]


def panes(doc):
    return {n["meta"]["name"][5:] for n in walk(doc["root"]) if n["meta"]["name"].startswith("Pane_")}


class ProfileTests(unittest.TestCase):
    """The generator kind in the tables a kind touches."""

    @classmethod
    def setUpClass(cls):
        cls.contracts = screen.load_contracts()
        cls.prof = library_profile.build(cls.contracts)

    def test_the_kind_is_in_every_table(self):
        self.assertEqual(screen.KIND_VIEW["generator"], "Automation/Generator")
        self.assertEqual(framework.FACEPLATE_VIEW["generator"], "Faceplate/ASM/Generator")
        self.assertEqual(framework.ASM_VIEW["generator"], "Faceplate/ASM/Generator")
        self.assertEqual(framework.faceplate_view("generator", "openbridge"), "Faceplate/ASM/Generator")
        self.assertEqual(framework.faceplate_view("generator", "asm"), "Faceplate/ASM/Generator")
        self.assertIn("Faceplate/ASM/Generator", gates.FACEPLATES)
        self.assertIn("'generator', 'Faceplate/ASM/Generator'", framework.FACEPLATE_OF_KIND)
        self.assertEqual(screen.TREND_KINDS["generator"], "engineSpeed")
        self.assertEqual(screen.TREND_ALSO["generator"], {"fuelLevel": "fuel level"})
        self.assertIn("generator", screen.FACEPLATE_MEMBERS)

    def test_the_members(self):
        known = screen.known_members("generator")
        self.assertEqual({m: t for m, t in known.items() if m in devices_asm.GENERATOR_CORE},
                         {"state": "Boolean", "runText": "String", "switchText": "String", "faultCode": "Int4",
                          "cmdStart": "Boolean", "cmdStop": "Boolean", "cmdReset": "Boolean"})
        for m in ("fault", "engineSpeed", "voltageLL", "fuelLevel", "fuelLowLimit", "startDelay", "stopDelay",
                  "runHours", "startsToday", "startsYesterday", "serviceHours", "cmdServiceDone", "mnt/errorMask",
                  "alarmAck"):
            self.assertIn(m, known, m)
        self.assertEqual(screen.pulse_members("generator"), ["cmdStart", "cmdStop", "cmdReset", "cmdServiceDone"])
        self.assertEqual(screen.pulse_members("sequence"),
                         ["trigger", "cmdInService", "cmdOutOfService", "cmdEnable", "cmdDisable"])
        self.assertEqual(screen.pulse_members("instrument"), [])
        # every pulse member is a W18 member and has a default and a caption
        w18 = scripts.constant("FUNCTION_MEMBERS")["W18"]
        defaults = scripts.constant("MEMBER_DEFAULTS")
        for m in devices_asm.GENERATOR_PULSES + devices_asm.SEQUENCE_PULSES:
            self.assertIn(m, w18)
            self.assertIs(defaults[m], False)
            self.assertIn(m, devices_asm.CAPTIONS)
        # every member the kinds know has a typed default for `device_read`
        for kind in ("generator", "sequence", "instrument"):
            for m, t in screen.known_members(kind).items():
                if "/" not in m and m != scripts.constant("ACK_MEMBER") and not m.endswith(("Limit", "Delay")) \
                        and m not in ("volume", "capacity", "trend"):
                    self.assertIn(m, defaults, (kind, m))

    def test_the_profile(self):
        dk = self.prof["deviceKinds"]["generator"]
        self.assertEqual(dk["faceplates"], {"openbridge": "Faceplate/ASM/Generator", "asm": "Faceplate/ASM/Generator"})
        self.assertEqual((dk["interlocks"], dk["config"], dk["maintenance"]), (False, True, True))
        self.assertEqual(dk["pulses"], ["cmdStart", "cmdStop", "cmdReset", "cmdServiceDone"])
        self.assertEqual(dk["trend"], ["engineSpeed", "fuelLevel"])
        self.assertEqual(dk["bind"], {"on": "state", "open": "state"})
        kind = self.prof["kinds"]["generator"]
        self.assertEqual((kind["view"], kind["flow"], kind["gate"], kind["anchor"], kind["faceplate"]),
                         ("Automation/Generator", "pass", None, "symbol-centre", "Faceplate/ASM/Generator"))
        self.assertEqual(kind["pulses"], dk["pulses"])
        for k in ("sequence", "instrument", "readout", "instrument-field", "generator"):
            self.assertTrue(self.prof["deviceKinds"][k]["config"], k)
        self.assertTrue(self.prof["deviceKinds"]["sequence"]["interlocks"])
        self.assertFalse(self.prof["deviceKinds"]["instrument"]["interlocks"])
        self.assertEqual(self.prof["deviceKinds"]["sequence"]["faceplates"],
                         {"openbridge": "Faceplate/Sequence", "asm": "Faceplate/ASM/Sequence"})
        self.assertEqual(self.prof["deviceKinds"]["instrument"]["faceplates"]["asm"], "Faceplate/ASM/Instrument")
        for view in ("Generator", "Sequence", "Instrument"):
            self.assertEqual(self.prof["faceplates"][f"Faceplate/ASM/{view}"],
                             {"tabs": [k for k, _ in framework.ASM_TABS], "style": "asm"})
        self.assertEqual(json.loads((ROOT / "library/profile.json").read_text(encoding="utf-8")), self.prof)   # current

    def test_the_tabs_a_device_shows(self):
        gen = ["state", "runText"]
        self.assertEqual(framework.expected_tabs("generator", gen), ["Home", "Diagnostics", "Alarms", "Info"])
        self.assertEqual(framework.expected_tabs("generator", gen + ["serviceHours"]),
                         ["Home", "Config", "Diagnostics", "Alarms", "Info"])
        self.assertEqual(framework.expected_tabs("generator", gen + ["cmdServiceDone"], style="asm")[1], "Config")
        self.assertEqual(framework.expected_tabs("generator", gen + ["mnt/errorMask"])[1], "Config")
        self.assertEqual(framework.expected_tabs("sequence", ["step"], style="asm"),
                         ["Home", "Diagnostics", "Alarms", "Info"])
        self.assertEqual(framework.expected_tabs("sequence", ["step", "cfg/runTimeSP", "ilk/permitted"], style="asm"),
                         ["Home", "Config", "Diagnostics", "Alarms", "Interlock", "Info"])
        self.assertEqual(framework.expected_tabs("sequence", ["step"], style="openbridge"), ["Status", "Alarms"])
        self.assertEqual(framework.expected_tabs("instrument", ["value"], style="asm"),
                         ["Home", "Diagnostics", "Alarms", "Info"])
        self.assertEqual(framework.expected_tabs("readout", ["value", "mnt/simulated"], style="asm")[1], "Config")
        self.assertEqual(framework.expected_tabs("instrument", ["value"]), ["Values", "Trend", "Alarms"])


class SymbolTests(unittest.TestCase):
    """The generator symbol and the generator set (gap GG-01)."""

    @classmethod
    def setUpClass(cls):
        cls.views = library.library_views()

    def test_the_icon_is_the_pins_and_the_symbol_is_drawn(self):
        icon = json.loads((ROOT / "library/icons/generator.json").read_text(encoding="utf-8"))
        self.assertEqual((icon["name"], icon["source"]["licence"], icon["source"]["commit"][:8]),
                         ("generator", "Apache-2.0", "2c98dda1"))
        self.assertIn("generator", json.loads((ROOT / "library/icons/index.json").read_text(encoding="utf-8"))["icons"])
        self.assertIn("generator", (ROOT / "library/icons/ICONS.txt").read_text(encoding="utf-8").split())
        for name, inverted in (("generator-on", ""), ("generator-off", "-inverted")):
            els = library.icon(name)["elements"]
            self.assertEqual(len(els), 3)
            self.assertEqual(els[1]["fill"]["paint"], f"var(--automation-device-primary{inverted}-color)")
            self.assertEqual(els[2]["fill"]["paint"], "none")                    # the G is a stroked arc
            self.assertEqual(els[2]["stroke"]["paint"], f"var(--automation-device-tertiary{inverted}-color)")
        self.assertEqual(library.DEVICE_KINDS["Generator"][:4], ("on", "generator-on", "generator-off", None))

    def test_the_symbol_is_an_automation_symbol_with_the_alarm_frame_and_the_click(self):
        doc, contract = self.views["Automation/Generator"]
        self.assertEqual((contract["kind"], contract["flow"], contract["gate"], contract["anchor"], contract["state"]),
                         ("generator", "pass", None, "symbol-centre", "on"))
        self.assertEqual((contract["params"]["picture"], contract["params"]["deviceKind"]), ("symbol", "generator"))
        nodes = view_nodes(doc)
        self.assertIn("AlertFrame", nodes)
        self.assertIn("AlertPulse", nodes)
        self.assertEqual({n for n in nodes if n.startswith("Flap_")},
                         {"Flap_alarm", "Flap_warning", "Flap_caution", "Flap_critical"})
        self.assertIn("IconOn", nodes)
        self.assertIn("select_device", doc["root"]["events"]["dom"]["onClick"]["config"]["script"])
        self.assertIn("openDock", doc["root"]["events"]["dom"]["onClick"]["config"]["script"])
        # a plain click names no tab
        self.assertNotIn("selectedTab", doc["root"]["events"]["dom"]["onClick"]["config"]["script"])

    def test_the_alarm_frame_of_the_other_symbols_is_the_same_frame(self):
        pump = view_nodes(self.views["Automation/Pump"][0])
        gen = view_nodes(self.views["Automation/Generator"][0])
        for n in (pump, gen):   # around the symbol and its readout, as the module's frame is (L5, glass)
            self.assertEqual(n["AlertFrame"]["props"]["style"]["position"], "absolute")
            self.assertEqual(n["Flap_alarm"]["props"]["style"]["right"], "-22px")

    def test_the_generator_set(self):
        doc, contract = self.views["Automation/GeneratorSet"]
        self.assertEqual((contract["anchor"], contract["flow"], contract["kind"], contract["state"]),
                         ("box", "pass", "generator", "on"))
        self.assertEqual(doc["props"]["defaultSize"], {"width": 240, "height": 150})
        nodes = view_nodes(doc)
        picture = nodes["Picture"]
        names = [e["name"] for e in picture["props"]["elements"]]
        for part in ("Skid", "Engine", "Head1", "Exhaust", "Coupling", "Alternator", "Terminals", "Louvre1"):
            self.assertIn(part, names)
        # running or stopped: every part follows `on` in its fill, and the bodies in their outline as well
        cfg = picture["propConfig"]
        for i, e in enumerate(picture["props"]["elements"]):
            self.assertIn(f"props.elements[{i}].fill.paint", cfg)
            self.assertEqual(f"props.elements[{i}].stroke.paint" in cfg, "stroke" in e, e["name"])
            self.assertIn("{view.params.on}", cfg[f"props.elements[{i}].fill.paint"]["binding"]["config"]["expression"])
        # it fits the box it is given (L4 item 11): a percent container, the picture centred at its own proportions
        self.assertEqual(doc["root"]["props"]["mode"], "percent")
        self.assertEqual(picture["position"], {"x": 0, "y": 0, "width": 1, "height": 0.8})
        self.assertEqual(picture["props"]["preserveAspectRatio"], "xMidYMid")
        self.assertEqual(picture["props"]["viewBox"], "0 0 240 120")
        for name in ("Tag", "Status"):
            self.assertLessEqual(nodes[name]["position"]["y"] + nodes[name]["position"]["height"], 1.0, name)
            self.assertEqual((nodes[name]["position"]["x"], nodes[name]["position"]["width"]), (0, 1), name)
        for n in walk(doc["root"]):   # every child is in fractions of the box, none in pixels
            if "x" in n.get("position", {}) and n is not doc["root"]:   # (the flaps are flex items of the frame)
                self.assertTrue(all(0 <= v <= 1 for v in n["position"].values()), n["meta"]["name"])
        self.assertEqual(nodes["AlertFrame"]["position"], {"x": 0, "y": 0, "width": 1, "height": 1})
        self.assertEqual(nodes["AlertPulse"]["position"], {"x": 0, "y": 0, "width": 1, "height": 1})
        self.assertEqual(nodes["Flap_alarm"]["props"]["viewBox"], "0 0 20 20")
        click = doc["root"]["events"]["dom"]["onClick"]["config"]["script"]
        self.assertIn("select_device(self.session, self.view.params.deviceId, self.view.params.deviceKind or 'generator'",
                      click)
        self.assertIn("Running", nodes["Status"]["propConfig"]["props.text"]["binding"]["config"]["expression"])

    def test_the_view_of_a_symbol(self):
        self.assertEqual(screen.view_of({"kind": "generator"}), "Automation/Generator")
        self.assertEqual(screen.view_of({"kind": "Generator", "params": {"picture": "symbol"}}), "Automation/Generator")
        self.assertEqual(screen.view_of({"kind": "generator", "params": {"picture": "genset"}}), "Automation/GeneratorSet")
        self.assertEqual(screen.view_of({"kind": "pump", "params": {"picture": "genset"}}), "Automation/Pump")
        self.assertEqual(screen.view_of({"kind": "nothing"}), "")


class WalkTests(unittest.TestCase):
    """The operator's walk reads the generator as it reads the other symbols (the glass table of `walk_plan`)."""

    def test_the_glass_table_knows_the_generator(self):
        import walk_plan as walk
        self.assertIn("generator", walk.AUTOMATION)
        self.assertEqual(walk.FIRST_TAB["Faceplate/ASM/Generator"], "Home")
        self.assertIn("Faceplate/ASM/Generator", walk.PULSE_VIEWS)
        self.assertNotIn("Faceplate/ASM/Generator", walk.STEP_VIEWS)
        rule, why = walk.reading_rule("generator", {"hasTag": True, "tag": "G-1"}, "on", "stock")
        self.assertEqual((rule["how"], rule["on"], rule["off"]), ("state", {"line": "On"}, {"line": "Off"}))
        rule, why = walk.reading_rule("generator", {"picture": "genset", "hasTag": True}, "on", "stock")
        self.assertEqual((rule["on"], rule["off"]), ({"line": "Running"}, {"line": "Stopped"}))
        self.assertEqual(walk.reading_rule("generator", {"picture": "genset"}, "alert", "module")[0], {"how": "frame"})
        self.assertIsNone(walk.reading_rule("generator", {"picture": "genset"}, "speed", "stock")[0])
        self.assertEqual(walk.find_text("generator", {"tag": "G-1", "hasTag": True}), "G-1")

    def test_the_plan_names_the_buttons_of_the_asm_faceplates(self):
        import walk_plan as walk
        desc, model = load("asm-screen.json"), load("asm-devices.json")
        plan = walk.build_plan([desc], devices=model, tags=None, faceplate="asm")
        pulses = [s for s in plan["steps"] if s.get("type") == "pulse"]
        by_device = {}
        for s in pulses:
            by_device.setdefault(s["device"], []).append((s["member"], s["button"], s["tab"]))
        gen = dict((m, (b, t)) for m, b, t in by_device["GEN-1"])
        self.assertEqual(gen["cmdStart"], ("Start generator", "Home"))
        # the service data are on Config (the gateway run of 2026-10-24: Home carries Start, Stop and Reset only)
        self.assertEqual(gen["cmdServiceDone"], ("Service done", "Config"))


class FaceplateTests(unittest.TestCase):
    """The three asm faceplates as views."""

    @classmethod
    def setUpClass(cls):
        cls.v = faceplates()

    def test_the_generator(self):
        doc = self.v["Faceplate/ASM/Generator"]
        self.assertEqual(tab_keys(doc), ["home", "config", "diagnostics", "alarms", "interlocks", "info"])
        self.assertEqual(panes(doc), {"home", "config", "diagnostics", "alarms", "interlocks", "info"})
        t = texts(doc)
        for caption in ("Start", "Stop", "Reset", "STATUS", "COMMANDS", "FUEL", "TOTALS", "TIMING", "Run sequence",
                        "Control switch", "Active fault", "Start delay", "Stop delay", "Fuel level", "Low limit",
                        "Run hours", "Starts today", "Starts yesterday", "Hours since service", "Service completed",
                        "Engine speed", "L-L voltage", "Genset time left"):
            self.assertIn(caption, " | ".join(t) + " | ".join(
                n["props"].get("text", "") for n in walk(doc["root"]) if n["type"] == "ia.input.button"), caption)
        # Start, Stop and Reset are pulses that ask first (W18, the Confirm row), and nothing writes at the click
        nodes = view_nodes(doc)
        for name, member in (("Pulse_cmdStart", "cmdStart"), ("Pulse_cmdStop", "cmdStop"), ("Pulse_cmdReset", "cmdReset"),
                             ("Pulse_cmdServiceDone", "cmdServiceDone")):
            script = script_of(nodes[name])
            self.assertIn(f"'path': 'W18', 'member': '{member}', 'value': True", script, name)
            self.assertNotIn("cadre.hmi", script, name)
            enabled = nodes[name]["propConfig"]["props.enabled"]["binding"]["config"]["expression"]
            self.assertIn("{view.custom.can.W18}", enabled)
            self.assertIn(f"{{view.custom.dev.write.{member}}}", enabled)
            self.assertIn("{view.custom.dev.allowed.W18}", enabled)          # the owner gates it like every pulse
            shown = nodes[name]["propConfig"]["position.display"]["binding"]["config"]["expression"]
            self.assertEqual(shown, f"{{view.custom.dev.writable.{member}}}")
        self.assertIn("W18", nodes["Confirm"]["children"][1]["propConfig"]["props.enabled"]["binding"]["config"]["expression"])
        self.assertIn("cadre.hmi.command(", nodes["ConfirmYes"]["events"]["component"]["onActionPerformed"]["config"]["script"])
        # Start reads selected while running, Stop while stopped
        self.assertIn("{view.custom.dev.value.state}",
                      nodes["Pulse_cmdStart"]["propConfig"]["props.style.classes"]["binding"]["config"]["expression"])
        # the caption is the device model's, else the library's
        cap = nodes["Pulse_cmdStart"]["propConfig"]["props.text"]["binding"]["config"]["expression"]
        self.assertEqual(cap, "if({view.custom.dev.pulses.cmdStart} = 'cmdStart', 'Start', {view.custom.dev.pulses.cmdStart})")

    def test_the_generator_reads_its_members_and_polls_them(self):
        doc = self.v["Faceplate/ASM/Generator"]
        script = doc["propConfig"]["custom.dev"]["binding"]["transforms"][0]["code"]
        for m in devices_asm.GENERATOR_READS:
            self.assertIn(f"'{m}'", script, m)
        self.assertEqual(set(doc["custom"]["dev"]["has"]), {m.replace("/", "_") for m in devices_asm.GENERATOR_READS})
        self.assertEqual(set(doc["custom"]["dev"]["pulses"]), set(devices_asm.GENERATOR_PULSES))
        # a trend of speed and fuel on the Home tab: two series, the fuel on the percent axis, drawn where historised
        chart = next(n for n in walk(doc["root"]) if n["type"] == "ia.chart.timeseries")
        self.assertEqual([t["series"] for t in chart["props"]["plots"][0]["trends"]], ["value", "fuelLevel"])
        self.assertEqual([t["axis"] for t in chart["props"]["plots"][0]["trends"]], ["value", "out"])
        self.assertEqual([c["key"] for t in chart["props"]["plots"][0]["trends"] for c in t["columns"]],
                         ["engineSpeed", "fuelLevel"])
        self.assertEqual(doc["custom"]["historyTags"], [{"path": "", "alias": "engineSpeed"}])
        self.assertEqual(doc["custom"]["historyFuel"], [{"path": "", "alias": "fuelLevel"}])
        self.assertIn("trended(self.session, value, ['engineSpeed', 'fuelLevel'])",
                      doc["propConfig"]["custom.trend"]["binding"]["transforms"][0]["code"])
        self.assertIn("trend_tags(self.session, value, 'fuelLevel')",
                      doc["propConfig"]["custom.historyFuel"]["binding"]["transforms"][0]["code"])
        # the Home tab scrolls: its rows and the trend are more than the faceplate's height holds
        home = next(n for n in walk(doc["root"]) if n["meta"]["name"] == "Pane_home")
        self.assertEqual(home["props"]["style"]["overflow"], "auto")

    def test_the_place_of_the_range_bars(self):
        doc = self.v["Faceplate/ASM/Generator"]
        home = [c["meta"]["name"] for c in next(n for n in walk(doc["root"]) if n["meta"]["name"] == "Pane_home")["children"]]
        self.assertLess(home.index("FuelLowRow"), home.index("FuelBar"))      # the fuel bar beneath the fuel rows
        self.assertLess(home.index("FuelBar"), home.index("TotalsTitle"))
        bar = next(n for n in walk(doc["root"]) if n["meta"]["name"] == "FuelBar")
        self.assertEqual(bar["props"]["path"], "Parts/RangeBar")             # COB-159, merged
        self.assertIn("fuelLowLimit", bar["propConfig"]["props.params.loLimit"]["binding"]["config"]["expression"])
        inst = self.v["Faceplate/ASM/Instrument"]
        vbar = next(n for n in walk(inst["root"]) if n["meta"]["name"] == "ValueBar")
        self.assertIn("rangeHi", vbar["propConfig"]["props.params.max"]["binding"]["config"]["expression"])

    def test_the_generators_config_holds_the_service_rows(self):
        doc = self.v["Faceplate/ASM/Generator"]
        config = next(n for n in walk(doc["root"]) if n["meta"]["name"] == "Pane_config")
        names = [c["meta"]["name"] for c in config["children"]]
        self.assertEqual(names[:4], ["ServiceTitle", "ServiceHoursRow", "ServiceCommands", "ConfigTitle"])
        self.assertIn("ConfigRows", names)                                 # the W19 rows of the library
        tabs = {c["meta"]["name"]: c for c in next(n for n in walk(doc["root"]) if n["meta"]["name"] == "Tabs")["children"]}
        shown = tabs["Tab_config"]["propConfig"]["position.display"]["binding"]["config"]["expression"]
        self.assertEqual(shown, "{view.custom.dev.mnt} || {view.custom.dev.config} > 0 || {view.custom.dev.has.serviceHours} "
                                "|| {view.custom.dev.has.cmdServiceDone}")
        self.assertEqual(tabs["Tab_interlocks"]["propConfig"]["position.display"]["binding"]["config"]["expression"],
                         "{view.custom.ilk.present}")

    def test_the_header_strips(self):
        for view, words in (("Generator", ["HeadState", "HeadRun", "HeadSwitch", "HeadFault", "HeadAlarms"]),
                            ("Sequence", ["HeadStep", "HeadOos", "HeadDisabled", "HeadFault", "HeadInterlock", "HeadAlarms"]),
                            ("Instrument", ["HeadRemote", "HeadOos", "HeadBad", "HeadIo", "HeadRange", "HeadAlarms"])):
            doc = self.v[f"Faceplate/ASM/{view}"]
            header = next(n for n in walk(doc["root"]) if n["meta"]["name"] == "Header")
            self.assertEqual([c["meta"]["name"] for c in header["children"]], words, view)
            for c in header["children"]:      # each word only while it holds
                self.assertIn("position.display", c["propConfig"], (view, c["meta"]["name"]))

    def test_the_sequence(self):
        doc = self.v["Faceplate/ASM/Sequence"]
        self.assertEqual(tab_keys(doc), ["home", "config", "diagnostics", "alarms", "interlocks", "info"])
        nodes = view_nodes(doc)
        for name, member in (("Pulse_cmdInService", "cmdInService"), ("Pulse_cmdOutOfService", "cmdOutOfService"),
                             ("Pulse_cmdEnable", "cmdEnable"), ("Pulse_cmdDisable", "cmdDisable"),
                             ("Pulse_trigger", "trigger")):
            self.assertIn(f"'path': 'W18', 'member': '{member}', 'value': True", script_of(nodes[name]), name)
        for row in ("InServiceRow", "EnabledRow", "PrerequisitesRow", "NormalRow", "StepRow", "FaultRow"):
            self.assertIn(row, nodes)
        # the prerequisite comes from the interlock contract (`custom.ilk`), the Interlock tab lists its conditions
        self.assertIn("{view.custom.ilk.permitted}",
                      nodes["PrerequisitesValue"]["propConfig"]["props.text"]["binding"]["config"]["expression"])
        self.assertEqual(nodes["PrerequisitesRow"]["propConfig"]["position.display"]["binding"]["config"]["expression"],
                         "{view.custom.ilk.present}")
        self.assertIn("Conditions", nodes)
        self.assertEqual(nodes["Conditions"]["props"]["path"], "Faceplate/InterlockRow")
        # the Config tab carries the W19 rows (the run time setpoint, gap GM-07)
        config = nodes["ConfigRows"]
        self.assertIn("config_rows(self.session", config["propConfig"]["props.instances"]["binding"]["transforms"][0]["code"])
        # the state of the device against the commands: In service reads selected while in service
        self.assertIn("{view.custom.dev.value.inService}",
                      nodes["Pulse_cmdInService"]["propConfig"]["props.style.classes"]["binding"]["config"]["expression"])
        self.assertTrue(set(doc["custom"]["dev"]["pulses"]) >= set(devices_asm.SEQUENCE_PULSES))

    def test_the_instrument(self):
        doc = self.v["Faceplate/ASM/Instrument"]
        self.assertEqual(tab_keys(doc), ["home", "config", "diagnostics", "alarms", "interlocks", "info"])
        nodes = view_nodes(doc)
        for name in ("Value", "RemoteAuto" + "Row", "Limits", "Delays", "Trend", "Chart"):
            self.assertIn(name, nodes, name)
        for name in ("DiagValueTitle", "DiagFlagsTitle", "DiagFlags0Row", "DiagFlags4Row"):
            self.assertIn(name, nodes, name)
        flags = [nodes[f"DiagFlags{i}Row"]["children"][0]["props"]["text"] for i in range(5)]
        self.assertEqual(flags, ["oos", "badValue", "ioFault", "overRange", "underRange"])
        self.assertEqual(nodes["Chart"]["propConfig"]["props.series[0].data"]["binding"]["type"], "tag-history")
        self.assertEqual(doc["custom"]["historyTags"], [{"path": "", "alias": "value"}])
        self.assertEqual(doc["custom"]["limitRows"], [])
        self.assertIn("delayRows", doc["custom"])
        for view in ("Generator", "Sequence", "Instrument"):                # a command always asks first
            for n in walk(self.v[f"Faceplate/ASM/{view}"]["root"]):
                if n["type"] == "ia.input.button" and n["meta"]["name"].startswith("Pulse_"):
                    self.assertNotIn("cadre.hmi.pulse", script_of(n))
        self.assertFalse([n for n in walk(doc["root"]) if n["meta"]["name"].startswith("Pulse_")])   # an instrument has none


class TabTests(unittest.TestCase):
    """Opening on a named tab (contract 2.1 of COB-158 to COB-160)."""

    def test_every_faceplate_view_takes_a_tab(self):
        views = faceplates()
        tabbed = ["Faceplate/" + v for v in ("Pump", "Valve", "Tank", "Instrument", "Controller", "Input", "Sequence")] \
            + sorted(framework.ASM_BUILT) + ["Faceplate/ASM/Pump", "Faceplate/ASM/Valve", "Faceplate/Empty"]
        for path in tabbed:
            doc = views[path]
            self.assertEqual(doc["params"]["tab"], "", path)
            self.assertEqual(doc["propConfig"]["params.tab"]["paramDirection"], "input", path)
        for path in tabbed[:-1]:
            keys = tab_keys(views[path])
            first = keys[0]
            reset = views[path]["propConfig"]["params.deviceId"]["onChange"]["script"]
            self.assertIn(f"self.custom.tab = '{first}'", reset, path)              # G7 reads this line
            self.assertIn("want = self.params.tab", reset, path)
            self.assertIn(f"if want in {tuple(keys)!r}:", reset, path)
            own = views[path]["propConfig"]["params.tab"]["onChange"]["script"]
            self.assertIn("want = currentValue.value", own, path)
            self.assertTrue(own.splitlines()[0].strip().endswith(f"'{first}'"), path)   # else the first

    def test_the_dock_binds_the_tab(self):
        body = next(n for n in walk(faceplates()["Framework/SideMenu"]["root"]) if n["meta"]["name"] == "Faceplate")
        self.assertEqual(body["props"]["params"], {"deviceId": "", "tab": ""})
        self.assertEqual(body["propConfig"]["props.params.tab"]["binding"]["config"]["expression"],
                         "coalesce({session.custom.selectedTab}, '')")
        popup = next(n for n in walk(faceplates()["Framework/FaceplatePopup"]["root"]) if n["meta"]["name"] == "Faceplate")
        self.assertIn("props.params.tab", popup["propConfig"])

    def test_the_opener_passes_the_tab_through_select_device(self):
        lines = library.open_device("'[default]p/D1'", "d['kind']", "'D-1'", "'Pump 1'", "'alarms'", indent="\t")
        self.assertEqual(lines[0], "\tcadre.hmi.select_device(self.session, '[default]p/D1', d['kind'], 'D-1', 'Pump 1', 'alarms')")
        self.assertEqual(lines[1:], library.open_faceplate("\t"))
        self.assertNotIn("selectedTab", "\n".join(lines))
        plain = library.open_device("x", "k")
        self.assertEqual(plain[0], "cadre.hmi.select_device(self.session, x, k, '', '', '')")

    def test_select_device_writes_the_tab_last(self):
        device = f"{ROOT_TAG}/P1"
        tags = {f"{device}/state": True, f"{device}/mnt/errorMask": False, f"{device}/ilk/permitted": True}
        ns, _calls = hmi_ns(tags)
        s = session(["Administrator"], devices=[{"folder": device, "kind": "pump", "title": "P-1", "label": "", "unit": ""}])
        s.custom.selectedTab = "stale"
        ns["select_device"](s, device, "pump", "P-1", "Pump 1")                  # a plain click clears the tab
        self.assertEqual((s.custom.selectedDevice, s.custom.selectedKind, s.custom.selectedTab), (device, "pump", ""))
        ns["select_device"](s, device, "pump", "P-1", "Pump 1", "alarms")        # a tab every faceplate shows
        self.assertEqual(s.custom.selectedTab, "alarms")
        ns["select_device"](s, device, "pump", "P-1", "Pump 1", "interlocks")    # the device has interlocks
        self.assertEqual(s.custom.selectedTab, "interlocks")
        ns["select_device"](s, device, "pump", "P-1", "Pump 1", "config")        # and a maintenance row
        self.assertEqual(s.custom.selectedTab, "config")

    def test_a_tab_the_device_does_not_show_opens_the_first(self):
        device = f"{ROOT_TAG}/G1"
        tags = {f"{device}/state": True}
        ns, _calls = hmi_ns(tags)
        s = session(["Administrator"], devices=[{"folder": device, "kind": "generator", "title": "G-1", "label": "", "unit": ""}])
        for tab in ("interlocks", "config", "maintenance"):
            ns["select_device"](s, device, "generator", "G-1", "", tab)
            self.assertEqual(s.custom.selectedTab, "", tab)
        tags[f"{device}/serviceHours"] = 12.0                                   # service data shows Config
        ns["select_device"](s, device, "generator", "G-1", "", "config")
        self.assertEqual(s.custom.selectedTab, "config")
        ns["select_device"](s, device, "generator", "G-1", "", "maintenance")   # the stock tab takes no service data
        self.assertEqual(s.custom.selectedTab, "")
        self.assertTrue(ns["tab_shown"](s, device, "home"))
        self.assertTrue(ns["tab_shown"](s, device, "no-such-tab"))              # the view refuses it
        tags[f"{device}/ilk/permitted"] = True
        self.assertTrue(ns["tab_shown"](s, device, "interlocks"))
        self.assertEqual(ns["CONFIG_SERVICE"], ["serviceHours", "cmdServiceDone"])

    def test_a_device_with_configuration_rows_alone_shows_config(self):
        # the first gateway run (2026-10-24): a sequence whose only Config content is a W19 row opened Home, because
        # the member read returns before it counts the rows when no maintenance member exists
        device = f"{ROOT_TAG}/SEQ1"
        ns, _calls = hmi_ns({f"{device}/step": 1, f"{device}/cfg/runTimeSP": 30.0})
        entry = {"folder": device, "kind": "sequence", "title": "SEQ-1", "label": "", "unit": "",
                 "config": [{"member": "cfg/runTimeSP", "caption": "Run time", "unit": "min", "minimum": 0,
                             "maximum": 1440, "format": "0"}]}
        s = session(["Administrator"], devices=[entry])
        ns["select_device"](s, device, "sequence", "SEQ-1", "", "config")
        self.assertEqual(s.custom.selectedTab, "config")
        s = session(["Administrator"], devices=[dict(entry, config=[])])   # no rows, no maintenance: the first tab
        ns["select_device"](s, device, "sequence", "SEQ-1", "", "config")
        self.assertEqual(s.custom.selectedTab, "")
        self.assertEqual(tuple(ns["CONFIG_SERVICE"]), framework.ASM_CONFIG_EXTRA["generator"])


class PulseTests(unittest.TestCase):
    """The generator's commands through the library's pulse path (W18), checked like the others."""

    def setUp(self):
        self.device = f"{ROOT_TAG}/GEN1"
        self.model = {"folder": self.device, "kind": "generator", "title": "GEN-1", "label": "",
                      "write": list(devices_asm.GENERATOR_PULSES), "pulses": []}
        self.tags = {f"{self.device}/{m}": False for m in devices_asm.GENERATOR_PULSES}
        self.tags[f"{self.device}/state"] = False

    def test_start_stop_reset_and_service_pulse_true_for_an_administrator(self):
        ns, calls = hmi_ns(self.tags)
        s = session(["Administrator"], devices=[self.model], model=True)
        for m in devices_asm.GENERATOR_PULSES:
            self.assertEqual(ns["command"](s, "W18", self.device, m, True), "", m)
            self.assertIs(self.tags[f"{self.device}/{m}"], True, m)
        self.assertEqual([c for c in calls if c[0] == "write"][0], ("write", [f"{self.device}/cmdStart"], [True]))

    def test_nothing_else_is_written(self):
        ns, _calls = hmi_ns(self.tags)
        s = session(["Administrator"], devices=[self.model], model=True)
        self.assertIn("only writes true", ns["command"](s, "W18", self.device, "cmdStart", False))
        self.assertIn("not a pulse command", ns["command"](s, "W18", self.device, "state", True))
        self.assertIn("is not a pulse command", ns["command"](s, "W18", self.device, "engineSpeed", True))
        self.assertIs(self.tags[f"{self.device}/cmdStart"], False)

    def test_a_session_without_the_role_and_a_device_without_the_member_are_refused(self):
        ns, _calls = hmi_ns(self.tags)
        s = session(["Operator"], devices=[self.model], model=True)
        self.assertEqual(ns["command"](s, "W18", self.device, "cmdStart", True), ns["REFUSED"])
        admin = session(["Administrator"], devices=[self.model], model=True)
        del self.tags[f"{self.device}/cmdReset"]
        self.assertIn("has no cmdReset", ns["command"](admin, "W18", self.device, "cmdReset", True))
        ro = dict(self.model, write=["cmdStart"])
        self.assertIn("read only", ns["command"](session(["Administrator"], devices=[ro], model=True),
                                                 "W18", self.device, "cmdStop", True))

    def test_the_owner_gates_the_pulses_of_a_device_with_modes(self):
        ns, _calls = hmi_ns(self.tags)
        self.tags[f"{self.device}/mode"] = 0
        model = dict(self.model, write=self.model["write"] + ["mode"],
                     modes=[{"value": 0, "name": "Remote auto", "owner": "program"},
                            {"value": 1, "name": "Remote manual", "owner": "operator"}])
        s = session(["Administrator"], devices=[model], model=True)
        self.assertIn("Refused", ns["command"](s, "W18", self.device, "cmdStart", True))   # the program holds it
        self.tags[f"{self.device}/mode"] = 1
        self.assertEqual(ns["command"](s, "W18", self.device, "cmdStart", True), "")


class SampleTests(unittest.TestCase):
    """A project built with a generator, a sequence and an instrument in the asm style, through gates G0 to G7."""

    @classmethod
    def setUpClass(cls):
        cls.desc, cls.model = load("asm-screen.json"), load("asm-devices.json")

    def build(self, render="stock", faceplate="asm", **extra):
        tags = screen.tags_document([self.desc], self.model)
        with tempfile.TemporaryDirectory() as d:
            prj, _ = par.build_parent()
            base = prj.write(Path(d))
            child, reports = screen.build_child("cadre_hmi_asmtest", [self.desc], "Asm", "*cadre_hmi_asmtest*", render,
                                                tag_model=tags, devices=self.model, faceplate=faceplate, **extra)
            out = child.write(Path(d))
            rep = Path(d) / "report.json"
            rep.write_text(json.dumps(reports, default=list), encoding="utf-8")
            res = gates.run(out, base, rep, tag_model=tags, devices=self.model,
                            symbols=screen.device_symbols([self.desc]),
                            profile=library_profile.build(screen.load_contracts()))
        return child, reports, res

    def test_the_sample_passes_every_offline_gate_under_both_renderings(self):
        self.assertEqual(screen.devices_schema_errors(self.model, "m") + screen.schema_errors([self.desc], ["d"]), [])
        for render in ("stock", "module"):
            child, reports, res = self.build(render)
            self.assertEqual(reports["/asm"]["errors"] + reports["/asm"]["gaps"], [], render)
            self.assertTrue(res["ok"], {k: v for k, v in res.items() if isinstance(v, dict) and not v.get("ok")})
            self.assertEqual(res["G7_devices"]["devices"], 4)
            self.assertEqual(res["G7_devices"]["symbols"], 4)
            self.assertEqual(res["G7_devices"]["problems"], [])
            self.assertEqual(res["G7_interlocks"]["devices"], ["cadre_hmi_asmtest/SQ1"])
            self.assertEqual(res["G7_interlocks"]["problems"], [])
            for fp in ("Faceplate/ASM/Generator", "Faceplate/ASM/Sequence", "Faceplate/ASM/Instrument"):
                self.assertEqual(res["G7_faceplates"]["tabs"][fp], [k for k, _ in framework.ASM_TABS], fp)

    def test_the_symbols_and_their_fallback(self):
        for render in ("stock", "module"):
            child, _reports, _res = self.build(render)
            nodes = view_nodes(json.loads(child.files[VIEW + "Screens/AsmSample/view.json"]))
            # the plain generator is the module's component under the module rendering (spike T0 wrap W2) and the stock
            # view otherwise; the generator set keeps its own view under either rendering
            if render == "module":
                self.assertEqual(nodes["GEN1"]["type"], "cadre.ob.generator")
            else:
                self.assertEqual(nodes["GEN1"]["props"]["path"], "Automation/Generator", render)
            self.assertEqual(nodes["GEN2"]["props"]["path"], "Automation/GeneratorSet", render)
            self.assertEqual(nodes["GEN2"]["position"], {"x": 400, "y": 100, "width": 240, "height": 150})
            self.assertEqual(nodes["GEN1"]["position"]["width"] >= 48, True)
            self.assertEqual(nodes["SQ1"]["props"]["path"], "Instrument/Sequence")
            self.assertEqual(nodes["GEN2"]["props"]["params"]["picture"], "genset")
            # a device symbol follows its device's alarms (F016): the frame is bound to the page's alert states
            if render == "module":
                self.assertIn("props.alert", nodes["GEN1"]["propConfig"])
                self.assertEqual(nodes["GEN1"]["custom"]["deviceKind"], "generator")
            else:
                self.assertEqual(nodes["GEN1"]["props"]["params"]["picture"], "symbol")
                self.assertIn("props.params.alert", nodes["GEN1"]["propConfig"])
                self.assertEqual(nodes["GEN1"]["props"]["params"]["deviceKind"], "generator")
            self.assertIn("props.params.alert", nodes["GEN2"]["propConfig"])
            self.assertEqual(nodes["GEN2"]["props"]["params"]["deviceKind"], "generator")
            self.assertIn("props.params.on", nodes["GEN2"]["propConfig"])

    def test_the_generated_tags_and_the_trend_index(self):
        tags = screen.tags_document([self.desc], self.model)
        leaves = gates._tag_leaves(tags)
        gen = {k.split("/GEN1/", 1)[1]: v for k, v in leaves.items() if "/GEN1/" in k and not k.endswith("/")}
        self.assertEqual(gen["cmdStart"]["dataType"], "Boolean")
        self.assertEqual(gen["faultCode"]["dataType"], "Int4")
        self.assertEqual(gen["fuelLevel"]["value"], 62.0)
        self.assertEqual(gen["runText"]["value"], "Ready")
        self.assertEqual(sorted(k for k in gen), sorted(self.model["devices"][0]["members"]))
        index = {e["folder"].split("/")[-1]: e for e in screen.device_index([self.desc], self.model)}
        self.assertEqual((index["GEN1"]["kind"], index["GEN2"]["kind"]), ("generator", "generator"))
        self.assertEqual(sorted(index["GEN1"]["pulses"], key=lambda p: p["member"]),
                         [{"member": m, "caption": c} for m, c in (
                             ("cmdReset", "Reset generator"), ("cmdServiceDone", "Service done"),
                             ("cmdStart", "Start generator"), ("cmdStop", "Stop generator"))])
        trends = [(t["deviceId"].split("/")[-1], t["member"], t["unit"]) for t in screen.trend_index([self.desc], tags, self.model)
                  if t["deviceId"].endswith("GEN1")]
        self.assertEqual(trends, [("GEN1", "engineSpeed", ""), ("GEN1", "fuelLevel", "%")])

    def test_the_gates_refuse_a_wrong_generator(self):
        profile = library_profile.build(screen.load_contracts())
        symbols = screen.device_symbols([self.desc])

        def problems(change):
            model = copy.deepcopy(self.model)
            change(model["devices"][0]["members"], model["devices"][0])
            return gates.g7_devices(model, profile, symbols)["problems"]
        self.assertEqual(problems(lambda m, d: None), [])
        self.assertTrue(any("not a member the library knows" in p for p in problems(lambda m, d: m.update(rpm=dict(type="Float8", access="read")))))
        self.assertTrue(any("marked writable without" in p for p in problems(lambda m, d: m["cmdStart"].pop("pulse"))))
        self.assertTrue(any("is marked a pulse" in p for p in problems(lambda m, d: m["engineSpeed"].update(pulse=True, type="Boolean", access="write"))))
        self.assertTrue(any("is Boolean" in p or "library reads it as" in p for p in problems(lambda m, d: m["runText"].update(type="Boolean"))))
        self.assertTrue(any("ilk" in p or "not a member" in p for p in problems(lambda m, d: m.update({"ilk/permitted": dict(type="Boolean", access="read")}))))
        self.assertTrue(any("label of a faceplate tab" in p for p in problems(lambda m, d: m["cmdStart"].update(caption="Home"))))
        # a symbol of the generator set that binds a member the device lacks
        model = copy.deepcopy(self.model)
        del model["devices"][1]["members"]["state"]
        self.assertTrue(any("no member 'state'" in p for p in gates.g7_devices(model, profile, symbols)["problems"]))

    def test_the_faceplates_of_the_sample_are_the_asm_ones(self):
        child, _reports, _res = self.build("stock")
        sp = json.loads(child.files["com.inductiveautomation.perspective/session-props/props.json"])
        self.assertEqual(sp["custom"]["faceplateStyle"], "asm")
        index = {e["folder"].split("/")[-1]: e for e in sp["custom"]["devices"]}
        self.assertEqual(index["SQ1"]["faceplate"], "asm")
        self.assertEqual(framework.faceplate_view("sequence", index["SQ1"]["faceplate"]), "Faceplate/ASM/Sequence")
        self.assertEqual(framework.faceplate_view("instrument", "asm"), "Faceplate/ASM/Instrument")
        self.assertEqual(framework.faceplate_view("readout", "asm"), "Faceplate/ASM/Instrument")
        self.assertEqual(framework.faceplate_view("instrument-field", "openbridge"), "Faceplate/Instrument")
        sel = framework.FACEPLATE_OF_SELECTION
        for kind, view in (("sequence", "Faceplate/ASM/Sequence"), ("instrument", "Faceplate/ASM/Instrument"),
                           ("generator", "Faceplate/ASM/Generator")):
            self.assertIn(f"'{kind}', '{view}'", sel)

    def test_a_project_without_a_device_model_still_builds_its_generator(self):
        desc = copy.deepcopy(self.desc)
        desc["symbols"] = [s for s in desc["symbols"] if s["id"] in ("GEN1", "GEN2")]
        desc["tagValues"] = {}
        tags = screen.tags_document([desc], None)
        members = {t["name"] for f in tags["tags"] if f["name"] == "GEN1" for t in f["tags"]}
        self.assertEqual(members, set(devices_asm.GENERATOR_CORE))
        child, reports = screen.build_child("cadre_hmi_asmtest", [desc], "Asm", "*cadre_hmi_asmtest*", "stock")
        self.assertEqual(reports["/asm"]["errors"], [])


if __name__ == "__main__":
    unittest.main()


class DeviceReadKeyTests(unittest.TestCase):
    """Every `custom.dev` key an asm faceplate's bindings name is in its defaults: a binding to a key the poll never
    writes draws a quality overlay (G11 on the gateway, 2026-10-24: the maintenance pane of the generator and the
    sequence faceplates)."""

    def test_every_dev_reference_has_its_default(self):
        import re
        views = {**dict(library_views_of_asm())}
        for name, doc in views.items():
            text = json.dumps(doc)
            dev = doc["custom"]["dev"]
            for group, key in sorted(set(re.findall(r"\{view\.custom\.dev\.(has|value|writable|write)\.([A-Za-z0-9_]+)\}", text))):
                self.assertIn(key, dev[group], f"{name}: dev.{group}.{key}")


def library_views_of_asm():
    yield from devices_asm.views().items()                       # the generator, the sequence, the instrument
    for view in sorted(set(framework.ASM_VIEW.values()) - set(framework.ASM_BUILT)):
        yield view, framework.faceplate(view.split("/")[-1].lower(), "asm")

