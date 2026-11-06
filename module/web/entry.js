// The OpenBridge custom elements this module wraps. Each import defines its element
// (customElements.define) as a side effect; only these and their dependencies are bundled.
import '@oicl/openbridge-webcomponents/dist/automation/pump/pump.js';
import '@oicl/openbridge-webcomponents/dist/automation/automation-tank/automation-tank.js';
import '@oicl/openbridge-webcomponents/dist/automation/motor/motor.js';
import '@oicl/openbridge-webcomponents/dist/automation/fan/fan.js';
import '@oicl/openbridge-webcomponents/dist/automation/digital-valve/digital-valve.js';
import '@oicl/openbridge-webcomponents/dist/automation/analog-valve/analog-valve.js';
import '@oicl/openbridge-webcomponents/dist/automation/transmitter/transmitter.js';
import '@oicl/openbridge-webcomponents/dist/navigation-instruments/instrument-field/instrument-field.js';
import '@oicl/openbridge-webcomponents/dist/components/alert-list-details/alert-list-details.js';
import '@oicl/openbridge-webcomponents/dist/pages/alert-list-page-small/alert-list-page-small.js';
// The generator (module 0.4.4, ruling RW-01): the automation button, and the two pinned icons its wrapper places in the
// button's icon slots (running and stopped). No OpenBridge file is copied; the bundle imports them from the pin.
import '@oicl/openbridge-webcomponents/dist/automation/automation-button/automation-button.js';
import '@oicl/openbridge-webcomponents/dist/icons/icon-electric-generator-on.js';
import '@oicl/openbridge-webcomponents/dist/icons/icon-electric-generator-off.js';
