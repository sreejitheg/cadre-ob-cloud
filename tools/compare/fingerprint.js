// Structural fingerprint of a Perspective diagram page, run in the page (browser devtools,
// the Claude browser tool's javascript_exec, or Playwright's page.evaluate).
//
// Returns {n, rows: [[index, centreX, centreY, width, height, text], ...]} for every symbol of
// the diagram, in diagram child order, with readout text read through shadow roots. It works on
// both renderings compared:
//   * the reference demo: components `automation.*` inside `openbridge.manual.connector-diagram`,
//     whose child index is in the component path (`C.0:<i>` or `C$0:<i>.`);
//   * the Cadre build: embedded views inside the `Diagram` coordinate container, whose 48 px
//     `Symbol` box carries the symbol centre.
// Read only: it changes nothing on the page.
(() => {
  const deep = (n) => {
    let t = '';
    const walk = (x) => {
      if (x.nodeType === 3) { t += x.textContent + ' '; return; }
      if (x.shadowRoot) walk(x.shadowRoot);
      if (x.childNodes) x.childNodes.forEach(walk);
    };
    walk(n);
    return t.replace(/\s+/g, ' ').trim();
  };
  const rows = [];
  // Card pages: one row per card, [index, centreX, centreY, width, height, text of the card].
  const vendorCards = [...document.querySelectorAll('[data-component="openbridge.manual.card"]')];
  const ourCards = [...document.querySelectorAll('[data-component="ia.container.flex"]')]
    .filter((e) => e.className.toString().includes('psc-cadre/surface/card') && e.getAttribute('data-component-path').startsWith('C'));
  const cards = vendorCards.length ? vendorCards : ourCards;
  const isDiagram = !!document.querySelector('[data-component="openbridge.manual.connector-diagram"]')
    || [...document.querySelectorAll('[data-component="ia.container.coord"]')]
      .some((e) => e.getBoundingClientRect().width > 1000);
  if (cards.length && !isDiagram) {
    cards.forEach((e, i) => {
      const r = e.getBoundingClientRect();
      rows.push([i, Math.round(r.x + r.width / 2), Math.round(r.y + r.height / 2),
                 Math.round(r.width), Math.round(r.height), deep(e).slice(0, 200)]);
    });
    return JSON.stringify({ n: rows.length, kind: 'cards', url: location.href, viewport: [innerWidth, innerHeight], rows });
  }
  const vendor = document.querySelectorAll('[data-component^="automation."]');
  if (vendor.length && document.querySelector('[data-component="openbridge.manual.connector-diagram"]')) {
    vendor.forEach((e) => {
      const m = e.getAttribute('data-component-path').match(/^C\$0:(\d+)\.|^C\.0:(\d+)$/);
      if (!m) return;
      const r = e.getBoundingClientRect();
      rows.push([+(m[1] || m[2]), Math.round(r.x + r.width / 2), Math.round(r.y + r.height / 2),
                 Math.round(r.width), Math.round(r.height), deep(e).slice(0, 60)]);
    });
  } else {
    const diag = [...document.querySelectorAll('[data-component="ia.container.coord"]')]
      .find((e) => e.getBoundingClientRect().width > 1000);
    const kids = [...diag.children].filter((e) => e.hasAttribute('data-component'));
    const off = kids.findIndex((e) => e.getAttribute('data-component') === 'ia.display.view');
    kids.slice(off).forEach((e, i) => {
      const sym = [...e.querySelectorAll('[data-component="ia.container.coord"]')]
        .find((s) => Math.round(s.getBoundingClientRect().width) === 48);
      const r = (sym || e).getBoundingClientRect();
      const text = [...e.querySelectorAll('[data-component="ia.display.label"]')]
        .filter((l) => getComputedStyle(l).visibility !== 'hidden' && l.offsetParent !== null)
        .map((l) => l.innerText.trim()).filter(Boolean).join(' ');
      rows.push([i, Math.round(r.x + r.width / 2), Math.round(r.y + r.height / 2),
                 Math.round(r.width), Math.round(r.height), text.slice(0, 60)]);
    });
  }
  rows.sort((a, b) => a[0] - b[0]);
  return JSON.stringify({ n: rows.length, url: location.href, viewport: [innerWidth, innerHeight], rows });
})();
