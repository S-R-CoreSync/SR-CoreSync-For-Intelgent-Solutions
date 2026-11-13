// Deterministic dock capture: banners neutralised, fixed clip, so two runs compare.
const port = 9333;
const fs = await import('node:fs');
const [out] = process.argv.slice(2);
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

  // neutralise anything that changes height between visits
  await send('Runtime.evaluate', { expression: `(() => {
    document.documentElement.style.setProperty('--privacy-h', '0px');
    document.documentElement.style.setProperty('--consent-h', '0px');
    document.body.style.setProperty('--privacy-h', '0px');
    document.body.style.setProperty('--consent-h', '0px');
    const css = '.sr-privacy-banner-wrap,.cc-banner,#cookieConsent,.sr-consent-banner{display:none !important}';
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    return true; })()`, returnByValue: true });
  await new Promise(r => setTimeout(r, 900));

  const probe = `(() => {
    const a = document.querySelector('.apple-dock-item');
    const aft = getComputedStyle(a, '::after');
    const r = document.getElementById('appleMacosDockWrapper').getBoundingClientRect();
    return { y: Math.round(r.top), x: Math.round(r.left), w: Math.round(r.width), h: Math.round(r.height),
             font: aft.fontFamily, size: aft.fontSize };
  })()`;
  const m = await send('Runtime.evaluate', { expression: probe, returnByValue: true });
  const v = m.result.value;
  console.log('probe', JSON.stringify(v));

  const clip = { x: 560, y: v.y - 40, width: 480, height: v.h + 70, scale: 1 };
  const s = await send('Page.captureScreenshot', { format: 'png', clip });
  fs.writeFileSync(out, Buffer.from(s.data, 'base64'));
  console.log('saved', out);
  ws.close();
})();
