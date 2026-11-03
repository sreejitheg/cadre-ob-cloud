package cadre.hmi.ob.common;

import com.inductiveautomation.ignition.common.jsonschema.JsonSchema;
import com.inductiveautomation.perspective.common.api.BrowserResource;
import com.inductiveautomation.perspective.common.api.ComponentDescriptor;
import com.inductiveautomation.perspective.common.api.ComponentDescriptorImpl;
import com.inductiveautomation.perspective.common.api.ComponentEventDescriptor;

import java.util.List;
import java.util.Set;

/**
 * The Cadre OpenBridge module: OpenBridge web components (Apache-2.0, 2.0.0-next.155) registered as
 * Perspective components. The property and event schemas are generated from the OpenBridge custom
 * elements manifest by module/tools/gen_module_assets.py. Component events are declared as the Ignition
 * SDK's perspective-component example declares them (ComponentEventDescriptor, setEvents); the browser
 * wrappers fire them from the elements' own events.
 */
public final class CadreOb {
    public static final String MODULE_ID = "cadre.hmi.ob";
    public static final String URL_ALIAS = "cadreob";
    public static final String CATEGORY = "Cadre OpenBridge";

    /** One script (the OpenBridge elements, then the React wrappers) and one scoped stylesheet. */
    public static final Set<BrowserResource> BROWSER_RESOURCES = Set.of(
        new BrowserResource("cadre-ob-js", "/res/" + URL_ALIAS + "/js/cadre-ob.js", BrowserResource.ResourceType.JS),
        new BrowserResource("cadre-ob-css", "/res/" + URL_ALIAS + "/css/cadre-ob.css", BrowserResource.ResourceType.CSS)
    );

