// Offline check of the module's browser side in Chromium: a page that loads the built bundle with a stub of the
// Perspective client (module/tools/harness/README.md).
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright');
import { pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const url = pathToFileURL(join(dirname(fileURLToPath(import.meta.url)), 'harness.html')).href;
const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const results = [];
function check(name, ok, detail) { results.push([ok ? 'PASS' : 'FAIL', name, detail === undefined ? '' : JSON.stringify(detail)]); }

async function session(touch, body) {
  const ctx = await browser.newContext({ viewport: { width: 700, height: 500 }, hasTouch: touch });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(url);
  await page.waitForFunction(() => Object.keys(window.registry).length >= 11);
  // the screen: a canvas, a sizer and a diagram; the zoom round trip takes 50 ms (write) and 40 ms (scale shows)
  await page.evaluate(() => {
    document.getElementById('stage').innerHTML =
      '<div id="cadre-canvas"><div id="sizer"><div id="diagram" style="width:800px;height:600px;transform-origin:0 0;position:relative"></div></div></div><div id="zc" style="position:absolute;left:0;top:0;width:0;height:0"></div>' +
      '<p id="outside" style="margin:20px">outside the canvas</p>';
    window.s = 1; window.raw = { zoom: 1 }; window.writes = [];
    window.apply = (z) => {
      window.s = z;
      const sz = document.getElementById('sizer'), d = document.getElementById('diagram');
      sz.style.width = 800 * z + 'px'; sz.style.height = 600 * z + 'px'; d.style.transform = 'scale(' + z + ')';
    };
    window.apply(1);
    // listener bookkeeping before the component mounts
    window.live = new Map();
    const add = document.addEventListener.bind(document), rem = document.removeEventListener.bind(document);
    const key = (t, f, o) => t + '|' + (f && f.__id || (f.__id = Math.random())) + '|' + (typeof o === 'object' ? !!o.capture : !!o);
    document.addEventListener = (t, f, o) => { window.live.set(key(t, f, o), { t, passive: o && typeof o === 'object' ? o.passive : undefined }); return add(t, f, o); };
    document.removeEventListener = (t, f, o) => { window.live.delete(key(t, f, o)); return rem(t, f, o); };
    const store = { props: { write: (n, v) => {
      window.writes.push([n, v]);
      setTimeout(() => { window.raw = Object.assign({}, window.raw, { [n]: v }); window.h.rerender(window.raw); if (n === 'zoom') setTimeout(() => window.apply(v), 40); }, 50);   // viewWidth and viewHeight (0.4.1) are not a scale
    } } };
    window.h = window.mount('cadre.ob.canvaszoom', window.raw, document.getElementById('zc'), store);
  });
  await page.waitForTimeout(200);
  await body(page, errors);
  check('no page errors', errors.length === 0, errors);
  await ctx.close();
}

// the content point under a client point
const pointUnder = (page, px, py) => page.evaluate(([px, py]) => {
  const c = document.getElementById('cadre-canvas'), r = c.getBoundingClientRect();
  return { x: (c.scrollLeft + px - r.left) / window.s, y: (c.scrollTop + py - r.top) / window.s, s: window.s, sl: c.scrollLeft, st: c.scrollTop };
}, [px, py]);
const rect = (page) => page.evaluate(() => { const r = document.getElementById('cadre-canvas').getBoundingClientRect(); return { l: r.left, t: r.top }; });
const wheel = (page, x, y, dy, ctrl = true) => page.evaluate(([x, y, dy, ctrl]) => {
  const t = document.elementFromPoint(x, y) || document.body;
  const e = new WheelEvent('wheel', { bubbles: true, cancelable: true, ctrlKey: ctrl, clientX: x, clientY: y, deltaY: dy, deltaMode: 0 });
  t.dispatchEvent(e);
  return e.defaultPrevented;
}, [x, y, dy, ctrl]);
const keydown = (page, key, code, ctrl = true) => page.evaluate(([key, code, ctrl]) => {
  const e = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, ctrlKey: ctrl, key, code });
  document.body.dispatchEvent(e);
  return e.defaultPrevented;
}, [key, code, ctrl]);
const settle = (page) => page.waitForTimeout(1100);
const near = (a, b, tol = 2) => Math.abs(a - b) <= tol;

