// Measure the bottom row exactly, at a chosen viewport, through Chrome DevTools.
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  if (!page) { console.log('no page'); process.exit(1); }
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (method, params) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);

  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 1200));

  const expr = `(() => {
    const g = s => { const e = document.querySelector(s); if (!e) return null;
      const r = e.getBoundingClientRect(), c = getComputedStyle(e);
      return { top: Math.round(r.top), bottom: Math.round(r.bottom), h: Math.round(r.height), w: Math.round(r.width),
               left: Math.round(r.left), right: Math.round(r.right), cy: Math.round(r.top + r.height / 2),
               pos: c.position, mb: c.marginBottom, mt: c.marginTop, pb: c.paddingBottom, pt: c.paddingTop, b: c.bottom,
               ff: c.fontFamily.split(',')[0], fs: c.fontSize }; };
    return { vw: innerWidth,
      section: g('.section-trust-metrics'), strip: g('.hero-trust-metrics-strip'),
      val: g('.metric-val'), lbl: g('.metric-lbl'),
      dock: g('#appleMacosDockWrapper'), dockInner: g('#appleMacosDock'), tools: g('.sr-tools-capsule'),
      vars: { privacy: getComputedStyle(document.body).getPropertyValue('--privacy-h'), consent: getComputedStyle(document.body).getPropertyValue('--consent-h') } };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
