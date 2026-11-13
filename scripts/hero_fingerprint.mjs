// Hero geometry fingerprint: proves (or disproves) that a CSS change moved nothing.
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
    const pick = ['#home', 'h1', '.hero-emblem', '#appleMacosDockWrapper', '.sr-tools-capsule',
                  '.section-trust-metrics', '#services', '.founder-editorial-card'];
    const out = {};
    for (const s of pick) {
      const e = document.querySelector(s);
      out[s] = e ? (r => ({ y: Math.round(r.top + scrollY), h: Math.round(r.height), w: Math.round(r.width) }))(e.getBoundingClientRect()) : null;
    }
    out.doc = document.documentElement.scrollHeight;
    return out;
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value));
  ws.close();
})();
