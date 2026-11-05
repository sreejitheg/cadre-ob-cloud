# Built Module Files

This folder holds built copies of the Cadre HMI Components module made in the cloud sessions, for the owner to install
without building. It exists only in the cloud copy and is not part of the merge back to the source repository, where
`*.modl` files stay ignored and the module is built and signed from source (`CONFIGURATION.md` section 3.3).

| File | Version | Signed | Built from | SHA-256 |
|---|---|---|---|---|
| `CadreHMIComponents-0.8.0-unsigned.modl` | 0.8.0 (97 components) | No | `spike/t0`, the commit that adds this file | In the `.sha256` file beside it |
| `cadre_hmi_base-0.8.0.zip` | Parent project, for module 0.8.0 | n/a | `python tools/hmi/parent.py`, then `showcase.py --export` | `sha256sum` of the file |
| `cadre_hmi_showcase-0.8.0.zip` | Showcase project, for module 0.8.0 | n/a | `python tools/hmi/showcase.py --export cloud/release` | `sha256sum` of the file |
| `cadre_hmi_showcase-tags.json` | The showcase's device tags (a tag folder document) | n/a | the same command | n/a |

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

## Installing the Showcase Project

The showcase (`wiki/15-showcase.md`) needs the module above installed and its parent project first. The order matters (GF-10): the parent, the
tags, the showcase, and a new browser session to look at it.

1. Install the module 0.8.0 (steps 1 to 4 above) and check in the gateway's module list that Cadre HMI Components 0.8.0 is running.
2. Import `cadre_hmi_base-0.8.0.zip` in the gateway web page under Config, Projects, Import Project: choose the file, type the project name
   `cadre_hmi_base` (the name field stays empty after the file is chosen, and Import stays disabled until it is filled), and press Import. The
   page sends `POST /data/api/v1/projects/import/cadre_hmi_base?overwrite=false` with the zip as the body (measured 2026-11-05). The project is an
   inheritable parent and has no page of its own.
3. Import the device tags at the root of the `default` tag provider. In the Designer's tag browser right-click the provider `default` itself, not a
   folder, choose Import Tags, pick `cadre_hmi_showcase-tags.json` as a JSON file with the collision policy Overwrite. Do not create a folder first.
   The file is rooted at the folder `cadre_hmi_showcase`, so it creates `cadre_hmi_showcase/_componentTest` with the memory and expression tags of
   the eleven test devices and no other tag. Check the browser now shows `default > cadre_hmi_showcase > _componentTest` (11 folders); a tag
   folder `_componentTest` directly under `default`, or a second `cadre_hmi_showcase` inside the first, means the import was started from the wrong
   node: delete it and import again. The same call over REST is `POST /data/api/v1/tags/import?provider=default&path=&type=json&collisionPolicy=Overwrite`.
4. Import `cadre_hmi_showcase-0.8.0.zip` the same way as the parent, with the project name `cadre_hmi_showcase`. Its `project.json` names the parent
   `cadre_hmi_base`.
5. Optional: a gateway import drops the project's identity provider (GF-44). To let the faceplates' commands ask for a sign in, open the project's
   properties in the Designer and choose the provider `default` under security; a viewer sees every page without it, and the page draws the same
   without it (measured 2026-11-05, GF-115).
6. Open `http://<gateway>:8088/data/perspective/client/cadre_hmi_showcase` in a new browser session. `python tools/hmi/showcase.py --deploy` does
   steps 3 to 5 in one call where the repository and an API token are at hand.


### If Every Device Card Shows an Error

A red error badge on each of the eleven device cards is a quality overlay (`ia_qualityOverlay--error`): the card's tags are not at
`[default]cadre_hmi_showcase/_componentTest/...`. The cause reproduced on 2026-11-05 is an import of the tags file made at the wrong node, or an
older tags file (before 0.8.0 rooted at `_componentTest`) imported at the provider root. Open the tag browser, delete the stray folders
(`_componentTest` under `default`, or `cadre_hmi_showcase` inside `cadre_hmi_showcase`), and import this release's file at the provider as in step 3.
