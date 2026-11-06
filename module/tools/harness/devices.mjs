// Offline check of the module's browser side in Chromium: a page that loads the built bundle with a stub of the
// Perspective client (module/tools/harness/README.md).
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright');
import { pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const url = pathToFileURL(join(dirname(fileURLToPath(import.meta.url)), 'harness.html')).href;
const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
await page.goto(url);
await page.waitForFunction(() => Object.keys(window.registry).length >= 12);

const results = [];
function check(name, ok, detail) { results.push([ok ? 'PASS' : 'FAIL', name, detail === undefined ? '' : JSON.stringify(detail)]); }

// all text drawn by an element, through every shadow root
const deepText = `(el) => {
  const out = [];
  const walk = (n) => {
    if (n.shadowRoot) walk(n.shadowRoot);
    for (const c of n.childNodes) {
      if (c.nodeType === 3) { const t = c.textContent.trim(); if (t) out.push(t); }
      else if (c.nodeType === 1) walk(c);
    }
  };
  walk(el);
  return out;
}`;

async function pump(type, raw, label) {
  await page.evaluate(([type, raw]) => {
    const st = document.getElementById('stage');
    st.innerHTML = '<div id="m" style="width:96px;height:96px"></div>';
    window.h = window.mount(type, raw, document.getElementById('m'));
  }, [type, raw]);
  await page.waitForTimeout(300);
  return page.evaluate(`(async () => {
    const el = document.querySelector('#m ${type === 'cadre.ob.motor' ? 'obc-motor' : type === 'cadre.ob.fan' ? 'obc-fan' : 'obc-pump'}');
    await el.updateComplete;
    const deepText = ${deepText};
    const badges = [];
    const walk = (n) => { if (n.shadowRoot) walk(n.shadowRoot); for (const c of n.children || n.childNodes) { if (c.nodeType === 1) { if (c.tagName === 'OBC-AUTOMATION-BADGE') badges.push({ slot: c.getAttribute('slot'), type: c.type }); walk(c); } } };
    walk(el);
    const oos = document.querySelector('#m .cadre-ob-oos');
    const r = oos && oos.getBoundingClientRect();
    return { text: deepText(el), badges, oos: oos ? { text: oos.textContent, w: r.width, h: r.height } : null };
  })()`);
}

for (const type of ['cadre.ob.pump', 'cadre.ob.motor', 'cadre.ob.fan']) {
  let r = await pump(type, { on: false }, 'off');
  check(`${type} stopped draws Off`, r.text.includes('Off'), r.text);
  r = await pump(type, { on: false, showStatus: false }, 'off muted');
  check(`${type} stopped, showStatus false: no Off`, !r.text.includes('Off'), r.text);
  r = await pump(type, { on: true, hasSpeed: false }, 'on nospeed');
  check(`${type} running with no speed draws nothing natively`, !r.text.includes('On') && !r.text.includes('Off'), r.text);
  r = await pump(type, { on: true, hasSpeed: false, statusText: 'On' }, 'on text');
  check(`${type} statusText On draws On`, r.text.includes('On'), r.text);
  r = await pump(type, { on: true, hasSpeed: false, statusText: 'On', showStatus: false }, 'on text muted');
  check(`${type} statusText muted by showStatus false`, !r.text.includes('On'), r.text);
  r = await pump(type, { on: false, statusText: 'Standby' }, 'off text');
  check(`${type} stopped, statusText Standby replaces Off`, r.text.includes('Standby') && !r.text.includes('Off'), r.text);
  r = await pump(type, { on: true, speedInPercent: 80 }, 'on speed');
  check(`${type} running with speed 80 draws the speed`, r.text.some(t => t.includes('80') || t === '080') || r.text.join('').includes('80'), r.text);
  r = await pump(type, { on: true, speedInPercent: 80, showStatus: false }, 'speed muted');
  check(`${type} speed muted by showStatus false`, !r.text.join('').includes('80'), r.text);
  r = await pump(type, { badgeDuty: true }, 'duty');
  check(`${type} duty badge in bottom-left`, r.badges.some(b => b.slot === 'badge-bottom-left' && b.type === 'interlock'), r.badges);
  r = await pump(type, { badgeDuty: true, badgeInterlock: 'interlock-inhibit' }, 'duty2');
  check(`${type} duty badge moves to bottom-right when bottom-left is taken`, r.badges.some(b => b.slot === 'badge-bottom-right' && b.type === 'interlock'), r.badges);
  r = await pump(type, { badgeDuty: true, badgeInterlock: 'interlock' }, 'duty3');
  check(`${type} no extra duty badge beside the interlock badge`, !r.badges.some(b => b.slot && b.slot.startsWith('badge-') && b.type === 'interlock' && b.slot !== 'badge-bottom-left'), r.badges);
  r = await pump(type, { badgeDuty: false }, 'noduty');
  check(`${type} no duty badge by default`, !r.badges.some(b => b.slot), r.badges);
  r = await pump(type, { outOfService: true }, 'oos');
  check(`${type} out of service veil 48x48 with OOS`, r.oos && r.oos.text === 'OOS' && Math.round(r.oos.w) === 48 && Math.round(r.oos.h) === 48, r.oos);
  r = await pump(type, {}, 'no oos');
  check(`${type} no veil by default`, r.oos === null, r.oos);
}

// The generator (module 0.4.4, ruling RW-01): `obc-automation-button` with the pinned generator icons, which the wrapper
// places in the button's icon slots by `on` and replaces when `on` changes (NOTE-WFB-10 section 16.3, Table 16.3).
const GEN = 'cadre.ob.generator';
async function generator(raw, label) {
  await page.evaluate(([type, raw]) => {
    const st = document.getElementById('stage');
    st.innerHTML = '<div id="m" style="width:96px;height:96px"></div>';
    window.h = window.mount(type, raw, document.getElementById('m'));
  }, [GEN, raw]);
  await page.waitForTimeout(300);
  return generatorState();
}
function generatorState() {
  return page.evaluate(`(async () => {
    const el = document.querySelector('#m obc-automation-button');
    await el.updateComplete;
    const deepText = ${deepText};
    const icons = [...el.children].filter((c) => c.tagName.startsWith('OBI-'))
      .map((c) => ({ tag: c.tagName.toLowerCase(), slot: c.getAttribute('slot') }));
    const oos = document.querySelector('#m .cadre-ob-oos');
    return { icons, text: deepText(el), alert: el.alert, status: el.alertFrameStatus, oos: oos ? oos.textContent : null };
  })()`);
}
const ON = 'obi-electric-generator-on', OFF = 'obi-electric-generator-off';
const only = (r, tag) => ['icon', 'icon-silhouette'].every((s) => r.icons.filter((i) => i.slot === s).length === 1 &&
  r.icons.some((i) => i.slot === s && i.tag === tag)) && r.icons.length === 2;
{
  let r = await generator({ on: true }, 'running');
  check(`${GEN} generator running: the ${ON} icon in both icon slots`, only(r, ON), r.icons);
  r = await generator({ on: false }, 'stopped');
  check(`${GEN} generator stopped: the ${OFF} icon in both icon slots`, only(r, OFF), r.icons);
  r = await generator({ on: true, alert: true, alertFrameStatus: 'alarm' }, 'fault');
  check(`${GEN} generator fault: the running icon and the element's alert frame at the alarm level`,
    only(r, ON) && r.alert === true && r.status === 'alarm', r);
  r = await generator({ on: false, outOfService: true }, 'out of service');
  check(`${GEN} generator out of service: the stopped icon and the veil with OOS`, only(r, OFF) && r.oos === 'OOS', r);
  // the icon is replaced when `on` changes: one element per slot after each change, never two stacked
  r = await generator({ on: false }, 'change');
  await page.evaluate(() => window.h.rerender({ on: true }));
  await page.waitForTimeout(300);
  r = await generatorState();
  check(`${GEN} generator running after stopped: the icon is replaced, not stacked`, only(r, ON), r.icons);
  await page.evaluate(() => window.h.rerender({ on: false }));
  await page.waitForTimeout(300);
  r = await generatorState();
  check(`${GEN} generator stopped after running: the icon is replaced, not stacked`, only(r, OFF), r.icons);
  // the status word: statusText when given, else On or Off from `on`; none while showStatus is false
  r = await generator({ on: true, statusText: 'Running' }, 'word');
  check(`${GEN} generator running: statusText Running is the status word`, r.text.includes('Running'), r.text);
  r = await generator({ on: true }, 'on');
  check(`${GEN} generator running with no statusText draws On`, r.text.includes('On'), r.text);
  r = await generator({ on: false }, 'off');
  check(`${GEN} generator stopped with no statusText draws Off`, r.text.includes('Off'), r.text);
  r = await generator({ on: true, statusText: 'Running', showStatus: false }, 'muted');
  check(`${GEN} generator running, showStatus false: no status word`, !r.text.includes('Running') && !r.text.includes('On'), r.text);
  r = await generator({ on: true, tag: 'GEN-1', positioning: 'symbol' }, 'tag');
  check(`${GEN} generator running keeps its identifier`, r.text.includes('GEN-1'), r.text);
}

// the pump drawn with every new prop, for the screenshot
await page.evaluate(() => {
  const st = document.getElementById('stage');
  st.innerHTML = '<div style="display:flex;gap:24px;padding:24px"><div id="a" style="width:96px;height:96px"></div><div id="b" style="width:96px;height:96px"></div><div id="c" style="width:96px;height:96px"></div><div id="d" style="width:96px;height:96px"></div></div>';
  window.mount('cadre.ob.pump', { on: true, hasSpeed: false, statusText: 'On', tag: 'P-101', positioning: 'symbol', badgeDuty: true }, document.getElementById('a'));
  window.mount('cadre.ob.pump', { on: false, tag: 'P-102', positioning: 'symbol', outOfService: true }, document.getElementById('b'));
  window.mount('cadre.ob.pump', { on: false, tag: 'P-103', positioning: 'symbol', showStatus: false }, document.getElementById('c'));
  window.mount('cadre.ob.motor', { on: true, speedInPercent: 55, tag: 'M-201', positioning: 'symbol' }, document.getElementById('d'));
});
await page.waitForTimeout(500);
await page.screenshot({ path: join(process.env.HARNESS_OUT || '.', 'devices.png'), clip: { x: 0, y: 0, width: 520, height: 170 } });

// readout stretch
const widths = await page.evaluate(async () => {
  const st = document.getElementById('stage');
  st.innerHTML = '';
  const out = {};
  for (const stretch of [false, true]) {
    for (const [i, v] of [[0, 5.5], [1, 1234.5]]) {
      const d = document.createElement('div'); d.className = 'box'; d.id = `r${stretch ? 's' : 'n'}${i}`;
      st.appendChild(d);
      window.mount('cadre.ob.readout', { value: v, unit: i ? 'm3/h' : '%', idTag: i ? 'FIT-101' : 'LT-1', stretch, fractionDigits: 1 }, d);
    }
  }
  await new Promise(r => setTimeout(r, 600));
  for (const id of ['rn0', 'rn1', 'rs0', 'rs1']) {
    const el = document.querySelector(`#${id} obc-transmitter`);
    await el.updateComplete;
    const chip = el.shadowRoot.querySelector('obc-transmitter-button');
    await chip.updateComplete;
    const wrap = chip.shadowRoot.querySelector('.visible-wrapper');
    out[id] = { host: Math.round(el.getBoundingClientRect().width), chip: Math.round(wrap.getBoundingClientRect().width), box: Math.round(document.getElementById(id).getBoundingClientRect().width) };
  }
  return out;
});
check('readout without stretch sizes to content (widths differ)', widths.rn0.chip !== widths.rn1.chip, widths);
check('readout with stretch fills the box (equal chip widths)', widths.rs0.chip === widths.rs1.chip && widths.rs0.chip >= widths.rs0.box - 4, widths);
await page.screenshot({ path: join(process.env.HARNESS_OUT || '.', 'readouts.png'), clip: { x: 0, y: 0, width: 260, height: 220 } });

check('no page errors', errors.length === 0, errors);
for (const r of results) console.log(r.join(' | '));
console.log(results.filter(r => r[0] === 'FAIL').length + ' failed of ' + results.length);
await browser.close();
