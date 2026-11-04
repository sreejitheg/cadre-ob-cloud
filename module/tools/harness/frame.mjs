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

// ---- batch F2: the alert button and the alert menu
r = await probe('cadre.ob.alertbuttonitem', 'obc-alert-button-item', { nAlerts: 2, alertType: '' }, '(el) => [el.alertType === undefined, el.nAlerts]');
check('alert button item alertType is undefined while empty', r[0] === true && r[1] === 2, r);
r = await probe('cadre.ob.alertbuttonitem', 'obc-alert-button-item', { nAlerts: 2, alertType: 'level-critical' }, '(el) => [el.alertType]');
check('alert button item alertType reaches the element', r[0] === 'level-critical', r);
r = await probe('cadre.ob.alertbuttonitem', 'obc-alert-button-item', { nAlerts: 2 }, '(el) => { el.click(); return window.fired; }');
check('alert button item carries click as onPress with no detail', JSON.stringify(r) === JSON.stringify([['onPress', {}]]), r);

r = await probe('cadre.ob.alertbutton', 'obc-alert-button', { nAlerts: 2, alertType: 'alarm' }, '(el) => [el.showSilenceButton, !!el.shadowRoot.querySelector("obc-button")]');
check('alert button hides the silence control by default', r[0] === false, r);
r = await probe('cadre.ob.alertbutton', 'obc-alert-button', { nAlerts: 2, alertType: 'alarm', showSilenceButton: true },
  `async (el) => { await el.updateComplete; const bs = [...el.shadowRoot.querySelectorAll("button, obc-alert-button-item")]; bs.forEach(b => b.click()); await new Promise(r => setTimeout(r, 100)); return window.fired.map(f => f[0]); }`);
check('alert button carries click-alert and click-silence', r.includes('onAlertClick') && r.includes('onSilenceClick'), r);

r = await probe('cadre.ob.alertmenuitem', 'obc-alert-menu-item', { title: 'T', alertIcon: [{ tag: 'obc-alert-icon', type: 'alarm', active: true }], hasIcon: true, iconName: 'info' }, kids);
check('alert menu item: the alert icon is an item in its slot, the icon a slot property', r.sort().join() === 'obc-alert-icon[alert-icon],obi-info[icon]', r);
r = await probe('cadre.ob.alertmenuitem', 'obc-alert-menu-item', { title: 'T', status: 'unacknowledged' },
  `async (el) => { el.dispatchEvent(new CustomEvent("item-click")); el.dispatchEvent(new CustomEvent("ack-click")); el.dispatchEvent(new CustomEvent("ack-secondary-click")); return window.fired; }`);
check('alert menu item carries its three events with no detail', JSON.stringify(r) === JSON.stringify([['onItemClick', {}], ['onAckClick', {}], ['onAckSecondaryClick', {}]]), r);

const rows = [{ tag: 'obc-alert-menu-item', id: 'A-1', title: 'One', status: 'unacknowledged' },
              { tag: 'obc-alert-menu-item', id: 'A-2', title: 'Two', status: 'acknowledged', children: [{ tag: 'obc-alert-icon', slot: 'alert-icon', type: 'warning' }] },
              { tag: 'obc-alert-menu-item', title: 'No id' }];
r = await probe('cadre.ob.alertmenu', 'obc-alert-menu', { items: rows }, '(el) => [...el.children].map(n => n.tagName.toLowerCase() + ":" + (n.getAttribute("data-item-id") || "") + ":" + n.children.length)');
check('alert menu builds one row element for each item, with its nested icon', r.join() === 'obc-alert-menu-item:A-1:0,obc-alert-menu-item:A-2:1,obc-alert-menu-item::0', r);
r = await probe('cadre.ob.alertmenu', 'obc-alert-menu', { items: rows },
  `async (el) => { const k = [...el.children]; k[0].dispatchEvent(new CustomEvent("ack-click")); k[1].dispatchEvent(new CustomEvent("item-click")); k[2].dispatchEvent(new CustomEvent("ack-secondary-click")); return window.fired; }`);
check('alert menu hears the events of its rows (which do not bubble) and reports the row id and tag',
  JSON.stringify(r) === JSON.stringify([['onAckClick', { id: 'A-1', tag: 'obc-alert-menu-item' }], ['onItemClick', { id: 'A-2', tag: 'obc-alert-menu-item' }],
                                       ['onAckSecondaryClick', { id: '', tag: 'obc-alert-menu-item' }]]), r);
r = await probe('cadre.ob.alertmenu', 'obc-alert-menu', { items: rows, canAckAll: true },
  `async (el) => { await el.updateComplete; const b = [...el.shadowRoot.querySelectorAll("obc-button")].filter(x => /ack/i.test(x.textContent)); b.forEach(x => x.click()); await new Promise(r => setTimeout(r, 100)); return window.fired.filter(f => f[0] === "onAckAllClick"); }`);
check('alert menu carries ACK visible with the tab and the ids of the visible rows', r.length === 1 && r[0][1].mode && Array.isArray(r[0][1].ids), r);
r = await probe('cadre.ob.alertmenu', 'obc-alert-menu', { items: rows }, '(el) => [el.showSilenceButton, el.showAlertListButton]');
check('alert menu hides the Silence button by default and keeps the Alerts button', r[0] === false && r[1] === true, r);
r = await probe('cadre.ob.alertmenu', 'obc-alert-menu', { items: rows, showSilenceButton: true },
  `async (el) => { await el.updateComplete; const b = [...el.shadowRoot.querySelectorAll("obc-button")]; b.forEach(x => x.click()); await new Promise(r => setTimeout(r, 100)); return window.fired.map(f => f[0]); }`);
check('alert menu carries silence-click and go-to-alert-list-click', r.includes('onSilenceClick') && r.includes('onGoToAlertListClick'), r);
r = await probe('cadre.ob.alertmenu', 'obc-alert-menu', { items: [rows[0], { tag: 'obc-notanitem' }] }, '(el) => el.children.length');
check('alert menu drops a tag that is not allowed', r === 1, r);

// ---- batch F3: navigation, tree navigation and the breadcrumb
const navRows = [{ tag: 'obc-navigation-item', id: 'n-home', label: 'Home', hasIcon: true, checked: true, children: [{ tag: 'obi-home', slot: 'icon' }] },
  { tag: 'obc-navigation-item-group', id: 'g-plant', label: 'Plant', hasIcon: true, defaultOpen: true, children: [
    { tag: 'obi-dashboard', slot: 'icon' },
    { tag: 'obc-navigation-item', id: 'n-pumps', label: 'Pumps' },
    { tag: 'obc-navigation-item-group', id: 'g-tanks', label: 'Tanks', children: [{ tag: 'obc-navigation-item', id: 'n-t201', label: 'T-201' }] }] }];
const navFoot = [{ tag: 'obc-navigation-item', id: 'n-help', label: 'Help' }];
r = await probe('cadre.ob.navigationitem', 'obc-navigation-item', { label: 'Home', hasIcon: true, iconName: 'home', hasTrailingIcon: true, trailingIconName: 'info' }, kids);
check('navigation item: both icon slots hold the named icons', r.sort().join() === 'obi-home[icon],obi-info[trailing-icon]', r);
r = await probe('cadre.ob.navigationitem', 'obc-navigation-item', { label: 'Home' }, '(el) => [el.href === undefined, el.alerts === undefined, el.variant, el.terminalType]');
check('navigation item: href and alerts are undefined while empty', r[0] === true && r[1] === true && r[2] === 'full' && r[3] === 'regular', r);
r = await probe('cadre.ob.navigationitem', 'obc-navigation-item', { label: 'Home' }, '(el) => { el.shadowRoot.querySelector("a").click(); return window.fired; }');
check('navigation item carries its click as onPress with no detail', JSON.stringify(r) === JSON.stringify([['onPress', {}]]), r);
r = await probe('cadre.ob.navigationitemgroup', 'obc-navigation-item-group', { label: 'Plant', items: navRows[1].children.slice(1), iconName: 'dashboard', hasIcon: true }, kids);
check('navigation group builds its child items and has the named icon', r.sort().join() === 'obc-navigation-item-group[null],obc-navigation-item[null],obi-dashboard[icon]', r);
r = await probe('cadre.ob.navigationitemgroup', 'obc-navigation-item-group', { label: 'Plant', items: navRows[1].children.slice(1) },
  '(el) => { el.shadowRoot.querySelector("a, .group-item, obc-navigation-item").click(); return window.fired; }');
