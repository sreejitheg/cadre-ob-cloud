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
        descriptor("cadre.ob.generator", "generator", "OB Generator",
            "OpenBridge generator: running or stopped icon, status word, badges and alert frame.", "obGenerator", List.of()),
        descriptor("cadre.ob.valve", "valve", "OB Valve",
            "OpenBridge digital valve: open or closed, badges and alert frame.", "obValve", List.of()),
        descriptor("cadre.ob.analogvalve", "analogvalve", "OB Analog Valve",
            "OpenBridge analogue valve: opening readout, badges and alert frame.", "obAnalogValve", List.of()),
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
            "Canvas zoom: Ctrl+wheel, pinch and Ctrl+plus, minus, 0 scale only the canvas, not the browser page.", "obCanvasZoom", List.of())
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
