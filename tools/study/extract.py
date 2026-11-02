"""Stage S2: one card per item, the cross-reference index, script groups and the batch plan
(COB-PLAN-03 section 7.2). Reads the backup and extract/MANIFEST.json; writes extract/cards/,
extract/xref.json and extract/BATCHES.json. Parse only; run with `python -I`.

    python -I tools/study/extract.py --study F:/repos/Ignition-ASM-Primary
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import studylib as sl  # noqa: E402

P = sl.PERSPECTIVE
EMBED_TYPES = {"ia.display.view", "ia.display.flex-repeater"}
SCRIPT_KEYS = ("script", "code")


class Builder:
    def __init__(self, study: sl.Study):
        self.study = study
        self.z = sl.open_backup(study.backup())
        self.info = sl.backup_info(self.z)
        sl.require_81(self.info)
        self.names = self.z.namelist()
        self.manifest = sl.read_json(study.extract / "MANIFEST.json")
        self.codes = study.codenames()
        self.cards = {}          # id -> card
        self.seq = collections.Counter()
        self.scripts = {}        # hash -> {"body", "occurrences"}
        self.view_ids = {}       # (project, path) -> id
        self.module_ids = {}     # dotted name -> id

    # ---------------------------------------------------------------- helpers
    def new(self, kind: str, key: str, **fields) -> dict:
        letter = sl.LETTER[kind]
        self.seq[letter] += 1
        cid = f"{letter}{self.seq[letter]:04d}"
        card = {"id": cid, "kind": kind, "key": key, **fields}
        self.cards[cid] = card
        return card

    def project_code(self, p: str) -> str | None:
        return self.codes["projects"].get(p)

    def add_script(self, body, card_id: str, pointer: str, location: str) -> str | None:
        if not isinstance(body, str) or not body.strip():
            return None
        h = sl.script_hash(body)
        entry = self.scripts.setdefault(h, {"body": sl.normalise_script(body), "occurrences": []})
        entry["occurrences"].append({"card": card_id, "pointer": pointer, "location": location})
        return h

    def projects(self) -> list:
        return sorted({n.split("/")[1] for n in self.names if n.startswith("projects/") and n.count("/") >= 2
                       and f"projects/{n.split('/')[1]}/project.json" in self.names})

    def resource_files(self, project: str, rtype: str) -> list:
        prefix = f"projects/{project}/{rtype}/"
        return sorted(n for n in self.names if n.startswith(prefix) and not n.endswith("/"))

    # ---------------------------------------------------------------- projects and their resources
    def build_projects(self):
        for p in self.projects():
            meta = sl.zjson(self.z, f"projects/{p}/project.json")
            small = {}
            for rtype in (f"{P}/general-properties", f"{P}/session-permissions", "ignition/global-props",
                          "com.inductiveautomation.vision/client-tags"):
                for n in self.resource_files(p, rtype):
                    if n.endswith(".json") and not n.endswith("resource.json"):
                        small[n.split(f"projects/{p}/", 1)[1]] = sl.zjson(self.z, n)
            counts = collections.Counter("/".join(n.split("/")[2:4]) for n in self.names
                                         if n.startswith(f"projects/{p}/") and n.count("/") >= 4 and not n.endswith("/"))
            self.new("project", p, project=p, project_code=self.project_code(p),
                     source={"entry": f"projects/{p}/project.json"},
                     summary={"parent": meta.get("parent"), "inheritable": meta.get("inheritable"),
                              "enabled": meta.get("enabled"), "resource_files": dict(counts)},
                     raw={"project": meta, "resources": small})
        for p in self.projects():
            files = self.resource_files(p, f"{P}/page-config")
            conf = next((n for n in files if n.endswith("config.json")), None)
            if conf:
                cfg = sl.zjson(self.z, conf)
                pages = cfg.get("pages") or {}
                routes = [{"route": r, "params": re.findall(r":(\w+)", r), "view": v.get("viewPath"),
                           "title": v.get("title"),
                           "docks": [{"side": s, "id": d.get("id"), "view": d.get("viewPath"), "show": d.get("show")}
                                     for s, ds in (v.get("docks") or {}).items() for d in (ds if isinstance(ds, list) else [])]}
                          for r, v in pages.items()]
                shared = [{"side": s, "id": d.get("id"), "view": d.get("viewPath"), "show": d.get("show"),
                           "size": d.get("size"), "anchor": d.get("anchor"), "handle": d.get("handle")}
                          for s, ds in (cfg.get("sharedDocks") or {}).items() for d in (ds if isinstance(ds, list) else [])]
                self.new("page-config", p, project=p, project_code=self.project_code(p), source={"entry": conf},
                         summary={"routes": routes, "shared_docks": shared}, raw=cfg)
            props = next((n for n in self.resource_files(p, f"{P}/session-props") if n.endswith("props.json")), None)
            sess = [n for n in self.resource_files(p, f"{P}/session-scripts") if not n.endswith("resource.json")]
            if props or sess:
                raw = {"props": sl.zjson(self.z, props) if props else None, "scripts": {}}
                for n in sess:
                    data = self.z.read(n)
                    try:
                        raw["scripts"][n.rsplit("/", 1)[1]] = json.loads(data.decode("utf-8"))
                    except (UnicodeDecodeError, ValueError):
                        raw["scripts"][n.rsplit("/", 1)[1]] = {"unparsed_bytes": len(data)}
                card = self.new("session", p, project=p, project_code=self.project_code(p),
                                source={"entry": props or sess[0]},
                                summary={"props": sorted((raw["props"] or {}).keys()) if isinstance(raw["props"], dict) else None,
                                         "script_files": sorted(raw["scripts"])}, raw=raw)
                self.collect_scripts_generic(raw["scripts"], card["id"], "/raw/scripts", "session event")

    def collect_scripts_generic(self, node, cid, pointer, location):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in SCRIPT_KEYS and isinstance(v, str):
                    self.add_script(v, cid, sl.ptr_join(pointer, k), location)
                else:
                    self.collect_scripts_generic(v, cid, sl.ptr_join(pointer, k), location)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                self.collect_scripts_generic(v, cid, sl.ptr_join(pointer, i), location)

    # ---------------------------------------------------------------- views
    def build_views(self):
        for p in self.projects():
            prefix = f"projects/{p}/{P}/views/"
            for n in sorted(x for x in self.names if x.startswith(prefix) and x.endswith("/view.json")):
                path = n[len(prefix):-len("/view.json")]
                v = sl.zjson(self.z, n)
                card = self.new("view", f"{p}/{path}", project=p, project_code=self.project_code(p),
                                path=path, source={"entry": n}, raw=v)
                self.view_ids[(p, path)] = card["id"]
                card["summary"] = self.view_summary(card)

    def view_summary(self, card) -> dict:
        v, cid = card["raw"], card["id"]
        comps, binds, events, classes, embeds, dyn, handlers = collections.Counter(), [], [], set(), [], [], 0
        params = []
        for k, val in (v.get("params") or {}).items():
            pc = (v.get("propConfig") or {}).get(f"params.{k}") or {}
            params.append({"name": k, "direction": pc.get("paramDirection", "input"), "default": val})
        for k, pc in (v.get("propConfig") or {}).items():
            self.binding(cid, "/raw/propConfig", k, pc, binds)
        def walk(node, ptr):
            nonlocal handlers
            t = node.get("type")
            if t:
                comps[t] += 1
            props = node.get("props") or {}
            cls = ((props.get("style") or {}).get("classes")) if isinstance(props.get("style"), dict) else None
            if isinstance(cls, str):
                classes.update(c for c in cls.split() if c)
            if t in EMBED_TYPES and isinstance(props.get("path"), str):
                embeds.append({"pointer": ptr + "/props/path", "path": props["path"], "type": t})
            for k, pc in (node.get("propConfig") or {}).items():
                b = self.binding(cid, ptr + "/propConfig", k, pc, binds)
                if b and t in EMBED_TYPES and k == "props.path":
                    dyn.append({"pointer": b["pointer"], "binding": b["type"], "target": b["target"]})
            for scope, evs in (node.get("events") or {}).items():
                for name, cfg in (evs or {}).items():
                    acts = cfg if isinstance(cfg, list) else [cfg]
                    for i, a in enumerate(acts):
                        ap = sl.ptr_join(ptr, "events", scope, name) + (f"/{i}" if isinstance(cfg, list) else "")
                        conf = (a or {}).get("config") or {}
                        e = {"pointer": ap, "scope": scope, "event": name, "type": (a or {}).get("type")}
                        if e["type"] == "script":
                            e["script"] = self.add_script(conf.get("script"), cid, ap + "/config/script", "view event")
                        elif e["type"] == "popup":
                            e.update(view=conf.get("viewPath"), popup_id=conf.get("id"), params=conf.get("viewParams"))
                        elif e["type"] == "nav":
                            e["config"] = conf
                        events.append(e)
            sc = node.get("scripts") or {}
            for i, h in enumerate(sc.get("messageHandlers") or []):
                handlers += 1
                self.add_script(h.get("script"), cid, sl.ptr_join(ptr, "scripts", "messageHandlers", i, "script"), "message handler")
            for i, m in enumerate(sc.get("customMethods") or []):
                self.add_script(m.get("script"), cid, sl.ptr_join(ptr, "scripts", "customMethods", i, "script"), "custom method")
            for i, ch in enumerate(node.get("children") or []):
                walk(ch, f"{ptr}/children/{i}")
        walk(v.get("root") or {}, "/raw/root")
        return {"params": params, "components": dict(comps), "component_count": sum(comps.values()),
                "bindings": binds, "binding_count": len(binds), "events": events, "style_classes": sorted(classes),
                "embeds": embeds, "dynamic_embeds": dyn, "message_handlers": handlers}

    def binding(self, cid, base, key, pc, out) -> dict | None:
        if not isinstance(pc, dict):
            return None
        ptr = sl.ptr_join(base, key)
        if isinstance((pc.get("onChange") or {}).get("script"), str):
            self.add_script(pc["onChange"]["script"], cid, ptr + "/onChange/script", "property change")
        b = pc.get("binding")
        if not isinstance(b, dict):
            return None
        conf = b.get("config") or {}
        target = conf.get("tagPath") or conf.get("path") or conf.get("expression") or conf.get("struct") or conf.get("tags")
        entry = {"pointer": ptr + "/binding", "prop": key, "type": b.get("type"),
                 "target": target if not isinstance(target, str) else target[:300],
                 "mode": conf.get("mode"), "references": conf.get("references"),
                 "bidirectional": conf.get("bidirectional", False), "transforms": [], "scripts": []}
        for i, t in enumerate(b.get("transforms") or []):
            entry["transforms"].append(t.get("type"))
            if t.get("type") == "script":
                h = self.add_script(t.get("code"), cid, f"{ptr}/binding/transforms/{i}/code", "script transform")
                if h:
                    entry["scripts"].append(h)
        out.append(entry)
        return entry

    # ---------------------------------------------------------------- style classes, themes, modules
    def build_styles(self):
        for p in self.projects():
            prefix = f"projects/{p}/{P}/style-classes/"
            for n in sorted(x for x in self.names if x.startswith(prefix) and x.endswith("/style.json")):
                path = n[len(prefix):-len("/style.json")]
                s = sl.zjson(self.z, n)
                text = json.dumps(s)
                variants = [{k: v for k, v in (var or {}).items() if k != "style"} for var in (s.get("variants") or [])]
                self.new("style", f"{p}/{path}", project=p, project_code=self.project_code(p), path=path,
                         source={"entry": n},
                         summary={"base_keys": sorted(((s.get("base") or {}).get("style") or {}).keys()),
                                  "variants": variants, "colours": sorted(set(sl.COLOUR.findall(text)))}, raw=s)

    def build_themes(self):
        for t in self.manifest.get("custom_themes", []):
            files = sorted(e["name"] for e in self.manifest["entries"] if e["kind"] == "theme-custom"
                           and re.match(rf"modules/{re.escape(P)}/themes/{re.escape(t)}(/|\.css$)", e["name"]))
            raw = {f.split("/themes/", 1)[1]: sl.ztext(self.z, f) for f in files}
            text = "\n".join(raw.values())
            variables = sorted(set(re.findall(r"(--[\w-]+)\s*:", text)))
            self.new("theme", t, name=t, source={"entry": files[0] if files else None},
                     summary={"files": sorted(raw), "variables_defined": variables,
                              "colours": sorted(set(sl.COLOUR.findall(text)))[:400]}, raw=raw)
        icons = [e["name"] for e in self.manifest["entries"] if e["kind"] == "icons"]
        if icons:
            raw = {f.split("/icons/", 1)[1]: sl.ztext(self.z, f) for f in icons}
            ids = sorted(set(re.findall(r'<(?:symbol|g)[^>]*\sid="([^"]+)"', "\n".join(raw.values()))))
            self.new("theme", "(icons)", name="(icon libraries)", source={"entry": icons[0]},
                     summary={"files": sorted(raw), "icon_ids": ids}, raw=raw)

    def build_modules(self):
        for p in self.projects():
            prefix = f"projects/{p}/ignition/script-python/"
            for n in sorted(x for x in self.names if x.startswith(prefix) and x.endswith("/code.py")):
                path = n[len(prefix):-len("/code.py")]
                src = sl.ztext(self.z, n)
                sigs, py3 = sl.python_functions(src)
                card = self.new("module", f"{p}/{path}", project=p, project_code=self.project_code(p), path=path,
                                dotted=path.replace("/", "."), source={"entry": n},
                                summary={"functions": sigs, "lines": src.count("\n") + 1, "parses_as_python3": py3,
                                         "system_calls": dict(collections.Counter(sl.SYSTEM_CALL.findall(src)))},
                                raw={"code": src})
                self.module_ids.setdefault(card["dotted"], card["id"])

    # ---------------------------------------------------------------- tags
    def build_tags(self):
        con = sl.open_idb(self.z, self.study)
        tree = self.tree = sl.TagTree(con)
        prov_code = lambda pid: self.codes["providers"].get(tree.provider_name(pid))
        rows = tree.rows
        udt_key = {}
        # UDT definitions
        defs = sorted((r for r in rows.values() if r["cfg"].get("tagType") == "UdtType" and tree.in_types(r)),
                      key=lambda r: (str(r["provider"]), tree.path(r)))
        for r in defs:
            members, alarms_at, scripts_at = {}, [], []
            for m in tree.descendants(r["id"]):
                rel = tree.path(m)[len(tree.path(r)) + 1:] or m["id"]
                key = rel if rel not in members else f"{rel}#{len(members)}"
                members[key] = {"tag_kind": tree.kind(m), **m["cfg"]}
            card = self.new("udt", f"{tree.provider_name(r['provider'])}/{tree.path(r)}",
                            provider=tree.provider_name(r["provider"]), provider_code=prov_code(r["provider"]),
                            provider_orphan=tree.providers[r["provider"]]["orphan"],
                            name=r["name"], path=tree.path(r), source={"table": "TAGCONFIG", "row": r["id"]},
                            raw={"definition": r["cfg"], "members": members})
            udt_key[(r["provider"], tree.path(r))] = card["id"]
        # instances, atomic tag folders
        insts = sorted((r for r in rows.values() if r["cfg"].get("tagType") == "UdtInstance"
                        and not tree.in_types(r) and not tree.inside_instance(r)),
                       key=lambda r: (str(r["provider"]), tree.path(r)))
        for r in insts:
            overrides = {}
            for m in tree.descendants(r["id"]):
                rel = tree.path(m)[len(tree.path(r)) + 1:]
                overrides[f"{rel}#{len(overrides)}" if rel in overrides else rel] = m["cfg"]
            self.new("instance", f"{tree.provider_name(r['provider'])}/{tree.path(r)}",
                     provider=tree.provider_name(r["provider"]), provider_code=prov_code(r["provider"]),
                     name=r["name"], path=tree.path(r), source={"table": "TAGCONFIG", "row": r["id"]},
                     raw={"instance": r["cfg"], "overrides": overrides})
        folders = collections.defaultdict(list)
        for r in rows.values():
            if tree.kind(r) == "AtomicTag" and not tree.in_types(r) and not tree.inside_instance(r):
                parent = tree.parent(r)
                fpath = tree.path(rows[parent]) if parent in rows else "(root)"
                folders[(r["provider"], fpath)].append(r)
        for (pid, fpath), tags in sorted(folders.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
            tags.sort(key=lambda t: str(t["name"]))
            self.new("folder", f"{tree.provider_name(pid)}/{fpath}", provider=tree.provider_name(pid),
                     provider_code=prov_code(pid), path=fpath, source={"table": "TAGCONFIG"},
                     raw={"tags": {str(t["name"]): t["cfg"] for t in tags}})
        # resolve inheritance and instances, then alarms and tag scripts
        for c in self.cards.values():
            if c["kind"] == "udt":
                d = c["raw"]["definition"]
                c["summary"] = {"parent_type": self.type_ref(udt_key, c, d.get("typeId")),
                                "parameters": {k: (v or {}).get("dataType") if isinstance(v, dict) else None
                                               for k, v in (d.get("parameters") or {}).items()},
                                "members": [{"path": k, "tag_kind": m.get("tag_kind"), "data_type": m.get("dataType"),
                                             "value_source": m.get("valueSource"),
                                             "alarms": len(m.get("alarms") or []),
                                             "event_scripts": [s.get("eventid") for s in (m.get("eventScripts") or []) if isinstance(s, dict)]}
                                            for k, m in c["raw"]["members"].items()]}
            elif c["kind"] == "instance":
                d = c["raw"]["instance"]
                c["summary"] = {"type": self.type_ref(udt_key, c, d.get("typeId")),
                                "type_path": d.get("typeId"), "parameters": d.get("parameters"),
                                "overrides": len(c["raw"]["overrides"])}
            elif c["kind"] == "folder":
                tags = c["raw"]["tags"].values()
                c["summary"] = {"tags": len(c["raw"]["tags"]), "names": sorted(c["raw"]["tags"])[:200],
                                "data_types": dict(collections.Counter(str(t.get("dataType")) for t in tags)),
                                "value_sources": dict(collections.Counter(str(t.get("valueSource", "memory")) for t in tags)),
                                "alarms": sum(len(t.get("alarms") or []) for t in tags),
                                "history": sum(1 for t in tags if t.get("historyEnabled"))}
        for c in list(self.cards.values()):
            if c["kind"] == "udt":
                items = [(f"/raw/members/{sl.ptr_escape(k)}", k, m) for k, m in c["raw"]["members"].items()]
                items.insert(0, ("/raw/definition", "", c["raw"]["definition"]))
            elif c["kind"] == "instance":
                items = [(f"/raw/overrides/{sl.ptr_escape(k)}", k, m) for k, m in c["raw"]["overrides"].items()]
            elif c["kind"] == "folder":
                items = [(f"/raw/tags/{sl.ptr_escape(k)}", k, m) for k, m in c["raw"]["tags"].items()]
            else:
                continue
            alarm_ids, script_hashes = [], []
            for ptr, member, cfg in items:
                for i, a in enumerate(cfg.get("alarms") or []):
                    ac = self.new("alarm", f"{c['key']}/{member}/{a.get('name')}", owner=c["id"], member=member,
                                  source={"card": c["id"], "pointer": f"{ptr}/alarms/{i}"},
                                  summary=self.alarm_summary(a), raw=a)
                    alarm_ids.append(ac["id"])
                for i, s in enumerate(cfg.get("eventScripts") or []):
                    if isinstance(s, dict):
                        h = self.add_script(s.get("script"), c["id"], f"{ptr}/eventScripts/{i}/script",
                                            f"tag event: {s.get('eventid')}" + ("" if s.get("enabled", True) else " (disabled)"))
                        if h:
                            script_hashes.append(h)
            c.setdefault("summary", {})["alarm_cards"] = alarm_ids
            c["summary"]["script_groups"] = script_hashes
        # providers and images
        for pid, pv in sorted(tree.providers.items(), key=lambda kv: str(kv[0])):
            prow = [r for r in rows.values() if r["provider"] == pid]
            self.new("provider", tree.provider_name(pid), provider=tree.provider_name(pid),
                     provider_code=prov_code(pid), source={"table": "TAGPROVIDERSETTINGS"},
                     summary={"type": pv["type"], "enabled": pv["enabled"], "orphan": pv["orphan"], "rows": len(prow),
                              "kinds": dict(collections.Counter(tree.kind(r) for r in prow))}, raw=pv)
        imgs = [{"path": p, "type": t, "description": d, "width": w, "height": h, "size": s}
                for p, t, d, w, h, s in sl.table_rows(con, "IMAGES", "PATH, TYPE, DESCRIPTION, WIDTH, HEIGHT, SIZE")]
        self.new("images", "(images)", source={"table": "IMAGES"},
                 summary={"count": len(imgs), "formats": dict(collections.Counter(str(i["type"]) for i in imgs))},
                 raw={"images": imgs, "tag_groups": [dict(zip(("name",), r)) for r in sl.table_rows(con, "TAGGROUPS", "NAME")]})
        con.close()

    def type_ref(self, udt_key, card, type_id):
        if not type_id:
            return None
        pid = next((k for k, v in self.tree.providers.items() if self.tree.provider_name(k) == card["provider"]), None)
        tid = re.sub(r"^\[[^\]]*\]", "", str(type_id)).lstrip("/")
        return udt_key.get((pid, f"_types_/{tid}")) or {"unresolved": type_id}

    @staticmethod
    def alarm_summary(a: dict) -> dict:
        bound = {k: v.get("value") for k, v in a.items() if isinstance(v, dict) and "bindType" in v}
        return {"name": a.get("name"), "mode": a.get("mode", "(default)"), "priority": a.get("priority", "(default)"),
                "setpoint": a.get("setpointA"), "bound": bound,
                "properties": sorted(k for k in a if k not in ("name",))}

    # ---------------------------------------------------------------- scripts and cross references
    def build_scripts(self):
        lib = sorted(self.module_ids, key=len, reverse=True)
        for h, s in sorted(self.scripts.items(), key=lambda kv: (kv[1]["occurrences"][0]["card"], kv[0])):
            body = s["body"]
            calls = {}
            for dotted in lib:
                fns = re.findall(rf"\b{re.escape(dotted)}\.(\w+)", body)
                if fns:
                    calls[self.module_ids[dotted]] = sorted(set(fns))
            card = self.new("script", h, hash=h, source={"occurrences": len(s["occurrences"])},
                            summary={"locations": dict(collections.Counter(o["location"] for o in s["occurrences"])),
                                     "occurrences": s["occurrences"], "lines": body.count("\n") + 1,
                                     "system_calls": dict(collections.Counter(sl.SYSTEM_CALL.findall(body))),
                                     "library_calls": calls,
                                     "popups": re.findall(r"openPopup\([^,]*,\s*(?:view\s*=\s*)?['\"]([^'\"]+)['\"]", body),
                                     "navigates": re.findall(r"navigate\(\s*(?:page\s*=\s*)?['\"]([^'\"]+)['\"]", body),
                                     "tag_writes": len(re.findall(r"system\.tag\.write\w*", body))},
                            raw={"script": body})
            s["id"] = card["id"]
        for c in self.cards.values():   # replace hashes by script card IDs
            sm = c.get("summary") or {}
            if c["kind"] == "view":
                for b in sm["bindings"]:
                    b["scripts"] = [self.scripts[h]["id"] for h in b["scripts"]]
                for e in sm["events"]:
                    if e.get("script"):
                        e["script"] = self.scripts[e["script"]]["id"]
            if "script_groups" in sm:
                sm["script_cards"] = sorted({self.scripts[h]["id"] for h in sm.pop("script_groups")})
        for c in self.cards.values():
            if c["kind"] == "module":
                calls = {}
                for dotted in sorted(self.module_ids, key=len, reverse=True):
                    if dotted != c["dotted"]:
                        fns = re.findall(rf"\b{re.escape(dotted)}\.(\w+)", c["raw"]["code"])
                        if fns:
                            calls[self.module_ids[dotted]] = sorted(set(fns))
                c["summary"]["library_calls"] = calls

    def resolve_view(self, project: str, path: str) -> str | None:
        p, seen = project, 0
        while p and seen < 8:
            if (p, path) in self.view_ids:
                return self.view_ids[(p, path)]
            parent = next((c["summary"]["parent"] for c in self.cards.values()
                           if c["kind"] == "project" and c["project"] == p), None)
            p, seen = parent, seen + 1
        return None

    def xref(self) -> dict:
        x = {"embeds": {}, "embedded_by": collections.defaultdict(list), "popups": {}, "opened_by": collections.defaultdict(list),
             "missing_views": [], "routes": {}, "docks": {}, "script_callers": collections.defaultdict(list),
             "udt_hint": {}, "member_refs": {}}
        script_of = {o["card"]: [] for c in self.cards.values() if c["kind"] == "script" for o in c["summary"]["occurrences"]}
        for c in self.cards.values():
            if c["kind"] == "script":
                for o in c["summary"]["occurrences"]:
                    script_of[o["card"]].append(c)
                for m in c["summary"]["library_calls"]:
                    x["script_callers"][m].append(c["id"])
            if c["kind"] == "module":
                for m in c["summary"]["library_calls"]:
                    x["script_callers"][m].append(c["id"])
        for c in self.cards.values():
            if c["kind"] != "view":
                continue
            sm, emb, pops = c["summary"], [], []
            for e in sm["embeds"]:
                t = self.resolve_view(c["project"], e["path"])
                (emb.append(t) if t else x["missing_views"].append({"card": c["id"], "path": e["path"]}))
            targets = [e.get("view") for e in sm["events"] if e.get("type") == "popup"]
            targets += [p for s in script_of.get(c["id"], []) for p in s["summary"]["popups"]]
            for path in targets:
                t = self.resolve_view(c["project"], path) if path else None
                (pops.append(t) if t else x["missing_views"].append({"card": c["id"], "path": path}))
            x["embeds"][c["id"]] = sorted(set(emb))
            x["popups"][c["id"]] = sorted(set(pops))
            for t in set(emb):
                x["embedded_by"][t].append(c["id"])
            for t in set(pops):
                x["opened_by"][t].append(c["id"])
            x["member_refs"][c["id"]] = sorted(self.member_refs(c, script_of.get(c["id"], [])))
        for c in self.cards.values():
            if c["kind"] == "page-config":
                for r in c["summary"]["routes"]:
                    x["routes"][f"{c['id']}{r['route']}"] = self.resolve_view(c["project"], r["view"] or "")
                    for d in r["docks"]:
                        x["docks"][f"{c['id']}:{d['id']}"] = self.resolve_view(c["project"], d["view"] or "")
                for d in c["summary"]["shared_docks"]:
                    x["docks"][f"{c['id']}:{d['id']}"] = self.resolve_view(c["project"], d["view"] or "")
        udts = {c["id"]: {m["path"].lower() for m in c["summary"]["members"]} for c in self.cards.values() if c["kind"] == "udt"}
        for vid, refs in x["member_refs"].items():
            want = {r.lower() for r in refs}
            if not want:
                continue
            scored = sorted(((len(want & ms) / len(want), uid) for uid, ms in udts.items() if want & ms), reverse=True)
            x["udt_hint"][vid] = [{"udt": u, "score": round(s, 2)} for s, u in scored[:3] if s >= 0.3]
            self.cards[vid]["summary"]["udt_hint"] = x["udt_hint"][vid]
        for k in ("embedded_by", "opened_by", "script_callers"):
            x[k] = {a: sorted(set(b)) for a, b in x[k].items()}
        for c in self.cards.values():
            if c["kind"] == "view":
                c["summary"].update(embedded_by=x["embedded_by"].get(c["id"], []), opened_by=x["opened_by"].get(c["id"], []),
                                    embeds_views=x["embeds"].get(c["id"], []), opens_popups=x["popups"].get(c["id"], []))
        return x

    @staticmethod
    def member_refs(card, scripts) -> set:
        refs = set()
        for b in card["summary"]["bindings"]:
            t = b.get("target")
            if b["type"] == "tag" and isinstance(t, str):
                m = re.search(r"\}\s*/?(.+)$", t)
                if m and "{" not in m.group(1):
                    refs.add(m.group(1).strip("/"))
        for s in scripts:
            refs.update(r.strip("/") for r in re.findall(r"\+\s*['\"](/[\w ./]+)['\"]", s["raw"]["script"]))
        return {r for r in refs if r}

    # ---------------------------------------------------------------- write
    def write(self) -> dict:
        out = sl.fresh_dir(self.study.extract / "cards")
        for cid, card in self.cards.items():
            sl.write_json(out / cid[0] / f"{cid}.json", card)
        return dict(collections.Counter(c["kind"] for c in self.cards.values()))


def batches(cards: dict, config: dict) -> dict:
    """The batch plan of COB-PROMPTS-02 Table 1, from the study's batch configuration."""
    lim_cards, lim_tokens = config.get("part_limit_cards", 40), config.get("part_limit_tokens", 150000)
    size = {cid: len(json.dumps(c, ensure_ascii=False)) // 4 for cid, c in cards.items()}
    of = lambda kind: sorted(cid for cid, c in cards.items() if c["kind"] == kind)
    used = collections.Counter()
    plan = {}

    def parts(batch, units, attached_of=lambda u: [], start=1):
        """units: lists of primary card IDs that must stay together (a UDT family, a view)."""
        n, cur, att, tok = start, [], [], 0
        for unit in units:
            extra = [a for u in unit for a in attached_of(u)]
            t = sum(size[i] for i in unit + extra)
            if cur and (len(cur) + len(unit) > lim_cards or tok + t > lim_tokens):
                plan[f"{batch}-{n}"] = {"cards": cur, "attached": att, "tokens_est": tok}
                n, cur, att, tok = n + 1, [], [], 0
            cur, att, tok = cur + unit, att + extra, tok + t
        if cur:
            plan[f"{batch}-{n}"] = {"cards": cur, "attached": att, "tokens_est": tok}
        for p in [k for k in plan if k.startswith(batch + "-")]:
            used.update(plan[p]["cards"] + plan[p]["attached"])
        return n + 1 if cur else n

    code = lambda c: c.get("project_code")
    view_in = lambda c, proj, prefixes: code(c) == proj and any(c["path"] == p or c["path"].startswith(p + "/") for p in prefixes)
    plan["B0-1"] = {"cards": of("project") + of("page-config") + of("provider"), "attached": [],
                    "reads": ["MANIFEST.json", "CENSUS.md", "BATCHES.json"]}
    used.update(plan["B0-1"]["cards"])
    # B1: UDT families by group, with instances and alarms attached
    fam = collections.defaultdict(list)
    for cid in of("udt"):
        fam[cards[cid]["name"]].append(cid)
    inst_of = collections.defaultdict(list)
    for cid in of("instance"):
        t = cards[cid]["summary"].get("type")
        if isinstance(t, str):
            inst_of[t].append(cid)
    attached = lambda u: inst_of.get(u, []) + cards[u]["summary"].get("alarm_cards", [])
    groups = config.get("b1_groups", [])
    n = 1
    grouped = set()
    for g in groups:
        units = [fam[f] for f in g["families"] if f in fam]
        grouped |= {f for f in g["families"] if f in fam}
        n = parts("B1", units, attached, n)
    rest = [fam[f] for f in sorted(fam) if f not in grouped]
    n = parts("B1", rest, attached, n)
    loose = [i for i in of("instance") if not isinstance(cards[i]["summary"].get("type"), str)]
    folder_alarms = lambda u: cards[u]["summary"].get("alarm_cards", [])
    n = parts("B1", [[f] for f in of("folder")] + [[i] for i in loose], folder_alarms, n)
    plan[f"B1-{n}"] = {"cards": [], "attached": [], "reads": ["out/B1"], "note": "UDT design across the families"}
    # B2: alarms
    alarm_fams = [f for f in config.get("alarm_families", []) if f in fam]
    plan["B2-1"] = {"cards": [u for f in alarm_fams for u in fam[f]], "attached": of("alarm"), "note": "alarm configuration"}
    alarm_x = [cid for cid in of("script") if any(o["location"].startswith("tag event: alarm") for o in cards[cid]["summary"]["occurrences"])]
    alarm_m = [cid for cid in of("module") if "alarm" in cards[cid]["path"].lower()]
    plan["B2-2"] = {"cards": alarm_x + alarm_m, "attached": [p for p in of("project") if code(cards[p]) in config.get("b2_projects", [])],
                    "note": "alarm roll-up"}
    used.update(plan["B2-1"]["cards"] + plan["B2-1"]["attached"] + plan["B2-2"]["cards"])
    # B3: alarm display
    alarm_views = [cid for cid in of("view") if any("alarm" in t for t in cards[cid]["summary"]["components"])
                   or any(h["udt"] in {u for f in alarm_fams for u in fam[f]} for h in cards[cid]["summary"].get("udt_hint", []))]
    plan["B3-1"] = {"cards": alarm_views, "attached": [s for s in of("style") if "alarm" in cards[s]["path"].lower()]}
    # B4, B5, B6: views
    b4 = config.get("b4", {})
    lib_views = [cid for cid in of("view") if view_in(cards[cid], b4.get("project"), b4.get("prefixes", []))]
    n = parts("B4", [[v] for v in lib_views])
    plan[f"B4-{n}"] = {"cards": [], "attached": [], "reads": ["out/B4"], "note": "faceplate anatomy"}
    b5 = config.get("b5", {})
    nav_views = [cid for cid in of("view") if any(view_in(cards[cid], pj, [pre]) for pj, pre in b5.get("views", []))
                 or code(cards[cid]) in b5.get("projects_all_views", [])]
    nav_mods = [cid for cid in of("module") if any(s in cards[cid]["path"] for s in b5.get("module_contains", []))]
    plan["B5-1"] = {"cards": nav_views + nav_mods, "attached": of("session") + of("page-config"), "reads": ["out/B1"]}
    used.update(nav_views + nav_mods + of("session") + of("page-config") + alarm_views)
    site = [cid for cid in of("view") if code(cards[cid]) in config.get("b6_projects", []) and cid not in used]
    other = [cid for cid in of("view") if cid not in used and cid not in lib_views and cid not in site]
    parts("B6", [[v] for v in site + other])
    # B7: scripts and modules
    parts("B7", [[m] for m in of("module")] + [[x] for x in of("script")])
    # B8: styles; themes and images
    parts("B8", [[s] for s in of("style")])
    plan["B8-T"] = {"cards": of("theme") + of("images"), "attached": []}
    used.update(of("theme") + of("images"))
    plan["B9-1"] = {"cards": [], "attached": [], "reads": ["out/B1", "out/B2", "out/B3", "out/B4", "out/B5", "out/B6", "out/B7", "out/B8"], "note": "standards practice"}
    plan["B9-2"] = {"cards": [], "attached": [], "reads": ["out/B1", "out/B2", "out/B3", "out/B4", "out/B5", "out/B6", "out/B7", "out/B8"], "note": "feature catalogue"}
    covered = {i for p in plan.values() for i in p.get("cards", []) + p.get("attached", [])}
    return {"parts": plan, "uncovered": sorted(set(cards) - covered)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--study", required=True)
    ap.add_argument("--config", help="batch configuration (default <study>/study/batches.config.json)")
    a = ap.parse_args(argv)
    study = sl.Study(a.study)
    b = Builder(study)
    b.build_projects()
    b.build_views()
    b.build_styles()
    b.build_themes()
    b.build_modules()
    b.build_tags()
    b.build_scripts()
    x = b.xref()
    counts = b.write()
    b.z.close()
    sl.write_json(study.extract / "xref.json", x)
    cfgp = Path(a.config) if a.config else study.work / "batches.config.json"
    plan = batches(b.cards, sl.read_json(cfgp) if cfgp.exists() else {})
    sl.write_json(study.extract / "BATCHES.json", plan)
    expected = b.manifest["counts"]
    checks = {"views": (counts.get("view", 0), expected["views"]),
              "style classes": (counts.get("style", 0), expected["style_classes"]),
              "script modules": (counts.get("module", 0), expected["script_modules"]),
              "UDT definitions": (counts.get("udt", 0), expected["udt_definitions"]),
              "alarm definitions": (counts.get("alarm", 0), expected["alarm_definitions"])}
    print("cards:", json.dumps(counts))
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    for k, (got, want) in checks.items():
        print(f"  {k}: {got} cards, manifest {want}{'' if got == want else '  MISMATCH'}")
    print(f"parts: {len(plan['parts'])}; uncovered cards: {len(plan['uncovered'])}; "
          f"missing view paths: {len(x['missing_views'])} ({len({v['path'] for v in x['missing_views']})} distinct)")
    return 1 if bad or plan["uncovered"] else 0


if __name__ == "__main__":
    sys.exit(main())