// ---------------------------------------------------------------- a desktop (no touch) session
await session(false, async (page) => {
  const { l, t } = await rect(page);
  await page.evaluate(() => { const c = document.getElementById('cadre-canvas'); c.scrollLeft = 100; c.scrollTop = 60; });
  const px = l + 150, py = t + 120;
  const before = await pointUnder(page, px, py);
  const prevented = await wheel(page, px, py, -100);
  await settle(page);
  const after = await pointUnder(page, px, py);
  check('Ctrl+wheel over the canvas is prevented', prevented === true);
  check('Ctrl+wheel up zooms in by one step (1.25)', near(after.s, 1.25, 0.001), after);
  check('the point under the pointer stays fixed (x, y within 2 px)', near(before.x, after.x) && near(before.y, after.y), { before, after });
  const w = (await page.evaluate(() => window.writes)).filter(x => x[0] === 'zoom');
  check('the component wrote zoom 1.25', w.length === 1 && w[0][0] === 'zoom' && near(w[0][1], 1.25, 0.001), w);

  // a burst of five notches, 16 ms apart
  const b2 = await pointUnder(page, px, py);
  for (let i = 0; i < 5; i++) { await wheel(page, px, py, -100); await page.waitForTimeout(16); }
  await settle(page);
  const a2 = await pointUnder(page, px, py);
  check('a burst of five notches compounds (1.25^6 = 3.81)', near(a2.s, Math.pow(1.25, 6), 0.01), a2);
  check('the point stays fixed after the burst', near(b2.x, a2.x, 3) && near(b2.y, a2.y, 3), { b2, a2 });

  // clamp at max 4
  for (let i = 0; i < 4; i++) { await wheel(page, px, py, -100); await page.waitForTimeout(16); }
  await settle(page);
  check('zoom is clamped at max 4', (await pointUnder(page, px, py)).s === 4);
  for (let i = 0; i < 20; i++) { await wheel(page, px, py, 100); await page.waitForTimeout(16); }
  await settle(page);
  check('zoom is clamped at min 0.5', (await pointUnder(page, px, py)).s === 0.5);

  // keys
  let p = await keydown(page, '0', 'Digit0'); await settle(page);
  check('Ctrl+0 resets to 1 and is prevented', p === true && (await pointUnder(page, px, py)).s === 1);
  p = await keydown(page, '+', 'Equal'); await settle(page);
  check('Ctrl+plus zooms in 1.25', p === true && near((await pointUnder(page, px, py)).s, 1.25, 0.001));
  p = await keydown(page, '=', 'Equal'); await settle(page);
  check('Ctrl+= (unshifted plus) zooms in again', near((await pointUnder(page, px, py)).s, 1.5625, 0.001));
  p = await keydown(page, '-', 'Minus'); await settle(page);
  check('Ctrl+minus zooms out 1.25', p === true && near((await pointUnder(page, px, py)).s, 1.25, 0.001));
  p = await keydown(page, 'a', 'KeyA');
  check('Ctrl+a is not taken', p === false);
  p = await keydown(page, '+', 'Equal', false);
  check('plus without Ctrl is not taken', p === false);

  // guard
  p = await wheel(page, 100, 450, -100, true);
  check('Ctrl+wheel outside the canvas is prevented (guard on)', p === true);
  p = await wheel(page, px, py, -100, false);
  check('a wheel without Ctrl scrolls the canvas (not prevented)', p === false);

  // the guard off
  await page.evaluate(() => { window.raw = Object.assign({}, window.raw, { guardBrowserZoom: false }); window.h.rerender(window.raw); });
  await page.waitForTimeout(100);
  p = await wheel(page, 100, 450, -100, true);
  check('Ctrl+wheel outside the canvas is left to the browser with guardBrowserZoom false', p === false);
  p = await wheel(page, px, py, -100, true);
  check('Ctrl+wheel over the canvas is still taken with guardBrowserZoom false', p === true);
  await page.evaluate(() => { window.raw = Object.assign({}, window.raw, { guardBrowserZoom: true }); window.h.rerender(window.raw); });
  await page.waitForTimeout(100);

  // pen pointers pinch
  await page.evaluate(() => window.h.rerender(Object.assign({}, window.raw, { zoom: 1 })));
  const ta = await page.evaluate(() => document.getElementById('cadre-canvas').style.touchAction);
  check('the canvas keeps one finger panning, the script gets the pinch (touch-action)', ta === 'pan-x pan-y', ta);
  const pz0 = (await pointUnder(page, px, py)).s;
  await page.evaluate(([px, py]) => {
    const t = document.getElementById('diagram');
    const ev = (type, id, x, y) => t.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerId: id, pointerType: 'pen', clientX: x, clientY: y }));
    ev('pointerdown', 1, px - 20, py); ev('pointerdown', 2, px + 20, py);
    ev('pointermove', 2, px + 40, py);       // 40 -> 60 px apart: 1.5
    ev('pointerup', 1, px - 20, py); ev('pointerup', 2, px + 40, py);
  }, [px, py]);
  await settle(page);
  const pz1 = await pointUnder(page, px, py);
  check('a two pointer pinch (pen) zooms by the ratio of distances, clamped', pz1.s > pz0 && near(pz1.s, pz0 * 1.5, 0.05), { pz0, pz1 });
});

