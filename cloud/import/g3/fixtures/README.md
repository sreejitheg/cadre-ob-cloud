# G1 fixtures (NOTE-WFB-15 section 13, package F0-W)

Synthetic fixtures derived from two recorded runs on one host, written by
`src/tests/fixtures/g1_fixtures.py` (run: `uv run --no-sync python
src/tests/fixtures/g1_fixtures.py`). Do not edit by hand; regenerate. No file holds a
client, site, project, page or tag name: test T-F0-01 (`src/tests/test_g1_fixtures.py`)
scans every file for the client terms of every engagement on the host and for the run's
page titles and tag stems.

## Rules

1. Texts (labels, titles, captions, treatments, node names, reasons) are `Item <n>`; a
   page title is `Page <n>`.
2. A page identifier is `Page_<n>` (a popup unit `Page_<n>.popups`), a design device
   identifier `Device_<n>`, other design identifiers `<role>_<n>` (roles `reg`, `ind`,
   `flow`, `ro`, `rd`, `nav`, `lbl`, `motor`, `starter`, `J`) or `E<n>`, a tag stem
   `T<nnn>` and a tag suffix `_S<k>` (`T001_S3`), the project folder `cadre_hmi_proj1`, a
   route `/page-<n>`. Identifiers of the shape `static.<n>`, `static_<n>` and `s<n>` are
   kept (the n-th static entry and the inventory object number).
3. Geometry (boxes, points, sizes), element kinds, classes, enumerations, member names,
   gap identifiers, units and formats are kept exactly, so the recorded losses reproduce:
   the well with its four marks and no vessel, the sections without `border` or `title`,
   the two fuse entries and their inventory objects, and the 34 static keys (`static.<n>`
   in the design, `s<n>` in the ASM model: 157 of 191 in the evidence pack, 191 of 191
   in block 24).