check('navigation group carries open with no detail', JSON.stringify(r) === JSON.stringify([['onOpen', {}]]), r);
r = await probe('cadre.ob.navigationmenu', 'obc-navigation-menu', { items: navRows, footerItems: navFoot },
  '(el) => [...el.children].map(n => n.tagName.toLowerCase() + "[" + n.getAttribute("slot") + "]:" + n.getAttribute("data-item-id") + ":" + n.querySelectorAll("*").length)');
check('navigation menu puts items in main and footer and nests to two levels', r.join() === 'obc-navigation-item[main]:n-home:1,obc-navigation-item-group[main]:g-plant:4,obc-navigation-item[footer]:n-help:0', r);
r = await probe('cadre.ob.navigationmenu', 'obc-navigation-menu', { items: navRows, footerItems: navFoot },
  `async (el) => { await new Promise(r => setTimeout(r, 200)); const q = (id) => el.querySelector('[data-item-id="' + id + '"]');
     q('n-t201').shadowRoot.querySelector('a').click(); q('n-pumps').shadowRoot.querySelector('a').click(); q('n-help').shadowRoot.querySelector('a').click();
     q('g-tanks').open(); await new Promise(r => setTimeout(r, 100)); return window.fired; }`);
check('navigation menu reports each press once, with the id of the nested item that was pressed',
  JSON.stringify(r) === JSON.stringify([['onItemClick', { id: 'n-t201', tag: 'obc-navigation-item' }], ['onItemClick', { id: 'n-pumps', tag: 'obc-navigation-item' }],
    ['onItemClick', { id: 'n-help', tag: 'obc-navigation-item' }], ['onGroupOpen', { id: 'g-tanks', tag: 'obc-navigation-item-group' }]]), r);
r = await probe('cadre.ob.navigationmenu', 'obc-navigation-menu', { items: navRows, footerItems: navFoot, variant: 'tree' },
  `async (el) => { await new Promise(r => setTimeout(r, 300)); const q = (id) => el.querySelector('[data-item-id="' + id + '"]'); return [q('n-t201').treeMode, q('n-t201').treeBranches.length, q('n-help').treeMode]; }`);
check('navigation menu in the tree variant sets the tree mode and the branches of nested rows itself', r[0] === true && r[1] === 2 && r[2] === false, r);

const alerts = { countAlarm: 2, countCaution: 1 };
const treeRows = [{ tag: 'obc-tree-navigation-group', id: 't-vessel', label: 'Vessel', expanded: true, alerts, children: [
    { tag: 'obi-home', slot: 'icon' },
    { tag: 'obc-tree-navigation-group', id: 't-engine', label: 'Engine room', expanded: true, alerts: { countLevelCritical: 1, combine: true }, children: [
      { tag: 'obi-dashboard', slot: 'icon' },
      { tag: 'obc-tree-navigation-item', id: 't-p101', label: 'Pump P-101', hasLeadingIcon: false, alerts: { countWarning: 3 } },
      { tag: 'obc-tree-navigation-item', id: 't-p102', label: 'Pump P-102', hasLeadingIcon: false }] },
    { tag: 'obc-tree-navigation-item', id: 't-deck', label: 'Deck', hasLeadingIcon: false }] }];
r = await probe('cadre.ob.treenavigationitem', 'obc-tree-navigation-item', { label: 'Pump', alerts: { countAlarm: 2, countCaution: 1 }, iconName: 'info' },
  `async (el) => { await el.updateComplete; return [[...el.shadowRoot.querySelectorAll('obc-badge')].map(b => b.number).join(), [...el.childNodes].map(n => n.tagName.toLowerCase() + '[' + n.getAttribute('slot') + ']').join()]; }`);
check('tree item: the alerts object draws a badge for each severity and the icon is in its slot', r[0] === '2,1' && r[1] === 'obi-info[icon]', r);
r = await probe('cadre.ob.treenavigationitem', 'obc-tree-navigation-item', { label: 'Pump' }, '(el) => [el.alerts === undefined, el.href === undefined, el.hasLeadingIcon, el.terminalType]');
check('tree item: alerts and href are undefined while empty, the leading icon is on, terminal regular', r[0] && r[1] && r[2] === true && r[3] === 'regular', r);
r = await probe('cadre.ob.treenavigationitem', 'obc-tree-navigation-item', { label: 'Pump', expandable: true },
  '(el) => { el.shadowRoot.querySelector(".wrapper").click(); return window.fired; }');
check('tree item carries one expand-toggle (the state asked for) and one press for one click, not the native click as well',
  JSON.stringify(r) === JSON.stringify([['onExpandToggle', { expanded: true }], ['onPress', {}]]), r);
r = await probe('cadre.ob.treenavigationitem', 'obc-tree-navigation-item', { label: 'Pump', disabled: true }, '(el) => { el.shadowRoot.querySelector(".wrapper").click(); return window.fired; }');
check('a disabled tree item fires nothing', r.length === 0, r);
r = await probe('cadre.ob.treenavigationgroup', 'obc-tree-navigation-group', { label: 'Vessel', items: treeRows[0].children.slice(1), iconName: 'home' },
  `async (el) => { el.shadowRoot.querySelector('obc-tree-navigation-item').shadowRoot.querySelector('.wrapper').click(); await new Promise(r => setTimeout(r, 100));
     return [window.fired, el.expanded, [...el.childNodes].map(n => n.tagName.toLowerCase() + '[' + n.getAttribute('slot') + ']').join()]; }`);
check('tree group builds its rows and the icon, and carries expand-toggle once with the state asked for',
  JSON.stringify(r[0]) === JSON.stringify([['onExpandToggle', { expanded: true }]]) && r[1] === true &&
  r[2] === 'obi-home[icon],obc-tree-navigation-group[null],obc-tree-navigation-item[null]', r);
r = await probe('cadre.ob.treenavigation', 'obc-tree-navigation', { items: treeRows },
  `async (el) => { await new Promise(r => setTimeout(r, 300)); const q = (id) => el.querySelector('[data-item-id="' + id + '"]');
     return [q('t-p101').branches.join(), q('t-engine').branches.join(), q('t-vessel').branches.length, q('t-deck').branches.join(),
             q('t-vessel').alerts.countAlarm, q('t-engine').alerts.combine]; }`);
check('tree navigation: branches of the nested rows are set by the container (two levels)', r[0].split(',').length === 2 && r[3] === 'corner' && r[2] === 0 && r[4] === 2 && r[5] === true, r);
r = await probe('cadre.ob.treenavigation', 'obc-tree-navigation', { items: treeRows },
  `async (el) => { await new Promise(r => setTimeout(r, 300)); const q = (id) => el.querySelector('[data-item-id="' + id + '"]');
     q('t-p101').shadowRoot.querySelector('.wrapper').click(); q('t-p102').shadowRoot.querySelector('.wrapper').click();
     q('t-engine').shadowRoot.querySelector('obc-tree-navigation-item').shadowRoot.querySelector('.wrapper').click();
     await new Promise(r => setTimeout(r, 100)); return window.fired; }`);
check('tree navigation reports a press of a nested row once, with its id, and the toggle of a nested group with the state asked for',
  JSON.stringify(r) === JSON.stringify([['onItemClick', { id: 't-p101', tag: 'obc-tree-navigation-item' }], ['onItemClick', { id: 't-p102', tag: 'obc-tree-navigation-item' }],
    ['onExpandToggle', { id: 't-engine', tag: 'obc-tree-navigation-group', expanded: false }]]), r);
r = await probe('cadre.ob.treenavigation', 'obc-tree-navigation', { items: [treeRows[0], { tag: 'obc-navigation-item' }] }, '(el) => el.children.length');
check('tree navigation drops a tag that is not allowed', r === 1, r);

