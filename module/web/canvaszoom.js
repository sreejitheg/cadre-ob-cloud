/* Cadre HMI Components module: the canvas zoom component (cadre.ob.canvaszoom).
   Read by module/tools/gen_module_assets.py and appended to cadre-ob.js after the generated wrappers;
   it is plain script (no bundler) and runs in the Perspective client, where PerspectiveClient and React
   are globals (GF-31).

   A leaf component that draws nothing. It finds its target (the scrolling canvas of a diagram screen) by
   its DOM id, and turns three gestures into a number, the `zoom` property, which the view binds two ways
   to its own `zoom` custom property and the canvas scales by:

     Ctrl + wheel (a trackpad pinch arrives the same way), a two finger pinch, Ctrl + plus, minus and 0.

   The point under the pointer stays where it is: once the new scale shows, the target's scroll position is
   set so that the content point that lay under the pointer lies under it again. With guardBrowserZoom the
   same gestures anywhere else on the document are prevented, so the browser never zooms the whole frame,
   and the viewport meta gains maximum-scale=1 on touch devices. Every listener is removed on unmount. */
(function () {
  'use strict';
  var PC = window.PerspectiveClient;
  if (!PC || !PC.ComponentRegistry) return;
  var h = window.React.createElement;
  var TYPE = 'cadre.ob.canvaszoom';
  var STEP = 1.25;            // one key press or one wheel notch (a mouse wheel notch is 100 units)
  var WHEEL_RATE = Math.log(STEP) / 100;
  var SETTLE_MS = 600;        // how long the scroll anchoring waits for the new scale to show

  var TOUCH = 'ontouchstart' in window || (navigator.maxTouchPoints || 0) > 0;

  function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }

  function viewportMeta(create) {
    var m = document.querySelector('meta[name="viewport"]');
    if (!m && create) {
      m = document.createElement('meta');
      m.setAttribute('name', 'viewport');
      m.setAttribute('data-cadre-zoom', '');
      document.head.appendChild(m);
    }
    return m;
  }

  class CanvasZoom extends PC.Component {
    constructor(props) {
      super(props);
      this.cur = null;            // the zoom the component last wrote, ahead of the echoed property
      this.wroteAt = 0;
      this.target = null;
      this.listeners = [];        // [node, type, handler, options] for removal
      this.touchPrev = null;      // the previous distance of a two finger pinch
      this.pointers = new Map();
      this.anchor = null;         // the scroll anchoring in progress
      this.raf = 0;
      this.touchAction = null;
      this.metaSaved = null;
    }

    // ---- the properties
    settings() {
      var p = this.props.props || {};
      var min = typeof p.min === 'number' && p.min > 0 ? p.min : 0.5;
      var max = typeof p.max === 'number' && p.max >= min ? p.max : 4;
      return { zoom: typeof p.zoom === 'number' ? p.zoom : 1, min: min, max: max,
               id: p.targetDomId || 'cadre-canvas', guard: p.guardBrowserZoom !== false };
    }

    // The zoom now: what the component wrote a moment ago, else what the property says.
    current() {
      var s = this.settings();
      if (this.cur !== null && Date.now() - this.wroteAt < 1500) return this.cur;
      this.cur = null;
      return s.zoom;
    }

    write(zoom) {
      this.cur = zoom;
      this.wroteAt = Date.now();
      this.put('zoom', zoom);
    }

    put(name, value) {
      try {
        var store = this.props.store;
        if (store && store.props && typeof store.props.write === 'function') store.props.write(name, value);
      } catch (e) { /* a write refused is not a reason to break the page */ }
    }

    // The target's box, written as viewWidth and viewHeight whenever it changes by a pixel or more: the page's fit
    // reads the canvas it really has (a docked faceplate, a reload, a second tab) instead of the viewport.
    measure() {
      if (!this.target) return;
      var r = this.target.getBoundingClientRect();
      var w = Math.round(r.width), hh = Math.round(r.height);
      if (w <= 0 || hh <= 0) return;
      if (this.measured && Math.abs(this.measured[0] - w) < 1 && Math.abs(this.measured[1] - hh) < 1) return;
      this.measured = [w, hh];
      this.put('viewWidth', w);
      this.put('viewHeight', hh);
    }

    // ---- zooming
    // Zoom by a factor, or to an absolute value, about a client point (cx, cy) of the target.
    zoomTo(next, cx, cy) {
      var s = this.settings(), t = this.target;
      var old = this.current();
      next = clamp(next, s.min, s.max);
      if (Math.abs(next - old) < 1e-6) return;
      if (t && !this.anchor) {
        var r = t.getBoundingClientRect();
        this.anchor = { left: t.scrollLeft, top: t.scrollTop, zoom: old, sw: t.scrollWidth, sh: t.scrollHeight,
                        px: 0, py: 0, last: 0, changed: false };
        this.anchor.px = (cx === undefined ? r.left + r.width / 2 : cx) - r.left;
        this.anchor.py = (cy === undefined ? r.top + r.height / 2 : cy) - r.top;
      }
      if (this.anchor) {
        this.anchor.last = Date.now();
        if (cx !== undefined && t) {
          var rr = t.getBoundingClientRect();
          this.anchor.px = cx - rr.left;
          this.anchor.py = cy - rr.top;
        }
      }
      this.write(next);
      this.settle();
    }

    zoomBy(factor, cx, cy) { this.zoomTo(this.current() * factor, cx, cy); }

    // Once the new scale shows (the target's scrollable size changes), set the scroll position so that the
    // point under the pointer has not moved: (scroll + p) * ratio - p, where ratio is new zoom over the zoom
    // at the start of the burst. Tried every frame until the size has settled.
    settle() {
      if (this.raf) return;
      var self = this;
      var tick = function () {
        self.raf = 0;
        var a = self.anchor, t = self.target;
        if (!a || !t) { self.anchor = null; return; }
        var ratio = self.current() / a.zoom;
        if (t.scrollWidth !== a.sw || t.scrollHeight !== a.sh) a.changed = true;
        if (a.changed || Date.now() - a.last > SETTLE_MS) {
          t.scrollLeft = (a.left + a.px) * ratio - a.px;
          t.scrollTop = (a.top + a.py) * ratio - a.py;
        }
        if (Date.now() - a.last > SETTLE_MS * 1.5) { self.anchor = null; return; }
        self.raf = window.requestAnimationFrame(tick);
      };
      this.raf = window.requestAnimationFrame(tick);
    }

    // ---- the gestures
    over(node) { return !!(this.target && node && this.target.contains(node)); }

    onWheel(e) {
      if (!e.ctrlKey) return;
      var s = this.settings();
      if (this.over(e.target)) {
        e.preventDefault();
        var d = e.deltaY * (e.deltaMode === 1 ? 33 : (e.deltaMode === 2 ? 400 : 1));
        this.zoomBy(Math.exp(-d * WHEEL_RATE), e.clientX, e.clientY);
      } else if (s.guard) {
        e.preventDefault();
      }
    }

    onKey(e) {
      if (!(e.ctrlKey || e.metaKey) || e.altKey) return;
      var k = e.key, code = e.code;
      var plus = k === '+' || k === '=' || code === 'NumpadAdd';
      var minus = k === '-' || k === '_' || code === 'NumpadSubtract';
      var zero = k === '0' || code === 'Numpad0';
      if (!(plus || minus || zero) || !this.target) return;
      e.preventDefault();
      if (zero) this.zoomTo(1);
      else this.zoomBy(plus ? STEP : 1 / STEP);
    }

    // Two finger pinch from touch events: the distance between the fingers drives the zoom, their midpoint
    // is the point that stays put.
    onTouch(e) {
      var s = this.settings(), over = this.over(e.target);
      if (e.touches && e.touches.length >= 2) {
        if (over || s.guard) e.preventDefault();
        if (!over) return;
        var a = e.touches[0], b = e.touches[1];
        var dist = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
        if (this.touchPrev && dist > 0) {
          this.zoomBy(dist / this.touchPrev, (a.clientX + b.clientX) / 2, (a.clientY + b.clientY) / 2);
        }
        this.touchPrev = dist;
      } else {
        this.touchPrev = null;
      }
    }

    // The same pinch from pointer events (pens, and touch where the browser reports pointers only).
    onPointer(e) {
      if (!this.over(e.target) && !this.pointers.has(e.pointerId)) return;
      if (e.type === 'pointerdown' || e.type === 'pointermove') {
        // a mouse never pinches; a touch pinch is read from touch events where the browser has them
        if (e.pointerType === 'mouse' || (e.pointerType === 'touch' && TOUCH)) return;
        if (e.type === 'pointermove' && !this.pointers.has(e.pointerId)) return;
        this.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
        if (this.pointers.size === 2) {
          var pts = Array.from(this.pointers.values());
          var dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
          if (this.pointerPrev && dist > 0 && e.type === 'pointermove') {
            this.zoomBy(dist / this.pointerPrev, (pts[0].x + pts[1].x) / 2, (pts[0].y + pts[1].y) / 2);
          }
          this.pointerPrev = dist;
        }
      } else {
        this.pointers.delete(e.pointerId);
        if (this.pointers.size < 2) this.pointerPrev = null;
      }
    }

    // Safari reports a pinch as gesture events that zoom the page unless prevented.
    onGesture(e) {
      if (this.settings().guard || this.over(e.target)) e.preventDefault();
    }

    // ---- life cycle
    listen(node, type, handler, options) {
      node.addEventListener(type, handler, options);
      this.listeners.push([node, type, handler, options]);
    }

    attach() {
      this.detach();
      var s = this.settings();
      this.target = document.getElementById(s.id);
      var self = this;
      var wheel = function (e) { self.onWheel(e); };
      var key = function (e) { self.onKey(e); };
      var touch = function (e) { self.onTouch(e); };
      var pointer = function (e) { self.onPointer(e); };
      var gesture = function (e) { self.onGesture(e); };
      // non-passive and in the capture phase, so that preventDefault is honoured before Perspective's handlers
      var opt = { passive: false, capture: true };
      this.listen(document, 'wheel', wheel, opt);
      this.listen(document, 'keydown', key, opt);
      if (TOUCH) {     // a non-passive touch listener makes the browser wait for it, so only where there is touch
        this.listen(document, 'touchstart', touch, opt);
        this.listen(document, 'touchmove', touch, opt);
        this.listen(document, 'touchend', touch, opt);
        this.listen(document, 'touchcancel', touch, opt);
      }
      this.listen(document, 'pointerdown', pointer, opt);
      this.listen(document, 'pointermove', pointer, opt);
      this.listen(document, 'pointerup', pointer, opt);
      this.listen(document, 'pointercancel', pointer, opt);
      this.listen(document, 'gesturestart', gesture, opt);
      this.listen(document, 'gesturechange', gesture, opt);
      if (this.target) {
        // the browser keeps one finger scrolling and gives the pinch to the script
        this.touchAction = this.target.style.touchAction;
        this.target.style.touchAction = 'pan-x pan-y';
        this.measured = null;
        if (typeof window.ResizeObserver === 'function') {
          this.resizer = new window.ResizeObserver(function () { self.measure(); });
          this.resizer.observe(this.target);
        }
        this.measure();
      }
      this.guarded = s.guard;
      if (s.guard && TOUCH) {
        var m = viewportMeta(true);
        this.metaSaved = { meta: m, content: m.getAttribute('content'), made: m.hasAttribute('data-cadre-zoom') };
        var c = (m.getAttribute('content') || 'width=device-width, initial-scale=1').replace(/,?\s*maximum-scale=[^,]*/i, '');
        m.setAttribute('content', c + ', maximum-scale=1');
      }
    }

    detach() {
      this.listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
      this.listeners = [];
      if (this.resizer) { this.resizer.disconnect(); this.resizer = null; }
      if (this.raf) { window.cancelAnimationFrame(this.raf); this.raf = 0; }
      this.anchor = null;
      this.pointers.clear();
      this.touchPrev = null;
      this.pointerPrev = null;
      if (this.target && this.touchAction !== null) this.target.style.touchAction = this.touchAction;
      this.touchAction = null;
      this.target = null;
      var ms = this.metaSaved;
      if (ms) {
        if (ms.made) { if (ms.meta.parentNode) ms.meta.parentNode.removeChild(ms.meta); }
        else if (ms.content === null) ms.meta.removeAttribute('content');
        else ms.meta.setAttribute('content', ms.content);
        this.metaSaved = null;
      }
    }

    componentDidMount() { this.attach(); }

    componentDidUpdate() {
      var s = this.settings();
      var t = document.getElementById(s.id);
      // the target or the guard changed, or the target was drawn after this component
      if (t !== this.target || this.guarded !== s.guard) this.attach();
    }

    componentWillUnmount() { this.detach(); }

    // Draws nothing: a zero sized, hidden box that takes no part in the layout and catches no pointer.
    render() {
      var e = this.props.emit ? this.props.emit() : {};
      var style = Object.assign({}, e.style, { position: 'absolute', left: 0, top: 0, width: 0, height: 0,
                                               overflow: 'hidden', visibility: 'hidden', pointerEvents: 'none' });
      return h('div', Object.assign({}, e, { style: style }));
    }
  }

  PC.ComponentRegistry.register({
    getComponentType: function () { return TYPE; },
    getViewComponent: function () { return CanvasZoom; },
    getDefaultSize: function () { return { width: 1, height: 1 }; },
    getPropsReducer: function (tree) {
      return {
        zoom: tree.readNumber('zoom', 1),
        min: tree.readNumber('min', 0.5),
        max: tree.readNumber('max', 4),
        targetDomId: tree.readString('targetDomId', 'cadre-canvas'),
        guardBrowserZoom: tree.readBoolean('guardBrowserZoom', true),
        viewWidth: tree.readNumber('viewWidth', 0),
        viewHeight: tree.readNumber('viewHeight', 0)
      };
    }
  });
})();
