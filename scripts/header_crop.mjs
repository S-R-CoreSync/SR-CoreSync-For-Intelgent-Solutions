// Header-only capture, cropped, from the same session as the measurement.
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
  await new Promise(r => setTimeout(r, 2000));
  const geo = await send('Runtime.evaluate', { expression: `(() => {
    const h = document.querySelector('header.tf-header');
    const r = s => { const e = h.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.right)]; };
    return { brand: r('.header-col-brand'), menu: r('.nav-menu-main'), box: r('.box-navigation') };
  })()`, returnByValue: true });
  console.log('geometry', JSON.stringify(geo.result.value));
  const s = await send('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: 0, width: 1600, height: 110, scale: 1 } });
  fs.writeFileSync(out, Buffer.from(s.data, 'base64'));
  ws.close();
})();