const crumbs = [{ label: 'Vessel', href: '/vessel' }, { label: 'Engine room', href: '/engine' }, { label: 'Pump P-101', icon: 'x' }];
r = await probe('cadre.ob.breadcrumb', 'obc-breadcrumb', { items: crumbs }, '(el) => [el.items.length, "icon" in el.items[2], [...el.shadowRoot.querySelectorAll(".label")].map(l => l.textContent).join()]');
check('breadcrumb: the crumbs are the element\'s own array, carrying label and href only', r[0] === 3 && r[1] === false && r[2] === 'Vessel,Engine room,Pump P-101', r);
r = await probe('cadre.ob.breadcrumb', 'obc-breadcrumb', { items: crumbs },
  '(el) => { const b = [...el.shadowRoot.querySelectorAll("button")]; b.forEach(x => x.click()); return [b.length, window.fired]; }');
check('breadcrumb carries a press as onBreadcrumbClick with label, href and index; the last crumb is no button',
  r[0] === 2 && JSON.stringify(r[1]) === JSON.stringify([['onBreadcrumbClick', { label: 'Vessel', href: '/vessel', index: 0 }], ['onBreadcrumbClick', { label: 'Engine room', href: '/engine', index: 1 }]]), r);
r = await probe('cadre.ob.breadcrumb', 'obc-breadcrumb', { items: crumbs, iconOnly: true }, '(el) => [...el.shadowRoot.querySelectorAll(".label")].map(l => l.textContent).join()');
check('breadcrumb iconOnly hides every label but the last', r === 'Pump P-101', r);

// batch F4: the menus and the top bar. `probeStore` mounts with a store that records the component's own property writes.
async function probeStore(type, tag, raw, fn) {
  return page.evaluate(async ([type, tag, raw, fn]) => {
    const st = document.getElementById('stage');
    st.innerHTML = '<div id="m" style="width:480px;height:360px"></div>';
    window.fired = [];
    window.writes = [];
    window.h = window.mount(type, raw, document.getElementById('m'), { props: { write: (n, v) => window.writes.push([n, v]) } });
    await new Promise(r => setTimeout(r, 300));
    const el = document.querySelector('#m ' + tag);
    await el.updateComplete;
    return eval(fn)(el);
  }, [type, tag, raw, fn]);
}
const settle = 'await new Promise(r => setTimeout(r, 150));';

r = await probeStore('cadre.ob.brilliancemenu', 'obc-brilliance-menu', { palette: 'day', brightness: 60 },
  `async (el) => { el.shadowRoot.querySelectorAll('.icon-button-container obc-button')[2].click(); ${settle} return [window.fired, window.writes, el.brightness]; }`);
check('brilliance menu: the increase button carries onBrightnessChanged with the new value and writes the component\'s brightness',
  JSON.stringify(r) === JSON.stringify([[['onBrightnessChanged', { value: 65 }]], [['brightness', 65]], 65]), r);
r = await probeStore('cadre.ob.brilliancemenu', 'obc-brilliance-menu', { palette: 'day', brightness: 60 },
  `async (el) => { el.nextPalette(); ${settle} return [window.fired, window.writes, el.palette]; }`);
check('brilliance menu: a palette press carries onPaletteChanged with the palette and writes the component\'s palette',
  JSON.stringify(r) === JSON.stringify([[['onPaletteChanged', { value: 'bright' }]], [['palette', 'bright']], 'bright']), r);
r = await probeStore('cadre.ob.brilliancemenu', 'obc-brilliance-menu', { palette: 'day', showLinkBrightness: true, showLinkPalette: true },
  `async (el) => { const t = [...el.shadowRoot.querySelectorAll('obc-toggle-switch')]; t.forEach(x => { x.checked = true; x.dispatchEvent(new Event('input')); }); ${settle} return [t.length, window.fired]; }`);
check('brilliance menu: the two link switches carry their state and write nothing',
  r[0] === 2 && JSON.stringify(r[1]) === JSON.stringify([['onLinkBrightnessChanged', { value: true }], ['onLinkPaletteChanged', { value: true }]]), r);
r = await probeStore('cadre.ob.brilliancemenu', 'obc-brilliance-menu', { palette: 'day' },
  `(el) => [el.shadowRoot.querySelectorAll('obc-toggle-switch').length, el.showLinkBrightness, el.showLinkPalette, el.showScreenControlLink]`);
check('brilliance menu: the link switches and the screen control link are off by default', r[0] === 0 && r[1] === false && r[2] === false && r[3] === false, r);
r = await probeStore('cadre.ob.brilliancemenu', 'obc-brilliance-menu', { palette: 'day', showBrightness: false },
  `(el) => [el.shadowRoot.querySelectorAll('.content-container.brilliance').length, el.shadowRoot.querySelectorAll('.content-container.palette').length]`);
check('brilliance menu: showBrightness false leaves the brightness section out', r[0] === 0 && r[1] === 1, r);

r = await probeStore('cadre.ob.usermenu', 'obc-user-menu', { type: 'sign-in' },
  `async (el) => { const b = [...el.shadowRoot.querySelectorAll('obc-button')]; b[0].click(); ${settle}
     return [el.shadowRoot.querySelectorAll('obc-text-input-field').length, b.map(x => x.textContent.trim()).join(), el.showUsername, el.showPassword, window.fired, el.username, el.password]; }`);
check('user menu: the sign in form is the title and the Sign in button (no input box), and the press carries nothing',
  r[0] === 0 && r[1] === 'Sign in' && r[2] === false && r[3] === false && JSON.stringify(r[4]) === JSON.stringify([['onSignInClick', {}]]) && r[5] === '' && r[6] === '', r);
r = await probeStore('cadre.ob.usermenu', 'obc-user-menu', { type: 'signed-in', userInitials: 'AB', userLabel: 'Alex Bravo', userRole: 'Operator' },
  `async (el) => { const b = [...el.shadowRoot.querySelectorAll('obc-button')]; b[b.length - 1].click(); ${settle}
     const u = el.shadowRoot.querySelector('obc-user-button');
     return [b.map(x => x.textContent.trim()).join(), u.initials, u.label, u.sublabel, window.fired]; }`);
check('user menu: the signed in form shows the user and a Sign out button that carries onSignOutClick',
  r[0] === 'Sign out' && r[1] === 'AB' && r[2] === 'Alex Bravo' && r[3] === 'Operator' && JSON.stringify(r[4]) === JSON.stringify([['onSignOutClick', {}]]), r);
r = await probeStore('cadre.ob.usermenu', 'obc-user-menu', { type: 'user-sign-in', userInitials: 'AB', userLabel: 'Alex Bravo' },
  `async (el) => { const b = [...el.shadowRoot.querySelectorAll('obc-button')]; b[1].click(); ${settle} return [b.map(x => x.textContent.trim()).join(), el.shadowRoot.querySelectorAll('obc-text-input-field').length, window.fired]; }`);
check('user menu: the user sign in form has no password box, and Use another account carries its event',
  r[0] === 'Sign in,Use another account' && r[1] === 0 && JSON.stringify(r[2]) === JSON.stringify([['onUseAnotherAccountClick', {}]]), r);
r = await probeStore('cadre.ob.usermenu', 'obc-user-menu', { userInitials: '', userLabel: '' }, '(el) => [el.userInitials === undefined, el.userLabel === undefined, el.userRole === undefined]');
check('user menu: initials, label and role are undefined while empty', r.every(Boolean), r);

const sys = { wifiState: { enabled: true, connected: true, networkName: 'Bridge network', strength: 3, status: 'Connected', networks: [{ name: 'Bridge network', signalStrength: 3 }], otherNetworks: [] },
  audioState: { muted: false, volume: 40, outputs: [{ name: 'Speakers' }], selectedOutput: 'Speakers' },
  microphoneState: { muted: true, currentLevel: 30, inputs: [{ name: 'Handset' }], selectedInput: 'Handset', pushToTalk: false },
  batteryState: { level: 80, charging: false, hasUsageButton: true, modes: [{ name: 'Normal' }], selectedMode: 'Normal' } };