4. One mapping serves every file: one original name has one generated name everywhere.
5. Names that hold no tag in the run (the design's `dev_*` identifiers) are numbered by
   their normalised form, so the entry `dev-<x>` and the element `dev_<x>` of one device
   both become `Device_<n>`.

## Files

| File | Test | Source in the run (block, attempt, key) |
|---|---|---|
| `T-F1-01/descriptor.json` | T-F1-01 | build_again/p1-r2 out/page_build/descriptors, the well page (found by its descriptor), as Page_8 |
| `T-F1-01/coverage_map.json` | T-F1-01 | build_again/p1-r2 out/page_build/coverage_map.json, the page's rows |
| `T-F1-01/understanding.json` | T-F1-01 | understandings_final/p1-r1 outputs.json, the page's unit |
| `T-F1-01/design_rows.json` | T-F1-01 | design/p2-r1 out/project_design.json key mapping, the rows of the page |
| `T-F1-02/descriptor.json` | T-F1-02 | build_again/p1-r2 out/page_build/descriptors, the overview page (found by its descriptor), as Page_2 |
| `T-F1-02/coverage_map.json` | T-F1-02 | build_again/p1-r2 out/page_build/coverage_map.json, the page's rows |
| `T-F1-02/understanding.json` | T-F1-02 | understandings_final/p1-r1 outputs.json, the page's unit |
| `T-F1-02/design_rows.json` | T-F1-02 | design/p2-r1 out/project_design.json key mapping, the rows of the page |
| `T-F1-02/gaps.json` | T-F1-02 | build_again/p1-r2 out/page_build/gaps.json, the gaps whose rows lie on the page |
| `T-F1-06/design_rows.json` | T-F1-06 | build_again/p1-r2 out/page_build/mapping.json (191 design rows) |
| `T-F1-06/coverage_map.json` | T-F1-06 | build_again/p1-r2 out/page_build/coverage_map.json (191 keys) |
| `T-F1-06/asm_mapping.json` | T-F1-06 | evidence_again/p1-r1 out/inputs/mapping.json (368 rows of the ASM model, with pop-ups) |
| `T-F1-06/understandings.json` | T-F1-06 | understandings_final/p1-r1 outputs.json, the three units (static entries: 34 in all) |
| `T-F1-06/evidence_checks.json` | T-F1-06 | evidence_again/p1-r1 out/evidence/offline/checks.json (rows, missing: 157 of 191) |
| `T-F1-06/block24_checks.json` | T-F1-06 | build_again/p1-r2 out/check/page_checks/checks.json (rows, missing, coverage: 191 of 191) |
| `T-F2-06/entries.json` | T-F2-06 | understandings_final/p1-r1 outputs.json (the device entries of type fuse), design/p2-r1 out/project_design.json key mapping, build descriptor key screen (canvas) |
| `T-F2-06/inventory_objects.json` | T-F2-06 | device_model/p1-r1 out/model/pages/<page>/inventory.json, the objects of the ans |
| `T-S2-02/devices.json` | T-S2-02 | build_again/p1-r2 out/page_build/devices.json (6 devices, 4 distinct member sets) |
| `T-S2W-04/model.json` | T-S2W-04 | device_model/p1-r1 out/model/model.json (nodes, pages, 47 devices, 368 mapping rows) |
| `T-S2W-04/devices.json` | T-S2W-04 | build_again/p1-r2 out/page_build/devices.json |
| `T-F1W-01_to_05/page_build/descriptors/<three pages>.json` | T-F1W-01 to T-F1W-05 | build_again/p1-r2 out/page_build/descriptors |
| `T-F1W-01_to_05/page_build/coverage_map.json` | T-F1W-01 to T-F1W-05 | build_again/p1-r2 out/page_build/coverage_map.json |
| `T-F1W-01_to_05/page_build/gaps.json` | T-F1W-01 to T-F1W-05 | build_again/p1-r2 out/page_build/gaps.json (30 gaps) |
| `T-F1W-01_to_05/page_build/devices.json` | T-F1W-01 to T-F1W-05 | build_again/p1-r2 out/page_build/devices.json |
| `T-F1W-01_to_05/page_build/tags.json` | T-F1W-01 to T-F1W-05 | build_again/p1-r2 out/page_build/tags.json (member names kept, tag names generated) |
| `T-F1W-01_to_05/page_build/mapping.json` | T-F1W-01 to T-F1W-05 | build_again/p1-r2 out/page_build/mapping.json |
| `T-F1W-01_to_05/page_build/design.json` | T-F1W-01 to T-F1W-05 | build_again/p1-r2 out/page_build/design.json keys pages, mapping (360 rows), gaps; no design_md |
| `T-F1W-01_to_05/model.json` | T-F1W-01 to T-F1W-05 | device_model/p1-r1 out/model/model.json |
| `T-F1W-01_to_05/pages.json` | T-F1W-01 to T-F1W-05 | evidence_again/p1-r1 out/inputs/pages.json |
| `T-F1W-01_to_05/evidence_checks.json` | T-F1W-01 to T-F1W-05 | evidence_again/p1-r1 out/evidence/offline/checks.json |
| `T-F1W-01_to_05/block24_checks.json` | T-F1W-01 to T-F1W-05 | build_again/p1-r2 out/check/page_checks/checks.json |
| `T-F1W-01_to_05/evidence.json` | T-F1W-01 to T-F1W-05 | evidence_again/p1-r1 out/evidence/evidence.json keys format, pages, project_items (causes page, tool, library) |
| `T-F1W-01_to_05/visual_findings.json` | T-F1W-01 to T-F1W-05 | visual_again/p1-r1 outputs.json key finding |
| `T-F2W-01_to_04/understanding_<page>.json` | T-F2W-01 to T-F2W-04 | understandings_final/p1-r1 outputs.json, one per page |
| `T-F2W-01_to_04/inventory_<page>.json` | T-F2W-01 to T-F2W-04 | device_model/p1-r1 out/model/pages/<page>/inventory.json (geometry kept, texts generated) |
| `T-F2W-01_to_04/descriptors/<page>.json` | T-F2W-01 to T-F2W-04 | build_again/p1-r2 out/page_build/descriptors |
| `T-F2W-01_to_04/design_rows.json` | T-F2W-01 to T-F2W-04 | design/p2-r1 out/project_design.json key mapping (191 rows) |
| `T-F2W-01_to_04/coverage_map.json` | T-F2W-01 to T-F2W-04 | build_again/p1-r2 out/page_build/coverage_map.json |

Runs: the design run and the page-build run named in `g1_fixtures.py` (`DESIGN_RUN`,
`BUILD_RUN`). The build folder of the page builder equals `build_again/p1-r2`. The
`capture_com` captures are not read: the inventory objects of the model pages carry the
same geometry, with the text and the paints that section 7.6 item 3 needs.

Not made from the run: T-S2-02's device needing an unmeasured shape (the recorded devices
hold no `mnt`, `cfg` or `ilk` member and no history key; every variant there needs the
parameter-per-member shape of section 9.2 item 3, which the manifest marks).
