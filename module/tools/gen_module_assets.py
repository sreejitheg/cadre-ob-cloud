"""Generate the Cadre HMI Components module's component assets from the pinned component package.

From the package's custom elements manifest (`custom-elements.json`), its enum declarations and
the measured element defaults (`module/web/defaults.json`, `measure_defaults.py`) this writes,
for every wrapped element:

  common/src/main/resources/schemas/<name>.props.json   Perspective property schema (Designer
                                                        property editor, validation, defaults)
  gateway/src/main/resources/mounted/js/cadre-ob.js     the component bundle followed by the
                                                        React wrappers and their registration
  gateway/src/main/resources/mounted/css/cadre-ob.css   the package stylesheet, scoped and trimmed
  gateway/src/main/resources/mounted/fonts/NotoSans-OB.ttf   the package's variable Noto Sans
  components.json                                       the contract: id, element, properties
  web/canvaszoom.js                                     (read, not written) the canvas zoom component, appended to
                                                        cadre-ob.js; its schema and contract entry are written here

A module's browser resources load in every Perspective session of the gateway, so the
stylesheet is scoped: the package declares its palettes and sizes on `:root` and some variables on
`*`; here they are declared on the wrapper (`.cadre-ob`) and keyed to the Cadre palette classes,
and only the variables the bundled elements use (with their dependencies) are kept.

Usage:  python module/tools/gen_module_assets.py [--allow-stale-bundle]

The pin check (`verify_pin.require_pin`) runs first. Without `--allow-stale-bundle` the bundle must be the one
`npm run build` recorded for this checkout (`verify_pin.require_bundle_record`: the SHA-256 of `package-lock.json`,
`entry.js` and the bundle beside it).

`node_modules` and `dist/` (the esbuild bundle) are read from `verify_pin.web_root()`: the sibling `web` folder, or the
folder named by the environment variable `CADRE_OB_WEB_ROOT` (a read only `module/web` of the main checkout, for a
worktree that has no `node_modules`). Nothing is written there. The tracked sources (`defaults.json`, `canvaszoom.js`,
`icons.js`) are always read from this module's own `web` folder. The run stops when the bundle does not define a wrapped
element, because the wrapper would register a tag nothing draws; `--allow-stale-bundle` lets it write anyway, for a host
that cannot rebuild the bundle (it then prints the tags missing, and the bundle is rebuilt, the defaults measured again
and this script run again before the module is built).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_pin  # noqa: E402  (the pin check runs first in main)

HERE = Path(__file__).resolve().parents[1]
WEB = verify_pin.web_root()                                   # node_modules and the built bundle (maybe another checkout)
PKG = WEB / "node_modules/@oicl/openbridge-webcomponents"
MOUNTED = HERE / "gateway/src/main/resources/mounted"
SCHEMAS = HERE / "common/src/main/resources/schemas"

# The wrapped elements: Perspective component id, short name, palette text, default size. `data`
# declares properties that carry JSON data rather than a scalar attribute (read from the property
# tree as plain JSON, `readArray`, measured GF-38, and converted for the element); `events` maps an
# element's custom event to the Perspective component event it fires (`componentEvents.
# fireComponentEvent`, measured GF-37) and the payload built from the event detail.
ALERT_EVENTS = {
    "ack-click": ("onAckClick", "alert", "The ACK button of an alert was clicked. event.ids holds its alert id; "
                                         "event.id, event.tagId, event.source and event.text describe it."),
    "row-click": ("onRowClick", "alert", "An alert row was clicked. event.ids holds its alert id; event.tagId is "
                                         "the device folder of the alarm."),
    "silence-click": ("onSilenceClick", "none", "The Silence button was clicked."),
    "ack-all-visible-click": ("onAckAllClick", "visible", "The ACK visible button was clicked. event.mode is the "
                                                          "list mode; event.ids holds the unacknowledged alerts it shows."),
    # The command button (spike T0 wrap W3): the element's own `click`, with no detail to carry.
    "click": ("onPress", "none", "The button was pressed. The event carries nothing; the page's script decides what it "
                                 "commands (the library's confirmed pulse, write path W18)."),
    # The frame components (T2, batch F1): events that carry a detail. None of them is wired to a script by the module.
    "obc-click": ("onNotificationClick", "notification", "The notification button was pressed. event.count is the count the "
                  "button holds; event.isActive is the state the press asks for (the opposite of the state shown; the "
                  "component does not toggle itself, the page sets isActive)."),
    "primary-action": ("onPrimaryAction", "label", "The primary button of the toggletip was pressed. event.label is the "
                       "text of the button."),
    "secondary-action": ("onSecondaryAction", "label", "The secondary button of the toggletip was pressed. event.label is "
                         "the text of the button."),
    # The alert button and the alert menu (T2, batch F2). Names that an earlier row holds for the alarm lists (`ack-click`,
    # `silence-click`) keep their name here; a component words the event for itself with `eventText` and changes the payload
    # with `eventKinds`.
    "click-alert": ("onAlertClick", "none", "The bell was pressed. The event carries nothing; the page's script decides what it opens."),
    "click-silence": ("onSilenceClick", "none", "The silence control of the alert button was pressed. The control is hidden by default "
                      "(`showSilenceButton`); the event carries nothing."),
    "item-click": ("onItemClick", "none", "The row was pressed. The event carries nothing."),
    "ack-secondary-click": ("onAckSecondaryClick", "none", "The secondary action of the row was pressed. The event carries nothing."),
    "go-to-alert-list-click": ("onGoToAlertListClick", "none", "The Alerts button of the menu was pressed. The event carries nothing; "
                               "the page's script decides where it goes."),
    # Navigation, tree navigation and the breadcrumb (T2, batch F3). A component changes the name with `eventNames`, the payload
    # with `eventKinds` and the text with `eventText`; `customEvents` names the events that only a CustomEvent of the element counts.
    "open": ("onOpen", "none", "The group was opened. The event carries nothing."),
    "expand-toggle": ("onExpandToggle", "expanded", "The row asks to open or close its children. event.expanded is the state the "
                      "press asks for; the group applies it itself."),
    "breadcrumb-click": ("onBreadcrumbClick", "crumb", "A crumb was pressed. event.label and event.href are the crumb's, event.index is "
                         "its position in `items` (the last crumb is the current page and is not a button)."),
    # The menus and the top bar (T2, batch F4). The kind `detail` builds the payload from the entry's `eventFields` (the fields of
    # the element's event detail, by name and type), so a component states its own fields; the rows give the name and the text.
    "search": ("onSearch", "detail", "The text of the search field changed. event.query is the text now in the field."),
    "change": ("onChange", "detail", "The element reports a change."),
    "palette-changed": ("onPaletteChanged", "detail", "A palette was chosen. event.value is the palette: night, dusk, day or bright."),
    "brightness-changed": ("onBrightnessChanged", "detail", "The brightness was changed. event.value is the new brightness."),
    "link-palette-changed": ("onLinkPaletteChanged", "detail", "The link palette switch was changed. event.value is the state of the switch."),
    "link-brightness-changed": ("onLinkBrightnessChanged", "detail",
                                "The link brightness switch was changed. event.value is the state of the switch."),
    "screen-control-link-clicked": ("onScreenControlLinkClick", "none", "The screen control link was pressed. The event carries nothing."),
    "sign-in-click": ("onSignInClick", "none", "The Sign in button was pressed. The event carries nothing: the module never reads a user "
                      "name or a password, and the page's script opens the gateway's own login."),
    "sign-out-click": ("onSignOutClick", "none", "The Sign out button was pressed. The event carries nothing."),
    "use-another-account-click": ("onUseAnotherAccountClick", "none", "The Use another account button was pressed. The event carries nothing."),
    "menu-button-clicked": ("onMenuButtonClick", "none", "The menu button was released. The event carries nothing."),
    "dimming-button-clicked": ("onDimmingButtonClick", "none", "The dimming button was pressed. The event carries nothing."),
    "apps-button-clicked": ("onAppsButtonClick", "none", "The apps button was pressed. The event carries nothing."),
    "left-more-button-clicked": ("onMoreButtonClick", "none", "The more button was pressed. The event carries nothing."),
    "user-button-clicked": ("onUserButtonClick", "none", "The user button was pressed. The event carries nothing."),
    "emergency-brightness-start": ("onEmergencyBrightnessStart", "none",
                                   "The menu button was held for half a second, which asks for the emergency brightness. The event carries nothing."),
    "emergency-brightness-stop": ("onEmergencyBrightnessStop", "none", "The held menu button was released. The event carries nothing."),
    "back": ("onBack", "none", "The Back button of the settings mode was pressed. The event carries nothing."),
    "close": ("onClose", "none", "The Close button of the settings mode was pressed. The event carries nothing."),
    "wifi-click": ("onWifiClick", "detail", "The Wi-Fi switch was changed. event.enabled is the state the switch asks for."),
    "audio-click": ("onAudioClick", "detail", "The audio mute button was pressed. event.muted is the state the button asks for."),
    "audio-volume-change": ("onAudioVolumeChange", "detail", "The audio volume was changed. event.volume is the new volume."),
    "microphone-click": ("onMicrophoneClick", "detail", "The microphone mute button was pressed. event.muted is the state it asks for."),
    "push-to-talk-change": ("onPushToTalkChange", "detail", "The push to talk switch was changed. event.pushToTalk is its state."),
    "battery-saving-mode-change": ("onBatterySavingModeChange", "detail",
                                   "The battery saving mode switch was changed. event.batterySavingMode is its state."),
    "battery-usage-click": ("onBatteryUsageClick", "detail", "The battery usage button was pressed. event.usage is true."),
    "wifi-network-change": ("onWifiNetworkChange", "detail", "A Wi-Fi network was chosen. event.network is its name."),
    "audio-output-change": ("onAudioOutputChange", "detail", "An audio output was chosen. event.output is its name."),
    "microphone-input-change": ("onMicrophoneInputChange", "detail", "A microphone input was chosen. event.input is its name."),
    "battery-mode-change": ("onBatteryModeChange", "detail", "A battery mode was chosen. event.mode is its name."),
    "settings-click": ("onSettingsClick", "none", "The Settings button was pressed. The event carries nothing."),
    "to-sub-menu-click": ("onSubMenuClick", "none", "A heading that opens a sub menu was pressed (with `externalControl` the menu does not "
                          "open it itself). The event carries nothing."),
    "wifi-options-click": ("onWifiOptionsClick", "none", "The Wi-Fi Options button was pressed. The event carries nothing."),
    "wifi-disconnect-click": ("onWifiDisconnectClick", "none", "The Wi-Fi Disconnect button was pressed. The event carries nothing."),
    # Tabs, pivots, the modal window, the context menu and the notification items (T2, batch F5). The kind `detail` takes its fields
    # from the entry's `eventFields` (a `from` with a dot reads a field of a nested object of the detail).
    "tab-click": ("onTabClick", "detail", "The tab was pressed. event.title is the title of the tab."),
    "tab-close": ("onTabClose", "detail", "The close button of the tab was pressed. event.title is the title of the tab."),
    "tab-selected": ("onTabSelected", "detail", "A tab was pressed. event.id, event.index and event.title name the tab."),
    "tab-closed": ("onTabClosed", "detail", "The close button of a tab was pressed. event.id, event.index and event.title name the tab."),
    "add-new-tab": ("onAddNewTab", "none", "The button that adds a tab was pressed. The event carries nothing."),
    "selected": ("onSelected", "detail", "The pivot was pressed while enabled and not selected. event.value is its value."),
    "close-click": ("onCloseClick", "none", "The close button of the window was pressed. The event carries nothing."),
    "cancel-click": ("onCancelClick", "none", "The cancel button of the window was pressed. The event carries nothing."),
    "done-click": ("onDoneClick", "none", "The done button of the window was pressed. The event carries nothing."),
    "option-click": ("onOptionClick", "none", "The optional action button of the window was pressed. The event carries nothing."),
    "message-click": ("onMessageClick", "none", "The item was pressed outside its action. The event carries nothing."),
    "action-click": ("onActionClick", "none", "The (primary) action of the item was pressed. The event carries nothing."),
    "action2-click": ("onAction2Click", "none", "The secondary action of the item was pressed. The event carries nothing."),
    "dismiss-click": ("onDismissClick", "none", "The dismiss button of the item was pressed. The event carries nothing."),
    "primary-action-click": ("onPrimaryActionClick", "none", "The primary action of the item was pressed. The event carries nothing."),
    "secondary-action-click": ("onSecondaryActionClick", "none", "The secondary action of the item was pressed. The event carries nothing."),
}
# The properties of the object a Perspective component event carries, by payload kind (the wrapper's `payload` builds the
# object from the element's event detail). A kind a later wrap needs is one entry here and one branch of `payload`.
PAYLOAD_PROPS = {
    "none": {},
    "detail": {},      # built from the entry's `eventFields` (see `event_payload_props`)
    "alert": {"ids": {"type": "array", "description": "The alert ids of the event."},
              "id": {"type": "string"}, "tagId": {"type": "string", "description": "The device folder."},
              "source": {"type": "string"}, "text": {"type": "string"}},
    "visible": {"ids": {"type": "array", "description": "The alert ids of the event."},
                "mode": {"type": "string", "description": "The list mode."}},
    "notification": {"count": {"type": "number", "description": "The count the button holds."},
                     "isActive": {"type": "boolean", "description": "The active state the press asks for."}},
    "label": {"label": {"type": "string", "description": "The text of the button that was pressed."}},
    # an event of a child built from `items`: the `id` its item object carries (empty if none) and its tag
    # the ACK visible button of the alert menu: the tab it acted on and the `id` of each visible row that has one
    "menuvisible": {"mode": {"type": "string", "description": "The tab the button acted on: unacked, all or shelved."},
                    "ids": {"type": "array", "description": "The `id` of each visible row that has one."}},
    "item": {"id": {"type": "string", "description": "The id of the item the event came from (empty if it has none)."},
             "tag": {"type": "string", "description": "The tag of the item the event came from."}},
    # batch F3: the state a row asks for (a row of the tree, alone or inside a list) and the crumb that was pressed
    "expanded": {"expanded": {"type": "boolean", "description": "The state the press asks for: true opens the row, false closes it."}},
    "itemexpanded": {"id": {"type": "string", "description": "The id of the item the event came from (empty if it has none)."},
                     "tag": {"type": "string", "description": "The tag of the item the event came from."},
                     "expanded": {"type": "boolean", "description": "The state the press asks for: true opens the row, false closes it."}},
    "crumb": {"label": {"type": "string", "description": "The label of the crumb that was pressed."},
              "href": {"type": "string", "description": "The href of the crumb (empty if it has none)."},
              "index": {"type": "number", "description": "The position of the crumb in `items`, from 0."}},
}
# The attributes of the two line chart elements that serve a slotted external scale or an instrument panel (`state`,
# `frameStyle`, the border radius family, `instrumentMode`) and the element's debug overlay: the module draws the chart
# alone, and a nullable enumeration (`borderRadiusPosition` is undefined by default, and any value adds a border) is not
# a property the contract carries.
LINE_FRAME = ["state", "frameStyle", "borderRadiusPosition", "borderRadiusPositionExternalScales", "instrumentMode",
              "borderRadius", "showDebugOverlay"]
# The attributes of the two bars (C2) that the module leaves out: the two nullable enumerations (`barContainerStyle` and
# `borderRadiusPosition` are undefined by default, and any explicit value overrides what the element derives), and the
# instrument mode with the border radius it enables, which serve a bar placed inside another instrument.
BAR_LEFT_OUT = ["barContainerStyle", "borderRadiusPosition", "instrumentMode", "borderRadius"]
# The alert type of the alert button family. The package's `AlertType` has the three IEC names and five severity levels; the five
# Cadre priorities map onto them as wiki 13 section 11.1 says (the module's colours already follow it): Critical the critical
# level (`level-critical`), High alarm, Medium warning, Low caution and Diagnostic none (empty). An empty value is the idle state,
# drawn without an alert colour.
ALERT_TYPE_TEXT = ("The alert type that selects the icon and colours. The Cadre priorities map onto it as wiki 13 section 11.1 says: "
                   "Critical level-critical, High alarm, Medium warning, Low caution, Diagnostic empty (no alert colour); "
                   "level-high, level-medium and level-low draw the same colours as alarm, warning and caution. Empty draws the idle state.")
# The per-severity counts a navigation or tree row shows as badges (`TreeNavigationItemAlerts`, the pinned `types.d.ts`
# `AlertCounts` and `combine`). The five Cadre priorities map onto the count fields as wiki 13 section 11.1 says (the same
# mapping as the alert button's `alertType`): Critical countLevelCritical, High countAlarm, Medium countWarning, Low countCaution,
# Diagnostic countLevelDiagnostic. A count of zero or less draws no badge.
ALERT_COUNT_FIELDS = ["countLevelCritical", "countAlarm", "countLevelHigh", "countWarning", "countLevelMedium", "countCaution",
                      "countLevelLow", "countLevelDiagnostic"]
ALERTS_TEXT = ("The active alerts at or beneath the row, as a badge for each severity with a count above zero: an object with the counts "
               + ", ".join(ALERT_COUNT_FIELDS) + " and combine (one badge with the total, in the colour of the highest severity). The "
               "Cadre priorities map onto the counts as wiki 13 section 11.1 says: Critical countLevelCritical, High countAlarm, Medium "
               "countWarning, Low countCaution, Diagnostic countLevelDiagnostic. An open group shows no badge of its own.")
ALERTS_SCHEMA = {"type": "object", "default": {},
                 "properties": {**{f: {"type": "number"} for f in ALERT_COUNT_FIELDS}, "combine": {"type": "boolean"}},
                 "description": ALERTS_TEXT}
# The state objects of the system menu (`WifiState`, `AudioState`, `MicrophoneState`, `BatteryState` of the pinned `system-menu.d.ts`),
# carried as plain objects (the field kind `object`, like the alert counts). The menu draws a section only while its object is
# present, and it writes to the object it is given, so the wrapper hands it a copy. The wording is our own.
CONTROL_MODES = ["mute-button", "icon-only", "hidden"]
STATE_OBJECTS = {
    "WifiState": ("The Wi-Fi section: whether it is on and connected, the network joined and its strength, a status word, and the networks "
                  "to choose from (`networks`, then `otherNetworks`). Empty draws no Wi-Fi section.",
                  {"enabled": {"type": "boolean"}, "connected": {"type": "boolean"}, "networkName": {"type": "string"},
                   "strength": {"type": "number"}, "status": {"type": "string"},
                   "networks": {"type": "array", "items": {"type": "object", "properties": {
                       "name": {"type": "string"}, "signalStrength": {"type": "number"}}}},
                   "otherNetworks": {"type": "array", "items": {"type": "object", "properties": {
                       "name": {"type": "string"}, "signalStrength": {"type": "number"}}}}}),
    "AudioState": ("The audio section: whether it is muted, the volume, the outputs to choose from, the output chosen and how the mute "
                   "control is drawn (`controlMode`: mute-button, icon-only or hidden). Empty draws no audio section.",
                   {"muted": {"type": "boolean"}, "volume": {"type": "number"},
                    "outputs": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}}}},
                    "selectedOutput": {"type": "string"}, "controlMode": {"type": "string", "enum": CONTROL_MODES}}),
    "MicrophoneState": ("The microphone section: whether it is muted, the level now heard, the inputs to choose from, the input chosen, the "
                        "push to talk state and how the mute control is drawn (`controlMode`). Empty draws no microphone section.",
                        {"muted": {"type": "boolean"}, "currentLevel": {"type": "number"},
                         "inputs": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}}}},
                         "selectedInput": {"type": "string"}, "pushToTalk": {"type": "boolean"},
                         "controlMode": {"type": "string", "enum": CONTROL_MODES}}),
    "BatteryState": ("The battery section: the charge level, whether it charges, whether the device is powered and not charging, a "
                     "notification flag, the battery saving mode, whether a usage button is drawn, and the modes to choose from. "
                     "Empty draws no battery section.",
                     {"level": {"type": "number"}, "charging": {"type": "boolean"}, "poweredNotCharging": {"type": "boolean"},
                      "notification": {"type": "boolean"}, "batterySavingMode": {"type": "boolean"}, "hasUsageButton": {"type": "boolean"},
                      "modes": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}}}},
                      "selectedMode": {"type": "string"}}),
}
COMPONENTS = [
    {"tag": "obc-pump", "type": "cadre.ob.pump", "name": "pump", "title": "Pump",
     "palette": "Pump: state, speed readout, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "extra": ["hasSpeed", "showStatus", "statusText", "badgeDuty", "outOfService"], "speedless": True, "status": True},
    {"tag": "obc-automation-tank", "type": "cadre.ob.tank", "name": "tank", "title": "Tank",
     "palette": "Tank: level, trend, value and maximum, badges and alert frame",
     "size": {"width": 168, "height": 216}, "exclude": ["touching"], "extra": ["unit", "hasCapacity"],
     "tankSlots": True},
    {"tag": "obc-motor", "type": "cadre.ob.motor", "name": "motor", "title": "Motor",
     "palette": "Motor: state, speed readout, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "extra": ["hasSpeed", "showStatus", "statusText", "badgeDuty", "outOfService"], "speedless": True, "status": True},
    {"tag": "obc-fan", "type": "cadre.ob.fan", "name": "fan", "title": "Fan",
     "palette": "Fan: state, speed readout, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "extra": ["hasSpeed", "showStatus", "statusText", "badgeDuty", "outOfService"], "speedless": True, "status": True},
    {"tag": "obc-digital-valve", "type": "cadre.ob.valve", "name": "valve", "title": "Valve",
     "palette": "Digital valve: open or closed, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-analog-valve", "type": "cadre.ob.analogvalve", "name": "analogvalve", "title": "Analog Valve",
     "palette": "Analogue valve: opening readout, badges and alert frame", "size": {"width": 96, "height": 96},
     "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-filter", "type": "cadre.ob.filter", "name": "filter", "title": "Filter",
     "palette": "Filter: a static symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-indicator-generator", "type": "cadre.ob.generator", "name": "generator", "title": "Generator",
     "palette": "Generator indicator: running state, readout and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "generator": True,
     "extra": ["on", "tag", "readoutPosition", "showStatus", "statusText", "alert", "alertFrameStatus", "alertFrameMode"],
     "describe": {"showStatus": "Whether the symbol draws its status word (On or Off, or statusText). False hides the "
                               "word; the identifier stays. The diagram toolbar's Readout button binds it.",
                  "statusText": "When not empty, the status word drawn beside the symbol in place of On or Off."}},
    {"tag": "obc-automation-button", "type": "cadre.ob.button", "name": "button", "title": "Button",
     "palette": "Automation button: a command button with identifier, state, progress and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "events": ["click"]},
    {"tag": "obc-transmitter", "type": "cadre.ob.readout", "name": "readout", "title": "Readout",
     "palette": "Transmitter: value chip with unit and an identifier beneath it",
     "size": {"width": 72, "height": 24}, "exclude": ["data", "lineType"], "extra": ["stretch"], "sheet": "readout",
     "chipSheet": "readoutchip"},
    {"tag": "obc-instrument-field", "type": "cadre.ob.instrumentfield", "name": "instrumentfield",
     "title": "Instrument Field", "palette": "Instrument field: value, optional setpoint, caption and unit",
     "size": {"width": 96, "height": 64}, "exclude": [], "sheet": "instrumentfield", "endAligned": True},
    {"tag": "obc-alert-list-details", "type": "cadre.ob.alertlist", "name": "alertlist", "title": "Alert List",
     "palette": "Alert list: Alert records with ACK and row click", "size": {"width": 368, "height": 480},
     "exclude": [], "dts": "components/alert-list-details/alert-list-details.d.ts",
     "data": {"alerts": "alerts"}, "events": ["ack-click", "row-click"],
     "extra": ["selectable", "selectedIds"], "selection": True},
    {"tag": "obc-alert-list-page-small", "type": "cadre.ob.alertpanel", "name": "alertpanel", "title": "Alert Panel",
     "palette": "Alert panel: mode tabs, alert list, ACK visible and Silence",
     "size": {"width": 640, "height": 420}, "exclude": [], "dts": "pages/alert-list-page-small/alert-list-page-small.d.ts",
     "data": {"alerts": "alerts"}, "events": ["ack-click", "row-click", "silence-click", "ack-all-visible-click"],
     "extra": ["selectable", "selectedIds"], "selection": True},
    {"tag": "obc-resistor", "type": "cadre.ob.resistor", "name": "resistor", "title": "Resistor",
     "palette": "Resistor: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-damper", "type": "cadre.ob.damper", "name": "damper", "title": "Damper",
     "palette": "Damper: an air damper symbol on a diagram, open or closed, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-switch", "type": "cadre.ob.switch", "name": "switch", "title": "Switch",
     "palette": "Switch: an electrical switch symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-capacitor", "type": "cadre.ob.capacitor", "name": "capacitor", "title": "Capacitor",
     "palette": "Capacitor: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-diodes", "type": "cadre.ob.diodes", "name": "diodes", "title": "Diodes",
     "palette": "Diodes: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-ground", "type": "cadre.ob.ground", "name": "ground", "title": "Ground",
     "palette": "Ground: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-source", "type": "cadre.ob.source", "name": "source", "title": "Source",
     "palette": "Source: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-converter", "type": "cadre.ob.converter", "name": "converter", "title": "Converter",
     "palette": "Converter: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-transformer", "type": "cadre.ob.transformer", "name": "transformer", "title": "Transformer",
     "palette": "Transformer: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-bipolar-transistor", "type": "cadre.ob.bipolartransistor", "name": "bipolartransistor", "title": "Bipolar Transistor",
     "palette": "Bipolar transistor: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-mosfet", "type": "cadre.ob.mosfet", "name": "mosfet", "title": "MOSFET",
     "palette": "MOSFET: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-logic", "type": "cadre.ob.logic", "name": "logic", "title": "Logic",
     "palette": "Logic: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-router", "type": "cadre.ob.router", "name": "router", "title": "Router",
     "palette": "Router: a static electrical symbol on a diagram, with readout, badges and alert frame",
     "size": {"width": 96, "height": 96}, "exclude": [], "properties": ["showStatus"]},
    {"tag": "obc-automation-badge", "type": "cadre.ob.automationbadge", "name": "automationbadge", "title": "Automation Badge",
     "palette": "Automation badge: the small corner badge of an automation symbol, drawn on its own (mode and type)",
     "size": {"width": 32, "height": 32}, "exclude": []},
    {"tag": "obc-hydraulic-check-valve", "type": "cadre.ob.checkvalve", "name": "checkvalve", "title": "Check Valve",
     "palette": "Hydraulic check valve: a display-only glyph on a hydraulic diagram",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-valve-analog-two-way-icon", "type": "cadre.ob.valvetwoway", "name": "valvetwoway", "title": "Two-Way Valve Glyph",
     "palette": "Analog two-way valve glyph: the valve with its opening, without readout or alert frame",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-valve-analog-three-way-icon", "type": "cadre.ob.valvethreeway", "name": "valvethreeway", "title": "Three-Way Valve Glyph",
     "palette": "Analog three-way valve glyph: the valve with two openings, without readout or alert frame",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-indicator-battery", "type": "cadre.ob.battery", "name": "battery", "title": "Battery Indicator",
     "palette": "Battery indicator: a battery drawn as a level bar or a trend graph, display only",
     "size": {"width": 48, "height": 48}, "exclude": [], "data": {"data": "numbers"}},
    {"tag": "obc-indicator-engine", "type": "cadre.ob.engine", "name": "engine", "title": "Engine Indicator",
     "palette": "Engine indicator: an engine block drawn in a static, regular or enhanced scheme, display only",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-indicator-tank-atmospheric", "type": "cadre.ob.tankatmospheric", "name": "tankatmospheric",
     "title": "Atmospheric Tank Indicator",
     "palette": "Atmospheric tank indicator: a tank drawn as a level bar or a trend graph, display only",
     "size": {"width": 48, "height": 48}, "exclude": [], "data": {"data": "numbers"}},
    {"tag": "obc-automation-readout", "type": "cadre.ob.automationreadout", "name": "automationreadout",
     "title": "Automation Readout",
     "palette": "Automation readout: a value with its unit in a bordered chip, display only",
     "size": {"width": 72, "height": 48}, "exclude": ["lineType"]},
    {"tag": "obc-heat-exchanger", "type": "cadre.ob.heatexchanger", "name": "heatexchanger", "title": "Heat Exchanger",
     "palette": "Heat exchanger: a specialty tank with a hot and a cold side, badges and alert frame, display only",
     "size": {"width": 152, "height": 96}, "exclude": []},
    {"tag": "obc-heat-pump", "type": "cadre.ob.heatpump", "name": "heatpump", "title": "Heat Pump",
     "palette": "Heat pump: a specialty tank with a hot and a cold side, badges and alert frame, display only",
     "size": {"width": 152, "height": 96}, "exclude": []},
    {"tag": "obc-hydraulic-separator", "type": "cadre.ob.hydraulicseparator", "name": "hydraulicseparator", "title": "Hydraulic Separator",
     "palette": "Hydraulic separator: a specialty tank with badges and alert frame, display only",
     "size": {"width": 152, "height": 96}, "exclude": []},
    {"tag": "obc-gauge-generator", "type": "cadre.ob.gaugegenerator", "name": "gaugegenerator", "title": "Generator Gauge",
     "palette": "Generator gauge: a dial with value, optional second value and setpoint marks, display only",
     "size": {"width": 240, "height": 280}, "exclude": []},
    {"tag": "obc-gauge-motors-and-pumps", "type": "cadre.ob.gaugemotorspumps", "name": "gaugemotorspumps", "title": "Motor and Pump Gauge",
     "palette": "Motor and pump gauge: a dial with value, optional second value and setpoint marks, display only",
     "size": {"width": 240, "height": 280}, "exclude": []},
    {"tag": "obc-gauge-valve", "type": "cadre.ob.gaugevalve", "name": "gaugevalve", "title": "Valve Gauge",
     "palette": "Valve gauge: the opening of a two-way or three-way valve as a dial, with setpoint marks, display only",
     "size": {"width": 240, "height": 280}, "exclude": []},
    {"tag": "obc-hydraulic-valve-4-3", "type": "cadre.ob.hydraulicvalve43", "name": "hydraulicvalve43", "title": "Hydraulic 4/3 Valve",
     "palette": "Hydraulic 4/3 valve: a three position selector showing the selected position, display only",
     "size": {"width": 144, "height": 48}, "exclude": []},
    {"tag": "obc-hydraulic-valve-x-2", "type": "cadre.ob.hydraulicvalvex2", "name": "hydraulicvalvex2", "title": "Hydraulic X/2 Valve",
     "palette": "Hydraulic two position valve (2/2, 3/2 or 4/2): a selector showing the selected position, display only",
     "size": {"width": 96, "height": 48}, "exclude": []},
    {"tag": "obc-transmitter-button", "type": "cadre.ob.transmitterbutton", "name": "transmitterbutton", "title": "Transmitter Button",
     "palette": "Transmitter button: a readout chip with a value and unit, optional advice and setpoint segments, or a tag pill, display only",
     "size": {"width": 96, "height": 40}, "exclude": []},
    # batch C1: the bars and graphs (module-only, display only). The series and segments are lists of objects (`data`).
    {"tag": "obc-area-graph", "type": "cadre.ob.areagraph", "name": "areagraph", "title": "Area Graph",
     "palette": "Area graph: one or several series drawn as filled areas, display only",
     "size": {"width": 480, "height": 320}, "exclude": LINE_FRAME,
     "data": {"data": "points", "datasets": "datasets", "labels": "labels", "colors": "colors", "yAxes": "yaxes"}},
    {"tag": "obc-line-graph", "type": "cadre.ob.linegraph", "name": "linegraph", "title": "Line Graph",
     "palette": "Line graph: one or several series drawn as lines, display only",
     "size": {"width": 480, "height": 320}, "exclude": LINE_FRAME,
     "data": {"data": "points", "datasets": "datasets", "labels": "labels", "colors": "colors", "yAxes": "yaxes"}},
    {"tag": "obc-donut-chart", "type": "cadre.ob.donutchart", "name": "donutchart", "title": "Donut Chart",
     "palette": "Donut chart: labelled segments of a ring with a centre total, display only",
     "size": {"width": 480, "height": 320}, "exclude": ["showDebugOverlay"],
     "data": {"data": "segments", "colors": "colors"}},
    {"tag": "obc-pie-chart", "type": "cadre.ob.piechart", "name": "piechart", "title": "Pie Chart",
     "palette": "Pie chart: labelled segments of a circle, with an optional sunburst ring of subsegments, display only",
     "size": {"width": 480, "height": 320}, "exclude": ["showDebugOverlay"],
     "data": {"data": "piesegments", "colors": "colors"}},
    {"tag": "obc-polar-chart", "type": "cadre.ob.polarchart", "name": "polarchart", "title": "Polar Chart",
     "palette": "Polar chart: sectors of equal angle whose reach shows each value, display only",
     "size": {"width": 480, "height": 320}, "exclude": ["showDebugOverlay"],
     "data": {"data": "segments", "colors": "colors"}},
    {"tag": "obc-radial-bar-chart", "type": "cadre.ob.radialbarchart", "name": "radialbarchart", "title": "Radial Bar Chart",
     "palette": "Radial bar chart: concentric rings, one for each value, display only",
     "size": {"width": 480, "height": 320}, "exclude": ["showDebugOverlay"],
     "data": {"data": "rings", "colors": "colors"}},
    # batch C2: the building blocks (module-only, display only). The scale of a bar is drawn by the element itself.
    {"tag": "obc-bar-horizontal", "type": "cadre.ob.barhorizontal", "name": "barhorizontal", "title": "Horizontal Bar",
     "palette": "Horizontal bar: a scale with an optional bar, value fill, advice zones and setpoint marker, display only",
     "size": {"width": 480, "height": 128}, "exclude": BAR_LEFT_OUT, "properties": ["hasScale", "showLabels"],
     "data": {"advices": "linearadvices"}},
    {"tag": "obc-bar-vertical", "type": "cadre.ob.barvertical", "name": "barvertical", "title": "Vertical Bar",
     "palette": "Vertical bar: a scale with an optional bar, value fill, advice zones and setpoint marker, display only",
     "size": {"width": 128, "height": 320}, "exclude": BAR_LEFT_OUT, "properties": ["hasScale", "showLabels"],
     "data": {"advices": "linearadvices"}},
    {"tag": "obc-circular-progress", "type": "cadre.ob.circularprogress", "name": "circularprogress", "title": "Circular Progress",
     "palette": "Circular progress: a ring that fills with a value, or spins while the wait has no end, display only",
     "size": {"width": 48, "height": 48}, "exclude": []},
    {"tag": "obc-instrument-radial", "type": "cadre.ob.instrumentradial", "name": "instrumentradial", "title": "Radial Instrument",
     "palette": "Radial instrument: a dial with a needle or filled arc, scale, advice zones and setpoint marker, display only",
     "size": {"width": 240, "height": 240}, "exclude": [], "data": {"advices": "radialadvices"}},
    # `valueSize` and `dataQuality` are nullable enumerations (undefined derives the size from `size`, or states the data fully
    # trusted), and `alert` is a flag or a frame configuration object: none is a property the contract carries.
    {"tag": "obc-readout-block", "type": "cadre.ob.readoutblock", "name": "readoutblock", "title": "Readout Block",
     "palette": "Readout block: a number or text with a value, setpoint or advice marker, display only",
     "size": {"width": 144, "height": 64}, "exclude": ["valueSize", "dataQuality", "alert"]},
    # batch F1 (T2): the frame's leaf components. They are module-only kinds listed in `screen.FRAME_ONLY`; their events are
    # carried and not wired (the frame option wires them), and their slotted children are slot properties (`slots`).
    {"tag": "obc-tooltip", "type": "cadre.ob.tooltip", "name": "tooltip", "title": "Tooltip",
     "palette": "Tooltip: a short label or an icon in a bubble with an arrow, in one of seven variants",
     "size": {"width": 224, "height": 40}, "exclude": [], "slots": [{"slot": "icon", "kind": "icon"}]},
    {"tag": "obc-toggletip", "type": "cadre.ob.toggletip", "name": "toggletip", "title": "Toggletip",
     "palette": "Toggletip: a title, description and optional text content and two actions in a bubble",
     "size": {"width": 320, "height": 232}, "exclude": [], "types": {"variant": "ToggletipVariant"},
     "undefinedWhenEmpty": ["description"], "events": ["primary-action", "secondary-action"],
     "slots": [{"slot": "leading-icon", "kind": "icon"}, {"slot": "trailing-icon", "kind": "icon"},
               {"slot": "content", "kind": "text"}],
     "describe": {"hasContent": "Whether the toggletip draws the `content` text below the description.",
                  "customWidth": "The width of the toggletip in px; unset sizes it to its content."}},
    {"tag": "obc-clock", "type": "cadre.ob.clock", "name": "clock", "title": "Clock",
     "palette": "Clock: the time of day with optional seconds, date, weekday, year and time zone",
     "size": {"width": 208, "height": 64}, "exclude": [], "properties": ["isClickable"],
     "describe": {"date": "The time to draw, an ISO 8601 string in UTC (for example 2026-01-01T09:30:00Z), which the page "
                          "binds to the current time. The clock does not tick by itself; empty draws NaN."}},
    {"tag": "obc-user-button", "type": "cadre.ob.userbutton", "name": "userbutton", "title": "User Button",
     "palette": "User button: a round button with a user icon or initials and an optional label and sublabel",
     "size": {"width": 128, "height": 136}, "exclude": [], "dts": "components/user-button/user-button.d.ts",
     "undefinedWhenEmpty": ["label", "sublabel"], "slots": [{"slot": "icon", "kind": "icon"}]},
    {"tag": "obc-app-button", "type": "cadre.ob.appbutton", "name": "appbutton", "title": "App Button",
     "palette": "App button: an icon above a label, as in the application menu",
     "size": {"width": 96, "height": 96}, "exclude": [], "types": {"size": "AppButtonSize"}, "events": ["click"],
     "properties": ["showLabel"], "slots": [{"slot": "icon", "kind": "icon"}],
     "eventText": {"click": "The app button was pressed. The event carries nothing; the page's script decides what it opens."}},
    {"tag": "obc-notification-button", "type": "cadre.ob.notificationbutton", "name": "notificationbutton",
     "title": "Notification Button",
     "palette": "Notification button: a bell, flat or filled, with an optional count",
     "size": {"width": 64, "height": 64}, "exclude": [], "events": ["obc-click"], "slots": [{"slot": "icon", "kind": "icon"}]},
    {"tag": "obc-notification-badge-button", "type": "cadre.ob.notificationbadgebutton", "name": "notificationbadgebutton",
     "title": "Notification Badge Button",
     "palette": "Notification badge button: a small button with a short text or an icon, used for counts",
     "size": {"width": 80, "height": 48}, "exclude": [], "events": ["click"],
     "slots": [{"slot": "", "kind": "text", "property": "label"}, {"slot": "", "kind": "icon"}],
     "eventText": {"click": "The badge button was pressed. The event carries nothing."}},
    # batch F2 (T2): the alert button and the alert menu, each child before its parent. The silence control is hidden by default
    # (owner's answer 4 of cloud/FRAME-DESIGN.md): no Cadre function silences an alarm, so `showSilenceButton` is false.
    {"tag": "obc-alert-button-item", "type": "cadre.ob.alertbuttonitem", "name": "alertbuttonitem", "title": "Alert Button Item",
     "palette": "Alert button item: one bell with an alert type and a count, as the alert button draws it",
     "size": {"width": 96, "height": 64}, "exclude": [], "events": ["click"], "undefinedWhenEmpty": ["alertType"],
     "describe": {"alertType": ALERT_TYPE_TEXT},
     "eventText": {"click": "The bell was pressed. The event carries nothing; the page's script decides what it opens."}},
    {"tag": "obc-alert-button", "type": "cadre.ob.alertbutton", "name": "alertbutton", "title": "Alert Button",
     "palette": "Alert button: a bell with the count of alerts and an alert type, with an optional silence control",
     "size": {"width": 160, "height": 64}, "exclude": [], "events": ["click-alert", "click-silence"],
     "undefinedWhenEmpty": ["alertType"], "types": {"type": "ObcAlertButtonType"},
     "describe": {"alertType": ALERT_TYPE_TEXT,
                  "showSilenceButton": "Whether the silence control is drawn beside the bell. False by default: no Cadre function "
                                       "silences an alarm, so the control stays hidden until one exists."}},
    {"tag": "obc-alert-menu-item", "type": "cadre.ob.alertmenuitem", "name": "alertmenuitem", "title": "Alert Menu Item",
     "palette": "Alert menu item: one alert row with a title, description, date, time and an ACK action",
     "size": {"width": 360, "height": 72}, "exclude": [], "events": ["item-click", "ack-click", "ack-secondary-click"],
     "eventKinds": {"ack-click": "none"}, "types": {"status": "ObcAlertMenuItemStatus"},
     "slots": [{"slot": "icon", "kind": "icon"}],
     "items": {"alertIcon": {"tags": ["obc-alert-icon"], "slot": "alert-icon",
                             "describe": "The alert icon at the start of the row, one `obc-alert-icon`"}},
     "eventText": {"ack-click": "The ACK action of the row was pressed. The event carries nothing."}},
    {"tag": "obc-alert-menu", "type": "cadre.ob.alertmenu", "name": "alertmenu", "title": "Alert Menu",
     "palette": "Alert menu: tabs of alert rows with ACK visible, Silence and an Alerts button",
     "size": {"width": 640, "height": 560}, "exclude": [],
     "events": ["ack-all-visible-click", "silence-click", "go-to-alert-list-click", "item-click", "ack-click", "ack-secondary-click"],
     "itemEvents": ["item-click", "ack-click", "ack-secondary-click"],
     "eventKinds": {"ack-all-visible-click": "menuvisible", "ack-click": "item", "item-click": "item", "ack-secondary-click": "item"},
     "properties": ["showSilenceButton", "showAlertListButton"],
     "items": {"items": {"tags": ["obc-alert-menu-item"], "slot": "",
                         "describe": "The alert rows of the menu, one `obc-alert-menu-item` for each"}},
     "describe": {"showSilenceButton": "Whether the menu draws its Silence button. False by default: no Cadre function silences an "
                                       "alarm, so the button stays hidden until one exists (the element's own default is true).",
                  "showAlertListButton": "Whether the menu draws its Alerts button, which asks for the page of the full alert list."},
     "eventText": {
         "ack-all-visible-click": "The ACK visible button was pressed. event.mode is the tab (unacked, all or shelved); event.ids "
                                  "holds the `id` of each visible row that has one.",
         "item-click": "A row was pressed. event.id is the row's `id` (empty if it has none) and event.tag its tag.",
         "ack-click": "The ACK action of a row was pressed. event.id is the row's `id` (empty if it has none) and event.tag its tag.",
         "ack-secondary-click": "The secondary action of a row was pressed. event.id is the row's `id` and event.tag its tag."}},
    # batch F3 (T2): navigation, tree navigation and the breadcrumb, each child before its parent. `treeBranches` and `branches` are
    # the container's (the navigation menu in the tree variant and the tree navigation compute them), so they are excluded. The
    # navigation menu's `logo` slot is not carried.
    {"tag": "obc-navigation-item", "type": "cadre.ob.navigationitem", "name": "navigationitem", "title": "Navigation Item",
     "palette": "Navigation item: one row of the navigation menu, with a label, a checked state and optional icons",
     "size": {"width": 280, "height": 48}, "exclude": ["treeBranches"], "events": ["click"], "undefinedWhenEmpty": ["href"],
     "types": {"variant": "ObcNavigationMenuVariant"}, "enums": {"terminalType": "TreeTerminalType"},
     "slots": [{"slot": "icon", "kind": "icon"}, {"slot": "trailing-icon", "kind": "icon"}],
     "eventText": {"click": "The item was pressed. The event carries nothing; the page's script decides where it goes."}},
    {"tag": "obc-navigation-item-group", "type": "cadre.ob.navigationitemgroup", "name": "navigationitemgroup",
     "title": "Navigation Item Group",
     "palette": "Navigation item group: a row that opens a flyout of navigation items and groups",
     "size": {"width": 280, "height": 48}, "exclude": ["treeBranches"], "events": ["open"], "undefinedWhenEmpty": ["href"],
     "types": {"variant": "ObcNavigationMenuVariant"}, "enums": {"terminalType": "TreeTerminalType"},
     "slots": [{"slot": "icon", "kind": "icon"}],
     "items": {"items": {"tags": ["obc-navigation-item", "obc-navigation-item-group"], "slot": "",
                         "describe": "The rows of the flyout, navigation items and groups (a group holds more, to any depth)"}},
     "eventText": {"open": "The group was opened. The event carries nothing."}},
    {"tag": "obc-navigation-menu", "type": "cadre.ob.navigationmenu", "name": "navigationmenu", "title": "Navigation Menu",
     "palette": "Navigation menu: main and footer items and groups, in the full, compact, icon only or tree variant",
     "size": {"width": 320, "height": 480}, "exclude": [],
     "events": ["click", "open"], "itemEvents": ["click", "open"], "eventKinds": {"click": "item", "open": "item"},
     "eventNames": {"click": "onItemClick", "open": "onGroupOpen"},
     "items": {"items": {"tags": ["obc-navigation-item", "obc-navigation-item-group"], "slot": "main",
                         "describe": "The items and groups of the `main` slot (a group holds more, to any depth)"},
               "footerItems": {"tags": ["obc-navigation-item", "obc-navigation-item-group"], "slot": "footer",
                               "describe": "The items and groups of the `footer` slot (settings, help)"}},
     "eventText": {"click": "A navigation item was pressed (at any depth). event.id is the item's `id` (empty if it has none) and event.tag "
                            "its tag.",
                   "open": "A group was opened (at any depth). event.id is the group's `id` (empty if it has none) and event.tag its tag."}},
    {"tag": "obc-tree-navigation-item", "type": "cadre.ob.treenavigationitem", "name": "treenavigationitem",
     "title": "Tree Navigation Item",
     "palette": "Tree navigation item: one row of a tree, with an optional chevron, icon and alert badges",
     "size": {"width": 280, "height": 48}, "exclude": ["branches"], "events": ["click", "expand-toggle"], "customEvents": ["click"],
     "undefinedWhenEmpty": ["href"], "enums": {"terminalType": "TreeTerminalType"}, "properties": ["hasLeadingIcon"],
     "slots": [{"slot": "icon", "kind": "icon"}],
     "eventText": {"click": "The row was pressed and was neither disabled nor already checked. The event carries nothing; the page's "
                            "script decides where it goes."}},
    {"tag": "obc-tree-navigation-group", "type": "cadre.ob.treenavigationgroup", "name": "treenavigationgroup",
     "title": "Tree Navigation Group",
     "palette": "Tree navigation group: a tree row that discloses child rows",
     "size": {"width": 280, "height": 240}, "exclude": ["branches"], "events": ["expand-toggle"],
     "undefinedWhenEmpty": ["href"], "enums": {"terminalType": "TreeTerminalType"}, "properties": ["hasIcon"],
     "slots": [{"slot": "icon", "kind": "icon"}],
     "items": {"items": {"tags": ["obc-tree-navigation-item", "obc-tree-navigation-group"], "slot": "",
                         "describe": "The child rows of the group, tree items and groups (a group holds more, to any depth)"}},
     "eventText": {"expand-toggle": "The header asks to open or close the group. event.expanded is the state the press asks for; the "
                                    "group applies it itself."}},
    {"tag": "obc-tree-navigation", "type": "cadre.ob.treenavigation", "name": "treenavigation", "title": "Tree Navigation",
     "palette": "Tree navigation: groups and items nested to any depth, with guide lines and alert badges for each row",
     "size": {"width": 320, "height": 240}, "exclude": [],
     "events": ["click", "expand-toggle"], "itemEvents": ["click", "expand-toggle"], "customEvents": ["click"],
     "eventKinds": {"click": "item", "expand-toggle": "itemexpanded"}, "eventNames": {"click": "onItemClick"},
     "items": {"items": {"tags": ["obc-tree-navigation-group", "obc-tree-navigation-item"], "slot": "",
                         "describe": "The rows of the tree, groups and items (a group holds more, to any depth)"}},
     "eventText": {"click": "A row was pressed (at any depth) and was neither disabled nor already checked. event.id is the row's `id` "
                            "(empty if it has none) and event.tag its tag.",
                   "expand-toggle": "A row asks to open or close its children (at any depth). event.id and event.tag name the row; "
                                    "event.expanded is the state the press asks for; the group applies it itself."}},
    {"tag": "obc-breadcrumb", "type": "cadre.ob.breadcrumb", "name": "breadcrumb", "title": "Breadcrumb",
     "palette": "Breadcrumb: the crumbs from the first to the current page",
     "size": {"width": 320, "height": 48}, "exclude": [], "data": {"items": "crumbs"}, "properties": ["iconOnly"],
     "events": ["breadcrumb-click"]},
    # batch F4 (T2): the menus and the top bar. The brilliance menu changes its own palette and brightness on a press, so the events
    # write the component's property back (`writeBack`); the frame wires the palette to the existing theme path (F6). The link switches
    # keep their own state, and are hidden by default as the element has them.
    {"tag": "obc-brilliance-menu", "type": "cadre.ob.brilliancemenu", "name": "brilliancemenu", "title": "Brilliance Menu",
     "palette": "Brilliance menu: the palette (night, dusk, day, bright) and the brightness, in the normal, compact or tabbed variant",
     "size": {"width": 320, "height": 460}, "exclude": [], "properties": ["showBrightness", "showPalette"],
     "types": {"variant": "ObcBrillianceMenuVariant", "brightnessInputVariant": "ObcBrillianceInputVariant"},
     "events": ["palette-changed", "brightness-changed", "link-palette-changed", "link-brightness-changed", "screen-control-link-clicked"],
     "eventFields": {"palette-changed": [("value", "string", "The palette chosen: night, dusk, day or bright.")],
                     "brightness-changed": [("value", "number", "The new brightness, from 0 to `brightnessMax`.")],
                     "link-palette-changed": [("value", "boolean", "The state of the link palette switch.")],
                     "link-brightness-changed": [("value", "boolean", "The state of the link brightness switch.")]},
     "writeBack": {"palette-changed": ("palette", "value"), "brightness-changed": ("brightness", "value")},
     "eventText": {"palette-changed": "A palette was chosen. event.value is the palette: night, dusk, day or bright. The menu shows the "
                                      "palette at once and the component's `palette` follows the press; the page's script sets the "
                                      "Cadre palette.",
                   "brightness-changed": "The brightness was changed. event.value is the new brightness. The component's `brightness` "
                                         "follows the press; Cadre has no brightness function, so the frame hides the section."},
     "describe": {"showLinkPalette": "Whether the menu draws the switch that links the palette to other screens. False by default: Cadre "
                                     "links nothing.",
                  "showLinkBrightness": "Whether the menu draws the switch that links the brightness to other screens. False by "
                                        "default: Cadre links nothing."}},
    # The user menu shows who is signed in with a Sign out button, or a Sign in button. The gateway's own login does the signing in
    # (GF-44), so no credential is ever a property: the user name, the password and their errors are excluded, the two fields that
    # draw the input boxes are fixed off (`fixed`: the form is the title and the Sign in button), and the event of the Sign in button
    # carries nothing (the element's detail holds the typed values, and the wrapper does not read it). The list of recent users and the
    # signed in actions (with the primary action and the icon slots of the actions) are not carried: Cadre has none.
    {"tag": "obc-user-menu", "type": "cadre.ob.usermenu", "name": "usermenu", "title": "User Menu",
     "palette": "User menu: the signed in user with a Sign out button, or a Sign in button; no credential is carried",
     "size": {"width": 320, "height": 280},
     "exclude": ["username", "password", "usernameError", "passwordError", "hasRecentlySignedIn", "primaryActionId"],
     "fixed": {"showUsername": False, "showPassword": False}, "undefinedWhenEmpty": ["userInitials", "userLabel", "userRole"],
     "events": ["sign-in-click", "sign-out-click", "use-another-account-click"]},
    # The system menu is display only here: Wi-Fi, audio, microphone and battery are not process state, so its fifteen events are
    # carried and nothing is wired. The four state objects are the menu's sections (a section is drawn only while its object is
    # set). Not carried: the `battery-status` slot (free content; the menu falls back to its own text), and the literal event
    # `eventName` that the manifest lists, which is the parameter name of a private helper of the element (`dispatchClickEvent`) and
    # not an event the element fires. With `externalControl` false the menu opens its sub menus itself, and the press of a heading
    # writes the component's `activeSubMenu` back from the element (the event has no detail), so that an update does not close the sub menu.
    {"tag": "obc-system-menu", "type": "cadre.ob.systemmenu", "name": "systemmenu", "title": "System Menu",
     "palette": "System menu: the Wi-Fi, audio, microphone and battery sections with their sub menus, display only",
     "size": {"width": 320, "height": 480}, "exclude": [], "objects": ["wifiState", "audioState", "microphoneState", "batteryState"],
     "writeBack": {"to-sub-menu-click": ("activeSubMenu", "@element")},      # the menu opens its sub menu itself (no detail): keep it open
     "events": ["wifi-click", "audio-click", "audio-volume-change", "microphone-click", "push-to-talk-change", "battery-saving-mode-change",
                "battery-usage-click", "wifi-network-change", "audio-output-change", "microphone-input-change", "battery-mode-change",
                "settings-click", "to-sub-menu-click", "wifi-options-click", "wifi-disconnect-click"],
     "eventFields": {
         "wifi-click": [("enabled", "boolean", "The state the Wi-Fi switch asks for.")],
         "audio-click": [("muted", "boolean", "The state the audio mute button asks for.")],
         "audio-volume-change": [("volume", "number", "The new volume.")],
         "microphone-click": [("muted", "boolean", "The state the microphone mute button asks for.")],
         "push-to-talk-change": [("pushToTalk", "boolean", "The state of the push to talk switch.")],
         "battery-saving-mode-change": [("batterySavingMode", "boolean", "The state of the battery saving mode switch.")],
         "battery-usage-click": [("usage", "boolean", "True: the usage button was pressed.")],
         "wifi-network-change": [("network", "string", "The name of the network chosen.")],
         "audio-output-change": [("output", "string", "The name of the output chosen.")],
         "microphone-input-change": [("input", "string", "The name of the input chosen.")],
         "battery-mode-change": [("mode", "string", "The name of the mode chosen.")]}},
    # The app menu holds its app buttons as `items` (an `obc-app-button` with an `obi-` icon child in the slot `icon`). A press of a
    # button is the button's own `click`, which bubbles; the menu reports the button's `id` and tag, and the search field its text.
    {"tag": "obc-app-menu", "type": "cadre.ob.appmenu", "name": "appmenu", "title": "App Menu",
     "palette": "App menu: a search field above a grid of app buttons",
     "size": {"width": 360, "height": 280}, "exclude": [], "events": ["search", "click"], "itemEvents": ["click"],
     "eventKinds": {"click": "item"}, "eventNames": {"click": "onAppClick"},
     "eventFields": {"search": [("query", "string", "The text now in the search field.")]},
     "items": {"items": {"tags": ["obc-app-button"], "slot": "",
                         "describe": "The app buttons of the menu, one `obc-app-button` for each"}},
     "eventText": {"click": "An app button was pressed. event.id is the button's `id` (empty if it has none) and event.tag its tag."}},
    # The command menu shows who has command (the status, description and location texts and the command icon) and a switch that takes
    # or releases it. The switch changes the menu's own state, so the event writes the component's `inCommand` back; the frame does not
    # use the switch to command anything (a command stays the Confirm row), and the menu writes no tag. The nine slots are text or
    # icon properties. The element's `toogle-` slot names carry the typo of the pinned release; the properties are spelled correctly.
    {"tag": "obc-command-menu", "type": "cadre.ob.commandmenu", "name": "commandmenu", "title": "Command Menu",
     "palette": "Command menu: the command status, its description and location, and a switch that takes or releases command",
     "size": {"width": 360, "height": 260}, "exclude": [], "properties": ["showLocation"], "events": ["change"],
     "eventNames": {"change": "onCommandChange"},
     "eventFields": {"change": [("inCommand", "boolean", "The state the switch asks for: true takes command, false releases it.")]},
     "writeBack": {"change": ("inCommand", "inCommand")},
     "eventText": {"change": "The command switch was pressed. event.inCommand is the state the press asks for. The menu shows it at once "
                             "and the component's `inCommand` follows the press; the menu writes no tag."},
     "slots": [{"slot": "command-icon", "kind": "icon"}, {"slot": "command-status", "kind": "text"},
               {"slot": "command-description", "kind": "text"}, {"slot": "command-location", "kind": "text"},
               {"slot": "toogle-action-to-in-command-label", "kind": "text", "property": "takeCommandLabel"},
               {"slot": "toogle-action-to-no-command-label", "kind": "text", "property": "releaseCommandLabel"},
               {"slot": "toogle-state-in-command-label", "kind": "text", "property": "inCommandLabel"},
               {"slot": "toogle-state-no-command-label", "kind": "text", "property": "noCommandLabel"},
               {"slot": "toogle-state-in-command-icon", "kind": "icon", "property": "inCommandIconName"}]},
    # The top bar is a composite: it renders an `obc-alert-button` in its `alerts` slot and an `obc-clock` in its `clock` slot itself
    # (`parts`), carrying their properties and the alert button's two events. The count is shown by default (`counter`), the silence
    # control is hidden (owner's answer 4), and the clock is a plain block (`isClickable` false: it has no event). The `app-icon`
    # and `command-button` slots are an icon and a text property. The element's own `showDate` is not used by the element (the clock
    # is slotted), so it is not carried. The breadcrumb is drawn only in the settings mode, where `breadcrumbItems` (label and href)
    # and the events `back`, `close` and `breadcrumb-click` apply; the frame keeps its own crumb row and does not use that mode.
    {"tag": "obc-top-bar", "type": "cadre.ob.topbar", "name": "topbar", "title": "Top Bar",
     "palette": "Top bar: menu button, application and page name, alert button, clock and the dimming, user and apps buttons",
     "size": {"width": 960, "height": 48}, "exclude": ["showDate"], "types": {"menuButtonIcon": "ObcTopBarMenuButtonIcon"},
     "data": {"breadcrumbItems": "crumbs"},
     "events": ["menu-button-clicked", "dimming-button-clicked", "apps-button-clicked", "left-more-button-clicked", "user-button-clicked",
                "emergency-brightness-start", "emergency-brightness-stop", "click-alert", "click-silence", "back", "close", "breadcrumb-click"],
     "parts": [{"tag": "obc-alert-button", "slot": "alerts", "fields": ["nAlerts", "counter", "alertType", "blinking", "showSilenceButton"],
                "events": ["click-alert", "click-silence"], "defaults": {"counter": True}},
               {"tag": "obc-clock", "slot": "clock", "fields": ["date", "showSeconds", "timeZoneOffsetHours"],
                "fixed": {"isClickable": False}}],
     "slots": [{"slot": "app-icon", "kind": "icon"}, {"slot": "command-button", "kind": "text", "property": "commandButtonText"}],
     "describe": {"showClock": "Whether the bar draws its clock (the `date`, `showSeconds` and `timeZoneOffsetHours` below).",
                  "showAppIcon": "Whether the bar draws the app icon (`appIconName`) before the application title.",
                  "settings": "The settings mode: Close and Back buttons, the application title and the breadcrumb (`breadcrumbItems`) in place "
                              "of the menu button and the page name. The frame does not use it.",
                  "breadcrumbItems": "The crumbs of the settings mode, one object each: `label` and `href`. A crumb's icon (a template "
                                     "function) is not carried. Drawn only while `settings` is true; the frame keeps its own crumb row."}},
    # batch F5 (T2): tabs, pivots, the modal window, the context menu input and the notification items, each child before its parent.
    # The tab item draws its title from `title` (the `title` slot is not carried: it would repeat the attribute), a leading icon and a
    # badge icon as icon slot properties. Not carried: the unused `icon` attribute (the element never reads it) and the `badges` list
    # (an object list whose entries name icon slots). The tab row builds its own items from `tabs`.
    {"tag": "obc-tab-item", "type": "cadre.ob.tabitem", "name": "tabitem", "title": "Tab Item",
     "palette": "Tab item: one tab with a title, an optional subtitle, leading icon, badge and close button",
     "size": {"width": 200, "height": 48}, "exclude": ["icon"], "events": ["tab-click", "tab-close"],
     "enums": {"badgeType": "BadgeType", "badgeSize": "BadgeSize"},
     "eventFields": {"tab-click": [("title", "string", "The title of the tab.")], "tab-close": [("title", "string", "The title of the tab.")]},
     "slots": [{"slot": "leading-icon", "kind": "icon"}, {"slot": "badge-icon", "kind": "icon"}],
     "describe": {"hasTitle": "Whether the tab draws its title (and subtitle). The tab row always sets it.",
                  "badgeType": "The type of the badge drawn while `hasBadge` is true.",
                  "badgeCount": "The number in the badge while `hasBadge` is true."}},
    # The tab row builds its tabs from `tabs` (the element's own array attribute, TabData[]), not from child elements. The leading icon of
    # a tab is the module's `iconName` of the tab object (an `obi-` element in the row's slot `tab-<id>-icon`, built by the wrapper).
    # The row selects a pressed tab itself and removes a closed tab from its own list, so the events write the component's
    # `selectedTabId` back (the closed tab stays in the component's `tabs` until the page drops it). Not carried: the `badges` list of a
    # tab and the per tab badge icon slots.
    {"tag": "obc-tab-row", "type": "cadre.ob.tabrow", "name": "tabrow", "title": "Tab Row",
     "palette": "Tab row: a row of tabs built from a list, with a selected tab, optional close buttons and an add button",
     "size": {"width": 480, "height": 48}, "exclude": [], "data": {"tabs": "tabs"}, "tabIcons": True,
     "events": ["tab-selected", "tab-closed", "add-new-tab"],
     "eventFields": {"tab-selected": [("id", "string", "The `id` of the tab that was pressed."),
                                      ("index", "number", "The position of the tab in `tabs`, from 0."),
                                      ("title", "string", "The title of the tab.", "tab.title")],
                     "tab-closed": [("id", "string", "The `id` of the tab whose close button was pressed."),
                                    ("index", "number", "The position the tab had in `tabs`, from 0."),
                                    ("title", "string", "The title of the tab.", "tab.title")]},
     "writeBack": {"tab-selected": ("selectedTabId", "id"), "tab-closed": ("selectedTabId", "@element")},
     "eventText": {"tab-selected": "A tab was pressed. event.id, event.index and event.title name the tab. The row shows it selected at once "
                                   "and the component's `selectedTabId` follows the press.",
                   "tab-closed": "The close button of a tab was pressed. event.id, event.index and event.title name the tab. The row "
                                 "removes the tab from its own list and selects a neighbour if it was selected; the component's "
                                 "`selectedTabId` follows, and its `tabs` list keeps the tab until the page drops it."},
     "describe": {"selectedTabId": "The `id` of the selected tab."}},
    # The pivot item is selected by its group (the group sets `selected` and `direction` on the items it holds), so a standalone item
    # only reports a press of an enabled item that is not selected; the page sets `selected`. Its leading icon is an icon slot property.
    {"tag": "obc-pivot-item", "type": "cadre.ob.pivotitem", "name": "pivotitem", "title": "Pivot Item",
     "palette": "Pivot item: one pivot with an optional icon and label, selected by its group",
     "size": {"width": 128, "height": 48}, "exclude": [], "types": {"direction": "ObcPivotItemDirection"}, "events": ["selected"],
     "eventFields": {"selected": [("value", "string", "The `value` of the pivot.")]},
     "slots": [{"slot": "icon", "kind": "icon"}],
     "eventText": {"selected": "The pivot was pressed while enabled and not selected. event.value is the `value` of the pivot. The pivot "
                               "does not select itself; the page sets `selected`."}},
    # The pivot group holds its pivots as `items`. It selects the pressed pivot itself (it sets `selected` on its children), so `change`
    # writes the component's `selectedValue` back; the wrapper asks the group to mark its children after the list is built.
    {"tag": "obc-pivot-item-group", "type": "cadre.ob.pivotitemgroup", "name": "pivotitemgroup", "title": "Pivot Item Group",
     "palette": "Pivot item group: a horizontal or vertical set of pivots, one of them selected",
     "size": {"width": 240, "height": 144}, "exclude": [], "events": ["change"],
     "eventFields": {"change": [("selectedValue", "string", "The `value` of the selected pivot (empty if the selection was removed).")]},
     "writeBack": {"change": ("selectedValue", "selectedValue")},
     "eventText": {"change": "A pivot was pressed. event.selectedValue is its `value` (empty when `allowDeselect` and the selected pivot was "
                             "pressed). The group shows the selection at once and the component's `selectedValue` follows the press."},
     "items": {"items": {"tags": ["obc-pivot-item"], "slot": "",
                         "describe": "The pivots of the group, one `obc-pivot-item` for each (a pivot's icon is an `obi-` child in the slot `icon`)"}}},
    # The modal window carries its title and its labels as text, its leading icon as an icon and its four buttons as events. Its `content`
    # slot takes arbitrary content, which a Perspective component cannot hold (the module has no container), so `content` is a text
    # property and the window is not used for commands: the command dialogue of the library stays the Confirm row (wiki 12 section 17.27).
    # The window is a plain block of the box it is given and draws no scrim or overlay of its own.
    {"tag": "obc-modal-window", "type": "cadre.ob.modalwindow", "name": "modalwindow", "title": "Modal Window",
     "palette": "Modal window: a title, a text content and Close, Cancel, Done and optional action buttons",
     "size": {"width": 540, "height": 240}, "exclude": [], "types": {"size": "ObcModalWindowSize"},
     "properties": ["hasCancelAction", "hasCloseAction"],
     "events": ["close-click", "cancel-click", "done-click", "option-click"],
     "slots": [{"slot": "leading-icon", "kind": "icon"}, {"slot": "title", "kind": "text"}, {"slot": "content", "kind": "text"},
               {"slot": "option-label", "kind": "text", "property": "optionLabel"},
               {"slot": "cancel-label", "kind": "text", "property": "cancelLabel"},
               {"slot": "done-label", "kind": "text", "property": "doneLabel"}],
     "describe": {"content": "The text in the content area; empty leaves it blank. The element's `content` slot takes any content, which "
                             "the module cannot hold, so only text is carried.",
                  "optionLabel": "The label of the optional action button, drawn while `hasOptionalAction` is true; empty keeps the "
                                 "element's own word, Option.",
                  "cancelLabel": "The label of the Cancel button, drawn while `hasCancelAction` is true; empty keeps the element's own "
                                 "word, Cancel.",
                  "doneLabel": "The label of the Done button; empty keeps the element's own word, Done.",
                  "title": "The title of the window; empty keeps the element's own word, Title."}},
    # The context menu input takes its `options`, `columnGroups` and `selectedValues` as array attributes (data, no child elements). An
    # option's icon is a template function in the element and is not carried, as is the element's default slot (custom option icons).
    # `multiSelect` and `selectPerGroup` are tri-state in the element (unset: it decides from `type`), so they are empty by default and
    # the element's own rule applies. The element selects an option itself, so `change` writes the component's `selectedValues` back.
    {"tag": "obc-context-menu-input", "type": "cadre.ob.contextmenuinput", "name": "contextmenuinput", "title": "Context Menu Input",
     "palette": "Context menu input: a list of options, with checkboxes, nested groups or columns, and an optional title bar",
     "size": {"width": 480, "height": 240}, "exclude": [],
     "data": {"options": "menuoptions", "columnGroups": "columngroups", "selectedValues": "strings"},
     "undefinedWhenEmpty": ["multiSelect", "selectPerGroup"], "events": ["close", "item-click", "change"],
     "eventKinds": {"item-click": "detail"},
     "eventFields": {"item-click": [("value", "string", "The `value` of the option that was pressed."),
                                    ("label", "string", "The `label` of the option that was pressed.", "option.label")],
                     "change": [("selectedValues", "array", "The `value` of each option now selected, in order.")]},
     "writeBack": {"change": ("selectedValues", "selectedValues")},
     "eventText": {"close": "The menu asks to close (the Escape key, or the close button of the title bar). The event carries nothing.",
                   "item-click": "An option was pressed (also an option that opens a flyout). event.value and event.label name it.",
                   "change": "The selection changed. event.selectedValues holds the `value` of each option now selected. The menu shows "
                             "the selection at once and the component's `selectedValues` follows."},
     "describe": {"multiSelect": "Whether several options can be selected. Empty leaves the choice to `type` (the checkbox and multi "
                                 "types select several).",
                  "selectPerGroup": "Whether one option is selected for each group or column. Empty leaves the choice to `type` "
                                    "(the flyout type selects one for each group).",
                  "title": "The title of the title bar, drawn while `hasTitleBar` is true."}},
    # The notification items (batch F5) are display rows of a notification list; no Cadre frame part uses them and no event writes a tag.
    # The menu item opens and closes itself on a press, so `item-click` writes the component's `open` back.
    {"tag": "obc-notification-menu-item", "type": "cadre.ob.notificationmenuitem", "name": "notificationmenuitem",
     "title": "Notification Menu Item",
     "palette": "Notification menu item: one notification row with a title, description, day and time, opened by a press",
     "size": {"width": 360, "height": 112}, "exclude": [], "events": ["item-click", "primary-action-click", "secondary-action-click"],
     "eventKinds": {"item-click": "detail"}, "eventFields": {"item-click": [("open", "boolean", "The state of the row after the press: true opened.")]},
     "writeBack": {"item-click": ("open", "open")},
     "slots": [{"slot": "icon", "kind": "icon"}],
     "eventText": {"item-click": "The row was pressed. event.open is the state of the row after the press. The row opens or closes at once "
                                 "and the component's `open` follows the press.",
                   "primary-action-click": "The primary action of the opened row was pressed. The event carries nothing.",
                   "secondary-action-click": "The secondary action of the opened row was pressed. The event carries nothing."}},
    # The message item draws the row of the top bar's notification list. Its press and its action are separate events. Its three
    # `show...` fields have no attribute (they hide the title, the description and the time); the module carries them at the element's
    # own default (shown).
    {"tag": "obc-notification-message-item", "type": "cadre.ob.notificationmessageitem", "name": "notificationmessageitem",
     "title": "Notification Message Item",
     "palette": "Notification message item: one message with a title, description, time and an optional action",
     "size": {"width": 640, "height": 64}, "exclude": [], "properties": ["showTitle", "showDescription", "showTimestamp"],
     "events": ["message-click", "action-click"], "slots": [{"slot": "secondary-icon", "kind": "icon"}],
     "describe": {"actionLabel": "The text of the action button, drawn by the `with-button` type.",
                  "emptyText": "The text drawn while `empty` is true (or the type is `inactive`).",
                  "timeSecondary": "The second time, drawn while `hasTimestamp2` is true."},
     "eventText": {"message-click": "The message was pressed outside its action. The event carries nothing.",
                   "action-click": "The action button (or the action icon) was pressed. The event carries nothing."}},
    # The floating item is a transient notification (a toast). Its title, description, time, day and the two action labels are text slot
    # properties (`actionLabel` and `action2Label`, because `action` and `action2` are the flags that draw the buttons); its primary icon
    # (drawn only by the `application` type) is an icon property. The item is dismissed by the page, which hides it on `onDismissClick`.
    {"tag": "obc-notification-floating-item", "type": "cadre.ob.notificationfloatingitem", "name": "notificationfloatingitem",
     "title": "Notification Floating Item",
     "palette": "Notification floating item: a transient notification with a title, description, time and up to two actions",
     "size": {"width": 640, "height": 136}, "exclude": [],
     "types": {"type": "ObcFloatingItemType", "direction": "ObcFloatingItemDirection", "lineType": "ObcFloatingItemLineType"},
     "events": ["action-click", "action2-click", "dismiss-click"],
     "slots": [{"slot": "primary-icon", "kind": "icon"}, {"slot": "title", "kind": "text"}, {"slot": "description", "kind": "text"},
               {"slot": "time", "kind": "text"}, {"slot": "day", "kind": "text"},
               {"slot": "action", "kind": "text", "property": "actionLabel"}, {"slot": "action2", "kind": "text", "property": "action2Label"}],
     "describe": {"time": "The time of the notification, drawn while `hasTimestamp` is true.",
                  "day": "The day of the notification, drawn while `hasDay` is true.",
                  "actionLabel": "The label of the primary action button, drawn while `action` is true.",
                  "action2Label": "The label of the secondary action button, drawn while `action2` is true."},
     "eventText": {"action-click": "The primary action was pressed. The event carries nothing.",
                   "action2-click": "The secondary action was pressed. The event carries nothing.",
                   "dismiss-click": "The dismiss button was pressed. The event carries nothing; the page's script hides the item."}},
    {"tag": "obc-horizontal-line", "type": "cadre.ob.pipehorizontal", "name": "pipehorizontal", "title": "Pipe, horizontal",
     "palette": "Horizontal line: a pipe, cable or air line drawn left to right over a number of 24 px units, display only",
     "size": {"width": 96, "height": 24}, "exclude": [], "sheet": "linehorizontal"},
    {"tag": "obc-vertical-line", "type": "cadre.ob.pipevertical", "name": "pipevertical", "title": "Pipe, vertical",
     "palette": "Vertical line: a pipe, cable or air line drawn top to bottom over a number of 24 px units, display only",
     "size": {"width": 24, "height": 96}, "exclude": [], "sheet": "linevertical"},
    {"tag": "obc-corner-line", "type": "cadre.ob.pipecorner", "name": "pipecorner", "title": "Pipe, corner",
     "palette": "Corner line: a pipe bend joining two sides of its box, display only",
     "size": {"width": 24, "height": 24}, "exclude": [], "sheet": "linejunction"},
    {"tag": "obc-three-way-line", "type": "cadre.ob.pipetee", "name": "pipetee", "title": "Pipe, tee",
     "palette": "Three-way line: a pipe tee with a run and one branch, display only",
     "size": {"width": 24, "height": 24}, "exclude": [], "sheet": "linejunction"},
    {"tag": "obc-line-cross", "type": "cadre.ob.pipecross", "name": "pipecross", "title": "Pipe, four-way junction",
     "palette": "Line cross: four pipe ends joined at the centre of the box, display only",
     "size": {"width": 24, "height": 24}, "exclude": [], "sheet": "linejunction"},
    {"tag": "obc-line-overlap", "type": "cadre.ob.pipeoverlap", "name": "pipeoverlap", "title": "Pipe, crossover",
     "palette": "Line overlap: one pipe passing over another without joining it, display only",
     "size": {"width": 24, "height": 24}, "exclude": [], "sheet": "linejunction", "without": {"lineType": ["connector"]}},
    {"tag": "obc-end-point-line", "type": "cadre.ob.pipeend", "name": "pipeend", "title": "Pipe, end point",
     "palette": "End point line: a pipe that ends in a terminal bar on one side of its box, display only",
     "size": {"width": 24, "height": 24}, "exclude": [], "sheet": "linejunction", "without": {"lineType": ["connector"]}},
    {"tag": "obc-direction-line", "type": "cadre.ob.pipedirection", "name": "pipedirection", "title": "Pipe, flow direction",
     "palette": "Direction line: a pipe segment with a flow direction chevron, display only",
     "size": {"width": 24, "height": 24}, "exclude": [], "sheet": "linejunction", "without": {"lineType": ["connector"]}},
    {"tag": "obc-bus", "type": "cadre.ob.bus", "name": "bus", "title": "Bus",
     "palette": "Bus: a labelled busbar or data bus drawn as a bar, display only",
     "size": {"width": 200, "height": 24}, "exclude": []},
]
# The canvas zoom component is not a package element: a leaf component whose browser side is
# `web/canvaszoom.js`. Its properties are fixed by the Level 4 contract (the stock screens bind `zoom` two ways).
CANVAS_ZOOM = {
    "type": "cadre.ob.canvaszoom", "name": "canvaszoom", "title": "Canvas Zoom",
    "palette": "Canvas zoom: Ctrl+wheel, pinch and Ctrl+plus, minus, 0 scale only the canvas, not the browser page",
    "size": {"width": 1, "height": 1},
    "props": {
        "zoom": {"type": "number", "default": 1, "description":
                 "The canvas scale, written by the component and bound two ways to the view's zoom property."},
        "min": {"type": "number", "default": 0.5, "description": "The smallest zoom."},
        "max": {"type": "number", "default": 4, "description": "The largest zoom."},
        "targetDomId": {"type": "string", "default": "cadre-canvas", "description":
                        "The DOM id of the scrolling canvas the gestures act on (a Perspective component's domId)."},
        "guardBrowserZoom": {"type": "boolean", "default": True, "description":
                             "Prevent the same gestures anywhere else on the document, so the browser never zooms "
                             "the frame; on touch devices the viewport meta gains maximum-scale=1."},
        "viewWidth": {"type": "number", "default": 0, "description":
                      "The target's measured width in px, written by the component when it changes (0 until measured); "
                      "the page's fit reads it, so a docked faceplate or a reload needs no session flag."},
        "viewHeight": {"type": "number", "default": 0, "description":
                       "The target's measured height in px, written by the component when it changes (0 until measured)."},
    },
}
DATA_SCHEMA = {"tabs": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                            "id": {"type": "string"}, "title": {"type": "string"}, "subtitle": {"type": "string"},
                            "showSubtitle": {"type": "boolean"}, "hasLeadingIcon": {"type": "boolean"}, "iconName": {"type": "string"},
                            "hasBadge": {"type": "boolean"}, "badgeCount": {"type": "number"}, "badgeType": {"type": "string"},
                            "badgeSize": {"type": "string"}, "badgeShowNumber": {"type": "boolean"},
                            "showLeadingBadgeIcon": {"type": "boolean"}, "disabled": {"type": "boolean"}},
                            "required": ["id", "title"]},
                        "description": "The tabs, one object each: `id` (unique; the events report it), `title`, `subtitle`, `showSubtitle`, "
                                       "`hasLeadingIcon`, `iconName` (a bundled icon, in the tab's leading icon slot; "
                                       "the element draws a placeholder icon where a tab has none, so a tab without an icon states "
                                       "`hasLeadingIcon` false), `hasBadge`, `badgeCount`, `badgeType`, `badgeSize`, `badgeShowNumber`, "
                                       "`showLeadingBadgeIcon` and `disabled`. The element's `badges` list is not carried."},
               "menuoptions": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                                   "value": {"type": "string"}, "label": {"type": "string"}, "level": {"type": "number"},
                                   "children": {"type": "array", "items": {"type": "object"}}}, "required": ["value", "label"]},
                               "description": "The options of the menu, one object each: `value` (unique; the events report it), `label`, `level` "
                                              "(the depth of the option, from 0) and `children` (objects of the same form, for the flyout and "
                                              "nested types). An option's icon (a template function in the element) is not carried."},
               "columngroups": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                                    "title": {"type": "string"}, "columns": {"type": "number"},
                                    "options": {"type": "array", "items": {"type": "object"}}}, "required": ["title", "options"]},
                                "description": "The column groups of the multi column types, one object each: `title`, `columns` (the least number "
                                               "of columns the group draws) and `options` (objects with `value` and `label`)."},
               "strings": {"type": "array", "default": [], "items": {"type": "string"},
                           "description": "A list of values as plain text, in order."},
               "crumbs": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                              "label": {"type": "string"}, "href": {"type": "string"}}, "required": ["label"]},
                          "description": "The crumbs from the first to the current page, one object each: `label` and `href`. A crumb's "
                                         "icon (a template function in the element) is not carried. The last crumb is the current page."},
               "alerts": {"type": "array", "default": [], "items": {"type": "object"},
                          "description": "Alert records (package types.d.ts Alert): id, tagId, source, text, note, "
                                         "acknowledged, active, type, time (epoch milliseconds), shelved."},
             "numbers": {"type": "array", "default": [], "items": {"type": "number"},
                         "description": "The samples of a trend graph, oldest first, as plain numbers (the element's `data`)."},
             # Lists of objects, carried as JSON like the alerts (GF-38). A chart draws a list the property tree holds as
             # plain data; the wrapper hands the element a mutable copy (`toRecords`), because Chart.js writes to the
             # arrays it is given. The item schemas are our own wording of the pinned `dist/` declarations.
             "points": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                            "label": {"type": "string"}, "x": {"type": ["number", "string"]}, "value": {"type": "number"}},
                            "required": ["value"]},
                        "description": "A single series, one object per point: `value`, and `label` (a category axis) or `x` "
                                       "(a time axis in epoch milliseconds or an ISO string, or a number axis)."},
             "datasets": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                              "label": {"type": "string"},
                              "data": {"type": "array", "description": "Numbers, or `{x, y}` objects on a time or number axis."},
                              "yAxisID": {"type": "string"}}, "required": ["data"]},
                          "description": "Several series, one object each: `label` and `data` (numbers, or `{x, y}` points on a "
                                         "time or number axis). When the list is not empty it replaces `data`."},
             "yaxes": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                           "id": {"type": "string"}, "position": {"type": "string", "enum": ["left", "right"]},
                           "min": {"type": "number"}, "max": {"type": "number"}, "grid": {"type": "boolean"}}},
                       "description": "The value axes, one object each: `id` (named by a series' `yAxisID`), `position`, "
                                      "`min`, `max` and `grid`. Empty draws the one default axis."},
             "labels": {"type": "array", "default": [], "items": {"type": ["string", "number"]},
                        "description": "The category labels shared by the objects of `datasets`, in order."},
             "colors": {"type": "array", "default": [], "items": {"type": "string"},
                        "description": "Colours of the series or segments in order, as CSS colour strings. Empty uses the "
                                       "palette of the scheme."},
             "rings": {"type": "array", "default": [], "items": {"type": "number"},
                       "description": "The value of each ring, outermost first, as plain numbers on the scale 0 to `max` "
                                      "(the element's `data`)."},
             # Advice zones (C2): the pinned declarations `LinearAdvice` (a bar) and `GaugeRadialAdvice` (the radial instrument)
             "linearadvices": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                                   "min": {"type": "number"}, "max": {"type": "number"},
                                   "type": {"type": "string", "enum": ["advice", "caution"]}, "hinted": {"type": "boolean"}},
                                   "required": ["min", "max", "type"]},
                               "description": "Advice zones on the scale, one object each: `min` and `max` (scale values), `type` "
                                              "(`advice` or `caution`) and `hinted` (drawn faint until the value reaches it)."},
             "radialadvices": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                                   "minValue": {"type": "number"}, "maxValue": {"type": "number"},
                                   "type": {"type": "string", "enum": ["advice", "caution"]}, "hinted": {"type": "boolean"}},
                                   "required": ["minValue", "maxValue", "type"]},
                               "description": "Advice zones on the dial, one object each: `minValue` and `maxValue` (scale values), "
                                              "`type` (`advice` or `caution`) and `hinted` (drawn faint until the value reaches it)."},
             "segments": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                              "label": {"type": "string"}, "value": {"type": "number"}}, "required": ["label", "value"]},
                          "description": "The segments, one object each: `label` and `value`."},
             "piesegments": {"type": "array", "default": [], "items": {"type": "object", "properties": {
                                 "label": {"type": "string"}, "value": {"type": "number"}, "children": {
                                     "type": "array", "items": {"type": "object", "properties": {
                                         "label": {"type": "string"}, "value": {"type": "number"}},
                                         "required": ["label", "value"]}}}, "required": ["label", "value"]},
                             "description": "The segments, one object each: `label`, `value` and, for the sunburst, `children` "
                                            "(objects with `label` and `value`)."}}
# Properties of the module's own, not the element's: the wrapper applies them (`speedless`, `tankSlots` in the
# WRAPPER below). Each lifts a case the element cannot show (COB-110): a device with no speed reads no speed, a
# tank states the unit of its level, and a vessel that states no capacity draws no capacity line.
EXTRA = {
    "hasSpeed": {"kind": "boolean", "def": True, "schema": {"type": "boolean", "default": True, "description":
                 "Whether the element prints a speed while it runs. False leaves the speed readout out (the "
                 "state readout stays); the package element has no such switch."}},
    "showStatus": {"kind": "boolean", "def": True, "schema": {"type": "boolean", "default": True, "description":
                   "Whether the symbol draws its status readouts. False hides every status word, including the "
                   "element's own Off, and the speed readout (the element's showStatus); the tag stays."}},
    "statusText": {"kind": "string", "def": "", "schema": {"type": "string", "default": "", "description":
                   "When not empty, the status word drawn in the element's status place (for example On or Off) "
                   "in place of its own readout; empty keeps the element's own."}},
    "badgeDuty": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
                  "The duty badge on the symbol, in the first free corner (bottom left, bottom right, "
                  "top left, top right); not drawn while the interlock badge, which is the same icon, is."}},
    "outOfService": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
                     "The symbol greyed and marked with the word OOS, as the stock library view draws an out of "
                     "service symbol."}},
    "stretch": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
                "The readout fills its component box (chip and identifier centred in it), so readouts of equal "
                "boxes show equal widths with their values aligned, instead of sizing to the content."}},
    # Row selection of the two alarm lists (module 0.4.2, eng02 ASM Level 5): The package's table has the tick column
    # (an obc-checkbox) itself; the alert list does not switch it on, so the wrapper does (`applySelection`).
    "selectable": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
                   "Whether each row starts with a tick box (the package checkbox) that selects it. A click on the "
                   "tick toggles only the selection; a click elsewhere on the row is the row click as before."}},
    "selectedIds": {"kind": "array", "def": [], "schema": {"type": "array", "default": [], "items": {"type": "string"},
                    "description": "The ids of the selected rows. Written by the component when a tick is toggled "
                                   "(bind it two ways); ticks show the ids in it, and an id of an alert the list no "
                                   "longer shows is dropped."}},
    # The indicator generator draws a disc and nothing else (no state, no readout, no alert attributes), so the
    # wrapper adds them (`generator` in the WRAPPER below): the running state selects the element's `value`
    # scheme, and its identifier, status word and alert frame are drawn from the package's own readout stack and
    # alert frame elements, unchanged, inside the element's shadow root.
    "on": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
           "Whether the generator is running. A generator that runs draws the scheme of `value` (the regular "
           "scheme where `value` is off); one that does not run draws the element's off scheme."}},
    "tag": {"kind": "string", "def": "", "schema": {"type": "string", "default": "", "description":
            "The identifier printed with the symbol; empty prints none."}},
    "readoutPosition": {"kind": "string", "def": "bottom", "schema": {"type": "string", "enum": [
                        "top", "bottom", "left", "right", "none"], "default": "bottom", "description":
                        "The side of the symbol on which the identifier and the status word lie; none draws neither."}},
    "alert": {"kind": "boolean", "def": False, "schema": {"type": "boolean", "default": False, "description":
              "Whether the symbol is framed by the alert frame."}},
    "alertFrameStatus": {"kind": "string", "def": "alarm", "enum": "AlertType", "schema": {
                         "type": "string", "default": "alarm", "description": "Available when alert==true."}},
    "alertFrameMode": {"kind": "string", "def": "acked-active", "enum": "ObcAlertFrameMode", "schema": {
                       "type": "string", "default": "acked-active", "description": "Available when alert==true."}},
    "unit": {"kind": "string", "def": "m³", "schema": {"type": "string", "default": "m³", "description":
             "The unit printed after the capacity, in place of the cubic metres of the pinned package's tank."}},
    "hasCapacity": {"kind": "boolean", "def": True, "schema": {"type": "boolean", "default": True, "description":
                    "Whether a static tank prints its capacity. False draws the vessel and its tag with no "
                    "capacity line, where the pinned package's tank always prints one."}},
}
# Element properties the manifest declares as fields with no attribute (`attribute: false` in the element), which the
# attribute loop of `schema_for` therefore does not see. The wrapper sets them on the element as it sets every field.
# `showStatus` hides the state readout of an automation button (On or Off, the speed, the opening) and keeps the
# identifier: the diagram toolbar's Readout button binds it, as it binds the library view's `showStatus`. The two
# valves take it here (0.3.2); the pump, motor and fan take it as an extra (0.4.0), which `applyStatus` passes on.
PROPERTIES = {
    "showStatus": {"type": "boolean", "default": True, "description":
                   "Whether the element draws its state readout (On or Off, the speed, the opening) beside the "
                   "symbol. The identifier stays. The diagram toolbar's Readout button binds it."},
    # the bars' scale (C2): fields without an attribute, true by default in the element
    "hasScale": {"type": "boolean", "default": True, "description": "Whether the bar draws its scale (tickmarks)."},
    "showLabels": {"type": "boolean", "default": True, "description": "Whether the scale draws its value labels. Needs the scale."},
    # the frame's leaf components (F1): fields without an attribute, true by default in the element
    "isClickable": {"type": "boolean", "default": True, "description":
                    "Whether the clock is a button (draws its pressed and hover states). False draws a plain block."},
    "showLabel": {"type": "boolean", "default": True, "description": "Whether the button draws its label under the icon."},
    # the alert menu (F2): fields without an attribute; the silence button is hidden by default (no Cadre silence function)
    "showSilenceButton": {"type": "boolean", "default": False, "description":
                          "Whether the menu draws its Silence button. False by default; the element's own default is true."},
    "showAlertListButton": {"type": "boolean", "default": True, "description": "Whether the menu draws its Alerts button."},
    # the tree rows (F3): fields without an attribute, at the element's own default
    "hasLeadingIcon": {"type": "boolean", "default": True, "description":
                       "Whether the row reserves and draws the leading icon (the `icon` slot). A row with no icon is drawn without "
                       "the space when this is false."},
    "hasIcon": {"type": "boolean", "default": True, "description":
                "Whether the group header reserves and draws the leading icon (the `icon` slot). A group with no icon is drawn "
                "without the space when this is false."},
    # the menus (F4): fields without an attribute, at the element's own default (true)
    "showBrightness": {"type": "boolean", "default": True, "description": "Whether the menu draws the brightness section."},
    "showPalette": {"type": "boolean", "default": True, "description": "Whether the menu draws the palette (day and night) section."},
    "showLocation": {"type": "boolean", "default": True, "description":
                     "Whether the menu draws the location of the command (the `command-location` text) beside its description."},
    # the modal window and the notification message item (F5): fields without an attribute, at the element's own default (true)
    "hasCancelAction": {"type": "boolean", "default": True, "description": "Whether the window draws its Cancel button (and its label)."},
    "hasCloseAction": {"type": "boolean", "default": True, "description": "Whether the window draws the close button of its title bar."},
    "showTitle": {"type": "boolean", "default": True, "description": "Whether the item draws its title."},
    "showDescription": {"type": "boolean", "default": True, "description": "Whether the item draws its description."},
    "showTimestamp": {"type": "boolean", "default": True, "description": "Whether the item draws its time."},
    "iconOnly": {"type": "boolean", "default": False, "description":
                 "Draws the crumbs before the last as their icon alone. The module carries no crumb icon (a crumb's icon is a "
                 "template function), so a crumb with only an icon is not possible; true hides every label but the last."},
}
# ------------------------------------------------------------------------------- frame mechanisms (T2, batch F1)
# Slotted children of a frame component are carried by three mechanisms, each driven by a key of the component's entry.
#
#   "slots": [{"slot": "icon", "kind": "icon"}, {"slot": "content", "kind": "text"}]
#       a text slot becomes a string property (named after the slot; `text` for the default slot) and an icon slot becomes a
#       string property (named after the slot with `Name` added: `iconName`) whose values are the names of `ICONS_JS`
#       (checked against `dist/icons` of the pinned package). An entry may name its property with "property". The slot must be
#       one the manifest declares for the element.
#   "items": {"items": {"tags": ["obc-pivot-item"], "slot": ""}}
#       a data property (a list of objects) that the wrapper turns into child elements of the host. An object holds `tag`
#       (one of the entry's `tags` at the top level, one of `ITEM_CHILDREN[parent]` below it, or `span` or an icon `obi-<name>`
#       anywhere below), the element's attributes by their field names (checked against the manifest, an unknown one is ignored),
#       `text` (the element's text), `id` (kept as `data-item-id`, which events from the item report), `slot` and `children`.
#   "types": {"size": "AppButtonSize"}
#       the enumeration of an attribute whose manifest type is missing; "undefinedWhenEmpty": ["description"] gives an
#       optional text the value undefined while it is empty (an element that tests `!== undefined` draws an empty block for null).
#
# A tag allowed as an item must be an element of the manifest. `ITEM_CHILDREN` maps an item tag to the item tags it may
# hold; `ITEM_FIELDS` lists fields a tag has with no attribute that an item may set (rows are added by the batch that needs them).
ICONS_JS = HERE / "web/icons.js"
# A navigation group holds navigation items and groups to any depth (ITEM_DEPTH); a tree group holds tree rows. A tree row has a
# leading icon field and a tree group an icon field, neither an attribute (batch F3).
ITEM_CHILDREN: dict[str, list[str]] = {
    "obc-alert-menu-item": ["obc-alert-icon"],
    "obc-navigation-item-group": ["obc-navigation-item", "obc-navigation-item-group"],
    "obc-tree-navigation-group": ["obc-tree-navigation-item", "obc-tree-navigation-group"]}
ITEM_FIELDS: dict[str, list[str]] = {"obc-tree-navigation-item": ["hasLeadingIcon"], "obc-tree-navigation-group": ["hasIcon"],
                                     "obc-app-button": ["showLabel"]}
ITEM_PLAIN = ["span"]          # elements that are not custom elements and may hold text anywhere below a top level item
ITEM_DEPTH = 8                 # the deepest nesting of `children` the wrapper builds


def icon_names() -> list[str]:
    """The icons the module bundles, in the order of `web/icons.js`: each import is checked against `dist/icons` of the pinned
    package and must define `obi-<name>`. This list is the enumeration of every icon slot property."""
    names = re.findall(r"^import '@oicl/openbridge-webcomponents/dist/icons/icon-([a-z0-9-]+)\.js';", ICONS_JS.read_text(encoding="utf-8"), re.M)
    if not names or len(set(names)) != len(names):
        raise SystemExit("web/icons.js lists no icon, or lists one twice")
    for n in names:
        f = PKG / "dist/icons" / f"icon-{n}.js"
        if not f.is_file() or f'customElement("obi-{n}")' not in f.read_text(encoding="utf-8"):
            raise SystemExit(f"icon {n!r} of web/icons.js is not an icon of the pinned package")
    return names


def camel(name: str) -> str:
    head, *rest = name.split("-")
    return head + "".join(w.capitalize() for w in rest)


def slot_specs(spec: dict, decl: dict, own: set[str]) -> list[dict]:
    """The slot properties of a component: for each entry of its `slots`, the slot, the kind (`text` or `icon`) and the
    property name. The slot must be declared by the element, and the name must not be one of the element's own."""
    declared = {s.get("name", "") for s in decl.get("slots", [])}
    out, seen = [], set()
    for e in spec.get("slots", []):
        slot, kind = e["slot"], e["kind"]
        if kind not in ("text", "icon"):
            raise SystemExit(f"{spec['tag']}: slot kind {kind!r} is neither text nor icon")
        if slot not in declared:
            raise SystemExit(f"{spec['tag']} declares no slot {slot!r} in the manifest")
        name = e.get("property") or ((camel(slot) if slot else "icon") + "Name" if kind == "icon" else (camel(slot) if slot else "text"))
        if name in own or name in seen:
            raise SystemExit(f"{spec['tag']}: the slot property {name!r} is already a property; name it with \"property\"")
        seen.add(name)
        about = next((clean(s.get("description")) for s in decl.get("slots", []) if s.get("name", "") == slot), "")
        out.append({"slot": slot, "kind": kind, "name": name, "about": about})
    return out