r = await probeStore('cadre.ob.systemmenu', 'obc-system-menu', {},
  '(el) => [el.wifiState === undefined, el.audioState === undefined, el.microphoneState === undefined, el.batteryState === undefined, el.shadowRoot.querySelectorAll(".group").length]');
check('system menu: the four sections are undefined and nothing is drawn while their objects are empty', r.slice(0, 4).every(Boolean) && r[4] === 0, r);
r = await probeStore('cadre.ob.systemmenu', 'obc-system-menu', { ...sys, showSettingsButton: true },
  `async (el) => { ${settle} return [el.shadowRoot.querySelectorAll('.group').length, el.wifiState.networkName, el.shadowRoot.querySelectorAll('.title').length]; }`);
check('system menu: the four state objects draw their four sections and the settings button (five groups)', r[0] === 5 && r[1] === 'Bridge network', r);
r = await probeStore('cadre.ob.systemmenu', 'obc-system-menu', { ...sys, showSettingsButton: true },
  `async (el) => { const root = el.shadowRoot;
     root.querySelector('obc-icon-check-button').dispatchEvent(new CustomEvent('icon-check-button-click', { detail: { checked: false } }));
     el.shadowRoot.querySelector('obc-slider').dispatchEvent(new CustomEvent('value', { detail: 55 }));
     el.dispatchEvent(new CustomEvent('wifi-network-change', { detail: { network: 'Engine room link' } }));
     el.dispatchEvent(new CustomEvent('audio-output-change', { detail: { output: 'Headset' } }));
     el.dispatchEvent(new CustomEvent('battery-mode-change', { detail: { mode: 'Saving' } }));
     el.dispatchEvent(new CustomEvent('battery-usage-click', { detail: { usage: true } }));
     el.dispatchEvent(new CustomEvent('push-to-talk-change', { detail: { pushToTalk: true } }));
     el.dispatchEvent(new CustomEvent('microphone-click', { detail: { muted: false } }));
     el.dispatchEvent(new CustomEvent('settings-click'));
     el.dispatchEvent(new CustomEvent('to-sub-menu-click'));
     ${settle} return window.fired; }`);
check('system menu: the events carry their fields (wifi switch, volume, network, output, mode, usage, push to talk, microphone, settings, sub menu)',
  JSON.stringify(r) === JSON.stringify([['onWifiClick', { enabled: false }], ['onAudioVolumeChange', { volume: 55 }],
    ['onWifiNetworkChange', { network: 'Engine room link' }], ['onAudioOutputChange', { output: 'Headset' }], ['onBatteryModeChange', { mode: 'Saving' }],
    ['onBatteryUsageClick', { usage: true }], ['onPushToTalkChange', { pushToTalk: true }], ['onMicrophoneClick', { muted: false }],
    ['onSettingsClick', {}], ['onSubMenuClick', {}]]), r);
r = await probeStore('cadre.ob.systemmenu', 'obc-system-menu', { ...sys, activeSubMenu: 'wifi' },
  `async (el) => { ${settle} const names = [...el.shadowRoot.querySelectorAll('.title')].map(t => t.textContent.trim()); return [names.join(), el.activeSubMenu]; }`);
check('system menu: the wifi sub menu draws when activeSubMenu is wifi', r[1] === 'wifi' && /Wi-Fi/.test(r[0]), r);

const apps = [{ tag: 'obc-app-button', id: 'app-home', label: 'Home', children: [{ tag: 'obi-home', slot: 'icon' }] },
  { tag: 'obc-app-button', id: 'app-help', label: 'Help', children: [{ tag: 'obi-help', slot: 'icon' }] }];
r = await probeStore('cadre.ob.appmenu', 'obc-app-menu', { items: apps },
  `async (el) => { const kids = [...el.children].map(n => n.tagName.toLowerCase() + ':' + n.label + ':' + n.firstElementChild.tagName.toLowerCase() + '[' + n.firstElementChild.getAttribute('slot') + ']');
     el.children[1].click(); el.children[0].click(); ${settle} return [kids, window.fired]; }`);
check('app menu: the items are app buttons with their icon in the icon slot, and a press carries onAppClick with the button\'s id, once',
  JSON.stringify(r[0]) === JSON.stringify(['obc-app-button:Home:obi-home[icon]', 'obc-app-button:Help:obi-help[icon]']) &&
  JSON.stringify(r[1]) === JSON.stringify([['onAppClick', { id: 'app-help', tag: 'obc-app-button' }], ['onAppClick', { id: 'app-home', tag: 'obc-app-button' }]]), r);
r = await probeStore('cadre.ob.appmenu', 'obc-app-menu', { items: apps },
  `async (el) => { const f = el.shadowRoot.querySelector('obc-text-input-field'); f.value = 'hel'; f.dispatchEvent(new Event('input', { bubbles: true, composed: true })); ${settle} return window.fired; }`);
check('app menu: the search field carries onSearch with its text', JSON.stringify(r) === JSON.stringify([['onSearch', { query: 'hel' }]]), r);
r = await probeStore('cadre.ob.appmenu', 'obc-app-menu', { items: [apps[0], { tag: 'obc-navigation-item' }, { tag: 'obc-app-button', id: 'x', bogus: 1 }] }, '(el) => el.children.length');
check('app menu: a tag that is not an app button is dropped', r === 2, r);

const cmd = { commandIconName: 'joystick', commandStatus: 'Joystick', commandDescription: 'Bridge wing', commandLocation: 'Bridge', takeCommandLabel: 'Take command',
  releaseCommandLabel: 'Release command', inCommandLabel: 'In command', noCommandLabel: 'No command', inCommandIconName: 'command-in' };
r = await probeStore('cadre.ob.commandmenu', 'obc-command-menu', cmd, kids);
check('command menu: the nine slot properties are text in their slots and icons in theirs',
  r.sort().join() === ['obi-command-in[toogle-state-in-command-icon]', 'obi-joystick[command-icon]', 'span[command-description]', 'span[command-location]',
    'span[command-status]', 'span[toogle-action-to-in-command-label]', 'span[toogle-action-to-no-command-label]', 'span[toogle-state-in-command-label]',
    'span[toogle-state-no-command-label]'].sort().join(), r);
r = await probeStore('cadre.ob.commandmenu', 'obc-command-menu', cmd,
  `async (el) => { const sw = el.shadowRoot.querySelector('obc-start-stop-switch'); sw.dispatchEvent(new CustomEvent('change', { detail: { checked: true } })); ${settle}
     return [window.fired, window.writes, el.inCommand, el.shadowRoot.querySelector('.card').className]; }`);
check('command menu: the switch carries onCommandChange with the state asked for, and the component\'s inCommand follows (no tag is written)',
  JSON.stringify(r[0]) === JSON.stringify([['onCommandChange', { inCommand: true }]]) && JSON.stringify(r[1]) === JSON.stringify([['inCommand', true]]) &&
  r[2] === true && /in-command/.test(r[3]), r);
r = await probeStore('cadre.ob.commandmenu', 'obc-command-menu', { ...cmd, showLocation: false }, '(el) => el.shadowRoot.querySelectorAll(".command-location").length');
check('command menu: showLocation false leaves the location out', r === 0, r);

const bar = { appTitle: 'Cadre HMI', pageName: 'Engine room', showClock: true, showUserButton: true, showDimmingButton: true, showAppsButton: true,
  date: '2026-01-01T09:30:45Z', showSeconds: true, nAlerts: 3, alertType: 'alarm', appIconName: 'dashboard', showAppIcon: true, commandButtonText: 'Command' };
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', bar,
  `async (el) => { await new Promise(r => setTimeout(r, 200)); const a = el.querySelector('obc-alert-button'), c = el.querySelector('obc-clock');
     return [[...el.children].map(n => n.tagName.toLowerCase() + '[' + n.getAttribute('slot') + ']').join(),
             [a.nAlerts, a.counter, a.alertType, a.showSilenceButton], [c.date, c.showSeconds, c.isClickable], c.shadowRoot.querySelector('.clock').textContent.replace(/\\s+/g, '')]; }`);
