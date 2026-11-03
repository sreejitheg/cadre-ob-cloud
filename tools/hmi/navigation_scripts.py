"""The scripts of the ASM frame (COB-160): appended to `cadre.hmi` (`scripts.HMI`), Jython 2.7, gateway scope.

Held apart from `scripts.py` so that the frame's functions merge without touching the rest of the library;
`scripts.py` appends `TEXT` to the library source, so these functions share `cadre.hmi`'s names
(`node_counts`, `alert_record`, `device_sources`, `_hierarchy`) and a view calls them as `cadre.hmi.<name>`.

API calls used: `system.alarm.queryStatus(path=, state=)` and the alarm event accessors the library already
uses (IGW:22-system-api-reference section 3.1; GF-06), and `system.date.format`, `system.date.fromMillis` as
`alarm_summary` uses them. No `system.perspective` call is made here: a popup, a dock or a navigation is
opened by the event script of the view that was clicked (IGW:23-perspective-scripting sections 4 to 6).

The frame's state lives in `session.custom` (written by the generator when a child is built with
`--frame asm`; see `navigation.session_custom`):

    frame          "asm" while the ASM frame is on, else "openbridge"
    floating       {popup id: slot} of the faceplates floated so far
    contentNode    the node id the Alarms and Trend pivot pages show; empty means the root
    pageInfo       {route: {"title", "level", "previous", "previousTitle", "next", "nextTitle"}}
    searchIndex    {"pages": [[route, title, node path, level]],
                    "devices": [[folder, kind, title, label, route, node path, faceplate 1 or 0]],
                    "tags": [[path, description, unit, device index or -1, tab]]}
    searchQuery    the text of the top bar's search field
    searchOpen     whether the in-page results panel is open (a key in the field opens it; Escape, a row, a click
                   outside the panel close it)
    navQuery       the text of the navigation dock's search box
    navPanel       what the one navigation dock lists: "pages" (the tree) or "support" (the support pages)
"""

