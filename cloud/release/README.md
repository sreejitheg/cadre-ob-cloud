# Built Module Files

This folder holds built copies of the Cadre HMI Components module made in the cloud sessions, for the owner to install
without building. It exists only in the cloud copy and is not part of the merge back to the source repository, where
`*.modl` files stay ignored and the module is built and signed from source (`CONFIGURATION.md` section 3.3).

| File | Version | Signed | Built from | SHA-256 |
|---|---|---|---|---|
| `CadreHMIComponents-0.8.0-unsigned.modl` | 0.8.0 (97 components) | No | `spike/t0`, the commit that adds this file | In the `.sha256` file beside it |

1. The file is the exact build installed on the cloud gateway and checked there (module ACTIVE as Cadre HMI Components 0.8.0, 97
   components registered, gate G8 passing on `cadre_hmi_wtpobf`). It adds the nine pipe components and carries the module name
   Cadre HMI Components. The module id is unchanged, so 0.8.0 upgrades 0.7.0 or older in place.
2. It is unsigned: a gateway installs it only with the JVM system property `ignition.allowunsignedmodules=true` (a
   `wrapper.java.additional.N=-Dignition.allowunsignedmodules=true` line in `data/ignition.conf`), and asks once, at its
   commissioning step after the restart, to trust it (GF-105); an upgrade whose licence page differs from the installed one
   also asks to accept the licence there (`CONFIGURATION.md` section 2.7). A signed build from source needs neither.
3. The module carries the pinned web components (Apache-2.0, release 2.0.0-next.155) with their licence and notice
   inside its gateway jar (`mounted/LICENSES/Apache-2.0.txt`, `mounted/NOTICE.txt`).
4. Check the file before installing: `sha256sum -c CadreHMIComponents-0.8.0-unsigned.modl.sha256`.
