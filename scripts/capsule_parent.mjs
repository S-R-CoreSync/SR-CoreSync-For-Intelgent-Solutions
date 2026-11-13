// Which box is the capsule fixed against, and what makes it a containing block?
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
    const e = document.querySelector('.sr-tools-capsule');
    if (!e) return { missing: true };
    const chain = []; let n = e.parentElement;
    while (n && n !== document.documentElement) {
      const c = getComputedStyle(n), r = n.getBoundingClientRect();
      if (c.transform !== 'none' || c.filter !== 'none' || c.perspective !== 'none' ||
          c.contain !== 'none' || c.willChange !== 'auto' || c.position === 'fixed' || c.contentVisibility === 'auto') {
        chain.push({ tag: n.tagName, id: n.id, cls: String(n.className).slice(0, 44), pos: c.position,
                     transform: c.transform, contain: c.contain, filter: c.filter,
                     x: Math.round(r.left), w: Math.round(r.width) });
      }
      n = n.parentElement;
    }
    const r = e.getBoundingClientRect(), c = getComputedStyle(e);
    return { box: { x: Math.round(r.left), w: Math.round(r.width) }, cssLeft: c.left, position: c.position,
             offsetParent: e.offsetParent ? e.offsetParent.tagName + '#' + e.offsetParent.id : null,
             chain };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