TEXT = r'''

# ---------------------------------------------------------------------------------------------------
# The ASM frame (COB-160; DESIGN sections 3 to 6 of the eng02 ASM reimagining). Every function reads the
# frame's state from `session.custom` and answers plain lists and dicts for the views' bindings.
# ---------------------------------------------------------------------------------------------------
NODE_ROUTES = {"/node/alarms": "alarms", "/node/trend": "trend"}
FLOAT_SLOTS = 6
FLOAT_TOP = 90
FLOAT_RIGHT = 5
FLOAT_STEP = 24
SEARCH_GROUP_ROWS = 9
BANNER_ROWS = 3
ROW_DEFAULT = {"kind": "", "label": "", "second": "", "icon": "", "depth": 0, "selected": False, "disabled": False,
	"action": "", "route": "", "nodeId": "", "deviceId": "", "deviceKind": "", "deviceTitle": "",
	"deviceLabel": "", "tab": "", "close": ""}


def _custom(session, name, default=None):
	"""A value of `session.custom`, else `default`."""
	try:
		v = getattr(session.custom, name)
		if v is None:
			return default
		return v
	except Exception:
		return default


def _text(value):
	return unicode(value if value is not None else "")


def _row(**kw):
	"""One row of the frame's lists (`Framework/ASM/ListRow`): the defaults, then the given fields."""
	r = dict(ROW_DEFAULT)
	r.update(kw)
	if "counts" not in r:
		r["counts"] = _no_counts()
	return r


def _clock(ms):
	try:
		return system.date.format(system.date.fromMillis(long(ms)), "HH:mm:ss")
	except Exception:
		return ""


# --- several floating faceplates (COB-160, DESIGN section 6) ---------------------------------------------
def asm_frame(session):
	"""True while the session runs the ASM frame (`session.custom.frame`, written by `screen.py --frame asm`);
	a project built without the option, or before it, answers False and keeps the single floating faceplate."""
	return _text(_custom(session, "frame", "openbridge")) == "asm"


def float_id(device):
	"""The popup id of a device's floating faceplate: one popup per device, so that opening a device that is
	already floating addresses its own popup."""
	out = ""
	for ch in _text(device):
		if ch.isalnum():
			out += ch
		else:
			out += "_"
	return "fp_" + out


def float_slot(session, device):
	"""The place of a device's floating faceplate: a device keeps its slot, a new one takes the next of
	FLOAT_SLOTS, each FLOAT_STEP px from the one before."""
	taken = {}
	try:
		taken = dict(_custom(session, "floating", {}) or {})
	except Exception:
		taken = {}
	key = float_id(device)
	if key not in taken:
		if len(taken) >= 4 * FLOAT_SLOTS:
			taken = {}
		taken[key] = len(taken) % FLOAT_SLOTS
		try:
			session.custom.floating = taken
		except Exception:
			pass
	return int(taken[key])


def float_position(session, device):
	"""The popup position of a device's faceplate: the first 5 px from the right, each further one offset 24 px
	down and to the left."""
	n = float_slot(session, device)
	return {"top": FLOAT_TOP + FLOAT_STEP * n, "right": FLOAT_RIGHT + FLOAT_STEP * n}


def float_params(session, popup_id):
	"""The view parameters of a floating faceplate: the device `select_device` has just selected, with its
	style and the tab `open_device` named. The popup reads these, never `session.custom.selected*`, so that
	a second device does not redraw the first."""
	return {"popupId": _text(popup_id), "deviceId": _text(_custom(session, "selectedDevice", "")),
		"kind": _text(_custom(session, "selectedKind", "")), "style": _text(_custom(session, "selectedStyle", "openbridge")),
		"title": _text(_custom(session, "selectedTitle", "")), "label": _text(_custom(session, "selectedLabel", "")),
		"tab": _text(_custom(session, "selectedTab", ""))}


# --- the node of the current page ------------------------------------------------------------------------
def _node_by_id(session, node_id):
	for n in _hierarchy(session):
		if _text(n["id"]) == _text(node_id):
			return n
	return None


def _first_route(node):
	pages = list(node["pages"] or []) if node is not None else []
	return _text(pages[0]["route"]) if pages else ""


def frame_node(session, route):
	"""The node a page shows: the node whose pages include `route`, else, for the Alarms and Trend pivot
	pages, the node `session.custom.contentNode` names (the root while it is empty). None for a page
	that names no node."""
	nodes = _hierarchy(session)
	if route in NODE_ROUTES:
		wanted = _text(_custom(session, "contentNode", ""))
		found = _node_by_id(session, wanted)
		if found is None and len(nodes) > 0:
			found = nodes[0]
		return found
	here = None
	for n in nodes:
		if len([p for p in (n["pages"] or []) if p["route"] == route]) > 0:
			here = n
	return here


def _chain(session, node):
	by_id = dict((_text(n["id"]), n) for n in _hierarchy(session))
	chain = []
	seen = 0
	while node is not None and seen < 64:
		chain.insert(0, node)
		node = by_id.get(_text(node["parentId"] or ""))
		seen += 1
	return chain


def frame_crumbs(session, route):
	"""The breadcrumb of the ASM frame: the nodes from the root to the current page's node, each with its
	id (the crumb's popup names it), name, the route of its first page, its counts and whether it is the
	first and the last. Empty for a page that names no node."""
	chain = _chain(session, frame_node(session, route))
	if not chain:
		return []
	counts = node_counts(session)
	out = []
	for i, n in enumerate(chain):
		out.append({"nodeId": _text(n["id"]), "name": _text(n["name"]), "route": _first_route(n),
			"counts": counts.get(_text(n["id"]), _no_counts()), "first": i == 0, "last": i == len(chain) - 1})
	return out


def crumb_menu(session, node_id):
	"""The rows of a crumb's popup (DESIGN section 4): Show (Mimic, Alarms, Trend of the node) and Areas
	(its child nodes, each with its badges)."""
	node = _node_by_id(session, node_id)
	if node is None:
		return []
	counts = node_counts(session)
	first = _first_route(node)
	nid = _text(node["id"])
	rows = [_row(kind="group", label="Show"),
		_row(kind="show", label="Mimic", icon="home", action="route" if first else "", route=first,
			nodeId=nid, disabled=not first, close="crumbPopup"),
		_row(kind="show", label="Alarms", icon="alert-list", action="alarms", nodeId=nid, close="crumbPopup"),
		_row(kind="show", label="Trend", icon="trend", action="trend", nodeId=nid, close="crumbPopup")]
	kids = [n for n in _hierarchy(session) if _text(n["parentId"] or "") == nid]
	if kids:
		rows.append(_row(kind="group", label="Areas"))
	for n in kids:
		route = _first_route(n)
		rows.append(_row(kind="area", label=_text(n["name"]), action="route" if route else "alarms", route=route,
			nodeId=_text(n["id"]), counts=counts.get(_text(n["id"]), _no_counts()), close="crumbPopup"))
	return rows


# --- the navigation dock (DESIGN section 3) -------------------------------------------------------------
def _children(session, parent_id):
	return [n for n in _hierarchy(session) if _text(n["parentId"] or "") == _text(parent_id)]


def _node_path(n):
	return _text(n["path"]) if n is not None else ""


def nav_tree(session, query, route):
	"""The rows of the navigation dock: the tree of the hierarchy's nodes, each with its badges and its
	pages beneath it, the current page selected; with a query, a flat list of the nodes and pages that match
	it. A project with no hierarchy lists its navigation items."""
	q = _text(query).strip().lower()
	nodes = _hierarchy(session)
	counts = node_counts(session)
	rows = []
	if not nodes:
		try:
			items = list(session.custom.nav["items"])
		except Exception:
			items = []
		for it in items:
			if q and q not in _text(it["label"]).lower():
				continue
			rows.append(_row(kind="page", label=_text(it["label"]), icon=_text(it["icon"]), route=_text(it["path"]),
				action="route", selected=it["path"] == route, close="nav"))
		return rows

	def node_row(n, depth, flat):
		r = _first_route(n)
		return _row(kind="node", label=_text(n["name"]), second=_node_path(n) if flat else "", depth=depth,
			counts=counts.get(_text(n["id"]), _no_counts()), nodeId=_text(n["id"]), route=r,
			action="route" if r else "alarms", close="nav")

	def page_row(n, p, depth, flat):
		return _row(kind="page", label=_text(p["label"]), second=_node_path(n) if flat else "", depth=depth,
			route=_text(p["route"]), action="route", selected=p["route"] == route, nodeId=_text(n["id"]), close="nav")

	if q:
		for n in nodes:
			if q in _text(n["name"]).lower() or q in _text(n["path"]).lower():
				rows.append(node_row(n, 0, True))
			for p in (n["pages"] or []):
				if q in _text(p["label"]).lower() or q in _text(p["route"]).lower():
					rows.append(page_row(n, p, 0, True))
		return rows

	def walk(n, depth):
		rows.append(node_row(n, depth, False))
		for p in (n["pages"] or []):
			rows.append(page_row(n, p, depth + 1, False))
		for k in _children(session, n["id"]):
			walk(k, depth + 1)
	for n in nodes:
		if not _text(n["parentId"] or ""):
			walk(n, 0)
	return rows


def nav_footer(session, route):
	"""The footer of the navigation dock: the support pages, those navigation items that name no node (the
	trend page and the like) and the frame's footer items (the alerts page)."""
	rows = []
	try:
		items = list(session.custom.nav["items"])
	except Exception:
		items = []
	try:
		footer = list(session.custom.nav["footer"])
	except Exception:
		footer = []
	for it in items:
		node = ""
		try:
			node = _text(it["node"])
		except Exception:
			pass
		if node == "" and len(_hierarchy(session)) > 0:
			rows.append(_row(kind="page", label=_text(it["label"]), icon=_text(it["icon"]), route=_text(it["path"]),
				action="route", selected=it["path"] == route, close="nav"))
	for it in footer:
		rows.append(_row(kind="page", label=_text(it["label"]), icon=_text(it["icon"]), route=_text(it["path"]),
			action="route", selected=it["path"] == route, close="nav"))
	return rows


def nav_support(session, route):
	"""The support list of the navigation dock (L4, `navPanel` "support"): all alarms (the Alarms pivot page of the
	root node), then the footer rows of `nav_footer` (the navigation items that name no node: trends, tools; and
	the alerts page)."""
	rows = [_row(kind="page", label="All alarms", icon="alert-list", action="alarms", nodeId="",
		selected=route == "/node/alarms", close="nav")]
	return rows + nav_footer(session, route)


# --- the page header (DESIGN section 3 item 2) ----------------------------------------------------------
def page_header(session, route):
	"""The page header of a route: the title and its display level, the node the pivot (Mimic, Alarms,
	Trend) acts on, the node's pages as tabs where it has several, and the previous and next pages."""
	out = {"title": page_title(session, route), "level": "", "nodeId": "", "mode": "mimic", "mimicRoute": "",
		"tabs": [], "previous": {"route": "", "title": "", "enabled": False},
		"next": {"route": "", "title": "", "enabled": False}}
	info = {}
	try:
		info = dict(dict(_custom(session, "pageInfo", {}) or {}).get(route) or {})
	except Exception:
		info = {}
	node = frame_node(session, route)
	if route in NODE_ROUTES:
		out["mode"] = NODE_ROUTES[route]
		out["title"] = (_text(node["name"]) if node is not None else "") + (" alarms" if route == "/node/alarms" else " trend")
	elif info:
		out["title"] = _text(info.get("title") or out["title"])
		out["level"] = _text(info.get("level") or "")
		for k in ("previous", "next"):
			target = _text(info.get(k) or "")
			out[k] = {"route": target, "title": _text(info.get(k + "Title") or ""), "enabled": target != ""}
	if node is not None:
		out["nodeId"] = _text(node["id"])
		out["mimicRoute"] = _first_route(node)
		pages = list(node["pages"] or [])
		if len(pages) > 1 and route not in NODE_ROUTES:
			out["tabs"] = [{"label": _text(p["label"]), "route": _text(p["route"]), "selected": p["route"] == route}
				for p in pages]
	return out


def node_devices(session, node_id):
	"""The device folders of a node and of every node beneath it ('' means every node)."""
	nodes = _hierarchy(session)
	want = set()
	if _text(node_id) == "":
		return [_text(d) for n in nodes for d in (n["devices"] or [])]
	todo = [_text(node_id)]
	seen = 0
	while todo and seen < 256:
		cur = todo.pop()
		want.add(cur)
		todo += [_text(n["id"]) for n in nodes if _text(n["parentId"] or "") == cur]
		seen += 1
	return [_text(d) for n in nodes if _text(n["id"]) in want for d in (n["devices"] or [])]


def node_sources(session, node_id):
	"""The alarm source patterns of a node's devices, comma separated, as the stock alarm table takes them
	(GF-52); the no-match pattern while the node has no device with an alarm, never the whole scope."""
	out = []
	for d in node_devices(session, node_id):
		for p in device_sources(session, d):
			if p != NO_MATCH and p not in out:
				out.append(p)
	return ",".join(out) if out else NO_MATCH


def node_trends(session, node_id, hours):
	"""The trend cards of a node: the entries of `session.custom.trends` whose device the node or a node
	beneath it holds, each with the page's range."""
	want = set(node_devices(session, node_id))
	out = []
	for t in (_custom(session, "trends", []) or []):
		if _text(t["deviceId"]) in want:
			r = dict(t)
			r["hours"] = hours
			out.append(r)
	return out


# --- the global search (DESIGN section 5) ----------------------------------------------------------------
def _rank(q, fields):
	"""0 exact on the id (the first field), 1 a prefix or an exact match of another field, 2 a substring,
	9 no match."""
	best = 9
	for i, f in enumerate(fields):
		s = _text(f).lower()
		if not s:
			continue
		if s == q:
			r = 0 if i == 0 else 1
		elif s.startswith(q):
			r = 1
		elif q in s:
			r = 2
		else:
			continue
		if r < best:
			best = r
	return best


def _ranked(q, entries, fields_of):
	scored = []
	for i, e in enumerate(entries):
		r = _rank(q, fields_of(e))
		if r < 9:
			scored.append((r, i))
	scored.sort()
	return [entries[i] for r, i in scored[:SEARCH_GROUP_ROWS]]


def search(session, query):
	"""The rows of the top bar's search popup: Pages, Devices and Tags that match `query`, in that order,
	each group ranked exact id, prefix, substring; at most 30 rows in all, the group titles included."""
	q = _text(query).strip().lower()
	if q == "":
		return []
	index = dict(_custom(session, "searchIndex", {}) or {})
	pages = list(index.get("pages") or [])
	devices = list(index.get("devices") or [])
	tags = list(index.get("tags") or [])
	rows = []
	found = _ranked(q, pages, lambda p: [_text(p[0]).lstrip("/"), p[1], p[2]])
	if found:
		rows.append(_row(kind="group", label="Pages"))
	for p in found:
		rows.append(_row(kind="page", label=_text(p[1]), second=_text(p[2]) + ("  " + _text(p[3]) if p[3] else ""),
			icon="home", action="route", route=_text(p[0]), close="search"))
	found = _ranked(q, devices, lambda d: [_text(d[0]).split("/")[-1], d[2], d[3], d[1]])
	if found:
		rows.append(_row(kind="group", label="Devices"))
	for d in found:
		rows.append(_device_row(d, "home", _text(d[3]) or _text(d[5])))
	found = _ranked(q, tags, lambda t: [_text(t[0]).split("/")[-1], t[0], t[1], t[2]])
	if found:
		rows.append(_row(kind="group", label="Tags"))
	for t in found:
		d = None
		try:
			if int(t[3]) >= 0:
				d = devices[int(t[3])]
		except Exception:
			d = None
		second = _text(t[1]) + ("  " + _text(t[2]) if t[2] else "")
		if d is not None:
			row = _device_row(d, _text(t[4]) or "home", second)
			row["kind"] = "tag"
			row["label"] = _text(t[0]).split("/")[-1]
			row["icon"] = "trend"
			rows.append(row)
		else:
			rows.append(_row(kind="tag", label=_text(t[0]).split("/")[-1], second=second, icon="trend", disabled=True,
				close="search"))
	return rows[:30]


def _device_row(d, tab, second):
	"""A search row for a device: its page, then its faceplate on `tab` where the kind has one."""
	has = len(d) > 6 and int(d[6]) == 1
	return _row(kind="device", label=_text(d[2]) or _text(d[0]).split("/")[-1], second=_text(second), icon="home",
		action="route" if d[4] else "", route=_text(d[4]), deviceId=_text(d[0]) if has else "", deviceKind=_text(d[1]),
		deviceTitle=_text(d[2]), deviceLabel=_text(d[3]), tab=tab, close="search")


def search_first(session, query):
	"""The first row of a search that acts, else None: what Enter in the search field does."""
	for r in search(session, query):
		if r["kind"] != "group" and not r["disabled"]:
			return r
	return None


# --- the bottom alarm banner (DESIGN section 3 item 4) ----------------------------------------------------
def banner_alarms(session, route=""):
	"""The three most important alarms (unacknowledged first, then priority, then newest) as rows for
	`Framework/ASM/BannerRow`, with the active alarms counted by priority. With the route of the open page (L5), those
	of the page's node and of every node beneath it: the sources of the node's devices (`node_sources`); on the Alarms and
	Trend pivot pages, those of the node `session.custom.contentNode` names. A page with no node, the pivot
	pages of the root, and a call without a route show the session's whole alarm scope. The counts follow the rows."""
	out = {"rows": [], "counts": _no_counts()}
	try:
		scope = session.custom.alarmScope
	except Exception:
		scope = "*"
	paths = [scope or "*"]
	route = _text(route)
	node = frame_node(session, route) if route else None
	if node is not None and route in NODE_ROUTES and _text(_custom(session, "contentNode", "")) == "":
		node = None
	if node is not None:
		paths = _paths(scope, node_sources(session, _text(node["id"])))
	try:
		events = system.alarm.queryStatus(path=paths, state=LIST_STATES)
	except Exception:
		return out
	devices = _devices_of(session)
	by_folder = dict((_text(d["folder"]), d) for d in devices)
	owner = {}
	for n in _hierarchy(session):
		for d in (n["devices"] or []):
			owner[_text(d)] = _text(n["name"])
	recs = []
	for e in events:
		rec = alert_record(e, devices)
		priority = _text(_accessor(e, "getPriority"))
		active = rec["active"] is True
		unacked = rec["acknowledged"] is False
		if active:
			c = out["counts"]
			if priority in c:
				c[priority] += 1
			c["total"] += 1
			if unacked:
				c["unacked"] += 1
		rank = PRIORITIES.index(priority) if priority in PRIORITIES else len(PRIORITIES) - 1
		recs.append((0 if unacked else 1, rank, -(rec["time"] or 0), rec, priority, active, unacked))
	recs.sort(key=lambda r: (r[0], r[1], r[2]))
	for flag, rank, neg, rec, priority, active, unacked in recs[:BANNER_ROWS]:
		folder = _text(rec["tagId"])
		d = by_folder.get(folder)
		if active and unacked:
			state = "Unacknowledged"
		elif active:
			state = "Acknowledged"
		else:
			state = "Cleared, unacknowledged"
		out["rows"].append({"id": _text(rec["id"]), "priority": priority, "status": PRIORITY_STATUS.get(priority, "") or "neutral",
			"unacked": unacked, "time": _clock(rec["time"]), "node": owner.get(folder, ""),
			"tag": _text(d["title"]) if d is not None else folder.split("/")[-1], "text": _text(rec["text"]),
			"state": state, "deviceId": folder if d is not None else "", "deviceKind": _text(d["kind"]) if d is not None else "",
			"deviceTitle": _text(d["title"]) if d is not None else "", "deviceLabel": _text(d["label"]) if d is not None else ""})
	return out


# --- the OpenBridge frame (`--frame ob`, tools/hmi/obframe.py) ----------------------------------------------
# The Cadre priority to the count of OpenBridge's `AlertCounts` (wiki 13 section 11.1: Critical the critical colour,
# High alarm, Medium warning, Low caution, Diagnostic its own level), for the `alerts` of a navigation item.
OB_COUNT_OF = {"Critical": "countLevelCritical", "High": "countAlarm", "Medium": "countWarning", "Low": "countCaution",
	"Diagnostic": "countLevelDiagnostic"}


def ob_items(kind, rows, state=None, icons=None):
	"""The item objects of the module's frame components (`items` of `cadre.ob.alertmenu` and
	`cadre.ob.navigationmenu`: `tag`, the element's attributes, `id`, `children`), built from rows the library already
	answers. It reads nothing but its arguments (and formats the times).

	`kind` "alerts": `rows` are `alarm_list` records, `state` whether the session may acknowledge (W8). A row is an
	`obc-alert-menu-item` whose `id` is the alarm event's id; ACK shows while the alarm is unacknowledged and is disabled
	without the permission (the scripts refuse anyway, `ack`).
	`kind` "nav": `rows` are navigation items (`nav_items`, or the footer: `label`, `path`, `icon`, optional `counts`),
	`state` the current route, `icons` the OpenBridge icon names the module bundles. An item's `id` is its route and an
	item that names a node shows the node's counts as `alerts`. An icon outside `icons` is left out."""
	out = []
	if kind == "alerts":
		for r in (rows or []):
			acked = r["acknowledged"] is not False
			day = ""
			try:
				day = system.date.format(system.date.fromMillis(long(r["time"])), "d MMM")
			except Exception:
				pass
			out.append({"tag": "obc-alert-menu-item", "id": _text(r["id"]), "title": _text(r["text"]),
				"description": _text(r["source"]), "day": day, "time": _clock(r["time"]),
				"status": "acknowledged" if acked else "unacknowledged",
				"primaryActionState": "enabled" if state else "disabled",
				"children": [{"tag": "obc-alert-icon", "slot": "alert-icon", "type": r["type"],
					"active": r["active"] is True, "acknowledged": acked}]})
		return out
	for it in (rows or []):
		path = _text(it["path"])
		icon = ""
		counts = None
		try:
			icon = _text(it["icon"])
		except Exception:
			pass
		try:
			counts = it["counts"]
		except Exception:
			pass
		item = {"tag": "obc-navigation-item", "id": path, "label": _text(it["label"]), "checked": path == _text(state)}
		if icon and icon in (icons or []):
			item["hasIcon"] = True
			item["children"] = [{"tag": "obi-" + icon, "slot": "icon"}]
		if counts is not None and counts["total"] > 0:
			item["alerts"] = dict((OB_COUNT_OF[p], counts[p]) for p in OB_COUNT_OF)
		out.append(item)
	return out
'''
