// Horizontal geometry of the three bottom blocks, and which rule sets the capsule's x.
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);
  await send('Emulation.setDeviceMetricsOverride', { width: Number(process.argv[2] || 1600), height: Number(process.argv[3] || 900), deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 900));
  const expr = `(() => {
    const box = s => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); const c = getComputedStyle(e);
      return { x: Math.round(r.left), right: Math.round(innerWidth - r.right), w: Math.round(r.width),
               left: c.left, rightCss: c.right, inset: c.insetInlineStart, marginLeft: c.marginLeft, transform: c.transform, position: c.position }; };
    return { vw: innerWidth, tools: box('.sr-tools-capsule'), dock: box('#appleMacosDockWrapper'), metrics: box('.section-trust-metrics') };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
