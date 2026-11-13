// Is the capsule positioned by an inline style (JS)?
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
    const all = [...document.querySelectorAll('.sr-tools-capsule')];
    return all.map(e => { const r = e.getBoundingClientRect(); const c = getComputedStyle(e);
      return { styleAttr: e.getAttribute('style'), cls: String(e.className), x: Math.round(r.left), w: Math.round(r.width),
               left: c.left, right: c.right, position: c.position, parent: e.parentElement.tagName + '.' + String(e.parentElement.className).slice(0, 30) }; });
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
