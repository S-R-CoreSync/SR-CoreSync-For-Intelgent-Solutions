// What is inside the tools capsule, and how tall is each part?
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
  await new Promise(r => setTimeout(r, 900));
  const expr = `(() => {
    const cap = document.querySelector('.sr-tools-capsule');
    const box = e => { const r = e.getBoundingClientRect(); const c = getComputedStyle(e);
      return { tag: e.tagName, cls: String(e.className).slice(0, 34), h: Math.round(r.height), w: Math.round(r.width),
               pad: c.padding, fs: c.fontSize, lh: c.lineHeight, box: c.boxSizing, mt: c.marginTop, mb: c.marginBottom }; };
    return { capsule: box(cap), kids: [...cap.children].map(box),
             inner: [...cap.querySelectorAll('a,button')].slice(0, 4).map(box) };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
