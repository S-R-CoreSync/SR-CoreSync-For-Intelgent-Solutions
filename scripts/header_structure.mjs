// What is the header made of, and in which order does it flow?
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
  await new Promise(r => setTimeout(r, 1200));

  const expr = `(() => {
    const h = document.querySelector('header.site-header') || document.querySelector('.tf-header') || document.querySelector('header');
    if (!h) return { missing: true };
    const kids = [...h.children].map(e => {
      const r = e.getBoundingClientRect(); const c = getComputedStyle(e);
      return { tag: e.tagName, cls: String(e.className).slice(0, 46), x: Math.round(r.left), w: Math.round(r.width),
               order: c.order, flex: c.flex, display: c.display, dir: c.direction };
    });
    const c = getComputedStyle(h);
    const brand = h.querySelector('.brand, .logo, [class*="logo"]');
    const nav = h.querySelector('nav');
    const br = brand && brand.getBoundingClientRect(), nr = nav && nav.getBoundingClientRect();
    return { hdr: { cls: String(h.className).slice(0, 50), display: c.display, dir: c.direction, justify: c.justifyContent, gap: c.gap, h: Math.round(h.getBoundingClientRect().height) },
             brand: br ? { x: Math.round(br.left), w: Math.round(br.width), cls: String(brand.className).slice(0, 40) } : null,
             nav: nr ? { x: Math.round(nr.left), w: Math.round(nr.width) } : null,
             kids };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