check('top bar: the alert button stands in the alerts slot, the clock in the clock slot, the app icon and command text in theirs, with the carried properties',
  r[0].split(',').sort().join() === 'obc-alert-button[alerts],obc-clock[clock],obi-dashboard[app-icon],span[command-button]' &&
  JSON.stringify(r[1]) === JSON.stringify([3, true, 'alarm', false]) && JSON.stringify(r[2]) === JSON.stringify(['2026-01-01T09:30:45Z', true, false]) && r[3] === '093045', r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', { showClock: true },
  '(el) => { const a = el.querySelector("obc-alert-button"); return [a.alertType === undefined, a.nAlerts, a.counter, a.blinking, a.showSilenceButton, el.shadowRoot.querySelectorAll(".silence-button").length]; }');
check('top bar: an empty alert type is undefined (idle), the silence control is off and the count is shown by default', r[0] && r[1] === 0 && r[2] === true && r[3] === false && r[4] === false && r[5] === 0, r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', bar,
  `async (el) => { window.h.rerender({ ...${JSON.stringify(bar)}, nAlerts: 7, blinking: true, alertType: 'level-critical', showSilenceButton: true, date: '2026-01-01T10:00:00Z' });
     await new Promise(r => setTimeout(r, 300)); const a = el.querySelector('obc-alert-button'), c = el.querySelector('obc-clock');
     return [a.nAlerts, a.blinking, a.alertType, a.showSilenceButton, c.date, el.children.length]; }`);
check('top bar: a later update reaches the alert button and the clock, and the children are not built twice',
  JSON.stringify(r) === JSON.stringify([7, true, 'level-critical', true, '2026-01-01T10:00:00Z', 4]), r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', { ...bar, showSilenceButton: true },
  `async (el) => { await new Promise(r => setTimeout(r, 200)); const a = el.querySelector('obc-alert-button'); await a.updateComplete;
     a.shadowRoot.querySelector('obc-alert-button-item').click(); a.shadowRoot.querySelector('.silence-button').click(); ${settle} return window.fired; }`);
check('top bar: the bell and the silence control of its alert button carry onAlertClick and onSilenceClick, once each',
  JSON.stringify(r) === JSON.stringify([['onAlertClick', {}], ['onSilenceClick', {}]]), r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', bar,
  `async (el) => { const q = (s) => el.shadowRoot.querySelector(s); q('.dimming-button').click(); q('.user-button').click(); q('.apps-button').click(); q('.left-more-button').click();
     const m = q('.menu-button obc-icon-button'); m.dispatchEvent(new Event('pointerdown')); m.dispatchEvent(new Event('pointerup')); ${settle} return window.fired; }`);
check('top bar: the dimming, user, apps, more and menu buttons carry their events and nothing else',
  JSON.stringify(r) === JSON.stringify([['onDimmingButtonClick', {}], ['onUserButtonClick', {}], ['onAppsButtonClick', {}], ['onMoreButtonClick', {}], ['onMenuButtonClick', {}]]), r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', bar,
  `async (el) => { const m = el.shadowRoot.querySelector('.menu-button obc-icon-button'); m.dispatchEvent(new Event('pointerdown')); await new Promise(r => setTimeout(r, 650));
     m.dispatchEvent(new Event('pointerup')); ${settle} return window.fired; }`);
check('top bar: holding the menu button carries the emergency brightness start and stop, and no menu press',
  JSON.stringify(r) === JSON.stringify([['onEmergencyBrightnessStart', {}], ['onEmergencyBrightnessStop', {}]]), r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', { appTitle: 'Cadre HMI', settings: true, breadcrumbItems: [{ label: 'Vessel', href: '/vessel', icon: 'x' }, { label: 'Engine room', href: '/engine' }, { label: 'Pump' }] },
  `async (el) => { await new Promise(r => setTimeout(r, 200)); const bc = el.shadowRoot.querySelector('obc-breadcrumb'); await bc.updateComplete;
     bc.shadowRoot.querySelector('button').click(); const back = [...el.shadowRoot.querySelectorAll('obc-icon-button')].find(b => b.getAttribute('aria-label') === 'Back'); back.click();
     const close = el.shadowRoot.querySelector('.menu-button obc-icon-button'); close.dispatchEvent(new Event('pointerdown')); close.dispatchEvent(new Event('pointerup')); ${settle}
     return [window.fired, 'icon' in el.breadcrumbItems[0]]; }`);
check('top bar: the settings mode carries a crumb press (label, href, index), Back and Close; the crumbs carry no icon',
  JSON.stringify(r[0]) === JSON.stringify([['onBreadcrumbClick', { label: 'Vessel', href: '/vessel', index: 0 }], ['onBack', {}], ['onClose', {}]]) && r[1] === false, r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', { ...bar, showClock: false, showAppIcon: false, showUserButton: false },
  '(el) => [el.shadowRoot.querySelectorAll(".user-button").length, el.shadowRoot.querySelectorAll("slot[name=clock]").length, el.shadowRoot.querySelectorAll(".app-icon").length]');