def slot_schema(sl: dict, icons: list[str]) -> dict:
    where = f"the `{sl['slot']}` slot" if sl["slot"] else "the default slot"
    if sl["kind"] == "icon":
        return {"type": "string", "enum": [""] + icons, "default": "",
                "description": f"The icon in {where}, by name (a bundled icon); empty puts none. {sl['about']}".strip()}
    return {"type": "string", "default": "",
            "description": f"The text in {where}; empty puts none. {sl['about']}".strip()}


def build_item_table(manifest: dict, specs: list[dict]) -> dict:
    """What the wrapper needs of each element an `items` property may build: its attribute field names, and the item tags
    it may hold. The closure of the entries' tags under `ITEM_CHILDREN`; every tag must be an element of the manifest."""
    todo = [t for sp in specs for e in sp.get("items", {}).values() for t in e["tags"]]
    for parent, kids in ITEM_CHILDREN.items():
        todo += [parent, *kids]
    table: dict[str, dict] = {}
    while todo:
        tag = todo.pop()
        if tag in table:
            continue
        decl = declaration(manifest, tag)
        names = [a["fieldName"] for a in decl.get("attributes", []) if a.get("fieldName")]
        fields = {m["name"] for m in decl.get("members", []) if m.get("kind") == "field"}
        for f in ITEM_FIELDS.get(tag, []):
            if f not in fields:
                raise SystemExit(f"{tag} declares no field {f!r} in the manifest")
        table[tag] = {"props": names + [f for f in ITEM_FIELDS.get(tag, []) if f not in names],
                      "kids": list(ITEM_CHILDREN.get(tag, []))}
        todo += table[tag]["kids"]
    return dict(sorted(table.items()))