    public static final List<ComponentDescriptor> DESCRIPTORS = List.of(
        descriptor("cadre.ob.pump", "pump", "OB Pump",
            "OpenBridge pump: state, speed readout, badges and alert frame.", "obPump", List.of()),
        descriptor("cadre.ob.tank", "tank", "OB Tank",
            "OpenBridge tank: level, trend, value and maximum, badges and alert frame.", "obTank", List.of()),
        descriptor("cadre.ob.motor", "motor", "OB Motor",
            "OpenBridge motor: state, speed readout, badges and alert frame.", "obMotor", List.of()),
        descriptor("cadre.ob.fan", "fan", "OB Fan",
            "OpenBridge fan: state, speed readout, badges and alert frame.", "obFan", List.of()),
        descriptor("cadre.ob.valve", "valve", "OB Valve",
            "OpenBridge digital valve: open or closed, badges and alert frame.", "obValve", List.of()),
        descriptor("cadre.ob.analogvalve", "analogvalve", "OB Analog Valve",
            "OpenBridge analogue valve: opening readout, badges and alert frame.", "obAnalogValve", List.of()),
        descriptor("cadre.ob.filter", "filter", "OB Filter",
            "OpenBridge filter: a static symbol on a diagram, with readout, badges and alert frame.", "obFilter", List.of()),
        descriptor("cadre.ob.generator", "generator", "OB Generator",
            "OpenBridge generator indicator: running state, readout and alert frame.", "obGenerator", List.of()),
        descriptor("cadre.ob.button", "button", "OB Button",
            "OpenBridge automation button: a command button with identifier, state, progress and alert frame.", "obButton",
            List.of(event("button", "onPress", "The button was pressed; the event carries nothing."))),
        descriptor("cadre.ob.readout", "readout", "OB Readout",
            "OpenBridge readout: value chip with its unit and an identifier beneath it.", "obReadout", List.of()),
        descriptor("cadre.ob.instrumentfield", "instrumentfield", "OB Instrument Field",
            "OpenBridge instrument field: value, optional setpoint, caption and unit.", "obInstrumentField", List.of()),
        descriptor("cadre.ob.alertlist", "alertlist", "OB Alert List",
            "OpenBridge alert list: Alert records with ACK and row click.", "obAlertList",
            List.of(event("alertlist", "onAckClick", "The ACK button of an alert was clicked; event.ids holds its id."),
                    event("alertlist", "onRowClick", "An alert row was clicked; event.tagId is its device folder."))),
        descriptor("cadre.ob.alertpanel", "alertpanel", "OB Alert Panel",
            "OpenBridge alert panel: mode tabs, alert list, ACK visible and Silence.", "obAlertPanel",
            List.of(event("alertpanel", "onAckClick", "The ACK button of an alert was clicked; event.ids holds its id."),
                    event("alertpanel", "onRowClick", "An alert row was clicked; event.tagId is its device folder."),
                    event("alertpanel", "onSilenceClick", "The Silence button was clicked."),
                    event("alertpanel", "onAckAllClick", "ACK visible was clicked; event.ids holds the unacknowledged alerts shown."))),
        descriptor("cadre.ob.canvaszoom", "canvaszoom", "OB Canvas Zoom",
            "Canvas zoom: Ctrl+wheel, pinch and Ctrl+plus, minus, 0 scale only the canvas, not the browser page.", "obCanvasZoom", List.of()),
        descriptor("cadre.ob.resistor", "resistor", "OB Resistor",
            "OpenBridge resistor: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obResistor", List.of()),
        descriptor("cadre.ob.damper", "damper", "OB Damper",
            "OpenBridge damper: an air damper symbol on a diagram, open or closed, with readout, badges and alert frame.", "obDamper", List.of()),
        descriptor("cadre.ob.switch", "switch", "OB Switch",
            "OpenBridge switch: an electrical switch symbol on a diagram, with readout, badges and alert frame.", "obSwitch", List.of()),
        descriptor("cadre.ob.capacitor", "capacitor", "OB Capacitor",
            "OpenBridge capacitor: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obCapacitor", List.of()),
        descriptor("cadre.ob.diodes", "diodes", "OB Diodes",
            "OpenBridge diodes: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obDiodes", List.of()),
        descriptor("cadre.ob.ground", "ground", "OB Ground",
            "OpenBridge ground: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obGround", List.of()),
        descriptor("cadre.ob.source", "source", "OB Source",
            "OpenBridge source: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obSource", List.of()),
        descriptor("cadre.ob.converter", "converter", "OB Converter",
            "OpenBridge converter: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obConverter", List.of()),
        descriptor("cadre.ob.transformer", "transformer", "OB Transformer",
            "OpenBridge transformer: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obTransformer", List.of()),
        descriptor("cadre.ob.bipolartransistor", "bipolartransistor", "OB Bipolar Transistor",
            "OpenBridge bipolar transistor: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obBipolarTransistor", List.of()),
        descriptor("cadre.ob.mosfet", "mosfet", "OB MOSFET",
            "OpenBridge MOSFET: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obMosfet", List.of()),
        descriptor("cadre.ob.logic", "logic", "OB Logic",
            "OpenBridge logic: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obLogic", List.of()),
        descriptor("cadre.ob.router", "router", "OB Router",
            "OpenBridge router: a static electrical symbol on a diagram, with readout, badges and alert frame.", "obRouter", List.of()),
        descriptor("cadre.ob.automationbadge", "automationbadge", "OB Automation Badge",
            "OpenBridge automation badge: the small corner badge of an automation symbol, drawn on its own.", "obAutomationBadge", List.of()),
        descriptor("cadre.ob.checkvalve", "checkvalve", "OB Check Valve",
            "OpenBridge hydraulic check valve: a display-only glyph on a hydraulic diagram.", "obCheckValve", List.of()),
        descriptor("cadre.ob.valvetwoway", "valvetwoway", "OB Two-Way Valve Glyph",
            "OpenBridge analog two-way valve glyph: the valve with its opening, without readout or alert frame.", "obValveTwoWay", List.of()),
        descriptor("cadre.ob.valvethreeway", "valvethreeway", "OB Three-Way Valve Glyph",
            "OpenBridge analog three-way valve glyph: the valve with two openings, without readout or alert frame.", "obValveThreeWay", List.of()),
        descriptor("cadre.ob.battery", "battery", "OB Battery Indicator",
            "OpenBridge battery indicator: the level of a battery as a bar or a trend graph, display only.", "obBattery", List.of()),
        descriptor("cadre.ob.engine", "engine", "OB Engine Indicator",
            "OpenBridge engine indicator: an engine block in a static, regular or enhanced scheme, display only.", "obEngine", List.of()),
        descriptor("cadre.ob.tankatmospheric", "tankatmospheric", "OB Atmospheric Tank Indicator",
            "OpenBridge atmospheric tank indicator: the level of a tank as a bar or a trend graph, display only.", "obTankAtmospheric", List.of()),
        descriptor("cadre.ob.automationreadout", "automationreadout", "OB Automation Readout",
            "OpenBridge automation readout: a value with its unit in a bordered chip, display only.", "obAutomationReadout", List.of()),
        descriptor("cadre.ob.heatexchanger", "heatexchanger", "OB Heat Exchanger",
            "OpenBridge heat exchanger: a specialty tank with a hot and a cold side, badges and alert frame, display only.", "obHeatExchanger", List.of()),
        descriptor("cadre.ob.heatpump", "heatpump", "OB Heat Pump",
            "OpenBridge heat pump: a specialty tank with a hot and a cold side, badges and alert frame, display only.", "obHeatPump", List.of()),
        descriptor("cadre.ob.hydraulicseparator", "hydraulicseparator", "OB Hydraulic Separator",
            "OpenBridge hydraulic separator: a specialty tank with badges and alert frame, display only.", "obHydraulicSeparator", List.of()),
        descriptor("cadre.ob.gaugegenerator", "gaugegenerator", "OB Generator Gauge",
            "OpenBridge generator gauge: a dial with value, optional second value and setpoint marks, display only.", "obGaugeGenerator", List.of()),
        descriptor("cadre.ob.gaugemotorspumps", "gaugemotorspumps", "OB Motor and Pump Gauge",
            "OpenBridge motor and pump gauge: a dial with value, optional second value and setpoint marks, display only.", "obGaugeMotorsPumps", List.of()),
        descriptor("cadre.ob.gaugevalve", "gaugevalve", "OB Valve Gauge",
            "OpenBridge valve gauge: the opening of a two-way or three-way valve as a dial, with setpoint marks, display only.", "obGaugeValve", List.of()),
        descriptor("cadre.ob.hydraulicvalve43", "hydraulicvalve43", "OB Hydraulic 4/3 Valve",
            "OpenBridge hydraulic 4/3 valve: a three position selector showing the selected position, display only.", "obHydraulicValve43", List.of()),
        descriptor("cadre.ob.hydraulicvalvex2", "hydraulicvalvex2", "OB Hydraulic X/2 Valve",
            "OpenBridge hydraulic two position valve (2/2, 3/2 or 4/2): a selector showing the selected position, display only.", "obHydraulicValveX2", List.of()),
        descriptor("cadre.ob.transmitterbutton", "transmitterbutton", "OB Transmitter Button",
            "OpenBridge transmitter button: a readout chip with a value and unit, optional advice and setpoint segments, or a tag pill, display only.", "obTransmitterButton", List.of()),
        descriptor("cadre.ob.areagraph", "areagraph", "OB Area Graph",
            "OpenBridge area graph: one or several series drawn as filled areas, display only.", "obAreaGraph", List.of()),
        descriptor("cadre.ob.linegraph", "linegraph", "OB Line Graph",
            "OpenBridge line graph: one or several series drawn as lines, display only.", "obLineGraph", List.of()),
        descriptor("cadre.ob.donutchart", "donutchart", "OB Donut Chart",
            "OpenBridge donut chart: labelled segments of a ring with a centre total, display only.", "obDonutChart", List.of()),
        descriptor("cadre.ob.piechart", "piechart", "OB Pie Chart",
            "OpenBridge pie chart: labelled segments of a circle, with an optional sunburst ring of subsegments, display only.", "obPieChart", List.of()),
        descriptor("cadre.ob.polarchart", "polarchart", "OB Polar Chart",
            "OpenBridge polar chart: sectors of equal angle whose reach shows each value, display only.", "obPolarChart", List.of()),
        descriptor("cadre.ob.radialbarchart", "radialbarchart", "OB Radial Bar Chart",
            "OpenBridge radial bar chart: concentric rings, one for each value, display only.", "obRadialBarChart", List.of()),
        descriptor("cadre.ob.barhorizontal", "barhorizontal", "OB Horizontal Bar",
            "OpenBridge horizontal bar: a scale with an optional bar, value fill, advice zones and setpoint marker, display only.", "obBarHorizontal", List.of()),
        descriptor("cadre.ob.barvertical", "barvertical", "OB Vertical Bar",
            "OpenBridge vertical bar: a scale with an optional bar, value fill, advice zones and setpoint marker, display only.", "obBarVertical", List.of()),
        descriptor("cadre.ob.circularprogress", "circularprogress", "OB Circular Progress",
            "OpenBridge circular progress: a ring that fills with a value, or spins while the wait has no end, display only.", "obCircularProgress", List.of()),
        descriptor("cadre.ob.instrumentradial", "instrumentradial", "OB Radial Instrument",
            "OpenBridge radial instrument: a dial with a needle or filled arc, scale, advice zones and setpoint marker, display only.", "obInstrumentRadial", List.of()),
        descriptor("cadre.ob.readoutblock", "readoutblock", "OB Readout Block",
            "OpenBridge readout block: a number or text with a value, setpoint or advice marker, display only.", "obReadoutBlock", List.of())
    );

    private CadreOb() {
    }

    private static ComponentEventDescriptor event(String schema, String name, String description) {
        return new ComponentEventDescriptor(name, description,
            JsonSchema.parse(CadreOb.class.getResourceAsStream("/schemas/" + schema + "." + name + ".json")));
    }

    private static ComponentDescriptor descriptor(String id, String schema, String name, String description,
                                                  String metaName, List<ComponentEventDescriptor> events) {
        ComponentDescriptorImpl.ComponentBuilder b = ComponentDescriptorImpl.ComponentBuilder.newBuilder()
            .setPaletteCategory(CATEGORY)
            .setId(id)
            .setModuleId(MODULE_ID)
            .setSchema(JsonSchema.parse(CadreOb.class.getResourceAsStream("/schemas/" + schema + ".props.json")))
            .setName(name)
            .addPaletteEntry("", name, description, null, null)
            .setDefaultMetaName(metaName)
            .setResources(BROWSER_RESOURCES);
        if (!events.isEmpty()) {
            b = b.setEvents(events);
        }
        return b.build();
    }
}
