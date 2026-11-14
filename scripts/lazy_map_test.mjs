// Does the map still open, and does the page still avoid loading it up front?
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const reqs = [];
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); return; }
    if (m.method === 'Network.responseReceived') {
      const u = m.params.response.url;
      if (u.includes('sr-lang-map')) { reqs.push(u.split('/').pop()); }
    }
  };
  await new Promise(r => ws.onopen = r);
  await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.reload', { ignoreCache: true });
  await new Promise(r => setTimeout(r, 4000));

  const before = await send('Runtime.evaluate', { expression: `({ mapLoaded: !!window.SRLangMap, requests: ${JSON.stringify(reqs)} })`, returnByValue: true });
  console.log('after load:', JSON.stringify(before.result.value));

  // click the launchpad trigger the way a visitor would
  await send('Runtime.evaluate', { expression: `(() => {
    const btn = document.getElementById('appleDockLaunchpadBtn') || document.querySelector('#appleMacosDockWrapper .apple-dock-launchpad-btn');
    if (!btn) return 'no button';
    btn.click(); return 'clicked';
  })()`, returnByValue: true }).then(r => console.log('trigger:', JSON.stringify(r.result.value)));

  await new Promise(r => setTimeout(r, 2500));
  const after = await send('Runtime.evaluate', { expression: `(() => ({
      mapLoaded: !!window.SRLangMap,
      isOpen: !!(window.SRLangMap && window.SRLangMap.isOpen && window.SRLangMap.isOpen()),
      host: !!document.getElementById('srLangMapHost'),
      requests: ${JSON.stringify(reqs)}
    }))()`, returnByValue: true });
  console.log('after click:', JSON.stringify(after.result.value));
  ws.close();
})();