def items_schema(entry: dict, table: dict) -> dict:
    tags = entry["tags"]
    kinds = "; ".join(f"`{t}` ({', '.join(table[t]['props']) or 'no attribute'})" for t in tags)
    about = entry.get("describe", "The child elements of the component")
    return {"type": "array", "default": [], "items": {"type": "object", "properties": {
                "tag": {"type": "string", "enum": list(tags)}, "id": {"type": "string"}, "slot": {"type": "string"},
                "text": {"type": "string"}, "children": {"type": "array", "items": {"type": "object"}}},
                "required": ["tag"]},
            "description": f"{about}, as a list with one object for each: `tag` and then the element's attributes by name, "
                           f"`text`, `id` (reported by the element's events), `slot` and `children` (objects of the same form). "
                           f"Tags and attributes: {kinds}."}


ITEM_TABLE: dict[str, dict] = {}    # set by `main` before the schemas are written

# Rules added to the shadow root of an element, where the element draws something a process diagram's box
# cannot use as it stands (COB-127). The transmitter is built to hang from a line by a leader line: it
# offsets itself by half its width and 8 px, which puts it beside the box a diagram gives it. The module
# draws it centred in its box with no leader line, as the library's readout is. The instrument field aligns
# its value and its setpoint to the end of the element, and `center` moves only the caption, so the wrapper
# sets `data-center` on the host of a centred symbol and the value and setpoint centre with it.
SHEETS = {
    "readout": ".transmitter { transform: none !important; top: auto !important; right: auto !important; "
               "padding: 0 !important; }\n.transmitter::before { display: none !important; }\n"
               ":host([data-stretch]), :host([data-stretch]) .transmitter, :host([data-stretch]) .content, "
               ":host([data-stretch]) .body { width: 100% !important; }\n"
               ":host([data-stretch]) .chip { display: block; flex: 1 1 auto; width: 100%; }",
    # the chip's own shadow root: its button is as wide as its content unless it is told to fill the chip
    "readoutchip": ":host([data-stretch]) { display: block; width: 100%; }\n"
                   ":host([data-stretch]) .button { display: flex; width: 100%; }\n"
                   ":host([data-stretch]) .visible-wrapper { width: 100%; justify-content: center; }",
    "instrumentfield": ":host([data-center]) .setpoint, :host([data-center]) .value { justify-content: center "
                       "!important; }",
    # The line elements draw their 24 px drawing offset by half its size toward the top left, so that the element's own
    # box is a grid point and the ink hangs off it (measured in Chromium, 2026-11-04: the drawing lay 12 px above or
    # left of the host box). A component box holds the drawing instead: the offsets are cancelled so that the ink
    # lies in the host, which is `length` units of 24 px along the line and 24 px across it.
    "linehorizontal": "svg { top: 0 !important; }",
    "linevertical": "svg { left: 0 !important; }",
    "linejunction": "svg { left: 0 !important; top: 0 !important; }",
}

