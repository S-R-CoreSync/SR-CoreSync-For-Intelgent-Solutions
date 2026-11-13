// Which hosts does the page talk to, which fonts actually loaded, and what does it look like?
const port = 9333;
const fs = await import('node:fs');
const [shot] = process.argv.slice(2);
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  const hosts = new Set();
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); return; }
    if (m.method === 'Network.requestWillBeSent') {
      try { hosts.add(new URL(m.params.request.url).host); } catch (e) {}
    }
  };
  await new Promise(r => ws.onopen = r);
  await send('Network.enable');
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.reload', { ignoreCache: true });
  await new Promise(r => setTimeout(r, 4500));

  const probe = `(async () => {
    await document.fonts.ready;
    const fam = getComputedStyle(document.querySelector('h1')).fontFamily;
    return {
      h1Font: fam,
      alexandria: document.fonts.check('500 16px Alexandria'),
      jakarta: document.fonts.check('500 16px "Plus Jakarta Sans"'),
      loadedCount: document.fonts.size,
      faces: [...document.fonts].slice(0, 4).map(f => f.family + ' ' + f.weight + ' ' + f.status)
    };
  })()`;
  const r = await send('Runtime.evaluate', { expression: probe, returnByValue: true, awaitPromise: true });
  console.log('fonts', JSON.stringify(r.result.value));
  console.log('hosts', JSON.stringify([...hosts].sort()));

  await send('Runtime.evaluate', { expression: `(() => {
    document.documentElement.style.setProperty('--privacy-h','0px');
    document.documentElement.style.setProperty('--consent-h','0px');
    document.body.style.setProperty('--privacy-h','0px');
    document.body.style.setProperty('--consent-h','0px');
    const st=document.createElement('style');
    st.textContent='.sr-privacy-banner-wrap,.cc-banner,#cookieConsent{display:none!important}';
    document.head.appendChild(st); return true; })()`, returnByValue: true });
  await new Promise(r => setTimeout(r, 400));

  const s = await send('Page.captureScreenshot', { format: 'png', clip: { x: 60, y: 150, width: 960, height: 360, scale: 1 } });
  fs.writeFileSync(shot, Buffer.from(s.data, 'base64'));
  console.log('saved', shot);
  ws.close();
})();
