// Offline check of the alarm lists' row selection (module 0.4.2) in Chromium: the real OpenBridge alert list and alert
// panel in the harness page, with a stub Perspective client whose property write comes back after 60 ms, as a two way
// binding does (module/tools/harness/README.md). Real mouse clicks go through the shadow roots.
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright');
import { pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const url = pathToFileURL(join(dirname(fileURLToPath(import.meta.url)), 'harness.html')).href;
const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 760, height: 560 } });
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
await page.goto(url);
await page.waitForFunction(() => Object.keys(window.registry).length >= 11);

const results = [];
function check(name, ok, detail) { results.push([ok ? 'PASS' : 'FAIL', name, detail === undefined ? '' : JSON.stringify(detail)]); }
const out = process.env.HARNESS_OUT || '.';

// five alerts: four active and unacknowledged, one acknowledged
const NOW = Date.now();
const ALERTS = [
  { id: 'a1', tagId: 'T1', source: 'Pump 1', text: 'Pump 1 fault', acknowledged: false, active: true, type: 'alarm', time: NOW - 5000 },
  { id: 'a2', tagId: 'T2', source: 'Pump 2', text: 'Pump 2 high temperature', acknowledged: false, active: true, type: 'warning', time: NOW - 4000 },
  { id: 'a3', tagId: 'T3', source: 'Tank 1', text: 'Tank 1 level high', acknowledged: false, active: true, type: 'alarm', time: NOW - 3000 },
  { id: 'a4', tagId: 'T4', source: 'Fan 1', text: 'Fan 1 trip', acknowledged: false, active: true, type: 'caution', time: NOW - 2000 },
  { id: 'a5', tagId: 'T5', source: 'Valve 1', text: 'Valve 1 travel', acknowledged: { by: 'op', acknowledgedAt: NOW - 1000 }, active: true, type: 'warning', time: NOW - 1000 },
];

// mount(type, raw): the echo of a property write comes back after `delay` ms, like a two way binding
async function mount(type, raw, delay = 60) {
  await page.evaluate(([type, raw, delay]) => {
    window.fired = []; window.writes = [];
    document.getElementById('stage').innerHTML = '<div id="m" style="width:' + (type === 'cadre.ob.alertlist' ? 420 : 640) + 'px;height:420px"></div>';
    window.raw = raw;
    const store = { props: { write: (n, v) => {
      window.writes.push([n, v]);
      if (delay >= 0) setTimeout(() => { window.raw = Object.assign({}, window.raw, { [n]: v }); window.h.rerender(window.raw); }, delay);
    } } };
    window.h = window.mount(type, raw, document.getElementById('m'), store);
  }, [type, raw, delay]);
  await page.waitForTimeout(500);
}
const rerender = async (patch) => {
  await page.evaluate((patch) => { window.raw = Object.assign({}, window.raw, patch); window.h.rerender(window.raw); }, patch);
  await page.waitForTimeout(400);
};
const settle = () => page.waitForTimeout(350);
// the rows with the state of their tick, read through every shadow root
const rows = () => page.evaluate(() => {
  const find = (root, sel, acc = []) => {
    root.querySelectorAll(sel).forEach(n => acc.push(n));
    root.querySelectorAll('*').forEach(n => { if (n.shadowRoot) find(n.shadowRoot, sel, acc); });
    return acc;
  };
  const m = document.getElementById('m');
  return find(m, 'button[role="row"]').map(r => ({ id: r.getAttribute('data-row-id'), tick: !!r.querySelector('obc-checkbox'),
    checked: r.querySelector('obc-checkbox') ? r.querySelector('obc-checkbox').status === 'checked' : null,
    selected: r.classList.contains('selected') }));
});
const headerTicks = () => page.evaluate(() => {
  const find = (root, sel, acc = []) => {
    root.querySelectorAll(sel).forEach(n => acc.push(n));
    root.querySelectorAll('*').forEach(n => { if (n.shadowRoot) find(n.shadowRoot, sel, acc); });
    return acc;
  };
  return find(document.getElementById('m'), '.selection-header obc-checkbox').length;
});
const tableHtml = () => page.evaluate(() => {
  const find = (root, sel, acc = []) => {
    root.querySelectorAll(sel).forEach(n => acc.push(n));
    root.querySelectorAll('*').forEach(n => { if (n.shadowRoot) find(n.shadowRoot, sel, acc); });
    return acc;
  };
  const t = find(document.getElementById('m'), 'obc-table')[0];
  return t ? t.shadowRoot.innerHTML.replace(/<!--.*?-->/g, '').replace(/\s+/g, ' ').replace(/class="([^"]*)"/g, (m, c) => 'class="' + c.trim() + '"') : null;
});
const tickedIds = async () => (await rows()).filter(r => r.checked).map(r => r.id).sort();
const lastWrite = () => page.evaluate(() => { const w = window.writes.filter(x => x[0] === 'selectedIds'); return w.length ? w[w.length - 1][1] : null; });
const writeCount = () => page.evaluate(() => window.writes.length);
const fired = () => page.evaluate(() => window.fired);
const rowSel = (id) => `#m button[role="row"][data-row-id="${id}"]`;
const tick = (id) => page.locator(`${rowSel(id)} obc-checkbox`).first();
const cellText = (id) => page.locator(`${rowSel(id)} .grid-cell.regular`).first();
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

