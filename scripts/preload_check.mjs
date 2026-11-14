// Do the preloaded fonts arrive, and does the text paint with them?
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const fonts = [];
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); return; }
    if (m.method === 'Network.responseReceived' && /\.woff2/.test(m.params.response.url)) {
      fonts.push({ file: m.params.response.url.split('/').pop().slice(0, 18), status: m.params.response.status, fromDisk: m.params.response.fromDiskCache });
    }
  };
  await new Promise(r => ws.onopen = r);
  await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.reload', { ignoreCache: true });
  await new Promise(r => setTimeout(r, 3500));

  const probe = `(async () => { await document.fonts.ready; return {
      alexandria: document.fonts.check('400 16px Alexandria'),
      figtree: document.fonts.check('400 16px Figtree'),
      bodyFont: getComputedStyle(document.body).fontFamily.split(',')[0].replace(/"/g,''),
      preloadTags: document.querySelectorAll('link[rel="preload"][as="font"]').length
    }; })()`;
  const r = await send('Runtime.evaluate', { expression: probe, returnByValue: true, awaitPromise: true });
  console.log('page:', JSON.stringify(r.result.value));
  console.log('font requests:', JSON.stringify(fonts));
  ws.close();
})();
