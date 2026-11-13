// Why is the dock 40px above the capsule, when both use the same calc?
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
    const info = s => { const e = document.querySelector(s); if (!e) return null; const c = getComputedStyle(e); const r = e.getBoundingClientRect();
      let anc = e.parentElement, inHome = false;
      while (anc) { if (anc.id === 'home') { inHome = true; break; } anc = anc.parentElement; }
      return { y: Math.round(r.top), bottom: Math.round(innerHeight - r.bottom), cssBottom: c.bottom, inHome,
               marginBottom: c.marginBottom, paddingBottom: c.paddingBottom, transform: c.transform }; };
    return { tools: info('.sr-tools-capsule'), dock: info('#appleMacosDockWrapper'), metrics: info('.section-trust-metrics'),
             vars: { privacy: getComputedStyle(document.body).getPropertyValue('--privacy-h'),
                     consent: getComputedStyle(document.body).getPropertyValue('--consent-h') },
             innerH: innerHeight };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
