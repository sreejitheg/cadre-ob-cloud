---
title: Roadmap and recommendations
type: wiki
updated: 2026-10-09
---
# 10 Roadmap and Recommendations

| Field | Value |
|---|---|
| Document ID | COB-WIKI-10 |
| Revision | C |
| Status | Proposed for owner review |

## 1. Recommendation

Adopt `cadre_hmi_base`, kept as a separate product (COBD-009), as the parent of new Perspective
projects that the Cadre tools build, and the screen descriptor as the interface between the Cadre
tools and screen building. The water treatment sample (page 11) shows the approach carries a
process plant, not only a single overview. The approach needs no third-party
module, proves every build
offline and live, and keeps the package design language under Apache-2.0 attribution.

## 2. Next Steps

Table 1. Proposed sequence. Register identifiers are in `REGISTER.md`.

| Order | Step | Outcome | Register |
|---|---|---|---|
| 1 | Close the library gaps of the comparison: medium size, alert frame types, speed readout, tank chart and vessel | Pixel agreement close to the reference on the process overview | COB-030 to COB-034 |
| 2 | Diagram toolbar with legend, zoom and pan, and the faceplate panel button | The operator tools of the reference diagram | COB-035, COB-036 |
| 3 | Connect ctig: a genie-type to library-kind map and a pipe extractor producing descriptors from the decoded Citect page model | Citect pages rebuilt on the parent library, gated as here | COB-050 |
| 4 | Done 2026-10-07: the cards layout end to end, the reference `Home` page as the second comparison test | Card pages proven like diagrams | COB-051 |
| 5 | The remaining frame behaviour: navigation groups, top bar breakpoints, alert categories and detail | Frame parity | COB-020 to COB-024 |
| 6 | Electrical single-line symbols from the factory (12 kinds ready) | Power distribution screens | COB-052 |
| 7 | Report the Ignition-Wiki feedback (page 07 section 3) | A validator check for view-level keys | COB-053 |
| 8 | Done 2026-10-07: a process plant sample on the library (page 11) | A clean, functional project, gated end to end | COB-058 to COB-060 |
| 9 | Close the process plant gaps of page 11 section 7: command security (done 2026-10-09, the admin role only, COBD-024), analogue instrument faceplate and faceplate trends (done 2026-10-08, page 13), a trend page (done 2026-10-09), label and text gates, filter and switch faceplates | A library ready for a client process plant | COB-061 to COB-066 |
| 10 | Reconcile the interlock contract's open items with the library sets study (condition type, I/O fault, first out, the core's request members) | The word provisional removed | COB-079 |

## 3. Owner Decisions

Table 2. The questions this page raised, answered by the owner on 2026-10-07.

| Question | Decision |
|---|---|
| Is a commercial licence for the AGPL package versions wanted, or is the Apache-2.0 pin (2.0.0-next.155) sufficient? | The Apache-2.0 pin is sufficient for now (COBD-008) |
| Should the parent project be promoted from this sandbox into Cadre (or ctig)? | No: it stays a separate product (COBD-009) |
| Is a maritime instrument set ever needed? | No: the scope is process automation only (COBD-010); the 39 maritime components stay unbuilt |

Table 3. The questions of the overnight session (COB-REPORT-01 section 11), answered by the owner on
2026-10-09.

| Question | Decision |
|---|---|
| Which rendering strategy: the stock library, the Cadre HMI Components module, or a hybrid (N-COB-5)? | The hybrid: module rendering where the gateway carries the module, stock rendering otherwise (COBD-022) |
| Should a trip latch until reset, and does `interlock-inhibit` mean a bypassed interlock (N-COB-8)? | Yes to both (COBD-023) |
| Which roles does command security require (N-COB-7)? | The admin role only, on every write path (COBD-024) |
| Where are alarm actions taken, and may a cleared alarm be acknowledged from a module row (COB-082)? | On the alerts page, in the top bar's alarm menu and with the top bar's ACK; the faceplate's module Alarms tab is display only, listing the device's active and unacknowledged alarms (COBD-025) |
