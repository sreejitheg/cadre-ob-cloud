# House HMI Standard

This folder holds the house HMI standard of WorkflowBuilder: the rules that a migrated project's screens, alarms,
tag structure, user defined types (UDTs) and history follow, above what the Cadre HMI library itself states. It is
independent of any one library and any one client (NOTE-WFB-14 ruling R7). Version 0.1 is a draft for the owner's
approval (NOTE-WFB-14 WP-S1).

## 1. Files

Table 1 lists the files of the standard.

Table 1. The files.

| File | Content | Owner |
|---|---|---|
| `STD-WFB-01-hmi-standard.md` | The standard: 68 rules in seven areas, each with its identifier, level, sources, check and fixed flag; the check catalogue; the client layer; the map from the design brief's fourteen principles and the house decisions; the owner's rulings | The orchestrating session; changed only by a new version the owner approves |
| `rules.json` | The machine-readable index of the rules and checks (format `wfb.hmi.rules/1`), generated from the standard's tables | Generated; never edited by hand |
| `client-layer.schema.json` | The JSON schema of an engagement's client layer (format `wfb.hmi.client-layer/1`) | The orchestrating session, with the standard |

## 2. How the Standard Is Used

1. **Rule identifiers.** A rule is `HMI-<AREA>-<nn>`, the areas being `DSP` (display), `NAV` (navigation), `VIS`
   (visibility), `ALM` (alarms), `TAG` (tag hierarchy and naming), `UDT` and `HIS` (history and trends). A check is
   `CK-<AREA>-<nn>`. Identifiers are stable and never reused.
2. **Citations.** The design notes, the briefs and the profiles cite rules by identifier and the library's wiki
   pages by section; neither restates the other.
3. **Checks.** Each checkable rule names its check; WP-S3 runs each check in block 18's design check, the page build's
   checks, the evidence block or the final review, and reports every rule's result by identifier.
4. **The library's share.** A rule marked `carried_by: library` is carried by the library's own code; the library's
   manifest declares the rule identifiers it carries, and the conformance check of NOTE-WFB-15 tests the declaration.
5. **The client layer.** One file per engagement (by default `projects/<engagement>/work/hmi/client-layer.json`, local
   only) sets parameters, replaces or withdraws overridable rules and adds client rules `CLI-<AREA>-<nn>`. A fixed rule
   cannot be changed by a client layer. The manager writes the layer from the migration page and builds the effective
   standard for each run.

## 3. Changing the Standard

1. A change is a new version (0.2 is the next), with a row in the revision table of the standard and the owner's
   approval recorded in `decisions/DECISIONS.md`.
2. After a change to a table of the standard, `rules.json` is regenerated and the test of WP-S3 that compares the two
   passes.
3. A withdrawn rule keeps its identifier with the status withdrawn; a client layer written for an earlier version is
   refused until it is moved to the current one.

## 4. References

1. NOTE-WFB-14 revision 0.3 (WFBD-146): principle 8, rulings R7 and R8, packages WP-S1 to WP-S3.
2. NOTE-WFB-15 (the library contract) and NOTE-WFB-16 (classification for any Citect project), revision 0.1.
3. The library's wiki pages 16 (component selection guide) and 17 (tag model and UDTs), revision B, at
   Cadre-Sandbox-OpenBridge `506076c`.
