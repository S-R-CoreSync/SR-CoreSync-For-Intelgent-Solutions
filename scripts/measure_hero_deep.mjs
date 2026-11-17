// Deep hero diagnosis: heights of every hero child block, root vs portals,
// at two viewports. Connect-only (browser on 9333, site on 8150).
const PAGES = ['index.html', 'en/index.html', 'de/index.html', 'ckb/index.html'];
const VIEWPORTS = [[1600, 900], [1920, 1080]];
(async () => {
  const list = await (await fetch('http://127.0.0.1:9333/json/list')).json();
  const page = list.find(t => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);

  for (const [w, h] of VIEWPORTS) {
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
    for (const p of PAGES) {
      await send('Page.navigate', { url: `http://127.0.0.1:8150/${p}` });
      await new Promise(r => setTimeout(r, 2200));
      const expr = `(() => {
        const hero = document.querySelector('section#hero'); if (!hero) return { page: ${JSON.stringify(p)}, err: 'no hero' };
        const R = e => { const r = e.getBoundingClientRect(); return Math.round(r.height); };
        const kids = [...hero.children].map(c => ({
            tag: c.tagName.toLowerCase() + (c.id ? '#' + c.id : '') + '.' + (c.className || '').toString().slice(0, 40),
            h: R(c), visible: !!(c.offsetParent || c.getClientRects().length) }));
        const hv2 = hero.querySelector('#hv2-hero');
        const hv2kids = hv2 ? [...hv2.querySelectorAll(':scope > * > *')].slice(0, 8).map(c =>
            (c.className || c.tagName).toString().slice(0, 46) + '=' + R(c)) : [];
        const cs = hero.querySelector('.c3-center-stage');
        const csKids = cs ? [...cs.children].map(c => (c.className || c.tagName).toString().slice(0, 44) + '=' + R(c)) : [];
        return { page: ${JSON.stringify(p)}, vw: innerWidth, hero: R(hero), hv2: hv2 ? R(hv2) : null,
                 cockpit: R(hero.querySelector('.concept-3-cockpit') || hero),
                 kids, hv2kids, csKids };
      })()`;
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
      console.log(JSON.stringify(r.result.value));
    }
  }
  ws.close();
  process.exit(0);
})().catch(e => { console.error('CATCH', e.message); process.exit(1); });
