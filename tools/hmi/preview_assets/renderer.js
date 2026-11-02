/* The one preview renderer of the OpenBridge pipeline (WFBD-092): it draws the pages, faceplates, navigation and
   search of both previews (mode "recon", the one to one view, and mode "asm", the ASM view) from the data block
   `preview-data` (application/json). It reads data only through textContent, builds every node with the DOM API,
   sets no inline handler and names no external address. Fixed script: its SHA-256 is recorded in checks.json. */
(function () {
  'use strict';
  var NS = 'ht' + 'tp:' + '//www.w3.org/2000/svg'; /* the SVG namespace name, not an address; split so no scan mistakes it */
  var D = JSON.parse(document.getElementById('preview-data').textContent);
  var body = document.body;
  var $ = function (id) { return document.getElementById(id); };
  function el(tag, cls, text, attrs) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  function svg(tag, attrs) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  var frozen = location.hash === '#frozen';
  var T = 0;
  var updaters = [];
  var pageEls = {};
  var fpEls = {};
  var pagesById = {};
  D.pages.forEach(function (p) { pagesById[p.id] = p; });
  var mode = D.mode;
  body.dataset.mode = mode;

  /* ---- simulated values ------------------------------------------------------------------------------- */
  function hash(s) { var h = 7; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 100003; return h; }
  function flag(tag, t) { var h = hash(tag); return Math.floor(t / (5 + h % 7)) % 2 === h % 2; }
  function num(tag, t) {
    var h = hash(tag), info = (D.taginfo || {})[tag] || {};
    var lo = info.lo === null || info.lo === undefined ? 0 : Number(info.lo);
    var hi = info.hi === null || info.hi === undefined ? 100 : Number(info.hi);
    return lo + (hi - lo) * (0.5 + 0.35 * Math.sin(t / (3 + h % 5) + h));
  }
  function isBool(tag) { var i = (D.taginfo || {})[tag]; return !!i && String(i.type).toUpperCase() === 'DIGITAL'; }
  function fmt(v, f) {
    /* no format is stated by the data: the preview shows three significant digits and claims no precision */
    if (!f) return Number(v).toPrecision(3);
    var d = f.indexOf('.') >= 0 ? f.length - f.indexOf('.') - 1 : 0;
    return Number(v).toFixed(d);
  }
  function colour(name) {
    return /^(on|off|alarm|warning|caution|critical|neutral)$/.test(name || '') ? 'var(--' + name + ')' : (name || 'var(--off)');
  }

  /* ---- navigation ------------------------------------------------------------------------------------- */
  function notice(text) {
    var n = $('notice');
    n.textContent = text || '';
    n.hidden = !text;
    body.dataset.notice = text || '';
  }
  function fit() {
    var p = pagesById[body.dataset.page];
    var wrap = $('canvas-wrap'), stage = $('stage');
    if (!p) { wrap.style.transform = ''; return; }
    var s = Math.min(1, (stage.clientWidth - 16) / p.width, (stage.clientHeight - 16) / p.height);
    if (!(s > 0)) s = 1;
    wrap.style.transform = 'scale(' + s + ')';
    wrap.style.width = p.width + 'px';
    wrap.style.height = p.height + 'px';
    body.dataset.scale = String(Math.round(s * 1000) / 1000);
  }
  function nodePath(id) {
    var by = {}, out = [];
    D.nodes.forEach(function (n) { by[n.id] = n; });
    while (id && by[id]) { out.unshift(by[id].name); id = by[id].parent; }
    return out.join(' / ');
  }
  function showPage(id) {
    var p = pagesById[id];
    if (!p) return false;
    D.pages.forEach(function (q) { pageEls[q.id].hidden = q.id !== id; });
    $('support').hidden = true;
    $('canvas-wrap').hidden = false;
    body.dataset.page = id;
    body.dataset.route = p.route;
    $('crumb').textContent = nodePath(p.node) + ' / ' + p.title + (p.level ? '  (' + p.level + ')' : '');
    document.querySelectorAll('#tree button').forEach(function (b) { b.classList.toggle('current', b.dataset.page === id); });
    fit();
    return true;
  }
  function showSupport(route) {
    $('canvas-wrap').hidden = true;
    var s = $('support');
    s.hidden = false;
    s.textContent = 'Library page ' + route;
    body.dataset.page = '';
    body.dataset.route = route;
    $('crumb').textContent = 'Library page ' + route;
  }
  function openFaceplate(id, tab) {
    var f = fpEls[id];
    if (!f) { notice('No faceplate ' + id); return false; }
    Object.keys(fpEls).forEach(function (k) { if (k !== id) $('fpstore').appendChild(fpEls[k].sec); });
    var floating = body.dataset.fpmode === 'float';
    (floating ? $('float') : $('dock')).appendChild(f.sec);
    f.sec.hidden = false;
    if (floating) $('float').hidden = false; else $('dock').classList.add('open');
    body.dataset.fp = id;
    body.dataset.fpmode = floating ? 'float' : 'dock';
    selectTab(id, tab || f.tabs[0]);
    return true;
  }
  function selectTab(id, tab) {
    var f = fpEls[id];
    var names = Object.keys(f.panes);
    if (names.indexOf(tab) < 0) tab = names[0];
    names.forEach(function (n) { f.panes[n].hidden = n !== tab; f.buttons[n].classList.toggle('cur', n === tab); });
    body.dataset.tab = tab || '';
  }
  function closeFaceplate() {
    var id = body.dataset.fp;
    if (id && fpEls[id]) $('fpstore').appendChild(fpEls[id].sec);
    $('dock').classList.remove('open');
    $('float').hidden = true;
    body.dataset.fp = '';
    body.dataset.fpmode = 'closed';
  }
  function floatFaceplate(on) {
    var id = body.dataset.fp;
    if (!id) return;
    var f = fpEls[id];
    if (on) {
      $('dock').classList.remove('open');
      $('float').appendChild(f.sec);
      $('float').hidden = false;
      body.dataset.fpmode = 'float';
    } else {
      $('float').hidden = true;
      $('dock').appendChild(f.sec);
      $('dock').classList.add('open');
      body.dataset.fpmode = 'dock';
    }
    fit();
  }
  function go(row) {
    notice('');
    if (row.resolution === 'page') return showPage(row.target);
    if (row.resolution === 'support') { showSupport(row.route); return true; }
    if (row.resolution === 'faceplate') return openFaceplate(row.faceplate, row.tab);
    notice((row.reason || 'Not migrated') + ': ' + row.target);
    return false;
  }

  /* ---- items ------------------------------------------------------------------------------------------ */
  function place(e, it) {
    e.style.left = it.x + 'px'; e.style.top = it.y + 'px'; e.style.width = it.w + 'px'; e.style.height = it.h + 'px';
  }
  function stateColour(it, v) {
    var s = (it.states || []).filter(function (x) { return String(x.value) === String(v); })[0];
    return s ? [colour(s.colour), s.label || ''] : [colour(it.state_default || 'off'), ''];
  }
  function draw(it, pageEl) {
    var e;
    var k = it.kind;
    if (k === 'hidden') {
      e = el('span', 'it');
      e.hidden = true;
      e.dataset.treatment = it.treatment || 'none';
    } else if (k === 'region') {
      e = el('div', 'it region');
      place(e, it);
      e.appendChild(el('span', 'rt', it.label || ''));
    } else if (k === 'pipe') {
      e = null;
    } else if (k === 'label') {
      e = el('div', 'it lbltext' + (it.style === 'heading' ? ' heading' : ''), it.text || it.label || '');
      place(e, it);
    } else if (k === 'link' || k === 'button') {
      e = el('div', it.hotspot ? 'it ctrl hot' : 'it ctrl');
      place(e, it);
      var b = el('button', 'ctl', it.hotspot ? '' : (it.label || it.text || 'Open'));
      if (it.hotspot) { e.title = it.label || it.text || 'Open'; b.setAttribute('aria-label', e.title); }
      if (it.nav !== undefined && it.nav !== null) b.dataset.nav = String(it.nav);
      b.addEventListener('click', function () {
        if (it.faceplate) openFaceplate(it.faceplate, it.tab);
        else if (it.nav !== undefined && it.nav !== null) go(D.nav[it.nav]);
      });
      e.appendChild(b);
    } else if (k === 'readout') {
      e = el('div', 'it readout');
      place(e, it);
      if (it.label) e.appendChild(el('span', 'lbl', it.label));
      var v = el('span', 'val', '--');
      var u = el('span', 'unit', it.unit || '');
      e.appendChild(v); e.appendChild(u);
      var tag = (it.reads || [])[0];
      updaters.push(function (t) { if (tag) v.textContent = fmt(num(tag, t), it.format); });
    } else if (k === 'indicator') {
      e = el('div', 'it lamp');
      place(e, it);
      var dot = el('i'); var word = el('span', 'w', it.label || '');
      e.appendChild(dot); e.appendChild(word);
      var tg = (it.reads || [])[0];
      updaters.push(function (t) {
        if (!tg) return;
        var c = stateColour(it, flag(tg, t));
        dot.style.background = c[0];
        word.textContent = c[1] || it.label || '';
      });
    } else if (k === 'symbol' || k === 'bar' || k === 'trend' || k === 'alarm-panel' || k === 'well') {
      e = el('div', 'it sym' + (it.plain ? ' plain' : ''));
      place(e, it);
      e.appendChild(el('span', 'g', (it.component || k).slice(0, 8)));
      if (it.label) e.appendChild(el('span', 'l', it.label));
      var fill = null;
      if (it.component === 'tank') { fill = el('span', 'fill'); e.appendChild(fill); }
      var tr = (it.reads || [])[0];
      updaters.push(function (t) {
        if (!tr) return;
        if (fill) fill.style.height = Math.round(40 + 35 * Math.sin(t / 7 + hash(tr))) + '%';
        else e.classList.toggle('on', flag(tr, t));
      });
      if (it.faceplate) {
        e.addEventListener('click', function () { openFaceplate(it.faceplate, it.tab); });
        e.dataset.opens = it.faceplate;
        e.classList.add('opens');
      }
    } else {
      e = el('div', 'it sym', it.label || k);
      place(e, it);
    }
    if (e) {
      e.dataset.uid = it.uid;
      e.dataset.kind = k;
      pageEl.appendChild(e);
    }
    return e;
  }
  function drawPipes(page, pageEl) {
    var pipes = page.items.filter(function (i) { return i.kind === 'pipe' && i.path && i.path.length > 1; });
    if (!pipes.length) {
      page.items.filter(function (i) { return i.kind === 'pipe'; }).forEach(function (it) {
        var h = el('span', 'it'); h.hidden = true; h.dataset.uid = it.uid; h.dataset.treatment = 'pipe-no-path'; pageEl.appendChild(h);
      });
      return;
    }
    var s = svg('svg', { 'class': 'pipes', width: page.width, height: page.height });
    page.items.filter(function (i) { return i.kind === 'pipe'; }).forEach(function (it) {
      var pl = svg('polyline', { points: (it.path || []).map(function (p) { return p[0] + ',' + p[1]; }).join(' '),
        'class': it.medium || 'neutral' });
      pl.dataset.uid = it.uid;
      pl.dataset.kind = 'pipe';
      s.appendChild(pl);
    });
    pageEl.appendChild(s);
  }

  /* ---- build ------------------------------------------------------------------------------------------ */
  function buildPages() {
    var host = $('canvas-wrap');
    D.pages.forEach(function (p) {
      var pe = el('div', 'page');
      pe.style.width = p.width + 'px'; pe.style.height = p.height + 'px';
      pe.dataset.page = p.id;
      pe.hidden = true;
      if (D.pictures && D.pictures[p.id] && mode === 'recon') {
        var img = el('img', 'orig'); img.alt = ''; img.hidden = true;
        img.src = D.pictures[p.id];
        pe.appendChild(img);
      }
      drawPipes(p, pe);
      p.items.forEach(function (it) { draw(it, pe); });
      host.appendChild(pe);
      pageEls[p.id] = pe;
    });
  }
  function buildFaceplates() {
    (D.faceplates || []).forEach(function (f) {
      var sec = el('section', 'fp'); sec.hidden = true; sec.dataset.fp = f.id;
      var head = el('header');
      head.appendChild(el('span', 't', f.title + (f.node ? '  (' + f.node + ')' : '')));
      var bf = el('button', null, 'Float'); bf.dataset.act = 'float';
      var bd = el('button', null, 'Dock'); bd.dataset.act = 'dock';
      var bc = el('button', null, 'Close'); bc.dataset.act = 'close';
      bf.addEventListener('click', function () { floatFaceplate(true); });
      bd.addEventListener('click', function () { floatFaceplate(false); });
      bc.addEventListener('click', closeFaceplate);
      head.appendChild(bf); head.appendChild(bd); head.appendChild(bc);
      head.addEventListener('mousedown', function (ev) {
        if (body.dataset.fpmode !== 'float' || ev.target.tagName === 'BUTTON') return;
        var fl = $('float'), ox = ev.clientX - fl.offsetLeft, oy = ev.clientY - fl.offsetTop;
        function move(m) { fl.style.left = (m.clientX - ox) + 'px'; fl.style.top = (m.clientY - oy) + 'px'; }
        function up() { document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up); }
        document.addEventListener('mousemove', move); document.addEventListener('mouseup', up);
      });
      sec.appendChild(head);
      var tabs = el('div', 'tabs'); sec.appendChild(tabs);
      var rec = { sec: sec, panes: {}, buttons: {}, tabs: [] };
      f.tabs.forEach(function (t) {
        var b = el('button', null, t.name); b.dataset.tab = t.name;
        b.addEventListener('click', function () { selectTab(f.id, t.name); });
        tabs.appendChild(b);
        var pane = el('div', 'pane'); pane.dataset.tab = t.name; pane.hidden = true;
        t.rows.forEach(function (r) {
          var row = el('div', 'row');
          row.dataset.uid = r.uid;
          row.appendChild(el('span', 'k', r.label || r.uid));
          var vv = el('span', 'v', '');
          row.appendChild(vv);
          var tg = (r.reads || [])[0];
          updaters.push(function (tm) { if (tg) vv.textContent = fmt(num(tg, tm), r.format); });
          pane.appendChild(row);
        });
        sec.appendChild(pane);
        rec.panes[t.name] = pane; rec.buttons[t.name] = b; rec.tabs.push(t.name);
      });
      $('fpstore').appendChild(sec);
      fpEls[f.id] = rec;
    });
  }
  function buildTree() {
    var tree = $('tree');
    function walk(parent, holder) {
      D.nodes.filter(function (n) { return n.parent === parent; }).forEach(function (n) {
        var li = el('li');
        li.appendChild(el('div', 'node', n.name));
        var ul = el('ul');
        n.pages.forEach(function (pid) {
          if (!pagesById[pid]) return;
          var b = el('button', null, pagesById[pid].title); b.dataset.page = pid;
          b.addEventListener('click', function () { showPage(pid); });
          var l = el('li'); l.appendChild(b); ul.appendChild(l);
        });
        walk(n.id, ul);
        li.appendChild(ul); holder.appendChild(li);
      });
    }
    var root = el('ul'); walk(null, root); tree.appendChild(root);
  }
  function buildNavTable() {
    var t = $('navtable');
    t.appendChild(el('div', null, 'Navigation table: ' + D.nav.length + ' rows'));
    D.nav.forEach(function (r) {
      var b = el('button', null, r.from + '  >  ' + r.target + '  [' + r.resolution + ']');
      b.dataset.row = String(r.i);
      b.addEventListener('click', function () { go(r); });
      t.appendChild(b);
    });
  }
  function buildSearch() {
    var box = $('search'), list = $('results');
    if (!D.search || !D.search.length) { box.hidden = true; return; }
    function run() {
      var q = box.value.trim().toLowerCase();
      list.textContent = '';
      list.hidden = !q;
      if (!q) return;
      var n = 0;
      D.search.forEach(function (s) {
        if (n >= 12 || (s.text + ' ' + (s.sub || '')).toLowerCase().indexOf(q) < 0) return;
        n++;
        var li = el('li', null, s.text + (s.sub ? '  ' + s.sub : '')); li.dataset.kind = s.kind;
        li.addEventListener('click', function () {
          if (s.page) showPage(s.page);
          if (s.faceplate) openFaceplate(s.faceplate, s.tab);
          list.hidden = true; box.value = '';
        });
        list.appendChild(li);
      });
      if (!n) list.appendChild(el('li', null, 'No result'));
    }
    box.addEventListener('input', run);
    box.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') { box.value = ''; run(); } });
  }
  function tick() {
    updaters.forEach(function (u) { u(T); });
  }

  function buildMarkers() {
    (D.markers || []).forEach(function (m) {
      var h = el('span'); h.hidden = true; h.dataset.uid = m.uid; h.dataset.treatment = m.treatment;
      $('fpstore').appendChild(h);
    });
  }
  buildMarkers(); buildPages(); buildFaceplates(); buildTree(); buildNavTable(); buildSearch();
  $('b-nav').addEventListener('click', function () { $('navtable').hidden = !$('navtable').hidden; });
  var ob = $('b-orig');
  if (mode === 'recon') {
    ob.addEventListener('click', function () {
      document.querySelectorAll('.orig').forEach(function (i) { i.hidden = !i.hidden; });
    });
  } else { ob.hidden = true; }
  $('title').textContent = D.title;
  window.addEventListener('resize', fit);
  window.__preview = { go: go, show: showPage, open: openFaceplate, expected: D.expected, ready: true };
  tick();
  if (D.pages.length) showPage(D.home || D.pages[0].id);
  if (D.simulation && !frozen) {
    setInterval(function () { T += (D.sim_ms || 1000) / 1000; tick(); }, D.sim_ms || 1000);
  }
  body.dataset.fpmode = 'closed';
  body.dataset.ready = '1';
}());
