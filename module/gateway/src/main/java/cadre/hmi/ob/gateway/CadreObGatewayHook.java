package cadre.hmi.ob.gateway;

import cadre.hmi.ob.common.CadreOb;
import com.inductiveautomation.ignition.common.licensing.LicenseState;
import com.inductiveautomation.ignition.common.util.LoggerEx;
import com.inductiveautomation.ignition.gateway.model.AbstractGatewayModuleHook;
import com.inductiveautomation.ignition.gateway.model.GatewayContext;
import com.inductiveautomation.perspective.common.api.ComponentDescriptor;
import com.inductiveautomation.perspective.common.api.ComponentRegistry;
import com.inductiveautomation.perspective.gateway.api.PerspectiveContext;

import java.util.Optional;

/** Registers the components with Perspective and serves the browser resources under /res/cadreob/. */
public class CadreObGatewayHook extends AbstractGatewayModuleHook {
    private static final LoggerEx log = LoggerEx.newBuilder().build("cadre.hmi.ob.gateway");
    private GatewayContext gatewayContext;
    private ComponentRegistry componentRegistry;

    @Override
    public void setup(GatewayContext context) {
        this.gatewayContext = context;
    }

    @Override
    public void startup(LicenseState activationState) {
        componentRegistry = PerspectiveContext.get(gatewayContext).getComponentRegistry();
        if (componentRegistry == null) {
            log.error("Perspective component registry not found; Cadre OpenBridge components are unavailable.");
            return;
        }
        for (ComponentDescriptor d : CadreOb.DESCRIPTORS) {
            componentRegistry.registerComponent(d);
        }
        log.info("Registered " + CadreOb.DESCRIPTORS.size() + " Cadre OpenBridge components.");
    }

    @Override
    public void shutdown() {
        if (componentRegistry != null) {
            for (ComponentDescriptor d : CadreOb.DESCRIPTORS) {
                componentRegistry.removeComponent(d.id());
            }
        }
    }

    @Override
    public Optional<String> getMountedResourceFolder() {
        return Optional.of("mounted");
    }

    @Override
    public Optional<String> getMountPathAlias() {
        return Optional.of(CadreOb.URL_ALIAS);
    }

    @Override
    public boolean isFreeModule() {
        return true;
    }
}