check('top bar: the show flags hide the user button, the clock slot and the app icon', JSON.stringify(r) === JSON.stringify([0, 0, 0]), r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', bar, `async (el) => { await new Promise(r => setTimeout(r, 200)); return [el.getBoundingClientRect().height, el.shadowRoot.querySelector('nav').getBoundingClientRect().height]; }`);
check('top bar: its height is 48 (the frame\'s top dock)', r[0] === 48 && r[1] === 48, r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', bar, `async (el) => { await new Promise(r => setTimeout(r, 200)); return [el.getBoundingClientRect().width, el.parentElement.parentElement.getBoundingClientRect().width]; }`);
check('top bar: it spans the width of its component box', r[0] === r[1] && r[0] === 480, r);
r = await probeStore('cadre.ob.topbar', 'obc-top-bar', { ...bar, tall: true }, `async (el) => { await new Promise(r => setTimeout(r, 200)); return el.getBoundingClientRect().height; }`);
check('top bar: tall draws a taller bar', r > 48, r);

r = await probeStore('cadre.ob.systemmenu', 'obc-system-menu', { wifiState: sys.wifiState, audioState: sys.audioState },
  `async (el) => { el.shadowRoot.querySelector('button.title-container').click(); ${settle}
     const wrote = window.writes.slice(); window.h.rerender({ wifiState: ${JSON.stringify(sys.wifiState)}, audioState: ${JSON.stringify({ ...sys.audioState, volume: 41 })}, activeSubMenu: wrote[0][1] });
     ${settle} return [el.activeSubMenu, wrote]; }`);
check('system menu: the press of a heading writes the sub menu the element opened, so a later update keeps it open', r[0] === 'wifi' && JSON.stringify(r[1]) === JSON.stringify([['activeSubMenu', 'wifi']]), r);

// ---- batch F5: tabs, pivots, the modal window, the context menu input and the notification items
r = await probeStore('cadre.ob.tabitem', 'obc-tab-item', { hasTitle: true, title: 'Engine', hasLeadingIcon: true, leadingIconName: 'dashboard', hasBadge: true, badgeCount: 3, showLeadingBadgeIcon: true, badgeIconName: 'info' }, kids);
check('tab item: the leading icon and the badge icon are icons in their slots', r.sort().join() === 'obi-dashboard[leading-icon],obi-info[badge-icon]', r);
r = await probeStore('cadre.ob.tabitem', 'obc-tab-item', { hasTitle: true, title: 'Engine', subtitle: 'Pumps', showSubtitle: true, hasBadge: true, badgeCount: 7, badgeType: 'alarm' },
  `(el) => [el.shadowRoot.querySelector('.title').textContent.trim(), el.shadowRoot.querySelector('.subtitle').textContent.trim(), el.shadowRoot.querySelectorAll('obc-badge').length, el.shadowRoot.querySelector('obc-badge').number, el.shadowRoot.querySelector('obc-badge').type]`);
check('tab item: the title, subtitle and badge come from the attributes', JSON.stringify(r) === JSON.stringify(['Engine', 'Pumps', 1, 7, 'alarm']), r);
r = await probeStore('cadre.ob.tabitem', 'obc-tab-item', { hasTitle: true, title: 'Engine', hasClose: true },
  `async (el) => { el.shadowRoot.querySelector('[role=tab]').click(); el.shadowRoot.querySelector('.close-button').click(); ${settle} return window.fired; }`);
check('tab item: a press carries onTabClick and the close button onTabClose (not also a tab press), each with the title',
  JSON.stringify(r) === JSON.stringify([['onTabClick', { title: 'Engine' }], ['onTabClose', { title: 'Engine' }]]), r);
r = await probeStore('cadre.ob.tabitem', 'obc-tab-item', { hasTitle: true, title: 'Engine', disabled: true }, `async (el) => { el.shadowRoot.querySelector('[role=tab]').click(); ${settle} return window.fired; }`);
check('tab item: a disabled tab carries no press', r.length === 0, r);

const tabs = [{ id: 'a', title: 'Overview', iconName: 'dashboard' }, { id: 'b', title: 'Alarms', iconName: 'alarm', hasBadge: true, badgeCount: 3, badgeType: 'alarm' },
  { id: 'c', title: 'Trends', hasLeadingIcon: false }, { id: 'd', title: 'Reports', disabled: true }];
r = await probeStore('cadre.ob.tabrow', 'obc-tab-row', { tabs, selectedTabId: 'a' },
  `async (el) => { ${settle} const t = [...el.shadowRoot.querySelectorAll('obc-tab-item')];
     return [t.map(x => x.title + ':' + x.checked + ':' + x.hasLeadingIcon + ':' + x.disabled).join(), [...el.children].map(n => n.tagName.toLowerCase() + '[' + n.getAttribute('slot') + ']').join()]; }`);
check('tab row: one tab for each entry, the selected one checked; a tab\'s icon is an icon in its slot (none where the tab has no icon)',
  r[0] === 'Overview:true:true:false,Alarms:false:true:false,Trends:false:false:false,Reports:false:true:true' && r[1] === 'obi-dashboard[tab-a-icon],obi-alarm[tab-b-icon]', r);
r = await probeStore('cadre.ob.tabrow', 'obc-tab-row', { tabs, selectedTabId: 'a' },
  `async (el) => { const t = [...el.shadowRoot.querySelectorAll('obc-tab-item')]; t[1].shadowRoot.querySelector('[role=tab]').click(); ${settle}
     return [window.fired, window.writes, el.selectedTabId]; }`);
check('tab row: a press carries onTabSelected with the id, the position and the title, and writes the component\'s selectedTabId',
  JSON.stringify(r) === JSON.stringify([[['onTabSelected', { id: 'b', index: 1, title: 'Alarms' }]], [['selectedTabId', 'b']], 'b']), r);
r = await probeStore('cadre.ob.tabrow', 'obc-tab-row', { tabs, selectedTabId: 'b', hasClose: true },
  `async (el) => { const t = [...el.shadowRoot.querySelectorAll('obc-tab-item')]; t[1].shadowRoot.querySelector('.close-button').click(); ${settle}
     return [window.fired, window.writes, el.tabs.length]; }`);
check('tab row: a close press carries onTabClosed, the row drops the tab and the component\'s selectedTabId follows its choice',
  JSON.stringify(r) === JSON.stringify([[['onTabClosed', { id: 'b', index: 1, title: 'Alarms' }]], [['selectedTabId', 'c']], 3]), r);
r = await probeStore('cadre.ob.tabrow', 'obc-tab-row', { tabs, selectedTabId: 'a', hasAddNewTab: true },
  `async (el) => { el.shadowRoot.querySelector('.add-new-tab').click(); ${settle} return window.fired; }`);
check('tab row: the add button carries onAddNewTab with no detail', JSON.stringify(r) === JSON.stringify([['onAddNewTab', {}]]), r);
r = await probeStore('cadre.ob.tabrow', 'obc-tab-row', { tabs, selectedTabId: 'a' },
  `async (el) => { window.h.rerender({ tabs: ${JSON.stringify(tabs.slice(0, 2).map(t => ({ ...t, iconName: 'info' })))}, selectedTabId: 'b' }); ${settle}
     return [el.tabs.length, el.selectedTabId, [...el.children].map(n => n.tagName.toLowerCase() + '[' + n.getAttribute('slot') + ']').join()]; }`);
check('tab row: a later update replaces the tabs, the selection and the icons, which are not built twice',
  JSON.stringify(r) === JSON.stringify([2, 'b', 'obi-info[tab-a-icon],obi-info[tab-b-icon]']), r);
r = await probeStore('cadre.ob.tabrow', 'obc-tab-row', { tabs: [{ id: 'a', title: 'A', iconName: 'no-such-icon' }, { title: 'No id' }, 'x'] },
  '(el) => [el.tabs.map(t => t.id).join(), el.children.length]');
check('tab row: an entry with no id is dropped, and an icon name outside the bundled list draws no child', JSON.stringify(r) === JSON.stringify(['a', 0]), r);

r = await probeStore('cadre.ob.pivotitem', 'obc-pivot-item', { value: 'alarms', hasLabel: true, label: 'Alarms', hasLeadingIcon: true, iconName: 'alarm' }, kids);
check('pivot item: the icon is an icon in the icon slot', r.join() === 'obi-alarm[icon]', r);
r = await probeStore('cadre.ob.pivotitem', 'obc-pivot-item', { value: 'alarms', hasLabel: true, label: 'Alarms' },
  `async (el) => { el.shadowRoot.querySelector('button').click(); ${settle} return [window.fired, window.writes, el.selected]; }`);
check('pivot item: a press carries onSelected with the value and writes nothing (the item does not select itself)',
  JSON.stringify(r) === JSON.stringify([[['onSelected', { value: 'alarms' }]], [], false]), r);
r = await probeStore('cadre.ob.pivotitem', 'obc-pivot-item', { value: 'alarms', hasLabel: true, label: 'Alarms', selected: true },
  `async (el) => { el.shadowRoot.querySelector('button').click(); ${settle} return window.fired; }`);
check('pivot item: a selected item carries no press', r.length === 0, r);

const pivots = [{ tag: 'obc-pivot-item', id: 'pv-a', value: 'alarms', hasLabel: true, label: 'Alarms' }, { tag: 'obc-pivot-item', id: 'pv-t', value: 'trends', hasLabel: true, label: 'Trends', children: [{ tag: 'obi-info', slot: 'icon' }], hasLeadingIcon: true },
  { tag: 'obc-pivot-item', value: 'reports', hasLabel: true, label: 'Reports', disabled: true }];
r = await probeStore('cadre.ob.pivotitemgroup', 'obc-pivot-item-group', { items: pivots, selectedValue: 'trends' },
  `async (el) => { ${settle} return [[...el.children].map(n => n.tagName.toLowerCase() + ':' + n.value + ':' + n.selected + ':' + n.direction + ':' + n.children.length).join(), [...el.children].map(n => n.getAttribute('data-item-id') || '').join()]; }`);
check('pivot group: the items are pivots, the group marks the one it selects', r[0] === 'obc-pivot-item:alarms:false:horizontal:0,obc-pivot-item:trends:true:horizontal:1,obc-pivot-item:reports:false:horizontal:0' && r[1] === 'pv-a,pv-t,', r);
r = await probeStore('cadre.ob.pivotitemgroup', 'obc-pivot-item-group', { items: pivots, selectedValue: 'trends' },
  `async (el) => { el.children[0].shadowRoot.querySelector('button').click(); ${settle} return [window.fired, window.writes, el.selectedValue, [...el.children].map(n => n.selected).join()]; }`);
check('pivot group: a press carries onChange with the value, shows the selection and writes the component\'s selectedValue (the pivot\'s own event does not reach the host)',
  JSON.stringify(r) === JSON.stringify([[['onChange', { selectedValue: 'alarms' }]], [['selectedValue', 'alarms']], 'alarms', 'true,false,false']), r);
r = await probeStore('cadre.ob.pivotitemgroup', 'obc-pivot-item-group', { items: pivots, selectedValue: 'trends', allowDeselect: true },
  `async (el) => { el.children[1].shadowRoot.querySelector('button').click(); ${settle} return [window.fired, el.selectedValue]; }`);
check('pivot group: pressing the selected pivot carries nothing, even with allowDeselect (the pivot ignores a press while selected, in this release)', JSON.stringify(r) === JSON.stringify([[], 'trends']), r);
r = await probeStore('cadre.ob.pivotitemgroup', 'obc-pivot-item-group', { items: pivots.slice(0, 1), selectedValue: 'alarms' },
  `async (el) => { window.h.rerender({ items: ${JSON.stringify(pivots)}, selectedValue: 'trends', direction: 'vertical' }); ${settle}
     return [[...el.children].map(n => n.selected + ':' + n.direction).join(), el.children.length]; }`);
check('pivot group: a later update rebuilds the pivots, marks the selected one and gives them the direction', JSON.stringify(r) === JSON.stringify(['false:vertical,true:vertical,false:vertical', 3]), r);

r = await probeStore('cadre.ob.modalwindow', 'obc-modal-window', { title: 'Release command', content: 'Body text', optionLabel: 'Details', cancelLabel: 'Keep', doneLabel: 'Release', hasLeadingIcon: true, hasOptionalAction: true, leadingIconName: 'info' }, kids);
check('modal window: the title, content and the three labels are spans in their slots and the icon is in the leading icon slot',
  r.sort().join() === 'obi-info[leading-icon],span[cancel-label],span[content],span[done-label],span[option-label],span[title]', r);
r = await probeStore('cadre.ob.modalwindow', 'obc-modal-window', {}, kids);
check('modal window: with no text the element keeps its own words (Title, Cancel, Done) and draws no child', r.length === 0, r);
r = await probeStore('cadre.ob.modalwindow', 'obc-modal-window', { title: 'T', hasOptionalAction: true },
  `async (el) => { const b = [...el.shadowRoot.querySelectorAll('obc-button, obc-icon-button')]; b.forEach(x => x.click()); ${settle} return [b.length, window.fired]; }`);
check('modal window: the close, option, cancel and done buttons carry their four events, with no detail',
  r[0] === 4 && JSON.stringify(r[1].map(x => x[0]).sort()) === JSON.stringify(['onCancelClick', 'onCloseClick', 'onDoneClick', 'onOptionClick']) && r[1].every(x => Object.keys(x[1]).length === 0), r);
r = await probeStore('cadre.ob.modalwindow', 'obc-modal-window', { title: 'T', hasCancelAction: false, hasCloseAction: false },
  `(el) => [el.shadowRoot.querySelectorAll('obc-button').length, el.shadowRoot.querySelectorAll('obc-icon-button').length, el.hasCancelAction, el.hasCloseAction]`);
check('modal window: hasCancelAction and hasCloseAction false leave the Cancel and close buttons out', JSON.stringify(r) === JSON.stringify([1, 0, false, false]), r);
r = await probeStore('cadre.ob.modalwindow', 'obc-modal-window', { title: 'T' }, `async (el) => { ${settle} const b = el.getBoundingClientRect(); return [b.width, b.height]; }`);
check('modal window: a plain block of its own width (540, large) that draws no overlay', r[0] === 540 && r[1] > 100 && r[1] < 300, r);

const opts = [{ value: 'a', label: 'Alpha' }, { value: 'b', label: 'Beta' }, { value: 'c', label: 'Gamma' }];
r = await probeStore('cadre.ob.contextmenuinput', 'obc-context-menu-input', { options: opts, selectedValues: ['b'] },
  '(el) => [[...el.shadowRoot.querySelectorAll("[data-menu-item]")].map(x => x.getAttribute("data-menu-value") + ":" + x.getAttribute("aria-selected")).join(), el.multiSelect === undefined, el.selectPerGroup === undefined, el.options.length, el.selectedValues.join()]');
check('context menu: one row for each option, the selected one marked; multiSelect and selectPerGroup stay undefined (the element decides from type)',
  r[0] === 'a:false,b:true,c:false' && r[1] === true && r[2] === true && r[3] === 3 && r[4] === 'b', r);
r = await probeStore('cadre.ob.contextmenuinput', 'obc-context-menu-input', { options: opts, selectedValues: ['b'] },
  `async (el) => { el.shadowRoot.querySelector('[data-menu-value=a]').click(); ${settle} return [window.fired, window.writes, el.selectedValues]; }`);
check('context menu: a press carries onItemClick with the value and label, then onChange with the selection, and writes the component\'s selectedValues',
  JSON.stringify(r) === JSON.stringify([[['onItemClick', { value: 'a', label: 'Alpha' }], ['onChange', { selectedValues: ['a'] }]], [['selectedValues', ['a']]], ['a']]), r);
r = await probeStore('cadre.ob.contextmenuinput', 'obc-context-menu-input', { type: 'checkboxes', options: opts, selectedValues: ['b'] },
  `async (el) => { const c = [...el.shadowRoot.querySelectorAll('obc-checkbox-item')]; c[0].dispatchEvent(new CustomEvent('change', { detail: { status: 'checked' } }));
     c[2].dispatchEvent(new CustomEvent('change', { detail: { status: 'checked' } })); ${settle} return [window.fired, window.writes.map(w => w[1].join()), el.selectedValues]; }`);
check('context menu: the checkbox type selects several, each change carries onChange with the whole selection and writes it',
  JSON.stringify(r) === JSON.stringify([[['onChange', { selectedValues: ['b', 'a'] }], ['onChange', { selectedValues: ['b', 'a', 'c'] }]], ['b,a', 'b,a,c'], ['b', 'a', 'c']]), r);
r = await probeStore('cadre.ob.contextmenuinput', 'obc-context-menu-input', { options: opts, hasTitleBar: true, title: 'Show' },
  `async (el) => { el.shadowRoot.querySelector('.title-container obc-icon-button').click(); el.shadowRoot.querySelector('[role=menu]').dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); ${settle}
     return [el.shadowRoot.querySelector('.title-text').textContent.trim(), window.fired]; }`);
check('context menu: the title bar shows the title, and its close button and the Escape key carry onClose with no detail',
  r[0] === 'Show' && JSON.stringify(r[1]) === JSON.stringify([['onClose', {}], ['onClose', {}]]), r);
const groups = [{ title: 'Show', columns: 1, options: [opts[0], opts[1]] }, { title: 'Areas', columns: 1, options: [opts[2]] }];
r = await probeStore('cadre.ob.contextmenuinput', 'obc-context-menu-input', { type: 'multi-with-subtitles', columnGroups: groups, selectedValues: ['a', 'c'] },
  '(el) => [el.columnGroups.length, el.columnGroups[0].options.length, [...el.shadowRoot.querySelectorAll("[data-menu-value]")].map(x => x.getAttribute("data-menu-value")).join(), el.shadowRoot.innerHTML.indexOf("Areas") >= 0]');
check('context menu: the column groups draw their titles and options', JSON.stringify(r) === JSON.stringify([2, 2, 'a,b,c', true]), r);
r = await probeStore('cadre.ob.contextmenuinput', 'obc-context-menu-input', { options: [{ value: 'x', label: 'X', icon: 'no', children: [{ value: 'y', label: 'Y', level: 1 }] }, 'bad'], multiSelect: true },
  '(el) => [el.options.length, JSON.stringify(el.options[0]), el.multiSelect]');
check('context menu: an option carries value, label, level and children only (no icon), and multiSelect true reaches the element',
  JSON.stringify(r) === JSON.stringify([1, '{"value":"x","label":"X","children":[{"value":"y","label":"Y","level":1}]}', true]), r);

r = await probeStore('cadre.ob.notificationmenuitem', 'obc-notification-menu-item', { title: 'Pump stopped', description: 'By the operator', day: 'Today', time: '09:41', hasIcon: true, iconName: 'info', open: true, primaryActionLabel: 'View', secondaryActionLabel: 'Dismiss' },
  `async (el) => { ${settle} const m = el.shadowRoot.querySelector('obc-message-menu-item'); return [[...el.children].map(n => n.tagName.toLowerCase() + '[' + n.getAttribute('slot') + ']').join(), m.title, m.day, m.time, m.primaryActionLabel, m.open]; }`);
check('notification menu item: the texts reach the row it draws, the icon is an icon in the icon slot', JSON.stringify(r) === JSON.stringify(['obi-info[icon]', 'Pump stopped', 'Today', '09:41', 'View', true]), r);
r = await probeStore('cadre.ob.notificationmenuitem', 'obc-notification-menu-item', { title: 'Pump stopped' },
  `async (el) => { const m = el.shadowRoot.querySelector('obc-message-menu-item'); m.dispatchEvent(new CustomEvent('message-click', { detail: { open: true }, bubbles: true, composed: true })); ${settle} return [window.fired, window.writes, el.open]; }`);
check('notification menu item: a press carries onItemClick with the state after the press and writes the component\'s open',
  JSON.stringify(r) === JSON.stringify([[['onItemClick', { open: true }]], [['open', true]], true]), r);
r = await probeStore('cadre.ob.notificationmenuitem', 'obc-notification-menu-item', { title: 'Pump stopped', open: true, primaryActionLabel: 'View', secondaryActionLabel: 'Dismiss' },
  `async (el) => { ${settle} const m = el.shadowRoot.querySelector('obc-message-menu-item'); await m.updateComplete; const b = [...m.shadowRoot.querySelectorAll('obc-button')]; b.forEach(x => x.click()); ${settle} return [b.length, window.fired]; }`);
check('notification menu item: the two actions carry onPrimaryActionClick and onSecondaryActionClick with no detail',
  r[0] === 2 && JSON.stringify(r[1].map(x => x[0]).sort()) === JSON.stringify(['onPrimaryActionClick', 'onSecondaryActionClick']) && r[1].every(x => Object.keys(x[1]).length === 0), r);
r = await probeStore('cadre.ob.notificationmenuitem', 'obc-notification-menu-item', { title: 'Pump stopped' }, `async (el) => { ${settle} return [el.getBoundingClientRect().width, el.parentElement.parentElement.getBoundingClientRect().width]; }`);
check('notification menu item: it fills the width of its component box', r[0] === r[1] && r[0] === 480, r);

r = await probeStore('cadre.ob.notificationmessageitem', 'obc-notification-message-item', { title: 'Pump stopped', description: 'By the operator', time: '09:41', type: 'with-button', actionLabel: 'View', hasSecondaryIcon: true, secondaryIconName: 'info' },
  `async (el) => { ${settle} const t = el.shadowRoot.querySelector('obc-topbar-message-item'); return [[...el.children].map(n => n.tagName.toLowerCase() + '[' + n.getAttribute('slot') + ']').join(), [...t.children].map(n => n.getAttribute('slot') + ':' + n.textContent.trim()).filter(x => /^(title|description|time|action-text):/.test(x)).join()]; }`);
check('notification message item: the texts reach the row it draws, the icon is an icon in the secondary icon slot',
  r[0] === 'obi-info[secondary-icon]' && r[1] === 'title:Pump stopped,description:By the operator,time:09:41,action-text:View', r);
r = await probeStore('cadre.ob.notificationmessageitem', 'obc-notification-message-item', { title: 'Pump stopped', type: 'with-button', showTitle: false, showTimestamp: false, time: '09:41' },
  `async (el) => { ${settle} const t = el.shadowRoot.querySelector('obc-topbar-message-item'); return [[...t.children].filter(n => n.getAttribute('slot') === 'title' || n.getAttribute('slot') === 'time').length, el.showTitle, el.showTimestamp, el.showDescription]; }`);
check('notification message item: showTitle and showTimestamp false leave the title and the time out', JSON.stringify(r) === JSON.stringify([0, false, false, true]), r);
r = await probeStore('cadre.ob.notificationmessageitem', 'obc-notification-message-item', { title: 'Pump stopped', type: 'with-button', actionLabel: 'View' },
  `async (el) => { ${settle} const t = el.shadowRoot.querySelector('obc-topbar-message-item'); await t.updateComplete; t.dispatchEvent(new CustomEvent('message-click')); t.dispatchEvent(new CustomEvent('action-click')); ${settle} return window.fired; }`);
check('notification message item: a press carries onMessageClick and the action carries onActionClick, with no detail, once each',
  JSON.stringify(r) === JSON.stringify([['onMessageClick', {}], ['onActionClick', {}]]), r);
r = await probeStore('cadre.ob.notificationmessageitem', 'obc-notification-message-item', { empty: true, emptyText: 'Nothing to show' },
  `async (el) => { ${settle} const t = el.shadowRoot.querySelector('obc-topbar-message-item'); return [t.type, [...t.children].filter(n => n.getAttribute('slot') === 'empty').map(n => n.textContent).join()]; }`);
check('notification message item: empty draws the inactive row with the empty text', JSON.stringify(r) === JSON.stringify(['inactive', 'Nothing to show']), r);
r = await probeStore('cadre.ob.notificationmessageitem', 'obc-notification-message-item', { title: 'T' }, `async (el) => { ${settle} const b = el.getBoundingClientRect(); return [b.width, b.height]; }`);
check('notification message item: 640 wide and 48 high in the regular size', JSON.stringify(r) === JSON.stringify([640, 48]), r);

r = await probeStore('cadre.ob.notificationfloatingitem', 'obc-notification-floating-item', { type: 'application', title: 'Pump stopped', description: 'By the operator', time: '09:41', day: 'Today', hasTimestamp: true, hasDay: true, action: true, actionLabel: 'View', action2: true, action2Label: 'Dismiss', primaryIconName: 'info' }, kids);
check('notification floating item: the five texts and the two labels are spans in their slots and the primary icon is an icon',
  r.sort().join() === 'obi-info[primary-icon],span[action2],span[action],span[day],span[description],span[time],span[title]'.split(',').sort().join(), r);
r = await probeStore('cadre.ob.notificationfloatingitem', 'obc-notification-floating-item', { title: 'Pump stopped', action: true, actionLabel: 'View', action2: true, action2Label: 'Dismiss' },
  `async (el) => { ${settle} const f = el.shadowRoot.querySelector('obc-floating-item'); await f.updateComplete; const b = [...f.shadowRoot.querySelectorAll('obc-button, obc-icon-button')]; b.forEach(x => x.click()); ${settle} return [b.length, window.fired]; }`);
check('notification floating item: the two actions and the dismiss button carry their three events with no detail',
  r[0] >= 3 && JSON.stringify(r[1].map(x => x[0]).sort()) === JSON.stringify(['onAction2Click', 'onActionClick', 'onDismissClick']) && r[1].every(x => Object.keys(x[1]).length === 0), r);
r = await probeStore('cadre.ob.notificationfloatingitem', 'obc-notification-floating-item', { title: 'T', direction: 'vertical', lineType: 'multi-line' }, '(el) => [el.direction, el.lineType, el.type]');
check('notification floating item: the enumerations reach the element', JSON.stringify(r) === JSON.stringify(['vertical', 'multi-line', 'regular']), r);
r = await probeStore('cadre.ob.notificationfloatingitem', 'obc-notification-floating-item', { title: 'T' }, `async (el) => { ${settle} const b = el.getBoundingClientRect(); return [b.width, b.height]; }`);
check('notification floating item: 640 wide and 73 high with a title alone', JSON.stringify(r) === JSON.stringify([640, 73]), r);

const unexpected = errors.filter(e => !e.includes('item tag not allowed here: obc-notanitem') && !e.includes('item tag not allowed here: obc-navigation-item') && !e.includes('obc-app-button has no item attribute bogus'));      // provoked above
check('no console error or warning', unexpected.length === 0, unexpected);
for (const [s, n, d] of results) console.log(s, n, d);
await browser.close();
process.exit(results.some(r => r[0] === 'FAIL') ? 1 : 0);