SIZES = ["regular", "medium", "large", "xl"]
PALETTES = ["day", "dusk", "night", "bright"]


# ------------------------------------------------------------------------------- manifest
def declaration(manifest: dict, tag: str) -> dict:
    for mod in manifest["modules"]:
        for d in mod.get("declarations", []):
            if d.get("tagName") == tag:
                return d
    raise SystemExit(f"{tag} not in the manifest")


def enums() -> dict[str, list[str]]:
    """Enum values from the full bundle (esbuild's enum pattern) and the type declarations."""
    out: dict[str, list[str]] = {}
    bundle = (PKG / "bundle/openbridge-webcomponents.bundle.js").read_text(encoding="utf-8")
    for m in re.finditer(r"var (\w+?)(?:\$\d+)? = /\* @__PURE__ \*/ \(\((\w+)\) => \{(.*?)return \2;", bundle, re.S):
        vals = re.findall(re.escape(m.group(2)) + r'\["[^"]+"\] = "([^"]+)"', m.group(3))
        if vals:
            out.setdefault(m.group(1), vals)
    for f in (PKG / "dist").rglob("*.d.ts"):
        for m in re.finditer(r"export declare enum (\w+) \{(.*?)\}", f.read_text(encoding="utf-8"), re.S):
            vals = re.findall(r'=\s*"([^"]+)"', m.group(2))
            if vals:
                out.setdefault(m.group(1), vals)
    return out


