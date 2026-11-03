plugins {
    base
    // The Ignition module plugin: https://github.com/inductiveautomation/ignition-module-tools
    id("io.ia.sdk.modl") version("0.1.1")
}

allprojects {
    version = "0.5.0"
    group = "cadre.hmi.ob"
}

ignitionModule {
    fileName.set("CadreOpenBridge")
    name.set("Cadre OpenBridge")
    id.set("cadre.hmi.ob")
    moduleVersion.set("${project.version}")
    moduleDescription.set("OpenBridge web components (Apache-2.0, 2.0.0-next.155) as Perspective components: pump, motor, fan, valve, analogue valve, tank, filter, generator, automation button, damper, switch, resistor, capacitor, readout, instrument field, alert list and alert panel, with status, duty and out of service marks on the devices a canvas zoom component and row selection on the alert lists.")
    requiredIgnitionVersion.set("8.3.0")
    requiredFrameworkVersion.set("8")
    freeModule.set(true)
    license.set("license.html")
    moduleDependencies.putAll(mapOf("com.inductiveautomation.perspective" to "GD"))
    projectScopes.putAll(mapOf(":gateway" to "G", ":common" to "DG", ":designer" to "D"))
    hooks.putAll(
        mapOf(
            "cadre.hmi.ob.gateway.CadreObGatewayHook" to "G",
            "cadre.hmi.ob.designer.CadreObDesignerHook" to "D"
        )
    )
    // Signed with a self-signed certificate when the signing properties are given
    // (-Pignition.signing.*); the gateway then asks once to trust that certificate.
    skipModlSigning.set(!project.hasProperty("ignition.signing.keystoreFile"))
}
