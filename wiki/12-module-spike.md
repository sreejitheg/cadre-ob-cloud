---
title: Perspective module spike
type: wiki
updated: 2026-10-26
---
# 12 Assessment Report: Cadre HMI Components Module Spike

| Field | Value |
|---|---|
| Document ID | COB-WIKI-12 |
| Revision | F |
| Status | In review |
| Issued | 2026-10-07 |
| Prepared by | Cadre HMI Library, at the owner's request |
| Gateway | `Ignition-PCS_DEV_Station`, Ignition 8.3.6, Perspective 3.3.6, trial licence |
| Register | COB-070 (the spike); COB-071 to COB-075 (follow-up) |
| Decisions | COBD-011 |
| Outstanding inputs | N-COB-6 (Designer check); N-COB-5 decided 2026-10-09 |

## 1. Purpose and Scope

This report records a spike: a Perspective module of Cadre's own that wraps two package web
components, the pump and the tank, and the comparison of that module with the stock component
library of `cadre_hmi_base` on the same screens. It establishes whether such a module works on the
8.3.6 gateway, and what it changes in rendering, integration, page cost, deployment and effort.

Out of scope: components other than the pump and the tank; the reference "package for Ignition"
module, which is neither used nor installed; Designer editing tools; production signing and
release management.

## 2. Summary of Findings

1. **The module works on Ignition 8.3.6.** The package elements `obc-pump` and
   `obc-automation-tank` render inside Perspective, bind to tags, open the faceplate dock and
   follow the Cadre palettes. The water treatment sample rendered through the module passes every
   gate the stock rendering passes: G0 to G8, the functional walk G10 (9 of 9) and the faceplate
   sweep G11 (26 of 26 devices).
2. **The module draws the package detail that the stock library approximates.** The speed
   readout with its double chevron and hinted zeros, the alert frame around symbol and readout
   with its flap outside the corner, the tank vessel and value row, and the maritime type weights
   all come from the package's own code. Registered gaps COB-032, COB-033, COB-034 and COB-068 close
   for the wrapped components; COB-030 (medium size) becomes one property.
3. **The descriptors and the interface of the Cadre tools do not change.** One generator option,
   `--render module`, draws pumps and tanks with the module and every other kind as before.
4. **Page cost falls in components and rises in first-load transfer.** Pages with seven module
   symbols carry 54 to 67 per cent fewer Perspective components. Load time shows no established
   difference at this scale. A cold load transfers 754 KB more: the module's script, stylesheet and font.
5. **Deployment gains a restart.** Installing or upgrading a module registers a required gateway
   restart; the restart took about 90 s and interrupted every project on the gateway. The module
   is signed, and each gateway trusts its certificate once.
6. **The effort is small.** Three Java classes (142 lines) and a 301-line generator, which derives
   the property schemas, the browser wrappers and a scoped stylesheet from the package
   manifest. The first build took 5 min 41 s including the download of the software development
   kit; a full rebuild takes 13 s.

## 3. Background

The stock library redraws each package component from stock Perspective parts, using the
Package tokens and icons only; the remaining differences are registered. A Perspective module can instead host the pinned web components themselves, which are
Apache-2.0 at the release pinned by COBD-003. The owner asked for a spike on the pump and the tank,
compared with the current library, before any decision. The owner's field practice, adding a pump
or a button after handover, is the main operational concern (section 9).

## 4. Terms and Abbreviations

The terms below are used throughout the report.

Table 1. Terms and abbreviations.

| Term | Meaning |
|---|---|
| API | Application programming interface |
| CSS | Cascading Style Sheets |
| DOM | Document Object Model; the shadow DOM is the private element tree of a web component |
| EULA | End user licence agreement |
| JDK | Java Development Kit |
| HTTP | Hypertext Transfer Protocol |
| KB | Kilobyte, 1,024 bytes |
| MB | Megabyte, 1,048,576 bytes |
| Manifest | `custom-elements.json`, the machine-readable description of every package element |
| Module | An Ignition module (`.modl` file) installed on the gateway |
| REST | Representational state transfer; the gateway's HTTP API |
| SDK | Software development kit; here the Ignition 8.3.6 SDK |
| Stock rendering | The water treatment sample drawn with the library views of `cadre_hmi_base` |
| Module rendering | The same sample with pumps and tanks drawn by the module |
| G0 to G11 | The gates of page 08 section 5 |

## 5. Build

### 5.1 Module Structure

The module follows the Ignition SDK's minimal Perspective component example: a gateway hook
registers the components and serves the browser files, a designer hook adds them to the Designer's
component palette, and one script and one stylesheet carry the browser side. No Inductive
Automation npm package is needed: the script uses the `PerspectiveClient` and `React` objects that
the Perspective client exposes (GF-31).

Table 2. Module parts.

| Part | Content | Size |
|---|---|---|
| `module/common` | `CadreOb`: the two component descriptors and the browser resources | 50 lines |
| `module/gateway` | `CadreObGatewayHook`: registration, files served under `/res/cadreob/` | 61 lines |
| `module/designer` | `CadreObDesignerHook`: the "Cadre HMI Components" palette category | 31 lines |
| `mounted/js/cadre-ob.js` | The package pump and tank with their dependencies, then the generated wrappers | 544 KB, 138 KB compressed |
| `mounted/css/cadre-ob.css` | the package stylesheet, scoped and trimmed | 47 KB, 5 KB compressed |
| `mounted/fonts/NotoSans-OB.ttf` | the package's variable Noto Sans | 611 KB |
| `CadreHMIComponents.modl` | The signed module | 492 KB |

### 5.2 Generation from the package Manifest

`module/tools/gen_module_assets.py` reads the manifest of package 2.0.0-next.155 (285 custom
elements) and writes everything per element; adding an element is one entry in its list.

1. **Property schemas.** Each element attribute becomes a Perspective property with its type, its
   enumerated domain (read from the package's enum declarations) and its default (measured by
   creating each element in a browser, `measure_defaults.py`): 27 properties for the pump, 30 for
   the tank, plus `componentSize` and `style`. The schemas drive the Designer property editor, the
   gateway's validation, and gate G1.
2. **Wrappers.** One React wrapper per element renders the element inside the Perspective component
   box and copies the properties onto it; DOM events reach the component's event scripts.
3. **Stylesheet.** the package declares its palettes and sizes on `:root` and some variables on
   every element. Loaded as shipped, these rules would reach every page of a project. The generator
   keeps only the 216 of 2,828 variables the bundled elements use, declares them on the module's
   wrapper, and keys the palettes to the Cadre palette classes, so palette switching needs no
   script. The stylesheet falls from 777 KB to 47 KB.
4. **Font.** The variable Noto Sans shipped with package is served under its own family name,
   so the package weights 370 and 570 render exactly (GF-26) without changing any other text.

### 5.3 Signing and Installation

The module is signed with a self-signed certificate held outside the repository. Installation uses
the gateway's REST API, in the order the gateway's own code defines (GF-28):

1. Upload the file.
2. Read and accept the certificate.
3. Accept the EULA.
4. Install.
5. Restart the gateway; the module starts with it.

### 5.4 Generator and Gate Integration

The generator option `--render module` draws pumps and tanks with the module and translates the
library parameters (for example `speed` to `speedInPercent`). A pump's box is its 48 px symbol box
with the reference `symbol` positioning, so pipes meet it exactly; the default `point` positioning
draws the symbol 24 px off its anchor (GF-30). The faceplate dock contract moves to the
component's custom properties and a DOM click script. The gates follow:

1. G1 loads the Ignition-Wiki validator as a library and adds the module's components with their
   generated schemas to its registry; an undeclared module property fails the gate (unit test).
2. G5 checks module components by their symbol boxes.
3. G10 and G11 read the module pump's state from the element, because its text lies in shadow DOM.

## 6. Test Configuration

Both renderings were built from the same four descriptors (`screens/wtp/`), bound to the same
tags, and deployed as `cadre_hmi_wtp` (stock) and `cadre_hmi_wtpob` (module). Measurements used
Chromium through Playwright at 1,600 x 900 px. Page cost was measured over four cold loads per
page and rendering; the medians are reported. Ready time runs from navigation start until the
count of Perspective components has been stable for 800 ms.

## 7. Results

### 7.1 Gates

Table 3 lists the gate results of the two renderings.

Table 3. Gate results, both renderings pass every gate.

| Gate | Stock rendering | Module rendering |
|---|---|---|
| G0 to G7 offline | Pass | Pass, 22 module components validated against their schemas |
| G8 render, 5 routes | 0 error badges, 0 quality overlays | 0 error badges, 0 quality overlays |
| G10 functional walk | 9 of 9 | 9 of 9 |
| G11 faceplate sweep | 26 of 26 devices | 26 of 26 devices |
| Unit tests | 19 pass (both renderings in one suite) | |

### 7.2 Rendering

Figure 1 shows the intake page in both renderings; Figures 2 and 3 enlarge the symbols, stock on
the left and module on the right. The module draws the following differently:

1. **Pump readout.** A double chevron and hinted leading zeros (`080 %`), in the package weights.
2. **Alert frame.** The frame encloses the symbol and its readout, and the flap sits outside the top
   right corner; the stock frame encloses the symbol only.
3. **Tank.** Straight sides with small corner radii, a chevron trend mark, and the value and maximum
   at one size.
4. **Compact tank.** The readout sits below the vessel; the stock compact tile carries it inside.

Pipes meet the module pumps at the same points as the stock symbols. Figure 4 shows the module
rendering in the night palette: the package elements follow the Cadre palette switch.

![Figure 1](figures/12/fig1-intake-stock-vs-module.png)

Figure 1. The intake page, stock rendering (left) and module rendering (right): same layout, same
tags, package detail on pumps and tanks.

![Figure 2](figures/12/fig2-pump-and-tank-crops.png)

Figure 2. Pump P-101, tank TK-101 and compact tank TK-201: the module brings the package speed
readout, tank vessel and compact layout.

![Figure 3](figures/12/fig3-alert-frame-and-tank-crops.png)

Figure 3. Faulted pump P-502 and tank TK-501: the module's alert frame encloses symbol and readout
with the flap outside the corner.

![Figure 4](figures/12/fig4-module-night-palette.png)

Figure 4. The module rendering in the night palette with the faceplate open: the package
elements follow the Cadre palette.

### 7.3 Page Cost

Table 4 compares the page cost of the two renderings, medians of four cold loads.

Table 4. Page cost: fewer components with the module, no measurable change in ready time.

| Page | Rendering | Module elements | Perspective components | DOM elements | Ready time (ms) | JavaScript heap (MB) | Cold transfer (KB) |
|---|---|---|---|---|---|---|---|
| Overview | Stock | 0 | 287 | 863 | 773 | 28.6 | 2,815 |
| Overview | Module | 7 | 106 | 755 | 913 | 25.8 | 3,569 |
| Intake | Stock | 0 | 309 | 967 | 1,081 | 31.4 | 2,815 |
| Intake | Module | 7 | 143 | 835 | 847 | 26.3 | 3,569 |
| Filtration | Stock | 0 | 282 | 887 | 804 | 27.4 | 2,815 |
| Filtration | Module | 1 | 252 | 867 | 888 | 28.8 | 3,569 |
| Disinfection | Stock | 0 | 264 | 865 | 820 | 26.7 | 2,815 |
| Disinfection | Module | 7 | 87 | 737 | 907 | 24.8 | 3,569 |

The median ready times differ by 84 to 140 ms in favour of the stock rendering on three pages
and by 234 ms in favour of the module rendering on the intake page. The four runs of a page spread
over 88 to 596 ms, so four runs establish no difference in either direction. The DOM element
counts include the shadow DOM of the module's elements.

### 7.4 Asset Loading Scope

The module's script and stylesheet load on every page of a project that uses a module component,
including pages without one; the font loads only where text is drawn with it. Pages of other
projects load nothing of the module (GF-29). Table 5 records the measurement.

Table 5. Module assets by page.

| Page | Module assets loaded |
|---|---|
| `cadre_hmi_wtpob/intake` (module components) | Script, stylesheet, font |
| `cadre_hmi_wtpob/alerts` (no module component) | Script, stylesheet |
| `cadre_hmi_wtp/intake` (stock project) | None |
| `cadre_scada_pump/` (another repository's project) | None |

### 7.5 Deployment and Change Cycle

1. Installation needs five REST calls and a gateway restart (section 5.3). The restart took about
   90 s, and every project on the gateway was unavailable meanwhile.
2. An installed module stays inactive until the restart; uninstalling also takes effect at the
   next restart (GF-28).
3. A change to a component takes 13 s to rebuild in full and about 2 to 3 min in total to reach
   the screens, most of it the restart.
4. A module version must be a plain `major.minor.revision` number; a suffix such as `-spike` makes
   the gateway reject the file with an empty reply (GF-27).

## 8. Comparison by Criterion

Table 6 compares the two approaches criterion by criterion.

Table 6. Stock library and module compared.

| Criterion | Stock library | Module | Evidence |
|---|---|---|---|
| Fidelity to the stock elements | Approximation; gaps COB-030 to COB-034 and COB-068 | the package's own drawing for the wrapped elements | Section 7.2 |
| Behaviour of the element | What the library view implements | The package's states, animations and readouts | Section 7.2 |
| Palettes | Cadre palette classes | The same classes, through the scoped stylesheet | Figure 4 |
| Tags, faceplates, alarms | Working | Working, unchanged faceplates and alarm logic | Table 3 |
| Gates | G0 to G11 | G0 to G11, with G1 extended by the module schemas | Table 3 |
| Perspective components | 10 to 30 per symbol | 1 per symbol | Table 4 |
| Ready time | No measurable difference | No measurable difference | Table 4 |
| First-load transfer | Baseline | 754 KB more per project session | Table 4 |
| Installation | Project import, no restart | Module install with a gateway restart | Section 7.5 |
| Change to a component | Project import, no restart | Module rebuild and a gateway restart | Section 7.5 |
| Field placement of a pump | Embedded view with parameters | Palette component with a property editor (not yet verified in the Designer) | Section 11 |
| Field change of a symbol's drawing | Possible in the Designer | Only by a new module release | Section 9 |
| Maintenance | Perspective views | Java, the Perspective client API, and the package release | Section 10 |
| Licence | Package tokens and icons, Apache-2.0 | Package code as well, Apache-2.0 at the pin | COBD-003 |

## 9. Consequences and Recommendation

1. **Screens.** The module is the route to package fidelity for symbols; the stock library stays
   the route for gateways that cannot take a custom module. The descriptors serve both, so the
   choice can be made per project at build time.
2. **Field customisation.** Placing a pump or a button in the field stays possible: the module's
   components sit in the Designer palette with generated property editors (section 11 records the
   check outstanding). Changing how a symbol is drawn moves from the field to a module release.
3. **Operations.** Every module install or upgrade needs a planned gateway restart, which affects
   every project on that gateway. Releases should therefore be infrequent and bundled.
4. **Recommendation.** Adopt a hybrid: module rendering for the automation symbols, tanks and alert
   frames where the gateway accepts the module; stock rendering otherwise; the frame, faceplates
   and alarm logic unchanged in both. Before adoption, close the outstanding items of section 11
   and decide the signing route (COB-073).
5. **Decision.** The owner adopted the hybrid on 2026-10-09 (N-COB-5, COBD-022). Under module
   rendering it includes the module's alarm views of section 12, with the faceplate's alarm list
   display only (COBD-025).

## 10. Risks

Table 7 lists the risks the spike identified.

Table 7. Risks of the module route.

| Risk | Consequence | Mitigation |
|---|---|---|
| Each install or upgrade restarts the gateway | Downtime for every project on the gateway | Planned windows; bundle components; stock fallback |
| The Perspective client API (`PerspectiveClient`, React 18.2) changes in a later Ignition release | Wrappers fail to load | Build and test the module against each Ignition release before upgrade |
| A self-signed certificate is not accepted by a client's IT policy | Module not installable | A code-signing certificate issued to Cadre (COB-073) |
| Newer package releases are AGPL-3.0 for 180 days | Upgrades lag upstream or need a fork | Stay on Apache-2.0 releases (COBD-008); fork when a fix is needed |
| Element text lies in shadow DOM | Tests and styling reach it only through properties and exposed variables | Test through element properties (as G10 now does) |
| One module defect affects every project that uses it | Wider failure scope than a view defect | Gate every release with G1 to G11 on a test gateway |

## 11. Outstanding Items

Table 8 lists the items that remain before adoption.

Table 8. Outstanding items.

| Item | Owner | Register |
|---|---|---|
| Decided 2026-10-09: the hybrid (COBD-022) | Owner | N-COB-5 |
| Check the Designer: the "Cadre HMI Components" palette entries and the generated property editors (needs a Designer login) | Owner | N-COB-6, COB-072 |
| Map the remaining library parameters: readout toggle, `hasSpeed`, tank unit and medium | Cadre | COB-075 |
| Signing and release procedure: certificate, versioning, upgrade windows | Cadre | COB-073 |
| Further components: valves, motors, fans, the frame's top bar and alert menu | Cadre | COB-074 |

## 12. Version 0.2.0: Alarm Components

The overnight session of 2026-10-08 added the alarm list components of COB-078 to the module
(page 13 section 5) and installed version 0.2.0 with the first of two authorised restarts
(COBD-012). Table 9 records the change cycle as measured.

Table 9. The 0.2.0 change cycle.

| Step | Result |
|---|---|
| Browser bundle (`npm run build`, local, no download) | 546 KB to 761 KB with `obc-alert-list-details` and `obc-alert-list-page-small` |
| Assets (`gen_module_assets.py`) | Two components, one data property each, two and four events; scoped stylesheet 47 KB to 95 KB (400 variables kept) |
| Build (`module/tools/build_module.py`, Gradle offline, JDK 17) | The first, incremental build after the version change packaged the 0.1.0 jars under a 0.2.0 `module.xml`; found by inspecting the file before installing. A clean build gave 544,954 bytes, signed; the helper now always cleans |
| Offline check of the wrappers | A page with a stubbed Perspective client and a real element: four components registered, `alerts` read with `readArray`, times converted to `Date`, an ACK click fired `onAckClick` with the alert id |
| Install and restart | Upload, certificate, EULA and install through REST (GF-28); restart by REST at 22:00; module 0.1.0 stopped 22:00:17, 0.2.0 active 22:01:09, about 52 s, "Registered 4 Cadre HMI Components components" in the log (GF-32) |

Two findings from the first look on the glass:

1. **Layout.** The module's wrapper centres its element, which suits a symbol. A list was centred
   and sized to its content. The parent project's stylesheet now stretches the alarm elements,
   which needed no restart; the rule belongs in the module's stylesheet at its next release
   (COB-082), and version 0.2.1 carries it (section 13).
2. **the package's alarm semantics.** The list's mode `all` draws active alerts, and only mode
   `rectified` draws cleared ones; the small alert page has no rectified mode; a row offers ACK only
   for an active alert that is not acknowledged. The faceplate and the menu therefore add a list
   of the cleared alarms not yet acknowledged, so no alarm is hidden; such an alarm is acknowledged
   on the alerts page.

The same override mechanism now also draws the tank faceplate's tile with the module's tank
(`Faceplate/TankTile`, page 13 section 8): until then the faceplate showed the library tank beside
the module's tank on the diagram.

On 2026-10-09 the owner decided where alarm actions are taken (COBD-025): on the alerts page, in
the top bar's alarm menu and with the top bar's ACK. The faceplate's module alarm list becomes
display only, listing the device's active and unacknowledged alarms. The second session removed
its ACK on 2026-10-09 without a module change: the records carry the pin's own `noAck` field, which
the wrapper passes through, and the list carries no acknowledge event (page 13 section 6).

## 13. Version 0.2.1: The Alarm Lists' Layout Rule

The second session of 2026-10-09 released version 0.2.1 (COB-082) with the owner's agreement to its
restart, given in the session. It moves the rule that makes an alarm list fill its component box,
top aligned, from the parent project's stylesheet into the module's own (`gen_module_assets.py`
appends it to `cadre-ob.css`); the parent's stylesheet no longer names the module's elements. The
display only faceplate tab of COBD-025 needed no module change: the records carry the pin's `noAck`
field, which the wrapper passes through (page 13 section 5). Table 10 records the change cycle as
measured.

Table 10. The 0.2.1 change cycle.

| Step | Result |
|---|---|
| Rollback copy | The installed 0.2.0 file kept outside the repository, `C:\Users\pcs_d\.cadre\modules\<module name>-0.2.0-installed-2026-10-08.modl` (544,954 bytes, SHA-256 beginning `776929DC`) |
| Browser bundle (`npm run build`, local) | Unchanged in content, 742.7 KB |
| Assets (`gen_module_assets.py`) | The four components as before; the scoped stylesheet gains the eight line rule (95,179 to 95,397 bytes as served) |
| Build (`module/tools/build_module.py`, clean, offline, JDK 17, signed) | 545,614 bytes, SHA-256 beginning `4EB5B5CA`; `module.xml` 0.2.1 with `common-0.2.1.jar`, `designer-0.2.1.jar` and `gateway-0.2.1.jar`, inspected before installing; a copy kept beside the 0.2.0 file |
| Install (REST, GF-28) | Upload 200; the certificate and the EULA answered 409, already accepted; install 200; enable 200; `/restart-tasks/pending` listed "Module Upgraded: cadre.hmi.ob" |
| Restart (REST, 2026-10-09) | Requested 23:48:46; 0.2.0 shut down 23:48:48; Ignition started 23:49:01; 0.2.1 started and "Registered 4 Cadre HMI Components components" 23:49:38; `/modules/healthy` reported 0.2.1 ACTIVE at 23:49:39, about 51 s after the request |
| Proof | In new sessions from 00:09 to 00:38 on 2026-10-10: both renderings G8 6 of 6 routes (0 overlays), G11 44 of 44, G10 15 of 15 (stock) and 19 of 19 (module), signed in; the sample and the demo G8 and G11. The module's lists fill their box from its own stylesheet: 368 by 712 px in the faceplate's dock and 624 by 356 px in the alarm menu, `align-self` stretch, with the parent's stylesheet no longer carrying the rule |

## 14. Version 0.3.0: Device Components

Version 0.3.0 (COB-074, COB-075, COB-110) lets a migrated project draw its devices with the module
wherever a pinned package component fits. The owner's direction of 2026-10-21 asked for it after the
pilot's first render drew none of its 74 devices with the module. It adds four components and three
properties of the module's own, in one release and one restart.

Table 11 lists the components. Each wraps the pinned element (2.0.0-next.155) through the same wrapper as
the pump and the tank: the property schema is generated from the custom elements manifest, and a symbol
is drawn in `symbol` positioning, so the descriptor's box is the 48 px symbol.

Table 11. Components of version 0.3.0.

| Component | Element | Library kind | Notes |
|---|---|---|---|
| `cadre.ob.motor` | `obc-motor` | `motor` | Same properties as the pump, including `hasSpeed` |
| `cadre.ob.fan` | `obc-fan` | `fan` | No vertical artwork: a vertical fan stays on the library's view |
| `cadre.ob.valve` | `obc-digital-valve` | `valve` | Variants `regular` and `flat` only; others stay on the library's view |
| `cadre.ob.analogvalve` | `obc-analog-valve` | `analogvalve` | As the valve; its opening is `value` |

The damper stays out: the element states its orientation as `orientation` and its variant as `square`,
which the generator would have to translate value by value (COB-074 stays open for it).

Three properties belong to the module, not to the element (`gen_module_assets.py`, `EXTRA`), and lift the
cases of COB-110. `hasSpeed` (pump, motor, fan; default true) leaves the speed readout out while the
state readout stays: the wrapper clears the element's two speed properties, which is what makes it print
none. `unit` (tank; default `m³`) fills the element's `unit` slot with the unit of the level. `hasCapacity`
(tank; default true) empties the `readout` slot of a static tank, so a vessel that states no capacity
draws the vessel and its tag only. The generator states these with the library contract's default where a
descriptor gives none (`screen.MODULE_STATE`), since the component's own default differs from the library
view's. With them `MODULE_NEEDS` and `MODULE_EXCEPT` shrink to two cases the component cannot show: a valve
variant outside `regular` and `flat`, a vertical fan, and a tank that asks for decimals
(`valueFractionDigits` other than 0, which the element does not print).

Open: a fixed status text (`statusText`) is not mapped, as before for the pump; a hidden status row
(`showStatus`) is mapped since version 0.3.2 (section 16). Version 0.4.0 maps both on the pump, motor and fan
(section 17). Instruments, controllers, indicators and sequences
keep the library's views (COB-126).

Table 12. The 0.3.0 change cycle.

| Step | Result |
|---|---|
| Unit tests and gates G0 to G7 | 302 unit tests pass; G0 to G7 pass on the module rendering of the sample |
| Build (`build_module.py`, clean, offline, JDK 17, signed) | 558,085 bytes, SHA-256 beginning `EA890451`; `module.xml` 0.3.0 |
| Install (REST, GF-28) | Upload 200; install 200; enable 200; pending "Module Upgraded: cadre.hmi.ob" |
| Restart (REST, 2026-10-21) | Requested 13:15:46; the module ACTIVE and serving the new 838,395 byte script at 13:17:16 |
| Proof | One combined run on `cadre_hmi_wtpob` in one trial window: G8 on 6 of 6 routes with 109, 90, 180, 90, 161 and 58 components and no overlay or error badge; G11 44 of 44; G10 19 of 19 signed in; the walk N 8, D 5, T 3, C 15, R 15, A 2 with 15 refusals by the gateway; the plant restored on 219 tags. Its first run stopped in G10, because the glass looked module symbols up by pump only, fixed and rerun (COB-110) |

## 15. Version 0.3.1: Instrument Components

Version 0.3.1 (COB-127) lets a migrated project draw the library kinds `readout` and `instrument-field` with
the module wherever the pinned package element (2.0.0-next.155) shows the symbol truthfully. It adds two
components, both wrapped through the generated wrapper of the earlier components (the property schema comes
from the custom elements manifest), and no property of the module's own.

Table 13. Components of version 0.3.1.

| Component | Element | Library kind | Notes |
|---|---|---|---|
| `cadre.ob.readout` | `obc-transmitter` | `readout` | `type` value; the identifier is `idTag`; `lineType` and `data` are not offered |
| `cadre.ob.instrumentfield` | `obc-instrument-field` | `instrument-field` | The label is the element's `tag`; no source |

The elements were chosen from the pinned package. `obc-automation-readout` does not fit the readout: it prints
`value.toFixed(0)` and has no tag. The transmitter prints the value in a chip with its unit and an optional
identifier beneath. `obc-transmitter-button`, which the register item first suggested for the field, is the
chip alone; the library's `Instrument/Field` was modelled on `obc-instrument-field` (sizes `regular` and
`enhanced`, a setpoint line, the caption of tag and unit, `center`), so the field uses that element. The
element carries a deprecation note in its declaration; the pinned package still ships it, and the choice
stands until a successor takes the same properties.