def local_enums(spec: dict) -> dict[str, list[str]]:
    """The enums an element's own declaration file declares. Two elements may declare an enum of
    the same name with different values (`AlertListMode`: five values in the alert list, three in
    the small alert page), so an element's own declaration wins over the package-wide map."""
    if not spec.get("dts"):
        return {}
    text = (PKG / "dist" / spec["dts"]).read_text(encoding="utf-8")
    return {m.group(1): re.findall(r'=\s*"([^"]+)"', m.group(2))
            for m in re.finditer(r"export declare enum (\w+) \{(.*?)\}", text, re.S)}


def clean(text: str | None) -> str:
    if not text:
        return ""
    t = re.sub(r"\s+", " ", text.replace("`", "")).strip()
    return t if len(t) <= 220 else t[:217].rsplit(" ", 1)[0] + "..."


MANIFEST: dict = {}      # set by `main`: the pinned custom elements manifest
DEFAULTS: dict = {}      # set by `main`: the measured defaults (web/defaults.json)


def part_specs(spec: dict, enum_map: dict) -> list[dict]:
    """The nested elements a composite renders itself (T2, batch F4: the top bar's alert button and clock). An entry
    `"parts": [{"tag": ..., "slot": ..., "fields": [...], "events": [...], "fixed": {...}}]` names an element of the manifest,
    the slot it stands in, the properties of that element the composite carries (their schemas, defaults and types are the
    element's own, as its own entry in `COMPONENTS` states them), the DOM events of that element the composite carries and
    the fields the wrapper sets on it and the page never does (`fixed`)."""
    out = []
    for pt in spec.get("parts", []):
        pspec = next((c for c in COMPONENTS if c["tag"] == pt["tag"]), None)
        if pspec is None:
            raise SystemExit(f"{spec['tag']}: part {pt['tag']} has no entry of its own in COMPONENTS")
        decl = declaration(MANIFEST, pt["tag"])
        if pt["slot"] not in {sl.get("name", "") for sl in declaration(MANIFEST, spec["tag"]).get("slots", [])}:
            raise SystemExit(f"{spec['tag']} declares no slot {pt['slot']!r} for the part {pt['tag']}")
        d = {k: (None if v == "__undefined__" else v) for k, v in DEFAULTS[pt["tag"]].items()}
        schema, fields = schema_for(pspec, decl, enum_map, d)
        by = {f["name"]: f for f in fields}
        members = {m["name"] for m in decl.get("members", []) if m.get("kind") == "field"}
        for n in pt["fields"]:
            if n not in by:
                raise SystemExit(f"{pt['tag']} has no carried property {n!r} for the part of {spec['tag']}")
        for n, v in pt.get("defaults", {}).items():      # the composite's own default for a carried property
            if n not in pt["fields"]:
                raise SystemExit(f"{pt['tag']}: {n!r} is not a carried property of the part, so it has no default to give")
            by[n]["def"] = v
            schema["properties"][n]["default"] = v
        for n in pt.get("fixed", {}):
            if n not in members:
                raise SystemExit(f"{pt['tag']} declares no field {n!r} for the part of {spec['tag']}")
        for e in pt.get("events", []):
            if e not in {x.get("name") for x in decl.get("events", [])}:
                raise SystemExit(f"{pt['tag']} declares no event {e!r} for the part of {spec['tag']}")
        out.append({"tag": pt["tag"], "slot": pt["slot"], "fields": [by[n] for n in pt["fields"]],
                    "props": {n: schema["properties"][n] for n in pt["fields"]}, "fixed": dict(pt.get("fixed", {})),
                    "events": list(pt.get("events", []))})
    return out


