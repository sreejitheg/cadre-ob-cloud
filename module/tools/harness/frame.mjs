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

const unexpected = errors.filter(e => !e.includes('item tag not allowed here: obc-notanitem') && !e.includes('item tag not allowed here: obc-navigation-item'));      // provoked above
check('no console error or warning', unexpected.length === 0, unexpected);
for (const [s, n, d] of results) console.log(s, n, d);
await browser.close();
process.exit(results.some(r => r[0] === 'FAIL') ? 1 : 0);