### 15.1 The generator's rules

The renames and drops are in `screen.MODULE_PARAM` and `MODULE_DROP`; the rules for what stays on the library's
view are in `MODULE_NEEDS`, `MODULE_EXCEPT` and `module_digits`, and the first two are published in the library
profile as before (new values, no new key).

1. The label of a field is the element's `tag`. A readout's tag is its `idTag`, and only when `hasTag` is true,
   as the library draws it. The field's own `tag` and `source` are drawn by neither the library's view nor the
   component.
2. A number format becomes `fractionDigits` (`screen.fraction_digits`): `#,##0` is 0, `#,##0.0` is 1, `0.00` is 2.
   A pattern the element cannot print the same way (a percent, an exponent, literal text, an optional digit)
   keeps the library's view. A field with a setpoint has one digit count for both numbers, so a `setpointFormat`
   with other digits keeps the library's view.
3. `align` `end` is the element's own layout and `center` is the element's `center`. The element's value and
   caption rows end at the end of the element and it has no start layout, so `start` keeps the library's view.
4. The enhanced field with a setpoint keeps the library's view: it is 6 px higher than the library's box. More
   generally, a readout or a field whose box (`symbol_box`, as the generator draws it) is more than 4 px shorter than
   its element keeps the library's view (`screen.module_height`, `MODULE_SHORT`): 26 px for the readout, 44 px with
   its identifier; 40 px for the field, 52 px enhanced, 60 px with a setpoint. Gate G5 does not look at a module
   component's height, so the generator does. The generator grows a readout's box to the library's size, which is
   within 4 px of the chip, so the rule takes a field in a short box and never a readout. A symbol in a card has
   no box of its own (the card lays it out) and is not judged. The rule is not published in the library profile.