def event_fields(spec: dict, dom: str) -> list[dict]:
    """The fields of an event of the kind `detail`, from the entry's `eventFields`: (name, type, text) or (name, type, text, from),
    where `from` is the key of the event detail (a detail that is not an object is the value of the one field)."""
    rows = spec.get("eventFields", {}).get(dom)
    if not rows:
        raise SystemExit(f"{spec['tag']}: the event {dom!r} is of the kind detail and has no eventFields")
    return [{"name": r[0], "type": r[1], "text": r[2], **({"from": r[3]} if len(r) > 3 else {})} for r in rows]


def schema_for(spec: dict, decl: dict, enum_map: dict, defaults: dict) -> tuple[dict, list[dict]]:
    members = {m["name"]: m for m in decl.get("members", []) if m.get("kind") == "field"}
    props: dict[str, dict] = {}
    fields: list[dict] = []
    enum_map = {**enum_map, **local_enums(spec)}
    for a in decl.get("attributes", []):
        name = a.get("fieldName")
        if not name or name in spec["exclude"] or name in spec.get("data", {}):
            continue
        ttext = (spec.get("enums", {}).get(name)      # an attribute the manifest types as `string` that is an enumeration
                 or ((a.get("type") or {}).get("text") or "").strip() or spec.get("types", {}).get(name, ""))
        desc = clean((members.get(name) or {}).get("description") or a.get("description"))
        default = defaults.get(name)
        base = ttext.replace(" | undefined", "").replace(" | null", "")
        nullable = ttext != base
        if base == "boolean" and nullable and name in spec.get("undefinedWhenEmpty", []):
            # a tri-state flag: unset means the element decides from another property (the context menu's `multiSelect`)
            p, kind = {"type": ["boolean", "null"], "default": None}, "nboolean"
        elif base == "boolean":
            p, kind = {"type": "boolean", "default": bool(default)}, "boolean"
        elif base == "number" and not nullable:
            p, kind = {"type": "number", "default": default if isinstance(default, (int, float)) else 0}, "number"
        elif base == "number | string":     # a readout's value: a number, or a text under `valueType` text
            p, kind = {"type": ["number", "string", "null"], "default": None}, "nvalue"
        elif base == "number":
            p, kind = {"type": ["number", "null"], "default": default if isinstance(default, (int, float)) else None}, "nnumber"
        elif base == "string":
            p, kind = {"type": "string", "default": default if isinstance(default, str) else ""}, ("nstring" if nullable else "string")
            if name in spec.get("undefinedWhenEmpty", []):
                kind = "ustring"
        elif base == "TreeNavigationItemAlerts":      # an object of counts; undefined while there is none (T2, batch F3)
            p, kind = json.loads(json.dumps(ALERTS_SCHEMA)), "object"
        elif base in enum_map:
            vals = [v for v in enum_map[base] if v not in spec.get("without", {}).get(name, [])]
            d = default if default in vals else vals[0]
            p, kind = {"type": "string", "enum": vals, "default": d}, "string"
            if nullable and name in spec.get("undefinedWhenEmpty", []):      # an optional enumeration: empty is undefined (the idle state)
                p, kind = {"type": "string", "enum": [""] + vals, "default": ""}, "ustring"
        else:
            print(f"  skipped {spec['tag']}.{name}: type {ttext!r} not mapped")
            continue
        p["description"] = ALERTS_TEXT if kind == "object" else desc or f"Property `{name}` of the `{spec['tag']}` element."
        props[name] = p
        fields.append({"name": name, "kind": kind, "def": p["default"]})
    for name in spec.get("properties", []):
        want = PROPERTIES[name]
        if ((members.get(name) or {}).get("type") or {}).get("text") != want["type"]:
            raise SystemExit(f"{spec['tag']} declares no {want['type']} field {name!r} in the manifest")
        props[name] = dict(want)
        fields.append({"name": name, "kind": want["type"], "def": want["default"]})
    for name in spec.get("objects", []):      # a state object that is a field and not an attribute (the system menu, T2 batch F4)
        base = (((members.get(name) or {}).get("type") or {}).get("text") or "").replace(" | undefined", "")
        if base not in STATE_OBJECTS:
            raise SystemExit(f"{spec['tag']}: field {name!r} is of type {base!r}, which has no state object schema")
        props[name] = {"type": "object", "default": {}, "properties": json.loads(json.dumps(STATE_OBJECTS[base][1])),
                       "description": STATE_OBJECTS[base][0]}
        fields.append({"name": name, "kind": "object", "def": {}})
    for name, kind in spec.get("data", {}).items():
        props[name] = json.loads(json.dumps(DATA_SCHEMA[kind]))
        if kind == "tabs":      # the badge enumerations of the pinned package (`BadgeType`, `BadgeSize`)
            tp = props[name]["items"]["properties"]
            tp["badgeType"]["enum"], tp["badgeSize"]["enum"] = enum_map["BadgeType"], enum_map["BadgeSize"]
    for pt in part_specs(spec, enum_map):
        for name, pp in pt["props"].items():
            if name in props:
                raise SystemExit(f"{spec['tag']}: the part {pt['tag']} carries {name!r}, which is already a property")
            props[name] = dict(pp)
    for name in spec.get("fixed", {}):      # a field the wrapper sets and the page never does (a credential field is switched off)
        if name not in members:
            raise SystemExit(f"{spec['tag']} declares no field {name!r} to fix")
        if name in props:
            raise SystemExit(f"{spec['tag']}: {name!r} is fixed and also a property")
    slots = slot_specs(spec, decl, set(props) | set(spec.get("data", {})) | set(spec.get("extra", [])) | set(spec.get("items", {})))
    if slots:
        icons = icon_names()
        for sl in slots:
            props[sl["name"]] = slot_schema(sl, icons)
    for name, entry in spec.get("items", {}).items():
        props[name] = items_schema(entry, ITEM_TABLE)
    for name in spec.get("extra", []):
        props[name] = dict(EXTRA[name]["schema"])
        if EXTRA[name].get("enum"):      # the enumeration of the package's own declaration, as for an attribute
            vals = enum_map[EXTRA[name]["enum"]]
            props[name] = {"type": "string", "enum": vals, "default": EXTRA[name]["def"],
                           "description": props[name]["description"]}
        if name in spec.get("describe", {}):
            props[name]["description"] = spec["describe"][name]
    for name, text in spec.get("describe", {}).items():
        if name in props and name not in spec.get("extra", []):
            props[name]["description"] = text
    props["componentSize"] = {"type": "string", "enum": SIZES, "default": "regular",
                              "description": "Component size: regular, medium, large or xl."}
    props["style"] = {"$ref": "urn:ignition-schema:schemas/style-properties.schema.json",
                      "default": {"classes": ""}}
    return {"type": "object", "additionalProperties": False, "properties": props}, fields


# ------------------------------------------------------------------------------- stylesheet
def parse_rules(css: str) -> list[tuple[str, str]]:
    """Top-level rules as (prelude, body); nested at-rule bodies are kept whole."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules, depth, start, prelude = [], 0, 0, ""
    for i, ch in enumerate(css):
        if ch == "{":
            if depth == 0:
                prelude, start = css[start:i].strip(), i + 1
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                rules.append((prelude, css[start:i]))
                start = i + 1
    return rules


def declarations(body: str) -> list[tuple[str, str]]:
    out = []
    for part in body.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out.append((k.strip(), v.strip()))
    return out


FRESH_WATER = ("--automation-fresh-water", "--automation-medium-fresh-water")   # the name the lines read, the name the package defines


def scoped_css(bundle_js: str) -> tuple[str, dict]:
    css = (PKG / "dist/openbridge.css").read_text(encoding="utf-8")
    rules = parse_rules(css)
    # A variable is used where the bundle writes `var(--name)`, and also where it names the variable in a string and reads
    # it from the computed style (the charts' palette and fonts, `charthelpers/constants.js`, from C1).
    used = set(re.findall(r"var\(\s*(--[\w-]+)", bundle_js)) | set(re.findall(r"[\"'](--[a-z][\w-]*)[\"']", bundle_js))
    # The line elements read `--automation-fresh-water` for the medium water and air, but the pinned stylesheet defines the
    # colour as `--automation-medium-fresh-water`: the variable is undefined and the inner stroke of such a line draws as
    # none (measured in Chromium, 2026-11-04). The module keeps the defined colour and names it under the read name.
    if FRESH_WATER[0] in used:
        used.add(FRESH_WATER[1])
    defs: dict[str, set[str]] = {}
    for _, body in rules:
        for k, v in declarations(body):
            if k.startswith("--"):
                defs.setdefault(k, set()).update(re.findall(r"var\(\s*(--[\w-]+)", v))
    keep, todo = set(), [v for v in used if v in defs]
    while todo:
        v = todo.pop()
        if v in keep:
            continue
        keep.add(v)
        todo += [d for d in defs.get(v, ()) if d not in keep and d in defs]

    def sel(prelude: str) -> str | None:
        parts = [p.strip() for p in prelude.split(",")]
        out = []
        for p in parts:
            m = re.fullmatch(r':root\[data-obc-theme="(\w+)"\]', p)
            if p in (":root", "html"):      # `html` carries `--obc-can-hover`, which the chip's hover colours read
                out.append(".cadre-ob.cadre-ob")
            elif m:
                out.append(f".psc-cadre\\/palette\\/{m.group(1)} .cadre-ob.cadre-ob")
            elif p == "*":
                out += [".cadre-ob", ".cadre-ob *"]
            elif re.fullmatch(r"\.obc-component-size-\w+", p):
                out.append(f".cadre-ob{p}")
            else:
                return None
        return ", ".join(dict.fromkeys(out))

    blocks, stats = [], {"rules_in": len(rules), "rules_out": 0, "vars_defined": len(defs),
                         "vars_used_by_bundle": len(used), "vars_kept": len(keep)}
    for prelude, body in rules:
        if prelude.startswith("@property"):
            name = prelude.split()[1]
            if name in keep:
                blocks.append(f"{prelude} {{{body.strip()}}}")
            continue
        s = sel(prelude) if not prelude.startswith("@") else None
        if not s:
            continue
        decls = [f"{k}: {v}" for k, v in declarations(body) if k in keep]
        if decls:
            blocks.append(f"{s} {{\n  " + ";\n  ".join(decls) + ";\n}")
    stats["rules_out"] = len(blocks)
    head = ("/* Cadre HMI Components module stylesheet. Generated by module/tools/gen_module_assets.py from\n"
            "   @oicl/openbridge-webcomponents 2.0.0-next.155 dist/openbridge.css (Apache-2.0, Copyright 2024 OICL),\n"
            "   scoped to .cadre-ob and the Cadre palette classes, trimmed to the variables the bundled elements use. */\n")
    font = ('@font-face {\n  font-family: "Noto Sans OB";\n  src: url("../fonts/NotoSans-OB.ttf") format("truetype");\n'
            '  font-weight: 100 900;\n  font-style: normal;\n  font-display: swap;\n}\n'
            '.cadre-ob.cadre-ob, .cadre-ob * {\n  --global-typography-font-family: "Noto Sans OB", "Noto Sans", sans-serif;\n'
            '  --font-family-main: "Noto Sans OB", "Noto Sans", sans-serif;\n}\n'
            '.cadre-ob {\n  width: 100%;\n  height: 100%;\n  display: flex;\n  align-items: center;\n'
            '  justify-content: center;\n  box-sizing: border-box;\n}\n')
    # The wrapper centres its element, which suits a symbol; an alarm list fills its component box, top
    # aligned (COB-078). The parent project's stylesheet carried this rule until version 0.2.1 (COB-082).
    fresh = (f"/* The line elements read {FRESH_WATER[0]}; the package defines {FRESH_WATER[1]}. */\n"
             f".cadre-ob.cadre-ob {{\n  {FRESH_WATER[0]}: var({FRESH_WATER[1]});\n}}\n")
    lists = ('/* The alarm lists fill the component box, top aligned. */\n'
             '.cadre-ob > obc-alert-list-details,\n.cadre-ob > obc-alert-list-page-small {\n'
             '  align-self: stretch;\n  flex: 1 1 auto;\n  width: 100%;\n  min-height: 0;\n}\n')
    # The device components. The out of service veil lies over the 48 px symbol at the centre of the box and takes
    # no pointer; a readout that is told to stretch fills the box.
    devices = ("/* Out of service: the library view's veil and word (COB-159) over the symbol. */\n"
               ".cadre-ob { position: relative; }\n"
               ".cadre-ob > .cadre-ob-oos {\n  position: absolute;\n  left: 50%;\n  top: 50%;\n  width: 48px;\n"
               "  height: 48px;\n  margin: -24px 0 0 -24px;\n  border-radius: 6px;\n  display: flex;\n"
               "  align-items: center;\n  justify-content: center;\n  pointer-events: none;\n"
               "  background: color-mix(in srgb, var(--container-background-color, #fff) 72%, transparent);\n"
               "  color: var(--element-active-color, #1f1f1f);\n"
               "  font: 570 12px/14px var(--global-typography-font-family, sans-serif);\n}\n"
               "/* A stretched readout fills its component box. */\n"
               ".cadre-ob > obc-transmitter[data-stretch] {\n  align-self: stretch;\n  flex: 1 1 auto;\n  width: 100%;\n}\n"
               # The radial instrument sizes its dial from its host and has no size of its own: centred in the box it
               # drew at 0 by 0 on the gateway (T2, 2026-11-03), so it fills the box like the alarm lists.
               "/* The radial instrument fills its component box. */\n"
               ".cadre-ob > obc-instrument-radial {\n  align-self: stretch;\n  flex: 1 1 auto;\n  width: 100%;\n"
               "  height: 100%;\n  min-height: 0;\n}\n"
               # A row of the alert menu has no width of its own and collapses to its icon when centred (F2, measured in Chromium).
               "/* An alert menu row fills the width of its component box. */\n"
               ".cadre-ob > obc-alert-menu-item {\n  align-self: stretch;\n  flex: 1 1 auto;\n  width: 100%;\n}\n"
               # A navigation or tree row is as wide as its content when centred; a row is meant to fill a menu (F3, measured).
               "/* A navigation or tree row, and the tree, fill the width of their component box. */\n"
               ".cadre-ob > obc-navigation-item,\n.cadre-ob > obc-navigation-item-group,\n.cadre-ob > obc-tree-navigation-item,\n"
               ".cadre-ob > obc-tree-navigation-group,\n.cadre-ob > obc-tree-navigation {\n  align-self: stretch;\n  flex: 1 1 auto;\n"
               "  width: 100%;\n}\n"
               # The top bar is as wide as its content when centred; it is meant to span its dock (F4, measured in Chromium). Its height is its own (48).
               "/* The top bar fills the width of its component box; its height stays its own. */\n"
               ".cadre-ob > obc-top-bar {\n  flex: 1 1 auto;\n  width: 100%;\n}\n"
               # A notification row has no width of its own and collapses to its icon when centred (F5, measured in Chromium).
               "/* A notification menu row fills the width of its component box. */\n"
               ".cadre-ob > obc-notification-menu-item {\n  align-self: stretch;\n  flex: 1 1 auto;\n  width: 100%;\n}\n")
    return head + "\n".join(blocks) + "\n" + font + fresh + lists + devices, stats


# ------------------------------------------------------------------------------- wrappers
WRAPPER = r"""
/* Cadre HMI Components module: Perspective wrappers for the pinned web components.
   Generated by module/tools/gen_module_assets.py; do not edit. */
