// Offline check of the `items` mechanism in Chromium (module/tools/harness/README.md): a synthetic host component whose items build
// `obc-app-button` elements, built by `items_bundle.py` from the generator's own wrapper. Run from the repository root.
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright');
import { execFileSync } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const out = mkdtempSync(join(tmpdir(), 'cadre-items-'));
execFileSync(process.env.PYTHON || 'python3', [join(here, 'items_bundle.py'), out]);
const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 700, height: 400 } });
const logs = [];
page.on('pageerror', e => logs.push('ERR ' + e));
page.on('console', m => logs.push(m.type() + ' ' + m.text()));
await page.goto(pathToFileURL(join(out, 'harness.html')).href);
await page.waitForFunction(() => Object.keys(window.registry).length >= 1);

const results = [];
function check(name, ok, detail) { results.push([ok ? 'PASS' : 'FAIL', name, detail === undefined ? '' : JSON.stringify(detail)]); }

const r = await page.evaluate(async () => {
  const st = document.getElementById('stage'); st.innerHTML = '<div id="m"></div>';
  const list = [
    { tag: 'obc-app-button', id: 'a1', label: 'Home', checked: true, bogus: 1, children: [
      { tag: 'obc-notification-badge-button', id: 'n1', indent: true, text: '7', slot: 'icon' },
      { tag: 'obi-info', slot: 'icon' }, { tag: 'span', text: 'plain' }, { tag: 'div', text: 'not allowed' }, { tag: 'obi-not-an-icon' }] },
    { tag: 'obc-tooltip' },
    { tag: 'obc-app-button', label: 'Second', size: 'small' }];
  const other = [{ tag: 'obc-app-button', label: 'Slotted' }];
  const h = window.mount('test.host', { items: list, other }, document.getElementById('m'));
  await new Promise(r => setTimeout(r, 400));
  const host = document.querySelector('#m obc-notification-badge-button');
  const dump = (n) => ({ t: n.tagName.toLowerCase(), slot: n.getAttribute('slot'), id: n.getAttribute('data-item-id'), label: n.label,
                         checked: n.checked, size: n.size, text: n.children.length ? undefined : n.textContent, kids: [...n.children].map(dump) });
  const first = [...host.children].map(dump);
  window.fired = [];
  host.querySelector('obc-app-button obc-notification-badge-button').click();
  await new Promise(r => setTimeout(r, 100));
  const fired = window.fired.slice();
  const before = host.children[0];
  h.rerender({ items: list, other });
  await new Promise(r => setTimeout(r, 100));
  const same = host.children[0] === before;
  h.rerender({ items: [{ tag: 'obc-app-button', label: 'Only' }], other: [] });
  await new Promise(r => setTimeout(r, 100));
  const second = [...host.children].map(dump);
  h.unmount();
  return { first, fired, same, second };
});
check('three top level items built: the tooltip is refused', r.first.length === 3 && r.first.map(n => n.t).join() === 'obc-app-button,obc-app-button,obc-app-button', r.first.map(n => n.t));
check('attributes are set as properties (a boolean and a string)', r.first[0].label === 'Home' && r.first[0].checked === true, [r.first[0].label, r.first[0].checked]);
check('id becomes data-item-id', r.first[0].id === 'a1', r.first[0].id);
check('nested children: a slotted item, an icon and a span; a div and an unknown icon are refused',
      r.first[0].kids.map(n => n.t).join() === 'obc-notification-badge-button,obi-info,span' && r.first[0].kids[0].slot === 'icon', r.first[0].kids.map(n => n.t));
check('text becomes the text of the element', r.first[0].kids[2].text === 'plain' && r.first[0].kids[0].text === '7', r.first[0].kids.map(n => n.text));
check('an entry with a slot puts it on its top level items', r.first[2].slot === 'x' && r.first[2].label === 'Slotted', r.first[2].slot);
check('an event from a nested item reports its id and tag', r.fired.length === 1 && r.fired[0][0] === 'onPress' && r.fired[0][1].id === 'n1'
      && r.fired[0][1].tag === 'obc-notification-badge-button', r.fired);
check('the same list leaves the children alone', r.same);
check('a changed list replaces the children, and an emptied entry removes its own', r.second.length === 1 && r.second[0].label === 'Only', r.second.map(n => n.label));
check('unwanted tags and attributes warn on the console', ['bogus', 'div', 'obi-not-an-icon', 'obc-tooltip'].every(w => logs.some(l => l.startsWith('warning') && l.includes(w))), logs);
check('no console error or page error', !logs.some(l => l.startsWith('ERR') || l.startsWith('error')), logs);

for (const [s, n, d] of results) console.log(s, n, d);
await browser.close();
process.exit(results.some(r => r[0] === 'FAIL') ? 1 : 0);
