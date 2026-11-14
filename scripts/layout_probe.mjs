// After swapping the Latin face: does anything overflow, clip, or fall back?
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes(process.argv[2] || '8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const failed = [];
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); return; }
    if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) {
      failed.push(m.params.response.status + ' ' + m.params.response.url.split('/').pop());
    }
  };
  await new Promise(r => ws.onopen = r);
  await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.reload', { ignoreCache: true });
  await new Promise(r => setTimeout(r, 4500));

  const expr = `(async () => {
    await document.fonts.ready;
    const cs = getComputedStyle(document.body);
    const bad = [];
    document.querySelectorAll('h1,h2,h3,p,a,button,span,li,td').forEach(e => {
      if (e.scrollWidth > e.clientWidth + 2 && e.clientWidth > 0 && getComputedStyle(e).overflow !== 'auto') {
        const t = (e.textContent || '').trim().slice(0, 28);
        if (t) bad.push({ tag: e.tagName, cls: String(e.className).slice(0, 24), by: e.scrollWidth - e.clientWidth, t });
      }
    });
    return {
      bodyFont: cs.fontFamily.split(',')[0],
      figtreeLoaded: document.fonts.check('400 16px Figtree'),
      pageOverflow: document.documentElement.scrollWidth - innerWidth,
      clipped: bad.slice(0, 8),
      clippedCount: bad.length,
      docHeight: document.documentElement.scrollHeight
    };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  console.log(JSON.stringify(r.result.value));
  console.log('failed requests:', JSON.stringify(failed.slice(0, 6)));
  ws.close();
})();
