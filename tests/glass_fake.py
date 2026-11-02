"""A fake gateway for the tests of `tools/compare/glass_gates.py`: a local HTTP server whose client page implements,
in a few lines of script, the frame behaviour the gates drive (search panel, zoom, docks, popups, banner, alert list
with Ack selected, Ack all and Confirm, a sign-in page), and a fake of `hmi.deploy` that writes tags into the
server's state. It proves the gates' control flow only: what the real glass does is measured on the gateway.

Only synthetic names are used (`tests/fixtures/asm-*.json`)."""
import http.server
import json
import threading
import urllib.parse

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>fake client</title>
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<style>
html,body{margin:0;height:100%;touch-action:pan-x pan-y;font:14px sans-serif}
.dock-head,.dock-nav,.dock-fp,.dock-banner{box-sizing:border-box}
.dock-head{position:fixed;left:0;top:0;right:0;height:84px;background:#e8e8e8;z-index:5}
.dock-head svg{position:absolute;top:8px;width:28px;height:28px}
.dock-head input{position:absolute;top:8px;left:220px;width:260px;height:28px}
#crumb{position:absolute;top:52px;left:20px;cursor:pointer}
#count{position:absolute;top:12px;right:120px;font-weight:700}
.dock-banner{position:fixed;left:0;right:0;bottom:0;height:76px;background:#f4f4f4;z-index:5;padding:6px 12px}
.dock-nav{position:fixed;left:0;top:84px;width:320px;bottom:76px;background:#fafafa;z-index:6;padding:8px}
.dock-fp{position:fixed;right:0;top:84px;width:400px;bottom:76px;background:#fafafa;z-index:6;padding:8px}
#wrap{position:absolute;left:0;top:84px;bottom:76px;right:0}
#cadre-canvas{width:100%;height:100%;overflow:hidden;position:relative}
.ia_popup{position:fixed;background:#fff;border:1px solid #888;z-index:40;padding:8px}
.zoom{position:absolute;top:4px;right:8px;z-index:3}
.obj{position:absolute}
#panel{position:fixed;left:220px;top:40px;width:420px;background:#fff;border:1px solid #888;z-index:50;padding:6px}
table{border-collapse:collapse} td{border:1px solid #ccc;padding:4px 8px}
</style></head><body>
<div id="head" class="dock-head">
<svg viewBox="0 0 28 28" id="i0" style="left:8px"><rect width="28" height="28"/></svg>
<svg viewBox="0 0 28 28" id="i1" style="left:48px"><rect width="28" height="28"/></svg>
<input id="search" placeholder="Search pages, devices, tags" autocomplete="off">
<svg viewBox="0 0 28 28" id="i2" style="right:150px"><circle cx="14" cy="14" r="12"/></svg>
<span id="count">0</span>
<svg viewBox="0 0 28 28" id="i3" style="right:90px"><circle cx="14" cy="14" r="12"/></svg>
<svg viewBox="0 0 28 28" id="i4" style="right:40px"><circle cx="14" cy="14" r="12"/></svg>
<span id="crumb"></span></div>
<div id="nav" class="dock-nav" hidden></div>
<div id="fpdock" class="dock-fp" hidden></div>
<div id="wrap"><div id="cadre-canvas"><div class="zoom"><button id="zin">+</button><button id="zout">-</button></div>
<div id="page"></div></div></div>
<div id="banner" class="dock-banner"></div>
<script>
var CFG = __CFG__;
var BASE = location.pathname.slice(0, location.pathname.indexOf(CFG.project) + CFG.project.length);
var route = location.pathname.slice(BASE.length) || '/';
var $ = function (i) { return document.getElementById(i); };
function div(cls, txt) { var d = document.createElement('div'); if (cls) d.className = cls; if (txt !== undefined) d.textContent = txt; return d; }
var page = CFG.pages.filter(function (p) { return p.route === route; })[0];
var state = {alarms: []};
var scale = 1, fitScale = 1, signed = document.cookie.indexOf('signed=1') >= 0, mute = false, colour = false;
function nav(r) { location.href = BASE + r; }
function fit() {
  var c = $('cadre-canvas'), w = page ? page.canvas.w : 800, h = page ? page.canvas.h : 600;
  var avail = $('wrap').getBoundingClientRect();
  fitScale = Math.min(1, avail.width / w, avail.height / h);
  scale = fitScale; apply();
}
function apply() { var p = $('page'); p.style.transform = 'scale(' + scale.toFixed(3) + ')'; p.style.transformOrigin = '0 0'; p.style.width = (page ? page.canvas.w : 800) + 'px'; p.style.height = (page ? page.canvas.h : 600) + 'px'; }
function dockOpen(tag) {
  var d = CFG.devices.filter(function (x) { return x.tag === tag; })[0]; if (!d) return;
  $('fpdock').hidden = false; $('fpdock').textContent = '';
  $('fpdock').appendChild(div('', d.tag + ' ' + d.label));
  var b = document.createElement('button'); b.textContent = 'Float'; b.onclick = function () { floatOpen(tag); }; $('fpdock').appendChild(b);
  $('wrap').style.right = '400px'; sessionStorage.setItem('dock', tag); fit();
}
function floatOpen(tag) {
  $('fpdock').hidden = true; $('wrap').style.right = '0'; sessionStorage.removeItem('dock');
  var f = div('ia_popup', tag + ' (floating)'); f.id = 'float'; f.style.left = '500px'; f.style.top = '200px';
  var b = document.createElement('button'); b.textContent = 'Dock'; b.onclick = function () { f.remove(); dockOpen(tag); }; f.appendChild(b);
  document.body.appendChild(f); fit();
}
function closePopups() { document.querySelectorAll('.ia_popup').forEach(function (e) { if (e.id !== 'float') e.remove(); }); $('nav').hidden = true; }
function popup(id, text) { closePopups(); var p = div('ia_popup', text); p.id = id; p.style.left = (innerWidth - 260) + 'px'; p.style.top = '90px'; p.style.width = '200px'; document.body.appendChild(p); return p; }
function render() {
  var pg = $('page'); pg.textContent = '';
  if (!page) { pg.appendChild(div('', route === '/alerts' ? '' : 'Library page ' + route)); }
  else {
    page.objects.forEach(function (o) {
      var e;
      if (o.el) { e = document.createElement(o.el); e.__txt = o.text; if (e.attachShadow) { var r = e.attachShadow({mode: 'open'}); var s = document.createElement('span'); s.textContent = o.text; r.appendChild(s); e.__s = s; } }
      else e = div('', o.text);
      if (o.device) { e.addEventListener('click', function () { dockOpen(o.device); }); }
      e.className = 'obj'; e.style.left = o.x + 'px'; e.style.top = o.y + 'px'; e.style.width = o.w + 'px'; e.style.height = '24px'; e.__o = o;
      pg.appendChild(e);
    });
    if (page.medium) { var s = document.createElementNS('ht' + 'tp://www.w3.org/2000/svg', 'svg'); s.setAttribute('width', 100); s.setAttribute('height', 20);
      var l = document.createElementNS('ht' + 'tp://www.w3.org/2000/svg', 'line'); l.setAttribute('x1', 0); l.setAttribute('y1', 10); l.setAttribute('x2', 90); l.setAttribute('y2', 10); l.id = 'pipe';
      l.style.stroke = '#777'; s.appendChild(l); s.style.position = 'absolute'; s.style.left = '10px'; s.style.top = '300px'; pg.appendChild(s);
      var cb = document.createElement('button'); cb.textContent = 'Color'; cb.style.position = 'absolute'; cb.style.left = '10px'; cb.style.top = '330px';
      cb.onclick = function () { colour = !colour; l.style.stroke = colour ? '#2c7fb8' : '#777'; }; pg.appendChild(cb); }
    if (page.objects.some(function (o) { return o.el; })) { var rb = document.createElement('button'); rb.textContent = 'Readout'; rb.style.position = 'absolute'; rb.style.left = '10px'; rb.style.top = '360px';
      rb.onclick = function () { mute = !mute; document.querySelectorAll('.obj').forEach(function (e) { if (e.__s) e.__s.textContent = mute ? '' : e.__txt; }); }; pg.appendChild(rb); }
  }
  if (route === '/alerts') {
    var t = document.createElement('table');
    state.alarms.filter(function (a) { return a.listed; }).forEach(function (a) {
      var tr = document.createElement('tr'); tr.setAttribute('data-alarm-row', '1'); tr.__a = a;
      var c0 = document.createElement('td'); c0.textContent = a.sel ? '[x]' : '[ ]'; c0.style.width = '32px';
      var c1 = document.createElement('td'); c1.textContent = a.desc; var c2 = document.createElement('td'); c2.textContent = (a.active ? 'Active' : 'Cleared') + ', ' + (a.acked ? 'Acknowledged' : 'Unacknowledged');
      tr.appendChild(c0); tr.appendChild(c1); tr.appendChild(c2); tr.onclick = function () { a.sel = !a.sel; render(); }; t.appendChild(tr);
    });
    pg.appendChild(t);
    var live = function () { return state.alarms.filter(function (a) { return a.listed; }); };
    var custom = function () { var n = live().filter(function (a) { return !a.acked; }).length;
      return {unacked: n, selected: live().filter(function (a) { return a.sel; }).map(function (a) { return a.tag; }),
              ackPending: confirming ? {text: 'Acknowledge ' + n + ' alarm' + (n === 1 ? '' : 's') + '?'} : null}; };
    var b1 = button('Ack selected', function () { return live().some(function (a) { return a.sel; }); }, custom, function () { post('/ack', {tags: live().filter(function (a) { return a.sel; }).map(function (a) { return a.tag; })}); });
    var b2 = button('Ack all', function () { return true; }, custom, function () { confirming = true; render(); });
    pg.appendChild(b1); pg.appendChild(b2);
    if (confirming) { pg.appendChild(button('Confirm', function () { return true; }, custom, function () { confirming = false; post('/ack', {tags: state.alarms.map(function (a) { return a.tag; })}); })); }
  }
  if (CFG.testpage && route === CFG.testpage.route) testPage(pg);
  var shown = state.alarms.filter(function (a) { return a.listed && page && a.shows.indexOf(route) >= 0; });
  $('banner').textContent = shown.map(function (a) { return a.desc; }).join('; ');
  $('count').textContent = String(state.alarms.filter(function (a) { return a.active; }).length);
}

function fibre(el, enabled, custom) {
  el['__reactFiber$f'] = {memoizedProps: {store: {props: {read: function () { return enabled(); }}, view: {custom: {read: function () { return custom(); }}}}}, return: null};
}
function button(text, enabled, custom, click) {
  var b = document.createElement('div'); b.setAttribute('data-component', 'ia.input.button'); b.textContent = text;
  b.style.cssText = 'display:inline-block;margin:4px;padding:2px 8px;border:1px solid #888;cursor:pointer';
  b.addEventListener('click', function () { if (enabled()) click(); }); fibre(b, enabled, custom); return b;
}
var lampColour = 'off', pulse = null, testAlarms = [], testSel = {};
function testPage(pg) {
  var T = CFG.testpage, y = 10;
  function section(title, h) {
    var box = div('', ''); box.style.cssText = 'position:absolute;left:12px;top:' + y + 'px;width:900px;height:' + h + 'px;border:1px solid #bbb';
    var lab = div('ia_labelComponent', title); lab.style.cssText = 'position:absolute;left:4px;top:2px'; box.appendChild(lab);
    pg.appendChild(box); y += h + 10; return box;
  }
  var lamps = section(T.lamps.section, 150);
  var lamp = div('', ''); lamp.setAttribute('data-component', 'ia.display.view'); lamp.style.cssText = 'position:absolute;left:20px;top:40px;width:48px;height:48px';
  fibre(lamp, function () { return true; }, function () { return {}; });
  lamp['__reactFiber$f'].memoizedProps.store.props.read = function () { return lampColour; };
  lamps.appendChild(lamp);
  T.lamps.buttons.forEach(function (c, i) {
    var b = button(c, function () { return true; }, function () { return {}; }, function () { pulse = {kind: 'lamp', caption: c}; render(); });
    b.style.position = 'absolute'; b.style.left = (100 + 140 * (i % 5)) + 'px'; b.style.top = (40 + 40 * Math.floor(i / 5)) + 'px'; lamps.appendChild(b);
  });
  var al = section(T.alarms.section, 260);
  var raise = button(T.alarms.raise_all, function () { return true; }, function () { return {}; }, function () { pulse = {kind: 'raise'}; render(); });
  raise.style.cssText += ';position:absolute;left:20px;top:30px'; al.appendChild(raise);
  testAlarms.forEach(function (a, i) {
    var c = document.createElement('obc-checkbox'); c.style.cssText = 'position:absolute;display:inline-block;width:16px;height:16px;border:1px solid #333;background:' + (testSel[i] ? '#333' : '#fff') + ';left:20px;top:' + (70 + 24 * i) + 'px';
    c.addEventListener('click', function () { testSel[i] = !testSel[i]; render(); }); al.appendChild(c);
    var t = div('', 'Test alarm ' + (i + 1) + (a.acked ? ' Acknowledged' : ' Unacknowledged')); t.style.cssText = 'position:absolute;left:50px;top:' + (70 + 24 * i) + 'px'; al.appendChild(t);
  });
  var custom = function () { var n = testAlarms.filter(function (a) { return !a.acked; }).length;
    return {unacked: n, selected: Object.keys(testSel).filter(function (k) { return testSel[k] && !testAlarms[k].acked; }), ackPending: confirming ? {text: 'Acknowledge ' + n + ' alarm' + (n === 1 ? '' : 's') + '?'} : null}; };
  var sel = button('Ack selected', function () { return Object.keys(testSel).some(function (k) { return testSel[k] && !testAlarms[k].acked; }); }, custom,
    function () { Object.keys(testSel).forEach(function (k) { if (testSel[k]) { testAlarms[k].acked = true; testSel[k] = false; } }); render(); });
  var all = button('Ack all', function () { return true; }, custom, function () { confirming = true; render(); });
  sel.style.cssText += ';position:absolute;left:200px;top:30px'; all.style.cssText += ';position:absolute;left:340px;top:30px';
  al.appendChild(sel); al.appendChild(all);
  if (confirming) { var cf = button('Confirm', function () { return true; }, custom, function () { confirming = false; testAlarms.forEach(function (a) { a.acked = true; }); render(); });
    cf.style.cssText += ';position:absolute;left:480px;top:30px'; al.appendChild(cf); }
  if (pulse) { var ok = button('Confirm', function () { return true; }, function () { return {}; }, function () {
      if (pulse.kind === 'lamp') lampColour = 'alarm'; else testAlarms = [0, 1, 2, 3, 4].map(function () { return {acked: false}; });
      pulse = null; render(); });
    ok.style.cssText += ';position:absolute;left:480px;top:2px'; lamps.appendChild(ok); }
}
var confirming = false;
function post(u, body) { var x = new XMLHttpRequest(); x.open('POST', BASE + u); x.send(JSON.stringify(body)); }
function poll() { var x = new XMLHttpRequest(); x.open('GET', BASE + '/state'); x.onload = function () {
  var s = JSON.parse(x.responseText); var sel = {}; state.alarms.forEach(function (a) { sel[a.tag] = a.sel; });
  var changed = JSON.stringify(s.alarms.map(function (a) { return [a.tag, a.active, a.acked, a.listed]; })) !== JSON.stringify(state.alarms.map(function (a) { return [a.tag, a.active, a.acked, a.listed]; }));
  if (changed) { state.alarms = s.alarms.map(function (a) { a.sel = sel[a.tag] || false; return a; }); render(); } }; x.send(); }
setInterval(poll, 40);
// search
var search = $('search'), panel = null;
function panelClose() { if (panel) { panel.remove(); panel = null; } }
function runSearch() {
  var q = search.value.trim().toLowerCase(); panelClose(); if (!q) return;
  panel = div(''); panel.id = 'panel'; panel.setAttribute('style', 'z-index: 50; position: fixed; left: 220px; top: 40px; width: 420px; background: #fff; border: 1px solid #888; padding: 6px');
  var pages = CFG.pages.filter(function (p) { return p.title.toLowerCase().indexOf(q) >= 0; });
  var devs = CFG.devices.filter(function (d) { return (d.tag + ' ' + d.label).toLowerCase().indexOf(q) >= 0; });
  var tags = CFG.tags.filter(function (t) { return t.name.toLowerCase().indexOf(q) >= 0; });
  if (!pages.length && !devs.length && !tags.length) { panel.appendChild(div('', 'No page, device or tag matches')); }
  if (pages.length) { panel.appendChild(div('', 'Pages')); pages.forEach(function (p) { var r = div('', p.title); r.onclick = function () { nav(p.route); }; panel.appendChild(r); }); }
  if (devs.length) { panel.appendChild(div('', 'Devices')); devs.forEach(function (d) { var r = div('', d.label); r.onclick = function () { panelClose(); search.value = ''; dockOpen(d.tag); }; panel.appendChild(r); }); }
  if (tags.length) { panel.appendChild(div('', 'Tags')); tags.forEach(function (t) { var r = div('', t.name); r.onclick = function () { nav(t.route); }; panel.appendChild(r); }); }
  document.body.appendChild(panel);
  panel.__go = function () { if (pages[0]) nav(pages[0].route); else if (devs[0]) { panelClose(); search.value = ''; dockOpen(devs[0].tag); } else if (tags[0]) nav(tags[0].route); };
}
search.addEventListener('input', runSearch);
search.addEventListener('keydown', function (e) { if (e.key === 'Enter' && panel && panel.__go) panel.__go(); if (e.key === 'Escape') { search.value = ''; panelClose(); } });
document.addEventListener('mousedown', function (e) { if (panel && !panel.contains(e.target) && e.target !== search) panelClose();
  if (!e.target.closest('.ia_popup') && !e.target.closest('svg') && !e.target.closest('#nav')) { closePopups(); } });
// icons
function svgClick(i, fn) { $(i).addEventListener('mousedown', function (e) { e.stopPropagation(); fn(); }); }
svgClick('i0', function () { closePopups(); $('nav').hidden = false; $('nav').textContent = ''; CFG.pages.forEach(function (p) { var r = div('', p.title); r.onclick = function () { nav(p.route); }; $('nav').appendChild(r); }); });
svgClick('i1', function () { closePopups(); $('nav').hidden = false; $('nav').textContent = ''; ['Trend', 'Alarms', 'Component test'].forEach(function (t) { $('nav').appendChild(div('', t)); }); });
svgClick('i2', function () { popup('alertmenu', 'Alerts'); });
svgClick('i3', function () { popup('brillmenu', 'Brilliance'); });
svgClick('i4', function () { var p = popup('usermenu', signed ? '' : ''); var b = document.createElement('button'); b.textContent = signed ? 'Sign out' : 'Sign in';
  b.onclick = function () { if (!signed) location.href = BASE + '/idp/login?back=' + encodeURIComponent(location.pathname); }; p.appendChild(b); });
$('crumb').textContent = CFG.root; $('crumb').onmousedown = function (e) { e.stopPropagation(); popup('crumbmenu', 'Site tree'); };
// zoom
function zoom(f) { scale = Math.max(0.1, scale * f); apply(); }
$('zin').onclick = function () { zoom(1.4); }; $('zout').onclick = function () { zoom(1 / 1.4); };
$('wrap').addEventListener('wheel', function (e) { if (e.ctrlKey) { e.preventDefault(); zoom(e.deltaY < 0 ? 1.2 : 1 / 1.2); } }, {passive: false});
document.addEventListener('wheel', function (e) { if (e.ctrlKey) e.preventDefault(); }, {passive: false});
document.addEventListener('keydown', function (e) { if (e.ctrlKey && e.key === '-') { e.preventDefault(); zoom(1 / 1.2); } if (e.ctrlKey && e.key === '0') { e.preventDefault(); fit(); } });
var d0 = null;
function dist(t) { return Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY); }
$('wrap').addEventListener('touchstart', function (e) { if (e.touches.length === 2) d0 = dist(e.touches); }, {passive: false});
$('wrap').addEventListener('touchmove', function (e) { if (e.touches.length === 2 && d0) { e.preventDefault(); var d = dist(e.touches); zoom(d / d0); d0 = d; } }, {passive: false});
$('wrap').addEventListener('touchend', function () { d0 = null; });
if (sessionStorage.getItem('dock')) dockOpen(sessionStorage.getItem('dock')); else fit();
render(); poll();
window.addEventListener('resize', fit);
</script></body></html>"""

LOGIN = """<!doctype html><html><body><input name="username" autofocus><script>
var u = document.querySelector('input'); var step = 0; var back = new URLSearchParams(location.search).get('back');
u.addEventListener('keydown', function (e) { if (e.key !== 'Enter') return;
  if (step === 0) { u.name = 'password'; u.type = 'password'; u.value = ''; step = 1; }
  else { document.cookie = 'signed=1; path=/'; location.href = back; } });
</script></body></html>"""


class FakeGateway:
    """A server and a tag store. `config` holds the pages, devices, tags and alarms the client page needs."""

    def __init__(self, config: dict):
        self.config = config
        self.tags: dict[str, object] = {}
        self.acked: set[str] = set()
        self.ignore_ack = False             # a gateway whose acknowledgement does nothing (a probe must see that)
        self.pending: set[str] = set()      # alarms with an event nobody has acknowledged (active, or cleared and listed)
        self.writes: list[tuple[str, object]] = []
        self.lock = threading.Lock()
        gw = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, body: str, ctype="text/html", code=200):
                data = body.encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", ctype + "; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                path = urllib.parse.urlsplit(self.path).path
                proj = "/data/perspective/client/" + gw.config["project"]
                if path.startswith(proj + "/idp/login"):
                    return self._send(LOGIN)
                if path == proj + "/state":
                    return self._send(json.dumps({"alarms": gw.alarm_state()}), "application/json")
                if path.startswith(proj):
                    return self._send(PAGE.replace("__CFG__", json.dumps(gw.config)))
                self._send("not found", code=404)

            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                if self.path.endswith("/ack") and not gw.ignore_ack:
                    with gw.lock:
                        gw.acked |= set(body.get("tags", []))
                        gw.pending -= set(body.get("tags", []))
                self._send("{}", "application/json")

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def write(self, full: str, value) -> None:
        """A tag write, with the alarm lifecycle: an alarm whose source goes active starts an event nobody has acknowledged;
        the event stays listed after the source clears until it is acknowledged (a cleared, acknowledged event leaves the
        list, GF-36). The tag store and the writes are what the earlier tests read."""
        with self.lock:
            was = bool(self.tags.get(full))
            self.tags[full] = value
            self.writes.append((full, value))
            if value and not was:
                for a in self.config["alarms"]:
                    if a["source"] == full:
                        self.pending.add(a["tag"])
                        self.acked.discard(a["tag"])

    def alarm_state(self) -> list[dict]:
        with self.lock:
            out = []
            for a in self.config["alarms"]:
                active = bool(self.tags.get(a["source"]))
                out.append({"tag": a["tag"], "desc": a["desc"], "shows": a["shows"], "active": active,
                            "listed": active or a["tag"] in self.pending, "acked": a["tag"] not in self.pending})
            return out

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self.server.server_address[1]}/data/perspective/client/{self.config['project']}"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *a):
        self.server.shutdown()
        self.server.server_close()


class FakeDeploy:
    """The two functions `walk_run.Tags` uses of `hmi.deploy`, over the fake gateway's tag store."""

    def __init__(self, gw: FakeGateway, initial: dict | None = None, fail_restore: bool = False):
        self.gw, self.fail_restore = gw, fail_restore
        self.gw.tags.update(initial or {})
        self.imports: list[tuple[str, str, dict]] = []

    @staticmethod
    def _leaves(node: dict, prefix: str):
        here = f"{prefix}/{node['name']}" if prefix else node["name"]
        if node.get("tagType") == "Folder":
            for t in node.get("tags", []):
                yield from FakeDeploy._leaves(t, here)
        else:
            yield here, node

    def export_tags(self, provider: str, path: str) -> dict:
        full = f"[{provider}]{path}"
        if full not in self.gw.tags:
            return {"name": path.rsplit("/", 1)[-1], "tagType": "Unknown"}
        return {"name": path.rsplit("/", 1)[-1], "tagType": "AtomicTag", "valueSource": "memory", "dataType": "Boolean",
                "value": self.gw.tags[full]}

    def import_tags(self, provider: str, path: str, doc: dict) -> dict:
        self.imports.append((provider, path, doc))
        for leaf, node in self._leaves(doc, path):
            full = f"[{provider}]{leaf}"
            if self.fail_restore and node.get("value") is False and self.gw.tags.get(full):
                return {"successCount": 0, "failureCount": 1, "failures": ["refused"]}
            self.gw.write(full, node.get("value"))
        return {"successCount": 1, "failureCount": 0}
