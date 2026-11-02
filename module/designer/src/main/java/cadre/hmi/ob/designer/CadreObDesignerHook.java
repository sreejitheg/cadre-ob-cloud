package cadre.hmi.ob.designer;

import cadre.hmi.ob.common.CadreOb;
import com.inductiveautomation.ignition.common.licensing.LicenseState;
import com.inductiveautomation.ignition.designer.model.AbstractDesignerModuleHook;
import com.inductiveautomation.ignition.designer.model.DesignerContext;
import com.inductiveautomation.perspective.common.api.ComponentDescriptor;
import com.inductiveautomation.perspective.designer.DesignerComponentRegistry;
import com.inductiveautomation.perspective.designer.api.PerspectiveDesignerInterface;

/** Adds the components to the Designer's Perspective component palette ("Cadre OpenBridge"). */
public class CadreObDesignerHook extends AbstractDesignerModuleHook {
    private DesignerComponentRegistry registry;

    @Override
    public void startup(DesignerContext context, LicenseState activationState) {
        registry = PerspectiveDesignerInterface.get(context).getDesignerComponentRegistry();
        for (ComponentDescriptor d : CadreOb.DESCRIPTORS) {
            registry.registerComponent(d);
        }
    }

    @Override
    public void shutdown() {
        if (registry != null) {
            for (ComponentDescriptor d : CadreOb.DESCRIPTORS) {
                registry.removeComponent(d.id());
            }
        }
    }
}
