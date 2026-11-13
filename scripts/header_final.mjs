// Final header geometry: brand, nav box, menu, and the gap between them.
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 1500));
  const expr = `(() => {
    const h = document.querySelector('header.tf-header');
    const g = s => { const e = h.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect();
      return [Math.round(r.left), Math.round(r.right), Math.round(r.width)]; };
    const box = h.querySelector('.box-navigation');
    return { vw: innerWidth, brand: g('.header-col-brand'), navCol: g('.header-col-nav'),
             menu: g('.nav-menu-main'), box: g('.box-navigation'),
             justify: box ? getComputedStyle(box).justifyContent : null,
             brandOrder: h.querySelector('.header-col-brand') ? getComputedStyle(h.querySelector('.header-col-brand')).order : null };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value));
  ws.close();
})();