(function () {
  'use strict';
  var PC = window.PerspectiveClient;
  var h = window.React.createElement;
  var COMPONENTS = __COMPONENTS__;
  var SHEETS = __SHEETS__;
  var ITEMS = __ITEMS__;          // the elements an `items` property may build: attribute field names and child tags
  var ICONS = __ICONS__;          // the icons the slot properties and the items may use (web/icons.js)
  var ITEM_PLAIN = __ITEM_PLAIN__;
  var ITEM_DEPTH = __ITEM_DEPTH__;

  function read(tree, f) {
    switch (f.kind) {
      case 'boolean': return tree.readBoolean(f.name, f.def);
      case 'number': return tree.readNumber(f.name, f.def);
      case 'array': return tree.readArray(f.name, f.def);
      case 'nnumber': { var v = tree.read(f.name); return (v === null || v === undefined || v === '') ? undefined : Number(v); }
      case 'nvalue': { var q = tree.read(f.name); return (q === null || q === undefined || q === '') ? null : (typeof q === 'number' ? q : String(q)); }
      case 'nboolean': { var b = tree.read(f.name); return (b === null || b === undefined || b === '') ? undefined : !!b; }
      case 'nstring': { var s = tree.readString(f.name, ''); return s === '' ? null : s; }
      case 'ustring': { var u = tree.readString(f.name, ''); return u === '' ? undefined : u; }
      case 'object': { var o = tree.read(f.name); return (o && typeof o === 'object' && Object.keys(o).length) ? JSON.parse(JSON.stringify(o)) : undefined; }
      default: return tree.readString(f.name, f.def);
    }
  }

  // Alert records arrive with epoch millisecond times (cadre.hmi.alarm_list); the elements expect Dates.
  function toDate(v) { return (v === null || v === undefined || v === '') ? v : new Date(Number(v)); }
  function toAlerts(list) {
    if (!Array.isArray(list)) return [];
    return list.map(function (a) {
      var o = Object.assign({}, a);
      o.time = toDate(a.time);
      if (a.lastModified !== undefined) o.lastModified = toDate(a.lastModified);
      if (a.acknowledged && typeof a.acknowledged === 'object')
        o.acknowledged = Object.assign({}, a.acknowledged, { acknowledgedAt: toDate(a.acknowledged.acknowledgedAt) });
      if (a.active && typeof a.active === 'object')
        o.active = Object.assign({}, a.active, { rectifiedTime: toDate(a.active.rectifiedTime) });
      if (a.shelved && typeof a.shelved === 'object')
        o.shelved = Object.assign({}, a.shelved, { shelvedStartTime: toDate(a.shelved.shelvedStartTime),
                                                    shelvedEndTime: toDate(a.shelved.shelvedEndTime) });
      return o;
    });
  }
  // A list of objects or strings the property tree holds, as a mutable copy: Chart.js writes to the arrays it is given.
  function toRecords(v) { return Array.isArray(v) ? JSON.parse(JSON.stringify(v)) : []; }
  // The crumbs of the breadcrumb: label and href only (the element calls a crumb's `icon`, which data cannot be).
  function toCrumbs(v) {
    return Array.isArray(v) ? v.filter(function (c) { return c && typeof c === 'object'; })
      .map(function (c) { return { label: String(c.label === undefined || c.label === null ? '' : c.label), href: c.href ? String(c.href) : undefined }; }) : [];
  }
  // The tabs of the tab row (TabData): the fields the element reads, as plain values (`iconName` is the module's own, see applyTabIcons).
  function toTabs(v) {
    var str = ['id', 'title', 'subtitle', 'badgeType', 'badgeSize'], bool = ['showSubtitle', 'hasLeadingIcon', 'hasBadge', 'badgeShowNumber',
      'showLeadingBadgeIcon', 'disabled'];
    return Array.isArray(v) ? v.filter(function (t) { return t && typeof t === 'object' && t.id !== undefined && t.id !== null && t.id !== ''; })
      .map(function (t) {
        var o = { id: String(t.id), title: String(t.title === undefined || t.title === null ? '' : t.title) };
        str.slice(2).forEach(function (k) { if (t[k] !== undefined && t[k] !== null && t[k] !== '') o[k] = String(t[k]); });
        bool.forEach(function (k) { if (t[k] !== undefined && t[k] !== null) o[k] = !!t[k]; });
        if (t.badgeCount !== undefined && t.badgeCount !== null) o.badgeCount = Number(t.badgeCount) || 0;
        return o;
      }) : [];
  }
  // The options of the context menu (ContextMenuOption without its icon, a template function) and its column groups (ColumnGroup).
  function toOptions(v) {
    return Array.isArray(v) ? v.filter(function (o) { return o && typeof o === 'object'; }).map(function (o) {
      var r = { value: String(o.value === undefined || o.value === null ? '' : o.value), label: String(o.label === undefined || o.label === null ? '' : o.label) };
      if (o.level !== undefined && o.level !== null) r.level = Number(o.level) || 0;
      if (Array.isArray(o.children) && o.children.length) r.children = toOptions(o.children);
      return r;
    }) : [];
  }
  function toColumnGroups(v) {
    return Array.isArray(v) ? v.filter(function (g) { return g && typeof g === 'object'; })
      .map(function (g) { return { title: String(g.title === undefined || g.title === null ? '' : g.title), columns: Number(g.columns) || 1, options: toOptions(g.options) }; }) : [];
  }
  var CONVERT = { alerts: toAlerts, crumbs: toCrumbs, tabs: toTabs, menuoptions: toOptions, columngroups: toColumnGroups,
                  strings: function (v) { return Array.isArray(v) ? v.map(String) : []; }, numbers: function (v) { return Array.isArray(v) ? v.map(Number) : []; },
                  points: toRecords, datasets: toRecords, yaxes: toRecords, labels: toRecords, colors: toRecords,
                  segments: toRecords, piesegments: toRecords, linearadvices: toRecords, radialadvices: toRecords,
                  rings: function (v) { return Array.isArray(v) ? v.map(Number) : []; } };

  // The payload of a Perspective component event, from the element's event detail.
  function payload(kind, e, el, node, ev) {
    var d = (e && e.detail) || {};
    if (kind === 'alert') {
      var a = d.alert || {};
      return { ids: a.id ? [String(a.id)] : [], id: String(a.id || ''), tagId: String(a.tagId || ''),
               source: String(a.source || ''), text: String(a.text || '') };
    }
    if (kind === 'visible') {
      var mode = d.mode || 'unacked';
      var shown = (el && el.alerts || []).filter(function (a) {
        return mode === 'shelved' ? !!a.shelved : (mode === 'all' ? true : !a.acknowledged);
      });
      return { mode: String(mode), ids: shown.filter(function (a) { return !a.acknowledged; })
                                            .map(function (a) { return String(a.id); }) };
    }
    if (kind === 'notification') return { count: Number(d.count) || 0, isActive: !!d.isActive };
    if (kind === 'menuvisible') {
      var vis = (d.visibleElements || []).map(function (v) { return v && v.element && v.element.getAttribute ? v.element.getAttribute('data-item-id') : null; })
                                        .filter(function (i) { return i !== null && i !== ''; });
      return { mode: String(d.tabName || 'unacked'), ids: vis };
    }
    if (kind === 'label') return { label: String(d.label === undefined || d.label === null ? '' : d.label) };
    if (kind === 'item' || kind === 'itemexpanded') {
      // the item that heard the event (a nested item hears its own), else the nearest item above the target
      var from = node || (e && e.target && e.target.closest ? e.target.closest('[data-item-id],[data-cadre-item]') : null);
      var o = { id: from ? String(from.getAttribute('data-item-id') || '') : '', tag: from ? String(from.tagName).toLowerCase() : '' };
      if (kind === 'itemexpanded') o.expanded = !!(e && e.detail);
      return o;
    }
    if (kind === 'expanded') return { expanded: !!(e && e.detail) };
    if (kind === 'detail') {
      // the fields the entry states (`eventFields`): from the detail object by the field's name (or its `from`), or the detail itself
      // when that is not an object (a search field reports its text)
      var out = {}, raw = e ? e.detail : undefined;
      ((ev && ev.fields) || []).forEach(function (f) {
        // a `from` with dots reads a field of a nested object of the detail (the tab row's `tab.title`)
        var v = raw;
        if (raw !== null && typeof raw === 'object') {
          v = raw;
          (f.from || f.name).split('.').forEach(function (k) { v = (v !== null && typeof v === 'object') ? v[k] : undefined; });
        }
        out[f.name] = f.type === 'boolean' ? !!v : (f.type === 'number' ? (Number(v) || 0)
          : (f.type === 'array' ? (Array.isArray(v) ? v.map(String) : []) : String(v === undefined || v === null ? '' : v)));
      });
      return out;
    }
    if (kind === 'crumb') {
      var c = (e && e.detail) || {};
      return { label: String(c.label === undefined || c.label === null ? '' : c.label), href: c.href ? String(c.href) : '',
               index: el && Array.isArray(el.items || el.breadcrumbItems) ? (el.items || el.breadcrumbItems).indexOf(c) : -1 };
    }
    return {};
  }

  // ---- Child elements from an `items` property (T2, batch F1). An item is an object: `tag`, the element's attributes by
  // field name, `text`, `id`, `slot` and `children`. The tag must be one the component's entry allows at the top level, or
  // one the parent's tag allows (ITEMS[parent].kids), or a plain element or a bundled icon below the top level; an
  // attribute the table does not list is ignored with a warning, and an item nested deeper than ITEM_DEPTH is dropped.
  // Attributes are set as properties of the element (never as markup), so booleans, numbers and objects arrive as they are.
  function isIconTag(tag) { return tag.indexOf('obi-') === 0 && ICONS.indexOf(tag.slice(4)) >= 0; }
  function buildItem(o, allowed, depth, slot) {
    if (!o || typeof o !== 'object' || typeof o.tag !== 'string' || depth > ITEM_DEPTH) return null;
    var tag = o.tag;
    var below = depth > 0 && (ITEM_PLAIN.indexOf(tag) >= 0 || isIconTag(tag));
    if (allowed.indexOf(tag) < 0 && !below) { console.warn('cadre-ob: item tag not allowed here: ' + tag); return null; }
    var el = document.createElement(tag);
    var own = slot || (typeof o.slot === 'string' ? o.slot : '');
    if (own) el.setAttribute('slot', own);
    if (o.id !== undefined && o.id !== null && o.id !== '') el.setAttribute('data-item-id', String(o.id));
    var info = ITEMS[tag], names = info ? info.props : [];
    Object.keys(o).forEach(function (k) {
      if (k === 'tag' || k === 'id' || k === 'slot' || k === 'text' || k === 'children') return;
      if (names.indexOf(k) >= 0) el[k] = o[k];
      else console.warn('cadre-ob: ' + tag + ' has no item attribute ' + k);
    });
    if (typeof o.text === 'string' && o.text !== '') el.textContent = o.text;
    var kids = info ? info.kids : [];
    (Array.isArray(o.children) ? o.children : []).forEach(function (c) {
      var n = buildItem(c, kids, depth + 1, '');
      if (n) el.appendChild(n);
    });
    return el;
  }

  function wrapper(spec) {
    class ObWrapper extends PC.Component {
      constructor(props) {
        super(props);
        this.el = null;
        this.handlers = [];
        this.applied = {};
        this.itemNodes = {};
        // row selection (alarm lists, module 0.4.2): the ids shown and sent, the table and what watches it
        this.selIds = [];
        this.selSent = [];
        this.selOn = false;
        this.selTouched = false;
        this.selQueued = false;
        this.table = null;
        this.selHost = null;
        this.tableKey = null;
        // the elements the component renders itself (the top bar's alert button and clock): the node, and the listeners on it
        this.partNodes = [];
        this.partListeners = [];
        this.partRefs = (spec.parts || []).map((pt, i) => (n) => this.setPart(i, n));
        this.onTick = (e) => {
          var t = this.table;
          if (!t) return;
          this.writeSelection(((e && e.detail && e.detail.selectedRowIds) || []).map(String));
          this.showSelection(t);
        };
        this.selWatch = (spec.selection && typeof MutationObserver === 'function')
          ? new MutationObserver(() => { if (this.selOn || this.selTouched) this.syncSelection(); }) : null;
        this.setRef = (el) => {
          this.unlisten();
          this.selDetach();
          this.el = el;
          this.applied = {};
          this.itemNodes = {};
          if (el && spec.sheet) this.sheets();
          if (el) {
            (spec.events || []).filter((ev) => !ev.onItems && ev.part === undefined).forEach((ev) => {
              var f = (e) => this.fire(ev, e);
              el.addEventListener(ev.dom, f);
              this.handlers.push([el, ev.dom, f]);
            });
          }
          this.apply();
        };
      }
      componentDidUpdate() { this.apply(); }
      componentWillUnmount() { this.unlisten(); this.selDetach(); (this.partNodes || []).forEach((n, i) => this.setPart(i, null)); }
      // Rules added to the shadow root of the element, and of the chip inside a readout (spec.chipSheet). The
      // shadow root exists once the element is connected and has drawn once, so the work waits for that; it
      // runs again after each update, because an alert frame around a readout draws a new chip.
      sheets() {
        var el = this.el;
        if (!el) return;
        Promise.resolve(el.updateComplete).then(() => {
          var put = function (root, css) {
            if (!root || root.querySelector('style[data-cadre]')) return;
            var st = document.createElement('style');
            st.setAttribute('data-cadre', '');
            st.textContent = css;
            root.appendChild(st);
          };
          put(el.shadowRoot, SHEETS[spec.sheet]);
          if (spec.chipSheet && el.shadowRoot) {
            var chip = el.shadowRoot.querySelector('obc-transmitter-button');
            if (chip) {
              put(chip.shadowRoot, SHEETS[spec.chipSheet]);
              chip.toggleAttribute('data-stretch', el.hasAttribute('data-stretch'));
            }
          }
        });
      }
      unlisten() {
        this.handlers.forEach(function (h) { h[0].removeEventListener(h[1], h[2]); });
        this.handlers = [];
      }
      fire(ev, e, node) {
        // an event of the element that only a CustomEvent counts (the tree row fires its own `click`; the user's native click
        // reaches the host as well, also for a disabled row)
        if (ev.custom && typeof MouseEvent === 'function' && e instanceof MouseEvent) return;
        var ce = this.props.componentEvents;
        if (ce && typeof ce.fireComponentEvent === 'function') ce.fireComponentEvent(ev.name, payload(ev.payload, e, this.el, node, ev));
        // an element that changes its own state on a press (the command menu, the brilliance menu): the component's property follows
        // the press, so that the next update does not set the element back. A property bound one way is set by its binding again.
        if (ev.write) {
          var raw = e ? e.detail : undefined;
          // `from` names the key of the event detail; the word @element says the event carries nothing and the element's own property is the value
          var v = ev.from === '@element' ? (this.el ? this.el[ev.write] : undefined)
            : ((raw !== null && typeof raw === 'object') ? raw[ev.from || ev.write] : raw);
          if (v !== undefined) this.put(ev.write, Array.isArray(v) ? v.slice() : v);
        }
      }
      // A nested element of a composite (spec.parts): its node is kept, its properties are set from the component's, and its events
      // are carried as the component's own. The events of such an element do not bubble, so they are heard on the node itself.
      setPart(i, n) {
        (this.partListeners[i] || []).forEach(function (l) { l[0].removeEventListener(l[1], l[2]); });
        this.partListeners[i] = [];
        this.partNodes[i] = n;
        if (!n) return;
        (spec.events || []).filter((ev) => ev.part === i).forEach((ev) => {
          var f = (e) => this.fire(ev, e);
          n.addEventListener(ev.dom, f);
          this.partListeners[i].push([n, ev.dom, f]);
        });
        this.applyPart(i);
      }
      applyPart(i) {
        var n = this.partNodes[i], pt = (spec.parts || [])[i], p = this.props.props;
        if (!n || !pt) return;
        pt.fields.forEach(function (f) { if (n[f.name] !== p[f.name]) n[f.name] = p[f.name]; });
        Object.keys(pt.fixed || {}).forEach(function (k) { if (n[k] !== pt.fixed[k]) n[k] = pt.fixed[k]; });
      }
      apply() {
        var el = this.el;
        if (!el) return;
        var p = this.props.props;
        // no speed: the element prints one unless both its speed properties are undefined
        var speedless = spec.speedless && p.hasSpeed === false;
        for (var i = 0; i < spec.fields.length; i++) {
          var n = spec.fields[i].name;
          if (speedless && (n === 'speed' || n === 'speedInPercent')) { if (el[n] !== undefined) el[n] = undefined; continue; }
          if (spec.generator && n === 'value') continue;      // set from the running state (applyGenerator)
          if (spec.fields[i].kind === 'object') {      // an object is compared by value: the property tree hands a new copy each time
            var ok = JSON.stringify(p[n] === undefined ? null : p[n]);
            if (this.applied['o:' + n] !== ok) { this.applied['o:' + n] = ok; el[n] = p[n]; }
            continue;
          }
          if (el[n] !== p[n]) el[n] = p[n];
        }
        Object.keys(spec.fixed || {}).forEach(function (k) { if (el[k] !== spec.fixed[k]) el[k] = spec.fixed[k]; });
        (spec.parts || []).forEach((pt, i) => this.applyPart(i));
        if (spec.endAligned) el.toggleAttribute('data-center', !!p.center);
        if (spec.chipSheet) { el.toggleAttribute('data-stretch', !!p.stretch); this.sheets(); }
        if (spec.status) this.applyStatus(el, p);
        if (spec.generator) this.applyGenerator(el, p);
        (spec.data || []).forEach((d) => {
          var key = JSON.stringify(p[d.name] === undefined ? null : p[d.name]);
          if (this.applied[d.name] !== key) { this.applied[d.name] = key; el[d.name] = CONVERT[d.kind](p[d.name]); }
        });
        this.applyItems(el, p);
        if (spec.tabIcons) this.applyTabIcons(el, p);
        if (spec.selection) this.applySelection(p);
      }
      // An event of an item that does not bubble (the alert menu's rows fire plain CustomEvents) is heard on the item itself;
      // the item node is dropped with its listeners when the list changes.
      // A nested item hears its own events too (a navigation group holds items, a tree group holds rows, to any depth). An event that
      // bubbles (a native click) reaches every item above its target, so an item answers only when it is the nearest item.
      listenItem(n) {
        var on = (spec.events || []).filter((ev) => ev.onItems);
        if (!on.length) return;
        var nodes = [n].concat(Array.prototype.slice.call(n.querySelectorAll('*')).filter(function (x) { return !!ITEMS[x.tagName.toLowerCase()]; }));
        nodes.forEach((m) => {
          on.forEach((ev) => {
            m.addEventListener(ev.dom, (e) => {
              var near = e.target && e.target.closest ? e.target.closest(Object.keys(ITEMS).join(',')) : null;
              if (near === m) this.fire(ev, e, m);
            });
          });
        });
      }
      // The children an `items` property builds (module 0.7.0): rebuilt when the list changes, marked data-cadre-item so that
      // they never mix with the children React draws for the slot properties.
      applyItems(el, p) {
        var rebuilt = false;
        (spec.items || []).forEach((it) => {
          var list = p[it.name];
          var key = JSON.stringify(list === undefined ? null : list);
          if (this.applied['items:' + it.name] === key) return;
          this.applied['items:' + it.name] = key;
          rebuilt = true;
          (this.itemNodes[it.name] || []).forEach(function (n) { n.remove(); });
          var nodes = [];
          (Array.isArray(list) ? list : []).forEach((o) => {
            var n = buildItem(o, it.tags, 0, it.slot);
            if (n) { n.setAttribute('data-cadre-item', ''); nodes.push(n); el.appendChild(n); this.listenItem(n); }
          });
          this.itemNodes[it.name] = nodes;
        });
        // a group that selects among its children (the pivot group) marks them only when its own selection changes, so it is asked to
        // mark the children that were just built
        if (rebuilt && typeof el.updateChildItems === 'function') el.updateChildItems();
      }
      // The icon of each tab of the tab row (batch F5): the row draws a placeholder icon in the slot `tab-<id>-icon` unless a child of the
      // host stands in it, so a tab's `iconName` (a bundled icon) becomes an `obi-` element in that slot. Rebuilt when the tabs change.
      applyTabIcons(el, p) {
        var tabs = Array.isArray(p.tabs) ? p.tabs : [];
        var key = JSON.stringify(tabs.map(function (t) { return t && [t.id, t.iconName]; }));
        if (this.applied.tabIcons === key) return;
        this.applied.tabIcons = key;
        (this.tabIconNodes || []).forEach(function (n) { n.remove(); });
        this.tabIconNodes = [];
        tabs.forEach((t) => {
          if (!t || t.id === undefined || t.id === null || t.id === '' || typeof t.iconName !== 'string' || ICONS.indexOf(t.iconName) < 0) return;
          var n = document.createElement('obi-' + t.iconName);
          n.setAttribute('slot', 'tab-' + t.id + '-icon');
          n.setAttribute('data-cadre-item', '');
          el.appendChild(n);
          this.tabIconNodes.push(n);
        });
      }
      // ---- Row selection of the two alarm lists (module 0.4.2). The package's table draws the tick column (an
      // obc-checkbox in each row, and one in the header of the full list) when its `selectable` is true, takes the
      // ticked ids from `selectedRowIds` and reports a toggle as `selection-change`; the alert list sets none of the
      // three, so the wrapper sets them on the table inside the list (the alert panel nests the list in its shadow
      // root). A tick stops its own click, so a toggle never reaches the row click. The wrapper keeps the ids itself,
      // shows a toggle at once and writes it to `selectedIds`; a value that comes back is either the wrapper's own
      // echo (ignored) or an outside change, such as the library clearing the selection after an acknowledgement
      // (it wins). Ids of rows the list no longer shows are dropped (pruneSelection).
      applySelection(p) {
        var on = !!p.selectable;
        if (!on && !this.selTouched) return;
        this.selTouched = true;
        this.selOn = on;
        var incoming = Array.isArray(p.selectedIds) ? p.selectedIds.map(String) : [];
        var at = this.selSent.indexOf(JSON.stringify(incoming));
        if (at >= 0) this.selSent.splice(0, at + 1);
        else { this.selSent = []; this.selIds = incoming; }
        this.syncSelection();
      }
      selectionHost() {
        var el = this.el;
        if (!el) return null;
        if (el.tagName === 'OBC-ALERT-LIST-DETAILS') return el;
        return el.shadowRoot ? el.shadowRoot.querySelector('obc-alert-list-details') : null;
      }
      // Waits until the element, the list inside it and the table have drawn, then binds the table.
      syncSelection() {
        var el = this.el;
        if (!el || this.selQueued) return;
        this.selQueued = true;
        var table = null;
        Promise.resolve(el.updateComplete).then(() => {
          var host = this.selectionHost();
          return host && host !== el ? host.updateComplete : null;
        }).then(() => {
          var host = this.selectionHost();
          table = host && host.shadowRoot ? host.shadowRoot.querySelector('obc-table') : null;
          return table ? table.updateComplete : null;
        }).then(() => {
          this.selQueued = false;
          if (this.el === el) this.bindSelection(table);
        }).catch(() => { this.selQueued = false; });
      }
      bindSelection(t) {
        var host = this.selectionHost();
        if (this.table !== t || this.selHost !== host) {
          if (this.table) this.table.removeEventListener('selection-change', this.onTick);
          if (this.selWatch) this.selWatch.disconnect();
          this.table = t;
          this.selHost = host;
          this.tableKey = null;
          if (t) t.addEventListener('selection-change', this.onTick);
          // the list draws a new table when it was empty, and the table draws new rows when its data changes
          if (this.selWatch && host && host.shadowRoot) this.selWatch.observe(host.shadowRoot, { childList: true, subtree: true });
          if (this.selWatch && t && t.renderRoot) this.selWatch.observe(t.renderRoot, { childList: true, subtree: true });
        }
        // no table: the list shows no row (an empty list draws a message instead), so nothing stays selected
        if (!t) { if (host && this.selOn && this.selIds.length) this.writeSelection([]); return; }
        if (t.selectable !== this.selOn) t.selectable = this.selOn;
        if (!this.selOn) { if (t.selectedRowIds !== undefined) t.selectedRowIds = undefined; this.tableKey = null; return; }
        this.pruneSelection(t);
        this.showSelection(t);
      }
      // The table's own ids (as the rows carry them) for the selected strings that its rows still show.
      rowIds(t, ids) {
        var byKey = {};
        (t.data || []).forEach(function (r) { byKey[String(r.id)] = r.id; });
        return ids.filter(function (i) { return Object.prototype.hasOwnProperty.call(byKey, i); })
                  .map(function (i) { return byKey[i]; });
      }
      showSelection(t) {
        var ids = this.rowIds(t, this.selIds), key = JSON.stringify(ids);
        if (this.tableKey !== key) { this.tableKey = key; t.selectedRowIds = ids; }
      }
      pruneSelection(t) {
        var kept = this.rowIds(t, this.selIds).map(String);
        if (kept.length !== this.selIds.length) this.writeSelection(kept);
      }
      writeSelection(ids) {
        this.selIds = ids;
        this.selSent.push(JSON.stringify(ids));
        this.put('selectedIds', ids);
      }
      put(name, value) {
        try {
          var store = this.props.store;
          if (store && store.props && typeof store.props.write === 'function') store.props.write(name, value);
        } catch (e) { /* a write refused is not a reason to break the page */ }
      }
      selDetach() {
        if (this.table) this.table.removeEventListener('selection-change', this.onTick);
        if (this.selWatch) this.selWatch.disconnect();
        this.table = null;
        this.selHost = null;
        this.selQueued = false;
      }

      // The status word of a pump, motor or fan. The element draws its status readouts from `extraReadouts`:
      // its speed while it runs and the word Off while it stands, none at all when its showStatus is false. The
      // wrapper passes showStatus on, and, when statusText is given, replaces the element's readouts with the one
      // word in the element's status place (the stock library view's status row does the same).
      applyStatus(el, p) {
        var show = p.showStatus !== false;
        if (el.showStatus !== show) el.showStatus = show;
        var text = typeof p.statusText === 'string' ? p.statusText : '';
        if (!this.statusInstalled) {
          this.statusInstalled = true;
          var base = null;
          for (var o = Object.getPrototypeOf(el); o && !base; o = Object.getPrototypeOf(o)) {
            var d = Object.getOwnPropertyDescriptor(o, 'extraReadouts');
            if (d && d.get) base = d.get;
          }
          var self = this;
          Object.defineProperty(el, 'extraReadouts', { configurable: true, get: function () {
            var own = base ? base.call(el) : [];
            if (!self.statusText || el.showStatus === false) return own;
            return [{ type: el.on ? 'state-on' : 'state-off', value: self.statusText, hasIcon: true }];
          } });
        }
        if (this.statusText !== text) { this.statusText = text; if (el.requestUpdate) el.requestUpdate(); }
      }
      // The indicator generator (module 0.4.4, spike T0 wrap W2). The element draws a disc whose scheme is its `value`
      // (`off` hides the rings and greys the disc) and knows nothing of a running state, an identifier, a status word
      // or an alert. The wrapper selects the scheme from `on` (a generator that is not running draws `off`; one that
      // runs draws `value`, the regular scheme where `value` is off), and draws the rest with the package's own elements,
      // unchanged, in the shadow root of the indicator: `obc-alert-frame` over the 48 px symbol, which colours its
      // levels as the other device components do, and `obc-automation-button-readout-stack`, the identifier and the
      // status word as the other symbols print them. The plain fields `tag`, `on`, `alert` and `alertFrameMode`
      // are set on the element as well, which is where the glass gates read a device component's state.
      applyGenerator(el, p) {
        var value = p.on ? (p.value === 'off' ? 'regular' : p.value) : 'off';
        if (el.value !== value) el.value = value;
        el.tag = p.tag || '';
        el.on = !!p.on;
        el.alert = !!p.alert;
        el.alertFrameMode = p.alertFrameMode;
        el.alertFrameStatus = p.alertFrameStatus;
        Promise.resolve(el.updateComplete).then(() => { if (this.el === el) this.drawGenerator(el, p); });
      }
      drawGenerator(el, p) {
        var root = el.shadowRoot;
        if (!root) return;
        var frame = root.querySelector('obc-alert-frame[data-cadre]');
        if (p.alert) {
          if (!frame) {
            frame = document.createElement('obc-alert-frame');
            frame.setAttribute('data-cadre', '');
            root.appendChild(frame);
          }
          frame.type = 'small-side-flip';
          frame.thickness = 'small';
          frame.status = p.alertFrameStatus;
          frame.mode = p.alertFrameMode;
        } else if (frame) frame.remove();
        var stack = root.querySelector('obc-automation-button-readout-stack[data-cadre]');
        var side = p.readoutPosition || 'bottom';
        var show = p.showStatus !== false;
        if (side === 'none' || (!show && !p.tag)) { if (stack) stack.remove(); return; }
        if (!stack) {
          stack = document.createElement('obc-automation-button-readout-stack');
          stack.setAttribute('data-cadre', '');
          root.appendChild(stack);
        }
        var word = (typeof p.statusText === 'string' && p.statusText) ? p.statusText : (p.on ? 'On' : 'Off');
        stack.tag = p.tag || null;
        stack.readouts = show ? [{ type: p.on ? 'state-on' : 'state-off', value: word, hasIcon: true }] : [];
        stack.size = 'regular';
        stack.idTagOrientation = side === 'top' ? 'top' : 'bottom';    // as obc-automation-button does
        var at = { top: 'bottom:100%;left:50%;transform:translateX(-50%)', bottom: 'top:100%;left:50%;transform:translateX(-50%)',
                   left: 'right:100%;top:50%;transform:translateY(-50%)', right: 'left:100%;top:50%;transform:translateY(-50%)' };
        stack.style.cssText = 'position:absolute;pointer-events:none;' + (at[side] || at.bottom);
      }
      // The duty badge goes into the first free corner of the element, unless its interlock badge, which draws
      // the same icon, is already there.
      dutySlot(p) {
        if (p.badgeInterlock === 'interlock') return null;
        var corners = [['badge-bottom-left', p.badgeInterlock], ['badge-bottom-right', p.badgeCommandLocked],
                       ['badge-top-left', p.badgeControl], ['badge-top-right', p.badgeAlert]];
        for (var i = 0; i < corners.length; i++) if (!corners[i][1] || corners[i][1] === 'none') return corners[i][0];
        return null;
      }
      render() {
        var size = this.props.props.componentSize || 'regular';
        var p = this.props.props, kids = [];
        if (spec.tankSlots) {
          // slotted content replaces the tank's own: its unit (cubic metres by default) and, for a static
          // tank with no capacity, its whole readout
          if (p.unit && p.unit !== 'm\u00b3') kids.push(h('span', { slot: 'unit', key: 'unit' }, p.unit));
          if (p.static && p.hasCapacity === false) kids.push(h('span', { slot: 'readout', key: 'readout' }));
        }
        if (spec.status && p.badgeDuty) {
          var slot = this.dutySlot(p);
          if (slot) kids.push(h('obc-automation-badge', { slot: slot, key: 'duty', type: 'interlock' }));
        }
        // the slot properties: a text becomes a text node (the default slot) or a span in its slot, an icon an `obi-` element
        (spec.slots || []).forEach(function (sl) {
          var v = p[sl.name];
          if (typeof v !== 'string' || v === '') return;
          if (sl.kind === 'icon') {
            if (ICONS.indexOf(v) >= 0) kids.push(h('obi-' + v, { slot: sl.slot || undefined, key: 'slot:' + sl.name }));
          } else kids.push(sl.slot ? h('span', { slot: sl.slot, key: 'slot:' + sl.name }, v) : v);
        });
        // the elements a composite renders itself, each in its slot; their properties are set in `applyPart`
        (spec.parts || []).forEach((pt, i) => kids.push(h(pt.tag, { slot: pt.slot, key: 'part:' + i, ref: this.partRefs[i] })));
        // an out of service symbol: the library view's veil of the page colour and the word OOS, over the symbol
        var oos = (spec.status && p.outOfService) ? h('div', { className: 'cadre-ob-oos', key: 'oos' }, 'OOS') : null;
        // an element that sits at the end of its box unless the symbol is centred
        var at = spec.endAligned ? { justifyContent: p.center ? 'center' : 'flex-end' } : undefined;
        return h('div', this.props.emit(),
          h('div', { className: 'cadre-ob obc-component-size-' + size, style: at },
            h.apply(null, [spec.tag, { ref: this.setRef }].concat(kids)), oos));
      }
    }
    return ObWrapper;
  }

  COMPONENTS.forEach(function (spec) {
    var View = wrapper(spec);
    PC.ComponentRegistry.register({
      getComponentType: function () { return spec.type; },
      getViewComponent: function () { return View; },
      getDefaultSize: function () { return spec.size; },
      getPropsReducer: function (tree) {
        var out = { componentSize: tree.readString('componentSize', 'regular') };
        spec.fields.forEach(function (f) { out[f.name] = read(tree, f); });
        (spec.extras || []).forEach(function (f) { out[f.name] = read(tree, f); });
        (spec.parts || []).forEach(function (pt) { pt.fields.forEach(function (f) { out[f.name] = read(tree, f); }); });
        (spec.data || []).forEach(function (d) { out[d.name] = tree.readArray(d.name, []); });
        (spec.items || []).forEach(function (d) { out[d.name] = tree.readArray(d.name, []); });
        return out;
      }
    });
  });
})();
"""


def js_spec(spec: dict, fields: list[dict], events: list[dict], slots: list[dict], items: list[dict],
            parts: list[dict] | None = None) -> dict:
    """What the browser wrapper needs of one component (the JSON in `COMPONENTS` of `WRAPPER`)."""
    return {"type": spec["type"], "tag": spec["tag"], "size": spec["size"], "fields": fields,
            "extras": [{"name": n, "kind": EXTRA[n]["kind"], "def": EXTRA[n]["def"]} for n in spec.get("extra", [])]
                      + [{"name": sl["name"], "kind": "string", "def": ""} for sl in slots],
            "speedless": bool(spec.get("speedless")), "generator": bool(spec.get("generator")), "tankSlots": bool(spec.get("tankSlots")),
            "sheet": spec.get("sheet", ""), "chipSheet": spec.get("chipSheet", ""),
            "selection": bool(spec.get("selection")), "tabIcons": bool(spec.get("tabIcons")),
            "status": bool(spec.get("status")), "endAligned": bool(spec.get("endAligned")),
            "data": [{"name": n, "kind": k} for n, k in spec.get("data", {}).items()],
            "events": events,
            **({"slots": [{"slot": sl["slot"], "kind": sl["kind"], "name": sl["name"]} for sl in slots]} if slots else {}),
            **({"items": items} if items else {}),
            **({"parts": [{"tag": pt["tag"], "slot": pt["slot"], "fields": pt["fields"], "fixed": pt["fixed"]} for pt in parts]} if parts else {}),
            **({"fixed": spec["fixed"]} if spec.get("fixed") else {})}


def wrapper_script(js_specs: list[dict]) -> str:
    """The React wrappers for `js_specs`, with the tables of the sheets, the item elements and the icons filled in."""
    out = WRAPPER.replace("__COMPONENTS__", json.dumps(js_specs, separators=(",", ":"))) \
                 .replace("__SHEETS__", json.dumps(SHEETS, separators=(",", ":")))
    return (out.replace("__ITEMS__", json.dumps(ITEM_TABLE, separators=(",", ":")))
            .replace("__ICONS__", json.dumps(icon_names(), separators=(",", ":")))
            .replace("__ITEM_PLAIN__", json.dumps(ITEM_PLAIN)).replace("__ITEM_DEPTH__", str(ITEM_DEPTH)))


def check_bundle(bundle_js: str) -> list[str]:
    """The tags the wrappers use that the bundle does not define. The bundle defines an element with
    `customElement("<tag>")`, which esbuild keeps as the string literal."""
    return sorted({c["tag"] for c in COMPONENTS if f'"{c["tag"]}"' not in bundle_js})


def require_recorded_bundle(allow_stale: bool, bundle_root: Path | None = None, checkout: Path | None = None) -> None:
    """Unless the offline option is given, end the process when the bundle has no record matching this checkout's lock
    and entry file (NOTE-WFB-10 section 13 invariant 4)."""
    if not allow_stale:
        verify_pin.require_bundle_record(bundle_root or WEB, checkout or HERE / "web")


def main() -> int:
    verify_pin.require_pin()
    allow_stale = "--allow-stale-bundle" in sys.argv[1:]
    require_recorded_bundle(allow_stale)
    manifest = json.loads((PKG / "custom-elements.json").read_text(encoding="utf-8"))
    defaults = json.loads((HERE / "web/defaults.json").read_text(encoding="utf-8"))
    enum_map = enums()
    MANIFEST.clear()
    MANIFEST.update(manifest)
    DEFAULTS.clear()
    DEFAULTS.update(defaults)
    ITEM_TABLE.clear()
    ITEM_TABLE.update(build_item_table(manifest, COMPONENTS))
    bundle_js = (WEB / "dist/ob-components.js").read_text(encoding="utf-8")
    missing = check_bundle(bundle_js)
    if missing:
        print(f"the bundle {WEB / 'dist/ob-components.js'} does not define: {', '.join(missing)}")
        if not allow_stale:
            raise SystemExit("rebuild it (npm run build in module/web, then measure_defaults.py) or pass --allow-stale-bundle")
        print("WARNING: written with a stale bundle; rebuild the bundle, measure the defaults and run this again before "
              "building the module")
    shutil.copyfile(WEB / "dist/ob-components.js.LEGAL.txt", MOUNTED / "js/ob-components.js.LEGAL.txt")
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    contract, js_specs = {}, []
    for spec in COMPONENTS:
        d = {k: (None if v == "__undefined__" else v) for k, v in defaults[spec["tag"]].items()}
        decl = declaration(manifest, spec["tag"])
        schema, fields = schema_for(spec, decl, enum_map, d)
        (SCHEMAS / f"{spec['name']}.props.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        declared = {e.get("name") for e in decl.get("events", [])}
        for e in spec.get("itemEvents", []):      # an item event is declared by the item element the list builds, not by the host
            if not any(e in {x.get("name") for x in declaration(manifest, t).get("events", [])}
                       for t in ITEM_TABLE if t != spec["tag"]):
                raise SystemExit(f"{spec['tag']}: item event {e!r} is declared by no item element")
            declared.add(e)
        parts = part_specs(spec, enum_map)
        part_of = {e: i for i, pt in enumerate(parts) for e in pt["events"]}      # the events of a nested element
        events = []
        for dom in spec.get("events", []):
            if dom not in declared and dom not in part_of:
                raise SystemExit(f"{spec['tag']} declares no event {dom!r} in the manifest")
            name, kind, text = ALERT_EVENTS[dom]
            name = spec.get("eventNames", {}).get(dom, name)     # and name it (the navigation menu's `click` is `onItemClick`)
            text = spec.get("eventText", {}).get(dom, text)      # a component may word the event for itself
            kind = spec.get("eventKinds", {}).get(dom, kind)     # and change its payload (the alert menu's rows report their `id`)
            ev = {"dom": dom, "name": name, "payload": kind, **({"onItems": True} if dom in spec.get("itemEvents", []) else {}),
                  **({"custom": True} if dom in spec.get("customEvents", []) else {}),
                  **({"part": part_of[dom]} if dom in part_of else {})}
            props = PAYLOAD_PROPS[kind]
            if kind == "detail":
                rows = event_fields(spec, dom)
                props = {r["name"]: {"type": r["type"], **({"items": {"type": "string"}} if r["type"] == "array" else {}),
                                     "description": r["text"]} for r in rows}
                ev["fields"] = [{"name": r["name"], "type": r["type"], **({"from": r["from"]} if "from" in r else {})} for r in rows]
            if dom in spec.get("writeBack", {}):      # the component's own property follows the press (the element changes itself)
                field, key = spec["writeBack"][dom]
                if field not in schema["properties"]:
                    raise SystemExit(f"{spec['tag']}: writeBack names {field!r}, which is not a property")
                ev["write"], ev["from"] = field, key
            events.append(ev)
            (SCHEMAS / f"{spec['name']}.{name}.json").write_text(json.dumps(
                {"type": "object", "description": text, "properties": props}, indent=2) + "\n", encoding="utf-8")
        slots = slot_specs(spec, decl, set())      # the names were checked against the properties by `schema_for`
        items = [{"name": n, "tags": e["tags"], "slot": e.get("slot", "")} for n, e in spec.get("items", {}).items()]
        js_specs.append(js_spec(spec, fields, events, slots, items, parts))
        contract[spec["type"]] = {"element": spec["tag"], "title": spec["title"], "palette": spec["palette"],
                                  "schema": f"schemas/{spec['name']}.props.json",
                                  "defaultSize": spec["size"],
                                  "props": {k: {kk: vv for kk, vv in v.items() if kk != "description"}
                                            for k, v in schema["properties"].items() if k != "style"}}
        if slots:      # which properties are slot properties, for the test page and the frame (not part of the Perspective schema)
            contract[spec["type"]]["slots"] = {sl["name"]: {"slot": sl["slot"], "kind": sl["kind"]} for sl in slots}
        if items:
            contract[spec["type"]]["items"] = {i["name"]: {"tags": i["tags"], "slot": i["slot"]} for i in items}
        if parts:      # the nested elements the component renders itself, and the properties each carries
            contract[spec["type"]]["parts"] = {pt["tag"]: {"slot": pt["slot"], "props": [f["name"] for f in pt["fields"]]} for pt in parts}
        if events:
            contract[spec["type"]]["events"] = {e["name"]: {"element": e["dom"], "schema": f"schemas/{spec['name']}.{e['name']}.json"}
                                                for e in events}
        print(f"{spec['type']}: {len(fields)} properties, {len(spec.get('data', {}))} data, {len(events)} events from {spec['tag']}")
    zoom = CANVAS_ZOOM
    zschema = {"type": "object", "additionalProperties": False,
               "properties": {**{k: dict(v) for k, v in zoom["props"].items()},
                              "style": {"$ref": "urn:ignition-schema:schemas/style-properties.schema.json",
                                        "default": {"classes": ""}}}}
    (SCHEMAS / f"{zoom['name']}.props.json").write_text(json.dumps(zschema, indent=2) + "\n", encoding="utf-8")
    contract[zoom["type"]] = {"element": None, "title": zoom["title"], "palette": zoom["palette"],
                              "schema": f"schemas/{zoom['name']}.props.json", "defaultSize": zoom["size"],
                              "props": {k: {kk: vv for kk, vv in v.items() if kk != "description"}
                                        for k, v in zoom["props"].items()}}
    print(f"{zoom['type']}: {len(zoom['props'])} properties (web/canvaszoom.js)")
    canvas_zoom_js = (HERE / "web/canvaszoom.js").read_text(encoding="utf-8")
    wrappers = wrapper_script(js_specs)
    (MOUNTED / "js/cadre-ob.js").write_text(bundle_js + "\n" + wrappers + "\n" + canvas_zoom_js, encoding="utf-8")
    css, stats = scoped_css(bundle_js)
    (MOUNTED / "css").mkdir(parents=True, exist_ok=True)
    (MOUNTED / "css/cadre-ob.css").write_text(css, encoding="utf-8")
    (MOUNTED / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PKG / "dist/NotoSans.ttf", MOUNTED / "fonts/NotoSans-OB.ttf")
    (HERE / "components.json").write_text(json.dumps(contract, indent=1) + "\n", encoding="utf-8")
    print("stylesheet", stats, f"{len(css) / 1024:.0f} KiB")
    print("cadre-ob.js", f"{(MOUNTED / 'js/cadre-ob.js').stat().st_size / 1024:.0f} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
