// Why does a fixed element land at the document bottom? Walk the ancestors.
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
  await new Promise(r => setTimeout(r, 1000));

  const expr = `(() => {
    const all = [...document.querySelectorAll('.section-trust-metrics')];
    const e = all[0];
    const chain = [];
    let n = e;
    while (n && n !== document.documentElement) {
      const c = getComputedStyle(n);
      if (c.position !== 'static' || c.transform !== 'none' || c.contain !== 'none' || c.filter !== 'none' || c.willChange !== 'auto' || c.overflow !== 'visible') {
        chain.push({ tag: n.tagName, id: n.id, cls: String(n.className).slice(0, 40), pos: c.position, transform: c.transform, contain: c.contain, overflow: c.overflow, h: Math.round(n.getBoundingClientRect().height) });
      }
      n = n.parentElement;
    }
    return { count: all.length, chain, docH: document.documentElement.scrollHeight, scrollY: scrollY, innerH: innerHeight };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
