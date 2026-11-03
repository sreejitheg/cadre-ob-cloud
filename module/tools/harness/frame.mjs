// Offline check of the frame leaf components (T2, batch F1) in Chromium: slot properties (text and icon), the carried events and
// their payloads, and an optional text that is undefined while empty (module/tools/harness/README.md). Run from the repository root.
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright');
import { pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const url = pathToFileURL(join(dirname(fileURLToPath(import.meta.url)), 'harness.html')).href;
const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(m.text()); });
await page.goto(url);
await page.waitForFunction(() => Object.keys(window.registry).length >= 60);
const results = [];
function check(name, ok, detail) { results.push([ok ? 'PASS' : 'FAIL', name, detail === undefined ? '' : JSON.stringify(detail)]); }

// mount one component, return what is asked of its element (a function of the element, run in the page)
async function probe(type, tag, raw, fn) {
  return page.evaluate(async ([type, tag, raw, fn]) => {
    const st = document.getElementById('stage');
    st.innerHTML = '<div id="m" style="width:320px;height:240px"></div>';
    window.fired = [];
    window.h = window.mount(type, raw, document.getElementById('m'));
    await new Promise(r => setTimeout(r, 300));
    const el = document.querySelector('#m ' + tag);
    await el.updateComplete;
    return eval(fn)(el);
  }, [type, tag, raw, fn]);
}
const kids = '(el) => [...el.childNodes].map(n => n.nodeType === 3 ? "#" + n.textContent : n.tagName.toLowerCase() + "[" + n.getAttribute("slot") + "]")';

let r = await probe('cadre.ob.tooltip', 'obc-tooltip', { type: 'icon', iconName: 'info' }, kids);
check('tooltip icon slot holds the named icon', r.join() === 'obi-info[icon]', r);
r = await probe('cadre.ob.tooltip', 'obc-tooltip', { type: 'icon', iconName: 'no-such-icon' }, kids);
check('an icon name outside the bundled list draws no child', r.length === 0, r);
r = await probe('cadre.ob.tooltip', 'obc-tooltip', { label: 'Pump running' }, '(el) => el.label');
check('tooltip label is the element attribute', r === 'Pump running', r);

r = await probe('cadre.ob.toggletip', 'obc-toggletip', { title: 'T', hasContent: true, content: 'Body', leadingIconName: 'info', trailingIconName: 'close-google' }, kids);
check('toggletip content is a span in the content slot, the icons are in theirs', r.sort().join() === 'obi-close-google[trailing-icon],obi-info[leading-icon],span[content]', r);
r = await probe('cadre.ob.toggletip', 'obc-toggletip', { title: 'T' }, '(el) => [el.description === undefined, el.customWidth === undefined]');
check('toggletip description and width are undefined while empty', r[0] === true && r[1] === true, r);
r = await probe('cadre.ob.toggletip', 'obc-toggletip', { title: 'T', description: 'D', customWidth: 280 }, '(el) => [el.description, el.customWidth]');
check('toggletip description and width reach the element', r[0] === 'D' && r[1] === 280, r);
r = await probe('cadre.ob.toggletip', 'obc-toggletip', { title: 'T', hasActions: true, primaryButtonLabel: 'Open', secondaryButtonLabel: 'Close' },
  `async (el) => { const b = [...el.shadowRoot.querySelectorAll("obc-button")]; b.forEach(x => x.click()); await new Promise(r => setTimeout(r, 100)); return window.fired; }`);
check('toggletip carries primary-action and secondary-action with the label', JSON.stringify(r) === JSON.stringify([['onPrimaryAction', { label: 'Open' }], ['onSecondaryAction', { label: 'Close' }]]), r);

r = await probe('cadre.ob.clock', 'obc-clock', { date: '2026-01-01T09:30:45Z', showSeconds: true }, '(el) => el.shadowRoot.querySelector(".clock").textContent.replace(/\\s+/g, "")');
check('clock draws the given UTC time (the ticks are drawn, not typed)', r === '093045', r);
r = await probe('cadre.ob.clock', 'obc-clock', { date: '2026-01-01T09:30:45Z', isClickable: false }, '(el) => el.shadowRoot.querySelector(".wrapper").tagName');
check('clock isClickable false draws a plain block', r === 'DIV', r);

r = await probe('cadre.ob.userbutton', 'obc-user-button', { label: '', sublabel: '' }, '(el) => [el.label === undefined, el.sublabel === undefined]');
check('user button label and sublabel are undefined while empty', r[0] && r[1], r);
r = await probe('cadre.ob.userbutton', 'obc-user-button', { iconName: 'user-settings' }, kids);
check('user button icon slot holds the named icon', r.join() === 'obi-user-settings[icon]', r);

r = await probe('cadre.ob.appbutton', 'obc-app-button', { label: 'Home', iconName: 'home', showLabel: false }, '(el) => [el.showLabel, !!el.shadowRoot.querySelector(".label")]');
check('app button showLabel false hides the label', r[0] === false && r[1] === false, r);
r = await probe('cadre.ob.appbutton', 'obc-app-button', { label: 'Home', iconName: 'home' }, '(el) => { el.click(); return window.fired; }');
check('app button carries click as onPress with no detail', JSON.stringify(r) === JSON.stringify([['onPress', {}]]), r);

r = await probe('cadre.ob.notificationbutton', 'obc-notification-button', { count: 5, showCount: true, isActive: false }, '(el) => { el.shadowRoot.querySelector("button").click(); return window.fired; }');
check('notification button carries obc-click with the count and the requested state', JSON.stringify(r) === JSON.stringify([['onNotificationClick', { count: 5, isActive: true }]]), r);
r = await probe('cadre.ob.notificationbutton', 'obc-notification-button', { iconName: 'alarm' }, kids);
check('notification button icon slot holds the named icon', r.join() === 'obi-alarm[icon]', r);

r = await probe('cadre.ob.notificationbadgebutton', 'obc-notification-badge-button', { label: '12' }, kids);
check('badge button text is a text node of the default slot', r.join() === '#12', r);
r = await probe('cadre.ob.notificationbadgebutton', 'obc-notification-badge-button', { icon: true, iconName: 'info' }, kids);
check('badge button icon is a child of the default slot', r.join() === 'obi-info[null]', r);
r = await probe('cadre.ob.notificationbadgebutton', 'obc-notification-badge-button', { label: '1' }, '(el) => { el.shadowRoot.querySelector("button").click(); return window.fired; }');
check('badge button carries click as onPress with no detail', JSON.stringify(r) === JSON.stringify([['onPress', {}]]), r);

check('no console error or warning', errors.length === 0, errors);
for (const [s, n, d] of results) console.log(s, n, d);
await browser.close();
process.exit(results.some(r => r[0] === 'FAIL') ? 1 : 0);