// ---------------------------------------------------------------- a touch session: touch pinch, the viewport meta
await session(true, async (page) => {
  const meta = await page.evaluate(() => document.querySelector('meta[name=viewport]').getAttribute('content'));
  check('maximum-scale=1 is set on a touch device', /maximum-scale=1/.test(meta), meta);
  const { l, t } = await rect(page);
  const px = l + 150, py = t + 120;
  await page.evaluate(() => { const c = document.getElementById('cadre-canvas'); c.scrollLeft = 100; c.scrollTop = 60; });
  const before = await pointUnder(page, px, py);
  const prevented = await page.evaluate(([px, py]) => {
    const target = document.getElementById('diagram');
    const touch = (id, x, y) => new Touch({ identifier: id, target, clientX: x, clientY: y });
    const fire = (type, pts) => { const e = new TouchEvent(type, { bubbles: true, cancelable: true, touches: pts, targetTouches: pts, changedTouches: pts }); target.dispatchEvent(e); return e.defaultPrevented; };
    fire('touchstart', [touch(1, px - 30, py), touch(2, px + 30, py)]);
    const a = fire('touchmove', [touch(1, px - 40, py), touch(2, px + 40, py)]);   // 60 -> 80
    return a;
  }, [px, py]);
  await settle(page);
  const after = await pointUnder(page, px, py);
  check('a two finger touch move is prevented', prevented === true);
  check('a two finger pinch zooms by the ratio of distances (80/60)', near(after.s, 80 / 60, 0.02), after);
  check('the pinch keeps the point under its midpoint', near(before.x, after.x) && near(before.y, after.y), { before, after });
  const outside = await page.evaluate(() => {
    const target = document.getElementById('outside');
    const touch = (id, x, y) => new Touch({ identifier: id, target, clientX: x, clientY: y });
    const pts = [touch(1, 100, 450), touch(2, 140, 450)];
    const e = new TouchEvent('touchmove', { bubbles: true, cancelable: true, touches: pts, targetTouches: pts, changedTouches: pts });
    target.dispatchEvent(e); return e.defaultPrevented;
  });
  check('a two finger gesture outside the canvas is prevented (guard on)', outside === true);
  const one = await page.evaluate(() => {
    const target = document.getElementById('diagram');
    const pts = [new Touch({ identifier: 1, target, clientX: 100, clientY: 100 })];
    const e = new TouchEvent('touchmove', { bubbles: true, cancelable: true, touches: pts, targetTouches: pts, changedTouches: pts });
    target.dispatchEvent(e); return e.defaultPrevented;
  });
  check('a one finger move still pans (not prevented)', one === false);
  const gs = await page.evaluate(() => { const e = new Event('gesturestart', { bubbles: true, cancelable: true }); document.body.dispatchEvent(e); return e.defaultPrevented; });
  check('Safari gesturestart is prevented', gs === true);

  // unmount: every listener goes, the meta and the touch action return
  const live = await page.evaluate(() => window.live.size);
  await page.evaluate(() => window.h.unmount());
  await page.waitForTimeout(100);
  const rest = await page.evaluate(() => ({ live: [...window.live.keys()], meta: document.querySelector('meta[name=viewport]').getAttribute('content'), ta: document.getElementById('cadre-canvas').style.touchAction }));
  check('listeners were added', live >= 10, live);
  check('unmount removes every listener', rest.live.filter(k => !k.startsWith('selectionchange')).length === 0, rest.live);
  check('unmount restores the viewport meta', !/maximum-scale/.test(rest.meta), rest.meta);
  check('unmount restores touch-action', rest.ta === '', rest.ta);
  const p = await page.evaluate(() => { const e = new WheelEvent('wheel', { bubbles: true, cancelable: true, ctrlKey: true, deltaY: -100 }); document.body.dispatchEvent(e); return e.defaultPrevented; });
  check('after unmount a Ctrl+wheel is the browser\'s again', p === false);
});

// ---------------------------------------------------------------- listeners are non-passive, capture
await session(false, async (page) => {
  const info = await page.evaluate(() => [...window.live.values()]);
  const wheel = info.find(i => i.t === 'wheel');
  check('the wheel listener is non-passive', wheel && wheel.passive === false, wheel);
  const types = [...new Set(info.map(i => i.t))].sort();
  check('listener types', ['gesturechange', 'gesturestart', 'keydown', 'pointercancel', 'pointerdown', 'pointermove', 'pointerup', 'wheel'].every(t => types.includes(t)), types);
  await page.evaluate(() => window.h.unmount());
  await page.waitForTimeout(100);
  check('desktop unmount removes every listener', (await page.evaluate(() => [...window.live.keys()].filter(k => !k.startsWith('selectionchange')).length)) === 0);
});

for (const r of results) console.log(r.join(' | '));
console.log(results.filter(r => r[0] === 'FAIL').length + ' failed of ' + results.length);
await browser.close();