for (const [type, label] of [['cadre.ob.alertlist', 'list'], ['cadre.ob.alertpanel', 'panel']]) {
  const base = { alerts: ALERTS, selectedMode: 'all' };
  const shown = ['a1', 'a2', 'a3', 'a4', 'a5'];

  // ---- selectable false: nothing changes from 0.4.1
  await mount(type, { ...base });
  const htmlDefault = await tableHtml();
  let r = await rows();
  check(`${label}: selectable false draws no tick`, r.length === shown.length && r.every(x => !x.tick), r);
  check(`${label}: selectable false draws no header tick`, (await headerTicks()) === 0);
  await cellText('a2').click(); await settle();
  let f = await fired();
  check(`${label}: selectable false, a row click fires onRowClick once with the alert id`,
        f.length === 1 && f[0][0] === 'onRowClick' && same(f[0][1].ids, ['a2']), f);
  check(`${label}: selectable false writes nothing`, (await writeCount()) === 0);
  await mount(type, { ...base, selectable: false, selectedIds: ['a1'] });
  check(`${label}: selectable false with ids set: same table markup as without`, (await tableHtml()) === htmlDefault);
  check(`${label}: selectable false with ids set writes nothing`, (await writeCount()) === 0);

  // ---- selectable true: a tick on every row, checked for the ids in selectedIds
  await mount(type, { ...base, selectable: true, selectedIds: ['a1', 'a3'] });
  r = await rows();
  check(`${label}: selectable shows a tick on each row`, r.length === shown.length && r.every(x => x.tick), r);
  check(`${label}: ticks are checked for the ids in selectedIds`, same(await tickedIds(), ['a1', 'a3']), await tickedIds());
  check(`${label}: a selected row is drawn selected`, r.filter(x => x.selected).map(x => x.id).sort().join() === 'a1,a3', r);
  check(`${label}: select all tick in the header only on the full list`, (await headerTicks()) === (label === 'list' ? 1 : 0), await headerTicks());
  check(`${label}: setting the ids writes nothing back`, (await writeCount()) === 0, await page.evaluate(() => window.writes));
  await page.screenshot({ path: join(out, `alertselect-${label}.png`), clip: { x: 0, y: 0, width: label === 'list' ? 440 : 660, height: 430 } });

  // ---- a click on a tick toggles only the selection
  await tick('a2').click(); await settle();
  check(`${label}: a click on a tick writes the new ids`, same([...(await lastWrite())].sort(), ['a1', 'a2', 'a3']), await lastWrite());
  check(`${label}: the tick shows at once and after the echo`, same(await tickedIds(), ['a1', 'a2', 'a3']), await tickedIds());
  check(`${label}: a click on a tick fires no onRowClick`, (await fired()).length === 0, await fired());
  await tick('a2').click(); await settle();
  check(`${label}: a second click unticks`, same(await tickedIds(), ['a1', 'a3']) && same([...(await lastWrite())].sort(), ['a1', 'a3']), await lastWrite());
  // the corner of the tick's cell, away from the box, is still not a row click
  const cell = await page.locator(`${rowSel('a4')} .grid-cell.selection`).first().boundingBox();
  await page.mouse.click(cell.x + cell.width / 2, cell.y + cell.height / 2); await settle();
  check(`${label}: the middle of the tick cell toggles and fires no row click`, same(await tickedIds(), ['a1', 'a3', 'a4']) && (await fired()).length === 0, { t: await tickedIds(), f: await fired() });
  await tick('a4').click(); await settle();

  // ---- a click elsewhere on the row is the row click, and leaves the selection alone
  await cellText('a2').click(); await settle();
  f = await fired();
  check(`${label}: a click elsewhere fires onRowClick with the alert id`, f.length === 1 && f[0][0] === 'onRowClick' && same(f[0][1].ids, ['a2']), f);
  check(`${label}: a row click leaves the selection`, same(await tickedIds(), ['a1', 'a3']), await tickedIds());

  // ---- the ACK button of a row is the acknowledgement, not a selection
  const ack = page.locator(`${rowSel('a1')} obc-button, ${rowSel('a1')} button`).first();
  if (await page.locator(`${rowSel('a1')} [role="button"], ${rowSel('a1')} obc-table-cell-button, ${rowSel('a1')} obc-button`).count()) {
    await page.evaluate(() => { window.fired = []; });
    await page.locator(`${rowSel('a1')} obc-button, ${rowSel('a1')} obc-table-cell-button`).first().click(); await settle();
    f = await fired();
    check(`${label}: the ACK button fires onAckClick and leaves the selection`, f.some(x => x[0] === 'onAckClick' && same(x[1].ids, ['a1'])) && same(await tickedIds(), ['a1', 'a3']), { f, t: await tickedIds() });
  }

  // ---- two quick clicks before the first echo returns: neither is lost
  await mount(type, { ...base, selectable: true, selectedIds: [] }, 150);
  await tick('a1').click(); await tick('a2').click();
  await page.waitForTimeout(700);
  check(`${label}: two quick toggles both stay (the first echo does not undo the second)`, same(await tickedIds(), ['a1', 'a2']) && same([...(await lastWrite())].sort(), ['a1', 'a2']), { t: await tickedIds(), w: await lastWrite() });

  // ---- a change from outside wins (the library clears the selection after an acknowledgement)
  await mount(type, { ...base, selectable: true, selectedIds: ['a1', 'a2'] });
  await rerender({ selectedIds: [] });
  check(`${label}: an outside change of selectedIds shows`, (await tickedIds()).length === 0, await tickedIds());
  check(`${label}: and writes nothing back`, (await writeCount()) === 0, await page.evaluate(() => window.writes));
  await rerender({ selectedIds: ['a4'] });
  check(`${label}: an outside selection shows`, same(await tickedIds(), ['a4']), await tickedIds());

  // ---- stale ids: an alert that is gone is dropped from selectedIds
  await mount(type, { ...base, selectable: true, selectedIds: ['a1', 'a3', 'a9'] });
  check(`${label}: an id that is not in alerts is dropped at once`, same([...(await lastWrite())].sort(), ['a1', 'a3']), await lastWrite());
  await mount(type, { ...base, selectable: true, selectedIds: ['a1', 'a3'] });
  await rerender({ alerts: ALERTS.filter(a => a.id !== 'a3') });
  check(`${label}: stale: an alert that leaves the list leaves selectedIds`, same([...(await lastWrite())].sort(), ['a1']) && same(await tickedIds(), ['a1']), { w: await lastWrite(), t: await tickedIds() });
  await rerender({ alerts: ALERTS });
  check(`${label}: stale: it does not come back when the alert returns`, same(await tickedIds(), ['a1']), await tickedIds());
  await rerender({ alerts: [] });
  check(`${label}: stale: an empty list empties selectedIds`, same(await lastWrite(), []), await lastWrite());
  await rerender({ alerts: ALERTS });
  check(`${label}: the ticks are back on rows after an empty list`, (await rows()).every(x => x.tick) && (await rows()).length === shown.length, await rows());

  // ---- a mode that hides a selected row drops it (Ack selected must not touch rows that are not shown)
  await mount(type, { ...base, selectedMode: 'unacked', selectable: true, selectedIds: ['a2', 'a5'] });
  r = await rows();
  check(`${label}: unacked mode shows the unacknowledged alarms and warnings only`, same(r.map(x => x.id).sort(), ['a1', 'a2', 'a3']), r);
  check(`${label}: a selected row the mode does not show is dropped`, same(await lastWrite(), ['a2']) && same(await tickedIds(), ['a2']), { w: await lastWrite(), t: await tickedIds() });

  // ---- selectable can be switched off and on again
  await mount(type, { ...base, selectable: true, selectedIds: ['a1'] });
  await rerender({ selectable: false });
  r = await rows();
  check(`${label}: switching selectable off removes the ticks`, r.length === shown.length && r.every(x => !x.tick), r);
  const htmlOff = await tableHtml();
  let at = 0; while (at < htmlOff.length && htmlOff[at] === htmlDefault[at]) at++;
  check(`${label}: and restores the markup of 0.4.1`, htmlOff === htmlDefault, { at, now: htmlOff.slice(Math.max(0, at - 40), at + 200), was: htmlDefault.slice(Math.max(0, at - 40), at + 200) });
  await rerender({ selectable: true });
  check(`${label}: switching it on again shows the ticks`, same(await tickedIds(), ['a1']), await tickedIds());

  // ---- select all (full list only)
  if (label === 'list') {
    await mount(type, { ...base, selectable: true, selectedIds: [] });
    await page.locator('#m .selection-header obc-checkbox').first().click(); await settle();
    check(`list: the header tick selects every shown row`, same(await tickedIds(), shown) && same([...(await lastWrite())].sort(), shown), await lastWrite());
    await page.locator('#m .selection-header obc-checkbox').first().click(); await settle();
    check(`list: and clears them`, (await tickedIds()).length === 0 && same(await lastWrite(), []), await lastWrite());
  }
}

check('no page error', errors.length === 0, errors);

let fail = 0;
for (const [s, n, d] of results) { console.log(s, n, d); if (s === 'FAIL') fail++; }
console.log(`${results.length - fail} of ${results.length} checks pass`);
await browser.close();
process.exit(fail ? 1 : 0);
