// Font rendering fingerprint: text widths + a screenshot of the same region.
const port = 9333;
const fs = await import('node:fs');
const [shot] = process.argv.slice(2);
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

  const expr = `(async () => {
    await document.fonts.ready;
    const probe = [];
    const sel = ['h1','h2','.lead','p','.price','.btn','a.btn','.nav-link','.metric-val','code','pre'];
    for (const s of sel) {
      const e = document.querySelector(s);
      if (!e) continue;
      const r = e.getBoundingClientRect();
      const cs = getComputedStyle(e);
      probe.push({ s, w: +r.width.toFixed(2), h: +r.height.toFixed(2), ff: cs.fontFamily.split(',')[0], fs: cs.fontSize, fw: cs.fontWeight });
    }
    return { probe, jakartaFaces: [...document.fonts].filter(f => /Jakarta/.test(f.family)).length };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  console.log(JSON.stringify(r.result.value));

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
  ws.close();
})();
