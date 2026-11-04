# Built Module Files

This folder holds built copies of the Cadre OpenBridge module made in the cloud sessions, for the owner to install
without building. It exists only in the cloud copy and is not part of the merge back to the source repository, where
`*.modl` files stay ignored and the module is built and signed from source (`CONFIGURATION.md` section 3.3).

| File | Version | Signed | Built from | SHA-256 |
|---|---|---|---|---|
| `CadreOpenBridge-0.7.0-unsigned.modl` | 0.7.0 (88 components) | No | `spike/t0` at `4cdda21`, module sources unchanged since | In the `.sha256` file beside it |

1. The file is the exact build installed and tested on the cloud gateway at the end of tranche T2 (`cloud/REPORT-T2.md`
   section 4.3).
2. It is unsigned: a gateway installs it only with the JVM system property `ignition.allowunsignedmodules=true` (a
   `wrapper.java.additional.N=-Dignition.allowunsignedmodules=true` line in `data/ignition.conf`), and asks once, at its
   commissioning step after the restart, to trust it (GF-105). A signed build from source needs neither.
3. The module carries the OpenBridge web components (Apache-2.0, release 2.0.0-next.155) with their licence and notice
   inside its gateway jar (`mounted/LICENSES/Apache-2.0.txt`, `mounted/NOTICE.txt`).
4. Check the file before installing: `sha256sum -c CadreOpenBridge-0.7.0-unsigned.modl.sha256`.