5. A symbol with a device opens the faceplate of the kind its `deviceKind` names (default `instrument`; a
   controller's process value names `controller`), titled with `tag` or else `label`, as `library.SELECT_INSTRUMENT`
   does.
6. A bound `value` or `setpoint` is its binding alone (GF-61). An unbound value is stated with the contract's
   default (0), since the element prints dashes for none.
7. Both components fill the box the descriptor and the library contract give (`symbol_box`, the contract's
   `sizes` and `grows`), so the library profile keeps its shape and gate G5 keeps its numbers. A readout's anchor
   is `symbol-centre`, but it is not a 48 px symbol and is not drawn in `symbol` positioning.

### 15.2 Measured facts

`module/tools/measure_instruments.py` measures the elements offline, in a page that holds the built bundle, the
module's stylesheet and the rules the wrapper adds (`module/web/instruments.json`).

Table 14. What the elements draw (regular component size).

| Fact | Result |
|---|---|
| Identifier of the readout | `idTag` draws it beneath the chip; `tag` draws nothing in a `value` chip (it is the pill text of type `indicator`) |
| Thousands | Neither element groups them: 1,234.5 in the library is `1234.5` in the module. A pattern without grouping (`0.0`) prints the same text |
| Readout chip | 26 px high, against the library's box of 24 px; with an identifier 44 px, against 40 px |
| Readout width | Narrower than the library's allowance for the same text in every case measured (for example 97.3 px for `1234.5 m3/h`, against 114.5 px); the identifier is narrower than the library's for every length |
| Field height | 40 px (regular), 52 px (enhanced), 60 px (regular with setpoint), 72 px (enhanced with setpoint) in boxes of 64 px and, for the last, 66 px |
| Field width | Caption of nine characters 73.4 px, of thirteen 91.3 px (the library allows 97.5 px for thirteen); a value of eight characters 84.4 px; an enhanced value of eight characters 157.6 px, beyond the 96 px box, as the library's 34 px value is |
| Field rows | Value and caption end at the end of the element; the element's `center` centres the caption only |
| Alignment `end` | The wrapper places the element at the end of its box; the value ends 4 px inside the edge |

Two things the element does that the box does not use as it stands are changed by the wrapper, in the element's
shadow root (`gen_module_assets.SHEETS`), and nowhere else. The transmitter hangs from a line by a leader line,
offsetting itself by half its width and 8 px; the wrapper removes the offset and the leader line so that the chip
lies centred in its box as the library's readout does. The field's `center` moves only its caption; the wrapper
centres the value and the setpoint with it.

The readout and the field exceed the library's box in height by 2 to 6 px (Table 14). The module component's box
does not clip (the pump's readout lies outside its 48 px box), so nothing is cut, and the cases up to 4 px stay on
the module. The enhanced field with a setpoint, 6 px over, stays on the library's view. The width of a live value
is not known when the page is built; the element needs less width than the library's allowance for the same
characters in every case measured, so a value that fits the library's block fits the component.

Open: a fixed status text and a hidden status row are not part of these two kinds. The deprecation of
`obc-instrument-field` is the package's; a replacement is a change of element, not of the generator's rules.
The walk reads the element's `value` and `setpoint` (`walk_plan.MODULE_PROP`) and the glass finds a readout by its
`idTag` and a field by its caption (`glass.SYMBOL_AT`, `READOUT_AT`).

Table 15. The 0.3.1 change cycle, to the point reached.

| Step | Result |
|---|---|
| Unit tests and gates G0 to G7 | 325 unit tests pass; G0 to G7 pass on the module rendering of the sample (`cadre_hmi_wtpob`), 11 readouts and 7 fields drawn by the module, none on the library's view |
| Review | One independent review of the whole diff before the build (COBD-041): two major findings (gate G10's check F3 looked a readout up by its library view; a field in a box shorter than its element overlapped its neighbours, unseen by G5) and a stylesheet defect (`--obc-can-hover` undefined, so a hovered chip lost its fill), each fixed with a unit test that failed first |
| Build (`build_module.py`, clean, offline, JDK 17, signed) | 601,307 bytes, SHA-256 beginning `9762E514`; `module.xml` 0.3.1 |
| Install (REST, GF-28) | Upload, certificate and EULA (already accepted, 409), install 200, enable 200; pending "Module Upgraded: cadre.hmi.ob" |
| Restart (REST, 2026-10-22) | Requested 08:16:32; the module ACTIVE and serving the new 983,924 byte script at 08:18:17, about 1 min 45 s; the 0.3.0 rollback copy is `C:\Users\pcs_d\.cadre\modules\<module name>-0.3.0-installed-2026-10-21.modl` |
| Deploy | `cadre_hmi_wtpob` imported, the tag model 261 of 261, from a build byte-identical to the committed one |
| Proof | One combined run of `wtp_suite.py` on `cadre_hmi_wtpob`, after the restart: G8 on 6 of 6 routes with 81, 84, 162, 81, 161 and 58 components and no overlay or error badge (fewer than under 0.3.0, since a readout or field is now one component); G11 44 of 44; G10 19 of 19 signed in, its check F3 reading the module readout FIT-101; the walk N 8, D 5, T 3, C 15, R 15, A 2 with 15 refusals by the gateway; the plant restored on 219 tags, none different. The readouts draw as package chips with the identifier beneath (`workspace/wtp/suite-0.3.1/`, local) |

## 16. Version 0.3.2: The State Readout Switch

Version 0.3.2 (COB-151) lets the diagram toolbar's Readout button reach the symbols the module draws. The owner
found on 2026-10-22 that the button hid the state readout of some devices and left others as they were: it was
bound to the library views' `showStatus`, and the module's pump, motor, fan and valves had no such property. The
pinned elements have one: `showStatus`, a field of the automation button that every one of the five inherits
(default true), which empties the state readout (On or Off, the speed, the opening) and keeps the identifier. The
element declares it with no attribute, so the asset generator, which reads the manifest's attributes, had never
offered it. `gen_module_assets.PROPERTIES` now lists such fields, and each component names the ones it carries;
the wrapper sets them on the element as it sets every other field. The generator binds the component's
`showStatus` to the toolbar's `showReadout` as it binds the library view's (`screen.toolbar_flag`), and passes a
descriptor's own `showStatus` where a page has no toolbar.

Table 16. The 0.3.2 change cycle.

| Step | Result |
|---|---|
| Unit tests and gates G0 to G7 | 325 unit tests pass; G0 to G7 pass on `cadre_hmi_wtpob` |
| Measured before the release | Gate G10's new check F20 on module 0.3.1 failed as the owner reported: Readout off hid the state of the library's filters F-301 to F-303 and left the module's P-301 and XV-301 to XV-303 as they were; the property bound on 0.3.1 drew no error badge (GF-72) |
| Review | One independent review of the whole diff after the build: no defect in the fix; the hardening it asked of G10's checks F20 and F21 and of the generator's library embeddings (GF-61) touches no file of the module |
| Build (`build_module.py`, clean, offline, JDK 17, signed) | 601,826 bytes, SHA-256 beginning `3E32290D`; `module.xml` 0.3.2; `showStatus` in the five schemas and in the wrapper |
| Install (REST, GF-28) | Upload 200, EULA already accepted (409), install 200, enable 200; pending "Module Upgraded: cadre.hmi.ob"; the 0.3.1 rollback copy is `C:\Users\pcs_d\.cadre\modules\<module name>-0.3.1-installed-2026-10-22.modl` |
| Restart (REST, 2026-10-22) | Requested 14:42:48; the module ACTIVE and serving the new 984,074 byte script with `showStatus` at 14:45:30, about 2 min 42 s; nothing left pending |
| Proof | One combined run of `wtp_suite.py` after the restart: the suite on `cadre_hmi_wtpob` passed, 14:45:39 to 15:09:53 (G8 on 6 of 6 routes with 85, 88, 166, 85, 165 and 62 components and no overlay or error badge; G11 44 of 44; G10 21 of 21 signed in, F20 with all seven symbols of `/filtration` hiding and showing their state and nine flowing pipes coloured and back, F21 with both menus closed both ways; the walk N 8, D 5, T 3, C 15, R 15, A 2 with 15 refusals by the gateway; the plant restored on 219 tags, none different) |

## 17. Version 0.4.0: Device Status, Duty and Out of Service Marks, Stretching Readout, Canvas Zoom

Version 0.4.0 is the module's part of eng02 ASM Level 4 (the owner's decision D17: one release and one gateway
restart). It closes the open item of sections 14 and 15 (a fixed status text and a hidden status row), moves the duty
badge and the out of service look from the library's view to the module's pump, motor and fan, lets the module readout
fill its box, and adds one component that scales only the canvas. The interface is fixed by the Level 4 contract
(3.1 and 3.2); the generator and the screen builder emit it in parallel. Nothing in this section is proved on the
gateway yet: section 17.5 lists what only the gateway can show.

### 17.1 The Owner's Findings

Table 17. Findings and their cure.

| Finding (2026-10-24) | Cause measured in the pinned element | Cure |
|---|---|---|
| The pump readout does not show the ON status and does not mute when the readout is deselected in the panel | `obc-pump`, `obc-motor` and `obc-fan` draw their status from `extraReadouts`: the speed while they run, the word Off while they stand, nothing for a running symbol with no speed. The element has a `showStatus` property that returns no readouts at all, but it is declared without an attribute, so the generated schema never offered it. `readoutPosition` and `labelDirection` only move the readout | `showStatus` and `statusText` on the three components (17.2) |
| Use package modules wherever possible: the duty badge and the out of service look must move from the library view to the module pump | The element draws four corner badges from its own properties and has no duty property; its `interlock` badge is drawn with the duty icon | `badgeDuty` and `outOfService` (17.2) |
| Text boxes grouped in a column or a row keep one length and size | `obc-transmitter` is `width: fit-content`, and its chip is as wide as its text, centred in the box | `stretch` on the readout (17.3) |
| Pinch or any zoom scales only the canvas | A browser zoom scales the whole frame | `cadre.ob.canvaszoom` (17.4) |

### 17.2 Device Properties

The properties belong to the module, not to the element, as `hasSpeed` does (`gen_module_assets.py`, `EXTRA`). They
exist on `cadre.ob.pump`, `cadre.ob.motor` and `cadre.ob.fan`, and on no other component.

Table 18. Device properties of version 0.4.0.

| Property | Type, default | Behaviour |
|---|---|---|
| `showStatus` | boolean, true | Passed to the element's own `showStatus`. False hides every status readout the symbol draws: the word Off while it stands, and the speed readout while it runs. The tag stays. Deselecting the readout in the panel therefore mutes the symbol with this one property |
| `statusText` | string, "" | When not empty, the one word drawn in the element's status place, with the element's state icon (the On icon for a running symbol, the Off icon for a standing one), in place of the element's own readouts. It does not draw while `showStatus` is false. Empty keeps the element's own readouts |
| `badgeDuty` | boolean, false | An `obc-automation-badge` of type `interlock`, which package draws with the duty icon, in the first free corner slot: bottom left, bottom right, top left, top right, in that order, a slot being taken when its own badge property is not `none`. Not drawn while `badgeInterlock` is `interlock`, which is the same icon |
| `outOfService` | boolean, false | A veil of the container background colour at 72 per cent opacity and the word OOS, 48 px square, centred on the component box (the 48 px symbol in `symbol` positioning), taking no pointer. It is the library view's veil and word (`tools/hmi/library.py`, `_out_of_service`) |

Decisions and differences from the library view, for the reviewer:

1. **The library's duty mark sits between the interlock and command locked badges.** The element has four corners only,
   so the duty badge takes a free corner. A symbol that carries several badges at once may show the duty badge in a
   corner the library would have left to another badge; the order above keeps the bottom row first, as the library does.
2. **`statusText` replaces the readouts; it does not add a row.** The library view's status row also shows one text
   (`statusText` when given, else the speed or On or Off). A mapped screen therefore passes `statusText` where the library
   passes its own, and an empty one where the library shows the speed.
3. **The veil lies over the whole element, badges and alert frame included.** The library places it under them. Drawing
   under the element's badges would need a change inside its shadow root; the veil takes no pointer, so the symbol's
   click and the faceplate dock work as before.
4. **`showStatus` false also hides the speed.** The element's own property does both. A symbol that shows a speed but no
   word uses `hasSpeed` as before and leaves `showStatus` true.

### 17.3 The Stretching Readout

`stretch` (boolean, default false) on `cadre.ob.readout`. When true the wrapper sets `data-stretch` on the element and on
the chip inside it. Three rules then apply: the host, the transmitter and its content are 100 per cent wide (a rule in the
element's shadow root, added as the existing rules are); the chip's own shadow root gets a rule that makes its button fill
the chip; and the module stylesheet makes the element fill the wrapper. The value and the unit stay centred in the chip and
the identifier stays centred beneath it. Readouts of equal boxes then show equal widths. The chip's shadow root is reached
after the element's first update and again after each later one, because an alert frame around the readout draws a new chip.

The generator keeps its height rules (section 15.1, rule 4): the readout's box height is unchanged.

### 17.4 The Canvas Zoom Component

`cadre.ob.canvaszoom` is a leaf component with no package element. Its browser side is `module/web/canvaszoom.js`, which
`gen_module_assets.py` appends to `cadre-ob.js` after the wrappers; its schema and contract entry are generated beside the
others (`element` is null in `components.json`). It draws a zero sized, hidden box. The stock screens place it as the last child
of the canvas, with `zoom` bound two ways to the view's `zoom` custom property.

Table 19. Properties of the canvas zoom component.

| Property | Type, default | Meaning |
|---|---|---|
| `zoom` | number, 1 | The scale. The component writes it (`store.props.write('zoom', value)`, GF-38); the view binds it two ways |
| `min` | number, 0.5 | The smallest zoom |
| `max` | number, 4 | The largest zoom |
| `targetDomId` | string, `cadre-canvas` | The DOM id of the scrolling canvas, found with `document.getElementById` (Perspective's `meta.domId`) |
| `guardBrowserZoom` | boolean, true | Prevents the same gestures elsewhere on the document, and on touch devices sets `maximum-scale=1` on the viewport meta |

Behaviour:

1. **Gestures.** Ctrl and the wheel over the target (a trackpad pinch arrives as the same event), a two finger pinch (touch
   events on touch devices, pointer events for a pen), and Ctrl with plus, equals, minus or 0 (and the numeric keypad's keys).
   One mouse wheel notch is one step of 1.25 times; a trackpad's small deltas scale smoothly; Ctrl and 0 return to 1. The
   zoom is clamped to `min` and `max`.
2. **The point under the pointer stays.** Before the first change of a burst the component records the target's scroll and
   the pointer's position in it. The new scale reaches the screen after the gateway round trip, so the component waits until
   the target's scrollable size changes and then sets `scrollLeft` and `scrollTop` to `(scroll + p) * ratio - p` every
   frame until the size has settled (at most about a second), where `p` is the pointer's offset in the target and `ratio` is
   the new zoom over the zoom at the start of the burst. Successive events of a burst compound at once, ahead of the echoed
   property.
3. **The guard.** With `guardBrowserZoom`, a Ctrl and wheel event anywhere on the document, a two finger touch move anywhere
   and Safari's `gesturestart` and `gesturechange` are prevented, so the browser never zooms the frame. The listeners are
   non-passive and in the capture phase, so that `preventDefault` is honoured. On a touch device the viewport meta gains
   `maximum-scale=1`, and the target takes `touch-action: pan-x pan-y`, which keeps one finger panning and gives the pinch to
   the script. Touch listeners are added only where the browser has touch, since a non-passive touch listener makes it wait.
4. **Unmount.** Every listener, the animation frame, the viewport meta and the target's `touch-action` are put back.

### 17.5 Verification

Table 20. What was verified offline and what only the gateway can show.

| Check | Where | Result |
|---|---|---|
| Contract, schemas and written files agree; every new property has its default; the script carries the listeners and their removal; the version | `tests/test_module.py` (21 tests) | Pass |
| The three devices: Off drawn and muted; `statusText` drawn, replaced and muted; speed muted; duty badge in the free corner and not beside the interlock badge; veil 48 by 48 with OOS | `module/tools/harness/devices.mjs`, real package elements in Chromium with a stub Perspective client | 45 of 45 checks pass |
| Readout stretch: widths differ without it, and a 49 px and a 97 px chip both measure 160 px in a 160 px box with it | same | Pass |
| Zoom: Ctrl and wheel, a burst of five notches (1.25 to the power 6), the clamps at 0.5 and 4, the keys, the guard on and off, the pen and touch pinch, the point under the pointer within 2 to 3 px with a simulated 90 ms round trip, the viewport meta, unmount | `module/tools/harness/zoom.mjs` | 38 of 38 checks pass |
| Compile | `gradlew clean build --offline` under JDK 17, unsigned, not installed | Build successful; `module.xml` 0.4.0 with `common-0.4.0.jar` carrying `schemas/canvaszoom.props.json` |

Only the gateway can show: that `store.props.write` reaches a two way binding and returns the value (the stub only records
it); that Perspective gives the canvas the DOM id `cadre-canvas` and does not clip the zero sized component; that the
Designer lists the component and the new properties; that the veil and the duty badge sit well on a real page in each
palette; that a phone or tablet pinch is handled as in the harness (the harness dispatches synthetic touch events); and that
no Perspective handler on the page reacts to Ctrl and wheel before the guard (the listeners are in the capture phase, on the
document, ahead of the page's own).

### 17.6 Release Steps

The orchestrator runs these, from the repository root, in PowerShell. Installing needs a gateway restart (GF-28): ask the
owner first.

1. Merge `eng02/l4-module` and the other Level 4 branches. The version is already 0.4.0 in `module/build.gradle.kts`
   (GF-27: plain `x.y.z`).
2. `cd module\web; npm ci; npm run build`, then `cd ..\..; python module\tools\gen_module_assets.py`. The committed files under
   `module/` are regenerated by these two steps; they should give no difference.
3. `python tests\test_module.py` and `python -m unittest discover -s tests`.
4. Optional offline check of the browser side: `node module\tools\harness\devices.mjs` and `zoom.mjs` (README beside them).
5. Keep a rollback copy of the installed 0.3.1 file outside the repository, as sections 13 to 15 did.
6. `python module\tools\build_module.py` (clean, offline, JDK 17, signed); inspect `module.xml` for 0.4.0 and the three jars
   of 0.4.0, as section 12 recorded.
7. `python module\tools\install_module.py` (upload, certificate, EULA, install; then the enable call of section 15 if the module is not enabled), then the gateway restart through
   `POST /restart-tasks/restart?confirm=true`, with the owner's approval.
8. Check the gateway log for "Registered 11 Cadre HMI Components components" and `/modules/healthy` for 0.4.0 ACTIVE.
9. Rebuild and import the screens that use the new properties, and run G8, G10 and G11, then look at the component test page
   and the pages with zoom in a new session (GF-10).

### 17.7 Version 0.4.1: the Measured Canvas

On the gateway (2026-10-24) a fitted page left the faceplate dock's 400 px empty after a reload with the dock closed:
the session's flag `faceplateDocked` outlives a reload, because the gateway keeps the page and starts no view again
(GF-94), and it is shared by every tab of a session. Version 0.4.1 gives the canvas zoom component two properties,
`viewWidth` and `viewHeight` (number, default 0): the component measures its target with a `ResizeObserver` and
writes the box whenever it changes by a pixel or more; the generator binds them two ways to `view.custom.canvasW`
and `view.custom.canvasH`, and the fit reads them where they are measured (wiki 04 section 8.11). Installed on
2026-10-24 (restart 07:38 UTC); every Level 4 fill and zoom gate passes on it.

### 17.8 Version 0.4.2: Row Selection of the Alarm Lists

Version 0.4.2 is the module's part of eng02 ASM Level 5 (the owner's decision D25): the alarm lists gain a tick box on
each row, so that the library can offer "Ack selected" beside "Ack all". The interface is fixed by the Level 5 contract
(3.5); the library emits it in parallel, and only where the module's schema lists the properties.

Table 21. Properties of version 0.4.2, on `cadre.ob.alertlist` and `cadre.ob.alertpanel` only.

| Property | Type, default | Behaviour |
|---|---|---|
| `selectable` | boolean, false | True gives each row a tick box as its first cell. False leaves the component exactly as in 0.4.1: the same markup and the same events, and nothing is written |
| `selectedIds` | array of strings, [] | The ids of the selected rows. The component writes it when a tick is toggled (`store.props.write('selectedIds', ids)`, as the canvas zoom writes `zoom`), and the view binds it two ways. The ticks show the ids it holds |

Events are unchanged: `onRowClick`, `onAckClick` and, on the panel, `onSilenceClick` and `onAckAllClick`, with the payloads
of section 12. Selection has no event of its own: a view reads `selectedIds`.

Behaviour:

1. **The tick is the package's own.** The package's table (`obc-table`, which both lists draw) has a selection column built
   from `obc-checkbox`, switched on by its `selectable` property, fed by `selectedRowIds` and reporting a toggle as
   `selection-change`. The alert list sets none of the three. The wrapper sets them on the table inside the list (the panel
   nests the list in its shadow root), so no new element is bundled, the bundle is unchanged and the tick has the theme's
   own look, with the selected row highlighted. The full list also draws a select all tick in its header, which selects the
   rows shown; the panel has no header and no such tick.
2. **A tick click selects and nothing else.** The table stops the click of its tick box and ignores clicks that pass through
   a checkbox, so `onRowClick` is not fired. A click anywhere else on the row fires `onRowClick` as before and leaves the
   selection alone. The ACK button of a row still fires `onAckClick`.
3. **A toggle shows at once.** The wrapper keeps the ids, ticks the box on the click and writes `selectedIds`. The value that
   returns through the binding is recognised as the wrapper's own write and ignored, so two quick clicks cannot undo each
   other; a value that is not the wrapper's own, such as the library clearing the selection after an acknowledgement,
   replaces the selection and writes nothing back.
4. **Stale ids are dropped.** After each draw the wrapper removes from `selectedIds` every id whose row the list does not show:
   an alert that has left `alerts`, and also an alert the selected mode hides (for example an acknowledged alert under the
   Unacked tab). The second case goes beyond the contract's wording (ids no longer in `alerts`); it keeps "Ack selected"
   from acting on a row that is not on the screen. Switching back to a mode that shows the row does not bring the tick back.
   An empty list empties `selectedIds`.
5. **Switching `selectable` off** restores the table's own state (no tick column, `selectedRowIds` unset); the markup then
   differs from 0.4.1 only in the spacing of one class attribute.

Verification, table 22.

Table 22. What was verified offline and what only the gateway can show.

| Check | Where | Result |
|---|---|---|
| Contract, schemas, written script and version agree; the props exist on the two lists only, with their defaults | `tests/test_module.py` (class `AlertRowSelection`) | Pass |
| List and panel in Chromium with real package elements and real mouse clicks: no tick when `selectable` is false (same markup, no write, row click fires); a tick per row, checked for the ids held; toggle writes the ids and fires no row click; a click on the middle of the tick cell likewise; a click elsewhere fires `onRowClick` and keeps the selection; ACK button; two quick toggles with a 150 ms echo; an outside change; stale ids (an alert gone, an empty list, a mode that hides the row); `selectable` off and on; select all on the list | `module/tools/harness/alertselect.mjs` | 69 of 69 checks pass |
| Earlier harness pages | `devices.mjs`, `zoom.mjs` | 45 of 45 and 38 of 38 (the zoom stub no longer takes the 0.4.1 `viewWidth` write for a scale) |
| Compile | `gradlew compileJava processResources --offline` under JDK 17 | Successful; no module file built |

Only the gateway can show: that `store.props.write` of an array reaches a two way binding to a view custom property of type
array and comes back as the same ids; that the Designer lists the two properties; that the tick and the selected row look right
in each palette and component size on a real page; that the stock row click of the library's handlers (the node jump) still
works with ticks on; and that a rebinding of `alerts` on the gateway never passes through an empty list, which would clear
the selection.

Release steps: those of section 17.6, with 0.4.2 in place of 0.4.0 (version in `module/build.gradle.kts`, 0.4.2; the
bundle needs no rebuild, since `web/entry.js` is unchanged, but `gen_module_assets.py` must run after any pull).

### 17.9 Version 0.4.3: the Merge with Version 0.3.2

Versions 0.3.2 (section 16) and 0.4.0 to 0.4.2 were built on two branches from 0.3.1, and both gave the pump, the motor and
the fan a `showStatus`: 0.3.2 as the element's own field, 0.4.0 as a property of the module that the wrapper passes on and
that also hides the word `statusText` draws. The merge of 2026-10-26 (COB-168) keeps the 0.4.0 form on those three and the
0.3.2 form on the digital and the analogue valve, which 0.4.0 left without one. The written files then differ from those
of the installed 0.4.2 by `showStatus` on `cadre.ob.valve` and `cadre.ob.analogvalve` alone, in their schemas, in
`components.json` and in the wrapper's specification, so the source carries version 0.4.3 (COBD-052). Version 0.4.3 is
neither built nor installed (COB-169): until it is, a valve's `showStatus` on a page is a property the installed schema
does not declare, which the gateway imports and the wrapper ignores (GF-72), and the toolbar's Readout button leaves the
module's valves as they are. Its release steps are those of section 17.6, with 0.4.3 in place of 0.4.0.

### 17.10 Wrap W1: the Filter (`cadre.ob.filter`)

Spike T0 wrap W1 adds `cadre.ob.filter`, a static symbol with no command of its own, from `obc-filter` (manifest path
`src/automation/filter/filter.ts`). The element has no events. The wrap changes the module's sources only; the module is not
built or installed by it, so the component reaches a gateway with the next module build.

Properties. The 22 attributes of the manifest (`alternativeIcon`, `on`, `variant`, `orientation`, `readoutPosition`,
`readoutSize`, `tag`, `positioning`, `activated`, `alert`, `alertFrameType`, `alertFrameThickness`, `alertFrameStatus`,
`alertFrameMode`, `showAlertIcon`, `progress`, `progressMode`, `progressValue`, `badgeControl`, `badgeCommandLocked`,
`badgeInterlock`, `badgeAlert`), the element's own `showStatus` field (as on the valves, so the toolbar's Readout button reaches
it) and `componentSize`. Enumerations come from the element's declarations as for the other elements: `alternativeIcon` is
`filter1` to `filter4`, `variant` is `square` or `flat`, and `orientation` is `horizontal`, `verticalRight` or `verticalLeft`. Defaults are
measured (`module/web/defaults.json`, `measure_defaults.py`). The filter takes no speed, status text, duty badge or out of
service mark.

Generator and bundle. `obc-filter` is imported in `module/web/entry.js`, listed in `measure_defaults.py` and in `COMPONENTS` of
`gen_module_assets.py`, registered in `CadreOb.java`, and the schema, `components.json` and the browser script are regenerated.

Test page. The library already has a `filter` kind (`Automation/Filter`, in the component test page's symbol kinds), so the page
needed no new block: `MODULE_KIND` maps `filter` to `cadre.ob.filter`, as it maps the valves, and the page's twelve filter
cases become module components under `--render module`. Three consequences follow. The library's variant `regular` is the
element's `square` (`MODULE_VALUE`, applied in `embed_module` and in the test page's `module_value_ok`). The library's
`vertical` flag does not say which side the element's two vertical orientations mean, so a vertical filter stays on the library's
view (`MODULE_EXCEPT`, as a vertical fan). A variant other than `regular` or `flat` stays on the library's view
(`MODULE_NEEDS`). The glass gates name the element in `MODULE_TAGS`. `library/profile.json` is regenerated.

Tests: `FilterComponent` in `tests/test_module.py` (five tests), and the filter cases added to `tests/test_hmi.py`. Gates G0 to G7
pass on the component test page with 19 devices and 21 device symbols.

### 17.11 Wrap W2: the Generator (`cadre.ob.generator`)

Spike T0 wrap W2 adds `cadre.ob.generator`, a stateful device symbol, from `obc-indicator-generator` (manifest path
`src/automation/indicator-generator/indicator-generator.ts`). The element has no events and no alert attributes. The wrap
changes the module's sources only; the module is not built or installed by it.

What the element draws. A compact generator indicator, 48 by 48 px (56 as a double bar): a disc with the generator G glyph, and
for the `bar` and `double-bar` variants one or two progress rings. `value` is the visual scheme (`off`, `regular`, `filled`,
`enhanced`, `categorical`): `off` greys the disc and hides the rings, the others draw it in the instrument colours. `level` and
`secondaryLevel` (0 to 100) sweep the rings. The element has no notion of running, no identifier, no status word and no alert, so a
plain `value` binding would carry the state and nothing else. The element can carry what the row needs, which is why the wrap
proceeds, with the module adding the rest in its wrapper.

Properties. The four attributes of the manifest (`variant`, `value`, `level`, `secondaryLevel`; enumerations from the element's
declarations, defaults measured in `module/web/defaults.json`) and the module's own eight, which the wrapper applies
(`gen_module_assets.EXTRA`, `generator`): `on`, `tag`, `readoutPosition` (`top`, `bottom`, `left`, `right`, `none`),
`showStatus`, `statusText`, `alert`, `alertFrameStatus` and `alertFrameMode`. The last two take the values of the package's own
`AlertType` and `ObcAlertFrameMode`, as the other device components do. `level` and `secondaryLevel` are not bound: the only
percentage in Table 13 of wiki page 13 is the fuel level, which is not the load the rings mean.

How the wrapper draws it. No file of package changes (CLAUDE.md non-negotiable 7). `on` selects the scheme: a generator that is
not running draws `off`, one that runs draws `value`, the regular scheme where `value` is `off` (a plain button in the other
schemes has an icon in the disc's own colour, so `regular` is the running look). The alarm frame is the package's `obc-alert-frame`
element, unchanged, added to the indicator's shadow root with the type `small-side-flip` and the small thickness, so that its levels
colour as those of the other device components: `level-critical` on the Cadre critical colour (a palette variable of the Cadre
palette classes, rgb(196, 36, 183) by day), `level-high` and `alarm` on the alarm colour, `level-medium` and `warning` on the
warning colour, `level-low` and `caution` on the caution colour (wiki page 13 section 11.1). The identifier and the status word are
The package's `obc-automation-button-readout-stack`, unchanged, on the side `readoutPosition` names. The wrapper also sets `tag`,
`on`, `alert` and `alertFrameMode` as plain fields on the indicator, which is where the glass gates read a device component.

Members. The library symbol binds `on` to the member `state` (Table 13 of wiki page 13) and no other. The members `fault` and
`faultCode` are not parameters of the symbol, so they are not bound here: a fault shows through the alarm frame, which follows the
device's alarms (section 11.2 of wiki page 13: one binding of `custom.alerts` for the page, `alert` from `alertAny`,
`alertFrameStatus` from `level`, `alertFrameMode` from `mode`), the same rule as every other module symbol. The identifier
and the status word follow the toolbar's ID tag and Readout buttons as on the other symbols (`embed_module`, `module_status`).

Click. As the other module components: when the symbol names a device, `embed_module` gives the component the `onClick` script that
calls `cadre.hmi.select_device` with the device, the kind `generator`, its title and label, and opens the faceplate in the session's
place for it (`library.open_faceplate`). `framework.FACEPLATE_VIEW` maps the kind to `Faceplate/ASM/Generator` for either style. The
faceplate sweep G11 clicks every `cadre.ob.` component at the centre of its box, so it opens this one.

Generator and test page. `MODULE_KIND` maps `generator` to the component. The module draws only the plain symbol: the
library's `variant` other than `regular`, `activated`, `progress`, the three badges (`MODULE_NEEDS`), the duty and out of service
marks (the page parts' marks) and the generator set, `params.picture` `genset` (`MODULE_EXCEPT`), keep the library's view. The
generator set stays on the library's view: it is a drawing of 240 by 150 px of our own, and the indicator is a 48 px disc with
another purpose. A parameter that is bound and that the component drops, such as `progress`, now also keeps the library's view
(`screen.module_probe`), because the binding would otherwise reach no property. The component has no `positioning`, so `embed_module`
states it only where the schema lists it. `MODULE_TAGS` of the glass gates and `MODULE_PROP` of the walk plan name the element,
and `library/profile.json` is regenerated. On the component test page 11 of the 16 generator cases become module components
(the variant, badges, out of service, progress and activated cases and the five generator sets stay on the library's view).

Tests: `GeneratorComponent` in `tests/test_module.py` (six tests) and one in `FirstRenderTests` of `tests/test_hmi.py`. A Chromium
check with a stand in for the Perspective client drew each case as expected (`on` off and on, the frame at each level and mode,
the four readout sides, no readout). Gates G0 to G7 pass on the component test page with 19 devices and 21 device symbols.

### 17.12 Wrap W3: the Button (`cadre.ob.button`)

Spike T0 wrap W3 adds `cadre.ob.button`, the shared control, from `obc-automation-button` (manifest path
`src/automation/automation-button/automation-button.ts`). The wrap changes the sources only; the module is not built or installed by it.

The element can carry what the row needs. It draws a round button with an icon holder, an identifier and readout stack, an alert
frame and a progress ring, and it has one event, `click` ("Fired when the button is clicked"). The click reaches the host from the
button inside its shadow root (a Chromium check dispatched it, with `static` on and off), so the wrapper's listener on the element
sees it.

Properties. The twenty attributes of the manifest (`variant`, `state`, `static`, `activated`, `tag`, `readoutPosition`, `readoutSize`,
`alert`, `alertFrameType`, `alertFrameThickness`, `alertFrameStatus`, `alertFrameMode`, `showAlertIcon`, `progress`, `progressMode`,
`progressValue`, `direction`, `positioning`, `orientation`, `hasBadgeSpacer`); the enumerations are those of the element's own
declarations and the defaults are measured (`module/web/defaults.json`). The wrapper adds nothing: the element is complete. The
fields without an attribute (`readouts`, `showReadoutStack`, `showAlertCategoryIcon`) are not properties of the component.

Event. As the alert lists (measured fact GF-37): the generator's `ALERT_EVENTS` gains `click`, carried as the component event
`onPress` with an empty payload (`schemas/button.onPress.json`, `ComponentEventDescriptor` in `CadreOb.java`), fired by the wrapper
through `componentEvents.fireComponentEvent`. The name is not `onClick`, which Perspective already uses for the DOM event of a
component.

The write path. No new path. The library's page command button (COB-159, `parts.button_node`) pulses a tag the descriptor declared
through `cadre.hmi.page_pulse`, write path W18 (wiki page 05 section 5.1): the role `Administrator` is asked first (COBD-024, GF-43),
a tag that is not in `session.custom.commands` is refused, `true` is written and `false` follows after the declared length. That path
asks first: the "Press" button only sets a pending flag, and the Confirm button makes the one checked write, with `enabled` bound
to the permission of W18 (gate G7 commands requires it of any control that names a checked write). The module button takes the
place of the Press button, so that it keeps the confirmation, the role check and the refusal when nobody is signed in exactly as they
are; a component event that called `page_pulse` itself would need an `enabled` property, which the element lacks, and would drop the
confirmation that every command of the library has. The descriptor's pulse button takes `render: module` (schema
`screen-descriptor.schema.json`; an error on any other action). Under `--render module` its Press is `cadre.ob.button` with the label
as `tag`, `positioning` `button` and the identifier on the right; `onPress` sets the pending flag; `static` is bound to the negation
of `{view.custom.can.W18}`, so that the button looks inert while the session lacks the permission (the check itself is Confirm's and
`page_pulse`'s). The answer of a refused command shows in place of the label, as for the library's button. Under the stock rendering
the library's button is drawn as before.

Test page. Section 13.4 of page 13 gains "Start generator" (`TB_press_GEN_start`, `render: module`) on the test generator's pulse
member `_componentTest/TB_GEN/cmdStart`, a memory Boolean held true for 60 s (`PULSE_MS`) by `page_pulse`; the generator's `state`
expression tag latches true on it (`latch("cmdStart", "cmdStop", "state")`), so the press is visible as the test generator running.
The library's own buttons stay. Gateway check, signed in with `Administrator`: press, Confirm; `cmdStart` reads true for 60 s and
`TB_GEN/state` true. Signed out: the button is static, Confirm is disabled, and the tag does not change.

Tests: `ButtonComponent` in `tests/test_module.py` (five tests: contract, event, enumerations, Java and bundle, the test page's
button) and three in `ButtonTests` of `tests/test_asm_parts.py` (the Press only asks, Confirm calls `page_pulse` with W18 and its
`enabled`; the stock rendering and an unmarked pulse keep the library's button; `render: module` on another action is an error).
Gates G0 to G7 pass on the component test page with 19 devices and 21 device symbols.

### 17.13 Batch B0: Module-Only Kinds, Piloted with the Resistor (`cadre.ob.resistor`)

Tranche T1 wraps package elements that the library has no view for (the eleven electrical symbols, the specialty elements and
others). The owner chose Option B of `cloud/WRAP-RECIPE.md` section 7.2: such an element is a module-only kind. The batch changes the
sources only; the module is not built or installed by it.

The table. `screen.MODULE_ONLY` maps a descriptor kind to the id of a module component (`{"resistor": "cadre.ob.resistor"}`). A kind in
the table is in neither `KIND_VIEW` nor `MODULE_KIND`, so no table of the library mapping (`MODULE_NEEDS`, `MODULE_EXCEPT`, `MODULE_VALUE`,
`MODULE_STATE`) is touched and the library profile lists no such kind. `module_type(kind)` answers the component of either table.

The contract. `load_contracts` adds one contract for each row under the pseudo view path `Module/<kind>` (`view_of` returns it), derived
by `module_contract` from `module/components.json`: every property of the component with its default (less `positioning`, which
`embed_module` states), the device and status marks of the library's symbols (`hasTag`, `deviceId`, `deviceKind`, `deviceLabel`,
`statusText`, `badgeDuty`, `outOfService`, which reach no property), and the geometry of an automation symbol (anchor `symbol-centre`, a
48 px symbol box, state `on`, the readout and identifier boxes), taken from the library's static symbol, the filter. The readers of
`contracts.get(view_of(s))` need no change. `embed_module` takes the component from `module_type`, no renaming, and the drop is the
status marks the component does not list.

The renderings. Under `--render module` `embed_symbol` hands the symbol to `embed_module`. Where the component cannot draw it (a mark
the component lacks, or `render` `view`, which has no library view to fall back to) and under `--render stock`, `embed_symbol` adds an
error to the report ("kind 'resistor' is module only (cadre.ob.resistor); build it with --render module") and draws the counted gap box;
the error stops the build ("CONTRACT ERRORS: not deploying") and gate G7 contract reports it, so a stock build cannot pass with the kind
as a silent gap. The glass gates find the kind by the element of its component (`glass_gates.MODULE_TAGS` is extended from the table).

The test page. `testbench.build(..., render="module")` (`screen.py` passes `--render`) adds one section "Module only" after the
generator set, built by `module_only_cases` from the contract and the component's schema: the state both ways, each other value of
`variant`, `orientation` and `readoutPosition`, each alert level, the badges, and the identifier and status hidden. Under the stock
rendering the section is omitted. For the resistor it adds 19 symbols (the page's device symbols and devices are those of before).

The pilot. `obc-resistor` (manifest path `src/automation/resistor/resistor.ts`) has the filter's 22 attributes (the `alternativeIcon`
enumeration is `resistor1` to `resistor5`, the others are those of the filter), no events, and the module's `showStatus`. Wrapped as in
section 2 of the recipe: `entry.js`, `measure_defaults.py`, `gen_module_assets.py` (`COMPONENTS`), `CadreOb.java`, and the generated
`components.json`, `resistor.props.json` and bundle. The component has 23 properties. Tests: `ResistorComponent` and `ModuleOnlyKinds` in
`tests/test_module.py` (the second runs over the table). Gateway check: `/component-test`, section "Module only", 19 `obc-resistor`
elements with a non-zero box and no console error.

### 17.14 Batch B1: the Damper, the Switch and the Capacitor (`cadre.ob.damper`, `cadre.ob.switch`, `cadre.ob.capacitor`)

Batch B1 of tranche T1 wraps three static symbols, none with events or a command of its own. The wraps change the module's
sources only; the module is not built or installed by them, so the components reach a gateway with the next module build.
Each is imported in `module/web/entry.js`, listed in `measure_defaults.py` and in `COMPONENTS` of `gen_module_assets.py`, and
registered in `CadreOb.java`, and the schemas, `components.json` and the browser script are regenerated. Each carries the
element's own attributes, `showStatus` and `componentSize`, and takes no speed, status text, duty badge or out of service mark.

Damper (manifest path `src/automation/damper/damper.ts`). The element has 21 attributes, the filter's set less
`alternativeIcon` (it has one drawing), so the component has 22 properties. It is the library kind `damper`
(`Automation/Damper`), a switched device with members, the `Faceplate/Valve` faceplate and `on` bound to its `state` member, so
`MODULE_KIND` maps it and the symbol keeps the page's existing bindings (the state, the alarm frame of wiki page 13 section 11.2
and the faceplate click) with no new member or write. As for the filter, the library's `regular` variant is the element's
`square` (`MODULE_VALUE`), a variant other than `regular` or `flat` stays on the library's view (`MODULE_NEEDS`), and a vertical
damper stays on the library's view, since the `vertical` flag does not say which of the two vertical orientations is meant
(`MODULE_EXCEPT`). The walk reads `on` and the alert frame from the element (`walk_plan.MODULE_PROP`). On the test page 13
damper symbols become the module's component, the twelve cases and the test device.

Switch (`src/automation/switch/switch.ts`). The element has the filter's 22 attributes; `alternativeIcon` is `regular`, `s1`,
`s2` or `s3`. It is the library kind `switch`, a plain symbol with no members and no faceplate of its own, mapped exactly as the
filter, with the same three rules. On the test page 17 switch symbols become the module's component: the twelve cases and the
five alarm lamps (`alarm_block`), which are switch symbols of indicator devices. A lamp opens the faceplate of the kind its
device names, so `embed_module` now takes the symbol's `deviceKind` where the descriptor states one and the kind otherwise,
as the library's view does; without it a module switch lamp would have opened the empty faceplate.

Capacitor (`src/automation/capacitor/capacitor.ts`). The element has the filter's 22 attributes; `alternativeIcon` is
`capacitor01` to `capacitor04`. The library has no such kind, so it is a module-only kind (section 17.13): one row in
`screen.MODULE_ONLY` and nothing else in the generator, the test page or the glass gates. The "Module only" section of the test
page gains 19 capacitor symbols, and a stock build of that page refuses them with one error each.

Tests: `DamperComponent`, `SwitchComponent` and `CapacitorComponent` in `tests/test_module.py` (five tests each), the damper
and switch cases in `tests/test_hmi.py` (mapping tables, variants, vertical, the lamp's faceplate kind), and the page test of
`tests/test_testbench.py`, whose example of a kind the module does not draw is now the indicator (the damper's `none` readout
position is a library value only, and the page omits it). Gates G0 to G7 pass on the component test page with 19 devices and 21
device symbols.

### 17.15 Batch B2: the Diodes, the Ground, the Source, the Converter and the Transformer (`cadre.ob.diodes`, `cadre.ob.ground`, `cadre.ob.source`, `cadre.ob.converter`, `cadre.ob.transformer`)

Batch B2 of tranche T1 wraps five static electrical symbols, none with events or a command of its own and none with a library
kind. Each has the filter's 22 attributes (checked against the pinned manifest, so `module_contract` needed no change), is a
module-only kind (section 17.13: one row in `screen.MODULE_ONLY` and nothing else in the generator, the test page or the glass
gates) and gains 19 symbols in the "Module only" section of the test page. A stock build of that page refuses every such symbol
with one error each. The wraps change the module's sources only; the module is not built or installed by them.

Diodes (`src/automation/diodes/diodes.ts`). `alternativeIcon` is `diodes01` to `diodes06`; the component has 23 properties.

Ground (`src/automation/ground/ground.ts`). `alternativeIcon` is `ground1`, `ground2` or `ground3`; the component has 23 properties.

Source (`src/automation/source/source.ts`). `alternativeIcon` is `sources01` to `sources05`; the component has 23 properties.

Converter (`src/automation/converter/converter.ts`). `alternativeIcon` is `converterDcdc`, `converterDcac`, `converterAcdc` or
`converterFilter1`; the component has 23 properties.

Transformer (`src/automation/transformer/transformer.ts`). `alternativeIcon` is `transformer01` or `transformer02`; the component
has 23 properties.

Tests: `DiodesComponent`, `GroundComponent`, `SourceComponent`, `ConverterComponent` and `TransformerComponent` in
`tests/test_module.py` (five tests each). Gates G0 to G7 pass on the component test page with 19 devices and 21 device symbols.

### 17.16 Batch B3: the Bipolar Transistor, the MOSFET, the Logic Symbol and the Router (`cadre.ob.bipolartransistor`, `cadre.ob.mosfet`, `cadre.ob.logic`, `cadre.ob.router`)

Batch B3 of tranche T1 wraps four more static symbols, none with events or a command of its own and none with a library kind.
Each has the filter's 22 attributes (checked against the pinned manifest, so `module_contract` needed no change), is a
module-only kind (section 17.13: one row in `screen.MODULE_ONLY`) and gains 19 symbols in the "Module only" section of the test
page. A stock build of that page refuses every such symbol with one error each. The kinds are `bipolar-transistor`, `mosfet`,
`logic` and `router`; the component ids carry no hyphen. The module is not built or installed by the wraps.

Bipolar transistor (`src/automation/bipolar-transistor/bipolar-transistor.ts`). `alternativeIcon` is `bipolarTransistor01` to
`bipolarTransistor04`, `bipolarTransistor03Flat` or `bipolarTransistor04Flat`; the component has 23 properties.

MOSFET (`src/automation/mosfet/mosfet.ts`). `alternativeIcon` is `mosfetNtype1` to `mosfetNtype4` or `mosfetPtype1` to
`mosfetPtype4`; the component has 23 properties.

Logic (`src/automation/logic/logic.ts`). `alternativeIcon` is `logic01` to `logic06`; the component has 23 properties.

Router (`src/automation/router/router.ts`). `alternativeIcon` is `router` or `router2`; the component has 23 properties.

Tests: `BipolarTransistorComponent`, `MosfetComponent`, `LogicComponent` and `RouterComponent` in `tests/test_module.py` (five
tests each).

### 17.17 Batch B4: Four Glyphs with Their Own Attributes (`cadre.ob.automationbadge`, `cadre.ob.checkvalve`, `cadre.ob.valvetwoway`, `cadre.ob.valvethreeway`)

Batch B4 of tranche T1 wraps four elements whose attributes are not the filter's: none has `on`, `tag`, `readoutPosition`, a status
word or an alert frame, and none has an event. All four are display-only (owner's decision of section 6 item 4 of the recipe: no
binding writes) and all four are module-only kinds (section 17.13): `automation-badge`, `hydraulic-check-valve`,
`valve-analog-two-way-icon` and `valve-analog-three-way-icon`. The component test page gains 21, 2, 5 and 7 symbols for them in the
"Module only" section, a stock build of the page refuses each one with one error, and the module is not built or installed by the
wraps.

17.17.1 The change to `screen.module_contract`. B0 assumed the filter's attribute set. A component now falls in one of two
geometries, decided from its own properties by `screen.module_geometry` (a symbol has `on`, `tag` and `readoutPosition`; any other is
a glyph). A symbol's contract is unchanged, byte for byte (`screen.load_contracts()` was compared before and after for all 76
earlier contracts, and a test restates the symbol form). A glyph's contract holds exactly the properties of its component with their
defaults (so no `on`, no marks, no alert set), `anchor` `box`, `flow` `none`, no `state`, `symbolSize`, `identifier`, `readoutExtent`
or `statusMode`, and its `size` is the component's `defaultSize`. A glyph is therefore laid out as a box kind (the descriptor's `w`
and `h`), `embed_module` states nothing beyond the descriptor's own parameters (no `positioning`, no identifier, no status), and a
parameter the component lacks is refused by the existing contract check. The test page's cases for a glyph come from its schema
(`testbench.glyph_cases`): the defaults, every value of every enumerated property (the module's `componentSize` apart), each number
at 50 and 100 and each flag against its default with the numbers at 50. `value2` and `closed` joined `GALLERY_PARAMS`, so the state
of a valve glyph is read from a gallery memory tag as `value` is.

17.17.2 What each element draws, from the pinned `dist/` source (read, not recalled), and which attributes are state.

1. Automation badge (`automation-badge.ts`; 2 attributes). A square badge of 16 px at regular size, with an icon chosen by `type`.
   `mode` (`flat`, `regular`, `enhanced`) is presentation: no frame, a framed neutral plate or a raised plate; an alert type always
   draws flat. `type` has 17 values (`auto`, `manual`, `manual-only`, `local`, `local-only`, `command-locked`, `interlock`,
   `interlock-inhibit`, `alert-silenced`, `caution`, `warning`, `alarm`, `level-critical`, `level-high`, `level-medium`, `level-low`,
   `level-diagnostic`) and is the state the badge signals (a control mode, a lock or an alert level). The element's own default for
   `type` is undefined, which draws nothing; the generator maps an optional enumeration to its first value, so the component's
   default is `auto`. It draws the badge useful on its own (it is the same badge the symbols carry in their corners), so it is wrapped;
   its two slots (`icon-silhouette` and the default) are not carried, because a Perspective property cannot fill a slot and the
   built-in types cover the owner's use.
2. Hydraulic check valve (`hydraulic-check-valve.ts`; 2 attributes). A `role="img"` tile in the style of the shuffle button
   (track and thumb) holding the hydraulic icon 13, the check valve symbol. `vertical` turns the tile and is presentation;
   `ariaLabel` (default `Check valve`) is the accessible name and presentation. It has no state; the stylesheet states the cursor as
   not selectable.
3. Analog two-way valve glyph (`valve-analog-two-way-icon.ts`; 3 attributes). A 24 unit drawing of a two-way valve with a handle and
   a travel gauge. `value` (0 to 100, the element divides by 100) is state, the opening; `closed` is state and replaces the
   drawing with the closed valve; `vertical` rotates the drawing by 90 degrees and is presentation.
4. Analog three-way valve glyph (`valve-analog-three-way-icon.ts`; 4 attributes). The same for a three-way valve. `value` and
   `value2` (0 to 100) are state, the two openings (the handle sits at 50 + value/2 - value2/2 percent of its travel); `closed` is
   state; `horisontal` (spelt so in the manifest, kept as is) is presentation and turns the handle through 180 degrees instead of 90 and
   swaps which opening a gauge shows.

None of the four was left unwrapped. The glyphs have no tag, readout or alert frame, so the page's `custom.alerts` bindings do not
reach them, and they open no faceplate (no device mark in the contract). A screen that needs the valve's state alarmed uses the
library valve or `analogvalve`, which the module draws as before.

17.17.3 Components and tests. Properties (with the module's `componentSize`): badge 3, check valve 3, two-way 4, three-way 5. The
registered components move from 27 to 31 (the gateway hook logs the count). Tests: `GlyphComponents` in `tests/test_module.py` (five tests over the four elements)
and, in `ModuleOnlyKinds`, the glyph contract, the unchanged symbol contract, the drawing, and the cases of the page, now split by
geometry. What the gateway step finds: `obc-automation-badge` 21, `obc-hydraulic-check-valve` 2, `obc-valve-analog-two-way-icon` 5 and
`obc-valve-analog-three-way-icon` 7 on `/component-test`, each with a size and no console error. Open: the badge default, and whether
a screen needs the badge's slots.

### 17.18 Batch B5: Four Stateful Indicators (`cadre.ob.battery`, `cadre.ob.engine`, `cadre.ob.tankatmospheric`, `cadre.ob.automationreadout`)

Batch B5 of tranche T1 wraps `obc-indicator-battery`, `obc-indicator-engine`, `obc-indicator-tank-atmospheric` and
`obc-automation-readout` as module-only kinds (section 17.13) of the glyph form (section 17.17.1): none has `on`, `tag` or
`readoutPosition`, a status word or an alert frame, and the manifest gives none of them an alert, so none is given one. They show
live values, but they are display only (owner's decision, section 6 item 4 of the recipe): no event writes a tag and none opens a
faceplate (a module-only kind names no device kind).

17.18.1 What each element draws and which attributes are live, from the pinned `dist/` sources (read, not recalled).

1. Battery (`indicator-battery.ts`; 6 attributes). A 48 unit battery outline. `level` (0 to 100, clamped by the element) is the live
   value: the height of the fill in the `bar` variant. `data` (a list of numbers, each 0 to 100, oldest first) is live in the `trend`
   variant: a polyline and area over the bar's rectangle, with `level` as a thin bar at its right; fewer than two samples draw no line.
   `value` (`regular`, `enhanced`, `categorical`) is the colour scheme of the fill and is a state a screen may bind (a tag that selects
   the scheme), but it is not a measurement. `variant` (`bar`, `trend`), `direction` (`vertical`, `horizontal`) and `hasIcon` (the
   battery icon over the bar variant) are presentation. Its `icon` slot is not carried (a property cannot fill a slot).
2. Atmospheric tank indicator (`indicator-tank-atmospheric.ts`; 6 attributes). The same attributes and meanings with a tank outline;
   `value` is `regular`, `enhanced` or `medium` (the third is the categorical scheme). `level` and `data` are live.
3. Engine indicator (`indicator-engine.ts`; 2 attributes). A frame with four cylinders. `value` (`static`, `regular`, `enhanced`) is
   the only state: the colour of the cylinders, by the stylesheet, so a screen binds it to a tag that gives the engine's condition.
   `direction` is presentation. It has no number.
4. Automation readout (`automation-readout.ts`; 4 attributes carried of 5). A bordered chip printing `value` rounded to a whole number
   (`toFixed(0)`) beside `unit`, in a minimum width of `numberOfDigits` characters, and a 48 px minimum height. `value` is live; `unit`
   is text, which a screen may bind. `numberOfDigits` and `position` (`left`, `right`, `top`, `bottom`: the side of a line the chip
   sits on) are presentation. `lineType` (`LineType | undefined`, an object type the generator does not map, as for the transmitter)
   is left out, which loses only a half-line-width offset of the chip.

17.18.2 How a symbol binds them. No change to `embed_module` was needed. For any symbol the generator turns each entry of `bind`
(parameter to tag member) into the tag binding of the component's property `props.<name>` and removes the parameter's stated value
(`embed_module`, the loop over `sym["bind"]`); a glyph's contract has no `state`, so none of its attributes is the dual
`view.custom.g_<id>` route of a device state, and every bind key is a plain tag binding. A test builds one symbol of each kind with a
`bind` for each live attribute and checks the `propConfig`, and a whole screen build with all of them at once. The binding of `data`
to a tag is accepted by the descriptor, but whether a gateway tag of an array type reaches the property as a list of numbers is not
measured here; the test page therefore states `data` as a fixed list. `value` and `level` join the gallery parameters of the page
(`testbench.GALLERY_PARAMS`: `value` was there; `level` is added), so the page reads them from gallery memory tags and G11 can
exercise the binding.

17.18.3 The change to the wrapper generator. The element's `data` is a list of numbers, which `schema_for` skipped. A data kind
`numbers` joins `gen_module_assets.DATA_SCHEMA` (an array of numbers) and the wrapper's `CONVERT` (each sample read as a number); the
data path (`readArray`, GF-38) is the one the alert lists already use. No earlier contract changes. The page's cases
(`testbench.glyph_cases`) now give every enumeration case the numbers at their first value, so that a scheme shows on a part-filled
bar; a case with `trend` carries a seven sample series; `numberOfDigits` has its own pair of values (1 and 6, as it is a width) and the
unit a text (`kn`).

17.18.4 The overlap of the automation readout with the readout kind. The library kind `readout` (component `cadre.ob.readout`,
`obc-transmitter`) also prints a value with a unit in a chip, and section 15 rejected `obc-automation-readout` for it. The two overlap
in the chip, the value and the unit. The automation readout differs in showing integers only, in having no identifier, setpoint,
advice, alert or fraction digits, in being a button (its `click` event) and in being positioned by a side of a line. It is wrapped as
asked and the overlap is left for the owner to decide: a screen that needs decimals or an identifier uses `readout`.

17.18.5 Components and tests. Properties (with `componentSize`): battery 7, engine 3, tank indicator 7, automation readout 5. The
registered components move from 31 to 35. Tests: five more tests in `GlyphComponents` (the four rows, the series, the enumerations),
the live binding tests and the updated page counts in `ModuleOnlyKinds` (`tests/test_module.py`). What the gateway step finds on
`/component-test`, in the "Module only" section: `obc-indicator-battery` 11, `obc-indicator-engine` 6,
`obc-indicator-tank-atmospheric` 11 and `obc-automation-readout` 10, each with a size and no console error; the trend cases show a
polyline, the bar cases a part-filled bar.

17.18.6 Open items. The readout's `click` event is not carried: a click would at most open a faceplate, and a module-only kind has no
device kind. The binding of `data` to an array tag. The icon slots of the battery and the tank indicator. The overlap with `readout`
(17.18.4).

### 17.19 Batches B6 and B7: Three Specialty Tanks and Three Gauges (`cadre.ob.heatexchanger`, `heatpump`, `hydraulicseparator`, `gaugegenerator`, `gaugemotorspumps`, `gaugevalve`)

Batches B6 and B7 of tranche T1 wrap `obc-heat-exchanger`, `obc-heat-pump`, `obc-hydraulic-separator`, `obc-gauge-generator`,
`obc-gauge-motors-and-pumps` and `obc-gauge-valve` as module-only kinds (section 17.13) of the glyph form (section 17.17.1): none has
`on` or `readoutPosition`, so the geometry check gives each the component's own properties, a `box` anchor and no state. All six are
display only (owner's decision, section 6 item 4 of the recipe): no event writes a tag, no setpoint is written and none opens a
faceplate (a module-only kind names no device kind). Facts are from the pinned manifest and the `dist/` sources, read and not recalled.

17.19.1 Heat exchanger (`heat-exchanger.js`, base `abstract-specialty-tank.js`; 14 attributes, all carried). A pressurised specialty tank
frame with the heat exchanger icon. `medium` (`regular`, `graphic`, `medium`) selects a single area, or a hot and a cold area split on
the diagonal; `static` draws the frame and icon only. The element carries its own `tag`, `activated`, four badge enumerations and an
alert frame (`alert`, `alertFrameType`, `alertFrameThickness`, `alertFrameStatus`, `showAlertIcon`), so the alert frame is the element's
and none is invented. Live attributes: `alert` and `alertFrameStatus` (the frame), `medium` (the scheme, a state a screen may bind),
`activated`, the badge enumerations and `tag` (text). Size 152 by 96, the element's own width and height.

17.19.2 Heat pump (`heat-pump.js`; the same 14 attributes and base). The same drawing with the heat pump icon; its frame is
pressurised and its split diagonal. Live attributes as for the heat exchanger.

17.19.3 Hydraulic separator (`hydraulic-separator.js`; the same 14 attributes and base). The same, with the separator icon and a
horizontal split in place of the diagonal one. Live attributes as for the heat exchanger.

17.19.4 Generator gauge (`gauge-generator.js`, base `gauge-proportional.js`; 30 attributes, all carried). A dial of a full circle
(sector `360` by default) with a needle, a value band and, in the `double` type, a split track for a second value. `value` (clamped
between `minValue` and `maxValue`) and `secondaryValue` are the measurements; `state` (`active`, `loading`, `off`) hides the graphics
unless active; `priority` (`regular`, `enhanced`, `medium`, `off`) is the colour scheme and `off` draws a flat disc. `label`, `unit`,
`secondaryLabel`, `secondaryUnit` and `tag` are text; `maxValue`, `minValue`, the tickmark intervals, `showLabels`, `fractionDigits`,
`large` and `faceDiameter` are presentation. `setpoint` and `newSetpoint` draw marks on the large face only, and the deadbands,
`touching`, `setpointOverride` and `animateSetpoint` shape the setpoint mark. The `icon` and `secondary-icon` slots are not carried
(a property cannot fill a slot). Size 240 by 280, the compact dial's design box with its label stack.

17.19.5 Motor and pump gauge (`gauge-motors-and-pumps.js`; the same 30 attributes). The same dial in a 270 degree sector. The type
`regular`, `negative` (a positive and negative scale, sector `270-pos-neg`, the minimum following `maxValue`) or `double` (a second
track). Live attributes as for the generator gauge.

17.19.6 Valve gauge (`gauge-valve.js`; 18 attributes, all carried). A dial of a two-way or three-way valve. `value` is the opening
through the valve (a percentage, clamped) and `bottomValue` the second opening of the three-way type; `priority` is the scheme;
`barStyle` (`fill`, `tint`), `scalePosition` (`top`, `right`, `bottom`, `left`), `large`, `label`, `unit` and `tag` are presentation
and text. The setpoint attributes are those of the generator gauge. It has no `state`, no `sector` and no readout switch.

17.19.7 How a symbol binds them. No change to `embed_module` was needed; each live attribute binds through `bind` as in section
17.18.2, and a test builds one symbol of each kind with a `bind` for each live attribute (`ModuleOnlyKinds.LIVE`). `setpoint` and
`newSetpoint` are in that list as shown values, bound to a tag read only. The identifier (`tag`) of the three tanks takes the
toolbar route of the other tanks (the text in `custom.idText`, the ID-tag button's flag in the binding); a test checks it. A glyph has
no `deviceId`, so the alert frame does not follow `custom.alerts`: a screen binds `alert` and `alertFrameStatus` to tags. The
property `positioning` of the three tanks is not stated for a glyph (the generator states it for a symbol only), so the element keeps
its default `button`, which fills its box.

17.19.8 The change to the generator. The nullable numbers (`number | undefined`) took the schema default `null` whether or not the
element had a number there, which gave the gauges no tickmarks (their intervals are 50 and 10 by default). The entry now takes the
measured default when it is a number (`gen_module_assets.schema_for`); no earlier schema changed. The page's number pairs gain the
gauges' scale and deadbands (`testbench.GLYPH_NUMBER_VALUES`: `maxValue` 100 and 200, `minValue` 0 and minus 50, the deadbands,
`fractionDigits`), so that a case keeps a span; `state`, `priority`, `medium` and `bottomValue` join the gallery parameters
(`testbench.GALLERY_PARAMS`) and are read from memory tags.

17.19.9 Components and tests. Properties (with `componentSize`; a tank's `positioning` is among them): three tanks 15 each,
generator gauge and motor and pump gauge 31 each, valve gauge 19. The registered components move from 35 to 41. Tests: six rows of
`GlyphComponents` (attribute sets, sizes, Java and bundle registration, the event not carried), the live binding and tag tests and the
updated page counts in `ModuleOnlyKinds` (`tests/test_module.py`). The component test page under `--render module` still passes G0
to G7 with 19 devices and 21 device symbols; a stock build of its descriptor stops with 233 refusals for these six kinds. What the
gateway step finds on `/component-test`, in the "Module only" section: `obc-heat-exchanger` 44, `obc-heat-pump` 44,
`obc-hydraulic-separator` 44, `obc-gauge-generator` 37, `obc-gauge-motors-and-pumps` 38 and `obc-gauge-valve` 26, each with a size and
no console error.

17.19.10 Open items. The `click` event of the three tanks is not wired (display only, no device kind). The setpoint writes of the three
gauges (`setpoint`, `newSetpoint`, `touching`) are not wired: a setpoint is shown as a bound value only, and a write needs a member and
a write path of the device model (wiki 13 section 5). The icon slots of the gauges and the slotted badges, tag and alert text of the
tanks. The sizes chosen for the gauges (240 by 280) are not measured on the gateway. The large face (`large`) is the only one that
draws the setpoint marks.

### 17.20 Batch B8: Two Hydraulic Valves, the Transmitter Button and the Input Modal (`cadre.ob.hydraulicvalve43`, `hydraulicvalvex2`, `transmitterbutton`; the modal is not wrapped)

Batch B8, the last of tranche T1, examines four control elements under the owner's decisions (recipe section 6 items 2 and 4): an element
whose event or property implies a write is wrapped for display and state only, no event writes and no binding writes. Three are wrapped as
module-only kinds of the glyph form (sections 17.13 and 17.17.1); one is not. Facts are from the pinned manifest and the `dist/` sources.

17.20.1 Hydraulic 4/3 valve (`hydraulic-valve-4-3.js`, base `shuffle-button-base.js`; 4 attributes, all carried). A selector of three
positions drawn as a sliding window of buttons, each showing a hydraulic symbol. `selectedPosition` (zero based, default 1, clamped to the
positions) is the state; `type` (`1` to `5`) chooses the symbol of the centre position, the outer two being fixed; `vertical` stacks the
positions; `ariaLabel` is the accessible name. Size 144 by 48, not measured on the gateway.

17.20.2 Hydraulic X/2 valve (`hydraulic-valve-x-2.js`, the same base and attributes). Two positions; `type` is `2/2`, `3/2` or `4/2` and
selects the pair of symbols. Size 96 by 48, not measured on the gateway. Live attribute of both valves: `selectedPosition`, bound to a tag
for display. The element changes nothing itself: a press dispatches `position-selected` with the requested position and leaves
`selectedPosition` to the host.

17.20.3 The write is deferred. The event `position-selected` (a composed, bubbling `CustomEvent` whose detail is `{position}`, dispatched
by a press or by an arrow key) is not carried: neither valve has an `events` entry, so Perspective receives nothing and nothing is written.
A later wiring follows recipe section 3.3: carry the event as a component event with a `payload` kind, set a pending flag on it, ask on
Press and write the position on Confirm through the existing write path with the `Administrator` check (COBD-024), and echo the written
position back through `selectedPosition`. This is an open item.

17.20.4 Transmitter button (`transmitter-button.js`; 14 attributes, all carried). A pressable chip that is the core of a transmitter. The
`value` variant draws an optional advice segment (`hasAdvice`, `adviceValue`), an optional setpoint segment (`hasSetPoint`,
`setpointValue`), then the value with its `unit`; the `tag` variant draws a rounded pill with `label` and no live value. `size`
(`regular`, `medium`, `large`) scales the text. The three numbers are nullable and draw dashes while empty. `fractionDigits`, `maxDigits`,
`hintedZeros` and `hasSignSpacer` are the shared numeric format of the element's `obc-readout-block`. `hasIcon` reserves a slot for a
leading icon; the slot (`icon`) is not carried, so the flag leaves its space empty. Live attributes: `value`, `adviceValue`,
`setpointValue` (and `label` as text), which bind to tags for display. Size 96 by 40, not measured on the gateway. The manifest declares
no event and the source has no listener; the inner `button` has a native click that bubbles out of the shadow root. A later wiring would
list the DOM event `click` in `ALERT_EVENTS` as the component event `onPress` (never `onClick`) and follow the same Press, Confirm rule;
it is left unwired and is an open item.

17.20.5 Input modal (`automation-input-modal.js`): not wrapped. The manifest gives it no attributes and no events, and four slots
(`header`, `preview`, `action-primary`, `action-secondary`). The source is a template of one wrapper with a header, a preview and an
actions row, each a bare `slot`, and a stylesheet: it holds no state and draws nothing of its own. A property cannot fill a slot (as for
the gauges' icon slots, section 17.19.4), so a component that carried the element alone would show an empty frame, and a faithful wrap
would need Perspective child components laid into those slots, which is a container component with its own contract and is outside the
display-only scope of T1. Recorded as not wrapped; it can return if a container wrapper is built.

17.20.6 Changes to the generator and the page. `testbench.glyph_cases` states a nullable number at the page's number pairs when it is
named in `GLYPH_NULLABLE` (`value`, `adviceValue`, `setpointValue`); a gauge's nullable setpoints stay unstated as before, so no earlier
page count moved. The `tag` variant case carries `label` `TT` (`GLYPH_COMPANION`). `selectedPosition` (1, 0, 2) and `maxDigits` (0, 4)
join `GLYPH_NUMBER_VALUES`; `selectedPosition`, `adviceValue` and `setpointValue` join `GALLERY_PARAMS`. No change to `embed_module`.

17.20.7 Components and tests. Properties (with `componentSize`): each valve 5, the transmitter button 15. The registered components move
from 41 to 44. Tests: three rows of `GlyphComponents` (attribute sets, sizes, the valves' event not carried, the button's no event),
the live binding tests and updated page counts in `ModuleOnlyKinds`, and one test of the button's page cases. The component test page
under `--render module` passes G0 to G7 with 19 devices and 21 device symbols; a stock build of its descriptor stops with 40 further
refusals for these kinds. What the gateway step finds on `/component-test`, in the "Module only" section: `obc-hydraulic-valve-4-3` 10,
`obc-hydraulic-valve-x-2` 8 and `obc-transmitter-button` 22, each with a size and no console error.

### 17.21 Batch C1: Six Bars and Graphs (`cadre.ob.areagraph`, `linegraph`, `donutchart`, `piechart`, `polarchart`, `radialbarchart`)

Batch C1 of tranche T2 wraps the six elements of the manifest group `bars-graphs` as module-only kinds (section 17.13) of the glyph form
(section 17.17.1). They draw with Chart.js 4.5.1, which is a dependency of the pinned package and was already in the bundle when the
batch began, so no charting dependency is added. All six are display only: none of them declares an
event, and none opens a faceplate. Their data are public fields without an attribute (`data`, `datasets`, `labels`, `colors`,
`yAxes`), which `schema_for` skips; the entry names them in `data`, and the module carries each as a JSON list property with an item
schema of our own wording (`gen_module_assets.DATA_SCHEMA`: `points`, `datasets`, `yaxes`, `labels`, `colors`, `segments`,
`piesegments`, `rings`). The wrapper hands the element a copy made with `JSON.parse(JSON.stringify(...))` (`toRecords`), because
Chart.js writes to the arrays it is given and the property tree holds immutable data. A symbol binds a list through `bind`, as for the
alert lists (GF-38): a Document tag, or a binding that returns a list of objects, drives the property; a fixed list is a parameter.
The sample data of the test page are our own (`testbench.GLYPH_POINTS`, `GLYPH_SEGMENTS`, `GLYPH_SECTORS`, `GLYPH_SUNBURST`).

17.21.1 Area graph (`area-graph.ts`; 30 attributes). A line chart that is always filled. Data: `data` (objects `{label, x, value}`: a
single series, `label` on the category axis, `x` on a time axis in epoch milliseconds or an ISO string or on a number axis) or
`datasets` (objects `{label, data, yAxisID}`; `data` holds numbers, or `{x, y}` points on a time or number axis), which replaces
`data` when it is not empty; `labels` (the category labels of `datasets`), `colors` (CSS colours) and `yAxes` (objects `{id, position,
min, max, grid}`). Presentation: `fillMode` (`semitransparent`, `solid`, `threshold`; threshold applies to one series), `stacked`,
`legend`, `width` and `height` (480 by 320), `fixedAspectRatioScaling`, `scaleReferenceSize`, `xAxisType`, `yAxisPosition`, the three
grid flags, `showTickMarks`, `rangeLabels`, `showPoints`, `lineMode`, `unit`, `timeDisplay`, the four tick limits and steps (nullable
numbers) and `priority`. Left out (`LINE_FRAME`): `state`, `frameStyle`, the border radius family and `instrumentMode`, which serve a
slotted external scale or an instrument panel (a nullable enumeration such as `borderRadiusPosition` adds a border plugin for any
value, so the contract cannot carry it with a default), and `showDebugOverlay`; the object `xAxis` (a pinned range) is not carried.
Component properties 29. Bundle growth 2,524 bytes (1,954,229 to 1,956,753).

17.21.2 Line graph (`line-graph.ts`; 28 attributes). The same base and data as the area graph, without the fill: the attributes of
17.21.1 less `fillMode` and `stacked`. Properties 27. Growth 1,759 bytes (to 1,958,512).

17.21.3 Donut chart (`donut-chart.ts`; 14 attributes). Segments of a ring with a total in the centre. `data` is a list of `{label,
value}`; the centre total is their sum. `max` (100) leaves an unfilled remainder in a distinct colour when it exceeds the total.
Presentation: `half`, `showOuterLabels`, `showUnit`, `outerLabelUnit`, `outerLabelMaxLength`, `outerLabelDecimalPlaces`,
`centerReadoutLabel`, `centerReadoutUnit`, `thickness`, `legend`, `fixedHeight` (the element hides labels below 192) and `priority`.
`showDebugOverlay` is left out. Properties 16. Growth 20,349 bytes (to 1,978,861).

17.21.4 Pie chart (`pie-chart.ts`; 10 attributes). `data` is a list of `{label, value, children}`; `children` (objects `{label,
value}`) are drawn as the outer ring when `sunburst` is true. Presentation as the donut's, with no total or `max`. Properties 12.
Growth 10,173 bytes (to 1,989,034).

17.21.5 Polar chart (`polar-chart.ts`; 12 attributes). Sectors of equal angle whose reach shows the value. `data` is a list of
`{label, value}`; `colors` are the series colours, or the threshold steps of the bands when `discreteColorStops` is true.
Presentation: `monochrome`, `showSectorLabels` (angles in place of names), `showUnit`, `showOuterLabels`, `outerLabelUnit` (a degree
sign by default), `outerLabelMaxLength`, `outerLabelDecimalPlaces`, `fixedHeight`, `legend`, `priority`. Properties 14. Growth 11,841
bytes (to 2,000,875).

17.21.6 Radial bar chart (`radial-bar-chart.ts`; 7 attributes). Concentric rings, one for each value. `data` is a list of numbers (the
generic `numbers` kind of 17.18 with another description, `rings`) on the scale 0 to `max` (100); `colors` as above. Presentation:
`circumference` (270 or 360), `minRingThickness`, `legend`, `fixedHeight`, `priority`. Properties 9. Growth 6,526 bytes (to 2,007,401).

17.21.7 Two generator changes beyond table rows. First, the stylesheet generator kept a CSS variable only where the bundle writes
`var(--name)`; the charts read their palette (`--base-gray-100` to `500`, `--base-blue-400`), fonts and frame colours by name from the
computed style (`charthelpers/constants.js`), so those variables were missing and every series drew black in a stand-in page. The
generator now also keeps a variable the bundle names in a string (`scoped_css`): 52 lines were added to `cadre-ob.css` (the grey and
blue base colours, three font weights, a frame radius and the overlay colour) and none was removed. Second, `testbench.glyph_cases` states the sample data of a kind (`GLYPH_DATA`) in every case
but the default, sets a chart's box from its `width` and `height`, adds the extra cases of `GLYPH_EXTRA` (several series, two axes,
a time axis, colours, labels, a sunburst, bands), and states `timeDisplay` `minutes` beside a time axis (`GLYPH_COMPANION`; the
default `date` display logs a console warning). The number pairs of the charts join `GLYPH_NUMBER_VALUES`.

17.21.8 Components and tests. The registered components move from 44 to 50. In a stand-in page (Chrome, the bundle, the generated
stylesheet) every case of the six kinds drew a canvas without a console message; a chart's box measured 480 by 320 for the two line
charts and 320 by 320 for the others (with the legend or labels up to 458 wide, which the default 480 by 320 holds). Tests:
six rows of `GlyphComponents`, one test of the list schemas and the wrapper copy, the live binding rows (`LIVE`) and the page counts of
`ModuleOnlyKinds`. The component test page under `--render module` passes G0 to G7 with 19 devices and 21 device symbols; a stock
build of its descriptor stops with one refusal for each of the 148 new symbols. What the gateway step finds on `/component-test`, in
the "Module only" section: `obc-area-graph` 39, `obc-line-graph` 35, `obc-donut-chart` 22, `obc-pie-chart` 17, `obc-polar-chart` 20 and
`obc-radial-bar-chart` 15, each with a canvas and no console error. Open items: a bound list needs a Document tag or an expression that
returns a list of objects, not yet tried on the gateway; the charts' interactive tooltips and legend clicks are the element's own and are
not wired to anything.

### 17.22 Batch C2: Five Building Blocks (`cadre.ob.barhorizontal`, `barvertical`, `circularprogress`, `instrumentradial`, `readoutblock`); the Alert List Not Wrapped

Batch C2 of tranche T2 wraps five of the six elements of the manifest group `building-blocks` as module-only kinds (section 17.13) of
the glyph form (section 17.17.1), display only. None has a library kind. A descriptor binds the live attributes with `bind`
(wiki 17.18.1); the registered components move from 50 to 55. The bundle grew from 2,007,401 bytes to 2,009,628 (horizontal bar),
2,011,825 (vertical bar), 2,012,334 (circular progress), 2,021,791 (radial instrument) and 2,023,193 (readout block).

17.22.1 Horizontal bar (`bar-horizontal.ts`; 38 attributes). A scale with an optional bar, a value fill, advice zones and a setpoint
marker. Live: `value` (a nullable number: no fill while empty), `setpoint` and `newSetpoint` (nullable numbers: a marker only while
set), `state` (`active`, `loading`, `off`) and `priority`. Presentation: the range (`minValue`, `maxValue`), `width` (320), the padding,
`side`, the scale (`scaleType`, `frameStyle`, the three tick intervals, the three thicknesses, `showMainTickmarkLabels`,
`scaleBackground`), the bar (`hasBar`, `fillMode`, `fillMin`, `fillMax`, `highlightCurrentValue`), the advice placement
(`advicePosition`), `fixedAspectRatio` with `scaleReferenceSize`, and the setpoint settings (`touching`, the two deadbands,
`setpointOverride`, `animateSetpoint`). Three fields without an attribute are carried: `hasScale` and `showLabels` (true by default in
the element; the `PROPERTIES` table) and `advices`, a list of zones `{min, max, type, hinted}` (`type` is `advice` or `caution`; the
data kind `linearadvices`, copied by `toRecords`). Left out (`BAR_LEFT_OUT`): `barContainerStyle` and `borderRadiusPosition`, nullable
enumerations whose undefined default derives from other properties and which any explicit value overrides (recipe 8.12 item 4), and
`instrumentMode` with `borderRadius`, which serve a bar placed inside another instrument. The field `mainTickmarks` (a list of
numbers) is not carried: empty, the element marks the minimum, zero and the maximum. The event `scale-dimensions-changed` reports the
scale's size to a parent chart; it is left unwired. Properties 38; page cases 58; default size 480 by 128 (a stand-in page in Chrome
measured the drawing 84 to 124 pixels high at 320 to 480 wide, with no console message).

17.22.2 Vertical bar (`bar-vertical.ts`; 38 attributes). The same attributes and fields as 17.22.1 with `height` (320), `paddingTop`
and `paddingBottom` in place of `width`, `paddingLeft` and `paddingRight`; the same live attributes, left-out attributes and unwired
event. Properties 38; page cases 58; default size 128 by 320 (the drawing measured 84 to 108 wide).

17.22.3 Circular progress (`circular-progress.ts`; 5 attributes). A ring that fills with `value` (0 to 100) in the `determinate`
and `progressive-indeterminate` modes, and spins in the default `indeterminate` mode. Live: `value` and `mode`. Presentation:
`strokeWidth`, `viewBoxSize` and `padding`. The element fills its box (an absolutely positioned host), so the component's box is its
size: default 48 by 48. Properties 6; page cases 12; no event.

17.22.4 Radial instrument (`instrument-radial.ts`; 29 attributes). A dial with a needle or a filled arc, a scale, advice zones and a
setpoint marker. Live: `value` (a number, 0 by default), `setpoint` and `newSetpoint` (nullable), `state` and `priority`.
Presentation: the range, `type` and `needleType` (`filled`, `bar`, `needle`), `needleColor` and `barColor` (empty uses the scheme's
colour), the scale (`showLabels`, the three tick intervals, `tickmarksInside`, `tickmarkStyle`, `endLabelsMaxMin`), the clip of the
face (`clipTop`, `clipBottom`, `clipLeft`, `clipRight`, `zoomToFitArc`), `faceDiameter` and the setpoint settings as for the bars.
`advices` is a list `{minValue, maxValue, type, hinted}` (the data kind `radialadvices`; the radial zones name their limits
differently from the bars'). Nothing is left out. The event `frame-changed` reports the computed frame to a parent; it is left
unwired. Properties 31; page cases 42; default size 240 by 240 (the element fills its box).

17.22.5 Readout block (`readout-block.ts`; 23 attributes). A number or a text with a value, setpoint or advice marker. Live: `value`
(the element declares `number | string | null`, which no earlier element had: the module carries it as a property of the types number,
string and null, and the wrapper hands the element a number as a number, a blank or missing value as null, which draws the
unavailable dash, and anything else as text), and for the advice variant `category` (`regular`, `optimal`, `eco`, `caution`,
`warning`, `alarm`, `running`) and `active` (triggered), `off` and `dataQuality` (left out). Presentation: `variant`, `valueType`
(`number` or `text`), `size`, `enhanced`, `weight`, `alignment`, `hasDegree`, `hasIcon`, the digits (`fractionDigits`, `maxDigits`,
`hintedZeros`, `hasSignSpacer`, `spaceReserver`), `offText`, `touching` and `hidePhase`. Left out: `valueSize` and `dataQuality`
(nullable enumerations whose undefined default is meaningful) and `alert`, which is a flag or an object of the element's own frame
configuration (the generator cannot map it, and the library draws its alert frames in the wrapper, wiki 13 section 12). The slot
`icon` is not carried. A text under `valueType` `number` throws in the element's own update (its documented contract), so a descriptor
that binds a text tag sets `valueType` `text`. Properties 21; page cases 40; default size 144 by 64; no event.

17.22.6 Alert list (`alert-list.ts`) is not wrapped. The element has no attribute and no data property: its rows are its slotted
children (`obc-alert-list-item` elements, with the slots `empty-icon`, `empty-title` and `empty-description` for the empty state), it
counts and animates them with a mutation observer, and its only property is `filter`, a function (`attribute: false`). A Perspective
component here is a single wrapper that sets properties on one element, with no children of its own, so the list as such cannot take
its rows from a binding. A wrapper that built the items from a list property would be a new list component beside the two the module
already has for alarms (`obc-alert-list-details` and `obc-alert-list-page-small`, which take `alerts` as data); that is a design
decision for the owner and is recorded as open, not taken here.

17.22.7 Changes beyond table rows. First, `schema_for` maps an attribute of the type `number | string` (with or without `null`) to a
property of the three types and the field kind `nvalue`, and the wrapper's `read` has the matching case (three lines). Second,
nothing else: the scale flags, the advice zones and the stock rows are entries of `PROPERTIES`, `DATA_SCHEMA`, `CONVERT`,
`COMPONENTS`, `GLYPH_NUMBER_VALUES`, `GLYPH_EXTRA` and `MODULE_ONLY`.

17.22.8 Tests and gateway checks. `tests.test_module` holds 136 tests (134 before this batch), with the five rows
of `GlyphComponents`, the tests of the bars' scale flags and zones and of the readout block's value, the live binding rows (`LIVE`)
and the page counts of `ModuleOnlyKinds`. The component test page under `--render module` passes G0 to G7 with 19 devices and 21
device symbols; a stock build of its descriptor stops with one refusal for each of the 210 new symbols. What the gateway step finds
on `/component-test`, in the "Module only" section: `obc-bar-horizontal` 58, `obc-bar-vertical` 58, `obc-circular-progress` 12,
`obc-instrument-radial` 42 and `obc-readout-block` 40, no console error. Open items: the two unwired events; an alert list built from
rows (17.22.6); `mainTickmarks` and the readout block's `alert` and slot `icon` not carried; a Document or list binding for `advices`
not yet tried on the gateway.

### 17.23 Batch F1: The Frame Mechanisms and Seven Leaf Components (`cadre.ob.tooltip`, `toggletip`, `clock`, `userbutton`, `appbutton`, `notificationbutton`, `notificationbadgebutton`)

Batch F1 of tranche T2 (`cloud/FRAME-DESIGN.md` sections 2.3 and 4.2). It builds, once and table driven, the mechanisms that the
frame components need, and wraps the seven leaves that use none of the heavy ones. The components are module-only kinds of the
table `FRAME_ONLY` (merged into `MODULE_ONLY`, never into `MODULE_KIND`) and the component test page shows them in the section
"Frame components".

17.23.1 Slot properties. A slot that takes text or an icon becomes a property of the component: the entry key `slots` lists
`{"slot", "kind"}` (and optionally `"property"`), the slot must be one the manifest declares for the element, and the property
name is the slot name in camel case (`content`, `leadingIconName`), `text` for the default slot and `iconName` for an icon in it;
a name that is already a property is refused at generation. A text slot property is a string; an icon slot property is a string
whose enumeration is the empty string and the icon names of `module/web/icons.js` (27 icons of the frame: menu, user, notification,
alarms, palettes, chevrons and others). Each import of that file is checked by the generator against `dist/icons` of the pinned
package, which must define `obi-<name>`; no icon name comes from recall, and the 2,104 icons of the package are not all bundled
(about 1.7 KB each). The wrapper draws a text as a text node (default slot) or a `span` in its slot, and an icon as the element
`obi-<name>` in its slot; a name outside the list draws nothing. The contract (`components.json`) gains a `slots` key for each
component so that tools know which properties are slot properties.

17.23.2 The `items` property. An entry key `items` (`{"items": {"tags": [...], "slot": ""}}`) declares a data property, a list of
objects, that the wrapper turns into child elements of the host. An object holds `tag` (one of the entry's tags at the top
level, one of `ITEM_CHILDREN[parent]` below it, or `span` or a bundled icon `obi-<name>` anywhere below it), the element's
attributes by their manifest field names, `text`, `id` (kept as `data-item-id`), `slot` and `children` (nested to a depth of 8).
The generator reads each allowed tag's attribute names from the manifest (`build_item_table`; a tag the manifest does not declare
stops the run) and puts the table in the wrapper; an attribute not in it is ignored with a console warning, as is a tag not
allowed at its place. Attributes are set as properties, never as markup, so booleans, numbers and objects arrive as they are
(React 18 would turn a boolean attribute of a custom element into a string). The children are rebuilt only when the list changes
and are marked `data-cadre-item`. None of the seven leaves uses it: it is proved in Chromium on a synthetic host
(`module/tools/harness/items.mjs`: nesting, a slot on the top level items, ids, refusals, rebuild) and by the generator tests.

17.23.3 Events. The element's custom events become Perspective component events (GF-37). The table `ALERT_EVENTS` has three new
rows, `obc-click` (`onNotificationClick`, payload `count` and `isActive`, the state the press asks for), `primary-action`
(`onPrimaryAction`) and `secondary-action` (`onSecondaryAction`), both with the button's `label`; the payload kinds are the table
`PAYLOAD_PROPS` (which now also writes the event schema files) and the wrapper's `payload`, and a new kind `item` reports the `id`
and tag of the item an event came from. A component words its own event text with the entry key `eventText`. No event is wired to a
script and none writes a tag; the frame option (F6) wires them. The clock and the user button declare no event: a press is the
host's own click, which Perspective's `onClick` already carries.

17.23.4 Two small generator additions. The entry key `types` names the enumeration of an attribute whose manifest type is missing
(`toggletip.variant`, `app-button.size`); the key `undefinedWhenEmpty` makes an optional text undefined while empty (field kind
`ustring`), which the toggletip needs because its element tests `description !== undefined` and would draw an empty block for
null (the user button's `label` and `sublabel` take it for the same reason). `describe` now also rewords an attribute's
description. The functions `js_spec` and `wrapper_script` were split out of `main` so that the harness can build a bundle for a synthetic
component.

17.23.5 The components. Counts are properties, including slot properties and `componentSize`, in the contract.

| Component | Element | Attributes and fields | Slot properties | Events | Not carried |
|---|---|---|---|---|---|
| `cadre.ob.tooltip` | `obc-tooltip` | 4: `type`, `variant` (seven), `label`, `showIcon` | `iconName` | none | none |
| `cadre.ob.toggletip` | `obc-toggletip` | 10 | `leadingIconName`, `trailingIconName`, `content` (text) | `onPrimaryAction`, `onSecondaryAction` | arbitrary elements in the `content` slot (it carries text only) |
| `cadre.ob.clock` | `obc-clock` | 14 attributes and the field `isClickable` | none | none | a ticking clock: the page binds `date`, and an empty `date` draws NaN |
| `cadre.ob.userbutton` | `obc-user-button` | 8 | `iconName` | none | none |
| `cadre.ob.appbutton` | `obc-app-button` | 5 attributes and the field `showLabel` | `iconName` | `onPress` | none |
| `cadre.ob.notificationbutton` | `obc-notification-button` | 5 | `iconName` | `onNotificationClick` | none |
| `cadre.ob.notificationbadgebutton` | `obc-notification-badge-button` | 7 | `label` (the default slot's text), `iconName` | `onPress` | none |

The default size of each is the largest its page cases draw, measured in Chromium (the tooltip 224 by 40, the toggletip 320 by
232 with a `customWidth` of 280, the clock 208 by 64, the user button 128 by 136, the app button 96 by 96, the notification button
64 by 64 and the badge button 80 by 48).

17.23.6 The test page. The section "Frame components" follows "Module only" under `--render module` and is absent under
`--render stock`. Its cases come from `testbench.frame_cases`: the glyph cases of the component's schema (each enumeration value,
each flag, each number) without the icon slot properties, each stating the kind's base sample of `FRAME_SAMPLE` (our own text and
time), then the named cases of the same table. The page holds 83 frame elements: `obc-tooltip` 13, `obc-toggletip` 14,
`obc-clock` 15, `obc-user-button` 14, `obc-app-button` 7, `obc-notification-button` 11 and `obc-notification-badge-button` 9. A
stand-in page in Chromium drew all 83 with no console message and none wider than its box. A stock build refuses every one, as for
the other module-only kinds.

17.23.7 Tests and gateway checks. `tests.test_module` holds 153 tests (136 before this batch), with the classes `FrameMechanisms`
and `FrameComponents`; `module/tools/harness/frame.mjs` (19 checks) and `items.mjs` (11 checks) pass in Chromium. The component test
page passes G0 to G7 with 19 devices and 21 device symbols. What the gateway step finds on `/component-test`, in the section
"Frame components": the counts of 17.23.6, each with a non-zero box and no console error; a click on the app button, the
notification buttons and the badge button fires its event (not wired, so nothing else happens). The registered components (the log line of the gateway
hook) move from 55 to 62.

### 17.24 Batch F2: The Alert Button and the Alert Menu (`cadre.ob.alertbuttonitem`, `alertbutton`, `alertmenuitem`, `alertmenu`)

Batch F2 of tranche T2 (`cloud/FRAME-DESIGN.md` sections 2 and 3). Each child was wrapped before its parent, by generator entries,
Java descriptors and table rows (`cloud/WRAP-RECIPE.md` section 9). The four are module-only kinds of `FRAME_ONLY`. The alert menu is
the first real parent of the `items` mechanism of 17.23.2.

17.24.1 The alert type and the Cadre priorities. The elements take The package's `AlertType` (`alarm`, `warning`, `caution` and the five
levels `level-critical`, `level-high`, `level-medium`, `level-low`, `level-diagnostic`). The property `alertType` of the alert button and
its item (and the `type` of the alert icon in a row) takes those values and also the empty string, which is the idle state: the element
tests `alertType` for undefined, so the module sends undefined for an empty value (the field kind `ustring`, now also used for an
optional enumeration declared with `undefinedWhenEmpty`). The five Cadre priorities map onto it as `wiki/13` section 11.1 says, and
the description of the property in both schemas records the mapping: Critical `level-critical`, High `alarm`, Medium `warning`, Low
`caution`, Diagnostic empty (no alert colour). The levels `level-high`, `level-medium` and `level-low` draw the colours of `alarm`,
`warning` and `caution` (11.1), so a frame may use either name. The frame option (F6) states the mapping in its binding; the module
only carries the value.

17.24.2 The silence control is hidden. The alert button's `showSilenceButton` defaults to false (its element default), as does the alert
menu's `showSilenceButton`, which the element declares as a field that is true by default: the module states false (the entry's
`properties` row `showSilenceButton`, `PROPERTIES`) because no Cadre function silences an alarm (owner's answer 4). The alert menu's
`showAlertListButton` stays true. The silence events are carried and unwired.

17.24.3 Row events. The element `obc-alert-menu-item` fires `item-click`, `ack-click` and `ack-secondary-click` as plain custom events
that do not bubble, so a listener on the parent never hears them (measured: a row's event does not reach the menu). The wrapper
therefore listens on each row it builds: an entry key `itemEvents` names the events that come from rows, and the wrapper adds the
listeners when it builds a row (`listenItem`; rows are removed with their listeners when the list changes). Row events carry the payload
kind `item` (the row's `id` and tag; an empty id when the row has none). A second key, `eventKinds`, changes the payload kind of an
event for one component, because `ALERT_EVENTS` is keyed by the event's DOM name and `ack-click` and `silence-click` already name the
alarm lists' events: the same DOM name is `none` on the row component and `item` on the menu. The `item` payload now finds its row
through `data-item-id` or `data-cadre-item`. A new payload kind `menuvisible` carries the ACK visible event: `mode` (the tab, `unacked`,
`all` or `shelved`, the element's `tabName`) and `ids` (the `id` of each visible row that has one).

17.24.4 The components.

| Component | Element | Attributes and fields | Items and slot properties | Events | Not carried |
|---|---|---|---|---|---|
| `cadre.ob.alertbuttonitem` | `obc-alert-button-item` | 10 attributes (`aria-label` as `ariaLabel`) | none | `onPress` (the element's `click`) | none |
| `cadre.ob.alertbutton` | `obc-alert-button` | 13 attributes | none | `onAlertClick`, `onSilenceClick` | none |
| `cadre.ob.alertmenuitem` | `obc-alert-menu-item` | 13 attributes | `iconName` (slot `icon`), `alertIcon` (items: `obc-alert-icon` in the slot `alert-icon`) | `onItemClick`, `onAckClick`, `onAckSecondaryClick` (no detail) | the `title` and `description` slots (the attributes draw the same text) |
| `cadre.ob.alertmenu` | `obc-alert-menu` | 2 attributes (`hasShelved`, `canAckAll`) and the fields `showSilenceButton`, `showAlertListButton` | `items` (rows: `obc-alert-menu-item`, each with `obc-alert-icon` in its `alert-icon` slot and a bundled icon in its `icon` slot) | `onAckAllClick`, `onSilenceClick`, `onGoToAlertListClick`, `onItemClick`, `onAckClick`, `onAckSecondaryClick` | the empty state slots (`empty-<tab>-title`, `-description`, `-icon`: the element's own messages draw) |

The alert icon `obc-alert-icon` is an item, not a property, because the slot takes an alert type and a state, not a bundled icon. A row
object holds the row's attributes, `id` and `children`; for example `{"tag": "obc-alert-menu-item", "id": "A-1", "title": "...",
"status": "unacknowledged", "children": [{"tag": "obc-alert-icon", "slot": "alert-icon", "type": "alarm", "active": true,
"acknowledged": false}]}`. The default sizes, measured in Chromium: the alert button item 96 by 64, the alert button 160 by 64 (a
global counter with the silence control draws 153 wide), the alert menu item 360 by 72 and the alert menu 640 by 560 (its own width and
height; a smaller box clips it). A row has no width of its own and drew 32 wide when centred in its box, so the stylesheet stretches
`obc-alert-menu-item` to its box, as it does for the alarm lists.

17.24.5 The test page. The section "Frame components" gains `obc-alert-button-item` 26, `obc-alert-button` 31, `obc-alert-menu-item` 22
and `obc-alert-menu` 8 elements (87 more; 170 in all). The alert menu's cases carry four sample rows of our own (`ALERT_MENU_ROWS`:
a critical unacknowledged alarm, a high alarm with an ACK action, an acknowledged warning and a caution with a source icon), a case of
two rows with the shelved tab, an empty menu and one with the silence button shown. The alert button's two breakpoints are left out
of its cases (they depend on the viewport).

17.24.6 Bundle size of `cadre-ob.js`: 2,174,766 bytes before the first component (F1 left 2,173,627; the wrapper additions are the
difference), then 2,248,479 with the alert button item (+73,713, which brings the alert icon, the counters and their icons),
2,256,584 with the alert button (+8,105), 2,277,380 with the alert menu item (+20,796) and 2,295,305 with the alert menu (+17,925).

17.24.7 Tests and gateway checks. `tests.test_module` holds 156 tests (153 before; the class `FrameComponents` gained four rows, the
`items` row key and three tests); `module/tools/harness/frame.mjs` holds 32 checks (19 before) and `items.mjs` 11, all passing in Chromium,
among them that the rows' events reach the menu with the row id and that a tag outside the allow list builds nothing. A stand-in page
in Chromium drew a menu with three rows, the ACK visible and Alerts buttons and the alert icons of the three severities with no console
message. The component test page passes G0 to G7 with 19 devices and 21 device symbols. What the gateway step finds on
`/component-test`, in the section "Frame components": the four counts of 17.24.5, each with a non-zero box and no console error; a
click on a bell fires `onPress` or `onAlertClick`, a click on a row's ACK fires `onAckClick`; none is wired. The registered components
(the log line of the gateway hook) move from 62 to 66.

### 17.25 Batch F3: Navigation, Tree Navigation and the Breadcrumb (`cadre.ob.navigationitem`, `navigationitemgroup`, `navigationmenu`, `treenavigationitem`, `treenavigationgroup`, `treenavigation`, `breadcrumb`)

Batch F3 of tranche T2 (`cloud/FRAME-DESIGN.md` sections 2 and 3). Each child was wrapped before its parent, by generator entries,
Java descriptors and table rows (`cloud/WRAP-RECIPE.md` section 9). The seven are module-only kinds of `FRAME_ONLY`. The navigation menu and
the tree navigation are the first parents that nest more than one level: a group holds items and groups, to any depth.

17.25.1 Nesting. `ITEM_CHILDREN` lists, for a navigation group, the navigation item and the navigation group itself, and for a tree
group, the tree item and the tree group. An item object is built with its `children` to a depth of `ITEM_DEPTH` (8). A nested item sets
its own `slot` only through the object; the navigation menu's `items` entry puts every top level object in the slot `main` and its
`footerItems` entry in the slot `footer`. The page's sample (`NAV_ITEMS`, `TREE_ROWS` of `tools/hmi/testbench.py`, of our own) holds a
group in a group in the navigation menu (two levels below the menu) and a group in a group holding rows in the tree (three levels).
`ITEM_FIELDS` gains the two fields that a tree row has and no attribute carries: `hasLeadingIcon` (tree item) and `hasIcon` (tree group),
which a row object may set.

17.25.2 Events. The component events carry the item's identity.

| Component | Events (the element's event) | Payload |
|---|---|---|
| `navigationitem` | `onPress` (`click`) | none |
| `navigationitemgroup` | `onOpen` (`open`) | none |
| `navigationmenu` | `onItemClick` (`click` of any item at any depth), `onGroupOpen` (`open` of any group at any depth) | `id`, `tag` |
| `treenavigationitem` | `onPress` (`click`), `onExpandToggle` (`expand-toggle`) | none; `expanded` |
| `treenavigationgroup` | `onExpandToggle` (`expand-toggle`) | `expanded` |
| `treenavigation` | `onItemClick` (`click` of any row at any depth), `onExpandToggle` (`expand-toggle` of any row at any depth) | `id`, `tag`; `id`, `tag`, `expanded` |
| `breadcrumb` | `onBreadcrumbClick` (`breadcrumb-click`) | `label`, `href`, `index` |

None is wired and none writes a tag; F6 binds them to the existing navigation. `expanded` is the state the press asks for. Four
additions to the wrapper carry the cases that F1 and F2 did not meet. (a) The `open`, `expand-toggle` and tree `click` events do not
bubble (they are plain custom events), so the wrapper hears them on each item it built, at every depth (`listenItem` walks the built
subtree); a native event that does bubble (the navigation item's `click`) reaches every item above its target, so an item answers only when
it is the nearest item to the target, and one press is one event. (b) The payload of an item event names the item that heard it
(a nested item without an `id` reports an empty `id`, never its parent's). (c) The tree item fires its own `click` as a `CustomEvent`
(only when the row is neither disabled nor already checked) and the user's native click reaches the host as well, so an entry key
`customEvents` marks the events that count only as a `CustomEvent`: one press is one `onPress`, a disabled row fires none (measured in
Chromium). (d) The entry keys `eventNames` (the navigation menu names the shared DOM event `click` `onItemClick`) and `enums` (the
terminal type is typed `string` in the manifest and is the enumeration `TreeTerminalType`: `regular`, `aggregated-header`,
`group-header`).

17.25.3 The alerts object. The attribute `alerts` of the navigation and tree rows is `TreeNavigationItemAlerts` of the pinned package: the
counts `countLevelCritical`, `countAlarm`, `countLevelHigh`, `countWarning`, `countLevelMedium`, `countCaution`, `countLevelLow`,
`countLevelDiagnostic` and `combine` (one badge with the total). The design table of `cloud/FRAME-DESIGN.md` section 2.2 names the fields
`critical`, `high`, `medium`, `low`, `diagnostic` and `combine`; the pinned `types.d.ts` and `alert-severity.js` are authoritative, and the
schema follows them. The five Cadre priorities map onto the counts as `wiki/13` section 11.1 says (the same mapping as the alert button,
17.24.1): Critical `countLevelCritical`, High `countAlarm`, Medium `countWarning`, Low `countCaution`, Diagnostic `countLevelDiagnostic`;
the description of the property in the four schemas records it. The property is a new field kind `object`: the wrapper reads it with
`tree.read` (GF-38 measured `read` for arrays; an object is read the same way and is copied as JSON, which also unwraps any wrapper), gives
the element undefined while no count is set, and writes it only when its value changes. The reading of an object through the property
tree is not yet measured on a gateway: the gateway step checks that a row with `{"countAlarm": 2}` draws a badge. An open group draws no
badge of its own (the element's rule), so the counts of an open group show on its rows.

17.25.4 The components.

| Component | Element | Attributes and fields | Items and slot properties | Not carried |
|---|---|---|---|---|
| `cadre.ob.navigationitem` | `obc-navigation-item` | 11 attributes (`treeBranches` excluded); `href` and `alerts` undefined while empty | `iconName`, `trailingIconName` | `treeBranches` |
| `cadre.ob.navigationitemgroup` | `obc-navigation-item-group` | 10 attributes (`treeBranches` excluded) | `iconName`; `items` (navigation items and groups, to any depth) | `treeBranches`, the `expanded` getter |
| `cadre.ob.navigationmenu` | `obc-navigation-menu` | `variant` (`full`, `icon-only`, `icon-only-large`, `compact`, `tree`), `flyoutVariant`, `smallScreen` | `items` (slot `main`), `footerItems` (slot `footer`) | the `logo` slot (design table, section 2.3) |
| `cadre.ob.treenavigationitem` | `obc-tree-navigation-item` | 8 attributes (`branches` excluded), field `hasLeadingIcon` | `iconName` | `branches`, `focusable` |
| `cadre.ob.treenavigationgroup` | `obc-tree-navigation-group` | 7 attributes (`branches` excluded), field `hasIcon` | `iconName`; `items` (tree rows, to any depth) | `branches` |
| `cadre.ob.treenavigation` | `obc-tree-navigation` | none | `items` (tree groups and items) | none |
| `cadre.ob.breadcrumb` | `obc-breadcrumb` | field `iconOnly`; the crumbs are the data property `items` | none | a crumb's `icon` (a template function) |

The container sets `treeBranches` of the navigation rows (menu variant `tree`) and `branches` of the tree rows itself, so they are not
properties. In the tree variant the navigation menu draws each row as a tree row in its shadow root and keeps footer items flat. The
breadcrumb carries its items as the element's own array (no child elements): objects of `label` and `href`; the wrapper drops any other
key, because the element calls a crumb's `icon` as a function. A crumb with no `href` is a crumb without one; the last crumb is the
current page and is not a button. `href` of a row navigates the browser (`window.location.href` in the tree row, an anchor in the
navigation item): the frame leaves it empty and navigates through the events (F6).

17.25.5 The breadcrumb is not used by the frame. The owner decided (`cloud/FRAME-DESIGN.md`, owner's answer 2) that the new frame keeps the
Cadre `Framework/Crumb` view with its node badges, which `obc-breadcrumb` cannot draw (it carries no counts). The breadcrumb is wrapped
and drawn on the component test page and the frame will not use it.

17.25.6 Measured sizes in Chromium (module defaults in brackets): navigation item 104 by 48 with a label and an icon (280 by 48), group
112 by 48 (280 by 48), menu 320 wide and as high as its rows, 258 with the sample (320 by 480), tree item 197 by 48 (280 by 48), tree group
202 by 240 (280 by 240), tree navigation 245 by 240 (320 by 240), breadcrumb of three crumbs 296 by 48 (320 by 48). A navigation or tree
row is as wide as its content when centred, so the stylesheet stretches the five row components to their box, as it does for an alert row.
An open group of the flat menu draws its flyout to the right of the menu, outside the component box.

17.25.7 The test page. The section "Frame components" gains `obc-navigation-item` 17, `obc-navigation-item-group` 15,
`obc-navigation-menu` 11, `obc-tree-navigation-item` 12, `obc-tree-navigation-group` 9, `obc-tree-navigation` 3 and `obc-breadcrumb` 4
elements (71 more; 241 in all). The menu's cases include the five variants, and one case of the tree variant with every group open, so
that the two levels of the sample show inline (a flyout of the flat menu floats over the next cell, cosmetic).

17.25.8 Bundle size of `cadre-ob.js`: 2,295,305 bytes before F3 and 2,314,333 after (+19,028). The elements were largely in the bundle already
(the navigation item imports the tree item for its enumerations, so the esbuild output stayed at 2,178,754 bytes for the navigation item, group,
menu and tree item, then rose to 2,180,857 with the tree group, 2,182,996 with the tree navigation and 2,188,866 with the breadcrumb); the rest
is the wrapper, the seven specs and the generated stylesheet rule.

17.25.9 Tests and gateway checks. `tests.test_module` holds 158 tests (156 before; the class `FrameComponents` gained seven rows, the
keys `EXCLUDED` and `DATA`, and two tests); `module/tools/harness/frame.mjs` holds 51 checks (32 before) and `items.mjs` 11, all passing in
Chromium, among them nested events with the id of the nested item (one event for one press), the branches of rows two levels down, the
alert badges, the custom-only click and the breadcrumb's press. The component test page passes G0 to G7 with 19 devices and 21 device
symbols. What the gateway step finds on `/component-test`, in the section "Frame components": the seven counts of 17.25.7, each with a
non-zero box and no console error; the tree rows with a badge (`countAlarm`) draw it; a click on a nested navigation item, a nested tree row
or a crumb fires its event with the identity; none is wired. The registered components (the log line of the gateway hook) move from 66 to 73.

### 17.26 Batch F4: The Menus and the Top Bar (`cadre.ob.brilliancemenu`, `usermenu`, `systemmenu`, `appmenu`, `commandmenu`, `topbar`)

Batch F4 of tranche T2 (`cloud/FRAME-DESIGN.md` sections 2 and 3, and the owner's answers). The six are module-only kinds of
`FRAME_ONLY`, wrapped one after another by generator entries, Java descriptors and table rows (`cloud/WRAP-RECIPE.md` section 9, item 11).
No event is wired and none writes a tag; F6 binds them. Four additions to the generator carry the cases that F1 to F3 did not meet.

17.26.1 Mechanism additions. (a) The payload kind `detail` builds an event payload from the entry's `eventFields` (name, type, text and
an optional detail key for each field); a detail that is not an object is the value of the one field, so the search field of the app menu
(a string) and the volume of the system menu are carried by the same code. (b) `writeBack` names the property that follows a press, for an
element that changes its own state (the command menu's switch, the brilliance menu's palette and brightness, the system menu's sub menu):
the wrapper writes the new value to the component's own property (`store.props.write`, as the alert list does for `selectedIds`), so that
the next update does not set the element back. The value is a key of the event detail, or `@element` when the event carries nothing (the
system menu's `to-sub-menu-click`). A property bound one way is set again by its binding. (c) `fixed` sets fields on the element that no
property carries (the user menu's two credential fields, switched off). (d) `parts` makes a composite (17.26.4): nested elements the
wrapper renders in slots, with the carried properties, the fixed fields, the carried events (heard on the node, since the alert button's
events do not bubble) and an optional default of the composite's own. The entry key `objects` carries the four state objects of the
system menu as the field kind `object` (17.26.3).

17.26.2 The components.

| Component | Element | Properties | Slots and items | Events (the element's event) | Not carried |
|---|---|---|---|---|---|
| `cadre.ob.brilliancemenu` | `obc-brilliance-menu` | 11 attributes, fields `showBrightness`, `showPalette` | none | `onPaletteChanged` (`value`), `onBrightnessChanged` (`value`), `onLinkPaletteChanged`, `onLinkBrightnessChanged` (`value`), `onScreenControlLinkClick` | the four `show*Palette` fields |
| `cadre.ob.usermenu` | `obc-user-menu` | `type`, `size`, `userInitials`, `userLabel`, `userRole` | none | `onSignInClick`, `onSignOutClick`, `onUseAnotherAccountClick` (none carries a payload) | see 17.26.5 |
| `cadre.ob.systemmenu` | `obc-system-menu` | 5 attributes, state objects `wifiState`, `audioState`, `microphoneState`, `batteryState` | none | 15 events (17.26.3) | the `battery-status` slot, the literal event `eventName` |
| `cadre.ob.appmenu` | `obc-app-menu` | none | `items` (`obc-app-button`, each with an `obi-` icon child in the slot `icon`) | `onSearch` (`query`), `onAppClick` (`id`, `tag`) | none |
| `cadre.ob.commandmenu` | `obc-command-menu` | `inCommand`, field `showLocation` | `commandIconName`, `commandStatus`, `commandDescription`, `commandLocation`, `takeCommandLabel`, `releaseCommandLabel`, `inCommandLabel`, `noCommandLabel`, `inCommandIconName` | `onCommandChange` (`inCommand`) | none |
| `cadre.ob.topbar` | `obc-top-bar` | 23 attributes (`showDate` excluded), `breadcrumbItems` as data, the alert button's `nAlerts`, `counter`, `alertType`, `blinking`, `showSilenceButton` and the clock's `date`, `showSeconds`, `timeZoneOffsetHours` | `appIconName`, `commandButtonText` | 12 events (17.26.4) | `showDate`, a crumb's icon |

The brilliance menu's payloads: `value` is the palette (`night`, `dusk`, `day`, `bright`, the same four as the Cadre palettes), the new
brightness, or the state of a link switch. The element changes its own palette and brightness on a press and the menu writes both back to
its properties; Cadre has no brightness function, so the frame hides that section (`showBrightness` false) or ignores the event. The two link
switches and the screen control link are off by default (the element's own default). The command menu names the element's four `toogle-`
slots (a misspelling of the pinned release) as the properties `takeCommandLabel`, `releaseCommandLabel`, `inCommandLabel` and
`noCommandLabel`; `event.inCommand` is the state the press asks for, the menu shows it at once, and the page's script decides what to do
(a command stays the Confirm row). The app menu reports a press of one of its buttons once, with the button's `id`.

17.26.3 The system menu. It carries Wi-Fi, audio, microphone and battery, which are not process state, so it is display only: 15 events
(`onWifiClick` with `enabled`, `onAudioClick` and `onMicrophoneClick` with `muted`, `onAudioVolumeChange` with `volume`,
`onPushToTalkChange` with `pushToTalk`, `onBatterySavingModeChange` with `batterySavingMode`, `onBatteryUsageClick` with `usage`,
`onWifiNetworkChange` with `network`, `onAudioOutputChange` with `output`, `onMicrophoneInputChange` with `input`, `onBatteryModeChange` with
`mode`, and `onSettingsClick`, `onSubMenuClick`, `onWifiOptionsClick`, `onWifiDisconnectClick` with none) and the four state objects, each a
section drawn only while its object is set (empty draws nothing). Their fields are those of the pinned `system-menu.d.ts`; a test holds the
schema to the declaration. The element writes to the object it is given, so the wrapper hands it a copy. The manifest lists 16 events; the
sixteenth, `eventName`, is the parameter name of a private helper of the element (`dispatchClickEvent(eventName)`) and not an event it fires,
so it is not carried (measured: the source never creates a `CustomEvent` of that name). The `d.ts` types the volume event as a number but the
element sends `{volume}`; the payload code accepts either. With `externalControl` false the menu opens its sub menus itself, and the wrapper
writes `activeSubMenu` back from the element on `onSubMenuClick`, because an update of any other property would otherwise close the sub menu
(measured in Chromium before the fix).

17.26.4 The top bar. It is a composite: it renders an `obc-alert-button` in its `alerts` slot and an `obc-clock` in its `clock` slot
itself, and the wrapper sets their properties from the component's. The alert button carries `nAlerts`, `counter`, `alertType`, `blinking`
and `showSilenceButton`; `counter` is carried because the bell shows no count without it, and the top bar's default for it is true (the
element's is false). `showSilenceButton` is false (owner's answer 4). `alertType` follows the mapping of 17.24.1; empty is the idle state.
The clock carries `date` (ISO text in UTC, to be bound to a ticking time), `showSeconds` and `timeZoneOffsetHours`, and is a plain block
(`isClickable` false: it has no event). The bar's own `showClock` must be true for the clock to draw. The events of the bar:
`onMenuButtonClick` (the menu button, on release), `onDimmingButtonClick`, `onAppsButtonClick`, `onMoreButtonClick`, `onUserButtonClick`,
`onEmergencyBrightnessStart` and `onEmergencyBrightnessStop` (the menu button held for half a second, then released: no menu press is
carried then), `onAlertClick` and `onSilenceClick` (the nested alert button), and, in the settings mode only, `onBack`, `onClose` and
`onBreadcrumbClick` (`label`, `href`, `index`). The slot `app-icon` is the icon property `appIconName` (drawn while `showAppIcon` is
true) and `command-button` is the text property `commandButtonText`: a text in the slot, not a button (the element draws whatever the slot
holds, and a button is an element a property cannot carry). The element's `showDate` is not used (its clock is slotted), so it is not carried.
The five `*BreakpointPx` attributes hide a part below a viewport width (default 500 px); the page's cases leave them out. A stylesheet rule
makes the bar span its component box.

The bar's own breadcrumb is not used by the frame. The owner decided (`cloud/FRAME-DESIGN.md`, owner's answer 2) that the frame keeps the
Cadre `Framework/Crumb` view with its node badges, and (answer 3) a Cadre alert message strip beside the bar; the bar draws its breadcrumb
only in the settings mode, which the frame does not use. `settings` and `breadcrumbItems` (label and href, no icon) are carried and drawn on
the test page, so the component is complete, and nothing in the frame binds them. The frame's top dock height is the bar's height: 48 px
(64 px with `tall`), measured in Chromium (17.26.7).

17.26.5 What is excluded from the user menu, and why. Credentials never enter a property (`CLAUDE.md` section 2, item 6; design section 2.3).
Excluded attributes: `username`, `password`, `usernameError`, `passwordError` (the credential fields and their messages), `hasRecentlySignedIn`
and `primaryActionId`. Fixed by the wrapper and never a property: `showUsername` and `showPassword`, both false, so the sign in form is the title
and the Sign in button (no input box exists to type into). Not carried at all: `recentUsers` and `signedInActions` (Cadre has neither) and the
slots `signed-in-action-icon-<id>`. The detail of the element's `sign-in-click` holds the typed values; the payload kind is `none`, so the
wrapper builds the event without reading the detail. The signed in form shows the user (`userInitials`, `userLabel`, `userRole`) and a Sign
out button. F6 binds `onSignInClick` to `system.perspective.login()` and `onSignOutClick` to `system.perspective.logout()` (GF-44). A test
holds that no property or payload names a credential.

17.26.6 Bundle size of `cadre-ob.js`: 2,314,333 bytes before F4, then 2,407,567 (brilliance menu, with the F4 wrapper additions), 2,477,933
(user menu), 2,589,342 (system menu), 2,591,299 (app menu), 2,645,652 (command menu, seven command icons) and 2,664,462 (top bar); 2,664,735
after the system menu's write back. The growth is the elements the menus import (slider, toggle buttons, text input, switches, battery and
audio parts).

17.26.7 Measured sizes in Chromium (module defaults in brackets). Brilliance menu 320 by 457 in the normal variant, 257 compact, 216 tabbed
(320 by 460). User menu 320 wide, 112 high for sign in, 247 signed in, 278 user sign in, 176 signed in small (320 by 280). System menu 320 by
476 with the four sections and the settings button, 375 on a small screen, 129 condensed (320 by 480). App menu 360 by 272 with six or
eight buttons in two rows of four, 321 by 80 with none (360 by 280). Command menu 360 by 256 (360 by 260). Top bar 48 high with every part
drawn, 64 high with `tall`, as wide as its box (960 by 48). The menus are as wide as their content, not their box.

17.26.8 The test page. The section "Frame components" gains `obc-brilliance-menu` 23, `obc-user-menu` 8, `obc-system-menu` 12, `obc-app-menu` 3,
`obc-command-menu` 4 and `obc-top-bar` 39 elements (89 more; 330 in all). The top bar's cases also build an `obc-alert-button` and an
`obc-clock` each, and the app menu's cases build 11 `obc-app-button` elements. The samples are of our own (a network, an output, a user,
eight apps).

17.26.9 Tests and gateway checks. `tests.test_module` holds 165 tests (158 before; the class `FrameComponents` gained six rows, the maps
`PARTS` and `PART_TAGS` and five tests, `FrameMechanisms` two); `module/tools/harness/frame.mjs` holds 82 checks (51 before) and `items.mjs`
11, all passing in Chromium. The component test page passes G0 to G7 with 19 devices and 21 device symbols. What the gateway step finds on
`/component-test`, in the section "Frame components": the six counts of 17.26.8, each with a non-zero box and no console error; every top bar
shows its bell with a count and its clock; the brilliance menu's palette buttons and the command switch change what they show at once; the
sign in form has no input box. None is wired. The registered components (the log line of the gateway hook) move from 73 to 79.

### 17.27 Batch F5: Tabs, Pivots, the Modal Window, the Context Menu Input and the Notification Items (`cadre.ob.tabitem`, `tabrow`, `pivotitem`, `pivotitemgroup`, `modalwindow`, `contextmenuinput`, `notificationmenuitem`, `notificationmessageitem`, `notificationfloatingitem`)

Batch F5 of tranche T2 (`cloud/FRAME-DESIGN.md` sections 2 and 3), the last of the frame batches. It wraps nine components, each child
before its parent, by the entries of recipe section 9, and adds five small things to the generator (17.27.1). The components are kinds of
the table `FRAME_ONLY`; the page shows them in the section "Frame components". Every event is carried as a Perspective component event
(GF-37) and none is wired; no event writes a tag. The only writes are to the component's own properties, where the element changes its own
state (17.27.2).

17.27.1 Generator additions. (a) The element's own array attributes are data properties, read as plain JSON (GF-38) and converted for the
element, with a schema kind and a converter for each: `tabs` (the pinned `TabData` less the `badges` list), `menuoptions` (the pinned
`ContextMenuOption` without its icon, a template function), `columngroups` (`ColumnGroup`) and `strings`. The converters keep only the fields
the element reads and copy them, so the element never writes into the property tree. (b) The entry key `tabIcons` builds an `obi-` element in the
slot `tab-<id>-icon` for each tab that states `iconName` (an icon the module bundles); the row draws a placeholder icon in a tab's slot
otherwise, so a tab without an icon states `hasLeadingIcon` false. (c) `undefinedWhenEmpty` on a nullable boolean gives the field kind
`nboolean` (the schema type `boolean` or `null`, default null, the element sees `undefined`): the context menu's `multiSelect` and
`selectPerGroup` are tri-state, and an unset flag leaves the choice to `type`. (d) A field of an event of the kind `detail` may be a list of
texts (`array`) and its detail key may be a dotted path (`tab.title`, `option.label`). (e) After the wrapper builds a list of `items`, it
asks the element to mark its children when the element has `updateChildItems`, which is what the pivot group does only when its own selection
changes. A write back of a list copies it. No Perspective property, enumeration or event is from memory: the badge enumerations are
`BadgeType` and `BadgeSize`, the others are those of the pinned `d.ts` files.

17.27.2 The components. Counts are properties, including slot properties and `componentSize`, in the contract.

| Component | Element | Properties | Slots and items | Events (the element's event) | Not carried |
|---|---|---|---|---|---|
| `cadre.ob.tabitem` | `obc-tab-item` | 19: 16 attributes (`icon` excluded) | `leadingIconName`, `badgeIconName` | `onTabClick`, `onTabClose` (each with `title`) | the `icon` attribute (the element never reads it), the `badges` field, the `title` slot (the attribute is the title) |
| `cadre.ob.tabrow` | `obc-tab-row` | 8: `tabs` as data, six attributes | none; each tab's `iconName` builds its icon | `onTabSelected`, `onTabClosed` (each with `id`, `index`, `title`), `onAddNewTab` | the `badges` of a tab and its badge icon slots |
| `cadre.ob.pivotitem` | `obc-pivot-item` | 9 | `iconName` | `onSelected` (`value`) | none |
| `cadre.ob.pivotitemgroup` | `obc-pivot-item-group` | 5 | `items` (`obc-pivot-item`, each with an `obi-` child in the slot `icon`) | `onChange` (`selectedValue`) | none |
| `cadre.ob.modalwindow` | `obc-modal-window` | 12: `size`, `hasOptionalAction`, `hasLeadingIcon`, fields `hasCancelAction`, `hasCloseAction` | `leadingIconName`, `title`, `content`, `optionLabel`, `cancelLabel`, `doneLabel` | `onCloseClick`, `onCancelClick`, `onDoneClick`, `onOptionClick` (none carries a payload) | arbitrary content in the `content` slot (17.27.3) |
| `cadre.ob.contextmenuinput` | `obc-context-menu-input` | 10: `options`, `columnGroups` and `selectedValues` as data, six attributes (`multiSelect` and `selectPerGroup` unset by default) | none | `onClose`, `onItemClick` (`value`, `label`), `onChange` (`selectedValues`) | an option's icon and the default slot of custom icons |
| `cadre.ob.notificationmenuitem` | `obc-notification-menu-item` | 11 | `iconName` | `onItemClick` (`open`), `onPrimaryActionClick`, `onSecondaryActionClick` | none |
| `cadre.ob.notificationmessageitem` | `obc-notification-message-item` | 17: 12 attributes, fields `showTitle`, `showDescription`, `showTimestamp` | `secondaryIconName` | `onMessageClick`, `onActionClick` | none |
| `cadre.ob.notificationfloatingitem` | `obc-notification-floating-item` | 15 | `primaryIconName`, `title`, `description`, `time`, `day`, `actionLabel`, `action2Label` | `onActionClick`, `onAction2Click`, `onDismissClick` | none |

The elements that change their own state write the component's property back on a press, as the brilliance menu does (17.26.1): the tab
row's `selectedTabId` (a pressed tab, and the neighbour the row picks after a close), the pivot group's `selectedValue`, the context menu's
`selectedValues` and the notification menu item's `open`. A closed tab stays in the component's `tabs` until the page drops it, because the
row removes it from its own list only. A standalone pivot item does not select itself (its group does), and the pivot ignores a press while
it is selected, so `allowDeselect` has no effect through the interface in this release (measured). The floating item's `action` and
`action2` are the flags that draw the buttons, so the two button texts are `actionLabel` and `action2Label`. The tab item takes its title,
and the tab row its tabs' titles, from the attributes; the element draws the title in a span of its own.

17.27.3 The modal window is not used for commands. Its `content` slot takes any content, which a Perspective component cannot hold (the
module has no container component), so `content` is a text property and the window carries its title and labels as text and its four
buttons as events. The command dialogue of the library stays the Confirm row (`custom.pending`, confirmed through the existing path with the
`Administrator` check); a frame that wants a window with other content than text needs a container component, which no wrap provides. The
window is a plain block of the box it is given: it draws no scrim and no overlay of its own, and its position is the view's.

17.27.4 Bundle size of `cadre-ob.js`: 2,664,735 bytes before F5, then 2,682,430 (tab item, with the F5 generator additions), 2,688,758 (tab
row), 2,698,730 (pivot item), 2,701,463 (pivot group), 2,709,627 (modal window), 2,710,714 (context menu input), 2,713,752 (notification
menu item), 2,736,717 (notification message item) and 2,753,601 (notification floating item). The growth is the elements the new ones
import (badge, button, icon button, the topbar message item, the floating item).

17.27.5 Measured sizes in Chromium (module defaults in brackets). Tab item 48 high, as wide as its box (200 by 48). Tab row 48 high, as
wide as its box (480 by 48). Pivot item 127 by 48 with a label, 48 by 48 icon only (128 by 48). Pivot group 207 by 48 for two labelled
pivots, 106 by 96 vertical (240 by 144). Modal window 540 wide in the large and medium sizes and 349 in the small, 133 to 229 high with one
line of content (540 by 240). Context menu input 160 wide for the regular, nested and flyout types, 248 for eight options in columns, as
wide as its box with two column groups; 104 to 153 high with four options (480 by 240). Notification menu item 57 high single line, 81
double line, 105 opened with its actions, as wide as its box once a stylesheet rule says so (it collapsed to 32 wide without: 360 by 112).
Notification message item 640 by 48 (64 tall; 640 by 64). Notification floating item 640 wide, 73 high with a title alone, 129 with two
actions (640 by 136).

17.27.6 The test page. The section "Frame components" gains `obc-tab-item` 34, `obc-tab-row` 10, `obc-pivot-item` 9, `obc-pivot-item-group` 6,
`obc-modal-window` 11, `obc-context-menu-input` 18, `obc-notification-menu-item` 7, `obc-notification-message-item` 15 and
`obc-notification-floating-item` 13 elements (123 more; 453 in all). The tab row's cases also build one `obc-tab-item` for each tab, and
the context menu's and the notification items' cases build rows of their own. The samples are of our own (four tabs, three pivots, four
menu options and two column groups, a pump notification).

17.27.7 Tests and gateway checks. `tests.test_module` holds 171 tests (165 before; the class `FrameComponents` gained nine rows, the maps
`DATA` and `EXCLUDED` and six tests); `module/tools/harness/frame.mjs` holds 123 checks (82 before) and `items.mjs` 11, all passing in
Chromium. The component test page passes G0 to G7 with 19 devices and 21 device symbols. What the gateway step finds on `/component-test`,
in the section "Frame components": the nine counts of 17.27.6, each with a non-zero box and no console error; the tab row shows four tabs
with icons, a badge on the second and a dimmed last one; the pivot group shows the selected pivot marked; the context menu shows its
selected options; the opened notification menu item shows its two actions; the modal window shows its title, text and buttons. None is
wired. The registered components (the log line of the gateway hook) move from 79 to 88.

17.27.8 All 33 frame components of the pinned release are now wrapped; none is left out, and what a component does not carry is recorded in
the table of its batch. F1 (17.23): the mechanisms and `tooltip`, `toggletip`, `clock`, `user-button`, `app-button`, `notification-button`
and `notification-badge-button`. F2 (17.24): `alert-button-item`, `alert-button`, `alert-menu-item` and `alert-menu`. F3 (17.25):
`navigation-item`, `navigation-item-group`, `navigation-menu`, `tree-navigation-item`, `tree-navigation-group`, `tree-navigation` and
`breadcrumb`. F4 (17.26): `brilliance-menu`, `user-menu`, `system-menu`, `app-menu`, `command-menu` and `top-bar`. F5 (17.27): `tab-item`,
`tab-row`, `pivot-item`, `pivot-item-group`, `modal-window`, `context-menu-input`, `notification-menu-item`, `notification-message-item` and
`notification-floating-item`. That is 7, 4, 7, 6 and 9, 33 in all. The parts recorded as not carried are the `logo` slot of the navigation
menu, the `battery-status` slot of the system menu, the credential fields and recent users of the user menu, the icons of crumbs and menu
options (template functions), the `badges` list of a tab, and the free `content` of the modal window and the toggletip. The next step is
F6, the frame option, which wires the events to the existing navigation, login, logout and acknowledge paths.

### 17.28 The Pipe Components: the Nine Line Elements as Module-Only Glyphs (`cadre.ob.pipehorizontal`, `pipevertical`, `pipecorner`, `pipetee`, `pipecross`, `pipeoverlap`, `pipeend`, `pipedirection`, `bus`)

On 2026-11-04 the owner asked for a pipe component in the module, which reverses the skip of the nine line elements recorded in
tranche T1 (recipe section 6 item 1; `cloud/WRAP-RECIPE.md` section 6.1 item 9). The decision for this batch is narrow: the nine
elements are wrapped as module-only glyphs (section 17.17), so that a pipe component exists in the module, on the palette and on the
component test page. The generator still draws its own pipes as SVG paths in the page view, and the flow solver (gate G6) still
colours them; neither changes. All nine are display only, carry no event and take no `tag`, readout or alert frame. A descriptor
binds a state to a property through `bind` as for any glyph. The palette titles begin with "Pipe," so that an engineer
looking for a pipe finds them together. The page gains 93 symbols in its "Module only" section (the counts are in 17.28.4).

17.28.1 What the elements share, from the pinned `dist/` sources (read, not recalled) and measured in Chromium. Eight of the nine
take `medium` (`normal`, `empty`, `water`, `air`) and `lineType` (`fluid` 4 px, `electric` 2 px, `air` 10 px, `connector` a dashed
neutral line). `medium` is the state: it chooses the inner colour (the primary pipe colour, its inverted colour for `empty`, fresh
water for `water` and `air`), so a screen binds it to show a pipe full, empty or carrying water. `lineType`, `length` and
`direction` are presentation. The overlap, end point and direction elements throw on `connector` when they render, so the
component leaves that value out of their `lineType` enumeration (`without` in the entry of `gen_module_assets.py`, tested). Each
element lays its 24 px drawing 12 px up and left of its host box (or up, or left, or by a direction dependent amount for the end
point), because package places a line on a grid point. Centred in a component box the drawing therefore lay half outside the
box. The module adds one stylesheet to the shadow root of each (`SHEETS`, keys `linehorizontal`, `linevertical`, `linejunction`)
that cancels the offset, and the measured ink then equals the host box for every element and every direction. No element draws
at zero size, so none needed the fill rule of the radial instrument. Second finding: the elements read the variable
`--automation-fresh-water`, but the pinned stylesheet defines `--automation-medium-fresh-water`, so the media `water` and `air`
drew no inner stroke at all (computed stroke `none`). The module stylesheet now names the variable the elements read as the
defined one, and keeps its value in every palette; the change is the generator's, not the package's code.

17.28.2 Elements, one paragraph each.

1. Horizontal line (`cadre.ob.pipehorizontal`, `obc-horizontal-line`). Attributes `medium`, `lineType`, `length`. It does not stretch
   to its box: its host is `length` units of 24 px wide and 24 px high (the ink is one pixel wider), so the default size is 96 by 24.
   `medium` is the state; `length` and `lineType` are presentation.
2. Vertical line (`cadre.ob.pipevertical`, `obc-vertical-line`). The same attributes, drawn top to bottom; the host is 24 px wide and
   `length` units high, default size 24 by 96. `medium` is the state.
3. Corner line (`cadre.ob.pipecorner`, `obc-corner-line`). `medium`, `lineType` and `direction` (`top-right`, `top-left`,
   `bottom-right`, `bottom-left`, the two sides the bend joins). Fixed 24 by 24 drawing, default size 24 by 24. `medium` is the state.
4. Three-way line (`cadre.ob.pipetee`, `obc-three-way-line`). `medium`, `lineType` and `direction` (`top`, `right`, `bottom`, `left`,
   the side of the branch). Fixed 24 by 24, default size 24 by 24. `medium` is the state.
5. Line cross (`cadre.ob.pipecross`, `obc-line-cross`). `medium` and `lineType`; four ends joined at the centre, with rounded inner
   corners. Fixed 24 by 24. `medium` is the state.
6. Line overlap (`cadre.ob.pipeoverlap`, `obc-line-overlap`). `medium` and `lineType` without `connector`; one pipe passes over
   another without joining it. Fixed 24 by 24. `medium` is the state.
7. End point line (`cadre.ob.pipeend`, `obc-end-point-line`). `medium`, `direction` (`top`, `right`, `bottom`, `left`, the side the
   pipe comes from) and `lineType` without `connector`; a stem ending in a terminal bar. Fixed 24 by 24. `medium` is the state.
8. Direction line (`cadre.ob.pipedirection`, `obc-direction-line`). `medium` and `lineType` without `connector`; a pipe segment with
   a chevron that points to the right. There is no `direction` attribute, so a flow in the other sense is not available from the
   element. Fixed 24 by 24. `medium` is the state.
9. Bus (`cadre.ob.bus`, `obc-bus`, manifest group `automation`). Attributes `label` (text in the bar), `size` (`small` 16 px,
   `medium` 24 px), `variant` (`regular`, `enhanced`, `medium`: grey, blue and teal), `tint` (the pale form of the variant) and
   `vertical`. It takes no `medium` or `lineType`. The host is 200 px long by default and shrinks to a smaller box (flex), and a
   vertical bus is 200 px high; the default size is 200 by 24. `variant` and `tint` are the attributes a screen would bind (for
   example a bus tinted while it is de-energised); `label`, `size` and `vertical` are presentation. The test page turns the box of a
   vertical case (`testbench.glyph_cases`).

17.28.3 Tests: `GlyphComponents` (nine more rows of `GLYPHS`, the attributes agreeing with the manifest), `ModuleOnlyKinds` (the
glyph contract, the drawing, the live attributes and the page counts) and `PipeElements` (the three shadow root sheets and their use,
the colour of the water media, the line types each pipe leaves out), all in `tests/test_module.py`; `tests/test_catalogue.py` now
expects 37 components in its second class. The registered components move from 88 to 97 (the gateway hook logs the count).

17.28.4 What the gateway step finds on `/component-test`: `obc-horizontal-line` 11, `obc-vertical-line` 11, `obc-corner-line` 13,
`obc-three-way-line` 13, `obc-line-cross` 9, `obc-line-overlap` 8, `obc-end-point-line` 12, `obc-direction-line` 8 and `obc-bus` 8,
93 in all, each with a non-zero size inside its box and no console error; a `water` or `air` case draws a light blue inner stroke.
Open: the pipes do not take part in the flow solver (the generator's own pipes still do), so a screen that wants a coloured flow
binds `medium` itself; the direction line points only to the right; the bus is not resizable beyond its 200 px length; the
colours of the `water` and `air` media follow the package's fresh water colour.

## 18. References

1. pinned web components, `@oicl/openbridge-webcomponents` 2.0.0-next.155, Apache-2.0,
   Copyright 2024 OICL: `custom-elements.json`, `dist/openbridge.css`, `dist/NotoSans.ttf`.
2. Inductive Automation, `ignition-sdk-examples`, `perspective-component-minimal`, commit
   `f96805a9` (2026-07-06); Ignition SDK 8.3.6; Gradle module plugin `io.ia.sdk.modl` 0.1.1.
3. `gateway-8.3.6.jar`: `ModuleInstallRoutes`, `ModuleManagerImpl`, `RestartTasksRoutes`, read with
   `javap` from JDK 17.0.20.
4. This wiki: page 06 (faceplate contract), page 07 (GF-26 to GF-32), page 08 (gates), page 11 (water treatment sample).
5. Decisions COBD-003, COBD-008, COBD-009, COBD-011; register items COB-030 to COB-034, COB-068,
   COB-070 to COB-075, COB-110, COB-127, COB-151.
6. Evidence: `workspace/spike/compare/module_compare.json`, `workspace/spike/faceplates/`,
   `workspace/spike/functional/` (local); figures in `wiki/figures/12/`.
7. Code: `module/` (the module and its tools), `tools/hmi/screen.py` (`--render module`),
   `tools/hmi/gates.py` (G1, G5), `tools/compare/module_compare.py`, `faceplates.py`, `functional.py`.
